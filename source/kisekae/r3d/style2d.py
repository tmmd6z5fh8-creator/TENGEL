"""3Dの馬を、イラストの描き方に変える道具（アニメ塗り・影絵・線画・たてがみとしっぽ）
   すべて線形ではなく 0〜1 の sRGB の色で扱う（絵本・イラスト向け）"""
import os, sys, math
import numpy as np
import cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from h3d import Scene, nrm
import horse3d as H

TMP = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tmp')
os.makedirs(TMP, exist_ok=True)


def hexc(h):
    h = h.lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)], np.float32)


def render_horse(pose, eye, tgt, fov, W, H_, ss=1, name='h', extra=None, mats=None, lights=None):
    """馬を描いて、形のデータ（アルファ・法線・奥行き・素材・AO）と目印を返す"""
    sc = Scene()
    sc.image(W, H_, ss)
    eye = np.asarray(eye, float); tgt = np.asarray(tgt, float)
    sc.camera(eye, tgt, fov)
    sc.bounce(0)
    sc.env((0.5, 0.5, 0.5), (0.4, 0.4, 0.4), (0.2, 0.2, 0.2))
    for L in (lights or [((0.5, 0.8, 0.6), (2.0, 2.0, 2.0), 10, 1)]):
        sc.light(*L)
    sc.mat(1, 1, (0.6, 0.6, 0.6), 0.6)
    sc.mat(5, 1, (0.02, 0.02, 0.02), 0.1)
    sc.mat(6, 1, (0.3, 0.3, 0.3), 0.6)
    if mats:
        for m in mats:
            sc.mat(*m)
    S = H.build(sc, pose, mats=dict(body=1, neck=1, hoof=6, eye=5, head=1))
    if extra:
        extra(sc, S)
    R = sc.render(os.path.join(TMP, name))
    ts = np.linspace(0, 1, 40)
    crest = H.bez(S['crest'], ts)
    throat = H.bez(S['throat'], ts)
    P = lambda pts: sc.project(np.asarray(pts, float))[0]
    R['crest'] = P(np.c_[crest, np.zeros(len(ts))])
    R['crest_near'] = P(np.c_[crest, np.full(len(ts), 0.07)])
    R['throat'] = P(np.c_[throat, np.zeros(len(ts))])
    R['poll'] = P([H.v3(S['poll'])])[0]
    R['muzzle'] = P([H.head_pt(S, 0.56, -0.03)])[0]
    R['tail'] = P([H.v3(p) for p in S['tail_pts']])
    e0, e1 = S['eyes']
    R['eye'] = P([e0 if np.dot(e0 - tgt, np.asarray(eye, float) - tgt) > np.dot(e1 - tgt, np.asarray(eye, float) - tgt) else e1])[0]
    R['hooves'] = P([H.v3(S[k]['hf'], 0.15 * S[k]['z']) for k in ('FL', 'FR', 'HL', 'HR')])
    R['S'] = S
    R['scene'] = sc
    return R


def edges(R, depth_k=0.02, crease=0.55, width=2.0):
    """輪郭と、重なり・折れ目の線（0〜1）"""
    a = R['a']
    d = R['d'].copy()
    n = R['n']
    hit = d > 0
    big = np.where(hit, d, 1e3)
    sil = cv2.morphologyEx((a > 0.5).astype(np.float32), cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8))
    gx = np.abs(np.diff(big, axis=1, append=big[:, -1:]))
    gy = np.abs(np.diff(big, axis=0, append=big[-1:, :]))
    dd = ((gx > depth_k * big) | (gy > depth_k * big)) & hit
    nx = np.sum(n * np.roll(n, -1, 1), -1)
    ny = np.sum(n * np.roll(n, -1, 0), -1)
    cr = ((nx < crease) | (ny < crease)) & hit
    m = np.clip(sil + dd + cr, 0, 1).astype(np.float32)
    if width > 1:
        k = int(round(width))
        m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    return cv2.GaussianBlur(m, (3, 3), 0.6)


