"""ネオンの壁紙の動き（まさちゃんの指定「常に走っている、10秒に一回流れ星が背景に通る」）：走るコマ
   - いまの絵と同じネオンの馬と騎手（neon_rider・同じカメラ・同じ線と光の色）を、ギャロップの1回分（N_FRAMES コマ）で描く。
     足の動きは海の馬と同じ（flat/sea_run.py の F_KEYS・H_KEYS・LEG_OFF：うしろの奥 → うしろの手前 → 前の奥 → 前の手前 → 4本とも宙）。
     体の傾き・首・頭は いまの絵の形を中心に少しゆれ、たてがみとしっぽは波打つ（1回で1周）
   - コマごとに、地面についているひづめの高さをそろえる（カメラを上下にずらして描く）。宙のコマは前後を結んだ山なり・上下は なめらかに
   - 夜空・太陽・格子・星・うしろの光のつぶは いまの絵と同じ。馬が動く所だけを切りぬいて横に並べた1まい（neon_run.webp・すき通しなし）。
     ページでは いまの絵の同じ場所に重ねて、コマを steps で送る（neon_wall.py）
   python3 flat/neon_run.py <出力フォルダ>  → neon_run.webp・neon_run.json（切りぬく場所・コマ数・上下）（sdfr がいる。1コマ約8秒）"""
import sys, os, math, json
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import neon_banner as NB
from neon_rider import POSE, Hm
from sea_run import F_KEYS, H_KEYS, LEG_OFF, STANCE, leg_at
from h3d import Scene, nrm

N_FRAMES = 10
LIFT = 6.0                         # 宙に浮くコマの いちばん高いところ（画素）
HOOF_KEYS = ('FL', 'FR', 'HL', 'HR')
FOV = 26.0


def pose_at(g):
    """ギャロップの位相 g（0〜1）の形（右向き：手前＝L・奥＝R）。体・首・頭は いまの絵の形（POSE）を中心にゆれる"""
    leg = lambda k: leg_at(F_KEYS if k[0] == 'F' else H_KEYS, g - LEG_OFF[k])
    w = 2 * math.pi
    return dict(theta=round(POSE['theta'] + 3.0 * math.cos(w * (g - 0.15)), 2), neck_rot=round(POSE['neck_rot'] + 5 * math.cos(w * (g - 0.55)), 2),
                head_ang=round(POSE['head_ang'] + 3 * math.sin(w * g), 2), tail=POSE['tail'],
                fore=dict(L=leg('FL'), R=leg('FR')), hind=dict(L=leg('HL'), R=leg('HR')))


def hooves_px(pose, cam):
    """ひづめの点（1倍の画素）：描かずに、骨組みとカメラだけで出す"""
    S = Hm.skeleton(pose)
    sc = Scene()
    sc.image(NB.W, NB.Hh, 1)
    sc.camera(cam[0], cam[1], FOV)
    q = sc.project([Hm.v3(S[k]['hf'], 0.155 * S[k]['z']) for k in HOOF_KEYS])[0]
    return {k: q[i] for i, k in enumerate(HOOF_KEYS)}


def stance_legs(g):
    return [k for k in HOOF_KEYS if ((g - LEG_OFF[k]) % 1.0) < STANCE]


def shifted(cam, dy):
    """絵の中で dy 画素 下へずれるように、カメラを上へずらす"""
    e, t = (np.asarray(v, float) for v in cam)
    fw = nrm(t - e)
    rt = nrm(np.cross(fw, (0, 1, 0)))
    up = np.cross(rt, fw)
    wpp = 2 * np.linalg.norm(t - e) * math.tan(math.radians(FOV / 2)) / NB.Hh
    d = up * dy * wpp
    return (e + d, t + d)


def ground_dy(cam):
    """コマごとの上下（地面についているひづめを そろえる・宙は山なり・2つの波で なめらかに）"""
    n = N_FRAMES
    lows = []
    for f in range(n):
        g = f / n
        hv, legs = hooves_px(pose_at(g), cam), stance_legs(g)
        lows.append(max(hv[k][1] for k in legs) if legs else None)
    ground = float(np.mean([v for v in lows if v is not None]))
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


def run(out):
    os.makedirs(out, exist_ok=True)
    bg = NB.background()
    R0 = NB.rider()                                                     # いまの絵の馬（カメラ・光のつぶの中心を決める）
    cam, hip0 = R0['cam'], NB.hip_px(R0)
    orig = NB.compose(bg.copy(), R0)
    dys, ground = ground_dy(cam)
    frames = []
    for f in range(N_FRAMES):
        g = f / N_FRAMES
        R = NB.rider(pose_at(g), shifted(cam, dys[f]), name=f'neon_run{f}')
        frames.append(NB.compose(bg.copy(), R, hip=hip0, hair=2 * math.pi * g))
        print('frame', f, 'dy', round(dys[f], 2), flush=True)
    # 切りぬく所：いまの絵と ちがう所がぜんぶ入る四角（偶数にそろえる）
    diff = np.maximum.reduce([np.abs(np.clip(fr, 0, 1) - np.clip(orig, 0, 1)).max(-1) for fr in frames])
    ys, xs = np.nonzero(diff > 1.5 / 255)
    x0, y0 = max(0, (xs.min() - 4) // 2 * 2), max(0, (ys.min() - 4) // 2 * 2)
    x1, y1 = min(NB.W, -(-(xs.max() + 5) // 2) * 2), min(NB.Hh, -(-(ys.max() + 5) // 2) * 2)
    cw, ch = x1 - x0, y1 - y0
    sheet = np.zeros((ch, cw * N_FRAMES, 3), np.float32)
    for i, fr in enumerate(frames):
        sheet[:, i * cw:(i + 1) * cw] = np.clip(fr, 0, 1)[y0:y1, x0:x1]
    NB.save_webp(sheet, f'{out}/neon_run.webp', q=86)
    info = dict(size=[NB.W, NB.Hh], cell=[int(x0), int(y0), int(cw), int(ch)], frames=N_FRAMES, dy=[round(v, 2) for v in dys])
    json.dump(info, open(f'{out}/neon_run.json', 'w'), ensure_ascii=False)
    print(json.dumps(info, ensure_ascii=False))


if __name__ == '__main__':
    run(sys.argv[1])
