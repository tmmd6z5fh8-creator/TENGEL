"""夕焼けの壁紙の動き（まさちゃんの指定「常に走っている、地面の模様が動く 同じ模様をリピートする、1秒〜2秒で夕日が沈み真っ暗になる、
   1秒真っ暗で、2秒〜4秒に元の位置に夕日が戻る、10秒に一回リピートする」。馬が左向きなので 地面は左から右へ流す）：絵の部品
   - 空：いまの絵と同じ 空・夕日のまわりの光・雲の筋・鳥（夕日の丸・丘・草・馬は ぬく）→ sunset_sky.webp（780×320）
   - 夕日：いまの絵と同じ 夕日の丸（すき通し・まわりを切りぬいた四角）→ sunset_sun.webp
   - 地面：横につなげても切れ目がない 丘と草。丘の上のふちは 馬の足もとの高さで まっすぐにして、小さな波と草（いまの絵と同じ 細い草・
     ところどころ 背の高い草むら）を 780（画面の1まいぶん）で くり返す → sunset_ground.webp（すき通し）
   - 馬：いまの絵と同じ 馬のシルエット（同じカメラ・同じ たてがみとしっぽの束・夕日がわのふちの光）を、ギャロップの1回分（N_FRAMES コマ）で描いて
     横に並べた1まい（すき通し）→ sunset_horse.webp。足の動きは 海・ネオンの馬と同じ（sea_run.py の F_KEYS・H_KEYS・LEG_OFF）、体・首・頭は
     いまの絵の形を中心に少しゆれる。コマごとに 地面についているひづめの高さを そろえる（カメラを上下にずらす）。たてがみとしっぽは 1回で1周 波打つ
   - 地面の流れる速さ：地面についているひづめが うしろへ動く速さ（コマのあいだの平均）→ sunset_run.json の ground.px_per_cycle
   python3 flat/sunset_run.py <出力フォルダ>  → 上の4まい と sunset_run.json（sdfr がいる。1コマ約15秒）
   python3 flat/sunset_run.py <出力フォルダ> --check  → いまの形（POSE）で すき通しの馬を作って いまの絵の背景に重ね、いまの絵と くらべる"""
import sys, os, math, json
import numpy as np
import cv2
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sunset_banner as SB
from sunset_horse import POSE, Hm, silhouette, camera, over, hexc
from sea_run import F_KEYS, H_KEYS, LEG_OFF, STANCE, leg_at
from h3d import Scene, nrm

W, Hh = SB.W, SB.Hh
N_FRAMES = 10
LIFT = 5.0                         # 4本とも宙のコマの いちばん高いところ（画素）
FOV = 26.0
HOOF_KEYS = ('FL', 'FR', 'HL', 'HR')
GROUND_Y0 = 200                    # 地面の絵の上はし（780×320 の画素）
SUN_BOX = (448, 164, 144, 144)     # 夕日の絵の四角（x0, y0, w, h・偶数）
TALL = 9                           # 背の高い草むらの数（1まいぶん）


def pose_at(g):
    """ギャロップの位相 g（0〜1）の形。体・首・頭は いまの絵の形（POSE）を中心にゆれる"""
    leg = lambda k: leg_at(F_KEYS if k[0] == 'F' else H_KEYS, g - LEG_OFF[k])
    w = 2 * math.pi
    return dict(theta=round(POSE['theta'] + 3.0 * math.cos(w * (g - 0.15)), 2), neck_rot=round(POSE['neck_rot'] + 5 * math.cos(w * (g - 0.55)), 2),
                head_ang=round(POSE['head_ang'] + 3 * math.sin(w * g), 2), tail=POSE['tail'],
                fore=dict(L=leg('FL'), R=leg('FR')), hind=dict(L=leg('HL'), R=leg('HR')))


def hooves_px(pose, cam):
    """ひづめの点（780×320 の画素）：描かずに、骨組みとカメラだけで出す"""
    S = Hm.skeleton(pose)
    sc = Scene()
    sc.image(W, Hh, 1)
    sc.camera(np.asarray(cam[0], float), np.asarray(cam[1], float), FOV)
    q = sc.project([Hm.v3(S[k]['hf'], 0.155 * S[k]['z']) for k in HOOF_KEYS])[0]
    return {k: q[i] for i, k in enumerate(HOOF_KEYS)}


def stance_legs(g):
    return [k for k in HOOF_KEYS if ((g - LEG_OFF[k]) % 1.0) < STANCE]


