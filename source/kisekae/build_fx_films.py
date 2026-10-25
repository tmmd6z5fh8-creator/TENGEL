"""特別な 演出の 動画 2本と さいごの 1まい（App Store版 第5弾：アップデート指示書 15章・16.3）を 手元で 作る。できた ファイルは リポジトリに 入れない（1章の11）：
     python3 build_fx_films.py [<出力フォルダ>] [<作業フォルダ>]     （何も指定しないと source/ios/fx_assets/。作業フォルダは その中の _films/）
   作るもの（1コマずつ 計算で 描く 絵なので 時間が かかる：数十分）
     sgd_film.mp4 … 超神様の 動画（超神様的中・超プレミアム神様的中で 同じ）：flat/kami_film.py ① 金の 嵐 48コマ → flat/kami_white.py 金粉の 白い 光 40コマ
                     （② の はじめの 8コマにも 金粉を かさねる）→ flat/kami_film2.py ② 金の 立体の 字 141コマ → flat/kami_film3.py ③ 神様的中 198コマ ＝ 427コマ・14.23秒
                     H.264・音なし・1170×2532・30コマ/秒・CRF 24（約11MB）
     sgd_last.webp … 超神様の 動画の さいごの 1まい（視差効果を減らす 時・動画が 動かない 時）
     spg_up.mp4   … 超プレミアム神様的中の 昇格の 動画：超プレミアムど的中の 6.0秒（き！）の 1まい（flat/capture_page.py・Playwright の Chromium）→
                     flat/kami_glitch.py バグ 59＋まっ暗 30 コマ → flat/kami_cutin.py 宇宙の カットイン 108コマ ＝ 197コマ・6.57秒（約5MB）
     sd_film.mp4  … 第4.70版：ど的中・紫電の ② の 動画（flat/shiden_film.py：リアルな 馬の 顔 120 → 蹄の カットイン 72 → 光の 玉 36 ＝ 228コマ・7.6秒・
                     780×1688・CRF 20。2コアで 約1時間）。FILMS=sd で これだけ 作る
   乱数の 種が 決まって いるので、コマの 絵は 何回 作っても 同じ（動画の ファイルは ffmpeg の 版で 少し ちがう ことが ある）。
   numpy・opencv・fontTools・librsvg・ffmpeg・Playwright がいる。キャンバス（見本）から 取った 同じ 名前の ファイルを 置いても よい。"""
import os
import shutil
import subprocess
import sys

K = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(K)
FLAT = os.path.join(K, 'flat')
out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(SRC, 'ios', 'fx_assets'))
work = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else os.path.join(out, '_films'))
os.makedirs(out, exist_ok=True)
os.makedirs(work, exist_ok=True)
sys.path.insert(0, K)
import kami_super as SG   # noqa: E402

FF = shutil.which('ffmpeg')
assert FF, 'ffmpeg がない'
ENC = ['-c:v', 'libx264', '-preset', 'slow', '-crf', '24', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-tag:v', 'avc1', '-an']


def run(args, **kw):
    print('$', ' '.join(os.path.relpath(a, SRC) if os.path.isabs(a) else a for a in args), flush=True)
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, **kw)


def frames(d, pat, n):
    """d の 中の pat（f%03d など）の コマが n こ そろって いるか"""
    return all(os.path.exists(os.path.join(d, pat % (i + 1))) for i in range(n))


def link(src, dst):
    if os.path.exists(dst):
        os.remove(dst)
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy(src, dst)


def encode(comb, n, name):
    """comb/f%03d.png（n こ）→ out/name"""
    assert frames(comb, 'f%03d.png', n), f'{name} の コマが そろって いない'
    run([FF, '-y', '-loglevel', 'error', '-framerate', '30', '-i', os.path.join(comb, 'f%03d.png')] + ENC + [os.path.join(out, name)])
    print(name, f'{os.path.getsize(os.path.join(out, name)) / 1e6:.2f}MB', f'{n}コマ', flush=True)


