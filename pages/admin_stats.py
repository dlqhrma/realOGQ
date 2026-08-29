import streamlit as st
from supabase_db import supabase


st.set_page_config(
    page_title="이용자 통계",
    page_icon="📊",
    layout="wide"
)


st.title("📊 서비스 이용 통계")


# =========================================================
# 활동 기록 조회
# =========================================================

try:
    response = (
        supabase
        .table("activity_logs")
        .select("user_id, activity_type, created_at")
        .execute()
    )

    logs = response.data

except Exception as e:
    st.error(f"활동 기록을 불러오지 못했습니다: {e}")
    st.stop()


# =========================================================
# 이용자 수 계산
# =========================================================

all_users = set()
cbt_users = set()
problem_users = set()
wrong_note_users = set()

for log in logs:
    user_id = log["user_id"]
    activity_type = log["activity_type"]

    all_users.add(user_id)

    if activity_type == "CBT":
        cbt_users.add(user_id)

    elif activity_type == "PROBLEM_GENERATION":
        problem_users.add(user_id)

    elif activity_type == "WRONG_NOTE":
        wrong_note_users.add(user_id)


# =========================================================
# 통계 표시
# =========================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "전체 이용자",
        len(all_users)
    )

with col2:
    st.metric(
        "CBT 이용자",
        len(cbt_users)
    )

with col3:
    st.metric(
        "문제 생성 이용자",
        len(problem_users)
    )

with col4:
    st.metric(
        "오답노트 이용자",
        len(wrong_note_users)
    )


# =========================================================
# 활동 횟수
# =========================================================

st.divider()

st.subheader("📈 활동 횟수")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "CBT 실행",
        sum(1 for log in logs if log["activity_type"] == "CBT")
    )

with col2:
    st.metric(
        "문제 생성",
        sum(
            1
            for log in logs
            if log["activity_type"] == "PROBLEM_GENERATION"
        )
    )

with col3:
    st.metric(
        "오답노트 이용",
        sum(
            1
            for log in logs
            if log["activity_type"] == "WRONG_NOTE"
        )
    )


# =========================================================
# 최근 활동
# =========================================================

st.divider()

st.subheader("🕒 최근 활동")

if logs:
    recent_logs = sorted(
        logs,
        key=lambda x: x["created_at"],
        reverse=True
    )[:20]

    st.dataframe(
        recent_logs,
        use_container_width=True
    )

else:
    st.info("아직 활동 기록이 없습니다.")