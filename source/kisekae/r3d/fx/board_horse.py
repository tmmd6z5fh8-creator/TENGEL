"""ボードを持つ馬（的中ボタンを押したあとに出る絵）
   python3 fx/board_horse.py <出力フォルダ> [名前] [JSON設定]
   → <名前>_back.png（馬ぜんぶ）・<名前>_front.png（ボードの上にかぶさる前足の先だけ）・<名前>_preview.png・<名前>.json（ボードの四角）
   アプリでは「うしろの馬 → ボード（HTMLの文字）→ 前足の先」の順に重ねる"""
import sys, os, math, json
import numpy as np, cv2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from style2d import *
import horse3d as Hm

out = sys.argv[1]
name = sys.argv[2] if len(sys.argv) > 2 else 'horse_board'
cfg = dict(theta=68, azim=42, elev=6, neck=-44, head=-30, fl=[-48, 12, 88, -40], fr=[-40, 22, 92, -45], spread=2.2,
           body=['#C27237', '#9A5327'], mane=['#5A2E14', '#3E1E0C'], line='#4A2614', hoof='#3A2A22', light=[0.55, 0.75, -0.55],
           bands=[0.02, 0.72], hi=None, W=720, H=900, box=[290, 30, 700, 880], board=[24, 0, 696, 0], board_h=440, ss=2,
           head_scale=1.22, top_pad=6, eye_k=0.10, mane_len=1.0, seed=7)
if len(sys.argv) > 3:
    cfg.update(json.loads(sys.argv[3]))
os.makedirs(out, exist_ok=True)
Hm.HEAD_SCALE = cfg['head_scale']
W, Hh = cfg['W'], cfg['H']
rng = np.random.default_rng(cfg['seed'])

pose = dict(Hm.REAR)
pose.update(theta=cfg['theta'], neck_rot=cfg['neck'], head_ang=cfg['head'], fore_spread=cfg['spread'])
pose['fore'] = dict(L=cfg['fl'], R=cfg['fr'])
pose['hind'] = dict(L=[-58, -112, -86, -60], R=[-64, -118, -90, -62])

e, t = frame_horse(pose, tuple(cfg['box']), W, Hh, facing='left', azim=cfg['azim'], elev=cfg['elev'], fov=26)
R = render_horse(pose, e, t, 26, W, Hh, ss=cfg['ss'], name=name)
A = R['a']
rgb = cel(R, cfg['body'][0], cfg['body'][1], light=tuple(cfg['light']), bands=tuple(cfg['bands']), hi=cfg['hi'], eye='#1A1008', hoof=cfg['hoof'])
rgb = draw_eye(rgb, R, '#1A1008', k=cfg['eye_k'])

