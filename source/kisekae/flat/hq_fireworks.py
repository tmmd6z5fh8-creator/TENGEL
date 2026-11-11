# 花火の 馬（光の 線で えがいた 馬：足す光・光の 粒 8組）：いまと 同じ 絵を 1.5倍の 細かさ（iPhone の 3倍の 画面に ぴったり）で
#   第4.157版（まさちゃん 2026/11/12 04:20「Aにして！あと、課金の壁紙は全部馬の画質が悪いから同じように画質を上げてほしい！」＝馬の 絵を 画面の 3倍に。
#   競馬新聞・勝負服・夕焼け〈第4.156版〉の つづき）
#   花火の 馬は 光の 線を 4倍の 紙に 描いて 1倍に 小さく して いる（fireworks_horse.Light）ので、同じ 紙（同じ 乱数・同じ 線）を 1.5倍に 小さく する。
#   ・まわりの 光（ぼかし 4つ）と きらめき（十字の 光）は 1倍の 式を 1.5倍の 画素の 上で（ぼかしの 広さ 1.5倍・きらめきは 同じ 式を 細かい 点で）
#   ・夜空・花火 4つ・ちょうちんは いまの 絵（1倍）を なめらかに 広げた もの（＝いま 画面に 出て いる 見え方と 同じ：馬 だけ 高画質）
#   ・足す光 ＝「馬を 描いた 絵 − 描く 前の 絵」（fireworks_banner.layers と 同じ。ちょうちんの 手前・うしろも 同じ）
#   ・光の 粒 8組の 分け方は いまの 絵（fireworks_blobs.json の scatter）の 分け方を そのまま 広げて 使う（組ごとの 光の 割合が いまの 画面と 同じ ＝ 散り方は かわらない）。
#     8組を 足すと 1.5倍の 足す光と 1つも ちがわない（あまりを 大きい 順に 配る）
#   python3 flat/hq_fireworks.py <出す フォルダ>
#     → fireworks_horse_hq.webp（馬 だけ・8組を 横に ならべた 1まい・1.5倍・ロスなし）
#        fireworks_bursts.webp（花火 4つ だけ：いまの 絵から 馬の 段を 切り落とした もの・1倍の まま・ロスなし＝画素は 1つも かわらない）
#        fireworks_horse_1x.png／fireworks_horse_15.png（足した 絵：いまの 作り方と 1.5倍・見くらべる 用）
import os, sys, json, math
import numpy as np, cv2
from PIL import Image
K = os.environ.get('HQ_K') or os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, K + '/flat'); sys.path.insert(0, K)      # HQ_K＝kisekae を まるごと 写した 作業用の フォルダ（3D の 下絵を r3d/tmp に 書く ので、写しで 走らせると リポジトリが よごれない）
import fireworks_horse as FH, fireworks_banner as FB
from style2d import blur
OUT = 1.5; W, Hh = FB.W, FB.Hh; W2, H2 = int(W * OUT), int(Hh * OUT); NCLS = 8
BLOBS = os.environ.get('HQ_BLOBS') or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'ios', 'kisekae_blobs')
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
lay = json.load(open(K + '/fireworks_layers.json')); sw, sh = lay['sheet']
e = lay['layers'][4]; assert e['kind'] == 'horse' and len(lay['layers']) == 5
x0, y0, w, h = e['rect']; hy = e['sheet_y']; assert hy + h == sh, 'horse must be the last row of the sheet'
for v in (x0, y0, w, h):
    assert v % 2 == 0
up = lambda a: cv2.resize(a, (W2, H2), interpolation=cv2.INTER_LINEAR)        # 画面が 広げる のと 同じ（なめらかに）

# ---- 馬を 描く 前の 絵（夜空・星・花火 4つ：fireworks_banner.compose と 同じ 順・同じ 乱数）と ちょうちん（かける 数・足す 色）
rng = np.random.default_rng(91); img = FB.sky(rng)
for (cx, cy, r, col) in FB.BURSTS:
    ang = FB.ray_angles(rng); core, g = FB.burst(ang, cx, cy, r, col); img = FB.add_burst(img, core, g)
