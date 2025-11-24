import json
import csv
from pathlib import Path

import pandas as pd
from scipy.stats import zscore

# ==========================
# 📁 경로 설정 (프로젝트 루트 기준)
# ==========================

ROOT_DIR = Path(__file__).resolve().parents[1]          # .../CloudForensic-ReportSystem
DATA_DIR = ROOT_DIR / "data"
OUT_DIR = ROOT_DIR / "out"
RULES_PATH = ROOT_DIR / "rules" / "sensitive_apis.json"
PARSED_PATH = DATA_DIR / "parsed_logs.jsonl"
ALERTS_PATH = OUT_DIR / "alerts.csv"
USER_ANOM_PATH = OUT_DIR / "anomalies.csv"
EVENT_ANOM_PATH = OUT_DIR / "event_anomalies.csv"


# ==========================
# 🔧 규칙 로딩 & 매칭
# ==========================

def load_rules():
    """rules/sensitive_apis.json 로드 (없으면 기본 규칙 생성)"""
    if not RULES_PATH.exists():
        print(f"⚠ 규칙 파일이 없습니다: {RULES_PATH}")
        print("   → 기본 규칙(*:*) 10점 Normal event로 대체합니다.")
        return {"*:*": {"risk": 10, "reason": "Normal event"}}

    with open(RULES_PATH, encoding="utf-8") as f:
        return json.load(f)


def match_rule(rules, service, action):
    """
    우선순위:
      1) service:action
      2) service:*
      3) *:action
      4) *:*
    """
    service = (service or "").strip().lower()
    action = action or "Unknown"

    keys = [
        f"{service}:{action}",
        f"{service}:*",
        f"*:{action}",
        "*:*",
    ]
    for k in keys:
        if k in rules:
            return rules[k]
    # 여기에 도달하면 규칙에 전혀 없음 → 기본값
    return {"risk": 10, "reason": "규칙 없음(기본)"}


# ==========================
# 1️⃣ 알림(alerts.csv) 생성
# ==========================

def generate_alerts():
    """
    parsed_logs.jsonl + rules/sensitive_apis.json 을 기반으로
    out/alerts.csv 생성
    """
    if not PARSED_PATH.exists():
        print(f"❌ 정규화 로그 파일이 없습니다: {PARSED_PATH}")
        print("   → 먼저 log_collector.py 를 실행해서 parsed_logs.jsonl 을 생성하세요.")
        return False

    rules = load_rules()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(PARSED_PATH, encoding="utf-8") as fin, \
         open(ALERTS_PATH, "w", newline="", encoding="utf-8") as fout:

        writer = csv.writer(fout)
        writer.writerow(["time", "actor", "service", "action", "result", "risk_score", "reason"])

        count = 0
        for line in fin:
            line = line.strip()
            if not line:
                continue
            try:
                evt = json.loads(line)
            except json.JSONDecodeError:
                continue

            service = (evt.get("service") or "").strip().lower()
            action = evt.get("action") or "Unknown"

            rule = match_rule(rules, service, action)

            writer.writerow([
                evt.get("eventTime", ""),
                evt.get("actor", "Unknown"),
                service,
                action,
                evt.get("result", ""),
                rule.get("risk", 10),
                rule.get("reason", "규칙 없음(기본)"),
            ])
            count += 1

    print(f"✅ alerts.csv 생성 완료 → {ALERTS_PATH} (총 {count}건)")
    return True


# ==========================
# 2️⃣ 사용자 단위 이상행동 탐지 (anomalies.csv)
# ==========================

