"""ドット絵の壁紙の動き（まさちゃんの指定）：走る・ジャンプ・一回転・こっちを見る・走りだす コマ
   「常に走っている」→「止まってからの走り出しが唐突だから、走り出しもちゃんとして！」→
   「4秒〜13秒 ランダムでジャンプ、一回転してユーザーの方を1秒見てから走り出して！」「ジャンプまたは一回転」→
   「20秒〜23秒に一回立ち止まるのがなくなってるよ！」
   - いまの絵と同じドットの馬（r3d/banners/pixel.py の horse・同じカメラ・同じ4色と1ドットのふち）を、156×64 のドットのまま描く
     ・走る：ギャロップ1回を N_RUN コマ。足の動きは海の馬と同じ（flat/sea_run.py の F_KEYS・H_KEYS・LEG_OFF）、体の傾き・首・頭は
       いまの絵の形（GALLOP）を中心に少しゆれる。地面についている ひづめの高さをそろえ（カメラを上下にずらして描く）、4本とも宙のときは少し浮く
     ・立ち止まる：前足を前へつっぱり、うしろ足を おなかの下へ入れて すべる2コマ（brake0・1：ひづめの うしろに土けむり（出たて → ふくらむ））→
       立って待つ2コマ（stand0・1：首と頭が少し上下・しっぽが少しゆれる。昔のゲームの「待っている」動き）
     ・ジャンプ：けり出す（push）→ 足をたたんで高く跳ぶ（jair0〜7・山なり・最後の2コマは前足をのばして おりる用意）→
       前足をつっぱって おりる（brake1 と同じコマ・土けむり）。宙にいる間は 地面に小さな かげ（高いほど小さい）
     ・一回転：その場で小さく跳ねながら くるっと回る（spin0〜10：45°ずつ・1回転と4分の1で こっちを向いて おりる）。
       回すのは カメラ（馬のまん中のたての軸のまわり）で、明るい側の向きも同じだけ回す（どの向きでも同じように見える）。
       正面では両目・うしろ向きでは目を描かない。おりたら 足もとに土けむり（sland）
     ・こっちを見る：正面を向いて立つ（look）・まばたき（blink）・ななめ（turn：正面 ↔ 横の あいだ）
     ・走りだす：かまえる（ready）→ けり出す（push・土けむり）→ 1歩め（dash＝走るコマの0に うしろへ流れた土けむり）
   - コマは 馬だけ（土けむり・宙の かげ も）：いまの絵の 馬が動く所を切りぬいて横に並べた1まい（pixel_run.webp・ドットのまま＝1倍・
     馬の所だけ すき通さない・ロスなし）。ページでは いまの絵の同じ場所に重ねて、ドットは ぼかさずに大きくする（pixel_wall.py・image-rendering:pixelated）。
   - まさちゃん「背景を右から左に動かしてリピートして！背景は遠いからゆっくりめで！」→ うしろの景色を 3まいに分ける（どれも ドットのまま・ロスなし）：
     ・空：上の帯と 下の帯の2色だけ（ページの CSS でぬる）
     ・遠くの景色（pixel_far.webp）：雲の帯と 丘の帯（すき通し）。はば FAR_P ドットで くり返す。はじめの156ドットは いまの絵と同じで、
       その先は 雲を1つ足し、丘の上のふちは いまの式から FAR_P で はじめに戻る式へ なめらかに うつる（丘のしまも FAR_P でつながる）
     ・前の景色（pixel_near.webp）：コース・さく・ゴール板・「GO!」（動かない・すき通し）
     空 → 雲 → 丘 → 前の景色 → 馬 と重ねて、ずれていない時は いまの絵と1ドットもちがわない（run() で確かめる）
   - 下に置く いまの絵も ここで ロスなしで書き出す（pixel_static.webp・5倍：キャンバスの いまの絵は ロスありで 色のふちが少し にじむので、
     重ねた所の さかい目が見えないように そろえた）
   python3 flat/pixel_run.py <出力フォルダ> [見本PNG]  → pixel_run.webp・pixel_far.webp・pixel_near.webp・pixel_static.webp・pixel_run.json
     （切りぬく場所・コマの並び・景色の帯）（sdfr がいる。1分ほど）"""
import sys, os, math, json
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d', 'banners'))
sys.path.insert(0, os.path.join(HERE, '..', 'r3d'))
sys.path.insert(0, HERE)
import pixel as PX
import horse3d as Hm
from h3d import Scene, nrm
from sea_run import F_KEYS, H_KEYS, LEG_OFF, STANCE, leg_at

N_RUN = 15                         # 全速の ギャロップ1回の コマ数（第4.167版：8 → 15＝1コマ 1/30秒。まさちゃん 2026/11/13
                                   #   「海賊の壁紙カクカクするんだけど、他にもカクカクする物があれば見つけて！全部ヌルヌル動くようにして！」）
