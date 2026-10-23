"""神様的中 ③ 神様的中・おめでとう御座います（第4.50版）：1コマずつ 描く 絵。1170×2532（iPhone の 画面の 画素）・1秒 30コマ
   まさちゃん「じゃあ最後のシーンいくね！ここは、GODの文字のところを、神様的中、GAMEの文字のところを、おめでとう御座います！にして！
   ファイルは全部で78枚あるよ！」
   → 送ってくれた コマは 見るだけ（描き写さない・字・形・構図・動きの 組み立ては 姫の オリジナル）。
     字は Dela Gothic One（アプリに 入れて いる フォント）を 本当の 立体（前の 面・まるい 金の ふち・うしろへの 厚い 厚み）に して、カメラから 見た 形（遠近）で 描く。
     字の 面は 夕やけの 金（上は まぶしい 金 → だいだい → 波の ような こい 赤の 線 → 赤 → 下は 明るい だいだい）・ふちは まわりの 光の 映りこみ（金）。
     金の 粒は 本当の 立体（ごつごつ した 金の かたまり：面ごとに 映りこみ）が 回りながら 手前へ とんで くる（近い 粒は ぼける・速い 粒は ぶれる）。
   流れ（0秒＝③ の はじめ＝② の おわりの まっ白）：
     白が ひく → 金の 粒が はじけて「神」の 寄り → 大きな 粒が 手前を 横切って「様」→ 金の 粒が はじけて「的」→ 大きな 粒が 横切って「中」
     → 金の 粒の 大爆発の 中に「神様／的中／おめでとう／御座います！」（ななめ）→ 正面へ 回りながら ひく（うしろに 金の 鳥居）→ 光が すべる → キラキラ
   画面 全体は 回さない・ゆらさない（動くのは 字と 金の 粒だけ・寄りは 横に ゆっくり）。点めつ：どの 1秒にも 3回 以下
   第4.49版：まさちゃん「このシーンからの文字をもっと立体的に、雷が、不定期に文字の周りを走ってる感じにして！あと⛩️ももっとリアルに豪華な感じにして！
     最後のシーン、神様的中、おめでとう御座います、の文字には雷がビリビリビリビリ不定期に走ってる演出にして！」
     → 字：厚みを 約1.6倍・ふちと 側面に 左上からの 光（光る 所と かげ）・さいごは 少し ななめ 下から 見上げる 角度（側面が 見える）・字の かげが 鳥居に おちる。
       雷：字の ふちを はしる 雷・字から 字へ とぶ 雷・ふちの 小さな ビリビリ（どれも 不定期・同じ 所には つづけて 出さない（点めつ））。
       鳥居：kami_torii3.py（朱ぬりの 明神鳥居の 本当の 立体：黒い 漆の 笠木・金の 台輪・帯・飾り金具・金の わくの 額「天眼」）
   第4.50版：まさちゃん「三枚目の写真の！を消して、四枚目の写真は後2秒長くして！」「小石のようなエフェクトは全てリアルな小判に変えて！」
     → 字は「御座います」（！なし）・さいごの 字の 場面を 2秒 のばす（全体 6.2秒：光が もう 1回 すべる・雷は さいごまで）・
       金の 粒は ぜんぶ 本物の ような 慶長小判（kami_koban.py：茣蓙目・扇の わくの 桐の 紋・壹两・光次と 花押／裏は 花押）が 回りながら とぶ
   python3 flat/kami_film3.py <出力フォルダ> [コマ番号（1〜）…]  → f001.png …（何回 作っても 同じ）"""
import os, sys, math, random
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
sys.path.insert(0, K)
import kami_art as KA
import kami_film as KF
import kami_torii3 as T3
import kami_koban as KB

S = 3.0
W, H = KF.W, KF.H
FPS = 30
N0 = 186                              # 6.2秒（第4.50版：さいごの 字の 場面を 2秒 のばした）。雷・キラッの 乱数は この 長さで 作る（前の コマは かわらない）
XN = 0                                # さいごの 場面を さらに のばす コマ（のばした 所の 雷と キラッは べつの 乱数）。声を「おめでとう御座います！」に もどしたので 0（6.2秒のまま）
N = N0 + XN
SSA = 2                               # 側面は 2倍で 描いて もどす
FOCAL = 1500.0                        # カメラ（絵の 画素）
ENV_R = 2600.0                        # 映りこみの 空までの きょり（1000 単位）
CXS, CYS = W / 2, H / 2

# ---------------------------------------------------------------- 時刻（③ の はじめが 0）
TT = dict(WIN=(0.0, .05, .3),                                          # 白（まっ白 → 消える）
          CU=((0.0, .55), (.55, 1.08), (1.08, 1.62), (1.62, 2.15)),    # 神・様・的・中 の 寄り
          BU=((0.0, 1, .55), (.5, 0, None), (1.05, 1, 1.62), (1.57, 0, None), (2.1, 2, None)),
          # 金の 粒（時刻・強さ 0＝大きな 粒が 手前を 横切る（光らない）・1＝はじける・2＝いちばん 大きい・寄りが かわる 時に 消す 時刻）
          LOGO=2.15, TURN=(2.15, 3.0),                                 # 神様／的中／おめでとう／御座います！（ななめ → 正面へ 回りながら ひく）
          SHINE=((3.1, 3.75), (5.15, 5.8)))                            # 光が すべる（2回）


def smoothstep(e0, e1, x):
    return KF.smoothstep(e0, e1, x)


def sstep(e0, e1, x):
    return KF.sstep(e0, e1, x)


def ease_out(u):
    return KF.ease_out(u)


# ---------------------------------------------------------------- 金の 映りこみ（夕やけの 金：正距円筒の 絵）
ENV_H, ENV_W = 256, 512


def env_map():
    """まわりの 光：たて＝上（+90°）→ 下（-90°）・よこ＝向き（0＝カメラの 前・±180＝カメラの うしろ）→ RGB（1 より 明るい 所 あり）"""
    def f():
        el = np.linspace(90, -90, ENV_H, dtype=np.float32)[:, None] * np.ones((1, ENV_W), np.float32)
        az = np.linspace(-180, 180, ENV_W, endpoint=False, dtype=np.float32)[None, :] * np.ones((ENV_H, 1), np.float32)
        stops = ((-90, (16, 5, 1)), (-55, (56, 18, 3)), (-28, (150, 52, 8)), (-10, (232, 108, 18)), (-3, (255, 178, 64)),
                 (0, (255, 236, 170)), (3, (255, 176, 46)), (10, (220, 104, 16)), (22, (255, 164, 48)), (42, (255, 212, 118)),
                 (68, (255, 236, 184)), (90, (255, 246, 214)))
        xs = np.array([s for s, _ in stops], np.float32)
        cs = np.array([c for _, c in stops], np.float32) / 255
        col = np.stack([np.interp(el, xs, cs[:, i]) for i in range(3)], -1).astype(np.float32)
        nz = KA.fbm(ENV_H, ENV_W, 8, 903, 4, .55)
        col *= (.8 + .4 * nz)[..., None]

        def dang(a0):
            return np.degrees(np.angle(np.exp(1j * np.radians(az - a0))))
        hi = np.zeros_like(el)
        for a0, e0, sa, se, g in ((150, 34, 24, 16, 1.5), (-150, 50, 18, 12, 1.1), (35, 22, 14, 10, .7), (-60, 28, 16, 10, .6)):
            hi += np.exp(-(dang(a0) / sa) ** 2 - ((el - e0) / se) ** 2) * g
        for a0, wd, g in ((122, 4.0, 1.4), (168, 2.5, 1.2), (-132, 5.0, 1.1), (-98, 3.0, 1.0), (64, 6.0, .7), (-36, 5.0, .6)):
            hi += np.exp(-(dang(a0) / wd) ** 2) * smoothstep(-4, 16, el) * (1 - smoothstep(58, 84, el)) * g
        col = col + np.float32([1.0, .94, .76])[None, None, :] * hi[..., None]
        return col.astype(np.float32)
    return KF.cache('env3', f)


def env_lvl(level):
    """映りこみの 地図：0＝はっきり（金）・1＝少し ぼけ（漆の つや）・2＝大きく ぼけ（まわりの 光：面の 明るさ）"""
    def f():
        e = env_map()
        sig = (0.0, 2.5, 34.0)[level]
        if sig <= 0:
            return e
        p = int(sig * 3)
        b = cv2.copyMakeBorder(e, p, p, 0, 0, cv2.BORDER_REPLICATE)
        b = cv2.copyMakeBorder(b, 0, 0, p, p, cv2.BORDER_WRAP)
        return cv2.GaussianBlur(b, (0, 0), sig)[p:-p, p:-p].copy()
    return KF.cache(f'env3_{level}', f)


def env_lookup(rv, rot=0.0, level=0):
    """映りこみの 向き rv（…×3：カメラ：x 右・y 下・z 前）→ 色"""
    env = env_lvl(level)
    x, y, z = rv[..., 0], rv[..., 1], rv[..., 2]
    el = np.degrees(np.arcsin(np.clip(-y, -1, 1)))
    az = np.degrees(np.arctan2(x, z)) + rot
    u = ((az + 180) % 360) / 360 * ENV_W
    v = np.clip((90 - el) / 180 * (ENV_H - 1), 0, ENV_H - 1.001)
    u0 = np.floor(u).astype(np.int32)
    v0 = np.floor(v).astype(np.int32)
    fu = (u - u0).astype(np.float32)[..., None]
    fv = (v - v0).astype(np.float32)[..., None]
    u0 %= ENV_W
    u1 = (u0 + 1) % ENV_W
    v1 = np.minimum(v0 + 1, ENV_H - 1)
    a = env[v0, u0] * (1 - fu) + env[v0, u1] * fu
    b = env[v1, u0] * (1 - fu) + env[v1, u1] * fu
    return a * (1 - fv) + b * fv


# 字の 面（夕やけの 金：上から まぶしい 金 → 金 → だいだい → 波の ような こい 赤の 線 → 赤 → 下は 明るい だいだい）
FACE = ((0.0, (255, 232, 140)), (.08, (255, 206, 64)), (.2, (255, 170, 30)), (.31, (255, 196, 70)), (.4, (248, 132, 18)),
        (.455, (212, 74, 8)), (.48, (112, 20, 3)), (.505, (200, 56, 8)), (.64, (184, 38, 6)), (.8, (214, 70, 10)), (.93, (250, 136, 34)),
        (1.0, (255, 186, 76)))
