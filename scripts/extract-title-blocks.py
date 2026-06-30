#!/usr/bin/env python3
"""
extract-title-blocks.py — Extract the title block (masthead region) of every
guide page into a structured JSON, for the title-block standardization task.

For each guides/**/*.html it captures the raw "current" state of:
  - <title> tag text
  - breadcrumb current crumb
  - masthead .kicker (full inner HTML + split label parts)
  - masthead h1.title (lead text, accent <span> word, .role tag)
  - masthead p.subtitle (if any)
  - masthead-meta spans (label/value pairs, with the Updated date pulled out)

Output: scripts/out/title-blocks.json  (one object per page, ordered)
Run:    python3 scripts/extract-title-blocks.py
Paths resolve relative to the repo root regardless of CWD.
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GUIDES = REPO / "guides"
OUT = REPO / "scripts" / "out"


def group_of(rel: str) -> str:
    if rel == "guides/index.html":
        return "index"
    if rel.startswith("guides/engineering/"):
        return "engineering"
    if rel.startswith("guides/systems/"):
        return "systems"
    if rel.startswith("guides/ships/dossiers/"):
        return "dossier"
    if rel.startswith("guides/ships/by-role/"):
        return "by-role"
    if rel.startswith("guides/ships/"):
        return "ships"
    if rel.startswith("guides/activities/"):
        return "activities"
    return "other"


def strip_tags(s: str) -> str:
    """Collapse a fragment of inner HTML to its visible text (entities kept raw)."""
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def first(pattern, text, flags=re.S):
    m = re.search(pattern, text, flags)
    return m.group(1) if m else None


def extract(path: Path) -> dict:
    rel = path.relative_to(REPO).as_posix()
    html = path.read_text(encoding="utf-8", errors="replace")

    row = {"file": rel, "group": group_of(rel)}

    # <title>
    row["title_tag"] = (first(r"<title>(.*?)</title>", html) or "").strip()

    # breadcrumb current
    crumb = first(r'<span class="current"[^>]*>(.*?)</span>', html)
    row["breadcrumb_current"] = strip_tags(crumb) if crumb else ""

    # Isolate the masthead block
    mast = first(r'<header class="masthead">(.*?)</header>', html)
    if not mast:
        row["_no_masthead"] = True
        return row

    # kicker — full inner HTML + split parts (on the // separator span)
    kicker_html = first(r'<div class="kicker">(.*?)</div>', mast)
    row["kicker_raw"] = kicker_html.strip() if kicker_html else ""
    if kicker_html is not None:
        # split on a <span class="sep">...</span> (the // divider)
        parts = re.split(r'<span class="sep">.*?</span>', kicker_html)
        parts = [strip_tags(p) for p in parts]
        parts = [p for p in parts if p]
        row["kicker_parts"] = parts
    else:
        row["kicker_parts"] = []

    # h1.title — lead text (before first <span>), first <span> accent word, .role tag
    h1 = first(r'<h1 class="title">(.*?)</h1>', mast)
    row["h1_raw"] = h1.strip() if h1 else ""
    if h1:
        role = first(r'<span class="role">(.*?)</span>', h1)
        row["h1_role"] = strip_tags(role) if role else ""
        # accent span = first <span> that is NOT the role span
        accent = ""
        for m in re.finditer(r'<span(?![^>]*class="role")[^>]*>(.*?)</span>', h1):
            accent = strip_tags(m.group(1))
            break
        row["h1_accent"] = accent
        # lead = text before the first <span> of any kind
        lead = re.split(r"<span", h1, 1)[0]
        row["h1_lead"] = strip_tags(lead)
        # trailing/middle plain text (e.g. "Run" in "The <span>Unlock</span> Run <role>")
        row["h1_text_all"] = strip_tags(h1)
    else:
        row["h1_role"] = row["h1_accent"] = row["h1_lead"] = row["h1_text_all"] = ""

    # subtitle
    sub = first(r'<p class="subtitle">(.*?)</p>', mast)
    row["subtitle"] = sub.strip() if sub else ""

    # masthead-meta spans
    meta_block = first(r'<div class="masthead-meta">(.*?)</div>', mast)
    metas = []
    if meta_block:
        for m in re.finditer(r"<span>(.*?)</span>", meta_block, re.S):
            metas.append(strip_tags(m.group(1)))
    row["meta_spans"] = metas
    row["meta_count"] = len(metas)
    # pull the Updated date out of whichever span carries it
    upd = ""
    for m in metas:
        mm = re.search(r"Updated\s+(\S+)", m)
        if mm:
            upd = mm.group(1)
            break
    row["updated_date"] = upd
    # meta[0] is typically the type/series label
    row["meta_label"] = metas[0] if metas else ""

    return row


def main():
    files = sorted(GUIDES.rglob("*.html"))
    rows = [extract(f) for f in files]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "title-blocks.json").write_text(
        json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # sanity check
    by_group = {}
    no_mast = [r["file"] for r in rows if r.get("_no_masthead")]
    for r in rows:
        by_group[r["group"]] = by_group.get(r["group"], 0) + 1
    print(f"Extracted {len(rows)} pages -> scripts/out/title-blocks.json")
    for g in sorted(by_group):
        print(f"  {g:12} {by_group[g]}")
    if no_mast:
        print(f"  WARNING: {len(no_mast)} pages with no masthead:")
        for f in no_mast:
            print(f"    {f}")


if __name__ == "__main__":
    sys.exit(main())
