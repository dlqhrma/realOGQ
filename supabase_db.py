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


# -------------------------
# 회원가입
# -------------------------
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

        print("회원가입 응답:", response)
        return len(response.data) > 0

    except Exception as e:
        print("회원가입 오류:", repr(e))
        return False


# -------------------------
# 로그인
# -------------------------
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

        print("로그인 응답:", response)

        if response.data:
            return (response.data[0]["id"],)

        return None

    except Exception as e:
        print("로그인 오류:", repr(e))
        return None


# -------------------------
# 연결 테스트
# -------------------------
def test_connection():
    response = (
        supabase
        .table("users")
        .select("id")
        .limit(1)
        .execute()
    )

    return response

    
# -------------------------
# 시험 기록 저장
# -------------------------
def save_exam(user_id, score, total_questions, duration):
    try:
        response = (
            supabase
            .table("exams")
            .insert({
                "user_id": user_id,
                "score": score,
                "total_questions": total_questions,
                "duration": duration
            })
            .execute()
        )

        print("시험 기록 저장:", response)

        if response.data:
            return response.data[0]["id"]

        return None

    except Exception as e:
        print("시험 기록 저장 오류:", repr(e))
        return None


# -------------------------
# 시험 기록 조회
# -------------------------
def get_exam_history(user_id):
    try:
        response = (
            supabase
            .table("exams")
            .select("*")
            .eq("user_id", user_id)
            .order("exam_date", desc=True)
            .execute()
        )

        return response.data

    except Exception as e:
        print("시험 기록 조회 오류:", repr(e))
        return []
    
if __name__ == "__main__":
    print("연결 테스트:", test_connection())

    print("시험 저장 테스트:")
    exam_id = save_exam(
        user_id=5,
        score=15,
        total_questions=20,
        duration=600
    )

    print("생성된 시험 ID:", exam_id)

    print("시험 기록 조회:")
    print(get_exam_history(5))