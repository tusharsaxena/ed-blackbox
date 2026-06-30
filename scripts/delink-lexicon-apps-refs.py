#!/usr/bin/env python3
"""delink-lexicon-apps-refs.py — trim redundant/noisy cross-links on two reference pages.

Two pages over-link auto-generated cross-references that add noise rather than value:

1. guides/systems/cmdrs-lexicon.html
   a. Term column — every first cell is <td class="mod">; the abbreviation/term itself
      was hyperlinked. Unwrap ALL links in those cells (keep the text). The Meaning
      column carries the useful links.
   b. Ship-name links in the Meaning column — ship rows read
      "<b><a …dossiers…>Asp Explorer</a></b> — desc. <a …dossiers…>Dossier</a>."
      The bold ship-name link duplicates the trailing "Dossier" link, so unwrap the
      ship-name link (keep <b>…</b> + the Dossier link). Only dossier links are touched;
      module/blueprint bold links in other tables are left alone.

2. guides/systems/third-party-apps.html
   App cards carry a deliberate external link to the resource (<a class="cb-ext"> ↗ in the
   <h3>). The card free-text had game-concept/app cross-links (Fuel Scoop, ship dossiers,
   #app-… anchors) auto-applied. Unwrap every INTERNAL link inside each <article class="card">
   block (relative or #anchor); keep the external cb-ext link and any other http(s) link.

Byte-preserving otherwise. Note: both pages are link SOURCES for apply-hyperlinks.py, so a
future pass could re-add internal links; mark elements class="nolink" if that recurs.

Usage:  python3 scripts/delink-lexicon-apps-refs.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEXICON = ROOT / "guides" / "systems" / "cmdrs-lexicon.html"
APPS = ROOT / "guides" / "systems" / "third-party-apps.html"

A_TAG = re.compile(r'<a\s+[^>]*?href="([^"]*)"[^>]*>(.*?)</a>', re.DOTALL)


def unwrap_all(fragment: str) -> str:
    """Unwrap every <a>…</a> in the fragment, keeping inner text."""
    return A_TAG.sub(lambda m: m.group(2), fragment)


def unwrap_internal(fragment: str) -> str:
    """Unwrap only internal links (not http/https); keep external links intact."""
    def repl(m):
        href = m.group(1)
        if href.startswith("http://") or href.startswith("https://"):
            return m.group(0)
        return m.group(2)
    return A_TAG.sub(repl, fragment)


def do_lexicon() -> int:
    html = orig = LEXICON.read_text(encoding="utf-8")

    # a) Term column: unwrap all links inside <td class="mod">…</td>
    term_cells = re.findall(r'<td class="mod">.*?</td>', html, re.DOTALL)
    term_links = sum(len(A_TAG.findall(c)) for c in term_cells)
    html = re.sub(r'<td class="mod">.*?</td>',
                  lambda m: unwrap_all(m.group(0)), html, flags=re.DOTALL)

    # b) Ship-name links in Meaning column. Ship rows bold the hull name(s) and link them
    #    to the dossier, then repeat a "Dossier" link at the end — so unwrap every dossier
    #    link inside any <b>…</b> group (handles single and slash-joined multi-hull groups
    #    like "Type-6 / Type-7 / …"). Bold groups with no dossier link (module/blueprint
    #    terms in other tables) are left untouched. The trailing "Dossier" link is outside
    #    the <b> and stays.
    ship_links = 0
    def _bold(m):
        nonlocal ship_links
        inner = m.group(1)
        if "dossiers/" in inner:
            ship_links += len(A_TAG.findall(inner))
            return "<b>" + unwrap_all(inner) + "</b>"
        return m.group(0)
    html = re.sub(r'<b>(.*?)</b>', _bold, html, flags=re.DOTALL)

    if html != orig:
        LEXICON.write_text(html, encoding="utf-8")
    print(f"{LEXICON.relative_to(ROOT)}")
    print(f"  Term-column links unwrapped     : {term_links}")
    print(f"  ship-name (dossier) links unwrap: {ship_links}")
    return 0


def do_apps() -> int:
    html = orig = APPS.read_text(encoding="utf-8")
    blocks = re.findall(r'<article class="card".*?</article>', html, re.DOTALL)
    internal_before = 0
    for b in blocks:
        for href, _ in A_TAG.findall(b):
            if not (href.startswith("http://") or href.startswith("https://")):
                internal_before += 1
    html = re.sub(r'<article class="card".*?</article>',
                  lambda m: unwrap_internal(m.group(0)), html, flags=re.DOTALL)

    if html != orig:
        APPS.write_text(html, encoding="utf-8")
    print(f"{APPS.relative_to(ROOT)}")
    print(f"  internal card-body links unwrap : {internal_before}")
    return 0


def main() -> int:
    rc = do_lexicon()
    rc |= do_apps()
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
