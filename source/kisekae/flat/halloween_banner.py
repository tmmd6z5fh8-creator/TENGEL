"""ハロウィン（780×320・まさちゃんの指定「壁紙、馬とドクロとドラキュラ、🎃」）：
   むらさきの夜（大きな満月・星・こうもり・遠くの丘の お城・はだかの木）に、左に マントを ひろげる ドラキュラ、
   まん中に 魔女の帽子を かぶった 芦毛の競走馬（むらさきに オレンジのふちの ゼッケン1・こうもり）、
   右と 手前に 光る ジャック・オー・ランタンと かわいい ドクロ。馬は horse_flat・人と物は flat/event_art.py（一から作った形）
   python3 flat/halloween_banner.py <出力.webp>
   HALLOWEEN_BASE=1 python3 flat/halloween_banner.py <出力.webp>   → 動く壁紙の 下の絵（ドラキュラと その影・顔のある かぼちゃ3つ・ドクロなし。
                                                                    どれも ページの SVG で動かす：halloween_wall.py・flat/halloween_run.py）"""
import sys, os, math
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
sys.path.insert(0, HERE)
from style2d import *
from cute_themes import draw_cute
from cute_horse import svg_layer
import event_art as A

W, Hh = 780, 320
out = sys.argv[1]
BASE = os.environ.get('HALLOWEEN_BASE') == '1'      # 動く壁紙の 下の絵（ドラキュラ・顔のある かぼちゃ・ドクロは halloween_wall.py が ページの SVG で 動かす）
PLAIN = os.environ.get('HALLOWEEN_SKY_PLAIN') == '1'   # 星と こうもりも 描かない（halloween_wall.py が ページの SVG で またたかせ・飛ばす。乱数の 順は 同じに 進める）
rng = np.random.default_rng(31)
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)

# 夜空・満月・星
img = grad_v(Hh, W, [(0, '#170B2B'), (0.5, '#3A1C5C'), (0.8, '#6A2F78')])
mx, my = 600, 92
img = over(img, hexc('#FFD98A'), np.exp(-(((xx - mx) ** 2 + (yy - my) ** 2) / (2 * 70.0 ** 2))) * 0.22)
img = over(img, hexc('#FFE8A8'), soft_circle(Hh, W, mx, my, 54, 1.2))
craters = soft_circle(Hh, W, mx - 18, my - 10, 10, 1.0) + soft_circle(Hh, W, mx + 16, my + 14, 7, 1.0) + soft_circle(Hh, W, mx + 20, my - 22, 5, 1.0)
img = over(img, hexc('#F2D488'), np.clip(craters, 0, 1) * soft_circle(Hh, W, mx, my, 52, 1.0) * 0.8)
for i in range(60):
    x, y = rng.uniform(0, W), rng.uniform(0, 150)
    if (x - mx) ** 2 + (y - my) ** 2 < 70 ** 2:
        continue
    r_, a_ = rng.uniform(0.6, 1.4), rng.uniform(0.4, 0.9)          # 乱数の 順は 前の まま（半径 → こさ）
    if not PLAIN:
        img = over(img, hexc('#FFFFFF'), soft_circle(Hh, W, x, y, r_, 0.8) * a_)
# 遠くの丘・お城・はだかの木
hill = 236 - 30 * np.exp(-((xx - 640) / 120) ** 2) + 5 * np.sin(xx / 40)
img = over(img, hexc('#2C1846'), np.clip((yy - hill) / 2 + .5, 0, 1))
lay = A.g(A.castle('#2C1846', '#FFC94A'), 650, 214, 0.78) + A.g(A.bare_tree('#1E1230'), 752, 262, 0.95)
if not PLAIN:
    for x, y, s in ((140, 52, 0.62), (196, 84, 0.42), (430, 40, 0.5), (712, 160, 0.38), (520, 150, 0.32)):
        lay += A.g(A.bat(s, '#1A1028'), x, y)
rgb, a = svg_layer(lay, W, Hh)
img = over(img, rgb, a)
# 地面（くさむら）
img = over(img, hexc('#3B2350'), np.clip((yy - (262 + 5 * np.sin(xx / 50 + 1))) / 2 + .5, 0, 1))
img = over(img, hexc('#2A1840'), np.clip((yy - (292 + 4 * np.sin(xx / 35))) / 2 + .5, 0, 1))
grass = ''
for i in range(70):
    x = rng.uniform(0, W)
    y = 266 + rng.uniform(0, 50)
    h = rng.uniform(5, 11)
    grass += A.path(f'M{x - 2:.1f},{y:.1f} L{x + rng.uniform(-3, 3):.1f},{y - h:.1f} L{x + 2:.1f},{y:.1f} Z', '#4A2C62')
rgb, a = svg_layer(grass, W, Hh)
img = over(img, rgb, a * 0.9)
# ドラキュラ（左）
if not BASE:
    rgb, a = svg_layer(A.shadow(108, 300, 66, 7, '#0E0818', .5) + A.g(A.vampire(), 108, 300, 0.92), W, Hh)
    img = over(img, rgb, a)
# 馬（まん中・左向き＝ドラキュラの方）
if os.environ.get('CUTE_NO_HORSE') != '1':
    img = draw_cute(img, 'halloween', W, Hh)
# ジャック・オー・ランタンと ドクロ（右・手前）
lay = A.shadow(600, 306, 120, 8, '#0E0818', .5)
if not BASE:
    lay += A.g(A.pumpkin(78, 58, look=-4), 560, 306) + A.g(A.pumpkin(54, 40, look=3), 640, 310) + A.g(A.skull(1.05), 690, 308)
    lay += A.g(A.pumpkin(46, 34, look=4), 216, 312)
lay += A.g(A.pumpkin(40, 30, face=False, glow=False), 742, 314)
rgb, a = svg_layer(lay, W, Hh)
img = over(img, rgb, a)
save_webp(img, out)
print(out)
