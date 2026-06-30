#!/usr/bin/env python3
# extract-blueprint-editorial.py — one-time seeder for the blueprints data pipeline.
#
# Parses the hand-typed guides/engineering/blueprints.html and lifts its AUTHORED
# content + presentation metadata into data/modifications-extra/editorial.json (Layer 3
# of the pipeline). Game data (materials, engineers, experimentals, costs) is NOT copied
# here — it stays canonical in data/modifications/ and is re-joined by build-blueprints.py.
#
# What it captures
#   - per .bp-modgroup : display name, enclosing section, document order (1-based per section)
#   - per .bp-card     : title, effect, suit[] tags, ctx{does,for,exp} panels
#   - card -> coriolis (mod-slug, fdname) resolution: each card is matched to the blueprint
#     it represents by its per-grade MATERIAL SIGNATURE (the .mr per-roll rows == the
#     coriolis `components` quantities — ground truth, robust to editorial title drift),
#     scoped to the card's module group; ties broken by normalized blueprint name.
#
# Why material-signature matching (not title matching): several editorial card titles
# diverge from the coriolis blueprint `name` (e.g. Bulkheads "Blast Resistant" /
# "Explosive Resistant" vs coriolis "Lightweight" / "Blast resistant"), so a title match
# alone would mis-resolve. The per-grade component quantities are exact and module-scoped.
#
# Emits WARN lines for: any card that does not resolve to an fdname, and any coriolis
# blueprint with no card on the page (the 185<->186 reconciliation delta — handled in
# Task 4). These WARN lines are the deliverable that drives reconciliation.
#
# Output JSON: sorted keys, 2-space indent (matches the sibling corrections.json).
# Stdlib only. See docs/superpowers/specs/2026-06-30-blueprints-data-pipeline-design.md
# and scripts/extract-blueprint-editorial.md.

import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bp_common as b

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "guides" / "engineering" / "blueprints.html"
OUT = ROOT / "data" / "modifications-extra" / "editorial.json"


def grade_signature(card_html):
    """Per-grade material -> per-roll signature from a card's .mr rows (the blueprint
    rows only; experimental .er rows start after the first .eh and are excluded).
    Returns a hashable tuple form for equality, plus a dict form for inspection."""
    sig = {}
    grade = None
    for m in re.finditer(r'<tr class="(gh|mr|eh)">(.*?)</tr>', card_html, re.S):
        cls, body = m.group(1), m.group(2)
        if cls == "eh":
            break
        if cls == "gh":
            grade = int(re.search(r"Grade (\d)", body).group(1))
            sig[grade] = {}
        else:
            mat = re.search(r'class="matname">(.*?)</td>', body).group(1)
            per_roll = int(re.findall(r'<td class="r">(\d+)</td>', body)[0])
            sig[grade][html.unescape(mat)] = per_roll
    return _freeze(sig)


def _freeze(sig):
    return tuple(sorted(
        (g, tuple(sorted(mats.items()))) for g, mats in sig.items()
    ))


def coriolis_signature(fdname, bps):
    grades = bps[fdname]["grades"]
    sig = {int(g): dict(v.get("components", {})) for g, v in grades.items()}
    return _freeze(sig)


def parse_cards(chunk):
    """Yield (data_bp, title, effect, suit[], ctx{}, signature) for each card in a
    modgroup chunk of HTML."""
    cards = re.split(r'<div class="bp-card" id="', chunk)[1:]
    out = []
    for c in cards:
        body = c.split("</table>")[0] + "</table>"
        data_bp = re.search(r'data-bp="([^"]*)"', c).group(1)
        title = html.unescape(re.search(r'class="bp-card-title">(.*?)</span>', c).group(1))
        effect = html.unescape(re.search(r'class="bp-effect">(.*?)</div>', c, re.S).group(1))
        suit = [html.unescape(t) for t in
                re.findall(r'<span class="bp-tag [a-z]+">(.*?)</span>', c)]
        panels = re.findall(r'<div class="bp-panel"><h6>.*?</h6><p>(.*?)</p></div>', c, re.S)
        ctx = {
            "does": html.unescape(panels[0]),
            "for": html.unescape(panels[1]),
            "exp": html.unescape(panels[2]),
        }
        out.append({
            "data_bp": data_bp,
            "title": title,
            "effect": effect,
            "suit": suit,
            "ctx": ctx,
            "sig": grade_signature(body),
        })
    return out


