"""勝負服（780×320）：漫画のコマ割りのような勝負服の柄の背景（flat/silks_bg.py）に、
   遊び心のある漫画の馬と騎手（flat/toon_rider.py）：首と足をいっぱいにのばして「とぶように」走る栗毛の馬
   （にらむ目・歯をくいしばった口・鼻から ふんっ の息）と、大きめの頭で低くかがむ騎手（ゴーグル・歯をくいしばった口・とぶ汗）。
   右下へずらした紺のかげ・ひづめのうしろの流線・うしろ足から出るもくもくの空気のかたまり
   python3 flat/silks_banner.py <出力.webp>"""
import sys, os, math
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from toon_rider import *
from flat_horse import to_png
import silks_bg

W, Hh = 780, 320
out = sys.argv[1]
POSE = dict(theta=-3.0, neck_rot=-44.0, head_ang=-20.0,
            fore=dict(L=[-56, -9, -3, 7], R=[-70, -20, -12, -2]),
            hind=dict(L=[-145, -170, -160, -172], R=[-135, -160, -150, -165]),
            tail=[-178, -175])
BOX = (184, 104, 634, 286)


def svg_png(parts, scale=4):
    """SVG の部品 → 1倍の (rgb, alpha)"""
    svg = f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{Hh}' viewBox='0 0 {W} {Hh}'>" + ''.join(parts) + "</svg>"
    tmp = os.path.join(TMP, 'silks_overlay.png')
    to_png(svg, W, Hh, tmp, scale=scale)
    im = cv2.imread(tmp, cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    im = cv2.resize(im, (W, Hh), interpolation=cv2.INTER_AREA)
    a_ = im[..., 3]
    return im[..., :3][..., ::-1] / np.maximum(a_[..., None], 1e-4), a_


# 背景
tmp = os.path.join(TMP, 'silks_bg.png')
to_png(silks_bg.bg_svg(), W, Hh, tmp, scale=2)
bg = cv2.imread(tmp, cv2.IMREAD_UNCHANGED)[..., :3][..., ::-1].astype(np.float32) / 255
img = cv2.resize(bg, (W, Hh), interpolation=cv2.INTER_AREA)

# 馬と騎手
R = render_toon(POSE, BOX, W, Hh, s=3, azim=18, elev=5, name='silks_toon', head_scale=1.32, js=1.35, head_r=0.15)
rgb, a = paint_comic(R, dict(num=1, seed=5, eye=False, mouth=False))
hv = np.asarray(R['hooves'], float) / R['s']


def puffs():
    """うしろ足から出る、もくもくの空気のかたまり（うしろへ小さく）"""
    S = []
    prng = np.random.default_rng(23)
    for k in (2, 3):                                   # うしろ足（HL・HR）
        x, y = hv[k]
        for j in range(3):
            cx, cy = x - 12 - j * 19 + prng.uniform(-2, 2), y + 4 + j * 3.0 + prng.uniform(-1.5, 1.5)
            r0 = 8.6 - j * 2.2
            bl = []
            for i in range(4):
                a_ = i * 1.7 + j
                bl.append((cx + math.cos(a_) * r0 * 0.6, cy + math.sin(a_) * r0 * 0.45, r0 * (0.75 if i else 0.95)))
            S.append("<g fill='#FFF8EA' stroke='#121A33' stroke-width='1.2'>" + ''.join(f"<circle cx='{u:.2f}' cy='{v:.2f}' r='{r:.2f}'/>" for u, v, r in bl) + "</g>")
            S.append("<g fill='#FFF8EA'>" + ''.join(f"<circle cx='{u:.2f}' cy='{v:.2f}' r='{r - 0.6:.2f}'/>" for u, v, r in bl) + "</g>")
    return S


def streaks():
    """ひづめのうしろへ流れる短い線（白・ふちは紺）"""
    S = []
    frng = np.random.default_rng(17)
    for (x, y) in hv[:2]:                              # 前足
        for j in range(3):
            yy_ = y - 4 + j * 4.5 + frng.uniform(-1, 1)
            x1 = x - 9 - j * 3 + frng.uniform(-2, 2)
            L = frng.uniform(18, 30) * (1 - 0.18 * j)
            x0 = x1 - L
            th = 2.6 - 0.5 * j
            d = f"M{x0:.1f} {yy_:.1f} Q{x0 + L * 0.6:.1f} {yy_ - th / 2:.1f} {x1:.1f} {yy_:.1f} Q{x0 + L * 0.6:.1f} {yy_ + th / 2:.1f} {x0:.1f} {yy_:.1f} Z"
            S.append(f"<path d='{d}' fill='#FFFFFF' stroke='#121A33' stroke-width='1.1' stroke-linejoin='round'/>")
    return S


def air_lines():
    """鼻先の前の、風を切る線（白・ふちは紺）"""
    S = []
    mz = np.asarray(R['muzzle'], float) / R['s']
    for (dx, dy, L, ang) in ((16, -20, 22, -28), (24, -8, 26, -16), (20, 14, 20, 22)):
        x0, y0 = mz[0] + dx, mz[1] + dy
        a_ = math.radians(ang)
        x1, y1 = x0 + math.cos(a_) * L, y0 + math.sin(a_) * L
        S.append(f"<path d='M{x0:.1f} {y0:.1f} L{x1:.1f} {y1:.1f}' stroke='#121A33' stroke-width='4.2' stroke-linecap='round'/>"
                 f"<path d='M{x0:.1f} {y0:.1f} L{x1:.1f} {y1:.1f}' stroke='#FFFFFF' stroke-width='2.0' stroke-linecap='round'/>")
    return S


# うしろのもくもく（馬のうしろ）
pr, pa = svg_png(puffs())
img = img * (1 - pa[..., None]) + pr * pa[..., None]
sh = cv2.warpAffine(a, np.float32([[1, 0, 6], [0, 1, 5]]), (W, Hh), flags=cv2.INTER_LINEAR, borderValue=0) * 0.45
img = img * (1 - sh[..., None]) + hexc('#0B1550') * sh[..., None]               # 右下へずらした紺のかげ
img = img * (1 - a[..., None]) + rgb * a[..., None]
# 顔・息・汗・前足の流線（馬の上）
fr, fa = svg_png(face_svg(R) + streaks() + air_lines())
img = img * (1 - fa[..., None]) + fr * fa[..., None]
save_webp(np.clip(img, 0, 1), out)
print(out)
