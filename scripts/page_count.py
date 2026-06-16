#!/usr/bin/env python3
"""
page_count.py — Deterministic page-length check for a resume PDF.

A resume should fit a target length — one page for most roles, but some fields
(academic CV, federal, senior/technical) legitimately run longer. Judging that
by eye from a render is unreliable, so this reads the real page count and, when
the resume spills past the target, prints the text that landed on the overflow
pages so the caller knows exactly what to trim.

The target defaults to 1 page but is configurable: pass --max-pages N, or let the
RUN step read it from the user's format.json ("max_pages": N) and pass it through.

Usage:
    python page_count.py /path/to/Resume_<Name>_<Company>.pdf
    python page_count.py <pdf> --max-pages 2

Output:
    PAGES: <n>
    (if over target) a "=== OVERFLOW (page N+) ===" block with the spilled text

Exit code 0 if the PDF is within the target page count, 1 otherwise (so it can
gate a loop).
"""
import argparse
import re
import shutil
import subprocess
import sys


def page_count(pdf_path):
    if shutil.which("pdfinfo"):
        out = subprocess.run(["pdfinfo", pdf_path], capture_output=True, text=True).stdout
        m = re.search(r"Pages:\s*(\d+)", out)
        if m:
            return int(m.group(1))
    try:
        from pypdf import PdfReader
        return len(PdfReader(pdf_path).pages)
    except Exception:
        return None


def overflow_text(pdf_path, first_overflow_page):
    """Text from first_overflow_page onward. Prefer pdftotext (poppler); fall
    back to pypdf so the 'what spilled' hint still works without poppler."""
    if shutil.which("pdftotext"):
        return subprocess.run(
            ["pdftotext", "-f", str(first_overflow_page), pdf_path, "-"],
            capture_output=True, text=True,
        ).stdout.strip()
    try:
        from pypdf import PdfReader
        pages = PdfReader(pdf_path).pages
        chunks = [pages[i].extract_text() or "" for i in range(first_overflow_page - 1, len(pages))]
        return "\n".join(chunks).strip()
    except Exception:
        return ""


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Check that a resume PDF fits a page target")
    ap.add_argument("pdf")
    ap.add_argument("--max-pages", type=int, default=1,
                    help="Target page count (default 1; read from format.json max_pages for longer-format fields)")
    args = ap.parse_args()
    target = max(1, args.max_pages)

    n = page_count(args.pdf)
    if n is None:
        print("ERROR: could not determine page count", file=sys.stderr)
        sys.exit(2)

    print(f"PAGES: {n}")
    if n <= target:
        sys.exit(0)

    spill = overflow_text(args.pdf, target + 1)
    if spill:
        print(f"\n=== OVERFLOW (page {target + 1}+) ===")
        print(spill)
    sys.exit(1)