def shifted(cam, dy):
    """絵の中で dy 画素 下へずれるように、カメラを上へずらす（4倍で描くので 画素は 4倍の絵の高さで はかる）"""
    e, t = (np.asarray(v, float) for v in cam)
    fw = nrm(t - e)
    rt = nrm(np.cross(fw, (0, 1, 0)))
    up = np.cross(rt, fw)
    wpp = 2 * np.linalg.norm(t - e) * math.tan(math.radians(FOV / 2)) / Hh
    d = up * dy * wpp
    return (e + d, t + d)


def ground_dy(cam):
    """コマごとの上下（地面についているひづめを そろえる・宙は山なり・2つの波で なめらかに）→ (上下, 地面の高さ)"""
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


def ground_speed(cam):
    """地面についているひづめが 1コマで うしろ（右）へ動く画素の平均 × コマ数 ＝ ギャロップ1回で 地面が流れる画素"""
    n = N_FRAMES
    hv = [hooves_px(pose_at(f / n), cam) for f in range(n)]
    d = []
    for f in range(n):
        g0, g1 = f / n, ((f + 1) % n) / n
        for k in HOOF_KEYS:
            if k in stance_legs(g0) and k in stance_legs(g1):
                d.append(hv[(f + 1) % n][k][0] - hv[f][k][0])
    return float(np.mean(d)) * n, [round(v, 2) for v in d]


def horse_rgba(A, rim_sun, rim_top):
    """いまの絵の draw() と同じ重ね方を、黒と白の上で計算して すき通しの色に（どの背景に重ねても いまの絵と同じになる）"""
    sun = SB.sun_alpha()
    wrap = cv2.GaussianBlur(sun * (1 - A), (0, 0), 1.4) * A
    out = []
    for bgv in (0.0, 1.0):
        img = np.full((Hh, W, 3), bgv, np.float32)
        img = over(img, hexc('#22102C'), A)
        img = img + wrap[..., None] * hexc('#FFC27A') * 0.42
        img = over(img, hexc('#FFB45A'), rim_sun * 0.95)
        img = over(img, hexc('#FF8E7A'), rim_top * 0.55)
        out.append(img)
    k, w = out
    a = np.clip(1 - (w - k).mean(-1), 0, 1)
    rgb = np.where(a[..., None] > 1e-4, k / np.maximum(a[..., None], 1e-4), 0)
    return np.clip(rgb, 0, 1), a


def ridge(x, base):
    """地面の上のふち（780 で くり返す小さな波）"""
    w = 2 * math.pi / W
    return base + 2.6 * np.sin(2 * w * x + 0.7) + 1.6 * np.sin(5 * w * x + 2.1) + 0.8 * np.sin(11 * w * x + 0.3)


def ground_tile(base, seed=7):
    """横につなげても切れ目がない 丘と草（すき通し・色は いまの丘と同じ）。(色, おおう量)：GROUND_Y0〜320"""
    rng = np.random.default_rng(seed)
    h = Hh - GROUND_Y0
    yy, xx = np.mgrid[GROUND_Y0:Hh, 0:W].astype(np.float32)
    hill = np.clip((yy - ridge(xx, base)) / 1.5 + .5, 0, 1)
    gr = np.zeros((h, W), np.float32)

    def blade(x, hgt, lean):
        y = float(ridge(np.float32(x), base)) + 2 - GROUND_Y0
        for ox in (-W, 0, W):                                           # 左右のはしは つなげた先にも描く（切れ目なし）
            cv2.line(gr, (int((x + ox) * 16), int(y * 16)), (int((x + ox + lean) * 16), int((y - hgt) * 16)), 1.0, 1, cv2.LINE_AA, shift=4)

    for i in range(260):                                                # いまの絵と同じ 細い草（同じ数・同じ高さ）
        x = rng.uniform(0, W)
        hgt = rng.uniform(6, 16)
        blade(x, hgt, rng.uniform(-4, 4))
    for i in range(TALL):                                               # ところどころ 背の高い草むら（流れるのが 見えやすい）
        x0 = rng.uniform(0, W)
        for j in range(int(rng.integers(4, 7))):
            blade(x0 + rng.uniform(-3, 3), rng.uniform(13, 22), rng.uniform(-7, 7))
    a = np.maximum(hill, np.clip(gr, 0, 1))
    rgb = np.ones((h, W, 3), np.float32) * hexc(SB.INK)
    return rgb, a


