"""マスター帯の 壁紙の 絵（780×320・第4.149版）：深い 緑の 地と 金の 光の 輪の 前に、まさちゃんの 3D の 像
   （「Tenger」：緑の 台の 上を 駆ける 金の 馬・緑の たてがみと 鞍・台に TENGER／テンゲル の 金の 字。flat/metal_glb.py の tengel）が まん中で 光る。
   まさちゃん 2026/11/11 02:14「マスター帯の壁紙変える！シルバー帯、ゴールド帯のようにこのファイルの3Dモデルが中央に合って光っているようにして！
   背景の色は、3Dモデルに合う色で合わせてみて！元々あったマスター帯の壁紙と雷の演出とかは消していいよ！」
   - 作りは シルバー帯・ゴールド帯（flat/silver_banner.py の compose）と 同じ：地（上は 明るく 下は 暗く・ヘアライン）・像の うしろの やわらかい 光・光の 輪・
     みがいた 床（像が うつる）・床の 影・ふちの 暗がり・像の いちばん 明るい 所に 小さな きらめき（馬の 所 だけ：台の 字の 上には 出さない）
   - 色は 像に 合わせる：地と 床は 像の 台・たてがみと 同じ 深い 緑、光は 金
   - 壁紙の 動き（metal_wall.py：きらめき・こまかい 光の 粒・うしろへ 流れる 金の 粉・光の 輪を 回る 光）の 絵と 形は flat/metal_run.py が まとめて 作る
   python3 flat/master_banner.py <出力.webp>"""
