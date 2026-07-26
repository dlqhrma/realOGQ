import streamlit as st
import re
from ai_service import generate_problems

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
        "유압",
        "공압",
        "기계요소"
    ]
)

# 난이도
difficulty = st.segmented_control(
    "🎯 난이도",
    options=["쉬움", "보통", "어려움"],
    default="보통"
)
# 문제 수
count = st.slider(
    "📝 문제 수",
    1,
    10,
    5
)

st.divider()

if "generated_problems" not in st.session_state:
    st.session_state.generated_problems = ""

if "show_result" not in st.session_state:
    st.session_state.show_result = False

if st.button("🤖 문제 생성", use_container_width=True):

    with st.spinner("AI가 문제를 생성하는 중입니다..."):

        result = generate_problems(
            chapter,
            difficulty,
            count
        )

    st.session_state.generated_problems = result

if st.session_state.generated_problems:

    text = st.session_state.generated_problems

    # 문제
    question = re.search(
        r"### 문제\s*(.*?)### 보기",
        text,
        re.S
    ).group(1).strip()

    # 보기
    choice_text = re.search(
        r"### 보기\s*(.*?)### 정답",
        text,
        re.S
    ).group(1).strip()

    choices = re.findall(
        r"[①②③④].*?(?=[①②③④]|$)",
        choice_text,
        re.S
    )

    # 정답
    answer = re.search(
        r"### 정답\s*(.*?)### 해설",
        text,
        re.S
    ).group(1).strip()

    # 해설
    explanation = re.search(
        r"### 해설\s*(.*?)### 단원",
        text,
        re.S
    ).group(1).strip()

    st.subheader("문제")

    st.write(question)

    user_answer = st.radio(
        "답을 선택하세요.",
        choices
    )

    if st.button("정답 확인"):

        if answer in user_answer:
            st.success("정답입니다!")
        else:
            st.error("오답입니다.")

        st.markdown("### 정답")
        st.write(answer)

        st.markdown("### 해설")
        st.write(explanation)