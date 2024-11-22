from flask import render_template, request
from flask_smorest import Blueprint
from app.models import db, Question, Answer, DetailQuestion
import plotly.express as px
import plotly.utils
import json

result_blp = Blueprint("results", __name__, description='Result API')  # Blueprint 생성

@result_blp.route('/results/<int:user_id>', methods=['GET'])
def result(user_id):
    # 사용자의 답변 가져오기
    user_answers = Answer.query.filter_by(user_id=user_id).all()

    if not user_answers:
        return render_template("results.html", same_result_chart=None, question_charts={})

    # 전체 응답 데이터 가져오기
    all_answers = db.session.query(Answer, DetailQuestion).join(
        DetailQuestion, Answer.detail_question_id == DetailQuestion.id
    ).all()

    # 사용자의 답변 데이터를 딕셔너리로 변환 (질문 ID: 선택지 ID)
    user_answer_dict = {answer.question_id: answer.detail_question_id for answer in user_answers}

    # 질문 ID 추출 (1~4번 질문)
    question_ids = list(user_answer_dict.keys())

    # 동일한 답변을 한 사람들의 ID 추출
    matching_user_ids = set()
    for answer, detail_question in all_answers:
        if (
            answer.question_id in question_ids
            and answer.detail_question_id == user_answer_dict[answer.question_id]
        ):
            matching_user_ids.add(answer.user_id)

    # 완벽히 동일한 응답을 한 사람만 필터링
    perfect_matches = []
    for user_id in matching_user_ids:
        user_responses = Answer.query.filter_by(user_id=user_id).all()
        user_response_dict = {answer.question_id: answer.detail_question_id for answer in user_responses}

        if all(user_answer_dict[qid] == user_response_dict.get(qid) for qid in question_ids):
            perfect_matches.append(user_id)

    # 전체 응답자 수
    total_count = len(set(answer.user_id for answer, _ in all_answers))

    # 동일한 응답자 비율
    perfect_match_count = len(perfect_matches)
    same_result_data = {
        "labels": ["나", "다른 사람들"],
        "values": [perfect_match_count, total_count - perfect_match_count],
    }

    # Plotly Pie Chart 생성
    same_result_chart = px.pie(
        data_frame=same_result_data,
        names="labels",
        values="values",
        title="나와 같은 대답을 한 사람과의 비율"
    )
    
    same_result_chart.update_layout(
        height=750,  # 차트 세로 크기
        title_x=0.5,  # 제목을 중앙에 배치
        title_y=0.95,  # 제목을 위쪽에 배치
        margin=dict(l=150, r=50),  # 여백 설정 (왼쪽, 오른쪽, 위, 아래 여백)
        title_font=dict( size = 30 )
    )

    
    same_result_chart = json.dumps(same_result_chart, cls=plotly.utils.PlotlyJSONEncoder)

    # 각 질문별 응답 수 계산
    question_charts = {}
    questions = Question.query.all()

    for question in questions:
        # 해당 질문에 대한 응답만 필터링
        question_answers = [
            detail_question.content for answer, detail_question in all_answers if answer.question_id == question.id
        ]
        if not question_answers:  # 응답이 없는 경우 스킵
            continue
        
        # 답변 빈도수 계산
        answer_counts = {}
        for answer_content in question_answers:
            answer_counts[answer_content] = answer_counts.get(answer_content, 0) + 1

        # 데이터프레임 구성
        chart_data = {
            "답변": list(answer_counts.keys()),
            "응답 수": list(answer_counts.values()),
        }

        # Plotly Bar Chart 생성
        question_chart = px.bar(
            data_frame=chart_data,
            x="답변",
            y="응답 수",
            title=f"{question.title}"
        )

        # 레이아웃 조정: x축 텍스트 크기와 각도 설정
        question_chart.update_layout(
            xaxis={
                "tickangle": 0,  # 텍스트를 0도로 세로 배치
                "automargin": True,  # 텍스트가 차트와 겹치지 않도록 여백 자동 추가
                "tickfont": {"size": 12},  # 텍스트 크기
            },
            xaxis_tickmode="linear",
            width=1000,  # 그래프 가로 크기
            height=700,  # 그래프 세로 크기
            title_x=0.5,  # 제목을 중앙에 배치
            title_y=0.95,  # 제목을 위쪽에 배치
            title_font=dict(
                            size=30
            )
        )

        question_charts[question.id] = json.dumps(
            question_chart, cls=plotly.utils.PlotlyJSONEncoder
        )

    # 결과 HTML 렌더링
    return render_template(
        "results.html",
        same_result_chart=same_result_chart,
        question_charts=question_charts,
    )
