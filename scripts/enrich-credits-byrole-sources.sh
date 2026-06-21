#!/usr/bin/env bash
# enrich-credits-byrole-sources.sh
# -----------------------------------------------------------------------------
# Enrichment pass (per §7 of docs/superpowers/specs/2026-06-21-per-page-credits-design.md):
# add role-specific deep sources (Fandom role/activity articles + EDSM/Spansh for
# exploration & trading) to the Sources `.cr-rows` of the by-role ship ladders, on
# top of the 4 generic outfitting rows.
#
# Idempotent: skips a file whose first added marker row is already present.
# Only the `.cr-rows` is touched (rows inserted after the generic Inara row).
# All URLs verified via WebSearch 2026-06-21 (see report).
# -----------------------------------------------------------------------------
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BYROLE="$ROOT/guides/ships/by-role"

INARA_ROW='      <div class="cr-row"><span class="cr-src">Inara</span><span class="cr-what">Module sellers, tech brokers, engineer unlocks, and material traders.</span><a class="cr-link" href="https://inara.cz">inara.cz</a></div>'

row () { # src  what  href  label
  printf '      <div class="cr-row"><span class="cr-src">%s</span><span class="cr-what">%s</span><a class="cr-link" href="%s">%s</a></div>' "$1" "$2" "$3" "$4"
}

declare -A EXTRA

EXTRA[ax]="$(row 'ED Wiki &mdash; Thargoid Combat' 'Thargoid hull mechanics, hearts, and AX weapon effectiveness referenced in the ratings.' 'https://elite-dangerous.fandom.com/wiki/Thargoid_Combat' 'elite-dangerous.fandom.com/wiki/Thargoid_Combat')"
EXTRA[ax]+=$'\n'"$(row 'ED Wiki &mdash; AX Conflict Zone' 'AX conflict-zone structure and threat tiers used to judge each hull&rsquo;s fit.' 'https://elite-dangerous.fandom.com/wiki/AX_Conflict_Zone' 'elite-dangerous.fandom.com/wiki/AX_Conflict_Zone')"

EXTRA[combat]="$(row 'ED Wiki &mdash; Combat' 'Combat career roles (bounty hunting, conflict zones) the suitability ratings target.' 'https://elite-dangerous.fandom.com/wiki/Combat' 'elite-dangerous.fandom.com/wiki/Combat')"
EXTRA[combat]+=$'\n'"$(row 'ED Wiki &mdash; Bounty Hunter' 'RES / Nav-Beacon / CZ engagement context behind the per-hull verdicts.' 'https://elite-dangerous.fandom.com/wiki/Bounty_Hunter' 'elite-dangerous.fandom.com/wiki/Bounty_Hunter')"

EXTRA[exploration]="$(row 'ED Wiki &mdash; Explorer' 'Exploration career mechanics (scanning, jump range, cartographics) behind the ranking.' 'https://elite-dangerous.fandom.com/wiki/Explorer' 'elite-dangerous.fandom.com/wiki/Explorer')"
EXTRA[exploration]+=$'\n'"$(row 'EDSM' 'Galactic map and system / body data used for jump-range and reach reference.' 'https://www.edsm.net' 'edsm.net')"
EXTRA[exploration]+=$'\n'"$(row 'Spansh' 'Neutron / galaxy route plotting that sets the practical value of jump range.' 'https://spansh.co.uk/plotter' 'spansh.co.uk/plotter')"

EXTRA[mining]="$(row 'ED Wiki &mdash; Miner' 'Mining career mechanics (laser, core, sub-surface) the suitability ratings weigh.' 'https://elite-dangerous.fandom.com/wiki/Miner' 'elite-dangerous.fandom.com/wiki/Miner')"
EXTRA[mining]+=$'\n'"$(row 'ED Wiki &mdash; Mining Laser' 'Mining tool and limpet-controller requirements that decide effective cargo per hull.' 'https://elite-dangerous.fandom.com/wiki/Mining_Laser' 'elite-dangerous.fandom.com/wiki/Mining_Laser')"

EXTRA[multipurpose]="$(row 'ED Wiki &mdash; Careers' 'The mixed combat / trade / exploration roles an all-rounder must cover.' 'https://elite-dangerous.fandom.com/wiki/Careers' 'elite-dangerous.fandom.com/wiki/Careers')"
EXTRA[multipurpose]+=$'\n'"$(row 'ED Wiki &mdash; Ships' 'Cross-hull comparison of size, hardpoints, and internals behind the ranking.' 'https://elite-dangerous.fandom.com/wiki/Ships' 'elite-dangerous.fandom.com/wiki/Ships')"

EXTRA[passenger]="$(row 'ED Wiki &mdash; Passenger Carrier' 'Passenger career mechanics and mission types the suitability ratings target.' 'https://elite-dangerous.fandom.com/wiki/Passenger_Carrier' 'elite-dangerous.fandom.com/wiki/Passenger_Carrier')"
EXTRA[passenger]+=$'\n'"$(row 'ED Wiki &mdash; Passenger Cabin' 'Cabin classes (Economy&ndash;Luxury) and per-hull cabin capacity referenced here.' 'https://elite-dangerous.fandom.com/wiki/Passenger_Cabin' 'elite-dangerous.fandom.com/wiki/Passenger_Cabin')"

EXTRA[trading]="$(row 'ED Wiki &mdash; Trader' 'Trading career mechanics and ship suitability behind the cargo-hauler ranking.' 'https://elite-dangerous.fandom.com/wiki/Trader' 'elite-dangerous.fandom.com/wiki/Trader')"
EXTRA[trading]+=$'\n'"$(row 'Spansh' 'Trade-route plotting that turns raw cargo tonnage into realised credits/hour.' 'https://spansh.co.uk/plotter' 'spansh.co.uk/plotter')"
EXTRA[trading]+=$'\n'"$(row 'EDSM' 'System / station reference used for market and route context.' 'https://www.edsm.net' 'edsm.net')"

count=0
for base in ax combat exploration mining multipurpose passenger trading; do
  f="$BYROLE/$base.html"
  if [ ! -f "$f" ]; then echo "MISSING: $f" >&2; continue; fi
  block="${EXTRA[$base]}"
  first_href="$(printf '%s\n' "$block" | head -1 | grep -oE 'href="[^"]+"' | head -1)"
  if grep -qF "$first_href" "$f"; then
    echo "skip (already enriched): $base"; continue
  fi
  python3 - "$f" "$INARA_ROW" "$block" <<'PY'
import sys
path, anchor, block = sys.argv[1], sys.argv[2], sys.argv[3]
with open(path, encoding='utf-8') as fh:
    s = fh.read()
assert anchor in s, f"anchor Inara row not found in {path}"
s = s.replace(anchor, anchor + "\n" + block, 1)
with open(path, 'w', encoding='utf-8') as fh:
    fh.write(s)
PY
  echo "enriched: $base"
  count=$((count+1))
done

echo "Done. Enriched $count by-role file(s)."
