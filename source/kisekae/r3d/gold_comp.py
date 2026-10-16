"""黄金の炎：3Dの金の馬に、炎のたてがみ・しっぽ・炎のうず・光の粒を重ねて仕上げる
   python3 gold_comp.py <描いたデータの頭> <出力フォルダ>"""
import sys, os, json, math
import numpy as np
import cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from h3d import load
from paint import fbm, warp, blur, smoothstep
from fire2d import Heat, flow_path, fire_color, bokeh, sparks, aces, to_srgb, dust, GOLD_STOPS

pre, outdir = sys.argv[1], sys.argv[2]
M = json.load(open(pre + '_marks.json'))
W, H = M['W'], M['H']
S = W / 780.0
R = load(pre, W, H)
rgb, A = R['rgb'], R['a']
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rng = np.random.default_rng(7)

crest = np.array(M['crest'])
poll = np.array(M['poll'][0])
tail = np.array(M['tail'])
eye = np.array(M['eye'][0])

# ---------- 背景（線形） ----------
cx, cy = crest[int(len(crest) * .45)]
cy -= 60 * S
dist = np.sqrt((xx - cx) ** 2 + ((yy - cy) * 0.85) ** 2)
bg = np.zeros((H, W, 3), np.float32)
top = np.array([0.020, 0.008, 0.002]); mid = np.array([0.012, 0.005, 0.0012]); bot = np.array([0.004, 0.0018, 0.0005])
t = (yy / H)[..., None]
bg += np.where(t < .5, top + (mid - top) * (t / .5), mid + (bot - mid) * ((t - .5) / .5))
glow = np.exp(-dist / (300 * S))[..., None] * np.array([0.12, 0.04, 0.007]) + np.exp(-dist / (130 * S))[..., None] * np.array([0.12, 0.045, 0.009])
bg += glow
# 煙
dxs = (fbm(H, W, 260 * S, 4, seed=4) - .5) * 300 * S
dys = (fbm(H, W, 260 * S, 4, seed=5) - .5) * 300 * S
smoke = warp(fbm(H, W, 180 * S, 6, seed=3), dxs, dys)
smoke = smoothstep(.5, .95, smoke) * (0.25 + 0.75 * np.exp(-dist / (520 * S)))
bg += smoke[..., None] * np.array([0.07, 0.028, 0.006])

# 炎のうず（うしろの大きな弧・細い炎のリボン）
sw = Heat(H, W, ss=1)
for i in range(16):
    r0 = rng.uniform(250, 420) * S
    a0 = rng.uniform(-math.pi * 1.05, -math.pi * 0.15)
    span = rng.uniform(1.4, 2.6)
    ox, oy = cx + rng.normal(0, 30 * S), cy + 40 * S + rng.normal(0, 30 * S)
    pts = []
    for k in range(60):
        a = a0 + span * k / 59
        r = r0 * (1 + 0.18 * k / 59) + 18 * S * math.sin(k * .2 + i)
        pts.append((ox + math.cos(a) * r * 0.82, oy + math.sin(a) * r))
    sw.lock(np.array(pts), rng.uniform(7, 16) * S, rng.uniform(.4, .7), root_taper=.3, power=0.6)
    for k in range(3):
        jit = np.array(pts) + rng.normal(0, 1, 2) * 9 * S + np.sin(np.linspace(0, 7, len(pts)) + k)[:, None] * 6 * S
        sw.lock(jit, rng.uniform(1.5, 3.5) * S, rng.uniform(.4, .7), root_taper=.3, power=0.5)
for i in range(10):                       # 外へ流れる細い炎
    a = rng.uniform(0, 2 * math.pi)
    p = (cx + math.cos(a) * 300 * S, cy + math.sin(a) * 360 * S)
    c = flow_path(p, a + rng.uniform(1.2, 1.9), rng.uniform(200, 380) * S, 30, rng, wave=1.4, phase=rng.uniform(0, 6), turn=rng.uniform(-0.05, 0.05))
    sw.lock(c, rng.uniform(4, 9) * S, rng.uniform(.4, .7), power=0.8)
swh = sw.result(turb=34 * S, fine=4 * S, seed=40, breakup=.28, up=2 * S)
swh = blur(swh, 1.2 * S)
swirl = fire_color(np.clip(swh * 0.85, 0, 1), GOLD_STOPS) * 0.26
bg += swirl + blur(swirl, 10 * S) * 0.7 + blur(swirl, 36 * S) * 0.35
bg += bokeh(H, W, 55, rng, 3 * S, 22 * S, inten=(0.02, 0.14))

