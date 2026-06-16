---
name: open-to-work
description: A complete, self-contained job-search pipeline for ANY user. Onboards once — building resume, fact pack, voice, and styling files from a resume, LinkedIn/portfolio, or quick interview. After that it tailors your resume to any job (truthfully, never fabricating), builds a one-page DOCX + PDF, runs an ATS scoring loop twice, writes a cover letter in your voice, answers application questions, and can fill/upload the form in the browser. Scans job boards on a schedule, preps for interviews (prep kit, mock, debrief), drafts outreach to recruiters or hiring managers, and tracks every application in a standing pipeline ledger with follow-ups, thank-yous, and offer-negotiation help — all feeding one self-improving library. Use for anything job-search related — onboarding, tailoring, cover letters, ATS scoring, applying, scanning, interview prep or debrief, outreach, tracking applications, negotiating offers, or any time they paste a job posting. If there's a chance this is a job-search task, load it.
---

# Open To Work

A full job-search loop in one self-contained skill: **scan → shortlist → tailor →
ATS-score → cover letter + application answers → browser fill/upload.** It works
for *any* user because all personal content lives in the user's own
**`user-library/`** files, which the skill builds during onboarding. Nothing about
any specific person is hardcoded.

There are four entry paths. Pick based on the request and on whether the user is
already onboarded.

- **A. ONBOARDING** — builds the user-library. Runs on first use, or when the user
  says "set me up / onboard me / customize me", or whenever the user-library is
  missing or empty.
- **B. RUN** — the tailor-and-apply pipeline for a specific job. Runs once the
  user-library exists and the user brings a job description (or picks one from a
  scan).
- **C. PREP** — interview preparation for a role the user already applied to (or is
  about to interview for), plus **post-interview debrief** that grades a real interview
  transcript against the prep and feeds the lessons back. Runs when the user says they
  "got an interview", asks to "prep", "practice", or "get ready" — or afterward,
  "debrief that interview / how did I do / review my interview". Best invoked **in the
  same chat where the application was built** — the strategy doc and JD are already in
  context — but works standalone too. See **C. PREP** below.
- **D. OUTREACH** — a direct, personal note (email or LinkedIn) to the recruiter or
  hiring manager, to pull a strong application out of the pile. Runs when the user
  asks to "reach out", "email the hiring manager/recruiter", "find their email", or
  do "cold outreach" — and is **offered proactively at the end of a strong tier-1
  RUN**. Gated to genuinely strong-fit roles. See **D. OUTREACH** below.

## The one rule that overrides everything

**Never fabricate experience.** Every word on the resume, in the cover letter, and
in the application answers must trace to the user's real background as recorded in
their `user-library/fact-pack.md` and `base_resume.md`, or to something they say in
the conversation. Tailoring means *reordering, reframing, and resurfacing* real
experience to match a role — never inventing employers, titles, metrics, skills,
tools, or projects. When the ATS step asks for something the user can't truthfully
claim, you do not add it; you flag it. A higher score earned by a lie is worthless
and collapses in an interview.

## Everything you write follows the house writing standard

All copy this kit produces — résumé bullets, the cover letter, application answers,
outreach notes, prep-kit framing — should read like the user wrote it, not like an AI.
**`references/writing-standards.md`** is the advisory house style: the structural tells
of machine-written prose (anaphora, the "not X, it's Y" false-negative, antithesis,
asyndeton, rhetorical-question transitions, clever comparative endings, staccato
fragments), the positive habits that read as human, and how the standard flexes by
format (a résumé bullet is terse and fragment-normal; a cover letter flows). Hold it in
mind *while drafting* so output adheres by construction — it's a writing habit, not a
post-hoc scoring gate. It never overrides the two rules above it: `voice.md` (the user's
actual voice) wins any conflict, and nothing it suggests excuses fabricating.

## The library is a living system — improve it on every pass

The user-library is not a static file you only read. It's a **self-improving record**
that should get richer and more accurate every time the user works with the kit. The
truthfulness rule and the enrichment habit are two sides of the same coin: you never
*invent* a fact to fill a gap, but you always *capture* a real one when it surfaces.

Across **every mode**, stay alert for material that belongs in the library but isn't
there yet, and for entries that have gone stale:

- a **real metric** the user mentions in chat that a fact-pack bullet was missing;
- a **story** they tell (a conflict, a failure, a 0→1 win) not yet in `fact-pack.md`;
- a **new role, title, or tool** they reference that post-dates the base resume;
- a **recurring hard-gap** worth noting as a standing pattern, or one that's now
  *closed* because they've gained the experience;
- a **refined preference** (a domain they're done with, a role shape they keep
  picking) that should update `scanner_config.json`;
- a **gap with no prepared framing** that prep should add.

**How to capture, safely:**

1. **Only ever record what the user actually stated or confirmed.** Never infer a fact
   into the library to make an answer or score better. A fillable gap (a missing
   number the user knows) → ask. A genuine gap (no domain experience) → leave it
   logged as-is; don't nag about what can't truthfully change.
2. **Batch it at the end, never mid-task.** Don't interrupt a tailoring or prep flow
   to do bookkeeping. Collect candidate additions and handle them in the close-out
   step of each mode.
3. **Respect the enrichment mode** in `profile.json → library_enrichment.mode`:
   - **`confirm`** (default) — list the candidate additions at the end and ask before
     writing anything. Trust comes first; the user should always know what's in their
     library.
   - **`silent`** — auto-write the clearly-true, unambiguous additions, then briefly
     note what you saved ("added that 40% metric to your Zoom entry"). Still pause to
     confirm genuinely ambiguous ones. The never-fabricate rule is absolute in both
     modes.
4. **Keep `base_resume.md` clean.** Enrich it only with confirmed durable facts (a new
   role, a real metric) — never with role-specific tailoring from a single RUN.

