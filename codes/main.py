# main.py
from utils.data_loader import load_data
from utils.config import CONFIG, REQUIRED_FEATURES
from training.data_preprocessing import load_and_preprocess_data, create_sequences
from training.model_training import create_lstm_autoencoder, train_model
from training.model_evaluation import evaluate_model
import numpy as np



def main():
    # 데이터 로딩(리스트 형태)
    dflist_1200 = load_data(CONFIG['rpm_1200']['data_dir'])
    #data_600 = load_data(CONFIG['data_dir'], 600)

    for model_type in CONFIG['model_type']:
        
        # RPM 1200 데이터를 모델에 맞게 전처리
        # 1. 필요 칼럼 선택
        # 2. 스케일링
        # 3. 시퀀스 생성
        normalized_data_1200_list, scaler_1200 = load_and_preprocess_data(dflist_1200, REQUIRED_FEATURES[model_type])
        sequences_1200 = create_sequences(normalized_data_1200_list, CONFIG['rpm_1200']['sequence_length'])

        # Process data for RPM 600
        #normalized_data_600, scaler_600 = load_and_preprocess_data(data_600, feature)
        #sequences_600 = create_sequences(normalized_data_600, CONFIG['sequence_length'])

        # Combine data
        #all_sequences = np.concatenate([sequences_1200, sequences_600], axis=0)
        all_sequences = sequences_1200
        # Split into train and test
        train_size = int(len(all_sequences) * CONFIG['rpm_1200']['train_test_split'])
        train_data = all_sequences[:train_size]
        test_data = all_sequences[train_size:]

        # Create and train model
        model = create_lstm_autoencoder(CONFIG['rpm_1200']['sequence_length'], model_type)
        history = train_model(model, train_data)

        # Evaluate model
        # For this example, we're using the test data as normal data
        # In practice, you'd need to create anomalous data for testing
        test_labels = np.zeros(len(test_data))  # All test data is labeled as normal
        results = evaluate_model(model, test_data, test_labels, CONFIG['rpm_1200']['anomaly_threshold'])

        print(f"Results for {feature}:")
        print(f"Precision: {results['precision']}")
        print(f"Recall: {results['recall']}")
        print(f"F1 Score: {results['f1_score']}")

        # Save model
        model.save(f"{CONFIG['models_dir']}/{feature}_model.h5")

if __name__ == "__main__":
    main()