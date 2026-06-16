#!/usr/bin/env python3
"""
selfcheck.py — verify an open-to-work install is healthy before you rely on it.

Run this after installing the skill, after editing any script, or whenever a run
fails in a confusing way. It does three things:

  1. COMPILE  — byte-compiles every bundled script so a syntax error surfaces
                here, not mid-pipeline.
  2. DEPS     — reports which runtime dependencies are present:
                  • python-docx   (required to build DOCX)   — hard
                  • LibreOffice   (soffice/libreoffice)      — hard for PDF export
                  • poppler       (pdfinfo / pdftotext)      — used by the page
                                   check + ATS text extraction (pypdf is a fallback)
                  • pypdf         (fallback page count / text)— soft
  3. LOGIC    — runs job_scanner against a tiny in-memory fixture and asserts the
                two behaviors most likely to silently regress:
                  • a strong role surfaces and is flagged deep_read=true;
                  • exclude_keywords match on WORD BOUNDARIES — a posting whose
                    text merely contains "define" is NOT dropped by exclude
                    ["defi"]; a posting that really mentions "defi" IS dropped.

Exit code 0 if all hard checks pass (soft/dep warnings don't fail the run);
non-zero if a script won't compile or the scanner logic is wrong.

Usage:
    python3 scripts/selfcheck.py
"""
import contextlib
import importlib.util
import io
import json
import os
import py_compile
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

OK, WARN, FAIL = "  ok ", " warn", "FAIL "
_failed = False


def line(status, msg):
    print("[{}] {}".format(status, msg))


def mark_fail(msg):
    global _failed
    _failed = True
    line(FAIL, msg)


# --- 1. COMPILE ------------------------------------------------------------- #
def check_compile():
    print("\n— compile —")
    for fn in sorted(os.listdir(HERE)):
        if fn.endswith(".py"):
            path = os.path.join(HERE, fn)
            try:
                py_compile.compile(path, doraise=True)
                line(OK, fn)
            except py_compile.PyCompileError as e:
                mark_fail("{}: {}".format(fn, str(e).splitlines()[-1]))


# --- 2. DEPS ---------------------------------------------------------------- #
def check_deps():
    print("\n— dependencies —")
    if importlib.util.find_spec("docx"):
        line(OK, "python-docx (DOCX builder)")
    else:
        line(WARN, "python-docx MISSING — resume/cover-letter DOCX will fail. `pip install python-docx`")
    if shutil.which("soffice") or shutil.which("libreoffice"):
        line(OK, "LibreOffice (PDF export)")
    else:
        line(WARN, "LibreOffice MISSING — PDF export will fail. Install LibreOffice.")
    have_pdfinfo = bool(shutil.which("pdfinfo"))
    have_pdftotext = bool(shutil.which("pdftotext"))
    if have_pdfinfo and have_pdftotext:
        line(OK, "poppler (pdfinfo + pdftotext)")
    else:
        missing = ", ".join(n for n, ok in
                            (("pdfinfo", have_pdfinfo), ("pdftotext", have_pdftotext)) if not ok)
        if importlib.util.find_spec("pypdf"):
            line(WARN, "poppler partial/missing ({}) — pypdf fallback present, page check still works".format(missing))
        else:
            line(WARN, "poppler MISSING ({}) and no pypdf fallback — page check + ATS text extraction degrade. "
                       "Install poppler (brew install poppler / apt-get install poppler-utils) or `pip install pypdf`".format(missing))


# --- 3. LOGIC --------------------------------------------------------------- #
def _import_scanner():
    spec = importlib.util.spec_from_file_location("job_scanner", os.path.join(HERE, "job_scanner.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check_scanner_logic():
    print("\n— scanner logic —")
    try:
        js = _import_scanner()
    except Exception as e:
        mark_fail("could not import job_scanner.py: {}".format(e))
        return

    criteria = {
        "role_title_regex": r"(senior|staff|principal|lead).*(product design|design)",
        "levels": ["principal", "staff", "lead", "senior"],
        "locations": ["United States", "Remote US"],
        "us_only": True,
        "comp_target": 180000, "comp_floor": 150000,
        "signal_keywords": ["design system"],
        "tier1_keywords": ["design system"],
        "shape_signals": ["0 to 1", "founding"],
        "exclude_keywords": ["defi"],   # crypto hard-no — must NOT match "define"
        "deep_read_threshold": 50,
        "result_cap": 8,
    }
    good = {"id": 1, "company_name": "Acme", "title": "Senior Product Designer",
            "candidate_required_location": "USA", "url": "https://acme.test/1",
            "description": "You will define the design system and own 0 to 1 work. $180,000-$210,000",
            "salary": "$180,000-$210,000", "publication_date": "2026-06-13T10:00:00"}
    crypto = {"id": 2, "company_name": "CoinCo", "title": "Senior Product Designer",
              "candidate_required_location": "USA", "url": "https://coin.test/2",
              "description": "Design our DeFi exchange. We live and breathe defi.",
              "publication_date": "2026-06-13T10:00:00"}

    with tempfile.TemporaryDirectory() as d:
        cfg = os.path.join(d, "config.json")
        fetched = os.path.join(d, "fetched")
        os.makedirs(fetched)
        json.dump({"discovery_sources": {"remotive": {"enabled": True, "queries": ["x"]},
                                         "remoteok": {"enabled": False}, "arbeitnow": {"enabled": False},
                                         "jobicy": {"enabled": False}},
                   "watchlist_enabled": False, "criteria": criteria}, open(cfg, "w"))
        json.dump({"jobs": [good, crypto]}, open(os.path.join(fetched, "remotive__x.json"), "w"))
        with contextlib.redirect_stdout(io.StringIO()):  # swallow the scanner's own markdown
            out = js.run(cfg, os.path.join(d, "seen.json"), os.path.join(d, "sl.json"),
                         dry_run=True, input_dir=fetched)

    titles = {p["company"]: p for p in out["shortlist"]}
    if "Acme" in titles:
        line(OK, "strong role surfaced (the 'define' posting was NOT dropped by exclude ['defi'])")
        if titles["Acme"].get("deep_read"):
            line(OK, "strong role flagged deep_read=true (score {})".format(titles["Acme"]["score"]))
        else:
            mark_fail("strong role surfaced but deep_read=false — scoring/threshold regression")
    else:
        mark_fail("WORD-BOUNDARY EXCLUDE REGRESSION: a posting containing 'define' was dropped by "
                  "exclude ['defi']. job_scanner must use regex \\bword\\b, not substring matching.")
    if "CoinCo" not in titles:
        line(OK, "genuine 'defi' posting correctly excluded")
    else:
        mark_fail("crypto posting that really mentions 'defi' was NOT excluded — exclude gate broken")


if __name__ == "__main__":
    print("open-to-work selfcheck")
    check_compile()
    check_deps()
    check_scanner_logic()
    print("\n" + ("SELFCHECK FAILED — fix the FAIL lines above." if _failed
                  else "SELFCHECK PASSED — compile + scanner logic OK (heed any 'warn' deps)."))
    sys.exit(1 if _failed else 0)
