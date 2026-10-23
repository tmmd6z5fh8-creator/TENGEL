"""超神様的中の「昇格」：超プレミアムど的中の ③「き！」で 画面が バグる 2秒（1コマずつ 描く 絵。1170×2532・30コマ/秒・60コマ）
   まさちゃん「このカットインは、超プレミアムど的中の演出が、画像のきの当たりで、いきなり画面が、2秒間電気がチカチカするように画面が
   歪みながらついたり消えたりして、このカットインが入り超神様的中の演出に入るようにして！」
   → 超神様的中の 4回に1回（※仮）は 超プレミアムど的中の ふりを して はじまり、③「き！」（押してから 6.0秒）で 画面が 止まって バグる：
     ゆがむ（よこの 波）・よこに ずれる（帯）・色が ずれる・ノイズ・細い 電気が バチバチ・ついたり 消えたり → さいごは 画面が 横一本の 線に
     ちぢんで 点に なって 消える（プツッ）→ 宇宙の カットイン（kami_cutin.py）→ 超神様的中の 動画
   もとの 絵（き！の 画面）は 見本の ページ（Fx_SuperPremium）の 6.0秒の 1まい（capture_page.py で 写す）。
   点めつ：画面 ぜんぶが 消えるのは 0.53秒ごとに 3回＋さいごの 1回（どの 1秒にも 2回 まで）。そのほかの チカチカは 明るさを そろえた 色の ずれと 帯で 出す
   消えた あとは まっ暗 1秒（BLACK_TAIL）→ 超プレミアムの ポニーに 隕石が 向かって くる（kami_pony.py）
   python3 flat/kami_glitch.py <き！の 1まい（png）> <出力フォルダ> [コマ番号（1〜）…] → g001.png …（何回 作っても 同じ）"""
import os, sys, math, random
import numpy as np
import cv2

W, H = 1170, 2532
BLACK_TAIL = 30                        # 消えた あとの まっ暗（まさちゃん「き！の後のバグってブラックアウト、のブラックアウトの時間を1秒にして！」）
FPS, N = 30, 59 + BLACK_TAIL           # 2秒（59コマめで 消える）＋ まっ暗 1秒
BLACK = (3, 4, 19, 20, 35, 36)         # 画面が 消える コマ（0 から：0.1・0.63・1.17秒 ごろ）
COLLAPSE = (53, 57, 59)                # 横一本の 線に ちぢむ はじめ・点に なる・消える
ZAP = (0, 1, 2)                        # はじめの ガツン（いちばん 強い ずれ）


def sstep(e0, e1, x):
    u = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return u * u * (3 - 2 * u)


def luma(x):
    return x[..., 0] * .2126 + x[..., 1] * .7152 + x[..., 2] * .0722


def s2l(c):
    return np.where(c <= .04045, c / 12.92, ((np.clip(c, 0, 1) + .055) / 1.055) ** 2.4).astype(np.float32)


def l2s(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= .0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - .055).astype(np.float32)


LW = np.float32([.2126, .7152, .0722])


def hue_shift_same_luma(img, deg):
    """光の 量（明るさ）を かえずに 色あいだけ 回す（チカチカ しても 点めつに しない）"""
    a = math.radians(deg)
    k = np.float32([[.299, .587, .114], [.596, -.274, -.322], [.211, -.523, .312]])     # 色の 平面（YIQ）で 回す
    ki = np.linalg.inv(k).astype(np.float32)
    yiq = img @ k.T
    i, q = yiq[..., 1].copy(), yiq[..., 2].copy()
    yiq[..., 1] = i * math.cos(a) - q * math.sin(a)
    yiq[..., 2] = i * math.sin(a) + q * math.cos(a)
    out = np.clip(yiq @ ki.T, 0, 1)
    lt = s2l(img) @ LW
    ol = s2l(out)
    lo = ol @ LW
    ol = ol * (lt / np.maximum(lo, 1e-5))[..., None]
    over = np.clip(ol.max(-1) - 1, 0, None)[..., None]                                  # 入りきらない 分は 白へ 寄せる
    ol = np.clip(ol, 0, 1) + over * .5
    return l2s(ol)


