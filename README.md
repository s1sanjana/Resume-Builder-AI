# Resume Builder AI

An AI-powered skill that tailors your resume and cover letter to any job posting — ATS-optimized, fully personalized, and built entirely from your real experience.

---

## What It Does

You give it a job description (or a URL). It:

1. Analyzes what the role actually needs
2. Finds the gaps and matches in your resume
3. Rewrites your resume to lead with the most relevant experience
4. Checks that every line sounds human, not AI-written
5. Scores it against ATS systems (targets 80–85 out of 100)
6. Writes a tailored cover letter in your voice
7. Asks if you want interview prep questions too

**Outputs:** 1-page resume PDF + 1-page cover letter PDF + ATS report

---

## Which Platform Are You Using?

This skill works on both **Claude.ai** and **Cowork**. Here's what's different:

| | Cowork (Desktop App) | Claude.ai (Web / Mobile) |
|---|---|---|
| **Your resume saved?** | Yes — saved permanently to files | No — paste it once per conversation |
| **Remembers you next time?** | Yes — loads your profile automatically | No — starts fresh each conversation |
| **Version history?** | Yes — logs every application | No |
| **All tailoring features?** | ✓ | ✓ |

### On Cowork
Your resume, cover letter template, and contact info are saved in a `career-tailor-data/` folder the first time you run the skill. Every time you come back, it loads automatically — you just paste the job description and go.

### On Claude.ai
Nothing is saved between conversations. At the start of each new chat, paste your resume when prompted. All the same tailoring features work exactly the same — you just need to bring your resume with you each time.

> **Tip:** Keep a text file on your computer with your resume and cover letter template. It takes 10 seconds to paste at the start of a session.

---

## Getting Started

### First Time

1. Open a conversation with this skill installed
2. Paste a job description or URL
3. The skill will either:
   - Ask you to paste your resume, **or**
   - Offer to help you build one from scratch
4. Follow the prompts — the skill walks you through everything

### Returning Users (Cowork)

1. Just paste a job description or URL — you're done with setup
2. The skill loads your saved resume and goes straight to tailoring
3. Say "update my resume" or "change my cover letter" anytime to update your saved files

### Returning Users (Claude.ai)

1. Paste your resume at the start of the conversation when prompted
2. Then paste the job description
3. The skill takes it from there

---

## Building a Resume from Scratch

If you don't have a resume yet, the skill can build one with you:

1. You tell it what **role or field** you're targeting (e.g., "Data Analyst", "Marketing Co-op")
2. You fill in your real information section by section — education, work experience, skills, projects, leadership
3. The AI writes the resume for you, shaped for your target role
4. Nothing is invented — it works only with what you provide

---

## Interview Prep

After your resume and cover letter are ready, the skill can generate an **Interview Prep Sheet** for the same role:

- **Technical questions** — based on the JD and your actual skills, with sample answers
- **Behavioural questions** — pre-filled STAR answers using your real experience from the resume
- **Questions to ask the interviewer** — smart, role-specific, not generic

Output: `interview_prep_<company>_<date>.pdf`

Just say "yes" when it asks at the end.

---

## Updating Your Saved Profile

On Cowork, say any of the following to update your files:
- "update my resume"
- "change my cover letter"
- "edit my contact info"
- "update my skills"

The skill will show you a menu to pick what to change, then save the new version.

---

## Output Files

Every run produces:
- `resume_<company>_<date>.pdf` — your tailored 1-page resume
- `cover_letter_<company>_<date>.pdf` — your tailored 1-page cover letter
- ATS report in the chat (score, gaps, keyword suggestions)
- `interview_prep_<company>_<date>.pdf` (if requested)

On Cowork, every run is also logged to `career-tailor-data/version_history.jsonl` so you can track every application.

---

## Hard Rules

The skill will never:
- Add skills or tools you don't actually have
- Invent metrics or results you didn't achieve
- Make up projects, job titles, or companies
- Claim experience at places you haven't worked

If there's a gap between your resume and the JD, it's reported honestly in the ATS report — not papered over.

---

## Files in This Skill

```
career-tailor-ai/
├── SKILL.md                          ← Main skill instructions
├── README.md                         ← This file
├── scripts/
│   └── generate_pdfs.py              ← PDF generator (resume + cover letter)
├── subskills/
│   └── interview-prep/
│       └── SKILL.md                  ← Interview prep subskill
└── evals/
    └── evals.json                    ← 3 test cases for benchmarking
```

---

## Built With

- Python + ReportLab (PDF generation)
- Claude (multi-phase agentic workflow)
- pypdf (resume extraction from uploaded PDFs)
