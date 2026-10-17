"""勝負服（780×320）：漫画のコマ割りのような勝負服の柄の背景（flat/silks_bg.py）に、
   漫画の塗りで描いた、騎手を乗せて走る栗毛の競走馬（flat/comic_rider.py）。右下へずらした紺のかげ・ひづめのうしろの流線
   python3 flat/silks_banner.py <出力.webp>"""
import sys, os, math
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from comic_rider import *
from flat_horse import to_png
import silks_bg

W, Hh = 780, 320
out = sys.argv[1]
POSE = dict(theta=-4.0, neck_rot=-30.0, head_ang=-38.0,
            fore=dict(L=[-88, -38, -45, -30], R=[-118, -5, -125, -155]),
            hind=dict(L=[-112, -145, -120, -140], R=[-50, -95, -62, -38]),
            tail=[-170, -158])
BOX = (214, 90, 628, 310)

# 背景
tmp = os.path.join(TMP, 'silks_bg.png')
to_png(silks_bg.bg_svg(), W, Hh, tmp, scale=2)
bg = cv2.imread(tmp, cv2.IMREAD_UNCHANGED)[..., :3][..., ::-1].astype(np.float32) / 255
img = cv2.resize(bg, (W, Hh), interpolation=cv2.INTER_AREA)

# 馬と騎手
R = render_anime(POSE, BOX, W, Hh, s=3, azim=22, elev=6, name='silks_comic', head_scale=1.12, js=1.25)
rgb, a = paint_comic(R, dict(num=1, seed=5))
sh = cv2.warpAffine(a, np.float32([[1, 0, 6], [0, 1, 5]]), (W, Hh), flags=cv2.INTER_LINEAR, borderValue=0) * 0.45
img = img * (1 - sh[..., None]) + hexc('#0B1550') * sh[..., None]               # 右下へずらした紺のかげ（背景から浮かせる）
img = img * (1 - a[..., None]) + rgb * a[..., None]


# 動きの線（ひづめのまわりの弧・前の空気を切る線）
def fx_svg():
    """ひづめのうしろへ流れる短い線（白・ふちは紺）"""
    S = []
    hv = R['hooves1']
    frng = np.random.default_rng(17)
    for (x, y) in hv:
        for j in range(3):
            yy_ = y - 4 + j * 4.5 + frng.uniform(-1, 1)
            x1 = x - 9 - j * 3 + frng.uniform(-2, 2)
            L = frng.uniform(18, 34) * (1 - 0.18 * j)
            x0 = x1 - L
            th = 2.6 - 0.5 * j
            d = f"M{x0:.1f} {yy_:.1f} Q{x0 + L * 0.6:.1f} {yy_ - th / 2:.1f} {x1:.1f} {yy_:.1f} Q{x0 + L * 0.6:.1f} {yy_ + th / 2:.1f} {x0:.1f} {yy_:.1f} Z"
            S.append(f"<path d='{d}' fill='#FFFFFF' stroke='#121A33' stroke-width='1.1' stroke-linejoin='round' opacity='.95'/>")
    return f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{Hh}' viewBox='0 0 {W} {Hh}'>" + ''.join(S) + "</svg>"


if os.environ.get('SILKS_FX', '1') == '1':
    tmp2 = os.path.join(TMP, 'silks_fx.png')
    to_png(fx_svg(), W, Hh, tmp2, scale=2)
    fx = cv2.imread(tmp2, cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    fx = cv2.resize(fx, (W, Hh), interpolation=cv2.INTER_AREA)
    fa = fx[..., 3:4]
    img = img * (1 - fa) + fx[..., :3][..., ::-1] * fa
save_webp(np.clip(img, 0, 1), out)
print(out)
