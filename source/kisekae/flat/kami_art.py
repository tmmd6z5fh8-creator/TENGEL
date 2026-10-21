"""神様的中の 絵（WebP）：金の 筆の 字と 金の オーラ（まさちゃん「金色のでっかい、ど！…リアルな文字で」「金色のオーラを纏ったど的中！！が縦文字で」）
   - 字の 形は ど的中の 演出と 同じ 筆の 字（brush_glyphs.json：brush.py で 筆の 動きから 描いた 形・フォントなし）
   - 描き方：形を librsvg で ぬって（3倍の 細かさで 作って もどす）、ふちからの きょり → 高さ（外の ふちの 面取り＋字の 面の 面取り）→ 向き →
     金の 光（上から 下への 金の 映りこみ＋左上からの 光＋つや＋右下の ふちの はねかえり）を numpy で。まわりに こい 茶色の ふち（白い 光の 中でも 読める）
   - 出す 絵（すき通しの ある WebP）：
       gd_dox：金の「ど！」（よこ）と まわりの 金の オーラを 1まいに（①②の ど！と とんでくる 10この ど！：1つの 層で 軽く）
       gd_fin：金の「ど的中！！」（たて書き：ど・的・中・！！（！は 2つ ならべる））／ gd_fin_aura：そのまわりの 金の オーラ（ページで ふくらむ・ひかる）
   - 絵の 大きさ（画面の px）と 字の まん中は kami_layers.json に（ページは この 箱で 置く）
   python3 flat/kami_art.py <出力フォルダ> [名前 …]   → <名前>.webp と kami_layers.json
   （絵を 作りなおしたら キャンバスに 入れて、id を kami_blobs.json に。絵は リポジトリに 入れない）"""
import sys, os, json
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
from cute_horse import svg_rgba

BZ = json.load(open(os.path.join(K, 'brush_glyphs.json'), encoding='utf-8'))
SS = 3                     # 細かく 作って もどす 倍率（ふちを なめらかに）
DPR = 2.5                  # 画面の 1px あたりの 絵の 画素（iPhone の 3倍 画面でも くっきり・重さと のつりあい）
PAD_DOX = .3               # ど！の オーラの あき（1文字の 何倍：とんでくる 10この 層が 重く ならない ように 小さく）
PAD_FIN = .75              # ど的中！！の オーラの あき
CLOSE = .016               # 筆の かすれの すきまを うめる 大きさ（1文字の 何倍）：金の かたまりに

# 字の ならび（1文字＝1000）。kern：となりの 字との つめ
DO = dict(text='ど！', kern=-90, w=350.0)                      # よこ：ど！（画面の はば 350px＝でっかい）
FIN = dict(cols=(('ど',), ('的',), ('中',), ('！', '！')), lead=-40, kern2=-120, h=640.0)   # たて：ど・的・中・！！（画面の 高さ 640px）

# 金（上から 下への 映りこみ：明るい 空 → 金 → 地平の こい 線 → 明るい 金 → こい 金）
GOLD = ((0.0, (255, 252, 226)), (0.20, (255, 222, 92)), (0.40, (232, 160, 20)), (0.47, (132, 74, 4)), (0.52, (255, 232, 140)),
        (0.70, (246, 178, 26)), (0.88, (176, 102, 8)), (1.0, (96, 52, 4)))
EDGE = (36, 18, 2)         # いちばん 外の こい 茶色の ふち
L_DIR = np.array([-.45, -.62, .64])          # 光（左上・手前）
L_DIR = L_DIR / np.linalg.norm(L_DIR)
R_DIR = np.array([.55, .55, .63])            # はねかえりの 光（右下から 少し）
R_DIR = R_DIR / np.linalg.norm(R_DIR)


def layout_do():
    """よこ書きの ど！：(path の ならび, 1000 単位の 箱)"""
    items, x = [], 0.0
    x0 = y0 = 1e9
    x1 = y1 = -1e9
    for c in DO['text']:
        g = BZ[c]
        items.append((g['d'], x, 0.0, 1.0))
        bx = g['bbox']
        x0, y0, x1, y1 = min(x0, x + bx[0]), min(y0, bx[1]), max(x1, x + bx[2]), max(y1, bx[3])
        x += g['adv'] + DO['kern']
    return items, (x0, y0, x1, y1)


