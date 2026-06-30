#!/usr/bin/env python3
# audit-blueprints.py — deterministic page<->data consistency audit for the Blueprints page.
#
# Independent of build-blueprints.py (different code path: this PARSES the rendered
# guides/engineering/engineering-manuals/blueprints.html and checks every fact against canonical data
# instead of re-rendering it). Stdlib only, non-LLM. Exits non-zero with one line per
# failure on any of:
#   - a material / category / per-roll / engineer / experimental on the page not matching
#     data/modifications/ (+ corrections overlay);
#   - a Total cell != Per Roll x avg_rolls(grade)  (experimentals: avg = 1);
#   - an engineers.html#engineer-<slug> link that resolves to no id in engineers.html;
#   - a "N blueprints" group count that != the rendered card count of that group;
#   - any internal-site <a href> inside the bottom-of-page section.credits block
#     (Sources is external references only).
#
# Joins page cards to coriolis (module-key, fdname) via the authored editorial overlay
# (data/modifications-extra/editorial.json): modgroup slug -> module key, card title -> fdname.
#
# Usage:  python3 scripts/audit-blueprints.py
# On success prints:  OK — N modgroups, M cards, 0 mismatches, 0 broken anchors
#
# See scripts/audit-blueprints.md and the design spec
# docs/superpowers/specs/2026-06-30-blueprints-data-pipeline-design.md.

import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bp_common as b

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "guides" / "engineering" / "engineering-manuals" / "blueprints.html"
ENGINEERS = ROOT / "guides" / "engineering" / "engineering-manuals" / "engineers.html"

BEGIN = "<!-- BEGIN generated:blueprints -->"
END = "<!-- END generated:blueprints -->"

CAT_CLASS = {"Raw": "raw", "Manufactured": "man", "Encoded": "enc"}

# Single <tr> of one of the four kinds (tables are emitted single-line).
ROW_RE = re.compile(r'<tr class="(gh|mr|eh|er)">(.*?)</tr>', re.S)
MAT_ROW_RE = re.compile(
    r'<td class="matname">([^<]*)</td>'
    r'<td class="cat (raw|man|enc)">([^<]*)</td>'
    r'<td class="r">(\d+)</td><td class="r">(\d+)</td>'
    r'<td class="r total">(\d+)</td>'
)
ENG_LINK_RE = re.compile(r'<a href="engineers\.html#(engineer-[a-z0-9-]+)">([^<]*)</a>')
GRADE_RE = re.compile(r'<span class="gnum">Grade (\d+)</span>')
EXP_NAME_RE = re.compile(r'<span class="enum">([^<]*)</span>')
EXP_DESC_RE = re.compile(r'<span class="exp-desc">— (.*?)</span>', re.S)
CARD_RE = re.compile(
    r'<div class="bp-card" id="(blueprint-[a-z0-9-]+)" '
    r'data-mod="([^"]*)" data-bp="([^"]*)">(.*?)\n</div>', re.S)
CARD_TITLE_RE = re.compile(r'<span class="bp-card-title">([^<]*)</span>')
TBODY_RE = re.compile(r'<tbody>(.*?)</tbody>', re.S)
MODGROUP_START_RE = re.compile(
    r'<div class="bp-modgroup" id="blueprint-group-([a-z0-9-]+)">.*?'
    r'<span class="bp-mod-count">(\d+) blueprints?</span>', re.S)
CREDITS_RE = re.compile(r'<section class="credits"[^>]*>(.*?)</section>', re.S)
ANY_HREF_RE = re.compile(r'<a\s[^>]*href="([^"]*)"')
EXTERNAL_RE = re.compile(r'^https?://', re.I)


def U(s):
    """HTML-unescape page text to compare against raw coriolis values."""
    return html.unescape(s)


