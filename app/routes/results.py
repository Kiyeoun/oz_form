from flask import render_template
from flask_smorest import Blueprint
from app.models import db, Question, Answer, DetailQuestion
import plotly.express as px
import plotly.utils
import json

result_blp = Blueprint("results", __name__, description="Result API")  # Blueprint 생성


@result_blp.route("/results/<int:user_id>", methods=["GET"])
def result(user_id):
    # 사용자의 답변 가져오기
    user_answers = db.session.query(Answer, DetailQuestion, Question).join(
    DetailQuestion, Answer.detail_question_id == DetailQuestion.id
    ).join(
        Question, Answer.question_id == Question.id
    ).filter(Answer.user_id == user_id).all()

    # 사용자 답변이 없는 경우 처리
    if not user_answers:
        return render_template("results.html", same_result_chart=None, question_charts={}, user_answers=[])

    # 사용자 답변 목록 생성
# 사용자 답변 목록 생성
    user_answer_list = [
    {"question": answer[2].title, "answer": answer[1].content}
    for answer in user_answers
    ]

    # 전체 응답 데이터 가져오기
    all_answers = db.session.query(Answer, DetailQuestion).join(
        DetailQuestion, Answer.detail_question_id == DetailQuestion.id
    ).all()

    # 사용자의 답변 데이터를 딕셔너리로 변환 (질문 ID: 선택지 ID)
    user_answer_dict = {answer[0].question_id: answer[0].detail_question_id for answer in user_answers}


    # 질문 ID 추출
    question_ids = list(user_answer_dict.keys())

    # 동일한 응답을 한 사람들의 ID 추출
    matching_user_ids = {
        answer.user_id
        for answer, detail_question in all_answers
        if answer.question_id in question_ids
        and answer.detail_question_id == user_answer_dict[answer.question_id]
    }

    # 완벽히 동일한 응답을 한 사람만 필터링
    perfect_matches = [
        uid
        for uid in matching_user_ids
        if all(
            user_answer_dict[qid] == Answer.query.filter_by(user_id=uid, question_id=qid).first().detail_question_id
            for qid in question_ids
        )
    ]

    # 전체 응답자 수 및 동일한 응답자 비율 계산
    total_count = len(set(answer.user_id for answer, _ in all_answers))
    perfect_match_count = len(perfect_matches)

    # 동일한 답변 비율 Pie Chart 생성
    same_result_chart = px.pie(
        data_frame={"labels": ["나", "다른 사람들"], "values": [perfect_match_count, total_count - perfect_match_count]},
        names="labels",
        values="values",
        title="나와 같은 대답을 한 사람과의 비율",
    )
    same_result_chart.update_layout(
        width=900,
        height=650,
        title_x=0.53,  # 타이틀을 가로축 가운데 정렬
        title_y=0.99,  # 타이틀의 y 위치 설정
        margin=dict(l=160, r=0, t=50, b=0),  # 여백을 최소화
        title_font=dict(size=30),
        paper_bgcolor="rgba(0,0,0,0)",  # 차트 배경 투명
        plot_bgcolor="rgba(0,0,0,0)"  # 플롯 영역 배경 투명
    )


    same_result_chart = json.dumps(same_result_chart, cls=plotly.utils.PlotlyJSONEncoder)

    # 각 질문별 응답 수 계산 및 Bar Chart 생성
    question_charts = {}
    for question in Question.query.all():
        # 해당 질문에 대한 응답만 필터링
        question_answers = [
            detail_question.content for answer, detail_question in all_answers if answer.question_id == question.id
        ]
        if not question_answers:  # 응답이 없는 경우 스킵
            continue

        # 답변 빈도수 계산
        answer_counts = {content: question_answers.count(content) for content in set(question_answers)}

        # Bar Chart 생성
        question_chart = px.bar(
            data_frame={"답변": list(answer_counts.keys()), "응답 수": list(answer_counts.values())},
            x="답변",
            y="응답 수",
            title=f"{question.title}",
        )
        question_chart.update_layout(
            xaxis={
                "tickangle": 0,
                "automargin": True,
                "tickfont": {"size": 12},
            },
            width=1000,
            height=700,
            title_x=0.5,
            title_y=0.95,
            title_font=dict(size=30),
        )
        question_charts[question.id] = json.dumps(question_chart, cls=plotly.utils.PlotlyJSONEncoder)

    # 결과 HTML 렌더링
    return render_template(
        "results.html",
        same_result_chart=same_result_chart,
        question_charts=question_charts,
        user_answers=user_answer_list,
    )
