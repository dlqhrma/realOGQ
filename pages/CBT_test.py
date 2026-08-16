import streamlit as st
from database import (
    save_exam,
    save_wrong_answer,
    save_question_history
)
from datetime import datetime
from ai_service import generate_problems

from time import time
import streamlit.components.v1 as components
import re

st.set_page_config(page_title="CBT 시험", page_icon="📝", layout="wide")

st.title("📝 설비보전기능사 CBT")



if "exam_started" not in st.session_state:
    st.session_state.exam_started = False
    
    
if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "time_limit" not in st.session_state:
    st.session_state.time_limit = 0
    
if "time_expired" not in st.session_state:
    st.session_state.time_expired = False

if "questions" not in st.session_state:
    st.session_state.questions = []
    

questions = st.session_state.questions

if "marked" not in st.session_state:
    st.session_state.marked = [False] * len(questions)

def grade_exam():

    if st.session_state.get("exam_finished", False):
        return

    if st.session_state.grading:
        return

    # 채점 시작
    st.session_state.grading = True

    # CBT 즉시 종료
    st.session_state.exam_started = False
    st.session_state.time_expired = True
    st.session_state.exam_finished = True


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
    print("score 저장:", score)
    print("total 저장:", len(questions))
    st.session_state.wrong_questions = wrong_questions
    
    if st.session_state.start_time is not None:
        duration = int(time() - st.session_state.start_time)
    
    else:
        duration = 0
    st.session_state.duration = duration

    exam_id = save_exam(
        user_id=st.session_state.user_id,
        exam_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        score=score,
        total_questions=len(questions),
        duration=duration
    )
    
    for i, q in enumerate(questions):

        correct = st.session_state.answers[i] == q["answer_index"]

        save_question_history(
            user_id=st.session_state.user_id,
            exam_id=exam_id,
            chapter=q["chapter"],
            is_correct=1 if correct else 0
        )

    today = datetime.now().strftime("%Y-%m-%d")

    for i, q in enumerate(questions):

        if st.session_state.answers[i] != q["answer_index"]:
            

            save_wrong_answer(
                user_id=st.session_state.user_id,
                exam_id=exam_id,
                question_id=q["id"],
                chapter=q["chapter"],
                subcategory=q["subcategory"],
                concept=q["concept"],
                difficulty=q["difficulty"],
                question=q["question"],
                choices=q["choices"],
                my_answer=st.session_state.answers[i],
                correct_answer=q["answer_index"],
                explanation=q["explanation"],
                wrong_date=today,
                exam_count=len(questions)
            )

    
    st.session_state.exam_started = False
    st.session_state.exam_finished = True
    st.session_state.grading = False
    st.session_state.exam_id = exam_id

    # CBT 시험 상태 완전 초기화
    st.session_state.questions = []
    st.session_state.answers = []
    st.session_state.marked = []
    st.session_state.current = 0
    st.session_state.number_page = 0

    # 타이머 초기화
    st.session_state.start_time = None
    st.session_state.time_limit = 0
    st.session_state.time_expired = False

    # 제출 상태 초기화
    st.session_state.submit_confirm = False
    st.session_state.unanswered = []

    st.switch_page("pages/result.py")

