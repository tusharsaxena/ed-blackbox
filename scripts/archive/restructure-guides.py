#!/usr/bin/env python3
# restructure-guides.py — move every guide into a folder that mirrors its
# index.html section/subsection, and rewrite ALL internal links so they resolve.
#
# Target tree (mirrors guides/index.html — see generate-guides-index.sh):
#   ships/general/                 rating-methodology, ship-role-matrix
#   ships/best-ships-by-role/      (was ships/by-role/)        7 ladders
#   ships/ship-dossiers/           (was ships/dossiers/)       128 dossiers
#   engineering/engineering-manuals/  checklist, engineers, blueprints, modules
#   engineering/materials-and-farming/ materials + 4 farms (flattened from farms/)
#   systems/new-pilot-and-interface/  new-cmdr-guide, pilots-federation, cmdrs-lexicon,
#                                     docking-landing-manual, hud-customization, third-party-apps
#   systems/galaxy-and-power-systems/ bgs, powerplay, superpower-rank, community-goals,
#                                     system-colonization, fleet-carrier
#   systems/activity-guides/       (was guides/activities/)    6 playbooks
#   systems/combat-venues/         combat-zones, pve-combat-venues
#
# WHAT IT DOES
#   - Builds the authoritative old->new path map for all 166 guides (relative to guides/).
#   - Rewrites every <a href>/<img|script|link src/href> in every moved HTML by
#     RESOLVE-THEN-RECOMPUTE: resolve the link against the file's OLD location to an
#     absolute target, remap the target if it is itself a moved guide (else leave it —
#     design-system/ images/ index.html don't move), then recompute the relative path
#     from the file's NEW location. Fragments (#id) are preserved. Byte-exact otherwise.
#   - Moves each HTML (+ its sibling <base>-anchors.md) and its data/sources/<...>.json
#     via `git mv` (history preserved). Source JSON + anchor .md carry no internal .html
#     links (verified), so only their location changes.
#   - SELF-VALIDATES: every rewritten internal guide link must resolve to a real
#     post-move target; any that doesn't is reported and (in --apply) aborts.
#
# It does NOT touch generators/tooling (generate-guides-index.sh and the path-coupled
# scripts) — those are updated separately, then `verify-links.py` is the final gate.
#
# USAGE
#   python3 scripts/restructure-guides.py --check   # dry run: plan + counts + validation
#   python3 scripts/restructure-guides.py --apply   # perform the move + rewrite
import os
import re
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
GUIDES = os.path.join(ROOT, "guides")
SOURCES = os.path.join(ROOT, "data", "sources")

ATTR_RE = re.compile(r'(\b(?:href|src)=")([^"]*)(")')
SKIP_SCHEMES = ("http://", "https://", "mailto:", "tel:", "data:", "//", "javascript:")


def posix(p):
    return p.replace(os.sep, "/")


# ---------------------------------------------------------------------------
# 1. Build the old->new map (POSIX, relative to guides/). index.html does NOT move.
# ---------------------------------------------------------------------------
def build_moves():
    moves = {}

    def add(old, new):
        assert old not in moves, old
        moves[old] = new

    # Ships — loose pages -> general/
    add("ships/rating-methodology.html", "ships/general/rating-methodology.html")
    add("ships/ship-role-matrix.html", "ships/general/ship-role-matrix.html")
    # Engineering manuals
    for p in ("checklist", "engineers", "blueprints", "modules"):
        add(f"engineering/{p}.html", f"engineering/engineering-manuals/{p}.html")
    # Materials (farms flattened in beside it below)
    add("engineering/materials.html", "engineering/materials-and-farming/materials.html")
    # Systems — New Pilot & Interface
    for p in ("new-cmdr-guide", "pilots-federation", "cmdrs-lexicon",
              "docking-landing-manual", "hud-customization", "third-party-apps"):
        add(f"systems/{p}.html", f"systems/new-pilot-and-interface/{p}.html")
    # Systems — Galaxy & Power Systems
    for p in ("bgs", "powerplay", "superpower-rank", "community-goals",
              "system-colonization", "fleet-carrier"):
        add(f"systems/{p}.html", f"systems/galaxy-and-power-systems/{p}.html")
    # Systems — Combat Venues
    for p in ("combat-zones", "pve-combat-venues"):
        add(f"systems/{p}.html", f"systems/combat-venues/{p}.html")

    # Directory-glob moves (rename / relocate whole folders)
    def map_dir(old_dir, new_dir):
        d = os.path.join(GUIDES, old_dir)
        for name in sorted(os.listdir(d)):
            if name.endswith(".html"):
                add(f"{old_dir}/{name}", f"{new_dir}/{name}")

    map_dir("ships/by-role", "ships/best-ships-by-role")
    map_dir("ships/dossiers", "ships/ship-dossiers")
    map_dir("engineering/farms", "engineering/materials-and-farming")  # flatten
    map_dir("activities", "systems/activity-guides")
    return moves


