# トレーニングセンターの フィールド（朝・夕方・夜）：iPhone 用に まん中の 砂を 少し のばす ＋ 草木を ゆらす 地図（3つの ゆれの 組）
#   python3 field_prep.py <元の 絵の フォルダ（field_morning/evening/night.png）> <出す フォルダ> [のばす 行の 数]
#   出す：tc_field_<朝昼夜>.webp（1052×(1495+のばす)）・tc_sway.png（地図：1/2 の 大きさ・R G B＝ゆれの 組 0〜2 の 重み）・tc_field.json（大きさ・組ごとの 動き）・見本 sway_vis.png
import json, os, sys
import numpy as np, cv2
from PIL import Image
SRC, OUT = sys.argv[1], sys.argv[2]
EXT = int(sys.argv[3]) if len(sys.argv) > 3 else 162
os.makedirs(OUT, exist_ok=True)
NAMES = ('morning', 'evening', 'night')
IM = {n: np.asarray(Image.open(os.path.join(SRC, f'field_{n}.png')).convert('RGB')) for n in NAMES}
H0, W0 = IM['morning'].shape[:2]

# ---- 1) ゆれる 物（元の 絵の px）：[名前, 組, 四角（x0,y0,x1,y1）, 色の 種類, 根もと（下の はしの y：ここから 上ほど 大きく ゆれる）, 根もとの はば（px）, 強さ]
EL = [
    ['左上の 木',     0, (0, 0, 470, 192),      'leaf',   None, 0,   1.0],
    ['左の 葉',       1, (0, 186, 128, 362),    'leaf',   None, 0,   0.8],
    ['右上の 木',     2, (896, 80, 1052, 340),  'leaf',   None, 0,   1.0],
    ['左の あじさい', 2, (0, 438, 120, 552),    'flower', 552,  70,  0.55],
    ['しげみ 左',     0, (84, 454, 208, 506),   'leaf',   506,  30,  0.35],
    ['しげみ 右',     1, (228, 454, 338, 506),  'leaf',   506,  30,  0.35],
    ['たるの 花 左',  2, (398, 414, 464, 466),  'flower', 462,  26,  0.45],
    ['たるの 花 右',  0, (600, 418, 666, 466),  'flower', 462,  26,  0.45],
    ['右の あじさい', 1, (972, 458, 1052, 566), 'flower', 566,  70,  0.55],
    ['左下の 花',     2, (0, 1240, 270, 1495),  'flower', 1495, 150, 1.0],
    ['右下の 花',     0, (812, 1205, 1052, 1495), 'flower', 1495, 150, 1.0],
]
im = IM['morning']
hsv = cv2.cvtColor(im, cv2.COLOR_RGB2HSV).astype(np.float32)
Hh, S, V = hsv[..., 0] * 2, hsv[..., 1] / 255, hsv[..., 2] / 255
leaf = (Hh >= 52) & (Hh <= 118) & (S > .3) & (V > .42)                    # 黄緑の 葉（屋根の 青みの 緑・山は 入らない）
flower = leaf | (((Hh >= 290) | (Hh <= 16)) & (S > .16) & (V > .5)) | ((Hh >= 235) & (Hh < 290) & (S > .2)) \
    | ((Hh >= 38) & (Hh < 58) & (S > .6) & (V > .7)) | ((S < .14) & (V > .86)) | ((Hh >= 118) & (Hh <= 160) & (S > .3) & (V > .3))
brown = (Hh >= 8) & (Hh <= 40) & (S > .35) & (V < .78)                       # 幹・たる
stone = (S < .12) & (V > .45) & (V < .86)                                    # 下の 石
fence = (S < .16) & (V > .8)                                                 # さく（白）
KIND = {'leaf': leaf, 'flower': flower}
yy, xx = np.mgrid[0:H0, 0:W0].astype(np.float32)
G = np.zeros((3, H0, W0), np.float32)
PIN = np.zeros((H0, W0), np.float32)
for name, grp, (x0, y0, x1, y1), kind, base, bw, amp in EL:
    box = np.zeros((H0, W0), bool); box[y0:y1, x0:x1] = True
    m = (KIND[kind] & box).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)).astype(np.float32)
    w = m * amp
    if base is not None:                       # 根もとは 動かない・上ほど 大きく
        w *= np.clip((base - yy) / max(bw, 1), 0, 1) ** 1.2
    G[grp] = np.maximum(G[grp], w)
    # 動かさない 物（幹・たる・石・さく）：その 物の 四角の まわり
    bx = np.zeros((H0, W0), bool); bx[max(0, y0 - 20):y1 + 20, max(0, x0 - 20):x1 + 20] = True
    PIN = np.maximum(PIN, ((brown | stone | fence) & bx & ~(KIND[kind] & box)).astype(np.float32))
# なめらかに（動きが 切れない）・動かない 物の そばは 小さく
for k in range(3):
    G[k] = cv2.GaussianBlur(G[k], (0, 0), 7)
