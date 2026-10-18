"""遊び心のある漫画の競走馬と騎手（勝負服のテーマ用）
   comic_rider（漫画の塗り）に、まんがらしい大げさな形と顔をのせる：
   - 馬：大きめの頭・首をまっすぐ前へのばし、前足は前へ・うしろ足はうしろへいっぱいにのばした「とぶような走り」。
     歯をくいしばった口・前をにらむ大きな目・ふくらんだ鼻の穴から「ふんっ」の白い息
   - 騎手：大きめの頭（ヘルメット）・低く前へかがみ、両手を首の前へつき出して手綱を押す。
     ゴーグルの奥のけわしい目・歯をくいしばった口・とぶ汗
   形はすべて一から作ったオリジナル。
   render_toon(...) → R、face_svg(R, ...) → 顔・息・汗の SVG（1倍の座標）"""
import sys, os, math
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from comic_rider import *


def jockey_t(sc, S, js=1.25, side_z=0.30, head_r=0.13):
    """低く前へかがんだ騎手（大きめの頭・両手を前へ）"""
    w = np.asarray(S['withers'], float)
    P3 = lambda y=0.0, x=0.0, z=0.0: np.array([w[0] + x * js, w[1] + y * js, z * js], float)
    J = {}
    J['pelvis'] = P3(0.31, -0.26); J['chest'] = P3(0.37, 0.12); J['neck'] = P3(0.40, 0.25); J['head'] = P3(0.45, 0.38)
    a, b = J['pelvis'], J['chest']
    sc.ell_ax((a + b) / 2, b - a, (np.linalg.norm(b - a) / 2 + 0.07 * js, 0.12 * js, 0.15 * js), up=(0, 1, 0), k=0.04, mat=M_SILK)
    sc.ell(a + np.array([0.02, -0.02, 0]) * js, (0.13 * js, 0.10 * js, 0.15 * js), k=0.05, mat=M_PANTS)
    sc.rcone(J['chest'], J['neck'], 0.07 * js, 0.055 * js, k=0.03, mat=M_SILK)
    sc.sph(J['head'], head_r * js, k=0.02, mat=M_HELMET)
    sc.ell(J['head'] + np.array([head_r * 0.92, -head_r * 0.28, 0]) * js, (head_r * 0.52 * js, head_r * 0.12 * js, head_r * 0.72 * js), k=0.01, mat=M_HELMET)
    for z in (1, -1):
        sh = P3(0.37, 0.12, 0.13 * z); el = P3(0.25, 0.30, 0.21 * z); hd = P3(0.17, 0.56, 0.11 * z)
        sc.rcone(sh, el, 0.052 * js, 0.044 * js, k=0.02, mat=M_SLEEVE)
        sc.rcone(el, hd, 0.042 * js, 0.034 * js, k=0.02, mat=M_SLEEVE)
        sc.sph(hd, 0.040 * js, k=0.01, mat=M_PANTS)
        hip = P3(0.29, -0.24, 0.12 * z); kn = P3(0.21, 0.06, side_z * z)
        an = P3(-0.12, -0.15, (side_z + 0.06) * z); toe = P3(-0.16, -0.03, (side_z + 0.07) * z)
        sc.rcone(hip, kn, 0.078 * js, 0.056 * js, k=0.03, mat=M_PANTS)
        sc.rcone(kn, an, 0.054 * js, 0.042 * js, k=0.02, mat=M_BOOT)
        sc.rcone(an, toe, 0.042 * js, 0.032 * js, k=0.01, mat=M_BOOT)
        J[f'hand{z}'] = hd; J[f'knee{z}'] = kn; J[f'ankle{z}'] = an
        J[f'arm{z}'] = (sh, el, hd)
    J['js'] = js
    J['head_r'] = head_r * js
    return J


