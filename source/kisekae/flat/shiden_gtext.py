"""紫電（極ど的中）と ノーマルど的中の 字を まさちゃんの Meshy の 3D（GLB）で 描く（第4.163版）
   まさちゃん 2026/11/13 00:15「極ど的中の演出の馬、文字をこのファイルと入れ替えて！」・02:35「ノーマルど的中演出の文字このファイルと入れ替えて！」
     title … 極ど的中の 蹄の 場面の 縦書きの「的中」＝ Golden_Rainbow_Fortune_Symbol（的 と 中：虹色の 前の 面・金の ふち・三角 35万）
     logo  … 極ど的中の さいごの「ど！！！／極／的中」＝ Golden_Rainbow_Emblem（金の ど！！！・虹の 光芒の 上の 極・虹色の 的中：ひとかたまり・三角 91万）
     nd    … ノーマルど的中の さいごの「ど！／的中」＝ Golden_Rainbow_Pop_Typography（ど・！・的中 の 3つの かたまり・三角 38万）
   3D は リポジトリに 入れない（まさちゃんの 絵と 同じ）。場所は SD_TEXT_DIR（1つずつは SD_TITLE_GLB・SD_LOGO_GLB・SD_ND_GLB）。
   ない とき・SD_TEXT=old → flat/shiden_film.py・flat/normal_film.py は 前の 字（flat/shiden_logo.py：Dela Gothic One の 立体）で 描く
   カメラ・単位・光の まわり（映りこむ 空）は shiden_logo.py と 同じ：1 ＝ 画面の 100px（390×844 の 画面）・ロゴの 原点＝画面の (195, 400)・
     カメラは 少し 右下から（CAM_DIR）・映りこみは SL.env（スタジオの 光の 帯・だいだい／むらさきの 横の 光・走る 光の 筋・雷の 光）
   呼び方も 同じ：render() → (見える 点の データ, 箱（K 倍の px）)・layer() → (色（すき通しを かけた 線形）, すき通し, 箱)
   描き方：kisekae/r3d/glb（C の ラスタライザ）で K 倍（2倍）の 細かさの 見える 点を 出す（flat/kami_glb.py の _raster・_attrs：点を 分けて 読む）
     → 点ごとに 色・金属・つや・面の 向き（法線の 絵）→ 金属は 色の ついた 映りこみ（つやが にぶい ほど ぼかす）・色の 下じき（虹と 金が 暗い 向きでも しずまない）・
       面を てらす 光 → 白熱（ふちから 先に 冷める：前の 字と 同じ）→ 2倍から もどす"""
import copy
import math
import os
import sys
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'r3d', 'glb'))
import shiden_logo as SL                                                       # noqa: E402
import kami_glb as KG                                                          # noqa: E402

DIR = os.environ.get('SD_TEXT_DIR', '/home/claude/work/sd163/orig')
FILES = dict(title='fortune.glb', logo='emblem.glb', nd='pop.glb')
K_SS = SL.K_SS                       # 2倍で 描いて もどす
NEAR, FAR = 0.5, 400.0               # カメラの 手前・おく（ロゴの 単位）
D3 = np.diag([1.0, -1.0, -1.0])      # ラスタライザの カメラ（x 右・y 上・z 手前）↔ kami_glb の カメラ（x 右・y 下・z おく）
M_GOLD, M_HIT, M_KYOKU = SL.M_GOLD, SL.M_HIT, SL.M_KYOKU

