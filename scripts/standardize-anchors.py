#!/usr/bin/env python3
# standardize-anchors.py
# -----------------------------------------------------------------------------
# Standardizes every NAVIGATION anchor across the guides onto one
# `<family>-<slug>` scheme, and rewrites every internal hyperlink to match.
# Design + full rules: docs/superpowers/specs/2026-06-24-anchor-standardization-design.md
#
# The rewrite is split so it can be driven (and verified) in phases:
#
#   --build-map            Build {file: {old_id: new_id}} from the CURRENT (pre-rename)
#                          HTML and write it to --map (default: scratchpad). Prints a
#                          summary; EXITS NONZERO on any per-page collision or any
#                          unclassified id-bearing nav element. Run this FIRST.
#   --phase1               Load --map; rewrite id="old"->id="new" in HTML + templates;
#                          patch generate-guides-index.sh (index ids + same-page hrefs).
#   --phase2               Load --map; rewrite every href "...#old"->"...#new" in HTML +
#                          templates, and the #ids in the 2 curated *-anchors.md catalogs.
#   --verify               Map-free integrity scan of the CURRENT files: every internal
#                          href#anchor must resolve to an existing id on its target page;
#                          report any leftover old-scheme id/href. EXITS NONZERO on failure.
#
# The map is built once (from original ids) and REUSED by phase1/phase2 — phase2 cannot
# rebuild it because phase1 has already renamed the ids.
#
# USAGE
#   python3 scripts/standardize-anchors.py --build-map --map /path/anchor-map.json
#   python3 scripts/standardize-anchors.py --phase1   --map /path/anchor-map.json
#   bash scripts/generate-anchor-files.sh
#   bash scripts/generate-guides-index.sh
#   python3 scripts/standardize-anchors.py --phase2   --map /path/anchor-map.json
#   python3 scripts/standardize-anchors.py --verify
# -----------------------------------------------------------------------------
import os, re, sys, json, argparse, html

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(SCRIPT_DIR)
GUIDES = os.path.join(REPO, "guides")
GEN_INDEX = os.path.join(REPO, "scripts", "generate-guides-index.sh")
TEMPLATES = [
    os.path.join(REPO, "design-system", "templates", "starter-page.html"),
    os.path.join(REPO, "design-system", "templates", "component-gallery.html"),
]
CURATED_MD = {
    # curated catalog  ->  the page whose map rewrites its #ids
    os.path.join(GUIDES, "engineering", "engineering-manuals", "engineers-anchors.md"):  "engineering/engineering-manuals/engineers.html",
    os.path.join(GUIDES, "engineering", "engineering-manuals", "blueprints-anchors.md"): "engineering/engineering-manuals/blueprints.html",
}

# --- regexes -----------------------------------------------------------------
# A start tag, tolerant of quoted attribute values that may contain '>'.
TAG_RE  = re.compile(r'<([a-zA-Z][a-zA-Z0-9]*)((?:"[^"]*"|\'[^\']*\'|[^>"\'])*?)\sid="([^"]+)"((?:"[^"]*"|\'[^\']*\'|[^>"\'])*)>')
HREF_RE = re.compile(r'href="([^"]*#[^"]+)"')
H_RE    = re.compile(r'<h[1-6][^>]*>(.*?)</h[1-6]>', re.DOTALL | re.IGNORECASE)
CLASS_RE= re.compile(r'class="([^"]*)"')

OLD_PREFIX_SCAN = ("eng-", "grp-", "bp-", "pw-", "pow-", "mod-", "wpn-",
                   "util-", "unlock-", "refer-", "grind-", "farm-", "prep-",
                   "build-", "travel-", "sec-")

def list_html():
    out = []
    for dp, _, fs in os.walk(GUIDES):
        for f in fs:
            if f.endswith(".html"):
                out.append(os.path.join(dp, f))
    out += [t for t in TEMPLATES if os.path.exists(t)]
    return sorted(out)

def relkey(path):
    """Canonical key: relative to guides/ for guides; 'tmpl:<name>' for templates."""
    if path.startswith(GUIDES + os.sep):
        return os.path.relpath(path, GUIDES).replace(os.sep, "/")
    return "tmpl:" + os.path.basename(path)

