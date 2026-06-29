# Scheduled job-scan task — prompt template

This is the **ready-made prompt to install as the recurring scheduled task** when the
user opts into automated scanning (Step A3b). Copy it, fill the two bracketed
placeholders, and register it with the scheduling capability (default cadence: twice
daily, ~8am and ~4pm local — confirm the user's timezone). Nothing here is
person-specific; all the search criteria live in the user's `scanner_config.json`.

The task runs the full flow your own on-demand scans do: a **logged-in browser pass**
over LinkedIn, Wellfound, and Built In (for tech users), the keyless API aggregators
(best-effort), two-stage scoring, a live-status check, the canonical-ATS lookup, and
a **tab cleanup step** that closes every tab the run opened. The browser pass needs
the **Claude for Chrome extension** and the user signed in to those sites; if Chrome
isn't available when the task fires, the task skips that pass and continues with the
API sources. Aggregator failures are skipped (never routed through the browser as a
fallback). Incremental `phases/` artifacts mean a mid-run drop is recoverable.

---

```
name: job-scanner-scheduled
description: Scheduled job scan — logged-in browser pass (LinkedIn + Wellfound + Built In for tech users) plus keyless API aggregators, scored against the user's criteria; surfaces a ranked shortlist with tab cleanup.
---

You are running the user's scheduled job scan. Work in: [WORKING_FOLDER]
The skill scripts/config are at: [SKILL_DIR]   (scripts in [SKILL_DIR]/scripts,
config + state in [WORKING_FOLDER]/user-library)

SURFACE-ONLY digest: discover new matching roles and report a ranked shortlist. Do
NOT tailor resumes or write cover letters. Make a clean `fetched/` folder first
(remove + recreate). Do BOTH passes; if either fails, continue with whatever you got.

TRACK TABS: keep a list of every browser tab ID you open during this run (search tabs
AND deep-read JD tabs). You will close them all in the CLEANUP step at the end.

=== PASS 1: BROWSER (needs the Claude for Chrome extension + the user's logged-in
    session) ===
Use the Claude for Chrome tools. Open a browser context; if the extension is
unavailable or not logged in, SKIP this pass and note it. Otherwise, each in its own
tab (record every tab ID):
  A. LinkedIn — jobs search for the user's target role, filtered to remote + past 24h,
     sorted newest.
  B. Wellfound — the matching remote role listing.
  C. Built In (TECH/STARTUP USERS ONLY — skip if the user's field is non-tech):
     - National/remote: https://builtin.com/jobs/remote/<category>?search=<role>
     - Metro (optional): https://builtin.com/jobs/<region>/<category>?search=<role>
       e.g. region = colorado, nyc, chicago, los-angeles, seattle, austin, boston
     Let the page load fully before capturing (JS-rendered). Save to:
       fetched/builtin__<role-slug>.json
       fetched/builtin-<region>__<role-slug>.json (if metro used)
  CAPTURE DEEP for all browser boards, not just the first screen: one page-read
  returns only the top few results. After the first read, SCROLL the results pane,
  wait ~1s, read again, repeat ~8-10x (on LinkedIn also page to 2-3). Accumulate ALL
  unique listings; stop when clearly older than 24h (LinkedIn) or after ~75 rows
  (Wellfound/Built In). Keep only genuine matches for the user's target role (use
  their role_keywords/levels); drop keyword noise. Write kept rows as JSON arrays of
  {title, company, location, url, comp_text, description} to the fetched/ files above.

=== PASS 2: API AGGREGATORS (best-effort; skip failures; NEVER route through browser)
  1. `python3 [SKILL_DIR]/scripts/job_scanner.py --print-urls --config [WORKING_FOLDER]/user-library/scanner_config.json`
     → source<TAB>label<TAB>url lines.
  2. Fetch each URL with the web tool and save raw JSON to
     fetched/{source}__{label}.json. RESILIENCE RULES:
     - If a fetch fails, times out, returns non-JSON, or is blocked: SKIP it, log it,
       continue. HARD RULE: NEVER route aggregator JSON through the browser/JS-eval
       as a fallback — that path causes connection drops. The browser pass is primary;
       aggregators are best-effort only.
     - Missing source files in --input-dir are skipped gracefully by the script.

=== STAGE 1: CARD-LEVEL SCORE (every role) ===
  3. `python3 [SKILL_DIR]/scripts/job_scanner.py --input-dir fetched --config [WORKING_FOLDER]/user-library/scanner_config.json`
     — applies the criteria (role gate, location gate, hard-exclude domains, recency
     gate, sub-floor-comp drop; non-exhaustive domain tiers; role-shape signals +
     right-shape baseline), dedupes across sources + `seen_postings.json`, scores
     0-100, writes shortlist_latest.json + phases/ artifacts (incremental persistence),
     and prints a ranked markdown block. This is the cheap pass — it rules out roughly
     half on obvious comp/domain mismatch. Each item is flagged deep_read=true/false
     against `deep_read_threshold` (default 50).

=== STAGE 2: DEEP READ (only roles above the threshold — keep it scoped) ===
  4. Do NOT deep-read everything. For each role with deep_read=true ONLY, open its
     `url` and read the FULL JD (web tool; if blocked or JS-heavy, use the Chrome
     page-text reader). Record every tab ID you open.
     LIVE-STATUS CHECK: if the page is a 404, redirects to a generic careers/listing
     page, or shows "no longer accepting applications" / "position filled", DROP that
     role (or, if uncertain, keep it and prefix the title "⚠ appears closed —
     verify"). Otherwise extract real comp + true seniority/scope + how on-target it
     is, and RE-SCORE. Card-level-only roles stay at their card score, labeled
     "(card-level only)".

=== STAGE 2b: CANONICAL ATS LINK (for profile-only finds) ===
  4b. For each shortlisted role whose `url` is a profile-only source that blocks file
     upload (wellfound.com, a linkedin.com job listing, or builtin.com), do ONE web
     search like `"<Company>" "<Title>" greenhouse OR ashby OR lever` (and/or check
     the company careers page) to find the CANONICAL ATS posting where the tailored
     résumé + cover letter can actually be uploaded. If found and it's the same role,
     capture it as the "Apply at" link. If none exists, note "profile-only — no ATS
     posting found." One or two searches per role, no more.

=== DELIVER ===
  5. Send the enriched shortlist, ranked by final (post-deep-read) score. For each
     role include the listing URL (and the "Apply at" canonical link when the find was
     profile-only), one line on what the company does, one honest line on why it fits
     vs the user's targeting, and mark "(deep-read)" or "(card-level only)". Add one
     line on which sources were hit (and whether the browser pass ran). If the scanner
     printed "No new matching postings," send just that.

=== CLEANUP (tab cleanup — after delivering the digest) ===
  6. Close every browser tab opened during this run using tabs_close_mcp. This
     includes: all search tabs from Pass 1 (LinkedIn, Wellfound, Built In), and all
     JD tabs opened during Stage 2 deep-read. Use the tab IDs you tracked above.
     ONLY close tabs from this run — do not close the user's own tabs or any
     application tabs they may have open. If a tabs_close_mcp call fails for a
     specific tab, note the tab ID in your status line but do not let it block
     completion.

Truthfulness: only real postings; recommendations on deep-read roles must come from
the actual JD, not the card or company assumptions. The browser pass only runs when
the desktop/Chrome are awake and the user is logged in.
```

---

**Filling the placeholders:** `[WORKING_FOLDER]` = the user's working folder (where
`user-library/` lives); `[SKILL_DIR]` = the installed skill's directory. Optionally
add a Glassdoor-rating enrichment step or a comp-range note per role if the user wants
it — keep it generic and honest ("unclear from the posting" when unknown).
