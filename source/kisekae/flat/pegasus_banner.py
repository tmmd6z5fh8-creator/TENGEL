"""星座・ペガサスの絵（780×320）：夜空・天の川・星・三日月は前の constellation.py のまま、ペガサスだけ描き直す
   走る馬（3Dの馬の形）＋風になびくたてがみとしっぽ＋羽（一から作った形）を、
   うすく光る形・なめらかな外の線・線の上の小さい星・星座の線と明るい星で描く
   python3 flat/pegasus_banner.py <出力.webp> [見本のPNG]"""
import sys, os, math
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(K, 'r3d'))
sys.path.insert(0, K)
from style2d import *
import horse3d as Hm
from paint import fbm, warp

W, Hh = 780, 320
out = sys.argv[1]
rng = np.random.default_rng(201)
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)

# ---------- 夜空（前の絵と同じ） ----------
img = grad_v(Hh, W, [(0, '#070A24'), (0.6, '#1B1546'), (1, '#2D1B5A')])
band = np.exp(-(((yy - (220 - xx * 0.28)) / 60) ** 2))
neb = warp(fbm(Hh, W, 70, 5, seed=3), (fbm(Hh, W, 120, 3, seed=4) - .5) * 60, (fbm(Hh, W, 120, 3, seed=5) - .5) * 30)
img = img + (band * neb ** 2)[..., None] * hexc('#9C7BFF') * 0.45 + (band * neb ** 4)[..., None] * hexc('#FFD6F2') * 0.35
for i in range(700):
    x, y = rng.uniform(0, W), rng.uniform(0, Hh)
    b = rng.random() ** 3
    xi, yi = int(x), int(y)
    img[yi, xi] = np.minimum(1, img[yi, xi] + 0.35 + b * 0.65)
moon = soft_circle(Hh, W, 700, 58, 30, 1.0) - soft_circle(Hh, W, 712, 50, 27, 1.0)
img = img + blur(np.clip(moon, 0, 1), 10)[..., None] * hexc('#FFE9A8') * 0.4
img = over(img, hexc('#FFF2C4'), np.clip(moon, 0, 1))

# ---------- 走る馬（形だけ使う） ----------
POSE = dict(theta=4.0, neck_rot=-22.0, head_ang=-46.0,
            fore=dict(L=[-100, -34, -24, -12], R=[-72, 8, -112, -140]),
            hind=dict(L=[-118, -158, -150, -162], R=[-98, -142, -122, -142]),
            tail=[148, 172])
BOX = (236, 112, 600, 306)
Hm.HEAD_SCALE = 1.24
e, t = frame_horse(POSE, BOX, W, Hh, facing='right', azim=0, elev=2)
R = render_horse(POSE, e, t, 26, W, Hh, ss=2, name='peg')
S, scn = R['S'], R['scene']
P2 = lambda p, z=0.0: scn.project(np.array([[p[0], p[1], z]]))[0][0][:2]
body_a = np.clip(R['a'], 0, 1)

# ---------- 前髪としっぽ（風で後ろへ大きくなびく。一から作った房）。たてがみは下の MANE_TOP ----------
hr = np.random.default_rng(12)
crest = np.asarray(R['crest'], float)
locks = []
nC = len(crest)
pp, mz = np.asarray(R['poll'], float), np.asarray(R['muzzle'], float)
fd = (mz - pp) / np.linalg.norm(mz - pp)
for k in range(2):                                          # 前髪
    pts = flow(pp + fd * 3, math.atan2(fd[1], fd[0]) - 0.9 + k * 0.4, 18, 7, wind=0.25, wind_ang=math.pi + 0.3, rng=hr)
    locks.append(lock_poly(pts, 7, 0.6))
th_ = np.asarray(R['tail'][0], float)
for k in range(7):                                          # しっぽ：上へ上がってから うしろ下へ流れる
    a0 = -2.05 + (k - 3) * 0.11
    L = 120 + (3 - abs(k - 3)) * 14
    pts = flow(th_ + np.array([2.0, 2.0]), a0, L, 18, wind=0.17, wind_ang=math.pi - 0.75, rng=hr, wave=1.5, phase=k * 0.9)
    locks.append(lock_poly(pts, 26 - abs(k - 3) * 3, 1.2))
hair_a = poly_aa((Hh, W), locks)

