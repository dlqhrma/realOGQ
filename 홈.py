import streamlit as st

st.set_page_config(
    page_title="AI 설비보전기능사 CBT Coach",
    page_icon="🤖",
    layout="wide"
)

# 제목
st.title("🤖 AI 설비보전기능사 CBT Coach")
st.caption("AI 기반 설비보전기능사 필기시험 학습 서비스")

st.divider()

# 카드 1행
col1, col2 = st.columns(2)

with col1:
    st.info("📘 문제 생성")
    st.write("AI가 새로운 CBT 문제를 생성합니다.")
    st.button("시작하기", key="problem")

with col2:
    st.success("📝 CBT 시험")
    st.write("실제 CBT처럼 문제를 풉니다.")
    st.button("시험 시작", key="cbt")

st.write("")

# 카드 2행
col3, col4 = st.columns(2)

with col3:
    st.warning("📂 오답노트")
    st.write("틀린 문제를 다시 공부합니다.")
    st.button("오답 보기", key="wrong")

with col4:
    st.error("📊 학습 분석")
    st.write("단원별 정답률을 확인합니다.")
    st.button("분석 보기", key="analysis")

st.divider()

st.subheader("📈 최근 학습 현황")

st.progress(90)
st.write("용접 90%")

st.progress(75)
st.write("베어링 75%")

st.progress(60)
st.write("윤활 60%")