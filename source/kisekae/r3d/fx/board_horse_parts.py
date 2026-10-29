"""結果ボードカスタム 22「ボードを持つ馬」の 部品の 絵（第4.108版・まさちゃんの 指定）
   python3 fx/board_horse_parts.py <出力フォルダ> [--preview <見本.png>] [--measure]
   → bcx_hb_head.webp（頭と首）・bcx_hb_fore.webp（前足）・bcx_hb_hind.webp（後ろ足）・bcx_hb_tail.webp（しっぽ）・bcx_hb_eye.webp（目を とじた 所）
   もとは いちばん はじめの 頃の「馬が うしろから ボードを 持つ」絵（board_horse.py：その 絵は そのまま）。まさちゃん（2026/10/29）
   「赤丸の前脚不自然だから自然にして！青丸の頭と後ろ脚をプルプル振動させて！黄丸の尻尾あと少しだけ長くして、ランダムに振って！」で
     ・しっぽ：1.4倍の 長さ。頭と首・後ろ足・しっぽは 別の 絵（アプリで 別に 動かす：bcx.js の B.carry）
   まさちゃん（23:19・23:21）「前脚長すぎ、蹄が乗ってるくらいでいい！胴体の長さも2枚目の長さがベスト！」「蹄と少し足が見えるくらい！二枚目くらいの前脚の長さが理想！」で
     ・馬の 形・カメラ・ボードの ふちは board_horse.py の はじめの 絵と 同じ（頭と首の 高さ・後ろ足の 長さ・前足の 見える 長さ）。大きさだけ CSS の 1px＝3画素に
     ・前足：ふちの 上に 短い 足と ひづめ。ボードの 前に 出すのは 球節から 下（つなぎと ひづめ）だけ（はじめの 絵で ひづめの 下に 出て いた 管の 切れはしは 出さない）
   描き方：3Dの 馬（horse3d.py）を 2回 描く。① ぜんぶ（前足の 前腕から 下だけ 素材 7）→ 前足の 形（ほかの 所に かくれた 所は 入れない）・後ろ足
     ② 前足の 前腕から 下を 消した 馬 → 頭と首（前足の うしろに なる 胸や 首も ぜんぶ ある：頭だけ ふるえても すき間が 出ない）
   大きさ：CSS の 1px を 3画素（ボードの 横は 350px＝board_horse.py の 672画素）。絵の 場所は ボードの 左上（頭と首・前足）・左下（後ろ足・しっぽ）からの px で、bcx.js の HBX と 同じ
   （--measure：いまの 絵が ちょうど 入る 四角を 出す。ちがって いたら 止まる）。乱数の 種が 決まって いるので、何回 作っても 同じ"""
import sys, os, math, json, inspect, tempfile, shutil, atexit
import numpy as np, cv2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from style2d import *
import style2d as S2
import horse3d as Hm
from h3d import Scene

args = [a for a in sys.argv[1:] if not a.startswith('--')]
OUT = args[0] if args else '.'
PREVIEW = sys.argv[sys.argv.index('--preview') + 1] if '--preview' in sys.argv else None
MEASURE = '--measure' in sys.argv
os.makedirs(OUT, exist_ok=True)

D = 3                                    # CSS の 1px の 画素
K = D * 350 / 672                        # board_horse.py の 1画素 → この 絵の 画素（1.5625）
# 部品の 四角（CSS px。頭と首・前足・目＝ボードの 左上から／後ろ足・しっぽ＝ボードの 左下から）と 動きの 中心。bcx.js の HBX と 同じ
HBX = dict(head=[196, -142, 128, 172], fore=[186, -15, 76, 40], hind=[242, -30, 100, 124], tail=[314, -46, 33, 96], eye=[248, -121, 26, 26],
           headO=[272, 12], hindO=[292, -18], tailO=[327, -61], legL=[206, -1], legR=[244, -1], eyeC=[261, -108], muzzle=[204, -70], poll=[285, -132])
