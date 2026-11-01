/* MOTOR AA hub: language (th/en/ko/zh/hi). Order: ?lang= > saved choice > browser language (if supported) > English. No network, no tracking. */
(function () {
  'use strict';
  var S = window.HUB_STRINGS, L = window.HUB_LANGS, doc = document, root = doc.documentElement;
  var NAMES = { th: 'ไทย', en: 'English', ko: '한국어', zh: '中文', hi: 'हिन्दी' };
  function norm(t) { t = String(t || '').toLowerCase().split(/[-_]/)[0]; return L.indexOf(t) >= 0 ? t : null; }
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }
  function pick() {
    var q = null; try { q = new URLSearchParams(location.search).get('lang'); } catch (e) {}
    var c = norm(q) || norm(store('lang'));
    if (c) return c;
    var list = navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language];
    for (var i = 0; i < list.length; i++) { c = norm(list[i]); if (c) return c; }
    return 'en';
  }
  var cur = null;
  function apply(code, fade) {
    cur = code; var d = S[code];
    root.lang = code === 'zh' ? 'zh-Hans' : code;
    doc.title = d.doc_title;
    Array.prototype.forEach.call(doc.querySelectorAll('[data-i18n]'), function (el) { var v = d[el.getAttribute('data-i18n')]; if (v != null) el.textContent = v; });
    Array.prototype.forEach.call(doc.querySelectorAll('[data-i18n-aria]'), function (el) { var v = d[el.getAttribute('data-i18n-aria')]; if (v) el.setAttribute('aria-label', v); });
    var lb = doc.getElementById('langBtn'), lm = doc.getElementById('langMenu');
    doc.getElementById('langCur').textContent = NAMES[code];
    lb.setAttribute('aria-label', d.lang + ': ' + NAMES[code]); lm.setAttribute('aria-label', d.lang);
    Array.prototype.forEach.call(lm.querySelectorAll('[data-set-lang]'), function (b) { b.setAttribute('aria-checked', b.getAttribute('data-set-lang') === code ? 'true' : 'false'); });
    if (fade && window.Motion) Motion.langFade(doc.querySelector('[data-lang-root]'));
  }
  var btn = doc.getElementById('langBtn'), menu = doc.getElementById('langMenu'), closeT = 0;
  function open() { clearTimeout(closeT); menu.classList.remove('closing'); menu.hidden = false; btn.setAttribute('aria-expanded', 'true'); var c = menu.querySelector('[aria-checked=true]'); if (c) c.focus({ preventScroll: true }); }
  function close(focusBtn) {
    if (menu.hidden) return; btn.setAttribute('aria-expanded', 'false'); menu.classList.add('closing');
    closeT = setTimeout(function () { menu.hidden = true; menu.classList.remove('closing'); }, 240);
    if (focusBtn) btn.focus({ preventScroll: true });
  }
  btn.addEventListener('click', function () { menu.hidden || menu.classList.contains('closing') ? open() : close(); });
  menu.addEventListener('click', function (e) {
    var b = e.target.closest('[data-set-lang]'); if (!b) return;
    var c = b.getAttribute('data-set-lang'); store('lang', c); apply(c, true); close(true);
  });
  doc.addEventListener('click', function (e) { if (!menu.hidden && !e.target.closest('.langwrap')) close(); });
  doc.addEventListener('keydown', function (e) {
    if (menu.hidden) return;
    if (e.key === 'Escape') { close(true); return; }
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      var items = Array.prototype.slice.call(menu.querySelectorAll('button')), i = items.indexOf(doc.activeElement);
      i = (i + (e.key === 'ArrowDown' ? 1 : items.length - 1)) % items.length; items[i].focus(); e.preventDefault();
    }
  });
  apply(pick(), false);
})();
