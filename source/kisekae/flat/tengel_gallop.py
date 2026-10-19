"""マスター帯の壁紙：エンブレムの馬が 本物の馬のように 走る コマ（flat/tengel_run.py が シートにする・ページは tengel_wall.py）
   まさちゃんの指定（2026/10/20・3回目）「脚の切れ目が見えて変 → 動かしても切れ目がない一体型の脚」「脚しか動いていないので不自然 →
   体もジョッキーも 動画の馬と騎手のように動かしてリアルに」「速すぎると不自然なので もう少しゆっくり」
   - 体・首と頭・騎手・たてがみ：もとの絵（説明書の上の絵の切り出し）を そのまま使い、3本の骨（体・頭・騎手）で 少しずつ 動かす。
     どの骨に どれだけ ついていくか（重さ）は なめらかに かわるので ちぎれない（皮膚つきの骨＝LBS を、描く がわから 逆に 解く：inverse_lbs）
     体：1歩に1回 上下（地面を けって 宙に 浮く時が いちばん上）・前後に かたむく（前足で 体を 持ち上げる時に 鼻先が 上）
     頭：首の つけねを 中心に うなずく（前足が 地面に つく時に 下がる）。騎手：体の かたむきを 7わり もどし・上下は 半分（ひざで うける）
   - 足：もとの絵の 足は 消して、同じ 金の板（光の 当たる 半分は 明るく・のこりは ふつう・かげの がわに こい線・まわりに 紺の ふち）で
     描きなおす。ひざ（後ろ足は 飛節）で とがらせて つなぐので 切れ目が ない。つけねは 体の 下に かくれる（足は 体の うしろ）
     4本が 順に 地面につく（奥の後ろ → 手前の後ろ → 奥の前 → 手前の前：FOOTFALL）→ 宙に浮く。ひづめの 通り道（PATH）から
     骨の 向きを 計算する（IK）。地面に ついている間は ひづめが 地面の 上を まっすぐ うしろへ（体が 上下しても 地面から はなれない）
   - 上がる グラフの 矢（体の上を 通る）は 動かさない（いちばん 上に 重ねる）
   python3 flat/tengel_gallop.py --plan  → 1歩の 予定（地面に ついている足・体の 上下と かたむき・頭）"""
import math
import numpy as np
import cv2

W, Hh = 780, 320
PERIOD = 0.75                   # 1歩（秒）：まえの 0.5秒より ゆっくり
FRAMES = 18                     # 1歩の コマ（1秒に 24コマ）

# ---------- 形（780×320 の 座標） ----------
BODY = [(157, 179), (157, 140), (162, 116), (176, 95), (205, 90), (232, 104), (246, 109), (266, 116.5), (276, 117), (275, 140), (276, 165),
        (264, 164.5), (250, 166), (240, 167), (214, 168.5), (211, 179.5)]            # 体（この中は ぜんぶ 体：紺の 面も）。下の ふちは 胸と 腹の 面の 下
HEAD = [(243, 103.5), (262, 92), (275.5, 83.5), (278, 64), (281.5, 64), (284, 73), (292, 79), (330, 116), (322, 132), (300, 121.5),
        (292, 117), (281, 115.5), (266, 116.5), (246, 109)]                           # 頭と 首の 上（この中の 紺でない 所と その ふち）
JOCKEY = [(166, 84), (172, 78), (180, 72), (198, 69), (214, 68), (218, 60), (226, 56), (236, 56), (243, 62), (246, 72), (240, 76), (238, 84),
          (236, 92), (242, 97), (243, 106), (232, 108), (218, 106), (212, 112), (206, 120), (196, 121), (180, 110), (168, 96)]
