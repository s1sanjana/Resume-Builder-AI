# Interview Prep Subskill

This subskill is triggered from the main Career Tailor AI workflow after the resume and cover letter have been generated. It creates a personalized interview prep sheet based on the user's **actual resume** and the **specific JD** they applied for.

Do not run this subskill standalone — it requires the tailored resume and JD from the main workflow to be available in context.

---

## What This Produces

Three things, compiled into one clean document:

1. **Technical Questions** — based on the JD requirements and the skills in the user's resume
2. **Behavioural Questions** — based on the user's real experience (projects, jobs, leadership roles), using the STAR format
3. **Questions to Ask the Interviewer** — smart, role-specific questions the candidate can ask at the end

Output: a single PDF saved as `interview_prep_<company>_<date>.pdf`

---

## Phase A — Technical Questions

Generate 5–8 technical interview questions based on:
- The required and preferred skills from the JD (Phase 1 output from the main workflow)
- The technical tools and skills present in the user's resume

**For each question, provide:**
- The question itself (written as an interviewer would ask it)
- A strong sample answer — specific and concrete, referencing the user's actual experience where possible
- What the interviewer is testing with this question (1 line)

**Example format:**
```
Q: Walk me through how you would approach cleaning a dataset with missing values in Python.

Sample answer: I'd start by understanding the extent of the missingness using df.isnull().sum() to see which columns are affected and how many rows. Then I'd decide on a strategy per column — for numerical columns I typically use median imputation if the data is skewed, or mean for normally distributed data. For categorical columns, I'd either use the most frequent value or create an 'Unknown' category depending on context. I'd avoid dropping rows unless missingness is random and less than 5%. In my Shopify project, I used this exact approach when cleaning transaction log data with about 8% null values in the shipping_address field.

What's being tested: Data wrangling instincts, knowledge of pandas, and whether you think through the "why" before the "how".
```

Keep answers grounded in the user's real resume. Don't fabricate project details — if the user's resume doesn't have a relevant example, write a solid general answer instead.

---

## Phase B — Behavioural Questions

Generate 5–7 behavioural questions based on:
- The soft skills and role requirements from the JD
- The user's actual experience (job titles, projects, leadership roles, team sizes — all from their resume)

**Pre-fill a STAR-format answer for each question using the user's real experience:**
- **Situation** — pull from a relevant role or project in their resume
- **Task** — what they were responsible for
- **Action** — what they specifically did (use their bullet points as source material)
- **Result** — use any metrics already in their resume; if none exist, use a qualitative outcome

**Show the user the pre-filled answer** and tell them they can edit it before their interview.

**Example format:**
```
Q: Tell me about a time you had to manage a project with a tight deadline.

Your STAR answer (edit as needed):

Situation: During my role as Events Director at [Organization], we had 3 weeks to plan and execute a [event type] for 200+ attendees after a previous vendor cancelled.

Task: I was responsible for coordinating all logistics — venue, speakers, marketing, and volunteer coordination — while keeping the team aligned.

Action: I broke the project into daily milestones, held 15-minute standups each morning, delegated tasks based on each volunteer's strengths, and personally handled the venue and speaker outreach to unblock the critical path.

Result: The event ran on time, received [outcome from resume — e.g. "positive feedback from 90% of attendees"] and we came in under budget.

Tip: If you have a specific number (attendance, budget, feedback score), add it — it makes the answer memorable.
```

---

## Phase C — Questions to Ask the Interviewer

Generate 5 smart, role-specific questions the candidate can ask at the end of their interview. These should be tailored to the company, role, and JD — not generic.

**Good questions to include (adapt to the role):**
- What does success look like in the first 90 days for this role?
- What are the biggest challenges someone in this position typically faces in the first few months?
- How does the team currently measure [relevant metric from JD — e.g. "data quality" / "design impact" / "code quality"]?
- What tools and workflows does the day-to-day work involve?
- What's the team structure — who would I be working most closely with?

Format them as natural, conversational questions the candidate would actually say out loud.

---

## PDF Generation

After generating all three phases, compile everything into one markdown document and convert to PDF:

```bash
python career-tailor-ai/scripts/generate_pdfs.py \
  --resume-file /tmp/interview_prep_content.md \
  --output-dir "<outputs dir>" \
  --company "<company name>"
```

The output file will be named: `resume_<company>_<date>.pdf`

> Note: The PDF generator uses `--resume-file` for any single-column document. The interview prep content renders cleanly as a structured text document using the same pipeline.

Name the output file manually after generation: `interview_prep_<company>_<date>.pdf`

---

## Delivery

Present the PDF to the user and say:

> *"Here's your interview prep sheet for [Company]. It includes [N] technical questions with sample answers, [N] behavioural questions pre-filled with your real experience, and 5 questions to ask the interviewer. Edit the STAR answers before your interview to make them feel natural in your own voice."*

---

## Hard Rules

- **NEVER** invent projects, job titles, companies, or outcomes not in the user's resume
- STAR answers must be built from real entries in the resume — if a matching experience doesn't exist, write a general strong answer and label it as such
- Technical sample answers may use general best-practice knowledge, but should reference the user's actual stack/tools wherever possible
- Do not include questions the resume clearly cannot support answering (e.g., don't ask about managing a team if the user has never managed anyone)
