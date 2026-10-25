"""紫電（しでん）の ど的中の ③ の 絵（WebP）：まさちゃん「新しい的中演出を作成したい！ 85枚の画像が入ったファイルとGIFを送るね！ そのGIFと画像を元に的中演出作成して！
   求めているのは、同じ感じの演出・圧倒的な迫力・見ていて気持ちのいい当たり演出になること！ 鬼の文字を的中に変えて、最後の鬼ががり6000の所を、
   鬼ががりの所をど！！！ビックリマークは上から下に小さく！6000の所を的中に変えて作成してみて！」
   - 送ってくれた 動画（パチンコの 演出）は 流れ・色・迫力を 見るだけ。登場人物・絵・字・ロゴは 使わない・なぞらない（権利の ある 絵なので）。ここで 一から 作る
   - 出す 絵（大きさと 置き場所は shiden_layers.json・id は shiden_blobs.json（中身の md5）。絵は リポジトリに 入れない）：
       sd_rtex     … 虹の ノイズの 布（さいごの 背景・流す）
       sd_t_do     …「ど」（炎の 金の 立体の 字・Dela Gothic One）
       sd_t_ex     …「！」（同じ 作り。CSS で 3つ・上から 下へ 小さく）
       sd_t_hit    …「的中」（虹色の つやの 立体の 字・黒い ふちと 白い 内ふち）
   - 第4.70版：① の 馬の 影・紫の 炎・ただよう 的中の 字と ② の コマの 絵（第4.67版〜第4.69版：shiden_cuts.py・shiden_face.py）は やめた。
     ② は 1コマずつ 3D で 描いた 動画（flat/shiden_film.py → sd_film.mp4）
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
    todo = {'sd_rtex': lambda: rtex(out), 'sd_t_do': lambda: fire_letter(out, 'sd_t_do', 'ど', 150), 'sd_t_ex': lambda: fire_letter(out, 'sd_t_ex', '！', 150),
            'sd_t_hit': lambda: hit_logo(out)}
    made = []
    for key, fn in todo.items():
        if names and key not in names:
            continue
        r = fn()
        made += r if isinstance(r, list) else [r]
        print('made', r, flush=True)
    # いま 使う 絵だけ のこす（第4.70版：③ の 4まい。前の 版の ① ② の 絵は 消す）
    for k in list(LAY):
        if k not in todo:
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
