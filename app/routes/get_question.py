# 라우트 및 뷰 정의
from flask import render_template, request, jsonify, redirect, url_for, session
from flask.views import MethodView
from flask_smorest import Blueprint
from app.models import db, Question, DetailQuestion, Answer, User, Image

get_blp = Blueprint("get_question", __name__, description='content api') # 매개변수 (블루프린트 이름, 블루프린트 모듈 이름(import할 이름))

# 질문지 화면 받아오기
@get_blp.route('/question/<int:sqe>', methods=['GET'])
def GET_detail_question(sqe):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('routes.signup')), 400
    # #쿼리 문자열에서 user_id 가져오기
    # user_id = request.args.get('user_id', type=int)
    # if not user_id:
    #     return "사용자 ID가 필요합니다.", 400

    if request.method == 'GET':
        # 질문 정보 가져오기
        question = Question.query.filter_by(sqe=sqe).first()
        if not question:
            return "질문을 찾을 수 없습니다.", 404

        # 선택지 가져오기
        choices = DetailQuestion.query.filter_by(question_id=question.id).all()
        image = question.image # relationship으로 연결되어 있기 때문에 question.image로 image의 모든 정보를 가져올 수 있다.
        
        
        # HTML 렌더링
        return render_template(
            'question.html',
            question=question.to_dict(),
            choices=[choice.to_dict() for choice in choices],
            image=image.to_dict(),
            user_id=user_id
        )