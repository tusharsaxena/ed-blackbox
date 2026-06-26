#!/usr/bin/env python3
"""build-link-dictionary.py — extract the canonical hyperlink targets.

Parses the seven "source" families and emits a machine-readable dictionary of
every linkable element (id + anchor + canonical label + seed surface forms).
This is the *base* dictionary; surface-form/alias curation and disambiguation
rules are layered on by the family sub-agents (see build-link-dictionary.md),
producing the final data/links/link-dictionary.json the applier consumes.

Families & anchor schemes:
    engineers     guides/engineering/engineers.html      #engineer-<slug>
    blueprint-grp guides/engineering/blueprints.html      #blueprint-group-<slug>
    blueprint     guides/engineering/blueprints.html      #blueprint-<group>-<effect>
    module        guides/engineering/modules.html         #module-<slug> (not -group-)
    material      guides/engineering/materials.html       #section-<slug> (page is coarse)
    powerplay     guides/systems/powerplay.html           #powerplay-<slug>
    superpower    guides/systems/superpower-rank.html     #superpower-<fed|emp|all>
    ship-dossier  guides/ships/dossiers/<ship>-<role>.html

Usage:  python3 scripts/build-link-dictionary.py [--out PATH]
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
G = ROOT / "guides"
OUT_DEFAULT = ROOT / "data" / "links" / "link-dictionary.base.json"

ROLES = ["multipurpose", "combat", "exploration", "trading", "mining", "passenger", "ax"]
# acronym fixes for slug->label title-casing
ACR = {"fsd": "FSD", "afmu": "AFMU", "ax": "AX", "scb": "SCB", "ii": "II", "iii": "III",
       "iv": "IV", "v": "V", "mk": "Mk", "dss": "DSS", "hrp": "HRP", "mrp": "MRP"}


def titleize(slug: str) -> str:
    words = []
    for w in slug.split("-"):
        words.append(ACR.get(w.lower(), w.capitalize()))
    return " ".join(words)


def soup_of(p: Path) -> BeautifulSoup:
    return BeautifulSoup(p.read_text(encoding="utf-8"), "lxml")


def lead_text(el) -> str:
    """First chunk of an element's text, collapsed, before a ' #' / count marker."""
    t = " ".join(el.get_text(" ", strip=True).split())
    return t


def engineers(entries):
    p = G / "engineering" / "engineers.html"
    soup = soup_of(p)
    rel = p.relative_to(G).as_posix()
    for el in soup.select('[id^="engineer-"]'):
        eid = el["id"]
        name = re.split(r"\s+#", lead_text(el))[0].strip()
        forms = {name}
        # strip a quoted nickname:  Tod "The Blaster" McQuinn -> Tod McQuinn
        n = re.sub(r'\s*"[^"]+"\s*', " ", name).strip()
        forms.add(re.sub(r"\s{2,}", " ", n))
        entries.append(dict(id=eid, family="engineer", file=rel, anchor=eid,
                            label=name, surface_forms=sorted(forms), confidence=0.9))


def blueprints(entries):
    p = G / "engineering" / "blueprints.html"
    soup = soup_of(p)
    rel = p.relative_to(G).as_posix()
    group_slugs = []
    for el in soup.select('[id^="blueprint-group-"]'):
        gid = el["id"]
        slug = gid[len("blueprint-group-"):]
        group_slugs.append(slug)
        label = titleize(slug)
        entries.append(dict(id=gid, family="blueprint-group", file=rel, anchor=gid,
                            label=label, surface_forms=[label], confidence=0.85,
                            group_slug=slug))
    group_slugs.sort(key=len, reverse=True)  # longest match first
    for el in soup.select('[id^="blueprint-"]'):
        bid = el["id"]
        if bid.startswith("blueprint-group-"):
            continue
        rest = bid[len("blueprint-"):]
        grp = next((g for g in group_slugs if rest.startswith(g + "-")), None)
        effect = rest[len(grp) + 1:] if grp else rest
        eff_label = titleize(effect)
        grp_label = titleize(grp) if grp else ""
        entries.append(dict(id=bid, family="blueprint", file=rel, anchor=bid,
                            label=f"{eff_label} ({grp_label})" if grp_label else eff_label,
                            effect=eff_label, group=grp_label,
                            surface_forms=[eff_label], confidence=0.75))


