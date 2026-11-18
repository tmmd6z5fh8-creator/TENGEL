# 調査隊切符（第4.203版・まさちゃん 2026/11/19 01:42「一枚目:調査隊切符 二枚目:調査隊切符ゲージ 三枚目:調査隊切符ゲージの配置」）の 絵
#   まさちゃんの 絵（ios/cb_assets/src/：リポジトリには 入れない・上書きしない）から アプリ用の 絵を 作る。kisekae/cb_art.py の plan() に 入る（台帳・古いかの たしかめも cb_art.py と いっしょ）
#     cb_quest_ticket.png（1920×819・すき通し）      → cb_q_tk.webp（TK_W の 幅：絵の ある 所を 切り出す）＝ 切符の 窓（ゲージを タップ・切符が 足りない とき）
#     cb_quest_ticket_gauge.png（2172×724・すき通し）→ cb_q_tg.webp（TG_W の 幅：ゲージ。絵の 中の 数字「0」は 消す ＝ アプリが いまの 枚数を 書く）
#                                                    → cb_q_tgf.webp（同じ 大きさ：切符の こま 15こを 金の 切符で うめた 所 だけ。アプリは 左から n こ 分 だけ 見せる）
#     cb_quest_ticket_place.jpg（まさちゃんの「調査隊切符ゲージの配置」：マップの 上の 赤い わく）は 見る だけ（アプリには 入れない）
#   アプリ（cb/cb_app.js の QTG）に 書く 数は  python3 kisekae/cb_ticket_art.py css  で 出す（こまの 切れ目・数字の 場所：切り出した ゲージの 中の 割合 %）
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.dirname(H)
SRC = os.path.join(W, 'ios', 'cb_assets', 'src')
TK = 'cb_quest_ticket.png'
TG = 'cb_quest_ticket_gauge.png'
TK_W = 960                     # 切符の 窓の 絵の 幅（画面で 約 300px × 3倍）
TG_W = 1160                    # ゲージの 幅（画面で 約 382px × 3倍）
TH = 40                        # すき通しの ふちの もや（不透明度 40 より 下）は 消す
# 切符の こま 15こ（もとの 絵 2172×724 の 中：x0, y0, x1, y1。金の ふちの 外がわ。左から 5こ × 3組）
SLOTS = [(449, 380, 535, 448), (548, 380, 633, 448), (646, 380, 731, 448), (745, 380, 830, 448), (844, 380, 930, 448),
         (1001, 380, 1088, 448), (1103, 379, 1190, 448), (1205, 380, 1291, 448), (1305, 380, 1395, 448), (1410, 380, 1499, 448),
         (1571, 380, 1660, 448), (1674, 380, 1763, 448), (1778, 380, 1866, 448), (1881, 380, 1970, 448), (1984, 380, 2073, 448)]
ZERO = (1640, 252, 1738, 356)  # 絵の 中の 数字「0」の まわり（ここの 明るい 字を 消して、まわりの 革の 色で うめる）
NUM_RIGHT = 1728               # アプリが 書く 枚数の 右の はし（もとの「0」の 右 ＋ すこし：「／ 15 枚」の 前）
NUM_MID = 304                  # 枚数の 字の たての まん中（もとの「0」の まん中）
NUM_H = 76                     # もとの「0」の 高さ（字の 大きさの もと）
FILL = dict(core=(255, 251, 222), mid=(255, 214, 92), rim=(224, 142, 30), rays=16, ray=0.55, ray_p=8, edge=0.40, glow=0.40)      # うめる 金の 切符（まさちゃんの 見本：まん中から 光が 広がる 金）：まん中・あいだ・ふちの 色・光の すじの 数と 強さ・ふちの 影
Q = dict(quality=86, method=6, alpha_quality=100)


