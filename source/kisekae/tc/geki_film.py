# 激馬熱馬（第4.175版）の 天国の 場面の 動画を 作る：天国の 絵の 上に 3D の「40000P」が 上から 降りて きて、40・00・0P を いろいろな 向きから 写す
#   まさちゃん 2026/11/15 13:56「天国のような画面に切り替わり、上から40000Pと書かれた立体の文字が降りてきて、40、00、0Pでそれぞれを色々な角度から映すカットが入って、
#     テデーンとデカ文字で40000P獲得と出てきて終わり！」「演出時に使用する背景、三枚目」「演出時に使う40000Pの3D一個目ファイル(演出は2秒程度)」・14:11「4の3Dの赤線の中だけくり抜いて！」
#   python3 -I geki_film.py <3D（くりぬいた GLB）> <天国の 絵> <出す フォルダ> [--scale 0.33] [--frames 0,9,17 | --range a b] [--sheet]
#     → <出す フォルダ>/f000.png …（1170×1842・30コマ／秒・72コマ＝2.4秒）。--sheet＝場面ごとの 見本の コマを 1まいに ならべる（小さく 作って 見る 用）
#   python3 -I geki_film.py --encode <コマの フォルダ> <出す フォルダ>
#     → tc_gk_film2.mp4（H.264・音なし）・tc_gk_end2.webp（さいごの コマ：動画が 流れない とき・演出を 控えめに する とき）
#       動画は CRF 22（はじめの 動かし方の とき：もとの コマと くらべて PSNR 42.6dB・約2.4MB。CRF 20＝43.8dB・3.0MB／24＝41.5dB・1.9MB：0.4〜0.9秒の 短い 場面なので 22 に した）
#   python3 -I geki_film.py --flash <コマの フォルダ>
#     → 動画 だけで 光の 点めつを 数える（kisekae/flash_px.py と 同じ 数え方：真っ暗 → 0.12秒で 出る → コマを 2回ずつ〈60コマ／秒〉→ さいごの コマで 止まる）。
#       動かし方を かえたら これで 数える（小さく 作った コマ〈--scale 0.2〉でも 同じ 数に なる）。アプリの 中での 数は test_tc_geki_flash.py
#   ・3D は kisekae/r3d/glb（自前の 読みこみ・描く 道具）で 1コマずつ 描く。うしろの 絵は 場面ごとに 写す 所・大きさ・ぼかしを かえる（カメラが 動いた ように 見える）
#   14:58（小さく 作った 見本を 見て）「これ40000Pの全体が見える前に、40、00、0Pのカットイン入れて！全体が見える時は背景切れてもいいからもっとアップにして迫力ある演出にして！」
#     → ぜんぶが 見える 前に カットイン 3つ（降りて くるのは 1つめの「40」の 中で 見せる）。ぜんぶが 見える 場面は、ななめ 下から 見上げて 字を 画面 いっぱいに（うしろの 絵は 切れて よい）
#   ・場面（秒）：0〜0.6「40」（左下から 見上げる：上から 降りて きて 0.33秒で 止まる）／0.6〜1.07「00」（右上から 見下ろす）／1.07〜1.5「0P」（右下から 見上げる）／
#     1.5〜2.4 ぜんぶ（すぐ 近くから 一気に 引いて ドーンと 止まる：字は 右上がりに ななめ・手前の「4」が 大きい。画面の 上 2/3 いっぱい＝下 1/3 に「40000P獲得」の 字が 入る）
#     カットは 0.43〜0.6秒 ごと（1秒に 3回 より 少ない）。1.97秒（TEXT_F）で アプリが テデーンと 字を 出す。カットの ときに 画面 ぜんぶが 白く・黒く なる コマは 入れない（明るさは 天国の 絵の まま）
#   ・光の 点めつ（1秒に 3回 まで・画面の 10%）：虹色の 字は 面ごとに 明るさが ちがう（黄＝明るい・青や 紫＝暗い）ので、字が 動くと その 所の 明るさが 何回も 上下 する。
#     はじめの 動かし方（カットインの 間に カメラが 12度 回る・着いた あと 少し 沈んで もどる）は、アプリの 中で 数えて 12.7%（動画 だけで 11.0%）＝ 決まりを こえて いた。
#     → カットインの 間は ゆっくり 寄る だけ（カメラは 4度・近さ 5%）・着いた あとの 沈みは なし に した：動画 だけで 1.7%（--flash）。向きは カットごとに かえる（左下・右上・右下）ので
#       「いろいろな 角度から 写す カット」の まま。ぜんぶが 見える 場面の 一気に 引く 動き（迫力）は そのまま（引く のは 0.3秒）
#     前の 動画（tc_gk_film.mp4・tc_gk_end.webp）は もとの フォルダに 残す（アプリには 入れない：assets_dir.superseded）
#   ・カットの 時刻（CUTS）を かえたら kisekae/tc/snd/sfx_geki.py の FILM と tc/tc_fx.js の GK も かえる
#   まさちゃんの 3D・絵・できた 動画は リポジトリに 入れない（ios/tc_assets/ は .gitignore）
import sys, os, math, time, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, '..', 'r3d', 'glb')))
import numpy as np
from PIL import Image, ImageFilter
FPS, LEN, W, H = 30, 2.4, 1170, 1842
CUT_F = (18, 32, 45)                                # カットの コマ（30コマ／秒）：「40」→「00」→「0P」→ ぜんぶ
CUTS = tuple(f / FPS for f in CUT_F)                # ＝ 0.6・1.067・1.5秒
TEXT_F = 59                                         # テデーンと「40000P獲得」の 字が 出る コマ（1.967秒：アプリが 出す。tc/tc_fx.js の GK.text）
HERO = dict(az=-42, el=-12, roll=40, fov=36, box=(0.02, 0.03, 0.98, 0.68))      # ぜんぶが 見える 場面の 止まった ときの 向き（いろいろ ためして 字が いちばん 大きく・読みやすい もの）と、字を 入れる 所（左・上・右・下）
NF = int(round(LEN * FPS))
BG_Y0 = 40                                          # 天国の 絵（941×1672）の 上から 切る 所（舞台の 形 1170:1842 に 合わせて 941×1482 を 使う）
sm = lambda x: (lambda v: v * v * (3 - 2 * v))(min(1.0, max(0.0, x)))
ease_out = lambda x: 1 - (1 - min(1.0, max(0.0, x))) ** 3
def back_out(x, c=1.4): x = min(1.0, max(0.0, x)); return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
lerp = lambda a, b, u: a + (b - a) * u


