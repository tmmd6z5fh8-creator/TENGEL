"""パドックの 馬の ときどきの 動き（壁紙パック・第4.93版：まさちゃんの 指定「ランダムで馬が首を激しく振ったり、うんちしたり、早歩きになったり、首を下げて歩いたり」）
   行動ごとの コマの シート。足は 常歩（paddock_art.pose_at）と 同じ＝1回り 1.25秒・12コマ。どの シートも コマ0は 常歩の コマ0と 同じ 形
   （ページが 見える シートを 回りの つぎめで 切りかえても 足が とばない）：
     s（首振り）：1回りに 2回、首と 頭を 上へ ぶんっと 振り上げて おろす（頭は 少し おくれて むちの ように・たてがみが はねる・耳を うしろへ）
     d（首下げ）：36コマ＝首を 下げていく 12・下げたまま 歩く 12・上げていく 12
     p（うんち・手前の 3頭）：24コマ（2回り）：しっぽを 上げて、丸い うんちが 4つ ぽとぽと 落ちる → しっぽを おろす。
        地面に ついた うんちは ページの 部品（その 場所に 残って、しばらく して 消える）＝ meta の drops（はじまりの コマ・x・地面・半径：2倍の 画素）
   早歩きは 常歩の シートを 1.5倍の はやさで めくる（ページ：横の はやさも 1.5倍＝ひづめが すべらない）。
   3Dの 形（horse_flat.render_body）は 形ごとに 1回だけ 描いて、色ちがいの 馬に 使う（しっぽ・たてがみ・色は 3Dでは ない＝同じ 形）
   python3 kisekae/pack/make/paddock_moves.py [n2 n5 n7 f1 f4 f8] [--only s,d,p] [--out DIR]
     → ios/kisekae_blobs/<id>.webp・kisekae/pack/blobs.json の paddock.<名前>_<s|d|p>"""
import json
import math
import os
import sys
from multiprocessing import Pool

import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paddock_art as PA  # noqa: E402
from sheets import camera, make_sheet, ground_dy, save_webp, record, preview_png, HOOF_ORDER, W2, H2  # noqa: E402

N = PA.N
NEAR = ('n2', 'n5', 'n7')
FAR = ('f1', 'f4', 'f8')
POOP = NEAR                      # うんちは 手前の 3頭（おくの 馬は 小さくて 生け垣に かくれる）
DROPS = [(6, 0.0), (7, 0.9), (8, -0.6), (10, 0.5)]   # うんち：(落ちはじめる コマ, 横の ずれ×半径)
FALL = 4                         # 落ちる コマ数（約0.42秒）
DUNG = ('#5A4220', '#3E2C14', '#8A6A3A')             # うんちの 色（まん中・ふち・つや）


