#!/usr/bin/env python3
"""
job_scanner.py — config-driven job-board scanner for the open-to-work skill.

WHAT IT DOES
  Broad market DISCOVERY across keyless, remote-focused job aggregators, plus an
  OPTIONAL per-company ATS watchlist. Every run:
    1. Reads scanner_config.json (discovery sources + optional watchlist + the
       calibrated `criteria` scoring brain).
    2. Pulls public job-board JSON (no API key required for the discovery
       sources; Adzuna is optional and gated behind a free key).
    3. Filters by role-title, location, recency, and hard-exclude domains.
    4. Dedupes against seen_postings.json AND across sources within the run.
    5. STAGE-1 SCORES survivors 0-100 with a transparent, criteria-driven
       heuristic, and flags which ones clear `deep_read_threshold` — i.e. which
       are worth a STAGE-2 full-JD deep read by the agent (the script does the
       cheap card-level pass; the agent does the expensive full-JD pass on only
       the cards that already look promising).
    6. Writes shortlist_latest.json + prints a human-readable markdown block.

NO personal data is baked in. Roles, levels, locations, comp thresholds, recency
window, domain tiers, exclude list, and keyword weights ALL come from the
`criteria` block of scanner_config.json — swap that file and the same script
scans for a completely different search. Home city/region live in
criteria.home_terms; there is no hardcoded location anywhere.

DISCOVERY SOURCES (primary; keyless free JSON APIs)
  - Remotive    https://remotive.com/api/remote-jobs?search=...
  - RemoteOK    https://remoteok.com/api
  - Arbeitnow   https://www.arbeitnow.com/api/job-board-api
  - Jobicy      https://jobicy.com/api/v2/remote-jobs?count=...&tag=...
  - Adzuna      OPTIONAL, gated behind config + a free API key (skipped if off)

WATCHLIST SUPPLEMENT (optional; toggle "watchlist_enabled")
  - Greenhouse / Lever / Ashby per company token.

Stdlib only (urllib). No pip installs. Python 3.8+.

PATHS — default to the script's own directory, override with flags or env:
  --config    <path>  scanner_config.json    (env JOB_SCANNER_CONFIG)
  --seen      <path>  seen_postings.json     (env JOB_SCANNER_SEEN)
  --shortlist <path>  shortlist_latest.json  (env JOB_SCANNER_SHORTLIST)
Point these at your user-library/ so config and state live with your data.

INCREMENTAL PERSISTENCE (Change 3)
  On every run the script writes intermediate artifacts to a phases/ subdirectory
  (next to shortlist_latest.json) so a mid-run connection drop loses nothing:
    phases/normalized_<source>_<label>.json   — rows per source after normalizing
    phases/scored_candidates.json             — all survivors after card-level score
    phases/deep_read_queue.json               — roles flagged for Stage-2 deep-read
  The final shortlist_latest.json is written at the end as before.
  Missing source files in --input-dir mode are skipped gracefully (no crash).
  HARD RULE: aggregator JSON is NEVER routed through the browser/JS-eval as a
  fallback. If a source fails, it is skipped; the browser pass is primary.

BUILTIN SUPPORT (Change 1)
  Built In (builtin.com) is a JS-rendered tech/startup board. The browser pass
  saves results as fetched/builtin__<label>.json (national/remote) and/or
  fetched/builtin-<region>__<label>.json (metro). All "builtin*" keys are
  automatically routed through normalize_manual.

USAGE
  python3 job_scanner.py --config user-library/scanner_config.json
  python3 job_scanner.py --print-urls --config user-library/scanner_config.json
        # emits one "source<TAB>label<TAB>url" line per fetch task, for the
        # unattended web_fetch flow (sandbox bash networking is blocked, so a
        # scheduled agent fetches each url with its web tool instead).
  python3 job_scanner.py --input-dir fetched --config user-library/scanner_config.json
        # parse pre-fetched JSON saved as <input-dir>/{source}__{label}.json
  python3 job_scanner.py --dry-run   # do not update seen_postings.json
"""

import os
import re
import sys
import json
import html
import time
import datetime
import email.utils
import urllib.parse
import urllib.request
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))

HTTP_TIMEOUT = 25  # seconds, per request
USER_AGENT = "Mozilla/5.0 (job-scanner; +personal use)"

# Comp parsing is config-driven so the scanner works outside the US/USD default.
# run() overwrites these from criteria.comp_band / criteria.accept_currencies
# before any normalizing happens. Defaults preserve the original US/USD behavior:
# a plausible annual band (so an hourly/monthly figure isn't mistaken for salary)
# and a currency allowlist (so a £/€ number isn't mis-ranked as USD).
COMP_BAND = (40000, 1000000)
ACCEPT_CURRENCIES = {"USD", "US$", "$", ""}

# Generic geographic vocabulary used only as a default US/non-US guard when
# criteria.us_only is true. This is general knowledge, not personal preference —
# your own home city/region go in criteria.home_terms / criteria.locations.
US_TOKENS = [
    "united states", "u.s.", "usa", "remote - us", "remote us", "remote, us",
    "remote-us", "americas", "anywhere in the us", "nationwide",
    "us-remote", "us remote", "north america",
]
NONUS_TOKENS = [
    "india", "bangalore", "mumbai", "hyderabad", "london", "united kingdom",
    "u.k.", " uk", "uk ", "ireland", "dublin", "germany", "berlin", "munich",
    "france", "paris", "spain", "madrid", "barcelona", "netherlands",
    "amsterdam", "poland", "warsaw", "krakow", "singapore", "australia",
    "sydney", "melbourne", "canada", "toronto", "vancouver", "emea", "apac",
    "europe", "brazil", "mexico", "japan", "tokyo", "israel", "tel aviv",
    "philippines", "argentina", "colombia", "portugal", "lisbon", "sweden",
    "denmark", "switzerland", "zurich", "new zealand", "south africa",
    "korea", "china", "hong kong", "taiwan", "vietnam", "indonesia",
]


def _terms(criteria, key):
    return [t.lower() for t in criteria.get(key, []) if t]


