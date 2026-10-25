"""紫電（第4.69版）：鏡の 世界を 左から 右へ 切り裂く 馬の 蹄（ひづめ）
   まさちゃん「画面を切るのをコーンじゃなくて馬の蹄にして！」（見本の 写真は 黒い 馬の 足と 蹄：形の イメージだけ・写真は 使わない）
   3D の 黒い 馬の 前足の 下（管・球節・つなぎ・蹄・蹄鉄）を sdfr で 光と つやまで 計算して 描き、2D で 赤く 焼けた 蹄鉄の 光・毛なみ・
   球節の 毛の なびき・うしろへの ぶれ（速さ）を 重ねる。
   足は 左から のび、蹄の 裏（蹄鉄）が 右を 向く（前へ 打ちだす 形・つま先は 上）。少し 前から 見て 焼けた 蹄鉄の 輪が 見える。左の はしは ぶれて すき通る。
   切り口（黒い 裂け目）は 蹄の つま先（いちばん 上）から のびる：足は その 下なので 裂け目に かからない。
   出す 絵：sd_w_hoof（1280×588・すき通し・RGBA）。LAY に 表示の 大きさ（640×294）と 蹄の つま先（切り口の 裂け目が 出る 点）tip、見える 左の はし x0 を 入れる。
   ためす とき：python3 flat/shiden_hoof.py <出力フォルダ>"""
import os, sys, math
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
sys.path.insert(0, os.path.join(HERE, '..'))
from h3d import Scene, nrm
from hair2d import HairBuf, guide
from fire2d import aces, to_srgb
from paint import fbm, blur, smoothstep

W2, H2 = 1280, 588                       # 絵の 大きさ（表示は 半分：640×294）
TH = math.radians(28)                    # 蹄と つなぎの 軸の うしろへの かたむき（立った とき）
TANA = 0.09                              # 蹄の 広がり（下ほど 太い）
R0 = 0.056                               # 地面での 蹄の 太さ（半径）
HT = 0.064                               # 蹄の 高さ（軸に そって）
M_COAT, M_HOOF, M_BAND, M_SHOE, M_SOLE = 1, 2, 3, 4, 6


def Rw(p):
    """立った 足の 座標（x 前・y 上・z 横）→ 絵の 世界：90° 左回り（足の 下 → 右・つま先 → 上）"""
    p = np.asarray(p, float)
    return np.array([-p[1], p[0], p[2]])


RL = np.array([[0, 1.0, 0], [-1.0, 0, 0], [0, 0, 1.0]])   # 立った 座標の 軸（x・y・z）が 世界で どこを 向くか（行）＝ ell の 回転


def sole_outline(n=64):
    """地面（y=0）で 切った 蹄の ふち（立った 座標・つま先が φ=0）"""
    u = np.array([-math.sin(TH), math.cos(TH), 0.0])
    e1 = np.array([math.cos(TH), math.sin(TH), 0.0])
    e2 = np.array([0, 0, 1.0])
    pts = []
    for ph in np.linspace(-math.pi, math.pi, n, endpoint=False):
        c = math.cos(ph)
        s = -R0 * c * math.sin(TH) / (math.cos(TH) - TANA * c * math.sin(TH))
        r = R0 - s * TANA
        pts.append(u * s + r * (c * e1 + math.sin(ph) * e2))
    return np.array(pts), u, e1


