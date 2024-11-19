from app import create_app

application = create_app()

if __name__ == "__main__":
    application.run(debug=True)

# 블루프린트가 문제였고 각자 블루프린트 객체명, 블루프린트 이름 바꾸고, import 추가해주고, 리다이렉트 수정해주고
