"""壁紙パック（第4.92版）の 馬の コマの シート：いままでの 壁紙と 同じ 馬（flat/horse_flat：3Dの 馬の 形を ぺたっとした 色で ぬる）を、
   テーマの 色と 飾りで 描いて、コマを 横に ならべた 1まい（すき通しの WebP）に する。ページは steps で めくる（common.sheet_css）。
   ・ギャロップ：flat/sea_run.py の 足の 動き（pose_at・stance_legs）と 同じ。地面に ついている ひづめが 地面の 高さに くるように 上下を そろえ、
     宙に 浮いている コマは 前後の コマの 高さを 山なりに つなぐ（LIFT）
   ・どの コマも 同じ カメラ（最初の 形で 決める）。影は いつも 同じ 所（地面の だ円）
   ・絵の 画素は 画面の 2倍（780×320 の 中の 場所）。シートは 動く 所を まとめた 四角で 切りぬく
   使い方：from make.sheets import gallop_sheet, still_sheet, save_webp（kisekae/pack/make/<テーマ>_art.py から）"""
import hashlib
import json
import math
import os
import sys
from multiprocessing import Pool

import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.dirname(HERE)
K = os.path.dirname(PACK)
FLAT = os.path.join(K, 'flat')
SRC = os.path.dirname(K)
for p in (os.path.join(K, 'r3d'), FLAT, K, PACK):
    if p not in sys.path:
        sys.path.insert(0, p)
BLOB_DIR = os.environ.get('KISEKAE_ASSETS') or os.path.join(SRC, 'ios', 'kisekae_blobs')
W2, H2 = 780, 320
HOOF_ORDER = ('FL', 'FR', 'HL', 'HR')          # draw_horse の marks['hooves'] の 順


