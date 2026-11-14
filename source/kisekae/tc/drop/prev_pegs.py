# 釘の 長さの 見本（元・1.5倍・2倍・2.5倍）を 同じ 向きで 描く
import sys
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from dp_env import ROOT
from common import *
import view as V
import pegs as PG
import glb as GLB
from PIL import Image
m = GLB.load(ORIG); prims = m.flatten()
p0 = prims[0]
P = p0.pos.astype(np.float64).copy(); N = p0.nrm.astype(np.float64).copy()
pegs = json.load(open(ROOT + '/out/pegs_orig.json'))
out = ROOT + '/out/look/'
for k in [float(x) for x in sys.argv[1:]]:
    if k == 1.0:
        p0.pos, p0.nrm = P.astype(np.float32), N.astype(np.float32)
    else:
        P2, N2, mv, log = PG.stretch(P, N, pegs, k)
        p0.pos, p0.nrm = P2.astype(np.float32), N2.astype(np.float32)
        print(k, 'moved', int(mv.sum()), 'tips', round(min(l['height_after'] for l in log), 4), round(max(l['height_after'] for l in log), 4), 'partial', sum(l['partial'] for l in log))
    for vn, (az, el, dist, tgt, W, H) in dict(s=(62, 8, 1.75, (0.0, 0.05, 0.03), 800, 1000), q=(-35, 22, 1.5, (0.0, 0.07, 0.03), 1000, 800), f=(0, 0, 1.75, (0.0, 0.05, 0.03), 1000, 800)).items():
        img = V.shot(prims, az, el, dist, tgt, 28, W, H)
        Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)).save(f'{out}k{k:.1f}_{vn}.png')
print('ok')
