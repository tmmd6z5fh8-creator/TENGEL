# 神様極的中の 動画の さいごの「神様極的中」の 字を、まさちゃんの 3D（神速極光祭_Meshy の GLB）に 入れかえる（第4.136版・11/10 00:19）
#   まさちゃん「神様極的中の演出の最後の神様極的中の文字をこのファイルの神様極的中に入れ替えて！」
#   python3 kisekae/gk_emblem.py <いまの 動画 gk_film.mp4> <字の 絵（RGBA・GLB を 正面から 描いた もの）> <作業フォルダ> <出す master.mp4>
#   ・動画の 8.63秒（コマ 260）から 前の 横長の 字が ドーンと 出る → 同じ 時刻・同じ 大きく なり方で 新しい 字（ほぼ 正方形）を 出す
#   ・前の 字は 消す（新しい 字に かくれない はしは まわりの 光の 筋で うめる：cv2.inpaint）・字の うしろに 金色の 後光
#   ・字の 上：光の すじ（2回）・極 の 虹の 光（ゆっくり）・宝石の きらめき・ドーンの 光の 輪（どれも 弱く：点めつの きまり 1秒に 3回まで／画面の 1割）
#   ・字の 絵と まさちゃんの GLB は リポジトリに 入れない（作業フォルダ）。できた master を build_fx_films.py の GK_MASTER に
import os, subprocess, sys
import numpy as np
import cv2

SRC, EMB, WORK, OUT = sys.argv[1:5]
FPS, W, H = 30, 780, 1688
START, LAST = 260, 361            # コマの 番号（1から：ffmpeg の f%03d）。260＝8.63秒（前の 字が 出る）
CX, CY = 390.0, 712.0             # 字の まん中
EW = 760.0                        # 字の はば（大きく なった あと）
SCALE = {260: .40, 261: .55, 262: .70, 263: .82, 264: .92, 265: .98, 266: 1.04, 267: 1.03, 268: 1.015, 269: 1.005}     # 266＝ドーン（8.84秒）
OLD = {260: .373, 261: .518, 262: .687, 263: .77, 264: .89, 265: .96, 266: 1.0}                                       # 前の 字の 大きさ（それ より あとは 1.04）
OLD_W, OLD_H = 800.0, 400.0
SWEEPS = ((274, 292), (322, 340))  # 光の すじ
# 宝石（字の 絵の 中の 場所：横・たての 割合）→ きらめく 時刻（コマ）
JEWELS = [((0.500, 0.086), 268), ((0.074, 0.490), 281), ((0.926, 0.490), 293), ((0.623, 0.091), 305), ((0.374, 0.909), 317),
          ((0.500, 0.901), 329), ((0.374, 0.091), 341), ((0.623, 0.909), 350)]


def load_emblem(p):
    im = cv2.imread(p, cv2.IMREAD_UNCHANGED).astype(np.float32) / 255      # BGRA
    a = im[..., 3]; ys, xs = np.nonzero(a > 0.02)
    im = im[max(0, ys.min() - 4):ys.max() + 5, max(0, xs.min() - 4):xs.max() + 5]
    im[..., :3] *= im[..., 3:4]                                              # 前もって アルファを かけた 形
    return im


def fit_jewels(E):
    """宝石の 場所を 字の 絵の 中で いちばん 明るい 所に 合わせる"""
    h, w = E.shape[:2]; lum = E[..., :3].mean(2); out = []
    for (u, v), t0 in JEWELS:
        x, y = int(u * w), int(v * h); r = int(0.03 * w)
        win = lum[max(0, y - r):y + r, max(0, x - r):x + r]; j = np.unravel_index(np.argmax(win), win.shape)
        out.append(((max(0, x - r) + j[1]) / w, (max(0, y - r) + j[0]) / h, t0))
    return out


def place(E, s):
    """字を 大きさ s で まん中に 置いた（W×H の）前もって かけた 色と アルファ"""
    h, w = E.shape[:2]; ew = EW * s; eh = ew * h / w
    sw, sh = max(2, int(round(ew))), max(2, int(round(eh)))
    R = cv2.resize(E, (sw, sh), interpolation=cv2.INTER_AREA if sw < w else cv2.INTER_CUBIC)
    x0 = int(round(CX - sw / 2)); y0 = int(round(CY - sh / 2))
    C = np.zeros((H, W, 4), np.float32)
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + sw), min(H, y0 + sh)
    C[ya:yb, xa:xb] = R[ya - y0:yb - y0, xa - x0:xb - x0]
    return C, (x0, y0, sw, sh)


