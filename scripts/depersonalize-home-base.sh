#!/usr/bin/env bash
# depersonalize-home-base.sh
#
# One-shot editorial pass: removes the author's personal home-base framing
# ("your Diaguandri / Ray Gateway base/home", masthead "Home/Base" tokens, and
# the Diaguandri-anchored fleet-carrier-vendor clause) and reworks each into a
# role-neutral phrasing that reads for any commander.
#
# Deliberately LEAVES factual Diaguandri/Ray Gateway mentions intact:
#   - engineering/checklist.html + engineers.html  (Diaguandri stocks Landmines)
#   - engineering/farms/jameson-crash-site.html    (Ray Gateway is the genuine
#                                                    nearest Encoded trader)
# It also leaves the kept author byline "CMDR Ka0s" untouched.
#
# Idempotent: re-running finds nothing to change. Paths resolve relative to the
# script, so it runs from anywhere.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

changed=0
note() { printf '  %s\n' "$1"; }

echo "depersonalize-home-base: reworking personal home-base references"

# 1) Ship dossiers — the bulk "your <station> base/home" possessive framing.
echo "[1] ship dossiers (possessive home-base framing)"
for f in guides/ships/dossiers/*.html; do
  grep -q "Diaguandri / Ray Gateway" "$f" || continue
  perl -i -pe '
    s{your Diaguandri / Ray Gateway base}{your home base}g;
    s{your Diaguandri / Ray Gateway home}{your home base}g;
  ' "$f"
  note "reworked $(basename "$f")"
  changed=$((changed+1))
done

# 2) Dossiers with a bespoke phrasing the bulk rule does not cover.
echo "[2] dossiers with bespoke phrasing"
# fer-de-lance / mamba: drop the "— around Diaguandri / Ray Gateway —" interjection.
for f in guides/ships/dossiers/fer-de-lance-combat.html guides/ships/dossiers/mamba-combat.html; do
  if grep -q "Diaguandri / Ray Gateway" "$f"; then
    perl -i -pe 's{ &mdash; around Diaguandri / Ray Gateway &mdash;}{}g;' "$f"
    note "reworked $(basename "$f")"
    changed=$((changed+1))
  fi
done
# viper-mk-iv: "Your home region around Diaguandri / Ray Gateway has" -> "Your home region has"
if grep -q "home region around Diaguandri / Ray Gateway" guides/ships/dossiers/viper-mk-iv-combat.html; then
  perl -i -pe 's{Your home region around Diaguandri / Ray Gateway has}{Your home region has}g;' \
    guides/ships/dossiers/viper-mk-iv-combat.html
  note "reworked viper-mk-iv-combat.html"
  changed=$((changed+1))
fi

# 3) Systems-page masthead meta tokens (author's own base stated as page metadata).
echo "[3] systems-page masthead meta"
if grep -q "Ray Gateway &middot; Diaguandri\|Ray Gateway · Diaguandri" guides/systems/bgs.html; then
  perl -i -pe 's{Ray Gateway (·|&middot;) Diaguandri}{your bubble base}g;' guides/systems/bgs.html
  note "reworked bgs.html masthead Home token"
  changed=$((changed+1))
fi
if grep -q "Ray Gateway, Diaguandri" guides/systems/docking-landing-manual.html; then
  perl -i -pe 's{Ray Gateway, Diaguandri}{your bubble base}g;' guides/systems/docking-landing-manual.html
  note "reworked docking-landing-manual.html masthead Base token"
  changed=$((changed+1))
fi

# 4) fleet-carrier.html — drop the "From Diaguandri" anchor, keep the vendor
#    examples but reframe them as generic bubble examples.
echo "[4] fleet-carrier vendor clause"
if grep -q "From Diaguandri the closest bubble options include" guides/systems/fleet-carrier.html; then
  perl -i -pe 's{From Diaguandri the closest bubble options include}{Bubble examples include}g;
               s{Confirm the nearest on Inara\.}{Confirm the nearest to you on Inara.}g;' \
    guides/systems/fleet-carrier.html
  note "reworked fleet-carrier.html vendor clause"
  changed=$((changed+1))
fi

echo
echo "depersonalize-home-base: done — $changed file(s) changed."
echo "sanity check (should print only kept factual mentions):"
grep -rn "Diaguandri\|Ray Gateway" --include='*.html' guides/ \
  | grep -vE "checklist\.html|engineers\.html|jameson-crash-site\.html" \
  || echo "  (none — all personal home-base framing removed)"
