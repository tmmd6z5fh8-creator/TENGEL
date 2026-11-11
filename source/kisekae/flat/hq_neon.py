# ネオンの 走る コマ（馬と 騎手と その 光・すき通し）：いまと 同じ 絵を 1.5倍の 細かさ（iPhone の 3倍の 画面に ぴったり）で
#   第4.157版（まさちゃん 2026/11/12 04:20「Aにして！」＝走る コマを 画面の 3倍に。競馬新聞・勝負服・夕焼け〈第4.156版〉の つづき）
#   ネオンの 絵は 線と 光を 1倍の 画素の 上で 作って いる（neon_banner.compose）ので、同じ 手順を 3倍の 画素の 上で やり直して（長さ・太さ・ぼかしを ぜんぶ 3倍）から 半分に 小さく する（＝1.5倍）。
#   ・3D の 馬と 騎手は 同じ カメラ・同じ 形で 3倍の 大きさに 描く（1点 1回：半分に する ので、いまの 絵〈1倍・1点 4回〉と 同じ 細かさの ふち）
#   ・線（重なり・折れ目）は いまの 絵と 同じ はば（3画素 はなれた 点を くらべる ＝ 1倍の となりの 点）で 見つける
#   ・夜空・太陽・格子は いまの 絵（1倍）を なめらかに 広げた もの（＝いま 画面に 出て いる 見え方と 同じ：馬 だけ 高画質）。光の つぶは 絵に 入れない（ページが 動かす）
#   python3 flat/hq_neon.py <出す フォルダ>   → neon_run_hq.webp（1.5倍）
import os, sys, json, math
import numpy as np, cv2
K = os.environ.get('HQ_K') or os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, K + '/flat'); sys.path.insert(0, K)      # HQ_K＝kisekae を まるごと 写した 作業用の フォルダ（3D の 下絵を r3d/tmp に たくさん 書く ので、写しで 走らせると リポジトリが よごれない）
os.environ['NEON_NO_DUST'] = '1'
import neon_banner as NB, neon_run as NR
from neon_rider import render_rider, M_SILK, M_PANTS, M_HELMET, M_BOOT, M_CLOTH
from style2d import hexc, over, blur, soft_circle, flow, lock_poly, poly_aa
S3 = 3; OUT = 1.5; W, Hh = NB.W, NB.Hh; W3, H3 = W * S3, Hh * S3; W2, H2 = int(W * OUT), int(Hh * OUT)
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
info = json.load(open(K + '/neon_run.json')); x0, y0, cw, ch = info['cell']; N = info['frames']; dys = info['dy']; assert N == NR.N_FRAMES
half = lambda a: cv2.resize(a, (W2, H2), interpolation=cv2.INTER_AREA)


def edges_k(R, k, depth_k=0.02, crease=0.55, width=2.0):
    """style2d.edges と 同じ 線を k倍の 絵の 上で：となりの 点（＝k画素 先）と くらべる・線の 太さも k倍"""
    a, d, n = R['a'], R['d'].copy(), R['n']
    hit = d > 0; big = np.where(hit, d, 1e3)
    sil = cv2.morphologyEx((a > 0.5).astype(np.float32), cv2.MORPH_GRADIENT, np.ones((2 * k + 1, 2 * k + 1), np.uint8))
    sx = np.concatenate([big[:, k:], np.repeat(big[:, -1:], k, 1)], 1); sy = np.concatenate([big[k:], np.repeat(big[-1:], k, 0)], 0)
    dd = ((np.abs(sx - big) > depth_k * big) | (np.abs(sy - big) > depth_k * big)) & hit
    cr = ((np.sum(n * np.roll(n, -k, 1), -1) < crease) | (np.sum(n * np.roll(n, -k, 0), -1) < crease)) & hit
    m = np.clip(sil + dd + cr, 0, 1).astype(np.float32)
    if width > 1:
        kk = int(round(width)) * k
        m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kk, kk)))
    return cv2.GaussianBlur(m, (0, 0), 0.6 * k)