# board_horse.py の はじめの 絵と 同じ 形（しっぽだけ 1.4倍）
cfg = dict(theta=68, azim=42, elev=6, neck=-44, head=-30, fov=26, fl=[-48, 12, 88, -40], fr=[-40, 22, 92, -45], spread=2.2,
           hl=[-58, -112, -86, -60], hr=[-64, -118, -90, -62],
           body=['#C27237', '#9A5327'], mane=['#5A2E14', '#3E1E0C'], line='#4A2614', hoof='#3A2A22', light=[0.55, 0.75, -0.55],
           bands=[0.02, 0.72], box=[290, 30, 700, 880], board=[24, 696], board_h=440, top_pad=6, ss=2, head_scale=1.22, eye_k=0.10, mane_len=1.0, tail_len=1.4, seed=7, cut_r=0.10)
Hm.HEAD_SCALE = cfg['head_scale']
W, Hh = round(720 * K), round(900 * K)  # board_horse.py の 720×900
BX0 = cfg['board'][0] * K                # ボードの 左の はし（画素）
TMP = tempfile.mkdtemp(prefix='hbparts_')
atexit.register(shutil.rmtree, TMP, True)   # 下書き（1回 約140MB）は おわったら 消す
S2.TMP = TMP                             # 下書きは 自分の フォルダへ（ほかの 絵と いっしょに 作っても まざらない）

pose = dict(Hm.REAR)
pose.update(theta=cfg['theta'], neck_rot=cfg['neck'], head_ang=cfg['head'], fore_spread=cfg['spread'])
pose['fore'] = dict(L=cfg['fl'], R=cfg['fr'])
pose['hind'] = dict(L=cfg['hl'], R=cfg['hr'])

# ---- 前足（前腕から 下）の 形だけ 素材を かえる／消す（horse3d.build の 中の 行で 見分ける。horse3d.py は かえない） ----
_ls, _l0 = inspect.getsourcelines(Hm.build)


def _line(tag):
    for i, l in enumerate(_ls):
        if tag in l:
            return _l0 + i
    raise KeyError(tag)


F0, F1 = _line('# 前腕'), _line('# ---------- 後ろ足')


class Part:
    """sc の かわり：前足の 前腕から 下の 形を 素材 7 に する（mode='tag'）か 出さない（mode='drop'）"""
    def __init__(self, sc, mode):
        self.sc, self.mode = sc, mode

    def __getattr__(self, k):
        f = getattr(self.sc, k)
        if k not in ('ell', 'rcone', 'ccone', 'sph', 'rbox'):
            return f

        def g(*a, **kw):
            fr = sys._getframe(1)
            if fr.f_code is Hm.build.__code__ and F0 <= fr.f_lineno < F1:
                if self.mode == 'drop':
                    return None
                if kw.get('mat', 1) == 1:
                    kw['mat'] = 7
            return f(*a, **kw)
        return g


def render(eye, tgt, name, mode):
    sc0 = Scene()
    sc0.image(W, Hh, cfg['ss'])
    sc0.camera(np.asarray(eye, float), np.asarray(tgt, float), cfg['fov'])
    sc0.bounce(0)
    sc0.env((0.5, 0.5, 0.5), (0.4, 0.4, 0.4), (0.2, 0.2, 0.2))
    sc0.light((0.5, 0.8, 0.6), (2.0, 2.0, 2.0), 10, 1)
    for mid in (1, 7):
        sc0.mat(mid, 1, (0.6, 0.6, 0.6), 0.6)
    sc0.mat(5, 1, (0.02, 0.02, 0.02), 0.1)
    sc0.mat(6, 1, (0.3, 0.3, 0.3), 0.6)
    S = Hm.build(Part(sc0, mode), pose, mats=dict(body=1, neck=1, hoof=6, eye=5, head=1))
    R = sc0.render(os.path.join(TMP, name))
    ts = np.linspace(0, 1, 40)
    P = lambda pts: sc0.project(np.asarray(pts, float))[0]
    R['crest'] = P(np.c_[Hm.bez(S['crest'], ts), np.zeros(len(ts))])
    R['throat'] = P(np.c_[Hm.bez(S['throat'], ts), np.zeros(len(ts))])
    R['poll'] = P([Hm.v3(S['poll'])])[0]
    R['muzzle'] = P([Hm.head_pt(S, 0.56, -0.03)])[0]
    R['tail'] = P([Hm.v3(p) for p in S['tail_pts']])
    e0, e1 = S['eyes']
    R['eye'] = P([e0 if np.dot(e0 - tgt, np.asarray(eye, float) - tgt) > np.dot(e1 - tgt, np.asarray(eye, float) - tgt) else e1])[0]
    R['S'] = S
    R['scene'] = sc0
    return R