N_FIT = 8                          # 上下の 波を 決める コマ数（第4.166版までの 8コマ：走る 上下の 動きは 前の まま）
N1, N2 = 30, 21                    # 走りだしの 1歩め（1.0秒）・2歩め（0.7秒）の コマ数（どれも 1コマ 1/30秒）
LEN = dict(stop=60, jump=75, spin=75, start=60)   # 1コマ 1/30秒：立ち止まる 2.0秒・ジャンプ／一回転 2.5秒・走りだし（けり出して 全速まで）2.0秒
READY_AT = dict(stop=53, jump=65, spin=62)        # 「かまえる」が 始まる コマ
LAND_AT = 23                       # ジャンプ・一回転から おりる コマ（宙は 19コマ・一回転は 23コマ）
LIFT = 1.2                         # 走っていて4本とも宙のときに浮く高さ（ドット）
JUMP_H = 5.0                       # ジャンプの いちばん高い所（体が 走っている時より何ドット上か・耳が絵の上から はみ出さない）
SPIN_H = 2.0                       # 一回転の小さな跳ね
N_JUMP, N_SPIN = 19, 23            # ジャンプの宙のコマ・一回転のコマ（第4.167版：8 → 19・11 → 23。一回転は 1コマ 18.75°ずつ 450°まで）
HOOF_KEYS = ('FL', 'FR', 'HL', 'HR')
FOV = 26.0
LIGHT = np.array([0.3, 0.8, 0.5])  # pixel.horse の明るい側（横向きのとき）
G = dict(Hm.GALLOP)
# 形（右向き：手前＝L・奥＝R）。hair：たてがみとしっぽ（pixel.HAIR を上書き）
BRAKE = dict(theta=4.0, neck_rot=-4.0, head_ang=-48.0, tail=[-150, -130],          # 立ち止まる・ジャンプから おりる：前足を前へつっぱり、うしろ足を おなかの下へ
             fore=dict(L=[-70, -62, -62, -50], R=[-76, -66, -66, -52]), hind=dict(L=[-50, -125, -60, -30], R=[-46, -121, -56, -28]),
             hair=dict(wind_ang=2.6, mane_len=0.85))
IDLE = [dict(theta=0.0, neck_rot=2.0, head_ang=-58.0, tail=[-118, -100],          # 立ち止まって待つ（横向き・2コマ：首と頭が少し上下・しっぽが少しゆれる）
             fore=dict(L=[-125, -90, -90, -60], R=[-122, -88, -88, -58]), hind=dict(L=[-62, -118, -92, -62], R=[-66, -120, -94, -64]),
             hair=dict(wind_ang=1.9, mane_len=0.55, tail_len=0.85)),
        dict(theta=0.0, neck_rot=5.0, head_ang=-52.0, tail=[-126, -108],
             fore=dict(L=[-125, -90, -90, -60], R=[-122, -88, -88, -58]), hind=dict(L=[-62, -118, -92, -62], R=[-66, -120, -94, -64]),
             hair=dict(wind_ang=2.1, mane_len=0.55, tail_len=0.85))]
STAND = dict(theta=0.0, neck_rot=-8.0, head_ang=-54.0, tail=[-118, -100],           # 立つ（こっちを見る・正面だと耳が上に来るので 頭を少し低く）
             fore=dict(L=[-125, -90, -90, -60], R=[-122, -88, -88, -58]), hind=dict(L=[-62, -118, -92, -62], R=[-66, -120, -94, -64]),
             hair=dict(wind_ang=1.9, mane_len=0.55, tail_len=0.85))
READY = dict(theta=2.0, neck_rot=-22.0, head_ang=-42.0, tail=[-140, -120],         # かまえる：頭を下げて前へ・うしろ足を おなかの下へ
             fore=dict(L=[-108, -94, -98, -72], R=[-112, -96, -100, -74]), hind=dict(L=[-48, -126, -74, -46], R=[-52, -128, -76, -48]),
             hair=dict(wind_ang=2.4, mane_len=0.7, tail_len=0.9))
PUSH = dict(theta=10.0, neck_rot=-20.0, head_ang=-40.0, tail=[-165, -150],          # けり出す：うしろ足で地面をけって前が上がる・前足は1本たたみ1本のばす
            fore=dict(L=[-118, -30, -140, -165], R=[-70, -30, -45, -30]), hind=dict(L=[-100, -136, -112, -124], R=[-94, -132, -108, -120]),
            hair=dict(wind_ang=3.0, mane_len=0.9))
TUCK = dict(theta=0.0, neck_rot=-12.0, head_ang=-46.0, tail=[-150, -135],           # ジャンプ：前足もうしろ足も たたむ
            fore=dict(L=[-62, -8, -112, -140], R=[-66, -14, -116, -146]), hind=dict(L=[-52, -150, -72, -42], R=[-56, -154, -76, -46]),
            hair=dict(wind_ang=2.9, mane_len=0.95))
REACH = dict(theta=-4.0, neck_rot=-6.0, head_ang=-50.0, tail=[-140, -125],          # ジャンプの おわり：前足を下へのばして おりる用意
             fore=dict(L=[-78, -70, -80, -66], R=[-84, -76, -86, -70]), hind=dict(L=[-96, -146, -110, -118], R=[-100, -150, -114, -122]),
             hair=dict(wind_ang=2.6, mane_len=0.9))
