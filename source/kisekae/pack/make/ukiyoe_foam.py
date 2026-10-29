"""浮世絵風の 壁紙（壁紙パック）の 小波と しぶきを 絵（WebP）に する。
   第4.100版 まさちゃん「赤四角の小波は、大波と同じ絵の質感にして！あと小波の形は3枚目と同じ感じにして！」「三枚目の赤線の小波のように！」：
     小波（small_wave）は まさちゃんの 赤い 線の 形（左の 海の 線から 低く 長く もり上がり、波の 先が 右へ まいて 少し はね上がり、
     その 下から 長い すそが 右へ 海の 線まで おりる・中に もう 1本の 線）を そのまま 使い（左右に うら返さない）、大波と 同じ 描き方で ぬる：
     浮世絵の 平らな 4色（白・明るい 青・藍・濃い 藍）・濃い 藍の ふちの 線・上の ふちに そった 明るい 青 → 藍 → 濃い 藍の 帯・白い すじ・
     波の 先に 白い 泡の かさと 爪（指の ような 泡が 濃い 藍の ふちで 下へ まく）。numpy で 大きく 描いて 3倍に する（iPhone でも ふちが くっきり）。
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
TIP = [(.672, .6), (.684, .625)]                       # 波の 先（右へ 少し はね上がる）
HOOK = [(.694, .62), (.702, .60), (.703, .577), (.696, .556), (.690, .566), (.689, .583), (.682, .593)]   # 波の 先の 爪（白い 泡が 下へ まいて 先が とがる）
UNDER_TIP = [(.677, .56), (.668, .51)]                 # 先の 下へ もどる
TAIL = [(.68, .46), (.698, .40), (.717, .35), (.736, .30), (.755, .265), (.774, .23), (.792, .19), (.811, .15), (.83, .12), (.849, .09),
        (.868, .07), (.887, .055), (.906, .048), (.925, .04), (.943, .035), (1.0, .03)]
LIP = [(.47, .955), (.491, .91), (.509, .86), (.528, .81), (.547, .745), (.566, .70), (.585, .66), (.604, .63), (.625, .605), (.645, .59), (.668, .58)]   # 泡の かさの 下の ふち
INNER = [(.321, .29), (.34, .37), (.358, .42), (.377, .46), (.396, .48), (.415, .49), (.453, .49), (.472, .47), (.491, .41), (.509, .35),
         (.528, .29), (.547, .26), (.566, .245), (.604, .24), (.642, .24), (.66, .26)]                                          # 中の 線（白い すじ）
STREAKS = [[(.2, .2), (.24, .33), (.28, .43), (.32, .52), (.36, .58), (.4, .62)], [(.70, .22), (.74, .17), (.79, .12), (.84, .085)]]   # 明るい 青の すじ
CLAWS = [[(.626, .600), (.635, .586), (.638, .566), (.633, .550), (.629, .561), (.628, .578), (.621, .588)]]   # 泡の かさの 下の 小さな 爪（先が とがる）
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


def small_wave(W, H, haze=0.0, pad=(2, 3), S=Z, SS=6):
    """はば W・高さ H（画面の px）の 小波 1つ → RGBA u8（S 倍の 画素）。左右に 1px・上に pad[0]・下に pad[1] の よゆう（根もとは 上から pad[0]＋H）"""
    K = S * SS
    PT, PB = pad
    Wp, Hp = int(round((W + 2) * K)), int(round((H + PT + PB) * K))
    base = (H + PT) * K
    lw = .055 * H                                                       # ふちの 線の 太さ（高さ 16px で 0.9px：大波の 線と 同じ くらい）

    def col(name):
        c = np.array(PAL[name], np.float32)
        return tuple(float(x) for x in (c + (np.array(PAPER, np.float32) - c) * haze * (.3 if name == 'white' else .7)))

    def m(pts):
        P = np.array(pts, np.float64)
        return np.stack([(1 + P[:, 0] * W) * K, base - P[:, 1] * H * K], 1)

    def sh(pts):
        return np.round(pts * 4).astype(np.int32)
    top, under = np.vstack([m(cr(OUTER + TIP)), m(cr(HOOK, 4))]), m(cr(UNDER_TIP + TAIL))
    sil = np.vstack([top, under, [[(1 + W) * K, base + PB * K], [K, base + PB * K]]])
    mask = np.zeros((Hp, Wp), np.uint8)
    cv2.fillPoly(mask, [sh(sil)], 255, lineType=cv2.LINE_AA, shift=2)
    A = mask.astype(np.float32) / 255
    # 帯：上の ふちからの 距離（明るい 青 → 藍 → 濃い 藍：大波の 体と 同じ 色の 帯）
    lm = np.full((Hp, Wp), 255, np.uint8)
    cv2.polylines(lm, [sh(top), sh(under)], False, 0, 1, cv2.LINE_8, shift=2)
    dist = cv2.distanceTransform(lm, cv2.DIST_L2, 5) / (H * K)
    rgb = np.zeros((Hp, Wp, 3), np.float32)
    rgb[:] = col('dark')
    rgb[dist < .58] = col('mid')
    rgb[dist < .17] = col('light')

    def line(pts, c, w):
        cv2.polylines(rgb, [sh(m(cr(pts)))], False, c, max(1, int(round(w * K))), cv2.LINE_AA, shift=2)
    for st in STREAKS:
        line(st, col('light'), .028 * H)
    line(INNER, col('white'), .038 * H)
    # 泡の かさ（白）：上の ふち と LIP の あいだ
    cap = np.vstack([m(cr([p for p in OUTER if p[0] >= .43] + TIP)), m(cr(HOOK, 4)), m(cr(LIP))[::-1]])
    cm = np.zeros((Hp, Wp), np.uint8)
    cv2.fillPoly(cm, [sh(cap)], 255, lineType=cv2.LINE_AA, shift=2)
    ca = (cm.astype(np.float32) / 255)[..., None]
    rgb = rgb * (1 - ca) + np.array(col('white'), np.float32) * ca
    line(LIP, col('dark'), .028 * H)
    # 外の ふち（濃い 藍の 線）
    cv2.polylines(rgb, [sh(top)], False, col('dark'), int(round(lw * K)), cv2.LINE_AA, shift=2)
    cv2.polylines(rgb, [sh(under)], False, col('dark'), int(round(lw * .9 * K)), cv2.LINE_AA, shift=2)
    # 小さな 爪（白い 指の ような 泡が 濃い 藍の ふちで 下へ まく・先が とがる：大波の 爪と 同じ）
    for cl in CLAWS:
        P = m(cr(cl, 4))
        cv2.fillPoly(rgb, [sh(P)], col('white'), cv2.LINE_AA, shift=2)
        cv2.polylines(rgb, [sh(P)], True, col('dark'), max(1, int(round(.024 * H * K))), cv2.LINE_AA, shift=2)
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
            out.append((f'sw{k}{v}', small_wave(w, h, p['haze'], U.SW_PAD), w + 2, h + sum(U.SW_PAD)))
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
