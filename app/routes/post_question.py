# 라우트 및 뷰 정의
from flask import request, redirect, url_for, session, flash
from flask_smorest import Blueprint
from app.models import db, Question, Answer

post_blp = Blueprint("post_question", __name__, description='post api') # 매개변수 (블루프린트 이름, 블루프린트 모듈 이름(import할 모듈명))

# 질문지 POST요청 처리하기
@post_blp.route('/question/<int:sqe>', methods=['POST'])
def POST_detail_question(sqe): # sqe는 URL 경로에서 받아온다
	if request.method == 'POST': # 혹시 모르니까 1번 더 POST 필터링
		# 쿼리 문자열, session user_id 가져오기
		user_id = session.get('user_id')
		if not user_id:
			flash('로그인이 필요합니다. 메인 화면으로 이동합니다.', 'warning')
			return redirect(url_for('signup.index'))

		# 세션에서 사용자가 접근할 수 있는 질문 번호 확인
		current_step = session.get('current_question', 1) # current_question이라는 key가 없으면 초기 value 1으로 설정
		# 사용자가 건너뛰기를 시도한 경우
		if sqe > current_step:
			flash("질문을 순서대로 진행해주세요.")
			return redirect(url_for('post_question.POST_detail_question', sqe=current_step, user_id = user_id))

		# 사용자의 응답 데이터 저장
		question_dict= Question.query.filter_by(sqe=sqe).first()
		detail_question_id = request.form.get('answer') # form에서 name이 answer인 곳에서 정보를 가져온다
		if not detail_question_id: # 답변을 선택하지 않았을 때 html에서 버튼을 활성화시키지 않겠지만 한번 더 필터링
			return "답변 정보가 필요합니다.", 400

		# 응답 저장
		duplicate_filter = Answer.query.filter_by(user_id = user_id, question_id = question_dict.id).first()
		if duplicate_filter: # duplicate_filter를 이용해 user_id와 question_id가 같은 값이 존재하면 dq_id의 값을 수정
			duplicate_filter.detail_question_id = detail_question_id
		else: # 존재하지 않으면 새로운 값을 생성
			answer = Answer(user_id=user_id, question_id=question_dict.id, detail_question_id=detail_question_id)
			db.session.add(answer)
		db.session.commit()

		# 다음 질문으로 이동
		next_question = Question.query.filter_by(sqe=sqe + 1).first()
		if next_question:
			session['current_question'] = sqe + 1
			return redirect(url_for('post_question.POST_detail_question', sqe=sqe + 1, user_id=user_id))
		else: # user_id는 라우트에 명시돼있지 않기 때문에 쿼리문자열(?user_id=<값>)으로 들어간다
			return redirect(url_for('results.result', user_id=user_id))
