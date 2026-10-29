"""浮世絵風の 壁紙（壁紙パック）の 小波（小さな 大波）の 絵の 帯（WebP）を 作る。
   第4.104版 まさちゃん「小波もう少し大きくして、海が埋まるように数を増やして！」「小波は同じ絵だから数を増やして何層かに重ねて自然に見えるようにして！」：
     小波は 第4.103版と 同じ「小さな 大波」（大波の 一生の コマ＝ukiyoe.wave の シートの うち、くずれはじめて 横長に なった 所＝コマ 28〜39）。
     数を ふやしても かるく 動く ように、その 12コマを 同じ 大きさの 箱に ならべた 1本の 帯に する（ページでは 箱の 中で 帯を transform だけで
     ずらして コマを 入れかえる＝はば・高さ・背景の 場所を 動かさない）。
   1コマ：大波の コマの 絵（シートの 中の 四角）を そのまま 写す（絵を 足さない・左右に うら返さない）。
     たては コマ 28 の 上の はしを 0 に して、コマが すすんで 上の はしが 下がる ぶんの 85% を もどす（第4.103版の MW_KEEP と 同じ：白い 波が 少しずつ 低く なる）。
     上から D_CELL（大波の 絵の px）まで だけ 入れる（その 下は 列の 海の 線より 下＝見えない）。
   大波の 絵（make/ukiyoe_great.py）を 作り直したら、これも 作り直す：
   python3 kisekae/pack/make/ukiyoe_mini.py [OUT] → ios/kisekae_blobs/<id>.webp・kisekae/pack/blobs.json の ukiyoe.mini"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))          # kisekae
from sheets import save_webp, record, preview_png, BLOB_DIR  # noqa: E402
import json  # noqa: E402
import numpy as np  # noqa: E402
import cv2  # noqa: E402

F0, F1 = 28, 39            # コマの はんい（1 から かぞえる ukiyoe.wave の cells）
KEEP = .85                 # 上の はしが 下がる ぶんを もどす わりあい
D_CELL = 58.0              # 帯の 高さ（大波の 絵の px）：見せる 深さ 44＋上下の ゆれ＋コマが 下がる ぶん
Z = 1.4                    # 帯の 細かさ（大波の 絵の 1px あたりの 画素：小波は いちばん 大きくて 0.42倍・iPhone の 3倍で 1.26）
GAP = 2                    # コマの 間（画素）


def main(out=None):
    B = json.load(open(os.path.join(os.path.dirname(HERE), 'blobs.json'), encoding='utf-8'))['ukiyoe']['wave']
    z = B['z']
    sheet = cv2.imread(os.path.join(BLOB_DIR, B['id'] + '.webp'), cv2.IMREAD_UNCHANGED)
    sheet = cv2.cvtColor(sheet, cv2.COLOR_BGRA2RGBA)
    cells = B['cells']
    top0 = cells[F0 - 1][5]
    xs0 = min(cells[k - 1][4] for k in range(F0, F1 + 1))
    xs1 = max(cells[k - 1][4] + cells[k - 1][2] for k in range(F0, F1 + 1))
    cw, ch = xs1 - xs0, int(round(D_CELL * z))                       # 1コマの 箱（シートの 画素＝大波の 絵の px × z）
    tiles = []
    for k in range(F0, F1 + 1):
        x, y, w, h, ox, oy = cells[k - 1]
        img = np.zeros((ch, cw, 4), np.uint8)
        dy = int(round(oy - (oy - top0) * KEEP - top0))                  # 箱の 上から（シートの 画素）
        src = sheet[y:y + h, x:x + w]
        y0, y1 = max(0, dy), min(ch, dy + h)
        if y1 > y0:
            img[y0:y1, ox - xs0:ox - xs0 + w] = src[y0 - dy:y1 - dy]
        tiles.append(img)
    s = Z / z                                                         # シートの 画素 → 帯の 画素
    tw, th = int(round(cw * s)), int(round(ch * s))
    strip = np.zeros((th, len(tiles) * (tw + GAP) - GAP, 4), np.uint8)
    for i, im in enumerate(tiles):
        # 色は アルファを かけてから 小さく（ふちが 黒く にじまない）
        a = im[..., 3:4].astype(np.float32) / 255
        pm = np.concatenate([im[..., :3].astype(np.float32) * a, a * 255], 2)
        sm = cv2.resize(pm, (tw, th), interpolation=cv2.INTER_AREA)
        al = np.clip(sm[..., 3:4], 0, 255)
        rgb = np.where(al > 0, sm[..., :3] / np.maximum(al, 1e-3) * 255, 0)
        strip[:, i * (tw + GAP):i * (tw + GAP) + tw] = np.concatenate([np.clip(rgb, 0, 255), al], 2).astype(np.uint8)
    if out:
        os.makedirs(out, exist_ok=True)
        preview_png(strip, os.path.join(out, 'uk_mini.png'), bg=(84, 112, 160))
    bid = save_webp(strip, quality=84)
    tops = [round((cells[k - 1][5] - (cells[k - 1][5] - top0) * KEEP - top0) / z, 3) for k in range(F0, F1 + 1)]
    meta = dict(z=Z, f0=F0, n=len(tiles), cell=[round(cw / z, 3), round(ch / z, 3)], step=round((tw + GAP) / Z, 4), px=[tw, th], gap=GAP,
                sheet=[strip.shape[1], strip.shape[0]], x0=round(xs0 / z, 3), top0=round(top0 / z, 3), tops=tops)
    record('ukiyoe', 'mini', bid, meta)
    print('mini', bid, meta, strip.shape, flush=True)


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    main(a[0] if a else os.environ.get('OUT'))
