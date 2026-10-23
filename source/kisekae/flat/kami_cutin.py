"""超神様的中の カットイン（宇宙）第2版：1コマずつ 描く 絵。1170×2532（iPhone の 画面の 画素・たて長の 画面いっぱい）・1秒 30コマ・141コマ（4.7秒）
   第1版：まさちゃん「超神様的中ボタンを追加して！ 超神様的中の4回に1回ランダムで発生」「送った一個目の動画のようなカットインの素材を作成したい！」
     （宇宙エフェクト 28枚・聞いたら「超神様的中に カットイン」「画面いっぱい」）→ 送ってくれた 絵は 見るだけ（なぞらない・字「Heat.」は 使わない）。
     惑星の ふち（ななめの 地平線）・まん中で ギラッと 光る 太陽・とぶ 岩 を 一から 計算で 描いた（1.7秒）
   第2版：まさちゃん「ここ中心に光ってるところを最初は光らせずに隕石が落ちて、一瞬二枚目の画像の光に包まれるシーンを入れて、中心が大きな爆発と
     地球に大きな雷が走り、中心の光が現れる、その後の黄色、赤色、青色、グレーのシーンを青色を黒に色にして、三枚目の画像のグレーの中心から外側へ
     波打つ演出を黄色と赤色の爆発と雷が混じった演出にして！ その後に四枚目の画像(爆発や雷は残ったまま)中心の光が小さくなり、超神様的中演出に繋げて！
     ここの超神様的中に繋げるためのシーンは、今の指示を追加して秒数が伸びるのは問題ない！」（一枚目＝赤い 宇宙・二枚目＝青い 宇宙・三枚目＝白い 反転の 波紋・
     四枚目＝赤い 惑星に もどった 所）
   流れ：
     0〜1.1秒 赤い 宇宙（まん中は まだ 光らない）に 隕石が 落ちる（惑星に 当たって 小さく 光る）→ 大きな 隕石が まん中に 当たる
     1.1〜1.3秒 一瞬 青い 光に つつまれる（二枚目の 青い 宇宙の 光）
     1.3〜2.3秒 まん中で 大きな 爆発（火の 玉・惑星の 上を 広がる 衝撃波・火花）・惑星に 大きな 雷が はしる → まん中の 光が あらわれる
     2.3〜2.8秒 黄色（反転）→ 赤い 宇宙 → 黒い 宇宙（前の 青を 黒に）
     2.8〜3.9秒 白い 反転の 中を 衝撃波の 波紋：波に のって 黄色と 赤の 火の 輪・あちこちで 爆発・まん中から 外へ 黄色と 赤の 雷
     3.9〜4.7秒 赤い 惑星に もどる（惑星の 上の 爆発と 雷は のこる）→ まん中の 光が 小さく なって まわりが 暗く なる
       → 超神様の 動画の はじめの 小さな 光（同じ 所）に つなぐ
   点めつ：画面の 大きな 明るさの 入れかわりは 青い 光・黄色・赤・白・赤 の 時だけ（黄色 → 赤 → 黒 は 0.17秒ずつ）。雷は 同じ 所に つづけて 出さない・
     火の 輪は 2つ だけ。反転の 中の 色は 明るさを そろえて 色だけ かえる
   python3 flat/kami_cutin.py <出力フォルダ> [コマ番号（1〜）…]  → f001.png …（何回 作っても 同じ）"""
import os, sys, math, random
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
import kami_film as KF
import kami_storm as KS
KM = KF.KM

W, H = KF.W, KF.H                     # 1170 × 2532
FPS = 30
F = (582.0, 1188.0)                   # まん中の 光（惑星の ふちの 上）：超神様の 動画の はじめの 小さな 光と 同じ 所
TILT = math.radians(35.0)             # 地平線の かたむき（左上 → 右下）
PR = 3300.0                           # 惑星の 半径（画面の 画素）
TAN = np.array([math.cos(TILT), math.sin(TILT)])
NRM = np.array([-math.sin(TILT), math.cos(TILT)])   # ふち → 惑星の 中へ（左下）
PC = np.array(F) + NRM * PR                          # 惑星の まん中（画面の 外・左下）
A0 = math.atan2(F[1] - PC[1], F[0] - PC[0])

# ---------------------------------------------------------------- 時間わり（コマ：はじめ, おわり（ふくまない）, 場面）
SEQ = ((0, 33, 'M'),         # 赤い 宇宙・まん中は まだ 光らない・隕石が 落ちる → 大きな 隕石が まん中へ
       (33, 39, 'Env'),      # 一瞬 青い 光に つつまれる（二枚目の 絵の 光）
       (39, 69, 'Boom'),     # まん中で 大きな 爆発・惑星に 大きな 雷 → まん中の 光が あらわれる
       (69, 74, 'Nyel'),     # 反転（黄色）
       (74, 79, 'R2'),       # 赤い 宇宙
       (79, 84, 'K'),        # 黒い 宇宙（前の 青を 黒に）
       (84, 117, 'Nwhite'),  # 白い 反転の 中を 衝撃波の 波紋＋黄色と 赤の 爆発と 雷
       (117, 141, 'R3'))     # 赤い 惑星に もどる（爆発と 雷は のこる）→ まん中の 光が 小さく なる
N = SEQ[-1][1]
IMPACT, BOOM = 33, 39                 # 大きな 隕石が 当たる コマ・爆発の はじまりの コマ
EXPO = .78                            # 光の 量（ふちを くっきり・反転の 黒い 帯は ふちに そって 細く）
RIPPLE = dict(f0=84, speed=2200.0, lam=112.0, width=150.0, amp=72.0, decay=.5, launch=(0.0, .08, .17))   # 衝撃波（秒は f0 から）
FIRE_RINGS = (0,)                     # 火の 輪に する 波紋（launch の 番号：1つ＝同じ 所の 点めつを ふやさない）
R3_SHRINK = (6, 21)                   # 赤い 惑星に もどって から まん中の 光が 小さく なる コマ（R3 の はじめから）


def mode_at(fi):
    for a, b, m in SEQ:
        if a <= fi < b:
            return m, fi - a, b - a
    return SEQ[-1][2], fi - SEQ[-1][0], SEQ[-1][1] - SEQ[-1][0]


def col(*c):
    return np.float32(c)


def sstep(e0, e1, x):
    u = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return u * u * (3 - 2 * u)


# ---------------------------------------------------------------- 画面の 座標
def grid():
    def f():
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        return xx, yy
    return KF.cache('ci2_grid', f)


def planet_coords():
    """惑星の ふちからの 深さ d（中が +）・ふちに そった 長さ s（右下が −）・球の 上の 深さ v（ふちの 近くは ちぢむ）・まん中からの きょり rf"""
    def f():
        xx, yy = grid()
        qx, qy = xx - PC[0], yy - PC[1]
        r = np.sqrt(qx * qx + qy * qy)
        d = PR - r
        ang = np.arctan2(qy, qx) - A0
        ang = (ang + np.pi) % (2 * np.pi) - np.pi
        s = -ang * PR
        v = PR * np.arccos(np.clip(1 - np.clip(d, 0, None) / PR, -1, 1))
        rf = np.hypot(xx - F[0], yy - F[1])
        return d.astype(np.float32), s.astype(np.float32), v.astype(np.float32), rf.astype(np.float32)
    return KF.cache('ci2_pc', f)


def sd_xy(s, d):
    """惑星の 上の 場所（s：ふちに そった 長さ・d：ふちから 中への 深さ）→ 画面の 画素"""
    a = A0 - s / PR
    r = PR - d
    return (float(PC[0] + r * math.cos(a)), float(PC[1] + r * math.sin(a)))


def depth_at(x, y):
    return PR - math.hypot(x - PC[0], y - PC[1])


