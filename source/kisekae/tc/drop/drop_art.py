# まさちゃんの 馬バレ（6色の メダル）・保留（6色の 宝石）を アプリ用に そろえる：大きさ・まん中を 6まいで 同じに
#   python3 -I drop_art.py <もとの フォルダ（01〜12）> <出力の フォルダ>
import sys, os, math
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import numpy as np
from PIL import Image
import art_fit as AF

UMA_SIZE, UMA_R = 344, 170          # 馬バレ：絵の 大きさ・色の 丸の 半径（画素）
UMA_IN = 0.818                      # 金の 枠の 内がわ＝外の 半径の 0.824倍（6まいとも）。その 少し 内がわで 丸く 切る
#   まさちゃん 2026/11/15 01:08「サイズ合うなら馬バレアイコンの金の枠無くして、馬バレの縁に合わせた方が綺麗かもね！」
#   → 金の 枠は 使わない：中の 色の 丸 だけを、台の 黄色い 縁（液晶の 丸）に ぴったり はめる
HOLD_SIZE, HOLD_W = 200, 180        # 保留：絵の 大きさ・八角の はば（辺から 辺）


def fit_circle(al):
    mb = AF.main_blob(al)
    ys, xs = np.nonzero(mb); cx, cy = xs.mean(), ys.mean()
    for _ in range(3):
        rr = AF.radial(mb, cx, cy)
        ang = 2 * math.pi * np.arange(len(rr)) / len(rr)
        px, py = cx + rr * np.cos(ang), cy + rr * np.sin(ang)
        A = np.c_[2 * px, 2 * py, np.ones(len(px))]; b = px ** 2 + py ** 2
        sol, *_ = np.linalg.lstsq(A, b, rcond=None)
        cx, cy = sol[0], sol[1]; R = math.sqrt(sol[2] + cx * cx + cy * cy)
    return cx, cy, R


def fit_oct(al):
    mb = AF.main_blob(al)
    ys, xs = np.nonzero(mb)
    return (xs.min() + xs.max() + 1) / 2, (ys.min() + ys.max() + 1) / 2, ((xs.max() - xs.min() + 1) + (ys.max() - ys.min() + 1)) / 2


def place(im, cx, cy, k, size):
    """もとの (cx,cy) を 新しい 絵の まん中に・k倍に して size×size に"""
    s = 1 / k
    half = size / 2 * s
    return im.transform((size, size), Image.AFFINE, (s, 0, cx - half, 0, s, cy - half), resample=Image.BICUBIC) if False else \
        im.resize((int(round(im.width * k)), int(round(im.height * k))), Image.LANCZOS).crop((int(round(cx * k - size / 2)), int(round(cy * k - size / 2)), int(round(cx * k - size / 2)) + size, int(round(cy * k - size / 2)) + size))


def premul_resize(im, k):
    a = np.asarray(im).astype(np.float32) / 255
    pm = np.dstack([a[..., :3] * a[..., 3:], a[..., 3:]])
    w, h = int(round(im.width * k)), int(round(im.height * k))
    ch = [np.asarray(Image.fromarray(pm[..., c]).resize((w, h), Image.LANCZOS)) for c in range(4)]
    o = np.dstack(ch); al = np.clip(o[..., 3:], 0, 1)
    rgb = np.where(al > 1e-4, o[..., :3] / np.maximum(al, 1e-4), 0)
    return Image.fromarray((np.clip(np.dstack([rgb, al]), 0, 1) * 255 + 0.5).astype(np.uint8), 'RGBA')


if __name__ == '__main__':
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    fs = sorted(f for f in os.listdir(src) if f.endswith('.png'))
    assert len(fs) == 12, fs
    for i, f in enumerate(fs):
        im = Image.open(os.path.join(src, f)).convert('RGBA')
        al = np.asarray(im)[..., 3]
        if i < 6:
            cx, cy, R = fit_circle(al); rin = R * UMA_IN; k = UMA_R / rin; size = UMA_SIZE; name = f'tc_dp_uma{i + 1}'
            yy, xx = np.mgrid[0:im.height, 0:im.width]
            m = np.clip(rin + 0.5 - np.hypot(xx + 0.5 - cx, yy + 0.5 - cy), 0, 1)          # 丸く 切る（ふちは なめらか）
            a4 = np.asarray(im).copy(); a4[..., 3] = np.rint(a4[..., 3] * m).astype(np.uint8); im = Image.fromarray(a4, 'RGBA')
        else:
            cx, cy, w = fit_oct(al); k = HOLD_W / w; size = HOLD_SIZE; name = f'tc_dp_hold{i - 5}'
        big = premul_resize(im, k)
        x0, y0 = int(round(cx * k - size / 2)), int(round(cy * k - size / 2))
        o = Image.new('RGBA', (size, size), (0, 0, 0, 0)); o.paste(big.crop((x0, y0, x0 + size, y0 + size)), (0, 0))
        a = np.asarray(o)
        edge = max(int(a[0, :, 3].max()), int(a[-1, :, 3].max()), int(a[:, 0, 3].max()), int(a[:, -1, 3].max()))
        o.save(os.path.join(out, name + '.png'))
        o.save(os.path.join(out, name + '.webp'), 'WEBP', quality=90, method=6, exact=False)
        print(f'{f} → {name}: k {k:.4f} center ({cx:.1f},{cy:.1f}) size {size} edge alpha {edge} webp {os.path.getsize(os.path.join(out, name + ".webp"))} B')
