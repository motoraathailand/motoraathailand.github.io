#!/usr/bin/env python3
"""python3 tools/shot.py URL OUT.png [locale] [dark] [width] — mobile headless screenshot (full page)"""
import sys
from playwright.sync_api import sync_playwright
url, out = sys.argv[1], sys.argv[2]
loc = sys.argv[3] if len(sys.argv) > 3 else 'en-US'
dark = len(sys.argv) > 4 and sys.argv[4] == 'dark'
w = int(sys.argv[5]) if len(sys.argv) > 5 else 390
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    ctx = b.new_context(viewport={'width': w, 'height': 844}, device_scale_factor=2, locale=loc, is_mobile=True, has_touch=True, color_scheme='dark' if dark else 'light')
    pg = ctx.new_page(); errs = []
    pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('requestfailed', lambda r: errs.append('FAILED ' + r.url))
    pg.goto(url, wait_until='networkidle'); pg.wait_for_timeout(1800)
    pg.evaluate("window.scrollTo(0, document.body.scrollHeight)"); pg.wait_for_timeout(1200); pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(300)
    print(pg.evaluate("({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth,lang:document.documentElement.lang,title:document.title})"), errs)
    pg.screenshot(path=out, full_page=True); b.close()
