"""浮世絵風の 壁紙（壁紙パック）の 小波と しぶきを 絵（WebP）に する。
   第4.100版 まさちゃん「赤四角の小波は、大波と同じ絵の質感にして！あと小波の形は3枚目と同じ感じにして！」「三枚目の赤線の小波のように！」：
     小波（small_wave）は まさちゃんの 赤い 線の 形（左の 海の 線から 低く 長く もり上がり、波の 先が 右へ まいて 少し はね上がり、
     その 下から 長い すそが 右へ 海の 線まで おりる・中に もう 1本の 線）を そのまま 使い（左右に うら返さない）、大波と 同じ 描き方で ぬる：
     浮世絵の 平らな 4色（白・明るい 青・藍・濃い 藍）・濃い 藍の ふちの 線・上の ふちに そった 明るい 青 → 藍 → 濃い 藍の 帯・白い すじ・
     波の 先に 白い 泡の かさと 爪（指の ような 泡が 濃い 藍の ふちで 下へ まく）。numpy で 大きく 描いて 3倍に する（iPhone でも ふちが くっきり）。
   第4.101版 まさちゃん（4.100 の 8倍の 小波に 赤い 線を 書きこんで）「小波この真ん中の第4に書き足した赤線に合わせて作成して！あともっと大波によせた絵にして！」：
     形（左の 海の 線から 低く 長く もり上がり、波の 先が 右へ まいて、長い すそが 右へ おりる）は そのまま。書きこみに 合わせて
     ① 上の ふち ぜんぶに そって 白い 泡の 帯（左の 肩では 細く・頭の 近くで 太く・波の 先で とじる：BAND）・帯の 下の ふちは 大波の 泡の 爪の ような
       小さな 指が 右下へ のびる（FRINGE）・その 下に 明るい 青
     ② 中の 線（INN：左の 根もとから 立ち上がって 帯の 下を 右へ ゆるく おりる 白い すじ）。その 下は 大波の 体と 同じ 濃い 藍に 藍の すじと 小さな 明るい 点
     ③ 波の 先の 小さな かぎ（爪）は なくす（×）。白い 丸は なし（第4.98版から）
   しぶき（波の 先が 落ちた 所で ふき上がる しぶき 2つ・小波の 頭の しぶき 2つ・大波の 頭から 吹き飛ぶ しぶき 2つ）は pack/ukiyoe.py の SVG を
   ブラウザ（Chromium）で 3倍に 描く。ぜんぶ 1まいの シートに ならべる（ページでは 部品の 背景に して background-position で えらぶ）
   python3 kisekae/pack/make/ukiyoe_foam.py → ios/kisekae_blobs/<id>.webp・kisekae/pack/blobs.json の ukiyoe.foam"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))          # kisekae
from sheets import save_webp, record, preview_png  # noqa: E402
import numpy as np  # noqa: E402
import cv2  # noqa: E402

Z = 3
GAP = 4

# まさちゃんの 赤い 線（16:05 の 3枚目の 画像から 写した 線を 0〜1 に：u＝左の はし → 右の はし・v＝海の 線からの 高さ（いちばん 高い 所＝1））
OUTER = [(0.0, .03), (.06, .0), (.113, .0), (.132, .04), (.151, .12), (.17, .2), (.189, .3), (.208, .42), (.226, .52), (.245, .6),
         (.264, .69), (.283, .76), (.302, .82), (.321, .87), (.34, .91), (.358, .93), (.377, .945), (.396, .955), (.415, .96), (.453, .97),
         (.491, .995), (.509, 1.0), (.528, .995), (.547, .97), (.566, .9), (.585, .8), (.604, .72), (.623, .64), (.642, .6), (.66, .585)]
TIP = [(.672, .6), (.684, .625)]                       # 波の 先（右へ 少し とがる・第4.101版：先の かぎ（HOOK）は なし）
UNDER_TIP = [(.677, .56), (.668, .51)]                 # 先の 下へ もどる
TAIL = [(.68, .46), (.698, .40), (.717, .35), (.736, .30), (.755, .265), (.774, .23), (.792, .19), (.811, .15), (.83, .12), (.849, .09),
        (.868, .07), (.887, .055), (.906, .048), (.925, .04), (.943, .035), (1.0, .03)]
# 第4.101版 まさちゃんの 書きこみ（4.100 の 8倍の 小波の 上の 赤い 線）を 0〜1 に：
BAND = [(.18, 0.0), (.21, .022), (.24, .063), (.27, .09), (.30, .095), (.33, .105), (.36, .12), (.39, .133), (.42, .142), (.45, .148),
        (.48, .158), (.51, .17), (.54, .172), (.57, .162), (.60, .125), (.63, .062), (.66, .018), (.675, 0.0)]     # 白い 泡の 帯の 厚さ（上の ふちから 下へ・高さの わりあい）
INN = [(.268, .06), (.285, .2), (.30, .305), (.33, .447), (.36, .543), (.39, .600), (.42, .612), (.45, .600), (.48, .537), (.51, .453), (.54, .383),
       (.57, .311), (.60, .257), (.63, .238), (.66, .236), (.675, .238)]                                          # 中の 線（白い すじ）
CORE_L = [(.25, -.4), (.258, -.18)]                                                                                # 濃い 藍の 所の 左の ふち（中の 線の 下へ）
CORE_R = [(.70, .225), (.73, .17), (.77, .10), (.81, .045), (.85, 0.0), (.875, -.2), (.89, -.4)]                   # 〃 右の ふち（白い 線は なし）
FRINGE = [(.385, .7), (.43, .85), (.475, .95), (.52, 1.0), (.565, .95), (.605, .8)]                               # 帯の 下の ふちの 小さな 指（u・大きさ）
TAIL_STREAK = [(.73, .3), (.77, .245), (.82, .19), (.87, .14), (.92, .10)]                                         # すその 明るい すじ
SPECKS = 6                                                                                                         # 濃い 藍の 所の 小さな 明るい 点（大波の 体の 点）
PAL = dict(white=(246, 241, 227), light=(178, 199, 222), mid=(84, 112, 160), dark=(27, 37, 92))       # 大波と 同じ 色（make/ukiyoe_great.py の PAL）
PAPER = (241, 230, 207)


def cr(pts, n=8):
    """とおる 点の なめらかな 線（Catmull-Rom）"""
    P = np.array(pts, np.float64)
    if len(P) < 3:
        return P
    out = []
    Q = np.vstack([P[0] * 2 - P[1], P, P[-1] * 2 - P[-2]])
    for i in range(1, len(Q) - 2):
        p0, p1, p2, p3 = Q[i - 1], Q[i], Q[i + 1], Q[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(P[-1])
    return np.array(out)


def top_curve():
    """上の ふちの 高さ（u → v）：波の 先までは OUTER＋TIP・その 先は すそ（UNDER_TIP＋TAIL）"""
    t1 = cr(OUTER + TIP)
    t2 = cr(UNDER_TIP + TAIL)
    us = np.linspace(0, 1, 2001)
    v1 = np.interp(us, t1[:, 0], t1[:, 1], right=-1)
    v2 = np.interp(us, t2[:, 0], t2[:, 1], left=-1)
    return us, np.maximum(v1, v2)


def small_wave(W, H, haze=0.0, pad=(2, 3), S=Z, SS=6, seed=5):
    """はば W・高さ H（画面の px）の 小波 1つ → RGBA u8（S 倍の 画素）。左右に 1px・上に pad[0]・下に pad[1] の よゆう（根もとは 上から pad[0]＋H）。
       第4.101版：まさちゃんの 書きこみ どおり（白い 泡の 帯・中の 線・先の かぎ なし）＋大波と 同じ 色の 帯・すじ・点・泡の 爪"""
    import random
    K = S * SS
    PT, PB = pad
    Wp, Hp = int(round((W + 2) * K)), int(round((H + PT + PB) * K))
    base = (H + PT) * K

    def col(name):
        c = np.array(PAL[name], np.float32)
        return tuple(float(x) for x in (c + (np.array(PAPER, np.float32) - c) * haze * (.3 if name == 'white' else .7)))

    def m(pts):
        P = np.array(pts, np.float64)
        return np.stack([(1 + P[:, 0] * W) * K, base - P[:, 1] * H * K], 1)

    def sh(pts):
        return np.round(pts * 4).astype(np.int32)
    top, under = m(cr(OUTER + TIP)), m(cr(UNDER_TIP + TAIL))
    sil = np.vstack([top, under, [[(1 + W) * K, base + PB * K], [K, base + PB * K]]])
    mask = np.zeros((Hp, Wp), np.uint8)
    cv2.fillPoly(mask, [sh(sil)], 255, lineType=cv2.LINE_AA, shift=2)
    A = mask.astype(np.float32) / 255
    yy, xx = np.mgrid[0:Hp, 0:Wp].astype(np.float32)
    U = (xx / K - 1) / W
    V = (base - yy) / (H * K)
    us, tv = top_curve()
    rel = np.interp(U, us, tv).astype(np.float32) - V                  # 上の ふちからの 深さ（高さの わりあい）
    bu, bv = [p[0] for p in BAND], [p[1] for p in BAND]
    bt = np.interp(U, bu, bv, left=0, right=0).astype(np.float32)
    core_line = cr(CORE_L + INN + CORE_R)
    cv_ = np.interp(U, core_line[:, 0], core_line[:, 1], left=-1, right=-1).astype(np.float32)
    # 色の 帯：藍 → 中の 線の 下は 濃い 藍（大波の 体）・上の ふちに そって 明るい 青・いちばん 上に 白い 泡の 帯
    rgb = np.zeros((Hp, Wp, 3), np.float32)
    rgb[:] = col('mid')
    rgb[V < cv_] = col('dark')
    light = ((rel >= bt) & (rel < bt + .075) & (bt > .01)) | ((bt <= .01) & (rel * H < .95))
    rgb[light] = col('light')
    rgb[(rel < bt) & (bt > 0)] = col('white')

    def line(pts, c, w):
        cv2.polylines(rgb, [sh(m(cr(pts)))], False, c, max(1, int(round(w * K))), cv2.LINE_AA, shift=2)

    def taper(pts, c, w0, w1, n=10):
        """両はしが 細い すじ（大波の 体の すじ）"""
        P = m(cr(pts, n))
        k = len(P)
        for i in range(k - 1):
            t = i / max(1, k - 2)
            w = w0 + (w1 - w0) * (1 - abs(2 * t - 1))
            cv2.line(rgb, tuple(np.round(P[i] * 4).astype(int)), tuple(np.round(P[i + 1] * 4).astype(int)), c, max(1, int(round(w * K))), cv2.LINE_AA, shift=2)

    def offset(pts, dv, du=0.0, a=0, b=None):
        return [(u + du, max(0.0, v - dv)) for u, v in pts[a:b]]
    lo = [(u, float(np.interp(u, us, tv)) - b) for u, b in BAND if b > 0]       # 帯の 下の ふち
    taper(offset(INN, .16, .012, 2, 13), col('mid'), .02 * H, .075 * H)       # 濃い 藍の 所の 藍の すじ 2本
    taper(offset(INN, .32, .022, 4, 12), col('mid'), .02 * H, .06 * H)
    taper(offset(lo, .14, .0, 2, 12), col('light'), .015 * H, .045 * H)        # 帯の 下の 明るい すじ
    taper(TAIL_STREAK, col('light'), .015 * H, .04 * H)                        # すその 明るい すじ
    R = random.Random(seed)                                                    # 小さな 明るい 点（大波の 体の 点：白い 丸は 入れない）
    for _ in range(SPECKS):
        u = R.uniform(.33, .62)
        vtop = float(np.interp(u, core_line[:, 0], core_line[:, 1]))
        v = R.uniform(.12, max(.15, vtop - .08))
        r = R.uniform(.014, .022) * H
        cv2.circle(rgb, tuple(np.round(m([(u, v)])[0] * 4).astype(int)), max(1, int(round(r * K * 4))), col('light'), -1, cv2.LINE_AA, shift=2)
    line(lo, col('dark'), .028 * H)                                            # 帯の 下の ふち（細い 濃い 藍の 線）
    line(INN, col('white'), .042 * H)                                          # 中の 線（白）
    # 泡の ふちの 小さな 指（大波の 泡の 爪：帯の 下の ふちから 右下へ のびて 先が とがる・白・濃い 藍の ふち）
    for u0, s0 in FRINGE:
        vb = float(np.interp(u0, us, tv)) - float(np.interp(u0, bu, bv))
        L = .075 * s0
        w0 = .016 * s0
        fin = [(u0 - w0, vb + .03), (u0 - w0 * .9, vb - L * .25), (u0 - w0 * .35, vb - L * .7), (u0 + w0 * .45, vb - L),
               (u0 + w0 * 1.35, vb - L * 1.08), (u0 + w0 * .75, vb - L * .62), (u0 + w0 * .55, vb - L * .2), (u0 + w0 * .9, vb + .03)]
        P = m(cr(fin, 6))
        cv2.fillPoly(rgb, [sh(P)], col('white'), cv2.LINE_AA, shift=2)
        cv2.polylines(rgb, [sh(P[3:-3])], False, col('dark'), max(1, int(round(.022 * H * K))), cv2.LINE_AA, shift=2)
    # 外の ふち（濃い 藍の 線：大波の 線と 同じ くらい）
    lw = .055 * H
    cv2.polylines(rgb, [sh(top)], False, col('dark'), int(round(lw * K)), cv2.LINE_AA, shift=2)
    cv2.polylines(rgb, [sh(under)], False, col('dark'), int(round(lw * .9 * K)), cv2.LINE_AA, shift=2)
    pre = np.dstack([rgb * A[..., None], A])
    small = cv2.resize(pre, (int(round((W + 2) * S)), int(round((H + PT + PB) * S))), interpolation=cv2.INTER_AREA)
    a = np.clip(small[..., 3:4], 1e-6, 1)
    c_ = np.where(small[..., 3:4] > 1e-4, small[..., :3] / a, 0)
    return np.clip(np.concatenate([c_, small[..., 3:4] * 255], -1), 0, 255).astype(np.uint8)


def items():
    """[(名前, svg か RGBA, 幅, 高さ)]（画面の px）"""
    from pack import ukiyoe as U
    out = []
    for k, p in enumerate(U.SW_ROWS):
        for v in range(len(U.SW_VAR)):
            w, h = U.sw_size(k, v)
            out.append((f'sw{k}{v}', small_wave(w, h, p['haze'], U.SW_PAD, seed=5 + 3 * k + v), w + 2, h + sum(U.SW_PAD)))
    out += [('bs0', U.burst_svg(11), 90, 70), ('bs1', U.burst_svg(12), 90, 70), ('pf0', U.puff_svg(51), 40, 26), ('pf1', U.puff_svg(53), 40, 26),
            ('sp1', U.spray_svg(41), 84, 44), ('sp2', U.spray_svg(43), 84, 44)]
    return out


def main(out=None):
    import ukiyoe_samurai as S
    its = items()
    S.Z = Z                                                       # お侍さんと 同じ 描き方で 3倍に
    svgs = [(i, svg, w, h) for i, (_, svg, w, h) in enumerate(its) if isinstance(svg, str)]
    shot = S.shot([(svg, w, h) for _, svg, w, h in svgs])
    ims = [svg if not isinstance(svg, str) else None for _, svg, _, _ in its]
    for (i, _, _, _), im in zip(svgs, shot):
        ims[i] = im
    # 行に つめる（はばが 600 を こえたら 次の 行）
    W = 600 * Z
    x = y = rowh = 0
    place = {}
    for (name, _, w, h), im in zip(its, ims):
        ih, iw = im.shape[:2]
        if x + iw > max(W, iw) and x > 0:
            x, y, rowh = 0, y + rowh + GAP, 0
        place[name] = (x, y, iw, ih)
        x += iw + GAP
        rowh = max(rowh, ih)
    SW = max(px + pw for px, _, pw, _ in place.values())
    SH = y + rowh
    sheet = np.zeros((SH, SW, 4), np.uint8)
    for (name, _, w, h), im in zip(its, ims):
        px, py, pw, ph = place[name]
        sheet[py:py + ph, px:px + pw] = im
    if out:
        os.makedirs(out, exist_ok=True)
        preview_png(sheet, os.path.join(out, 'uk_foam.png'), bg=(84, 112, 160))
    bid = save_webp(sheet, quality=86)
    meta = dict(z=Z, sheet=[SW, SH], parts={k: [v[0], v[1], v[2], v[3]] for k, v in place.items()})
    record('ukiyoe', 'foam', bid, meta)
    print('foam', bid, meta, flush=True)


if __name__ == '__main__':
    main(os.environ.get('OUT'))
