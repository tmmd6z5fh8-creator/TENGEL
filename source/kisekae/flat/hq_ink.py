# 水墨画の 走る コマ（2頭・紙と 山と 地面ごと・すき通しなし）：いまと 同じ 絵を 1.5倍の 細かさ（iPhone の 3倍の 画面に ぴったり）で
#   第4.157版（まさちゃん 2026/11/12 04:20「Aにして！」＝走る コマを 画面の 3倍に。競馬新聞・勝負服・夕焼け〈第4.156版〉の つづき）
#   墨の 2頭は 小さく する 前の 絵（3倍：sumi_rider.paint_sumi の debug の kk・A）から 1.5倍へ。
#   紙・山・地面の 筆・墨の しぶき・落款は いまの 絵（1倍）を なめらかに 広げた もの（＝いま 画面に 出て いる 見え方と 同じ：馬 だけ 高画質）。
#   重ねる 順は いまの 絵と 同じ（紙と 地面 → 奥の 馬 → 手前の 馬 → しぶき → 落款）
#   python3 flat/hq_ink.py <出す フォルダ>   → ink_run_hq.webp（1.5倍）・ink_run_1x.webp（いまと 同じ 作り方：もとの 絵と 見くらべる 用）
import os, sys, json, math
import numpy as np, cv2
K = os.environ.get('HQ_K') or os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, K + '/flat'); sys.path.insert(0, K)      # HQ_K＝kisekae を まるごと 写した 作業用の フォルダ（3D の 下絵を r3d/tmp に たくさん 書く ので、写しで 走らせると リポジトリが よごれない）
import sumi_banner as SB, sumi_run as SR
from sumi_rider import render_anime, paint_sumi
from style2d import save_webp, soft_circle
OUT = 1.5; W, Hh = SB.W, SB.Hh; W2, H2 = int(W * OUT), int(Hh * OUT); N = SR.N_FRAMES
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
info = json.load(open(K + '/ink_run.json')); x0, y0, cw, ch = info['cell']; assert info['frames'] == N and info['phase'] == SR.PHASE
up = lambda a: cv2.resize(a, (W2, H2), interpolation=cv2.INTER_LINEAR)        # 画面が 広げる のと 同じ（なめらかに）


def layer(h, pose=None, cam=None, name=None):
    """SB.horse_layer と 同じ ＋ 小さく する 前の 絵（3倍）から 1.5倍の (墨の 濃さ, おおう 量)"""
    bx0, by0, bx1, by1 = h['box']
    R = render_anime(pose or h['pose'], (W - bx1, by0, W - bx0, by1), W, Hh, name=name or 'sumi_' + h['name'], cam=cam)
    dbg = {}
    k1, A1 = paint_sumi(R, h, debug=dbg)
    hv = np.asarray(R['hooves'], float) / R['s']; hv[:, 0] = W - hv[:, 0]
    kk, A = dbg['kk'], dbg['A']
    assert kk.shape == (Hh * R['s'], W * R['s']), (kk.shape, R['s'])
    kA2 = cv2.resize(kk * A, (W2, H2), interpolation=cv2.INTER_AREA); A2 = cv2.resize(A, (W2, H2), interpolation=cv2.INTER_AREA)
    k2 = np.clip(kA2 / np.maximum(A2, 1e-4), 0, 1); A2 = np.clip(A2, 0, 1)
    return k1[:, ::-1], A1[:, ::-1], hv, h, R, k2[:, ::-1], A2[:, ::-1]


def shift2(a, dy):
    return cv2.warpAffine(a, np.float32([[1, 0, 0], [0, 1, dy]]), (a.shape[1], a.shape[0]), flags=cv2.INTER_LINEAR, borderValue=0)


