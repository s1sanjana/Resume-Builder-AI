#!/usr/bin/env python3
"""
Career Tailor AI — PDF Generator
Converts resume and cover letter markdown to clean, 1-page PDFs.
Uses reportlab for reliable PDF generation without system dependencies.
"""

import argparse
import os
import sys
import re
from datetime import date

def install_deps():
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab", "--break-system-packages", "-q"])

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, KeepInFrame
    from reportlab.platypus.flowables import BalancedColumns
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
except ImportError:
    install_deps()
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, KeepInFrame
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY


# ── Color palette ────────────────────────────────────────────────────────────
DARK       = colors.HexColor("#1a1a2e")
ACCENT     = colors.HexColor("#16213e")
MID        = colors.HexColor("#4a4a6a")
LIGHT_GREY = colors.HexColor("#f0f0f5")
RULE_COLOR = colors.HexColor("#c0c0d0")


def make_styles():
    styles = getSampleStyleSheet()

    base = dict(fontName="Helvetica", fontSize=9.5, leading=13, textColor=DARK,
                spaceAfter=0, spaceBefore=0)

    return {
        "name": ParagraphStyle("name", fontName="Helvetica-Bold", fontSize=18,
                                leading=20, textColor=DARK, spaceAfter=2),
        "contact": ParagraphStyle("contact", fontName="Helvetica", fontSize=8.5,
                                   leading=11, textColor=MID, spaceAfter=0),
        "section_header": ParagraphStyle("section_header", fontName="Helvetica-Bold",
                                          fontSize=9, leading=12, textColor=ACCENT,
                                          spaceBefore=6, spaceAfter=1, textTransform="uppercase",
                                          letterSpacing=1.0),
        "job_title": ParagraphStyle("job_title", fontName="Helvetica-Bold", fontSize=9.5,
                                     leading=12, textColor=DARK, spaceBefore=4, spaceAfter=0),
        "job_meta": ParagraphStyle("job_meta", fontName="Helvetica-Oblique", fontSize=8.5,
                                    leading=11, textColor=MID, spaceAfter=1),
        "bullet": ParagraphStyle("bullet", fontName="Helvetica", fontSize=9, leading=12,
                                  textColor=DARK, leftIndent=10, firstLineIndent=-6, spaceAfter=1),
        "body": ParagraphStyle("body", fontName="Helvetica", fontSize=9, leading=12,
                                textColor=DARK, spaceAfter=2),
        "skills_label": ParagraphStyle("skills_label", fontName="Helvetica-Bold", fontSize=9,
                                        leading=12, textColor=DARK, spaceAfter=1),
        "skills_value": ParagraphStyle("skills_value", fontName="Helvetica", fontSize=9,
                                        leading=12, textColor=DARK, spaceAfter=2),
        "cl_body": ParagraphStyle("cl_body", fontName="Helvetica", fontSize=10, leading=15,
                                   textColor=DARK, spaceAfter=8, alignment=TA_JUSTIFY),
        "cl_name": ParagraphStyle("cl_name", fontName="Helvetica-Bold", fontSize=16,
                                   leading=18, textColor=DARK, spaceAfter=2),
        "cl_contact": ParagraphStyle("cl_contact", fontName="Helvetica", fontSize=9,
                                      leading=12, textColor=MID, spaceAfter=0),
        "cl_date": ParagraphStyle("cl_date", fontName="Helvetica", fontSize=10,
                                   leading=13, textColor=DARK, spaceAfter=6),
    }


def rule(width="100%", thickness=0.5, color=RULE_COLOR, space_before=2, space_after=3):
    return [Spacer(1, space_before), HRFlowable(width=width, thickness=thickness,
            color=color, spaceAfter=space_after)]


