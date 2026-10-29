"""浮世絵風の 壁紙（壁紙パック）の 小波と しぶきを 絵（WebP）に する。
   第4.100版 まさちゃん「赤四角の小波は、大波と同じ絵の質感にして！あと小波の形は3枚目と同じ感じにして！」「三枚目の赤線の小波のように！」：
     小波の 形は まさちゃんの 赤い 線（左の 海の 線から 低く 長く もり上がり、波の 先が 右へ まいて、長い すそが 右へ 海の 線まで おりる）。
   第4.101版 まさちゃん（書きこみ）「小波この真ん中の第4に書き足した赤線に合わせて作成して！あともっと大波によせた絵にして！」：
     上の ふち ぜんぶに 白い 泡の 帯・中の 白い 線・先の かぎ なし。
   第4.102版 まさちゃん「小波の形を全て統一せずに、バラバラにして！」「小波の絵は一枚目の赤丸みたいにして！」（赤丸＝大波の 上の 所：
     白い 背中に 藍の 巻いた 泡の 爪）：
     ① 絵は 大波（make/ukiyoe_great.py：神奈川沖浪裏の 切りぬき・まるい 爪・ぼかし）の 模様 そのもの を 小波の 形に 写す（同じ 絵の 質感）：
        小波の 上の ふち（左の 根もと → 波の 先）には 大波の 上の ふち（白い 背中 → 頭の 巻いた 泡の 爪）を、
        小波の すそ（波の 先の 下 → 右の 根もと）には 大波の 前の 面（濃い 藍に 白い すじ）を、ふちに そって 写す（C_TOP・C_FACE）。
        どちらも ふちからの 深さ ごとに 大波の 中へ 入って いく（法線は たて向きに よせて 頭の 下で 交わらない）。
        小波は 大波の 模様の 0.6倍 くらいの 大きさ（K_PX）＝ 大波の 小さな かけら。根もとは 海の 藍へ ぼかす。ふちは 濃い 藍の 線。
        左右に うら返さない（波の 先は いつも 右）・先の かぎ なし・白い 丸 なし（大波の 模様の まま）。
     ② 形は 7つ（pack/ukiyoe.py の SW_SHAPES：長さ・高さ・頭の 場所・どれだけ 右へ まくか・すその 長さ・頭が 2つ の もの）。
        小波 1つずつ 形・大きさ・大波の どこを 写すか（SW_WAVES の k・a_back・face0）が ちがう＝となりどうしは 同じ 形に しない。
   しぶき（波の 先が 落ちた 所で ふき上がる しぶき 2つ・小波の 頭の しぶき 2つ・大波の 頭から 吹き飛ぶ しぶき 2つ）は pack/ukiyoe.py の SVG を
   ブラウザ（Chromium）で 3倍に 描く。ぜんぶ 1まいの シートに ならべる（ページでは 部品の 背景に して background-position で えらぶ）
   python3 kisekae/pack/make/ukiyoe_foam.py 画像.jpg [OUT] → ios/kisekae_blobs/<id>.webp・kisekae/pack/blobs.json の ukiyoe.foam
   （画像＝大波と 同じ 神奈川沖浪裏の 画像：リポジトリには 入れない）"""
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
PAL = dict(white=(246, 241, 227), light=(178, 199, 222), mid=(84, 112, 160), dark=(27, 37, 92))       # 大波と 同じ 色（make/ukiyoe_great.py の PAL）
PAPER = (241, 230, 207)
TOP_X = (90, 576)            # 大波の 上の ふち（列ごとの いちばん 上）を とる 横の はんい（元の 画素）：背中 → 頭の 巻いた 泡の 爪
# 大波の 前の 面（頭の 下 → 濃い 藍の 体の 右の ふち を 下へ：内がわは 左）（元の 画素）
FACE_PTS = [(574, 92), (566, 150), (548, 205), (520, 232), (492, 252), (476, 272), (468, 300), (463, 330), (464, 360), (470, 385), (480, 405), (492, 425)]
D_OFF = 5.0                  # ふちから この 深さ（元の 画素）より 中を 写す（大波の ふちの でこぼこを 小波の ふちに 出さない：ふちの 線は 小波の 形で 引く）

SRC = None                   # 大波の 絵（前もって アルファを かけた RGBA・元の 画素）と 道