def PARAMS():
    """決めごと（cb_art.py の 台帳に 書く：かわったら 作り直す）"""
    return [TK_W, TG_W, TH, [list(s) for s in SLOTS], list(ZERO), NUM_RIGHT, NUM_MID, NUM_H, {k: list(v) if isinstance(v, tuple) else v for k, v in FILL.items()}, Q]


def rgba(p):
    return np.asarray(Image.open(p).convert('RGBA')).astype(np.float32)


def box_of(a, pad=2):
    """絵の ある 所（不透明度 TH より 上）＋ よゆう"""
    ys, xs = np.nonzero(a[..., 3] > TH)
    return (max(0, int(xs.min()) - pad), max(0, int(ys.min()) - pad), min(a.shape[1], int(xs.max()) + 1 + pad), min(a.shape[0], int(ys.max()) + 1 + pad))


def clean_alpha(a):
    b = a.copy(); b[..., 3] = np.clip((b[..., 3] - TH) / (236.0 - TH), 0, 1) * 255; return b


def save(img, size, path):
    im = Image.fromarray(np.clip(img + 0.5, 0, 255).astype(np.uint8), 'RGBA')
    if im.size != size: im = im.resize(size, Image.LANCZOS)
    im.save(path, 'WEBP', **Q); return os.path.getsize(path)


def ticket(p, o):
    a = clean_alpha(rgba(p)); x0, y0, x1, y1 = box_of(a, 4); b = a[y0:y1, x0:x1]
    return save(b, (TK_W, round(TK_W * (y1 - y0) / (x1 - x0))), o)


def gauge_box():
    return box_of(clean_alpha(rgba(os.path.join(SRC, TG))))


def no_zero(a):
    """数字「0」を 消す：ZERO の 中の 明るい 字（と その まわり）を、まわりの 革から 少しずつ うめる（OpenCV の inpaint）"""
    import cv2
    x0, y0, x1, y1 = ZERO
    rgb = a[..., :3].copy(); lum = rgb.mean(axis=2)
    m = np.zeros(lum.shape, np.uint8)
    sub = lum[y0:y1, x0:x1]; bg = np.median(sub)
    m[y0:y1, x0:x1] = (sub > bg + 38).astype(np.uint8)
    m = ndimage.binary_dilation(m, iterations=6).astype(np.uint8) * 255
    out = cv2.inpaint(np.clip(rgb, 0, 255).astype(np.uint8)[..., ::-1].copy(), m, 9, cv2.INPAINT_TELEA)[..., ::-1].astype(np.float32)
    # うめた 所に 革の こまかい むらを すこし もどす（まわりの むらの 強さ）
    rng = np.random.default_rng(7); noise = ndimage.gaussian_filter(rng.normal(0, 1, lum.shape), 1.2)
    sd = float(np.std(sub[sub < bg + 20] - ndimage.gaussian_filter(sub, 6)[sub < bg + 20])) if np.any(sub < bg + 20) else 3.0
    mm = ndimage.gaussian_filter((m > 0).astype(np.float32), 2.0)[..., None]
    out = out + noise[..., None] * sd * 0.8 * mm
    b = a.copy(); b[..., :3] = rgb * (1 - mm) + out * mm
    return b


def gauge(p, o):
    a = no_zero(clean_alpha(rgba(p))); x0, y0, x1, y1 = box_of(a)
    return save(a[y0:y1, x0:x1], (TG_W, round(TG_W * (y1 - y0) / (x1 - x0))), o)


def slot_inside(a, s):
    """こまの 中（金の ふちの 内がわ）：ふちより 暗い 所で、まん中に つながる 所"""
    x0, y0, x1, y1 = s; c = a[y0 - 4:y1 + 4, x0 - 4:x1 + 4]
    R, G, B = c[..., 0], c[..., 1], c[..., 2]
    gold = (R > 150) & (G > 95) & (B < 140) & (R - B > 60)
    gold = ndimage.binary_dilation(gold, iterations=1)
    lab, _n = ndimage.label(~gold)
    cy, cx = c.shape[0] // 2, c.shape[1] // 2
    inside = lab == lab[cy, cx]
    return inside, (x0 - 4, y0 - 4)


