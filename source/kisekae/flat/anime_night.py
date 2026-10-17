"""ナイター（アニメ塗り）（780×320）
   3頭の位置・走り方・勝負服・番号は flat/night_banner.py と同じまま、絵をアニメの塗りに：
   - 馬と騎手：flat/anime_rider.py（くっきりした影・つや・ふちの光・線・とがった房のたてがみ／しっぽ）
   - 空：夜空のグラデーションとうすい雲・星のきらめき
   - 照明：ランプの粒・光のにじみ・十字の光・横に長い光の筋・下へ広がる光
   - スタンド：屋根のふちの光・窓の灯り・観客の光の粒・ぼけた光の玉
   - ダート：はけで塗ったような色と筋・照明の光だまり・ひづめのあと
   - 動き：スピード線・ふわっとした砂けむり（もこもこの丸・明るい上がわ・影の下がわ・線）・とぶ砂
   - 柵：白い柵（影の段・線）
   python3 flat/anime_night.py <出力.webp>"""
import sys, os, math
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from anime_rider import *

W, Hh = 780, 320
out = sys.argv[1]
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
H = hexc


def aa_canvas(scale=4):
    return np.zeros((Hh * scale, W * scale), np.float32)


def down(c, scale=4):
    return cv2.resize(c, (W, Hh), interpolation=cv2.INTER_AREA)


# ============ 空 ============
img = grad_v(Hh, W, [(0, '#060A2C'), (0.30, '#101654'), (0.48, '#262A78'), (0.58, '#43358C'), (0.62, '#4E3A90')])
cl = np.random.default_rng(3)
cloud = np.zeros((Hh, W), np.float32)
for i in range(7):                                                # うすい雲（横長・下のふちが照明で明るい）
    cx, cy = cl.uniform(-40, W + 40), cl.uniform(70, 125)
    for j in range(9):
        cv2.ellipse(cloud, (int((cx + cl.normal(0, 60)) * 16), int((cy + cl.normal(0, 5)) * 16)),
                    (int(cl.uniform(40, 110) * 16), int(cl.uniform(5, 11) * 16)), 0, 0, 360, 1.0, -1, cv2.LINE_AA, shift=4)
cloud = blur(np.clip(cloud, 0, 1), 4)
img = over(img, H('#3A3A8E'), cloud * 0.45)
img = img + (np.clip(cloud - np.roll(cloud, -5, axis=0), 0, 1))[..., None] * H('#8E86D8') * 0.35
srng = np.random.default_rng(11)
for i in range(120):                                              # 星（点・ときどき十字のきらめき）
    x, y = srng.uniform(0, W), srng.uniform(0, 140)
    r = srng.uniform(0.45, 1.1)
    b = srng.uniform(0.45, 0.95)
    img = img + soft_circle(Hh, W, x, y, r, 0.8)[..., None] * b
    if srng.random() < 0.10:
        L = srng.uniform(3.5, 6.5)
        sp = aa_canvas()
        cv2.line(sp, (int((x - L) * 64), int(y * 64)), (int((x + L) * 64), int(y * 64)), 1.0, 2, cv2.LINE_AA, shift=4)
        cv2.line(sp, (int(x * 64), int((y - L) * 64)), (int(x * 64), int((y + L) * 64)), 1.0, 2, cv2.LINE_AA, shift=4)
        sp = down(sp)
        img = img + sp[..., None] * H('#EAF0FF') * 0.75 + blur(sp, 1.5)[..., None] * H('#9DB4FF') * 0.5

# ============ スタンド ============
top_s = 145 - 13 * np.exp(-((xx - 390) / 320) ** 2)
stand = np.clip((yy - top_s) * 1.2 + 0.5, 0, 1) * (yy < 191)
img = over(img, H('#191846'), stand)
img = over(img, H('#24225E'), stand * np.clip((yy - 158) / 20, 0, 1) * 0.8)
roofline = np.exp(-((yy - top_s - 0.5) / 0.9) ** 2) * (yy < 191)
img = img + roofline[..., None] * H('#A9B8FF') * 0.65                          # 屋根のふちの光
for row, (yo, ph, col_) in enumerate(((9, 0.0, '#FFE2A0'), (15, 1.7, '#FFD490'))):
    win = ((np.sin(xx * 0.85 + ph) > 0.62) & (np.abs(yy - (top_s + yo)) < 1.1)).astype(np.float32)
    img = img + blur(win * stand, 0.6)[..., None] * H(col_) * 0.6
