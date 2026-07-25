import streamlit as st
from database import save_exam, save_wrong_answer
from datetime import datetime

st.set_page_config(page_title="CBT 시험", page_icon="📝", layout="wide")

st.title("📝 설비보전기능사 CBT")

# -------------------------
# 임시 문제 (나중에 AI 문제로 교체)
# -------------------------

questions = [
    {
        "id": 1,
        "chapter": "베어링",
        "difficulty": "보통",

        "question": "베어링의 주요 역할은 무엇인가?",

        "choices": [
            "동력 전달",
            "마찰 감소",
            "절삭",
            "용접"
        ],

        "answer_index": 1,

        "explanation": "",

        "concept": ""
    },

    {
        "id": 2,
        "chapter": "용접",
        "difficulty": "쉬움",

        "question": "용접 작업 시 가장 먼저 착용해야 하는 것은?",

        "choices": [
            "장갑",
            "안전화",
            "보안면",
            "귀마개"
        ],

        "answer_index": 2,

        "explanation": "",

        "concept": ""
    }
]

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
                st.switch_page("pages/시험결과.py")
