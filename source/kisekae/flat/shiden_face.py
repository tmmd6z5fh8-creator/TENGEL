"""紫電（第4.69版）：リアルな 黒い 馬の 顔の ドアップ（動き つき・N コマ）
   まさちゃん「三枚目の馬の顔は動きをつけて長めにして！ リアルに！」
   3D の 馬（r3d：h3d＋horse3d の 首と 頭だけ）を sdfr で 光と つやまで 計算して 描き、2D で たてがみ・前髪・光る 目・毛なみ・火の粉を 重ねる。
   コマごとに：頭が 少し 上がって こちらを 向く・耳が うしろから 前へ 立つ・カメラが 目へ 寄る・目の 光が 強く なる・たてがみが なびく・火の粉が 上がる。
   出す 絵：sd_rf00〜sd_rf{N-1}（390×844 の 2倍・RGB）。shiden_cuts.build から 呼ぶ。
   ためす とき：python3 flat/shiden_face.py <出力フォルダ> [u …]（u＝0〜1：その コマだけ）"""
import os, sys, math, json
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
sys.path.insert(0, os.path.join(HERE, '..'))
from h3d import Scene, nrm
import horse3d as Hm
from hair2d import HairBuf, guide
from fire2d import aces, to_srgb, dust
from paint import fbm, blur, smoothstep

N = 12                                    # コマの 数
W2, H2 = 780, 1688


def ease(u):
    return u * u * (3 - 2 * u)


CAM0 = dict(ha=-38.0, ear=-12.0, side=1.0, u=0.18, v=0.04, dist=2.35, ex=0.50, ey=0.37)    # はじめ：横顔（頭 ぜんぶ）
CAM1 = dict(ha=-27.0, ear=22.0, side=1.0, u=0.42, v=0.00, dist=1.60, ex=0.47, ey=0.36)     # おわり：少し こちらを 向き 目へ 寄る（目の 画面の 場所 ex, ey）
FS = float(os.environ.get('FACE_SCALE', '1'))                                                  # ためす とき 0.5
FOV = 34.0


def aim(cam, eye, fov, W, H, sx, sy):
    """目が 画面の (sx, sy)（0〜1）に 来る ように カメラの 見る 点を きめる"""
    tgt = eye.copy()
    th = math.tan(math.radians(fov) / 2); asp = W / H
    for _ in range(30):
        fw = nrm(tgt - cam); rt = nrm(np.cross(fw, (0, 1, 0))); up = np.cross(rt, fw)
        d = eye - cam
        nx = (d @ rt) / (d @ fw) / (th * asp); ny = (d @ up) / (d @ fw) / th
        px, py = (nx + 1) / 2, (1 - ny) / 2
        D = np.linalg.norm(d)
        tgt = tgt - rt * ((sx - px) * 2 * th * asp * D * .8) + up * ((sy - py) * 2 * th * D * .8)
    return tgt


def setup(u, W=W2, H=H2):
    """コマ u（0〜1）の ポーズ・カメラ：頭が 上がる・耳が 前へ 立つ・カメラが 寄る"""
    e = ease(u)
    c = {k: CAM0[k] + (CAM1[k] - CAM0[k]) * e for k in CAM0}
    pose = dict(Hm.REAR)
    pose['head_ang'] = c['ha']
    pose['ear_rot'] = c['ear']
    tmp = Scene()
    S = Hm.build(tmp, pose, mats=dict(body=1, neck=1, hoof=6, eye=5, head=1))
    eye = np.array(S['eye'], float)
    U3, V3 = np.array(S['head_u'], float), np.array(S['head_v'], float)
    d = nrm(np.array([0, 0, 1.0]) * c['side'] + U3 * c['u'] + V3 * c['v'])
    cam = eye + d * c['dist']
    tgt = aim(cam, eye, FOV, W, H, c['ex'], c['ey'])
    return pose, S, cam, tgt, FOV