# ---------------------------------------------------------------- 色の くみ
PAL = dict(
    R=dict(near=col(1.0, .42, .1), mid=col(.42, .05, .035), far=col(.03, .006, .012), neb=col(.75, .16, .06), haze=col(1.0, .3, .12),
           atm_in=col(1.0, .82, .95), atm_out=col(1.0, .34, .42), atm_far=col(.55, .18, .62),
           lit=col(.95, .42, .95), deep=col(.05, .03, .16), cloud=col(1.0, .86, 1.0),
           core=col(1.0, .97, .9), halo=col(1.0, .55, .18), streak=col(1.0, .3, .1), spike=col(1.0, .62, .42), rock_lit=col(1.0, .55, .25)),
    B=dict(near=col(.45, .75, 1.0), mid=col(.03, .1, .42), far=col(.006, .01, .05), neb=col(.12, .3, .9), haze=col(.35, .6, 1.0),
           atm_in=col(.85, .93, 1.0), atm_out=col(.35, .55, 1.0), atm_far=col(.4, .25, .85),
           lit=col(.6, .45, 1.0), deep=col(.03, .03, .16), cloud=col(.9, .92, 1.0),
           core=col(.92, .97, 1.0), halo=col(.4, .7, 1.0), streak=col(.25, .55, 1.0), spike=col(.6, .8, 1.0), rock_lit=col(.55, .75, 1.0)),
    # 黒い 宇宙（まさちゃん「青色を黒に」）：まっ黒な 宇宙・黒い 惑星・白い 光
    K=dict(near=col(.5, .5, .55), mid=col(.02, .02, .024), far=col(.002, .002, .003), neb=col(.05, .05, .06), haze=col(.5, .5, .55),
           atm_in=col(.95, .95, 1.0), atm_out=col(.55, .55, .6), atm_far=col(.22, .22, .26),
           lit=col(.22, .22, .25), deep=col(.008, .008, .01), cloud=col(.55, .55, .6),
           core=col(1.0, 1.0, 1.0), halo=col(.75, .78, .85), streak=col(.85, .88, 1.0), spike=col(.9, .92, 1.0), rock_lit=col(.75, .76, .8)))


def space(p, sun=1):
    """宇宙（動かない）：太陽の まわりの 光・星雲・ちり・星（sun＝0 は まん中が まだ 光らない 時）"""
    def f():
        P = PAL[p]
        xx, yy = grid()
        d, s, v, rf = planet_coords()
        n1 = KS.fbm(H, W, 5, 501, 5)
        n2 = KS.fbm(H, W, 14, 517, 4)
        sk = 1.0 if sun else .08
        base = P['far'][None, None] * np.ones((H, W, 1), np.float32)
        g1 = np.exp(-rf / 900.0)[..., None]
        g2 = np.exp(-rf / 330.0)[..., None]
        img = base + (P['mid'] * g1 * 1.1 + P['near'] * g2 * .55) * sk
        neb = np.clip((n1 - .42) * 2.2, 0, 1) ** 1.4 * (.35 + .65 * np.exp(-rf / 1400.0) * (1.0 if sun else .4))
        dust = np.clip((n2 - .55) * 3.0, 0, 1)
        img += P['neb'][None, None] * (neb * (1 - .6 * dust))[..., None] * .55
        img *= (1 - .45 * dust * np.exp(-rf / 2000.0))[..., None]
        vig = np.clip(1 - ((xx - W * .2) / W) ** 2 * .25 - ((H * .9 - yy) / H) ** 2 * .35, .35, 1)
        img *= vig[..., None]
        rng = np.random.default_rng(530 if p == 'R' else 531)
        st = np.zeros((H, W), np.float32)
        for _ in range(900):
            x, y = rng.uniform(0, W), rng.uniform(0, H)
            b = rng.pareto(2.2) * .25
            st[int(y), int(x)] += min(b, 2.5)
        st = cv2.GaussianBlur(st, (0, 0), .9) * 6
        img += (st[..., None] * col(1.0, .9, .85)) * (d < -4)[..., None]
        return img.astype(np.float32)
    return KF.cache(f'ci2_space_{p}{sun}', f)


