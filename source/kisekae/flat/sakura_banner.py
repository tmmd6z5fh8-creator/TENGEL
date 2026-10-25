"""桜（780×320）：満開の桜・若草の丘・舞う花びらは前の r3d/banners/sakura.py のまま（同じ乱数の順）、
   馬だけ描き直す → 馬らしい形の、ぺたっとした色の競走馬（第2版・horse_flat）：桜の下に立つ白い馬（桜色のたてがみ・耳もとの桜の花かざり・桜色の布）
   python3 flat/sakura_banner.py <出力.webp>"""
import sys, os, math
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
sys.path.insert(0, HERE)
from style2d import *
from cute_themes import draw_cute

W, Hh = 780, 320
out = sys.argv[1]
rng = np.random.default_rng(21)

# 空・遠くの丘
img = grad_v(Hh, W, [(0, '#BFE0F4'), (0.55, '#F3EEF6'), (1, '#FDEFF4')])
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
hill = 205 + 18 * np.sin(xx / 120 + 1.2) + 10 * np.sin(xx / 47)
img = over(img, hexc('#CFE3C8'), np.clip((yy - hill) / 2 + .5, 0, 1) * 0.9)
img = over(img, hexc('#B5D69A'), np.clip((yy - (250 + 8 * np.sin(xx / 90))) / 2 + .5, 0, 1))
img = over(img, hexc('#9CC97C'), np.clip((yy - (290 + 5 * np.sin(xx / 60 + 2))) / 2 + .5, 0, 1))

# 桜の木（左と右の上から枝がのびる）
CANOPY = [(90, 60, 120, 260), (20, 140, 70, 90), (210, 20, 80, 120), (700, 40, 120, 260), (770, 150, 60, 70), (560, 10, 70, 80)]   # 花の かたまり（中心 x, y, 半径, 数）


