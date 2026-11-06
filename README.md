# MOTOR AA regional hubs

Three **independent** static app hubs, with no cross-links between regions:

- `/` — Worldwide, English by default; global apps only.
- `/kr/` — Korea + Worldwide, Korean by default; global and Korea-only apps.
- `/th/` — Thailand + Worldwide, Thai by default; global and Thailand-only apps.

Published at <https://motoraathailand.github.io/>. Language choices are scoped to
each regional page. `?lang=` temporarily overrides the selected language;
otherwise the last choice for that region wins. The fallback is always the
region's default language rather than browser detection.

## Build

```sh
python3 tools/build.py
# Only when translated text changes and Noto source fonts are installed:
python3 tools/build.py --fonts
```

`tools/build.py` contains the app registry and th/en/ko/zh/hi translations. It
renders the three `index.html` files and `sitemap.xml`. App cards have a region
of `global`, `kr`, or `th`. `live=True` adds that app's introduction URL;
otherwise it is a non-linked, in-development card. `주유소를부탁해` is Korea-only
and awaits its introduction URL.

`assets/hub.css` is the tropical coral/peach design. `icons/logo-mark.png` is
transparent winged-AA-only line art cropped from the supplied reference; the
curved MOTOR AA / SARABURI lettering is excluded. Every page loads those assets
through root-relative `/assets` and `/icons` paths, so the same file works at all three URLs.
`hub.js` does not navigate between pages. Contact: motoraathailand@gmail.com.

Fonts are self-hosted IBM Plex Sans and Noto subsets (SIL OFL); no ad, analytics,
or tracker requests. `motion.css` / `motion.js` are copies of the shared standard.
A pre-rebuild archive is stored outside the repository in
`/workspace/hub-backups/hub-before-regional-tropical-20261106-2036.tar.gz`.

## Verify

```sh
python3 tools/verify.py
```

The verification fails on missing or incorrect apps per region, internal hub
cross-links, wrong default languages, non-winged-AA header images, broken local
asset paths, or sitemap omissions.