def fore_segs(S):
    sp = cfg['spread']
    out = {}
    for k in ('FL', 'FR'):
        F = S[k]
        zl = 0.155 * F['z']
        zk = zl * 0.93 * (1 + (sp - 1) * 0.55)
        zf = zl * 0.9 * (1 + (sp - 1) * 0.9)
        out[k] = dict(el=np.array([*F['el'], zl]), kn=np.array([*F['kn'], zk]), ft=np.array([*F['ft'], zf]), co=np.array([*F['co'], zf]), hf=np.array([*F['hf'], zf]))
    return out


# ---- カメラと ボードの ふち：board_horse.py と 同じ（馬が box に 入る・ボードの 上の ふちは 低い ほうの 球節の 少し 下・下の ふちは その 440画素 下） ----
SK = Hm.skeleton(pose)
segs = fore_segs(SK)
eye, tgt = frame_horse(pose, tuple(v * K for v in cfg['box']), W, Hh, facing='left', azim=cfg['azim'], elev=cfg['elev'], fov=cfg['fov'])
sc_ = Scene(); sc_.image(W, Hh, 1); sc_.camera(eye, tgt, cfg['fov'])
BY0 = max(sc_.project(np.array([segs[k]['ft']]))[0][0][1] for k in segs) + cfg['top_pad'] * K   # ボードの 上の ふち（画素）
BY1 = BY0 + cfg['board_h'] * K                                                                   # ボードの 下の ふち（画素）
shift = 0.0
RF = render(eye, tgt, 'full', 'tag')     # ぜんぶ（前足の 前腕から 下＝素材 7）
RB = render(eye, tgt, 'body', 'drop')    # 前足の 前腕から 下なし


def paint(R, eye_open=True):
    A = R['a']
    rgb = cel(R, cfg['body'][0], cfg['body'][1], light=tuple(cfg['light']), bands=tuple(cfg['bands']), eye='#1A1008', hoof=cfg['hoof'])
    if eye_open:
        rgb = draw_eye(rgb, R, '#1A1008', k=cfg['eye_k'])
    ln = edges(R, width=3) * np.clip(A, 0, 1)
    col = over(np.zeros((Hh, W, 3), np.float32), rgb, A)
    col = over(col, hexc(cfg['line']), ln * 0.9)
    return col, A.copy(), rgb


