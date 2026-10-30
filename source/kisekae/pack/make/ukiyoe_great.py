"""浮世絵風の 壁紙（壁紙パック・第4.95版 → 第4.96版 → 第4.97版 → 第4.99版）の 大波を 絵（WebP）に する。
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
   第4.97版 まさちゃん「🌊自体をもう少し波の先や小波など丸い絵に変えて！」：泡の 爪を 少し まるく（roundify：細い 線の 先を まるい 筆に・
     泡の 色を 少し なめらかに・外の ふちを 少し ふとらせて 線を 引き直す。波の 体の 白い すじと 点は そのまま）。UK_SHARP=1 で とがった 爪（第4.96版）。
   第4.99版 まさちゃん「やっぱり二枚目のような波にして、リアルで立体的に波がでてきて、消えていく表現にして！」：第4.98版の かわいい 平らな 大波を やめて
     この 絵に もどし、浮世絵の ぼかし（bokashi）で 立体の かげを つける（shade：波の 体は 根もとへ いくほど 濃く・波の 先の 下の くぼみは さらに 濃く・
     白い 背中は 下の 左ほど 明るい 青へ。UK_FLAT=1 で ぼかし なし）。動き（3秒の 波の 一生・奥行き）は pack/ukiyoe.py の CSS。
   第4.100版 まさちゃん「波の先端だけ動くの変だから、波が出てきて、徐々に水平になっていくようにして！今だと今ある絵が伸び縮みしてて変だから、
     ちゃんと形を変えながらリアルに出てきたり、水平になっていったりして！」「大波は出てきてから水平になるまで、もっと早くして！」
     「大波の動作も止まったり鈍いとへんだからリアルに！」：絵を のばしたり ちぢめたり（scale）しない。波の 一生を 1まいずつ 描いた コマ（life）に する：
       海の 中から うしろへ ねた 波が 立ち上がり（うつす・回す・かたむける・頭の 巻き c −1→0）→ 神奈川沖浪裏（止まらずに すぎる）→
       波の 先を 投げ出して 前へ のりだし（c 0→1）→ 落ちる（c→1.6）→ 左の 根もとを 軸に 前へ たおれて 低く なり 水平に（海の 線の 下へ）。
       絵の 中身は いつも 同じ 大きさ（回す・うつす・高い 所ほど 前へ かたむける・頭の 巻き＝形が かわる）。24コマ／秒・1.9秒・海の 線（CSS 112）で 切る。
       コマごとに 中身の ある 四角だけ 切りぬいて 1まいの シートに つめる（pack/ukiyoe.py が step-end で 入れかえる）。爪の 下の しぶきの 点も コマの 中で とぶ。
   第4.101版 まさちゃん「あと大波は水平に近くにつれて横長になり、走ってる馬を超えて水平になった方が速度的にもリアルかも！」：
     くずれて 低く なる 間に 横長に のびて 右へ 走る（のばす ゆがみ D：左の 根もと（XS[0]）では 0・白い 背中の 上で ふえて 頭（XS[1]）より 右は
     そのまま D だけ 右へ＝頭の 絵は のびない・白い 背中が 長く なる。scaleX では ない）。波の 先と 白い 水は 走る 馬（CSS x 190〜312）を こえて、
     約 CSS x 360 で 水平に（2.05秒）。コマの 絵は 右へ ひろく（CANVAS 1260）。
   第4.107版 まさちゃん「あと絵が伸びたり縮んだりするのやめて！」：のばす ゆがみ D・かたむき（高い 所ほど ずらす）・頭の 外へ のばす ε を やめた
     （絵は 回して うつす だけ・頭は 巻き c で 回して 落とす だけ）。横長に のびる かわりに、くずれて 前へ たおれながら 波 ぜんたいが 右へ 走り
     （170px）、走る 馬を 追いこして 海の 線の 下へ 沈む。
     まさちゃん「大波は出てくる位置ランダムにして！」：大波を 右へ ずらして 出しても 絵の 左の はし（元の 画像の 左の はし）で 背中が
     たてに 切れて 見えない ように、白い 背中の 墨の 線を 左下へ のばして 海へ 沈めた（tail）。出る 場所は pack/ukiyoe.py の UK_POS。
   第4.104版：小波（小さな 大波）は この コマの 28〜39 を 同じ 大きさの 箱に ならべた 帯（make/ukiyoe_mini.py → ukiyoe.mini）。
     第4.106版：小波の 層 4つ（1つの 層が 1まいの つながった 絵）は この コマの 26〜40 の 頭の 帯から 作る（make/ukiyoe_mini.py → ukiyoe.ribbon）。
     この 絵を 作り直したら make/ukiyoe_mini.py も 動かす（第4.107版の 作り直しでは 動かして いない：小波の 層 ukiyoe.ribbon は
     第4.106版の 大波の コマから 作った まま。いま 動かすと のびない コマから 作り直す ので 小波の 形が 少し かわる）。
   しくみ：空を 色の つながりで ぬりつぶして（黒い 線で 止まる）波を とりだす → 明るさで 4つの 色に 分ける（細い 黒い 線は 濃い 藍）→
     絵 1まい：wave＝波の 一生の コマ（life：Z倍（第4.112版から 3倍）の 画素・コマごとの 四角を つめた シート）
   python3 kisekae/pack/make/ukiyoe_great.py 画像.jpg [OUT] [--save] → ios/kisekae_blobs/<id>.webp・kisekae/pack/blobs.json の ukiyoe.wave（ukiyoe.crest は 消す）"""
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
Z = 3                               # シートは 画面の 3倍（第4.112版：2 → 3。SC＝1/3 なので 元の 画像の 画素 そのまま＝これより 細かくは できない）
PIVOT = (480, 330)                  # 波の 先（頭）を 回す 中心（元の 画素）
SPLIT = [(318, 118), (420, 232), (480, 330), (522, 425), (560, 520)]    # 体と 頭の さかいめ（左上 → 右下・右がわが 頭）
D_IN = 150.0                        # さかいめから この 距離（元の 画素）で ゆがみが いっぱいに なる
Y_STOP = (390.0, 520.0)             # この 高さ（元の 画素）より 下は ゆがめない（波の 根もと）
PAL = dict(white=(246, 241, 227), light=(178, 199, 222), mid=(84, 112, 160), dark=(27, 37, 92))    # 浮世絵の 平らな 色
SKY_SEEDS = [(600, 40), (950, 100), (800, 180), (600, 450), (620, 540), (900, 450), (150, 120), (20, 150), (1100, 300), (700, 300), (700, 520)]