def parse_table(tbody):
    """Parse one card's <tbody> into structured facts. Returns
    (grades, exps) where grades[g] = {engineers:[(anchor,display)], mats:{mat:(pr,avg,tot)}}
    and exps = [{name, desc, mats:{mat:(pr,avg,tot)}}], preserving document order."""
    grades, exps = {}, []
    cur_grade, cur_exp = None, None
    for kind, inner in ROW_RE.findall(tbody):
        if kind == "gh":
            g = int(GRADE_RE.search(inner).group(1))
            engs = [(a, U(d)) for a, d in ENG_LINK_RE.findall(inner)]
            grades[g] = {"engineers": engs, "mats": {}}
            cur_grade, cur_exp = g, None
        elif kind == "eh":
            name = U(EXP_NAME_RE.search(inner).group(1))
            dm = EXP_DESC_RE.search(inner)
            desc = U(dm.group(1)) if dm else ""
            cur_exp = {"name": name, "desc": desc, "mats": {}}
            exps.append(cur_exp)
        else:  # mr / er
            m = MAT_ROW_RE.search(inner)
            mat = U(m.group(1))
            cls, cat_text = m.group(2), m.group(3)
            pr, avg, tot = int(m.group(4)), int(m.group(5)), int(m.group(6))
            bucket = grades[cur_grade]["mats"] if kind == "mr" else cur_exp["mats"]
            bucket[mat] = (pr, avg, tot, cls, cat_text)
    return grades, exps


def main():
    data = b.load_data()
    corr = b.load_corrections()
    edit = b.load_editorial()
    if not edit:
        sys.exit("editorial.json is missing — run build-blueprints.py pipeline first.")

    blueprints = data["blueprints"]
    modules = data["modules"]
    specials = data["specials"]

    eng_ids = set(re.findall(r'id="(engineer-[a-z0-9-]+)"', ENGINEERS.read_text(encoding="utf-8")))

    # slug -> module key; (slug, title) -> fdname  (the authored page<->data join).
    slug_modkey = {s: info["module"] for s, info in edit["modgroups"].items()}
    title_fd = {}
    for key, info in edit["blueprints"].items():
        s, fd = key.split("/", 1)
        title_fd[(s, info["title"])] = fd

    page = PAGE.read_text(encoding="utf-8")

    # Concatenate the generated marker regions (sections 02-05).
    regions = re.findall(re.escape(BEGIN) + r"\n(.*?)\n" + re.escape(END), page, re.S)
    if not regions:
        sys.exit("no <!-- BEGIN generated:blueprints --> regions found in the page")
    gen = "\n".join(regions)

    mismatches = []   # any value/data discrepancy
    broken = []       # engineer anchors with no matching id in engineers.html

    # Slice the generated text into per-modgroup spans by modgroup-start positions.
    starts = [(m.start(), m.group(1), int(m.group(2))) for m in MODGROUP_START_RE.finditer(gen)]
    n_groups = len(starts)
    n_cards = 0

    for i, (pos, slug, count_label) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(gen)
        block = gen[pos:end]
        modkey = slug_modkey.get(slug)
        if modkey is None:
            mismatches.append(f"[group] blueprint-group-{slug}: no editorial modgroup / module key")
            continue
        mod = modules.get(modkey, {})

        cards = list(CARD_RE.finditer(block))
        if len(cards) != count_label:
            mismatches.append(
                f"[count] blueprint-group-{slug}: label says {count_label} blueprints "
                f"but {len(cards)} cards rendered")

        # Expected experimentals for this module group (non-legacy), keyed by name.
        exp_keys = [e for e in mod.get("specials", [])
                    if e in specials and "(Legacy)" not in specials[e]["name"]]
        exp_by_name = {specials[e]["name"]: specials[e] for e in exp_keys}

        for cm in cards:
            n_cards += 1
            cid = cm.group(1)
            body = cm.group(4)
            tm = CARD_TITLE_RE.search(body)
            title = U(tm.group(1)) if tm else ""
            fd = title_fd.get((slug, title))
            if fd is None or fd not in blueprints:
                mismatches.append(f"[card] {cid}: title {title!r} maps to no blueprint fdname in data")
                continue
            bp = blueprints[fd]
            mod_bp = mod.get("blueprints", {}).get(fd)
            if mod_bp is None:
                mismatches.append(f"[card] {cid}: ({modkey}, {fd}) is not a data module x blueprint instance")
                continue

            tbm = TBODY_RE.search(body)
            if not tbm:
                mismatches.append(f"[card] {cid}: no <tbody> table found")
                continue
            grades, exps = parse_table(tbm.group(1))

            # --- per-grade: engineers, materials, categories, per-roll, totals ---
            for g_str, gdata in bp["grades"].items():
                g = int(g_str)
                if g not in grades:
                    mismatches.append(f"[grade] {cid}: data has Grade {g} but page omits it")
                    continue
                pg = grades[g]
                avgx = b.avg_rolls(g)

                # engineers: post-fix, deduped by display, anchor must match + resolve
                exp_eng = {}
                for raw in mod_bp["grades"][g_str]["engineers"]:
                    fixed = b.fix_engineer(raw, corr)
                    disp = re.sub(r"\s+", " ", re.sub(r'"[^"]*"', "", fixed)).strip()
                    exp_eng[disp] = b.engineer_anchor(fixed)
                page_eng = {disp: anchor for anchor, disp in pg["engineers"]}
                if set(page_eng) != set(exp_eng):
                    mismatches.append(
                        f"[engineer] {cid} G{g}: engineers {sorted(page_eng)} != data {sorted(exp_eng)}")
                for disp, anchor in page_eng.items():
                    if disp in exp_eng and anchor != exp_eng[disp]:
                        mismatches.append(
                            f"[engineer] {cid} G{g}: {disp!r} anchor #{anchor} != expected #{exp_eng[disp]}")
                    if anchor not in eng_ids:
                        broken.append(f"[anchor] {cid} G{g}: engineers.html#{anchor} resolves to no id")

                # materials / categories / per-roll / total
                _check_rows(cid, f"G{g}", gdata.get("components", {}), pg["mats"], avgx, mismatches)

            for g in grades:
                if str(g) not in bp["grades"]:
                    mismatches.append(f"[grade] {cid}: page has Grade {g} not in data")

            # --- experimentals: set, names, descriptions, costs ---
            page_exp = {e["name"]: e for e in exps}
            if set(page_exp) != set(exp_by_name):
                mismatches.append(
                    f"[experimental] {cid}: experimentals {sorted(page_exp)} != data {sorted(exp_by_name)}")
            for name, pe in page_exp.items():
                sp = exp_by_name.get(name)
                if sp is None:
                    continue
                if pe["desc"] != sp["description"]:
                    mismatches.append(f"[experimental] {cid}: {name!r} description differs from specials.json")
                _check_rows(cid, f"Exp {name}", sp.get("components", {}), pe["mats"], 1, mismatches)

    # --- Sources block: external references only ---
    cm = CREDITS_RE.search(page)
    if cm:
        for href in ANY_HREF_RE.findall(cm.group(1)):
            if not EXTERNAL_RE.match(href):
                mismatches.append(f"[credits] internal-site link in Sources block: {href!r}")

    fails = mismatches + broken
    if fails:
        for line in fails:
            print(line)
        print(f"FAIL — {n_groups} modgroups, {n_cards} cards, "
              f"{len(mismatches)} mismatches, {len(broken)} broken anchors")
        return 1

    print(f"OK — {n_groups} modgroups, {n_cards} cards, 0 mismatches, 0 broken anchors")
    return 0


