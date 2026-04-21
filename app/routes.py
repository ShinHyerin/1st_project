from seaborn.external.husl import refU

from app import app
from flask import render_template, request
import joblib
import numpy as np
import pandas as pd
import os
from .utils import generate_scatter_plot
from flask import render_template, request, redirect, url_for, session
from .models import insert_user, save_health_record, get_user_records

# 1. 모델 및 스케일러 로드
model_path = 'models/health_kmeans_v3.pkl'
scaler_path = 'models/health_scaler_v3.pkl'

if os.path.exists(model_path) and os.path.exists(scaler_path):
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
else:
    print("❌ 모델 파일을 찾을 수 없습니다. 경로를 확인하세요.")


# --- 페이지 라우팅 구간 ---

@app.route('/')
def index():
    # 메인 페이지 (캐러셀 화면)
    return render_template('index.html')


@app.route('/analysis')
def analysis():
    # 분석 입력 폼 페이지 (새로 추가된 함수)
    return render_template('analysis.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        birth_date = request.form.get('birth_date')

        if insert_user(user_name, birth_date):
            session['user_name'] = user_name  # 이제 secret_key 덕분에 에러 안 남!
            return redirect(url_for('index'))  # 메인 페이지로 이동
        else:
            return render_template('login.html', error="오류 발생")

    return render_template('login.html')


@app.route('/logout')
def logout():
    # 세션에서 사용자 정보 삭제
    session.clear()
    return redirect(url_for('index'))


@app.route('/history')
def history():
    if not session.get('user_name'):
        return redirect(url_for('login'))

    records = get_user_records(session['user_name'])
    return render_template('history.html', records=records)


@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':

        try:
            # 1. 폼 데이터 가져오기
            f = request.form
            data = {
                'height': float(f['height']),
                'weight': float(f['weight']),
                'high_active': float(f['high_active']),
                'mid_active': float(f['mid_active']),
                'sitting': float(f['sitting']),
                'energy': float(f['energy']),
                'fat': float(f['fat']),
                'na': float(f['na']),
                'sugar': float(f['sugar']),
                'ldl': float(f['ldl']),
                'hdl': float(f['hdl'])
            }

            # 2. 모델 입력용 데이터 가공
            bmi = data['weight'] / ((data['height'] / 100) ** 2)

            # --- 수정 포인트: data['key'] 형식으로 변수 사용 ---
            input_df = pd.DataFrame([{
                'HE_BMI': bmi,
                'HIGH_ACTIVE_LOG': np.log1p(data['high_active']),
                'MID_ACTIVE_LOG': np.log1p(data['mid_active']),
                'TOTAL_SITTING_MIN': data['sitting'],
                'N_FAT_RATIO': data['fat'] / data['energy'] if data['energy'] > 0 else 0,
                'N_NA_RATIO': data['na'] / data['energy'] if data['energy'] > 0 else 0,
                'LDL_HDL_RATIO': data['ldl'] / data['hdl'] if data['hdl'] > 0 else 0
            }])

            # 3. 스케일링 및 예측
            input_scaled = scaler.transform(input_df)
            prediction = model.predict(input_scaled)
            cluster = int(prediction[0])

            # 4. 산점도용 좌표 생성
            # input_scaled는 스케일링된 2차원 배열입니다.
            # 그중 첫 번째 행의 BMI 컬럼(0번 인덱스)과 활동량 컬럼(1번 인덱스)을 가져옵니다.
            user_x = float(input_scaled[0][0])  # 스케일링된 BMI
            user_y = float(input_scaled[0][1])  # 스케일링된 활동량 로그값

            # 시각화 이미지 생성 시 전달
            generate_scatter_plot([user_x, user_y], cluster)



            # 5. 군집별 결과 데이터 설정
            # 1. 정보 정의 (상단 또는 함수 내부에 위치) (여기서 result가 만들어짐)
            cluster_info = {
                0: {
                    "name": "슬림한 저활동군",
                    "feedback": "체중은 정상이지만 활동량이 매우 적어 근감소증 위험이 있습니다.",
                    "warning": "🚨 마른 비만 위험! 현재 앉아있는 시간이 너무 길어 하체 근력이 부족해질 수 있습니다.",
                    "solution": {
                        "task": "단백질 위주의 식단과 함께 계단 이용하기",
                        "exercise": "스쿼트 15회 3세트 & 맨몸 런지",
                        "habit": "매시간 알람을 맞춰 5분간 제자리 걷기"
                    }
                },
                1: {
                    "name": "에너지 뿜뿜 운동가",
                    "feedback": "균형 잡힌 식단과 꾸준한 운동 습관을 가지고 계시네요!",
                    "warning": "✅ 아주 훌륭합니다! 지금처럼 꾸준히 유지하는 것이 가장 중요합니다.",
                    "solution": {
                        "task": "충분한 수면과 수분 섭취로 컨디션 관리",
                        "exercise": "현재 루틴 유지 또는 고강도 인터벌 트레이닝",
                        "habit": "운동 전후 스트레칭으로 유연성 보완하기"
                    }
                },
                2: {
                    "name": "집중 관리 필요군",
                    "feedback": "혈관 지표와 BMI가 다소 높은 편입니다.",
                    "warning": "⚠️ 주의가 필요합니다! 나트륨 섭취를 줄이고 유산소 운동이 시급합니다.",
                    "solution": {
                        "task": "식사 시 채소 먼저 먹기 (식이섬유 섭취)",
                        "exercise": "빠르게 걷기 30분 또는 수영",
                        "habit": "국물 요리 섭취 줄이기 및 저염 식단 실천"
                    }
                }
            }


            # 결과 추출 (안전하게 get 사용)
            result = cluster_info.get(cluster, {
                "name": "일반 관리군",
                "feedback": "전반적인 건강 관리가 필요합니다.",
                "warning": "생활 습관 개선을 제안합니다.",
                "solution": {"task": "규칙적인 식사", "exercise": "가벼운 산책", "habit": "충분한 휴식"}
            })

            if session.get('user_name') and result:
                from .models import save_health_record  # 여기서 불러오거나 상단에서 불러오기
                # 이름, BMI, 클러스터 이름을 저장
                save_health_record(session['user_name'], round(bmi, 2), result['name'])
                print(f"✅ {session['user_name']}님의 기록이 저장되었습니다.")

            # 모든 데이터를 템플릿으로 전달
            return render_template(
                'result.html',
                user_height=data['height'],
                user_weight=data['weight'],
                user_bmi=round(bmi, 2),
                user_high_active=data['high_active'],
                user_mid_active=data['mid_active'],
                user_sitting=data['sitting'],
                user_energy=data['energy'],
                user_fat=data['fat'],
                user_na=data['na'],
                user_sugar=data['sugar'],
                user_ldl=data['ldl'],
                user_hdl=data['hdl'],
                # warning_msg="현재 활동량이 부족합니다. 운동량 증가가 필요합니다.",
                cluster_name=result['name'],
                feedback=result['feedback'],
                warning_msg=result['warning'],
                solutions=result['solution'],  # 딕셔너리 통째로 전달
                cluster=cluster)
                # target_msg=f"현재 당류를 {data['sugar']} g 섭취 중입니다. 감량을 권장합니다."




        # except Exception as e:
        #     return f"데이터 처리 중 오류가 발생했습니다: {str(e)}"


        except Exception as e:
            import traceback
            return f"<pre>{traceback.format_exc()}</pre>"

    # app = Flask(__name__)
    # app.secret_key = 'your_very_secret_key_here'  # 아무 문자열이나 길게 넣으세요!


    return "잘못된 접근입니다."




