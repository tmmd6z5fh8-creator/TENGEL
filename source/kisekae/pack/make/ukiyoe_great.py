"""浮世絵風の 壁紙（壁紙パック・第4.95版）の 大波を 絵（WebP）に する。
   まさちゃんの 指定「波だけ七枚目の画像と形を全く同じにして！」：七枚目＝葛飾北斎「神奈川沖浪裏」（1831年ごろ・パブリックドメイン）の 画像から
   左の 大波（白い 背中・爪の 泡・濃い 藍の 体と 白い すじ・内がわの 明るい 青・爪から 落ちる しぶきの 点）を 切りぬいて、
   浮世絵の 平らな 色（白・明るい 青・藍・濃い 藍）に まとめる（ポスタライズ）。空・題箋・落款・画面の アイコンは すける ように、
   波の 中の 舟と 人・富士山は 入れない（舟の 所は まわりの 波の 色で うめる）。
   しくみ：空を 色の つながりで ぬりつぶして（黒い 線で 止まる）波を とりだす → 明るさで 4つの 色に 分ける（細い 黒い 線は 濃い 藍）→
     部品に 分ける（動きは pack/ukiyoe.py の CSS）：body（波の 体）・lip1〜lip4（波の 先と 爪を さかいめから の 距離で 4まいに：根もと PIVOT を 中心に
     先の まい ほど 大きく 回す＝波の 先が なめらかに しなって 巻きこむ・つなぎめは ぼかして 重ねる）・dots（爪から 落ちる しぶきの 点）。
     部品は 同じ 大きさの 箱で 横に ならべた 1まいの シート（2倍の 画素）
   python3 kisekae/pack/make/ukiyoe_great.py 画像.jpg [OUT] → ios/kisekae_blobs/<id>.webp・kisekae/pack/blobs.json の ukiyoe.wave"""
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
PIVOT = (480, 330)                  # 波の 先（lip）を 回す 中心（元の 画素）
SPLIT = [(318, 118), (420, 232), (480, 330), (522, 425), (560, 520)]    # body と lip の さかいめ（左上 → 右下・右がわが lip）
BAND = 13.0                         # さかいめの ぼかしの はば（片がわ・元の 画素）
LIP_EDGES = (0.0, 45.0, 95.0, 150.0)    # 波の 先を 4まいに 分ける さかいめ（SPLIT からの 距離）：先の まい ほど 大きく 回す＝なめらかに しなる
OVER = 26.0                         # となりの まいの 下へ のばす 重なり（回る 角度の ちがいで すき間が 出ない）
PAL = dict(white=(246, 241, 227), light=(178, 199, 222), mid=(84, 112, 160), dark=(27, 37, 92))    # 浮世絵の 平らな 色
SKY_SEEDS = [(600, 40), (950, 100), (800, 180), (600, 450), (620, 540), (900, 450), (150, 120), (20, 150), (1100, 300), (700, 300), (700, 520)]


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


