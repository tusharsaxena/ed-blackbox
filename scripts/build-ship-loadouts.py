#!/usr/bin/env python3
"""build-ship-loadouts.py — build dossier loadout tables from canonical SLEF data.

CANONICAL SOURCE: data/ship-loadouts/<dossier-basename>.json — a SLEF array
(Ship Loadout Export Format, https://inara.cz/elite/inara-impexp-slef/) of THREE builds
(Initial / A-Rated / Engineered), each a standalone, importable SLEF loadout. The state is
tagged in header.appCustomProperties.state; the editorial layer (intro, callout, per-slot
notes, engineering plan) lives in header.appCustomProperties.edbb (SLEF-sanctioned arbitrary
custom data). FDev `Item` symbols, blueprint fdnames and experimental ednames are resolved to
display strings via scripts/slef_resolve.py (driven by EDCD coriolis-data in data/).

This renders the 3-State Loadout (table.l3 + intro + callout) and the Engineering Plan
(table.data) inside each dossier from that data. The data is the source of truth — edit the
SLEF JSON, never the generated tables.

Usage:
    python3 scripts/build-ship-loadouts.py                 # build all
    python3 scripts/build-ship-loadouts.py corvette        # matching basenames
    python3 scripts/build-ship-loadouts.py --check         # report, write nothing

Idempotent. Non-SLEF (legacy object) data files are skipped with a notice.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import slef_resolve as R  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "ship-loadouts"
DOSSIER_DIR = ROOT / "guides" / "ships" / "dossiers"
SHIPS_DIR = ROOT / "data" / "ships"

MDASH = "—"
MIDDOT = "·"
STATES = ["initial", "arated", "engineered"]


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# ---------- cell rendering ----------

def _module_display(mod):
    """A build's module dict {Slot, Item, ...} -> 'size+rating Name (Mount)'."""
    if not mod or not mod.get("Item"):
        return MDASH, None
    spec = R.resolve_item(mod["Item"])
    if not spec:
        return f"?{mod['Item']}", None
    size, rating, name = spec.get("size"), spec.get("rating"), spec.get("name")
    prefix = f"{size}{rating} " if size is not None and rating else ""
    text = f"{prefix}{name}"
    if spec.get("mount"):
        text += f" ({R.MOUNT_DISPLAY.get(spec['mount'], spec['mount'])})"
    return text, spec


def render_buy_cell(mod):
    return _module_display(mod)[0]


def render_eng_cell(eng_mod, arated_mod):
    """Engineered column: blueprint + experimental ONLY.
      - A-Rated slot empty          -> '—'
      - blueprint + experimental    -> 'G5 Overcharged + Corrosive Shell'
      - blueprint, no experimental  -> 'G5 Overcharged (no experimental effect)'
      - fitted, no blueprint        -> '(No blueprint available)'
    """
    if not arated_mod or not arated_mod.get("Item"):
        return MDASH
    eng = (eng_mod or {}).get("Engineering")
    if eng and eng.get("BlueprintName"):
        grade = eng.get("Level")
        bp = R.resolve_blueprint(eng["BlueprintName"])
        head = f"G{grade} {bp}" if grade else bp
        if eng.get("ExperimentalEffect"):
            head += f" + {R.resolve_special(eng['ExperimentalEffect'])}"
        else:
            head += " (no experimental effect)"
        return head
    return "(No blueprint available)"


# ---------- table HTML ----------

def _slot_rows(builds):
    """Align modules across builds by Slot. Returns ordered list of
    {group, label, initial, arated, engineered, slot}."""
    by_state = {}
    for st in STATES:
        by_state[st] = {m["Slot"]: m for m in builds.get(st, {}).get("data", {}).get("Modules", [])}
    slots = {}
    for st in STATES:
        for slot in by_state[st]:
            slots.setdefault(slot, R.parse_slot(slot))
    rows = []
    for slot, info in slots.items():
        if info is None:
            continue  # slot we don't surface (e.g. PlanetaryApproachSuite)
        rows.append({
            "group": info["group"], "label": info["label"], "slot": slot,
            "sort": (info["g"], info["o"]),
            "initial": by_state["initial"].get(slot),
            "arated": by_state["arated"].get(slot),
            "engineered": by_state["engineered"].get(slot),
        })
    rows.sort(key=lambda r: r["sort"])
    return rows


