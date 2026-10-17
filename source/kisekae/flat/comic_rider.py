"""漫画（コミック）の塗りの競走馬と騎手（勝負服のテーマ用）
   3Dの馬（horse3d）と騎手（anime_rider.jockey_a）を3倍の大きさで描き（anime_rider.render_anime）、漫画の絵にする：
   - 塗り：ベタの色＋くっきりした影の1段（深い影は少しだけ）。つやは小さな明るい形だけ
   - 線：黒い太い外の線・重なりと部分のさかい目の線・筋肉の線（体のふくらみにそった、入りと抜きのある細い線）
   - 栗毛（明るいオレンジ）・うしろ足の白い靴下・顔の白い流星・灰色のひづめ・黒いたてがみとしっぽ（毛の筋の線）
   - 騎手：黄色に青のひし形の勝負服・青に黄の輪のそで・赤いヘルメット・ゴーグル・白いズボン・黒いブーツ
   - 赤い頭のベルト・白い鼻革（シャドーロール）・黒い手綱・ゼッケン
   形はすべて一から作ったオリジナル。paint_comic(R, look) → 1倍の (rgb, alpha)"""
import sys, os, math
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from anime_rider import *
from anime_rider import _dist_line, _thick, _gsmooth

INK = hexc('#15111A')
CP = {                                     # ベタの色・影・深い影
    'coat': ('#F49233', '#CC6620', '#9C4814'),
    'mane': ('#26212B', '#17131B', '#0C0A0F'),
    'sock': ('#FFFFFF', '#D6DAE8', '#B4B9CC'),
    'hoof': ('#70737F', '#4B4E59', '#33353E'),
    'cloth': ('#FFFFFF', '#D6DAE8', '#B4B9CC'),
    'girth': ('#3A3D4A', '#262833', '#181A22'),
    'saddle': ('#4E3A30', '#33251E', '#1E1612'),
    'pants': ('#FFFFFF', '#D6DAE8', '#B4B9CC'),
    'boot': ('#2A2A33', '#18181E', '#0C0C10'),
    'cuff': ('#C98B4E', '#9A6234', '#6C4220'),
    'skin': ('#F7D3B5', '#DDA98B', '#B98168'),
    'goggle': ('#9DB3D6', '#6F86AE', '#4B5F86'),
    'eye': ('#1A1418', '#1A1418', '#1A1418'),
}
YEL = ('#FFC400', '#E39C00', '#B37600')
BLU = ('#1F47C8', '#163596', '#0E2468')
RED = ('#E8262A', '#B5191D', '#7E1013')
STRAND = hexc('#6A6372')


def _col3(pal):
    return tuple(hexc(x) for x in pal)


def tapered(canvas, pts, w0, w1=None, prof=(0.12, 0.25), value=255):
    """入りと抜きのある線を canvas（uint8, 3倍）へ。pts は3倍の点、w0 は3倍の太さ"""
    P = np.asarray(pts, float)
    if len(P) < 2:
        return
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    L = np.r_[0, np.cumsum(seg)]
    if L[-1] < 1:
        return
    t = np.linspace(0, L[-1], max(2, int(L[-1] / 0.8)))
    Q = np.stack([np.interp(t, L, P[:, 0]), np.interp(t, L, P[:, 1])], 1)
    u = t / L[-1]
    w = w0 * np.clip(u / prof[0], 0, 1) ** 0.6 * np.clip((1 - u) / prof[1], 0, 1) ** 0.8
    for (x, y), r in zip(Q, w):
        if r < 0.25:
            continue
        cv2.circle(canvas, (int(round(x * 16)), int(round(y * 16))), max(1, int(round(r / 2 * 16))), value, -1, cv2.LINE_AA, shift=4)


def comic_lock(col, alpha, pts, w0, base, lw, rng, tip=0.9, leaf=True, strands=2):
    """1本の房（漫画）：黒いベタ＋中に灰色の毛の筋の線＋黒いふちの線"""
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
    up = nr if np.mean(nr[:, 1]) < 0 else -nr
    cap = [P_[0] + (up[0] * math.cos(a_) - tg[0] * math.sin(a_)) * w[0] for a_ in np.linspace(0, math.pi, 9)[1:-1]]
    poly = np.vstack([P_ + up * w[:, None], (P_ - up * w[:, None])[::-1], np.array(cap)[::-1]])
    m = fill_poly(shape, [poly])
    col = over(col, hexc(base), m)
    st = np.zeros(shape, np.uint8)
    for k in range(strands):                                          # 毛の筋
        off = (k + 1) / (strands + 1) * 2 - 1 + rng.uniform(-0.12, 0.12)
        a0, a1 = rng.uniform(0.08, 0.25), rng.uniform(0.62, 0.92)
        i0, i1 = int(a0 * len(P_)), int(a1 * len(P_))
        q = P_[i0:i1] + up[i0:i1] * (w[i0:i1] * off * 0.62)[:, None]
        tapered(st, q, max(1.0, 0.75 * lw), prof=(0.2, 0.4))
    col = over(col, STRAND, st.astype(np.float32) / 255 * m)
    ol = np.zeros(shape, np.uint8)
    cv2.polylines(ol, [np.round(poly * 16).astype(np.int32)], True, 255, max(1, int(round(lw))), cv2.LINE_AA, shift=4)
    ol = ol.astype(np.float32) / 255
    col = over(col, INK, ol)
    return col, np.maximum(alpha, np.maximum(m, ol))


