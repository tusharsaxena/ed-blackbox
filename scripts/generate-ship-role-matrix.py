#!/usr/bin/env python3
"""generate-ship-role-matrix.py — build the Ship x Role Matrix.

Projects the canonical 1-100 ratings in data/ship-ratings/*.json into a single
ships(rows) x roles(columns) matrix. Each cell carries the rating, a rating bar,
and (when a dossier exists) a deep link to guides/ships/ship-dossiers/<ship>-<role>.html.

Pad class (Small/Medium/Large) is sourced from data/ships/*.json `properties.class`
(1/2/3) and reconciled against PAD below for the newer hulls that the imported
coriolis-data set predates. Mismatches are printed as warnings.

Design (signed-off Concept A, refined):
  - Ship + Class columns (Class = centred DS pad pill), no rule between them
  - equal-width role columns, dim vertical separators, cells tinted by role colour
  - rating bars span 90% of the column; table body is non-bold (headers bold)
  - each header carries two compact glyph buttons:
      sort glyph  — cycles ⇅ (default) → ▲ asc → ▼ desc
      funnel glyph— opens a quick-nav-styled dropdown with that column's filter
        Ship  -> name search · Class -> pad toggles · Role -> minimum score
  - the header row sticks under the site-header while the table scrolls, then
    releases at the end of the table

Modes:
  --mockups   write the refined mockup to guides/ships/_mockup-matrix-a2.html
  --page      write the real page to guides/ships/general/ship-role-matrix.html
  (default)   print the matrix data-model summary
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RATINGS = ROOT / "data" / "ship-ratings"
SHIPS = ROOT / "data" / "ships"
OUT_DIR = ROOT / "guides" / "ships"

ROLES = [
    ("combat", "Combat"), ("ax", "AX"), ("mining", "Mining"), ("trading", "Trading"),
    ("exploration", "Exploration"), ("passenger", "Passenger"), ("multipurpose", "Multipurpose"),
]

# Pad class per hull — verified against the hand-checked dossiers (rule 1).
PAD = {
    "Small": [
        "Adder", "Cobra Mk III", "Cobra Mk IV", "Cobra Mk V", "Diamondback Explorer",
        "Diamondback Scout", "Dolphin", "Eagle Mk II", "Hauler", "Imperial Courier",
        "Imperial Eagle", "Kestrel Mk II", "Sidewinder Mk I", "Viper Mk III",
        "Viper Mk IV", "Vulture",
    ],
    "Medium": [
        "Alliance Challenger", "Alliance Chieftain", "Alliance Crusader", "Asp Explorer",
        "Asp Scout", "Corsair", "Federal Assault Ship", "Federal Dropship",
        "Federal Gunship", "Fer-de-Lance", "Keelback", "Krait Mk II", "Krait Phantom",
        "Lynx Highliner", "Mamba", "Mandalay", "Python",
        "Python Mk II", "Type-6 Transporter", "Type-8 Transporter", "Type-11 Prospector",
    ],
    "Large": [
        "Anaconda", "Beluga Liner", "Caspian Explorer", "Federal Corvette",
        "Imperial Clipper", "Imperial Cutter", "Orca", "Panther Clipper Mk II",
        "Type-7 Transporter", "Type-9 Heavy", "Type-10 Defender",
    ],
}
PAD_OF = {ship: pad for pad, ships in PAD.items() for ship in ships}
PAD_CLASS = {"Small": "pad-small", "Medium": "pad-medium", "Large": "pad-large"}


# Suitability >= CUTOFF warrants a dedicated dossier (rendered bright + linked, or
# as a >=CUTOFF "candidate" if not yet built); < CUTOFF is a poor fit shown greyed
# and unlinked. Exact cutoff — no fuzzy band.
CUTOFF = 40


def load_matrix():
    """Every ship x role cell, filled. Authored ratings (dossier-backed OR the few
    consistent dossier-less values) come from the canonical role JSONs; every
    remaining pair comes from the matrix-only overlay data/ship-ratings/matrix-extra.json
    (hand-authored, matrix-only — never fed to compute/reconcile or the ladders)."""
    data = {}
    for key, _ in ROLES:
        j = json.loads((RATINGS / f"{key}.json").read_text())
        for r in j["ratings"]:
            if r["ship"] == "Python (original)":
                continue  # legacy duplicate of Python (combat-only, no dossier)
            data.setdefault(r["ship"], {})[key] = {
                "rating": r["rating"], "dossier": r.get("dossier")
            }
    extra = json.loads((RATINGS / "matrix-extra.json").read_text())
    for key, ships in extra["ratings"].items():
        for ship, rating in ships.items():
            # only fill a cell the canonical files didn't already author
            data.setdefault(ship, {}).setdefault(key, {"rating": rating, "dossier": None})
    return data


def cross_check_pad():
    cls_to_pad = {1: "Small", 2: "Medium", 3: "Large"}
    by_name = {}
    for f in SHIPS.glob("*.json"):
        d = json.loads(f.read_text())
        for v in d.values():
            p = v.get("properties", {})
            if "name" in p and "class" in p:
                by_name[p["name"]] = cls_to_pad.get(p["class"])
    for ship, pad in PAD_OF.items():
        canon = by_name.get(ship)
        if canon and canon != pad:
            print(f"  ! PAD mismatch: {ship}: PAD={pad} vs data/ships class={canon}")


# ---------------------------------------------------------------------------
MATRIX_CSS = """
/* ===== Ship x Role Matrix ===== */
.mx-bar{display:flex;align-items:center;gap:.9rem;margin:0 0 .7rem}
.mx-bar .mx-count{font-size:.72rem;letter-spacing:.04em;color:var(--ink-dim);margin-left:auto}
.mx-reset{display:inline-flex;align-items:center;gap:.4em;background:var(--panel2);
  border:1px solid var(--hair-strong);border-radius:var(--radius-md);color:var(--ink-dim);
  font-family:'Chakra Petch',sans-serif;font-weight:600;font-size:.7rem;letter-spacing:.06em;
  text-transform:uppercase;padding:.34rem .7rem;cursor:pointer;
  transition:color .15s,border-color .15s,background .15s}
