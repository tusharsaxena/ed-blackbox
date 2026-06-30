#!/usr/bin/env python3
"""link-checklist-engineers.py — link engineer names in the checklist.html STEP HEADERS.

checklist.html (the Unlock Checklist) is the one deliberate exception to the
"never link section/sub headers" rule: the engineer being unlocked/climbed is the whole
point of each step, so the engineer name in every `<h3 class="step-action">` header (and
its referral `.sub`) is linked to engineers.html#engineer-<slug>.

Two passes, scoped to the step-action headers only (the Engineer Unlock Map nodes and the
"What to do" prose are already linked; quick-nav is left alone; 'Farseer Inc' never appears
in a header, so partial-name expansion is safe here):
  1. Expand a partial engineer surname to the full name ('Climb Farseer' -> 'Climb Felicity
     Farseer'; 'referrals to Qwent, Nemo' -> '... Marco Qwent, Zacariah Nemo') so linking is
     consistent.
  2. Wrap each engineer full name (not already inside an <a>) in a link to its engineer card.

Idempotent. Usage: python3 scripts/link-checklist-engineers.py [--check]
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "guides" / "engineering" / "engineering-manuals" / "checklist.html"
DICT = ROOT / "data" / "links" / "link-dictionary.base.json"

# only the engineer unlock/climb step cards — NOT farm/build/grind cards (those headers name
# locations like "Jameson Crash Site" that must not be expanded/linked as engineers)
CARD_RE = re.compile(r'<article class="step-card ac-(?:unlock|climb)[^"]*"[^>]*>.*?</article>', re.S)
H3_RE = re.compile(r'(<h3 class="step-action">)(.*?)(</h3>)', re.S)


def _engineers():
    """full name -> slug, and unique surname -> full name (from the link dictionary)."""
    base = json.loads(DICT.read_text(encoding="utf-8"))
    full2slug, surname2full, seen_sur = {}, {}, {}
    for e in base["entries"]:
        if e["family"] != "engineer":
            continue
        slug = e["anchor"].replace("engineer-", "")
        name = e["label"]
        full2slug[name] = slug
        for sf in e.get("surface_forms", []):
            if '"' not in sf:
                full2slug.setdefault(sf, slug)
        last = re.sub(r'"[^"]*"', "", name).split()[-1]   # drop nickname, take surname
        seen_sur[last] = seen_sur.get(last, 0) + 1
        surname2full[last] = name
    # keep only UNIQUE surnames (avoid ambiguous expansion)
    surname2full = {s: f for s, f in surname2full.items() if seen_sur[s] == 1}
    return full2slug, surname2full


def link_header(inner, full2slug, surname2full, firsts):
    # 1. expand a standalone surname -> full name. Skip when it's already preceded by its first
    #    name, when it's followed by another Capitalized word (a place, e.g. 'Jameson Crash
    #    Site'), or when it sits inside a tag/attribute.
    def expand(m):
        pre = m.group(1) or ""
        if pre.strip() in firsts:              # already "<First> <Surname>"
            return m.group(0)
        return f"{pre}{surname2full[m.group(2)]}"
    sur_alt = "|".join(re.escape(s) for s in sorted(surname2full, key=len, reverse=True))
    inner = re.sub(rf'(\w+\s+)?\b({sur_alt})\b(?!\s+[A-Z])(?![^<]*>)', expand, inner)

    # 2. link full names not already inside an <a>
    names = sorted(full2slug, key=len, reverse=True)
    name_alt = "|".join(re.escape(n) for n in names)
    # split on existing anchors so we never touch text already linked
    parts = re.split(r'(<a\b.*?</a>)', inner, flags=re.S)
    for i, seg in enumerate(parts):
        if seg.startswith("<a"):
            continue
        parts[i] = re.sub(
            rf'\b({name_alt})\b(?![^<]*>)',
            lambda m: f'<a href="engineers.html#engineer-{full2slug[m.group(1)]}">{m.group(1)}</a>',
            seg)
    return "".join(parts)


def main():
    check = "--check" in sys.argv[1:]
    full2slug, surname2full = _engineers()
    # every non-surname (leading) token, so a surname already inside a full name isn't re-expanded
    # ('Colonel Bris Dekker' -> firsts has Colonel + Bris, so 'Dekker' after 'Bris' is left alone)
    firsts = {t for n in full2slug for t in n.split()[:-1]}
    src = PAGE.read_text(encoding="utf-8")
    n = [0]

    def fix(m):
        new_inner = link_header(m.group(2), full2slug, surname2full, firsts)
        if new_inner != m.group(2):
            n[0] += 1
        return m.group(1) + new_inner + m.group(3)

    # only rewrite h3 headers inside unlock/climb step cards
    out = CARD_RE.sub(lambda c: H3_RE.sub(fix, c.group(0)), src)
    print(f"{'[check] ' if check else ''}checklist.html: {n[0]} step headers updated; "
          f"+{out.count('engineers.html#engineer') - src.count('engineers.html#engineer')} header links")
    if not check and out != src:
        PAGE.write_text(out, encoding="utf-8")


if __name__ == "__main__":
    main()
