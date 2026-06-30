#!/usr/bin/env bash
# scripts/migrate-docking-panels.sh — one-shot panel->card conversion for the docking manual
# (guides/systems/docking-landing-manual.html). Its 12 panels are richer than the dossiers'
# (accent eyebrow + h3.subhead title + body) and blue/green path-coded, so:
#   <div class="cols-2">              -> <div class="cards two">
#   .panel + <div class="subhd fed">  -> <div class="card ac-fed"> + <span class="ico">   (blue path)
#   .panel + <div class="subhd good"> -> <div class="card ac-good"> + <span class="ico">   (green path)
#   .panel + <div class="subhd">      -> <div class="card"> + <span class="ico">           (plain)
#   the in-panel <h3 class="subhead"> title -> <h4>   (card title; all 12 h3.subhead are titles)
# Accent is carried by the card (.ac-fed/.ac-good) — the DS recolors the .ico to match.
# Markup-only; no wording/fact/id changes. Re-runnable.
set -euo pipefail
cd "$(dirname "$0")/.."
f=guides/systems/docking-landing-manual.html
perl -0777 -i -CSD -pe '
  s{<div class="cols-2">}{<div class="cards two">}g;
  s{<div class="panel">\s*<div class="subhd fed">(.*?)</div>}{<div class="card ac-fed"><span class="ico">$1</span>}gs;
  s{<div class="panel">\s*<div class="subhd good">(.*?)</div>}{<div class="card ac-good"><span class="ico">$1</span>}gs;
  s{<div class="panel">\s*<div class="subhd">(.*?)</div>}{<div class="card"><span class="ico">$1</span>}gs;
  s{<h3 class="subhead">(.*?)</h3>}{<h4>$1</h4>}gs;
' "$f"
echo "migrate-docking-panels: done"
echo "  residual .subhd/.panel/.cols-2: $(grep -cE 'class="subhd|class="panel"|class="cols-2"' "$f")  (expect 0)"
echo "  cards: $(grep -oE 'class="card[^"]*"' "$f" | sort | uniq -c | tr '\n' ' ')"