MANE = [[(247, 74), (274, 74), (274, 83), (247, 83)], [(233, 85), (259, 84), (260, 89), (254, 97), (234, 97), (231, 91)]]   # たてがみ（金の 2本）
HANDS = [(228, 92), (246, 92), (248, 110), (228, 110)]                                  # 騎手の 手（騎手と 頭の あいだ）
RIM = [(277, 112), (294, 112), (294, 172), (277, 172)]                                  # 盾の 右の 金の ふち（体ではない）
ARROW = [(93, 194), (154, 139.5), (155, 113.5), (186.5, 113.5), (189, 119), (176.5, 136), (191, 136.5), (192, 150.5), (160.5, 152.5), (99, 201)]
ARROW_DIR = (0.67, -0.74)                                                               # 矢の 向き（手前の 後ろ足の 上は この線で 切る）
# 足：つけね（体の中）・上と下の 長さ・はば（上・ひざ・ひづめ）・色・地面の 高さ（奥の 足は 少し上）
LEG = dict(
    HL2=dict(kind='H', root=(167, 174), a=26, b=40, w=(8.5, 6.0, 5.0), pal='farh', ground=236),
    FL2=dict(kind='F', root=(260, 163), a=35, b=41, w=(11.0, 7.5, 6.5), pal='farf', ground=236),
    HL1=dict(kind='H', root=(151, 173), a=30, b=52, w=(13.0, 8.0, 7.0), pal='near', ground=244, top=ARROW_DIR, ext=0.0),
    FL1=dict(kind='F', root=(224, 166), a=39, b=46, w=(12.5, 8.5, 7.0), pal='near', ground=244))
LEG_ORDER = ('HL2', 'FL2', 'HL1', 'FL1')       # 奥から
EXT = 9.0                                      # 足の 上を 体の 中へ のばす 長さ（かくれる）
HIND_UP = (-80.0, 5.0)                         # 後ろ足の 上の 骨の 向きの はば（下＝0°・前＋）
SS = 4                                         # 足を 描く 倍率（ちぢめて なめらかに）

# ---------- 走り方 ----------
FOOTFALL = dict(HL2=0.00, HL1=0.045, FL2=0.38, FL1=0.60)   # ひづめが つく 位相：奥の後ろ → 手前の後ろ → 奥の前 → 手前の前（動画では 前足2本の あいだが ひらく）
# ひづめの 通り道：つけねからの 位置を 足の長さで わった値（x 前＋・y 下＋）。その足が つく時＝0。
# 地面（ground）に ついている間（〜stance）は x0 → x1 へ まっすぐ・同じ速さ。宙は swing の点を なめらかに つなぐ（地面の 速さに つながる）
PATH = dict(
    F=dict(stance=0.30, ground=0.87, x0=0.48, x1=-0.46,
           swing=[(0.36, -0.52, 0.70), (0.44, -0.30, 0.42), (0.52, 0.00, 0.36), (0.60, 0.30, 0.48), (0.68, 0.55, 0.62),
                  (0.76, 0.68, 0.70), (0.86, 0.62, 0.78), (0.94, 0.53, 0.84)]),
    H=dict(stance=0.27, ground=0.90, x0=0.18, x1=-0.48,
           swing=[(0.35, -0.58, 0.64), (0.45, -0.50, 0.48), (0.56, -0.24, 0.44), (0.68, 0.10, 0.56), (0.80, 0.28, 0.72),
                  (0.90, 0.23, 0.85)]))
# 体の 動き（780 の 座標・度）：上下 dy（下＋）・かたむき pitch（鼻先 上＋）・頭 head（鼻先 上＋）。cos(2π(g−ph)) の ふれはば
HIP = (172.0, 142.0)            # 体が かたむく 中心（おしり）
NECK = (262.0, 111.0)           # 首の つけね
SEAT = (205.0, 112.0)           # 騎手の すわる所
MOTION = dict(dy=3.0, dy_ph=0.50, pitch=3.0, pitch_ph=0.85, head=6.5, head_ph=0.12, jrot=0.7, jbob=0.5)

