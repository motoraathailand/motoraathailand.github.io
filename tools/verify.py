#!/usr/bin/env python3
"""Static invariants for the MOTOR AA hub: Thailand collection at / and /th/; /kr/ is deleted."""
from html.parser import HTMLParser
from pathlib import Path
import hashlib
import importlib.util
import unittest
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
# Deleted hubs: these files must not exist.
DELETED = ('kr/index.html', 'kr')
TH_URL = 'https://motoraath.com'
# Bytes of shared files this change must not touch.
STABLE_SHA256 = {
    # /th/ after BGAA App Store button set to unsupported (2026-11-12).
    'index.html': '17ce63d94271792ce208795a66e92f85e1b71f52984913b288acb3df68a5e4c6',
    'th/index.html': '17ce63d94271792ce208795a66e92f85e1b71f52984913b288acb3df68a5e4c6',
    'assets/hub.js': '94396a697ab78814233e455899a4bd5cd8cb035d1f16c626c7fd813eaf31b7a2',
    'motion.css': 'a441adf71bc5d124353e1ec14f81f52d5c389a25462299036ce4ab36a7f6f447',
    'motion.js': '7807dd5b18432e4dece794d932d54369f22d3a87ef861dd4bdf708a7f5de9da1',
}
REGION_TEXT = ('ไทย + ทั่วโลก', 'Thailand + Worldwide', '태국 + 전 세계', '泰国 + 全球', 'थाईलैंड + दुनिया भर',
               'Worldwide apps', '한국 + 전 세계', 'Korea + Worldwide', '전 세계 앱')
CSS_PREFIX_SHA256 = 'd6430472029f7db1ab721763ef2eeb378c2cb32fce77a441cc26b1c2d45e4104'
NAMMANTHUK_INTRO = 'https://motoraathailand.github.io/nammanthuk-site/'
AAFRANCHISE_INTRO = 'https://motoraathailand.github.io/aafranchise-site/'
AAAI_INTRO = 'https://aaai-iji8.onrender.com/about'
BGAA_INTRO = 'https://motoraathailand.github.io/bgaa-site/'
TH_ORDER = ('nammanthuk', 'aafranchise', 'aaai', 'bgaa')
TH_NAMES = ('น้ำมันถูก', 'AA Franchise', 'AAAi', 'BGAA')

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.lang = ''; self.links = []; self.assets = []; self.cards = []; self.brand = [] ; self.body_region = ''
        self.names = []; self.stores = []; self._name = None; self._name_buf = []; self._store = None; self._store_buf = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html': self.lang = a.get('lang', '')
        if tag == 'body': self.body_region = a.get('data-region', '')
        if tag == 'a': self.links.append(a.get('href', ''))
        if tag == 'img':
            if not self.brand: self.brand.append(a['src'])
            if not a['src'].startswith(('http:', 'https:')): self.assets.append(a['src'])
        if tag == 'link' and a.get('href', '').startswith('/'): self.assets.append(a['href'])
        if tag == 'script' and a.get('src', '').startswith('/'): self.assets.append(a['src'])
        if tag == 'source' and a.get('srcset', '').startswith('/'): self.assets.append(a['srcset'])
        if tag in ('a', 'div') and a.get('data-app'): self.cards.append({'id': a['data-app'], 'linked': tag == 'a', 'stores': []})
        classes = a.get('class', '').split()
        if 'app-name' in classes:
            self._name = True; self._name_buf = []
        if a.get('data-store'):
            self._store = {
                'kind': a.get('data-store'), 'state': a.get('data-state'), 'href': a.get('href'),
                'disabled': 'disabled' in a or a.get('aria-disabled') == 'true', 'tag': tag, 'text': '',
            }
            self._store_buf = []
            if self.cards: self.cards[-1]['stores'].append(self._store)
            self.stores.append(self._store)
    def handle_endtag(self, tag):
        if self._name and tag == 'span':
            self.names.append(''.join(self._name_buf).strip()); self._name = None
        if self._store and tag in ('a', 'button'):
            self._store['text'] = ''.join(self._store_buf)
            self._store = None
    def handle_data(self, data):
        if self._name: self._name_buf.append(data)
        if self._store: self._store_buf.append(data)

