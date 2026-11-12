/* Seizure Watch - shared top bar. Add  <script src="PATH/shared/topbar.js" data-active="board"></script>  right after <body>. */
(function () {
  var s = document.currentScript, base = s.src.replace(/shared\/topbar\.js.*$/, '');
  var active = s.getAttribute('data-active') || '';
  var pages = [['dashboard', 'Dashboard', ''], ['board', 'Board', 'board/'], ['motion', 'Motion', 'motion/'],
    ['lite', 'Lite', 'lite/'], ['bulletin', 'Bulletin', 'bulletin.html'], ['newsletter', 'Newsletter', 'newsletter.html'],
    ['reports', 'Reports', 'reports/']];
  var h = '<div class="swbar-in"><a class="swbrand" href="' + base + '"><img src="' + base + 'shared/logo.png" alt="AIRCOP - Container Control Programme">' +
    '<span><b>Seizure Watch</b><small>Open-source seizure intelligence</small></span></a><nav class="swpages">';
  pages.forEach(function (p) { h += '<a href="' + base + p[2] + '"' + (p[0] === active ? ' class="on"' : '') + '>' + p[1] + '</a>'; });
  h += '</nav><details class="swdl"><summary>Downloads &#9662;</summary><div><a href="' + base + 'events.csv">Events (CSV)</a>' +
    '<a href="' + base + 'seizure_watch.xlsx">Excel workbook</a><a href="' + base + 'newsletter.pdf">Weekly newsletter (PDF)</a></div></details></div>';
  var bar = document.createElement('header'); bar.className = 'swbar'; bar.innerHTML = h;
  document.body.insertBefore(bar, document.body.firstChild);
  document.addEventListener('click', function (e) { var d = bar.querySelector('details'); if (d && d.open && !d.contains(e.target)) d.open = false; });
})();
