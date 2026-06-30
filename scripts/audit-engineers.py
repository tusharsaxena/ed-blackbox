#!/usr/bin/env python3
# audit-engineers.py — deterministic engineers.html <-> data gate (read-only).
#
# Verifies: 38 cards == EDCD roster (engineers.csv, name-fixed); 8 marker pairs; rendered
# ship-engineer mod grades do not OVER-CLAIM vs coriolis modules.json (hard fail); OMISSIONS
# (coriolis engineer->group not on the page) are reported as warnings for editorial review;
# engineer-<slug> + blueprint-group-<slug> anchors resolve; Sources external-only.
# Exits nonzero on hard fails only. Stdlib only. See scripts/audit-engineers.md.

import html as H
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import engineers_common as e

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "guides" / "engineering" / "engineers.html"
BP = ROOT / "guides" / "engineering" / "blueprints.html"
BEGIN = "<!-- BEGIN generated:engineers -->"
END = "<!-- END generated:engineers -->"

CARD_RE = re.compile(r'<article class="rec [^"]*" id="engineer-([^"]+)">(.*?)</article>', re.S)
NAME_RE = re.compile(r'<h3>(.*?)</h3>')
MODS_BLOCK_RE = re.compile(r'Modifications offered.*?<ul class="reclist">(.*?)</ul>', re.S)
LI_RE = re.compile(r'<li>(.*?)</li>', re.S)
GRADE_RE = re.compile(r'G(\d)\s+(.+)')


def text(s):
    return H.unescape(re.sub(r'<[^>]+>', '', s)).strip()


def namekey(s):
    """Quote-insensitive name key: EDCD engineers.csv writes a nickname with single quotes
    (Tod 'The Blaster' McQuinn) while the page/coriolis use double quotes. Compare without
    quote chars so the same engineer matches across sources."""
    return re.sub(r'["\']', "", H.unescape(s)).strip().lower()


def main():
    fails, warns = [], []
    page = PAGE.read_text(encoding="utf-8")
    roster = e.load_roster()
    mods = e.ship_mods_by_engineer()

    # 1. marker pairs
    if page.count(BEGIN) != 8 or page.count(END) != 8:
        fails.append(f"marker count: {page.count(BEGIN)} BEGIN / {page.count(END)} END (want 8/8)")

    # 2. roster <-> cards
    cards = {slug: body for slug, body in CARD_RE.findall(page)}
    if len(cards) != 38:
        fails.append(f"card count: {len(cards)} (want 38)")
    rendered_names = {text(NAME_RE.search(b).group(1)) for b in cards.values() if NAME_RE.search(b)}
    roster_keys = {namekey(n) for n in roster}
    rendered_keys = {namekey(n) for n in rendered_names}
    missing = roster_keys - rendered_keys
    extra = rendered_keys - roster_keys
    if missing:
        fails.append(f"roster engineers with no card: {sorted(missing)}")
    if extra:
        fails.append(f"cards not in EDCD roster: {sorted(extra)}")

    # 3. mod-grade verification (ship engineers): over-claim = hard fail, omission = warning
    bp_html = BP.read_text(encoding="utf-8") if BP.exists() else ""
    for slug, body in cards.items():
        nm = text(NAME_RE.search(body).group(1)) if NAME_RE.search(body) else None
        cor = mods.get(nm, {})
        mb = MODS_BLOCK_RE.search(body)
        page_groups = {}
        if mb:
            for li in LI_RE.findall(mb.group(1)):
                m = GRADE_RE.match(text(li))
                if m:
                    page_groups[m.group(2).strip()] = int(m.group(1))
        # over-claim: page grade exceeds coriolis-backed max for a known group
        for grp, g in page_groups.items():
            if grp in cor and g > cor[grp]["grade"]:
                fails.append(f"{nm}: claims G{g} {grp} but coriolis backs only G{cor[grp]['grade']}")
        # omission: coriolis group absent from the page list (editorial review)
        for grp, info in cor.items():
            if grp not in page_groups:
                warns.append(f"{nm}: coriolis shows G{info['grade']} {grp}, page omits it")
        # 4. blueprint-group anchors used on the card resolve in blueprints.html
        for slug_anchor in re.findall(r'blueprints\.html#(blueprint-group-[a-z0-9-]+)', body):
            if bp_html and f'id="{slug_anchor}"' not in bp_html:
                fails.append(f"{nm}: dangling anchor blueprints.html#{slug_anchor}")
        # engineer refers-to anchors resolve on this page
        for ref in re.findall(r'href="#(engineer-[a-z0-9-]+)"', body):
            if f'id="{ref}"' not in page:
                fails.append(f"{nm}: dangling #${ref}")

    # 5. Sources external-only
    cred = re.search(r'<section class="credits".*?</section>', page, re.S)
    if cred and re.search(r'href="(#|\.\./|[^"]*\.html)', cred.group(0)):
        fails.append("Sources block contains an internal link (must be external-only)")

    for w in warns:
        print("  warn:", w)
    if fails:
        print("audit-engineers: FAIL")
        for f in fails:
            print("  -", f)
        sys.exit(1)
    print(f"audit-engineers: OK — 38 cards == roster, markers 8/8, no grade over-claims, "
          f"anchors resolve, Sources external-only ({len(warns)} omission warnings)")


if __name__ == "__main__":
    main()
