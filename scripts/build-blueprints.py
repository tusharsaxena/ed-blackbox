#!/usr/bin/env python3
# build-blueprints.py — render the Blueprints page cards from canonical data.
#
# Canonical game data (data/modifications/, verbatim EDCD/coriolis-data import, read-only)
# + a project-authored corrections overlay + an authored editorial overlay
# (data/modifications-extra/) are merged and rendered into the .bp-modgroup / .bp-card
# markup of guides/engineering/engineering-manuals/blueprints.html, BYTE-COMPATIBLE with the hand-authored
# page. Only the run of modgroups inside each of sections 02-05 — delimited by
#   <!-- BEGIN generated:blueprints -->  ...  <!-- END generated:blueprints -->
# — is rewritten; everything else on the page (About, masthead, callouts, footer, the
# generated Sources block) is preserved untouched.
#
# Data joins (see the design spec):
#   - which coriolis module a display group represents : editorial modgroups[<mslug>].module
#     (authored structural metadata — several module groups share a blueprint set but differ
#      in engineers/experimentals, so the key cannot be inferred from data alone)
#   - blueprint title / effect / suit / ctx prose       : editorial blueprints[<mslug>/<fd>]
#   - per-grade component costs (Per Roll = qty)         : blueprints.json[<fd>].grades[g].components
#   - engineers per grade                                : modules.json[<key>].blueprints[<fd>].grades[g].engineers
#                                                          (post engineer_name_fixes; deduped + sorted by display)
#   - experimentals (per module, same for every card)    : modules.json[<key>].specials -> specials.json
#                                                          (excludes "(Legacy)" effects; sorted by name)
#   - Avg Rolls / Total                                  : AVG_ROLLS formula; Total = Per Roll x Avg Rolls
#                                                          (experimentals: Avg Rolls = 1, Total = Per Roll)
#
# Usage:
#   python3 scripts/build-blueprints.py            # write the page
#   python3 scripts/build-blueprints.py --check    # print a unified diff, write nothing
#
# Stdlib only. See scripts/build-blueprints.md and the design spec
# docs/superpowers/specs/2026-06-30-blueprints-data-pipeline-design.md.

import argparse
import difflib
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bp_common as b

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "guides" / "engineering" / "engineering-manuals" / "blueprints.html"

BEGIN = "<!-- BEGIN generated:blueprints -->"
END = "<!-- END generated:blueprints -->"

# Section render order: editorial `section` value -> page <section id="section-...">.
SECTIONS = ["core-internals", "optional-internals", "utility-mounts", "hardpoints"]

CAT_CLASS = {"Raw": "raw", "Manufactured": "man", "Encoded": "enc"}


def esc(s):
    """HTML-escape matching the page's entity set (&#x27; for ', &quot; for ", &amp;/&lt;/&gt;)."""
    return html.escape(s, quote=True)


def eng_display(name):
    """Engineer display text as shown on the page: drop a quoted nickname and collapse
    whitespace, e.g. 'Tod "The Blaster" McQuinn' -> 'Tod McQuinn'."""
    return re.sub(r"\s+", " ", re.sub(r'"[^"]*"', "", name)).strip()


def engineer_links(engineers, corr):
    """Render the per-grade engineer list: name-fixes applied, deduped, sorted by display,
    each linked to engineers.html#engineer-<slug>, joined by ' · '."""
    by_disp = {}
    for e in engineers:
        fixed = b.fix_engineer(e, corr)
        by_disp[eng_display(fixed)] = b.engineer_anchor(fixed)
    return " · ".join(
        f'<a href="engineers.html#{by_disp[d]}">{esc(d)}</a>' for d in sorted(by_disp)
    )


def material_rows(components, avg, cls, data):
    """Render the `.mr`/`.er` material rows for one grade or experimental, sorted by
    material name. Per Roll = component qty; Total = qty x avg."""
    out = []
    for mat in sorted(components):
        qty = components[mat]
        cat = b.material_category(mat, data)
        out.append(
            f'<tr class="{cls}"><td class="matname">{esc(mat)}</td>'
            f'<td class="cat {CAT_CLASS[cat]}">{cat}</td>'
            f'<td class="r">{qty}</td><td class="r">{avg}</td>'
            f'<td class="r total">{qty * avg}</td></tr>'
        )
    return "".join(out)