B = img.astype(np.float32)
Cm = FB.lanterns(np.zeros_like(B)); Tm = FB.lanterns(np.ones_like(B)) - Cm       # ちょうちんを 重ねる ＝ 絵 × Tm ＋ Cm
assert float(np.abs(FB.lanterns(B.copy()) - (B * Tm + Cm)).max()) < 1e-5

# ---- 馬（1倍：いまの 作り方）。4倍の 紙と きらめきの 場所を 取って おく
rec = {'fl': []}
_down, _flare = FH.Light.down, FH.flare


def down(self):
    rec['lt'] = self
    return _down(self)


def flare(add, x, y, L, col, k=1.0, ang=0.0, thin=0.55):
    rec['fl'].append((float(x), float(y), float(L), np.asarray(col, np.float32).copy(), float(k), float(ang), float(thin)))
    return _flare(add, x, y, L, col, k, ang, thin)


FH.Light.down, FH.flare = down, flare
H1 = FH.light_horse(B.copy(), W, Hh)
FH.Light.down, FH.flare = _down, _flare
layer = lambda H, B_, T, C: np.clip(np.clip(H * T + C, 0, 1) - np.clip(B_ * T + C, 0, 1), 0, 1)
D1 = layer(H1, B, Tm, Cm)
assert float(np.abs(np.clip(H1 * Tm + Cm, 0, 1) - FB.compose()).max()) < 1e-5, 'not the same picture as fireworks_banner.compose'


def flare_k(add, x, y, L, col, k, ang, thin, s):
    """fireworks_horse.flare と 同じ 式を s倍の 画素の 上で（画素の まん中の 場所を 1倍の 場所に 直して 計算）"""
    Hk, Wk = add.shape[:2]
    r = (int(L * 1.6) + 4) * s
    xc, yc = (x + 0.5) * s - 0.5, (y + 0.5) * s - 0.5
    xa, xb, ya, yb = max(0, int(xc - r)), min(Wk, int(xc + r) + 2), max(0, int(yc - r)), min(Hk, int(yc + r) + 2)
    if xa >= xb or ya >= yb:
        return
    yy, xx = np.mgrid[ya:yb, xa:xb].astype(np.float32)
    dx, dy = (xx + 0.5) / s - 0.5 - x, (yy + 0.5) / s - 0.5 - y
    inside = (np.abs(dx) <= int(L * 1.6) + 4.5) & (np.abs(dy) <= int(L * 1.6) + 4.5)      # 1倍の 絵は この 四角の 中 だけ 足して いる
    ca, sa = math.cos(ang), math.sin(ang)
    u, v = dx * ca + dy * sa, -dx * sa + dy * ca
    ray = np.exp(-(v / thin) ** 2) * np.clip(1 - np.abs(u) / L, 0, 1) ** 2.2 + np.exp(-(u / thin) ** 2) * np.clip(1 - np.abs(v) / L, 0, 1) ** 2.2
    rr = np.sqrt(dx ** 2 + dy ** 2)
    m = (ray * 0.9 + np.exp(-(rr / (0.9 + L * 0.06)) ** 2) * 1.2 + np.exp(-(rr / (L * 0.35)) ** 2) * 0.25) * inside
    add[ya:yb, xa:xb] += m[..., None] * np.asarray(col, np.float32) * k


