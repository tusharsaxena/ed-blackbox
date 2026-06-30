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
#   - Auto-discovers every ship dossier in guides/ships/ship-dossiers/*.html and groups
#     them by ship, with one role link per dossier (colour-coded by role).
#
# WHEN TO RE-RUN
#   - After adding/removing/renaming any ship dossier (ships/ship-dossiers/*.html) — the
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

# Hero stat-card + masthead counts — computed from the filesystem so they never
# drift (substituted into the HEAD heredoc's __TOKENS__ after generation). One card
# per top-level namespace; activities now live under Systems (guides/systems/
# activity-guides/), so the systems find already counts them. TOTAL = every guide
# HTML minus index.html, and equals SHIPS + ENG + SYSTEMS by construction.
SHIPS_COUNT=$(find "$GUIDES/ships" -name '*.html' | wc -l | tr -d ' ')
ENG_COUNT=$(find "$GUIDES/engineering" -name '*.html' | wc -l | tr -d ' ')
SYSTEMS_COUNT=$(find "$GUIDES/systems" -name '*.html' | wc -l | tr -d ' ')
TOTAL_COUNT=$(( $(find "$GUIDES" -name '*.html' | wc -l) - 1 ))

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
      <div class="hdr-crumb solo">
        <span class="hdr-crumb-title">Home</span>
      </div>
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
          <a class="qn-item qn-group" href="#section-about-site"><span class="qn-nm">What Is This Website</span><span class="qn-side">Intro</span></a>
          <a class="qn-item qn-group" href="#section-dossiers"><span class="qn-nm">Ships</span><span class="qn-side">3 guides</span></a>
          <a class="qn-item" href="#section-general"><span class="qn-dot amber"></span><span class="qn-nm">General</span><span class="qn-side">Ships</span></a>
          <a class="qn-item" href="#section-best-ships"><span class="qn-dot amber"></span><span class="qn-nm">Best Ships by Role</span><span class="qn-side">Ships</span></a>
          <a class="qn-item" href="#section-ship-dossiers"><span class="qn-dot amber"></span><span class="qn-nm">Ship Dossiers</span><span class="qn-side">Ships</span></a>
          <a class="qn-item qn-group" href="#section-engineering"><span class="qn-nm">Engineering</span><span class="qn-side">2 guides</span></a>
          <a class="qn-item" href="#section-eng-manuals"><span class="qn-dot amber"></span><span class="qn-nm">Engineering Manuals</span><span class="qn-side">Engineering</span></a>
          <a class="qn-item" href="#section-farming"><span class="qn-dot amber"></span><span class="qn-nm">Material Farming</span><span class="qn-side">Engineering</span></a>
          <a class="qn-item qn-group" href="#section-systems"><span class="qn-nm">Systems</span><span class="qn-side">4 guides</span></a>
          <a class="qn-item" href="#section-new-pilot"><span class="qn-dot amber"></span><span class="qn-nm">New Pilot &amp; Interface</span><span class="qn-side">Systems</span></a>
          <a class="qn-item" href="#section-galaxy"><span class="qn-dot amber"></span><span class="qn-nm">Galaxy &amp; Power Systems</span><span class="qn-side">Systems</span></a>
          <a class="qn-item" href="#section-activities"><span class="qn-dot amber"></span><span class="qn-nm">Activity Guides</span><span class="qn-side">Systems</span></a>
          <a class="qn-item" href="#section-combat-venues"><span class="qn-dot amber"></span><span class="qn-nm">Combat Venues</span><span class="qn-side">Systems</span></a>
          <a class="qn-item qn-group" href="#section-faq"><span class="qn-nm">FAQ</span><span class="qn-side">Info</span></a>
          <a class="qn-item qn-group" href="#section-changelog"><span class="qn-nm">Changelog</span><span class="qn-side">Releases</span></a>
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
      <span><b>__TOTAL__</b> guides</span>
      <span>Updated <b>__BUILD_DATE__</b></span>
    </div>
  </header>

  <!-- ---- BRIEFING ---- -->
  <div class="verdict">
    <div class="v-eyebrow">Start Here</div>
    <h2>Everything a commander needs, in <em>one shelf</em></h2>
    <p>The Black Box collects operator-grade guides for Elite Dangerous into a single index: the engineering referral tree and blueprint catalogue, material-farm routes, activity playbooks, "best ship for the job" ladders, and a full set of ship &times; role dossiers. New here? Read <a href="#section-about-site">What Is This Website</a>, then dive into Ships, Engineering or Systems.</p>
    <div class="stat-grid">
      <div class="stat"><div class="n">__SHIPS__</div><div class="l">Ship guides</div></div>
      <div class="stat"><div class="n">__ENG__</div><div class="l">Engineering guides</div></div>
      <div class="stat"><div class="n">__SYSTEMS__</div><div class="l">Systems guides</div></div>
    </div>
  </div>

  <!-- ---- 01 ABOUT ---- -->
  <section id="section-about-site">
    <div class="sec-head"><span class="sec-num">01</span><h2>What Is This Website</h2><span class="tag">Start here</span></div>
    <p>The <strong>Elite:Dangerous Black Box</strong> is where I keep the notes I got tired of re-looking-up &mdash; which ship to fly for a job, how to unlock an engineer, what a blueprint costs, where to farm the mats. It started as a side project &mdash; somewhere to learn the game's systems for myself &mdash; but as the pile of personal notes grew it became a resource worth sharing. So it's all in one cross-linked place now, written the way one commander would explain it to another.</p>
    <p>There's a dossier for every ship-and-role worth flying, the ladders that rank them, and the reasoning behind each rating. The engineering side has the referral tree, the blueprint and module references, farm routes, and an unlock checklist. The systems side explains how the game's mechanics actually work and how to run each activity.</p>
    <p>Whether you're picking your first proper ship or fine-tuning a maxed-out build, there's something here. I keep the hard numbers honest: every stat is checked against coriolis-data, INARA, EDSY and the rest, and sourced on the page. The ratings and loadout calls are my opinion, and I say so where it counts.</p>
    <p>Start with <a href="#section-dossiers">Ships</a>, <a href="#section-engineering">Engineering</a> or <a href="#section-systems">Systems</a> below. Every dossier comes with a loadout you can open straight in Coriolis or EDSY, the reasoning for its rating, and an engineering plan to follow.</p>
  </section>

  <!-- ---- 02 SHIPS ---- -->
  <section id="section-dossiers">
    <div class="sec-head"><span class="sec-num">02</span><h2>Ships</h2><span class="tag">Fly the right hull</span></div>
    <p class="lead">How each career plays, which hull wins each role, and a dossier for every viable ship &times; role pairing.</p>

    <h3 class="subhead" id="section-general">General</h3>
    <p>How every ship is rated — and how the whole fleet stacks up across all seven roles.</p>
    <div class="gcards">
