# たてがみの 色を そろえる（まさちゃん 11/09 23:51「紫の立髪が白いところがあるから紫に直して！」：⑧ 幻の馬＆神様馬・黒い 馬の 紫の たてがみ）
#   元の GLB の 絵から 金・白の すじが 紫の たてがみに 入って いる（元の まま でも 出る）→ 紫に かこまれた 金・白の 点を まわりの 紫に する
#   python3 kisekae/fig/fig_recolor.py <作業フォルダの out/figN（.npz・_c.webp・_m.webp）> [--show <しるしの 絵.png>]
#   ・fig_prep.py の あとに 使う（fig_prep.py を やり直すと もどる ので、もう一度 これを）
#   ・どこを 直すかは 下の AREA（3D の 箱：たてがみ だけ）と 色の きまり（金・ベージュ・だいだい。黒い 馬の 灰色の 光は 入れない）
#   ・金属／あらさ も まわりの 紫と 同じに（金の すじは 金属が 強くて 光り方も ちがう）
import os, sys
import numpy as np
from PIL import Image
from scipy.spatial import cKDTree
import matplotlib.colors as mc
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig_prep import lib, mesh_pos

# フィギュアの 番号 → 直す 3D の 箱（x・y・z の 下と 上）
#   （わくの 上の 金の ふち・まん中の 金の 飾り・月桂樹・黒い 馬の 歯 は 箱の 外）
AREA = {8: ((-1.0, -0.25), (1.70, 2.20), (-1.0, 1.0))}      # 黒い 馬（幻の馬）の 紫の たてがみ の 上の 方（金の すじは y 1.7〜2.1・黒い 馬に 金の 飾りは ない）
R = 0.025          # まわりを 見る はんい（m：高さ 2.15 の 単位）
FRAC = 0.0         # まわりの 紫の 割合が これ より 多い 点だけ 直す（箱が たてがみ だけ なので 0：すじの まわりは 金や 影も 多い）


def purple(hsv):
    h = hsv[..., 0] * 360; return (h > 255) & (h < 350) & (hsv[..., 1] > 0.3) & (hsv[..., 2] > 0.15)


def main():
    base = os.path.abspath(sys.argv[1]); n = int(os.path.basename(base)[3:])
    show = sys.argv[sys.argv.index('--show') + 1] if '--show' in sys.argv else None
    if n not in AREA: print('fig', n, '：直す ところ なし'); return
    (x0, x1), (y0, y1), (z0, z1) = AREA[n]
    d = np.load(base + '.npz'); V, T, UVc = d['V'], d['T'], d['UVc']; L = lib()
    col = np.asarray(Image.open(base + '_c.webp').convert('RGB'), np.float32) / 255; S = col.shape[0]
    P, cv = mesh_pos(L, V, T, UVc, S)
    inb = cv & (P[..., 0] > x0) & (P[..., 0] < x1) & (P[..., 1] > y0) & (P[..., 1] < y1) & (P[..., 2] > z0) & (P[..., 2] < z1)
    hsv = mc.rgb_to_hsv(np.clip(col, 0, 1)); pur = purple(hsv) & inb
    hh = hsv[..., 0] * 360
    cand = inb & ~pur & ((hh < 75) | (hh > 350)) & (hsv[..., 1] > 0.12) & (hsv[..., 2] > 0.3)     # 金・ベージュ・だいだい（黒い 馬の 体の 灰色の 光は 色が うすいので 入らない）
    pp = P[pur]; tp = cKDTree(pp); ta = cKDTree(P[inb])
    qc = P[cand]
    npur = tp.query_ball_point(qc, R, return_length=True); nall = ta.query_ball_point(qc, R, return_length=True)
    fix = (npur / np.maximum(nall, 1)) >= FRAC
    idx = np.argwhere(cand)[fix]
    _, j = tp.query(P[idx[:, 0], idx[:, 1]], k=24, workers=-1)
    pc = col[pur]; new = pc[j].mean(1)
    # 明るさは 少しだけ 残す（すじの 形が うすく 見える くらい）
    lum = lambda a: a.mean(-1, keepdims=True)
    new = np.clip(new * (1 + 0.15 * (lum(col[idx[:, 0], idx[:, 1]]) / np.maximum(lum(new), 1e-3) - 1)), 0, 1)
    out = col.copy(); out[idx[:, 0], idx[:, 1]] = new
    print('fig', n, '箱の 中', int(inb.sum()), '紫', int(pur.sum()), '金・白の 点', int(cand.sum()), '→ 紫に した', len(idx), flush=True)
    Image.fromarray((out * 255 + 0.5).astype(np.uint8)).save(base + '_c.webp', 'WEBP', lossless=True, method=4)
    # 金属／あらさ（大きさが ちがう ので その 大きさで 同じ 場所を 直す）
    mrp = base + '_m.webp'; mr = np.asarray(Image.open(mrp).convert('RGB'), np.float32) / 255; Sm = mr.shape[0]
    Pm, cm = mesh_pos(L, V, T, UVc, Sm)
    mk = np.zeros((S, S), bool); mk[idx[:, 0], idx[:, 1]] = True
    k = S // Sm; mkm = mk.reshape(Sm, k, Sm, k).mean((1, 3)) > 0.25
    pm = np.asarray(Image.fromarray(pur.astype(np.uint8) * 255).resize((Sm, Sm), Image.BOX)) > 200
    pm &= cm; mkm &= cm & ~pm
    if mkm.any() and pm.any():
        tm = cKDTree(Pm[pm]); _, jm = tm.query(Pm[mkm], k=16, workers=-1)
        mr2 = mr.copy(); mr2[mkm] = mr[pm][jm].mean(1)
        Image.fromarray((mr2 * 255 + 0.5).astype(np.uint8)).save(mrp, 'WEBP', lossless=True, method=4)
        print('  金属／あらさ も', int(mkm.sum()), '点', flush=True)
    if show:
        vis = (col * 0.35 * 255).astype(np.uint8); vis[inb] = (col[inb] * 255).astype(np.uint8); vis[mk] = (0, 255, 0)
        Image.fromarray(vis).save(show)


if __name__ == '__main__':
    main()
