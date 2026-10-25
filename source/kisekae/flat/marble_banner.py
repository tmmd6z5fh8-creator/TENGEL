"""大理石（780×320）：あたたかい白の地・うすい大理石のすじ・金の帯の台・金の月桂樹は前の r3d/banners/marble.py のまま、
   像の馬だけ描き直す → 後ろ足で立ち上がる大理石の馬（波打つたてがみ・ねじれながら台までとどくしっぽ・岩の台座）
   カメラと台は前と同じ（同じ位置・同じ大きさ）。像は少しこちらを向く。形はすべて一から作ったオリジナル（flat/marble_horse.py）
   python3 flat/marble_banner.py <出力.webp>"""
import sys, os, math
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
sys.path.insert(0, os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
from style2d import *
from h3d import Scene, nrm
import horse3d as Hm
from fire2d import aces, to_srgb
from paint import fbm, warp
import marble_horse as MH

W, Hh = 780, 320
yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
ROCK = 0.10                                                 # 岩の台座の高さ（台の上）
YAW, G = 16.0, 0.98                                         # 像の向き（少しこちらへ）・大きさ


def background():
    """あたたかい白・うすい大理石のすじ"""
    img = grad_v(Hh, W, [(0, '#F4F0E8'), (1, '#E6DFD2')])
    v = np.sin(xx / 60 + yy / 35 + warp(fbm(Hh, W, 120, 4, seed=2), (fbm(Hh, W, 160, 3, seed=3) - .5) * 80, xx * 0) * 9)
    vein = (1 - np.abs(v)) ** 10
    img = img * (1 - 0.035 * vein[..., None])
    vig = np.exp(-(((xx - 400) / 330) ** 2 + ((yy - 150) / 200) ** 2))
    return img * (0.90 + 0.10 * vig[..., None])


def camera():
    """カメラと台：前の絵と同じ（前の像のポーズで決めたカメラ）→ (eye, tgt, 台のまん中 PX, 地面 gy)"""
    pose0 = dict(Hm.REAR)
    S0 = Hm.skeleton(pose0)
    gy = S0['ground']
    TMPD = os.path.join(TMP, f'marble{os.getpid()}')        # このプロセスだけの作業フォルダ
    os.makedirs(TMPD, exist_ok=True)
    import style2d as S2
    S2.TMP = TMPD
    e, t = frame_horse(pose0, (268, 10, 530, 248), W, Hh, facing='left', azim=-6, elev=8)
    hx = np.mean([S0['HL']['hf'][0], S0['HR']['hf'][0]])
    return e, t, hx - 0.05, gy                              # 台のまん中（x）


def scene(cam, ss=2, rect=None, psi=0.0, look=0.0, spin_c=None, horse=True, look_kw=None, pose=None):
    """場面：像（psi＝台の上で まわす角度・look＝首と頭を うしろへ ふり向ける角度・pose＝骨組み（ヒヒィーン）：flat/marble_run.py）と台"""
    e, t, PX, gy = cam
    sc = Scene()
    sc.image(W, Hh, ss, rect)
    sc.camera(e, t, 26)
    sc.bounce(1)
    sc.env((0.85, 0.82, 0.78), (0.55, 0.52, 0.48), (0.25, 0.23, 0.20))
    sc.lobe((0.3, 0.9, -0.4), (1.6, 1.55, 1.45), 4.0)
    sc.light((0.6, 0.7, -0.6), (2.2, 2.1, 1.9), 10, 1)
    sc.light((-0.7, 0.4, 0.5), (0.8, 0.8, 0.85), 8, 0)
    sc.mat(1, 3, (0.95, 0.93, 0.89), 0.2, 3.2, 8.0)              # 台（前と同じ）
    sc.mat(7, 0, (1.0, 0.78, 0.40), 0.18)                        # 金の帯
    sc.mat(3, 3, (0.95, 0.935, 0.90), 0.22, 2.0, 5.0)            # 像：すじの少ない白い大理石
    sc.mat(2, 3, (0.93, 0.91, 0.87), 0.35, 3.2, 8.0)             # 岩の台座：少しざらざら
    sc.bump(2, 1, 5.0, 0.12)
    # 像：後ろ足のひづめを、台の上の岩にのせる（少しこちらを向く：yaw 16°・大きさ 0.98 倍で、てっぺんは前の像と同じ高さ）
    foot = np.array([PX + 0.30, gy + ROCK, 0.0])
    st = MH.Spin(sc, psi, spin_c if spin_c is not None else (PX, 0.0, 0.0)) if psi else sc
    if horse:
        # のど元（まさちゃんが引いた黄色の線に合わせる）：あごの下のふくらみをとって、のどの線は首の骨組みにそわせ、
        # 首の根元の太さは残す。ほおの下のふくらみも小さく。首の横に、のど元から肩へ向かう すじを彫る
        S = MH.build_statue(st, foot, yaw=YAW, g=G, pose=pose or MH.POSE, mats=dict(body=3, neck=3, hoof=3, eye=3, head=3),
                            throat=dict(neck_k=0.03, neck_k_from=0.3, amount=0.9, jowl=1.0), groove=True, look=look, **(look_kw or {}))
        MH.rock(st, foot, S['tail_end_world'], gy + ROCK)
    sc.rbox(np.array([PX, gy - 0.30, 0.0]), (0.62, 0.30, 0.42), 0.03, k=0.0, mat=1)
    sc.rbox(np.array([PX, gy - 0.05, 0.0]), (0.645, 0.028, 0.445), 0.01, k=0.0, mat=7)
    sc.rbox(np.array([PX, gy - 0.56, 0.0]), (0.66, 0.035, 0.46), 0.01, k=0.0, mat=7)
    return sc


def render(sc, name='marble'):
    import style2d as S2
    R = sc.render(os.path.join(S2.TMP, name))
    for k in ('rgb', 'a', 'd', 'n', 'm', 'ao'):
        try:
            os.remove(os.path.join(S2.TMP, f'{name}_{k}.f32'))
        except OSError:
            pass
    return R


def compose(img, R, sc, cam):
    """台の下の影・像と台の絵・金の月桂樹（左右）"""
    e, t, PX, gy = cam
    rgb = to_srgb(aces(R['rgb'] / np.maximum(R['a'], 1e-4)[..., None] * 1.05))
    A = R['a']
    cx = sc.project(np.array([[PX, gy, 0.0]]))[0][0][0]           # 影は台の下（前の絵と同じ所）
    sh = np.exp(-(((xx - round(cx)) / 140) ** 2 + ((yy - (np.nonzero(A.sum(1) > 0)[0].max())) / 8) ** 2))
    img = img * (1 - 0.25 * sh[..., None])
    img = over(img, rgb, A)
    img = laurel(img, 160, 170, 120, math.radians(110), math.radians(250), 1)
    return laurel(img, 620, 170, 120, math.radians(110), math.radians(250), -1)


# 金の月桂樹（左右）：本物の 金の 月桂冠のように（2026/10/25 まさちゃん「大理石の左右の赤丸の中のものをもっとリアルに金ピカにして！」）
#   前は 平らな 金色（たての グラデーション 1枚）の 細い 茎と ひし形の 葉だった → 太い 丸い 茎（光の すじ）・細長く とがった 月桂樹の 葉を
#   茎の 先の 向きに そろえて 2列（少しずつ 重なる）・葉ごとに 金属の 照り（横方向の 明暗の 帯・葉脈の 線・先の 小さな 光）・金の 実（丸い 玉）・
#   うすい 落ち影。4倍で 描いて 縮める
LAUREL_COL = dict(shadow='#5E3F0C', dark='#8E6516', base='#C99A2E', light='#EFCF6C', hi='#FFF3C4', edge='#7A5611')


def _leaf_poly(p, d, n_, L, w, curve):
    """葉の 形（細長く 先が とがる・少し そる）。p：つけ根・d：葉の 向き（単位）・n_：横（単位）・L：長さ・w：はば・curve：そり（横への ずれ）"""
    pts = []
    for i in range(13):                                        # 片がわ（つけ根 → 先）
        t = i / 12
        half = w * math.sin(math.pi * t) ** 0.8 * (1 - 0.15 * t)
        c = curve * t * t
        pts.append(p + d * (L * t) + n_ * (half + c))
    for i in range(12, -1, -1):                                 # もう片がわ（先 → つけ根）
        t = i / 12
        half = w * math.sin(math.pi * t) ** 0.8 * (1 - 0.15 * t)
        c = curve * t * t
        pts.append(p + d * (L * t) + n_ * (-half + c))
    return np.array(pts)


def laurel(img, cx, cy, r, a0, a1, flip):
    S = 4
    H4, W4 = Hh * S, W * S
    yy4, xx4 = np.mgrid[0:H4, 0:W4].astype(np.float32) / S          # 1倍の 座標
    C = {k: hexc(v) for k, v in LAUREL_COL.items()}
    col = np.zeros((H4, W4, 3), np.float32)
    acc = np.zeros((H4, W4), np.float32)                             # 金の ぜんたいの α（影に 使う）
    light = np.array([-0.55, -0.83])                                 # 光の 向き（左上から）

    def paint(mask, rgb):
        nonlocal col, acc
        m = mask[..., None]
        col = col * (1 - m) + rgb * m
        acc = np.maximum(acc, mask)

    def fill_aa(polys, shape=(H4, W4)):
        m = np.zeros(shape, np.uint8)
        for q in polys:
            cv2.fillPoly(m, [np.round(np.asarray(q) * S * 16).astype(np.int32)], 255, cv2.LINE_AA, shift=4)
        return m.astype(np.float32) / 255

    # ---- 茎（丸い 金の 棒）：太さ 4.2px・暗い → 明るい → 光の すじ
    n = 72
    stem = np.array([(cx + math.cos(a) * r * flip, cy + math.sin(a) * r) for a in np.linspace(a0, a1, n)])
    def stroke(pts, wpx, val, off=(0, 0)):
        m = np.zeros((H4, W4), np.uint8)
        q = np.round((pts + np.array(off)) * S * 16).astype(np.int32)
        cv2.polylines(m, [q], False, 255, max(1, int(round(wpx * S))), cv2.LINE_AA, shift=4)
        return m.astype(np.float32) / 255
    paint(stroke(stem, 4.4, 1), C['dark'])
    paint(stroke(stem, 3.0, 1, (0.0, -0.3)), C['base'])
    paint(stroke(stem, 1.4, 1, (-0.4, -0.9)), C['light'])
    paint(stroke(stem, 0.6, 1, (-0.6, -1.2)) * 0.9, C['hi'])

    # ---- 葉：茎に そって 2列（左右）に、先の 向きへ 傾けて。つけ根が 先の 葉の 下に 少し 重なる
    rng = np.random.default_rng(5)
    leaves = []                                                        # (poly, p, d, n_, L, w, sgn)
    for k in range(3, n - 2, 4):
        p = stem[k]
        d = stem[min(k + 2, n - 1)] - stem[k - 2]; d = d / np.linalg.norm(d)   # 成長の 向き（茎の 先へ）
        nrm_ = np.array([-d[1], d[0]])
        for j, sgn in enumerate((1, -1)):
            ang = math.radians(38 + rng.uniform(-6, 6)) * sgn           # 茎から 開く 角度
            dl = np.array([d[0] * math.cos(ang) - d[1] * math.sin(ang), d[0] * math.sin(ang) + d[1] * math.cos(ang)])
            nl = np.array([-dl[1], dl[0]])
            L = 23 + rng.uniform(-2.5, 2.5)
            w = 4.6 + rng.uniform(-0.5, 0.5)
            base_pt = p + nrm_ * sgn * 1.2 - d * 2.5                      # つけ根は 茎の 少し うしろ
            poly = _leaf_poly(base_pt, dl, nl, L, w, curve=-sgn * 1.6)
            leaves.append((poly, base_pt, dl, nl, L, w, sgn))
    # 奥（茎の はじめ）から 手前へ 順に 描く（先の 葉が 上に 重なる）。計算は 葉の まわりの 四角だけ（速さの ため）
    for poly, p, dl, nl, L, w, sgn in leaves:
        bx0, by0 = max(0, int(poly[:, 0].min() * S) - 3), max(0, int(poly[:, 1].min() * S) - 3)
        bx1, by1 = min(W4, int(poly[:, 0].max() * S) + 4), min(H4, int(poly[:, 1].max() * S) + 4)
        if bx1 <= bx0 or by1 <= by0:
            continue
        sl = (slice(by0, by1), slice(bx0, bx1))
        m_full = fill_aa([poly])
        m = m_full[sl]
        if m.max() <= 0:
            continue
        # 葉の 中の 座標：t（つけ根 0 → 先 1）・u（まん中 0 → ふち ±1）
        rx, ry = xx4[sl] - p[0], yy4[sl] - p[1]
        t = (rx * dl[0] + ry * dl[1]) / L
        half = np.maximum(w * np.sin(np.pi * np.clip(t, 0, 1)) ** 0.8 * (1 - 0.15 * np.clip(t, 0, 1)), 0.3)
        u = (rx * nl[0] + ry * nl[1] - (-sgn * 1.6) * np.clip(t, 0, 1) ** 2) / half
        # 金属の 照り：光の 向きと 葉の 横の 向きで 明るい 帯の 位置が きまる。帯の 両がわは 暗く・ふちは もっと 暗く
        lit = float(nl[0] * light[0] + nl[1] * light[1])                 # 光が 当たる がわ（-1〜1）
        band = np.exp(-((u - 0.35 * lit) ** 2) / (2 * 0.33 ** 2))        # 明るい 帯
        glint = np.exp(-((u - 0.35 * lit) ** 2) / (2 * 0.12 ** 2)) * np.exp(-((t - 0.42) ** 2) / (2 * 0.16 ** 2))   # 小さな 強い 光
        shade_side = np.clip(-u * lit, 0, 1) ** 1.5 * 0.55                 # 光の 反対がわは 暗く
        edge = np.clip((np.abs(u) - 0.78) / 0.22, 0, 1) * 0.6             # ふち
        tipd = np.clip((t - 0.86) / 0.14, 0, 1) * 0.25                     # 先は 少し 暗く（厚みが ある 感じ）
        rgb = C['base'][None, None, :] * np.ones((by1 - by0, bx1 - bx0, 1), np.float32)
        rgb = rgb * (1 - band[..., None] * 0.85) + C['light'] * band[..., None] * 0.85
        rgb = rgb * (1 - glint[..., None] * 0.9) + C['hi'] * glint[..., None] * 0.9
        rgb = rgb * (1 - shade_side[..., None]) + C['dark'] * shade_side[..., None]
        rgb = rgb * (1 - edge[..., None]) + C['edge'] * edge[..., None]
        rgb = rgb * (1 - tipd[..., None]) + C['dark'] * tipd[..., None]
        # 葉脈：まん中の 細い 暗い 線と、その 光が 当たる がわの 細い 明るい 線
        vein = np.exp(-(u ** 2) / (2 * 0.07 ** 2)) * (t > 0.06) * (t < 0.94)
        vein_hi = np.exp(-((u - 0.16 * lit) ** 2) / (2 * 0.05 ** 2)) * (t > 0.1) * (t < 0.9)
        rgb = rgb * (1 - vein[..., None] * 0.55) + C['edge'] * vein[..., None] * 0.55
        rgb = rgb * (1 - vein_hi[..., None] * 0.5) + C['hi'] * vein_hi[..., None] * 0.5
        col[sl] = col[sl] * (1 - m[..., None]) + rgb * m[..., None]
        acc[sl] = np.maximum(acc[sl], m)
    # ---- 金の 実（丸い 玉）：3つおきの 節に 2こ
    for k in range(5, n - 4, 12):
        p = stem[k]; d = stem[k + 1] - stem[k - 1]; d = d / np.linalg.norm(d); nrm_ = np.array([-d[1], d[0]])
        for sgn, off in ((1, 0.0), (-1, 2.0)):
            c0 = p + nrm_ * sgn * 3.6 + d * off
            rr = 2.4
            bx0, by0 = max(0, int((c0[0] - rr - 1) * S)), max(0, int((c0[1] - rr - 1) * S))
            bx1, by1 = min(W4, int((c0[0] + rr + 2) * S)), min(H4, int((c0[1] + rr + 2) * S))
            sl = (slice(by0, by1), slice(bx0, bx1))
            dist = np.sqrt((xx4[sl] - c0[0]) ** 2 + (yy4[sl] - c0[1]) ** 2)
            m = np.clip((rr - dist) * S * 0.9 + 0.5, 0, 1)
            hx, hy = c0[0] + light[0] * rr * 0.45, c0[1] + light[1] * rr * 0.45
            sp = np.exp(-((xx4[sl] - hx) ** 2 + (yy4[sl] - hy) ** 2) / (2 * (rr * 0.42) ** 2))
            dk = np.clip((dist / rr) ** 2, 0, 1) * 0.55
            rgb = C['base'] * (1 - dk[..., None]) + C['dark'] * dk[..., None]
            rgb = rgb * (1 - sp[..., None] * 0.95) + C['hi'] * sp[..., None] * 0.95
            col[sl] = col[sl] * (1 - m[..., None]) + rgb * m[..., None]
            acc[sl] = np.maximum(acc[sl], m)
    # ---- 1倍に 縮めて 重ねる：うすい 落ち影（右下へ 2px・ぼかし）→ 金
    a1x = cv2.resize(acc, (W, Hh), interpolation=cv2.INTER_AREA)
    rgb1 = cv2.resize(np.where(acc[..., None] > 0, col, 0), (W, Hh), interpolation=cv2.INTER_AREA)
    rgb1 = np.where(a1x[..., None] > 1e-4, rgb1 / np.maximum(a1x[..., None], 1e-4), 0)
    sh = blur(np.roll(np.roll(a1x, 3, 0), 2, 1), 2.2) * 0.42
    img = over(img, hexc('#5A4420'), sh)
    return over(img, rgb1, a1x)


def cleanup():
    import shutil
    import style2d as S2
    shutil.rmtree(S2.TMP, ignore_errors=True)


if __name__ == '__main__':
    out = sys.argv[1]
    cam = camera()
    sc = scene(cam, horse=os.environ.get('MARBLE_NO_HORSE') != '1')
    R = render(sc)
    cleanup()
    img = compose(background(), R, sc, cam)
    save_webp(np.clip(img, 0, 1), out)
    print(out)
