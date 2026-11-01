# MOTOR AA hub

One landing page (https://motoraathailand.github.io/) that lists every MOTOR AA app and links each one to its own introduction page.
Static, no ads, no trackers, no external requests. Languages th/en/ko/zh/hi (`?lang=` > saved choice > browser language > English).

- `tools/build.py` renders `index.html` + `assets/strings.js` from the app list and strings (`python3 tools/build.py`; add `--fonts` to rebuild font subsets).
- Apps with a live intro page (`live=True` in `tools/build.py`) get a link card. Others are shown as "Coming soon" without a link. Flip `live` and set `url` when an app's intro page goes live, then rebuild.
- `motion.css` / `motion.js` are byte copies of the shared motion standard. Icons in `icons/` are copies from each app's own site/assets (the hub never hot-links other sites' files).
- Contact: motoraathailand@gmail.com. Fonts: IBM Plex (OFL), Noto subsets (OFL).