def fill_holes(R, max_area=900):
    """形の中の小さな穴（光線がすきまをぬけた所）を、となりの画素の値でうめる"""
    from scipy import ndimage
    inside = R['a'] > 0.5
    n_, lab_, st_, _ = cv2.connectedComponentsWithStats((~inside).astype(np.uint8), connectivity=4)
    H3, W3 = inside.shape
    hole = np.zeros_like(inside)
    for i in range(1, n_):
        x, y, w_, h_, ar = st_[i]
        if ar <= max_area and x > 0 and y > 0 and x + w_ < W3 and y + h_ < H3:
            hole |= lab_ == i
    if not hole.any():
        return 0
    _, (iy, ix) = ndimage.distance_transform_edt(~inside, return_indices=True)
    for k in ('a', 'd', 'n', 'm', 'rgb', 'ao'):
        if k in R:
            R[k] = R[k].copy()
            R[k][hole] = R[k][iy[hole], ix[hole]]
    return int(hole.sum())


def paint_comic(R, look, debug=None):
    """look: lw（線の太さの倍率）・num・seed・tail・mane・socks（白い靴下の足）・blaze（流星）
       戻り値：1倍の (rgb, alpha)。R に hooves1（1倍のひづめ）・tail_ends を入れる"""
    s = R['s']
    if look.get('fill_holes', True):
        fill_holes(R)
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
    u1 = hl_ / HEAD_REF
    rng = np.random.default_rng(look.get('seed', 1))

    def segd(p0, p1):
        dd = p1 - p0
        tt = np.clip(np.sum((Pn - p0) * dd, -1) / np.dot(dd, dd), 0, 1)
        return np.linalg.norm(Pn - (p0 + tt[..., None] * dd), axis=-1), tt

    head = (segd(Hm.v3(S['poll']), Hm.head_pt(S, 0.56, -0.03))[0] < 0.20 * Hm.HEAD_SCALE) & horse
    lts = np.where(head, _gsmooth(lt, groups, 3.0 * s), _gsmooth(lt, groups, 1.6 * s))
    ns = _gsmooth(n, groups, 2.0 * s)
    ns = ns / (np.linalg.norm(ns, axis=-1, keepdims=True) + 1e-6)
    nl = np.sum(ns * Lk, -1)
    spec = np.sum(ns * nrm(Lk + V), -1)
    ao = _gsmooth(R['ao'], groups, 1.5 * s)

    # ---------- 部分 ----------
    part = np.full(m.shape, -1, int)
    part[m == M_COAT] = 0; part[m == M_EYE] = 1; part[m == M_HOOF] = 2
    for k, v in ((M_SILK, 10), (M_SLEEVE, 11), (M_HELMET, 12), (M_PANTS, 13), (M_BOOT, 14)):
        part[m == k] = v
    socks = look.get('socks', ('HL', 'HR'))
    for k, top in (('FL', 'kn'), ('FR', 'kn'), ('HL', 'hk'), ('HR', 'hk')):
        if k not in socks:
            continue
        F = S[k]
        zl = 0.155 * F['z'] * 0.92
        q0 = np.array([*(np.asarray(F[top]) + (np.asarray(F['ft']) - np.asarray(F[top])) * 0.10), zl])
        q1 = np.array([*np.asarray(F['hf']), zl])
        dist, tt = segd(q0, q1)
        wav = 0.04 * np.sin(Pn[..., 0] * 60 + Pn[..., 2] * 40)          # 靴下のふちを少し波に
        part[(part == 0) & (dist < 0.12) & (tt > 0.30 + wav)] = 4
    if look.get('blaze', False):                                        # 顔の白い流星（横からはほとんど見えないので、ふだんはなし）
        u = Hm.adir(S['head_ang'])
        vv = np.array([-u[1], u[0]])
        rel = Pn[..., :2] - np.asarray(S['poll'])
        hs = (rel @ u) / Hm.HEAD_SCALE
        hw = (rel @ vv) / Hm.HEAD_SCALE
        width = np.interp(hs, [0.05, 0.12, 0.22, 0.40, 0.56], [0.0, 0.085, 0.048, 0.040, 0.062])
        bl = head & (part == 0) & (hs > 0.06) & (hs < 0.57) & (np.abs(Pn[..., 2]) < width * Hm.HEAD_SCALE) & (hw > -0.06)
        part[bl] = 18
    w = np.asarray(S['withers'], float)
    zs = Pn[..., 2] * side
    cloth = (part == 0) & (Pn[..., 0] > w[0] - 0.56) & (Pn[..., 0] < w[0] - 0.08) & (Pn[..., 1] > w[1] - 0.50) & (zs > -0.05)
    part[cloth] = 5
    saddle = (part == 5) & (Pn[..., 0] > w[0] - 0.47) & (Pn[..., 0] < w[0] - 0.15) & (Pn[..., 1] > w[1] - 0.115)
    part[saddle] = 7
    girth = np.isin(part, (0, 5)) & (Pn[..., 0] > w[0] - 0.21) & (Pn[..., 0] < w[0] - 0.15) & (Pn[..., 1] < w[1] - 0.20) & (Pn[..., 1] > w[1] - 0.80)
    part[girth] = 6
    hc = J['head']
    q = Pn - hc
    if 'head_r' in J:                                                  # 大きめの頭（toon_rider）：顔を広く
        hr = J['head_r']
        front = (part == 12) & (q[..., 0] > 0.02 * hr) & (q[..., 1] < -0.22 * hr)
        part[front & (q[..., 1] > -0.52 * hr)] = 16
        part[front & (q[..., 1] <= -0.52 * hr)] = 15
    else:
        front = (part == 12) & (q[..., 0] > 0.005 * js) & (q[..., 1] < -0.036 * js)
        part[front & (q[..., 1] > -0.066 * js)] = 16                   # ゴーグル（ひさしのすぐ下）
        part[front & (q[..., 1] <= -0.066 * js)] = 15                  # 顔
    for z in (1, -1):
        kn = J[f'knee{z}']
        part[(part == 14) & (np.linalg.norm(Pn - kn, axis=-1) < 0.075 * js)] = 17

    pals = {0: CP['coat'], 1: CP['eye'], 2: CP['hoof'], 4: CP['sock'], 5: CP['cloth'], 6: CP['girth'], 7: CP['saddle'],
            10: YEL, 11: BLU, 12: RED, 13: CP['pants'], 14: CP['boot'], 15: CP['skin'], 16: CP['goggle'], 17: CP['cuff'], 18: CP['sock']}
    thr = {0: 0.30, 1: 0.0, 2: 0.30, 4: 0.28, 5: 0.24, 6: 0.30, 7: 0.28, 10: 0.28, 11: 0.28, 12: 0.28, 13: 0.24, 14: 0.28, 15: 0.22,
           16: 0.26, 17: 0.28, 18: 0.26}
    col = np.zeros((H3, W3, 3), np.float32)
    shd_all = np.zeros((H3, W3), np.float32)
    for pid, pal in pals.items():
        reg = part == pid
        if not reg.any():
            continue
        b, s1, s2 = _col3(pal)
        t_sh = thr[pid]
        shd = ss_(t_sh + 0.02, t_sh - 0.02, lts)
        c = b * (1 - shd[..., None]) + s1 * shd[..., None]
        deep = np.maximum(ss_(-0.30, -0.40, nl), ss_(0.52, 0.44, ao)) * shd
        c = c * (1 - deep[..., None] * 0.8) + s2 * deep[..., None] * 0.8
        col = np.where(reg[..., None], c, col)
        shd_all = np.where(reg, shd, shd_all)
    # 勝負服の柄：胴は黄色に青のひし形、そでは青に黄の輪
    silk = part == 10
    if silk.any():
        sz = 0.105 * js
        uu = (Pn[..., 0] + Pn[..., 1]) / sz
        vv_ = (Pn[..., 0] - Pn[..., 1]) / sz
        dia = ((np.floor(uu) + np.floor(vv_)) % 2 == 0) & silk
        b, s1, s2 = _col3(BLU)
        c = b * (1 - shd_all[..., None]) + s1 * shd_all[..., None]
        col = np.where(dia[..., None], c, col)
        R['_dia'] = dia
    slv = part == 11
    if slv.any():
        tbest = np.full(m.shape, -1.0, np.float32)
        dbest = np.full(m.shape, 9.0, np.float32)
        for z in (1, -1):
            if f'arm{z}' in J:
                sh, el, hd = (np.asarray(v, float) for v in J[f'arm{z}'])
            else:
                sh = np.array([w[0] + 0.06 * js, w[1] + 0.34 * js, 0.13 * z * js])
                el = np.array([w[0] + 0.10 * js, w[1] + 0.18 * js, 0.21 * z * js])
                hd = np.array([w[0] + 0.36 * js, w[1] + 0.06 * js, 0.10 * z * js])
            d1, t1 = segd(sh, el)
            d2, t2 = segd(el, hd)
            l1, l2 = np.linalg.norm(el - sh), np.linalg.norm(hd - el)
            tt = np.where(d1 < d2, t1 * l1, l1 + t2 * l2) / (l1 + l2)
            dd = np.minimum(d1, d2)
            better = dd < dbest
            tbest = np.where(better, tt, tbest)
            dbest = np.where(better, dd, dbest)
        hoop = slv & (((tbest > 0.40) & (tbest < 0.50)) | ((tbest > 0.66) & (tbest < 0.76)))
        b, s1, s2 = _col3(YEL)
        c = b * (1 - shd_all[..., None]) + s1 * shd_all[..., None]
        col = np.where(hoop[..., None], c, col)
        R['_hoop'] = hoop
    gg = part == 16
    if gg.any():
        ys_g, xs_g = np.nonzero(gg)
        gx, gy = xs_g.mean(), ys_g.mean()
        glint = np.zeros((H3, W3), np.uint8)
        cv2.line(glint, (int((gx - 2.0 * s) * 16), int((gy + 1.0 * s) * 16)), (int((gx + 1.0 * s) * 16), int((gy - 1.4 * s) * 16)), 255,
                 max(1, int(round(1.1 * s))), cv2.LINE_AA, shift=4)
        col = over(col, hexc('#FFFFFF'), glint.astype(np.float32) / 255 * gg)
    # 小さなつや（毛の上だけ・明るい所）
    hi = ss_(0.975, 0.985, spec) * (part == 0) * (1 - shd_all)
    col = col * (1 - hi[..., None] * 0.7) + hexc('#FFC27A') * hi[..., None] * 0.7
    if debug is not None:
        debug['part'] = part; debug['lts'] = lts; debug['u1'] = u1

    # ---------- 線 ----------
    sil = _dist_line(inside.astype(np.float32), 3.3 * lw, 3.6 * lw)
    big = np.where(inside, d, 1e3)
    near = np.zeros(m.shape, bool)
    bound = np.zeros(m.shape, bool)
    for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        nb = np.roll(np.roll(big, dy, 0), dx, 1)
        pnb = np.roll(np.roll(part, dy, 0), dx, 1)
        near |= inside & (nb - big > 0.06) & (nb < 1e3)
        diffp = (pnb != part) & inside & (nb < 1e3)
        bound |= diffp & (big <= nb + 0.01)
    if 'R' in look.get('no_bound', ''):
        pass
    patb = np.zeros(m.shape, bool)                                     # 柄のさかい目（細い線）
    for key in ('_dia', '_hoop'):
        if key in R:
            pm = R[key].astype(np.uint8)
            patb |= (cv2.morphologyEx(pm, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)) > 0) & np.isin(part, (10, 11))
    def drop_small(mk, lim):                                           # 小さな島の線（3Dの形のつなぎ目のこぶ）は描かない
        n_, lab_, st_, _ = cv2.connectedComponentsWithStats(mk.astype(np.uint8), connectivity=8)
        keep = np.zeros(n_, bool)
        keep[1:] = np.maximum(st_[1:, 2], st_[1:, 3]) >= lim
        return keep[lab_]
    near = drop_small(near, 14 * s)
    inner = np.maximum(_thick(near.astype(np.float32), 2.2 * lw), _thick(bound.astype(np.float32), 1.5 * lw))
    inner = np.maximum(inner, _thick(patb.astype(np.float32), 0.9 * lw) * 0.9)
    # 筋肉の線：光の当たり方の段（ふくらみ）のさかい目を、ところどころ入りと抜きのある細い線で
    ml = np.zeros((H3, W3), np.uint8)
    coat = (part == 0) & horse
    dsil = cv2.distanceTransform(inside.astype(np.uint8), cv2.DIST_L2, 5)
    ltm = _gsmooth(lts, groups, 1.2 * s)
    for lev, k_ in look.get('muscle', ((0.62, 1.0), (0.42, 0.8))):
        bm = ((ltm > lev) & coat).astype(np.uint8)
        cs, _ = cv2.findContours(bm, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        for c in cs:
            Pc = c[:, 0, :].astype(float)
            if len(Pc) < 30 * s:
                continue
            ext = Pc.max(0) - Pc.min(0)
            if ext.max() < 16 * s:                                     # 小さな輪（目のように見える）は描かない
                continue
            ok = coat[Pc[:, 1].astype(int), Pc[:, 0].astype(int)] & (dsil[Pc[:, 1].astype(int), Pc[:, 0].astype(int)] > 4.5 * s)
            i = 0
            nP = len(Pc)
            while i < nP:
                L = int(rng.uniform(20, 40) * s)
                seg_ = np.arange(i, min(nP, i + L))
                good = ok[seg_]
                if good.mean() > 0.9 and len(seg_) > 12 * s and rng.random() < 0.58:
                    Q = Pc[seg_]
                    kk = max(1, int(1.2 * s))
                    Q = np.stack([np.convolve(np.r_[np.full(kk, Q[0, j]), Q[:, j], np.full(kk, Q[-1, j])], np.ones(2 * kk + 1) / (2 * kk + 1), 'valid') for j in (0, 1)], 1)
                    tapered(ml, Q, 1.25 * s * lw * k_)
                i += L + int(rng.uniform(4, 14) * s)
    line = np.clip(np.maximum(np.maximum(sil, inner * inside), ml.astype(np.float32) / 255 * inside), 0, 1)
    if debug is not None:
        debug['L_sil'] = sil; debug['L_inner'] = inner; debug['L_ml'] = ml.astype(np.float32) / 255; debug['inside'] = inside
    col = col * (1 - line[..., None]) + INK * line[..., None]
    A = np.clip(np.maximum(a, line), 0, 1)

    # ---------- 目・鼻の穴・口 ----------
    ex, ey = R['eye']
    fd = (np.asarray(R['muzzle']) - np.asarray(R['poll'])) / (hl_ + 1e-9)
    pv = np.array([fd[1], -fd[0]])
    if pv[1] > 0:
        pv = -pv                                                          # 顔の上（ひたい）がわ
    ang = math.degrees(math.atan2(fd[1], fd[0]))
    r = max(2.0, hl_ * 0.095)
    def ell(cx, cy, ax, ay, rot, a0=0, a1=360, th=-1):
        mm = np.zeros((H3, W3), np.uint8)
        cv2.ellipse(mm, (int(cx * 16), int(cy * 16)), (int(ax * 16), int(ay * 16)), rot, a0, a1, 255, th, cv2.LINE_AA, shift=4)
        return mm.astype(np.float32) / 255
    E = np.array([ex, ey])
    if look.get('eye', True):                                            # toon_rider は目を上に描くので、なしにできる
        alm = fill_poly((H3, W3), [np.array([E - fd * r * 1.05 + pv * r * 0.10, E - fd * r * 0.4 + pv * r * 0.62, E + fd * r * 0.55 + pv * r * 0.55,
                                             E + fd * r * 1.10 + pv * r * 0.05, E + fd * r * 0.40 - pv * r * 0.48, E - fd * r * 0.45 - pv * r * 0.40])])
        col = over(col, hexc('#FFFDF6'), alm)                               # 白目
        ir = E + fd * r * 0.30 + pv * r * 0.04
        iris = soft_circle(H3, W3, ir[0], ir[1], r * 0.45, 1.0) * alm
        col = over(col, hexc('#2A1A12'), iris)
        col = over(col, hexc('#FFFFFF'), soft_circle(H3, W3, ir[0] - r * 0.12, ir[1] - r * 0.16, r * 0.14, 1.0) * alm)
        lid = np.zeros((H3, W3), np.uint8)
        tapered(lid, [E - fd * r * 1.30 + pv * r * 0.05, E - fd * r * 0.4 + pv * r * 0.66, E + fd * r * 0.55 + pv * r * 0.58, E + fd * r * 1.15 + pv * r * 0.05],
                2.4 * s * lw, prof=(0.2, 0.15))                               # 太い上まぶた
        tapered(lid, [E + fd * r * 1.10 + pv * r * 0.05, E + fd * r * 0.40 - pv * r * 0.50, E - fd * r * 0.45 - pv * r * 0.42], 1.2 * s * lw, prof=(0.2, 0.3))
        tapered(lid, [E - fd * r * 1.15 + pv * r * 1.35, E - fd * r * 0.1 + pv * r * 1.10, E + fd * r * 0.95 + pv * r * 0.78], 1.6 * s * lw, prof=(0.3, 0.2))   # けわしい眉の線
        col = over(col, INK, lid.astype(np.float32) / 255)
        A = np.maximum(A, lid.astype(np.float32) / 255 * horse)
    nx_, ny_ = R['nostril']
    nos = np.zeros((H3, W3), np.uint8)
    tapered(nos, [np.array([nx_, ny_]) - fd * r * 0.55 + pv * r * 0.35, np.array([nx_, ny_]) + fd * r * 0.25 + pv * r * 0.30,
                  np.array([nx_, ny_]) + fd * r * 0.30 - pv * r * 0.45], 1.9 * s * lw, prof=(0.2, 0.3))        # ふくらんだ鼻の穴
    col = over(col, INK, nos.astype(np.float32) / 255 * horse)

    # ---------- ゼッケンの番号 ----------
    clm = part == 5
    if clm.any():
        from PIL import Image, ImageDraw, ImageFont
        dt = cv2.distanceTransform(clm.astype(np.uint8), cv2.DIST_L2, 5)
        cy, cx = np.unravel_index(int(np.argmax(dt)), dt.shape)
        size = int(min(dt.max() * 1.75, (np.percentile(np.nonzero(clm)[0], 95) - np.percentile(np.nonzero(clm)[0], 5)) * 0.66))
        F = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'
        lay = Image.new('L', (W3, H3), 0)
        ImageDraw.Draw(lay).text((cx, cy), str(look['num']), font=ImageFont.truetype(F, max(8, size)), fill=255, anchor='mm')
        col = over(col, INK, np.asarray(lay).astype(np.float32) / 255 * clm)

    # ---------- たてがみ・前髪・しっぽ（黒い房＋毛の筋） ----------
    hlw = max(1.0, 1.4 * s * lw)
    crest = np.asarray(R['crest'], float)
    nC = len(crest)
    pp, mz = np.asarray(R['poll'], float), np.asarray(R['muzzle'], float)
    mane_k = look.get('mane', 1.0)
    base = CP['mane'][0]

    def crest_dir(i):
        tg = crest[min(i + 1, nC - 1)] - crest[max(i - 1, 0)]
        upa = math.atan2(tg[1], tg[0]) - math.pi / 2
        if math.cos(upa) > 0.3:
            upa += math.pi
        return upa
    back = []
    for i in range(10, nC - 3, 5):
        upa = crest_dir(i)
        L = (34 + 12 * math.sin(i / nC * math.pi) + rng.uniform(-4, 5)) * u1 * mane_k
        pts = flow(crest[i] + np.array([0.0, 2.0 * u1]), upa - 0.30 + rng.uniform(-0.12, 0.12), L, 16, wind=0.20,
                   wind_ang=math.pi + 0.40, curl=0.025, rng=rng, wave=1.2, phase=i * 0.5)
        back.append((pts, (13.0 + rng.uniform(-1, 1.5)) * u1))
    bcol = np.zeros((H3, W3, 3), np.float32); ba = np.zeros((H3, W3), np.float32)
    for pts, w0 in back:
        bcol, ba = comic_lock(bcol, ba, pts, w0, '#1A161E', hlw, rng)
    front = []
    for i in range(8, nC - 3, 4):
        upa = crest_dir(i)
        root = crest[i] - np.array([math.cos(upa), math.sin(upa)]) * 2.0 * u1
        L = (30 + 14 * math.sin(i / nC * math.pi) + rng.uniform(-4, 4)) * u1 * mane_k
        pts = flow(root, upa - 0.62 + rng.uniform(-0.12, 0.12), L, 16, wind=0.22, wind_ang=math.pi + 0.30, curl=0.03,
                   rng=rng, wave=1.3, phase=i * 0.7)
        front.append((pts, (12.5 + rng.uniform(-1, 1.5)) * u1))
    for k in range(2):
        a0 = math.atan2(-fd[1], -fd[0]) - 0.55 - 0.25 * k
        pts = flow(pp + fd * (3.0 + 2.5 * k) * u1, a0, (16 - 3 * k) * u1 * mane_k, 10, wind=0.18, wind_ang=math.pi + 0.35,
                   curl=0.03, rng=rng, wave=0.6, phase=k)
        front.append((pts, (7.0 - k) * u1))
    hcol = np.zeros((H3, W3, 3), np.float32); ha = np.zeros((H3, W3), np.float32)
    for pts, w0 in front:
        hcol, ha = comic_lock(hcol, ha, pts, w0, base, hlw, rng)
    # しっぽ：お尻のいちばんうしろから、波打ってうしろへ（毛の筋の多い大きな房）
    Pj = lambda p3: R['scene'].project(np.asarray([p3], float))[0][0][:2]
    cr2, bt2 = Pj(Hm.v3(S['croup'])), Pj(Hm.v3(S['buttock']))
    ys_, xs_ = np.nonzero(np.isin(part, (0, 4, 5, 6, 7)))
    sel = (ys_ > cr2[1] - 10 * u1) & (ys_ < bt2[1] + 10 * u1) & (xs_ < cr2[0])
    k_ = np.argmin(xs_[sel] * 0.9 + ys_[sel] * 0.44)
    troot = np.array([xs_[sel][k_], ys_[sel][k_]], float) + np.array([3.0, -2.0]) * u1
    tl = []
    t_ang = look.get('tail_ang', 186.0)
    NT = 9
    for k in range(NT):
        root = troot + np.array([rng.normal(0, 0.5), (k - (NT - 1) / 2) * 0.9]) * u1
        ang0 = math.radians(t_ang) + (k - (NT - 1) / 2) * 0.055 + rng.uniform(-0.04, 0.04)
        L = (64 + rng.uniform(-6, 10) - abs(k - (NT - 1) / 2) * 3.5) * u1 * look.get('tail', 1.0)
        pts = flow(root, ang0, L, 24, wind=0.0, wind_ang=math.pi, curl=0.0, rng=rng, wave=look.get('tail_wave', 2.6), phase=k * 0.35)
        tl.append((pts, (16.0 - abs(k - (NT - 1) / 2) * 1.3) * u1))
    tl.sort(key=lambda x: -x[0][-1][1])
    R['tail_ends'] = [pts[-1] / s for pts, _ in tl]
    for pts, w0 in tl:
        bcol, ba = comic_lock(bcol, ba, pts, w0, base, hlw, rng, tip=0.75, leaf=False, strands=3)
    jm = np.clip(np.maximum(jock.astype(np.float32), _dist_line(jock.astype(np.float32), 0, 3.6 * lw)) * 1.5, 0, 1)
    ha = ha * (1 - jm)
    col = col * (1 - ha[..., None]) + hcol * ha[..., None]
    A = np.maximum(A, ha)
    col = col * A[..., None] + bcol * (ba * (1 - A))[..., None]
    A = A + ba * (1 - A)
    col = col / np.maximum(A[..., None], 1e-4)

    # ---------- 頭のベルト（赤）・シャドーロール（白）・手綱 ----------
    mo, ey_ = np.asarray(R['mouth'], float), np.asarray(R['eye'], float)
    perp = np.array([-fd[1], fd[0]])
    nose = mz + (ey_ - mz) * 0.30

    def strap(pts, wd, color):
        nonlocal col, A
        o = np.zeros((H3, W3), np.uint8)
        cv2.polylines(o, [np.round(np.asarray(pts) * 16).astype(np.int32)], False, 255, max(1, int(round(wd + 2.2 * s * lw))), cv2.LINE_AA, shift=4)
        i_ = np.zeros((H3, W3), np.uint8)
        cv2.polylines(i_, [np.round(np.asarray(pts) * 16).astype(np.int32)], False, 255, max(1, int(round(wd))), cv2.LINE_AA, shift=4)
        o = o.astype(np.float32) / 255; i_ = i_.astype(np.float32) / 255
        col = over(col, INK, o)
        col = over(col, hexc(color), i_)
        A = np.maximum(A, o)
    top = pp + fd * 1.0 * u1 + perp * 1.0 * u1
    rel_e = ey_ - pp
    behind = pp + fd * (np.dot(rel_e, fd) * 0.95) + perp * (np.dot(rel_e, perp) + 2.6 * r / u1 * u1)   # 目のうしろ下を通る
    c1_ = behind
    c2_ = mo + (behind - mo) * 0.45 + perp * 1.0 * u1
    cheek_pts = [(1 - v_) ** 3 * top + 3 * (1 - v_) ** 2 * v_ * (top + (c1_ - top) * 1.25) + 3 * (1 - v_) * v_ ** 2 * c2_ + v_ ** 3 * mo
                 for v_ in np.linspace(0, 1, 30)]
    strap(cheek_pts, 2.2 * u1, RED[0])                                                           # ほおのベルト（なめらかに）
    if look.get('mouth', True):
        mouthl = np.zeros((H3, W3), np.uint8)                            # 口の線（はみから鼻先の下へ）
        tapered(mouthl, [mo + fd * 0.5 * u1, mo + fd * 4.0 * u1 + perp * 0.6 * u1, mo + fd * 7.5 * u1 - perp * 0.3 * u1], 1.6 * s * lw, prof=(0.15, 0.35))
        col = over(col, INK, mouthl.astype(np.float32) / 255 * horse)
    strap([pp + fd * 3.4 * u1 + perp * 0.5 * u1, pp + fd * 4.8 * u1 - perp * 4.6 * u1], 2.2 * u1, RED[0])   # ひたいのベルト
    # シャドーロール（白いふわふわの鼻革）
    roll = np.zeros((H3, W3), np.uint8)
    rp = [nose + perp * 6.2 * u1, nose - perp * 5.8 * u1]
    cv2.polylines(roll, [np.round(np.asarray(rp) * 16).astype(np.int32)], False, 255, max(1, int(round(5.2 * u1))), cv2.LINE_AA, shift=4)
    rl = roll.astype(np.float32) / 255
    col = over(col, INK, _dist_line(rl, 0, 2.0 * s * lw) * (1 - rl))
    col = over(col, hexc('#FFFFFF'), rl)
    sh_ = np.zeros((H3, W3), np.uint8)
    for j in range(4):                                                  # ふわふわの影の線
        c0 = nose + perp * (4.6 - j * 3.0) * u1
        tapered(sh_, [c0 - fd * 2.0 * u1, c0 + fd * 0.6 * u1 - perp * 0.8 * u1], 0.9 * s * lw)
    col = over(col, hexc('#B9BED0'), sh_.astype(np.float32) / 255 * rl)
    A = np.maximum(A, np.maximum(rl, _dist_line(rl, 0, 2.0 * s * lw)))
    hand = np.asarray(R['hand_near'], float)
    mid = (mo + hand) / 2 + np.array([0.0, 4.0 * u1])
    rein = np.zeros((H3, W3), np.uint8)
    cv2.polylines(rein, [np.round(np.array([(1 - v_) ** 2 * mo + 2 * (1 - v_) * v_ * mid + v_ ** 2 * hand for v_ in np.linspace(0, 1, 24)]) * 16).astype(np.int32)],
                  False, 255, max(1, int(round(1.8 * u1))), cv2.LINE_AA, shift=4)
    rk = rein.astype(np.float32) / 255
    col = over(col, INK, rk)
    A = np.maximum(A, rk)
    ring = np.zeros((H3, W3), np.uint8)
    cv2.circle(ring, (int(mo[0] * 16), int(mo[1] * 16)), int(2.2 * u1 * 16), 255, max(1, int(round(1.4 * u1))), cv2.LINE_AA, shift=4)
    rg = ring.astype(np.float32) / 255
    col = over(col, INK, _dist_line(rg, 0, 1.2 * s * lw) * (1 - rg))
    col = over(col, hexc('#FFD24A'), rg)

    if debug is not None:
        debug['col3'] = col.copy(); debug['A3'] = A.copy()
    R['hooves1'] = np.asarray(R['hooves'], float) / s
    W1, H1 = W3 // s, H3 // s
    pre = cv2.resize(col * A[..., None], (W1, H1), interpolation=cv2.INTER_AREA)
    A1 = cv2.resize(A, (W1, H1), interpolation=cv2.INTER_AREA)
    rgb1 = pre / np.maximum(A1[..., None], 1e-4)
    return np.clip(rgb1, 0, 1), np.clip(A1, 0, 1)


if __name__ == '__main__':
    import json
    W, Hh = 780, 320
    pose = json.loads(sys.argv[2]) if len(sys.argv) > 2 else dict(theta=-2.0, neck_rot=-40.0, head_ang=-28.0,
        fore=dict(L=[-100, -30, -20, -8], R=[-128, -20, -140, -165]), hind=dict(L=[-110, -152, -132, -152], R=[-58, -100, -72, -50]), tail=[-170, -158])
    box = tuple(json.loads(sys.argv[3])) if len(sys.argv) > 3 else (250, 105, 620, 298)
    azim = float(sys.argv[4]) if len(sys.argv) > 4 else 18.0
    js = float(sys.argv[5]) if len(sys.argv) > 5 else 1.12
    R = render_anime(pose, box, W, Hh, s=3, azim=azim, elev=6, name='comictest', head_scale=1.12, js=js)
    dbg = {}
    rgb, a = paint_comic(R, dict(num=1, seed=5), debug=dbg)
    bg = np.zeros((Hh, W, 3), np.float32) + hexc('#DDE4F6')
    out = bg * (1 - a[..., None]) + rgb * a[..., None]
    cv2.imwrite(sys.argv[1], cv2.cvtColor((np.clip(out, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