## Track the pipeline — one standing ledger

Where the library captures *who the user is*, the **`user-library/applications.json`**
ledger captures *where every role stands* — applied, reached out, interviewing, heard
back — and what's owed next. Every mode updates it in its close-out (RUN logs an
application, OUTREACH logs a note, PREP logs an interview, the debrief logs the outcome),
so the user can ask "what's still open?" or "who do I owe a follow-up?" and get a real
answer. The full schema and the per-mode update rules are in
**`references/application-tracker.md`**. It's the same discipline as the library: agent-
maintained plain JSON, written at close-out (not mid-task), under `library_enrichment.mode`,
recording only what actually happened. Thank-yous, status nudges, and offer-negotiation
briefs hang off it — see **`references/followup-and-negotiation.md`**.

## This skill needs Cowork or Claude Code — not a plain chat

**The full system only works in an environment with a persistent filesystem, a shell,
and (for the power features) scheduled tasks and browser control — i.e. Claude Cowork
or Claude Code.** This is not optional polish; several core pieces silently fail
without it, and a user who runs this in a regular claude.ai/Claude-app chat will get a
convincing conversation with nothing real behind it. Be honest about this up front
rather than letting them discover it after onboarding.

What depends on the environment:

- **The persistent `user-library/`** — onboarding's entire premise is "build it once,
  reuse it forever." A plain chat has no folder that survives between conversations, so
  nothing actually saves; the library evaporates when the chat ends.
- **The bundled Python scripts** — `generate_resume.py` (DOCX), `export_pdf.py`
  (LibreOffice → PDF), `page_count.py`, and `job_scanner.py` need a shell to run. No
  shell, no real DOCX/PDF, no scan.
- **Scheduled scans** need scheduled tasks; **browser fill and the LinkedIn/Wellfound
  pass** need the Claude for Chrome extension on an agentic surface.

In a plain chat the skill can still *talk* — discuss strategy, draft a cover letter or
answers as throwaway text — but it cannot save a library, produce files, score with the
real scripts, scan, or apply. **If you detect you're in an environment without a usable
filesystem/shell, say so before onboarding** (see Step A0) so the user can switch to
Cowork or Claude Code instead of building a library that won't persist. Never narrate
`✓ Saved …` for writes you cannot actually perform.

## Where the user-library lives

The user-library is a `user-library/` folder in the user's **working folder** (the
folder they've connected, or wherever their job-search files live) — NOT inside the
installed skill bundle, which may be read-only. The bundle ships a
`user-library/NOT_ONBOARDED.md` marker as the seed.

**Detect first-run:** at the start of any job task, check for the user's
`user-library/` with filled files (`profile.json`, `base_resume.md`,
`fact-pack.md`, `voice.md`, `format.json`). If it doesn't exist, is empty, or still
contains `NOT_ONBOARDED.md`, go to **ONBOARDING** — starting with the **Step A0
welcome** below. Otherwise go to **RUN** (or the scanner). If you're unsure where
the working folder is, ask the user, or create `user-library/` in the folder you
have access to.

---

# A. ONBOARDING — build the user-library

The point is to capture, once, everything the pipeline needs so every later run is
fast. Be warm and efficient; don't interrogate.

### Step A0 — First-run welcome & overview (always do this first)

**Before anything, confirm the environment can actually run the full system.** The kit
needs a *persistent* filesystem (a library that survives between conversations), a shell
(to run the bundled scripts), and — for the power features — scheduled tasks and browser
control. That means **Claude Cowork or Claude Code**. Be careful here: a regular
claude.ai/Claude-app chat with code execution on has a *temporary* sandbox that looks
writable but is wiped when the conversation ends — so "can I write a file right now?" is
**not** a sufficient test. It would pass in plain chat and then silently lose the whole
library.

So determine the surface honestly:
- If you can tell you're on an **agentic surface with a persistent working folder**
  (Cowork or Claude Code — you have a connected/working directory the user returns to,
  not just an ephemeral sandbox), proceed.
- If you're in a **plain chat** (no persistent working folder across sessions, even if a
  temporary sandbox exists, or you genuinely can't tell), **say so before onboarding** in
  one short message: the full kit — saving a reusable library, generating the DOCX/PDF,
  scanning, and applying — needs **Claude Cowork or Claude Code**. In a regular chat you
  can only talk through strategy or draft throwaway text that won't persist. If unsure
  which surface you're on, ask the user (e.g. "Are you running me in Cowork or Claude
  Code, or a regular Claude chat?") rather than assuming. Offer the lighter help, but
  recommend they re-open the skill in Cowork or Claude Code for the real thing.

**Do not proceed into onboarding and pretend-save a library that will vanish, and never
narrate `✓ Saved …` for a write that won't persist.** Only continue past this point once
you've confirmed a genuinely persistent place to write.

On the **very first run** (the library is missing/empty or `NOT_ONBOARDED.md` is
still present), before asking anything else, give the user a short, friendly
orientation so they know what they're installing and what it will need from them.
Keep it to a tight, skimmable message — a couple of short paragraphs or a compact
list, not a wall of text — covering:

1. **What this skill does.** The full loop, in one breath: it learns your
   background once, then for any job you target it tailors your resume (truthfully —
   never inventing experience), builds a polished one-page DOCX + PDF, ATS-scores it
   twice, writes a cover letter in your voice, answers the application questions,
   can fill and upload the application in your browser (stopping before Submit), and
   can scan job boards on a schedule to surface new matching roles.

2. **What you'll provide (in onboarding, next).** Whatever you have — an uploaded
   resume, a LinkedIn/portfolio link, or just a guided Q&A — plus a few things only
   you know: real metrics and stories, any genuine personal hooks to companies or
   domains, an honest list of gaps, and a writing sample so the voice matches yours.
   This builds your private library (`profile.json`, `base_resume.md`,
   `fact-pack.md`, `voice.md`, `format.json`).