def build(sc):
    """形を 出す（世界の 座標）。もどり値：だいじな 点（世界）"""
    out, u, e1 = sole_outline(96)
    g = np.zeros(3)
    U = lambda s: g + u * s
    # ---------- 蹄（ひづめ）：かたむいた 円すい台を 地面で 平らに 切る ----------
    sc.begin('U', 0.004, M_HOOF)
    a, b = U(-0.03), U(HT)
    sc.ccone(Rw(a), Rw(b), R0 + 0.03 * TANA, R0 - HT * TANA, rnd=0.006, side=Rw(e1), mat=M_HOOF)
    sc.rbox(Rw((0, -0.15, 0)), (0.15, 0.4, 0.4), 0.0, op='S', k=0.003, mat=M_HOOF)          # 地面で 切る（裏は 平ら）
    sc.end()
    cx0 = out[:, 0].mean()
    sc.ell(Rw((cx0, 0.0004, 0)), (0.058, 0.0016, 0.052), RL, k=0.002, mat=M_SOLE)                 # 裏（うすい 灰色）
    sc.begin('U', 0.003, M_SOLE)                                                           # 裏の かえる（つま先へ とがる V の ふくらみ）
    sc.ell(Rw((cx0 - 0.026, -0.0008, 0)), (0.046, 0.0055, 0.022), RL, mat=M_SOLE)
    sc.ell(Rw((cx0 - 0.04, -0.004, 0)), (0.03, 0.004, 0.0055), RL, op='S', k=0.002, mat=M_SOLE)
    sc.end()
    # ---------- 蹄鉄：裏の ふちに そった U の 形（かかとは あく） ----------
    sc.begin('U', 0.003, M_SHOE)
    n = len(out)
    first = True
    for inset, rr in ((0.0042, 0.0038), (0.0102, 0.004), (0.016, 0.0037)):
        P = []
        for i in range(n):
            ph = -math.pi + 2 * math.pi * i / n
            if abs(ph) > math.radians(140):
                continue
            q = out[i].copy()
            q2 = np.array([q[0], 0, q[2]])
            ctr = np.array([out[:, 0].mean(), 0, 0])
            d = q2 - ctr
            q2 = q2 - d / (np.linalg.norm(d) + 1e-9) * inset
            q2[1] = -0.0038
            P.append(q2)
        for p0, p1 in zip(P[:-1], P[1:]):
            sc.rcone(Rw(p0), Rw(p1), rr, rr, k=0.0 if first else 0.003, mat=M_SHOE)
            first = False
    sc.end()
    # ---------- 毛の 足：かんむり（毛の ふち）・つなぎ・球節・管・腱・かかと ----------
    ct = U(HT)
    f = U(HT + 0.105) + np.array([-0.004, 0.0, 0.0])
    sc.begin('U', 0.02, M_COAT)
    sc.ell(Rw(ct + u * 0.004), (R0 - HT * TANA + 0.003, 0.013, R0 - HT * TANA + 0.003), np.array([Rw(e1), Rw(u), Rw((0, 0, 1))]), mat=M_COAT)       # かんむり（蹄の 上の 毛の ふち）
    sc.rcone(Rw(ct + u * 0.01), Rw(f - u * 0.02), 0.041, 0.034, k=0.022, mat=M_COAT)                              # つなぎ（球節より 細い）
    sc.ell(Rw(f + np.array([-0.016, 0.0, 0])), (0.064, 0.052, 0.05), RL, k=0.022, mat=M_COAT)                       # 球節（まるい 関節）
    sc.ell(Rw(f + np.array([-0.058, -0.026, 0])), (0.02, 0.017, 0.017), RL, k=0.015, mat=M_COAT)                # けづめ（球節の うしろ）
    kn = f + np.array([0.012, 0.40, 0])
    sc.rcone(Rw(f + np.array([0.004, 0.035, 0])), Rw(kn), 0.031, 0.033, k=0.025, mat=M_COAT)                      # 管（骨）
    sc.rcone(Rw(f + np.array([-0.026, 0.045, 0])), Rw(kn + np.array([-0.028, -0.04, 0])), 0.022, 0.021, k=0.015, mat=M_COAT)   # 腱（うしろの すじ）
    for z in (1, -1):
        hb = U(0.058) + e1 * -0.04 + np.array([0, 0, 0.021 * z])
        sc.ell(Rw(hb), (0.024, 0.02, 0.021), RL, k=0.02, mat=M_COAT)                                          # かかと（ふくらみ）
    sc.end()
    sc.torus(Rw(ct + u * 0.003), Rw(u), R0 - HT * TANA + 0.001, 0.0042, k=0.004, mat=M_BAND)                  # 蹄の 上の 毛の ふち（明るい すじ）
    toe = out[np.argmin(np.abs(np.arctan2(out[:, 2], out[:, 0] - out[:, 0].mean())))]
    return dict(sole=Rw(np.array([out[:, 0].mean(), -0.012, 0])), toe=Rw(toe), fet=Rw(f), knee=Rw(kn), crown=Rw(ct),
                ergot=Rw(f + np.array([-0.06, -0.026, 0])), ax=Rw(u), e1=Rw(e1), outline=np.array([Rw(np.array([p[0], -0.012, p[2]])) for p in out]))


