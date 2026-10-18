"""メリーゴーランドの絵（780×320）：背景・屋根・電球・ぼけた光・床・金の柱は前のまま、木馬だけ「ぺたっとした色＋太い線」に
   python3 flat/carousel_banner.py <出力.webp>
   python3 flat/carousel_banner.py --base <出力.webp>   → 木馬の上下の動き（まさちゃん「馬が上下に動く」）のための下の絵：
     いまの絵から、木馬・柱の金の輪・床の影だけをぬいたもの（背景・柱・柱の下の台・屋根・電球はそのまま）。
     木馬と輪と影はページの SVG で描いて動かす（carousel_wall.py が horse_parts() で同じ形を使う）"""
import sys, os
import numpy as np
import cv2
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
sys.path.insert(0, HERE)
from style2d import grad_v, soft_circle, over, hexc, blur, save_webp
from flat_horse import to_png
from carousel_horse import carousel_horse, PALETTES

W, Hh = 780, 320
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
LINE = '#4A2A4E'
HORSES = [  # (色, 左上x, 左上y, 大きさ)  奥 → 手前の順
    ('gold', 474, 82, 0.66),
    ('pink', 84, 76, 0.725),
]
DEFS = ('<defs><pattern id="tw" width="10" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(-32)">'
        '<rect width="10" height="9" fill="#C9952B"/><rect width="10" height="4.5" fill="#F7DE8A"/></pattern>'
        '<filter id="sh" x="-50%" y="-200%" width="200%" height="500%"><feGaussianBlur stdDeviation="3.2"/></filter></defs>')
ROOF_Y = 44                     # 屋根のふち（しま模様の下は 40 ごとの丸い波・深さ16）
BULB_Y, BULB_R = ROOF_Y + 22, 4  # 電球（x = 20, 60, 100, …）
ALL = ('shadow', 'pole', 'horse', 'ring', 'base')


def background():
    """背景（前の絵と同じ）：ピンクから藤色・ぼけた光・床"""
    rng = np.random.default_rng(171)
    img = grad_v(Hh, W, [(0, '#FBE3EE'), (1, '#E9DDF7')])
    for i in range(40):
        x, y = rng.uniform(0, W), rng.uniform(60, Hh); r = rng.uniform(8, 24)
        img = over(img, hexc(['#FFFFFF', '#FFE7A8', '#FFD1E6'][rng.integers(0, 3)]), soft_circle(Hh, W, x, y, r, 3) * 0.35)
    img = over(img, hexc('#E7C9E9'), np.clip((yy - 288) / 1.5 + .5, 0, 1))
    return img


def horse_parts(key, x0, y0, sc):
    """1頭ぶんの SVG の部品（描く順）：[(種類, svg)]・と 柱の x・鞍と おなかの高さ・影の (cx, cy, rx, ry)"""
    g, m = carousel_horse(PALETTES[key], ow=4.2 / sc)
    px = x0 + m['pole_x'] * sc
    top_y, bot_y = y0 + m['seat_y'] * sc, y0 + m['belly_y'] * sc
    parts = [('shadow', f'<ellipse cx="{x0 + 178 * sc:.1f}" cy="296" rx="{120 * sc:.1f}" ry="6" fill="#8A4F86" opacity=".22" filter="url(#sh)"/>'),   # 床の影
             ('pole', f'<rect x="{px - 5:.1f}" y="40" width="10" height="{298 - 40}" rx="2" fill="url(#tw)" stroke="{LINE}" stroke-width="2.2"/>'),  # 柱（うしろ）
             ('horse', f'<g transform="translate({x0} {y0}) scale({sc})">{g}</g>')]                                                                   # 木馬
    for cy in (top_y - 3, bot_y + 1):                                   # 柱が鞍と おなかを通るところの金の輪
        parts.append(('ring', f'<rect x="{px - 8.5:.1f}" y="{cy - 4:.1f}" width="17" height="8" rx="3" fill="#E9C46A" stroke="{LINE}" stroke-width="2.2"/>'))
    parts.append(('base', f'<rect x="{px - 10:.1f}" y="290" width="20" height="9" rx="3" fill="#E9C46A" stroke="{LINE}" stroke-width="2.2"/>'))   # 柱の下の台
    return parts, dict(px=px, top_y=top_y, bot_y=bot_y, shadow=(x0 + 178 * sc, 296, 120 * sc, 6))


def fg_over(img, which=ALL, tmpdir=None):
    """木馬と柱（SVG を Chromium で2倍に描いて縮める）を重ねる。which：描く部品の種類"""
    parts = []
    for key, x0, y0, sc in HORSES:
        parts += [s for k, s in horse_parts(key, x0, y0, sc)[0] if k in which]
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{Hh}" viewBox="0 0 {W} {Hh}">{DEFS}{"".join(parts)}</svg>'
    tmp = os.path.join(tmpdir or HERE, '_carousel_fg.png')
    to_png(svg, W, Hh, tmp, scale=2)
    fg = np.asarray(Image.open(tmp).convert('RGBA')).astype(np.float32) / 255
    a2 = fg[..., 3:4]
    pm = cv2.resize(fg[..., :3] * a2, (W, Hh), interpolation=cv2.INTER_AREA)        # 2倍で描いて、色×透明度のまま縮める
    al = cv2.resize(a2[..., 0], (W, Hh), interpolation=cv2.INTER_AREA)
    rgb = np.where(al[..., None] > 1e-4, pm / np.maximum(al, 1e-4)[..., None], 0)
    img = over(img, rgb, al)
    os.remove(tmp)
    return img


def roof(img):
    """屋根（しま模様のふち）と電球（前の絵と同じ）"""
    stripe = ((xx // 40) % 2 == 0)
    rf = np.where(stripe[..., None], hexc('#F49AC1'), hexc('#FFFFFF'))
    sc_edge = ROOF_Y + 16 * np.sqrt(np.clip(1 - ((xx % 40) - 20) ** 2 / 400, 0, 1))
    rm = np.clip((sc_edge - yy) / 1.2 + .5, 0, 1)
    img = over(img, rf, rm)
    img = over(img, hexc('#C9952B'), np.clip(1 - np.abs(yy - ROOF_Y) / 2.5, 0, 1))
    bl = np.zeros((Hh, W), np.float32)
    for x in range(20, W, 40):
        cv2.circle(bl, (x * 4, int(BULB_Y * 4)), BULB_R * 4, 1.0, -1, cv2.LINE_AA, shift=2)
    img = img + blur(bl, 7)[..., None] * hexc('#FFE08A') * 0.8
    img = over(img, hexc('#FFF6D0'), bl)
    return np.clip(img, 0, 1)


def render(which=ALL, tmpdir=None):
    return roof(fg_over(background(), which, tmpdir))


if __name__ == '__main__':
    if sys.argv[1] == '--base':
        out = sys.argv[2]
        save_webp(render(('pole', 'base'), os.path.dirname(os.path.abspath(out))), out)
    else:
        out = sys.argv[1]
        save_webp(render(ALL, os.path.dirname(os.path.abspath(out))), out)
    print(out)
