"""ドット絵の壁紙の動き（まさちゃんの指定「常に走っている、10秒に一回止まる2秒止まってまた走りだす」）：走る・止まる・立つ コマ
   - いまの絵と同じドットの馬（r3d/banners/pixel.py の horse・同じカメラ・同じ4色と1ドットのふち）を、156×64 のドットのまま描く
     ・走る：ギャロップ1回を N_RUN コマ。足の動きは海の馬と同じ（flat/sea_run.py の F_KEYS・H_KEYS・LEG_OFF）、体の傾き・首・頭は
       いまの絵の形（GALLOP）を中心に少しゆれる。地面についている ひづめの高さをそろえ（カメラを上下にずらして描く）、4本とも宙のときは少し浮く
     ・止まる：前足を前へつっぱり、うしろ足を おなかの下へ入れて すべる2コマ（ブレーキ）。ひづめの うしろに ドットの土けむり（出たて → ふくらむ）
     ・立つ：止まって立っている2コマ（首と頭が少し上下・しっぽが少しゆれる。昔のゲームの「待っている」動き）
     ・走りだす：かまえる（頭を下げて、うしろ足を おなかの下へ）→ けり出す（うしろ足で地面をけって、前が上がる・うしろに大きな土けむり）→
       1歩め（走るコマの0に、土けむりが うしろへ流れて小さくなったのを足したコマ）。ページで 1歩め・2歩めを ゆっくり → 少し速く して全速へ
   - 空・丘・コース・ゴール板・「GO!」は いまの絵と同じ。馬が動く所だけを切りぬいて横に並べた1まい（pixel_run.webp・5倍・すき通しなし）。
     ページでは いまの絵の同じ場所に重ねる（pixel_wall.py）。下に置く いまの絵も ここで ロスなしで書き出す（pixel_static.webp：
     キャンバスの いまの絵は ロスありで、色のふちが少し にじむので、重ねた所の さかい目が見えないように 両方とも ロスなしに そろえた）
   python3 flat/pixel_run.py <出力フォルダ> [見本PNG]  → pixel_run.webp・pixel_static.webp・pixel_run.json（切りぬく場所・コマの並び）（sdfr がいる。数秒）"""
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
LIFT = 1.2                         # 4本とも宙のときに浮く高さ（ドット）
HOOF_KEYS = ('FL', 'FR', 'HL', 'HR')
FOV = 26.0
G = dict(Hm.GALLOP)
# 止まる・立つ の形（右向き：手前＝L・奥＝R）。hair：たてがみとしっぽ（pixel.HAIR を上書き）
BRAKE = dict(theta=4.0, neck_rot=-4.0, head_ang=-48.0, tail=[-150, -130],          # 前足を前へつっぱり、うしろ足を おなかの下へ（すべって止まる）
             fore=dict(L=[-70, -62, -62, -50], R=[-76, -66, -66, -52]), hind=dict(L=[-50, -125, -60, -30], R=[-46, -121, -56, -28]),
             hair=dict(wind_ang=2.6, mane_len=0.85))
STAND = [dict(theta=0.0, neck_rot=2.0, head_ang=-58.0, tail=[-118, -100],
              fore=dict(L=[-125, -90, -90, -60], R=[-122, -88, -88, -58]), hind=dict(L=[-62, -118, -92, -62], R=[-66, -120, -94, -64]),
              hair=dict(wind_ang=1.9, mane_len=0.55, tail_len=0.85)),
         dict(theta=0.0, neck_rot=5.0, head_ang=-52.0, tail=[-126, -108],
              fore=dict(L=[-125, -90, -90, -60], R=[-122, -88, -88, -58]), hind=dict(L=[-62, -118, -92, -62], R=[-66, -120, -94, -64]),
              hair=dict(wind_ang=2.1, mane_len=0.55, tail_len=0.85))]
READY = dict(theta=2.0, neck_rot=-22.0, head_ang=-42.0, tail=[-140, -120],         # かまえる：頭を下げて前へ・うしろ足を おなかの下へ
             fore=dict(L=[-108, -94, -98, -72], R=[-112, -96, -100, -74]), hind=dict(L=[-48, -126, -74, -46], R=[-52, -128, -76, -48]),
             hair=dict(wind_ang=2.4, mane_len=0.7, tail_len=0.9))