crowd = np.random.default_rng(12)
for i in range(520):                                              # 観客の光の粒
    x = crowd.uniform(0, W); y = crowd.uniform(163, 189)
    if stand[int(y), int(x)] > .5:
        c = [H('#FFE7A8'), H('#FFFFFF'), H('#A8C8FF'), H('#FF9AC8'), H('#9CF0FF')][crowd.integers(0, 5)]
        img = img + soft_circle(Hh, W, x, y, crowd.uniform(0.5, 0.9), 0.7)[..., None] * c * 0.85
bk = np.random.default_rng(13)
for i in range(26):                                               # ぼけた光の玉（ふちが少し明るい）
    x, y = bk.uniform(0, W), bk.uniform(150, 192)
    r = bk.uniform(3, 8)
    c = [H('#FFD9A0'), H('#A8C4FF'), H('#FFB0D8'), H('#B8FFF0')][bk.integers(0, 4)]
    disc = soft_circle(Hh, W, x, y, r, 1.2)
    ring = disc - soft_circle(Hh, W, x, y, r - 1.0, 1.2)
    img = img + (disc * 0.12 + ring * 0.05)[..., None] * c

# ============ 照明 ============
for tx, ty in [(70, 40), (720, 34), (390, 20)]:
    pole = aa_canvas()
    cv2.line(pole, (int(tx * 64), int((ty + 8) * 64)), (int(tx * 64), int(190 * 64)), 1.0, 12, cv2.LINE_AA, shift=4)
    for yb in range(ty + 22, 186, 16):                                         # 柱の横棒
        cv2.line(pole, (int((tx - 3) * 64), int(yb * 64)), (int((tx + 3) * 64), int((yb + 8) * 64)), 1.0, 5, cv2.LINE_AA, shift=4)
    img = over(img, H('#0C0D28'), down(pole))
    ang = np.arctan2(xx - tx, yy - ty)                                          # 下へ広がる光
    cone = np.clip(1 - np.abs(ang) / 0.62, 0, 1) ** 1.5 * (yy > ty) * np.exp(-(yy - ty) / 240)
    img = img + blur(cone, 5)[..., None] * H('#7F96FF') * 0.14
    lamp = aa_canvas()
    for i in range(3):
        for j in range(5):
            cv2.circle(lamp, (int((tx - 16 + j * 8) * 64), int((ty - 7 + i * 7) * 64)), int(3.1 * 64), 1.0, -1, cv2.LINE_AA, shift=4)
    frame = aa_canvas()
    cv2.rectangle(frame, (int((tx - 21) * 64), int((ty - 11) * 64)), (int((tx + 21) * 64), int((ty + 11) * 64)), 1.0, -1, cv2.LINE_AA, shift=4)
    img = over(img, H('#1A1C40'), down(frame))
    lamp = down(lamp)
    img = img + blur(lamp, 30)[..., None] * H('#6E84FF') * 0.75 + blur(lamp, 10)[..., None] * H('#B8C8FF') * 0.9
    img = np.maximum(img, lamp[..., None] * H('#FFFFFF'))
    fl = aa_canvas()
    for (dx, dy, L, wd) in ((1, 0, 150, 3), (0, 1, 44, 3), (0.7, 0.7, 20, 2), (0.7, -0.7, 20, 2)):
        cv2.line(fl, (int((tx - dx * L) * 64), int((ty - dy * L) * 64)), (int((tx + dx * L) * 64), int((ty + dy * L) * 64)), 1.0, wd * 4, cv2.LINE_AA, shift=4)
    fl = down(fl)
    fall = np.exp(-np.sqrt((xx - tx) ** 2 * 0.6 + ((yy - ty) * 2.4) ** 2) / 60)
    img = img + (blur(fl, 0.8) * fall)[..., None] * H('#E2E8FF') * 1.1 + (blur(fl, 3) * fall)[..., None] * H('#8EA2FF') * 0.5

# ============ ダート ============
TOP, Y0 = 194, 150
trk = np.clip((yy - TOP) + 0.5, 0, 1)
dirt = grad_v(Hh, W, [(0, '#3C2A34'), (0.60, '#3C2A34'), (0.61, '#5C4040'), (0.75, '#74503E'), (1, '#8E6248')])
pool = np.zeros((Hh, W), np.float32)
for tx in (70, 390, 720):
    pool += np.exp(-(((xx - tx) / 200) ** 2 + ((yy - 254) / 50) ** 2))
