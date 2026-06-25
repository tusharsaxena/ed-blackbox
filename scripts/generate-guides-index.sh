#!/usr/bin/env bash
#
# generate-guides-index.sh
# -----------------------------------------------------------------------------
# Regenerates guides/index.html — the "Elite:Dangerous Black Box" landing page
# that links to every guide in the project.
#
# The page is on the shared design system (design-system/css/ed-blackbox.css +
# js/ed-blackbox.js). Only the landing-specific guide-card grid and ship-dossier
# grid live in a small scoped <style> block here.
#
# WHAT IT DOES
#   - Emits guides/index.html: global chrome + quick-nav, a briefing, an
#     "What Is This Website" intro, then THREE top-level sections that mirror the
#     header links — Ships, Engineering, Systems — each holding the relevant
#     guide groups as labelled sub-sections. Ends with FAQ + Changelog.
#   - Hand-curated cards for the guides (title + one-liner, set in the CARD CALLS).
#   - Auto-discovers every ship dossier in guides/ships/dossiers/*.html and groups
#     them by ship, with one role link per dossier (colour-coded by role).
#
# WHEN TO RE-RUN
#   - After adding/removing/renaming any ship dossier (ships/dossiers/*.html) — the
#     ship grid is rebuilt from the filesystem, so those stay in sync for free.
#   - After adding a new top-level guide, add a matching `card ...` line in the
#     relevant sub-section below, then re-run.
#
# DO NOT auto-edit the Changelog section — its entries are hand-written here and
# stamped with a FIXED date (not the build date). Add a release only when asked.
#
# USAGE
#   bash scripts/generate-guides-index.sh        # from anywhere in the repo
#
# OUTPUT
#   guides/index.html  (overwritten)
#   Prints the ship-row and guide-card counts as a sanity check.
#
# NOTE: editing guides/index.html by hand will be lost on the next run — change
# this generator instead.
# -----------------------------------------------------------------------------
set -euo pipefail

# Resolve repo paths relative to this script (scripts/ lives at the repo root).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GUIDES="$REPO_ROOT/guides"
OUT="$GUIDES/index.html"

# Emit a guide card.  args: href, accentClass, title, desc
card(){ printf '    <a class="gcard %s" href="%s"><h3>%s</h3><p>%s</p></a>\n' "$2" "$1" "$3" "$4"; }

# Map a role slug to its role-chip colour class (used in the ship grid). Each role gets a
# distinct hue (RED→VIOLET); the colours resolve from the design-system --role-* tokens.
role_class(){ case "$1" in combat) echo "r-combat";; ax) echo "r-ax";; mining) echo "r-mining";; trading) echo "r-trading";; exploration) echo "r-exploration";; passenger) echo "r-passenger";; multipurpose) echo "r-multipurpose";; *) echo "";; esac; }

# Display label for a role slug (AX stays upper-case; others Title-case).
role_label(){ case "$1" in ax) echo "AX";; *) echo "$(echo "$1" | awk '{print toupper(substr($0,1,1)) substr($0,2)}')";; esac; }

# Display name for a ship slug — looked up in ship-names.tsv (slug<TAB>Name);
# falls back to Title-casing the slug's words if the ship isn't in the map.
NAMES="$SCRIPT_DIR/ship-names.tsv"
ship_name(){
  local n; n="$(awk -F'\t' -v s="$1" '$1==s{print $2; exit}' "$NAMES")"
  [ -n "$n" ] && { printf '%s' "$n"; return; }
  echo "$1" | tr '-' ' ' | awk '{for(i=1;i<=NF;i++)$i=toupper(substr($i,1,1)) substr($i,2)}1'
}

