import streamlit as st
from database import create_user

st.set_page_config(
    page_title="회원가입",
    page_icon="📝"
)

st.title("📝 회원가입")

username = st.text_input("아이디")
password = st.text_input("비밀번호", type="password")
password_check = st.text_input("비밀번호 확인", type="password")

col1, col2 = st.columns(2)

with col1:
    if st.button("회원가입", use_container_width=True):

        if not username or not password:
            st.error("아이디와 비밀번호를 입력하세요.")

        elif password != password_check:
            st.error("비밀번호가 일치하지 않습니다.")

        else:
            success = create_user(username, password)

            if success:
                st.success("회원가입이 완료되었습니다.")
                st.switch_page("pages/login.py")

            else:
                st.error("이미 존재하는 아이디입니다.")

with col2:
    if st.button("로그인", use_container_width=True):
        st.switch_page("pages/login.py")