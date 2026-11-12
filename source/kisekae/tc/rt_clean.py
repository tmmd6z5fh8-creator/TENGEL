# ルーレットの 絵（3つ：ノーマル・幻の馬・神様馬）を きれいに する ＋ 神様馬・幻の馬の 目を 光らせる
#   第4.158版（まさちゃん 2026/11/12 08:59「このルーレットの神様馬、目が怖いから金色に光らせて！あと、画像がなんかまだらに色がついてるから綺麗にできる？」・
#   09:00「幻の馬のルーレットは、目を紫に光らせて！」）
#   python3 kisekae/tc/rt_clean.py <もとの 絵の フォルダ> [アプリ用の 絵の フォルダ ios/tc_assets] [--out <見る 用の フォルダ>]
#     <もとの 絵の フォルダ>：まさちゃんの 絵 rt_kamisama.png・rt_maboroshi.png・rt_normal.png（1024×1536・すき通し。リポジトリには 入れない）
#     → <アプリ用の 絵の フォルダ>/rt_<絵>_plate2.webp・rt_<絵>_knob2.webp・rt_<絵>_stick2.webp・rt_<絵>_ptr2.webp（12まい）
#   ・**前の 絵（rt_<絵>_plate.webp など）は 上書きしない・消さない**（新しい 名前で 足す）。アプリは 新しい 名前を 読む（tc/tc_fx.js）・
#     前の 絵は アプリにも 軽い 版にも 入れない（assets_dir.superseded）。足した あとは python3 kisekae/lite_assets.py
#   ・まだら ＝ 絵の 紙の もよう（折り紙の 紙の うすい 地模様：明るさ ±3〜7）。面の 中を なめらかに して、折り目・ふち・字は のこす：
#       下地 ＝ ふちを のこす ぼかし（cv2.edgePreservingFilter：広さ 40・色の 差 0.14）／細部 ＝ もとの 絵 − 下地／
#       細部の 大きさ（まわり 1.2px で ならした もの）が 7 より 小さい 所は 下地 だけ・14 より 大きい 所（折り目・ふち）は もとの 細部を ぜんぶ もどす
#   ・台紙（plate）は まさちゃんの もとの 絵（PNG）から 作り直す（いまの 台紙は 圧縮を 1回 通って いる）。レバーと 矢印を ぬいた 所 だけ いまの 台紙の 形（すき通し）を 使う
#   ・目：ひとみ（黒目）を 光の 玉に かえて、まわりに 光の にじみと 十字の きらめき。神様馬＝金色（白い 顔の 上なので 金色を かぶせる）・幻の馬＝紫（暗い 顔の 上なので 光を 足す）。
#     光が ゆっくり 息を する 動きは アプリが 足す（tc/tc_fx.js の drawEye：場所は RT_STYLE の eye＝下の EYE と 同じ）
import json, os, sys
import numpy as np, cv2
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
THEMES = ('normal', 'maboroshi', 'kamisama'); PARTS = ('knob', 'stick', 'ptr')
EYE = {'kamisama': dict(c=(641.0, 271.9), kind='gold'), 'maboroshi': dict(c=(651.4, 286.0), kind='purple')}      # 目の まん中（台紙の 画素）
Q = 92                                         # WebP の 画質（すき通しは ロスなし）
SIG_S, SIG_R, T0, T1 = 40, 0.14, 7.0, 14.0     # 下地の ぼかし（広さ・色の 差）・細部を もどす しきい（T0 より 小さい＝もどさない・T1 より 大きい＝ぜんぶ もどす）


