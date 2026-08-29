import os
from dotenv import load_dotenv
from supabase import create_client, Client


# =========================================================
# Supabase 연결
# =========================================================

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
# 회원가입
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

        print("회원가입 응답:", response)
        return len(response.data) > 0

    except Exception as e:
        print("회원가입 오류:", repr(e))
        return False


# =========================================================
# 로그인
# =========================================================

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


# =========================================================
# 연결 테스트
# =========================================================

def test_connection():
    try:
        response = (
            supabase
            .table("users")
            .select("id")
            .limit(1)
            .execute()
        )

        return response

    except Exception as e:
        print("Supabase 연결 오류:", repr(e))
        return None


# =========================================================
# 이용자 활동 기록
# =========================================================

def log_activity(user_id, activity_type):
    try:
        response = (
            supabase
            .table("activity_logs")
            .insert({
                "user_id": user_id,
                "activity_type": activity_type
            })
            .execute()
        )

        print("활동 기록:", response)
        return len(response.data) > 0

    except Exception as e:
        print("활동 기록 오류:", repr(e))
        return False


# =========================================================
# 테스트
# =========================================================

if __name__ == "__main__":
    print("연결 테스트:", test_connection())

    print("활동 기록 테스트:")