GOLD_TINT = np.float32([1.0, .86, .55])       # ふちの 金
KEY_T = np.array([-.45, -.78, -.45])
KEY_T = KEY_T / np.linalg.norm(KEY_T)         # 左上 手前からの 光（字の ふちと 側面の 光る 所と かげ）
SIDE_TINT = np.float32([1.0, .62, .26])       # 側面（こい 金 → こげ茶）


# ---------------------------------------------------------------- 立体の 字（前の 面の 地図・側面の 線）
def _normals(h):
    gx = cv2.Sobel(h, cv2.CV_32F, 1, 0, ksize=3) / 8
    gy = cv2.Sobel(h, cv2.CV_32F, 0, 1, ksize=3) / 8
    n = np.dstack([-gx, -gy, -np.ones_like(h)])
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return n.astype(np.float32)


def _segments(m, dep, Wt, Ht):
    """形の ふちの 線の きれはし：[x0, y0, x1, y1, 外向き nx, ny, 厚み]（絵の 画素）"""
    b = (m > .5).astype(np.uint8)
    cs, _ = cv2.findContours(b, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    out = []
    for c in cs:
        if len(c) < 6:
            continue
        c = cv2.approxPolyDP(c, .7, True)[:, 0, :].astype(np.float64)
        if len(c) < 3:
            continue
        p0 = c
        p1 = np.roll(c, -1, axis=0)
        dv = p1 - p0
        L = np.hypot(dv[:, 0], dv[:, 1]) + 1e-9
        nx, ny = dv[:, 1] / L, -dv[:, 0] / L
        mid = (p0 + p1) / 2
        tx = np.clip(np.round(mid[:, 0] + nx * 2.0).astype(int), 0, Wt - 1)
        ty = np.clip(np.round(mid[:, 1] + ny * 2.0).astype(int), 0, Ht - 1)
        ins = b[ty, tx] > 0
        nx = np.where(ins, -nx, nx)
        ny = np.where(ins, -ny, ny)
        out.append(np.stack([p0[:, 0], p0[:, 1], p1[:, 0], p1[:, 1], nx, ny, np.full(len(c), dep)], 1))
    return out


def _outlines(m, k, cx, cy, row, sp_px=10.0):
    """形の ふちを 等間隔の 点に（雷が はしる 道）：[dict(P＝点（字の 座標）, N＝外向き, L＝ふちに そった 長さ, tot＝1周, row＝行)]"""
    b = (m > .5).astype(np.uint8)
    cs, _ = cv2.findContours(b, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    Hm, Wm = b.shape
    out = []
    for c in cs:
        c = c[:, 0, :].astype(np.float64)
        if len(c) < 40:
            continue
        kern = np.ones(5) / 5
        c = np.stack([np.convolve(np.r_[c[-2:, i], c[:, i], c[:2, i]], kern, 'valid') for i in (0, 1)], 1)
        cc = np.vstack([c, c[:1]])
        Lc = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(cc, axis=0).T))])
        tot = Lc[-1]
        n = max(8, int(tot / sp_px))
        ss = np.linspace(0, tot, n, endpoint=False)
        P = np.stack([np.interp(ss, Lc, cc[:, 0]), np.interp(ss, Lc, cc[:, 1])], 1)
        tg = np.roll(P, -1, 0) - np.roll(P, 1, 0)
        tg /= np.linalg.norm(tg, axis=1, keepdims=True) + 1e-9
        nr = np.stack([tg[:, 1], -tg[:, 0]], 1)
        tx = np.clip(np.round(P[:, 0] + nr[:, 0] * 3).astype(int), 0, Wm - 1)
        ty = np.clip(np.round(P[:, 1] + nr[:, 1] * 3).astype(int), 0, Hm - 1)
        if (b[ty, tx] > 0).mean() > .5:                       # 内 向きなら 返す（1周 まとめて）
            nr = -nr
        out.append(dict(P=(P - [cx, cy]) / k, N=nr, L=ss / k, tot=tot / k, row=row))
    return out


