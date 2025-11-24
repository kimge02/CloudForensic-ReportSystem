📌 CloudForensic-ReportSystem (V4)

AWS CloudTrail 기반 자동 수집 → 정규화 → 분석 → 리포트 생성 → Slack 알림까지
완전 자동화된 클라우드 포렌식 리포트 생성 시스템

🚀 V4 핵심 기능 요약
✅ 1. S3 기반 실시간 CloudTrail 로그 자동 수집

main.py 실행 시 S3 버킷을 자동 체크

CloudTrail 최신 로그(JSON / JSON.GZ) 다운로드

Digest 및 불필요 로그 제외

✅ 2. 로그 정규화(log_collector.py – V4)

raw_logs/ + raw_logs/expanded/ + S3로 받은 로그 모두 처리

CloudTrail 형식 차이 해결

공통 JSON(LINE JSON – jsonl) 구조로 출력

✅ 3. 위험 이벤트 탐지(log_analyzer.py – V4)

rules/sensitive_apis.json 사용한 정규 탐지

권한 상승 / 사용자 생성 / IAM 변경 / CloudTrail 설정 변경 등 탐지

결과 → alerts.csv 생성

✅ 4. 이상행동 분석 (Z-score + IsolationForest)

사용자 활동량 기반 Z-score 이상치 계산 → anomalies.csv

이벤트 기반 행동 분포 기반 IsolationForest → event_anomalies.csv

✅ 5. 사용자 프로파일링(user_profiler.py – V4)

최근 활동, 서비스 사용 비율, 위험 이벤트 개수 자동 분석

user_summary.json 생성

✅ 6. PDF 자동 리포트(report_generator.py – V4)

Anomaly Summary

Risky Events

User Profiling Summary

Recent 5 Events

서비스별 이벤트 분포 그래프 포함

reports/report.pdf 출력됨

✅ 7. Slack 알림(alert_sender.py + config.json)

이상 이벤트 발생 시 Slack 채널로 자동 알림

Webhook 기반 메시지 전송

✅ 8. 전체 파이프라인 자동 실행(main.py – V4)

한 번 실행으로 흐름 전체가 돌아감:

S3 다운로드 → 로그 정규화 → 분석 → 프로파일링 → 리포트 생성 → Slack 알림

📂 프로젝트 구조 (V4)
CloudForensic-ReportSystem/
 ┣ config.json                ← Slack 설정
 ┣ main.py                    ← 전체 파이프라인 자동 실행
 ┣ .gitignore
 ┣ rules/
 │   ┗ sensitive_apis.json
 ┣ data/
 │   ┣ raw_logs/
 │   ┣ parsed_logs.jsonl
 │   ┣ anomalies.csv
 │   ┣ event_anomalies.csv
 │   ┗ user_summary.json
 ┣ reports/
 │   ┗ report.pdf
 ┣ out/
 │   ┗ service_chart.png
 ┗ src/
     ┣ log_collector.py
     ┣ log_analyzer.py
     ┣ user_profiler.py
     ┣ report_generator.py
     ┣ alert_sender.py
     ┗ s3_downloader.py

⚙️ 설치 및 실행 방법
1) 패키지 설치
pip install -r requirements.txt

2) Slack Webhook 설정

config.json 생성:

{
    "enable_slack": true,
    "slack_webhook_url": "https://hooks.slack.com/services/여기에_웹훅_URL"
}

3) 전체 파이프라인 실행
python main.py


실행 후 자동으로 생성됨:

alerts.csv

anomalies.csv

event_anomalies.csv

user_summary.json

report.pdf

Slack 메시지 전송

🧪 테스트 방법
Slack 알림 테스트
python src/alert_sender.py

로그 수집만 테스트
python src/log_collector.py

분석만 테스트
python src/log_analyzer.py

리포트만 생성
python src/report_generator.py

🛠 V3 → V4 개선점 비교
기능	V3	V4
로그 수집	로컬 JSON만	S3 자동 수집 + GZ 지원
탐지 엔진	규칙 기반	규칙 + 이상치 분석 통합
프로파일링	없음	사용자 행동 분석 추가
리포트	기본 구조	Anomaly·Profiling·Recent Events 확장
실시간성	없음	main.py로 완전 자동화
알림	없음	Slack 알림 지원




