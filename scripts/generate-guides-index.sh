#!/usr/bin/env bash
#
# generate-guides-index.sh
# -----------------------------------------------------------------------------
# Regenerates guides/index.html — the "Black Book" landing page that links to
# every guide in the project, grouped logically.
#
# The look & feel is copied from guides/engineering/Engineers.html (the inline
# CSS, fonts, masthead, sections, footer) — it intentionally does NOT use the
# design-system/ stylesheet yet.
#
# WHAT IT DOES
#   - Emits a self-contained guides/index.html.
#   - Hand-curated cards for the game-system, engineering, farming, activity and
#     role guides (title + one-line description, set in the CARD CALLS below).
#   - Auto-discovers every ship dossier in guides/ship/ship/*.html and groups
#     them by ship, with one role link per dossier (colour-coded by role).
#
# WHEN TO RE-RUN
#   - After adding/removing/renaming any ship dossier (ship/ship/*.html) — the
#     ship grid is rebuilt from the filesystem, so those stay in sync for free.
#   - After adding a new top-level guide (misc/, farm/, role-*), add a matching
#     `card ...` line in the relevant section below, then re-run.
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

# Map a role name to a role-chip colour class (used in the ship grid).
role_class(){ case "$1" in Combat|AX) echo "r-mar";; Exploration|Passenger) echo "r-fed";; Trading) echo "r-good";; *) echo "";; esac; }