CAM = dict(az=float(os.environ.get('HOOF_AZ', '24')), el=float(os.environ.get('HOOF_EL', '6')), dist=1.24, fov=14.3)   # 少し 前から（蹄の 横顔と 焼けた 蹄鉄の 輪が 見える：まさちゃん「蹄こっちの角度の方がいい！」）


def camera(K):
    tgt = K['sole'] + np.array([-0.24, -0.042, 0.0])
    a, e = math.radians(CAM['az']), math.radians(CAM['el'])
    d = np.array([math.sin(a) * math.cos(e), math.sin(e), math.cos(a) * math.cos(e)])
    return tgt + d * CAM['dist'], tgt


def render(prefix, W=W2, H=H2, ss=2):
    tmp = Scene()
    K = build(tmp)
    cam, tgt = camera(K)
    sc = Scene()
    sc.image(W, H, ss)
    sc.camera(cam, tgt, CAM['fov'])
    sc.bounce(1)
    cd = nrm(cam - tgt)
    sc.env((0.010, 0.004, 0.018), (0.012, 0.005, 0.020), (0.004, 0.001, 0.006), (0.001, 0.0005, 0.002))
    sc.lobe(nrm(np.array([-0.2, 0.9, -0.4])), (0.5, 0.25, 0.5), 6.0)            # 上うしろ：桃色
    sc.lobe(nrm(np.array([0.2, -0.8, -0.3])), (0.15, 0.25, 0.8), 6.0)           # 下うしろ：青
    sc.lobe(nrm(cd + np.array([0.0, 0.5, 0.0])), (0.25, 0.22, 0.3), 10.0)       # 前：うすい 白
    sc.light(nrm(cd * 0.7 + np.array([-0.3, 0.9, 0.0])), (2.4, 2.4, 2.8), 10, 0)        # 前 上：つやの 白い 光
    sc.light(nrm(-cd + np.array([0.0, 0.9, 0.0])), (1.5, 0.85, 1.6), 8, 0)               # うしろ 上：うす桃色の ふち
    sc.light(nrm(-cd + np.array([0.3, -0.8, 0.0])), (0.9, 1.4, 3.4), 8, 0)               # うしろ 下：青白い ふち
    sc.plight(K['sole'] + np.array([0.06, 0.0, 0.02]), (0.020, 0.0045, 0.0012), 8, 0)    # 焼けた 蹄鉄の 赤い 光
    sc.mat(M_COAT, 1, (0.010, 0.009, 0.011), 0.36, 0.6, 0.25, 5.0)
    sc.mat(M_HOOF, 1, (0.14, 0.13, 0.135), 0.34, 0.5, 0.25, 3.0)
    sc.bump(M_HOOF, 4, 300.0, 0.00011, o=(0, 0, 0), ax=K['e1'], rx=(0, 0, 1), rad=0.2)
    sc.mat(M_BAND, 1, (0.17, 0.16, 0.155), 0.8, 0.3, 0.2, 3.0)
    sc.mat(M_SHOE, 0, (0.62, 0.56, 0.56), 0.28)
    sc.mat(M_SOLE, 1, (0.07, 0.062, 0.058), 0.6, 0.2, 0.1, 3.0)
    build(sc)
    R = sc.render(prefix)
    P = lambda pts: sc.project(np.atleast_2d(np.asarray(pts, float)))[0]
    marks = {k: P(v).tolist() for k, v in K.items() if k not in ('ax', 'e1')}
    return R, marks