def make_obj(parts, k, cx, cy, Wt, Ht, glint_n=14, seed=1, style='stripe', extra=None):
    """parts＝[(形 0〜1, 面取りの はば（画素）, 厚み（1000 単位）, しまの 座標 0〜1 か None)]（どれも 同じ 大きさの 絵）。
       k：1 単位あたりの 画素・(cx, cy)：字の まん中（画素）。→ 立体（地図は 3段：細かい → あらい）"""
    alpha = np.zeros((Ht, Wt), np.float32)
    hgt = np.zeros((Ht, Wt), np.float32)
    rim = np.zeros((Ht, Wt), np.float32)
    sv = np.zeros((Ht, Wt), np.float32)
    segs = []
    outl = []
    for j, (m, w, dep, svm) in enumerate(parts):
        if m.max() < .5:
            continue
        outl += _outlines(m, k, cx, cy, j)
        d = KA.dist_in(m)
        h = w * .75 * KA.bevel(d, w)
        h -= np.exp(-((d - w * 1.2) / (w * .16)) ** 2) * w * .06          # みぞ（ふちと 面の さかい）
        sel = (m > .5) | (m > alpha)
        hgt = np.where(sel, hgt + h if j else h, hgt)                         # 2つめ からは 上に のせる（額の 字）
        rim = np.where(sel, 1 - smoothstep(w * .92, w * 1.3, d), rim)
        if svm is not None:
            sv = np.where(sel, svm, sv)
        alpha = np.maximum(alpha, m)
        segs += _segments(m, dep, Wt, Ht)
    hgt = cv2.GaussianBlur(hgt, (0, 0), max(.6, .0025 * 1000 * k))
    n = _normals(hgt)
    segs = np.concatenate(segs, 0)
    segs[:, 0:4:2] = (segs[:, 0:4:2] - cx) / k
    segs[:, 1:4:2] = (segs[:, 1:4:2] - cy) / k
    # キラッの 場所の 候補（ふちの 上：ばらばらに）
    cand = np.argwhere((rim > .6) & (alpha > .9))
    rng = np.random.default_rng(seed)
    pick = []
    em_px = 1000 * k
    if len(cand):
        for i in rng.permutation(len(cand))[:4000]:
            y_, x_ = cand[i]
            if all((x_ - a) ** 2 + (y_ - b) ** 2 > (.42 * em_px) ** 2 for a, b in pick):
                pick.append((x_, y_))
            if len(pick) >= glint_n:
                break
    lv = []
    m4 = np.dstack([alpha, alpha * n[..., 0], alpha * n[..., 1], alpha * sv]).astype(np.float32)     # alpha を かけて おく（ふちで まざっても くずれない）
    r2 = (alpha * rim).astype(np.float32)
    ex = (alpha * extra).astype(np.float32) if extra is not None else None
    kk, ccx, ccy = k, cx, cy
    for j in range(3):
        lv.append(dict(m4=m4, rim=r2, extra=ex, k=kk, c=(ccx, ccy)))
        h_, w_ = m4.shape[:2]
        m4 = cv2.resize(m4, (max(1, w_ // 2), max(1, h_ // 2)), interpolation=cv2.INTER_AREA)
        r2 = cv2.resize(r2, (max(1, w_ // 2), max(1, h_ // 2)), interpolation=cv2.INTER_AREA)
        if ex is not None:
            ex = cv2.resize(ex, (max(1, w_ // 2), max(1, h_ // 2)), interpolation=cv2.INTER_AREA)
        kk *= (w_ // 2) / w_
        ccx, ccy = ccx * (w_ // 2) / w_, ccy * (h_ // 2) / h_
    gl = (np.array(pick, np.float64) - np.array([cx, cy])) / k if pick else np.zeros((0, 2))
    return dict(lv=lv, segs=segs, glints=gl, style=style, outl=outl)


def text_obj(lines, k, bevel_em=.06, depth=280.0, pad_em=.14, seed=1):
    """lines＝[(文字列, 大きさ, 下の 線（1000 単位・y 下向き）, 面取り（字の 大きさの 何倍）, 厚み（1000 単位）)]（まん中 そろえ）→ 立体"""
    rows = []
    for txt, s, base, bev, dep in lines:
        its, box, w = KA.run([(c, s) for c in txt], 0.0, base, -40.0)
        its = KA.shift_items(its, -w / 2, 0)
        box = (box[0] - w / 2, box[1], box[2] - w / 2, box[3])
        rows.append((its, box, s, bev, dep))
    box = KA.union_box(*[r[1] for r in rows])
    pad = int(pad_em * 1000 * k)
    Wt = int(np.ceil((box[2] - box[0]) * k + 2 * pad))
    Ht = int(np.ceil((box[3] - box[1]) * k + 2 * pad))
    yy = np.arange(Ht, dtype=np.float32)[:, None] * np.ones((1, Wt), np.float32)
    parts = []
    for its, b, s, bev, dep in rows:
        m = KA.mask(its, box, k, pad)
        m = m[:Ht, :Wt] if m.shape[0] >= Ht and m.shape[1] >= Wt else cv2.copyMakeBorder(m, 0, max(0, Ht - m.shape[0]), 0, max(0, Wt - m.shape[1]), cv2.BORDER_CONSTANT, value=0)[:Ht, :Wt]
        y0 = (b[1] - box[1]) * k + pad
        y1 = (b[3] - box[1]) * k + pad
        svm = (yy - y0) / max(1.0, y1 - y0)
        parts.append((m, bev * 1000 * s * k, dep, svm))
    cx = (0 - box[0]) * k + pad
    cy = ((box[1] + box[3]) / 2 - box[1]) * k + pad
    o = make_obj(parts, k, cx, cy, Wt, Ht, seed=seed)
    o['size'] = (box[2] - box[0], box[3] - box[1])
    o['ymid'] = (box[1] + box[3]) / 2
    return o


# ---------------------------------------------------------------- 立体を 1コマ 描く
def rot(yaw, pitch, roll):
    """回転（度）：yaw＝たての 軸（＋で 右が おく）・pitch＝横の 軸（＋で 上が おく）・roll＝前の 軸"""
    a, b, c = math.radians(yaw), math.radians(pitch), math.radians(roll)
    Ry = np.array([[math.cos(a), 0, math.sin(a)], [0, 1, 0], [-math.sin(a), 0, math.cos(a)]])
    Rx = np.array([[1, 0, 0], [0, math.cos(b), -math.sin(b)], [0, math.sin(b), math.cos(b)]])
    Rz = np.array([[math.cos(c), -math.sin(c), 0], [math.sin(c), math.cos(c), 0], [0, 0, 1]])
    return Ry @ Rx @ Rz


def project(P):
    z = np.maximum(P[..., 2], 1e-3)
    return np.stack([FOCAL * P[..., 0] / z + CXS, FOCAL * P[..., 1] / z + CYS], -1)


def sides(obj, R, Tv, gain=1.0, env_rot=0.0):
    """側面（うしろ → 前の 順：前ほど 明るい 金・うしろは こげ茶）→ (色, おおい)（画面の 画素）"""
    segs = obj['segs']
    Wc, Hc = W * SSA, H * SSA
    p0 = np.stack([segs[:, 0], segs[:, 1], np.zeros(len(segs))], 1)
    p1 = np.stack([segs[:, 2], segs[:, 3], np.zeros(len(segs))], 1)
    nl = np.stack([segs[:, 4], segs[:, 5], np.zeros(len(segs))], 1)
    dep = segs[:, 6]
    Nc = nl @ R.T
    lf = .56 + .66 * np.clip(Nc @ KEY_T, 0, 1)            # 左上からの 光（上 向きの 側面は 明るく・下 向きは かげ）
    polys, cols, zs = [], [], []
    edges = [0.0, .015, .035, .06, .09, .125, .165, .21, .26, .32, .39, .47, .56, .66, .77, .88, 1.0]
    zero = np.zeros(len(segs))
    for j in range(len(edges) - 1):
        f0, f1 = edges[j], edges[j + 1]
        fm = (f0 + f1) / 2
        gk = 1.45 * (1 - fm) ** 2.2 + .16
        a = p0 + np.stack([zero, zero, dep * f0], 1)
        b = p1 + np.stack([zero, zero, dep * f0], 1)
        c = p1 + np.stack([zero, zero, dep * f1], 1)
        d = p0 + np.stack([zero, zero, dep * f1], 1)
        quad = np.stack([a, b, c, d], 1) @ R.T + Tv
        cen = quad.mean(1)
        vis = np.einsum('ij,ij->i', Nc, -cen) > 0
        if not vis.any():
            continue
        V = cen / np.linalg.norm(cen, axis=1, keepdims=True)
        rv = V - 2 * np.einsum('ij,ij->i', V, Nc)[:, None] * Nc
        rv = rv + (cen - Tv) / ENV_R
        rv /= np.linalg.norm(rv, axis=1, keepdims=True)
        col = env_lookup(rv, env_rot) * (.5 * gk * gain) * SIDE_TINT * lf[:, None].astype(np.float32)
        if j == len(edges) - 2:                        # うしろの はしの 金の 線
            col = col * .6 + np.float32([.5, .32, .08]) * gain
        pr = project(quad) * SSA
        polys.append(pr[vis])
        cols.append(col[vis])
        zs.append(cen[vis, 2])
    out = np.zeros((Hc, Wc, 3), np.float32)
    cov = np.zeros((Hc, Wc), np.float32)
    if polys:
        P = np.concatenate(polys, 0)
        C = np.concatenate(cols, 0)
        Z = np.concatenate(zs, 0)
        for i in np.argsort(-Z):
            q = np.round(P[i] * 4).astype(np.int32)
            if q[:, 0].max() < 0 or q[:, 1].max() < 0 or q[:, 0].min() > Wc * 4 or q[:, 1].min() > Hc * 4:
                continue
            cv2.fillConvexPoly(out, q, C[i].tolist(), cv2.LINE_8, shift=2)
            cv2.fillConvexPoly(cov, q, 1.0, cv2.LINE_8, shift=2)
        out = cv2.GaussianBlur(out, (0, 0), 1.3)
        cov = cv2.GaussianBlur(cov, (0, 0), .6)
    out = cv2.resize(out, (W, H), interpolation=cv2.INTER_AREA)
    cov = cv2.resize(cov, (W, H), interpolation=cv2.INTER_AREA)
    return out * cov[..., None], cov


def homography(L, R, Tv):
    k = L['k']
    cx, cy = L['c']
    Hm = np.array([[1 / k, 0, -cx / k], [0, 1 / k, -cy / k], [0, 0, 1]])
    Mcam = np.column_stack([R[:, 0], R[:, 1], Tv])
    Kc = np.array([[FOCAL, 0, CXS], [0, FOCAL, CYS], [0, 0, 1]])
    return Kc @ Mcam @ Hm


def pick_level(obj, Tv):
    """画面の 1画素 あたり 1〜2 の 細かさの 地図を えらぶ"""
    scr = FOCAL / max(Tv[2], 1.0)                     # 1 単位 あたりの 画面の 画素（まん中）
    for j, L in enumerate(obj['lv']):
        if L['k'] <= scr * 1.6 or j == len(obj['lv']) - 1:
            return j
    return 0


def face(obj, R, Tv, env_rot=0.0, gain=1.0, shine=None, tilt=0.0):
    """前の 面（ふち：映りこみの 金・面：夕やけの しま＋つや）→ (premultiplied 色, alpha, 字 → 画面 の 行列)"""
    L = obj['lv'][pick_level(obj, Tv)]
    Hs = homography(L, R, Tv)
    m4 = cv2.warpPerspective(L['m4'], Hs, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    rw = cv2.warpPerspective(L['rim'], Hs, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    ex = None
    if L['extra'] is not None:
        ex = cv2.warpPerspective(L['extra'], Hs, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    a = m4[..., 0]
    idx = np.flatnonzero(a > .002)
    rgb = np.zeros((H * W, 3), np.float32)
    if len(idx):
        ys, xs = np.divmod(idx, W)
        al = a.ravel()[idx]
        nx = m4[..., 1].ravel()[idx] / np.maximum(al, 1e-3)
        ny = m4[..., 2].ravel()[idx] / np.maximum(al, 1e-3)
        sv = m4[..., 3].ravel()[idx] / np.maximum(al, 1e-3)
        rr = np.clip(rw.ravel()[idx] / np.maximum(al, 1e-3), 0, 1)
        nz = -np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
        n = np.stack([nx, ny, nz], 1) @ R.T
        n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
        d = np.stack([(xs - CXS) / FOCAL, (ys - CYS) / FOCAL, np.ones(len(idx))], 1)
        nP = R[:, 2]
        t = (nP @ Tv) / (d @ nP)
        P = d * t[:, None]
        V = d / np.linalg.norm(d, axis=1, keepdims=True)
        rv = V - 2 * np.sum(V * n, 1, keepdims=True) * n
        rv = rv + (P - Tv) / ENV_R
        rv /= np.linalg.norm(rv, axis=1, keepdims=True)
        envc = env_lookup(rv, env_rot).astype(np.float32)
        ndl = np.clip(n @ KEY_T, 0, 1).astype(np.float32)
        hv = KEY_T[None, :] - V
        hv /= np.linalg.norm(hv, axis=1, keepdims=True)
        spec = (np.clip(np.sum(n * hv, 1), 0, 1) ** 48).astype(np.float32)
        gold = envc * GOLD_TINT * 1.05 * (.7 + .52 * ndl)[:, None] + spec[:, None] * np.float32([1.0, .95, .82]) * 1.25
        u = (P - Tv) @ R[:, 0]                               # 字の 横の 位置（1000 単位）
        if obj['style'] == 'stripe':
            w = sv + .016 * np.sin(u / 1000 * 2 * math.pi * 2.3 + 1.1 + tilt) + .008 * np.sin(u / 1000 * 2 * math.pi * 5.9 + .4)
            fc = KA.ramp(w, FACE)
            lum = envc @ np.float32([.3, .55, .15])
            fc = fc * (.58 + .36 * np.clip(lum, 0, 1.6))[:, None]
            fc = fc + (np.clip(lum - 1.0, 0, None) * .4)[:, None] * np.float32([1.0, .9, .7])
            fc = fc * (.9 + .22 * ndl)[:, None]
        else:                                                # 金（鳥居）：みがいた 金の 面
            fc = envc * GOLD_TINT * .82
            if ex is not None:                               # 額：こい 赤（金の 字は ふちの 金）
                pm = np.clip(ex.ravel()[idx] / np.maximum(al, 1e-3), 0, 1)
                lac = np.float32([.36, .04, .02]) * (.7 + .5 * np.clip(envc @ np.float32([.3, .55, .15]), 0, 1.5))[:, None]
                fc = fc * (1 - pm[:, None]) + lac * pm[:, None]
        col = gold * rr[:, None] + fc * (1 - rr[:, None])
        if shine is not None:                                # 光が すべる（ななめの 光の 帯）
            s_pos, s_w = shine
            v_ = (P - Tv) @ R[:, 1]
            band = np.exp(-(((u + v_ * .55) / 1000 - s_pos) / s_w) ** 2)
            col = col + band[:, None] * np.float32([1.0, .86, .55]) * .5
        rgb[idx] = col * gain * al[:, None]
    return rgb.reshape(H, W, 3), a, Hs


def draw(img, obj, R, Tv, env_rot=0.0, gain=1.0, side_gain=1.0, shine=None, tilt=0.0, mv=None):
    """側面 → 前の 面 を img に 重ねる（mv：動きの ぶれ（画面の 画素））→ 字 → 画面 の 行列"""
    sc, scov = sides(obj, R, Tv, side_gain * gain, env_rot)
    fr, fa, Hs = face(obj, R, Tv, env_rot, gain, shine, tilt)
    rgb = fr + sc * (1 - fa[..., None])
    al = np.clip(fa + scov * (1 - fa), 0, 1)
    if mv is not None and math.hypot(*mv) > 1.5:
        lay = KF.motion_blur(np.dstack([rgb, al]).astype(np.float32), mv[0], mv[1])
        p_ = (lay.shape[0] - H) // 2
        lay = lay[p_:p_ + H, p_:p_ + W]
        rgb, al = lay[..., :3], np.clip(lay[..., 3], 0, 1)
    img *= (1 - al[..., None])
    img += rgb
    return Hs, al


# ---------------------------------------------------------------- 字（1回だけ 作る）
CU_CHARS = '神様的中'
CU_K = 1.6                            # 寄りの 字の 地図の 細かさ（1 単位 あたりの 画素）
LOGO_K = .8
LOGO_LINES = (('神様', 1.0, 0.0, .064, 460.0), ('的中', 1.0, 860.0, .064, 460.0),
              ('おめでとう', .36, 1272.0, .08, 290.0), ('御座います', .36, 1620.0, .08, 290.0))


def cu_obj(j):
    return KF.cache(f'cu{j}', lambda: text_obj([(CU_CHARS[j], 1.0, 0.0, .052, 470.0)], CU_K, seed=11 + j))


def logo_obj():
    return KF.cache('logo5', lambda: text_obj(list(LOGO_LINES), LOGO_K, seed=21))


# ---------------------------------------------------------------- 朱ぬりの 鳥居（うしろ：kami_torii3.py）
TORII_BACK = 540.0                     # 字の うしろ（1000 単位）
TORII_FIT = (24.0, 1146.0, 150.0)      # さいごの 形で：笠木の 左の 端・右の 端（x）・笠木の 上（y）（画面の 画素）
TORII_DOF = 1.1                        # 鳥居の ぼけ（字に ピント）


def torii_geo():
    return KF.cache('torii4', T3.build)


def plq_tex():
    return KF.cache('plqtex', T3.plaque_tex)


def torii_fit():
    """さいごの 形（回りおわり）で 鳥居が 画面に おさまる 大きさと 場所（字の 座標で）→ (off (3,), D の 大きさ)"""
    def f():
        from scipy.optimize import fsolve
        yaw, pitch, roll, x, y, z = logo_pose(TT['TURN'][1])
        R = rot(yaw, pitch, roll)
        Tv = np.array([x, y, z])
        ky = T3.SHI_Y0 - T3.SHI_H - T3.KAS_H / 2
        e = .004
        tipL = np.array([-(T3.LK + e), ky - float(T3.curve(T3.LK)), -T3.KAS_D / 2 - e])
        tipR = tipL * np.array([-1, 1, 1])
        topC = np.array([0.0, ky - T3.KAS_H / 2, -T3.KAS_D / 2])

        def res(q):
            ox, oy, dsc = q
            Tt = Tv + R @ np.array([ox, oy, TORII_BACK])
            pl, pr, pt = (project(R @ (p * dsc) + Tt) for p in (tipL, tipR, topC))
            return [pl[0] - TORII_FIT[0], pr[0] - TORII_FIT[1], pt[1] - TORII_FIT[2]]
        z0 = z + TORII_BACK
        q = fsolve(res, [0.0, -(CYS - 150) * z0 / FOCAL, .5 * z0])
        return np.array([q[0], q[1], TORII_BACK]), float(q[2])
    return KF.cache('toriifit', f)


def torii_place(R, Tv):
    """鳥居（字と いっしょに 動く）→ (回転, 場所, D の 大きさ)"""
    off, dsc = torii_fit()
    return R, Tv + R @ off, dsc


def text_shadow(o, R, Tv):
    """字の かげ（鳥居に おちる：左上 手前からの 光 → 右下へ ずれて ぼける）→ 0〜1"""
    L = o['lv'][min(len(o['lv']) - 1, pick_level(o, Tv) + 1)]
    Hs = homography(L, R, Tv)
    sc = .25
    Mv = np.array([[sc, 0, 26 * sc], [0, sc, 64 * sc], [0, 0, 1]]) @ Hs
    a = cv2.warpPerspective(L['m4'][..., 0], Mv, (int(W * sc), int(H * sc)), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    a = cv2.GaussianBlur(a, (0, 0), 16 * sc)
    return cv2.resize(a, (W, H), interpolation=cv2.INTER_LINEAR)


def draw_torii(img, R, Tv, t, mv, o):
    Rt, Tt, dsc = torii_place(R, Tv)
    rgb, a = T3.render(torii_geo(), plq_tex(), Rt, Tt, dsc, W, H, FOCAL, CXS, CYS, lambda rv, rt, lv: env_lookup(rv, rt, lv),
                       env_rot=8 - 6 * (t - TT['LOGO']), ss=2)
    rgb *= (1 - .58 * text_shadow(o, R, Tv))[..., None]
    rgba = np.dstack([rgb, a]).astype(np.float32)
    rgba = cv2.GaussianBlur(rgba, (0, 0), TORII_DOF)
    ox = oy = 0
    if math.hypot(*mv) > 1.5:
        b = KF.motion_blur(rgba, mv[0], mv[1])
        p_ = (b.shape[0] - H) // 2
        rgba, ox, oy = b, -p_, -p_
    KF.place(img, rgba, ox, oy)


# ---------------------------------------------------------------- 背景（暗い 金の 部屋：動かない）
def background():
    def f():
        X = np.arange(W, dtype=np.float32)[None, :] / S
        Y = np.arange(H, dtype=np.float32)[:, None] / S
        r = np.sqrt(((X - 195) / 1.0) ** 2 + ((Y - 430) / 1.25) ** 2)
        base = np.float32([.035, .012, .004])
        img = np.ones((H, W, 3), np.float32) * base
        img += np.exp(-(r / 330) ** 2)[..., None] * np.float32([.3, .11, .025])
        img += np.exp(-(r / 150) ** 2)[..., None] * np.float32([.26, .12, .03])
        nz = KA.fbm(H // 4, W // 4, 10, 991, 4, .55)
        nz = cv2.resize(nz, (W, H), interpolation=cv2.INTER_CUBIC)
        img *= (.75 + .5 * nz)[..., None]
        # ぼけた 金の 光の 玉（遠くの 光：動かない）
        rng = np.random.default_rng(57)
        bok = np.zeros((H, W), np.float32)
        for _ in range(26):
            x, y = rng.uniform(0, W), rng.uniform(0, H)
            rr = rng.uniform(14, 46) * S
            cv2.circle(bok, (int(x * 4), int(y * 4)), int(rr * 4), float(rng.uniform(.25, .7)), -1, cv2.LINE_AA, shift=2)
        bok = cv2.GaussianBlur(bok, (0, 0), 3 * S)
        img += bok[..., None] * np.float32([.24, .12, .035])
        return img.astype(np.float32)
    return KF.cache('bg3', f)


# ---------------------------------------------------------------- 小判（第4.50版：金の 粒の かわり。kami_koban.py）
NUG_TYPES = 10
NUG_N = dict(burst=22, big=56, cover=3, drift=4, linger=4)      # 小判の 数（点めつ：1つの 所を 何回も 横切らない ように 少なめ）
KOBAN_V = 3                            # 打ちあとの ちがう 小判の しゅるい
KOBAN_SZ = 1.15                        # 粒の 大きさ → 小判の たての 半分
KOBAN_T = .055                         # 小判の 厚み（たての 半分に 対して）
KOBAN_TINT = np.float32([1.0, .82, .46])


def koban_tex(i):
    return KF.cache(f'koban{i}', lambda: KB.koban(i))


def axis_rot(ax, ang):
    ax = np.asarray(ax, np.float64)
    ax = ax / np.linalg.norm(ax)
    x, y, z = ax
    c, s = math.cos(ang), math.sin(ang)
    C = 1 - c
    return np.array([[c + x * x * C, x * y * C - z * s, x * z * C + y * s],
                     [y * x * C + z * s, c + y * y * C, y * z * C - x * s],
                     [z * x * C - y * s, z * y * C + x * s, c + z * z * C]])


def _gold_at(n, V):
    """金の 色（映りこみ・左上の 光）：n, V（…×3：カメラ）"""
    vn = np.sum(V * n, -1, keepdims=True)
    rv = V - 2 * vn * n
    rv[..., 1] = rv[..., 1] * .55 - .2                               # 下（暗い 床）を 映しすぎない（ひっくり返る たびに 暗く ならない）
    rv /= np.linalg.norm(rv, axis=-1, keepdims=True)
    envc = env_lookup(rv).astype(np.float32)
    ndl = np.clip(n @ KEY_T, 0, 1).astype(np.float32)
    hv = KEY_T - V
    hv /= np.linalg.norm(hv, axis=-1, keepdims=True)
    spec = (np.clip(np.sum(n * hv, -1), 0, 1) ** 50).astype(np.float32)
    return envc * KOBAN_TINT * (.55 + .5 * ndl)[..., None] + spec[..., None] * np.float32([1.0, .95, .8]) * 1.1 + np.float32([.08, .04, .012])


def draw_koban(img, kb, Rn, pos, size, boost=1.0, blur=0.0, mv=(0.0, 0.0), fade=1.0):
    """小判 1まいを img に（見える 面＋ふちの 側面・近い ほど ぼける・速い ほど ぶれる）"""
    B = size * KOBAN_SZ
    A = B * KB.TW / KB.TH
    t = B * KOBAN_T
    if pos[2] - B < 40:
        return
    ol, on = KB.outline(48)
    olA = ol * np.array([A * .985, B * .985])
    Pf = np.column_stack([olA, np.full(len(olA), -t / 2)]) @ Rn.T + pos
    Pb = np.column_stack([olA, np.full(len(olA), t / 2)]) @ Rn.T + pos
    pf, pb = project(Pf), project(Pb)
    allp = np.vstack([pf, pb])
    pad = blur * 2.6 + 4
    X0, Y0 = int(math.floor(allp[:, 0].min() - pad)), int(math.floor(allp[:, 1].min() - pad))
    X1, Y1 = int(math.ceil(allp[:, 0].max() + pad)), int(math.ceil(allp[:, 1].max() + pad))
    mvl = math.hypot(*mv)
    if X1 + mvl < 0 or Y1 + mvl < 0 or X0 - mvl > W or Y0 - mvl > H:
        return
    w, h = X1 - X0, Y1 - Y0
    if w * h > 9e6:
        return
    ss = 2.0 if max(w, h) < 220 else (1.0 if blur < 4 else (.5 if blur < 14 else .25))
    cw, ch = max(2, int(w * ss) + 1), max(2, int(h * ss) + 1)
    canvas = np.zeros((ch, cw, 3), np.float32)
    cov = np.zeros((ch, cw), np.float32)
    # ふち（側面：遠い 順）
    nl = on / np.array([A, B])
    nl /= np.linalg.norm(nl, axis=1, keepdims=True)
    j1 = (np.arange(len(ol)) + 1) % len(ol)
    nm = nl + nl[j1]
    nm /= np.linalg.norm(nm, axis=1, keepdims=True)
    Nc = np.column_stack([nm, np.zeros(len(nm))]) @ Rn.T
    cen = (Pf + Pf[j1] + Pb + Pb[j1]) / 4
    vis = np.einsum('ij,ij->i', Nc, cen) < 0
    if vis.any():
        V = cen / np.linalg.norm(cen, axis=1, keepdims=True)
        col = _gold_at(Nc, V) * .78 * boost
        for i in np.flatnonzero(vis)[np.argsort(-cen[vis, 2])]:
            q = np.array([pf[i], pf[j1[i]], pb[j1[i]], pb[i]])
            q = np.round((q - [X0, Y0]) * ss * 4).astype(np.int32)
            cv2.fillConvexPoly(canvas, q, col[i].tolist(), cv2.LINE_8, shift=2)
            cv2.fillConvexPoly(cov, q, 1.0, cv2.LINE_8, shift=2)
    # 見える 面（表 か 裏）
    nf = Rn @ np.array([0.0, 0.0, -1.0])
    front = float(nf @ pos) < 0
    sgn = 1.0 if front else -1.0
    zf_ = -t / 2 if front else t / 2
    hpx = 2 * B * FOCAL / pos[2] * ss
    j = int(np.clip(math.floor(math.log2(max(1.0, KB.TH / max(hpx * 1.25, 1.0)))), 0, 4))
    L = kb['front' if front else 'back'][j]
    sc = KB.TH / L.shape[0]
    c0 = Rn[:, 0] * (sgn * A / (KB.TW / 2)) * sc
    c1 = Rn[:, 1] * (B / (KB.TH / 2)) * sc
    c2 = pos + Rn @ np.array([0.0, 0.0, zf_]) - Rn[:, 0] * sgn * A - Rn[:, 1] * B
    Kc = np.array([[FOCAL, 0, CXS], [0, FOCAL, CYS], [0, 0, 1]])
    Hc = np.array([[ss, 0, -X0 * ss], [0, ss, -Y0 * ss], [0, 0, 1]]) @ Kc @ np.column_stack([c0, c1, c2])
    m4 = cv2.warpPerspective(L, Hc, (cw, ch), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    a = m4[..., 0]
    idx = np.flatnonzero(a > .003)
    if len(idx):
        al = a.ravel()[idx]
        nx = m4[..., 1].ravel()[idx] / al
        ny = m4[..., 2].ravel()[idx] / al
        cv_ = np.clip(m4[..., 3].ravel()[idx] / al, 0, 1)
        nloc = np.stack([nx, ny, -np.ones_like(nx)], 1) if front else np.stack([-nx, ny, np.ones_like(nx)], 1)
        n = nloc @ Rn.T
        n /= np.linalg.norm(n, axis=1, keepdims=True)
        ys, xs = np.divmod(idx, cw)
        V = np.stack([((xs + .5) / ss + X0 - CXS) / FOCAL, ((ys + .5) / ss + Y0 - CYS) / FOCAL, np.ones(len(idx))], 1)
        V /= np.linalg.norm(V, axis=1, keepdims=True)
        vn = np.sum(V * n, 1, keepdims=True)
        n = np.where(vn > 0, n - 2 * vn * n, n)
        col = _gold_at(n, V) * (1 - .55 * cv_)[:, None] * boost
        fr = np.zeros((ch * cw, 3), np.float32)
        fr[idx] = col * al[:, None]
        canvas = fr.reshape(ch, cw, 3) + canvas * (1 - a[..., None])
        cov = a + cov * (1 - a)
    rgba = np.dstack([canvas, cov]).astype(np.float32)
    if ss != 1.0:
        rgba = cv2.resize(rgba, (max(1, w), max(1, h)), interpolation=cv2.INTER_AREA if ss > 1 else cv2.INTER_LINEAR)
    if ss > 1:
        rgba = cv2.GaussianBlur(rgba, (0, 0), .55)
    if blur > .6:
        rgba = cv2.GaussianBlur(rgba, (0, 0), blur)
    ox, oy = X0, Y0
    if mvl > 1.5:
        b = KF.motion_blur(rgba, mv[0], mv[1])
        p_ = (b.shape[0] - rgba.shape[0]) // 2
        rgba, ox, oy = b, X0 - p_, Y0 - p_
    if fade < 1.0:
        rgba = rgba * fade
    KF.place(img, rgba, ox, oy)


def nug_events():
    """金の 粒の 一つ一つ：(はじめの 時刻, 種, 形, はじめの 場所, 速さ, ブレーキ, 回る 軸, 回る 速さ, 向き, 大きさ, 命)"""
    def f():
        ev = []
        for bi, (t0, kind, t_end) in enumerate(TT['BU']):
            rng = random.Random(500 + bi * 37)
            if kind == 0:                                           # 大きな 粒が 手前を 横切る（字の かわり目を かくす）
                dirn = -1 if bi % 4 == 1 else 1
                for k in range(NUG_N['cover']):
                    z = rng.uniform(300, 640)
                    half = (W / 2) * z / FOCAL * 1.45
                    y = rng.uniform(-.85, .85) * (H / 2) * z / FOCAL
                    tc = t0 + .05 + k * .04 + rng.uniform(-.02, .02)
                    dur = rng.uniform(.26, .36)
                    vx = 2 * half / dur * dirn
                    ev.append(dict(t0=tc - dur / 2, kind=0, typ=rng.randrange(NUG_TYPES), p0=np.array([-dirn * half, y, z]),
                                   v0=np.array([vx, rng.uniform(-150, 150), rng.uniform(-60, 60)]), tau=99.0, g=0.0,
                                   ax=np.array([rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, 1)]), w=rng.uniform(3, 7) * rng.choice((-1, 1)),
                                   ph=rng.uniform(0, 6.3), size=rng.uniform(120, 175), life=dur + .02, end=None, soft=True))
                # 次の 寄りの 間：手前を ゆっくり ただよう 粒（光らない・ぼけて いる）
                j = 1 if bi == 1 else 3
                s0, s1 = TT['CU'][j]
                r2 = random.Random(800 + bi)
                for k in range(NUG_N['drift']):
                    z = r2.uniform(320, 850)
                    tt = s0 + r2.uniform(.04, .14)
                    ev.append(dict(t0=tt, kind=3, typ=r2.randrange(NUG_TYPES),
                                   p0=np.array([r2.uniform(-.8, .8) * (W / 2) * z / FOCAL, r2.uniform(-.85, .85) * (H / 2) * z / FOCAL, z]),
                                   v0=np.array([r2.uniform(-140, 140), r2.uniform(-120, 40), r2.uniform(-200, -60)]), tau=99.0, g=60.0,
                                   ax=np.array([r2.gauss(0, 1), r2.gauss(0, 1), r2.gauss(0, 1)]), w=r2.uniform(1.0, 2.5) * r2.choice((-1, 1)),
                                   ph=r2.uniform(0, 6.3), size=r2.uniform(18, 55), life=s1 - tt + .02, end=s1, fin=.15))
                continue
            big = kind == 2
            n = NUG_N['big'] if big else NUG_N['burst']
            cz, cx, cy = (2050.0, 0.0, 380.0) if big else (960.0, 0.0, 60.0)
            for k in range(n):
                th = rng.uniform(0, 2 * math.pi)
                lat = rng.uniform(600, 2000) * (1.35 if big else 1.0)
                vz = -rng.uniform(700, 2000) * (1.25 if big else 1.0)            # 小判が 見える ように カメラへ 来すぎない
                vx, vy = lat * math.cos(th), lat * math.sin(th) * .85
                if big:
                    vy -= rng.uniform(300, 1100)                    # 下から 上へ ぶわっと
                sz = 9 + 70 * rng.random() ** 2.6
                if rng.random() < (.12 if big else .06):
                    sz = rng.uniform(70, 125)
                ev.append(dict(t0=t0 + rng.uniform(0, .07 if big else .05), kind=kind, typ=rng.randrange(NUG_TYPES),
                               p0=np.array([cx + rng.gauss(0, 380 if big else 230), cy + rng.gauss(0, 300 if big else 190), cz - rng.uniform(0, 420)]),
                               v0=np.array([vx, vy, vz]), tau=rng.uniform(.8, 1.2) if big else rng.uniform(.7, 1.0), g=rng.uniform(200, 500),
                               ax=np.array([rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, 1)]), w=rng.uniform(3, 9) * rng.choice((-1, 1)),
                               ph=rng.uniform(0, 6.3), size=sz, life=rng.uniform(.55, .9) if big else rng.uniform(.45, .75), end=t_end))
            if big:                                                 # ゆっくり ただよう 粒（おちつく まで 少し のこる）
                for k in range(NUG_N['linger']):
                    th = rng.uniform(0, 2 * math.pi)
                    lat = rng.uniform(150, 480)
                    ev.append(dict(t0=t0 + rng.uniform(.02, .12), kind=kind, typ=rng.randrange(NUG_TYPES),
                                   p0=np.array([rng.choice((-1, 1)) * rng.uniform(320, 700), 380 + rng.gauss(0, 420), rng.uniform(1100, 1700)]),
                                   v0=np.array([lat * math.cos(th), lat * math.sin(th) - 200, -rng.uniform(150, 500)]), tau=1.2, g=rng.uniform(150, 300),
                                   ax=np.array([rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, 1)]), w=rng.uniform(1.5, 4) * rng.choice((-1, 1)),
                                   ph=rng.uniform(0, 6.3), size=rng.uniform(20, 60), life=rng.uniform(1.0, 1.4), end=None))
        return ev
    return KF.cache('nugev', f)


def nug_state(e, t):
    s = t - e['t0']
    tau = e['tau']
    p = e['p0'] + e['v0'] * tau * (1 - math.exp(-s / tau)) + np.array([0.0, e['g'] * s * s * .5, 0.0])
    return p


def focus_z(t):
    """ピントの きょり（今 写って いる 字）"""
    return 970.0 if t < TT['LOGO'] else logo_pose(t)[5]


def nuggets(img, t):
    """小判（遠い 順に）"""
    zf = focus_z(t)
    items = []
    for e in nug_events():
        s = t - e['t0']
        if not (0 <= s <= e['life']) or (e['end'] is not None and t >= e['end']):
            continue
        p = nug_state(e, t)
        if p[2] < 60:
            continue
        items.append((p[2], e, p, s))
    items.sort(key=lambda a: -a[0])
    for z, e, p, s in items:
        pp = nug_state(e, t - .33 / FPS)                                 # 動きの ぶれ（1/3 コマ：小判の すじが 見える）
        c1 = project(p)
        c0 = project(pp)
        blur = min(22.0, 3.2 * abs(zf / z - 1.0)) if z < zf else min(4.0, 3.0 * (1 - zf / z))
        if e.get('soft'):
            blur = max(blur, 30.0)                                  # 手前を 横切る 大きな 粒は 大きく ぼかす（中の 明暗で ちらつかない）
        Rn = axis_rot(e['ax'], e['ph'] + e['w'] * s)
        boost = (1.0, 1.0 + .5 * math.exp(-s / .08), 1.0 + .5 * math.exp(-s / .08), 1.0)[e['kind']]   # はじけた 時の 光は 少しだけ（小判の 形が 見える）
        fin = e.get('fin', .03)
        fade = min(1.0, (e['life'] - s) / .2) * min(1.0, s / fin + .2)
        draw_koban(img, koban_tex(e['typ'] % KOBAN_V), Rn, p, e['size'], boost, blur, (c1[0] - c0[0], c1[1] - c0[1]), fade)


# ---------------------------------------------------------------- はじける 光・金の ちり・キラッ
def burst_light(img, t):
    """金の 粒が はじける 時の 光（すぐ 消える：1回の はじけで 1回）"""
    X = np.arange(W, dtype=np.float32)[None, :]
    Y = np.arange(H, dtype=np.float32)[:, None]
    for t0, kind, _ in TT['BU']:
        s = t - t0
        if kind == 0 or not (-.01 <= s <= .5):
            continue
        A = 1.25 if kind == 1 else 1.7
        g = A * math.exp(-max(0.0, s) / .12) * smoothstep(-.01, .03, s)
        if g < .01:
            continue
        cx, cy = CXS, CYS + (60 if kind == 1 else 300) * S * .3
        d2 = (X - cx) ** 2 + ((Y - cy) * .8) ** 2
        r = (420 + 900 * s) * (1.3 if kind == 2 else 1.0)
        img += (np.exp(-d2 / (r * r)) * g)[..., None] * np.float32([1.0, .82, .45])
        img += (np.exp(-d2 / ((r * .3) ** 2)) * g * .8)[..., None] * np.float32([1.0, .96, .86])


def debris(img, t):
    """はじけた 時の 細かい 金の ちり（光の つぶ）"""
    m = np.zeros((H, W), np.float32)
    for bi, (t0, kind, t_end) in enumerate(TT['BU']):
        s = t - t0
        if kind == 0 or not (0 <= s <= 1.0) or (t_end is not None and t >= t_end):
            continue
        rng = random.Random(900 + bi)
        cx, cy = CXS, CYS + (60 if kind == 1 else 300) * S * .3
        for _ in range(120 if kind == 2 else 70):
            a = rng.uniform(0, 2 * math.pi)
            v = rng.uniform(300, 2200) * (1.3 if kind == 2 else 1.0)
            life = rng.uniform(.35, 1.0)
            if s > life:
                continue
            tau = .22
            dist = v * tau * (1 - math.exp(-s / tau))
            x = cx + rng.gauss(0, 60) + dist * math.cos(a)
            y = cy + rng.gauss(0, 60) + dist * math.sin(a) + 260 * s * s
            e = (1 - s / life) ** .7 * (.55 + .45 * math.sin(rng.uniform(0, 6.3) + 30 * s))
            tail = v * math.exp(-s / tau) * .012
            cv2.line(m, (int((x - tail * math.cos(a)) * 4), int((y - tail * math.sin(a)) * 4)), (int(x * 4), int(y * 4)),
                     float(max(0.0, e)), max(1, int(rng.uniform(2, 5))), cv2.LINE_AA, shift=2)
    if m.max() > 0:
        KF.glow_add(img, m, ((0, (1, .97, .85), 1.1), (1.2, (1, .82, .4), .8), (5, (1, .6, .15), .35)))


def sparkle_events():
    def f():
        rng = random.Random(4242)
        ev = []
        t = 0.0
        while t < N / FPS:
            ev.append((t, rng.uniform(.04, .96), rng.uniform(.06, .94), rng.uniform(.6, 1.3), rng.uniform(.25, .42)))
            t += rng.uniform(.02, .07)
        return ev
    return KF.cache('spk', f)


def sparkles(img, t, amt=1.0):
    """白い 星の きらめき（ふわっと 出て 消える）"""
    m = np.zeros((H, W), np.float32)
    for t0, u, v, sc, dur in sparkle_events():
        if not (t0 <= t <= t0 + dur):
            continue
        e = math.sin(math.pi * (t - t0) / dur) * amt
        x, y = u * W, v * H
        L = 30 * S * sc * (.55 + .45 * e)
        for ang, l, g in ((0.0, L, 1.0), (math.pi / 2, L, 1.0), (math.pi / 4, L * .4, .55), (-math.pi / 4, L * .4, .55)):
            cv2.line(m, (int((x - l * math.cos(ang)) * 4), int((y - l * math.sin(ang)) * 4)),
                     (int((x + l * math.cos(ang)) * 4), int((y + l * math.sin(ang)) * 4)), float(e * g), 2, cv2.LINE_AA, shift=2)
        cv2.circle(m, (int(x * 4), int(y * 4)), int(3 * S * 4 * e) + 1, float(e), -1, cv2.LINE_AA, shift=2)
    if m.max() > 0:
        KF.glow_add(img, m, ((0, (1, 1, 1), 1.0), (1.4, (1, .93, .75), .8), (5, (1, .75, .35), .35)))


def glints(img, obj, Hs, t, seed):
    """キラッ（ふちの 上の 小さな 光の 星：1つずつ ふわっと 出て 消える）"""
    g = obj['glints']
    if len(g) == 0:
        return
    m = np.zeros((H, W), np.float32)
    rng = random.Random(seed)
    rx = random.Random(seed + 9001)                                  # のばした 所（N0 から あと）の キラッ：べつの 乱数（前の コマは かわらない）
    px = (XN / FPS) / (N0 / FPS + .2)
    for (gx, gy) in g:
        t0 = rng.uniform(-.2, N0 / FPS)
        dur = rng.uniform(.26, .42)
        t1x = rx.uniform(N0 / FPS, N / FPS) if rx.random() < px else -9.0
        if not (t0 <= t <= t0 + dur):
            if t1x <= t <= t1x + dur:
                t0 = t1x
            else:
                continue
        p = Hs @ np.array([gx, gy, 1.0])
        x, y = p[0] / p[2], p[1] / p[2]
        if not (0 <= x < W and 0 <= y < H):
            continue
        e = math.sin(math.pi * (t - t0) / dur)
        Lg = rng.uniform(26, 44) * S * (.6 + .4 * e)
        for ang in (0.0, math.pi / 2, math.pi / 4, -math.pi / 4):
            l = Lg if ang in (0.0, math.pi / 2) else Lg * .45
            cv2.line(m, (int((x - l * math.cos(ang)) * 4), int((y - l * math.sin(ang)) * 4)),
                     (int((x + l * math.cos(ang)) * 4), int((y + l * math.sin(ang)) * 4)), float(e * (1.0 if l == Lg else .6)), 2, cv2.LINE_AA, shift=2)
        cv2.circle(m, (int(x * 4), int(y * 4)), int(5 * S * 4 * e) + 1, float(e), -1, cv2.LINE_AA, shift=2)
    if m.max() > 0:
        KF.glow_add(img, m, ((0, (1, 1, 1), 1.2), (1.5, (1, .92, .7), 1.0), (6, (1, .75, .3), .5)))


def unit_h(R, Tv):
    """字の 単位 (u, v) → 画面 の 行列"""
    Kc = np.array([[FOCAL, 0, CXS], [0, FOCAL, CYS], [0, 0, 1]])
    return Kc @ np.column_stack([R[:, 0], R[:, 1], Tv])


# ---------------------------------------------------------------- 雷（字の まわりを はしる：不定期）
# まさちゃん「雷が、不定期に文字の周りを走ってる感じにして！」「神様的中、おめでとう御座います、の文字には雷がビリビリビリビリ不定期に走ってる演出にして！」
# → ふちを はしる 雷（先が ふちに そって 走る・形は 場所で 決まり、いちばん 細かい ギザギザだけ コマごとに かわる＝ビリビリ）・
#   字から 字へ とぶ 雷（さいごの 字）・寄りの 字から 外へ はしる 雷・ふちの 小さな ビリビリ（毎コマ ちがう 所）。
#   点めつ：明るさは 1コマで つき 2コマで 消える（ちかちか させない）・同じ 区画には 12コマ あけて 出す・太い 雷は 少しだけ
ELEC_GLOW = ((0, (1, 1, 1), 1.5), (1.0, (1, .98, .9), 1.35), (3.0, (1, .82, .5), .8), (8.0, (1, .55, .18), .34))
ELEC_RIM = .4                         # 雷の まわりを 少し 暗く（金の 上でも 白い 線が 見える）
ELEC_LOGO0 = 2.42                     # さいごの 字の 雷の はじまり（大爆発が おちついて から）
ELEC_ZOFF = -14.0                     # 雷は 字の 前の 面より 少し 手前


def obj_key(t):
    return 'logo' if t >= TT['LOGO'] else min(3, sum(1 for a, b in TT['CU'] if t >= b))


def obj_of(key):
    return logo_obj() if key == 'logo' else cu_obj(key)


def obj_pose(key, t):
    yaw, pitch, roll, x, y, z = logo_pose(t) if key == 'logo' else cu_pose(key, t)
    return rot(yaw, pitch, roll), np.array([x, y, z])


def ol_at(c, s):
    """ふちの 長さ s（1000 単位・1周で もどる）の 所の 点と 外向き"""
    s = np.asarray(s, np.float64) % c['tot']
    Lp = np.r_[c['L'], c['tot']]
    P = np.vstack([c['P'], c['P'][:1]])
    Nn = np.vstack([c['N'], c['N'][:1]])
    p = np.stack([np.interp(s, Lp, P[:, 0]), np.interp(s, Lp, P[:, 1])], -1)
    n = np.stack([np.interp(s, Lp, Nn[:, 0]), np.interp(s, Lp, Nn[:, 1])], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True) + 1e-9
    return p, n


def ol_screen(p, n, R, Tv, push=10.0):
    """字の 座標の 点と 外向き → 画面の 点と 画面での 外向き"""
    z = np.full(p.shape[:-1] + (1,), ELEC_ZOFF)
    a = project(np.concatenate([p, z], -1) @ R.T + Tv)
    b = project(np.concatenate([p + n * push, z], -1) @ R.T + Tv)
    d = b - a
    d /= np.linalg.norm(d, axis=-1, keepdims=True) + 1e-9
    return a, d


def _zz(seed, k):
    return random.Random(seed * 1000003 + int(k)).random() * 2 - 1


def elec_events():
    """雷の 一覧（はじめに まとめて 作る：何回 作っても 同じ）"""
    def f():
        rng = random.Random(4747)
        ev, used = [], {}

        def blk(p):
            return (int(p[0] // 170), int(p[1] // 170))

        def free(p, f0, gap=12):
            return f0 - used.get(blk(p), -99) > gap

        def mark(p, f0, life):
            used[blk(p)] = max(used.get(blk(p), -99), f0 + life)

        def pick(key, t, margin=40):
            o = obj_of(key)
            R, Tv = obj_pose(key, t)
            f0 = int(round(t * FPS))
            cand = []
            for ci, c in enumerate(o['outl']):
                sc, _ = ol_screen(c['P'], c['N'], R, Tv)
                ok = np.flatnonzero((sc[:, 0] > margin) & (sc[:, 0] < W - margin) & (sc[:, 1] > margin) & (sc[:, 1] < H - margin))
                cand += [(ci, int(i), sc[i]) for i in ok[::2]]
            if not cand:
                return None
            for _ in range(80):
                ci, i, p = cand[rng.randrange(len(cand))]
                if free(p, f0):
                    return o, R, Tv, ci, i, p
            ci, i, p = cand[rng.randrange(len(cand))]
            return o, R, Tv, ci, i, p

        def runner(key, t):
            r = pick(key, t)
            if r is None:
                return
            o, R, Tv, ci, i, p = r
            c = o['outl'][ci]
            sc = FOCAL / Tv[2]                                   # 1 単位 あたりの 画面の 画素
            wide = rng.random() < .3
            life = rng.randint(6, 10)
            e = dict(kind='run', key=key, f0=int(round(t * FPS)), life=life, ci=ci, s0=float(c['L'][i]), dirn=rng.choice((-1, 1)),
                     v=rng.uniform(1100, 2200) / sc, Lseg=rng.uniform(260, 520) / sc, off=rng.uniform(16, 40) if wide else rng.uniform(0, 6),
                     amp=rng.uniform(8, 16) if wide else rng.uniform(5, 10), step=20.0 / sc, seed=rng.randrange(1 << 30),
                     wm=float(np.clip(sc / .55, 1.0, 1.5)))                # 寄りの 大きな 字では 雷も 太く
            ev.append(e)
            mark(p, e['f0'], life)
            pe, ne = ol_at(c, e['s0'] + e['dirn'] * e['v'] * life / FPS)
            mark(ol_screen(pe, ne, R, Tv)[0], e['f0'], life)

        # 寄り（神・様・的・中）
        for j, (t0, t1) in enumerate(TT['CU']):
            t = t0 + (.14 if j == 0 else .07)
            while t < t1 - .1:
                runner(j, t)
                if rng.random() < .3:
                    runner(j, t + rng.choice((0.0, 1 / FPS)))
                t += rng.choice((.04, .06, .08, .11, .15))
            for tt in (t0 + rng.uniform(.12, .2) + (.1 if j == 0 else 0), t0 + rng.uniform(.3, .4)):   # 字から 外へ はしる 雷
                r = pick(j, tt, 120)
                if r is not None:
                    o, R, Tv, ci, i, p = r
                    ev.append(dict(kind='out', key=j, f0=int(round(tt * FPS)), life=5, ci=ci, i=i, da=rng.uniform(-.5, .5),
                                   Lpx=rng.uniform(260, 520), style=rng.choice(('zig', 'zig', 'step')), seed=rng.randrange(1 << 30)))
                    mark(p, int(round(tt * FPS)), 5)
        # さいごの 字：N0 まで 前と 同じ 乱数（前の コマは かわらない）→ のばした 所（第4.53版）は べつの 乱数
        def logo_runs(t, t_end):
            while t < t_end:
                runner('logo', t)
                if rng.random() < .5:
                    runner('logo', t + rng.choice((0.0, 1 / FPS)))
                t += rng.choice((.02, .03, .05, .07, .09, .12, .16))
            return t

        def logo_jumps(t, t_end):
            while t < t_end:                                  # 字から 字へ とぶ 雷
                r = pick('logo', t)
                if r is not None:
                    o, R, Tv, ci, i, p = r
                    best = []
                    for cj, c in enumerate(o['outl']):
                        if cj == ci:
                            continue
                        sc_, _ = ol_screen(c['P'], c['N'], R, Tv)
                        d = np.hypot(sc_[:, 0] - p[0], sc_[:, 1] - p[1])
                        ok = np.flatnonzero((d > 110) & (d < 360))
                        best += [(cj, int(q)) for q in ok[::3]]
                    if best:
                        cj, q = best[rng.randrange(len(best))]
                        ev.append(dict(kind='jump', key='logo', f0=int(round(t * FPS)), life=4, ci=ci, i=i, cj=cj, q=q,
                                       style=rng.choice(('zig', 'zig', 'step', 'wander')), seed=rng.randrange(1 << 30)))
                        mark(p, int(round(t * FPS)), 4)
                t += rng.uniform(.12, .3)
            return t

        t_run = logo_runs(ELEC_LOGO0, N0 / FPS - .08)
        t_jmp = logo_jumps(ELEC_LOGO0 + .1, N0 / FPS - .15)
        if XN:
            rng = random.Random(4748)
            logo_runs(max(t_run, N0 / FPS), N / FPS - .08)
            logo_jumps(max(t_jmp, N0 / FPS), N / FPS - .15)
        return ev
    return KF.cache('elecev', f)


def _poly(mask, pts, val, th):
    if len(pts) < 2:
        return
    q = np.int32(np.round(np.array(pts, np.float64) * 8))
    cv2.polylines(mask, [q], False, float(val), int(th), cv2.LINE_AA, shift=3)


def _taper(mask, pts, w0, w1, val, grow=1.0):
    """太さ w0 → w1（画素）の 線（はじめから grow の 割合まで）"""
    acc = KF.poly_len(pts)
    L = acc[-1] or 1.0
    lim = L * grow
    for i in range(len(pts) - 1):
        if acc[i] >= lim:
            break
        a, b = pts[i], pts[i + 1]
        if acc[i + 1] > lim:
            f_ = (lim - acc[i]) / max(1e-6, acc[i + 1] - acc[i])
            b = (a[0] + (b[0] - a[0]) * f_, a[1] + (b[1] - a[1]) * f_)
        u = ((acc[i] + acc[i + 1]) / 2) / L
        cv2.line(mask, (int(a[0] * 8), int(a[1] * 8)), (int(b[0] * 8), int(b[1] * 8)), float(val), max(1, int(round(w0 + (w1 - w0) * u))), cv2.LINE_AA, shift=3)


def _fine(rng, pts, rough):
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        out += KF.KM._disp_ms(rng, a, b, rough)[1:]
    return out


def _env(age, life):
    if age == 0:
        return .85
    if age >= life - 1:
        return .32
    if age >= life - 2:
        return .62
    return 1.0


def elec(img, t, fi):
    """雷を 描く（今 写って いる 字の まわり）"""
    if t < .12:
        return
    key = obj_key(t)
    o = obj_of(key)
    R, Tv = obj_pose(key, t)
    mask = np.zeros((H, W), np.float32)
    for e in elec_events():
        if e['key'] != key:
            continue
        age = fi - e['f0']
        if not (0 <= age < e['life']):
            continue
        val = _env(age, e['life'])
        if e['kind'] == 'run':
            c = o['outl'][e['ci']]
            tau = age / FPS
            head = e['s0'] + e['dirn'] * e['v'] * tau
            tail = head - e['dirn'] * e['Lseg'] * min(1.0, (age + 1) / 2.5)
            lo, hi = min(head, tail), max(head, tail)
            ks = np.arange(math.ceil(lo / e['step']), math.floor(hi / e['step']) + 1)
            ss = np.r_[lo, ks * e['step'], hi]
            p, n = ol_at(c, ss)
            sp, sn = ol_screen(p, n, R, Tv)
            zz = np.array([0.0] + [_zz(e['seed'], k) for k in ks] + [0.0])
            pts = sp + sn * (e['off'] + e['amp'] * zz)[:, None]
            pts = [tuple(q) for q in pts]
            rf = random.Random(e['seed'] * 31 + fi)
            fine = _fine(rf, pts, (.26, .3))
            wm = e['wm']
            _poly(mask, fine, val, 7 * wm)
            fine2 = _fine(random.Random(e['seed'] * 53 + fi), [(x + rf.uniform(-4, 4) * wm, y + rf.uniform(-4, 4) * wm) for x, y in pts], (.3, .34))
            _poly(mask, fine2, val * .6, 3 * wm)                 # となりを はしる 細い 線（ビリビリ）
            rb = random.Random(e['seed'] * 7 + fi // 2)
            for _ in range(rb.randint(1, 3)):
                if len(pts) < 3:
                    break
                j = rb.randrange(1, len(pts) - 1)
                a0 = math.atan2(sn[j][1], sn[j][0]) + rb.choice((-1, 1)) * rb.uniform(.3, 1.1)
                ln = rb.uniform(20, 64) * wm
                q0 = pts[j]
                q1 = (q0[0] + ln * math.cos(a0), q0[1] + ln * math.sin(a0))
                br = KF.KM._disp_ms(rb, q0, q1, (.35, .4, .45))
                _poly(mask, br, val * .85, 4 * wm)
                if rb.random() < .4:
                    q2 = br[len(br) // 2]
                    a1 = a0 + rb.choice((-1, 1)) * rb.uniform(.4, .9)
                    l2 = ln * rb.uniform(.35, .6)
                    _poly(mask, KF.KM._disp_ms(rb, q2, (q2[0] + l2 * math.cos(a1), q2[1] + l2 * math.sin(a1)), (.35, .4)), val * .65, 2)
        elif e['kind'] == 'jump':
            ca, cb = o['outl'][e['ci']], o['outl'][e['cj']]
            pa, na = ol_screen(ca['P'][e['i']], ca['N'][e['i']], R, Tv)
            pb, nb = ol_screen(cb['P'][e['q']], cb['N'][e['q']], R, Tv)
            rs = random.Random(e['seed'])
            macro = KF.macro_path(rs, tuple(pa), tuple(pb), e['style'])
            mid = _fine(random.Random(e['seed'] + 1), macro, (.14, .2))
            pts = _fine(random.Random(e['seed'] * 7 + fi), mid, (.12,))
            _taper(mask, pts, 5.0, 9.0, val, min(1.0, (age + 1) / 2))
            for _ in range(rs.randint(1, 2)):
                if len(macro) < 3:
                    break
                k = rs.randrange(1, len(macro) - 1)
                q0 = macro[k]
                a0 = math.atan2(macro[k + 1][1] - q0[1], macro[k + 1][0] - q0[0]) + rs.choice((-1, 1)) * rs.uniform(.5, 1.0)
                ln = rs.uniform(30, 70)
                br = _fine(random.Random(e['seed'] + 2 + k), [q0, (q0[0] + ln * math.cos(a0), q0[1] + ln * math.sin(a0))], (.25, .3, .35))
                _taper(mask, br, 4.0, 1.5, val * .85)
        else:                                                    # 字から 外へ
            c = o['outl'][e['ci']]
            pa, na = ol_screen(c['P'][e['i']], c['N'][e['i']], R, Tv)
            a0 = math.atan2(na[1], na[0]) + e['da']
            pb = (pa[0] + e['Lpx'] * math.cos(a0), pa[1] + e['Lpx'] * math.sin(a0))
            rs = random.Random(e['seed'])
            macro = KF.macro_path(rs, tuple(pa), pb, e['style'])
            mid = _fine(random.Random(e['seed'] + 1), macro, (.14, .2))
            pts = _fine(random.Random(e['seed'] * 7 + fi), mid, (.12,))
            _taper(mask, pts, 9.0, 2.5, val, min(1.0, (age + 1) / 2))
            k = rs.randrange(1, len(macro) - 1) if len(macro) > 2 else 0
            if k:
                q0 = macro[k]
                a1 = a0 + rs.choice((-1, 1)) * rs.uniform(.5, .9)
                ln = e['Lpx'] * rs.uniform(.2, .35)
                br = _fine(random.Random(e['seed'] + 3), [q0, (q0[0] + ln * math.cos(a1), q0[1] + ln * math.sin(a1))], (.25, .3, .35))
                _taper(mask, br, 3.2, 1.2, val * .8)
    # ふちの 小さな ビリビリ（毎コマ ちがう 所）
    rz = random.Random(9100 + fi)
    dens = random.Random(9500 + fi // 3).uniform(.4, 1.0)
    nz = int(round((18 if key == 'logo' else 9) * dens))
    if t >= (ELEC_LOGO0 if key == 'logo' else .14):
        lens = np.array([c['tot'] for c in o['outl']])
        cum = np.cumsum(lens) / lens.sum()
        for _ in range(nz):
            ci = int(np.searchsorted(cum, rz.random()))
            c = o['outl'][min(ci, len(o['outl']) - 1)]
            p, n = ol_at(c, rz.uniform(0, c['tot']))
            sp, sn = ol_screen(p, n, R, Tv)
            if not (0 <= sp[0] < W and 0 <= sp[1] < H):
                continue
            a0 = math.atan2(sn[1], sn[0]) + rz.uniform(-1.3, 1.3)
            ln = rz.uniform(10, 30)
            q0 = (sp[0] + sn[0] * rz.uniform(0, 4), sp[1] + sn[1] * rz.uniform(0, 4))
            _poly(mask, KF.KM._disp(rz, q0, (q0[0] + ln * math.cos(a0), q0[1] + ln * math.sin(a0)), 2, .9), rz.uniform(.6, .9), 4)
    if mask.max() > 0:
        rim = cv2.GaussianBlur(cv2.dilate(np.clip(mask * 2, 0, 1), np.ones((5, 5), np.uint8)), (0, 0), 3.0)
        img *= (1 - ELEC_RIM * np.clip(rim, 0, 1))[..., None]
        KF.glow_add(img, mask, ELEC_GLOW)


# ---------------------------------------------------------------- 字の 動き
# 神・様・的・中 の 寄り：(yaw はじめ, おわり, pitch, roll, x はじめ, おわり, y, z)。横に ゆっくり（しまは 横 なので たてには 動かさない）
CU_POSE = ((-21.0, -16.0, 20.0, -3.0, -50.0, 45.0, 60.0, 960.0),
           (19.0, 14.0, 19.0, 3.0, 50.0, -45.0, 60.0, 970.0),
           (-15.0, -10.0, 21.0, -2.5, -45.0, 40.0, 60.0, 950.0),
           (22.0, 17.0, 18.0, 3.0, 45.0, -45.0, 60.0, 980.0))


CU_DRIFT = .35                       # 寄りの 横の 動きの 大きさ（点めつ：字の 細かい 明暗が 画素を 何度も 通らない）


def cu_pose(j, t):
    t0, t1 = TT['CU'][j]
    u = (t - t0) / (t1 - t0) - .5
    y0, y1, pitch, roll, x0, x1, y, z = CU_POSE[j]
    return (y0 + y1) / 2 + (y1 - y0) * u * CU_DRIFT, pitch, roll, (x0 + x1) / 2 + (x1 - x0) * u * CU_DRIFT, y, z


LOGO_END = (5.0, -7.0)               # さいごの 角度（yaw・pitch：右と 下の 側面が 少し 見える）


def logo_final():
    lo = logo_obj()
    zf = FOCAL * lo['size'][0] / (.9 * W)
    return zf, (470 * S - CYS) * zf / FOCAL


def logo_pose(t):
    """ななめ（大きい）→ 正面へ 回りながら ひく → ゆっくり"""
    zf, yf = logo_final()
    t0, t1 = TT['TURN']
    p = min(1.0, max(0.0, (t - t0) / (t1 - t0)))
    u = 1 - (1 - p) ** 2.6
    a = (-13.0, 10.0, -2.5, 170.0, yf + 140.0, zf * .82)
    b = (LOGO_END[0], LOGO_END[1], 0.0, 0.0, yf, zf)
    pose = [x + (y - x) * u for x, y in zip(a, b)]
    s = max(0.0, t - t1)
    pose[0] += .9 * s
    pose[5] *= 1 + .012 * s
    return pose


def white_amt(t):
    w0, w1, w2 = TT['WIN']
    return 1.0 if t <= w1 else max(0.0, 1.0 - sstep(w1, w2, t))


def frame(fi):
    t = fi / FPS
    img = background().copy()
    if t < TT['LOGO']:
        j = min(3, sum(1 for a, b in TT['CU'] if t >= b))
        yaw, pitch, roll, x, y, z = cu_pose(j, t)
        R = rot(yaw, pitch, roll)
        Tv = np.array([x, y, z])
        u = (t - TT['CU'][j][0]) / (TT['CU'][j][1] - TT['CU'][j][0])
        o = cu_obj(j)
        draw(img, o, R, Tv, env_rot=-10 + 14 * u + j * 25, tilt=j * 1.7)
        glints(img, o, unit_h(R, Tv), t, 60 + j)
    else:
        yaw, pitch, roll, x, y, z = logo_pose(t)
        R = rot(yaw, pitch, roll)
        Tv = np.array([x, y, z])
        pv = logo_pose(max(TT['LOGO'], t - .5 / FPS))                # 動きの ぶれ（半コマぶん）
        c1, c0 = project(Tv), project(np.array(pv[3:]))
        mv = (float(c1[0] - c0[0]) * 1.4, float(c1[1] - c0[1]) * 1.4)
        o = logo_obj()
        draw_torii(img, R, Tv, t, mv, o)
        sh = None
        for s0, s1 in TT['SHINE']:
            if s0 - .05 <= t <= s1 + .05:
                q = (t - s0) / (s1 - s0)
                sh = (-2.6 + 5.2 * ease_out(q), .5)
        draw(img, o, R, Tv, env_rot=-14 + 10 * (t - TT['LOGO']), shine=sh, mv=mv)
        glints(img, o, unit_h(R, Tv), t, 70)
    elec(img, t, fi)
    burst_light(img, t)
    nuggets(img, t)
    debris(img, t)
    sparkles(img, t, .8 if t < TT['LOGO'] else .55)
    img = KF.bloom(img)
    w = white_amt(t)
    if w > 0:
        img = img * (1 - w) + np.float32([1.0, 1.0, 1.0]) * w * 1.15 + img * w * .15
    out = KF.tonemap(img)
    return (out * 255 + .5).astype(np.uint8)


def main(out, which=None):
    os.makedirs(out, exist_ok=True)
    for fi in (which or range(N)):
        im = frame(fi)
        cv2.imwrite(os.path.join(out, f'f{fi + 1:03d}.png'), cv2.cvtColor(im, cv2.COLOR_RGB2BGR))
        print('f', fi + 1, flush=True)


# ---------------------------------------------------------------- ためし
def _test(out):
    os.makedirs(out, exist_ok=True)
    for j in range(4):
        o = cu_obj(j)
        img = background().copy()
        yaw = (-20, 18, -14, 22)[j]
        R = rot(yaw, 16.0, (-3, 3, -2, 3)[j])
        Tv = np.array([0.0, 60.0, 1050.0])
        draw(img, o, R, Tv)
        img = KF.bloom(img)
        cv2.imwrite(os.path.join(out, f'cu{j}.png'), cv2.cvtColor((KF.tonemap(img) * 255 + .5).astype(np.uint8), cv2.COLOR_RGB2BGR))
        print('cu', j, flush=True)
    for nm, t in (('logo_tilt', TT['LOGO'] + .1), ('logo', N / FPS - .01)):
        im = frame(int(round(t * FPS)))
        cv2.imwrite(os.path.join(out, f'{nm}.png'), cv2.cvtColor(im, cv2.COLOR_RGB2BGR))
        print(nm, flush=True)


if __name__ == '__main__':
    if sys.argv[2:3] == ['test']:
        _test(sys.argv[1])
    else:
        main(sys.argv[1], [int(v) - 1 for v in sys.argv[2:]] or None)