def planet_tex():
    def f():
        TW, TH = 4096, 2048
        tex = .55 * KS.fbm(TH, TW, 18, 611, 6) + .45 * KS.fbm(TH, TW, 7, 623, 5)
        streak = KS.fbm(TH, TW // 6, 22, 641, 4)
        streak = cv2.resize(streak, (TW, TH), interpolation=cv2.INTER_CUBIC)
        return (.7 * tex + .3 * streak).astype(np.float32)
    return KF.cache('ci2_ptex', f)


def planet(p, sun=1):
    """惑星（動かない）：ふちに そって まがる 雲・太陽に 近い ほど 明るい・ふちの 大気の 光 → (色, 外の 光, 惑星の 形)"""
    def f():
        P = PAL[p]
        d, s, v, rf = planet_coords()
        tex = planet_tex()
        TW = tex.shape[1]
        mx = np.clip(s / 2.2 + TW / 2, 0, TW - 2).astype(np.float32)
        my = np.clip(v / 1.6, 0, tex.shape[0] - 2).astype(np.float32)
        cl = cv2.remap(tex, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        cloud = np.clip((cl - .47) * 3.6, 0, 1) ** 1.2
        sk = 1.0 if sun else .1
        light = np.clip(1 - v / 2900.0, 0, 1) ** 1.25 * (.45 + .55 * np.exp(-(s / 1900.0) ** 2) * sk) * (1.0 if sun else .55)
        base = P['deep'][None, None] + (P['lit'] - P['deep'])[None, None] * (light * .8)[..., None]
        img = (base * (.55 + .8 * cl[..., None]) + P['cloud'] * (cloud * (.12 + 1.0 * light))[..., None] * .8) * .85
        rng = np.random.default_rng(650)
        city = np.zeros((H, W), np.float32)
        for _ in range(500):
            x, y = rng.uniform(0, W), rng.uniform(0, H)
            city[int(y), int(x)] = rng.uniform(.3, 1.0)
        city = cv2.GaussianBlur(city, (0, 0), 1.2) * 5 * np.clip((v - 500) / 900, 0, 1) * (cl > .45)
        img += city[..., None] * col(1.0, .6, .3) * .5
        near = np.exp(-(s / 900.0) ** 2) * sk
        a_in = (np.exp(-np.clip(d, 0, None) / 9.0) * 1.4 + np.exp(-np.clip(d, 0, None) / 45.0) * .45) * (.5 + 1.5 * near) * (d > 0)
        img += P['atm_in'] * a_in[..., None]
        a_out = (np.exp(np.clip(d, None, 0) / 30.0) * (.5 + 1.6 * near) + np.exp(np.clip(d, None, 0) / 220.0) * (.1 + .45 * near)) * (d <= 0)
        img_out = P['atm_out'] * (a_out * near)[..., None] + P['atm_far'] * (a_out * (1 - near))[..., None]
        mask = np.clip(d / 2.0 + .5, 0, 1)
        return img.astype(np.float32), img_out.astype(np.float32), mask.astype(np.float32)
    return KF.cache(f'ci2_planet_{p}{sun}', f)


def flare(img, p, I, kz=None):
    """太陽の 光：しん・まわりの 光・よこに のびる 光の 帯・たての とげ（I＝強さ・kz＝大きさ：ふつうは √I）"""
    P = PAL[p]
    xx, yy = grid()
    dx, dy = xx - F[0], yy - F[1]
    r2 = dx * dx + dy * dy
    k = math.sqrt(I) if kz is None else kz
    k = max(k, .12)
    img += P['core'] * (I * (3.0 * np.exp(-r2 / max(4.0, 16.0 * k) ** 2) + 1.0 * np.exp(-r2 / (48.0 * k) ** 2)))[..., None]
    img += P['halo'] * (I * .5 * np.exp(-r2 / (150.0 * k) ** 2) + I * .12 * np.exp(-r2 / (420.0 * k) ** 2))[..., None]
    ax = np.abs(dx)
    img += P['streak'] * (I * (1.3 * np.exp(-(dy / (4.0 + 2 * k)) ** 2) * np.exp(-ax / (900.0 * k)) +
                              .3 * np.exp(-(dy / 34.0) ** 2) * np.exp(-ax / (520.0 * k))))[..., None]
    ay = np.abs(dy)
    img += P['spike'] * (I * .7 * np.exp(-(dx / 3.0) ** 2) * np.exp(-ay / (150.0 * k)))[..., None]
    for a in (math.radians(62), math.radians(-62)):
        u = dx * math.cos(a) + dy * math.sin(a)
        w_ = -dx * math.sin(a) + dy * math.cos(a)
        img += P['spike'] * (I * .25 * np.exp(-(w_ / 2.5) ** 2) * np.exp(-np.abs(u) / (170.0 * k)))[..., None]


def sparkles(img, p, t, g=1.0):
    """ふちの 上と 宇宙の 小さな 光（たての 光の すじ つき）"""
    if g <= .01:
        return
    P = PAL[p]
    rng = random.Random(700)
    for k in range(9):
        if k < 5:
            sv = rng.uniform(-1400, 1300)
            x, y = F[0] + TAN[0] * sv, F[1] + TAN[1] * sv
        else:
            x, y = rng.uniform(100, W - 100), rng.uniform(150, H - 150)
        tw = .6 + .4 * math.sin(t * rng.uniform(9, 15) + rng.uniform(0, 6))
        gg = rng.uniform(.5, 1.0) * tw * g
        x0, x1 = int(max(0, x - 40)), int(min(W, x + 40))
        y0, y1 = int(max(0, y - 420)), int(min(H, y + 420))
        if x1 <= x0 or y1 <= y0:
            continue
        xx, yy = np.meshgrid(np.arange(x0, x1, dtype=np.float32), np.arange(y0, y1, dtype=np.float32))
        dx, dy = xx - x, yy - y
        sp = 1.6 * np.exp(-(dx * dx + dy * dy) / 30.0) + .5 * np.exp(-(dx / 2.2) ** 2) * np.exp(-np.abs(dy) / 70.0) + \
            .3 * np.exp(-(dy / 2.2) ** 2) * np.exp(-np.abs(dx) / 18.0)
        img[y0:y1, x0:x1] += P['spike'] * (sp * gg)[..., None]


# ---------------------------------------------------------------- 岩（立体：太陽の 光が うしろから）
ROCKS = ((-.30, -.36, 150, 11, -14, 22), (.36, -.44, 95, 12, 18, -30), (-.42, .08, 70, 13, -26, 6), (.40, .12, 120, 14, 24, 16),
         (-.08, -.62, 55, 15, -6, -40), (.18, .52, 160, 16, 8, 34), (-.36, .44, 85, 17, -20, 26), (.06, .30, 40, 18, 4, 30),
         (.30, -.10, 34, 19, 28, -6), (-.18, -.20, 28, 20, -16, -12), (.46, .40, 48, 21, 26, 22))
# (x（画面の はばに 対して）, y（高さに 対して）, 大きさ（画素）, 種, x の 速さ（画素/秒）, y の 速さ)


def rock_maps(R, seed):
    """岩の 形と 面の 向き（はじめに 1回）：(alpha, nx, ny, nz, 地の 色の 明るさ)"""
    def f():
        rng = np.random.default_rng(seed)
        S = int(R * 2.4) | 1
        c = S / 2
        n = 13
        angs = np.sort(rng.uniform(0, 2 * np.pi, n))
        pts = [(c + math.cos(a) * R * rng.uniform(.62, 1.0), c + math.sin(a) * R * rng.uniform(.62, 1.0) * rng.uniform(.75, 1.0)) for a in angs]
        m = np.zeros((S * 4, S * 4), np.uint8)
        cv2.fillPoly(m, [np.int32(np.array(pts) * 4)], 255, cv2.LINE_AA)
        m = cv2.resize(m.astype(np.float32) / 255, (S, S), interpolation=cv2.INTER_AREA)
        rough = KS.fbm(S, S, 9, seed + 3, 4)
        m = KS.smoothstep(.45, .55, cv2.GaussianBlur(m, (0, 0), max(.8, R * .05)) + (rough - .5) * .22)
        din = cv2.distanceTransform((m > .5).astype(np.uint8), cv2.DIST_L2, 5)
        hgt = np.sqrt(np.clip(din / (R * .8), 0, 1)) * R * .7 + (KS.fbm(S, S, 7, seed + 5, 5) - .5) * R * .5
        crater = KS.fbm(S, S, 16, seed + 9, 3)
        hgt -= np.clip(crater - .62, 0, None) * R * .8
        gx = cv2.Sobel(hgt, cv2.CV_32F, 1, 0, ksize=3) / 8
        gy = cv2.Sobel(hgt, cv2.CV_32F, 0, 1, ksize=3) / 8
        nz = 1 / np.sqrt(1 + gx * gx + gy * gy)
        alb = .7 + .6 * KS.fbm(S, S, 12, seed + 11, 4)
        return np.dstack([m, -gx * nz, -gy * nz, nz, alb]).astype(np.float32)
    return KF.cache(f'ci_rock{seed}', f)


def rocks(img, p, t, rim=1.0):
    """とぶ 岩（rim＝うしろからの 光の 強さ：まん中が 光る 前は 弱い）"""
    P = PAL[p]
    for (fx, fy, R, seed, vx, vy) in ROCKS:
        mp = rock_maps(R, seed)
        ang = t * (14 + seed * 3) * (1 if seed % 2 else -1)
        S = mp.shape[0]
        Mr = cv2.getRotationMatrix2D((S / 2, S / 2), ang, 1.0 + .06 * t)
        rot = cv2.warpAffine(mp, Mr, (S, S), flags=cv2.INTER_LINEAR, borderValue=0)
        a = math.radians(-ang)
        nx = rot[..., 1] * math.cos(a) - rot[..., 2] * math.sin(a)
        ny = rot[..., 1] * math.sin(a) + rot[..., 2] * math.cos(a)
        nz = rot[..., 3]
        al = rot[..., 0]
        cx = W * (.5 + fx) + vx * t * 3
        cy = H * (.5 + fy) + vy * t * 3
        lx, ly = F[0] - cx, F[1] - cy
        ln = math.hypot(lx, ly) + 1e-6
        L = np.array([lx / ln * .9, ly / ln * .9, -.35])
        L /= np.linalg.norm(L)
        ndl = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
        rimv = np.clip(nx * L[0] + ny * L[1], 0, 1) ** 2.2 * (1 - nz) ** .6
        amb = np.clip(nz * .6 + ny * .25, 0, 1)
        near = math.exp(-ln / 1500.0)
        c = col(.045, .03, .03)[None, None] * rot[..., 4:5] + col(.1, .05, .13) * amb[..., None] * .35
        c = c + P['rock_lit'] * (ndl * .22 + rimv * 2.4)[..., None] * (.3 + .9 * near) * rim
        x0, y0 = int(round(cx - S / 2)), int(round(cy - S / 2))
        xs0, ys0, xs1, ys1 = max(0, x0), max(0, y0), min(W, x0 + S), min(H, y0 + S)
        if xs1 <= xs0 or ys1 <= ys0:
            continue
        sub = (slice(ys0 - y0, ys1 - y0), slice(xs0 - x0, xs1 - x0))
        aa = al[sub][..., None]
        img[ys0:ys1, xs0:xs1] = img[ys0:ys1, xs0:xs1] * (1 - aa) + c[sub] * aa


def debris_list():
    def f():
        rng = np.random.default_rng(720)
        out = []
        for _ in range(220):
            a = rng.uniform(0, 2 * math.pi)
            r0 = rng.uniform(80, 1500)
            out.append((a, r0, rng.uniform(60, 420), rng.uniform(.6, 2.4), rng.uniform(.2, 1.0)))
        return out
    return KF.cache('ci_deb', f)


def debris(img, p, t, g=1.0):
    """ちり（まん中から 外へ ゆっくり とぶ 小さな 光の 粒）"""
    if g <= .01:
        return
    P = PAL[p]
    m = np.zeros((H, W), np.float32)
    for a, r0, v, sz, b in debris_list():
        r = r0 + v * t
        x, y = F[0] + r * math.cos(a), F[1] + r * math.sin(a) * 1.4
        if 0 <= x < W and 0 <= y < H:
            cv2.circle(m, (int(x * 4), int(y * 4)), int(sz * 4), float(b), -1, cv2.LINE_AA, shift=2)
    m = cv2.GaussianBlur(m, (0, 0), .8)
    img += P['spike'] * m[..., None] * (.9 * g)


def scene_lin(p, t, sun=1.0, I=0.0, rim=1.0):
    """1まいの 宇宙（光の 量の まま：ブルームの 前）。sun＝まん中の まわりの 明るさ（0＝まだ 光らない）・I＝まん中の 光"""
    if p == 'R' and sun < .999:
        s0, s1 = space('R', 0), space('R', 1)
        (pl0, po0, pm), (pl1, po1, _) = planet('R', 0), planet('R', 1)
        sp = s0 + (s1 - s0) * sun
        pl = pl0 + (pl1 - pl0) * sun
        po = po0 + (po1 - po0) * sun
    else:
        sp = space(p, 1)
        pl, po, pm = planet(p, 1)
    img = sp * (1 - pm[..., None]) + pl * pm[..., None] + po
    if I > 0:
        flare(img, p, I)
    sparkles(img, p, t, min(1.0, sun))
    debris(img, p, t, min(1.0, sun))
    rocks(img, p, t, rim)
    return img


def finish(img, expo=EXPO):
    """光の 量 → 画面の 色（にじみ・白く とぶ 前に 頭うち）"""
    return KF.tonemap(KF.bloom(img * expo))


def zoom(img, z):
    if abs(z - 1.0) < 1e-4:
        return img
    M = np.float32([[z, 0, F[0] * (1 - z)], [0, z, F[1] * (1 - z)]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


# ---------------------------------------------------------------- 線を 描く 道具（雷・隕石の 尾）
def P8(p):
    return (int(round(p[0] * 8)), int(round(p[1] * 8)))


def poly_len(pts):
    acc = [0.0]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        acc.append(acc[-1] + math.hypot(bx - ax, by - ay))
    return acc


def draw_taper(mask, pts, w0, w1, val, grow=1.0, gam=1.3):
    """太さ w0 → w1（画素）の 線（はじめから grow の 割合まで）"""
    acc = poly_len(pts)
    L = acc[-1] or 1.0
    lim = L * grow
    for i in range(len(pts) - 1):
        if acc[i] >= lim:
            break
        a, b = pts[i], pts[i + 1]
        if acc[i + 1] > lim:
            f = (lim - acc[i]) / max(1e-6, acc[i + 1] - acc[i])
            b = (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
        s = ((acc[i] + acc[i + 1]) / 2) / L
        wd = w0 + (w1 - w0) * s ** gam
        cv2.line(mask, P8(a), P8(b), float(val), max(1, int(round(wd))), cv2.LINE_AA, shift=3)


def glow_add(dst, mask, layers):
    for sig, c, g in layers:
        m = mask if sig <= 0 else KF.fblur(mask, sig)
        dst += m[..., None] * (col(*c) * g)


# ---------------------------------------------------------------- 隕石
METEORS = (  # (はじまる 秒, x, y, 向き（度：0＝右・90＝下）, 速さ（画素/秒）, 頭の 大きさ（画素）, 明るさ, 尾の 長さ, 燃えつきる 深さ（ふちから 中へ 画素）)
    (0.00, 990, -60, 121, 2050, 6.0, 1.0, 720, 260),
    (0.07, 330, -80, 117, 2300, 4.0, .75, 520, 120),
    (0.16, 1240, 980, 128, 2000, 5.5, .95, 650, 520),
    (0.27, 760, -90, 116, 2550, 4.0, .7, 600, 820),
    (0.38, 1240, 780, 134, 1950, 7.0, 1.0, 760, 380),
    (0.49, 150, -60, 119, 2250, 3.5, .6, 460, 200),
    (0.58, 1240, 1250, 131, 2250, 5.0, .9, 640, 640),
    (0.70, 520, -90, 117, 2600, 4.5, .8, 650, 300),
    (0.80, 1240, 600, 129, 2300, 5.0, .85, 600, 900),
)
BIG = dict(p0=(1330.0, 40.0), size=(9.0, 40.0), trail=(380.0, 1150.0))   # 大きな 隕石：右上の 外から まん中（F）へ・IMPACT で 当たる
MET_GLOW = ((0, (1.0, .97, .85), 2.2), (3, (1.0, .75, .35), 1.2), (10, (1.0, .45, .12), .8), (30, (1.0, .3, .06), .35))


def meteor_end(m):
    """隕石が 惑星に 当たって 燃えつきる 秒と 場所（画面の 外へ 出る 時は その 秒）"""
    t0, x, y, ang, v, sz, b, tr, dend = m
    dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    t = 0.0
    while t < 3.0:
        px, py = x + dx * v * t, y + dy * v * t
        if depth_at(px, py) >= dend:
            return t0 + t, (px, py), True
        if px < -200 or py > H + 200:
            return t0 + t, (px, py), False
        t += 1 / 240
    return t0 + 3.0, (x + dx * v * 3, y + dy * v * 3), False


def meteor_events():
    """効果音 用：[(はじまる 秒, 当たる 秒, 当たる x, 当たったか, 大きさ)]・大きな 隕石は さいご"""
    out = []
    for m in METEORS:
        te, p, hit = meteor_end(m)
        out.append((m[0], te, p[0], hit, m[5]))
    out.append((0.0, IMPACT / FPS, F[0], True, BIG['size'][1]))
    return out


def meteor_trail(m_core, m_glow, head, dv, Lt, size, b):
    n = 20
    for i in range(n, 0, -1):
        u0, u1 = i / n, (i - 1) / n
        p0 = (head[0] - dv[0] * Lt * u0, head[1] - dv[1] * Lt * u0)
        p1 = (head[0] - dv[0] * Lt * u1, head[1] - dv[1] * Lt * u1)
        w = size * (1 - .82 * u0) * 2
        val = b * (1 - u0) ** 1.6
        cv2.line(m_core, P8(p0), P8(p1), float(val), max(1, int(round(w * .45))), cv2.LINE_AA, shift=3)
        cv2.line(m_glow, P8(p0), P8(p1), float(val), max(1, int(round(w * 1.5))), cv2.LINE_AA, shift=3)


def meteors(img, t):
    """隕石（頭は 白く 光り、尾は だいだい → 赤）：惑星に 当たると 小さく 光って 消える"""
    mc = np.zeros((H, W), np.float32)
    mg = np.zeros((H, W), np.float32)
    hit_light = []
    for m in METEORS:
        t0, x, y, ang, v, sz, b, tr, dend = m
        if t < t0:
            continue
        dv = (math.cos(math.radians(ang)), math.sin(math.radians(ang)))
        te, pe, hit = meteor_end(m)
        fin = min(1.0, (t - t0) / .06)
        if t < te:
            el = t - t0
            head = (x + dv[0] * v * el, y + dv[1] * v * el)
            meteor_trail(mc, mg, head, dv, min(tr, v * el), sz, b * fin)
            cv2.circle(mc, P8(head), int(sz * .9 * 8), float(b * 1.5 * fin), -1, cv2.LINE_AA, shift=3)
        else:
            age = t - te
            if age < .2:
                k = (1 - age / .2) ** 2
                meteor_trail(mc, mg, pe, dv, min(tr, v * (te - t0)) * (1 - .5 * age / .2), sz, b * k * .8)
            if hit and age < .25:
                hit_light.append((pe, sz, b, age))
    glow_add(img, mc, MET_GLOW[:1])
    glow_add(img, mg, MET_GLOW[1:])
    for (p, sz, b, age) in hit_light:             # 当たった 所の 小さな 光（すぐ 消える）
        g = b * 1.4 * math.exp(-age / .07)
        r = 18 + sz * 4 + 220 * age
        x0, x1 = int(max(0, p[0] - r * 3)), int(min(W, p[0] + r * 3))
        y0, y1 = int(max(0, p[1] - r * 3)), int(min(H, p[1] + r * 3))
        if x1 <= x0 or y1 <= y0:
            continue
        xx, yy = grid()
        rr = np.hypot(xx[y0:y1, x0:x1] - p[0], yy[y0:y1, x0:x1] - p[1])
        img[y0:y1, x0:x1] += (np.exp(-(rr / r) ** 2) * g)[..., None] * col(1.0, .62, .25) + \
            (np.exp(-(rr / (r * .3)) ** 2) * g)[..., None] * col(1.0, .95, .8)


def big_meteor(img, t):
    """大きな 隕石：右上の 外から まん中へ（だんだん 大きく・明るく）"""
    T = IMPACT / FPS
    if t >= T:
        return
    u = t / T
    p0 = BIG['p0']
    head = (p0[0] + (F[0] - p0[0]) * u, p0[1] + (F[1] - p0[1]) * u)
    L = math.hypot(F[0] - p0[0], F[1] - p0[1])
    dv = ((F[0] - p0[0]) / L, (F[1] - p0[1]) / L)
    sz = BIG['size'][0] + (BIG['size'][1] - BIG['size'][0]) * u ** 2
    tr = BIG['trail'][0] + (BIG['trail'][1] - BIG['trail'][0]) * u
    b = 1.2 + 1.3 * u
    mc = np.zeros((H, W), np.float32)
    mg = np.zeros((H, W), np.float32)
    meteor_trail(mc, mg, head, dv, tr, sz, b)
    cv2.circle(mc, P8(head), int(sz * 8), float(b * 1.6), -1, cv2.LINE_AA, shift=3)
    glow_add(img, mc, ((0, (1.0, .97, .85), 2.2), (4, (1.0, .78, .4), 1.4)))
    glow_add(img, mg, ((12, (1.0, .45, .12), 1.0), (36, (1.0, .3, .06), .5)))
    # 頭の まわりの 光（まわりを 照らす）
    xx, yy = grid()
    rr = np.hypot(xx - head[0], yy - head[1])
    img += (np.exp(-rr / (110.0 + 260.0 * u)) * (.35 + 1.4 * u ** 2))[..., None] * col(1.0, .52, .18)


# ---------------------------------------------------------------- 火（爆発・火の 玉・けむり）
FIRE = ((0, (0, 0, 0)), (.12, (.3, .02, .01)), (.28, (.85, .12, .02)), (.45, (1.0, .38, .06)), (.62, (1.0, .62, .15)),
        (.78, (1.0, .84, .38)), (.92, (1.0, .95, .7)), (1.1, (1.1, 1.06, 1.0)))
SMOKE = col(.16, .1, .08)


def fire_col(T):
    xs = np.float32([a for a, _ in FIRE])
    cs = np.float32([c for _, c in FIRE])
    T = np.clip(T, 0, 1.1)
    return np.stack([np.interp(T, xs, cs[:, i]) for i in range(3)], -1).astype(np.float32)


def fire_lut():
    """火の 色あい（T）× 明るさ（光の 量 L）→ 画面の 色（どの 色あいでも 明るさは L）"""
    def f():
        Ts = np.linspace(0, 1.05, 48, dtype=np.float32)
        Ls = np.linspace(0, 1, 48, dtype=np.float32)
        lut = np.zeros((48, 48, 3), np.float32)
        for i, T in enumerate(Ts):
            c = np.clip(fire_col(np.float32([max(T, .2)]))[0] * 1.15, 0, 1)
            for j, L in enumerate(Ls):
                lut[i, j] = match_lum(c, float(L))
        return lut
    return KF.cache('ci2_firelut', f)


def fire_lum(T, L):
    lut = fire_lut()
    ti = np.clip(np.asarray(T, np.float32) / 1.05 * 47, 0, 47)
    li = np.clip(np.asarray(L, np.float32) * 47, 0, 47) * np.ones_like(ti)
    t0 = np.minimum(ti.astype(np.int32), 46)
    l0 = np.minimum(li.astype(np.int32), 46)
    ft = (ti - t0)[..., None]
    fl = (li - l0)[..., None]
    c00, c01, c10, c11 = lut[t0, l0], lut[t0, l0 + 1], lut[t0 + 1, l0], lut[t0 + 1, l0 + 1]
    return ((c00 * (1 - fl) + c01 * fl) * (1 - ft) + (c10 * (1 - fl) + c11 * fl) * ft).astype(np.float32)


def fire_tex():
    def f():
        return (KS.fbm(H, W, 9, 801, 5).astype(np.float32), KS.fbm(H, W, 23, 811, 4).astype(np.float32))
    return KF.cache('ci2_firetex', f)


def tex_sample(tex, cx, cy, z, rot, box):
    """tex を (cx, cy) を 中心に z 倍に のばして rot 回して 読む（box＝(x0, y0, x1, y1) の 所だけ）"""
    x0, y0, x1, y1 = box
    xx, yy = grid()
    dx = xx[y0:y1, x0:x1] - cx
    dy = yy[y0:y1, x0:x1] - cy
    c, s = math.cos(rot), math.sin(rot)
    mx = (cx + (dx * c - dy * s) / z).astype(np.float32)
    my = (cy + (dx * s + dy * c) / z).astype(np.float32)
    return cv2.remap(tex, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def box_of(cx, cy, r):
    x0, x1 = int(max(0, cx - r)), int(min(W, cx + r))
    y0, y1 = int(max(0, cy - r)), int(min(H, cy + r))
    if x1 <= x0 or y1 <= y0:
        return None
    return x0, y0, x1, y1


def fire_fields(cx, cy, R, a, seed, squash, box, flat=1.0):
    """火の 玉の 形：(q：まん中からの 割合, n：もよう, n2, n3)。squash＝惑星の 中の 方だけ ちぢめる・flat＝ふちに そって 平たく"""
    x0, y0, x1, y1 = box
    xx, yy = grid()
    dx = xx[y0:y1, x0:x1] - cx
    dy = yy[y0:y1, x0:x1] - cy
    ut = dx * TAN[0] + dy * TAN[1]
    un = -(dx * NRM[0] + dy * NRM[1]) * flat
    if squash != 1.0:
        un = np.where(un > 0, un, un * squash)
    q = np.sqrt(ut * ut + un * un) / R
    t1, t2 = fire_tex()
    zr = max(R, 40.0) / 850.0                          # もようの 大きさは 火の 玉に 合わせる（＋ 外へ ながれる）
    n1 = tex_sample(t1, cx, cy, zr * (1 + .9 * a), .3 * a + seed, box)
    n2 = tex_sample(t2, cx, cy, zr * (1 + 1.6 * a), -.5 * a + seed * 1.7, box)
    n3 = tex_sample(t2, cx, cy, zr * .42 * (1 + 2.2 * a), .8 * a + seed * 2.3 + 1.0, box)   # 細かい 炎の もよう
    return q, .55 * n1 + .3 * n2 + .15 * n3, n2, n3


def fire_T(q, n, n2, n3, heat):
    """火の 形（D）と 熱さ（T）：ふちは もようで でこぼこ・中は 炎の もようで 明るい 所と 暗い 所"""
    qn = q + .62 * (n - .5) - .04
    D = KS.smoothstep(1.0, .6, qn)
    T = heat * D * np.clip(1.3 - 1.0 * q, 0, 1.3) * (.42 + 1.15 * n3) + .25 * heat * (n2 - .5) * D
    return qn, D, T


def fireball(img, cx, cy, R, heat, smoke, a, seed=0.0, squash=2.4, gain=1.9, lift=0.0, flat=1.0):
    """火の 玉（光の 量に 足す・けむりは かげ）：R＝半径・heat＝熱さ（0〜1）・smoke＝けむり（0〜1）・a＝はじまってからの 秒（もようが ふくらむ）
       lift＝けむりを 宇宙の 方へ ずらす 割合"""
    box = box_of(cx, cy, R * (1.4 + lift))
    if box is None or (heat <= .005 and smoke <= .005):
        return
    x0, y0, x1, y1 = box
    q, n, n2, n3 = fire_fields(cx, cy, R, a, seed, squash, box, flat)
    qn, D, T = fire_T(q, n, n2, n3, heat)
    if lift > 0:
        sx, sy = cx - NRM[0] * R * lift, cy - NRM[1] * R * lift
        qs, ns, n2s, _ = fire_fields(sx, sy, R * (1 + .4 * lift), a, seed + .5, 1.0, box)
        sm = KS.smoothstep(1.15, .65, qs + .4 * (ns - .5)) * smoke
    else:
        sm = KS.smoothstep(1.18, .7, qn + .3 * (n2 - .5)) * smoke
    sub = img[y0:y1, x0:x1]
    sub *= (1 - .85 * sm * np.clip(1 - T * 2.2, 0, 1))[..., None]
    sub += SMOKE * (sm * .06)[..., None]
    sub += fire_col(T) * (D * gain)[..., None]


def fireball_disp(out, cx, cy, R, heat, a, seed=0.0, fade=1.0):
    """火の 玉（画面の 色に 重ねる：白い 反転の 上でも 見える ように）。明るさは まん中から ふちへ なめらかに 下がるだけ・炎の もようは 色あいで
       （白い 中で 明るさが ちらちら かわらない ＝ 点めつに しない）"""
    box = box_of(cx, cy, R * 1.35)
    if box is None or heat <= .005:
        return
    x0, y0, x1, y1 = box
    q, n, n2, n3 = fire_fields(cx, cy, R, a, seed, 1.0, box)
    qn, D, T = fire_T(q, n, n2, n3, heat)
    af = (np.clip(KS.smoothstep(1.05, .62, q + .3 * (n - .5)) * (.75 + .25 * np.clip(T * 2.5, 0, 1)), 0, 1) * fade)[..., None]
    fc = np.clip(fire_col(np.clip(T * 1.25 + .18, 0, 1.05)) * 1.15, 0, 1)
    sub = out[y0:y1, x0:x1]
    sub[:] = sub * (1 - af) + fc * af


# ---------------------------------------------------------------- 大きな 爆発（まん中）
def boom_R(a):
    return 160.0 + 640.0 * (1 - math.exp(-a / .16))


def boom_heat(a):
    return math.exp(-a / .4)


def boom_smoke(a):
    return min(1.0, (1 - boom_heat(a)) * 1.3) * math.exp(-max(0.0, a - .55) / .45)


BC = (F[0] - NRM[0] * 30, F[1] - NRM[1] * 30)       # 火の 玉の まん中（ふちの 少し 外）


def boom_light(img, a):
    """爆発の 光で まわりが 照らされる"""
    h = boom_heat(a)
    if h < .01:
        return
    d, s, v, rf = planet_coords()
    img += ((np.exp(-(rf / 900.0) ** 2) * 2.0 + np.exp(-rf / 1300.0) * .6) * h)[..., None] * col(1.0, .5, .16)


def shock(img, a):
    """衝撃波：惑星の 上を 平たい 輪で ひろがる・宇宙の 方へ うすい 輪"""
    if a > 1.2:
        return
    xx, yy = grid()
    d, s, v, rf = planet_coords()
    dx, dy = xx - F[0], yy - F[1]
    ut = dx * TAN[0] + dy * TAN[1]
    un = -(dx * NRM[0] + dy * NRM[1])
    rho = np.sqrt(ut * ut + (np.minimum(un, 0) * 3.4) ** 2)
    Rs = 250.0 + 2400.0 * a
    w = 40.0 + 140.0 * a
    g = 2.2 * math.exp(-a / .3)
    ring = np.exp(-((rho - Rs) / w) ** 2) * (un < 15) * g
    img += ring[..., None] * col(1.0, .7, .4)
    Rp = 260.0 + 2900.0 * a
    g2 = .9 * math.exp(-a / .18)
    if g2 > .01:
        ring2 = np.exp(-((rf - Rp) / (26.0 + 60.0 * a)) ** 2) * (un > 0) * g2
        img += ring2[..., None] * col(1.0, .9, .75)


def spark_list():
    def f():
        rng = random.Random(8300)
        out = []
        for _ in range(170):
            if rng.random() < .72:
                th = math.atan2(-NRM[1], -NRM[0]) + rng.uniform(-1.6, 1.6)      # 宇宙の 方へ
            else:
                th = math.atan2(TAN[1], TAN[0]) + rng.choice((0.0, math.pi)) + rng.uniform(-.35, .35)   # 惑星に そって
            out.append((th, rng.uniform(700, 2600), rng.uniform(.3, .8), rng.uniform(.5, 1.0), rng.uniform(1.5, 3.5)))
        return out
    return KF.cache('ci2_sparks', f)


def sparks(img, a):
    """火花（まん中から とびちる・すこし ずつ おそく なる）"""
    if a > 1.3:
        return
    m = np.zeros((H, W), np.float32)
    tau = .32
    for th, v, life, b, w in spark_list():
        g = b * math.exp(-a / life)
        if g < .03:
            continue
        r = v * tau * (1 - math.exp(-a / tau))
        vel = v * math.exp(-a / tau)
        ln = max(4.0, vel * .045)
        x, y = BC[0] + r * math.cos(th), BC[1] + r * math.sin(th) + 260 * a * a
        x2, y2 = x - ln * math.cos(th), y - ln * math.sin(th)
        cv2.line(m, P8((x2, y2)), P8((x, y)), float(g), max(1, int(round(w))), cv2.LINE_AA, shift=3)
    glow_add(img, m, ((0, (1.0, .95, .8), 1.6), (3, (1.0, .6, .2), 1.0), (9, (1.0, .35, .08), .5)))


# ---------------------------------------------------------------- 雷
PB_KIND = {  # 惑星の 上を はしる 雷：(はじめ (s, d), おわり (s, d), 形)。s は 左上へ ＋・右下へ −、d は ふちから 中へ
    'L': ((60, 12), (1750, 55), 'wander'),
    'L2': ((140, 110), (1550, 380), 'zig'),
    'Rr': ((-60, 12), (-1850, 60), 'wander'),
    'R2': ((-140, 130), (-1550, 420), 'zig'),
    'D1': ((90, 50), (650, 1750), 'step'),
    'D2': ((-90, 50), (-450, 1950), 'zig'),
    'D3': ((10, 70), (260, 2350), 'wander'),
}
PBOLTS = (  # (出る コマ, 種類, 長さ（コマ）, 先の 太さ（画素）)：同じ 種類は 10コマ 以上 あける
    (39, 'L', 6, 16), (39, 'Rr', 6, 16), (41, 'D1', 5, 18), (43, 'D2', 5, 18), (46, 'L2', 5, 14), (48, 'R2', 5, 14),
    (51, 'D3', 5, 18), (54, 'L', 5, 15), (57, 'Rr', 5, 15), (60, 'D1', 5, 16), (63, 'D2', 4, 16),
    (70, 'L2', 4, 13), (75, 'D3', 4, 15), (80, 'R2', 4, 13),       # 黄色・赤・黒の 間も 1本ずつ
    (118, 'L2', 5, 13), (123, 'D2', 5, 15), (128, 'Rr', 4, 13))    # 赤い 惑星に もどった 後（雷は のこる）
BOLT_GLOW = ((0, (1, 1, 1), 1.5), (3, (1, .86, .5), 1.5), (10, (1, .55, .15), .95), (30, (1, .32, .08), .45))   # 金（超神様の 雷と 同じ 色）


def env_g(age, life):
    seq = {6: (.85, 1.0, 1.0, .75, .45, .2), 5: (.85, 1.0, .9, .55, .25), 4: (.9, 1.0, .6, .3)}[life]
    return seq[age]


def bolt_points(seed, fi, a, b, style, rough=(.14, .2)):
    rs = random.Random(seed)
    macro = KF.macro_path(rs, a, b, style)
    mid = KF.fine_jag(random.Random(seed + 1), macro, rough)
    rj = random.Random(seed * 7 + fi)                       # ビリビリ：いちばん 細かい ギザギザだけ コマごとに かわる
    pts = [mid[0]]
    for q0, q1 in zip(mid, mid[1:]):
        pts += KM._disp_ms(rj, q0, q1, (.12,))[1:]
    return pts, macro, rs


def planet_bolt_mask(fi):
    """惑星の 上を はしる 雷（ふちに そって まがる・先ほど 太い）→ 光の 地図"""
    m = None
    for k, (f0, kind, life, w1) in enumerate(PBOLTS):
        age = fi - f0
        if not (0 <= age < life):
            continue
        if m is None:
            m = np.zeros((H, W), np.float32)
        g = env_g(age, life)
        a, b, style = PB_KIND[kind]
        seed = 9100 + k * 31
        pts, macro, rs = bolt_points(seed, fi, a, b, style)
        grow = min(1.0, (age + 1) / 2)
        xy = [sd_xy(*p) for p in pts]
        draw_taper(m, xy, 2.5, w1, g, grow)
        Ltot = poly_len(macro)[-1]
        for i in range(1, len(macro) - 1):
            if rs.random() < .55 or grow < i / (len(macro) - 1):
                continue
            p, q = macro[i], macro[i + 1]
            ang2 = math.atan2(q[1] - p[1], q[0] - p[0]) + rs.choice((-1, 1)) * rs.uniform(.5, 1.0)
            ln = Ltot * rs.uniform(.12, .26)
            br = KF.fine_jag(random.Random(seed + 2 + i), [p, (p[0] + ln * math.cos(ang2), p[1] + ln * math.sin(ang2))], (.25, .3, .35))
            draw_taper(m, [sd_xy(*c) for c in br], 1.5, w1 * .45, g * .8)
    return m


def planet_bolts(img, fi, gain=1.0):
    m = planet_bolt_mask(fi)
    if m is not None:
        glow_add(img, m * gain, BOLT_GLOW)


def edge_point(c, ang):
    a = math.radians(ang)
    dx, dy = math.cos(a), math.sin(a)
    best = 1e9
    for lim, d, o in ((-30.0, dx, c[0]), (W + 30.0, dx, c[0]), (-30.0, dy, c[1]), (H + 30.0, dy, c[1])):
        if abs(d) > 1e-6:
            k = (lim - o) / d
            if k > 0:
                best = min(best, k)
    return c[0] + dx * best, c[1] + dy * best


NBOLTS = ((86, -118), (91, 158), (96, -36), (102, 100), (108, -168))   # 白い 反転の 中の 雷：(出る コマ, 向き（度）)
NB_COL = dict(red=col(.92, .16, .04), yel=col(1.0, .82, .16), core=col(1.0, .98, .82))


def nwhite_bolts(out, fi):
    """まん中から 外へ はしる 黄色と 赤の 雷（白い 反転の 上に 重ねる）"""
    for k, (f0, ang) in enumerate(NBOLTS):
        age = fi - f0
        if not (0 <= age < 4):
            continue
        g = env_g(age, 4)
        seed = 9700 + k * 37
        st = (F[0] + 70 * math.cos(math.radians(ang)), F[1] + 70 * math.sin(math.radians(ang)))
        en = edge_point(F, ang)
        pts, macro, rs = bolt_points(seed, fi, st, en, ('zig', 'wander', 'step')[k % 3])
        grow = min(1.0, (age + 1) / 2)
        m = np.zeros((H, W), np.float32)
        draw_taper(m, pts, 3.0, 15.0, g, grow)
        Ltot = poly_len(macro)[-1]
        for i in range(1, len(macro) - 1):
            if rs.random() < .5 or grow < i / (len(macro) - 1):
                continue
            p, q = macro[i], macro[i + 1]
            ang2 = math.atan2(q[1] - p[1], q[0] - p[0]) + rs.choice((-1, 1)) * rs.uniform(.5, 1.0)
            ln = Ltot * rs.uniform(.12, .24)
            br = KF.fine_jag(random.Random(seed + 2 + i), [p, (p[0] + ln * math.cos(ang2), p[1] + ln * math.sin(ang2))], (.25, .3, .35))
            draw_taper(m, br, 2.0, 7.0, g * .8)
        m1 = KF.fblur(m, 4)
        m2 = KF.fblur(m, 14)
        m3 = KF.fblur(m, 40)
        ar = np.clip(m3 * 2.4 + m2 * .9, 0, .85)[..., None]
        out[:] = out * (1 - ar) + NB_COL['red'] * ar
        ay = np.clip(m1 * 2.0 + m2 * .7, 0, 1)[..., None]
        out[:] = out * (1 - ay) + NB_COL['yel'] * ay
        ac = np.clip(m * 1.3, 0, 1)[..., None]
        out[:] = out * (1 - ac) + NB_COL['core'] * ac


# ---------------------------------------------------------------- 反転（ネガ）・色の かえ方
def luma(x):
    return x[..., 0] * .2126 + x[..., 1] * .7152 + x[..., 2] * .0722


RAMPS = dict(  # 反転した 明るさ（0＝もとの いちばん 明るい 所）→ 色
    Nyel=((0, (0, 0, 0)), (.18, (.45, .02, .02)), (.4, (1.0, .32, .05)), (.62, (1.0, .82, .12)), (.82, (1.0, .97, .6)), (1, (1.0, .97, .96))),
    Nwhite=((0, (0, 0, .02)), (.22, (.02, .06, .18)), (.45, (.12, .45, .65)), (.7, (.62, .86, .95)), (.88, (.96, .95, .98)), (1, (1.0, .96, .98))))


def s2l(c):
    c = np.asarray(c, np.float64)
    return np.where(c <= .04045, c / 12.92, ((c + .055) / 1.055) ** 2.4)


def l2s(c):
    c = np.clip(np.asarray(c, np.float64), 0, 1)
    return np.where(c <= .0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - .055)


def match_lum(c, Lt):
    """色 c（画面の 値）の 色あいの まま、明るさ（光の 量）を Lt に（明るすぎて 入らない 時は 白へ 寄せる）"""
    cl = s2l(c)
    L = float(np.dot(cl, [.2126, .7152, .0722]))
    if L < 1e-6:
        return l2s(np.full(3, Lt)).astype(np.float32)
    lo, hi = 0.0, 1.0
    for _ in range(40):
        w = (lo + hi) / 2
        base = cl * (1 - w) + w
        k = Lt / float(np.dot(base, [.2126, .7152, .0722]))
        if (base * k).max() > 1.0:
            lo = w
        else:
            hi = w
    base = cl * (1 - hi) + hi
    k = Lt / float(np.dot(base, [.2126, .7152, .0722]))
    return l2s(base * k).astype(np.float32)


NEG_LUM = ((0, .0), (.2, .012), (.4, .07), (.6, .26), (.8, .6), (.9, .78), (1, .9))   # 反転の 明るさ（光の 量）：どの 色でも 同じ


def ramp(x, stops, lum_match=True):
    def f():
        xs = np.float32([a for a, _ in stops])
        cs = np.float32([c for _, c in stops])
        if lum_match:
            lx = np.float32([a for a, _ in NEG_LUM])
            ly = np.float32([b for _, b in NEG_LUM])
            cs = np.float32([match_lum(c, float(np.interp(a, lx, ly))) for a, c in zip(xs, cs)])
            fx = np.linspace(0, 1, 65, dtype=np.float32)
            fc = np.stack([np.interp(fx, xs, cs[:, i]) for i in range(3)], -1)
            fc = np.float32([match_lum(c, float(np.interp(a, lx, ly))) for a, c in zip(fx, fc)])
            xs, cs = fx, fc
        return xs, cs
    xs, cs = KF.cache('ci2_ramp_' + repr(stops), f)
    return np.stack([np.interp(x, xs, cs[:, i]) for i in range(3)], -1).astype(np.float32)


def negative(c, name):
    L = luma(c)
    inv = np.clip(1 - L, 0, 1)
    return np.clip(ramp(inv, RAMPS[name]), 0, 1)


def rgb_split(img, px, ang=0.0):
    """赤と 青を 少し ずらす（ぶつかった 衝撃）"""
    if px < .5:
        return img
    dx, dy = px * math.cos(ang), px * math.sin(ang)
    M1 = np.float32([[1, 0, dx], [0, 1, dy]])
    M2 = np.float32([[1, 0, -dx], [0, 1, -dy]])
    out = img.copy()
    out[..., 0] = cv2.warpAffine(img[..., 0], M1, (W, H), borderMode=cv2.BORDER_REFLECT)
    out[..., 2] = cv2.warpAffine(img[..., 2], M2, (W, H), borderMode=cv2.BORDER_REFLECT)
    return out


# ---------------------------------------------------------------- 衝撃波の 波紋（白い 反転の 中）
def ripple_field(fi):
    """まん中から 広がる 輪：外向きの ずれ（画素）"""
    d, s, v, rf = planet_coords()
    t = (fi - RIPPLE['f0']) / FPS
    disp = np.zeros((H, W), np.float32)
    for k, tl in enumerate(RIPPLE['launch']):
        age = t - tl
        if age < 0:
            continue
        Rk = 40 + RIPPLE['speed'] * age
        A = RIPPLE['amp'] * math.exp(-age / RIPPLE['decay']) * (1.0 - .25 * k)
        env = np.exp(-((rf - Rk) / RIPPLE['width']) ** 2) * (1 / (1 + rf / 1400.0))
        inner = np.clip((Rk - rf) / 600.0, 0, 1) * math.exp(-age / .25) * .18
        disp += A * (env + inner * np.exp(-(rf / max(1.0, Rk)) ** 2)) * np.sin(2 * np.pi * (rf - Rk) / RIPPLE['lam'])
    return disp


def apply_ripple(img, disp, ca=.08):
    xx, yy = grid()
    d, s, v, rf = planet_coords()
    ux, uy = (xx - F[0]) / np.maximum(rf, 1), (yy - F[1]) / np.maximum(rf, 1)
    out = np.empty_like(img)
    for ch, k in ((0, 1 + ca), (1, 1.0), (2, 1 - ca)):
        mx = (xx - ux * disp * k).astype(np.float32)
        my = (yy - uy * disp * k).astype(np.float32)
        out[..., ch] = cv2.remap(img[..., ch], mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    gy, gx = np.gradient(disp)
    edge = np.clip(gx * ux + gy * uy, -1, 1)
    out += (edge * .045)[..., None]
    return np.clip(out, 0, 1)


def fire_ring(out, fi, k):
    """波紋に のって ひろがる 黄色と 赤の 火の 輪（白い 反転の 上に 重ねる）"""
    tl = RIPPLE['launch'][k]
    age = (fi - RIPPLE['f0']) / FPS - tl
    if age <= 0:
        return
    life = 1.0 if age < .22 else max(0.0, 1 - (age - .22) / .5)
    if life <= 0:
        return
    Rk = 40 + RIPPLE['speed'] * age
    th = 120.0 + 300.0 * age
    d, s, v, rf = planet_coords()
    x = (Rk - rf) / th
    t1, t2 = fire_tex()
    z = max(Rk, 150.0) / 520.0
    box = (0, 0, W, H)
    n = .6 * tex_sample(t2, F[0], F[1], z, .7 * k, box) + .4 * tex_sample(t1, F[0], F[1], z * .8, -.4 * k, box)
    n3 = tex_sample(t2, F[0], F[1], z * .4, 1.3 + k, box)
    ridge = 1 - np.abs(2 * n3 - 1)                                   # 炎の 舌（色あいで 見せる）
    xf = x + .35 * (n - .5) * (1 - KS.smoothstep(0, .4, x))          # 前の ふちは ギザギザ（明るさが まわりと ほぼ 同じ 所なので 点めつに ならない）
    prof = np.where(xf < 0, np.exp(-(xf * th / 26.0) ** 2), 1.0 - KS.smoothstep(.8, 1.8, x))
    a = (np.clip(prof * (1.0 + .1 * (n - .5)), 0, 1) * life)[..., None]
    xc = np.clip(x, 0, 1.5)
    T = np.clip(1.0 - .47 * xc + .35 * (n - .5) + .25 * (ridge - .5), .25, 1.05 - .5 * xc / 1.5)
    Lf = .72 - .56 * KS.smoothstep(0, 1.5, x)                        # 火の 明るさ（光の 量）：前は 明るい 黄色・後ろは 暗い 赤（なめらかに 1回 下がるだけ）
    out[:] = out * (1 - a) + fire_lum(T, Lf) * a


NW_BURSTS = ((3, 300, 1500, 230), (7, 900, 760, 200), (11, 820, 1750, 250), (15, 200, 900, 180), (19, 640, 2150, 260),
             (23, 1000, 1250, 210), (27, 380, 520, 190))   # 白い 反転の 中の 爆発：(f0 から の コマ, x, y, 大きさ)


def nwhite_bursts(out, fi):
    for k, (df, x, y, R0) in enumerate(NW_BURSTS):
        age = (fi - RIPPLE['f0'] - df) / FPS
        if not (0 <= age < .42):
            continue
        R = R0 * (.25 + .75 * (1 - math.exp(-age / .1)))
        heat = 1.25 * math.exp(-age / .2)                       # はじめは 黄色く 光る
        fade = 1.0 - sstep(.18, .4, age)
        fireball_disp(out, x, y, R, heat, age, seed=k * 1.3, fade=fade)


R3_FIRES = tuple((x, y, R0) for (df, x, y, R0) in NW_BURSTS if depth_at(x, y) > 40) + \
    ((sd_xy(480, 40)[0], sd_xy(480, 40)[1], 130), (sd_xy(-560, 70)[0], sd_xy(-560, 70)[1], 150))   # 赤い 惑星に のこる 火（惑星の 上の 爆発と ふちの 2つ）


def r3_fires(img, fi):
    k = fi - SEQ[-1][0]
    heat = .62 * (1 - sstep(4, 18, k))
    smoke = .55 * (1 - sstep(10, 22, k))
    t = fi / FPS
    for i, (x, y, R0) in enumerate(R3_FIRES):
        R = R0 * .55 * (1 + .05 * math.sin(fi * .5 + i * 1.7))
        fireball(img, x, y, R * 1.15, heat, smoke, .4 + .3 * t, seed=2.0 + i, squash=1.0, gain=1.4, lift=.6, flat=1.35)


# ---------------------------------------------------------------- 1コマ
def frame_M(fi):
    t = fi / FPS
    u = fi / IMPACT
    img = scene_lin('R', t, sun=0.0, I=0.0, rim=.35)
    meteors(img, t)
    big_meteor(img, t)
    img = zoom(img, 1.0 + .05 * u * u)
    if fi < 4:
        img *= (fi + 1) / 4.0                              # バグの さいごの 黒から ふっと 入る
    return finish(img)


def frame_Env(fi):
    k = fi - IMPACT
    t = fi / FPS
    I = (10.0, 9.0, 8.0, 7.0, 6.0, 5.0)[k]
    img = scene_lin('B', t, sun=1.0, I=I, rim=1.0)
    img += col(.3, .55, 1.0) * (.5, .42, .34, .28, .22, .16)[k]
    img = zoom(img, 1.05 + .02 * sstep(0, 5, k))
    out = finish(img)
    return rgb_split(out, (8.0, 5.0, 3.0, 2.0, 0.0, 0.0)[k], TILT)


def frame_Boom(fi):
    t = fi / FPS
    a = (fi - BOOM) / FPS
    sun = .35 + .65 * sstep(.3, .9, a)
    I = 1.4 * sstep(.4, .95, a)
    img = scene_lin('R', t, sun=sun, I=I, rim=.6 + .4 * sun)
    boom_light(img, a)
    shock(img, a)
    fireball(img, BC[0], BC[1], boom_R(a), boom_heat(a), boom_smoke(a), a)
    sparks(img, a)
    planet_bolts(img, fi)
    img = zoom(img, 1.0 + .07 * (1 - KF.ease_out(a / .3)))
    out = finish(img)
    return rgb_split(out, 6.0 if fi == BOOM else (3.0 if fi == BOOM + 1 else 0.0), TILT)


def frame_color(fi, m, k):
    t = fi / FPS
    a = (fi - BOOM) / FPS
    if m == 'K':
        img = scene_lin('K', t, sun=1.0, I=1.5)
    else:
        img = scene_lin('R', t, sun=1.0, I=1.35 if m == 'Nyel' else 1.75)
        fireball(img, BC[0], BC[1], boom_R(a), boom_heat(a), boom_smoke(a), a)
    planet_bolts(img, fi)
    out = finish(img)
    if m == 'Nyel':
        return rgb_split(negative(out, 'Nyel'), 7.0 if k == 0 else 3.0, TILT)
    return rgb_split(out, (4.0 if m == 'R2' else 5.0) if k == 0 else 0.0, TILT)


def frame_Nwhite(fi):
    t = fi / FPS
    img = scene_lin('R', t, sun=1.0, I=1.5)
    neg = negative(finish(img), 'Nwhite')
    disp = ripple_field(fi)
    neg = apply_ripple(neg, disp)
    neg = rgb_split(neg, 3.0 * math.exp(-(fi - RIPPLE['f0']) / 6.0), TILT)
    for k in FIRE_RINGS:
        fire_ring(neg, fi, k)
    nwhite_bursts(neg, fi)
    nwhite_bolts(neg, fi)
    return neg


def frame_R3(fi):
    t = fi / FPS
    k = fi - SEQ[-1][0]
    sh = sstep(R3_SHRINK[0], R3_SHRINK[1], k)
    sun = 1.0 - .9 * sh
    expo = EXPO * (1 - .965 * sstep(R3_SHRINK[0] + 2, N - SEQ[-1][0] - 1, k))
    img = scene_lin('R', t, sun=sun, I=0.0, rim=1.0 - .7 * sh)
    r3_fires(img, fi)
    planet_bolts(img, fi, 1.0 - sh)
    img *= expo / EXPO
    fl = np.zeros_like(img)
    flare(fl, 'R', 1.75 - .7 * sh, kz=math.sqrt(1.75) * (1 - .9 * sh))    # まん中の 光：小さく なる（明るさは のこす）
    img += fl
    out = finish(img)
    disp = ripple_field(fi)
    return apply_ripple(out, disp * .8 * (1 - sh), ca=.03)


def frame(fi):
    m, k, n = mode_at(fi)
    if m == 'M':
        out = frame_M(fi)
    elif m == 'Env':
        out = frame_Env(fi)
    elif m == 'Boom':
        out = frame_Boom(fi)
    elif m in ('Nyel', 'R2', 'K'):
        out = frame_color(fi, m, k)
    elif m == 'Nwhite':
        out = frame_Nwhite(fi)
    else:
        out = frame_R3(fi)
    return (np.clip(out, 0, 1) * 255 + .5).astype(np.uint8)


def main(out, which=None):
    os.makedirs(out, exist_ok=True)
    for fi in (which or range(N)):
        im = frame(fi)
        cv2.imwrite(os.path.join(out, f'f{fi + 1:03d}.png'), cv2.cvtColor(im, cv2.COLOR_RGB2BGR))
        print('f', fi + 1, flush=True)


if __name__ == '__main__':
    o = sys.argv[1]
    w = [int(a) - 1 for a in sys.argv[2:]] or None
    main(o, w)
