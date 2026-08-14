import streamlit as st

st.set_page_config(
    page_title="AI 설비보전기능사 CBT Coach",
    layout="wide"
)

home = st.Page(
    "pages/home.py",
    title="홈",
    icon="🏠"
)

problem = st.Page(
    "pages/problem_generator.py",
    title="AI 문제 생성",
    icon="📘"
)

cbt = st.Page(
    "pages/CBT_test.py",
    title="CBT 시험",
    icon="📝"
)

note = st.Page(
    "pages/wrong_note.py",
    title="오답노트",
    icon="📂"
)

analysis = st.Page(
    "pages/analysis.py",
    title="학습분석",
    icon="📊"
)

login = st.Page(
    "pages/login.py",
    title="로그인"
)

signup = st.Page(
    "pages/signup.py",
    title="회원가입"
)

result = st.Page(
    "pages/result.py",
    title="시험 결과"
)

review = st.Page(
    "pages/wrong_review.py",
    title="오답 다시풀기"
)

if "user_id" in st.session_state:

    pg = st.navigation([
        home,
        problem,
        cbt,
        note,
        analysis,
        result,
    ])

else:

    pg = st.navigation([
        login,
        signup,
    ])

pg.run()