#!/usr/bin/env bash
# enrich-credits-ship-sources.sh
# -----------------------------------------------------------------------------
# Enrichment pass (per §7 of docs/superpowers/specs/2026-06-21-per-page-credits-design.md):
# add ship-specific deep sources (Inara ship page + Fandom /wiki/<Ship>) to the
# Sources `.cr-rows` of selected ship-dossier pages, on top of the 4 generic rows.
#
# Idempotent: skips a file if its ship-specific Inara ship-page row is already present.
# Only the `.cr-rows` of `<section class="credits">` is touched (rows inserted after
# the generic Inara row). All URLs verified via WebSearch 2026-06-21 (see report).
# -----------------------------------------------------------------------------
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOSS="$ROOT/guides/ships/dossiers"

# file-basename  ship-display-name  inara-ship-id  fandom-slug
ROWS=$(cat <<'EOF'
type-6-transporter-trading|Type-6 Transporter|30|Type-6_Transporter
type-7-transporter-mining|Type-7 Transporter|40|Type-7_Transporter
type-7-transporter-trading|Type-7 Transporter|40|Type-7_Transporter
type-8-transporter-mining|Type-8 Transporter|41|Type-8_Transporter
type-8-transporter-trading|Type-8 Transporter|41|Type-8_Transporter
type-9-heavy-mining|Type-9 Heavy|65|Type-9_Heavy
type-9-heavy-trading|Type-9 Heavy|65|Type-9_Heavy
viper-mk-iii-combat|Viper Mk III|20|Viper_Mk_III
viper-mk-iv-combat|Viper Mk IV|21|Viper_Mk_IV
vulture-combat|Vulture|34|Vulture
EOF
)

INARA_ROW='      <div class="cr-row"><span class="cr-src">Inara</span><span class="cr-what">Module sellers, tech brokers, engineer unlocks, and material traders.</span><a class="cr-link" href="https://inara.cz">inara.cz</a></div>'

count=0
while IFS='|' read -r base name iid slug; do
  [ -z "$base" ] && continue
  f="$DOSS/$base.html"
  if [ ! -f "$f" ]; then echo "MISSING: $f" >&2; continue; fi
  if grep -q "inara.cz/elite/ship/$iid/" "$f"; then
    echo "skip (already enriched): $base"; continue
  fi
  ship_row="      <div class=\"cr-row\"><span class=\"cr-src\">Inara &mdash; $name</span><span class=\"cr-what\">Ship specification, base stats, and shipyard pricing for this hull.</span><a class=\"cr-link\" href=\"https://inara.cz/elite/ship/$iid/\">inara.cz/elite/ship/$iid</a></div>"
  wiki_row="      <div class=\"cr-row\"><span class=\"cr-src\">ED Wiki &mdash; $name</span><span class=\"cr-what\">Hull role, manufacturer background, and hardpoint / internal layout.</span><a class=\"cr-link\" href=\"https://elite-dangerous.fandom.com/wiki/$slug\">elite-dangerous.fandom.com/wiki/$slug</a></div>"

  python3 - "$f" "$INARA_ROW" "$ship_row" "$wiki_row" <<'PY'
import sys
path, anchor, ship_row, wiki_row = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
with open(path, encoding='utf-8') as fh:
    s = fh.read()
assert anchor in s, f"anchor Inara row not found in {path}"
s = s.replace(anchor, anchor + "\n" + ship_row + "\n" + wiki_row, 1)
with open(path, 'w', encoding='utf-8') as fh:
    fh.write(s)
PY
  echo "enriched: $base (+Inara ship $iid, +Fandom $slug)"
  count=$((count+1))
done <<< "$ROWS"

echo "Done. Enriched $count dossier file(s)."
