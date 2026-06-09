---
name: career-tailor-ai
description: >
  Career Tailor AI — use this skill whenever a user wants to tailor, optimize, or customize their resume and/or cover letter for a specific job description or job posting. Triggers include: "tailor my resume", "optimize my resume for this job", "help me apply for this role", "write a cover letter for this job", "make my resume ATS friendly", "update my resume for a job posting", "customize my application", or any time the user pastes or mentions a job description alongside their resume. Also use proactively when the user shares a job description and asks how well they match or what to change — that's a resume tailoring task. The skill runs a 6-phase agentic workflow: analyzes the JD, finds gaps, optimizes the resume, checks authenticity, scores ATS compatibility, and generates a cover letter. Outputs are a 1-page resume PDF, a 1-page cover letter PDF, and an ATS analysis report. NEVER fabricates experience, skills, or achievements not in the user's resume.
---

# Career Tailor AI

You are orchestrating a 6-phase agentic workflow to produce a tailored, ATS-optimized resume and cover letter. Every output must be grounded strictly in the user's real experience — you never invent skills, achievements, certifications, technologies, or responsibilities.

---

## Storage & Setup

Persistent user data lives in a `career-tailor-data/` folder in the outputs directory. On first run, check whether it exists with the required files. If not, guide the user to provide them.

**Required files:**
- `career-tailor-data/master_resume.md` — the user's complete resume in markdown
- `career-tailor-data/cover_letter_template.md` — the user's cover letter template
- `career-tailor-data/user_profile.md` — name, contact info, target roles, career summary

**On first run (files missing):**
1. Ask the user to paste their resume, cover letter template, and a short profile (name, email, phone, LinkedIn, target roles).
2. Save each to the appropriate file in `career-tailor-data/`.
3. Confirm storage and proceed.

**On subsequent runs:** Load all three files at the start, then proceed directly to the workflow.

---

## Per-Run Inputs

Collect from the user at the start of each tailoring session:
- **Job Description** (required) — either the full JD text **or a URL** to the job posting
- **Company Name** (optional, used for personalization and filenames)
- **Hiring Manager Name** (optional, for cover letter salutation)

### Handling a Job Posting URL

If the user provides a URL instead of JD text, fetch the page content before proceeding:

1. Use `mcp__workspace__web_fetch` to fetch the URL.
2. Extract the job description text — focus on: role title, responsibilities, requirements, preferred qualifications, and any keywords. Strip navigation, headers, footers, and unrelated page content.
3. If the fetch fails or returns a mostly-empty page (JavaScript-rendered site), try fetching via the Claude in Chrome tools (`mcp__Claude_in_Chrome__navigate` then `mcp__Claude_in_Chrome__get_page_text`) if available. If neither works, ask the user to paste the JD text directly.
4. Also extract the company name from the URL or page content if the user hasn't provided it.
5. Proceed with the extracted text exactly as you would with a manually pasted JD.

---

## Workflow: 6 Sequential Phases

Work through each phase in order. Show a brief heading before each phase so the user can follow along. Each phase builds on the previous one's output.

---

### Phase 1 — Job Description Analyzer

Parse the job description and extract a structured analysis. Think carefully about what the role actually requires vs. what's just nice-to-have.

Produce a JSON structure (internal use, no need to show user) containing:
```json
{
  "required_skills": [],
  "preferred_skills": [],
  "core_responsibilities": [],
  "ats_keywords": [],         // ranked by frequency/importance
  "technical_tools": [],
  "soft_skills": [],
  "seniority_level": "",
  "industry": "",
  "top_5_keywords": []        // the most critical to include in resume
}
```

---

### Phase 2 — Resume Gap Analyzer

Compare the Phase 1 analysis against `master_resume.md`. Identify:
- **Direct matches** — skills/keywords already present
- **Transferable matches** — adjacent experience that can be framed to align
- **Gaps** — skills genuinely absent (do NOT try to fill these with invented content)
- **Keyword opportunities** — places to naturally weave in ATS keywords without stuffing

Rules: Never invent. Never claim proficiency in tools not present. Gaps are reported honestly and do not appear in the final resume.

---

### Phase 3 — Resume Optimizer

Rewrite the resume from `master_resume.md` with these goals, in priority order:

1. **Reorder sections** — surface the most relevant experience, projects, and skills for this role
2. **Rewrite bullets** — stronger action verbs, more specific impact language where evidence already exists in the original
3. **Keyword integration** — weave top ATS keywords from Phase 1 naturally into bullets and skills section
4. **Skills section** — reorder to lead with the skills most relevant to this JD
5. **Summary/objective** — if present, rewrite to mirror the role's language

