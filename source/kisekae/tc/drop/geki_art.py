# 激馬熱馬（第4.175版・まさちゃん 2026/11/15 13:56「当選時、馬バレの画像一枚目・馬バレ保留の画像二枚目」）の 絵を アプリ用に そろえる
#   python3 -I geki_art.py <馬バレの 絵（丸）> <保留の 絵（八角）> <出力の フォルダ>
#   ・馬バレ（tc_dp_uma7）：ほかの 6色と 同じ 大きさ（344×344・色の 丸の 半径 170）。丸の ふちは でこぼこ（半径 604〜621）なので、その 少し 内がわ（600）で 丸く 切って 台の 黄色い 縁に はめる
#   ・保留（tc_dp_hold7）：ほかの 6色と 同じ 大きさ（200×200・八角の はば 180）
#   ・もらった 絵は 中まで 少し すけて いる（すけ具合 248〜254／255）→ 中が ぴったり 255 に なる ように 直す
#   まさちゃんの 絵・できた 素材は リポジトリに 入れない（ios/tc_assets/ は .gitignore）
import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
UMA_SIZE, UMA_R, UMA_CUT = 344, 170, 600.0          # 絵の 大きさ・色の 丸の 半径（drop_art.py と 同じ）／もとの 絵で 丸く 切る 半径（画素）
HOLD_SIZE, HOLD_W = 200, 180                        # 絵の 大きさ・八角の はば（drop_art.py と 同じ）


def load(p):
    a = np.asarray(Image.open(p).convert('RGBA')).copy(); al = a[..., 3].astype(np.float32)
    lab, n = ndi.label(al > 128); cnt = np.bincount(lab.ravel()); cnt[0] = 0; mb = lab == cnt.argmax()
    core = ndi.binary_erosion(mb, iterations=6); full = float(al[core].min()); assert full >= 245, full      # ふちから 6画素 内がわの いちばん うすい 所（248〜250）
    a[..., 3] = np.clip(np.rint(al * 255.0 / full), 0, 255).astype(np.uint8)          # 中を ぴったり 255 に
    ys, xs = np.nonzero(mb)
    return a, (xs.min() + xs.max() + 1) / 2, (ys.min() + ys.max() + 1) / 2, xs.max() - xs.min() + 1, ys.max() - ys.min() + 1


def premul_resize(a, k):
    f = a.astype(np.float32) / 255; pm = np.dstack([f[..., :3] * f[..., 3:], f[..., 3:]])
    w, h = int(round(a.shape[1] * k)), int(round(a.shape[0] * k))
    o = np.dstack([np.asarray(Image.fromarray(pm[..., c]).resize((w, h), Image.LANCZOS)) for c in range(4)]); al = np.clip(o[..., 3:], 0, 1)
    rgb = np.where(al > 1e-4, o[..., :3] / np.maximum(al, 1e-4), 0)
    return Image.fromarray((np.clip(np.dstack([rgb, al]), 0, 1) * 255 + 0.5).astype(np.uint8), 'RGBA')


def place(a, cx, cy, k, size):
    big = premul_resize(a, k); x0, y0 = int(round(cx * k - size / 2)), int(round(cy * k - size / 2))
    o = Image.new('RGBA', (size, size), (0, 0, 0, 0)); o.paste(big.crop((x0, y0, x0 + size, y0 + size)), (0, 0)); return o


if __name__ == '__main__':
    uma, hold, out = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(out, exist_ok=True)
    a, cx, cy, w, h = load(uma)
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    m = np.clip(UMA_CUT + 0.5 - np.hypot(xx + 0.5 - cx, yy + 0.5 - cy), 0, 1)             # 丸く 切る（ふちは なめらか）
    assert (a[..., 3][m >= 1] == 255).all(), '切る 丸の 中に すけた 所が ある'
    a[..., 3] = np.rint(a[..., 3] * m).astype(np.uint8)
    o = place(a, cx, cy, UMA_R / UMA_CUT, UMA_SIZE); o.save(os.path.join(out, 'tc_dp_uma7.png')); o.save(os.path.join(out, 'tc_dp_uma7.webp'), 'WEBP', quality=90, method=6, exact=False)
    print('馬バレ', (w, h), 'まん中', (cx, cy), '→ tc_dp_uma7', o.size, os.path.getsize(os.path.join(out, 'tc_dp_uma7.webp')), 'B')
    a, cx, cy, w, h = load(hold)
    o = place(a, cx, cy, HOLD_W / ((w + h) / 2), HOLD_SIZE); e = np.asarray(o)
    assert max(int(e[0, :, 3].max()), int(e[-1, :, 3].max()), int(e[:, 0, 3].max()), int(e[:, -1, 3].max())) == 0, '絵が はしで 切れて いる'
    o.save(os.path.join(out, 'tc_dp_hold7.png')); o.save(os.path.join(out, 'tc_dp_hold7.webp'), 'WEBP', quality=90, method=6, exact=False)
    print('保留', (w, h), 'まん中', (cx, cy), '→ tc_dp_hold7', o.size, os.path.getsize(os.path.join(out, 'tc_dp_hold7.webp')), 'B')
