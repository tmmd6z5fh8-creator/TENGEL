"""勝負服の壁紙の動き（まさちゃんの指定「常に走っている、背景が常に右から左に模様が動く同じ模様をリピートする」）：
   - 背景：くり返しの1まい（silks_bg.strip_svg・はば PERIOD・左はしの780は いまの絵と同じ）→ silks_tile.webp。
     ページで右から左へ流して、同じ柄をくり返す（silks_wall.py）
   - 馬と騎手：いまの絵と同じ漫画の馬（toon_rider・同じカメラ・同じ塗り）を、ギャロップ1回分 N_FRAMES コマで描く。コマ0 は いまの絵と同じ形。
     足は「のびて とぶ → 前足が おりて うしろへかく・うしろ足は たたんで前へ → 前足を たたむ・うしろ足が前へ のびる → うしろへ けって またのびる」（奥の足は少し先）。
     絵の下からはみ出さないように、足が下を向く所では ひざを まげ、体を少し上げる（1回に2回 上下）
   - うしろ足のもくもくは、いまの絵の場所から コマごとに うしろへ流れて小さくなる（コマ0 で また出る）。前足の流線は 前へのびている時だけ
   - すき通し（alpha）つきで横に並べた1まい（silks_run.webp）と silks_run.json（切りぬく場所・コマ数・上下・くり返しのはば）
   python3 flat/silks_run.py <出力フォルダ>  （sdfr がいる。1コマ約40秒）"""
import sys, os, math, json
import numpy as np
import cv2
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import silks_banner as SB
import silks_bg
from sea_run import leg_at
from flat_horse import to_png

N_FRAMES = 10
BOB = 7.0                                    # 体が上がる いちばん高い所（画素）
# 足の形のかなめ（位相 0〜1・4つの角度）。"base" は いまの絵の形（POSE）
# のびた形（base）は 0〜0.06 のあいだ そのまま（とんでいる間）。奥の足（R）は OFF だけ先に動く → コマ0 は 手前も奥も いまの絵の形
F_KEYS = [(0.0, 'base'), (0.06, 'base'), (0.18, [-62, -25, -60, -45]), (0.30, [-88, -30, -128, -145]), (0.42, [-120, -115, -150, -155]),
          (0.57, [-118, -40, -150, -170]), (0.80, [-70, -20, -30, -15])]
H_KEYS = [(0.0, 'base'), (0.06, 'base'), (0.24, [-125, -170, -120, -110]), (0.42, [-80, -150, -55, -25]), (0.60, [-55, -120, -50, -35]),
          (0.72, [-80, -140, -105, -115]), (0.86, [-122, -160, -148, -152])]
OFF = 0.06                                   # 奥の足（R）が先に動く分
BODY = dict(theta=4.0, neck=6.0, head=-4.0)  # 体の傾き・首・頭のゆれ（足をたたむ所で少し起きる）


def pose_at(g):
    P0 = SB.POSE
    w = 2 * math.pi
    k = (1 - math.cos(w * g)) / 2
    p = dict(theta=round(P0['theta'] + BODY['theta'] * k, 2), neck_rot=round(P0['neck_rot'] + BODY['neck'] * k, 2),
             head_ang=round(P0['head_ang'] + BODY['head'] * k, 2), tail=P0['tail'])
    def leg(keys, part, side, gg):
        ks = [(t, P0[part][side] if v == 'base' else v) for t, v in keys]
        return leg_at(ks, gg)
    p['fore'] = dict(L=leg(F_KEYS, 'fore', 'L', g), R=leg(F_KEYS, 'fore', 'R', g + OFF))
    p['hind'] = dict(L=leg(H_KEYS, 'hind', 'L', g), R=leg(H_KEYS, 'hind', 'R', g + OFF))
    return p


def bob(g):
    return -BOB * (1 - math.cos(4 * math.pi * g)) / 2


def tile(out):
    """背景のくり返しの1まい"""
    P, H = silks_bg.PERIOD, silks_bg.Hh
    tmp = os.path.join(SB.TMP, 'silks_tile.png')
    to_png(silks_bg.strip_svg(), P, H, tmp, scale=2)
    im = cv2.imread(tmp, cv2.IMREAD_UNCHANGED)[..., :3][..., ::-1].astype(np.float32) / 255
    im = cv2.resize(im, (P, H), interpolation=cv2.INTER_AREA)
    SB.save_webp(np.clip(im, 0, 1), f'{out}/silks_tile.webp')
    return im


