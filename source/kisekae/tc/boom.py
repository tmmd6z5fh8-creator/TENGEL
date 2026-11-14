# ルーレットの 高い 方の 爆発（第4.171版・まさちゃん 2026/11/14 16:18
#   「④トレーニングセンターの神様馬、幻の馬ルーレットで高い方が当選し、プチュンした後は、リアルな爆発と一緒に獲得ポイントの表示するようにして！」）
#   プチュンで 真っ暗に なった すぐ あとの 爆発の 動画（黒の 上に 火の 玉・煙・火花）を、計算で 1コマずつ 作る（写真・素材は 使わない）。
#   ・流れの 計算（2次元・けむりの 流れ）：燃料の かたまりに 火が ついて ふくらむ（燃えた 所から 気体が ふくらむ）→ 熱い 所は 上へ（浮力）→ うずが 巻く（渦の 強め）→ 冷えて 黒い 煙に
#     はじめに 外へ 飛ぶ 火の すじ（燃料の かけらが 燃えながら 飛ぶ）が 数本
#   ・絵：温度 → 火の 色（暗い 赤 → 橙 → 黄 → 白：明るさは 上限なしで 計算して さいごに 映画の ような 丸め方）・すすが 手前で 火を かくす・煙は 近くの 火に 照らされる・
#     にじむ 光（ブルーム）・飛ぶ 火花（すじ・だんだん 赤く）・はじめの 1回の 閃光・広がる うすい 輪・はじめ だけ 画面の ゆれ・うすい 粒
#   ・点めつ：明るく なるのは はじめの 1回 だけ（0.1秒で いちばん 明るく → あとは ゆっくり 暗く：kisekae/flash_px.py で 確かめる）
#   python3 boom.py <コマの フォルダ> [はじめ] [おわり]        … コマ（f%03d.png・1170×1842：390×614 の 3倍）。SCALE=0.5 で ためしの 小さい 絵
#   python3 boom.py --encode <コマの フォルダ> <出す mp4> [CRF]  … H.264・30コマ/秒・音なし
#   python3 boom.py --sheet <コマの フォルダ> <出す jpg>         … 見くらべる 用の 一覧
#   音（tc_se_boom）は kisekae/tc/snd/sfx_boom.py
import math, os, subprocess, sys
import numpy as np
import cv2
from scipy import fft as sfft

FPS = 30
DUR = 2.6                      # 秒（78コマ）：火は 1.9秒で 消える → のこりは うすい 煙 → さいごの 0.5秒で 真っ暗へ（動画が おわる ときに 絵が とばない）
NF = int(round(DUR * FPS))
W0, H0 = 1170, 1842            # 出す 絵（トレーニングセンターの 舞台 390×614 の 3倍）
SC = float(os.environ.get('SCALE', '1'))
OW, OH = int(round(W0 * SC)), int(round(H0 * SC))
SIMK = 2.0 / 3.0               # 流れの 計算は 2倍の 大きさ（780×1228）で して、絵に する ときに 3倍へ のばす（火は もともと やわらかい・火花は 3倍で 描く）
SW, SH = int(round(OW * SIMK)), int(round(OH * SIMK))
PAD = 0.22                     # 計算の 場所は 見える 所より 左右に 22% ずつ 広い（火の 玉は 画面の 幅より 大きい：はみ出した 分も 計算して、かべに 当たって 平らに ならない ように）
SWS = SW + 2 * int(round(SW * PAD)); SX0 = (SWS - SW) // 2
SUB = 4                        # 1コマを 4つに 分けて 計算
DT = 1.0 / (FPS * SUB)
CX, CY = 0.5, 0.47             # 爆発の まん中（テロップの 少し 下）
PXS = SW / 780.0               # 長さの 倍率（計算の 幅 780 の とき 1）
SEED = 171
JSEED = int(os.environ.get('JSEED', '303'))      # 飛ぶ 火の すじの 乱数（形を えらぶ：下の 見くらべで 決めた）
EXPAND = 15.5                  # 燃えた 燃料 1 に つき ふくらむ 面積（火の 玉の 大きさ：半径が 画面の 幅の 0.55 くらい ＝ 手前に 出る テロップ〈幅 372・高さ 249〉の 上と 下に 火が 見える）


