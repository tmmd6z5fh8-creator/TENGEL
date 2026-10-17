"""馬らしい形の、ぺたっとした色の競走馬（線なし）：午年・雪・紅葉・海・桜のテーマ用（第2版）
   - 体・首・頭・足は3Dの馬（horse3d）の形を3倍の大きさで描いて、色でぬる → 長い首・長く細い足・細長い頭の、ほんとうの馬のつりあい。
     光の当たらない面だけ少し暗い色（1段だけ）、奥の足と奥の耳はもっと暗い色、鼻先は明るい色、ひづめは暗い色
   - 目はアーモンド形に白い光。鼻の穴・口
   - たてがみ：首の上のふちから、首の横にたれて うしろへ流れる房（下に暗い色の房がのぞく）。前髪。しっぽは3つの房
   - 頭のベルト（鼻・ほお・ひたい・のど）・はみの輪・手綱、鞍の下の布（番号）・鞍・腹帯
   SVG の部分は librsvg で3倍に描く（cute_horse.svg_rgba：何回描いても同じ絵）。形はすべて一から作ったオリジナル。
   draw_horse(spec, pal, W, Hh, acc) → (色, アルファ, 目印)：1倍の大きさ"""
import sys, os, math
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
sys.path.insert(0, HERE)
import shutil
import style2d as S2
from style2d import frame_horse, world_pos, hexc, blur
from h3d import Scene
import horse3d as Hm
from cute_horse import svg_rgba, smooth, f2, path, stroke, circ, ell, unit, V, lock_d, tuft, mix
from throat_fix import slim_throat

S3 = 3
HEAD_SC = 1.14

# ポーズ（near＝手前の足・far＝奥の足。向きに合わせて L／R に入れかえる）
POSES = {
    'stand': dict(theta=0.0, neck_rot=-4.0, head_ang=-56.0, tail=[-118, -100], tail_kind='hang',
                  fore_near=[-125, -90, -90, -60], fore_far=[-122, -92, -90, -60],
                  hind_near=[-60, -118, -92, -62], hind_far=[-64, -116, -92, -62]),
    'walk': dict(theta=0.0, neck_rot=-6.0, head_ang=-54.0, tail=[-118, -100], tail_kind='sway',
                 fore_near=[-100, -38, -112, -142], fore_far=[-126, -92, -90, -60],
                 hind_near=[-66, -116, -92, -62], hind_far=[-56, -122, -94, -64]),
    'prance': dict(theta=8.0, neck_rot=-8.0, head_ang=-62.0, tail=[-130, -108], tail_kind='sway',
                   fore_near=[-84, -8, -98, -132], fore_far=[-120, -94, -90, -62],
                   hind_near=[-56, -114, -88, -60], hind_far=[-66, -120, -94, -64]),
    'gallop': dict(theta=3.0, neck_rot=-22.0, head_ang=-46.0, tail=[-160, -150], tail_kind='fly',
                   fore_near=[-66, -28, -38, -22], fore_far=[-122, -22, -145, -172],
                   hind_near=[-116, -154, -128, -148], hind_far=[-60, -104, -74, -48]),
}
# しっぽの房：(p1, p2, p3 は根元からのずれ［うしろ, 下］m, ふくらみ m)。うしろの房から
TAILS = {
    'hang': [((0.20, 0.08), (0.40, 0.50), (0.42, 0.90), 0.22), ((0.10, 0.10), (0.18, 0.56), (0.08, 0.94), 0.18),
             ((0.16, 0.00), (0.30, 0.42), (0.24, 0.98), 0.30)],
    'sway': [((0.24, 0.04), (0.52, 0.40), (0.62, 0.84), 0.22), ((0.12, 0.08), (0.28, 0.54), (0.26, 0.96), 0.18),
             ((0.20, -0.04), (0.44, 0.34), (0.48, 0.94), 0.30)],
    'fly': [((0.26, -0.02), (0.60, 0.12), (1.0, 0.28), 0.22), ((0.22, -0.12), (0.52, -0.22), (0.92, -0.14), 0.18),
            ((0.26, -0.10), (0.62, -0.06), (1.08, 0.08), 0.28)],
}


def make_pose(name, facing):
    P = POSES[name]
    near, far = ('L', 'R') if facing == 'right' else ('R', 'L')
    return dict(theta=P['theta'], neck_rot=P['neck_rot'], head_ang=P['head_ang'], tail=P['tail'],
                fore={near: P['fore_near'], far: P['fore_far']}, hind={near: P['hind_near'], far: P['hind_far']})