{
cat <<'HEAD'
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Black Book | E:D Black Box</title>
<link rel="icon" type="image/png" href="../images/logos/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;500;600;700&family=Saira:wght@300;400;500;600&family=Saira+Condensed:wght@500;600;700&display=swap" rel="stylesheet">
<style>
:root{--bg:#0a0708;--bg2:#0e0a0b;--panel:#140d0f;--panel2:#1a1113;--grid:rgba(180,70,60,.045);
--maroon:#8b2332;--maroon-lt:#b13140;--amber:#e0913a;--amber-lt:#f4b15f;--fed:#4f9fd6;--fed-lt:#7cc0ee;
--danger:#d8423b;--good:#5fb37a;--good-lt:#7fce98;--ink:#ece4df;--ink-dim:#a89a93;--ink-faint:#6e615c;
--hair:rgba(190,120,110,.16);--hair-strong:rgba(190,120,110,.32);}
*{box-sizing:border-box;margin:0;padding:0}html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--ink);font-family:'Saira',sans-serif;font-weight:300;line-height:1.62;letter-spacing:.2px;-webkit-font-smoothing:antialiased;overflow-x:hidden}
body::before{content:"";position:fixed;inset:0;z-index:0;pointer-events:none;background-image:linear-gradient(var(--grid) 1px,transparent 1px),linear-gradient(90deg,var(--grid) 1px,transparent 1px);background-size:42px 42px}
body::after{content:"";position:fixed;inset:0;z-index:0;pointer-events:none;background:radial-gradient(900px 600px at 78% -8%,rgba(224,145,58,.10),transparent 60%),radial-gradient(1000px 700px at 10% 4%,rgba(139,35,50,.16),transparent 62%),radial-gradient(1200px 900px at 50% 120%,rgba(79,159,214,.07),transparent 60%)}
.wrap{position:relative;z-index:1;max-width:1140px;margin:0 auto;padding:0 22px 120px}
/* ---- global sticky header + landing hero (v1.1.0) ---- */
.site-header{position:sticky;top:0;z-index:50;background:var(--bg);border-bottom:1px solid var(--hair-strong)}
.site-header .hdr-inner{max-width:1140px;margin:0 auto;padding:0 22px;height:62px;display:flex;align-items:center;gap:22px}
.brand{display:flex;align-items:center;gap:10px;text-decoration:none;flex:none}
.brand img{width:34px;height:34px;display:block;filter:drop-shadow(0 0 7px rgba(224,145,58,.35))}
.brand .wordmark{font-family:'Chakra Petch',sans-serif;font-weight:700;font-size:14px;letter-spacing:2.5px;text-transform:uppercase;color:var(--ink);white-space:nowrap}
.brand .wordmark .hl{color:var(--amber)}
.brand:hover .wordmark{color:#fff}
.nav-sep{width:1px;height:26px;background:var(--hair-strong);flex:none;margin:0 6px}
.site-nav{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-left:auto}
.site-nav a{font-family:'Saira Condensed',sans-serif;font-weight:600;font-size:14px;letter-spacing:1.6px;text-transform:uppercase;color:var(--ink-dim);text-decoration:none;padding:8px 4px;position:relative}
.site-nav a:hover{color:var(--amber-lt)}
.site-nav a.active{color:var(--amber)}
.site-nav a.active::after{content:"";position:absolute;left:4px;right:4px;bottom:0;height:2px;background:var(--amber);border-radius:2px}
.hero{margin-bottom:10px}
.hero img{display:block;width:100%;max-width:560px;height:auto;border-radius:6px;border:1px solid var(--hair-strong);box-shadow:0 8px 30px rgba(0,0,0,.4)}
header.masthead{padding:54px 0 26px;border-bottom:1px solid var(--hair-strong);margin-bottom:8px}
.kicker{font-family:'Chakra Petch',sans-serif;font-weight:600;font-size:12px;letter-spacing:5px;text-transform:uppercase;color:var(--amber);display:flex;align-items:center;gap:12px;margin-bottom:18px;flex-wrap:wrap}
.kicker::before{content:"";width:34px;height:1px;background:var(--amber);opacity:.7}
.kicker .id{margin-left:auto;color:var(--ink-faint);letter-spacing:3px;font-weight:500}
h1.title{font-family:'Chakra Petch',sans-serif;font-weight:700;font-size:clamp(34px,6vw,62px);line-height:.98;letter-spacing:1px;color:var(--ink);text-transform:uppercase}
h1.title span{color:var(--amber)}
.subtitle{margin-top:16px;font-size:clamp(15px,2.2vw,18px);color:var(--ink-dim);max-width:840px;font-weight:300}
.masthead-meta{margin-top:26px;display:flex;flex-wrap:wrap;gap:10px 26px;font-family:'Saira Condensed',sans-serif;font-size:13px;letter-spacing:1px;text-transform:uppercase;color:var(--ink-faint)}
.masthead-meta b{color:var(--amber-lt);font-weight:600}
.verdict{margin:34px 0 14px;border:1px solid rgba(224,145,58,.4);border-radius:4px;background:linear-gradient(180deg,rgba(224,145,58,.10),rgba(20,13,15,.6));padding:30px 30px 26px;position:relative;overflow:hidden}
.verdict::before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:linear-gradient(180deg,var(--amber),transparent)}
.verdict .v-eyebrow{font-family:'Chakra Petch',sans-serif;font-weight:600;font-size:11px;letter-spacing:4px;text-transform:uppercase;color:var(--amber-lt);margin-bottom:10px}
.verdict h2{font-family:'Chakra Petch',sans-serif;font-weight:700;font-size:clamp(22px,4vw,32px);line-height:1.05;text-transform:uppercase;letter-spacing:.5px;color:var(--ink);margin-bottom:6px}
.verdict h2 em{font-style:normal;color:var(--amber-lt)}
.verdict p{font-size:15.5px;color:var(--ink-dim);margin-top:12px;max-width:980px}
.stat-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:14px;margin:22px 0 4px}
.stat{background:rgba(10,7,8,.5);border:1px solid var(--hair);border-radius:4px;padding:16px 18px}
.stat .n{font-family:'Chakra Petch',sans-serif;font-weight:700;font-size:26px;color:var(--amber-lt);line-height:1}
.stat .n.fed{color:var(--fed-lt)}.stat .n.mar{color:var(--maroon-lt)}
.stat .l{font-size:12.5px;color:var(--ink-dim);margin-top:6px;letter-spacing:.3px}
section{margin-top:56px;scroll-margin-top:20px}
.sec-head{display:flex;align-items:center;gap:16px;margin-bottom:8px;border-bottom:1px solid var(--hair);padding-bottom:14px}
.sec-num{font-family:'Chakra Petch',sans-serif;font-weight:700;font-size:clamp(21px,3.4vw,30px);line-height:1;letter-spacing:2px;color:var(--bg);background:var(--amber);padding:.12em .4em;border-radius:2px;flex:none}
.sec-head h2{font-family:'Chakra Petch',sans-serif;font-weight:700;font-size:clamp(21px,3.4vw,30px);text-transform:uppercase;letter-spacing:.6px;color:var(--ink);line-height:1.05}
.sec-head .tag{margin-left:auto;font-family:'Saira Condensed',sans-serif;font-size:12px;letter-spacing:2px;text-transform:uppercase;color:var(--ink-faint);flex:none;align-self:center}
p.lead{font-size:15px;color:var(--ink-dim);margin:14px 0 4px}
a{color:var(--amber-lt)}
.muted{color:var(--ink-faint)}
/* ---- guide cards ---- */
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(264px,1fr));gap:14px;margin-top:20px}
.gcard{display:block;background:var(--panel);border:1px solid var(--hair);border-left:3px solid var(--amber);border-radius:4px;padding:16px 18px;text-decoration:none;transition:background .18s,border-color .18s,transform .12s}
.gcard:hover{background:var(--panel2);transform:translateY(-1px)}
.gcard.ac-fed{border-left-color:var(--fed)}.gcard.ac-mar{border-left-color:var(--maroon-lt)}.gcard.ac-good{border-left-color:var(--good)}
.gcard h3{font-family:'Chakra Petch',sans-serif;font-weight:700;font-size:16px;letter-spacing:.4px;color:var(--ink);line-height:1.15;margin-bottom:7px}
.gcard:hover h3{color:var(--amber-lt)}
.gcard p{font-size:13px;color:var(--ink-dim);line-height:1.5}
/* ---- ship dossier grid ---- */
.ship-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:10px;margin-top:20px}
.ship{display:flex;align-items:center;gap:12px;background:var(--panel);border:1px solid var(--hair);border-radius:4px;padding:11px 15px;transition:background .18s}
.ship:hover{background:var(--panel2)}
.ship .nm{font-family:'Chakra Petch',sans-serif;font-weight:600;font-size:13.5px;letter-spacing:.3px;color:var(--ink);flex:1;text-transform:uppercase}
.ship .roles{display:flex;flex-wrap:wrap;gap:6px;justify-content:flex-end}
.ship .roles a{font-family:'Saira Condensed',sans-serif;font-size:11px;font-weight:600;letter-spacing:.6px;text-transform:uppercase;color:var(--amber-lt);text-decoration:none;border:1px solid var(--hair-strong);border-radius:10px;padding:2px 10px;transition:.14s;white-space:nowrap}
.ship .roles a:hover{color:var(--bg);background:var(--amber-lt);border-color:var(--amber-lt)}
.ship .roles a.r-fed{color:var(--fed-lt)}.ship .roles a.r-fed:hover{background:var(--fed-lt);border-color:var(--fed-lt);color:var(--bg)}
.ship .roles a.r-mar{color:var(--maroon-lt)}.ship .roles a.r-mar:hover{background:var(--maroon-lt);border-color:var(--maroon-lt);color:var(--ink)}
.ship .roles a.r-good{color:var(--good-lt)}.ship .roles a.r-good:hover{background:var(--good-lt);border-color:var(--good-lt);color:var(--bg)}
/* ---- back to top ---- */
.totop{position:fixed;right:22px;bottom:22px;z-index:60;width:42px;height:42px;display:flex;align-items:center;justify-content:center;background:rgba(16,10,12,.92);border:1px solid var(--hair-strong);border-radius:6px;color:var(--amber-lt);font-size:20px;text-decoration:none;backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);opacity:0;pointer-events:none;transition:opacity .2s,background .18s}
.totop.show{opacity:1;pointer-events:auto}
.totop:hover{background:var(--panel2)}
footer{margin-top:70px;padding-top:24px;border-top:1px solid var(--hair-strong);font-family:'Saira Condensed',sans-serif;font-size:12.5px;letter-spacing:1px;text-transform:uppercase;color:var(--ink-faint);display:flex;flex-wrap:wrap;gap:8px 20px}
footer b{color:var(--amber-lt)}
@media (max-width:560px){.sec-head .tag{display:none}}
@media (prefers-reduced-motion:reduce){*{scroll-behavior:auto}.gcard:hover{transform:none}}
</style>
</head>
<body>
<header class="site-header">
  <div class="hdr-inner">
    <a class="brand" href="index.html" aria-label="E:D Black Box — home">
      <img src="../images/logos/logo.png" alt="">
      <span class="wordmark"><span class="hl">E:D</span> Black Box</span>
    </a>
    <span class="nav-sep" aria-hidden="true"></span>
    <nav class="site-nav" aria-label="Primary">
      <a href="#" class="active">Home</a>
      <a href="#dossiers">Ships</a>
      <a href="#engineering">Engineering</a>
      <a href="#systems">Systems</a>
    </nav>
  </div>