def location_ok(loc, criteria):
    """True if a location string is acceptable given criteria.

    A posting passes when its location matches any of criteria.locations or
    criteria.home_terms (plus empty/remote, which are ambiguous and let
    through). If criteria.us_only is true, the generic non-US guard excludes
    clearly foreign-only roles. With no location preferences configured, falls
    back to the generic US/non-US heuristic."""
    if not loc:
        return True  # no location given -> let it through; scoring handles rest
    s = loc.lower()
    wanted = _terms(criteria, "locations") + _terms(criteria, "home_terms")
    remote = "remote" in s or "worldwide" in s or "anywhere" in s
    if wanted:
        if any(tok in s for tok in wanted):
            return True
        if remote:
            return True
        if criteria.get("us_only", True) and any(tok in s for tok in NONUS_TOKENS):
            return False
        return False
    # No location preferences configured: fall back to US/non-US heuristic.
    if not criteria.get("us_only", True):
        return True
    has_us = (
        any(tok in s for tok in US_TOKENS)
        or re.search(r"\bus\b", s) is not None
        or re.search(r"\bu\.s\.?\b", s) is not None
    )
    if has_us:
        return True
    if any(tok in s for tok in NONUS_TOKENS):
        return False
    return remote  # generic "Remote" with no country signal -> allow


def location_bucket(loc, criteria):
    """Return ('home'|'remote'|'ok'|'unknown') for scoring."""
    s = (loc or "").lower()
    if any(tok in s for tok in _terms(criteria, "home_terms")):
        return "home"
    if "remote" in s or "worldwide" in s or "anywhere" in s:
        return "remote"
    if location_ok(loc, criteria):
        return "ok"
    return "unknown"


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #
def _http_get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    return json.loads(raw)


# --------------------------------------------------------------------------- #
# Text + comp helpers
# --------------------------------------------------------------------------- #
def _strip_html(text):
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _comp_from_text(text):
    """Best-effort: find an annual USD figure in free text.
    Returns (display, max_int) or (None, None). Ignores small hourly/monthly
    figures by requiring the value to land in a plausible annual band."""
    if not text:
        return None, None
    nums = []
    for m in re.finditer(r"\$\s?(\d{2,3})(?:,?(\d{3}))?\s?[kK]?", text):
        whole, thousands = m.group(1), m.group(2)
        raw = m.group(0).lower()
        if "k" in raw and not thousands:
            val = int(whole) * 1000
        elif thousands:
            val = int(whole + thousands)
        else:
            val = int(whole)
        if COMP_BAND[0] <= val <= COMP_BAND[1]:
            nums.append(val)
    if not nums:
        return None, None
    lo, hi = min(nums), max(nums)
    disp = "${:,}".format(hi) if lo == hi else "${:,}-${:,}".format(lo, hi)
    return disp, hi


def _comp_from_minmax(smin, smax, currency="USD"):
    """Build comp from structured numeric min/max fields. Only trusts USD
    (or unspecified) currency so a £/€ figure is never mis-ranked as USD."""
    try:
        smin = int(float(smin)) if smin not in (None, "", 0, "0") else 0
    except (TypeError, ValueError):
        smin = 0
    try:
        smax = int(float(smax)) if smax not in (None, "", 0, "0") else 0
    except (TypeError, ValueError):
        smax = 0
    cur = (currency or "USD").upper()
    if cur not in ACCEPT_CURRENCIES:
        return None, None
    hi = max(smin, smax)
    lo = min(smin, smax) if smin and smax else hi
    if hi < COMP_BAND[0] or hi > COMP_BAND[1]:
        return None, None
    if lo and lo != hi:
        return "${:,}-${:,}".format(lo, hi), hi
    return "${:,}".format(hi), hi


def _mark_remote(loc):
    """For remote-only boards: ensure the location string carries a 'remote'
    signal so a require_remote_or_home gate doesn't wrongly drop it, while
    leaving any country token intact for the US/non-US gate."""
    loc = (loc or "").strip()
    if not loc:
        return "Remote"
    if "remote" in loc.lower():
        return loc
    return loc + " (Remote)"


# --------------------------------------------------------------------------- #
# Date parsing (recency gate). VERY defensive: any unparseable / missing value
# returns None so the row is treated as "no date" and KEPT — never dropped,
# never crashes the run.
# --------------------------------------------------------------------------- #
def _to_epoch(value):
    """Best-effort: turn a posting's date field into a UTC epoch (float seconds).

    Accepts epoch seconds or milliseconds (int/float or numeric string),
    ISO-8601 strings ("2026-06-09T19:54:57+00:00", "...Z", date-only), and
    RFC-2822 strings ("Mon, 09 Jun 2026 19:54:57 +0000"). Returns epoch seconds
    (float) or None on anything missing/unparseable."""
    if value is None:
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        try:
            v = float(value)
        except (TypeError, ValueError):
            return None
        if v <= 0:
            return None
        return v / 1000.0 if v > 1e12 else v  # > 1e12 looks like ms
    if not isinstance(value, str):
        return None
    s = value.strip()
    if not s:
        return None
    if re.fullmatch(r"\d{9,16}", s):
        try:
            v = float(s)
        except ValueError:
            return None
        if v <= 0:
            return None
        return v / 1000.0 if v > 1e12 else v
    iso = s.replace("Z", "+00:00").replace(" ", "T", 1) if "T" not in s and " " in s else s.replace("Z", "+00:00")
    for candidate in (iso, s[:10]):  # full ISO, then date-only fallback
        try:
            dt = datetime.datetime.fromisoformat(candidate)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            return dt.timestamp()
        except (ValueError, TypeError):
            pass
    try:
        dt = email.utils.parsedate_to_datetime(s)
        if dt is not None:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            return dt.timestamp()
    except (TypeError, ValueError, IndexError, OverflowError):
        pass
    return None


