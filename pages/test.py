import streamlit as st
import os
from google import genai

st.title("Gemini 연결 테스트")

key = os.getenv("GEMINI_API_KEY")

st.write("API Key 존재:", bool(key))
st.write("API Key 길이:", len(key) if key else 0)

if st.button("Gemini 테스트"):
    try:
        client = genai.Client(api_key=key)

        test_prompt = """
        설비보전기능사 객관식 문제 1개를 생성해주세요.

        단원: 기계요소
        난이도: 보통

        다음 형식으로 답해주세요.

        ### 문제
        문제 내용

        ### 보기
        1. 보기
        2. 보기
        3. 보기
        4. 보기

        ### 정답
        1

        ### 해설
        정답에 대한 간단한 설명
        """

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=test_prompt
        )

        st.success("Gemini 연결 성공")
        st.write(response.text)

    except Exception as e:
        st.error("Gemini 연결 실패")
        st.exception(e)