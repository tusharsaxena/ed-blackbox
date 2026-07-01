/*! ed-blackbox — page scroll-progress indicator
   A thin amber hairline pinned to the bottom edge of the site-header that fills left→right
   as the reader scrolls the page. Single source of truth for the indicator. Loaded once per
   page via <script src=".../design-system/js/scroll-progress.js" defer>.

   Self-contained and markup-independent — like analytics.js it injects its own element and
   styles and never touches existing page behaviour, so it is safe on every page, INCLUDING
   the four engineering-manual pages that ship their own inline quick-nav and cannot load
   ed-blackbox.js. Styling uses the design-system CSS tokens (--maroon/--amber/--amber-lt,
   present on every page via ed-blackbox.css) with hard fallbacks.

   WHY IT'S BUILT THIS WAY (earlier attempts flickered on load — a thick line that thinned to
   crisp only after a scroll). Root causes, now all removed:
     1. The glow. A box-shadow renders as a fuzzy band during progressive paint, and the
        page's background grid shows through it — reading as a thick, textured line. FIX: no
        box-shadow at all; the bar is a crisp solid gradient.
     2. The fill technique. transform:scaleX() scales the whole element including its
        gradient, so a short bar showed mostly the dark maroon end (looked like a dark thick
        band). FIX: fill with width% over a viewport-anchored gradient (background-size:100vw)
        — the colour is identical at any width; the bar just reveals more of it.
     3. Sub-pixel position. The bar sits at top = header height. On a fractional-DPR display
        (Windows/WSL at 125/150%) that CSS height maps to a *fractional device pixel*, so a
        2px line straddled a device-pixel boundary and rendered 3px thick until a scroll
        snapped it. FIX: snap `top` to the nearest whole device pixel —
        Math.round(h*dpr)/dpr — so the top edge always lands on a device-pixel boundary.
        (Recomputed on resize/zoom, which is when DPR or the header height can change.)

   Perf: width writes on a 2px element are trivial; updates are requestAnimationFrame-
   throttled on a passive scroll listener. No transition (a scroll-driven bar must track the
   scroll exactly), so nothing for prefers-reduced-motion to disable. A ResizeObserver on
   <body> keeps the fill correct as the document height settles during load. To restyle or
   disable, edit this file and nowhere else. */
(function(){
  if(document.getElementById('edbb-scroll-progress')) return;   // never double-inject

  // --- inject the bar: no glow, viewport-anchored gradient, filled by width --------------
  var bar=document.createElement('div');
  bar.id='edbb-scroll-progress';
  bar.setAttribute('aria-hidden','true');   // decorative chrome — not announced
  bar.style.cssText=[
    'position:fixed','top:0','left:0','width:0','height:2px',
    'z-index:40',   // --z-sticky: above page content, below the --z-nav:50 site-header
    'pointer-events:none',
    'background:linear-gradient(90deg,var(--maroon,#8b2332),var(--amber,#e0913a) 55%,var(--amber-lt,#f4b15f))',
    'background-size:100vw 100%','background-repeat:no-repeat','background-position:left center',
    'will-change:width'
  ].join(';');
  (document.body||document.documentElement).appendChild(bar);

  // --- position under the (sticky) site-header, snapped to a whole device pixel ----------
  var header=document.querySelector('.site-header'), lastTop=-1;
  function place(){
    if(!header) return;   // no header → leave it at top:0
    var dpr=window.devicePixelRatio||1;
    var t=Math.round(header.getBoundingClientRect().height*dpr)/dpr;
    if(t!==lastTop){ lastTop=t; bar.style.top=t+'px'; }
  }

  // --- fraction scrolled (0..1) ----------------------------------------------
  function frac(){
    var d=document.documentElement, b=document.body;
    var st=window.pageYOffset||d.scrollTop||b.scrollTop||0;
    var max=(d.scrollHeight||b.scrollHeight)-d.clientHeight;
    return max<=0?0:Math.min(1,Math.max(0,st/max));
  }

  var pending=false;
  function render(){ pending=false; place(); bar.style.width=(frac()*100)+'%'; }
  function schedule(){ if(!pending){ pending=true; requestAnimationFrame(render); } }

  window.addEventListener('scroll',schedule,{passive:true});
  window.addEventListener('resize',schedule);   // catches zoom / DPR changes → re-snaps top
  window.addEventListener('load',schedule);
  // The document height (and the header, via font/wrap) keep settling as assets stream in
  // during load; recompute whenever <body> resizes so the bar converges without a scroll.
  if(window.ResizeObserver){
    var ro=new ResizeObserver(schedule);
    if(document.body) ro.observe(document.body);
    if(header) ro.observe(header);
  }

  schedule();
})();
