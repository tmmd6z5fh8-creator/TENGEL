# TENGERカードバトルの プレイボード 3つ：絵の「山札」の 札だけを 左へ うつした 絵を 作る（第4.194版）
#
#   まさちゃん（2026/11/18 10:15）「カードバトルのこのプレイボード、赤丸のところ、馬と山札重なってる！改善して！」と 画面 3まい
#   （『歯車の工房』steam・『紫月の夜』violet・『黄金の星空』starry）。
#   この 3つは 第4.185版の 絵の まま：「山札」の 札が もとの 場所に あって、その 上の 山札の カードが 右の 馬に かぶる。
#   第4.186版で 絵を 入れ替えた 4つ（紅蓮・桜・白亜・蒼氷）は、まさちゃんの 新しい 絵で 札が 左へ 98px（1672 の 5.86%）→ 山札も 左へ（.cbboard.dl）。
#   → この 3つも 同じ 形に そろえる：絵の「山札」の 札 だけを 左へ 98px うつした 絵 cb_board_<名前>_dl.png を 作って、アプリでは 7つ ぜんぶ dl に する。
#     ・馬・飾り・色・台・捨て札・VS の わく・歯車は そのまま（さわるのは 札と 札の あと だけ）。もとの 絵は のこす（上書きしない・消さない：アプリには 入れない）
#     ・札の 形：『黄金の星空』の 札の ふちから とる（3つとも 同じ 形の 札）→ ほかの 2つは 縁の 強さで いちばん 合う 場所に 合わせる
#     ・札の あと：まわりと なめらかに つなぐ（ポアソンの つなぎ：下の poisson()・scipy で 解く）。うめる 模様は
#         『歯車の工房』『黄金の星空』：同じ 行の 140px 左（木目・夜空）
#         『紫月の夜』：札の うしろに かくれて いた 馬の たてがみと 三日月の ふちを、左右 対称の 左がわの 飾りから（左右を 反転して いちばん 合う ずれで）
#     ・うつした 札の 下に うすい かげ（もとの 札と 同じ くらい）
#
#   使い方：python3 kisekae/cb_board_dl.py [見本の 出力フォルダ]
#     → ios/cb_assets/src/cb_board_<steam|violet|starry>_dl.png（1672×941）。そのあと python3 kisekae/cb_art.py で アプリの 絵（cb_bd_<名前>.webp・_s.webp）を 作り直す
import os, sys
import numpy as np, cv2

cv2.setNumThreads(0)      # 同じ 入力で いつも 同じ 絵に（この OpenCV 5.0 は 並列の 計算で 答えが ゆれる ことが あった）
W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(W, 'ios', 'cb_assets', 'src')
IDS = ('steam', 'violet', 'starry')
SHIFT = 98                                   # 左へ うつす 幅（第4.186版の 新しい 絵と 同じ：1672 × 5.86%）
ROI = (1145, 432, 1305, 500)                 # 札を さがす 所（x0, y0, x1, y1）
FILL = {'steam': 'left', 'starry': 'left', 'violet': 'mirror'}


def disk(r):
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))


def grad(im):
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)
    return cv2.magnitude(cv2.Sobel(g, cv2.CV_32F, 1, 0), cv2.Sobel(g, cv2.CV_32F, 0, 1))


