#!/usr/bin/env bash
# inject-rating-methodology-links.sh
# ---------------------------------------------------------------------------
# Inserts a cross-link to guides/ships/rating-methodology.html everywhere a
# 1-100 suitability rating is shown:
#
#   * 77 ship dossiers  (guides/ships/dossiers/*.html)
#       A `.callout` is inserted right BEFORE the `<!-- s1 -->` comment, i.e.
#       after the `.verdict` (rating/briefing) box and before section 01.
#
#   * 7 by-role pages   (guides/ships/by-role/*.html)
#       A short link line is inserted right BEFORE the `<!-- 3 -->` comment,
#       i.e. at the end of section 02 "How These Ships Are Scored".
#
# Both dossiers and by-role pages link with the SAME relative href
# (../rating-methodology.html) because both live one level below the page.
#
# IDEMPOTENT: any file already containing "rating-methodology.html" is skipped.
# Adds NO new <section id>, so anchor catalogs do not need regenerating.
#
# Paths resolve relative to this script, so it runs from anywhere.
# Prints a sanity count: modified vs skipped, per group.
# ---------------------------------------------------------------------------
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DOSSIER_DIR="$REPO_ROOT/guides/ships/dossiers"
BYROLE_DIR="$REPO_ROOT/guides/ships/by-role"

MARKER="rating-methodology.html"

# Insertion anchors (verified against the real markup).
DOSSIER_ANCHOR='<!-- s1 -->'
BYROLE_ANCHOR='<!-- 3 -->'

# --- the callout inserted into each dossier (2-space indent matches siblings) ---
read -r -d '' DOSSIER_BLOCK <<'HTML' || true
  <div class="callout"><span class="lbl">Rating methodology</span><p>This ship's <span class="acc">1&ndash;100 suitability rating</span> reflects its fully-engineered fit for this role, scored against every ship in the role. See <a href="../rating-methodology.html">how ships are rated</a>.</p></div>

HTML

# --- the link line inserted into each by-role page ---
read -r -d '' BYROLE_BLOCK <<'HTML' || true
  <p class="subhd">How the scores are built</p><p>This 1&ndash;100 rating is a roster-relative, fully-engineered editorial verdict &mdash; not a hidden formula. See the shared <a href="../rating-methodology.html">rating methodology</a> for the full rubric and worked examples.</p>

HTML

modified=0
skipped=0

inject() {
  local file="$1" anchor="$2" block="$3"
  if grep -q "$MARKER" "$file"; then
    skipped=$((skipped + 1))
    return
  fi
  if ! grep -qF "$anchor" "$file"; then
    echo "  WARN: anchor '$anchor' not found in $(basename "$file") -- skipped" >&2
    skipped=$((skipped + 1))
    return
  fi
  # Insert block immediately BEFORE the (first) anchor line, using awk so the
  # multi-line HTML is inserted verbatim with no shell-escaping surprises.
  # `print block` guarantees a trailing newline so the anchor stays on its own line.
  awk -v anchor="$anchor" -v block="$block" '
    !done && index($0, anchor) { print block; done = 1 }
    { print }
  ' "$file" > "$file.tmp" && mv "$file.tmp" "$file"
  modified=$((modified + 1))
}

echo "== Dossiers (guides/ships/dossiers/*.html) =="
dmod_before=$modified
for f in "$DOSSIER_DIR"/*.html; do
  inject "$f" "$DOSSIER_ANCHOR" "$DOSSIER_BLOCK"
done
dmod=$((modified - dmod_before))

echo "== By-role pages (guides/ships/by-role/*.html) =="
bmod_before=$modified
for f in "$BYROLE_DIR"/*.html; do
  inject "$f" "$BYROLE_ANCHOR" "$BYROLE_BLOCK"
done
bmod=$((modified - bmod_before))

echo
echo "------------------------------------------------------------"
echo "Dossiers modified : $dmod"
echo "By-role modified  : $bmod"
echo "Total modified    : $modified"
echo "Total skipped     : $skipped (already linked or anchor missing)"
echo "------------------------------------------------------------"
