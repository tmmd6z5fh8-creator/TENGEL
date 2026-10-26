"""紫電（第4.71版）：3D の「ど！！！的中」（動画の さいごの 場面：flat/shiden_film.py の D）
   まさちゃん「ど！！！的中も馬とか蹄カットインと同じリアルで立体的に作成して！」「！！！のビックリマークがデカすぎて、バランス悪いから
   ！！！の上から下にかけて小さくする、はそのままでサイズとか、配置考えて青四角×の幅が開かないようにして！」
   - 字の 形は Dela Gothic One（OFL）。字ごとに 2D の 距離の 絵（中が マイナス）を 作り、sdfr の glyph（距離の 絵を 厚みで のばして 45° の 面取り・
     前の 面は ふちから 少し ふくらむ）で 3D に。うしろに 少し 大きい こい 色の 板（字の ふち）。
   - 「！」は「ど」の 右に 上から 下へ 小さく（高さ 108・84・65：3つで「ど」の 高さに おさめる）→「的中」を「ど」の すぐ 下に（あきを 作らない）。
   - 光は 2D で 計算（あとから 動かせる）：sdfr の 法線・すき通し・素材 → 金属の 映り込み（スタジオの 光の 帯・地平の 暗い 線・だいだいの 照りかえし・
     左 だいだい／右 むらさきの 横の 光・走る 光の 筋）。「ど」「！」＝金・「的中」＝つやのある 虹色（上から 下へ 赤 → むらさき）・ふちは 銀・横は 金・板は 黒。
   - 置き場所の 単位：1 ＝ 画面の 100px（390×844 の 画面）。ロゴの まん中（画面の 195, 400）が ロゴの 原点
   - 蹄の 場面の 縦書きの「的中」（title_layout）も 同じ しくみ（虹色・字の あいだが 蹄の 切る 高さ）
   - 2倍の 大きさで 描いて 縮める（K_SS）。描くのは ロゴが 入る 箱だけ（screen_rect）
   第4.76版・まさちゃん「画像のど！！！と的中の間に金色と虹色でできた、青丸のあたりに、極、って文字入れて！」
   「極もう二回り大きく！ 角度は、的中と同じ水平にして！ あともっとリアルに！」「でかすぎ！ 極もう一回り小さく！」
   → 「極」を「ど」と「的中」の あいだ（まん中より 少し 左）に 手前へ 浮かせて 置く（的中と 同じ 水平）。字の 形は Noto Sans CJK JP Black
     （SIL OFL：Dela Gothic One の「極」は すきまが 小さくて 立体に すると つぶれる）。前の 面は みがいた 金・面取りは 見る 向きで 色が かわる
     虹色の 金属（ホログラム）・横は 金・うしろに うすい こい ふち・うしろの「ど」「的中」に 影を おとす"""
