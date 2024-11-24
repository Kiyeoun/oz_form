from flask import render_template
from flask_smorest import Blueprint
from app.models import db, Question, Answer, DetailQuestion
import plotly.express as px
import plotly.utils
import json

result_blp = Blueprint("results", __name__, description="Result API")  # Blueprint 생성

@result_blp.route("/results/<int:user_id>", methods=["GET"])
def result(user_id):
    # 사용자 답변 로드
    user_answers = db.session.query(Answer, DetailQuestion, Question).join(
        DetailQuestion, Answer.detail_question_id == DetailQuestion.id
    ).join(
        Question, Answer.question_id == Question.id
    ).filter(Answer.user_id == user_id).all()

    if not user_answers:
        return render_template("results.html", same_result_chart=None, question_charts={}, user_answers=[])

    # 사용자 답변 요약: 각 질문과 선택한 상세 질문 저장
    user_answer_dict = {
        answer[0].question_id: answer[0].detail_question_id for answer in user_answers
    }
    user_answer_list = [
        {"question_title": answer[2].title, "dq_content": answer[1].content}
        for answer in user_answers
    ]

    # 전체 응답 데이터 로드
    all_user_answers = db.session.query(Answer, DetailQuestion).join(
        DetailQuestion, Answer.detail_question_id == DetailQuestion.id
    ).all()

    # 동일한 응답을 한 사용자 ID 추출
    same_answer_user_ids = {
        answer.user_id
        for answer, detail_question in all_user_answers
        if answer.question_id in user_answer_dict and
            answer.detail_question_id == user_answer_dict[answer.question_id]
    }

    # 완전히 동일한 응답을 한 사용자 ID 추출
    perfect_matches = [
        uid
        for uid in same_answer_user_ids
        if all(
            user_answer_dict[qid] == Answer.query.filter_by(user_id=uid, question_id=qid).first().detail_question_id
            for qid in user_answer_dict
        )
    ]

    # 통계 계산
    total_users = len(set(answer.user_id for answer, _ in all_user_answers))
    perfect_match_count = len(perfect_matches)

    # Pie Chart 생성
    same_result_chart = px.pie(
        data_frame={
            "labels": ["나", "다른 사람들"],
            "values": [perfect_match_count, total_users - perfect_match_count],
        },
        names="labels",
        values="values",
        title="나와 같은 대답을 한 사람과의 비율",
    )
    same_result_chart.update_layout(
        width=900, height=650, title_x=0.53, title_y=0.99,
        margin=dict(l=160, r=0, t=50, b=0),
        title_font=dict(size=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    same_result_chart = json.dumps(same_result_chart, cls=plotly.utils.PlotlyJSONEncoder)

    # 질문별 Bar Chart 생성
    question_charts = {}
    for question in Question.query.all():
        question_answers = [
            detail_question.content
            for answer, detail_question in all_user_answers
            if answer.question_id == question.id
        ]
        if not question_answers:
            continue

        answer_counts = {content: question_answers.count(content) for content in set(question_answers)}
        sorted_answers = sorted(answer_counts.items(), key=lambda x: x[0])  # 키 값(content) 기준으로 정렬
        question_chart = px.bar(
            data_frame={
                "답변": [item[0] for item in sorted_answers],  # 정렬된 키
                "응답 수": [item[1] for item in sorted_answers],  # 정렬된 값
            },
            x="답변",
            y="응답 수",
            title=f"{question.title}",
        )
        question_chart.update_layout(
            xaxis={"tickangle": 0, "automargin": True, "tickfont": {"size": 12}},
            width=1000, height=700, title_x=0.5, title_y=0.95,
            title_font=dict(size=30),
        )
        question_charts[question.id] = json.dumps(question_chart, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template(
        "results.html",
        same_result_chart=same_result_chart,
        question_charts=question_charts,
        user_answers=user_answer_list,
    )
