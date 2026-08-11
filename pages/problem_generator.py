import streamlit as st
import re
from ai_service import (
    generate_problems,
    generate_ai_explanation
)

st.set_page_config(page_title="AI 문제 생성", page_icon="📘")

st.title("📘 AI 문제 생성")
st.write("원하는 조건을 선택한 후 AI가 문제를 생성합니다.")

st.divider()

# 단원 선택
chapter = st.selectbox(
    "📚 단원 선택",
    [
        "기계구동장치",
        "공유압장치",
        "전기전자장치",
        "용접 및 안전관리"
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

if "problem_list" not in st.session_state:
    st.session_state.problem_list = []

if "current_index" not in st.session_state:
    st.session_state.current_index = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "show_result" not in st.session_state:
    st.session_state.show_result = False

if "answered" not in st.session_state:
    st.session_state.answered = False
    
if "ai_explanation" not in st.session_state:
    st.session_state.ai_explanation = ""

if st.button("🤖 문제 생성", use_container_width=True):

    with st.spinner("AI가 문제를 생성하는 중입니다..."):

        try:
            result = generate_problems(
                chapter,
                difficulty,
                count
            )
        except Exception:
            st.error("AI 문제 생성을 실패했습니다. 잠시 후 다시 시도해주세요.")
            st.stop()
            
    st.session_state.problem_list = re.split(
    r"(?=### 문제)",
    result
    )

    st.session_state.problem_list = [
        p.strip()
        for p in st.session_state.problem_list
        if p.strip()
    ]

    st.session_state.current_index = 0
    st.session_state.score = 0
    st.session_state.show_result = False
    st.session_state.answered = False
    st.session_state.ai_explanation = ""

if st.session_state.generated_problems:

    text = st.session_state.problem_list[
        st.session_state.current_index
    ]
    
    match = re.search(
        r"### 보기\s*(.*?)### 정답",
        text,
        re.S
    )

    if match is None:
        st.error("AI가 예상과 다른 형식으로 문제를 생성했습니다. 다시 생성해주세요.")
        st.code(text)
        st.stop()

    choice_text = match.group(1).strip()


    # 문제
    question = re.search(
        r"### 문제\s*(.*?)### 보기",
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
    
    answer_index = {
        "①": 0,
        "②": 1,
        "③": 2,
        "④": 3
    }[answer[0]]


    st.subheader(
        f"문제 {st.session_state.current_index + 1} / {len(st.session_state.problem_list)}"
    )

    st.write(question)

    user_answer = st.radio(
        "답을 선택하세요.",
        choices
    )

    if not st.session_state.answered:

        if st.button("정답 확인"):

            st.session_state.show_result = True
            st.session_state.answered = True

            correct = answer[0]
            selected = user_answer[0]

            if selected == correct:
                st.success("정답입니다!")
                st.session_state.score += 1
            else:
                st.error("오답입니다.")
            
            with st.spinner("AI가 해설을 생성하는 중입니다..."):

                try:
                    st.session_state.ai_explanation = generate_ai_explanation(
                        question=question,
                        choices=choices,
                        correct_answer=answer_index,
                        user_answer=user_answer
                    )

                except Exception:
                    st.session_state.ai_explanation = (
                        "AI 해설을 생성하지 못했습니다.\n"
                        "잠시 후 다시 시도해주세요."
                    )
                
    if st.session_state.show_result:

        st.markdown("### 정답")
        st.write(answer)
        
        st.markdown(st.session_state.ai_explanation)
    
        if st.session_state.current_index < len(st.session_state.problem_list) - 1:

            if st.button("다음 문제"):

                st.session_state.current_index += 1
                st.session_state.show_result = False
                st.session_state.answered = False
                st.session_state.ai_explanation = ""
                
                st.rerun()

        else:

            st.success("모든 문제를 완료했습니다!")

            total = len(st.session_state.problem_list)
            correct = st.session_state.score
            wrong = total - correct
            accuracy = (correct / total) * 100

            st.write(f"총 문제 : {total}")
            st.write(f"정답 : {correct}")
            st.write(f"오답 : {wrong}")
            st.write(f"정답률 : {accuracy:.1f}%")
        
            col1, col2 = st.columns(2)

            with col1:
                if st.button("다시 문제 생성", use_container_width=True):

                    st.session_state.generated_problems = ""
                    st.session_state.problem_list = []
                    st.session_state.current_index = 0
                    st.session_state.score = 0
                    st.session_state.show_result = False
                    st.session_state.answered = False
                    st.session_state.ai_explanation = ""

                    st.rerun()

            with col2:
                if st.button("🏠 Home", use_container_width=True):

                    st.session_state.generated_problems = ""
                    st.session_state.problem_list = []
                    st.session_state.current_index = 0
                    st.session_state.score = 0
                    st.session_state.show_result = False
                    st.session_state.answered = False
                    st.session_state.ai_explanation = ""

                    st.switch_page("pages/home.py")
