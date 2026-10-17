"""銀（780×320）：全力で駆ける 銀の馬の像（一から作った創作の絵）。全体を銀でまとめる
   色はパレット（PAL）にまとめてある。金の壁紙（flat/gold_banner.py）は、同じ像・同じ作りで GOLD のパレットを使う
   - 像：flat/silver_horse.py（3Dの馬＋うしろへ流れるたてがみ・しっぽ）を、みがいた銀（クロム）の金属で描く。
     まわりの光（上は白・地平は灰・下は暗い）が体に映る。手前の前足のひづめが床につく
   - 背景：明るい銀の地（ヘアライン＝横の細いすじ）・像のうしろのやわらかい光・みがいた床（像がうつる）・床の影・
     ふちの暗がり・像のいちばん明るい所に小さなきらめき
   python3 flat/silver_banner.py <出力.webp>（sdfr がいる）"""
import sys, os, math, shutil
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
sys.path.insert(0, os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import style2d as S2
from style2d import frame_horse, save_webp, grad_v, over
from h3d import Scene, nrm
from fire2d import aces, to_srgb
from paint import fbm, blur, smoothstep
import silver_horse as SH

W, Hh = 780, 320
BOX = (84, 46, 696, 262)            # 体（たてがみ・しっぽをのぞく）が入る箱
AZIM, ELEV = -6.0, 5.0

# 色（銀）：まわりの光（上は白い光・地平はうすい灰・下は暗い灰：クロムに映る）・像の金属・背景・床・きらめき
SILVER = dict(
    env=((1.00, 1.00, 1.03), (0.11, 0.115, 0.13), (0.025, 0.027, 0.03), (0.0, 0.0, 0.0)),
    lobes=(((0.30, 0.90, -0.40), (2.2, 2.2, 2.25), 6.0),               # 上・手前のやわらかい光（はっきりした明るい帯）
           ((-0.60, 0.30, 0.60), (0.9, 0.95, 1.05), 10.0)),            # うしろからのふちの光
    lights=(((0.55, 0.65, -0.55), (1.0, 1.0, 1.05), 10, 1),            # 主光
            ((-0.50, 0.30, -0.60), (0.25, 0.25, 0.28), 8, 0)),         # 補助
    metal=(0.82, 0.84, 0.88), rough=0.08,                              # 像：みがいた銀（クロム）
    bg=[(0, '#E4E7EB'), (0.5, '#AEB5BD'), (1, '#747B83')],             # 銀の地（上は明るく・下は少し暗く）
    glow=(0.16, 0.16, 0.17), ring=(1.0, 1.0, 1.0), streak=(0.12, 0.12, 0.13),
    floor=[(0, '#5A6168'), (1, '#2B3036')], spark=(1.0, 1.0, 1.0))


def render3d(tmp, pal=SILVER):
    pose = dict(SH.POSE)
    S2.TMP = tmp
    e, t = frame_horse(pose, BOX, W, Hh, facing='left', azim=AZIM, elev=ELEV)
    sc = Scene()
    sc.image(W, Hh, 2)
    sc.camera(e, t, 26)
    sc.bounce(1)
    sc.env(*pal['env'])
    for d, c, k in pal['lobes']:
        sc.lobe(d, c, k)
    for d, c, k, shadow in pal['lights']:
        sc.light(d, c, k, shadow)
    sc.mat(1, 0, pal['metal'], pal['rough'], 0, 0, 0.0)
    sc.bump(1, 1, 2.6, 0.0035)                                      # 鋳物のかすかなうねり（映りこみがゆれる）
    S = SH.build_statue(sc, pose, mats=dict(body=1, neck=1, hoof=1, eye=1, head=1))
    R = sc.render(os.path.join(tmp, 'silver'))
    return R, S


def compose(R, rng_seed=5, pal=SILVER):
    rng = np.random.default_rng(rng_seed)
    yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
    A = np.clip(R['a'], 0, 1)
    rgb = to_srgb(aces(R['rgb'] / np.maximum(R['a'], 1e-4)[..., None] * 1.0))
    # 床の線：ひづめのいちばん下
    rows = np.nonzero(A.sum(1) > 0.5)[0]
    gy = int(rows.max())
    # ---------- 背景：銀の地（上は明るく・下は少し暗く）＋ヘアライン ----------
    bg = grad_v(Hh, W, pal['bg'])
    hair = fbm(Hh, W, 3, 2, seed=8)
    hair = cv2.GaussianBlur((hair - .5) * 2, (0, 0), sigmaX=22, sigmaY=0.4)      # 横に長くのばす
    bg = bg * (1 + 0.06 * hair[..., None])
    glow = np.exp(-(((xx - W * .46) / 300) ** 2 + ((yy - gy * 0.55) / 150) ** 2))
    bg = bg + glow[..., None] * np.array(pal['glow'])
    # 大きなうすい輪（銀のメダルのように：像のうしろ）
    rr = np.sqrt(((xx - W * .5) ** 2 + (yy - gy * 0.52) ** 2))
    ring = np.exp(-((rr - 150) / 3.0) ** 2) * 0.14 + smoothstep(152, 140, rr) * 0.05
    bg = bg + ring[..., None] * np.array(pal['ring'])
    # 走る勢い（像のうしろへ流れる、やわらかい銀のすじ）
    streak = np.zeros((Hh, W), np.float32)
    for i in range(9):
        y0 = rng.uniform(gy * 0.25, gy * 0.92)
        x0 = rng.uniform(W * .45, W * .78)
        L = rng.uniform(120, 300)
        cv2.line(streak, (int(x0 * 16), int(y0 * 16)), (int((x0 + L) * 16), int(y0 * 16)), float(rng.uniform(.4, 1.0)), int(rng.uniform(1.2, 3.0) * 16 / 16 + 1), cv2.LINE_AA, shift=4)
    streak = cv2.GaussianBlur(streak, (0, 0), sigmaX=18, sigmaY=1.2)
    bg = bg + streak[..., None] * np.array(pal['streak'])
    # 床：床の線から下は、みがいた暗い銀。像がさかさまにうつる
    floor = smoothstep(gy - 2, gy + 6, yy)
    fcol = grad_v(Hh, W, pal['floor'])
    bg = bg * (1 - floor[..., None]) + fcol * floor[..., None]
    refl_rgb = np.zeros_like(rgb); refl_a = np.zeros_like(A)
    h = Hh - gy - 1
    if h > 0:
        src_rgb = rgb[gy - h:gy][::-1]
        src_a = A[gy - h:gy][::-1]
        refl_rgb[gy + 1:gy + 1 + h] = src_rgb
        refl_a[gy + 1:gy + 1 + h] = src_a
    fade = np.clip(1 - (yy - gy) / 75.0, 0, 1) ** 1.3 * 0.7
    refl_rgb = blur(refl_rgb, 1.6); refl_a = blur(refl_a, 1.6)
    bg = bg * (1 - (refl_a * fade)[..., None]) + refl_rgb * (refl_a * fade)[..., None]
    # 床の影（ひづめのそば）と、像の下のやわらかい影
    cols = np.nonzero(A[gy - 3:gy + 1].sum(0) > 0.5)[0]
    hx = float(cols.mean()) if len(cols) else W * 0.35
    sh = np.exp(-(((xx - hx) / 60) ** 2 + ((yy - gy) / 5) ** 2)) * 0.35
    body_cols = np.nonzero(A.sum(0) > 0.5)[0]
    sh2 = np.exp(-(((xx - body_cols.mean()) / 230) ** 2 + ((yy - gy - 10) / 22) ** 2)) * 0.18
    bg = bg * (1 - (sh + sh2)[..., None])
    # ---------- 像を重ねる ----------
    img = over(bg, rgb, A)
    # きらめき（いちばん明るい所に4本の光）
    lum = (rgb.max(2) * A)
    lum_s = cv2.GaussianBlur(lum, (0, 0), 1.0)
    spark = np.zeros((Hh, W), np.float32)
    taken = []
    order = np.argsort(lum_s.ravel())[::-1]
    for idx in order[:4000]:
        y, x = divmod(int(idx), W)
        if lum_s[y, x] < 0.9:
            break
        if all((x - tx) ** 2 + (y - ty) ** 2 > 90 ** 2 for tx, ty in taken):
            taken.append((x, y))
        if len(taken) >= 4:
            break
    for (x, y) in taken:
        L = rng.uniform(12, 20)
        for (dx, dy, l) in ((1, 0, L), (0, 1, L * 0.75), (0.7, 0.7, L * 0.35), (0.7, -0.7, L * 0.35)):
            for s in (1, -1):
                cv2.line(spark, (int(x * 16), int(y * 16)), (int((x + dx * l * s) * 16), int((y + dy * l * s) * 16)), 1.0, 1, cv2.LINE_AA, shift=4)
        cv2.circle(spark, (int(x * 16), int(y * 16)), int(2.2 * 16), 1.0, -1, cv2.LINE_AA, shift=4)
    spark = spark * 0.9 + blur(spark, 2.0) * 0.6 + blur(spark, 7.0) * 0.4
    img = img + spark[..., None] * np.array(pal['spark']) * 0.9
    # ふちの暗がり（上は明るいまま）
    v = np.clip(1.04 - np.sqrt(((xx - W * .5) / (W * .72)) ** 2 + ((yy - Hh * .40) / (Hh * .95)) ** 2) * .22, .6, 1)[..., None]
    img = img * v
    # 金属らしいコントラスト（少し締める）
    img = np.clip(img, 0, 1)
    img = np.clip(img + (img - 0.5) * 0.08 * (1 - np.abs(img - 0.5) * 2), 0, 1)
    return img.astype(np.float32)


if __name__ == '__main__':
    out = sys.argv[1]
    tmp = os.path.join(S2.TMP, f'silver{os.getpid()}')
    os.makedirs(tmp, exist_ok=True)
    try:
        R, S = render3d(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    img = compose(R)
    save_webp(img, out)
