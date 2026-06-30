#!/usr/bin/env python3
# audit-powerplay.py — deterministic powerplay.html <-> data/powerplay/powers.json gate.
#
# Verifies: 12 power cards + 12 module cards; rendered power slugs == powers.json powers and
# each card's allegiance class matches; rendered module names == powers.json modules; 2
# generated:powerplay marker pairs; powerplay-<slug> anchors resolve; Sources external-only.
# Exits nonzero on any mismatch. Stdlib only. See scripts/audit-powerplay.md.

import html as H
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "guides" / "systems" / "powerplay.html"
DATA = ROOT / "data" / "powerplay" / "powers.json"
BEGIN = "<!-- BEGIN generated:powerplay -->"
END = "<!-- END generated:powerplay -->"

ALLEGIANCE_CLASS = {
    "federation": "sp-fed", "empire": "sp-emp", "alliance": "sp-all", "independent": "sp-ind",
}


def text(s):
    return H.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def main():
    fails = []
    page = PAGE.read_text(encoding="utf-8")
    data = json.loads(DATA.read_text(encoding="utf-8"))
    powers = {p["slug"]: p for p in data["powers"]}
    modules = data["modules"]

    # 1. marker pairs
    if page.count(BEGIN) != 2 or page.count(END) != 2:
        fails.append(f"marker count: {page.count(BEGIN)} BEGIN / {page.count(END)} END (want 2/2)")

    regions = re.findall(re.escape(BEGIN) + r"(.*?)" + re.escape(END), page, re.S)
    powers_region = regions[0] if regions else ""
    modules_region = regions[1] if len(regions) > 1 else ""

    # 2. power cards: id powerplay-<slug> + allegiance class, against powers.json
    card_re = re.compile(r'<article class="rec ([a-z- ]*?)pw" id="powerplay-([a-z-]+)">(.*?)</article>', re.S)
    rendered = {}
    for accent, slug, body in card_re.findall(powers_region):
        cls = re.search(r'<h3 class="(sp-[a-z]+)"', body)
        rendered[slug] = cls.group(1) if cls else None
    if len(rendered) != 12:
        fails.append(f"power cards: {len(rendered)} (want 12)")
    miss = set(powers) - set(rendered)
    extra = set(rendered) - set(powers)
    if miss:
        fails.append(f"powers in powers.json with no card: {sorted(miss)}")
    if extra:
        fails.append(f"power cards not in powers.json: {sorted(extra)}")
    for slug, cls in rendered.items():
        if slug in powers:
            want = ALLEGIANCE_CLASS.get(powers[slug]["allegiance"])
            if cls != want:
                fails.append(f"{slug}: allegiance class {cls} != {want} (powers.json={powers[slug]['allegiance']})")

    # 3. module cards: names against powers.json
    rendered_modules = [text(m) for m in re.findall(r"<h3>([^<]+)</h3>", modules_region)]
    if len(rendered_modules) != 12:
        fails.append(f"module cards: {len(rendered_modules)} (want 12)")
    want_modules = {m["name"] for m in modules}
    miss_m = want_modules - set(rendered_modules)
    extra_m = set(rendered_modules) - want_modules
    if miss_m:
        fails.append(f"modules in powers.json with no card: {sorted(miss_m)}")
    if extra_m:
        fails.append(f"module cards not in powers.json: {sorted(extra_m)}")

    # 4. powerplay-<slug> referral anchors resolve
    for ref in re.findall(r'href="#(powerplay-[a-z-]+)"', page):
        if f'id="{ref}"' not in page:
            fails.append(f"dangling anchor #{ref}")

    # 5. Sources external-only
    cred = re.search(r'<section class="credits".*?</section>', page, re.S)
    if cred and re.search(r'href="(#|\.\./|[^"]*\.html)', cred.group(0)):
        fails.append("Sources block contains an internal link (must be external-only)")

    if fails:
        print("audit-powerplay: FAIL")
        for f in fails:
            print("  -", f)
        sys.exit(1)
    print("audit-powerplay: OK — 12 powers (allegiance matched) + 12 modules == powers.json, "
          "markers 2/2, anchors resolve, Sources external-only")


if __name__ == "__main__":
    main()
