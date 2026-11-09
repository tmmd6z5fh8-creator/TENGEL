# 神様極的中の 動画の さいごの「神様極的中」の 字を、まさちゃんの 3D（神速極光祭_Meshy の GLB）に 入れかえる（第4.136版・11/10 00:19）
#   まさちゃん「神様極的中の演出の最後の神様極的中の文字をこのファイルの神様極的中に入れ替えて！」
#   python3 kisekae/gk_emblem.py <いまの 動画 gk_film.mp4> <字の 絵（RGBA・GLB を 正面から 描いた もの）> <作業フォルダ> <出す master.mp4> [<極の 形（白黒）>]
#   ・極の 雷（まさちゃん 11/10 00:48「極の周りに金と白と虹色の雷を纏いながら、ランダムに雷が色々なところに飛んでいく演出入れて！」）：
#     ドーン（コマ 266）から 極の ふちに そって 金・白・虹色の 雷が パチパチ（2コマで 消えて 次々）・ときどき 極から 雷が いろいろな 方へ 飛ぶ（枝わかれ・3コマ）
#     細い 線＋ぼかした 光（面積が 小さい ので 点めつの きまりの 中）。乱数は コマの 番号から（何度 作っても 同じ）
#   ・動画の 8.63秒（コマ 260）から 前の 横長の 字が ドーンと 出る → 同じ 時刻・同じ 大きく なり方で 新しい 字（ほぼ 正方形）を 出す
#   ・前の 字は 消す（新しい 字に かくれない はしは まわりの 光の 筋で うめる：cv2.inpaint）・字の うしろに 金色の 後光
#   ・字の 上：光の すじ（2回）・極 の 虹の 光（ゆっくり）・宝石の きらめき・ドーンの 光の 輪（どれも 弱く：点めつの きまり 1秒に 3回まで／画面の 1割）
#   ・字の 絵と まさちゃんの GLB は リポジトリに 入れない（作業フォルダ）。できた master を build_fx_films.py の GK_MASTER に
import os, subprocess, sys
import numpy as np
import cv2

SRC, EMB, WORK, OUT = sys.argv[1:5]
GLYPH = sys.argv[5] if len(sys.argv) > 5 else None     # 極の 形（字の 絵と 同じ 大きさの 白黒：GLB の 深さで いちばん 手前の 層）
FPS, W, H = 30, 780, 1688
START, LAST = 260, 361            # コマの 番号（1から：ffmpeg の f%03d）。260＝8.63秒（前の 字が 出る）
CX, CY = 390.0, 712.0             # 字の まん中
EW = 760.0                        # 字の はば（大きく なった あと）
SCALE = {260: .40, 261: .55, 262: .70, 263: .82, 264: .92, 265: .98, 266: 1.04, 267: 1.03, 268: 1.015, 269: 1.005}     # 266＝ドーン（8.84秒）
OLD = {260: .373, 261: .518, 262: .687, 263: .77, 264: .89, 265: .96, 266: 1.0}                                       # 前の 字の 大きさ（それ より あとは 1.04）
OLD_W, OLD_H = 800.0, 400.0
SWEEPS = ((274, 292), (322, 340))  # 光の すじ
# 宝石（字の 絵の 中の 場所：横・たての 割合）→ きらめく 時刻（コマ）
JEWELS = [((0.500, 0.086), 268), ((0.074, 0.490), 281), ((0.926, 0.490), 293), ((0.623, 0.091), 305), ((0.374, 0.909), 317),
          ((0.500, 0.901), 329), ((0.374, 0.091), 341), ((0.623, 0.909), 350)]


def load_emblem(p):
    im = cv2.imread(p, cv2.IMREAD_UNCHANGED).astype(np.float32) / 255      # BGRA
    a = im[..., 3]; ys, xs = np.nonzero(a > 0.02)
    box = (max(0, ys.min() - 4), ys.max() + 5, max(0, xs.min() - 4), xs.max() + 5)
    im = im[box[0]:box[1], box[2]:box[3]]
    im[..., :3] *= im[..., 3:4]                                              # 前もって アルファを かけた 形
    return im, box


