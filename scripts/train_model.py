import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
# from sklearn.preprocessing import MinMaxScaler # 1. 임포트 변경
from sklearn.metrics import silhouette_score
import joblib
import os
from db_config import get_oracle_connection


# 도구 함수는 함수 밖, 맨 위에 하나만 둡니다.
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


def train_health_model_v3(k=3):
    # 1. DB에서 데이터 로드
    conn = get_oracle_connection()
    # query = "SELECT * FROM KNHANES_RAW WHERE N_EN > 0 AND HE_CHOL > 0"
    # 수정 제안: BMI가 0인 데이터는 아예 분석 대상에서 제외
    query = "SELECT * FROM KNHANES_RAW WHERE N_EN > 0 AND HE_CHOL > 0 AND HE_BMI > 0"
    df = pd.read_sql(query, conn)
    conn.close()

    # 2. 파생 변수 생성 및 데이터 정제
    # A. 활동량 계산
    df['TOTAL_HIGH_ACTIVE'] = (df['BE3_73'] * 60 + df['BE3_74']) + (df['BE3_77'] * 60 + df['BE3_78'])
    df['TOTAL_MID_ACTIVE'] = (df['BE3_83'] * 60 + df['BE3_84']) + (df['BE3_87'] * 60 + df['BE3_88'])
    df['TOTAL_SITTING_MIN'] = df['BE8_1'] * 60 + df['BE8_2']

    # B. 이상치 제거 (주관식 응답 위주)

    outlier_features = ['HE_BMI', 'TOTAL_SITTING_MIN', 'N_EN']
    for col in outlier_features:
        df = remove_outliers(df, col)

    # C. 영양소 및 콜레스테롤 비율
    for n in ['N_PROT', 'N_FAT', 'N_CHO', 'N_SUGAR', 'N_NA']:
        df[f'{n}_RATIO'] = df[n] / df['N_EN']

    df['LDL_HDL_RATIO'] = df['HE_LDL_DRCT'] / df['HE_HDL_ST2'].replace(0, np.nan)
    df['LDL_HDL_RATIO'].fillna(df['LDL_HDL_RATIO'].mean(), inplace=True)

    # D. 로그 변환 및 변수명 통일 (★중요: 아래 features 리스트와 이름을 맞춰야 함)
    # 1. 음주 잔 수: 800 이상(888, 999 포함)은 모두 0으로 처리
    # df.loc[df['BD2_14'] >= 800, 'BD2_14'] = 0
    # df['DRINK_AMOUNT_LOG'] = np.log1p(df['BD2_14'])

    # 2. 폭음 빈도: 8 이상(8, 9 포함)은 모두 0으로 처리
    # df.loc[df['BD2_31'] >= 8, 'BD2_31'] = 0
    # df['BINGE_FREQ'] = df['BD2_31']

    df['HIGH_ACTIVE_LOG'] = np.log1p(df['TOTAL_HIGH_ACTIVE'])
    df['MID_ACTIVE_LOG'] = np.log1p(df['TOTAL_MID_ACTIVE'])

    # 3. 최종 Feature 리스트 (데이터프레임 컬럼명과 100% 일치해야 빨간줄이 안 뜸)
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

    # 4. 스케일링 및 학습
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 5. 가중치 부여 (군집을 더 촘촘하고 의미 있게 만드는 핵심)
    # 특정 변수의 영향력을 높여서 그 변수를 중심으로 더 잘 뭉치게 합니다.
    X_scaled_weighted = X_scaled.copy()
    feature_names = features  # 위에서 정의한 리스트

    # BMI와 활동량의 가중치를 높여서 체격과 생활 패턴 중심의 군집 유도
    X_scaled_weighted[:, feature_names.index('HE_BMI')] *= 1.5
    X_scaled_weighted[:, feature_names.index('HIGH_ACTIVE_LOG')] *= 1.2
    # # 음주 관련 변수의 영향력을 살짝 줄이고, 체격(BMI) 중심으로 뭉치게 유도
    # X_scaled_weighted[:, feature_names.index('HE_BMI')] *= 2.0  # BMI 강조
    # X_scaled_weighted[:, feature_names.index('DRINK_AMOUNT_LOG')] *= 0.7  # 음주 영향력 감소
    # X_scaled_weighted[:, feature_names.index('BINGE_FREQ')] *= 0.7  # 폭음 영향력 감소

    # 학습은 가중치가 부여된 데이터로 진행
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(X_scaled_weighted)

    # scaler = MinMaxScaler()  # 2. 스케일러 교체
    # X_scaled = scaler.fit_transform(X)

    # kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    # df['cluster'] = kmeans.fit_predict(X_scaled)

    # 5. 모델 저장
    if not os.path.exists('models'): os.makedirs('models')
    joblib.dump(kmeans, 'models/health_kmeans_v3.pkl')
    joblib.dump(scaler, 'models/health_scaler_v3.pkl')

    # 6. 결과 출력
    # score = silhouette_score(X_scaled, df['cluster'])
    score = silhouette_score(X_scaled_weighted, df['cluster'])
    print(f"\n🚀 K={k} 모델 학습 완료!")
    print(f"✨ 실루엣 점수: {score:.4f}")
    print(f"📊 군집별 데이터 분포:\n{df['cluster'].value_counts()}")

    return df, features


if __name__ == "__main__":
    final_df, feature_list = train_health_model_v3(k=3)
    profile = final_df.groupby('cluster')[feature_list].mean().T
    print("\n🔍 군집별 특징 분석 (평균값):")
    print(profile)