"""紫電（しでん）の ど的中の 絵（WebP）：まさちゃん「新しい的中演出を作成したい！ 85枚の画像が入ったファイルとGIFを送るね！ そのGIFと画像を元に的中演出作成して！
   求めているのは、同じ感じの演出・圧倒的な迫力・見ていて気持ちのいい当たり演出になること！ 鬼の文字を的中に変えて、最後の鬼ががり6000の所を、
   鬼ががりの所をど！！！ビックリマークは上から下に小さく！6000の所を的中に変えて作成してみて！」
   - 送ってくれた 動画（パチンコの 演出）は 流れ・色・迫力を 見るだけ。登場人物・絵・字・ロゴは 使わない・なぞらない（権利の ある 絵なので）。
     人物の 代わりは テンゲルの 馬（後ろ足で 立ち上がる 黒い 馬の 影：r3d の 3Dの 馬・flat/marble_horse.py と 同じ 形の 馬）。ほかは ここで 一から 作る
   - 出す 絵（大きさと 置き場所は shiden_layers.json・id は shiden_blobs.json（中身の md5）。絵は リポジトリに 入れない）：
       sd_horse    … 黒い 馬の 影（紫の ふちの 光・赤い 目）。すき通し
       sd_bg       … 金の 水晶の かけらが ちらばる 紫の 夜（下の 絵・2倍）
       sd_fire_p1〜3 … 紫の 炎（3まい：ページが 入れかわりで 燃やす）。すき通し
       sd_fire_o1〜3 … 赤い 炎（同じ 形で 色だけ 赤・金）
       sd_glyph    … 炎の 中を ただよう「的中」の 字（送ってくれた 動画の「鬼」の 字の 所：まさちゃん「鬼の文字を的中に変えて」）
       sd_rtex     … 虹の ノイズの 布（さいごの 背景・流す）
       sd_t_do     …「ど」（炎の 金の 立体の 字・Dela Gothic One）
       sd_t_ex     …「！」（同じ 作り。CSS で 3つ・上から 下へ 小さく）
       sd_t_hit    …「的中」（虹色の つやの 立体の 字・黒い ふちと 白い 内ふち）
       ② の 絵（第4.68版：送ってくれた GIF の 1コマずつ）は flat/shiden_cuts.py（sd_c0・sd_rbs・sd_c1・sd_eye・sd_c5・sd_c6・sd_w_…・sd_c16〜19・sd_pillar）
   python3 flat/shiden_art.py <出力フォルダ> [名前 …]   → <名前>.webp・shiden_layers.json・shiden_blobs.json"""
import sys, os, json, math, hashlib
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(K, 'r3d'))
sys.path.insert(0, HERE)
sys.path.insert(0, K)
import kami_art as KA
from kami_art import mask, run, ramp, fbm, noise, radial, rays, smoothstep, grow, dist_in, normals_of, over, save, save_rgb, crop, gold3d, front, extrude

W_, H_ = 390, 844
S2X = 2
LAY = {}