# ---- たてがみ・前髪・しっぽ（board_horse.py と 同じ 作り方。大きさは 画素の 数に あわせる・しっぽは tail_len 倍） ----
def hair(R):
    rng = np.random.default_rng(cfg['seed'])
    A = R['a']
    ys = np.nonzero(A > 0.5)[0]
    u = (ys.max() - ys.min()) / 872.0                            # board_horse.py の 馬（高さ 872画素）と 同じ 見た目の 太さ・長さに
    crest, throat = np.asarray(R['crest']), np.asarray(R['throat'])
    pa, pb, ta, tb = [], [], [], []
    n = len(crest)
    for i in range(4, n - 6, 2):
        c = crest[i]
        v = c - throat[i]
        v = v / (np.linalg.norm(v) + 1e-9)
        p = c.copy()
        for _ in range(400):
            q = p + v
            xi, yi = int(round(q[0])), int(round(q[1]))
            if not (0 <= xi < W and 0 <= yi < Hh) or A[yi, xi] < 0.5:
                break
            p = q
        tt = i / n
        L = (34 + 20 * math.sin(tt * math.pi)) * cfg['mane_len'] * u
        ang = math.atan2(v[1], v[0])
        ang = ang + (math.pi / 2 - ang) * 0.78
        pts = flow(p - v * 10 * u, ang, L, 9, wind=0.0, rng=rng, wave=0.5, phase=i)
        (pa if (i // 2) % 2 == 0 else pb).append(lock_poly(pts, 19 * u, 1.0))
    pp = np.asarray(R['poll'], float)
    mz = np.asarray(R['muzzle'], float)
    fd = (mz - pp) / (np.linalg.norm(mz - pp) + 1e-9)
    es = np.array([fd[1], -fd[0]])
    if np.dot(es, np.asarray(R['eye'], float) - pp) > 0:
        es = -es
    for k in range(2):
        a0 = math.atan2(fd[1], fd[0]) + 0.55 * math.copysign(1, fd[0] * es[1] - fd[1] * es[0]) + (k - 0.5) * 0.25
        pts = flow(pp + es * 4 * u + rng.normal(0, 1.0, 2) * u, a0, 20 * u, 6, wind=0.0)
        (pa if k == 0 else pb).append(lock_poly(pts, 10 * u, 1.0))
    tl = np.asarray(R['tail'], float)
    base_ang = math.atan2(*(tl[-1] - tl[0])[::-1])
    t0 = tl[0] + (tl[1] - tl[0]) * 0.3
    for k in range(5):
        a0 = base_ang + (k - 2) * 0.14
        pts = flow(t0, a0, (120 + k * 10) * 0.9 * cfg['tail_len'] * u, 12, wind=0.1, wind_ang=math.pi / 2, rng=rng, wave=0.8, phase=k)
        (ta if k % 2 == 0 else tb).append(lock_poly(pts, 30 * u, 1.5))

    def lay(PA, PB):
        m = poly_aa((Hh, W), PA)
        s = poly_aa((Hh, W), PB)
        c1, c2 = hexc(cfg['mane'][0]), hexc(cfg['mane'][1])
        rgb = c1 * m[..., None] + c2 * (s * (1 - m))[..., None]
        a = np.clip(m + s, 0, 1)
        rgb = np.where(a[..., None] > 0, rgb / np.maximum(a, 1e-4)[..., None], 0)
        hl = cv2.morphologyEx((a > .5).astype(np.float32), cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8))
        hl = cv2.GaussianBlur(hl, (3, 3), .6)
        c = over(rgb * a[..., None], hexc(cfg['line']), hl * 0.85)
        a = np.clip(a + hl * (1 - a), 0, 1)
        return np.where(a[..., None] > 1e-4, c / np.maximum(a, 1e-4)[..., None], 0), a
    return lay(pa, pb), lay(ta, tb), t0


def ov(c0, a0, c1, a1):
    """c1 を c0 の 前に 重ねる（色は 0〜1・アルファ べつ）"""
    a = a1 + a0 * (1 - a1)
    c = c1 * a1[..., None] + c0 * a0[..., None] * (1 - a1[..., None])
    return np.where(a[..., None] > 1e-4, c / np.maximum(a, 1e-4)[..., None], 0), a


(mane_rgb, mane_a), (tail_rgb, tail_a), tail0 = hair(RB)
colF, aF, _ = paint(RF)
colB, aB, rgbB = paint(RB)
yy = np.mgrid[0:Hh, 0:W][0]

# ---- 前足（第4.108版・まさちゃん 23:56「前脚不自然だから自然に見えるように直して！」）：2Dで 描く（3Dの 馬と 同じ 色・線）。
#      管は ボードの うしろ（見えない）→ 球節が ボードの 上の ふちに のる（ふちの 上に 少し ふくらむ）→ 短い つなぎが 前へ 下がる →
#      ひづめ（下が 広い 壁・こい 色の つま先・小さな つや・つなぎとの さかいの 線）が ふちの 前に かかる。ひづめの 下と ふちの 所に うすい 影。
#      白い ふち（ほかの 部品の .bco と 同じ 見え方）は 絵に 入れる（影に 白い ふちが つかない ように）。2本は 少し ちがう 向き（つま先が 内がわ）
LEG = dict(L=dict(at=HBX['legL'], rot=-6.0, sc=1.0), R=dict(at=HBX['legR'], rot=5.0, sc=1.06))
LSS = 4                                                   # 4倍で 描いて 縮める（なめらかな ふち）


def leg_shapes():
    """前足 1本の 形（球節の まん中が 0,0・CSS px・y は 下が ＋）"""
    bul = [(7.2 * math.cos(t), -1.6 + 5.6 * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 48, endpoint=False)]
    pas = [(-5.4, -0.6), (5.2, -0.2), (3.4, 8.9), (-6.8, 8.5)]
    hoof = [(-7.5, 8.0), (-2.2, 7.4), (3.5, 8.5), (4.4, 12.0), (4.9, 15.6), (4.2, 16.9), (2.8, 17.5), (-2.4, 17.9), (-7.8, 17.6), (-9.6, 16.9), (-10.2, 15.8), (-9.0, 12.0)]
    toe = [(-9.4, 13.4), (4.7, 13.9), (4.9, 15.6), (4.2, 16.9), (2.8, 17.5), (-2.4, 17.9), (-7.8, 17.6), (-9.6, 16.9), (-10.2, 15.8)]
    band = [(2.6, -0.3), (5.2, -0.2), (3.4, 8.9), (1.2, 8.8)]                       # つなぎの うしろ側の かげ
    cor = [(-7.6, 8.4), (-4.6, 9.3), (-1.6, 9.7), (1.4, 9.4), (3.5, 8.7)]           # つなぎと ひづめの さかい
    hil = [(-6.6, 10.4), (-7.4, 12.6), (-8.0, 15.0)]                                # ひづめの つや
    sole = (-2.6, 18.2)
    return bul, pas, hoof, toe, band, cor, hil, sole


def draw_legs():
    """前足 2本 → 画面 ぜんたいの (色, アルファ)。ひづめの 下の 影の 中心（CSS）も 返す"""
    bul, pas, hoof, toe, band, cor, hil, sole = leg_shapes()
    col = np.zeros((Hh, W, 3), np.float32); al = np.zeros((Hh, W), np.float32)
    soles = {}
    for key in ('L', 'R'):
        L = LEG[key]; cx, cy = L['at']; a = math.radians(L['rot']); k = L['sc']
        x0, y0, bw, bh = cx - 24, cy - 16, 48, 44                                   # この 足を 描く 四角（CSS）
        Wl, Hl = int(bw * D * LSS), int(bh * D * LSS)
        def tp(pt):
            x, y = pt[0] * k, pt[1] * k
            return cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a)
        def poly(pts):
            q = np.array([[((tp(p)[0] - x0) * D * LSS) * 16, ((tp(p)[1] - y0) * D * LSS) * 16] for p in pts], np.int64)
            return q.astype(np.int32)
        def mask(pts_list):
            m = np.zeros((Hl, Wl), np.uint8)
            for pts in pts_list:
                cv2.fillPoly(m, [poly(pts)], 255, cv2.LINE_AA, shift=4)
            return m.astype(np.float32) / 255
        def line(pts, w):
            m = np.zeros((Hl, Wl), np.uint8)
            cv2.polylines(m, [poly(pts)], False, 255, max(1, int(round(w * D * LSS))), cv2.LINE_AA, shift=4)
            return m.astype(np.float32) / 255
        mB, mP, mH, mT, mN = mask([bul]), mask([pas]), mask([hoof]), mask([toe]), mask([band])
        body = np.clip(mB + mP, 0, 1) * (1 - mH)
        sil = np.clip(mB + mP + mH, 0, 1)
        r_out = int(round(0.55 * D * LSS)); r_in = int(round(0.6 * D * LSS))
        ker = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
        silb = (sil > 0.5).astype(np.uint8)
        outer = cv2.dilate(silb, ker(r_out)).astype(np.float32)
        ring = np.clip(outer - cv2.erode(silb, ker(r_in)).astype(np.float32), 0, 1)
        white = np.clip(cv2.dilate(silb, ker(int(round(1.45 * D * LSS)))).astype(np.float32) - outer, 0, 1)
        c = np.zeros((Hl, Wl, 3), np.float32)
        c[:] = hexc(cfg['body'][0])
        c = over(c, hexc(cfg['body'][1]), mN * body)
        c = over(c, hexc(cfg['hoof']), mH)
        c = over(c, hexc('#241812'), mT * mH * 0.55)
        c = over(c, hexc('#8C7262'), line(hil, 0.9) * mH * 0.55)
        c = over(c, hexc(cfg['line']), line(cor, 0.85) * 0.9)
        c = over(c, hexc(cfg['line']), ring * 0.95)
        c = over(c, np.ones(3, np.float32), white * 0.9)
        A = np.clip(np.maximum(outer, white * 0.9), 0, 1)
        # ひづめの 下と ふちの 所の うすい 影（足の うしろ）
        sx, sy = tp(sole)
        yy_, xx_ = np.mgrid[0:Hl, 0:Wl].astype(np.float32)
        def blob(ex_, ey_, rx, ry, v):
            px, py = (ex_ - x0) * D * LSS, (ey_ - y0) * D * LSS
            return np.clip(v * np.exp(-(((xx_ - px) / (rx * D * LSS)) ** 2 + ((yy_ - py) / (ry * D * LSS)) ** 2) * 2.2), 0, 1)
        sh = np.clip(blob(sx, sy + 0.6, 9.0, 2.6, 0.42) + blob(cx + 0.6, cy + 4.2, 9.5, 2.4, 0.30), 0, 0.5)
        sh = sh * (1 - A)
        C = c * A[..., None]
        C = C + hexc('#28140A') * sh[..., None]
        At = np.clip(A + sh, 0, 1)
        C = np.where(At[..., None] > 1e-4, C / np.maximum(At, 1e-4)[..., None], 0)
        # 4倍 → 1倍・画面の 中へ
        C1 = cv2.resize(C * At[..., None], (int(bw * D), int(bh * D)), interpolation=cv2.INTER_AREA)
        A1 = cv2.resize(At, (int(bw * D), int(bh * D)), interpolation=cv2.INTER_AREA)
        px0, py0 = int(round(BX0 + x0 * D)), int(round(BY0 + y0 * D))
        dst = (slice(py0, py0 + A1.shape[0]), slice(px0, px0 + A1.shape[1]))
        prem = col[dst] * al[dst][..., None]
        prem = C1 + prem * (1 - A1[..., None])
        al[dst] = A1 + al[dst] * (1 - A1)
        col[dst] = np.where(al[dst][..., None] > 1e-4, prem / np.maximum(al[dst], 1e-4)[..., None], 0)
        soles[key] = (round(sx, 1), round(sy, 1))
    return col, al, soles