def signed_dist_split(h, w):
    """さかいめ（SPLIT の 折れ線）からの 符号つき 距離（＋が lip の がわ＝線の 右）"""
    pts = np.array(SPLIT, np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    best = np.full((h, w), 1e9, np.float32)
    sign = np.zeros((h, w), np.float32)
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
    # 線の はしの 外がわ：上の はしより 上は lip（波の 頭）・下の はしより 下は body
    sd = best * sign
    top_ext = (yy < SPLIT[0][1]) & (xx > SPLIT[0][0])
    sd = np.where(top_ext, np.abs(best), sd)
    return sd


def build(src, out=None):
    im = cv2.imread(src)[:, :, ::-1].astype(np.float32)
    H0, W0 = im.shape[:2]
    den = cv2.bilateralFilter(im, 5, 20, 3)
    sky = sky_mask(den)
    wave = ~sky
    yy, xx = np.mgrid[0:H0, 0:W0]
    cx, cy, cw, ch = CROP
    inbox = (xx >= cx) & (xx < cx + cw) & (yy >= cy) & (yy < cy + ch)
    wave &= inbox
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
    # ラベル番号 → いちばん 近い 既知の 画素の 色
    lut = np.zeros(idx.max() + 1, np.uint8)
    lab_known = lab[ky, kx]
    lut[idx[ky, kx]] = lab_known
    lab = np.where(boat, lut[idx], lab)
    lab = mode_filter(lab, body_m, 3, 2)
    # しぶきの 点は 白
    lab = np.where(dots_m, 0, lab)
    # 色の 画像（RGBA・元の 画素）
    pal = np.array([PAL['white'], PAL['light'], PAL['mid'], PAL['dark']], np.float32)
    rgb = pal[lab]
    sd = signed_dist_split(H0, W0)
    alphas = [(sd <= LIP_EDGES[0] + BAND + OVER).astype(np.float32) * body_m]     # body：はじめの さかいめの 少し 先まで（上は lip で かくれる）
    for k, e in enumerate(LIP_EDGES):
        t = np.clip((sd - e + BAND) / (2 * BAND), 0, 1)
        a = t * t * (3 - 2 * t)                                       # さかいめで なめらかに 0 → 1
        if k + 1 < len(LIP_EDGES):
            a = a * (sd <= LIP_EDGES[k + 1] + BAND + OVER)            # つぎの まいの 下まで（その 先は つぎの まい）
        alphas.append(a.astype(np.float32) * body_m)
    alphas.append(dots_m.astype(np.float32))
    parts = []
    for a in alphas:
        rgba = np.dstack([rgb, a[..., None] * 255.0])[cy:cy + ch, cx:cx + cw]
        parts.append(rgba)
    # 画面の 2倍へ（色は アルファで 重みを つけて 縮める＝ふちが なめらか）
    W2, H2 = int(round(cw * SC * Z)), int(round(ch * SC * Z))
    cells = []
    for p in parts:
        a = p[..., 3:4] / 255.0
        pre = np.concatenate([p[..., :3] * a, a], -1)
        sm = cv2.resize(pre, (W2, H2), interpolation=cv2.INTER_AREA)
        al = np.clip(sm[..., 3:4], 1e-6, 1)
        col = np.where(sm[..., 3:4] > 1e-4, sm[..., :3] / al, 0)
        cells.append(np.clip(np.concatenate([col, sm[..., 3:4] * 255.0], -1), 0, 255).astype(np.uint8))
    sheet = np.concatenate(cells, 1)
    if out:
        os.makedirs(out, exist_ok=True)
        bg = np.full((H2, W2 * len(cells), 3), (241, 230, 207), np.float32)
        a = sheet[..., 3:4] / 255.0
        cv2.imwrite(os.path.join(out, 'great_sheet.png'), (sheet[..., :3] * a + bg * (1 - a))[..., ::-1].astype(np.uint8))
        comp = np.full((H2, W2, 3), (241, 230, 207), np.float32)
        for c in cells:
            a = c[..., 3:4] / 255.0
            comp = c[..., :3] * a + comp * (1 - a)
        cv2.imwrite(os.path.join(out, 'great_comp.png'), comp[..., ::-1].astype(np.uint8))
        dbg = im.copy()
        dbg[~(body_m | dots_m)] = dbg[~(body_m | dots_m)] * .3 + np.array([255, 0, 255]) * .7
        cv2.polylines(dbg, [np.array(SPLIT, np.int32)], False, (0, 255, 0), 2)
        cv2.circle(dbg, PIVOT, 5, (255, 0, 0), -1)
        cv2.imwrite(os.path.join(out, 'great_dbg.png'), dbg[..., ::-1].astype(np.uint8))
    return sheet, dict(cell=[W2, H2], size=[round(cw * SC, 2), round(ch * SC, 2)], frames=len(cells),
                       parts=['body'] + [f'lip{k + 1}' for k in range(len(LIP_EDGES))] + ['dots'],
                       pivot=[round((PIVOT[0] - cx) * SC, 2), round((PIVOT[1] - cy) * SC, 2)])


def main(src, out=None, save=False):
    sheet, meta = build(src, out)
    print('sheet', sheet.shape, meta, flush=True)
    if save:
        from sheets import save_webp, record
        bid = save_webp(sheet, quality=90)
        record('ukiyoe', 'wave', bid, meta)
        print('wave', bid, meta, flush=True)


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    main(a[0], a[1] if len(a) > 1 else os.environ.get('OUT'), '--save' in sys.argv)
