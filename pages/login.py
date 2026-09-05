import streamlit as st
from supabase_db import login_user

st.set_page_config(
    page_title="로그인",
    page_icon="🔑"
)

st.title("🔑 로그인")

username = st.text_input("아이디")
password = st.text_input("비밀번호", type="password")

if st.button("로그인", use_container_width=True):

    if not username or not password:
        st.error("아이디와 비밀번호를 입력하세요.")

    else:

        user = login_user(username, password)

        if user:
            st.session_state.user_id = user[0]
            st.session_state.is_admin = user[1]
            st.success("로그인 성공!")
            st.rerun()

        else:
            st.error("아이디 또는 비밀번호가 올바르지 않습니다.")

st.divider()

st.caption("계정이 없으신가요?")

if st.button("회원가입", use_container_width=True):
    st.switch_page("pages/signup.py")