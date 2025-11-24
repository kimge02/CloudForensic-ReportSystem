import os
from pathlib import Path

import boto3
import pandas as pd

from src.log_collector import collect_logs
from src.log_analyzer import analyze_logs
from src.user_profiler import generate_user_profile
from src.report_generator import generate_report
from src.alert_sender import send_slack_message

# ==============================
# 🔧 환경 설정
# ==============================

# 네가 만든 CloudTrail용 S3 버킷 이름
BUCKET = "cloudtrail-log-demo-goeun"     # ← 필요하면 여기 버킷 이름만 수정
PREFIX = "AWSLogs/"                      # CloudTrail이 기본으로 쓰는 prefix

ROOT_DIR = Path(__file__).resolve().parent
RAW_DIR = ROOT_DIR / "data" / "raw_logs"
OUT_DIR = ROOT_DIR / "out"


# ==============================
# 1️⃣ S3에서 CloudTrail 로그 다운로드
# ==============================

def download_new_logs():
    s3 = boto3.client("s3")

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[S3] Listing objects from s3://{BUCKET}/{PREFIX}")
    objects = s3.list_objects_v2(Bucket=BUCKET, Prefix=PREFIX)

    if "Contents" not in objects:
        print("[S3] No logs found in S3.")
        return

    count = 0
    for obj in objects["Contents"]:
        key = obj["Key"]

        # CloudTrail 로그 파일만 대상 (.json 또는 .json.gz)
        if not (key.endswith(".json") or key.endswith(".json.gz")):
            continue

        # 로컬 파일 이름: 경로 구분자를 _로 치환
        local_path = RAW_DIR / key.replace("/", "_")
        if local_path.exists():
            # 이미 받은 파일은 스킵 (원하면 지우고 다시 받는 로직으로 바꿀 수 있음)
            continue

        print(f"[S3] Downloading {key} → {local_path}")
        local_path.parent.mkdir(parents=True, exist_ok=True)
        s3.download_file(BUCKET, key, str(local_path))
        count += 1

    print(f"[S3] ✅ S3 Log Download Complete (new files: {count})")


# ==============================
# 2️⃣ Slack에 요약 알림 보내기
# ==============================

def send_slack_summary():
    """
    alerts.csv / anomalies.csv / event_anomalies.csv 기반으로
    Slack에 간단한 요약 알림 전송
    """
    alerts_path = OUT_DIR / "alerts.csv"
    user_anom_path = OUT_DIR / "anomalies.csv"
    event_anom_path = OUT_DIR / "event_anomalies.csv"

    if not alerts_path.exists():
        print("[Slack] alerts.csv 가 없어서 Slack 요약을 건너뜀")
        return

    try:
        df_alerts = pd.read_csv(alerts_path)
    except Exception as e:
        print(f"[Slack] alerts.csv 읽기 오류: {e}")
        return

    total_events = len(df_alerts)
    avg_risk = None
    if "risk_score" in df_alerts.columns and total_events > 0:
        avg_risk = df_alerts["risk_score"].mean()

    # 이상 사용자
    user_cnt = 0
    user_list_preview = ""
    if user_anom_path.exists():
        try:
            df_u = pd.read_csv(user_anom_path)
            user_cnt = len(df_u)
            if user_cnt > 0:
                preview = df_u["actor"].astype(str).tolist()
                if len(preview) > 3:
                    preview = preview[:3] + ["..."]
                user_list_preview = ", ".join(preview)
        except Exception as e:
            print(f"[Slack] anomalies.csv 읽기 오류: {e}")

    # 이상 이벤트
    event_cnt = 0
    event_list_preview = ""
    if event_anom_path.exists():
        try:
            df_e = pd.read_csv(event_anom_path)
            event_cnt = len(df_e)
            if event_cnt > 0:
                preview = df_e["action"].astype(str).tolist()
                if len(preview) > 3:
                    preview = preview[:3] + ["..."]
                event_list_preview = ", ".join(preview)
        except Exception as e:
            print(f"[Slack] event_anomalies.csv 읽기 오류: {e}")

    # Slack 메시지 구성
    lines = [
        "⚠️ *CloudTrail 분석 완료 (CloudForensic-ReportSystem V4)*",
        f"- 총 이벤트 수: *{total_events}*",
    ]

    if avg_risk is not None:
        lines.append(f"- 평균 위험도 점수: *{avg_risk:.1f}*")

    lines.append(f"- 이상 사용자 수: *{user_cnt}*")
    if user_list_preview:
        lines.append(f"  · 예시: {user_list_preview}")

    lines.append(f"- 이상 이벤트 종류 수: *{event_cnt}*")
    if event_list_preview:
        lines.append(f"  · 예시: {event_list_preview}")

    lines.append("")
    lines.append("📄 자세한 내용은 최신 report.pdf를 확인하세요.")

    text = "\n".join(lines)

    # 실제 Slack 전송 (config.json 설정 따라감)
    send_slack_message(text)


# ==============================
# 🔄 메인 파이프라인
# ==============================

def main():
    print("\n=== Step 1: Downloading Logs from S3 ===")
    download_new_logs()

    print("\n=== Step 2: Normalizing Logs (log_collector) ===")
    collect_logs()

    print("\n=== Step 3: Detecting Anomalies (log_analyzer) ===")
    analyze_logs()

    print("\n=== Step 4: User Profiling (user_profiler) ===")
    generate_user_profile()

    print("\n=== Step 5: Generating PDF Report (report_generator) ===")
    generate_report()

    print("\n=== Step 6: Sending Slack Summary ===")
    try:
        send_slack_summary()
    except Exception as e:
        print(f"[Slack] 요약 알림 전송 중 오류: {e}")

    print("\n[✓] All steps completed successfully!\n")


if __name__ == "__main__":
    main()