# ---------- 足の 色（RGB） ----------
LIGHT = np.array([-0.6, -0.8])  # 光の 来る 向き（左上）
PAL = dict(
    near=dict(hi=(239, 217, 154), base=(214, 172, 84), shade=(160, 120, 50), line=(10, 22, 28)),
    farf=dict(hi=(186, 166, 112), base=(165, 132, 66), shade=(122, 92, 40), line=(8, 18, 24)),
    farh=dict(hi=(46, 92, 118), base=(15, 48, 72), shade=(6, 30, 50), line=(3, 17, 28)),
    white=dict(hi=(255, 255, 255), base=(255, 255, 255), shade=(255, 255, 255), line=(255, 255, 255)))
LINE_W = 1.6                    # ふちの 線


# ================= 走り方 =================
def _cr(ext, p):
    """(位相, x, y) の 列を Catmull-Rom で（間かくが ふぞろいでも）"""
    i = max(j for j in range(1, len(ext) - 2) if ext[j][0] <= p)
    out = []
    for col in (1, 2):
        p0, p1, p2, p3 = (ext[i + d][col] for d in (-1, 0, 1, 2))
        t0, t1, t2, t3 = (ext[i + d][0] for d in (-1, 0, 1, 2))
        m1 = (p2 - p0) / (t2 - t0)
        m2 = (p3 - p1) / (t3 - t1)
        h = t2 - t1
        s = (p - t1) / h
        out.append((2 * s**3 - 3 * s**2 + 1) * p1 + (s**3 - 2 * s**2 + s) * h * m1
                   + (-2 * s**3 + 3 * s**2) * p2 + (s**3 - s**2) * h * m2)
    return tuple(out)


def hoof(kind, psi):
    """足の位相 psi の ひづめの位置（つけねからの x・y を 足の長さで わった値）"""
    spec = PATH[kind]
    psi %= 1.0
    st, gy, x0, x1 = spec['stance'], spec['ground'], spec['x0'], spec['x1']
    if psi <= st:
        return x0 + (x1 - x0) * psi / st, gy
    v = (x1 - x0) / st
    ext = [(st - .06, x1 - v * .06, gy), (st, x1, gy)] + list(spec['swing']) + [(1.0, x0, gy), (1.06, x0 + v * .06, gy)]
    return _cr(ext, psi)


def contact(kind, psi):
    """ひづめが 地面に ついている 度合い（0〜1・はなれる／つく 前後は なめらかに）"""
    st = PATH[kind]['stance']
    psi %= 1.0
    e = 0.05
    if psi <= st:
        return 1.0
    if psi < st + e:
        t = (psi - st) / e
        return 1 - t * t * (3 - 2 * t)
    if psi > 1 - e:
        t = (psi - (1 - e)) / e
        return t * t * (3 - 2 * t)
    return 0.0


def ik(a, b, tx, ty, knee_front, lim=None):
    """つけね(0,0) → ひづめ (tx, ty)。上の骨 a・下の骨 b。戻り値：上と下の 向き（下＝0°・前＝＋）。
       knee_front：ひざが 前（前足）・うしろ（後ろ足）。lim＝上の骨の 向きの はば（はみ出たら おさえて、下の骨は ひづめへ 向ける）"""
    d = math.hypot(tx, ty)
    d = min(max(d, abs(a - b) + 1e-3), a + b - 1e-3)
    A = math.degrees(math.acos(max(-1.0, min(1.0, (a * a + d * d - b * b) / (2 * a * d)))))
    ph = math.degrees(math.atan2(tx, ty))
    au = ph + A if knee_front else ph - A
    if lim:
        au = min(max(au, lim[0]), lim[1])
    kx, ky = a * math.sin(math.radians(au)), a * math.cos(math.radians(au))
    return au, math.degrees(math.atan2(tx - kx, ty - ky))


def rotm(deg, c):
    """c を 中心に deg 回す 3×3（＋＝見た目の 反時計回り＝鼻先が 上・y 下向きの 座標）"""
    a = math.radians(deg)
    R = np.array([[math.cos(a), math.sin(a)], [-math.sin(a), math.cos(a)]])
    T = np.eye(3)
    T[:2, :2] = R
    T[:2, 2] = np.array(c) - R @ np.array(c)
    return T


