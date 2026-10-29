"""的中ボタンの絵と音（App Store版 第3弾・第5弾）を手元で作る。できたファイルはリポジトリに入れない（1章の11）：
     python3 build_fx_assets.py [<出力フォルダ>]     （何も指定しないと source/ios/fx_assets/。build_ios.py がここから Resources/ に入れる）
   作るもの
     fz_ncore.webp・fz_nglow.webp … ど的中のネオンの線画のマスク（neon_icon.py：icons/icon_master_en.png から）
     sfx_hit_push.m4a・sfx_hit.m4a・sfx_big_push.m4a・sfx_big.m4a・sfx_fz_push.m4a・sfx_fz.m4a … 効果音（gen_sfx.py → ffmpeg で AAC 160kbps）
     第5弾（16.3 の 特別な 演出）：
       pm_….webp 38まい … プレミアムど的中の 絵（flat/premium_art.py・約2.1MB）
       gd_….webp 24まい … 神様的中の 絵（flat/kami_art.py・flat/kami_storm.py・約1.7MB）
       sfx_pc・sfx_zp・sfx_gd・sfx_sgd・sfx_spg_up・sfx_spg … 特別な 演出の 音 6こ（gen_sfx.py：超神様・超プレミアム神様の 音は 動画の 絵の 時刻を 読むので 少し かかる）
       第4.66版：sfx_sd.m4a（ど的中・紫電の 音）。第4.71版：sfx_sdp.m4a（紫電の 押した 瞬間の プチュン＝ど的中の 音の はじめ）。第4.77版：sfx_nd.m4a（ノーマルど的中の 音）。第4.79版：sfx_ndt.m4a（ノーマルど的中・極ど的中の 押した 瞬間の 音：ポチッ・トンッ・キラン）
       sgd_film.mp4・sgd_last.webp・spg_up.mp4・sd_film.mp4・sd_last.webp・nd_film.mp4・nd_last.webp … 動画 4本と さいごの 1まい 3まいは build_fx_films.py で 作る（時間が かかる）。
       ここでは 作らない（ない ときは 知らせる）。第4.71版：紫電は 絵を 使わない（ど！！！的中も 動画の 中の 3D）
     第4.108版：bcx_hb_head・bcx_hb_fore・bcx_hb_hind・bcx_hb_tail・bcx_hb_eye.webp … 結果ボードカスタム 22「ボードを持つ馬」の 部品 5まい
       （r3d/fx/board_horse_parts.py：3Dの 馬を 2回 描いて 頭と首・前足（くさびを 足す）・後ろ足・しっぽ・目を とじた 所に 分ける・約28KB・1〜2分）
   乱数の種が決まっているので、何回作っても同じ。numpy・scipy・opencv・librsvg・fontTools・ffmpeg がいる（なければ、その分は作らずに知らせる）
   ART=0 で 絵を 作らない・SFX=0 で 音を 作らない（ためす とき）"""
import os
import shutil
import subprocess
import sys

K = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(K)
out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(SRC, 'ios', 'fx_assets'))
os.makedirs(out, exist_ok=True)
sys.path.insert(0, K)
from build_fx import ASSET_FILES, SFX, ART, FILMS, STILL   # noqa: E402

made, skipped = [], []
# 1) ネオンのマスク
try:
    import cv2  # noqa: F401
    subprocess.run([sys.executable, os.path.join(K, 'neon_icon.py'), os.path.join(SRC, 'icons', 'icon_master_en.png'), out], check=True, stdout=subprocess.DEVNULL)
    pv = os.path.join(out, 'neon_preview.png')
    if os.path.exists(pv):
        os.remove(pv)   # 確認用の絵は入れない（PNG は Resources に入れない）
    made += ['fz_ncore.webp', 'fz_nglow.webp']
except Exception as e:   # noqa: BLE001
    skipped.append(f'ネオンのマスク（{e}）')

# 2) 第5弾の 絵（プレミアムど的中 38まい・神様的中 24まい）
if os.environ.get('ART', '1') != '0':
    for name, script in (('プレミアムど的中の 絵', 'premium_art.py'), ('神様的中の 絵', 'kami_art.py')):
        try:
            subprocess.run([sys.executable, os.path.join(K, 'flat', script), out], check=True, stdout=subprocess.DEVNULL)
            made.append(name)
        except Exception as e:   # noqa: BLE001
            skipped.append(f'{name}（{e}）')

    # 第4.108版：結果ボードカスタム 22「ボードを持つ馬」の 部品 5まい
    try:
        subprocess.run([sys.executable, os.path.join(K, 'r3d', 'fx', 'board_horse_parts.py'), out], check=True, stdout=subprocess.DEVNULL)
        made.append('ボードを持つ馬の 部品')
    except Exception as e:   # noqa: BLE001
        skipped.append(f'ボードを持つ馬の 部品（{e}）')

# 3) 効果音（14こ）
ff = shutil.which('ffmpeg')
if os.environ.get('SFX', '1') != '0':
    try:
        import numpy as np  # noqa: F401
        argv = sys.argv
        sys.argv = ['gen_sfx.py']
        import gen_sfx as S
        sys.argv = argv
        if not ff:
            raise RuntimeError('ffmpeg がない')
        fns = dict(S.SOUNDS)
        for key, name in SFX.items():
            stem = name[:-4]
            x = fns[stem]()
            wav = os.path.join(out, stem + '.wav')
            S.write_wav(wav, x)
            subprocess.run([ff, '-y', '-loglevel', 'error', '-i', wav, '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', os.path.join(out, name)], check=True)
            os.remove(wav)
            made.append(name)
            print(f'{name}  {len(x) / S.SR:.2f}秒  {S.lufs(x):.1f} LUFS', flush=True)
    except Exception as e:   # noqa: BLE001
        skipped.append(f'効果音（{e}）')

size = sum(os.path.getsize(os.path.join(out, f)) for f in ASSET_FILES if os.path.exists(os.path.join(out, f)))
print('作った:', out, made, f'{size / 1e6:.2f}MB')
if skipped:
    print('作れなかった:', '・'.join(skipped))
films = [f for f in list(FILMS.values()) + list(STILL.values()) if not os.path.exists(os.path.join(out, f))]
if films:
    print('動画と さいごの 1まいは build_fx_films.py で 作る（まだない）:', films)
missing = [f for f in ASSET_FILES if not os.path.exists(os.path.join(out, f))]
if missing:
    print('まだないファイル:', len(missing), 'こ', missing[:8])
    sys.exit(1)
