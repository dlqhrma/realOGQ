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

stats = st.Page(
    "pages/admin_stats.py",
    title="이용자 통계",
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

stats = st.Page(
    "pages/admin_stats.py",
    title="통계"
)

if "user_id" in st.session_state:

    pg = st.navigation(
        [
            home,
            problem,
            cbt,
            note,
            analysis,
            result,
            review,
            stats,
        ],
        position="hidden"
    )
    
    with st.sidebar:
        st.page_link(home, label="홈", icon="🏠")
        st.page_link(problem, label="AI 문제 생성", icon="📘")
        st.page_link(cbt, label="CBT 시험", icon="📝")
        st.page_link(note, label="오답노트", icon="📂")
        st.page_link(analysis, label="학습분석", icon="📊")
        
        if st.session_state.get("is_admin", False):
            st.page_link(
                stats,
                label="이용자 통계",
                icon="📊"
            )
else:

    pg = st.navigation([
        login,
        signup,
    ])
    

pg.run()