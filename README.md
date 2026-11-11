# MOTOR AA regional hubs

Three **independent** static app hubs, with no cross-links between regions:

- `/` — Worldwide, English by default; global apps only.
- `/kr/` — Korea + Worldwide, Korean by default; global and Korea-only apps.
- `/th/` — Thailand market. Thai is the primary version of the page, not a forced language. Only น้ำมันถูก, AA Franchise, and BGAA, each with store buttons.

Published at <https://motoraathailand.github.io/>. Language choices are scoped to
each regional page. `?lang=` temporarily overrides the selected language;
otherwise the last manual choice for that region wins. With no saved choice,
the page follows the device language and falls back to English.

## Build

```sh
python3 tools/build.py
# Only when translated text changes and Noto source fonts are installed:
python3 tools/build.py --fonts
```

`tools/build.py` contains the app registry and th/en/ko/zh/hi translations. It
renders the three `index.html` files and `sitemap.xml`. On `/` and `/kr/`, app
cards have a region of `global` or `kr`. `live=True` adds that app's introduction
URL; otherwise it is a non-linked, in-development card. `주유소를부탁해` is
Korea-only and awaits its introduction URL. `/th/` does not use that grid and
does not show `주유소를부탁해`. The generator writes only น้ำมันถูก, AA Franchise,
then BGAA. Other apps stay in the registry and are hidden from `/th/`. EZZ is
registered as a global app but filtered off `/` and `/kr/`. Each card has a
Google Play button and an App Store button, and no leaf decoration. Both
Nammanthuk buttons open `https://motoraathailand.github.io/nammanthuk-site/`,
and both AA Franchise buttons open
`https://motoraathailand.github.io/aafranchise-site/`. Those intro pages follow
the device language. BGAA store buttons are localized in-development
controls. Thailand-only stylesheet rules are appended under
`body[data-region="th"]` and the Thailand page loads them with its own CSS query.

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

The verification fails on missing or incorrect apps per region, a Thailand page
that is not the three cards in order with six store buttons in the right state,
a rebuild that changes `/` or `/kr/` bytes, internal hub cross-links, wrong
default languages, non-winged-AA header images, broken local asset paths, or
sitemap omissions.
