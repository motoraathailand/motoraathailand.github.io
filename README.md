# MOTOR AA app hub

Only the **Thailand** hub is operated:

- `/th/` — Thailand market. Thai is the primary version of the page, not a forced language. Only น้ำมันถูก, AA Franchise, and BGAA, each with store buttons. The hero keeps its star mark without a region label.
- `/` and `/kr/` — deleted (Nov 11, 2026). No page and no redirect is built there; GitHub Pages serves `404.html` (a plain not-found page with a link to `/th`). Intro sites link to `https://motoraathailand.github.io/th` directly; canonical, og:url and the sitemap use that same address.

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
renders `th/index.html` and `sitemap.xml` (which lists
only `/th/`). `/th/` does not show `주유소를부탁해`. The generator writes only น้ำมันถูก, AA Franchise,
then BGAA. Other apps stay in the registry and are hidden from `/th/`. EZZ stays in the registry, hidden. Each card has a
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
through root-relative `/assets` and `/icons` paths, so the same file works at any URL.
`hub.js` does not navigate between pages. Contact: motoraathailand@gmail.com.

Fonts are self-hosted IBM Plex Sans and Noto subsets (SIL OFL); no ad, analytics,
or tracker requests. `motion.css` / `motion.js` are copies of the shared standard.
A pre-rebuild archive is stored outside the repository in
`/workspace/hub-backups/hub-before-regional-tropical-20261106-2036.tar.gz`.

## Verify

```sh
python3 tools/verify.py
```

The verification fails when `/` or `/kr/` pages exist, `404.html` redirects, a Thailand
page that is not the three cards in order with six store buttons in the right
state, region label text or hub cross-links on `/th/`, a rebuild that differs
from the committed output, non-winged-AA header images, broken local asset
paths, or a sitemap that lists anything but `/th/`.
