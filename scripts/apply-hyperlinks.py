#!/usr/bin/env python3
"""apply-hyperlinks.py — cross-link references to the source pages.

Scans editable guide pages for references to catalogued elements (engineers,
blueprints, modules, materials, powers, superpowers, ship dossiers) and wraps
each occurrence in an internal <a href> to the right anchor — every occurrence,
in prose / callouts / lists / data-table cells, but never inside headings, nav,
stat tiles, the scorecard, credits, existing links, or <script>/<style>/<svg>.

Matching is fuzzy + context-aware (data/links/link-aliases.json): FSD -> Frame
Shift Drive; "Conda" -> Anaconda; "Frame Shift Drive" resolves to the *module*
or the *blueprint group* by surrounding context; a bare ship name resolves to
the role dossier implied by the page/section.

Confidence >= 0.75 is applied; EVERY candidate (incl. below-bar) is logged to
data/links/link-candidates.csv for post-review.

The rewrite is byte-preserving — only the matched text spans are wrapped.

Usage:
    python3 scripts/apply-hyperlinks.py --check                 # dry-run all editable pages
    python3 scripts/apply-hyperlinks.py guides/systems          # one dir/glob/file
    python3 scripts/apply-hyperlinks.py --reset-log <paths...>  # truncate the CSV first
Exclusions (never edited as link sources): guides/activities/**, guides/ships/by-role/**, guides/index.html (generated).
"""
from __future__ import annotations
import csv
import json
import os
import re
import sys
from bisect import bisect_right
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
G = ROOT / "guides"
DATA = ROOT / "data" / "links"
LOG = DATA / "link-candidates.csv"
BAR = 0.75

ROLES = ["multipurpose", "combat", "exploration", "trading", "mining", "passenger", "ax"]

SKIP_TAGS = {"a", "h1", "h2", "h3", "h4", "h5", "h6", "script", "style", "svg",
             "code", "pre", "button", "textarea", "option", "title", "nav", "head"}
SKIP_CLASSES = {"kicker", "role", "brand", "qn-item", "qn", "toc", "quicknav",
                "dial", "hud", "scval", "fct", "cr-link", "cr-src", "credits",
                "lex-btn", "lex-copy", "mx-search", "breadcrumb", "tabs",
                "masthead-meta", "tag", "chip", "bp-card-title", "nolink"}
VOID = {"br", "img", "input", "meta", "link", "hr", "area", "base", "col",
        "embed", "source", "track", "wbr", "path", "circle", "rect", "line",
        "polyline", "polygon", "use", "stop"}

EXCLUDE_DIRS = ("activities/", "ships/by-role/")


# ---------------------------------------------------------------- skip scanner
class SkipScanner(HTMLParser):
    """Collect byte intervals that are inside a skip subtree (tag or class)."""

    def __init__(self, src):
        super().__init__(convert_charrefs=False)
        self.src = src
        self.line_start = [0]
        for i, ch in enumerate(src):
            if ch == "\n":
                self.line_start.append(i + 1)
        self.stack = []          # frames: dict(tag, skip, start)
        self.intervals = []      # (start, end) skip regions

    def _abs(self):
        ln, col = self.getpos()
        return self.line_start[ln - 1] + col

    def _tag_end(self, start):
        gt = self.src.find(">", start)
        return gt + 1 if gt != -1 else len(self.src)

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        start = self._abs()
        classes = set()
        for k, v in attrs:
            if k == "class" and v:
                classes.update(v.split())
        skip = tag in SKIP_TAGS or bool(classes & SKIP_CLASSES)
        self.stack.append(dict(tag=tag, skip=skip, start=start))

    def handle_startendtag(self, tag, attrs):
        return  # self-closing: no subtree

    def handle_endtag(self, tag):
        end = self._tag_end(self._abs())
        # pop until we find the matching tag (tolerate stray/unclosed voids)
        while self.stack:
            frame = self.stack.pop()
            if frame["skip"]:
                self.intervals.append((frame["start"], end))
            if frame["tag"] == tag:
                break

    def finish(self):
        # close any dangling skip frames at EOF
        for frame in self.stack:
            if frame["skip"]:
                self.intervals.append((frame["start"], len(self.src)))
        # merge intervals
        self.intervals.sort()
        merged = []
        for s, e in self.intervals:
            if merged and s <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], e))
            else:
                merged.append((s, e))
        self.starts = [s for s, _ in merged]
        self.ends = [e for _, e in merged]
        return self

    def in_skip(self, pos):
        i = bisect_right(self.starts, pos) - 1
        return i >= 0 and pos < self.ends[i]