pool = np.clip(pool, 0, 1.2)
dirt = dirt * (0.70 + 0.42 * pool)[..., None] + (pool * 0.08)[..., None] * H('#C4B4FF')
br = np.random.default_rng(21)
lite = aa_canvas(); dark = aa_canvas()
for i in range(170):                                              # はけの筋（遠いほど細く短く）
    y = TOP + 3 + (Hh - TOP - 3) * br.random() ** 0.85
    sc_ = (y - Y0) / (Hh - Y0)
    x = br.uniform(-60, W); L = (br.uniform(20, 110) * sc_ + 8)
    tgt = lite if br.random() < 0.5 else dark
    pts = np.array([[x + L * t, y + math.sin(t * math.pi) * -0.6 * sc_] for t in np.linspace(0, 1, 8)])
    cv2.polylines(tgt, [np.round(pts * 64).astype(np.int32)], False, br.uniform(0.4, 1.0), max(1, int(round(6 * sc_))), cv2.LINE_AA, shift=4)
dirt = dirt + blur(down(lite), 0.5)[..., None] * H('#B08C70') * 0.20 - blur(down(dark), 0.5)[..., None] * 0.06
hp = aa_canvas(2)
pr = np.random.default_rng(7)
for i in range(260):                                              # ひづめのあと
    y = TOP + 6 + (Hh - TOP - 6) * pr.random() ** 0.8
    x = pr.uniform(0, W)
    sc_ = (y - Y0) / (Hh - Y0)
    cv2.ellipse(hp, (int(x * 2 * 16), int(y * 2 * 16)), (int(max(1.0, 3.6 * sc_) * 2 * 16), int(max(0.5, 1.3 * sc_) * 2 * 16)), 0, 0, 360,
                pr.uniform(0.4, 1.0), -1, cv2.LINE_AA, shift=4)
hp = cv2.resize(hp, (W, Hh), interpolation=cv2.INTER_AREA)
dirt = dirt * (1 - hp * 0.25)[..., None] + np.roll(hp, -1, axis=0)[..., None] * H('#C8A88C') * 0.10
img = img * (1 - trk[..., None]) + dirt * trk[..., None]
img = img * (1 - (np.exp(-(yy - TOP) / 6) * trk * 0.35))[..., None]               # 柵の下の暗がり

# 奥の柵
fr = aa_canvas()
cv2.line(fr, (0, 190 * 64), (W * 64, 190 * 64), 1.0, 9, cv2.LINE_AA, shift=4)
for x in range(6, W, 24):
    cv2.line(fr, (x * 64, 190 * 64), (x * 64, 201 * 64), 1.0, 5, cv2.LINE_AA, shift=4)
fr = down(fr)
img = over(img, H('#E8ECFF'), fr)
img = over(img, H('#9EA6D4'), fr * np.clip(yy - 190.3, 0, 1) * 0.9)

# ============ スピード線（馬のうしろ） ============
sl = aa_canvas()
sr = np.random.default_rng(33)
for i in range(60):
    y = sr.uniform(150, 312); x = sr.uniform(-80, W - 60); L = sr.uniform(50, 240)
    wd = sr.uniform(1.0, 2.6)
    n_ = 10
    for k in range(n_):
        t0, t1 = k / n_, (k + 1) / n_
        th = wd * math.sin(math.pi * (t0 + t1) / 2)
        cv2.line(sl, (int((x + L * t0) * 64), int(y * 64)), (int((x + L * t1) * 64), int(y * 64)), sr.uniform(0.5, 1.0), max(1, int(th * 4)), cv2.LINE_AA, shift=4)
sl = down(sl)
img = img + sl[..., None] * H('#D8E2FF') * 0.28


