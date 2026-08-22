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


if __name__ == "__main__":
    print("연결 테스트:", test_connection())

    print("회원가입 테스트:")
    print(create_user("supabase_test", "1234"))

    print("로그인 테스트:")
    print(login_user("supabase_test", "1234"))