HEAD

card "ships/general/rating-methodology.html"   ""  "Rating Methodology"    "How every ship earns its 1–100 suitability rating — the roster-relative, fully-engineered rubric."
card "ships/general/ship-role-matrix.html"      ""  "Ship × Role Matrix"    "Every published ship-role suitability score on one sortable grid — 48 hulls across seven roles, each cell linked straight to its dossier."

cat <<'SHIPS_BEST'
    </div>

    <h3 class="subhead" id="section-best-ships">Best Ships by Role</h3>
    <p>"What should I fly for this?" — ships ranked head-to-head for each role.</p>
    <div class="gcards">
SHIPS_BEST

card "ships/best-ships-by-role/combat.html"       ""  "Combat"       "Combat ships ranked, from starter to capital."
card "ships/best-ships-by-role/ax.html"           ""  "Anti-Xeno (AX)"    "The ships that hold up against Thargoids."
card "ships/best-ships-by-role/exploration.html"  ""  "Exploration"  "Jump range, comfort and the long black, ranked."
card "ships/best-ships-by-role/mining.html"       ""        "Mining"       "Mining platforms ranked by yield and fit."
card "ships/best-ships-by-role/trading.html"      "" "Trading"      "Cargo haulers ranked by tonnage and economy."
card "ships/best-ships-by-role/passenger.html"    ""  "Passenger"    "Cabin capacity and range for the tourism trade."
card "ships/best-ships-by-role/multipurpose.html" ""        "Multipurpose"     "Do-everything ships ranked for the multipurpose pilot."

cat <<'SHIPS3'
    </div>

    <h3 class="subhead" id="section-ship-dossiers">Ship Dossiers</h3>
    <p>A dossier for every viable ship-and-role pairing — rating, spec readout and recommended loadout. Pick a ship, then a role.</p>
    <div class="ship-grid">
SHIPS3