# 頭の 巻きの 強さ c（c<0 もり上がる・0 神奈川沖浪裏・0<c≦1 投げ出す・c>1 くずれる）→ 回す・のばす・落とす
def warp_params(c):
    """c → (回す 角度 θ°・外へ のばす ε・下へ 落とす 元の 画素)。
       第4.107版（まさちゃん「絵が伸びたり縮んだりするのやめて！」）：外へ のばす ε は いつも 0（頭は 回して 落とす だけ＝爪が のびたり ちぢんだり しない）"""
    if c <= 0:
        return 15.0 * c, 0.0, 0.0
    if c <= 1:
        return 16.0 * c, 0.0, 0.0
    u = (c - 1) / 0.6
    return 16.0 + 12.0 * u, 0.0, 36.0 * u


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


def crest_inv(c, X, Y, iters=7):
    """頭の ゆがみの 逆（元の 画像の 座標の 点 → ゆがめる 前の 点）：前へ 写す 式を くり返しで 逆に 解く"""
    th, ep, drop = warp_params(c)
    qx, qy = X - PIVOT[0], Y - PIVOT[1]
    px, py = X.copy(), Y.copy()
    for _ in range(iters):
        s = weight(px, py)
        ph = -math.radians(th) * s
        k = 1.0 / (1 + ep * s)
        cs, sn = np.cos(ph), np.sin(ph)
        ry = qy - drop * s
        px = PIVOT[0] + k * (cs * qx - sn * ry)
        py = PIVOT[1] + k * (sn * qx + cs * ry)
    return px, py


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


def _disk(r):
    k = int(round(2 * r + 1))
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))


