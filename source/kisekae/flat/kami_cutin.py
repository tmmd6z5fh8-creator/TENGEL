"""超神様的中の カットイン（宇宙）：1コマずつ 描く 絵。1170×2532（iPhone の 画面の 画素・たて長の 画面いっぱい）・1秒 30コマ・51コマ（1.7秒）
   まさちゃん「超神様的中ボタンを追加して！ 超神様的中の4回に1回ランダムで発生」「送った一個目の動画のようなカットインの素材を作成したい！」
   （宇宙エフェクト 28枚・聞いたら「超神様的中に カットイン」「画面いっぱい」）
   → 送ってくれた 絵は 見るだけ（なぞらない・字「Heat.」は 使わない）。惑星の ふち（ななめの 地平線）・まん中で ギラッと 光る 太陽・とぶ 岩 を
     一から 計算で 描いて、同じ 流れ（ふつうの 色 → 色が 反転 → 青 → 赤 → 白い 反転の 中を 水の 波紋の ような 衝撃波 → 暗く → もどる）に した。
   点めつ：画面の 大きな 明るさの 入れかわりは 4回だけ（反転の 中の 色の かわりは 明るさを そろえて 色だけ かえる）・送ってくれた 絵の さいごの
     チカチカ（0.2秒に 5回）は やめて 1回で 暗く。波紋の 輪は 明るさを あまり かえず ゆがみと 色の ずれで 見せる。
   python3 flat/kami_cutin.py <出力フォルダ> [コマ番号（1〜）…]  → f001.png …（何回 作っても 同じ）"""
import os, sys, math, random
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
import kami_film as KF
import kami_storm as KS

W, H = KF.W, KF.H                     # 1170 × 2532
FPS, N = 30, 51                       # 1.7秒
F = (585.0, 1200.0)                   # 太陽（光の まん中・惑星の ふちの 上）
TILT = math.radians(35.0)             # 地平線の かたむき（左上 → 右下）
PR = 3300.0                           # 惑星の 半径（画面の 画素）
TAN = np.array([math.cos(TILT), math.sin(TILT)])
NRM = np.array([-math.sin(TILT), math.cos(TILT)])   # ふち → 惑星の 中へ（左下）
PC = np.array(F) + NRM * PR                          # 惑星の まん中（画面の 外・左下）

# ---------------------------------------------------------------- 時間わり（コマ：はじめ, おわり（ふくまない）, 場面）
SEQ = ((0, 8, 'R'),        # ふつうの 色（赤い 宇宙）：太陽が ギラッと 大きく なる
       (8, 9, 'Ncyan'),    # 反転①（水色）
       (9, 10, 'Nviolet'),  # 反転（すみれ色）
       (10, 12, 'Nyel'),   # 反転（白地に 黄色と 赤）
       (12, 14, 'Nblue'),  # 反転（白地に 青）
       (14, 16, 'Ncyan2'),  # 反転（白地に 水色）
       (16, 18, 'B'),      # 青い 宇宙
       (18, 20, 'R2'),     # 赤い 宇宙（太陽が もっと 大きく）
       (20, 44, 'Nwhite'),  # 白い 反転の 中を 衝撃波の 波紋
       (44, 46, 'Dark'),   # 暗く（赤い 波紋の ふちだけ）
       (46, 49, 'R3'),     # 赤と むらさきに もどる（波紋の なごり）
       (49, 51, 'Fade'))   # 黒へ（超神様の 動画の はじめの 黒に つなぐ）
EXPO = .78                            # 光の 量（ふちを くっきり・反転の 黒い 帯は ふちに そって 細く）
RIPPLE = dict(f0=20, speed=2200.0, lam=112.0, width=150.0, amp=72.0, decay=.5, launch=(0.0, .08, .17))   # 衝撃波（秒は f0 から）


def mode_at(fi):
    for a, b, m in SEQ:
        if a <= fi < b:
            return m, fi - a, b - a
    return 'Fade', 1, 2


