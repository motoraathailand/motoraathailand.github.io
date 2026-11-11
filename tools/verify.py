#!/usr/bin/env python3
"""Static invariants for the three independent regional app hubs."""
from html.parser import HTMLParser
from pathlib import Path
import hashlib
import importlib.util
import unittest
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
EXPECTED = {
    'world': {
        'global': {'aaai', 'autoreport', 'aacalc', 'moffee', 'bgaa'},
        'upcoming': {'scanner'},
        'default': 'en', 'absent': {'nammanthuk', 'aafranchise', 'fuelkr', 'ezz'},
    },
    'kr': {
        'global': {'aaai', 'autoreport', 'aacalc', 'moffee', 'bgaa'},
        'upcoming': {'scanner', 'fuelkr'},
        'default': 'ko', 'absent': {'nammanthuk', 'aafranchise', 'ezz'},
    },
}
# Bytes of files this change must not touch. Thailand HTML and the appended
# hub.css rules are the only generated/style output that may differ.
STABLE_SHA256 = {
    'index.html': '296d5f01d1d63aa0507e990a04a1b3738706d15826fad7b10822fac7aca32600',
    'kr/index.html': 'c2f7f4d4957e799a54ee02b3e955332143752ff988a664dee5820f3a16b50a16',
    'sitemap.xml': '06ce531f9db8fc09ae7e67e7942e2be6f40d3f0a9924cd549ed5de6f6a8ce4c0',
    'assets/hub.js': '94396a697ab78814233e455899a4bd5cd8cb035d1f16c626c7fd813eaf31b7a2',
    'motion.css': 'a441adf71bc5d124353e1ec14f81f52d5c389a25462299036ce4ab36a7f6f447',
    'motion.js': '7807dd5b18432e4dece794d932d54369f22d3a87ef861dd4bdf708a7f5de9da1',
}
CSS_PREFIX_SHA256 = 'd6430472029f7db1ab721763ef2eeb378c2cb32fce77a441cc26b1c2d45e4104'
NAMMANTHUK_INTRO = 'https://motoraathailand.github.io/nammanthuk-site/'
AAFRANCHISE_INTRO = 'https://motoraathailand.github.io/aafranchise-site/'
TH_ORDER = ('nammanthuk', 'aafranchise', 'bgaa')
TH_NAMES = ('น้ำมันถูก', 'AA Franchise', 'BGAA')

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
    def test_worldwide_and_korea_hubs(self):
        for region, expected in EXPECTED.items():
            with self.subTest(region=region):
                directory = ROOT if region == 'world' else ROOT / region
                page = Page(); page.feed((directory / 'index.html').read_text())
                self.assertEqual(page.lang, expected['default'])
                self.assertEqual(page.body_region, region)
                self.assertEqual({c['id'] for c in page.cards if c['linked']}, expected['global'])
                self.assertEqual({c['id'] for c in page.cards if not c['linked']}, expected['upcoming'])
                self.assertFalse(expected['absent'] & {c['id'] for c in page.cards})
                self.assertEqual(page.brand, ['/icons/logo-mark.png'])
                for asset in page.assets:
                    self.assertTrue((ROOT / asset.split('?', 1)[0].lstrip('/')).resolve().is_file(), asset)
                for href in page.links:
                    parsed = urlsplit(href)
                    self.assertTrue(parsed.scheme in ('https', 'mailto'), f'Unexpected internal link: {href}')
                    if parsed.scheme == 'https':
                        self.assertNotIn(parsed.path, ('/', '/kr/', '/th/'), f'Hub cross-link: {href}')

    def test_thailand_cards_and_store_buttons(self):
        text = (ROOT / 'th' / 'index.html').read_text(encoding='utf-8')
        page = Page(); page.feed(text)
        self.assertEqual(page.lang, 'th')
        self.assertEqual(page.body_region, 'th')
        self.assertEqual([c['id'] for c in page.cards], list(TH_ORDER))
        self.assertEqual(tuple(page.names), TH_NAMES)
        self.assertEqual(len(page.stores), 6)
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
        expect['aafranchise'] = (
            ('google-play', 'live', AAFRANCHISE_INTRO),
            ('app-store', 'live', AAFRANCHISE_INTRO),
        )
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

    def test_rebuild_leaves_root_and_korea_bytes(self):
        spec = importlib.util.spec_from_file_location('hubbuild', ROOT / 'tools' / 'build.py')
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for page in mod.PAGES:
            rendered = mod.render_page(page).replace('|', ' ')
            path = ROOT / 'index.html' if page['slug'] == 'world' else ROOT / page['path'] / 'index.html'
            if page['slug'] == 'th':
                self.assertEqual(rendered, (ROOT / 'th' / 'index.html').read_text(encoding='utf-8'))
                continue
            self.assertEqual(rendered, path.read_text(encoding='utf-8'))
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
        self.assertEqual(actual, ['https://motoraathailand.github.io/', 'https://motoraathailand.github.io/kr/', 'https://motoraathailand.github.io/th/'])

if __name__ == '__main__': unittest.main()