def parse_markdown_resume(text: str, styles: dict) -> list:
    """Convert markdown resume text into reportlab flowables."""
    flowables = []
    lines = text.strip().splitlines()
    i = 0

    while i < len(lines):
        line = lines[i].rstrip()

        # H1 — name
        if line.startswith("# "):
            flowables.append(Paragraph(line[2:].strip(), styles["name"]))
            i += 1
            # collect contact line(s) right after the name
            contact_parts = []
            while i < len(lines) and not lines[i].startswith("#") and lines[i].strip():
                raw = lines[i].strip()
                # strip markdown links: [text](url) → text
                raw = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', raw)
                contact_parts.append(raw)
                i += 1
            if contact_parts:
                flowables.append(Paragraph(" · ".join(contact_parts), styles["contact"]))
            flowables.extend(rule())

        # H2 — section header
        elif line.startswith("## "):
            flowables.append(Paragraph(line[3:].strip(), styles["section_header"]))
            flowables.extend(rule(thickness=0.3, space_before=0, space_after=2))
            i += 1

        # H3 — job title / project title
        elif line.startswith("### "):
            title = line[4:].strip()
            # peek ahead for italic meta line
            meta = ""
            if i + 1 < len(lines) and lines[i + 1].strip().startswith("*"):
                i += 1
                meta = lines[i].strip().strip("*").strip("_")
            flowables.append(Paragraph(title, styles["job_title"]))
            if meta:
                flowables.append(Paragraph(meta, styles["job_meta"]))
            i += 1

        # Bullet point
        elif line.startswith("- ") or line.startswith("* "):
            bullet_text = "• " + line[2:].strip()
            # bold inline: **text** → <b>text</b>
            bullet_text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', bullet_text)
            flowables.append(Paragraph(bullet_text, styles["bullet"]))
            i += 1

        # Bold label: **Label:** value  (skills lines)
        elif re.match(r'^\*\*[^*]+\*\*:', line):
            m = re.match(r'^\*\*([^*]+)\*\*:\s*(.*)', line)
            if m:
                label, value = m.group(1), m.group(2)
                flowables.append(Paragraph(f"<b>{label}:</b> {value}", styles["skills_value"]))
            i += 1

        # Horizontal rule
        elif re.match(r'^---+$', line):
            flowables.extend(rule())
            i += 1

        # Non-empty body line
        elif line.strip():
            body = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', line)
            flowables.append(Paragraph(body, styles["body"]))
            i += 1

        else:
            i += 1

    return flowables


def parse_markdown_cover_letter(text: str, styles: dict) -> list:
    """Convert cover letter markdown to reportlab flowables."""
    flowables = []
    lines = text.strip().splitlines()
    i = 0

    while i < len(lines):
        line = lines[i].rstrip()

        if line.startswith("# "):
            flowables.append(Paragraph(line[2:].strip(), styles["cl_name"]))
            i += 1
            # contact lines
            while i < len(lines) and lines[i].strip() and not lines[i].startswith("#"):
                raw = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', lines[i].strip())
                flowables.append(Paragraph(raw, styles["cl_contact"]))
                i += 1
            flowables.extend(rule())

        elif re.match(r'^---+$', line):
            flowables.extend(rule())
            i += 1

        elif line.strip():
            body = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', line.strip())
            flowables.append(Paragraph(body, styles["cl_body"]))
            i += 1
        else:
            i += 1

    return flowables


def build_pdf(flowables: list, output_path: str, doc_type: str = "resume"):
    """Render flowables to a single-page PDF."""
    margins = 0.55 * inch

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=margins,
        rightMargin=margins,
        topMargin=0.45 * inch,
        bottomMargin=0.45 * inch,
        title=f"Career Tailor AI — {doc_type.title()}",
    )

    # Wrap in KeepInFrame to enforce single page
    page_w = letter[0] - 2 * margins
    page_h = letter[1] - 0.9 * inch  # top + bottom margins
    frame = KeepInFrame(page_w, page_h, flowables, mode="shrink")

    doc.build([frame])
    print(f"✓ Saved {doc_type}: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate resume and cover letter PDFs")
    parser.add_argument("--resume", type=str, help="Resume markdown text")
    parser.add_argument("--resume-file", type=str, help="Path to resume markdown file")
    parser.add_argument("--cover-letter", type=str, help="Cover letter markdown text")
    parser.add_argument("--cover-letter-file", type=str, help="Path to cover letter markdown file")
    parser.add_argument("--output-dir", type=str, default=".", help="Output directory")
    parser.add_argument("--company", type=str, default="application", help="Company name for filename")
    args = parser.parse_args()

    # Load content
    resume_text = args.resume
    if not resume_text and args.resume_file:
        with open(args.resume_file, "r") as f:
            resume_text = f.read()

    cl_text = args.cover_letter
    if not cl_text and args.cover_letter_file:
        with open(args.cover_letter_file, "r") as f:
            cl_text = f.read()

    if not resume_text and not cl_text:
        print("Error: provide --resume/--resume-file and/or --cover-letter/--cover-letter-file")
        sys.exit(1)

    os.makedirs(args.output_dir, exist_ok=True)
    today = date.today().strftime("%Y-%m-%d")
    company_slug = re.sub(r'[^a-z0-9]+', '_', args.company.lower()).strip('_')

    styles = make_styles()

    if resume_text:
        out = os.path.join(args.output_dir, f"resume_{company_slug}_{today}.pdf")
        flowables = parse_markdown_resume(resume_text, styles)
        build_pdf(flowables, out, "resume")

    if cl_text:
        out = os.path.join(args.output_dir, f"cover_letter_{company_slug}_{today}.pdf")
        flowables = parse_markdown_cover_letter(cl_text, styles)
        build_pdf(flowables, out, "cover letter")


if __name__ == "__main__":
    main()
