import json
from pathlib import Path

# 🔧 raw_logs와 expanded 폴더 모두 탐색
base_dir = Path("../data/raw_logs")
expanded_dir = base_dir / "expanded"
out_path = Path("../data/parsed_logs.jsonl")

def normalize_event(event):
    service = ""
    src = event.get("eventSource")
    if src:
        service = src.split(".")[0].lower()

    action = event.get("eventName") or "Unknown"
    actor  = event.get("userIdentity", {}).get("userName") or \
             event.get("userIdentity", {}).get("arn", "Unknown").split("/")[-1]

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
        # ✅ 두 폴더 모두 읽기
        all_files = list(base_dir.glob("*.json"))
        if expanded_dir.exists():
            all_files += list(expanded_dir.glob("*.json"))

        print(f"[+] Found {len(all_files)} log files to process")

        for file in all_files:
            with open(file, encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print(f"[!] Invalid JSON: {file}")
                    continue

                for e in data.get("Records", []):
                    parsed = normalize_event(e)
                    out.write(json.dumps(parsed) + "\n")
    print(f"✅ 정규화 완료 → {out_path}")

if __name__ == "__main__":
    main()

