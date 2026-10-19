"""シルバー帯・ゴールド帯の壁紙（metal_wall.py：銀・金の馬の像が いつも キラキラ）の絵と形。flat/silver_banner.py・gold_banner.py と同じ像・同じ作り
   - silver_banner.webp・gold_banner.webp：いまの絵（きらめきつき）。顔のすじを平らにした像（silver_horse.flat_face）で 描きなおした絵
   - silver_base.webp・gold_base.webp：同じ絵から きらめき（4本の光）だけ ぬいた絵（壁紙では きらめきを ページの SVG で またたかせる）
   - metal_run.json：像の形（ふちの線：光が走るのを 像の中だけにする）・きらめきの場所と長さ（いまの絵の4つ＋またたく所）・
     こまかい光の粒の場所・うしろの光の輪（まん中・半径）・床の線（780×320 の座標）
   python3 flat/metal_run.py <出力フォルダ>（sdfr がいる・約40秒）"""
import sys, os, json, math, shutil
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import silver_banner as SB
import gold_banner as GB
import style2d as S2
from style2d import save_webp

W, Hh = SB.W, SB.Hh
EXTRA = 10                 # またたく きらめき（いまの絵の4つの ほかに）
EXTRA_GAP = 30             # きらめきどうしの 間（画素）
DOTS = 26                  # こまかい光の粒


def f1(v):
    s = f'{v:.1f}'
    return s[:-2] if s.endswith('.0') else s


def outline(A, eps=0.6):
    """像の ふちの線（2倍で ふちを たどって なめらかに）→ SVG の d（いちばん大きい輪＋小さい輪も）"""
    SS = 2
    m2 = cv2.resize(A, (W * SS, Hh * SS), interpolation=cv2.INTER_LINEAR)
    cs, _ = cv2.findContours((m2 > 0.5).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    d = ''
    for c in sorted(cs, key=cv2.contourArea, reverse=True):
        if cv2.contourArea(c) < 20 * SS * SS:
            continue
        p = c[:, 0, :].astype(np.float32)
        kk = np.arange(-4, 5); g = np.exp(-(kk / 1.8) ** 2); g /= g.sum()
        ps = np.stack([np.convolve(np.r_[p[-4:, k], p[:, k], p[:4, k]], g, 'valid') for k in (0, 1)], 1) / SS
        q = cv2.approxPolyDP(ps.reshape(-1, 1, 2).astype(np.float32), eps, True)[:, 0, :]
        d += 'M' + 'L'.join(f'{f1(x)} {f1(y)}' for x, y in q) + 'Z'
    return d


def glints(R, spark, n=EXTRA, gap=EXTRA_GAP):
    """いまの絵の きらめき（spark）の ほかに、像の明るい所から n か所（たがいに gap 以上 はなす）"""
    A = np.clip(R['a'], 0, 1)
    rgb = SB.to_srgb(SB.aces(R['rgb'] / np.maximum(R['a'], 1e-4)[..., None]))
    lum_s = cv2.GaussianBlur(rgb.max(2) * A, (0, 0), 1.0)
    inner = cv2.erode((A > 0.5).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    taken = [(x, y) for x, y, L in spark]
    out = []
    for idx in np.argsort((lum_s * inner).ravel())[::-1][:60000]:
        y, x = divmod(int(idx), W)
        if lum_s[y, x] < 0.72:
            break
        if all((x - tx) ** 2 + (y - ty) ** 2 > gap ** 2 for tx, ty in taken):
            taken.append((x, y))
            out.append((int(x), int(y), round(float(8 + 6 * (lum_s[y, x] - 0.72) / 0.28), 1)))
        if len(out) >= n:
            break
    return out


def dots(R, n=DOTS, seed=17):
    """こまかい光の粒：像の上の 明るめの所から ばらばらに"""
    A = np.clip(R['a'], 0, 1)
    rgb = SB.to_srgb(SB.aces(R['rgb'] / np.maximum(R['a'], 1e-4)[..., None]))
    lum = rgb.max(2) * A
    inner = cv2.erode((A > 0.5).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    ys, xs = np.nonzero(inner & (lum > 0.55))
    rng = np.random.default_rng(seed)
    pick, out = rng.permutation(len(xs)), []
    for i in pick:
        x, y = int(xs[i]), int(ys[i])
        if all((x - a) ** 2 + (y - b) ** 2 > 22 ** 2 for a, b in out):
            out.append((x, y))
        if len(out) >= n:
            break
    return out


def build(outdir):
    os.makedirs(outdir, exist_ok=True)
    run = dict(size=[W, Hh])
    for name, pal in (('silver', SB.SILVER), ('gold', GB.GOLD)):
        tmp = os.path.join(S2.TMP, f'metal{os.getpid()}{name}')
        os.makedirs(tmp, exist_ok=True)
        try:
            R, S = SB.render3d(tmp, pal)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        info = {}
        save_webp(SB.compose(R, pal=pal, info=info), os.path.join(outdir, f'{name}_banner.webp'))
        save_webp(SB.compose(R, pal=pal, sparkle=False), os.path.join(outdir, f'{name}_base.webp'))
        A = np.clip(R['a'], 0, 1)
        ys, xs = np.nonzero(A > 0.5)
        if 'shape' not in run:
            gy = info['gy']
            run['shape'] = dict(d=outline(A), box=[int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)], floor=int(gy),
                                ring=[round(W * .5, 1), round(gy * 0.52, 1), 150])
        run[name] = dict(spark=[[x, y, round(L, 2)] for x, y, L in info['spark']], glint=[list(g) for g in glints(R, info['spark'])],
                         dots=[list(p) for p in dots(R)])
        print(name, 'きらめき', run[name]['spark'], 'またたく', len(run[name]['glint']), '粒', len(run[name]['dots']))
    json.dump(run, open(os.path.join(outdir, 'metal_run.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    return run


if __name__ == '__main__':
    build(sys.argv[1])
