import os
from dotenv import load_dotenv
from google import genai


load_dotenv()

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
def generate_problems(
    chapter,
    difficulty,
    count
):

    system_prompt = load_prompt("system_prompt.txt")
    problem_prompt = load_prompt("problem_prompt.txt")
    output_format = load_prompt("output_format.txt")
    
    knowledge = load_knowledge()

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
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text