3. **The two power features worth turning on** (don't undersell these — they're
   where most of the leverage is, and they need a little setup, so actively walk the
   user toward them rather than mentioning them in passing):

   - **Automated job scanning on a schedule.** Runs twice a day (or your cadence) and
     surfaces a ranked shortlist of new matching roles — including a **logged-in
     browser pass over LinkedIn and Wellfound** alongside the keyless job-board APIs,
     so you're not limited to boards with a public API. You'll configure your search
     (roles, levels, locations, comp floor, the role *shape* and priority vs. hard-no
     domains, companies to watch) and pick a schedule.
   - **Browser fill & upload.** At the end of an application run, it can open the form
     in your browser, fill the standard fields from your profile, upload your tailored
     résumé + cover letter into the right slots, drop in your drafted answers, and
     **stop before Submit** for you to review.

   Both of these use the **Claude for Chrome extension** (for the browser pass and the
   form fill) and a logged-in browser session. Tell the user this up front so they can
   install it — these aren't afterthoughts, they're the difference between a one-shot
   document generator and a standing job-search engine. You'll prompt them to set both
   up right after the library is built (Step A3).

4. **Where your data lives & privacy.** Everything personal stays in your own
   `user-library/` files in your working folder, on your machine — nothing is baked
   into the skill or shared by installing it.

5. **Dependencies (mention briefly).** Python 3.8+, the `python-docx` package,
   LibreOffice for PDF export, and **poppler** (`pdfinfo`/`pdftotext`, for the page check
   + ATS text extraction — `pypdf` is an auto-fallback); the scanner itself is pure
   standard library. The **Claude for Chrome extension** powers the scheduled browser
   pass and the form fill/upload. Running **`python3 <skill_dir>/scripts/selfcheck.py`**
   verifies dependencies and the scanner's core logic in one shot — do this once after
   install, and after editing any script.

6. **Where it runs (state this plainly).** The full system runs in **Claude Cowork or
   Claude Code** — it needs a persistent place to keep your library and a shell to build
   your documents. In a regular Claude chat it can still talk through strategy and draft
   text, but it can't save your library or generate real files. If they're already in
   Cowork/Code, a quick "you're in the right place" is enough; if not, point them there
   before going further.

Then tell them what happens next and **hand off to Step A1** to begin — e.g. *"Ready
to set up your library? It takes ~5 minutes if you have a resume to upload, or ~20
for a fuller guided version — and once it's built I'll get you set up with automated
scanning and browser apply. Which would you prefer?"* Don't wait for a separate "go"
if they've already asked to be onboarded — flow straight from the overview into the
Quick-vs-Thorough choice.

### Step A1 — Offer Quick vs. Thorough

Ask the user which they'd prefer (use the question tool if available):

- **QUICK (~5 min)** — best if they upload a resume. Parse it, then ask only the
  gaps. Produces a solid library.
- **THOROUGH (~20 min)** — a fuller guided interview. Produces a richer fact pack
  and a more precise voice capture. Best if there's no resume or they want the
  strongest output.

Accept **any** starting material: an uploaded resume file, a pasted LinkedIn or
portfolio URL/text, or pure guided Q&A. Parse whatever they give first and only ask
for what's genuinely missing.

The full question banks for both depths are in
**`references/onboarding-interview.md`** — read it and follow the matching set.

### Step A2 — Produce the library files

Write these into the user's `user-library/` folder. Each has a template in
`references/` — read the template, then fill it from what you gathered. **Strip
nothing into them but the user's real information.**

- **`profile.json`** — name, contact, links, location, work authorization,
  sponsorship need, comp target/floor, and the standard application-form answers.
  Template: `references/profile-template.json`.
- **`base_resume.md`** — their master resume in the exact markdown format
  `generate_resume.py` consumes. Template: `references/base_resume-template.md`.
- **`fact-pack.md`** — roles with real metrics; signature stories (including a
  "deviated from standard process" story, which most applications ask a version
  of); genuine personal hooks/passions; the reusable elevator pitch; recurring
  narrative threads; differentiators; and an honest list of gaps. Template:
  `references/fact-pack-template.md`.
- **`voice.md`** — their writing voice, captured from a writing sample if they have
  one, else from how they answer. Template (with the capture method):
  `references/voice-template.md`.
- **`format.json`** — letterhead/styling tokens (name font, body font, accent
  color, text/muted/rule colors) so the output reflects them, not a fixed design.
  Template: `references/format-template.json`.

### Step A3 — Set up automation & browser apply (strongly recommended — prompt for it)

This is the step that turns the kit from a document generator into a standing
job-search engine. **Don't present it as a throwaway "optional" — actively walk the
user through it** and explain what each piece buys them. Use the question tool if
available. Cover all three of the following; if the user declines any, that's fine —
note it and tell them they can turn it on later by saying "set up scanning" or "set
up browser apply."

**A3a — Build the scanner config.** Gather the config the template asks for and
write it into **`user-library/scanner_config.json`** (template:
`references/scanner_config.template.json`):

- target roles/levels and (optionally) a precise `role_title_regex`;
- acceptable locations + `home_terms`, and whether to require remote-or-home;
- `comp_target`/`comp_floor` (and whether to admit unleveled roles when comp clears
  the floor);
- `signal_keywords` (role-fit themes) and **`shape_signals`** (the role *shape* they
  most want — founding / first-hire / 0→1 / generalist — edit the example list);
- **`tier1_keywords`/`tier2_keywords`** as *example* priority domains (non-exhaustive
  — an unlisted domain stays neutral) and **`exclude_keywords`** as the hard-no list;