# ---------------------------------------------------------------- 置き方（ロゴの 座標：x 右・y 上・z 手前）
TITLE_HT = 5.0                       # 縦書きの「的中」：的の 上から 中の 下まで（前の 字は 5.04）
TITLE_ZF = 0.2                       # 前の 面の z（前の 字の 前の 面と 同じ）
TITLE_DEPTH = float(os.environ.get('SD_TITLE_DEPTH', '0.55'))      # 厚みを この 倍に（3D は 厚み 1.06＝字の 高さの 4割：少し 右下から 見るので 横の 面が 広く 見えすぎる）
LOGO_WD = 3.45                       # 「ど！！！／極／的中」の はば（前の 字は 3.66＝的中の はば。3D は 上から 下まで はばが 同じ なので 少し 小さく：上と 下は 前の 字と ほぼ 同じ 高さ）
LOGO_CY = -0.05                      # まん中の 高さ（前の 字の 上と 下の まん中は −0.03）
LOGO_ZF = 0.45                       # いちばん 手前（極）の z（前の 字の「極」の 前の 面は 0.71・「ど」「的中」は 0.2）
LOGO_DEPTH = float(os.environ.get('SD_LOGO_DEPTH', '0.6'))
KY_Y = (0.38, -0.44)                 # 「極」の 上と 下（GLB の y）：雷の もと（shiden_film.py の kyoku_bolts）
ND_WD = 3.6                          # ノーマルど的中の「ど！／的中」の はば（前の 字は 3.66）
ND_FOOT = (SL.ORIGIN[1] - 624) / 100  # 足もと（「的中」の 下）の y：前の 字と 同じ（normal_film.py の LOGO_BASE＝芝の 上）
ND_ZF = 0.2
ND_DEPTH = float(os.environ.get('SD_ND_DEPTH', '0.55'))
# カメラは 少し 右下から 見る（SL.CAM_DIR）。3D の 字は 厚みが 大きい ので、そのまま 置くと 右の 横の 面が 広く 見えて 字が 右へ 曲がって 見える
#   （超神様的中の さいごの 字で まさちゃん 2026/11/13 01:10「まだ少し右に曲がってるように見える」）→ 止まった 形で 左右は カメラに ま正面（たての 軸の まわりに FACE_YAW 回して 置く）。
#   下からの 見上げ（下の 横の 面が 少し 見える）は そのまま＝立体に 見える
FACE_YAW = math.degrees(math.atan2(SL.CAM_DIR[0], SL.CAM_DIR[2])) if os.environ.get('SD_TEXT_YAW', '1') != '0' else 0.0


def path(name):
    return os.environ.get(f'SD_{name.upper()}_GLB') or os.path.join(DIR, FILES[name])


def have(names=('title', 'logo')):
    """3D が ある（names：極ど的中＝title・logo／ノーマルど的中＝nd）"""
    return all(os.path.exists(path(n)) for n in names)


_O = {}


def obj(name):
    """3D を ロゴの 座標に 置いた もの：prim・s（GLB の 1 あたり）・lo／hi（箱）・（title）gap＝的と 中の あいだ（ロゴの y）・（logo）ky＝極の 上と 下（ロゴの y）"""
    if name in _O:
        return _O[name]
    GLB, _ = KG._mods()
    ps = GLB.load(path(name)).flatten()
    assert len(ps) == 1, (name, len(ps))
    p = ps[0]
    P = p.pos.astype(np.float64)
    lo, hi = P.min(0), P.max(0)
    out = dict()
    if name == 'title':
        lab, nc = KG.comp_labels(p)
        ym = np.array([P[p.idx[lab == c]][..., 1].mean() for c in range(nc)])
        big = np.argsort(-np.bincount(lab, minlength=nc))[:2]                    # 的・中（大きい かたまり 2つ）
        top, bot = (big[0], big[1]) if ym[big[0]] > ym[big[1]] else (big[1], big[0])
        gy = (P[p.idx[lab == top]][..., 1].min() + P[p.idx[lab == bot]][..., 1].max()) / 2      # 的の 下と 中の 上の まん中
        s = TITLE_HT / (hi[1] - lo[1])
        c = np.array([(lo[0] + hi[0]) / 2, gy, hi[2]])
        o = np.array([0.0, (SL.ORIGIN[1] - SL.TITLE_Y) / 100, TITLE_ZF])           # あいだの まん中＝蹄が 切る 高さ
        zk = TITLE_DEPTH
    elif name == 'nd':
        s = ND_WD / (hi[0] - lo[0])
        c = np.array([(lo[0] + hi[0]) / 2, lo[1], hi[2]])                          # 足もとを そろえる
        o = np.array([0.0, ND_FOOT, ND_ZF])
        zk = ND_DEPTH
    else:
        s = LOGO_WD / (hi[0] - lo[0])
        c = np.array([(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, hi[2]])
        o = np.array([0.0, LOGO_CY, LOGO_ZF])
        zk = LOGO_DEPTH
        out['ky'] = tuple((y - c[1]) * s + o[1] for y in KY_Y)
    sc = np.array([s, s, s * zk])
    Ry = SL.rot_xyz(0.0, FACE_YAW, 0.0)                                          # 左右は カメラに ま正面
    q = copy.copy(p)
    q.pos = (((P - c) * sc + o) @ Ry.T).astype(np.float32)
    n = p.nrm.astype(np.float64) * np.array([1.0, 1.0, 1.0 / zk])                # 厚みを うすく した ぶん 面の 向きを 直す（法線は 逆転置）
    q.nrm = ((n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-12)) @ Ry.T).astype(np.float32)
    if p.tangent is not None:
        t = p.tangent[:, :3].astype(np.float64) * np.array([1.0, 1.0, zk])
        t /= np.linalg.norm(t, axis=1, keepdims=True) + 1e-12
        q.tangent = np.concatenate([t @ Ry.T, p.tangent[:, 3:]], 1).astype(np.float32)
    out.update(prim=q, s=s, c=c, o=o, Ry=Ry, lo=(lo - c) * sc + o, hi=(hi - c) * sc + o)
    _O[name] = out
    return out


