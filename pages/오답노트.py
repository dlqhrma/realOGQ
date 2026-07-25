import streamlit as st
from database import get_exam_history

st.set_page_config(
    page_title="오답노트",
    page_icon="📂",
    layout="wide"
)

st.title("📂 오답노트")

history = get_exam_history()

if len(history) == 0:
    st.warning("오답노트가 없습니다.")
    if st.button("🏠 Home"):
        st.switch_page("app.py")
    st.stop()

st.subheader("시험 기록")

for exam_id, exam_date, score, total, wrong_count in history:

    with st.container():

        col1, col2 = st.columns([4, 1])

        with col1:
            st.write(f"📄 CBT #{exam_id}")
            st.caption(exam_date)
            st.write(f"점수 : {score} / {total}")
            st.write(f"오답 : {wrong_count}문제")

        with col2:
            if st.button("다시 풀기", key=exam_id):
                st.session_state.selected_exam = exam_id
                st.switch_page("pages/오답다시풀기.py")

        st.divider()

if st.button("🏠 Home"):
    st.switch_page("app.py")