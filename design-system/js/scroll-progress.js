/*! ed-blackbox — page scroll-progress indicator
   A thin amber hairline bar, pinned directly under the 62px site-header, that fills
   left→right as the reader scrolls the page. Single source of truth for the indicator.
   Loaded once per page via <script src=".../design-system/js/scroll-progress.js" defer>.

   Self-contained and (nearly) markup-independent — like analytics.js it injects its own
   element and styles and never touches existing page markup/behaviour, so it is safe on
   every page, INCLUDING the four engineering-manual pages that ship their own inline
   quick-nav and cannot load ed-blackbox.js. Styling uses the design-system CSS tokens
   (--maroon/--amber/--amber-lt, present on every page via ed-blackbox.css) with hard
   fallbacks, so it still renders correctly if those tokens are ever absent.

   Perf: the bar is a 100%-wide fixed element scaled with transform:scaleX() (GPU-
   composited, zero layout), updated on a requestAnimationFrame-throttled passive scroll
   listener — the same approach as ed-blackbox.js's sticky-header module. No width
   transition (a scroll-driven bar must track the scroll exactly, not ease behind it), so
   there is nothing for prefers-reduced-motion to disable. To restyle or disable, edit
   this file and nowhere else. */
(function(){
  if(document.getElementById('edbb-scroll-progress')) return;   // never double-inject

  // --- inject the bar ---------------------------------------------------------
  var bar=document.createElement('div');
  bar.id='edbb-scroll-progress';
  bar.setAttribute('aria-hidden','true');   // decorative chrome — not announced
  bar.style.cssText=[
    'position:fixed','left:0','top:62px','width:100%','height:2px',
    'transform:scaleX(0)','transform-origin:left center',
    'z-index:40',   // --z-sticky: above content, below the --z-nav:50 site-header
    'pointer-events:none',
    'background:linear-gradient(90deg,var(--maroon,#8b2332),var(--amber,#e0913a) 60%,var(--amber-lt,#f4b15f))',
    'box-shadow:0 0 10px rgba(224,145,58,.5)',
    'will-change:transform'
  ].join(';');
  (document.body||document.documentElement).appendChild(bar);

  // --- position under the (sticky) site-header, whatever its height -----------
  var header=document.querySelector('.site-header');
  function place(){ bar.style.top=(header?header.offsetHeight:0)+'px'; }

  // --- fraction scrolled (0..1) ----------------------------------------------
  function frac(){
    var d=document.documentElement, b=document.body;
    var st=window.pageYOffset||d.scrollTop||b.scrollTop||0;
    var max=(d.scrollHeight||b.scrollHeight)-d.clientHeight;
    return max<=0?0:Math.min(1,Math.max(0,st/max));
  }

  var pending=false;
  function render(){ pending=false; bar.style.transform='scaleX('+frac()+')'; }
  function schedule(){ if(!pending){ pending=true; requestAnimationFrame(render); } }

  window.addEventListener('scroll',schedule,{passive:true});
  window.addEventListener('resize',function(){ place(); schedule(); });
  window.addEventListener('load',function(){ place(); render(); });   // fonts may re-wrap the header
  place(); render();
})();
