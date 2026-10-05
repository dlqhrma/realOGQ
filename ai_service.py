from google import genai
from dotenv import load_dotenv
import os
import re
import random
import time
from difflib import SequenceMatcher

load_dotenv(override=True)


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def load_fallback_cbt(count):
    fallback_files = [
        f"Data/fallback_cbt_{count}_1.txt",
        f"Data/fallback_cbt_{count}_2.txt",
        f"Data/fallback_cbt_{count}_3.txt",
    ]

    filename = random.choice(fallback_files)

    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

def generate_with_retry(prompt, max_retries=2):

    for attempt in range(max_retries):
        try:
            return client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )

        except Exception as e:
            error_text = str(e)

            # 503 서버 과부하가 아니면 그대로 오류 발생
            if "503" not in error_text and "UNAVAILABLE" not in error_text:
                raise

            # 마지막 시도까지 실패
            if attempt == max_retries - 1:
                raise e

            # 503일 때 1초만 기다렸다가 한 번 재시도
            time.sleep(1)

# =========================================================
# 프롬프트 불러오기
# =========================================================

def load_prompt(filename):
    with open(f"prompts/{filename}", "r", encoding="utf-8") as f:
        return f.read()


# =========================================================
# Knowledge 불러오기
# =========================================================

def load_knowledge(chapter=None):
    """
    Knowledge.txt에서 필요한 대단원만 불러온다.

    chapter가 아래 중 하나이면 전체 Knowledge를 반환한다.
    - None
    - 전체
    - 랜덤

    그 외에는 CHAPTER_START / CHAPTER_END 경계를 이용하여
    해당 대단원만 추출한다.
    """

    with open("Data/Knowledge.txt", "r", encoding="utf-8") as f:
        knowledge = f.read()

    # 전체 Knowledge가 필요한 경우
    if chapter is None or chapter in ["전체", "랜덤"]:
        return knowledge

    start_marker = f"=== CHAPTER_START:{chapter} ==="
    end_marker = f"=== CHAPTER_END:{chapter} ==="

    start = knowledge.find(start_marker)
    end = knowledge.find(end_marker)

    # 경계를 찾지 못한 경우
    # 기존 기능이 완전히 깨지는 것을 방지하기 위해 전체 Knowledge 사용
    if start == -1 or end == -1:
        return knowledge

    start += len(start_marker)

    return knowledge[start:end].strip()


# =========================================================
# AI 해설 생성
# =========================================================

def generate_ai_explanation(
    question,
    choices,
    correct_answer,
    user_answer,
    chapter
):

    system_prompt = load_prompt("system_prompt.txt")
    answer_prompt = load_prompt("answer_prompt.txt")
    output_format = load_prompt("output_format.txt")

    knowledge = load_knowledge(chapter)

    prompt = f"""
{system_prompt}


## 참고 자료
{knowledge}

{answer_prompt}

{output_format}

## 입력 정보

문제 :
{question}

보기 :
{choices}

정답 :
{choices[correct_answer]}

사용자 답안 :
{user_answer}

단원 :
{chapter}
"""

    response = generate_with_retry(prompt)

    return response.text


# =========================================================
# 유사문제 생성
# =========================================================

def generate_similar_problem(
    question,
    choices,
    correct_answer,
    chapter,
    concept,
    difficulty
):

    system_prompt = load_prompt("system_prompt.txt")
    similar_prompt = load_prompt("similar_prompt.txt")
    output_format = load_prompt("output_format.txt")

    # 해당 문제의 대단원 Knowledge만 사용
    knowledge = load_knowledge(chapter)

    prompt = f"""
{system_prompt}


## 참고 자료
{knowledge}

{similar_prompt}

{output_format}

## 입력 정보

원본 문제 :
{question}

원본 보기 :
{choices}

정답 :
{choices[correct_answer]}

단원 :
{chapter}

핵심 개념 :
{concept}

난이도 :
{difficulty}
"""

    response = generate_with_retry(prompt)

    return response.text


# =========================================================
# AI 응답에서 문제 블록 분리
# =========================================================

def extract_problem_blocks(text):
    """
    AI 응답에서 문제 단위로 분리한다.
    """

    blocks = re.split(
        r"(?=### 문제)",
        text
    )

    return [
        block.strip()
        for block in blocks
        if block.strip().startswith("### 문제")
    ]


