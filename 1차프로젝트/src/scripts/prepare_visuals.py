import pandas as pd
import numpy as np
import joblib
import os
from sklearn.decomposition import PCA
from db_config import get_oracle_connection


def prepare_web_assets():
    print("🚀 웹 서비스용 시각화 자산 생성을 시작합니다...")

    # 1. 저장된 모델 및 스케일러 로드
    model_path = 'models/health_kmeans_v3.pkl'
    scaler_path = 'models/health_scaler_v3.pkl'

    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        print("❌ 모델 파일을 찾을 수 없습니다. 경로를 확인하세요.")
        return

    kmeans = joblib.load(model_path)
    scaler = joblib.load(scaler_path)

    # 2. DB에서 데이터 로드
    print("📡 DB에서 데이터를 불러오는 중...")
    conn = get_oracle_connection()
    query = "SELECT * FROM KNHANES_RAW WHERE N_EN > 0 AND HE_CHOL > 0"
    df = pd.read_sql(query, conn)
    conn.close()

    # 3. 데이터 전처리 (학습 로직과 동일)
    print("🧹 데이터 전처리 중...")
    df['TOTAL_HIGH_ACTIVE'] = (df['BE3_73'] * 60 + df['BE3_74']) + (df['BE3_77'] * 60 + df['BE3_78'])
    df['TOTAL_MID_ACTIVE'] = (df['BE3_83'] * 60 + df['BE3_84']) + (df['BE3_87'] * 60 + df['BE3_88'])
    df['TOTAL_SITTING_MIN'] = df['BE8_1'] * 60 + df['BE8_2']

    # 비율 계산
    df['N_FAT_RATIO'] = df['N_FAT'] / df['N_EN']
    df['N_NA_RATIO'] = df['N_NA'] / df['N_EN']

    # 혈관 지표 비율
    df['LDL_HDL_RATIO'] = df['HE_LDL_DRCT'] / df['HE_HDL_ST2'].replace(0, np.nan)
    df['LDL_HDL_RATIO'].fillna(df['LDL_HDL_RATIO'].mean(), inplace=True)

    # 로그 변환
    df['HIGH_ACTIVE_LOG'] = np.log1p(df['TOTAL_HIGH_ACTIVE'])
    df['MID_ACTIVE_LOG'] = np.log1p(df['TOTAL_MID_ACTIVE'])

    # 4. Feature 선택 및 스케일링
    features = [
        'HE_BMI', 'HIGH_ACTIVE_LOG', 'MID_ACTIVE_LOG',
        'TOTAL_SITTING_MIN', 'N_FAT_RATIO', 'N_NA_RATIO', 'LDL_HDL_RATIO'
    ]

    X = df[features].fillna(0)
    X_scaled = scaler.transform(X)  # fit_transform이 아니라 transform 사용

    # 5. PCA 생성 및 좌표 추출
    print("📊 PCA 차원 축소 중 (7D -> 2D)...")
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(X_scaled)

    # 6. 결과 저장용 데이터프레임 생성
    pca_df = pd.DataFrame(pca_result, columns=['PC1', 'PC2'])
    pca_df['Cluster'] = kmeans.predict(X_scaled)  # 예측된 군집 번호 추가

    # 7. 파일 저장 (이 위치가 웹 서버가 읽는 위치여야 함)
    print("💾 파일 저장 중...")

    # 경로 보장
    os.makedirs('data', exist_ok=True)
    os.makedirs('models', exist_ok=True)

    # PCA 모델 저장
    joblib.dump(pca, 'models/pca_model.pkl')
    # 배경 데이터 저장
    pca_df.to_csv('data/pca_transformed_data.csv', index=False)

    print("-" * 30)
    print("✅ 생성 완료!")
    print(f"1. PCA 모델: models/pca_model.pkl")
    print(f"2. 배경 데이터: data/pca_transformed_data.csv (총 {len(pca_df)}행)")
    print("-" * 30)


if __name__ == "__main__":
    prepare_web_assets()