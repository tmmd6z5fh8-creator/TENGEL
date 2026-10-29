"""浮世絵風の 壁紙（壁紙パック・第4.98版）の かわいい 大波を 絵（WebP）に する。
   まさちゃん「大波の絵をもう少し可愛く、他のエフェクトにあった波にして！」：小波と 同じ 平らな 絵（藍の 体・明るい すじ・細い 白い 泡の かさ・墨の ふち・
   先の 少し とがった 白い 爪）で、神奈川沖浪裏の 大波の 形を 描く（pack/ukiyoe.py の bigwave_svg）。
   巻きの 強さ c（−1：小波の 中から もり上がる とちゅう → 0：いちばん 高い → 1：波の 先を 投げ出す → 1.6：落ちて くずれる）の じゅんの 形の コマ（WAVE_CS）を
   ブラウザ（Chromium）で 2.5倍に 描いて、5れつの ます目の シートに ならべる。ページでは 形の コマを step-end で 入れかえ、高さ・かたむき・沈む のは 箱の transform（pack/ukiyoe.py）
   使わなく なった 絵（第4.97版までの 神奈川沖浪裏の 頭の コマ ukiyoe.crest）は blobs.json から 消す
   python3 kisekae/pack/make/ukiyoe_bigwave.py → ios/kisekae_blobs/<id>.webp・kisekae/pack/blobs.json の ukiyoe.wave"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))          # kisekae
from sheets import save_webp, record, preview_png, PACK  # noqa: E402
import numpy as np  # noqa: E402

Z = 2.5
COLS = 5


def unrecord(theme, name):
    """blobs.json から 使わなく なった 絵の 行を 消す（record と 同じ ロック）"""
    import fcntl
    p = os.path.join(PACK, 'blobs.json')
    with open(p + '.lock', 'w') as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        d = json.load(open(p, encoding='utf-8'))
        if d.get(theme, {}).pop(name, None) is not None:
            tmp = p + '.tmp'
            json.dump(d, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
            os.replace(tmp, p)
        fcntl.flock(lk, fcntl.LOCK_UN)


def main(out=None):
    import ukiyoe_samurai as S
    from pack import ukiyoe as U
    S.Z = Z
    ims = S.shot([(U.bigwave_svg(c), U.BW, U.BH) for c in U.WAVE_CS])
    fh, fw = ims[0].shape[:2]
    rows = (len(ims) + COLS - 1) // COLS
    sheet = np.zeros((rows * fh, COLS * fw, 4), np.uint8)
    for i, im in enumerate(ims):
        r, q = divmod(i, COLS)
        sheet[r * fh:(r + 1) * fh, q * fw:(q + 1) * fw] = im
    if out:
        os.makedirs(out, exist_ok=True)
        preview_png(sheet, os.path.join(out, 'uk_bigwave.png'), bg=(241, 230, 207))
    bid = save_webp(sheet, quality=88)
    meta = dict(cell=[fw, fh], cols=COLS, rows=rows, cs=U.WAVE_CS, size=[round(U.BW * U.WSC, 2), round(U.BH * U.WSC, 2)], z=Z)
    record('ukiyoe', 'wave', bid, meta)
    unrecord('ukiyoe', 'crest')
    print('wave', bid, meta['cell'], len(ims), flush=True)


if __name__ == '__main__':
    main(os.environ.get('OUT'))
