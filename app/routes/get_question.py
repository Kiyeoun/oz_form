# 라우트 및 뷰 정의
from flask import render_template, request, redirect, url_for, session, flash
from flask_smorest import Blueprint
from app.models import db, Question, DetailQuestion

get_blp = Blueprint("get_question", __name__, description='get api') # 매개변수 (블루프린트 이름, 블루프린트 모듈 이름(import할 이름))

# 질문지 화면 받아오기
@get_blp.route('/question/<int:sqe>', methods=['GET'])
def GET_detail_question(sqe):
	if request.method == 'GET':
		user_id = session.get('user_id') # Flask session에서 user_id를 가져온다
		if not user_id:
			flash('로그인이 필요합니다. 회원가입 페이지로 이동합니다.', 'warning')
			return redirect(url_for('signup.Signup'))
		# #쿼리 문자열에서 user_id 가져오기, 세션x버전
		# user_id = request.args.get('user_id', type=int)
		# if not user_id:
		#	 return "사용자 ID가 필요합니다.", 400

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