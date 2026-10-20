"""バレンタイン（780×320・まさちゃんの指定「壁紙、馬とカップル、チョコレート」）：
   ピンクの空（ふわっと光る ハート）に 上から とろける チョコ、左に チョコ色の競走馬（クリーム色の たてがみ・赤いリボン・ハートの ピンクのゼッケン1）、
   右に ハートの チョコの箱を わたす 女の子と、てれる 男の子のカップル、手前に 板チョコと トリュフと ハートのチョコ。
   馬は horse_flat・人と物は flat/event_art.py（一から作った形）
   python3 flat/valentine_banner.py <出力.webp>
   EVENT_SKY=1 CUTE_NO_HORSE=1 … → 動く壁紙の 空の絵（空と 床だけ：ハート・とろける チョコ・馬・カップル・手前の チョコなし。
                                     馬の 影と 前の絵は flat/couple_run.py・動きは couple_wall.py）"""
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
SKY = os.environ.get('EVENT_SKY') == '1'           # 動く壁紙の 空の絵（乱数は いつもと 同じ順に つかう）
rng = np.random.default_rng(14)
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)

# ピンクの空・ふわっと光る ハート
img = grad_v(Hh, W, [(0, '#FFC9DA'), (0.6, '#FFE3EC'), (1, '#FFF1F5')])
lay = ''
for x, y, s, op in A.sky_hearts(rng, W):
    lay += A.path(A.heart_d(x, y, s), '#FFFFFF', f'opacity="{op:.2f}"')
if not SKY:
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
drip = A.choco_drip(rng)
if not SKY:
    rgb, a = svg_layer(A.choco_drip_svg(drip), W, Hh)
    img = over(img, rgb, a)
# 馬（左・右向き＝カップルの方）
if os.environ.get('CUTE_NO_HORSE') != '1':
    img = draw_cute(img, 'valentine', W, Hh)
if SKY:                                            # 空の絵は ここまで（カップルと 手前の チョコは ページの SVG）
    save_webp(img, out)
    sys.exit(0)
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