def frame_rgba(f, cam, hv0):
    """1コマの馬と騎手（もくもく・かげ・顔・流線つき）：すき通しの (色×透明度, 透明度)"""
    g = f / N_FRAMES
    R, rgb, a = SB.rider(pose_at(g), cam=cam, name=f'silks_run{f}')
    hv = np.asarray(R['hooves'], float) / R['s']
    pr, pa = SB.svg_png(SB.puffs(hv0, 7.0 * f, 1.0 - 0.055 * f))                    # もくもく：いまの絵の所から うしろへ
    sh = cv2.warpAffine(a, np.float32([[1, 0, 6], [0, 1, 5]]), (SB.W, SB.Hh), flags=cv2.INTER_LINEAR, borderValue=0) * 0.45
    fwd = math.cos(2 * math.pi * g) > 0.3                                            # 前足が前へのびている時だけ流線
    fr, fa = SB.svg_png(SB.face_svg(R) + (SB.streaks(hv) if fwd else []) + SB.air_lines(R))
    Cp = np.zeros((SB.Hh, SB.W, 3), np.float32)
    A = np.zeros((SB.Hh, SB.W), np.float32)
    for c, al in [(pr, pa), (SB.SHADOW, sh), (rgb, a), (fr, fa)]:
        Cp = Cp * (1 - al[..., None]) + c * al[..., None]
        A = A * (1 - al) + al
    dy = bob(g)
    if abs(dy) > 1e-6:
        M = np.float32([[1, 0, 0], [0, 1, dy]])
        Cp = cv2.warpAffine(Cp, M, (SB.W, SB.Hh), flags=cv2.INTER_LINEAR, borderValue=0)
        A = cv2.warpAffine(A, M, (SB.W, SB.Hh), flags=cv2.INTER_LINEAR, borderValue=0)
    return Cp, A, R


def run(out):
    os.makedirs(out, exist_ok=True)
    tile(out)
    R0, rgb0, a0 = SB.rider()                                                       # いまの絵の馬（カメラを決める）
    cam = R0['cam']
    hv0 = np.asarray(R0['hooves'], float) / R0['s']
    frames = []
    for f in range(N_FRAMES):
        Cp, A, R = frame_rgba(f, cam, hv0)
        frames.append((Cp, A))
        low = float((np.asarray(R['hooves'], float) / R['s'])[:, 1].max() + bob(f / N_FRAMES))
        print('frame', f, 'low hoof', round(low, 1), flush=True)
    ys, xs = np.nonzero(np.maximum.reduce([A for _, A in frames]) > 0.003)
    x0, y0 = max(0, (xs.min() - 4) // 2 * 2), max(0, (ys.min() - 4) // 2 * 2)
    x1, y1 = min(SB.W, -(-(xs.max() + 5) // 2) * 2), min(SB.Hh, -(-(ys.max() + 5) // 2) * 2)
    cw, ch = x1 - x0, y1 - y0
    sheet = np.zeros((ch, cw * N_FRAMES, 4), np.float32)
    for i, (Cp, A) in enumerate(frames):
        c = np.where(A[..., None] > 1e-4, Cp / np.maximum(A, 1e-4)[..., None], 0)
        sheet[:, i * cw:(i + 1) * cw, :3] = c[y0:y1, x0:x1]
        sheet[:, i * cw:(i + 1) * cw, 3] = A[y0:y1, x0:x1]
    u8 = (np.clip(sheet, 0, 1) * 255 + .5).astype(np.uint8)
    Image.fromarray(u8, 'RGBA').save(f'{out}/silks_run.webp', 'WEBP', quality=86, method=6)
    info = dict(size=[SB.W, SB.Hh], period=silks_bg.PERIOD, cell=[int(x0), int(y0), int(cw), int(ch)], frames=N_FRAMES,
                dy=[round(bob(f / N_FRAMES), 2) for f in range(N_FRAMES)])
    json.dump(info, open(f'{out}/silks_run.json', 'w'), ensure_ascii=False)
    print(json.dumps(info, ensure_ascii=False))


if __name__ == '__main__':
    run(sys.argv[1])
