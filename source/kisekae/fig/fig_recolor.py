# フィギュアの 絵の 色を 部分だけ 直す（元の GLB の 絵に 入って いる よけいな 色：fig_prep.py の あとに 使う）
#   ⑧ 幻の馬＆神様馬：黒い 馬の 紫の たてがみ に 金・ベージュの すじ → まわりの 紫に（まさちゃん 11/09 23:51「紫の立髪が白いところがあるから紫に直して！」）
#   ② ゴールデンスカラー：ハンコの うら（取っ手の がわ）に 赤い しみ（はんこの 面の 朱が はみ出た）→ まわりの 金に（11/10 00:19「二枚目のハンコの裏赤くなってるところ直して！」）
#   python3 kisekae/fig/fig_recolor.py <作業フォルダの out/figN（.npz・_c.webp・_m.webp）> [--show <しるしの 絵.png>]
#   ・fig_prep.py を やり直すと もどる ので、もう一度 これを
#   ・どこを 直すかは RULES（3D の 場所・直す 色・まわりの 色）。金属／あらさ も まわりの 色の 所と 同じに
import os, sys
import numpy as np
from PIL import Image
from scipy.spatial import cKDTree
import matplotlib.colors as mc
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig_prep import lib, mesh_pos, fill


def box(P, xr, yr, zr):
    return (P[..., 0] > xr[0]) & (P[..., 0] < xr[1]) & (P[..., 1] > yr[0]) & (P[..., 1] < yr[1]) & (P[..., 2] > zr[0]) & (P[..., 2] < zr[1])


def cyl(P, c, a, tr, rmax):     # 円柱（中心 c・軸 a）の 中：軸の 向きの 位置 t が tr の 間・軸からの 距離 rmax まで
    c = np.asarray(c); a = np.asarray(a, np.float64); a /= np.linalg.norm(a)
    q = P - c; t = q @ a; r = np.linalg.norm(q - t[..., None] * a, axis=-1)
    return (t > tr[0]) & (t < tr[1]) & (r < rmax)


H = lambda s: s[..., 0] * 360
purple = lambda s: (H(s) > 255) & (H(s) < 350) & (s[..., 1] > 0.3) & (s[..., 2] > 0.15)
goldish = lambda s: ((H(s) < 75) | (H(s) > 350)) & (s[..., 1] > 0.12) & (s[..., 2] > 0.3)          # 金・ベージュ・だいだい（灰色の 光は 色が うすいので 入らない）
red = lambda s: ((H(s) < 21) | (H(s) > 340)) & (s[..., 1] > 0.45) & (s[..., 2] > 0.25)                 # 朱・赤だいだい（金・だいだいは 色相 22〜45）
notred_bright = lambda s: ~red(s) & (H(s) > 22) & (H(s) < 70) & (s[..., 2] > 0.3)                 # 金・だいだい

RULES = {
    # 黒い 馬（幻の馬）の 紫の たてがみ の 上の 方（金の すじは y 1.7〜2.1・黒い 馬に 金の 飾りは ない）。わくの 金の ふち・まん中の 飾り・歯 は 外
    8: dict(region=lambda P: box(P, (-1.0, -0.25), (1.70, 2.20), (-1.0, 1.0)), fix=goldish, target=purple, keep_light=0.15, what='紫の たてがみの 金の すじ'),
    # ハンコ：はんこの 面（朱）は 軸の 向き t≈0。うら（取っ手・うらの くぼみ・取っ手の 根もと）は t −0.05 より うしろ → 赤を 金に
    2: dict(region=lambda P: cyl(P, (-0.41, 1.601, 0.167), (0.461, -0.083, 0.884), (-0.30, -0.05), 0.27), fix=red, target=notred_bright, keep_light=0.25, what='ハンコの うらの 赤'),
}


def main():
    base = os.path.abspath(sys.argv[1]); n = int(os.path.basename(base)[3:])
    show = sys.argv[sys.argv.index('--show') + 1] if '--show' in sys.argv else None
    if n not in RULES: print('fig', n, '：直す ところ なし'); return
    rule = RULES[n]
    d = np.load(base + '.npz'); V, T, UVc = d['V'], d['T'], d['UVc']; L = lib()
    col = np.asarray(Image.open(base + '_c.webp').convert('RGB'), np.float32) / 255; S = col.shape[0]
    P, cv = mesh_pos(L, V, T, UVc, S)
    inb = cv & rule['region'](P)
    hsv = mc.rgb_to_hsv(np.clip(col, 0, 1))
    tgt = rule['target'](hsv) & inb; cand = rule['fix'](hsv) & inb & ~tgt
    if not tgt.any() or not cand.any(): print('fig', n, '：直す 点 なし'); return
    tp = cKDTree(P[tgt])
    idx = np.argwhere(cand)
    _, j = tp.query(P[idx[:, 0], idx[:, 1]], k=24, workers=-1)
    new = col[tgt][j].mean(1)
    # 明るさは 少しだけ 残す（形の かげが うすく 見える くらい）
    lum = lambda a: a.mean(-1, keepdims=True)
    new = np.clip(new * (1 + rule['keep_light'] * (lum(col[idx[:, 0], idx[:, 1]]) / np.maximum(lum(new), 1e-3) - 1)), 0, 1)
    out = col.copy(); out[idx[:, 0], idx[:, 1]] = new
    out = fill(out, cv)                    # 島の すき間も 直した 色で うめ直す（ふちに 前の 色の 細い 線が 出ない）
    print('fig', n, rule['what'], '：場所の 中', int(inb.sum()), 'まわりの 色', int(tgt.sum()), '→ 直した', len(idx), flush=True)
    Image.fromarray((out * 255 + 0.5).astype(np.uint8)).save(base + '_c.webp', 'WEBP', lossless=True, method=4)
    # 金属／あらさ（大きさが ちがう ので その 大きさで 同じ 場所を 直す）
    mrp = base + '_m.webp'; mr = np.asarray(Image.open(mrp).convert('RGB'), np.float32) / 255; Sm = mr.shape[0]
    Pm, cm = mesh_pos(L, V, T, UVc, Sm)
    mk = np.zeros((S, S), bool); mk[idx[:, 0], idx[:, 1]] = True
    k = S // Sm; mkm = mk.reshape(Sm, k, Sm, k).mean((1, 3)) > 0.25
    pm = np.asarray(Image.fromarray(tgt.astype(np.uint8) * 255).resize((Sm, Sm), Image.BOX)) > 200
    pm &= cm; mkm &= cm & ~pm
    if mkm.any() and pm.any():
        tm = cKDTree(Pm[pm]); _, jm = tm.query(Pm[mkm], k=16, workers=-1)
        mr2 = mr.copy(); mr2[mkm] = mr[pm][jm].mean(1); mr2 = fill(mr2, cm)
        Image.fromarray((mr2 * 255 + 0.5).astype(np.uint8)).save(mrp, 'WEBP', lossless=True, method=4)
        print('  金属／あらさ も', int(mkm.sum()), '点', flush=True)
    if show:
        vis = (col * 0.35 * 255).astype(np.uint8); vis[inb] = (col[inb] * 255).astype(np.uint8); vis[mk] = (0, 255, 0)
        Image.fromarray(vis).save(show)


if __name__ == '__main__':
    main()