pinb = cv2.GaussianBlur(cv2.dilate(PIN, np.ones((5, 5), np.uint8)), (0, 0), 3)
G *= np.clip(1 - pinb * 1.6, 0, 1)[None]
G = np.clip(G, 0, 1)

# ---- 2) iPhone 用に まん中の 砂を のばす（行 B0〜B1 を なめらかに のばす：はしは 1倍・まん中ほど のびる）
B0, B1 = 680, 1150
Hn = H0 + EXT
n_in, n_out = B1 - B0, B1 - B0 + EXT
# 元の 行 s（0〜n_in）の のび d(s) = 1 + a·sin²(π s / n_in)（はしで 1・まん中ほど のびる）。出す 行 y'(s) = ∫d → 逆に して 出す 行ごとの 元の 行
a_ = 2 * (n_out - n_in) / n_in
s_ = np.linspace(0, n_in, 20001)
yo = s_ + a_ * (s_ / 2 - n_in / (4 * np.pi) * np.sin(2 * np.pi * s_ / n_in))
src_in = B0 + np.interp(np.arange(n_out, dtype=np.float64), yo, s_)
ymap = np.concatenate([np.arange(B0, dtype=np.float32), src_in.astype(np.float32), np.arange(B1, H0, dtype=np.float32)])
assert len(ymap) == Hn, (len(ymap), Hn)
mapy = np.repeat(ymap[:, None], W0, 1).astype(np.float32); mapx = np.repeat(np.arange(W0, dtype=np.float32)[None], Hn, 0)
for n in NAMES:
    out = cv2.remap(IM[n], mapx, mapy, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    Image.fromarray(out).save(os.path.join(OUT, f'tc_field_{n}.webp'), quality=86, method=6)
    Image.fromarray(out).save(os.path.join(OUT, f'tc_field_{n}.png'))
Gx = np.stack([cv2.remap(G[k], mapx, mapy, cv2.INTER_LINEAR) for k in range(3)], -1)


# ---- 3) 砂に うつる 木の かげ（朝・夕方・夜で ちがう）：左上の 木と 同じ 組（0）で 少し ゆれる
def shadow(n):
    im = np.asarray(Image.open(os.path.join(OUT, f'tc_field_{n}.png')).convert('RGB')).astype(np.float32) / 255
    lum = cv2.GaussianBlur(im.max(-1), (0, 0), 2.5)
    arena = np.zeros((Hn, W0), np.uint8)
    cv2.ellipse(arena, (W0 // 2, B0 + (n_out // 2) + 80), (600, 640), 0, 0, 360, 1, -1)   # 砂の 所（のばした 絵）
    arena[:590] = 0
    k_ = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (91, 91))
    clo = cv2.GaussianBlur(cv2.morphologyEx(lum, cv2.MORPH_CLOSE, k_), (0, 0), 20)
    r = (clo - lum) / np.maximum(clo, 1e-3)
    sh = np.clip((r - .10) / .22, 0, 1) * arena
    sh = cv2.morphologyEx(sh, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    return cv2.GaussianBlur(sh, (0, 0), 6) * .55


# 地図は 1/2（なめらか なので 小さくて よい）・朝昼夜ごと（かげが ちがう）
for n in NAMES:
    Gn = Gx.copy(); Gn[..., 0] = np.clip(np.maximum(Gn[..., 0], shadow(n)), 0, 1)
    Gs = cv2.resize(Gn, (W0 // 2, Hn // 2), interpolation=cv2.INTER_AREA)
    Image.fromarray(np.clip(Gs * 255 + .5, 0, 255).astype(np.uint8), 'RGB').save(os.path.join(OUT, f'tc_sway_{n}.png'), optimize=True)
cfg = {'w': W0, 'h': Hn, 'ext': EXT, 'band': [B0, B1],
       'amp': [5.0, 4.2, 4.6], 'per': [4.6, 3.7, 5.3], 'ph': [0.0, 0.37, 0.71]}
json.dump(cfg, open(os.path.join(OUT, 'tc_field.json'), 'w'), indent=1)
# 見本：地図を 色で
vis = (np.asarray(Image.open(os.path.join(OUT, 'tc_field_morning.png'))).astype(np.float32) * .45)
col = np.array([[255, 60, 60], [60, 255, 60], [60, 120, 255]], np.float32)
for k in range(3):
    vis += Gx[..., k:k + 1] * col[k] * .6
Image.fromarray(np.clip(vis, 0, 255).astype(np.uint8)).resize((W0 // 2, Hn // 2)).save(os.path.join(OUT, 'sway_vis.png'))
print('field', W0, Hn, 'sway map', Gs.shape, [os.path.getsize(os.path.join(OUT, f'tc_sway_{n}.png')) for n in NAMES], 'webp', [os.path.getsize(os.path.join(OUT, f'tc_field_{n}.webp')) for n in NAMES])