</header>
<div class="wrap">
<header class="masthead">
  <div class="hero"><img src="../images/logos/banner.png" alt="E:D Black Box" width="560"></div>
  <div class="kicker">Elite Dangerous Field Manuals</div>
  <h1 class="title">The Black <span>Book</span></h1>
  <p class="subtitle">A growing library of operator-grade field manuals for Elite Dangerous: Odyssey — engineering, ships, combat, trade, and the systems that run the galaxy. Written commander-to-commander. Pick a manual below.</p>
  <div class="masthead-meta">
    <span><b>100+</b> manuals</span>
    <span>Updated <b>__BUILD_DATE__</b></span>
  </div>
</header>
<div class="verdict">
  <div class="v-eyebrow">Start Here</div>
  <h2>Everything a commander needs, in <em>one shelf</em>.</h2>
  <p>The Black Book collects the field manuals into a single index: the engineering referral tree and blueprint catalogue, material-farm routes, activity playbooks, "best ship for the job" ladders, and a full set of ship × role dossiers. New here? Start with the game-systems manuals, then pick a ship and a role.</p>
</div>
<div class="stat-grid">
  <div class="stat"><div class="n">11</div><div class="l">Game-system guides</div></div>
  <div class="stat"><div class="n">3</div><div class="l">Engineering manuals</div></div>
  <div class="stat"><div class="n fed">77</div><div class="l">Ship dossiers</div></div>
  <div class="stat"><div class="n mar">13</div><div class="l">Role &amp; activity guides</div></div>