PUSH = dict(theta=10.0, neck_rot=-20.0, head_ang=-40.0, tail=[-165, -150],          # けり出す：うしろ足で地面をけって前が上がる・前足は1本たたみ1本のばす
            fore=dict(L=[-118, -30, -140, -165], R=[-70, -30, -45, -30]), hind=dict(L=[-100, -136, -112, -124], R=[-94, -132, -108, -120]),
            hair=dict(wind_ang=3.0, mane_len=0.9))
DUST = '#FFF1E8', '#C2C3C7'        # 土けむりの色（白・かげの灰）
# 土けむり（ひづめの うしろ）：ブレーキの2コマ（出たて → ふくらんで少し上へ）。(ひづめからの x, 地面からの y, 半径)
DUST_HIND = ([(-6, -1.5, 2.2), (-10, -2.2, 1.8), (-7.5, -4.2, 1.3)], [(-7, -2.2, 2.7), (-11.5, -3.2, 2.3), (-15, -1.6, 1.6), (-8.5, -5.6, 1.9)])
DUST_FORE = ([(-4.5, -1.2, 1.7), (-7.5, -2, 1.3)], [(-5, -1.8, 2.1), (-8.5, -2.8, 1.7), (-6, -4.6, 1.3)])
# 走りだしの土けむり（けり出したときの うしろ足からの x）：けり出す（大きい）→ 1歩め（うしろへ流れて小さく）
DUST_PUSH = [(-4.5, -1.8, 2.6), (-9, -3, 2.4), (-13, -1.6, 1.9), (-6.5, -5.6, 2.0), (-11, -6.4, 1.3)]
DUST_DASH = [(-11, -2.4, 2.0), (-15.5, -3.6, 1.7), (-18.5, -1.8, 1.2), (-13, -6.4, 1.1)]


def run_pose(g):
    """ギャロップの位相 g（0〜1）の形。体・首・頭は いまの絵の形（GALLOP）を中心にゆれる"""
    leg = lambda k: leg_at(F_KEYS if k[0] == 'F' else H_KEYS, g - LEG_OFF[k])
    w = 2 * math.pi
    return dict(theta=round(G['theta'] + 3.0 * math.cos(w * (g - 0.15)), 2), neck_rot=round(G['neck_rot'] + 5 * math.cos(w * (g - 0.55)), 2),
                head_ang=round(G['head_ang'] + 3 * math.sin(w * g), 2), tail=G['tail'],
                fore=dict(L=leg('FL'), R=leg('FR')), hind=dict(L=leg('HL'), R=leg('HR')))


def hooves(pose, cam):
    """ひづめの点（ドット）：描かずに、骨組みとカメラだけで出す"""
    S = Hm.skeleton(pose)
    sc = Scene()
    sc.image(PX.W, PX.Hh, 1)
    sc.camera(cam[0], cam[1], FOV)
    q = sc.project([Hm.v3(S[k]['hf'], 0.155 * S[k]['z']) for k in HOOF_KEYS])[0]
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


def save_lossless(img, path):
    """WebP（ロスなし）：ドットの色がそのまま残る（ロスありだと 色のふちが にじんで、重ねた所の さかい目が見える）"""
    u8 = (np.clip(img, 0, 1) * 255 + .5).astype(np.uint8)
    cv2.imwrite(path, cv2.cvtColor(u8, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_WEBP_QUALITY, 101])     # 101＝ロスなし


def frame(pose, cam, ground, name, hair=None, dy=None):
    """1コマ：背景 → 馬 → 「GO!」。dy がなければ、いちばん低い ひづめを地面に"""
    if dy is None:
        dy = ground - max(hooves(pose, cam)[k][1] for k in HOOF_KEYS)
    img = PX.background()
    img, R = PX.horse(img, pose, shifted(cam, dy), name=name, hair=hair)
    return img, R, dy


