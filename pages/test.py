import streamlit as st
from ai_service import generate_problems

st.title("실제 문제 생성 테스트")

if st.button("실제 문제 생성 테스트"):
    try:
        result = generate_problems(
            chapter="전체",
            difficulty="랜덤",
            count=1
        )

        st.success("실제 generate_problems 성공!")
        st.write(result)

    except Exception as e:
        st.error("실제 generate_problems 실패")
        st.exception(e)