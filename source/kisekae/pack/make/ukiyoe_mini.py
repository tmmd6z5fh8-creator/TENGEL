"""浮世絵風の 壁紙（壁紙パック）の 小波の 層（WebP）を 作る。
   第4.106版 まさちゃん「小波を各層ごとに絵をつなげて一個の層を一つの絵みたいに小波が個々にならないようにして！
   あと小波の青の部分画面上に見えるところ増やして！」：
     小波の 層 4つを、それぞれ 1まいの つながった 絵に した（ukiyoe.ribbon：1つの 層＝はば 390px で くり返す 絵 2本）。
     ・波の 頭（ukRc）：大波の 一生の コマ（ukiyoe.wave の シート）の うち くずれはじめて 横長に なった 所（コマ 26〜40）の
       頭の 線に そって ほどいた 帯（墨の 線・白い 泡・その 下の 爪と 藍の 顔）を 切れめ なく つないで、ゆるく うねる 頭の 線
       （トロコイド：頭が 少し とがり、谷は ひろい・前（右）が 少し 急）に そって 巻きもどした もの。列ごとに 白の 下の はし
       （爪の はじまり）を そろえて 白い 泡を うすく（頭の 所だけ 少し 厚く）、爪の すき間と その 下は 藍＝青が ふえる。
     ・波の 体（ukRb）：大波の 体と 同じ 藍の ぼかしに 明るい 青の 短い 弧（さざなみ・上に 墨の ふち）。
       上の はしは 頭の 帯の 下に かくれる（平らな 海が 見えない）。いちばん 手前の 層の 体は 石の 土手の うしろまで。
     おくの 層ほど 小さく かすむ（かすみの 色を まぜる）。層の 場所・大きさ・うねり は pack/ukiyoe.py の RB_ROWS と RB_*。
     第4.104版〜第4.105版の 動く 小波の 帯（ukiyoe.mini）は やめた（blobs.json から 消す）。
   大波の 絵（make/ukiyoe_great.py）を 作り直したら、これも 作り直す（第4.107版で 大波の コマを のびない 形に 作り直した ときは
   作り直して いない：いまの ukiyoe.ribbon は 第4.106版の 大波の コマ 26〜40 から 作った もの。いま 動かすと 小波の 形が 少し かわる）：
   python3 kisekae/pack/make/ukiyoe_mini.py [OUT] → ios/kisekae_blobs/<id>.webp・kisekae/pack/blobs.json の ukiyoe.ribbon
   第4.108版：層ごとの 波の 頭の 線（帯の 上の ふち）を はかって ukiyoe.ribbon の edge に 入れる（pack/ukiyoe.py の 帆かけ舟が
   すぐ 前の 層の 波の 頭に のって 上下し かたむく）。絵を 作り直さずに edge だけ 入れる：python3 kisekae/pack/make/ukiyoe_mini.py --edge"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))          # kisekae
from sheets import save_webp, record, preview_png, BLOB_DIR  # noqa: E402
import json  # noqa: E402
import numpy as np  # noqa: E402
import cv2  # noqa: E402

FRAMES = (26, 28, 30, 32, 34, 36, 38, 40)    # 使う コマ（1 から かぞえる ukiyoe.wave の cells）：くずれはじめて 横長に なった 大波
TRIM = (14, 22)                              # 使える 列の かたまりの 左右の はしを けずる（シートの 画素）
PAL = dict(white=(246, 241, 227), light=(178, 199, 222), mid=(84, 112, 160), dark=(27, 37, 92))     # make/ukiyoe_great.py と 同じ 浮世絵の 色
HAZE = (206, 218, 230)                       # かすみの 色（空の 下の 方）
BODY_C = (52, 78, 136)                       # 体の 上の 色（頭の 帯の 下地も 同じ 色）
INK = (24, 32, 82)


def frame(sheet, cells, k):
    """コマ k（色×アルファ・アルファ：0..1）"""
    x, y, w, h, ox, oy = cells[k - 1]
    im = sheet[y:y + h, x:x + w].astype(np.float32) / 255.0
    im[..., :3] *= im[..., 3:4]
    return im


def unroll(im, Dr, sig=2.5, up=3.0):
    """頭の 線（いちばん 上の 不透明な 所を ならした 線）に そって ほどく：行 0 が 線の up 上・下へ Dr 行"""
    a = im[..., 3]
    has = (a > .5).any(axis=0)
    top = np.argmax(a > .5, axis=0).astype(np.float32)
    cols = np.arange(im.shape[1], dtype=np.float32)
    top = np.interp(cols, cols[has], top[has]).astype(np.float32)
    base = cv2.GaussianBlur(top[None, :], (0, 0), sig)[0] - up
    my = (base[None, :] + np.arange(Dr, dtype=np.float32)[:, None]).astype(np.float32)
    mx = np.tile(cols[None, :], (Dr, 1)).astype(np.float32)
    U = cv2.remap(im, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    U[:, ~has] = 0
    return U, has


def col_align(im, cap, gw, Dc, thr, Dr=220, sig=5.0, valid_a=.75, wthr=.7):
    """ほどいた 帯で、列ごとに 白い 泡の 下の はし（濃い 藍の 爪が はじまる 所）を そろえる。
       出す 行：0..cap（頭の 墨の 線）・cap..cap+gw（爪の すぐ 上の 白い 泡）・その 下 Dc（爪と 藍の 顔）。
       返り値：(帯, 使える 列の かたまり [(x0, x1)…])"""
    U, has = unroll(im, Dr)
    a = U[..., 3]
    col = U[..., :3] / np.maximum(a[..., None], 1e-4)
    dark = (a > .5) & (col[..., 0] < thr)
    dark[:8] = False
    white = (a > .5) & (col[..., 0] > .82) & (col[..., 2] > .8)
    W_ = U.shape[1]
    yw = np.array([np.argmax(dark[:, x]) if dark[:, x].any() else -1 for x in range(W_)], np.float32)
    ok = (yw > 0) & has
    sw = np.zeros(W_, np.float32)
    sa = np.zeros(W_, np.float32)
    for x in np.where(ok)[0]:
        y0 = int(yw[x])
        if y0 - gw < cap + 1 or y0 + Dc > Dr:
            ok[x] = False
            continue
        sw[x] = white[y0 - gw:y0, x].mean()                  # 爪の 上が 白い 泡か
        sa[x] = a[y0:y0 + Dc, x].mean()                      # 爪と 顔が つまって いるか
    k_ = np.ones(15, np.float32) / 15
    n_ = np.maximum(np.convolve(ok.astype(np.float32), k_, mode='same'), 1e-3)
    ok = ok & (np.convolve(sw * ok, k_, mode='same') / n_ > wthr) & (np.convolve(sa * ok, k_, mode='same') / n_ > valid_a)
    xs = np.arange(W_, dtype=np.float32)
    if ok.sum() < 20:
        return None, []
    yws = cv2.GaussianBlur(np.interp(xs, xs[ok], yw[ok]).astype(np.float32)[None, :], (0, 0), sig)[0]
    Dout = cap + gw + Dc
    v = np.arange(Dout, dtype=np.float32)[:, None]
    src = np.where(v < cap, v, np.where(v < cap + gw, yws[None, :] - gw + (v - cap), yws[None, :] + (v - cap - gw)))
    R = cv2.remap(U, np.tile(xs[None, :], (Dout, 1)), src.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    okd = cv2.dilate(ok.astype(np.uint8)[None, :], np.ones((1, 5), np.uint8))[0].astype(bool)
    runs, x = [], 0
    while x < W_:
        if okd[x]:
            x0 = x
            while x < W_ and okd[x]:
                x += 1
            if x - x0 >= 40:
                runs.append((x0, x))
        x += 1
    return R, runs


def sources(sheet, cells, U):
    """つなぐ 材料：コマ FRAMES の 爪と 顔の ある 所（波の 右がわ）の 帯（下の はしは ぼかす）"""
    regs = []
    for k in FRAMES:
        R, runs = col_align(frame(sheet, cells, k), U.RB_CAP, U.RB_GW, U.RB_DC, U.RB_THR)
        for x0, x1 in runs:
            if x0 < .3 * R.shape[1]:                              # 白い 背中の 所は 使わない
                continue
            a, b = x0 + TRIM[0], x1 - TRIM[1]
            if b - a > 60:
                regs.append(R[:, a:b])
    n = regs[0].shape[0]
    fade = np.clip((n - np.arange(n)) / U.RB_FADE, 0, 1)[:, None, None]
    return [r * fade for r in regs]


def assemble(regs, Lf, rng, XF=24, Lmin=80, Lmax=170):
    """材料を 右へ つないで はば Lf の くり返す 帯に（つなぎめと くり返しの はしは XF で まぜる）"""
    Dr = regs[0].shape[0]
    S = np.zeros((Dr, int(Lf) + XF + 600, 4), np.float32)
    x, prev = 0, None
    while x < Lf + XF:
        i = int(rng.integers(0, len(regs)))
        if i == prev:
            i = (i + 1) % len(regs)
        prev = i
        R = regs[i]
        L = min(int(rng.integers(Lmin, Lmax)), R.shape[1] - 2)
        s0 = int(rng.integers(0, max(1, R.shape[1] - L)))
        seg = R[:, s0:s0 + L]
        w = seg.shape[1]
        if x == 0:
            S[:, :w] = seg
            x = w
        else:
            ramp = np.clip(np.arange(w) / XF, 0, 1)[None, :, None]
            xa = x - XF
            S[:, xa:xa + w] = S[:, xa:xa + w] * (1 - ramp) + seg * ramp
            x = xa + w
    Lf = int(Lf)
    ramp = np.clip(np.arange(XF) / XF, 0, 1)[None, :, None]
    T = S[:, :Lf].copy()
    T[:, :XF] = S[:, Lf:Lf + XF] * (1 - ramp) + S[:, :XF] * ramp
    return T


def troch(r, n=400):
    """トロコイド（頭が 少し とがり 谷は ひろい）：t（0..1）→ 高さ（0..1：t=0.5 が 頭）"""
    ph = np.linspace(-np.pi, np.pi, n)
    X = (ph + np.pi - r * np.sin(ph + np.pi)) / (2 * np.pi)
    Y = (np.cos(ph) + 1) / 2
    return lambda t: np.interp(t, X, Y)


def crest_line(n, A, W, rng, r, peak, jit=(.8, 1.2), hmin=.7, sm=5):
    """くり返す 波の 頭の 線（0..A：大きい ほど 下）：n この 頭（前＝右が 少し 急：peak）"""
    xs = np.arange(W, dtype=np.float64)
    ws = rng.uniform(*jit, n)
    ws = ws / ws.sum() * W
    edges = np.concatenate([[0], np.cumsum(ws)])
    y = np.zeros(W)
    g = math.log(.5) / math.log(peak)
    F = troch(r)
    for i in range(n):
        a, b = edges[i], edges[i + 1]
        h = A * rng.uniform(hmin, 1.0)
        t = np.clip((xs - a) / (b - a), 0, 1)
        m = (xs >= a) & (xs < b)
        y[m] = (A - h * F(t ** g))[m]
    yy = np.concatenate([y, y, y]).astype(np.float32)
    return cv2.GaussianBlur(yy[None, :], (sm | 1, 1), 0)[0][W:2 * W]


def body(H, W, seed, u, gap=2.0, lw=.5, L=(10, 18), h=(.5, .9), dens=.8, y_first=1.2, ink_a=.5, alpha=.6):
    """波の 体（くり返す）：藍の ぼかし（上は BODY_C・下は 濃い 藍）に 明るい 青の 短い 弧（さざなみ：まん中が 上がる・上に 墨の ふち）。
       u：画面の 1px あたりの 画素 × 大きさ"""
    R = np.random.default_rng(seed)
    yy = np.linspace(0, 1, H)[:, None, None]
    tc, bc = np.array(BODY_C, np.float32) / 255, np.array(PAL['dark'], np.float32) / 255
    img = np.repeat(tc * (1 - yy ** .7) + bc * yy ** .7, W, axis=1).astype(np.float32)
    light, ink = np.array(PAL['light'], np.float32) / 255, np.array(INK, np.float32) / 255
    SS = 4
    big = np.zeros((H * SS, W * SS), np.float32)
    edge = np.zeros_like(big)
    y0 = y_first * u
    while y0 < H - 1:
        x = R.uniform(0, 1) * L[1] * u
        while x < W + L[1] * u:
            ln, hh = R.uniform(*L) * u, R.uniform(*h) * u
            t = np.linspace(0, 1, 24)
            pts = np.stack([np.linspace(x, x + ln, 24), y0 + R.uniform(-.25, .25) * u - hh * np.sin(np.pi * t) ** 1.2], 1) * SS
            for dx in (-W, 0, W):                                      # くり返しの はしで つながる
                cv2.polylines(big, [(pts + np.array([dx * SS, 0])).astype(np.int32)], False, 1.0, thickness=max(1, int(round(lw * u * SS))), lineType=cv2.LINE_AA)
                cv2.polylines(edge, [(pts + np.array([dx * SS, -lw * u * SS * .9])).astype(np.int32)], False, 1.0, thickness=max(1, int(round(.35 * u * SS))), lineType=cv2.LINE_AA)
            x += ln * R.uniform(1.25, 1.9) / dens
        y0 += gap * u * R.uniform(.85, 1.15)
    m = cv2.resize(big, (W, H), interpolation=cv2.INTER_AREA)[..., None]
    e = cv2.resize(edge, (W, H), interpolation=cv2.INTER_AREA)[..., None] * (1 - m)
    img = img * (1 - e * ink_a) + ink * e * ink_a
    return img * (1 - m * alpha) + light * m * alpha


def layer(U, regs, k, z):
    """層 k：(頭の 帯 RGBA, 体 RGB, 体の 上の はし（頭の 帯の 上から：画面の px）)"""
    p = U.RB_ROWS[k]
    Z = U.RB_Z
    rng = np.random.default_rng(p['seed'])
    s = p['s']
    T = assemble(regs, U.RB_TILE * z / s, rng)
    f_ = Z * s / z                                                   # シートの 画素 → 出す 画素
    Wo, Ho = U.RB_TILE * Z, int(round(T.shape[0] * f_))
    Tb = cv2.resize(T, (Wo, Ho), interpolation=cv2.INTER_AREA)
    A = p['A'] * Z
    yc = crest_line(p['n'], A, Wo, rng, U.RB_R, U.RB_PEAK)
    Tc = (U.RB_CAP + U.RB_GW) * f_                                   # 墨の 線と 白い 泡の 厚さ（出す 画素）
    ext = U.RB_BETA * (A - yc)                                       # 頭ほど 白い 泡が 厚い
    Hc = int(math.ceil(A + Ho + ext.max())) + 2
    d = np.arange(Hc, dtype=np.float32)[:, None] - yc[None, :].astype(np.float32)
    mm = (1 + ext / Tc)[None, :].astype(np.float32)
    my = np.where(d < Tc * mm, d / mm, d - Tc * (mm - 1)).astype(np.float32)
    mx = np.tile(np.arange(Wo, dtype=np.float32)[None, :], (Hc, 1))
    C = cv2.remap(Tb, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    # 爪の すき間と 帯の 下は 藍の 下地（体の 上の 色）：墨の 線の 下から・帯の 下の はしで ぼかす
    b0 = U.RB_BSTART * s * Z
    fd = U.RB_FADE / z * s * Z
    ab = np.clip((my - b0) / 1.5, 0, 1) * np.clip((Ho - my) / fd, 0, 1)
    bc = np.array(BODY_C, np.float32) / 255
    C = C + np.concatenate([bc[None, None, :] * ab[..., None], ab[..., None]], 2) * (1 - C[..., 3:4])
    # 体の 上の はし：頭の 線の いちばん 下より 下（体が 頭の 上に 出ない）・頭の 帯の 下地が 体の 上の はしを かくす
    bt = int(math.ceil(A + b0 + 1))
    cover = (yc + ext + Ho - fd).min()
    assert cover >= bt + 1, (k, cover, bt)
    nxt = U.RB_ROWS[k + 1] if k + 1 < len(U.RB_ROWS) else None
    bot = min(U.RB_BOT, nxt['top'] + nxt['A'] + U.RB_UNDER) if nxt else U.RB_BOT
    Hb = int(round((bot - p['top']) * Z)) - bt
    bd = body(Hb, Wo, p['seed'] + 7, Z * max(.5, s * 3.0))
    if p['haze']:
        hz = np.array(HAZE, np.float32) / 255
        C[..., :3] = C[..., :3] * (1 - p['haze']) + hz * C[..., 3:4] * p['haze']
        bd = bd * (1 - p['haze']) + hz * p['haze']
    a = np.clip(C[..., 3:4], 1e-4, 1)
    crest = np.concatenate([np.clip(C[..., :3] / a, 0, 1) * 255, np.clip(C[..., 3:4], 0, 1) * 255], 2).astype(np.uint8)
    crest[..., :3][crest[..., 3] == 0] = 0
    bod = np.concatenate([np.clip(bd, 0, 1) * 255, np.full(bd.shape[:2] + (1,), 255, np.float32)], 2).astype(np.uint8)
    return crest, bod, bt / Z


def edges(big, rows, z, tile, thr=.5, q=.02):
    """層ごとの 波の 頭の 帯の 上の ふち（こさ thr を こえる 所：その 上は すけて うしろが 見える）を 画面の 1px ごとに はかる（第4.108版）。
       返り値：層ごとの 文字（帯の 上から 下へ の px を q px 単位の 16進 2けたで 1px ごとに ならべた もの）。big：シート（色 4つ・4つ目が こさ）"""
    out = []
    for cy, ch, by, bh, bt in rows:
        a = big[cy:cy + ch, :, 3].astype(np.float64) / 255
        c = np.arange(a.shape[1])
        i = np.argmax(a > thr, axis=0)
        v0, v1 = a[np.maximum(i - 1, 0), c], a[i, c]
        e = np.where(i == 0, 0.0, i - 1 + (thr - v0) / np.maximum(1e-6, v1 - v0))     # シートの 画素（帯の 上から）
        e = e.reshape(tile, -1).mean(1) / z                                            # 画面の px（1px ごと）
        out.append(''.join('%02x' % int(round(min(255.0, x / q))) for x in e))
    return out


def edge_only():
    """いまの ukiyoe.ribbon の 絵は そのまま、波の 頭の 線（edge）だけ はかって blobs.json に 入れる（第4.108版）"""
    R = json.load(open(os.path.join(os.path.dirname(HERE), 'blobs.json'), encoding='utf-8'))['ukiyoe']['ribbon']
    big = cv2.imread(os.path.join(BLOB_DIR, R['id'] + '.webp'), cv2.IMREAD_UNCHANGED)
    meta = {k: v for k, v in R.items() if k != 'id'}
    meta['edge'] = edges(big, R['rows'], R['z'], R['tile'])
    record('ukiyoe', 'ribbon', R['id'], meta)
    print('ribbon edge', R['id'], [len(e) for e in meta['edge']], flush=True)


def main(out=None):
    B = json.load(open(os.path.join(os.path.dirname(HERE), 'blobs.json'), encoding='utf-8'))['ukiyoe']['wave']
    z = B['z']
    sheet = cv2.imread(os.path.join(BLOB_DIR, B['id'] + '.webp'), cv2.IMREAD_UNCHANGED)
    sheet = cv2.cvtColor(sheet, cv2.COLOR_BGRA2RGBA)
    from pack import ukiyoe as U
    regs = sources(sheet, B['cells'], U)
    gap = 4
    parts, rows, y = [], [], 0
    for k in range(len(U.RB_ROWS)):
        crest, bod, bt = layer(U, regs, k, z)
        rows.append([y, crest.shape[0], y + crest.shape[0] + gap, bod.shape[0], round(bt, 4)])
        parts += [crest, bod]
        y += crest.shape[0] + bod.shape[0] + 2 * gap
    Wd = U.RB_TILE * U.RB_Z
    big = np.zeros((y - gap, Wd, 4), np.uint8)
    for (cy, ch, by, bh, _), (crest, bod) in zip(rows, zip(parts[::2], parts[1::2])):
        big[cy:cy + ch] = crest
        big[by:by + bh] = bod
    if out:
        os.makedirs(out, exist_ok=True)
        preview_png(big, os.path.join(out, 'uk_ribbon.png'), bg=(241, 230, 207))
    rid = save_webp(big, quality=84)
    # rows：[頭の 帯の y, 高さ, 体の y, 高さ, 体の 上の はし（頭の 帯の 上から・画面の px）]（シートの 画素）
    back = cv2.imread(os.path.join(BLOB_DIR, rid + '.webp'), cv2.IMREAD_UNCHANGED)       # できた 絵から 波の 頭の 線を はかる（第4.108版）
    rmeta = dict(z=U.RB_Z, tile=U.RB_TILE, sheet=[big.shape[1], big.shape[0]], rows=rows, edge=edges(back, rows, U.RB_Z, U.RB_TILE))
    record('ukiyoe', 'ribbon', rid, rmeta)
    from ukiyoe_great import forget
    forget('ukiyoe', 'mini')                                          # 第4.104版〜第4.105版の 動く 小波の 帯（もう 使わない）
    print('ribbon', rid, rmeta, big.shape, os.path.getsize(os.path.join(BLOB_DIR, rid + '.webp')), flush=True)


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    if '--edge' in sys.argv:
        edge_only()
    else:
        main(a[0] if a else os.environ.get('OUT'))