def compose(R, M, W=W2, H=H2, seed=5):
    """3D の 絵に 焼けた 蹄鉄の 光・毛なみ・毛の なびき・ぶれを 重ねる → 前もって かけた RGBA（0〜1）"""
    rgb, A, mid = R['rgb'], R['a'], R['m']
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    S = W / 960.0
    shoe = (np.abs(mid - M_SHOE) < .5).astype(np.float32) * A
    shoe = cv2.GaussianBlur(shoe, (0, 0), .6)
    # ---------- 毛なみ（足の 向き＝横に そった 細い すじ） ----------
    rs = np.random.RandomState(seed)
    tex = cv2.resize(rs.rand(H // 18 + 2, W // 2).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    coat = (np.abs(mid - M_COAT) < .5).astype(np.float32)
    lum = rgb.mean(-1)
    rgb = rgb * (1 + (tex - .5)[..., None] * 0.5 * (coat * smoothstep(0.004, 0.06, lum))[..., None])
    # 蹄の 色むら（縦の すじ・少し 明るい 所と 暗い 所）
    hoofm = (np.abs(mid - M_HOOF) < .5).astype(np.float32)
    ax = np.array(M['crown'][0]) - np.array(M['toe'][0])
    ang = math.degrees(math.atan2(ax[1], ax[0]))
    big = int(math.hypot(W, H)) + 8
    t2 = cv2.resize(rs.rand(big // 7, big // 60 + 2).astype(np.float32), (big, big), interpolation=cv2.INTER_CUBIC)
    t2 = cv2.warpAffine(t2, cv2.getRotationMatrix2D((big / 2, big / 2), ang - 90, 1.0), (big, big), borderMode=cv2.BORDER_REFLECT)
    t2 = t2[(big - H) // 2:(big - H) // 2 + H, (big - W) // 2:(big - W) // 2 + W]
    rgb = rgb * (1 + (t2 - .5)[..., None] * 0.28 * hoofm[..., None])
    # ---------- 焼けた 蹄鉄（白 → 黄 → だいだい → 赤）と その 光 ----------
    hot = np.array([1.7, 0.32, 0.05])
    rgb = rgb * (1 - shoe[..., None] * .6) + shoe[..., None] * hot
    halo = cv2.GaussianBlur(shoe, (0, 0), 3 * S)[..., None] * np.array([0.8, 0.16, 0.04]) + cv2.GaussianBlur(shoe, (0, 0), 14 * S)[..., None] * np.array([0.4, 0.05, 0.10])
    # ---------- 球節の うしろの 毛（左へ なびく：速さ） ----------
    rng = np.random.default_rng(seed)
    hb = HairBuf(H, W, ss=2)
    ex, ey = M['ergot'][0]
    fx, fy = M['fet'][0]

    def flow(x, y, a, t):
        d = math.atan2(math.sin(math.pi - a), math.cos(math.pi - a))
        return d * 0.10
    for i in range(26):
        p0 = np.array([ex + rng.normal(0, 8 * S), ey + rng.normal(0, 10 * S)])
        gp = guide(p0, math.pi + rng.normal(0.15, 0.25), rng.uniform(70, 150) * S, 16, rng, flow, wave=rng.uniform(1, 2), phase=rng.uniform(0, 6))
        hb.lock(gp, 18, rng, spread=4 * S, clump=0.6, wmin=0.5 * S, wmax=1.2 * S, rimk=0.8)
    cov, rimw, cnt = hb.result(k=0.5)
    hair = np.stack([0.004 + rimw * 0.07, 0.004 + rimw * 0.06, 0.007 + rimw * 0.12], -1)
    img = rgb * (1 - cov[..., None]) + hair * cov[..., None]
    a = np.clip(A + cov, 0, 1)
    # ---------- 左の はしは ぶれて すき通る（速さ） ----------
    fade = smoothstep(fx - 330 * S, fx - 70 * S, xx)
    img = img * fade[..., None]
    a = a * fade
    # うしろへの ぶれ（足の 形を 左へ のばした 光の 尾：上は うす桃色・下は 青）
    k = int(300 * S)
    ker = np.zeros((1, 2 * k + 1), np.float32)
    ker[0, k:] = np.exp(-np.arange(k + 1) / (110 * S))
    ker /= ker.sum()
    legm = np.clip((np.abs(mid - M_COAT) < .5).astype(np.float32) + cov, 0, 1)        # ぶれは 足（毛）だけ：蹄の うしろ（裂け目の 所）は きれいに
    tail = cv2.filter2D(np.dstack([img * (a * legm)[..., None], a * legm]), -1, ker, borderType=cv2.BORDER_CONSTANT)   # 右の 形を 左へ のばす
    ta = np.clip(tail[..., 3] * 1.4, 0, 1) * (1 - a)
    tcol = np.array([0.55, 0.22, 0.6]) * (1 - smoothstep(fy - 60 * S, fy + 40 * S, yy))[..., None] + np.array([0.2, 0.3, 0.75]) * smoothstep(fy - 60 * S, fy + 40 * S, yy)[..., None]
    img = img + tcol * ta[..., None] * 0.55
    a = np.clip(a + ta * 0.55, 0, 1)
    # ---------- 光（蹄鉄・ふち） ----------
    img = img + halo
    ga = np.clip(halo.max(-1) / 1.5, 0, 1)
    a = np.clip(np.maximum(a, ga), 0, 1)
    out = to_srgb(aces(img))
    return np.dstack([np.clip(out, 0, 1) * a[..., None], a])


def build_asset(out, SA=None, prefix=None):
    if SA is None:
        import shiden_art as SA
    prefix = prefix or os.path.join(out, '_tmp', 'hoof')
    os.makedirs(os.path.dirname(prefix), exist_ok=True)
    R, M = render(prefix)
    img = compose(R, M)
    SA.save(img, os.path.join(out, 'sd_w_hoof.webp'), q=86)
    tx, ty = M['toe'][0]                                               # 切り口の 先＝蹄の つま先（蹄鉄の いちばん 上）の 少し 内がわ
    xs = np.where(img[..., 3].max(0) > .02)[0]
    SA.put_lay('sd_w_hoof', W2 / 2, H2 / 2, tip=[round(tx / 2 - 2, 1), round(ty / 2 + 7, 1)], x0=round(float(xs.min()) / 2, 1))
    return 'sd_w_hoof'


if __name__ == '__main__':
    o = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.makedirs(o, exist_ok=True)
    pre = os.path.join(o, 'hoof')
    R, M = render(pre, ss=int(os.environ.get('SS', '1')))
    img = compose(R, M)
    cv2.imwrite(os.path.join(o, 'hoof_rgba.png'), (np.clip(img[..., [2, 1, 0, 3]], 0, 1) * 255).astype(np.uint8))
    bg = np.zeros((H2, W2, 3), np.float32) + np.array([0.55, 0.75, 0.95])
    comp = img[..., :3] + bg * (1 - img[..., 3:])
    cv2.imwrite(os.path.join(o, 'hoof_on_bg.png'), (np.clip(comp[..., ::-1], 0, 1) * 255).astype(np.uint8))
    dk = img[..., :3] + np.array([0.05, 0.02, 0.06]) * (1 - img[..., 3:])
    cv2.imwrite(os.path.join(o, 'hoof_on_dark.png'), (np.clip(dk[..., ::-1], 0, 1) * 255).astype(np.uint8))
    print({k: (np.round(v[0], 1) if k != 'outline' else len(v)) for k, v in M.items()})