def compose_k(img, R, k, hair=0.0, dbg=None):
    """neon_banner.compose と 同じ 重ね方を k倍の 絵の 上で（光の つぶ は なし）"""
    Hk, Wk = R['a'].shape
    scn, J = R['scene'], R['J']
    A = np.clip(R['a'], 0, 1); mat = np.round(R['m']).astype(int)
    proj = lambda p3: scn.project(np.array([p3]))[0][0][:2]
    grad = lambda m: cv2.morphologyEx(m, cv2.MORPH_GRADIENT, np.ones((2 * k + 1, 2 * k + 1), np.uint8))
    hr = np.random.default_rng(31)
    crest = np.asarray(R['crest'], float); nC = len(crest); locks = []
    for i in range(4, nC - 8, 2):
        p = crest[i]; tg = crest[min(i + 1, nC - 1)] - crest[i - 1]
        up = math.atan2(tg[1], tg[0]) - math.pi / 2
        if math.cos(up) > 0.3:
            up += math.pi
        pts = flow(p, up - 0.7, (22 + 10 * math.sin(i / nC * math.pi)) * k, 8, wind=0.35, wind_ang=math.pi + 0.35, rng=hr, wave=1.0, phase=i + hair)
        locks.append(lock_poly(pts, 10 * k, 0.6 * k))
    th_ = np.asarray(R['tail'][0], float)
    for q in range(5):
        pts = flow(th_, math.pi + 0.55 + (q - 2) * 0.12, (54 + (2 - abs(q - 2)) * 8) * k, 14, wind=0.16, wind_ang=math.pi + 0.05, rng=hr, wave=2.2, phase=q * 0.8 + hair)
        locks.append(lock_poly(pts, (12 - abs(q - 2) * 2) * k, 0.8 * k))
    hair_a = poly_aa((Hk, Wk), locks, scale=2)
    sil = np.clip(np.maximum(A, hair_a), 0, 1)
    cols = {1: NB.HORSE, 5: NB.HORSE, 6: NB.HORSE, M_SILK: NB.SILK, M_HELMET: NB.SILK, M_PANTS: NB.PANTS, M_BOOT: NB.BOOT, M_CLOTH: NB.CLOTH}
    cimg = np.zeros((Hk, Wk, 3), np.float32); inside = A > 0.5
    for q, c in cols.items():
        cimg[(mat == q) & inside] = hexc(c)
    cimg[(hair_a > 0.5) & ~inside] = hexc(NB.HORSE)
    known = ((A > 0.5) | (hair_a > 0.5)).astype(np.uint8)
    _dist, lab = cv2.distanceTransformWithLabels(1 - known, cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    ys, xs = np.nonzero(known == 1)
    lut = np.zeros((lab.max() + 1, 3), np.float32); lut[lab[ys, xs]] = cimg[ys, xs]
    cfull = lut[lab]
    ln = edges_k(R, k, width=2.0, crease=0.62)
    mb = np.zeros((Hk, Wk), np.float32)
    for q in (M_SILK, M_PANTS, M_BOOT, M_CLOTH, M_HELMET):
        mb = np.maximum(mb, grad(((mat == q) & inside).astype(np.uint8)).astype(np.float32))
    hl = grad((hair_a > .5).astype(np.float32)) * (A < 0.5)
    line = np.clip(ln + mb * 0.9 + hl, 0, 1)
    line = cv2.GaussianBlur(line, (0, 0), 0.5 * k)
    mz = np.asarray(R['muzzle'], float)[:2]
    rein = np.zeros((Hk * 4, Wk * 4), np.float32)
    for z in (1, -1):
        h2 = proj(J[f'hand{z}'])
        mid = (h2 + mz) / 2 + np.array([0, 6.0 * k])
        curve = np.array([(1 - u) ** 2 * h2 + 2 * (1 - u) * u * mid + u ** 2 * mz for u in np.linspace(0, 1, 16)])
        cv2.polylines(rein, [(curve * 4 * 16).astype(np.int32)], False, 1.0, 5 * k, cv2.LINE_AA, shift=4)
    rein = cv2.resize(rein, (Wk, Hk), interpolation=cv2.INTER_AREA)
    img = over(img, hexc('#060312'), sil * 0.88)
    img = img + blur(sil, 10 * k)[..., None] * hexc('#4A1A8A') * 0.18
    glow_c = cfull * line[..., None]
    img = img + blur(glow_c, 6 * k) * 1.1 + blur(glow_c, 2 * k) * 0.8
    img = np.maximum(img, line[..., None] * (0.55 * cfull + 0.45))
    rc = hexc('#FFE45C')
    img = img + blur(rein, 2.5 * k)[..., None] * rc * 0.7
    img = np.maximum(img, rein[..., None] * (0.6 * rc + 0.4))
    ex, ey = np.asarray(R['eye'], float)[:2]
    img = np.maximum(img, soft_circle(Hk, Wk, ex, ey, 1.8 * k, 0.8 * k)[..., None] * hexc('#E6FDFF'))
    if dbg is not None:
        dbg['sil'] = sil
    return img


bg1 = NB.background()
bg3 = cv2.resize(bg1, (W3, H3), interpolation=cv2.INTER_LINEAR)             # 画面が 広げる のと 同じ（なめらかに）
bgc = half(np.clip(bg3, 0, 1))
R0 = NB.rider(); cam = R0['cam']                                              # いまの 絵の 馬（カメラを 決める）
X0, Y0, CW, CH = (int(v * OUT) for v in (x0, y0, cw, ch))
sheet = np.zeros((CH, CW * N, 4), np.float32)
for f in range(N):
    g = f / N
    R = render_rider(NB.BOX, W3, H3, azim=55, elev=6, ss=1, name=f'neon_hq{f}', js=1.15, pose=NR.pose_at(g), cam=NR.shifted(cam, dys[f]))
    dbg = {}
    frc = half(np.clip(compose_k(bg3.copy(), R, S3, hair=2 * math.pi * g, dbg=dbg), 0, 1))
    sil = half(np.clip(dbg['sil'], 0, 1))
    dpos = (frc - bgc).max(-1) * 255
    a = np.maximum(np.clip((dpos - 1.5) / 22.5, 0, 1), np.clip(sil * 1.6, 0, 1)).astype(np.float32)
    a = np.maximum(a, cv2.blur(a, (3, 3)) * 0.999)
    sheet[:, f * CW:(f + 1) * CW, :3] = frc[Y0:Y0 + CH, X0:X0 + CW]; sheet[:, f * CW:(f + 1) * CW, 3] = a[Y0:Y0 + CH, X0:X0 + CW]
    print('frame', f, 'dy', dys[f], flush=True)
NR.save_rgba(f'{out}/neon_run_hq.webp', sheet[..., :3], sheet[..., 3], q=90)
print('size', os.path.getsize(f'{out}/neon_run_hq.webp'), sheet.shape)
# 入れ方：python3 flat/hq_install.py neon <出す フォルダ>（手元の 絵の フォルダ ios/kisekae_blobs と 台帳へ。前の 絵は 消さない）