# ---- ship dossiers, auto-discovered (slug-role.html) and grouped by ship ----
# Filenames are kebab-case `<ship-slug>-<role>.html`; role = last '-' token,
# ship-slug = the rest. Display name comes from ship_name() (ship-names.tsv).
for f in "$GUIDES"/ships/ship-dossiers/*.html; do
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
    printf '<a class="%s" href="ships/ship-dossiers/%s">%s</a>' "$cls" "$file" "$(role_label "$role")"
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

card "engineering/engineering-manuals/checklist.html"  ""       "Unlock Checklist"   "New-pilot engineering progression — what to unlock, and when."
card "engineering/engineering-manuals/engineers.html"  ""       "Engineers"      "Every engineer: location, meeting requirement, unlock and referrals."
card "engineering/engineering-manuals/blueprints.html" ""       "Blueprints"         "The module blueprint catalogue across every grade and effect."
card "engineering/engineering-manuals/modules.html"    ""       "Modules"            "Every outfitting slot — core internals, optionals, hardpoints and utilities, the A–E trade-off and what to fit per role."

cat <<'FARM'
    </div>

    <h3 class="subhead" id="section-farming">Materials &amp; Farming</h3>
    <p>What the materials are, how the trader works, and the known sites and loops for stocking them.</p>
    <div class="gcards">
FARM

card "engineering/materials-and-farming/materials.html"            "" "Materials"            "The three material types, grade ladders and trader exchange ratios — hoard high, trade down."
card "engineering/materials-and-farming/davs-hope.html"            "" "Dav's Hope"           "The classic manufactured-material loop at Dav's Hope."
card "engineering/materials-and-farming/crystalline-shards.html"   "" "Crystalline Shards"   "Surface raw-material farming at Crystalline Shard sites."
card "engineering/materials-and-farming/high-grade-emissions.html" "" "High Grade Emissions" "Farming encoded materials from High Grade Emission signals."
card "engineering/materials-and-farming/jameson-crash-site.html"   "" "Jameson Crash Site"   "The Jameson Crash Site encoded-data farm."

cat <<'SYS'
    </div>
  </section>

  <!-- ---- 04 SYSTEMS ---- -->
  <section id="section-systems">
    <div class="sec-head"><span class="sec-num">04</span><h2>Systems</h2><span class="tag">How the galaxy runs</span></div>
    <p class="lead">Getting started, the big persistent systems that run the galaxy, and where to go looking for a fight.</p>

    <h3 class="subhead" id="section-new-pilot">New Pilot &amp; Interface</h3>
    <p>Start here — what to do as a new commander, how ranks work, and the site lexicon — then docking, the cockpit HUD, and the companion apps every commander runs.</p>
    <div class="gcards">
SYS

card "systems/new-pilot-and-interface/new-cmdr-guide.html"          ""  "New CMDR's Guide"   "Your first hours in the black — controls, the core loop, the career tracks, first credits, and a getting-started checklist."
card "systems/new-pilot-and-interface/pilots-federation.html"       ""  "Pilots Federation" "What the Pilots Federation is, and every pilot rank ladder — how each is earned and what it unlocks."
card "systems/new-pilot-and-interface/cmdrs-lexicon.html"            ""  "CMDR's Lexicon"        "The site glossary — Elite Dangerous terminology, acronyms and community slang, defined and cross-linked."
card "systems/new-pilot-and-interface/docking-landing-manual.html" ""  "Docking &amp; Landing" "Requesting docking, pads, and station/outpost landing procedure."
card "systems/new-pilot-and-interface/hud-customization.html"      ""  "HUD Customization"     "Retune your cockpit HUD colours with the GraphicsConfig matrix."
card "systems/new-pilot-and-interface/third-party-apps.html"       ""  "Third-Party Apps"      "The essential companion apps, planners and tools for commanders."

cat <<'SYS2'
    </div>

    <h3 class="subhead" id="section-galaxy">Galaxy &amp; Power Systems</h3>
    <p>The big persistent systems — factions, powers, rank, and the things you build once you have credits to spare.</p>
    <div class="gcards">
SYS2

card "systems/galaxy-and-power-systems/bgs.html"                 ""        "Background Simulation" "How minor factions, influence and states actually work."
card "systems/galaxy-and-power-systems/powerplay.html"           ""        "Powerplay"                   "Pledging to a Power, earning merits, and the weekly cycle."
card "systems/galaxy-and-power-systems/superpower-rank.html"     ""        "Superpower Rank"       "Climbing Federation, Empire and Alliance reputation."
card "systems/galaxy-and-power-systems/community-goals.html"     ""        "Community Goals"             "How CGs work and how to land in the top tiers."
card "systems/galaxy-and-power-systems/system-colonization.html" ""  "System Colonisation"         "Claiming systems and building out your own infrastructure."
card "systems/galaxy-and-power-systems/fleet-carrier.html"       ""  "Fleet Carrier"              "Buying, financing, fitting and jumping a Fleet Carrier."

cat <<'SYS3'
    </div>

    <h3 class="subhead" id="section-activities">Activity Guides</h3>
    <p>How each career actually plays — the loop, the gear, and the money.</p>
    <div class="gcards">
SYS3

card "systems/activity-guides/combat.html"      ""  "Combat"       "Bounty hunting, massacre missions and PvE combat."
card "systems/activity-guides/ax.html"          ""  "Anti-Xeno" "Fighting Thargoids — gear, tactics and venues."
card "systems/activity-guides/exploration.html" ""  "Exploration"  "Long-range exploration, scanning and exobiology."
card "systems/activity-guides/mining.html"      ""        "Mining"       "Laser, core and subsurface mining for profit."
card "systems/activity-guides/trading.html"     "" "Trading"      "Cargo trading, loops and reading the market."
card "systems/activity-guides/passenger.html"   ""  "Passenger"    "Passenger missions, tourism and sightseeing runs."

cat <<'SYS4'
    </div>

    <h3 class="subhead" id="section-combat-venues">Combat Venues</h3>
    <p>The places you go looking for a fight, and what each pays.</p>
    <div class="gcards">
SYS4

card "systems/combat-venues/combat-zones.html"      "" "Combat Zones" "Conflict Zones — tactics, payouts, and how to read a CZ."
card "systems/combat-venues/pve-combat-venues.html" "" "PvE Combat Venues"       "RES, CZ, Nav Beacons and signal sources for PvE combat."

cat <<'FOOT'
    </div>
  </section>

  <!-- ---- 05 FAQ ---- -->
  <section id="section-faq">
    <div class="sec-head"><span class="sec-num">05</span><h2>FAQ</h2><span class="tag">Good to know</span></div>
    <div class="faq">
      <div class="faq-row"><h4 class="faq-q">Is this affiliated with Frontier Developments?</h4><p class="faq-a">No. The Black Box is unofficial fan content &mdash; not affiliated with, sponsored by, or endorsed by Frontier Developments. <em>Elite Dangerous</em> is a trademark of Frontier Developments plc, and all game data, names and imagery remain their property.</p></div>
      <div class="faq-row"><h4 class="faq-q">Is this a complete guide to the game?</h4><p class="faq-a">No. The Black Box covers only the ships, systems and activities I've worked through myself so far &mdash; not the whole of Elite Dangerous. I add guides as I get hands-on with more of the game, so the library keeps growing; expect gaps, and expect them to fill in over time. Want something specific covered next? <a href="https://github.com/tusharsaxena/ed-blackbox/issues">Open a feature request</a>.</p></div>
      <div class="faq-row"><h4 class="faq-q">Does this apply to my platform (PC / console)?</h4><p class="faq-a">Mostly PC. This manual targets the <strong>Live (Odyssey 4.0)</strong> game. Console (PS4/Xbox) is frozen on <strong>Legacy 3.8</strong> &mdash; Frontier ended console development in 2022 &mdash; so it never got Odyssey, Powerplay 2.0, System Colonisation, or any ship added since late 2022 (Python Mk II, Cobra Mk V, Kestrel Mk II, Lynx Highliner&hellip;). For hulls that exist on both, core stats and engineering still match, so those ratings and builds hold &mdash; but the newer-ship dossiers and several systems guides are Live-only.</p></div>
      <div class="faq-row"><h4 class="faq-q">How current is the information?</h4><p class="faq-a">Game figures &mdash; ship, module and engineering stats &mdash; are checked against EDCD/coriolis-data, INARA, EDSY and Coriolis, and every page lists its sources at the foot. Ship ratings, loadouts and &ldquo;best for the job&rdquo; picks are <em>editorial judgement</em>, not Frontier data. When the game changes a page can lag; anything uncertain is marked rather than guessed, and corrections are welcome.</p></div>
      <div class="faq-row"><h4 class="faq-q">How are the ship ratings decided?</h4><p class="faq-a">Each ship gets a 1&ndash;100 score for a given role, but it's a judgement call, not a spec-sheet sum. The number is <em>roster-relative</em> (measured against every other ship doing that job), assumes a <em>fully-engineered</em> build, and is weighed across an ordered set of role factors. Every dossier shows the working in its &ldquo;Why This Rating&rdquo; scorecard, and the full method is on the <a href="ships/general/rating-methodology.html">rating methodology</a> page.</p></div>
      <div class="faq-row"><h4 class="faq-q">Why is the same ship rated differently in different roles?</h4><p class="faq-a">Because each score is set against the field <em>for that role</em>, using that role's factor weights. A hull that's a monster hauler can be middling in a knife-fight, so its trading and combat numbers differ on purpose. Compare ships within a role, not across roles.</p></div>
      <div class="faq-row"><h4 class="faq-q">Can I open these builds in Coriolis or EDSY?</h4><p class="faq-a">Yes. Every dossier's 3-State Loadout has <strong>Open in Coriolis</strong> and <strong>Open in EDSY</strong> links that load the exact build straight into the planner &mdash; no copy-paste &mdash; plus a <strong>Copy SLEF</strong> button to drop it into anything else that reads Ship Loadout Export Format.</p></div>
      <div class="faq-row"><h4 class="faq-q">What do the three loadout columns mean?</h4><p class="faq-a">They're a budget path, not one fixed build. <strong>Initial</strong> is buy-only with no engineering &mdash; what you fly the day you buy the hull. <strong>A-Rated</strong> swaps in A-rated cores for a combat-ready ship. <strong>Engineered</strong> is the full blueprint-and-experimental tour. Fly whichever column you can afford and work toward the next.</p></div>
      <div class="faq-row"><h4 class="faq-q">Do I have to engineer everything?</h4><p class="faq-a">No. The A-Rated column is a genuinely capable ship on its own &mdash; engineering is the ceiling, not the price of entry. Engineer when you're ready; each dossier's plan tells you what to prioritise first.</p></div>
      <div class="faq-row"><h4 class="faq-q">Why isn't a particular ship or role covered?</h4><p class="faq-a">The dossiers cover the ship &times; role pairings actually worth flying. If a hull can't do a job well enough to recommend, it's left out rather than padded with a build no one should fly.</p></div>
      <div class="faq-row"><h4 class="faq-q">Is this AI-generated content?</h4><p class="faq-a">Yes &mdash; although I prefer to call it <em>curated</em> AI content. I steer the model deliberately to write the guides I want, including fact-checking against authoritative sources. It began as a side project to learn Elite Dangerous's systems for myself; as the collection of personal guides grew, it became something worth sharing. I've done my best to credit every source used &mdash; if your work isn't credited, <a href="https://github.com/tusharsaxena/ed-blackbox/issues">open an issue</a> and I'll make it right.</p></div>
      <div class="faq-row"><h4 class="faq-q">Found an error, or want to contribute?</h4><p class="faq-a">This is a personal project by CMDR Ka0s. Spot a wrong number, a broken link, or a build you'd fit differently? <a href="https://github.com/tusharsaxena/ed-blackbox/issues">Open an issue</a>. Ratings and loadouts are opinions &mdash; disagree and say why; a well-argued correction gets folded in.</p></div>
    </div>
  </section>

  <!-- ---- 06 CHANGELOG ----
       Hand-written. Dates are FIXED, NOT the build date. Add a release only
       when explicitly asked — do not auto-edit this section. -->
  <section id="section-changelog">
    <div class="sec-head"><span class="sec-num">06</span><h2>Changelog</h2><span class="tag">Releases</span></div>
    <p class="lead">Notable updates to the Black Box.</p>
    <h3 class="subhead">2026-06-23 &mdash; Initial release</h3>
    <ul class="bullets">
      <li>First public release of the Elite:Dangerous Black Box field-manual library.</li>
      <li>All guides unified on the shared design system.</li>
    </ul>
  </section>

  <!-- ---- FOOTER ---- -->
  <footer>
    <div class="ft-fine">
      <span>&copy; 2026 Elite:Dangerous Black Box &middot; CMDR Ka0s &middot; Fly safe, commander. &middot; <a href="https://github.com/tusharsaxena/ed-blackbox/issues">Report an issue</a></span>
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

# Substitute the computed hero stat-card counts.
sed -i -e "s/__SHIPS__/$SHIPS_COUNT/" -e "s/__ENG__/$ENG_COUNT/" \
       -e "s/__SYSTEMS__/$SYSTEMS_COUNT/" -e "s/__TOTAL__/$TOTAL_COUNT/" "$OUT"

echo "Wrote $OUT"
grep -c 'class="ship"' "$OUT" | sed 's/^/ship rows: /'
grep -c 'class="gcard' "$OUT" | sed 's/^/guide cards: /'
