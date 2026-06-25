#!/usr/bin/env python3
"""
apply-title-blocks.py — Apply standardized title blocks to guide pages from the
reviewed workbook export (scripts/out/edited-rows.json).

Element-TARGETED and idempotent: for each page it rewrites ONLY the masthead
elements whose target differs from what's live in the file (the <title>, the
.kicker, the h1.title, a dropped p.subtitle, the .masthead-meta). Anything not
modelled by the workbook columns — e.g. an h1 with middle text the user didn't
touch — is preserved verbatim. Re-running makes no further changes.

Built-in corrections applied to the workbook data:
  - dates normalized to the site's ISO YYYY-MM-DD (Excel exports M/D/YYYY)
  - checklist.html "Unlock Chestlist" typo -> "Unlock Checklist"
  - meta label keyword bolded house-style: "Series Ships" -> "Series <b>Ships</b>"

Usage:
  python3 scripts/apply-title-blocks.py [--files a.html b.html ...] [--dry-run]
  (no --files = every page whose target differs from current)

Paths resolve relative to the repo root. Prints a per-file element report.
"""
import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "scripts" / "out" / "edited-rows.json"

ELEM = ['page_name','title_suffix','title_full','kicker_a','kicker_b',
        'h1_lead','h1_accent','h1_role','subtitle','meta_label','meta_updated']


def norm_date(s):
    s = (s or "").strip()
    m = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})$', s)          # M/D/YYYY
    if m:
        mo, d, y = m.groups()
        return f"{y}-{int(mo):02d}-{int(d):02d}"
    m = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2})$', s)          # already ISO
    if m:
        y, mo, d = m.groups()
        return f"{y}-{int(mo):02d}-{int(d):02d}"
    return s


def bold_label(label):
    """House style: bold the keyword. 'Series Ships' -> 'Series <b>Ships</b>'.
    Labels that already carry their own <b> (e.g. the index count) pass through."""
    label = (label or "").strip()
    if "<b>" in label:
        return label
    m = re.match(r'(Series)\s+(.+)$', label)
    if m:
        return f"{m.group(1)} <b>{m.group(2)}</b>"
    return label


def esc_amp(s):
    """Escape bare ampersands to &amp; while leaving real entities (&amp; &times;
    &middot; &ndash; &#39; …) intact — the workbook cells mix both."""
    return re.sub(r'&(?!#?\w+;)', '&amp;', s or "")


def correct(row):
    """Apply built-in data corrections to a row's NEW values; return a clean dict."""
    n = {k: ("" if row['new'][k] is None else str(row['new'][k])).strip() for k in ELEM}
    f = row['file']
    if f.endswith("engineering/checklist.html"):
        n['page_name'] = n['page_name'].replace("Chestlist", "Checklist")
        n['kicker_b'] = n['kicker_b'].replace("Chestlist", "Checklist")
    n['meta_updated'] = norm_date(n['meta_updated'])
    # normalize bare ampersands in every inserted text field (keeps valid HTML)
    for k in ['page_name','title_suffix','kicker_a','kicker_b','h1_lead','h1_accent','h1_role','meta_label']:
        n[k] = esc_amp(n[k])
    # title_full is rebuilt from the (corrected) components so the typo/format fixes flow through
    if n['title_suffix']:
        n['title_full'] = f"{n['page_name']} &middot; {n['title_suffix']} | E:D Black Box"
    else:
        n['title_full'] = f"{n['page_name']} | E:D Black Box"
    return n


def build_kicker(a, b):
    if b:
        return f'<div class="kicker">{a} <span class="sep">//</span> {b}</div>'
    return f'<div class="kicker">{a}</div>'


def build_h1(lead, accent, role, cur_h1_raw):
    # preserve the file's existing accent->role spacing (dossiers are adjacent,
    # engineering/systems use a space); default to a space when adding a role span.
    m = re.search(r'</span>(\s*)<span class="role"', cur_h1_raw or "")
    role_sep = m.group(1) if m else " "
    s = ""
    if lead:
        s += f"{lead} "
    s += f"<span>{accent}</span>"
    if role:
        s += f"{role_sep}<span class=\"role\">{role}</span>"
    return f'<h1 class="title">{s}</h1>'


