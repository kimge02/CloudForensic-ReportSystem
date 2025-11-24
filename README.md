---

# 🌩️ CloudForensic-ReportSystem (V4)

AWS CloudTrail 기반 **자동 수집 → 정규화 → 분석 → 리포트 생성 → Slack 알림**까지
완전 자동화된 **클라우드 포렌식 리포트 생성 시스템**

---

## 🚀 V4 핵심 기능 요약

### ✅ 1. **S3 기반 실시간 CloudTrail 로그 자동 수집**

* `main.py` 실행 시 S3 버킷 자동 체크
* 최신 CloudTrail 로그(JSON / JSON.GZ) 다운로드
* Digest 파일 및 불필요 로그 자동 제거

---

### ✅ 2. **로그 정규화 (`log_collector.py` - V4)**

* `raw_logs/` + `raw_logs/expanded/` + **S3 다운로드 로그** 모두 처리
* CloudTrail 형식 차이 완전 해결
* 공통 JSONL(JSON Lines) 구조로 변환
* 출력: `data/parsed_logs.jsonl`

---

### ✅ 3. **위험 이벤트 탐지 (`log_analyzer.py` - V4)**

* `rules/sensitive_apis.json` 기반 정교한 규칙 탐지
* IAM 변경 / 권한 상승 / CloudTrail 설정 변경 등 위험행위 탐지
* 출력: `out/alerts.csv`

---

### ✅ 4. **이상행동 분석 (Z-score + IsolationForest)**

* 사용자별 비정상 패턴 탐지
* 이벤트 기반 통계 분석
* 출력:

  * `out/anomalies.csv`
  * `out/event_anomalies.csv`

---

### ✅ 5. **사용자 프로파일링 (`user_profiler.py`)**

* 사용자별 CloudTrail 활동 패턴 추출
* 요약 정보 생성
* 출력: `out/user_summary.json`

---

### ✅ 6. **PDF 포렌식 리포트 생성 (`report_generator.py`)**

포함 내용:

* 전체 이벤트 요약
* Top 위험 이벤트
* 사용자 이상행동 요약
* 최근 5개 이벤트
* 서비스별 이벤트 분포 그래프
* 출력: `reports/report.pdf`

---

### ✅ 7. **Slack 알림 자동 발송 (`alert_sender.py`)**

* 분석 완료 시 Slack 채널에 자동 메시지 전송
* Slack Webhook 기반
* `config.json`으로 기능 on/off 가능

예시 알림:

```
⚠️ CloudTrail 분석 완료  
- 총 이벤트 수: xxxx  
- 평균 위험도: xx.x  
- 이상 사용자 수: x  
- 이상 이벤트 수: x  
자세한 내용은 report.pdf를 확인하세요.
```

---

### ✅ 8. **메인 파이프라인 통합 (`main.py`)**

1. S3에서 최신 로그 다운로드
2. 정규화(log_collector)
3. 위험 이벤트 분석(log_analyzer)
4. 이상행동 분석
5. 사용자 프로파일링
6. 보고서 PDF 생성
7. Slack 자동 알림

단 한 줄:

```bash
python main.py
```

---

## 📁 프로젝트 구조

```
CloudForensic-ReportSystem/
 ┣ data/
 ┃ ┣ raw_logs/
 ┃ ┣ raw_logs/expanded/
 ┃ ┗ parsed_logs.jsonl
 ┣ out/
 ┃ ┣ alerts.csv
 ┃ ┣ anomalies.csv
 ┃ ┗ event_anomalies.csv
 ┣ reports/
 ┃ ┗ report.pdf
 ┣ rules/
 ┃ ┗ sensitive_apis.json
 ┣ src/
 ┃ ┣ log_collector.py
 ┃ ┣ log_analyzer.py
 ┃ ┣ report_generator.py
 ┃ ┣ s3_downloader.py
 ┃ ┣ alert_sender.py
 ┃ ┗ user_profiler.py
 ┣ main.py
 ┗ config.json
```

---

## 🔧 설정 방법

### 1) Slack 알림 설정 — `config.json`

```json
{
    "enable_slack": true,
    "slack_webhook_url": "https://hooks.slack.com/services/your/webhook/url"
}
```

---

## 🏁 실행

```bash
python main.py
```

---


