"""パドックの 馬の コマの シート（壁紙パック・第4.94版：まさちゃんの 指定「パドックの馬地面から脚が浮いたり地面についたりしてるから安定して同じ場所で歩かせて！
   あと脚の動きもう少しスムーズにして！」。第4.93版「ランダムで馬が首を激しく振ったり、うんちしたり、早歩きになったり、首を下げて歩いたり」）
   足は どの シートも 同じ 常歩（paddock_gait：1回り 1.25秒・24コマ・ひづめの 道を 先に 決めて 足の 角度を 逆に 解く）。
   地面に ついて いる ひづめは どの コマでも 同じ 地面の 線（手前の 道の 同じ 高さ）に くる：コマの 上下の ずらしは 体の 上下（paddock_gait.bob）だけ
   （どの シートも 同じ ずらし＝シートを 切りかえても 足の 高さが そろう）。影は 地面に 止まった まま。
     w（常歩）：24コマ。早歩きは この シートを 1.5倍の はやさで めくる（ページ：横の はやさも 1.5倍＝ひづめが すべらない）
     s（首振り）：24コマ。1回りに 2回、首と 頭を 上へ ぶんっと 振り上げて おろす（頭は 少し おくれて むちの ように・たてがみが はねる・耳を うしろへ）
     dl・dd・dr（首下げ）：24コマずつ＝首を 下げていく・下げたまま 歩く・上げていく
     p（うんち・手前の 3頭）：48コマ（2回り）：しっぽを 上げて、丸い うんちが 4つ ぽとぽと 落ちる → しっぽを おろす。
        地面に ついた うんちは ページの 部品（その 場所に 残って、しばらく して 消える）＝ meta の drops（はじまりの コマ・x・地面・半径：2倍の 画素）
   どの シートも コマ0は 常歩の コマ0と 同じ 形（ページが 見える シートを 回りの つぎめで 切りかえても 足が とばない）。
   3Dの 形（horse_flat.render_body）は 形ごとに 1回だけ 描いて、色ちがいの 馬・しっぽだけ ちがう コマ（常歩と うんち）に 使う
   python3 kisekae/pack/make/paddock_moves.py [n2 n5 n7 f1 f4 f8] [--only w,s,d,p] [--out DIR] [--workers 2]
     → ios/kisekae_blobs/<id>.webp・kisekae/pack/blobs.json の paddock.<名前>（常歩・speed）／<名前>_s／<名前>_dl・_dd・_dr／<名前>_p
   python3 kisekae/pack/make/paddock_moves.py --recompress   できて いる シートを いまの WebP の 質で 保存し直す"""
import json
import math
import os
import sys

import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paddock_art as PA  # noqa: E402
from sheets import camera, make_sheet, record, preview_png, HOOF_ORDER, W2, H2, BLOB_DIR, PACK, Z, ZW, ZH  # noqa: E402
import paddock_gait as G  # noqa: E402

N = G.N                          # 1回りの コマ（24）
CYCLE = PA.CYCLE                 # 1回りの 秒（1.25）
NEAR = ('n2', 'n5', 'n7')
FAR = ('f1', 'f4', 'f8')
POOP = NEAR                      # うんちは 手前の 3頭（おくの 馬は 小さくて 生け垣に かくれる）
NF = dict(w=N, s=N, dl=N, dd=N, dr=N, p=2 * N)
DROPS = [(12, 0.0), (14, 0.9), (16, -0.6), (20, 0.5)]   # うんち：(落ちはじめる コマ, 横の ずれ×半径)
FALL = 8                         # 落ちる コマ数（約0.42秒）
DUNG = ('#5A4220', '#3E2C14', '#8A6A3A')             # うんちの 色（まん中・ふち・つや）
DUNG_R = 0.064                   # うんちの 半径（m：ほんとうより 大きく＝画面で 見える ように）
QUALITY = 74                     # WebP の 質（24コマで 絵の 容量が ふえすぎない ように：PIL の method 6・すき通しの 質 ALPHA_Q。ぺたっとした 色なので 見た目は 90 と かわらない）
ALPHA_Q = 82
XV = -0.10                       # 地面の 線を 決める 点（体の 中の x：前足と うしろ足の まん中）
CANVAS = dict(right=(0, W2), left=(180, 372))       # 描く 画面（左の はし, はば：2倍の 画素）。おくの 馬は 小さい＝まわりを 切って はやく 描く


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


