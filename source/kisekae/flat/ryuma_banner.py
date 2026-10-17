"""龍馬（780×320）第2版：雷雲の夜空と日輪の前で、前足を上げて立つ 銀のうろこの龍馬（一から作ったオリジナルの絵）
   - 体は3D（flat/ryuma_horse.py：青みがかった銀の金属に細かいうろこ・龍の頭（開いた口と牙・金の角・金に光る目）・
     のどと胸の象牙色の板・肩と腰の金の飾り板と赤い玉・金のひづめ）。左向きに立ち、顔を少しこちらへ向ける
   - たてがみ・ほおの毛・あごひげ・しっぽ・足もとの毛は2Dの銀白の毛（やわらかい房＋細いすじ）。うしろの毛は体にかくれる
   - 背景：墨色から紺へ、金の光・日輪・雲（下は雲の海）・雷（2本）・うしろへ流れる金の気流・火の粉・瑞雲・金の縁の線（第1版のまま）
   python3 flat/ryuma_banner.py <出力.webp>（sdfr がいる）"""
import sys, os, math, shutil
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
sys.path.insert(0, os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import style2d as S2
from style2d import frame_horse, save_webp
from h3d import Scene, nrm
import horse3d as Hm
from paint import fbm, warp, blur, smoothstep
from fire2d import Heat, flow_path, fire_color, aces, to_srgb, dust, sparks, GOLD_STOPS

# 銀白の毛の色（線形・明るいほど白く）
SILVER_STOPS = [(0.0, (0, 0, 0)), (0.22, (0.06, 0.07, 0.09)), (0.45, (0.30, 0.34, 0.40)), (0.7, (0.85, 0.92, 1.05)), (0.88, (1.7, 1.78, 1.9)), (1.0, (2.6, 2.65, 2.7))]
import ryuma_horse as RH

W, Hh = 780, 320
BOX = (150, 62, 540, 304)          # 体（角・ひげをのぞく）がちょうど入る箱
YAW = 26.0                         # 頭と首を こちらへ
AZIM, ELEV = 4.0, 2.0

GOLD = (1.0, 0.72, 0.30)
SCALE = (0.42, 0.50, 0.56)         # 青みがかった銀（つや消しの金属）


def render3d(tmp):
    pose = dict(RH.POSE)
    S2.TMP = tmp
    e, t = frame_horse(pose, BOX, W, Hh, facing='left', azim=AZIM, elev=ELEV)
    sc = Scene()
    sc.image(W, Hh, 2)
    sc.camera(e, t, 26)
    sc.bounce(1)
    # 環境：暗い夜。うしろ上から金の光（ふちの光）・上から青緑・下から炎の照り返し・カメラがわのやわらかい明かり
    sc.env((0.07, 0.11, 0.16), (0.045, 0.047, 0.050), (0.025, 0.017, 0.010), (0.002, 0.002, 0.002))
    sc.lobe((0.35, 0.45, 0.82), (1.3, 0.80, 0.26), 5.0)            # うしろの金（うろこの縁に映る）
    sc.lobe((-0.2, 0.9, -0.35), (0.55, 0.85, 1.05), 3.0)           # 上の青（うろこの面に映る）
    sc.lobe((0.0, -1.0, 0.0), (0.6, 0.30, 0.08), 3.0)              # 下の炎の照り返し
    sc.lobe((-0.9, 0.2, -0.3), (0.6, 0.40, 0.18), 10.0)            # 前（顔の方）の金
    sc.lobe((-0.1, 0.35, -0.93), (1.1, 1.1, 1.1), 4.0)             # カメラがわの明かり（銀に映る）
    sc.light((0.42, 0.66, -0.62), (2.0, 1.95, 1.9), 12, 1)         # 主光（手前の上から）
    sc.light((-0.55, 0.45, 0.70), (5.0, 3.0, 1.0), 10, 0)          # ふちの光（うしろの金）
    sc.light((0.15, -0.85, -0.5), (0.5, 0.28, 0.10), 8, 0)         # 下からの炎の照り返し
    S0 = Hm.skeleton(pose)
    th = pose['theta']
    piv2 = np.array([-0.60, 1.25])
    T = lambda p: Hm.rot2(p, piv2, th)
    Rw = RH.roty(YAW)
    nb = Hm.v3(T((0.52, 1.40)))
    # 素材：体は青みがかった銀の金属に うろこ（参考の像の色あい）。まわりの金と青緑の光を映す
    sc.mat(1, 0, SCALE, 0.50, 0, 0, 0.0)                           # 体：うろこ（つや消しの銀：まわりの光をやわらかく映す）
    ch, bu = T((0.66, 1.10)), T((-0.93, 1.30))
    sc.bump(1, 2, 0.038, 0.004, Hm.v3(ch), Hm.v3(bu - ch), (0, 0, 1), 0.28)
    sc.mat(2, 0, SCALE, 0.50, 0, 0, 0.0)                           # 首：うろこ（首にそって）
    a = Rw @ (Hm.v3(Hm.bez(S0['crest'], 0.1)) - nb) + nb
    b = Rw @ (Hm.v3(Hm.bez(S0['crest'], 0.95)) - nb) + nb
    sc.bump(2, 2, 0.032, 0.006, a, b - a, Rw @ np.array([0, 0, 1.0]), 0.16)
    sc.mat(8, 0, SCALE, 0.46, 0, 0, 0.0)                           # 頭：細かいうろこ（頭にそって）
    pl = Rw @ (Hm.v3(S0['poll']) - nb) + nb
    hd = Rw @ Hm.v3(Hm.adir(S0['head_ang']))
    sc.bump(8, 2, 0.018, 0.0035, pl, hd, Rw @ np.array([0, 0, 1.0]), 0.09)
    sc.mat(7, 0, (0.78, 0.62, 0.36), 0.32, 0, 0, 4.0)              # 角：古い金（少しくすんだ）
    sc.mat(3, 0, GOLD, 0.22, 0, 0, 0.0)                            # 飾り板：金（彫り模様）
    sc.bump(3, 3, 9.0, 0.022)
    sc.mat(6, 0, (0.80, 0.56, 0.24), 0.30, 0, 0, 6.0)              # ひづめ：濃い金
    sc.mat(5, 2, (1.0, 0.62, 0.16), 0.03, 2.2, 0.4)                # 目：中から金に光る
    sc.mat(4, 2, (0.95, 0.14, 0.10), 0.03, 0.9, 1.0)               # 飾り板の玉：赤
    sc.mat(9, 1, (0.86, 0.80, 0.66), 0.45, 0.0, 0.5, 3.0)          # 歯・のどの板：象牙
    sc.mat(10, 1, (0.22, 0.03, 0.03), 0.5, 0.0, 0.0, 0.0)          # 口の中：暗い赤
    sc.mat(11, 0, (0.62, 0.68, 0.72), 0.40, 0, 0, 0.0)             # ひれ・ひげ：明るい銀
    hs0 = Hm.HEAD_SCALE
    Hm.HEAD_SCALE = 1.30                                            # 頭は大きく（龍の頭）
    try:
        M = RH.build(sc, pose, yaw=YAW, mats=dict(body=1, neck=2, head=8, horn=7, hoof=6, eye=5, teeth=9, mouth=10, fin=11, plate=9, gold=3, gem=4))
    finally:
        Hm.HEAD_SCALE = hs0
    R = sc.render(os.path.join(tmp, 'ryuma'))
    P = lambda pts: sc.project(np.asarray(pts, float))[0][:, :2]
    marks = dict(
        crest=P(M['crest']), crest_near=P(M['crest_near']), crest_far=P(M['crest_far']), throat=P(M['throat']),
        poll=P([M['poll']])[0], eye=P([M['eye']])[0], eye_far=P([M['eye_far']])[0], muzzle=P([M['muzzle']])[0], jaw=P([M['jaw']])[0],
        tailhead=P([M['tailhead']])[0], croup=P([M['croup']])[0], withers=P([M['withers']])[0], back=P([M['back']])[0], loin=P([M['loin']])[0],
        hooves=P(M['hooves']), fetlocks=P(M['fetlocks']), horn_tips=P(M['horn_tips']), chest=P([M['chest']])[0],
        whisk_near=P(M['whiskers'][-1]), whisk_far=P(M['whiskers'][1]),
    )
    return R, marks


def compose(R, M, rng_seed=7):
    rgb, A = R['rgb'], np.clip(R['a'], 0, 1)
    yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
    rng = np.random.default_rng(rng_seed)
    crest, poll, tail = M['crest'], M['poll'], M['tailhead']
    cx, cy = M['withers']

    # ---------- 背景（線形） ----------
    t = (yy / Hh)[..., None]
    top = np.array([0.0025, 0.0045, 0.012]); mid = np.array([0.007, 0.010, 0.018]); bot = np.array([0.006, 0.006, 0.007])
    bg = np.where(t < .55, top + (mid - top) * (t / .55), mid + (bot - mid) * ((t - .55) / .45)).astype(np.float32)
    dist = np.sqrt(((xx - cx) * 0.9) ** 2 + ((yy - cy) * 1.1) ** 2)
    bg += np.exp(-dist / 260)[..., None] * np.array([0.030, 0.015, 0.004]) + np.exp(-dist / 110)[..., None] * np.array([0.05, 0.025, 0.006])
    # 日輪（うしろの大きな金の輪：うすい面と、細く光るふち）
    rx, ry = cx + 30, cy + 10
    rr = np.sqrt((xx - rx) ** 2 + (yy - ry) ** 2)
    disc = smoothstep(172, 160, rr)
    ring = np.exp(-((rr - 168) / 2.2) ** 2)
    bg += disc[..., None] * np.array([0.016, 0.009, 0.003]) + ring[..., None] * np.array([0.38, 0.25, 0.08]) + blur(ring, 6)[..., None] * np.array([0.14, 0.08, 0.025])
    # 雲（上は雷雲・下は雲の海）
    dxs = (fbm(Hh, W, 220, 4, seed=4) - .5) * 220
    dys = (fbm(Hh, W, 220, 4, seed=5) - .5) * 220
    n1 = warp(fbm(Hh, W, 160, 6, seed=3), dxs, dys)
    hi_cloud = smoothstep(.52, .92, n1) * smoothstep(.75, .15, yy / Hh)
    bg += hi_cloud[..., None] * np.array([0.026, 0.032, 0.050])
    sea = warp(fbm(Hh, W, 90, 6, seed=11), dxs * .5, dys * .5)
    sea_m = smoothstep(.36, .78, sea) * smoothstep(.52, .95, yy / Hh) + smoothstep(.84, 1.0, yy / Hh) * .6
    sea_lit = np.clip(np.gradient(blur(sea_m, 2.0), axis=0) * -14, 0, 1)                       # 上のふちが明るい
    bg += sea_m[..., None] * np.array([0.046, 0.050, 0.064]) + (sea_lit * sea_m)[..., None] * np.array([0.55, 0.30, 0.08])
    bg += (sea_m * np.exp(-dist / 240))[..., None] * np.array([0.20, 0.10, 0.025])

    # 雷（2本：うしろの空）：一本の本すじに、枝を2本
    def bolt(acc, p0, p1, w, inten=1.0, branches=((0.36, 0.6, 0.35), (0.62, -0.7, 0.3))):
        p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
        d = p1 - p0
        nrm_ = np.array([-d[1], d[0]]) / (np.linalg.norm(d) + 1e-9)
        n = 16
        pts = [p0 + d * (k / n) + nrm_ * rng.normal(0, 7) * math.sin(math.pi * k / n) ** .5 for k in range(n + 1)]
        pts[0], pts[-1] = p0, p1
        q = np.round(np.array(pts) * 16).astype(np.int32)
        cv2.polylines(acc, [q], False, float(inten), max(1, int(round(w))), cv2.LINE_AA, shift=4)
        for u, ang, L in branches:
            k = int(u * n)
            dv = d * L
            dv = np.array([dv[0] * math.cos(ang) - dv[1] * math.sin(ang), dv[0] * math.sin(ang) + dv[1] * math.cos(ang)])
            b0 = pts[k]
            bp = [b0 + dv * (m / 8) + nrm_ * rng.normal(0, 4) * math.sin(math.pi * m / 8) for m in range(9)]
            q = np.round(np.array(bp) * 16).astype(np.int32)
            cv2.polylines(acc, [q], False, float(inten * .55), max(1, int(round(w * .6))), cv2.LINE_AA, shift=4)

    la = np.zeros((Hh, W), np.float32)
    bolt(la, (668, -10), (598, 152), 1.8, inten=.9)
    bolt(la, (112, -6), (158, 112), 1.4, inten=.6, branches=((0.5, 0.7, 0.3),))
    lcol = np.array([0.55, 0.70, 1.0])
    bg += la[..., None] * lcol * 1.6 + blur(la, 3)[..., None] * lcol * 0.9 + blur(la, 14)[..., None] * lcol * 0.4 + blur(la, 40)[..., None] * lcol * 0.22
    # 瑞雲（金の細い線で描いた、うずまく雲：左下と右上）：うずを3つ、ゆるい弧でつないで、先に流れる尾
    def spiral(acc, c, r0, turns, w, val, flip=1, n=90):
        pts = []
        for k in range(n + 1):
            u = k / n
            a_ = u * turns * 2 * math.pi * flip + (math.pi if flip < 0 else 0)
            r = r0 * (1 - 0.84 * u)
            pts.append((c[0] + math.cos(a_) * r, c[1] + math.sin(a_) * r * 0.8))
        q = np.round(np.array(pts) * 16).astype(np.int32)
        cv2.polylines(acc, [q], False, float(val), max(1, int(round(w))), cv2.LINE_AA, shift=4)
        return pts[0]

    def cloud(acc, c, sx, sy, scale, val):
        """c＝いちばん大きいうずの中心。sx＝尾が流れる向き（±1）・sy＝上下（±1）"""
        heads = []
        for (dx, dy, r, flip) in ((0, 0, 40, 1), (52, 14, 27, -1), (-42, 18, 22, -1)):
            cc = (c[0] + dx * scale * sx, c[1] + dy * scale * sy)
            heads.append(spiral(acc, cc, r * scale, 1.25, 1.6, val, flip * sx))
        # うずをつなぐ弧（上のふち）と、流れる尾
        arc = [(c[0] + (-60 + 150 * u) * scale * sx, c[1] - (26 * math.sin(math.pi * u) + 8 * math.sin(3 * math.pi * u)) * scale * sy - 6 * scale * sy)
               for u in np.linspace(0, 1, 40)]
        q = np.round(np.array(arc) * 16).astype(np.int32)
        cv2.polylines(acc, [q], False, float(val * .8), 1, cv2.LINE_AA, shift=4)
        tail = [(c[0] + (80 + 70 * u) * scale * sx, c[1] + (18 - 8 * u + 5 * math.sin(2 * math.pi * u)) * scale * sy) for u in np.linspace(0, 1, 30)]
        q = np.round(np.array(tail) * 16).astype(np.int32)
        cv2.polylines(acc, [q], False, float(val * .7), 1, cv2.LINE_AA, shift=4)

    zu = np.zeros((Hh, W), np.float32)
    cloud(zu, (96, 258), 1, 1, 1.0, .75)
    cloud(zu, (690, 72), -1, -1, 0.9, .7)
    zcol = np.array([1.0, 0.76, 0.34])
    bg += zu[..., None] * zcol * 0.55 + blur(zu, 4)[..., None] * zcol * 0.25 + blur(zu, 16)[..., None] * zcol * 0.12
    # 金の気流（うしろへ流れる長い炎のすじ）
    sw = Heat(Hh, W, ss=1)
    for i in range(14):
        y0 = rng.uniform(70, 250)
        x0 = cx + rng.uniform(-80, 90)
        c = flow_path((x0, y0), math.radians(rng.uniform(-12, 10)), rng.uniform(220, 420), 40, rng, wave=1.3, phase=rng.uniform(0, 6),
                      turn=rng.uniform(-0.004, 0.004), curl=rng.uniform(-0.02, 0.02))
        sw.lock(c, rng.uniform(2.5, 6), rng.uniform(.3, .6), root_taper=.2, power=0.7)
    swh = blur(sw.result(turb=26, fine=4, seed=40, breakup=.3, up=0), 1.0)
    swirl = fire_color(np.clip(swh * .8, 0, 1), GOLD_STOPS) * 0.14
    bg += swirl + blur(swirl, 8) * 0.6 + blur(swirl, 30) * 0.3

    # ---------- 毛（たてがみ・ほおの毛・あごひげ・しっぽ・足もとの毛）：銀白の房 ----------
    # やわらかい房（Heat：量感）と、細いすじ（Hair.buf：毛の線）を別に作って重ねる → 煙ではなく「毛」に見せる
    class Hair:
        def __init__(self, ss=3):
            self.soft = Heat(Hh, W, ss=2)
            self.ss = ss
            self.buf = np.zeros((Hh * ss, W * ss), np.float32)

        def line(self, c, v, power):
            s_ = self.ss
            q = np.round(np.asarray(c, float) * s_ * 16).astype(np.int32)
            n = len(c)
            for k in range(n - 1):
                t = k / (n - 1)
                val = v * (1 - t) ** power * (0.45 + 0.55 * smoothstep(0.0, 0.12, t))
                cv2.line(self.buf, tuple(q[k]), tuple(q[k + 1]), float(val), 1, cv2.LINE_AA, shift=4)

        def lock(self, c, w0, peak, ns=8, spread=1.6, root_taper=0.08, power=1.0, soft=0.8):
            c = np.asarray(c, float)
            if soft > 0:
                self.soft.lock(c, w0, peak * soft, root_taper=root_taper, power=power)
            tang = np.gradient(c, axis=0)
            nn = np.stack([-tang[:, 1], tang[:, 0]], 1)
            nn /= np.linalg.norm(nn, axis=1, keepdims=True) + 1e-9
            L_ = len(c)
            for k in range(ns):
                off = rng.uniform(-1, 1) * w0 * 0.7
                sp = np.linspace(0, 1, L_) ** 1.3 * rng.uniform(-1, 1) * w0 * spread
                wob = np.sin(np.linspace(0, rng.uniform(3, 8), L_) + rng.uniform(0, 6)) * w0 * 0.25
                c2 = c + nn * (off + sp + wob)[:, None]
                cut = int(L_ * rng.uniform(.6, 1.0))
                self.line(c2[:cut], peak * rng.uniform(.5, 1.0), power)

        def result(self, turb, fine, seed, breakup):
            soft = self.soft.result(turb=turb, fine=fine, seed=seed, breakup=breakup, up=0)
            strands = cv2.resize(self.buf, (W, Hh), interpolation=cv2.INTER_AREA)
            return np.clip(soft, 0, 1.2), np.clip(strands, 0, 2.0)

    def hair(hr, pts, n, peak_rng, side_off, ang_rng, L_rng, w_rng, turn=(-0.004, 0.012), curl=0.02, t_rng=(0.0, 1.0), up=0.1, ns=8):
        L_all = len(pts)
        for i in range(n):
            t = t_rng[0] + (t_rng[1] - t_rng[0]) * (i + rng.random()) / n
            j = t * (L_all - 1); j0 = int(j); j1 = min(j0 + 1, L_all - 1)
            p = pts[j0] + (pts[j1] - pts[j0]) * (j - j0)
            p = p + np.array([rng.normal(0, 3), side_off * rng.uniform(.3, 1.0)])
            base_ang = math.radians(rng.uniform(*ang_rng))
            L = rng.uniform(*L_rng)
            c = flow_path(p, base_ang, L, 30, rng, wave=1.1, phase=rng.uniform(0, 6), turn=rng.uniform(*turn), curl=curl, rise=up)
            hr.lock(c, rng.uniform(*w_rng), rng.uniform(*peak_rng), ns=ns)

    SILVER = np.array([0.88, 0.94, 1.05])

    def colorize(soft, strands, gain=1.0):
        return fire_color(np.clip(soft * 0.9, 0, 1), SILVER_STOPS) * 0.40 * gain + strands[..., None] * SILVER * 1.9 * gain

    # うしろ（体にかくれる）：むこうがわのたてがみ・うなじの毛・しっぽの根元
    back = Hair()
    hair(back, M['crest_far'], 16, (.55, .9), -8, (-58, -18), (70, 150), (4, 8), t_rng=(0.0, 0.92))
    for i in range(9):                                                  # うなじ（角のうしろ）から うしろ上へ（頭のうしろ）
        p = M['poll'] + np.array([rng.uniform(-4, 12), rng.uniform(-4, 10)])
        c = flow_path(p, math.radians(rng.uniform(-70, -20)), rng.uniform(45, 95), 18, rng, wave=1.1, phase=rng.uniform(0, 6), curl=0.02, rise=0.1)
        back.lock(c, rng.uniform(3, 6), rng.uniform(.5, .85), ns=6)
    backh, backs = back.result(turb=8, fine=3, seed=10, breakup=.35)
    hair_back = colorize(backh, backs, 0.75)

    front = Hair()
    hair(front, M['crest_near'], 16, (.6, .95), 8, (-56, -14), (70, 150), (4, 8), t_rng=(0.0, 0.92))
    # 頭のまわりの毛（ほお・あごの下から うしろへ流れる：参考の像のように、頭を毛でかこむ）
    poll = M['poll']; eye = M['eye']; jaw = M['jaw']
    cheek = eye + (poll - eye) * 0.3 + np.array([14, 16])
    for i in range(14):                                                 # ほお（目のうしろ）から うしろ・下へ
        p = cheek + np.array([rng.uniform(-6, 12), rng.uniform(-12, 16)])
        c = flow_path(p, math.radians(rng.uniform(-25, 35)), rng.uniform(30, 75), 16, rng, wave=1.2, phase=rng.uniform(0, 6), curl=0.03, rise=0.05)
        front.lock(c, rng.uniform(2.5, 5), rng.uniform(.5, .85), ns=6)
    for i in range(6):                                                  # あごひげ（あご先から 下・うしろへ）
        p = jaw + np.array([rng.uniform(-4, 6), rng.uniform(-3, 4)])
        c = flow_path(p, math.radians(rng.uniform(40, 95)), rng.uniform(26, 55), 12, rng, wave=1.2, phase=rng.uniform(0, 6), curl=0.04)
        front.lock(c, rng.uniform(2, 4), rng.uniform(.5, .85), ns=5)
    tail = M['tailhead']
    for i in range(18):                                                 # しっぽ：根元から うしろ上へ、ゆれて下へ
        p = tail + rng.normal(0, 4, 2) + np.array([rng.uniform(0, 12), rng.uniform(-6, 6)])
        a = math.radians(rng.uniform(-62, -28))
        c = flow_path(p, a, rng.uniform(110, 200), 30, rng, wave=1.3, phase=rng.uniform(0, 6), turn=rng.uniform(0.018, 0.04), curl=0.01, rise=-0.1)
        front.lock(c, rng.uniform(4, 9), rng.uniform(.5, .9), ns=9, spread=2.0, root_taper=0.15, power=0.85)
    for (fx, fy) in M['fetlocks']:                                      # 足もとの毛（球節から うしろ下へ）
        for i in range(5):
            p = np.array([fx, fy]) + rng.normal(0, 3, 2)
            c = flow_path(p, math.radians(rng.uniform(15, 75)), rng.uniform(18, 40), 10, rng, wave=1.0, phase=rng.uniform(0, 6))
            front.lock(c, rng.uniform(3, 6), rng.uniform(.45, .8), ns=5)
    fronth, fronts = front.result(turb=8, fine=3, seed=20, breakup=.35)
    hair_front = colorize(fronth, fronts, 1.0)
    # 根元の金のにじみ（毛の根元が少し金に）
    root_glow = blur(fire_color(np.clip(fronth * 0.9, 0, 1), GOLD_STOPS) * 0.25, 6) + blur(fire_color(np.clip(backh * 0.9, 0, 1), GOLD_STOPS) * 0.2, 6)

    # ---------- 合成 ----------
    img = bg + hair_back + blur(hair_back, 10) * 0.18
    fl = blur(hair_front + hair_back, 24) * 0.35 + blur(swirl, 60) * 0.5
    # 体のふちの金の光（うしろ上からの光：法線がカメラに対して寝ている所）
    n = R['n']
    nv = np.clip(1 - np.abs(n[..., 2]), 0, 1) ** 2.6
    lr = np.clip(n[..., 0] * 0.45 + n[..., 1] * 0.62 + n[..., 2] * 0.64, 0, 1)
    rim = (nv * (0.35 + 0.65 * lr) * A).astype(np.float32)
    rim = blur(rim, 0.8)
    horse = rgb + fl * np.array([1.0, 0.8, 0.5]) * A[..., None] * 0.12 + rim[..., None] * np.array([1.0, 0.72, 0.30]) * 0.7
    img = img * (1 - A[..., None]) + horse
    img += hair_front + blur(hair_front, 6) * 0.15 + root_glow * 0.5
    # ひげ（銀の細いすじ：手前は体の上・むこうは体のうしろ）
    def strand(acc, pts, w0, w1, val):
        pts = np.asarray(pts, float)
        for k in range(len(pts) - 1):
            u = k / (len(pts) - 1)
            w = w0 + (w1 - w0) * u
            q = np.round(pts[k:k + 2] * 16).astype(np.int32)
            cv2.line(acc, tuple(q[0]), tuple(q[1]), float(val * (1 - 0.5 * u)), max(1, int(round(w))), cv2.LINE_AA, shift=4)
    wn, wf = np.zeros((Hh, W), np.float32), np.zeros((Hh, W), np.float32)
    strand(wn, M['whisk_near'], 1.4, 0.6, 0.45)
    strand(wf, M['whisk_far'], 1.6, 0.8, 0.6)
    wcol = np.array([0.95, 0.97, 1.0])
    img += (wf * (1 - A))[..., None] * wcol * 1.0 + blur(wf * (1 - A), 3)[..., None] * wcol * 0.4
    img += wn[..., None] * wcol * 1.1 + blur(wn, 3)[..., None] * wcol * 0.35 + blur(wn, 10)[..., None] * np.array([1.0, 0.8, 0.5]) * 0.15
    # 角の先の光
    for (ax, ay) in M['horn_tips']:
        g = np.exp(-((xx - ax) ** 2 + (yy - ay) ** 2) / (2 * 2.2 ** 2))
        img += g[..., None] * np.array([1.0, 0.78, 0.36]) * 0.9 + blur(g, 5)[..., None] * np.array([1.0, 0.7, 0.3]) * 0.5
    # 目の光
    for (ex, ey), r, col, k in ((M['eye'], 3.4, (1.0, 0.62, 0.16), 3.2), (M['eye_far'], 2.2, (1.0, 0.62, 0.16), 1.2)):
        g = np.exp(-((xx - ex) ** 2 + (yy - ey) ** 2) / (2 * r * r))
        img += g[..., None] * np.array(col) * k + blur(g, 7)[..., None] * np.array(col) * k * 0.6
    # 火の粉
    def dpos(r):
        if r.random() < 0.6:
            c0 = crest[r.integers(0, len(crest))]
            return c0[0] + r.normal(60, 170), c0[1] + r.normal(-30, 120)
        return r.uniform(0, W), r.uniform(0, Hh * .9)
    dd = dust(Hh, W, 150, rng, dpos, size=(0.4, 1.5), inten=(0.2, 1.8))
    img += dd[..., None] * np.array([1.0, 0.66, 0.24])
    spk = sparks(Hh, W, 14, rng, region=lambda r: (r.uniform(0, W), r.uniform(Hh * .05, Hh * .8)), streak=(1, -0.6), slen=(5, 12), inten=(0.15, 0.6))
    img += blur(spk, 0.6)[..., None] * np.array([1.0, 0.55, 0.15])

    # ---------- 仕上げ ----------
    lum = img.max(2)
    bl = img * smoothstep(1.2, 4.0, lum)[..., None]
    img += blur(bl, 9) * 0.2 + blur(bl, 36) * 0.15
    v = np.clip(1.10 - np.sqrt(((xx - W * .5) / (W * .78)) ** 2 + ((yy - Hh * .45) / (Hh * .95)) ** 2) * .55, .3, 1)[..., None]
    img = img * v
    out = to_srgb(aces(img))
    out = np.clip(out + (out - 0.5) * 0.10 * (1 - np.abs(out - 0.5) * 2), 0, 1)
    # 金の縁の線（細い二重）と、すみの雷文
    line = np.zeros((Hh, W), np.float32)
    cv2.rectangle(line, (7, 7), (W - 8, Hh - 8), 1.0, 1, cv2.LINE_AA)
    cv2.rectangle(line, (11, 11), (W - 12, Hh - 12), 0.55, 1, cv2.LINE_AA)
    mea = [(0, 0), (16, 0), (16, 16), (6, 16), (6, 6), (11, 6), (11, 11)]                     # 雷文（ひとつ）
    for (ox, oy, sx, sy) in ((16, 16, 1, 1), (W - 17, 16, -1, 1), (16, Hh - 17, 1, -1), (W - 17, Hh - 17, -1, -1)):
        q = np.round(np.array([(ox + sx * x, oy + sy * y) for x, y in mea]) * 16).astype(np.int32)
        cv2.polylines(line, [q], False, 0.9, 1, cv2.LINE_AA, shift=4)
    out = out * (1 - line[..., None] * 0.9) + np.array([0.93, 0.76, 0.36]) * (line[..., None] * 0.9)
    return np.clip(out, 0, 1).astype(np.float32)


if __name__ == '__main__':
    out = sys.argv[1]
    tmp = os.path.join(S2.TMP, f'ryuma{os.getpid()}')
    os.makedirs(tmp, exist_ok=True)
    try:
        R, M = render3d(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    img = compose(R, M)
    save_webp(img, out)
    print(out)
