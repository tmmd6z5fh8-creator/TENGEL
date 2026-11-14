# いちばん 左の コップに 入る 落ち方を ねらって さがす（入った ものの 近くの 出だしを ためす）
import sys, pickle, time
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from dp_env import ROOT
import numpy as np
import physics as PH
import pick as PK
res = pickle.load(open(ROOT + '/out/look/sims_big.pkl', 'rb'))['res']
c0 = [r for r in res if r['cup'] == 0]
for r in c0:
    print('vx0', round(r['vx0'], 4), 'vy0', round(r['vy0'], 4), 'seed', r['seed'], 'tin', round(r['tin'], 2))
Wd = PH.build()
rng = np.random.default_rng(77)
out = []; n = 0; t0 = time.time()
N = int(sys.argv[1])
# 左へ 行く 出だしを 広く：釘 1 の 左を 通る（vx が マイナスで 大きい）ものと、右の 面に 当たって から 左へ もどる もの
while n < N:
    base = c0[int(rng.integers(len(c0)))] if rng.random() < 0.6 else None
    if base is not None:
        vx = base['vx0'] + rng.normal(0, 0.012); vy = base['vy0'] + rng.normal(0, 0.012)
    else:
        vx = float(rng.uniform(-0.46, -0.20)); vy = float(rng.uniform(0.12, 0.30))
    r = PH.sim(Wd, float(vx), float(vy), 100000 + n); n += 1
    if r is not None and r['cup'] == 0: out.append(r)
print('tried', N, 'cup0', len(out), round(time.time() - t0, 1), 's', 'good', sum(1 for r in out if PK.ok(PK.feats(r))))
pickle.dump(dict(res=out), open(ROOT + '/out/look/sims_c0.pkl', 'wb'))
