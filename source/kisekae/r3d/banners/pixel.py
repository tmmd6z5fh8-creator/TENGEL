"""ドット絵：昔のゲームのような、コースを走る馬（156×64 で描いて 5倍）（780×320）
   python3 r3d/banners/pixel.py <出力.webp>
   （壁紙の動き（flat/pixel_run.py）のために、背景（background）・馬（horse）・字（go_text）・5倍（upscale）に分けた。
     いつもの絵は前と1バイトもちがわない）"""
import sys, os, math
import numpy as np
import cv2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from style2d import *
import horse3d as Hm

W, Hh = 156, 64
SCALE = 5
BOX = (40, 15, 110, 58)
PAL = {k: hexc(v) for k, v in dict(sky1='#29ADFF', sky2='#7FD3FF', cloud='#FFF1E8', hill='#00B543', hill2='#008751', dirt='#AB5236',
                                   dirt2='#8A3F28', rail='#FFF1E8', post='#FF004D', horse='#8A4A24', horse2='#5A2A14', mane='#1D1D1D',
                                   white='#FFF1E8', yel='#FFEC27', black='#000000').items()}
HAIR = dict(mode='flow', scale=0.25, seed=4, wind_ang=math.pi)


def background():
    """空・雲・丘・コース・ゴール板"""
    img = np.zeros((Hh, W, 3), np.float32)
    img[:] = PAL['sky1']
    img[18:40] = PAL['sky2']
    # 雲（ドット）
    for cx, cy in [(20, 9), (70, 6), (128, 11)]:
        for dx, dy, w in [(0, 0, 14), (3, -2, 8), (-2, 1, 4)]:
            img[cy + dy:cy + dy + 3, cx + dx:cx + dx + w] = PAL['cloud']
    # 丘
    for x in range(W):
        h1 = int(34 + 3 * math.sin(x / 9) + 2 * math.sin(x / 4.3))
        img[h1:40, x] = PAL['hill2'] if (x // 2 + h1) % 5 == 0 else PAL['hill']
    # コース
    img[40:64] = PAL['dirt']
    for y in range(42, 64, 3):
        for x in range((y * 7) % 6, W, 6):
            img[y, x] = PAL['dirt2']
    img[40, :] = PAL['rail']; img[39, ::4] = PAL['rail']
    img[60, :] = PAL['rail']
    # ゴール板
    img[22:40, 140] = PAL['white']; img[22:28, 136:145] = PAL['post']; img[24:26, 138:143] = PAL['white']
    return img


def camera(pose=None):
    """いまの絵のカメラ（ギャロップの馬が BOX に入る）"""
    pose = dict(Hm.GALLOP) if pose is None else pose
    return frame_horse(pose, BOX, W, Hh, facing='right', azim=4, elev=4, fov=26)


def horse(img, pose=None, cam=None, name='pix', hair=None, light=(0.3, 0.8, 0.5), eyes='near'):
    """馬（低い解像度で描いて、4色にへらす）を img に描く（その場で書きかえる）。hair：たてがみとしっぽの描き方（HAIR を上書き）
       light：明るい側の向き（カメラを馬のまわりに回すときは、光も同じだけ回す）・eyes：目の光（'near'＝手前の目・'both'＝両目（正面）・'none'＝つむる）"""
    pose = dict(Hm.GALLOP) if pose is None else pose
    e, t = camera(pose) if cam is None else cam
    R = render_horse(pose, e, t, 26, W, Hh, ss=3, name=name)
    hair_, ha = mane_tail(R, (Hh, W), '#000000', '#000000', **dict(HAIR, **(hair or {})))
    A = R['a']
    n = R['n']
    l = np.sum(n * nrm(light), -1)
    body = (A > 0.45)
    img[body & (l > 0.2)] = PAL['horse']
    img[body & (l <= 0.2)] = PAL['horse2']
    p = world_pos(R)
    legs = np.nan_to_num((p[..., 1] - R['S']['ground']) < 0.38).astype(bool) & body
    legs |= hoof_tips(p, R['S']) & body                                 # 第4.87版：宙に ある 足の ひづめも
    img[legs] = PAL['black']
    img[(ha > 0.45) & ~body] = PAL['mane']
    # 輪郭（1ドット）
    m = (body | (ha > 0.45)).astype(np.uint8)
    edge = (cv2.dilate(m, np.ones((3, 3), np.uint8)) - m).astype(bool)
    img[edge & (np.arange(Hh)[:, None] < 60)] = PAL['black']
    # 目（描いた 画素の 場所を R['eye_px'] に 残す：pixel_run.py が コマを 切りぬく ときの すき通しの 印に 使う。
    #   正面の 右目が 白い 雲の 上に 重なると「背景と 同じ 色」と 見なされて すき通しに なり、雲が 流れると 空の 青が のぞいていた
    #   （2026/10/25 まさちゃん「ドットの馬が画面側を見た時に右目が青になっている白に統一して！」））
    R['eye_px'] = []
    if eyes == 'near':
        ex, ey = R['eye']; ex, ey = int(round(ex)), int(round(ey)); img[ey, ex] = PAL['white']; R['eye_px'].append((ex, ey))
    elif eyes == 'both':
        for q in R['scene'].project(np.array(R['S']['eyes']))[0]:
            ex, ey = int(round(q[0])), int(round(q[1])); img[ey, ex] = PAL['white']; R['eye_px'].append((ex, ey))
    R['cam'] = (e, t)
    return img, R


HOOF_L = 0.34          # 黒い 足先（ひづめ）：ひづめの 先から 足に そって この m まで（地面に ついた 足は いままでの「地面から 0.38m」と ほぼ 同じ）
LEG_R = 0.075          # 足の 太さの 半分（これより 足の 線に 近い 画素だけ）


def hoof_tips(p, S):
    """ひづめの 先から 足の 線（ひづめ → つなぎ → 球節 → ひざ／飛節）に そって HOOF_L m までの 画素（第4.87版・まさちゃん
       「ドットの馬が走ると蹄が無くなる瞬間があるから直して！」：いままでは 地面から 0.38m より 下だけを 黒く したので、
       足を たたんで 宙に ある コマでは ひづめが 茶色に なって 消えていた）。z は horse3d.build と 同じ（前足 0.1395・後ろ足 0.1452）"""
    P = np.nan_to_num(p, nan=99.0)
    out = np.zeros(P.shape[:2], bool)
    for k in ('FL', 'FR', 'HL', 'HR'):
        L = S[k]
        z = L['z']
        if k[0] == 'F':
            pts = [(L['hf'], 0.1395 * z), (L['co'], 0.1395 * z), (L['ft'], 0.1395 * z), (L['kn'], 0.1442 * z)]
        else:
            pts = [(L['hf'], 0.1452 * z), (L['co'], 0.1452 * z), (L['ft'], 0.1452 * z), (L['hk'], 0.1518 * z)]
        Q = [np.array([q[0], q[1], zz], np.float32) for q, zz in pts]
        best = np.full(P.shape[:2], 9.0, np.float32)
        arc = np.full(P.shape[:2], 9.0, np.float32)
        acc = 0.0
        for a_, b_ in zip(Q, Q[1:]):
            d = b_ - a_
            L2 = float(np.dot(d, d)) or 1e-9
            t = np.clip(np.sum((P - a_) * d, -1) / L2, 0, 1)
            dist = np.linalg.norm(P - (a_ + t[..., None] * d), axis=-1)
            closer = dist < best
            best = np.where(closer, dist, best)
            arc = np.where(closer, acc + t * L2 ** .5, arc)
            acc += L2 ** .5
        out |= (best < LEG_R) & (arc < HOOF_L)
    return out


def go_text(img):
    """文字「GO!」（ドットの文字）"""
    F = {'G': ['01110', '10000', '10111', '10001', '01110'], 'O': ['01110', '10001', '10001', '10001', '01110'], '!': ['1', '1', '1', '0', '1']}
    x = 118
    for ch in 'GO!':
        g = F[ch]
        for r_, row in enumerate(g):
            for c_, v in enumerate(row):
                if v == '1':
                    img[44 + r_ * 1:45 + r_ * 1, x + c_] = PAL['yel']
        x += len(g[0]) + 1
    return img


def upscale(img):
    return cv2.resize(img, (W * SCALE, Hh * SCALE), interpolation=cv2.INTER_NEAREST)


if __name__ == '__main__':
    out = sys.argv[1]
    img = background()
    img, R = horse(img)
    go_text(img)
    save_webp(upscale(img), out, q=95)
    print(out)
