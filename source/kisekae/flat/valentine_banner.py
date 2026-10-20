"""バレンタイン（780×320・まさちゃんの指定「壁紙、馬とカップル、チョコレート」）：
   ピンクの空（ふわっと光る ハート）に 上から とろける チョコ、左に チョコ色の競走馬（クリーム色の たてがみ・赤いリボン・ハートの ピンクのゼッケン1）、
   右に ハートの チョコの箱を わたす 女の子と、てれる 男の子のカップル、手前に 板チョコと トリュフと ハートのチョコ。
   馬は horse_flat・人と物は flat/event_art.py（一から作った形）
   python3 flat/valentine_banner.py <出力.webp>"""
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
rng = np.random.default_rng(14)
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)

# ピンクの空・ふわっと光る ハート
img = grad_v(Hh, W, [(0, '#FFC9DA'), (0.6, '#FFE3EC'), (1, '#FFF1F5')])
lay = ''
for i in range(16):
    x, y, s = rng.uniform(0, W), rng.uniform(40, 230), rng.uniform(10, 26)
    lay += A.path(A.heart_d(x, y, s), '#FFFFFF', f'opacity="{rng.uniform(.25, .5):.2f}"')
rgb, a = svg_layer(lay, W, Hh)
img = over(img, rgb, a)
# 床（ピンクの台・チェック）
img = over(img, hexc('#F7B6CB'), np.clip((yy - 262) / 1.5 + .5, 0, 1))
chk = ''
for i in range(0, W, 26):
    chk += A.rect(i, 262, 13, 60, '#F4A3BD', 0, 'opacity=".55"')
rgb, a = svg_layer(chk, W, Hh)
img = over(img, rgb, a)
img = over(img, hexc('#E98AA8'), np.clip((yy - 262) / 1.2 + .5, 0, 1) * np.clip((265 - yy) / 1.2 + .5, 0, 1))
# 上から とろける チョコ
drip = 'M0,0 L780,0 L780,18'
x = 780
k = 0
while x > 0:
    w = rng.uniform(26, 48)
    dl = rng.uniform(14, 42) if k % 2 == 0 else rng.uniform(4, 10)
    xm = x - w / 2
    drip += f' Q{x - 4:.1f},{18 + dl * 0.2:.1f} {x - w * 0.3:.1f},{18 + dl * 0.8:.1f} Q{xm:.1f},{18 + dl + 8:.1f} {x - w * 0.7:.1f},{18 + dl * 0.8:.1f} Q{x - w + 4:.1f},{18 + dl * 0.2:.1f} {x - w:.1f},18'
    x -= w
    k += 1
drip += ' L0,0 Z'
lay = A.path(drip, '#5A2E1C') + A.rect(0, 0, 780, 10, '#6E3A24')
lay += A.path('M0,10 L780,10', 'none', 'stroke="#8A5232" stroke-width="3" opacity=".6"')
rgb, a = svg_layer(lay, W, Hh)
img = over(img, rgb, a)
# 馬（左・右向き＝カップルの方）
if os.environ.get('CUTE_NO_HORSE') != '1':
    img = draw_cute(img, 'valentine', W, Hh)
# カップル（右）・ハートの チョコの箱
lay = A.shadow(600, 300, 110, 7, '#C9708E', .45)
lay += A.g(A.girl(hold=A.heart_box(0.9), hand_out=1), 552, 300, 0.95)
lay += A.g(A.boy(hand_out=-1, shy=True), 664, 300, 0.95)
for x, y, s in ((600, 116, 9), (624, 92, 6), (580, 92, 5)):
    lay += A.path(A.heart_d(x, y, s), '#E8547C')
rgb, a = svg_layer(lay, W, Hh)
img = over(img, rgb, a)
# 手前の チョコ
lay = A.shadow(400, 306, 120, 6, '#C9708E', .4)
lay += A.g(A.choco_bar(76, 36), 380, 308, rot=-6) + A.g(A.truffle(12), 444, 308) + A.g(A.truffle(10, top='#F7A8C0'), 470, 310)
lay += A.g(A.heart_box(0.75, '#6B3A22', '#4E2816', '#F2C14E'), 330, 296) + A.g(A.truffle(9, drizzle=False), 300, 312)
lay += A.g(A.truffle(10), 740, 310) + A.g(A.heart_box(0.6), 768, 300)
rgb, a = svg_layer(lay, W, Hh)
img = over(img, rgb, a)
save_webp(img, out)
print(out)
