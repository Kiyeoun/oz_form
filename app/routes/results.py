# 라우트 및 뷰 정의
from flask import render_template, request, jsonify, redirect, url_for, session
from flask.views import MethodView
from flask_smorest import Blueprint
from app.models import db, Question, DetailQuestion, Answer, User, Image


result_blp = Blueprint("result", __name__, description='content api') # 매개변수 (블루프린트 이름, 블루프린트 모듈 이름(import할 이름))

# 기본 화면
@post_blp.route('/results/<int:user_id>', methods=['GET'])
def result(user_id):
    # 사용자의 응답 데이터 가져오기
    answers = Answer.query.filter_by(user_id=user_id).all()

    # 필요한 통계 데이터 계산 (예시)
    results_data = {
        "total_answers": len(answers),
        "same_result_chart": [],  # Plotly 그래프 데이터 추가
        "age_chart": [],
        "gender_chart": [],
        "age_distribution_chart": [],
        "question_charts": []
    }

    # 결과 HTML 렌더링
    return render_template('results.html', results=results_data)