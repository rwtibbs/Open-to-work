# Scheduled Job Scanning

How to set up a recurring scan that surfaces a ranked shortlist of new matching
roles on a schedule, and exactly how the unattended run works. Nothing here is
person-specific — the sources and criteria live in the user's
`user-library/scanner_config.json`.

## Setting up the schedule

Use the scheduling capability to create a recurring task. Let the user pick the
frequency and times; **default to twice daily, ~8am and ~4pm local time** (a fresh
morning batch and an afternoon catch-up). Confirm their timezone.

Install the ready-made prompt from **`references/scanner-scheduled-task.template.md`**
as the scheduled task (fill its two placeholders first). It already wires up the full
flow below — the logged-in LinkedIn/Wellfound browser pass, the keyless API
aggregators, two-stage scoring, the live-status check, and the canonical-ATS lookup.
This is a **surface-only** digest — discover and rank, do NOT tailor resumes or write
cover letters in the scheduled run.

## The unattended run flow (important — read carefully)

The scanner hits public job-board JSON APIs, but **the sandbox's bash networking is
blocked**, so the script can't fetch the sources itself when run unattended. Instead
the scheduled agent fetches each source with its **web tool** and feeds the saved
JSON back to the script.

Make a clean `fetched/` folder first (remove + recreate) so stale files from a prior
run aren't re-parsed.

### Stage 0 — fetch

1. **Get the source URLs.** Run the scanner in URL mode:
   ```bash
   python3 scripts/job_scanner.py --print-urls --config user-library/scanner_config.json
   ```
   It prints one `source<TAB>label<TAB>url` line per fetch task — one per discovery
   query/tag, plus one per watchlist board if the watchlist is enabled.

2. **Fetch each URL with the web tool and save the JSON.** For every printed line,
   web-fetch the URL and write the raw JSON response to:
   ```
   fetched/{source}__{label}.json
   ```
   (e.g. `fetched/remotive__product-designer.json`, `fetched/greenhouse__acme.json`).
   The filename pattern matters — the script looks for exactly
   `{source}__{label}.json`. Skip any source that fails to fetch; the run continues
   without it.

   **Browser pass (recommended — this is how LinkedIn + Wellfound get included).**
   LinkedIn and Wellfound have no keyless API, so the *only* way to scan them is a
   logged-in browser pass using the **Claude for Chrome extension** and the user's
   signed-in session. When the extension is set up, run this pass: open each site's
   role search in its own tab, **capture deep** (scroll and re-read 8–10×, don't stop
   at the first screen — a single read returns only the top few), keep genuine
   matches, and save them as `fetched/linkedin__<label>.json` /
   `fetched/wellfound__<label>.json` in the simple shape
   `[{title, company, location, url, description?, comp_text?}]`. The script picks up
   any extra `{source}__{label}.json` files in `--input-dir` and scores them through
   the exact same pipeline. If the extension isn't installed or Chrome isn't awake,
   skip this pass and note it — the scan continues with the API sources.

### Stage 1 — card-level score (every role)

3. **Parse, filter, score, dedupe from the saved files:**
   ```bash
   python3 scripts/job_scanner.py --input-dir fetched --config user-library/scanner_config.json
   ```
   This reads the saved JSON instead of the network, applies the criteria
   (role-title gate, US/location gate, optional remote-or-home, hard-exclude
   domains, the **recency gate** that drops postings older than `max_age_days` *only*
   where a date is exposed, and the sub-floor-comp drop), drops anything already in
   `seen_postings.json`, dedupes across sources, scores survivors 0–100, writes
   `shortlist_latest.json`, and prints a markdown shortlist. This is the **cheap
   pass** — the card rules out roughly half on obvious comp/domain mismatch.

   Each shortlist item carries `deep_read: true/false`, set by whether its card score
   clears the configurable `deep_read_threshold` (default 50).

### Stage 2 — deep read (only the promising cards)

4. **Do NOT deep-read everything.** For each role marked `deep_read: true` (card
   score > threshold), open its `url` and read the **full JD** (web-fetch; if blocked
   or JS-heavy, use the browser tool's page-text reader). From the real JD:
   - **Live-status check.** If the page is a 404, redirects to a generic
     careers/listing page, or shows "no longer accepting applications" / "position
     filled," **drop** that role (or, if uncertain, keep it and prefix the title with
     "⚠ appears closed — verify").
   - **Re-score from the real JD:** correct any comp the card lacked, judge true
     seniority/scope, and re-assess domain tier. Note any role whose score materially
     changed. Roles marked `deep_read: false` stay at their card score and are
     labeled "(card-level only)."

5. **Canonical ATS link for profile-only finds.** For each shortlisted role whose
   `url` is a profile-only source that blocks file upload (e.g. `wellfound.com`, a
   `linkedin.com` job listing), do one quick search like
   `"<Company>" "<Title>" greenhouse OR ashby OR lever` (and/or check the company
   careers page) to find the **canonical ATS posting** where the tailored résumé +
   cover letter can actually be uploaded. If found and it's the same role, surface it
   as the **"Apply at"** link; if none exists, note "profile-only — no ATS posting
   found." One or two searches per role, no more.

### Deliver

6. **Surface the top-N shortlist to the user**, ranked by final (post-deep-read)
   score, each item showing its listing URL (and the "Apply at" canonical link when
   the find was profile-only), and marked "(deep-read)" or "(card-level only)."
   Newly surfaced postings are recorded in `seen_postings.json` so they don't reappear
   on the next run — each scan shows only what's genuinely new.

From there the user can pick a posting and say "tailor my resume for this" to drop
straight into the RUN pipeline. That closes the loop: **scan → shortlist →
(deep-read) → tailor → ATS → cover letter + answers → browser fill/upload.**

## What's supported

- **Discovery sources** — Remotive, RemoteOK, Arbeitnow, Jobicy via their key-free
  public JSON APIs; **Adzuna** optionally behind a free API key. These do broad
  market discovery across companies the user never pre-listed.
- **Watchlist supplement** — **Greenhouse, Lever, and Ashby** boards, via their
  key-free public JSON APIs. To add a company, find its board slug
  (`boards.greenhouse.io/<token>`, `jobs.lever.co/<token>`, or
  `jobs.ashbyhq.com/<token>` — Ashby slugs are case-sensitive) and add a
  `{company, ats, token}` object to the watchlist. Verify it resolves before trusting
  it.
- Companies on other systems (Workday, SmartRecruiters, etc.) would each need a new
  normalizer in `job_scanner.py` — straightforward to add (see the `NORMALIZERS`
  dict), but not included.

## LinkedIn / Wellfound / Indeed — via the browser pass, not an API

**LinkedIn, Wellfound (AngelList), and Indeed** have no clean, key-free public JSON
API and actively block scripted access (auth walls, bot detection, ToS limits), so
they can't be reached by the keyless aggregator path. The way to include them is the
**logged-in browser pass** above (Claude for Chrome + the user's session) — which the
scheduled-task template runs for **LinkedIn and Wellfound** by default. Indeed is the
most aggressively bot-protected of the three and isn't included by default, but a
browser pass for it can be added the same way. If the user hasn't set up the Chrome
extension, these sources are simply skipped and the scan falls back to the keyless
aggregators — prompt them to add it (Step A3c) to unlock LinkedIn + Wellfound.
