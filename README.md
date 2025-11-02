# ☁️ Cloud Forensic Automatic Report System  
AWS CloudTrail 기반 **자동 로그 분석 및 보안 리포트 생성 시스템**

---

## 📘 프로젝트 개요

이 시스템은 **AWS CloudTrail 로그를 자동으로 수집, 분석, 시각화**하여  
보안 이상행동을 탐지하고 **PDF 리포트** 및 **웹 대시보드** 형태로 자동 보고합니다.  

> 👤 팀장: 김고은  
> 🏫 배재대학교 정보보안학과 캡스톤디자인 (2025년 2학기)  
> 📦 Repository: [github.com/kimge02/CloudForensic-ReportSystem](https://github.com/kimge02/CloudForensic-ReportSystem)

---

## 🧩 시스템 구조

CloudForensic-ReportSystem/
┣ data/
┃ ┣ raw_logs/ ← 원본 AWS CloudTrail 로그(JSON)
┃ ┣ parsed_logs.jsonl ← 정규화된 로그
┣ out/
┃ ┣ alerts.csv ← 이벤트 분석 결과
┃ ┣ anomalies.csv ← 사용자 이상탐지
┃ ┣ event_anomalies.csv ← 이벤트 이상탐지
┃ ┣ user_summary.json ← 사용자 프로파일링
┃ ┣ service_chart.png ← 서비스별 그래프
┣ reports/
┃ ┗ report.pdf ← 자동 생성 리포트
┣ rules/
┃ ┗ sensitive_apis.json ← 위험도 규칙 파일
┣ src/
┃ ┣ log_collector.py ← 로그 정규화
┃ ┣ log_analyzer.py ← 이상행동 탐지
┃ ┣ report_generator.py ← PDF 리포트 생성
┃ ┣ user_profiler.py ← 사용자 프로파일링
┃ ┗ watcher.py ← 실시간 감시 자동화
┣ dashboard_app.py ← Streamlit 대시보드




---

## 🧠 주요 실행 흐름

```bash
python src/log_collector.py     # CloudTrail JSON 로그 → 표준화 JSONL
python src/log_analyzer.py      # 위험도 규칙 기반 이상행동 탐지
python src/user_profiler.py     # 사용자별 활동 패턴 요약
python src/report_generator.py  # PDF 리포트 자동 생성
python src/watcher.py           # 실시간 로그 감시 자동화
streamlit run dashboard_app.py  # Streamlit 웹 대시보드 실행
🧾 Version History
🥇 V1.0 — 기본 분석 및 리포트 시스템 구축
기능	설명
CloudTrail 로그 정규화	log_collector.py로 핵심 필드만 추출
위험도 기반 이벤트 탐지	rules/sensitive_apis.json을 기반으로 탐지
기본 PDF 리포트	report_generator.py로 상위 위험 이벤트 요약
🥈 V2.0 — 시각화 및 데이터 확장
기능	설명
서비스별 이벤트 그래프 추가	matplotlib 그래프 자동 삽입 (service_chart.png)
로그 데이터 증식 및 다변화	다양한 샘플 로그 추가 (expanded/)
리포트 자동화 강화	평균 위험도 / 상위 이벤트 표 포함
코드 구조 개선	함수화 및 폴더 구조 정리
🥇 V3.0 — 실시간 감시 + 사용자 프로파일링 + 대시보드
기능 구분	설명	파일/모듈
이상행동 탐지 고도화	Z-score 기반 사용자/이벤트 빈도 이상탐지 (anomalies.csv, event_anomalies.csv)	src/log_analyzer.py
사용자 프로파일링	사용자별 활동 패턴 요약 (서비스, 시간대, 이벤트 수)	src/user_profiler.py
PDF 리포트 확장	이상탐지/프로파일링 요약 자동 포함	src/report_generator.py
실시간 감시 기능	watchdog 기반 로그 감시 및 자동 리포트 생성	src/watcher.py
Streamlit 대시보드	웹 기반 로그 시각화 및 필터링 기능	dashboard_app.py
S3·CloudWatch 탐지 강화	rules/sensitive_apis.json 업데이트	rules/sensitive_apis.json
📊 리포트 예시 (V3)

Anomaly Summary: 비정상 사용자 및 API 호출 자동 요약

User Profiling Summary: 주요 서비스 / 시간대별 활동 패턴

Service-wise Event Chart: 서비스별 이벤트 분포

Top 5 Risk Events: 위험도 상위 이벤트 리스트

🖥️ Streamlit 대시보드 개요
항목	설명
Service Distribution	서비스별 이벤트 비율 시각화
Risk Score Histogram	위험도 분포 차트
Event Viewer	전체 로그 상세 검색
Top Actors	사용자별 로그 빈도 상위 목록

실행 명령:

streamlit run dashboard_app.py

🧾 Output Files
경로	설명
out/alerts.csv	모든 이벤트 분석 결과
out/anomalies.csv	사용자 기반 이상탐지 결과
out/event_anomalies.csv	이벤트 호출 빈도 이상탐지
out/user_summary.json	사용자별 패턴 요약
reports/report.pdf	자동 생성 리포트
out/service_chart.png	서비스별 이벤트 분포 그래프
🏷️ Git 버전 태그
git tag -a v1.0 -m "Initial version: Basic report generator"
git tag -a v2.0 -m "V2: Added charts, improved analysis"
git tag -a v3.0 -m "V3: Streamlit dashboard + real-time monitoring"
git push origin --tags




