#!/usr/bin/env python3
# verify-links.py
# -----------------------------------------------------------------------------
# Full hyperlink audit for the guides: every <a href> is resolved and checked.
#   - INTERNAL links: the target file must exist, and any #fragment must match an
#     id on that target page (relative, same-page, and /ed-blackbox/guides/ site-
#     absolute paths all resolved).
#   - QUICK-NAV: every .qn-item / .site-nav anchor must resolve, and its visible
#     label is checked against the target section heading (semantic "correctness").
#   - EXTERNAL links (http/https/mailto) are inventoried (deduped) and written to
#     a file for a separate liveness pass; not fetched here.
#
# Exits nonzero if any internal link or quick-nav anchor is broken.
#
# USAGE
#   python3 scripts/verify-links.py [--ext-out /path/external-urls.txt]
# -----------------------------------------------------------------------------
import os, re, sys, html, argparse, collections

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(SCRIPT_DIR)
GUIDES = os.path.join(REPO, "guides")
SITE = "/ed-blackbox/guides/"

A_RE     = re.compile(r'<a\b([^>]*?)\shref="([^"]+)"([^>]*)>(.*?)</a>', re.DOTALL | re.IGNORECASE)
IDTAG_RE = re.compile(r'<([a-zA-Z][a-zA-Z0-9]*)((?:"[^"]*"|\'[^\']*\'|[^>"\'])*?)\sid="([^"]+)"((?:"[^"]*"|\'[^\']*\'|[^>"\'])*)>')
H_RE     = re.compile(r'<h[1-6][^>]*>(.*?)</h[1-6]>', re.DOTALL | re.IGNORECASE)
CLASS_RE = re.compile(r'class="([^"]*)"')

def text_of(frag):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', frag))).strip()

def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', html.unescape(s).lower()).strip('-')

def list_html():
    out = []
    for dp, _, fs in os.walk(GUIDES):
        for f in fs:
            if f.endswith(".html"):
                out.append(os.path.join(dp, f))
    return sorted(out)

def relkey(path):
    return os.path.relpath(path, GUIDES).replace(os.sep, "/")

def index_ids_and_headings():
    """Per file: set of ids, and {id: heading-text} for sections/subheads."""
    ids, headings = {}, {}
    for path in list_html():
        k = relkey(path)
        txt = open(path, encoding="utf-8", errors="replace").read()
        s, hd = set(), {}
        for m in IDTAG_RE.finditer(txt):
            tag, pre, oid, post = m.group(1).lower(), m.group(2), m.group(3), m.group(4)
            s.add(oid)
            cm = CLASS_RE.search(pre) or CLASS_RE.search(post)
            classes = cm.group(1) if cm else ""
            if tag == "section":
                hm = H_RE.search(txt, m.end())
                if hm:
                    hd[oid] = text_of(hm.group(1))
            elif re.fullmatch(r'h[1-6]', tag) and "subhead" in classes.split():
                # the heading element itself carries the id and the text
                hm = re.match(r'<h[1-6][^>]*>(.*?)</h[1-6]>', txt[m.start():], re.DOTALL | re.IGNORECASE)
                if hm:
                    hd[oid] = text_of(hm.group(1))
        ids[k], headings[k] = s, hd
    return ids, headings

def resolve(curkey, path_part):
    if path_part == "":
        return curkey
    if path_part.startswith(SITE):
        return path_part[len(SITE):]
    cur_dir = os.path.dirname(os.path.join(GUIDES, curkey))
    tgt = os.path.normpath(os.path.join(cur_dir, path_part))
    if tgt.startswith(GUIDES + os.sep):
        return os.path.relpath(tgt, GUIDES).replace(os.sep, "/")
    return None  # off-tree

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ext-out", default=os.path.join(SCRIPT_DIR, "..", "external-urls.txt"))
    a = ap.parse_args()

    ids, headings = index_ids_and_headings()
    broken_file, broken_anchor, qn_broken, qn_label, dt_broken = [], [], [], [], []
    ext = collections.defaultdict(list)
    n_internal = n_qn = n_dt = 0

    for path in list_html():
        k = relkey(path)
        txt = open(path, encoding="utf-8", errors="replace").read()
        # JS quick-nav: data-target="<same-page id>" must match a real id on this page.
        for dt in re.findall(r'data-target="([^"]+)"', txt):
            n_dt += 1
            if dt not in ids[k]:
                dt_broken.append((k, 'data-target="%s"' % dt, k))
        for pre, href, post, inner in A_RE.findall(txt):
            attrs = pre + " " + post
            cm = CLASS_RE.search(attrs)
            classes = (cm.group(1) if cm else "").split()
            is_qn = ("qn-item" in classes) or ("qn-totop" in classes)
            if href.startswith(("http://", "https://", "mailto:")):
                ext[href].append(k)
                continue
            if href == "#":
                continue  # to-top / placeholder
            n_internal += 1
            path_part, _, anchor = href.partition("#")
            tgt = resolve(k, path_part)
            if tgt is None:
                continue  # off-tree, not a guides target
            if tgt not in ids:
                broken_file.append((k, href, tgt)); continue
            if anchor and anchor not in ids[tgt]:
                rec = (k, href, tgt)
                broken_anchor.append(rec)
                if is_qn: qn_broken.append(rec)
                continue
            # quick-nav label vs target heading (same-page items only)
            if is_qn and not path_part and anchor in headings.get(tgt, {}):
                n_qn += 1
                label = text_of(re.search(r'class="qn-nm"[^>]*>(.*?)</span>', inner, re.DOTALL).group(1)) \
                    if re.search(r'class="qn-nm"', inner) else text_of(inner)
                head = headings[tgt][anchor]
                ls, hs = slug(label), slug(head)
                if ls and hs and ls not in hs and hs not in ls and not (set(ls.split('-')) & set(hs.split('-'))):
                    qn_label.append((k, anchor, label, head))

    # write external inventory
    with open(a.ext_out, "w", encoding="utf-8") as f:
        for url in sorted(ext):
            f.write("%s\t%d\n" % (url, len(ext[url])))

    print("internal links checked : %d" % n_internal)
    print("data-target attrs checked: %d" % n_dt)
    print("quick-nav labels checked: %d" % n_qn)
    print("unique external URLs    : %d  (-> %s)" % (len(ext), os.path.abspath(a.ext_out)))
    print("broken target FILES     : %d" % len(broken_file))
    print("broken ANCHORS          : %d  (of which quick-nav: %d)" % (len(broken_anchor), len(qn_broken)))
    print("broken data-target attrs: %d" % len(dt_broken))
    print("quick-nav LABEL mismatches (review): %d" % len(qn_label))
    for title, rows in (("BROKEN FILES", broken_file), ("BROKEN ANCHORS", broken_anchor),
                        ("BROKEN data-target", dt_broken)):
        if rows:
            print("\n-- %s --" % title)
            for k, href, tgt in rows[:80]:
                print("  %-42s %s" % (k, href))
    if qn_label:
        print("\n-- QUICK-NAV LABEL/HEADING MISMATCHES (heuristic) --")
        for k, anc, lab, head in qn_label[:80]:
            print("  %-34s #%-26s label=%r vs heading=%r" % (k, anc, lab, head))

    sys.exit(1 if (broken_file or broken_anchor or dt_broken) else 0)

if __name__ == "__main__":
    main()
