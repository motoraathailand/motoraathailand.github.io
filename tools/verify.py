#!/usr/bin/env python3
"""Static invariants for the three independent regional app hubs."""
from html.parser import HTMLParser
from pathlib import Path
import unittest
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
EXPECTED = {
    'world': {
        'global': {'aaai', 'autoreport', 'aacalc', 'moffee', 'bgaa'},
        'upcoming': {'scanner'},
        'default': 'en', 'absent': {'nammanthuk', 'aafranchise', 'fuelkr'},
    },
    'kr': {
        'global': {'aaai', 'autoreport', 'aacalc', 'moffee', 'bgaa'},
        'upcoming': {'scanner', 'fuelkr'},
        'default': 'ko', 'absent': {'nammanthuk', 'aafranchise'},
    },
    'th': {
        'global': {'aaai', 'autoreport', 'aacalc', 'moffee', 'bgaa', 'nammanthuk', 'aafranchise'},
        'upcoming': {'scanner'},
        'default': 'th', 'absent': {'fuelkr'},
    },
}

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.lang = ''; self.links = []; self.assets = []; self.cards = []; self.brand = [] ; self.body_region = ''
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
        if tag in ('a', 'div') and a.get('data-app'): self.cards.append({'id': a['data-app'], 'linked': tag == 'a'})

class Hubs(unittest.TestCase):
    def test_three_regional_hubs(self):
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
    def test_sitemap(self):
        xml = ET.parse(ROOT / 'sitemap.xml')
        actual = [item.text for item in xml.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
        self.assertEqual(actual, ['https://motoraathailand.github.io/', 'https://motoraathailand.github.io/kr/', 'https://motoraathailand.github.io/th/'])

if __name__ == '__main__': unittest.main()
