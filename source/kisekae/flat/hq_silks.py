# 勝負服の 走る コマ（馬と 騎手・すき通し）：いまと 同じ 絵を 1.5倍の 細かさで
#   第4.156版（まさちゃん 2026/11/12 04:20「Aにして！」＝走る コマを 画面の 3倍に。A／B の 見くらべの 見本と 同じ 作り方）
#   3D の 絵（3倍で 描いて ぬった もの）を 1倍へ 小さく する 所を 1.5倍に。顔・もくもく・流線（SVG）は 6倍で 描いて 1.5倍へ。かげ・上下の ずれは 1.5倍の 画素で
#   python3 flat/hq_silks.py <出す フォルダ>   → silks_run_hq.webp（1.5倍）・silks_run_1x.webp（いまと 同じ 作り方：もとの 絵と 見くらべる 用）
import os, sys, json, math
import numpy as np, cv2
from PIL import Image
K = os.environ.get('HQ_K') or os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, K + '/flat'); sys.path.insert(0, K)      # HQ_K＝kisekae を まるごと 写した 作業用の フォルダ（3D の 下絵を r3d/tmp に たくさん 書く ので、写しで 走らせると リポジトリが よごれない）
import silks_banner as SB, silks_run as SR
from flat_horse import to_png
OUT = 1.5; W, Hh = SB.W, SB.Hh; W2, H2 = int(W * OUT), int(Hh * OUT); N = SR.N_FRAMES
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
info = json.load(open(K + '/silks_run.json')); x0, y0, cw, ch = info['cell']; assert info['frames'] == N


def svg_hq(parts):
    """SVG の 部品 → 1.5倍の (rgb, alpha)：SB.svg_png と 同じ 手順（4倍に 描いて 1/4 に）を 6倍 → 1.5倍で"""
    svg = f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{Hh}' viewBox='0 0 {W} {Hh}'>" + ''.join(parts) + "</svg>"
    tmp = os.path.join(SB.TMP, 'silks_overlay_hq.png')
    to_png(svg, W, Hh, tmp, scale=6)
    im = cv2.imread(tmp, cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    im = cv2.resize(im, (W2, H2), interpolation=cv2.INTER_AREA)
    a_ = im[..., 3]
    return im[..., :3][..., ::-1] / np.maximum(a_[..., None], 1e-4), a_


def stack(L, w, h):
    Cp = np.zeros((h, w, 3), np.float32); A = np.zeros((h, w), np.float32)
    for c, al in L:
        Cp = Cp * (1 - al[..., None]) + c * al[..., None]; A = A * (1 - al) + al
    return Cp, A


def shift(Cp, A, dy, w, h):
    if abs(dy) > 1e-6:
        M = np.float32([[1, 0, 0], [0, 1, dy]])
        Cp = cv2.warpAffine(Cp, M, (w, h), flags=cv2.INTER_LINEAR, borderValue=0); A = cv2.warpAffine(A, M, (w, h), flags=cv2.INTER_LINEAR, borderValue=0)
    return Cp, A


R0, rgb0, a0 = SB.rider(); cam = R0['cam']; hv0 = np.asarray(R0['hooves'], float) / R0['s']
F1, F2 = [], []
for f in range(N):
    g = f / N
    R = SB.render_toon(SR.pose_at(g), SB.BOX, W, Hh, s=3, azim=18, elev=5, name=f'silks_run{f}', head_scale=1.32, js=1.35, head_r=0.15, cam=cam)
    dbg = {}
    rgb1, a1 = SB.paint_comic(R, dict(num=1, seed=5, eye=False, mouth=False, girth=False), debug=dbg)      # girth=False：腹帯は ぬらない（第4.168版）
    col3, A3 = dbg['col3'], dbg['A3']
    a2 = cv2.resize(A3, (W2, H2), interpolation=cv2.INTER_AREA); rgb2 = np.clip(cv2.resize(col3 * A3[..., None], (W2, H2), interpolation=cv2.INTER_AREA) / np.maximum(a2[..., None], 1e-4), 0, 1); a2 = np.clip(a2, 0, 1)
    hv = np.asarray(R['hooves'], float) / R['s']; fwd = math.cos(2 * math.pi * g) > 0.3
    pf = SB.puffs(hv0, 70.0 * g, 1.0 - 0.55 * g); fc = SB.face_svg(R) + (SB.streaks(hv) if fwd else []) + SB.air_lines(R)
    # いまと 同じ 作り方（1倍）
    pr, pa = SB.svg_png(pf); fr, fa = SB.svg_png(fc)
    sh = cv2.warpAffine(a1, np.float32([[1, 0, 6], [0, 1, 5]]), (W, Hh), flags=cv2.INTER_LINEAR, borderValue=0) * 0.45
    F1.append(shift(*stack([(pr, pa), (SB.SHADOW, sh), (rgb1, a1), (fr, fa)], W, Hh), SR.bob(g), W, Hh))
    # 1.5倍
    pr, pa = svg_hq(pf); fr, fa = svg_hq(fc)
    sh = cv2.warpAffine(a2, np.float32([[1, 0, 6 * OUT], [0, 1, 5 * OUT]]), (W2, H2), flags=cv2.INTER_LINEAR, borderValue=0) * 0.45
    F2.append(shift(*stack([(pr, pa), (SB.SHADOW, sh), (rgb2, a2), (fr, fa)], W2, H2), SR.bob(g) * OUT, W2, H2))
    print('frame', f, flush=True)


def sheet(F, k, path):
    X0, Y0, CW, CH = (int(round(v * k)) for v in (x0, y0, cw, ch))
    S = np.zeros((CH, CW * N, 4), np.float32)
    for i, (Cp, A) in enumerate(F):
        c = np.where(A[..., None] > 1e-4, Cp / np.maximum(A, 1e-4)[..., None], 0)
        S[:, i * CW:(i + 1) * CW, :3] = c[Y0:Y0 + CH, X0:X0 + CW]; S[:, i * CW:(i + 1) * CW, 3] = A[Y0:Y0 + CH, X0:X0 + CW]
    u8 = (np.clip(S, 0, 1) * 255 + .5).astype(np.uint8)
    Image.fromarray(u8, 'RGBA').save(path, 'WEBP', quality=86, method=6)
    if os.environ.get('HQ_RAW', '1') != '0':
        np.save(path[:-5] + '.npy', u8)
    return os.path.getsize(path)


print('sizes', sheet(F1, 1, f'{out}/silks_run_1x.webp'), sheet(F2, OUT, f'{out}/silks_run_hq.webp'))
# WebP に する 前の 画素（.npy）も 書く（HQ_RAW=0 で 書かない）（第4.166版：コマを ならべ直す とき 描き直さなくて よい ように）
# 入れ方：python3 flat/hq_install.py silks <出す フォルダ>（手元の 絵の フォルダ ios/kisekae_blobs と 台帳へ。前の 絵は 消さない）