# いまの 絵の 2頭（カメラ・地面を 決める：sumi_run.run と 同じ）
static = [layer(h) for h in SB.HORSES]
ground = [st[2] for st in static]
per = []
for (k0, A0, hv0, h, R0, _k2, _A2) in static:
    frames = []
    for f in range(N):
        g = (f / N + SR.PHASE[h['name']]) % 1.0
        k, A, hv, _h, R, k2, A2 = layer(h, SR.pose_at(g, h['pose']), R0['cam'], name=f'sumi_run_{h["name"]}{f}')
        dy = info['dy'][h['name']][f]                                            # 上下の ずれは 台帳の 数（いまの コマと 同じ）
        frames.append(dict(k=SR.shift(k, dy), A=SR.shift(A, dy), hv=hv, k2=shift2(k2, dy * OUT), A2=shift2(A2, dy * OUT)))
        print(h['name'], 'frame', f, 'dy', dy, flush=True)
    per.append((h, frames))

# 馬より 下（紙・山・地面の 筆）と 馬より 上（しぶき・落款）を 1倍で 作って 広げる
img_bg, paper, rng = SB.background()
grng = np.random.default_rng(131)
for (h, _fr), ghv in zip(per, ground):
    gy = ghv[:, 1].max() + 2.0; scl = 1.0 if h['tones'] == 'dark' else 0.8
    img_bg = SB.dry_ground(img_bg, gy, ghv[:, 0].min() - 10, ghv[:, 0].max() + 10, scl, 0.42 if h['tones'] == 'dark' else 0.26, grng)
keep = np.ones((Hh, W), np.float32)                                              # しぶき 16こ：下の 絵が のこる 割合（どれも 墨の 色で 0.85 ずつ）
for i in range(16):
    x, y = rng.uniform(150, 650), rng.uniform(40, 300)
    keep = keep * (1 - soft_circle(Hh, W, x, y, rng.uniform(0.8, 3.0), 1.0) * 0.85)
sx, sy, ss = 660, 210, 58                                                        # 落款（赤い 四角：SB.compose と 同じ 場所）
seal_a = np.zeros((Hh, W), np.float32); seal_a[sy:sy + ss, sx:sx + ss] = 1
bg2, paper2, keep2, seal2 = up(img_bg), up(paper), up(keep), up(seal_a)
sheet1 = np.zeros((ch, cw * N, 3), np.float32); sheet2 = np.zeros((int(ch * OUT), int(cw * OUT) * N, 3), np.float32)
for f in range(N):
    img1 = SB.compose([(fr['k'], fr['A'], fr['hv'], h) for (h, frames) in per for fr in [frames[f]]], ground)      # いまと 同じ 作り方（1倍）
    sheet1[:, f * cw:(f + 1) * cw] = img1[y0:y0 + ch, x0:x0 + cw]
    img = bg2.copy()
    for (h, frames) in per:                                                      # 奥 → 手前
        fr = frames[f]; col = paper2 * (1 - fr['k2'][..., None]) + SB.INK * fr['k2'][..., None]
        img = img * (1 - fr['A2'][..., None]) + col * fr['A2'][..., None]
    img = img * keep2[..., None] + SB.INK * (1 - keep2[..., None])               # しぶき
    img = img * (1 - seal2[..., None]) + up(img1) * seal2[..., None]             # 落款（いまの 絵の まま）
    sheet2[:, f * int(cw * OUT):(f + 1) * int(cw * OUT)] = np.clip(img, 0, 1)[int(y0 * OUT):int((y0 + ch) * OUT), int(x0 * OUT):int((x0 + cw) * OUT)]
save_webp(sheet1, f'{out}/ink_run_1x.webp', q=84); save_webp(sheet2, f'{out}/ink_run_hq.webp', q=84)
if os.environ.get('HQ_RAW', '1') != '0':                                                     # 第4.166版：WebP に する 前の 画素も 書く（コマを ならべ直す とき 描き直さなくて よい ように）
    np.save(f'{out}/ink_run_hq.npy', (np.clip(sheet2, 0, 1) * 255 + .5).astype(np.uint8))
print('sizes', os.path.getsize(f'{out}/ink_run_1x.webp'), os.path.getsize(f'{out}/ink_run_hq.webp'))
# 入れ方：python3 flat/hq_install.py ink <出す フォルダ>（手元の 絵の フォルダ ios/kisekae_blobs と 台帳へ。前の 絵は 消さない）
