"""クリスマス（780×320・まさちゃんの指定「壁紙、馬とサンタさん、クリスマスツリー」）：
   雪の夜（星・月・遠くの町の あかり・降る雪）に、左に クリスマスツリー（金の星・玉・あかり・プレゼント）、
   まん中に トナカイの カチューシャを つけた 鹿毛の競走馬（耳の うしろに 赤い カチューシャと ふわふわの 角2本・赤と緑の綱に 金の鈴・白いふちの 赤いゼッケン1・ひいらぎ）、
   右に プレゼントを さしだす サンタさん。馬は horse_flat（ぺたっとした色の絵）・人と物は flat/event_art.py（一から作った形）
   python3 flat/xmas_banner.py <出力.webp>
   XMAS_BASE=1 python3 flat/xmas_banner.py <出力.webp>   → 動く壁紙の 下の絵（サンタさんと 手前の 降る雪なし。どちらも ページの SVG で動かす：xmas_wall.py・flat/xmas_run.py）"""
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
rng = np.random.default_rng(71)
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)

# 夜空・月・星
img = grad_v(Hh, W, [(0, '#0E1C3C'), (0.55, '#1F3D6E'), (0.78, '#3A5E92')])
glow = np.exp(-(((xx - 700) ** 2 + (yy - 50) ** 2) / (2 * 46.0 ** 2))) * 0.16
img = over(img, hexc('#FFF6D6'), glow)
moon = soft_circle(Hh, W, 700, 50, 24, 1.2) * (1 - soft_circle(Hh, W, 711, 43, 21, 1.2))   # 三日月
img = over(img, hexc('#FFF4CC'), moon)
for i in range(70):
    x, y = rng.uniform(0, W), rng.uniform(0, 170)
    r = rng.uniform(0.6, 1.5)
    img = over(img, hexc('#FFFFFF'), soft_circle(Hh, W, x, y, r, 0.8) * rng.uniform(0.5, 0.95))
# 遠くの 雪の丘と 町（あかりの ともる まど）
hill = 214 + 10 * np.sin(xx / 70 + 0.6) + 6 * np.sin(xx / 29)
img = over(img, hexc('#C9D8EA'), np.clip((yy - hill) / 2 + .5, 0, 1))
town = ''
for k, x in enumerate(range(222, 560, 30)):
    hgt = 22 + 14 * ((k * 37) % 5) / 4
    y0 = 214 + 10 * math.sin(x / 70 + 0.6) + 6 * math.sin(x / 29) - hgt + 4
    town += A.rect(x, y0, 24, hgt + 6, '#2B4470') + A.path(f'M{x - 3},{y0 + 1} L{x + 12},{y0 - 11} L{x + 27},{y0 + 1} Z', '#2B4470')
    town += A.path(f'M{x - 3},{y0 + 1} L{x + 12},{y0 - 11} L{x + 27},{y0 + 1} L{x + 23},{y0 + 3} L{x + 12},{y0 - 6} L{x + 1},{y0 + 3} Z', '#EEF4FB')
    for wx_ in (x + 5, x + 14):
        if (k + wx_) % 3:
            town += A.rect(wx_, y0 + 8, 5, 6, '#FFD873', 1)
rgb, a = svg_layer(town, W, Hh)
img = over(img, rgb, a * 0.85)
img = over(img, hexc('#E3ECF6'), np.clip((yy - (232 + 6 * np.sin(xx / 55 + 1))) / 2 + .5, 0, 1))
img = over(img, hexc('#F6F9FD'), np.clip((yy - (258 + 5 * np.sin(xx / 40 + 2))) / 2 + .5, 0, 1))
img = over(img, hexc('#D3E1EF'), np.clip((yy - (300 + 4 * np.sin(xx / 33))) / 2 + .5, 0, 1) * 0.8)

# ツリー・プレゼント（左）
lay = A.shadow(130, 298, 112, 9, '#8FA9C8', .5) + A.g(A.xmas_tree(266), 130, 296)
lay += A.g(A.gift(36, 30, '#D7323A', '#A9232B', '#F2C14E'), 70, 304) + A.g(A.gift(30, 22, '#4A8FE0', '#2F6CB5', '#FFFFFF'), 190, 306)
lay += A.g(A.gift(26, 34, '#F2C14E', '#C9962C', '#D7323A'), 222, 302)
rgb, a = svg_layer(lay, W, Hh)
img = over(img, rgb, a)
# 馬（まん中・右向き）
if os.environ.get('CUTE_NO_HORSE') != '1':
    img = draw_cute(img, 'xmas', W, Hh)
if os.environ.get('XMAS_BASE') != '1':        # 動く壁紙の 下の絵は サンタさんと 降る雪なし（xmas_wall.py が ページの SVG で 動かす）
    # サンタさん（右・プレゼントを 馬へ）
    rgb, a = svg_layer(A.shadow(640, 300, 54, 7, '#8FA9C8', .55) + A.g(A.santa(), 640, 300, 0.86), W, Hh)
    img = over(img, rgb, a)
    # 降る雪（手前）
    snow = ''
    FACES = ((596, 112, 700, 200), (430, 58, 520, 150))                    # 顔の前には 雪を 置かない（サンタさん・馬）
    free = lambda x, y: not any(x0 <= x <= x1 and y0 <= y <= y1 for x0, y0, x1, y1 in FACES)
    for i in range(90):
        x, y = rng.uniform(0, W), rng.uniform(0, Hh)
        r = rng.uniform(1.2, 3.0)
        op = rng.uniform(.55, .95)
        if free(x, y):
            snow += A.circ(x, y, r, '#FFFFFF', f'opacity="{op:.2f}"')
    for i in range(10):
        x, y, r = rng.uniform(0, W), rng.uniform(0, 190), rng.uniform(4, 6.5)
        if free(x, y):
            snow += A.snowflake(x, y, r, op=0.85)
    rgb, a = svg_layer(snow, W, Hh)
    img = over(img, rgb, a)
save_webp(img, out)
print(out)
