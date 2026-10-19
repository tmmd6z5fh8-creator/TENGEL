"""アニメ塗りの競走馬と騎手（ナイター用）
   3Dの馬（horse3d）と騎手の形を 3倍の大きさで描き、アニメの塗り（くっきりした影の段・毛並みのつや・ふちの光）と
   線（外がわは太く、重なりと部分のさかい目は細く・線の色は塗りの色に寄せる）にしてから縮める。
   ゼッケン・腹帯・足先の黒・白い靴下・騎手の顔とゴーグル・ブーツの折り返しは、3Dの位置で体に貼る（はみ出さない）。
   たてがみ・前髪・しっぽは、とがった房（影・つやの帯・1本ずつの線）。形はすべて一から作ったオリジナル"""
import sys, os, math
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from real_rider import *          # style2d（hexc・blur・over・flow・world_pos・frame_horse・soft_circle・TMP）・h3d・horse3d（Hm）・素材の番号

JOCKEY = (M_SILK, M_PANTS, M_HELMET, M_BOOT, M_SLEEVE)
HORSE = (M_COAT, M_EYE, M_HOOF)
HEAD_REF = 53.5                   # いちばん手前の馬の頭の長さ（1倍の画素）：たてがみ・線の大きさの基準

# ---------- 色（明るい・影・深い影・つや） ----------
COATS = {
    'bay': ('#A4532A', '#5E2A2C', '#35161C', '#F2A673'),
    'darkbay': ('#6C3322', '#3A1B20', '#1F0E14', '#C88462'),
    'chestnut': ('#C4682F', '#76392C', '#43201C', '#FFC48E'),
}
SILKS = {
    'red': ('#F23A4E', '#A31F3A', '#6A1228', '#FFB4BC'),
    'white': ('#F6F8FF', '#B0B6DC', '#848CB8', '#FFFFFF'),
    'green': ('#22B65E', '#0E7342', '#084828', '#A4F2C4'),
    'yellow': ('#FFD844', '#D0981E', '#8C6410', '#FFF6BC'),
    'blue': ('#4064E8', '#23349C', '#141F60', '#AEC0FF'),
}
PAL = {
    'leg': ('#3A2C3E', '#1E1526', '#110B17', '#8E8AB6'),
    'sock': ('#F2F2FC', '#ABAED0', '#7E80AA', '#FFFFFF'),
    'hoof': ('#3E3644', '#201A26', '#120E16', '#8C88A4'),
    'pants': ('#F4F6FF', '#B2B8DC', '#848CB6', '#FFFFFF'),
    'boot': ('#2C2C3A', '#17171F', '#0B0B11', '#8A90BA'),
    'cuff': ('#D49A64', '#94603E', '#603A24', '#FFD8A8'),
    'cloth': ('#F6F8FF', '#B9BFE2', '#8C93BC', '#FFFFFF'),
    'girth': ('#3A3A4A', '#202030', '#121220', '#9A9CC0'),
    'saddle': ('#3C2A2C', '#22161C', '#140C12', '#A08AA0'),
    'skin': ('#F8D6B8', '#DCA48C', '#B07A6A', '#FFF0E0'),
    'goggle': ('#2A3050', '#1A1E36', '#0E1020', '#B4E0FF'),
    'hair': ('#3A3448', '#211B2C', '#100C16', '#A4A2D2'),
    'hair_back': ('#272233', '#16121E', '#0A080E', '#6E6C98'),
    'hair_chestnut': ('#94442A', '#5E2618', '#36140C', '#F0A070'),
    'hair_chestnut_back': ('#6E2E1C', '#461C12', '#280E08', '#B86E4C'),
}
LINE = hexc('#1A1024')
RIM = hexc('#E4EEFF')