HOP = dict(theta=0.0, neck_rot=-20.0, head_ang=-48.0, tail=[-130, -112],            # 一回転：ひざを少しまげて小さく跳ねる（頭は少し低く＝上がはみ出さない）
           fore=dict(L=[-112, -72, -100, -82], R=[-110, -70, -98, -80]), hind=dict(L=[-56, -128, -86, -58], R=[-60, -130, -88, -60]),
           hair=dict(wind_ang=2.0, mane_len=0.6, tail_len=0.9))
DUST = '#FFF1E8', '#C2C3C7'        # 土けむりの色（白・かげの灰）
SHADOW = '#8A3F28'                 # 宙にいるときの地面の かげ（コースのこい色）
# 土けむり：(ひづめからの x, 地面からの y, 半径)
DUST_HIND = ([(-6, -1.5, 2.2), (-10, -2.2, 1.8), (-7.5, -4.2, 1.3)],                                  # ブレーキの2コマ（出たて → ふくらんで少し上へ）：うしろ足の うしろ
             [(-7, -2.2, 2.7), (-11.5, -3.2, 2.3), (-15, -1.6, 1.6), (-8.5, -5.6, 1.9)])
DUST_FORE = ([(-4.5, -1.2, 1.7), (-7.5, -2, 1.3)], [(-5, -1.8, 2.1), (-8.5, -2.8, 1.7), (-6, -4.6, 1.3)])   #                                        ：前足の うしろ
DUST_PUSH = [(-4.5, -1.8, 2.6), (-9, -3, 2.4), (-13, -1.6, 1.9), (-6.5, -5.6, 2.0), (-11, -6.4, 1.3)]   # けり出す（大きい）
DUST_DASH = [(-11, -2.4, 2.0), (-15.5, -3.6, 1.7), (-18.5, -1.8, 1.2), (-13, -6.4, 1.1)]               # 1歩め（うしろへ流れて小さく）
DUST_SPIN = [(-5.5, -1.6, 2.3), (-9, -2.8, 1.7), (-6.5, -4.4, 1.3), (5.5, -1.6, 2.3), (9, -2.8, 1.7), (6.5, -4.4, 1.3)]   # 一回転から おりる（足もとの左右・まん中からの x）
FAR_P = 200                        # 遠くの景色（雲・丘）を くり返す はば（ドット）。はじめの156は いまの絵と同じ（200 の半分が5の倍数＝丘のしまも つながる）
MORE_CLOUDS = [(172, 8)]           # 157〜200 に足す雲（いまの雲と同じ形）
CLOUD_ROWS, HILL_ROWS = (0, 16), (28, 40)   # 雲の帯・丘の帯（行）


def run_pose(g):
    """ギャロップの位相 g（0〜1）の形。体・首・頭は いまの絵の形（GALLOP）を中心にゆれる"""
    leg = lambda k: leg_at(F_KEYS if k[0] == 'F' else H_KEYS, g - LEG_OFF[k])
    w = 2 * math.pi
    return dict(theta=round(G['theta'] + 3.0 * math.cos(w * (g - 0.15)), 2), neck_rot=round(G['neck_rot'] + 5 * math.cos(w * (g - 0.55)), 2),
                head_ang=round(G['head_ang'] + 3 * math.sin(w * g), 2), tail=G['tail'],
                fore=dict(L=leg('FL'), R=leg('FR')), hind=dict(L=leg('HL'), R=leg('HR')))


def scene(cam):
    sc = Scene()
    sc.image(PX.W, PX.Hh, 1)
    sc.camera(cam[0], cam[1], FOV)
    return sc


def hooves(pose, cam):
    """ひづめの点（ドット）：描かずに、骨組みとカメラだけで出す"""
    S = Hm.skeleton(pose)
    q = scene(cam).project([Hm.v3(S[k]['hf'], 0.155 * S[k]['z']) for k in HOOF_KEYS])[0]
    return {k: q[i] for i, k in enumerate(HOOF_KEYS)}


def shifted(cam, dy):
    """絵の中で dy ドット 下へずれるように、カメラを上へずらす"""
    e, t = (np.asarray(v, float) for v in cam)
    fw = nrm(t - e)
    rt = nrm(np.cross(fw, (0, 1, 0)))
    up = np.cross(rt, fw)
    wpp = 2 * np.linalg.norm(t - e) * math.tan(math.radians(FOV / 2)) / PX.Hh
    d = up * dy * wpp
    return (e + d, t + d)


def rot_y(v, deg):
    """たての軸のまわりに deg 度（+ で、横向きの馬が こっちを向く方へ回って見える）"""
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    x, y, z = v
    return np.array([x * c + z * s, y, -x * s + z * c])


def body_center(pose):
    """回す軸（き甲と腰のまん中・地面の高さは関係なし）"""
    S = Hm.skeleton(pose)
    return np.array([(S['withers'][0] + S['hip'][0]) / 2, 0.0, 0.0])


