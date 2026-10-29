"""浮世絵風の 壁紙（壁紙パック）の しぶきを 絵（WebP）に する。
   第4.103版 まさちゃん「ダメだ小波だけがどうしても納得いかない。絵を大波に似せた小波で作成して」：
     小波は 大波の 子ども（小さな 大波）＝ 大波の 一生の コマ（make/ukiyoe_great.py の life・ukiyoe.wave の シート）を pack/ukiyoe.py で そのまま
     小さく 使う（絵を 足さない）。この シートには もう 小波を 入れない（第4.100版〜第4.102版の 小波の 絵＝small_wave は やめた）。
   しぶき（波の 先が 落ちた 所で 横へ ひろがる しぶき 1つ・大波の 頭から 吹き飛ぶ しぶき 2つ・第4.106版：大波が 沈みはじめて から 水平に なる まで
   白い 水の 先で 高く ふき上がる 潮しぶき 2つ＝plume_svg）は pack/ukiyoe.py の SVG を ブラウザ（Chromium）で 3倍に 描く。
   ぜんぶ 1まいの シートに ならべる（ページでは 部品の 背景に して background-position で えらぶ）。第4.106版で 小波の 頭の しぶき（pf）は やめた
   python3 kisekae/pack/make/ukiyoe_foam.py [OUT] → ios/kisekae_blobs/<id>.webp・kisekae/pack/blobs.json の ukiyoe.foam"""
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
    return [('bs0', U.burst_svg(11), 90, 70), ('sp1', U.spray_svg(41), 84, 44), ('sp2', U.spray_svg(43), 84, 44),
            ('pl0', U.plume_svg(61), U.PL_W, U.PL_H), ('pl1', U.plume_svg(67), U.PL_W, U.PL_H)]


def main(out=None):
    import ukiyoe_samurai as S
    its = items()
    S.Z = Z                                                       # お侍さんと 同じ 描き方で 3倍に
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
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    main(a[0] if a else os.environ.get('OUT'))
