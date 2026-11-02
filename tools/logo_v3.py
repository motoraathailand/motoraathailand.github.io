#!/usr/bin/env python3
"""python3 tools/logo_v3.py SRC.jpg — transparent full logo + winged-AA mark (light/dark) from line art on white."""
import sys, numpy as np
from PIL import Image
g = Image.open(sys.argv[1]).convert('L'); a = np.array(g)
ink = a < 160
rows = np.where(ink.any(axis=1))[0]
# split into row bands separated by gaps > 40px: [text-top, wings, text-bottom]
bands = []; s = rows[0]; p = rows[0]
for y in rows[1:]:
    if y - p > 40: bands.append((s, p)); s = y
    p = y
bands.append((s, p)); print('bands', bands)
def lineart(img, color):
    arr = np.array(img).astype(float)
    alpha = np.clip((255 - arr) / 255 * 1.15, 0, 1)
    out = np.zeros(arr.shape + (4,), np.uint8); out[..., :3] = color; out[..., 3] = (alpha * 255).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')
def crop_ink(y0, y1, pad, width):
    sub = ink[y0:y1 + 1]; xs = np.where(sub.any(axis=0))[0]
    box = (xs.min() - pad, y0 - pad, xs.max() + pad + 1, y1 + pad + 1)
    im = g.crop(box); im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    return im
LIGHT, DARK = 0, 242
full = crop_ink(bands[0][0], bands[-1][1], 14, 900)
# full logo is a circle-ish; use the ink extents of all bands
sub = ink[bands[0][0]:bands[-1][1] + 1]
full = g.crop((np.where(ink.any(axis=0))[0].min() - 14, bands[0][0] - 14, np.where(ink.any(axis=0))[0].max() + 15, bands[-1][1] + 15))
full = full.resize((900, round(full.height * 900 / full.width)), Image.LANCZOS)
lineart(full, LIGHT).save('icons/logo.png', optimize=True); lineart(full, DARK).save('icons/logo-dark.png', optimize=True)
mark = crop_ink(bands[1][0], bands[1][1], 10, 600)
lineart(mark, LIGHT).save('icons/logo-mark.png', optimize=True); lineart(mark, DARK).save('icons/logo-mark-dark.png', optimize=True)
print('full', full.size, 'mark', mark.size)
