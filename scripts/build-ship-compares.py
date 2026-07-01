#!/usr/bin/env python3
"""build-ship-compares.py — generate the §4 "How It Compares" section of ship dossiers.

The §4 tables were hand-authored per dossier and drifted: incomplete same-class
lists, ships filed under the wrong pad class, missing other-class sections. This
renders §4 deterministically from the canonical ratings + coriolis ship data so
it is always complete and class-correct:

  - "Same class — <class> <role> ships": every role-rated (>=40, has-dossier) hull
    of THIS hull's pad class, this hull shown as the `this` baseline row.
  - "Other classes — <name>": the two OTHER pad classes, each its own named section
    with a short editorial takeaway.

Pros/cons are auto-derived from each peer ship's scorecard (top factors = pros,
weakest = con, plus a higher/lower-rated note vs this hull). Ratings, pad classes,
hardpoint profiles and cargo come from data — nothing is invented.

Modes:
  python3 scripts/build-ship-compares.py               # all dossiers with a role rating
  python3 scripts/build-ship-compares.py krait-phantom-combat  # matching basenames
  python3 scripts/build-ship-compares.py --check       # preview changes, write nothing
"""
import json
import re
import sys
import glob
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RATINGS = ROOT / "data" / "ship-ratings"
SHIPS = ROOT / "data" / "ships"
DOSS = ROOT / "guides" / "ships" / "ship-dossiers"
CUTOFF = 40

ROLES = ["combat", "ax", "mining", "trading", "exploration", "passenger", "multipurpose"]
ROLE_LABEL = {"combat": "combat", "ax": "AX", "mining": "mining", "trading": "trading",
              "exploration": "exploration", "passenger": "passenger", "multipurpose": "multipurpose"}

PAD = {
    "Small": ["Adder", "Cobra Mk III", "Cobra Mk IV", "Cobra Mk V", "Diamondback Explorer",
              "Diamondback Scout", "Dolphin", "Eagle Mk II", "Hauler", "Imperial Courier",
              "Imperial Eagle", "Kestrel Mk II", "Sidewinder Mk I", "Viper Mk III", "Viper Mk IV", "Vulture"],
    "Medium": ["Alliance Challenger", "Alliance Chieftain", "Alliance Crusader", "Asp Explorer",
               "Asp Scout", "Corsair", "Federal Assault Ship", "Federal Dropship", "Federal Gunship",
               "Fer-de-Lance", "Keelback", "Krait Mk II", "Krait Phantom", "Mamba", "Mandalay",
               "Python", "Python Mk II", "Type-6 Transporter", "Type-8 Transporter", "Type-11 Prospector"],
    "Large": ["Anaconda", "Beluga Liner", "Caspian Explorer", "Federal Corvette", "Imperial Clipper",
              "Imperial Cutter", "Orca", "Panther Clipper Mk II", "Type-7 Transporter", "Type-9 Heavy",
              "Type-10 Defender"],
}
PAD_OF = {s: p for p, ss in PAD.items() for s in ss}
PAD_PILL = {"Small": "pad-small", "Medium": "pad-medium", "Large": "pad-large"}

# section name for the OTHER-class tables, by role x class
OTHER_NAME = {
    "combat":       {"Large": "the heavy hitters",        "Medium": "the versatile mediums",   "Small": "the light fighters"},
    "ax":           {"Large": "the capital AX platforms", "Medium": "the medium AX fighters",  "Small": "the light AX skirmishers"},
    "mining":       {"Large": "the capital barges",       "Medium": "the medium miners",       "Small": "the small-pad prospectors"},
    "trading":      {"Large": "the bulk freighters",      "Medium": "the medium haulers",      "Small": "the small-pad haulers"},
    "exploration":  {"Large": "the long-range flagships", "Medium": "the medium explorers",    "Small": "the pocket explorers"},
    "passenger":    {"Large": "the liners",               "Medium": "the medium tourers",      "Small": "the shuttle-class"},
    "multipurpose": {"Large": "the capital all-rounders", "Medium": "the medium all-rounders", "Small": "the small all-rounders"},
}
# the stat column header + how it's computed
STAT_HDR = {"combat": "Hardpoints", "ax": "Hardpoints", "trading": "Max cargo", "mining": "Max cargo",
            "multipurpose": "Max cargo", "exploration": "Optional cap.", "passenger": "Cabin cap."}
STAT_DESC = {"combat": "the hardpoint loadout — the basis for a weapon suite",
             "ax": "the hardpoint loadout — the mount count for a Gauss suite",
             "trading": "maximum cargo tonnage behind a shield",
             "mining": "maximum ore-hold tonnage",
             "multipurpose": "maximum cargo tonnage — a proxy for internal room",
             "exploration": "total optional-internal capacity — room for scanners, AFMU and fuel",
             "passenger": "total optional-internal capacity — room for cabins"}

ALIAS = {"Eagle Mk II": "Eagle", "Sidewinder Mk I": "Sidewinder", "Viper Mk III": "Viper"}