# =========================================================
# 문제 본문 추출
# =========================================================

def extract_question_text(problem):
    """
    문제 블록에서 실제 문제 본문만 추출한다.
    """

    match = re.search(
        r"### 문제\s*(.*?)### 보기",
        problem,
        re.S
    )

    if match:
        return match.group(1).strip()

    return problem.strip()


# =========================================================
# 문제 비교용 정규화
# =========================================================

def normalize_question(text):
    """
    중복 문제 비교를 위해 문자열을 정규화한다.
    """

    text = text.lower()

    text = re.sub(
        r"\s+",
        "",
        text
    )

    text = re.sub(
        r"[.,!?，。！？:：()（）\-]",
        "",
        text
    )

    return text


# =========================================================
# 중복 문제 검사
# =========================================================

def is_duplicate_question(
    new_question,
    existing_questions
):
    """
    완전히 같거나 매우 비슷한 문제인지 검사한다.
    """

    new_normalized = normalize_question(
        new_question
    )

    for old_question in existing_questions:

        old_normalized = normalize_question(
            old_question
        )

        # 완전히 동일한 문제
        if new_normalized == old_normalized:
            return True

        # 유사도 검사
        similarity = SequenceMatcher(
            None,
            new_normalized,
            old_normalized
        ).ratio()

        # 92% 이상 유사하면 중복으로 처리
        if similarity >= 0.92:
            return True

    return False


# =========================================================
# 문제 생성
# =========================================================

def generate_problems(
    chapter,
    difficulty,
    count
):

    system_prompt = load_prompt(
        "system_prompt.txt"
    )

    problem_prompt = load_prompt(
        "problem_prompt.txt"
    )

    output_format = load_prompt(
        "output_format.txt"
    )

    # -----------------------------------------------------
    # 핵심 변경 부분
    #
    # 일반 문제 생성:
    # 선택한 대단원 Knowledge만 사용
    #
    # CBT:
    # chapter="전체"이므로 전체 Knowledge 사용
    # -----------------------------------------------------

    knowledge = load_knowledge(chapter)

    # =====================================================
    # 1차 문제 생성
    # =====================================================

    prompt = f"""
{system_prompt}

## 참고 자료
{knowledge}

{problem_prompt}

{output_format}

## 사용자 입력

단원 :
{chapter}

난이도 :
{difficulty}

문제 수 :
{count}

## 중복 방지

- 동일한 문제를 반복해서 생성하지 않는다.
- 문제의 핵심 개념이 같더라도 질문의 조건과 상황이 다르면 출제할 수 있다.
- 동일하거나 거의 동일한 문제는 생성하지 않는다.
"""

    response = generate_with_retry(prompt)

    problem_blocks = extract_problem_blocks(
        response.text
    )

    # =====================================================
    # 2차 중복 검사
    # =====================================================

    unique_problems = []
    existing_questions = []

    for problem in problem_blocks:

        question = extract_question_text(
            problem
        )

        if not is_duplicate_question(
            question,
            existing_questions
        ):
            unique_problems.append(
                problem
            )

            existing_questions.append(
                question
            )

    # =====================================================
    # 부족한 문제 재생성
    # =====================================================

    max_retry = 3
    retry_count = 0

    while (
        len(unique_problems) < count
        and retry_count < max_retry
    ):

        missing_count = (
            count - len(unique_problems)
        )

        existing_text = "\n".join(
            f"- {question}"
            for question in existing_questions
        )

        retry_prompt = f"""
{system_prompt}

## 참고 자료
{knowledge}

{problem_prompt}

{output_format}

## 사용자 입력

단원 :
{chapter}

난이도 :
{difficulty}

문제 수 :
{missing_count}

## 이미 생성된 문제

{existing_text}

## 매우 중요한 규칙

위의 이미 생성된 문제와 동일하거나 거의 동일한 문제를 만들지 않는다.

새로운 문제를 생성한다.

단, 같은 핵심 개념을 다른 조건이나 상황으로 묻는 것은 허용한다.

반드시 {missing_count}개의 문제를 생성한다.
"""

        retry_response = generate_with_retry(retry_prompt)

        retry_blocks = extract_problem_blocks(
            retry_response.text
        )

        for problem in retry_blocks:

            question = extract_question_text(
                problem
            )

            if not is_duplicate_question(
                question,
                existing_questions
            ):

                unique_problems.append(
                    problem
                )

                existing_questions.append(
                    question
                )

                if len(unique_problems) >= count:
                    break

        retry_count += 1

    # =====================================================
    # 최종 문제 수 제한
    # =====================================================

    unique_problems = unique_problems[:count]

    return "\n\n".join(
        unique_problems
    )

