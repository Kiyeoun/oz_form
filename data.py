import plotly.graph_objects as go

axis = {}
n = 5

men = ["상훈", "수현", "파머"]

for name in men:
    if name not in axis:
        axis[name] = []
    axis[name].extend(range(1, n * n))
    n += 1


x_axis = list(axis.keys())


y_axis = [sum(values) for values in axis.values()]


fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=x_axis,
        y=y_axis,
        hovertemplate="선택 문항 = %{x}<br>선택한 사람 수 = %{y}<extra></extra>",  # 툴팁 텍스트 정의
    )
)

fig.update_layout(
    xaxis=dict(
        title="선택 문항",  # x축의 타이틀 설정
    ),
    yaxis=dict(
        title="선택한 사람 수",  # y축의 타이틀 설정
    ),
)

fig.show()