def _view():
    """世界 → カメラ（x 右・y 上・z 手前）の 回転と 目の 場所（shiden_logo.py の カメラ）"""
    eye, tgt, fov = SL.camera()
    fw = SL.nrm(tgt - eye)
    rt = SL.nrm(np.cross(fw, (0, 1, 0)))
    up = np.cross(rt, fw)
    return np.asarray(eye, float), np.stack([rt, up, -fw])


def _cam(W, H, K):
    _, RS = KG._mods()
    return RS.Camera.look_at((0, 0, 0), (0, 0, -1), (0, 1, 0), fov_y=SL.CAM_FOV, W=W * K, H=H * K, near=NEAR, far=FAR)


def render(name, W, H, rot=(0, 0, 0), pos=(0, 0, 0), K=K_SS):
    """3D の 字 → 見える 点の データ（a・m：箱の 中の 絵／N・alb・metal・rough・Pl：見える 点ごと）と 箱（K 倍の px：x0, y0, x1, y1）。見えない → (None, None)"""
    o = obj(name)
    eye, Rv = _view()
    Rl = SL.rot_xyz(*rot)
    pos = np.asarray(pos, float)
    cam = _cam(W, H, K)
    st = KG._raster([o['prim']], D3 @ Rv @ Rl, D3 @ Rv @ (pos - eye), cam)
    if st is None:
        return None, None
    W2, H2 = cam.W, cam.H
    pix = st['pix']
    ys, xs = pix // W2, pix % W2
    pad = 6 * K
    x0 = max(0, int(xs.min()) - pad) // 2 * 2
    y0 = max(0, int(ys.min()) - pad) // 2 * 2
    x1 = min(W2, (int(xs.max()) + pad + 2) // 2 * 2)
    y1 = min(H2, (int(ys.max()) + pad + 2) // 2 * 2)
    n = len(pix)
    N = np.empty((n, 3), np.float32)
    alb = np.empty((n, 3), np.float32)
    metal = np.empty(n, np.float32)
    rough = np.empty(n, np.float32)
    Pl = np.empty((n, 3), np.float32)
    Mw = (Rv.T @ D3).astype(np.float32)                                          # kami_glb の カメラ → 世界
    C = KG.CHUNK
    for i in range(0, n, C):
        g = KG._attrs(st, slice(i, i + C))
        N[i:i + C] = g['N'] @ Mw.T
        Pl[i:i + C] = ((g['P'] @ Mw.T + eye.astype(np.float32)) - pos.astype(np.float32)) @ Rl.astype(np.float32)
        alb[i:i + C] = g['alb']
        metal[i:i + C] = g['metal']
        rough[i:i + C] = g['rough']
    iy, ix = (ys - y0).astype(np.int32), (xs - x0).astype(np.int32)
    a = np.zeros((y1 - y0, x1 - x0), np.float32)
    a[iy, ix] = 1.0
    m = np.zeros_like(a)
    if name == 'logo':
        ky = o['ky']
        mm = np.where(Pl[:, 1] > ky[0], M_GOLD, np.where(Pl[:, 1] > ky[1], M_KYOKU, M_HIT)).astype(np.float32)
    else:
        mm = np.full(n, M_HIT, np.float32)
    m[iy, ix] = mm
    return dict(a=a, m=m, iy=iy, ix=ix, N=N, alb=alb, metal=metal, rough=rough, Pl=Pl, name=name), (x0, y0, x1, y1)


# ---------------------------------------------------------------- 光らせる
ENV_W, ENV_H = 720, 360
# 見た目の 強さ（gain＝ぜんたい・spec＝映りこみ・paint＝色の 下じき・diff＝まわりの 光・edge＝ふちの 白い つや・sat＝色の こさ）。
#   蹄の 場面は さいごに 1.6倍で 仕上げる（うしろに 白い 後光）ので 的中は ひかえめに・こい 色に。さいごの ロゴは 金の 映りこみを 強く（にぶい 金に しない）
LOOK = dict(title=dict(gain=.8, spec=.8, paint=.5, diff=.15, edge=.35, sat=1.25),
            logo=dict(gain=.85, spec=1.3, paint=.35, diff=.2, edge=.35, sat=1.1),
            nd=dict(gain=1.0, spec=1.3, paint=.42, diff=.2, edge=.35, sat=1.1))
KEY_L = SL.nrm(np.array([-.45, .7, .55]))                                       # 面を てらす 光（左上 手前）


def _env_tables(sweep, flash):
    """映りこむ まわり（SL.env）を 緯度経度の 表に して ぼかした もの 2つ：少し ぼけ（つやの にぶい 所の 映りこみ）・大きく ぼけ（面を てらす 光）"""
    az = (np.arange(ENV_W) + .5) / ENV_W * 2 * np.pi - np.pi
    el = np.pi / 2 - (np.arange(ENV_H) + .5) / ENV_H * np.pi
    ce = np.cos(el)[:, None]
    R = np.stack([np.sin(az)[None, :] * ce, np.repeat(np.sin(el)[:, None], ENV_W, 1), np.cos(az)[None, :] * ce], -1).astype(np.float32)
    E, _ = SL.env(R, sweep, flash)
    E = np.concatenate([E[:, -90:], E, E[:, :90]], 1).astype(np.float32)          # 左右は つながる
    out = []
    for sg in (9.0, 34.0):                                                       # 度（表は 1画素＝0.5°）
        b = cv2.GaussianBlur(E, (0, 0), sg * 2, borderType=cv2.BORDER_REPLICATE)
        out.append(np.ascontiguousarray(b))
    return out


def _env_at(T, R):
    """表 T を 向き R（n×3）で 読む"""
    az = np.arctan2(R[:, 0], R[:, 2])
    el = np.arcsin(np.clip(R[:, 1], -1, 1))
    u = np.clip((az + np.pi) / (2 * np.pi) * ENV_W - .5 + 90, 0, T.shape[1] - 1.001).astype(np.float32)
    v = np.clip((np.pi / 2 - el) / np.pi * ENV_H - .5, 0, T.shape[0] - 1.001).astype(np.float32)
    u0, v0 = u.astype(np.int32), v.astype(np.int32)
    fu, fv = (u - u0)[:, None], (v - v0)[:, None]
    return (T[v0, u0] * (1 - fu) + T[v0, u0 + 1] * fu) * (1 - fv) + (T[v0 + 1, u0] * (1 - fu) + T[v0 + 1, u0 + 1] * fu) * fv


def shade(Rb, rect, W2, H2, rot=(0, 0, 0), pos=(0, 0, 0), sweep=None, flash=None, heat=0.0, K=K_SS, look=None):
    """見える 点の データ → 字の 色（線形・すき通しを かけた もの）と すき通し（箱の 中・K 倍）。W2, H2＝K 倍の 画面の 大きさ。
       heat＝白熱（1＝まっ白 → 0＝ふだん：ふちから 先に 冷める）・sweep＝走る 光の 筋（映りこむ 向き：度）・flash＝[(向き, 色)]（雷の 光）"""
    lk = dict(LOOK[Rb['name']])
    lk.update(look or {})
    iy, ix = Rb['iy'], Rb['ix']
    cam = SL.camera()
    V = -SL.rays(cam, W2, H2, rect)[iy, ix]                                       # 点 → 目（世界）
    N, alb = Rb['N'], Rb['alb']
    m, r = Rb['metal'][:, None], Rb['rough'][:, None]
    ndv = np.clip(np.sum(N * V, -1, keepdims=True), 0, 1)
    Rf = 2 * ndv * N - V
    E0, band = SL.env(Rf[None], sweep, flash)
    E0, band = E0[0], band[0]
    T1, T2 = _env_tables(sweep, flash)
    w1 = np.clip((r - .14) / .4, 0, 1)                                           # つやが にぶい ほど ぼけた 映りこみ
    Es = E0 * (1 - w1) + _env_at(T1, Rf) * w1
    Ed = _env_at(T2, N)
    f0 = .04 * (1 - m) + alb * m
    fres = (1 - ndv) ** 5
    fr = f0 + (1 - f0) * fres
    lit = .55 + .45 * np.clip(N @ KEY_L.astype(np.float32), 0, 1)[:, None]
    col = Es * fr * (1 - .4 * r) * lk['spec']                                   # 映りこみ（金は 金の 色・虹は 虹の 色）
    col += alb * lit * lk['paint']                                              # 色の 下じき（虹と 金が 暗い 向きでも しずまない）
    col += alb * Ed * ((1 - m) + .25 * m) * lk['diff']                          # 面を てらす まわりの 光
    col += (band * .07 + np.minimum(E0, 1.4) * (.02 + lk['edge'] * fres))       # ふちの 白い つや・光の 帯
    if lk['sat'] != 1.0:
        lum = (col @ np.float32([.3, .59, .11]))[:, None]
        col = np.clip(lum + (col - lum) * lk['sat'], 0, None)
    col *= lk['gain']
    x0, y0, x1, y1 = rect
    A = Rb['a']
    out = np.zeros((y1 - y0, x1 - x0, 3), np.float32)
    out[iy, ix] = col
    if heat > 0:                                                                 # 白熱 → 黄 → だいだい → ふだん（ふちから 先に 冷める：shiden_logo.py と 同じ）
        inner = cv2.distanceTransform((A > .5).astype(np.uint8), cv2.DIST_L2, 3) / (14.0 * K)
        h = np.clip((heat - .35 * (1 - np.clip(inner, 0, 1))) / .65, 0, 1) if heat < 1 else np.ones_like(A)
        hot = (np.array([3.2, 3.0, 2.6], np.float32) * SL._ss(.55, 1.0, h)[..., None]
               + np.array([2.6, 1.4, .3], np.float32) * (SL._ss(.0, .55, h) * (1 - SL._ss(.55, 1.0, h)))[..., None])
        # 3D の 字は ひとかたまり（字と 字が くっついて いる）なので、まっ白だと 字が 読めない → 面取りと 横の 面（こちらを 向いて いない 面）は 白熱を 暗く して 字の 形を のこす
        fs = np.zeros_like(A)
        fs[iy, ix] = (lk.get('hot_lo', .08) + (1 - lk.get('hot_lo', .08)) * ndv[:, 0] ** 5)
        mixk = np.clip(h * 1.4, 0, 1)[..., None]
        out = out * (1 - mixk) + hot * fs[..., None] * mixk
    return out * A[..., None], A


def layer(g, W, H, rot=(0, 0, 0), pos=(0, 0, 0), sweep=None, flash=None, heat=0.0, K=K_SS, look=None):
    """3D の 字の 1まい（W×H の 画面）→（色・すき通し（箱の 中）, 箱 x0, y0, x1, y1）。g＝render() の 結果（同じ 向き・場所なら 光だけ 計算し直せる）"""
    Rb, rect = g
    if Rb is None:
        return None
    col, A = shade(Rb, rect, W * K, H * K, rot, pos, sweep, flash, heat, K, look)
    x0, y0, x1, y1 = rect
    w, h = (x1 - x0) // K, (y1 - y0) // K
    col = cv2.resize(col, (w, h), interpolation=cv2.INTER_AREA)
    A = cv2.resize(A, (w, h), interpolation=cv2.INTER_AREA)
    return col, A, (x0 // K, y0 // K, x0 // K + w, y0 // K + h)


def mask_full(g, W, H, mid=None, K=K_SS):
    """すき通し（mid が あれば その 素材 だけ）を W×H の 画面に"""
    out = np.zeros((H, W), np.float32)
    Rb, rect = g
    if Rb is None:
        return out
    x0, y0, x1, y1 = rect
    w, h = (x1 - x0) // K, (y1 - y0) // K
    a = Rb['a'] if mid is None else ((np.abs(Rb['m'] - mid) < .5) & (Rb['a'] > .5)).astype(np.float32)
    out[y0 // K:y0 // K + h, x0 // K:x0 // K + w] = cv2.resize(a, (w, h), interpolation=cv2.INTER_AREA)
    return out
