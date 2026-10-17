"""龍馬（780×320）：雷雲の夜空を、金の炎をまとって天へかける黒い龍馬（一から作ったオリジナルの絵）
   - 体は3D（flat/ryuma_horse.py：黒い鉄のようなうろこの体・金の角とひげ・金のひづめ・ひたいの玉・首の金の輪）。
     左向きで跳び、顔を少しこちらへ向ける。目は金に光る
   - たてがみ・しっぽ・背すじ・足もと・前髪の炎は2D（r3d/fire2d.py の Heat：金の炎）。うしろの炎は体にかくれる
   - 背景：墨色から紺へ、金の光・雲（下は雲の海）・雷（2本）・うしろへ流れる金の気流・火の粉・金の縁の線
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
import ryuma_horse as RH

W, Hh = 780, 320
BOX = (150, 58, 540, 300)          # 体（角・ひげをのぞく）がちょうど入る箱
YAW = 22.0                         # 頭と首を こちらへ
AZIM, ELEV = 4.0, 2.0

GOLD = (1.0, 0.72, 0.30)
BODY = (0.022, 0.040, 0.038)       # 黒い鉄に、わずかな翠（金属：まわりの光をうすく映す）


def render3d(tmp):
    pose = dict(RH.POSE)
    S2.TMP = tmp
    e, t = frame_horse(pose, BOX, W, Hh, facing='left', azim=AZIM, elev=ELEV)
    sc = Scene()
    sc.image(W, Hh, 2)
    sc.camera(e, t, 26)
    sc.bounce(1)
    # 環境：暗い夜。うしろ上から金の光（ふちの光）・上から少し青緑・下から炎の照り返し
    sc.env((0.012, 0.020, 0.028), (0.008, 0.009, 0.009), (0.006, 0.004, 0.002), (0.001, 0.001, 0.001))
    sc.lobe((0.35, 0.45, 0.82), (1.5, 0.95, 0.32), 5.0)            # うしろの金（うろこの縁に映る）
    sc.lobe((-0.2, 0.9, -0.35), (0.28, 0.62, 0.70), 6.0)           # 上の青緑
    sc.lobe((0.0, -1.0, 0.0), (0.6, 0.30, 0.08), 3.0)              # 下の炎の照り返し
    sc.lobe((-0.9, 0.2, -0.3), (0.7, 0.42, 0.16), 10.0)            # 前（顔の方）の金
    sc.lobe((-0.1, 0.35, -0.93), (1.3, 1.0, 0.6), 4.0)             # カメラがわの明かり（金に映る）
    sc.light((0.42, 0.66, -0.62), (1.5, 1.4, 1.3), 12, 1)          # 主光（手前の上から）
    sc.light((-0.55, 0.45, 0.70), (5.0, 3.0, 1.0), 10, 0)          # ふちの光（うしろの金）
    sc.light((0.15, -0.85, -0.5), (0.5, 0.28, 0.10), 8, 0)         # 下からの炎の照り返し
    # 素材（体：黒い鉄のようなうろこ。金の光を映して、うろこの縁が光る）
    sc.mat(1, 0, BODY, 0.42, 0, 0, 0.0)                            # 体：うろこ
    S0 = Hm.skeleton(pose)
    th = pose['theta']
    piv2 = np.array([-0.60, 1.25])
    T = lambda p: Hm.rot2(p, piv2, th)
    ch, bu = T((0.66, 1.10)), T((-0.93, 1.30))
    sc.bump(1, 2, 0.060, 0.085, Hm.v3(ch), Hm.v3(bu - ch), (0, 0, 1), 0.28)
    sc.mat(2, 0, BODY, 0.42, 0, 0, 0.0)                            # 首：うろこ（首にそって）
    Rw = RH.roty(YAW)
    nb = Hm.v3(T((0.52, 1.40)))
    a = Rw @ (Hm.v3(Hm.bez(S0['crest'], 0.1)) - nb) + nb
    b = Rw @ (Hm.v3(Hm.bez(S0['crest'], 0.95)) - nb) + nb
    sc.bump(2, 2, 0.050, 0.050, a, b - a, Rw @ np.array([0, 0, 1.0]), 0.16)
    sc.mat(8, 0, BODY, 0.40, 0, 0, 0.0)                            # 頭：細かいうろこ（頭にそって）
    pl = Rw @ (Hm.v3(S0['poll']) - nb) + nb
    hd = Rw @ Hm.v3(Hm.adir(S0['head_ang']))
    sc.bump(8, 2, 0.024, 0.06, pl, hd, Rw @ np.array([0, 0, 1.0]), 0.09)
    sc.mat(7, 0, GOLD, 0.18, 0, 0, 0.0)                            # 金
    sc.mat(6, 0, (0.85, 0.56, 0.22), 0.30, 0, 0, 6.0)              # ひづめ：濃い金
    sc.mat(5, 2, (1.0, 0.62, 0.16), 0.03, 2.2, 0.4)                # 目：中から金に光る
    sc.mat(4, 2, (0.95, 0.14, 0.10), 0.03, 0.9, 1.0)               # ひたいの玉：赤
    M = RH.build(sc, pose, yaw=YAW, mats=dict(body=1, neck=2, head=8, hoof=6, eye=5, gold=7, gem=4))
    R = sc.render(os.path.join(tmp, 'ryuma'))
    P = lambda pts: sc.project(np.asarray(pts, float))[0][:, :2]
    marks = dict(
        crest=P(M['crest']), crest_near=P(M['crest_near']), crest_far=P(M['crest_far']), throat=P(M['throat']),
        poll=P([M['poll']])[0], eye=P([M['eye']])[0], eye_far=P([M['eye_far']])[0], muzzle=P([M['muzzle']])[0], gem=P([M['gem']])[0],
        tailhead=P([M['tailhead']])[0], croup=P([M['croup']])[0], withers=P([M['withers']])[0], back=P([M['back']])[0], loin=P([M['loin']])[0],
        hooves=P(M['hooves']), fetlocks=P(M['fetlocks']), antler_tips=P(M['antler_tips']), chest=P([M['chest']])[0],
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

    # ---------- 炎（たてがみ・しっぽ・背すじ・足もと） ----------
    def mane(heat, pts, n, peak_rng, side_off, ang_rng=(-84, -46), L_rng=(90, 210), w_rng=(6, 13), strands=3, up=0.3):
        pts = pts[:int(len(pts) * 0.8)]                                  # うなじの先（角のまわり）には出さない
        L_all = len(pts)
        for i in range(n):
            t = (i + rng.random()) / n
            j = t * (L_all - 1); j0 = int(j); j1 = min(j0 + 1, L_all - 1)
            p = pts[j0] + (pts[j1] - pts[j0]) * (j - j0)
            p = p + np.array([rng.normal(0, 3), side_off * rng.uniform(.3, 1.0)])
            base_ang = math.radians(rng.uniform(*ang_rng) + 16 * (1 - t))
            L = rng.uniform(*L_rng) * (1.05 - 0.4 * t)
            c = flow_path(p, base_ang, L, 30, rng, wave=1.2, phase=rng.uniform(0, 6), turn=rng.uniform(-0.004, 0.012), curl=0.03, rise=up)
            w0 = rng.uniform(*w_rng) * (1.05 - 0.35 * t)
            heat.lock(c, w0, rng.uniform(*peak_rng))
            tang = np.gradient(c, axis=0)
            nn = np.stack([-tang[:, 1], tang[:, 0]], 1)
            nn /= np.linalg.norm(nn, axis=1, keepdims=True) + 1e-9
            for k in range(strands):
                off = rng.uniform(-1, 1) * w0 * 0.7
                spread = np.linspace(0, 1, len(c)) ** 1.3 * rng.uniform(-1, 1) * w0 * 1.6
                wob = np.sin(np.linspace(0, rng.uniform(4, 9), len(c)) + rng.uniform(0, 6))[:, None] * w0 * 0.25
                c2 = c + nn * (off + spread)[:, None] + nn * wob
                cut = int(len(c2) * rng.uniform(.75, 1.0))
                heat.lock(c2[:cut], rng.uniform(1.6, 4.0), rng.uniform(.55, .95) * peak_rng[1], root_taper=.05, power=0.9)
            for k in range(2):
                j2 = int(len(c) * rng.uniform(.35, .6))
                c3 = flow_path(c[j2], math.atan2(*(c[j2] - c[j2 - 1])[::-1]) + rng.normal(0, .5), L * rng.uniform(.3, .55), 14, rng, wave=1.4,
                               phase=rng.uniform(0, 6), rise=.3)
                heat.lock(c3, w0 * rng.uniform(.2, .4), rng.uniform(.45, .75) * (1 - j2 / len(c)))

    back = Heat(Hh, W)
    mane(back, M['crest_far'], 14, (.68, 1.0), -8)
    # 背すじの小さな炎（き甲 → 腰：うしろ）
    spine = np.array([M['withers'], M['back'], M['loin'], M['croup']])
    for i in range(10):
        u = (i + rng.random()) / 10
        k = u * 3; k0 = int(k); p = spine[k0] + (spine[min(k0 + 1, 3)] - spine[k0]) * (k - k0)
        c = flow_path(p + np.array([0, -4]), math.radians(rng.uniform(-80, -40)), rng.uniform(40, 95), 14, rng, wave=1.2, phase=rng.uniform(0, 6), rise=.3)
        back.lock(c, rng.uniform(6, 11), rng.uniform(.5, .8))
    backh = back.result(turb=26, fine=9, seed=10, breakup=.6)
    fire_back = fire_color(np.clip(backh * 0.9, 0, 1), GOLD_STOPS) * 0.62

    front = Heat(Hh, W)
    mane(front, M['crest_near'], 10, (.62, .98), 8)
    for i in range(7):                                                  # 前髪（角のあいだから前上へ）
        p = poll + rng.normal(0, 4, 2)
        c = flow_path(p, math.radians(rng.uniform(-125, -80)), rng.uniform(36, 80), 16, rng, wave=1.1, phase=rng.uniform(0, 6), curl=0.03, rise=0.3)
        front.lock(c, rng.uniform(4, 8), rng.uniform(.5, .82))
    tdir = np.array([1.0, -0.25])
    for i in range(24):                                                 # しっぽ：うしろ上へ流れて、先は上へ巻く
        p = tail + rng.normal(0, 5, 2) + np.array([rng.uniform(0, 30), rng.uniform(-6, 10)])
        a = math.atan2(tdir[1], tdir[0]) + rng.normal(0, .3)
        c = flow_path(p, a, rng.uniform(150, 300), 30, rng, wave=1.4, phase=rng.uniform(0, 6), turn=rng.uniform(-0.03, -0.005), curl=-0.02, rise=0.35)
        front.lock(c, rng.uniform(6, 14), rng.uniform(.45, .78))
    for fx, fy in M['fetlocks']:                                        # 足もと（球節のまわり）
        for i in range(5):
            p = np.array([fx, fy]) + rng.normal(0, 4, 2)
            c = flow_path(p, math.radians(rng.uniform(-40, 30)), rng.uniform(26, 60), 10, rng, wave=1.0, phase=rng.uniform(0, 6), rise=.2)
            front.lock(c, rng.uniform(5, 9), rng.uniform(.4, .7))
    fronth = front.result(turb=26, fine=9, seed=20, breakup=.6)
    fire_front = fire_color(np.clip(fronth * 0.9, 0, 1), GOLD_STOPS) * 0.62

    # ---------- 合成 ----------
    img = bg + fire_back + blur(fire_back, 16) * 0.35
    fire_all = fire_back + fire_front + swirl * 0.5
    fl = blur(fire_all, 24) * 0.55 + blur(fire_all, 60) * 0.35
    # 体のふちの金の光（うしろ上からの光：法線がカメラに対して寝ている所）
    n = R['n']
    nv = np.clip(1 - np.abs(n[..., 2]), 0, 1) ** 2.6
    lr = np.clip(n[..., 0] * 0.45 + n[..., 1] * 0.62 + n[..., 2] * 0.64, 0, 1)
    rim = (nv * (0.35 + 0.65 * lr) * A).astype(np.float32)
    rim = blur(rim, 0.8)
    horse = rgb + fl * np.array([1.0, 0.72, 0.32]) * A[..., None] * 0.16 + rim[..., None] * np.array([1.0, 0.70, 0.28]) * 0.9
    horse += (A * (1 - rim))[..., None] * np.array([0.004, 0.009, 0.010])                       # 影の中にうすい青緑
    img = img * (1 - A[..., None]) + horse
    img += fire_front + blur(fire_front, 14) * 0.3 + blur(fire_front, 44) * 0.15 + blur(fire_back, 44) * 0.12
    # ひげ（金の細いすじ：手前は体の上・むこうは体のうしろ）
    def strand(acc, pts, w0, w1, val):
        pts = np.asarray(pts, float)
        for k in range(len(pts) - 1):
            u = k / (len(pts) - 1)
            w = w0 + (w1 - w0) * u
            q = np.round(pts[k:k + 2] * 16).astype(np.int32)
            cv2.line(acc, tuple(q[0]), tuple(q[1]), float(val * (1 - 0.5 * u)), max(1, int(round(w))), cv2.LINE_AA, shift=4)
    wn, wf = np.zeros((Hh, W), np.float32), np.zeros((Hh, W), np.float32)
    strand(wn, M['whisk_near'], 4.4, 1.2, 1.0)
    strand(wf, M['whisk_far'], 3.4, 1.0, 0.8)
    wcol = np.array([1.0, 0.74, 0.30])
    img += (wf * (1 - A))[..., None] * wcol * 1.6 + blur(wf * (1 - A), 3)[..., None] * wcol * 0.6
    img += wn[..., None] * wcol * 2.2 + blur(wn, 3)[..., None] * wcol * 0.9 + blur(wn, 10)[..., None] * wcol * 0.3
    # 角の先の光
    for (ax, ay) in M['antler_tips']:
        g = np.exp(-((xx - ax) ** 2 + (yy - ay) ** 2) / (2 * 2.2 ** 2))
        img += g[..., None] * np.array([1.0, 0.78, 0.36]) * 0.9 + blur(g, 5)[..., None] * np.array([1.0, 0.7, 0.3]) * 0.5
    # 目と玉の光
    for (ex, ey), r, col, k in ((M['eye'], 3.6, (1.0, 0.62, 0.16), 3.2), (M['gem'], 2.8, (1.0, 0.18, 0.08), 2.4),
                                (M['eye_far'], 2.4, (1.0, 0.62, 0.16), 1.2)):
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