def col(*c):
    return np.float32(c)


# ---------------------------------------------------------------- 画面の 座標
def grid():
    def f():
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        return xx, yy
    return KF.cache('ci_grid', f)


def planet_coords():
    """惑星の ふちからの 深さ d（中が +）・ふちに そった 長さ s（太陽が 0・右下が +）・球の 上の 深さ v（ふちの 近くは ちぢむ）"""
    def f():
        xx, yy = grid()
        qx, qy = xx - PC[0], yy - PC[1]
        r = np.sqrt(qx * qx + qy * qy)
        d = PR - r
        a0 = math.atan2(F[1] - PC[1], F[0] - PC[0])
        ang = np.arctan2(qy, qx) - a0
        ang = (ang + np.pi) % (2 * np.pi) - np.pi
        s = -ang * PR                                  # 右下へ +（時計回りの 逆）
        v = PR * np.arccos(np.clip(1 - np.clip(d, 0, None) / PR, -1, 1))
        rf = np.hypot(xx - F[0], yy - F[1])
        return d.astype(np.float32), s.astype(np.float32), v.astype(np.float32), rf.astype(np.float32)
    return KF.cache('ci_pc', f)


# ---------------------------------------------------------------- 色の くみ
PAL = dict(
    R=dict(near=col(1.0, .42, .1), mid=col(.42, .05, .035), far=col(.03, .006, .012), neb=col(.75, .16, .06), haze=col(1.0, .3, .12),
           atm_in=col(1.0, .82, .95), atm_out=col(1.0, .34, .42), atm_far=col(.55, .18, .62),
           lit=col(.95, .42, .95), deep=col(.05, .03, .16), cloud=col(1.0, .86, 1.0),
           core=col(1.0, .97, .9), halo=col(1.0, .55, .18), streak=col(1.0, .3, .1), spike=col(1.0, .62, .42), rock_lit=col(1.0, .55, .25)),
    B=dict(near=col(.45, .75, 1.0), mid=col(.03, .1, .42), far=col(.006, .01, .05), neb=col(.12, .3, .9), haze=col(.35, .6, 1.0),
           atm_in=col(.85, .93, 1.0), atm_out=col(.35, .55, 1.0), atm_far=col(.4, .25, .85),
           lit=col(.6, .45, 1.0), deep=col(.03, .03, .16), cloud=col(.9, .92, 1.0),
           core=col(.92, .97, 1.0), halo=col(.4, .7, 1.0), streak=col(.25, .55, 1.0), spike=col(.6, .8, 1.0), rock_lit=col(.55, .75, 1.0)))


def space(p):
    """宇宙（動かない）：太陽の まわりの 光・赤い 星雲・ちり・星"""
    def f():
        P = PAL[p]
        xx, yy = grid()
        d, s, v, rf = planet_coords()
        n1 = KS.fbm(H, W, 5, 501, 5)
        n2 = KS.fbm(H, W, 14, 517, 4)
        base = P['far'][None, None] * np.ones((H, W, 1), np.float32)
        g1 = np.exp(-rf / 900.0)[..., None]
        g2 = np.exp(-rf / 330.0)[..., None]
        img = base + P['mid'] * g1 * 1.1 + P['near'] * g2 * .55
        # 星雲（太陽から 右上へ ひろがる もや・ちりの すじ は 暗く）
        neb = np.clip((n1 - .42) * 2.2, 0, 1) ** 1.4 * (.35 + .65 * np.exp(-rf / 1400.0))
        dust = np.clip((n2 - .55) * 3.0, 0, 1)
        img += P['neb'][None, None] * (neb * (1 - .6 * dust))[..., None] * .55
        img *= (1 - .45 * dust * np.exp(-rf / 2000.0))[..., None]
        # 右上の すみは 暗く
        vig = np.clip(1 - ((xx - W * .2) / W) ** 2 * .25 - ((H * .9 - yy) / H) ** 2 * .35, .35, 1)
        img *= vig[..., None]
        # 星（小さな 光の 点）
        rng = np.random.default_rng(530 if p == 'R' else 531)
        st = np.zeros((H, W), np.float32)
        for _ in range(900):
            x, y = rng.uniform(0, W), rng.uniform(0, H)
            b = rng.pareto(2.2) * .25
            st[int(y), int(x)] += min(b, 2.5)
        st = cv2.GaussianBlur(st, (0, 0), .9) * 6
        img += (st[..., None] * col(1.0, .9, .85)) * (d < -4)[..., None]
        return img.astype(np.float32)
    return KF.cache('ci_space_' + p, f)


