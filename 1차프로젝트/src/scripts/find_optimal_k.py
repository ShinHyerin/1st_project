import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
# from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import silhouette_score
from db_config import get_oracle_connection


def remove_outliers(df, column):
    """상위 1%와 하위 1%를 넘어가는 극단적인 값 제거"""
    if column not in df.columns:
        return df
    lower_bound = df[column].quantile(0.01)
    upper_bound = df[column].quantile(0.99)
    initial_count = len(df)
    df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
    print(f"🧹 {column} 이상치 제거 완료: {initial_count - len(df)}개 삭제")
    return df


def find_optimal_k():
    # 1. DB 데이터 로드
    conn = get_oracle_connection()
    # query = "SELECT * FROM KNHANES_RAW WHERE N_EN > 0 AND HE_CHOL > 0"
    query = "SELECT * FROM KNHANES_RAW WHERE N_EN > 0 AND HE_CHOL > 0 AND HE_BMI > 0"
    df = pd.read_sql(query, conn)
    conn.close()

    # 2. 파생 변수 생성 (기존 train_model 로직과 일치)
    df['TOTAL_HIGH_ACTIVE'] = (df['BE3_73'] * 60 + df['BE3_74']) + (df['BE3_77'] * 60 + df['BE3_78'])
    df['TOTAL_MID_ACTIVE'] = (df['BE3_83'] * 60 + df['BE3_84']) + (df['BE3_87'] * 60 + df['BE3_88'])
    df['TOTAL_SITTING_MIN'] = df['BE8_1'] * 60 + df['BE8_2']

    # 3. 이상치 제거 (학습과 동일한 조건)
    outlier_features = ['HE_BMI', 'TOTAL_SITTING_MIN', 'N_EN']
    for col in outlier_features:
        df = remove_outliers(df, col)

    # 4. 영양소 및 콜레스테롤 비율
    df['N_FAT_RATIO'] = df['N_FAT'] / df['N_EN']
    df['N_NA_RATIO'] = df['N_NA'] / df['N_EN']
    df['LDL_HDL_RATIO'] = df['HE_LDL_DRCT'] / df['HE_HDL_ST2'].replace(0, np.nan)
    df['LDL_HDL_RATIO'].fillna(df['LDL_HDL_RATIO'].mean(), inplace=True)

    # # 5. 새로운 음주 변수 처리 (800 이상, 8 이상 조건 처리 포함)
    # # 한 번에 마시는 양 (BD2_14) 처리
    # df.loc[df['BD2_14'] >= 800, 'BD2_14'] = 0
    # df['DRINK_AMOUNT_LOG'] = np.log1p(df['BD2_14'])
    #
    # # 폭음 빈도 (BD2_31) 처리
    # df.loc[df['BD2_31'] >= 8, 'BD2_31'] = 0
    # df['BINGE_FREQ'] = df['BD2_31']

    # 활동량 로그 변환
    df['HIGH_ACTIVE_LOG'] = np.log1p(df['TOTAL_HIGH_ACTIVE'])
    df['MID_ACTIVE_LOG'] = np.log1p(df['TOTAL_MID_ACTIVE'])

    # 최종 Feature 선택
    features = [
        'HE_BMI',
        'HIGH_ACTIVE_LOG',
        'MID_ACTIVE_LOG',
        'TOTAL_SITTING_MIN',
        'N_FAT_RATIO',
        'N_NA_RATIO',
        'LDL_HDL_RATIO'
    ]

    X = df[features].fillna(0)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # scaler = MinMaxScaler()
    # X_scaled = scaler.fit_transform(X)

    # 6. K값 변화에 따른 지표 계산
    inertia = []
    silhouette_avg = []
    k_range = range(2, 11)

    # ★ 가중치 반영 (가중치를 줬을 때의 최적 K는 다를 수 있음)
    X_scaled_weighted = X_scaled.copy()
    X_scaled_weighted[:, features.index('HE_BMI')] *= 1.5
    X_scaled_weighted[:, features.index('HIGH_ACTIVE_LOG')] *= 1.2

    print(f"\n🔎 총 {len(df)}개 데이터로 K값 계산 시작...")
    # 6. K값 변화에 따른 지표 계산
    # ... (이후 루프 내에서 fit할 때 X_scaled 대신 X_scaled_weighted 사용)
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        # 가중치가 적용된 데이터로 계산해야 실제 모델과 일치합니다.
        cluster_labels = kmeans.fit_predict(X_scaled_weighted)

        inertia.append(kmeans.inertia_)
        # silhouette_avg.append(silhouette_score(X_scaled, cluster_labels))
        # 수정 제안 (가중치 데이터 기준으로 점수 확인)
        silhouette_avg.append(silhouette_score(X_scaled_weighted, cluster_labels))
        print(f"K={k} 완료 (Inertia: {kmeans.inertia_:.2f}, Silhouette: {silhouette_avg[-1]:.4f})")

    # 7. 시각화
    fig, ax1 = plt.subplots(figsize=(10, 6))

    color = 'tab:blue'
    ax1.set_xlabel('Number of Clusters (k)')
    ax1.set_ylabel('Inertia (SSE)', color=color)
    ax1.plot(k_range, inertia, marker='o', color=color, label='Inertia')
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Silhouette Score', color=color)
    ax2.plot(k_range, silhouette_avg, marker='s', color=color, linestyle='--', label='Silhouette Score')
    ax2.tick_params(axis='y', labelcolor=color)

    plt.title('Elbow Method & Silhouette Score (Optimized Version)')
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    find_optimal_k()