def plate_shape(im):
    """札の 形（ROI の 中の 0/255）：ふちの 線（Canny）で かこまれた いちばん 大きい 札の 大きさの 形"""
    x0, y0, x1, y1 = ROI; g = cv2.cvtColor(im[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY)
    e = cv2.dilate(cv2.Canny(g, 40, 120), np.ones((3, 3), np.uint8))
    cs, _ = cv2.findContours(e, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cs = [c for c in cs if 100 <= cv2.boundingRect(c)[2] <= 135 and 28 <= cv2.boundingRect(c)[3] <= 48]
    m = np.zeros(g.shape, np.uint8); cv2.drawContours(m, [max(cs, key=cv2.contourArea)], -1, 255, -1)
    return m


def plate_mask(im, shape, tpl_im):
    """この 絵の 札の 場所（絵 ぜんたいの 0/255）：tpl_im の 札の 縁と いちばん 合う ずれ（±10px）"""
    x0, y0, x1, y1 = ROI
    ys, xs = np.nonzero(shape); tx0, ty0, tx1, ty1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    tpl = grad(tpl_im[y0:y1, x0:x1])[ty0:ty1, tx0:tx1] * (cv2.dilate(shape, disk(2))[ty0:ty1, tx0:tx1] > 0)
    r = cv2.matchTemplate(grad(im[y0 - 10:y1 + 10, x0 - 10:x1 + 10]), tpl, cv2.TM_CCORR_NORMED)
    _, score, _, loc = cv2.minMaxLoc(r); dx, dy = loc[0] - 10 - tx0, loc[1] - 10 - ty0
    m = np.zeros(im.shape[:2], np.uint8)
    m[y0:y1, x0:x1] = cv2.warpAffine(shape, np.float32([[1, 0, dx], [0, 1, dy]]), (x1 - x0, y1 - y0), flags=cv2.INTER_NEAREST)
    return m, (dx, dy), score


def poisson(src, dst, hole):
    """ポアソンの つなぎ：穴の 中は src の 模様（となりとの 差）・ふちは dst に ぴったり（Δf ＝ Δsrc・ふち＝dst）。
    cv2.seamlessClone は この 入れ物の OpenCV 5.0 では 同じ 入力でも 答えが ゆれる（たしかめた）ので、scipy の 疎行列で 自分で 解く"""
    import scipy.sparse as sp, scipy.sparse.linalg as sl
    ys, xs = np.nonzero(hole); n = len(ys); H, W_ = hole.shape
    idx = -np.ones(hole.shape, np.int64); idx[ys, xs] = np.arange(n)
    rows, cols, vals = [np.arange(n)], [np.arange(n)], [np.full(n, 4.0)]
    s = src.astype(np.float64); d = dst.astype(np.float64); b = np.zeros((n, 3))
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        qy, qx = np.clip(ys + dy, 0, H - 1), np.clip(xs + dx, 0, W_ - 1)
        b += s[ys, xs] - s[qy, qx]                                  # 模様（src の となりとの 差）
        qi = idx[qy, qx]; inside = qi >= 0
        rows.append(np.arange(n)[inside]); cols.append(qi[inside]); vals.append(np.full(inside.sum(), -1.0))
        b[~inside] += d[qy[~inside], qx[~inside]]                   # ふち＝dst
    A = sp.csc_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(n, n))
    solve = sl.factorized(A); out = dst.copy()
    for c in range(3):
        out[ys, xs, c] = np.clip(np.round(solve(b[:, c])), 0, 255).astype(np.uint8)
    return out


def fill_src(im, hole, how):
    """札の あとを うめる 模様（絵 ぜんたいと 同じ 大きさ）"""
    if how == 'left':
        return np.roll(im, 140, axis=1), (140, 0)
    f = cv2.flip(im, 1)                                          # 左右 対称の 左がわの 飾り
    ry0, ry1, rx0, rx1 = 380, 545, 1150, 1345
    ring = ((cv2.dilate(hole, disk(30)) > 0) & (hole == 0))[ry0:ry1, rx0:rx1]
    a = im.astype(np.float32)[ry0:ry1, rx0:rx1]; best = None
    for dy in range(-14, 15):
        for dx in range(-14, 15):
            b = np.roll(np.roll(f, dy, axis=0), dx, axis=1).astype(np.float32)[ry0:ry1, rx0:rx1]
            d = float(((a - b) ** 2).sum(axis=2)[ring].mean())
            if best is None or d < best[0]: best = (d, dx, dy)
    return np.roll(np.roll(f, best[2], axis=0), best[1], axis=1), (best[1], best[2])


def make(bid, shape, tpl_im):
    im = cv2.imread(os.path.join(SRC, f'cb_board_{bid}.png'))
    m, off, score = plate_mask(im, shape, tpl_im)
    hole = cv2.dilate(m, disk(7))                                 # 札＋まわりの かげ
    src, soff = fill_src(im, hole, FILL[bid])
    base = poisson(src, im, hole > 0).astype(np.float32)
    al = cv2.GaussianBlur(np.roll(m, -SHIFT, axis=1).astype(np.float32) / 255, (0, 0), 0.8)[..., None]
    shade = cv2.GaussianBlur(np.roll(np.roll(m, -SHIFT, axis=1), 3, axis=0).astype(np.float32) / 255, (0, 0), 2.5)[..., None] * 0.45
    out = (np.roll(im, -SHIFT, axis=1).astype(np.float32) * al + base * (1 - shade) * (1 - al)).clip(0, 255).astype(np.uint8)
    # さわった 所 いがいは もとの まま（ねんのため：札の あと＋うつした 札の まわり だけ）
    touch = cv2.dilate(hole | np.roll(cv2.dilate(m, disk(8)), -SHIFT, axis=1) | np.roll(np.roll(cv2.dilate(m, disk(8)), -SHIFT, axis=1), 3, axis=0), disk(2)) > 0
    out[~touch] = im[~touch]
    p = os.path.join(SRC, f'cb_board_{bid}_dl.png'); cv2.imwrite(p, out)
    ys, xs = np.nonzero(m)
    print(f'  {bid}：札 x {xs.min()}〜{xs.max()}・y {ys.min()}〜{ys.max()}（縁の 合い {score:.3f}・ずれ {off}）→ 左へ {SHIFT}px・'
          f'あとを うめる 模様：{"同じ 行の 左" if FILL[bid] == "left" else "左右 対称の 左がわ"}（{soff}）・さわった 点 {int(touch.sum())}（{touch.mean() * 100:.2f}%）→ {os.path.basename(p)}')
    return im, out, m


def main():
    tpl_im = cv2.imread(os.path.join(SRC, 'cb_board_starry.png'))
    shape = plate_shape(tpl_im)
    prev = sys.argv[1] if len(sys.argv) > 1 else None
    rows = []
    for bid in IDS:
        im, out, m = make(bid, shape, tpl_im)
        if prev:
            c = lambda a: cv2.resize(a[380:540, 980:1400], None, fx=2, fy=2, interpolation=cv2.INTER_LANCZOS4)
            rows.append(np.hstack([c(im), c(out)]))
    if prev:
        os.makedirs(prev, exist_ok=True); cv2.imwrite(os.path.join(prev, 'cb_board_dl_preview.png'), np.vstack(rows))


if __name__ == '__main__':
    main()
