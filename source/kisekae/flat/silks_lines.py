# 勝負服の 壁紙の 走る コマ：馬の 体の 中の 細い 黒い 線（筋肉・関節の 線）を 消して、やわらかい かげに かえる（第4.215版）
#   まさちゃん 2026/11/24 01:22「勝負服の赤丸の線がへんだから動いている時も見えないように消して！立体感が無くなるなら違和感なく影を追加して！」
#   線＝馬の 体（だいだい色）の 中に ある 細い 暗い 線（もも・肩・首・おなか・足の つけね）。コマごとに 形が かわる ので、走ると ちらちら 動いて 見えた。
#   3D から 描き直さずに、いまの シート（silks_run_hq.webp：ios/kisekae_blobs の 台帳 silks_blobs.json の run）から 線 だけを 直す：
#     1. 体の 色（だいだい）の 所を 出す → 細い すき間を とじた 形の 内がわ（外の ふち線から 6px より 中）に ある 暗い 画素 ＝ 体の 中の 線
#        （顔＝体の 右はしから 168px は さわらない：目・鼻・口・ほおの 線は のこす。外の ふち線・たてがみ・しっぽ・騎手・ゼッケン・ひづめ・白い 足先も さわらない）
#     2. 線を まわりの 体の 色で うめる（cv2.inpaint）
#     3. 線が あった 所を ぼかして、体の 色を 少し だけ 暗く する（やわらかい かげ：立体感を のこす・線には 見えない）
#   python3 kisekae/flat/silks_lines.py <もとの シート> <出す フォルダ>   → silks_run_hq.webp（flat/hq_install.py silks <出す フォルダ> で 入れる）・silks_lines_dbg.png（消した 線）
import sys, os, numpy as np, cv2
from scipy import ndimage
from PIL import Image
N = 15
SHADE = 0.075       # かげの 濃さ（いちばん 濃い 所で 体の 色の 7.5% 暗く：うすく）
SIG = 6.5           # かげの ぼかし（px：広く やわらかく）
HEAD = 168          # 顔の 長さ（px：コマ 924×441 の 中）


def disk(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]; return (x * x + y * y <= r * r).astype(np.uint8)


def fix_cell(c):
    """c＝1コマ（float32 RGBA）。→ 直した コマ・消した 線"""
    rgb, a = c[..., :3], c[..., 3]
    R, G, B = rgb[..., 0], rgb[..., 1], rgb[..., 2]; mx, mn = rgb.max(2), rgb.min(2)
    coat = (a > 200) & (R > 150) & (R > G + 35) & (G > B + 30) & (B < 150)                       # 体の 色（だいだい：明るい 所〜暗い 所）
    coat = ndimage.binary_opening(coat, iterations=1)
    fill = cv2.morphologyEx(coat.astype(np.uint8), cv2.MORPH_CLOSE, disk(5)) > 0                   # 細い 線を とじた 体
    inner = cv2.erode(fill.astype(np.uint8), disk(6)) > 0                                         # 外の ふち線から はなれた 中
    dark = (a > 200) & ~coat & (mx < 170) & (R >= B - 10)                                         # 暗い 画素（線）：青い もの（勝負服）は のぞく
    # 顔（体の 右はしから 左へ HEAD px：目・鼻・口・ほおの 線・頭絡）は さわらない
    ys, xs = np.nonzero(coat); face = np.zeros(a.shape, bool)
    if len(xs): face[:, max(0, int(np.percentile(xs, 99.8)) - HEAD):] = True
    lines = inner & dark & ~face
    lines = ndimage.binary_dilation(lines, iterations=1) & fill & ~face
    # 太い 暗い かたまり（たてがみ・鞍の 下・ゼッケンの ふち）は 線では ない：細い もの だけ
    thick = cv2.morphologyEx(lines.astype(np.uint8), cv2.MORPH_OPEN, disk(4)) > 0
    lines &= ~ndimage.binary_dilation(thick, iterations=3)
    if not lines.any(): return c, lines
    m8 = (ndimage.binary_dilation(lines, iterations=1) & fill).astype(np.uint8) * 255
    src = np.clip(rgb, 0, 255).astype(np.uint8); filled = cv2.inpaint(src, m8, 5, cv2.INPAINT_TELEA).astype(np.float32)
    w = cv2.GaussianBlur((m8 > 0).astype(np.float32), (0, 0), 0.7)[..., None]
    out = rgb * (1 - w) + filled * w
    sh = cv2.GaussianBlur(lines.astype(np.float32), (0, 0), SIG); sh = sh / max(float(sh.max()), 1e-3) * SHADE
    body = cv2.GaussianBlur(fill.astype(np.float32), (0, 0), 1.0)                                  # かげは 体の 中 だけ
    out = out * (1 - (sh * body * (~face))[..., None])
    return np.dstack([out, a]), lines


if __name__ == '__main__':
    src, outd = sys.argv[1], sys.argv[2]; os.makedirs(outd, exist_ok=True)
    im = np.asarray(Image.open(src).convert('RGBA')).astype(np.float32); H, W = im.shape[:2]; cw = W // N; o = im.copy(); dbg = im.copy(); tot = 0
    for f in range(N):
        c, k = fix_cell(im[:, f * cw:(f + 1) * cw]); o[:, f * cw:(f + 1) * cw] = c; tot += int(k.sum())
        d = dbg[:, f * cw:(f + 1) * cw]; d[k] = (255, 0, 255, 255); print('コマ', f, '線', int(k.sum()), flush=True)
    Image.fromarray(np.clip(o + 0.5, 0, 255).astype(np.uint8), 'RGBA').save(os.path.join(outd, 'silks_run_hq.webp'), 'WEBP', quality=90, method=6)
    Image.fromarray(dbg.astype(np.uint8), 'RGBA').save(os.path.join(outd, 'silks_lines_dbg.png'))
    print('合計', tot, os.path.getsize(os.path.join(outd, 'silks_run_hq.webp')), 'B')
