import streamlit as st
import pandas as pd
from database import (
    get_exam_history,
    get_chapter_statistics,
    get_chapter_accuracy
)

st.set_page_config(
    page_title="학습 분석",
    page_icon="📊",
    layout="wide"
)

st.title("📊 학습 분석")

history = get_exam_history()

if len(history) == 0:
    st.warning("아직 시험 기록이 없습니다.")
    st.stop()

exam_count = len(history)

avg_score = sum(
    score
    for _, score, _, _ in history
) / exam_count



total_time = sum(
    duration
    for _, _, _, duration in history
)

scores = [score for _, score, _, _ in history]

best_score = max(scores)
worst_score = min(scores)

passed = sum(
    1
    for score in scores
    if score >= 60
)

pass_rate = passed / exam_count * 100

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("📚 총 시험", exam_count)

with col2:
    st.metric("🎯 평균 점수", f"{avg_score:.1f}")

with col3:
    st.metric("🏆 최고 점수", best_score)

with col4:
    st.metric("📉 최저 점수", worst_score)

with col5:
    st.metric("✅ 합격률", f"{pass_rate:.1f}%")

st.divider()

st.subheader("📈 점수 추이")


df = pd.DataFrame({
    "시험": list(range(1, len(scores) + 1)),
    "점수": scores
})

st.line_chart(
    data=df,
    x="시험",
    y="점수",
    use_container_width=True
)

st.divider()

st.subheader("📚 단원별 정답률")

accuracy = get_chapter_accuracy()

if accuracy:

    for chapter, rate in accuracy:

        st.write(f"**{chapter}**")

        st.progress(rate / 100)

        st.caption(f"정답률 {rate:.1f}%")

else:
    st.info("아직 학습 데이터가 없습니다.")

st.divider()

chapter_stats = get_chapter_statistics()

st.subheader("🔥 많이 틀린 단원 TOP 3")

if chapter_stats:

    medals = ["🥇", "🥈", "🥉"]

    for i, (chapter, wrong_count) in enumerate(chapter_stats[:3]):
        st.write(f"{medals[i]} **{chapter}** : {wrong_count}문제")

else:
    st.info("통계가 없습니다.")
    
st.divider()

st.subheader("📌 학습 코멘트")

st.write(f"✅ 총 {exam_count}회의 CBT 시험을 완료했습니다.")

st.write(f"📈 평균 점수는 {avg_score:.1f}점입니다.")

if chapter_stats:
    weak_chapter = chapter_stats[0][0]

    st.write(f"⚠ 가장 많이 틀린 단원은 **{weak_chapter}** 입니다.")
    st.write(f"💡 다음 학습은 **{weak_chapter}** 단원을 먼저 복습하는 것을 추천합니다.")
    
st.divider()

st.subheader("📅 최근 시험 기록")

recent_history = history[-5:][::-1]

for exam_date, score, total, duration in recent_history:

    minute = duration // 60
    second = duration % 60

    st.write(
        f"📄 {exam_date} | "
        f"{score}/{total}점 | "
        f"{minute}분 {second}초"
    )
"DELETE"