def fbm(rng, h, w, base, octs=5, pers=0.55):
    """なめらかな 雑音（-1〜1）：あらい 乱数を のばして 重ねる"""
    out = np.zeros((h, w), np.float32); amp = 1.0; tot = 0.0; s = base
    for _ in range(octs):
        gh, gw = max(2, int(math.ceil(h / s)) + 2), max(2, int(math.ceil(w / s)) + 2)
        g = rng.normal(0, 1, (gh, gw)).astype(np.float32)
        big = cv2.resize(g, (int(gw * s), int(gh * s)), interpolation=cv2.INTER_CUBIC)
        oy, ox = rng.integers(0, max(1, big.shape[0] - h)), rng.integers(0, max(1, big.shape[1] - w))
        out += amp * big[oy:oy + h, ox:ox + w]; tot += amp; amp *= pers; s = max(2.0, s / 2)
    return out / tot


class Sim:
    def __init__(self):
        rng = self.rng = np.random.default_rng(SEED)
        h, w = SH, SWS; self.h, self.w = h, w
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); self.xx, self.yy = xx, yy
        cx, cy = CX * w, CY * h; self.cx, self.cy = cx, cy
        dx, dy = xx - cx, yy - cy; r = np.sqrt(dx * dx + dy * dy) + 1e-3; self.rx, self.ry, self.r = dx / r, dy / r, r
        R0 = 0.11 * SW                                                      # 燃料の かたまりの 半径
        n1 = fbm(rng, h, w, 70 * PXS, 4); n2 = fbm(rng, h, w, 26 * PXS, 4)
        edge = R0 * (1 + 0.42 * n1 + 0.16 * n2)                             # でこぼこの ふち
        self.F = (1.5 * np.clip((edge - r) / (0.25 * R0) + 0.5, 0, 1) * (0.62 + 0.38 * np.clip(fbm(rng, h, w, 18 * PXS, 3) * 1.6 + 0.5, 0, 1))).astype(np.float32)      # 燃料（中に むらが ある）
        # 火が つく 時刻（所に よって ばらばら：0〜0.3秒）＝ かたまりの 中が あちこち 順に 燃える（まん中が すぐ 暗く ならない）
        self.fuse = (0.3 * np.clip(fbm(rng, h, w, 30 * PXS, 3) * 1.5 + 0.45, 0, 1) * np.clip(r / (R0 * 0.35), 0.25, 1)).astype(np.float32)
        self.T = np.zeros((h, w), np.float32); self.S = np.zeros((h, w), np.float32)
        self.D = np.clip(fbm(rng, h, w, 20 * PXS, 5, 0.62) * 1.9 + 0.5, 0, 1).astype(np.float32)      # 火の こまかい 模様（流れに 乗って のびる）
        self.dn = [np.clip(fbm(rng, h, w, 15 * PXS, 4, 0.6) * 1.9 + 0.5, 0, 1).astype(np.float32) for _ in range(2)]
        # はじめの いきおい（外へ・むらが ある）
        sp = 260 * PXS * np.clip(1 - r / (R0 * 2.6), 0, 1) * (1 + 0.6 * n1)
        self.u = (self.rx * sp).astype(np.float32); self.v = (self.ry * sp).astype(np.float32)
        # 波の 数（周期的な 計算：ふちは スポンジで 消す ので 回りこまない）
        ky = sfft.fftfreq(h).astype(np.float32)[:, None] * 2 * np.pi; kx = sfft.rfftfreq(w).astype(np.float32)[None, :] * 2 * np.pi
        self.kx, self.ky = kx, ky; k2 = kx * kx + ky * ky; k2[0, 0] = 1.0; self.k2 = k2
        m = 0.07; ex = np.clip(np.minimum(xx, w - 1 - xx) / (m * SW), 0, 1); ey = np.clip(np.minimum(yy, h - 1 - yy) / (m * SW), 0, 1)
        self.sponge = (ex * ey) ** 0.5
        # うずを 足す 雑音（3まいを ずらして 使う）
        self.turb = [(fbm(rng, h, w, 44 * PXS, 4), fbm(rng, h, w, 44 * PXS, 4)) for _ in range(3)]
        self.turb2 = [(fbm(rng, h, w, 15 * PXS, 3), fbm(rng, h, w, 15 * PXS, 3)) for _ in range(3)]      # こまかい うず（もこもこ した ふち）
        # 外へ 飛ぶ 火の すじ（燃えながら 飛ぶ 燃料の かけら）
        self.jets = []; angs = []; rng = np.random.default_rng(JSEED)
        while len(angs) < 15:                                               # 向きは ばらばら（近すぎる 2本は 作らない）
            a = rng.uniform(0, 2 * np.pi)
            if all(abs((a - b + np.pi) % (2 * np.pi) - np.pi) > 0.2 for b in angs): angs.append(a)
        for i, a in enumerate(angs):
            big = i < 6                                                     # 太くて 遠くへ 行く 6本 ＋ 細くて 短い 9本
            sp_ = (rng.uniform(1400, 2300) if big else rng.uniform(750, 1600)) * PXS * (1.0 if math.sin(a) < 0.3 else 0.8)
            self.jets.append(dict(x=cx + math.cos(a) * R0 * 0.5, y=cy + math.sin(a) * R0 * 0.5, vx=math.cos(a) * sp_, vy=math.sin(a) * sp_, life=rng.uniform(0.4, 0.75) if big else rng.uniform(0.2, 0.45),
                                  r=(rng.uniform(7, 11) if big else rng.uniform(4, 7)) * PXS, amt=rng.uniform(0.8, 1.3) if big else rng.uniform(0.5, 0.9)))
        self.t = 0.0

    def advect(self, q, u, v, dt, border=cv2.BORDER_CONSTANT):
        return cv2.remap(q, self.xx - dt * u, self.yy - dt * v, cv2.INTER_LINEAR, borderMode=border, borderValue=0)

    def mac(self, q, u, v, dt):
        """MacCormack（にじみが 少ない 運び方）：行って もどって 差の 半分を もどす・はみ出しは おさえる"""
        a = self.advect(q, u, v, dt); b = self.advect(a, u, v, -dt); c = a + 0.5 * (q - b)
        k = np.ones((3, 3), np.uint8); lo, hi = cv2.erode(a, k), cv2.dilate(a, k)
        return np.clip(c, lo, hi)

    def splat(self, q, x, y, rad, amt):
        x0, x1 = max(0, int(x - 3 * rad)), min(self.w, int(x + 3 * rad) + 1); y0, y1 = max(0, int(y - 3 * rad)), min(self.h, int(y + 3 * rad) + 1)
        if x1 <= x0 or y1 <= y0: return
        g = np.exp(-((self.xx[y0:y1, x0:x1] - x) ** 2 + (self.yy[y0:y1, x0:x1] - y) ** 2) / (2 * rad * rad)); q[y0:y1, x0:x1] += amt * g

    def step(self):
        dt = DT; t = self.t; u, v, T, F, S = self.u, self.v, self.T, self.F, self.S
        # 飛ぶ 火の すじ：通った 所に 燃料と 熱と いきおいを 置く
        for j in self.jets:
            if t > j['life']: continue
            k = 1 - t / j['life']
            self.splat(F, j['x'], j['y'], j['r'], 0.075 * j['amt'] * k * dt * 60); self.splat(T, j['x'], j['y'], j['r'] * 0.8, 0.3 * k * dt * 60)
            self.splat(u, j['x'], j['y'], j['r'] * 1.6, 0.25 * j['vx'] * dt * 60 * k); self.splat(v, j['x'], j['y'], j['r'] * 1.6, 0.25 * j['vy'] * dt * 60 * k)
            j['vx'] *= math.exp(-2.4 * dt); j['vy'] = j['vy'] * math.exp(-2.4 * dt) + 420 * PXS * dt; j['x'] += j['vx'] * dt; j['y'] += j['vy'] * dt
        # 燃える：火が つく 時刻を すぎた 燃料・熱い 所の 燃料
        ign = np.clip((t - self.fuse) / 0.02, 0, 1) if t < 0.3 else 1.0
        hot = np.clip((T - 0.18) / 0.25, 0, 1)
        rate = F * np.maximum(ign, 0.5 * hot) * 6.0                           # 1秒 あたりの 燃える 量
        burn = np.minimum(F, rate * dt)
        F -= burn; S += 5.0 * burn
        T += np.maximum(1.45 - T, 0) * (1 - np.exp(-22.0 * burn))             # 燃えた 所は 炎の 温度へ（ふくらんで うすく なっても 温度は 炎の 温度：量に 比例させると ふくらんだ 分 だけ 暗く なって まん中が 黒く ぬける）
        src = EXPAND * burn / dt                                              # 燃えた 所から ふくらむ（発散）：燃えた 燃料 1 に つき 面積 EXPAND
        dil = np.exp(-src * dt); F *= dil; S *= dil                           # ふくらんだ 分 だけ うすく なる（量は ふえない：これが ないと 燃料が ふくらみと いっしょに ふえて 止まらない）
        # 冷える（熱い ほど 速く）・煙は ゆっくり うすく
        Tb = cv2.GaussianBlur(T, (0, 0), 11 * PXS); thin = np.clip((T - Tb) / (T + 0.05), 0, 1)
        late = max(0.0, t - 1.1)
        T /= (1 + dt * ((0.45 + 0.95 * T * T + 2.4 * thin + 1.5 * late) * (0.55 + 0.9 * self.dn[1]))); np.minimum(T, 1.9, out=T); S *= math.exp(-dt * 0.22)
        # 力：浮力（熱い 所は 上へ・煙は 少し 重い）・うずを 強める・雑音の うず
        v += dt * (-460 * PXS * T)
        wz = (np.roll(v, -1, 1) - np.roll(v, 1, 1) - np.roll(u, -1, 0) + np.roll(u, 1, 0)) * 0.5
        aw = np.abs(wz); gx = (np.roll(aw, -1, 1) - np.roll(aw, 1, 1)) * 0.5; gy = (np.roll(aw, -1, 0) - np.roll(aw, 1, 0)) * 0.5
        gl = np.sqrt(gx * gx + gy * gy) + 1e-5; eps = 9.0
        u += dt * eps * (gy / gl) * wz; v += dt * eps * (-gx / gl) * wz
        tb = self.turb[int(t * 7) % 3]; amp = 950 * PXS * np.clip(T + 0.4 * S, 0, 1.2) * (1.0 if t > 0.05 else 0.3)
        u += dt * amp * tb[0]; v += dt * amp * tb[1]
        ts = self.turb2[int(t * 11) % 3]; u += dt * 0.6 * amp * ts[0]; v += dt * 0.6 * amp * ts[1]
        # 運ぶ
        un = self.advect(u, u, v, dt, cv2.BORDER_REPLICATE); vn = self.advect(v, u, v, dt, cv2.BORDER_REPLICATE)
        self.T = self.mac(T, u, v, dt); self.F = self.mac(F, u, v, dt); self.S = self.mac(S, u, v, dt); self.fuse = self.advect(self.fuse, u, v, dt, cv2.BORDER_REPLICATE)
        self.D = self.mac(self.D, u, v, dt)
        self.D += dt * 1.6 * (self.dn[int(t * 5) % 2] - self.D)                 # 模様は 少しずつ 新しい 雑音へ（のびきって のっぺり しない）
        src = self.advect(src.astype(np.float32), u, v, dt)
        # ふくらみを 入れて、のこりの わき出しを 消す（周期的な 計算）
        uh, vh = sfft.rfft2(un, workers=2), sfft.rfft2(vn, workers=2)
        div = 1j * self.kx * uh + 1j * self.ky * vh - sfft.rfft2(src, workers=2)
        ph = div / (-self.k2); ph[0, 0] = 0
        uh -= 1j * self.kx * ph; vh -= 1j * self.ky * ph
        self.u = sfft.irfft2(uh, s=(self.h, self.w), workers=2).astype(np.float32) * self.sponge; self.v = sfft.irfft2(vh, s=(self.h, self.w), workers=2).astype(np.float32) * self.sponge
        self.u *= math.exp(-0.5 * dt); self.v *= math.exp(-0.5 * dt)
        self.T *= self.sponge; self.S *= self.sponge; self.F *= self.sponge
        self.t += dt