def _ss(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def _resample(pts, sm=0.0):
    P = np.array(pts, np.float64)
    if sm > 0:
        P = np.stack([cv2.GaussianBlur(P[:, 0].reshape(1, -1), (0, 0), sm).ravel(), cv2.GaussianBlur(P[:, 1].reshape(1, -1), (0, 0), sm).ravel()], 1)
    seg = np.hypot(*np.diff(P, axis=0).T)
    arc = np.concatenate([[0], np.cumsum(seg)])
    A = np.arange(0, arc[-1], 1.0)
    X = np.interp(A, arc, P[:, 0])
    Y = np.interp(A, arc, P[:, 1])
    TX, TY = np.gradient(X), np.gradient(Y)
    nn = np.hypot(TX, TY) + 1e-9
    return A, X, Y, TX / nn, TY / nn


class Path:
    """大波の 中の 道（ふち）：長さ a・内がわへの 法線（進む 向きの 右がわ・vert で たて／横 向きに よせる）"""
    def __init__(self, pre, pts, sm, nsm, vert, vdir):
        self.pre = pre
        self.A, self.X, self.Y, tx, ty = _resample(pts, sm)
        nx, ny = -ty, tx
        nx = cv2.GaussianBlur(nx.reshape(1, -1), (0, 0), nsm).ravel()
        ny = cv2.GaussianBlur(ny.reshape(1, -1), (0, 0), nsm).ravel()
        nn = np.hypot(nx, ny) + 1e-9
        nx, ny = nx / nn * (1 - vert) + vert * vdir[0], ny / nn * (1 - vert) + vert * vdir[1]
        nn = np.hypot(nx, ny) + 1e-9
        self.NX, self.NY = nx / nn, ny / nn
        self.L = float(self.A[-1])

    def sample(self, a, dep):
        a = np.clip(a, 0, self.L - 1)
        cx, cy = np.interp(a, self.A, self.X), np.interp(a, self.A, self.Y)
        nx, ny = np.interp(a, self.A, self.NX), np.interp(a, self.A, self.NY)
        return cv2.remap(self.pre, (cx + nx * dep).astype(np.float32), (cy + ny * dep).astype(np.float32), cv2.INTER_LINEAR,
                         borderMode=cv2.BORDER_CONSTANT, borderValue=0)


def load_src(src):
    """大波と 同じ 絵（extract → まるい 爪 → ぼかし）から 小波の 模様の もと（上の ふち・前の 面の 道）を 作る"""
    global SRC
    import ukiyoe_great as G
    rgb, bm, _ = G.extract(src)
    rgb, bm = G.roundify(rgb, bm)
    rgb = G.shade(rgb, bm)
    pre = np.dstack([rgb * bm[..., None], bm]).astype(np.float32)
    n, cc, st, _ = cv2.connectedComponentsWithStats((bm > .5).astype(np.uint8), 8)
    body = cc == (np.argmax(st[1:, cv2.CC_STAT_AREA]) + 1)
    xs = np.arange(*TOP_X)
    yt = np.array([np.nonzero(body[:, x])[0][0] for x in xs], np.float64)
    SRC = dict(top=Path(pre, np.stack([xs, yt], 1), 6.0, 14.0, .7, (0.0, 1.0)),
               face=Path(pre, FACE_PTS, 3.0, 10.0, .5, (-1.0, 0.0)))
    return SRC


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


def _proj(P, X, Y):
    """折れ線 P の いちばん 近い 点 → (道の 長さ, 距離)・道の 長さ ぜんぶ"""
    from scipy.spatial import cKDTree
    seg = np.hypot(*np.diff(P, axis=0).T)
    arc = np.concatenate([[0], np.cumsum(seg)])
    tot = arc[-1]
    a = np.linspace(0, tot, max(2, int(tot * 2)))
    px, py = np.interp(a, arc, P[:, 0]), np.interp(a, arc, P[:, 1])
    dd, ii = cKDTree(np.stack([px, py], 1)).query(np.stack([X.ravel(), Y.ravel()], 1))
    return a[ii].reshape(X.shape), dd.reshape(X.shape), tot


def small_wave(shape, W, H, haze=0.0, pad=(2, 3), k=4.8, a_back=0.0, face0=0.0, S=Z, SS=4):
    """形 shape（top：左の 根もと → 波の 先・tail：波の 先 → 先の 下 → すそ → 右の 根もと：0〜1）の はば W・高さ H（画面の px）の 小波 → RGBA u8（S 倍の 画素）。
       左右に 1px・上に pad[0]・下に pad[1] の よゆう（根もとは 上から pad[0]＋H）。
       k：画面 1px に 写す 大波の 元の 画素（大波の 模様の 大きさ 3/k 倍）・a_back：波の 先に あてる 大波の 上の ふちの 場所（頭の 先から もどる 元の 画素）・
       face0：すそに 写す 大波の 前の 面の はじめの 場所"""
    K = S * SS
    PT, PB = pad
    Wp, Hp = int(round((W + 2) * K)), int(round((H + PT + PB) * K))
    base = (H + PT) * K

    def m(pts):
        P = np.array(pts, np.float64)
        return np.stack([(1 + P[:, 0] * W) * K, base - P[:, 1] * H * K], 1)

    def sh(pts):
        return np.round(pts * 4).astype(np.int32)
    T, L = m(cr(shape['top'], 12)), m(cr(shape['tail'], 12))
    sil = np.vstack([T, L, [[(1 + W) * K, base + PB * K], [K, base + PB * K]]])
    mask = np.zeros((Hp, Wp), np.uint8)
    cv2.fillPoly(mask, [sh(sil)], 255, lineType=cv2.LINE_AA, shift=2)
    A = mask.astype(np.float32) / 255
    yy, xx = np.mgrid[0:Hp, 0:Wp].astype(np.float64)
    s1, d1, t1 = _proj(T, xx, yy)
    s2, d2, t2 = _proj(L, xx, yy)
    top, face = SRC['top'], SRC['face']
    a_end = top.L - 2 - a_back
    k = min(k, (a_end - 4) / (t1 / K))                          # 写す 所が 大波の 背中の はしを こえない
    px = k / K                                                  # 高い 画素 1つ → 元の 画素
    pf_ = min(px, (face.L - 4 - face0) / t2)                    # すそも 大波の 前の 面の はしを こえない（こえると すじが のびる）
    dark, mid = np.array(PAL['dark'], np.float32), np.array(PAL['mid'], np.float32)
    tp = top.sample(a_end - (t1 - s1) * px, D_OFF + d1 * px)
    fc = face.sample(face0 + s2 * pf_, D_OFF + d2 * px)
    tc = tp[..., :3] + (1 - tp[..., 3:4]) * dark                # 大波の 外に 出た 所は 濃い 藍
    fcc = fc[..., :3] + (1 - fc[..., 3:4]) * dark
    w2 = _ss(-.12 * H * K, .12 * H * K, d1 - d2)[..., None]       # すそに 近い 所は 前の 面の 模様
    rgb = tc * (1 - w2) + fcc * w2
    v = (base - yy) / (H * K)                                   # 海の 線からの 高さ（0〜1）
    rgb = rgb + (mid - rgb) * ((1 - _ss(0, .45, v)) * .55)[..., None]          # 根もとは 海の 藍へ ぼかす
    lw = max(1, int(round(.055 * H * K)))                       # ふちの 線（大波の 線と 同じ くらい）
    cv2.polylines(rgb, [sh(T)], False, PAL['dark'], lw, cv2.LINE_AA, shift=2)
    cv2.polylines(rgb, [sh(L[:int(len(L) * .55)])], False, PAL['dark'], max(1, int(lw * .85)), cv2.LINE_AA, shift=2)
    if haze:                                                    # おくの 列は かすむ
        rgb = rgb + (np.array(PAPER, np.float32) - rgb) * haze * .45
    pre = np.dstack([rgb * A[..., None], A]).astype(np.float32)
    small = cv2.resize(pre, (int(round((W + 2) * S)), int(round((H + PT + PB) * S))), interpolation=cv2.INTER_AREA)
    a = np.clip(small[..., 3:4], 1e-6, 1)
    c_ = np.where(small[..., 3:4] > 1e-4, small[..., :3] / a, 0)
    return np.clip(np.concatenate([c_, small[..., 3:4] * 255], -1), 0, 255).astype(np.uint8)


def items():
    """[(名前, svg か RGBA, 幅, 高さ)]（画面の px）"""
    from pack import ukiyoe as U
    out = []
    for k, (p, waves) in enumerate(zip(U.SW_ROWS, U.SW_WAVES)):
        for i, w in enumerate(waves):
            W_, H_ = w['W'], w['H']
            out.append((f'ukW{k}{i}', small_wave(U.SW_SHAPES[w['shape']], W_, H_, p['haze'], U.SW_PAD, w['k'], w['a_back'], w['face0']),
                        W_ + 2, H_ + sum(U.SW_PAD)))
    out += [('bs0', U.burst_svg(11), 90, 70), ('bs1', U.burst_svg(12), 90, 70), ('pf0', U.puff_svg(51), 40, 26), ('pf1', U.puff_svg(53), 40, 26),
            ('sp1', U.spray_svg(41), 84, 44), ('sp2', U.spray_svg(43), 84, 44)]
    return out


def main(src, out=None):
    import ukiyoe_samurai as S
    load_src(src)
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
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    if not a:
        sys.exit('python3 kisekae/pack/make/ukiyoe_foam.py 画像.jpg [OUT]（大波と 同じ 神奈川沖浪裏の 画像）')
    main(a[0], a[1] if len(a) > 1 else os.environ.get('OUT'))
