#!/usr/bin/env python3
"""
Career Tailor AI — PDF Generator
Matches the resume template design:
  - Name: centered, dark navy, bold caps
  - Section headers: blue, bold, ALL CAPS, followed by thin rule
  - Skills: two-column table with blue bold labels on left
  - Project titles: bold name | italic blue tech stack (no date)
  - Job/leadership titles: bold left, italic date right-aligned
  - Bullets: filled circles
"""

import argparse
import os
import sys
import re
from datetime import date


def install_deps():
    import subprocess
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "reportlab", "--break-system-packages", "-q"]
    )


try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer,
        HRFlowable, KeepInFrame, Table, TableStyle,
    )
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
except ImportError:
    install_deps()
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer,
        HRFlowable, KeepInFrame, Table, TableStyle,
    )
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY


# ── Palette (matched to template) ────────────────────────────────────────────
NAME_COLOR = colors.HexColor("#1a3560")   # dark navy — name
ACCENT     = colors.HexColor("#2e6db4")   # medium blue — section headers, skill labels, tech stack
TEXT       = colors.HexColor("#1a1a1a")   # near-black — body
META       = colors.HexColor("#444444")   # dark grey — dates, meta
RULE       = colors.HexColor("#b0b8c8")   # light blue-grey — divider lines

ACCENT_HEX = "#2e6db4"
META_HEX   = "#444444"


# ── Styles ────────────────────────────────────────────────────────────────────
def make_styles():
    return {
        # Header
        "name": ParagraphStyle("name", fontName="Helvetica-Bold", fontSize=20,
                               leading=24, textColor=NAME_COLOR,
                               alignment=TA_CENTER, spaceAfter=2),
        "contact": ParagraphStyle("contact", fontName="Helvetica", fontSize=9,
                                  leading=12, textColor=TEXT,
                                  alignment=TA_CENTER, spaceAfter=4),
        # Section
        "section": ParagraphStyle("section", fontName="Helvetica-Bold", fontSize=9.5,
                                  leading=12, textColor=ACCENT,
                                  spaceBefore=5, spaceAfter=1),
        # Skills table cells
        "skill_label": ParagraphStyle("skill_label", fontName="Helvetica-Bold", fontSize=9,
                                      leading=13, textColor=ACCENT, spaceAfter=0),
        "skill_value": ParagraphStyle("skill_value", fontName="Helvetica", fontSize=9,
                                      leading=13, textColor=TEXT, spaceAfter=0),
        # Entry titles (jobs / leadership) — left col
        "entry_title": ParagraphStyle("entry_title", fontName="Helvetica-Bold", fontSize=9.5,
                                      leading=12, textColor=TEXT, spaceBefore=4, spaceAfter=0),
        # Entry date — right col
        "entry_date": ParagraphStyle("entry_date", fontName="Helvetica-Oblique", fontSize=9,
                                     leading=12, textColor=META,
                                     alignment=TA_RIGHT, spaceBefore=4, spaceAfter=0),
        # Project title (no date)
        "proj_title": ParagraphStyle("proj_title", fontName="Helvetica-Bold", fontSize=9.5,
                                     leading=12, textColor=TEXT, spaceBefore=4, spaceAfter=0),
        # Bullet
        "bullet": ParagraphStyle("bullet", fontName="Helvetica", fontSize=9, leading=12.5,
                                 textColor=TEXT, leftIndent=14, firstLineIndent=-8, spaceAfter=1),
        # Generic body (summary, education, etc.)
        "body": ParagraphStyle("body", fontName="Helvetica", fontSize=9, leading=13,
                               textColor=TEXT, spaceAfter=2),
        # Cover letter
        "cl_name": ParagraphStyle("cl_name", fontName="Helvetica-Bold", fontSize=16,
                                  leading=20, textColor=NAME_COLOR,
                                  alignment=TA_CENTER, spaceAfter=2),
        "cl_contact": ParagraphStyle("cl_contact", fontName="Helvetica", fontSize=9,
                                     leading=12, textColor=TEXT,
                                     alignment=TA_CENTER, spaceAfter=0),
        "cl_body": ParagraphStyle("cl_body", fontName="Helvetica", fontSize=10, leading=15,
                                  textColor=TEXT, spaceAfter=8, alignment=TA_JUSTIFY),
    }


# ── Helpers ───────────────────────────────────────────────────────────────────
def hr_line(before=2, after=4, thickness=0.7):
    return [Spacer(1, before),
            HRFlowable(width="100%", thickness=thickness, color=RULE, spaceAfter=after)]


def section_block(title, styles):
    """Blue bold ALL-CAPS header + thin rule."""
    return [Paragraph(title.upper(), styles["section"])] + hr_line(before=1, after=3)


