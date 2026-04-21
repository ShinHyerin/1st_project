# db_config.py
import oracledb
import os

DB_CONFIG = {
    "user": "shin",
    "password": "123456",
    "dsn": "localhost:1521/xe"
}

def get_oracle_connection():
    try:
        # [중요] Oracle 11g 연결을 위해 Thick 모드 활성화
        # 시스템 Path에 이미 C:\oraclexe\...\bin이 있으므로 아래 명령어로 클라이언트를 초기화합니다.
        try:
            oracledb.init_oracle_client()
        except Exception as e:
            # 이미 초기화된 경우 에러가 날 수 있으므로 무시합니다.
            pass

        conn = oracledb.connect(
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            dsn=DB_CONFIG["dsn"]
        )
        return conn
    except Exception as e:
        print(f"DB 연결 실패: {e}")
        return None