hv = np.array(M['hooves'])
fy = hv[:, 1].max() + 6 * S
fxc = hv[:, 0].mean()
floor = np.exp(-(((xx - fxc) / (330 * S)) ** 2 + ((yy - fy) / (40 * S)) ** 2))
bg += floor[..., None] * np.array([0.10, 0.045, 0.008])

# ---------- うしろ側のたてがみの炎（馬の体にかくれる） ----------
def mane(heat, n, side_off, peak_rng, seed_shift, strands=5):
    L_all = len(crest)
    for i in range(n):
        t = (i + rng.random()) / n
        j = t * (L_all - 1); j0 = int(j); j1 = min(j0 + 1, L_all - 1)
        p = crest[j0] + (crest[j1] - crest[j0]) * (j - j0)
        p = p + np.array([side_off * rng.uniform(.3, 1.0), rng.normal(0, 4 * S)])
        base_ang = math.radians(rng.uniform(-130, -96) - 22 * (1 - t))
        L = rng.uniform(190, 440) * S * (1.05 - 0.4 * t)
        ph = rng.uniform(0, 6)
        c = flow_path(p, base_ang, L, 30, rng, wave=1.2, phase=ph, turn=rng.uniform(-0.012, 0.004), curl=-0.04, rise=0.35)
        w0 = rng.uniform(12, 22) * S * (1.05 - 0.35 * t)
        heat.lock(c, w0, rng.uniform(*peak_rng))
        # 髪のような細いすじ（同じ流れにそって少しずつ広がる）
        tang = np.gradient(c, axis=0)
        nrm_ = np.stack([-tang[:, 1], tang[:, 0]], 1)
        nrm_ /= np.linalg.norm(nrm_, axis=1, keepdims=True) + 1e-9
        for k in range(strands):
            off = rng.uniform(-1, 1) * w0 * 0.7
            spread = np.linspace(0, 1, len(c)) ** 1.3 * rng.uniform(-1, 1) * w0 * 1.6
            wob = np.sin(np.linspace(0, rng.uniform(4, 9), len(c)) + rng.uniform(0, 6))[:, None] * w0 * 0.25
            c2 = c + nrm_ * (off + spread)[:, None] + nrm_ * wob
            cut = int(len(c2) * rng.uniform(.75, 1.0))
            heat.lock(c2[:cut], rng.uniform(1.6, 4.0) * S, rng.uniform(.55, .95) * peak_rng[1], root_taper=.05, power=0.9)
        for k in range(2):                # 先で分かれる細い炎
            j2 = int(len(c) * rng.uniform(.35, .6))
            c3 = flow_path(c[j2], math.atan2(*(c[j2] - c[j2 - 1])[::-1]) + rng.normal(0, .5), L * rng.uniform(.3, .55), 14, rng, wave=1.4, phase=rng.uniform(0, 6), rise=.3)
            heat.lock(c3, w0 * rng.uniform(.2, .4), rng.uniform(.45, .75) * (1 - j2 / len(c)))

back = Heat(H, W)
mane(back, 30, -14 * S, (.6, .92), 0)
backh = back.result(turb=30 * S, fine=10 * S, seed=10, breakup=.65)
fire_back = fire_color(np.clip(backh * 0.88, 0, 1)) * 0.55

# ---------- 前側のたてがみ・しっぽ・ひづめの炎 ----------
front = Heat(H, W)
mane(front, 20, 10 * S, (.55, .9), 1)
for i in range(9):                         # 前髪の炎（ひたいから上へ）
    p = poll + rng.normal(0, 6 * S, 2)
    c = flow_path(p, math.radians(rng.uniform(-112, -62)), rng.uniform(70, 170) * S, 18, rng, wave=1.1, phase=rng.uniform(0, 6), curl=-0.03, rise=0.3)
    front.lock(c, rng.uniform(8, 15) * S, rng.uniform(.5, .82))
