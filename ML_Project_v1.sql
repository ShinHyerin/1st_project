CREATE TABLE KNHANES_RAW (
    ID          VARCHAR2(50) PRIMARY KEY,
    sex         NUMBER(1),
 
    HE_wt       NUMBER(10,2),
    HE_ht       NUMBER(10,2),
    HE_BMI      NUMBER(10,2),
    
    N_EN        NUMBER(10,2),
    N_PROT      NUMBER(10,2),
    N_FAT       NUMBER(10,2),
    N_CHO       NUMBER(10,2),
    N_SUGAR     NUMBER(10,2),
    N_NA        NUMBER(10,2),
    
    HE_CHOL     NUMBER(10,2),   -- 총 콜레스테롤
    HE_HDL_st2  NUMBER(10,2),   -- HDL
    HE_TG       NUMBER(10,2),   -- 중성지방
    HE_LDL_drct NUMBER(10,2),   -- LDL
    HE_HCHOL    NUMBER(1),      -- 유병여부
    
    BE8_1       NUMBER(10,2),   -- 앉아서 보내는 시간(시)
    BE8_2       NUMBER(10,2),   -- 앉아서 보내는 시간(분)
    BE3_31      NUMBER(3),      -- 걷기 일수
    BE3_32      NUMBER(10,2),   -- 걷기 지속(시)
    BE3_33      NUMBER(10,2),   -- 걷기 지속(분)
    BE5_1       NUMBER(3),      -- 근력운동 일수
    
    BP1         NUMBER(2),      -- 스트레스
    BP5         NUMBER(2),      -- 우울감
    
    UPLOAD_DATE DATE DEFAULT SYSDATE
);


-- 테이블에 컬럼이 없다면 추가
ALTER TABLE KNHANES_RAW ADD (
    BD1_11 NUMBER, BD2_1 NUMBER,
    BE3_73 NUMBER, BE3_74 NUMBER, BE3_77 NUMBER, BE3_78 NUMBER,
    BE3_83 NUMBER, BE3_84 NUMBER, BE3_87 NUMBER, BE3_88 NUMBER
);

ALTER TABLE KNHANES_RAW ADD (
    BD2_14 NUMBER, BD2_31 NUMBER
    );



SELECT 
    COUNT(*) AS total_count, -- 전체 행 개수
    COUNT(CASE WHEN AGE < 18 THEN 1 END) AS under_18_count, -- 미성년자 수
    AVG(HE_CHOL) AS avg_cholesterol, -- 평균 콜레스테롤 (정상 범위인지 확인)
    MAX(HE_CHOL) AS max_cholesterol  -- 최댓값 (999 같은 코드값이 섞였는지 확인)
FROM KNHANES_RAW;


SELECT 
    ID, 
    BE8_1 AS sit_hour, BE8_2 AS sit_min, -- 좌식 시간
    BE3_31 AS walk_days,                -- 걷기 일수
    HE_LDL_DRCT AS ldl,                 -- LDL 수치
    BP1 AS stress_level,                -- 스트레스 (1~4 사이여야 함)
    BP5 AS depression                   -- 우울감 (1, 2 여야 함)
FROM KNHANES_RAW
WHERE ROWNUM <= 20;


SELECT 
    ROUND(AVG(CASE WHEN HE_CHOL = 0 THEN 1 ELSE 0 END) * 100, 2) || '%' AS chol_zero_ratio,
    ROUND(AVG(CASE WHEN N_EN = 0 THEN 1 ELSE 0 END) * 100, 2) || '%' AS energy_zero_ratio,
    ROUND(AVG(CASE WHEN BE3_31 = 0 THEN 1 ELSE 0 END) * 100, 2) || '%' AS no_walking_ratio
FROM KNHANES_RAW;


SELECT DISTINCT BE3_31, BP1 FROM KNHANES_RAW;



-- 테이블 생성
CREATE TABLE USERS (
    ID NUMBER PRIMARY KEY,
    USER_NAME VARCHAR2(50) NOT NULL,
    BIRTH_DATE VARCHAR2(8) NOT NULL,
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE HEALTH_RECORDS (
    RECORD_ID NUMBER PRIMARY KEY,
    USER_NAME VARCHAR2(50) NOT NULL, -- 로그인한 세션의 이름과 매칭
    BMI NUMBER(5,2),
    CLUSTER_NAME VARCHAR2(50),
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE SEQUENCE HEALTH_RECORDS_SEQ START WITH 1 INCREMENT BY 1 NOCACHE;



-- 시퀀스 생성
CREATE SEQUENCE USERS_SEQ START WITH 1 INCREMENT BY 1 NOCACHE;


SELECT * FROM USERS;

SELECT * FROM HEALTH_RECORDS;



/* TRUNCATE TABLE KNHANES_RAW; */





COMMIT;