def main():
    page = PAGE.read_text(encoding="utf-8")
    data = b.load_data()
    mods, bps = data["modules"], data["blueprints"]

    # coriolis modules carrying blueprints, with their per-blueprint material signatures.
    mod_keys = {k: v["blueprints"] for k, v in mods.items() if v.get("blueprints")}
    sig_of = {fd: coriolis_signature(fd, bps) for fd in bps}

    # Section boundaries (02-05). Map each modgroup to its enclosing section id.
    sec_spans = [(m.group(1), m.start()) for m in
                 re.finditer(r'<section id="section-([a-z-]+)"', page)]

    def section_at(pos):
        cur = None
        for sid, start in sec_spans:
            if start <= pos:
                cur = sid
            else:
                break
        return cur

    # Split the page into modgroup chunks (preserving document order + position).
    mg_iter = list(re.finditer(
        r'<div class="bp-modgroup" id="blueprint-group-([a-z0-9-]+)">'
        r'.*?<div class="bp-mod-label">(.*?) <span class="bp-mod-count">', page, re.S))
    mg_starts = [m.start() for m in mg_iter] + [len(page)]

    modgroups = []
    order_in_section = {}
    for i, m in enumerate(mg_iter):
        mslug = m.group(1)
        display = html.unescape(m.group(2))
        section = section_at(m.start())
        chunk = page[mg_starts[i]:mg_starts[i + 1]]
        cards = parse_cards(chunk)
        order_in_section[section] = order_in_section.get(section, 0) + 1
        modgroups.append({
            "mslug": mslug,
            "display": display,
            "section": section,
            "order": order_in_section[section],
            "cards": cards,
        })

    # Resolve each card to a coriolis fdname, scoped to the module group's coriolis key.
    def resolve_in_key(key, card):
        fds = mod_keys[key]
        sig_hits = [fd for fd in fds if sig_of[fd] == card["sig"]]
        cands = sig_hits if sig_hits else list(fds)
        if len(cands) == 1:
            return cands[0]
        # tie (e.g. two same-signature blueprints in one module): disambiguate by name.
        for target in (b.slugify(card["data_bp"]), b.slugify(card["title"])):
            for fd in cands:
                if b.slugify(bps[fd]["name"]) == target:
                    return fd
        return None

    # A modgroup's coriolis key = a module that fully covers all its cards (every card
    # resolves). Among full-cover candidates prefer an exact blueprint-count match, then
    # display-name token overlap, then key name — and keep the assignment distinct so a
    # genuinely absent module is left unassigned (the 185<->186 delta).
    def candidate_keys(mg):
        cands = []
        for key in mod_keys:
            if all(resolve_in_key(key, c) is not None for c in mg["cards"]):
                cands.append(key)
        return cands

    def disp_tokens(key):
        toks = set()
        for fd in mod_keys[key]:
            for name in bps[fd]["modulename"]:
                toks |= set(b.slugify(name).split("-"))
        return toks

    assigned = {}
    used = set()
    # Assign the most-constrained modgroups first (fewest candidates) for a stable bijection.
    for mg in sorted(modgroups, key=lambda g: len(candidate_keys(g))):
        cands = [k for k in candidate_keys(mg) if k not in used]
        if not cands:
            cands = candidate_keys(mg)  # fall back (alias already used) — fdnames identical
        mslug_tokens = set(mg["mslug"].split("-"))

        def score(key):
            return (
                len(mod_keys[key]) == len(mg["cards"]),
                len(mslug_tokens & disp_tokens(key)),
                -len(mod_keys[key]),
                key,
            )

        best = max(cands, key=score)
        assigned[mg["mslug"]] = best
        used.add(best)

    # Build the editorial overlay + collect WARNs.
    editorial = {"modgroups": {}, "blueprints": {}}
    warn_unresolved = []
    covered = set()  # (key, fdname) instances represented on the page
    for mg in modgroups:
        key = assigned[mg["mslug"]]
        editorial["modgroups"][mg["mslug"]] = {
            "display": mg["display"],
            "section": mg["section"],
            "order": mg["order"],
        }
        for c in mg["cards"]:
            fd = resolve_in_key(key, c)
            if fd is None:
                warn_unresolved.append(
                    f"{mg['mslug']} / data-bp={c['data_bp']!r} -> no fdname")
                continue
            covered.add((key, fd))
            editorial["blueprints"][f"{mg['mslug']}/{fd}"] = {
                "title": c["title"],
                "effect": c["effect"],
                "suit": c["suit"],
                "ctx": c["ctx"],
            }

    # Data blueprints with no card = coriolis (module, fdname) instances no modgroup covers.
    warn_nocard = []
    for key, fdlist in mod_keys.items():
        for fd in fdlist:
            if (key, fd) not in covered:
                warn_nocard.append((key, fd))

    OUT.write_text(
        json.dumps(editorial, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")

    n_cards = sum(len(mg["cards"]) for mg in modgroups)
    print(f"modgroups: {len(modgroups)}")
    print(f"blueprint cards captured: {n_cards}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    if warn_unresolved:
        for w in warn_unresolved:
            print(f"WARN unresolved card: {w}")
    if warn_nocard:
        for key, fd in warn_nocard:
            mod_disp = bps[fd]["modulename"][0]
            print(f"WARN data blueprint with no card: "
                  f"module={key} ({mod_disp}) blueprint={fd} ({bps[fd]['name']})")
    if not warn_unresolved and not warn_nocard:
        print("WARN: none")


if __name__ == "__main__":
    main()