def slugify(text):
    text = re.sub(r'<[^>]+>', '', text)          # strip inline tags
    text = html.unescape(text)
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def first_heading_slug(body, tag_end):
    m = H_RE.search(body, tag_end)
    if m:
        s = slugify(m.group(1))
        if s:
            return s
    return None

def classify(relk, tag, classes, oid, body, tag_end):
    """Return ('rename', new_id) | ('skip', reason) | ('unknown', None)."""
    tag = tag.lower()
    cset = set(classes.split())

    # --- excluded functional / widget / diagram ids (any page) ---
    if oid.startswith("qn-"):           return ("skip", "quicknav-widget")
    if oid == "toc":                    return ("skip", "scrollspy-container")
    if relk == "engineering/engineering-manuals/checklist.html":
        if oid in ("emap-inner", "wires"):              return ("skip", "unlock-map-structural")
        if oid.startswith("n-") and "enode" in cset:    return ("skip", "diagram-node")
        if oid.startswith("c-") and "echip" in cset:    return ("skip", "diagram-chip")

    # --- Sections: any <section>, or a heading used as a subhead anchor ---
    if tag == "section" or (re.fullmatch(r'h[1-6]', tag) and "subhead" in cset):
        if re.fullmatch(r's\d+', oid):
            s = first_heading_slug(body, tag_end)
            base = s if s else oid          # fall back to the raw id if no heading
        elif oid.startswith("sec-"):
            base = oid[len("sec-"):]
        elif oid.startswith("grp-"):
            base = oid[len("grp-"):]        # engineers.html tier sections
        else:
            base = oid
        return ("rename", "section-" + base)

    # --- typed families (page + element aware) ---
    if relk == "engineering/engineering-manuals/engineers.html" and tag == "article" and oid.startswith("eng-"):
        return ("rename", "engineer-" + oid[len("eng-"):])

    if relk == "engineering/engineering-manuals/checklist.html" and tag == "article":
        if oid.startswith("unlock-"): return ("rename", "engineer-unlock-" + oid[len("unlock-"):])
        if oid.startswith("refer-"):  return ("rename", "engineer-refer-"  + oid[len("refer-"):])
        for p in ("grind-", "farm-", "prep-", "build-", "travel-"):
            if oid.startswith(p):     return ("rename", "step-" + oid)

    if relk == "engineering/engineering-manuals/blueprints.html" and tag == "div":
        if oid.startswith("grp-"): return ("rename", "blueprint-group-" + oid[len("grp-"):])
        if oid.startswith("bp-"):  return ("rename", "blueprint-" + oid[len("bp-"):])

    if relk == "engineering/engineering-manuals/modules.html" and tag == "div":
        if "bp-modgroup" in cset and oid.startswith("grp-"):
            return ("rename", "module-group-" + oid[len("grp-"):])
        if "bp-card" in cset:
            for p in ("mod-", "wpn-", "util-"):
                if oid.startswith(p): return ("rename", "module-" + oid[len(p):])

    if relk == "systems/galaxy-and-power-systems/powerplay.html" and tag == "article" and oid.startswith("pw-"):
        return ("rename", "powerplay-" + oid[len("pw-"):])
    if relk == "systems/galaxy-and-power-systems/superpower-rank.html" and tag == "article" and oid.startswith("pow-"):
        return ("rename", "superpower-" + oid[len("pow-"):])
    if relk == "systems/new-pilot-and-interface/third-party-apps.html" and tag == "article" and oid.startswith("app-"):
        return ("skip", "already-app")

    # templates: treat their sections like guides (handled above); anything else here
    if relk.startswith("tmpl:"):
        return ("skip", "template-other")

    return ("unknown", None)

def build_map():
    fmap, skips, unknowns = {}, [], []
    for path in list_html():
        relk = relkey(path)
        body = open(path, encoding="utf-8", errors="replace").read()
        page = {}
        for m in TAG_RE.finditer(body):
            tag, pre, oid, post = m.group(1), m.group(2), m.group(3), m.group(4)
            cm = CLASS_RE.search(pre) or CLASS_RE.search(post)
            classes = cm.group(1) if cm else ""
            kind, new = classify(relk, tag, classes, oid, body, m.end())
            if kind == "rename":
                if new != oid:
                    page[oid] = new
            elif kind == "skip":
                skips.append((relk, oid, new))
            else:
                unknowns.append((relk, tag, oid))
        if page:
            fmap[relk] = page
    return fmap, skips, unknowns

