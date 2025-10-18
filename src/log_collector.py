import json
from pathlib import Path

data_dir = Path("../data/raw_logs")
out_path = Path("../data/parsed_logs.jsonl")

def normalize_event(event):
    service = ""
    src = event.get("eventSource")
    if src:
        service = src.split(".")[0].lower()

    action = event.get("eventName") or "Unknown"
    actor  = event.get("userIdentity", {}).get("userName") or \
             event.get("userIdentity", {}).get("arn", "Unknown").split("/")[-1]

    # 에러코드 기반 판정이 더 정확
    result = "Allowed"
    err = event.get("errorCode")
    if err:
        result = err


    return {
        "eventTime": event.get("eventTime", ""),
        "service": service,
        "action": action,
        "actor": actor,
        "result": result
    }

def main():
    with open(out_path, "w", encoding="utf-8") as out:
        for file in data_dir.glob("*.json"):
            with open(file, encoding="utf-8") as f:
                data = json.load(f)
                for e in data.get("Records", []):
                    parsed = normalize_event(e)
                    out.write(json.dumps(parsed) + "\n")
    print(f"✅ 정규화 완료 → {out_path}")

if __name__ == "__main__":
    main()
