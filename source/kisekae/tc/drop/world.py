# 玉の 物理の ための 台の 形（切り口 → つながった 線 → かどを へらす）
import sys, json
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from dp_env import ROOT
from common import *
import slice as SL

ZC = 0.054            # 玉の 中心の 深さ（盤 0.022 ＋ 玉の 半径 0.032）
ZL = 0.035            # 低い もの（液晶の 輪・左右の かべ）を 見る 深さ
R_BALL = 0.032
BOX = (-0.52, 0.52, -0.40, 0.44)


def chain(S, tol=2e-5):
    """線分（n,2,2）を つないで 折れ線に する → [点の 列（閉じて いれば はじめと おわりが 同じ）]"""
    n = len(S)
    key = lambda p: (int(round(p[0] / tol)), int(round(p[1] / tol)))
    ends = {}
    for i in range(n):
        for e in (0, 1):
            ends.setdefault(key(S[i, e]), []).append((i, e))
    used = np.zeros(n, bool)
    out = []
    for i0 in range(n):
        if used[i0]: continue
        used[i0] = True
        line = [S[i0, 0], S[i0, 1]]
        for fwd in (True, False):
            while True:
                p = line[-1] if fwd else line[0]
                nxt = None
                for (j, e) in ends.get(key(p), []):
                    if not used[j]:
                        nxt = (j, e); break
                if nxt is None: break
                j, e = nxt; used[j] = True
                q = S[j, 1 - e]
                if fwd: line.append(q)
                else: line.insert(0, q)
        out.append(np.array(line))
    return out


def rdp(P, eps):
    """かどを へらす（Ramer–Douglas–Peucker）"""
    if len(P) < 3: return P
    a, b = P[0], P[-1]
    ab = b - a; L = np.linalg.norm(ab)
    if L < 1e-12:
        d = np.linalg.norm(P - a, axis=1)
    else:
        d = np.abs(ab[0] * (P[:, 1] - a[1]) - ab[1] * (P[:, 0] - a[0])) / L
    k = int(d.argmax())
    if d[k] > eps:
        l = rdp(P[:k + 1], eps); r = rdp(P[k:], eps)
        return np.vstack([l[:-1], r])
    return np.array([a, b])


def simplify(P, eps):
    closed = np.linalg.norm(P[0] - P[-1]) < 1e-4
    if closed and len(P) > 4:      # 閉じた 線：いちばん 遠い 2点で 分けて から
        c = P[:-1]; k = int(np.linalg.norm(c - c[0], axis=1).argmax())
        a = rdp(c[:k + 1], eps); b = rdp(np.vstack([c[k:], c[:1]]), eps)
        return np.vstack([a[:-1], b])
    return rdp(P, eps)


def loops(z0, box=BOX, minlen=0.01):
    js, binb = read_glb(SL.V2)
    pos, uv, nrm, idx = arrays(js, binb)
    S = SL.slice_z(pos, idx, z0, box)
    L = chain(S)
    res = []
    for P in L:
        ln = float(np.linalg.norm(np.diff(P, axis=0), axis=1).sum())
        if ln < minlen: continue
        res.append(P)
    return res


if __name__ == '__main__':
    from PIL import Image, ImageDraw
    K = 2200; box = BOX
    W, H = int((box[1] - box[0]) * K), int((box[3] - box[2]) * K)
    im = Image.new('RGB', (W, H), 'white'); dr = ImageDraw.Draw(im)
    T = lambda p: ((p[0] - box[0]) * K, (box[3] - p[1]) * K)
    for z0, col in ((ZL, (230, 150, 150)), (ZC, (30, 90, 200))):
        L = loops(z0)
        print('z', z0, 'lines', len(L))
        for i, P in enumerate(sorted(L, key=lambda P: -len(P))):
            closed = np.linalg.norm(P[0] - P[-1]) < 1e-4
            Q = simplify(P, 0.0012)
            c = P.mean(0)
            if z0 == ZC:
                print(f'  {i:2d} pts {len(P):4d} → {len(Q):3d} closed {closed} bbox x[{P[:,0].min():+.3f},{P[:,0].max():+.3f}] y[{P[:,1].min():+.3f},{P[:,1].max():+.3f}]')
            dr.line([T(p) for p in Q], fill=col, width=3 if z0 == ZC else 2)
            if z0 == ZC:
                for p in Q: dr.ellipse((T(p)[0] - 4, T(p)[1] - 4, T(p)[0] + 4, T(p)[1] + 4), outline=(0, 0, 0))
    im.save(ROOT + '/out/look/world.png'); print(im.size)