def render(u, prefix, W=None, H=None, ss=1):
    W = W or int(W2 * FS); H = H or int(H2 * FS)
    pose, S0, cam, tgt, fov = setup(u, W, H)
    g = smoothstep(0.08, 0.62, u)                # 目の 光の 強さ
    sc = Scene()
    sc.image(W, H, ss)
    sc.camera(cam, tgt, fov)
    sc.bounce(1)
    cd = nrm(cam - tgt)
    sc.env((0.006, 0.002, 0.012), (0.010, 0.004, 0.018), (0.002, 0.001, 0.004), (0.0008, 0.0003, 0.0014))
    sc.lobe(nrm(-cd + np.array([0.35, 0.55, 0.0])), (1.1, 0.28, 0.95), 6.0)     # うしろの 桃色の 光
    sc.lobe(nrm(np.array([-0.2, 1.0, -0.3])), (0.18, 0.16, 0.26), 8.0)          # 上の うすい 光
    sc.light(nrm(cd * 0.55 + np.array([-0.55, 0.75, 0.15])), (0.32, 0.28, 0.42), 10, 1)  # 前 左上：ごく よわい 光
    sc.light(nrm(-cd + np.array([0.45, 0.45, 0.0])), (6.5, 1.5, 4.8), 8, 0)     # うしろ 右上：桃色の ふち
    sc.light(nrm(-cd + np.array([-0.6, -0.15, 0.0])), (1.3, 1.9, 5.2), 8, 0)    # うしろ 左：青白い ふち
    sc.light(nrm(-cd * 0.6 + np.array([0.0, 1.0, 0.0])), (1.8, 1.6, 2.4), 8, 0)  # 上うしろ：白い ふち
    eye = np.array(S0['eye'], float)
    sc.plight(eye + cd * 0.05 + np.array([0, 0.01, 0]), (0.05 * g + 0.004, 0.022 * g + 0.001, 0.004 * g), 8, 0)   # 目の 光が まわりを てらす
    sc.mat(1, 1, (0.012, 0.009, 0.014), 0.42, 0.9, 0.35, 3.5)
    sc.mat(5, 1, (0.006, 0.003, 0.002), 0.06, 0.0, 0.3)
    sc.mat(6, 1, (0.02, 0.017, 0.015), 0.45, 0.3, 0.4)
    S = Hm.build(sc, pose, mats=dict(body=1, neck=1, hoof=6, eye=5, head=1))
    R = sc.render(prefix)
    ts = np.linspace(0, 1, 40)
    P = lambda pts: sc.project(np.asarray(pts, float))[0]
    crest = Hm.bez(S['crest'], ts)
    marks = dict(
        crest=P(np.c_[crest, np.full(len(ts), 0.02)]).tolist(),
        poll=P([Hm.v3(S['poll'], 0.0)])[0].tolist(),
        eye=P([S['eye']])[0].tolist(),
        muzzle=P([Hm.head_pt(S, 0.56, -0.03)])[0].tolist(),
        brow=P([Hm.head_pt(S, 0.13, 0.07, 0.085)])[0].tolist(),
        fore=P([Hm.head_pt(S, 0.02, 0.06, 0.0)])[0].tolist(),
    )
    return R, marks, g


