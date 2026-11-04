# 写した コマ（60コマ/秒）を つなげて 見本の 動画に（30コマ/秒・H.264）
import os, shutil, subprocess, sys
FR, OUT = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
clips = sys.argv[3].split(',')
SKIP = 6                     # 各 clip の はじめ 0.1秒（アプリの 画面が 見える 所）は とばす
tmp = os.path.join(os.path.dirname(OUT), '_seq'); shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
k = 0
for c in clips:
    d = os.path.join(FR, c); fs = sorted(f for f in os.listdir(d) if f.startswith('f') and f.endswith('.png'))[SKIP:]
    for i, f in enumerate(fs):
        if i % 2: continue                      # 60 → 30コマ/秒
        os.symlink(os.path.join(d, f), os.path.join(tmp, f'g{k:05d}.png')); k += 1
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '30', '-i', os.path.join(tmp, 'g%05d.png'),
                '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', OUT], check=True)
shutil.rmtree(tmp, ignore_errors=True)
print('video', OUT, k, 'frames', round(k / 30, 1), 's', os.path.getsize(OUT))