def supere(s, ax=0.56, by=0.62, p=4.0):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a = ax * OLD_W * s; b = by * OLD_H * s
    return (np.abs((xx - CX) / a) ** p + np.abs((yy - CY) / b) ** p) <= 1.0


def star(size, inten):
    """4本の 光の きらめき（小さい 絵）"""
    n = int(size * 2) | 1; c = n // 2; yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) - c
    r = np.sqrt(xx ** 2 + yy ** 2) + 1e-6
    core = np.exp(-(r / (size * 0.08)) ** 2)
    rays = np.exp(-np.abs(xx) / (size * 0.025)) * np.exp(-np.abs(yy) / (size * 0.42)) + np.exp(-np.abs(yy) / (size * 0.025)) * np.exp(-np.abs(xx) / (size * 0.42))
    d1 = (xx + yy) / np.sqrt(2); d2 = (xx - yy) / np.sqrt(2)
    diag = 0.45 * (np.exp(-np.abs(d1) / (size * 0.02)) * np.exp(-np.abs(d2) / (size * 0.22)) + np.exp(-np.abs(d2) / (size * 0.02)) * np.exp(-np.abs(d1) / (size * 0.22)))
    return np.clip(core + 0.8 * rays + diag, 0, 1.5) * inten


def add_at(img, spr, x, y, col):
    n = spr.shape[0]; c = n // 2; x0, y0 = int(round(x)) - c, int(round(y)) - c
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + n), min(H, y0 + n)
    if xa >= xb or ya >= yb: return
    img[ya:yb, xa:xb] += spr[ya - y0:yb - y0, xa - x0:xb - x0, None] * np.asarray(col, np.float32)


