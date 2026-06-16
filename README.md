# Job Application Kit

A complete, self-contained job-search pipeline as a single installable Claude
skill. It onboards you once, then handles the whole loop for any role you target:

**scan job boards → shortlist → tailor your resume → ATS-score it twice → write a
cover letter in your voice → answer the application questions → fill & upload the
application in the browser → prep you for the interview → debrief it afterward →
draft outreach to the recruiter — all tracked in a standing pipeline ledger.**

Everything personal lives in *your* files — nothing about any specific person is
baked into the skill. Install it, onboard yourself, and it's yours.

## What's in the box

```
open-to-work/
├── SKILL.md                      # the orchestrator (onboard + run + scan + prep + outreach)
├── README.md
├── scripts/
│   ├── generate_resume.py        # resume markdown -> polished one-page .docx
│   ├── export_pdf.py             # .docx -> .pdf via LibreOffice (faithful)
│   ├── page_count.py             # page-length guard (configurable); prints overflow
│   ├── build_cover_letter.py     # cover-letter markdown -> matching .docx
│   ├── job_scanner.py            # config-driven scanner: broad discovery + watchlist
│   ├── lint_copy.py              # advisory AI-tell + ATS parse-safety linter
│   └── selfcheck.py              # verify deps + scanner logic after install/edits
├── references/
│   ├── onboarding-interview.md   # Quick (~5 min) + Thorough (~20 min) questions
│   ├── profile-template.json
│   ├── base_resume-template.md
│   ├── fact-pack-template.md
│   ├── voice-template.md
│   ├── format-template.json
│   ├── writing-standards.md      # house style: the structural AI tells to avoid
│   ├── cover-letter-playbook.md  # opener hierarchy, anti-staccato, truthfulness
│   ├── ats-rubric.md             # self-contained ATS scorer
│   ├── browser-autofill.md       # Claude-in-Chrome fill/upload procedure
│   ├── interview-prep.md         # prep kit, mock interview, transcript debrief
│   ├── outreach-playbook.md      # tier-gated recruiter/HM outreach
│   ├── application-tracker.md    # the standing pipeline ledger (applications.json)
│   ├── followup-and-negotiation.md  # thank-yous, status nudges, offer negotiation
│   ├── scheduling.md             # recurring scan setup + unattended run flow
│   ├── scanner_config.template.json
│   └── scanner-scheduled-task.template.md  # ready-to-install scheduled-task prompt
└── user-library/
    └── NOT_ONBOARDED.md          # first-run marker (replaced during onboarding)
```

## Install

Install the `.skill` file like any Claude skill (Cowork/Claude Code: drop it in via
Settings → Capabilities, or your skills directory). Once installed, just start
talking about your job search and it triggers. After installing (or editing any
script), run `python3 scripts/selfcheck.py` to confirm dependencies and core logic.

**Where it runs:** the full system needs **Claude Cowork or Claude Code** — a
persistent filesystem (so your library survives between sessions) and a shell (to run
the bundled scripts). A plain claude.ai chat can talk through strategy but can't save a
library or build real files.

**Dependencies:** Python 3.8+, the `python-docx` package (resume/cover-letter
builders), LibreOffice (PDF export), and **poppler** (`pdfinfo`/`pdftotext`, for the
page-length check and ATS text extraction — `pip install pypdf` is an automatic
fallback if poppler is absent). The scanner itself is pure standard library. The
**Claude for Chrome extension** powers the logged-in LinkedIn/Wellfound browser pass in
your scans and the application fill/upload — install it if you want those (onboarding
prompts you to).

## How onboarding works