def render_toon(pose, box, W, Hh, s=3, azim=18, elev=5, name='toon', head_scale=1.32, fov=26, js=1.25, head_r=0.13,
                key=(0.30, 0.80, 0.55), cam=None):
    """anime_rider.render_anime と同じ描き方で、騎手だけ jockey_t（大きめの頭・前へつき出す手）。
       cam：決めたカメラ (eye, tgt)（走るコマで いまの絵と同じカメラを使う）。なければ box に入るように決める。R['cam'] に入れる"""
    Hm.HEAD_SCALE = head_scale
    W3, H3 = W * s, Hh * s
    if cam is None:
        e, t = frame_horse(pose, tuple(v * s for v in box), W3, H3, facing='right', azim=azim, elev=elev, fov=fov)
    else:
        e, t = (np.asarray(v, float) for v in cam)
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
    J = jockey_t(sc, S, js, head_r=head_r)
    R = sc.render(os.path.join(TMP, name))
    ts = np.linspace(0, 1, 40)
    P = lambda pts: sc.project(np.asarray(pts, float))[0]
    R['crest'] = P(np.c_[Hm.bez(S['crest'], ts), np.zeros(len(ts))])
    R['poll'] = P([Hm.v3(S['poll'])])[0]
    R['muzzle'] = P([Hm.head_pt(S, 0.56, -0.03)])[0]
    R['mouth'] = P([Hm.head_pt(S, 0.50, -0.10, 0.06 * side)])[0]
    R['nostril'] = P([Hm.head_pt(S, 0.535, 0.022, 0.055 * side)])[0]
    R['chin'] = P([Hm.head_pt(S, 0.52, -0.105, 0.0)])[0]
    R['lip'] = P([Hm.head_pt(S, 0.585, -0.055, 0.0)])[0]
    R['tail'] = P([Hm.v3(p) for p in S['tail_pts']])
    e0, e1 = S['eyes']
    R['eye'] = P([e0 if np.dot(e0 - t, np.asarray(e, float) - t) > np.dot(e1 - t, np.asarray(e, float) - t) else e1])[0]
    R['hooves'] = P([Hm.v3(S[k]['hf'], 0.15 * S[k]['z']) for k in ('FL', 'FR', 'HL', 'HR')])
    R['hand_near'] = P([J['hand1'] if side > 0 else J['hand-1']])[0]
    hcen = P([J['head']])[0]
    R['jhead'] = hcen
    R['jhead_r'] = float(np.linalg.norm(P([J['head'] + np.array([0, J['head_r'], 0])])[0] - hcen))
    fwd2 = P([J['head'] + np.array([J['head_r'], 0, 0])])[0] - hcen
    R['jfwd'] = fwd2 / (np.linalg.norm(fwd2) + 1e-9)
    R['S'], R['scene'], R['J'], R['side'], R['Lk'], R['s'] = S, sc, J, side, Lk, s
    R['cam'] = (e, t)
    return R


def _f(v):
    return f'{v[0]:.2f} {v[1]:.2f}'


def cr_path(pts, closed=True):
    """点を通るなめらかな線（Catmull-Rom → 3次ベジェ）の SVG の d"""
    P = [np.asarray(p, float) for p in pts]
    n = len(P)
    if not closed:
        P = [P[0] * 2 - P[1]] + P + [P[-1] * 2 - P[-2]]
        d = 'M' + _f(P[1])
        for i in range(1, n):
            p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
            d += ' C' + _f(p1 + (p2 - p0) / 6) + ' ' + _f(p2 - (p3 - p1) / 6) + ' ' + _f(p2)
        return d
    d = 'M' + _f(P[0])
    for i in range(n):
        p0, p1, p2, p3 = P[(i - 1) % n], P[i], P[(i + 1) % n], P[(i + 2) % n]
        d += ' C' + _f(p1 + (p2 - p0) / 6) + ' ' + _f(p2 - (p3 - p1) / 6) + ' ' + _f(p2)
    return d + ' Z'


def wedge(p0, p1, w0, w1, bulge=0.0):
    """太さが w0 → w1 に変わる、少し曲がった線（くさび形）の d"""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    dv = p1 - p0
    L = np.linalg.norm(dv) + 1e-9
    nv = np.array([-dv[1], dv[0]]) / L
    m = (p0 + p1) / 2 + nv * bulge
    pts = [p0 + nv * w0 / 2, m + nv * (w0 + w1) / 4, p1 + nv * w1 / 2, p1 - nv * w1 / 2, m - nv * (w0 + w1) / 4, p0 - nv * w0 / 2]
    return cr_path(pts, closed=True)


INKS = '#15111A'


