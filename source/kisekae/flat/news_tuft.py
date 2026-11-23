# 競馬新聞の 走る コマ：おなかの 下の 小さな とっき（とがった かけら）を 消す（第4.215版）
#   まさちゃん 2026/11/24 01:22「競馬新聞の壁紙赤丸のところから変なとっきが出てるから無くして！」
#   とっき＝おなかの 下（うしろ足と 前足の あいだ）に 出る 短い とがった 墨（3D の 下絵の おなかの ひだ が 墨の 形に なった もの）。15コマ ぜんぶに ある。
#   3D から 描き直さずに、いまの シート（news_run_hq.webp：ios/kisekae_blobs の 台帳 news_blobs.json の run）から その かけら だけ 消す（ほかの 画素は かえない）：
#     1. 墨の 形（暗い 画素）から 細い 所（半径 R の 丸で ひらくと 消える 所）を 出す
#     2. その うち「体の まん中の 下に ぶら下がる 短い かけら」（高さ MAXH より 短い・足では ない＝下まで のびない・体の 横はばの 20〜80% の 所・体の 上下の まん中より 下）を えらぶ
#     3. えらんだ 所を まわりの 紙の 色で うめる（ふちは 1px なじませる）
#   python3 kisekae/flat/news_tuft.py <もとの シート> <出す フォルダ>   → news_run_hq.webp（flat/hq_install.py news <出す フォルダ> で 入れる）・news_tuft_dbg.png（消した 所）
import sys, os, numpy as np, cv2
from scipy import ndimage
from PIL import Image
N = 15; R = 9; MAXH = 34


def disk(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]; return (x * x + y * y <= r * r).astype(np.uint8)


def fix_cell(c):
    """c＝1コマ（float32 RGB）。→ 直した コマ・消した 所"""
    lum = c.mean(2); ink = lum < 120
    lab, n = ndimage.label(ink)
    if not n: return c, np.zeros(ink.shape, bool)
    big = lab == (np.argmax(np.bincount(lab.ravel())[1:]) + 1)                     # 馬（いちばん 大きい 墨）
    ys, xs = np.nonzero(big); x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    core = cv2.morphologyEx(big.astype(np.uint8), cv2.MORPH_OPEN, disk(R)) > 0      # 太い 所（体・足の 上）
    thin = big & ~core
    tl, tn = ndimage.label(thin); kill = np.zeros(ink.shape, bool)
    cyb = y0 + (y1 - y0) * 0.42                                                    # 体の 上下の まん中あたり
    for k in range(1, tn + 1):
        m = tl == k; yy, xx = np.nonzero(m)
        if len(yy) < 25: continue
        hgt = yy.max() - yy.min() + 1; cx = xx.mean()
        if hgt > MAXH or yy.min() < cyb or yy.max() > y0 + (y1 - y0) * 0.74: continue      # 長い もの（足）・体の 上の もの（たてがみ・しっぽ）・下の 方の もの（ひづめ・足先）は のこす
        if not (x0 + 0.22 * (x1 - x0) < cx < x0 + 0.78 * (x1 - x0)): continue
        # 上で 太い 所（体）に ついて いて、下は 紙（足の とちゅう では ない）
        up = ndimage.binary_dilation(m, iterations=2) & core
        if not up.any() or np.nonzero(up)[0].mean() > yy.mean(): continue
        below = ndimage.binary_dilation(m, iterations=3) & big & ~m & ~core
        if below.any(): continue
        kill |= m
    if not kill.any(): return c, kill
    kd = ndimage.binary_dilation(kill, iterations=2) & ~core                        # ふちの にじみ まで
    near = ndimage.binary_dilation(kill, iterations=14); dark = (lum < 200) & ~core & near          # 消した 所の そばに のこる 小さな 点（かけらの はし）も 消す
    dl, dn = ndimage.label(dark & ~ndimage.binary_dilation(core, iterations=1)); cnt = np.bincount(dl.ravel(), minlength=dn + 1)
    kd |= np.isin(dl, [i for i in range(1, dn + 1) if cnt[i] <= 60]) & near
    paper = ~ndimage.binary_dilation(ink, iterations=3)
    num = cv2.GaussianBlur(c * paper[..., None].astype(np.float32), (0, 0), 9); den = cv2.GaussianBlur(paper.astype(np.float32), (0, 0), 9)[..., None]
    fill = num / np.maximum(den, 1e-3)
    a = cv2.GaussianBlur(kd.astype(np.float32), (0, 0), 0.8)[..., None]; a = np.where(core[..., None], 0, a)
    return c * (1 - a) + fill * a, kd


if __name__ == '__main__':
    src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
    im = np.asarray(Image.open(src).convert('RGB')).astype(np.float32); H, W = im.shape[:2]; cw = W // N; o = im.copy(); dbg = im.copy(); tot = 0
    for f in range(N):
        c, k = fix_cell(im[:, f * cw:(f + 1) * cw]); o[:, f * cw:(f + 1) * cw] = c; tot += int(k.sum())
        d = dbg[:, f * cw:(f + 1) * cw]; d[k] = (255, 0, 255); print('コマ', f, '消した 点', int(k.sum()), flush=True)
    Image.fromarray(np.clip(o + 0.5, 0, 255).astype(np.uint8)).save(os.path.join(out, 'news_run_hq.webp'), 'WEBP', quality=86, method=6)
    Image.fromarray(dbg.astype(np.uint8)).save(os.path.join(out, 'news_tuft_dbg.png'))
    print('合計', tot, os.path.getsize(os.path.join(out, 'news_run_hq.webp')), 'B')
