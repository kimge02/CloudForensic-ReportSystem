☁️ CloudForensic-ReportSystem

AWS CloudTrail 로그 기반 클라우드 포렌식 자동 리포트 시스템


🧭 프로젝트 개요

이 프로젝트는 AWS CloudTrail 로그를 자동 분석하여
보안 이벤트 탐지 및 PDF 리포트 자동 생성을 수행하는 시스템입니다.

CloudTrail 로그에서 사용자 활동을 수집

위험도 점수 기반으로 이상행동 탐지

자동 PDF 리포트 생성 및 시각화 포함

관리자는 복잡한 로그 분석 없이 클릭 한 번으로 보안 요약 리포트를 받을 수 있습니다.

⚙️ 실행 방법
# 1️⃣ 로그 확장 (샘플 로그 8 → 25개 복제)
python src/log_mutator.py

# 2️⃣ 로그 정규화
python src/log_collector.py

# 3️⃣ 탐지 분석
python src/log_analyzer.py

# 4️⃣ PDF 리포트 생성 (그래프 포함)
python src/report_generator.py

🧾 V2 업데이트 내역 (2025.11.01)
🚀 개요

V2 버전에서는 로그 데이터 다양화 및 PDF 내 시각화 기능이 새롭게 추가되었습니다.
기존 CloudTrail 로그 기반 분석에 더해,
이제 서비스별 이벤트 분포를 그래프 형태로 자동 생성하여 PDF에 포함합니다.

📊 주요 변경 사항
구분	파일명	변경 내용	비고
신규	src/log_mutator.py	CloudTrail 샘플 로그 자동 복제 및 다변화	데이터 확장
수정	src/log_collector.py	확장 로그 포함 전체 정규화 처리	8개 → 25개 이상
수정	src/report_generator.py	Matplotlib 그래프 생성 + PDF 삽입	시각화 기능 완성
🖼️ PDF 리포트 예시
항목	설명
총 이벤트 수	수집된 로그 개수 자동 계산
평균 위험 점수	탐지된 이벤트의 평균 Risk Score
Top 5 위험 이벤트	가장 위험한 이벤트 5개 자동 정렬
서비스별 그래프	EC2, IAM, CloudTrail 등 서비스별 비율 시각화




