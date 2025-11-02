import pandas as pd
import json
from pathlib import Path
from datetime import datetime

# 파일 경로
ALERTS = Path(__file__).resolve().parent.parent / "out" / "alerts.csv"
OUT_JSON = Path(__file__).resolve().parent.parent / "out" / "user_summary.json"

def extract_hour(timestamp):
    """이벤트 발생 시각에서 시(hour)만 추출"""
    try:
        return datetime.fromisoformat(timestamp.replace("Z", "")).hour
    except Exception:
        return None

def generate_user_profile():
    df = pd.read_csv(ALERTS)
    profiles = {}

    for user, group in df.groupby("actor"):
        profile = {
            "total_events": len(group),
            "services": group["service"].value_counts().to_dict(),
            "actions": group["action"].value_counts().head(5).to_dict(),  # 상위 5개
        }

        # 리전 통계 (있을 경우만)
        if "region" in group.columns:
            profile["regions"] = group["region"].value_counts().to_dict()

        # 시간대 통계
        hours = group["time"].dropna().apply(extract_hour).dropna()
        if not hours.empty:
            hour_bins = pd.cut(hours, bins=[0,6,12,18,24], labels=["00-06","06-12","12-18","18-24"], right=False)
            profile["time_distribution"] = hour_bins.value_counts().sort_index().to_dict()

        profiles[user] = profile

    # 저장
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=4, ensure_ascii=False)

    print(f"✅ 사용자 프로파일링 완료 → {OUT_JSON}")

if __name__ == "__main__":
    generate_user_profile()