def rot_x(a): c, s = math.cos(a), math.sin(a); return np.array([[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1.0]])
def rot_y(a): c, s = math.cos(a), math.sin(a); return np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1.0]])
def rot_z(a): c, s = math.cos(a), math.sin(a); return np.array([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1.0]])
def trans(x, y, z): m = np.eye(4); m[:3, 3] = (x, y, z); return m


def orbit(target, dist, az, el):
    """まん中（target）を 見る カメラの 場所：az＝横（度・＋で 右から）・el＝たて（度・＋で 上から）"""
    a, e = math.radians(az), math.radians(el)
    return (target[0] + dist * math.sin(a) * math.cos(e), target[1] + dist * math.sin(e), target[2] + dist * math.cos(a) * math.cos(e))


def shot(t, hero):
    """t 秒の 写し方 → dict（k：場面・eye・target・fov・M：3D の 動かし方・bg：うしろの 絵 [まん中x, まん中y, 大きさ, ぼかし]・u：場面の 中の 進み 0〜1）。hero＝ぜんぶの 場面の 合わせた カメラ（Film.fit）"""
    k = sum(1 for c in CUTS if t >= c - 1e-9); t0 = 0 if k == 0 else CUTS[k - 1]; t1 = CUTS[k] if k < len(CUTS) else LEN; u = (t - t0) / (t1 - t0)
    M = np.eye(4)
    # カットインの 間の カメラ：ゆっくり 寄る だけ（横 4度・たて 1.5〜2度・近さ 5%）。速く 回すと 虹色の 面が 通る 所の 明るさが 何回も 上下 する（上の「光の 点めつ」）
    if k == 0:                                      # 「40」：左下から 見上げる。字は 上の 外から 降りて きて 止まる（0.33秒：音の ドンと 同じ 時。着いた あとは 沈まない）
        d = ease_out(u / 0.55)
        M = trans(0, 1.05 * (1 - d), 0) @ rot_x(math.radians(-16) * (1 - d))
        tg = (-0.60, 0.0, 0.0); return dict(k=k, u=u, eye=orbit(tg, lerp(2.1, 2.0, u), lerp(-40.5, -36.5, u), lerp(-23, -21.5, u)), target=tg, fov=30, M=M, bg=[lerp(0.378, 0.402, u), 0.20, 2.0, 5.0])
    if k == 1:                                      # 「00」：右上から 見下ろす
        tg = (0.0, 0.0, 0.0); return dict(k=k, u=u, eye=orbit(tg, lerp(2.12, 2.02, u), lerp(24.5, 20.5, u), lerp(34, 32, u)), target=tg, fov=30, M=M, bg=[lerp(0.532, 0.508, u), 0.78, 1.9, 5.0])
    if k == 2:                                      # 「0P」：右下から 見上げる
        tg = (0.62, 0.0, 0.0); return dict(k=k, u=u, eye=orbit(tg, lerp(2.1, 2.0, u), lerp(42.5, 38.5, u), lerp(-21, -19.5, u)), target=tg, fov=30, M=M, bg=[lerp(0.642, 0.618, u), 0.22, 2.0, 5.0])
    # ぜんぶ：すぐ 近く（字が 画面から はみ出す）から 一気に 引いて 止まる（0.3秒・少し 行きすぎて もどる）→ そのあと ごく ゆっくり 寄る
    v = t - t0; e = back_out(v / 0.3, 1.1); dr = max(0.0, v - 0.3) / (LEN - t0 - 0.3)
    az = lerp(-60, HERO['az'], e) + 0.75 * dr; el = lerp(-24, HERO['el'], e); roll = lerp(52, HERO['roll'], e) - 0.4 * dr; dist = hero['dist'] * (lerp(0.42, 1.0, e) - 0.01 * dr)
    return dict(k=k, u=u, eye=orbit(hero['target'], dist, az, el), target=hero['target'], fov=HERO['fov'], M=rot_z(math.radians(roll)), bg=[0.5, 0.40, lerp(1.9, 1.5, ease_out(v / 0.375)) - 0.03 * dr, 2.5])