def hexc(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255


def edge_fade(img, m):
    """絵の ふち m px で すき通しを 0 に（光が 絵の 四角で 切れて 見えない ように）"""
    H, W = img.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.minimum(np.minimum(xx, W - 1 - xx), np.minimum(yy, H - 1 - yy))
    w = np.clip(d / m, 0, 1)
    w = w * w * (3 - 2 * w)
    return img * w[..., None]


def put_lay(name, w, h, **kw):
    LAY[name] = dict(w=round(w, 1), h=round(h, 1), **kw)


# ---------------------------------------------------------------- 黒い 馬の 影
def horse(out):
    """後ろ足で 立ち上がる 黒い 馬（r3d）：体は 黒に 近い 紫・ふちに 紫と 桃色の 光・まわりに うすい 紫の 光・赤く 光る 目。たてがみと しっぽは 上へ なびく（炎の ように）"""
    import style2d as S2
    import horse3d as Hm
    S2.TMP = os.path.join(out, '_tmp')
    os.makedirs(S2.TMP, exist_ok=True)
    W, H = 600, 1120
    rgb, a, R = S2.horse_illust(Hm.REAR, (50, 60, 560, 1090), W, H, facing='right', azim=25, elev=6, body=('#160A1E', '#0B0411'), mane=('#1C0C28', '#0E0514'),
                                line='#2A1238', mode='flow', ss=2, name='sd_horse', wind_ang=-math.pi / 2, mane_len=1.5, tail_len=1.25, mane_scale=1.45)
    a = np.clip(a, 0, 1).astype(np.float32)
    H2, W2 = a.shape
    # 体の 色：下は 黒・上へ 少し 紫（光は 上から）
    ys = (np.arange(H2, dtype=np.float32)[:, None] / H2) * np.ones((1, W2), np.float32)
    body = ramp(1 - ys, ((0, (10, 4, 16)), (.6, (18, 8, 28)), (1, (34, 14, 50))))
    # ふちの 光：形の 内がわ 7px で 紫 → 桃色。上と 左の ふち（光の 方）は 強く
    d_in = dist_in(a)
    ab = cv2.GaussianBlur(a, (0, 0), 2.0)
    gx = cv2.Sobel(ab, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(ab, cv2.CV_32F, 0, 1, ksize=3)
    gl = np.sqrt(gx * gx + gy * gy) + 1e-6
    facing = np.clip((-gx * .35 - gy * .94) / gl, 0, 1)                      # ふちが 上（と 少し 左）を 向いている 所
    rim = np.exp(-d_in / 6.0) * (a > .5) * (.35 + .65 * facing)
    rim2 = np.exp(-d_in / 2.2) * (a > .5)
    col = body * (1 - rim[..., None] * .9) + hexc('#B23CFF') * (rim * .9)[..., None]
    col = col + hexc('#FF66E6') * (rim2 * .9)[..., None]
    col = np.clip(col, 0, 1)
    # 赤い 目（目の 素材 5）：赤い しんと まわりの 光
    m = R['m'] if 'm' in R else None
    if m is not None:
        eye = (np.abs(m - 5) < .5).astype(np.float32)
        if eye.shape != a.shape:
            eye = cv2.resize(eye, (W2, H2), interpolation=cv2.INTER_AREA)
        eye_g = cv2.GaussianBlur(eye, (0, 0), 1.2)
        glow = cv2.GaussianBlur(eye, (0, 0), 7.0) * 2.4
        col = col * (1 - np.clip(eye_g, 0, 1)[..., None]) + hexc('#FF2A3A') * np.clip(eye_g, 0, 1)[..., None]
        col = col + hexc('#FF2040') * np.clip(glow, 0, 1)[..., None] * .9 * (a > .3)[..., None]
        col = col + hexc('#FFE0E0') * np.clip(cv2.GaussianBlur(eye, (0, 0), .6), 0, 1)[..., None] * .8
    col = np.clip(col, 0, 1)
    # まわりの うすい 紫の 光（形の 外 18px）
    halo = np.clip(cv2.GaussianBlur(grow(a, 14), (0, 0), 9.0) - a, 0, 1) * .55
    img = np.zeros((H2, W2, 4), np.float32)
    img[..., :3] = hexc('#8A2BE2') * halo[..., None]
    img[..., 3] = halo
    fg = np.dstack([col * a[..., None], a])
    img = over(img, fg)
    img, (x0, y0) = crop(img, 6)
    save(img, os.path.join(out, 'sd_horse.webp'), q=90)
    h, w = img.shape[:2]
    put_lay('sd_horse', w / S2X, h / S2X, eye=[round(float(R['eye'][0] - x0) / S2X, 1), round(float(R['eye'][1] - y0) / S2X, 1)])
    return 'sd_horse'


# ---------------------------------------------------------------- 金の 水晶の 夜
def bg(out, seed=5):
    """紫の 夜に 金の 水晶の かけら（細長い 四角）が ちらばる（下の 絵・2倍の 780×1688）"""
    W, H = W_ * S2X, H_ * S2X
    rng = np.random.default_rng(seed)
    ys = (np.arange(H, dtype=np.float32)[:, None] / H) * np.ones((1, W), np.float32)
    xs = (np.arange(W, dtype=np.float32)[None, :] / W) * np.ones((H, 1), np.float32)
    img = ramp(ys, ((0, (14, 4, 30)), (.5, (34, 8, 60)), (1, (10, 2, 20))))
    img = img * (0.75 + 0.5 * radial(H, W, W / 2, H * .48, W * .9, 1.6))[..., None]
    cloud = fbm(H, W, 4, seed + 1, 5)
    img = img + hexc('#6A1FA8') * (smoothstep(.45, .85, cloud) * .35)[..., None]
    # かけら：細長い 四角（ななめ）に 金の グラデーション。大きい のは こく・小さい のは うすく ぼかす
    acc = np.zeros((H, W, 3), np.float32)
    aa = np.zeros((H, W), np.float32)
    for i in range(96):
        cx, cy = rng.uniform(-40, W + 40), rng.uniform(-40, H + 40)
        big = rng.random() < .2
        L = rng.uniform(140, 520) if big else rng.uniform(30, 160)
        wd = L * rng.uniform(.05, .16)
        ang = rng.uniform(0, math.pi)
        pts = []
        for (u, v) in ((-.5, -.5), (.5, -.35), (.5, .5), (-.5, .35)):
            px, py = u * L, v * wd
            pts.append((cx + px * math.cos(ang) - py * math.sin(ang), cy + px * math.sin(ang) + py * math.cos(ang)))
        m = np.zeros((H, W), np.float32)
        cv2.fillPoly(m, [np.round(np.array(pts) * 16).astype(np.int32)], 1.0, cv2.LINE_AA, shift=4)
        if not big:
            m = cv2.GaussianBlur(m, (0, 0), rng.uniform(1.2, 4.0))     # 小さい かけらは 奥（ぼかす）
        t = ((xs * W - cx) * math.cos(ang) + (ys * H - cy) * math.sin(ang)) / L + .5
        c = ramp(t, ((0, (255, 236, 150)), (.3, (255, 196, 60)), (.6, (170, 100, 10)), (1, (90, 40, 0))))
        edge = np.clip(1 - dist_in(m) / max(2.0, wd * .18), 0, 1) * (m > .5)
        c = c * (1 - edge[..., None] * .5) + hexc('#FFF4C8') * (edge * .5)[..., None]
        k = rng.uniform(.55, .95) if big else rng.uniform(.25, .6)
        acc = acc * (1 - (m * k)[..., None]) + c * (m * k)[..., None]
        aa = np.maximum(aa, m * k)
    img = img * (1 - aa[..., None]) + acc * aa[..., None]
    img = img + hexc('#FFD37A') * (cv2.GaussianBlur(aa, (0, 0), 18) * .22)[..., None]     # 金の にじみ
    # 小さな 光の 粒
    for _ in range(260):
        x, y = int(rng.uniform(0, W)), int(rng.uniform(0, H))
        r = rng.uniform(1.0, 3.2)
        cv2.circle(img, (x, y), int(r), (1.0, .95, .75), -1, cv2.LINE_AA)
    img = img * (0.6 + 0.4 * radial(H, W, W / 2, H * .5, W * 1.1, 1.2))[..., None]
    save_rgb(np.clip(img, 0, 1), os.path.join(out, 'sd_bg.webp'), q=84)
    put_lay('sd_bg', W_, H_)
    return 'sd_bg'


# ---------------------------------------------------------------- 炎（紫・赤）
PURPLE = ((0, (0, 0, 0)), (.28, (40, 6, 80)), (.55, (150, 40, 255)), (.78, (255, 110, 240)), (1, (255, 240, 255)))
ORANGE = ((0, (0, 0, 0)), (.28, (90, 10, 0)), (.52, (255, 70, 0)), (.76, (255, 190, 50)), (1, (255, 252, 220)))


def flame(k, seed):
    """炎の 形（0〜1）：下から 上へ のびる ゆがんだ ノイズ。k＝コマ（少しずつ 位相を ずらす）"""
    W, H = W_, H_
    ys = (np.arange(H, dtype=np.float32)[:, None] / H) * np.ones((1, W), np.float32)
    xs = (np.arange(W, dtype=np.float32)[None, :] / W) * np.ones((H, 1), np.float32)
    q1 = fbm(H, W, 4, seed + k * 3, 4)
    q2 = fbm(H, W, 4, seed + 9 + k * 3, 4)
    mx = (xs + .22 * (q1 - .5)) * W
    my = (ys * 1.3 + .25 * (q2 - .5) - .31 * k) * H
    base = fbm(H, W, 6, seed + 3, 6, .55)
    f = cv2.remap(base, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    # 下ほど 強く・まん中ほど 強く・上へ 消える
    env = np.clip(1.15 - 1.1 * np.abs(xs - .5) ** 1.4 * 2.0, 0, 1) * np.clip((ys - .12) / .5, 0, 1) ** .9
    t = smoothstep(.3, .78, f * (.55 + .7 * env)) * np.clip((ys - .05) / .25, 0, 1)
    return t


def fires(out):
    names = []
    for k in range(3):
        t = flame(k, 61)
        for tag, stops in (('p', PURPLE), ('o', ORANGE)):
            col = ramp(t, stops)
            a = np.clip(t * 1.25, 0, 1)
            img = np.dstack([col * a[..., None], a])
            nm = f'sd_fire_{tag}{k + 1}'
            save(img, os.path.join(out, nm + '.webp'), q=80)
            put_lay(nm, W_, H_)
            names.append(nm)
    return names


# ---------------------------------------------------------------- ただよう「的中」の 字
def glyph(out):
    """炎の 中を ただよう「的中」（小さく・金から 赤へ・ふちが 光る）"""
    items, box, _ = run([('的', 1.0), ('中', 1.0)], track=-60)
    em = 64.0 * S2X
    k = em / 1000
    a = mask(items, box, k, 10)
    d = dist_in(a)
    t = np.clip(d / (em * .07), 0, 1)
    col = ramp(1 - t, ((0, (255, 250, 200)), (.4, (255, 200, 60)), (.8, (255, 90, 20)), (1, (200, 40, 20))))
    glow = cv2.GaussianBlur(a, (0, 0), em * .06) * .9
    img = np.zeros((a.shape[0], a.shape[1], 4), np.float32)
    img[..., :3] = hexc('#FF7A1A') * glow[..., None]
    img[..., 3] = glow
    img = over(img, np.dstack([col * a[..., None], a]))
    img = edge_fade(img, em * .12)
    img, _ = crop(img, 4)
    save(img, os.path.join(out, 'sd_glyph.webp'), q=84)
    h, w = img.shape[:2]
    put_lay('sd_glyph', w / S2X, h / S2X)
    return 'sd_glyph'


# ---------------------------------------------------------------- 虹の ノイズの 布
def rtex(out, seed=81):
    W, H = W_ * S2X, H_ * S2X
    rng = np.random.default_rng(seed)
    ys = (np.arange(H, dtype=np.float32)[:, None] / H) * np.ones((1, W), np.float32)
    xs = (np.arange(W, dtype=np.float32)[None, :] / W) * np.ones((H, 1), np.float32)
    bands = fbm(H, W, 3, seed, 3) * .55 + ys * .9
    hue = (bands * 1.5 + .25 * np.sin(xs * 7.0 + ys * 3.0)) % 1.0
    col = ramp(hue, ((0, (255, 40, 90)), (.17, (255, 150, 30)), (.33, (255, 240, 60)), (.5, (60, 240, 130)), (.67, (40, 170, 255)), (.84, (200, 70, 255)), (1, (255, 40, 90))))
    # ななめの 細い 光の 筋（布の つや）と ごく うすい 四角の ちらつき
    diag = (np.sin((xs * W + ys * H * .6) * .045 + fbm(H, W, 4, seed + 5, 3) * 5) * .5 + .5) ** 5
    blocks = noise(H, W, 26, seed + 7, cv2.INTER_NEAREST)
    light = .6 + .4 * smoothstep(.3, .8, fbm(H, W, 6, seed + 11, 4)) + .1 * diag + .04 * (blocks > .9)
    img = col * light[..., None]
    img = img + np.array([1, 1, 1], np.float32) * (diag * .07 + np.clip(blocks - .97, 0, 1) * 3)[..., None]
    # 横の 細い 線（走査線）
    scan = (np.sin(ys * H * 1.3) * .5 + .5) ** 8 * .18
    img = img * (1 - scan[..., None])
    save_rgb(np.clip(img, 0, 1), os.path.join(out, 'sd_rtex.webp'), q=78)
    put_lay('sd_rtex', W_, H_)
    return 'sd_rtex'


# ---------------------------------------------------------------- ロゴの 字
def fire_glow(a, em):
    """字の まわりの 炎の 光（赤 → 金 → 白）：すき通しの RGBA"""
    H, W = a.shape
    base = np.maximum(cv2.GaussianBlur(a, (0, 0), em * .1) * 1.4, cv2.GaussianBlur(a, (0, 0), em * .22) * 1.1)
    tongues = flame_small(H, W, em)
    t = np.clip(base * 1.9 * (.5 + 1.0 * tongues), 0, 1)
    col = ramp(t, ((0, (120, 0, 0)), (.35, (255, 60, 0)), (.7, (255, 190, 40)), (1, (255, 250, 220))))
    a2 = np.clip(t * 1.8, 0, 1) * (1 - np.clip(a * 1.2, 0, 1))
    return np.dstack([col * a2[..., None], a2])


def flame_small(H, W, em, seed=91):
    ys = (np.arange(H, dtype=np.float32)[:, None] / H) * np.ones((1, W), np.float32)
    xs = (np.arange(W, dtype=np.float32)[None, :] / W) * np.ones((H, 1), np.float32)
    q1 = fbm(H, W, 5, seed, 4)
    q2 = fbm(H, W, 5, seed + 9, 4)
    base = fbm(H, W, 8, seed + 3, 5, .55)
    f = cv2.remap(base, ((xs + .2 * (q1 - .5)) * W).astype(np.float32), ((ys * 1.2 + .2 * (q2 - .5) - .1) * H).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return smoothstep(.35, .8, f)


def fire_letter(out, name, text, em_px, track=-40):
    """炎の 金の 立体の 字（ど・！）：金の 立体の 字（kami_art）＋ まわりに 炎の 光 ＋ こい ふち"""
    items, box, _ = run([(c, 1.0) for c in text], track=track)
    em = em_px * S2X
    k = em / 1000
    pad = int(em * .8)
    a = mask(items, box, k, pad)
    letters = gold3d(a, em, ext=(.075, .11), rim=(.052, .03, .02), style='gold', glints=3, edge=.02)
    glow = fire_glow(a, em)
    img = over(glow, letters)
    img = edge_fade(img, em * .3)
    img, _ = crop(img, 4)
    save(img, os.path.join(out, name + '.webp'), q=90)
    h, w = img.shape[:2]
    put_lay(name, w / S2X, h / S2X)
    return name


RAINBOW = ((0.0, (255, 40, 60)), (.16, (255, 150, 30)), (.33, (255, 236, 60)), (.5, (60, 225, 110)), (.66, (40, 170, 255)), (.83, (170, 70, 255)), (1.0, (255, 60, 170)))


def rainbow_front(a, em):
    """「的中」の 前の 面：虹色の 面（上から 下へ 色が かわる・横の つやの 帯）＋ 白い 内ふち。premultiplied RGBA"""
    H, W = a.shape
    rimw = .055 * em
    body = grow(a, rimw)
    da, db = dist_in(a), dist_in(body)
    ys = (np.arange(H, dtype=np.float32)[:, None] / H) * np.ones((1, W), np.float32)
    xs = (np.arange(W, dtype=np.float32)[None, :] / W) * np.ones((H, 1), np.float32)
    yy, xx = np.nonzero(a > .5)
    y0, y1 = yy.min(), yy.max()
    u = (ys * H - y0) / max(1.0, y1 - y0)
    u = u + .03 * np.sin(xs * W / em * 4.0)
    face = ramp(np.clip(u, 0, 1), RAINBOW)
    gloss = np.exp(-((u - .22) / .07) ** 2) * .55 + np.exp(-((u - .62) / .035) ** 2) * .3
    face = np.clip(face + gloss[..., None], 0, 1)
    # 字の 面の 立体：ふち 近くは 面取り（暗く）
    h = .06 * em * KA.bevel(da, .06 * em)
    n = normals_of(h, 1.0)
    ndl = np.clip(n @ KA.L_DIR, 0, 1)
    hv = KA.L_DIR + np.array([0, 0, 1.0]); hv /= np.linalg.norm(hv)
    spec = np.clip(n @ hv, 0, 1) ** 60
    face = face * (.55 + .5 * ndl)[..., None] + np.array([1, 1, 1], np.float32) * spec[..., None] * .9
    # 白い 内ふち（字と 黒ふちの あいだ）
    white = np.clip(1 - np.abs(db - rimw * .5) / (rimw * .5), 0, 1) * (body > .5) * (a < .5)
    col = face * np.clip(a, 0, 1)[..., None] + np.array([1, 1, 1], np.float32) * (white * (1 - a))[..., None]
    col = np.clip(col, 0, 1)
    alpha = np.clip(body, 0, 1)
    return np.dstack([col * alpha[..., None] + (1 - alpha[..., None]) * 0, alpha]), body


def hit_logo(out, em_px=150):
    """「的中」：虹色の つやの 立体の 字。外は 黒い ふち・うしろへ 金の 厚み"""
    items, box, _ = run([('的', 1.0), ('中', 1.0)], track=-70)
    em = em_px * S2X
    k = em / 1000
    pad = int(em * .5)
    a = mask(items, box, k, pad)
    fr, body = rainbow_front(a, em)
    sd = extrude(body, (.07 * em, .1 * em), em)
    allm = np.maximum(body, sd[..., 3])
    ring = np.clip(grow(allm, .03 * em) - allm, 0, 1)
    img = np.zeros_like(fr)
    img[..., :3] = hexc('#120A06') * ring[..., None]
    img[..., 3] = ring
    img = over(img, sd)
    img = over(img, fr)
    # まわりの 光（白 → 金）
    glow = cv2.GaussianBlur(allm, (0, 0), em * .08) * .8 * (1 - np.clip(allm * 1.5, 0, 1))
    g = np.dstack([hexc('#FFE9A0') * glow[..., None], glow])
    img = over(g, img)
    img = edge_fade(img, em * .2)
    img, _ = crop(img, 4)
    save(img, os.path.join(out, 'sd_t_hit.webp'), q=90)
    h, w = img.shape[:2]
    put_lay('sd_t_hit', w / S2X, h / S2X)
    return 'sd_t_hit'


# ---------------------------------------------------------------- 作る
def build(out, names=None):
    os.makedirs(out, exist_ok=True)
    lay_path = os.path.join(K, 'shiden_layers.json')
    if os.path.exists(lay_path):
        LAY.update(json.load(open(lay_path, encoding='utf-8')))
    todo = {
        'sd_horse': lambda: horse(out), 'sd_bg': lambda: bg(out), 'sd_fire': lambda: fires(out), 'sd_glyph': lambda: glyph(out),
        'sd_rtex': lambda: rtex(out), 'sd_t_do': lambda: fire_letter(out, 'sd_t_do', 'ど', 150), 'sd_t_ex': lambda: fire_letter(out, 'sd_t_ex', '！', 150),
        'sd_t_hit': lambda: hit_logo(out)}
    made = []
    for key, fn in todo.items():
        if names and key not in names:
            continue
        r = fn()
        made += r if isinstance(r, list) else [r]
        print('made', r, flush=True)
    import shiden_cuts                                         # ② の 絵（① の 馬・炎の 絵を 使うので あとで）
    shiden_cuts.SA = sys.modules[__name__]                     # 同じ LAY に 書く（python3 flat/shiden_art.py で 動かした ときも）
    made += shiden_cuts.build(out, names)
    # いま 使う 絵だけ のこす（前の 版の sd_streaks・sd_stream などは 消す）
    keep = {'sd_horse', 'sd_bg', 'sd_glyph', 'sd_rtex', 'sd_t_do', 'sd_t_ex', 'sd_t_hit', 'sd_c0', 'sd_rbs', 'sd_c1', 'sd_c2', 'sd_eye', 'sd_c5', 'sd_c6',
            'sd_w_bg', 'sd_w_near', 'sd_w_fire1', 'sd_w_fire2', 'sd_w_prism', 'sd_c16', 'sd_c17', 'sd_c18', 'sd_c19', 'sd_pillar'} | {f'sd_fire_{c}{k}' for c in 'po' for k in (1, 2, 3)}
    for k in list(LAY):
        if k not in keep:
            del LAY[k]
    json.dump(LAY, open(lay_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # id（中身の md5）→ shiden_blobs.json（見本の /_blob/<id> と 同じ 形で 参照する）
    bl_path = os.path.join(K, 'shiden_blobs.json')
    bl = {}
    for nm in LAY:
        fn = os.path.join(out, nm + '.webp')
        if os.path.exists(fn):
            bl[nm] = hashlib.md5(open(fn, 'rb').read()).hexdigest()
    json.dump(bl, open(bl_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    tmp = os.path.join(out, '_tmp')
    if os.path.isdir(tmp):
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
    size = sum(os.path.getsize(os.path.join(out, n + '.webp')) for n in LAY if os.path.exists(os.path.join(out, n + '.webp')))
    return f'{len(LAY)}まい {size / 1e6:.2f}MB'


if __name__ == '__main__':
    print(build(sys.argv[1], sys.argv[2:] or None))