def ss_(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def jockey_a(sc, S, js=1.12, side_z=0.30):
    """前かがみの騎手（右向きの馬の上）。ゼッケンは3Dで作らず、体に貼る"""
    w = np.asarray(S['withers'], float)
    P3 = lambda y=0.0, x=0.0, z=0.0: np.array([w[0] + x * js, w[1] + y * js, z * js], float)
    J = {}
    J['pelvis'] = P3(0.24, -0.30); J['chest'] = P3(0.33, 0.06); J['neck'] = P3(0.37, 0.15); J['head'] = P3(0.45, 0.24)
    a, b = J['pelvis'], J['chest']
    sc.ell_ax((a + b) / 2, b - a, (np.linalg.norm(b - a) / 2 + 0.07 * js, 0.12 * js, 0.15 * js), up=(0, 1, 0), k=0.04, mat=M_SILK)
    sc.ell(a + np.array([0.02, -0.02, 0]) * js, (0.13 * js, 0.10 * js, 0.15 * js), k=0.05, mat=M_PANTS)
    sc.rcone(J['chest'], J['neck'], 0.07 * js, 0.05 * js, k=0.03, mat=M_SILK)
    sc.sph(J['head'], 0.095 * js, k=0.02, mat=M_HELMET)
    sc.ell(J['head'] + np.array([0.085, -0.03, 0]) * js, (0.05 * js, 0.012 * js, 0.07 * js), k=0.01, mat=M_HELMET)
    for z in (1, -1):
        sh = P3(0.34, 0.06, 0.13 * z); el = P3(0.18, 0.10, 0.21 * z); hd = P3(0.06, 0.36, 0.10 * z)
        sc.rcone(sh, el, 0.05 * js, 0.042 * js, k=0.02, mat=M_SLEEVE)
        sc.rcone(el, hd, 0.04 * js, 0.032 * js, k=0.02, mat=M_SLEEVE)
        sc.sph(hd, 0.035 * js, k=0.01, mat=M_PANTS)
        hip = P3(0.22, -0.26, 0.12 * z); kn = P3(0.14, 0.02, side_z * z)
        an = P3(-0.18, -0.18, (side_z + 0.06) * z); toe = P3(-0.22, -0.06, (side_z + 0.07) * z)
        sc.rcone(hip, kn, 0.075 * js, 0.055 * js, k=0.03, mat=M_PANTS)
        sc.rcone(kn, an, 0.052 * js, 0.04 * js, k=0.02, mat=M_BOOT)
        sc.rcone(an, toe, 0.04 * js, 0.03 * js, k=0.01, mat=M_BOOT)
        J[f'hand{z}'] = hd; J[f'knee{z}'] = kn; J[f'ankle{z}'] = an
    J['js'] = js
    return J


def jockey_win(sc, S, js=1.12, side_z=0.30, side=1.0):
    """表彰の騎手：体を起こして、手前の手を高く上げる（ガッツポーズ）。手綱は奥の手。ゼッケンは体に貼る"""
    w = np.asarray(S['withers'], float)
    P3 = lambda y=0.0, x=0.0, z=0.0: np.array([w[0] + x * js, w[1] + y * js, z * js], float)
    J = {}
    J['pelvis'] = P3(0.24, -0.32); J['chest'] = P3(0.56, -0.22); J['neck'] = P3(0.64, -0.19); J['head'] = P3(0.74, -0.15)
    a, b = J['pelvis'], J['chest']
    sc.ell_ax((a + b) / 2, b - a, (np.linalg.norm(b - a) / 2 + 0.07 * js, 0.12 * js, 0.15 * js), up=(1, 0, 0), k=0.04, mat=M_SILK)
    sc.ell(a + np.array([0.0, -0.02, 0]) * js, (0.13 * js, 0.10 * js, 0.15 * js), k=0.05, mat=M_PANTS)
    sc.rcone(J['chest'], J['neck'], 0.07 * js, 0.05 * js, k=0.03, mat=M_SILK)
    sc.sph(J['head'], 0.095 * js, k=0.02, mat=M_HELMET)
    sc.ell(J['head'] + np.array([0.085, -0.03, 0]) * js, (0.05 * js, 0.012 * js, 0.07 * js), k=0.01, mat=M_HELMET)
    for z in (1, -1):
        up = z == side                                                   # 手前の手を上げる
        sh = P3(0.53, -0.20, 0.13 * z)
        el, hd = (P3(0.70, -0.06, 0.22 * z), P3(0.93, -0.02, 0.17 * z)) if up else (P3(0.38, -0.10, 0.21 * z), P3(0.30, 0.18, 0.12 * z))
        sc.rcone(sh, el, 0.05 * js, 0.042 * js, k=0.02, mat=M_SLEEVE)
        sc.rcone(el, hd, 0.04 * js, 0.032 * js, k=0.02, mat=M_SLEEVE)
        sc.sph(hd, (0.045 if up else 0.035) * js, k=0.01, mat=M_PANTS)
        hip = P3(0.22, -0.26, 0.12 * z); kn = P3(0.14, 0.02, side_z * z)
        an = P3(-0.18, -0.18, (side_z + 0.06) * z); toe = P3(-0.22, -0.06, (side_z + 0.07) * z)
        sc.rcone(hip, kn, 0.075 * js, 0.055 * js, k=0.03, mat=M_PANTS)
        sc.rcone(kn, an, 0.052 * js, 0.04 * js, k=0.02, mat=M_BOOT)
        sc.rcone(an, toe, 0.04 * js, 0.03 * js, k=0.01, mat=M_BOOT)
        J[f'hand{z}'] = hd; J[f'knee{z}'] = kn; J[f'ankle{z}'] = an
        if not up:
            J['rein'] = hd
        else:
            J['fist'] = hd
    J['js'] = js
    return J

def render_anime(pose, box, W, Hh, s=3, azim=12, elev=4, name='anime', head_scale=1.06, fov=26, js=1.12,
                 key=(0.30, 0.80, 0.55), cam=None, jockey=None):
    """3倍の大きさで形を描く（光は1つ・影つき・白い素材）。rgb は「光の当たり具合（影をふくむ）」になる。
       cam：決めたカメラ (目, 見る所)（走るコマで、どのコマも同じカメラにするとき）。なければ box に入るように決める（R['cam'] に入れて返す）
       jockey：'win' なら 表彰の騎手（体を起こして 手前の手を上げる・jockey_win）"""
    Hm.HEAD_SCALE = head_scale
    W3, H3 = W * s, Hh * s
    e, t = cam if cam is not None else frame_horse(pose, tuple(v * s for v in box), W3, H3, facing='right', azim=azim, elev=elev, fov=fov)
    sc = Scene()
    sc.image(W3, H3, 1)
    sc.camera(e, t, fov)
    sc.bounce(0)
    cam = nrm(np.asarray(e, float) - np.asarray(t, float))
    side = 1.0 if cam[2] >= 0 else -1.0
    sc.env((0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0))
    Lk = nrm((key[0], key[1], key[2] * side))
    sc.light(Lk, (1.0, 1.0, 1.0), 18, 1)
    for mid in HORSE + JOCKEY:
        sc.mat(mid, 1, (1.0, 1.0, 1.0), 1.0, 0.0, 0.0, 0.0)
    # しっぽの根元の3Dの出っぱり（背中の上）は作らない：しっぽはお尻のいちばんうしろから2Dの房で出す
    S0 = Hm.skeleton(pose)
    ta0 = Hm.v3(S0['tailhead']); t10 = Hm.v3(S0['tailhead'] + Hm.adir(pose['tail'][0]) * 0.20)
    rcone0 = sc.rcone
    def rcone_no_dock(a, b, *args, **kw):
        if np.allclose(np.asarray(a, float), ta0) or np.allclose(np.asarray(a, float), t10):
            return
        return rcone0(a, b, *args, **kw)
    sc.rcone = rcone_no_dock
    S = Hm.build(sc, pose, mats=dict(body=M_COAT, neck=M_COAT, hoof=M_HOOF, eye=M_EYE, head=M_COAT))
    sc.rcone = rcone0
    J = jockey_win(sc, S, js, side=side) if jockey == 'win' else jockey_a(sc, S, js)
    R = sc.render(os.path.join(TMP, name))
    ts = np.linspace(0, 1, 40)
    P = lambda pts: sc.project(np.asarray(pts, float))[0]
    R['crest'] = P(np.c_[Hm.bez(S['crest'], ts), np.zeros(len(ts))])
    R['poll'] = P([Hm.v3(S['poll'])])[0]
    R['muzzle'] = P([Hm.head_pt(S, 0.56, -0.03)])[0]
    R['mouth'] = P([Hm.head_pt(S, 0.50, -0.10, 0.06 * side)])[0]
    R['nostril'] = P([Hm.head_pt(S, 0.535, 0.022, 0.055 * side)])[0]
    R['tail'] = P([Hm.v3(p) for p in S['tail_pts']])
    e0, e1 = S['eyes']
    R['eye'] = P([e0 if np.dot(e0 - t, np.asarray(e, float) - t) > np.dot(e1 - t, np.asarray(e, float) - t) else e1])[0]
    R['hooves'] = P([Hm.v3(S[k]['hf'], 0.15 * S[k]['z']) for k in ('FL', 'FR', 'HL', 'HR')])
    R['hand_near'] = P([J['rein'] if 'rein' in J else (J['hand1'] if side > 0 else J['hand-1'])])[0]
    if 'fist' in J:
        R['fist'] = P([J['fist']])[0]
    R['S'], R['scene'], R['J'], R['side'], R['Lk'], R['s'] = S, sc, J, side, Lk, s
    R['cam'] = (e, t)
    return R


def _dist_line(mask, w_in, w_out):
    """形のふちの線（内がわ w_in・外がわ w_out の太さ、なめらか）"""
    m = (mask > 0.5).astype(np.uint8)
    din = cv2.distanceTransform(m, cv2.DIST_L2, 5)
    dout = cv2.distanceTransform(1 - m, cv2.DIST_L2, 5)
    return np.where(m > 0, np.clip(w_in + 0.5 - din, 0, 1), np.clip(w_out + 0.5 - dout, 0, 1)).astype(np.float32)


def _thick(seed_mask, w):
    """1画素の線 → 太さ w（半分）のなめらかな線"""
    d = cv2.distanceTransform((seed_mask < 0.5).astype(np.uint8), cv2.DIST_L2, 5)
    return np.clip(w + 0.5 - d, 0, 1).astype(np.float32)


def _gsmooth(x, groups, sig):
    """馬・騎手それぞれの中だけでぼかす（となりの色や向きがまざらない）"""
    out = np.zeros_like(x)
    for g in groups:
        gm = g.astype(np.float32)
        if x.ndim == 3:
            v = blur(x * gm[..., None], sig) / np.maximum(blur(gm, sig), 1e-4)[..., None]
            out = np.where(g[..., None], v, out)
        else:
            v = blur(x * gm, sig) / np.maximum(blur(gm, sig), 1e-4)
            out = np.where(g, v, out)
    return out


def fill_poly(shape, polys):
    m = np.zeros(shape, np.uint8)
    for p in polys:
        cv2.fillPoly(m, [np.round(np.asarray(p) * 16).astype(np.int32)], 255, cv2.LINE_AA, shift=4)
    return m.astype(np.float32) / 255.0


def draw_lock(col, alpha, pts, w0, pal, lw, tip=0.9, hi=(0.14, 0.55), leaf=False):
    """1本の房：明るい色 → 下がわの影 → 上がわのつやの帯 → 線（leaf=True：根元も細い葉の形）"""
    shape = alpha.shape
    P_ = np.asarray(pts, float)
    tg = np.gradient(P_, axis=0)
    tg /= np.linalg.norm(tg, axis=1, keepdims=True) + 1e-9
    nr = np.stack([-tg[:, 1], tg[:, 0]], 1)
    t = np.linspace(0, 1, len(P_))
    if leaf:
        w = w0 * (0.50 + 0.50 * np.sin(np.pi / 2 * np.clip(t / 0.35, 0, 1))) * (1 - t) ** tip / 2 + 0.3
    else:
        w = w0 * (1 - t) ** tip * (0.80 + 0.20 * np.sin(np.pi * t)) / 2 + 0.3
    up = nr if np.mean(nr[:, 1]) < 0 else -nr                         # 上がわ（画面の上）へのむき
    cap = [P_[0] + (up[0] * math.cos(a_) - tg[0] * math.sin(a_)) * w[0] for a_ in np.linspace(0, math.pi, 9)[1:-1]]
    poly = np.vstack([P_ + up * w[:, None], (P_ - up * w[:, None])[::-1], np.array(cap)[::-1]])     # 根元は丸く
    m = fill_poly(shape, [poly])
    shade = fill_poly(shape, [np.vstack([P_ - up * (w * 0.05)[:, None], (P_ - up * w[:, None])[::-1]])]) * m
    i0 = int(len(P_) * hi[0]); i1 = max(i0 + 3, int(len(P_) * hi[1]))
    q = P_[i0:i1]; uq = up[i0:i1]; wq = w[i0:i1]
    tt = np.linspace(0, 1, len(q))
    hw = wq * 0.30 * np.sin(np.pi * tt) ** 0.7
    c = q + uq * (wq * 0.42)[:, None]
    hl = fill_poly(shape, [np.vstack([c + uq * hw[:, None], (c - uq * hw[:, None])[::-1]])]) * m
    b, s1, s2, h = (hexc(x) for x in pal)
    col = over(col, b, m)
    col = over(col, s1, shade * 0.95)
    col = over(col, h, hl * 0.85)
    ol = np.zeros(shape, np.uint8)
    cv2.polylines(ol, [np.round(poly * 16).astype(np.int32)], True, 255, max(1, int(round(lw))), cv2.LINE_AA, shift=4)
    ol = ol.astype(np.float32) / 255
    col = over(col, LINE, ol)
    return col, np.maximum(alpha, np.maximum(m, ol))


def paint_anime(R, look, debug=None):
    """look: coat・legs（'black'／'socks'）・silk・sleeve・helmet・num・seed・tail・mane・lw（線の太さの倍率）・roll（白い鼻革）・hair_phase（たてがみ・しっぽの波の位相）・hair_wind（なびく強さの倍率）・hair_drop（0：うしろへ なびく 〜 1：下へ たれる）
       戻り値：1倍の (rgb, alpha)"""
    s = R['s']
    a = np.clip(R['a'], 0, 1)
    inside = a > 0.5
    H3, W3 = a.shape
    m = np.round(R['m']).astype(int) * inside
    n = R['n']
    d = R['d']
    side = R['side']
    Lk = R['Lk']
    e_, t_ = R['scene'].cam[0], R['scene'].cam[1]
    V = nrm(np.asarray(e_, float) - np.asarray(t_, float))
    Lb = nrm((-0.45, 0.50, -0.75 * side))
    horse = np.isin(m, HORSE) & inside
    jock = np.isin(m, JOCKEY) & inside
    groups = (horse, jock)
    lt = np.clip(R['rgb'].mean(-1) / 0.318, 0, 1.3)
    P = world_pos(R)
    Pn = np.nan_to_num(P, nan=99.0)
    S, J = R['S'], R['J']
    js = J['js']
    lw = look.get('lw', 1.0)
    hl_ = np.linalg.norm(np.asarray(R['muzzle']) - np.asarray(R['poll']))
    u1 = hl_ / HEAD_REF                                                  # 1倍の基準の1画素 → この馬の3倍の画素

    def segd(p0, p1):
        dd = p1 - p0
        tt = np.clip(np.sum((Pn - p0) * dd, -1) / np.dot(dd, dd), 0, 1)
        return np.linalg.norm(Pn - (p0 + tt[..., None] * dd), axis=-1), tt
    # 頭は小さな形が多いので、光と向きを大きめにならす（まだらを消す）
    head = (segd(Hm.v3(S['poll']), Hm.head_pt(S, 0.56, -0.03))[0] < 0.20 * Hm.HEAD_SCALE) & horse
    lts = np.where(head, _gsmooth(lt, groups, 2.6 * s), _gsmooth(lt, groups, 1.0 * s))
    ns = np.where(head[..., None], _gsmooth(n, groups, 3.4 * s), _gsmooth(n, groups, 1.6 * s))
    ns = ns / (np.linalg.norm(ns, axis=-1, keepdims=True) + 1e-6)
    Hv = nrm(Lk + V)
    spec = np.sum(ns * Hv, -1)
    nl = np.sum(ns * Lk, -1)
    ao = _gsmooth(R['ao'], groups, 1.5 * s)
    # ふちの光：外の形と、重なりの手前がわのふちに、同じ太さの帯（うしろ上からの光が当たる向きだけ）
    big0 = np.where(inside, d, 1e3)
    farside = np.zeros(m.shape, bool)
    for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)):
        nb = np.roll(np.roll(big0, dy, 0), dx, 1)
        farside |= inside & (big0 - nb > 0.06)
    seed = (~inside) | farside
    dseed = cv2.distanceTransform((~seed).astype(np.uint8), cv2.DIST_L2, 5)
    n1 = _gsmooth(n, groups, 0.7 * s)
    facing = np.sum(n1 * Lb, -1)
    rw = 2.0 * lw + 2.4 * u1
    rim = ss_(rw + 0.8, rw - 0.8, dseed) * (~seed) * ss_(0.02, 0.16, facing)
    # ---------- 部分（素材＋体に貼る部分） ----------
    part = np.full(m.shape, -1, int)
    part[m == M_COAT] = 0; part[m == M_EYE] = 1; part[m == M_HOOF] = 2
    for k, v in ((M_SILK, 10), (M_SLEEVE, 11), (M_HELMET, 12), (M_PANTS, 13), (M_BOOT, 14)):
        part[m == k] = v
    legd = np.full(m.shape, 9.0, np.float32)
    sock = np.zeros(m.shape, bool)
    for k, top in (('FL', 'kn'), ('FR', 'kn'), ('HL', 'hk'), ('HR', 'hk')):
        F = S[k]
        zl = 0.155 * F['z'] * 0.92
        q0 = np.array([*(np.asarray(F[top]) + (np.asarray(F['ft']) - np.asarray(F[top])) * 0.25), zl])
        q1 = np.array([*np.asarray(F['hf']), zl])
        dd = q1 - q0
        tt = np.clip(np.sum((Pn - q0) * dd, -1) / np.dot(dd, dd), 0, 1)
        dist = np.linalg.norm(Pn - (q0 + tt[..., None] * dd), axis=-1)
        legd = np.minimum(legd, dist)
        if k[0] == 'H':
            sock |= (dist < 0.12) & (tt > 0.45)
    if look.get('legs', 'black') == 'black':
        part[(part == 0) & (legd < 0.11)] = 3                           # 足先の黒
    else:
        part[(part == 0) & sock] = 4                                     # うしろ足の白い靴下
    w = np.asarray(S['withers'], float)
    zs = Pn[..., 2] * side
    cloth = (part == 0) & (Pn[..., 0] > w[0] - 0.56) & (Pn[..., 0] < w[0] - 0.08) & (Pn[..., 1] > w[1] - 0.50) & (zs > -0.05)
    part[cloth] = 5                                                      # ゼッケン（上は背中の線まで）
    saddle = (part == 5) & (Pn[..., 0] > w[0] - 0.47) & (Pn[..., 0] < w[0] - 0.15) & (Pn[..., 1] > w[1] - 0.115)
    part[saddle] = 7                                                     # 鞍
    girth = np.isin(part, (0, 5)) & (Pn[..., 0] > w[0] - 0.21) & (Pn[..., 0] < w[0] - 0.15) & (Pn[..., 1] < w[1] - 0.20) & (Pn[..., 1] > w[1] - 0.80)
    part[girth] = 6                                                      # 腹帯
    hc = J['head']
    q = Pn - hc
    front = (part == 12) & (q[..., 0] > -0.01 * js) & (q[..., 1] < -0.042 * js)
    part[front & (q[..., 1] > -0.074 * js)] = 16                         # ゴーグル
    part[front & (q[..., 1] <= -0.074 * js)] = 15                        # 顔
    for z in (1, -1):
        kn = J[f'knee{z}']
        part[(part == 14) & (np.linalg.norm(Pn - kn, axis=-1) < 0.075 * js)] = 17     # ブーツの折り返し

    pals = {0: COATS[look['coat']], 1: PAL['hair'], 2: PAL['hoof'], 3: PAL['leg'], 4: PAL['sock'], 5: PAL['cloth'], 6: PAL['girth'], 7: PAL['saddle'],
            8: PAL['hair_chestnut'] if look['coat'] == 'chestnut' else PAL['hair'],
            10: SILKS[look['silk']], 11: SILKS[look['sleeve']], 12: SILKS[look['helmet']], 13: PAL['pants'], 14: PAL['boot'],
            15: PAL['skin'], 16: PAL['goggle'], 17: PAL['cuff']}
    # 部分ごとの段：影のしきい・つやのしきい・ふちの光の強さ
    thr = {0: (0.24, 0.93, 0.85), 1: (0.0, 2.0, 0.0), 2: (0.24, 0.96, 0.3), 3: (0.24, 0.95, 0.5), 4: (0.24, 2.0, 0.5),
           5: (0.20, 2.0, 0.35), 6: (0.24, 0.97, 0.4), 7: (0.22, 0.95, 0.5), 8: (0.22, 0.95, 0.6), 10: (0.22, 0.90, 0.5), 11: (0.22, 0.90, 0.5), 12: (0.22, 0.94, 0.6),
           13: (0.20, 0.97, 0.35), 14: (0.22, 0.93, 0.55), 15: (0.18, 2.0, 0.3), 16: (0.20, 0.90, 0.3), 17: (0.22, 0.95, 0.4)}
    col = np.zeros((H3, W3, 3), np.float32)
    for pid, pal in pals.items():
        reg = part == pid
        if not reg.any():
            continue
        b, s1, s2, hi = (hexc(x) for x in pal)
        t_sh, t_sp, rimk = thr[pid]
        shd = ss_(t_sh + 0.025, t_sh - 0.025, lts)
        c = b * (1 - shd[..., None]) + s1 * shd[..., None]
        deep = np.maximum(ss_(-0.40, -0.48, nl), ss_(0.56, 0.48, ao)) * shd
        c = c * (1 - deep[..., None] * 0.85) + s2 * deep[..., None] * 0.85
        h = ss_(t_sp - 0.006, t_sp + 0.006, spec) * (1 - shd)
        c = c * (1 - h[..., None] * 0.9) + hi * h[..., None] * 0.9
        h2 = ss_(1 - (1 - t_sp) * 0.22 - 0.003, 1 - (1 - t_sp) * 0.22 + 0.003, spec) * (1 - shd)       # いちばん明るい つや
        c = c * (1 - h2[..., None] * 0.75) + (hi * 0.4 + 0.6) * h2[..., None] * 0.75
        c = c * (1 - rim[..., None] * rimk) + RIM * rim[..., None] * rimk
        col = np.where(reg[..., None], c, col)
    if debug is not None:
        debug['part'] = part; debug['lts'] = lts; debug['spec'] = spec; debug['rim'] = rim; debug['u1'] = u1

    # ---------- 線 ----------
    sil = _dist_line(inside.astype(np.float32), 2.0 * lw, 2.2 * lw)
    big = np.where(inside, d, 1e3)
    near = np.zeros(m.shape, bool)
    bound = np.zeros(m.shape, bool)
    soft = (0, 3, 4)                                                     # 毛の色のさかい（線なし）
    for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        nb = np.roll(np.roll(big, dy, 0), dx, 1)
        pnb = np.roll(np.roll(part, dy, 0), dx, 1)
        near |= inside & (nb - big > 0.06) & (nb < 1e3)
        diffp = (pnb != part) & inside & (nb < 1e3) & ~(np.isin(part, soft) & np.isin(pnb, soft))
        bound |= diffp & (big <= nb + 0.01)
    nx = np.sum(n * np.roll(n, -1, 1), -1); ny = np.sum(n * np.roll(n, -1, 0), -1)
    crease = ((nx < 0.70) | (ny < 0.70)) & inside
    inner = np.maximum(_thick(near.astype(np.float32), 1.25 * lw), _thick((bound | crease).astype(np.float32), 1.0 * lw))
    line = np.clip(np.maximum(sil, inner * inside), 0, 1)
    lc = np.where(inside[..., None], LINE * 0.62 + col * 0.17, LINE)     # 線の色：暗い紺に、塗りの色を少し
    col = col * (1 - line[..., None]) + lc * line[..., None]
    A = np.clip(np.maximum(a, line), 0, 1)

    # ---------- 目・鼻の穴 ----------
    ex, ey = R['eye']
    u = (np.asarray(R['muzzle']) - np.asarray(R['poll'])) / (hl_ + 1e-9)
    ang = math.degrees(math.atan2(u[1], u[0]))
    r = max(2.0, hl_ * 0.082)
    def ell(cx, cy, ax, ay, rot, a0=0, a1=360, th=-1):
        mm = np.zeros((H3, W3), np.uint8)
        cv2.ellipse(mm, (int(cx * 16), int(cy * 16)), (int(ax * 16), int(ay * 16)), rot, a0, a1, 255, th, cv2.LINE_AA, shift=4)
        return mm.astype(np.float32) / 255
    em = ell(ex, ey, r, r * 0.70, ang - 12) * horse
    col = over(col, hexc('#120A16'), em)
    col = over(col, hexc('#5A3A44'), ell(ex + 0.15 * r, ey + 0.25 * r, r * 0.55, r * 0.30, ang - 12) * em)
    col = over(col, hexc('#FFFFFF'), soft_circle(H3, W3, ex - 0.25 * r, ey - 0.30 * r, r * 0.30, 1.0) * em)
    col = over(col, LINE, ell(ex, ey + 0.1 * r, r * 1.15, r * 0.85, ang - 12, 195, 330, max(1, int(round(1.1 * s)))))
    nx_, ny_ = R['nostril']
    col = over(col, LINE, ell(nx_, ny_, r * 0.75, r * 0.35, ang - 60, 160, 340, max(1, int(round(0.9 * s)))) * horse)

    # ---------- ゼッケンの番号 ----------
    clm = part == 5
    if clm.any():
        from PIL import Image, ImageDraw, ImageFont
        ys, xs = np.nonzero(clm)
        cx, cy = np.median(xs), np.median(ys)
        size = int((np.percentile(ys, 95) - np.percentile(ys, 5)) * 0.66)
        F = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
        lay = Image.new('L', (W3, H3), 0)
        ImageDraw.Draw(lay).text((cx, cy), str(look['num']), font=ImageFont.truetype(F, max(8, size)), fill=255, anchor='mm')
        col = over(col, hexc('#141022'), np.asarray(lay).astype(np.float32) / 255 * clm)

    # ---------- たてがみ・前髪・しっぽ（房） ----------
    rng = np.random.default_rng(look.get('seed', 1))
    hph = look.get('hair_phase', 0.0)                                   # たてがみ・しっぽの波の位相（走るコマで なびかせる）
    hwk = look.get('hair_wind', 1.0)                                    # なびく強さ（止まる馬は弱く）
    hdrop = look.get('hair_drop', 0.0)                                  # 0：うしろへ なびく 〜 1：下へ たれる（止まった馬）
    wang = lambda a_: (1 - hdrop) * a_ + hdrop * (math.pi / 2 + 0.45)
    hlw = max(1.0, s * lw)
    crest = np.asarray(R['crest'], float)
    nC = len(crest)
    pp, mz = np.asarray(R['poll'], float), np.asarray(R['muzzle'], float)
    fd = (mz - pp) / np.linalg.norm(mz - pp)
    mane_k = look.get('mane', 1.0)
    hpal = PAL['hair_chestnut'] if look['coat'] == 'chestnut' else PAL['hair']
    hpal_b = PAL['hair_chestnut_back'] if look['coat'] == 'chestnut' else PAL['hair_back']

    def crest_dir(i):
        tg = crest[min(i + 1, nC - 1)] - crest[max(i - 1, 0)]
        upa = math.atan2(tg[1], tg[0]) - math.pi / 2
        if math.cos(upa) > 0.3:
            upa += math.pi
        return upa
    # うしろの列（首の向こうがわ：体のうしろに描く）
    back = []
    for i in range(10, nC - 3, 5):
        upa = crest_dir(i)
        L = (32 + 12 * math.sin(i / nC * math.pi) + rng.uniform(-4, 5)) * u1 * mane_k
        pts = flow(crest[i] + np.array([0.0, 2.0 * u1]), upa - 0.30 + rng.uniform(-0.12, 0.12), L, 16, wind=0.20 * hwk,
                   wind_ang=wang(math.pi + 0.40), curl=0.025, rng=rng, wave=1.2, phase=i * 0.5 + hph)
        back.append((pts, (12.0 + rng.uniform(-1, 1.5)) * u1))
    bcol = np.zeros((H3, W3, 3), np.float32); ba = np.zeros((H3, W3), np.float32)
    for pts, w0 in back:
        bcol, ba = draw_lock(bcol, ba, pts, w0, hpal_b, hlw, leaf=True)
    # 手前の列（首の上にかかる）・前髪
    front = []
    for i in range(8, nC - 3, 4):
        upa = crest_dir(i)
        root = crest[i] - np.array([math.cos(upa), math.sin(upa)]) * 2.0 * u1        # 首の中から
        L = (28 + 14 * math.sin(i / nC * math.pi) + rng.uniform(-4, 4)) * u1 * mane_k
        pts = flow(root, upa - 0.62 + rng.uniform(-0.12, 0.12), L, 16, wind=0.22 * hwk, wind_ang=wang(math.pi + 0.30), curl=0.03,
                   rng=rng, wave=1.3, phase=i * 0.7 + hph)
        front.append((pts, (12.0 + rng.uniform(-1, 1.5)) * u1))
    for k in range(2):
        a0 = math.atan2(-fd[1], -fd[0]) - 0.55 - 0.25 * k
        pts = flow(pp + fd * (3.0 + 2.5 * k) * u1, a0, (15 - 3 * k) * u1 * mane_k, 10, wind=0.18 * hwk, wind_ang=wang(math.pi + 0.35),
                   curl=0.03, rng=rng, wave=0.6, phase=k + hph)
        front.append((pts, (6.5 - k) * u1))
    hcol = np.zeros((H3, W3, 3), np.float32); ha = np.zeros((H3, W3), np.float32)
    for pts, w0 in front:
        hcol, ha = draw_lock(hcol, ha, pts, w0, hpal, hlw, leaf=True)
    # しっぽ：お尻のいちばんうしろ（上がわ・背中の線が下がりきって、うしろのふちが立ち上がる所）から出して、うしろへなびかせる
    tp = np.asarray(R['tail'], float)
    tdir = math.atan2(*(tp[-1] - tp[0])[::-1])                           # 3Dのしっぽの向き（ポーズの角度）
    Pj = lambda p3: R['scene'].project(np.asarray([p3], float))[0][0][:2]
    cr2, bt2 = Pj(Hm.v3(S['croup'])), Pj(Hm.v3(S['buttock']))
    ys_, xs_ = np.nonzero(np.isin(part, (0, 3, 4, 5, 6, 7)))
    sel = (ys_ > cr2[1] - 10 * u1) & (ys_ < bt2[1] + 10 * u1) & (xs_ < cr2[0])
    k_ = np.argmin(xs_[sel] * 0.9 + ys_[sel] * 0.44)
    tin = look.get('tail_in', 3.0)
    troot = np.array([xs_[sel][k_], ys_[sel][k_]], float) + np.array([tin, -2.0]) * u1     # 体の中から（ふちのうしろから出る）
    R['tail_root'] = troot
    tl = []
    t_ang = look.get('tail_ang')                  # 画面の上での向き（度・0＝右・90＝下）を決めるとき（まさちゃんの赤線など）
    for k in range(7):
        root = troot + np.array([rng.normal(0, 0.5), (k - 3) * 0.9]) * u1
        if t_ang is None:
            ang0 = tdir + (k - 3) * 0.07 + 0.10 + rng.uniform(-0.05, 0.05)
            wind_t, wang_t, curl_t = 0.08 * hwk, wang(math.pi + 0.10), 0.006 * (1 if k % 2 else -1)
        else:
            ang0 = math.radians(t_ang) + (k - 3) * look.get('tail_spread', 0.07) + rng.uniform(-0.05, 0.05)
            wind_t, wang_t, curl_t = 0.0, math.pi, look.get('tail_curl', 0.0)
        L = (58 + rng.uniform(-6, 10) - abs(k - 3) * 3) * u1 * look.get('tail', 1.0)
        if t_ang is not None:                     # 下へ流れる房ほど長く、上の房は短く（扇のように広がる）
            L = L / (58 + 2 - abs(k - 3) * 3) * 60 * look.get('tail_prof', (1.0, 1.0, 0.98, 0.95, 0.88, 0.80, 0.72))[k]
        pts = flow(root, ang0, L, 20, wind=wind_t, wind_ang=wang_t, curl=curl_t, rng=rng, wave=look.get('tail_wave', 1.8), phase=k * 0.9 + hph)
        tl.append((pts, (look.get('tail_w', 15.0) - abs(k - 3) * 1.2) * u1))
    tl.sort(key=lambda x: -x[0][-1][1])                                    # 下の房から
    R['tail_ends'] = [pts[-1] / s for pts, _ in tl]
    for pts, w0 in tl:                                                    # しっぽは体のうしろ（お尻のふちの線が前に来る）
        if look.get('tail_over'):
            hcol, ha = draw_lock(hcol, ha, pts, w0, hpal, hlw, tip=0.8, hi=(0.10, 0.50), leaf=True)
        else:
            bcol, ba = draw_lock(bcol, ba, pts, w0, hpal, hlw, tip=0.8, hi=(0.10, 0.50))
    # 毛のふちの光（うしろ上からの光）：暗い空の前でも、たてがみ・しっぽの形が見えるように
    def hair_rim(c_, al_, k=0.5):
        U = (al_ > 0.5).astype(np.float32)
        d_ = np.array([-0.67, -0.74])
        def sh(dist):
            M_ = np.float32([[1, 0, -d_[0] * dist], [0, 1, -d_[1] * dist]])
            return cv2.warpAffine(U, M_, (U.shape[1], U.shape[0]), flags=cv2.INTER_LINEAR, borderValue=0)
        rb = U * ss_(0.4, 0.6, sh(0.9 * hlw + 0.5)) * (1 - ss_(0.4, 0.6, sh(0.9 * hlw + 0.5 + 1.3 * u1)))
        return c_ * (1 - rb[..., None] * k) + RIM * rb[..., None] * k
    hcol = hair_rim(hcol, ha)
    bcol = hair_rim(bcol, ba)
    # 重ね：うしろの列としっぽは体のうしろ、手前の列は体の前（騎手の前には出さない）
    jm = np.clip(np.maximum(jock.astype(np.float32), _dist_line(jock.astype(np.float32), 0, 2.2 * lw)) * 1.5, 0, 1)
    ha = ha * (1 - jm)
    col = col * (1 - ha[..., None]) + hcol * ha[..., None]
    A = np.maximum(A, ha)
    col = col * A[..., None] + bcol * (ba * (1 - A))[..., None]
    A = A + ba * (1 - A)
    col = col / np.maximum(A[..., None], 1e-4)

    # ---------- 頭のベルト・手綱 ----------
    tack = np.zeros((H3, W3), np.uint8)
    mo, ey_ = np.asarray(R['mouth'], float), np.asarray(R['eye'], float)
    perp = np.array([-fd[1], fd[0]])                                     # あごの方向
    nose = mz + (ey_ - mz) * 0.30
    def L3(img, pts, wd, closed=False):
        cv2.polylines(img, [np.round(np.asarray(pts) * 16).astype(np.int32)], closed, 255, max(1, int(round(wd))), cv2.LINE_AA, shift=4)
    if look.get('roll'):
        roll = np.zeros((H3, W3), np.uint8)
        L3(roll, [nose + perp * 6.0 * u1, nose - perp * 5.5 * u1], 4.4 * u1)
    else:
        L3(tack, [nose + perp * 5.5 * u1, nose - perp * 5.0 * u1], 1.7 * u1)            # 鼻のベルト
    top = pp + fd * 1.0 * u1 + perp * 1.0 * u1
    L3(tack, [top, (mo + top) / 2 + perp * 2.0 * u1, mo], 1.4 * u1)                      # ほおのベルト
    L3(tack, [pp + fd * 3.2 * u1 + perp * 0.5 * u1, pp + fd * 4.5 * u1 - perp * 4.5 * u1], 1.4 * u1)   # ひたいのベルト
    hand = np.asarray(R['hand_near'], float)
    mid = (mo + hand) / 2 + np.array([0.0, 4.0 * u1])
    L3(tack, [(1 - v_) ** 2 * mo + 2 * (1 - v_) * v_ * mid + v_ ** 2 * hand for v_ in np.linspace(0, 1, 18)], 1.3 * u1)   # 手綱
    tk = tack.astype(np.float32) / 255
    col = over(col, hexc('#22161E'), tk)
    A = np.maximum(A, tk)
    ring = np.zeros((H3, W3), np.uint8)
    cv2.circle(ring, (int(mo[0] * 16), int(mo[1] * 16)), int(1.8 * u1 * 16), 255, max(1, int(round(0.9 * u1))), cv2.LINE_AA, shift=4)
    col = over(col, hexc('#DADCF0'), ring.astype(np.float32) / 255)                  # はみの輪
    if look.get('roll'):
        rl = roll.astype(np.float32) / 255
        col = over(col, hexc('#F4F4FF'), rl)
        col = over(col, hexc('#B4B8DA'), rl * ss_(0.0, 1.0, _dist_line(rl, 9, 0) * 0) )
        col = over(col, LINE, _dist_line(rl, 1.0 * lw, 1.0 * lw) * (1 - ss_(0.6, 1.0, rl)))
        A = np.maximum(A, rl)

    if debug is not None:
        debug['col3'] = col.copy(); debug['A3'] = A.copy()
    # ---------- 1倍へ（色×不透明度で縮めて、ふちをなめらかに） ----------
    W1, H1 = W3 // s, H3 // s
    pre = cv2.resize(col * A[..., None], (W1, H1), interpolation=cv2.INTER_AREA)
    A1 = cv2.resize(A, (W1, H1), interpolation=cv2.INTER_AREA)
    rgb1 = pre / np.maximum(A1[..., None], 1e-4)
    return np.clip(rgb1, 0, 1), np.clip(A1, 0, 1)


