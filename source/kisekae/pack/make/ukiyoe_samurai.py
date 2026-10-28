"""浮世絵風の 壁紙（壁紙パック・第4.94版）の お侍さんを 絵（WebP）に する：pack/ukiyoe.py の SVG（3人 × 歩く 12コマ・会釈 8コマ）を ブラウザ（Chromium）で
   絵の 単位の Z倍（2.5倍）に 描いて、1まいの シートに たてに ならべる（上から a の 歩く・a の 会釈・b の 歩く・b の 会釈・c の 歩く・c の 会釈。行の 間は すき間 GAP）。
   SVG の まま だと 上の絵の HTML が 300KB ほど 重く なるため。ページでは 歩く／会釈の 部品の 背景に して background-position で 行を えらぶ（動きは いままで どおり）
   python3 kisekae/pack/make/ukiyoe_samurai.py → ios/kisekae_blobs/<id>.webp・kisekae/pack/blobs.json の ukiyoe.samurai"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))          # kisekae
from sheets import save_webp, record, preview_png  # noqa: E402
import numpy as np  # noqa: E402
import cv2  # noqa: E402

Z = 2.5                   # 絵の 単位 → シートの 画素（画面では SM_K 倍 → 1px に 約2.2画素）
GAP = 4                   # 行の 間の すき間（となりの 行が にじまない ように）


def shot(items):
    """[(svg, 幅, 高さ)]（絵の 単位）を Z倍で 描く → [RGBA u8]"""
    from playwright.sync_api import sync_playwright
    from pack.common import durl
    out = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for svg, w, h in items:
            pg = b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=Z)
            html = (f"<html><body style='margin:0;background:transparent'>"
                    f"<img src=\"{durl(svg)}\" style='display:block;width:{w}px;height:{h}px'></body></html>")
            fd, p = tempfile.mkstemp(suffix='.html')
            os.close(fd)
            open(p, 'w', encoding='utf-8').write(html)
            pg.goto('file://' + p)
            pg.evaluate("() => Promise.all(Array.from(document.images).map(i => i.decode ? i.decode().catch(() => 0) : 0))")
            png = p + '.png'
            pg.screenshot(path=png, omit_background=True, clip={'x': 0, 'y': 0, 'width': w, 'height': h})
            im = cv2.imread(png, cv2.IMREAD_UNCHANGED)
            out.append(cv2.cvtColor(im, cv2.COLOR_BGRA2RGBA))
            os.remove(p)
            os.remove(png)
            pg.close()
        b.close()
    return out


def main(out=None):
    from pack import ukiyoe as U
    items, rows = [], []
    for who in ('a', 'b', 'c'):
        items += [(U.samurai_walk_svg(who), U.SM_W * 12, U.SM_H), (U.samurai_bow_svg(who), U.SM_W * len(U.BOW), U.SM_H)]
        rows += [f'{who}_w', f'{who}_b']
    ims = shot(items)
    rh = int(round(U.SM_H * Z))
    pitch = rh + GAP
    W = max(im.shape[1] for im in ims)
    sheet = np.zeros((pitch * len(ims), W, 4), np.uint8)
    for i, im in enumerate(ims):
        assert im.shape[0] == rh, im.shape
        sheet[i * pitch:i * pitch + rh, :im.shape[1]] = im
    if out:
        preview_png(sheet, os.path.join(out, 'uk_samurai.png'), bg=(241, 230, 207))
    bid = save_webp(sheet, quality=85)
    meta = dict(z=Z, row=pitch, sheet=[W, pitch * len(ims)], rows=rows)
    record('ukiyoe', 'samurai', bid, meta)
    print('samurai', bid, meta, flush=True)


if __name__ == '__main__':
    main(os.environ.get('OUT'))
