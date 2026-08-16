
from google import genai
from dotenv import load_dotenv
import os
import re
from difflib import SequenceMatcher

load_dotenv(override=True)


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def load_prompt(filename):
    with open(f"prompts/{filename}", "r", encoding="utf-8") as f:
        return f.read()

def load_knowledge():
    with open("Data/Knowledge.txt", "r", encoding="utf-8") as f:
        return f.read()


def generate_ai_explanation(
    question,
    choices,
    correct_answer,
    user_answer
):

    system_prompt = load_prompt("system_prompt.txt")
    answer_prompt = load_prompt("answer_prompt.txt")
    output_format = load_prompt("output_format.txt")
    
    knowledge = load_knowledge()

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
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text
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
    
    knowledge = load_knowledge()

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

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text

def extract_problem_blocks(text):
    """AI 응답에서 문제 단위로 분리"""
    blocks = re.split(r"(?=### 문제)", text)

    return [
        block.strip()
        for block in blocks
        if block.strip().startswith("### 문제")
    ]


def extract_question_text(problem):
    """문제 본문만 추출"""
    match = re.search(
        r"### 문제\s*(.*?)### 보기",
        problem,
        re.S
    )

    if match:
        return match.group(1).strip()

    return problem.strip()


def normalize_question(text):
    """문제 비교용 정규화"""
    text = text.lower()
    text = re.sub(r"\s+", "", text)
    text = re.sub(r"[.,!?，。！？:：()（）\-]", "", text)

    return text


def is_duplicate_question(new_question, existing_questions):
    """완전히 같거나 매우 비슷한 문제인지 확인"""

    new_normalized = normalize_question(new_question)

    for old_question in existing_questions:

        old_normalized = normalize_question(old_question)

        # 완전히 같은 문제
        if new_normalized == old_normalized:
            return True

        # 거의 같은 문제
        similarity = SequenceMatcher(
            None,
            new_normalized,
            old_normalized
        ).ratio()

        if similarity >= 0.92:
            return True

    return False


def generate_problems(
    chapter,
    difficulty,
    count
):

    system_prompt = load_prompt("system_prompt.txt")
    problem_prompt = load_prompt("problem_prompt.txt")
    output_format = load_prompt("output_format.txt")

    knowledge = load_knowledge()

    # -------------------------
    # 1차 문제 생성
    # -------------------------

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

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    problem_blocks = extract_problem_blocks(response.text)

    # -------------------------
    # 2차 중복 검사
    # -------------------------

    unique_problems = []
    existing_questions = []

    for problem in problem_blocks:

        question = extract_question_text(problem)

        if not is_duplicate_question(
            question,
            existing_questions
        ):
            unique_problems.append(problem)
            existing_questions.append(question)

    # -------------------------
    # 부족한 문제 재생성
    # -------------------------

    max_retry = 3
    retry_count = 0

    while len(unique_problems) < count and retry_count < max_retry:

        missing_count = count - len(unique_problems)

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

        retry_response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=retry_prompt
        )

        retry_blocks = extract_problem_blocks(
            retry_response.text
        )

        for problem in retry_blocks:

            question = extract_question_text(problem)

            if not is_duplicate_question(
                question,
                existing_questions
            ):
                unique_problems.append(problem)
                existing_questions.append(question)

                if len(unique_problems) >= count:
                    break

        retry_count += 1

    # -------------------------
    # 최종 문제 수 제한
    # -------------------------

    unique_problems = unique_problems[:count]

    return "\n\n".join(unique_problems)