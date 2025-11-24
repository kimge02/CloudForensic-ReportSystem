# dashboard_app.py
import os
from pathlib import Path
import json
import pandas as pd
import streamlit as st
import altair as alt

BASE = Path(__file__).resolve().parent
OUT  = BASE / "out"

ALERTS = OUT / "alerts.csv"
ANOM   = OUT / "anomalies.csv"
EV_AN  = OUT / "event_anomalies.csv"
USRJS  = OUT / "user_summary.json"

st.set_page_config(page_title="Cloud Forensic Dashboard (V4)", layout="wide")
st.title("☁️ Cloud Forensic Dashboard (V4)")
st.caption("AWS CloudTrail 기반 자동 분석 리포트 (alerts.csv, anomalies.csv, user_summary.json)")

# ---------- 데이터 로드 ----------
def load_alerts():
    if not ALERTS.exists():
        return pd.DataFrame()
    df = pd.read_csv(ALERTS)
    # 컬럼 표준화
    expected = ["time","actor","service","action","result","risk_score","reason"]
    df = df[[c for c in expected if c in df.columns]]
    # 시간 파싱 & 파생
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], errors="coerce")
        df["date"] = df["time"].dt.date
        df["hour"] = df["time"].dt.hour
    if "risk_score" in df.columns:
        df["risk_score"] = pd.to_numeric(df["risk_score"], errors="coerce")
    return df

def load_csv(path):
    return pd.read_csv(path) if path.exists() else pd.DataFrame()

def load_user_summary():
    if not USRJS.exists():
        return {}
    with open(USRJS, "r", encoding="utf-8") as f:
        return json.load(f)

df = load_alerts()
anomalies = load_csv(ANOM)
event_anom = load_csv(EV_AN)
profiles = load_user_summary()

if df.empty:
    st.warning("`out/alerts.csv` 가 아직 없습니다. 파이프라인을 먼저 실행하세요.")
    st.stop()

# ---------- 사이드바 필터 ----------
with st.sidebar:
    st.header("🔎 Filters")
    dates = sorted(df["date"].dropna().unique())
    date_range = st.date_input("Date range", value=(dates[0], dates[-1]) if len(dates)>=2 else None)
    services = ["<All>"] + sorted(df["service"].dropna().unique())
    actors   = ["<All>"] + sorted(df["actor"].dropna().unique())
    service_sel = st.selectbox("Service", services)
    actor_sel   = st.selectbox("Actor", actors)
    min_risk    = st.slider("Min Risk Score", 0, int(df["risk_score"].max() if "risk_score" in df else 100), 0)

# 날짜 필터
if isinstance(date_range, tuple) and len(date_range)==2 and date_range[0] and date_range[1]:
    df = df[(df["date"] >= date_range[0]) & (df["date"] <= date_range[1])]
# 서비스/사용자/리스크 필터
if service_sel != "<All>":
    df = df[df["service"] == service_sel]
if actor_sel != "<All>":
    df = df[df["actor"] == actor_sel]
if "risk_score" in df.columns:
    df = df[df["risk_score"] >= min_risk]

# ---------- KPI 상단 카드 ----------
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Events", len(df))
with col2:
    st.metric("Unique Actors", df["actor"].nunique() if "actor" in df else 0)
with col3:
    st.metric("Unique Services", df["service"].nunique() if "service" in df else 0)
with col4:
    avg_risk = round(df["risk_score"].mean(), 2) if "risk_score" in df and len(df)>0 else 0
    st.metric("Avg Risk Score", avg_risk)

st.divider()

# ---------- 차트: 서비스 분포 ----------
st.subheader("📊 Event Distribution by Service")
if "service" in df.columns and not df.empty:
    svc = df["service"].value_counts().reset_index()
    svc.columns = ["service","count"]
    chart = alt.Chart(svc).mark_bar().encode(
        x=alt.X("service:N", sort="-y"),
        y="count:Q",
        tooltip=["service","count"]
    ).properties(height=280)
    st.altair_chart(chart, use_container_width=True)
