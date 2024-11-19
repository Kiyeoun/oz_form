# 라우트 및 뷰 정의
from flask import render_template, request, jsonify, redirect, url_for, session
from flask_smorest import Blueprint
from app.models import db, Question, DetailQuestion, Answer

post_blp = Blueprint("post_question", __name__, description='content api') # 매개변수 (블루프린트 이름, 블루프린트 모듈 이름(import할 모듈명))

# 질문지 POST요청 처리하기
@post_blp.route('/question/<int:sqe>', methods=['POST'])
def POST_detail_question(sqe):
	if request.method == 'POST':
		# 쿼리 문자열, session user_id 가져오기
		user_id = session.get('user_id')
		if not user_id:
			return redirect(url_for('routes.signup')), 400
		
		# 사용자의 응답 데이터 저장
		detail_question_id = request.form.get('answer') # form에서 name이 answer인 곳에서 정보를 가져온다
		if not detail_question_id:
			return "답변 정보가 필요합니다.", 400

		# 응답 저장
		duplicate_filter = Answer.query.filter_by(user_id=user_id, detail_question_id=detail_question_id).first()
		if duplicate_filter:
			duplicate_filter.detail_question_id = detail_question_id
		else:
			answer = Answer(user_id=user_id, detail_question_id=detail_question_id)
			db.session.add(answer)
		db.session.commit()

		# 다음 질문으로 이동
		next_question = Question.query.filter_by(sqe=sqe + 1).first()
		if next_question:
			return redirect(url_for('post_question.POST_detail_question', sqe=sqe + 1, user_id=user_id))
		else:
			return redirect(url_for('post_question.result', user_id=user_id))


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