import sys, os
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
sys.path.insert(0, os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
from style2d import save_webp, grad_v, over
from paint import fbm, blur, smoothstep

W, Hh = 780, 320
RING_R = 124                   # うしろの 光の 輪の 半径
HORIZON = 30                   # 床は 台の いちばん 下より これだけ 上（台の 奥）から はじまる ＝ 台が 床の 上に 立つ（まさちゃん 11/11 02:33「台が地面から浮いてるからちゃんと地面につけて！」）
PAL = dict(
    bg=[(0, '#124A3A'), (0.5, '#0C352B'), (1, '#07201B')],              # 深い 緑の 地（上は 明るく・下は 暗く）
    glow=(0.035, 0.150, 0.100), core=(0.060, 0.130, 0.060),              # 像の うしろの 光（エメラルドの 緑）
    ring=(1.0, 0.84, 0.42), floor=[(0, '#0F3B30'), (1, '#051813')], spark=(1.0, 0.97, 0.84))


def pedestal_top(A):
    """台の 上の はし（行）：下から 上へ 見て、形の 幅が 台の 幅の 半分より せまく なる 所（その 上は 馬の 足）"""
    wid = (A > 0.5).sum(1)
    rows = np.nonzero(wid > 0)[0]
    gy = int(rows.max())
    lo = max(gy - 70, 0)
    y = lo + int(np.argmax(wid[lo:gy + 1]))                # 台の いちばん 広い 行
    base = float(wid[y])
    while y > 0 and wid[y] > base * 0.5:
        y -= 1
    return y + 1


def compose(R, rng_seed=5, pal=PAL, sparkle=True, info=None):
    """絵にする。sparkle=False なら きらめきを 描かない（壁紙の 動く きらめきの 下の 絵）。info に dict を 渡すと きらめきの 場所と 長さ・床の 線・台の 上の はし・光の 輪を 入れる"""
    rng = np.random.default_rng(rng_seed)
    yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
    A = np.clip(R['a'], 0, 1)
    rgb = R['srgb']
    rows = np.nonzero(A.sum(1) > 0.5)[0]
    gy = int(rows.max())                                   # 床の 線：台の いちばん 下
    ped = pedestal_top(A)
    cols = np.nonzero(A.sum(0) > 0.5)[0]
    cx = float(cols.min() + cols.max() + 1) / 2
    cy = float(rows.min() + ped) / 2 + 22                  # 馬の 体の まん中（少し 下：輪の 上が 絵に おさまる）
    # ---------- 背景：深い 緑の 地＋ヘアライン ----------
    bg = grad_v(Hh, W, pal['bg'])
    hair = fbm(Hh, W, 3, 2, seed=8)
    hair = cv2.GaussianBlur((hair - .5) * 2, (0, 0), sigmaX=22, sigmaY=0.4)      # 横に 長く のばす
    bg = bg * (1 + 0.07 * hair[..., None])
    glow = np.exp(-(((xx - cx) / 300) ** 2 + ((yy - cy) / 150) ** 2))
    core = np.exp(-(((xx - cx) / 150) ** 2 + ((yy - cy) / 82) ** 2))
    bg = bg + glow[..., None] * np.array(pal['glow']) + core[..., None] * np.array(pal['core'])
    # 大きな うすい 輪（金の メダルの ように：像の うしろ）
    rr = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    ring = np.exp(-((rr - RING_R) / 3.0) ** 2) * 0.34 + np.exp(-((rr - RING_R) / 11.0) ** 2) * 0.07 + smoothstep(RING_R + 2, RING_R - 10, rr) * 0.03
    bg = bg + ring[..., None] * np.array(pal['ring'])
    # 床：台の 奥（HORIZON だけ 上）から 下は、みがいた 暗い 緑。台は 床の 上に 立つ（台の ふちの すぐ 下に 影・台が 床に うつる）
    hy = gy - HORIZON
    floor = smoothstep(hy - 1, hy + 5, yy)
    tfl = np.clip((yy - hy) / max(Hh - hy, 1), 0, 1)[..., None]
    f0, f1 = grad_v(2, 1, pal['floor'])[0, 0], grad_v(2, 1, pal['floor'])[1, 0]
    fcol = f0 * (1 - tfl) + f1 * tfl
    fcol = fcol + np.exp(-(((xx - cx) / 260) ** 2 + ((yy - hy) / 26) ** 2))[..., None] * np.array(pal['glow']) * 0.55      # 奥の 光が 床に うすく うつる
    bg = bg * (1 - floor[..., None]) + fcol * floor[..., None]
    bg = bg + (np.exp(-((yy - hy) / 1.3) ** 2) * np.exp(-((xx - cx) / 330) ** 2))[..., None] * np.array(pal['ring']) * 0.10          # 床と 地の さかいの 細い 光
    # 台の 下の ふち（列ごと）：台は ななめから 見て いるので、ふちは まっすぐな 横線で ない
    Ap = A.copy()
    Ap[:ped] = 0
    pm = Ap > 0.5
    has = pm.any(0)
    yb = np.where(has, Hh - 1 - np.argmax(pm[::-1], axis=0), -1)                     # 列ごとの 台の いちばん 下
    # 台が 床に うつる（ふちを さかいに さかさま・下へ いくほど うすく）
    refl_rgb = np.zeros_like(rgb); refl_a = np.zeros_like(A)
    xs_p = np.nonzero(has)[0]
    for d in range(1, HORIZON + 44):
        ys_d, ys_s = yb[xs_p] + d, yb[xs_p] - d
        ok = (ys_d < Hh) & (ys_s >= 0)
        refl_rgb[ys_d[ok], xs_p[ok]] = rgb[ys_s[ok], xs_p[ok]]
        refl_a[ys_d[ok], xs_p[ok]] = A[ys_s[ok], xs_p[ok]] * (0.50 * np.exp(-d / 22.0))
    refl_rgb = blur(refl_rgb, 1.2); refl_a = blur(refl_a, 1.2)
    bg = bg * (1 - refl_a[..., None]) + refl_rgb * refl_a[..., None]
    # 影：台の ふちの すぐ 下（こい・細い）と、台の まわりの やわらかい 影
    edge = np.zeros((Hh, W), np.float32)
    for d in range(0, 7):
        ys_d = yb[xs_p] + d
        ok = ys_d < Hh
        edge[ys_d[ok], xs_p[ok]] = np.maximum(edge[ys_d[ok], xs_p[ok]], 1 - d / 7.0)
    contact = np.clip(blur(edge, 1.6) * 1.25, 0, 1) * 0.78
    bw = float(xs_p.max() + 1 - xs_p.min())
    pcx = float(xs_p.min() + xs_p.max() + 1) / 2
    soft = np.exp(-(((xx - pcx) / (bw * 0.66)) ** 2 + ((yy - (gy - HORIZON * 0.30)) / (HORIZON * 0.62)) ** 2)) * 0.50 * floor
    bg = bg * (1 - np.clip(contact + soft, 0, 0.9)[..., None])
    # ---------- 像を 重ねる ----------
    img = over(bg, rgb, A)
    # きらめき（馬の いちばん 明るい 所に 4本の 光：台と 台の 字の 上には 出さない）
    lum = rgb.max(2) * A
    lum[ped - 6:] = 0
    lum_s = cv2.GaussianBlur(lum, (0, 0), 1.0)
    spark = np.zeros((Hh, W), np.float32)
    taken = []
    for idx in np.argsort(lum_s.ravel())[::-1][:6000]:
        y, x = divmod(int(idx), W)
        if lum_s[y, x] < 0.86:
            break
        if all((x - tx) ** 2 + (y - ty) ** 2 > 70 ** 2 for tx, ty in taken):
            taken.append((x, y))
        if len(taken) >= 4:
            break
    if info is not None:
        info['gy'] = gy
        info['hy'] = hy
        info['ped'] = ped
        info['ring'] = [round(cx, 1), round(cy, 1), RING_R]
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
    spark = spark * 0.9 + blur(spark, 2.0) * 0.6 + blur(spark, 7.0) * 0.4
    img = img + spark[..., None] * np.array(pal['spark']) * 0.9
    # ふちの 暗がり
    v = np.clip(1.05 - np.sqrt(((xx - W * .5) / (W * .70)) ** 2 + ((yy - Hh * .42) / (Hh * .95)) ** 2) * .30, .55, 1)[..., None]
    img = np.clip(img * v, 0, 1)
    img = np.clip(img + (img - 0.5) * 0.08 * (1 - np.abs(img - 0.5) * 2), 0, 1)        # 少し 締める
    return img.astype(np.float32)


if __name__ == '__main__':
    import metal_glb as MG
    save_webp(compose(MG.render('tengel')), sys.argv[1])