def modules(entries):
    p = G / "engineering" / "modules.html"
    soup = soup_of(p)
    rel = p.relative_to(G).as_posix()
    for el in soup.select('[id^="module-"]'):
        mid = el["id"]
        if mid.startswith("module-group-"):
            continue
        slug = mid[len("module-"):]
        label = titleize(slug)
        entries.append(dict(id=mid, family="module", file=rel, anchor=mid,
                            label=label, surface_forms=[label], confidence=0.85))


def materials(entries):
    p = G / "engineering" / "materials.html"
    rel = p.relative_to(G).as_posix()
    # only section-level anchors exist; expose the page + a few useful sections
    for slug, label in [("section-raw", "Raw Materials"),
                        ("section-manufactured", "Manufactured Materials"),
                        ("section-encoded", "Encoded Materials"),
                        ("section-trader", "Material Trader"),
                        ("section-grades", "Material Grades")]:
        entries.append(dict(id=slug, family="material-section", file=rel, anchor=slug,
                            label=label, surface_forms=[label], confidence=0.7))


def powerplay(entries):
    p = G / "systems" / "powerplay.html"
    soup = soup_of(p)
    rel = p.relative_to(G).as_posix()
    for el in soup.select('[id^="powerplay-"]'):
        pid = el["id"]
        name = re.split(r"\s+#", lead_text(el))[0].strip()
        entries.append(dict(id=pid, family="powerplay", file=rel, anchor=pid,
                            label=name, surface_forms=[name], confidence=0.9))


def superpowers(entries):
    p = G / "systems" / "superpower-rank.html"
    rel = p.relative_to(G).as_posix()
    for sid, label, alt in [("superpower-fed", "Federation", ["Federal"]),
                            ("superpower-emp", "Empire", ["Imperial"]),
                            ("superpower-all", "Alliance", [])]:
        entries.append(dict(id=sid, family="superpower", file=rel, anchor=sid,
                            label=label, surface_forms=[label] + alt, confidence=0.75))


def ships(entries, ships_map):
    ddir = G / "ships" / "dossiers"
    for f in sorted(ddir.glob("*.html")):
        base = f.stem
        role = next((r for r in ROLES if base.endswith("-" + r)), None)
        ship_slug = base[: -(len(role) + 1)] if role else base
        soup = soup_of(f)
        h1 = soup.select_one("h1.title") or soup.select_one("h1")
        name = ""
        if h1:
            # drop the .role tag span text, keep the ship name
            for sp in h1.select(".role"):
                sp.extract()
            name = " ".join(h1.get_text(" ", strip=True).split())
        if not name:
            name = titleize(ship_slug)
        m = ships_map.setdefault(ship_slug, {"name": name, "roles": {}})
        m["name"] = name or m["name"]
        m["roles"][role or "default"] = f"ships/dossiers/{base}.html"
    # choose a default role per ship by priority
    for slug, m in ships_map.items():
        m["default_role"] = next((r for r in ROLES if r in m["roles"]),
                                 next(iter(m["roles"])))


def main():
    out = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else OUT_DEFAULT
    entries, ships_map = [], {}
    engineers(entries)
    blueprints(entries)
    modules(entries)
    materials(entries)
    powerplay(entries)
    superpowers(entries)
    ships(entries, ships_map)

    out.parent.mkdir(parents=True, exist_ok=True)
    data = dict(entries=entries, ships=ships_map)
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    from collections import Counter
    fam = Counter(e["family"] for e in entries)
    print(f"wrote {out.relative_to(ROOT)}")
    for k, v in sorted(fam.items()):
        print(f"  {k:16} {v}")
    print(f"  {'ships':16} {len(ships_map)} hulls, {sum(len(m['roles']) for m in ships_map.values())} dossiers")


if __name__ == "__main__":
    main()