if not st.session_state.exam_started:

    st.info("""
    ### 📚 CBT 시험 안내

    **20문제**
    - 핵심 개념을 빠르게 점검하는 연습용 CBT

    **40문제**
    - 실제 시험과 유사한 구성으로 종합 실력을 점검하는 CBT

    **60문제**
    - 실전 시험을 충분히 대비하기 위한 고난도 CBT
    """)

    count = st.selectbox(
        "문제 수",
        [20, 40, 60],
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
                st.error("⚠️ AI 문제 생성에 실패했습니다. 잠시 후 다시 시도해주세요.")
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
                chapter = block.split("### 단원")[1].split("### 세부 분류")[0].strip()

                # 세부 분류
                subcategory = block.split("### 세부 분류")[1].split("### 난이도")[0].strip()

                # 난이도
                difficulty = block.split("### 난이도")[1].split("### 시험 유형")[0].strip()

                # 핵심 개념
                concept = block.split("### 핵심 개념")[1].strip()

                parsed_questions.append({
                    "id": idx,
                    "chapter": chapter,
                    "subcategory": subcategory,
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
            st.error("AI 문제를 생성하지 못했습니다. 다시 시도해주세요.")
            st.stop()
        
        st.session_state.questions = parsed_questions
        st.session_state.answers = [None] * len(parsed_questions)
        st.session_state.marked = [False] * len(parsed_questions)
        
        from time import time

        st.session_state.start_time = time()

        if count == 20:
            st.session_state.time_limit = 20 * 60
        elif count == 40:
            st.session_state.time_limit = 40 * 60
        else:
            st.session_state.time_limit = 60 * 60
    
        st.session_state.current = 0
        st.session_state.number_page = 0
        st.session_state.exam_started = True
        st.session_state.grading = False
        st.session_state.exam_finished = False

        st.rerun()

# -------------------------
# Session
# -------------------------

if "submit_confirm" not in st.session_state:
    st.session_state.submit_confirm = False
    
if "grading" not in st.session_state:
    st.session_state.grading = False
    
if "unanswered" not in st.session_state:
    st.session_state.unanswered = []

if "current" not in st.session_state:
    st.session_state.current = 0
    
if "number_page" not in st.session_state:
    st.session_state.number_page = 0

if "answers" not in st.session_state:
    st.session_state.answers = [None] * len(questions)

current = st.session_state.current
if len(questions) == 0:
    st.warning("문제가 없습니다.")
    st.stop()
question = questions[current]

def move_question(index):
    st.session_state.current = index
    st.session_state.number_page = index // 20


def move_next():
    current = st.session_state.current
    st.session_state.current = current + 1
    st.session_state.number_page = (current + 1) // 20


def move_previous():
    current = st.session_state.current
    st.session_state.current = current - 1
    st.session_state.number_page = (current - 1) // 20

page = st.session_state.number_page

start = page * 20
end = min(start + 20, len(questions))

# -------------------------
# 타이머
# -------------------------

@st.fragment(run_every="1s")
def show_timer():

    if not st.session_state.exam_started:
        return

    elapsed = int(time() - st.session_state.start_time)

    remaining = max(
        0,
        st.session_state.time_limit - elapsed
    )

    minutes = remaining // 60
    seconds = remaining % 60

    st.markdown(
        f"""
        <div style="
            font-size:28px;
            font-weight:bold;
            text-align:center;
            margin-bottom:20px;
        ">
            ⏱ 남은 시간 : {minutes:02d}:{seconds:02d}
        </div>
        """,
        unsafe_allow_html=True
    )

    if remaining <= 0:
        st.error("⏰ 시험 시간이 종료되었습니다.")
        grade_exam()


show_timer()
    
# -------------------------
# 진행률
# -------------------------

progress = (current + 1) / len(questions)

st.progress(progress)

# -------------------------
# 문제 번호 이동
# -------------------------

st.markdown("#### 문제 번호")

total_page = (len(questions) + 19) // 20

# 20문제 단위 페이지 선택
page_cols = st.columns(total_page)

for p in range(total_page):
    start_num = p * 20 + 1
    end_num = min((p + 1) * 20, len(questions))

    with page_cols[p]:
        st.button(
            f"{start_num}~{end_num}",
            key=f"page_{p}",
            use_container_width=True,
            on_click=lambda p=p: st.session_state.update(
                number_page=p
            )
        )

# 현재 페이지의 문제 번호
start = st.session_state.number_page * 20
end = min(start + 20, len(questions))

number_cols = st.columns(5)

for i in range(start, end):

    with number_cols[(i - start) % 5]:

        if i == st.session_state.current:
            label = f"➡ {i + 1}"
        else:
            label = f"{i + 1}"

        if st.session_state.answers[i] is not None:
            label += " ✅"

        if st.session_state.marked[i]:
            label += " ⭐"

        st.button(
            label,
            key=f"move_{i}",
            use_container_width=True,
            on_click=move_question,
            args=(i,)
        )
            


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

        st.button(
            "⬅ 이전 문제",
            use_container_width=True,
            on_click=move_previous
        )

# -------------------------
# 다음 / 제출
# -------------------------

with col2:

    if current < len(questions)-1:

        st.button(
            "다음 문제 ➡",
            use_container_width=True,
            on_click=move_next
        )
    else:

        if st.button(
            "✅ 시험 제출",
            use_container_width=True,
            disabled=st.session_state.grading
        ):

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
                if not st.session_state.grading:
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
