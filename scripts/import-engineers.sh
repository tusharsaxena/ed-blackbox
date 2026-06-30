#!/usr/bin/env bash
# import-engineers.sh — vendor the canonical engineer roster from EDCD/FDevIDs.
#
# data/engineers/engineers.csv is imported VERBATIM (read-only — re-fetched here, never
# hand-edited). Project editorial/fixes live in data/engineers-extra/. The ship-engineer
# "Modifications offered" grades come from coriolis data/modifications/modules.json (not here).
# See docs/superpowers/specs/2026-06-30-engineers-data-pipeline-design.md.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="$HERE/../data/engineers"
BASE="https://raw.githubusercontent.com/EDCD/FDevIDs/master"
mkdir -p "$DEST"
curl -fsSL "$BASE/engineers.csv" -o "$DEST/engineers.csv"
echo "fetched engineers.csv -> data/engineers/engineers.csv ($(tail -n +2 "$DEST/engineers.csv" | wc -l) engineers, expect 38)"