- `max_age_days` (recency window), `deep_read_threshold` (default 50), `result_cap`;
- any companies to watch (find and verify their Greenhouse/Lever/Ashby board slugs),
  or leave `watchlist_enabled: false` for discovery-only.

Present these as **user-configurable with sensible defaults** — the tier/keyword and
watchlist lists are examples, not a fixed whitelist. Also write an empty
**`user-library/seen_postings.json`** containing `{"seen": []}` and an empty
**`user-library/applications.json`** containing `{"applications": []}` (the pipeline
ledger — see **`references/application-tracker.md`**).

**A3b — Create the recurring schedule (offer it directly, with a default).** Don't
just mention that scheduling exists — propose it: *"I'll set this to scan twice a day
(~8am and ~4pm your time) and send you a ranked shortlist — sound good, or want a
different cadence?"* Then create the scheduled task using the ready-made prompt in
**`references/scanner-scheduled-task.template.md`** (it already wires up the full
flow: the logged-in LinkedIn/Wellfound browser pass, the keyless API aggregators,
two-stage scoring, the live-status check, and the canonical-ATS lookup). Confirm
their timezone. See the **Scanner & Scheduling** section for the run mechanics.

**A3c — Set up the Claude for Chrome extension (the key enabler — prompt for it).**
Two of the best features depend on it, so explicitly ask the user to install it and
confirm it's connected:

- the **logged-in browser pass** over LinkedIn and Wellfound in the scheduled scan
  (these have no keyless API — the browser pass is the *only* way to include them,
  and it needs the user signed in to those sites in their browser);
- the **browser fill & upload** at the end of an application run.

Walk them to it: *"Install the Claude for Chrome extension and stay signed in to
LinkedIn/Wellfound — that lets me scan those two and fill out applications for you.
Want to do that now?"* If they install it, confirm it connects. If they skip it, note
that LinkedIn/Wellfound won't be scanned and applications will be hand-off-to-them
rather than auto-filled — and that they can add it anytime.

**A3d — Set the library-enrichment mode (quick, one question).** Explain in a line
that the kit keeps their library improving over time — when a real metric, story, or
preference surfaces during a run, it can save it so every future application and prep
gets sharper. Ask how they want that handled and write it to `profile.json →
library_enrichment.mode`:

- **Confirm (default)** — *"I'll ask before saving anything new to your library."*
- **Silent** — *"I'll auto-save clearly-true additions and just tell you what I saved
  (and still check with you on anything ambiguous)."*

Note that either way it only ever saves things they actually said — it never invents
or guesses a fact. Default to **confirm** if they don't care.

### Step A4 — Confirm back, then finish

Read back a concise confirmation: identity, the roles captured, the personal hooks
and the deviated-from-process story, the honest gap list, and a 2–3 sentence
pastiche in the captured voice ("does this sound like you?"). Adjust from their
reaction. Then **delete `user-library/NOT_ONBOARDED.md`** so first-run won't
re-trigger, and summarize what's now live: that they can paste a job description to
tailor an application; whether scanning is scheduled (and when); and whether browser
apply is ready (Chrome extension connected) or still needs the extension. Name
anything they skipped and how to turn it on later.

---

# B. RUN — tailor an application for a specific job

Mirrors a proven pipeline, reading the user's library. **Tailor → build DOCX →
export PDF → enforce one page → ATS loop ×2 → coordinated cover letter +
application answers → report → (optional) browser apply.**

The split is deliberate: the fiddly, error-prone mechanics (building the `.docx`,
PDF conversion, page counting, letterhead) are handled by deterministic scripts so
they come out identical every time. The parts that need judgment — what to
emphasize, which ATS recommendations to act on, whether a claim is true, and the
writing — stay with you.

## Prerequisites

- **Full JD text is required.** If given only a URL, fetch it and confirm you have
  the real responsibilities and qualifications. If the fetch is thin or blocked,
  ask the user to paste the posting. Don't infer the role from a company name.
- **The user-library exists** (else onboard first). Identify the company name from
  the JD — it drives the file names.

## Naming convention

Working files in the user's working folder; `<Name>` = the user's name (no spaces),
`<Company>` = the company TitleCased, `<company>` lowercase:

- Resume working markdown: `resume_<company>.md`
- Cover-letter working markdown: `coverletter_<company>.md`
- Deliverables: `Resume_<Name>_<Company>.docx` / `.pdf`, and
  `CoverLetter_<Name>_<Company>.docx`

## Path note for the scripts

Run scripts from `<skill_dir>/scripts/`. Always pass the user's library files so
nothing is hardcoded:

```
--profile <working>/user-library/profile.json
--format  <working>/user-library/format.json
```

### Step 1 — Strategy + tailor (judgment)

Read `user-library/fact-pack.md` and `user-library/base_resume.md`. Analyze the JD
against them: strongest alignment, real gaps, the positioning angle. Then create
`resume_<company>.md` by **copying `base_resume.md` and editing the copy** — never
edit the base; it must stay clean for the next role.

Tailor through the levers the format supports: the **title** line (highest-impact
single change — match the role's language), the **summary** (lead with the most
relevant angle), **experience** lines (reorder and reword for keyword alignment,
never invent), **skills** (reorder so JD-relevant terms lead), and **projects**
(reorder/lightly reword). Keep the section order and density of the base.

When rewording any prose — the summary especially, and bullet phrasing — follow
**`references/writing-standards.md`**, calibrated to résumé register: bullets are terse
and metric-led (a bullet is allowed to be a fragment), but avoid the résumé-specific
tells — every bullet opening the same way, buzzword padding, and a summary written in
abstract "results-driven professional" AI-speak. Lead with concrete outcomes.

