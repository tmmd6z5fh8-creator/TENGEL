"""ホワイトデー（780×320・まさちゃんの指定「壁紙、馬とカップル、マシュマロ」）：
   水色の空（マシュマロみたいな 雲・キラッ）に 上から 水色の リボン、左に マシュマロの びんを わたす 男の子と、よろこぶ 女の子のカップル、
   右に 白い競走馬（水色の たてがみ・水色の リボン・ハートの 水色のゼッケン1）、手前に 白・ピンク・水色の マシュマロと プレゼント。
   馬は horse_flat・人と物は flat/event_art.py（一から作った形）
   python3 flat/whiteday_banner.py <出力.webp>"""
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
rng = np.random.default_rng(314)
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)

# 水色の空・マシュマロみたいな 雲・キラッ
img = grad_v(Hh, W, [(0, '#9ACDF0'), (0.55, '#C4E2F7'), (1, '#E9F4FC')])
lay = ''
for cx, cy, s in ((120, 120, 1.0), (400, 74, 0.8), (352, 196, 0.62), (742, 58, 0.62)):
    for dx, dy, r in ((-36, 6, 22), (-12, -8, 28), (18, -4, 24), (40, 8, 18), (0, 12, 22)):
        lay += A.circ(cx + dx * s, cy + dy * s, r * s, '#FFFFFF', 'opacity=".85"')
for i in range(14):
    x, y = rng.uniform(0, W), rng.uniform(40, 230)
    lay += A.path(A.sparkle_d(x, y, rng.uniform(4, 8)), '#FFFFFF', 'opacity=".9"')
rgb, a = svg_layer(lay, W, Hh)
img = over(img, rgb, a)
# 床（白と水色の しま）
img = over(img, hexc('#E6F2FB'), np.clip((yy - 262) / 1.5 + .5, 0, 1))
chk = ''
for i in range(0, W, 26):
    chk += A.rect(i, 262, 13, 60, '#CFE5F5', 0, 'opacity=".75"')
rgb, a = svg_layer(chk, W, Hh)
img = over(img, rgb, a)
img = over(img, hexc('#A9CDE8'), np.clip((yy - 262) / 1.2 + .5, 0, 1) * np.clip((265 - yy) / 1.2 + .5, 0, 1))
# 上の リボン（ゆるい なみ・ちょうむすび）
rib = 'M0,0 L780,0 L780,12'
for i in range(6):
    x0 = 780 - i * 130
    rib += f' Q{x0 - 65:.0f},{40:.0f} {x0 - 130:.0f},12'
rib += ' L0,0 Z'
lay = A.path(rib, '#8CC4EC') + A.path(rib.replace('L780,12', 'L780,6'), '#B5DBF5', 'opacity=".6"')
for i in range(1, 6):
    x0 = 780 - i * 130
    lay += A.path(f'M{x0},10 Q{x0 - 22},-6 {x0 - 18},16 Z', '#6FAEDB') + A.path(f'M{x0},10 Q{x0 + 22},-6 {x0 + 18},16 Z', '#6FAEDB')
    lay += A.path(f'M{x0},12 L{x0 - 8},34 L{x0 - 2},30 Z M{x0},12 L{x0 + 8},34 L{x0 + 2},30 Z', '#5E9FD0') + A.circ(x0, 12, 4, '#5E9FD0')
rgb, a = svg_layer(lay, W, Hh)
img = over(img, rgb, a)
# カップル（左）：男の子が マシュマロの びんを わたす
lay = A.shadow(170, 300, 112, 7, '#8FB4D6', .45)
lay += A.g(A.girl(dress='#F7B6CB', dressD='#E58FAD', hair='#4A2E22', hairD='#33201A', ribbon='#6FAEDB', hand_out=1, hold=None), 122, 300, 0.95)
lay += A.g(A.boy(top='#6FA8DC', topD='#4F8CC8', pants='#3E5A80', hair='#5A3A28', hand_out=-1, shy=False, hold=A.g(A.jar(46, 54), 0, 26, 0.95)), 226, 300, 0.95)
for x, y, s in ((170, 104, 8), (150, 84, 5.5), (192, 86, 5)):
    lay += A.path(A.heart_d(x, y, s), '#8CC4EC')
rgb, a = svg_layer(lay, W, Hh)
img = over(img, rgb, a)
# 馬（右・左向き＝カップルの方）
if os.environ.get('CUTE_NO_HORSE') != '1':
    img = draw_cute(img, 'whiteday', W, Hh)
# 手前の マシュマロと プレゼント
lay = A.shadow(400, 306, 110, 6, '#8FB4D6', .4)
cols = (('#FFFFFF', '#E3EAF2'), ('#FFD6E2', '#F2B5C8'), ('#D6ECFB', '#B5D6EF'))
for i, (x, y, w, rot) in enumerate(((330, 308, 26, -8), (360, 312, 22, 6), (392, 306, 28, -4), (424, 312, 22, 10), (452, 308, 24, -6), (300, 314, 20, 0))):
    c, cd = cols[i % 3]
    lay += A.g(A.marshmallow(w, w * 0.78, c, cd), x, y, rot=rot)
lay += A.g(A.gift(40, 30, '#FFFFFF', '#D6E2EE', '#8CC4EC'), 740, 308) + A.g(A.marshmallow(22, 17, '#FFD6E2', '#F2B5C8'), 706, 312, rot=-8)
rgb, a = svg_layer(lay, W, Hh)
img = over(img, rgb, a)
save_webp(img, out)
print(out)
