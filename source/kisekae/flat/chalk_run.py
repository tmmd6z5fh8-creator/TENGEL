"""黒板の壁紙（chalk_wall.py：馬を 黒板消しで消して、チョークで 書きなおす）の絵と形。flat/chalk_banner.py の部品から作る
   - chalk_base.webp：馬のない黒板（メモの字・矢印・星・「1着」・木の枠・チョーク）。いまの絵から 馬だけ ない形
   - chalk_f{1,2,3}.webp：馬の ぬり（チョークの白・ゼッケンの黄色・毛の線・目）・すき通し
   - chalk_l{1,2,3}.webp：馬の 外の線・すき通し（地面の線は ページの SVG）・chalk_c2.webp：ゼッケンのふち（黄色）・すき通し
   - chalk_z{1,2,3}.webp：黒板消しで 消したあとの もや（消した所だけ・すき通し）
   - chalk_run.json：絵を置く場所と、チョークで書く線（外の線・ゼッケンのふち・地面の線）・ぬる ジグザグ・黒板消しの ジグザグ（780×320 の座標）
   馬は 1＝いまの絵の 走る馬・2＝くらと ゼッケン「1」の競走馬・3＝立っている馬（chalk_banner.HORSES）
   chalk_base ＋ chalk_f1 ＋ chalk_l1 を重ねると いまの絵と同じ（8bit と WebP の分だけ ちがう。--check で たしかめる）
   python3 flat/chalk_run.py <出力フォルダ> [--check]"""
import sys, os, math, json
import numpy as np
import cv2
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import chalk_banner as CB
from chalk_banner import W, Hh, over, hexc

Q = 88                               # WebP の きれいさ（いまの絵と同じ）
LINE_W = 9.0                         # 外の線を 書いて出す 線のはば（780×320 の座標）
CLOTH_W = 9.0                        # ゼッケンのふちを 書いて出す 線のはば
SIMPLIFY = 0.8                       # 外の線を 点の列にする時の まとめ
HATCH_W, HATCH_D = 34.0, 28.0        # ぬる ジグザグの はば・ならびの間
HATCH_ANG = math.radians(62)         # ぬる向き（チョークの筋と同じ：右下へ）
ERASE_W, ERASE_D = 78.0, 66.0        # 黒板消しの はば（たての ジグザグ）・ならびの間
MARGIN = 4.0                         # 消す・ぬる はしの ゆとり
HAZE = '#C9D6CF'                     # 消したあとの もやの色


def rgba_of(ops):
    """（色・こさ）を すき通しの上に 順に重ねる → (色, こさ)。色は こさで わる前（premultiplied）から もどす"""
    P = np.zeros((Hh, W, 3), np.float32)
    A = np.zeros((Hh, W), np.float32)
    for col, a in ops:
        a = np.clip(a, 0, 1).astype(np.float32)
        c = np.broadcast_to(np.asarray(col, np.float32), (Hh, W, 3))
        P = P * (1 - a[..., None]) + c * a[..., None]
        A = A * (1 - a) + a
    C = np.where(A[..., None] > 1e-6, P / np.maximum(A, 1e-6)[..., None], 0)
    return np.clip(C, 0, 1), A


def save_rgba(C, A, path):
    """8bit にして はしを切って保存 → [x, y, w, h]"""
    a8 = (np.clip(A, 0, 1) * 255 + .5).astype(np.uint8)
    ys, xs = np.nonzero(a8)
    x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    c8 = (np.clip(C, 0, 1) * 255 + .5).astype(np.uint8)
    im = Image.fromarray(np.dstack([c8, a8])[y0:y1, x0:x1], 'RGBA')
    im.save(path, 'WEBP', quality=Q, alpha_quality=100, method=6)
    return [int(x0), int(y0), int(x1 - x0), int(y1 - y0)]


def simplify(pts, eps, closed=False):
    c = np.asarray(pts, np.float32).reshape(-1, 1, 2)
    return cv2.approxPolyDP(c, eps, closed)[:, 0, :].astype(float)


