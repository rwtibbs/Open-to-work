# Open to Work

**A complete job-search pipeline as a single Claude skill.**

Scan boards, tailor your resume, score it against the ATS, write the cover letter, fill the application, prep for the interview, debrief it, reach out to the recruiter — all tracked in a standing ledger. You stay in the loop; the skill does the legwork.

→ **[opentowork.tools](https://opentowork.tools)**

---

## Quick start

1. Download [`open-to-work.skill`](files/open-to-work.skill)
2. Install it in **Claude Cowork** or **Claude Code** (Settings → Capabilities → Install skill, or drop it in your skills directory)
3. Run `python3 scripts/selfcheck.py` to confirm dependencies
4. Say: *"Start my job search"*

Onboarding handles everything else.

---

## Where it runs

The full system needs **Claude Cowork or Claude Code** — a persistent filesystem (so your library survives between sessions) and a shell (to run the bundled scripts). A plain claude.ai chat can talk strategy but can't save a library or produce real files.

**Dependencies:** Python 3.8+, `python-docx`, LibreOffice (PDF export), and poppler (`pdfinfo`/`pdftotext` — `pypdf` auto-fallback if absent). The job scanner is pure standard library. The **Claude for Chrome extension** powers the logged-in LinkedIn/Wellfound browser pass and application fill/upload; onboarding walks you through it.

---

## What's in the box

```
open-to-work/
├── SKILL.md                              # orchestrator (onboard + run + scan + prep + outreach)
├── scripts/
│   ├── generate_resume.py                # resume markdown → polished one-page .docx
│   ├── export_pdf.py                     # .docx → .pdf via LibreOffice
│   ├── page_count.py                     # page-length guard; prints overflow
│   ├── build_cover_letter.py             # cover-letter markdown → matching .docx
│   ├── job_scanner.py                    # config-driven scanner: broad discovery + watchlist
│   ├── lint_copy.py                      # AI-tell + ATS parse-safety linter
│   └── selfcheck.py                      # verify deps + scanner logic after install/edits
├── references/
│   ├── onboarding-interview.md           # Quick (~5 min) + Thorough (~20 min) question sets
│   ├── profile-template.json
│   ├── base_resume-template.md
│   ├── fact-pack-template.md
│   ├── voice-template.md
│   ├── format-template.json
│   ├── writing-standards.md              # house style: the structural AI tells to avoid
│   ├── cover-letter-playbook.md          # opener hierarchy, anti-staccato, truthfulness rules
│   ├── ats-rubric.md                     # self-contained ATS scorer
│   ├── browser-autofill.md               # Claude-in-Chrome fill/upload procedure
│   ├── interview-prep.md                 # prep kit, mock interview, transcript debrief
│   ├── outreach-playbook.md              # tier-gated recruiter/HM outreach
│   ├── application-tracker.md            # standing pipeline ledger (applications.json)
│   ├── followup-and-negotiation.md       # thank-yous, status nudges, offer negotiation
│   ├── scheduling.md                     # recurring scan setup + unattended run flow
│   ├── scanner_config.template.json
│   └── scanner-scheduled-task.template.md
└── user-library/
    └── NOT_ONBOARDED.md                  # first-run marker; replaced during onboarding
```

---

## How the loop works

### 1. Onboard once

The first time you talk about your job search, it opens with a short overview then kicks off onboarding to build your personal **user-library**. You choose the depth:

- **Quick (~5 min)** — upload your resume; it parses and asks only the gaps.
- **Thorough (~20 min)** — a guided interview for a richer fact pack and sharper voice capture.

You can start from an uploaded resume, a pasted LinkedIn/portfolio, or pure Q&A. It produces your `profile.json`, `base_resume.md`, `fact-pack.md`, `voice.md`, and `format.json`, reads them back to confirm, and you're set.

### 2. Target a role

Paste a job description (full text — a URL alone isn't enough) and say something like *"tailor my resume for this."* It will:

1. Tailor your resume to the role — truthfully, never inventing experience.
2. Build the one-page DOCX and a matching PDF.
3. Run an ATS scoring loop **twice**, implementing only truthful fixes and reporting the gaps it deliberately didn't fake.
4. Write a cover letter in your voice and answer any open-ended application questions, coordinated so your stories don't repeat.
5. Optionally fill and upload the application in your browser, stopping at the final Submit for your review.

### 3. Scan automatically

Set up job scanning during onboarding (or any time). Give it your target roles, levels, locations, comp floor, recency window, role shape, priority domains, and an optional company watchlist.

The scanner does **broad market discovery** across keyless remote-job aggregators (Remotive, RemoteOK, Arbeitnow, Jobicy; Adzuna optional) plus the optional Greenhouse/Lever/Ashby watchlist. It scores in two stages: a cheap card-level pass rules out obvious mismatches; only promising cards get the full JD fetched and re-scored. LinkedIn and Wellfound are covered via a logged-in browser pass (Claude for Chrome extension).

Run on demand or schedule it (default: twice daily). Each scan surfaces a ranked shortlist of **new** matching roles — deduped so nothing repeats — and you can drop any one straight into the tailoring pipeline.

### 4. Stay in the loop after you apply

- **Prep and practice** — when you land an interview, it builds a tailored prep kit and runs a live mock, then debriefs the real interview from a transcript (Meetily recommended) and feeds the lessons back into your library.
- **Reach out** — on strong-fit roles it helps you find the recruiter or hiring manager and drafts a short note in your voice. Tier-gated; never auto-sent.
- **Track everything** — a standing ledger (`user-library/applications.json`) records what you applied to, reached out on, and interviewed for. Ask *"what's still open?"* and get a real answer.

---

## Privacy

All of your personal data — resume, fact pack, voice, contact details, form answers, and job-search history — lives in **your own `user-library/` files**, on your machine. The skill ships with only empty templates and a first-run marker. Your information isn't embedded in the skill and isn't shared by installing or distributing it. Pass the `.skill` file to someone else and they get the machinery; they onboard themselves into their own library.

---

## License

MIT
