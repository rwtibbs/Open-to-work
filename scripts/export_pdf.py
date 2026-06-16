#!/usr/bin/env python3
"""
export_pdf.py — Deterministic DOCX -> PDF export via LibreOffice headless.

This is the sanctioned way to produce the PDF for a generated resume or cover
letter. LibreOffice (soffice) renders the .docx faithfully — same fonts, layout,
and links the recruiter will open. Do NOT reach for pypdf/reportlab/docx2pdf;
those re-render and drift from the Word file.

Usage:
    python export_pdf.py /path/to/Resume_<Name>_<Company>.docx
    python export_pdf.py <docx> --outdir /path/to/dir   # defaults to docx's dir

Exit code 0 on success (prints the PDF path), non-zero on failure.
"""
import argparse
import os
import shutil
import subprocess
import sys


def find_soffice():
    for name in ("soffice", "libreoffice"):
        path = shutil.which(name)
        if path:
            return path
    mac = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
    if os.path.exists(mac):
        return mac
    return None


def export(docx_path, outdir=None):
    docx_path = os.path.abspath(docx_path)
    if not os.path.exists(docx_path):
        print(f"ERROR: docx not found: {docx_path}", file=sys.stderr)
        return None
    outdir = os.path.abspath(outdir) if outdir else os.path.dirname(docx_path)

    soffice = find_soffice()
    if not soffice:
        print("ERROR: LibreOffice (soffice/libreoffice) not found on PATH.", file=sys.stderr)
        return None

    pdf_path = os.path.join(
        outdir, os.path.splitext(os.path.basename(docx_path))[0] + ".pdf"
    )

    # Two attempts: LibreOffice headless can no-op on the first cold start.
    for _ in range(2):
        subprocess.run(
            [soffice, "--headless", "--convert-to", "pdf", "--outdir", outdir, docx_path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        if os.path.exists(pdf_path):
            print(pdf_path)
            return pdf_path
    print(f"ERROR: conversion produced no PDF at {pdf_path}", file=sys.stderr)
    return None


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Convert a .docx to .pdf via LibreOffice")
    ap.add_argument("docx")
    ap.add_argument("--outdir", default=None)
    args = ap.parse_args()
    result = export(args.docx, args.outdir)
    sys.exit(0 if result else 1)
