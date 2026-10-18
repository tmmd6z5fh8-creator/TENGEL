"""水墨画の壁紙の動き（まさちゃんの指定「常に馬が走っている」）：
   - いまの絵と同じ2頭（騎手を乗せた墨の馬・同じカメラ・同じ筆・同じ乱数）を、ギャロップの1回分（N_FRAMES コマ）で描く。
     足の動きは海の馬と同じ（flat/sea_run.py の F_KEYS・H_KEYS・LEG_OFF）・体の傾き・首・頭は いまの絵の形を中心に少しゆれる。
     2頭は足の運びをずらす（PHASE：競り合っている感じ）
   - 紙・山・地面の筆・墨のしぶき・落款は いまの絵のまま（地面の筆は いまの絵のひづめで引く）。
     コマごとに、地面についているひづめを いまの絵の地面にそろえ、宙のコマは山なり、上下は なめらかに（くり返しの2つの波）
   - 2頭が動く所だけを切りぬいて横に並べた1まい（ink_run.webp・すき通しなし）。
     ページでは いまの絵の同じ場所に重ねて、コマを steps で送る（ink_wall.py）
   python3 flat/sumi_run.py <出力フォルダ>  → ink_run.webp・ink_run.json（切りぬく場所・コマ数）（sdfr がいる。1コマ約35秒）"""
import sys, os, math, json
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sumi_banner as SB
from sea_run import F_KEYS, H_KEYS, LEG_OFF, STANCE, leg_at
from style2d import save_webp

N_FRAMES = 10                      # ギャロップ1回のコマ数
LIFT = 7.0                         # 宙に浮くコマの いちばん高いところ（画素）
PHASE = dict(near=0.0, far=0.35)   # 2頭の足の運びのずれ
HOOF_KEYS = ('FL', 'FR', 'HL', 'HR')


def pose_at(g, P0):
    """ギャロップの位相 g（0〜1）の形（3Dは右向き：手前＝L・奥＝R）。体・首・頭は いまの絵の形 P0 を中心にゆれる"""
    leg = lambda k: leg_at(F_KEYS if k[0] == 'F' else H_KEYS, g - LEG_OFF[k])
    w = 2 * math.pi
    return dict(theta=round(P0['theta'] + 3.0 * math.cos(w * (g - 0.15)), 2), neck_rot=round(P0['neck_rot'] + 5 * math.cos(w * (g - 0.55)), 2),
                head_ang=round(P0['head_ang'] + 3 * math.sin(w * g), 2), tail=P0['tail'],
                fore=dict(L=leg('FL'), R=leg('FR')), hind=dict(L=leg('HL'), R=leg('HR')))


def stance_legs(g):
    return [k for k in HOOF_KEYS if ((g - LEG_OFF[k]) % 1.0) < STANCE]


def smooth_dy(dys):
    """上下のずれを なめらかに（くり返しの2つの波に合わせる）"""
    n = len(dys)
    ph = 2 * math.pi * np.arange(n) / n
    A = np.stack([np.ones(n), np.cos(ph), np.sin(ph), np.cos(2 * ph), np.sin(2 * ph)], 1)
    return A @ np.linalg.lstsq(A, np.asarray(dys, float), rcond=None)[0]


def shift(a, dy):
    return cv2.warpAffine(a, np.float32([[1, 0, 0], [0, 1, dy]]), (a.shape[1], a.shape[0]), flags=cv2.INTER_LINEAR, borderValue=0)


def run(out):
    os.makedirs(out, exist_ok=True)
    static = [SB.horse_layer(h) for h in SB.HORSES]                    # いまの絵の2頭（カメラ・地面を決める）
    ground = [st[2] for st in static]
    n = N_FRAMES
    per = []                                                           # 1頭ずつ：コマのリスト
    for (k0, A0, hv0, h, R0) in static:
        frames = []
        for f in range(n):
            g = (f / n + PHASE[h['name']]) % 1.0
            k, A, hv, _, R = SB.horse_layer(h, pose_at(g, h['pose']), R0['cam'], name=f'sumi_run_{h["name"]}{f}')
            legs = stance_legs(g)
            low = max(hv[HOOF_KEYS.index(q), 1] for q in legs) if legs else None
            frames.append(dict(k=k, A=A, hv=hv, low=low, legs=legs))
            print(h['name'], 'frame', f, 'stance', legs, 'low', None if low is None else round(low, 1), flush=True)
        gy = hv0[:, 1].max()                                           # いまの絵の地面（いちばん低いひづめ）
        for fr in frames:
            fr['dy'] = None if fr['low'] is None else gy - fr['low']
        for i, fr in enumerate(frames):
            if fr['dy'] is None:
                jp = next(j for j in range(1, n) if frames[(i - j) % n]['low'] is not None)
                jn = next(j for j in range(1, n) if frames[(i + j) % n]['low'] is not None)
                t = jp / (jp + jn)
                prev, nxt = frames[(i - jp) % n]['dy'], frames[(i + jn) % n]['dy']
                fr['dy_air'] = prev + (nxt - prev) * t - LIFT * 4 * t * (1 - t)
        for fr in frames:
            if fr['dy'] is None:
                fr['dy'] = fr.pop('dy_air')
        for fr, v in zip(frames, smooth_dy([fr['dy'] for fr in frames])):
            fr['dy'] = float(v)
            fr['k'], fr['A'] = shift(fr['k'], fr['dy']), shift(fr['A'], fr['dy'])
        per.append((h, frames, A0))
    # 切りぬく所：どのコマの2頭も、いまの絵の2頭も入る四角（少し広く・偶数にそろえる）
    masks = [A0 > 0.004 for (_, _, A0) in per] + [fr['A'] > 0.004 for (_, frames, _) in per for fr in frames]
    ys, xs = np.nonzero(np.any(np.stack(masks), 0))
    x0 = max(0, (int(xs.min()) - 6) // 2 * 2)
    y0 = max(0, (int(ys.min()) - 6) // 2 * 2)
    x1 = min(SB.W, -(-(int(xs.max()) + 7) // 2) * 2)
    y1 = min(SB.Hh, -(-(int(ys.max()) + 7) // 2) * 2)
    cw, ch = x1 - x0, y1 - y0
    sheet = np.zeros((ch, cw * n, 3), np.float32)
    for f in range(n):
        layers = [(fr['k'], fr['A'], fr['hv'], h) for (h, frames, _) in per for fr in [frames[f]]]
        img = SB.compose(layers, ground)
        sheet[:, f * cw:(f + 1) * cw] = img[y0:y1, x0:x1]
    save_webp(sheet, f'{out}/ink_run.webp', q=84)
    info = dict(size=[SB.W, SB.Hh], cell=[x0, y0, cw, ch], frames=n, phase=PHASE,
                dy={h['name']: [round(fr['dy'], 2) for fr in frames] for (h, frames, _) in per})
    json.dump(info, open(f'{out}/ink_run.json', 'w'), ensure_ascii=False)
    print(json.dumps(info, ensure_ascii=False))


if __name__ == '__main__':
    run(sys.argv[1])