def trans(dx, dy):
    T = np.eye(3)
    T[:2, 2] = (dx, dy)
    return T


def body_pose(g, p=MOTION):
    """位相 g の 体・頭・騎手の 3×3（780 の 座標）"""
    th = p['pitch'] * math.cos(2 * math.pi * (g - p['pitch_ph']))
    dy = p['dy'] * math.cos(2 * math.pi * (g - p['dy_ph']))
    hd = p['head'] * math.cos(2 * math.pi * (g - p['head_ph']))
    B = trans(0, dy) @ rotm(th, HIP)
    return dict(body=B, head=B @ rotm(hd, NECK), jockey=B @ rotm(-p['jrot'] * th, SEAT) @ trans(0, -p['jbob'] * dy), th=th, dy=dy, hd=hd)


def leg_pts(L, g, B):
    """足の 点（780 の 座標）：[体の中の 点, ひざ, ひづめ]・底の 線の 向き・地面に ついている 度合い"""
    c = LEG[L]
    kind = c['kind']
    R0 = np.array(c['root'], float)
    Rw = (B @ np.append(R0, 1))[:2]                     # つけねは 体と いっしょに 動く
    a, b = c['a'], c['b']
    Lt = a + b
    psi = g - FOOTFALL[L]
    hx, hy = hoof(kind, psi)
    hy = hy * ((c['ground'] - R0[1]) / Lt) / PATH[kind]['ground']     # 地面の 高さを この足の 地面に
    tx, ty = R0[0] + hx * Lt, R0[1] + hy * Lt          # ひづめの 目当て（地面は 動かない）
    au, al = ik(a, b, tx - Rw[0], ty - Rw[1], knee_front=(kind == 'F'), lim=None if kind == 'F' else HIND_UP)
    du = np.array([math.sin(math.radians(au)), math.cos(math.radians(au))])
    dl = np.array([math.sin(math.radians(al)), math.cos(math.radians(al))])
    Kw = Rw + a * du
    Tw = Kw + b * dl
    top = Rw - du * c.get('ext', EXT)
    cf = contact(kind, psi)
    perp = np.array([dl[1], -dl[0]])
    if perp[0] < 0:
        perp = -perp
    ap = math.atan2(perp[1], perp[0])
    da = (0.0 - ap + math.pi) % (2 * math.pi) - math.pi
    da = max(-math.radians(38), min(math.radians(38), da * cf))      # 底は 地面に そろえる（骨に 直角から 38° まで）
    return [top, Kw, Tw], np.array([math.cos(ap + da), math.sin(ap + da)]), cf


# ================= 足を 描く（金の 板） =================
def _n(v):
    return v / max(float(np.linalg.norm(v)), 1e-9)


def _left(d):
    return np.array([d[1], -d[0]])                     # y 下向きの 座標で 進む向きの 左


def _isect(p, d, q, e):
    den = d[0] * e[1] - d[1] * e[0]
    if abs(den) < 1e-9:
        return None
    t = ((q[0] - p[0]) * e[1] - (q[1] - p[1]) * e[0]) / den
    return p + t * d


def offsets(pts, widths, f, end_dir, top_dir=None, miter_lim=2.0):
    """f（左が ＋・はばの 割合）だけ ずらした 線：点ごとに [1点]（とがらせる）か [2点]（とがりすぎは 切る）。
       はじめは 骨に 直角（top_dir が あれば その線で 切る）・さいごは 底の 線（end_dir）で 切る"""
    N = len(pts)
    ds = [_n(pts[i + 1] - pts[i]) for i in range(N - 1)]
    o0 = pts[0] + _left(ds[0]) * widths[0] * f
    if top_dir is not None:
        x0 = _isect(o0, ds[0], pts[0], top_dir)
        o0 = x0 if x0 is not None and np.linalg.norm(x0 - pts[0]) < 2.5 * widths[0] else o0
    out = [[o0]]
    for i in range(1, N - 1):
        oa = pts[i] + _left(ds[i - 1]) * widths[i] * f
        ob = pts[i] + _left(ds[i]) * widths[i] * f
        x = _isect(oa, ds[i - 1], ob, ds[i])
        if x is None or np.linalg.norm(x - pts[i]) > miter_lim * widths[i] * max(abs(f), .05):
            out.append([oa, ob])
        else:
            out.append([x])
    o = pts[-1] + _left(ds[-1]) * widths[-1] * f
    x = _isect(o, ds[-1], pts[-1], end_dir)
    out.append([x if x is not None and np.linalg.norm(x - pts[-1]) < 2.5 * widths[-1] else o])
    return out


