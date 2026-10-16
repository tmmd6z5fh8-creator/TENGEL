"""黄金の炎：金の馬（3D）を描いて、合成用のデータ（色・アルファ・奥行き・目印）を保存する
   python3 gold3d.py <出力の頭> <倍率 0.5/1> [ss]"""
import sys, os, time, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from h3d import Scene, nrm
import horse3d as H
import armor3d

out = sys.argv[1]
scale = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
ss = int(sys.argv[3]) if len(sys.argv) > 3 else 1
W, Hh = int(round(780 * scale)), int(round(1688 * scale))

pose = dict(H.PRANCE)
pose['head_ang'] = -62.0
S0 = H.skeleton(pose)
gy = S0['ground']
EYE = np.array((4.7, 0.62 + gy, 5.2))
TGT = np.array((0.30, 1.42 + gy, 0.0))
FOV = 34

sc = Scene()
sc.image(W, Hh, ss)
sc.camera(EYE, TGT, FOV)
sc.bounce(1)
# 環境：暗い中に、上と手前の柔らかい明かり・うしろの炎・下の金の照り返し（磨いた金が映すもの）
sc.env((0.03, 0.012, 0.003), (0.008, 0.0035, 0.001), (0.02, 0.01, 0.002), (0.002, 0.001, 0.0002))
cam_dir = nrm(EYE - TGT)
sc.lobe((0.2, 1.0, 0.3), (2.2, 1.6, 0.95), 6.0)                          # 上の大きな明かり
sc.lobe((0.7, 0.35, 0.6), (6.0, 4.6, 3.0), 26.0)                         # 手前右の明かり
sc.lobe(-cam_dir + np.array([0, 0.45, 0]), (2.4, 0.95, 0.2), 3.0)        # うしろの炎
sc.lobe((-0.85, 0.3, 0.35), (1.6, 0.9, 0.32), 14.0)                      # 左のふちの明かり
sc.lobe((0.0, -1.0, 0.1), (0.7, 0.38, 0.08), 3.0)                        # 下の照り返し
sc.lobe(cam_dir + np.array([0, 0.25, 0]), (0.5, 0.36, 0.19), 5.0)        # カメラのうしろの大きな柔らかい明かり
sc.light((0.55, 0.75, 0.45), (3.0, 2.6, 2.0), 14, 1)                     # 主光
sc.light((-0.5, 0.55, -0.68), (6.0, 2.5, 0.6), 10, 0)                    # うしろの炎のふち
sc.light((0.15, -0.9, 0.45), (0.4, 0.22, 0.06), 8, 0)                    # 下から

# 素材
GOLD = (1.0, 0.71, 0.29)
sc.mat(1, 0, GOLD, 0.2, 0, 0, 0.0)                         # 体の金
sc.bump(1, 1, 5.0, 0.004)
sc.mat(2, 0, (1.0, 0.72, 0.28), 0.2, 0, 0, 0.0)            # 首のうろこ
a = H.bez(S0['crest'], 0.1); b = H.bez(S0['crest'], 0.95)
sc.bump(2, 2, 0.042, 0.2, H.v3(a), H.v3(b - a), (0, 0, 1), 0.16)
sc.mat(3, 0, (1.0, 0.80, 0.42), 0.14, 0, 0, 5.0)           # よろい
sc.bump(3, 3, 3.2, 0.012)
sc.mat(4, 2, (0.05, 0.16, 0.95), 0.03, 0.30, 1.0)          # サファイア
sc.mat(5, 1, (0.006, 0.004, 0.002), 0.06, 0.0, 0.3)        # 目（光らない・つやのある黒）
sc.mat(6, 0, (0.85, 0.55, 0.22), 0.32, 0, 0, 9.0)          # ひづめ（濃い金）
sc.mat(7, 0, (1.0, 0.82, 0.45), 0.10, 0, 0, 0)             # 縁取り（よく磨いた金）

S = H.build(sc, pose, mats=dict(body=1, neck=2, hoof=6, eye=5, head=1))
gems = armor3d.build(sc, pose, S)
t0 = time.time()
R = sc.render(out)
print(f'render {time.time() - t0:.1f}s  {W}x{Hh} ss{ss}')

# 合成に使う目印（画素）
def P(pts):
    xy, z = sc.project(np.asarray(pts, float))
    return xy.tolist()
ts = np.linspace(0, 1, 40)
crest = H.bez(S['crest'], ts)
marks = dict(
    crest=P(np.c_[crest, np.zeros(len(ts))]),
    crest_z=P(np.c_[crest, np.full(len(ts), 0.06)]),
    poll=P([H.v3(S['poll'])]),
    tail=P([H.v3(p) for p in S['tail_pts']]),
    eye=P([S['eye']]),
    hooves=P([H.v3(S[k]['hf'], 0.15 * S[k]['z']) for k in ('FL', 'FR', 'HL', 'HR')]),
    gems=P([g[0] for g in gems]),
    W=W, H=Hh,
)
json.dump(marks, open(out + '_marks.json', 'w'))