# ============ 砂けむり ============
def dust_puffs(img, hx, hy, scl, dim, seed, n=22):
    """けり上げた砂けむり：うしろ足のうしろに、うしろへ広がりながら上がる雲。
       丸を重ねた形をひとつの雲にして、ふちの向きで「右上は明るい・左下は影」をくっきり塗る（うしろほど うすい）＋とぶ砂の粒"""
    r_ = np.random.default_rng(seed)
    S2 = 3
    x0, x1 = int(max(0, hx - 160 * scl - 40)), int(min(W, hx + 26))
    y0, y1 = int(max(0, hy - 100 * scl - 24)), int(min(Hh, hy + 10))
    if x1 <= x0 or y1 <= y0:
        return img
    cw, ch = (x1 - x0) * S2, (y1 - y0) * S2
    base, shade, lite = H('#BC9E8A'), H('#86685E'), H('#F2E2D0')
    M = np.zeros((ch, cw), np.uint8)
    fade = np.zeros((ch, cw), np.float32)
    for i in range(n):
        t = (i + r_.uniform(0, 1)) / n                                # うしろへの きょり（0：足もと 〜 1：うしろ）
        r = (8 + 13 * t + r_.uniform(-2.5, 3.5)) * scl
        px = hx - 2 * scl - t * 115 * scl + r_.normal(0, 3) * scl
        hmax = (4 + 40 * t) * scl
        py = hy - r * 0.50 - r_.uniform(0, 1) ** 1.2 * hmax
        cv2.circle(M, (int((px - x0) * S2 * 16), int((py - y0) * S2 * 16)), int(max(2, r) * S2 * 16), 255, -1, cv2.LINE_AA, shift=4)
    M = M.astype(np.float32) / 255
    xs_ = (np.arange(cw)[None, :] / S2 + x0)
    fade = np.clip(1.0 - (hx - xs_) / (125 * scl) * 0.66, 0.26, 0.95) * np.ones((ch, 1), np.float32)
    sig = 2.2 * scl * S2
    Mb = cv2.GaussianBlur(M, (0, 0), sig)
    gx = cv2.Sobel(Mb, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(Mb, cv2.CV_32F, 0, 1, ksize=3)
    gn = np.sqrt(gx * gx + gy * gy) + 1e-6
    face = (-gx * 0.62 + gy * 0.78) / gn                             # 外向きが右上（光の方）なら＋
    edge = ss_(0.02, 0.10, gn / (gn.max() + 1e-6) * 4)                # ふちの近く
    lit = ss_(0.30, 0.42, face) * edge * M
    shd = ss_(-0.20, -0.32, face) * edge * M
    c = np.zeros((ch, cw, 3), np.float32) + base
    c = c * (1 - shd[..., None]) + shade * shd[..., None]
    c = c * (1 - lit[..., None]) + lite * lit[..., None]
    al = M * fade
    col = c
    for i in range(int(30 * scl) + 6):                                # とぶ砂の粒（小さなかたまり・うしろへ短い筋）
        px = (hx - r_.uniform(-8, 110) * scl - x0) * S2; py = (hy - r_.uniform(3, 64) * scl - y0) * S2
        rr = r_.uniform(0.7, 1.8) * S2 * max(0.6, scl)
        clod = np.zeros((ch, cw), np.uint8)
        cv2.ellipse(clod, (int(px * 16), int(py * 16)), (int(rr * 1.25 * 16), int(rr * 16)), r_.uniform(0, 180), 0, 360, 255, -1, cv2.LINE_AA, shift=4)
        cv2.line(clod, (int(px * 16), int(py * 16)), (int((px + rr * 3.5) * 16), int((py + rr * 0.8) * 16)), 110, max(1, int(rr * 0.7)), cv2.LINE_AA, shift=4)
        cm = clod.astype(np.float32) / 255
        col = over(col, H('#5A3E36'), cm); al = np.maximum(al, cm)
        hl = np.zeros((ch, cw), np.uint8)
        cv2.circle(hl, (int((px - rr * 0.3) * 16), int((py - rr * 0.35) * 16)), int(rr * 0.42 * 16), 255, -1, cv2.LINE_AA, shift=4)
        col = over(col, H('#D8BCA4'), hl.astype(np.float32) / 255 * cm)
    colS = cv2.resize(col * al[..., None], (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
    alS = cv2.resize(al, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
    rgbS = colS / np.maximum(alS[..., None], 1e-4) * dim
    img = img.copy()
    img[y0:y1, x0:x1] = over(img[y0:y1, x0:x1], rgbS, alS)
    return img


# ============ 3頭（奥 → 手前） ============
HORSES = [
    dict(box=(486, 120, 652, 238), num=5, seed=5, tail=0.85, mane=0.72, coat='chestnut', legs='socks', silk='blue', sleeve='white', helmet='blue', lw=0.85,
         pose=dict(theta=-2.0, neck_rot=-34.0, head_ang=-34.0, fore=dict(L=[-84, -24, -50, -30], R=[-112, -52, -128, -155]),
                   hind=dict(L=[-122, -158, -140, -160], R=[-82, -120, -96, -76]), tail=[-168, -156]), haze=0.20),
    dict(box=(46, 126, 268, 268), num=3, seed=3, tail=0.80, mane=0.72, coat='darkbay', legs='black', silk='green', sleeve='yellow', helmet='yellow', lw=0.92,
         roll=True,
         pose=dict(theta=1.0, neck_rot=-32.0, head_ang=-34.0, fore=dict(L=[-96, -48, -44, -28], R=[-128, -36, -140, -165]),
                   hind=dict(L=[-118, -150, -128, -150], R=[-70, -112, -84, -62]), tail=[-166, -154]), haze=0.10),
    dict(box=(256, 104, 556, 300), num=7, seed=7, tail=1.52, tail_ang=153, tail_spread=0.055, tail_wave=1.0, mane=0.72, coat='bay', legs='black', silk='red', sleeve='white', helmet='red', lw=1.0,
         pose=dict(theta=0.0, neck_rot=-36.0, head_ang=-32.0, fore=dict(L=[-100, -40, -30, -18], R=[-132, -28, -150, -170]),
                   hind=dict(L=[-112, -152, -136, -156], R=[-56, -106, -76, -56]), tail=[-170, -158]), haze=0.0),
]
HAZE = H('#2E2C66')
for k, h in enumerate(HORSES):
    R = render_anime(h['pose'], h['box'], W, Hh, name=f'anight{k}')
    rgb, a = paint_anime(R, h)
    hv = np.asarray(R['hooves'], float) / R['s']
    gy = hv[:, 1].max() + 1.5
    x0, x1 = hv[:, 0].min(), hv[:, 0].max()
    scl = (gy - Y0) / (Hh - Y0)
    # 影（ふちのはっきりした横長の影）
    sh = aa_canvas()
    cv2.ellipse(sh, (int((x0 + x1) / 2 * 64), int(gy * 64)), (int((x1 - x0) / 2 * 1.02 * 64), int((5.5 * scl + 1.2) * 64)), 0, 0, 360, 1.0, -1, cv2.LINE_AA, shift=4)
    for hx_, hy_ in hv:                                               # 地面に近いひづめの下の小さな影
        if gy - hy_ < 10 * scl + 2:
            cv2.ellipse(sh, (int(hx_ * 64), int(gy * 64)), (int(7 * scl * 64 + 64), int(2 * scl * 64 + 32)), 0, 0, 360, 1.0, -1, cv2.LINE_AA, shift=4)
    sh = down(sh)
    img = img * (1 - sh[..., None] * 0.38)
    img = dust_puffs(img, hv[2:, 0].min(), gy, scl, 1.0 - h['haze'] * 0.8, 200 + k)
    rgb = rgb * (1 - h['haze']) + HAZE * h['haze']
    img = over(img, rgb, a)

# ============ 手前の柵 ============
RY = 302
post = aa_canvas(); rail = aa_canvas()
for x in range(30, W, 92):
    cv2.rectangle(post, (int((x - 4) * 64), int(RY * 64)), (int((x + 4) * 64), int(Hh * 64)), 1.0, -1, cv2.LINE_AA, shift=4)
cv2.rectangle(rail, (0, int((RY - 4) * 64)), (W * 64, int((RY + 5) * 64)), 1.0, -1, cv2.LINE_AA, shift=4)
post = down(post); rail = down(rail)
img = img * (1 - (np.roll(post, 4, axis=1) * 0.30)[..., None])                         # 支柱の影
pshade = np.clip(((xx - 30) % 92) - 0.5, 0, 1) * (((xx - 30) % 92) < 46)           # 支柱の右半分は影
img = over(img, H('#F2F4FF') * (1 - pshade[..., None]) + H('#AAB2DC') * pshade[..., None], post)
rshade = np.clip(yy - (RY + 0.5), 0, 1)
img = over(img, H('#F6F8FF') * (1 - rshade[..., None]) + H('#B0B8E0') * rshade[..., None], rail)
img = np.maximum(img, (np.exp(-((yy - (RY - 2.6)) / 0.7) ** 2) * (rail > 0.5))[..., None] * 1.0)   # レールのつや
um = ((post + rail) > 0.5).astype(np.uint8)
ol = cv2.morphologyEx(um, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)).astype(np.float32) * (yy < Hh - 1)
img = over(img, LINE, cv2.GaussianBlur(ol, (3, 3), 0.5) * 0.8)
save_webp(np.clip(img, 0, 1), out)
print(out)
