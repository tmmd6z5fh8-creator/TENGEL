"""リアルな競走馬と騎手（3D・照明つき）：ナイター用
   3Dの馬（horse3d）＋3Dの形で作った騎手（勝負服・そで・ヘルメット・白いズボン・ブーツ・ゼッケン）を、
   照明の光で描く。黒い足先（球節から下）は、3Dの高さで色をかえる。たてがみ・しっぽは hair2d の毛
   形はすべて一から作ったオリジナル"""
import sys, os, math
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(K, 'r3d'))
sys.path.insert(0, K)
from style2d import *
from h3d import Scene, nrm, tonemap
import horse3d as Hm
from hair2d import HairBuf, guide

M_COAT, M_EYE, M_HOOF = 1, 5, 6
M_SILK, M_PANTS, M_HELMET, M_BOOT, M_CLOTH, M_SLEEVE = 7, 8, 9, 10, 11, 12


def lin(hexs):
    c = hexc(hexs)
    return tuple(float(x) for x in np.power(c, 2.2))


def jockey(sc, S, js=1.12, side_z=0.30):
    """前かがみの騎手（右向きの馬の上）"""
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
        sc.rbox(np.array([w[0] - 0.30, w[1] - 0.42, 0.29 * z]), (0.19, 0.13, 0.02), 0.03, k=0.02, mat=M_CLOTH)
        J[f'hand{z}'] = hd
        J[f'cloth{z}'] = np.array([w[0] - 0.30, w[1] - 0.42, 0.31 * z])
    return J


def render_real(pose, box, W, Hh, colors, azim=12, elev=4, ss=2, name='real', head_scale=1.06, fov=26):
    """colors: coat・silk・sleeve・helmet（'#RRGGBB'）。戻り値 R（rgb はトーンマップ前の光の量）"""
    Hm.HEAD_SCALE = head_scale
    e, t = frame_horse(pose, box, W, Hh, facing='right', azim=azim, elev=elev, fov=fov)
    sc = Scene()
    sc.image(W, Hh, ss)
    sc.camera(e, t, fov)
    sc.bounce(0)
    cam = nrm(np.asarray(e, float) - np.asarray(t, float))
    side = 1.0 if cam[2] >= 0 else -1.0                            # カメラがいる側（z）
    # 夜の空と、照明（手前の上・右上・うしろのふち）
    sc.env((0.010, 0.012, 0.030), (0.035, 0.035, 0.070), (0.070, 0.050, 0.032), (0.006, 0.006, 0.010))
    sc.light(nrm((-0.30, 0.80, 0.55 * side)), (2.6, 2.7, 3.0), 10, 1)
    sc.light(nrm((0.55, 0.65, 0.45 * side)), (1.3, 1.35, 1.5), 10, 0)
    sc.light(nrm((0.15, 0.45, -0.85 * side)), (2.2, 2.3, 2.7), 8, 0)
    sc.mat(M_COAT, 1, lin(colors['coat']), 0.42, 0.40, 0.10, 4.0)
    sc.mat(M_EYE, 1, (0.004, 0.003, 0.003), 0.06, 0.0, 0.0, 0.0)
    sc.mat(M_HOOF, 1, (0.018, 0.016, 0.014), 0.45, 0.2, 0.0, 0.0)
    sc.mat(M_SILK, 1, lin(colors['silk']), 0.30, 0.35, 0.35, 3.0)
    sc.mat(M_SLEEVE, 1, lin(colors['sleeve']), 0.30, 0.35, 0.35, 3.0)
    sc.mat(M_HELMET, 1, lin(colors['helmet']), 0.16, 0.35, 0.10, 3.0)
    sc.mat(M_PANTS, 1, (0.62, 0.62, 0.64), 0.60, 0.25, 0.10, 3.0)
    sc.mat(M_BOOT, 1, (0.012, 0.012, 0.014), 0.30, 0.30, 0.05, 3.0)
    sc.mat(M_CLOTH, 1, (0.70, 0.70, 0.72), 0.75, 0.2, 0.0, 3.0)
    S = Hm.build(sc, pose, mats=dict(body=M_COAT, neck=M_COAT, hoof=M_HOOF, eye=M_EYE, head=M_COAT))
    J = jockey(sc, S)
    R = sc.render(os.path.join(TMP, name))
    ts = np.linspace(0, 1, 40)
    P = lambda pts: sc.project(np.asarray(pts, float))[0]
    R['crest'] = P(np.c_[Hm.bez(S['crest'], ts), np.zeros(len(ts))])
    R['poll'] = P([Hm.v3(S['poll'])])[0]
    R['muzzle'] = P([Hm.head_pt(S, 0.56, -0.03)])[0]
    R['mouth'] = P([Hm.head_pt(S, 0.50, -0.10, 0.06 * side)])[0]
    R['tail'] = P([Hm.v3(p) for p in S['tail_pts']])
    e0, e1 = S['eyes']
    R['eye'] = P([e0 if np.dot(e0 - t, np.asarray(e, float) - t) > np.dot(e1 - t, np.asarray(e, float) - t) else e1])[0]
    R['hooves'] = P([Hm.v3(S[k]['hf'], 0.15 * S[k]['z']) for k in ('FL', 'FR', 'HL', 'HR')])
    R['hands'] = [P([J['hand1']])[0], P([J['hand-1']])[0]]
    R['cloth'] = P([J['cloth1'] if side > 0 else J['cloth-1']])[0]
    R['cloth_w'] = np.linalg.norm(P([J['cloth1'] + np.array([0.19, 0, 0])])[0] - R['cloth']) if side > 0 else \
        np.linalg.norm(P([J['cloth-1'] + np.array([0.19, 0, 0])])[0] - R['cloth'])
    R['S'], R['scene'], R['J'], R['side'] = S, sc, J, side
    R['ground_y'] = S['ground']
    return R


