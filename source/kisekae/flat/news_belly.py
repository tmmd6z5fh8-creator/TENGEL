# 競馬新聞の 走る コマ：おなかの 下から 出たり 戻ったり する 出っぱり（黄色い 丸の 所）を 消す（第4.233版）
#   まさちゃん 2026/11/27 22:57「あと、壁紙の競馬新聞の馬の絵で、黄丸の突起みたいなのが、出てきたり戻ったりしてコンプライアンスに引っかかりそうだから無くして！」
#   出っぱり＝おなかの 下（うしろ足と 前足の あいだ）に ぶら下がる 細長い 形（墨の ふちの 中が 白い「レンズ」の 形＋前の はしが 丸い 墨）。
#     3D の 下絵の 奥の うしろ足の もも（スタイフル）が おなかの 線より 下に 出た 所が、墨の 形に なった もの。15コマ の うち 10コマ（0・6〜14）に あり、6〜9 で 大きい
#   3D から 描き直さずに、いまの シート（ios/kisekae_blobs の 台帳 news_blobs.json の run）から その 形 だけ 消す（ほかの 画素は かえない：第4.215版 news_tuft.py と 同じ 考え方）：
#     1. 体の 中の「白い 穴」（墨に かこまれた 紙の 色）の うち、おなかの 下の はしに ある もの（すぐ 下が 外の 紙）を さがす
#     2. 絵の 下の はし（下から 見て はじめて 墨に あたる 所）を 列ごとに 出して、足の ない ひとつながりの 列で「上の 包」（下へ ふくらむ 出っぱりを 橋わたし）を 引く
#        → その 線より 下に ある 白い 穴 だけが 出っぱり（体の 中の 白い かすれは 線より 上なので のこる）
#     3. 新しい おなかの 線＝上の 包を 少し 下へ ふくらませた 線（おなかの まるみ：はばの 6%・4px まで）。線より 下は 紙・線より 上に のこる 白い 穴は 墨で うめる
#        左の はしで のこる 墨が 線より ずっと 下まで ある ときは、ななめ（45°）に 切って うしろ足の 前へ つなぐ。消した 所の そばに のこる 小さな 墨の 点も 消す
#     4. 紙は ほかの コマの 同じ 所（紙と 字は どの コマも 同じ 所に ある）の まん中の 値。のこる 墨の そばは hq_news.py と 同じ うすい かげ（10%）
#   python3 kisekae/flat/news_belly.py <もとの シート> <出す フォルダ>   → news_run_hq.webp（flat/hq_install.py news <出す フォルダ> で 入れる）・news_belly_dbg.png（消した 所）
import sys, os, numpy as np, cv2
from scipy import ndimage
from PIL import Image
N = 15
ZX, ZY = (215, 385), (105, 220)          # おなかの 下を さがす 所（1コマの 中の 画素：1.5倍の シート）
INK, PAPER = 110, 140                    # 墨／紙 と みなす 明るさ


def disk(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]; return (x * x + y * y <= r * r).astype(np.uint8)


def paper_of(cells):
    """紙（馬の ない 所）：コマごとに 墨から はなれた 所の 色を あつめて、画素ごとの まん中の 値。どの コマでも かくれて いる 所は まわりの 紙を ぼかした 色"""
    st = np.stack(cells); lums = st.mean(3)
    far = np.stack([~ndimage.binary_dilation(l < 150, iterations=6) for l in lums])
    bg = np.zeros_like(cells[0])
    import warnings
    with np.errstate(all='ignore'), warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning)
        for ch in range(3):
            bg[..., ch] = np.nanmedian(np.where(far, st[..., ch], np.nan), axis=0)
    miss = np.isnan(bg).any(2) | (far.sum(0) < 3)                                 # 紙が 見える コマが 3つ より 少ない 所は まわりから
    if miss.any():
        pap = far.any(0); fb = np.nan_to_num(bg) * pap[..., None]
        num = cv2.GaussianBlur(fb, (0, 0), 9); den = cv2.GaussianBlur(pap.astype(np.float32), (0, 0), 9)[..., None]
        bg[miss] = (num / np.maximum(den, 1e-3))[miss]
    return bg


def upper_hull(xs, ys):
    """点（x, 下の はしの y）の 上の 包（y が 小さい 方：下へ ふくらむ 出っぱりを 橋わたし）→ x を 入れると y を 返す"""
    pts = sorted(zip(xs, ys)); h = []
    for p in pts:
        while len(h) >= 2:
            (x1, y1), (x2, y2) = h[-2], h[-1]
            if (x2 - x1) * (p[1] - y1) - (y2 - y1) * (p[0] - x1) <= 0: h.pop()
            else: break
        h.append(p)
    hx = np.array([q[0] for q in h], float); hy = np.array([q[1] for q in h], float)
    return lambda x: np.interp(x, hx, hy)