def pose_shake(p, g):
    q = dict(p)
    u = (2 * g) % 1.0                         # 1回りに 2回
    s = toss(u)
    sl = toss(u ** 1.22)                      # 頭は 少し おくれる（はじめと おわりは 同じ＝つぎめで とばない）
    q['neck_rot'] = round(p['neck_rot'] + 21.0 * s, 3)
    q['head_ang'] = round(p['head_ang'] + 30.0 * sl, 3)
    q['ear_rot'] = round(-16.0 * max(0.0, s), 3)
    return q


def over_shake(g):
    """たてがみが はねる（房の 長さと ばらつき）"""
    s = toss((2 * g) % 1.0)
    base = (1.0, 1.14, 0.9, 1.1, 0.96, 1.06)
    var = tuple(round(b * (1 + 0.22 * s * math.sin(k * 1.9 + 4 * math.pi * g)), 4) for k, b in enumerate(base))
    return dict(mane_len=round(1.0 + 0.30 * max(0.0, s) + 0.08 * abs(s), 4), mane_var=var)


# ---------------------------------------------------------------- 首下げ
DOWN = (-44.0, 1.05, -88.0)              # 首の まげ°・首ののばし・頭の 角度°（下げきった 時）


def pose_down(p, g, amt, nod=0.0):
    """amt：下げぐあい（0〜1）・nod：下げて 歩く 時の 小さな うなずき（1回りの はじめと おわりで 0）"""
    q = dict(p)
    e = ease(amt)
    if e > 0:
        Bd, Ld, Hd = DOWN
        w = math.sin(2 * math.pi * 2 * g)
        q['neck_bend'] = round(Bd * e + nod * 4.0 * w, 4)
        q['neck_len'] = round(1 + (Ld - 1) * e, 5)
        q['head_ang'] = round(p['head_ang'] + (Hd - p['head_ang']) * e ** 1.2 + nod * 3.0 * w, 4)
    return q


# ---------------------------------------------------------------- うんち
RAISE = [((0.18, -0.16), (0.40, -0.14), (0.52, 0.34), 0.22), ((0.10, -0.12), (0.30, -0.06), (0.34, 0.44), 0.18),
         ((0.16, -0.18), (0.38, -0.16), (0.48, 0.40), 0.30)]


def raise_amt(i):
    """48コマの しっぽの 上げぐあい"""
    if i <= 8:
        return ease(i / 8.0)
    if i <= 30:
        return 1.0
    return ease(1 - (i - 30) / 18.0)


def pose_poop(p, i):
    q = dict(p)
    r = raise_amt(i)
    if r > 0:
        q['tail_tufts'] = [tuple((a[0] + (b[0] - a[0]) * r, a[1] + (b[1] - a[1]) * r) for a, b in zip(t0[:3], t1[:3])) + (t0[3] + (t1[3] - t0[3]) * r,)
                           for t0, t1 in zip(p['tail_tufts'], RAISE)]
    return q


# ---------------------------------------------------------------- 行動の コマ
def frames_of(kind, base):
    """[(コマ, 常歩の コマ（足）, ポーズ（手前＝L の 名前）, spot の 上書き)]"""
    if kind == 'w':
        return [(i, i, base[i], {}) for i in range(N)]
    if kind == 's':
        return [(i, i, pose_shake(base[i], i / N), over_shake(i / N)) for i in range(N)]
    if kind == 'dl':
        return [(i, i, pose_down(base[i], i / N, i / N), {}) for i in range(N)]                 # 下げていく
    if kind == 'dd':
        return [(i, i, pose_down(base[i], i / N, 1.0, nod=1.0), {}) for i in range(N)]          # 下げて 歩く
    if kind == 'dr':
        return [(i, i, pose_down(base[i], i / N, 1 - i / N), {}) for i in range(N)]             # 上げていく
    if kind == 'p':
        return [(i, i % N, pose_poop(base[i % N], i), {}) for i in range(2 * N)]
    raise KeyError(kind)