# ---------------------------------------------------------------- 火花（ばらばらに 飛ぶ 点）
class Sparks:
    def __init__(self, rng, n=900):
        a = rng.uniform(0, 2 * np.pi, n); sp = np.exp(rng.normal(math.log(900), 0.55, n)) * (OW / 1170.0)
        up = np.where(np.sin(a) < 0, 1.15, 0.85)
        self.x = np.full(n, CX * OW) + np.cos(a) * rng.uniform(0, 30, n) * (OW / 1170.0); self.y = np.full(n, CY * OH) + np.sin(a) * rng.uniform(0, 30, n) * (OW / 1170.0)
        self.vx = np.cos(a) * sp; self.vy = np.sin(a) * sp * up
        self.life = rng.uniform(0.35, 1.9, n) * np.where(rng.random(n) < 0.15, 1.5, 1.0); self.t0 = rng.uniform(0.0, 0.07, n)
        self.size = rng.uniform(1.6, 4.0, n) * (OW / 1170.0); self.drag = rng.uniform(1.6, 3.4, n); self.flick = rng.uniform(0, 6.28, n); self.g = 620 * (OW / 1170.0)
        self.px, self.py = self.x.copy(), self.y.copy()

    def step(self, dt, t):
        on = t >= self.t0
        self.px, self.py = self.x.copy(), self.y.copy()
        k = np.exp(-self.drag * dt)
        self.vx = np.where(on, self.vx * k, self.vx); self.vy = np.where(on, self.vy * k + self.g * dt, self.vy)
        self.x = np.where(on, self.x + self.vx * dt, self.x); self.y = np.where(on, self.y + self.vy * dt, self.y)

    def draw(self, img, t):
        """img：(h, w, 3) の 明るさ（上限なし）に 足す。1コマの 間に 動いた 分は すじ（点を ならべて 置く：なめらかな ふち）"""
        h, w = img.shape[:2]; age = (t - self.t0) / self.life; idx = np.nonzero((age > 0) & (age < 1))[0]
        if not len(idx): return
        a = age[idx]; heat = (1 - a) ** 1.3 * (0.75 + 0.25 * np.sin(self.flick[idx] + t * 40)); sz = self.size[idx] * (0.6 + 0.4 * (1 - a))
        col = np.stack([(0.04 + 0.55 * (1 - a) ** 3) * heat * 10, (0.25 + 0.75 * (1 - a) ** 1.2) * heat * 12, heat * 15], 1).astype(np.float32)      # BGR：白っぽい 黄 → 橙 → 赤
        x0, y0, x1, y1 = self.px[idx], self.py[idx], self.x[idx], self.y[idx]
        K = np.clip(np.ceil(np.hypot(x1 - x0, y1 - y0) / 0.8), 1, 70).astype(int); lay = np.zeros((h, w, 3), np.float32)
        for kk in range(int(K.max())):
            m = K > kk; f = (kk + 0.5) / K[m]
            xs = x0[m] + (x1[m] - x0[m]) * f; ys = y0[m] + (y1[m] - y0[m]) * f; c = col[m] * (sz[m] ** 1.5 / np.sqrt(K[m]))[:, None]
            xi = np.floor(xs).astype(int); yi = np.floor(ys).astype(int); fx = (xs - xi).astype(np.float32); fy = (ys - yi).astype(np.float32)
            for dx_, dy_, wg in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)), (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
                X = xi + dx_; Y = yi + dy_; ok = (X >= 0) & (X < w) & (Y >= 0) & (Y < h)
                np.add.at(lay, (Y[ok], X[ok]), c[ok] * wg[ok][:, None])
        sg = max(0.6, 1.0 * w / 1170.0)
        img += cv2.GaussianBlur(lay, (0, 0), sg) * (2.4 * sg)


# ---------------------------------------------------------------- 絵に する
def sstep(a, b, x):
    x = np.clip((x - a) / (b - a), 0, 1); return x * x * (3 - 2 * x)


def fire_color(T):
    """温度 → 火の 色（明るさは 上限なし）。BGR：暗い 赤 → 赤橙 → 橙 → 黄 → 白"""
    t = np.clip(T, 0, 2.2)
    r = sstep(0.1, 0.5, t) * (1 + 1.4 * np.clip(t - 0.55, 0, 2))
    g = sstep(0.2, 0.95, t) ** 1.25 * (1 + 1.5 * np.clip(t - 0.85, 0, 2))
    b = sstep(0.7, 1.45, t) ** 1.6 * (1 + 1.2 * np.clip(t - 1.2, 0, 2))
    inten = t ** 1.8 * 2.6
    return (np.stack([b * 0.85, g * 0.82, r * 1.0], -1) * inten[..., None]).astype(np.float32)


def aces(x):
    a, b, c, d, e = 2.51, 0.03, 2.43, 0.59, 0.14
    return np.clip((x * (a * x + b)) / (x * (c * x + d) + e), 0, 1)


def render(sim, sparks, t, rng):
    up = lambda q: cv2.resize(np.ascontiguousarray(q[:, SX0:SX0 + SW]), (OW, OH), interpolation=cv2.INTER_CUBIC)
    T, S, D = np.maximum(up(sim.T), 0), np.maximum(up(sim.S), 0), np.clip(up(sim.D), 0, 1)
    k = OW / 1170.0
    # 火：温度の 色（こまかい 模様で 明るい 所と 暗い 所）・すすが 手前で かくす（冷えた 煙の 濃い 所ほど）
    Sd = S * (0.45 + 1.1 * cv2.GaussianBlur(D, (0, 0), 2.5 * k))                # 煙の 濃さ（むら）
    E = fire_color(T * (0.5 + 0.95 * D))
    E *= (0.1 + 0.9 * np.exp(-2.2 * Sd * np.clip(1.0 - T, 0, 1)))[..., None]
    # 煙：もこもこ した かたまり（濃さを ぼかした 形の 向きで 明るい 側と 暗い 側）・近くの 火に 照らされる
    glow = cv2.GaussianBlur(E, (0, 0), 46 * k)
    sa = cv2.GaussianBlur(Sd, (0, 0), 9.0 * k); a_s = (1 - np.exp(-3.0 * sa))[..., None]
    sb = cv2.GaussianBlur(Sd, (0, 0), 18 * k); gx = cv2.Sobel(sb, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(sb, cv2.CV_32F, 0, 1, ksize=3)
    lx, ly = (OW * CX - np.arange(OW, dtype=np.float32))[None, :], (OH * CY - np.arange(OH, dtype=np.float32))[:, None]
    ll = np.sqrt(lx * lx + ly * ly) + 1; shade = np.clip(0.6 - 60 * k ** -1 * (gx * lx / ll + gy * ly / ll) + 30 * k ** -1 * gy, 0.25, 1.6)[..., None]      # 火の ある まん中の 側 ＋ 上からの うすい 光
    smoke = (np.array([0.016, 0.015, 0.014], np.float32) + glow * np.array([0.5, 0.56, 0.66], np.float32)) * shade
    img = E + smoke * a_s * (1 - np.clip(E.max(-1, keepdims=True), 0, 1) * 0.7)
    # 火花
    sparks.draw(img, t)
    # はじめの 閃光（1回）：まん中の 白い 玉 ＋ 画面に 広がる 橙の 光
    fl = math.exp(-t / 0.09) * min(1.0, t / 0.03) * float(np.clip((0.62 - t) / 0.2, 0, 1))      # 0コマ目は 真っ暗（動画が 止まって いる 間に 光が 見えない）・0.6秒で なめらかに 0 へ（とちゅうで 急に 消えない）
    if fl > 0:
        yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32); rr = np.sqrt((xx - CX * OW) ** 2 + (yy - CY * OH) ** 2) / OW
        core = np.exp(-(rr / min(0.07 + 0.9 * t, 0.2)) ** 2) * 6.0 * fl; wide = np.exp(-(rr / 0.55) ** 1.6) * 0.42 * fl
        img += core[..., None] * np.array([0.75, 0.92, 1.0], np.float32) + wide[..., None] * np.array([0.18, 0.5, 1.0], np.float32)
    # 広がる うすい 輪（衝撃の 波）
    if t < 0.42:
        yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32); rr = np.sqrt((xx - CX * OW) ** 2 + (yy - CY * OH) ** 2)
        R = (60 + 2300 * (1 - math.exp(-t / 0.22))) * k; ring = np.exp(-((rr - R) / (34 * k)) ** 2) * 0.09 * (1 - t / 0.42) ** 1.5 * min(1.0, t / 0.05)
        img += ring[..., None] * np.array([0.7, 0.85, 1.0], np.float32)
    # にじむ 光（明るい 所 だけ）
    br = np.maximum(img - 0.85, 0)
    for sg, am in ((7, 0.55), (22, 0.4), (64, 0.3)):
        img += am * cv2.GaussianBlur(br, (0, 0), sg * k)
    # 横に のびる 光の すじ（レンズ）：はじめの 明るい 間 だけ
    if t < 0.5:
        img += 0.07 * (1 - t / 0.5) * cv2.GaussianBlur(br, (0, 0), sigmaX=150 * k, sigmaY=3 * k)
    # うすい 粒（フィルムの 粒：暗い 所の しま を かくす）
    img += rng.normal(0, 0.006, img.shape[:2]).astype(np.float32)[..., None] * (0.4 + img)
    out = aces(np.maximum(img, 0) * 0.7 * float(np.clip((DUR - 1.0 / FPS - t) / 0.5, 0, 1)) ** 1.5) ** (1 / 2.2)
    # はじめ だけ 画面の ゆれ（0.5秒で おさまる）
    sh = math.exp(-t / 0.16) * 13 * k if t > 0.02 else 0
    if sh > 0.3:
        M = np.float32([[1, 0, sh * math.sin(t * 97)], [0, 1, sh * math.cos(t * 71 + 1)]]); out = cv2.warpAffine(out, M, (OW, OH), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return (np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)


def main(out, f0=0, f1=NF):
    os.makedirs(out, exist_ok=True)
    sim = Sim(); rng = np.random.default_rng(SEED + 1); sparks = Sparks(np.random.default_rng(SEED + 2))
    for f in range(f1):
        t = f / FPS
        if f >= f0:
            cv2.imwrite(os.path.join(out, f'f{f:03d}.png'), render(sim, sparks, t, rng), [cv2.IMWRITE_PNG_COMPRESSION, 3])
            print('boom', f, flush=True)
        for s in range(SUB):
            sim.step(); sparks.step(DT, sim.t)


def encode(src, dst, crf='20'):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS), '-i', os.path.join(src, 'f%03d.png'), '-c:v', 'libx264', '-preset', 'slow', '-crf', str(crf), '-profile:v', 'high', '-pix_fmt', 'yuv420p',
                    '-movflags', '+faststart', '-tag:v', 'avc1', '-an', dst], check=True)
    print(dst, f'{os.path.getsize(dst) / 1e6:.2f}MB')


def sheet(src, dst, cols=10, w=180):
    fs = sorted(f for f in os.listdir(src) if f.startswith('f') and f.endswith('.png'))[::3]
    ims = [cv2.imread(os.path.join(src, f)) for f in fs]; h = int(ims[0].shape[0] * w / ims[0].shape[1])
    rows = (len(ims) + cols - 1) // cols; S_ = np.zeros((rows * h, cols * w, 3), np.uint8)
    for i, im in enumerate(ims):
        S_[(i // cols) * h:(i // cols + 1) * h, (i % cols) * w:(i % cols + 1) * w] = cv2.resize(im, (w, h), interpolation=cv2.INTER_AREA)
    cv2.imwrite(dst, S_, [cv2.IMWRITE_JPEG_QUALITY, 88])


if __name__ == '__main__':
    if sys.argv[1] == '--encode': encode(sys.argv[2], sys.argv[3], *(sys.argv[4:5]))
    elif sys.argv[1] == '--sheet': sheet(sys.argv[2], sys.argv[3])
    else: main(sys.argv[1], *(int(a) for a in sys.argv[2:4]))
