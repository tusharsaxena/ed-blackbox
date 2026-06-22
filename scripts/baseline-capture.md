# baseline-capture.sh — pre-migration baseline for every guide

Captures the **comparison baseline** for the design-system migration: a full-page PNG and
a content fingerprint for each of the 108 guides, written into `_migration/baseline/`
(gitignored). The migration compares each migrated page against its baseline here — the
screenshot for visual diff, the `*.fp.json` for the content-invariance gate.

## What it produces

For every `guides/**/*.html` except `index.html`:

```
_migration/baseline/<relpath>.png       # full-page screenshot (via shot.mjs)
_migration/baseline/<relpath>.fp.json   # content fingerprint (via fingerprint.mjs)
```

e.g. `guides/ships/dossiers/adder-exploration.html` →
`_migration/baseline/ships/dossiers/adder-exploration.{png,fp.json}`.

## Usage

```bash
bash scripts/baseline-capture.sh
```

Prints `baseline captured: 108 pages → …/_migration/baseline` on success. Runtime is a
few minutes (two headless-Chromium passes per page).

## Prerequisites

Playwright + Chromium (see [shot.md](shot.md)) and the [fingerprint](fingerprint.md)
scripts.

## Notes

- `_migration/` is gitignored — the baseline is a local working artifact, not committed.
- Re-run only to **re-establish** the baseline (e.g. before starting a fresh migration
  pass). Don't re-run mid-migration, or you'd overwrite the pre-migration reference with
  already-migrated pages.