def render_l3_table(builds, notes):
    rows = _slot_rows(builds)
    lines = ['<table class="l3">']
    lines.append("<thead><tr><th>Slot</th><th>Initial " + MIDDOT
                 + " buy-only</th><th>A-Rated " + MIDDOT
                 + " no eng</th><th>Engineered</th><th>Notes</th></tr></thead>")
    lines.append("<tbody>")
    last_group = None
    for row in rows:
        if row["group"] != last_group:
            lines.append(f'<tr class="grouprow"><td colspan="5">{esc(row["group"])}</td></tr>')
            last_group = row["group"]
        init = render_buy_cell(row["initial"])
        arat = render_buy_cell(row["arated"])
        eng = render_eng_cell(row["engineered"], row["arated"])
        note = notes.get(row["slot"], "")
        lines.append(
            f'<tr><td class="slot">{esc(row["label"])}</td>'
            f'<td class="st">{esc(init)}</td>'
            f'<td class="st">{esc(arat)}</td>'
            f'<td class="eng">{esc(eng)}</td>'
            f'<td class="note">{esc(note)}</td></tr>'
        )
    lines.append("</tbody>")
    lines.append("</table>")
    return "\n".join(lines)


def render_eng_plan_table(plan):
    lines = ['<table class="data">']
    lines.append("<thead><tr><th>Module</th><th>Blueprint</th><th>Experimental</th>"
                 "<th>Engineer</th></tr></thead>")
    lines.append("<tbody>")
    for e in plan:
        mod = esc(e["module"])
        if e.get("size") is not None:
            mod = f"{mod} ({e['size']})"
        grade = e.get("grade")
        bp = e.get("blueprint", "")
        bp_disp = f"{esc(bp)} ({grade})" if grade else esc(bp)
        exp = esc(e.get("experimental", MDASH) or MDASH)
        eng = esc(e.get("engineer", MDASH) or MDASH)
        lines.append(f'<tr><td class="mod">{mod}</td><td>{bp_disp}</td>'
                     f'<td>{exp}</td><td>{eng}</td></tr>')
    lines.append("</tbody>")
    lines.append("</table>")
    return "\n".join(lines)


# ---------- validation ----------

_ship_cache = {}


def load_ship(ship):
    key = (ship or "").lower()
    if key in _ship_cache:
        return _ship_cache[key]
    val = None
    for p in SHIPS_DIR.glob("*.json"):
        try:
            d = json.loads(p.read_text())
        except Exception:
            continue
        inner = d.get(p.stem, d)
        nm = inner.get("properties", {}).get("name", "")
        if p.stem.lower() == key or nm.replace(" ", "").lower() == key.replace("_", "").replace(" ", ""):
            val = inner
            break
    _ship_cache[key] = val
    return val


def validate(builds):
    warns = []
    # every Item resolves
    for st in STATES:
        for m in builds.get(st, {}).get("data", {}).get("Modules", []):
            if m.get("Item") and not R.resolve_item(m["Item"]):
                warns.append(f"  [{st}] {m['Slot']}: unresolved Item '{m['Item']}'")
    # engineered requires the slot fitted in A-Rated
    ar = {m["Slot"] for m in builds.get("arated", {}).get("data", {}).get("Modules", []) if m.get("Item")}
    for m in builds.get("engineered", {}).get("data", {}).get("Modules", []):
        if (m.get("Engineering") or {}).get("BlueprintName") and m["Slot"] not in ar:
            warns.append(f"  engineered {m['Slot']}: blueprint but slot empty in A-Rated")
    # core sizes vs hull
    ship = load_ship(builds.get("engineered", {}).get("data", {}).get("Ship", ""))
    if ship:
        std = ship.get("slots", {}).get("standard", [])
        size_by_core = {R.CORE_ORDER[i]: std[i] for i in range(min(len(std), len(R.CORE_ORDER)))}
        for m in builds.get("arated", {}).get("data", {}).get("Modules", []):
            info = R.parse_slot(m["Slot"])
            if info and info["group"] == "Core Internals":
                spec = R.resolve_item(m.get("Item", ""))
                want = size_by_core.get(info["label"])
                if spec and want is not None and str(spec.get("size")) != str(want):
                    warns.append(f"  {info['label']}: item size {spec.get('size')} != hull size {want}")
    return warns


