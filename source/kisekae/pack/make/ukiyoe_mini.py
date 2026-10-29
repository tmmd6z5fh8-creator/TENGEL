"""浮世絵風の 壁紙（壁紙パック）の 小波（小さな 大波）の 絵の 帯（WebP）を 作る。
   第4.104版 まさちゃん「小波もう少し大きくして、海が埋まるように数を増やして！」「小波は同じ絵だから数を増やして何層かに重ねて自然に見えるようにして！」：
     小波は 第4.103版と 同じ「小さな 大波」（大波の 一生の コマ＝ukiyoe.wave の シートの うち、くずれはじめて 横長に なった 所＝コマ 28〜39）。
     数を ふやしても かるく 動く ように、その 12コマを 同じ 大きさの 箱に ならべた 1本の 帯に する（ページでは 箱の 中で 帯を transform だけで
     ずらして コマを 入れかえる＝はば・高さ・背景の 場所を 動かさない）。
   1コマ：大波の コマの 絵（シートの 中の 四角）を そのまま 写す（絵を 足さない・左右に うら返さない）。
     たては コマ 28 の 上の はしを 0 に して、コマが すすんで 上の はしが 下がる ぶんの 85% を もどす（第4.103版の MW_KEEP と 同じ：白い 波が 少しずつ 低く なる）。
     上から D_CELL（大波の 絵の px）まで だけ 入れる（その 下は 列の 海の 線より 下＝見えない）。
   第4.105版 まさちゃん「小波達をいい感じに繋げて何層か作成し、海が波で見えなくなってほしい！」：
     同じ コマ（28〜39）を つないだ 波の 帯（リボン）4層も 作る（ukiyoe.ribbon）。帯の 1本は はば 390px で くり返す 絵：コマを 右から 左へ
     すきまなく 重ね（左の 波の 巻きが 右の 波の 白い 背中に かぶさる）、頭から RB_D より 下は ぼかして、波の 頭の 線より 下は ぜんぶ
     大波の 体と 同じ 藍の 体（藍 → 濃い 藍の ぼかし・明るい 青の 帯・白い すじ）で うめる（平らな 海が 見えない）。おくの 層ほど 小さく かすむ。
     層の 大きさ・高さ・かすみ は pack/ukiyoe.py の RB_ROWS。
   大波の 絵（make/ukiyoe_great.py）を 作り直したら、これも 作り直す：
   python3 kisekae/pack/make/ukiyoe_mini.py [OUT] → ios/kisekae_blobs/<id>.webp・kisekae/pack/blobs.json の ukiyoe.mini と ukiyoe.ribbon"""
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
    from pack import ukiyoe as U
    rb, rows = ribbons(U, sheet, cells, z)
    if out:
        preview_png(rb, os.path.join(out, 'uk_ribbon.png'), bg=(241, 230, 207))
    rid = save_webp(rb, quality=84)
    rmeta = dict(z=U.RB_Z, tile=U.RB_TILE, sheet=[rb.shape[1], rb.shape[0]], rows=[[y, h, round(t['top'] - U.RB_PAD, 2), vm] for (y, h, vm), t in zip(rows, U.RB_ROWS)])
    record('ukiyoe', 'ribbon', rid, rmeta)
    print('ribbon', rid, rmeta, rb.shape, flush=True)


PAL = dict(white=(246, 241, 227), light=(178, 199, 222), mid=(84, 112, 160), dark=(27, 37, 92))     # make/ukiyoe_great.py と 同じ 浮世絵の 色
HAZE = (206, 218, 230)                                                                                 # かすみの 色（空の 下の 方）


