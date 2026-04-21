from app import app  # app 폴더의 __init__.py에서 생성한 app 객체를 가져옴

if __name__ == '__main__':
    # host='0.0.0.0'을 추가하면 외부 기기에서도 접속 가능합니다.
    # debug=True는 코드 수정 시 서버가 자동으로 재시작되게 합니다.
    app.run(host='0.0.0.0', port=5000, debug=True)