def finish(R, colors, seed=1, mane_len=1.0, tail_len=1.0):
    """光の量 → 色（トーンマップ）・黒い足先・たてがみ／しっぽ。戻り値 (rgb, alpha)"""
    Hh, W = R['a'].shape
    rgb = tonemap(R['rgb'], 1.15)
    a = np.clip(R['a'], 0, 1)
    m = np.round(R['m']).astype(int)
    # 黒い足先：足ごとに「ひざ（後ろ足は飛節）の少し下 → ひづめ」の3Dの線のそばの毛を黒っぽく
    P = world_pos(R)
    S = R['S']
    near = np.zeros(a.shape, np.float32)
    for k, top in (('FL', 'kn'), ('FR', 'kn'), ('HL', 'hk'), ('HR', 'hk')):
        F = S[k]
        zl = 0.155 * F['z'] * 0.92
        q0 = np.array([*(np.asarray(F[top]) + (np.asarray(F['ft']) - np.asarray(F[top])) * 0.25), zl])
        q1 = np.array([*np.asarray(F['hf']), zl])
        d = q1 - q0
        tt = np.clip(np.nansum((P - q0) * d, -1) / np.dot(d, d), 0, 1)
        dist = np.linalg.norm(P - (q0 + tt[..., None] * d), axis=-1)
        near = np.maximum(near, np.clip((0.115 - np.nan_to_num(dist, nan=9)) / 0.03, 0, 1))
    dark = ((m == M_COAT) | (m == M_HOOF)).astype(np.float32) * near
    lum = rgb.mean(-1, keepdims=True)
    blackleg = np.clip(lum * 0.45, 0, 1) * np.array([1.0, 0.95, 0.92])
    rgb = rgb * (1 - dark[..., None]) + blackleg * dark[..., None]
    # たてがみ・前髪・しっぽ（黒い毛・光が当たる毛先は少し明るい）
    rng = np.random.default_rng(seed)
    hb = HairBuf(Hh, W, ss=2)
    crest = np.asarray(R['crest'], float)
    nC = len(crest)
    for i in range(3, nC - 6, 2):
        p = crest[i]
        tg = crest[min(i + 1, nC - 1)] - crest[i - 1]
        up = math.atan2(tg[1], tg[0]) - math.pi / 2
        if math.cos(up) > 0.3:
            up += math.pi
        L = (18 + 14 * math.sin(i / nC * math.pi)) * mane_len
        g = guide(p, up - 0.6, L, 12, rng, lambda x, y, aa, t: (math.pi + 0.25 - aa) * 0.10, wave=1.2, phase=i)
        hb.lock(g, 14, rng, spread=2.6, clump=0.6, wmin=0.5, wmax=1.1, rimk=1.0)
    pp, mz = np.asarray(R['poll'], float), np.asarray(R['muzzle'], float)
    fd = (mz - pp) / np.linalg.norm(mz - pp)
    g = guide(pp + fd * 2, math.atan2(fd[1], fd[0]) - 0.9, 11, 8, rng, lambda x, y, aa, t: 0.02, wave=0.6)
    hb.lock(g, 10, rng, spread=1.8, clump=0.7, wmin=0.5, wmax=1.0)
    th_ = np.asarray(R['tail'][0], float)
    for k in range(9):
        g = guide(th_ + rng.normal(0, 1.2, 2), math.pi + 0.30 + (k - 4) * 0.07, (66 + rng.uniform(-10, 12)) * tail_len, 22, rng,
                  lambda x, y, aa, t: (math.pi + 0.15 - aa) * 0.06, wave=1.6, phase=k)
        hb.lock(g, 22, rng, spread=3.2, clump=0.55, wmin=0.6, wmax=1.3, rimk=1.0)
    cov, rimw, cnt = hb.result(k=0.55)
    hair_col = np.array([0.035, 0.026, 0.022]) + np.clip(rimw, 0, 1.5)[..., None] * np.array([0.30, 0.31, 0.36]) * 0.6
    rgb = rgb * (1 - cov[..., None]) + hair_col * cov[..., None]
    a = np.clip(a + cov * (1 - a), 0, 1)
    # 頭のベルト（鼻の上と、ほおを通って耳のうしろへ）・手綱（口 → 騎手の手）
    tack = np.zeros((Hh * 4, W * 4), np.float32)
    mo, ey, po = np.asarray(R['mouth'], float), np.asarray(R['eye'], float), np.asarray(R['poll'], float)
    nose = mz + (ey - mz) * 0.30
    perp = np.array([-fd[1], fd[0]])
    def L4(pts, w):
        cv2.polylines(tack, [(np.asarray(pts) * 4 * 16).astype(np.int32)], False, 1.0, w, cv2.LINE_AA, shift=4)
    L4([nose + perp * 5.5, nose - perp * 4.5], 6)                                   # 鼻のベルト
    L4([mo, (mo + po) / 2 + perp * 1.5, po + fd * 2], 5)                             # ほおのベルト
    hand = np.asarray(R['hands'][0], float)
    mid = (mo + hand) / 2 + np.array([0.0, 5.0])
    L4([(1 - u) ** 2 * mo + 2 * (1 - u) * u * mid + u ** 2 * hand for u in np.linspace(0, 1, 14)], 5)   # 手綱
    tack = cv2.resize(tack, (W, Hh), interpolation=cv2.INTER_AREA)
    rgb = rgb * (1 - tack[..., None] * 0.9) + np.array([0.05, 0.035, 0.03]) * tack[..., None] * 0.9
    a = np.clip(a + tack * (1 - a), 0, 1)
    return np.clip(rgb, 0, 1), a


