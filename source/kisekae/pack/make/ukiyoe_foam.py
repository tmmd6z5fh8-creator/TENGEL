"""浮世絵風の 壁紙（壁紙パック・第4.96版）の 白い 泡と しぶきを 絵（WebP）に する：pack/ukiyoe.py の SVG（くずれた 波の 白い 泡の かたまり 2列・
   白い 水が 走る ときの 泡の 山 5つ・はじける しぶき 2つ・頭から 吹き飛ぶ しぶき 2つ）を ブラウザ（Chromium）で 2倍に 描いて 1まいの シートに ならべる。
   北斎の 泡の 爪の 指が 多くて、SVG の まま だと 上の絵の HTML が 1MB ほど 重く なるため。ページでは 部品の 背景に して background-position で えらぶ
   python3 kisekae/pack/make/ukiyoe_foam.py → ios/kisekae_blobs/<id>.webp・kisekae/pack/blobs.json の ukiyoe.foam"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))          # kisekae
from sheets import save_webp, record, preview_png  # noqa: E402
import numpy as np  # noqa: E402

Z = 2
GAP = 4


def items():
    """[(名前, svg, 幅, 高さ)]（画面の px）"""
    from pack import ukiyoe as U
    out = [('band_b', U.foam_band_svg('b'), 280, 40), ('band_f', U.foam_band_svg('f'), 280, 40)]
    out += [(f'fm{k}', U.foam_svg(21 + k), 72, 36) for k in range(len(U.PEEL))]
    out += [('bs0', U.burst_svg(11), 90, 70), ('bs1', U.burst_svg(12), 90, 70), ('sp1', U.spray_svg(41), 84, 44), ('sp2', U.spray_svg(43), 84, 44)]
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
