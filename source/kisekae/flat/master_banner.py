"""マスター帯の 壁紙の 絵（780×320）：暗い 舞台の まん中で、うしろからの 金の 光を せおって 光る まさちゃんの 3D の 像（flat/metal_glb.py の tengel）
   - 第4.149版（まさちゃん 2026/11/11 02:14「マスター帯の壁紙変える！シルバー帯、ゴールド帯のようにこのファイルの3Dモデルが中央に合って光っているようにして！
     背景の色は、3Dモデルに合う色で合わせてみて！元々あったマスター帯の壁紙と雷の演出とかは消していいよ！」）：深い 緑の 地（ヘアライン）と 金の 光の 輪の 前に 像「Tenger」
   - **第4.158版**（まさちゃん 2026/11/12 09:18「マスター帯の絵、この3Dモデルと入れ替えて！色合いとかは深みつけて、背景の光とかもリアルにカッコよくして！」）：
     像を「Golden Tenger」（金の 馬に 騎手・緑の 台に TENGER の 金の 字）に。背景は 平らな 緑の 地を やめて、**暗い 舞台と 本物らしい 光**に：
       1. 暗い 舞台（像の うしろ だけ 深い 緑が のこる・まわりは 黒に 近い）
       2. 像の うしろの 金の 光（にじみ）と、そこから 四方へ のびる 光の すじ（もやで むらが ある）
       3. 上からの 照明（左右から ななめに 2本の 緑がかった 光・真上から 金の 光：もやの 中の 光の 道）
       4. 像の うしろの 細い 金の 光の 輪（にじみつき・左上が 明るい）：壁紙の 動き（metal_wall.py）の「輪を 回る 光」は この 輪の 上を 通る
       5. ぼけた 光の 玉（金・緑・白：像の まわりには 置かない）
       6. みがいた 暗い 床（うしろの 景色と 金の 光が さかさまに うつる・床の はしの 細い 光）と、台の うしろの 影
       7. 像（色は flat/metal_glb.py の STUDIO：暗い スタジオの 照明）
       8. 像の いちばん 明るい 所の にじみ（レンズの にじみ）
       9. きらめき（金の いちばん 明るい 所に 4つ：台と 台の 字の 上・騎手の 服と 白い ズボンの 上には 出さない）
      10. ふちの 暗がり・少し 締める
     前の 絵の 作り方は 第4.157版（コミット 8d6b80c）の この ファイル
   - 壁紙の 動き（metal_wall.py：きらめき・こまかい 光の 粒・うしろへ 流れる 金の 粉・光の 輪を 回る 光）の 絵と 形は flat/metal_run.py が まとめて 作る
   python3 flat/master_banner.py <出力.webp>"""
import sys, os
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
sys.path.insert(0, os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
from style2d import save_webp

W, Hh = 780, 320
RING_R = 124                   # うしろの 光の 輪の 半径（像の 幅 390px の とき。絵の 上に はみ出す ときは 小さく する）
RING_TOP = 10                  # 光の 輪の いちばん 上は 絵の 上から これだけ 下
HORIZON = 30                   # 台を ぜんぶ 入れる 置き方：床は 台の いちばん 下より これだけ 上（台の 奥）から はじまる ＝ 台が 床の 上に 立つ（まさちゃん 11/11 02:33「台が地面から浮いてるからちゃんと地面につけて！」）
FLOOR_CUT = 262                # 台の 下が 絵の 外に 出る 置き方（第4.150版から）の ときの 床の はじまり（シルバー帯・ゴールド帯の 床の 線 261 と そろえる：台は 床の 手前に 立つ）
QUALITY = 93                   # 絵の 質（WebP）：暗い 所の なだらかな 光に 段が 出ない ように（シルバー帯・ゴールド帯は 88）
PAL = dict(
    stage=('#08281F', '#010807'),                                      # 暗い 舞台：像の うしろの 深い 緑・まわりの 黒
    back=(0.66, 0.47, 0.17), back_wide=(0.10, 0.085, 0.03),            # うしろの 金の 光（にじみ：しん・広い ところ）
    ray=(1.0, 0.80, 0.40), ring=(1.0, 0.82, 0.42),                     # 光の すじ・光の 輪
    beam=(0.55, 0.95, 0.78), beam_top=(1.0, 0.88, 0.55),               # 上からの 照明（左右：緑がかった 光・真上：金）
    bokeh=((1.0, 0.84, 0.45), (0.45, 0.95, 0.72), (1.0, 0.95, 0.85)),  # ぼけた 光の 玉
    floor=('#07261E', '#020B09'), floor_glow=(0.40, 0.33, 0.13), edge=(1.0, 0.86, 0.5),
    bloom=(1.0, 0.88, 0.55), spark=(1.0, 0.97, 0.84))


def _hex(h):
    return np.float32([int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)])