def shape_key(kind, i):
    """3Dの 形が 同じ コマを まとめる 名前（しっぽは 3Dでは ない＝常歩と うんちは 同じ 形）"""
    return ('wp', i % N) if kind in ('w', 'p') else (kind, i)


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


def _draw_mv(tasks):
    """tasks：同じ 3Dの 形の [(kind, コマ, ポーズ, 上書き)]。馬ごとに 色を ぬって ROI で 切りぬく"""
    from horse_flat import draw_horse, first_out
    import horse3d as Hm
    J = _JB
    ox = J['ox']
    x0, y0, x1, y1 = J['roi']
    x0, x1 = x0 - ox, x1 - ox                     # 描く 画面の 中の ROI
    x0, y0, x1, y1 = zroi((x0, y0, x1, y1))        # 第4.112版：絵は Z 倍の 画素（ROI も Z 倍）
    out = []
    for kind, i, pose, over in tasks:
        for nm, pal, number in J['horses']:
            if kind == 'p' and nm not in POOP:
                continue
            sp = dict(J['spot'], pose=pose, cam=J['cam'], **over)
            sp.pop('cam_out', None)
            rgb, a, m = draw_horse(sp, pal, J['W'], J['H'], acc=None, number=number, name=f'pm{nm}{kind}{i}')
            s = m['s']
            th = np.asarray(m['P1'](Hm.v3(m['S']['tailhead'])), float) * s
            wi = np.asarray(m['P1'](Hm.v3(m['S']['withers'])), float) * s
            root = first_out(m['inside'], th, th - wi) / s - np.asarray(m['back_dir']) * 0.035 * m['p1u']
            a = np.asarray(a, np.float32)
            edge = max(float(a[y0:y1, x0].max()), float(a[y0:y1, x1 - 1].max()), float(a[y0, x0:x1].max()))
            out.append((kind, i, nm, rgb[y0:y1, x0:x1].astype(np.float16), a[y0:y1, x0:x1].astype(np.float16), edge,
                        [(float(h[0]) + ox, float(h[1])) for h in m['hooves']], (float(root[0]) + ox, float(root[1])), tuple(map(float, m['back_dir'])), float(m['p1u'])))
    return out


def group_spot(names):
    kind0, cloth0, numc0, num0, facing = PA.HORSES[names[0]]
    box = PA.BOX_NEAR if facing == 'right' else PA.BOX_FAR
    ox, cw = CANVAS[facing]
    spot = dict(pose='stand', facing=facing, box=(box[0] - ox, box[1], box[2] - ox, box[3]), azim=6 if facing == 'right' else -6,
                shadow=('#3A2A10', 0.0))                       # ext なし（管の のびは ポーズの cannon_ext）。box は 描く 画面の 中
    horses = []
    for nm in names:
        k, cloth, numc, num, fc = PA.HORSES[nm]
        assert fc == facing
        horses.append((nm, PA.pal(k, cloth, numc, '#F2C14E' if cloth != '#FFFFFF' else '#1A1A1A'), num))
    roi = (max(ox, box[0] - 120), max(0, box[1] - 84), min(ox + cw, box[2] + 120), H2)       # 2倍の 画素の 画面（780×320）の 中
    return spot, horses, box, facing, roi, (ox, cw)


