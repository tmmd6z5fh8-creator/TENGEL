import sys, pickle
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from dp_env import ROOT
import numpy as np
from PIL import Image, ImageDraw
import physics as PH
Wd = PH.build()
res = pickle.load(open(ROOT + '/out/look/sims.pkl', 'rb'))['res']
K = 1500; box = (-0.5, 0.5, -0.36, 0.42)
W, H = int((box[1] - box[0]) * K), int((box[3] - box[2]) * K)
T = lambda x, y: ((x - box[0]) * K, (box[3] - y) * K)
tiles = []
for cup in range(4):
    rs = [r for r in res if r['cup'] == cup][:6]
    im = Image.new('RGB', (W, H), 'white'); dr = ImageDraw.Draw(im)
    for s in Wd['S']:
        dr.line((T(s[0], s[1]), T(s[2], s[3])), fill=(120, 120, 120), width=3)
    cols = [(220, 40, 40), (30, 110, 220), (20, 150, 60), (200, 120, 0), (160, 60, 200), (0, 160, 170)]
    for r, c in zip(rs, cols):
        pts = [T(x, y) for x, y in zip(r['x'], r['y'])]
        dr.line(pts, fill=c, width=3)
        x, y = T(r['x'][-1], r['y'][-1]); rr = PH.R * K
        dr.ellipse((x - rr, y - rr, x + rr, y + rr), outline=c, width=2)
    dr.text((10, 10), f'cup {cup}  n={len([r for r in res if r["cup"] == cup])}', fill=(0, 0, 0))
    tiles.append(im.resize((W // 2, H // 2), Image.LANCZOS))
sheet = Image.new('RGB', (W, H), 'white')
for i, t in enumerate(tiles): sheet.paste(t, ((i % 2) * (W // 2), (i // 2) * (H // 2)))
sheet.save(ROOT + '/out/look/simview.png'); print(sheet.size)