def compose(R, M, u, g, seed=7, W=None, H=None):
    W = W or int(W2 * FS); H = H or int(H2 * FS)
    """3D の 絵に 背景・たてがみ・前髪・光る 目・毛なみ・火の粉を 重ねて 仕上げる → 0〜1 の sRGB"""
    rgb, A = R['rgb'], R['a']
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    S = W / 780.0
    ex, ey = M['eye']
    mz = np.array(M['muzzle']); pl = np.array(M['poll'])
    hd = mz - np.array([ex, ey]); hd = hd / (np.linalg.norm(hd) + 1e-6)          # 画面での 頭の 向き（目 → 鼻）
    # ---------- 背景：むらさきの 闇・右上から 桃色の もや・左下に 青い もや ----------
    t = (yy / H)[..., None]
    bg = np.array([0.004, 0.0015, 0.009]) * (1 - t) + np.array([0.0015, 0.0008, 0.004]) * t
    haze = fbm(H, W, 260 * S, 5, seed=seed + 1)
    back = np.exp(-(((xx - ex - 120 * S) / (W * .55)) ** 2 + ((yy - ey + 40 * S) / (H * .32)) ** 2)) * (0.55 + 0.7 * haze)   # 頭の うしろの 光
    pink = np.exp(-(((xx - W * 1.0) / (W * .7)) ** 2 + ((yy - H * .15) / (H * .4)) ** 2)) * (0.4 + 0.8 * haze)
    blue = np.exp(-(((xx - W * 0.05) / (W * .6)) ** 2 + ((yy - H * .85) / (H * .35)) ** 2)) * (0.4 + 0.7 * haze)
    bg = bg + back[..., None] * np.array([0.050, 0.012, 0.060]) + pink[..., None] * np.array([0.06, 0.010, 0.045]) + blue[..., None] * np.array([0.008, 0.012, 0.045])
    # 首と 胸は 闇に しずめる（頭だけ 光る：目から 鼻への 向きの だ円の 外を 暗く）
    hl = np.linalg.norm(mz - np.array([ex, ey]))
    nv = np.array([hd[1], -hd[0]])                                  # 頭の 上の 向き（画面）
    if nv[1] > 0:
        nv = -nv
    cxh, cyh = ex + hd[0] * hl * .42 + nv[0] * hl * .06, ey + hd[1] * hl * .42 + nv[1] * hl * .06
    pu = ((xx - cxh) * hd[0] + (yy - cyh) * hd[1]) / (hl * .9)
    pv = ((xx - cxh) * nv[0] + (yy - cyh) * nv[1])
    pv = np.where(pv > 0, pv / (hl * .5), -pv / (hl * .26))                # 上（ひたい・耳）は 広く・下（あご・のど）は せまく
    headm = 1 - smoothstep(.7, 1.15, np.sqrt(pu ** 2 + pv ** 2))
    rgb = rgb * (0.06 + 0.94 * headm)[..., None]
    img = bg * (1 - A[..., None]) + rgb
    smoke = smoothstep(.3, .75, fbm(H, W, 220 * S, 5, seed=seed + 9)) * smoothstep(H * .46, H * .9, yy + 60 * S * np.sin(xx / W * 3 + u * 2))
    img = img * (1 - smoke[..., None] * .85) + smoke[..., None] * .85 * np.array([0.012, 0.005, 0.020])
    # ---------- 毛なみ（頭の 向きに そった 細い すじ・明るい 所だけ 少し） ----------
    ang = math.atan2(hd[1], hd[0])
    big = int(math.hypot(W, H)) + 8
    rs = np.random.RandomState(seed + 3)
    tex = cv2.resize(rs.rand(big // 2, big // 22).astype(np.float32), (big, big), interpolation=cv2.INTER_CUBIC)
    Mr = cv2.getRotationMatrix2D((big / 2, big / 2), -math.degrees(ang), 1.0)
    tex = cv2.warpAffine(tex, Mr, (big, big), borderMode=cv2.BORDER_REFLECT)[(big - H) // 2:(big - H) // 2 + H, (big - W) // 2:(big - W) // 2 + W]
    lum = img.mean(-1)
    img = img * (1 + (tex - .5)[..., None] * 0.22 * smoothstep(0.004, 0.05, lum)[..., None] * A[..., None])
    # ---------- たてがみ（首すじから うしろ上へ なびく・うしろからの 光の ふち） ----------
    rng = np.random.default_rng(seed)
    hb = HairBuf(H, W, ss=2)
    crest = np.array(M['crest'])
    nC = len(crest)
    fs = fbm(H, W, 140 * S, 3, seed=seed + 5)
    wind = math.radians(-104) + 0.2 * math.sin(u * math.pi * 1.6)

    def flow_m(x, y, a, tt):
        d = math.atan2(math.sin(wind - a), math.cos(wind - a))
        return d * 0.07 + (fs[int(np.clip(y, 0, H - 1)), int(np.clip(x, 0, W - 1))] - .5) * 0.25

    for i in range(110):
        tt = (i + rng.random()) / 110
        k0 = 0.04 + tt * 0.9
        q = k0 * (nC - 1); a0 = int(q); a1 = min(a0 + 1, nC - 1)
        p = crest[a0] + (crest[a1] - crest[a0]) * (q - a0)
        tg = crest[a1] - crest[max(a0 - 1, 0)]
        out_ang = math.atan2(tg[1], tg[0]) - math.pi / 2
        if math.sin(out_ang) > 0.3:
            out_ang += math.pi
        L = rng.uniform(300, 620) * S * (0.7 + 0.5 * math.sin(tt * math.pi))
        gpts = guide(p + rng.normal(0, 4 * S, 2), out_ang + rng.normal(0, 0.35), L, 34, rng, flow_m, wave=rng.uniform(1.2, 2.4), phase=rng.uniform(0, 6) + u * 2.2)
        hb.lock(gpts, 46, rng, spread=rng.uniform(6, 13) * S, clump=0.55, wmin=0.45 * S, wmax=1.2 * S, rimk=1.0)
        hb.lock(gpts[:10], 26, rng, spread=7 * S, clump=0.3, wmin=0.7 * S, wmax=1.5 * S, rimk=0.05)
    # 前髪（耳の あいだから ひたいへ・目に かからない）
    for i in range(14):
        gpts = guide(pl + rng.normal(0, 6 * S, 2), wind + rng.normal(0.3, 0.3), rng.uniform(140, 260) * S, 18, rng,
                     flow_m, wave=1.2, phase=rng.uniform(0, 6) + u * 3)
        keep = np.hypot(gpts[:, 0] - ex, gpts[:, 1] - ey) > 85 * S
        cut = int(np.argmin(keep)) if not keep.all() else len(gpts)
        if cut > 4:
            hb.lock(gpts[:cut], 20, rng, spread=4 * S, clump=0.65, wmin=0.4 * S, wmax=1.0 * S, rimk=0.6)
    cov, rimw, cnt = hb.result(k=0.5)
    dens = blur(cov, 4 * S)
    rimI = np.clip(rimw * np.clip(1 - dens, 0, 1) ** 1.3 * 1.6, 0, 1.2)
    behind = np.clip(1 - A, 0, 1)
    outer = smoothstep(.2, .9, rimw) * behind                                  # 毛先（うしろの 光を すかす）
    hair_col = np.stack([0.003 + rimI * (0.30 * outer + 0.05), 0.0015 + rimI * (0.07 * outer + 0.02), 0.004 + rimI * (0.30 * outer + 0.06)], -1)
    img = img * (1 - cov[..., None]) + hair_col * cov[..., None]
    # ---------- 光る 目（アーモンド形の くぼみに 白 → 黄 → だいだい → 赤） ----------
    a_ = math.atan2(hd[1], hd[0]) * 0.5 - 0.2
    du = ((xx - ex) * math.cos(a_) + (yy - ey) * math.sin(a_)) / (34 * S)
    dv = (-(xx - ex) * math.sin(a_) + (yy - ey) * math.cos(a_)) / (21 * S)
    alm = np.clip(1 - (np.abs(du) ** 1.7 + np.abs(dv) ** 2.1), 0, 1)
    sock = smoothstep(0, .12, alm)
    img = img * (1 - sock[..., None] * 0.85) + np.array([0.012, 0.001, 0.001]) * sock[..., None] * 0.85
    rr = np.sqrt((xx - ex) ** 2 + (yy - ey) ** 2) / S
    orb = smoothstep(0, .3, alm)
    glow = (np.array([6.0, 5.2, 4.0]) * np.exp(-(rr / 9) ** 2)[..., None] + np.array([4.0, 2.2, 0.5]) * np.exp(-(rr / 17) ** 2)[..., None]
            + np.array([2.2, 0.6, 0.08]) * np.exp(-((rr - 22) / 6) ** 2)[..., None]) * orb[..., None]
    halo = np.array([1.0, 0.25, 0.04]) * np.exp(-(rr / 34) ** 1.4)[..., None] + np.array([0.12, 0.02, 0.05]) * np.exp(-(rr / 110) ** 1.2)[..., None]
    flare = np.exp(-(((yy - ey) / (3.0 * S)) ** 2)) * np.exp(-(np.abs(xx - ex) / (90 * S)) ** 1.3)        # 横の 短い 光の 筋
    img = img + (glow + halo) * (0.15 + 0.85 * g) + flare[..., None] * np.array([1.6, 0.8, 0.35]) * g * 0.6
    # ---------- 火の粉（下から 上へ・コマで 少しずつ 上がる） ----------
    rng2 = np.random.default_rng(seed + 11)
    pts = [(rng2.uniform(0, W), rng2.uniform(0, H)) for _ in range(140)]
    def pos(r):
        x, y = pts[pos.i % len(pts)]; pos.i += 1
        return x + 40 * S * math.sin(u * 4 + y * .01), (y - u * 420 * S) % H
    pos.i = 0
    emb = dust(H, W, 140, rng2, pos, size=(0.6 * S, 2.2 * S), inten=(0.3, 1.6))
    img = img + emb[..., None] * np.array([1.0, 0.35, 0.6]) * 0.6 * (1 - 0.8 * headm)[..., None]
    # ---------- 仕上げ：にじみ・周辺を 暗く・トーン・粒 ----------
    lm = img.max(2)
    bl = img * smoothstep(0.6, 2.5, lm)[..., None]
    img = img + blur(bl, 5 * S) * 0.3 + blur(bl, 22 * S) * 0.15
    v = np.clip(1.12 - np.sqrt(((xx - W * .45) / (W * .95)) ** 2 + ((yy - H * .42) / (H * .75)) ** 2) * .55, .35, 1)[..., None]
    out = to_srgb(aces(img * v * 2.2))
    out = np.clip(out + rng.normal(0, 0.008, out.shape[:2]).astype(np.float32)[..., None], 0, 1)
    return out


def build(out, n=N, us=None, SA=None):
    if SA is None:                                # shiden_cuts.build から 呼ぶ ときは 同じ LAY（shiden_art の モジュール）を もらう
        import shiden_art as SA
    tmp = os.path.join(out, '_tmp'); os.makedirs(tmp, exist_ok=True)
    names = []
    for i in range(n) if us is None else range(len(us)):
        u = (i / (n - 1)) if us is None else us[i]
        R, M, g = render(u, os.path.join(tmp, f'rf{i}'))
        img = compose(R, M, u, g)
        nm = f'sd_rf{i:02d}' if us is None else f'sd_rf_test{i}'
        if FS != 1:
            img = cv2.resize(img, (W2, H2), interpolation=cv2.INTER_CUBIC)
        SA.save_rgb(img, os.path.join(out, nm + '.webp'), q=80)
        if us is None:
            SA.put_lay(nm, 390, 844)
        names.append(nm)
        print('made', nm, flush=True)
    return names


if __name__ == '__main__':
    o = sys.argv[1]
    us = [float(x) for x in sys.argv[2:]] or None
    sys.path.insert(0, HERE)
    print(build(o, us=us))