def fill_rgb(rgb, al, thr=200):
    """すき通しの 所の 色を いちばん 近い 絵の 色で うめる（ふちで 外の 色が まざらない ように）"""
    known = (al > thr).astype(np.uint8)
    if known.all():
        return rgb.copy()
    _d, lab = cv2.distanceTransformWithLabels(1 - known, cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    ys, xs = np.nonzero(known); lut = np.zeros((lab.max() + 1, 3), np.uint8); lut[lab[ys, xs]] = rgb[ys, xs]
    return lut[lab]


def clean(rgba):
    """紙の もようを けす（折り目・ふち・字は のこす）。すき通しは かえない"""
    rgb, al = rgba[..., :3], rgba[..., 3]
    f = fill_rgb(rgb, al)
    base = cv2.edgePreservingFilter(f, flags=cv2.RECURS_FILTER, sigma_s=SIG_S, sigma_r=SIG_R).astype(np.float32)
    d = f.astype(np.float32) - base
    m = cv2.GaussianBlur(np.abs(d).max(-1), (0, 0), 1.2)
    g = np.clip((m - T0) / (T1 - T0), 0, 1); g = (g * g * (3 - 2 * g))[..., None]
    out = base + d * g
    w = np.clip((al.astype(np.float32) - 128) / 100, 0, 1)[..., None]          # ふちの 半分 すき通った 点は もとの 色の まま
    out = rgb.astype(np.float32) * (1 - w) + out * w
    return np.dstack([np.clip(out + 0.5, 0, 255).astype(np.uint8), al])


def eye_glow(rgba, cx, cy, kind, R=88, S=4):
    """目を 光の 玉に（4倍で 描いて 小さく する）"""
    out = rgba.astype(np.float32); x0, y0 = int(round(cx)) - R, int(round(cy)) - R; n = 2 * R
    box = out[y0:y0 + n, x0:x0 + n]; rgb = cv2.resize(box[..., :3], (n * S, n * S), interpolation=cv2.INTER_LINEAR)
    yy, xx = np.mgrid[0:n * S, 0:n * S].astype(np.float32)
    dx, dy = (xx + 0.5) / S + x0 - 0.5 - cx, (yy + 0.5) / S + y0 - 0.5 - cy; r = np.hypot(dx, dy)
    ss = lambda a, b, v: (lambda t: t * t * (3 - 2 * t))(np.clip((v - a) / (b - a), 0, 1))
    over = lambda img, col, a: img * (1 - a[..., None]) + np.float32(col) * a[..., None]
    flare = (np.exp(-(dy / 1.25) ** 2) * np.clip(1 - np.abs(dx) / 46, 0, 1) ** 2.2 + np.exp(-(dx / 1.25) ** 2) * np.clip(1 - np.abs(dy) / 28, 0, 1) ** 2.2 + 1.1 * np.exp(-(r / 3.4) ** 2))
    disc = 1 - ss(8.0, 9.8, r)                                                   # 光の 玉（ひとみの 大きさ）
    if kind == 'gold':
        halo = np.clip(1.0 * np.exp(-(r / 12.5) ** 2) + 0.5 * np.exp(-(r / 31.0) ** 2), 0, 1)
        rgb = rgb * (1 - halo[..., None] * (1 - np.float32((255, 180, 34)) / 255))   # 金色の にじみ（白い 顔を 金色に そめる：かけ算なので まぶたの 線は のこる）
        core = np.float32((255, 253, 228))[None, None] * (1 - ss(2.0, 8.6, r))[..., None] + np.float32((255, 214, 84))[None, None] * ss(2.0, 8.6, r)[..., None]
        rgb = rgb * (1 - disc[..., None]) + core * disc[..., None]
        rgb = over(rgb, (255, 250, 220), np.clip(flare * 0.92, 0, 1))
    else:
        glow = 0.95 * np.exp(-(r / 12.0) ** 2) + 0.46 * np.exp(-(r / 31.0) ** 2)
        rgb = rgb + np.float32((150, 62, 255))[None, None] * glow[..., None]     # 紫の 光（暗い 顔に 足す）
        core = np.float32((250, 238, 255))[None, None] * (1 - ss(2.5, 9.0, r))[..., None] + np.float32((204, 118, 255))[None, None] * ss(2.5, 9.0, r)[..., None]
        rgb = rgb * (1 - disc[..., None]) + core * disc[..., None]
        rgb = rgb + np.float32((236, 206, 255))[None, None] * np.clip(flare * 0.95, 0, 1.2)[..., None]
    rgb = cv2.resize(np.clip(rgb, 0, 255), (n, n), interpolation=cv2.INTER_AREA)
    w = np.clip((box[..., 3] - 128) / 100, 0, 1)[..., None]                      # 絵の 中 だけ
    box[..., :3] = box[..., :3] * (1 - w) + rgb * w
    return np.clip(out + 0.5, 0, 255).astype(np.uint8)


def plate_base(orig, plate):
    """もとの 絵（PNG）に、いまの 台紙で ぬいて ある 所（レバー・矢印）だけ いまの 台紙を 入れる"""
    o, p = orig.astype(np.float32), plate.astype(np.float32)
    cut = cv2.dilate(((o[..., 3] - p[..., 3]) > 40).astype(np.uint8), np.ones((17, 17), np.uint8)) > 0
    ys, xs = np.nonzero(cut)
    assert cut.any() and xs.min() > 700 and ys.min() > 600 and ys.max() < 1150, ('ぬいた 所が レバーの あたりで ない', xs.min(), ys.min(), ys.max())
    po, pp = o[..., :3] * o[..., 3:] / 255, p[..., :3] * p[..., 3:] / 255
    assert float(np.abs(po - pp)[~cut].mean()) < 4.0, 'いまの 台紙と もとの 絵が ちがう 絵'
    out = orig.copy(); out[cut] = plate[cut]
    return out, int(cut.sum())


def save(rgba, path):
    Image.fromarray(rgba, 'RGBA').save(path, 'WEBP', quality=Q, method=6, alpha_quality=100, exact=False)
    return os.path.getsize(path)


def main(src, dst, view=None):
    rep = {}
    for th in THEMES:
        orig = np.asarray(Image.open(os.path.join(src, f'rt_{th}.png')).convert('RGBA')); assert orig.shape == (1536, 1024, 4), orig.shape
        plate = np.asarray(Image.open(os.path.join(dst, f'rt_{th}_plate.webp')).convert('RGBA')); assert plate.shape == orig.shape
        base, ncut = plate_base(orig, plate)
        new = clean(base)
        if th in EYE:
            new = eye_glow(new, *EYE[th]['c'], EYE[th]['kind'])
        assert (new[..., 3] == base[..., 3]).all()
        rep[f'rt_{th}_plate2.webp'] = save(new, os.path.join(dst, f'rt_{th}_plate2.webp'))
        if view:
            os.makedirs(view, exist_ok=True); Image.fromarray(base, 'RGBA').save(os.path.join(view, f'{th}_before.png')); Image.fromarray(new, 'RGBA').save(os.path.join(view, f'{th}_after.png'))
        for p in PARTS:
            sp = np.asarray(Image.open(os.path.join(dst, f'rt_{th}_{p}.webp')).convert('RGBA'))
            rep[f'rt_{th}_{p}2.webp'] = save(clean(sp), os.path.join(dst, f'rt_{th}_{p}2.webp'))
    for k, v in rep.items():
        old = os.path.getsize(os.path.join(dst, k.replace('2.webp', '.webp')))
        print(f'{k}  {v:,} bytes（前の 絵 {old:,}）')
    print('合計', f'{sum(rep.values()):,}', '（前の 絵', f"{sum(os.path.getsize(os.path.join(dst, k.replace('2.webp', '.webp'))) for k in rep):,}", '）')


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if x != '--out' and (sys.argv.index(x) == 0 or sys.argv[sys.argv.index(x) - 1] != '--out')]
    view = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else None
    if not a:
        raise SystemExit(__doc__ or 'python3 kisekae/tc/rt_clean.py <もとの 絵の フォルダ> [ios/tc_assets] [--out <見る 用の フォルダ>]')
    main(os.path.abspath(a[0]), os.path.abspath(a[1] if len(a) > 1 else os.path.join(HERE, '..', '..', 'ios', 'tc_assets')), view)
