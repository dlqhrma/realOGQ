import streamlit as st

st.set_page_config(page_title="AI 문제 생성", page_icon="📘")

st.title("📘 AI 문제 생성")
st.write("원하는 조건을 선택한 후 AI가 문제를 생성합니다.")

st.divider()

# 단원 선택
chapter = st.selectbox(
    "📚 단원 선택",
    [
        "베어링",
        "용접",
        "윤활",
        "유압·공압",
        "기계요소"
    ]
)

# 난이도
difficulty = st.radio(
    "🎯 난이도",
    ["쉬움", "보통", "어려움"],
    horizontal=True
)

# 문제 수
count = st.slider(
    "📝 문제 수",
    5,
    20,
    10
)

st.divider()

if st.button("🤖 문제 생성", use_container_width=True):
    st.success("AI 연결 예정입니다.")
    st.write(f"단원 : {chapter}")
    st.write(f"난이도 : {difficulty}")
    st.write(f"문제 수 : {count}문제")