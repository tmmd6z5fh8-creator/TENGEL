"""結果ボードカスタム 22「ボードを持つ馬」の 部品の 絵（第4.108版〜第4.112版・まさちゃんの 指定）
   python3 fx/board_horse_parts.py <出力フォルダ> [--preview <見本.png>] [--measure]
   → bcx_hb_head.webp（頭と首）・bcx_hb_fore.webp（前足）・bcx_hb_hind.webp（後ろ足）・bcx_hb_tail.webp（しっぽ）・bcx_hb_eye.webp（目を とじた 所）
   もとは いちばん はじめの 頃の「馬が うしろから ボードを 持つ」絵（board_horse.py：その 絵は そのまま）。まさちゃん（2026/10/29）
   「赤丸の前脚不自然だから自然にして！青丸の頭と後ろ脚をプルプル振動させて！黄丸の尻尾あと少しだけ長くして、ランダムに振って！」で
     ・しっぽ：1.4倍の 長さ。頭と首・後ろ足・しっぽは 別の 絵（アプリで 別に 動かす：bcx.js の B.carry）
   まさちゃん（23:19・23:21）「前脚長すぎ、蹄が乗ってるくらいでいい！胴体の長さも2枚目の長さがベスト！」「蹄と少し足が見えるくらい！二枚目くらいの前脚の長さが理想！」で
     ・馬の 形・カメラ・ボードの ふちは board_horse.py の はじめの 絵と 同じ（頭と首の 高さ・後ろ足の 長さ・前足の 見える 長さ）。大きさだけ CSS の 1px＝3画素に
     ・前足：ふちの 上に 短い 足と ひづめ（見える 長さは はじめの 絵と 同じ くらい）
   まさちゃん（第4.109版・01:18）「どう見てもおかしいよ… 2枚目の写真のようにして！ 赤は消すところ！ 茶色は、脚の形のイメージ！ 自然にして！」・
   （01:21）「茶色の脚イメージは黄丸のところね！」・（02:22）の 直しで（23:56 の 2Dの 前足は やめた）
     ・前足は はじめの 絵の 3Dの 足に もどす（丸い 上の はしは 球節・ひづめは こい 色の 輪・場所と 向きと 大きさも 同じ）
     ・ボードの ふちより 上：足 ぜんぶ ＋ うしろ側の くさび（足の うしろの ふちから ななめに ボードの ふちへ：管が ボードの うしろから 上がって くる 形。
       右の 足は 胸の 前まで つづけて 胸と すき間なく つなぐ）。ボードの うしろへ 入る 所は 白い 輪の 上で 切る（線も 白い ふちも つけない。第4.112版 10:38 から 輪の いちばん 上）
     ・ふちより 下：ひづめと その 上の つなぎ だけ（ひづめの うしろ・下に 出て いた 切れはし＝赤は 消す）。つなぎの うしろの ふちは
       ひづめの うしろの 上の かどから ななめに ボードの ふちへ（02:22「左脚は、90°に切れてておかしい」）。切り口に 線
   まさちゃん（第4.110版・07:45）「赤線に合わせて」で
     ・左の 足：つなぎの うしろの ふちは ひづめの うしろの 上の かど → 関節の 線が ボードの ふちに とどく 所 の まっすぐな 線（そこまで 足の 色で うめる）
     ・右の 足：関節の 線は ひづめの うしろの 上の かど → くさびの 上の はし の まっすぐな 線。その 右（ボードの ふちまで）は ぜんぶ くさびの 色
     ・（08:02）「あと前脚の濃い茶色ほんの少しだけ薄くして！」：くさびの 色を 少し 明るく（#9A5327 → #A85E2D。ひづめは そのまま）
   まさちゃん（第4.111版・08:29）「白のボードの縁に馬の前脚が入ってるから、入らないようにして！ あと濃い茶色もっと薄く、影に見えるくらいにして！」で
     ・前足は 1本ずつ 上へ ずらして、ひづめの 下を ボードの 白い 輪（的中 3px）の 上に のせる（ボードの 白い ふちには なにも かからない。ハズレ（輪 1.5px）は
       bcx.js で 1.5px 下げる）。頭と首・後ろ足は そのまま。足の 形（第4.110版の 赤線・関節の 線）は 同じで、くさび（足の むこう側の かげ）は 下を ボードの 上の
       ふちまで のばし、下の はばは ひづめの うしろから 左 6px・右 14px。色は かげに 見える くらい 明るく（関節の 線の 近く #B06430 → ななめの 方 #BA6C34）。
       ひづめの 下に ごく うすい 影（ボードの ふちより 上だけ）
     ・くさびは 足の 下に しいて 足の うしろの 線（関節の 線）を のこす・色は 馬の かげの 色（02:22「右脚は、関節の線がないから分かりにくい」）
     ・白い ふちと 影（ほかの 部品の .bco と 同じ 見え方）は 絵に 入れる（胸の 前・切り口には つけない・影は ボードの 前に 出る 所だけ）
     ・見出しの 字（どの テーマでも）と 3px 以上 あける ため、馬を ボードに 対して 3.1px 上げた（top_pad 6 → 12）
   まさちゃん（第4.112版・09:50）「俺の表現が悪いね。蹄で持つんじゃなくて、関節で挟んでるようにして」（08:59「ボードから前脚浮いてる、直して」の 言い直し）で
     ・第4.110版の 形に もどす：関節（球節）で ボードを はさむ＝管は ボードの うしろ・球節が ボードの 上の ふちに のり・つなぎと ひづめは ボードの 前の 面に おしつく
       （ひづめは ボードの 白い 輪と 見出しの 上の 帯に かかる：ふちから 21.5px まで）。第4.111版の 上へ ずらす 形と 09:35 の 平らな 底は やめた。
       くさびの 色は 第4.111版の かげの 色の まま（関節の 線の 近く #B06430 → ななめの 方 #BA6C34）。
       おしつけて いる 感じの ため、ボードの 面に 出る つなぎと ひづめの まわりに ごく うすい 密着の 影を 足した（.bco と 同じ 影の ほかに）
   まさちゃん（10:30・10:38）「どう見てもボードに腕の模様が被っているのが直ってないよ」「ボードに脚の線が被ってるか、被ってないかのちがい」で
     ・足が ボードの うしろへ 入る 所の 切り目を、白い 輪の まん中（ふちの 1.5px 上）から 白い 輪の いちばん 上（的中・大的中 3px）へ（CUT）。
       白い 輪の 上に 出るのは つなぎと ひづめ だけ：足の うしろの 線・くさびの 下・それらの 白い ふちと 影は 白い 輪に かからない。
       赤線の 上の はし（Pb）も 白い 輪の 上で 足の うしろの ふちに つく。ハズレ（輪 1.5px）は bcx.js で 前足を 1.5px 下げて、切り目を 輪の 上に 合わせる
   描き方：3Dの 馬（horse3d.py）を 2回 描く。① ぜんぶ（前足の 前腕から 下だけ 素材 7）→ 前足（上の とおり）・後ろ足
     ② 前足の 前腕から 下を 消した 馬 → 頭と首（前足の うしろに なる 胸や 首も ぜんぶ ある：頭だけ ふるえても すき間が 出ない）。ぜんぶで 約27KB・1〜2分
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
HBX = dict(head=[196, -145, 128, 175], fore=[136, -34, 107, 63], hind=[242, -30, 100, 120], tail=[314, -46, 33, 90], eye=[248, -124, 26, 26],
           headO=[272, 9], hindO=[292, -21], tailO=[327, -64], eyeC=[261, -111], muzzle=[211, -67], poll=[267, -116])
# board_horse.py の はじめの 絵と 同じ 形（しっぽだけ 1.4倍）
cfg = dict(theta=68, azim=42, elev=6, neck=-44, head=-30, fov=26, fl=[-48, 12, 88, -40], fr=[-40, 22, 92, -45], spread=2.2,
           hl=[-58, -112, -86, -60], hr=[-64, -118, -90, -62],
           body=['#C27237', '#9A5327'], mane=['#5A2E14', '#3E1E0C'], line='#4A2614', hoof='#3A2A22', light=[0.55, 0.75, -0.55],
           bands=[0.02, 0.72], box=[290, 30, 700, 880], board=[24, 696], board_h=440, top_pad=12, ss=2, head_scale=1.22, eye_k=0.10, mane_len=1.0, tail_len=1.4, seed=7, cut_r=0.10)
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

# ---- 前足（第4.109版・まさちゃん 01:18「どう見てもおかしいよ… 2枚目の写真のようにして！ 赤は消すところ！ 茶色は、脚の形のイメージ！ 自然にして！」・
#      01:21「茶色の脚イメージは黄丸のところね！」・02:22「左脚は、90°に切れてておかしい」「右脚は、関節の線がないから分かりにくい」）：
#      はじめの 絵（board_horse.py）の 前足に もどす（3Dの 足：丸い 上の はしは 球節・ひづめは こい 色の 輪。場所・向き・大きさも はじめの 絵と 同じ）。
#      ・ボードの 上の ふちより 上：足 ぜんぶ ＋ うしろ側の くさび（足の むこう側：馬の かげの 色。足の うしろの ふちから ななめに ボードの 上の ふちへ ＝
#        管が ボードの うしろから 上がって きて ふちの 上で 曲がる 形。左の 足は 小さな 三角・右の 足は 足の うしろの 線と 胸の 前の あいだの 大きな 三角）。
#        くさびは 足の 下に しく ので 足の うしろの 線（関節の 線）は のこる
#      ・ふちより 下：ひづめと その すぐ 上の つなぎ だけ（はじめの 絵で ひづめの うしろ・下に 出て いた 切れはしは 消す）。つなぎの うしろの ふちは
#        ひづめの うしろの 上の かどから ななめに ボードの ふちへ（たての 切り口・90° の かどを 作らない。第4.110版：まさちゃんの 赤線＝関節の 線の 下の はしまで まっすぐ）
#      ・第4.110版（07:45「赤線に合わせて」）：右の 足の 関節の 線は ひづめの うしろの 上の かど → くさびの 上の はし の まっすぐな 線。その 右は くさびの 色を 足の 上に ぬる
#      ・第4.112版（09:50「俺の表現が悪いね。蹄で持つんじゃなくて、関節で挟んでるようにして」）：この 第4.110版の 形（関節で ボードを はさむ：球節が ボードの ふちに のり、
#        つなぎと ひづめは ボードの 前の 面に おしつく）に もどした。第4.111版の 上へ ずらす 形と 09:35 の 平らな 底は やめた。くさびの 色だけ 第4.111版の かげの 色（WEDGE_COL）。
#        おしつけて いる 感じの ため、ボードの 面に 出る つなぎと ひづめの まわりに ごく うすい 密着の 影（CONTACT）を 足した（.bco と 同じ 影の ほかに）
#      ・第4.112版（10:30「ボードに腕の模様が被っている」・10:38「ボードに脚の線が被ってるか、被ってないかのちがい」）：切り目（CUT）を 白い 輪の いちばん 上に。
#        足の うしろの 線・くさび・白い ふち・影は 白い 輪に かからず、輪の 上に 出るのは つなぎと ひづめ だけ（ハズレは bcx.js で 1.5px 下げる）
#      線は 外の ふちだけ（くさびの ななめ・つなぎの うしろの ふち）。ボードの ふちで 切れる 所（足が ボードの うしろへ 入る 所）には 線を 引かない
WEDGE = dict(FL=dict(apex=-9.1, foot=5.0), FR=dict(apex=-20.6, foot=242.0))   # くさび：上の はしの 高さ（ボードの 上の ふちから CSS px）と 下の 右の はし（FL：足の うしろの ふちから ＋px／FR：x）
WEDGE_COL = ('#B06430', '#BA6C34')                         # くさびの 色（足の むこう側の かげ）：関節の 線の 近く → ななめの 方。馬の かげの 色 #9A5327 から 足の 色 #C27237 へ 55% → 80%（第4.111版 08:29「濃い茶色もっと薄く、影に見えるくらいにして！」）
CUT = 3.0                                                 # 第4.112版（10:38）：足が ボードの うしろへ 入る 所は 白い 輪の いちばん 上（的中・大的中 3px）で 切る。ハズレ（輪 1.5px）は bcx.js で 前足を 1.5px 下げて 合わせる
LW = 3.0                                                  # 新しく 引く 線の 太さ（画素。3Dの 線と 同じ）
CONTACT = dict(dy=1.0, blur=0.9, a=0.30)                  # 第4.112版：密着の 影（ボードの 面に おしつけて いる つなぎと ひづめの まわり：下へ CSS px・ぼかし CSS px・こさ）
P3 = world_pos(RF)
PROJ = {k: {kk: sc_.project(np.array([vv]))[0][0] for kk, vv in v.items()} for k, v in segs.items()}
yy_, xx_ = np.mgrid[0:Hh, 0:W]


def dseg(p0, p1):
    d = p1 - p0
    t = np.clip(np.nansum((P3 - p0) * d, -1) / np.dot(d, d), 0, 1)
    q = p0 + t[..., None] * d
    return np.nan_to_num(np.linalg.norm(P3 - q, axis=-1), nan=9)


def aa_poly(polys, close=True, width=None):
    """CSS の 点（ボードの 左上から）の 多角形・線 → 画面の 0〜1（4倍で 描いて 縮める）"""
    m4 = np.zeros((Hh * 4, W * 4), np.uint8)
    for poly in polys:
        pts = np.array([[(BX0 + px * D) * 4 * 16, (BY0 + py * D) * 4 * 16] for px, py in poly], np.int64).astype(np.int32)
        if width is None:
            cv2.fillPoly(m4, [pts], 255, cv2.LINE_AA, shift=4)
        else:
            cv2.polylines(m4, [pts], close, 255, max(1, int(round(width * 4))), cv2.LINE_AA, shift=4)
    return cv2.resize(m4, (W, Hh), interpolation=cv2.INTER_AREA).astype(np.float32) / 255


def back_x(mk, yc):
    """その 高さ（CSS）の 足の うしろ（右）の ふち（CSS）"""
    xs = np.nonzero(mk[int(round(BY0 + yc * D))])[0]
    return (xs.max() + 1 - BX0) / D


def build_fore():
    mF = RF['m']
    legs = ((mF == 7) | ((mF == 6) & (yy_ < (BY0 + BY1) / 2))) & (RF['a'] > 0.02)
    hoofm = (mF == 6) & legs
    dist = {k: np.minimum.reduce([dseg(sg[a_], sg[b_]) for a_, b_ in (('el', 'kn'), ('kn', 'ft'), ('ft', 'co'), ('co', 'hf'))]) for k, sg in segs.items()}
    own = {k: legs & (dist[k] <= dist[o]) for k, o in (('FL', 'FR'), ('FR', 'FL'))}
    up = yy_ < BY0
    upf = np.clip(BY0 - CUT * D - yy_, 0, 1).astype(np.float32)            # 白い 輪の いちばん 上より 上（画素の 中の わりあい）：ここより 下に 出るのは つなぎと ひづめ だけ
    keepM, wedgeM, wlineM, lineM, frontM, overM, olineM, fillM = (np.zeros((Hh, W), np.float32) for _ in range(8))
    wgrad = np.zeros((Hh, W), np.float32)                                     # くさびの 色の まざり（0＝関節の 線の 近く → 1＝ななめの 方）
    hooves = {}
    o_ = LW / 2 / D

    def side(A, B):                                                           # 線 A→B（下から 上へ）の 右（うしろ）が ＋（画素）
        d = B - A; n_ = math.hypot(*d)
        return (d[0] * (yy_ - A[1]) - d[1] * (xx_ - A[0])) / n_

    def rightmost(m):                                                         # 行ごとの いちばん 右の 画素（ない 行は -1）
        return np.where(m.any(1), W - 1 - np.argmax(m[:, ::-1], 1), -1)
    for k, mk in own.items():
        sg, pr = segs[k], PROJ[k]
        hk = hoofm & mk
        u = pr['hf'] - pr['co']; u = u / np.linalg.norm(u)                    # ひづめの 向き（下へ）
        v = np.array([-u[1], u[0]]) if -u[1] > 0 else np.array([u[1], -u[0]])   # それに 直角で うしろ（右）へ
        s_ = (xx_ - pr['co'][0]) * u[0] + (yy_ - pr['co'][1]) * u[1]
        t = (xx_ - pr['co'][0]) * v[0] + (yy_ - pr['co'][1]) * v[1]
        top = hk & (s_ <= np.percentile(s_[hk], 4))
        ci = np.argmax(np.where(top, t, -1e9))
        cy_, cx_ = np.unravel_index(ci, t.shape)
        Ph = np.array([cx_ + 0.5, cy_ + 0.5])                                 # ひづめの うしろの 上の かど（画素）
        s_top = float(np.percentile(s_[hk], 1))                               # ひづめの 上の ふち（ひづめの 向きで）
        ya = WEDGE[k]['apex']; xa = back_x(mk & up, ya); x0b = back_x(mk & up, -0.4); xcb = back_x(mk & up, -CUT)
        xb = x0b + WEDGE[k]['foot'] if k == 'FL' else WEDGE[k]['foot']
        nx, ny = -ya, -(xb - xa); nn = math.hypot(nx, ny); nx, ny = nx / nn, ny / nn   # くさびの ななめの 外むき
        Pa = np.array([BX0 + xa * D, BY0 + ya * D])                           # くさびの 上の はし
        Pf = np.array([BX0 + xb * D, BY0])                                    # くさびの 下の 右の はし（ボードの 上の ふち）
        dh = side(Pf, Pa)                                                     # くさびの ななめ（下の はし → 上の はし）の 右＝胸の 方・外が ＋
        if k == 'FL':
            # 第4.110版（07:45「赤線に合わせて」）：つなぎの うしろの ふちは ひづめの うしろの 上の かど → 関節の 線が ボードの ふち（白い 輪の 上）に とどく 所 の まっすぐな 線
            Pb = np.array([BX0 + xcb * D, BY0 - CUT * D])
            dred = side(Ph, Pb)
            fill = (s_ <= s_top + 1.5) & (yy_ >= Pb[1] - 1) & ~hk               # ふちより 下・ひづめより 上
            front = mk | ((dred < 0) & (xx_ >= np.where(mk.any(1, keepdims=True), np.argmax(mk, 1)[:, None], W)))   # 足の 前の ふちより うしろ
            low = (fill & front).astype(np.float32) * np.clip(0.5 - dred, 0, 1)
            fillM = np.maximum(fillM, low * ~(mk & (aF > 0.5)))                    # 3Dの 足が ない 所（赤線まで）は 足の 色で うめる
            low = np.maximum(low, hk.astype(np.float32))
            lineM = np.maximum(lineM, ((np.abs(dred + LW / 2) < LW / 2 + 0.5) & (upf < 0.5) & (low > 0.5) & ~hk).astype(np.float32))
            # くさび（左は 小さな 三角：足の 下に しく ので 足の うしろの 線＝関節の 線は のこる）
            wedgeM = np.maximum(wedgeM, aa_poly([[(xa - 4.0, ya + 1.0), (xa, ya), (xb, 0.0), (x0b - 4.0, 0.0)]]) * upf)
            wlineM = np.maximum(wlineM, aa_poly([[(xa - o_ * nx, ya - o_ * ny), (xb - o_ * nx, -o_ * ny)]], close=False, width=LW) * upf)
            dback = xx_ - rightmost(mk & (aF > 0.5) & up)[:, None]              # 足の うしろの ふちから 右へ（画素）
            region = wedgeM
        else:
            # 第4.110版（07:45「赤線に合わせて」）：関節の 線は ひづめの うしろの 上の かど → くさびの 上の はし の まっすぐな 線。
            # その 右（ボードの ふちまで）は ぜんぶ くさびの 色（足の 上に ぬる）
            low = hk.astype(np.float32)
            dj = side(Ph, Pa)
            reg = (np.clip(0.5 + dj, 0, 1) * np.clip(0.5 - dh, 0, 1) * (yy_ >= Pa[1]) * upf * (1 - cv2.dilate(hk.astype(np.uint8), np.ones((3, 3), np.uint8))))
            overM = np.maximum(overM, reg.astype(np.float32))
            olineM = np.maximum(olineM, aa_poly([[((Ph[0] - BX0) / D, (Ph[1] - BY0) / D), (xa, ya)]], close=False, width=LW))
            olineM = np.maximum(olineM, aa_poly([[(xa - o_ * nx, ya - o_ * ny), (xb - o_ * nx, -o_ * ny)]], close=False, width=LW) * upf)
            dback = dj                                                        # 関節の 線から 右へ（画素）
            region = overM
        # くさびの 色の まざり（第4.111版）：関節の 線の 近くは 少し こく → ななめの 方へ うすく
        f = np.clip(np.maximum(dback, 0) / np.maximum(np.maximum(dback, 0) - dh, 1.0), 0, 1)
        wgrad = np.where(region > 0.02, f * f * (3 - 2 * f), wgrad)
        keepM = np.maximum(keepM, mk.astype(np.float32) * upf + low * (1 - upf))
        frontM = np.maximum(frontM, low)                                      # ボードの 前に 出る 所（つなぎと ひづめ）
        hooves[k] = hk
    body = (legs & up) & (cv2.erode(legs.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0)
    legcol = np.median(colF[body], axis=0)                                    # 足の 色（3Dの 足の まん中の 色）
    fillM = fillM * (1 - upf)
    la = np.clip(np.maximum(keepM * np.clip(aF, 0, 1), fillM), 0, 1)          # 足（3Dの 色と 線）＋ 赤線まで うめた 所
    lc = colF * (1 - fillM[..., None]) + legcol * fillM[..., None]
    lc = lc * (1 - lineM[..., None] * 0.92) + hexc(cfg['line']) * lineM[..., None] * 0.92
    wcmap = hexc(WEDGE_COL[0]) * (1 - wgrad[..., None]) + hexc(WEDGE_COL[1]) * wgrad[..., None]   # くさび（足の かげの 色：関節の 線の 近く → ななめの 方）
    wc = wcmap * (1 - wlineM[..., None] * 0.92) + hexc(cfg['line']) * wlineM[..., None] * 0.92   # と ななめの 線
    a = np.clip(la + wedgeM * (1 - la), 0, 1)
    c = (lc * la[..., None] + wc * (wedgeM * (1 - la))[..., None]) / np.maximum(a, 1e-4)[..., None]
    # 右の 足：関節の 線より 右（くさびの ななめ・ボードの ふちまで）は くさびの 色を 足の 上に ぬる → 関節の 線と くさびの ななめの 線
    a2 = np.clip(a + overM * (1 - a), 0, 1)
    c = (c * a[..., None] * (1 - overM[..., None]) + wcmap * overM[..., None]) / np.maximum(a2, 1e-4)[..., None]
    a = a2
    ol_ = olineM * (a > 0.02)
    c = c * (1 - ol_[..., None] * 0.92) + hexc(cfg['line']) * ol_[..., None] * 0.92
    # 白い ふち（ほかの 部品の .bco と 同じ 見え方を 絵に 入れる）：胸や 首の 前・ボードの うしろへ 入る 切り口には つけない。
    # 影（.bco と 同じ：3px 下・ぼかし 3px・0.34）は ボードの 前に 出る つなぎと ひづめ だけ。
    # 第4.112版：その まわりに 密着の 影（CONTACT：1px 下・ぼかし 0.9px・0.30）も 足す＝ボードの 面に おしつけて いる 感じ
    ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    sil = (a > 0.5).astype(np.uint8)
    rim = np.clip(cv2.GaussianBlur(cv2.dilate(sil, ker).astype(np.float32), (5, 5), 1.0) - a, 0, 1) * 0.95
    behind = cv2.GaussianBlur((np.maximum(aB, mane_a) > 0.5).astype(np.float32), (5, 5), 1.0) * (yy_ < BY0 - CUT * D)
    cutz = (np.abs(yy_ - (BY0 - CUT * D)) < 4) & ~(cv2.dilate((frontM > 0.5).astype(np.uint8), ker) > 0)
    rim = rim * (1 - behind) * (1 - cutz)
    fa = frontM * a
    sh = cv2.GaussianBlur(np.roll(fa, int(round(3 * D)), axis=0), (0, 0), 1.5 * D) * 0.34
    ct = cv2.GaussianBlur(np.roll(fa, int(round(CONTACT['dy'] * D)), axis=0), (0, 0), CONTACT['blur'] * D) * CONTACT['a']
    sh = (sh + ct * (1 - sh)) * (1 - a) * (1 - rim)
    A = np.clip(a + rim * (1 - a) + sh, 0, 1)
    C = (c * a[..., None] + rim[..., None] * (1 - a[..., None])) / np.maximum(A, 1e-4)[..., None]
    return C, A, hooves


foreC, foreA, HOOVES = build_fore()

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
    print('鼻先:', [round((v - o) / D, 1) for v, o in zip(RB['muzzle'], (BX0, BY0))], ' 頭の てっぺん（poll）:', [round((v - o) / D, 1) for v, o in zip(RB['poll'], (BX0, BY0))], ' ひづめの 下（CSS・ボードの 上の ふちから）:', {k: round(((np.nonzero(h.any(1))[0].max() + 1) - BY0) / D, 1) for k, h in HOOVES.items()},
          ' ひづめの 横:', {k: [round((np.nonzero(h.any(0))[0].min() - BX0) / D, 1), round((np.nonzero(h.any(0))[0].max() + 1 - BX0) / D, 1)] for k, h in HOOVES.items()})
    shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(0)

from PIL import Image
bad = []
for k_, v_ in (('eyeC', (ex, ey)), ('muzzle', RB['muzzle']), ('poll', RB['poll'])):       # アプリが 使う 目印（目を 見ひらく・汗・鼻の 息）
    gx, gy = (v_[0] - BX0) / D, (v_[1] - BY0) / D
    if abs(gx - HBX[k_][0]) > 1.5 or abs(gy - HBX[k_][1]) > 1.5:
        bad.append(f'{k_}：HBX {HBX[k_]} と 絵 {gx:.1f},{gy:.1f} が ちがう')
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
