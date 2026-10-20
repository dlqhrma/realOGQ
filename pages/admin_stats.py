import streamlit as st
from supabase_db import supabase
from datetime import datetime
from zoneinfo import ZoneInfo



st.set_page_config(
    page_title="이용자 통계",
    page_icon="📊",
    layout="wide"
)

# =========================================================
# 관리자 접근 권한 확인
# =========================================================

if "user_id" not in st.session_state:
    st.error("로그인이 필요합니다.")
    st.stop()

if not st.session_state.get("is_admin", False):
    st.error("🚫 관리자만 접근할 수 있습니다.")
    st.stop()

st.title("📊 서비스 이용 통계")



# =========================================================
# 전체 이용자 조회
# =========================================================

try:
    user_response = (
        supabase
        .table("users")
        .select("id")
        .execute()
    )

    users = user_response.data or []

except Exception as e:
    st.error(f"⚠️ 이용자 정보를 불러오지 못했습니다: {e}")
    st.stop()


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

    logs = response.data or []

except Exception as e:
    st.error(f"⚠️ 활동 기록을 불러오지 못했습니다: {e}")
    st.stop()


# =========================================================
# 이용자 수 계산
# =========================================================

# 전체 이용자 = users 테이블 기준
total_users = len(users)

cbt_users = set()
problem_users = set()
wrong_note_users = set()

# 중복 포함 실제 활동 횟수
cbt_total_count = sum(
    1 for log in logs
    if log["activity_type"] == "CBT"
)

problem_total_count = sum(
    1 for log in logs
    if log["activity_type"] == "PROBLEM_GENERATION"
)

learning_total_count = cbt_total_count + problem_users

for log in logs:

    user_id = log["user_id"]
    activity_type = log["activity_type"]

    if activity_type == "CBT":
        cbt_users.add(user_id)

    elif activity_type == "PROBLEM_GENERATION":
        problem_users.add(user_id)

    elif activity_type == "WRONG_NOTE":
        wrong_note_users.add(user_id)


# =========================================================
# 이용자 수 표시
# =========================================================

col1, col2, col3, col4 = st.columns(4)


with col1:
    st.metric(
        "전체 이용자",
        total_users
    )


with col2:
    st.metric(
        "CBT 이용자",
        cbt_total_count
    )
 #with col2:
 #   st.metric(
 #       "CBT 이용자",
 #       len(cbt_users)
 #   )

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
# 최근 활동
# =========================================================

# =========================================================
# 과제용 실측 대시보드
# =========================================================

from collections import defaultdict
from datetime import timedelta

st.divider()
st.header("📊 활동 기록 대시보드")


# =========================================================
# 공통 데이터 정리
# =========================================================

def parse_log_datetime(created_at):
    try:
        dt = datetime.fromisoformat(
            created_at.replace("Z", "+00:00")
        )

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo("UTC"))

        return dt.astimezone(ZoneInfo("Asia/Seoul"))

    except Exception:
        return None


# 사용자별 활동 날짜 저장
user_activity_dates = defaultdict(set)

# 기능을 실제로 시작한 사용자
started_users = set()

# CBT를 완료한 사용자
completed_users = set()


for log in logs:

    user_id = log.get("user_id")
    activity_type = log.get("activity_type")

    dt = parse_log_datetime(
        log.get("created_at", "")
    )

    if dt is not None:
        user_activity_dates[user_id].add(
            dt.date()
        )

    # CBT 또는 AI 문제 생성을 사용했다면 학습 시작
    if activity_type in [
        "CBT",
        "PROBLEM_GENERATION"
    ]:
        started_users.add(user_id)

    # 현재 CBT 로그는 CBT 완료 후 기록되므로 완료로 사용
    if activity_type == "CBT":
        completed_users.add(user_id)


# 서로 다른 날짜에 2일 이상 활동한 사용자
revisit_users = {
    user_id
    for user_id, dates in user_activity_dates.items()
    if len(dates) >= 2
}


# =========================================================
# ① 계측 이벤트
# =========================================================

st.subheader("① 계측 이벤트")

st.caption(
    "가입 계정 수와 활동 로그 기반 고유 계정 수를 표시합니다. "
    "방문 및 실제 세션 시작 이벤트는 별도로 수집하지 않습니다."
)

event_col1, event_col2, event_col3, event_col4 = st.columns(4)

visit_count = total_users
start_count = len(started_users)
complete_count = len(completed_users)
revisit_count = len(revisit_users)


with event_col1:
    st.metric(
        "👤 가입 계정",
        visit_count
    )
    st.caption("가입된 전체 계정 수 (사람 수와 다를 수 있음)")


with event_col2:
    st.metric(
        "🚀 학습 기능 이용",
        learning_total_count
    )
    st.caption("CBT 완료 또는 AI 문제 생성 로그가 있는 계정")


with event_col3:
    st.metric(
        "✅ 완료",
        cbt_total_count
    )
    st.caption("CBT 1회 이상 완료")


with event_col4:
    st.metric(
        "🔁 2일 이상 활동",
        revisit_count
    )
    st.caption("서로 다른 날짜에 2일 이상 활동한 계정")


# =========================================================
# ② 퍼널
# =========================================================

st.divider()
st.subheader("② 활동 계정 현황")


def drop_rate(previous, current):

    if previous <= 0:
        return 0.0

    return max(
        0.0,
        ((previous - current) / previous) * 100
    )


