import streamlit as st
import ast
import re
from database import get_wrong_questions
from ai_service import (
    generate_ai_explanation,
    generate_similar_problem
)


st.set_page_config(
    page_title="오답 다시풀기",
    page_icon="📝",
    layout="wide"
)

st.title("📝 오답 다시풀기")

if "selected_exam" not in st.session_state:
    st.warning("선택된 시험이 없습니다.")
    st.stop()

exam_id = st.session_state.selected_exam

questions = get_wrong_questions(exam_id)

if len(questions) == 0:
    st.warning("오답이 없습니다.")
    st.stop()

if "retry_index" not in st.session_state:
    st.session_state.retry_index = 0

idx = st.session_state.retry_index

chapter, concept, difficulty, question, choices, my_answer, correct_answer, explanation = questions[idx]

choices = ast.literal_eval(choices)

st.progress((idx + 1) / len(questions))

st.subheader(f"문제 {idx+1} / {len(questions)}")

st.write(question)

answer = st.radio(
    "정답을 선택하세요.",
    choices,
    index=None,
    key=f"retry_answer_{idx}"
)

if st.button("정답 확인"):

    if answer == choices[correct_answer]:
        st.success("정답입니다!")

    else:
        st.error("오답입니다.")
        st.write(f"정답 : {choices[correct_answer]}")

st.divider()

if st.button("🤖 AI 해설 생성"):

    with st.spinner("AI가 해설을 생성하는 중입니다..."):

        import time
        time.sleep(2)

    answer = st.session_state.get(f"retry_answer_{idx}")

    if "ai_result" not in st.session_state:

        with st.spinner("AI가 해설을 생성하는 중입니다..."):
            result = generate_ai_explanation(
                question,
                choices,
                correct_answer,
                answer
            )
            st.session_state.ai_result = result

    st.success("AI 해설 생성 완료!")
    
if "ai_result" in st.session_state:
    st.markdown(st.session_state.ai_result)

st.divider()

if st.button("🔄 유사문제 생성"):

    if "similar_problem" not in st.session_state:

        with st.spinner("AI가 유사문제를 생성하는 중입니다..."):

            result = generate_similar_problem(
                question,
                choices,
                correct_answer,
                chapter,
                concept,
                difficulty
            )

            st.session_state.similar_problem = result

    st.success("유사문제 생성 완료!")

if "similar_problem" in st.session_state:
    result = st.session_state.similar_problem
    problem_part, answer_part = result.split("### 정답", 1)


    match = re.search(r"①|②|③|④", answer_part)

    if match:
            ai_correct_answer = match.group()
    else:
            ai_correct_answer = None

    st.markdown(problem_part)
    user_answer = st.radio(
    "답을 선택하세요.",
    ["①", "②", "③", "④"],
    index=None,
    key=f"similar_answer_{idx}"
    )

    if st.button("정답 확인", key=f"similar_check_{idx}"):

        if user_answer is None:
            st.warning("답을 선택해주세요.")

        else:

            if ai_correct_answer is None:
                st.error("AI 정답을 찾을 수 없습니다.")

            elif user_answer == ai_correct_answer:
                st.success("🎉 정답입니다!")

            else:
                st.error("❌ 오답입니다.")
                st.write(f"정답 : **{ai_correct_answer}**")

            # "### 해설" 이후는 제거
            if "### 해설" in answer_part:
                answer_part = answer_part.split("### 해설")[0]
            st.markdown(answer_part)
    
st.divider()

col1, col2, col3 = st.columns(3)

with col1:

    if idx > 0:
        if st.button("⬅ 이전"):
            st.session_state.pop("ai_result", None)
            st.session_state.pop("similar_problem", None)

            st.session_state.retry_index -= 1
            st.rerun()

with col2:

    if st.button("📂 오답노트"):

        st.session_state.retry_index = 0

        st.session_state.pop("ai_result", None)
        st.session_state.pop("similar_problem", None)

        st.switch_page("pages/오답노트.py")

with col3:

    if idx < len(questions)-1:

        if st.button("다음 ➡"):
            st.session_state.pop("ai_result", None)
            st.session_state.pop("similar_problem", None)

            st.session_state.retry_index += 1
            st.rerun()

    else:

        if st.button("✅ 종료"):

            st.session_state.retry_index = 0

            st.session_state.pop("ai_result", None)
            st.session_state.pop("similar_problem", None)

            st.switch_page("pages/오답노트.py")