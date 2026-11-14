# 見くらべの 絵の もと（元・直し・釘の 長さの 見本）を 描く
import sys
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from dp_env import ROOT
from common import *
import view as V
import pegs as PG
import glb as GLB
from PIL import Image
OUT = ROOT + '/out/sheet/'
import os
os.makedirs(OUT, exist_ok=True)
VIEWS = dict(peg=(-58, 6, 1.9, (0.0, 0.05, 0.03), 800, 1000), eyet=(-28, 50, 0.62, (-0.03, 0.83, 0.09), 800, 800), eyef=(0, 4, 0.62, (-0.03, 0.82, 0.09), 800, 800), all=(-32, 12, 4.5, (0.0, 0.0, 0.0), 900, 1400))


def go(prims, tag, names):
    for n in names:
        az, el, dist, tgt, W, H = VIEWS[n]
        img = V.shot(prims, az, el, dist, tgt, 28, W, H)
        Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)).save(f'{OUT}{tag}_{n}.png')
        print(tag, n)


m = GLB.load(ORIG); prims = m.flatten()
go(prims, 'orig', ['peg', 'eyet', 'eyef', 'all'])
p0 = prims[0]
P = p0.pos.astype(np.float64).copy(); N = p0.nrm.astype(np.float64).copy()
pegs = PG.find_pegs()
for k in (1.5, 2.5):
    P2, N2, mv, log = PG.stretch(P, N, pegs, k)
    p0.pos, p0.nrm = P2.astype(np.float32), N2.astype(np.float32)
    go(prims, f'k{k}', ['peg'])
del m, prims
m = GLB.load(ROOT + '/out/Tenger_Lucky_Drop_v2.glb'); prims = m.flatten()
go(prims, 'v2', ['peg', 'eyet', 'eyef', 'all'])