def fix_cell(c, bg):
    """c＝1コマ（float32 RGB）・bg＝紙。→ 直した コマ・消した 所（紙に した 所）・墨で うめた 所・ようす"""
    Hh, Ww = c.shape[:2]; lum = c.mean(2); ink = lum < INK
    none = np.zeros(lum.shape, bool)
    lab, n = ndimage.label(ink)
    if not n: return c, none, none, None
    big = lab == (np.argmax(np.bincount(lab.ravel())[1:]) + 1)                     # 馬（いちばん 大きい 墨）
    filled = ndimage.binary_fill_holes(big); holes = filled & ~big
    bigpaper = cv2.morphologyEx((~filled).astype(np.uint8), cv2.MORPH_OPEN, disk(3)) > 0      # 外の 紙（細い すじは のぞく）
    # 1. おなかの 下の はしに ある 白い 穴（候補）
    hl, hn = ndimage.label(holes); cand = []
    for k in range(1, hn + 1):
        m = hl == k; yy, xx = np.nonzero(m)
        if len(yy) < 30 or xx.max() - xx.min() < 12: continue
        if not (ZX[0] <= xx.mean() <= ZX[1] and ZY[0] <= yy.mean() <= ZY[1]): continue
        d = []
        for x in range(xx.min(), xx.max() + 1):
            col = np.nonzero(m[:, x])[0]
            if not len(col): continue
            j = col.max() + 1
            while j < Hh and not bigpaper[j, x]: j += 1
            d.append(j - col.max() - 1)
        d = np.array(d)
        if np.median(d) > 9 or (d <= 12).mean() < 0.75: continue
        cand.append(dict(m=m, x0=int(xx.min()), x1=int(xx.max()), y1=int(yy.max()), cx=float(xx.mean()), cy=float(yy.mean())))
    if not cand: return c, none, none, None
    # 2. 絵の 下の はし（下から）と 上の 包
    lo = max(cand, key=lambda q: q['cy'])                                          # いちばん 下の 穴を 中心に
    ys = min(max(q['y1'] for q in cand) + 16, Hh - 1)
    yb = {}
    for x in range(max(0, min(q['x0'] for q in cand) - 30), min(Ww, max(q['x1'] for q in cand) + 50)):
        if lum[ys, x] < PAPER: continue                                            # 下まで 墨＝足
        y = ys
        while y > 0 and lum[y, x] >= INK: y -= 1
        yb[x] = y
    st0 = [x for x in range(lo['x0'], lo['x1'] + 1) if x in yb]
    if not st0: return c, none, none, None
    sa = sb = st0[len(st0) // 2]
    while sa - 1 in yb: sa -= 1
    while sb + 1 in yb: sb += 1
    cols = list(range(sa, sb + 1))
    hull = upper_hull(cols, [yb[x] for x in cols])
    # 下の はしが 線より 下に 出る 穴（または 線の すぐ 上に いる 小さな すき間）だけ。体の 中の 白い かすれ（線より ずっと 上）は のこす
    lens = [q for q in cand if sa <= q['cx'] <= sb and (q['y1'] > hull(q['cx']) + 3 or (q['y1'] >= hull(q['cx']) and q['cy'] > hull(q['cx']) - 3))]
    if not lens: return c, none, none, None
    dep = {x: yb[x] - hull(x) for x in cols}
    t0, t1 = min(q['x0'] for q in lens), max(q['x1'] for q in lens)
    while t0 - 1 in dep and dep[t0 - 1] > 2: t0 -= 1
    while t1 + 1 in dep and dep[t1 + 1] > 2: t1 += 1
    # 3. 新しい おなかの 線（上の 包 ＋ まるみ）
    sag = min(4.0, 0.06 * (t1 - t0))
    cut = lambda x: hull(x) + sag * 4 * ((x - t0) / max(1, t1 - t0)) * (1 - (x - t0) / max(1, t1 - t0))
    kill = np.zeros(lum.shape, bool); fill_ink = np.zeros(lum.shape, bool)
    lm = np.zeros(lum.shape, bool); other = np.zeros(lum.shape, bool)
    for q in lens: lm |= q['m']
    for q in cand:
        if not any(q is r for r in lens): other |= q['m']
    lm2 = ndimage.binary_dilation(lm, iterations=2) & ~ndimage.binary_dilation(other | (holes & ~lm), iterations=1)      # 穴の ふちの 灰色（にじみ）まで。ほかの 白い かすれには さわらない
    for x in range(t0, t1 + 1):
        top = int(np.ceil(cut(x))) + 1
        if x in yb and yb[x] >= top: kill[top:yb[x] + 3, x] = True
        fill_ink[:top, x] = lm2[:top, x]                                           # 線より 上に のこる 白い 穴（と ふちの 灰色）は 墨で うめる
    ycut0 = cut(t0)
    for x in range(t0 - 1, max(0, t0 - 30), -1):                                   # 左の はし：ななめに 切って うしろ足の 前へ
        yc = int(np.ceil(ycut0 + (t0 - x) * 1.0)) + 1
        if yc >= Hh or not ink[yc, x]: break
        y = yc
        while y < Hh and ink[y, x]: y += 1
        if y >= Hh - 2: break                                                      # 下まで つづく＝足（切らない）
        kill[yc:y + 2, x] = True
    near = ndimage.binary_dilation(kill, iterations=6)                             # 消した 所の そばに のこる 小さな 墨の 点
    dl, dn = ndimage.label((lum < 150) & near & ~kill)
    if dn:
        keep = ndimage.binary_dilation(big & ~kill & ~near, iterations=1); cnt = np.bincount(dl.ravel(), minlength=dn + 1)
        for i in range(1, dn + 1):
            if cnt[i] <= 40 and not ((dl == i) & keep).any(): kill |= dl == i
    kill &= ~fill_ink
    # 消した 所の まわり（線より 下）に のこる うすい 灰色（ふちの にじみ）も 紙に
    below = np.zeros(lum.shape, bool)
    for x in range(max(0, t0 - 30), min(Ww, t1 + 4)):
        below[int(np.ceil(cut(min(max(x, t0), t1)))) + 2:, x] = True
    rest = ndimage.binary_dilation((ink & ~kill) | fill_ink, iterations=1)
    kill |= ndimage.binary_dilation(kill, iterations=3) & below & (lum < 215) & ~rest
    # 4. ぬる：紙（＋のこる 墨の そばの うすい かげ）・墨
    ink_after = (ink & ~kill) | fill_ink
    halo = cv2.GaussianBlur(ink_after.astype(np.float32), (0, 0), 1.8)
    paper = bg * (1 - 0.10 * halo)[..., None]
    inkc = np.median(c[ink & ~kill & ndimage.binary_dilation(fill_ink | kill, iterations=8)], axis=0) if (ink & ~kill).any() else np.array([20, 20, 20], np.float32)
    a = np.maximum(cv2.GaussianBlur(kill.astype(np.float32), (0, 0), 0.7), kill.astype(np.float32))
    b = np.maximum(cv2.GaussianBlur(fill_ink.astype(np.float32), (0, 0), 0.6), fill_ink.astype(np.float32))
    o = c.copy()
    o = np.where(a[..., None] > 0, o * (1 - a[..., None]) + paper * a[..., None], o)
    o = np.where(b[..., None] > 0, o * (1 - b[..., None]) + inkc[None, None, :] * b[..., None], o)
    return o, kill, fill_ink, dict(tube=(t0, t1), depth=round(float(max(dep[x] for x in range(t0, t1 + 1) if x in dep)), 1), sag=round(sag, 1))


if __name__ == '__main__':
    src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
    im = np.asarray(Image.open(src).convert('RGB')).astype(np.float32); H, W = im.shape[:2]; cw = W // N
    cells = [im[:, f * cw:(f + 1) * cw] for f in range(N)]
    bg = paper_of(cells)
    o = im.copy(); dbg = im.copy(); tot = 0
    for f in range(N):
        c, k, fi, info = fix_cell(cells[f], bg)
        o[:, f * cw:(f + 1) * cw] = c; tot += int(k.sum())
        d = dbg[:, f * cw:(f + 1) * cw]; d[k] = (255, 0, 255); d[fi] = (0, 200, 255)
        print('コマ', f, '消した 点', int(k.sum()), '墨で うめた 点', int(fi.sum()), info or '', flush=True)
    Image.fromarray(np.clip(o + 0.5, 0, 255).astype(np.uint8)).save(os.path.join(out, 'news_run_hq.webp'), 'WEBP', quality=86, method=6)
    Image.fromarray(dbg.astype(np.uint8)).save(os.path.join(out, 'news_belly_dbg.png'))
    print('合計', tot, os.path.getsize(os.path.join(out, 'news_run_hq.webp')), 'B')
