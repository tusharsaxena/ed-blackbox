#!/usr/bin/env bash
# scripts/modernize-by-role-cards.sh — one-shot markup modernization for the by-role pages
# (guides/ships/by-role/*.html). Two transforms:
#   1. <p class="subhd">…</p>  ->  <h3 class="subhead">…</h3>   (consistent subheadings)
#   2. pick cards: drop the leading "· " inside each .pick <small>, so the score/cost reads
#      "66 · ~3M all-in" once the DS moves it to its own row (.pickcard .pick small{display:block}).
# Markup-only; no wording/fact/id changes. Re-runnable (idempotent on already-migrated files).
set -euo pipefail
cd "$(dirname "$0")/.."
shopt -s nullglob
files=(guides/ships/by-role/*.html)
for f in "${files[@]}"; do
  perl -0777 -i -CSD -pe '
    s{<p class="subhd">(.*?)</p>}{<h3 class="subhead">$1</h3>}gs;
    s{(<div class="pick">[^<]*<small>)\x{00b7}\s+}{$1}g;
  ' "$f"
done
echo "modernize-by-role-cards: applied subhd->subhead + pick cost-row strip to ${#files[@]} files"
grep -l 'class="subhd"' "${files[@]}" >/dev/null 2>&1 && echo "  WARN: residual .subhd remains" || echo "  no residual .subhd ✓"