def build_meta(indent, label, date):
    i2 = indent + "  "
    return (f'<div class="masthead-meta">\n'
            f'{i2}<span>{bold_label(label)}</span>\n'
            f'{i2}<span>Updated <b>{date}</b></span>\n'
            f'{indent}</div>')


def apply_page(path: Path, cur: dict, n: dict, dry: bool):
    html = path.read_text(encoding="utf-8")
    orig = html
    changed = []

    mast_m = re.search(r'(<header class="masthead">)(.*?)(</header>)', html, re.S)
    if not mast_m:
        return ["NO MASTHEAD"], False
    head, inner, tail = mast_m.group(1), mast_m.group(2), mast_m.group(3)

    # --- <title> (lives in <head>, replace globally) ---
    new_title = f"<title>{n['title_full']}</title>"
    cur_title_m = re.search(r'<title>.*?</title>', html)
    if cur_title_m and cur_title_m.group(0) != new_title:
        html = html[:cur_title_m.start()] + new_title + html[cur_title_m.end():]
        changed.append("title")
        # masthead match indices shift if title precedes it (it does); recompute below
        mast_m = re.search(r'(<header class="masthead">)(.*?)(</header>)', html, re.S)
        head, inner, tail = mast_m.group(1), mast_m.group(2), mast_m.group(3)

    new_inner = inner

    # --- kicker ---
    kick_m = re.search(r'<div class="kicker">.*?</div>', new_inner, re.S)
    if kick_m:
        target = build_kicker(n['kicker_a'], n['kicker_b'])
        if kick_m.group(0) != target:
            new_inner = new_inner[:kick_m.start()] + target + new_inner[kick_m.end():]
            changed.append("kicker")

    # --- h1 (only if a user-modelled h1 field changed) ---
    h1_changed = (cur['h1_lead'], cur['h1_accent'], cur['h1_role']) != \
                 (n['h1_lead'], n['h1_accent'], n['h1_role'])
    h1_m = re.search(r'<h1 class="title">.*?</h1>', new_inner, re.S)
    if h1_changed and h1_m:
        target = build_h1(n['h1_lead'], n['h1_accent'], n['h1_role'], h1_m.group(0))
        if h1_m.group(0) != target:
            new_inner = new_inner[:h1_m.start()] + target + new_inner[h1_m.end():]
            changed.append("h1")

    # --- subtitle drop ---
    if not n['subtitle'].strip():
        sub_m = re.search(r'\n?[ \t]*<p class="subtitle">.*?</p>', new_inner, re.S)
        if sub_m:
            new_inner = new_inner[:sub_m.start()] + new_inner[sub_m.end():]
            changed.append("subtitle-removed")

    # --- masthead-meta ---
    meta_m = re.search(r'([ \t]*)<div class="masthead-meta">.*?</div>', new_inner, re.S)
    if meta_m:
        indent = meta_m.group(1)
        target = indent + build_meta(indent, n['meta_label'], n['meta_updated'])
        if meta_m.group(0) != target:
            new_inner = new_inner[:meta_m.start()] + target + new_inner[meta_m.end():]
            changed.append("meta")

    if new_inner != inner:
        html = html[:mast_m.start()] + head + new_inner + tail + html[mast_m.end():]

    if html != orig and not dry:
        path.write_text(html, encoding="utf-8")
    return changed, (html != orig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", nargs="*", default=None)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    rows = {r['file']: r for r in json.loads(DATA.read_text(encoding="utf-8"))}
    targets = a.files if a.files else list(rows.keys())

    n_files = n_writes = 0
    for f in targets:
        f = f.replace(str(REPO) + "/", "")
        if f not in rows:
            print(f"  ?? not in workbook: {f}")
            continue
        cur = {k: ("" if rows[f]['cur'][k] is None else str(rows[f]['cur'][k])).strip() for k in ELEM}
        n = correct(rows[f])
        changed, wrote = apply_page(REPO / f, cur, n, a.dry_run)
        n_files += 1
        n_writes += 1 if wrote else 0
        tag = "DRY " if a.dry_run else ("WROTE" if wrote else "noop ")
        print(f"  {tag} {f:52} {changed}")
    print(f"\n{'(dry-run) ' if a.dry_run else ''}{n_files} files processed, {n_writes} written")


if __name__ == "__main__":
    main()
