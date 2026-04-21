import pandas as pd
from db_config import get_oracle_connection


def load_data_to_oracle(csv_path):
    print(f"🚀 Reading CSV from {csv_path}...")
    df = pd.read_csv(csv_path, low_memory=False)

    # 1. 여기서 age를 사용해 18세 이상만 남깁니다.
    if 'age' in df.columns:
        df = df[df['age'] >= 18]
        print(f"🔞 성인 데이터만 추출 완료 (현재 {len(df)}건)")


    # 1. 사용할 모든 컬럼 정의 (DB 원본 컬럼들)
    target_columns = [
        'ID', 'sex', 'HE_wt', 'HE_ht', 'HE_BMI',
        'N_EN', 'N_PROT', 'N_FAT', 'N_CHO', 'N_SUGAR', 'N_NA',
        'HE_chol', 'HE_HDL_st2', 'HE_TG', 'HE_LDL_drct', 'HE_HCHOL',
        'BE8_1', 'BE8_2', 'BE3_31', 'BE3_32', 'BE3_33', 'BE5_1',
        'BP1', 'BP5',
        'BD1_11', 'BD2_1',
        'BE3_73', 'BE3_74', 'BE3_77', 'BE3_78', 'BE3_83', 'BE3_84', 'BE3_87', 'BE3_88',
        'BD2_14', 'BD2_31'
    ]

    # 2. 기본 숫자 변환 및 결측치 0 채움
    for col in target_columns:
        if col in df.columns and col != 'ID':
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    df['ID'] = df['ID'].astype(str)

    # 3. [개별 전처리 규칙 적용]

    # 규칙 A: 걷기 일수 7 이상 제거
    df.loc[df['BE3_31'] >= 7, 'BE3_31'] = 0

    # 규칙 B: 정신건강 8, 9 제거
    for col in ['BP1', 'BP5']:
        df.loc[df[col] >= 8, col] = 0

    # 규칙 C: 활동 시간 80, 88, 99 제거
    time_cols = [
        'BE8_1', 'BE8_2', 'BE3_32', 'BE3_33', 'BE5_1',
        'BE3_73', 'BE3_74', 'BE3_77', 'BE3_78',
        'BE3_83', 'BE3_84', 'BE3_87', 'BE3_88'
    ]
    for col in time_cols:
        if col in df.columns:
            # 88(비해당), 99(모름)를 0으로 처리
            df.loc[df[col] >= 80, col] = 0

# [규칙 2] 일수/여부/정신건강/음주 관련 컬럼 (8, 9 제거)
# BE3_31(걷기 일수), BP1(스트레스), BP5(우울감), BD1_11(음주빈도), BD2_1(음주량)
# 만약 BE3_71, 72(고강도 일수/여부) 등을 추가한다면 여기에 포함시켜야 합니다.
    count_and_status_cols = ['BE3_31', 'BP1', 'BP5', 'BD1_11', 'BD2_1', 'BD2_31']
    for col in count_and_status_cols:
        if col in df.columns:
            # 8(비해당), 9(모름/무응답)를 0으로 처리
            df.loc[df[col] >= 8, col] = 0


    count_cols_alc = ['BD2_14']
    for col in count_cols_alc:
        # 888, 999 를 0으로 처리
        if col in df.columns:
            df.loc[df[col] >= 888, col] = 0


    # 규칙 추가: 걷기 일수는 0~6(7일 이상)까지만 유효하므로 7도 처리 (기존 코드 유지)
    df.loc[df['BE3_31'] >= 7, 'BE3_31'] = 0

    print("✅ 전처리 규칙 적용 완료 (8/9 및 88/99 제거 확인)")

    # 4. DB 연결
    conn = get_oracle_connection()
    cursor = conn.cursor()

    # 5. INSERT SQL 수정 (컬럼 개수 맞춤 - 총 37개)
    insert_sql = f"""
        INSERT INTO KNHANES_RAW (
            {', '.join(target_columns)}
        ) VALUES (
            {', '.join([':' + str(i + 1) for i in range(len(target_columns))])}
        )
    """

    # 6. 모든 전처리가 끝난 후 튜플 생성
    data_tuples = [tuple(x) for x in df[target_columns].values]

    try:
        # 기존 데이터 삭제 (중요!)
        cursor.execute("TRUNCATE TABLE KNHANES_RAW")

        # 데이터 대량 삽입
        cursor.executemany(insert_sql, data_tuples)
        conn.commit()
        print(f"✨ Successfully loaded {len(data_tuples)} rows to Oracle!")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error loading data: {e}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    load_data_to_oracle('C:/ML_Project/ml_proj_v1/data/data_2024.csv')