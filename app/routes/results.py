from flask import render_template, session, redirect, url_for, flash
from flask_smorest import Blueprint
from app.models import db, Question, Answer, DetailQuestion
import plotly.express as px
import plotly.utils
import json
from typing import Dict, List, Tuple, Set, Optional
import sys

result_blp = Blueprint("results", __name__, description="Result API")

# pie 차트 만드는 함수
def create_pie_chart(perfect_match_count: int, total_users: int) -> str:
    chart = px.pie(
        data_frame={
            "labels": ["나", "다른 사람들"],
            "values": [perfect_match_count, total_users - perfect_match_count],
        },
        names="labels",
        values="values",
        title="나와 같은 대답을 한 사람과의 비율",
    )
    chart.update_layout(
        width=900, height=650,
        title_x=0.53, title_y=0.99,
        margin=dict(l=160, r=0, t=50, b=0),
        title_font=dict(size=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return json.dumps(chart, cls=plotly.utils.PlotlyJSONEncoder)

# bar 차트 만드는 함수
def create_bar_chart(question_title: str, answer_data: List[Tuple[str, int, int]], ordered_categories: List[str]) -> str:
    df_data = {
        "답변": [item[0] for item in answer_data],
        "응답 수": [item[2] for item in answer_data]
    }
    chart = px.bar(
        data_frame=df_data,
        x="답변",
        y="응답 수",
        title=question_title,
        category_orders={"답변": ordered_categories}
    )
    chart.update_layout(
        xaxis={"tickangle": 0, "automargin": True, "tickfont": {"size": 12}},
        width=1000, height=700,
        title_x=0.5, title_y=0.95,
        title_font=dict(size=30),
    )
    return json.dumps(chart, cls=plotly.utils.PlotlyJSONEncoder)

# 유저가 선택한 질문지에 대한 정보를 가져오는 함수
def get_user_answers(user_id: int) -> Optional[Tuple[List, Dict[int, int], List[Dict[str, str]]]]:
    # user_id가 일치하는 정보 중 db의 Answer, DQ, Question을 join해서 가져온다
    user_answers = db.session.query(Answer, DetailQuestion, Question).join(
        DetailQuestion, DetailQuestion.id == Answer.detail_question_id
    ).join(
        Question, Question.id == Answer.question_id
    ).filter(Answer.user_id == user_id).all()
    if not user_answers:
        return None
    
    
    # user_id가 선택한 질문지를 dict 형태로 가져온다 -> {q_id: dq_id, ...}
    user_answer_id = {
        answer[0].question_id: answer[0].detail_question_id
        for answer in user_answers
    }
    # 확인해볼 수 있는 코드
    # print(user_answer_id, file = sys.stderr)
    
    
    # user_id가 선택한 {question_title: q.title, dq_content: dq.content}를 리스트로 전부 가져온다
    # 그래프의 x축에 dq_id가 아닌 dq_content를 넣어주기 위한 코드
    user_answer_content = [
        {"question_title": answer[2].title, "dq_content": answer[1].content}
        for answer in user_answers
    ]
    # 확인해볼 수 있는 코드
    # print(user_answer_content, file = sys.stderr)
    
    return user_answers, user_answer_id, user_answer_content

# 완벽하게 동일한 답변을 가진 유저 체크하는 함수
def get_perfect_matches(user_answer_id: Dict[int, int], all_user_answers: List[Tuple[Answer, DetailQuestion]]) -> Tuple[List[int], int]:
    # 나와 q_id, dq_id가 1개라도 같으면 same_answer_uesr_ids에 담는다, 집합이므로 중복되지 않는다
    same_answer_user_ids: Set[int] = { # 집합 컴프리헨션 {}
        answer.user_id
        for answer in all_user_answers
        if answer.question_id in user_answer_id and
            answer.detail_question_id == user_answer_id[answer.question_id]
    }
    # 앞서 할당한 same_answer_user_ids를 통해 나와 q_id, dq_id가 전부 같은 사람을 구하는 코드
    perfect_matches = [
        uid for uid in same_answer_user_ids
        if all( # all은 하나라도 false가 나오면 뒤에는 검사하지 않고 바로 false시킨다
            user_answer_id[qid] == Answer.query.filter_by( # 제너레이터 표현식 컴프리헨션에서 ()만 다름
                user_id=uid, question_id=qid
            ).first().detail_question_id
            for qid in user_answer_id # dict는 key값을 전달한다, value도 전달하고 싶으면 items()를 쓰면 된다
        )
    ]
    total_users = len(set(answer.user_id for answer in all_user_answers)) # 집합 컴프리헨션
    return perfect_matches, total_users

def get_question_answer_data(question_id: int) -> Optional[List[Tuple[str, int, int]]]:
    """Fetch answer data for a specific question."""
    return db.session.query(
        DetailQuestion.content,
        DetailQuestion.id,
        db.func.count(Answer.id).label('count')
    ).join(
        Answer, DetailQuestion.id == Answer.detail_question_id
    ).filter(
        Answer.question_id == question_id
    ).group_by(
        DetailQuestion.content, DetailQuestion.id
    ).order_by(
        DetailQuestion.sqe
    ).all()


# 메인 라우트

@result_blp.route("/results/<int:user_id>", methods=["GET"])
def result(user_id: int):
    # user_id가 세션에 존재하는지 체크
    session_user_id = session.get('user_id')
    if not session_user_id:
        flash('로그인이 필요합니다.', 'warning')
        return redirect(url_for('signup.Signup'))
    if session_user_id != user_id:
        flash('본인의 결과만 확인할 수 있습니다.', 'danger')
        return redirect(url_for('results.result', user_id=session_user_id))
    
    # 유저 답변 데이터 가져오기
    user_answer_data = get_user_answers(user_id)
    if not user_answer_data: # 유저 데이터가 없으면 빈페이지
        return render_template("results.html", same_result_chart=None, question_charts={}, user_answers=[])
    # 각 변수 할당
    user_answer_id = user_answer_data[1]
    user_answer_content = user_answer_data[2]

    # 모든 유저의 답변 데이터 가져오기
    all_user_answers = db.session.query(Answer).all()
    # 확인해볼 수 있는 코드
    # print(all_user_answers, file = sys.stderr)

    # Identify Perfect Matches
    perfect_matches, total_users = get_perfect_matches(user_answer_id, all_user_answers)

    # 차트 생성
    same_result_chart = create_pie_chart(len(perfect_matches), total_users)
    question_charts = {}
    for question in Question.query.all():
        answer_data = get_question_answer_data(question.id)
        if not answer_data:
            continue
        ordered_categories = [item[0] for item in answer_data]
        question_charts[question.id] = create_bar_chart(
            question.title,
            answer_data,
            ordered_categories
        )

    # Render Template
    return render_template(
        "results.html",
        same_result_chart=same_result_chart,
        question_charts=question_charts,
        user_answers=user_answer_content,
    )
