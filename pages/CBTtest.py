
from database import (
    save_exam,
    save_wrong_answer,
    save_question_history
)
from datetime import datetime
from ai_service import generate_problems
from time import time
from streamlit_autorefresh import st_autorefresh
import re

st.set_page_config(page_title="CBT 시험", page_icon="📝", layout="wide")

st.title("📝 설비보전기능사 CBT")


if "exam_started" not in st.session_state:
    st.session_state.exam_started = False
    
if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "time_limit" not in st.session_state:
    st.session_state.time_limit = 0

if "questions" not in st.session_state:
    st.session_state.questions = []
    

questions = st.session_state.questions

if "marked" not in st.session_state:
    st.session_state.marked = [False] * len(questions)

def grade_exam():

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
    
    if st.session_state.start_time is not None:
        duration = int(time() - st.session_state.start_time)
    
    else:
        duration = 0
    st.session_state.duration = duration

    exam_id = save_exam(
        exam_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        score=score,
        total_questions=len(questions),
        duration=duration
    )
    
    for i, q in enumerate(questions):

        correct = st.session_state.answers[i] == q["answer_index"]

        save_question_history(
            exam_id=exam_id,
            chapter=q["chapter"],
            is_correct=1 if correct else 0
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

    
    st.session_state.exam_id = exam_id

    st.session_state.exam_started = False
    st.session_state.questions = []
    st.session_state.answers = []
    st.session_state.marked = []
    st.session_state.current = 0
    st.session_state.start_time = None
    st.session_state.time_limit = 0
    st.session_state.submit_confirm = False
    st.session_state.unanswered = []

    st.switch_page("pages/result.py")

if not st.session_state.exam_started:

    st.write("실제 설비보전기능사 CBT처럼 전 범위에서 문제가 출제됩니다.")

    count = st.selectbox(
        "문제 수",
        [20, 40],
        index=0
    )

    if st.button("🚀 시험 시작", use_container_width=True):

        with st.spinner("AI가 CBT 문제를 생성하는 중입니다..."):

            try:
                result = generate_problems(
                    chapter="전체",
                    difficulty="랜덤",
                    count=count
                )
            except Exception as e:
                st.error("AI 문제 생성에 실패했습니다. 잠시 후 다시 시도해주세요.")
                st.stop()
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
            
        if len(parsed_questions) == 0:
            st.error("AI 문제를 파싱하지 못했습니다.")
            st.stop()
        
        st.session_state.questions = parsed_questions
        st.session_state.answers = [None] * len(parsed_questions)
        st.session_state.marked = [False] * len(parsed_questions)
        
        from time import time

        st.session_state.start_time = time()

        if count == 20:
            st.session_state.time_limit = 20 * 60
        else:
            st.session_state.time_limit = 40 * 60
    
        st.session_state.current = 0
        st.session_state.exam_started = True

        st.rerun()

# -------------------------
# Session
# -------------------------

if "submit_confirm" not in st.session_state:
    st.session_state.submit_confirm = False
    
if "unanswered" not in st.session_state:
    st.session_state.unanswered = []

if "current" not in st.session_state:
    st.session_state.current = 0

if "answers" not in st.session_state:
    st.session_state.answers = [None] * len(questions)

current = st.session_state.current
if len(questions) == 0:
    st.warning("문제가 없습니다.")
    st.stop()
question = questions[current]

# -------------------------
# 타이머
# -------------------------

if st.session_state.exam_started:
    st_autorefresh(interval=1000, key="timer")

elapsed = int(time() - st.session_state.start_time)
remaining = st.session_state.time_limit - elapsed

if remaining < 0:
    remaining = 0
    
if remaining == 0:
    st.error("⏰ 시험 시간이 종료되었습니다.")

    # 이후 자동 채점 코드를 실행할 위치
    grade_exam()

minute = remaining // 60
second = remaining % 60

st.metric("⏱ 남은 시간", f"{minute:02d}:{second:02d}")

# -------------------------
# 진행률
# -------------------------

progress = (current + 1) / len(questions)

st.progress(progress)

# -------------------------
# 문제 번호 이동
# -------------------------

cols = st.columns(5)

for i in range(len(questions)):

    with cols[i % 5]:

        if i == current:
            label = f"➡ {i+1}"
        else:
            label = f"{i+1}"

        if st.session_state.answers[i] is not None:
            label += " ✅"
            
        if st.session_state.marked[i]:
            label += " ⭐"

        if st.button(label, key=f"move_{i}", use_container_width=True):
            st.session_state.current = i
            st.rerun()

st.subheader(f"문제 {current+1} / {len(questions)}")

st.write(question["question"])

saved_answer = st.session_state.answers[current]

choice = st.radio(
    "정답을 선택하세요.",
    range(len(question["choices"])),
    index=saved_answer,
    format_func=lambda i: question["choices"][i],
    key=f"radio_{current}"
)


if st.button(
    "⭐ 체크 해제" if st.session_state.marked[current] else "⭐ 체크하기",
    use_container_width=True
):
    st.session_state.marked[current] = not st.session_state.marked[current]
    st.rerun()

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

            unanswered = [
                i + 1
                for i, answer in enumerate(st.session_state.answers)
                if answer is None
            ]

            if unanswered:
                st.session_state.unanswered = unanswered
                st.session_state.submit_confirm = True
                st.rerun()
            else:
                grade_exam()

if st.session_state.submit_confirm:

    st.warning(
        f"미응답 문제가 있습니다. ({', '.join(map(str, st.session_state.unanswered))}번)\n\n그래도 제출하시겠습니까?"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("제출"):
            st.session_state.submit_confirm = False

            # 여기서 기존 채점 코드 실행
            
            grade_exam()

    with col2:
        if st.button("계속 풀기"):
            st.session_state.submit_confirm = False
            st.rerun()