DATE_COL_WIDTH = 1.35 * inch   # fixed date column — fits "Sept 2024 – Apr 2028" at 9pt

def entry_title_row(title, date_str, styles, page_width):
    """Bold title left + italic date right in a two-column table.
    Title column takes all remaining width so long education titles stay on one line."""
    title_col = page_width - DATE_COL_WIDTH
    tbl = Table(
        [[Paragraph(f"<b>{title}</b>", styles["entry_title"]),
          Paragraph(date_str, styles["entry_date"])]],
        colWidths=[title_col, DATE_COL_WIDTH],
    )
    tbl.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    return tbl


def xml_escape(text):
    """Escape XML special characters for ReportLab Paragraph content."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_skills_table(rows, styles, page_width):
    """Two-column skills: blue bold label | value."""
    data = [[Paragraph(xml_escape(lbl), styles["skill_label"]),
             Paragraph(xml_escape(val), styles["skill_value"])]
            for lbl, val in rows]
    tbl = Table(data, colWidths=[page_width * 0.25, page_width * 0.75])
    tbl.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
        ("TOPPADDING",    (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return tbl


def inline_bold(text):
    """Convert **bold** markdown to ReportLab XML bold tags."""
    return re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)


def strip_md_links(text):
    return re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)


# ── Resume parser ─────────────────────────────────────────────────────────────
def parse_markdown_resume(text: str, styles: dict, page_width: float) -> list:
    flowables = []
    lines = text.strip().splitlines()
    i = 0
    skill_rows = []
    in_skills_section = False

    def flush_skills():
        nonlocal skill_rows
        if skill_rows:
            flowables.append(build_skills_table(skill_rows, styles, page_width))
            skill_rows = []

    while i < len(lines):
        line = lines[i].rstrip()

        # ── H1: Candidate name ────────────────────────────────────────────
        if line.startswith("# "):
            flush_skills()
            name = line[2:].strip().upper()
            flowables.append(Paragraph(name, styles["name"]))
            i += 1
            # Contact lines immediately after name
            contact_parts = []
            while i < len(lines) and not lines[i].startswith("#") and lines[i].strip():
                contact_parts.append(strip_md_links(lines[i].strip()))
                i += 1
            if contact_parts:
                flowables.append(Paragraph(" | ".join(contact_parts), styles["contact"]))
            flowables.extend(hr_line(before=3, after=5, thickness=0.9))

        # ── H2: Section header ────────────────────────────────────────────
        elif line.startswith("## "):
            flush_skills()
            section_name = line[3:].strip()
            in_skills_section = any(k in section_name.upper()
                                    for k in ("SKILL", "TOOL", "TECH"))
            flowables.extend(section_block(section_name, styles))
            i += 1

        # ── H3: Entry title (project or job/leadership) ───────────────────
        elif line.startswith("### "):
            flush_skills()
            in_skills_section = False
            title_raw = line[4:].strip()

            # Project pattern: "Title | Tech Stack" — no date
            if " | " in title_raw:
                parts    = title_raw.split(" | ", 1)
                proj_name = parts[0].strip()
                tech      = parts[1].strip()
                combined  = (f'<b>{proj_name}</b>'
                             f'<font color="{ACCENT_HEX}"> | </font>'
                             f'<font color="{ACCENT_HEX}" face="Helvetica-Oblique">{tech}</font>')
                flowables.append(Paragraph(combined, styles["proj_title"]))
                i += 1

            else:
                # Look ahead for an italic date line
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                next_line = lines[j].strip() if j < len(lines) else ""
                is_date = (next_line.startswith("*") and next_line.endswith("*")
                           and not next_line.startswith("**"))

                if is_date:
                    date_str = next_line.strip("*").strip("_")
                    flowables.append(entry_title_row(title_raw, date_str, styles, page_width))
                    i = j + 1
                else:
                    flowables.append(Paragraph(f"<b>{title_raw}</b>", styles["entry_title"]))
                    i += 1

        # ── Standalone italic line (unconsumed date) ──────────────────────
        elif (line.strip().startswith("*") and line.strip().endswith("*")
              and not line.strip().startswith("**")):
            flush_skills()
            meta_text = line.strip().strip("*").strip("_")
            flowables.append(Paragraph(
                f'<font color="{META_HEX}" face="Helvetica-Oblique">{meta_text}</font>',
                styles["body"]))
            i += 1

        # ── Bullet point ──────────────────────────────────────────────────
        elif line.startswith("- ") or line.startswith("* ") or line.startswith("● "):
            flush_skills()
            in_skills_section = False
            content = line[2:].strip()
            content = inline_bold(content)
            flowables.append(Paragraph("• " + content, styles["bullet"]))
            i += 1

        # ── **Label:** value — skills row or bold body ────────────────────
        elif re.match(r'^\*\*[^*]+\*\*:', line):
            m = re.match(r'^\*\*([^*]+)\*\*:\s*(.*)', line)
            if m:
                if in_skills_section:
                    skill_rows.append((m.group(1).strip(), m.group(2).strip()))
                else:
                    flush_skills()
                    flowables.append(Paragraph(
                        f"<b>{m.group(1)}:</b> {m.group(2)}", styles["body"]))
            i += 1

        # ── Horizontal rule ───────────────────────────────────────────────
        elif re.match(r'^---+$', line):
            flush_skills()
            flowables.extend(hr_line())
            i += 1

        # ── Non-empty body text ───────────────────────────────────────────
        elif line.strip():
            flush_skills()
            # Check if the next non-blank line is an italic date — if so,
            # render as a two-column title+date row (handles education entries)
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            next_line = lines[j].strip() if j < len(lines) else ""
            is_date = (next_line.startswith("*") and next_line.endswith("*")
                       and not next_line.startswith("**"))

            if is_date:
                date_str  = next_line.strip("*").strip("_")
                title_str = inline_bold(line.strip())
                flowables.append(entry_title_row(title_str, date_str, styles, page_width))
                i = j + 1
            else:
                flowables.append(Paragraph(inline_bold(line), styles["body"]))
                i += 1

        else:
            i += 1

    flush_skills()
    return flowables


# ── Cover letter parser ───────────────────────────────────────────────────────
def parse_markdown_cover_letter(text: str, styles: dict) -> list:
    flowables = []
    lines = text.strip().splitlines()
    i = 0

    while i < len(lines):
        line = lines[i].rstrip()

        if line.startswith("# "):
            flowables.append(Paragraph(line[2:].strip().upper(), styles["cl_name"]))
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].startswith("#"):
                raw = strip_md_links(lines[i].strip())
                flowables.append(Paragraph(raw, styles["cl_contact"]))
                i += 1
            flowables.extend(hr_line(before=4, after=8, thickness=0.8))

        elif re.match(r'^---+$', line):
            flowables.extend(hr_line())
            i += 1

        elif line.strip():
            flowables.append(Paragraph(inline_bold(line.strip()), styles["cl_body"]))
            i += 1

        else:
            i += 1

    return flowables


# ── PDF builder ───────────────────────────────────────────────────────────────
def build_pdf(flowables: list, output_path: str, doc_type: str = "resume"):
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
    page_w = letter[0] - 2 * margins
    page_h = letter[1] - 0.9 * inch
    frame  = KeepInFrame(page_w, page_h, flowables, mode="shrink")
    doc.build([frame])
    print(f"✓ Saved {doc_type}: {output_path}")


# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Generate resume and cover letter PDFs")
    parser.add_argument("--resume",            type=str, help="Resume markdown text")
    parser.add_argument("--resume-file",       type=str, help="Path to resume markdown file")
    parser.add_argument("--cover-letter",      type=str, help="Cover letter markdown text")
    parser.add_argument("--cover-letter-file", type=str, help="Path to cover letter markdown file")
    parser.add_argument("--output-dir",        type=str, default=".", help="Output directory")
    parser.add_argument("--company",           type=str, default="application", help="Company name")
    args = parser.parse_args()

    resume_text = args.resume
    if not resume_text and args.resume_file:
        with open(args.resume_file) as f:
            resume_text = f.read()

    cl_text = args.cover_letter
    if not cl_text and args.cover_letter_file:
        with open(args.cover_letter_file) as f:
            cl_text = f.read()

    if not resume_text and not cl_text:
        print("Error: provide --resume/--resume-file and/or --cover-letter/--cover-letter-file")
        sys.exit(1)

    os.makedirs(args.output_dir, exist_ok=True)
    today = date.today().strftime("%Y-%m-%d")
    slug  = re.sub(r'[^a-z0-9]+', '_', args.company.lower()).strip('_')

    styles = make_styles()
    margins = 0.55 * inch
    page_w  = letter[0] - 2 * margins

    if resume_text:
        out = os.path.join(args.output_dir, f"resume_{slug}_{today}.pdf")
        build_pdf(parse_markdown_resume(resume_text, styles, page_w), out, "resume")

    if cl_text:
        out = os.path.join(args.output_dir, f"cover_letter_{slug}_{today}.pdf")
        build_pdf(parse_markdown_cover_letter(cl_text, styles), out, "cover letter")


if __name__ == "__main__":
    main()