# ---------- 羽（せなかから上へ・羽の先は後ろへ） ----------
BL = np.linalg.norm(P2(S['withers']) - P2(S['croup']))   # 背中の長さ（羽の大きさの目安）
WS = BL / 104.0
wr = P2(S['withers']) + np.array([-20.0, 4.0]) * WS      # 羽のつけね
WS = (wr[1] - 16) / 124.0                                  # 羽の先が絵の上から16pxに来る大きさ


def wing_outline(root, s=1.0):
    """羽：前のふち（肩 → 手首 → 先）と、うしろの羽の先（先は丸く、羽と羽の間だけ角）"""
    r = np.asarray(root, float)
    P = lambda q: r + np.array(q, float) * s
    lead = [P((0, 0)), P((6, -30)), P((-2, -66)), P((-24, -98)), P((-58, -120))]
    tips = [P(q) for q in ((-92, -128), (-116, -116), (-131, -96), (-137, -72), (-133, -48), (-118, -27), (-97, -11), (-73, -1), (-48, 5), (-24, 8))]
    wrist, ctr = P((-24, -98)), P((-60, -56))
    pts, sharp = list(lead), []
    for k in range(len(tips)):
        pts.append(tips[k])
        if k < len(tips) - 1:
            a, b = tips[k], tips[k + 1]
            notch = (a + b) / 2 + (ctr - (a + b) / 2) * 0.13
            pts.append(notch)
            sharp.append(len(pts) - 1)
    pts.append(P((-6, 10)))
    sharp.append(len(pts) - 1)
    return np.array(pts), sharp, tips, (wrist, ctr, r)


def smooth_poly(pts, sharp, n_seg=10):
    """角の点は角のまま、ほかはなめらかに（Catmull-Rom を細かい点に）"""
    P = np.asarray(pts, float); n = len(P); out = []
    for i in range(n):
        p0, p1, p2, p3 = P[i - 1], P[i], P[(i + 1) % n], P[(i + 2) % n]
        c1 = p1 if i in sharp else p1 + (p2 - p0) / 6
        c2 = p2 if (i + 1) % n in sharp else p2 - (p3 - p1) / 6
        for k in range(n_seg):
            u = k / n_seg
            out.append((1 - u) ** 3 * p1 + 3 * (1 - u) ** 2 * u * c1 + 3 * (1 - u) * u ** 2 * c2 + u ** 3 * p2)
    return np.array(out)


wing_pts, wing_sharp, wing_tips, wing_ctr = wing_outline(wr, WS)
wing_poly = smooth_poly(wing_pts, set(wing_sharp), 12)
wing_a = poly_aa((Hh, W), [wing_poly])

# たてがみ（首の上）：上のふちは まさちゃんの赤い線（羽のふち → 少し下がって → ほぼまっすぐ → 耳の方へ上がる）
MANE_TOP = [(437, 101), (450, 125), (468, 127), (486, 126), (505, 121), (518, 111)]
MANE_IN = [(524, 124), (500, 146), (470, 162), (440, 158)]          # 下のふちは首と羽の中（外の線には出ない）
mane_poly = smooth_poly(np.array(MANE_TOP + MANE_IN, float), {0, len(MANE_TOP) - 1, len(MANE_TOP)}, 12)
mane_a = poly_aa((Hh, W), [mane_poly])
mask = np.clip(np.maximum.reduce([body_a, hair_a, wing_a, mane_a]), 0, 1)
# 形の中の小さいすき間（羽のつけねなど）はうめる
_bin = (mask > 0.5).astype(np.uint8)
_n, _lab, _st, _ = cv2.connectedComponentsWithStats(1 - _bin, connectivity=4)
for _i in range(1, _n):
    x0, y0, w0, h0, area = _st[_i]
    if area < 150 and x0 > 0 and y0 > 0 and x0 + w0 < W and y0 + h0 < Hh:
        mask[_lab == _i] = 1.0

# ---------- うすく光る形 ----------
lav = hexc('#8E8CFF')
img = img + blur(mask, 14)[..., None] * lav * 0.12 + blur(mask, 5)[..., None] * lav * 0.16
img = img + mask[..., None] * hexc('#B8B4FF') * 0.13

