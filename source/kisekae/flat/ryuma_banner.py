"""龍馬（780×320）第3版：金の双龍の額縁（アニメ調）。まん中は雷雲の夜空と金の日輪（一から作ったオリジナルの絵）
   - 額縁は flat/ryuma_frame.py（左右の上すみで向かい合う龍・体は左右のふちを下へうねる・前足の爪が下の横木をつかむ・
     上下のまん中に飾り）。龍は3Dで組み立てて法線からアニメ調に塗り、うろこ・背びれ・たてがみ・ひげは2D
   - 背景：墨色から紺へ、金の光・まん中の日輪（双龍がかこむ玉）・雲（下は雲の海）・雷・金の気流・火の粉・瑞雲（第1版の背景をまん中に寄せた）
   - 第2版までの龍馬（生きもの）は出さない（まさちゃん「龍馬は一回消して！」）。作り方は flat/ryuma_horse.py に残す
   python3 flat/ryuma_banner.py <出力.webp>（sdfr がいる）"""
import sys, os, math, shutil
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
sys.path.insert(0, os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import style2d as S2
from style2d import save_webp
from paint import fbm, warp, blur, smoothstep
from fire2d import Heat, flow_path, fire_color, aces, to_srgb, dust, sparks, GOLD_STOPS
import ryuma_frame as RF

W, Hh = 780, 320
RING = (390.0, 162.0, 118.0)        # 日輪（まん中の玉）：中心と半径


def background(rng_seed=7):
    """背景（sRGB 0〜1・780×320）：夜空・日輪・雲・雷・金の気流・火の粉・瑞雲"""
    yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
    rng = np.random.default_rng(rng_seed)
    cx, cy, rr0 = RING

    # ---------- 背景（線形） ----------
    t = (yy / Hh)[..., None]
    top = np.array([0.0025, 0.0045, 0.012]); mid = np.array([0.007, 0.010, 0.018]); bot = np.array([0.006, 0.006, 0.007])
    bg = np.where(t < .55, top + (mid - top) * (t / .55), mid + (bot - mid) * ((t - .55) / .45)).astype(np.float32)
    dist = np.sqrt(((xx - cx) * 0.9) ** 2 + ((yy - cy) * 1.1) ** 2)
    bg += np.exp(-dist / 260)[..., None] * np.array([0.030, 0.015, 0.004]) + np.exp(-dist / 110)[..., None] * np.array([0.05, 0.025, 0.006])
    # 日輪（まん中の大きな金の輪：うすい面と、細く光るふち）
    rr = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    disc = smoothstep(rr0 + 4, rr0 - 8, rr)
    ring = np.exp(-((rr - rr0) / 2.2) ** 2)
    bg += disc[..., None] * np.array([0.016, 0.009, 0.003]) + ring[..., None] * np.array([0.38, 0.25, 0.08]) + blur(ring, 6)[..., None] * np.array([0.14, 0.08, 0.025])
    bg += (disc * np.exp(-rr / 70))[..., None] * np.array([0.09, 0.05, 0.015])               # 玉の中のやわらかい光
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

    # 雷（2本：日輪の左右の上から）：一本の本すじに、枝を2本
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
    bolt(la, (248, 30), (300, 150), 1.6, inten=.8)
    bolt(la, (540, 30), (486, 128), 1.3, inten=.55, branches=((0.5, 0.7, 0.3),))
    lcol = np.array([0.55, 0.70, 1.0])
    bg += la[..., None] * lcol * 1.6 + blur(la, 3)[..., None] * lcol * 0.9 + blur(la, 14)[..., None] * lcol * 0.4 + blur(la, 40)[..., None] * lcol * 0.22

    # 瑞雲（金の細い線で描いた、うずまく雲：日輪の下の左右）：うずを3つ、ゆるい弧でつないで、先に流れる尾
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
        for (dx, dy, r, flip) in ((0, 0, 40, 1), (52, 14, 27, -1), (-42, 18, 22, -1)):
            cc = (c[0] + dx * scale * sx, c[1] + dy * scale * sy)
            spiral(acc, cc, r * scale, 1.25, 1.6, val, flip * sx)
        arc = [(c[0] + (-60 + 150 * u) * scale * sx, c[1] - (26 * math.sin(math.pi * u) + 8 * math.sin(3 * math.pi * u)) * scale * sy - 6 * scale * sy)
               for u in np.linspace(0, 1, 40)]
        q = np.round(np.array(arc) * 16).astype(np.int32)
        cv2.polylines(acc, [q], False, float(val * .8), 1, cv2.LINE_AA, shift=4)
        tail = [(c[0] + (80 + 70 * u) * scale * sx, c[1] + (18 - 8 * u + 5 * math.sin(2 * math.pi * u)) * scale * sy) for u in np.linspace(0, 1, 30)]
        q = np.round(np.array(tail) * 16).astype(np.int32)
        cv2.polylines(acc, [q], False, float(val * .7), 1, cv2.LINE_AA, shift=4)

    zu = np.zeros((Hh, W), np.float32)
    cloud(zu, (262, 246), -1, 1, 0.62, .75)
    cloud(zu, (518, 246), 1, 1, 0.62, .75)
    zcol = np.array([1.0, 0.76, 0.34])
    bg += zu[..., None] * zcol * 0.55 + blur(zu, 4)[..., None] * zcol * 0.25 + blur(zu, 16)[..., None] * zcol * 0.12
    # 金の気流（日輪のまわりを流れる長い炎のすじ）
    sw = Heat(Hh, W, ss=1)
    for i in range(14):
        y0 = rng.uniform(70, 250)
        x0 = cx + rng.uniform(-150, 60)
        c = flow_path((x0, y0), math.radians(rng.uniform(-12, 10)), rng.uniform(160, 300), 40, rng, wave=1.3, phase=rng.uniform(0, 6),
                      turn=rng.uniform(-0.004, 0.004), curl=rng.uniform(-0.02, 0.02))
        sw.lock(c, rng.uniform(2.5, 6), rng.uniform(.3, .6), root_taper=.2, power=0.7)
    swh = blur(sw.result(turb=26, fine=4, seed=40, breakup=.3, up=0), 1.0)
    swirl = fire_color(np.clip(swh * .8, 0, 1), GOLD_STOPS) * 0.14
    bg += swirl + blur(swirl, 8) * 0.6 + blur(swirl, 30) * 0.3
    # 火の粉
    def dpos(r):
        if r.random() < 0.6:
            a_ = r.uniform(0, 2 * math.pi); rad = rr0 * (0.6 + 0.6 * r.random())
            return cx + math.cos(a_) * rad * 1.3, cy + math.sin(a_) * rad
        return r.uniform(0, W), r.uniform(0, Hh * .9)
    dd = dust(Hh, W, 150, rng, dpos, size=(0.4, 1.5), inten=(0.2, 1.8))
    bg += dd[..., None] * np.array([1.0, 0.66, 0.24])
    spk = sparks(Hh, W, 14, rng, region=lambda r: (r.uniform(W * .25, W * .75), r.uniform(Hh * .1, Hh * .8)), streak=(1, -0.6), slen=(5, 12), inten=(0.15, 0.6))
    bg += blur(spk, 0.6)[..., None] * np.array([1.0, 0.55, 0.15])

    # ---------- 仕上げ（背景だけ） ----------
    img = bg
    lum = img.max(2)
    bl = img * smoothstep(1.2, 4.0, lum)[..., None]
    img += blur(bl, 9) * 0.2 + blur(bl, 36) * 0.15
    v = np.clip(1.10 - np.sqrt(((xx - W * .5) / (W * .78)) ** 2 + ((yy - Hh * .45) / (Hh * .95)) ** 2) * .55, .3, 1)[..., None]
    img = img * v
    out = to_srgb(aces(img))
    out = np.clip(out + (out - 0.5) * 0.10 * (1 - np.abs(out - 0.5) * 2), 0, 1)
    return out.astype(np.float32)


def compose(tmp, rng_seed=7):
    bg = background(rng_seed)
    out, _ = RF.frame(bg, np.random.default_rng(rng_seed), tmp)
    return out


if __name__ == '__main__':
    out = sys.argv[1]
    tmp = os.path.join(S2.TMP, f'ryuma{os.getpid()}')
    os.makedirs(tmp, exist_ok=True)
    try:
        img = compose(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    save_webp(img, out)