ta = tail[0]
tdir = tail[-1] - tail[0]
tang = math.atan2(tdir[1], tdir[0])
for i in range(20):
    p = ta + rng.normal(0, 6 * S, 2) + (tail[1] - ta) * rng.uniform(0, .6)
    a = tang + rng.normal(0, .35) - 0.3
    c = flow_path(p, a, rng.uniform(220, 460) * S, 28, rng, wave=1.4, phase=rng.uniform(0, 6), turn=rng.uniform(-0.01, 0.02), curl=0.05, rise=0.25)
    front.lock(c, rng.uniform(10, 20) * S, rng.uniform(.4, .72))
for hx, hy in M['hooves']:
    for i in range(5):
        p = np.array([hx, hy]) + rng.normal(0, 5 * S, 2)
        c = flow_path(p, math.radians(rng.uniform(-150, -100)), rng.uniform(30, 70) * S, 10, rng, wave=1.0, phase=rng.uniform(0, 6))
        front.lock(c, rng.uniform(8, 14) * S, rng.uniform(.4, .7))
fronth = front.result(turb=30 * S, fine=10 * S, seed=20, breakup=.65)
fire_front = fire_color(np.clip(fronth * 0.88, 0, 1)) * 0.55

# ---------- 合成 ----------
img = bg + fire_back + blur(fire_back, 18 * S) * 0.35
fire_all = fire_back + fire_front + swirl * 0.5
# 炎の光が金に映る
fl = blur(fire_all, 26 * S) * 0.55 + blur(fire_all, 70 * S) * 0.35
gold_tint = np.array([1.0, 0.72, 0.32])
horse = rgb + fl * gold_tint * A[..., None] * 0.22
img = img * (1 - A[..., None]) + horse
img += fire_front + blur(fire_front, 16 * S) * 0.3 + blur(fire_front, 50 * S) * 0.15
img += blur(fire_back, 50 * S) * 0.12
# 火の粉
def dpos(r):
    if r.random() < 0.55:
        c0 = crest[r.integers(0, len(crest))]
        return c0[0] + r.normal(-60 * S, 170 * S), c0[1] + r.normal(-90 * S, 200 * S)
    return r.uniform(0, W), r.uniform(0, H * .8)
dd = dust(H, W, 520, rng, dpos, size=(0.6 * S, 2.6 * S), inten=(0.25, 2.4))
img += dd[..., None] * np.array([1.0, 0.66, 0.24])
spk = sparks(H, W, 40, rng, region=lambda r: (r.uniform(0, W), r.uniform(H * .05, H * .7)), slen=(6 * S, 18 * S), inten=(0.2, 0.8))
img += blur(spk, 0.6)[..., None] * np.array([1.0, 0.55, 0.15])

# ---------- 仕上げ ----------
lum = img.max(2)
bl = img * smoothstep(1.2, 4.0, lum)[..., None]
img += blur(bl, 10 * S) * 0.2 + blur(bl, 40 * S) * 0.15
v = np.clip(1.12 - np.sqrt(((xx - W * .52) / (W * .95)) ** 2 + ((yy - H * .3) / (H * .78)) ** 2) * .62, .25, 1)[..., None]
img = img * v
out = to_srgb(aces(img * 1.0))
# 少しだけコントラストを強く（S字）
out = np.clip(out + (out - 0.5) * 0.12 * (1 - np.abs(out - 0.5) * 2), 0, 1)
# ほんの少しの粒子
out = np.clip(out + rng.normal(0, 0.008, out.shape[:2]).astype(np.float32)[..., None], 0, 1)
u8 = (out * 255 + .5).astype(np.uint8)
os.makedirs(outdir, exist_ok=True)
cv2.imwrite(os.path.join(outdir, 'goldfire3_wall.jpg'), cv2.cvtColor(u8, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 90])
eye = np.array(M['eye'][0])
# 小さな見本の絵：頭を中心に少し大きく切り出す（780×320）
tw = int(740 * S); th_ = int(tw * 320 / 780)
cxh = int(np.clip(eye[0] + -60 * S - tw / 2, 0, W - tw)); cyh = int(np.clip(eye[1] + 40 * S - th_ / 2, 0, H - th_))
thumb = cv2.resize(u8[cyh:cyh + th_, cxh:cxh + tw], (int(780 * S), int(320 * S)), interpolation=cv2.INTER_AREA)
cv2.imwrite(os.path.join(outdir, 'goldfire3_thumb.jpg'), cv2.cvtColor(thumb, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 90])
print('ok', W, H)
