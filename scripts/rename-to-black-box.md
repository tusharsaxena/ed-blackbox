# rename-to-black-box.py

**One-shot project rename.** The project was renamed from **E:D Black Book** to
**E:D Black Box**. This sweeps every tracked text file and applies two exact, disjoint
string replacements:

| From | To | Covers |
|---|---|---|
| `Black Book` | `Black Box` | display/brand name, page titles, prose, SLEF `appName` |
| `blackbook` | `blackbox` | `ed-blackbook` → `ed-blackbox` — issue/repo URLs, `package.json` name |

A survey confirmed those were the only casings present; correct `blackbox` refs
(`ed-blackbox.css`/`.js`, the git remote) contain no `book` and are untouched. Binary files
are skipped (the file list comes from `git grep -lI`). Line endings are preserved (LF).

## Usage

```bash
python3 scripts/rename-to-black-box.py --check   # per-file replacement counts, write nothing
python3 scripts/rename-to-black-box.py           # apply
```

The script excludes itself and this doc (they hold the search strings verbatim).

## After running

Generated artifacts are rewritten by the sweep **and** so are their sources (the generators +
`data/ship-loadouts/*.json` `appName`), so regeneration is a no-op that confirms consistency:

```bash
python3 scripts/build-ship-loadouts.py        # dossier loadout tables / data-slef
bash    scripts/generate-guides-index.sh      # landing page
python3 scripts/generate-ship-role-matrix.py --page
python3 scripts/verify-links.py               # 0 broken
python3 scripts/audit-sources.py              # external-only, no drift
```

A single **line-wrapped** `Black\nBook` (the `docs/CLAUDE.md` header) is not matched by the
single-line replacement and was fixed by hand. Re-run a whitespace-tolerant check
(`grep -Pzo 'Black[\s\xa0]+Book'`) if the brand text is ever re-wrapped.

One-shot; kept for reference. Run once (done at the rename); not part of routine builds.
