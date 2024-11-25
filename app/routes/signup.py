# 라우트 및 뷰 정의
from flask import render_template, request, jsonify, redirect, url_for, session
from flask.views import MethodView
from flask_smorest import Blueprint
from app.models import db, Question, DetailQuestion, Answer, User, Image
from datetime import datetime


signup_blp = Blueprint("signup", __name__, description='signup api') # 매개변수 (블루프린트 이름, 블루프린트 모듈 이름(import할 이름))

# 기본 화면
@signup_blp.route("/")
def index():
    image_url = Image.query.filter_by(type="main").first()
    return render_template("index.html", image_url=image_url)
    # html에서 .url로 받아야한다

# 회원가입 화면
@signup_blp.route('/signup')
class Signup(MethodView):
    def get(self):
        return render_template("signup.html")

    def post(self):
        print("요청 확인")
        user_data = request.get_json()
        user = User(name=user_data['name'], age=user_data['age'], gender=user_data['gender'])
        # SQLAlchemy는 Model 클래스의 인스턴스를 생성할 때 자동적으로 __init__메서드를 생성해준다. models에서 db.Model을 상속받고 있기 때문에 키워드 인자 지정 가능
        db.session.add(user) # db(SQLAchemy)의 세션에 추가
        db.session.commit() # db 커밋
        session['user_id'] = user.id # Flask의 session에 user_id추가(브라우저 쿠키에 저장 / 26열에서 User로 객체를 만들었을 경우 안에 있는 내용을 갖고오고 싶을 때 .을 사용해야한다)
        return jsonify({"message": "설문 조사에 참여해주셔서 감사합니다.", "user_id": user.id}), 201
        # jsonify는 서버에서 클라이언트로 정보를 전달하기 위해 쓰인다