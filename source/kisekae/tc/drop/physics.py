# 玉の 落ち方：2D の 物理（玉＝円・台＝折れ線）で たくさん 落として、自然な ものを えらぶ
import sys, json, math
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from dp_env import ROOT
import numpy as np
import world as WD

R = WD.R_BALL
G = 2.6                    # 重力（台の 単位／秒²）：見て 気持ちの いい 速さ
DT = 1 / 1200
import os
E_PEG, E_CUP, E_RING, E_WALL = float(os.environ.get('E_PEG', '0.46')), 0.22, 0.30, 0.35       # はね返り
MU = 0.22                  # まさつ
DRAG = 0.12                # 空気・盤の ていこう（1/秒）
LCD = (-0.0008, -0.2746, 0.123)       # 液晶の 輪（外の 半径）
WALL_X = 0.462
START = (0.004, 0.333)     # 受け皿の 出口（ポケットの 中で 止まって いる 所）
CUP_X = [(-0.454, -0.284), (-0.278, -0.107), (0.106, 0.276), (0.283, 0.453)]
RIM_Y = -0.188
CUP_FLOOR = -0.297


def build():
    """台の 線分：A（始点）・B（終点）・e（はね返り）・kind（0 釘・1 コップ・2 輪・3 かべ・4 出口）・id"""
    L = WD.loops(WD.ZC)
    segs = []
    pegs, cups, spout = [], [], None
    for P in L:
        x0, x1, y0, y1 = P[:, 0].min(), P[:, 0].max(), P[:, 1].min(), P[:, 1].max()
        closed = np.linalg.norm(P[0] - P[-1]) < 1e-4
        if y1 > 0.40 and not closed and x1 - x0 > 0.3:
            spout = WD.simplify(P, 0.0012); continue          # 受け皿と 出口の 外がわ
        if y0 > 0.29 and closed and abs((x0 + x1) / 2) < 0.02:
            continue                                           # 出口の ポケットの 内がわ（玉は ここから とび出す）
        if y1 < -0.15 and closed and x1 - x0 > 0.12:
            Q = WD.simplify(P, 0.0012).copy()
            # コップの 中の 底：前（手前）へ 行くほど 深い（z=0.10 の 切り口では y −0.293）。玉は 前の 深い 所へ ころがって 前の かべの うしろに かくれる
            fl = (Q[:, 1] > -0.28) & (Q[:, 1] < -0.255) & (np.abs(Q[:, 0] - Q[:, 0].mean()) < 0.06)
            Q[fl, 1] = CUP_FLOOR
            cups.append(Q); continue
        if closed and x1 - x0 < 0.06 and y0 > -0.14 and y1 < 0.29 and abs((x0 + x1) / 2) < 0.42:
            pegs.append(WD.simplify(P, 0.0012)); continue
    pegs.sort(key=lambda P: (-round(P[:, 1].mean() / 0.04), P[:, 0].mean()))
    cups.sort(key=lambda P: P[:, 0].mean())
    assert len(pegs) == 18 and len(cups) == 4 and spout is not None, (len(pegs), len(cups))

    def add(P, e, kind, i, close):
        Q = np.vstack([P, P[:1]]) if close and np.linalg.norm(P[0] - P[-1]) > 1e-6 else P
        for a, b in zip(Q[:-1], Q[1:]):
            if np.linalg.norm(b - a) > 1e-7:
                segs.append((a[0], a[1], b[0], b[1], e, kind, i))
    for i, P in enumerate(pegs): add(P, E_PEG, 0, i, True)
    for i, P in enumerate(cups): add(P, E_CUP, 1, i, True)
    th = np.linspace(math.radians(8), math.radians(172), 41)
    ring = np.c_[LCD[0] + LCD[2] * np.cos(th), LCD[1] + LCD[2] * np.sin(th)]
    add(ring, E_RING, 2, 0, False)
    for s in (-1, 1):
        add(np.array([[s * WALL_X, 0.42], [s * WALL_X, -0.36]]), E_WALL, 3, 0 if s < 0 else 1, False)
    sp = spout[(spout[:, 1] < 0.41)]
    add(sp, E_WALL, 4, 0, False)
    S = np.array(segs, float)
    return dict(S=S, pegs=pegs, cups=cups, spout=spout, ring=ring)