# ---- 馬（1.5倍）：同じ 4倍の 紙を 1.5倍へ
lt = rec['lt']
f15 = lambda m: cv2.resize(m, (W2, H2), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
core, glow, ca_ = f15(lt.core), f15(lt.glow), f15(lt.a)
gl = blur(glow, 1.0 * OUT) * 0.9 + blur(glow, 3.0 * OUT) * 0.6 + blur(glow, 8.0 * OUT) * 0.36 + blur(glow, 18.0 * OUT) * 0.15
B2, T2, C2 = up(B), up(Tm), up(Cm)
H2_ = (B2 + gl) * (1 - ca_[..., None] * 0.92) + core * 0.92
add = np.zeros((H2, W2, 3), np.float32)
for (x, y, L, col, k, ang, thin) in rec['fl']:
    flare_k(add, x, y, L, col, k, ang, thin, OUT)
H2_ = H2_ + add
D2 = layer(H2_, B2, T2, C2)
X2, Y2, w2, h2 = (int(v * OUT) for v in (x0, y0, w, h))
d1 = D1[y0:y0 + h, x0:x0 + w]; d2 = D2[Y2:Y2 + h2, X2:X2 + w2]
outside = D2.copy(); outside[Y2:Y2 + h2, X2:X2 + w2] = 0
print('light outside the rect (x255):', round(float(outside.max()) * 255, 2), '/ 1x:', round(float(np.delete(D1.reshape(Hh, W, 3), np.s_[y0:y0 + h], 0).max()) * 255, 2))

# ---- 光の 粒 8組：いまの 絵の 分け方を 広げる
S = np.asarray(Image.open(f'{BLOBS}/{json.load(open(K + "/fireworks_blobs.json"))["scatter"]}.webp').convert('RGB'))
assert S.shape == (sh, sw * NCLS, 3), S.shape
g1 = [S[hy:hy + h, g * sw:g * sw + w].astype(np.float32) / 255 for g in range(NCLS)]
upt = lambda a: cv2.resize(a, (w2, h2), interpolation=cv2.INTER_LINEAR)
gu = np.stack([upt(a).sum(-1) for a in g1]); tot = gu.sum(0)
wts = np.where(tot > 1e-6, gu / np.maximum(tot, 1e-6), 1.0 / NCLS)                   # (8, h2, w2)：足すと 1
T = np.rint(d2 * 255).astype(np.int32)                                              # 1.5倍の 足す光（8bit）
v = T[None] * wts[..., None]; fl_ = np.floor(v + 1e-9).astype(np.int32); rem = T - fl_.sum(0)
rank = np.argsort(np.argsort(-(v - fl_), axis=0, kind='stable'), axis=0, kind='stable')
parts = fl_ + (rank < rem[None]).astype(np.int32)
assert (parts.sum(0) == T).all() and parts.min() >= 0 and parts.max() <= 255
sheet = np.zeros((h2, w2 * NCLS, 3), np.uint8)
for g in range(NCLS):
    sheet[:, g * w2:(g + 1) * w2] = parts[g]
Image.fromarray(sheet).save(f'{out}/fireworks_horse_hq.webp', 'WEBP', lossless=True, method=6)
back = np.asarray(Image.open(f'{out}/fireworks_horse_hq.webp').convert('RGB')); assert (back == sheet).all(), 'lossless?'
Image.fromarray(S[:hy]).save(f'{out}/fireworks_bursts.webp', 'WEBP', lossless=True, method=6)
back = np.asarray(Image.open(f'{out}/fireworks_bursts.webp').convert('RGB')); assert (back == S[:hy]).all(), 'lossless?'
Image.fromarray(np.rint(sum(g1) * 255).clip(0, 255).astype(np.uint8)).save(f'{out}/fireworks_horse_now.png')      # いま 入って いる 絵（8組を 足した もの）
Image.fromarray(np.rint(d1 * 255).astype(np.uint8)).save(f'{out}/fireworks_horse_1x.png')
Image.fromarray(T.astype(np.uint8)).save(f'{out}/fireworks_horse_15.png')
json.dump(dict(rect=[X2, Y2, w2, h2], cell=[w2, h2], groups=NCLS, scale=OUT, bursts=[sw * NCLS, hy]), open(f'{out}/fireworks_horse_hq.json', 'w'))
print('sizes', {n: os.path.getsize(f'{out}/{n}') for n in ('fireworks_horse_hq.webp', 'fireworks_bursts.webp')}, 'sheet', sheet.shape, 'bursts', S[:hy].shape)
# 入れ方：python3 flat/hq_install.py fireworks <出す フォルダ>（手元の 絵の フォルダ ios/kisekae_blobs と 台帳へ。前の 絵は 消さない）