def cel(R, base, shade, light=(0.5, 0.75, 0.45), hi=None, bands=(0.12, 0.62), rim=None, ao_k=0.12, eye='#1A1410', hoof=None, smooth_div=55):
    """アニメ塗り：明るい面・影・（つや）の段"""
    n = R['n']
    L = nrm(light)
    l = np.sum(n * L, -1)
    # 光をなめらかにしてから段にする（小さな凸凹のまだらを消す）
    a_ = (R['a'] > 0.5).astype(np.float32)
    sm = max(2.0, n.shape[0] / smooth_div)
    l = blur(l * a_, sm) / np.maximum(blur(a_, sm), 1e-3)
    base, shade = hexc(base) if isinstance(base, str) else base, hexc(shade) if isinstance(shade, str) else shade
    t = 1 - np.clip((l - bands[0]) / 0.025, 0, 1)                      # 影（くっきり）
    col = base * (1 - t[..., None]) + shade * t[..., None]
    if hi is not None:
        h = np.clip((l - bands[1]) / 0.05, 0, 1)
        hc = hexc(hi) if isinstance(hi, str) else hi
        col = col * (1 - h[..., None] * 0.6) + hc * h[..., None] * 0.6
    if rim is not None:
        V = nrm(R['scene'].cam[0] - R['scene'].cam[1])
        rr = np.clip(1 - np.abs(np.sum(n * V, -1)), 0, 1) ** 4
        col = col + hexc(rim) * rr[..., None] * 0.6
    col = col * (1 - ao_k * (1 - R['ao']))[..., None]
    m = R['m']
    col[m == 5] = hexc(eye)
    if 'eye' in R:
        col = draw_eye(col, R, eye)
    if hoof:
        col[m == 6] = col[m == 6] * 0 + hexc(hoof) * (0.75 + 0.25 * np.clip(l[m == 6], 0, 1))[..., None]
    return np.clip(col, 0, 1)