def _hexc(c):
    c = c.lstrip('#')
    return np.array([int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)


# ---------------------------------------------------------------- 1コマを 描く（別の プロセスでも 動く 形）
_JOB = {}


def _init(job):
    _JOB.clear()
    _JOB.update(job)


def _draw(args):
    i, pose = args
    from horse_flat import draw_horse
    J = _JOB
    acc = J['acc'](i) if J.get('acc') else None
    sp = dict(J['spot'], pose=pose, cam=J['cam'])
    sp.pop('cam_out', None)
    rgb, a, m = draw_horse(sp, J['pal'], J['W'], J['H'], acc=acc, number=J['number'], name=f"{J['tag']}{i}")
    return i, rgb.astype(np.float32), a.astype(np.float32), [tuple(map(float, h)) for h in m['hooves']]


def camera(pal, spot, number='1', tag='pkref', W=W2, H=H2):
    """その 置き場（spot の pose・box・facing・azim）の カメラ（どの コマも これで 描く）"""
    from horse_flat import draw_horse
    sp = dict(spot)
    sp['cam_out'] = []
    rgb, a, m = draw_horse(sp, pal, W, H, acc=None, number=number, name=tag)
    return sp['cam_out'], m


def render(pal, spot, poses, acc=None, number='1', tag='pk', workers=2, W=W2, H=H2, cam=None):
    """poses（horse_flat の POSES と 同じ 形の dict の ならび）を 描く → [(rgb, a, hooves)…]。acc：(コマの 番号) → 飾りの 関数（なし＝None）"""
    if cam is None:
        cam, _ = camera(pal, spot, number, tag + 'ref', W, H)
    job = dict(pal=pal, spot=spot, cam=cam, number=number, tag=tag, acc=acc, W=W, H=H)
    jobs = list(enumerate(poses))
    if workers > 1 and len(jobs) > 1:
        with Pool(workers, initializer=_init, initargs=(job,)) as pool:
            res = pool.map(_draw, jobs)
    else:
        _init(job)
        res = [_draw(j) for j in jobs]
    res.sort(key=lambda r: r[0])
    return [(r[1], r[2], r[3]) for r in res], cam


# ---------------------------------------------------------------- ギャロップ
def gallop_poses(n=10):
    import sea_run as SR
    return [SR.pose_at(i / n) for i in range(n)]


def gallop_stance(n=10):
    import sea_run as SR
    return [SR.stance_legs(i / n) for i in range(n)]


def ground_dy(frames, stance, ground, lift=6.0):
    """地面に ついている ひづめを 地面（ground：2倍の 画素）に そろえる ずれ。宙に 浮いた コマは 前後を 山なりに つなぐ"""
    n = len(frames)
    dys = []
    for (rgb, a, hooves), legs in zip(frames, stance):
        ys = [hooves[HOOF_ORDER.index(k)][1] for k in legs]
        dys.append(ground - max(ys) if ys else None)
    out = list(dys)
    for i in range(n):
        if dys[i] is None:
            jp = next(j for j in range(1, n) if dys[(i - j) % n] is not None)
            jn = next(j for j in range(1, n) if dys[(i + j) % n] is not None)
            t = jp / (jp + jn)
            prev, nxt = dys[(i - jp) % n], dys[(i + jn) % n]
            out[i] = prev + (nxt - prev) * t - lift * 4 * t * (1 - t)
    return out


def shadow_layer(W, H, cx, cy, rx, ry, blur=3.4, alpha=0.22):
    sm = np.zeros((H * 4, W * 4), np.float32)
    cv2.ellipse(sm, (int(cx * 4), int(cy * 4)), (int(rx * 4), int(ry * 4)), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
    return cv2.GaussianBlur(cv2.resize(sm, (W, H), interpolation=cv2.INTER_AREA), (0, 0), blur) * alpha


def make_sheet(frames, dys=None, dxs=None, shadow=None, pad=4, W=W2, H=H2, extra=None):
    """コマ（rgb・a）を 上下（dys）・左右（dxs）に ずらし、影（shadow＝(色, cx, cy, rx, ry, 濃さ)）を 足して、動く 所の 四角で 切りぬいて 横に ならべる。
       extra：(コマの 番号, pre, A) → (pre, A)（コマごとの 足し：しぶき・ほこり など。premultiplied）。返り値：(u8 RGBA, meta)"""
    n = len(frames)
    dys = dys or [0.0] * n
    dxs = dxs or [0.0] * n
    sm = None
    if shadow:
        col, cx, cy, rx, ry, al = shadow
        sm = shadow_layer(W, H, cx, cy, rx, ry, alpha=al)
        sc = _hexc(col)
    cells = []
    for i, ((rgb, a, _), dy, dx) in enumerate(zip(frames, dys, dxs)):
        M = np.float32([[1, 0, dx], [0, 1, dy]])
        pre = cv2.warpAffine(rgb * a[..., None], M, (W, H), flags=cv2.INTER_LINEAR)
        A = cv2.warpAffine(a, M, (W, H), flags=cv2.INTER_LINEAR)
        if sm is not None:
            pre = pre + sc[None, None, :] * (sm * (1 - A))[..., None]
            A = A + sm * (1 - A)
        if extra:
            pre, A = extra(i, pre, A)
        cells.append((pre, A))
    allA = np.max([A for _, A in cells], axis=0)
    ys, xs = np.nonzero(allA > 0.004)
    x0, x1 = max(0, xs.min() - pad), min(W, xs.max() + pad + 1)
    y0, y1 = max(0, ys.min() - pad), min(H, ys.max() + pad + 1)
    x0, y0 = x0 - x0 % 2, y0 - y0 % 2                 # 画面の 画素（半分）に そろえる
    x1, y1 = x1 + (x1 - x0) % 2, y1 + (y1 - y0) % 2
    x1, y1 = min(x1, W + (x1 - x0) % 2), min(y1, H + (y1 - y0) % 2)
    cw, ch = x1 - x0, y1 - y0
    sheet = np.zeros((ch, cw * n, 4), np.float32)
    for i, (pre, A) in enumerate(cells):
        cut_p = np.zeros((ch, cw, 3), np.float32)
        cut_a = np.zeros((ch, cw), np.float32)
        hh, ww = min(ch, H - y0), min(cw, W - x0)
        cut_p[:hh, :ww] = pre[y0:y0 + hh, x0:x0 + ww]
        cut_a[:hh, :ww] = A[y0:y0 + hh, x0:x0 + ww]
        rgb = np.where(cut_a[..., None] > 1e-4, cut_p / np.maximum(cut_a, 1e-4)[..., None], 0)
        sheet[:, i * cw:(i + 1) * cw, :3] = rgb
        sheet[:, i * cw:(i + 1) * cw, 3] = cut_a
    u8 = (np.clip(sheet, 0, 1) * 255 + .5).astype(np.uint8)
    return u8, dict(frames=n, cell=[int(cw), int(ch)], at=[int(x0), int(y0)])


def save_webp(u8, quality=90, lossless=False, out_dir=None):
    """RGBA（u8）か RGB を WebP に して、中身の md5 を id に 置く。返り値：id"""
    out_dir = out_dir or BLOB_DIR
    os.makedirs(out_dir, exist_ok=True)
    if u8.ndim == 3 and u8.shape[2] == 4:
        img = cv2.cvtColor(u8, cv2.COLOR_RGBA2BGRA)
    else:
        img = cv2.cvtColor(u8, cv2.COLOR_RGB2BGR)
    params = [cv2.IMWRITE_WEBP_QUALITY, 101 if lossless else quality]
    ok, buf = cv2.imencode('.webp', img, params)
    assert ok
    data = buf.tobytes()
    bid = hashlib.md5(data).hexdigest()
    open(os.path.join(out_dir, bid + '.webp'), 'wb').write(data)
    return bid


def gallop_sheet(pal, spot, acc=None, n=10, number='1', tag='pk', ground=None, lift=6.0, shadow=None, workers=2, extra=None):
    """ギャロップの シート。ground：地面の 高さ（2倍の 画素・なければ spot の box の 下 − 4）。shadow：(色, 濃さ) か (色, cx, cy, rx, ry, 濃さ)"""
    frames, cam = render(pal, spot, gallop_poses(n), acc=acc, number=number, tag=tag, workers=workers)
    g = ground if ground is not None else spot['box'][3] - 4
    dys = ground_dy(frames, gallop_stance(n), g, lift)
    sh = None
    if shadow:
        if len(shadow) == 2:
            xs = [h[0] for fr in frames for h in fr[2]]
            cx = (min(xs) + max(xs)) / 2
            sh = (shadow[0], cx, g + 5, (max(xs) - min(xs)) * 0.5, 6.0, shadow[1])
        else:
            sh = shadow
    u8, meta = make_sheet(frames, dys, shadow=sh, extra=extra)
    meta['dy'] = [round(float(d), 2) for d in dys]
    return u8, meta, frames, cam


def still_sheet(pal, spot, pose=None, acc=None, number='1', tag='pk', shadow=None):
    """1コマ（止まった 馬）。返り値：(u8, meta, (rgb, a, hooves))"""
    from horse_flat import draw_horse
    sp = dict(spot)
    if pose is not None:
        sp['pose'] = pose
    rgb, a, m = draw_horse(sp, pal, W2, H2, acc=acc, number=number, name=tag)
    fr = (rgb.astype(np.float32), a.astype(np.float32), [tuple(map(float, h)) for h in m['hooves']])
    sh = None
    if shadow:
        xs = [h[0] for h in fr[2]]
        g = max(h[1] for h in fr[2]) + 3
        sh = (shadow[0], (min(xs) + max(xs)) / 2, g, (max(xs) - min(xs)) * 0.55, 6.0, shadow[1]) if len(shadow) == 2 else shadow
    u8, meta = make_sheet([fr], shadow=sh)
    return u8, meta, fr


def record(theme, name, bid, meta=None):
    """kisekae/pack/blobs.json に 絵の id（と シートの 大きさ）を 書く（いくつかの 作業が 同時に 書いても こわれない ように ロックする）"""
    import fcntl
    p = os.path.join(PACK, 'blobs.json')
    with open(p + '.lock', 'w') as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        d = json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}
        d.setdefault(theme, {})[name] = dict(id=bid, **(meta or {}))
        tmp = p + '.tmp'
        json.dump(d, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
        os.replace(tmp, p)
        fcntl.flock(lk, fcntl.LOCK_UN)
    return d


def preview_png(u8, path, bg=(205, 222, 240)):
    """シートを 確かめる 用の PNG（色の 地に 重ねる）"""
    a = u8[..., 3:4].astype(np.float32) / 255
    rgb = u8[..., :3].astype(np.float32) * a + np.array(bg, np.float32)[None, None, :] * (1 - a)
    cv2.imwrite(path, cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2BGR))
