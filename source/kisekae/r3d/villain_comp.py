"""ヴィラン：赤い月・嵐の雲・稲妻・岩山に、3Dの黒馬と2Dのたてがみ・しっぽを重ねて仕上げる（赤い目なし）
   python3 villain_comp.py <描いたデータの頭> <出力フォルダ>"""
import sys, os, json, math
import numpy as np
import cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from h3d import load
from paint import fbm, warp, blur, smoothstep, fill
from fire2d import dust, aces, to_srgb, sparks
from hair2d import HairBuf, guide

pre, outdir = sys.argv[1], sys.argv[2]
M = json.load(open(pre + '_marks.json'))
W, H = M['W'], M['H']
S = W / 780.0
R = load(pre, W, H)
rgb, A = R['rgb'], R['a']
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rng = np.random.default_rng(11)
crest = np.array(M['crest']); poll = np.array(M['poll'][0]); tail = np.array(M['tail'])
hooves = np.array(M['hooves'])
lumf = lambda im: im[..., 0] * 0.6 + im[..., 1] * 0.3 + im[..., 2] * 0.1

# ---------- 空 ----------
mid_c = crest[int(len(crest) * 0.55)]
MX, MY = (poll * 0.45 + mid_c * 0.55) + np.array([-40, -30]) * S
MR = 268 * S
dist = np.sqrt((xx - MX) ** 2 + (yy - MY) ** 2)
md = dist / MR
t = (yy / H)[..., None]
sky = np.where(t < 0.55, np.array([0.003, 0.0004, 0.0006]) + (np.array([0.022, 0.0025, 0.003]) - np.array([0.003, 0.0004, 0.0006])) * (t / 0.55),
               np.array([0.022, 0.0025, 0.003]) + (np.array([0.002, 0.0003, 0.0004]) - np.array([0.022, 0.0025, 0.003])) * np.clip((t - 0.55) / 0.3, 0, 1))
halo = np.exp(-np.clip(dist - MR, 0, None) / (130 * S)) * 0.5 + np.exp(-np.clip(dist - MR, 0, None) / (30 * S)) * 0.5
sky = sky + halo[..., None] * np.array([0.26, 0.02, 0.014])
# 月
moon = np.clip((1.0 - md) * MR / 1.5 + 0.5, 0, 1)
tex = fbm(H, W, 80 * S, 5, seed=61)
maria = smoothstep(0.42, 0.75, warp(fbm(H, W, 150 * S, 4, seed=62), (fbm(H, W, 90 * S, 3, seed=63) - .5) * 60 * S, 0 * xx))
crat = smoothstep(0.55, 0.85, fbm(H, W, 22 * S, 3, seed=64))
limb = np.clip(1 - md ** 3 * 0.55, 0, 1)
ml = (0.58 + tex * 0.45 - maria * 0.42 - crat * 0.14) * limb
moon_col = np.stack([ml * 1.9, ml * 0.20 + ml ** 3 * 0.22, ml * 0.10 + ml ** 3 * 0.08], -1)
sky = sky * (1 - moon[..., None]) + moon_col * moon[..., None]
# 嵐の雲
n1 = fbm(H, W, 240 * S, 6, seed=11)
dx = (fbm(H, W, 360 * S, 4, seed=12) - .5) * 260 * S
dy = (fbm(H, W, 360 * S, 4, seed=13) - .5) * 90 * S
cl = warp(n1, dx, dy)
band = np.exp(-((yy - 120 * S) / (220 * S)) ** 2) * 0.55 + np.exp(-((yy - 900 * S) / (260 * S)) ** 2) * 0.5 + np.exp(-((yy - MY - MR * 0.75) / (90 * S)) ** 2) * 0.35
cd = smoothstep(0.5, 0.8, cl * (0.6 + band))
lit = np.clip(np.exp(-np.clip(dist - MR * 0.9, 0, None) / (220 * S)), 0, 1)
edge = np.clip(smoothstep(0.0, 0.35, cd) - smoothstep(0.35, 1.0, cd) * 0.85, 0, 1)
cloud = np.stack([0.002 + edge * lit * 0.7, 0.0003 + edge * lit * 0.06, 0.0004 + edge * lit * 0.04], -1)
sky = sky * (1 - cd[..., None] * 0.94) + cloud * cd[..., None] * 0.94 + (cd * lit * 0.04)[..., None] * np.array([1, .1, .06])

