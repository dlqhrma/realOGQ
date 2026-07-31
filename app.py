import streamlit as st
from database import get_chapter_accuracy
import uuid

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    
st.set_page_config(
    page_title="AI 설비보전기능사 CBT Coach",   
    layout="wide"
)

st.image("logo.gif", use_container_width=True)
st.caption("AI 기반 설비보전기능사 필기시험 학습 서비스")
st.divider()

# 카드 1행
col1, col2 = st.columns(2)

with col1:
    st.info("📘 문제 생성")
    st.write("AI가 새로운 CBT 문제를 생성합니다.")
    if st.button("시작하기", key="problem"):
        st.switch_page("pages/problem.py")
with col2:
    st.success("📝 CBT 시험")
    st.write("실제 CBT처럼 문제를 풉니다.")
    if st.button("시험 시작", key="cbt"):
        st.switch_page("pages/CBTtest.py")

st.write("")

# 카드 2행
col3, col4 = st.columns(2)

with col3:
    st.warning("📂 오답노트")
    st.write("틀린 문제를 다시 공부합니다.")
    if st.button("오답 보기", key="wrong"):
        st.switch_page("pages/note.py")

with col4:
    st.error("📊 학습 분석")
    st.write("단원별 정답률을 확인합니다.")
    if st.button("분석 보기", key="analysis"):
        st.switch_page("pages/analysis.py")

st.divider()

st.subheader("📈 최근 학습 현황")

accuracy = get_chapter_accuracy(st.session_state.session_id)

if accuracy:

    for chapter, rate in accuracy[:3]:

        st.write(f"**{chapter}**")

        st.progress(rate / 100)

        st.caption(f"정답률 {rate:.1f}%")

else:
    st.info("아직 학습 데이터가 없습니다.")