def cloth_number(rgb, R, num):
    """ゼッケンに番号（黒）"""
    from PIL import Image, ImageDraw, ImageFont
    Hh, W = rgb.shape[:2]
    cx, cy = R['cloth']
    size = max(9, int(R['cloth_w'] * 0.95))
    F = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
    lay = Image.new('L', (W * 2, Hh * 2), 0)
    d = ImageDraw.Draw(lay)
    d.text((cx * 2, cy * 2), str(num), font=ImageFont.truetype(F, size * 2), fill=255, anchor='mm')
    t = np.asarray(lay.resize((W, Hh), Image.LANCZOS)).astype(np.float32) / 255
    t = t * (np.abs(np.round(R['m']) - M_CLOTH) < 0.5)
    return rgb * (1 - t[..., None] * 0.92) + np.array([0.03, 0.03, 0.035]) * t[..., None] * 0.92


if __name__ == '__main__':
    W, Hh = 780, 320
    pose = dict(theta=0.0, neck_rot=-36.0, head_ang=-32.0,
                fore=dict(L=[-100, -40, -30, -18], R=[-132, -28, -150, -170]),
                hind=dict(L=[-112, -152, -136, -156], R=[-56, -106, -76, -56]),
                tail=[-170, -158])
    cols = dict(coat='#5A2812', silk='#C8102E', sleeve='#F2F2F2', helmet='#C8102E')
    R = render_real(pose, (190, 40, 590, 300), W, Hh, cols, name='realtest')
    rgb, a = finish(R, cols)
    rgb = cloth_number(rgb, R, 7)
    bg = np.zeros((Hh, W, 3), np.float32) + np.array([0.08, 0.08, 0.14])
    out = bg * (1 - a[..., None]) + rgb * a[..., None]
    cv2.imwrite(sys.argv[1], cv2.cvtColor((np.clip(out, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
    print('ok side', R['side'])