# 稲妻
lt = np.zeros((H, W), np.float32)
def bolt(x, y, ang, n, step, w, depth=0):
    pts = [(x, y)]
    for i in range(n):
        a = ang + rng.uniform(-0.8, 0.8)
        x += math.cos(a) * step * rng.uniform(.6, 1.3); y += math.sin(a) * step * rng.uniform(.6, 1.3)
        pts.append((x, y))
        if depth < 2 and rng.random() < 0.14:
            bolt(x, y, ang + rng.choice([-0.7, 0.7]), int(n * .45), step * .8, max(1, w - 1), depth + 1)
    q = np.round(np.array(pts) * 16).astype(np.int32)
    cv2.polylines(lt, [q], False, 1.0 if depth == 0 else 0.7, w, cv2.LINE_AA, shift=4)
bolt(70 * S, 60 * S, math.radians(96), 34, 17 * S, max(1, int(2.5 * S)))
bolt(735 * S, 20 * S, math.radians(100), 24, 16 * S, max(1, int(2 * S)))
lcore = blur(lt, 0.6 * S)
lglow = blur(lt, 6 * S) * 0.8 + blur(lt, 26 * S) * 0.9 + blur(lt, 90 * S) * 1.2
sky += lcore[..., None] * np.array([3.0, 2.5, 2.8]) + lglow[..., None] * np.array([0.35, 0.07, 0.10])

# 遠くの山（赤い霧）
def ridge(y0, amp, seed, peaks):
    r = np.random.default_rng(seed)
    n = 257
    y = np.zeros(n); step = 128; a = amp
    y[0], y[-1] = r.normal(0, amp), r.normal(0, amp)
    while step >= 1:
        for i in range(step, n, step * 2):
            y[i] = (y[i - step] + y[i + step]) / 2 + r.normal(0, a)
        step //= 2; a *= 0.55
    for px, ph in peaks:
        y -= ph * np.exp(-((np.linspace(0, 1, n) - px) / 0.07) ** 2)
    xs = np.linspace(-20, W + 20, n)
    return np.vstack([np.stack([xs, y0 + y * S], 1), [[W + 20, H], [-20, H]]])
far = np.zeros((H, W), np.float32); fill(far, [ridge(1060 * S, 24, 21, [(.1, 110), (.32, 60), (.88, 140)])])
mid = np.zeros((H, W), np.float32); fill(mid, [ridge(1150 * S, 18, 23, [(.05, 50), (.6, 80), (.96, 60)])])
haze = np.clip(halo * 0.5 + 0.12, 0, 1)
sky = sky * (1 - far[..., None] * 0.85) + (haze[..., None] * np.array([0.10, 0.012, 0.012])) * far[..., None] * 0.85
sky = sky * (1 - mid[..., None] * 0.9) + (haze[..., None] * np.array([0.04, 0.005, 0.005])) * mid[..., None] * 0.9

# 岩山（馬が立つ崖）
gy_img = hooves[2:, 1].max() + 8 * S
gx = hooves[2:, 0].mean()
pts = [(-30, H + 20)]
r2 = np.random.default_rng(5)
xs = np.linspace(-30, W + 30, 40)
for x in xs:
    d = (x - gx) / (W * 0.62)
    yv = gy_img + (d ** 2) * 240 * S + abs(d) * 60 * S + r2.normal(0, 12 * S)
    pts.append((x, yv))