# ---------- なめらかな外の線（2倍の大きさで線を出してから縮める） ----------
SS = 2
m2 = cv2.resize(mask, (W * SS, Hh * SS), interpolation=cv2.INTER_LINEAR)
cs, hier = cv2.findContours((m2 > 0.5).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)   # 外がわだけ（房のすき間の小さい輪は描かない）
ln2 = np.zeros((Hh * SS, W * SS), np.float32)
dots = []
for c in cs:
    if cv2.contourArea(c) < 30 * SS * SS:
        continue
    p = c[:, 0, :].astype(np.float32)
    n = len(p)
    k = np.arange(-6, 7); g = np.exp(-(k / 2.4) ** 2); g /= g.sum()
    ps = np.stack([np.convolve(np.r_[p[-6:, d], p[:, d], p[:6, d]], g, 'valid') for d in (0, 1)], 1)   # 輪のまま少しなめらかに
    cv2.polylines(ln2, [(ps * 16).astype(np.int32)], True, 1.0, 2, cv2.LINE_AA, shift=4)
    seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(ps, axis=0), axis=1))]
    for sv in np.arange(9 * SS, seg[-1], 23 * SS):
        i = int(np.searchsorted(seg, sv)); dots.append(ps[min(i, len(ps) - 1)] / SS)
ln = cv2.resize(ln2, (W, Hh), interpolation=cv2.INTER_AREA)

# 羽の中の線：羽と羽の切れ目から根元の方へ（長い羽は手首へ、短い羽は腕の骨へ）＋小さい羽の列（丸い波）
det = np.zeros((Hh * SS, W * SS), np.float32)
wrist, wctr, wroot = wing_ctr
nT = len(wing_tips)
for k in range(nT - 1):
    a, b = wing_tips[k], wing_tips[k + 1]
    notch = (a + b) / 2 + (wctr - (a + b) / 2) * 0.13
    base = wrist + (wroot - wrist) * min(1.0, max(0.0, (k - 2) / (nT - 3)))
    end = notch + (base - notch) * 0.32
    cv2.line(det, tuple((notch * SS * 16).astype(int)), tuple((end * SS * 16).astype(int)), 1.0, 2, cv2.LINE_AA, shift=4)
cov = []
for u in np.linspace(0, 1, 7):
    q = wroot + (wrist - wroot) * u + (wctr - (wroot + (wrist - wroot) * u)) * 0.30
    cov.append(q)
for i in range(len(cov) - 1):                               # 小さい羽の列：丸いふくらみを うしろ下へ
    a, b = cov[i], cov[i + 1]
    mid = (a + b) / 2 + (wctr - (a + b) / 2) * 0.10 + np.array([-3.0, 4.0]) * WS
    arc = np.array([(1 - u) ** 2 * a + 2 * (1 - u) * u * mid + u ** 2 * b for u in np.linspace(0, 1, 10)])
    cv2.polylines(det, [(arc * SS * 16).astype(np.int32)], False, 1.0, 2, cv2.LINE_AA, shift=4)
top = smooth_poly(np.array(MANE_TOP, float), {0, len(MANE_TOP) - 1}, 10)[:-10]
for off, t0, t1 in ((7, 0.12, 0.92), (14, 0.22, 0.80)):                 # たてがみの毛の流れ（うすい線）
    seg = top[int(len(top) * t0):int(len(top) * t1)] + np.array([0.0, off])
    seg[:, 1] += np.sin(np.linspace(0, 3 * math.pi, len(seg))) * 1.6
    cv2.polylines(det, [(seg * SS * 16).astype(np.int32)], False, 1.0, 2, cv2.LINE_AA, shift=4)
det = cv2.resize(det, (W, Hh), interpolation=cv2.INTER_AREA)

line_col = hexc('#CFD6FF')
img = img + blur(ln, 2.0)[..., None] * hexc('#8FA4FF') * 0.6 + ln[..., None] * line_col * 0.82
img = img + det[..., None] * line_col * 0.38

# 外の線の上の小さい星
sd = np.zeros((Hh, W), np.float32)
for i, (x, y) in enumerate(dots):
    cv2.circle(sd, (int(x * 16), int(y * 16)), int((1.1 + (i % 3 == 0) * 0.5) * 16), 1.0, -1, cv2.LINE_AA, shift=4)
img = img + blur(sd, 2.2)[..., None] * hexc('#FFE7A8') * 0.5 + sd[..., None] * hexc('#FFF6DC') * 0.7