def render_kinds(names, kinds, base, cam, workers=2):
    """同じ 向き・同じ 大きさの 馬たち（names）の 行動 kinds の コマ → {(kind, 名前): [コマ…]}"""
    spot, horses, box, facing, roi, (ox, cw) = group_spot(names)
    groups = {}
    for kind in kinds:
        for i, gi, pose, over in frames_of(kind, base):
            groups.setdefault(shape_key(kind, i), []).append((kind, i, G.with_facing(pose, facing), over))
    jobs = list(groups.values())
    job = dict(spot=spot, cam=cam, horses=horses, W=cw, H=H2, roi=roi, ox=ox)
    res = []
    if workers > 1:
        import multiprocessing as mp
        ctx = mp.get_context('spawn')            # fork だと 親の ライブラリの ロックを ひきついで 止まる ことが ある
        with ctx.Pool(workers, initializer=_init_mv, initargs=(job,)) as pool:
            for k, r in enumerate(pool.imap_unordered(_draw_mv, jobs, chunksize=1)):
                res += r
                if k % 8 == 0:
                    print(f'  {names[0]}… {kinds} {k + 1}/{len(jobs)}', flush=True)
    else:
        _init_mv(job)
        for r in map(_draw_mv, jobs):
            res += r
    out = {}
    for kind, i, nm, rgb, a, edge, hooves, root, bd, p1u in res:
        assert edge < 0.01, (kind, i, nm, edge)                 # ROI の はしに 馬が かからない
        out.setdefault((kind, nm), {})[i] = (rgb, a, hooves, root, bd, p1u)
    return {k: [v[i] for i in range(len(v))] for k, v in out.items()}, roi


def zroi(roi):
    """2倍の 画素の 四角 → 絵の 画素（Z 倍。どの はしも ちょうど 画素に なる 所だけ）"""
    out = [v * Z for v in roi]
    assert all(abs(v - round(v)) < 1e-6 for v in out), roi
    return tuple(int(round(v)) for v in out)


def full(rgb, a, roi):
    """ROI の 切りぬき → 画面の 大きさ（make_sheet 用・Z 倍の 画素）"""
    x0, y0, x1, y1 = zroi(roi)
    R = np.zeros((ZH, ZW, 3), np.float32)
    A = np.zeros((ZH, ZW), np.float32)
    R[y0:y1, x0:x1] = rgb.astype(np.float32)
    A[y0:y1, x0:x1] = a.astype(np.float32)
    return R, A


# ---------------------------------------------------------------- 地面と 上下（どの シートも 同じ）
def ground_line(box):
    return box[3] - 4


def frame_dy(m0, facing, box):
    """コマ（常歩の 0〜23）ごとの 上下の ずらし（2倍の 画素）：地面に ついて いる 手前の ひづめが いつも 地面の 線に くる。
       ひづめは 体から 見て Y_G − bob(g) の 高さ（paddock_gait）＝ずらしは 体の 上下 だけ"""
    import horse3d as Hm
    zn = 0.15 if facing == 'right' else -0.15             # 手前の ひづめの 目印の z（horse_flat の hooves と 同じ）
    g0 = ground_line(box)
    return [g0 - float(m0['P1'](Hm.v3((XV, G.Y_G - G.bob(i / N)), zn))[1]) for i in range(N)]


def near_legs(facing):
    return ('FL', 'HL') if facing == 'right' else ('FR', 'HR')


def stance_of(g, facing):
    legs = G.stance(g)
    if facing == 'left':
        sw = {'FL': 'FR', 'FR': 'FL', 'HL': 'HR', 'HR': 'HL'}
        legs = [sw[k] for k in legs]
    return legs


def speed_of(frames, facing):
    """地面に ついて いる 手前の ひづめが すべらない 横の はやさ（2倍の 画素／コマ）：つぎの コマでも 地面に ついて いる 足の ひづめの 動きの 平均"""
    vals = []
    for i in range(N):
        j = (i + 1) % N
        for k in near_legs(facing):
            if k in stance_of(i / N, facing) and k in stance_of(j / N, facing):
                vals.append(frames[i][2][HOOF_ORDER.index(k)][0] - frames[j][2][HOOF_ORDER.index(k)][0])
    return sum(vals) / len(vals)