# ---- たてがみ：首のうしろの縁にそって垂れる房（首のまん中に線が出ないように） ----
crest, throat = np.asarray(R['crest']), np.asarray(R['throat'])
polys_a, polys_b = [], []
n = len(crest)
for i in range(4, n - 6, 2):
    c = crest[i]
    v = c - throat[i]
    v = v / (np.linalg.norm(v) + 1e-9)
    p = c.copy()
    for _ in range(200):                                  # 首の外の縁まで進む
        q = p + v
        xi, yi = int(round(q[0])), int(round(q[1]))
        if not (0 <= xi < W and 0 <= yi < Hh) or A[yi, xi] < 0.5:
            break
        p = q
    tt = i / n
    L = (34 + 20 * math.sin(tt * math.pi)) * cfg['mane_len']
    ang = math.atan2(v[1], v[0])
    ang = ang + (math.pi / 2 - ang) * 0.78                # 外へ少し出て、首にそって下へ垂れる
    start = p - v * 10
    pts = flow(start, ang, L, 9, wind=0.0, rng=rng, wave=0.5, phase=i)
    (polys_a if (i // 2) % 2 == 0 else polys_b).append(lock_poly(pts, 19, 1.0))
# 前髪
pp = np.asarray(R['poll'], float)
mz = np.asarray(R['muzzle'], float)
fd = (mz - pp) / (np.linalg.norm(mz - pp) + 1e-9)
ear_side = np.array([fd[1], -fd[0]])                     # 前髪は耳のあいだから、目にかからない向きへ
if np.dot(ear_side, np.asarray(R['eye'], float) - pp) > 0:
    ear_side = -ear_side
for k in range(2):
    a0 = math.atan2(fd[1], fd[0]) + 0.55 * math.copysign(1, fd[0] * ear_side[1] - fd[1] * ear_side[0]) + (k - 0.5) * 0.25
    pts = flow(pp + ear_side * 4 + rng.normal(0, 1.0, 2), a0, 20, 6, wind=0.0)
    (polys_a if k == 0 else polys_b).append(lock_poly(pts, 10, 1.0))
# しっぽ（体のうしろへ垂れる）
tl = np.asarray(R['tail'], float)
base_ang = math.atan2(*(tl[-1] - tl[0])[::-1])
for k in range(5):
    a0 = base_ang + (k - 2) * 0.14
    pts = flow(tl[0] + (tl[1] - tl[0]) * 0.3, a0, (120 + k * 10) * 0.9, 12, wind=0.1, wind_ang=math.pi / 2, rng=rng, wave=0.8, phase=k)
    (polys_a if k % 2 == 0 else polys_b).append(lock_poly(pts, 30, 1.5))
hair_m = poly_aa((Hh, W), polys_a)
hair_s = poly_aa((Hh, W), polys_b)
ft_a = np.zeros((Hh, W), np.float32); ft_rgb = np.zeros((Hh, W, 3), np.float32)
c1, c2 = hexc(cfg['mane'][0]), hexc(cfg['mane'][1])
mane_rgb = c1 * hair_m[..., None] + c2 * (hair_s * (1 - hair_m))[..., None]
mane_a = np.clip(hair_m + hair_s, 0, 1)
mane_rgb = np.where(mane_a[..., None] > 0, mane_rgb / np.maximum(mane_a, 1e-4)[..., None], 0)
# たてがみは首の「うしろ」に（体に重なる所は体が前）
mane_a = mane_a * (1 - (A > 0.5) * 0.0)

ln = edges(R, width=3) * np.clip(A, 0, 1)
col = np.zeros((Hh, W, 3), np.float32)
a = np.zeros((Hh, W), np.float32)
col = over(col, rgb, A); a = np.clip(a + A * (1 - a), 0, 1)              # 体
col = over(col, mane_rgb, mane_a); a = np.clip(a + mane_a * (1 - a), 0, 1)   # たてがみ・前髪・しっぽ（首の縁にかぶさる）
col = over(col, ft_rgb, ft_a); a = np.clip(a + ft_a * (1 - a), 0, 1)     # 前髪・しっぽ
col = over(col, hexc(cfg['line']), ln * 0.9)
hl = cv2.morphologyEx(((mane_a + ft_a) > .5).astype(np.float32), cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8))
hl = cv2.GaussianBlur(hl, (3, 3), .6)
col = over(col, hexc(cfg['line']), hl * 0.85)
a = np.clip(a + hl * (1 - a), 0, 1)
rgb_all = np.where(a[..., None] > 1e-4, col / np.maximum(a, 1e-4)[..., None], 0)

# ---- ボードの上にかぶさる前足の先（球節→つなぎ→ひづめ） ----
S = R['S']; sc = R['scene']
sp = cfg['spread']
segs, hooves, fets = [], {}, {}
for k in ('FL', 'FR'):
    F = S[k]
    zl = 0.155 * F['z']
    zf = zl * 0.9 * (1 + (sp - 1) * 0.9)
    pts = [np.array([F['ft'][0], F['ft'][1], zf]), np.array([F['co'][0], F['co'][1], zf]), np.array([F['hf'][0], F['hf'][1], zf])]
    segs.append(pts)
    hooves[k] = sc.project(np.array([pts[-1]]))[0][0]
    fets[k] = sc.project(np.array([pts[0]]))[0][0]
P = world_pos(R)
near = np.zeros((Hh, W), bool)
for pts in segs:
    for i in range(len(pts) - 1):
        p0, p1 = pts[i], pts[i + 1]
        d = p1 - p0
        tt = np.clip(np.nansum((P - p0) * d, -1) / np.dot(d, d), 0, 1)
        q = p0 + tt[..., None] * d
        dist = np.linalg.norm(P - q, axis=-1)
        near |= np.nan_to_num(dist, nan=9) < 0.10
near = cv2.dilate(near.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(np.float32)
front_a = a * near

hy = max(fets['FL'][1], fets['FR'][1])       # 球節（いちばん上の曲がり）がボードの上に出る
bx0, bx1 = cfg['board'][0], cfg['board'][2]
by0 = int(hy + cfg['top_pad'])
by1 = by0 + cfg['board_h']
rect = dict(x=bx0, y=by0, w=bx1 - bx0, h=by1 - by0, W=W, H=Hh,
            hooves={k: [round(float(v[0])), round(float(v[1]))] for k, v in hooves.items()},
            fetlocks={k: [round(float(v[0])), round(float(v[1]))] for k, v in fets.items()})
save_png(rgb_all, f'{out}/{name}_back.png', alpha=a)
save_png(rgb_all, f'{out}/{name}_front.png', alpha=front_a)
json.dump(rect, open(f'{out}/{name}.json', 'w'))

# ---- 見本：うしろ → ボード → 前足の先 ----
bg = grad_v(Hh, W, [(0, '#FFF6D8'), (1, '#F4E3B4')])
img = over(bg, rgb_all, a)
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)


def rrect(x0, y0, x1, y1, r):
    cx = np.clip(xx, x0 + r, x1 - r); cy = np.clip(yy, y0 + r, y1 - r)
    return np.clip(r - np.hypot(xx - cx, yy - cy) + 0.5, 0, 1)


img = over(img, np.zeros(3, np.float32), blur(rrect(bx0 + 6, by0 + 10, bx1 + 6, by1 + 10, 26), 8) * 0.25)
img = over(img, hexc('#8A5A2B'), rrect(bx0, by0, bx1, by1, 26))
img = over(img, hexc('#FFFDF5'), rrect(bx0 + 14, by0 + 14, bx1 - 14, by1 - 14, 16))
img = over(img, rgb_all, front_a)
save_png(np.clip(img, 0, 1), f'{out}/{name}_preview.png')
print(json.dumps(rect))