# ---------- 星座の線と明るい星 ----------
FL, FR, HL, HR = (S[k] for k in ('FL', 'FR', 'HL', 'HR'))
leg_pt = lambda F, key: P2(F[key], 0.155 * F['z'])
STARS = dict(muzzle=np.asarray(R['muzzle'])[:2], eye=np.asarray(R['eye'])[:2], poll=np.asarray(R['poll'])[:2],
             withers=P2(S['withers']), back=P2(S['back']), croup=P2(S['croup']), tail=np.asarray(R['tail'][-1])[:2] + np.array([-34.0, -6.0]),
             chest=P2(S['chest']),
             fl_knee=leg_pt(FL, 'kn'), fl_hoof=leg_pt(FL, 'hf'), fr_knee=leg_pt(FR, 'kn'), fr_hoof=leg_pt(FR, 'hf'),
             hip=P2(S['hip']), hl_hock=leg_pt(HL, 'hk'), hl_hoof=leg_pt(HL, 'hf'), hr_hock=leg_pt(HR, 'hk'), hr_hoof=leg_pt(HR, 'hf'),
             w_wrist=wr + np.array([-40.0, -104.0]) * WS, w_tip=wing_tips[0], w_mid=wing_tips[3], w_low=wing_tips[6])
LINKS = [('muzzle', 'eye'), ('eye', 'poll'), ('poll', 'withers'), ('withers', 'back'), ('back', 'croup'), ('croup', 'tail'),
         ('withers', 'chest'), ('chest', 'fl_knee'), ('fl_knee', 'fl_hoof'), ('chest', 'fr_knee'), ('fr_knee', 'fr_hoof'),
         ('croup', 'hip'), ('hip', 'hl_hock'), ('hl_hock', 'hl_hoof'), ('hip', 'hr_hock'), ('hr_hock', 'hr_hoof'),
         ('withers', 'w_wrist'), ('w_wrist', 'w_tip'), ('w_tip', 'w_mid'), ('w_mid', 'w_low'), ('w_low', 'back')]
BIG = ('eye', 'withers', 'croup', 'w_tip', 'muzzle', 'fl_hoof', 'hl_hoof', 'tail', 'w_mid')
cl = np.zeros((Hh * SS, W * SS), np.float32)
for a, b in LINKS:
    pa, pb = STARS[a] * SS, STARS[b] * SS
    cv2.line(cl, tuple((pa * 16).astype(int)), tuple((pb * 16).astype(int)), 1.0, 2, cv2.LINE_AA, shift=4)
cl = cv2.resize(cl, (W, Hh), interpolation=cv2.INTER_AREA)
img = img + blur(cl, 2.2)[..., None] * hexc('#FFD98A') * 0.42 + cl[..., None] * hexc('#FFE9B0') * 0.62

stl = np.zeros((Hh * SS, W * SS), np.float32)
for k, p in STARS.items():
    big = k in BIG
    x, y = p * SS
    r = (2.6 if big else 1.9) * SS
    cv2.circle(stl, (int(x * 16), int(y * 16)), int(r * 16), 1.0, -1, cv2.LINE_AA, shift=4)
    L = (11 if big else 6) * SS
    for ang in (0, 90):
        dx, dy = math.cos(math.radians(ang)) * L, math.sin(math.radians(ang)) * L
        pts = np.array([[x - dx, y - dy], [x + dy * 0.12, y - dx * 0.12], [x + dx, y + dy], [x - dy * 0.12, y + dx * 0.12]])
        cv2.fillPoly(stl, [(pts * 16).astype(np.int32)], 1.0, cv2.LINE_AA, shift=4)
stl = cv2.resize(stl, (W, Hh), interpolation=cv2.INTER_AREA)
img = img + blur(stl, 3.0)[..., None] * hexc('#FFD27A') * 0.9
img = np.maximum(img, stl[..., None] * hexc('#FFFBEA'))

save_webp(np.clip(img, 0, 1), out)
if len(sys.argv) > 2:      # 確かめ用：形だけ
    dbg = (np.dstack([mask] * 3) * 150).astype(np.uint8)
    for k, p in STARS.items():
        cv2.circle(dbg, (int(p[0]), int(p[1])), 3, (255, 255, 0), -1)
        cv2.putText(dbg, k, (int(p[0]) + 4, int(p[1]) - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.32, (255, 200, 80), 1)
    cv2.imwrite(sys.argv[2], cv2.cvtColor(dbg, cv2.COLOR_RGB2BGR))
print(out)
