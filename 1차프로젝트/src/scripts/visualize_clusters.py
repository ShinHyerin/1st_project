# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
# from sklearn.decomposition import PCA
# import joblib
# from db_config import get_oracle_connection
#
#
# def visualize_v3_clusters():
#     # 1. DB에서 데이터 로드 (학습 때와 동일한 조건)
#     conn = get_oracle_connection()
#     query = "SELECT * FROM KNHANES_RAW WHERE N_EN > 0 AND HE_CHOL > 0"
#     df = pd.read_sql(query, conn)
#     conn.close()
#
#     # 2. 파생 변수 및 로그 변환 (학습 코드와 100% 일치해야 함)
#     df['ALC_INDEX'] = df['BD1_11'] * df['BD2_1']
#     df['TOTAL_HIGH_ACTIVE'] = (df['BE3_73'] * 60 + df['BE3_74']) + (df['BE3_77'] * 60 + df['BE3_78'])
#     df['TOTAL_MID_ACTIVE'] = (df['BE3_83'] * 60 + df['BE3_84']) + (df['BE3_87'] * 60 + df['BE3_88'])
#     df['TOTAL_SITTING_MIN'] = df['BE8_1'] * 60 + df['BE8_2']
#     df['N_FAT_RATIO'] = df['N_FAT'] / df['N_EN']
#     df['N_NA_RATIO'] = df['N_NA'] / df['N_EN']
#     df['LDL_HDL_RATIO'] = df['HE_LDL_DRCT'] / df['HE_HDL_ST2'].replace(0, np.nan)
#     df['LDL_HDL_RATIO'].fillna(df['LDL_HDL_RATIO'].mean(), inplace=True)
#
#     df['ALC_INDEX_LOG'] = np.log1p(df['ALC_INDEX'])
#     df['HIGH_ACTIVE_LOG'] = np.log1p(df['TOTAL_HIGH_ACTIVE'])
#     df['MID_ACTIVE_LOG'] = np.log1p(df['TOTAL_MID_ACTIVE'])
#
#     # 3. 모델 및 스케일러 로드
#     scaler = joblib.load('models/health_scaler_v3.pkl')
#     kmeans = joblib.load('models/health_kmeans_v3.pkl')
#
#     # 4. 데이터 전처리 및 군집 예측
#     features = ['HE_BMI', 'ALC_INDEX_LOG', 'HIGH_ACTIVE_LOG', 'MID_ACTIVE_LOG',
#                 'TOTAL_SITTING_MIN', 'N_FAT_RATIO', 'N_NA_RATIO', 'LDL_HDL_RATIO']
#
#     X = df[features].fillna(0)
#     X_scaled = scaler.transform(X)
#     df['cluster'] = kmeans.predict(X_scaled)
#
#     # 5. PCA로 2차원 축소
#     pca = PCA(n_components=2)
#     pca_refined = pca.fit_transform(X_scaled)
#     df['pca_x'] = pca_refined[:, 0]
#     df['pca_y'] = pca_refined[:, 1]
#
#     # 6. 그래프 그리기
#     plt.figure(figsize=(12, 8))
#     sns.scatterplot(
#         x='pca_x', y='pca_y',
#         hue='cluster',
#         palette='viridis',
#         data=df,
#         alpha=0.6,
#         edgecolor='w',
#         s=50
#     )
#
#     # 군집 중심점(Centroids) 표시
#     centers_pca = pca.transform(kmeans.cluster_centers_)
#     plt.scatter(
#         centers_pca[:, 0], centers_pca[:, 1],
#         c='red', marker='X', s=200, label='Centroids'
#     )
#
#     plt.title(f'K-Means Clustering Visualization (K=4, Silhouette: 0.1561)')
#     plt.legend()
#     plt.show()
#
#
# if __name__ == "__main__":
#     visualize_v3_clusters()


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os
from sklearn.decomposition import PCA
from db_config import get_oracle_connection


def visualize_existing_model():
    # 1. 저장된 모델 및 스케일러 로드
    model_path = 'models/health_kmeans_v3.pkl'
    scaler_path = 'models/health_scaler_v3.pkl'

    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        print("❌ 모델 파일을 찾을 수 없습니다. train_model.py를 먼저 실행하세요.")
        return

    kmeans = joblib.load(model_path)
    scaler = joblib.load(scaler_path)

    # 2. DB에서 데이터 로드 (학습 때와 동일한 쿼리)
    conn = get_oracle_connection()
    query = "SELECT * FROM KNHANES_RAW WHERE N_EN > 0 AND HE_CHOL > 0"
    df = pd.read_sql(query, conn)
    conn.close()

    # 3. 데이터 전처리 (train_model.py와 100% 일치해야 함)
    df['TOTAL_HIGH_ACTIVE'] = (df['BE3_73'] * 60 + df['BE3_74']) + (df['BE3_77'] * 60 + df['BE3_78'])
    df['TOTAL_MID_ACTIVE'] = (df['BE3_83'] * 60 + df['BE3_84']) + (df['BE3_87'] * 60 + df['BE3_88'])
    df['TOTAL_SITTING_MIN'] = df['BE8_1'] * 60 + df['BE8_2']

    for n in ['N_PROT', 'N_FAT', 'N_CHO', 'N_SUGAR', 'N_NA']:
        df[f'{n}_RATIO'] = df[n] / df['N_EN']

    df['LDL_HDL_RATIO'] = df['HE_LDL_DRCT'] / df['HE_HDL_ST2'].replace(0, np.nan)
    df['LDL_HDL_RATIO'].fillna(df['LDL_HDL_RATIO'].mean(), inplace=True)

    # df.loc[df['BD2_14'] >= 800, 'BD2_14'] = 0
    # df['DRINK_AMOUNT_LOG'] = np.log1p(df['BD2_14'])
    # df.loc[df['BD2_31'] >= 8, 'BD2_31'] = 0
    # df['BINGE_FREQ'] = df['BD2_31']

    df['HIGH_ACTIVE_LOG'] = np.log1p(df['TOTAL_HIGH_ACTIVE'])
    df['MID_ACTIVE_LOG'] = np.log1p(df['TOTAL_MID_ACTIVE'])

    # 4. Feature 선택 및 스케일링
    features = [
        'HE_BMI',
        'HIGH_ACTIVE_LOG', 'MID_ACTIVE_LOG', 'TOTAL_SITTING_MIN',
        'N_FAT_RATIO', 'N_NA_RATIO', 'LDL_HDL_RATIO'
    ]


    X = df[features].fillna(0)
    X_scaled = scaler.fit_transform(X)  # 주의: fit_transform이 아니라 transform만 사용


    # 5. 군집 예측
    df['cluster'] = kmeans.predict(X_scaled)

    # 6. PCA 시각화
    print("🎨 2D 산점도 생성 중...")
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(X_scaled)

    plt.figure(figsize=(12, 8))
    sns.scatterplot(
        x=pca_result[:, 0], y=pca_result[:, 1],
        hue=df['cluster'], palette='viridis',
        alpha=0.6, edgecolor='w', s=60
    )


    joblib.dump(pca, 'models/pca_model.pkl')






    plt.title('Health Data Clusters (PCA 2D Visualization)', fontsize=15)
    plt.xlabel('Principal Component 1', fontsize=12)
    plt.ylabel('Principal Component 2', fontsize=12)
    plt.legend(title='Cluster', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()







if __name__ == "__main__":
    visualize_existing_model()