def draw_eye(col, R, eye_col='#1A1410', k=0.075, hl=True):
    """見える側の目を、少し大きめのアーモンド形で描く（白いつや付き）"""
    ex, ey = R['eye']
    hl_ = np.linalg.norm(np.asarray(R['muzzle']) - np.asarray(R['poll']))
    r = max(1.6, hl_ * k)
    Hh, W = col.shape[:2]
    m = np.zeros((Hh * 4, W * 4), np.uint8)
    u = np.asarray(R['muzzle']) - np.asarray(R['poll']); u = u / (np.linalg.norm(u) + 1e-9)
    ang = math.degrees(math.atan2(u[1], u[0])) - 90
    cv2.ellipse(m, (int(ex * 64), int(ey * 64)), (int(r * 64), int(r * 0.72 * 64)), ang, 0, 360, 255, -1, cv2.LINE_AA, shift=4)
    e = cv2.resize(m, (W, Hh), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    e *= (R['a'] > 0.5)
    col = col * (1 - e[..., None]) + hexc(eye_col) * e[..., None]
    if hl:
        m2 = np.zeros_like(m)
        cv2.circle(m2, (int((ex - r * 0.25) * 64), int((ey - r * 0.3) * 64)), int(r * 0.32 * 64), 255, -1, cv2.LINE_AA, shift=4)
        d = cv2.resize(m2, (W, Hh), interpolation=cv2.INTER_AREA).astype(np.float32) / 255 * e
        col = col * (1 - d[..., None]) + d[..., None]
    return col


def over(dst, rgb, a):
    a = a[..., None] if a.ndim == 2 else a
    return dst * (1 - a) + rgb * a


def poly_aa(shape, polys, scale=4):
    """なめらかな多角形の塗り（0〜1）"""
    Hh, W = shape
    m = np.zeros((Hh * scale, W * scale), np.uint8)
    for p in polys:
        q = np.round(np.asarray(p) * scale * 16).astype(np.int32)
        cv2.fillPoly(m, [q], 255, cv2.LINE_AA, shift=4)
    return cv2.resize(m, (W, Hh), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0


def lock_poly(pts, w0, w1=0.5, taper=1.0):
    """線にそって太さが変わる房の形"""
    pts = np.asarray(pts, float)
    n = len(pts)
    tg = np.gradient(pts, axis=0)
    tg /= np.linalg.norm(tg, axis=1, keepdims=True) + 1e-9
    nr = np.stack([-tg[:, 1], tg[:, 0]], 1)
    t = np.linspace(0, 1, n)
    w = (w0 * (1 - t) ** taper + w1 * t) / 2
    L = pts + nr * w[:, None]
    Rr = pts - nr * w[:, None]
    return np.vstack([L, Rr[::-1]])


def flow(p, ang, L, n, wind=0.0, wind_ang=math.pi, curl=0.0, rng=None, wave=0.0, phase=0.0):
    pts = [np.array(p, float)]
    a = ang
    for k in range(n):
        d = math.atan2(math.sin(wind_ang - a), math.cos(wind_ang - a))
        a += d * wind + curl + wave * math.sin(k * 0.6 + phase) * 0.08 + (rng.normal(0, 0.02) if rng is not None else 0)
        pts.append(pts[-1] + np.array([math.cos(a), math.sin(a)]) * L / n)
    return np.array(pts)


def mane_tail(R, shape, color, shade, mode='flow', scale=1.0, seed=3, tail_len=1.0, mane_len=1.0, wind_ang=math.pi):
    """たてがみ・前髪・しっぽ（アニメ塗り向けのなめらかな房）。RGBA（0〜1）を返す"""
    rng = np.random.default_rng(seed)
    Hh, W = shape
    crest = R['crest']
    polys_a, polys_b = [], []
    nC = len(crest)
    for i in range(1, nC - 5, 2):
        p = crest[i]
        tg = crest[min(i + 1, nC - 1)] - crest[i - 1]
        out = math.atan2(tg[1], tg[0]) - math.pi / 2
        if math.cos(out) > 0.3:
            out += math.pi
        t = i / nC
        if mode == 'flow':                                   # 風になびく（走る・立ち上がる）
            L = (38 + 26 * math.sin(t * math.pi)) * scale * mane_len
            pts = flow(p, out + 0.3, L, 10, wind=0.32, wind_ang=wind_ang, rng=rng, wave=1.0, phase=i)
        else:                                                # 首にそって垂れる（立つ）
            L = (16 + 8 * math.sin(t * math.pi)) * scale * mane_len
            back = math.atan2(-tg[1], -tg[0])                   # 首すじを体の方へ
            pts = flow(p, back + 0.5 * (1 if math.sin(back) < 0 else -1), L, 8, wind=0.14, wind_ang=math.pi / 2, rng=rng)
        (polys_a if (i // 2) % 2 == 0 else polys_b).append(lock_poly(pts, 14 * scale, 1.0))
    # 前髪
    pp = R['poll']
    mz = np.asarray(R['muzzle']); fd = (mz - pp) / (np.linalg.norm(mz - pp) + 1e-9)
    for k in range(2):
        a0 = math.atan2(fd[1], fd[0]) + (k - 0.5) * 0.5
        pts = flow(pp + rng.normal(0, 1.5, 2), a0, 11 * scale, 6, wind=0.0)
        polys_a.append(lock_poly(pts, 7 * scale, 1.0))
    # しっぽ
    tl = R['tail']
    base_ang = math.atan2(*(tl[-1] - tl[0])[::-1])
    for k in range(5):
        a0 = base_ang + (k - 2) * 0.14
        if mode == 'flow':
            pts = flow(tl[0] + (tl[1] - tl[0]) * 0.3, a0, (70 + k * 6) * scale * tail_len, 12, wind=0.08, wind_ang=wind_ang, rng=rng, wave=1.2, phase=k)
        else:
            pts = flow(tl[0] + (tl[1] - tl[0]) * 0.3, a0, (64 + k * 5) * scale * tail_len, 12, wind=0.1, wind_ang=math.pi / 2, rng=rng, wave=0.8, phase=k)
        (polys_a if k % 2 == 0 else polys_b).append(lock_poly(pts, 18 * scale, 1.5))
    ma = poly_aa(shape, polys_a)
    mb = poly_aa(shape, polys_b)
    c1 = hexc(color) if isinstance(color, str) else color
    c2 = hexc(shade) if isinstance(shade, str) else shade
    rgb = c1 * ma[..., None] + c2 * (mb * (1 - ma))[..., None]
    a = np.clip(ma + mb, 0, 1)
    rgb = np.where(a[..., None] > 0, rgb / np.maximum(a, 1e-4)[..., None], 0)
    return rgb, a


def save_png(img, path, alpha=None):
    u8 = (np.clip(img, 0, 1) * 255 + .5).astype(np.uint8)
    if alpha is not None:
        a8 = (np.clip(alpha, 0, 1) * 255 + .5).astype(np.uint8)
        cv2.imwrite(path, cv2.cvtColor(np.dstack([u8, a8]), cv2.COLOR_RGBA2BGRA))
    else:
        cv2.imwrite(path, cv2.cvtColor(u8, cv2.COLOR_RGB2BGR))


def save_webp(img, path, q=88):
    u8 = (np.clip(img, 0, 1) * 255 + .5).astype(np.uint8)
    cv2.imwrite(path, cv2.cvtColor(u8, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_WEBP_QUALITY, q])


def grad_v(Hh, W, stops):
    """縦のグラデーション（stops=[(位置, '#色'), …]）"""
    y = np.linspace(0, 1, Hh)[:, None]
    xs = [s[0] for s in stops]
    out = np.zeros((Hh, W, 3), np.float32)
    for c in range(3):
        out[..., c] = np.interp(y, xs, [hexc(s[1])[c] for s in stops])
    return out


def soft_circle(Hh, W, cx, cy, r, feather=1.0):
    yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    return np.clip((r - d) / feather + 0.5, 0, 1)


def blur(img, s):
    if s <= 0:
        return img
    k = int(s * 3) * 2 + 1
    return cv2.GaussianBlur(img, (k, k), s)


def frame_horse(pose, box, W, H_, facing='left', azim=0.0, elev=4.0, fov=26.0, iters=3):
    """馬（体）が画像の box=(x0,y0,x1,y1) にちょうど入るカメラ（eye, tgt）を求める"""
    S = H.skeleton(pose)
    gy = S['ground']
    tgt = np.array([0.1, 1.25 + gy, 0.0])
    dist = 7.0
    side = -1.0 if facing == 'left' else 1.0
    a = math.radians(azim)
    e = math.radians(elev)
    dirv = nrm(np.array([math.sin(a) * math.cos(e), math.sin(e), side * math.cos(a) * math.cos(e)]))
    th = math.tan(math.radians(fov) / 2)
    q = 4
    for it in range(iters):
        eye = tgt + dirv * dist
        R = render_horse(pose, eye, tgt, fov, W // q, H_ // q, ss=1, name='frame')
        ys, xs = np.nonzero(R['a'] > 0.5)
        bx0, bx1, by0, by1 = xs.min() * q, (xs.max() + 1) * q, ys.min() * q, (ys.max() + 1) * q
        s = min((box[3] - box[1]) / (by1 - by0), (box[2] - box[0]) / (bx1 - bx0))
        dist /= s
        cx = W / 2 + ((bx0 + bx1) / 2 - W / 2) * s
        cy = H_ / 2 + ((by0 + by1) / 2 - H_ / 2) * s
        dx, dy = (box[0] + box[2]) / 2 - cx, (box[1] + box[3]) / 2 - cy
        wpp = 2 * dist * th / H_
        fw = -dirv
        rt = nrm(np.cross(fw, (0, 1, 0)))
        up = np.cross(rt, fw)
        tgt = tgt - rt * dx * wpp + up * dy * wpp
    return tgt + dirv * dist, tgt


def horse_illust(pose, box, W, H_, facing='left', azim=-12, elev=4, fov=26, body=('#FFFFFF', '#C8BEDA'), mane=('#E9E1EE', '#C9BCD5'),
                 line='#5E4E66', mane_line=None, mode='stand', light=None, bands=(0.18, 0.72), hi=None, hoof='#6A5A50', eye='#2A2030',
                 mane_scale=1.3, tail_len=1.0, mane_len=1.0, seed=5, name='h', line_w=2, ss=2, wind_ang=None, extra=None, post=None):
    """アニメ塗りの馬（たてがみ・しっぽ・輪郭つき）。(rgb, alpha, R) を返す"""
    e, t = frame_horse(pose, box, W, H_, facing=facing, azim=azim, elev=elev, fov=fov)
    R = render_horse(pose, e, t, fov, W, H_, ss=ss, name=name, extra=extra)
    if light is None:
        light = (0.45, 0.8, -0.5) if facing == 'left' else (0.45, 0.8, 0.5)
    rgb = cel(R, body[0], body[1], light=light, bands=bands, hi=hi, eye=eye, hoof=hoof)
    if post is not None:
        rgb = post(rgb, R)
    if wind_ang is None:
        wind_ang = 0.0 if facing == 'left' else math.pi
    hair, ha = mane_tail(R, (H_, W), mane[0], mane[1], mode=mode, scale=mane_scale, seed=seed, tail_len=tail_len, mane_len=mane_len, wind_ang=wind_ang)
    A = R['a']
    ln = edges(R, width=line_w) * np.clip(A, 0, 1)
    out = np.zeros((H_, W, 3), np.float32)
    a = np.zeros((H_, W), np.float32)
    out = over(out, rgb, A); a = np.maximum(a, A)
    out = over(out, hair, ha); a = np.clip(a + ha * (1 - a), 0, 1)
    out = over(out, hexc(line), ln * 0.9)
    hl = cv2.morphologyEx((ha > .5).astype(np.float32), cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8))
    out = over(out, hexc(mane_line or line), cv2.GaussianBlur(hl, (3, 3), .6) * 0.85)
    a = np.clip(a + cv2.GaussianBlur(hl, (3, 3), .6) * (1 - a), 0, 1)
    out = np.where(a[..., None] > 1e-4, out / np.maximum(a, 1e-4)[..., None], 0)
    return out, a, R


def place(img, rgb, a):
    return over(img, rgb, a)


def ground_shadow(img, R, k=0.2, w=150, h=9, dx=0):
    Hh, W = img.shape[:2]
    yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
    gy = max(p[1] for p in R['hooves']) + 3
    cx = (R['tail'][0][0] + R['poll'][0]) / 2 + dx
    m = np.exp(-(((xx - cx) / w) ** 2 + ((yy - gy) / h) ** 2))
    return img * (1 - k * m[..., None])


def world_pos(R):
    """奥行きから、画素ごとの世界の位置（ヒットしていない所は nan）"""
    sc = R['scene']
    eye, tgt, fov = sc.cam
    W, Hh = sc.size
    fw = nrm(tgt - eye); rt = nrm(np.cross(fw, (0, 1, 0))); up = np.cross(rt, fw)
    th = math.tan(math.radians(fov) / 2); asp = W / Hh
    yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
    nx = (2 * (xx + .5) / W - 1) * th * asp
    ny = (1 - 2 * (yy + .5) / Hh) * th
    rd = fw[None, None] + rt[None, None] * nx[..., None] + up[None, None] * ny[..., None]
    rd /= np.linalg.norm(rd, axis=-1, keepdims=True)
    d = R['d']
    p = eye[None, None] + rd * d[..., None]
    p[d <= 0] = np.nan
    return p


def leg_points(rgb, R, color, height=0.42, soft=0.06):
    """ひざから下（低いところ）の色を変える（黒い足・白い靴下）"""
    p = world_pos(R)
    gy = R['S']['ground']
    y = p[..., 1] - gy
    t = np.clip((height - y) / soft, 0, 1)
    t = np.nan_to_num(t)
    t *= (R['m'] != 6)
    c = hexc(color) if isinstance(color, str) else color
    return rgb * (1 - t[..., None]) + c * t[..., None] * (0.75 + 0.25 * (rgb.mean(-1, keepdims=True) / (rgb.max() + 1e-6)))


def jockey(R, shape, jacket='#FFD21F', pattern=None, pcol='#1A3FB8', cap='#E02424', breeches='#FFFFFF', boots='#1A1A1A',
           skin='#E8B48A', line='#2A2A2A', line_w=1.6, silhouette=None):
    """走る馬にまたがる騎手（前かがみ）。(rgb, alpha) を返す。pattern: None / 'diamond' / 'hoops' / 'check' / 'sash'"""
    S = R['S']
    sc = R['scene']
    th = R['S'].get('theta', 0.0)
    wx, wy = S['withers']
    P = lambda x, y, z: sc.project(np.array([[wx + x, wy + y, z]]))[0][0]
    hip = P(-0.42, 0.40, 0.0); sh = P(0.14, 0.58, 0.0); head = P(0.40, 0.64, 0.0)
    knee = P(0.02, 0.20, 0.30); foot = P(-0.22, -0.10, 0.30)
    elbow = P(0.12, 0.30, 0.24); hand = P(0.50, 0.14, 0.20)
    scale = np.linalg.norm(sh - hip) / 0.45 * 0.92
    polys = {}
    polys['thigh'] = [lock_poly(np.linspace(hip, knee, 6), 0.20 * scale, 0.15 * scale, 0.5)]
    polys['shin'] = [lock_poly(np.linspace(knee, foot, 6), 0.13 * scale, 0.11 * scale, 0.5)]
    polys['torso'] = [lock_poly(np.linspace(hip, sh, 8), 0.30 * scale, 0.26 * scale, 0.3)]
    polys['arm'] = [lock_poly(np.vstack([np.linspace(sh, elbow, 5), np.linspace(elbow, hand, 5)[1:]]), 0.11 * scale, 0.09 * scale, 0.3)]
    m = {k: poly_aa(shape, v) for k, v in polys.items()}
    yy, xx = np.mgrid[0:shape[0], 0:shape[1]].astype(np.float32)
    hr = 0.13 * scale
    helmet = np.clip((hr - np.sqrt((xx - head[0]) ** 2 + (yy - head[1]) ** 2)) / 0.8 + .5, 0, 1)
    face = np.clip((hr * 0.7 - np.sqrt((xx - head[0] - hr * 0.35) ** 2 + (yy - head[1] - hr * 0.35) ** 2)) / 0.8 + .5, 0, 1)
    rgb = np.zeros(shape + (3,), np.float32)
    a = np.zeros(shape, np.float32)
    if silhouette is not None:
        allm = np.clip(sum(m.values()) + helmet, 0, 1)
        return np.broadcast_to(hexc(silhouette), shape + (3,)).copy(), allm
    def lay(mask, col):
        nonlocal rgb, a
        rgb = over(rgb, hexc(col) if isinstance(col, str) else col, mask)
        a = np.clip(a + mask * (1 - a), 0, 1)
    lay(m['shin'], boots)
    lay(m['thigh'], breeches)
    jac = np.broadcast_to(hexc(jacket), shape + (3,)).copy()
    if pattern:
        d = sh - hip; d = d / (np.linalg.norm(d) + 1e-9)
        u = (xx - hip[0]) * d[0] + (yy - hip[1]) * d[1]
        v = -(xx - hip[0]) * d[1] + (yy - hip[1]) * d[0]
        cs = 0.12 * scale
        if pattern == 'diamond':
            pm = ((np.abs((u / cs) % 2 - 1) + np.abs((v / cs) % 2 - 1)) < 0.75)
        elif pattern == 'hoops':
            pm = ((u / cs) % 2) < 1
        elif pattern == 'check':
            pm = (((u / cs) // 1 + (v / cs) // 1) % 2) == 0
        else:
            pm = np.abs(u * 0.7 - v) < cs * 0.6
        jac = np.where(pm[..., None], hexc(pcol), jac)
    rgb = over(rgb, jac, m['torso']); a = np.clip(a + m['torso'] * (1 - a), 0, 1)
    rgb = over(rgb, jac, m['arm']); a = np.clip(a + m['arm'] * (1 - a), 0, 1)
    lay(helmet, cap)
    lay(face * (xx > head[0]), skin)
    # 輪郭
    edge = sum(cv2.morphologyEx((mm > .5).astype(np.float32), cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)) for mm in list(m.values()) + [helmet])
    edge = cv2.GaussianBlur(np.clip(edge, 0, 1), (3, 3), .6)
    rgb = over(rgb, hexc(line), edge * 0.85)
    a = np.clip(a + edge * 0.85 * (1 - a), 0, 1)
    return rgb, a
