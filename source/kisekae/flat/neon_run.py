"""ネオンの壁紙の動き（まさちゃんの指定「常に走っている、10秒に一回流れ星が背景に通る」）：走るコマ
   - いまの絵と同じネオンの馬と騎手（neon_rider・同じカメラ・同じ線と光の色）を、ギャロップの1回分（N_FRAMES コマ）で描く。
     足の動きは海の馬と同じ（flat/sea_run.py の F_KEYS・H_KEYS・LEG_OFF：うしろの奥 → うしろの手前 → 前の奥 → 前の手前 → 4本とも宙）。
     体の傾き・首・頭は いまの絵の形を中心に少しゆれ、たてがみとしっぽは波打つ（1回で1周）
   - コマごとに、地面についているひづめの高さをそろえる（カメラを上下にずらして描く）。宙のコマは前後を結んだ山なり・上下は なめらかに
   - 夜空・太陽・格子・星は いまの絵と同じ。馬が動く所だけを切りぬいて横に並べた1まい（neon_run.webp・馬と騎手と その光だけの すき通し）。
     うしろの光のつぶは 別の 絵（neon_dust.webp・足す光）と きらめく 粒（neon_run.json の dust.sparks）で、ページが 動かす（2026/10/25〜）。
     ページでは いまの絵（光のつぶなし）の同じ場所に 光のつぶ → コマ（steps）の 順で 重ねる（neon_wall.py）
   python3 flat/neon_run.py <出力フォルダ>  → neon_run.webp・neon_run.json（切りぬく場所・コマ数・上下）（sdfr がいる。1コマ約8秒）"""
import sys, os, math, json
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ['NEON_NO_DUST'] = '1'   # 光のつぶは 絵に 入れない（別の 層：neon_dust.webp と きらめく 粒。2026/10/25 まさちゃん「小さな光は常にキラキラと光りながら動いているようにして！」）
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
    frames, sils = [], []
    for f in range(N_FRAMES):
        g = f / N_FRAMES
        R = NB.rider(pose_at(g), shifted(cam, dys[f]), name=f'neon_run{f}')
        dbg = {}
        frames.append(NB.compose(bg.copy(), R, hip=hip0, hair=2 * math.pi * g, dbg=dbg))
        sils.append(np.clip(dbg['sil'], 0, 1))                           # 馬と 騎手の 形（体の 中は 暗い 塗り＝背景と 近い 色でも 不透明に する ため）
        print('frame', f, 'dy', round(dys[f], 2), flush=True)
    # 切りぬく所：いまの絵と ちがう所がぜんぶ入る四角（偶数にそろえる）
    diff = np.maximum.reduce([np.abs(np.clip(fr, 0, 1) - np.clip(orig, 0, 1)).max(-1) for fr in frames])
    ys, xs = np.nonzero(diff > 1.5 / 255)
    x0, y0 = max(0, (xs.min() - 4) // 2 * 2), max(0, (ys.min() - 4) // 2 * 2)
    x1, y1 = min(NB.W, -(-(xs.max() + 5) // 2) * 2), min(NB.Hh, -(-(ys.max() + 5) // 2) * 2)
    cw, ch = x1 - x0, y1 - y0
    # コマは 馬と 騎手（と その光）だけの すき通しの シート：背景（光のつぶなし）と どれだけ ちがうかで すき通しを 決める
    #   （明るい 差：1.5/255 で 0 → 24/255 で 1。体と 騎手の 形（sil）の 中は 1（暗い 塗りが 床の 色と 近くても 不透明）・まわりの うすい 光は うすく＝下の 光のつぶが 透けて 見える。0/1 だと うすい 光の 所まで
    #    不透明に なって、馬の まわりの 広い 四角で つぶが 消えていた）。
    # 下の 止まった絵（光のつぶなし）→ 光のつぶの 層 → このシート の 順に 重ねると、いまの絵と ほぼ 同じ 見た目で 光のつぶだけ 動かせる
    bgc = np.clip(bg, 0, 1)
    sheet = np.zeros((ch, cw * N_FRAMES, 4), np.float32)
    for i, (fr, sil) in enumerate(zip(frames, sils)):
        frc = np.clip(fr, 0, 1)
        dpos = (frc - bgc).max(-1) * 255                                   # 背景より 明るい（線・光）
        a = np.maximum(np.clip((dpos - 1.5) / 22.5, 0, 1), np.clip(sil * 1.6, 0, 1)).astype(np.float32)   # 体（形の 中）は 不透明・光は なだらか
        a = np.maximum(a, cv2.blur(a, (3, 3)) * 0.999)                     # 1画素の 穴を うめる
        sheet[:, i * cw:(i + 1) * cw, :3] = frc[y0:y1, x0:x1]
        sheet[:, i * cw:(i + 1) * cw, 3] = a[y0:y1, x0:x1]
    save_rgba(f'{out}/neon_run.webp', sheet[..., :3], sheet[..., 3], q=90)
    # 光のつぶの 層（足す光：mix-blend-mode:plus-lighter で 重ねる → いまの絵と 同じ）：つぶの ある 所だけ 切りぬく
    L = np.clip(NB.dust_light(hip0), 0, 1)
    la = L.max(-1)
    ys, xs = np.nonzero(la > 1 / 255)
    dx0, dy0 = max(0, (xs.min() - 4) // 2 * 2), max(0, (ys.min() - 4) // 2 * 2)
    dx1, dy1 = min(NB.W, -(-(xs.max() + 5) // 2) * 2), min(NB.Hh, -(-(ys.max() + 5) // 2) * 2)
    lrgb = np.where(la[..., None] > 1e-6, L / np.maximum(la[..., None], 1e-6), 0)
    save_rgba(f'{out}/neon_dust.webp', lrgb[dy0:dy1, dx0:dx1], la[dy0:dy1, dx0:dx1], q=92)
    # きらめく 粒：つぶの うち 明るくて 大きい もの（上から 44こ）。x・y は 絵の 画素
    parts = NB.dust_particles(hip0)
    parts = sorted(parts, key=lambda t: -(t[5] * (t[3] if t[2] == 'dot' else 1.2)))[:44]
    sparks = [[round(x, 1), round(y, 1), ci, round(w, 2), round(size if kind == 'dot' else 1.3, 2)] for x, y, kind, size, ci, w in parts]
    info = dict(size=[NB.W, NB.Hh], cell=[int(x0), int(y0), int(cw), int(ch)], frames=N_FRAMES, dy=[round(v, 2) for v in dys],
                hip=[round(float(hip0[0]), 2), round(float(hip0[1]), 2)], dust=dict(box=[int(dx0), int(dy0), int(dx1 - dx0), int(dy1 - dy0)], cols=list(NB.DUST_COLS), sparks=sparks))
    json.dump(info, open(f'{out}/neon_run.json', 'w'), ensure_ascii=False)
    print(json.dumps({k: v for k, v in info.items() if k != 'dust'}, ensure_ascii=False), 'dust box', info['dust']['box'], 'sparks', len(sparks))


def save_rgba(path, rgb, a, q=90):
    u8 = (np.clip(np.dstack([rgb, a[..., None]]), 0, 1) * 255 + .5).astype(np.uint8)
    cv2.imwrite(path, cv2.cvtColor(u8, cv2.COLOR_RGBA2BGRA), [cv2.IMWRITE_WEBP_QUALITY, q])


if __name__ == '__main__':
    run(sys.argv[1])
