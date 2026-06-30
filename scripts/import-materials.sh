#!/usr/bin/env bash
# import-materials.sh — vendor the canonical materials data from EDCD/FDevIDs.
#
# data/materials/ is imported VERBATIM (read-only — re-fetched here, never hand-edited).
# Project fixes/presentation live in data/materials-extra/. Mirrors the provenance of
# data/fdev/shipyard.csv. See:
#   docs/superpowers/specs/2026-06-30-edcd-reference-data-pipelines-design.md
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="$HERE/../data/materials"
BASE="https://raw.githubusercontent.com/EDCD/FDevIDs/master"
mkdir -p "$DEST"
for f in material.csv microresources.csv; do
  curl -fsSL "$BASE/$f" -o "$DEST/$f"
  echo "fetched $f -> data/materials/$f ($(wc -l < "$DEST/$f") lines)"
done
echo "Raw/Manufactured/Encoded type counts (expect Raw 28, Manufactured 64, Encoded 45):"
awk -F, 'NR>1{print $4}' "$DEST/material.csv" | sort | uniq -c