foreC, foreA, SOLES = draw_legs()

# ---- 部品 ----
headC, headA = ov(colB, aB, mane_rgb, mane_a)
# 目を とじた 所（頭と首の 絵の 上に 一瞬 重ねる）：目の まわりの 毛の 色で ぬって、まぶたの 線
ex, ey = RB['eye']
r = max(1.6, np.linalg.norm(np.asarray(RB['muzzle']) - np.asarray(RB['poll'])) * cfg['eye_k'])
ring = (np.hypot(*(np.mgrid[0:Hh, 0:W][::-1] - np.array([ex, ey])[:, None, None])) - r * 1.9)
ringM = (np.abs(ring) < r * 0.35) & (RB['m'] != 5) & (aB > 0.9)
fur = np.median(rgbB[ringM], axis=0) if ringM.any() else hexc(cfg['body'][0])
eyeC = headC.copy()
lid = np.zeros((Hh * 4, W * 4), np.uint8)
u_ = np.asarray(RB['muzzle']) - np.asarray(RB['poll']); u_ = u_ / (np.linalg.norm(u_) + 1e-9)
ang = math.degrees(math.atan2(u_[1], u_[0])) - 90
cv2.ellipse(lid, (int(ex * 64), int(ey * 64)), (int(r * 1.25 * 64), int(r * 0.95 * 64)), ang, 0, 360, 255, -1, cv2.LINE_AA, shift=4)
lidm = cv2.resize(lid, (W, Hh), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
eyeC = eyeC * (1 - lidm[..., None]) + fur * lidm[..., None]
arc = np.zeros((Hh * 4, W * 4), np.uint8)
cv2.ellipse(arc, (int(ex * 64), int((ey - r * 0.15) * 64)), (int(r * 1.05 * 64), int(r * 0.55 * 64)), ang, 20, 160, 255, int(max(2, D * 0.75) * 4), cv2.LINE_AA, shift=4)
arcm = cv2.resize(arc, (W, Hh), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
eyeC = eyeC * (1 - arcm[..., None]) + hexc('#1A1008') * arcm[..., None]
eyeA = np.clip(headA + lidm + arcm, 0, 1)

LAYERS = dict(head=(headC, headA, 'top'), fore=(foreC, foreA, 'top'), hind=(colF, aF * (yy > BY1 - 40 * D), 'bot'), tail=(tail_rgb, tail_a, 'bot'), eye=(eyeC, eyeA, 'top'))


def box_px(b, ref):
    x, y, w, h = b
    py0 = BY0 if ref == 'top' else BY1
    return int(round(BX0 + x * D)), int(round(py0 + y * D)), int(round(w * D)), int(round(h * D))


def tight(a, ref, thr=0.02, clip=None):
    ys, xs = np.nonzero(a > thr)
    py0 = BY0 if ref == 'top' else BY1
    x0, x1 = (xs.min() - BX0) / D, (xs.max() + 1 - BX0) / D
    y0, y1 = (ys.min() - py0) / D, (ys.max() + 1 - py0) / D
    return [math.floor(x0) - 2, math.floor(y0) - 2, math.ceil(x1 - x0) + 4, math.ceil(y1 - y0) + 4]


# 頭と首は ボードの 上の ふちの 下 26px まで（ボードの 角の 丸み 22px より 下）・後ろ足は 下の ふちの 上 30px から・しっぽは 下の ふちの 上 46px から
CUT = dict(head=('y1', 26), hind=('y0', -30), tail=('y0', -46))
lay = {}
for k, (c, a, ref) in LAYERS.items():
    a = a.copy()
    if k in CUT:
        side, v = CUT[k]
        py = (BY0 if ref == 'top' else BY1) + v * D
        a = a * ((yy < py) if side == 'y1' else (yy >= py))
    if k == 'eye':                                       # 目の まわりだけ
        a = a * (np.hypot(*(np.mgrid[0:Hh, 0:W][::-1] - np.array([ex, ey])[:, None, None])) < r * 1.6)
    lay[k] = (c, a, ref)

if PREVIEW:
    # 見本：しっぽ → 後ろ足 → 頭と首 → ボード（ふつうの 見出しの 帯と 字の 所）→ 前足
    bg = grad_v(Hh, W, [(0, '#2A2F55'), (1, '#1B1E3A')])
    img = bg.copy()
    for k in ('tail', 'hind', 'head'):
        c, a, ref = lay[k]
        img = over(img, c, a)
    yyf, xxf = np.mgrid[0:Hh, 0:W].astype(np.float32)

    def rrect(x0, y0, x1, y1, rr):
        cx = np.clip(xxf, x0 + rr, x1 - rr); cy = np.clip(yyf, y0 + rr, y1 - rr)
        return np.clip(rr - np.hypot(xxf - cx, yyf - cy) + 0.5, 0, 1)
    img = over(img, hexc('#EEF1F6'), rrect(BX0, BY0, BX0 + 350 * D, BY1, 22 * D))
    img = over(img, hexc('#14214A'), rrect(BX0 + 8 * D, BY0 + 8 * D, BX0 + 342 * D, BY0 + 98 * D, 14 * D))
    tz = np.zeros((Hh, W), np.float32)
    tz[int(BY0 + 21 * D):int(BY0 + 58 * D), int(BX0 + 96 * D):int(BX0 + 254 * D)] = 0.35
    img = over(img, hexc('#FF3030'), tz)
    c, a, ref = lay['fore']
    img = over(img, c, a)
    save_png(np.clip(img, 0, 1), PREVIEW)
if MEASURE:
    ys_, xs_ = np.nonzero(aF > 0.5)
    print('馬の 四角（ボードの 左上から CSS px）:', round((xs_.min() - BX0) / D, 1), round((ys_.min() - BY0) / D, 1), round((xs_.max() - BX0) / D, 1), round((ys_.max() - BY0) / D, 1), ' 下の ふちから:', round((ys_.max() - BY1) / D, 1))
    got = {k: tight(a, ref) for k, (c, a, ref) in lay.items()}
    print('ちょうどの 四角（CSS px）:', json.dumps(got))
    print('目の 中心（ボードの 左上から）:', round((ex - BX0) / D, 1), round((ey - BY0) / D, 1), ' 目の 大きさ:', round(r / D, 2), ' 目の 向き:', round(math.degrees(math.atan2(u_[1], u_[0])) - 90, 1),
          ' しっぽの 根もと（左下から）:', round((tail0[0] - BX0) / D, 1), round((tail0[1] - BY1) / D, 1))
    print('鼻先:', [round((v - o) / D, 1) for v, o in zip(RB['muzzle'], (BX0, BY0))], ' 頭の てっぺん（poll）:', [round((v - o) / D, 1) for v, o in zip(RB['poll'], (BX0, BY0))], ' ひづめの 下:', SOLES)
    shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(0)

from PIL import Image
bad = []
for k, (c, a, ref) in lay.items():
    x, y, w, h = box_px(HBX[k], ref)
    # 四角の 外に 見える 所が ない こと（切った ふちは のぞく）。四角が 絵の 外に 出る 所は すき通しで うめる
    outside = a.copy()
    outside[max(0, y):max(0, y + h), max(0, x):max(0, x + w)] = 0
    if outside.max() > 0.04:
        bad.append(f'{k}：四角の 外に 絵が ある（{outside.max():.2f}）')
    rgba = np.zeros((h, w, 4), np.float32)
    sy0, sx0, sy1, sx1 = max(0, y), max(0, x), min(Hh, y + h), min(W, x + w)
    rgba[sy0 - y:sy1 - y, sx0 - x:sx1 - x] = np.dstack([np.clip(c[sy0:sy1, sx0:sx1], 0, 1), np.clip(a[sy0:sy1, sx0:sx1], 0, 1)])
    u8 = (rgba * 255 + .5).astype(np.uint8)
    Image.fromarray(u8, 'RGBA').save(os.path.join(OUT, f'bcx_hb_{k}.webp'), 'WEBP', quality=86, method=6)
    print(f'bcx_hb_{k}.webp', f'{w}×{h}', f'{os.path.getsize(os.path.join(OUT, f"bcx_hb_{k}.webp")) / 1e3:.1f}KB', flush=True)

shutil.rmtree(TMP, ignore_errors=True)
if bad:
    print('⚠️', '・'.join(bad))
    sys.exit(1)
