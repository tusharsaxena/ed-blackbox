#!/usr/bin/env python3
# extract-engineers-editorial.py — one-time seeder: current engineers.html cards ->
# data/engineers-extra/editorial.json (reference only; the overlay is hand-maintained after).
#
# Per the preserve-and-verify decision (design spec), the engineer cards are editorial. The
# seeder captures, for each <article id="engineer-<slug>"> card: its accent class, name,
# section, document order, and the card's INNER HTML verbatim (everything between the
# <article ...> open tag and </article>). build-engineers.py re-emits the cards byte-for-byte
# from this; audit-engineers.py verifies the rendered mod grades against coriolis.
#
# Stdlib only. See docs/superpowers/specs/2026-06-30-engineers-data-pipeline-design.md.

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "guides" / "engineering" / "engineers.html"
EXTRA = ROOT / "data" / "engineers-extra"

SECTION_RE = re.compile(r'<section id="(section-(?:ship|ody)-(?:t[123]|col))">(.*?)</section>', re.S)
# Card: <article class="rec <accent>" id="engineer-<slug>"> INNER </article>
CARD_RE = re.compile(r'<article class="rec ([^"]*)" id="engineer-([^"]+)">(.*?)</article>', re.S)
NAME_RE = re.compile(r'<h3>(.*?)</h3>')


def main():
    html = PAGE.read_text(encoding="utf-8")
    cards = {}
    order = 0
    for sec_id, sec_body in SECTION_RE.findall(html):
        for accent, slug, inner in CARD_RE.findall(sec_body):
            nm = NAME_RE.search(inner)
            cards[f"engineer-{slug}"] = {
                "name": nm.group(1) if nm else slug,
                "section": sec_id,
                "order": order,
                "accent": accent.strip(),
                "html": inner,
            }
            order += 1
    EXTRA.mkdir(parents=True, exist_ok=True)
    out = EXTRA / "editorial.json"
    out.write_text(json.dumps({"cards": cards}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"extract-engineers-editorial: wrote {len(cards)} cards to {out.relative_to(ROOT)}")
    if len(cards) != 38:
        print(f"  WARNING: expected 38 cards, got {len(cards)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