def check_ground(frames, dys, facing, box, tag):
    """地面に ついて いる 手前の ひづめが 地面の 線から どれだけ ずれるか（2倍の 画素）"""
    g0 = ground_line(box)
    worst = 0.0
    for i, fr in enumerate(frames):
        for k in near_legs(facing):
            if k in stance_of((i % N) / N, facing):
                worst = max(worst, abs(fr[2][HOOF_ORDER.index(k)][1] + dys[i % N] - g0))
    print(f'  {tag}: 地面の 線からの ずれ 最大 {worst:.2f}px（2倍の 画素）', flush=True)
    return worst


def walk_shadow(frames, box):
    xs = [h[0] for fr in frames for h in fr[2]]
    g = ground_line(box)
    return ('#3A2A10', (min(xs) + max(xs)) / 2, g + 3, (max(xs) - min(xs)) * 0.52, 5.0, 0.22)


def build_sheet(nm, kind, frs, dy24, box, facing, roi, sh, out=None, extra_meta=None):
    """1頭・1つの 行動の シート（make_sheet）→ 絵の id と meta（blobs.json）"""
    frames = [full(rgb, a, roi) + (hooves,) for rgb, a, hooves, root, bd, p1u in frs]
    dys = [dy24[i % N] for i in range(len(frames))]
    check_ground(frames, dys, facing, box, f'{nm}_{kind}')
    drops = []
    extra = None
    if kind == 'p':
        g0 = ground_line(box)
        for st, dx in DROPS:
            r0, bd0, p1u = frs[st][3], frs[st][4], frs[st][5]
            rb = DUNG_R * p1u                                   # うんちの 半径（2倍の 画素：ほんとうより 少し 大きく＝見える ように）
            x = r0[0] + bd0[0] * 0.03 * p1u + dx * rb
            y0 = r0[1] + 0.09 * p1u + dys[st]
            drops.append(dict(f=st, x=round(x, 2), y0=round(y0, 2), g=round(g0 - rb * 0.86, 2), r=round(rb, 2)))

        def extra(i, pre, A):
            for d in drops:
                q = drop_at(d, i)
                if q:
                    pre, A = dung_ball(pre, A, *(v * Z for v in q))    # 第4.112版：絵は Z 倍の 画素
            return pre, A
    u8, meta = make_sheet(frames, dys, shadow=sh, extra=extra)
    meta['dy'] = [round(float(d), 2) for d in dys[:N]]
    meta['facing'] = facing
    meta.update(extra_meta or {})
    if drops:
        meta['drops'] = drops
        meta['fall'] = FALL
        meta['dung_r'] = DUNG_R
    if out:
        preview_png(u8, os.path.join(out, f'paddock_{nm}_{kind}.png'), bg=(196, 170, 120))
    bid = save_small(u8)
    name = nm if kind == 'w' else f'{nm}_{kind}'
    record('paddock', name, bid, meta)
    print(name, bid, {k: v for k, v in meta.items() if k not in ('dy', 'drops')}, u8.shape, flush=True)
    return bid, meta


def save_small(u8):
    """RGBA（u8）を 小さな WebP に（PIL：質 QUALITY・method 6・すき通しの 質 ALPHA_Q）→ id（中身の md5）"""
    import hashlib
    import io
    from PIL import Image
    b = io.BytesIO()
    Image.fromarray(u8, 'RGBA').save(b, 'WEBP', quality=QUALITY, method=6, alpha_quality=ALPHA_Q)
    data = b.getvalue()
    bid = hashlib.md5(data).hexdigest()
    os.makedirs(BLOB_DIR, exist_ok=True)
    open(os.path.join(BLOB_DIR, bid + '.webp'), 'wb').write(data)
    return bid


