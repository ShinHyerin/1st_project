# models.py
from db_config import get_oracle_connection


def insert_user(user_name, birth_date):
    """새로운 사용자를 DB에 저장하는 함수"""
    conn = get_oracle_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        # Oracle 11g 시퀀스 사용 방식
        sql = "INSERT INTO USERS (ID, USER_NAME, BIRTH_DATE) VALUES (USERS_SEQ.NEXTVAL, :1, :2)"
        cursor.execute(sql, (user_name, birth_date))
        conn.commit()
        return True
    except Exception as e:
        print(f"DB 저장 실패: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


# models.py에 추가

def save_health_record(user_name, bmi, cluster_name):
    conn = get_oracle_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        sql = "INSERT INTO HEALTH_RECORDS (RECORD_ID, USER_NAME, BMI, CLUSTER_NAME) VALUES (HEALTH_RECORDS_SEQ.NEXTVAL, :1, :2, :3)"
        cursor.execute(sql, (user_name, bmi, cluster_name))
        conn.commit()
        return True
    except Exception as e:
        print(f"기록 저장 실패: {e}")
        return False
    finally:
        conn.close()

def get_user_records(user_name):
    conn = get_oracle_connection()
    if not conn: return []
    try:
        cursor = conn.cursor()
        sql = "SELECT BMI, CLUSTER_NAME, TO_CHAR(CREATED_AT, 'YYYY-MM-DD') FROM HEALTH_RECORDS WHERE USER_NAME = :1 ORDER BY CREATED_AT DESC"
        cursor.execute(sql, [user_name])
        return cursor.fetchall() # [(23.5, '에너지 뿜뿜', '2026-04-08'), ...]
    finally:
        conn.close()