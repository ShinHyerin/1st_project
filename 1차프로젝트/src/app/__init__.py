# # app/__init__.py
# from flask import Flask
# import os
#
#
# def create_app():
#     # 1. Flask 앱 생성 (templates, static 경로 고정)
#     # 현재 파일(__file__)의 위치를 기준으로 경로를 잡으면 어디서 실행해도 안전합니다.
#     template_dir = os.path.join(os.path.dirname(__file__), 'templates')
#     static_dir = os.path.join(os.path.dirname(__file__), 'static')
#
#     app = Flask(__name__,
#                 template_folder=template_dir,
#                 static_folder=static_dir)
#
#     # 2. 보안 및 앱 설정
#     app.config['SECRET_KEY'] = 'dev_key_1234'
#     app.config['JSON_AS_ASCII'] = False  # 한글 깨짐 방지
#
#     return app


# app/__init__.py
from flask import Flask

app = Flask(__name__)
app.secret_key = 'namedly_health_secret_key'

from app import routes