def face_svg(R):
    """顔（馬のにらむ目・歯をくいしばった口・鼻の息、騎手のゴーグル・歯・汗）の SVG の部品（1倍の座標）"""
    s = R['s']
    out = []
    # ---------- 馬 ----------
    poll, muz = np.asarray(R['poll'], float) / s, np.asarray(R['muzzle'], float) / s
    hl = np.linalg.norm(muz - poll)
    fd = (muz - poll) / hl
    pv = np.array([fd[1], -fd[0]])
    if pv[1] > 0:
        pv = -pv
    r = hl * 0.088
    E = np.asarray(R['eye'], float) / s - pv * 0.30 * r + fd * 0.10 * r       # 頭の上のふちから少しはなす
    Q = lambda a, b: E + fd * a * r + pv * b * r
    alm = [Q(-1.10, 0.10), Q(-0.35, 0.80), Q(0.62, 0.72), Q(1.22, 0.06), Q(0.45, -0.55), Q(-0.55, -0.46)]
    out.append(f"<defs><clipPath id='heye'><path d='{cr_path(alm)}'/></clipPath></defs>")
    out.append(f"<path d='{cr_path(alm)}' fill='#FFFFFF' stroke='{INKS}' stroke-width='1.0'/>")
    pc = Q(0.62, 0.12)
    out.append(f"<g clip-path='url(#heye)'><circle cx='{pc[0]:.2f}' cy='{pc[1]:.2f}' r='{0.30 * r:.2f}' fill='{INKS}'/>"
               f"<circle cx='{pc[0] - 0.10 * r:.2f}' cy='{pc[1] - 0.12 * r:.2f}' r='{0.09 * r:.2f}' fill='#FFFFFF'/></g>")
    out.append(f"<path d='{cr_path([Q(-1.40, 0.04), Q(-0.40, 0.92), Q(0.70, 0.84), Q(1.32, 0.04)], closed=False)}' fill='none' stroke='{INKS}' stroke-width='{max(1.4, 0.30 * r):.2f}' stroke-linecap='round'/>")
    out.append(f"<path d='{wedge(Q(-1.30, 1.30), Q(1.10, 0.86), 0.50 * r, 0.18 * r, bulge=0.10 * r)}' fill='{INKS}'/>")       # けわしい眉
    # 歯をくいしばった口（はみの所から鼻先の下へ）
    M = np.asarray(R['mouth'], float) / s
    Z = np.asarray(R['lip'], float) / s
    md = Z - M
    Lm = np.linalg.norm(md)
    md = md / (Lm + 1e-9)
    mp = np.array([md[1], -md[0]])
    if np.dot(mp, pv) < 0:
        mp = -mp
    M = M - md * 0.55 * Lm                                              # 口の角ははみより うしろ（大きく笑う口）
    Lm = Lm * 1.50
    Tt = lambda t, h: M + md * t * Lm + mp * h * Lm
    top = [Tt(t, 0.04 + 0.10 * t) for t in np.linspace(0.06, 0.95, 7)]
    bot = [Tt(t, -(0.035 + 0.085 * t)) for t in np.linspace(0.95, 0.06, 7)]
    out.append(f"<path d='{cr_path(top + bot)}' fill='#FFFFFF' stroke='{INKS}' stroke-width='1.1' stroke-linejoin='round'/>")
    out.append(f"<path d='{cr_path([Tt(t, 0.008 * math.sin(t * 6)) for t in np.linspace(0.07, 0.93, 6)], closed=False)}' fill='none' stroke='{INKS}' stroke-width='0.75'/>")
    for t in (0.26, 0.40, 0.54, 0.68, 0.82):
        out.append(f"<path d='M{_f(Tt(t, 0.035 + 0.095 * t))} L{_f(Tt(t + 0.01, -(0.03 + 0.08 * t)))}' stroke='{INKS}' stroke-width='0.6'/>")
    out.append(f"<path d='{cr_path([Tt(-0.10, 0.16), Tt(0.02, 0.02), Tt(-0.04, -0.12)], closed=False)}' fill='none' stroke='{INKS}' stroke-width='1.0' stroke-linecap='round'/>")
    M = np.asarray(R['mouth'], float) / s
    # はみの輪（口の上にもう一度）
    out.append(f"<circle cx='{M[0]:.2f}' cy='{M[1]:.2f}' r='{max(1.6, 0.045 * hl):.2f}' fill='none' stroke='{INKS}' stroke-width='{max(1.8, 0.05 * hl):.2f}'/>"
               f"<circle cx='{M[0]:.2f}' cy='{M[1]:.2f}' r='{max(1.6, 0.045 * hl):.2f}' fill='none' stroke='#FFD24A' stroke-width='{max(0.9, 0.025 * hl):.2f}'/>")
    # 鼻から ふんっ の息（前の下へ）
    N = np.asarray(R['nostril'], float) / s
    dS = fd * 0.95 - pv * 0.30
    dS = dS / np.linalg.norm(dS)
    for k, (dist, rad) in enumerate(((0.11, 0.042), (0.21, 0.056), (0.34, 0.070))):
        c = N + dS * dist * hl
        bl = []
        for j in range(3):
            a_ = j * 2.1 + k
            bl.append(f"<circle cx='{c[0] + math.cos(a_) * rad * hl * 0.55:.2f}' cy='{c[1] + math.sin(a_) * rad * hl * 0.55:.2f}' r='{rad * hl * 0.62:.2f}'/>")
        out.append(f"<g fill='#FFFFFF' stroke='{INKS}' stroke-width='0.9'>" + ''.join(bl) + "</g>")
        out.append(f"<g fill='#FFFFFF'>" + ''.join(b_.replace("/>", " stroke='none'/>") for b_ in bl) + "</g>")
    # ---------- 騎手 ----------
    C = np.asarray(R['jhead'], float) / s
    rr = R['jhead_r'] / s
    F = np.asarray(R['jfwd'], float)
    U = np.array([F[1], -F[0]])
    if U[1] > 0:
        U = -U
    G = lambda a, b: C + F * a * rr + U * b * rr
    # ゴーグルのバンド（ヘルメットのうしろへ）
    out.append(f"<path d='{cr_path([G(0.35, -0.30), G(-0.30, -0.22), G(-0.92, -0.34)], closed=False)}' fill='none' stroke='{INKS}' stroke-width='{0.30 * rr:.2f}' stroke-linecap='round'/>")
    lens = [G(0.30, -0.12), G(0.62, -0.08), G(0.95, -0.18), G(0.95, -0.48), G(0.62, -0.58), G(0.30, -0.52)]
    out.append(f"<path d='{cr_path(lens)}' fill='#BFE6FF' stroke='{INKS}' stroke-width='1.1'/>")
    out.append(f"<path d='{wedge(G(0.48, -0.30), G(0.86, -0.36), 0.20 * rr, 0.10 * rr)}' fill='{INKS}'/>")                 # けわしい目
    out.append(f"<path d='M{_f(G(0.40, -0.18))} L{_f(G(0.56, -0.15))}' stroke='#FFFFFF' stroke-width='{0.07 * rr + 0.4:.2f}' stroke-linecap='round'/>")
    # 鼻と、歯をくいしばった口
    out.append(f"<path d='{cr_path([G(0.93, -0.56), G(1.10, -0.70), G(0.94, -0.78)], closed=False)}' fill='none' stroke='{INKS}' stroke-width='0.9' stroke-linecap='round'/>")
    mouth = [G(0.42, -0.84), G(0.66, -0.80), G(0.86, -0.86), G(0.84, -1.04), G(0.62, -1.06), G(0.42, -1.00)]
    out.append(f"<path d='{cr_path(mouth)}' fill='#FFFFFF' stroke='{INKS}' stroke-width='1.0'/>")
    out.append(f"<path d='M{_f(G(0.44, -0.93))} L{_f(G(0.85, -0.95))}' stroke='{INKS}' stroke-width='0.6'/>")
    for a_ in (0.57, 0.71):
        out.append(f"<path d='M{_f(G(a_, -0.82))} L{_f(G(a_, -1.05))}' stroke='{INKS}' stroke-width='0.55'/>")
    # とぶ汗（ヘルメットのうしろ）
    for (a_, b_, sz, rot) in ((-1.20, 0.95, 0.30, 40), (-1.52, 0.40, 0.26, 62), (-1.38, -0.15, 0.22, 95)):
        p = G(a_, b_)
        h = sz * rr
        d = f"M{p[0]:.2f} {p[1] - h:.2f} C{p[0] + h * 0.7:.2f} {p[1] - h * 0.1:.2f} {p[0] + h * 0.55:.2f} {p[1] + h * 0.75:.2f} {p[0]:.2f} {p[1] + h * 0.75:.2f} " \
            f"C{p[0] - h * 0.55:.2f} {p[1] + h * 0.75:.2f} {p[0] - h * 0.7:.2f} {p[1] - h * 0.1:.2f} {p[0]:.2f} {p[1] - h:.2f} Z"
        out.append(f"<path d='{d}' fill='#9FDCFF' stroke='{INKS}' stroke-width='0.9' transform='rotate({rot} {p[0]:.2f} {p[1]:.2f})'/>")
    return out