### Step 2 — Build the DOCX (deterministic)

Do not hand-roll a renderer. The whole visual design lives in the script:

```bash
python3 <skill_dir>/scripts/generate_resume.py \
  --input resume_<company>.md \
  --output Resume_<Name>_<Company>.docx \
  --profile <working>/user-library/profile.json \
  --format  <working>/user-library/format.json
```

(Optional company logo: `--logo logos/<company>.png --logo-height 38`.)

### Step 3 — Export the PDF (deterministic)

```bash
python3 <skill_dir>/scripts/export_pdf.py "<working>/Resume_<Name>_<Company>.docx"
```

### Step 4 — Enforce the page target (deterministic check, judgment fix)

```bash
python3 <skill_dir>/scripts/page_count.py "<working>/Resume_<Name>_<Company>.pdf" \
  --max-pages <format.json max_pages, default 1>
```

The target is one page for most roles; pass the user's `format.json` `max_pages` so
longer-format fields (academic CV, federal, senior/technical) aren't force-trimmed to
one. If it reports more than the target, it prints exactly what spilled past it. Trim
the smallest amount that fixes it (tighten the longest wrapped lines first, drop the
least JD-relevant skill terms) in `resume_<company>.md`, then re-run Steps 2→3→4 until
it's within target.

**Optional parse-safety check.** Confirm the PDF extracts cleanly the way an ATS parser
reads it (catches a styled header — e.g. a logo table — scrambling extraction order):
```bash
python3 <skill_dir>/scripts/lint_copy.py parse "<working>/Resume_<Name>_<Company>.pdf" \
  --expect "<Name>" "EXPERIENCE" "SKILLS"
```

### Step 5 — ATS loop, run it TWICE (judgment inside a fixed loop)

Use the self-contained rubric in **`references/ats-rubric.md`**. Run the whole
sub-loop **two full rounds**. Each round: score the current resume against the full
JD → triage each gap through the truthfulness filter (soft gap → reword/surface it
truthfully; **hard gap → do NOT fix; record it for the report**) → apply edits to
`resume_<company>.md` and re-run Steps 2→3→4 so docx, pdf, and the one-page
guarantee stay in sync. Length is fixed at one page — every addition needs a trim.
Capture both scores and the specific changes; Round 2 scores what Round 1 produced.

### Step 6 — Coordinated writing pass: cover letter + application questions

Runs after the resume is locked, drawing on the same role analysis. Cover letter
(a file) and answers to open-ended application questions (delivered in chat) come
from **one coordinated effort** — plan them as a single set so the user's stories
and metrics don't collide across them.

**First, load the user's voice.** Read `user-library/voice.md` and hold it in mind
for every sentence — the whole point is that the letter sounds like them, not like
generic AI cover-letter voice. Then read **`references/cover-letter-playbook.md`**
for the universal craft rules: the opener hierarchy (genuine personal connection if
real > elevator pitch > **never** a thesis cold open), the anti-staccato rhythm
rule (flowing sentences whose clauses connect — clipped fragments-for-effect are
the #1 machine-written tell), naming honest gaps plainly, and the coordinated
evidence-distribution plan across the letter and every answer. Also hold
**`references/writing-standards.md`** — the full house style — so the letter and every
answer avoid the structural AI tells while you draft them, not after.

Ground every claim in `user-library/fact-pack.md`; the never-fabricate rule applies
in full. Scan for open-ended application questions both in the JD text and — if you
have browser access — in the application form itself (most ATS hide essay questions
behind the Apply button). List the questions you found before answering.

Write the letter, save it as `coverletter_<company>.md` (frontmatter + body
paragraphs — see the format in `scripts/build_cover_letter.py`), then render it:

```bash
python3 <skill_dir>/scripts/build_cover_letter.py \
  --input coverletter_<company>.md \
  --output "CoverLetter_<Name>_<Company>.docx" \
  --format  <working>/user-library/format.json \
  --profile <working>/user-library/profile.json
```

This reuses the resume's exact design tokens so the letter is a visual match. Keep
it to one page, ~3–5 tight paragraphs (verify with export_pdf + page_count if
unsure). As an **advisory** pass, you can run `lint_copy.py prose <coverletter_<company>.md>`
to surface the structural AI tells from `writing-standards.md` — judge each flag against
the user's voice; never auto-rewrite a clean, true line. **Output the application answers
directly in chat**, copy-paste-ready — a
markdown heading with the exact question text and the answer beneath — never as a
file. If you found no open-ended questions and couldn't see the form, say so and
remind the user to check the form for hidden questions.

### Step 7 — Report & enrich the library

Give a tight summary: Round 1 score + changes; Round 2 score + changes; final
score; **Deliberately skipped** (every recommendation declined because it would
require fabricating experience — a feature, not an apology); the cover-letter
angle/hook and any honest gap named; which application questions you found (and
whether any may be hidden behind the form); and the three deliverable paths. Then
share the files (via `present_files` if available, else give the paths).

**Then enrich the library** (per "The library is a living system" up top). Look back
over the run for anything true that surfaced and isn't captured yet: a real metric
the user mentioned that a bullet was missing, a story they told in chat, a tool or
role newer than the base resume, or a hard-gap that recurred and is worth logging as
a pattern. Handle it per `profile.json → library_enrichment.mode` — in **confirm**
mode, list the candidates and ask before writing; in **silent** mode, save the
clearly-true ones and note what you saved. Only ever record what the user actually
said. Keep `base_resume.md` clean — durable facts only, never this role's tailoring.

**Update the tracker.** Log this role in `user-library/applications.json` — `status`
(`applied` if submitted, else `prepared`), the deliverable paths, JD/apply links, ATS,
and tier — per **`references/application-tracker.md`**. This is what lets the user later
ask "what's still open?"

**If this is a strong tier-1 fit, offer outreach** (see **D. OUTREACH**). When the
user has a genuine hook to this company/role/domain — a real passion, a near-exact
experience match — a personal note to the recruiter or hiring manager is the natural
next step, and it's strongest right now while everything's in context. Offer to draft
it. On a weaker (tier-2/3) fit with no genuine hook, don't push it — just mention it's
available if they have a personal angle worth playing.

### Step 8 — Apply in the browser (optional)

If the user wants you to fill/upload the application, follow
**`references/browser-autofill.md`**. The essentials:

- **Apply on the canonical ATS, not a profile-only aggregator.** Some sources
  (e.g. Wellfound, LinkedIn Easy Apply) only transmit the user's profile with **no
  file upload** — so the tailored résumé and cover letter can't be attached. When a
  role was found on one of those, first search for the same posting on the company's
  real ATS (Greenhouse / Ashby / Lever) or careers page and apply **there**.
  Profile-only is the fallback when no canonical posting exists.
- Stage the final PDFs into the agent's **writable outputs/working folder** (never a
  read-only dir, Drive/Dropbox cross-origin picker, or the native OS dialog — only
  the outputs→`file_upload` path works), open **each** application in its **own
  tab**, fill standard fields from `profile.json`, upload résumé then cover letter
  (re-find each file input **right before** each upload; verify the filenames landed
  in the correct slots after).
