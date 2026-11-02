#!/usr/bin/env python3
"""Layout audit: all langs x widths x schemes. Flags overflow, orphan last lines, uneven chip rows. python3 tools/matrix.py URL [outdir]"""
import sys, itertools, json
from playwright.sync_api import sync_playwright
url = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else None
JS = """() => {
 const res = [];
 const sels = ['h1','.sub','.desc','.soon-sub','.contact p','.foot span','.sec','.app-name','.cat','.chips li span','.cta span'];
 const doc = document.documentElement;
 if (doc.scrollWidth > doc.clientWidth) res.push('OVERFLOW-X ' + doc.scrollWidth);
 for (const s of sels) for (const el of document.querySelectorAll(s)) {
   if (!el.offsetParent) continue;
   const r = document.createRange(); r.selectNodeContents(el);
   const rects = [...r.getClientRects()].filter(x => x.width > 1);
   const tops = []; rects.forEach(x => { if (!tops.some(t => Math.abs(t.top - x.top) < 4)) tops.push({top: x.top, l: x.left, r: x.right}); else { const t = tops.find(t => Math.abs(t.top - x.top) < 4); t.l = Math.min(t.l, x.left); t.r = Math.max(t.r, x.right); } });
   if (tops.length > 1) {
     const w = Math.max(...tops.map(t => t.r - t.l)), last = tops[tops.length-1], lw = last.r - last.l;
     if (lw < w * 0.28 && !s.includes('chips') ) res.push('ORPHAN ' + s + ' "' + el.textContent.trim().slice(0,30) + '" last=' + Math.round(lw) + ' max=' + Math.round(w));
   }
   const b = el.getBoundingClientRect(); if (b.right > doc.clientWidth + 1 || b.left < -1) res.push('CLIP ' + s + ' ' + el.textContent.trim().slice(0,20));
 }
 const ch = [...document.querySelectorAll('.chips li')].map(e => Math.round(e.getBoundingClientRect().height)); if (new Set(ch).size > 1) res.push('CHIPS-UNEVEN ' + ch);
 return res; }"""
bad = 0
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    for lang, w, dark in itertools.product(['th','en','ko','zh','hi'], [360, 390, 412, 1100], [False, True]):
        ctx = b.new_context(viewport={'width': w, 'height': 800}, device_scale_factor=1, locale={'th':'th-TH','en':'en-US','ko':'ko-KR','zh':'zh-CN','hi':'hi-IN'}[lang], is_mobile=w < 800, color_scheme='dark' if dark else 'light')
        pg = ctx.new_page(); pg.goto(url, wait_until='networkidle'); pg.wait_for_timeout(1700)
        pg.evaluate("window.scrollTo(0, document.body.scrollHeight)"); pg.wait_for_timeout(1100); pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(200)
        r = pg.evaluate(JS); tag = f'{lang}-{w}-{"dark" if dark else "light"}'
        if r: bad += 1; print(tag, r)
        if out and (w in (360, 412, 1100) or True): pg.screenshot(path=f'{out}/{tag}.png', full_page=True)
        ctx.close()
    b.close()
print('combos with findings:', bad)