if __name__ == '__main__':
    W, Hh = 780, 320
    pose = dict(theta=0.0, neck_rot=-36.0, head_ang=-32.0, fore=dict(L=[-100, -40, -30, -18], R=[-132, -28, -150, -170]),
                hind=dict(L=[-112, -152, -136, -156], R=[-56, -106, -76, -56]), tail=[-170, -158])
    R = render_anime(pose, (256, 104, 556, 300), W, Hh, name='animetest')
    dbg = {}
    rgb, a = paint_anime(R, dict(coat='bay', silk='red', sleeve='white', helmet='red', num=7, seed=7, tail=0.72), debug=dbg)
    print('u1', dbg['u1'], 'head', np.linalg.norm(np.asarray(R['muzzle']) - np.asarray(R['poll'])) / 3)
    bg = np.zeros((Hh, W, 3), np.float32) + hexc('#3A3050')
    out = bg * (1 - a[..., None]) + rgb * a[..., None]
    cv2.imwrite(sys.argv[1], cv2.cvtColor((np.clip(out, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
    if len(sys.argv) > 3:
        c3 = dbg['col3'] * dbg['A3'][..., None] + hexc('#3A3050') * (1 - dbg['A3'][..., None])
        cv2.imwrite(sys.argv[3], cv2.cvtColor((np.clip(c3, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
    if len(sys.argv) > 2:
        pc = dbg['part']
        lut = np.random.default_rng(3).uniform(0.2, 1, (20, 3))
        lut[0] = (0.6, 0.35, 0.2)
        img = np.where((pc >= 0)[..., None], lut[np.clip(pc, 0, 19)], 0)
        cv2.imwrite(sys.argv[2], cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