def glyph_contour(p, box):
    """極の ふち（字の 絵の 中の 点・外向きの 向き）"""
    g = cv2.imread(p, cv2.IMREAD_GRAYSCALE)[box[0]:box[1], box[2]:box[3]] > 127
    cs, _ = cv2.findContours(g.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=cv2.contourArea)[:, 0, :].astype(np.float32)
    k = 9; cp = np.concatenate([c[-k:], c, c[:k]]); sm = np.stack([np.convolve(cp[:, i], np.ones(2 * k + 1) / (2 * k + 1), 'valid') for i in range(2)], 1)
    t = np.roll(sm, -3, 0) - np.roll(sm, 3, 0); t /= np.maximum(np.linalg.norm(t, axis=1, keepdims=True), 1e-6)
    n = np.stack([t[:, 1], -t[:, 0]], 1)
    q = np.clip((sm + n * 6).round().astype(int), 0, [g.shape[1] - 1, g.shape[0] - 1])
    if g[q[:, 1], q[:, 0]].mean() > 0.5: n = -n                              # 外向きに
    return sm, n


# ---------------------------------------------------------------- 雷（極の まわり・飛ぶ 雷）
BOLT_FROM = 271          # 9.0秒（ドーンの 0.17秒 あと）から だんだん
KINDS = (('gold', .36), ('white', .30), ('rainbow', .34))


def jag(p0, p1, rng, rough=.22, depth=5):
    pts = [np.asarray(p0, np.float32), np.asarray(p1, np.float32)]
    for _ in range(depth):
        new = [pts[0]]
        for a_, b_ in zip(pts[:-1], pts[1:]):
            d = b_ - a_; L = float(np.hypot(*d)) + 1e-6; nrm = np.array([-d[1], d[0]], np.float32) / L
            new += [(a_ + b_) / 2 + nrm * rng.normal(0, rough * L), b_]
        pts = new
    return np.array(pts)


def hue_bgr(h):
    c = cv2.cvtColor(np.uint8([[[int(h / 2) % 180, 215, 255]]]), cv2.COLOR_HSV2BGR)[0, 0].astype(np.float32) / 255
    return c


def bolt_colors(kind, n, rng):
    """線の 1つずつの 色（芯・光）"""
    if kind == 'gold':
        return [((.62, .93, 1.0), (.10, .62, 1.0))] * n
    if kind == 'white':
        return [((1.0, 1.0, 1.0), (1.0, .82, .70))] * n
    h0 = rng.uniform(0, 360); out = []
    for i in range(n):
        c = hue_bgr(h0 + 320 * i / max(1, n - 1)); out.append((tuple(.35 + .65 * c), tuple(c)))
    return out


def draw_bolt(core, glow, pts, kind, inten, th, rng):
    cols = bolt_colors(kind, len(pts) - 1, rng)
    for (p, q), (cc, gc) in zip(zip(pts[:-1], pts[1:]), cols):
        P = (int(round(p[0])), int(round(p[1]))); Q = (int(round(q[0])), int(round(q[1])))
        cv2.line(core, P, Q, tuple(float(v) * inten for v in cc), max(1, int(round(th))), cv2.LINE_8)
        cv2.line(glow, P, Q, tuple(float(v) * inten for v in gc), max(2, int(round(th * 3.5))), cv2.LINE_8)


def pick_kind(rng):
    r = rng.uniform(); acc = 0
    for k, w in KINDS:
        acc += w
        if r <= acc: return k
    return KINDS[-1][0]


