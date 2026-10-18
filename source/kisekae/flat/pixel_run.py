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
   - 空・丘・コース・ゴール板・「GO!」は いまの絵と同じ。馬が動く所だけを切りぬいて横に並べた1まい（pixel_run.webp・ドットのまま＝1倍・
     すき通しなし・ロスなし）。ページでは いまの絵の同じ場所に重ねて、ドットは ぼかさずに大きくする（pixel_wall.py・image-rendering:pixelated）。
     下に置く いまの絵も ここで ロスなしで書き出す（pixel_static.webp・5倍：キャンバスの いまの絵は ロスありで 色のふちが少し にじむので、
     重ねた所の さかい目が見えないように そろえた）
   python3 flat/pixel_run.py <出力フォルダ> [見本PNG]  → pixel_run.webp・pixel_static.webp・pixel_run.json（切りぬく場所・コマの並び）（sdfr がいる。1分ほど）"""
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

N_RUN = 8                          # ギャロップ1回のコマ数
LIFT = 1.2                         # 走っていて4本とも宙のときに浮く高さ（ドット）
JUMP_H = 5.0                       # ジャンプの いちばん高い所（体が 走っている時より何ドット上か・耳が絵の上から はみ出さない）
SPIN_H = 2.0                       # 一回転の小さな跳ね
N_JUMP, N_SPIN = 8, 11             # ジャンプの宙のコマ・一回転のコマ（45°ずつ 0〜450°）
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


def run_dy(cam):
    """走るコマごとの上下（地面についている ひづめを そろえる・宙は山なり・2つの波で なめらかに）"""
    n = N_RUN
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
    return [float(v) for v in A @ coef], ground


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
    return img, R, dy, c


def spin_eyes(yaw):
    a = yaw % 360
    return 'both' if a == 90 else 'none' if 180 < a < 360 else 'near'


def run(out, sample=None):
    os.makedirs(out, exist_ok=True)
    cam = PX.camera()
    orig = PX.background()
    orig, _ = PX.horse(orig)
    PX.go_text(orig)
    dys, ground = run_dy(cam)
    frames, info = [], []

    def add(name, img, dy):
        frames.append(PX.go_text(img))
        info.append((name, round(dy, 2)))

    for f in range(N_RUN):                                                  # 走る
        img, R, dy, c = frame(run_pose(f / N_RUN), cam, ground, f'pxrun{f}', dy=dys[f])
        add(f'run{f}', img, dy)
    img, R, dy, c = frame(READY, cam, ground, 'pxready')                    # かまえる
    add('ready', img, dy)
    img, R, dy, c = frame(PUSH, cam, ground, 'pxpush')                      # けり出す（土けむり）
    hv = hooves({k: v for k, v in PUSH.items() if k != 'hair'}, c)
    hx = min(hv['HL'][0], hv['HR'][0])
    dust(img, [(hx + x, ground + y, r) for x, y, r in DUST_PUSH])
    add('push', img, dy)
    img, R, dy, c = frame(run_pose(0), cam, ground, 'pxdash', dy=dys[0])    # 1歩め（うしろへ流れた土けむり）
    dust(img, [(hx + x, ground + y, r) for x, y, r in DUST_DASH])
    add('dash', img, dy)
    by0 = float(np.mean([body_y(run_pose(f / N_RUN), shifted(cam, dys[f])) for f in range(N_RUN)]))   # 走っている時の体の高さ
    for i in range(N_JUMP):                                                 # ジャンプ（体が山なり・最後の2コマは おりる用意）
        u = (i + 1) / (N_JUMP + 1)
        img, R, dy, c = frame(TUCK if i < N_JUMP - 2 else REACH, cam, ground, f'pxjump{i}', by=by0 - JUMP_H * 4 * u * (1 - u), shade=True)
        add(f'jair{i}', img, dy)
    for i in range(2):                                                      # 立ち止まる（ブレーキ2コマ・土けむり。brake1 は ジャンプから おりる時にも）
        img, R, dy, c = frame(BRAKE, cam, ground, f'pxbrake{i}')
        hv = hooves({k: v for k, v in BRAKE.items() if k != 'hair'}, c)
        hx, fx = min(hv['HL'][0], hv['HR'][0]), min(hv['FL'][0], hv['FR'][0])
        dust(img, [(hx + x, ground + y, r) for x, y, r in DUST_HIND[i]])
        dust(img, [(fx + x, ground + y, r) for x, y, r in DUST_FORE[i]])
        add(f'brake{i}', img, dy)
    for i, p in enumerate(IDLE):                                            # 立って待つ（2コマ）
        img, R, dy, c = frame(p, cam, ground, f'pxstand{i}')
        add(f'stand{i}', img, dy)
    for i in range(N_SPIN):                                                 # 一回転（小さく跳ねながら 45°ずつ・こっちを向いて おりる）
        u = (i + .5) / N_SPIN
        yaw = 45 * i
        img, R, dy, c = frame(HOP, cam, ground, f'pxspin{i}', yaw=yaw, lift=SPIN_H * 4 * u * (1 - u), eyes=spin_eyes(yaw), shade=True)
        add(f'spin{i}', img, dy)
    img, R, dy, c = frame(STAND, cam, ground, 'pxsland', yaw=90, eyes='both')    # 一回転から おりる（足もとの左右に土けむり）
    hv = hooves({k: v for k, v in STAND.items() if k != 'hair'}, c)
    mx = sum(v[0] for v in hv.values()) / 4
    dust(img, [(mx + x, ground + y, r) for x, y, r in DUST_SPIN])
    add('sland', img, dy)
    img, R, dy, c = frame(STAND, cam, ground, 'pxturn', yaw=45)             # ななめ（正面 ↔ 横）
    add('turn', img, dy)
    img, R, dy, c = frame(STAND, cam, ground, 'pxlook', yaw=90, eyes='both')     # こっちを見る
    add('look', img, dy)
    img, R, dy, c = frame(STAND, cam, ground, 'pxblink', yaw=90, eyes='none')    # まばたき
    add('blink', img, dy)
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
    sheet = np.concatenate([fr[y0:y1, x0:x1] for fr in frames], 1)
    save_lossless(sheet, f'{out}/pixel_run.webp')                          # ドットのまま（1倍）
    save_lossless(PX.upscale(orig), f'{out}/pixel_static.webp')            # 下に置く いまの絵（同じ絵・5倍・ロスなし）
    S_ = PX.SCALE
    js = dict(size=[PX.W * S_, PX.Hh * S_], cell=[int(x0 * S_), int(y0 * S_), int(cw * S_), int(ch * S_)], sheet_scale=1,
              order=[k for k, _ in info], run=N_RUN, dy=[d for _, d in info])
    json.dump(js, open(f'{out}/pixel_run.json', 'w'), ensure_ascii=False)
    print(json.dumps(js, ensure_ascii=False))
    if sample:                                           # 見本：いまの絵とコマ（3倍）
        tiles = [orig] + frames
        cols = 6
        rows = -(-len(tiles) // cols)
        sh = np.ones((rows * 66, cols * 158, 3), np.float32)
        for i, t in enumerate(tiles):
            r_, c_ = divmod(i, cols)
            sh[r_ * 66:r_ * 66 + 64, c_ * 158:c_ * 158 + 156] = t
        sh = cv2.resize(sh, (sh.shape[1] * 3, sh.shape[0] * 3), interpolation=cv2.INTER_NEAREST)
        cv2.imwrite(sample, cv2.cvtColor((np.clip(sh, 0, 1) * 255 + .5).astype(np.uint8), cv2.COLOR_RGB2BGR))


if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