- **Some ATS forms have no cover-letter slot and/or no open-ended essay questions.**
  That's fine — the cover letter is **always a standalone deliverable** the user can
  email or hand to a recruiter, so produce it regardless of whether the form accepts
  it.
- **Leave genuine user-judgment fields for the human** — never auto-answer or
  auto-agree to: relocation-willingness questions, "have you used <product>
  before" questions, terms/consent checkboxes, and the final **Submit**. Fill what
  you can verify from `profile.json`, then **stop before Submit** for the user to
  review — unless they've explicitly authorized you to submit.

---

# C. PREP — get ready for the interview

The loop doesn't end at "applied." When the user lands an interview, this turns the
same context the application was built from — the JD, the positioning strategy, the
fact pack, the honest gap list — into a focused prep kit, and (if they want) runs a
mock interview. The advantage over generic interview advice is **continuity**: the
prep emphasizes the exact strengths you positioned on and defends the exact gaps you
logged, so the user walks in consistent with the application that got them the call.

**Tell the user the best way to invoke this:** from the **same chat where the
application was built**, the JD and strategy are already in context, so prep is
sharpest there. If they're in a fresh chat, that's fine — reconstruct from the
library and ask them to paste the JD (and the company/role if unclear).

## Prerequisites

- **The user-library exists** (else onboard first — though prep can run thin if they
  just want quick practice).
- **The role.** Ideally the original JD + the strategy/tailoring notes from the RUN.
  If this is a fresh chat, ask for the JD and company; pull everything else from
  `fact-pack.md`, `base_resume.md`, and the tailored `resume_<company>.md` if it's
  still around.

## Step P1 — Ask how they want to prep (unless they've said)

If the user hasn't already specified, ask (use the question tool if available) which
they want — they can pick more than one:

- **Prep kit** — a single written brief they can read on their phone before walking
  in. The default; fast and high-value.
- **Mock interview** — an interactive practice loop where you play the interviewer,
  ask questions, and give feedback after each.
- **Both** — build the kit first, then run the mock off it.

Also ask **what round this is** if it's not obvious, because it reshapes everything:
**recruiter screen** (tight pitch, comp positioning, logistics, "why this company"),
**hiring-manager / behavioral** (STAR stories mapped to competencies, gap defense),
**panel / cross-functional** (stakeholder stories, breadth, working style),
**portfolio / case review** (which work to lead with, how to narrate decisions and
tradeoffs — for design/eng/PM), **technical / take-home** (scope, what "good" looks
like, how to talk through tradeoffs), or **final / executive / skip-level** (vision,
trajectory, culture-add, smart questions upward). Default to a hiring-manager
behavioral round if they don't know.

The full prep playbook — what goes in the kit, how to map stories, how to run the
mock loop, and round-by-round emphasis — is in **`references/interview-prep.md`**.
Read it and follow it.

## Step P2 — Build the prep kit (if chosen)

Following `references/interview-prep.md`, assemble a tailored brief with these parts,
drawn from the JD + strategy + library (not generic advice):

1. **Company & role refresher** — what the company does, recent context worth
   knowing, and a plain-language read of what this role actually owns and is measured
   on. If you have web access and the company may have had recent news/funding/launches,
   do a quick check so the user isn't blindsided; otherwise work from the JD.
2. **Your angle** — the positioning the application led with, restated as the through
   line to hold across every answer.
3. **Strengths to emphasize** — the 3–5 strongest alignments between their background
   and this role, each with the proof point ready.
4. **Gaps to manage** — the honest gaps logged during the application (and any new
   ones the JD implies), each with a prepared, non-defensive framing. These are the
   "questions you're afraid of"; rehearse them most.
5. **Story bank, mapped** — their signature stories from `fact-pack.md` mapped to the
   competencies this role screens for, so they know which story answers which likely
   question. Include the "deviated from standard process" story (commonly asked) and
   at least one conflict/failure story.
6. **Predicted questions** — the behavioral and role-specific questions *this posting*
   is most likely to generate, each with a one-line angle (and which mapped story to
   reach for). Not a generic bank — derived from the JD's responsibilities and the
   gaps.
7. **Questions to ask them** — tiered by interviewer (recruiter vs. hiring manager vs.
   skip-level/exec), because asking the right person the right thing reads as
   seniority. Include 1–2 that surface real red flags about the team or role.