def sim(Wd, vx0, vy0, seed, x0=None, tmax=9.0, jit=0.035):
    """1こ 落とす → dict（t・x・y・角度・当たった 所・入った コップ…）か None（とちゅうで 止まった など）"""
    S = Wd['S']; A = S[:, 0:2]; B = S[:, 2:4]; AB = B - A; L2 = (AB ** 2).sum(1)
    Es = S[:, 4]; Ks = S[:, 5].astype(int); Is = S[:, 6].astype(int)
    rng = np.random.default_rng(seed)
    p = np.array([START[0] if x0 is None else x0, START[1]], float); v = np.array([vx0, vy0], float); w = 0.0; ang = 0.0
    out = True                       # まだ 出口の 上（出口の 線は 見ない）
    T, X, Y, AN = [], [], [], []
    hits = []; last_hit = {}
    slow_t = 0.0; t = 0.0; n = 0; tin = None; rest_t = 0.0
    while t < tmax:
        v[1] -= G * DT
        v *= (1 - DRAG * DT)
        p = p + v * DT
        ang += w * DT
        if out and p[1] < 0.262:
            out = False
            if abs(p[0]) > 0.080: return None         # 出口の 下の ふちから 出て いない（横の かべを こえた）
        for _ in range(3):
            d = p - A
            u = np.clip((d * AB).sum(1) / L2, 0, 1)
            c = A + AB * u[:, None]
            dv = p - c; dist = np.sqrt((dv ** 2).sum(1))
            if out: dist = np.where(Ks == 4, 9.0, dist)
            k = int(dist.argmin())
            if dist[k] >= R: break
            nrm = dv[k] / max(dist[k], 1e-9)
            p = c[k] + nrm * R
            vn = float(v @ nrm)
            if vn < 0:
                tg = np.array([-nrm[1], nrm[0]])
                vt = float(v @ tg)
                e = Es[k] if -vn > 0.10 else 0.0
                jn = -(1 + e) * vn
                rel = vt + w * R                      # 当たった 点の すべる 速さ
                jt = -rel * 2 / 7
                lim = MU * jn
                jt = max(-lim, min(lim, jt))
                v = v + nrm * jn + tg * jt
                w += jt * 2.5 / R
                if -vn > 0.16:
                    if jit and Ks[k] == 0:           # 釘：ほんの 少し ばらつく（きれいすぎない）
                        a = rng.normal(0, jit); ca, sa = math.cos(a), math.sin(a)
                        v = np.array([v[0] * ca - v[1] * sa, v[0] * sa + v[1] * ca]) * (1 + rng.normal(0, 0.02))
                    key = (int(Ks[k]), int(Is[k]))
                    if t - last_hit.get(key, -9) > 0.07:
                        hits.append((round(t, 4), int(Ks[k]), int(Is[k]), round(-vn, 3)))
                    last_hit[key] = t
        if n % 20 == 0:
            T.append(t); X.append(p[0]); Y.append(p[1]); AN.append(ang)
        sp = math.hypot(v[0], v[1])
        cup = next((i for i, (a, b) in enumerate(CUP_X) if a < p[0] < b), None)
        inside = cup is not None and p[1] < RIM_Y - 0.012
        if inside and tin is None: tin = (t, cup)
        if not inside: tin = None
        if sp < 0.035:
            slow_t += DT
            if inside:
                rest_t += DT
                if rest_t > 0.22: break
            elif slow_t > 0.5: return None            # コップの 外で 止まった
        else:
            slow_t = 0.0; rest_t = 0.0
        t += DT; n += 1
    else:
        return None
    if tin is None: return None
    return dict(t=np.array(T), x=np.array(X), y=np.array(Y), a=np.array(AN), hits=hits, cup=tin[1], tin=tin[0], dur=t, vx0=vx0, vy0=vy0, seed=seed, x0=p[0])


if __name__ == '__main__':
    Wd = build()
    print('segments', len(Wd['S']))
    rng = np.random.default_rng(11)
    res = []; bad = 0
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    import time; t0 = time.time()
    for i in range(N):
        vx = float(rng.uniform(-0.46, 0.30)); vy = float(rng.uniform(0.12, 0.30))
        r = sim(Wd, vx, vy, i)
        if r is None: bad += 1; continue
        res.append(r)
    print('ok', len(res), 'bad', bad, round(time.time() - t0, 1), 's')
    cups = np.bincount([r['cup'] for r in res], minlength=4); print('cups', cups)
    du = np.array([r['dur'] for r in res]); ti = np.array([r['tin'] for r in res])
    print('dur p10/50/90', np.percentile(du, [10, 50, 90]).round(2), 'tin p10/50/90', np.percentile(ti, [10, 50, 90]).round(2))
    nh = np.array([sum(1 for h in r['hits'] if h[1] == 0) for r in res]); print('peg hits p10/50/90', np.percentile(nh, [10, 50, 90]))
    import pickle; pickle.dump(dict(res=res), open(sys.argv[2] if len(sys.argv) > 2 else ROOT + '/out/look/sims.pkl', 'wb'))