def bolts_for(f, cont, nrm, to_frame, s):
    """コマ f の 雷（線の 点・種類・強さ・太さ）。乱数は 生まれた コマ g と 番号から（何度 作っても 同じ）
       ・極の ふちの 雷：1つ 4〜7コマ 同じ 所に いて、形だけ 毎コマ かわる（パチパチ）→ 同じ 所が 何度も 点いたり 消えたり しない（点めつの きまり）
       ・飛ぶ 雷：3コマ（毎コマ 形が かわる・枝わかれ）・3コマに 1本 くらい・いろいろな 方へ
       ・ドーン（コマ 266）の すぐ あとは 字の 光の 輪と 砕ける 絵が あるので、雷は BOLT_FROM から だんだん 強く"""
    out = []; N = len(cont); ramp = min(1.0, max(0.0, (f - BOLT_FROM + 1) / 16.0))
    for g in range(max(BOLT_FROM, f - 7), f + 1):
        age = f - g
        # 極の ふちの 雷：毎コマ 1つ（ときどき 2つ）生まれる
        r0 = np.random.default_rng(g * 7907 + 1)
        for j in range(1 + (r0.uniform() < .35)):
            r = np.random.default_rng(g * 97 + j)
            life = int(r.integers(4, 8))
            if age >= life: continue
            env = (.55, 1.0)[min(age, 1)] if age < life - 2 else (.6, .3)[age - (life - 2)]
            i0 = int(r.integers(N)); L = int(N * r.uniform(.10, .22)); step = max(3, L // 14)
            idx = (i0 + np.arange(0, L, step)) % N
            off = r.uniform(3, 10); kind = pick_kind(r)
            rf = np.random.default_rng(g * 131 + j * 7 + f * 3)            # 形は 毎コマ かわる
            base = cont[idx] + nrm[idx] * off + rf.normal(0, 3.5, (len(idx), 2))
            pts = [base[0]]
            for a_, b_ in zip(base[:-1], base[1:]): pts += list(jag(a_, b_, rf, .3, 2)[1:])
            inten = env * ramp * r.uniform(.8, 1.0)
            out.append((to_frame(np.array(pts)), kind, inten, 2.2 * s + .5, r))
            for q in range(int(r.integers(2, 4))):                         # 外への 小さな とげ（場所は 同じ・形は かわる）
                k = int(idx[int(r.integers(len(idx)))]); a_ = cont[k] + nrm[k] * 4
                ang = np.arctan2(nrm[k][1], nrm[k][0]) + r.uniform(-.7, .7); Ls = r.uniform(18, 60)
                sp = jag(a_, a_ + Ls * np.array([np.cos(ang), np.sin(ang)]), np.random.default_rng(g * 17 + j * 5 + q + f * 11), .28, 3)
                out.append((to_frame(sp), kind, inten * .85, 1.6 * s + .4, r))
        # 飛ぶ 雷（3コマ）：BOLT_FROM＋10 から・2コマに 1本 くらい
        if age <= 2 and g >= BOLT_FROM + 10:
            r = np.random.default_rng(g * 7919 + 13)
            nf = (1 if r.uniform() < .46 else 0) + (1 if r.uniform() < .10 else 0)
            for j in range(nf):
                rr_ = np.random.default_rng(g * 104729 + j)
                k = int(rr_.integers(N)); a_ = cont[k] + nrm[k] * 3
                ang = np.arctan2(nrm[k][1], nrm[k][0]) + rr_.uniform(-.9, .9)
                A = to_frame(a_[None])[0]
                Ls = rr_.uniform(140, 260) if rr_.uniform() < .35 else rr_.uniform(300, 700)
                B = A + Ls * np.array([np.cos(ang), np.sin(ang)])
                main = jag(A, B, np.random.default_rng(g * 7 + j * 3 + age), .2, 6)          # 毎コマ 少し 形が かわる（パチパチ）
                kind = pick_kind(rr_); inten = (1.0, .65, .3)[age]
                out.append((main, kind, inten, 3.4, rr_))
                out.append(('spark', B, kind, inten if age < 2 else 0.0, rr_))       # 当たった 所の 光
                for b in range(int(rr_.integers(1, 3))):                   # 枝
                    t0 = rr_.uniform(.3, .7); P0 = main[int(t0 * (len(main) - 1))]
                    a2 = ang + rr_.choice([-1, 1]) * rr_.uniform(.35, .8); L2 = Ls * rr_.uniform(.25, .45)
                    br = jag(P0, P0 + L2 * np.array([np.cos(a2), np.sin(a2)]), np.random.default_rng(g * 11 + j * 5 + b + age), .24, 5)
                    out.append((br, kind, inten * .75, 2.0, rr_))
    return out


def fit_jewels(E):
    """宝石の 場所を 字の 絵の 中で いちばん 明るい 所に 合わせる"""
    h, w = E.shape[:2]; lum = E[..., :3].mean(2); out = []
    for (u, v), t0 in JEWELS:
        x, y = int(u * w), int(v * h); r = int(0.03 * w)
        win = lum[max(0, y - r):y + r, max(0, x - r):x + r]; j = np.unravel_index(np.argmax(win), win.shape)
        out.append(((max(0, x - r) + j[1]) / w, (max(0, y - r) + j[0]) / h, t0))
    return out


def place(E, s):
    """字を 大きさ s で まん中に 置いた（W×H の）前もって かけた 色と アルファ"""
    h, w = E.shape[:2]; ew = EW * s; eh = ew * h / w
    sw, sh = max(2, int(round(ew))), max(2, int(round(eh)))
    R = cv2.resize(E, (sw, sh), interpolation=cv2.INTER_AREA if sw < w else cv2.INTER_CUBIC)
    x0 = int(round(CX - sw / 2)); y0 = int(round(CY - sh / 2))
    C = np.zeros((H, W, 4), np.float32)
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + sw), min(H, y0 + sh)
    C[ya:yb, xa:xb] = R[ya - y0:yb - y0, xa - x0:xb - x0]
    return C, (x0, y0, sw, sh)