# ---------- splicing ----------

def splice(html, builds, editorial):
    """Minimal string surgery — replace ONLY the two target regions, leaving the rest of
    the document byte-for-byte intact (so diffs stay small and reviewable)."""
    notes = editorial.get("notes", {})

    # --- 3-State Loadout: replace everything between the .sec-head and the section close ---
    sec_open = html.find('<section id="section-3-state-loadout">')
    if sec_open == -1:
        raise ValueError("no <section id='section-3-state-loadout'>")
    sh = html.find('<div class="sec-head">', sec_open)
    sh_end = html.find("</div>", sh) + len("</div>")
    sec_close = html.find("</section>", sh_end)
    frag = []
    if editorial.get("intro"):
        frag.append(f'<p>{esc(editorial["intro"])}</p>')
    frag.append('<div class="tbl-scroll">')
    frag.append(render_l3_table(builds, notes))
    frag.append("</div>")
    if editorial.get("callout"):
        c = editorial["callout"]
        frag.append(f'<div class="callout"><span class="lbl">{esc(c["label"])}</span>'
                    f'<p>{esc(c["text"])}</p></div>')
    block = "\n    " + "\n    ".join(frag) + "\n  "
    html = html[:sh_end] + block + html[sec_close:]

    # --- Engineering Plan: replace the table.data inside that section ---
    if editorial.get("engineeringPlan"):
        ep = html.find('<section id="section-engineering-plan">')
        if ep != -1:
            tbl = html.find('<table class="data">', ep)
            close = html.find("</table>", tbl) if tbl != -1 else -1
            if close != -1:
                tbl_end = close + len("</table>")
                html = html[:tbl] + render_eng_plan_table(editorial["engineeringPlan"]) + html[tbl_end:]
    return html


def find_dossier(basename):
    p = DOSSIER_DIR / f"{basename}.html"
    return p if p.exists() else None


def process(spec_path, check_only=False):
    try:
        raw = json.loads(spec_path.read_text())
    except Exception as e:
        return False, f"{spec_path.stem}: BAD JSON {e}"
    if not isinstance(raw, list):
        return True, f"{spec_path.stem}: skipped (not SLEF array — legacy format)"
    basename = spec_path.stem
    dossier = find_dossier(basename)
    if dossier is None:
        return False, f"{basename}: NO DOSSIER"
    builds, editorial = {}, {}
    for b in raw:
        props = b.get("header", {}).get("appCustomProperties", {}) or {}
        st = props.get("state")
        if st in STATES:
            builds[st] = b
        if props.get("edbb"):
            editorial = props["edbb"]
    missing = [s for s in STATES if s not in builds]
    if missing:
        return False, f"{basename}: missing build states {missing}"
    warns = validate(builds)
    html = dossier.read_text()
    try:
        new_html = splice(html, builds, editorial)
    except Exception as e:  # noqa
        return False, f"{basename}: ERROR {e}"
    changed = new_html != html
    if not check_only and changed:
        dossier.write_text(new_html)
    status = ("would change" if changed else "ok") if check_only else \
             ("built" if changed else "ok (no change)")
    msg = f"{basename}: {status}"
    for w in warns:
        msg += "\n" + w
    return True, msg


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check_only = "--check" in sys.argv[1:]
    specs = sorted(DATA_DIR.glob("*.json"))
    if args:
        specs = [s for s in specs if any(a in s.stem for a in args)]
    if not specs:
        print("no matching loadout data files")
        sys.exit(1)
    ok = warn = err = skip = 0
    for s in specs:
        good, msg = process(s, check_only)
        print(("  " if good else "! ") + msg)
        if not good:
            err += 1
        elif "skipped" in msg:
            skip += 1
        elif "\n  " in msg:
            warn += 1
        else:
            ok += 1
    print(f"\n{len(specs)} file(s): {ok} clean, {warn} with warnings, {skip} skipped, {err} errors")
    if err:
        sys.exit(1)


if __name__ == "__main__":
    main()