def outline_path(S):
    """外の線を 書く順の点の列（780×320 の座標）：鼻先から 頭の上 → 背中 → しっぽ → … と ひと回り。ほかの輪は あとで"""
    cs = sorted(CB.contours(S['mask']), key=lambda c: -len(c))
    out = []
    for n, ps in enumerate(cs):
        p = np.asarray(ps, float) / CB.SS
        if n == 0:
            i0 = int(np.argmin(np.linalg.norm(p - S['mz'][:2], axis=1)))
            p = np.roll(p, -i0, axis=0)
            if p[min(25, len(p) - 1), 1] > p[-min(25, len(p) - 1), 1]:     # 上（頭の上）へ 向かう向きに
                p = np.r_[p[:1], p[1:][::-1]]
        q = simplify(np.r_[p, p[:1]], SIMPLIFY)
        k = 1                                            # はじめの所を 少し こえて 書きおわる（はしが とがった所でも すきまが できない）
        while k < len(q) - 1 and plen(q[:k + 1]) < 12:
            k += 1
        out.append(np.r_[q, q[1:k + 1]])
    return out


def band_path(alpha, w, d, ang, margin, flip=False, thr=0.004):
    """ジグザグ：向き ang（ラジアン・画像の座標）に 行ったり来たりしながら、それと直角の向きへ すすむ。
       こさ alpha が thr より こい所を ぜんぶ通る（はば w・ならびの間 d）。flip：すすむ向きを 逆に"""
    v = np.array([math.cos(ang), math.sin(ang)])                 # 行ったり来たりの向き
    u = np.array([v[1], -v[0]])                                  # すすむ向き（右・上より）
    if flip:
        u = -u
    ys, xs = np.nonzero(alpha > thr)
    P = np.stack([xs + .5, ys + .5], 1)
    pu, pv = P @ u, P @ v
    u0, u1 = pu.min() - margin, pu.max() + margin
    n = max(1, int(math.ceil((u1 - u0 - w) / d)) + 1)
    dd = (u1 - u0 - w) / max(1, n - 1)
    cs = [u0 + w / 2 + k * dd for k in range(n)]
    rng = []
    for c in cs:
        sel = np.abs(pu - c) <= w / 2 + 1.0
        if sel.any():
            rng.append([pv[sel].min() - margin, pv[sel].max() + margin])
        else:
            rng.append(None)
    for k in range(n):                                           # 何もない所は となりに合わせる
        if rng[k] is None:
            nb = [r for r in (rng[k - 1] if k else None, rng[k + 1] if k + 1 < n else None) if r]
            rng[k] = [min(r[0] for r in nb), max(r[1] for r in nb)] if nb else [0, 0]
    pts = []
    for k, c in enumerate(cs):
        down = k % 2 == 0                                        # v が ふえる向き（たての時は 下へ）
        lo, hi = rng[k]
        if down:
            st = min(lo, rng[k - 1][0]) if k else lo
            en = max(hi, rng[k + 1][1]) if k + 1 < n else hi
        else:
            st = max(hi, rng[k - 1][1]) if k else hi
            en = min(lo, rng[k + 1][0]) if k + 1 < n else lo
        pts.append(c * u + st * v)
        pts.append(c * u + en * v)
    return np.array(pts)


def cover(paths, w, shape=(Hh, W), join='round'):
    """線（はば w・はしは まっすぐ切る）が かぶる所（少し内がわ：1画素けずる）"""
    m = np.zeros(shape, np.uint8)
    for p in paths:
        p = np.asarray(p, float)
        for a, b in zip(p[:-1], p[1:]):
            d = b - a
            L = np.linalg.norm(d)
            if L < 1e-6:
                continue
            nrm = np.array([-d[1], d[0]]) / L * w / 2
            q = np.array([a + nrm, b + nrm, b - nrm, a - nrm])
            cv2.fillConvexPoly(m, np.round(q * 16).astype(np.int32), 1, cv2.LINE_8, shift=4)
        if join == 'round':
            for c in p[1:-1]:
                cv2.circle(m, (int(round(c[0] * 16)), int(round(c[1] * 16))), int(w / 2 * 16), 1, -1, cv2.LINE_8, shift=4)
    return cv2.erode(m, np.ones((3, 3), np.uint8)).astype(bool)


