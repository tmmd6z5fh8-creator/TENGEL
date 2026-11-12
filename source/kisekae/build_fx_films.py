"""特別な 演出の 動画と さいごの 1まい（App Store版 第5弾：アップデート指示書 15章・16.3）を 手元で 作る。できた ファイルは リポジトリに 入れない（1章の11）：
     python3 build_fx_films.py [<出力フォルダ>] [<作業フォルダ>]     （何も指定しないと source/ios/fx_assets/。作業フォルダは その中の _films/）
   作るもの（1コマずつ 計算で 描く 絵なので 時間が かかる：数十分）
     sgd_film2.mp4 … 超神様の 動画（第4.162版：まさちゃん 2026/11/12 22:32「一枚目の球体のシーン消して！いきなり2枚目の爆破のシーンに入るようにして！あと、鳥居とか文字関係は
                     このファイルのデータを使って！」）：flat/kami_film.py ① 金の 爆発 6コマ（前の 48コマの さいごの 6コマ）→ flat/kami_white.py 金粉の 白い 光 40コマ
                     （② の はじめの 8コマにも 金粉を かさねる）→ flat/kami_film2.py ② 金の 立体の 字 141コマ → flat/kami_film3.py ③ 神様的中 198コマ ＝ 385コマ・12.83秒
                     ②③ の 字と 鳥居は まさちゃんの Meshy の 3D（flat/kami_glb.py：場所は SGD_GLB_DIR。ない ときは 前の 字と 鳥居で 描く）
                     H.264・音なし・1170×2532・30コマ/秒・CRF 20（もと。アプリには kisekae/lite_assets.py が CRF 24 に した 軽い 版を 入れる）
                     ※ 前の 動画（球体の 場面 あり・427コマ・14.23秒）＝ sgd_film.mp4・sgd_last.webp は もとの フォルダに のこす（上書きしない・アプリには 入れない）
     sgd_last2.webp … 超神様の 動画の さいごの 1まい（視差効果を減らす 時・動画が 動かない 時）
     sfx_sgd2.m4a … 超神様の 動画の 音（第4.162版：gen_sfx.py の sfx_sgd＝動画の 絵の スクリプトの 時刻で 作る → AAC 160kbps。金の 爆発から 鳴る。FILMS=sgd で 動画と いっしょに 作る。
                     ③ の 雷の 場所は 字の 形から 出すので、まさちゃんの 3D が ある 所で 作る）
     spg_up.mp4   … （第4.162版から アプリに 入れない）超プレミアム神様的中の 昇格の 動画：超プレミアムど的中の 6.0秒（き！）の 1まい（flat/capture_page.py・Playwright の Chromium）→
                     flat/kami_glitch.py バグ 59＋まっ暗 30 コマ → flat/kami_cutin.py 宇宙の カットイン 108コマ ＝ 197コマ・6.57秒（約5MB）
     sd_film2.mp4 … ど的中・紫電（極ど的中）の 動画（第4.71版：flat/shiden_film.py：黒 54 → 暗闇に 光る 目と 馬の 顔 60 → 縦書きの 的中と 蹄の カットイン 108
                     → 3D の ど！！！的中（flat/shiden_logo.py）93 ＝ 315コマ・10.5秒・780×1688・CRF 20。2コアで 約1時間）。FILMS=sd で これだけ 作る
                     第4.119版：馬の 顔（54〜113）と 蹄（175〜205）は まさちゃんの Meshy の 馬と 蹄（flat/shiden_glb.py・shiden_face2.py・r3d/glb。
                     GLB の 場所は SD_HORSE_GLB・SD_HOOF_GLB）。顔は G バッファ（shiden_film.py --facebuf <buf>）→ 雷・息・仕上げ（--facecomp <buf> <_films/sd> 54 114）。
                     できた コマが _films/sd に あれば とばして 書き出す だけ。SD_HORSE=old で 前の 馬（その コマを 消してから）
                     第4.163版（まさちゃん 2026/11/13 00:15「極ど的中の演出の馬、文字をこのファイルと入れ替えて！」）：顔の 馬は Violet_Nightmane（SD_HORSE_MODEL=nightmane・
                     場所は SD_GLB_DIR）・縦書きの 的中と ど！！！／極／的中は まさちゃんの 3D（flat/shiden_gtext.py：場所は SD_TEXT_DIR。ない とき・SD_TEXT=old は 前の 字）。
                     ※ 前の 動画＝ sd_film.mp4・sd_last.webp は もとの フォルダに のこす（上書きしない・アプリには 入れない）
     sd_last2.webp … 紫電の 動画の さいごの 1まい（視差効果を減らす 時・動画が 動かない 時）
     nd_film2.mp4 … ノーマルど的中の 動画（第4.77版：flat/normal_film.py：真っ暗 30 → 光の 玉 → シルバーの 競走馬と 騎手（flat/nd_horse.py の 走り）が 芝の 上を ギャロップ
                     → 光に つつまれる → 低い 目線（芝・大きな 玉）に 3D の ど！的中（flat/shiden_logo.py）が 落ちて くる ＝ 315コマ・10.5秒（さいごの 場面を 2.3秒 のばした）・780×1688・CRF 20。2コアで 約1時間）。FILMS=nd で これだけ 作る
                     第4.163版（02:35「ノーマルど的中演出の文字このファイルと入れ替えて！」）：ど！／的中は まさちゃんの 3D（flat/shiden_gtext.py の nd）。字が 出る 前（170コマ目まで）は
                     前の 動画（nd_film.mp4）の 絵を 圧縮し直さずに そのまま 使い、170コマ目から だけ 新しく 描いて つなぐ（nd_film()）。※ 前の 動画と さいごの 1まいは のこす
     nd_last2.webp … ノーマルど的中の 動画の さいごの 1まい
     gk_film.mp4  … 神様極的中の 動画（第4.117版：kami_kiwami.py。まさちゃんの 3D と 背景の 絵で 1コマずつ 描いた できた 動画（MASTER・第13稿・リポジトリの 外：
                     GK_MASTER=<mp4> で ほかの 所も）を アプリ用に CRF 23 で 作り直す ＝ 361コマ・12.03秒・780×1688・約10.3MB）。FILMS=gk で これだけ 作る
     gk_last.webp … 神様極的中の 動画の さいごの 1まい
   乱数の 種が 決まって いるので、コマの 絵は 何回 作っても 同じ（動画の ファイルは ffmpeg の 版で 少し ちがう ことが ある）。
   第4.162版：もう ある 動画は 作り直さない（もと＝マスターを 上書きしない）。作り直す ときは FORCE=1（その 動画の 名前を FILMS で 決めて）。
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
import build_fx as BF     # noqa: E402  （ファイルの 名前：FILMS・STILL）

FF = shutil.which('ffmpeg')
assert FF, 'ffmpeg がない'
ENC = ['-c:v', 'libx264', '-preset', 'slow', '-crf', '24', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-tag:v', 'avc1', '-an']
SGD_CRF = '20'      # 第4.162版：超神様の 新しい 動画の もとは CRF 20（紫電・ノーマルと 同じ）。アプリに 入る 軽い 版（CRF 24）を 1回の 圧縮に 近づける（前は もとも CRF 24＝2回 圧縮）
FORCE = os.environ.get('FORCE') == '1'


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


def encode(comb, n, name, crf=None):
    """comb/f%03d.png（n こ）→ out/name"""
    assert frames(comb, 'f%03d.png', n), f'{name} の コマが そろって いない'
    enc = list(ENC)
    if crf:
        enc[enc.index('-crf') + 1] = crf
    run([FF, '-y', '-loglevel', 'error', '-framerate', '30', '-i', os.path.join(comb, 'f%03d.png')] + enc + [os.path.join(out, name)])
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
    assert len(seq) == N1 + NW + N2 + N3 == 385 == round(SG.FILM * SG.FPS), len(seq)      # 第4.162版：① は 金の 爆発 だけ（6コマ）。前は 427
    for i, s in enumerate(seq):
        link(s, os.path.join(comb, f'f{i + 1:03d}.png'))
    film, last = BF.FILMS['sgd_film'], BF.STILL['sgd_last']
    encode(comb, len(seq), film, SGD_CRF)
    import cv2
    im = cv2.imread(seq[-1])
    assert im is not None and im.shape[:2] == (2532, 1170), 'さいごの 1まいが 読めない'
    cv2.imwrite(os.path.join(out, last), im, [cv2.IMWRITE_WEBP_QUALITY, 90])
    print(last, f'{os.path.getsize(os.path.join(out, last)) / 1e6:.2f}MB', flush=True)


def sgd_sound():
    """超神様の 動画の 音（gen_sfx.py の sfx_sgd）→ out/<build_fx.py の SFX の sgd>（AAC 160kbps：build_fx_assets.py の 音と 同じ 形）"""
    name = BF.SFX['sgd']
    argv = sys.argv
    sys.argv = ['gen_sfx.py']
    try:
        import gen_sfx as S
    finally:
        sys.argv = argv
    x = S.sfx_sgd()
    wav = os.path.join(work, name[:-4] + '.wav')
    S.write_wav(wav, x)
    run([FF, '-y', '-loglevel', 'error', '-i', wav, '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', os.path.join(out, name)])
    os.remove(wav)
    print(name, f'{len(x) / S.SR:.2f}秒  {S.lufs(x):.1f} LUFS  {os.path.getsize(os.path.join(out, name)) / 1e6:.2f}MB', flush=True)


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


# ---------------------------------------------------------------- 紫電の 動画と さいごの 1まい（第4.70版・第4.71版）
def sd_film():
    """第4.163版：顔の 馬は Violet_Nightmane・字（縦書きの 的中／ど！！！・極・的中）は まさちゃんの 3D（flat/shiden_gtext.py）→ 新しい 名前（build_fx.py の FILMS・STILL）で 書き出す。
       顔の コマ（54〜113）が まだ ない ときは G バッファ（--facebuf）→ 雷・息・仕上げ（--facecomp）を 先に 作る（3D の 馬の とき）"""
    sd = os.path.join(work, 'sd')
    sys.path.insert(0, FLAT)
    import shiden as SDM
    n = int(round(SDM.FILM['END'] * SDM.FILM['FPS']))
    film, last = BF.FILMS['sd_film'], BF.STILL['sd_last']
    f0, f1 = int(round(SDM.FILM['BLACK'] * SDM.FILM['FPS'])), int(round(SDM.FILM['FACE'] * SDM.FILM['FPS']))
    if os.environ.get('SD_HORSE', 'new') != 'old' and not all(os.path.exists(os.path.join(sd, f'f{i:03d}.png')) for i in range(f0, f1)):
        buf = os.path.join(work, 'sd_buf')
        run([sys.executable, os.path.join(FLAT, 'shiden_film.py'), '--facebuf', buf])
        run([sys.executable, os.path.join(FLAT, 'shiden_film.py'), '--facecomp', buf, sd, str(f0), str(f1)])
    run([sys.executable, os.path.join(FLAT, 'shiden_film.py'), sd])          # できて いる コマは とばす（作りかけから つづける）
    assert all(os.path.exists(os.path.join(sd, f'f{i:03d}.png')) for i in range(n)), '紫電の コマが そろって いない'
    run([sys.executable, os.path.join(FLAT, 'shiden_film.py'), '--encode', sd, os.path.join(out, film)])
    print(film, f'{os.path.getsize(os.path.join(out, film)) / 1e6:.2f}MB', f'{n}コマ', flush=True)
    run([sys.executable, os.path.join(FLAT, 'shiden_film.py'), '--last', sd, os.path.join(out, last)])
    print(last, f'{os.path.getsize(os.path.join(out, last)) / 1e6:.2f}MB', flush=True)
    # 第4.113版：結果ボードカスタム「出世馬」の 幻の 馬の 絵（この コマ 60・70 → bcx_ph0・bcx_ph1.webp）は 出世馬と いっしょに 消した


# ---------------------------------------------------------------- ノーマルど的中の 動画と さいごの 1まい（第4.77版）
ND_CUT = 170          # 第4.163版：ノーマルど的中の 新しい 動画は ここ（5.67秒：字が 出る 5.8秒の 前・前の 動画の キーフレーム）から を 描き直して つなぐ


def key_frames(mp4):
    """動画の キーフレームの コマ（0 から）"""
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries', 'frame=key_frame', '-of', 'csv=p=0', mp4], capture_output=True, text=True, check=True)
    return [i for i, ln in enumerate(r.stdout.split()) if ln.strip().startswith('1')]


def nd_film():
    """第4.163版：「ど！／的中」は まさちゃんの 3D（flat/shiden_gtext.py の nd）→ 新しい 名前（build_fx.py の FILMS・STILL）で 書き出す。
       字が 出る（5.8秒）より 前の 絵は 前と 同じ。前の 動画（もと：nd_film.mp4）が あって ND_CUT コマ目が キーフレームなら、はじめの ND_CUT コマは 圧縮し直さずに そのまま 使い、
       ND_CUT コマ目から だけ 新しく 描いて つなぐ（同じ 圧縮の 決めごと＝つなぎ目の 前後で 動画の 形は 同じ）。ND_SPLICE=0・前の 動画が ない ときは ぜんぶ 描く"""
    nd = os.path.join(work, 'nd')
    sys.path.insert(0, K)
    import normal_do as NDM
    n = int(round(NDM.FILM['END'] * NDM.FILM['FPS']))
    film, last = BF.FILMS['nd_film'], BF.STILL['nd_last']
    old = os.path.join(out, 'nd_film.mp4')
    splice = os.environ.get('ND_SPLICE', '1') != '0' and film != 'nd_film.mp4' and os.path.exists(old) and ND_CUT in key_frames(old)
    i0 = ND_CUT if splice else 0
    run([sys.executable, os.path.join(FLAT, 'normal_film.py'), nd, str(i0), str(n)])          # できて いる コマは とばす（作りかけから つづける）
    assert all(os.path.exists(os.path.join(nd, f'f{i:03d}.png')) for i in range(i0, n)), 'ノーマルど的中の コマが そろって いない'
    if splice:
        a, b, lst = (os.path.join(work, x) for x in ('nd_a.mp4', 'nd_b.mp4', 'nd_ab.txt'))
        run([FF, '-y', '-loglevel', 'error', '-i', old, '-frames:v', str(ND_CUT), '-c', 'copy', a])
        run([FF, '-y', '-loglevel', 'error', '-framerate', '30', '-start_number', str(ND_CUT), '-i', os.path.join(nd, 'f%03d.png'),
             '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-tag:v', 'avc1', '-an', b])
        open(lst, 'w').write(f"file '{a}'\nfile '{b}'\n")
        run([FF, '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', '-movflags', '+faststart', '-tag:v', 'avc1', os.path.join(out, film)])
        import cv2
        import numpy as np
        co, cn = cv2.VideoCapture(old), cv2.VideoCapture(os.path.join(out, film))
        same = 0
        for i in range(ND_CUT):
            ok1, x = co.read(); ok2, y = cn.read()
            assert ok1 and ok2 and np.array_equal(x, y), f'つないだ 動画の {i} コマ目が 前の 動画と ちがう'
            same += 1
        cnt = same
        while cn.read()[0]:
            cnt += 1
        assert cnt == n, f'つないだ 動画の コマ数 {cnt}（{n} の はず）'
        for x in (a, b, lst):
            os.remove(x)
        print(f'つないだ：はじめの {same}コマは 前の 動画と 1画素も 同じ（圧縮し直して いない）・{ND_CUT}コマ目から 新しい 絵', flush=True)
    else:
        run([sys.executable, os.path.join(FLAT, 'normal_film.py'), '--encode', nd, os.path.join(out, film)])
    print(film, f'{os.path.getsize(os.path.join(out, film)) / 1e6:.2f}MB', f'{n}コマ', flush=True)
    run([sys.executable, os.path.join(FLAT, 'normal_film.py'), '--last', nd, os.path.join(out, last)])
    print(last, f'{os.path.getsize(os.path.join(out, last)) / 1e6:.2f}MB', flush=True)


# ---------------------------------------------------------------- 神様極的中の 動画と さいごの 1まい（第4.117版）
def gk_film():
    import kami_kiwami as KK
    src = os.environ.get('GK_MASTER') or KK.MASTER
    assert os.path.exists(src), f'神様極的中の できた 動画が ない：{src}（GK_MASTER=<mp4> で 指定）'
    dst = os.path.join(out, 'gk_film.mp4')
    # できた 動画（CRF 20）を アプリ用に（CRF 23・veryfast・音なし・faststart）。見た目は 同じ（SSIM 0.976）・点めつは 0個（flash_px.py AREA=.1）
    run([FF, '-y', '-loglevel', 'error', '-i', src, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', str(KK.CRF), '-profile:v', 'high', '-pix_fmt', 'yuv420p',
         '-movflags', '+faststart', '-tag:v', 'avc1', '-an', dst])
    print('gk_film.mp4', f'{os.path.getsize(dst) / 1e6:.2f}MB', flush=True)
    last = os.path.join(work, 'gk_last.png')
    run([FF, '-y', '-loglevel', 'error', '-sseof', '-0.05', '-i', src, '-frames:v', '1', '-update', '1', last])   # さいごの コマ
    import cv2
    im = cv2.imread(last)
    assert im is not None and im.shape[:2] == (KK.FILM['H'], KK.FILM['W']), 'さいごの 1まいが 読めない'
    cv2.imwrite(os.path.join(out, 'gk_last.webp'), im, [cv2.IMWRITE_WEBP_QUALITY, 90])
    os.remove(last)
    print('gk_last.webp', f'{os.path.getsize(os.path.join(out, "gk_last.webp")) / 1e6:.2f}MB', flush=True)


if __name__ == '__main__':
    which = os.environ.get('FILMS', 'sgd,spg,sd,nd,gk').split(',')
    jobs = (('sgd', sgd_film, BF.FILMS['sgd_film']), ('sgd', sgd_sound, BF.SFX['sgd']), ('spg', spg_up, 'spg_up.mp4'), ('sd', sd_film, BF.FILMS['sd_film']), ('nd', nd_film, BF.FILMS['nd_film']), ('gk', gk_film, BF.FILMS['gk_film']))
    for key, fn, name in jobs:
        if key not in which:
            continue
        if os.path.exists(os.path.join(out, name)) and not FORCE:      # もと（マスター）を 上書きしない
            print(f'{name} は もう ある → 作り直さない（作り直す ときは FORCE=1）', flush=True)
            continue
        fn()
    names = sorted(set([n for _, _, n in jobs] + list(BF.STILL.values())))
    print('作った:', out, [f for f in names if os.path.exists(os.path.join(out, f))])