def supere(s, ax=0.56, by=0.62, p=4.0):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a = ax * OLD_W * s; b = by * OLD_H * s
    return (np.abs((xx - CX) / a) ** p + np.abs((yy - CY) / b) ** p) <= 1.0


def star(size, inten):
    """4本の 光の きらめき（小さい 絵）"""
    n = int(size * 2) | 1; c = n // 2; yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) - c
    r = np.sqrt(xx ** 2 + yy ** 2) + 1e-6
    core = np.exp(-(r / (size * 0.08)) ** 2)
    rays = np.exp(-np.abs(xx) / (size * 0.025)) * np.exp(-np.abs(yy) / (size * 0.42)) + np.exp(-np.abs(yy) / (size * 0.025)) * np.exp(-np.abs(xx) / (size * 0.42))
    d1 = (xx + yy) / np.sqrt(2); d2 = (xx - yy) / np.sqrt(2)
    diag = 0.45 * (np.exp(-np.abs(d1) / (size * 0.02)) * np.exp(-np.abs(d2) / (size * 0.22)) + np.exp(-np.abs(d2) / (size * 0.02)) * np.exp(-np.abs(d1) / (size * 0.22)))
    return np.clip(core + 0.8 * rays + diag, 0, 1.5) * inten


def add_at(img, spr, x, y, col):
    n = spr.shape[0]; c = n // 2; x0, y0 = int(round(x)) - c, int(round(y)) - c
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + n), min(H, y0 + n)
    if xa >= xb or ya >= yb: return
    img[ya:yb, xa:xb] += spr[ya - y0:yb - y0, xa - x0:xb - x0, None] * np.asarray(col, np.float32)


