"""浮世絵風の 壁紙（壁紙パック・第4.95版 → 第4.96版）の 大波を 絵（WebP）に する。
   第4.95版 まさちゃん「波だけ七枚目の画像と形を全く同じにして！」：七枚目＝葛飾北斎「神奈川沖浪裏」（1831年ごろ・パブリックドメイン）の 画像から
   左の 大波（白い 背中・爪の 泡・濃い 藍の 体と 白い すじ・内がわの 明るい 青・爪から 落ちる しぶきの 点）を 切りぬいて、
   浮世絵の 平らな 色（白・明るい 青・藍・濃い 藍）に まとめる（ポスタライズ）。空・題箋・落款・画面の アイコンは すける ように、
   波の 中の 舟と 人・富士山は 入れない（舟の 所は まわりの 波の 色で うめる）。
   第4.96版 まさちゃん「浮世絵の赤丸の波はもっと動きを出してリアルにして！波飛沫とか波の高さが変わったりとか！
     リアルな波の映像から波ができてから消えていく動きを勉強して、浮世絵に転用して！」：
     いちばん 高い 時の 形は 神奈川沖浪裏の まま。波の 先（爪の ある 頭）を「巻きの 強さ c」で なめらかに ゆがめた コマ（crest）を 作る：
       c＝−1：まだ 巻いて いない（頭が うしろへ 起きて 爪が 短い＝もり上がる とちゅう）→ c＝0：神奈川沖浪裏 そのまま →
       c＝1：波の 先が 前へ 投げ出されて 爪が のびて 下へ 巻きこむ → c＝1.6：くずれて 落ちる。
     ゆがめ方：さかいめ（SPLIT）から 波の 先へ いくほど 強く、根もと PIVOT の まわりに 回して（θ）・外へ のばして（ε）・下へ 落とす（drop）。
       さかいめと 下の はしでは ゆがみが 0（なめらかに 0 から）＝体（body）と つなぎめが ずれない・すき間も 二重も 出ない。
     体（body）は 動く 所（頭）を ぬいた 止まった 絵。頭の コマを 上に 重ねる（動きは pack/ukiyoe.py の CSS）。
   しくみ：空を 色の つながりで ぬりつぶして（黒い 線で 止まる）波を とりだす → 明るさで 4つの 色に 分ける（細い 黒い 線は 濃い 藍）→
     絵 2まい：wave＝[body・dots（爪から 落ちる しぶきの 点）]（2倍の 画素の 横ならび）・crest＝頭の コマ（CS の c の じゅん・8れつの ます目）
   python3 kisekae/pack/make/ukiyoe_great.py 画像.jpg [OUT] [--save] → ios/kisekae_blobs/<id>.webp・kisekae/pack/blobs.json の ukiyoe.wave・ukiyoe.crest"""
import math
import os
import sys
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))          # kisekae
import numpy as np  # noqa: E402
import cv2  # noqa: E402

# 元の 画像（1169×887）の 中の 切りぬく 箱と 画面の 大きさ
CROP = (0, 90, 780, 525)            # 左・上・はば・高さ（元の 画素）
SC = 1 / 3                          # 元の 画素 → 画面の px
Z = 2                               # シートは 画面の 2倍
PIVOT = (480, 330)                  # 波の 先（頭）を 回す 中心（元の 画素）
SPLIT = [(318, 118), (420, 232), (480, 330), (522, 425), (560, 520)]    # 体と 頭の さかいめ（左上 → 右下・右がわが 頭）
D_IN = 150.0                        # さかいめから この 距離（元の 画素）で ゆがみが いっぱいに なる
Y_STOP = (390.0, 520.0)             # この 高さ（元の 画素）より 下は ゆがめない（波の 根もと）
BAND = 18.0                         # 頭の コマの ふちの ぼかし（元の 画素：ゆがみ 0 の 所で 体と 重ねる）
PAL = dict(white=(246, 241, 227), light=(178, 199, 222), mid=(84, 112, 160), dark=(27, 37, 92))    # 浮世絵の 平らな 色
SKY_SEEDS = [(600, 40), (950, 100), (800, 180), (600, 450), (620, 540), (900, 450), (150, 120), (20, 150), (1100, 300), (700, 300), (700, 520)]
COLS = 8                            # 頭の コマの ます目の れつ

# 頭の コマの 巻きの 強さ c（pack/ukiyoe.py が 時に 当てる：c<0 もり上がる・0 神奈川沖浪裏・0<c≦1 投げ出す・c>1 くずれる）
CS = ([round(-1 + i / 20, 4) for i in range(20)] + [0.0]
      + [round(i / 18, 4) for i in range(1, 19)] + [round(1 + 0.6 * i / 16, 4) for i in range(1, 17)])


