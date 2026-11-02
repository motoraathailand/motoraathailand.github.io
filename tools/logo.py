#!/usr/bin/env python3
"""python3 tools/logo.py SRC.jpg — regenerate logo/favicon/apple-touch/og from the master logo (black line art on white).
Line art -> alpha (black for light mode, white for dark mode); favicon/apple/og use the original on white."""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
src = sys.argv[1]
g = Image.open(src).convert('L'); a = np.array(g)
ink = a < 160; ys, xs = np.where(ink)
x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
def crop(box, pad):
    l, t, r, b = box
    return g.crop((l - pad, t - pad, r + pad, b + pad))
def lineart(img, color):
    arr = np.array(img).astype(float)
    alpha = np.clip((255 - arr) / 255 * 1.15, 0, 1)  # slight boost keeps hairlines crisp
    out = np.zeros(arr.shape + (4,), np.uint8); out[..., :3] = color; out[..., 3] = (alpha * 255).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')
full = crop((x0, y0, x1, y1), 8)
full = full.resize((1000, round(full.height * 1000 / full.width)), Image.LANCZOS)  # 1000px wide: crisp up to ~3x on a 340px hero
lineart(full, 0).save('icons/logo.png', optimize=True)
lineart(full, 255).save('icons/logo-dark.png', optimize=True)
# winged AA only (no arched text) for small icons: ink below the text arc
wy = np.where(ink[:, :].any(axis=1))[0]
rows = ink.any(axis=1); gaps = []
prev = None
for y in range(y0, y1 + 1):
    if rows[y] and prev is not None and y - prev > 40: gaps.append((prev, y))
    if rows[y]: prev = y
wy0 = gaps[-1][1] if gaps else y0
wm = ink[wy0:y1 + 1]; xs2 = np.where(wm.any(axis=0))[0]
wing = (xs2.min(), wy0, xs2.max(), y1)
def square(box, size, padfrac, bg=255):
    l, t, r, b = box; w, h = r - l, b - t; s = max(w, h) * (1 + 2 * padfrac)
    cx, cy = (l + r) / 2, (t + b) / 2
    im = Image.new('L', (int(s), int(s)), bg)
    src_img = g.crop((int(cx - s / 2), int(cy - s / 2), int(cx + s / 2), int(cy + s / 2)))
    return src_img.resize((size, size), Image.LANCZOS)
from PIL import ImageFilter
cx = (wing[0] + wing[2]) // 2
def small_icon(box, size, padfrac, thick, blank_above=None):
    l, t, r, b = box; s = int(max(r - l, b - t) * (1 + 2 * padfrac)); cy = (t + b) // 2
    im = g.copy()
    if blank_above: im.paste(255, (0, 0, im.width, blank_above))  # drop the arched text
    im = im.crop((cx - s // 2, cy - s // 2, cx + s // 2, cy + s // 2)).filter(ImageFilter.MinFilter(thick))  # thicken hairlines
    return im.resize((size, size), Image.LANCZOS).convert('RGB')
# 192 / apple-touch: whole winged AA, hairlines thickened; 32: centre AA with wing roots only (legible at 32px)
small_icon(wing, 192, 0.05, 9).save('icons/favicon-192.png', optimize=True)
small_icon(wing, 180, 0.05, 9).save('icons/apple-touch-icon.png', optimize=True)
core = (cx - 290, wing[1], cx + 290, wing[3])
small_icon(core, 32, 0.03, 13, blank_above=wing[1] - 20).save('icons/favicon-32.png', optimize=True)
# og 1200x630
og = Image.new('RGB', (1200, 630), 'white')
lg = full.copy(); lg.thumbnail((560, 560), Image.LANCZOS)
og.paste(lg, (50, (630 - lg.height) // 2))
d = ImageDraw.Draw(og)
bold = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 56)
small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 28)
d.text((650, 210), 'All our apps,', font=bold, fill=(17, 17, 17)); d.text((650, 285), 'in one place', font=bold, fill=(17, 17, 17))
d.text((650, 385), 'motoraathailand.github.io', font=small, fill=(110, 110, 115))
og.save('assets/og.jpg', quality=90, optimize=True)
print('full', full.size, 'wing', wing)
