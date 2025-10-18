from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import pandas as pd
from pathlib import Path

ALERTS  = Path(r"E:\고은폴더\대학교\정보보안\3학년\캡스톤디자인(3-2)\CloudForensic-ReportSystem\out\alerts.csv")
REPORTS = Path(r"E:\고은폴더\대학교\정보보안\3학년\캡스톤디자인(3-2)\CloudForensic-ReportSystem\reports\report.pdf")

def generate_report():
    df = pd.read_csv(ALERTS)
    cols = ["time", "actor", "service", "action", "result", "risk_score", "reason"]
    df = df[cols]

    REPORTS.parent.mkdir(parents=True, exist_ok=True)

    # (한글 폰트 필요 없으면 이 줄은 생략해도 됨)
    pdfmetrics.registerFont(UnicodeCIDFont('HYSMyeongJo-Medium'))

    # ▶ 가로방향 + 여백 축소로 폭 확보
    doc = SimpleDocTemplate(
        str(REPORTS),
        pagesize=landscape(A4),
        leftMargin=18, rightMargin=18, topMargin=24, bottomMargin=22
    )

    styles = getSampleStyleSheet()
    # 기본 폰트/크기 통일
    styles["Normal"].fontName = 'HYSMyeongJo-Medium'
    styles["Title"].fontName  = 'HYSMyeongJo-Medium'
    styles["Normal"].fontSize = 9
    styles["Normal"].leading  = 11

    # ▶ 긴 단어도 강제로 줄바꿈되도록 별도 스타일
    wrap_style = ParagraphStyle(
        'wrap',
        parent=styles['Normal'],
        wordWrap='CJK',         # 영문 긴 토큰도 분리해서 줄바꿈
        fontName='HYSMyeongJo-Medium',
        fontSize=9,
        leading=11
    )

    elements = []

    # 제목
    elements.append(Paragraph("<b>Cloud Forensics Automatic Report</b>", styles['Title']))
    elements.append(Spacer(1, 14))

    # 요약
    elements.append(Paragraph("&#9632; Event Summary", styles['Heading2']))
    elements.append(Paragraph(f"Total Events: {len(df)}", styles['Normal']))
    elements.append(Paragraph(f"Average Risk Score: {df['risk_score'].mean():.1f}", styles['Normal']))
    elements.append(Spacer(1, 8))

    # 상위 5개
    top = df.sort_values("risk_score", ascending=False).head(5)

    header = ["Time", "Actor", "Service", "Action", "Result", "Risk", "Reason"]
    rows = []
    for _, r in top.iterrows():
        rows.append([
            Paragraph(str(r["time"]),    wrap_style),
            Paragraph(str(r["actor"]),   wrap_style),
            Paragraph(str(r["service"]), wrap_style),
            Paragraph(str(r["action"]),  wrap_style),   # 긴 액션도 줄바꿈
            Paragraph(str(r["result"]),  wrap_style),   # 에러코드도 줄바꿈
            int(r["risk_score"]),
            Paragraph(str(r["reason"]),  wrap_style)    # 설명 줄바꿈
        ])

    data = [header] + rows

    # ▶ 가로 A4 기준 적당한 폭(필요하면 미세조정)
    col_widths = [120, 70, 70, 120, 90, 40, 320]

    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR',  (0,0), (-1,0), colors.whitesmoke),
        ('GRID',       (0,0), (-1,-1), 0.5, colors.black),

        ('VALIGN',     (0,0), (-1,-1), 'TOP'),
        ('ALIGN',      (0,0), (-3,-1), 'CENTER'),   # Risk 전까지 가운데
        ('ALIGN',      (-2,1), (-2,-1), 'RIGHT'),   # Risk 숫자 오른쪽 정렬

        ('LEFTPADDING',(0,0), (-1,-1), 4),
        ('RIGHTPADDING',(0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING',(0,0), (-1,-1), 3),

        ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
    ]))

    elements.append(t)
    elements.append(Spacer(1, 14))

    elements.append(Paragraph(
        "This report summarizes recent AWS CloudTrail events and highlights potentially risky actions based on defined detection rules.",
        styles['Normal']
    ))

    doc.build(elements)
    print("✅ PDF report generated →", REPORTS)

if __name__ == "__main__":
    generate_report()

