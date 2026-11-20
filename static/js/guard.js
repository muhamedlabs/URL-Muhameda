(function () {
  'use strict';
  var fine = false;
  try { fine = matchMedia('(hover:hover) and (pointer:fine)').matches; } catch (e) {}
  try { if (localStorage.getItem('dev') === '1') return; } catch (e) {}
  var editable = function (t) { return t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable); };

  document.addEventListener('contextmenu', function (e) { if (!editable(e.target)) e.preventDefault(); }, true);
  document.addEventListener('dragstart', function (e) { e.preventDefault(); }, true);

  document.addEventListener('keydown', function (e) {
    var k = (e.key || '').toLowerCase(), c = e.ctrlKey || e.metaKey;
    var block = e.key === 'F12' ||
      (c && e.shiftKey && 'ijcke'.indexOf(k) > -1 && k.length === 1) ||
      (c && e.altKey && 'iujc'.indexOf(k) > -1 && k.length === 1) ||
      (c && !e.shiftKey && (k === 'u' || k === 's'));
    if (block) { e.preventDefault(); e.stopPropagation(); return false; }
  }, true);

  if (!fine) return;
  var st = document.createElement('style');
  st.textContent = 'html.dt-lock body{visibility:hidden!important}html.dt-lock{background:#111}';
  document.head.appendChild(st);
  var lock = function (on) { document.documentElement.classList.toggle('dt-lock', on); };
  var open = false;
  var check = function () {
    var wide = outerWidth - innerWidth > 170, high = outerHeight - innerHeight > 170;
    var t = performance.now();
    (function () { debugger; })();
    var slow = performance.now() - t > 120;
    open = wide || high || slow;
    lock(open);
  };
  setInterval(check, 1200);
  addEventListener('resize', check);
})();