pts.append((W + 30, H + 20))
rock = np.zeros((H, W), np.float32)
fill(rock, [np.array(pts)])
rtex = fbm(H, W, 60 * S, 5, seed=81)
cracks = 1 - smoothstep(0.0, 0.04, np.abs(fbm(H, W, 90 * S, 4, seed=82) - 0.5))
rd = cv2.distanceTransform((rock > .5).astype(np.uint8), cv2.DIST_L2, 5).astype(np.float32)
redge = np.exp(-rd / (5 * S)) * smoothstep(0.3, 0.9, rtex)
rock_col = np.stack([0.006 + rtex * 0.01 + redge * 0.5, 0.0012 + rtex * 0.002 + redge * 0.05, 0.0012 + rtex * 0.002 + redge * 0.035], -1)
rock_col *= (1 - cracks * 0.6)[..., None]
sky = sky * (1 - rock[..., None]) + rock_col * rock[..., None]
bg = sky.copy()

# ---------- 馬 ----------
img = bg * (1 - A[..., None]) + rgb

# ---------- たてがみ・前髪・しっぽ（逆光の毛） ----------
hb = HairBuf(H, W, ss=2)
WIND = math.radians(-172)      # 左へ（少し上）


def flow_mane(x, y, a, t):
    d = math.atan2(math.sin(WIND - a), math.cos(WIND - a))
    curl = (fbm_s[int(np.clip(y, 0, H - 1)), int(np.clip(x, 0, W - 1))] - 0.5) * 0.22
    return d * 0.06 + curl


fbm_s = fbm(H, W, 120 * S, 3, seed=91)
nC = len(crest)
for i in range(90):
    tt = (i + rng.random()) / 90
    j = 0.02 + tt * 0.98
    k0 = j * (nC - 1); a0 = int(k0); a1 = min(a0 + 1, nC - 1)
    p = crest[a0] + (crest[a1] - crest[a0]) * (k0 - a0)
    tg = crest[a1] - crest[max(a0 - 1, 0)]
    out_ang = math.atan2(tg[1], tg[0]) - math.pi / 2          # 首すじから外へ
    if math.cos(out_ang) > 0.2: out_ang += math.pi
    # 首の手前側へ少し垂れる房と、うしろへ流れる房
    if 0.12 < tt < 0.8 and rng.random() < 0.3:
        ang = out_ang + math.radians(rng.uniform(40, 80))
        L = rng.uniform(90, 200) * S
    else:
        ang = out_ang + rng.normal(0, 0.4)
        L = rng.uniform(190, 400) * S * (0.75 + 0.45 * math.sin(tt * math.pi))
    root = p + rng.normal(0, 4 * S, 2)
    g = guide(root, ang, L, 36, rng, flow_mane, wave=rng.uniform(1.4, 2.6), phase=rng.uniform(0, 6))
    hb.lock(g, 56, rng, spread=rng.uniform(6, 12) * S, clump=0.55, wmin=0.4 * S, wmax=1.1 * S, rimk=1.0)
    # 根もとは毛が多い（黒く詰まる）
    hb.lock(g[:12], 30, rng, spread=7 * S, clump=0.3, wmin=0.7 * S, wmax=1.5 * S, rimk=0.05)
for i in range(7):                     # 前髪（ひたいへ流れる）
    g = guide(poll + rng.normal(0, 3 * S, 2), math.radians(rng.uniform(15, 55)), rng.uniform(45, 85) * S, 14, rng, lambda x, y, a, t: 0.03, wave=0.8, phase=rng.uniform(0, 6))
    hb.lock(g, 22, rng, spread=3 * S, clump=0.7, wmin=0.4 * S, wmax=1.0 * S, rimk=0.1)
ta = tail[0]
tdir = tail[-1] - tail[0]
tang0 = math.atan2(tdir[1], tdir[0])
TAILW = math.radians(160)


def flow_tail(x, y, a, t):
    d = math.atan2(math.sin(TAILW - a), math.cos(TAILW - a))
    curl = (fbm_s[int(np.clip(y, 0, H - 1)), int(np.clip(x, 0, W - 1))] - 0.5) * 0.18
    return d * 0.05 * t + curl
