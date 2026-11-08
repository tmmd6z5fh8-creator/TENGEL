# トレーニングセンターの フィールド（夕方・夜）の ライトの 地図：ライトごとに 光が 弱く なったり 戻ったり する 所
#   python3 light_prep.py <元の 絵の フォルダ> <出す フォルダ>
#   出す：tc_light_evening.png・tc_light_night.png（1/2 の 大きさ・R＝光の 重み・G＝ライトの 番号×16・B＝弱く なる 深さ）・見本 light_vis_*.png
#   ライトは のばす 行（680〜）より 上 なので、のばした 絵でも 同じ 場所（下に 行を 足す だけ）
import json, os, sys
import numpy as np, cv2
from PIL import Image
SRC, OUT = sys.argv[1], sys.argv[2]
cfg = json.load(open(os.path.join(OUT, 'tc_field.json')))
Hn, W0 = cfg['h'], cfg['w']
# [名前, x, y, 半径 rx, ry, 深さ, 夕方も 光る か]（元の 絵の px）
LAMPS = [
    ['左はしの ランプ', 37, 388, 30, 34, .45, False],
    ['ランプ 1', 147, 390, 34, 40, .45, True],
    ['ランプ 2', 272, 390, 34, 40, .45, True],
    ['ランプ 3', 397, 390, 30, 36, .45, True],
    ['入り口の ランプ 左', 432, 388, 42, 50, .45, True],
    ['入り口の ランプ 右', 637, 388, 42, 50, .45, True],
    ['通路の ランプ 1', 478, 392, 18, 20, .35, False],
    ['通路の ランプ 2', 548, 394, 18, 20, .35, False],
    ['洗い場の 明かり', 930, 418, 118, 96, .38, True],
    ['屋根の 窓 左', 258, 286, 34, 30, .22, False],
    ['屋根の 窓 右', 757, 283, 34, 30, .22, False],
    ['塔の 窓', 532, 205, 28, 22, .2, False],
]
yy, xx = np.mgrid[0:Hn, 0:W0].astype(np.float32)
for tod in ('evening', 'night'):
    im = np.asarray(Image.open(os.path.join(OUT, f'tc_field_{tod}.png')).convert('RGB'))
    hsv = cv2.cvtColor(im, cv2.COLOR_RGB2HSV).astype(np.float32)
    Hh, S, V = hsv[..., 0] * 2, hsv[..., 1] / 255, hsv[..., 2] / 255
    warm = ((Hh >= 14) & (Hh <= 62)).astype(np.float32) * np.clip((S - .12) / .25, 0, 1)
    warm = np.maximum(warm, np.clip((V - .82) / .12, 0, 1))          # ランプの まん中（白っぽく 光って いる 所）も
    R = np.zeros((Hn, W0), np.float32); G = np.zeros_like(R); B = np.zeros_like(R)
    sc = 1.0 if tod == 'night' else .62                               # 夕方は 明るい ので ライトの まわり だけ
    vlo = .42 if tod == 'night' else .78
    for i, (name, cx, cy, rx, ry, depth, eve) in enumerate(LAMPS):
        if tod == 'evening' and not eve:
            continue
        d = np.sqrt(((xx - cx) / (rx * sc)) ** 2 + ((yy - cy) / (ry * sc)) ** 2)
        fall = np.clip(1 - d ** 2, 0, 1) ** 1.5
        lit = np.clip((V - vlo) / (1 - vlo + 1e-3), 0, 1) * warm
        w = fall * lit
        sel = w > R
        R[sel] = w[sel]; G[sel] = i * 16 / 255; B[sel] = depth          # G：ライトの 番号×16（アプリが 1つずつ ゆらす）
    R = cv2.GaussianBlur(R, (0, 0), 1.2)
    out = np.dstack([R, G, B])
    small = cv2.resize(out, (W0 // 2, Hn // 2), interpolation=cv2.INTER_AREA)
    # 番号と 深さは まぜない（いちばん 近い 点）
    small[..., 1:] = cv2.resize(out[..., 1:], (W0 // 2, Hn // 2), interpolation=cv2.INTER_NEAREST)
    Image.fromarray(np.clip(small * 255 + .5, 0, 255).astype(np.uint8), 'RGB').save(os.path.join(OUT, f'tc_light_{tod}.png'), optimize=True)
    vis = im.astype(np.float32) * .4; vis[..., 0] += R * 255 * .9; vis[..., 1] += R * 255 * .5
    Image.fromarray(np.clip(vis[150:520], 0, 255).astype(np.uint8)).save(os.path.join(OUT, f'light_vis_{tod}.png'))
    print(tod, 'lit px', int((R > .05).sum()), os.path.getsize(os.path.join(OUT, f'tc_light_{tod}.png')))
