#!/usr/bin/env python3
"""dossier_links.py — deterministic cross-link resolution for the GENERATED dossier
loadout tables (3-State Loadout §06 + Engineering Plan §09).

Per the loadout-table linking rules:
  * MODULE name      -> module / weapon anchor                 (ALWAYS linked)
  * BLUEPRINT name   -> the exact blueprint anchor, disambiguated by its module group
                                                               (ALWAYS linked where resolvable)
  * ENGINEER name    -> engineer anchor (splits "A / B")       (ALWAYS linked)
  * EXPERIMENTAL     -> NEVER linked (the builder emits it as plain text)

Common-term blocking (mining/refinery/sensors/…) does NOT apply here: these cells are
definitive module/blueprint references, so they override the prose common-term rule.

Maps are built from data/links/link-dictionary.base.json (+ link-aliases.json) — the same
canonical source the hyperlink applier uses — so the anchors stay in sync. Resolution is
exact (no fuzzy confidence), because the builder knows each cell's column.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "links"
DPREFIX = "../../"   # guides/ships/ship-dossiers/<x>.html -> guides/


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _norm(s):
    return re.sub(r"[^a-z0-9]+", " ", str(s).lower()).strip()


# module display / filebase variant -> canonical blueprint group (normalized)
GROUP_ALIAS = {"armour": "bulkheads"}

# Module/weapon display names that aren't catalogued surface forms, mapped to the anchor the
# modules.html / blueprints.html page documents them under (so rule 3.1 — module ALWAYS linked
# — holds for armour variants, mining tools, Guardian/AX gear, passenger cabins, limpets, etc.).
# Keyed by normalized display name; verified against the actual page section ids.
MODULE_ALIAS = {
    # armour grades -> the Bulkheads engineering group (no module-bulkheads anchor exists)
    "lightweight alloy": "blueprint-group-bulkheads",
    "reinforced alloy": "blueprint-group-bulkheads",
    "military grade composite": "blueprint-group-bulkheads",
    "mirrored surface composite": "blueprint-group-bulkheads",
    "reactive surface composite": "blueprint-group-bulkheads",
    # passenger cabins
    "economy passenger cabin": "module-passenger-cabin",
    "first passenger cabin": "module-passenger-cabin",
    "business passenger cabin": "module-passenger-cabin",
    "luxury passenger cabin": "module-passenger-cabin",
    # Guardian / AX weapons + reinforcement
    "guardian gauss cannon": "module-guardian-ax",
    "guardian shard cannon": "module-guardian-ax",
    "guardian plasma charger": "module-guardian-ax",
    "enhanced ax multi cannon": "module-guardian-ax",
    "ax multi cannon": "module-guardian-ax",
    "mining volley repeater": "module-mining",
    "shutdown field neutraliser": "module-xeno",
    "guardian hull reinforcement": "module-guardian-reinforcement",
    "guardian module reinforcement": "module-guardian-reinforcement",
    "guardian shield reinforcement": "module-guardian-reinforcement",
    # mining tools
    "abrasion blaster": "module-mining",
    "seismic charge launcher": "module-mining",
    "sub surface displacement missile": "module-mining",
    "pulse wave analyser": "module-mining",
    # scanners / limpets / flight assists
    "xeno scanner": "module-xeno",
    "decontamination limpet controller": "module-limpet-controllers",
    "repair limpet controller": "module-limpet-controllers",
    "planetary vehicle hangar": "module-flight-assists",
    "fighter hangar": "module-flight-assists",
    "supercruise assist": "module-flight-assists",
    "docking computer": "module-flight-assists",
}

_M = None


def _maps():
    global _M
    if _M:
        return _M
    base = json.loads((DATA / "link-dictionary.base.json").read_text(encoding="utf-8"))
    al = json.loads((DATA / "link-aliases.json").read_text(encoding="utf-8"))
    by_anchor = {e["anchor"]: e for e in base["entries"]}

    module_surf = {}     # norm(surface) -> (file, anchor)  [module + blueprint-group]

    def addsurf(surf, anchor):
        e = by_anchor.get(anchor)
        if e:
            module_surf.setdefault(_norm(surf), (e["file"], anchor))

    for e in base["entries"]:
        if e["family"] in ("module", "blueprint-group"):
            for sf in e.get("surface_forms", []):
                if '"' not in sf:
                    addsurf(sf, e["anchor"])
            addsurf(e["label"], e["anchor"])
    for form, anchor in {**al.get("module_aliases", {}),
                         **al.get("blueprint_group_aliases", {})}.items():
        addsurf(form, anchor)

    bp_eg = {}           # (norm effect, norm group) -> (file, anchor)
    eff_groups = {}      # norm effect -> set of (file, anchor)
    groups = set()       # all normalized blueprint group names
    for e in base["entries"]:
        if e["family"] == "blueprint" and "(" in e["label"]:
            eff = _norm(e["label"].split(" (")[0])
            grp = _norm(e["label"].split("(", 1)[1].rstrip(")"))
            bp_eg[(eff, grp)] = (e["file"], e["anchor"])
            eff_groups.setdefault(eff, set()).add((e["file"], e["anchor"]))
            groups.add(grp)
    bp_alias = {}
    for form, anchor in al.get("blueprint_aliases", {}).items():
        e = by_anchor.get(anchor)
        if e:
            bp_alias[_norm(form)] = (e["file"], e["anchor"])

    eng = {}             # norm engineer name -> (file, anchor)
    for e in base["entries"]:
        if e["family"] == "engineer":
            for sf in e.get("surface_forms", []):
                if '"' not in sf:
                    eng.setdefault(_norm(sf), (e["file"], e["anchor"]))

    _M = dict(module_surf=module_surf, bp_eg=bp_eg, eff_groups=eff_groups,
              groups=groups, bp_alias=bp_alias, eng=eng, by_anchor=by_anchor)
    return _M


def _a(file, anchor, text):
    return f'<a href="{DPREFIX}{file}#{anchor}">{esc(text)}</a>'


def _module_hit(name):
    M = _maps()
    key = _norm(name)
    if key in MODULE_ALIAS:                       # curated display-name -> page anchor
        e = M["by_anchor"].get(MODULE_ALIAS[key])
        if e:
            return (e["file"], e["anchor"])
    hit = M["module_surf"].get(key) or (M["module_surf"].get(key[:-1]) if key.endswith("s") else None)
    if hit:
        return hit
    # containment fallback (e.g. "Bi-Weave Shield" -> "bi weave shield generator"): the text
    # must be a UNIQUE substring of exactly one catalogued surface (so bare "shield" stays
    # unlinked — it's contained in many).
    if len(key) >= 4:
        cands = {v for k, v in M["module_surf"].items() if key in k}
        if len(cands) == 1:
            return next(iter(cands))
    return None


def link_module(name):
    """Link a single module/weapon display name (ALWAYS, ignores common-term block).
    Returns esc(name) unchanged if the name has no catalogued anchor."""
    if not name:
        return esc(name)
    hit = _module_hit(name)
    return _a(hit[0], hit[1], name) if hit else esc(name)


_SPLIT_RE = re.compile(r"\s*(/|&|,)\s*")


def link_module_text(text):
    """Link the module column of the Engineering Plan, which is editorial free text that may
    name several modules ('Life Support / Sensors', 'Beam & Pulse Lasers'). Splits on / & ,
    and links each token that resolves, preserving the separators and any '(...)' suffix."""
    if not text:
        return esc(text)
    parts = _SPLIT_RE.split(text)
    out = []
    for tok in parts:
        if tok in ("/", "&", ","):
            out.append(f" {tok} ")
            continue
        m = re.match(r"(.+?)(\s*\([^)]*\))?$", tok.strip())
        if not m or not tok.strip():
            out.append(esc(tok))
            continue
        nm, tail = m.group(1).strip(), (m.group(2) or "")
        hit = _module_hit(nm)
        out.append((_a(hit[0], hit[1], nm) + esc(tail)) if hit else esc(tok))
    return "".join(out)


def group_norm(group_hint):
    """Normalize a module display / filebase to a canonical blueprint group name."""
    M = _maps()
    g = GROUP_ALIAS.get(_norm(group_hint), _norm(group_hint))
    if g in M["groups"]:
        return g
    if g.endswith("s") and g[:-1] in M["groups"]:
        return g[:-1]
    for cand in M["groups"]:                       # variant containment, longest first
        if g and (g in cand or cand in g):
            return cand
    return g


def link_blueprint(effect, group_hint):
    """Link a blueprint effect, disambiguated by its module group. ALWAYS links where the
    (effect, group) is resolvable; falls back to a unique-effect or curated alias."""
    if not effect:
        return esc(effect)
    M = _maps()
    eff = _norm(effect)
    hit = M["bp_eg"].get((eff, group_norm(group_hint)))
    if not hit and len(M["eff_groups"].get(eff, ())) == 1:
        hit = next(iter(M["eff_groups"][eff]))
    if not hit:
        hit = M["bp_alias"].get(eff)
    return _a(hit[0], hit[1], effect) if hit else esc(effect)


def link_engineer(text):
    """Link engineer name(s); splits 'A / B' and keeps a trailing '(...)' out of the link."""
    if not text:
        return esc(text)
    M = _maps()

    def one(part):
        s = part.strip()
        m = re.match(r"(.+?)(\s*\([^)]*\))?$", s)
        nm, tail = m.group(1).strip(), (m.group(2) or "")
        hit = M["eng"].get(_norm(nm))
        return (_a(hit[0], hit[1], nm) + esc(tail)) if hit else esc(part)

    return " / ".join(one(p) for p in text.split("/")) if "/" in text else one(text)