for i in range(36):
    p = ta + (tail[1] - ta) * rng.uniform(0, .8) + rng.normal(0, 5 * S, 2)
    g = guide(p, tang0 + rng.normal(0, .3), rng.uniform(300, 520) * S, 36, rng, flow_tail, wave=1.4, phase=rng.uniform(0, 6))
    hb.lock(g, 40, rng, spread=rng.uniform(6, 12) * S, clump=0.7, wmin=0.6 * S, wmax=1.5 * S)
cov, rimw, cnt = hb.result(k=0.5)
dens = blur(cov, 4 * S)
bgL = blur(lumf(img), 6 * S)          # 馬の体の前の毛は月の光を受けない
rimI = np.clip(np.clip(bgL, 0, 3) ** 0.85 * rimw * np.clip(1 - dens, 0, 1) ** 1.2 * 2.6, 0, 1.4)
hair_col = np.stack([0.004 + rimI * 0.9, 0.0012 + rimI * 0.11, 0.0012 + rimI * 0.06], -1)
# 稲妻側（右上）の白いつや
spec = smoothstep(0.3, 1.0, rimw) * np.clip(1 - dens, 0, 1) * 0.04
hair_col += spec[..., None] * np.array([0.8, 0.8, 1.0])
img = img * (1 - cov[..., None]) + hair_col * cov[..., None]

# ---------- ひづめの土ぼこり・火の粉・霧 ----------
dustm = np.zeros((H, W), np.float32)
for hx, hy in hooves[2:]:
    dustm += np.exp(-(((xx - hx) / (110 * S)) ** 2 + ((yy - hy - 10 * S) / (45 * S)) ** 2))
dn = fbm(H, W, 40 * S, 4, seed=95)
dustm = dustm * smoothstep(0.35, 0.8, dn)
img += dustm[..., None] * np.array([0.12, 0.018, 0.012])


def epos(r):
    if r.random() < 0.6:
        return r.uniform(0, W), gy_img + r.normal(-120 * S, 260 * S)
    return r.uniform(0, W), r.uniform(0, H)
emb = dust(H, W, 170, rng, epos, size=(0.4 * S, 1.6 * S), inten=(0.25, 1.8))
img += emb[..., None] * np.array([1.0, 0.22, 0.08])
mist = fbm(H, W, 200 * S, 5, seed=96) * smoothstep(1100 * S, 1400 * S, yy)
img += (mist * 0.06)[..., None] * np.array([1.0, 0.12, 0.08])

# ---------- 仕上げ ----------
lum = img.max(2)
bl = img * smoothstep(0.8, 3.0, lum)[..., None]
img += blur(bl, 8 * S) * 0.25 + blur(bl, 36 * S) * 0.2
v = np.clip(1.15 - np.sqrt(((xx - W * .5) / (W * .9)) ** 2 + ((yy - H * .3) / (H * .8)) ** 2) * .7, .2, 1)[..., None]
img = img * v
out = to_srgb(aces(img * 1.0))
out = np.clip(out + (out - 0.5) * 0.10 * (1 - np.abs(out - 0.5) * 2), 0, 1)
out = np.clip(out + rng.normal(0, 0.009, out.shape[:2]).astype(np.float32)[..., None], 0, 1)
u8 = (out * 255 + .5).astype(np.uint8)
os.makedirs(outdir, exist_ok=True)
cv2.imwrite(os.path.join(outdir, 'villain3_wall.jpg'), cv2.cvtColor(u8, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 90])
eye = np.array(M['eye'][0])
# 小さな見本の絵：頭を中心に少し大きく切り出す（780×320）
tw = int(600 * S); th_ = int(tw * 320 / 780)
cxh = int(np.clip(eye[0] + -110 * S - tw / 2, 0, W - tw)); cyh = int(np.clip(eye[1] + 30 * S - th_ / 2, 0, H - th_))
thumb = cv2.resize(u8[cyh:cyh + th_, cxh:cxh + tw], (int(780 * S), int(320 * S)), interpolation=cv2.INTER_AREA)
cv2.imwrite(os.path.join(outdir, 'villain3_thumb.jpg'), cv2.cvtColor(thumb, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 90])
print('ok', W, H)
