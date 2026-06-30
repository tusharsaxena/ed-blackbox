#!/usr/bin/env python3
"""sources_lib.py — shared parse/render helpers for the canonical Sources pipeline.

CANONICAL SOURCE: data/sources/<path-mirroring-guides>.json is the source of truth for
every page's bottom-of-page **Sources** block (`<section class="credits"
id="section-credits">`). The block is GENERATED from that data by build-sources.py — never
hand-edit the credits HTML.

This module is imported by extract-sources.py, build-sources.py and audit-sources.py. It
provides:
  - page_to_data_path() / data_to_page_path() — map between a guides/**.html page and its
    data/sources/**.json file (mirrored tree).
  - parse_credits(text) — pull (indent, sec_num, leads[], rows[]) out of a page's credits
    section. Returns None if the page has no credits section.
  - render_credits(indent, sec_num, leads, rows, eol) — emit the canonical credits markup.
  - replace_credits(text, new_block) — splice a freshly rendered block back into the page.
  - strip_internal_links(html) — unwrap inline <a href="#..."> / relative cross-links to
    plain text (the Sources section is external references only).

The Sources section is intentionally uniform across all pages (one cr-row per line); parsing
is line-based and the build owns the block's formatting (indent, tag order, target/rel).
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUIDES_DIR = ROOT / "guides"
DATA_DIR = ROOT / "data" / "sources"

SECTION_OPEN_RE = re.compile(
    r'^([ \t]*)<section class="credits" id="section-credits">\s*$'
)
SEC_HEAD_RE = re.compile(
    r'^<div class="sec-head"><span class="sec-num">(\d+)</span><h2>Sources</h2>'
    r'(?:<span class="tag">(.*?)</span>)?</div>$'
)
LEAD_RE = re.compile(r'^<p class="lead">(.*)</p>$')
ROW_RE = re.compile(
    r'^<div class="cr-row">'
    r'<span class="cr-src">(?P<label>.*?)</span>'
    r'<span class="cr-what">(?P<what>.*?)</span>'
    r'<a class="cr-link" href="(?P<url>.*?)" target="_blank" rel="noopener noreferrer">'
    r'(?P<display>.*?)</a>'
    r'</div>$'
)
# Inline anchors that are internal references (same-page #..., relative .html, ./ or ../).
INTERNAL_A_RE = re.compile(
    r'<a\s+href="(?:#[^"]*|\.{0,2}/[^"]*|[^":/]+\.html[^"]*)"[^>]*>(.*?)</a>',
    re.DOTALL,
)


# ----------------------------------------------------------------------------- path mapping
def page_to_data_path(page_path):
    """guides/systems/activity-guides/exploration.html -> data/sources/systems/activity-guides/exploration.json"""
    p = Path(page_path)
    rel = p.relative_to("guides") if p.parts and p.parts[0] == "guides" else \
        p.relative_to(GUIDES_DIR)
    return DATA_DIR / rel.with_suffix(".json")


def data_to_page_rel(data_path):
    """data/sources/systems/activity-guides/exploration.json -> guides/systems/activity-guides/exploration.html"""
    rel = Path(data_path).resolve().relative_to(DATA_DIR)
    return "guides/" + str(rel.with_suffix(".html")).replace("\\", "/")


def detect_eol(text):
    return "\r\n" if "\r\n" in text else "\n"


# ----------------------------------------------------------------------------------- parsing
def strip_internal_links(html):
    """Unwrap inline internal-reference anchors to their text. Returns (clean, n_stripped)."""
    n = 0

    def repl(m):
        nonlocal n
        n += 1
        return m.group(1)

    return INTERNAL_A_RE.sub(repl, html), n


def parse_credits(text):
    """Return dict(indent, sec_num, leads, rows, start, end) or None.

    start/end are line indices (inclusive) of the <section>..</section> block in the
    keepends-split line list, so callers can splice. Raises ValueError on a malformed
    credits block (unexpected inner line) so problems surface loudly.
    """
    lines = text.splitlines(keepends=True)
    start = indent = None
    for i, line in enumerate(lines):
        m = SECTION_OPEN_RE.match(line.rstrip("\r\n"))
        if m:
            start, indent = i, m.group(1)
            break
    if start is None:
        return None
    close_re = re.compile(r'^' + re.escape(indent) + r'</section>\s*$')
    end = None
    for j in range(start + 1, len(lines)):
        if close_re.match(lines[j].rstrip("\r\n")):
            end = j
            break
    if end is None:
        raise ValueError("credits <section> never closed")

    sec_num, tag, leads, rows = None, None, [], []
    for line in lines[start + 1:end]:
        s = line.strip()
        if not s:
            continue
        m = SEC_HEAD_RE.match(s)
        if m:
            sec_num, tag = m.group(1), m.group(2)
            continue
        m = LEAD_RE.match(s)
        if m:
            leads.append(m.group(1))
            continue
        if s in ('<div class="cr-rows">', "</div>"):
            continue
        m = ROW_RE.match(s)
        if m:
            rows.append({
                "label": m.group("label"),
                "what": m.group("what"),
                "url": m.group("url"),
                "display": m.group("display"),
            })
            continue
        raise ValueError(f"unrecognized credits line: {s[:120]!r}")
    if sec_num is None:
        raise ValueError("credits block has no sec-num")
    return {"indent": indent, "sec_num": sec_num, "tag": tag, "leads": leads,
            "rows": rows, "start": start, "end": end}


# --------------------------------------------------------------------------------- rendering
def render_credits(indent, sec_num, leads, rows, eol, tag=None):
    """Emit the canonical credits block as a string ending in `eol` after </section>."""
    i1 = indent + "  "
    i2 = indent + "    "
    tag_html = f'<span class="tag">{tag}</span>' if tag else ""
    out = [f'{indent}<section class="credits" id="section-credits">']
    out.append(f'{i1}<div class="sec-head"><span class="sec-num">{sec_num}</span>'
               f'<h2>Sources</h2>{tag_html}</div>')
    for lead in leads:
        out.append(f'{i1}<p class="lead">{lead}</p>')
    out.append(f'{i1}<div class="cr-rows">')
    for r in rows:
        out.append(
            f'{i2}<div class="cr-row">'
            f'<span class="cr-src">{r["label"]}</span>'
            f'<span class="cr-what">{r["what"]}</span>'
            f'<a class="cr-link" href="{r["url"]}" target="_blank" '
            f'rel="noopener noreferrer">{r["display"]}</a></div>'
        )
    out.append(f'{i1}</div>')
    out.append(f'{indent}</section>')
    return eol.join(out) + eol


def replace_credits(text, parsed, new_block):
    """Splice new_block (a render_credits string) over the parsed section in text."""
    lines = text.splitlines(keepends=True)
    before = "".join(lines[:parsed["start"]])
    after = "".join(lines[parsed["end"] + 1:])
    return before + new_block + after


# ------------------------------------------------------------------------------------- io
def read_text(path):
    return Path(path).read_text(encoding="utf-8")


def write_text(path, text):
    Path(path).write_text(text, encoding="utf-8", newline="")


def iter_credits_pages():
    """Yield Path for every guides/**.html that carries a credits section."""
    for p in sorted(GUIDES_DIR.rglob("*.html")):
        txt = p.read_text(encoding="utf-8")
        if 'class="credits" id="section-credits"' in txt:
            yield p
