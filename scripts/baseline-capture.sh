#!/usr/bin/env bash
# scripts/baseline-capture.sh — pre-migration screenshot + fingerprint for every guide.
# Captures the comparison baseline for the design-system migration: a full-page PNG and a
# content fingerprint (*.fp.json) for each of the 108 guides, into _migration/baseline/
# (gitignored). Re-run only to re-establish the baseline; the migration compares against it.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/_migration/baseline"; mkdir -p "$OUT"
cd "$ROOT"
n=0
while IFS= read -r f; do
  rel="${f#./guides/}"; base="$OUT/${rel%.html}"; mkdir -p "$(dirname "$base")"
  node scripts/shot.mjs "$ROOT/${f#./}" "$base.png"
  node scripts/fingerprint.mjs "$ROOT/${f#./}" > "$base.fp.json"
  n=$((n+1))
done < <(find ./guides -name '*.html' ! -name 'index.html' | sort)
echo "baseline captured: $n pages → $OUT"