# ---------------------------------------------------------------- dictionary
def load_dict():
    base = json.loads((DATA / "link-dictionary.base.json").read_text(encoding="utf-8"))
    al = json.loads((DATA / "link-aliases.json").read_text(encoding="utf-8"))
    by_anchor = {e["anchor"]: e for e in base["entries"]}
    ships = base["ships"]

    # surface form -> list of resolvers. resolver = (kind, key)
    #   kind "anchor": key=anchor id   |  kind "ship": key=ship slug
    forms = {}
    surfaces = []          # (original_form, case_sensitive_bool)

    def is_acronym(f):
        return bool(re.fullmatch(r"[A-Z0-9]{2,5}", f))

    def add(form, kind, key):
        if not form:
            return
        forms.setdefault(form.lower(), []).append((kind, key, form))
        cs = kind == "ship" or is_acronym(form)
        surfaces.append((form, cs))
        # English-plural variant so a singular surface ("Shield Booster", "SCB",
        # "Heat Sink Launcher", "Beam Laser") also matches plural prose ("Shield
        # Boosters", "SCBs", …). The matcher is exact AND the resolver looks the
        # matched text up by exact key, so the plural must be registered in BOTH
        # `forms` and `surfaces`. Ship proper nouns stay singular-only (plurals
        # are vanishingly rare in prose and risk false common-noun hits).
        if kind != "ship" and not form.lower().endswith("s"):
            plural = form + "s"
            forms.setdefault(plural.lower(), []).append((kind, key, plural))
            surfaces.append((plural, cs))

    for e in base["entries"]:
        for sf in e.get("surface_forms", []):
            if '"' in sf:        # skip quoted-nickname forms (won't appear in prose)
                continue
            add(sf, "anchor", e["anchor"])
    for slug, m in ships.items():
        add(m["name"], "ship", slug)
        # per-hull display-name aliases folded in from data/ship-aliases/
        for alias in m.get("aliases", []):
            add(alias, "ship", slug)
    for form, slug in al["ship_aliases"].items():
        add(form, "ship", slug)
    for grp in ("module_aliases", "blueprint_group_aliases", "blueprint_aliases",
                "powerplay_aliases"):
        for form, anchor in al[grp].items():
            add(form, "anchor", anchor)

    # how many distinct blueprint anchors share each effect label (ambiguity)
    from collections import Counter
    effect_count = Counter(e["label"].split(" (")[0].lower()
                           for e in base["entries"] if e["family"] == "blueprint")
    # curated distinctive blueprint aliases are always safe to pin
    alias_bp = {k.lower() for k in al["blueprint_aliases"]}
    # weapon-category modules that are also bare English adjectives
    soft_modules = {"kinetic", "explosive", "plasma"}

    # validate alias anchors exist
    for grp in ("module_aliases", "blueprint_group_aliases", "blueprint_aliases", "powerplay_aliases"):
        for form, anchor in al[grp].items():
            if anchor not in by_anchor:
                print(f"  WARN alias '{form}' -> unknown anchor {anchor}", file=sys.stderr)
    for form, slug in al["ship_aliases"].items():
        if slug not in ships:
            print(f"  WARN ship alias '{form}' -> unknown hull {slug}", file=sys.stderr)

    # verification-driven corrections (optional keys in link-aliases.json)
    block_forms = {f.lower() for f in al.get("block_forms", [])}        # never link these
    prefer_module = {f.lower() for f in al.get("prefer_module_forms", [])}  # drop blueprint-group candidate
    ship_default = {k: v for k, v in al.get("ship_default_role", {}).items()}

    return dict(by_anchor=by_anchor, ships=ships, forms=forms, surfaces=surfaces,
                ctx=al["context"], effect_count=effect_count, alias_bp=alias_bp,
                soft_modules=soft_modules, block_forms=block_forms,
                prefer_module=prefer_module, ship_default=ship_default)


# ---------------------------------------------------------------- matcher
def build_regexes(surfaces):
    """Two alternations: case-insensitive (common words) + case-sensitive
    (acronyms + ship proper nouns, to avoid 'hauler'/'adder' common-noun hits)."""
    ci = {f for f, cs in surfaces if not cs}
    cs = {f for f, c in surfaces if c}

    def alt(words):
        words = sorted(words, key=len, reverse=True)
        return "|".join(re.escape(w) for w in words) if words else None

    pat_ci, pat_cs = alt(ci), alt(cs)
    rx = []
    if pat_ci:
        rx.append(re.compile(rf"(?<![\w-])(?:{pat_ci})(?![\w-])", re.IGNORECASE))
    if pat_cs:
        rx.append(re.compile(rf"(?<![\w-])(?:{pat_cs})(?![\w-])"))
    return rx


def text_runs(src):
    for m in re.finditer(r">([^<>]+)<", src):
        yield m.start(1), m.group(1)