def load_ship_stats():
    def sz(x):
        return x if isinstance(x, int) else x.get("class", 0)
    stats = {}
    for f in SHIPS.glob("*.json"):
        v = list(json.loads(f.read_text()).values())[0]
        p = v["properties"]; s = v["slots"]
        hp = [sz(x) for x in s["hardpoints"] if sz(x) > 0]
        internal = [x for x in s["internal"] if isinstance(x, int)]
        from collections import Counter
        c = Counter(hp); m = {4: "H", 3: "L", 2: "M", 1: "S"}
        prof = " ".join(f"{c[k]}{m[k]}" for k in (4, 3, 2, 1) if c[k]) or "—"
        stats[p["name"]] = {"hp": prof, "cargo": sum(2 ** x for x in internal)}
    return stats


def stat_value(role, ship, stats):
    m = stats.get(ALIAS.get(ship, ship)) or stats.get(ship)
    if not m:
        return "—"
    if role in ("combat", "ax"):
        return m["hp"]
    return f"~{m['cargo']} t"


SHORT = {  # trim long scorecard factor names for the pros/cons capsule
    "Hardpoints for Gauss": "Gauss mounts", "Heat capacity & management": "heat",
    "Hull tank & reinforcement room": "hull tank", "Caustic handling & support slots": "caustic kit",
    "Power distributor": "distributor", "Armour & internals": "armour",
    "Utility & flexibility": "flexibility", "Effective ore capacity": "ore hold",
    "Tool & slot fit": "tool fit", "Pad class & access": "pad access",
    "Cost & specialisation": "value", "Maximum cargo": "cargo", "Pad class & market reach": "reach",
    "Laden jump range": "laden range", "Speed & cost": "speed/value",
    "Engineered jump range": "jump range", "Heat profile": "heat", "Fuel tank & reach": "fuel reach",
    "Canopy & visibility": "canopy", "Comfort & cost": "comfort/value",
    "Cabin capacity & class fit": "cabins", "Comfort": "comfort", "Jump range & tank": "range",
    "Shield & safety": "shield", "Pad class & cost": "pad/cost", "Breadth of internals": "internals",
    "Firepower": "firepower", "Jump range": "range", "Flexibility & re-fit cost": "flexibility",
    "Survivability & handling": "survivability", "Survivability": "survivability", "Shield": "shield",
    "Agility": "agility", "Hardpoints": "hardpoints", "Internals": "internals",
}


def short(f):
    return SHORT.get(f, f[:1].lower() + f[1:])


def pros_cons(peer_card, peer_rating, this_rating, weights):
    """Derive terse pros/cons from a peer's scorecard vs this hull.

    Strength of a factor = earned / weight (how fully it maxed that dimension),
    so a small-weight factor scored full counts as a strength. Top two ratios are
    pros, the weakest is the con, plus a higher/lower-rated note vs this hull.
    """
    pros, cons = [], []
    if peer_card:
        ranked = sorted(peer_card["factors"],
                        key=lambda f: -(f["earned"] / max(weights.get(f["factor"], 1), 1)))
        pros = [short(f["factor"]) for f in ranked[:2]]
        cons = [short(ranked[-1]["factor"])]
    p = (["higher-rated"] if peer_rating > this_rating else []) + pros
    c = (["lower-rated"] if peer_rating < this_rating else []) + cons
    cap = lambda s: (s[:1].upper() + s[1:]) if s else s
    return cap("; ".join(p[:3])), cap("; ".join(c[:2]))


def bar(n):
    return f'<span class="rscore">{n}</span><div class="bar mini"><i style="--pct:{n}"></i></div>'


def row(role, ship, rating, dossier, this_ship, this_rating, stats, card, weights):
    pill = PAD_PILL[PAD_OF.get(ship, "Medium")]
    cls = PAD_OF.get(ship, "Medium")
    sv = stat_value(role, ship, stats)
    if ship == this_ship:
        return (f'<tr><td class="mod">{ship} <span class="pill md">this</span></td>'
                f'<td><span class="pill {pill}">{cls}</span></td><td>{sv}</td>'
                f'<td class="pcc"><span class="base">&mdash; this hull (baseline)</span></td>'
                f'<td>{bar(rating)}</td></tr>')
    p, c = pros_cons(card, rating, this_rating, weights)
    return (f'<tr><td class="mod"><a href="{dossier}">{ship}</a></td>'
            f'<td><span class="pill {pill}">{cls}</span></td><td>{sv}</td>'
            f'<td class="pcc"><span class="p">{p}</span><span class="c">{c}</span></td>'
            f'<td>{bar(rating)}</td></tr>')


def table(role, rows_html):
    return ('<div class="tbl-scroll nolink">\n    <table class="cmp">\n'
            '      <colgroup><col style="width:17%"><col style="width:9%"><col style="width:16%">'
            '<col style="width:46%"><col style="width:12%"></colgroup>\n'
            f'      <thead><tr><th>Ship</th><th>Class</th><th>{STAT_HDR[role]}</th>'
            f'<th>Pros &amp; cons</th><th>Rating</th></tr></thead>\n'
            f'      <tbody>\n{rows_html}\n      </tbody>\n    </table>\n    </div>')


