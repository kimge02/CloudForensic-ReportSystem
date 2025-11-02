import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path

# 감시할 폴더 (raw_logs)
WATCH_DIR = Path(__file__).resolve().parent.parent / "data" / "raw_logs"
print(f"👀 Monitoring folder: {WATCH_DIR}")

# 순서대로 실행할 스크립트
SCRIPTS = [
    "log_collector.py",
    "log_analyzer.py",
    "report_generator.py"
]

class LogHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith(".json"):
            return
        print(f"\n🟢 새 로그 감지됨: {event.src_path}")

        for script in SCRIPTS:
            script_path = Path(__file__).resolve().parent / script
            print(f"▶ 실행 중: {script_path.name}")
            try:
                subprocess.run(["python", str(script_path)], check=True)
            except subprocess.CalledProcessError as e:
                print(f"❌ 오류: {e}")
                break

        print("✅ 모든 분석 및 리포트 완료!\n")

def main():
    event_handler = LogHandler()
    observer = Observer()
    observer.schedule(event_handler, str(WATCH_DIR), recursive=False)
    observer.start()
    print("🚀 실시간 로그 감시 시작 (Ctrl+C로 종료)")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("🛑 감시 중단됨")

    observer.join()

if __name__ == "__main__":
    main()