class Film:
    def __init__(self, glb_path, bg_path, scale=1.0):
        from glb import load
        import raster as R
        self.R = R; self.scale = scale; self.w = int(round(W * scale / 2)) * 2; self.h = int(round(H * scale / 2)) * 2
        self.prims = load(glb_path).flatten()
        bg = Image.open(bg_path).convert('RGB'); bh = int(round(bg.width * H / W)); self.bg = bg.crop((0, BG_Y0, bg.width, BG_Y0 + bh))
        self.lights = [R.Light.key(direction=(0.25, 0.75, 0.85), color=(1.0, 0.96, 0.88), intensity=2.3, shadow=False),
                       R.Light.fill(direction=(-0.6, -0.35, 0.7), color=(1.0, 0.86, 0.74), intensity=0.75),
                       R.Light.rim(direction=(0.05, 0.55, -1.0), color=(1.0, 0.9, 0.6), intensity=2.2)]
        self.rng = np.random.default_rng(175)
        self.dust = self.rng.uniform(0, 1, (90, 6))  # きらきらの 粒（場所 x・y・大きさ・速さ・ゆれ・手前か）
        self.pts = np.concatenate([p.pos[::25] for p in self.prims]).astype(np.float64)
        self.hero = self.fit(HERO['az'], HERO['el'], HERO['roll'], HERO['fov'], HERO['box'])

    def fit(self, az, el, roll, fov, box):
        """字 ぜんぶが 画面の box（左・上・右・下：割合）に ちょうど 入る カメラ → dict（target・dist）"""
        R = self.R; P = self.pts @ rot_z(math.radians(roll))[:3, :3].T; tg = np.zeros(3); dist = 4.0
        for _ in range(60):
            cam = R.Camera.look_at(orbit(tg, dist, az, el), tg, fov_y=fov, W=self.w, H=self.h)
            q = np.c_[P, np.ones(len(P))] @ (cam.proj @ cam.view).T
            if (q[:, 3] <= 0.05).any(): dist *= 1.3; continue
            x = (q[:, 0] / q[:, 3] + 1) / 2; y = (1 - q[:, 1] / q[:, 3]) / 2; x0, x1, y0, y1 = x.min(), x.max(), y.min(), y.max()
            dist *= 1 + 0.6 * (max((x1 - x0) / (box[2] - box[0]), (y1 - y0) / (box[3] - box[1])) - 1)
            hh = dist * math.tan(math.radians(fov) / 2); cx, cy = (x0 + x1) / 2 - (box[0] + box[2]) / 2, (y0 + y1) / 2 - (box[1] + box[3]) / 2
            tg = tg + cam.inv_view[:3, 0] * cx * 2 * hh * (self.w / self.h) * 0.8 - cam.inv_view[:3, 1] * cy * 2 * hh * 0.8
        return dict(target=tuple(float(v) for v in tg), dist=float(dist), box=(float(x0), float(y0), float(x1), float(y1)))

    def back(self, s, t):
        """うしろの 絵（その 場面の 写し方で）→ (h, w, 3) 0〜1"""
        cx, cy, z, blur = s['bg']; bw, bh = self.bg.size; ww, hh = bw / z, bh / z
        x0 = min(max(cx * bw - ww / 2, 0), bw - ww); y0 = min(max(cy * bh - hh / 2, 0), bh - hh)
        im = self.bg.resize((self.w, self.h), Image.BICUBIC, box=(x0, y0, x0 + ww, y0 + hh))
        if blur > 0: im = im.filter(ImageFilter.GaussianBlur(blur * self.scale))
        return np.asarray(im, np.float32) / 255

    def stars(self, img, s, t, front):
        """きらきら（4つの 先の 星と 金の 粒）を 足す。front＝3D の 手前の 粒か"""
        h, w = img.shape[:2]; yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        for i, (px, py, sz, sp, ph, fr) in enumerate(self.dust):
            if (fr > 0.62) != front: continue
            tw = 0.5 + 0.5 * math.sin(2 * math.pi * (0.9 + 1.3 * sp) * t + 6.283 * ph)          # ゆっくり またたく（1秒に 1〜2回）
            x = ((px + 0.02 * math.sin(6.283 * (ph + 0.3 * t))) % 1) * w; y = ((py - (0.02 + 0.05 * sp) * t) % 1) * h
            r = (2.2 + 7.5 * sz * sz) * self.scale * (0.6 + 0.4 * tw); a = (0.25 + 0.6 * tw) * (0.55 if not front else 0.9)
            x0, x1, y0, y1 = int(max(0, x - 6 * r)), int(min(w, x + 6 * r + 1)), int(max(0, y - 6 * r)), int(min(h, y + 6 * r + 1))
            if x1 <= x0 or y1 <= y0: continue
            dx, dy = xx[y0:y1, x0:x1] - x, yy[y0:y1, x0:x1] - y
            g = np.exp(-(dx * dx + dy * dy) / (2 * r * r)) + (0.8 * np.exp(-(dx * dx) / (0.18 * r * r) - (dy * dy) / (14 * r * r)) + 0.8 * np.exp(-(dy * dy) / (0.18 * r * r) - (dx * dx) / (14 * r * r)) if sz > 0.45 else 0)
            img[y0:y1, x0:x1] += (a * g)[..., None] * np.array([1.0, 0.93, 0.7], np.float32)
        return img

    def frame(self, t):
        R = self.R; s = shot(t, self.hero)
        cam = R.Camera.look_at(s['eye'], s['target'], fov_y=s['fov'], W=self.w, H=self.h)
        o = R.render(self.prims, cam, lights=self.lights, ss=2, model_matrix=s['M'], ambient=((0.95, 0.86, 0.66), (0.62, 0.5, 0.36)), env_spec=(1.0, 0.92, 0.7),
                     ao_strength=0.8, rim=((1.0, 0.9, 0.62), 0.35, 3.0), want=('rgb', 'alpha'))
        hdr = o['rgb']; a = o['alpha'][..., None]
        fg = R.tonemap(hdr, exposure=1.0)
        bg = self.back(s, t)
        # うしろの 光：3D の まわりが ふわっと 金色に 光る（3D の 形を ぼかして 足す）
        halo = np.asarray(Image.fromarray((o['alpha'] * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(34 * self.scale)), np.float32) / 255
        bg = bg + halo[..., None] * np.array([0.30, 0.24, 0.10], np.float32)
        bg = self.stars(bg, s, t, False)
        img = bg * (1 - a) + fg * a
        # 3D の 明るい 所が にじむ
        lum = hdr.max(-1); hi = (np.clip((lum - 0.95) / 0.9, 0, 1.5)[..., None] * a * hdr / np.maximum(lum, 1e-3)[..., None]).astype(np.float32)
        gl = np.dstack([np.asarray(Image.fromarray((np.clip(hi[..., c], 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(11 * self.scale)), np.float32) / 255 for c in range(3)])
        img = img + 0.75 * gl
        img = self.stars(img, s, t, True)
        return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8), s


FILM_NAME, END_NAME = 'tc_gk_film2.mp4', 'tc_gk_end2.webp'      # 2＝カットインの カメラを ゆっくりに した もの（光の 点めつ）。前の もの（番号 なし）は もとの フォルダに 残す


def flash(src):
    """動画 だけで 光の 点めつを 数える（kisekae/flash_px.py と 同じ 数え方）→ (4回 以上 点めつ した 点の 面積の いちばん 多い 窓, その 窓が はじまる 動画の 秒)"""
    fs = sorted(f for f in os.listdir(src) if f.startswith('f') and f.endswith('.png') and len(f) == 8)
    ims = [np.asarray(Image.open(os.path.join(src, f)).convert('RGB').resize((98, 211), Image.BILINEAR), dtype=np.float32) / 255 for f in fs]
    seq = [np.zeros_like(ims[0])] * 30 + [ims[i // 2] * sm((i / 60) / 0.12) for i in range(len(ims) * 2)] + [ims[-1]] * 72      # 真っ暗 0.5秒 → 0.12秒で 出る → 2回ずつ → さいごの コマ 1.2秒
    def lum(a): a = np.where(a <= .04045, a / 12.92, ((a + .055) / 1.055) ** 2.4); return .2126 * a[..., 0] + .7152 * a[..., 1] + .0722 * a[..., 2]
    L = [lum(x) for x in seq]; ext = L[0].copy(); dirn = np.zeros_like(ext, dtype=np.int8); tr = []
    for x in L[1:]:
        up = (x - ext >= .1) & (np.minimum(x, ext) < .8) & (dirn <= 0); dn = (ext - x >= .1) & (np.minimum(x, ext) < .8) & (dirn >= 0); ch = up | dn
        dirn = np.where(up, 1, np.where(dn, -1, dirn)).astype(np.int8)
        ext = np.where(ch, x, np.where(dirn > 0, np.maximum(ext, x), np.where(dirn < 0, np.minimum(ext, x), ext))); tr.append(ch)
    C = np.stack(tr).astype(np.int16); cs = np.concatenate([np.zeros((1,) + C.shape[1:], np.int16), np.cumsum(C, 0)], 0)
    best = max((float((((cs[min(len(tr), i + 60)] - cs[i]) // 2) > 3).mean()), (i + 1 - 30) / 60) for i in range(len(tr)))
    return best


def encode(src, dst):
    os.makedirs(dst, exist_ok=True); mp4 = os.path.join(dst, FILM_NAME)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS), '-i', os.path.join(src, 'f%03d.png'), '-frames:v', str(NF), '-c:v', 'libx264', '-preset', 'slow', '-crf', '22', '-profile:v', 'high',
                    '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-tag:v', 'avc1', '-an', mp4], check=True)
    Image.open(os.path.join(src, 'f%03d.png' % (NF - 1))).convert('RGB').save(os.path.join(dst, END_NAME), 'WEBP', quality=88, method=6)
    print(FILM_NAME, os.path.getsize(mp4), 'B ・', END_NAME, os.path.getsize(os.path.join(dst, END_NAME)), 'B')


if __name__ == '__main__':
    A = sys.argv[1:]
    if A[0] == '--encode': encode(A[1], A[2]); sys.exit(0)
    if A[0] == '--flash':
        a, t = flash(A[1]); print(f'動画 だけの 点めつ：1秒に 4回 以上 点めつ する 点の 面積 {a * 100:.1f}%（いちばん 多い 窓：動画の {t:.2f}秒から）・決まりは 10% 未満'); sys.exit(0 if a < 0.1 else 1)
    glb_path, bg_path, out = A[0], A[1], A[2]; os.makedirs(out, exist_ok=True)
    scale = float(A[A.index('--scale') + 1]) if '--scale' in A else 1.0
    frames = [int(x) for x in A[A.index('--frames') + 1].split(',')] if '--frames' in A else list(range(int(A[A.index('--range') + 1]), int(A[A.index('--range') + 2]))) if '--range' in A else list(range(NF))
    if '--sheet' in A: frames = [0, 2, 4, 6, 9, 17, 18, 31, 32, 44, 45, 46, 47, 49, 52, 55, 59, 71]
    F = Film(glb_path, bg_path, scale); t0 = time.time(); ims = []
    for i in frames:
        t1 = time.time(); img, s = F.frame(i / FPS); Image.fromarray(img).save(os.path.join(out, 'f%03d.png' % i)); ims.append(img)
        print('f%03d' % i, '場面', s['k'], round(time.time() - t1, 1), 's', flush=True)
    if '--sheet' in A:
        n = len(ims); cols = 6; rows = (n + cols - 1) // cols; hh, ww = ims[0].shape[:2]; sh = np.zeros((rows * hh, cols * ww, 3), np.uint8)
        for j, im in enumerate(ims): sh[(j // cols) * hh:(j // cols + 1) * hh, (j % cols) * ww:(j % cols + 1) * ww] = im
        Image.fromarray(sh).save(os.path.join(out, 'sheet.jpg'), quality=88)
    print('ぜんぶ', round(time.time() - t0, 1), 's')
