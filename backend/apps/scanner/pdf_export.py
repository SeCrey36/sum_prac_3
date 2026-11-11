import os
from io import BytesIO
from typing import List, Dict, Any

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONTS_DIR = os.path.join(os.path.dirname(__file__), "fonts")
REGULAR_FONT_PATH = os.path.join(FONTS_DIR, "arial.ttf")
BOLD_FONT_PATH = os.path.join(FONTS_DIR, "arialbd.ttf")

FONT_NAME = "ArialCustom"
FONT_BOLD_NAME = "ArialCustomBold"

# Register fonts once
try:
    if os.path.exists(REGULAR_FONT_PATH):
        pdfmetrics.registerFont(TTFont(FONT_NAME, REGULAR_FONT_PATH))
    else:
        FONT_NAME = "Helvetica"

    if os.path.exists(BOLD_FONT_PATH):
        pdfmetrics.registerFont(TTFont(FONT_BOLD_NAME, BOLD_FONT_PATH))
    else:
        FONT_BOLD_NAME = FONT_NAME
except Exception:
    FONT_NAME = "Helvetica"
    FONT_BOLD_NAME = "Helvetica-Bold"


def generate_pdf_report(
    original_filename: str,
    file_size_bytes: int,
    uploaded_at_str: str,
    risk_level: str,
    risk_summary: str,
    findings: List[Dict[str, Any]],
    file_deleted: bool = False,
) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName=FONT_BOLD_NAME,
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#111827"),
        alignment=1,  # Center
        spaceAfter=6,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName=FONT_NAME,
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#6B7280"),
        alignment=1,
        spaceAfter=16,
    )

    h2_style = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontName=FONT_BOLD_NAME,
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#111827"),
        spaceBefore=12,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName=FONT_NAME,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#111827"),
    )

    badge_style = ParagraphStyle(
        "BadgeText",
        parent=styles["Normal"],
        fontName=FONT_BOLD_NAME,
        fontSize=12,
        leading=16,
        textColor=colors.white,
        alignment=1,
    )

    risk_text_style = ParagraphStyle(
        "RiskDesc",
        parent=styles["Normal"],
        fontName=FONT_NAME,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#374151"),
    )

    elements = []

    # Title
    elements.append(Paragraph("ОТЧЁТ ОБ АУДИТЕ ПЕРСОНАЛЬНЫХ ДАННЫХ", title_style))
    elements.append(Paragraph("Автоматизированный анализ документа на соответствие 152-ФЗ", subtitle_style))
    elements.append(Spacer(1, 10))

    # Meta Table
    size_kb = round(file_size_bytes / 1024, 1)
    file_status = "Удалён сервером (политика конфиденциальности)" if file_deleted else "Временное хранение (до 1 ч)"

    meta_data = [
        [Paragraph(f"<b>Имя файла:</b> {original_filename}", body_style),
         Paragraph(f"<b>Размер:</b> {size_kb} КБ", body_style)],
        [Paragraph(f"<b>Дата проверки:</b> {uploaded_at_str}", body_style),
         Paragraph(f"<b>Статус файла:</b> {file_status}", body_style)],
    ]
    meta_table = Table(meta_data, colWidths=[260, 260])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F9FAFB")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#E5E7EB")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 14))

    # Risk block
    risk_colors = {
        "LOW": (colors.HexColor("#10B981"), "НИЗКИЙ РИСК"),
        "MEDIUM": (colors.HexColor("#F59E0B"), "СРЕДНИЙ РИСК"),
        "CRITICAL": (colors.HexColor("#EF4444"), "КРИТИЧЕСКИЙ РИСК"),
    }
    bg_color, label = risk_colors.get(risk_level, (colors.HexColor("#6B7280"), risk_level))

    risk_box_data = [
        [
            Paragraph(f"<b>{label}</b>", badge_style),
            Paragraph(risk_summary, risk_text_style),
        ]
    ]
    risk_table = Table(risk_box_data, colWidths=[130, 390])
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), bg_color),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor("#F3F4F6")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#E5E7EB")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(risk_table)
    elements.append(Spacer(1, 14))

    # Findings section
    elements.append(Paragraph(f"Обнаруженные персональные данные ({len(findings)} записей)", h2_style))

    if findings:
        table_headers = [
            Paragraph("<b>№</b>", body_style),
            Paragraph("<b>Тип данных</b>", body_style),
            Paragraph("<b>Стр.</b>", body_style),
            Paragraph("<b>Фрагмент (маскированный)</b>", body_style),
            Paragraph("<b>Контекст</b>", body_style),
        ]
        table_rows = [table_headers]

        for i, item in enumerate(findings, start=1):
            table_rows.append([
                Paragraph(str(i), body_style),
                Paragraph(item.get("type_name", item.get("pii_type", "")), body_style),
                Paragraph(str(item.get("page_number", "-")), body_style),
                Paragraph(f"<code>{item.get('masked_value', '')}</code>", body_style),
                Paragraph(item.get("context", "")[:80] + ("..." if len(item.get("context", "")) > 80 else ""), body_style),
            ])

        findings_table = Table(table_rows, colWidths=[24, 130, 32, 140, 194])
        findings_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E5E7EB")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#D1D5DB")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(findings_table)
    else:
        elements.append(Paragraph("В проверенном документе персональных данных не обнаружено.", body_style))

    elements.append(Spacer(1, 20))
    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["Italic"],
        fontName=FONT_NAME,
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#9CA3AF"),
        alignment=1,
    )
    elements.append(Paragraph(
        "Отчёт сформирован сервисом аудита документов. Обработка произведена без постоянного сохранения содержимого на сервере.",
        footer_style
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