def _check_rows(cid, where, expected_components, page_mats, avgx, mismatches):
    """Compare one grade's / experimental's material rows against canonical components."""
    exp_mats = {U(k): v for k, v in expected_components.items()}
    if set(page_mats) != set(exp_mats):
        mismatches.append(
            f"[material] {cid} {where}: materials {sorted(page_mats)} != data {sorted(exp_mats)}")
    for mat, (pr, avg, tot, cls, cat_text) in page_mats.items():
        # category (taxonomy / data)
        try:
            cat = b.material_category(mat)
        except KeyError:
            mismatches.append(f"[category] {cid} {where}: unknown material category for {mat!r}")
            cat = None
        if cat is not None:
            if cat_text != cat:
                mismatches.append(f"[category] {cid} {where}: {mat!r} category {cat_text!r} != {cat!r}")
            if cls != CAT_CLASS[cat]:
                mismatches.append(f"[category] {cid} {where}: {mat!r} class {cls!r} != {CAT_CLASS[cat]!r}")
        # per-roll vs data
        if mat in exp_mats and pr != exp_mats[mat]:
            mismatches.append(f"[per-roll] {cid} {where}: {mat!r} Per Roll {pr} != data {exp_mats[mat]}")
        # avg-rolls formula
        if avg != avgx:
            mismatches.append(f"[avg-rolls] {cid} {where}: {mat!r} Avg Rolls {avg} != formula {avgx}")
        # total = per-roll x avg-rolls
        if tot != pr * avg:
            mismatches.append(f"[total] {cid} {where}: {mat!r} Total {tot} != Per Roll {pr} x Avg {avg}")


if __name__ == "__main__":
    raise SystemExit(main())