class Hubs(unittest.TestCase):
    def test_korea_hub_deleted_and_root_is_thailand(self):
        for rel in DELETED:
            self.assertFalse((ROOT / rel).exists(), rel)
        html_pages = sorted(str(p.relative_to(ROOT)) for p in ROOT.rglob('*.html') if '.git' not in p.parts)
        self.assertEqual(html_pages, ['404.html', 'index.html', 'th/index.html'])
        notfound = (ROOT / '404.html').read_text(encoding='utf-8')
        self.assertNotIn('http-equiv="refresh"', notfound)
        self.assertNotIn('location.', notfound)
        self.assertIn('href="/"', notfound)
        root = (ROOT / 'index.html').read_text(encoding='utf-8')
        th = (ROOT / 'th' / 'index.html').read_text(encoding='utf-8')
        self.assertEqual(root, th)

    def test_thailand_cards_and_store_buttons(self):
        text = (ROOT / 'th' / 'index.html').read_text(encoding='utf-8')
        page = Page(); page.feed(text)
        self.assertEqual(page.lang, 'th')
        self.assertEqual(page.body_region, 'th')
        self.assertEqual([c['id'] for c in page.cards], list(TH_ORDER))
        self.assertEqual(tuple(page.names), TH_NAMES)
        self.assertEqual(len(page.stores), 8)
        self.assertNotIn('soon-section', text)
        self.assertNotIn('class="cta"', text)
        self.assertNotIn('class="palm"', text)
        self.assertNotIn('<video', text)
        self.assertNotIn('play.google.com', text)
        self.assertNotIn('apps.apple.com', text)
        self.assertNotIn('data-app="fuelkr"', text)
        self.assertNotIn('join.html', text)
        self.assertIn('window.HUB_REGION="th"', text)
        self.assertIn('window.HUB_DEFAULT="th"', text)
        self.assertIn('window.HUB_LANGS=["th", "en", "ko", "zh", "hi"]', text)
        self.assertIn('/assets/hub.css?v=14', text)
        dev = 'กำลังพัฒนา'
        both_dev = (('google-play', 'dev', None), ('app-store', 'dev', None))
        expect = {app_id: both_dev for app_id in TH_ORDER}
        expect['nammanthuk'] = (
            ('google-play', 'live', NAMMANTHUK_INTRO),
            ('app-store', 'live', NAMMANTHUK_INTRO),
        )
        expect['bgaa'] = (
            ('google-play', 'live', BGAA_INTRO),
            ('app-store', 'unsupported', None),
        )
        self.assertNotIn('data-state="dev"', text)
        self.assertIn('data-state="unsupported"', text)
        self.assertIn('data-i18n="unsupported_badge"', text)
        expect['aaai'] = (
            ('google-play', 'live', AAAI_INTRO),
            ('app-store', 'live', AAAI_INTRO),
        )
        expect['aafranchise'] = (
            ('google-play', 'live', AAFRANCHISE_INTRO),
            ('app-store', 'live', AAFRANCHISE_INTRO),
        )
        self.assertTrue(all(st in ('live', 'unsupported') for v in expect.values() for _, st, _ in v), 'no in-development cards')
        unsupported = 'ไม่รองรับ'
        for card in page.cards:
            self.assertFalse(card['linked'])
            self.assertEqual(len(card['stores']), 2)
            for store, (kind, state, href) in zip(card['stores'], expect[card['id']]):
                self.assertEqual(store['kind'], kind)
                self.assertEqual(store['state'], state)
                label = 'Google Play' if kind == 'google-play' else 'App Store'
                self.assertIn(label, store['text'])
                if state == 'live':
                    self.assertEqual(store['tag'], 'a')
                    self.assertEqual(store['href'], href)
                    self.assertFalse(store['disabled'])
                    self.assertNotIn(dev, store['text'])
                    self.assertNotIn(unsupported, store['text'])
                elif state == 'unsupported':
                    self.assertEqual(store['tag'], 'button')
                    self.assertIsNone(store['href'])
                    self.assertTrue(store['disabled'])
                    self.assertIn(unsupported, store['text'])
                    self.assertNotIn(dev, store['text'])
                else:
                    self.assertEqual(store['tag'], 'button')
                    self.assertIsNone(store['href'])
                    self.assertTrue(store['disabled'])
                    self.assertIn(dev, store['text'])
        for href in page.links:
            parsed = urlsplit(href)
            self.assertTrue(parsed.scheme in ('https', 'mailto'), href)
            if parsed.scheme == 'https':
                self.assertNotIn(parsed.path, ('/', '/kr/', '/th/'), href)
        self.assertEqual(page.brand, ['/icons/logo-mark.png'])
        self.assertNotIn('class="chips"', text)
        self.assertNotIn('data-i18n="chips_free"', text)
        self.assertNotIn('data-i18n="chips_notrack"', text)
        self.assertNotIn('"chips_free"', text)
        self.assertNotIn('"chips_noads"', text)
        self.assertNotIn('"chips_notrack"', text)
        # The region label text is gone in every language; the star stays.
        self.assertNotIn('region_', text)
        for label in REGION_TEXT:
            self.assertNotIn(label, text)
        self.assertIn('<span class="region" aria-hidden="true"></span>', text)
        star = '<span class="eyebrow m-stagger" style="--i:0"><svg class="ic " viewBox="0 0 24 24" aria-hidden="true"><path d="m12 3 2.1 6.9L21 12l-6.9 2.1L12 21l-2.1-6.9L3 12l6.9-2.1z"/></svg></span>'
        self.assertIn(star, text)
        self.assertNotIn('motoraathailand.github.io/kr/', text)
        self.assertIn('<link rel="canonical" href="%s">' % TH_URL, text)
        self.assertIn('<meta property="og:url" content="%s">' % TH_URL, text)

    def test_rebuild_matches_committed_output(self):
        spec = importlib.util.spec_from_file_location('hubbuild', ROOT / 'tools' / 'build.py')
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertEqual([p['slug'] for p in mod.PAGES], ['th'])
        rendered = mod.render_page(mod.PAGES[0]).replace('|', ' ')
        self.assertEqual(rendered, (ROOT / 'th' / 'index.html').read_text(encoding='utf-8'))
        self.assertEqual(rendered, (ROOT / 'index.html').read_text(encoding='utf-8'))
        self.assertEqual(mod.SITE, 'https://motoraath.com')
        self.assertEqual(mod.TH_URL, 'https://motoraath.com')
        self.assertFalse(hasattr(mod, 'render_redirect'))
        for rel, digest in STABLE_SHA256.items():
            body = (ROOT / rel).read_bytes()
            self.assertEqual(hashlib.sha256(body).hexdigest(), digest, rel)
        css = (ROOT / 'assets' / 'hub.css').read_bytes()
        marker = b'/* Thailand hub store actions.'
        self.assertIn(marker, css)
        prefix, added = css.split(marker, 1)
        self.assertEqual(hashlib.sha256(prefix).hexdigest(), CSS_PREFIX_SHA256)
        self.assertIn(b'body[data-region="th"]', added)
        self.assertNotIn(b'\n.card{', added)
        js = (ROOT / 'assets' / 'hub.js').read_text(encoding='utf-8')
        self.assertIn("return norm(q) || norm(store()) || dev || 'en';", js)
        self.assertIn("var STORE = 'motoraa.lang.' + region;", js)

    def test_intro_pages_resolve(self):
        import urllib.request
        for url, needle in (
            (NAMMANTHUK_INTRO, 'น้ำมันถูก'),
            (AAFRANCHISE_INTRO, 'AA Franchise'),
            (AAAI_INTRO, 'AAAi'),
            (BGAA_INTRO, 'BGAA'),
        ):
            req = urllib.request.Request(url, headers={'User-Agent': 'motoraa-hub-verify'})
            with urllib.request.urlopen(req, timeout=30) as res:
                body = res.read().decode('utf-8', 'replace')
                self.assertEqual(res.status, 200, url)
                self.assertEqual(res.geturl(), url)
                self.assertIn('html', res.headers.get('content-type', ''))
            self.assertIn('rel="canonical" href="%s"' % url, body)
            self.assertIn(needle, body)
            self.assertNotIn('join.html"', 'href="%s"' % url)

    def test_sitemap(self):
        xml = ET.parse(ROOT / 'sitemap.xml')
        actual = [item.text for item in xml.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
        self.assertEqual(actual, [TH_URL])

    def test_custom_domain(self):
        self.assertEqual((ROOT / 'CNAME').read_text(encoding='utf-8').strip(), 'motoraath.com')
        robots = (ROOT / 'robots.txt').read_text(encoding='utf-8')
        self.assertIn('Sitemap: https://motoraath.com/sitemap.xml', robots)
        self.assertNotIn('motoraathailand.github.io/sitemap.xml', robots)

if __name__ == '__main__': unittest.main()
