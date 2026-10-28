"""近未来都市の 壁紙（壁紙パック・第4.92版）の 走る 馬：いままでの 壁紙と 同じ 馬（horse_flat）の ギャロップ（flat/sea_run.py と 同じ 足の 動き）を、
   黒に 近い 鉄の 色の 体・水色に 光る たてがみと しっぽ・水色の 光の 帯の 布で 描いて、まわりに 水色の 光（ぼかした ふち）と、
   体の 上の ふちに 細い 光の 線（リムライト）を 足す。右を 向いて 光の レーンを 走る（10コマ）。
   第4.93版（まさちゃん「常に足元に青い雷を纏っているようにして！」）：ひづめの まわりに いつも 水色の 光の もや（馬の シートに 入れる）と、
   ぱちぱち 走る 細い 雷（雷だけの シート 3まい＝形の ちがう 3とおり。馬と 同じ 10コマ・同じ 切りぬき＝ページで 馬と いっしょに めくり、
   3まいを 0.1秒ずつ 入れかえて ぱちぱち させる）。雷は コマごとの ひづめの 場所から 外へ（下・うしろ・横）・枝わかれ・手前と 奥の 足の あいだを つなぐ 弧も。
   第4.94版（まさちゃん「黄丸の脚の雷はもっと線細く！」「脚の雷の光が通ったところに光の線が残っているような演出して！」）：
   雷の 線を 細く（芯は 2倍の 画素で 1・まわりの 光は うすく）。ひづめの 通った あとに 光の すじ（trail：20コマの シート＝ギャロップ 1回りの 中の 20の 時刻）。
   すじは ひづめが 通った 所（地面＝レーンの 上で 止まって 見える 所）に 残って レーンと 同じ はやさで うしろへ 流れ、0.5秒で うすく 消える
   （光で 絵を 描いた ような あと：宙を けった ひづめの 弧と 地面の 光の 点）。レーンの はやさは 地面に ついた ひづめの はやさ（speed：ページの px／秒）。
   すじの 先は いちばん 新しい 馬の コマの ひづめ（コマが かわる まで は その ひづめから うしろへ 流れる 所だけ）＝すじが ひづめより 前に 出ない
   python3 kisekae/pack/make/future_art.py   → ios/kisekae_blobs/<id>.webp・kisekae/pack/blobs.json の future.run・future.bolt0〜2・future.trail"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sheets import gallop_sheet, save_webp, record, preview_png, render, gallop_poses, gallop_stance, ground_dy, W2, H2  # noqa: E402
import numpy as np  # noqa: E402
import cv2  # noqa: E402
from cute_horse import smooth, path, stroke, circ, unit, V, f2  # noqa: E402

PAL = dict(body='#2E3448', shade='#1D2232', muzzle='#4A5370', mane='#5FE6FF', maneD='#1C9CC4', hoof='#9EE9FF', eye='#06080F',
           blush='#3A4A6A', tack='#45E0FF', ring='#DFFBFF', cloth='#121829', clothTrim='#45E0FF', num='#BFF6FF', saddle='#0E1220',
           bodyShade='#262C3E')
SPOT = dict(pose='gallop', facing='right', box=(250, 70, 520, 262), azim=6, shadow=('#000000', 0.0))
GROUND = 258
CYCLE = 0.48       # ギャロップ 1回の 秒（future.RUN と 同じ）
NT = 20            # 光の すじの コマ（1回りに 20＝0.024秒ごと）
FADE = 0.55        # 光の すじが 消える までの 秒


def acc_factory(i):
    def acc(m):
        """布に 光の 帯（水色の すじ 2本）と 小さな 六角の しるし"""
        p = m['p1u']
        x0, x1, yt, yb, trim = m['cloth']
        out = [f'<defs><clipPath id="ftc{i}"><path d="{m["cloth_d"]}"/></clipPath></defs><g clip-path="url(#ftc{i})">']
        for off, w, op in ((0.07, 0.022, .95), (0.12, 0.012, .7)):
            y = yt + off * p
            out.append(f'<rect x="{f2(x0 - 4)}" y="{f2(y)}" width="{f2(x1 - x0 + 8)}" height="{f2(w * p)}" fill="#5FE6FF" fill-opacity="{op}"/>')
        out.append('</g>')
        cx, cy = (x0 + x1) / 2, (yt + trim) / 2 + 0.035 * p
        r = 0.07 * p
        hexd = 'M' + ' L'.join(f'{f2(cx + math.cos(math.radians(60 * k + 30)) * r)},{f2(cy + math.sin(math.radians(60 * k + 30)) * r)}' for k in range(6)) + ' Z'
        out.append(f'<path d="{hexd}" fill="none" stroke="#5FE6FF" stroke-width="{f2(0.016 * p)}"/>')
        out.append(circ(V(cx, cy), 0.022 * p, '#BFF6FF'))
        return dict(cloth=out)
    return acc


def hexc(c):
    c = c.lstrip('#')
    return np.array([int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)


def neon(i, pre, A):
    """まわりの 水色の 光（ぼかした ふち）と、上の ふちの 細い 光の 線"""
    k5 = np.ones((5, 5), np.uint8)
    er = cv2.erode(A, k5)
    edge = np.clip(A - er, 0, 1)
    dy = np.zeros_like(A)
    dy[2:-2] = A[4:] - A[:-4]
    top = np.clip(dy * 1.6, 0, 1)
    rim = np.clip(edge * (0.25 + top), 0, 1) * 0.85
    rc = hexc('#9FF4FF')
    pre = pre * (1 - rim[..., None]) + rc[None, None, :] * (rim * A)[..., None]
    g = np.clip(cv2.GaussianBlur(A, (0, 0), 5.0) * 0.55 + cv2.GaussianBlur(A, (0, 0), 14.0) * 0.25, 0, 1)
    gc = hexc('#36D6FF')
    pre = pre + gc[None, None, :] * (g * (1 - A))[..., None]
    A2 = A + g * (1 - A)
    return pre, A2


# ---------------------------------------------------------------- 足もとの 雷（第4.93版）
BOLT_CORE = hexc('#F2FFFF')
BOLT_MID = hexc('#5FDCFF')
BOLT_GLOW = hexc('#1FA8FF')


def jag(R, p0, ang, L, n=5, jit=0.32):
    """ぎざぎざの 線（p0 から ang° の 向きへ 長さ L）：とちゅうを 横に ずらす"""
    d = np.array([math.cos(math.radians(ang)), math.sin(math.radians(ang))])
    nv = np.array([-d[1], d[0]])
    pts = [np.asarray(p0, float)]
    for j in range(1, n + 1):
        t = j / n
        off = R.uniform(-1, 1) * L * jit * (0.4 if j == n else 1.0)
        pts.append(np.asarray(p0, float) + d * L * t + nv * off)
    return pts


def bolts_layer(hooves, seed, ground):
    """1コマ・1とおりの 雷（2倍の 画素）：ひづめごとに 2〜3本の ぎざぎざ（下・うしろ・横へ）と 小さな 枝。地面に ついた ひづめは 地面に そって 横へ も 走る。
       返り値：(pre, A)＝premultiplied"""
    import random
    R = random.Random(seed)
    core = np.zeros((H2, W2), np.float32)
    mid = np.zeros((H2, W2), np.float32)
    lines = []
    for k, (hx, hy) in enumerate(hooves):
        on_ground = hy > ground - 7
        base = (hx + R.uniform(-3, 3), hy - R.uniform(1, 5))
        angs = [R.uniform(95, 150), R.uniform(30, 85)] + ([R.uniform(160, 200)] if R.random() < 0.6 else [])
        if on_ground:
            angs = [R.choice((172, 186)) + R.uniform(-8, 8), R.uniform(-12, 8), R.uniform(100, 150)]
        for a in angs:
            L = R.uniform(16, 30) * (1.0 if on_ground else 0.85)
            pts = jag(R, base, a, L, n=R.choice((4, 5, 6)))
            lines.append(pts)
            if R.random() < 0.55:                                  # 枝
                j = R.randint(1, len(pts) - 2)
                lines.append(jag(R, pts[j], a + R.choice((-1, 1)) * R.uniform(30, 55), L * R.uniform(.3, .5), n=3))
    # 手前と 奥の 足の あいだの 弧（前足どうし・うしろ足どうし が 近い ときだけ）
    for a_, b_ in ((0, 1), (2, 3)):
        (x1, y1), (x2, y2) = hooves[a_], hooves[b_]
        dist = math.hypot(x2 - x1, y2 - y1)
        if 6 < dist < 60 and R.random() < 0.8:
            ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
            lines.append(jag(R, (x1, y1 - 3), ang, dist, n=max(3, int(dist / 9)), jit=0.25))
    for pts in lines:                                              # 第4.94版：線を 細く（芯 2 → 1・まわり 5 → 2）・まわりの 光を うすく
        q = np.round(np.array(pts) * 4).astype(np.int32).reshape(-1, 1, 2)
        cv2.polylines(core, [q], False, 1.0, 1, cv2.LINE_AA, shift=2)
        cv2.polylines(mid, [q], False, 1.0, 2, cv2.LINE_AA, shift=2)
    mid = np.clip(cv2.GaussianBlur(mid, (0, 0), 0.9), 0, 1)
    glow = np.clip(cv2.GaussianBlur(mid, (0, 0), 3.2) * 1.1, 0, 1)
    A = np.clip(core * 0.9 + mid * 0.45 + glow * 0.26, 0, 1)
    pre = (BOLT_CORE[None, None, :] * (core * 0.9)[..., None] + BOLT_MID[None, None, :] * (mid * 0.45 * (1 - core * 0.9))[..., None]
           + BOLT_GLOW[None, None, :] * (glow * 0.26 * (1 - np.clip(core * 0.9 + mid * 0.45, 0, 1)))[..., None])
    return pre, A


def stance_speed(hvs, stance):
    """地面に ついた ひづめの 横の はやさ（2倍の 画素／コマ：左へ ＋）"""
    from sheets import HOOF_ORDER
    n = len(hvs)
    vals = []
    for i in range(n):
        j = (i + 1) % n
        for k in stance[i]:
            if k in stance[j]:
                vals.append(hvs[i][HOOF_ORDER.index(k)][0] - hvs[j][HOOF_ORDER.index(k)][0])
    return sum(vals) / len(vals) if vals else 0.0


def hoof_at(hvs, k, t):
    """時刻 t（秒）の ひづめ k の 場所：コマの 場所を 1回りで つないだ なめらかな 線（Catmull-Rom）"""
    n = len(hvs)
    u = (t / CYCLE % 1.0) * n
    i = int(math.floor(u)) % n
    f = u - math.floor(u)
    p0, p1, p2, p3 = (np.asarray(hvs[(i + d) % n][k], float) for d in (-1, 0, 1, 2))
    return 0.5 * (2 * p1 + (-p0 + p2) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f * f + (-p0 + 3 * p1 - 3 * p2 + p3) * f ** 3)


def trail_layer(hvs, j, u2):
    """光の すじの コマ j（時刻 j × CYCLE / NT）：ひづめが 時刻 t0 に いた 所は、いま t には レーンと いっしょに u2 × (t − t0) だけ 左へ 流れて いる。
       t0 は いちばん 新しい 馬の コマの 時刻 まで（すじが ひづめより 前に 出ない）。古いほど うすい。返り値：(pre, A)＝premultiplied"""
    n = len(hvs)
    t = j * CYCLE / NT
    t_last = math.floor(j * n / NT) * CYCLE / n
    core = np.zeros((H2, W2), np.float32)
    glow = np.zeros((H2, W2), np.float32)
    dt = 0.002
    for k in range(4):
        t0s = np.arange(t - FADE, t_last + 1e-9, dt)
        pts = [(hoof_at(hvs, k, t0) - np.array([u2 * (t - t0), 0.0]), t - t0) for t0 in t0s]
        for (p, age), (q, _) in zip(pts, pts[1:]):
            a = 0.95 * max(0.0, 1 - age / FADE) ** 1.25
            if a <= 0.01:
                continue
            P = (int(round(p[0] * 4)), int(round(p[1] * 4)))
            Q = (int(round(q[0] * 4)), int(round(q[1] * 4)))
            cv2.line(core, P, Q, a, 2, cv2.LINE_AA, shift=2)
            cv2.line(glow, P, Q, a, 5, cv2.LINE_AA, shift=2)
    glow = np.clip(cv2.GaussianBlur(glow, (0, 0), 2.6) * 1.25, 0, 1)
    cc, gc = hexc('#C8F6FF'), hexc('#29C6FF')
    core = np.clip(core, 0, 1)
    A = np.clip(core * 0.9 + glow * 0.5, 0, 1)
    pre = cc[None, None, :] * (core * 0.9)[..., None] + gc[None, None, :] * (glow * 0.5 * (1 - core * 0.9))[..., None]
    return pre, A


def hoof_glow(hooves, ground):
    """ひづめの まわりの いつもの 光の もや（地面に ついた ひづめは 少し 強く）"""
    m = np.zeros((H2, W2), np.float32)
    for hx, hy in hooves:
        r = 9.0 if hy > ground - 7 else 7.0
        cv2.circle(m, (int(round(hx)), int(round(hy - 2))), int(r), 1.0 if hy > ground - 7 else 0.7, -1, cv2.LINE_AA)
    return np.clip(cv2.GaussianBlur(m, (0, 0), 5.5) * 0.85, 0, 1)


def to_sheet(cells, box, pad=0):
    """premultiplied の コマ（pre, A）を 同じ 四角（box＝x0, y0, x1, y1）で 切りぬいて 横に ならべる → u8 RGBA"""
    x0, y0, x1, y1 = box
    cw, ch = x1 - x0, y1 - y0
    n = len(cells)
    sheet = np.zeros((ch, cw * n, 4), np.float32)
    for i, (pre, A) in enumerate(cells):
        cut_p = np.zeros((ch, cw, 3), np.float32)
        cut_a = np.zeros((ch, cw), np.float32)
        hh, ww = min(ch, H2 - y0), min(cw, W2 - x0)
        cut_p[:hh, :ww] = pre[y0:y0 + hh, x0:x0 + ww]
        cut_a[:hh, :ww] = A[y0:y0 + hh, x0:x0 + ww]
        rgb = np.where(cut_a[..., None] > 1e-4, cut_p / np.maximum(cut_a, 1e-4)[..., None], 0)
        sheet[:, i * cw:(i + 1) * cw, :3] = rgb
        sheet[:, i * cw:(i + 1) * cw, 3] = cut_a
    return (np.clip(sheet, 0, 1) * 255 + .5).astype(np.uint8)


def build(out=None):
    n = 10
    frames, cam = render(PAL, SPOT, gallop_poses(n), acc=acc_factory, number='', tag='pkfuture', workers=2)
    dys = ground_dy(frames, gallop_stance(n), GROUND, 6.0)
    horse, bolts = [], [[], [], []]
    gc = hexc('#5FE6FF')
    for i, ((rgb, a, hooves), dy) in enumerate(zip(frames, dys)):
        M = np.float32([[1, 0, 0], [0, 1, dy]])
        pre = cv2.warpAffine(rgb * a[..., None], M, (W2, H2), flags=cv2.INTER_LINEAR)
        A = cv2.warpAffine(a, M, (W2, H2), flags=cv2.INTER_LINEAR)
        pre, A = neon(i, pre, A)
        hv = [(x, y + dy) for x, y in hooves]
        g = hoof_glow(hv, GROUND)                                      # ひづめの まわりの 光（馬の うしろ・まわり）
        pre = pre + gc[None, None, :] * (g * (1 - A))[..., None]
        A = A + g * (1 - A)
        horse.append((pre, A))
        for v in range(3):
            bolts[v].append(bolts_layer(hv, 1000 * v + 17 * i + 3, GROUND))
    allA = np.max([A for _, A in horse] + [A for b in bolts for _, A in b], axis=0)
    ys, xs = np.nonzero(allA > 0.004)
    x0, x1 = max(0, xs.min() - 4), min(W2, xs.max() + 5)
    y0, y1 = max(0, ys.min() - 4), min(H2, ys.max() + 5)
    x0, y0 = x0 - x0 % 2, y0 - y0 % 2
    x1, y1 = x1 + (x1 - x0) % 2, y1 + (y1 - y0) % 2
    box = (int(x0), int(y0), int(x1), int(y1))
    meta = dict(frames=n, cell=[box[2] - box[0], box[3] - box[1]], at=[box[0], box[1]], dy=[round(float(d), 2) for d in dys])
    hvs = [[(x, y + dy) for x, y in fr[2]] for fr, dy in zip(frames, dys)]
    v2 = stance_speed(hvs, gallop_stance(n))                         # 2倍の 画素／コマ
    meta['speed'] = round(v2 / 2 * n / CYCLE, 2)                     # ページの px／秒（レーンと 光の すじの 流れ）
    u8 = to_sheet(horse, box)
    if out:
        preview_png(u8, os.path.join(out, 'future_run.png'), bg=(18, 22, 44))
    bid = save_webp(u8, quality=90)
    record('future', 'run', bid, meta)
    print('run', bid, meta)
    # 光の すじ（20コマ：自分の 四角で 切りぬく）
    u2 = v2 * n / CYCLE                                              # 2倍の 画素／秒
    trail = [trail_layer(hvs, j, u2) for j in range(NT)]
    tA = np.max([A for _, A in trail], axis=0)
    ys, xs = np.nonzero(tA > 0.004)
    tx0, tx1 = max(0, xs.min() - 2), min(W2, xs.max() + 3)
    ty0, ty1 = max(0, ys.min() - 2), min(H2, ys.max() + 3)
    tx0, ty0 = tx0 - tx0 % 2, ty0 - ty0 % 2
    tx1, ty1 = tx1 + (tx1 - tx0) % 2, ty1 + (ty1 - ty0) % 2
    tbox = (int(tx0), int(ty0), int(tx1), int(ty1))
    ut = to_sheet(trail, tbox)
    if out:
        preview_png(ut[:, :ut.shape[1] // NT * 4], os.path.join(out, 'future_trail.png'), bg=(18, 22, 44))
    tb = save_webp(ut, quality=90)
    record('future', 'trail', tb, dict(frames=NT, cell=[tbox[2] - tbox[0], tbox[3] - tbox[1]], at=[tbox[0], tbox[1]]))
    print('trail', tb, tbox, 'speed', meta['speed'])
    for v in range(3):
        ub = to_sheet(bolts[v], box)
        if out:
            preview_png(ub, os.path.join(out, f'future_bolt{v}.png'), bg=(18, 22, 44))
        b = save_webp(ub, quality=92)
        record('future', f'bolt{v}', b, dict(frames=n, cell=meta['cell'], at=meta['at']))
        print(f'bolt{v}', b)


if __name__ == '__main__':
    build(os.environ.get('OUT'))