def section_body(role, this_ship, this_rating, by_class, stats, weights):
    order = ["Large", "Medium", "Small"]
    this_class = PAD_OF.get(this_ship, "Medium")
    intro = (f'    <p>Every table rates ships <em>for {ROLE_LABEL[role]} specifically</em>, '
             f'split by landing-pad class. The <b>{STAT_HDR[role]}</b> column is {STAT_DESC[role]}; '
             f'the rating is the same 1&ndash;100 suitability verdict used across the site.</p>')
    parts = [intro]

    def rows_for(cls):
        out = []
        for rating, ship, dossier, card in by_class.get(cls, []):
            out.append("        " + row(role, ship, rating, dossier, this_ship, this_rating, stats, card, weights))
        return "\n".join(out)

    def lead_b(lead):
        # bold, linked to the lead's dossier (unless it IS this hull) so the site-wide
        # hyperlink pass leaves the blurb alone (it skips existing <a>).
        if lead[1] == this_ship:
            return f'<b>{lead[1]}</b>'
        return f'<b><a href="{lead[2]}">{lead[1]}</a></b>'

    # same class
    sc_rows = rows_for(this_class)
    parts.append(f'    <h3 class="subhead">Same class &mdash; {this_class.lower()} {ROLE_LABEL[role]} ships</h3>')
    parts.append("    " + table(role, sc_rows))
    n_same = len(by_class.get(this_class, []))
    top = by_class.get(this_class, [])
    lead = top[0] if top else None
    parts.append(f'    <p class="nolink">{n_same} {this_class.lower()}-pad {ROLE_LABEL[role]} hulls carry a rating, '
                 + (f'led by {lead_b(lead)} ({lead[0]}). ' if lead else '')
                 + f'Every same-pad rival lands where this one does &mdash; the direct field to shop.</p>')

    # other classes (the two that aren't this_class), Large-first then Small
    for cls in [c for c in order if c != this_class]:
        rows = by_class.get(cls, [])
        if not rows:
            continue
        name = OTHER_NAME[role][cls]
        parts.append(f'    <h3 class="subhead">Other classes &mdash; {name}</h3>')
        parts.append("    " + table(role, rows_for(cls)))
        lead = rows[0]
        cmp = ("out-muscle" if cls == "Large" else "undercut")
        note = ("bigger pads and bankrolls" if cls == "Large" else "cheaper hulls and tighter pads")
        parts.append(f'    <p class="nolink">The {cls.lower()}-pad {ROLE_LABEL[role]} field ({len(rows)} rated), '
                     f'led by {lead_b(lead)} ({lead[0]}) &mdash; {note}. They {cmp} this hull on '
                     f'the numbers, but sit a pad class away.</p>')
    return "\n".join(parts)


def load_matrix():
    data = {}   # role -> class -> [(rating, ship, dossier, scorecard)]
    ship_role = {}  # dossier-basename -> (ship, role, rating)
    for r in ROLES:
        j = json.loads((RATINGS / f"{r}.json").read_text())
        for it in j["ratings"]:
            if it["ship"] == "Python (original)":
                continue
            if not it.get("dossier") or it["rating"] < CUTOFF:
                continue
            cls = PAD_OF.get(it["ship"], "Medium")
            data.setdefault(r, {}).setdefault(cls, []).append(
                (it["rating"], it["ship"], it["dossier"], it.get("scorecard")))
            ship_role[it["dossier"][:-5]] = (it["ship"], r, it["rating"])
    for r in data:
        for cls in data[r]:
            data[r][cls].sort(key=lambda t: (-t[0], t[1]))
    return data, ship_role


SEC_OPEN = '<section id="section-how-it-compares">'


def splice(html, body):
    i = html.find(SEC_OPEN)
    if i < 0:
        return None
    sh = html.find('<div class="sec-head"', i)
    sh_end = html.find("</div>", sh) + len("</div>")
    close = html.find("</section>", sh_end)
    return html[:sh_end] + "\n" + body + "\n  " + html[close:]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check = "--check" in sys.argv
    stats = load_ship_stats()
    data, ship_role = load_matrix()
    weights = {r: {w['factor']: w['weight'] for w in json.loads((RATINGS / f'{r}.json').read_text())['scorecard_weights']} for r in ROLES}

    targets = sorted(ship_role) if not args else \
        [b for b in ship_role if any(a in b for a in args)]
    changed = 0
    for base in targets:
        ship, role, rating = ship_role[base]
        page = DOSS / f"{base}.html"
        if not page.exists():
            continue
        html = page.read_text(encoding="utf-8")
        body = section_body(role, ship, rating, data[role], stats, weights[role])
        new = splice(html, body)
        if new is None:
            print(f"  ! no §4 section: {base}")
            continue
        if new != html:
            changed += 1
            if check:
                print(f"  would update {base}")
            else:
                page.write_text(new, encoding="utf-8")
                print(f"  updated {base} ({ship} · {role})")
    print(f"\n{'DRY-RUN ' if check else ''}done — {changed}/{len(targets)} dossiers")


if __name__ == "__main__":
    main()