def find_collisions(fmap):
    bad = []
    for relk, page in fmap.items():
        seen = {}
        for old, new in page.items():
            seen.setdefault(new, []).append(old)
        for new, olds in seen.items():
            if len(olds) > 1:
                bad.append((relk, new, olds))
    return bad

# --- application -------------------------------------------------------------
def rewrite_ids(text, page):
    n = 0
    for old, new in page.items():
        pat = re.compile(r'(?<=\s)id="' + re.escape(old) + r'"')
        text, c = pat.subn('id="' + new + '"', text)
        n += c
    return text, n

def resolve_target(curkey, path_part):
    """Map an href path to a canonical map key (guides-relative)."""
    if curkey.startswith("tmpl:"):
        base_dir = os.path.dirname(TEMPLATES[0])  # both templates share a dir
        cur = "tmpl"
    else:
        cur = curkey
    if path_part == "":
        return curkey
    # site-absolute links (templates use /ed-blackbox/guides/… as the deployed root)
    SITE = "/ed-blackbox/guides/"
    if path_part.startswith(SITE):
        return path_part[len(SITE):]
    cur_dir = os.path.dirname(os.path.join(GUIDES, cur if not curkey.startswith("tmpl:") else "x"))
    if curkey.startswith("tmpl:"):
        cur_dir = os.path.dirname(TEMPLATES[0])
    tgt_abs = os.path.normpath(os.path.join(cur_dir, path_part))
    if tgt_abs.startswith(GUIDES + os.sep):
        return os.path.relpath(tgt_abs, GUIDES).replace(os.sep, "/")
    return None

def rewrite_hrefs_in_text(text, curkey, fmap):
    changed = 0
    def repl(m):
        nonlocal changed
        full = m.group(1)
        if "://" in full or full.startswith("mailto:"):
            return m.group(0)
        path_part, anchor = full.split("#", 1)
        tgtkey = resolve_target(curkey, path_part)
        page = fmap.get(tgtkey)
        if page and anchor in page:
            changed += 1
            return 'href="' + path_part + "#" + page[anchor] + '"'
        return m.group(0)
    text = HREF_RE.sub(repl, text)
    return text, changed

def patch_generator(fmap):
    """Apply index.html's map to the generator source (ids + same-page #hrefs)."""
    page = fmap.get("index.html", {})
    if not page:
        return 0
    text = open(GEN_INDEX, encoding="utf-8").read()
    n = 0
    for old, new in page.items():
        for a, b in (('id="%s"' % old, 'id="%s"' % new),
                     ('href="#%s"' % old, 'href="#%s"' % new),
                     ('"#%s"' % old, '"#%s"' % new)):
            text, c = re.subn(re.escape(a), b, text)
            n += c
    open(GEN_INDEX, "w", encoding="utf-8").write(text)
    return n

def do_phase1(fmap):
    tot = 0
    for path in list_html():
        relk = relkey(path)
        page = fmap.get(relk)
        if not page:
            continue
        text = open(path, encoding="utf-8", errors="replace").read()
        text, n = rewrite_ids(text, page)
        open(path, "w", encoding="utf-8").write(text)
        tot += n
    g = patch_generator(fmap)
    print("phase1: rewrote %d id attributes; patched generator (%d substitutions)" % (tot, g))

def do_phase2(fmap):
    tot = dtot = 0
    for path in list_html():
        relk = relkey(path)
        text = open(path, encoding="utf-8", errors="replace").read()
        text, c = rewrite_hrefs_in_text(text, relk, fmap)
        # JS quick-nav uses data-target="<same-page id>" (blueprints.html / modules.html);
        # rewrite it with this page's own map so getElementById(data-target) keeps resolving.
        d = 0
        for old, new in fmap.get(relk, {}).items():
            text, c2 = re.subn(r'data-target="' + re.escape(old) + r'"', 'data-target="' + new + '"', text)
            d += c2
        if c or d:
            open(path, "w", encoding="utf-8").write(text)
        tot += c; dtot += d
    # curated catalogs: rewrite the #ids using the owning page's map
    md = 0
    for mdpath, owner in CURATED_MD.items():
        if not os.path.exists(mdpath):
            continue
        page = fmap.get(owner, {})
        text = open(mdpath, encoding="utf-8").read()
        for old, new in page.items():
            text, c = re.subn(r'#' + re.escape(old) + r'\b', "#" + new, text)
            md += c
        open(mdpath, "w", encoding="utf-8").write(text)
    print("phase2: rewrote %d href anchors; %d data-target attrs; %d curated-catalog anchors" % (tot, dtot, md))