def _body(h, w, seed, R3):
    """帯の 体：藍の ぼかし（上は 藍・下は 濃い 藍）に 明るい 青の 帯と 白い すじ（ゆるい 波の 線：大波の 前の 面の ように）"""
    Rg = np.random.default_rng(seed)
    yy = np.linspace(0, 1, h)[:, None, None]
    top_c, bot_c = np.array((70, 98, 150), np.float32), np.array(PAL['dark'], np.float32)
    img = np.repeat(top_c * (1 - yy) + bot_c * yy, w, axis=1)
    xs = np.arange(w)
    light, white = np.array(PAL['light'], np.float32), np.array(PAL['white'], np.float32)
    lw = max(1, int(round(R3 * .6)))
    for i in range(int(h / (3 * R3)) + 2):
        y0 = Rg.uniform(0, h)
        amp = Rg.uniform(.5, 1.3) * R3
        per = w / int(Rg.integers(3, 7))                                  # くり返しの はばで ちょうど つながる 波の 線
        ph = Rg.uniform(0, 6.28)
        ys = (y0 + amp * np.sin(xs / per * 6.28 + ph)).astype(int)
        gap = int(Rg.integers(28, 46)) * R3
        for x in range(w):
            yi = ys[x]
            if 0 <= yi < h - lw:
                img[yi:yi + lw, x] = img[yi:yi + lw, x] * .35 + light * .65
            yw = yi + lw + 1
            if 0 <= yw < h - lw and (x // gap + i) % 3 != 0:
                img[yw:yw + lw, x] = img[yw:yw + lw, x] * .3 + white * .7
    return img


def _cut(im, z, d_top, d_fade):
    """コマ（色・アルファ）の 上から d_top だけ（その 下は d_fade で ぼかす：大波の 絵の px）"""
    im = im.copy()
    yy = np.arange(im.shape[0])[:, None] / z
    im[..., 3] *= np.clip((d_top - yy) / d_fade, 0, 1)
    return im


def ribbons(U, sheet, cells, z):
    """つないだ 波の 帯 4層（U.RB_ROWS）を 1まいの シートに たてに ならべる"""
    R3, TW = U.RB_Z, U.RB_TILE
    Wd = int(TW * R3)
    frames = []
    for k in range(F0, F1 + 1):
        x, y, w, h, ox, oy = cells[k - 1]
        im = sheet[y:y + h, x:x + w].astype(np.float32)
        a = im[..., 3:4] / 255.0
        frames.append(_cut(np.concatenate([im[..., :3] * a, a], 2), z, U.RB_D, U.RB_FADE))      # 色×アルファ・アルファ（0..1）
    tiles, rows = [], []
    for r, p in enumerate(U.RB_ROWS):
        Rg = np.random.default_rng(p['seed'])
        top = p['top'] - U.RB_PAD
        H = int(round((U.RB_BOT - top) * R3))
        # 1回り（TW）ぶんの 波の ならび：となりと 同じ コマに しない・倍率と 高さを 少し ずつ かえる
        items, x, prev = [], 0.0, -1
        while x < TW:
            k = int(Rg.integers(0, len(frames)))
            if k == prev:
                k = (k + 3) % len(frames)
            prev = k
            s = Rg.uniform(*p['s'])
            cw = frames[k].shape[1] / z * s
            items.append((x, k, s, Rg.uniform(-.8, 1.0)))
            x += cw * Rg.uniform(U.RB_STEP - .06, U.RB_STEP + .06)
        fx = TW / x                                                       # ならびの 長さを TW に そろえる（くり返しで つながる）
        allits = [(xi * fx + rep * TW, k, s, dy) for rep in (-1, 0, 1) for xi, k, s, dy in items]
        allits.sort(key=lambda t: -t[0])                                  # 右から 左へ 重ねる（左の 波が 上）
        pad = Wd
        can = np.zeros((H, Wd + 2 * pad, 4), np.float32)
        for xi, k, s, dy in allits:
            f_ = s * R3 / z
            src0 = frames[k]
            nw, nh = max(1, int(round(src0.shape[1] * f_))), max(1, int(round(src0.shape[0] * f_)))
            src = cv2.resize(src0, (nw, nh), interpolation=cv2.INTER_AREA)
            y0 = int(round((U.RB_PAD + dy) * R3))
            x0 = int(round(xi * R3)) + pad
            ya, yb = max(0, y0), min(H, y0 + nh)
            xa, xb = max(0, x0), min(can.shape[1], x0 + nw)
            if yb <= ya or xb <= xa:
                continue
            sv = src[ya - y0:yb - y0, xa - x0:xb - x0]
            dv = can[ya:yb, xa:xb]
            a = sv[..., 3:4]
            dv[..., :3] = sv[..., :3] + dv[..., :3] * (1 - a)
            dv[..., 3:4] = a + dv[..., 3:4] * (1 - a)
        tile = can[:, pad:pad + Wd]
        # 波の 頭の 線（いちばん 上の 不透明な 所：波の ない 列は となりを つなぐ・くり返しの はしも つなぐ・少し なめらかに）より 下を 体で うめる
        alpha = tile[..., 3]
        has = alpha.max(axis=0) > .5
        env = np.argmax(alpha > .5, axis=0).astype(np.float32)
        cols = np.arange(Wd)
        cx = np.concatenate([cols[has] - Wd, cols[has], cols[has] + Wd])
        env = np.interp(cols, cx, np.concatenate([env[has]] * 3)).astype(np.float32)
        kk = int(R3 * 3) | 1
        envs = cv2.GaussianBlur(np.tile(env[None, :], (1, 3)), (kk * 3, 1), 0)[0, Wd:2 * Wd]
        env = np.maximum(env, envs) + U.RB_DROP * R3
        below = np.arange(H)[:, None] >= env[None, :]
        bd = _body(H, Wd, p['seed'] + 7, R3)
        a = alpha[..., None]
        col = tile[..., :3] / np.maximum(a, 1e-4)
        col = np.where(below[..., None], col * a + bd * (1 - a), col)
        al = np.where(below, 1.0, alpha)
        if p.get('haze'):
            col = col * (1 - p['haze']) + np.array(HAZE, np.float32) * p['haze']
        out = np.concatenate([np.clip(col, 0, 255), np.clip(al * 255, 0, 255)[..., None]], 2).astype(np.uint8)
        out[..., :3][out[..., 3] == 0] = 0
        vmax = float((env.max() - env.min()) / R3)                       # 頭の 線の でこぼこ（画面の px：動く 小波が かくれる 深さに）
        tiles.append(out)
        rows.append((H, round(vmax + U.RB_DROP, 2)))
    gap = 4
    SH = sum(t.shape[0] for t in tiles) + gap * (len(tiles) - 1)
    big = np.zeros((SH, Wd, 4), np.uint8)
    y, meta_rows = 0, []
    for t, (H, vm) in zip(tiles, rows):
        big[y:y + H] = t
        meta_rows.append([y, H, vm])
        y += H + gap
    return big, meta_rows


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    main(a[0] if a else os.environ.get('OUT'))