</div>

<section id="systems">
  <div class="sec-head"><span class="sec-num">01</span><h2>New Pilot &amp; Interface</h2><span class="tag">Basics</span></div>
  <p class="lead">Get off the ground: docking, the cockpit HUD, and the companion apps every commander runs.</p>
  <div class="cards">
HEAD

card "misc/Docking_Landing_Manual.html" ""       "Docking &amp; Landing"      "Requesting docking, pads, and station/outpost landing procedure."
card "misc/HUD_Customization.html"      ""       "HUD Customization"        "Retune your cockpit HUD colours with the GraphicsConfig matrix."
card "misc/Third_Party_Apps_apps.html"  ""       "Third-Party Apps"         "The essential companion apps, planners and tools for commanders."

cat <<'S2'
  </div>
</section>

<section id="galaxy">
  <div class="sec-head"><span class="sec-num">02</span><h2>Galaxy &amp; Power Systems</h2><span class="tag">Endgame loops</span></div>
  <p class="lead">The big persistent systems — factions, powers, rank, and the things you build once you have credits to spare.</p>
  <div class="cards">
S2

card "misc/BGS.html"                 ""        "Background Simulation (BGS)" "How minor factions, influence and states actually work."
card "misc/Powerplay.html"           ""        "Powerplay"                   "Pledging to a Power, earning merits, and the weekly cycle."
card "misc/Superpower_Rank.html"     ""        "Superpower Rank Grind"       "Climbing Federation, Empire and Alliance reputation."
card "misc/Community_Goals.html"     ""        "Community Goals"             "How CGs work and how to land in the top tiers."
card "misc/System_Colonization.html" "ac-fed"  "System Colonization"         "Claiming systems and building out your own infrastructure."
card "misc/Fleet_Carrier.html"       "ac-fed"  "Fleet Carriers"              "Buying, financing, fitting and jumping a Fleet Carrier."

