from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
import pandas as pd
import matplotlib.pyplot as plt
import os
from pathlib import Path

ALERTS  = Path(r"E:\고은폴더\대학교\정보보안\3학년\캡스톤디자인(3-2)\CloudForensic-ReportSystem\out\alerts.csv")
REPORTS = Path(r"E:\고은폴더\대학교\정보보안\3학년\캡스톤디자인(3-2)\CloudForensic-ReportSystem\reports\report.pdf")

def generate_report():
    df = pd.read_csv(ALERTS)
    cols = ["time", "actor", "service", "action", "result", "risk_score", "reason"]
    df = df[cols]

    REPORTS.parent.mkdir(parents=True, exist_ok=True)

    # (한글 폰트 필요 없으면 생략 가능)
    pdfmetrics.registerFont(UnicodeCIDFont('HYSMyeongJo-Medium'))

    # ▶ 가로방향 + 여백 축소로 폭 확보
    doc = SimpleDocTemplate(
        str(REPORTS),
        pagesize=landscape(A4),
        leftMargin=18, rightMargin=18, topMargin=24, bottomMargin=22
    )

    styles = getSampleStyleSheet()
    styles["Normal"].fontName = 'HYSMyeongJo-Medium'
    styles["Title"].fontName  = 'HYSMyeongJo-Medium'
    styles["Normal"].fontSize = 9
    styles["Normal"].leading  = 11

    wrap_style = ParagraphStyle(
        'wrap',
        parent=styles['Normal'],
        wordWrap='CJK',
        fontName='HYSMyeongJo-Medium',
        fontSize=9,
        leading=11
    )

    elements = []

    # 제목
    elements.append(Paragraph("<b>Cloud Forensics Automatic Report (V2)</b>", styles['Title']))
    elements.append(Spacer(1, 14))

    # 요약
    elements.append(Paragraph("&#9632; Event Summary", styles['Heading2']))
    elements.append(Paragraph(f"Total Events: {len(df)}", styles['Normal']))
    elements.append(Paragraph(f"Average Risk Score: {df['risk_score'].mean():.1f}", styles['Normal']))
    elements.append(Spacer(1, 8))

    # ========================
    # ✅ V2 추가: 서비스별 이벤트 그래프
    # ========================
    try:
        service_counts = df["service"].value_counts()
        plt.figure(figsize=(6,4))
        service_counts.plot(kind='bar', color='skyblue', title='Event Distribution by Service')
        plt.xlabel('Service')
        plt.ylabel('Count')
        plt.tight_layout()

        # 🔧 절대 경로 기반으로 out 폴더 지정
        chart_path = Path(__file__).resolve().parent.parent / "out" / "service_chart.png"
        chart_path.parent.mkdir(parents=True, exist_ok=True)

        plt.savefig(chart_path)
        plt.close()

        elements.append(Paragraph("&#9632; Service-wise Event Distribution", styles['Heading2']))
        elements.append(Spacer(1, 8))
        if chart_path.exists():
            elements.append(Image(str(chart_path), width=420, height=260))
            elements.append(Spacer(1, 12))
    except Exception as e:
        elements.append(Paragraph(f"(그래프 생성 중 오류 발생: {e})", styles['Normal']))
        elements.append(Spacer(1, 12))


    # 상위 5개 위험 이벤트
    top = df.sort_values("risk_score", ascending=False).head(5)
    header = ["Time", "Actor", "Service", "Action", "Result", "Risk", "Reason"]
    rows = []
    for _, r in top.iterrows():
        rows.append([
            Paragraph(str(r["time"]),    wrap_style),
            Paragraph(str(r["actor"]),   wrap_style),
            Paragraph(str(r["service"]), wrap_style),
            Paragraph(str(r["action"]),  wrap_style),
            Paragraph(str(r["result"]),  wrap_style),
            int(r["risk_score"]),
            Paragraph(str(r["reason"]),  wrap_style)
        ])

    data = [header] + rows
    col_widths = [120, 70, 70, 120, 90, 40, 320]

    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR',  (0,0), (-1,0), colors.whitesmoke),
        ('GRID',       (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN',     (0,0), (-1,-1), 'TOP'),
        ('ALIGN',      (0,0), (-3,-1), 'CENTER'),
        ('ALIGN',      (-2,1), (-2,-1), 'RIGHT'),
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


