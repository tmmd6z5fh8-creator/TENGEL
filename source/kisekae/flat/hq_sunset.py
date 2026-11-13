# 夕焼けの 走る コマ（馬の かげ絵・すき通し）：いまと 同じ 絵を 1.5倍の 細かさで
#   第4.156版（まさちゃん 2026/11/12 04:20「Aにして！」＝走る コマを 画面の 3倍に。A／B の 見くらべの 見本と 同じ 作り方）
#   かげ絵は 4倍で 描いた 絵（体＋たてがみ・しっぽ）を 1倍へ 小さく する 所を 1.5倍に。ふちの 光は 4倍の 絵の 上で 同じ 計算（長さを 4倍）を して から 1.5倍へ
#   python3 flat/hq_sunset.py <出す フォルダ>   → sunset_horse_hq.webp（1.5倍）・sunset_horse_1x.webp（いまと 同じ 作り方：もとの 絵と 見くらべる 用）
import os, sys, json, math
import numpy as np, cv2
K = os.environ.get('HQ_K') or os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, K + '/flat'); sys.path.insert(0, K)      # HQ_K＝kisekae を まるごと 写した 作業用の フォルダ（3D の 下絵を r3d/tmp に たくさん 書く ので、写しで 走らせると リポジトリが よごれない）
import sunset_banner as SB, sunset_run as SR
from sunset_horse import silhouette, camera, SUN, S4, over, hexc
from style2d import soft_circle
OUT = 1.5; W, Hh = SB.W, SB.Hh; W2, H2 = int(W * OUT), int(Hh * OUT); N = SR.N_FRAMES
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
info = json.load(open(K + '/sunset_run.json'))['horse']; x0, y0, cw, ch = info['cell']; assert info['frames'] == N


def rims4(A4):
    """sunset_horse.silhouette の「ふちの光」を 4倍の 絵の 上で（長さは ぜんぶ 4倍）"""
    s = S4; h, w = A4.shape
    Ab = cv2.GaussianBlur(A4, (0, 0), 1.1 * s)
    gx = cv2.Sobel(Ab, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(Ab, cv2.CV_32F, 0, 1, ksize=3)
    gm = np.sqrt(gx ** 2 + gy ** 2) + 1e-6; nx, ny = -gx / gm, -gy / gm
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    sx, sy = SUN[0] * s - xx, SUN[1] * s - yy; sd = np.sqrt(sx ** 2 + sy ** 2) + 1e-6
    face_sun = np.clip(nx * sx / sd + ny * sy / sd, 0, 1)
    band = np.clip(A4 - cv2.erode(A4, np.ones((2 * s + 1, 2 * s + 1), np.uint8)), 0, 1)
    band = np.maximum(band, np.clip(A4 - cv2.GaussianBlur(A4, (0, 0), 0.9 * s), 0, 1) * 1.5)
    near_sun = np.exp(-sd / (150.0 * s))
    rim_sun = np.clip(band * np.clip((face_sun - 0.25) / 0.75, 0, 1) ** 2.0 * near_sun * 2.2, 0, 1) * A4
    rim_top = np.clip(band * np.clip((-ny - 0.55) / 0.45, 0, 1) ** 2 * 0.6, 0, 1) * A4
    return rim_sun, rim_top


def rgba2(A, rim_sun, rim_top):
    """sunset_run.horse_rgba と 同じ 重ね方を 1.5倍の 画素で"""
    sun = soft_circle(H2, W2, SB.SUN_C[0] * OUT, SB.SUN_C[1] * OUT, SB.SUN_R * OUT, 1.2 * OUT)
    wrap = cv2.GaussianBlur(sun * (1 - A), (0, 0), 1.4 * OUT) * A
    o = []
    for bgv in (0.0, 1.0):
        img = np.full((H2, W2, 3), bgv, np.float32)
        img = over(img, hexc('#22102C'), A); img = img + wrap[..., None] * hexc('#FFC27A') * 0.42
        img = over(img, hexc('#FFB45A'), rim_sun * 0.95); img = over(img, hexc('#FF8E7A'), rim_top * 0.55); o.append(img)
    k, w = o; a = np.clip(1 - (w - k).mean(-1), 0, 1)
    return np.clip(np.where(a[..., None] > 1e-4, k / np.maximum(a[..., None], 1e-4), 0), 0, 1), a


cam = camera(W, Hh); dys = [float(v) for v in info['dy']]        # 第4.166版：上下は 台帳の 数（sunset_run.py が 決めた もの＝前の 動きの 波）。前は ここで コマから 決め直して いた（sunset_run.py と 同じ 式 だった ので 同じ 数 だった）
print('dy', [round(v, 2) for v in dys], flush=True)
F1, F2 = [], []
for f in range(N):
    g = f / N
    A, rs, rt, R = silhouette(W, Hh, pose=SR.pose_at(g), cam=SR.shifted(cam, dys[f]), phase=2 * math.pi * g, name=f'sunset_run{f}')
    F1.append(SR.horse_rgba(A, rs, rt))
    A4 = R['A4']; rs4, rt4 = rims4(A4)
    rz = lambda m: np.clip(cv2.resize(m, (W2, H2), interpolation=cv2.INTER_AREA), 0, 1)
    F2.append(rgba2(rz(A4), rz(rs4), rz(rt4)))
    print('frame', f, flush=True)


def sheet(F, k, path):
    X0, Y0, CW, CH = (int(round(v * k)) for v in (x0, y0, cw, ch))
    rgb = np.zeros((CH, CW * N, 3), np.float32); a = np.zeros((CH, CW * N), np.float32)
    for i, (c, al) in enumerate(F):
        rgb[:, i * CW:(i + 1) * CW] = c[Y0:Y0 + CH, X0:X0 + CW]; a[:, i * CW:(i + 1) * CW] = al[Y0:Y0 + CH, X0:X0 + CW]
    SR.save_rgba(path, rgb, a)
    return os.path.getsize(path)


print('sizes', sheet(F1, 1, f'{out}/sunset_horse_1x.webp'), sheet(F2, OUT, f'{out}/sunset_horse_hq.webp'))
# 入れ方：python3 flat/hq_install.py sunset <出す フォルダ>（手元の 絵の フォルダ ios/kisekae_blobs と 台帳へ。前の 絵は 消さない）
