/* Independent regional hubs. ?lang= > this region's saved choice > page default. */
(function () {
  'use strict';
  var S = window.HUB_STRINGS, L = window.HUB_LANGS, doc = document, root = doc.documentElement;
  var def = window.HUB_DEFAULT || 'en', region = window.HUB_REGION || 'world';
  var STORE = 'motoraa.lang.' + region;
  var NAMES = { th: 'ไทย', en: 'English', ko: '한국어', zh: '中文', hi: 'हिन्दी' };
  function norm(t) { t = String(t || '').toLowerCase().split(/[-_]/)[0]; return L.indexOf(t) >= 0 ? t : null; }
  function store(v) { try { if (v === undefined) return localStorage.getItem(STORE); localStorage.setItem(STORE, v); } catch (e) { return null; } }
  function pick() {
    var q = null; try { q = new URLSearchParams(location.search).get('lang'); } catch (e) {}
    return norm(q) || norm(store()) || def;
  }
  var SPACED = { en: 1, ko: 1, hi: 1 };
  function setText(el, v, code) {
    if (v.indexOf('|') < 0) { el.textContent = v; return; }
    el.textContent = '';
    v.split('|').forEach(function (p, i) {
      if (i && SPACED[code]) el.appendChild(doc.createTextNode(' '));
      var span = doc.createElement('span'); span.className = 'ph'; span.textContent = p; el.appendChild(span);
    });
  }
  function apply(code, fade) {
    var d = S[code]; if (!d) return;
    root.lang = code === 'zh' ? 'zh-Hans' : code;
    doc.title = d.doc_title;
    Array.prototype.forEach.call(doc.querySelectorAll('[data-i18n]'), function (el) {
      var value = d[el.getAttribute('data-i18n')]; if (value != null) setText(el, value, code);
    });
    var btn = doc.getElementById('langBtn'), menu = doc.getElementById('langMenu');
    doc.getElementById('langCur').textContent = NAMES[code];
    btn.setAttribute('aria-label', d.lang + ': ' + NAMES[code]); menu.setAttribute('aria-label', d.lang);
    Array.prototype.forEach.call(menu.querySelectorAll('[data-set-lang]'), function (item) {
      item.setAttribute('aria-checked', item.getAttribute('data-set-lang') === code ? 'true' : 'false');
    });
    if (fade && window.Motion) Motion.langFade(doc.querySelector('[data-lang-root]'));
  }
  var btn = doc.getElementById('langBtn'), menu = doc.getElementById('langMenu'), closeTimer = 0;
  function open() { clearTimeout(closeTimer); menu.classList.remove('closing'); menu.hidden = false; btn.setAttribute('aria-expanded', 'true'); var checked = menu.querySelector('[aria-checked=true]'); if (checked) checked.focus({ preventScroll: true }); }
  function close(focus) { if (menu.hidden) return; btn.setAttribute('aria-expanded', 'false'); menu.classList.add('closing'); closeTimer = setTimeout(function () { menu.hidden = true; menu.classList.remove('closing'); }, 240); if (focus) btn.focus({ preventScroll: true }); }
  btn.addEventListener('click', function () { menu.hidden || menu.classList.contains('closing') ? open() : close(); });
  menu.addEventListener('click', function (event) {
    var item = event.target.closest('[data-set-lang]'); if (!item) return;
    var code = item.getAttribute('data-set-lang'); store(code); apply(code, true); close(true);
  });
  doc.addEventListener('click', function (event) { if (!menu.hidden && !event.target.closest('.langwrap')) close(); });
  doc.addEventListener('keydown', function (event) {
    if (menu.hidden) return;
    if (event.key === 'Escape') { close(true); return; }
    if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      var items = Array.prototype.slice.call(menu.querySelectorAll('button')), i = items.indexOf(doc.activeElement);
      i = (i + (event.key === 'ArrowDown' ? 1 : items.length - 1)) % items.length; items[i].focus(); event.preventDefault();
    }
  });
  apply(pick(), false);
}());
