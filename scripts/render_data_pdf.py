from html import escape
import argparse
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    Image,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/data-provenance-th.md"
OUTPUT = ROOT / "docs/data-provenance-th.pdf"
FONT = "/Library/Fonts/Arial Unicode.ttf"
pdfmetrics.registerFont(TTFont("Thai", FONT))

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="ThaiBody", parent=styles["BodyText"], fontName="Thai", fontSize=9.4, leading=14, spaceAfter=5))
styles.add(ParagraphStyle(name="ThaiH1", parent=styles["Title"], fontName="Thai", fontSize=22, leading=28, textColor=colors.HexColor("#123f35"), alignment=TA_CENTER, spaceAfter=10))
styles.add(ParagraphStyle(name="ThaiH2", parent=styles["Heading2"], fontName="Thai", fontSize=14, leading=19, textColor=colors.HexColor("#17614f"), spaceBefore=12, spaceAfter=6))
styles.add(ParagraphStyle(name="ThaiH3", parent=styles["Heading3"], fontName="Thai", fontSize=11, leading=15, textColor=colors.HexColor("#245f52"), spaceBefore=8, spaceAfter=4))
styles.add(ParagraphStyle(name="ThaiSmall", parent=styles["BodyText"], fontName="Thai", fontSize=7.2, leading=10))
styles.add(ParagraphStyle(name="ThaiCode", parent=styles["Code"], fontName="Thai", fontSize=8, leading=11, backColor=colors.HexColor("#f2f6f4"), borderColor=colors.HexColor("#2e806c"), borderWidth=1, borderPadding=5))

def inline(value):
    value = escape(value, quote=False)
    value = re.sub(r"\[([^]]+)\]\(([^)]+)\)", r'<link href="\2" color="#126b5a">\1</link>', value)
    value = re.sub(r"`([^`]+)`", r"<font name='Thai'>\1</font>", value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)
    return value

def make_table(lines):
    rows = []
    for line in lines:
        if re.match(r"^\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?$", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        rows.append([Paragraph(inline(c), styles["ThaiSmall"]) for c in cells])
    if not rows:
        return None
    widths = [((180 / len(rows[0])) * mm) for _ in rows[0]]
    table = Table(rows, colWidths=widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dceee8")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#123f35")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#a8c0b8")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return table

def build(source: Path = SOURCE, output: Path = OUTPUT, title: str = "Airport TimeTwin Data Provenance"):
    story = []
    lines = source.read_text().splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        image_match = re.match(r"!\[([^]]*)\]\(([^)]+)\)", line)
        if image_match:
            image_path = (source.parent / image_match.group(2)).resolve()
            if image_path.exists():
                img = Image(str(image_path))
                img._restrictSize(175 * mm, 92 * mm)
                story.append(img)
                story.append(Paragraph(inline(image_match.group(1)), styles["ThaiSmall"]))
                story.append(Spacer(1, 3 * mm))
            i += 1
            continue
        if line.startswith("```"):
            code = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code.append(lines[i]); i += 1
            story.append(Preformatted("\n".join(code), styles["ThaiCode"]))
            story.append(Spacer(1, 3 * mm)); i += 1; continue
        if line.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].startswith("|"):
                table_lines.append(lines[i]); i += 1
            story.append(make_table(table_lines)); story.append(Spacer(1, 3 * mm)); continue
        if line.startswith("# "):
            story.append(Paragraph(inline(line[2:]), styles["ThaiH1"]))
        elif line.startswith("## "):
            story.append(Paragraph(inline(line[3:]), styles["ThaiH2"]))
        elif line.startswith("### "):
            story.append(Paragraph(inline(line[4:]), styles["ThaiH3"]))
        elif line == "---":
            story.append(HRFlowable(width="100%", color=colors.HexColor("#a8c0b8")))
        elif line.startswith("- ") or re.match(r"^\d+\. ", line):
            items = []
            ordered = line[0].isdigit()
            while i < len(lines) and (lines[i].startswith("- ") or re.match(r"^\d+\. ", lines[i])):
                item = re.sub(r"^(?:- |\d+\. )", "", lines[i])
                items.append(ListItem(Paragraph(inline(item), styles["ThaiBody"]), leftIndent=8))
                i += 1
            story.append(ListFlowable(items, bulletType="1" if ordered else "bullet", leftIndent=14))
            continue
        elif line.startswith("> "):
            story.append(Paragraph("<i>" + inline(line[2:]) + "</i>", styles["ThaiBody"]))
        else:
            story.append(Paragraph(inline(line), styles["ThaiBody"]))
        i += 1
    def footer(canvas, doc):
        canvas.saveState(); canvas.setFont("Thai", 7); canvas.setFillColor(colors.HexColor("#55736a"))
        canvas.drawString(16 * mm, 9 * mm, title)
        canvas.drawRightString(194 * mm, 9 * mm, f"หน้า {doc.page}"); canvas.restoreState()
    doc = SimpleDocTemplate(str(output), pagesize=A4, rightMargin=16*mm, leftMargin=16*mm, topMargin=15*mm, bottomMargin=16*mm, title=title)
    doc.build(story, onFirstPage=footer, onLaterPages=footer)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--title", default="Airport TimeTwin · Data provenance and demo methodology")
    args = parser.parse_args()
    build(args.source, args.output, args.title)
    print(args.output)