def rel_href(cur_file: Path, target_rel: str, anchor: str) -> str:
    tgt = (G / target_rel).resolve()
    rel = os.path.relpath(tgt, cur_file.parent.resolve())
    return f"{rel.replace(os.sep, '/')}#{anchor}"


def resolve(matched, key, candidates, window, cur_file, D):
    """Return (kind,target_rel,anchor,family,label,conf,reason) or None to skip."""
    # honour block_forms for the matched text AND its singular (the plural
    # surfaces registered in load_dict must not bypass a curated block, e.g.
    # "cannon" blocked -> "cannons" must stay blocked too)
    if key in D["block_forms"] or (key.endswith("s") and key[:-1] in D["block_forms"]):
        return None
    wl = window.lower()
    bp_ctx = any(k in wl for k in D["ctx"]["blueprint_keywords"])
    rank_ctx = any(k in wl for k in D["ctx"]["rank_keywords"])
    cur_rel = cur_file.relative_to(G).as_posix()
    cur_base = cur_file.stem
    cur_role = next((r for r in ROLES if cur_base == r or cur_base.endswith("-" + r)), None)

    # ---- ship candidates ----
    ship = next((c for c in candidates if c[0] == "ship"), None)
    if ship:
        slug = ship[1]
        m = D["ships"][slug]
        # don't link a ship to its own dossier page
        if cur_base.startswith(slug + "-") or cur_base == slug:
            return None
        # pick a role: explicit role word in window > current page role > default
        role = next((r for r in ROLES if r in wl and r in m["roles"]), None)
        conf = 0.85
        if not role and cur_role and cur_role in m["roles"]:
            role = cur_role
        if not role:
            override = D["ship_default"].get(slug)
            role = override if override in m["roles"] else m["default_role"]
            conf = 0.78
        is_alias = ship[2].lower() != m["name"].lower()
        if is_alias:
            conf -= 0.03
        target_rel = m["roles"][role]
        return ("ship", target_rel, "", "ship-dossier",
                f"{m['name']} ({role})", round(conf, 2),
                f"role={role}{' alias' if is_alias else ''}")

    # ---- anchor candidates ----
    anchors = [c for c in candidates if c[0] == "anchor"]
    # verification fix: bare component names in fit/loadout prose -> module, not blueprint group
    if key in D["prefer_module"]:
        non_bp = [a for a in anchors if D["by_anchor"].get(a[1], {}).get("family") != "blueprint-group"]
        if non_bp:
            anchors = non_bp
    fams = {D["by_anchor"][a[1]]["family"] for a in anchors if a[1] in D["by_anchor"]}

    def pick(anchor):
        e = D["by_anchor"][anchor]
        return e["file"], e["anchor"], e["family"], e["label"]

    # module vs blueprint-group ambiguity (same display name)
    if {"module", "blueprint-group"} & fams and len(fams) > 1:
        if bp_ctx:
            a = next(c for c in anchors if D["by_anchor"][c[1]]["family"] == "blueprint-group")
            f, an, fam, lbl = pick(a[1])
            conf, reason = 0.85, "ambig->blueprint (context)"
        else:
            a = next(c for c in anchors if D["by_anchor"][c[1]]["family"] == "module")
            f, an, fam, lbl = pick(a[1])
            conf, reason = 0.85, "ambig->module (default)"
    else:
        a = anchors[0]
        if a[1] not in D["by_anchor"]:
            return None
        f, an, fam, lbl = pick(a[1])
        conf, reason = {
            "engineer": (0.9, "engineer"),
            "powerplay": (0.9, "power"),
            "module": (0.85, "module"),
            "blueprint-group": (0.8, "blueprint group"),
            "material-section": (0.6, "material (coarse)"),
            "superpower": (0.6, "superpower"),
            "blueprint": (0.7, "blueprint"),
        }.get(fam, (0.7, fam))
        # contextual adjustments
        if fam == "superpower":
            conf = 0.85 if rank_ctx else 0.6
            reason += " +rank" if rank_ctx else " (no rank ctx)"
        if fam == "module" and matched.lower() in D["soft_modules"]:
            conf, reason = 0.65, "weapon-category adj (soft)"
        if fam == "blueprint":
            eff = lbl.split(" (")[0].lower()
            grp = (lbl.split("(", 1)[1].rstrip(")").lower() if "(" in lbl else "")
            ambiguous = D["effect_count"].get(eff, 0) > 1
            generic = eff in D["ctx"]["generic_blueprint_effects"]
            grp_named = bool(grp) and grp in wl       # the module/group is named nearby
            if key in D["alias_bp"]:
                conf, reason = 0.85, "blueprint (curated alias)"
            elif generic:
                # bare English adjective -> only when its module is named in context
                conf = 0.8 if grp_named else 0.5
                reason = "blueprint generic" + ("+group named" if grp_named else " (log only)")
            elif ambiguous:
                conf = 0.82 if grp_named else 0.55
                reason = "blueprint ambiguous" + ("+group named" if grp_named else " (log only)")
            else:
                conf = 0.85 if (bp_ctx or grp_named) else 0.78
                reason = "blueprint distinctive"
        # power last-name aliases are slightly softer
        if fam == "powerplay" and key in {"archer", "winters", "patreus", "torval",
                                          "mahon", "delaine", "grom", "antal", "kaine",
                                          "nakato", "aisling", "ald", "lyr"}:
            conf = 0.82

    # never self-link to the same page
    if (G / f).resolve() == cur_file.resolve():
        return None
    return ("anchor", f, an, fam, lbl, round(conf, 2), reason)