# =========================================================
# CBT 문제 생성
# =========================================================

def generate_cbt_problems(count):

    if count not in [20, 40, 60]:
        raise ValueError("CBT 문제 수는 20, 40, 60 중 하나여야 합니다.")

    system_prompt = load_prompt("system_prompt.txt")
    cbt_prompt = load_prompt("cbt_prompt.txt")
    output_format = load_prompt("output_format.txt")

    # 전체 Knowledge 사용
    knowledge = load_knowledge("전체")

    # 실제 CBT에서 필요한 단원별 문제 수
    count_per_chapter = count // 4

    # 중복 제거를 대비해 단원별 1문제씩 추가 생성
    request_per_chapter = count_per_chapter + 1
    request_count = request_per_chapter * 4

    chapters = [
        "기계구동장치",
        "공유압장치",
        "전기전자장치",
        "용접 및 안전관리"
    ]

    prompt = f"""
{system_prompt}

## 참고 자료
{knowledge}

{cbt_prompt}

{output_format}

## CBT 생성 정보

최종 CBT 문제 수 :
{count}

이번 AI 생성 문제 수 :
{request_count}

## 이번 생성에서 반드시 지켜야 할 단원별 문제 수

- 기계구동장치: {request_per_chapter}문제
- 공유압장치: {request_per_chapter}문제
- 전기전자장치: {request_per_chapter}문제
- 용접 및 안전관리: {request_per_chapter}문제

## 매우 중요한 규칙

- 이번 응답에서는 정확히 {request_count}개의 문제를 생성한다.
- 각 대단원에서 정확히 {request_per_chapter}문제씩 생성한다.
- 각 문제는 반드시 해당 대단원의 Knowledge를 기반으로 생성한다.
- 다른 대단원의 내용을 섞지 않는다.
- ### 단원에는 반드시 위 4개 대단원 중 하나를 정확히 작성한다.
- 난이도는 쉬움, 보통, 어려움을 적절히 혼합한다.
- 동일하거나 거의 동일한 문제를 반복하지 않는다.
- 정답 번호가 특정 위치에 과도하게 반복되지 않도록 한다.
"""

    response = generate_with_retry(prompt)

    problem_blocks = extract_problem_blocks(response.text)

    # 단원별 문제 저장
    chapter_problems = {
        chapter: []
        for chapter in chapters
    }

    existing_questions = []

    for problem in problem_blocks:

        question = extract_question_text(problem)

        # 중복 문제 제거
        if is_duplicate_question(
            question,
            existing_questions
        ):
            continue

        # 문제의 단원 추출
        chapter_match = re.search(
            r"### 단원\s*(.*?)\s*### 세부 분류",
            problem,
            re.S
        )

        # 단원 형식이 잘못된 문제는 제외
        if not chapter_match:
            continue

        chapter = chapter_match.group(1).strip()

        # 지정된 4개 대단원이 아니면 제외
        if chapter not in chapter_problems:
            continue

        # 해당 단원이 이미 필요한 개수만큼 찼으면 제외
        if len(chapter_problems[chapter]) >= count_per_chapter:
            continue

        chapter_problems[chapter].append(problem)
        existing_questions.append(question)

    # 각 단원이 정확한 문제 수를 확보했는지 확인
    for chapter in chapters:

        generated_count = len(chapter_problems[chapter])

        if generated_count != count_per_chapter:
            raise ValueError(
                f"CBT 문제 생성 실패 - {chapter} "
                f"(필요: {count_per_chapter}, 생성: {generated_count})"
            )

    # 최종 문제 합치기
    final_problems = []

    for chapter in chapters:
        final_problems.extend(
            chapter_problems[chapter]
        )

    # 최종 문제 수 확인
    if len(final_problems) != count:
        raise ValueError(
            f"CBT 문제 생성 실패 "
            f"(요청: {count}, 생성: {len(final_problems)})"
        )

    # 시험 문제 순서 랜덤화
    random.shuffle(final_problems)

    return "\n\n".join(final_problems)