cat <<'S3'
  </div>
</section>

<section id="combat-venues">
  <div class="sec-head"><span class="sec-num">03</span><h2>Combat Venues</h2><span class="tag">Where to fight</span></div>
  <p class="lead">The places you go looking for a fight, and what each pays.</p>
  <div class="cards">
S3

card "misc/Combat_Zones.html"      "ac-mar" "Combat / Conflict Zones" "Conflict Zones — tactics, payouts, and how to read a CZ."
card "misc/PVE_Combat_Venues.html" "ac-mar" "PVE Combat Venues"       "RES, CZ, Nav Beacons and signal sources for PvE combat."

cat <<'S4'
  </div>
</section>

<section id="engineering">
  <div class="sec-head"><span class="sec-num">04</span><h2>Engineering</h2><span class="tag">3 manuals</span></div>
  <p class="lead">The full engineering set — who modifies your gear, what they grant, and the order to unlock them.</p>
  <div class="cards">
S4

card "engineering/Checklist.html"  ""       "Unlock Checklist"   "New-pilot engineering progression — what to unlock, and when."
card "engineering/Engineers.html"  ""       "The Engineers"      "Every engineer: location, meeting requirement, unlock and referrals."
card "engineering/Blueprints.html" ""       "Blueprints"         "The module blueprint catalogue across every grade and effect."

cat <<'S5'
  </div>
</section>

<section id="farming">
  <div class="sec-head"><span class="sec-num">05</span><h2>Material Farming</h2><span class="tag">Farm routes</span></div>
  <p class="lead">Known sites and loops for stocking the materials engineering eats.</p>
  <div class="cards">
S5

card "engineering/farm/Davs_Hope.html"           "ac-good" "Dav's Hope"            "The classic manufactured-material loop at Dav's Hope."
card "engineering/farm/Crystalline_Shards.html"  "ac-good" "Crystalline Shards"    "Surface raw-material farming at Crystalline Shard sites."
card "engineering/farm/High_Grade_Emissions.html" "ac-good" "High Grade Emissions" "Farming encoded materials from High Grade Emission signals."
card "engineering/farm/Jameson_Crash_Site.html"  "ac-good" "Jameson Crash Site"    "The Jameson Crash Site encoded-data farm."

cat <<'S6'
  </div>
</section>

<section id="activities">
  <div class="sec-head"><span class="sec-num">06</span><h2>Activity Field Manuals</h2><span class="tag">How to play a role</span></div>
  <p class="lead">How each career actually plays — the loop, the gear, and the money.</p>
  <div class="cards">
S6

card "ship/role-activities/Combat.html"      "ac-mar"  "Combat"       "Bounty hunting, massacre missions and PvE combat."
card "ship/role-activities/AX.html"          "ac-mar"  "Anti-Xeno (AX)" "Fighting Thargoids — gear, tactics and venues."
card "ship/role-activities/Exploration.html" "ac-fed"  "Exploration"  "Long-range exploration, scanning and exobiology."
card "ship/role-activities/Mining.html"      ""        "Mining"       "Laser, core and subsurface mining for profit."
card "ship/role-activities/Trading.html"     "ac-good" "Trading"      "Cargo trading, loops and reading the market."
card "ship/role-activities/Passenger.html"   "ac-fed"  "Passenger"    "Passenger missions, tourism and sightseeing runs."

