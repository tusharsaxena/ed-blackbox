/*! ed-blackbox design system v1.0.0 — behaviours
   Four independent, null-safe modules. Load once per page with
   <script src=".../ed-blackbox.js" defer></script>. Each checks for
   its own markup, so pages without a given component are unaffected:
     1. quick-nav  — filterable record jump menu (needs .header-qn / #qn-*)
     2. toc        — scrollspy that marks the active section (needs nav#toc)
     3. coord-copy — click-to-copy coordinate chips (needs .coord[data-copy])
     4. to-top     — scroll the page to the top (needs .qn-totop)
*/

/* 1 — quick-nav */
(function(){
  var dd=document.getElementById('qn-dd'),
      inp=document.getElementById('qn-search'),
      clr=document.getElementById('qn-clear'),
      panel=document.getElementById('qn-panel');
  if(!dd||!inp||!panel) return;
  var empty=panel.querySelector('.qn-empty'),
      items=Array.prototype.slice.call(panel.querySelectorAll('.qn-item'));
  function open(){dd.classList.add('open');inp.setAttribute('aria-expanded','true');}
  function close(){dd.classList.remove('open');inp.setAttribute('aria-expanded','false');clearActive();}
  function clearActive(){items.forEach(function(a){a.classList.remove('qn-active');});}
  function visible(){return items.filter(function(a){return a.style.display!=='none';});}
  function filter(){
    var q=inp.value.trim().toLowerCase(), n=0;
    items.forEach(function(a){
      var nm=a.querySelector('.qn-nm').textContent.toLowerCase();
      var show=!q||nm.indexOf(q)>-1;
      a.style.display=show?'':'none';
      if(show)n++;
    });
    empty.hidden=n>0;
    clr.hidden=!inp.value;
    clearActive();
    panel.scrollTop=0;
  }
  inp.addEventListener('focus',open);
  inp.addEventListener('input',function(){open();filter();});
  inp.addEventListener('keydown',function(e){
    var vis=visible();
    if(e.key==='Escape'){ if(inp.value){inp.value='';filter();} else {close();inp.blur();} return; }
    if(e.key==='Enter'){
      var cur=panel.querySelector('.qn-item.qn-active')||vis[0];
      if(cur){e.preventDefault();cur.click();}
      return;
    }
    if(e.key==='ArrowDown'||e.key==='ArrowUp'){
      e.preventDefault(); open();
      if(!vis.length) return;
      var i=vis.indexOf(panel.querySelector('.qn-item.qn-active'));
      clearActive();
      i = e.key==='ArrowDown' ? (i+1)%vis.length : (i<=0?vis.length-1:i-1);
      vis[i].classList.add('qn-active');
      vis[i].scrollIntoView({block:'nearest'});
    }
  });
  clr.addEventListener('click',function(e){e.preventDefault();inp.value='';filter();inp.focus();open();});
  items.forEach(function(a){a.addEventListener('click',function(){close();inp.value='';filter();});});
  document.addEventListener('click',function(e){if(!dd.contains(e.target))close();});
  filter();
})();

/* 2 — TOC scrollspy */
(function(){
  var toc=document.getElementById('toc'); if(!toc) return;
  var links=Array.prototype.slice.call(toc.querySelectorAll('a'));
  var map=links.map(function(a){var el=document.querySelector(a.getAttribute('href'));return {a:a,el:el};}).filter(function(x){return x.el;});
  if(!('IntersectionObserver' in window)||!map.length) return;
  var io=new IntersectionObserver(function(entries){
    entries.forEach(function(en){
      if(en.isIntersecting){
        var hit=map.filter(function(x){return x.el===en.target;})[0];
        if(hit){links.forEach(function(l){l.classList.remove('active');});hit.a.classList.add('active');}
      }
    });
  },{rootMargin:'-45% 0px -50% 0px'});
  map.forEach(function(x){io.observe(x.el);});
})();

/* 3 — coordinate copy */
(function(){
  document.querySelectorAll('.coord[data-copy]').forEach(function(el){
    el.addEventListener('click',function(){
      var t=el.getAttribute('data-copy');
      if(navigator.clipboard) navigator.clipboard.writeText(t);
      var cp=el.querySelector('.cp'), old=cp?cp.textContent:'';
      el.classList.add('copied'); if(cp)cp.textContent='Copied';
      setTimeout(function(){el.classList.remove('copied'); if(cp)cp.textContent=old||'Copy';},1200);
    });
  });
})();

/* 4 — scroll to top (header button) */
(function(){
  var btns=document.querySelectorAll('.qn-totop'); if(!btns.length) return;
  var reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  btns.forEach(function(b){
    b.addEventListener('click',function(e){
      e.preventDefault();
      window.scrollTo({top:0,behavior:reduce?'auto':'smooth'});
    });
  });
})();