def run(out, sample=None):
    os.makedirs(out, exist_ok=True)
    cam = PX.camera()
    orig = PX.background()
    orig, _ = PX.horse(orig)
    PX.go_text(orig)
    dys, ground = run_dy(cam)
    frames, info = [], []
    for f in range(N_RUN):
        img, R, dy = frame(run_pose(f / N_RUN), cam, ground, f'pxrun{f}', dy=dys[f])
        frames.append(PX.go_text(img))
        info.append((f'run{f}', round(dy, 2)))
    # 止まる：前足をつっぱる（2コマ：土けむりが ひづめの うしろに出て、ふくらむ）
    pb = {k: v for k, v in BRAKE.items() if k != 'hair'}
    for i in range(2):
        img, R, dy = frame(pb, cam, ground, f'pxbrake{i}', hair=BRAKE['hair'])
        hv = hooves(pb, shifted(cam, dy))
        hx, fx = min(hv['HL'][0], hv['HR'][0]), min(hv['FL'][0], hv['FR'][0])
        dust(img, [(hx + x, ground + y, r) for x, y, r in DUST_HIND[i]])
        dust(img, [(fx + x, ground + y, r) for x, y, r in DUST_FORE[i]])
        frames.append(PX.go_text(img))
        info.append((f'brake{i}', round(dy, 2)))
    for i, p in enumerate(STAND):
        ps = {k: v for k, v in p.items() if k != 'hair'}
        img, R, dy = frame(ps, cam, ground, f'pxstand{i}', hair=p['hair'])
        frames.append(PX.go_text(img))
        info.append((f'stand{i}', round(dy, 2)))
    # 走りだす：かまえる → けり出す（土けむり）→ 1歩め（走るコマの0に、うしろへ流れた土けむり）
    pr = {k: v for k, v in READY.items() if k != 'hair'}
    img, R, dy = frame(pr, cam, ground, 'pxready', hair=READY['hair'])
    frames.append(PX.go_text(img))
    info.append(('ready', round(dy, 2)))
    pp = {k: v for k, v in PUSH.items() if k != 'hair'}
    img, R, dy = frame(pp, cam, ground, 'pxpush', hair=PUSH['hair'])
    hv = hooves(pp, shifted(cam, dy))
    hx = min(hv['HL'][0], hv['HR'][0])
    dust(img, [(hx + x, ground + y, r) for x, y, r in DUST_PUSH])
    frames.append(PX.go_text(img))
    info.append(('push', round(dy, 2)))
    img, R, dy = frame(run_pose(0), cam, ground, 'pxdash', dy=dys[0])
    dust(img, [(hx + x, ground + y, r) for x, y, r in DUST_DASH])
    frames.append(PX.go_text(img))
    info.append(('dash', round(dy, 2)))
    # 切りぬく所：いまの絵と ちがう所がぜんぶ入る四角（ドットを偶数にそろえる＝ページの画素が整数になる）
    diff = np.maximum.reduce([np.abs(fr - orig).max(-1) for fr in frames])
    ys, xs = np.nonzero(diff > 1e-6)
    x0, y0 = max(0, (xs.min() - 1) // 2 * 2), max(0, (ys.min() - 1) // 2 * 2)
    x1, y1 = min(PX.W, -(-(xs.max() + 2) // 2) * 2), min(PX.Hh, -(-(ys.max() + 2) // 2) * 2)
    cw, ch = x1 - x0, y1 - y0
    sheet = np.concatenate([fr[y0:y1, x0:x1] for fr in frames], 1)
    big = cv2.resize(sheet, (sheet.shape[1] * PX.SCALE, sheet.shape[0] * PX.SCALE), interpolation=cv2.INTER_NEAREST)
    save_lossless(big, f'{out}/pixel_run.webp')
    save_lossless(PX.upscale(orig), f'{out}/pixel_static.webp')     # 下に置く いまの絵（同じ絵・ロスなし）
    S_ = PX.SCALE
    js = dict(size=[PX.W * S_, PX.Hh * S_], cell=[int(x0 * S_), int(y0 * S_), int(cw * S_), int(ch * S_)],
              order=[k for k, _ in info], run=N_RUN, dy=[d for _, d in info])
    json.dump(js, open(f'{out}/pixel_run.json', 'w'), ensure_ascii=False)
    print(json.dumps(js, ensure_ascii=False))
    if sample:                                           # 見本：いまの絵とコマ（3倍）
        tiles = [orig] + frames
        cols = 4
        rows = -(-len(tiles) // cols)
        sh = np.ones((rows * 66, cols * 158, 3), np.float32)
        for i, t in enumerate(tiles):
            r_, c_ = divmod(i, cols)
            sh[r_ * 66:r_ * 66 + 64, c_ * 158:c_ * 158 + 156] = t
        sh = cv2.resize(sh, (sh.shape[1] * 3, sh.shape[0] * 3), interpolation=cv2.INTER_NEAREST)
        cv2.imwrite(sample, cv2.cvtColor((np.clip(sh, 0, 1) * 255 + .5).astype(np.uint8), cv2.COLOR_RGB2BGR))


if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