def recompress(names):
    """できて いる シートを いまの QUALITY・ALPHA_Q で 小さく 保存し直す（3Dを 描き直さない）"""
    from PIL import Image
    B = json.load(open(os.path.join(PACK, 'blobs.json'), encoding='utf-8'))['paddock']
    for key in sorted(B):
        if key == 'still' or key.split('_')[0] not in names:
            continue
        meta = B[key]
        src = os.path.join(BLOB_DIR, meta['id'] + '.webp')
        u8 = np.array(Image.open(src).convert('RGBA'))
        bid = save_small(u8)
        record('paddock', key, bid, {k: v for k, v in meta.items() if k != 'id'})
        print(key, meta['id'][:8], '→', bid[:8], os.path.getsize(src), '→', os.path.getsize(os.path.join(BLOB_DIR, bid + '.webp')), flush=True)


def drop_at(d, i):
    """コマ i の 落ちて いる うんち d の (x, y, 半径)。落ちて いない／地面に ついた（ページの 部品）なら None"""
    k = i - d['f']
    if not 0 <= k < FALL:
        return None
    t = (k + 0.6) / FALL
    return d['x'], d['y0'] + (d['g'] - d['y0']) * t * t, d['r'] * (0.75 + 0.25 * min(1.0, t * 2))


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


STAGES = (('w', 'p'), ('s',), ('dl', 'dd', 'dr'))      # いっしょに 描く 行動（常歩と うんちは 3Dの 形が 同じ）


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    opts = {a.split('=')[0]: (a.split('=')[1] if '=' in a else '1') for a in sys.argv[1:] if a.startswith('--')}
    only = opts.get('--only', 'w,s,d,p').split(',')
    only = [k for k in only if k != 'd'] + (['dl', 'dd', 'dr'] if 'd' in only else [])
    out = opts.get('--out') or os.environ.get('OUT')
    if out:
        os.makedirs(out, exist_ok=True)
    names = args or list(NEAR + FAR)
    if '--recompress' in opts:
        recompress(names)
        return
    base = G.cycle(N)
    print('常歩：地面に ついて いる ひづめの ずれ 最大', round(max(p['_err'] for p in base) * 1000, 2), 'mm', flush=True)
    for grp in (NEAR, FAR):
        nms = [n for n in names if n in grp]
        if not nms:
            continue
        spot, horses, box, facing, roi, (ox, cw) = group_spot(nms)
        cam, m0 = camera(horses[0][1], spot, horses[0][2], 'pmref' + nms[0], W=cw, H=H2)
        dy24 = frame_dy(m0, facing, box)
        speed, sh = None, None
        for stage in STAGES:
            kinds = [k for k in stage if k in only and (k != 'p' or any(n in POOP for n in nms))]
            if not kinds:
                continue
            if sh is None and 'w' not in kinds:                 # 影と はやさは 常歩の シートから（blobs.json の 常歩の meta を 使う）
                meta_w = json.load(open(os.path.join(os.path.dirname(HERE), 'blobs.json'), encoding='utf-8'))['paddock'][nms[0]]
                sh = tuple(meta_w['shadow'])
            res, roi = render_kinds(nms, kinds, base, cam, workers=int(opts.get('--workers', '2')))
            for nm in nms:
                if 'w' in kinds:
                    frs = res[('w', nm)]
                    fr3 = [(None, None, h) for _, _, h, _, _, _ in frs]
                    v = speed_of(fr3, facing)
                    speed = round(abs(v) / 2 * N / CYCLE, 2)        # CSS の px／秒
                    sh = walk_shadow(fr3, box)
                    build_sheet(nm, 'w', frs, dy24, box, facing, roi, sh, out, dict(speed=speed, shadow=[sh[0]] + [round(float(x), 2) for x in sh[1:]]))
                for kind in kinds:
                    if kind == 'w' or (kind, nm) not in res:
                        continue
                    build_sheet(nm, kind, res[(kind, nm)], dy24, box, facing, roi, sh, out)
            del res


if __name__ == '__main__':
    main()
