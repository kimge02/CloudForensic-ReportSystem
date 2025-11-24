# src/log_collector.py
import json
import gzip
from pathlib import Path

# 프로젝트 루트 기준으로 paths 계산
ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR  = ROOT_DIR / "data" / "raw_logs"
OUT_PATH = ROOT_DIR / "data" / "parsed_logs.jsonl"


def normalize_event(event: dict) -> dict:
    """
    CloudTrail 이벤트 하나를 우리가 쓰는 공통 포맷으로 변환
    """
    service = ""
    src = event.get("eventSource")
    if src:
        service = src.split(".")[0].lower()

    action = event.get("eventName") or "Unknown"

    # actor: userName 우선, 없으면 ARN 뒤쪽
    identity = event.get("userIdentity", {}) or {}
    actor = identity.get("userName")
    if not actor:
        arn = identity.get("arn", "Unknown")
        actor = arn.split("/")[-1] if "/" in arn else arn

    result = "Allowed"
    err = event.get("errorCode")
    if err:
        result = err

    return {
        "eventTime": event.get("eventTime", ""),
        "service": service,
        "action": action,
        "actor": actor,
        "result": result,
    }


def collect_logs():
    """
    data/raw_logs 안의 *.json, *.json.gz 를 모두 읽어서
    data/parsed_logs.jsonl 로 정규화해서 저장
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # .json + .json.gz 모두 대상
    all_files = list(RAW_DIR.glob("*.json")) + list(RAW_DIR.glob("*.json.gz"))
    print(f"[collector] Found {len(all_files)} raw log files")

    total_events = 0

    with OUT_PATH.open("w", encoding="utf-8") as out_f:
        for fp in all_files:
            # CloudTrail-Digest 파일은 무시 (Records가 아니라 서명 정보라서)
            if "CloudTrail-Digest" in fp.name:
                # 필요하면 여기에서 따로 로깅만 하고 continue
                continue

            # 압축 여부에 따라 다르게 열기
            if fp.suffix == ".gz":
                f = gzip.open(fp, "rt", encoding="utf-8")
            else:
                f = fp.open("r", encoding="utf-8")

            try:
                with f:
                    data = json.load(f)
            except json.JSONDecodeError:
                print(f"[collector] Invalid JSON, skip: {fp}")
                continue

            records = data.get("Records", [])
            if not records:
                # CloudTrail-Digest 처럼 Records 없는 것도 많음
                continue

            for e in records:
                parsed = normalize_event(e)
                out_f.write(json.dumps(parsed, ensure_ascii=False) + "\n")
                total_events += 1

    print(f"✅ 정규화 완료 → {OUT_PATH} (총 {total_events} events)")


if __name__ == "__main__":
    collect_logs()



