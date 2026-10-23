"""的中ボタンの絵と音（App Store版 第3弾）を手元で作る。できたファイルはリポジトリに入れない（1章の11）：
     python3 build_fx_assets.py [<出力フォルダ>]     （何も指定しないと source/ios/fx_assets/。build_ios.py がここから Resources/ に入れる）
   作るもの（ぜんぶで約0.6MB）
     fz_ncore.webp・fz_nglow.webp … ど的中のネオンの線画のマスク（neon_icon.py：icons/icon_master_en.png から）
     sfx_hit_push.m4a・sfx_hit.m4a・sfx_big_push.m4a・sfx_big.m4a・sfx_fz_push.m4a・sfx_fz.m4a … 効果音（gen_sfx.py → ffmpeg で AAC 160kbps）
   乱数の種が決まっているので、何回作っても同じ。numpy・scipy・opencv・ffmpeg がいる（なければ、その分は作らずに知らせる）"""
import os
import shutil
import subprocess
import sys

K = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(K)
out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(SRC, 'ios', 'fx_assets'))
os.makedirs(out, exist_ok=True)
sys.path.insert(0, K)
from build_fx import ASSET_FILES, SFX   # noqa: E402

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

# 2) 効果音（6こ）
ff = shutil.which('ffmpeg')
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
        print(f'{name}  {len(x) / S.SR:.2f}秒  {S.lufs(x):.1f} LUFS')
except Exception as e:   # noqa: BLE001
    skipped.append(f'効果音（{e}）')

size = sum(os.path.getsize(os.path.join(out, f)) for f in ASSET_FILES if os.path.exists(os.path.join(out, f)))
print('作った:', out, made, f'{size / 1e6:.2f}MB')
if skipped:
    print('作れなかった:', '・'.join(skipped))
missing = [f for f in ASSET_FILES if not os.path.exists(os.path.join(out, f))]
if missing:
    print('まだないファイル:', missing)
    sys.exit(1)