{
cat <<'HEAD'
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Home | E:D Black Box</title>
<link rel="icon" type="image/png" href="../images/logos/favicon.png">
<link rel="stylesheet" href="../design-system/css/ed-blackbox.css">
<style>
/* landing-page-specific grids (kept out of the design system) */
.gcards{display:grid;grid-template-columns:repeat(auto-fill,minmax(264px,1fr));gap:14px;margin-top:var(--space-9)}
.gcard{display:block;background:var(--panel);border:1px solid var(--hair);border-left:3px solid var(--amber);border-radius:var(--radius-sm);padding:16px 18px;text-decoration:none;transition:background .18s,border-color .18s,transform .12s}
.gcard:hover{background:var(--panel2);transform:translateY(-1px)}
.gcard.ac-fed{border-left-color:var(--fed)}.gcard.ac-mar{border-left-color:var(--maroon-lt)}.gcard.ac-good{border-left-color:var(--good)}
.gcard h3{font-family:'Chakra Petch',sans-serif;font-weight:700;font-size:16px;letter-spacing:.4px;color:var(--ink);line-height:1.15;margin-bottom:7px}
.gcard:hover h3{color:var(--amber-lt)}
.gcard p{font-size:13px;color:var(--ink-dim);line-height:1.5}
.subhead[id]{scroll-margin-top:74px}
.ship-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:10px;margin-top:var(--space-9)}
.ship{display:flex;align-items:center;gap:12px;background:var(--panel);border:1px solid var(--hair);border-radius:var(--radius-sm);padding:11px 15px;transition:background .18s}
.ship:hover{background:var(--panel2)}
.ship .nm{font-family:'Chakra Petch',sans-serif;font-weight:600;font-size:13.5px;letter-spacing:.3px;color:var(--ink);flex:1;text-transform:uppercase}
.ship .roles{display:flex;flex-wrap:wrap;gap:6px;justify-content:flex-end}
.ship .roles a{font-family:'Saira Condensed',sans-serif;font-size:11px;font-weight:600;letter-spacing:.6px;text-transform:uppercase;color:var(--amber-lt);text-decoration:none;border:1px solid var(--hair-strong);border-radius:10px;padding:2px 10px;transition:.14s;white-space:nowrap}
.ship .roles a:hover{color:var(--bg);background:var(--amber-lt);border-color:var(--amber-lt)}
.ship .roles a.r-combat{color:var(--role-combat)}.ship .roles a.r-combat:hover{background:var(--role-combat);border-color:var(--role-combat);color:var(--ink)}
.ship .roles a.r-ax{color:var(--role-ax)}.ship .roles a.r-ax:hover{background:var(--role-ax);border-color:var(--role-ax);color:var(--bg)}
.ship .roles a.r-mining{color:var(--role-mining)}.ship .roles a.r-mining:hover{background:var(--role-mining);border-color:var(--role-mining);color:var(--bg)}
.ship .roles a.r-trading{color:var(--role-trading)}.ship .roles a.r-trading:hover{background:var(--role-trading);border-color:var(--role-trading);color:var(--bg)}
.ship .roles a.r-exploration{color:var(--role-exploration)}.ship .roles a.r-exploration:hover{background:var(--role-exploration);border-color:var(--role-exploration);color:var(--bg)}
.ship .roles a.r-passenger{color:var(--role-passenger)}.ship .roles a.r-passenger:hover{background:var(--role-passenger);border-color:var(--role-passenger);color:var(--bg)}
.ship .roles a.r-multipurpose{color:var(--role-multipurpose)}.ship .roles a.r-multipurpose:hover{background:var(--role-multipurpose);border-color:var(--role-multipurpose);color:var(--bg)}
</style>
</head>
<body>

