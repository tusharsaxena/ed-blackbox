/*! ed-blackbox — mobile sticky table headers (standalone)
   Markup-independent and null-safe, like analytics.js: it can load on EVERY page,
   including the engineering pages that can't take ed-blackbox.js (their inline
   quick-nav would double-bind). This is the same behaviour as ed-blackbox.js
   module 6 (sticky-tables) — kept as a separate file so no-ed-blackbox.js pages
   (e.g. modules.html, with 86 spec tables) still get it. A dedup guard means a
   page that somehow loads both never builds duplicate clones.

   What it does: on narrow viewports the scroll wrapper (.tbl-scroll / .mx-wrap) is
   an overflow-x container, which forces overflow-y:auto and traps position:sticky
   (so the native pinned header can't work — and the mobile site-header is taller
   than the desktop 62px). For each such table it builds a fixed .sthc clone of the
   <thead>, pins it just under the site-header while the table is in view, and
   translates it by -scrollLeft so the columns track the table's horizontal scroll.
   Desktop is untouched (native CSS sticky). Presentational only (aria-hidden,
   pointer-events:none) — the real header stays interactive.

   Scales to many tables: an IntersectionObserver keeps only the tables near the
   viewport "active", so a page with dozens of tables only measures the 1–2 on
   screen per scroll frame. Load once, deferred:
     <script src=".../design-system/js/sticky-tables.js" defer></script>
*/
(function(){
  if(window.__edbbSticky) return; window.__edbbSticky=1;
  if(!window.matchMedia||!window.requestAnimationFrame||!('IntersectionObserver' in window)) return;

  var mq=window.matchMedia('(max-width:920px)');
  var header=document.querySelector('.site-header');
  function pinLine(){ return header ? Math.max(0, header.getBoundingClientRect().bottom) : 0; }

  // One entry per sticky table. Two shapes:
  //  - a horizontal-scroll wrapper (.tbl-scroll/.mx-wrap): geometry (left/width/scrollLeft)
  //    comes from the WRAPPER, so the clone tracks the table's horizontal scroll.
  //  - a stand-alone .bp-table (no wrapper, width:100%, no h-scroll): geometry comes from the
  //    TABLE itself (scrollLeft is always 0).
  var entries=[], seen=[];
  function addEntry(geom, table){
    var thead=table&&table.tHead;
    if(!thead || seen.indexOf(table)>-1) return;
    seen.push(table);
    var e={geom:geom,table:table,thead:thead,clone:null,ct:null,shown:false};
    geom.addEventListener('scroll',function(){
      if(e.shown&&e.ct) e.ct.style.transform='translateX('+(-geom.scrollLeft)+'px)';
    },{passive:true});
    geom.__sthEntry=e;
    entries.push(e);
  }
  [].slice.call(document.querySelectorAll('.tbl-scroll, .mx-wrap')).forEach(function(s){ addEntry(s, s.querySelector('table')); });
  [].slice.call(document.querySelectorAll('.bp-table')).forEach(function(t){ if(!t.closest('.tbl-scroll, .mx-wrap')) addEntry(t, t); });
  if(!entries.length) return;

  function build(e){
    var clone=document.createElement('div');
    clone.className='sthc'; clone.setAttribute('aria-hidden','true');
    var ct=document.createElement('table');
    ct.className=e.table.className;
    var cg=e.table.querySelector('colgroup');
    if(cg) ct.appendChild(cg.cloneNode(true));
    ct.appendChild(e.thead.cloneNode(true));
    clone.appendChild(ct);
    document.body.appendChild(clone);
    e.clone=clone; e.ct=ct;
  }
  function place(e){
    if(!mq.matches){ if(e.shown){e.clone.style.display='none';e.shown=false;} return; }
    var pin=pinLine(),
        hr=e.thead.getBoundingClientRect(),
        tr=e.table.getBoundingClientRect(),
        sr=e.geom.getBoundingClientRect();
    // pin zone: the real header has scrolled above the pin line, but the table still spans it
    if(hr.top<pin && tr.bottom>pin+hr.height){
      if(!e.clone) build(e);
      e.clone.style.display='block';
      e.clone.style.top=pin+'px';
      e.clone.style.left=sr.left+'px';
      e.clone.style.width=e.geom.clientWidth+'px';
      e.clone.style.height=hr.height+'px';
      e.ct.style.width=e.table.offsetWidth+'px';
      e.ct.style.tableLayout='fixed';
      var a=e.thead.querySelectorAll('th'), b=e.ct.querySelectorAll('thead th');
      for(var i=0;i<a.length;i++){ if(b[i]) b[i].style.width=a[i].getBoundingClientRect().width+'px'; }
      e.ct.style.transform='translateX('+(-e.geom.scrollLeft)+'px)';
      e.shown=true;
    }else if(e.shown){
      e.clone.style.display='none'; e.shown=false;
    }
  }

  // only tables near the viewport are "active" and get measured on scroll
  var active=[], raf=0;
  function tick(){ raf=0; for(var i=0;i<active.length;i++) place(active[i]); }
  function schedule(){ if(!raf) raf=requestAnimationFrame(tick); }

  var io=new IntersectionObserver(function(list){
    list.forEach(function(en){
      var e=en.target.__sthEntry, idx=active.indexOf(e);
      if(en.isIntersecting){ if(idx<0) active.push(e); }
      else{ if(idx>=0) active.splice(idx,1); if(e.shown&&e.clone){e.clone.style.display='none';e.shown=false;} }
    });
    schedule();
  },{rootMargin:'250px 0px 250px 0px'});
  entries.forEach(function(e){ io.observe(e.geom); });

  window.addEventListener('scroll',schedule,{passive:true});
  window.addEventListener('resize',schedule);
  (mq.addEventListener?mq.addEventListener.bind(mq,'change'):mq.addListener.bind(mq))(schedule);
  schedule();
})();