if __name__ == '__main__':
    import json
    W, Hh = 780, 320
    pose = json.loads(sys.argv[2])
    box = tuple(json.loads(sys.argv[3]))
    azim = float(sys.argv[4]); hs = float(sys.argv[5]); js = float(sys.argv[6])
    hr = float(sys.argv[7]) if len(sys.argv) > 7 else 0.13
    R = render_toon(pose, box, W, Hh, s=3, azim=azim, elev=5, name='toontest', head_scale=hs, js=js, head_r=hr)
    rgb, a = paint_comic(R, dict(num=1, seed=5, eye=False, mouth=False))
    bg = np.zeros((Hh, W, 3), np.float32) + hexc('#DDE4F6')
    out = bg * (1 - a[..., None]) + rgb * a[..., None]
    from flat_horse import to_png
    svg = f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{Hh}' viewBox='0 0 {W} {Hh}'>" + ''.join(face_svg(R)) + "</svg>"
    tmp = os.path.join(TMP, 'toon_face.png')
    to_png(svg, W, Hh, tmp, scale=4)
    fx = cv2.imread(tmp, cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    fx = cv2.resize(fx, (W, Hh), interpolation=cv2.INTER_AREA)
    fa = fx[..., 3:4]
    out = out * (1 - fa) + fx[..., :3][..., ::-1] * fa
    cv2.imwrite(sys.argv[1], cv2.cvtColor((np.clip(out, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
    print('jhead', R['jhead'] / 3, R['jhead_r'] / 3, 'eye', np.asarray(R['eye']) / 3)