<!-- ---- GLOBAL HEADER ---- -->
<header class="site-header">
  <div class="hdr-inner">
    <a class="brand" href="index.html" aria-label="E:D Black Box — home">
      <img src="../images/logos/logo.png" alt="">
      <span class="wordmark"><span class="hl">E:D</span> Black Box</span>
    </a>
    <span class="nav-sep" aria-hidden="true"></span>
    <nav class="site-nav" aria-label="Primary">
      <a href="#" class="active">Home</a>
      <a href="#section-dossiers">Ships</a>
      <a href="#section-engineering">Engineering</a>
      <a href="#section-systems">Systems</a>
    </nav>
    <div class="header-qn">
      <span class="qn-eyebrow muted">On this page</span>
      <button class="qn-totop" type="button" aria-label="Scroll to top" title="Scroll to top">
        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M4 13 L12 6 L20 13"/><path d="M4 18.5 L12 11.5 L20 18.5"/></svg>
      </button>
      <div class="qn-dd" id="qn-dd">
        <div class="qn-field">
          <span class="qn-ico" aria-hidden="true">&#9906;</span>
          <input id="qn-search" class="qn-input" type="text" placeholder="Jump to a section…" autocomplete="off" spellcheck="false" role="combobox" aria-expanded="false" aria-controls="qn-panel" aria-autocomplete="list">
          <button id="qn-clear" class="qn-clear" type="button" aria-label="Clear search" hidden>&times;</button>
        </div>
        <div class="qn-panel" id="qn-panel" role="listbox">
          <div class="qn-sec">Start</div>
          <a class="qn-item" href="#section-about-site"><span class="qn-dot amber"></span><span class="qn-nm">What Is This Website</span><span class="qn-side">Intro</span></a>
          <div class="qn-sec">Ships</div>
          <a class="qn-item" href="#section-dossiers"><span class="qn-dot amber"></span><span class="qn-nm">Ships</span><span class="qn-side">Section</span></a>
          <a class="qn-item" href="#section-best-ships"><span class="qn-dot amber"></span><span class="qn-nm">Best Ships by Role</span><span class="qn-side">Ships</span></a>
          <a class="qn-item" href="#section-ship-dossiers"><span class="qn-dot amber"></span><span class="qn-nm">Ship Dossiers</span><span class="qn-side">Ships</span></a>
          <div class="qn-sec">Engineering</div>
          <a class="qn-item" href="#section-engineering"><span class="qn-dot amber"></span><span class="qn-nm">Engineering</span><span class="qn-side">Section</span></a>
          <a class="qn-item" href="#section-eng-manuals"><span class="qn-dot amber"></span><span class="qn-nm">Engineering Manuals</span><span class="qn-side">Engineering</span></a>
          <a class="qn-item" href="#section-farming"><span class="qn-dot amber"></span><span class="qn-nm">Material Farming</span><span class="qn-side">Engineering</span></a>
          <div class="qn-sec">Systems</div>
          <a class="qn-item" href="#section-systems"><span class="qn-dot amber"></span><span class="qn-nm">Systems</span><span class="qn-side">Section</span></a>
          <a class="qn-item" href="#section-new-pilot"><span class="qn-dot amber"></span><span class="qn-nm">New Pilot &amp; Interface</span><span class="qn-side">Systems</span></a>
          <a class="qn-item" href="#section-galaxy"><span class="qn-dot amber"></span><span class="qn-nm">Galaxy &amp; Power Systems</span><span class="qn-side">Systems</span></a>
          <a class="qn-item" href="#section-activities"><span class="qn-dot amber"></span><span class="qn-nm">Activity Guides</span><span class="qn-side">Systems</span></a>
          <a class="qn-item" href="#section-combat-venues"><span class="qn-dot amber"></span><span class="qn-nm">Combat Venues</span><span class="qn-side">Systems</span></a>
          <div class="qn-sec">More</div>
          <a class="qn-item" href="#section-faq"><span class="qn-dot amber"></span><span class="qn-nm">FAQ</span><span class="qn-side">Info</span></a>
          <a class="qn-item" href="#section-changelog"><span class="qn-dot amber"></span><span class="qn-nm">Changelog</span><span class="qn-side">Info</span></a>
          <div class="qn-empty" hidden>No matching sections</div>
        </div>
      </div>
    </div>
  </div>
</header>