import os, sys, math
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
sys.path.insert(0, os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
from h3d import Scene, nrm, load

# 字（字・横の 太さの 倍率・字の 間）と 置き場所（画面の px：字の 黒い 所の 箱 x0, y0, x1, y1）
GLYPHS = {'do': ('ど', 1.0, -40), 'ex': ('！', 1.35, -40), 'hit': ('的中', 1.0, -70), 'teki': ('的', 1.0, 0), 'chu': ('中', 1.0, 0),
          'kyoku': ('極', 1.0, 0)}
KY_BOX = (98, 357, 272, 531)                 # 第4.76版：「極」（「ど」と「的中」の あいだ：はばと まん中だけ 使う・高さは 字の 形の まま）
KYOKU_GLYPH = ('M336 57V-63H976V57ZM794 500 721 484 722 601C722 616 723 651 723 651H607L622 705H952V825H357V705H489C474 647 457 587 441 542L569 525L576 546H603C602 298 600 209 588 189C581 177 573 173 561 174C546 173 521 174 492 177C508 147 521 101 522 69C562 68 600 69 626 74C654 80 675 90 695 119C701 129 706 144 709 166C730 146 754 114 767 93C792 114 814 139 833 166C854 138 878 113 905 93C923 124 959 168 985 190C949 212 918 243 891 279C925 367 944 476 954 607L884 621L863 619H739V513H835C830 481 825 449 818 420C809 446 801 473 794 500ZM137 855V653H40V521H128C107 410 65 282 15 207C34 174 62 120 74 83C97 121 119 170 137 225V-95H266V308C281 271 295 233 304 206L357 284V137H451V208H571V511H357V330C332 374 286 452 266 482V521H347V653H266V855ZM451 416H476V303H451ZM720 416C734 367 750 319 769 276C753 243 734 215 712 193C717 240 719 311 720 416Z',
               (15, -95, 985, 855), 1000)   # 「極」の 形（Noto Sans CJK JP Black・SIL OFL 1.1：path（1000 単位・y は 上向き）・箱・送り）
LAYOUT = [('do', (53, 224, 283, 452)), ('e1', (291, 182, 336, 290)), ('e2', (300, 296, 335, 380)), ('e3', (309, 387, 336, 452)),
          ('kyoku', KY_BOX), ('hit', (12, 466, 378, 624))]     # 「的中」は さいご（HIT_Y）
PART_Z = {'kyoku': .55}                       # 第4.76版：手前へ（「ど」「的中」の 前に 浮かぶ）
PART_RZ = {'kyoku': 0.0}                      # かたむき（度）：的中と 同じ 水平
PART_PLATE = {'kyoku': .04}                   # うしろの 板（こい ふち）の 太さ（ふつうは PLATE[0]：字の すきまを うめない）
PART_BEV = {'kyoku': 1.0}                     # 面取りの 大きさの 倍率
PART_HZ = {'kyoku': .8}                       # 厚みの 倍率（横が 見えすぎない）
ORIGIN = (195.0, 400.0)                       # ロゴの 原点（画面の px）
HZ, BEV, DOME = 0.2, 0.05, (0.025, 0.10)      # 厚みの 半分・面取り・ふくらみ（高さ・はば）＝「ど」と「的中」の 大きさで。「！」は 小さく
PLATE = (0.065, 0.07)                         # うしろの 板：字より 外へ・うしろへ
M_GOLD, M_HIT, M_PLATE, M_KYOKU = 1, 2, 3, 4
CAM_DIR, CAM_DIST, CAM_FOV = (0.2, -0.13, 1.0), 11.0, 42.0
K_TEX = 0.9                                   # 字の 絵の 細かさ（1000 単位 → 画素）
_SDF = {}


def sdf(key, cache):
    """字の 距離の 絵（画素・中が マイナス）と 黒い 所の 箱（画素）"""
    if key in _SDF:
        return _SDF[key]
    fn = os.path.join(cache, f'sdf_{key}.npz')
    if os.path.exists(fn):
        z = np.load(fn)
        _SDF[key] = (z['sd'], tuple(int(v) for v in z['bb']))
        return _SDF[key]
    import kami_art as KA
    text, sxk, tr = GLYPHS[key]
    if key == 'kyoku':                                                                 # 第4.76版：「極」は Noto Sans CJK JP Black の 形
        d_, (bx0, by0, bx1, by1), _ = KYOKU_GLYPH
        items, box = [(d_, 0.0, 0.0, 1.0)], (bx0, -by1, bx1, -by0)
    else:
        items, box, _ = KA.run([(c, 1.0) for c in text], track=tr)
    a = KA.mask(items, box, K_TEX, 120)
    if sxk != 1.0:
        a = cv2.resize(a, (int(round(a.shape[1] * sxk)), a.shape[0]), interpolation=cv2.INTER_CUBIC)
    m = (a > .5).astype(np.uint8)
    din = cv2.distanceTransform(m, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
    dout = cv2.distanceTransform(1 - m, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
    sd = np.where(m > 0, dout - din + .5, dout - din - .5).astype(np.float32)
    ys, xs = np.nonzero(m)
    bb = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    os.makedirs(cache, exist_ok=True)
    np.savez(fn, sd=sd, bb=np.array(bb))
    _SDF[key] = (sd, bb)
    return _SDF[key]


TITLE_H, TITLE_GAP, TITLE_Y = 235.0, 34.0, 396.7     # 縦書きの「的中」（蹄の 場面）：字の 高さ・あいだ・あいだの まん中（画面の px＝蹄が 切る 高さ）


def title_layout(cache):
    """縦書きの「的中」の 置き場所（画面の px：字の 黒い 所の 箱）。字の 横と 縦の 比は 字の 形の まま"""
    out = []
    for name, top in (('teki', TITLE_Y - TITLE_GAP / 2 - TITLE_H), ('chu', TITLE_Y + TITLE_GAP / 2)):
        _, ib = sdf(name, cache)
        w = TITLE_H * (ib[2] - ib[0]) / (ib[3] - ib[1])
        out.append((name, (195 - w / 2, top, 195 + w / 2, top + TITLE_H)))
    return out


def parts(cache, layout=None):
    """字ごとの（名前, 字の 種類, ロゴの 中の まん中（3D）, 1画素の 長さ）"""
    out = []
    for name, (x0, y0, x1, y1) in (layout or LAYOUT):
        key = 'ex' if name.startswith('e') else name
        sd, ib = sdf(key, cache)
        sx = (x1 - x0) / 100.0 / (ib[2] - ib[0])
        icx, icy = (ib[0] + ib[2]) / 2, (ib[1] + ib[3]) / 2
        tcx, tcy = sd.shape[1] / 2, sd.shape[0] / 2
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        lx = (cx - ORIGIN[0]) / 100 + (tcx - icx) * sx
        ly = (ORIGIN[1] - cy) / 100 - (tcy - icy) * sx
        out.append((name, key, np.array([lx, ly, PART_Z.get(name, 0.0)]), sx))
    return out


def rot_xyz(rx, ry, rz):
    """度 → ロゴ → 世界 の 回転（Z・Y・X の 順に かける）"""
    a, b, c = (math.radians(v) for v in (rx, ry, rz))
    Rx = np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])
    Ry = np.array([[math.cos(b), 0, math.sin(b)], [0, 1, 0], [-math.sin(b), 0, math.cos(b)]])
    Rz = np.array([[math.cos(c), -math.sin(c), 0], [math.sin(c), math.cos(c), 0], [0, 0, 1]])
    return Rx @ Ry @ Rz


def camera():
    tgt = np.array([0.0, -0.1, 0.0])
    eye = tgt + nrm(np.array(CAM_DIR)) * CAM_DIST
    return eye, tgt, CAM_FOV


K_SS = 2                                      # 2倍の 大きさで 描いて 縮める（字の ふち・つやの ギザギザを なくす）


def corners(layout=None):
    """ロゴ 全体を かこむ 箱の 8つの かど（ロゴの 中の 座標）"""
    L = layout or LAYOUT
    xs = [(b[0] - ORIGIN[0]) / 100 for _, b in L] + [(b[2] - ORIGIN[0]) / 100 for _, b in L]
    ys = [(ORIGIN[1] - b[1]) / 100 for _, b in L] + [(ORIGIN[1] - b[3]) / 100 for _, b in L]
    m = PLATE[0] + .08
    x0, x1, y0, y1 = min(xs) - m, max(xs) + m, min(ys) - m, max(ys) + m
    z0, z1 = -(HZ + PLATE[1] + .06), HZ + DOME[0] + .06 + max([PART_Z.get(n, 0.0) for n, _ in L])
    return np.array([[x, y, z] for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)])