def layout_fin():
    """たて書きの ど的中！！：1文字ずつ 下へ（lead：上下の つめ）。！！は 2つ よこに ならべて 1行"""
    items, y = [], 0.0
    x0 = y0 = 1e9
    x1 = y1 = -1e9
    for col in FIN['cols']:
        gs = [BZ[c] for c in col]
        wsum = sum(g['adv'] for g in gs) + FIN['kern2'] * (len(gs) - 1)
        x = 500 - wsum / 2 if len(gs) > 1 else 0.0
        top = min(g['bbox'][1] for g in gs)
        bot = max(g['bbox'][3] for g in gs)
        for g in gs:
            items.append((g['d'], x, y, 1.0))
            bx = g['bbox']
            x0, y0, x1, y1 = min(x0, x + bx[0]), min(y0, y + bx[1]), max(x1, x + bx[2]), max(y1, y + bx[3])
            x += g['adv'] + FIN['kern2']
        y += (bot - top) + FIN['lead'] if len(gs) == 1 else 0
    return items, (x0, y0, x1, y1)


def mask(items, box, k, pad):
    """形の ぬり（0〜1）：1000 単位 → 絵の 画素（k：1000 単位あたりの 画素・pad：まわりの あき 画素）"""
    x0, y0, x1, y1 = box
    W, H = int(np.ceil((x1 - x0) * k + 2 * pad)), int(np.ceil((y1 - y0) * k + 2 * pad))
    s = SS
    paths = ''.join(f'<path d="{d}" fill="#fff" fill-rule="evenodd" transform="translate({(tx - x0) * k * s + pad * s:.2f} {(ty - y0) * k * s + pad * s:.2f}) scale({k * s * sc:.5f})"/>'
                    for d, tx, ty, sc in items)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W * s}" height="{H * s}" viewBox="0 0 {W * s} {H * s}">{paths}</svg>'
    a = svg_rgba(svg, W * s, H * s)[..., 3]
    return cv2.resize(a, (W, H), interpolation=cv2.INTER_AREA)


def dist_in(a, thr=.5):
    return cv2.distanceTransform((a > thr).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE)