<div class="wrap">

  <!-- ---- MASTHEAD ---- -->
  <header class="masthead">
    <div class="kicker">Elite: Dangerous <span class="sep">//</span> Guides</div>
    <h1 class="title">Elite:Dangerous <span>Black Box</span></h1>
    <div class="masthead-meta">
      <span><b>100+</b> guides</span>
      <span>Updated <b>__BUILD_DATE__</b></span>
    </div>
  </header>

  <!-- ---- BRIEFING ---- -->
  <div class="verdict">
    <div class="v-eyebrow">Start Here</div>
    <h2>Everything a commander needs, in <em>one shelf</em></h2>
    <p>The Black Box collects operator-grade guides for Elite Dangerous into a single index: the engineering referral tree and blueprint catalogue, material-farm routes, activity playbooks, "best ship for the job" ladders, and a full set of ship &times; role dossiers. New here? Read <a href="#section-about-site">What Is This Website</a>, then dive into Ships, Engineering or Systems.</p>
    <div class="stat-grid">
      <div class="stat"><div class="n">11</div><div class="l">Game-system guides</div></div>
      <div class="stat"><div class="n">7</div><div class="l">Engineering manuals</div></div>
      <div class="stat"><div class="n fed">77</div><div class="l">Ship dossiers</div></div>
      <div class="stat"><div class="n mar">13</div><div class="l">Role &amp; activity guides</div></div>
    </div>
  </div>

  <!-- ---- 01 ABOUT ---- -->
  <section id="section-about-site">
    <div class="sec-head"><span class="sec-num">01</span><h2>What Is This Website</h2><span class="tag">Placeholder</span></div>
    <p class="lead"><em>Placeholder — to be refined.</em></p>
    <p>The <strong>Elite:Dangerous Black Box</strong> is a library of operator-grade guides for <em>Elite Dangerous: Odyssey</em>, written commander-to-commander. It pulls the things you actually look up mid-session — engineer unlocks, blueprint material costs, farm routes, where to fight, what to fly — into one cross-linked reference, with every page citing its sources.</p>
    <p><em>(Placeholder copy. This intro will be rewritten later — what the site is, who it's for, how it's maintained, and how to use it.)</em></p>
  </section>

  <!-- ---- 02 SHIPS ---- -->
  <section id="section-dossiers">
    <div class="sec-head"><span class="sec-num">02</span><h2>Ships</h2><span class="tag">Fly the right hull</span></div>
    <p class="lead">How each career plays, which hull wins each role, and a dossier for every viable ship &times; role pairing.</p>

    <h3 class="subhead" id="section-best-ships">Best Ships by Role</h3>
    <p>"What should I fly for this?" — ships ranked head-to-head for each role.</p>
    <div class="gcards">
HEAD

card "ships/by-role/combat.html"       ""  "Combat"       "Combat ships ranked, from starter to capital."
card "ships/by-role/ax.html"           ""  "Anti-Xeno (AX)"    "The ships that hold up against Thargoids."
card "ships/by-role/exploration.html"  ""  "Exploration"  "Jump range, comfort and the long black, ranked."
card "ships/by-role/mining.html"       ""        "Mining"       "Mining platforms ranked by yield and fit."
card "ships/by-role/trading.html"      "" "Trading"      "Cargo haulers ranked by tonnage and economy."
card "ships/by-role/passenger.html"    ""  "Passenger"    "Cabin capacity and range for the tourism trade."
card "ships/by-role/multipurpose.html" ""        "Multipurpose"     "Do-everything ships ranked for the multipurpose pilot."
card "ships/rating-methodology.html"   ""  "Rating Methodology"    "How every ship earns its 1–100 suitability rating — the roster-relative, fully-engineered rubric."

cat <<'SHIPS3'
    </div>

    <h3 class="subhead" id="section-ship-dossiers">Ship Dossiers</h3>
    <p>A dossier for every viable ship-and-role pairing — rating, spec readout and recommended loadout. Pick a ship, then a role.</p>
    <div class="ship-grid">
SHIPS3

