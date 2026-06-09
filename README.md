# Career Tailor AI

A Cowork skill that tailors your resume and cover letter for any job description — without fabricating experience.

## What it does

Runs a 6-phase agentic workflow on every job application:

1. **JD Analyzer** — extracts required skills, ATS keywords, responsibilities
2. **Gap Analyzer** — maps your resume against the JD; identifies matches and honest gaps
3. **Resume Optimizer** — reorders, reframes, and rewrites bullets using only what's in your resume
4. **Authenticity Review** — removes AI-sounding language; ensures every claim is interview-defensible
5. **ATS Scoring** — simulates ATS evaluation, targets 80–85 score
6. **Cover Letter Generator** — personalizes your template for the specific role and company

**Output:** 1-page resume PDF + 1-page cover letter PDF + ATS analysis report

## Hard rules

- Never adds skills, tools, certifications, or experience not in your master resume
- Never invents metrics or achievements
- Gaps are reported honestly in the ATS report

## Usage

1. Install `career-tailor-ai.skill` in Claude Cowork (Settings → Capabilities → Skills)
2. On first run, paste your master resume and cover letter template — saved permanently
3. Each subsequent run: paste a job description or URL → get tailored PDFs

## Files

```
SKILL.md                  — skill instructions (loaded by Claude)
scripts/generate_pdfs.py  — converts optimized resume/cover letter markdown to PDFs
evals/evals.json          — test cases used during skill development
```

## Requirements

- Python 3 + `reportlab` (`pip install reportlab`)
- Claude Cowork (desktop app)