start_drop = drop_rate(
    visit_count,
    start_count
)

complete_drop = drop_rate(
    start_count,
    complete_count
)

revisit_drop = drop_rate(
    complete_count,
    revisit_count
)


funnel_data = {
    "단계": [
        "가입 계정",
        "학습 기능 이용",
        "CBT 완료",
        "2일 이상 활동"
    ],

    "인원": [
        visit_count,
        start_count,
        complete_count,
        revisit_count
    ],

    "비고": [
        "가입된 계정",
        "CBT 또는 문제 생성 로그",
        "CBT 완료 로그",
        "서로 다른 2일 이상 활동 로그"
    ]
}


st.dataframe(
    funnel_data,
    use_container_width=True,
    hide_index=True
)


# 간단한 퍼널 그래프
st.bar_chart(
    {
        "가입 계정": visit_count,
        "학습 기능 이용": start_count,
        "CBT 완료": complete_count,
        "2일 이상 활동": revisit_count
    }
)


# =========================================================
# ③ 리텐션
# =========================================================

st.divider()
st.subheader("③ 주간 활동 계정 리텐션")

now_kst = datetime.now(
    ZoneInfo("Asia/Seoul")
)

today = now_kst.date()

# 이번 주 월요일
this_week_start = (
    today - timedelta(days=today.weekday())
)

# 지난 주 월요일
last_week_start = (
    this_week_start - timedelta(days=7)
)

last_week_end = (
    this_week_start - timedelta(days=1)
)


week1_users = set()
week2_users = set()


for log in logs:

    user_id = log.get("user_id")

    dt = parse_log_datetime(
        log.get("created_at", "")
    )

    if dt is None:
        continue

    activity_date = dt.date()

    # 지난 주
    if (
        last_week_start
        <= activity_date
        <= last_week_end
    ):
        week1_users.add(user_id)

    # 이번 주
    elif this_week_start <= activity_date <= today:
        week2_users.add(user_id)


retained_users = (
    week1_users & week2_users
)


if len(week1_users) > 0:

    retention_rate = (
        len(retained_users)
        / len(week1_users)
        * 100
    )

else:
    retention_rate = 0.0


ret_col1, ret_col2, ret_col3, ret_col4 = st.columns(4)


with ret_col1:
    st.metric(
        "1주차 이용자",
        len(week1_users)
    )


with ret_col2:
    st.metric(
        "2주차 이용자",
        len(week2_users)
    )


with ret_col3:
    st.metric(
        "재방문 이용자",
        len(retained_users)
    )


with ret_col4:
    st.metric(
        "1주 → 2주 리텐션",
        f"{retention_rate:.1f}%"
    )


st.progress(
    min(
        retention_rate / 100,
        1.0
    )
)


# =========================================================
# ④ 개선 1건
# =========================================================

st.divider()
st.subheader("④ 서비스 개선 내용")

st.markdown("""
#### AI 문제 생성 안정성 개선

**개선 전**

- AI API 오류 발생 시 문제 생성 실패
- 사용자가 CBT 시험을 시작하지 못하는 문제가 있었음

**개선 내용**

- AI 문제 생성 실패 시 자동으로 저장된 CBT 문제 세트 사용
- 20 / 40 / 60문제별 fallback 문제 세트 구성
- 각 문제 수마다 여러 세트를 준비하여 랜덤 선택

**개선 후**

- AI API 오류가 발생해도 CBT 시험을 계속 시작할 수 있도록 개선
""")


# 시도/성공 이벤트 및 개선 전후 기간별 측정 데이터가 없어 산출하지 않음.
# 임의의 성공률을 표시하지 않습니다.

improve_col1, improve_col2 = st.columns(2)


with improve_col1:
    st.metric(
        "개선 전 CBT 시작 성공률",
        "측정 데이터 없음"
    )


with improve_col2:
    st.metric(
        "개선 후 CBT 시작 성공률",
        "측정 데이터 없음"
    )


# =========================================================
# ⑤ 북극성 현황
# =========================================================

st.divider()
st.subheader("⑤ 북극성 지표 현황")

st.markdown(
    "**북극성 지표:** 이번 주 CBT를 1회 이상 완료한 고유 계정 수"
)

NORTH_STAR_GOAL = 30


# 이번 주 CBT 완료 로그가 있는 고유 계정 (문제 생성만 한 계정 제외)
weekly_learning_users = set()


for log in logs:

    activity_type = log.get(
        "activity_type"
    )

    if activity_type != "CBT":
        continue

    dt = parse_log_datetime(
        log.get("created_at", "")
    )

    if dt is None:
        continue

    if this_week_start <= dt.date() <= today:

        weekly_learning_users.add(
            log.get("user_id")
        )


north_star_current = len(
    weekly_learning_users
)

north_star_rate = min(
    (
        north_star_current
        / NORTH_STAR_GOAL
        * 100
    ),
    100
)


north_col1, north_col2, north_col3 = st.columns(3)


with north_col1:
    st.metric(
        "현재",
        f"{north_star_current}명"
    )


with north_col2:
    st.metric(
        "목표",
        f"{NORTH_STAR_GOAL}명"
    )


with north_col3:
    st.metric(
        "목표 달성률",
        f"{north_star_rate:.1f}%"
    )


st.progress(
    north_star_rate / 100
)

st.caption(
    f"이번 주 CBT 완료 계정 "
    f"{north_star_current}명 / "
    f"목표 {NORTH_STAR_GOAL}명"
)