import json
import csv
from pathlib import Path

PARSED = Path(r"E:\고은폴더\대학교\정보보안\3학년\캡스톤디자인(3-2)\CloudForensic-ReportSystem\data/parsed_logs.jsonl")
RULES  = Path(r"E:\고은폴더\대학교\정보보안\3학년\캡스톤디자인(3-2)\CloudForensic-ReportSystem\rules/sensitive_apis.json")
OUT    = Path(r"E:\고은폴더\대학교\정보보안\3학년\캡스톤디자인(3-2)\CloudForensic-ReportSystem\out/alerts.csv")

def load_rules():
    with open(RULES, encoding="utf-8") as f:
        return json.load(f)

def match_rule(rules, service, action):
    # 우선순위: service:action → service:* → *:action → *:*
    keys = [
        f"{service}:{action}",
        f"{service}:*",
        f"*:{action}",
        "*:*"
    ]
    for k in keys:
        if k in rules:
            return rules[k]
    return {"risk": 10, "reason": "규칙 없음(기본)"}

def main():
    rules = load_rules()
    OUT.parent.mkdir(parents=True, exist_ok=True)

    with open(PARSED, encoding="utf-8") as fin, \
         open(OUT, "w", newline="", encoding="utf-8") as fout:

        writer = csv.writer(fout)
        writer.writerow(["time","actor","service","action","result","risk_score","reason"])

        for line in fin:
            if not line.strip():
                continue
            evt = json.loads(line)
            service = (evt.get("service") or "").strip().lower()
            action  = evt.get("action") or "Unknown"

            rule = match_rule(rules, service, action)
            writer.writerow([
                evt.get("eventTime",""),
                evt.get("actor","Unknown"),
                service,
                action,
                evt.get("result",""),
                rule["risk"],
                rule["reason"]
            ])

    print(f"✅ 분석 완료 → {OUT}")

# ==========================
# ✅ V3 기능: 이상행동 탐지 (Z-score)
# ==========================
import pandas as pd
from scipy.stats import zscore
from pathlib import Path

ALERTS = Path("../out/alerts.csv")
if not ALERTS.exists():
    raise FileNotFoundError("❌ alerts.csv 파일이 존재하지 않습니다. 먼저 log_analyzer를 실행하세요.")

# 1️⃣ CSV 불러오기
df = pd.read_csv(ALERTS)

# 2️⃣ 사용자별 이벤트 발생 횟수 계산
user_counts = df['actor'].value_counts().reset_index()
user_counts.columns = ['actor', 'count']

# 3️⃣ 각 사용자별 Z-score 계산
user_counts['zscore'] = zscore(user_counts['count'])

# 4️⃣ 이상값 탐지 (Z-score > 2 인 경우)
anomalies = user_counts[user_counts['zscore'] > 2]

# 5️⃣ 결과 저장
out_path = Path("../out/anomalies.csv")
out_path.parent.mkdir(parents=True, exist_ok=True)
anomalies.to_csv(out_path, index=False, encoding="utf-8-sig")

print(f"✅ 이상행동 탐지 완료 → {out_path} (총 {len(anomalies)}명 탐지)")

if __name__ == "__main__":
    main()