The first time you use it, it opens with a short overview — what the skill does,
what you'll provide, what's optional/configurable, and where your data lives — then
kicks off onboarding to build your personal **user-library**. (Any later "onboard me
/ set me up" jumps straight to the setup.) You choose the depth:

- **Quick (~5 min)** — upload a resume; it parses it and asks only the gaps.
- **Thorough (~20 min)** — a guided interview for a richer fact pack and a sharper
  voice capture. Good if you don't have a resume handy.

You can start from an uploaded resume, a pasted LinkedIn/portfolio, or pure Q&A. It
produces your `profile.json`, `base_resume.md`, `fact-pack.md`, `voice.md`, and
`format.json`, reads it all back to confirm, and then you're set. The
`NOT_ONBOARDED.md` marker is deleted so it won't re-onboard you.

## How to run an application

Paste a job description (full text — a URL alone isn't enough) and say something like
"tailor my resume for this." It will:

1. Tailor your resume to the role — truthfully, never inventing experience.
2. Build the one-page DOCX and a matching PDF.
3. Run an ATS scoring loop **twice**, implementing only the truthful fixes and
   reporting the gaps it deliberately *didn't* fake.
4. Write a cover letter in your voice and answer any open-ended application
   questions (inline, copy-paste-ready), coordinated so your stories don't repeat.
5. Optionally fill and upload the application in your browser — stopping at the
   final Submit for you to review.

## Job scanning + scheduling

During onboarding (or any time) you can set up automated job scanning. Give it your
target roles, levels, locations, comp floor, recency window, the role *shape* and
priority/hard-no domains you care about, and (optionally) a watchlist of companies.
It does **broad market discovery** across keyless remote-job aggregators (Remotive,
RemoteOK, Arbeitnow, Jobicy; Adzuna optional) — surfacing roles at companies you
never listed — plus the optional Greenhouse / Lever / Ashby watchlist.

It scores in **two stages**: a cheap card-level pass rules out the obvious
mismatches, and only the promising cards (above a configurable `deep_read_threshold`)
get the full JD fetched and re-scored. The domain lists are non-exhaustive (an
unlisted domain stays neutral; only your hard-no list drops a role), a recency gate
drops stale postings, and the deep read includes a live-status check and a search for
the canonical ATS posting when a role was found on an upload-blocking aggregator.

You can run a scan on demand or schedule it (default: twice daily, ~8am/4pm local).
Each scan surfaces a ranked shortlist of **new** matching roles — deduped so nothing
repeats — and you can drop any one of them straight into the tailoring pipeline.
Onboarding actively walks you through setting up the config, the schedule, and the
Chrome extension — these aren't buried options.

**LinkedIn and Wellfound are included via a logged-in browser pass** (using the Claude
for Chrome extension + your signed-in session), since they have no key-free API. With
the extension set up, your scheduled scans cover them alongside the keyless
aggregators; without it, those two are skipped and the scan falls back to the API
sources. Indeed is the most bot-protected and isn't covered by default. See
`references/scheduling.md` and `references/scanner-scheduled-task.template.md` for the
full run flow and the ready-to-install scheduled-task prompt.

## Interview prep, outreach & a pipeline you can query

The loop doesn't stop at "applied":

- **Prep & practice** — when you land an interview, it builds a tailored prep kit
  (strengths, gaps, stories mapped to likely questions) and runs a live mock, then
  **debriefs the real interview** from a transcript (Meetily recommended, but any
  accurate transcript works) and feeds the lessons back into your library.
- **Reach out** — on genuinely strong-fit roles it finds the recruiter or hiring
  manager, helps you get their contact, and drafts a short note in your voice (email or
  LinkedIn). Tier-gated and never auto-sent.
- **Track everything** — a standing ledger (`user-library/applications.json`) records
  what you applied to, reached out on, and interviewed for, so you can ask "what's still
  open?" or "who do I owe a follow-up?" and get a real answer. Thank-yous, status
  nudges, and offer-negotiation briefs come from the same place.

Everything written follows one house style (`writing-standards.md`) so it reads like you
wrote it — and the never-fabricate rule holds across all of it.

## Privacy

All of your personal data — resume, fact pack, voice, contact details, form answers,
and job-search history — lives in **your own `user-library/` files** in your working
folder, on your machine. The skill itself ships with only empty templates and a
first-run marker. Your information isn't embedded in the skill and isn't shared by
installing or distributing it. If you pass the `.skill` file to someone else, they
get the machinery, not your data — they onboard themselves into their own library.
