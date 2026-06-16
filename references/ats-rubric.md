# ATS Scoring Rubric (self-contained)

The RUN pipeline scores the tailored resume against the JD twice. This rubric is
the scorer — no external skill needed. Apply it honestly: a higher score earned by
a lie is worthless and will collapse in an interview. The scorer's only job is to
find gaps; closing them (truthfully) happens back in the tailoring step.

## Inputs

Both must be present: the resume text (extract with `pdftotext -layout <pdf> -`)
and the **full JD text** (not just a URL).

## Step 1 — Classify the JD before scoring (required)

Before reading the resume, classify the JD's sections by intent and state it
explicitly. Skipping this is a scoring error.

| Section type | Signal phrases | How to treat it |
|---|---|---|
| **Role description** | "You will…", "This role owns…", "Your work will…" | Scope context only. Do NOT score gaps against it. |
| **Qualifications** | "Requirements", "Who you are", "You have…", "We're looking for…" | The actual hiring bar. Score against this. |
| **Integrated JD** (no clear split) | Mixed/absent headers | Extract implied qualifications (years, domain, skills), then apply the role-native rule below. |

**Role-native knowledge rule:** never penalize the candidate for lacking
proprietary, platform-specific, or internal knowledge that could only be acquired
by working in this exact seat (a company's internal tool names, their specific
implementation of a common technology, product areas unique to that org). Those
belong to the role description, not the hiring bar — exclude them from gap scoring.

State before scoring: **Qualifications section identified**, **Excluded terms**
(role-description-only items that must not appear in the gap list), and **Scoring
basis** (one sentence on what you're scoring against).

## Step 2 — Score, 1–100, weighted

Be calibrated. Most resumes land 40–75. A 90+ means near-perfect keyword and
experience match; sub-40 means meaningful gaps.

| Category | Weight | What to evaluate |
|---|---|---|
| **Keyword Match** | 35% | Hard skills, tools, technologies, role-specific terms from the JD that appear in the resume |
| **Title & Level Alignment** | 20% | How closely the candidate's current/recent title and seniority match the posted role |
| **Experience Relevance** | 40% | Depth of relevant experience — whether past work aligns with the actual JD responsibilities, not just years |
| **Education & Credentials** | 5% | Degree/certs/credentials the JD calls out |

## Output format

```
## ATS Score: [X]/100

### Keyword Match — [X]/35
[2–3 sentences on coverage]
Present: [matched terms]
Missing: [unmatched JD terms]
Near-misses: [resume uses a synonym/related phrase instead of the exact JD term]

### Title & Level Alignment — [X]/20
[1–2 sentences; note any parsing risks]

### Experience Relevance — [X]/40
[2–3 sentences; name specific JD responsibilities not reflected in the resume]

### Education & Credentials — [X]/5
[1 sentence]

### Summary
[3–4 sentences: overall read, the 1–2 highest-impact gaps, and an honest ceiling —
"with these addressed, this resume could realistically reach X/100"]

### Gap List
Numbered, priority order by score impact. Gaps only — no fixes. Each item names the
JD term/requirement that's missing or underrepresented, where in the resume it's
absent, and whether it's a HARD gap (experience doesn't exist) or a SOFT gap
(experience exists but isn't surfaced).
1. **[gap name]** — Missing from [location]. [Hard/Soft] gap.
```

## Behavioral rules

- **Be an ATS, not a cheerleader.** Score on signal matching, not writing quality.
- **Penalize missing keywords even when the experience clearly implies them.** ATS
  matches strings, not inferences. Near-misses get partial credit, not full.
- **Don't inflate.** A 70 should feel like a real 70.
- **No fixes here.** This step identifies gaps; the tailoring step closes the soft
  ones (truthfully) and records the hard ones for the report.
- After the score, add a 2–3 sentence **Human Reviewer Take** noting where the ATS
  score and a human's impression are likely to diverge (common for senior
  candidates whose strengths don't reduce to keywords).

## How the RUN loop uses this

For each of two rounds: score → triage each gap through the truthfulness filter
(soft gap → reword/surface it truthfully; **hard gap → do NOT fix; record it for
the report**) → apply edits to `resume_<company>.md` → rebuild docx/pdf and
re-check one page. Round 2 scores what Round 1 produced. Capture both scores and
the specific changes for the final report, and list every recommendation
deliberately skipped because it would require fabricating experience — that list is
a feature, not an apology.