def _sm(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def _blur(a, s):
    return cv2.GaussianBlur(a, (0, 0), s)


def _haze(h, w, octaves=4, base=4, seed=11):
    """もや（なめらかな むら 0〜1）：光の すじと 照明の 道に むらを つける"""
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        n = base * 2 ** o
        g = rng.random((max(2, int(n * h / w) + 2), n + 2)).astype(np.float32)
        out += amp * cv2.resize(g, (w, h), interpolation=cv2.INTER_CUBIC)
        tot += amp
        amp *= 0.5
    return out / tot


def size_of(A):
    """像の 大きさ（第4.149版の 像＝幅 390px を 1 と して）"""
    cols = np.nonzero((A > 0.5).sum(0) > 0)[0]
    return float(cols.max() + 1 - cols.min()) / 390.0


def pedestal_top(A):
    """台の 上の はし（行）：下から 上へ 見て、形の 幅が 台の 幅の 半分より せまく なる 所（その 上は 馬の 足）"""
    wid = (A > 0.5).sum(1)
    rows = np.nonzero(wid > 0)[0]
    gy = int(rows.max())
    lo = max(gy - int(70 * size_of(A)), 0)
    y = lo + int(np.argmax(wid[lo:gy + 1]))                # 台の いちばん 広い 行
    base = float(wid[y])
    while y > 0 and wid[y] > base * 0.5:
        y -= 1
    return y + 1


def compose(R, rng_seed=5, pal=PAL, sparkle=True, info=None, floor_at=None):
    """絵にする。sparkle=False なら きらめきを 描かない（壁紙の 動く きらめきの 下の 絵）。info に dict を 渡すと きらめきの 場所と 長さ・床の 線・台の 上の はし・光の 輪を 入れる。
       台の 下が 絵の 外（下）に 出る 置き方（cut：第4.150版から。台の いちばん 下は R['fit'] の ほんとうの 場所・床に うつる 台と ふちの 影は 絵の 外 なので 描かない）と、
       台を ぜんぶ 入れる 置き方（第4.149版：台が 床に うつる・ふちの すぐ 下に 影）の どちらも できる。floor_at＝床の はじまりの 行を 決めて おく とき"""
    rng = np.random.default_rng(rng_seed)
    C = lambda v: np.asarray(v, np.float32)
    yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
    A = np.clip(R['a'], 0, 1)
    rgb = R['srgb']
    k = size_of(A)
    rows = np.nonzero(A.sum(1) > 0.5)[0]
    cut = int(rows.max()) >= Hh - 1                        # 台の 下が 絵の 外に 出て いる
    gy = int(R['fit'][3]) - 1 if cut else int(rows.max())  # 台の いちばん 下（絵の 外の ときも ほんとうの 場所）
    ped = pedestal_top(A)
    # 台（列ごとの いちばん 下：台は 少し 上から 見て いるので、ふちは まっすぐな 横線で ない）
    Ap = A.copy()
    Ap[:ped] = 0
    pm = Ap > 0.5
    has = pm.any(0)
    yb = np.where(has, Hh - 1 - np.argmax(pm[::-1], axis=0), -1)
    xs_p = np.nonzero(has)[0]
    bw = float(xs_p.max() + 1 - xs_p.min())
    pcx = float(xs_p.min() + xs_p.max() + 1) / 2
    cx = pcx                                               # 舞台の まん中（うしろの 光・光の 輪・照明）＝台の まん中：像は 台ごと 舞台の まん中に 立つ（馬は 台の まん中に いるとは かぎらない：しっぽが 長い）
    rcy = float(rows.min() + ped) / 2 + 5                  # 光の 輪の まん中の 高さ：馬と 騎手の まん中より 少し 下
    rr = min(RING_R * k, rcy - RING_TOP)                   # 輪の 上が 絵に おさまる 大きさ
    sx, sy = cx + 6, rcy - 14                              # うしろの 光の まん中（馬の 体の うしろ）
    hy = int(floor_at) if floor_at is not None else (FLOOR_CUT if cut else int(round(gy - HORIZON * k)))      # 床の はじまり
    haze = _haze(Hh, W)
    # ---------- 1. 暗い 舞台（像の うしろ だけ 深い 緑 → まわりは 黒） ----------
    r0 = np.sqrt(((xx - sx) / 430) ** 2 + ((yy - sy) / 250) ** 2)
    bg = _hex(pal['stage'][0]) * np.clip(1 - r0, 0, 1)[..., None] ** 1.5 + _hex(pal['stage'][1])
    # ---------- 2. うしろの 金の 光（にじみ）と 光の すじ ----------
    core = np.exp(-(((xx - sx) / 150) ** 2 + ((yy - sy) / 95) ** 2))
    wide = np.exp(-(((xx - sx) / 330) ** 2 + ((yy - sy) / 190) ** 2))
    bg = bg + core[..., None] * C(pal['back']) + wide[..., None] * C(pal['back_wide'])
    ang = np.arctan2(yy - sy, xx - sx)
    rad = np.hypot(xx - sx, yy - sy)
    rays = np.zeros((Hh, W), np.float32)
    for i in range(46):                                    # すじ 46本（向き・太さ・強さは ばらばら）
        th = rng.uniform(-np.pi, np.pi); w = rng.uniform(0.012, 0.055); a = rng.uniform(0.25, 1.0) ** 1.6
        d = np.angle(np.exp(1j * (ang - th)))
        rays += a * np.exp(-(d / w) ** 2)
    rays = (rays * np.exp(-rad / 270) * _sm(18, 70, rad)) ** 1.25 * (0.5 + 1.0 * haze)
    bg = bg + _blur(rays, 1.4)[..., None] * C(pal['ray']) * 0.36
    # ---------- 3. 上からの 照明（もやの 中の 光の 道：左右から ななめに・真上から） ----------
    for (px, py, tx, ty, wd, kk, col) in ((cx - 270, -70, cx - 60, 200, 0.105, 0.20, pal['beam']), (cx + 270, -70, cx + 60, 200, 0.105, 0.20, pal['beam']), (cx, -110, cx, 220, 0.16, 0.10, pal['beam_top'])):
        ax, ay = tx - px, ty - py
        L = np.hypot(ax, ay); ax, ay = ax / L, ay / L
        t = (xx - px) * ax + (yy - py) * ay
        dperp = np.abs((xx - px) * ay - (yy - py) * ax)
        cone = np.exp(-(dperp / (np.maximum(t, 1) * wd + 4)) ** 2) * _sm(0, 60, t) * np.exp(-np.maximum(t, 0) / 420)
        bg = bg + (cone * (0.7 + 0.6 * haze))[..., None] * C(col) * kk
    # ---------- 4. 光の 輪（像の うしろの 細い 金の 輪：にじみつき・左上が 明るい） ----------
    dr = np.sqrt((xx - cx) ** 2 + (yy - rcy) ** 2) - rr
    lit = 0.62 + 0.38 * np.cos(np.arctan2(yy - rcy, xx - cx) + 2.2)
    ring = (np.exp(-(dr / 1.25) ** 2) * 0.85 + np.exp(-(dr / 5.0) ** 2) * 0.22 + np.exp(-(dr / 16.0) ** 2) * 0.07) * lit
    bg = bg + ring[..., None] * C(pal['ring'])
    # ---------- 5. ぼけた 光の 玉（像の まわりには 置かない） ----------
    bok = np.zeros((Hh, W, 3), np.float32)
    for i in range(16):
        bx = rng.uniform(20, W - 20); by = rng.uniform(8, 200); br = rng.uniform(5, 15)
        if abs(bx - cx) < 150 and by > 60:
            continue
        col = C(pal['bokeh'][i % 3]); al = rng.uniform(0.05, 0.14)
        d = np.sqrt((xx - bx) ** 2 + (yy - by) ** 2)
        disc = _sm(br + 1.2, br - 1.2, d) * (0.75 + 0.25 * _sm(br * 0.55, br, d))          # ふちが 少し 明るい 丸（レンズの ぼけ）
        bok += disc[..., None] * col * al
    bg = bg + _blur(bok, 0.8)
    # ---------- 6. 床（みがいた 暗い 床：うしろの 景色と 金の 光が うつる） ----------
    floor = _sm(hy - 1, hy + 3, yy)
    tfl = np.clip((yy - hy) / max(Hh - hy, 1), 0, 1)[..., None]
    fcol = _hex(pal['floor'][0]) * (1 - tfl) + _hex(pal['floor'][1]) * tfl
    fcol = fcol + (np.exp(-(((xx - sx) / 210) ** 2)) * np.exp(-((yy - hy) / 34.0)))[..., None] * C(pal['floor_glow']) * 0.9          # うしろの 金の 光（たてに のびて うつる）
    refl_ring = np.exp(-((np.sqrt((xx - cx) ** 2 + ((2 * hy - yy) - rcy) ** 2) - rr) / 3.0) ** 2) * 0.10 * np.exp(-(yy - hy) / 30.0)
    fcol = fcol + refl_ring[..., None] * C(pal['ring'])
    mirror = bg[np.clip(2 * hy - yy, 0, Hh - 1).astype(np.int32), xx.astype(np.int32)]                                          # うしろの 景色（さかさま）
    mirror = cv2.GaussianBlur(mirror, (0, 0), sigmaX=1.2, sigmaY=3.5)
    fcol = fcol + mirror * (0.34 * np.exp(-(yy - hy) / 46.0))[..., None]
    fcol = fcol * (0.9 + 0.2 * _blur(haze, 3))[..., None]
    bg = bg * (1 - floor[..., None]) + fcol * floor[..., None]
    bg = bg + (np.exp(-((yy - hy) / 1.1) ** 2) * np.exp(-((xx - sx) / 300) ** 2))[..., None] * C(pal['edge']) * 0.16                 # 床の はしの 細い 光
    if not cut:
        # 台が 床に うつる（ふちを さかいに さかさま・下へ いくほど うすく）
        refl_rgb = np.zeros_like(rgb); refl_a = np.zeros_like(A)
        for d in range(1, int(round((HORIZON + 44) * k))):
            ys_d, ys_s = yb[xs_p] + d, yb[xs_p] - d
            ok = (ys_d < Hh) & (ys_s >= 0)
            refl_rgb[ys_d[ok], xs_p[ok]] = rgb[ys_s[ok], xs_p[ok]]
            refl_a[ys_d[ok], xs_p[ok]] = A[ys_s[ok], xs_p[ok]] * (0.50 * np.exp(-d / (22.0 * k)))
        refl_rgb = _blur(refl_rgb, 1.2); refl_a = _blur(refl_a, 1.2)
        bg = bg * (1 - refl_a[..., None]) + refl_rgb * refl_a[..., None]
        # 影：台の ふちの すぐ 下（こい・細い）と、台の まわりの やわらかい 影
        edge = np.zeros((Hh, W), np.float32)
        for d in range(0, 7):
            ys_d = yb[xs_p] + d
            ok = ys_d < Hh
            edge[ys_d[ok], xs_p[ok]] = np.maximum(edge[ys_d[ok], xs_p[ok]], 1 - d / 7.0)
        contact = np.clip(_blur(edge, 1.6) * 1.25, 0, 1) * 0.78
        soft = np.exp(-(((xx - pcx) / (bw * 0.66)) ** 2 + ((yy - (gy - HORIZON * k * 0.30)) / (HORIZON * k * 0.62)) ** 2)) * 0.50 * floor
        bg = bg * (1 - np.clip(contact + soft, 0, 0.9)[..., None])
    else:
        # 台の 下は 絵の 外：床に うつる 台と ふちの 影は 見えない。台の うしろの 床に やわらかい 影 だけ（台が 床の 上に 立って いる）
        soft = np.exp(-(((xx - pcx) / (bw * 0.62)) ** 2 + ((yy - (Hh + 4)) / (max(Hh - hy, 8) * 0.95)) ** 2)) * 0.55 * floor
        bg = bg * (1 - np.clip(soft, 0, 0.9)[..., None])
    # ---------- 7. 像 ----------
    img = bg * (1 - A[..., None]) + rgb * A[..., None]
    # ---------- 8. 像の いちばん 明るい 所の にじみ（レンズ） ----------
    hi = np.clip((rgb.max(2) - 0.80) / 0.20, 0, 1) * A
    bloom = _blur(hi, 5.0) * 0.30 + _blur(hi, 14.0) * 0.16
    img = img + bloom[..., None] * C(pal['bloom']) * 0.75
    # ---------- 9. きらめき（金の いちばん 明るい 所に 4本の 光：台と 台の 字の 上・騎手の 服と 白い ズボンの 上には 出さない） ----------
    lum = rgb.max(2) * A
    if 'metal' in R:                                       # 金の 上 だけ（騎手の 白い ズボンは 明るい けれど、金の きらめきを のせると しみに 見える）
        lum = lum * (R['metal'] > 0.5)
    lum[ped - 6:] = 0
    lum_s = _blur(lum, 1.0)
    spark = np.zeros((Hh, W), np.float32)
    taken = []
    for idx in np.argsort(lum_s.ravel())[::-1][:8000]:
        y, x = divmod(int(idx), W)
        if lum_s[y, x] < 0.86:
            break
        if all((x - tx) ** 2 + (y - ty) ** 2 > 75 ** 2 for tx, ty in taken):
            taken.append((x, y))
        if len(taken) >= 4:
            break
    if info is not None:
        info['gy'] = gy
        info['hy'] = hy
        info['ped'] = ped
        info['ring'] = [round(cx, 1), round(rcy, 1), int(round(rr))]
        info['cut'] = bool(cut)
        info['spark'] = []
    for (x, y) in taken:
        L = rng.uniform(12, 20)
        if info is not None:
            info['spark'].append((int(x), int(y), float(L)))
        if not sparkle:
            continue
        for (dx, dy, l) in ((1, 0, L), (0, 1, L * 0.75), (0.7, 0.7, L * 0.35), (0.7, -0.7, L * 0.35)):
            for s in (1, -1):
                cv2.line(spark, (int(x * 16), int(y * 16)), (int((x + dx * l * s) * 16), int((y + dy * l * s) * 16)), 1.0, 1, cv2.LINE_AA, shift=4)
        cv2.circle(spark, (int(x * 16), int(y * 16)), int(2.2 * 16), 1.0, -1, cv2.LINE_AA, shift=4)
    spark = spark * 0.9 + _blur(spark, 2.0) * 0.6 + _blur(spark, 7.0) * 0.4
    img = img + spark[..., None] * C(pal['spark']) * 0.9
    # ---------- 10. ふちの 暗がり・少し 締める ----------
    v = np.clip(1.10 - np.sqrt(((xx - W * .5) / (W * .58)) ** 2 + ((yy - Hh * .44) / (Hh * .86)) ** 2) * .50, .34, 1)[..., None]
    img = np.clip(img * v, 0, 1)
    img = np.clip(img + (img - 0.5) * 0.10 * (1 - np.abs(img - 0.5) * 2), 0, 1)
    return img.astype(np.float32)


if __name__ == '__main__':
    import metal_glb as MG
    save_webp(compose(MG.render('tengel')), sys.argv[1], q=QUALITY)
