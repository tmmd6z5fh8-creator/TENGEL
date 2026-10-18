"""墨の筆で描いた走る競走馬（新聞の絵用）
   3Dの馬の形（horse3d）を3倍の大きさで描き、
   - 体：骨にそった「筆の向き」を作り、その向きに流れる筋（毛先の跡）で外のふちをかすれさせる（筆のかすれ）
   - たてがみ・しっぽ・ひづめ：毛（穂先）の1本ずつを線にした筆の線（はじめは墨たっぷり、先へ行くほどかすれて割れる）
   を、墨の黒1色で。しっぽはお尻のいちばんうしろ（上がわ）から出す。形はすべて一から作ったオリジナル"""
import sys, os, math
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(K, 'r3d'))
sys.path.insert(0, K)
from style2d import *
from h3d import Scene, nrm
import horse3d as Hm


def ss_(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def render_sil(pose, box, W, Hh, s=3, azim=4, elev=3, fov=26, head_scale=1.15, name='ink', cam=None):
    """3倍の大きさで馬の形を描く（しっぽの根元の3Dの出っぱりは作らない）。
       cam：決めたカメラ (目, 見る所)（走るコマで、どのコマも同じカメラにするとき）。なければ box に入るように決める（R['cam'] に入れて返す）"""
    Hm.HEAD_SCALE = head_scale
    W3, H3 = W * s, Hh * s
    e, t = cam if cam is not None else frame_horse(pose, tuple(v * s for v in box), W3, H3, facing='right', azim=azim, elev=elev, fov=fov)
    sc = Scene()
    sc.image(W3, H3, 1)
    sc.camera(e, t, fov)
    sc.bounce(0)
    sc.env((0.5, 0.5, 0.5), (0.4, 0.4, 0.4), (0.2, 0.2, 0.2))
    sc.light((0.5, 0.8, 0.6), (2.0, 2.0, 2.0), 10, 0)
    sc.mat(1, 1, (0.6, 0.6, 0.6), 0.6)
    sc.mat(5, 1, (0.02, 0.02, 0.02), 0.1)
    sc.mat(6, 1, (0.3, 0.3, 0.3), 0.6)
    S0 = Hm.skeleton(pose)
    ta0 = Hm.v3(S0['tailhead']); t10 = Hm.v3(S0['tailhead'] + Hm.adir(pose['tail'][0]) * 0.20)
    rcone0 = sc.rcone
    def rcone_no_dock(a, b, *args, **kw):
        if np.allclose(np.asarray(a, float), ta0) or np.allclose(np.asarray(a, float), t10):
            return
        return rcone0(a, b, *args, **kw)
    sc.rcone = rcone_no_dock
    S = Hm.build(sc, pose, mats=dict(body=1, neck=1, hoof=6, eye=5, head=1))
    sc.rcone = rcone0
    R = sc.render(os.path.join(TMP, name))
    P = lambda pts: sc.project(np.asarray(pts, float))[0]
    ts = np.linspace(0, 1, 40)
    R['crest'] = P(np.c_[Hm.bez(S['crest'], ts), np.zeros(len(ts))])
    R['poll'] = P([Hm.v3(S['poll'])])[0]
    R['muzzle'] = P([Hm.head_pt(S, 0.56, -0.03)])[0]
    e0, e1 = S['eyes']
    R['eye'] = P([e0 if np.dot(e0 - t, np.asarray(e, float) - t) > np.dot(e1 - t, np.asarray(e, float) - t) else e1])[0]
    R['S'], R['scene'], R['s'] = S, sc, s
    R['P'] = P
    R['cam'] = (e, t)
    return R


def bones(R):
    """筆の向きを決める骨（2Dの線分のリスト）"""
    S, P = R['S'], R['P']
    v = lambda p, z=0.0: Hm.v3(p, z)
    segs = []
    def chain(pts):
        q = P(pts)
        for i in range(len(q) - 1):
            segs.append((q[i][:2], q[i + 1][:2]))
    chain([v(S['tailhead']), v(S['croup']), v(S['loin']), v(S['back']), v(S['withers']), v(S['scap'])])
    chain([v(S['buttock']), v(S['hip']), v((S['hip'] + S['sternum']) / 2), v(S['sternum']), v(S['chest'])])
    cr = Hm.bez(S['crest'], np.linspace(0, 1, 8)); th = Hm.bez(S['throat'], np.linspace(0, 1, 8))
    chain([v(p) for p in cr]); chain([v(p) for p in th]); chain([v((a + b) / 2) for a, b in zip(cr, th)])
    chain([v(S['poll']), Hm.head_pt(S, 0.28, -0.04), Hm.head_pt(S, 0.56, -0.03)])
    for k in ('FL', 'FR'):
        F = S[k]; z = 0.155 * F['z']
        chain([v(F['s0'], z * 0.5), v(F['ps'], z), v(F['el'], z), v(F['kn'], z), v(F['ft'], z), v(F['co'], z), v(F['hf'], z)])
    for k in ('HL', 'HR'):
        F = S[k]; z = 0.155 * F['z']
        chain([v(F['hj'], z * 0.5), v(F['st'], z), v(F['hk'], z), v(F['ft'], z), v(F['co'], z), v(F['hf'], z)])
    return segs


def direction_field(shape, segs, box, sig=14.0):
    """骨の向きを、近い骨ほど強くまぜた向き（2倍角でまぜる＝向きの裏表を気にしない）"""
    H3, W3 = shape
    x0, y0, x1, y1 = box
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    c2 = np.zeros(xx.shape, np.float32); s2 = np.zeros(xx.shape, np.float32); wsum = np.zeros(xx.shape, np.float32)
    dmin = np.full(xx.shape, 1e9, np.float32)
    for a, b in segs:
        a = np.asarray(a, np.float32); b = np.asarray(b, np.float32)
        d = b - a; L2 = float(d @ d) + 1e-6
        t = np.clip(((xx - a[0]) * d[0] + (yy - a[1]) * d[1]) / L2, 0, 1)
        dist = np.hypot(xx - (a[0] + t * d[0]), yy - (a[1] + t * d[1]))
        w = np.exp(-(dist / sig) ** 2) + 1e-12
        ang = math.atan2(d[1], d[0])
        c2 += w * math.cos(2 * ang); s2 += w * math.sin(2 * ang); wsum += w
        dmin = np.minimum(dmin, dist)
    th = 0.5 * np.arctan2(s2, c2)
    out = np.zeros((H3, W3, 2), np.float32)
    out[y0:y1, x0:x1, 0] = np.cos(th); out[y0:y1, x0:x1, 1] = np.sin(th)
    return out


def lic(noise, field, box, steps=22, h=1.6):
    """向きにそってノイズをならす（筆の毛の筋）"""
    x0, y0, x1, y1 = box
    N = noise[y0:y1, x0:x1].astype(np.float32)
    F = field[y0:y1, x0:x1]
    hh, ww = N.shape
    yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
    acc = N.copy(); cnt = np.ones_like(N)
    for sgn in (1, -1):
        px, py = xx.copy(), yy.copy()
        dx, dy = F[..., 0] * sgn, F[..., 1] * sgn
        for k in range(steps):
            px = px + dx * h; py = py + dy * h
            ndx = cv2.remap(F[..., 0], px, py, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            ndy = cv2.remap(F[..., 1], px, py, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            flip = np.sign(ndx * dx + ndy * dy + 1e-9)          # 向きの裏表をそろえる
            dx, dy = ndx * flip, ndy * flip
            wk = 1.0 - k / steps
            acc += cv2.remap(N, px, py, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT) * wk
            cnt += wk
    out = np.zeros(noise.shape, np.float32)
    out[y0:y1, x0:x1] = acc / cnt
    return out


def resample(path, step=1.0):
    P = np.asarray(path, float)
    seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    n = max(4, int(seg[-1] / step))
    u = np.linspace(0, seg[-1], n)
    return np.stack([np.interp(u, seg, P[:, 0]), np.interp(u, seg, P[:, 1])], 1)


def bristle_stroke(canvas, path, w0, w1, rng, nb=26, lw=2, dry=0.62, split=0.35, taper=1.0, wander=0.5, gap=0.55, ink=1.0, start=0.0):
    """穂先の毛を1本ずつ線にした筆の線。path は筆の通り道（3倍の画素）。
       根元は墨たっぷり（すき間なし）、dry から先はかすれ（毛の線が切れる）、両はしの毛ほど早く終わる（穂先が割れる）"""
    P = resample(path, 1.0)
    n = len(P)
    t = np.linspace(0, 1, n)
    tg = np.gradient(P, axis=0); tg /= np.linalg.norm(tg, axis=1, keepdims=True) + 1e-9
    nr = np.stack([-tg[:, 1], tg[:, 0]], 1)
    w = w0 * (1 - t) ** taper + w1 * (1 - (1 - t) ** taper)
    offs = (np.arange(nb) + rng.uniform(0.2, 0.8, nb)) / nb - 0.5
    for b in range(nb):
        o = offs[b]
        Lb = 1.0 - split * (abs(o) * 2) ** 1.4 * rng.uniform(0.4, 1.0) - rng.uniform(0, 0.10)
        nn = max(3, int(n * Lb))
        jit = np.cumsum(rng.normal(0, 0.12, n))[:nn] * wander
        q = P[:nn] + nr[:nn] * (o * w[:nn] + jit)[:, None]
        td = dry + rng.uniform(-0.18, 0.22) - abs(o) * 0.30
        on = np.ones(nn, bool)
        i = int(td * n)
        while i < nn:                                   # かすれ：墨が切れた所はとぶ
            run = int(rng.integers(3, 14))
            if rng.random() < gap * min(1.0, (i / n - td) * 3 + 0.3):
                on[i:i + run] = False
            i += run
        if start > 0:                                   # 毛ごとに はじまりをずらす（かすれの入りが まっすぐにならない）
            on[:int(rng.uniform(0, start) * n)] = False
        idx = np.nonzero(np.diff(np.r_[0, on.astype(int), 0]))[0]
        for s0, s1 in zip(idx[::2], idx[1::2]):
            if s1 - s0 >= 2:
                cv2.polylines(canvas, [np.round(q[s0:s1] * 16).astype(np.int32)], False, ink, lw, cv2.LINE_AA, shift=4)
    return canvas


def flow_path(p, ang, L, n=24, bend=0.0, wave=0.0, phase=0.0, rng=None):
    pts = [np.asarray(p, float)]
    a = ang
    for k in range(n):
        a += bend + wave * math.sin(k * 0.45 + phase) * 0.05 + (rng.normal(0, 0.012) if rng is not None else 0)
        pts.append(pts[-1] + np.array([math.cos(a), math.sin(a)]) * L / n)
    return np.array(pts)


def paint_ink(R, look):
    """戻り値：1倍の墨の濃さ（0〜1）"""
    s = R['s']
    a = np.clip(R['a'], 0, 1)
    H3, W3 = a.shape
    M = (a > 0.5).astype(np.uint8)
    rng = np.random.default_rng(look.get('seed', 5))
    S = R['S']; Pj = lambda p3: R['P']([p3])[0][:2]
    ys, xs = np.nonzero(M)
    pad = 70 * s
    box = (max(0, xs.min() - pad), max(0, ys.min() - pad), min(W3, xs.max() + pad), min(H3, ys.max() + pad))
    segs = bones(R)
    F = direction_field((H3, W3), segs, box, sig=6.0 * s)
    noise = rng.random((H3, W3)).astype(np.float32)
    noise = cv2.GaussianBlur(noise, (0, 0), look.get('grain', 1.1) * s)
    Sx = lic(noise, F, box, steps=30, h=1.0 * s)
    sub = Sx[box[1]:box[3], box[0]:box[2]]
    mu, sd = sub.mean(), sub.std() + 1e-6
    Sx = np.clip(0.5 + (Sx - mu) / sd * 0.18, 0, 1)
    din = cv2.distanceTransform(M, cv2.DIST_L2, 5)
    dout = cv2.distanceTransform(1 - M, cv2.DIST_L2, 5)
    sdist = din - dout
    lowf = cv2.GaussianBlur(rng.random((H3 // 8 + 1, W3 // 8 + 1)).astype(np.float32), (0, 0), 3.0)
    lowf = cv2.resize(lowf, (W3, H3), interpolation=cv2.INTER_CUBIC)
    lowf = np.clip((lowf - lowf.mean()) / (lowf.std() + 1e-6) * 0.5 + 0.5, 0, 1)
    hl = np.linalg.norm(np.asarray(R['muzzle'][:2]) - np.asarray(R['poll'][:2]))
    u1 = hl / 60.0
    # 頭はかすれさせない（顔に白い筋が出ないように）
    yyb, xxb = np.mgrid[0:H3, 0:W3].astype(np.float32)
    pp, mz = np.asarray(R['poll'][:2], float), np.asarray(R['muzzle'][:2], float)
    dd = mz - pp; tt = np.clip(((xxb - pp[0]) * dd[0] + (yyb - pp[1]) * dd[1]) / (dd @ dd), -0.3, 1.0)
    headd = np.hypot(xxb - (pp[0] + tt * dd[0]), yyb - (pp[1] + tt * dd[1]))
    headk = ss_(hl * 0.30, hl * 0.55, headd)                          # 0：頭の中 1：頭から遠い
    # 下向き・うしろ向きのふち（腹・胸の下・おしりのうしろ）ほど、筆がかすれて毛羽立つ
    Mb = cv2.GaussianBlur(M.astype(np.float32), (0, 0), 2.5 * s)
    gx = cv2.Sobel(Mb, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(Mb, cv2.CV_32F, 0, 1, ksize=3)
    gn = np.sqrt(gx * gx + gy * gy) + 1e-6
    down = np.clip(-gy / gn, 0, 1); rear = np.clip(gx / gn, 0, 1)
    rough = np.clip(0.35 + 0.9 * down + 0.5 * rear, 0, 1.4)
    amp = (look.get('edge_amp', 2.6) + 3.2 * lowf) * s * (0.35 + 0.65 * headk) * rough
    ink = ss_(-0.8, 0.8, sdist + (Sx - 0.5) * 2 * amp)                  # ふちが毛の筋でぎざぎざ
    kb = look.get('kasure_band', 7.0) * s * (0.35 + 1.0 * lowf) * (0.5 + 0.7 * np.clip(rough, 0, 1))
    thr = 0.60 + 0.40 * np.clip(din / np.maximum(kb, 1e-3), 0, 1)
    kas = ss_(thr, thr + 0.04, Sx) * (din > 0.9 * s) * (din < kb) * headk
    ink = ink * (1 - kas * look.get('kasure', 0.95))
    # 体の中のかすれ（筆の通った跡の白い筋）：腹のふち・おしりの丸み・首の下・前の足
    gaps = np.zeros((H3, W3), np.float32)
    v = lambda p, z=0.0: Hm.v3(p, z)
    FL, HL = S['FL'], S['HL']
    gp = [
        ([v(S['sternum']) + [0.10, 0.10, 0], v((S['sternum'] + S['hip']) / 2) + [0, 0.06, 0], v(S['hip']) + [0.12, -0.10, 0]], 0.20, 9),
        ([v(S['croup']) + [-0.10, -0.08, 0], v(S['buttock']) + [0.05, 0.10, 0], v(S['buttock']) + [0.12, -0.12, 0]], 0.16, 7),
        ([Hm.v3(Hm.bez(S['throat'], 0.25)) + [0.04, 0.06, 0], Hm.v3(Hm.bez(S['throat'], 0.65)) + [0.02, 0.07, 0]], 0.12, 6),
        ([v(FL['el'], 0.155) + [0.02, 0.02, 0], v(FL['kn'], 0.155)], 0.07, 4),
        ([v(HL['st'], 0.155) + [0.03, 0.02, 0], v(HL['hk'], 0.155)], 0.08, 4),
    ]
    for pts3, wm, nb in gp:
        path = R['P']([np.asarray(q, float) for q in pts3])[:, :2]
        path = resample(path, 1.0)
        wpx = wm * np.linalg.norm(Pj(v(S['withers'])) - Pj(v(S['croup']))) / 0.95
        bristle_stroke(gaps, path, wpx, wpx * 0.25, rng, nb=nb, lw=max(1, int(round(0.6 * s))), dry=0.35, split=0.85, gap=0.35,
                       taper=1.3, wander=0.8, start=0.45)
    gaps = gaps * (din > 1.5 * s) * headk
    ink = ink * (1 - np.clip(gaps, 0, 1) * 0.92)
    # 目（小さく紙の色を残す）
    if look.get('eye', True):
        ex, ey = R['eye'][:2]
        em = np.zeros((H3, W3), np.uint8)
        cv2.circle(em, (int(ex * 16), int(ey * 16)), int(max(1.2, hl * 0.022) * 16), 255, -1, cv2.LINE_AA, shift=4)
        ink = ink * (1 - em.astype(np.float32) / 255 * 0.85)
    strokes = np.zeros((H3, W3), np.float32)
    # ---------- たてがみ：首の上から、うしろ上へ大きく飛ぶ ----------
    crest = np.asarray(R['crest'], float)[:, :2]
    nC = len(crest)
    order = list(range(nC - 3, 6, -2))
    for j, i in enumerate(order):
        p = crest[i]
        tgv = crest[min(i + 1, nC - 1)] - crest[i - 1]
        upa = math.atan2(tgv[1], tgv[0]) - math.pi / 2
        if math.cos(upa) > 0.3:
            upa += math.pi
        root = p - np.array([math.cos(upa), math.sin(upa)]) * 4.0 * u1
        frac = i / nC
        L = (40 + 34 * math.sin(frac * math.pi) + rng.uniform(-8, 10)) * u1 * look.get('mane', 1.0)
        ang = upa - 1.05 + rng.uniform(-0.16, 0.12)
        path = flow_path(root, ang, L, 30, bend=-0.012 + rng.uniform(-0.005, 0.004), wave=1.4, phase=j * 0.8, rng=rng)
        bristle_stroke(strokes, path, (11 + rng.uniform(-1.5, 2.5)) * u1, 0.8 * u1, rng, nb=26, lw=max(1, int(round(0.75 * s))),
                       dry=0.58, split=0.50, taper=0.9)
    fd = (mz - pp) / np.linalg.norm(mz - pp)
    for k in range(2):                                                   # 前髪
        path = flow_path(pp + fd * (4 + 3 * k) * u1, math.atan2(-fd[1], -fd[0]) - 0.75 - 0.2 * k, (20 - 4 * k) * u1, 14, bend=-0.01, rng=rng)
        bristle_stroke(strokes, path, (6.5 - k) * u1, 0.6 * u1, rng, nb=12, lw=max(1, int(round(0.75 * s))), dry=0.55, split=0.5)
    # ---------- しっぽ：お尻のいちばんうしろ（上がわ）から、うしろへ長くなびく ----------
    cr2, bt2 = Pj(Hm.v3(S['croup'])), Pj(Hm.v3(S['buttock']))
    ys_, xs_ = np.nonzero(M)
    sel = (ys_ > cr2[1] - 12 * u1) & (ys_ < bt2[1] + 12 * u1) & (xs_ < cr2[0])
    k_ = np.argmin(xs_[sel] * 0.9 + ys_[sel] * 0.44)
    troot = np.array([xs_[sel][k_], ys_[sel][k_]], float) + np.array([5.0, 1.5]) * u1
    R['tail_root'] = troot / s
    t_ang = math.radians(look.get('tail_ang', 172))
    nt = look.get('tail_n', 6)
    for k in range(nt):
        f = (k - (nt - 1) / 2)
        L = (look.get('tail_len', 150) - abs(f) * 12 + rng.uniform(-10, 12)) * u1
        path = flow_path(troot + np.array([0.0, f * 2.6 * u1]), t_ang + f * 0.075 + rng.uniform(-0.04, 0.04), L, 34,
                         bend=look.get('tail_bend', 0.004) + rng.uniform(-0.003, 0.003), wave=1.8, phase=k * 1.3, rng=rng)
        bristle_stroke(strokes, path, (19 - abs(f) * 2.2 + rng.uniform(-1, 1.5)) * u1, 1.0 * u1, rng, nb=34, lw=max(1, int(round(0.75 * s))),
                       dry=0.52, split=0.55, taper=0.8)
    # ---------- ひづめ：筆をトンと置いて 先へ払う ----------
    for kk in ('FL', 'FR', 'HL', 'HR'):
        Fk = S[kk]; z = 0.155 * Fk['z']
        co = Pj(Hm.v3(Fk['co'], z)); hf = Pj(Hm.v3(Fk['hf'], z))
        d_ = hf - co; dl = np.linalg.norm(d_) + 1e-9
        path = [co - d_ / dl * 3 * u1, hf + d_ / dl * 5 * u1]
        bristle_stroke(strokes, path, 8.5 * u1, 5.5 * u1, rng, nb=14, lw=max(1, int(round(0.8 * s))), dry=0.5, split=0.45, taper=1.0)
    ink = np.clip(np.maximum(ink, strokes), 0, 1)
    # 墨のしぶき（小さく少し）
    hvs = R['P']([Hm.v3(S[kk]['hf'], 0.155 * S[kk]['z']) for kk in ('FL', 'HL', 'HR')])[:, :2]
    for i in range(look.get('splash', 12)):
        hv = hvs[rng.integers(0, 3)]
        q = hv + np.array([rng.uniform(-34, 8), rng.uniform(-10, 10)]) * u1
        cv2.circle(ink, (int(q[0] * 16), int(q[1] * 16)), int(rng.uniform(0.5, 1.5) * u1 * 16), 1.0, -1, cv2.LINE_AA, shift=4)
    W1, H1 = W3 // s, H3 // s
    return np.clip(cv2.resize(ink, (W1, H1), interpolation=cv2.INTER_AREA), 0, 1)
