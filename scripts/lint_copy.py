#!/usr/bin/env python3
"""
lint_copy.py — advisory checks for the prose this kit writes and the resume it
builds. ADVISORY, not a gate: it surfaces likely problems for a human (or the
agent) to judge — it never rewrites, and a clean exit is not a guarantee of good
writing. The real standard lives in references/writing-standards.md and the
user's voice.md; this just catches the mechanical tells that slip through.

Two modes:

  prose <file.md|->   Scan a cover letter / outreach note / application answers
                      for the STRUCTURAL AI tells from writing-standards.md
                      (false-negative "not X, it's Y", rhetorical-question
                      transitions, staccato fragment runs, empty-intensifier
                      openers, asyndeton, em-dash overuse, known AI-tell words).
                      Reads stdin if the file is "-".

  parse <resume.pdf> [--expect STR ...]
                      ATS parse-safety: extract the PDF's text the way a parser
                      would (pdftotext, else pypdf) and confirm each --expect
                      string survives extraction in readable order. Catches the
                      classic failure where a styled header (e.g. a logo table)
                      renders fine but extracts garbled or out of order.

Exit code is 0 when nothing flagged, 1 when there are findings (so a caller can
choose to surface them) — but treat it as advisory either way.

Usage:
    python3 scripts/lint_copy.py prose CoverLetter_Jane_Acme.md
    python3 scripts/lint_copy.py parse Resume_Jane_Acme.pdf --expect "Jane Doe" "EXPERIENCE" "SKILLS"
"""
import argparse
import re
import shutil
import subprocess
import sys

# (regex, label) — conservative, high-signal patterns. Case-insensitive.
PROSE_TELLS = [
    (r"\b(?:isn'?t|wasn'?t|aren'?t|not)\b[^.?!\n]{1,60}?,?\s+it'?s\b",
     "false-negative setup ('not X, it's Y') — state the thing directly"),
    (r"(?:^|[.!?]\s+)(?:the result|the catch|the kicker|the best part|why does this matter|so what'?s the (?:point|catch))\?\s",
     "rhetorical-question transition — just make the statement"),
    (r"\b(?:here'?s the thing|what if i told you|let that sink in|make no mistake|here'?s the kicker)\b",
     "empty-intensifier opener — delete the runway, start at the point"),
    (r"\b(?:delve|tapestry|testament to|seamlessly|in today'?s world|navigating the landscape|ever-evolving|it'?s worth noting|not only\b[^.\n]{0,40}\bbut also)\b",
     "known AI-tell word/phrase — cut on sight"),
    (r"\bno\s+\w+,\s*no\s+\w+,\s*no\s+\w+\b",
     "asyndeton ('no X, no Y, no Z') — write it as a normal sentence"),
]


def lint_prose(text):
    findings = []
    for rx, label in PROSE_TELLS:
        for m in re.finditer(rx, text, re.I | re.M):
            ln = text.count("\n", 0, m.start()) + 1
            snippet = re.sub(r"\s+", " ", m.group(0)).strip()[:70]
            findings.append((ln, label, snippet))

    # staccato run: 3+ consecutive ultra-short sentences/fragments (<=4 words)
    sentences = re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text).strip())
    run = []
    for s in sentences:
        wc = len(s.split())
        if 0 < wc <= 4:
            run.append(s)
            if len(run) == 3:
                findings.append((0, "staccato fragment run (3+ ultra-short sentences) — let clauses flow",
                                 " / ".join(run)[:70]))
        else:
            run = []

    # em-dash density
    dashes = text.count("—")
    words = max(1, len(text.split()))
    if dashes >= 4 and dashes / words > 0.012:
        findings.append((0, "em-dash overuse ({} in {} words) — vary the punctuation per voice.md".format(dashes, words), ""))

    return sorted(findings, key=lambda f: f[0])


def extract_pdf_text(pdf_path):
    if shutil.which("pdftotext"):
        return subprocess.run(["pdftotext", "-layout", pdf_path, "-"],
                              capture_output=True, text=True).stdout
    try:
        from pypdf import PdfReader
        return "\n".join((pg.extract_text() or "") for pg in PdfReader(pdf_path).pages)
    except Exception:
        return None


def lint_parse(pdf_path, expect):
    text = extract_pdf_text(pdf_path)
    if text is None:
        print("WARN: could not extract text (install poppler or pypdf to run the parse check)")
        return []
    norm = re.sub(r"\s+", " ", text).lower()
    missing = [s for s in expect if re.sub(r"\s+", " ", s).lower() not in norm]
    findings = []
    for s in missing:
        findings.append((0, "ATS parse-safety: expected text not found after extraction", s))
    # crude order check on the ones that are present
    present = [s for s in expect if s not in missing]
    positions = [norm.find(re.sub(r"\s+", " ", s).lower()) for s in present]
    if positions != sorted(positions):
        findings.append((0, "ATS parse-safety: --expect strings extracted OUT OF ORDER "
                            "(styled header/table may be scrambling parse order)", ""))
    return findings


def report(findings, what):
    if not findings:
        print("clean — no {} flagged (advisory).".format(what))
        return 0
    print("{} finding(s) — advisory, judge each:".format(len(findings)))
    for ln, label, snippet in findings:
        loc = "L{}".format(ln) if ln else " · "
        print("  [{}] {}{}".format(loc, label, "  →  \"{}\"".format(snippet) if snippet else ""))
    return 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Advisory prose / parse-safety linter")
    sub = ap.add_subparsers(dest="mode", required=True)
    pp = sub.add_parser("prose", help="scan a prose file for structural AI tells")
    pp.add_argument("file", help="markdown/text file, or - for stdin")
    pa = sub.add_parser("parse", help="ATS parse-safety check on a resume PDF")
    pa.add_argument("pdf")
    pa.add_argument("--expect", nargs="*", default=[],
                    help="strings that must survive text extraction in order (name, section headers)")
    args = ap.parse_args()

    if args.mode == "prose":
        text = sys.stdin.read() if args.file == "-" else open(args.file, encoding="utf-8").read()
        sys.exit(report(lint_prose(text), "tells"))
    else:
        sys.exit(report(lint_parse(args.pdf, args.expect), "parse issues"))