def _nearest(lab, holes, allowed):
    """holes の 画素を、allowed の 色の いちばん 近い 画素の 色で うめる"""
    known = (~holes) & np.isin(lab, allowed)
    _, idx = cv2.distanceTransformWithLabels((~known).astype(np.uint8), cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    ky, kx = np.nonzero(known)
    lut = np.zeros(idx.max() + 1, np.uint8)
    lut[idx[ky, kx]] = lab[ky, kx]
    return np.where(holes, lut[idx], lab)


def roundify(rgb, bm):
    """第4.97版 まさちゃん「🌊自体をもう少し波の先や小波など丸い絵に変えて！」：泡の 爪（白・明るい 青と 細い 濃い 藍の 線）を 少し まるく。
       細い 線は ぼかして しきいで 太さを そろえ 先を まるく（まるい 筆の 線）・泡の 色は 少し なめらかに・外の ふちは 少し ふとらせて まるく して 線を 引き直す。
       波の 体（濃い 藍に 白い すじと 点）は そのまま（泡の 多い 所だけ）。→ (rgb, bm)"""
    pal = np.array([PAL['white'], PAL['light'], PAL['mid'], PAL['dark']], np.float32)
    lab = np.argmin(((rgb[..., None, :] - pal[None, None]) ** 2).sum(-1), -1).astype(np.uint8)
    a0 = bm > 0
    lab[~a0] = 4
    dark = lab == 3
    thick = cv2.morphologyEx(dark.astype(np.uint8), cv2.MORPH_OPEN, _disk(2)).astype(bool)
    line = dark & ~thick
    fill = _nearest(lab, line, [0, 1, 2, 3, 4])
    ms = [cv2.GaussianBlur((fill == k).astype(np.float32), (0, 0), 2.0) for k in range(5)]
    sm = np.argmax(np.stack(ms, -1), -1).astype(np.uint8)
    lm = cv2.GaussianBlur(line.astype(np.float32), (0, 0), 1.5) > 0.30           # 線：先が まるい 筆
    # 外の ふち：小さな かけら（しぶきに ちかい）は そのまま・大きい かたまりは 少し ふとらせて まるく
    n, cc, st, _ = cv2.connectedComponentsWithStats(a0.astype(np.uint8), 8)
    small = np.isin(cc, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] < 60])
    big = (a0 & ~small).astype(np.uint8)
    a1 = cv2.erode(cv2.dilate(big, _disk(3.0)), _disk(1.5))
    a1 = (cv2.GaussianBlur(a1.astype(np.float32), (0, 0), 1.5) > 0.5) | (cv2.GaussianBlur(big.astype(np.float32), (0, 0), 1.5) > 0.5)
    out = sm.copy()
    out = _nearest(out, a1 & (out == 4), [0, 1, 2, 3])
    out[lm] = 3
    foam = ((lab == 0) | (lab == 1)).astype(np.float32)
    zone = cv2.dilate((cv2.GaussianBlur(foam, (0, 0), 8.0) > 0.35).astype(np.uint8), _disk(4)).astype(bool)   # 泡の 多い 所
    res = np.where(zone, out, lab)
    grow = a1 & ~a0
    res[grow] = np.where(zone, out, 3)[grow]
    res[~a1] = 4
    ring = a1 & ~cv2.erode(a1.astype(np.uint8), _disk(1.0)).astype(bool)          # 外の ふちの 線（引き直し）
    res[ring] = 3
    res[small] = lab[small]                                                      # 小さな かけらは もとの まま
    alpha = (res != 4)
    col = pal[np.minimum(res, 3)]
    return col, alpha.astype(np.float32)


SHADE = dict(face=.30, curl=.22, back=.38)     # 第4.99版：ぼかし（bokashi）の 強さ（波の 根もと・巻きの 下の くぼみ・背中の 下の 明るい 青）
BACK_TINT = (196, 213, 233)                     # 白い 背中の 下の ぼかしの 明るい 青（水あさぎ）


