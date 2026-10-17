"""ナイターの絵（780×320）：夜空・スタンドの光・照明の塔と光の筋は前の nightrace.py のまま、
   コース（ダート）と3頭（騎手つき）をリアルに描き直す
   - ダート：遠近のついた ならした筋・ひづめのあと・照明の光だまり・馬の影・けり上げた砂
   - 柵：奥の白い柵（細い支柱）と、手前の白い柵（太い支柱・つやのある丸いレール）
   - 馬：3Dの馬と騎手を照明の光で（flat/real_rider.py）。毛色・勝負服・番号・走り方は3頭ともちがう
   python3 flat/night_banner.py <出力.webp>"""
import sys, os, math
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from real_rider import *          # style2d・render_real・finish・cloth_number
from paint import fbm

W, Hh = 780, 320
out = sys.argv[1]
rng = np.random.default_rng(101)
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)

# ---------- 夜空・スタンド・照明（前の絵と同じ） ----------
img = grad_v(Hh, W, [(0, '#090C24'), (0.55, '#1E1B4B'), (0.62, '#2A2A5E'), (1, '#1A1A33')])
stand = np.clip((yy - (150 - 18 * np.exp(-((xx - 390) / 300) ** 2))) / 1.5 + .5, 0, 1) * (yy < 190)
img = over(img, hexc('#14163A'), stand)
for i in range(500):
    x = rng.uniform(0, W); y = rng.uniform(138, 186)
    if stand[int(y), int(x)] > .5:
        img[int(y), int(x)] = img[int(y), int(x)] * 0.3 + hexc(['#FFE7A8', '#FFFFFF', '#A8C8FF'][rng.integers(0, 3)]) * 0.7
for tx, ty in [(70, 40), (720, 34), (390, 20)]:
    cv2.line(img, (int(tx), int(ty)), (int(tx), 190), (0.08, 0.08, 0.16), 4)
    lamp = np.zeros((Hh, W), np.float32)
    for i in range(3):
        for j in range(5):
            cv2.circle(lamp, (int((tx - 16 + j * 8) * 4), int((ty - 8 + i * 7) * 4)), int(3 * 4), 1.0, -1, cv2.LINE_AA, shift=2)
    lamp = np.clip(lamp, 0, 1)
    img = img + blur(lamp, 18)[..., None] * hexc('#BFD4FF') * 1.1 + blur(lamp, 60)[..., None] * hexc('#7F8BFF') * 0.5
    img = np.maximum(img, lamp[..., None])
    ang = np.arctan2(yy - ty, xx - tx)
    rays = (np.sin(ang * 22) > 0.85) * np.exp(-np.sqrt((xx - tx) ** 2 + (yy - ty) ** 2) / 120) * 0.2
    img = img + rays[..., None] * hexc('#DCE6FF')