def proc_tmp():
    """このプロセスだけの作業フォルダ（いくつ同時に動かしても、3Dの描画の一時ファイルがぶつからない）"""
    d = os.path.join(S2.TMP, f'hf{os.getpid()}')
    os.makedirs(d, exist_ok=True)
    return d


def render_body(pose, eye, tgt, fov, W, Hh, name, tmp, throat=None):
    """style2d.render_horse と同じ形（しっぽの根元の3Dの出っぱりだけ作らない：しっぽは房で描く）"""
    sc = Scene()
    sc.image(W, Hh, 1)
    sc.camera(np.asarray(eye, float), np.asarray(tgt, float), fov)
    sc.bounce(0)
    sc.env((0.5, 0.5, 0.5), (0.4, 0.4, 0.4), (0.2, 0.2, 0.2))
    sc.light((0.5, 0.8, 0.6), (2.0, 2.0, 2.0), 10, 1)
    sc.mat(1, 1, (0.6, 0.6, 0.6), 0.6)
    sc.mat(5, 1, (0.02, 0.02, 0.02), 0.1)
    sc.mat(6, 1, (0.3, 0.3, 0.3), 0.6)
    S0 = Hm.skeleton(pose)
    ta0 = Hm.v3(S0['tailhead'])
    t10 = Hm.v3(S0['tailhead'] + Hm.adir(pose['tail'][0]) * 0.20)
    rc0 = sc.rcone

    def rc(a_, b_, *args, **kw):
        if np.allclose(np.asarray(a_, float), ta0) or np.allclose(np.asarray(a_, float), t10):
            return
        return rc0(a_, b_, *args, **kw)

    sc.rcone = rc
    with slim_throat(sc, pose, **(throat or {})):                  # のど元をすっきり（spec の throat があるときだけ：throat_fix.py）
        S = Hm.build(sc, pose, mats=dict(body=1, neck=1, hoof=6, eye=5, head=1))
    sc.rcone = rc0
    R = sc.render(os.path.join(tmp, name))
    R['S'], R['scene'] = S, sc
    return R


def first_out(mask, p, d, step=0.5, maxn=800):
    """p から d の向きに進んで、mask の外に出る直前の点（3倍の画素）"""
    H3, W3 = mask.shape
    d = unit(d)
    q = np.asarray(p, float)
    last = q.copy()
    for _ in range(maxn):
        xi, yi = int(round(q[0])), int(round(q[1]))
        if not (0 <= xi < W3 and 0 <= yi < H3) or not mask[yi, xi]:
            return last
        last = q.copy()
        q = q + d * step
    return last


def sm1(a, k=5):
    a = np.asarray(a, float)
    h = k // 2
    return np.convolve(np.r_[np.full(h, a[0]), a, np.full(h, a[-1])], np.ones(k) / k, 'valid')