else:
    st.info("서비스 데이터가 없습니다.")

# ---------- 시간 추이 ----------
st.subheader("⏱️ Events Over Time")
if "time" in df.columns and not df["time"].isna().all():
    ts = df.dropna(subset=["time"]).set_index("time").resample("H").size().reset_index(name="events")
    line = alt.Chart(ts).mark_line(point=True).encode(
        x="time:T", y="events:Q", tooltip=["time:T","events:Q"]
    ).properties(height=280)
    st.altair_chart(line, use_container_width=True)
else:
    st.info("시간 정보가 없습니다.")

# ---------- 테이블: Top 5 위험 이벤트 / 최근 5개 ----------
left, right = st.columns(2)
with left:
    st.markdown("### 🔥 Top 5 Risky Events")
    if "risk_score" in df.columns:
        top5 = df.sort_values("risk_score", ascending=False).head(5)
        st.dataframe(top5, use_container_width=True)
    else:
        st.info("risk_score 컬럼이 없습니다.")

with right:
    st.markdown("### 🆕 Recent 5 Events")
    if "time" in df.columns:
        recent5 = df.sort_values("time", ascending=False).head(5)
        st.dataframe(recent5, use_container_width=True)
    else:
        st.info("time 컬럼이 없습니다.")

st.divider()

# ---------- 이상탐지 섹션 ----------
st.subheader("⚠️ Anomaly Detection")
cols = st.columns(2)

with cols[0]:
    st.markdown("**Anomalous Users (Z-score > 2)**")
    if not anomalies.empty:
        st.dataframe(anomalies, use_container_width=True)
    else:
        st.info("이상 사용자 없음(또는 anomalies.csv 미생성).")

with cols[1]:
    st.markdown("**Anomalous Actions (Z-score > 2)**")
    if not event_anom.empty:
        st.dataframe(event_anom, use_container_width=True)
    else:
        st.info("이상 이벤트 없음(또는 event_anomalies.csv 미생성).")

# ---------- 사용자 프로파일링 요약 ----------
st.subheader("👤 User Profiling Summary")
if profiles:
    prof_df_rows = []
    for user, info in profiles.items():
        services = ", ".join(list(info.get("services", {}).keys())[:2]) or "-"
        time_dist = info.get("time_distribution", {})
        active = max(time_dist, key=time_dist.get) if time_dist else "-"
        prof_df_rows.append({
            "user": user,
            "main_services": services,
            "active_hours": active,
            "total_events": info.get("total_events", 0)
        })
    prof_df = pd.DataFrame(prof_df_rows).sort_values("total_events", ascending=False)
    st.dataframe(prof_df, use_container_width=True)
else:
    st.info("user_summary.json 미생성.")

# ---------- 다운로드 ----------
st.subheader("⬇️ Download")
import subprocess

st.divider()
st.subheader("📄 Generate PDF Report")

report_path = BASE / "reports" / "report.pdf"

if st.button("Generate PDF Report"):
    try:
        with st.spinner("Generating PDF report..."):
            subprocess.run(["python", str(BASE / "src" / "report_generator.py")], check=True)
        st.success(f"✅ Report generated successfully!")
        if report_path.exists():
            with open(report_path, "rb") as f:
                st.download_button(
                    label="📥 Download Latest report.pdf",
                    data=f,
                    file_name="report.pdf",
                    mime="application/pdf"
                )
    except subprocess.CalledProcessError as e:
        st.error(f"❌ Error generating report: {e}")

c1, c2, c3 = st.columns(3)
with c1:
    if ALERTS.exists():
        st.download_button("Download alerts.csv", ALERTS.read_bytes(), file_name="alerts.csv")
with c2:
    if ANOM.exists():
        st.download_button("Download anomalies.csv", ANOM.read_bytes(), file_name="anomalies.csv")
with c3:
    if USRJS.exists():
        st.download_button("Download user_summary.json", USRJS.read_bytes(), file_name="user_summary.json")

st.caption("© CloudForensic-ReportSystem V3")
