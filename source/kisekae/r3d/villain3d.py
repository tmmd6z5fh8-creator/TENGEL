"""ヴィラン：赤い月を背に後ろ足で立つ黒馬（3D）を描いて、合成用のデータを保存する
   python3 villain3d.py <出力の頭> <倍率 0.5/1> [ss]"""
import sys, os, time, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from h3d import Scene, nrm
import horse3d as H

out = sys.argv[1]
scale = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
ss = int(sys.argv[3]) if len(sys.argv) > 3 else 1
W, Hh = int(round(780 * scale)), int(round(1688 * scale))

pose = dict(H.REAR)
S0 = H.skeleton(pose)
gy = S0['ground']
EYE = np.array((2.1, 0.45 + gy, 8.4))
TGT = np.array((-0.02, 1.62 + gy, 0.0))
FOV = 30

sc = Scene()
sc.image(W, Hh, ss)
sc.camera(EYE, TGT, FOV)
sc.bounce(1)
cam_dir = nrm(EYE - TGT)
moon_dir = nrm(-cam_dir + np.array([0.05, 0.42, 0.0]))
# 環境：赤黒い空・うしろに赤い月・右うしろに稲妻
sc.env((0.035, 0.004, 0.005), (0.07, 0.008, 0.008), (0.006, 0.001, 0.001), (0.001, 0.0002, 0.0002))
sc.lobe(moon_dir, (3.2, 0.55, 0.28), 5.0)                                  # 月のまわりの赤い光
sc.lobe(nrm((0.75, 0.55, -0.4)), (0.9, 0.95, 1.25), 24.0)                   # 稲妻の白い光
sc.lobe((0.0, 1.0, 0.0), (0.16, 0.02, 0.02), 2.0)                           # 上の赤い空
sc.light(moon_dir, (7.5, 1.5, 0.75), 8, 0)                                  # 月（うしろから・ふちの光）
sc.light(nrm((0.8, 0.6, -0.45)), (2.4, 2.5, 3.2), 8, 0)                      # 稲妻（右うしろの冷たいふち）
sc.light(nrm(cam_dir + np.array([0, 0.35, 0])), (0.09, 0.022, 0.022), 12, 1)  # 前からの弱い赤

# 素材：つやのある黒い毛・光らない黒い目・黒いひづめ
sc.mat(1, 1, (0.014, 0.011, 0.011), 0.30, 0.35, 0.45, 6.0)
sc.mat(5, 1, (0.004, 0.003, 0.003), 0.05, 0.0, 0.4)
sc.mat(6, 1, (0.02, 0.017, 0.015), 0.45, 0.3, 0.4)

S = H.build(sc, pose, mats=dict(body=1, neck=1, hoof=6, eye=5, head=1))
t0 = time.time()
R = sc.render(out)
print(f'render {time.time() - t0:.1f}s  {W}x{Hh} ss{ss}')


def P(pts):
    xy, z = sc.project(np.asarray(pts, float))
    return xy.tolist()


ts = np.linspace(0, 1, 48)
crest = H.bez(S['crest'], ts)
throat = H.bez(S['throat'], ts)
marks = dict(
    crest=P(np.c_[crest, np.zeros(len(ts))]),
    throat=P(np.c_[throat, np.zeros(len(ts))]),
    poll=P([H.v3(S['poll'])]),
    tail=P([H.v3(p) for p in S['tail_pts']]),
    eye=P([S['eye']]),
    hooves=P([H.v3(S[k]['hf'], 0.15 * S[k]['z']) for k in ('FL', 'FR', 'HL', 'HR')]),
    ground=P([np.array([x, gy, 0.0]) for x in np.linspace(-3, 3, 13)]),
    moon_dir=moon_dir.tolist(),
    W=W, H=Hh,
)
json.dump(marks, open(out + '_marks.json', 'w'))