def tree(img, x0, y0, side, seed):
    """幹（150）と 太い枝 5本は 前と 同じ 乱数で 形を 決める。そのあと、枝の 先から 細い 枝を 花の かたまりの 中へ のばす（別の 乱数・2026/10/25）：
       前は 枝の 先が 花の 下の 空で 終わっていて、木と 花の あいだが あいていた（まさちゃん「桜の木と桜の花との距離が長いから違和感なく繋げて！」）。
       2026/10/25 その2（まさちゃん「左側の黄丸のところ、桜の花まで木が届いていないから違和感なく届かせて、右側の青丸の枝いらないから消して！」）：
       - 左の木（side 1）：幹の 先を 花の 中まで のばし（細く なって 花に 消える）、低い 枝も ふくめて 5本 ぜんぶの 先から 細い 枝を 花の 方へ。
         幹の 先にも 細い 枝。花は 呼び出し元が 幹の 先の まわり（EXTRA）と 細い 枝の 先・まん中に 足す
       - 右の木（side -1）：先が 低い 枝（y > 175・馬の しっぽへ 長く のびていた 2本）は 描かない（乱数の 順は 同じ）
       返り値の tips は 細い 枝の 先と 幹の 先（ここに 花の かたまりを 足す）"""
    r = np.random.default_rng(seed)
    polys = []
    pts = flow((x0, y0), math.radians(-90 + side * 12), 150, 10, rng=r, wave=0.6)
    polys.append(lock_poly(pts, 30, 12))
    branches = []
    for k in range(5):
        j = int(len(pts) * r.uniform(.35, .9))
        a = math.radians(-90 + side * r.uniform(25, 70))
        b = flow(pts[j], a, r.uniform(60, 130), 8, rng=r, wave=0.8, phase=k)
        wdt = r.uniform(7, 12)
        if side < 0 and b[-1][1] > 175:                    # 右の木の 低い 枝は 描かない
            continue
        polys.append(lock_poly(b, wdt, 2))
        branches.append((b, a, wdt))
    r2 = np.random.default_rng(seed + 100)
    tips = []
    if side > 0:                                           # 左の木：幹の 先を 花の 中へ（12 → 4 に 細く）。先に 細い 枝 2本
        ext = flow(pts[-1], math.radians(-90 + side * 12), 44, 5, rng=r2, wave=0.5, phase=2)
        polys.append(lock_poly(ext, 12.5, 4))
        tips.append(tuple(ext[-1]))
        for m_, da in enumerate((-28, 22)):
            e = flow(ext[-2], math.radians(-90 + da), r2.uniform(30, 44), 5, rng=r2, wave=0.7, phase=m_)
            polys.append(lock_poly(e, 3.0, 1.4))
            tips.append(tuple(e[-1]))
    for k, (b, a, wdt) in enumerate(branches):
        if side < 0 and b[-1][1] > 175:                    # （右の木で 描かなかった 枝には 来ない）
            continue
        # 枝の 先から、いちばん 近い 花の かたまりの 方へ 少し 向きを 変えて、細い 枝を 2本：長い 1本（花の 中まで）と 短い 1本
        cx, cy = min(CANOPY, key=lambda c: (c[0] - b[-1][0]) ** 2 + (c[1] - b[-1][1]) ** 2)[:2]
        to_c = math.atan2(cy - b[-1][1], cx - b[-1][0])
        a_c = a + 0.5 * math.atan2(math.sin(to_c - a), math.cos(to_c - a))          # 枝の 向きと 花への 向きの まん中
        low = b[-1][1] > 175                               # 左の木の 低い 枝：長い 細い 枝は 少し 長く（花まで とどくように）
        for m_, (da, L) in enumerate(((math.radians(r2.uniform(-6, 6)), r2.uniform(85, 125) + (25 if low else 0)), (side * math.radians(r2.uniform(14, 30)), r2.uniform(40, 70)))):
            e = flow(b[-1], a_c + da, L, 7, rng=r2, wave=0.7, phase=k + m_)
            polys.append(lock_poly(e, 2.6 if m_ else 3.4, 1.4))
            tips.append(tuple(e[-1]))
            if m_ == 0:
                tips.append(tuple(e[len(e) // 2]))
    m = poly_aa((Hh, W), polys)
    img = over(img, hexc('#5B3B33'), m)
    return img, pts, tips

img, t1, tips1 = tree(img, 70, 330, 1, 3)
img, t2, tips2 = tree(img, 760, 330, -1, 4)
# 花のかたまり
blossom = np.zeros((Hh, W), np.float32)
shade = np.zeros((Hh, W), np.float32)
for cx, cy, rr, n in CANOPY:
    for i in range(n):
        a = rng.uniform(0, 2 * math.pi); d = rr * math.sqrt(rng.random())
        x, y = cx + math.cos(a) * d * 1.2, cy + math.sin(a) * d * 0.75
        r0 = rng.uniform(6, 13)
        cv2.circle(blossom, (int(x * 4), int(y * 4)), int(r0 * 4), 1.0, -1, cv2.LINE_AA, shift=2)
        cv2.circle(shade, (int((x + 3) * 4), int((y + 4) * 4)), int(r0 * 4), 1.0, -1, cv2.LINE_AA, shift=2)
# 細い 枝の 先と まん中に 小さな 花の かたまり（枝が 花の 中に 消える・木と 花が つながる。別の 乱数＝上の かたまりは 前と 同じ）
# ＋ 左の木の 幹の 先の まわりの かたまり（EXTRA・2026/10/25 その2：幹が 花の 中へ 入って 見える）
EXTRA = [(110, 160, 42, 60)]
rng_t = np.random.default_rng(221)
for (cx, cy, rr, n) in [(x, y, 30, 34) for (x, y) in tips1 + tips2] + EXTRA:
    for i in range(n):
        a = rng_t.uniform(0, 2 * math.pi); d = rr * math.sqrt(rng_t.random())
        x, y = cx + math.cos(a) * d * 1.15, cy + math.sin(a) * d * 0.8
        r0 = rng_t.uniform(6, 12)
        cv2.circle(blossom, (int(x * 4), int(y * 4)), int(r0 * 4), 1.0, -1, cv2.LINE_AA, shift=2)
        cv2.circle(shade, (int((x + 3) * 4), int((y + 4) * 4)), int(r0 * 4), 1.0, -1, cv2.LINE_AA, shift=2)
blossom = np.clip(blossom, 0, 1); shade = np.clip(shade, 0, 1)
img = over(img, hexc('#E99AB4'), shade * 0.9)
img = over(img, hexc('#F7C3D3'), blossom)
hl = np.zeros((Hh, W), np.float32)
for i in range(420):
    x, y = rng.uniform(0, W), rng.uniform(0, 200)
    if blossom[int(min(y, Hh - 1)), int(min(x, W - 1))] > .5:
        cv2.circle(hl, (int(x * 4), int(y * 4)), int(rng.uniform(2, 4.5) * 4), 1.0, -1, cv2.LINE_AA, shift=2)
img = over(img, hexc('#FFE8EF'), np.clip(hl, 0, 1) * blossom)

# かわいい競走馬（flat/cute_themes.py・桜の下に立つ白い馬（桜色のたてがみ・耳もとの桜の花かざり・桜色の布））
if os.environ.get('CUTE_NO_HORSE') != '1':
    img = draw_cute(img, 'sakura', W, Hh)
# 舞う花びら（手前）
pet = np.zeros((Hh, W), np.float32)
pet2 = np.zeros((Hh, W), np.float32)
for i in range(70):
    x, y = rng.uniform(0, W), rng.uniform(0, Hh)
    s = rng.uniform(3, 7); a = rng.uniform(0, 180)
    tgt = pet if rng.random() < .7 else pet2
    cv2.ellipse(tgt, (int(x * 4), int(y * 4)), (int(s * 4), int(s * 2.2)), a, 0, 360, 1.0, -1, cv2.LINE_AA, shift=2)
img = over(img, hexc('#F9B9CD'), np.clip(pet, 0, 1))
img = over(img, hexc('#FFDCE6'), np.clip(pet2, 0, 1))
save_webp(img, out)
print(out)
