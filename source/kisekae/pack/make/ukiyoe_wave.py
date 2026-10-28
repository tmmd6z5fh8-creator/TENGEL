"""浮世絵風の 壁紙（壁紙パック・第4.94版）の 大波を 絵（WebP）に する：pack/ukiyoe.py の SVG（hk_wave の S1・S2・S3 と hk_crash・手前の 小さな 波 hk_small）を
   ブラウザ（Chromium）で 2倍の 大きさに 描いて、すき通しつきの 1まいの シートに ならべる。SVG の まま だと 爪の 泡の 点が 多くて 上の絵の HTML が 1.6MB に なるため
   （絵に すると 数十KB）。ページでは 同じ シートを 4つの 部品の 背景に して、background-position で 形を えらぶ（重ねて 入れかえる 動きは いままで どおり CSS）
   python3 kisekae/pack/make/ukiyoe_wave.py → ios/kisekae_blobs/<id>.webp・kisekae/pack/blobs.json の ukiyoe.wave（4こま）・ukiyoe.small"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))          # kisekae
from sheets import save_webp, record, preview_png  # noqa: E402
import numpy as np  # noqa: E402
import cv2  # noqa: E402

Z = 2                     # 2倍（馬の シートと 同じ）


def shot(svgs, w, h):
    """SVG（同じ 大きさ w×h）を Chromium で Z倍に 描く → [(h*Z, w*Z, 4) の RGBA u8]"""
    from playwright.sync_api import sync_playwright
    from pack.common import durl
    out = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=Z)
        for svg in svgs:
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
        b.close()
    return out


def main(out=None):
    from pack import ukiyoe as U
    fr = shot([U.hk_wave(U.HK_S1, 3), U.hk_wave(U.HK_S2, 1), U.hk_wave(U.HK_S3, 2), U.hk_crash()], U.HK_W, U.HK_H)
    u8 = np.concatenate(fr, axis=1)
    if out:
        preview_png(u8, os.path.join(out, 'uk_wave.png'), bg=(241, 230, 207))
    bid = save_webp(u8, quality=90)
    meta = dict(frames=len(fr), cell=[U.HK_W * Z, U.HK_H * Z], size=[U.HK_W, U.HK_H])
    record('ukiyoe', 'wave', bid, meta)
    print('wave', bid, meta, flush=True)
    sw, sh = U.SMALL_WH
    sm = shot([U.hk_small(w=sw, h=sh)], sw, sh)[0]
    if out:
        preview_png(sm, os.path.join(out, 'uk_small.png'), bg=(241, 230, 207))
    bid2 = save_webp(sm, quality=90)
    meta2 = dict(frames=1, cell=[sw * Z, sh * Z], size=[sw, sh])
    record('ukiyoe', 'small', bid2, meta2)
    print('small', bid2, meta2, flush=True)


if __name__ == '__main__':
    main(os.environ.get('OUT'))
