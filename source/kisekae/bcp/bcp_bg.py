# 結果ボードカスタム（絵の ボード）：きれいに した 絵を 舞台（390×844pt）の 3倍 1170×2532 に 置く（上と 下は 鏡で 足す）・ボードの 面 → 板 の 射影
#   python3 bcp_bg.py <デザインの フォルダ>   → geom.json・<srv>/bcp_<name>.webp・bg_small.png
import json, os, sys
import numpy as np, cv2
from PIL import Image
D = sys.argv[1]
cfg = json.load(open(os.path.join(D, 'cfg.json'), encoding='utf8'))
SRV = os.environ.get('SRV', '/home/claude/work/bcpic/srv/TEST')
pic = cv2.cvtColor(cv2.imread(os.path.join(D, 'clean.png')), cv2.COLOR_BGR2RGB).astype(np.float32)
ph, pw = pic.shape[:2]
Q = np.array(cfg['quad'], np.float64)                    # 板の 四すみ（左上・右上・右下・左下）絵の px
fx0, fx1 = cfg['frame_lr']                               # 金の ふちの 外の 左右（絵の px）
S = cfg.get('S') or (380.0 / (fx1 - fx0))                 # pt / px
OX = 195 - S * cfg.get('cx', (fx0 + fx1) / 2)
OY = cfg['top_pt'] - S * (Q[0, 1] + Q[1, 1]) / 2
wq = (np.linalg.norm(Q[1] - Q[0]) + np.linalg.norm(Q[2] - Q[3])) / 2
hq = (np.linalg.norm(Q[3] - Q[0]) + np.linalg.norm(Q[2] - Q[1])) / 2
HP = float(cfg.get('hp') or round(350 * hq / wq, 1))
Qs = Q * S + np.array([OX, OY])
HB = np.array([20.0, 196.0])                              # .rb の 左上（変形 前）
srcp = np.array([(0, 0), (350, 0), (350, HP), (0, HP)], np.float32)
Hm = cv2.getPerspectiveTransform(srcp, (Qs - HB).astype(np.float32)).astype(np.float64); Hm /= Hm[2, 2]
a, b, c = Hm[0]; d, e, f = Hm[1]; g, h, _ = Hm[2]
m3d = [a, d, 0, g, b, e, 0, h, 0, 0, 1, 0, c, f, 0, 1]
K = 3; Wc, Hc = 390 * K, 844 * K
M = np.array([[S * K, 0, OX * K], [0, S * K, OY * K]], np.float32)
canvas = cv2.warpAffine(pic, M, (Wc, Hc), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
ct, cb = cfg.get('crop', [0, ph])                       # 絵の 上と 下の 使わない 行（うすい アプリの 画面が ある 所など）
top = max(0, int(np.ceil((OY + ct * S) * K))); bot = min(Hc, int(np.floor((OY + cb * S) * K)))
fillm = cfg.get('fill', {'mode': 'mirror'})
def radial(y0, y1, edge, nlen, fm=None):
    """光の すじ（まん中 c から 広がる）を 絵の はしから 外へ のばす。境目は 絵の はしの 色の まま つながり、はなれる ほど 紙ふぶきを 消した 金の 光 → 暗く"""
    import scipy.ndimage as ndi
    fillm = dict(globals()['fillm'], **(fm or {}))
    cx, cy = fillm['c']; ccx, ccy = cx * S * K + OX * K, cy * S * K + OY * K
    yy, xx = np.mgrid[y0:y1, 0:Wc].astype(np.float32)
    t = (edge - ccy) / np.where(np.abs(yy - ccy) < 1e-3, 1e-3, yy - ccy)
    qx = np.clip(ccx + (xx - ccx) * t, 0, Wc - 1).astype(np.float32)
    e0 = int(np.clip(edge, 2, Hc - 3))
    raw = cv2.GaussianBlur(canvas[e0 - 1:e0 + 2].mean(0)[None], (0, 0), 1.2)[0]
    med = ndi.median_filter(canvas[e0 - 2:e0 + 3], size=(5, fillm.get('med', 41), 1)).mean(0)
    med = cv2.GaussianBlur(med[None], (0, 0), fillm.get('blur', 1.2))[0]
    # はしの 行の 紙ふぶき・きらきら（なめらかな 行から 大きく はなれた 所）は なめらかな 行に（すじに ならない ように）
    dif = np.abs(raw - med).max(-1)
    out_ = ndi.binary_dilation(dif > fillm.get('raw_thr', 45), iterations=6)
    wq = cv2.GaussianBlur(out_.astype(np.float32)[None], (0, 0), 3)[0][:, None]
    raw = raw * (1 - wq) + med * wq
    xs = np.arange(Wc, dtype=np.float32)
    at = lambda st: np.stack([np.interp(qx.ravel(), xs, st[:, c]).reshape(qx.shape) for c in range(3)], -1).astype(np.float32)
    dist = np.abs(yy - edge)[..., None]
    a_raw = np.clip(1 - dist / float(fillm.get('raw', 40)), 0, 1)
    E = at(raw) * a_raw + at(med) * (1 - a_raw)
    ds = fillm.get('desat', 0.0)
    if ds:
        gold = np.array([1.12, 0.92, 0.55], np.float32)
        ad = ds * np.clip(dist / 120.0, 0, 1)
        E = E * (1 - ad) + np.clip(E.mean(-1, keepdims=True) * gold, 0, 255) * ad
    tt = dist / max(nlen, 1)
    k = np.clip(1 - tt / fillm.get('len', 0.75), 0, 1) ** 1.3
    k = k * (1 - (1 - fillm.get('k', 0.85)) * np.clip(dist / 120.0, 0, 1))
    floor = np.array(cfg.get('floor', [10, 8, 16]), np.float32)
    return E * k + floor * (1 - k)
if top > 0 and fillm.get('top', fillm['mode']) == 'glow':
    # 上の すき間：絵の 上の はしの 光を 横に 大きく ぼかして、上へ だんだん 暗く。絵の 上の 何行かも その 光へ なじませる（つなぎ目なし）
    go = dict({'sigma': 40, 'k_edge': 0.6, 'k_top': 0.12, 'nb': 70}, **fillm.get('top_opts', {}))
    base = canvas[top:top + 6].mean(0)
    base = cv2.GaussianBlur(base[None], (0, 0), go['sigma'])[0]
    ys = np.arange(top, dtype=np.float32)
    kk = go['k_top'] + (go['k_edge'] - go['k_top']) * (ys / max(top, 1)) ** 1.5
    canvas[:top] = base[None] * kk[:, None, None]
    nb = int(go['nb'])
    for i in range(nb):
        w = (1 - i / nb) ** 2
        canvas[top + i] = canvas[top + i] * (1 - w) + base * go['k_edge'] * w
elif top > 0 and fillm.get('top', fillm['mode']) == 'radial':
    canvas[:top] = radial(0, top, top + 6, max(top, 240), fillm.get('top_opts'))
else:
    for y in range(0, top):
        k = 0.55 + 0.45 * (y / max(top, 1))
        canvas[y] = canvas[min(top + (top - y), Hc - 1)] * k
n = Hc - bot
if n > 0 and fillm.get('bottom') == 'glow':
    # 下の すき間：絵の 下の はしの 色を 横に 大きく ぼかして、下へ だんだん 暗く（絵の 下の 何行かも なじませる）
    go = dict({'sigma': 50, 'k_edge': 0.6, 'k_bot': 0.08, 'nb': 90}, **fillm.get('bottom_opts', {}))
    base = canvas[bot - 6:bot].mean(0)
    base = cv2.GaussianBlur(base[None], (0, 0), go['sigma'])[0]
    ys = np.arange(n, dtype=np.float32)
    kk = go['k_edge'] + (go['k_bot'] - go['k_edge']) * (ys / max(n, 1)) ** 0.7
    canvas[bot:] = base[None] * kk[:, None, None]
    nb = int(go['nb'])
    for i in range(nb):
        w = (1 - i / nb) ** 2
        canvas[bot - 1 - i] = canvas[bot - 1 - i] * (1 - w) + base * go['k_edge'] * w
elif n > 0 and fillm['mode'] == 'radial' and fillm.get('bottom', 'radial') == 'radial':
    canvas[bot:] = radial(bot, Hc, bot - 6, n)
elif n > 0:
    refl = cv2.GaussianBlur(canvas[bot - n:bot][::-1].copy(), (0, 0), 2.2)
    t = np.linspace(0, 1, n)[:, None, None]
    fade = cfg.get('refl', 0.46) * np.clip(1 - t / 0.5, 0, 1) ** 1.4 + 0.02
    floor = np.array(cfg.get('floor', [16, 11, 20]), np.float32) * (1.0 - 0.45 * t)
    canvas[bot:] = refl * fade + floor * (1 - fade) * 0.9
    nb = 90
    for i in range(nb):
        canvas[bot - nb + i] *= 1.0 - 0.42 * ((i + 1) / nb) ** 1.3
# 切った 所（crop）に あった 紙ふぶき などを もどす：cfg['paste'] = [[x0,y0,x1,y1], …]（絵の px）。
#   その 四角の ふちの 色を 地と して、いちばん 地から 遠い 色との まぜ具合を すき通しに して かさねる
for pr in cfg.get('paste', []):
    x0, y0, x1, y1 = pr
    src0 = cv2.cvtColor(cv2.imread(os.path.join(D, cfg.get('src', 'src.png'))), cv2.COLOR_BGR2RGB).astype(np.float32) if 'src0' not in dir() else src0
    p_ = src0[y0:y1, x0:x1]
    edge = np.concatenate([p_[:2].reshape(-1, 3), p_[-2:].reshape(-1, 3), p_[:, :2].reshape(-1, 3), p_[:, -2:].reshape(-1, 3)])
    bgc = np.median(edge, 0)
    d_ = np.linalg.norm(p_ - bgc, axis=-1)
    fc = np.median(p_[d_ >= np.percentile(d_, 97)], 0)
    dv = fc - bgc
    al = np.clip(((p_ - bgc) @ dv) / max(float(dv @ dv), 1.0), 0, 1)
    al = np.clip((al - 0.12) / 0.88, 0, 1)
    # 紙ふぶき の かたまり（地から 十分 はなれた 色）と その まわり 2px だけ（うしろの 光の すじの むらは もどさない）
    import scipy.ndimage as ndi
    core_ = d_ >= 0.5 * d_.max()
    lab_, n_ = ndi.label(core_)
    if n_:
        sz_ = ndi.sum(core_, lab_, range(1, n_ + 1)); core_ = lab_ == (np.argmax(sz_) + 1)
    keep_ = cv2.GaussianBlur(ndi.binary_dilation(core_, iterations=2).astype(np.float32), (0, 0), 0.8)
    al = al * np.clip(keep_ * 1.5, 0, 1)
    al = np.maximum(al, cv2.GaussianBlur(ndi.binary_erosion(core_, iterations=1).astype(np.float32), (0, 0), 0.6))   # 中は すき通さない
    k_ = 3; mm = np.ones_like(al)
    mm[:k_] *= np.linspace(0, 1, k_)[:, None]; mm[-k_:] *= np.linspace(1, 0, k_)[:, None]
    mm[:, :k_] *= np.linspace(0, 1, k_)[None]; mm[:, -k_:] *= np.linspace(1, 0, k_)[None]
    al = al * mm
    col = np.clip((p_ - (1 - al[..., None]) * bgc) / np.maximum(al[..., None], 1e-3), 0, 255)
    Mp = np.array([[S * K, 0, (OX + x0 * S) * K], [0, S * K, (OY + y0 * S) * K]], np.float32)
    w4 = cv2.warpAffine(np.dstack([col * al[..., None], al]).astype(np.float32), Mp, (Wc, Hc), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    aa = np.clip(w4[..., 3:4], 0, 1)
    canvas = canvas.astype(np.float32) * (1 - aa) + np.clip(w4[..., :3], 0, 255)
canvas = np.clip(canvas, 0, 255).astype(np.uint8)
name = cfg['name']
fgp = os.path.join(D, 'fg.png')
if cfg.get('fg') and os.path.exists(fgp):
    # ボードの 前の 絵（bcp_fg）：背景と 同じ 置き方で 1170×2532 の すき通しの 絵に
    fg = np.asarray(Image.open(fgp).convert('RGBA')).astype(np.float32)
    pm = fg[..., :3] * (fg[..., 3:] / 255.0)
    w4 = cv2.warpAffine(np.dstack([pm, fg[..., 3]]), M, (Wc, Hc), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    al = np.clip(w4[..., 3], 0, 255)
    rgb = np.clip(w4[..., :3] / np.maximum(al[..., None] / 255.0, 1e-3), 0, 255)
    rgb[al < 1] = 0
    Image.fromarray(np.dstack([rgb, al]).astype(np.uint8), 'RGBA').save(os.path.join(SRV, f'bcp_{name}_fg.webp'), quality=90)
    print('fg', name, int((al > 8).sum()), 'px')
Image.fromarray(canvas).save(os.path.join(SRV, f'bcp_{name}.webp'), quality=88)
Image.fromarray(canvas).resize((390, 844), Image.LANCZOS).save(os.path.join(D, 'bg_small.png'))
json.dump({'S': S, 'OX': OX, 'OY': OY, 'HP': HP, 'm3d': m3d, 'Qs': Qs.tolist()}, open(os.path.join(D, 'geom.json'), 'w'))
print('bg', name, 'S', round(S, 4), 'HP', HP, 'pic y', round(OY, 1), round(OY + ph * S, 1))