# ---------- ダートのコース（遠近つき） ----------
TOP, Y0 = 194, 150                                       # 奥の柵の高さ・遠近の消える高さ
trk = (yy >= TOP).astype(np.float32)
dep = 1.0 / np.maximum(yy - Y0, 1.0)                     # 遠いほど大きい
U = (xx - W / 2) * dep * 34.0                             # 遠近の横
V = dep * 900.0                                           # 遠近の縦
big = fbm(512, 512, 24, 5, seed=41)                       # 1枚の模様を遠近で貼る
streak_src = fbm(512, 512, 6, 3, seed=42)
def tex(src, su, sv):
    mx = np.mod(U * su, 511.0).astype(np.float32); my = np.mod(V * sv, 511.0).astype(np.float32)
    return cv2.remap(src, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
mott = tex(big, 1.0, 1.0)                                 # まだら
streak = tex(streak_src, 0.08, 6.0)                       # ならした筋（横に長い）
base = np.zeros((Hh, W, 3), np.float32) + hexc('#5B4334')
base = base * (0.80 + 0.30 * mott[..., None]) * (0.88 + 0.22 * streak[..., None])
# 照明の光だまり（照明の下が明るい）と、遠くほど暗く・青く
pool = np.zeros((Hh, W), np.float32)
for tx in (70, 390, 720):
    pool += np.exp(-(((xx - tx) / 230) ** 2 + ((yy - 250) / 60) ** 2))
light = 0.55 + 0.75 * np.clip(pool, 0, 1.3)
far = np.clip((yy - TOP) / (Hh - TOP), 0, 1)
dirt = base * light[..., None] * (0.70 + 0.30 * far)[..., None] + hexc('#2A2F5A') * (1 - far)[..., None] * 0.18
img = img * (1 - trk[..., None]) + dirt * trk[..., None]

# ひづめのあと（遠いほど小さく・うすく）
hp = np.zeros((Hh * 2, W * 2), np.float32)
pr = np.random.default_rng(7)
for i in range(900):
    y = TOP + 4 + (Hh - TOP - 4) * pr.random() ** 0.8
    x = pr.uniform(0, W)
    s = (y - Y0) / (Hh - Y0)
    cv2.ellipse(hp, (int(x * 2 * 16), int(y * 2 * 16)), (int(max(1.2, 4.2 * s) * 2 * 16), int(max(0.6, 1.5 * s) * 2 * 16)), pr.uniform(-12, 12), 0, 360,
                pr.uniform(0.35, 1.0), -1, cv2.LINE_AA, shift=4)
hp = cv2.resize(hp, (W, Hh), interpolation=cv2.INTER_AREA)
img = img * (1 - (hp * 0.32 * trk)[..., None])
img = img + (np.roll(hp, -1, axis=0) * 0.10 * trk)[..., None] * hexc('#C8AA8A')          # あとのふちの明るい所

# 奥の柵（白いレールと細い支柱）
fr = np.zeros((Hh * 4, W * 4), np.float32)
cv2.line(fr, (0, 191 * 4 * 4), (W * 4 * 4, 191 * 4 * 4), 1.0, 9, cv2.LINE_AA, shift=2)
for x in range(4, W, 22):
    cv2.line(fr, (x * 4 * 4, 191 * 4 * 4), (x * 4 * 4, 201 * 4 * 4), 0.85, 5, cv2.LINE_AA, shift=2)
fr = cv2.resize(fr, (W, Hh), interpolation=cv2.INTER_AREA)
img = img * (1 - (blur(fr, 2.0) * 0.35)[..., None] * (yy > 192)[..., None])
img = over(img, hexc('#E9ECF6'), fr)

# ---------- 3頭（奥 → 手前） ----------
HORSES = [
    dict(box=(486, 120, 652, 238), num=5, seed=5, tail=0.9, coat='#6E3416', silk='#1F3FA8', sleeve='#F2F2F2', helmet='#1F3FA8',
         pose=dict(theta=-2.0, neck_rot=-34.0, head_ang=-34.0, fore=dict(L=[-84, -24, -50, -30], R=[-112, -52, -128, -155]),
                   hind=dict(L=[-122, -158, -140, -160], R=[-82, -120, -96, -76]), tail=[-168, -156]), dim=0.82),
    dict(box=(46, 126, 268, 268), num=3, seed=3, coat='#3A1C0E', silk='#0E7A3D', sleeve='#F4C430', helmet='#F4C430', tail=0.85,
         pose=dict(theta=1.0, neck_rot=-32.0, head_ang=-34.0, fore=dict(L=[-96, -48, -44, -28], R=[-128, -36, -140, -165]),
                   hind=dict(L=[-118, -150, -128, -150], R=[-70, -112, -84, -62]), tail=[-166, -154]), dim=0.92),
    dict(box=(256, 104, 556, 300), num=7, seed=7, tail=0.72, coat='#5A2812', silk='#C8102E', sleeve='#F2F2F2', helmet='#C8102E',
         pose=dict(theta=0.0, neck_rot=-36.0, head_ang=-32.0, fore=dict(L=[-100, -40, -30, -18], R=[-132, -28, -150, -170]),
                   hind=dict(L=[-112, -152, -136, -156], R=[-56, -106, -76, -56]), tail=[-170, -158]), dim=1.0),
]
for k, h in enumerate(HORSES):
    cols = dict(coat=h['coat'], silk=h['silk'], sleeve=h['sleeve'], helmet=h['helmet'])
    R = render_real(h['pose'], h['box'], W, Hh, cols, name=f'night{k}')
    rgb, a = finish(R, cols, seed=h['seed'], tail_len=h['tail'])
    rgb = cloth_number(rgb, R, h['num'])
    hv = np.asarray(R['hooves'], float)
    gy = hv[:, 1].max() + 2
    x0, x1 = hv[:, 0].min(), hv[:, 0].max()
    scl = (gy - Y0) / (Hh - Y0)
    # 影：照明は左上と右上 → 体の下に横長の影＋少し右へのびる影
    sh = np.zeros((Hh, W), np.float32)
    cv2.ellipse(sh, (int((x0 + x1) / 2 * 16), int(gy * 16)), (int((x1 - x0) / 2 * 1.05 * 16), int(7 * scl * 16 + 16)), 0, 0, 360, 1.0, -1, cv2.LINE_AA, shift=4)
    body = cv2.resize(cv2.resize(a, (W, max(1, int(Hh * 0.10)))), (W, Hh))
    img = img * (1 - (blur(sh, 5 * scl + 1) * 0.55)[..., None])
    # けり上げた砂（うしろ足のうしろ・ふわっと光る）
    dr = np.random.default_rng(100 + k)
    dust = np.zeros((Hh, W), np.float32); haze = np.zeros((Hh, W), np.float32)
    hx, hy = hv[2:, 0].min(), gy
    for i in range(70):
        r = abs(dr.normal(0, 1)) * 40 * scl + 3
        px = hx - r * 1.3 - dr.uniform(0, 8); py = hy - abs(dr.normal(0, 1)) * 18 * scl - 2
        cv2.circle(dust, (int(px * 16), int(py * 16)), int(max(0.6, dr.uniform(0.6, 1.8) * scl) * 16), dr.uniform(0.4, 1.0), -1, cv2.LINE_AA, shift=4)
    cv2.ellipse(haze, (int((hx - 26 * scl) * 16), int((hy - 8 * scl) * 16)), (int(34 * scl * 16), int(12 * scl * 16)), 0, 0, 360, 1.0, -1, cv2.LINE_AA, shift=4)
    img = img + blur(haze, 8 * scl + 2)[..., None] * hexc('#8C7A6A') * 0.30 * h['dim']
    img = over(img, hexc('#A89078'), blur(dust, 0.6) * 0.75)
    img = over(img, rgb * h['dim'], a)

# ---------- 手前の柵（太い支柱・丸いレール） ----------
RY = 302
post = np.zeros((Hh, W), np.float32); rail = np.zeros((Hh, W), np.float32)
for x in range(30, W, 92):
    cv2.rectangle(post, (int((x - 4) * 4), int(RY * 4)), (int((x + 4) * 4), int(Hh * 4)), 1.0, -1, cv2.LINE_AA, shift=2)
cv2.rectangle(rail, (0, int((RY - 4) * 4)), (W * 4, int((RY + 5) * 4)), 1.0, -1, cv2.LINE_AA, shift=2)
shade_p = np.clip(0.75 + 0.35 * np.sin((xx % 92 - 26) / 8 * math.pi / 2), 0.55, 1.1)             # 支柱の丸み
img = img * (1 - (blur(np.roll(post, 6, axis=1) * 0.35, 3))[..., None])                         # 支柱の影
img = over(img, hexc('#DADDE8') * shade_p[..., None], post)
rail_shade = np.clip(1.08 - np.abs(yy - (RY - 1.5)) / 7, 0.55, 1.08)                              # レールの上が光る
img = img * (1 - (blur(np.roll(rail, 5, axis=0) * 0.30, 2.5))[..., None])
img = over(img, hexc('#E6E9F2') * rail_shade[..., None], rail)
img = np.maximum(img, (np.exp(-((yy - (RY - 2.5)) / 0.9) ** 2) * (rail > 0.5))[..., None] * 0.98)    # レールのつやの線
save_webp(np.clip(img, 0, 1), out)
print(out)
