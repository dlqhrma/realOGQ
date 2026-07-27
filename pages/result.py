import streamlit as st

st.set_page_config(
    page_title="시험 결과",
    page_icon="📊",
    layout="wide"
)

st.title("📊 CBT 시험 결과")

# 시험을 보지 않고 들어온 경우
if "score" not in st.session_state:
    st.warning("시험 결과가 없습니다.")
    st.stop()

score = st.session_state.score
total = st.session_state.total_questions
wrong = total - score

percent = int(score / total * 100)

st.progress(percent / 100)

st.metric(
    label="최종 점수",
    value=f"{percent}점"
)

col1, col2 = st.columns(2)

with col1:
    st.success(f"⭕ 정답 : {score}문제")

with col2:
    st.error(f"❌ 오답 : {wrong}문제")

st.divider()

st.subheader("시험이 완료되었습니다.")

st.write("오답노트에서 틀린 문제를 다시 학습할 수 있습니다.")

st.divider()

col1, col2 = st.columns(2)

with col1:

    if st.button("🏠 Home", use_container_width=True):

        st.session_state.current = 0
        st.session_state.answers = [None] * total

        st.switch_page("app.py")

with col2:

    if st.button("📂 오답노트", use_container_width=True):

        st.switch_page("pages/note.py")