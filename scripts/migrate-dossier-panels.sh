#!/usr/bin/env bash
# scripts/migrate-dossier-panels.sh — one-shot .subhd retirement for ship dossiers
# (guides/ships/dossiers/*.html). All 77 dossiers share one templated structure, so this is
# a uniform markup-only transform:
#   Phase A — section subheadings:  <p class="subhd">…</p>  ->  <h3 class="subhead">…</h3>
#   Phase B — the single .cols-2 pair of bullet .panels  ->  .cards two of .card with .ico:
#       <div class="cols-2"> -> <div class="cards two">
#       <div class="panel"><div class="subhd">X</div><ul class="bullets">
#         -> <div class="card"><span class="ico">X</span><ul class="bullets">
# Mirrors the activities/by-role panel->card pattern. No wording/fact/id changes. Re-runnable.
set -euo pipefail
cd "$(dirname "$0")/.."
shopt -s nullglob
files=(guides/ships/dossiers/*.html)
for f in "${files[@]}"; do
  perl -0777 -i -CSD -pe '
    s{<p class="subhd">(.*?)</p>}{<h3 class="subhead">$1</h3>}gs;
    s{<div class="cols-2">}{<div class="cards two">}g;
    s{<div class="panel"><div class="subhd">(.*?)</div>}{<div class="card"><span class="ico">$1</span>}gs;
  ' "$f"
done
echo "migrate-dossier-panels: applied to ${#files[@]} dossiers"
res=$(grep -lE 'class="subhd"|class="cols-2"|class="panel"' "${files[@]}" 2>/dev/null | wc -l)
echo "  dossiers still carrying .subhd/.cols-2/.panel: $res (expect 0)"
