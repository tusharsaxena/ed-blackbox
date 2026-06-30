#!/usr/bin/env python3
"""add-ship-render.py — drop a framed ship render into each dossier's briefing.

Implements the "Concept A" placement: the hull render rides at the right of the
briefing box (`.verdict.has-render`), with the stat-grid spanning full width beneath.
The matching component CSS lives in `design-system/css/ed-blackbox.css`
(`.ship-figure` / `.verdict.has-render`).

For each dossier in guides/ships/dossiers/ it:
  1. Derives the hull render from the dossier slug — strips the role suffix
     (-combat, -exploration, …) and collapses "mk-<roman>" to "mk<roman>" to match
     the image filenames (cobra-mk-iii -> cobra-mkiii.jpg). Dossiers whose render
     does not exist in images/ships/ are SKIPPED and listed (currently only
     cobra-mk-iv, which has no render).
  2. Reads the display name from scripts/ship-names.tsv and the manufacturer from
     the page's own kicker (`… // <Manufacturer>`) for the caption.
  3. Wraps the briefing's eyebrow/heading/copy in `.v-body`, inserts the
     `<figure class="ship-figure">` before the stat-grid, and adds `has-render`
     to the `.verdict`.

Idempotent: a dossier already carrying `verdict has-render` (or a `.ship-figure`)
is left untouched, so it is safe to re-run after adding a missing render.

Usage:
  python3 scripts/add-ship-render.py            # edit all dossiers in place
  python3 scripts/add-ship-render.py --check     # report what WOULD change, write nothing
"""

import os
import re
import sys
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOSSIERS = os.path.join(ROOT, "guides", "ships", "dossiers")
IMAGES = os.path.join(ROOT, "images", "ships")
NAMES_TSV = os.path.join(ROOT, "scripts", "ship-names.tsv")

ROLE_SUFFIXES = ("-multipurpose", "-combat", "-exploration", "-ax",
                 "-trading", "-mining", "-passenger")
KICKER_RE = re.compile(r'<div class="kicker">.*?</span>\s*(.*?)\s*</div>', re.S)


def hull_slug(slug):
    for r in ROLE_SUFFIXES:
        if slug.endswith(r):
            return slug[:-len(r)]
    return slug


def render_name(slug):
    """Image basename (no extension) for a dossier slug, or None if no render exists."""
    cand = hull_slug(slug).replace("-mk-", "-mk")
    return cand if os.path.isfile(os.path.join(IMAGES, cand + ".jpg")) else None


def load_names():
    names = {}
    with open(NAMES_TSV, encoding="utf-8") as fh:
        for line in fh:
            if "\t" in line:
                k, v = line.rstrip("\n").split("\t", 1)
                names[k] = v
    return names


def figure_block(render, display, manufacturer):
    return (
        '    <figure class="ship-figure">\n'
        f'      <img src="../../../images/ships/{render}.jpg" alt="{display}" width="160" height="90">\n'
        f'      <figcaption><b>{display}</b> &middot; {manufacturer}</figcaption>\n'
        '    </figure>\n'
    )


def transform(html, figure):
    """Wrap the briefing body in .v-body, insert the figure, add has-render."""
    open_tag = '<div class="verdict">'
    i = html.index(open_tag)
    line_end = html.index("\n", i)                 # end of the verdict-open line
    sg = html.index('<div class="stat-grid">', line_end)
    head = html[line_end + 1:sg]                    # eyebrow/h2/p… + stat-grid indent
    lines = head.split("\n")
    body_lines, indent = lines[:-1], lines[-1]      # last line is the stat-grid's indent
    reindented = "".join(("  " + ln if ln.strip() else ln) + "\n" for ln in body_lines)
    new_head = (
        '    <div class="v-body">\n'
        + reindented
        + '    </div>\n'
        + figure
        + indent
    )
    return html[:i] + '<div class="verdict has-render">\n' + new_head + html[sg:]


def main():
    check = "--check" in sys.argv
    names = load_names()
    files = sorted(glob.glob(os.path.join(DOSSIERS, "*.html")))
    changed, skipped_done, skipped_norender = 0, 0, []
    for f in files:
        slug = os.path.basename(f)[:-5]
        html = open(f, encoding="utf-8").read()
        if "verdict has-render" in html or 'class="ship-figure"' in html:
            skipped_done += 1
            continue
        render = render_name(slug)
        if render is None:
            skipped_norender.append(slug)
            continue
        m = KICKER_RE.search(html)
        manufacturer = m.group(1) if m else ""
        display = names.get(hull_slug(slug), hull_slug(slug))
        out = transform(html, figure_block(render, display, manufacturer))
        changed += 1
        if check:
            print(f"would add render ({render}.jpg): {slug}")
        else:
            open(f, "w", encoding="utf-8").write(out)
            print(f"added render ({render}.jpg): {slug}")
    verb = "would change" if check else "changed"
    print(f"\n{len(files)} dossiers | {changed} {verb} | "
          f"{skipped_done} already done | {len(skipped_norender)} no render: "
          f"{skipped_norender or 'none'}")


if __name__ == "__main__":
    main()