def warp_params(c):
    """c → (回す 角度 θ°・外へ のばす ε・下へ 落とす 元の 画素)"""
    if c <= 0:
        return 15.0 * c, 0.10 * c, 0.0
    if c <= 1:
        return 16.0 * c, 0.12 * c, 0.0
    u = (c - 1) / 0.6
    return 16.0 + 12.0 * u, 0.12 - 0.06 * u, 36.0 * u


def sky_mask(den):
    """空：種の 点から 色が なめらかに つながる 所を ぬりつぶす（藍・黒い 線で 止まる）"""
    h, w = den.shape[:2]
    R, B = den[..., 0], den[..., 2]
    L = den @ np.array([.3, .59, .11], np.float32)
    block = ((B - R) > 16) | (L < 95)
    sky = np.zeros((h, w), bool)
    q = deque()
    for x, y in SKY_SEEDS:
        if not block[y, x]:
            sky[y, x] = True
            q.append((x, y))
    while q:
        x, y = q.popleft()
        c = den[y, x]
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and not sky[ny, nx] and not block[ny, nx] and np.abs(den[ny, nx] - c).max() < 9.0:
                sky[ny, nx] = True
                q.append((nx, ny))
    # 水平線の 近くの 暗い 灰色の 空（ぬりつぶしが 止まる）：藍でも 白でも ない 所は 空
    yy, xx = np.mgrid[0:h, 0:w]
    low = (xx > 470) & (yy > 530)
    gray = ((B - R) < 10) & (L < 200)
    sky |= low & gray
    return sky


