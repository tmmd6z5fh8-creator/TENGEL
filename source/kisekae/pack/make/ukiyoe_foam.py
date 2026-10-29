"""浮世絵風の 壁紙（壁紙パック）の 小波の 列と しぶきを 絵（WebP）に する：pack/ukiyoe.py の SVG（第4.97版：まるい 小波の 列 4つ・
   波の 先が 落ちた 所で ふき上がる しぶき 2つ・小波の 頭の しぶき 2つ・大波の 頭から 吹き飛ぶ しぶき 2つ）を ブラウザ（Chromium）で 3倍に 描いて
   1まいの シートに ならべる（SVG の まま だと 上の絵の HTML が 重く なるため・3倍＝iPhone でも ふちが くっきり）。ページでは 部品の 背景に して background-position で えらぶ
   python3 kisekae/pack/make/ukiyoe_foam.py → ios/kisekae_blobs/<id>.webp・kisekae/pack/blobs.json の ukiyoe.foam"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))          # kisekae
from sheets import save_webp, record, preview_png  # noqa: E402
import numpy as np  # noqa: E402

Z = 3
GAP = 4


def items():
    """[(名前, svg, 幅, 高さ)]（画面の px）"""
    from pack import ukiyoe as U
    out = [(f'rw{k}', U.ripple_row_svg(k), U.ROW_W, p['H']) for k, p in enumerate(U.ROWS)]
    out += [('bs0', U.burst_svg(11), 90, 70), ('bs1', U.burst_svg(12), 90, 70), ('pf0', U.puff_svg(51), 40, 26), ('pf1', U.puff_svg(53), 40, 26),
            ('sp1', U.spray_svg(41), 84, 44), ('sp2', U.spray_svg(43), 84, 44)]
    return out


def main(out=None):
    import ukiyoe_samurai as S
    its = items()
    S.Z = Z                                                       # お侍さんと 同じ 描き方で 2倍に
    ims = S.shot([(svg, w, h) for _, svg, w, h in its])
    # 行に つめる（はばが 600 を こえたら 次の 行）
    W = 600 * Z
    x = y = rowh = 0
    place = {}
    for (name, _, w, h), im in zip(its, ims):
        ih, iw = im.shape[:2]
        if x + iw > max(W, iw) and x > 0:
            x, y, rowh = 0, y + rowh + GAP, 0
        place[name] = (x, y, iw, ih)
        x += iw + GAP
        rowh = max(rowh, ih)
    SW = max(px + pw for px, _, pw, _ in place.values())
    SH = y + rowh
    sheet = np.zeros((SH, SW, 4), np.uint8)
    for (name, _, w, h), im in zip(its, ims):
        px, py, pw, ph = place[name]
        sheet[py:py + ph, px:px + pw] = im
    if out:
        os.makedirs(out, exist_ok=True)
        preview_png(sheet, os.path.join(out, 'uk_foam.png'), bg=(84, 112, 160))
    bid = save_webp(sheet, quality=86)
    meta = dict(z=Z, sheet=[SW, SH], parts={k: [v[0], v[1], v[2], v[3]] for k, v in place.items()})
    record('ukiyoe', 'foam', bid, meta)
    print('foam', bid, meta, flush=True)


if __name__ == '__main__':
    main(os.environ.get('OUT'))