def quads(pts, widths, fa, fb, end_dir, top_dir=None):
    """fa〜fb の 帯：骨ごとの 四角（と 関節の 切った 角の うめ）[(骨の 番号, 多角形)]"""
    A = offsets(pts, widths, fa, end_dir, top_dir)
    B = offsets(pts, widths, fb, end_dir, top_dir)
    out = []
    for i in range(len(pts) - 1):
        out.append((i, np.array([A[i][-1], A[i + 1][0], B[i + 1][0], B[i][-1]])))
        j = i + 1
        if j < len(pts) - 1 and (len(A[j]) == 2 or len(B[j]) == 2):
            out.append((j, np.array([A[j][0], A[j][-1], B[j][-1], B[j][0]])))
    return out


def draw_leg(canvas, pts, widths, pal, end_dir, sc, top_dir=None):
    """canvas（780 の sc 倍・BGR）へ 1本の 足：ふち → 骨ごとに 光の 当たる 半分を 明るく → かげの がわに こい線"""
    P = PAL[pal]
    pts = [np.asarray(p, float) for p in pts]
    to = lambda pg: np.round(np.asarray(pg) * sc * 16).astype(np.int32)

    def fill(pg, c):
        cv2.fillPoly(canvas, [to(pg)], (c[2], c[1], c[0]), lineType=cv2.LINE_8, shift=4)
    end_dir = _n(np.asarray(end_dir, float))
    td = None if top_dir is None else _n(np.asarray(top_dir, float))
    d0, d1 = _n(pts[1] - pts[0]), _n(pts[-1] - pts[-2])
    po = [pts[0] - d0 * (LINE_W if td is None else 0)] + pts[1:-1] + [pts[-1] + d1 * LINE_W / max(abs(float(d1 @ _left(end_dir))), .35)]
    for _, pg in quads(po, [w + 2 * LINE_W for w in widths], -.5, .5, end_dir, td):
        fill(pg, P['line'])
    lit = [float(_left(_n(pts[i + 1] - pts[i])) @ LIGHT) > 0 for i in range(len(pts) - 1)]
    for i, pg in quads(pts, widths, -.5, 0, end_dir, td):
        fill(pg, P['base'] if lit[min(i, len(lit) - 1)] else P['hi'])
    for i, pg in quads(pts, widths, 0, .5, end_dir, td):
        fill(pg, P['hi'] if lit[min(i, len(lit) - 1)] else P['base'])
    for i, pg in quads(pts, widths, -.5, -.36, end_dir, td):
        if lit[min(i, len(lit) - 1)]:
            fill(pg, P['shade'])
    for i, pg in quads(pts, widths, .36, .5, end_dir, td):
        if not lit[min(i, len(lit) - 1)]:
            fill(pg, P['shade'])


# ================= 体（もとの 絵を 骨で 動かす） =================
def norm_weights(masks, s1, s2=30.0):
    """マスク → どこでも 定まる 重さ（合計1・なめらか）"""
    G = [cv2.GaussianBlur(m.astype(np.float32), (0, 0), s1) + 1e-4 * cv2.GaussianBlur(m.astype(np.float32), (0, 0), s2) for m in masks]
    tot = np.maximum(sum(G), 1e-12)
    return [g / tot for g in G]


def soft(m):
    """マスク → ふちを 少し ぼかした すき通し"""
    return np.clip(cv2.GaussianBlur(m.astype(np.float32), (0, 0), .6) * 1.25, 0, 1) * (cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0)