def classify(den):
    """4つの 色の 番号（0 白・1 明るい 青・2 藍・3 濃い 藍）：明るさ と 細い 黒い 線（black-hat）"""
    L = den @ np.array([.3, .59, .11], np.float32)
    bh = cv2.morphologyEx(L, cv2.MORPH_BLACKHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
    lab = np.full(L.shape, 2, np.uint8)
    lab[L >= 132] = 1
    lab[L >= 203] = 0
    lab[(L < 52) | ((bh > 42) & (L < 150))] = 3
    return lab


def mode_filter(lab, mask, k=3, iters=1):
    """まわりで いちばん 多い 色に（JPEG の ちらばりを けす）"""
    for _ in range(iters):
        votes = []
        for c in range(4):
            m = ((lab == c) & mask).astype(np.float32)
            votes.append(cv2.boxFilter(m, -1, (k, k), normalize=False))
        v = np.stack(votes, -1)
        best = v.argmax(-1).astype(np.uint8)
        strong = v.max(-1) >= (k * k) // 2 + 1
        lab = np.where(mask & strong, best, lab)
    return lab


def boat_poly():
    """左の 舟（へさき → ふなべり → とも・人）：まわりの 波の 色で うめる"""
    return np.array([(14, 422), (36, 424), (88, 492), (142, 530), (246, 584), (296, 598), (298, 662), (136, 664), (92, 578), (58, 510)], np.int32)


def signed_dist(xx, yy):
    """さかいめ（SPLIT の 折れ線）からの 符号つき 距離（＋が 頭の がわ＝線の 右）。上の はしより 上で 右は 頭"""
    pts = np.array(SPLIT, np.float32)
    best = np.full(xx.shape, 1e9, np.float32)
    sign = np.zeros(xx.shape, np.float32)
    for (x1, y1), (x2, y2) in zip(pts[:-1], pts[1:]):
        dx, dy = x2 - x1, y2 - y1
        L2 = dx * dx + dy * dy
        t = np.clip(((xx - x1) * dx + (yy - y1) * dy) / L2, 0, 1)
        px, py = x1 + t * dx, y1 + t * dy
        d = np.hypot(xx - px, yy - py)
        cr = dx * (yy - y1) - dy * (xx - x1)          # 線の 右（画面で 下が ＋y）が 負
        s = np.where(cr < 0, 1.0, -1.0)
        upd = d < best
        best = np.where(upd, d, best)
        sign = np.where(upd, s, sign)
    sd = best * sign
    top_ext = (yy < SPLIT[0][1]) & (xx > SPLIT[0][0])
    return np.where(top_ext, np.abs(best), sd)


def _ss(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def weight(xx, yy):
    """ゆがみの 強さ（0〜1）：さかいめで 0・頭の 先ほど 1・根もとの 下では 0（どこも なめらか）"""
    return _ss(0, D_IN, signed_dist(xx, yy)) * (1 - _ss(Y_STOP[0], Y_STOP[1], yy))


def inverse_map(c, h, w, ox, oy, iters=7):
    """出口の 画素 → もとの 画素（元の 画像の 座標）：前へ 写す 式を くり返しで 逆に 解く"""
    th, ep, drop = warp_params(c)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    xx += ox
    yy += oy
    qx, qy = xx - PIVOT[0], yy - PIVOT[1]
    px, py = xx.copy(), yy.copy()
    for _ in range(iters):
        s = weight(px, py)
        ph = -math.radians(th) * s
        k = 1.0 / (1 + ep * s)
        cs, sn = np.cos(ph), np.sin(ph)
        ry = qy - drop * s
        px = PIVOT[0] + k * (cs * qx - sn * ry)
        py = PIVOT[1] + k * (sn * qx + cs * ry)
    return px - ox, py - oy


def extract(src):
    """元の 画像 → (色 RGB, 波の アルファ, しぶきの 点の アルファ)：元の 画素・CROP の 箱"""
    im = cv2.imread(src)[:, :, ::-1].astype(np.float32)
    H0, W0 = im.shape[:2]
    den = cv2.bilateralFilter(im, 5, 20, 3)
    sky = sky_mask(den)
    wave = ~sky
    yy, xx = np.mgrid[0:H0, 0:W0]
    cx, cy, cw, ch = CROP
    wave &= (xx >= cx) & (xx < cx + cw) & (yy >= cy) & (yy < cy + ch)
    wave &= ~((xx >= 690) & (yy >= 560))                              # 富士山・右の 舟
    wave &= ~((xx < 108) & (yy < 300) & (yy > 70) & (xx > 44))        # 題箋（字の 札）
    wave &= ~((xx < 50) & (yy < 312) & (yy > 150))                    # 落款（サイン）
    # つながりで 分ける：いちばん 大きい かたまり＝波・小さな しま＝しぶきの 点（空の 所）
    n, cc, st, _ = cv2.connectedComponentsWithStats(wave.astype(np.uint8), 8)
    main = np.argmax(st[1:, cv2.CC_STAT_AREA]) + 1
    body_m = cc == main
    dots_m = np.zeros_like(body_m)
    for i in range(1, n):
        if i == main:
            continue
        a = st[i, cv2.CC_STAT_AREA]
        x_, y_ = st[i, cv2.CC_STAT_LEFT], st[i, cv2.CC_STAT_TOP]
        comp = cc == i
        bw_, bh_ = st[i, cv2.CC_STAT_WIDTH], st[i, cv2.CC_STAT_HEIGHT]
        mx, my = x_ + bw_ / 2, y_ + bh_ / 2
        spray = mx > 470 and my > 300 and a < 600                    # 爪の 下の しぶきの 点（大きい つぶも）
        if spray and a >= 3:
            dots_m |= comp
        elif a >= 40 or (a >= 3 and my < 420 and mx > 300):          # 爪の 先の かけら・爪の あいだの 小さな 泡は 波
            body_m |= comp
    lab = classify(den)
    # 舟：まわりの 色を おしひろげて うめる（いちばん 近い 波の 色）
    boat = np.zeros((H0, W0), np.uint8)
    cv2.fillPoly(boat, [boat_poly()], 1)
    boat = boat.astype(bool) & body_m
    known = body_m & ~boat
    _, idx = cv2.distanceTransformWithLabels((~known).astype(np.uint8), cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    ky, kx = np.nonzero(known)
    lut = np.zeros(idx.max() + 1, np.uint8)
    lut[idx[ky, kx]] = lab[ky, kx]
    lab = np.where(boat, lut[idx], lab)
    lab = mode_filter(lab, body_m, 3, 2)
    lab = np.where(dots_m, 0, lab)                                     # しぶきの 点は 白
    pal = np.array([PAL['white'], PAL['light'], PAL['mid'], PAL['dark']], np.float32)
    rgb = pal[lab]
    sl = (slice(cy, cy + ch), slice(cx, cx + cw))
    return rgb[sl], body_m[sl].astype(np.float32), dots_m[sl].astype(np.float32)


def down(pre, w2, h2):
    """前もって アルファを かけた 色（元の 画素）→ 2倍の 画素の RGBA u8（ふちが なめらか）"""
    sm = cv2.resize(pre, (w2, h2), interpolation=cv2.INTER_AREA)
    al = np.clip(sm[..., 3:4], 1e-6, 1)
    col = np.where(sm[..., 3:4] > 1e-4, sm[..., :3] / al, 0)
    return np.clip(np.concatenate([col, sm[..., 3:4] * 255.0], -1), 0, 255).astype(np.uint8)


def build(src, out=None):
    rgb, bm, dm = extract(src)
    h, w = bm.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    ox, oy = CROP[0], CROP[1]
    X, Y = xx + ox, yy + oy                                            # 元の 画像の 座標
    s0 = weight(X, Y)
    moving = s0 > 0                                                    # 動く 所（頭）：体から ぬく
    sd = signed_dist(X, Y)
    af = _ss(-BAND, 0, sd) * (1 - _ss(Y_STOP[1], Y_STOP[1] + BAND, Y))   # 頭の コマの アルファ（ゆがみ 0 の ふちで 体と 重なる）
    W2, H2 = int(round(w * SC * Z)), int(round(h * SC * Z))
    body = down(np.dstack([rgb * (bm * ~moving)[..., None], bm * ~moving]), W2, H2)
    dots = down(np.dstack([rgb * dm[..., None], dm]), W2, H2)
    pre = np.dstack([rgb * (bm * af)[..., None], bm * af]).astype(np.float32)
    frames = []
    for c in CS:
        mx, my = inverse_map(c, h, w, ox, oy)
        frames.append(cv2.remap(pre, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0))
    # 頭の コマの 箱：どの コマでも 見える 所を ぜんぶ ふくむ（2倍の 画素の きりの よい 所へ）
    al = np.max([f[..., 3] for f in frames], 0) > 1e-3
    ys, xs = np.nonzero(al)
    k = 3                                                              # 元の 画素 → 2倍の 画素 は 1.5 で わる：3の 倍数で 切る
    x0, y0 = (xs.min() // k) * k, (ys.min() // k) * k
    x1, y1 = min(w, -(-(xs.max() + 1) // k) * k), min(h, -(-(ys.max() + 1) // k) * k)
    fw, fh = int(round((x1 - x0) * SC * Z)), int(round((y1 - y0) * SC * Z))
    cells = [down(f[y0:y1, x0:x1], fw, fh) for f in frames]
    rows = -(-len(cells) // COLS)
    grid = np.zeros((rows * fh, COLS * fw, 4), np.uint8)
    for i, c_ in enumerate(cells):
        r, q = divmod(i, COLS)
        grid[r * fh:(r + 1) * fh, q * fw:(q + 1) * fw] = c_
    wave_sheet = np.concatenate([body, dots], 1)
    if out:
        os.makedirs(out, exist_ok=True)
        bg = (241, 230, 207)

        def flat(u8):
            a = u8[..., 3:4] / 255.0
            return (u8[..., :3] * a + np.array(bg, np.float32) * (1 - a))[..., ::-1].astype(np.uint8)
        cv2.imwrite(os.path.join(out, 'great_wave.png'), flat(wave_sheet))
        cv2.imwrite(os.path.join(out, 'great_crest.png'), flat(grid))
        for i in (0, 10, 20, 29, 38, 46, 54):                          # 体と 重ねた ためし
            comp = np.full((H2, W2, 3), bg, np.float32)
            for u8, (px_, py_) in ((body, (0, 0)), (cells[i], (int(round(x0 * SC * Z)), int(round(y0 * SC * Z))))):
                a = u8[..., 3:4] / 255.0
                sub = comp[py_:py_ + u8.shape[0], px_:px_ + u8.shape[1]]
                sub[:] = u8[..., :3] * a + sub * (1 - a)
            cv2.imwrite(os.path.join(out, f'great_c{i:02d}.png'), comp[..., ::-1].astype(np.uint8))
    meta_w = dict(cell=[W2, H2], size=[round(w * SC, 2), round(h * SC, 2)], frames=2, parts=['body', 'dots'])
    meta_c = dict(cell=[fw, fh], cols=COLS, rows=rows, cs=list(CS), at=[round(x0 * SC, 3), round(y0 * SC, 3)],
                  size=[round((x1 - x0) * SC, 3), round((y1 - y0) * SC, 3)])
    return wave_sheet, grid, meta_w, meta_c


def main(src, out=None, save=False):
    ws, grid, mw, mc = build(src, out)
    print('wave', ws.shape, mw, flush=True)
    print('crest', grid.shape, {k: v for k, v in mc.items() if k != 'cs'}, flush=True)
    if save:
        from sheets import save_webp, record
        bid = save_webp(ws, quality=90)
        record('ukiyoe', 'wave', bid, mw)
        cid = save_webp(grid, quality=82)
        record('ukiyoe', 'crest', cid, mc)
        print('wave', bid, 'crest', cid, flush=True)


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    main(a[0], a[1] if len(a) > 1 else os.environ.get('OUT'), '--save' in sys.argv)