def ease(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------- 首振り
TOSS_KEYS = [(0.0, 0.0), (1 / 6, 0.80), (2 / 6, 1.0), (3 / 6, 0.36), (4 / 6, -0.42), (5 / 6, -0.20), (1.0, 0.0)]


def toss(u):
    """首振り 1回（u：0〜1）の 上げぐあい：すばやく 上へ → ゆっくり おろして 少し 下へ → もどる"""
    u %= 1.0
    for (u0, v0), (u1, v1) in zip(TOSS_KEYS, TOSS_KEYS[1:]):
        if u0 <= u <= u1:
            t = (u - u0) / (u1 - u0)
            t = t * t * (3 - 2 * t)
            return v0 + (v1 - v0) * t
    return 0.0


def pose_shake(g):
    p = PA.pose_at(g)
    s = toss(2 * g)                           # 1回りに 2回
    sl = toss(2 * g - 1 / 12)                 # 頭は 少し おくれる
    p['neck_rot'] = round(p['neck_rot'] + 21.0 * s, 3)
    p['head_ang'] = round(p['head_ang'] + 30.0 * sl, 3)
    p['ear_rot'] = round(-16.0 * max(0.0, s), 3)
    return p


def over_shake(g):
    """たてがみが はねる（房の 長さと ばらつき）"""
    s = toss(2 * g)
    base = (1.0, 1.14, 0.9, 1.1, 0.96, 1.06)
    var = tuple(round(b * (1 + 0.22 * s * math.sin(k * 1.9 + 4 * math.pi * g)), 4) for k, b in enumerate(base))
    return dict(mane_len=round(1.0 + 0.30 * max(0.0, s) + 0.08 * abs(s), 4), mane_var=var)


# ---------------------------------------------------------------- 首下げ
DOWN = (-44.0, 1.05, -88.0)              # 首の まげ°・首ののばし・頭の 角度°（下げきった 時）


def pose_down(g, p, nod=0.0):
    """p：下げぐあい（0〜1）・nod：下げて 歩く 時の 小さな うなずき"""
    q = PA.pose_at(g)
    e = ease(p)
    if e > 0:
        Bd, Ld, Hd = DOWN
        q['neck_bend'] = round(Bd * e + nod * 4.0 * math.sin(2 * math.pi * 2 * (g - 0.1)), 4)
        q['neck_len'] = round(1 + (Ld - 1) * e, 5)
        q['head_ang'] = round(q['head_ang'] + (Hd - q['head_ang']) * e ** 1.2 + nod * 3.0 * math.sin(2 * math.pi * 2 * g), 4)
    return q


# ---------------------------------------------------------------- うんち
RAISE = [((0.18, -0.16), (0.40, -0.14), (0.52, 0.34), 0.22), ((0.10, -0.12), (0.30, -0.06), (0.34, 0.44), 0.18),
         ((0.16, -0.18), (0.38, -0.16), (0.48, 0.40), 0.30)]


def raise_amt(i):
    """24コマの しっぽの 上げぐあい"""
    if i <= 4:
        return ease(i / 4.0)
    if i <= 15:
        return 1.0
    return ease(1 - (i - 15) / 9.0)


def pose_poop(i):
    g = (i % N) / N
    p = PA.pose_at(g)
    r = raise_amt(i)
    if r > 0:
        p['tail_tufts'] = [tuple((a[0] + (b[0] - a[0]) * r, a[1] + (b[1] - a[1]) * r) for a, b in zip(t0[:3], t1[:3])) + (t0[3] + (t1[3] - t0[3]) * r,)
                           for t0, t1 in zip(p['tail_tufts'], RAISE)]
    return p


# ---------------------------------------------------------------- 行動の コマ
def frames_of(kind):
    """[(g, pose, spot の 上書き)]"""
    if kind == 's':
        return [(i / N, pose_shake(i / N), over_shake(i / N)) for i in range(N)]
    if kind == 'd':
        out = [(i / N, pose_down(i / N, i / N), {}) for i in range(N)]                       # 下げていく
        out += [(i / N, pose_down(i / N, 1.0, nod=1.0), {}) for i in range(N)]               # 下げて 歩く
        out += [(i / N, pose_down(i / N, 1 - i / N), {}) for i in range(N)]                  # 上げていく
        return out
    if kind == 'p':
        return [((i % N) / N, pose_poop(i), {}) for i in range(2 * N)]
    raise KeyError(kind)


# ---------------------------------------------------------------- 描く（Pool：1つの 形を いくつかの 色で。3Dの 形は 1回だけ）
_JB = {}
_CACHE = {}


def _init_mv(job):
    _JB.clear()
    _JB.update(job)
    import horse_flat as HF
    if not getattr(HF, '_pk_cached', False):
        orig = HF.render_body

        def cached(pose, eye, tgt, fov, W, Hh, name, tmp, throat=None):
            key = json.dumps([pose, [float(v) for v in eye], [float(v) for v in tgt], fov, W, Hh, throat], sort_keys=True, default=float)
            if key not in _CACHE:
                _CACHE.clear()
                _CACHE[key] = orig(pose, eye, tgt, fov, W, Hh, name, tmp, throat)
            return _CACHE[key]
        HF.render_body = cached
        HF._pk_cached = True


def _draw_mv(args):
    i, pose, over = args
    from horse_flat import draw_horse, first_out
    import horse3d as Hm
    J = _JB
    out = []
    for nm, pal, number in J['horses']:
        sp = dict(J['spot'], pose=pose, cam=J['cam'], **over)
        sp.pop('cam_out', None)
        rgb, a, m = draw_horse(sp, pal, J['W'], J['H'], acc=None, number=number, name=f'pm{nm}{J["kind"]}{i}')
        s = m['s']
        th = np.asarray(m['P1'](Hm.v3(m['S']['tailhead'])), float) * s
        wi = np.asarray(m['P1'](Hm.v3(m['S']['withers'])), float) * s
        root = first_out(m['inside'], th, th - wi) / s - np.asarray(m['back_dir']) * 0.035 * m['p1u']
        out.append((nm, rgb.astype(np.float32), a.astype(np.float32), [tuple(map(float, h)) for h in m['hooves']],
                    (float(root[0]), float(root[1])), tuple(map(float, m['back_dir'])), float(m['p1u'])))
    return i, out


def render_group(names, kind, workers=2):
    """同じ 向き・同じ 大きさの 馬たち（names）の 行動 kind の コマ → {名前: [(rgb, a, hooves, root, back_dir, p1u)…]}"""
    kind0, cloth0, numc0, num0, facing = PA.HORSES[names[0]]
    box = PA.BOX_NEAR if facing == 'right' else PA.BOX_FAR
    spot = dict(pose='stand', facing=facing, box=box, azim=6 if facing == 'right' else -6, shadow=('#3A2A10', 0.0), ext=(0.05, 0.05))
    horses = []
    for nm in names:
        k, cloth, numc, num, fc = PA.HORSES[nm]
        assert fc == facing
        horses.append((nm, PA.pal(k, cloth, numc, '#F2C14E' if cloth != '#FFFFFF' else '#1A1A1A'), num))
    cam, _ = camera(horses[0][1], spot, horses[0][2], 'pmref' + kind)
    frs = frames_of(kind)
    job = dict(spot=spot, cam=cam, horses=horses, kind=kind, W=W2, H=H2)
    jobs = [(i, pose, over) for i, (g, pose, over) in enumerate(frs)]
    if workers > 1:
        with Pool(workers, initializer=_init_mv, initargs=(job,)) as pool:
            res = pool.map(_draw_mv, jobs, chunksize=1)
    else:
        _init_mv(job)
        res = [_draw_mv(j) for j in jobs]
    res.sort(key=lambda r: r[0])
    out = {nm: [] for nm in names}
    for i, lst in res:
        for nm, rgb, a, hooves, root, bd, p1u in lst:
            out[nm].append((rgb, a, hooves, root, bd, p1u))
    return out, [g for g, _, _ in frs], box, facing


def stance_of(g, facing):
    legs = PA.stance(g)
    if facing == 'left':
        sw = {'FL': 'FR', 'FR': 'FL', 'HL': 'HR', 'HR': 'HL'}
        legs = [sw[k] for k in legs]
    return legs


def walk_shadow(frames, box):
    xs = [h[0] for fr in frames for h in fr[2]]
    g = box[3] - 4
    return ('#3A2A10', (min(xs) + max(xs)) / 2, g + 3, (max(xs) - min(xs)) * 0.52, 5.0, 0.22)


def build_sheet(nm, kind, frs, gs, box, facing, out=None):
    """1頭・1つの 行動の シート（make_sheet）→ 絵の id と meta（blobs.json）"""
    frames = [(rgb, a, hooves) for rgb, a, hooves, root, bd, p1u in frs]
    legs = [stance_of(g, facing) for g in gs]
    g0 = box[3] - 4
    dys = ground_dy(frames, legs, g0, lift=0.0)
    sh = walk_shadow(frames, box)
    drops = []
    extra = None
    if kind == 'p':
        root, bd, p1u = frs[0][3], frs[0][4], frs[0][5]
        rb = 0.040 * p1u                                    # うんちの 半径（2倍の 画素）
        for k, (st, dx) in enumerate(DROPS):
            r0, bd0 = frs[st][3], frs[st][4]
            x = r0[0] + bd0[0] * 0.03 * p1u + dx * rb
            y0 = r0[1] + 0.09 * p1u + dys[st]
            drops.append(dict(f=st, x=round(x, 2), y0=round(y0, 2), g=round(g0 - rb * 0.86, 2), r=round(rb, 2)))

        def extra(i, pre, A):
            for d in drops:
                k = i - d['f']
                if 0 <= k < FALL:
                    t = (k + 0.6) / FALL
                    y = d['y0'] + (d['g'] - d['y0']) * t * t
                    rr = d['r'] * (0.75 + 0.25 * min(1.0, t * 2))
                    pre, A = dung_ball(pre, A, d['x'], y, rr)
            return pre, A
    u8, meta = make_sheet(frames, dys, shadow=sh, extra=extra)
    meta['dy'] = [round(float(d), 2) for d in dys]
    meta['facing'] = facing
    if drops:
        meta['drops'] = drops
        meta['fall'] = FALL
    if out:
        preview_png(u8, os.path.join(out, f'paddock_{nm}_{kind}.png'), bg=(196, 170, 120))
    bid = save_webp(u8, quality=90)
    record('paddock', f'{nm}_{kind}', bid, meta)
    print(nm, kind, bid, {k: v for k, v in meta.items() if k not in ('dy', 'drops')}, flush=True)
    return bid, meta


def dung_ball(pre, A, x, y, r):
    """丸い うんち（premultiplied の 2倍の 画素に 描く：ふちの 濃い色・まん中・つや）"""
    S = 4
    x0, y0 = int(x - r - 3), int(y - r - 3)
    w = int(2 * r + 7)
    if w <= 0:
        return pre, A
    sub = np.zeros((w * S, w * S, 4), np.float32)
    cx, cy = (x - x0) * S, (y - y0) * S
    def disc(col, cxx, cyy, rr, al=1.0):
        m = np.zeros((w * S, w * S), np.float32)
        cv2.circle(m, (int(round(cxx)), int(round(cyy))), int(round(rr)), 1.0, -1, cv2.LINE_AA)
        c = np.array([int(col[i:i + 2], 16) / 255 for i in (1, 3, 5)], np.float32)
        a = m * al
        sub[..., :3] = sub[..., :3] * (1 - a[..., None]) + c * a[..., None]
        sub[..., 3] = sub[..., 3] * (1 - a) + a
    disc(DUNG[1], cx, cy, r * S)
    disc(DUNG[0], cx - 0.12 * r * S, cy - 0.12 * r * S, r * 0.80 * S)
    disc(DUNG[2], cx - 0.38 * r * S, cy - 0.40 * r * S, r * 0.26 * S, 0.9)
    small = cv2.resize(sub, (w, w), interpolation=cv2.INTER_AREA)
    a = small[..., 3]
    rgbp = small[..., :3]                                     # すでに a を かけた 色（premultiplied で 重ねる）
    ys, xs = slice(max(0, y0), min(A.shape[0], y0 + w)), slice(max(0, x0), min(A.shape[1], x0 + w))
    sy, sx = slice(ys.start - y0, ys.stop - y0), slice(xs.start - x0, xs.stop - x0)
    pre[ys, xs] = pre[ys, xs] * (1 - a[sy, sx, None]) + rgbp[sy, sx]
    A[ys, xs] = A[ys, xs] * (1 - a[sy, sx]) + a[sy, sx]
    return pre, A


def dung_svg(r):
    """ページの 部品：地面の うんち 1つ（4r × 4r の 中の まん中）"""
    s = 4 * r
    c = s / 2
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {s:.2f} {s:.2f}' width='{s:.2f}' height='{s:.2f}'>"
            f"<ellipse cx='{c:.2f}' cy='{c + r * 0.86:.2f}' rx='{r * 1.1:.2f}' ry='{r * 0.32:.2f}' fill='#3A2A10' opacity='.22'/>"
            f"<circle cx='{c:.2f}' cy='{c:.2f}' r='{r:.2f}' fill='{DUNG[1]}'/>"
            f"<circle cx='{c - 0.12 * r:.2f}' cy='{c - 0.12 * r:.2f}' r='{r * 0.8:.2f}' fill='{DUNG[0]}'/>"
            f"<circle cx='{c - 0.38 * r:.2f}' cy='{c - 0.40 * r:.2f}' r='{r * 0.26:.2f}' fill='{DUNG[2]}' opacity='.9'/></svg>")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    opts = {a.split('=')[0]: (a.split('=')[1] if '=' in a else '1') for a in sys.argv[1:] if a.startswith('--')}
    only = opts.get('--only', 's,d,p').split(',')
    out = opts.get('--out') or os.environ.get('OUT')
    if out:
        os.makedirs(out, exist_ok=True)
    names = args or list(NEAR + FAR)
    for grp in (NEAR, FAR):
        nms = [n for n in names if n in grp]
        if not nms:
            continue
        for kind in only:
            hs = [n for n in nms if kind != 'p' or n in POOP]
            if not hs:
                continue
            res, gs, box, facing = render_group(hs, kind, workers=int(opts.get('--workers', '2')))
            for nm in hs:
                build_sheet(nm, kind, res[nm], gs, box, facing, out)


if __name__ == '__main__':
    main()