def draw_horse(spec, pal, W, Hh, acc=None, number='1', name='flat'):
    """spec: pose・facing・box・azim・elev。pal: 色。acc: 飾り（関数 (marks) → dict(dapples・cloth・neck・head・front・back)）"""
    s = S3
    pal = dict(pal)
    pal.setdefault('earIn', pal['shade'])
    pal.setdefault('nostril', mix(pal['eye'], pal['muzzle'], 0.5))
    pal.setdefault('saddleFlap', mix('#FFFFFF', pal['saddle'], 0.14))
    pal.setdefault('bodyShade', mix(pal['shade'], pal['body'], 0.55))
    pal.setdefault('muzzleShade', mix(pal['shade'], pal['muzzle'], 0.40))
    facing = spec['facing']
    fx = 1.0 if facing == 'right' else -1.0
    pose = make_pose(spec['pose'], facing)
    Hm.HEAD_SCALE = HEAD_SC
    W3, H3 = W * s, Hh * s
    tmp, tmp0 = proc_tmp(), S2.TMP
    S2.TMP = tmp                                                         # frame_horse の一時ファイルも このフォルダへ
    try:
        e, t = frame_horse(pose, tuple(v * s for v in spec['box']), W3, H3, facing=facing, azim=spec.get('azim', 0.0), elev=spec.get('elev', 3.0))
        R = render_body(pose, e, t, 26, W3, H3, name, tmp, throat=spec.get('throat'))
    finally:
        S2.TMP = tmp0
        shutil.rmtree(tmp, ignore_errors=True)
    sc, S = R['scene'], R['S']
    cam = np.asarray(e, float) - np.asarray(t, float)
    side = 1.0 if cam[2] >= 0 else -1.0
    P1 = lambda p3: sc.project(np.asarray([p3], float))[0][0][:2] / s        # 世界の点 → 1倍の画素
    P3 = lambda p3: sc.project(np.asarray([p3], float))[0][0][:2]            # → 3倍の画素
    hp = lambda a_, b_, z=0.0: Hm.head_pt(S, a_, b_, z)
    wv = np.asarray(S['withers'], float)
    ppu = np.linalg.norm(P3(Hm.v3(wv)) - P3(Hm.v3(wv) + np.array([1.0, 0, 0])))   # 3倍の画素 / m
    p1u = ppu / s

    # ---------------- ぬり（3倍） ----------------
    a = np.clip(R['a'], 0, 1)
    inside = a > 0.5
    m = np.round(R['m']).astype(int) * inside
    Pw = world_pos(R)
    Pn = np.nan_to_num(Pw, nan=99.0)
    zs = Pn[..., 2] * side

    def segd(p0, p1):
        p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
        dd = p1 - p0
        tt = np.clip(np.sum((Pn - p0) * dd, -1) / np.dot(dd, dd), 0, 1)
        return np.linalg.norm(Pn - (p0 + tt[..., None] * dd), axis=-1), tt

    def segd2(p0, p1):
        """横から見た（xy だけの）線分までの距離"""
        p0, p1 = np.asarray(p0, float)[:2], np.asarray(p1, float)[:2]
        dd = p1 - p0
        q = Pn[..., :2]
        tt = np.clip(np.sum((q - p0) * dd, -1) / np.dot(dd, dd), 0, 1)
        return np.linalg.norm(q - (p0 + tt[..., None] * dd), axis=-1)

    u2 = Hm.adir(S['head_ang'])
    v2 = np.array([-u2[1], u2[0]])
    U3, V3 = Hm.v3(u2), Hm.v3(v2)
    # 奥の足・奥の耳だけを暗い色に（背中の上にのぞく奥がわの筋肉は体の色のまま）
    fk = 'R' if side > 0 else 'L'
    near_far_leg = np.zeros(inside.shape, bool)
    for key, chain in (('F' + fk, ('ps', 'el', 'kn', 'ft', 'co', 'hf')), ('H' + fk, ('st', 'hk', 'ft', 'co', 'hf'))):
        J = S[key]
        for j in range(len(chain) - 1):
            near_far_leg |= segd2(J[chain[j]], J[chain[j + 1]]) < (0.10 if j else 0.08)
    d_ear_f = Hm.nrm(-U3 * 0.9 + V3 * 0.25 + np.array([0, 0, -0.30 * side]))
    b_ear_f = hp(0.0, 0.02, -0.058 * side)
    ear_f = segd(b_ear_f, b_ear_f + d_ear_f * 0.19 * HEAD_SC)[0] < 0.05 * HEAD_SC
    far = inside & (zs < -0.045) & (near_far_leg | ear_f)

    rel = Pn[..., :2] - np.asarray(S['poll'])
    hs = (rel @ u2) / HEAD_SC
    head = inside & (segd(Hm.v3(S['poll']), hp(0.56, -0.03))[0] < 0.21 * HEAD_SC)
    muzzle = head & (hs > 0.44) & ~far
    # 耳の中（手前の耳）
    d_ear = Hm.nrm(-U3 * 0.9 + V3 * 0.25 + np.array([0, 0, 0.30 * side]))
    b_ear = hp(0.0, 0.02, 0.058 * side)
    ear_in = inside & (segd(b_ear + d_ear * 0.05 * HEAD_SC, b_ear + d_ear * 0.15 * HEAD_SC)[0] < 0.013 * HEAD_SC) & (zs > 0.02)

    # 光の当たらない面（1段だけ）：法線をなめらかにしてから
    Lv = np.array([0.30, 0.85, 0.45 * side])
    Lv /= np.linalg.norm(Lv)
    lit = np.sum(R['n'] * Lv, -1)
    a_ = inside.astype(np.float32)
    sg = max(2.0, H3 / 55)
    lit = blur((lit * a_).astype(np.float32), sg) / np.maximum(blur(a_, sg), 1e-3)
    tsh = (1 - np.clip((lit - spec.get('band', 0.10)) / 0.03, 0, 1)).astype(np.float32)

    col = np.zeros((H3, W3, 3), np.float32)
    body_c, bshade_c = hexc(pal['body']), hexc(pal['bodyShade'])
    mz_c, mzs_c = hexc(pal['muzzle']), hexc(pal['muzzleShade'])
    col[:] = body_c * (1 - tsh[..., None]) + bshade_c * tsh[..., None]
    col[muzzle] = (mz_c * (1 - tsh[..., None]) + mzs_c * tsh[..., None])[muzzle]
    col[far] = hexc(pal['shade'])
    col[ear_in] = hexc(pal['earIn'])
    col[m == 6] = hexc(pal['hoof'])
    col[m == 5] = hexc(pal['eye'])
    A = a.astype(np.float32).copy()

    def comp(rgb, al):
        nonlocal col, A
        col = col * (1 - al[..., None]) + rgb * al[..., None]
        A = np.maximum(A, al)

    def layer(parts, mask=None):
        """SVG の部品（1倍の座標）→ 3倍で描いて重ねる（mask があれば その中だけ）"""
        if not parts:
            return
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{Hh}" viewBox="0 0 {W} {Hh}">' + ''.join(parts) + '</svg>'
        pm = svg_rgba(svg, W3, H3)
        al = pm[..., 3]
        if mask is not None:
            al = al * mask
            pm = pm * mask[..., None]
        rgb = np.where(al[..., None] > 1e-4, pm[..., :3] / np.maximum(pm[..., 3:4], 1e-4), 0)
        comp(rgb, al)

    # ---------------- 目印（1倍） ----------------
    back_dir = unit(P1(Hm.v3(S['tailhead'])) - P1(Hm.v3(S['withers'])))      # 体のうしろの向き（画面）
    body_mask = inside & ~far

    def backline(x1):
        """1倍の x での背中の上のふち（1倍の y）"""
        xi = int(round(x1 * s))
        c_ = np.nonzero(body_mask[:, xi])[0]
        return c_.min() / s if len(c_) else None

    wx = lambda dx: P1(Hm.v3(wv + np.array([dx, 0.0]), 0.2 * side))[0]
    # 鞍の下の布（背中にそって、下は まっすぐ）
    xa, xb = wx(-0.04), wx(-0.70)
    x0, x1 = min(xa, xb), max(xa, xb)
    xs = np.linspace(x0, x1, 28)
    tops = sm1([backline(x) for x in xs], 5)
    ytop_mid = tops[len(tops) // 2]
    ybot = ytop_mid + 0.44 * p1u
    rr = 0.055 * p1u
    cl = [V(x, y + 0.012 * p1u) for x, y in zip(xs, tops)]
    cloth_pts = cl + [V(x1, ybot - rr), V(x1 - rr * 0.3, ybot - rr * 0.3), V(x1 - rr, ybot), V(x0 + rr, ybot), V(x0 + rr * 0.3, ybot - rr * 0.3), V(x0, ybot - rr)]
    cloth_d = 'M' + ' L'.join(f'{f2(p[0])},{f2(p[1])}' for p in cloth_pts) + ' Z'
    trim_y = ybot - 0.075 * p1u
    # 鞍（低くて長い：前に小さな前橋、うしろに後橋）
    sx = np.linspace(wx(-0.06), wx(-0.50), 24)
    stop = sm1([backline(x) for x in sx], 5)
    tt = np.linspace(0, 1, len(sx))
    rise = (0.055 * np.exp(-((tt - 0.05) / 0.09) ** 2) + 0.014 + 0.05 * np.exp(-((tt - 0.97) / 0.08) ** 2)) * p1u
    seat_top = [V(x, y - r_) for x, y, r_ in zip(sx, stop, rise)]
    seat_bot = [V(x, y + 0.035 * p1u) for x, y in zip(sx[::-1], stop[::-1])]
    seat_d = smooth(seat_top + seat_bot)
    i0, i1 = 3, 15
    flap = [V(sx[i0], stop[i0] + 0.02 * p1u), V(sx[i1], stop[i1] + 0.02 * p1u), V(sx[i1] - fx * 0.01 * p1u, stop[i1] + 0.17 * p1u),
            V(sx[i0] + fx * 0.02 * p1u, stop[i0] + 0.17 * p1u)]
    xg = wx(-0.17)
    yg0 = backline(xg)
    gb = first_out(body_mask, V(xg * s, (yg0 + 0.05 * p1u) * s), V(0, 1)) / s
    gw = 0.024 * p1u
    girth_d = f'M{f2(xg - gw)},{f2(yg0)} L{f2(xg + gw)},{f2(yg0)} L{f2(xg + gw * 1.1)},{f2(gb[1] + 0.6)} L{f2(xg - gw * 1.1)},{f2(gb[1] + 0.6)} Z'

    # 首（飾り用）：t は 0＝き甲 … 1＝うなじ
    crest = Hm.bez(S['crest'], np.linspace(0, 1, 41))
    throat = Hm.bez(S['throat'], np.linspace(0, 1, 41))

    def collar(t_):
        """首の t のところの、上のふち・下のふち（1倍）と首にそった向き（頭がわ）"""
        i = int(round(np.clip(t_, 0, 1) * 40))
        c3, th3 = P3(Hm.v3(crest[i])), P3(Hm.v3(throat[i]))
        top = first_out(inside, (c3 + th3) / 2, c3 - th3) / s
        bot = first_out(inside, (c3 + th3) / 2, th3 - c3) / s
        j = min(40, i + 2)
        k = max(0, i - 2)
        ax = unit((P1(Hm.v3(crest[j])) + P1(Hm.v3(throat[j]))) / 2 - (P1(Hm.v3(crest[k])) + P1(Hm.v3(throat[k]))) / 2)
        return top, bot, ax

    ear_tip = P1(b_ear + d_ear * 0.17 * HEAD_SC)
    eye_c = P1(hp(0.152, 0.036, 0.091 * side))
    head_dir = unit(P1(hp(0.4, 0.0)) - P1(hp(0.0, 0.0)))
    marks = dict(P1=P1, hp=hp, side=side, fx=fx, p1u=p1u, back_dir=back_dir, collar=collar, facing=facing,
                 cloth=(x0, x1, ytop_mid, ybot, trim_y), cloth_d=cloth_d, inside=inside, body_mask=body_mask, s=s,
                 poll=P1(Hm.v3(S['poll'])), muzzle=P1(hp(0.60, -0.03, 0.0)), ear_base=P1(b_ear), ear_tip=ear_tip,
                 forelock=P1(hp(0.06, 0.08, 0.03 * side)), eye=eye_c, head_dir=head_dir,
                 torso=(wx(0.0), wx(-1.2)), wx=wx, cloth_top=lambda x_: float(np.interp(x_, xs, tops)))
    hooves = [P1(Hm.v3(S[k]['hf'], 0.15 * S[k]['z'])) for k in ('FL', 'FR', 'HL', 'HR')]
    marks['hooves'] = hooves
    marks['ground'] = max(h[1] for h in hooves)
    marks['bottom'] = float(np.nonzero(inside.any(1))[0].max() + 1) / s       # 馬の体のいちばん下（ひづめの下のふち）
    extra = acc(marks) if acc is not None else {}

    # ---------------- 重ね（3倍） ----------------
    if extra.get('dapples'):                                               # まだら（雪）：胴の中だけ
        torso = body_mask & ~head & (m == 1)
        layer(extra['dapples'], mask=torso.astype(np.float32))
    cl_parts = [path(cloth_d, pal['cloth']), stroke(f'M{f2(x0 - 2)},{f2(trim_y)} H{f2(x1 + 2)}', pal['clothTrim'], 0.05 * p1u)]
    cl_parts += extra.get('cloth', [])
    layer(cl_parts, mask=body_mask.astype(np.float32))
    layer([path(girth_d, pal['saddle'])], mask=body_mask.astype(np.float32))
    layer([path(smooth(flap), pal['saddleFlap']), path(seat_d, pal['saddle'])])

    # たてがみ：首の上のふち → 首の横にたれて、うしろへ流れる房
    tops2 = []
    for i in range(41):
        c3, th3 = P3(Hm.v3(crest[i])), P3(Hm.v3(throat[i]))
        tops2.append(first_out(inside, (c3 * 0.8 + th3 * 0.2), c3 - th3) / s)
    tops2 = np.array(tops2)
    tops2 = np.stack([sm1(tops2[:, j], 7) for j in (0, 1)], 1)
    tg = np.gradient(tops2, axis=0)
    tg /= np.linalg.norm(tg, axis=1, keepdims=True) + 1e-9
    nr = np.stack([tg[:, 1], -tg[:, 0]], 1)
    if nr[20, 1] > 0:
        nr = -nr                                                          # 外向き（上）
    Tm = lambda f: tops2[int(np.clip(round(f * 40), 0, 40))]
    Nm = lambda f: nr[int(np.clip(round(f * 40), 0, 40))]
    f0, f1 = 0.02, 0.94
    up_edge = [Tm(f) + Nm(f) * (0.024 * p1u) * math.sin(math.pi * np.clip((f - f0) / (f1 - f0), 0, 1)) ** 0.5 for f in np.linspace(f0, f1, 18)]
    K = 6
    var = spec.get('mane_var', (1.0, 1.14, 0.9, 1.1, 0.96, 1.06))
    Lb = 0.21 * p1u * spec.get('mane_len', 1.0)
    low, sharp = [], []
    n_up = len(up_edge)
    for k in range(K, 0, -1):                                              # うなじ → き甲
        fa = f0 + (f1 - f0) * k / K
        fb = f0 + (f1 - f0) * (k - 1) / K
        w_ = fa - fb
        fm = (fa + fb) / 2
        prof = 0.62 + 0.38 * math.sin(math.pi * (0.12 + 0.76 * (fm - f0) / (f1 - f0)))
        L = Lb * prof * var[(K - k) % len(var)]
        if k == K:
            low.append(Tm(fa) - Nm(fa) * L * 0.18)
        else:
            low.append(Tm(fa) - Nm(fa) * L * 0.36)
        q = fa - 0.10 * w_
        low.append(Tm(q) - Nm(q) * L * 0.78)
        q = fa - 0.55 * w_
        sharp.append(n_up + len(low))
        low.append(Tm(q) - Nm(q) * L + back_dir * 0.05 * p1u)                # 房の先（うしろへ流れる）
        q = fb + 0.30 * w_
        low.append(Tm(q) - Nm(q) * L * 0.50)
    low.append(Tm(f0) - Nm(f0) * 0.03 * p1u)
    mane_pts = up_edge + low
    mane_d = smooth(mane_pts, sharp=sharp)
    under = [p - (Nm(0.5) * 0.035 * p1u) + back_dir * 0.035 * p1u for p in mane_pts]
    mane_parts = [path(smooth(under, sharp=sharp), pal['maneD']), path(mane_d, pal['mane'])]
    for k in range(K, 0, -1):                                              # 房の中の すじ
        fa = f0 + (f1 - f0) * k / K
        fb = f0 + (f1 - f0) * (k - 1) / K
        w_ = fa - fb
        fm = (fa + fb) / 2
        prof = 0.62 + 0.38 * math.sin(math.pi * (0.12 + 0.76 * (fm - f0) / (f1 - f0)))
        L = Lb * prof * var[(K - k) % len(var)]
        q0, q1 = fa - 0.25 * w_, fa - 0.45 * w_
        a_p = Tm(q0) - Nm(q0) * L * 0.18
        b_p = Tm(q1) - Nm(q1) * L * 0.72 + back_dir * 0.03 * p1u
        mane_parts.append(stroke(smooth([a_p, (a_p + b_p) / 2 - Nm(q0) * 0.0 + back_dir * 0.004 * p1u, b_p], closed=False), pal['maneD'], 0.02 * p1u))
    # 前髪（耳のあいだから、ひたいへ）
    fb_ = P1(hp(0.0, 0.075, 0.03 * side))
    mane_parts.append(path(tuft(fb_, P1(hp(0.21, 0.075, 0.075 * side)), 0.08 * p1u, bend=0.12, side=-fx), pal['maneD']))
    mane_parts.append(path(tuft(fb_, P1(hp(0.18, 0.10, 0.07 * side)), 0.07 * p1u, bend=0.10, side=fx), pal['mane']))
    layer(mane_parts)
    layer(extra.get('neck', []))

    # 顔：目・鼻の穴・口・頭のベルト・はみ・手綱
    ang = math.degrees(math.atan2(head_dir[1], head_dir[0]))
    er = 0.034 * p1u
    face = [ell(eye_c, er, er * 0.74, ang - 14 * fx, pal['eye']),
            circ(eye_c + head_dir * er * 0.28 + V(0, -er * 0.30), er * 0.30, '#FFFFFF')]
    nos = P1(hp(0.535, 0.024, 0.06 * side))
    face.append(ell(nos, 0.024 * p1u, 0.014 * p1u, ang - 30 * fx, pal['nostril']))
    face.append(stroke(smooth([P1(hp(0.50, -0.098, 0.06 * side)), P1(hp(0.545, -0.088, 0.06 * side)), P1(hp(0.585, -0.070, 0.05 * side))], closed=False), pal['nostril'], 0.016 * p1u))
    tw = 0.030 * p1u
    zz = 0.094 * side
    ring = P1(hp(0.48, -0.092, zz))
    face.append(stroke(smooth([P1(hp(0.395, 0.055, zz)), P1(hp(0.40, -0.02, zz * 1.05)), P1(hp(0.42, -0.10, zz))], closed=False), pal['tack'], tw))       # 鼻
    face.append(stroke(smooth([P1(hp(0.02, 0.035, zz)), P1(hp(0.22, -0.035, zz * 1.05)), ring], closed=False), pal['tack'], tw))                        # ほお
    face.append(stroke(smooth([P1(hp(0.09, 0.085, zz)), P1(hp(0.035, 0.045, zz))], closed=False), pal['tack'], tw))                                    # ひたい
    face.append(stroke(smooth([P1(hp(0.03, 0.02, zz)), P1(hp(0.06, -0.09, zz)), P1(hp(0.13, -0.17, zz * 0.9))], closed=False), pal['tack'], tw * 0.85))   # のど
    pommel = V(sx[1], stop[1] - 0.05 * p1u)
    sag = (ring + pommel) / 2 + V(0, 0.14 * p1u)
    face.append(stroke(smooth([ring, sag, pommel], closed=False), pal['tack'], 0.024 * p1u))                                                                # 手綱
    face.append(circ(ring, 0.040 * p1u, 'none', f'stroke="{pal["ring"]}" stroke-width="{f2(0.02 * p1u)}"'))
    layer(face)
    layer(extra.get('head', []))
    # 番号
    cx_ = (x0 + x1) / 2
    cy_ = (ytop_mid + 0.03 * p1u + trim_y) / 2
    size = 0.27 * p1u
    layer([f'<text x="{f2(cx_)}" y="{f2(cy_ + size * 0.36)}" font-family="Noto Sans CJK JP" font-weight="900" font-size="{f2(size)}" '
           f'fill="{pal["num"]}" text-anchor="middle">{number}</text>'])
    layer(extra.get('front', []))

    # しっぽ（体のうしろ）：いちばん下にしく
    th = P3(Hm.v3(S['tailhead']))
    root = first_out(inside, th, th - P3(Hm.v3(S['withers']))) / s - back_dir * 0.035 * p1u
    kind = POSES[spec['pose']]['tail_kind']
    dn = V(0, 1.0)
    tparts = []
    TL = TAILS[kind]
    for k, (p1_, p2_, p3_, wm) in enumerate(TL):
        cvt = lambda q: root + back_dir * q[0] * p1u + dn * q[1] * p1u
        d_, C_ = lock_d(root, cvt(p1_), cvt(p2_), cvt(p3_), wm * p1u, w0=0.11 * p1u)
        tparts.append(path(d_, pal['mane'] if k == len(TL) - 1 else pal['maneD']))
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{Hh}" viewBox="0 0 {W} {Hh}">' + ''.join(extra.get('back', []) + tparts) + '</svg>'
    pm = svg_rgba(svg, W3, H3)
    ta = pm[..., 3]
    trgb = np.where(ta[..., None] > 1e-4, pm[..., :3] / np.maximum(ta, 1e-4)[..., None], 0)
    col = col * A[..., None] + trgb * (ta * (1 - A))[..., None]
    A = A + ta * (1 - A)
    col = col / np.maximum(A[..., None], 1e-4)

    # ---------------- 1倍へ ----------------
    pre = cv2.resize(col * A[..., None], (W, Hh), interpolation=cv2.INTER_AREA)
    A1 = cv2.resize(A, (W, Hh), interpolation=cv2.INTER_AREA)
    rgb1 = np.clip(pre / np.maximum(A1[..., None], 1e-4), 0, 1)
    return rgb1, A1, marks