# ---------------------------------------------------------------------------
# 2. Link rewriter
# ---------------------------------------------------------------------------
def rewrite_links(text, old_rel, moves, new_set, unresolved):
    """Rewrite every href/src in `text` for a file moving old_rel -> moves[old_rel]."""
    new_rel = moves[old_rel]
    old_dir_abs = os.path.dirname(os.path.join(GUIDES, old_rel))
    new_dir_abs = os.path.dirname(os.path.join(GUIDES, new_rel))

    def repl(m):
        pre, val, post = m.group(1), m.group(2), m.group(3)
        low = val.lower()
        if val == "" or val.startswith("#") or low.startswith(SKIP_SCHEMES):
            return m.group(0)
        path_part, _, frag = val.partition("#")
        if path_part == "":  # pure fragment after split (shouldn't happen here)
            return m.group(0)
        # Resolve against OLD location
        tgt_abs = os.path.normpath(os.path.join(old_dir_abs, path_part))
        # Is the target a guide under guides/ ?
        try:
            tgt_rel = posix(os.path.relpath(tgt_abs, GUIDES))
        except ValueError:
            tgt_rel = None
        if tgt_rel is not None and not tgt_rel.startswith(".."):
            # target is inside guides/
            if tgt_rel in moves:
                new_tgt_abs = os.path.join(GUIDES, moves[tgt_rel])
            else:
                # index.html (stays) or some guides asset that isn't a moved page
                new_tgt_abs = tgt_abs
                if tgt_rel.endswith(".html") and tgt_rel != "index.html":
                    unresolved.append((old_rel, val, f"links to guides/{tgt_rel} (not in move map)"))
        else:
            new_tgt_abs = tgt_abs  # design-system/, images/, etc. — unchanged
        new_path = posix(os.path.relpath(new_tgt_abs, new_dir_abs))
        new_val = new_path + (("#" + frag) if frag else "")
        # Validate internal guide targets resolve in the post-move world
        if tgt_rel is not None and not tgt_rel.startswith(".."):
            final_rel = posix(os.path.relpath(new_tgt_abs, GUIDES))
            if final_rel.endswith(".html") and final_rel != "index.html" and final_rel not in new_set:
                unresolved.append((old_rel, val, f"-> {final_rel} missing post-move"))
        return pre + new_val + post

    new_text, n = ATTR_RE.subn(repl, text)
    return new_text, n


# ---------------------------------------------------------------------------
# 3. Driver
# ---------------------------------------------------------------------------
def git_mv(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    subprocess.run(["git", "-C", ROOT, "mv", src, dst], check=True)


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("--check", "--apply"):
        sys.exit("usage: restructure-guides.py --check | --apply")
    apply = sys.argv[1] == "--apply"

    moves = build_moves()
    new_set = set(moves.values())
    new_set.add("index.html")  # stays put

    # Sanity: every guide html (except index.html) is mapped exactly once.
    all_html = []
    for dp, _, fs in os.walk(GUIDES):
        for f in fs:
            if f.endswith(".html"):
                all_html.append(posix(os.path.relpath(os.path.join(dp, f), GUIDES)))
    mapped = set(moves) | {"index.html"}
    missing = sorted(set(all_html) - mapped)
    extra = sorted(set(moves) - set(all_html))
    if missing or extra:
        print("MAP MISMATCH:")
        for m in missing:
            print(f"  unmapped guide: {m}")
        for e in extra:
            print(f"  mapped but absent: {e}")
        sys.exit(1)

    # Rewrite pass (in memory), collecting validation problems.
    unresolved = []
    rewritten = {}  # old_rel -> (new_rel, new_text, nlinks)
    total_links = 0
    for old_rel in sorted(moves):
        with open(os.path.join(GUIDES, old_rel), encoding="utf-8") as fh:
            text = fh.read()
        new_text, n = rewrite_links(text, old_rel, moves, new_set, unresolved)
        rewritten[old_rel] = (moves[old_rel], new_text, n)
        total_links += n

    changed = sum(1 for o, (_, t, _) in rewritten.items()
                  if t != open(os.path.join(GUIDES, o), encoding="utf-8").read())

    print(f"guides to move      : {len(moves)}")
    print(f"files with link edits: {changed}")
    print(f"href/src scanned     : {total_links}")
    print(f"validation problems  : {len(unresolved)}")
    for o, v, why in unresolved[:40]:
        print(f"  ! {o}: {v}  {why}")
    print("\nsample rewrites (first 6 moves, first changed link each):")
    shown = 0
    for old_rel in sorted(moves):
        if shown >= 6:
            break
        nr, nt, _ = rewritten[old_rel]
        old_text = open(os.path.join(GUIDES, old_rel), encoding="utf-8").read()
        ol = ATTR_RE.findall(old_text)
        nl = ATTR_RE.findall(nt)
        diff = [(a[1], b[1]) for a, b in zip(ol, nl) if a[1] != b[1]]
        if diff:
            print(f"  {old_rel} -> {nr}")
            print(f"      {diff[0][0]}   =>   {diff[0][1]}")
            shown += 1

    if unresolved:
        print("\nABORT: unresolved links — fix the map/rewriter before applying.")
        sys.exit(2)

    if not apply:
        print("\n--check only; nothing written. Re-run with --apply to perform the move.")
        return

    # Apply: git mv html (+ sibling -anchors.md) + sources json, then write new content.
    moved_extra = 0
    for old_rel in sorted(moves):
        new_rel, new_text, _ = rewritten[old_rel]
        git_mv(os.path.join(GUIDES, old_rel), os.path.join(GUIDES, new_rel))
        with open(os.path.join(GUIDES, new_rel), "w", encoding="utf-8") as fh:
            fh.write(new_text)
        # sibling anchor catalog
        a_old = old_rel[:-5] + "-anchors.md"
        a_new = new_rel[:-5] + "-anchors.md"
        if os.path.exists(os.path.join(GUIDES, a_old)):
            git_mv(os.path.join(GUIDES, a_old), os.path.join(GUIDES, a_new))
            moved_extra += 1
        # mirrored sources json
        s_old = os.path.join(SOURCES, old_rel[:-5] + ".json")
        s_new = os.path.join(SOURCES, new_rel[:-5] + ".json")
        if os.path.exists(s_old):
            git_mv(s_old, s_new)
            moved_extra += 1

    print(f"\nAPPLIED: moved {len(moves)} guides + {moved_extra} sibling files (anchors/sources).")
    print("Next: update generators/tooling, then run verify-links.py as the gate.")


if __name__ == "__main__":
    main()