def shade(rgb, bm):
    """第4.99版 まさちゃん「リアルで立体的に波がでてきて、消えていく表現にして！」：浮世絵の ぼかし（bokashi）で 波に 立体の かげを つける。
       ① 波の 体（藍・濃い 藍・明るい 青）は 根もとへ いくほど 濃く（下の 方は 海に 沈んで 光が とどかない）
       ② 波の 先の 下の くぼみ（巻きの 内がわ）は さらに 濃く（波の 先の かげ）
       ③ 白い 背中は 下の 左ほど 明るい 青へ ぼかす（光の あたる 頭は 白い まま＝丸い 背中に 見える）
       色の 数は ふやさない（平らな 4色の 上に なめらかな こさの 差を のせる だけ）。UK_FLAT=1 で ぼかし なし。座標は 元の 画素（CROP の 中）"""
    if os.environ.get('UK_FLAT') == '1':
        return rgb
    h, w = bm.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    X, Y = xx + CROP[0], yy + CROP[1]
    pal = np.array([PAL['white'], PAL['light'], PAL['mid'], PAL['dark']], np.float32)
    lab = np.argmin(((rgb[..., None, :] - pal[None, None]) ** 2).sum(-1), -1)
    white = (lab == 0).astype(np.float32)
    blue = 1.0 - white
    # ① 根もとへ 濃く（たての ぼかし）
    g_face = _ss(300, 640, Y) * SHADE['face']
    # ② 巻きの 内がわ（波の 先の 下の くぼみ）：だ円の ぼかし
    d = np.hypot((X - 470) / 150.0, (Y - 400) / 190.0)
    g_curl = (1 - _ss(.35, 1.0, d)) * SHADE['curl']
    k = 1 - np.clip(g_face + g_curl, 0, .45)
    out = rgb * (blue * k + white)[..., None]
    # ③ 白い 背中：下の 左ほど 明るい 青へ（頭の 近くは 白い まま）
    g_back = _ss(260, 560, Y) * (1 - _ss(300, 460, X)) * SHADE['back']
    tint = np.array(BACK_TINT, np.float32)
    out = out + (white * g_back)[..., None] * (tint - out)
    return np.clip(out, 0, 255).astype(np.float32)


TAIL = (92, 1.10, .004, 6)     # 第4.107版：左の はしの 白い 背中の 墨の 線を のばす（つなぐ x・かたむき・まがり・線の 太さ：crop の 画素）


def tail(rgb, bm):
    """第4.107版（まさちゃん「大波は出てくる位置ランダムにして！」）：大波を 右へ ずらして 出しても、絵の 左の はし（元の 画像の 左の はし）で
       背中が たてに 切れて 見えない ように、白い 背中の 墨の 線を 左下へ のばして 海の 線の 下へ 沈める
       （線より 上は すける・線の すぐ 下に 残った うしろの 波の 藍は 白い 背中に）。座標は crop の 画素（roundify の あと・shade の 前）"""
    x0, s, k, th = TAIL
    h, w = bm.shape
    rgb, bm = rgb.copy(), bm.copy()
    y0 = float(np.argmax(bm[:, x0] > .5))                               # つなぐ 所の 背中の 線の 上の はし
    white = np.array(PAL['white'], np.float32)
    dark = np.array(PAL['dark'], np.float32)
    pal = np.array([PAL['white'], PAL['light'], PAL['mid'], PAL['dark']], np.float32)

    def band(c):                                                          # うしろの 波の 藍（藍・濃い 藍）か
        return int(np.argmin(((pal - c) ** 2).sum(-1))) >= 2

    for x in range(0, x0 + 2):
        d = max(0.0, x0 - x)
        yc = y0 + s * d + k * d * d
        y1 = int(math.ceil(yc))
        if x < x0:
            bm[:max(0, min(h, y1)), x] = 0                                # 線より 上は すける
        yi = min(h, y1 + th)
        if y1 < h:
            on = bm[y1:yi, x] > .5
            rgb[y1:yi, x][on] = dark                                      # 墨の 線
        if x < x0:                                                        # 線の すぐ 下に 残った うしろの 波（藍）→ 白い 背中
            y = yi
            while y < h and bm[y, x] > .5 and band(rgb[y, x]):
                rgb[y, x] = white
                y += 1
    return rgb, bm


