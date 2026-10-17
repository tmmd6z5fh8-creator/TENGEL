"""ボードを持つ馬：ポーズとカメラのお試し（低い解像度で並べる）"""
import sys, os, math, json
import numpy as np, cv2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from style2d import *
import horse3d as Hm

out = sys.argv[1]
cands = json.loads(sys.argv[2])
W, Hh = 300, 380
tiles = []
for i, c in enumerate(cands):
    pose = dict(Hm.REAR)
    pose.update(theta=c.get('theta', 62), neck_rot=c.get('neck', -40), head_ang=c.get('head', -40), fore_spread=c.get('spread', 1.0))
    pose['fore'] = dict(L=c['fl'], R=c['fr'])
    pose['hind'] = dict(L=c.get('hl', [-58, -112, -86, -60]), R=c.get('hr', [-64, -118, -90, -62]))
    rgb, a, R = horse_illust(pose, (30, 40, 270, 360), W, Hh, facing='left', azim=c.get('azim', 45), elev=c.get('elev', 6),
                             body=('#C27237', '#8E4A21'), mane=('#5A2E14', '#3E1E0C'), line='#4A2614', mode='stand', hoof='#3A2A22',
                             eye='#1A1008', ss=1, name=f'ht{i}', mane_scale=1.2, tail_len=0.9)
    bg = np.ones((Hh, W, 3), np.float32) * 0.93
    img = over(bg, rgb, a)
    # 前足のひづめの位置（広げた分も入れて）
    S = R['S']; sc = R['scene']
    sp = pose.get('fore_spread', 1.0)
    for k in ('FL', 'FR'):
        z = S[k]['z'] * 0.155 * 0.9 * (1 + (sp - 1) * 0.9)
        p = sc.project(np.array([[S[k]['hf'][0], S[k]['hf'][1], z]]))[0][0]
        cv2.circle(img, (int(p[0]), int(p[1])), 5, (1, 0, 0), -1)
    img[4:10, 4:4 + 8 * (i + 1)] = (0, 0, 0)
    tiles.append(img)
sheet = np.concatenate(tiles, axis=1)
save_png(np.clip(sheet, 0, 1), out)
print(out)