def save_rgba(path, rgb, a, q=90):
    u8 = (np.clip(np.dstack([rgb, a[..., None]]), 0, 1) * 255 + .5).astype(np.uint8)
    cv2.imwrite(path, cv2.cvtColor(u8, cv2.COLOR_RGBA2BGRA), [cv2.IMWRITE_WEBP_QUALITY, q])


def check(out):
    """いまの形（POSE）で すき通しの馬を作り、いまの絵の背景（馬なし）に重ねて いまの絵と くらべる"""
    os.makedirs(out, exist_ok=True)
    A, rs, rt, _ = silhouette(W, Hh)
    rgb, a = horse_rgba(A, rs, rt)
    rng = np.random.default_rng(81)
    bg = SB.sky()
    bg = over(bg, hexc(SB.INK), SB.hill_alpha())
    bg = over(bg, hexc(SB.INK), SB.grass_alpha(rng))
    img = SB.birds(rgb * a[..., None] + bg * (1 - a[..., None]))
    ref = SB.banner()
    d = np.abs(img - ref).max(-1) * 255
    print('max', round(float(d.max()), 3), 'mean', round(float(d.mean()), 4))
    SB.save_webp(img, f'{out}/check.webp')


def run(out):
    os.makedirs(out, exist_ok=True)
    cam = camera(W, Hh)                                                 # いまの絵のカメラ（うごかさない）
    dys, ground = ground_dy(cam)
    px_cycle, steps_ = ground_speed(cam)
    print('ground', round(ground, 2), 'dy', [round(v, 2) for v in dys], 'px/cycle', round(px_cycle, 1), steps_, flush=True)
    # 空・夕日・地面
    SB.save_webp(SB.birds(SB.sky(with_sun=False)), f'{out}/sunset_sky.webp')
    x0, y0, bw, bh = SUN_BOX
    sa = SB.sun_alpha()[y0:y0 + bh, x0:x0 + bw]
    save_rgba(f'{out}/sunset_sun.webp', np.ones((bh, bw, 3), np.float32) * hexc(SB.SUN_COL), sa)
    base = ground + 1.0                                                 # 地面の上のふち：地面についているひづめ（の点）の少し下
    grgb, ga = ground_tile(base)
    save_rgba(f'{out}/sunset_ground.webp', grgb, ga)
    # 馬のコマ
    frames = []
    for f in range(N_FRAMES):
        g = f / N_FRAMES
        A, rs, rt, _ = silhouette(W, Hh, pose=pose_at(g), cam=shifted(cam, dys[f]), phase=2 * math.pi * g, name=f'sunset_run{f}')
        frames.append(horse_rgba(A, rs, rt))
        print('frame', f, flush=True)
    amax = np.maximum.reduce([a for _, a in frames])
    ys, xs = np.nonzero(amax > 1 / 255)
    cx0, cy0 = max(0, (xs.min() - 4) // 2 * 2), max(0, (ys.min() - 4) // 2 * 2)
    cx1, cy1 = min(W, -(-(xs.max() + 5) // 2) * 2), min(Hh, -(-(ys.max() + 5) // 2) * 2)
    cw, ch = cx1 - cx0, cy1 - cy0
    sheet_rgb = np.zeros((ch, cw * N_FRAMES, 3), np.float32)
    sheet_a = np.zeros((ch, cw * N_FRAMES), np.float32)
    for i, (rgb, a) in enumerate(frames):
        sheet_rgb[:, i * cw:(i + 1) * cw] = rgb[cy0:cy1, cx0:cx1]
        sheet_a[:, i * cw:(i + 1) * cw] = a[cy0:cy1, cx0:cx1]
    save_rgba(f'{out}/sunset_horse.webp', sheet_rgb, sheet_a)
    info = dict(size=[W, Hh], sun=dict(box=list(SUN_BOX), center=list(SB.SUN_C), r=SB.SUN_R),
                ground=dict(y0=GROUND_Y0, base=round(base, 2), px_per_cycle=round(px_cycle, 2)),
                horse=dict(frames=N_FRAMES, cell=[int(cx0), int(cy0), int(cw), int(ch)], dy=[round(v, 2) for v in dys],
                           stance=[stance_legs(f / N_FRAMES) for f in range(N_FRAMES)]))
    json.dump(info, open(f'{out}/sunset_run.json', 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(info, ensure_ascii=False))


if __name__ == '__main__':
    if '--check' in sys.argv:
        check(sys.argv[1])
    else:
        run(sys.argv[1])