def body_y(pose, cam):
    """体のまん中（き甲と腰のまん中）の 絵の上の高さ（ドット）"""
    S = Hm.skeleton(pose)
    return float(scene(cam).project(np.array([Hm.v3((np.asarray(S['withers']) + np.asarray(S['hip'])) / 2)]))[0][0][1])


def orbit(cam, pose, yaw):
    """カメラを 馬のまん中の たての軸のまわりに yaw 度 回す（馬が回って見える）"""
    C = body_center(pose)
    e, t = (np.asarray(v, float) for v in cam)
    return C + rot_y(e - C, yaw), C + rot_y(t - C, yaw)


def run_wave(cam):
    """走る 上下の 波（位相 g → 上下の ずれ）と 地面の 高さ。決め方は 第4.166版までと 同じ（8コマ：地面に ついて いる ひづめを そろえる・宙は 山なり・
       2つの 波で なめらかに）＝走る 上下の 動きは 前の まま。コマを ふやして 決め直すと、足が 地面を はなれる 瞬間の コマが 入って 体が しずむ（第4.166版）"""
    n = N_FIT
    lows = []
    for f in range(n):
        g = f / n
        hv = hooves(run_pose(g), cam)
        legs = [k for k in HOOF_KEYS if ((g - LEG_OFF[k]) % 1.0) < STANCE]
        lows.append(max(hv[k][1] for k in legs) if legs else None)
    ground = float(max(hooves(G, cam)[k][1] for k in HOOF_KEYS))        # いまの絵の いちばん低い ひづめ
    dy = [None if v is None else ground - v for v in lows]
    for i in range(n):
        if dy[i] is None:
            jp = next(j for j in range(1, n) if lows[(i - j) % n] is not None)
            jn = next(j for j in range(1, n) if lows[(i + j) % n] is not None)
            t = jp / (jp + jn)
            prev, nxt = ground - lows[(i - jp) % n], ground - lows[(i + jn) % n]
            dy[i] = prev + (nxt - prev) * t - LIFT * 4 * t * (1 - t)
    ph = 2 * math.pi * np.arange(n) / n
    A = np.stack([np.ones(n), np.cos(ph), np.sin(ph), np.cos(2 * ph), np.sin(2 * ph)], 1)
    coef = np.linalg.lstsq(A, np.array(dy), rcond=None)[0]

    def wave(g):
        p = 2 * math.pi * g
        return float(coef @ np.array([1.0, math.cos(p), math.sin(p), math.cos(2 * p), math.sin(2 * p)]))
    return wave, ground


HAIR0 = dict(wind_ang=PX.HAIR['wind_ang'], mane_len=1.0, tail_len=1.0)       # たてがみ・しっぽの きまった 形（hair が ない 形）


def mix(a, b, w):
    """形 a → b の あいだ（w：0＝a・1＝b）。角度・しっぽ・足・たてがみを 1つずつ まぜる（形の 入れかわりを 1/30秒ずつ つなぐ）"""
    w = min(1.0, max(0.0, w))
    L = lambda x, y: x + (y - x) * w
    out = {k: round(L(a[k], b[k]), 3) for k in ('theta', 'neck_rot', 'head_ang')}
    out['tail'] = [round(L(x, y), 3) for x, y in zip(a['tail'], b['tail'])]
    for part in ('fore', 'hind'):
        out[part] = {sd: [round(L(x, y), 3) for x, y in zip(a[part][sd], b[part][sd])] for sd in 'LR'}
    ha, hb = dict(HAIR0, **a.get('hair', {})), dict(HAIR0, **b.get('hair', {}))
    out['hair'] = {k: round(L(ha[k], hb[k]), 4) for k in HAIR0}
    return out


def dmix(d0, d1, w):
    """土けむり d0 → d1 の あいだ（丸の 数が ちがう 時は、足りない 丸を 半径 0 から ふくらます／0 へ しぼます）"""
    out = []
    for i in range(max(len(d0), len(d1))):
        p = d0[i] if i < len(d0) else (d1[i][0], d1[i][1], 0.0)
        q = d1[i] if i < len(d1) else (d0[i][0], d0[i][1], 0.0)
        out.append(tuple(u + (v - u) * w for u, v in zip(p, q)))
    return out


def dmove(d, dx=0.0, dy=0.0, k=1.0):
    """土けむりを ずらす・小さく する（半径 k 倍）"""
    return [(x + dx, y + dy, r * k) for x, y, r in d]


def brake_dust(j):
    """ブレーキ・着地の 土けむり（j：出て からの コマ）→ (うしろ足の うしろ, 前足の うしろ)。出たて → ふくらむ（前の 2コマの あいだを うめる）→ 上へ → うすれる"""
    H0, H1 = DUST_HIND
    F0, F1 = DUST_FORE
    if j < 0 or j > 11:
        return [], []
    if j == 0:
        return dmove(H0, k=.6), dmove(F0, k=.6)
    if j <= 4:
        return dmix(H0, H1, (j - 1) / 3), dmix(F0, F1, (j - 1) / 3)
    if j <= 7:
        return dmove(H1, -.2 * (j - 4), -.3 * (j - 4)), dmove(F1, -.2 * (j - 4), -.3 * (j - 4))
    k = 1 - .22 * (j - 7)
    return dmove(H1, -.6 - .2 * (j - 7), -.9 - .3 * (j - 7), k), dmove(F1, -.6 - .2 * (j - 7), -.9 - .3 * (j - 7), k)


