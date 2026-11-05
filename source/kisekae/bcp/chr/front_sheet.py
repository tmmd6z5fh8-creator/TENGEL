# 見なおし用：前に 重ねる 動かない 物（occl.png：緑）と キャラの 絵の ふち（水色）を 絵 ぜんたいで ならべる
#   python3 front_sheet.py <出す png> <幅> <chr の 出力> …
import sys, json, os
import numpy as np, cv2
from PIL import Image, ImageDraw
out, TW = sys.argv[1], int(sys.argv[2]); tiles = []
for O in sys.argv[3:]:
    c = json.load(open(os.path.join(O, 'cfg.json')))
    src = np.asarray(Image.open(c['clean']).convert('RGB')).astype(np.float32); H, W = src.shape[:2]
    v = src * 0.75
    if os.path.exists(os.path.join(O, 'occl.png')):
        oc = np.asarray(Image.open(os.path.join(O, 'occl.png')).convert('L')).astype(np.float32)[..., None] / 255
        v = v * (1 - oc * 0.7) + np.array([0, 255, 60]) * oc * 0.7
    for p in c['parts']:
        a = (np.asarray(Image.open(os.path.join(O, p['id'] + '.png')).convert('RGBA'))[..., 3] > 127).astype(np.uint8)
        e = a.astype(bool) & ~cv2.erode(a, np.ones((5, 5), np.uint8)).astype(bool); v[e] = (0, 220, 255)
    im = Image.fromarray(np.clip(v, 0, 255).astype(np.uint8)); s = TW / W; im = im.resize((TW, int(H * s)), Image.LANCZOS)
    ImageDraw.Draw(im).text((4, 4), os.path.basename(O), fill=(255, 255, 0)); tiles.append(im)
NC = 4; R = (len(tiles) + NC - 1) // NC; th = max(t.height for t in tiles)
S = Image.new('RGB', (NC * (TW + 4), R * (th + 4)), (200, 200, 200))
for k, t in enumerate(tiles): S.paste(t, ((k % NC) * (TW + 4), (k // NC) * (th + 4)))
S.save(out); print(out, S.size)