# ---- ship dossiers, auto-discovered (slug-role.html) and grouped by ship ----
# Filenames are kebab-case `<ship-slug>-<role>.html`; role = last '-' token,
# ship-slug = the rest. Display name comes from ship_name() (ship-names.tsv).
for f in "$GUIDES"/ships/dossiers/*.html; do
  base="$(basename "$f" .html)"
  role="$(echo "$base" | sed -E 's/.*-([a-z]+)$/\1/')"
  slug="$(echo "$base" | sed -E 's/-[a-z]+$//')"
  echo "$(ship_name "$slug")|$role|$base.html"
done | awk -F'|' '{ships[$1]=ships[$1]$2"="$3";"} END{for(s in ships)print s"|"ships[s]}' | sort | \
while IFS='|' read -r ship roles; do
  printf '    <div class="ship"><span class="nm">%s</span><span class="roles">' "$ship"
  echo "$roles" | tr ';' '\n' | while IFS='=' read -r role file; do
    [ -z "$role" ] && continue
    cls="$(role_class "$role")"
    printf '<a class="%s" href="ships/dossiers/%s">%s</a>' "$cls" "$file" "$(role_label "$role")"
  done
  printf '</span></div>\n'
done

cat <<'ENG'
    </div>
  </section>

  <!-- ---- 03 ENGINEERING ---- -->
  <section id="section-engineering">
    <div class="sec-head"><span class="sec-num">03</span><h2>Engineering</h2><span class="tag">Modify your gear</span></div>
    <p class="lead">Who modifies your gear, what they grant and the order to unlock them — plus the routes for the materials it eats.</p>

    <h3 class="subhead" id="section-eng-manuals">Engineering Manuals</h3>
    <p>The full engineering set — engineers, blueprints, modules, and the unlock run.</p>
    <div class="gcards">
ENG

card "engineering/checklist.html"  ""       "Unlock Checklist"   "New-pilot engineering progression — what to unlock, and when."
card "engineering/engineers.html"  ""       "Engineers"      "Every engineer: location, meeting requirement, unlock and referrals."
card "engineering/blueprints.html" ""       "Blueprints"         "The module blueprint catalogue across every grade and effect."
card "engineering/modules.html"    ""       "Modules"            "Every outfitting slot — core internals, optionals, hardpoints and utilities, the A–E trade-off and what to fit per role."

cat <<'FARM'
    </div>

    <h3 class="subhead" id="section-farming">Materials &amp; Farming</h3>
    <p>What the materials are, how the trader works, and the known sites and loops for stocking them.</p>
    <div class="gcards">
FARM

card "engineering/materials.html"                  "" "Materials"            "The three material types, grade ladders and trader exchange ratios — hoard high, trade down."
card "engineering/farms/davs-hope.html"            "" "Dav's Hope"           "The classic manufactured-material loop at Dav's Hope."
card "engineering/farms/crystalline-shards.html"   "" "Crystalline Shards"   "Surface raw-material farming at Crystalline Shard sites."
card "engineering/farms/high-grade-emissions.html" "" "High Grade Emissions" "Farming encoded materials from High Grade Emission signals."
card "engineering/farms/jameson-crash-site.html"   "" "Jameson Crash Site"   "The Jameson Crash Site encoded-data farm."

cat <<'SYS'
    </div>
  </section>

  <!-- ---- 04 SYSTEMS ---- -->
  <section id="section-systems">
    <div class="sec-head"><span class="sec-num">04</span><h2>Systems</h2><span class="tag">How the galaxy runs</span></div>
    <p class="lead">Getting started, the big persistent systems that run the galaxy, and where to go looking for a fight.</p>

    <h3 class="subhead" id="section-new-pilot">New Pilot &amp; Interface</h3>
    <p>Get off the ground: docking, the cockpit HUD, and the companion apps every commander runs.</p>
    <div class="gcards">
SYS

card "systems/docking-landing-manual.html" ""  "Docking &amp; Landing" "Requesting docking, pads, and station/outpost landing procedure."
card "systems/hud-customization.html"      ""  "HUD Customization"     "Retune your cockpit HUD colours with the GraphicsConfig matrix."
card "systems/third-party-apps.html"       ""  "Third-Party Apps"      "The essential companion apps, planners and tools for commanders."

cat <<'SYS2'
    </div>

    <h3 class="subhead" id="section-galaxy">Galaxy &amp; Power Systems</h3>
    <p>The big persistent systems — factions, powers, rank, and the things you build once you have credits to spare.</p>
    <div class="gcards">
SYS2

card "systems/bgs.html"                 ""        "Background Simulation" "How minor factions, influence and states actually work."
card "systems/powerplay.html"           ""        "Powerplay"                   "Pledging to a Power, earning merits, and the weekly cycle."
card "systems/superpower-rank.html"     ""        "Superpower Rank"       "Climbing Federation, Empire and Alliance reputation."
card "systems/community-goals.html"     ""        "Community Goals"             "How CGs work and how to land in the top tiers."
card "systems/system-colonization.html" ""  "System Colonisation"         "Claiming systems and building out your own infrastructure."
card "systems/fleet-carrier.html"       ""  "Fleet Carrier"              "Buying, financing, fitting and jumping a Fleet Carrier."

cat <<'SYS3'
    </div>

    <h3 class="subhead" id="section-activities">Activity Guides</h3>
    <p>How each career actually plays — the loop, the gear, and the money.</p>
    <div class="gcards">
SYS3

card "activities/combat.html"      ""  "Combat"       "Bounty hunting, massacre missions and PvE combat."
card "activities/ax.html"          ""  "Anti-Xeno" "Fighting Thargoids — gear, tactics and venues."
card "activities/exploration.html" ""  "Exploration"  "Long-range exploration, scanning and exobiology."
card "activities/mining.html"      ""        "Mining"       "Laser, core and subsurface mining for profit."
card "activities/trading.html"     "" "Trading"      "Cargo trading, loops and reading the market."
card "activities/passenger.html"   ""  "Passenger"    "Passenger missions, tourism and sightseeing runs."

cat <<'SYS4'
    </div>

    <h3 class="subhead" id="section-combat-venues">Combat Venues</h3>
    <p>The places you go looking for a fight, and what each pays.</p>
    <div class="gcards">
SYS4

card "systems/combat-zones.html"      "" "Combat Zones" "Conflict Zones — tactics, payouts, and how to read a CZ."
card "systems/pve-combat-venues.html" "" "PvE Combat Venues"       "RES, CZ, Nav Beacons and signal sources for PvE combat."

cat <<'FOOT'
    </div>
  </section>

  <!-- ---- 05 FAQ ---- -->
  <section id="section-faq">
    <div class="sec-head"><span class="sec-num">05</span><h2>FAQ</h2><span class="tag">Placeholder</span></div>
    <p class="lead"><em>Placeholder — to be refined.</em></p>
    <div class="cards one">
      <div class="card"><h4>Is this affiliated with Frontier Developments?</h4><p>No. This is a community reference. <em>(Placeholder answer.)</em></p></div>
      <div class="card"><h4>How current is the information?</h4><p>Pages are verified against authoritative sources and dated. <em>(Placeholder answer.)</em></p></div>
      <div class="card"><h4>Can I suggest a correction?</h4><p><em>(Placeholder answer — contact / contribution details to come.)</em></p></div>
    </div>
  </section>

  <!-- ---- 06 CHANGELOG ----
       Hand-written. Dates are FIXED, NOT the build date. Add a release only
       when explicitly asked — do not auto-edit this section. -->
  <section id="section-changelog">
    <div class="sec-head"><span class="sec-num">06</span><h2>Changelog</h2><span class="tag">Releases</span></div>
    <p class="lead">Notable updates to the Black Book.</p>
    <h3 class="subhead">2026-06-23 &mdash; Initial release</h3>
    <ul class="bullets">
      <li>First public release of the Elite:Dangerous Black Box field-manual library.</li>
      <li>All guides unified on the shared design system.</li>
    </ul>
  </section>

  <!-- ---- FOOTER ---- -->
  <footer>
    <div class="ft-fine">
      <span>&copy; 2026 Elite:Dangerous Black Box &middot; CMDR Ka0s &middot; Fly safe, commander. &middot; <a href="https://github.com/tusharsaxena/ed-blackbook/issues">Report an issue</a></span>
      <span>Elite Dangerous is a trademark of Frontier Developments plc. Unofficial fan content &mdash; not affiliated with or endorsed by Frontier Developments.</span>
    </div>
  </footer>

</div>

<script src="../design-system/js/ed-blackbox.js" defer></script>
</body>
</html>
FOOT
} > "$OUT"

# Stamp the masthead "Updated" line with the build date (heredocs are single-quoted,
# so the placeholder is substituted here rather than expanded inline).
# NOTE: only the masthead date is build-stamped; the Changelog dates are fixed.
sed -i "s/__BUILD_DATE__/$(date +%F)/" "$OUT"

echo "Wrote $OUT"
grep -c 'class="ship"' "$OUT" | sed 's/^/ship rows: /'
grep -c 'class="gcard' "$OUT" | sed 's/^/guide cards: /'
