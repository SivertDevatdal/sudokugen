"""pdfs/index.json — the list of downloadable days for the website.

The download page (web/index.html) reads this file to know which days
have a PDF and why the other days have none (Sunday, a holiday, ...),
so the holiday rules only live in publishing.py.
"""

from __future__ import annotations

import json
import os
import re
from datetime import date, timedelta

from .publishing import no_paper_reason

PDF_FILE = re.compile(r'^sudoku-(\d{4}-\d{2}-\d{2})\.pdf$')

# How far past the newest PDF the calendar still marks no-paper days.
LOOKAHEAD_DAYS = 120


def build_manifest(pdf_dir: str) -> dict:
    available = sorted(
        m.group(1) for name in os.listdir(pdf_dir)
        if (m := PDF_FILE.match(name)))
    no_paper = {}
    if available:
        day = date.fromisoformat(available[0])
        end = date.fromisoformat(available[-1]) + timedelta(days=LOOKAHEAD_DAYS)
        while day <= end:
            reason = no_paper_reason(day)
            if reason:
                no_paper[day.isoformat()] = reason
            day += timedelta(days=1)
    return {'available': available, 'noPaper': no_paper}


def write_manifest(pdf_dir: str) -> str:
    path = os.path.join(pdf_dir, 'index.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(build_manifest(pdf_dir), f, indent=1, ensure_ascii=False)
        f.write('\n')
    return path