cat <<'S7'
  </div>
</section>

<section id="best-ships">
  <div class="sec-head"><span class="sec-num">07</span><h2>Best Ships by Role</h2><span class="tag">Ranked ladders</span></div>
  <p class="lead">"What should I fly for this?" — ships ranked head-to-head for each role.</p>
  <div class="cards">
S7

card "ship/role-ship/Combat.html"       "ac-mar"  "Best for Combat"       "Combat ships ranked, from starter to capital."
card "ship/role-ship/AX.html"           "ac-mar"  "Best for Anti-Xeno"    "The ships that hold up against Thargoids."
card "ship/role-ship/Exploration.html"  "ac-fed"  "Best for Exploration"  "Jump range, comfort and the long black, ranked."
card "ship/role-ship/Mining.html"       ""        "Best for Mining"       "Mining platforms ranked by yield and fit."
card "ship/role-ship/Trading.html"      "ac-good" "Best for Trading"      "Cargo haulers ranked by tonnage and economy."
card "ship/role-ship/Passenger.html"    "ac-fed"  "Best for Passenger"    "Cabin capacity and range for the tourism trade."
card "ship/role-ship/Multipurpose.html" ""        "Best All-Rounders"     "Do-everything ships ranked for the multipurpose pilot."

cat <<'S8'
  </div>
</section>

<section id="dossiers">
  <div class="sec-head"><span class="sec-num">08</span><h2>Ship Dossiers</h2><span class="tag">77 ship × role</span></div>
  <p class="lead">A dossier for every viable ship-and-role pairing — rating, spec readout and recommended loadout. Pick a ship, then a role.</p>
  <div class="ship-grid">
S8

# ---- ship dossiers, auto-discovered and grouped by ship ----
for f in "$GUIDES"/ship/ship/*.html; do
  base="$(basename "$f" .html)"
  role="$(echo "$base" | sed -E 's/.*_([A-Za-z]+)$/\1/')"
  ship="$(echo "$base" | sed -E 's/_[A-Za-z]+$//' | tr '_' ' ')"
  echo "$ship|$role|$base.html"
done | awk -F'|' '{ships[$1]=ships[$1]$2"="$3";"} END{for(s in ships)print s"|"ships[s]}' | sort | \
while IFS='|' read -r ship roles; do
  printf '    <div class="ship"><span class="nm">%s</span><span class="roles">' "$ship"
  echo "$roles" | tr ';' '\n' | while IFS='=' read -r role file; do
    [ -z "$role" ] && continue
    cls="$(role_class "$role")"
    printf '<a class="%s" href="ship/ship/%s">%s</a>' "$cls" "$file" "$role"
  done
  printf '</span></div>\n'
done

cat <<'FOOT'
  </div>
</section>

<footer>
  <span>E:D Black Box</span>
  <span>By <b>CMDR Ka0s</b></span>
  <span>Elite Dangerous: Odyssey</span>
  <span><b>Fly safe, commander.</b></span>
</footer>
</div>
<a href="#" class="totop" id="totop" aria-label="Back to top">↑</a>
<script>
(function(){
  var btn=document.getElementById('totop');
  if(!btn) return;
  window.addEventListener('scroll',function(){
    if(window.scrollY>500){btn.classList.add('show');}else{btn.classList.remove('show');}
  },{passive:true});
  btn.addEventListener('click',function(e){e.preventDefault();window.scrollTo({top:0,behavior:'smooth'});});
})();
</script>
</body>
</html>
FOOT
} > "$OUT"

# Stamp the masthead "Updated" line with the build date (heredocs are single-quoted,
# so the placeholder is substituted here rather than expanded inline).
sed -i "s/__BUILD_DATE__/$(date +%F)/" "$OUT"

echo "Wrote $OUT"
grep -c 'class="ship"' "$OUT" | sed 's/^/ship rows: /'
grep -c 'class="gcard' "$OUT" | sed 's/^/guide cards: /'