def detect_user_anomalies(threshold=2.0):
    """
    alerts.csv 기반으로 actor별 이벤트 수를 세고,
    Z-score > threshold 인 사용자만 anomalies.csv에 저장
    """
    if not ALERTS_PATH.exists():
        print(f"⚠ alerts.csv 가 없습니다: {ALERTS_PATH}")
        print("   → generate_alerts()를 먼저 실행해야 합니다.")
        return False

    df = pd.read_csv(ALERTS_PATH)

    if "actor" not in df.columns:
        print("⚠ alerts.csv 에 'actor' 컬럼이 없습니다. 이상 사용자 탐지를 건너뜁니다.")
        return False

    if df.empty:
        print("⚠ alerts.csv 가 비어 있습니다. 이상 사용자 탐지를 건너뜁니다.")
        return False

    user_counts = df["actor"].value_counts().reset_index()
    user_counts.columns = ["actor", "count"]

    if len(user_counts) < 2:
        print("⚠ 사용자 수가 너무 적어 Z-score를 계산할 수 없습니다.")
        return False

    user_counts["zscore"] = zscore(user_counts["count"])

    anomalies = user_counts[user_counts["zscore"] > threshold]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    anomalies.to_csv(USER_ANOM_PATH, index=False, encoding="utf-8-sig")

    print(f"✅ 사용자 이상행동 탐지 완료 → {USER_ANOM_PATH} (임계값 Z>{threshold}, 총 {len(anomalies)}명)")
    return True


# ==========================
# 3️⃣ 이벤트(action) 단위 이상탐지 (event_anomalies.csv)
# ==========================

def detect_event_anomalies(threshold=2.0):
    """
    alerts.csv 기반으로 action별 발생 횟수를 세고,
    Z-score > threshold 인 action만 event_anomalies.csv에 저장
    """
    if not ALERTS_PATH.exists():
        print(f"⚠ alerts.csv 가 없습니다: {ALERTS_PATH}")
        print("   → generate_alerts()를 먼저 실행해야 합니다.")
        return False

    df = pd.read_csv(ALERTS_PATH)

    if "action" not in df.columns:
        print("⚠ alerts.csv 에 'action' 컬럼이 없습니다. 이상 이벤트 탐지를 건너뜁니다.")
        return False

    if df.empty:
        print("⚠ alerts.csv 가 비어 있습니다. 이상 이벤트 탐지를 건너뜁니다.")
        return False

    event_counts = df["action"].value_counts().reset_index()
    event_counts.columns = ["action", "count"]

    if len(event_counts) < 2:
        print("⚠ 이벤트 종류가 너무 적어 Z-score를 계산할 수 없습니다.")
        return False

    event_counts["zscore"] = zscore(event_counts["count"])
    anomalies = event_counts[event_counts["zscore"] > threshold]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    anomalies.to_csv(EVENT_ANOM_PATH, index=False, encoding="utf-8-sig")

    print(f"✅ 이벤트 이상탐지 완료 → {EVENT_ANOM_PATH} (임계값 Z>{threshold}, 총 {len(anomalies)}개)")
    return True


# ==========================
# 🔔 V4용 통합 엔트리 포인트
# ==========================

def analyze_logs(user_thresh=2.0, event_thresh=2.0):
    """
    V4에서 main.py 등에서 호출할 통합 함수.
    1) alerts.csv 생성
    2) anomalies.csv 생성 (사용자)
    3) event_anomalies.csv 생성 (이벤트)
    """
    print("\n=== [Analyzer] Step 1: Generate alerts.csv ===")
    ok = generate_alerts()
    if not ok:
        print("❌ alerts.csv 생성 실패 → 이후 단계를 건너뜁니다.")
        return

    print("\n=== [Analyzer] Step 2: User anomaly detection (anomalies.csv) ===")
    detect_user_anomalies(threshold=user_thresh)

    print("\n=== [Analyzer] Step 3: Event anomaly detection (event_anomalies.csv) ===")
    detect_event_anomalies(threshold=event_thresh)

    print("\n✅ Analyzer 전체 작업 완료\n")


def main():
    """단독 실행용 (python src/log_analyzer.py)"""
    analyze_logs()


if __name__ == "__main__":
    main()