def wave_warp(img, amp, lam, ph, xx, yy):
    """よこの 波で ゆがむ（たてに 少し ゆれる）"""
    mx = (xx + amp * np.sin(2 * np.pi * yy / lam + ph) + amp * .35 * np.sin(2 * np.pi * yy / (lam * .37) + ph * 1.7)).astype(np.float32)
    my = (yy + amp * .12 * np.sin(2 * np.pi * xx / 300.0 + ph)).astype(np.float32)
    return cv2.remap(img, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def tear(img, rng, n, maxshift, maxh):
    """よこに ずれる 帯（n 本）"""
    out = img.copy()
    bands = []
    for _ in range(n):
        y0 = int(rng.uniform(0, H - 10))
        h = int(rng.uniform(8, maxh))
        dx = int(rng.choice((-1, 1)) * rng.uniform(maxshift * .2, maxshift))
        y1 = min(H, y0 + h)
        out[y0:y1] = np.roll(img[y0:y1], dx, axis=1)
        bands.append((y0, y1))
    return out, bands


def rgb_split(img, px, py=0.0):
    if abs(px) < .5 and abs(py) < .5:
        return img
    out = img.copy()
    M1 = np.float32([[1, 0, px], [0, 1, py]])
    M2 = np.float32([[1, 0, -px], [0, 1, -py]])
    out[..., 0] = cv2.warpAffine(img[..., 0], M1, (W, H), borderMode=cv2.BORDER_REFLECT)
    out[..., 2] = cv2.warpAffine(img[..., 2], M2, (W, H), borderMode=cv2.BORDER_REFLECT)
    return out


def jag(rng, a, b, rough, depth=6):
    pts = [a, b]
    for d in range(depth):
        new = [pts[0]]
        for p, q in zip(pts, pts[1:]):
            L = math.hypot(q[0] - p[0], q[1] - p[1])
            mx_, my_ = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
            nx, ny = -(q[1] - p[1]) / (L + 1e-6), (q[0] - p[0]) / (L + 1e-6)
            off = rng.gauss(0, rough * L)
            new += [(mx_ + nx * off, my_ + ny * off), q]
        pts = new
    return pts


def arcs(img, rng, k):
    """細い 電気（白い しん・水色と ピンクの 光）：k 本"""
    m = np.zeros((H, W), np.float32)
    for _ in range(k):
        x0, y0 = rng.uniform(80, W - 80), rng.uniform(500, H - 500)
        ang = rng.uniform(0, 2 * math.pi)
        L = rng.uniform(220, 700)
        x1, y1 = x0 + L * math.cos(ang), y0 + L * math.sin(ang)
        pts = jag(rng, (x0, y0), (x1, y1), .22)
        q = np.int32(np.round(np.array(pts) * 8))
        cv2.polylines(m, [q], False, 1.0, 4, cv2.LINE_AA, shift=3)
        for _ in range(rng.randint(1, 3)):                       # えだ
            j = rng.randint(len(pts) // 4, len(pts) - 2)
            p = pts[j]
            a2 = ang + rng.choice((-1, 1)) * rng.uniform(.5, 1.1)
            l2 = L * rng.uniform(.2, .4)
            br = jag(rng, p, (p[0] + l2 * math.cos(a2), p[1] + l2 * math.sin(a2)), .25, 5)
            cv2.polylines(m, [np.int32(np.round(np.array(br) * 8))], False, .7, 2, cv2.LINE_AA, shift=3)
    core = np.clip(m, 0, 1)
    g1 = cv2.GaussianBlur(m, (0, 0), 5)
    g2 = cv2.GaussianBlur(m, (0, 0), 16)
    out = img * (1 - .6 * np.clip(g1 * 3.5, 0, 1))[..., None] * (1 - .25 * np.clip(g2 * 4, 0, 1))[..., None]   # まわりを 暗く（明るい 絵の 上でも 線が 見える）
    out += core[..., None] * np.float32([1, 1, 1]) * 1.0
    out += g1[..., None] * np.float32([.45, .95, 1.0]) * 2.2
    out += g2[..., None] * np.float32([.85, .25, 1.0]) * 1.3
    return np.clip(out, 0, 1)


def snow(img, rng, bands):
    """ザザッ：細い 帯に ノイズ（明るさは もとと 同じ くらい）"""
    out = img.copy()
    for y0, y1 in bands:
        h = y1 - y0
        if h <= 0:
            continue
        nz = rng_np(rng).random((h, W // 3)).astype(np.float32)
        nz = cv2.resize(nz, (W, h), interpolation=cv2.INTER_NEAREST)
        base = luma(out[y0:y1]).mean()
        v = np.clip(base + (nz - .5) * .5, 0, 1)
        out[y0:y1] = out[y0:y1] * .35 + v[..., None] * .65
    return out


def rng_np(rng):
    return np.random.default_rng(rng.randrange(1 << 30))


def scanlines(img, k=.06):
    s = np.ones((H, 1, 1), np.float32)
    s[::3] = 1 - k
    return img * s


def blackout(rng, img):
    """消えた 画面：ほぼ 黒・うすい 走査線と ノイズ（明るさ 2% 以下）"""
    out = np.zeros_like(img)
    nz = rng_np(rng).random((H // 4, W // 4)).astype(np.float32)
    nz = cv2.resize(nz, (W, H), interpolation=cv2.INTER_NEAREST)
    out += (nz[..., None] * .03)
    y = int(rng.uniform(H * .3, H * .7))
    out[y:y + 3] += .12
    return out


def collapse(img, u):
    """横一本の 線に ちぢむ（u：0→1）→ 点に（u：1→2）"""
    out = np.zeros_like(img)
    cy = H * .5
    if u <= 1:
        sy = max(.004, (1 - u) ** 2.2)
        h = max(3, int(H * sy))
        sm = cv2.resize(img, (W, h), interpolation=cv2.INTER_AREA)
        y0 = int(cy - h / 2)
        k = 1 + .5 * u * u                                 # ちぢむ ほど 少し 明るく（細く なってから）
        out[y0:y0 + h] = np.clip(sm * k, 0, 1)
        if h <= 12:
            out[y0:y0 + h] = np.float32([1, 1, 1])
        thin = h <= 60
    else:
        w_ = max(4, int(W * (1 - (u - 1)) ** 2))
        x0 = int(W / 2 - w_ / 2)
        out[int(cy) - 2:int(cy) + 2, x0:x0 + w_] = 1.0
        thin = True
    if thin:                                               # 細い 線の 光（広い 画面は 光らせない）
        out = out + cv2.GaussianBlur(out, (0, 0), 10) * .8
    return np.clip(out, 0, 1)


STATES = (0, 8, 16, 27, 33, 43, 49)    # ずれ方が かわる コマ（1秒に 2〜3回：ずれる 帯・ゆがむ 帯は その間 止まって いる）
SPLIT = 5.0                             # 色の ずれ（いつも 同じ：かわると 線の 所が ちらつく）


def state_of(fi):
    return max(i for i, c in enumerate(STATES) if c <= fi)


def band_warp(img, rng, n, xx, yy, amp_lo, amp_hi):
    """ゆがむ 帯（画面の 一部だけ・よこの 波）"""
    out = img
    for _ in range(n):
        cy = rng.uniform(H * .12, H * .88)
        hh = rng.uniform(220, 420)
        amp = rng.uniform(amp_lo, amp_hi) * rng.choice((-1, 1))
        lam = rng.uniform(90, 260)
        ph = rng.uniform(0, 6.3)
        y0, y1 = int(max(0, cy - hh)), int(min(H, cy + hh))
        env = np.clip(1 - np.abs((yy[y0:y1] - cy) / hh), 0, 1) ** 1.5
        mx = (xx[y0:y1] + amp * env * np.sin(2 * np.pi * yy[y0:y1] / lam + ph)).astype(np.float32)
        my = yy[y0:y1].astype(np.float32)
        seg = cv2.remap(out, mx, my + 0, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        out = out.copy()
        out[y0:y1] = seg[:y1 - y0] if seg.shape[0] >= y1 - y0 else out[y0:y1]
    return out


def glitched(base, st, jolt):
    """その 状態の ずれた 画面（同じ 状態の 間は 同じ 絵）"""
    rng = random.Random(9100 + st * 7 + (1000 if jolt else 0))
    xx, yy = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
    img = band_warp(base, rng, 3 if jolt else rng.randint(1, 2), xx, yy, 18 if jolt else 10, 40 if jolt else 26)
    img, bands = tear(img, rng, 9 if jolt else rng.randint(3, 6), 160 if jolt else 110, 80 if jolt else 50)
    for (y0, y1) in bands[:rng.randint(1, 3)]:
        img[y0:y1] = hue_shift_same_luma(img[y0:y1], rng.choice((150, 180, 210, 90)))
    return np.clip(rgb_split(img, 16.0 if jolt else SPLIT), 0, 1)


def frame(base, fi):
    """1コマ（base：き！の 画面 0〜1 の float RGB）"""
    rng1 = random.Random(9500 + fi)
    if fi >= COLLAPSE[2]:
        return np.zeros_like(base)
    if fi >= COLLAPSE[0]:
        u = (fi - COLLAPSE[0]) / (COLLAPSE[1] - COLLAPSE[0]) if fi < COLLAPSE[1] else 1 + (fi - COLLAPSE[1] + 1) / (COLLAPSE[2] - COLLAPSE[1])
        return collapse(rgb_split(base, SPLIT), min(u, 2.0))
    if fi in BLACK:
        return blackout(rng1, base)
    st = state_of(fi)
    img = KEEP.get((st, fi in ZAP[:2]))
    if img is None:
        img = KEEP[(st, fi in ZAP[:2])] = glitched(base, st, fi in ZAP[:2])
    img = img.copy()
    # 画面の 半分が 色あいごと 入れかわる（チカチカ：明るさは かえない）
    if fi % 6 in (2, 3):
        half = slice(0, H // 2) if (fi // 6) % 2 else slice(H // 2, H)
        img[half] = hue_shift_same_luma(img[half], 170)
    sn = [(int(y), int(y + rng1.uniform(6, 20))) for y in (rng1.uniform(0, H) for _ in range(rng1.randint(1, 2)))]
    img = snow(img, rng1, sn)
    img = arcs(img, rng1, 3 if fi in ZAP else rng1.randint(1, 3))
    img = scanlines(img)
    return np.clip(img, 0, 1)


KEEP = {}


def main(src, out, which=None):
    os.makedirs(out, exist_ok=True)
    base = cv2.cvtColor(cv2.imread(src), cv2.COLOR_BGR2RGB).astype(np.float32) / 255
    assert base.shape[:2] == (H, W), base.shape
    for fi in (which or range(N)):
        im = (np.clip(frame(base, fi), 0, 1) * 255 + .5).astype(np.uint8)
        cv2.imwrite(os.path.join(out, f'g{fi + 1:03d}.png'), cv2.cvtColor(im, cv2.COLOR_RGB2BGR))
        print('g', fi + 1, flush=True)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], [int(a) - 1 for a in sys.argv[3:]] or None)