def gauge_fill(p, o):
    """こま 15こを 金の 切符で うめた 所 だけ（ほかは すき通し）"""
    a = clean_alpha(rgba(p)); out = np.zeros_like(a)
    c0, c1, c2 = (np.array(FILL[k], np.float32) for k in ('core', 'mid', 'rim'))
    for s in SLOTS:
        ins, (ox, oy) = slot_inside(a, s)
        h, w = ins.shape
        ys, xs = np.nonzero(ins); cy, cx = (ys.min() + ys.max()) / 2, (xs.min() + xs.max()) / 2
        ry, rx = (ys.max() - ys.min()) / 2 + 1, (xs.max() - xs.min()) / 2 + 1
        yy, xx = np.mgrid[0:h, 0:w]; r = np.sqrt(((yy - cy) / ry) ** 2 + ((xx - cx) / rx) ** 2); th = np.arctan2((yy - cy) / ry, (xx - cx) / rx)
        r = np.clip(r, 0, 1.2)[..., None]
        col = np.where(r < 0.45, c0 + (c1 - c0) * (r / 0.45), c1 + (c2 - c1) * np.clip((r - 0.45) / 0.65, 0, 1))      # まん中は 白に 近い 金 → ふちは こい 金
        ray = (np.abs(np.cos(th * FILL['rays'] / 2)) ** FILL['ray_p']) * np.clip(1.25 - r[..., 0], 0, 1)                    # まん中から 広がる 光の すじ
        col = col + (255 - col) * (FILL['ray'] * ray)[..., None]
        d = ndimage.distance_transform_edt(ins)
        col = col * (1 - FILL['edge'] * np.exp(-d / 2.5))[..., None]                                                    # ふちの 内がわに うすい 影（はめこんだ ように）
        al = ndimage.gaussian_filter(ins.astype(np.float32), 0.6)
        ring = ndimage.binary_dilation(ins, iterations=5) & ~ins                                                           # 金の ふち：うすく 光らせる（うめた こまが 光って 見える）
        ga = ndimage.gaussian_filter(ring.astype(np.float32), 0.8) * FILL['glow']
        sub = out[oy:oy + h, ox:ox + w]
        sub[..., :3] = np.where(ins[..., None], col, np.where((ga > 0)[..., None], np.array([255, 238, 170], np.float32), sub[..., :3]))
        sub[..., 3] = np.maximum(sub[..., 3], np.maximum(al, ga) * 255)
    x0, y0, x1, y1 = gauge_box()
    return save(out[y0:y1, x0:x1], (TG_W, round(TG_W * (y1 - y0) / (x1 - x0))), o)


def css():
    """アプリ（cb_app.js の QTG）に 書く 数：切り出した ゲージの 中の 割合（%）
       cut[n]＝左から n こ 見せる ときの 切れ目（となりの こまとの あいだ）・num＝枚数の 字（右の はし・たての まん中・字の 高さ）"""
    x0, y0, x1, y1 = gauge_box(); w, h = x1 - x0, y1 - y0
    cut = [0.0]
    for i in range(1, len(SLOTS)):
        cut.append(round(((SLOTS[i - 1][2] + SLOTS[i][0]) / 2 - x0) / w * 100, 3))
    cut.append(100.0)
    return {'cut': cut, 'right': round((x1 - NUM_RIGHT) / w * 100, 3), 'mid': round((NUM_MID - y0) / h * 100, 3), 'fs': round(NUM_H / w * 100, 3), 'ar': round(w / h, 4)}


def jobs():
    """作る もの（cb_art.plan() が 使う）：[(できる 名前, もとの 名前, 作る 関数)]"""
    return [('cb_q_tk.webp', TK, ticket), ('cb_q_tg.webp', TG, gauge), ('cb_q_tgf.webp', TG, gauge_fill)]


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'css':
        print(css())
