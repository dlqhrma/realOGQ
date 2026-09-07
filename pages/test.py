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

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents="안녕하세요. 테스트입니다. 한 문장으로 답해주세요."
        )

        st.success("Gemini 연결 성공")
        st.write(response.text)

    except Exception as e:
        st.error("Gemini 연결 실패")
        st.exception(e)