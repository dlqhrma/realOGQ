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
duration = st.session_state.get("duration", 0)

percent = int(score / total * 100)
passed = percent >= 60

st.progress(percent / 100)

st.metric(
    label="최종 점수",
    value=f"{percent}점"
)

if passed:
    st.success("🎉 합격")
else:
    st.error("❌ 불합격")
    
minute = duration // 60
second = duration % 60

st.metric(
    label="시험 시간",
    value=f"{minute}분 {second}초"
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

        st.session_state.exam_started = False
        st.session_state.questions = []
        st.session_state.answers = []
        st.session_state.marked = []
        st.session_state.current = 0
        st.session_state.start_time = None
        st.session_state.time_limit = 0
        st.session_state.submit_confirm = False
        st.session_state.unanswered = []

        st.switch_page("app.py")

with col2:

    if st.button("📂 오답노트", use_container_width=True):

        st.session_state.exam_started = False
        st.session_state.questions = []
        st.session_state.answers = []
        st.session_state.marked = []
        st.session_state.current = 0
        st.session_state.start_time = None
        st.session_state.time_limit = 0
        st.session_state.submit_confirm = False
        st.session_state.unanswered = []

        st.switch_page("pages/note.py")