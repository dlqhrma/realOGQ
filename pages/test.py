import streamlit as st
from ai_service import load_prompt, load_knowledge

st.title("프롬프트 크기 테스트")

system_prompt = load_prompt("system_prompt.txt")
problem_prompt = load_prompt("problem_prompt.txt")
output_format = load_prompt("output_format.txt")
knowledge = load_knowledge()

st.write("system_prompt:", len(system_prompt), "문자")
st.write("problem_prompt:", len(problem_prompt), "문자")
st.write("output_format:", len(output_format), "문자")
st.write("Knowledge:", len(knowledge), "문자")

total = len(system_prompt) + len(problem_prompt) + len(output_format) + len(knowledge)

st.write("총 문자 수:", total)