def do_verify():
    # current ids per file
    ids = {}
    for path in list_html():
        relk = relkey(path)
        s = set()
        for m in TAG_RE.finditer(open(path, encoding="utf-8", errors="replace").read()):
            s.add(m.group(3))
        ids[relk] = s
    broken, leftover = [], []
    for path in list_html():
        relk = relkey(path)
        text = open(path, encoding="utf-8", errors="replace").read()
        for full in HREF_RE.findall(text):
            if "://" in full or full.startswith("mailto:"):
                continue
            path_part, anchor = full.split("#", 1)
            tgt = resolve_target(relk, path_part)
            if tgt is None or tgt not in ids:
                continue  # off-tree / non-guide target
            if anchor not in ids[tgt]:
                broken.append((relk, full, tgt))
        # leftover old-scheme ids: a genuine old prefix or bare s<N> still used as an
        # id, excluding the deliberately-kept functional ids (qn-/toc/n-/c-/emap-/wires).
        for m in TAG_RE.finditer(text):
            tag, pre, oid, post = m.group(1), m.group(2), m.group(3), m.group(4)
            cm = CLASS_RE.search(pre) or CLASS_RE.search(post)
            classes = cm.group(1) if cm else ""
            if classify(relk, tag, classes, oid, text, m.end())[0] == "skip":
                continue  # legitimately excluded / no-op id
            if re.fullmatch(r's\d+', oid) or oid.startswith(OLD_PREFIX_SCAN):
                leftover.append((relk, oid))
    if broken:
        print("BROKEN LINKS (%d):" % len(broken))
        for r, h, t in broken[:60]:
            print("  %-40s %s  -> target %s" % (r, h, t))
    if leftover:
        print("LEFTOVER OLD-SCHEME IDS (%d):" % len(leftover))
        for r, o in leftover[:60]:
            print("  %-40s %s" % (r, o))
    if not broken and not leftover:
        print("VERIFY OK: all internal anchors resolve; no old-scheme ids remain.")
        return 0
    return 1

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build-map", action="store_true")
    ap.add_argument("--phase1", action="store_true")
    ap.add_argument("--phase2", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--map", default=os.path.join(SCRIPT_DIR, "..", "anchor-map.json"))
    a = ap.parse_args()

    if a.build_map:
        fmap, skips, unknowns = build_map()
        cols = find_collisions(fmap)
        total = sum(len(p) for p in fmap.values())
        print("files with renames : %d" % len(fmap))
        print("total id renames   : %d" % total)
        print("skipped (excluded) : %d" % len(skips))
        print("UNKNOWN nav ids    : %d" % len(unknowns))
        print("COLLISIONS         : %d" % len(cols))
        from collections import Counter
        byfam = Counter(new.split("-")[0] + "-" for p in fmap.values() for new in p.values())
        print("by new family      : " + ", ".join("%s=%d" % (k, v) for k, v in sorted(byfam.items())))
        if unknowns:
            print("\n-- UNKNOWN (must classify or exclude) --")
            for r, t, o in unknowns[:80]:
                print("  %-40s <%s> %s" % (r, t, o))
        if cols:
            print("\n-- COLLISIONS --")
            for r, new, olds in cols:
                print("  %-40s %s <= %s" % (r, new, olds))
        json.dump({"files": fmap}, open(a.map, "w"), indent=1)
        print("\nmap written: %s" % os.path.abspath(a.map))
        sys.exit(1 if (unknowns or cols) else 0)

    if a.verify:
        sys.exit(do_verify())

    if a.phase1 or a.phase2:
        fmap = json.load(open(a.map))["files"]
        if a.phase1: do_phase1(fmap)
        if a.phase2: do_phase2(fmap)

if __name__ == "__main__":
    main()