def planet(p):
    """惑星（動かない）：ふちに そって まがる 雲・太陽に 近い ほど 明るい・ふちの 大気の 光 → (色, 惑星の 形)"""
    def f():
        P = PAL[p]
        d, s, v, rf = planet_coords()
        # 雲の 絵（球の 上の 座標 s・v で 読む → ふちの 近くは ぎゅっと ちぢむ）
        TW, TH = 4096, 2048
        tex = .55 * KS.fbm(TH, TW, 18, 611, 6) + .45 * KS.fbm(TH, TW, 7, 623, 5)
        streak = KS.fbm(TH, TW // 6, 22, 641, 4)
        streak = cv2.resize(streak, (TW, TH), interpolation=cv2.INTER_CUBIC)
        tex = .7 * tex + .3 * streak
        mx = np.clip(s / 2.2 + TW / 2, 0, TW - 2).astype(np.float32)      # 見える はんいは ±1400 → つぎ目なし
        my = np.clip(v / 1.6, 0, TH - 2).astype(np.float32)
        cl = cv2.remap(tex.astype(np.float32), mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        cloud = np.clip((cl - .47) * 3.6, 0, 1) ** 1.2
        light = np.clip(1 - v / 2900.0, 0, 1) ** 1.25 * (.45 + .55 * np.exp(-(s / 1900.0) ** 2))
        base = P['deep'][None, None] + (P['lit'] - P['deep'])[None, None] * (light * .8)[..., None]
        img = (base * (.55 + .8 * cl[..., None]) + P['cloud'] * (cloud * (.12 + 1.0 * light))[..., None] * .8) * .85
        # 夜の 側の 町の 光（小さく・まばら）
        rng = np.random.default_rng(650)
        city = np.zeros((H, W), np.float32)
        for _ in range(500):
            x, y = rng.uniform(0, W), rng.uniform(0, H)
            city[int(y), int(x)] = rng.uniform(.3, 1.0)
        city = cv2.GaussianBlur(city, (0, 0), 1.2) * 5 * np.clip((v - 500) / 900, 0, 1) * (cl > .45)
        img += city[..., None] * col(1.0, .6, .3) * .5
        # 大気（ふちの すぐ 内の 白い 光の 帯・外へ にじむ 光）
        near = np.exp(-(s / 900.0) ** 2)
        a_in = (np.exp(-np.clip(d, 0, None) / 9.0) * 1.4 + np.exp(-np.clip(d, 0, None) / 45.0) * .45) * (.5 + 1.5 * near) * (d > 0)
        img += P['atm_in'] * a_in[..., None]
        a_out = (np.exp(np.clip(d, None, 0) / 30.0) * (.5 + 1.6 * near) + np.exp(np.clip(d, None, 0) / 220.0) * (.1 + .45 * near)) * (d <= 0)
        img_out = P['atm_out'] * (a_out * near)[..., None] + P['atm_far'] * (a_out * (1 - near))[..., None]
        mask = np.clip(d / 2.0 + .5, 0, 1)
        return img.astype(np.float32), img_out.astype(np.float32), mask.astype(np.float32)
    return KF.cache('ci_planet_' + p, f)


def flare(img, p, I):
    """太陽の 光：しん・まわりの 光・よこに のびる 光の 帯・たての とげ・ふちの 小さな 光（I＝強さ）"""
    P = PAL[p]
    xx, yy = grid()
    dx, dy = xx - F[0], yy - F[1]
    r2 = dx * dx + dy * dy
    k = math.sqrt(I)
    img += P['core'] * (I * (3.0 * np.exp(-r2 / (16.0 * k) ** 2) + 1.0 * np.exp(-r2 / (48.0 * k) ** 2)))[..., None]
    img += P['halo'] * (I * .5 * np.exp(-r2 / (150.0 * k) ** 2) + I * .12 * np.exp(-r2 / (420.0 * k) ** 2))[..., None]
    ax = np.abs(dx)
    img += P['streak'] * (I * (1.3 * np.exp(-(dy / (4.0 + 2 * k)) ** 2) * np.exp(-ax / (900.0 * k)) +
                              .3 * np.exp(-(dy / 34.0) ** 2) * np.exp(-ax / (520.0 * k))))[..., None]
    ay = np.abs(dy)
    img += P['spike'] * (I * .7 * np.exp(-(dx / 3.0) ** 2) * np.exp(-ay / (150.0 * k)))[..., None]
    # ななめの 細い とげ 2本
    for a in (math.radians(62), math.radians(-62)):
        u = dx * math.cos(a) + dy * math.sin(a)
        w_ = -dx * math.sin(a) + dy * math.cos(a)
        img += P['spike'] * (I * .25 * np.exp(-(w_ / 2.5) ** 2) * np.exp(-np.abs(u) / (170.0 * k)))[..., None]


def sparkles(img, p, t):
    """ふちの 上と 宇宙の 小さな 光（たての 光の すじ つき）"""
    P = PAL[p]
    rng = random.Random(700)
    for k in range(9):
        if k < 5:
            sv = rng.uniform(-1400, 1300)
            x, y = F[0] + TAN[0] * sv, F[1] + TAN[1] * sv
        else:
            x, y = rng.uniform(100, W - 100), rng.uniform(150, H - 150)
        tw = .6 + .4 * math.sin(t * rng.uniform(9, 15) + rng.uniform(0, 6))
        g = rng.uniform(.5, 1.0) * tw
        x0, x1 = int(max(0, x - 40)), int(min(W, x + 40))
        y0, y1 = int(max(0, y - 420)), int(min(H, y + 420))
        if x1 <= x0 or y1 <= y0:
            continue
        xx, yy = np.meshgrid(np.arange(x0, x1, dtype=np.float32), np.arange(y0, y1, dtype=np.float32))
        dx, dy = xx - x, yy - y
        sp = 1.6 * np.exp(-(dx * dx + dy * dy) / 30.0) + .5 * np.exp(-(dx / 2.2) ** 2) * np.exp(-np.abs(dy) / 70.0) + \
            .3 * np.exp(-(dy / 2.2) ** 2) * np.exp(-np.abs(dx) / 18.0)
        img[y0:y1, x0:x1] += P['spike'] * (sp * g)[..., None]


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


def rocks(img, p, t, inv=False):
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
        # 太陽（うしろ）からの 光：ふちが 光る
        lx, ly = F[0] - cx, F[1] - cy
        ln = math.hypot(lx, ly) + 1e-6
        L = np.array([lx / ln * .9, ly / ln * .9, -.35])
        L /= np.linalg.norm(L)
        ndl = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
        rim = np.clip(nx * L[0] + ny * L[1], 0, 1) ** 2.2 * (1 - nz) ** .6
        amb = np.clip(nz * .6 + ny * .25, 0, 1)
        near = math.exp(-ln / 1500.0)
        c = col(.045, .03, .03)[None, None] * rot[..., 4:5] + col(.1, .05, .13) * amb[..., None] * .35
        c = c + P['rock_lit'] * (ndl * .22 + rim * 2.4)[..., None] * (.3 + .9 * near)
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


def debris(img, p, t):
    """ちり（太陽から 外へ ゆっくり とぶ 小さな 光の 粒）"""
    P = PAL[p]
    m = np.zeros((H, W), np.float32)
    for a, r0, v, sz, b in debris_list():
        r = r0 + v * t
        x, y = F[0] + r * math.cos(a), F[1] + r * math.sin(a) * 1.4
        if 0 <= x < W and 0 <= y < H:
            cv2.circle(m, (int(x * 4), int(y * 4)), int(sz * 4), float(b), -1, cv2.LINE_AA, shift=2)
    m = cv2.GaussianBlur(m, (0, 0), .8)
    img += P['spike'] * m[..., None] * .9


# ---------------------------------------------------------------- 1まいの 宇宙（色）
def flare_I(fi):
    t = fi / FPS
    if fi < 8:
        return .55 + .8 * KF.ease_out(fi / 7.0)
    if fi < 18:
        return 1.35
    if fi < 20:
        return 1.75
    return 1.5


def scene(p, fi, expo=1.0):
    """expo：光の 量を へらす（白く とんだ 所を 暗く すると 灰色に なるので、まとめる 前に へらす）"""
    t = fi / FPS
    sp = space(p)
    pl, pout, pm = planet(p)
    img = sp * (1 - pm[..., None]) + pl * pm[..., None] + pout
    flare(img, p, flare_I(fi))
    sparkles(img, p, t)
    debris(img, p, t)
    rocks(img, p, t)
    if expo != 1.0:
        img *= expo
    img = KF.bloom(img)
    return KF.tonemap(img)


# ---------------------------------------------------------------- 反転（ネガ）・色の かえ方
def luma(x):
    return x[..., 0] * .2126 + x[..., 1] * .7152 + x[..., 2] * .0722


RAMPS = dict(  # 反転した 明るさ（0＝もとの いちばん 明るい 所）→ 色
    Ncyan=((0, (0, 0, .02)), (.25, (.02, .12, .35)), (.55, (.15, .62, .85)), (.8, (.55, .95, 1.0)), (1, (.85, 1.0, 1.0))),
    Nviolet=((0, (0, 0, 0)), (.3, (.2, .05, .45)), (.6, (.45, .35, 1.0)), (.85, (.75, .78, 1.0)), (1, (.92, .93, 1.0))),
    Nyel=((0, (0, 0, 0)), (.18, (.45, .02, .02)), (.4, (1.0, .32, .05)), (.62, (1.0, .82, .12)), (.82, (1.0, .97, .6)), (1, (1.0, .97, .96))),
    Nblue=((0, (0, 0, .03)), (.25, (.02, .08, .5)), (.55, (.1, .35, 1.0)), (.82, (.7, .82, 1.0)), (1, (.98, .97, 1.0))),
    Ncyan2=((0, (0, .02, .04)), (.25, (.0, .3, .45)), (.55, (.2, .85, .95)), (.82, (.8, 1.0, 1.0)), (1, (.98, 1.0, 1.0))),
    Nwhite=((0, (0, 0, .02)), (.22, (.02, .06, .18)), (.45, (.12, .45, .65)), (.7, (.62, .86, .95)), (.88, (.96, .95, .98)), (1, (1.0, .96, .98))))


def s2l(c):
    c = np.asarray(c, np.float64)
    return np.where(c <= .04045, c / 12.92, ((c + .055) / 1.055) ** 2.4)


def l2s(c):
    c = np.clip(np.asarray(c, np.float64), 0, 1)
    return np.where(c <= .0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - .055)


def lum_lin(c):
    return float(np.dot(s2l(c), [.2126, .7152, .0722]))


def match_lum(c, Lt):
    """色 c（画面の 値）の 色あいの まま、明るさ（光の 量）を Lt に（明るすぎて 入らない 時は 白へ 寄せる）"""
    cl = s2l(c)
    L = float(np.dot(cl, [.2126, .7152, .0722]))
    if L < 1e-6:
        return l2s(np.full(3, Lt)).astype(np.float32)
    lo, hi = 0.0, 1.0
    for _ in range(40):                       # 白へ 寄せる 量 w を さがす
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


NEG_LUM = ((0, .0), (.2, .012), (.4, .07), (.6, .26), (.8, .6), (.9, .78), (1, .9))   # 反転の 明るさ（光の 量）：どの 色でも 同じ（色を かえても 点めつに しない）


def ramp(x, stops, lum_match=True):
    xs = np.float32([a for a, _ in stops])
    cs = np.float32([c for _, c in stops])
    if lum_match:
        lx = np.float32([a for a, _ in NEG_LUM])
        ly = np.float32([b for _, b in NEG_LUM])
        cs = np.float32([match_lum(c, float(np.interp(a, lx, ly))) for a, c in zip(xs, cs)])
        # あいだの 明るさも そろえる：細かく きざんで から 色を 合わせる
        fx = np.linspace(0, 1, 65, dtype=np.float32)
        fc = np.stack([np.interp(fx, xs, cs[:, i]) for i in range(3)], -1)
        fc = np.float32([match_lum(c, float(np.interp(a, lx, ly))) for a, c in zip(fx, fc)])
        xs, cs = fx, fc
    return np.stack([np.interp(x, xs, cs[:, i]) for i in range(3)], -1).astype(np.float32)


def negative(c, name):
    """反転：明るさを ひっくり返して 色の 地図で ぬる（もとの 色も 少し のこす）"""
    L = luma(c)
    inv = np.clip(1 - L, 0, 1)
    out = ramp(inv, RAMPS[name])
    return np.clip(out, 0, 1)


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


# ---------------------------------------------------------------- 衝撃波の 波紋
def ripple_field(fi):
    """まん中（太陽）から 広がる 輪：外向きの ずれ（画素）"""
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
        inner = np.clip((Rk - rf) / 600.0, 0, 1) * math.exp(-age / .25) * .18       # 輪の 内の なごりの ゆれ
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
    # 輪の ふちの ガラスの ような 光と かげ（うすく）
    gy, gx = np.gradient(disp)
    edge = np.clip(gx * ux + gy * uy, -1, 1)
    out += (edge * .045)[..., None]
    return np.clip(out, 0, 1)


# ---------------------------------------------------------------- 1コマ
def frame(fi):
    m, k, n = mode_at(fi)
    t = fi / FPS
    if m in ('R', 'R2'):
        img = scene('R', fi, EXPO)
    elif m in ('R3', 'Dark', 'Fade'):
        expo = dict(Dark=(.07, .09), R3=(.42, .5, .58), Fade=(.3, .1))[m][k]
        img = scene('R', fi, expo)
    elif m == 'B':
        img = scene('B', fi, EXPO)
    else:
        img = scene('R', fi, EXPO)
    if m.startswith('N'):
        neg = negative(img, m)
        if m == 'Nwhite':
            disp = ripple_field(fi)
            neg = apply_ripple(neg, disp)
            neg = rgb_split(neg, 3.0 * math.exp(-(fi - RIPPLE['f0']) / 6.0), TILT)
        else:
            neg = rgb_split(neg, 7.0 if k == 0 else 3.0, TILT)
        out = neg
    elif m == 'Dark':
        disp = ripple_field(fi)
        base = apply_ripple(img, disp * .7, ca=.03)
        ring = np.clip(np.abs(disp) / RIPPLE['amp'] * 2.2, 0, 1)
        out = np.clip(base + ring[..., None] * col(1.0, .22, .1) * .45, 0, 1)
    elif m in ('R3', 'Fade'):
        disp = ripple_field(fi)
        out = apply_ripple(img, disp * (.8 if m == 'R3' else .5), ca=.03)
    elif m == 'R2':
        out = rgb_split(img, 4.0 if k == 0 else 0.0, TILT)
    elif m == 'B':
        out = rgb_split(img, 5.0 if k == 0 else 0.0, TILT)
    else:
        out = img
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
