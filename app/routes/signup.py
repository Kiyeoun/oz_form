# 라우트 및 뷰 정의
from flask import render_template, request, jsonify, redirect, url_for, session
from flask.views import MethodView
from flask_smorest import Blueprint
from app.models import db, Question, DetailQuestion, Answer, User, Image


signup_blp = Blueprint("signup", __name__, description='content api') # 매개변수 (블루프린트 이름, 블루프린트 모듈 이름(import할 이름))

# 기본 화면
@signup_blp.route("/")
def index():
    image_url = Image.query.filter_by(type="main").first()
    return render_template("index.html", image_url=image_url)
    # html에서 .url로 받아야한다

# 회원가입 화면
@signup_blp.route('/signup')
class UserList(MethodView):
    def get(self):
        return render_template("signup.html")

    def post(self):
        print("요청 확인")
        user_data = request.get_json()
        user = User(name=user_data['name'], age=user_data['age'], gender=user_data['gender'])
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user_data.id
        return jsonify({"message": "User created", "user_id": user.id}), 201