def main():
    fr = os.path.join(WORK, 'frames_src'); fo = os.path.join(WORK, 'frames_new')
    os.makedirs(fr, exist_ok=True); os.makedirs(fo, exist_ok=True)
    if not os.path.exists(os.path.join(fr, 'f%03d.png' % LAST)):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', SRC, '-vsync', '0', os.path.join(fr, 'f%03d.png')], check=True)
    E = load_emblem(EMB); jw = fit_jewels(E)
    # 極（虹色）の ところ：緑〜青〜紫の 色 と その まわり
    hsv = cv2.cvtColor((np.clip(E[..., :3] / np.maximum(E[..., 3:4], 1e-4), 0, 1) * 255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
    rb = (hsv[..., 0] > 32) & (hsv[..., 0] < 165) & (hsv[..., 1] > 90) & (hsv[..., 2] > 70) & (E[..., 3] > 0.5)
    ys, xs = np.nonzero(rb); kb = (xs.min(), ys.min(), xs.max(), ys.max())
    K = np.zeros(E.shape[:2], np.float32); K[kb[1]:kb[3], kb[0]:kb[2]] = 1; K = cv2.GaussianBlur(K, (0, 0), E.shape[1] * 0.02) * E[..., 3]
    Kc = E[..., :3] * K[..., None]                                   # 極の まわりの 色（光らせる 元）
    gold = np.clip((E[..., :3].mean(2) / np.maximum(E[..., 3], 1e-4) - 0.42) * 3, 0, 1) * E[..., 3]    # 明るい 金の ところ（光の すじ）
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rr = np.sqrt((xx - CX) ** 2 + (yy - CY) ** 2)
    halo_col = np.array([0.70, 0.92, 1.0], np.float32)             # BGR：あたたかい 金白
    for f in range(1, LAST + 1):
        src = os.path.join(fr, 'f%03d.png' % f); dst = os.path.join(fo, 'f%03d.png' % f)
        if f < START:
            if not os.path.exists(dst): os.link(src, dst) if os.stat(fr).st_dev == os.stat(fo).st_dev else subprocess.run(['cp', src, dst], check=True)
            continue
        img = cv2.imread(src)
        t = f - 266                                                   # ドーンからの コマ
        s = SCALE.get(f, 1.0 + 0.006 * np.sin(2 * np.pi * (f - 269) / 45.0))
        so = OLD.get(f, 1.04)
        C, (x0, y0, sw, sh) = place(E, s)
        a = C[..., 3]
        # 前の 字を 消す：新しい 字で かくれない ところだけ まわりで うめる
        core = cv2.erode((a > 0.6).astype(np.uint8), np.ones((5, 5), np.uint8))
        m = (supere(so) & (core == 0)).astype(np.uint8)
        m = cv2.dilate(m, np.ones((5, 5), np.uint8))
        if m.any(): img = cv2.inpaint(img, m * 255, 7, cv2.INPAINT_TELEA)
        b = img.astype(np.float32) / 255
        # 後光（字の うしろ）：ドーンで 強く → おちついて ゆっくり ゆれる
        kh = min(1.0, max(0.0, (f - 259) / 6.0)) * (1.0 + 0.35 * np.exp(-max(0, t) / 4.0) * (t >= 0)) * (1.0 + 0.06 * np.sin(2 * np.pi * f / 36.0))
        R0 = 0.56 * EW * s
        hal = (0.62 * kh * np.exp(-1.25 * (rr / R0) ** 2))[..., None] * halo_col
        b = 1 - (1 - b) * (1 - np.clip(hal, 0, 1))
        # ドーンの 光の 輪（字の うしろ）
        if 0 <= t <= 9:
            tau = t / 9.0; rad = R0 * (0.95 + 1.3 * tau); th = 14 * (1 - tau) + 4
            ring = np.exp(-((rr - rad) / th) ** 2) * 0.55 * (1 - tau) ** 2
            b += ring[..., None] * np.array([0.55, 0.85, 1.0], np.float32)
        # 字の かげ（明るい 光の 中で ふちを 見やすく）
        sh_ = cv2.GaussianBlur(a, (0, 0), 7); sh_ = np.roll(sh_, 5, axis=0)
        b *= (1 - 0.32 * sh_)[..., None]
        # 字
        b = C[..., :3] + b * (1 - a[..., None])
        # 極の 虹の 光（ゆっくり）
        if f >= 263:
            ki = min(1.0, (f - 262) / 5.0) * (0.20 + 0.06 * np.sin(2 * np.pi * (f - 266) / 24.0)) + (0.18 * np.exp(-max(0, t) / 3.0) if t >= 0 else 0)
            Kp, _ = place(np.dstack([Kc, K]), s)
            glow = cv2.GaussianBlur(Kp[..., :3], (0, 0), 10 * s + 2)
            b += glow * ki
        # 光の すじ（金の ところだけ）
        for f0, f1 in SWEEPS:
            if f0 <= f <= f1:
                tau = (f - f0) / (f1 - f0); d = np.array([1.0, 0.55]); d /= np.linalg.norm(d)
                u = (xx - CX) * d[0] + (yy - CY) * d[1]; span = 0.62 * (sw + sh) / 2
                c0 = -span + 2 * span * tau
                band = np.exp(-((u - c0) / (0.05 * sw + 6)) ** 2) * np.sin(np.pi * tau) ** 0.5
                Gp, _ = place(np.dstack([np.repeat(gold[..., None], 3, 2), gold]), s)
                b += (band * Gp[..., 0] * 0.42)[..., None] * np.array([0.86, 0.96, 1.0], np.float32)
        # 宝石の きらめき
        for (u, v, t0) in jw:
            k = f - t0
            if 0 <= k <= 12:
                env = np.sin(np.pi * k / 12.0) ** 2
                spr = star(max(16.0, 46 * s), 0.9 * env)
                add_at(b, spr, x0 + u * sw, y0 + v * sh, (0.85, 0.97, 1.0))
        cv2.imwrite(dst, (np.clip(b, 0, 1) * 255 + 0.5).astype(np.uint8))
        if f % 20 == 0: print('コマ', f, flush=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS), '-i', os.path.join(fo, 'f%03d.png'), '-c:v', 'libx264', '-preset', 'slow', '-crf', '16',
                    '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-an', OUT], check=True)
    print('できた', OUT, flush=True)


if __name__ == '__main__':
    main()
