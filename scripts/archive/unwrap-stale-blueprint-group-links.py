#!/usr/bin/env python3
"""unwrap-stale-blueprint-group-links.py — one-shot (archived after use).

After switching the hyperlink applier to PREFER the module page for module names
(data/links/link-aliases.json -> prefer_module_forms + weapon->category module_aliases), the
already-applied `#blueprint-group-*` links in dossier PROSE (e.g. the §A-Rated Upgrade Plan)
stayed put — the applier only ADDS links, it never re-resolves an existing <a>. This unwraps
those stale blueprint-group links so the next relink re-adds them as `#module-*`.

Scope: ship dossiers. Unwraps every internal `#blueprint-group-X` link EXCEPT
`blueprint-group-bulkheads` (armour/bulkheads has no module anchor, so that link is correct).
Blueprint EFFECT links (`#blueprint-<group>-<effect>`, e.g. blueprint-multi-cannon-overcharged)
are NOT matched and stay — the Engineered / blueprint columns are unaffected. Idempotent.
Run, then rebuild dossiers (build-ship-loadouts.py).
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DOSSIERS = ROOT / "guides" / "ships" / "ship-dossiers"
# blueprint-GROUP links only (group slug has no further '-<effect>'), excluding bulkheads
A_RE = re.compile(r'<a\b[^>]*\bhref="[^"]*#(blueprint-group-[a-z0-9-]+)"[^>]*>([^<]+)</a>')


def main():
    files = unwrapped = 0
    for p in sorted(DOSSIERS.glob("*.html")):
        h = p.read_text(encoding="utf-8")

        def repl(m):
            if m.group(1) == "blueprint-group-bulkheads":
                return m.group(0)            # armour — no module anchor, keep
            return m.group(2)
        new = A_RE.sub(repl, h)
        if new != h:
            files += 1
            unwrapped += h.count("#blueprint-group-") - new.count("#blueprint-group-")
            p.write_text(new, encoding="utf-8")
    print(f"unwrapped {unwrapped} stale blueprint-group prose links across {files} dossiers "
          f"(bulkheads kept)")


if __name__ == "__main__":
    main()