def main():
    fr = os.path.join(WORK, 'frames_src'); fo = os.path.join(WORK, 'frames_new')
    os.makedirs(fr, exist_ok=True); os.makedirs(fo, exist_ok=True)
    if not os.path.exists(os.path.join(fr, 'f%03d.png' % LAST)):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', SRC, '-vsync', '0', os.path.join(fr, 'f%03d.png')], check=True)
    E, box = load_emblem(EMB); jw = fit_jewels(E)
    cont, nrm = glyph_contour(GLYPH, box) if GLYPH else (None, None)
    # 極（虹色）の ところ：緑〜青〜紫の 色 と その まわり
    hsv = cv2.cvtColor((np.clip(E[..., :3] / np.maximum(E[..., 3:4], 1e-4), 0, 1) * 255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
    rb = (hsv[..., 0] > 32) & (hsv[..., 0] < 165) & (hsv[..., 1] > 90) & (hsv[..., 2] > 70) & (E[..., 3] > 0.5)
    ys, xs = np.nonzero(rb); kb = (xs.min(), ys.min(), xs.max(), ys.max())
    K = np.zeros(E.shape[:2], np.float32); K[kb[1]:kb[3], kb[0]:kb[2]] = 1; K = cv2.GaussianBlur(K, (0, 0), E.shape[1] * 0.02) * E[..., 3]
    Kc = E[..., :3] * K[..., None]                                   # 極の まわりの 色（光らせる 元）
    gold = np.clip((E[..., :3].mean(2) / np.maximum(E[..., 3], 1e-4) - 0.42) * 3, 0, 1) * E[..., 3]    # 明るい 金の ところ（光の すじ）
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rr = np.sqrt((xx - CX) ** 2 + (yy - CY) ** 2)
    halo_col = np.array([0.70, 0.92, 1.0], np.float32)             # BGR：あたたかい 金白
    for f in range(1, LAST + 1):
        src = os.path.join(fr, 'f%03d.png' % f); dst = os.path.join(fo, 'f%03d.png' % f)
        if f < START:
            if not os.path.exists(dst): os.link(src, dst) if os.stat(fr).st_dev == os.stat(fo).st_dev else subprocess.run(['cp', src, dst], check=True)
            continue
        img = cv2.imread(src)
        t = f - 266                                                   # ドーンからの コマ
        s = SCALE.get(f, 1.0 + 0.006 * np.sin(2 * np.pi * (f - 269) / 45.0))
        so = OLD.get(f, 1.04)
        C, (x0, y0, sw, sh) = place(E, s)
        a = C[..., 3]
        # 前の 字を 消す：新しい 字で かくれない ところだけ まわりで うめる
        core = cv2.erode((a > 0.6).astype(np.uint8), np.ones((5, 5), np.uint8))
        m = (supere(so) & (core == 0)).astype(np.uint8)
        m = cv2.dilate(m, np.ones((5, 5), np.uint8))
        if m.any(): img = cv2.inpaint(img, m * 255, 7, cv2.INPAINT_TELEA)
        b = img.astype(np.float32) / 255
        # 後光（字の うしろ）：ドーンで 強く → おちついて ゆっくり ゆれる
        kh = min(1.0, max(0.0, (f - 259) / 6.0)) * (1.0 + 0.35 * np.exp(-max(0, t) / 4.0) * (t >= 0)) * (1.0 + 0.06 * np.sin(2 * np.pi * f / 36.0))
        R0 = 0.56 * EW * s
        hal = (0.62 * kh * np.exp(-1.25 * (rr / R0) ** 2))[..., None] * halo_col
        b = 1 - (1 - b) * (1 - np.clip(hal, 0, 1))
        # ドーンの 光の 輪（字の うしろ）
        if 0 <= t <= 9:
            tau = t / 9.0; rad = R0 * (0.95 + 1.3 * tau); th = 14 * (1 - tau) + 4
            ring = np.exp(-((rr - rad) / th) ** 2) * 0.55 * (1 - tau) ** 2
            b += ring[..., None] * np.array([0.55, 0.85, 1.0], np.float32)
        # 字の かげ（明るい 光の 中で ふちを 見やすく）
        sh_ = cv2.GaussianBlur(a, (0, 0), 7); sh_ = np.roll(sh_, 5, axis=0)
        b *= (1 - 0.32 * sh_)[..., None]
        # 字
        b = C[..., :3] + b * (1 - a[..., None])
        # 極の 虹の 光（ゆっくり）
        if f >= 263:
            ki = min(1.0, (f - 262) / 5.0) * (0.20 + 0.06 * np.sin(2 * np.pi * (f - 266) / 24.0)) + (0.18 * np.exp(-max(0, t) / 3.0) if t >= 0 else 0)
            Kp, _ = place(np.dstack([Kc, K]), s)
            glow = cv2.GaussianBlur(Kp[..., :3], (0, 0), 10 * s + 2)
            b += glow * ki
        # 光の すじ（金の ところだけ）
        for f0, f1 in SWEEPS:
            if f0 <= f <= f1:
                tau = (f - f0) / (f1 - f0); d = np.array([1.0, 0.55]); d /= np.linalg.norm(d)
                u = (xx - CX) * d[0] + (yy - CY) * d[1]; span = 0.62 * (sw + sh) / 2
                c0 = -span + 2 * span * tau
                band = np.exp(-((u - c0) / (0.05 * sw + 6)) ** 2) * np.sin(np.pi * tau) ** 0.5
                Gp, _ = place(np.dstack([np.repeat(gold[..., None], 3, 2), gold]), s)
                b += (band * Gp[..., 0] * 0.42)[..., None] * np.array([0.86, 0.96, 1.0], np.float32)
        # 宝石の きらめき
        for (u, v, t0) in jw:
            k = f - t0
            if 0 <= k <= 12:
                env = np.sin(np.pi * k / 12.0) ** 2
                spr = star(max(16.0, 46 * s), 0.9 * env)
                add_at(b, spr, x0 + u * sw, y0 + v * sh, (0.85, 0.97, 1.0))
        # 極の 雷（ふちで パチパチ・いろいろな 方へ 飛ぶ）
        if cont is not None and f >= BOLT_FROM:
            hE, wE = E.shape[:2]
            to_frame = lambda q: np.stack([x0 + q[:, 0] * sw / wE, y0 + q[:, 1] * sh / hE], 1)
            core = np.zeros((H, W, 3), np.float32); glow = np.zeros((H, W, 3), np.float32)
            sparks = []
            for it in bolts_for(f, cont, nrm, to_frame, s):
                if isinstance(it[0], str): sparks.append(it[1:]); continue
                draw_bolt(core, glow, *it)
            g1 = cv2.GaussianBlur(glow, (0, 0), 4.5); g2 = cv2.GaussianBlur(glow, (0, 0), 14)
            dk = cv2.GaussianBlur(g1.max(2), (0, 0), 6)                     # 雷の まわりを 少し 暗く（明るい 金の 上でも 見える）
            b *= (1 - 0.14 * np.clip(dk, 0, 1))[..., None]
            b += cv2.GaussianBlur(core, (0, 0), .8) * 1.1 + g1 * 1.0 + g2 * .45
            for B, kind, inten, r in sparks:
                if inten > 0: add_at(b, star(26.0, 0.9 * inten), B[0], B[1], bolt_colors(kind, 1, r)[0][0])
        cv2.imwrite(dst, (np.clip(b, 0, 1) * 255 + 0.5).astype(np.uint8))
        if f % 20 == 0: print('コマ', f, flush=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS), '-i', os.path.join(fo, 'f%03d.png'), '-c:v', 'libx264', '-preset', 'slow', '-crf', '16',
                    '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-an', OUT], check=True)
    print('できた', OUT, flush=True)


if __name__ == '__main__':
    main()
