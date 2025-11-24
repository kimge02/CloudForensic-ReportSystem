import json
import requests
from pathlib import Path

CONFIG = Path(__file__).resolve().parents[1] / "config.json"

def send_slack_message(text: str):
    if not CONFIG.exists():
        print("⚠ config.json 없음 → Slack 알림 비활성화")
        return

    with open(CONFIG, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    if not cfg.get("enable_slack", False):
        print("ℹ enable_slack = false → 전송 안 함")
        return

    url = cfg.get("slack_webhook_url")
    if not url:
        print("⚠ slack_webhook_url 없음 → 전송 불가")
        return

    payload = {"text": text}

    try:
        resp = requests.post(url, json=payload)
        print(f"HTTP status: {resp.status_code}")
        print(f"Slack response: {resp.text}")
        if resp.status_code == 200:
            print(f"📨 Slack 전송 완료: {text}")
        else:
            print("⚠ Slack 쪽에서 에러 응답을 줬음. 위 메시지 참고.")
    except Exception as e:
        print(f"⚠ Slack 전송 오류: {e}")

if __name__ == "__main__":
    send_slack_message("🔔 테스트 알림: CloudForensic-ReportSystem Slack 연동 디버그 테스트!")