def _posted(*values):
    """Given candidate raw date values (priority order), return
    (iso_string, epoch_seconds). Uses the first that parses; ('', None) if
    none. Stored on every normalized posting as posted_date / posted_epoch."""
    for v in values:
        ep = _to_epoch(v)
        if ep is not None:
            try:
                iso = datetime.datetime.fromtimestamp(
                    ep, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
            except (ValueError, OSError, OverflowError):
                iso = ""
            return iso, ep
    return "", None


# --------------------------------------------------------------------------- #
# Normalizers: each source -> common posting dict
#   {id, company, title, location, url, description, comp_text, comp_max,
#    posted_date, posted_epoch}
# --------------------------------------------------------------------------- #
def normalize_remotive(payload, label):
    out = []
    for j in payload.get("jobs", []):
        desc = _strip_html(j.get("description", ""))
        cat = j.get("category") or ""
        if cat:
            desc = (desc + " \n category: " + cat).strip()
        comp_text, comp_max = _comp_from_text(j.get("salary") or "")
        posted_date, posted_epoch = _posted(j.get("publication_date"))
        out.append({
            "id": "remotive:{}".format(j.get("id")),
            "company": (j.get("company_name") or "").strip(),
            "title": (j.get("title") or "").strip(),
            "location": _mark_remote(j.get("candidate_required_location") or ""),
            "url": j.get("url", ""),
            "description": desc, "comp_text": comp_text, "comp_max": comp_max,
            "posted_date": posted_date, "posted_epoch": posted_epoch,
        })
    return out


def normalize_remoteok(payload, label):
    """RemoteOK returns a JSON array whose FIRST element is metadata; skip it."""
    out = []
    if not isinstance(payload, list):
        return out
    rows = payload[1:] if payload and isinstance(payload[0], dict) and \
        "legal" in payload[0] else payload
    for j in rows:
        if not isinstance(j, dict):
            continue
        tags = j.get("tags") or []
        desc = _strip_html(j.get("description", ""))
        if tags:
            desc = (desc + " \n tags: " + ", ".join(map(str, tags))).strip()
        comp_text, comp_max = _comp_from_minmax(
            j.get("salary_min"), j.get("salary_max"), "USD")
        if comp_text is None:
            comp_text, comp_max = _comp_from_text(desc)
        posted_date, posted_epoch = _posted(j.get("epoch"), j.get("date"))
        out.append({
            "id": "remoteok:{}".format(j.get("id") or j.get("slug")),
            "company": (j.get("company") or "").strip(),
            "title": (j.get("position") or "").strip(),
            "location": _mark_remote(j.get("location") or ""),
            "url": j.get("url", "") or j.get("apply_url", ""),
            "description": desc, "comp_text": comp_text, "comp_max": comp_max,
            "posted_date": posted_date, "posted_epoch": posted_epoch,
        })
    return out


def normalize_arbeitnow(payload, label):
    out = []
    for j in payload.get("data", []):
        tags = j.get("tags") or []
        desc = _strip_html(j.get("description", ""))
        if tags:
            desc = (desc + " \n tags: " + ", ".join(map(str, tags))).strip()
        loc = j.get("location") or ""
        if j.get("remote"):
            loc = _mark_remote(loc)
        comp_text, comp_max = _comp_from_text(desc)
        posted_date, posted_epoch = _posted(j.get("created_at"))
        out.append({
            "id": "arbeitnow:{}".format(j.get("slug")),
            "company": (j.get("company_name") or "").strip(),
            "title": (j.get("title") or "").strip(),
            "location": loc,
            "url": j.get("url", ""),
            "description": desc, "comp_text": comp_text, "comp_max": comp_max,
            "posted_date": posted_date, "posted_epoch": posted_epoch,
        })
    return out


def normalize_jobicy(payload, label):
    out = []
    for j in payload.get("jobs", []):
        desc = _strip_html(j.get("jobDescription", "")) or \
            _strip_html(j.get("jobExcerpt", ""))
        lvl = j.get("jobLevel") or ""
        if lvl:
            desc = (desc + " \n level: " + lvl).strip()
        loc = _mark_remote(j.get("jobGeo") or "")  # remote-only board
        smin = j.get("salaryMin", j.get("annualSalaryMin"))
        smax = j.get("salaryMax", j.get("annualSalaryMax"))
        cur = j.get("salaryCurrency") or "USD"
        comp_text, comp_max = _comp_from_minmax(smin, smax, cur)
        if comp_text is None:
            comp_text, comp_max = _comp_from_text(desc)
        posted_date, posted_epoch = _posted(
            j.get("jobModified"), j.get("pubDate"), j.get("jobPubDate"))
        out.append({
            "id": "jobicy:{}".format(j.get("id")),
            "company": (j.get("companyName") or "").strip(),
            "title": (j.get("jobTitle") or "").strip(),
            "location": loc,
            "url": j.get("url", ""),
            "description": desc, "comp_text": comp_text, "comp_max": comp_max,
            "posted_date": posted_date, "posted_epoch": posted_epoch,
        })
    return out


def normalize_adzuna(payload, label):
    out = []
    for j in payload.get("results", []):
        desc = _strip_html(j.get("description", ""))
        # Adzuna usually returns PREDICTED salaries (salary_is_predicted=="1"):
        # Adzuna's own estimates, not employer-stated comp. Don't trust them as
        # real comp (it would wrongly trigger the sub-floor DROP on a fabricated
        # number) — fall back to any explicit figure in the text.
        predicted = str(j.get("salary_is_predicted", "")).lower() in ("1", "true")
        if predicted:
            comp_text, comp_max = _comp_from_text(desc)
        else:
            comp_text, comp_max = _comp_from_minmax(
                j.get("salary_min"), j.get("salary_max"), "USD")
            if comp_text is None:
                comp_text, comp_max = _comp_from_text(desc)
        company = ((j.get("company") or {}) or {}).get("display_name", "") or ""
        locobj = (j.get("location") or {}) or {}
        loc = locobj.get("display_name", "") or ""
        area = locobj.get("area") or []
        if area and str(area[0]).upper() == "US" and "united states" not in loc.lower():
            loc = (loc + ", US").strip().strip(",").strip()
        if re.search(r"\bremote\b", (j.get("title", "") + " " + desc), re.I) and "remote" not in loc.lower():
            loc = loc + " (Remote)"
        posted_date, posted_epoch = _posted(j.get("created"))
        out.append({
            "id": "adzuna:{}".format(j.get("id")),
            "company": company.strip(),
            "title": (j.get("title") or "").strip(),
            "location": loc,
            "url": j.get("redirect_url", ""),
            "description": desc, "comp_text": comp_text, "comp_max": comp_max,
            "posted_date": posted_date, "posted_epoch": posted_epoch,
        })
    return out


# Watchlist (optional supplement) normalizers
def normalize_greenhouse(payload, company):
    out = []
    for j in payload.get("jobs", []):
        desc = _strip_html(j.get("content", ""))
        comp_text, comp_max = _comp_from_text(desc)
        posted_date, posted_epoch = _posted(
            j.get("updated_at"), j.get("first_published"), j.get("created_at"))
        out.append({
            "id": "greenhouse:{}".format(j.get("id")),
            "company": company,
            "title": (j.get("title") or "").strip(),
            "location": (j.get("location") or {}).get("name", "") or "",
            "url": j.get("absolute_url", ""),
            "description": desc, "comp_text": comp_text, "comp_max": comp_max,
            "posted_date": posted_date, "posted_epoch": posted_epoch,
        })
    return out


def normalize_lever(payload, company):
    out = []
    for j in payload:
        cats = j.get("categories", {}) or {}
        loc = cats.get("location") or ""
        if not loc and j.get("allLocations"):
            loc = ", ".join(j.get("allLocations"))
        desc = j.get("descriptionPlain") or _strip_html(j.get("description", ""))
        comp_text, comp_max = None, None
        sr = j.get("salaryRange") or {}
        if sr.get("min") and sr.get("max"):
            comp_text = "${:,}-${:,}".format(int(sr["min"]), int(sr["max"]))
            comp_max = int(sr["max"])
        if comp_text is None:
            comp_text, comp_max = _comp_from_text(desc)
        posted_date, posted_epoch = _posted(j.get("createdAt"))  # epoch ms
        out.append({
            "id": "lever:{}".format(j.get("id")),
            "company": company,
            "title": (j.get("text") or "").strip(),
            "location": loc,
            "url": j.get("hostedUrl", "") or j.get("applyUrl", ""),
            "description": desc, "comp_text": comp_text, "comp_max": comp_max,
            "posted_date": posted_date, "posted_epoch": posted_epoch,
        })
    return out


def normalize_ashby(payload, company):
    out = []
    for j in payload.get("jobs", []):
        loc = j.get("location") or ""
        if not loc and j.get("address"):
            loc = j.get("address", {}).get("postalAddress", {}).get("addressRegion", "") or ""
        if j.get("isRemote") and "remote" not in loc.lower():
            loc = (loc + " (Remote)").strip()
        desc = j.get("descriptionPlain") or _strip_html(j.get("descriptionHtml", ""))
        comp_text, comp_max = None, None
        comp = j.get("compensation") or {}
        summary = comp.get("compensationTierSummary") or comp.get("scrapeableCompensationSalarySummary")
        if summary:
            comp_text, comp_max = _comp_from_text(summary)
            if comp_text is None:
                comp_text = summary
        if comp_text is None:
            comp_text, comp_max = _comp_from_text(desc)
        posted_date, posted_epoch = _posted(
            j.get("publishedAt"), j.get("publishedDate"), j.get("updatedAt"))
        out.append({
            "id": "ashby:{}".format(j.get("id")),
            "company": company,
            "title": (j.get("title") or "").strip(),
            "location": loc,
            "url": j.get("jobUrl", "") or j.get("applyUrl", ""),
            "description": desc, "comp_text": comp_text, "comp_max": comp_max,
            "posted_date": posted_date, "posted_epoch": posted_epoch,
        })
    return out


def normalize_manual(payload, label):
    """Generic normalizer for browser-extracted listings (e.g. a logged-in
    LinkedIn / Wellfound pass, or any 'manual' source). The browser pass writes
    a JSON list (or {"postings":[...]}) of simple objects:
    {title, company, location, url, description?, comp_text?}."""
    rows = payload.get("postings", payload) if isinstance(payload, dict) else payload
    out = []
    for j in (rows or []):
        if not isinstance(j, dict):
            continue
        comp_text = j.get("comp_text") or j.get("comp") or None
        comp_max = None
        if comp_text:
            _disp, comp_max = _comp_from_text(comp_text)
            if _disp:
                comp_text = _disp
        elif j.get("description"):
            comp_text, comp_max = _comp_from_text(j["description"])
        posted_date, posted_epoch = _posted(
            j.get("posted_date"), j.get("date"), j.get("posted_epoch"))
        out.append({
            "id": (j.get("url") or j.get("id") or "{}:{}".format(label, j.get("title", ""))),
            "company": (j.get("company") or "").strip(),
            "title": (j.get("title") or "").strip(),
            "location": (j.get("location") or "").strip(),
            "url": j.get("url", ""),
            "description": j.get("description", "") or "",
            "comp_text": comp_text, "comp_max": comp_max,
            "posted_date": posted_date, "posted_epoch": posted_epoch,
        })
    return out


NORMALIZERS = {
    "remotive": normalize_remotive,
    "remoteok": normalize_remoteok,
    "arbeitnow": normalize_arbeitnow,
    "jobicy": normalize_jobicy,
    "adzuna": normalize_adzuna,
    "greenhouse": normalize_greenhouse,
    "lever": normalize_lever,
    "ashby": normalize_ashby,
    # Optional browser pass (profile-only boards). The agent extracts listings
    # and saves them as fetched/{source}__{label}.json in the simple shape.
    "linkedin": normalize_manual,
    "wellfound": normalize_manual,
    # Built In (builtin.com) — JS-rendered tech/startup board; browser pass only.
    # Regional variants use "builtin-<region>" keys (e.g. "builtin-co", "builtin-nyc").
    # Any key starting with "builtin" that isn't registered explicitly is picked up
    # by the catch-all logic in run() and routed through normalize_manual below.
    "builtin": normalize_manual,
    "manual": normalize_manual,
}


# --------------------------------------------------------------------------- #
# Fetch-task assembly (shared by --print-urls, live fetch, and --input-dir)
# Each task: {"source", "label", "url", "filename"}
#   filename == "{source}__{label}.json"  (what the unattended agent saves to)
# --------------------------------------------------------------------------- #
def _slug(text):
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return s or "all"


def board_url(ats, token):
    return {
        "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{}/jobs?content=true".format(token),
        "lever": "https://api.lever.co/v0/postings/{}?mode=json".format(token),
        "ashby": "https://api.ashbyhq.com/posting-api/job-board/{}?includeCompensation=true".format(token),
    }.get(ats)


def build_fetch_tasks(config):
    """Return the ordered list of fetch tasks for all ENABLED sources."""
    tasks = []
    disc = config.get("discovery_sources", {}) or {}

    rm = disc.get("remotive", {}) or {}
    if rm.get("enabled", True):
        for q in rm.get("queries", ["product designer"]):
            url = "https://remotive.com/api/remote-jobs?search=" + urllib.parse.quote(q)
            tasks.append({"source": "remotive", "label": _slug(q), "url": url})

    ro = disc.get("remoteok", {}) or {}
    if ro.get("enabled", True):
        tasks.append({"source": "remoteok", "label": "all",
                      "url": "https://remoteok.com/api"})

    ab = disc.get("arbeitnow", {}) or {}
    if ab.get("enabled", True):
        tasks.append({"source": "arbeitnow", "label": "all",
                      "url": "https://www.arbeitnow.com/api/job-board-api"})

    jb = disc.get("jobicy", {}) or {}
    if jb.get("enabled", True):
        count = int(jb.get("count", 50))
        for tag in jb.get("tags", ["product designer"]):
            url = "https://jobicy.com/api/v2/remote-jobs?count={}&tag={}".format(
                count, urllib.parse.quote_plus(tag))
            tasks.append({"source": "jobicy", "label": _slug(tag), "url": url})

    az = config.get("adzuna", {}) or {}
    if az.get("enabled") and az.get("app_id") and az.get("app_key"):
        for q in az.get("queries", ["product designer"]):
            url = ("https://api.adzuna.com/v1/api/jobs/us/search/1"
                   "?app_id={}&app_key={}&what={}"
                   "&results_per_page=50&max_days_old={}").format(
                       az["app_id"], az["app_key"], urllib.parse.quote(q),
                       int(az.get("max_days_old", 2)))
            tasks.append({"source": "adzuna", "label": _slug(q), "url": url})

    if config.get("watchlist_enabled", True):
        for entry in config.get("watchlist", []):
            ats, token = entry.get("ats"), entry.get("token")
            url = board_url(ats, token)
            if url:
                tasks.append({"source": ats, "label": token, "url": url,
                              "company": entry.get("company", token)})

    for t in tasks:
        t["filename"] = "{}__{}.json".format(t["source"], t["label"])
    return tasks


def _load_task_payload(task, input_dir):
    """In --input-dir mode read the saved file; else hit the live API."""
    if input_dir:
        path = os.path.join(input_dir, task["filename"])
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return _http_get_json(task["url"])


# --------------------------------------------------------------------------- #
# Role-title gating
# --------------------------------------------------------------------------- #
def detect_level(title, levels):
    """Return the most-preferred configured level word found in the title.
    `levels` is ordered most-preferred-first. Recognizes 'sr'/'sr.' as
    'senior' when 'senior' is a configured level."""
    t = (title or "").lower()
    for lvl in levels:
        if lvl.lower() in t:
            return lvl.lower()
    if "senior" in [l.lower() for l in levels] and re.search(r"\bsr\.?\b", t):
        return "senior"
    return ""


def _default_title_matches(title, criteria):
    """Fallback matcher when no role_title_regex is configured: a title matches
    if it contains a role keyword (and, if require_level, a level word)."""
    t = (title or "").lower()
    roles = _terms(criteria, "role_keywords")
    if not roles:
        return False  # nothing configured -> match nothing (safer)
    if not any(r in t for r in roles):
        return False
    if criteria.get("require_level") and _terms(criteria, "levels"):
        if not any(l in t for l in _terms(criteria, "levels")):
            return False
    return True


def role_decision(title, comp_max, criteria, leveled_matcher):
    """Decide whether a posting passes the role-title gate. Two ways to pass:

      1. LEVELED (or whatever the configured role regex / matcher accepts —
         e.g. a player/coach manager or a design lead): always passes,
         regardless of comp. Comp still affects score and the sub-floor drop.
      2. UNLEVELED bare role title with no level word: only passes when
         criteria.allow_unleveled_if_comp_ok is on AND comp_max is KNOWN and
         >= comp_floor. Here comp is the seniority proxy: a bare-title role with
         unknown or sub-floor comp is dropped.

    Returns (passed: bool, mode: 'leveled'|'unleveled'|None, drop_reason: str).
    The "bare role" pattern is the first role_keyword, matched as a whole phrase.
    """
    if leveled_matcher(title):
        return True, "leveled", ""
    if criteria.get("allow_unleveled_if_comp_ok", False):
        roles = _terms(criteria, "role_keywords")
        t = (title or "").lower()
        if roles and any(r in t for r in roles):
            floor = criteria.get("comp_floor", 0) or 0
            if comp_max and floor and comp_max >= floor:
                return True, "unleveled", ""
            return False, None, ("unleveled-subfloor" if comp_max else "unleveled-no-comp")
    return False, None, "no-role-match"


# --------------------------------------------------------------------------- #
# Scoring (transparent, 0-100) — calibrated criteria.
# Domain is treated as NON-EXHAUSTIVE: a tier match is a BONUS, NO match is
# NEUTRAL (no penalty), and role-SHAPE signals (founding / first-hire / 0->1 /
# generalist) plus a right-shape baseline can carry a role over the deep-read
# bar with no domain match at all. Only exclude_keywords actually drop a domain.
# --------------------------------------------------------------------------- #
def score_posting(p, criteria):
    title = (p.get("title") or "")
    desc = (p.get("description") or "")
    hay = (title + " \n " + desc).lower()
    reasons = []
    score = 0
    levels = _terms(criteria, "levels")

    # --- Title relevance (0-35): seniority + role-keyword in title ---
    lvl = detect_level(title, levels)
    if lvl and levels:
        rank = levels.index(lvl) if lvl in levels else len(levels) - 1
        lvl_pts = max(12, 22 - rank * 3)  # earlier in list = more senior = more
    else:
        lvl_pts = 0
    role_pts = 13 if any(r in title.lower() for r in _terms(criteria, "role_keywords")) else 0
    score += min(35, lvl_pts + role_pts)
    if lvl:
        reasons.append("{} level".format(lvl))

    # --- Signal keywords (0-30): generic role-fit signals ---
    sig_hits = [kw for kw in criteria.get("signal_keywords", []) if kw.lower() in hay]
    score += min(30, len(sig_hits) * 8)
    if sig_hits:
        reasons.append("signals: " + ", ".join(sorted(set(sig_hits))[:4]))

    # --- Role-SHAPE signals: founding / first-hire / 0->1 / generalist breadth.
    # These describe the SHAPE of role the user most wants, independent of
    # DOMAIN. Stronger per-hit weight than generic signals, and a single hit is
    # enough to lift an otherwise right-shaped role over the deep-read bar with
    # no domain match. ---
    shape_per_hit = criteria.get("shape_signal_points", 14)
    shape_cap = criteria.get("shape_signal_cap", 24)
    shape_hits = [kw for kw in criteria.get("shape_signals", []) if kw.lower() in hay]
    score += min(shape_cap, len(shape_hits) * shape_per_hit)
    if shape_hits:
        reasons.append("role-shape (founding/first-hire/0->1): "
                       + ", ".join(sorted(set(shape_hits))[:3]))

    # --- Compensation (0-15) ---
    target = criteria.get("comp_target")
    floor = criteria.get("comp_floor")
    comp_max = p.get("comp_max")
    if comp_max and target:
        if comp_max >= target:
            score += 15
            reasons.append("comp >= ${:,}".format(target))
        elif floor and comp_max >= floor:
            score += 8
            reasons.append("comp near target")
        else:
            score += 3
    # unknown comp: 0 (no penalty, just no credit)

    # --- Location (0-10) ---
    bucket = location_bucket(p.get("location"), criteria)
    score += {"home": 10, "remote": 8, "ok": 6}.get(bucket, 0)
    if bucket == "home":
        reasons.append("home location")
    elif bucket == "remote":
        reasons.append("remote")

    # --- Domain fit: Tier 1 (+18) / Tier 2 (+9). NON-EXHAUSTIVE: a match is a
    # bonus, NO match is neutral. ---
    tier1 = [kw for kw in criteria.get("tier1_keywords", []) if kw.lower() in hay]
    tier2 = [kw for kw in criteria.get("tier2_keywords", []) if kw.lower() in hay]
    tier2 += [kw for kw in criteria.get("bonus_keywords", []) if kw.lower() in hay]
    if tier1:
        score += 18
        reasons.append("TIER-1 domain: " + ", ".join(sorted(set(tier1))[:3]))
    elif tier2:
        score += 9
        reasons.append("tier-2 domain: " + ", ".join(sorted(set(tier2))[:3]))

    # --- Manager/Head roles: only strong if player/coach; else downweight ---
    manager_only = False
    if re.search(r"\b(manager|head of|director)\b", title, re.I):
        cues = criteria.get("manager_player_coach_cues", [])
        if any(c.lower() in hay for c in cues):
            reasons.append("player/coach manager")
        else:
            score -= 12
            manager_only = True
            reasons.append("manager-only (downweighted)")

    # --- Right-shape baseline (domain-agnostic benefit-of-the-doubt) ---
    # A leveled IC role in an acceptable location with comp that isn't sub-floor
    # is the user's sweet spot REGARDLESS of domain. Because the domain list is
    # non-exhaustive, such a role must still clear the deep-read bar so the full
    # JD can make the real call. Give it a baseline. This is also the
    # "thin-card but right-shape" trigger: when a browser card is too thin to
    # carry a founding/0->1 signal in its text, level + location + comp alone
    # still lift it to deep-read. ---
    bump = criteria.get("shape_baseline_points", 0)
    ic_leveled = bool(lvl)
    good_loc = bucket in ("home", "remote", "ok")
    comp_not_subfloor = (comp_max is None) or (not floor) or (comp_max >= floor)
    if bump and ic_leveled and good_loc and comp_not_subfloor and not manager_only:
        score += bump
        if not tier1 and not tier2 and not shape_hits:
            reasons.append("right-shape IC, unlisted/unknown domain "
                           "— deep-read to confirm scope")
        else:
            reasons.append("right-shape IC fit")

    score = max(0, min(100, score))
    why = "; ".join(reasons) if reasons else "matched role criteria"
    return score, why


# --------------------------------------------------------------------------- #
# State (seen postings)
# --------------------------------------------------------------------------- #
def load_seen(seen_path):
    if not os.path.exists(seen_path):
        return set()
    try:
        with open(seen_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            return set(data.get("seen", []))
        if isinstance(data, list):
            return set(data)
    except Exception:
        pass
    return set()


def save_seen(seen, seen_path):
    with open(seen_path, "w", encoding="utf-8") as fh:
        json.dump({"seen": sorted(seen)}, fh, indent=2)


def seen_key(p):
    return p.get("url") or p.get("id")


def dupe_key(p):
    """Within-run cross-source dedupe: normalized title+company."""
    t = re.sub(r"\s+", " ", (p.get("title") or "").lower()).strip()
    c = re.sub(r"\s+", " ", (p.get("company") or "").lower()).strip()
    return "{}|{}".format(t, c)


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def run(config_path, seen_path, shortlist_path, dry_run=False, input_dir=None):
    with open(config_path, "r", encoding="utf-8") as fh:
        config = json.load(fh)
    criteria = config.get("criteria", {})
    # Comp parsing config (defaults preserve US/USD behavior). A non-US user sets
    # criteria.accept_currencies (e.g. ["GBP","£"]) and criteria.comp_band to the
    # plausible annual band in their currency.
    global COMP_BAND, ACCEPT_CURRENCIES
    band = criteria.get("comp_band")
    if isinstance(band, (list, tuple)) and len(band) == 2:
        try:
            COMP_BAND = (int(band[0]), int(band[1]))
        except (TypeError, ValueError):
            pass
    accept = criteria.get("accept_currencies")
    if accept:
        ACCEPT_CURRENCIES = {str(c).upper() for c in accept} | {""}
    cap = criteria.get("result_cap", 8)
    deep_read_threshold = criteria.get("deep_read_threshold", 50)

    # Incremental persistence: write phase artifacts next to shortlist_latest.json
    # so a mid-run drop is recoverable. phases/ is created if it doesn't exist.
    phases_dir = os.path.join(os.path.dirname(os.path.abspath(shortlist_path)), "phases")
    os.makedirs(phases_dir, exist_ok=True)

    def _write_phase(name, obj):
        try:
            path = os.path.join(phases_dir, name)
            with open(path, "w", encoding="utf-8") as _fh:
                json.dump(obj, _fh, indent=2)
        except Exception as _e:
            pass  # phase write failure must not abort the run

    seen = load_seen(seen_path)
    stats = {
        "sources_ok": [], "sources_failed": [],
        "per_source_fetched": {}, "per_source_surfaced": {},
        "total_postings": 0, "title_pass": 0, "loc_pass": 0,
        "excluded": 0, "subfloor_dropped": 0, "stale_dropped": 0,
        "new_after_dedupe": 0, "cross_source_dupes": 0,
        "unleveled_admitted": 0, "unleveled_dropped": 0,
    }
    candidates = []
    run_urls = set()
    run_dupes = set()

    tasks = build_fetch_tasks(config)

    # In --input-dir mode, also pick up extra {source}__{label}.json files
    # dropped in (browser pass: linkedin/wellfound/builtin/manual).
    # "builtin-<region>" regional keys (e.g. "builtin-co") route through
    # normalize_manual automatically — no explicit NORMALIZERS entry required.
    if input_dir and os.path.isdir(input_dir):
        existing = {t["filename"] for t in tasks}
        for fn in sorted(os.listdir(input_dir)):
            if not fn.endswith(".json") or "__" not in fn or fn in existing:
                continue
            src = fn.split("__", 1)[0]
            # Accept exact NORMALIZERS keys AND any "builtin-*" regional variant.
            normalizer_key = src if src in NORMALIZERS else (
                "builtin" if src.startswith("builtin-") else None)
            if normalizer_key:
                lbl = fn[len(src) + 2:-5]
                tasks.append({"source": src, "label": lbl, "filename": fn, "url": "",
                               "_normalizer": normalizer_key})

    exclude_kw = [k.lower() for k in criteria.get("exclude_keywords", [])]
    # Word-boundary match so short keywords don't fire as substrings inside
    # innocent words (e.g. "defi" matching "define/defined", "ai" inside
    # "again", "pm" inside "company"). Multi-word phrases keep their internal
    # spacing. Do NOT regress this to `k in hay` substring matching — it silently
    # drops good roles on incidental collisions.
    exclude_res = [re.compile(r"\b" + re.escape(k) + r"\b") for k in exclude_kw]
    require_roh = criteria.get("require_remote_or_home", False)
    home_terms = _terms(criteria, "home_terms")
    comp_floor = criteria.get("comp_floor")
    # Recency gate: drop rows older than this many days WHEN the source exposed a
    # parseable date. 0/None/negative disables the gate.
    try:
        max_age_days = float(criteria.get("max_age_days") or 0)
    except (TypeError, ValueError):
        max_age_days = 0
    stale_cutoff = (time.time() - max_age_days * 86400) if max_age_days > 0 else None
    cfg_role_re = None
    if criteria.get("role_title_regex"):
        try:
            cfg_role_re = re.compile(criteria["role_title_regex"], re.I)
        except re.error:
            cfg_role_re = None
    leveled_matcher = (lambda t: cfg_role_re.search(t or "") is not None) \
        if cfg_role_re is not None else (lambda t: _default_title_matches(t, criteria))

    for task in tasks:
        source = task["source"]
        label = task["label"]
        company_hint = task.get("company")
        # _normalizer is set for builtin-* regional keys to route through "builtin"
        normalizer_key = task.get("_normalizer", source)
        if normalizer_key not in NORMALIZERS:
            stats["sources_failed"].append("{}/{} (unknown source)".format(source, label))
            continue
        try:
            payload = _load_task_payload(task, input_dir)
            arg = company_hint if company_hint else label
            postings = NORMALIZERS[normalizer_key](payload, arg)
            stats["sources_ok"].append("{}/{}: {} postings".format(source, label, len(postings)))
            # Persist normalized rows for this source immediately (Change 3)
            _write_phase("normalized_{}__{}.json".format(
                re.sub(r"[^a-z0-9_-]", "-", source), re.sub(r"[^a-z0-9_-]", "-", label)),
                postings)
        except FileNotFoundError:
            stats["sources_failed"].append("{}/{}: no input file".format(source, label))
            continue
        except Exception as e:  # timeout / HTTP / parse — SKIP and continue (Change 3 hard rule)
            stats["sources_failed"].append("{}/{}: {}".format(source, label, str(e)[:80]))
            continue

        stats["total_postings"] += len(postings)
        stats["per_source_fetched"][source] = stats["per_source_fetched"].get(source, 0) + len(postings)

        for p in postings:
            title = p.get("title") or ""
            passed, mode, _drop = role_decision(
                title, p.get("comp_max"), criteria, leveled_matcher)
            if not passed:
                if _drop in ("unleveled-subfloor", "unleveled-no-comp"):
                    stats["unleveled_dropped"] += 1
                continue
            if mode == "unleveled":
                stats["unleveled_admitted"] += 1
            stats["title_pass"] += 1
            # US / location gate
            if not location_ok(p.get("location"), criteria):
                continue
            # Remote-or-home requirement
            if require_roh:
                loc_l = (p.get("location") or "").lower()
                is_remote = "remote" in loc_l or "worldwide" in loc_l or "anywhere" in loc_l
                is_home = any(tok in loc_l for tok in home_terms)
                if not is_remote and not is_home:
                    continue
            stats["loc_pass"] += 1
            # Hard-exclude domains
            hay_excl = (title + " \n " + (p.get("description") or "") + " \n " + (p.get("company") or "")).lower()
            if any(rx.search(hay_excl) for rx in exclude_res):
                stats["excluded"] += 1
                continue
            # Comp floor: only DROP rows that EXPLICITLY list sub-floor pay.
            cmax = p.get("comp_max")
            if comp_floor and cmax and cmax < comp_floor:
                stats["subfloor_dropped"] += 1
                continue
            # Recency gate: only DROP rows with a parseable date older than cutoff.
            if stale_cutoff is not None:
                pe = p.get("posted_epoch")
                if pe is not None and pe < stale_cutoff:
                    stats["stale_dropped"] += 1
                    continue
            if seen_key(p) in seen:
                continue
            if p.get("url") and p["url"] in run_urls:
                stats["cross_source_dupes"] += 1
                continue
            dk = dupe_key(p)
            if dk in run_dupes:
                stats["cross_source_dupes"] += 1
                continue
            run_urls.add(p.get("url"))
            run_dupes.add(dk)
            stats["new_after_dedupe"] += 1
            sc, why = score_posting(p, criteria)
            p["score"], p["why"], p["source"] = sc, why, source
            p["comp_display"] = p.get("comp_text") or "comp unknown"
            candidates.append(p)

    candidates.sort(key=lambda x: x["score"], reverse=True)
    # Persist scored candidates and deep-read queue immediately (Change 3)
    _write_phase("scored_candidates.json", [
        {"title": p["title"], "company": p["company"], "score": p["score"],
         "source": p.get("source"), "url": p.get("url"), "why": p.get("why")}
        for p in candidates
    ])
    _write_phase("deep_read_queue.json", [
        {"title": p["title"], "company": p["company"], "score": p["score"],
         "url": p.get("url"), "source": p.get("source")}
        for p in candidates if p["score"] > deep_read_threshold
    ])
    shortlist = candidates[:cap]

    if shortlist and not dry_run:
        for p in shortlist:
            seen.add(seen_key(p))
        save_seen(seen, seen_path)

    for p in shortlist:
        s = p.get("source", "?")
        stats["per_source_surfaced"][s] = stats["per_source_surfaced"].get(s, 0) + 1

    out = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "mode": "input-dir" if input_dir else "live",
        "deep_read_threshold": deep_read_threshold,
        "counts": {
            "total_postings_scanned": stats["total_postings"],
            "passed_title": stats["title_pass"],
            "passed_title_and_location": stats["loc_pass"],
            "excluded_by_domain": stats["excluded"],
            "dropped_subfloor_comp": stats["subfloor_dropped"],
            "dropped_stale": stats["stale_dropped"],
            "unleveled_admitted": stats["unleveled_admitted"],
            "unleveled_dropped_comp": stats["unleveled_dropped"],
            "cross_source_duplicates": stats["cross_source_dupes"],
            "new_after_dedupe": stats["new_after_dedupe"],
            "surfaced": len(shortlist),
        },
        "per_source_fetched": stats["per_source_fetched"],
        "per_source_surfaced": stats["per_source_surfaced"],
        "sources_ok": stats["sources_ok"],
        "sources_failed": stats["sources_failed"],
        "shortlist": [
            {
                "title": p["title"], "company": p["company"],
                "level": detect_level(p["title"], _terms(criteria, "levels")) or "n/a",
                "source": p.get("source", "?"),
                "comp": p["comp_display"], "location": p["location"] or "n/a",
                "score": p["score"],
                "deep_read": p["score"] > deep_read_threshold,
                "why": p["why"], "apply_url": p["url"], "id": p["id"],
            } for p in shortlist
        ],
    }
    with open(shortlist_path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
    # Also persist the final digest as a phase artifact (Change 3)
    _write_phase("digest_latest.json", out)

    print(render_markdown(out))
    return out


def render_markdown(out):
    c = out["counts"]
    thr = out.get("deep_read_threshold", 50)
    lines = ["## Job Scanner — {} new matching postings".format(c["surfaced"]), ""]
    lines.append("_Scanned {} postings · {} passed role · {} passed role+location · "
                 "{} excluded (domain) · {} dropped (sub-floor comp) · "
                 "{} dropped (stale) · {} cross-source dupes · {} new after dedupe._".format(
                     c["total_postings_scanned"], c["passed_title"],
                     c["passed_title_and_location"], c["excluded_by_domain"],
                     c["dropped_subfloor_comp"], c.get("dropped_stale", 0),
                     c["cross_source_duplicates"], c["new_after_dedupe"]))
    if out.get("per_source_fetched"):
        fetched = ", ".join("{}={}".format(k, v) for k, v in sorted(out["per_source_fetched"].items()))
        lines.append("")
        lines.append("_Fetched by source: {}._".format(fetched))
    if out.get("per_source_surfaced"):
        surf = ", ".join("{}={}".format(k, v) for k, v in sorted(out["per_source_surfaced"].items()))
        lines.append("_Surfaced by source: {}._".format(surf or "none"))
    lines.append("")
    lines.append("_Stage 2: deep-read the full JD for any role marked ⬇ DEEP-READ "
                 "(card score > {}); leave the rest at card level._".format(thr))
    lines.append("")
    if not out["shortlist"]:
        lines.append("No new matching postings.")
        return "\n".join(lines)
    for i, p in enumerate(out["shortlist"], 1):
        tag = "  ·  ⬇ DEEP-READ" if p.get("deep_read") else "  ·  (card-level only)"
        lines.append("**{}. {} — {}**  ·  _{}_  ·  via {}  ·  score {}{}".format(
            i, p["title"], p["company"], p["level"], p["source"], p["score"], tag))
        lines.append("   {}  ·  {}".format(p["comp"], p["location"]))
        lines.append("   Why it fits: {}".format(p["why"]))
        lines.append("   Apply: {}".format(p["apply_url"]))
        lines.append("")
    return "\n".join(lines)


def print_urls(config_path):
    """Print one line per fetch task: source<TAB>label<TAB>url. The unattended
    agent web_fetches each url and saves the JSON to
    <input-dir>/{source}__{label}.json, then runs again with --input-dir."""
    with open(config_path, "r", encoding="utf-8") as fh:
        config = json.load(fh)
    for task in build_fetch_tasks(config):
        print("{}\t{}\t{}".format(task["source"], task["label"], task["url"]))


def _arg(flag, default=None):
    if flag in sys.argv:
        i = sys.argv.index(flag)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


if __name__ == "__main__":
    config_path = _arg("--config", os.environ.get("JOB_SCANNER_CONFIG",
                       os.path.join(HERE, "scanner_config.json")))
    seen_path = _arg("--seen", os.environ.get("JOB_SCANNER_SEEN",
                     os.path.join(os.path.dirname(config_path), "seen_postings.json")))
    shortlist_path = _arg("--shortlist", os.environ.get("JOB_SCANNER_SHORTLIST",
                          os.path.join(os.path.dirname(config_path), "shortlist_latest.json")))

    if "--print-urls" in sys.argv:
        print_urls(config_path)
        sys.exit(0)
    input_dir = None
    if "--input-dir" in sys.argv:
        input_dir = _arg("--input-dir")
    elif os.environ.get("JOB_SCANNER_FIXTURES"):
        input_dir = os.environ["JOB_SCANNER_FIXTURES"]
    run(config_path, seen_path, shortlist_path,
        dry_run=("--dry-run" in sys.argv), input_dir=input_dir)
