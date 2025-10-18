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

if __name__ == "__main__":
    main()
