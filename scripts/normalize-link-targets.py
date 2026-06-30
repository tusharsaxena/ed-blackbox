#!/usr/bin/env python3
"""normalize-link-targets.py — enforce the site link-open policy.

Policy (settled 2026-06-26): internal links open in the SAME tab; external links
open in a NEW tab.

  * external  (href starts with http://, https://, //)  ->  add target="_blank"
              and rel="noopener noreferrer" (merging any existing rel tokens).
  * internal  (relative path, "#anchor", "./", "../", bare file, or a
              mailto:/tel: scheme)                       ->  strip target="_blank"
              and drop the noopener/noreferrer rel tokens it no longer needs.

The script is byte-preserving: it only rewrites the `<a ...>` opening tags it
must change, leaving every other byte of each file untouched. Run it site-wide
(it is a global UX policy, independent of the hyperlink-creation exclusions).

Usage:
    python3 scripts/normalize-link-targets.py [--check] [paths...]

    --check   report what would change, write nothing
    paths     limit to specific files/globs (default: all guides/**/*.html + index)
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
A_OPEN = re.compile(r"<a\b[^>]*>", re.IGNORECASE)
ATTR = lambda name: re.compile(rf'\s{name}\s*=\s*"([^"]*)"', re.IGNORECASE)
HREF_RE = ATTR("href")
TARGET_RE = ATTR("target")
REL_RE = ATTR("rel")


def is_external(href: str) -> bool:
    h = href.strip()
    return bool(re.match(r"(https?:)?//", h, re.IGNORECASE))


def is_skippable(href: str) -> bool:
    """Schemes we leave entirely alone (no tab policy applies)."""
    return bool(re.match(r"(mailto:|tel:|javascript:|data:)", href.strip(), re.IGNORECASE))


def rewrite_tag(tag: str) -> str:
    m = HREF_RE.search(tag)
    if not m:
        return tag  # anchors without href (named targets) — leave alone
    href = m.group(1)
    if is_skippable(href):
        return tag

    rel_m = REL_RE.search(tag)
    rel_tokens = rel_m.group(1).split() if rel_m else []
    has_target = TARGET_RE.search(tag)

    if is_external(href):
        # ensure target="_blank" and noopener noreferrer
        rel = [t for t in rel_tokens if t.lower() not in ("noopener", "noreferrer")]
        rel = rel + ["noopener", "noreferrer"]
        new_tag = TARGET_RE.sub("", tag)            # drop any existing target
        new_tag = REL_RE.sub("", new_tag)           # drop any existing rel
        new_tag = re.sub(r"\s+", " ", new_tag)      # tidy the gaps we just opened
        # re-insert right after href value
        insert = f' target="_blank" rel="{" ".join(rel)}"'
        new_tag = new_tag.replace(f'href="{href}"', f'href="{href}"{insert}', 1)
        return new_tag
    else:
        # internal: strip target=_blank and the now-pointless noopener/noreferrer
        if not has_target and not any(t.lower() in ("noopener", "noreferrer") for t in rel_tokens):
            return tag
        new_tag = TARGET_RE.sub("", tag)
        rel = [t for t in rel_tokens if t.lower() not in ("noopener", "noreferrer")]
        if rel_m:
            new_tag = REL_RE.sub("", new_tag)
            if rel:
                new_tag = new_tag.replace("<a", f'<a rel="{" ".join(rel)}"', 1)
        new_tag = re.sub(r"\s+", " ", new_tag)
        new_tag = new_tag.replace(" >", ">").replace("< a", "<a")
        return new_tag


def process(text: str):
    changes = {"ext": 0, "int": 0}

    def repl(mo):
        tag = mo.group(0)
        new = rewrite_tag(tag)
        if new != tag:
            href = HREF_RE.search(tag)
            if href and is_external(href.group(1)):
                changes["ext"] += 1
            else:
                changes["int"] += 1
        return new

    return A_OPEN.sub(repl, text), changes


def collect(paths):
    if paths:
        files = []
        for p in paths:
            pp = Path(p)
            files.extend(ROOT.glob(p) if not pp.is_absolute() else [pp])
        return [f for f in files if f.suffix == ".html"]
    return sorted((ROOT / "guides").rglob("*.html"))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check = "--check" in sys.argv
    files = collect(args)
    total = {"ext": 0, "int": 0, "files": 0}
    for f in files:
        src = f.read_text(encoding="utf-8")
        out, ch = process(src)
        if out != src:
            total["files"] += 1
            total["ext"] += ch["ext"]
            total["int"] += ch["int"]
            if not check:
                f.write_text(out, encoding="utf-8")
            print(f"  {'would fix' if check else 'fixed'}: {f.relative_to(ROOT)}  (+{ch['ext']} ext, {ch['int']} int)")
    print(f"\n{'[check] ' if check else ''}{total['files']} files; "
          f"{total['ext']} external -> new tab, {total['int']} internal -> same tab")


if __name__ == "__main__":
    main()
