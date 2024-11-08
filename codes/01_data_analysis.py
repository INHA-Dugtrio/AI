# create and train model.py
import argparse
import os
import numpy as np
import pandas as pd
import argparse
import time

from utils.config import CONFIG, REQUIRED_FEATURES
from utils.data_loader import load_data
from training.data_preprocessing import load_and_preprocess_data, create_sequences
from training.model_training import create_lstm_autoencoder, train_model
from joblib import dump, load

def parse_arguments():
    parser = argparse.ArgumentParser(description='Train anomaly detection model')
    
    # RPM 선택 인자
    rpm_group = parser.add_mutually_exclusive_group(required=True)
    rpm_group.add_argument('-600', '--rpm_600', action='store_true', help='Use 600 RPM data')
    rpm_group.add_argument('-1200', '--rpm_1200', action='store_true', help='Use 1200 RPM data')
    
    # 모델 타입 선택 인자
    model_group = parser.add_mutually_exclusive_group(required=True)
    model_group.add_argument('-temp', '--temperature', action='store_true', help='Train temperature model')
    model_group.add_argument('-vib', '--vibration', action='store_true', help='Train vibration model')
    model_group.add_argument('-volt', '--voltage', action='store_true', help='Train voltage model')
    model_group.add_argument('-mult', '--multi_feature', action='store_true', help='Train multi-feature model')
    
    return parser.parse_args()

def get_model_type(args):
    if args.temperature:
        return 'temperature'
    elif args.vibration:
        return 'vibration'
    elif args.voltage:
        return 'voltage'
    elif args.multi_feature:
        return 'multi-feature'

def get_rpm_config(args):
    if args.rpm_600:
        return 'rpm_600'
    elif args.rpm_1200:
        return 'rpm_1200'

def format_time(seconds):
    """초를 시:분:초 형식으로 변환"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}시간 {minutes}분 {seconds}초"
    elif minutes > 0:
        return f"{minutes}분 {seconds}초"
    else:
        return f"{seconds}초"

def main():

    # 전체 수행 시간 측정 시작
    total_start_time = time.time()

    # 인자 파싱
    args = parse_arguments()
    
    # RPM 설정 및 모델 타입 결정
    rpm_config = get_rpm_config(args)
    model_type = get_model_type(args)
    
    print(f"Training {model_type} model with {rpm_config} data")
    print("-" * 50)
    
    # 데이터 디렉토리 설정
    data_dir = CONFIG[rpm_config]['train_data_dir']
    
    # 데이터 로드
    print("Loading data...")
    data_load_start = time.time()
    data_list = []
    for file in os.listdir(data_dir):
        if file.endswith('.csv'):
            df = pd.read_csv(os.path.join(data_dir, file))
            data_list.append(df)
    
    # 특성 선택 및 데이터 전처리
    print("\nPreprocessing data...")
    preprocess_start = time.time()
    required_features = REQUIRED_FEATURES[model_type]
    normalized_data_list, scaler = load_and_preprocess_data(data_list, required_features)
    
    # 시퀀스 생성
    print("\nCreating sequences...")
    sequence_start = time.time()
    sequences = create_sequences(normalized_data_list, CONFIG[rpm_config]['sequence_length'])
    
    # 모델 생성
    n_features = sequences.shape[2]  # 특성 수
    model = create_lstm_autoencoder(CONFIG[rpm_config]['sequence_length'], model_type)
    
    # 모델 학습
    print("Starting model training...")
    training_start = time.time()
    history = train_model(
        model, 
        sequences,
        epochs=CONFIG['training']['epochs'],
        batch_size=CONFIG['training']['batch_size'],
        validation_split=CONFIG['training']['validation_split']
    )

    training_time = time.time() - training_start
    
    # 모델 저장
    print("\nSaving model and scaler...")
    save_start = time.time()

    models_dir = CONFIG[rpm_config]['models_dir']
    os.makedirs(models_dir, exist_ok=True)

    model_path = os.path.join(models_dir, f'{model_type}_model.h5')
    model.save(model_path)

    scaler_path = os.path.join(models_dir, f'{model_type}_scaler.pkl')
    joblib.dump(scaler, scaler_path)

    print(f"Model saved to {model_path}")

    save_time = time.time() - save_start
    print(f"Model and scaler saving completed in {format_time(save_time)}")
    
    # 전체 수행 시간 계산
    total_time = time.time() - total_start_time
    
    # 최종 결과 출력
    print("\n" + "=" * 50)
    print("Training Summary:")
    print("-" * 50)
    print(f"Data Loading Time: {format_time(data_load_time)}")
    print(f"Preprocessing Time: {format_time(preprocess_time)}")
    print(f"Sequence Creation Time: {format_time(sequence_time)}")
    print(f"Model Training Time: {format_time(training_time)}")
    print(f"Model Saving Time: {format_time(save_time)}")
    print("-" * 50)
    print(f"Total Execution Time: {format_time(total_time)}")
    print("=" * 50)

if __name__ == "__main__":
    main()