.mx-reset:hover{color:var(--amber-lt);border-color:var(--amber);background:var(--panel)}

.mx-wrap{position:relative}
@media(max-width:920px){.mx-wrap{overflow-x:auto;border:1px solid var(--hair);border-radius:var(--radius-md)}}
.matrix{border-collapse:separate;border-spacing:0;width:100%;table-layout:fixed;min-width:920px;font-size:.82rem}
.matrix col.col-ship{width:158px}
.matrix col.col-class{width:90px}

/* header row — sticky under the site-header */
.matrix thead th{position:sticky;top:62px;z-index:20;background:var(--bg);vertical-align:middle;
  padding:.5rem .3rem;border-bottom:1px solid var(--line,#2a241c);text-align:center;
  border-left:1px solid rgba(255,255,255,.05)}
.matrix thead th.col-ship{z-index:21;text-align:left;border-left:0}
.matrix thead th.mh-open{z-index:45}
.matrix thead th .mh{display:flex;flex-direction:row;align-items:center;justify-content:center;gap:.4rem}
.matrix thead th.col-ship .mh{justify-content:flex-start}
.mh-title{font-family:'Saira Condensed',sans-serif;font-weight:700;font-size:.64rem;letter-spacing:.04em;
  text-transform:uppercase;color:var(--ink-dim);white-space:nowrap}
.matrix thead th.r-combat .mh-title{color:var(--role-combat)}.matrix thead th.r-ax .mh-title{color:var(--role-ax)}
.matrix thead th.r-mining .mh-title{color:var(--role-mining)}.matrix thead th.r-trading .mh-title{color:var(--role-trading)}
.matrix thead th.r-exploration .mh-title{color:var(--role-exploration)}.matrix thead th.r-passenger .mh-title{color:var(--role-passenger)}
.matrix thead th.r-multipurpose .mh-title{color:var(--role-multipurpose)}
.mh-ctl{display:inline-flex;align-items:center;gap:0}
.mh-sort,.mh-filt{position:relative;display:inline-flex;align-items:center;justify-content:center;
  width:16px;height:18px;background:none;border:0;color:var(--ink-faint);cursor:pointer;border-radius:5px;
  transition:color .15s,background .15s}
.mh-sort:hover,.mh-filt:hover{color:var(--amber-lt);background:var(--panel2)}
.mh-sort .g{font-size:.82rem;line-height:1}
.matrix thead th.sorted .mh-sort{color:var(--amber)}
.mh-filt .ic{width:13px;height:13px;fill:none;stroke:currentColor;stroke-width:1.7;stroke-linejoin:round;stroke-linecap:round}
.mh-filt.on{color:var(--amber)}

/* funnel dropdown — quick-nav styled */
.mh-pop{position:absolute;top:calc(100% + 5px);left:50%;transform:translateX(-50%);min-width:178px;
  background:rgba(16,10,12,.99);border:1px solid var(--hair-strong);border-radius:var(--radius-lg);
  box-shadow:0 20px 56px rgba(0,0,0,.6);padding:.55rem;display:none;z-index:46;text-align:left}
.matrix thead th.mh-open .mh-pop{display:block}
.matrix thead th.col-ship .mh-pop{left:0;transform:none}
.matrix thead th.r-multipurpose .mh-pop,.matrix thead th.r-passenger .mh-pop{left:auto;right:0;transform:none}
.pop-h{font-family:'Saira Condensed',sans-serif;font-size:.62rem;letter-spacing:.09em;text-transform:uppercase;
  color:var(--ink-faint);margin:0 0 .45rem}
.mxf{position:relative;display:flex;align-items:center;background:var(--panel2);
  border:1px solid var(--hair-strong);border-radius:var(--radius-md);transition:border-color .15s}
.mxf:focus-within{border-color:var(--amber)}
.mxf .ico{position:absolute;left:8px;color:var(--ink-faint);font-size:.85rem;pointer-events:none}
.mxf input{background:transparent;border:0;outline:0;color:var(--ink);
  font-family:'Chakra Petch',sans-serif;font-weight:600;font-size:.74rem;letter-spacing:.3px;width:100%}
.mxf.search input{padding:.34rem .45rem .34rem 25px}
.mxf.min .lab{padding-left:9px;color:var(--ink-faint);font-size:.78rem;font-weight:700}
.mxf.min input{padding:.34rem .4rem;width:3.4em}
.mxf.min input::-webkit-outer-spin-button,.mxf.min input::-webkit-inner-spin-button{-webkit-appearance:none;margin:0}
.pop-presets{display:flex;gap:.34rem;margin-top:.5rem;flex-wrap:wrap}
.pop-presets button{background:var(--panel2);border:1px solid var(--hair-strong);border-radius:var(--radius-md);
  color:var(--ink-dim);font-family:'Chakra Petch',sans-serif;font-weight:600;font-size:.68rem;
  padding:.24rem .5rem;cursor:pointer;transition:color .15s,border-color .15s}
.pop-presets button:hover{color:var(--amber-lt);border-color:var(--amber)}
.mh-opt{display:flex;align-items:center;gap:.55rem;padding:.36rem .5rem;border-radius:var(--radius-md);
  cursor:pointer;color:var(--ink-faint);font-family:'Saira',sans-serif;font-size:.82rem}
.mh-opt:hover{background:var(--panel2);color:var(--ink)}
.mh-opt .dot{width:8px;height:8px;border-radius:50%;flex:none}
.mh-opt .dot.pad-small{background:var(--good-lt)}.mh-opt .dot.pad-medium{background:var(--amber-lt)}.mh-opt .dot.pad-large{background:var(--danger)}
.mh-opt .nm{flex:1}
.mh-opt .ck{color:var(--amber);opacity:0;font-size:.85rem}
.mh-opt.on{color:var(--ink)}
.mh-opt.on .ck{opacity:1}

/* body cells */
.matrix th.col-ship,.matrix td.col-ship{text-align:left;padding:.42rem .6rem;white-space:nowrap}
.matrix td.col-ship .shipname{color:var(--ink,#e9e2d4);font-weight:400}
.matrix th.col-class,.matrix td.col-class{text-align:center;padding:.42rem .5rem;white-space:nowrap;
  border-right:1px solid var(--line,#2a241c)}
.matrix td.col-class .pill{font-size:.6rem;padding:.1rem .5rem}
.matrix td.cell{text-align:center;padding:.3rem .25rem;border-bottom:1px solid rgba(255,255,255,.05);
  border-left:1px solid rgba(255,255,255,.05)}
.matrix tbody tr:hover td.col-ship,.matrix tbody tr:hover td.col-class,.matrix tbody tr:hover td.cell{
  box-shadow:inset 0 0 0 99px rgba(247,179,43,.05)}
/* hover highlights the WHOLE cell — amber border + fill (linked cells only) */
.matrix tbody tr:hover td.cell:not(.nd):hover{
  box-shadow:inset 0 0 0 1px var(--amber),inset 0 0 0 99px rgba(247,179,43,.13)}
.matrix td.cell a,.matrix td.cell span{display:block;color:inherit;text-decoration:none;padding:.16rem .15rem}
.matrix td.cell .rscore{display:block;font-weight:400;font-size:.82rem;line-height:1.1}
.matrix td.cell .bar.mini{height:5px;margin-top:3px;width:90%;margin-inline:auto}
/* no-dossier cells — Concept D: greyscale @30%, unlinked, "no dossier" tooltip */
.matrix td.cell.nd{filter:grayscale(1) opacity(.30)}
.matrix td.cell.nd span{cursor:default}
/* NOTE(candidate-ring · TEMPORARY): a no-dossier pair scored >=40 is a dossier
   CANDIDATE, flagged with a dashed amber ring so the build backlog is visible on
   the board. REMOVE the .cand ring (this rule + the " cand" class emitted in
   render_table) once the candidate dossiers are written. */
.matrix td.cell.nd.cand{outline:1px dashed var(--amber);outline-offset:-2px;filter:grayscale(.55) opacity(.62)}
.matrix td.cell.empty{color:var(--muted,#6b6256)}
.matrix td.cell.empty .dash{opacity:.35}

/* per-role column tint */
.r-combat{background:color-mix(in srgb,var(--role-combat) 12%,transparent)}
.r-ax{background:color-mix(in srgb,var(--role-ax) 12%,transparent)}
.r-mining{background:color-mix(in srgb,var(--role-mining) 12%,transparent)}
.r-trading{background:color-mix(in srgb,var(--role-trading) 12%,transparent)}
.r-exploration{background:color-mix(in srgb,var(--role-exploration) 12%,transparent)}
.r-passenger{background:color-mix(in srgb,var(--role-passenger) 12%,transparent)}
.r-multipurpose{background:color-mix(in srgb,var(--role-multipurpose) 12%,transparent)}
.matrix td.cell.empty.r-combat{background:color-mix(in srgb,var(--role-combat) 4%,transparent)}
.matrix td.cell.empty.r-ax{background:color-mix(in srgb,var(--role-ax) 4%,transparent)}
.matrix td.cell.empty.r-mining{background:color-mix(in srgb,var(--role-mining) 4%,transparent)}
.matrix td.cell.empty.r-trading{background:color-mix(in srgb,var(--role-trading) 4%,transparent)}
.matrix td.cell.empty.r-exploration{background:color-mix(in srgb,var(--role-exploration) 4%,transparent)}
.matrix td.cell.empty.r-passenger{background:color-mix(in srgb,var(--role-passenger) 4%,transparent)}
.matrix td.cell.empty.r-multipurpose{background:color-mix(in srgb,var(--role-multipurpose) 4%,transparent)}
/* header keeps a hairline of its role colour */
.matrix thead th.sorted{border-bottom-color:var(--amber)}
.hi-red{color:var(--danger);font-weight:700}
.hi-green{color:var(--good-lt);font-weight:700}
"""

MATRIX_JS = """
(function(){
  var tbl=document.getElementById('mx-table'); if(!tbl) return;
  var tbody=tbl.tBodies[0];
  var rows=[].slice.call(tbody.rows);
  var rank={Small:0,Medium:1,Large:2};
  function toTop(){var y=tbl.getBoundingClientRect().top+window.pageYOffset-70;
    window.scrollTo({top:y,behavior:'smooth'});}
  var pads={Small:true,Medium:true,Large:true};
  var sortKey=null, sortDir=1;             // null => default (ship asc)
  var search=document.getElementById('mx-search');
  var countEl=document.getElementById('mx-count');
  var mins={};
  [].forEach.call(tbl.querySelectorAll('.mxf.min input'),function(i){mins[i.getAttribute('data-role')]=i;});

  function rt(r,role){var v=r.getAttribute('data-r-'+role);return (v===null||v==='')?null:+v;}
  function eff(){return {k:sortKey||'ship', d:sortKey?sortDir:1};}
  function apply(){
    var q=(search.value||'').trim().toLowerCase(), e=eff();
    var vis=rows.filter(function(r){
      if(!pads[r.getAttribute('data-pad')]) return false;
      if(q && r.getAttribute('data-ship').toLowerCase().indexOf(q)<0) return false;
      for(var role in mins){var mn=parseInt(mins[role].value,10)||0; if(mn>0){var v=rt(r,role);
        if(v===null||v<mn) return false;}}
      return true;
    });
    vis.sort(function(a,b){
      var byName=a.getAttribute('data-ship').localeCompare(b.getAttribute('data-ship'));
      if(e.k==='ship') return e.d*byName;
      if(e.k==='pad'){var d=rank[a.getAttribute('data-pad')]-rank[b.getAttribute('data-pad')];return (d*e.d)||byName;}
      var x=rt(a,e.k),y=rt(b,e.k);
      if(x===null&&y===null) return byName;
      if(x===null) return 1; if(y===null) return -1;
      return ((x-y)*e.d)||byName;
    });
    vis.forEach(function(r){tbody.appendChild(r);});
    rows.forEach(function(r){r.style.display=vis.indexOf(r)<0?'none':'';});
    countEl.textContent=vis.length+' / '+rows.length+' ships';
    indicators();
  }
  function indicators(){
    var e=eff();
    [].forEach.call(tbl.querySelectorAll('thead th[data-sortkey]'),function(th){
      var k=th.getAttribute('data-sortkey'), on=(e.k===k);
      th.classList.toggle('sorted',on);
      var g=th.querySelector('.mh-sort .g'); if(g) g.textContent=on?(e.d>0?'▲':'▼'):'⇅';
      var f=th.querySelector('.mh-filt'); if(!f) return;
      var active=false;
      if(k==='ship') active=q0();
      else if(k==='pad') active=!(pads.Small&&pads.Medium&&pads.Large);
      else active=(parseInt((mins[k]||{}).value,10)||0)>0;
      f.classList.toggle('on',active);
    });
  }
  function q0(){return (search.value||'').trim()!=='';}

  // sorting (tri-state cycle: ⇅ -> ▲ -> ▼ -> ⇅)
  [].forEach.call(tbl.querySelectorAll('.mh-sort'),function(btn){
    btn.addEventListener('click',function(ev){ev.stopPropagation();
      var k=btn.closest('th').getAttribute('data-sortkey'), e=eff();
      if(e.k!==k){sortKey=k;sortDir=1;} else if(e.d===1){sortKey=k;sortDir=-1;} else {sortKey=null;sortDir=1;}
      apply();toTop();});
  });
  // funnel popovers
  function closeAll(except){[].forEach.call(tbl.querySelectorAll('thead th.mh-open'),function(th){
    if(th!==except) th.classList.remove('mh-open');});}
  [].forEach.call(tbl.querySelectorAll('.mh-filt'),function(btn){
    btn.addEventListener('click',function(ev){ev.stopPropagation();
      var th=btn.closest('th'); var open=th.classList.contains('mh-open');
      closeAll(); if(!open) th.classList.add('mh-open');});
  });
  [].forEach.call(tbl.querySelectorAll('.mh-pop'),function(p){
    p.addEventListener('click',function(ev){ev.stopPropagation();});});
  document.addEventListener('click',function(){closeAll();});
  document.addEventListener('keydown',function(ev){if(ev.key==='Escape')closeAll();});

  // filters
  search.addEventListener('input',apply);
  for(var role in mins) mins[role].addEventListener('input',apply);
  [].forEach.call(tbl.querySelectorAll('.pop-presets button'),function(b){
    b.addEventListener('click',function(){var inp=b.closest('.mh-pop').querySelector('input');
      inp.value=b.getAttribute('data-v'); apply();toTop();});});
  [].forEach.call(tbl.querySelectorAll('.mh-opt'),function(o){
    o.addEventListener('click',function(){var p=o.getAttribute('data-pad');
      pads[p]=!pads[p]; o.classList.toggle('on',pads[p]); apply();toTop();});});

  document.getElementById('mx-reset').addEventListener('click',function(){
    search.value=''; sortKey=null; sortDir=1; pads={Small:true,Medium:true,Large:true};
    for(var role in mins) mins[role].value='0';
    [].forEach.call(tbl.querySelectorAll('.mh-opt'),function(o){o.classList.add('on');});
    closeAll(); apply();
  });
  apply();
})();
"""

FUNNEL_SVG = ('<svg class="ic" viewBox="0 0 24 24" aria-hidden="true">'
              '<path d="M4 5 H20 L14 12 V18 L10 20 V12 Z"/></svg>')


def glyphs(label):
    return ('<span class="mh-ctl">'
            f'<button type="button" class="mh-sort" title="Sort by {label}"><span class="g">⇅</span></button>'
            f'<button type="button" class="mh-filt" title="Filter {label}">{FUNNEL_SVG}</button>'
            '</span>')


def header_html():
    ship = ('<th class="col-ship" data-sortkey="ship">'
            f'<div class="mh"><span class="mh-title">Ship</span>{glyphs("Ship")}</div>'
            '<div class="mh-pop"><p class="pop-h">Filter ships</p>'
            '<div class="mxf search"><span class="ico">⌕</span>'
            '<input type="text" id="mx-search" placeholder="Name…" autocomplete="off"></div></div></th>')
    klass = ('<th class="col-class" data-sortkey="pad">'
             f'<div class="mh"><span class="mh-title">Class</span>{glyphs("Class")}</div>'
             '<div class="mh-pop"><p class="pop-h">Pad class</p>'
             + "".join(
                 f'<div class="mh-opt on" data-pad="{p}"><span class="dot {PAD_CLASS[p]}"></span>'
                 f'<span class="nm">{p}</span><span class="ck">✓</span></div>'
                 for p in ("Small", "Medium", "Large"))
             + '</div></th>')
    roles = []
    for key, label in ROLES:
        roles.append(
            f'<th class="rolehd r-{key}" data-sortkey="{key}">'
            f'<div class="mh"><span class="mh-title">{label}</span>{glyphs(label)}</div>'
            f'<div class="mh-pop"><p class="pop-h">Minimum {label}</p>'
            f'<div class="mxf min"><span class="lab">≥</span>'
            f'<input type="number" min="0" max="100" value="0" data-role="{key}" '
            f'aria-label="Minimum {label} rating"></div>'
            f'<div class="pop-presets"><button type="button" data-v="70">70+</button>'
            f'<button type="button" data-v="80">80+</button>'
            f'<button type="button" data-v="90">90+</button>'
            f'<button type="button" data-v="0">Any</button></div></div></th>')
    return "<tr>" + ship + klass + "".join(roles) + "</tr>"


def render_table(data, dossier_dir="../ship-dossiers/"):
    ships = sorted(data.keys(), key=lambda s: s.lower())
    cols = '<col class="col-ship"><col class="col-class">' + '<col>' * len(ROLES)
    rows = []
    for s in ships:
        pad = PAD_OF.get(s, "Medium")
        padcls = PAD_CLASS.get(pad, "")
        attrs = [f'data-ship="{s}"', f'data-pad="{pad}"']
        cells = [
            # nolink: the Ship column is never hyperlinked (apply-hyperlinks skips it)
            f'<td class="col-ship nolink"><span class="shipname">{s}</span></td>',
            f'<td class="col-class"><span class="pill {padcls}">{pad}</span></td>',
        ]
        for key, label in ROLES:
            c = data[s][key]
            rating = c["rating"]
            attrs.append(f'data-r-{key}="{rating}"')
            inner = (f'<span class="rscore">{rating}</span>'
                     f'<div class="bar mini"><i style="--pct:{rating}"></i></div>')
            if c["dossier"]:
                inner = f'<a href="{dossier_dir}{c["dossier"]}" title="{s} · {label}">{inner}</a>'
                cells.append(f'<td class="cell r-{key}">{inner}</td>')
            else:
                # no dossier: Concept-D greyed + unlinked; a >=CUTOFF score is a
                # dossier CANDIDATE (dashed-ring — a temporary build-tracker, see CSS)
                cand = rating >= CUTOFF
                klass = "cell nd" + (" cand" if cand else "")
                tip = (f"{s} · {label} — no dossier"
                       + (" · candidate (score ≥40)" if cand else ""))
                inner = f'<span title="{tip}">{inner}</span>'
                cells.append(f'<td class="{klass} r-{key}">{inner}</td>')
        rows.append(f'<tr {" ".join(attrs)}>' + "".join(cells) + "</tr>")

    bar = ('<div class="mx-bar"><span class="mx-count" id="mx-count"></span>'
           '<button type="button" id="mx-reset" class="mx-reset">↺ Reset</button></div>')
    table = (f'<div class="mx-wrap"><table class="matrix" id="mx-table">'
             f'<colgroup>{cols}</colgroup>'
             f'<thead>{header_html()}</thead>'
             f'<tbody>{"".join(rows)}</tbody></table></div>')
    desc = (f'<p class="tbl-desc"><b>Ship × Role suitability matrix</b> — '
            f'each cell is the hull\'s 1–100 score for that role; the bar runs '
            f'<span class="hi-red">red</span> (high) → <span class="hi-green">green</span> (low). '
            f'<b>Bright, linked</b> cells open a dossier; <b>greyed</b> cells are a '
            f'sub-40 poor fit with no dossier (hover for the tooltip). Use each '
            f'column\'s sort and filter glyphs to reorder and narrow the grid. '
            f'{len(ships)} ships × {len(ROLES)} roles.</p>')
    return bar + table + desc


def page_shell(body, n_ships, mockup=True):
    banner = ""
    if mockup:
        banner = """  <div class="verdict"><div class="v-body">
    <div class="v-eyebrow">Concept Mockup · A (refined)</div>
    <h2>Ship × Role suitability — the whole roster on one grid</h2>
    <p>Each column header carries a sort glyph (⇅ → ▲ → ▼) and a funnel that opens a quick-nav-styled filter — name search on Ship, pad toggles on Class, minimum score on each role. The header row stays pinned while you scroll the grid. Try it live.</p>
  </div></div>
"""
    kicker = "MOCKUP <span class=\"sep\">//</span> Concept A refined" if mockup else "Ships <span class=\"sep\">//</span> Reference"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ship × Role Matrix | E:D Black Box</title>
<link rel="icon" type="image/png" href="../../images/logos/favicon.png">
<link rel="stylesheet" href="../../design-system/css/ed-blackbox.css">
<style>{MATRIX_CSS}</style>
</head>
<body>
<header class="site-header"><div class="hdr-inner">
  <a class="brand" href="../index.html" aria-label="E:D Black Box — home">
    <img src="../../images/logos/logo.png" alt=""><span class="wordmark"><span class="hl">E:D</span> Black Box</span>
  </a>
  <span class="nav-sep" aria-hidden="true"></span>
  <nav class="site-nav" aria-label="Primary">
    <a href="../index.html">Home</a>
    <a href="../index.html#section-dossiers" class="active">Ships</a>
    <a href="../index.html#section-engineering">Engineering</a>
    <a href="../index.html#section-systems">Systems</a>
  </nav>
</div></header>
<nav class="breadcrumbs" aria-label="Breadcrumb">
  <a href="../index.html">Home</a><span class="sep">›</span>
  <a href="../index.html#section-dossiers">Ships</a><span class="sep">›</span>
  <span class="current" aria-current="page">Ship × Role Matrix</span>
</nav>
<div class="wrap">
  <header class="masthead">
    <div class="kicker">{kicker}</div>
    <h1 class="title">Ship × Role <span>Matrix</span></h1>
    <div class="masthead-meta"><span>Series <b>Ships</b></span><span>Updated <b>2026-06-25</b></span></div>
  </header>
{banner}  <section id="section-matrix">
    <div class="sec-head"><span class="sec-num">02</span><h2>The Matrix</h2><span class="tag">{n_ships} ships · 7 roles</span></div>
    {body}
  </section>
</div>
<script src="../../design-system/js/ed-blackbox.js" defer></script>
<script>{MATRIX_JS}</script>
</body>
</html>
"""


SITE_HEADER = """<header class="site-header">
  <div class="hdr-inner">
    <a class="brand" href="../../index.html" aria-label="E:D Black Box — home">
      <img src="../../../images/logos/logo.png" alt="">
      <span class="wordmark"><span class="hl">E:D</span> Black Box</span>
    </a>
    <span class="nav-sep" aria-hidden="true"></span>
    <nav class="site-nav" aria-label="Primary">
      <a href="../../index.html">Home</a>
      <a href="../../index.html#section-dossiers" class="active">Ships</a>
      <a href="../../index.html#section-engineering">Engineering</a>
      <a href="../../index.html#section-systems">Systems</a>
    </nav>
    <div class="header-qn">
      <div class="hdr-crumb">
        <span class="hdr-crumb-title">Ship × Role Matrix</span>
        <span class="hdr-crumb-trail">
          <a href="../../index.html#section-dossiers">Ships</a>
          <span class="sep">›</span>
          <a href="../../index.html#section-general">General</a>
        </span>
      </div>
      <button class="qn-totop" type="button" aria-label="Scroll to top" title="Scroll to top">
        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M4 13 L12 6 L20 13"/><path d="M4 18.5 L12 11.5 L20 18.5"/></svg>
      </button>
      <div class="qn-dd" id="qn-dd">
        <div class="qn-field">
          <span class="qn-ico" aria-hidden="true">⌕</span>
          <input id="qn-search" class="qn-input" type="text" placeholder="Jump to a section…" autocomplete="off" spellcheck="false" role="combobox" aria-expanded="false" aria-controls="qn-panel" aria-autocomplete="list">
          <button id="qn-clear" class="qn-clear" type="button" aria-label="Clear search" hidden>×</button>
        </div>
        <div class="qn-panel" id="qn-panel" role="listbox">
          <a class="qn-item" href="#section-reading-the-grid"><span class="qn-dot amber"></span><span class="qn-nm">Reading the Grid</span><span class="qn-side">01</span></a>
          <a class="qn-item" href="#section-matrix"><span class="qn-dot amber"></span><span class="qn-nm">The Matrix</span><span class="qn-side">02</span></a>
          <a class="qn-item" href="#section-what-the-grid-reveals"><span class="qn-dot amber"></span><span class="qn-nm">What the Grid Reveals</span><span class="qn-side">03</span></a>
          <div class="qn-empty" hidden>No matching sections</div>
        </div>
      </div>
    </div>
  </div>
</header>"""


def build_page(data, date="2026-07-01"):
    n_ships = len(data)
    n_cells = sum(len(v) for v in data.values())
    n_dossier = sum(1 for v in data.values() for c in v.values() if c["dossier"])
    n_cand = sum(1 for v in data.values() for c in v.values()
                 if not c["dossier"] and c["rating"] >= CUTOFF)
    n_poor = n_cells - n_dossier - n_cand
    matrix = render_table(data)

    intro = f"""  <section id="section-reading-the-grid">
    <div class="sec-head"><span class="sec-num">01</span><h2>Reading the Grid</h2><span class="tag">Orientation</span></div>
    <p class="lead">One board for the whole fleet: <b>{n_ships} hulls</b> down the side, <b>seven roles</b> across the top, and in every cell the ship's <b>1&ndash;100 suitability</b> for that job &mdash; all <b>{n_cells}</b> pairings, none left blank. A <b>bright, linked</b> cell opens that pairing's dossier; a <b>greyed</b> cell is a sub-40 poor fit with no dossier.</p>
    <div class="cards four">
      <div class="card"><span class="ico">Rows × cols</span><h4>Every hull × role</h4><p>All {n_ships} hulls scored against all seven job columns &mdash; the complete {n_cells}-cell board.</p></div>
      <div class="card"><span class="ico">1&ndash;100</span><h4>The score</h4><p>A roster-relative, fully-engineered suitability <a href="rating-methodology.html">rating</a> &mdash; higher is a better fit for that role.</p></div>
      <div class="card"><span class="ico">Bar</span><h4>At a glance</h4><p>The bar runs <span class="hi-red">red</span> (high) to <span class="hi-green">green</span> (low), so a column reads as a ladder without parsing numbers.</p></div>
      <div class="card"><span class="ico">Class</span><h4>Landing pad</h4><p>The Class column is the hull's pad size &mdash; <b>Small</b>, <b>Medium</b> or <b>Large</b> &mdash; the first filter on any buy.</p></div>
    </div>

    <h3 class="subhead">Bright is documented, grey is a poor fit</h3>
    <p>Of the <b>{n_cells}</b> pairings, <b>{n_dossier}</b> carry a published dossier &mdash; the <b>bright, linked</b> cells. The <b>greyed</b> cells score <b>below&nbsp;40</b>: the hull is a poor fit for that role, so there is no dedicated write-up (hover a cell for its &ldquo;no dossier&rdquo; note). A greyed number is a coarse &ldquo;don't bother&rdquo; signal, not a full verdict &mdash; use the bright cells to compare what's documented.</p>
    <div class="callout"><span class="lbl">Drive it from the headers</span><p>Every column title carries a <b>sort</b> glyph (⇅&nbsp;→&nbsp;▲&nbsp;→&nbsp;▼) and a <b>funnel</b>. Sort by any role to rank the field; search a hull by name; gate the table by pad class; or set a minimum score on one or more roles &mdash; the role minimums <b>stack</b>, so &ldquo;Combat&nbsp;≥&nbsp;85 and Trading&nbsp;≥&nbsp;70&rdquo; finds the hulls that do both.</p></div>
  </section>"""

    # Each champion's "Top hull" links to the dossier for THAT role (column A) —
    # sourced from the matrix data so it can never drift to the hull's default role.
    label_to_key = {label: key for key, label in ROLES}
    champions = [
        ("Combat", "Federal Corvette", 98), ("AX", "Alliance Chieftain", 90),
        ("Mining", "Type-11 Prospector", 95), ("Trading", "Panther Clipper Mk II", 98),
        ("Exploration", "Mandalay", 96), ("Passenger", "Beluga Liner", 95),
        ("Multipurpose", "Anaconda", 88),
    ]
    champ_parts = []
    for lbl, ship, rat in champions:
        cell = data.get(ship, {}).get(label_to_key[lbl])
        hull = (f'<b><a href="../ship-dossiers/{cell["dossier"]}">{ship}</a></b>'
                if cell and cell.get("dossier") else f'<b>{ship}</b>')
        champ_parts.append(
            f'<tr><td class="mod">{lbl}</td><td>{hull}</td>'
            f'<td><span class="rscore">{rat}</span><div class="bar mini"><i style="--pct:{rat}"></i></div></td></tr>')
    champ_rows = "".join(champ_parts)

    concl = f"""  <section id="section-what-the-grid-reveals">
    <div class="sec-head"><span class="sec-num">03</span><h2>What the Grid Reveals</h2><span class="tag">Patterns</span></div>
    <p class="lead">Read down the columns and a few truths fall out of the board &mdash; about who can do everything, who owns each role, and how little a landing pad actually decides.</p>

    <div class="cards two nolink">
      <div class="card">
        <div class="c-head"><h3>The true generalists</h3><span class="c-eyebrow">70+ in all 7</span></div>
        <p>Only two hulls <b>clear 70 in every single role</b>: the <b>Anaconda</b> and the <b>Python</b>. The Anaconda never drops below <b>76</b> (trading) and peaks at <b>94</b> (exploration) &mdash; the definitive do-everything, at a Large-pad price and a Large-pad bankroll. The Python repeats the trick on a <b>Medium</b> pad for a fraction of the cost: the working commander's one-ship answer.</p>
      </div>
      <div class="card">
        <div class="c-head"><h3>Pad size isn't destiny</h3><span class="c-eyebrow">Medium punches up</span></div>
        <p>The top of <b>exploration</b> (Mandalay, 96) and <b>mining</b> (Type-11 Prospector, 95) is <b>Medium</b>-pad, and the <b>Fer-de-Lance</b> (93) is the second-best gun in the game on a Medium hull. Large pads own only the <b>bulk</b> jobs &mdash; trading and luxury passenger. You do not need outpost-locking size to reach the top of most roles.</p>
      </div>
    </div>

    <h3 class="subhead">Role champions</h3>
    <p>The highest published verdict in each column &mdash; the hull to beat for that job.</p>
    <div class="tbl-scroll">
      <table class="data">
        <colgroup><col style="width:34%"><col style="width:42%"><col style="width:24%"></colgroup>
        <thead><tr><th>Role</th><th>Top hull</th><th>Rating</th></tr></thead>
        <tbody>{champ_rows}</tbody>
      </table>
    </div>
    <p class="tbl-desc"><b>Apex per role</b> &mdash; AX is a tie at 90 (Alliance Chieftain shown; Imperial Cutter matches it).</p>

    <div class="callout"><span class="lbl">Specialists buy a podium</span><p>Specialist hulls trade breadth for a peak: the <b>Fer-de-Lance</b> (combat&nbsp;93), <b>Caspian Explorer</b> (exploration&nbsp;94), <b>Type-11 Prospector</b> (mining&nbsp;95) and <b>Lynx Highliner</b> (passenger&nbsp;90) each carry a published dossier in <b>one</b> role and dominate it. The <b>grey cells</b> down the rest of their row are the price &mdash; pick a specialist when you fly one job, a generalist when you fly all of them.</p></div>
  </section>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ship &times; Role Matrix &middot; Ship Ratings | E:D Black Box</title>
<link rel="icon" type="image/png" href="../../../images/logos/favicon.png">
<link rel="stylesheet" href="../../../design-system/css/ed-blackbox.css">
<!-- Deliberately-scoped bespoke block: the Ship × Role Matrix interactive table
     (like checklist.html's Unlock Map and index.html's grids). Not page chrome,
     not the accent override. Generated by scripts/generate-ship-role-matrix.py. -->
<style>{MATRIX_CSS}</style>
</head>
<body>
{SITE_HEADER}

<div class="wrap">

  <header class="masthead">
    <div class="kicker">Ship Ratings <span class="sep">//</span> Ship × Role Matrix</div>
    <h1 class="title">Ship × Role <span>Matrix</span> <span class="role">Reference</span></h1>
    <div class="masthead-meta">
      <span>Series <b>Ships</b></span>
      <span>Updated <b>{date}</b></span>
    </div>
  </header>

  <div class="verdict">
    <div class="v-eyebrow">Field Briefing</div>
    <h2>Every ship&times;role verdict, on one <em>sortable</em> grid.</h2>
    <p>The matrix puts all <b>{n_cells} pairings</b> on a single board &mdash; <b>{n_ships} hulls</b> against <b>seven roles</b>, each cell the hull's 1&ndash;100 suitability for that job. <b>{n_dossier}</b> are documented and linked straight to the write-up; the rest are scored but sub-40. It is the fastest way to ask &ldquo;what's the best ship for X?&rdquo; or &ldquo;what else is this hull good at?&rdquo; without opening fifty pages.</p>
    <div class="why">
      <div><h4>Rows are hulls</h4><p>Columns are the seven roles; the Class column is the landing pad.</p></div>
      <div><h4>Cells are verdicts</h4><p>The same roster-relative, engineered 1&ndash;100 score each dossier carries.</p></div>
      <div><h4>Grey is a poor fit</h4><p>A greyed, unlinked cell scored below 40 &mdash; no dossier, a hull to skip for that job.</p></div>
    </div>
  </div>

{intro}

  <section id="section-matrix">
    <div class="sec-head"><span class="sec-num">02</span><h2>The Matrix</h2><span class="tag">{n_ships} ships · 7 roles</span></div>
    <p class="lead">The whole board. Sort by any role, filter by pad class or minimum score, and click a cell to open its dossier.</p>
    {matrix}
  </section>

{concl}

  <footer>
    <div class="ft-fine">
      <span>&copy; 2026 Elite:Dangerous Black Box &middot; CMDR Ka0s &middot; Ships &middot; <a href="https://github.com/tusharsaxena/ed-blackbox/issues">Report an issue</a></span>
      <span>Elite Dangerous is a trademark of Frontier Developments plc. Unofficial fan content &mdash; not affiliated with or endorsed by Frontier Developments.</span>
    </div>
  </footer>

</div>

<script src="../../../design-system/js/ed-blackbox.js" defer></script>
<script>{MATRIX_JS}</script>
</body>
</html>
"""


def main():
    data = load_matrix()
    n_cells = sum(len(v) for v in data.values())
    n_doss = sum(1 for v in data.values() for c in v.values() if c["dossier"])
    n_cand = sum(1 for v in data.values() for c in v.values()
                 if not c["dossier"] and c["rating"] >= CUTOFF)
    print(f"Loaded {len(data)} ships, {n_cells} cells across {len(ROLES)} roles "
          f"({n_doss} dossier · {n_cand} candidates >=40 · {n_cells-n_doss-n_cand} greyed <40).")
    cross_check_pad()
    if "--mockups" in sys.argv:
        out = OUT_DIR / "_mockup-matrix-a3.html"
        out.write_text(page_shell(render_table(data, "ship-dossiers/"), len(data), mockup=True))
        print(f"  wrote {out.relative_to(ROOT)}")
    if "--page" in sys.argv:
        out = OUT_DIR / "general" / "ship-role-matrix.html"
        out.write_text(build_page(data))
        print(f"  wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