# ---------------------------------------------------------------- per file
def process_file(path: Path, D, regexes, writer, apply: bool):
    src = path.read_text(encoding="utf-8")
    scan = SkipScanner(src)
    try:
        scan.feed(src)
        scan.close()
    except Exception as ex:
        print(f"  WARN parse {path.name}: {ex}", file=sys.stderr)
        return 0, 0
    scan.finish()

    edits = []           # (start, end, replacement)
    applied = logged = 0
    seen_spans = []

    for run_start, run_text in text_runs(src):
        if scan.in_skip(run_start):
            continue
        matches = []
        for rx in regexes:
            for m in rx.finditer(run_text):
                matches.append((m.start(), m.end(), m.group()))
        if not matches:
            continue
        matches.sort(key=lambda t: (t[0], -(t[1] - t[0])))
        last_end = -1
        for ms, me, mt in matches:
            if ms < last_end:
                continue
            key = mt.lower()
            cands = D["forms"].get(key)
            if not cands:
                continue
            res = resolve(mt, key, cands, run_text, path, D)
            if not res:
                continue
            kind, trel, anchor, fam, lbl, conf, reason = res
            abs_s = run_start + ms
            href = rel_href(path, trel, anchor) if anchor else \
                rel_href(path, trel, "").rstrip("#")
            ln = src.count("\n", 0, abs_s) + 1
            do = conf >= BAR
            writer.writerow([path.relative_to(ROOT).as_posix(), ln, mt, key, fam,
                             trel, anchor, conf, "yes" if do and apply else ("bar" if do else "no"),
                             reason, run_text.strip()[:120]])
            logged += 1
            if do:
                edits.append((abs_s, run_start + me,
                              f'<a href="{href}">{mt}</a>'))
                applied += 1
                last_end = me

    if apply and edits:
        edits.sort()
        out, prev = [], 0
        for s, e, rep in edits:
            out.append(src[prev:s]); out.append(rep); prev = e
        out.append(src[prev:])
        path.write_text("".join(out), encoding="utf-8")
    return applied, logged


# ---------------------------------------------------------------- driver
def editable_files(args):
    if args:
        files = []
        for a in args:
            p = Path(a) if Path(a).is_absolute() else (ROOT / a)
            if p.is_dir():
                files.extend(sorted(p.rglob("*.html")))
            elif p.is_file():
                files.append(p)
            else:
                files.extend(sorted(ROOT.glob(a)))
        cand = [f for f in files if f.suffix == ".html"]
    else:
        cand = sorted(G.rglob("*.html"))
    out = []
    for f in cand:
        rel = f.relative_to(G).as_posix()
        if any(rel.startswith(d) for d in EXCLUDE_DIRS):
            continue
        if rel == "index.html":
            continue
        out.append(f)
    return out


def main():
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    apply = "--check" not in flags
    D = load_dict()
    regexes = build_regexes(D["surfaces"])
    files = editable_files(args)

    DATA.mkdir(parents=True, exist_ok=True)
    # --check writes to a throwaway log so it can never pollute the live candidate log
    log_path = LOG if apply else DATA / "link-candidates.check.csv"
    new_log = "--reset-log" in flags or not log_path.exists()
    mode = "w" if new_log else "a"
    with log_path.open(mode, newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        if new_log:
            writer.writerow(["source_file", "line", "matched_text", "surface_form",
                             "target_family", "target_file", "target_anchor",
                             "confidence", "applied", "reason", "context"])
        tot_a = tot_l = nfiles = 0
        for f in files:
            a, l = process_file(f, D, regexes, writer, apply)
            if l:
                nfiles += 1
                tot_a += a; tot_l += l
                print(f"  {'[check] ' if not apply else ''}{f.relative_to(ROOT)}: "
                      f"{a} applied / {l} candidates")
    print(f"\n{'[CHECK] ' if not apply else ''}{nfiles} files; "
          f"{tot_a} links applied, {tot_l} candidates logged -> {log_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