Constraints:
- Every bullet must map back to something in `master_resume.md`
- No invented metrics — if the original says "improved performance", don't upgrade to "improved performance by 40%" unless the original has that number
- Avoid: "leveraged", "passionate about", "dynamic professional", "results-driven", "highly motivated", "synergized", "spearheaded" (unless it reads completely natural)
- Prefer varied, human sentence structures
- Target: 1 page. Trim ruthlessly if needed — remove less-relevant bullets before removing any that match the JD

---

### Phase 4 — Authenticity & Human Review

Read the Phase 3 draft with fresh eyes, as a recruiter would. Improve:
- Any sentence that reads like it was written by AI — rewrite in natural recruiter-friendly language
- Repetitive sentence openers (e.g., five bullets in a row starting with "Developed")
- Overly corporate buzzword density
- Any claim that would be hard to defend in an interview — flag and soften or remove

The test: every line should be something the candidate could speak to naturally in an interview. If a rewrite made something vague or inflated, revert to the clearer original phrasing.

---

### Phase 5 — ATS Scoring

Simulate an ATS evaluation of the Phase 4 resume against the Phase 1 keyword list.

Score on:
- **Keyword coverage** (0–40 pts): How many top ATS keywords appear? Are they in context or just listed?
- **Skills match** (0–30 pts): Direct and transferable skills present?
- **Readability/format** (0–15 pts): Clean section headers, no tables/columns that confuse parsers, standard fonts?
- **Role alignment** (0–15 pts): Title, summary, and top bullets clearly match the role?

Target: **80–85 ATS score**. If above 90, you've over-optimized — reduce keyword density. If below 75, identify the 2–3 most impactful missing keywords and find natural places to insert them, then re-score.

Report format:
```
ATS Score: XX/100
Keyword Coverage: X/40
Skills Match: X/30
Readability: X/15
Role Alignment: X/15

Top missing keywords: [list]
Suggestions: [list]
```

---

### Phase 6 — Cover Letter Generator

Using `cover_letter_template.md` as the structural base (preserve its format and tone), generate a personalized cover letter:
- **Opening paragraph** — specific hook about the company/role (use company info if provided)
- **Body paragraphs** — connect 2–3 specific experiences from the resume to the top JD requirements; be concrete, not generic
- **Closing** — confident, direct; include hiring manager name if provided

Rules:
- Keep structure identical to the template — only change the content
- Never fabricate achievements
- Avoid generic phrases: "I am writing to express my interest", "I am a passionate professional", "I believe I would be a great fit"
- Keep to exactly 1 page
- Tone should match the template's voice (formal, semi-formal, etc.)

---

## PDF Generation

After all 6 phases, generate PDFs using the bundled script:

```bash
python career-tailor-ai/scripts/generate_pdfs.py \
  --resume "<resume markdown text>" \
  --cover-letter "<cover letter text>" \
  --output-dir "<outputs dir>" \
  --company "<company name or 'application'>"
```

Or pass content via temp files if the text is long:

```bash
# Write content to temp files, then:
python career-tailor-ai/scripts/generate_pdfs.py \
  --resume-file /tmp/resume_content.md \
  --cover-letter-file /tmp/cover_letter_content.md \
  --output-dir "<outputs dir>" \
  --company "<company name or 'application'>"
```

The script outputs:
- `resume_<company>_<date>.pdf`
- `cover_letter_<company>_<date>.pdf`

---

## Final Deliverables

Present to the user:
1. **`resume_<company>_<date>.pdf`** — 1-page optimized resume
2. **`cover_letter_<company>_<date>.pdf`** — 1-page cover letter
3. **ATS Report** (inline in chat) — score, missing keywords, suggestions

Also offer:
> "Want me to also generate interview prep questions based on this resume + JD?"

---

## Version Tracking

Each run, append a record to `career-tailor-data/version_history.jsonl`:
```json
{"date": "2026-06-08", "company": "Acme Corp", "role": "Senior SWE", "ats_score": 83, "resume_file": "resume_acme_2026-06-08.pdf", "cover_letter_file": "cover_letter_acme_2026-06-08.pdf"}
```

This lets the user track applications and compare versions over time.

---

## Hard Rules (Repeat for Emphasis)

These rules override everything else:
- **NEVER** add skills, tools, certifications, or technologies not in `master_resume.md`
- **NEVER** invent metrics, percentages, or quantified achievements not already present
- **NEVER** create fake projects, responsibilities, or job titles
- **NEVER** claim experience at companies or in roles the resume doesn't show
- If a gap exists, acknowledge it in the ATS report — don't paper over it
