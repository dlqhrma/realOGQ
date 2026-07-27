import streamlit as st
from database import save_exam, save_wrong_answer
from datetime import datetime
from ai_service import generate_problems
import re

st.set_page_config(page_title="CBT 시험", page_icon="📝", layout="wide")

st.title("📝 설비보전기능사 CBT")

# -------------------------
# 임시 문제 (나중에 AI 문제로 교체)
# -------------------------

if "exam_started" not in st.session_state:
    st.session_state.exam_started = False

if "questions" not in st.session_state:
    st.session_state.questions = []

questions = st.session_state.questions

if not st.session_state.exam_started:

    st.write("실제 설비보전기능사 CBT처럼 전 범위에서 문제가 출제됩니다.")

    count = st.selectbox(
        "문제 수",
        [20, 40],
        index=0
    )

    if st.button("🚀 시험 시작", use_container_width=True):

        with st.spinner("AI가 CBT 문제를 생성하는 중입니다..."):

            result = generate_problems(
                chapter="전체",
                difficulty="랜덤",
                count=count
            )

        # -------------------------
        # AI 결과 파싱
        # -------------------------

        parsed_questions = []

        blocks = re.split(r"### 문제", result)

        for idx, block in enumerate(blocks):

            block = block.strip()

            if not block:
                continue

            try:

                # 문제
                question = block.split("### 보기")[0].strip()

                # 보기
                choices_text = block.split("### 보기")[1].split("### 정답")[0]

                choices = []

                for line in choices_text.split("\n"):

                    line = line.strip()

                    if line.startswith(("①", "②", "③", "④")):
                        choices.append(line[2:].strip())

                # 정답
                answer_text = block.split("### 정답")[1].split("### 해설")[0].strip()

                answer_map = {
                    "①": 0,
                    "②": 1,
                    "③": 2,
                    "④": 3
                }

                answer_index = answer_map.get(answer_text, 0)

                # 해설
                explanation = block.split("### 해설")[1].split("### 단원")[0].strip()

                # 단원
                chapter = block.split("### 단원")[1].split("### 난이도")[0].strip()

                # 난이도
                difficulty = block.split("### 난이도")[1].split("### 핵심 개념")[0].strip()

                # 핵심 개념
                concept = block.split("### 핵심 개념")[1].strip()

                parsed_questions.append({
                    "id": idx,
                    "chapter": chapter,
                    "difficulty": difficulty,
                    "question": question,
                    "choices": choices,
                    "answer_index": answer_index,
                    "explanation": explanation,
                    "concept": concept
                })

            except Exception:
                continue

        st.session_state.questions = parsed_questions
        st.session_state.answers = [None] * len(parsed_questions)
        st.session_state.current = 0
        st.session_state.exam_started = True

        st.rerun()

# -------------------------
# Session
# -------------------------

if "current" not in st.session_state:
    st.session_state.current = 0

if "answers" not in st.session_state:
    st.session_state.answers = [None] * len(questions)

current = st.session_state.current
question = questions[current]

# -------------------------
# 진행률
# -------------------------

progress = (current + 1) / len(questions)

st.progress(progress)

st.subheader(f"문제 {current+1} / {len(questions)}")

st.write(question["question"])

choice = st.radio(
    "정답을 선택하세요.",
    question["choices"],
    index=None,
    key=f"radio_{current}"
)

# 이미 선택했던 답 불러오기
if st.session_state.answers[current] is not None:
    choice = st.session_state.answers[current]

# 저장
if choice:
    st.session_state.answers[current] = choice

st.divider()

col1, col2 = st.columns(2)

# -------------------------
# 이전 문제
# -------------------------

with col1:

    if current > 0:

        if st.button("⬅ 이전 문제", use_container_width=True):
            st.session_state.current -= 1
            st.rerun()

# -------------------------
# 다음 / 제출
# -------------------------

with col2:

    if current < len(questions)-1:

        if st.button("다음 문제 ➡", use_container_width=True):

            if st.session_state.answers[current] is None:
                st.warning("답을 선택해주세요.")
            else:
                st.session_state.current += 1
                st.rerun()

    else:

        if st.button("✅ 시험 제출", use_container_width=True):

            if st.session_state.answers[current] is None:
                st.warning("답을 선택해주세요.")
            else:

                score = 0
                wrong_questions = []

                for i, q in enumerate(questions):

                    if st.session_state.answers[i] == q["answer_index"]:
                        score += 1

                    else:

                        wrong_questions.append({
                            "number": i + 1,
                            "question": q["question"],
                            "choices": q["choices"],
                            "my_answer": st.session_state.answers[i],
                            "correct_answer": q["answer_index"]
                        })
                        
                st.session_state.score = score
                st.session_state.total_questions = len(questions)
                st.session_state.wrong_questions = wrong_questions

                 # 시험 기록 저장
                exam_id = save_exam(
                    exam_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    score=score,
                    total_questions=len(questions),
                    duration=0
                )
                
                today = datetime.now().strftime("%Y-%m-%d")

                for i, q in enumerate(questions):

                    if st.session_state.answers[i] != q["answer_index"]:

                        save_wrong_answer(
                            exam_id=exam_id,
                            question_id=q["id"],
                            chapter=q["chapter"],
                            concept=q["concept"],
                            difficulty=q["difficulty"],
                            question=q["question"],
                            choices=q["choices"],
                            my_answer=st.session_state.answers[i],
                            correct_answer=q["answer_index"],
                            explanation=q["explanation"],
                            wrong_date=today
                        )
                # 나중에 오답 저장할 때 사용
                st.session_state.exam_id = exam_id

                # 결과 페이지 이동
                st.switch_page("pages/result.py")