class Rig:
    """S：flat/tengel_run.py の Src（元の絵・色・座標）。legs：もとの 足（ぬく所）・gold_legs：その中の 金の 足。bar：盾の ふちを 写す所"""

    def __init__(self, S, legs, gold_legs, bar):
        self.S = S
        self.s = s = S.s
        crop = S.crop.astype(np.float32)
        self.crop = crop
        poly = lambda pts: S.poly(pts)
        bgcol = ((S.H >= 85) & (S.H <= 112) & (S.Sa >= 95) & (S.V <= 140)).astype(np.uint8)    # 地の 紺
        self.bgcol = bgcol
        # 矢（動かない）
        ar = poly(ARROW) & (1 - bgcol)
        ar = cv2.dilate(ar, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))) & poly(ARROW)
        self.arrow = soft(ar)
        arm = ar.astype(bool)
        legd = cv2.dilate(gold_legs, np.ones((3, 3), np.uint8))
        # 体の かたち：BODY の 中は ぜんぶ・頭と 騎手と たてがみは 紺でない 所と その ふち（すきまは とじる）
        Uo = (poly(HEAD) | poly(JOCKEY) | poly(MANE[0]) | poly(MANE[1])).astype(np.uint8)
        Uo = cv2.dilate(Uo, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))) & (1 - poly(RIM))
        Ub = poly(BODY).astype(np.uint8)
        Up = Uo | Ub
        fg = Uo & (1 - bgcol) & (1 - arm.astype(np.uint8))
        sil = cv2.dilate(fg, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))) & Uo
        sil = cv2.morphologyEx(sil | Ub, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))) & Up
        n, lab = cv2.connectedComponents((1 - sil).astype(np.uint8), connectivity=4)
        outside = set(np.unique(lab[Up == 0]).tolist())
        holes = np.isin(lab, [i for i in range(1, n) if i not in outside]) & (sil == 0)
        sil = sil | holes.astype(np.uint8)
        # 体の 色：矢の 下は まわりの 体の 色・もとの 金の 足の つけねは こい紺（体の 下の かげ）
        bad = (arm | (legd > 0)) & (sil > 0)
        valid = (sil > 0) & ~bad
        num = cv2.GaussianBlur(crop * valid[..., None], (0, 0), 3)
        den = cv2.GaussianBlur(valid.astype(np.float32), (0, 0), 3)[..., None]
        body_rgb = np.where(arm[..., None], num / np.maximum(den, 1e-4), crop)
        body_rgb = np.where(((legd > 0) & (sil > 0))[..., None], np.array([34, 26, 12], np.float32), body_rgb)
        self.body_rgb = body_rgb
        self.body_alpha = soft(sil)
        # 骨の 重さ：騎手と たてがみは かけらごとに まるごと（ちぎれない）・頭は 首に そって なめらかに・手は 騎手と 頭の あいだ
        n, lab = cv2.connectedComponents(sil, connectivity=8)
        cnt = np.maximum(np.bincount(lab.ravel(), None, n), 1)
        frac = lambda m: np.bincount(lab.ravel(), m.ravel().astype(np.float64), n) / cnt
        upper = (S.yy < 108 * s)
        fj = frac(poly(JOCKEY) * upper)
        fm = frac(poly(MANE[0]) | poly(MANE[1]))
        fj[0] = fm[0] = 0
        jk = fj[lab] > .5
        jk = jk | ((fj[lab] > .05) & ~jk & (poly(JOCKEY) > 0) & upper)       # 騎手と 体が つながった かけら（もも）は 騎手の 形の 中だけ
        mn = (fm[lab] > .5) & ~jk
        hd = poly(HEAD) > 0
        hn = (poly(HANDS) > 0) & jk
        mb = ((sil > 0) & ~jk & ~mn & ~hd).astype(np.float32)
        mh = (hd & ~jk & ~mn).astype(np.float32)
        mj = (jk & ~hn).astype(np.float32)
        w_b, w_h, w_j = norm_weights([mb + .35 * mn, mh + .65 * mn + .5 * hn, mj + .5 * hn], 3.0)
        self.weights = (w_b, w_h, w_j)
        # 馬（体・足）を ぬいて 地の 紺で うめた絵（矢は のこす）
        allm = ((Up > 0) | (legs > 0)) & ~arm
        allm = cv2.dilate(allm.astype(np.uint8), np.ones((3, 3), np.uint8)) & (~arm).astype(np.uint8)
        self.removed = allm
        self.plate = self._plate(allm, bar)

    def _plate(self, u8, bar):
        S, cf = self.S, self.crop
        near = cv2.dilate(u8, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
        dark = cv2.erode(self.bgcol, np.ones((5, 5), np.uint8)) > 0               # 地の 紺（物の ふちの こい線から はなれた所）だけから ぼかして ひろげる
        valid = (dark & (near == 0)).astype(np.float32)
        fill = wgt = None
        for sig in (6, 14, 30):
            num = cv2.GaussianBlur(cf * valid[..., None], (0, 0), sig)
            den = cv2.GaussianBlur(valid, (0, 0), sig)[..., None]
            f = num / np.maximum(den, 1e-4)
            w = np.clip(den / 0.2, 0, 1)
            if fill is None:
                fill, wgt = f, w
            else:
                fill = fill * wgt + f * (1 - wgt)
                wgt = np.maximum(wgt, w)
        m = u8[..., None].astype(np.float32)
        plate = cf * (1 - m) + fill * m
        s = S.s
        x0, x1 = int(bar['x'][0] * s), int(bar['x'][1] * s) + 1                   # 頭の うしろの 盾の 金の ふち：下の所を 写して つなぐ
        ya, yb = int(bar['gap'][0] * s), int(bar['gap'][1] * s)
        src = cf[int(bar['src'][0] * s):int(bar['src'][1] * s), x0:x1]
        for y in range(ya, yb):
            plate[y, x0:x1] = np.where(u8[y, x0:x1, None] > 0, src[(y - ya) % src.shape[0]], plate[y, x0:x1])
        return plate


def _bil(img, X, Y):
    return cv2.remap(img, X.astype(np.float32), Y.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)


def inverse_lbs(weights, mats, PX, PY, iters=6):
    """描く 点（PX, PY）→ もとの 絵の 点：骨ごとに さがし はじめて、重さを つけた 動きの 逆を くり返し 解く。[(QX, QY, ずれ)]"""
    out = []
    Ms = np.stack(mats)
    for b in range(len(mats)):
        Mi = np.linalg.inv(mats[b])
        QX = Mi[0, 0] * PX + Mi[0, 1] * PY + Mi[0, 2]
        QY = Mi[1, 0] * PX + Mi[1, 1] * PY + Mi[1, 2]
        for it in range(iters + 1):
            Wt = np.stack([_bil(w, QX, QY) for w in weights], -1)
            Wt = Wt / np.maximum(Wt.sum(-1, keepdims=True), 1e-9)
            A = np.einsum('...b,bij->...ij', Wt, Ms)
            if it == iters:
                FX = A[..., 0, 0] * QX + A[..., 0, 1] * QY + A[..., 0, 2]
                FY = A[..., 1, 0] * QX + A[..., 1, 1] * QY + A[..., 1, 2]
                out.append((QX, QY, np.hypot(FX - PX, FY - PY)))
                break
            a, bb, c, d = A[..., 0, 0], A[..., 0, 1], A[..., 1, 0], A[..., 1, 1]
            det = a * d - bb * c
            rx, ry = PX - A[..., 0, 2], PY - A[..., 1, 2]
            QX = (d * rx - bb * ry) / det
            QY = (-c * rx + a * ry) / det
    return out


def render(rig, g):
    """位相 g の 馬（780×320・BGRA の float：色は すき通しで わる前）"""
    s = rig.s
    bp = body_pose(g)
    # 足：780 の SS 倍で 描いて ちぢめる（奥から）
    can = np.zeros((Hh * SS, W * SS, 3), np.float32)
    acc = np.zeros((Hh * SS, W * SS), np.float32)
    for L in LEG_ORDER:
        pts, sole, _ = leg_pts(L, g, bp['body'])
        c = LEG[L]
        col = np.zeros((Hh * SS, W * SS, 3), np.uint8)
        msk = np.zeros((Hh * SS, W * SS, 3), np.uint8)
        draw_leg(col, pts, list(c['w']), c['pal'], sole, SS, c.get('top'))
        draw_leg(msk, pts, list(c['w']), 'white', sole, SS, c.get('top'))
        a = msk[..., 0].astype(np.float32) / 255
        can = col.astype(np.float32) * a[..., None] + can * (1 - a[..., None])
        acc = a + acc * (1 - a)
    pm = cv2.resize(can * acc[..., None], (W, Hh), interpolation=cv2.INTER_AREA)
    al = cv2.resize(acc, (W, Hh), interpolation=cv2.INTER_AREA)
    # 体（足の 上）
    Hs, Ws = rig.crop.shape[:2]
    Sm = np.diag([s, s, 1.0])
    mats = [Sm @ bp[k] @ np.linalg.inv(Sm) for k in ('body', 'head', 'jockey')]
    ys, xs = np.nonzero(rig.body_alpha > 0)
    pad = int(12 * s)
    x0, x1 = max(0, xs.min() - pad), min(Ws, xs.max() + pad)
    y0, y1 = max(0, ys.min() - pad), min(Hs, ys.max() + pad)
    PY, PX = np.mgrid[y0:y1, x0:x1].astype(np.float64)
    best = np.zeros(PX.shape, np.float32)
    bx, by = np.zeros(PX.shape), np.zeros(PX.shape)
    for QX, QY, res in inverse_lbs(list(rig.weights), mats, PX, PY):
        a = _bil(rig.body_alpha, QX, QY) * (res < 0.35)
        better = a > best + 1e-6
        best = np.where(better, a, best)
        bx, by = np.where(better, QX, bx), np.where(better, QY, by)
    brgb = np.zeros((Hs, Ws, 3), np.float32)
    ba = np.zeros((Hs, Ws), np.float32)
    brgb[y0:y1, x0:x1] = _bil(rig.body_rgb, bx, by)
    ba[y0:y1, x0:x1] = best
    b_pm = cv2.resize(brgb * ba[..., None], (W, Hh), interpolation=cv2.INTER_AREA)
    b_a = cv2.resize(ba, (W, Hh), interpolation=cv2.INTER_AREA)
    pm = b_pm + pm * (1 - b_a[..., None])
    al = b_a + al * (1 - b_a)
    # 矢（動かない・いちばん 上）
    r_pm = cv2.resize(rig.crop * rig.arrow[..., None], (W, Hh), interpolation=cv2.INTER_AREA)
    r_a = cv2.resize(rig.arrow, (W, Hh), interpolation=cv2.INTER_AREA)
    pm = r_pm + pm * (1 - r_a[..., None])
    al = r_a + al * (1 - r_a)
    rgb = np.where(al[..., None] > 1e-4, pm / np.maximum(al, 1e-6)[..., None], 0)
    return np.dstack([np.clip(rgb, 0, 255), np.clip(al * 255, 0, 255)])


def plan():
    for i in range(FRAMES):
        g = i / FRAMES
        bp = body_pose(g)
        on = [L for L in LEG_ORDER if ((g - FOOTFALL[L]) % 1.0) < PATH[LEG[L]['kind']]['stance']]
        print(f'コマ{i:2d}  {g * PERIOD:.3f}秒  地面:{",".join(on) or "（宙）":<12} 体の上下 {bp["dy"]:+.1f}  かたむき {bp["th"]:+.1f}°  頭 {bp["hd"]:+.1f}°')


if __name__ == '__main__':
    import sys
    if '--plan' in sys.argv:
        plan()