def grow(a, r):
    """r 画素 ふとらせる（まるく）"""
    if r <= 0:
        return a
    d = cv2.distanceTransform((a < .5).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
    return np.clip(r + .5 - d, 0, 1).astype(np.float32)


def shrink(a, r):
    """r 画素 やせさせる"""
    return 1 - grow(1 - a, r)


def close(a, r):
    """筆の かすれの すきま（細い すじ）を うめる（ふとらせて もどす）：金の かたまりに"""
    return np.clip(shrink(grow(a, r), r), 0, 1).astype(np.float32)


def ramp(t, stops):
    t = np.clip(t, 0, 1)
    xs = np.array([s for s, _ in stops])
    cs = np.array([c for _, c in stops], np.float32) / 255
    return np.stack([np.interp(t, xs, cs[:, i]) for i in range(3)], -1)


def bevel(d, w):
    """面取り：ふちで 0 → w で 1（まるく）"""
    u = np.clip(d / max(w, 1e-3), 0, 1)
    return 1 - (1 - u) ** 2


def gold(a, em, seed=3, glints=4):
    """金の 立体の 字：a＝字の ぬり・em＝1文字の 画素 → premultiplied RGBA"""
    H, W = a.shape
    body = grow(a, .045 * em)                  # 字の まわりの 金の ふち（面取り）
    edge = grow(body, .022 * em)               # いちばん 外の こい 茶色の ふち
    db, da = dist_in(body), dist_in(a)
    h = .055 * em * bevel(db, .05 * em)        # 外の ふちの 面取り
    h += .03 * em * bevel(da, .028 * em)       # 字の 面が 少し 高い（字の 形が 光で うき出る）
    h += .012 * em * np.clip(da / (.12 * em), 0, 1)      # 太い 所は ほんの 少し ふくらむ
    h = cv2.GaussianBlur(h.astype(np.float32), (0, 0), max(.6, .004 * em))
    gx = cv2.Sobel(h, cv2.CV_32F, 1, 0, ksize=3) / 8
    gy = cv2.Sobel(h, cv2.CV_32F, 0, 1, ksize=3) / 8
    n = np.dstack([-gx, -gy, np.ones_like(h)])
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    ndl = np.clip(n @ L_DIR, 0, 1)
    ndr = np.clip(n @ R_DIR, 0, 1)
    hv = (L_DIR + np.array([0, 0, 1.0]))
    hv /= np.linalg.norm(hv)
    ndh = np.clip(n @ hv, 0, 1)
    ys = (np.arange(H, dtype=np.float32)[:, None] / H) * np.ones((1, W), np.float32)
    # 金の 映りこみ：画面の 上下 ＋ 面の 向き（面取りで 映る 所が ずれる）
    t = .1 + .8 * ys + .55 * n[..., 1] - .12 * n[..., 0]
    col = ramp(t, GOLD)
    col *= (.62 + .55 * ndl)[..., None]                       # 光の 当たり方
    col += np.array([.55, .38, .12], np.float32) * (.35 * ndr ** 3)[..., None]   # 右下の ふちの はねかえり（あたたかい 光）
    spec = ndh ** 70 * 1.25 + ndh ** 12 * .22                   # つや（白く 光る 所）
    col += np.array([1.0, .97, .86], np.float32) * spec[..., None]
    col = np.clip(col, 0, 1)
    # こい 茶色の ふち（いちばん 外）：金の ふちの 外がわ
    ring = np.clip(edge - body, 0, 1)
    out = np.zeros((H, W, 4), np.float32)
    out[..., :3] = col * body[..., None] + np.array(EDGE, np.float32) / 255 * ring[..., None]
    out[..., 3] = np.clip(edge, 0, 1)
    # 金の ふちと 字の 面の さかいめに こい 線（字の 形が はっきり）
    seam = np.clip(1 - np.abs(da - .7) / 1.4, 0, 1) * body * (1 - a * 0)
    seam *= (da > 0) | (a < .5)
    out[..., :3] *= (1 - .45 * cv2.GaussianBlur(seam.astype(np.float32), (0, 0), .7))[..., None]
    # キラッ（つやの いちばん 強い 所に 小さな 光の 星）
    if glints:
        pts = []
        s2 = spec * (a > .5)
        for _ in range(glints):
            k = int(np.argmax(s2))
            yy, xx = divmod(k, W)
            if s2[yy, xx] < .6:
                break
            pts.append((xx, yy))
            cv2.circle(s2, (xx, yy), int(.35 * em), 0, -1)
        for xx, yy in pts:
            L = int(.16 * em)
            star = np.zeros((H, W), np.float32)
            cv2.line(star, (xx - L, yy), (xx + L, yy), 1.0, max(1, int(.012 * em)), cv2.LINE_AA)
            cv2.line(star, (xx, yy - L), (xx, yy + L), 1.0, max(1, int(.012 * em)), cv2.LINE_AA)
            star = cv2.GaussianBlur(star, (0, 0), .9)
            yy_, xx_ = np.mgrid[0:H, 0:W]
            fall = np.exp(-(((xx_ - xx) ** 2 + (yy_ - yy) ** 2) / (2 * (.09 * em) ** 2)))
            core = np.exp(-(((xx_ - xx) ** 2 + (yy_ - yy) ** 2) / (2 * (.022 * em) ** 2)))
            g = np.clip(star * fall + core, 0, 1) * out[..., 3]
            out[..., :3] = out[..., :3] + (out[..., 3:] - out[..., :3]) * g[..., None]
    return out


def aura(a, em, scale=.5, reach=1.0):
    """金の オーラ（字の まわりの 光）：あらい 絵（scale 倍）で ぼかす → premultiplied RGBA。reach：光の 広がり（1＝大きく）。
       絵の はしでは 0 に（光が 箱で 切れて 見えない ように）"""
    H, W = a.shape
    sm = cv2.resize(a, (max(1, int(W * scale)), max(1, int(H * scale))), interpolation=cv2.INTER_AREA)
    e = em * scale
    g1 = cv2.GaussianBlur(grow(sm, .06 * e), (0, 0), .10 * e * reach)
    g2 = cv2.GaussianBlur(grow(sm, .02 * e), (0, 0), .28 * e * reach)
    g3 = cv2.GaussianBlur(sm, (0, 0), .55 * e * reach)
    al = np.clip(.95 * g1 + .75 * g2 + .55 * g3, 0, 1)
    al = 1 - (1 - al) ** 1.6
    h_, w_ = al.shape
    yy, xx = np.mgrid[0:h_, 0:w_]
    edge = np.minimum(np.minimum(xx, w_ - 1 - xx), np.minimum(yy, h_ - 1 - yy)).astype(np.float32)
    u = np.clip(edge / max(1.0, .12 * e * reach * 2), 0, 1)
    al *= u * u * (3 - 2 * u)
    hot = np.clip(g1 * 1.2, 0, 1)                    # 字に 近い ほど 白っぽい 金
    col = ramp(1 - hot, ((0, (255, 248, 206)), (.35, (255, 214, 72)), (.7, (255, 168, 18)), (1, (255, 120, 0))))
    out = np.zeros((sm.shape[0], sm.shape[1], 4), np.float32)
    out[..., :3] = col * al[..., None]
    out[..., 3] = al
    return out


def save(img, fn, q=90):
    a = np.clip(img[..., 3], 0, 1)
    rgb = np.where(a[..., None] > 1e-4, img[..., :3] / np.maximum(a, 1e-4)[..., None], 0)
    u8 = (np.clip(np.dstack([rgb, a]), 0, 1) * 255 + .5).astype(np.uint8)
    cv2.imwrite(fn, cv2.cvtColor(u8, cv2.COLOR_RGBA2BGRA), [cv2.IMWRITE_WEBP_QUALITY, q])


def build(out, names=None):
    os.makedirs(out, exist_ok=True)
    lay = {}
    jobs = []
    items, box = layout_do()
    k_css = DO['w'] / (box[2] - box[0])                  # 1000 単位 → 画面の px
    jobs.append(('gd_do', items, box, k_css))
    items, box = layout_fin()
    k_css2 = FIN['h'] / (box[3] - box[1])
    jobs.append(('gd_fin', items, box, k_css2))
    for name, items, box, kc in jobs:
        k = kc * DPR
        em = 1000 * k
        pad_a = int((PAD_DOX if name == 'gd_do' else PAD_FIN) * em)    # オーラの ぶん
        a = close(mask(items, box, k, pad_a), CLOSE * em)
        g = gold(a, em)
        au = aura(a, em, reach=.45 if name == 'gd_do' else 1.0)
        H, W = a.shape
        if name == 'gd_do':                               # 金の 字と オーラを 1まいに（オーラは あらく 作って のばす）
            up = cv2.resize(au, (W, H), interpolation=cv2.INTER_CUBIC)
            up = np.clip(up, 0, 1)
            up[..., :3] = np.minimum(up[..., :3], up[..., 3:])
            x = g + up * (1 - g[..., 3:])
            nm = 'gd_dox'
            if not names or nm in names:
                save(x, os.path.join(out, nm + '.webp'))
            yy, xx = np.where(g[..., 3] > .002)
            lay[nm] = dict(w=round(W / DPR, 1), h=round(H / DPR, 1),
                           tx=round(float(xx.min() + xx.max()) / 2 / DPR, 1), ty=round(float(yy.min() + yy.max()) / 2 / DPR, 1),
                           gw=round(float(xx.max() - xx.min()) / DPR, 1), gh=round(float(yy.max() - yy.min()) / DPR, 1))   # 字の まん中と 大きさ（絵の 中）
            print(nm, W, 'x', H, '→ css', lay[nm])
            continue
        yy, xx = np.where(g[..., 3] > .002)              # 金の 字の 絵は オーラの あきを 切る（小さく）
        cy0, cy1, cx0, cx1 = max(0, yy.min() - 2), min(H, yy.max() + 3), max(0, xx.min() - 2), min(W, xx.max() + 3)
        gc = g[cy0:cy1, cx0:cx1]
        if not names or name in names:
            save(gc, os.path.join(out, name + '.webp'))
        if not names or name + '_aura' in names:
            save(au, os.path.join(out, name + '_aura.webp'), q=80)
        lay[name] = dict(w=round(gc.shape[1] / DPR, 1), h=round(gc.shape[0] / DPR, 1),
                         x=round(float(cx0) / DPR, 1), y=round(float(cy0) / DPR, 1))      # 字の 絵（オーラの 箱の 中の 場所）
        lay[name + '_aura'] = dict(w=round(W / DPR, 1), h=round(H / DPR, 1))
        print(name, gc.shape[1], 'x', gc.shape[0], '→ css', lay[name], ' aura', au.shape[1], 'x', au.shape[0], '→ css', lay[name + '_aura'])
    if not names:
        with open(os.path.join(K, 'kami_layers.json'), 'w', encoding='utf-8') as f:
            json.dump(lay, f, ensure_ascii=False, indent=1)
    return lay


if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2:] or None)
