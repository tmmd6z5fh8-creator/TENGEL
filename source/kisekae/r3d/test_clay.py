"""粘土の色で馬の形だけを確かめる（横・斜め前・斜め後ろ）"""
import sys, os, time, json
import numpy as np
import cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from h3d import Scene, tonemap
import horse3d as H

out = sys.argv[1]
pose_name = sys.argv[2] if len(sys.argv) > 2 else 'STAND'
pose = getattr(H, pose_name) if hasattr(H, pose_name) else json.load(open(pose_name))
views = [((0.05, 1.25, 7.0), (0.05, 1.25, 0)), ((3.6, 1.1, 5.2), (0.15, 1.3, 0)), ((-3.8, 1.4, 4.6), (-0.1, 1.2, 0))]
tiles = []
for i, (eye, tgt) in enumerate(views):
    sc = Scene()
    sc.image(420, 420, 1)
    S = H.skeleton(pose)
    gy = S['ground']
    sc.camera(np.array(eye) + (0, gy, 0), np.array(tgt) + (0, gy, 0), 32)
    sc.env((0.35, 0.37, 0.42), (0.25, 0.24, 0.23), (0.10, 0.09, 0.08))
    sc.light((0.5, 0.8, 0.6), (2.6, 2.5, 2.3), 10, 1)
    sc.light((-0.6, 0.3, -0.5), (0.6, 0.6, 0.7), 10, 0)
    sc.mat(1, 1, (0.55, 0.52, 0.48), 0.55)
    sc.mat(5, 1, (0.02, 0.02, 0.02), 0.1)
    H.build(sc, pose)
    t0 = time.time()
    R = sc.render(f'{out}_v{i}')
    print('view', i, f'{time.time() - t0:.1f}s')
    img = tonemap(R['rgb'] + (1 - R['a'][..., None]) * np.array([0.16, 0.17, 0.19]), 1.0)
    tiles.append((img * 255).astype(np.uint8))
cv2.imwrite(out + '.png', cv2.cvtColor(np.concatenate(tiles, 1), cv2.COLOR_RGB2BGR))
print(out + '.png')
