import streamlit as st
from database import get_exam_history_for_note
from supabase_db import log_activity

st.set_page_config(
    page_title="오답노트",
    page_icon="📂",
    layout="wide"
)

col1, col2 = st.columns([6, 1])

with col1:
    st.title("📂 오답노트")

with col2:
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("pages/home.py")

history = get_exam_history_for_note(
    st.session_state.user_id
)

if history and not st.session_state.get("wrong_note_logged", False):
    log_activity(
        st.session_state.user_id,
        "WRONG_NOTE"
    )
    st.session_state.wrong_note_logged = True



st.subheader("시험 기록")

total_exams = len(history)

for index, (exam_id, exam_date, score, total, wrong_count) in enumerate(history):
    exam_number = total_exams - index

    with st.container():

        col1, col2 = st.columns([4, 1])

        with col1:
            st.write(f"📄 CBT #{exam_number}")

            st.caption(f"📝 {total}문제 CBT")

            st.caption(exam_date)

            st.write(f"점수 : {score} / {total}")

            st.write(f"오답 : {wrong_count}문제")

        with col2:
            if st.button("다시 풀기", key=exam_id):
                st.session_state.selected_exam = exam_id
                st.switch_page("pages/wrong_review.py")

        st.divider()

if st.button("🏠 Home"):
    st.switch_page("pages/home.py")