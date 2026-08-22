import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase 환경변수가 설정되지 않았습니다.")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# =========================================================
# 회원
# =========================================================

def create_user(username, password):
    try:
        response = (
            supabase
            .table("users")
            .insert({
                "username": username,
                "password": password
            })
            .execute()
        )

        return len(response.data) > 0

    except Exception as e:
        print("회원가입 오류:", repr(e))
        return False


def login_user(username, password):
    try:
        response = (
            supabase
            .table("users")
            .select("id")
            .eq("username", username)
            .eq("password", password)
            .limit(1)
            .execute()
        )

        if response.data:
            return (response.data[0]["id"],)

        return None

    except Exception as e:
        print("로그인 오류:", repr(e))
        return None


# =========================================================
# 시험
# =========================================================

def save_exam(user_id, exam_date, score, total_questions, duration):
    try:
        data = {
            "user_id": user_id,
            "score": score,
            "total_questions": total_questions,
            "duration": duration
        }

        # exam_date가 전달되었을 때만 저장
        if exam_date is not None:
            data["exam_date"] = exam_date

        response = (
            supabase
            .table("exams")
            .insert(data)
            .execute()
        )

        if response.data:
            return response.data[0]["id"]

        return None

    except Exception as e:
        print("시험 기록 저장 오류:", repr(e))
        return None


def get_exam_history(user_id):
    try:
        response = (
            supabase
            .table("exams")
            .select("exam_date, score, total_questions, duration")
            .eq("user_id", user_id)
            .order("id", desc=False)
            .execute()
        )

        return [
            (
                row["exam_date"],
                row["score"],
                row["total_questions"],
                row["duration"]
            )
            for row in response.data
        ]

    except Exception as e:
        print("시험 기록 조회 오류:", repr(e))
        return []


# =========================================================
# 문제 풀이 기록
# =========================================================

def save_question_history(
    user_id,
    exam_id,
    chapter,
    is_correct
):
    try:
        response = (
            supabase
            .table("question_history")
            .insert({
                "user_id": user_id,
                "exam_id": exam_id,
                "chapter": chapter,
                "is_correct": is_correct
            })
            .execute()
        )

        return len(response.data) > 0

    except Exception as e:
        print("문제 풀이 기록 저장 오류:", repr(e))
        return False


def get_chapter_accuracy(user_id):
    try:
        response = (
            supabase
            .table("question_history")
            .select("chapter, is_correct")
            .eq("user_id", user_id)
            .execute()
        )

        chapter_data = {}

        for row in response.data:
            chapter = row["chapter"]
            is_correct = row["is_correct"]

            if chapter not in chapter_data:
                chapter_data[chapter] = []

            chapter_data[chapter].append(is_correct)

        result = []

        for chapter, answers in chapter_data.items():
            accuracy = sum(answers) / len(answers) * 100
            result.append((chapter, round(accuracy, 1)))

        return result

    except Exception as e:
        print("단원 정답률 조회 오류:", repr(e))
        return []


# =========================================================
# 오답 저장
# =========================================================

def save_wrong_answer(
    user_id,
    exam_id,
    question_id,
    chapter,
    subcategory,
    concept,
    difficulty,
    question,
    choices,
    my_answer,
    correct_answer,
    explanation,
    wrong_date,
    exam_count
):
    try:
        response = (
            supabase
            .table("wrong_answers")
            .insert({
                "user_id": user_id,
                "exam_id": exam_id,
                "question_id": question_id,
                "chapter": chapter,
                "subcategory": subcategory,
                "concept": concept,
                "difficulty": difficulty,
                "question": question,
                "choices": str(choices),
                "my_answer": my_answer,
                "correct_answer": correct_answer,
                "explanation": explanation,
                "wrong_date": wrong_date,
                "exam_count": exam_count
            })
            .execute()
        )

        return len(response.data) > 0

    except Exception as e:
        print("오답 저장 오류:", repr(e))
        return False


# =========================================================
# 오답노트 - 시험 기록
# =========================================================

def get_exam_history_for_note(user_id):
    try:
        exams_response = (
            supabase
            .table("exams")
            .select("id, exam_date, score, total_questions")
            .eq("user_id", user_id)
            .order("id", desc=True)
            .execute()
        )

        wrong_response = (
            supabase
            .table("wrong_answers")
            .select("id, exam_id")
            .eq("user_id", user_id)
            .execute()
        )

        wrong_count = {}

        for row in wrong_response.data:
            exam_id = row["exam_id"]
            wrong_count[exam_id] = wrong_count.get(exam_id, 0) + 1

        result = []

        for exam in exams_response.data:
            exam_id = exam["id"]

            result.append((
                exam_id,
                exam["exam_date"],
                exam["score"],
                exam["total_questions"],
                wrong_count.get(exam_id, 0)
            ))

        return result

    except Exception as e:
        print("오답노트 시험 기록 조회 오류:", repr(e))
        return []


# =========================================================
# 오답 문제 조회
# =========================================================

def get_wrong_questions(user_id, exam_id):
    try:
        response = (
            supabase
            .table("wrong_answers")
            .select(
                "chapter, subcategory, concept, difficulty, "
                "question, choices, my_answer, correct_answer, explanation"
            )
            .eq("user_id", user_id)
            .eq("exam_id", exam_id)
            .execute()
        )

        return [
            (
                row["chapter"],
                row["subcategory"],
                row["concept"],
                row["difficulty"],
                row["question"],
                row["choices"],
                row["my_answer"],
                row["correct_answer"],
                row["explanation"]
            )
            for row in response.data
        ]

    except Exception as e:
        print("오답 문제 조회 오류:", repr(e))
        return []


# =========================================================
# 단원별 오답 통계
# =========================================================

def get_chapter_statistics(user_id):
    try:
        response = (
            supabase
            .table("wrong_answers")
            .select("chapter")
            .eq("user_id", user_id)
            .execute()
        )

        statistics = {}

        for row in response.data:
            chapter = row["chapter"]
            statistics[chapter] = statistics.get(chapter, 0) + 1

        return list(statistics.items())

    except Exception as e:
        print("단원 통계 조회 오류:", repr(e))
        return []


# =========================================================
# 연결 테스트
# =========================================================

def test_connection():
    return (
        supabase
        .table("users")
        .select("id")
        .limit(1)
        .execute()
    )


# =========================================================
# 직접 실행 테스트
# =========================================================

if __name__ == "__main__":
    print("Supabase 연결 테스트")
    print(test_connection())

    print("\n시험 기록 조회 테스트")
    print(get_exam_history(5))