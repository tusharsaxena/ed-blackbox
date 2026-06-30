/*! ed-blackbox — Google Analytics (GA4)
   Single source of truth for the site's analytics tag. Loaded once per page via
   <script src=".../design-system/js/analytics.js" defer></script>. Self-contained
   and DOM-independent — it never touches page markup/behaviour, so it is safe on
   every page (including the four that ship their own inline quick-nav and cannot
   load ed-blackbox.js). To change or disable tracking, edit GA_ID here and nowhere
   else: an empty/placeholder value makes this a no-op. */
(function(){
  var GA_ID='G-MQ22R0QSS7';   // GA4 Measurement ID (GA Admin → Data streams → Web)
  if(GA_ID.indexOf('G-')!==0 || GA_ID==='G-XXXXXXXXXX') return;   // not configured → do nothing
  var s=document.createElement('script');
  s.async=true;
  s.src='https://www.googletagmanager.com/gtag/js?id='+encodeURIComponent(GA_ID);
  document.head.appendChild(s);
  window.dataLayer=window.dataLayer||[];
  function gtag(){window.dataLayer.push(arguments);}
  window.gtag=gtag;
  gtag('js', new Date());
  gtag('config', GA_ID);
})();