def down(pre, w2, h2):
    """前もって アルファを かけた 色（元の 画素）→ Z倍の 画素の RGBA u8（ふちが なめらか）"""
    sm = cv2.resize(pre, (w2, h2), interpolation=cv2.INTER_AREA)
    al = np.clip(sm[..., 3:4], 1e-6, 1)
    col = np.where(sm[..., 3:4] > 1e-4, sm[..., :3] / al, 0)
    return np.clip(np.concatenate([col, sm[..., 3:4] * 255.0], -1), 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- 第4.100版：波の 一生の コマ（life）
FPS = 24                            # コマ／秒
T_END = 2.05                        # 出て きて から 水平に なる まで（秒）：この あと 次の 波 まで 何も 出さない（pack/ukiyoe.py の WAVE_T＝7秒）
CANVAS = (1380, 330)                # コマの 絵（crop の 画素）：右へ 走って 馬を こえる よゆう（CSS で -22 → 438）・下は 海の 線（crop y 330＝CSS 112）で 切る
P0 = (430.0, 330.0)                 # 回す 中心（波の 根もとの まん中・海の 線：crop の 画素）
LEFT = (-60.0, 330.0)               # 前へ たおれる 中心（左の 根もと）
HB = 330.0                          # かたむける 高さの もと（海の 線＝crop y 330 から 上へ）
XS = (-20.0, 330.0)                 # 第4.101版：のばす ゆがみ D が 0 → いっぱいに なる 横の はんい（白い 背中の 上：頭の 絵は のびない）
# 鍵の 形（秒, 回す°（＋＝時計まわり＝前へ）, 回す 中心, 右へ, 下へ（crop px）, かたむき（高い 所ほど 右へ）, 頭の 巻き c, 右へ のばす D（crop px））
# 第4.107版（まさちゃん「あと絵が伸びたり縮んだりするのやめて！」）：かたむき（高い 所ほど ずらす）と のばす D は いつも 0＝絵は 回して うつす だけ
#   （頭は 巻き c で 回して 落とす だけ）。横長に のびる かわりに、くずれて 前へ たおれながら 波 ぜんたいが 右へ 走って（右へ 510 crop px＝170px）
#   走る 馬を 追いこし、海の 線の 下へ 沈む（水平に）。立ち上がる ときの うしろへ ねる 形は 回す だけ（−20°）
LIFE_KEYS = [
    (0.00, -20.0, P0, 0, 330, 0.0, -1.0, 0),       # 海の 中（うしろへ ねた 低い うねり：見えない）
    (0.30, -12.0, P0, 0, 165, 0.0, -.75, 0),       # 海から 出て くる
    (0.55, -4.0, P0, 0, 45, 0.0, -.3, 0),          # 立ち上がる・頭が 立つ
    (0.75, 0.0, P0, 0, 0, 0.0, 0.0, 0),            # 神奈川沖浪裏（止まらずに すぎる）
    (0.95, 1.5, LEFT, 0, 3, 0.0, .6, 0),           # 波の 先を 投げ出す
    (1.12, 3.0, LEFT, 12, 8, 0.0, 1.0, 0),         # のりだす
    (1.30, 4.5, LEFT, 60, 20, 0.0, 1.42, 0),       # 落ちる → ここから 前へ たおれながら 右へ 走る
    (1.48, 6.5, LEFT, 160, 40, 0.0, 1.6, 0),
    (1.64, 8.5, LEFT, 270, 68, 0.0, 1.6, 0),       # 走る 馬に 追いつく
    (1.78, 10.0, LEFT, 370, 100, 0.0, 1.6, 0),     # 馬を 追いこす
    (1.92, 11.0, LEFT, 450, 145, 0.0, 1.6, 0),
    (2.05, 11.5, LEFT, 510, 205, 0.0, 1.6, 0),     # 水平（海の 線の 下）
]
DOTS = (.50, .75, 1.40)             # 爪の 下の しぶきの 点：出はじめ・とびはじめ・消える（秒）


def stretch_g(x):
    """のばす ゆがみの 強さ（0〜1）：XS[0] より 左は 0・XS[1] より 右は 1（なめらか）"""
    t = np.clip((x - XS[0]) / (XS[1] - XS[0]), 0, 1)
    return t * t * (3 - 2 * t)


def _rig(a, piv, tx, ty):
    """piv の まわりに a° 回して (tx, ty) うつす → P0 の まわりの 回しと うつしに なおす"""
    r = math.radians(a)
    c, s = math.cos(r), math.sin(r)
    vx, vy = P0[0] - piv[0], P0[1] - piv[1]
    return a, c * vx - s * vy + piv[0] + tx - P0[0], s * vx + c * vy + piv[1] + ty - P0[1]


def life_fn():
    """鍵の 形を なめらかに つなぐ（形 ごとに PCHIP：止まらない・行きすぎない）→ t → (回す°, 右へ, 下へ, かたむき, c, のばす D)"""
    from scipy.interpolate import PchipInterpolator
    ts = [k[0] for k in LIFE_KEYS]
    rg = [_rig(a, p, x, y) for _, a, p, x, y, _, _, _ in LIFE_KEYS]
    fs = [PchipInterpolator(ts, [r[i] for r in rg]) for i in range(3)] + [PchipInterpolator(ts, [k[i] for k in LIFE_KEYS]) for i in (5, 6, 7)]
    return lambda t: tuple(float(f(min(max(t, 0.0), T_END))) for f in fs)


def life_frame(t, pre, pred, fn):
    """t 秒の コマ（crop の 画素・前もって アルファを かけた RGBA）：出口の 点 → のばすの 逆 → うつす・回す・かたむけるの 逆 → 頭の 巻きの 逆 → 元の 絵"""
    a, tx, ty, lean, c, D = fn(t)
    W_, H_ = CANVAS
    yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32)
    if D > 1e-3:                                                        # 第4.101版：のばす ゆがみ x＋D g(x) の 逆（ふえる いっぽう → 表で 逆に）
        xg = np.linspace(-400.0, W_ + 200.0, 6001)
        xx = np.interp(xx, xg + D * stretch_g(xg), xg).astype(np.float32)
    x, y = xx - tx, yy - ty
    r = math.radians(-a)
    cs, sn = math.cos(r), math.sin(r)
    dx, dy = x - P0[0], y - P0[1]
    x, y = P0[0] + dx * cs - dy * sn, P0[1] + dx * sn + dy * cs
    h = np.clip(HB - y, 0, None) / HB
    x = x - lean * HB * h ** 1.6
    sx, sy = crest_inv(c, x + CROP[0], y + CROP[1])
    sx, sy = (sx - CROP[0]).astype(np.float32), (sy - CROP[1]).astype(np.float32)
    out = cv2.remap(pre, sx, sy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    d0, d1, d2 = DOTS
    if d0 < t < d2:                                                     # しぶきの 点：爪の 下に あらわれ、投げ出す ときに 前へ とんで 落ちる
        k = min(1.0, (t - d0) / .2) * min(1.0, (d2 - t) / .25)
        u = max(0.0, (t - d1) / (d2 - d1))
        d = cv2.remap(pred, sx - 45 * u, sy - 110 * u * u, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0) * k
        out = d + out * (1 - d[..., 3:4])
    out[-1, :, :] *= .5                                                  # 海の 線で 切る（ふちを なめらかに）
    return out


def pack_cells(cells):
    """コマ（RGBA u8・それぞれ 大きさが ちがう）を 1まいに つめる（高い じゅんに 段に ならべる）→ (シート, [(x, y)])"""
    order = sorted(range(len(cells)), key=lambda i: -cells[i].shape[0])
    WMAX = 2400
    pos = [None] * len(cells)
    x = y = rowh = 0
    for i in order:
        h, w = cells[i].shape[:2]
        if x + w > WMAX and x > 0:
            x, y, rowh = 0, y + rowh + 2, 0
        pos[i] = (x, y)
        x += w + 2
        rowh = max(rowh, h)
    SW = max(p[0] + cells[i].shape[1] for i, p in enumerate(pos))
    SH = max(p[1] + cells[i].shape[0] for i, p in enumerate(pos))
    sheet = np.zeros((SH, SW, 4), np.uint8)
    for i, (px, py) in enumerate(pos):
        h, w = cells[i].shape[:2]
        sheet[py:py + h, px:px + w] = cells[i]
    return sheet, pos


def build_life(src, out=None):
    rgb, bm, dm = extract(src)
    if os.environ.get('UK_SHARP') != '1':                              # 第4.97版：泡の 爪を 少し まるく
        rgb, bm = roundify(rgb, bm)
    rgb, bm = tail(rgb, bm)                                            # 第4.107版：左の はしの 背中を 海へ 沈める（どの 場所に 出ても 切れて 見えない）
    rgb = shade(rgb, bm)                                               # 第4.99版：ぼかしで 立体の かげ
    pre = np.dstack([rgb * bm[..., None], bm]).astype(np.float32)
    pred = np.dstack([np.full_like(rgb, 246.0) * dm[..., None], dm]).astype(np.float32)
    fn = life_fn()
    W_, H_ = CANVAS
    W2, H2 = int(round(W_ * SC * Z)), int(round(H_ * SC * Z))
    n = int(round(T_END * FPS))
    cells, boxes = [], []
    for k in range(1, n + 1):
        fr = down(life_frame(k / FPS, pre, pred, fn), W2, H2)
        al = fr[..., 3] > 2
        if not al.any():
            cells.append(np.zeros((2, 2, 4), np.uint8))
            boxes.append([0, 0, 2, 2])
            continue
        ys, xs = np.nonzero(al)
        x0, y0 = max(0, xs.min() - 1), max(0, ys.min() - 1)
        x1, y1 = min(W2, xs.max() + 2), min(H2, ys.max() + 2)
        x0 -= x0 % Z                                                  # 画面の 1px（Z 画素）に そろえる
        y0 -= y0 % Z
        cells.append(fr[y0:y1, x0:x1])
        boxes.append([int(x0), int(y0), int(x1 - x0), int(y1 - y0)])
        if out and k % 4 == 0:
            os.makedirs(out, exist_ok=True)
            a = fr[..., 3:4] / 255.0
            cv2.imwrite(os.path.join(out, f'life_{k:02d}.png'), (fr[..., :3] * a + np.array((241, 230, 207)) * (1 - a))[..., ::-1].astype(np.uint8))
    sheet, pos = pack_cells(cells)
    meta = dict(z=Z, fps=FPS, t_end=T_END, canvas=[round(W_ * SC, 2), round(H_ * SC, 2)], sheet=[int(sheet.shape[1]), int(sheet.shape[0])],
                cells=[[p[0], p[1], b[2], b[3], b[0], b[1]] for p, b in zip(pos, boxes)])   # シートの x・y・はば・高さ・コマの 中の x・y（Z倍の 画素）
    return sheet, meta


def forget(theme, name):
    """blobs.json から 使わなく なった 絵を 消す（record と 同じ ロック）"""
    import fcntl
    import json
    from sheets import PACK
    p = os.path.join(PACK, 'blobs.json')
    with open(p + '.lock', 'w') as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        d = json.load(open(p, encoding='utf-8'))
        if d.get(theme, {}).pop(name, None) is not None:
            tmp = p + '.tmp'
            json.dump(d, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
            os.replace(tmp, p)
        fcntl.flock(lk, fcntl.LOCK_UN)


def main(src, out=None, save=False):
    sheet, meta = build_life(src, out)
    print('life', sheet.shape, len(meta['cells']), 'frames', flush=True)
    if out:
        from sheets import preview_png
        preview_png(sheet, os.path.join(out, 'life_sheet.png'), bg=(241, 230, 207))
    if save:
        from sheets import save_webp, record
        bid = save_webp(sheet, quality=84)
        record('ukiyoe', 'wave', bid, meta)
        forget('ukiyoe', 'crest')
        print('wave', bid, os.path.getsize(os.path.join(os.environ.get('KISEKAE_ASSETS') or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), 'ios', 'kisekae_blobs'), bid + '.webp')), flush=True)


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    main(a[0], a[1] if len(a) > 1 else os.environ.get('OUT'), '--save' in sys.argv)