def render_table(fdname, modkey, data, corr):
    """Render the `.bp-table` for a blueprint: per-grade material rows + experimentals."""
    bp = data["blueprints"][fdname]
    mod = data["modules"][modkey]
    specials = data["specials"]
    rows = []
    for g in sorted(int(x) for x in bp["grades"]):
        grade = bp["grades"][str(g)]
        engineers = mod["blueprints"][fdname]["grades"][str(g)]["engineers"]
        rows.append(
            f'<tr class="gh"><td colspan="5"><span class="gnum">Grade {g}</span> '
            f'<span class="eng">— {engineer_links(engineers, corr)}</span></td></tr>'
        )
        rows.append(material_rows(grade.get("components", {}), b.avg_rolls(g), "mr", data))
    # Experimentals: this module's specials (excluding Legacy effects), sorted by name.
    exps = [e for e in mod.get("specials", [])
            if e in specials and "(Legacy)" not in specials[e]["name"]]
    for ed in sorted(exps, key=lambda e: specials[e]["name"]):
        sp = specials[ed]
        rows.append(
            f'<tr class="eh"><td colspan="5"><span class="bp-exp-tag">Exp</span> '
            f'<span class="enum">{esc(sp["name"])}</span> '
            f'<span class="exp-desc">— {esc(sp["description"])}</span></td></tr>'
        )
        rows.append(material_rows(sp.get("components", {}), 1, "er", data))
    return (
        '<table class="bp-table"><colgroup><col class="c-mat"><col class="c-cat">'
        '<col class="c-num"><col class="c-num"><col class="c-num"></colgroup>'
        '<thead><tr><th>Material</th><th>Category</th><th class="r">Per Roll</th>'
        '<th class="r">Avg Rolls</th><th class="r">Total</th></tr></thead><tbody>'
        + "".join(rows) + "</tbody></table>"
    )


def render_card(mslug, fdname, display, modkey, data, corr, edit):
    """Render one `.bp-card` block (multi-line, no trailing newline)."""
    ed = edit["blueprints"][f"{mslug}/{fdname}"]
    title = ed["title"]
    cid = f"blueprint-{mslug}-{b.slugify(title)}"
    suit = "".join(
        f'<span class="bp-tag {"fleet" if t == "All ships" else "ship"}">{esc(t)}</span>'
        for t in ed["suit"]
    )
    ctx = ed["ctx"]
    table = render_table(fdname, modkey, data, corr)
    return (
        f'<div class="bp-card" id="{cid}" data-mod="{display.lower()}" '
        f'data-bp="{title.lower()}">\n'
        f'  <div class="bp-card-head" role="button" tabindex="0" aria-expanded="false">\n'
        f'    <span class="bp-fold" aria-hidden="true">&#9654;</span>\n'
        f'    <span class="bp-card-title">{esc(title)}</span>\n'
        f'    <span class="bp-card-tag">{esc(display)}</span>\n'
        f'  </div>\n'
        f'  <div class="bp-card-body">\n'
        f'    <div class="bp-effect">{esc(ed["effect"])}</div>\n'
        f'    <div class="bp-suit">{suit}</div>\n'
        f'    <div class="bp-ctx">\n'
        f'      <div class="bp-panel"><h6><span class="ic">&#9881;</span> What it does</h6>'
        f'<p>{esc(ctx["does"])}</p></div>\n'
        f'      <div class="bp-panel"><h6><span class="ic">&#9733;</span> Who it\'s for</h6>'
        f'<p>{esc(ctx["for"])}</p></div>\n'
        f'      <div class="bp-panel"><h6><span class="ic">&#9889;</span> Experimental pick</h6>'
        f'<p>{esc(ctx["exp"])}</p></div>\n'
        f'    </div>\n'
        f'    {table}\n'
        f'  </div>\n'
        f'</div>'
    )


def render_modgroup(mslug, data, corr, edit):
    """Render one `.bp-modgroup` block (head + alphabetised cards + closing div)."""
    mg = edit["modgroups"][mslug]
    display = mg["display"]
    modkey = mg["module"]
    # Cards for this group, alphabetised by title (the page's card order).
    fds = [k.split("/", 1)[1] for k in edit["blueprints"] if k.split("/", 1)[0] == mslug]
    fds.sort(key=lambda fd: edit["blueprints"][f"{mslug}/{fd}"]["title"])
    n = len(fds)
    noun = "blueprint" if n == 1 else "blueprints"
    head = (
        f'<div class="bp-modgroup" id="blueprint-group-{mslug}"><div class="bp-mod-head">'
        f'<div class="bp-mod-label">{esc(display)} '
        f'<span class="bp-mod-count">{n} {noun}</span></div>'
        f'<button class="bp-grp-bulk bp-grp-exp" type="button" '
        f'aria-label="Expand all {esc(display)} blueprints"><span>+</span> Expand all</button>'
        f'<button class="bp-grp-bulk bp-grp-col" type="button" '
        f'aria-label="Collapse all {esc(display)} blueprints">'
        f'<span>&minus;</span> Collapse all</button></div>'
    )
    cards = [render_card(mslug, fd, display, modkey, data, corr, edit) for fd in fds]
    return head + "\n" + "\n".join(cards) + "\n</div>"