8. **Logistics & comp** — their target/floor from `profile.json`, how to deflect an
   early comp question, and any format specifics (who they're meeting, how long).

Deliver the kit as **chat text by default** (readable on a phone), or as a file if
the user asks for something to keep. Keep it tight and scannable — this is a
pre-interview brief, not a dossier.

## Step P3 — Run the mock interview (if chosen)

Run it as a real interactive loop, per `references/interview-prep.md`: play the
interviewer for the chosen round, ask **one question at a time**, wait for the user's
answer, then give brief, specific feedback (what landed, what to tighten, whether they
reached for the right story) before the next question. Calibrate difficulty to the
round. Pull from the predicted-questions list and lean into the gap questions, since
those are where people most need reps. After ~6–10 questions (or when they call it),
give a short overall read: strongest answers, the 2–3 things to fix, and any story
that still needs sharpening. Never invent facts about the user to fill an answer — if
they fumble a story, help them reshape *their real* material, not a better fictional
one.

## Step P4 — Close out & enrich the library

Point them back to whichever piece they didn't use yet ("want the mock now?" / "want
the written kit to review later?"), and remind them prep is sharpest from the
application chat next time. **Log the upcoming interview** on the role's
`applications.json` record (round + date, `status: interviewing`) per
**`references/application-tracker.md`**.

Then **enrich the library** (per "The library is a living system" up top). Prep is one
of the richest sources of new material: stories the user told better out loud than
they're written in the fact pack, a failure or conflict story that wasn't logged, a
gap framing they worked out during the mock that's worth saving, or a metric they
recalled mid-answer. Capture it per `profile.json → library_enrichment.mode` (confirm
vs. silent), recording only what they actually said. If the library was thin where it
mattered — a sparse story bank, no failure story, gaps with no prepared framing — name
it so `fact-pack.md` is stronger before the next round.

## Step P5 — Debrief the real interview (after it happens)

Prep gets the user ready; the **debrief** is how the kit learns from how it actually
went. Runs when the user comes back from a real interview and wants to review it —
"debrief that interview", "how did I do", "review my interview". Best run in the same
chat as the prep, where the prep kit and predicted questions are already in context.

**This requires a written transcript** (Meetily recommended, but any accurate
transcript works — Otter, the call platform's own captions, or a clean manual
transcription). The debrief grades what *actually happened* against the prep; a
from-memory recap is too lossy and biased by the user's own impression to be useful, so
the kit does **not** reconstruct a debrief from recollection. No transcript, no
debrief — say that plainly and point them at the capture setup for next time (in
`references/interview-prep.md`).

When the user has a transcript:

1. **Quick consent note (once).** The speakerphone capture path records the other
   party's voice. Most places are one-party consent, but ~a dozen states (and some
   countries) require all-party consent. Remind the user it's on them to have had the
   legal basis to record; the kit doesn't police it, but flags it so they're not
   blindsided. (Don't moralize — one line.)
2. **Synthesize against the prep kit**, per `references/interview-prep.md`: which
   predicted questions actually came up (and which the prep missed), how each answer
   landed, where they reached for the right story vs. fumbled, which gaps got probed
   and whether the prepared framing held, and anything notable in how the interviewer
   reacted or where the conversation cooled or warmed.
3. **Deliver a tight learning report**: strongest answers, the 2–3 highest-leverage
   fixes, and specific lines or stories to tighten — concrete and quotable from the
   transcript, never generic interview advice.
4. **Enrich the library** (per "The library is a living system"). The debrief is the
   single richest signal the kit gets, because it's real performance, not rehearsal:
   flag underperforming stories for reshaping, add questions the prep didn't predict to
   the bank for next time, and rewrite gap-framings that didn't hold. Capture per the
   user's `library_enrichment.mode`, recording only what the transcript actually shows.
   This is the compounding loop — every real interview makes the next prep sharper.
5. **Update the tracker and offer a thank-you.** Mark the interview `debriefed` with a
   one-line outcome in `applications.json`, and — since it's within the ~24-hour window —
   offer to draft the post-interview thank-you (specific to this conversation, in the
   user's voice). Both per **`references/followup-and-negotiation.md`** and
   **`references/application-tracker.md`**.

Setup for capturing the transcript (Meetily, both call types, speakerphone tips) is in
`references/interview-prep.md`.

---

# D. OUTREACH — reach the human directly

An application goes into a pile; a personal note to the right human can pull it out.
This builds that note — but only when the fit is genuine, because outreach works
*because* it's real. Best run as the next step after a strong RUN (the JD, strategy,
and tailored materials are right there), but works standalone too ("help me reach out
to the hiring manager at X").

Full method — finding the person, deducing the email, the subject-line formula, the
body arc, the LinkedIn variant, and the guardrails — is in
**`references/outreach-playbook.md`**. Read it and follow it. The essentials:

- **Tier-gate it.** Outreach is for **tier-1, genuinely strong-fit roles** — where the
  user has a real passion, near-exact experience match, or personal hook. On tier-1,
  **recommend it proactively and draft it without being asked**. On tier-2/3 with no
  genuine hook, **don't push it**; offer only if asked, and be honest it's weaker
  without a real connection. Never manufacture a passion or connection to justify a
  note. (Pull the tier from the scan score if there is one; judge fit from the fact
  pack if standalone.)
- **Two methods: email preferred, LinkedIn fallback.** Email when the address is
  findable and the user's willing; LinkedIn (shorter, no subject line) when the email
  can't be found/verified or they'd rather not cold-email. On a strong tier-1 role,
  prepare both.
- **Find a real named person** (hiring manager for "why I'm a fit," recruiter for "is
  this live / please flag my app") via LinkedIn research — never invent a name.
- **Deduce the email honestly** — hunter.io in the browser or pattern inference from a
  known company address; **flag whether it's verified or just deduced** (deduced may
  bounce), and never present a guess as confirmed.
- **Write it in the user's voice** (`voice.md` + the cover-letter playbook's craft
  rules + `references/writing-standards.md`), grounded in `fact-pack.md`. The
  subject-line formula and body arc in the playbook are an **adaptable pattern, not a
  fill-in template** — shape them to the individual's voice, material, and prep. A true
  single hook beats three stretched ones. The danger here is sounding like cold AI
  outreach, so the structural tells matter doubly: no asyndeton lists, no "Here's why
  I'm perfect for this," lead with a genuine specific.
- **Deliver copy-paste-ready; never auto-send.** The human always presses send on
  something genuinely personal. (A reviewed Gmail *draft* is fine if they ask; the human
  still sends.)
- **Enrich the library** afterward with any genuine new hook that surfaced, per the
  enrichment mode, and **log the outreach** on the role's `applications.json` record
  (method, who, email-confidence, date) per **`references/application-tracker.md`**.

---

# Scanner & Scheduling (optional)

A config-driven scanner surfaces new matching roles and feeds them into RUN. It does
**broad market discovery** across keyless aggregators (Remotive, RemoteOK, Arbeitnow,
Jobicy; Adzuna optional) plus an **optional** Greenhouse/Lever/Ashby watchlist.
Everything it filters/scores on lives in `user-library/scanner_config.json`.

**Run a scan now** (on a machine with network):
```bash
python3 <skill_dir>/scripts/job_scanner.py --config <working>/user-library/scanner_config.json
```

**Two-stage scoring (don't deep-read everything).** The script is the cheap **Stage-1**
card pass: it scores every role 0–100 from the listing and flags `deep_read: true/false`
against `deep_read_threshold` (default 50). The agent does **Stage 2** by hand only on
flagged cards — open the JD, do a live-status check (drop 404s / "no longer accepting"),
extract real comp + scope, re-score, and for a profile-only find (Wellfound/LinkedIn)
search for the canonical ATS "Apply at" link. Scoring is calibrated so domain is
non-exhaustive (an unlisted domain is neutral; only `exclude_keywords` drop a role) and
role-shape/baseline can carry a well-shaped role over the bar with no domain match.

**Scheduled & unattended runs** can't use bash networking, so the agent web-fetches each
source. Full procedure, the LinkedIn/Wellfound logged-in browser pass, and the ready-made
scheduled-task prompt are in **`references/scheduling.md`** and
**`references/scanner-scheduled-task.template.md`** — default cadence twice daily
(~8am/4pm local). Postings dedupe via `seen_postings.json` so nothing repeats. From a
shortlisted role the user drops into **RUN**.

**Scan reactions are preference signal — feed them back.** When the user reacts to a
shortlist ("not interested in crypto," "more founding roles," "too junior"), offer to
refine `scanner_config.json` per the enrichment mode — only encoding preferences they
actually expressed.

---

## Why the script/judgment split (so future-you doesn't undo it)

The scripts exist because docx building, PDF conversion, page counting, and
letterhead styling are deterministic and were re-derived by hand every time before
they existed — slow and inconsistent. They now run identically every run, and read
the user's `profile.json` + `format.json` so they carry no one's identity in code.
Everything left in these instructions is genuine judgment: the tailoring, the
truthfulness filter, the trim decisions, which ATS recs to honor, and — above all —
writing in the user's actual voice. Don't push judgment into scripts (they can't
tell truth from plausible fiction, and they can't write like the user) and don't
pull mechanics back into prose (you'll reinvent them under time pressure).

## Bundled scripts

- `scripts/generate_resume.py` — resume markdown → polished one-page `.docx`.
  Parametrized by `profile.json` (identity) + `format.json` (fonts/colors).
- `scripts/export_pdf.py` — DOCX → PDF via LibreOffice headless (faithful render).
- `scripts/page_count.py` — prints `PAGES: n`; on overflow prints the page-2+ text
  so you trim deliberately.
- `scripts/build_cover_letter.py` — cover-letter markdown → `.docx` using the
  resume's design tokens, so letter and resume match. Renders only — words are
  yours.
- `scripts/job_scanner.py` — config-driven scanner: broad discovery across keyless
  remote-job aggregators (Remotive/RemoteOK/Arbeitnow/Jobicy, Adzuna optional) plus
  an optional Greenhouse/Lever/Ashby watchlist. Card-level (Stage 1) scoring with a
  recency gate, non-exhaustive domain tiers, role-shape signals + baseline, and a
  `deep_read` flag per result. `--print-urls` and `--input-dir` support the
  unattended web-fetch flow.
- `scripts/lint_copy.py` — advisory linter: `prose` flags the structural AI tells from
  `writing-standards.md`; `parse` checks a resume PDF extracts cleanly for ATS parsing.
  Surfaces issues for judgment; never rewrites.
- `scripts/selfcheck.py` — post-install/edit health check: compiles the scripts, reports
  dependencies (python-docx / LibreOffice / poppler / pypdf), and asserts the scanner's
  core logic (incl. the word-boundary exclude behavior) against a built-in fixture.

## Bundled references

`references/onboarding-interview.md` (Quick + Thorough question sets) ·
`references/profile-template.json` · `references/base_resume-template.md` ·
`references/fact-pack-template.md` · `references/voice-template.md` ·
`references/format-template.json` · `references/cover-letter-playbook.md` ·
`references/ats-rubric.md` · `references/browser-autofill.md` ·
`references/scheduling.md` · `references/scanner_config.template.json` ·
`references/scanner-scheduled-task.template.md` · `references/interview-prep.md` ·
`references/outreach-playbook.md` · `references/writing-standards.md` ·
`references/application-tracker.md` · `references/followup-and-negotiation.md`