# ---------------------------------------------------------------- 超神様の 動画（①・白い 光・②・③）
def sgd_film():
    a, w, b, c, comb = (os.path.join(work, x) for x in ('a', 'w', 'b', 'c', 'comb'))
    N1, NW, N2, N3 = SG.N1, SG.NW, SG.N2, SG.N3
    if not frames(a, 'f%02d.png', N1):
        run([sys.executable, os.path.join(FLAT, 'kami_film.py'), a])
    if not frames(b, 'f%03d.png', N2):
        run([sys.executable, os.path.join(FLAT, 'kami_film2.py'), b])
    if not (frames(w, 'w%03d.png', NW) and frames(w, 'x%03d.png', 8)):
        run([sys.executable, os.path.join(FLAT, 'kami_white.py'), os.path.join(a, f'f{N1:02d}.png'), w] + [os.path.join(b, f'f{i + 1:03d}.png') for i in range(8)])
    if not frames(c, 'f%03d.png', N3):
        run([sys.executable, os.path.join(FLAT, 'kami_film3.py'), c])
    os.makedirs(comb, exist_ok=True)
    seq = ([os.path.join(a, f'f{i + 1:02d}.png') for i in range(N1)] + [os.path.join(w, f'w{i + 1:03d}.png') for i in range(NW)]
           + [os.path.join(w, f'x{i + 1:03d}.png') for i in range(8)] + [os.path.join(b, f'f{i + 1:03d}.png') for i in range(8, N2)]
           + [os.path.join(c, f'f{i + 1:03d}.png') for i in range(N3)])
    assert len(seq) == N1 + NW + N2 + N3 == 427, len(seq)
    for i, s in enumerate(seq):
        link(s, os.path.join(comb, f'f{i + 1:03d}.png'))
    encode(comb, len(seq), 'sgd_film.mp4')
    import cv2
    im = cv2.imread(seq[-1])
    assert im is not None and im.shape[:2] == (2532, 1170), 'さいごの 1まいが 読めない'
    cv2.imwrite(os.path.join(out, 'sgd_last.webp'), im, [cv2.IMWRITE_WEBP_QUALITY, 90])
    print('sgd_last.webp', f'{os.path.getsize(os.path.join(out, "sgd_last.webp")) / 1e6:.2f}MB', flush=True)


# ---------------------------------------------------------------- 昇格の 動画（き！の 1まい → バグ → まっ暗 → 宇宙の カットイン）
def spg_up():
    zp, g, cut, comb = (os.path.join(work, x) for x in ('zp', 'g', 'cut', 'up'))
    sys.path.insert(0, FLAT)
    import kami_glitch as KG
    import kami_cutin as KC
    NG, NC = KG.N, KC.N
    assert NG + NC == SG.UP_N, (NG, NC, SG.UP_N)
    ki = int(round(SG.UP_AT * SG.FPS)) + 1          # き！の 1まい（0秒が f001 なので 6.0秒は f181）
    src = os.path.join(zp, f'f{ki:03d}.png')
    if not os.path.exists(src):
        run([sys.executable, os.path.join(FLAT, 'capture_page.py'), os.path.join(K, 'mock', 'Fx_SuperPremium.dc.html'), zp, '0', f'{SG.UP_AT:g}'])
    assert os.path.exists(src), 'き！の 1まいが ない（Playwright の Chromium が いる）'
    if not frames(g, 'g%03d.png', NG):
        run([sys.executable, os.path.join(FLAT, 'kami_glitch.py'), src, g])
    if not frames(cut, 'f%03d.png', NC):
        run([sys.executable, os.path.join(FLAT, 'kami_cutin.py'), cut])
    os.makedirs(comb, exist_ok=True)
    seq = [os.path.join(g, f'g{i + 1:03d}.png') for i in range(NG)] + [os.path.join(cut, f'f{i + 1:03d}.png') for i in range(NC)]
    for i, s in enumerate(seq):
        link(s, os.path.join(comb, f'f{i + 1:03d}.png'))
    encode(comb, len(seq), 'spg_up.mp4')


# ---------------------------------------------------------------- 紫電の ② の 動画（第4.70版）
def sd_film():
    sd = os.path.join(work, 'sd')
    sys.path.insert(0, FLAT)
    import shiden as SDM
    n = int(round(SDM.FILM['END'] * SDM.FILM['FPS']))
    run([sys.executable, os.path.join(FLAT, 'shiden_film.py'), sd])          # できて いる コマは とばす（作りかけから つづける）
    assert all(os.path.exists(os.path.join(sd, f'f{i:03d}.png')) for i in range(n)), '紫電の コマが そろって いない'
    run([sys.executable, os.path.join(FLAT, 'shiden_film.py'), '--encode', sd, os.path.join(out, 'sd_film.mp4')])
    print('sd_film.mp4', f'{os.path.getsize(os.path.join(out, "sd_film.mp4")) / 1e6:.2f}MB', f'{n}コマ', flush=True)


if __name__ == '__main__':
    which = os.environ.get('FILMS', 'sgd,spg,sd').split(',')
    if 'sgd' in which:
        sgd_film()
    if 'spg' in which:
        spg_up()
    if 'sd' in which:
        sd_film()
    print('作った:', out, [f for f in ('sgd_film.mp4', 'sgd_last.webp', 'spg_up.mp4', 'sd_film.mp4') if os.path.exists(os.path.join(out, f))])
