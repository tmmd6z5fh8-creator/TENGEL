"""競馬新聞の壁紙の動き（まさちゃんの指定「常に馬が走っている」）：
   - いまの絵と同じ墨の馬（ink_horse・同じカメラ・同じ筆のようす・同じ乱数）を、ギャロップの1回分（N_FRAMES コマ）で描く。
     足の動きは海の馬と同じ（flat/sea_run.py の F_KEYS・H_KEYS・LEG_OFF：うしろの奥 → うしろの手前 → 前の奥 → 前の手前 → 4本とも宙）。
     体の傾き・首・頭は いまの絵の馬を中心に少しゆれ、しっぽ・たてがみも少しなびく
   - コマごとに、地面についているひづめの高さをそろえる（地面は描かない）。宙のコマは前後のコマを結んだ山なり
   - 紙と字は いまの絵と同じ（news_banner.render）。馬が動く所だけを切りぬいて横に並べた1まい（news_run.webp・すき通しなし）。
     ページでは いまの絵の同じ場所に重ねて、コマを steps で送る（news_wall.py）
   python3 flat/news_run.py <出力フォルダ>  → news_run.webp・news_run.json（切りぬく場所・コマ数）（sdfr がいる。1コマ約10秒）"""
import sys, os, math, json
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import news_banner as NB
from sea_run import F_KEYS, H_KEYS, LEG_OFF, STANCE, leg_at
from ink_horse import Hm, save_webp

N_FRAMES = 10                      # ギャロップ1回のコマ数
LIFT = 8.0                         # 宙に浮くコマの いちばん高いところ（画素）
HOOF_KEYS = ('FL', 'FR', 'HL', 'HR')


def pose_at(g):
    """ギャロップの位相 g（0〜1）の墨の馬の形（右向き：手前＝L・奥＝R）。体・首・頭は いまの絵の形（POSE）を中心にゆれる"""
    leg = lambda k: leg_at(F_KEYS if k[0] == 'F' else H_KEYS, g - LEG_OFF[k])
    w = 2 * math.pi
    P0 = NB.POSE
    return dict(theta=round(P0['theta'] + 3.0 * math.cos(w * (g - 0.15)), 2), neck_rot=round(P0['neck_rot'] + 5 * math.cos(w * (g - 0.55)), 2),
                head_ang=round(P0['head_ang'] + 3 * math.sin(w * g), 2), tail=P0['tail'],
                fore=dict(L=leg('FL'), R=leg('FR')), hind=dict(L=leg('HL'), R=leg('HR')))


def look_at(g):
    """筆のようす：しっぽの向きと たてがみの長さだけ、少しなびかせる（乱数は いまの絵と同じ）"""
    w = 2 * math.pi
    return dict(NB.LOOK, tail_ang=round(NB.LOOK['tail_ang'] + 4 * math.sin(w * g - 0.6), 2), mane=round(1.0 + 0.06 * math.sin(w * g + 0.4), 3))


def hooves(R):
    """ひづめの点（1倍の画素）"""
    S, s = R['S'], R['s']
    q = R['P']([Hm.v3(S[k]['hf'], 0.155 * S[k]['z']) for k in HOOF_KEYS])[:, :2] / s
    return {k: q[i] for i, k in enumerate(HOOF_KEYS)}


def stance_legs(g):
    return [k for k in HOOF_KEYS if ((g - LEG_OFF[k]) % 1.0) < STANCE]


def run(out):
    os.makedirs(out, exist_ok=True)
    ink0, R0 = NB.ink_layer()                                             # いまの絵の馬（カメラを決める）
    cam = R0['cam']
    frames = []
    for f in range(N_FRAMES):
        g = f / N_FRAMES
        ink, R = NB.ink_layer(pose_at(g), cam, look_at(g), name=f'news_run{f}')
        hv, legs = hooves(R), stance_legs(g)
        low = max(hv[k][1] for k in legs) if legs else None
        frames.append(dict(ink=ink, low=low, legs=legs))
        print('frame', f, 'stance', legs, 'low', None if low is None else round(low, 1), flush=True)
    # 地面の高さ：地面についているコマの まん中 → そろえる。宙のコマは前後を結んだ山なり
    lows = [fr['low'] for fr in frames if fr['low'] is not None]
    ground = float(np.mean(lows))
    n = len(frames)
    for fr in frames:
        fr['dy'] = None if fr['low'] is None else ground - fr['low']
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
    # 上下は なめらかに（くり返しの2つの波に合わせる：足の形のちがいで がたがたしないように）
    ph = 2 * math.pi * np.arange(n) / n
    A = np.stack([np.ones(n), np.cos(ph), np.sin(ph), np.cos(2 * ph), np.sin(2 * ph)], 1)
    coef = np.linalg.lstsq(A, np.array([fr['dy'] for fr in frames]), rcond=None)[0]
    for fr, v in zip(frames, A @ coef):
        fr['dy_raw'], fr['dy'] = fr['dy'], float(v)
    # 切りぬく所：どのコマの墨も、いまの絵の馬も入る四角（にじみの分だけ広く・偶数にそろえる）
    boxes = []
    for ink, dy in [(ink0, 0.0)] + [(fr['ink'], fr['dy']) for fr in frames]:
        ys, xs = np.nonzero(ink > 0.004)
        boxes.append((xs.min(), ys.min() + dy, xs.max(), ys.max() + dy))
    x0 = int(math.floor(min(b[0] for b in boxes) - 6)) // 2 * 2
    y0 = int(math.floor(min(b[1] for b in boxes) - 6)) // 2 * 2
    x1 = -(-int(math.ceil(max(b[2] for b in boxes) + 6)) // 2) * 2
    y1 = -(-int(math.ceil(max(b[3] for b in boxes) + 6)) // 2) * 2
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(NB.W, x1), min(NB.Hh, y1)
    cw, ch = x1 - x0, y1 - y0
    sheet = np.zeros((ch, cw * n, 3), np.float32)
    for i, fr in enumerate(frames):
        img = NB.render(fr['ink'], fr['dy'])
        sheet[:, i * cw:(i + 1) * cw] = img[y0:y1, x0:x1]
    save_webp(sheet, f'{out}/news_run.webp', q=86)
    info = dict(size=[NB.W, NB.Hh], cell=[x0, y0, cw, ch], frames=n, dy=[round(fr['dy'], 2) for fr in frames])
    json.dump(info, open(f'{out}/news_run.json', 'w'), ensure_ascii=False)
    print(json.dumps(info, ensure_ascii=False))


if __name__ == '__main__':
    run(sys.argv[1])