def render_section(section, data, corr, edit):
    """Render the modgroup run for one section, ordered by editorial `order`."""
    slugs = [m for m, info in edit["modgroups"].items() if info["section"] == section]
    slugs.sort(key=lambda m: edit["modgroups"][m]["order"])
    return "\n".join(render_modgroup(m, data, corr, edit) for m in slugs)


def reconcile_instances(data, corr, edit):
    """Reconcile the canonical module x blueprint instances against what the page
    renders, consuming corrections.json#exclude_instances.

    Every blueprint-bearing (module-key, fdname) in data/modifications/modules.json
    must be EITHER rendered (present in editorial, keyed mslug/fdname -> module-key) OR
    listed in exclude_instances with a `why`. Anything unaccounted for is a hard error —
    this is the deterministic gate that documents the 185 (page) vs 186 (data) delta.
    Returns (n_data, n_rendered, n_excluded)."""
    data_instances = {
        (mk, fd)
        for mk, mv in data["modules"].items()
        for fd in mv.get("blueprints", {})
    }
    rendered = {
        (edit["modgroups"][k.split("/", 1)[0]]["module"], k.split("/", 1)[1])
        for k in edit["blueprints"]
    }
    excluded = set()
    for ex in corr.get("exclude_instances", []):
        key = (ex.get("module"), ex.get("blueprint"))
        if not ex.get("why"):
            sys.exit(f"exclude_instances entry {key} is missing a 'why'")
        if key not in data_instances:
            sys.exit(f"exclude_instances entry {key} is not a real data instance")
        excluded.add(key)

    overlap = rendered & excluded
    if overlap:
        sys.exit(f"instances both rendered and excluded: {sorted(overlap)}")
    unaccounted = data_instances - rendered - excluded
    if unaccounted:
        sys.exit(
            "data module x blueprint instances neither rendered nor excluded "
            f"(add to editorial.json or corrections.json#exclude_instances): "
            f"{sorted(unaccounted)}"
        )
    return len(data_instances), len(rendered), len(excluded)


def build(check):
    data = b.load_data()
    corr = b.load_corrections()
    edit = b.load_editorial()
    if not edit:
        sys.exit("editorial.json is missing — run extract-blueprint-editorial.py first.")

    n_data, n_rendered, n_excluded = reconcile_instances(data, corr, edit)

    old = PAGE.read_text(encoding="utf-8")

    # Locate each marker region and the section it belongs to (nearest preceding <section id>).
    regions = list(re.finditer(
        re.escape(BEGIN) + r"\n(.*?)\n" + re.escape(END), old, re.S))
    if len(regions) != len(SECTIONS):
        sys.exit(f"expected {len(SECTIONS)} marker regions, found {len(regions)}")

    new = old
    # Replace from last to first so spans stay valid.
    for m in reversed(regions):
        sid = None
        for sm in re.finditer(r'<section id="section-([a-z-]+)"', old[:m.start()]):
            sid = sm.group(1)
        if sid not in SECTIONS:
            sys.exit(f"marker region not inside a known section (got {sid!r})")
        body = render_section(sid, data, corr, edit)
        new = new[:m.start(1)] + body + new[m.end(1):]

    if check:
        diff = list(difflib.unified_diff(
            old.splitlines(keepends=True), new.splitlines(keepends=True),
            fromfile="blueprints.html (on disk)", tofile="blueprints.html (generated)"))
        sys.stdout.writelines(diff)
        n_cards = len(edit["blueprints"])
        n_groups = len(edit["modgroups"])
        recon = f"reconcile: {n_data} data instances = {n_rendered} rendered + {n_excluded} excluded"
        if diff:
            print(f"\n[--check] {n_groups} modgroups, {n_cards} cards — "
                  f"{sum(1 for l in diff if l.startswith(('+', '-')) and not l.startswith(('+++', '---')))} changed lines")
        else:
            print(f"[--check] byte-identical — {n_groups} modgroups, {n_cards} cards, no diff")
        print(f"[--check] {recon}")
        return 0

    if new != old:
        PAGE.write_text(new, encoding="utf-8")
    n_cards = len(edit["blueprints"])
    n_groups = len(edit["modgroups"])
    print(f"wrote {PAGE.relative_to(ROOT)} — {n_groups} modgroups, {n_cards} cards")
    print(f"reconcile: {n_data} data instances = {n_rendered} rendered + {n_excluded} excluded")
    # The cards are re-emitted without the cross-links the hyperlink pass adds (ctx panels,
    # prose), so re-apply them after every build to keep them durable (idempotent; relink.py).
    print("\nrelinking blueprints.html…")
    from relink import relink
    relink([PAGE])
    return 0


def main():
    ap = argparse.ArgumentParser(description="Render the Blueprints page cards from canonical data.")
    ap.add_argument("--check", action="store_true",
                    help="print a unified diff against the on-disk page; write nothing")
    args = ap.parse_args()
    return build(args.check)


if __name__ == "__main__":
    raise SystemExit(main())
