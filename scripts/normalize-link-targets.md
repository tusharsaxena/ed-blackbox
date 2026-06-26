# normalize-link-targets.py

Enforces the site's **link-open policy** (settled 2026-06-26): internal links open in the
**same tab**, external links open in a **new tab**.

For every `<a href>` site-wide it classifies the target and rewrites the opening tag:

| target | rule |
|---|---|
| external — `http://`, `https://`, `//host` | add `target="_blank" rel="noopener noreferrer"` (merging any existing `rel` tokens) |
| internal — relative path, `#anchor`, own-site file | strip `target="_blank"` and the now-pointless `noopener`/`noreferrer` `rel` tokens |
| `mailto:` / `tel:` / `javascript:` / `data:` | left untouched |

The rewrite is **byte-preserving** — only the `<a …>` opening tags that must change are
touched. Idempotent (re-running is a no-op once normalized).

```bash
python3 scripts/normalize-link-targets.py            # apply to all guides/**/*.html
python3 scripts/normalize-link-targets.py --check    # report, write nothing
python3 scripts/normalize-link-targets.py guides/systems   # limit to files/globs
```

**Run it after authoring/generating any page** so its links follow the policy — and as the
companion to `apply-hyperlinks.py` (which already emits same-tab internal links).
