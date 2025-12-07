from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import json

ROOT_DIR = Path(__file__).resolve().parents[1]
ALERTS = ROOT_DIR / "out" / "alerts.csv"
REPORTS = ROOT_DIR / "reports" / "report.pdf"


def generate_report():
    df = pd.read_csv(ALERTS)
    cols = ["time", "actor", "service", "action", "result", "risk_score", "reason"]
    df = df[cols]

    REPORTS.parent.mkdir(parents=True, exist_ok=True)
    pdfmetrics.registerFont(UnicodeCIDFont('HYSMyeongJo-Medium'))

    doc = SimpleDocTemplate(
        str(REPORTS),
        pagesize=landscape(A4),
        leftMargin=18, rightMargin=18, topMargin=24, bottomMargin=22
    )

    styles = getSampleStyleSheet()
    styles["Normal"].fontName = 'HYSMyeongJo-Medium'
    styles["Title"].fontName = 'HYSMyeongJo-Medium'
    styles["Normal"].fontSize = 9
    styles["Normal"].leading = 11

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
    elements.append(Paragraph("<b>Cloud Forensics Automatic Report (V4)</b>", styles['Title']))
    elements.append(Spacer(1, 14))

    # 이벤트 요약
    elements.append(Paragraph("&#9632; Event Summary", styles['Heading2']))
    elements.append(Paragraph(f"Total Events: {len(df)}", styles['Normal']))
    elements.append(Paragraph(f"Average Risk Score: {df['risk_score'].mean():.1f}", styles['Normal']))
    elements.append(Spacer(1, 8))

    # ✅ Anomaly Summary
    elements.append(Paragraph("&#9632; Anomaly Summary", styles['Heading2']))

    anomaly_path = Path(__file__).resolve().parent.parent / "out" / "anomalies.csv"
    if anomaly_path.exists():
        df_user = pd.read_csv(anomaly_path)
        if not df_user.empty:
            summary_users = ", ".join([
                f"{row['actor']} ({row['count']} events)"
                for _, row in df_user.iterrows()
            ])
            elements.append(Paragraph(f"Anomalous Users: {summary_users}", styles['Normal']))
        else:
            elements.append(Paragraph("No anomalous users detected.", styles['Normal']))
    else:
        elements.append(Paragraph("No anomalous users detected.", styles['Normal']))

    event_anom_path = Path(__file__).resolve().parent.parent / "out" / "event_anomalies.csv"
    if event_anom_path.exists():
        df_event = pd.read_csv(event_anom_path)
        if not df_event.empty:
            summary_events = ", ".join(df_event['action'].astype(str).tolist())
            elements.append(Paragraph(f"Anomalous Actions: {summary_events} (High Frequency)", styles['Normal']))
        else:
            elements.append(Paragraph("No anomalous actions detected.", styles['Normal']))
    else:
        elements.append(Paragraph("No anomalous actions detected.", styles['Normal']))

    elements.append(Spacer(1, 12))

    # ✅ User Profiling Summary
    elements.append(Paragraph("&#9632; User Profiling Summary", styles['Heading2']))

    user_summary_path = Path(__file__).resolve().parent.parent / "out" / "user_summary.json"
    if user_summary_path.exists():
        with open(user_summary_path, "r", encoding="utf-8") as f:
            profiles = json.load(f)

        table_data = [["User", "Main Services", "Active Hours", "Total Events"]]
        for user, info in profiles.items():
            main_services = ", ".join(list(info.get("services", {}).keys())[:2]) or "-"
            if info.get("time_distribution"):
                top_hour = max(info["time_distribution"], key=info["time_distribution"].get)
            else:
                top_hour = "-"
            table_data.append([
                user,
                main_services,
                top_hour,
                str(info.get("total_events", 0))
            ])

        t = Table(table_data, colWidths=[100, 150, 100, 80])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#3b5998")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
            ('FONTNAME', (0,0), (-1,-1), 'HYSMyeongJo-Medium'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 12))
    else:
        elements.append(Paragraph("No user profiling data available.", styles['Normal']))
        elements.append(Spacer(1, 12))

    # ✅ 서비스 분포 그래프 (Top N + 라벨 정리)
    try:
        service_counts = df["service"].value_counts()
        top_n = 15
        if len(service_counts) > top_n:
            svc_counts = service_counts.head(top_n)
        else:
            svc_counts = service_counts

        plt.figure(figsize=(7.5, 3.8))
        svc_counts.plot(kind='bar', color='skyblue')
        plt.title(f"Top {len(svc_counts)} Services by Event Count")
        plt.xlabel('Service')
        plt.ylabel('Count')
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        chart_path = Path(__file__).resolve().parent.parent / "out" / "service_chart.png"
        chart_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(chart_path, dpi=150)
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
            Paragraph(str(r["time"]), wrap_style),
            Paragraph(str(r["actor"]), wrap_style),
            Paragraph(str(r["service"]), wrap_style),
            Paragraph(str(r["action"]), wrap_style),
            Paragraph(str(r["result"]), wrap_style),
            int(r["risk_score"]),
            Paragraph(str(r["reason"]), wrap_style)
        ])

    data = [header] + rows
    col_widths = [120, 70, 70, 120, 90, 40, 320]

    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (0,0), (-3,-1), 'CENTER'),
        ('ALIGN', (-2,1), (-2,-1), 'RIGHT'),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 14))
    
    # ✅ 최신 5개 이벤트 추가
    elements.append(Paragraph("&#9632; Recent 5 Events", styles['Heading2']))
    recent = df.sort_values("time", ascending=False).head(5)

    recent_rows = []
    for _, r in recent.iterrows():
        recent_rows.append([
            Paragraph(str(r["time"]), wrap_style),
            Paragraph(str(r["actor"]), wrap_style),
            Paragraph(str(r["service"]), wrap_style),
            Paragraph(str(r["action"]), wrap_style),
            Paragraph(str(r["result"]), wrap_style),
            int(r["risk_score"]),
            Paragraph(str(r["reason"]), wrap_style)
        ])

    recent_data = [header] + recent_rows
    t2 = Table(recent_data, colWidths=col_widths, repeatRows=1)
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2f5496")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (0,0), (-3,-1), 'CENTER'),
        ('ALIGN', (-2,1), (-2,-1), 'RIGHT'),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING',(0,0), (-1,-1), 3),
        ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
    ]))
    elements.append(t2)
    elements.append(Spacer(1, 14))

    elements.append(Paragraph(
        "This report summarizes recent AWS CloudTrail events and highlights potentially risky actions based on defined detection rules.",
        styles['Normal']
    ))

    doc.build(elements)
    print("✅ PDF report generated →", REPORTS)

if __name__ == "__main__":
    generate_report()