def extend(p, d):
    """点の列の 両はしを d だけ のばす"""
    p = np.asarray(p, float).copy()
    for i, j in ((0, 1), (-1, -2)):
        t = p[i] - p[j]
        p[i] = p[i] + t / (np.linalg.norm(t) + 1e-9) * d
    return p


def plen(p):
    p = np.asarray(p, float)
    return float(np.linalg.norm(np.diff(p, axis=0), axis=1).sum())


def r1(p):
    return [[round(float(x), 1), round(float(y), 1)] for x, y in p]


def build(outdir, check=False):
    os.makedirs(outdir, exist_ok=True)
    img0, smudge = CB.board()
    run = dict(size=[W, Hh], horses=[])
    base = None
    for h, H in enumerate(CB.HORSES, 1):
        S = CB.shape(H)
        O = CB.ops(S, smudge)
        if h == 1:                                   # いまの絵の 黒板（鼻の穴のつもりの点は 黒板の上の 小さな点：いまの絵のまま 黒板に残す）
            b = img0
            for name, col, a, grp in O:
                if grp == 'board':
                    b = over(b, col, a)
            base = CB.decor(b)
            CB.save_webp(np.clip(base, 0, 1), os.path.join(outdir, 'chalk_base.webp'))
        x0, x1, gy = CB.ground(S)
        gl = np.zeros((Hh, W), np.float32)            # 地面の線（ページでは 同じ形の SVG の線：はば3・x0-1〜x1+2）
        cv2.line(gl, (x0, gy), (x1, gy), 1.0, 2, cv2.LINE_AA)
        fill_ops = [(col, a) for name, col, a, grp in O if grp in ('fill', 'hole')]
        hole = np.ones((Hh, W), np.float32)
        for name, col, a, grp in O:                  # 目は 外の線より上（いまの絵の順）：線も 目の所は うすく
            if grp == 'hole':
                hole = hole * (1 - a)
        line_ops = [(col, a * hole) for name, col, a, grp in O if grp == 'line']
        Cf, Af = rgba_of(fill_ops)
        Cl, Al = rgba_of(line_ops)
        fbox = save_rgba(Cf, Af, os.path.join(outdir, f'chalk_f{h}.webp'))
        lbox = save_rgba(Cl, Al, os.path.join(outdir, f'chalk_l{h}.webp'))
        # 書く線：外の線（ひと回り）→ ゼッケンのふち（べつの絵）→ 地面の線（SVG の線）。線ごとに べつの絵なので 2重に ぬらない
        strokes = [dict(kind='line', layer='l', col='w', pts=r1(p)) for p in outline_path(S)]
        cbox = None
        cl_ops = [(col, a) for name, col, a, grp in O if grp == 'cline']
        if cl_ops:
            Cc, Ac = rgba_of(cl_ops)
            cbox = save_rgba(Cc, Ac, os.path.join(outdir, f'chalk_c{h}.webp'))
            ca, cedge = CB.cloth_parts(S)
            strokes.append(dict(kind='line', layer='c', col='y', pts=r1(extend(simplify(cedge / CB.SS, SIMPLIFY), 3.0))))
        strokes.append(dict(kind='line', layer='g', col='w', pts=r1([(x0 - 1, gy + .5), (x1 + 2, gy + .5)])))
        # ぬる ジグザグ（しっぽ → 頭）
        hatch = band_path(Af, HATCH_W, HATCH_D, HATCH_ANG, MARGIN)
        strokes.append(dict(kind='fill', layer='f', col='w', pts=r1(hatch)))
        # 黒板消し：たての ジグザグ（頭 → しっぽ）
        U = np.maximum(np.maximum(Af, Al), gl)
        if cbox:
            U = np.maximum(U, Ac)
        er = band_path(U, ERASE_W, ERASE_D, math.pi / 2, MARGIN + 2, flip=True)
        er_c = cover([er], ERASE_W)
        # 消したあとの もや：チョークを たてに こすって のばした形（消した所だけ）
        At = 1 - (1 - Af) * (1 - Al) * (1 - gl) * ((1 - Ac) if cbox else 1)
        sm = cv2.GaussianBlur(At, (0, 0), sigmaX=4.5, sigmaY=17)
        rng = np.random.default_rng(60 + h)
        stv = cv2.resize(rng.random((4, 140)).astype(np.float32), (W, Hh), interpolation=cv2.INTER_CUBIC)
        ghost = np.clip(sm * 0.34, 0, 0.15) * (0.6 + 0.5 * np.clip(stv, 0, 1))           # のびた チョーク（たての すじ）
        soft = cv2.GaussianBlur(cv2.erode(er_c.astype(np.uint8), np.ones((15, 15), np.uint8)).astype(np.float32), (0, 0), 6)
        rub = 0.016                                                                      # こすった所の うすい もや
        haze = np.clip(ghost + rub, 0, 0.2) * soft * er_c * (CB.yy < 297)                # 消した所だけ（ふちは ぼかす）・木の枠には かからない
        Cz = np.broadcast_to(hexc(HAZE), (Hh, W, 3))
        zbox = save_rgba(Cz, haze, os.path.join(outdir, f'chalk_z{h}.webp'))
        # かぶり：消す ジグザグは 馬を ぜんぶ通る・書く線と ぬる ジグザグは それぞれの絵を ぜんぶ通る
        a8f, a8l = Af * 255 >= .5, Al * 255 >= .5
        lc = cover([np.asarray(s['pts']) for s in strokes if s['layer'] == 'l'], LINE_W)
        hc = cover([hatch], HATCH_W)
        miss = dict(erase=int(((U * 255 >= .5) & ~er_c).sum()), line=int((a8l & ~lc).sum()), fill=int((a8f & ~hc).sum()))
        if cbox:
            miss['cloth'] = int(((Ac * 255 >= .5) & ~cover([np.asarray(s['pts']) for s in strokes if s['layer'] == 'c'], CLOTH_W)).sum())
        run['horses'].append(dict(fill=fbox, line=lbox, haze=zbox, strokes=strokes, erase=r1(er), **(dict(cloth=cbox) if cbox else {}),
                                  ground=[int(x0) - 1, int(x1) + 2, int(gy) + .5], miss=miss,
                                  len=dict(line=round(sum(plen(s['pts']) for s in strokes if s['kind'] == 'line'), 1),
                                           fill=round(plen(hatch), 1), erase=round(plen(er), 1))))
        print(f'馬{h}: ぬり {fbox} 線 {lbox} ゼッケンのふち {cbox} もや {zbox} かぶらない画素 {miss} 長さ {run["horses"][-1]["len"]}')
        if check and h == 1:
            st = CB.paint(img0, S, smudge)
            st = CB.decor(st)
            comp = base * (1 - Af[..., None]) + Cf * Af[..., None]
            comp = comp * (1 - Al[..., None]) + Cl * Al[..., None]
            comp = comp * (1 - gl[..., None]) + np.array([0.85, 0.85, 0.8], np.float32) * gl[..., None]
            d = np.abs(comp - st) * 255
            print(f'  いまの絵との ちがい（重ねた時・8bit 前）：最大 {d.max():.3f} 平均 {d.mean():.4f}')
    run['widths'] = dict(line=LINE_W, cloth=CLOTH_W, fill=HATCH_W, erase=ERASE_W, ground=5)
    json.dump(run, open(os.path.join(outdir, 'chalk_run.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    return run


if __name__ == '__main__':
    build(sys.argv[1], check='--check' in sys.argv)