def project(P, cam, W, H):
    """世界の 点 → 画面の px と 奥行き"""
    eye, tgt, fov = cam
    fw = nrm(tgt - eye); rt = nrm(np.cross(fw, (0, 1, 0))); up = np.cross(rt, fw)
    th = math.tan(math.radians(fov) / 2); asp = W / H
    d = np.atleast_2d(np.asarray(P, float)) - eye
    xc, yc, zc = d @ rt, d @ up, d @ fw
    return np.stack([(xc / zc / (th * asp) + 1) * .5 * W, (1 - yc / zc / th) * .5 * H], -1), zc


def screen_rect(rot, pos, W, H, pad=8, layout=None):
    """ロゴが 入る 画面の 箱（px：x0, y0, x1, y1・偶数）。見えない → None"""
    Cw = corners(layout) @ rot_xyz(*rot).T + np.asarray(pos, float)
    p, zc = project(Cw, camera(), W, H)
    if (zc <= .2).any():
        return (0, 0, W, H)
    x0 = max(0, int(math.floor(p[:, 0].min())) - pad) // 2 * 2
    y0 = max(0, int(math.floor(p[:, 1].min())) - pad) // 2 * 2
    x1 = min(W, (int(math.ceil(p[:, 0].max())) + pad + 1) // 2 * 2)
    y1 = min(H, (int(math.ceil(p[:, 1].max())) + pad + 1) // 2 * 2)
    if x1 - x0 < 4 or y1 - y0 < 4:
        return None
    return (x0, y0, x1, y1)


def render(prefix, W, H, rot=(0, 0, 0), pos=(0, 0, 0), cache=None, K=K_SS, layout=None):
    """3D の ロゴ → sdfr の バッファ（a・n・m・ao：ロゴの 入る 箱だけ・K 倍の 大きさ）と 箱（K 倍の px）。
       rot＝度（x, y, z）・pos＝ロゴの 原点の 世界の 場所。見えない → (None, None)"""
    cache = cache or os.path.dirname(prefix)
    W2, H2 = W * K, H * K
    rect = screen_rect(rot, pos, W2, H2, layout=layout)
    if rect is None:
        return None, None
    sc = Scene()
    sc.image(W2, H2, 1, rect)
    eye, tgt, fov = camera()
    sc.camera(eye, tgt, fov)
    sc.bounce(0)
    sc.env((0.5, 0.45, 0.4), (0.2, 0.15, 0.12), (0.02, 0.015, 0.02))                 # 色は 2D で 計算（ここは AO の ため だけ）
    for mid in (M_GOLD, M_HIT, M_PLATE, M_KYOKU):
        sc.mat(mid, 0, (0.9, 0.9, 0.9), 0.2)
    Rl = rot_xyz(*rot)
    P = np.asarray(pos, float)
    tid = 0
    for name, key, c, sx in parts(cache, layout):
        sd, _ = sdf(key, cache)
        k = (sx / 0.0029) ** 0.5 if key == 'ex' else 1.0
        hz, bev = HZ * k, BEV * k
        tfn = os.path.join(cache, f'tex_{key}.f32')
        if not os.path.exists(tfn):
            sd.astype(np.float32).tofile(tfn)
        sc.raw(f'tex {tid} {sd.shape[1]} {sd.shape[0]} {tfn}')
        Rp = Rl @ rot_xyz(0.0, 0.0, PART_RZ.get(name, 0.0))                          # 第4.76版：字ごとの かたむき（「極」）
        mat = M_HIT if key in ('hit', 'teki', 'chu') else M_KYOKU if key == 'kyoku' else M_GOLD
        hzp = hz * PART_HZ.get(name, 1.0)
        sc.glyph(Rl @ c + P, sx, hzp, bev * PART_BEV.get(name, 1.0), tid, R=Rp.T, mat=mat, dome=DOME[0] * k, domew=DOME[1] * k)
        tid += 1
        pk = PART_PLATE.get(name, PLATE[0])
        pfn = os.path.join(cache, f'tex_{key}_plate.f32' if pk == PLATE[0] else f'tex_{key}_plate{int(round(pk * 1000))}.f32')
        if not os.path.exists(pfn):
            (sd - pk / sx).astype(np.float32).tofile(pfn)
        sc.raw(f'tex {tid} {sd.shape[1]} {sd.shape[0]} {pfn}')
        sc.glyph(Rl @ (c + np.array([0, 0, -PLATE[1]])) + P, sx, hzp - 0.03 * k, bev * .8, tid, R=Rp.T, mat=M_PLATE)
        tid += 1
    R = sc.render(prefix)
    x0, y0, x1, y1 = rect
    out = {k: np.ascontiguousarray(R[k][y0:y1, x0:x1]) for k in ('a', 'n', 'm', 'ao', 'd')}
    del R
    for k in ('rgb', 'a', 'd', 'n', 'm', 'ao'):
        try:
            os.remove(f'{prefix}_{k}.f32')
        except OSError:
            pass
    return out, rect


def rays(cam, W, H, rect=None):
    """画面の 点ごとの 目からの 向き（rect＝箱の 中だけ）"""
    eye, tgt, fov = cam
    x0, y0, x1, y1 = rect or (0, 0, W, H)
    fw = nrm(tgt - eye); rt = nrm(np.cross(fw, (0, 1, 0))); up = np.cross(rt, fw)
    th = math.tan(math.radians(fov) / 2); asp = W / H
    xs = ((2 * (np.arange(x0, x1) + .5) / W - 1) * th * asp).astype(np.float32)
    ys = ((1 - 2 * (np.arange(y0, y1) + .5) / H) * th).astype(np.float32)
    rd = fw[None, None, :].astype(np.float32) + rt[None, None, :].astype(np.float32) * xs[None, :, None] + up[None, None, :].astype(np.float32) * ys[:, None, None]
    return rd / np.linalg.norm(rd, axis=2, keepdims=True)


def _ss(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def env(R, sweep=None, flash=None):
    """映り込む まわり（R＝向き）：上の 明るい 空・スタジオの 光の 帯・地平の 暗い 線・だいだいの 照りかえし・左 だいだい／右 むらさき・走る 光の 筋。
       flash＝[(向き, 色)]（雷の 光）"""
    el = np.degrees(np.arcsin(np.clip(R[..., 1], -1, 1)))
    az = np.degrees(np.arctan2(R[..., 0], R[..., 2]))
    c = _ss(4, 30, el)[..., None] * np.array([1.15, .95, .7], np.float32)
    band = (_ss(9.5, 11.5, el) * (1 - _ss(15, 17.5, el)))[..., None] * np.array([2.4, 2.1, 1.7], np.float32)
    c = c + band
    c = c * (1 - .7 * (_ss(5.2, 6.2, el) * (1 - _ss(7.6, 8.8, el))))[..., None]
    c = c + (_ss(-6, -2, el) * (1 - _ss(5.2, 6.4, el)))[..., None] * np.array([1.35, .62, .16], np.float32)
    c = c + (1 - _ss(-12, -5, el))[..., None] * np.array([.22, .1, .05], np.float32)
    c = c + np.exp(-((el + 25) / 18) ** 2)[..., None] * np.array([.25, .1, .35], np.float32)
    c = c + np.exp(-((az + 70) / 25) ** 2 - (el / 30) ** 2)[..., None] * np.array([2.2, .9, .2], np.float32)
    c = c + np.exp(-((az - 70) / 25) ** 2 - (el / 30) ** 2)[..., None] * np.array([1.2, .5, 2.4], np.float32)
    if sweep is not None:
        sw = np.exp(-((az - sweep) / 3.5) ** 2) * _ss(-25, 0, el)
        c = c + sw[..., None] * np.array([4.5, 4.2, 3.8], np.float32)
        band = band + sw[..., None] * np.array([1.5, 1.4, 1.3], np.float32)
    if flash:
        for d, col in flash:
            c = c + (np.clip(np.sum(R * np.asarray(d, np.float32), axis=2), 0, 1) ** 6)[..., None] * np.asarray(col, np.float32)
    return c, band


HIT_Y = ((ORIGIN[1] - LAYOUT[-1][1][1]) / 100, (ORIGIN[1] - LAYOUT[-1][1][3]) / 100)   # 的中 の 上と 下（ロゴの 中の y）
DO_Y = ((ORIGIN[1] - min(b[1] for k, b in LAYOUT if k not in ('hit', 'kyoku'))) / 100, (ORIGIN[1] - max(b[3] for k, b in LAYOUT if k not in ('hit', 'kyoku'))) / 100)   # 「ど」「！」の 上と 下（第4.73版：虹の ど）
KY_Y = ((ORIGIN[1] - KY_BOX[1]) / 100, (ORIGIN[1] - KY_BOX[3]) / 100)          # 第4.76版：「極」の 上と 下（面取りの 虹）
_RAIN = None


def rainbow(u):
    """0〜1（的中 の 上 → 下）→ 虹色（線形）：赤 → だいだい → 黄 → 緑 → 水色 → 青 → むらさき"""
    global _RAIN
    if _RAIN is None:
        uu = np.linspace(0, 1, 512)
        hue = (0.96 + uu * 0.8) % 1.0
        hsv = np.stack([hue * 179, np.full_like(uu, 235), np.full_like(uu, 255)], 1)[None].astype(np.uint8)
        _RAIN = (cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)[0].astype(np.float32) / 255) ** 2.2
    return _RAIN[np.clip((u * 511).astype(np.int32), 0, 511)]


PALETTES = {   # ロゴの 色。face・bev・side＝「ど」「！」の 金属（前の 面・面取り・横）・do＝'rainbow' なら「ど」「！」の 前の 面も 虹・hit＝「的中」の 前の 面（rainbow か 金属の 色）・
               # plate＝うしろの 板・gain＝映り込みの 明るさ。第4.72版〜第4.73版の 細切れの 色（赤・青・緑・紫・金・白・虹）は 第4.74版で 細切れを やめたので 消した
    'gold': dict(face=(1.0, .64, .20), bev=(1.0, .84, .48), side=(.85, .45, .1), hit='rainbow', hbev=(.95, .95, .97), plate=(.05, .045, .05), gain=1.0,
                 kface=(1.0, .66, .22)),      # 本物：金と 虹（kface＝第4.76版の「極」の 前の 面の 金）
}


def shade(Rb, rect, W, H, rot=(0, 0, 0), pos=(0, 0, 0), sweep=None, flash=None, heat=0.0, K=K_SS, hit_y=None, pal='gold'):
    """sdfr の バッファ（render の 箱の 中）→ ロゴの 色（線形・すき通しを かけた もの）と すき通し（どちらも 箱の 中・K 倍）。
       W, H＝K 倍の 画面の 大きさ。heat＝白熱（1＝まっ白 → 0＝ふだん：ふちから 先に 冷める）。pal＝色（PALETTES）"""
    n, A, m, ao, dep = Rb['n'], Rb['a'], Rb['m'], Rb['ao'], Rb['d']
    cam = camera()
    rd = rays(cam, W, H, rect)
    Rl = rot_xyz(*rot).astype(np.float32)
    nl = n @ Rl                                                                        # ロゴの 中の 法線（前の 面＝+z）
    Rf = rd - 2 * np.sum(rd * n, axis=2, keepdims=True) * n
    E, band = env(Rf, sweep, flash)
    cosv = np.clip(-np.sum(rd * n, axis=2), 0, 1)
    fz = nl[..., 2]
    face = _ss(.8, .9, fz)
    bev = _ss(.35, .55, fz) * (1 - face)
    side = 1 - _ss(.35, .55, fz)
    is_g = np.abs(m - M_GOLD) < .5; is_h = np.abs(m - M_HIT) < .5; is_p = np.abs(m - M_PLATE) < .5; is_k = np.abs(m - M_KYOKU) < .5
    P = PALETTES[pal]
    gface, gbev, gside = (np.array(P[k], np.float32) for k in ('face', 'bev', 'side'))
    F0 = (is_g[..., None]) * (gface * face[..., None] + gbev * bev[..., None] + gside * side[..., None])
    hmetal = not isinstance(P['hit'], str)
    hface = np.array(P['hit'], np.float32) if hmetal else np.zeros(3, np.float32)
    F0 = F0 + (is_h[..., None]) * (hface * face[..., None] + np.array(P['hbev'], np.float32) * bev[..., None] + gside * side[..., None])
    F0 = F0 + is_p[..., None] * np.array(P['plate'], np.float32)
    F0 = F0 + is_k[..., None] * (np.array(P.get('kface', P['face']), np.float32) * face[..., None] + gbev * bev[..., None] + gside * side[..., None])   # 第4.76版：「極」は 金
    fres = (1 - cosv) ** 5
    F = F0 + (1 - F0) * fres[..., None] * (F0.max(2, keepdims=True) > 0)
    col = F * E * (.35 + .65 * ao[..., None]) * P.get('gain', 1.0)
    # 的中 の 前の 面：つやのある 虹色（ロゴの 中の 高さで 上から 下へ：字に はりつく）
    eye = cam[0].astype(np.float32)
    pw = eye + rd * np.maximum(dep, 0)[..., None]
    ql = (pw - np.asarray(pos, np.float32)) @ Rl
    hy = hit_y or HIT_Y
    u = (hy[0] - ql[..., 1]) / (hy[0] - hy[1])
    rain = rainbow(u)
    lit = .75 + .25 * np.clip(nl[..., 1] * .5 + .5, 0, 1)
    paint = rain * (.5 + .3 * lit)[..., None] + (0.01 + 0.3 * fres)[..., None] * np.minimum(E, 1.2) + .07 * band
    hf = (is_h & (face > .01) & (not hmetal))[..., None]
    col = np.where(hf, paint * face[..., None] + col * (1 - face[..., None]), col)
    if P.get('do') == 'rainbow':                                                       # 第4.73版：「ど」「！」の 前の 面も 虹（上から 赤 → むらさき）
        u2 = (DO_Y[0] - ql[..., 1]) / (DO_Y[0] - DO_Y[1])
        paint2 = rainbow(u2) * (.5 + .3 * lit)[..., None] + (0.01 + 0.3 * fres)[..., None] * np.minimum(E, 1.2) + .07 * band
        gf = (is_g & (face > .01))[..., None]
        col = np.where(gf, paint2 * face[..., None] + col * (1 - face[..., None]), col)
    if is_k.any():                                                                     # 第4.76版：「極」
        # 面取り：見る 向きで 色が かわる 虹色の 金属（ホログラム）＝面の 向きと 映り込みで 色相が まわる・映り込みの 明るさで 光る
        uk = (KY_Y[0] - ql[..., 1]) / (KY_Y[0] - KY_Y[1])                            # 左上（赤）→ 右下（むらさき）の 虹 ＋ 見る 向きで 少し ずれる
        ux = (ql[..., 0] - (KY_BOX[0] - ORIGIN[0]) / 100) / ((KY_BOX[2] - KY_BOX[0]) / 100)
        irid = rainbow(np.clip(.62 * uk + .38 * ux + .12 * (Rf[..., 1] + Rf[..., 0]), 0, 1))
        elum = np.minimum(E.mean(2, keepdims=True), 2.2)
        paintk = irid * (.22 + .9 * elum) + .35 * band + (0.03 + 0.5 * fres)[..., None] * np.minimum(E, 1.6)
        kb = np.clip(bev * 1.2, 0, 1)
        col = np.where(is_k[..., None], paintk * kb[..., None] + col * (1 - kb[..., None]), col)
        # うしろの「ど」「的中」に おとす 影（光は 左上 → 影は 右下へ ずれて ぼける）
        km = ((is_k | (is_p & (np.abs(dep - dep[is_k].mean()) < .35 if is_k.any() else False))) & (A > .5)).astype(np.float32)
        sh = cv2.GaussianBlur(km, (0, 0), 7 * K)
        Msh = np.float32([[1, 0, 11 * K], [0, 1, 15 * K]])
        sh = cv2.warpAffine(sh, Msh, (sh.shape[1], sh.shape[0]))
        back = (~is_k & (km < .5))[..., None]
        col = np.where(back, col * (1 - .6 * np.clip(sh, 0, 1))[..., None], col)
    if heat > 0:                                                                       # 白熱 → 黄 → だいだい → ふだん（ふちから 先に 冷める）
        inner = cv2.distanceTransform(((A > .5) & ~is_p).astype(np.uint8), cv2.DIST_L2, 3) / (14.0 * K)
        h = np.clip((heat - .35 * (1 - np.clip(inner, 0, 1))) / .65, 0, 1) if heat < 1 else np.ones_like(A)
        hot = np.array([3.2, 3.0, 2.6], np.float32) * _ss(.55, 1.0, h)[..., None] + np.array([2.6, 1.4, .3], np.float32) * (_ss(.0, .55, h) * (1 - _ss(.55, 1.0, h)))[..., None]
        mixk = np.clip(h * 1.4, 0, 1)[..., None] * (~is_p)[..., None]
        col = col * (1 - mixk) + hot * mixk
    return col * A[..., None], A


def layer(prefix, W, H, rot=(0, 0, 0), pos=(0, 0, 0), sweep=None, flash=None, heat=0.0, cache=None, K=K_SS, layout=None, hit_y=None, gbuf=None, pal='gold'):
    """3D の ロゴの 1まい（W×H の 画面）→（色・すき通し（箱の 中）, 箱 x0, y0, x1, y1）。見えない → None
       gbuf＝前に 描いた 形（render の 結果：同じ 向き・場所なら 光だけ 計算し直す）"""
    Rb, rect = gbuf if gbuf is not None else render(prefix, W, H, rot, pos, cache, K, layout)
    if Rb is None:
        return None
    col, A = shade(Rb, rect, W * K, H * K, rot, pos, sweep, flash, heat, K, hit_y, pal)
    x0, y0, x1, y1 = rect
    w, h = (x1 - x0) // K, (y1 - y0) // K
    col = cv2.resize(col, (w, h), interpolation=cv2.INTER_AREA)
    A = cv2.resize(A, (w, h), interpolation=cv2.INTER_AREA)
    return col, A, (x0 // K, y0 // K, x0 // K + w, y0 // K + h)


def outline(A, step=3):
    """すき通しの ふち → [(x, y, 外向きの nx, ny)]（雷の もと）"""
    m = (A > .5).astype(np.uint8)
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    out = []
    for c in cs:
        c = c[:, 0, :].astype(np.float32)
        if len(c) < 12:
            continue
        for i in range(0, len(c), step):
            p0, p1 = c[(i - 3) % len(c)], c[(i + 3) % len(c)]
            t = p1 - p0
            nv = np.array([t[1], -t[0]], np.float32)
            nv /= np.linalg.norm(nv) + 1e-6
            q = c[i] + nv * 4
            qi = (int(np.clip(q[1], 0, m.shape[0] - 1)), int(np.clip(q[0], 0, m.shape[1] - 1)))
            if m[qi]:
                nv = -nv
            out.append((float(c[i][0]), float(c[i][1]), float(nv[0]), float(nv[1])))
    return out
