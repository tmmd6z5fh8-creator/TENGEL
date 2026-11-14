# たくさん 落とした 中から、自然な 落ち方を コップごとに えらぶ
import sys, pickle, math
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import numpy as np
import physics as PH


def feats(r):
    t, x, y = r['t'], r['x'], r['y']
    vx, vy = np.gradient(x, t), np.gradient(y, t)
    sp = np.hypot(vx, vy)
    pre = t < r['tin']
    # とちゅうで 止まりかける 長さ（コップに 入る 前・出だしの 0.25秒は 見ない）
    slow = (sp < 0.16) & pre & (t > 0.25)
    run = 0; best = 0
    for s in slow:
        run = run + 1 if s else 0; best = max(best, run)
    stall = best / 60
    hits = r['hits']
    npeg = sum(1 for h in hits if h[1] == 0 and h[0] < r['tin'])
    ncup = sum(1 for h in hits if h[1] == 1 and h[0] < r['tin'])
    nring = sum(1 for h in hits if h[1] == 2)
    nwall = sum(1 for h in hits if h[1] == 3)
    nsp = sum(1 for h in hits if h[1] == 4)
    # はね上がり：釘に 当たった あとに 上がった 高さの 最大
    up = 0.0
    k0 = int(np.searchsorted(t, 0.35))
    lo = y[k0]
    for i in range(k0, len(y)):
        lo = min(lo, y[i]); up = max(up, y[i] - lo)
    seq = tuple(h[2] for h in hits if h[1] == 0 and h[0] < r['tin'])
    # コップの 中で 落ちつく までの 長さ
    settle = r['dur'] - r['tin']
    return dict(stall=stall, npeg=npeg, ncup=ncup, nring=nring, nwall=nwall, nsp=nsp, up=up, seq=seq, settle=settle, dur=r['dur'], tin=r['tin'], vmax=float(sp.max()))


def ok(f):
    return (1.25 <= f['tin'] <= 2.7 and f['dur'] <= 3.7 and f['stall'] <= 0.22 and 3 <= f['npeg'] <= 8 and f['ncup'] <= 3 and f['nring'] <= 2 and f['nwall'] <= 1 and f['nsp'] == 0
            and f['up'] <= 0.085 and f['settle'] <= 1.25)


if __name__ == '__main__':
    res = []
    for p in sys.argv[1:]:
        res += pickle.load(open(p, 'rb'))['res']
    print('sims', len(res))
    F = [feats(r) for r in res]
    for c in range(4):
        idx = [i for i, r in enumerate(res) if r['cup'] == c]
        good = [i for i in idx if ok(F[i])]
        print(f'cup {c}: {len(idx)} → good {len(good)}')
        if c == 0:
            for i in idx:
                f = F[i]; print('   ', {k: (round(v, 3) if isinstance(v, float) else v) for k, v in f.items()}, 'OK' if ok(f) else '')


def xsig(r, levels=(0.22, 0.15, 0.08, 0.01, -0.06, -0.13)):
    """高さごとの 横の 場所（はじめて その 高さを 通る とき）＝落ち方の しるし"""
    out = []
    for lv in levels:
        k = np.nonzero(r['y'] < lv)[0]
        out.append(r['x'][k[0]] if len(k) else r['x'][-1])
    return np.array(out)


def choose(res, n_per=4, seed=3):
    F = [feats(r) for r in res]
    picks = []
    rng = np.random.default_rng(seed)
    for c in range(4):
        idx = [i for i, r in enumerate(res) if r['cup'] == c and ok(F[i])]
        # ふつうの 落ち方を 先に（釘 4〜6回・止まりかけ なし）
        pref = [i for i in idx if 4 <= F[i]['npeg'] <= 7 and F[i]['stall'] <= 0.12 and F[i]['ncup'] <= 2] or idx
        sig = {i: xsig(res[i]) for i in pref}
        first = pref[int(rng.integers(len(pref)))]
        got = [first]
        while len(got) < n_per and len(got) < len(pref):
            best, bd = None, -1
            for i in pref:
                if i in got: continue
                d = min(float(np.abs(sig[i] - sig[j]).mean()) + 0.08 * abs(F[i]['tin'] - F[j]['tin']) + (0.03 if F[i]['seq'][:3] != F[j]['seq'][:3] else 0) for j in got)
                if d > bd: best, bd = i, d
            got.append(best)
        picks.append(got)
    return picks, F
