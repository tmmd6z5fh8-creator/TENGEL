"""夕焼け（780×320）：空・夕日・雲の筋・丘・草・鳥は前の r3d/banners/sunset.py のまま（同じ乱数の順）、
   馬だけ描き直す → 夕日を背に丘をかける馬のシルエット（flat/sunset_horse.py：細い毛の束のたてがみとしっぽ・夕日がわのふちの光）
   python3 flat/sunset_banner.py <出力.webp>
   壁紙の動き（flat/sunset_run.py）のために、部品を べつべつに使える：sky()（空・夕日のまわりの光・雲の筋。with_sun で夕日の丸も）・
   sun_alpha()（夕日の丸）・hill_alpha()（丘）・grass_alpha()（草）・birds()（鳥）。banner() が いつもの絵（前と1バイトもちがわない）"""
import sys, os, math
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sunset_horse import *

W, Hh = 780, 320
SUN_C, SUN_R = (520, 236), 64          # 夕日のまん中と半径（sunset_horse.SUN と同じ）
INK = '#2A1235'                        # 丘・草・鳥の色
SUN_COL = '#FFE7A6'


def grid():
    return np.mgrid[0:Hh, 0:W].astype(np.float32)


def sun_alpha():
    return soft_circle(Hh, W, SUN_C[0], SUN_C[1], SUN_R, 1.2)


def sky(with_sun=True):
    """空のグラデーション・夕日のまわりの光（足す光）・夕日の丸（with_sun）・うすい雲の筋"""
    yy, xx = grid()
    img = grad_v(Hh, W, [(0, '#3B1E5E'), (0.32, '#8E3B78'), (0.58, '#F0663F'), (0.78, '#FFB15A'), (1, '#FFD98A')])
    sx, sy = SUN_C
    glow = np.exp(-np.sqrt((xx - sx) ** 2 + ((yy - sy) * 1.3) ** 2) / 120)
    img = img + glow[..., None] * hexc('#FFB46A') * 0.45
    if with_sun:
        img = over(img, hexc(SUN_COL), sun_alpha())
    for y0, w_, c in [(70, 4, '#C2507A'), (96, 3, '#D8607A'), (128, 3, '#F08A5E'), (152, 2.5, '#FFB37A')]:
        band = np.exp(-((yy - y0 - 6 * np.sin(xx / 90 + y0)) / w_) ** 2) * (0.5 + 0.5 * np.sin(xx / 37 + y0))
        img = over(img, hexc(c), np.clip(band, 0, 1) * 0.6)
    return img


def hill_alpha():
    yy, xx = grid()
    hill = 262 - 34 * np.exp(-((xx - 480) / 260) ** 2) + 5 * np.sin(xx / 30)
    return np.clip((yy - hill) / 1.5 + .5, 0, 1)


def grass_alpha(rng):
    gr = np.zeros((Hh, W), np.float32)
    for i in range(260):
        x = rng.uniform(0, W); y = 262 - 34 * math.exp(-((x - 480) / 260) ** 2) + 5 * math.sin(x / 30) + 2
        h = rng.uniform(6, 16)
        cv2.line(gr, (int(x * 16), int(y * 16)), (int((x + rng.uniform(-4, 4)) * 16), int((y - h) * 16)), 1.0, 1, cv2.LINE_AA, shift=4)
    return np.clip(gr, 0, 1)


BIRDS = [(120, 70, 8), (150, 58, 6), (176, 76, 7), (650, 60, 7)]


def bird_alpha(x, y, s, w=W, h=Hh):
    pts = np.array([(x - s, y), (x - s * .45, y - s * .5), (x, y), (x + s * .45, y - s * .5), (x + s, y)])
    m = np.zeros((h * 4, w * 4), np.uint8)
    cv2.polylines(m, [np.round(pts * 64).astype(np.int32)], False, 255, 5, cv2.LINE_AA, shift=4)
    return cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255


def birds(img):
    for (x, y, s) in BIRDS:
        img = over(img, hexc(INK), bird_alpha(x, y, s))
    return img


def banner(horse=True):
    """いつもの絵（空 → 丘 → 草 → 馬 → 鳥）"""
    rng = np.random.default_rng(81)
    img = sky()
    img = over(img, hexc(INK), hill_alpha())
    img = over(img, hexc(INK), grass_alpha(rng))
    if horse:                                                           # 走る馬のシルエット（左向き）＋夕日がわのふちの光
        img = draw(img, W, Hh)
    return birds(img)


if __name__ == '__main__':
    out = sys.argv[1]
    save_webp(banner(os.environ.get('SUNSET_NO_HORSE') != '1'), out)
    print(out)