def push_dust(f):
    """けり出す 土けむり（f：走りだしの コマ）：ふくらむ → 少し 上へ → うしろへ 流れて 小さく（前の「けり出す」と「1歩め」の あいだを うめる）"""
    if f < 1 or f > 15:
        return []
    if f <= 3:
        return dmove(DUST_PUSH, k=(.5, .75, 1.0)[f - 1])
    up = lambda j: dmove(DUST_PUSH, -.15 * j, -.12 * j)
    if f <= 8:
        return up(f - 3)
    if f <= 11:
        return dmix(up(5), DUST_DASH, (f - 8) / 3)
    j = f - 11
    return dmove(DUST_DASH, -1.0 * j, -.3 * j, 1 - .22 * j)


def spin_dust(j):
    """一回転から おりる 土けむり（j：おりて からの コマ）"""
    if j < 0 or j > 7:
        return []
    if j <= 1:
        return dmove(DUST_SPIN, k=(.6, .8)[j])
    if j <= 4:
        return dmove(DUST_SPIN, 0, -.15 * (j - 2))
    return dmove(DUST_SPIN, 0, -.3 - .25 * (j - 4), (.7, .45, .25)[j - 5])


def dust(img, discs):
    """ドットの土けむり：丸をいくつか重ねた形（白・右下は かげの灰）"""
    H, W = img.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W] + .5
    m = np.zeros((H, W), bool)
    sh = np.zeros((H, W), bool)
    for cx, cy, r in discs:
        d = (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r
        m |= d
        sh |= d & (((xx - cx) * .5 + (yy - cy)) > r * .35)
    img[m] = PX.hexc(DUST[0])
    img[m & sh] = PX.hexc(DUST[1])


def shadow(img, cx, ground, w):
    """宙にいるときの地面の かげ（よこ長の だ円・コースの上だけ）"""
    yy, xx = np.mgrid[0:PX.Hh, 0:PX.W] + .5
    m = (((xx - cx) / w) ** 2 + ((yy - (ground + .5)) / 1.6) ** 2 <= 1) & (yy > 41)
    img[m] = PX.hexc(SHADOW)


def save_lossless(img, path):
    """WebP（ロスなし）：ドットの色がそのまま残る（ロスありだと 色のふちが にじんで、重ねた所の さかい目が見える）"""
    u8 = (np.clip(img, 0, 1) * 255 + .5).astype(np.uint8)
    cv2.imwrite(path, cv2.cvtColor(u8, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_WEBP_QUALITY, 101])     # 101＝ロスなし


EYE_PX = []                                      # frame() が 描いた 目の 画素（コマごと。run() の add() で すき通しの 印に 足す）


def frame(pose, cam, ground, name, dy=None, yaw=0.0, lift=0.0, eyes='near', shade=False, by=None):
    """1コマ：背景（宙なら かげ）→ 馬（「GO!」は add で）。pose の hair は たてがみとしっぽ。dy がなければ、いちばん低い ひづめを 地面から lift 上に
       （by：体のまん中を この高さに。ひづめは地面より下へは行かない）。yaw：馬が回って見える角度（カメラと明るい側を回す）"""
    p = {k: v for k, v in pose.items() if k != 'hair'}
    c = orbit(cam, p, yaw) if yaw else cam
    if dy is None:
        dy = ground - max(hooves(p, c)[k][1] for k in HOOF_KEYS)
        dy = min(by - body_y(p, c), dy) if by is not None else dy - lift
    c = shifted(c, dy)
    img = PX.background()
    if shade:
        cx = scene(c).project(np.array([body_center(p)]))[0][0][0]
        shadow(img, cx, ground, max(4.0, 9.0 - lift * .45))
    img, R = PX.horse(img, p, c, name=name, hair=pose.get('hair'), light=rot_y(LIGHT, yaw), eyes=eyes)
    EYE_PX.append(list(R.get('eye_px', [])))                                 # このコマの 目の 画素（add() が 拾う）
    return img, R, dy, c


def spin_eyes(yaw):
    """回って いる 時の 目：正面の 近く（90°±20°）は 両目・うしろ向き（202.5°〜337.5°）は 描かない（前の 45°きざみの コマと 同じ 分け方）"""
    a = yaw % 360
    return 'both' if abs(a - 90) < 20 else 'none' if 202.5 < a < 337.5 else 'near'


def hill_top(x):
    """丘の上のふち（いまの絵と同じ式。156 より先は、FAR_P で はじめに戻る式へ なめらかに うつる）"""
    f = lambda u: 34 + 3 * math.sin(u / 9) + 2 * math.sin(u / 4.3)
    if x < PX.W:
        return int(f(x))
    w = (x - PX.W) / (FAR_P - PX.W)
    w = w * w * (3 - 2 * w)
    return int((1 - w) * f(x) + w * f(x - FAR_P))


def far_sheet():
    """遠くの景色（すき通し・はば FAR_P でくり返す）：上に雲の帯（CLOUD_ROWS）・下に丘の帯（HILL_ROWS）"""
    c0, c1 = CLOUD_ROWS
    h0, h1 = HILL_ROWS
    sh = np.zeros((c1 - c0 + h1 - h0, FAR_P, 4), np.float32)
    for cx, cy in [(20, 9), (70, 6), (128, 11)] + MORE_CLOUDS:              # 雲（いまの絵と同じ形）
        for dx, dy, w in [(0, 0, 14), (3, -2, 8), (-2, 1, 4)]:
            for x in range(cx + dx, cx + dx + w):
                sh[cy + dy - c0:cy + dy + 3 - c0, x % FAR_P] = (*PX.PAL['cloud'], 1)
    for x in range(FAR_P):                                                  # 丘（たての しまは いまの絵と同じ きまり）
        h = hill_top(x)
        sh[c1 - c0 + h - h0:c1 - c0 + h1 - h0, x] = (*(PX.PAL['hill2'] if (x // 2 + h) % 5 == 0 else PX.PAL['hill']), 1)
    return sh


def near_layer():
    """前の景色（動かない・すき通し）：コース・さく（下の線と 丘の前の くい）・ゴール板・「GO!」"""
    img = PX.go_text(PX.background())
    a = np.zeros((PX.Hh, PX.W), np.float32)
    a[40:] = 1
    a[39, ::4] = 1
    a[22:40, 140] = 1
    a[22:28, 136:145] = 1
    return np.dstack([img, a])


def sky_rows():
    """空の2色（[(色, ここまでの行)]）"""
    return [(PX.PAL['sky1'], 18), (PX.PAL['sky2'], 40)]


def layered(off_c=0, off_h=0):
    """空 → 雲 → 丘 → 前の景色 を重ねた絵（off：左へ ずらすドット）"""
    img = np.zeros((PX.Hh, PX.W, 3), np.float32)
    y = 0
    for col, y1 in sky_rows():
        img[y:y1] = col
        y = y1
    far = far_sheet()
    for (r0, r1), sy, off in ((CLOUD_ROWS, 0, off_c), (HILL_ROWS, CLOUD_ROWS[1] - CLOUD_ROWS[0], off_h)):
        band = far[sy:sy + r1 - r0, (np.arange(PX.W) + off) % FAR_P]
        a = band[..., 3:] > 0
        img[r0:r1] = np.where(a, band[..., :3], img[r0:r1])
    near = near_layer()
    return np.where(near[..., 3:] > 0, near[..., :3], img)


def save_lossless_rgba(img, path):
    """すき通しつきの WebP（ロスなし）"""
    u8 = (np.clip(img, 0, 1) * 255 + .5).astype(np.uint8)
    cv2.imwrite(path, cv2.cvtColor(u8, cv2.COLOR_RGBA2BGRA), [cv2.IMWRITE_WEBP_QUALITY, 101])


def run(out, sample=None):
    os.makedirs(out, exist_ok=True)
    cam = PX.camera()
    orig = PX.background()
    orig, _ = PX.horse(orig)
    PX.go_text(orig)
    wave, ground = run_wave(cam)
    bare = lambda p: {k: v for k, v in p.items() if k != 'hair'}
    RUN0 = run_pose(0.0)
    by0 = float(np.mean([body_y(run_pose(f / N_FIT), shifted(cam, wave(f / N_FIT))) for f in range(N_FIT)]))   # 走っている時の体の高さ（前と 同じ 8コマで）
    cache = {}

    def shot(pose, discs=(), **kw):
        """1コマ（絵・目の 画素・上下の ずれ）。同じ 形・同じ 土けむりは 1回 だけ 描く"""
        discs = [(round(x, 3), round(y, 3), round(r, 3)) for x, y, r in discs if r >= .6]
        key = json.dumps([pose, sorted((k, round(float(v), 4) if not isinstance(v, (str, bool)) else v) for k, v in kw.items()), discs], sort_keys=True)
        if key not in cache:
            img, R, dy, c = frame(pose, cam, ground, 'pxw', **kw)
            if discs:
                dust(img, discs)
            cache[key] = (PX.go_text(img), list(R.get('eye_px', [])), round(float(dy), 2))
            print(f'  {len(cache)}', end='\r', flush=True)
        return cache[key]

    def on_ground(pose, yaw=0.0):
        """地面に 立つ 形の カメラ（土けむりの 場所を 決める：描かない）"""
        p = bare(pose)
        c = orbit(cam, p, yaw) if yaw else cam
        return p, shifted(c, ground - max(hooves(p, c)[k][1] for k in HOOF_KEYS))

    at = lambda discs, x0: [(x0 + x, ground + y, r) for x, y, r in discs]
    p_, c_ = on_ground(PUSH)
    hv = hooves(p_, c_)
    hx_push = min(hv['HL'][0], hv['HR'][0])                                 # けり出す うしろ足
    p_, c_ = on_ground(BRAKE)
    hv = hooves(p_, c_)
    hx_brake, fx_brake = min(hv['HL'][0], hv['HR'][0]), min(hv['FL'][0], hv['FR'][0])
    p_, c_ = on_ground(STAND, 90)
    mx_stand = sum(v[0] for v in hooves(p_, c_).values()) / 4               # こっちを 向いて おりた 足もとの まん中

    def braked(j):
        h, f = brake_dust(j)
        return at(h, hx_brake) + at(f, fx_brake)

    def start_strip():
        """走りだし（60コマ）：かまえる → けり出す（土けむり）→ 1歩め（30コマ）→ 2歩め（21コマ）→ つぎの コマから 全速（15コマ）"""
        out = []
        for f in range(LEN['start']):
            d = at(push_dust(f), hx_push)
            if f < 9:
                pose = mix(READY, PUSH, (f + 1) / 3) if f < 2 else PUSH if f < 8 else mix(PUSH, RUN0, .5)
                out.append(shot(pose, d))
            elif f < 9 + N1:
                g = (f - 9) / N1
                out.append(shot(run_pose(g), d, dy=wave(g)))
            else:
                g = (f - 9 - N1) / N2
                out.append(shot(run_pose(g), d, dy=wave(g)))
        assert 9 + N1 + N2 == LEN['start']
        return out

    def stop_strip():
        """立ち止まる（60コマ）：すべって止まる（土けむり）→ 立って待つ（首と頭が ゆっくり 上下）→ かまえる"""
        idle = lambda f: mix(IDLE[0], IDLE[1], (1 - math.cos(2 * math.pi * (f - 13) / 27)) / 2)
        out = []
        for f in range(LEN['stop']):
            if f < 2:
                pose = mix(RUN0, BRAKE, (f + 1) / 3)
            elif f < 9:
                pose = BRAKE
            elif f < 13:
                pose = mix(BRAKE, IDLE[0], (f - 8) / 5)
            elif f < 50:
                pose = idle(f)
            elif f < READY_AT['stop']:
                pose = mix(idle(49), READY, (f - 49) / 4)
            else:
                pose = READY
            out.append(shot(pose, braked(f - 1)))
        return out

    def jump_strip():
        """ジャンプ（75コマ）：けり出す → 宙（19コマ・山なり）→ おりる（土けむり）→ こっちを 向く → 1秒 見る（まばたき）→ ななめ → かまえる"""
        out = []
        for f in range(LEN['jump']):
            kw, d = {}, []
            if f < 4:
                pose = mix(RUN0, PUSH, (f + 1) / 3) if f < 2 else PUSH
                d = at(dmove(DUST_PUSH, k=(0, .6, .85, 1.0)[f]), hx_push)
            elif f < LAND_AT:
                i = f - 4
                u = (i + 1) / (N_JUMP + 1)
                pose = mix(PUSH, TUCK, (i + 1) / 3) if i < 2 else TUCK if i < 12 else mix(TUCK, REACH, (i - 11) / 4) if i < 15 else REACH
                kw = dict(by=by0 - JUMP_H * 4 * u * (1 - u), shade=True)
                d = at(dmove(DUST_PUSH, -.3 * (i + 1), -.35 * (i + 1), 1 - .2 * (i + 1)), hx_push) if i < 4 else []
            elif f < 27:
                pose = mix(REACH, BRAKE, .5) if f == LAND_AT else BRAKE
            elif f < 31:
                k = f - 26
                pose, kw = mix(BRAKE, STAND, k / 4), dict(yaw=18.0 * k)
            elif f < 61:
                pose, kw = STAND, dict(yaw=90.0, eyes='none' if 43 <= f < 47 else 'both')
            elif f < READY_AT['jump']:
                k = f - 60
                pose, kw = mix(STAND, READY, k / 5), dict(yaw=90.0 - 18.0 * k)
            else:
                pose = READY
            out.append(shot(pose, d + braked(f - LAND_AT), **kw))
        assert 4 + N_JUMP == LAND_AT
        return out

    def spin_strip():
        """一回転（75コマ）：小さく 跳ねながら くるっと 1回転と 4分の1（23コマ）→ こっちを 向いて おりる（土けむり）→ 1秒 見る（まばたき）→ ななめ → かまえる"""
        out = []
        for f in range(LEN['spin']):
            kw = {}
            if f < LAND_AT:
                u = (f + 1) / (N_SPIN + 1)
                yaw = 450.0 * u
                pose = mix(RUN0, HOP, (f + 1) * .4) if f < 2 else HOP if f < 20 else mix(HOP, STAND, (f - 19) / 4)
                kw = dict(yaw=yaw, lift=SPIN_H * 4 * u * (1 - u), eyes=spin_eyes(yaw), shade=True)
            elif f < 58:
                pose, kw = STAND, dict(yaw=90.0, eyes='none' if 40 <= f < 44 else 'both')
            elif f < READY_AT['spin']:
                k = f - 57
                pose, kw = mix(STAND, READY, k / 5), dict(yaw=90.0 - 18.0 * k)
            else:
                pose = READY
            out.append(shot(pose, at(spin_dust(f - LAND_AT), mx_stand), **kw))
        assert N_SPIN == LAND_AT
        return out

    start = start_strip()
    strips = [('run', [shot(run_pose(f / N_RUN), dy=wave(f / N_RUN)) for f in range(N_RUN)]),      # 全速（15コマ・0.5秒）
              ('stop', stop_strip() + start), ('jump', jump_strip() + start), ('spin', spin_strip() + start)]   # できごと ＋ 走りだし（つづけて めくる）
    print(f'描いた コマ {len(cache)}・ならべる コマ {sum(len(v) for _, v in strips)}')
    frames = [fr for _, v in strips for fr, _, _ in v]
    eyes_px = [e for _, v in strips for _, e, _ in v]
    # 切りぬく所：いまの絵と ちがう所がぜんぶ入る四角（ドットを偶数にそろえる＝ページの画素が整数になる）
    diff = np.maximum.reduce([np.abs(fr - orig).max(-1) for fr in frames])
    ys, xs = np.nonzero(diff > 1e-6)
    x0, y0 = max(0, (xs.min() - 1) // 2 * 2), max(0, (ys.min() - 1) // 2 * 2)
    x1, y1 = min(PX.W, -(-(xs.max() + 2) // 2) * 2), min(PX.Hh, -(-(ys.max() + 2) // 2) * 2)
    # 上と下のふちは、ふちの上と下の行が同じ所まで広げる（ドットを大きくするとき ふちの1行が ずれても 見た目が変わらない＝土の点の行に かからない）
    while y1 < PX.Hh and not np.array_equal(orig[y1 - 1, x0:x1], orig[y1, x0:x1]):
        y1 += 2
    while y0 > 0 and not np.array_equal(orig[y0 - 1, x0:x1], orig[y0, x0:x1]):
        y0 -= 2
    cw, ch = x1 - x0, y1 - y0
    ref = PX.go_text(PX.background())                                       # 馬のいない絵
    assert np.array_equal(layered(), ref), '重ねた景色が いまの絵とちがう'
    rgba = []
    for fr, epx in zip(frames, eyes_px):                                   # 馬（土けむり・かげ）だけ。目の 画素は 背景（白い 雲）と 同じ 色でも 馬の 一部
        a = np.any(np.abs(fr - ref) > 1e-6, -1)
        for ex, ey in epx:
            a[ey, ex] = True
        rgba.append(np.dstack([fr, a.astype(np.float32)]))
    cols = max(len(v) for _, v in strips)                                   # 1段に 1つの つづき（全速・立ち止まる・ジャンプ・一回転）
    sheet = np.zeros((len(strips) * ch, cols * cw, 4), np.float32)
    it = iter(rgba)
    for r_, (_, v) in enumerate(strips):
        for c_ in range(len(v)):
            sheet[r_ * ch:(r_ + 1) * ch, c_ * cw:(c_ + 1) * cw] = next(it)[y0:y1, x0:x1]
    save_lossless_rgba(sheet, f'{out}/pixel_run.webp')                      # ドットのまま（1倍）
    save_lossless_rgba(far_sheet(), f'{out}/pixel_far.webp')
    save_lossless_rgba(near_layer(), f'{out}/pixel_near.webp')
    save_lossless(PX.upscale(orig), f'{out}/pixel_static.webp')            # 下に置く いまの絵（同じ絵・5倍・ロスなし）
    S_ = PX.SCALE
    js = dict(size=[PX.W * S_, PX.Hh * S_], cell=[int(x0 * S_), int(y0 * S_), int(cw * S_), int(ch * S_)], sheet_scale=1,
              cols=cols, rows=[[k, len(v)] for k, v in strips], run=N_RUN, ev=LEN, ready=READY_AT, land=LAND_AT,
              dy=[d for _, _, d in strips[0][1]],
              sky=[['#%02X%02X%02X' % tuple(int(round(v * 255)) for v in col), y1] for col, y1 in sky_rows()],
              far=dict(period=FAR_P, clouds=list(CLOUD_ROWS), hills=list(HILL_ROWS)))
    json.dump(js, open(f'{out}/pixel_run.json', 'w'), ensure_ascii=False)
    print(json.dumps(js, ensure_ascii=False))
    if sample:                                           # 見本：コマの シートを 15コマずつ 折って 2倍に（すき通しは 灰色）
        per = 15
        tiles = [fr[y0:y1, x0:x1] for fr in rgba]
        rows = -(-len(tiles) // per)
        sh = np.full((rows * (ch + 2), per * (cw + 2), 3), .55, np.float32)
        for i, t in enumerate(tiles):
            r_, c_ = divmod(i, per)
            cell = sh[r_ * (ch + 2):r_ * (ch + 2) + ch, c_ * (cw + 2):c_ * (cw + 2) + cw]
            cell[:] = np.where(t[..., 3:] > 0, t[..., :3], cell)
        sh = cv2.resize(sh, (sh.shape[1] * 2, sh.shape[0] * 2), interpolation=cv2.INTER_NEAREST)
        cv2.imwrite(sample, cv2.cvtColor((np.clip(sh, 0, 1) * 255 + .5).astype(np.uint8), cv2.COLOR_RGB2BGR))


if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
