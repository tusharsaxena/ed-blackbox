#!/usr/bin/env python3
"""link-by-role-pages.py — curate the cross-links on the by-role ladder pages.

`guides/ships/by-role/**` is deliberately EXCLUDED from the generic
`apply-hyperlinks.py` pass (it would resolve a bare ship name to the hull's
*default* role, which is wrong on a role ladder). This script adds the role-correct
links those pages need, deterministically:

  1. Ship column (`<td class="mod">`) in the **Full <Role> Ladder** and the
     **Small/Medium/Large-Pad <Role>** sections → the `<ship>-<role>` dossier for
     *this page's* role (combat.html → federal-corvette-combat.html).
  2. The headline pick (`<div class="pick">`) in **Recommendations By <Role>** →
     same role-correct dossier.
  3. The **Cost & Engineering Reality** table:
       - Module column   → guides/engineering/modules.html#module-<slug>
       - Blueprint col   → blueprints.html#blueprint-<group>-<effect> (module×blueprint)
       - Engineer col    → engineers.html#engineer-<slug>
     …and strips bold (`<b>`) / accent (`<span class="acc">`) emphasis from the
     Blueprint, Experimental and Engineer columns (muted qualifier spans are kept).

Targets/anchors come from data/links/link-dictionary.base.json (the same catalog the
applier uses), so they stay in sync. Links are role-correct and only emitted when the
target dossier / anchor actually exists — anything unresolved is reported, never guessed.

The rewrite is byte-preserving (only matched spans change). `reconcile-ratings-html.py`
strips tags when it identifies a ship and leaves engineering tables alone, so these links
survive a later ratings reconcile.

Usage:
    python3 scripts/link-by-role-pages.py --check         # dry-run, print every change
    python3 scripts/link-by-role-pages.py                 # apply to all 7 by-role pages
    python3 scripts/link-by-role-pages.py guides/ships/by-role/combat.html   # one file
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BYROLE = ROOT / "guides" / "ships" / "by-role"
DICT = ROOT / "data" / "links" / "link-dictionary.base.json"
ALIASES = ROOT / "data" / "ship-aliases" / "ship-aliases.json"

ROLES = ["combat", "ax", "mining", "trading", "exploration", "passenger", "multipurpose"]

# ---- engineering-table mapping: module display -> (module anchor, blueprint group) ----
# keyed by the module name normalised (lowercased, parenthetical/qualifier stripped).
MODULE_MAP = {
    "power distributor": ("module-power-distributor", "power-distributor"),
    "power plant": ("module-power-plant", "power-plant"),
    "thrusters": ("module-thrusters", "thrusters"),
    "shield generator": ("module-shield-generator", "shield-generator"),
    "shield boosters": ("module-shield-booster", "shield-booster"),
    "shield booster": ("module-shield-booster", "shield-booster"),
    "bulkheads / hrps": ("module-hull-reinforcement", "hull-reinforcement-package"),
    "multi-cannons": ("module-kinetic", "multi-cannon"),
    "multi-cannon": ("module-kinetic", "multi-cannon"),
    "lasers": ("module-lasers", None),          # no single laser blueprint group
    "fsd": ("module-frame-shift-drive", "frame-shift-drive"),
    "frame shift drive": ("module-frame-shift-drive", "frame-shift-drive"),
    "life support / sensors": ("module-life-support", "life-support"),
    "life support": ("module-life-support", "life-support"),
    "sensors": ("module-sensors", "sensors"),
    # AX page variants ("Blueprint / Source" table)
    "gauss cannons": ("module-guardian-ax", None),
    "hull / bulkheads": ("module-hull-reinforcement", "bulkheads"),
    "guardian hull / module reinforcement": ("module-module-reinforcement", None),
    # Pulse Wave Analyser has no catalogued module/blueprint anchor -> left unlinked
}
# engineer-column values that are deliberately NOT engineers (don't flag as misses)
ENGINEER_SKIP = {"various", "guardian broker"}
# blueprint effect display -> anchor effect slug (auto-derived otherwise)
BLUEPRINT_EFFECT_ALIAS = {"dirty drives": "dirty-drive-tuning"}
# engineer cell name -> dictionary engineer key (for the few that differ)
ENGINEER_ALIAS = {"prof palin": "professor palin"}


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", s.lower())).strip()


# normalise the hand-written keys above so lookups match norm()ed cell text
MODULE_MAP = {norm(k): v for k, v in MODULE_MAP.items()}


def load_catalog():
    d = json.loads(DICT.read_text(encoding="utf-8"))
    module_anchors = {e["anchor"] for e in d["entries"] if e["family"] == "module"}
    blueprint_anchors = {e["anchor"] for e in d["entries"] if e["family"] == "blueprint"}
    # engineer: normalised label (nickname stripped) -> anchor
    eng = {}
    for e in d["entries"]:
        if e["family"] == "engineer":
            lab = re.sub(r'"[^"]*"', " ", e["label"])   # drop "The Blaster" nicknames
            eng[norm(lab)] = e["anchor"]
    # ships: per role, display name / alias -> dossier basename
    al = json.loads(ALIASES.read_text(encoding="utf-8")).get("aliases", {}) if ALIASES.exists() else {}
    ship_by_role = {r: {} for r in ROLES}
    for slug, m in d["ships"].items():
        forms = [m["name"]] + list(al.get(slug, []))
        for role, path in m["roles"].items():
            base = path.rsplit("/", 1)[-1]
            for f in forms:
                ship_by_role.setdefault(role, {})[f] = base
    return module_anchors, blueprint_anchors, eng, ship_by_role


MOD_CELL = re.compile(r'(<td class="mod">)([^<]+?)(</td>)')
PICK = re.compile(r'(<div class="pick">)([^<]+?)(\s*<small>)')


def link_ships_in_section(sec: str, ships: dict, log: list) -> str:
    """Wrap ship-name <td class="mod"> cells (ladder/pad tables) in role dossier links."""
    def repl(m):
        name = m.group(2).strip()
        base = ships.get(name)
        if not base:
            if name not in _NON_SHIP_SEEN:        # only ship-looking misses are interesting
                log.append(("ship?", name))
            return m.group(0)
        return f'{m.group(1)}<a href="../dossiers/{base}">{m.group(2)}</a>{m.group(3)}'
    return MOD_CELL.sub(repl, sec)


def link_picks_in_section(sec: str, ships: dict, log: list) -> str:
    def repl(m):
        name = m.group(2).strip()
        base = ships.get(name)
        if not base:
            log.append(("pick?", name))
            return m.group(0)
        return f'{m.group(1)}<a href="../dossiers/{base}">{m.group(2)}</a>{m.group(3)}'
    return PICK.sub(repl, sec)


# emphasis to strip from blueprint/experimental/engineer columns (NOT muted qualifiers)
STRIP_EMPH = [
    (re.compile(r'<span class="acc">(.*?)</span>', re.S), r"\1"),
    (re.compile(r"</?b>"), ""),
]


def strip_emphasis(cell: str) -> str:
    for rx, rep in STRIP_EMPH:
        cell = rx.sub(rep, cell)
    return cell


def lead_split(cell: str):
    """Split a cell into (leading-name, rest) at the first ' (' or '<span'/'<' marker."""
    m = re.search(r"\s*(?:\(|<)", cell)
    return (cell[:m.start()], cell[m.start():]) if m else (cell, "")


def link_eng_table(sec: str, cat, log: list) -> str:
    module_anchors, blueprint_anchors, eng = cat
    m = re.search(r'(<thead><tr><th>Module</th><th>Blueprint[^<]*</th>'
                  r'<th>Experimental</th><th>Engineer[^<]*</th></tr></thead>\s*<tbody>)(.*?)(</tbody>)',
                  sec, re.S)
    if not m:
        return sec
    head, body, tail = m.groups()

    def eng_link(em):
        nm = em.group(0)
        if not nm.strip():
            return nm
        k = ENGINEER_ALIAS.get(norm(nm), norm(nm))
        a = eng.get(k)
        if a:
            return f'<a href="../../engineering/engineers.html#{a}">{nm}</a>'
        if k not in ENGINEER_SKIP:
            log.append(("engineer?", nm.strip()))
        return nm

    def do_row(rowm):
        cells = re.findall(r'<td[^>]*>(.*?)</td>', rowm.group(1), re.S)
        if len(cells) != 4:
            return rowm.group(0)
        mod, bp, exp, eng_c = cells
        # module name (read through any existing link) -> module anchor + blueprint group
        mod_name = lead_split(re.sub(r"<[^>]+>", "", mod))[0]
        manchor, group = MODULE_MAP.get(norm(mod_name), (None, None))
        # --- Module column (skip if already linked) ---
        if "<a" not in mod:
            lead, rest = lead_split(mod)
            if manchor and manchor in module_anchors:
                mod = f'<a href="../../engineering/modules.html#{manchor}">{lead}</a>{rest}'
            elif lead.strip():
                log.append(("module?", lead.strip()))
        # --- Blueprint column: strip emphasis, then link module×blueprint ---
        bp = strip_emphasis(bp)
        if "<a" not in bp:
            bl, brest = lead_split(bp)
            slug = BLUEPRINT_EFFECT_ALIAS.get(norm(bl), norm(bl).replace(" ", "-"))
            if group and bl.strip():
                anchor = f"blueprint-{group}-{slug}"
                if anchor in blueprint_anchors:
                    bp = f'<a href="../../engineering/blueprints.html#{anchor}">{bl}</a>{brest}'
                else:
                    log.append(("blueprint?", f"{group} / {bl.strip()}"))
        # --- Experimental column: strip emphasis only ---
        exp = strip_emphasis(exp)
        # --- Engineer column: strip emphasis, link each named engineer ---
        eng_c = strip_emphasis(eng_c)
        if "<a" not in eng_c:
            eng_c = re.sub(r"[^/<>]+", eng_link, eng_c)
        return (f'<tr><td class="mod">{mod}</td><td>{bp}</td>'
                f'<td>{exp}</td><td>{eng_c}</td></tr>')

    new_body = re.sub(r'<tr>(.*?)</tr>', do_row, body, flags=re.S)
    return sec[:m.start()] + head + new_body + tail + sec[m.end():]


SECTION = re.compile(r'(<section id="([^"]+)">)(.*?)(</section>)', re.S)
_NON_SHIP_SEEN = set()   # cells we already know aren't ships (suppress repeat noise)


def process(path: Path, cat, ship_by_role) -> tuple[str, list]:
    role = path.stem
    html = path.read_text(encoding="utf-8")
    ships = ship_by_role.get(role, {})
    log: list = []

    def on_section(m):
        open_tag, sid, body, close = m.groups()
        if (sid == f"section-the-full-{role}-ladder"
                or sid in (f"section-small-pad-{role}", f"section-medium-pad-{role}",
                           f"section-large-pad-{role}")):
            body = link_ships_in_section(body, ships, log)
        elif sid.startswith("section-recommendations-"):
            body = link_picks_in_section(body, ships, log)
        elif sid == "section-cost-engineering-reality":
            body = link_eng_table(body, cat, log)
        return open_tag + body + close

    return SECTION.sub(on_section, html), log


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--check" in sys.argv
    module_anchors, blueprint_anchors, eng, ship_by_role = load_catalog()
    cat = (module_anchors, blueprint_anchors, eng)
    files = ([Path(a) if Path(a).is_absolute() else ROOT / a for a in args]
             or sorted(BYROLE.glob("*.html")))
    tot_changed = 0
    for f in files:
        before = f.read_text(encoding="utf-8")
        after, log = process(f, cat, ship_by_role)
        n_links = after.count('href=') - before.count('href=')
        changed = after != before
        tot_changed += 1 if changed else 0
        status = "DRY" if dry else ("wrote" if changed else "noop")
        print(f"  [{status}] {f.relative_to(ROOT)}: +{n_links} links")
        misses = [x for x in log if x[1]]
        for kind, val in misses:
            print(f"      · unresolved {kind}: {val}")
        if changed and not dry:
            f.write_text(after, encoding="utf-8")
    print(f"\n{'[CHECK] ' if dry else ''}{tot_changed} file(s) changed.")


if __name__ == "__main__":
    main()
