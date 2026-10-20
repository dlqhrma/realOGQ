"""설비보전기능사 CBT Coach 관리자 통계.

모든 '이용 계정' 지표는 user_id 중복을 제거해 집계합니다.
실제 활동 횟수는 별도 항목으로 표시하며, 임의의 숫자를 더하지 않습니다.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import streamlit as st
from supabase_db import supabase


st.set_page_config(
    page_title="이용자 통계",
    page_icon="📊",
    layout="wide",
)

# 관리자 접근 권한 확인
if "user_id" not in st.session_state:
    st.error("로그인이 필요합니다.")
    st.stop()

if not st.session_state.get("is_admin", False):
    st.error("🚫 관리자만 접근할 수 있습니다.")
    st.stop()

st.title("📊 서비스 이용 통계")

# Supabase에서 실제 계정 및 활동 로그 조회
try:
    users = (
        supabase.table("users")
        .select("id")
        .execute()
        .data or []
    )
    logs = (
        supabase.table("activity_logs")
        .select("user_id, activity_type, created_at")
        .execute()
        .data or []
    )
except Exception as e:
    st.error(f"⚠️ 통계 데이터를 불러오지 못했습니다: {e}")
    st.stop()


def parse_log_datetime(created_at):
    """활동 로그 시각을 한국 표준시로 변환합니다."""
    try:
        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo("UTC"))
        return dt.astimezone(ZoneInfo("Asia/Seoul"))
    except (AttributeError, TypeError, ValueError):
        return None


# 1. 전체 기간 집계: 고유 계정 수와 활동 횟수를 구분
all_account_ids = {user["id"] for user in users if user.get("id") is not None}
total_users = len(all_account_ids)

cbt_users = set()
problem_users = set()
wrong_note_users = set()
started_users = set()
user_activity_dates = defaultdict(set)

cbt_total_count = 0
problem_total_count = 0
wrong_note_total_count = 0

for log in logs:
    user_id = log.get("user_id")
    activity_type = log.get("activity_type")
    if user_id is None:
        continue

    if activity_type == "CBT":
        cbt_users.add(user_id)
        started_users.add(user_id)
        cbt_total_count += 1
    elif activity_type == "PROBLEM_GENERATION":
        problem_users.add(user_id)
        started_users.add(user_id)
        problem_total_count += 1
    elif activity_type == "WRONG_NOTE":
        wrong_note_users.add(user_id)
        wrong_note_total_count += 1

    dt = parse_log_datetime(log.get("created_at"))
    if dt is not None:
        user_activity_dates[user_id].add(dt.date())

revisit_users = {
    user_id
    for user_id, active_dates in user_activity_dates.items()
    if len(active_dates) >= 2
}

# 모두 고유 계정 수입니다. CBT를 여러 번 완료한 계정도 1개로 계산합니다.
learning_unique_count = len(started_users)
cbt_unique_count = len(cbt_users)
revisit_count = len(revisit_users)

# 상단 서비스 이용 통계
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("전체 가입 계정", total_users)
with col2:
    st.metric("CBT 이용 계정", cbt_unique_count)
with col3:
    st.metric("문제 생성 이용 계정", len(problem_users))
with col4:
    st.metric("오답노트 이용 계정", len(wrong_note_users))

st.caption("이용 계정 수는 user_id 기준으로 중복을 제거한 값이며, 실제 사람 수와 다를 수 있습니다.")

st.divider()
st.header("📊 활동 기록 대시보드")

# ① 계측 이벤트
st.subheader("① 계측 이벤트")
st.caption(
    "가입 계정 수와 활동 로그에 기반한 고유 계정 수를 표시합니다. "
    "방문 및 실제 세션 시작 이벤트는 별도로 수집하지 않습니다."
)

event_col1, event_col2, event_col3, event_col4 = st.columns(4)
with event_col1:
    st.metric("👤 가입 계정", total_users)
    st.caption("가입된 전체 계정 수")
with event_col2:
    st.metric("🚀 학습 기능 이용 계정", learning_unique_count)
    st.caption("CBT 완료 또는 AI 문제 생성 로그가 있는 고유 계정")
with event_col3:
    st.metric("✅ CBT 완료 계정", cbt_unique_count)
    st.caption("CBT를 1회 이상 완료한 고유 계정")
with event_col4:
    st.metric("🔁 2일 이상 활동 계정", revisit_count)
    st.caption("서로 다른 날짜에 2일 이상 활동한 고유 계정")

# ② 활동 계정 현황 — 기존 표 및 막대그래프 형태 유지
st.divider()
st.subheader("② 활동 계정 현황")

funnel_data = {
    "단계": ["가입 계정", "학습 기능 이용", "CBT 완료", "2일 이상 활동"],
    "인원": [total_users, learning_unique_count, cbt_unique_count, revisit_count],
    "비고": [
        "가입된 전체 계정",
        "CBT 또는 문제 생성 로그가 있는 고유 계정",
        "CBT 완료 로그가 있는 고유 계정",
        "서로 다른 날짜에 2일 이상 활동한 고유 계정",
    ],
}
st.dataframe(funnel_data, use_container_width=True, hide_index=True)
st.bar_chart({
    "가입 계정": total_users,
    "학습 기능 이용": learning_unique_count,
    "CBT 완료": cbt_unique_count,
    "2일 이상 활동": revisit_count,
})
st.caption("표와 그래프의 모든 수치는 고유 계정 수입니다(중복 제외).")

# 별도 참고: 실제 활동 횟수. 이용자 수와 혼동하지 않도록 구분
with st.expander("실제 활동 로그 건수 보기 (반복 이용 포함)"):
    st.dataframe(
        {
            "활동 유형": ["CBT 완료", "AI 문제 생성", "오답노트"],
            "활동 횟수": [cbt_total_count, problem_total_count, wrong_note_total_count],
            "고유 계정 수": [
                cbt_unique_count,
                len(problem_users),
                len(wrong_note_users),
            ],
        },
        use_container_width=True,
        hide_index=True,
    )
    st.caption("활동 횟수는 로그 건수이며, 이용 계정 수와 동일하지 않습니다.")

# ③ 리텐션: 지난주와 이번 주 활동 고유 계정 집합의 교집합
st.divider()
st.subheader("③ 주간 활동 계정 리텐션")

now_kst = datetime.now(ZoneInfo("Asia/Seoul"))
today = now_kst.date()
this_week_start = today - timedelta(days=today.weekday())
last_week_start = this_week_start - timedelta(days=7)
last_week_end = this_week_start - timedelta(days=1)

week1_users = set()
week2_users = set()
for log in logs:
    user_id = log.get("user_id")
    dt = parse_log_datetime(log.get("created_at"))
    if user_id is None or dt is None:
        continue

    activity_date = dt.date()
    if last_week_start <= activity_date <= last_week_end:
        week1_users.add(user_id)
    elif this_week_start <= activity_date <= today:
        week2_users.add(user_id)

retained_users = week1_users & week2_users
retention_rate = (
    len(retained_users) / len(week1_users) * 100
    if week1_users else 0.0
)

ret_col1, ret_col2, ret_col3, ret_col4 = st.columns(4)
with ret_col1:
    st.metric("지난주 활동 계정", len(week1_users))
with ret_col2:
    st.metric("이번 주 활동 계정", len(week2_users))
with ret_col3:
    st.metric("양쪽 주간 모두 활동", len(retained_users))
with ret_col4:
    st.metric("지난주 → 이번 주 유지율", f"{retention_rate:.1f}%")
st.progress(min(retention_rate / 100, 1.0))
st.caption("현재 날짜를 기준으로 직전 주(월~일)와 이번 주(월~오늘)를 비교합니다.")

# ④ 서비스 개선 내용
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

improve_col1, improve_col2 = st.columns(2)
with improve_col1:
    st.metric("개선 전 CBT 시작 성공률", "측정 데이터 없음")
with improve_col2:
    st.metric("개선 후 CBT 시작 성공률", "측정 데이터 없음")

# ⑤ 북극성 지표 — '주 1회 이상 CBT 완료한 고유 계정 수' 유지
st.divider()
st.subheader("⑤ 북극성 지표 현황")
st.markdown("**북극성 지표:** 이번 주 CBT를 1회 이상 완료한 고유 계정 수")

NORTH_STAR_GOAL = 30
weekly_cbt_users = set()
for log in logs:
    if log.get("activity_type") != "CBT":
        continue
    user_id = log.get("user_id")
    dt = parse_log_datetime(log.get("created_at"))
    if user_id is not None and dt is not None and this_week_start <= dt.date() <= today:
        weekly_cbt_users.add(user_id)

north_star_current = len(weekly_cbt_users)
north_star_rate = min(north_star_current / NORTH_STAR_GOAL * 100, 100)

north_col1, north_col2, north_col3 = st.columns(3)
with north_col1:
    st.metric("현재", f"{north_star_current}개 계정")
with north_col2:
    st.metric("목표", f"{NORTH_STAR_GOAL}개 계정")
with north_col3:
    st.metric("목표 달성률", f"{north_star_rate:.1f}%")
st.progress(north_star_rate / 100)
st.caption(
    f"이번 주 CBT 완료 고유 계정 {north_star_current}개 / "
    f"목표 {NORTH_STAR_GOAL}개 (반복 완료 중복 제외)"
)
