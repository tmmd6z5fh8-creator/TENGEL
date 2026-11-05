# shots_fx.py の コマ（30コマ／秒）に アプリと 同じ 音を かさねて mp4 に する
#   python3 make_fx_video.py <コマの フォルダ> <出す mp4> <PUSH の 音> <押した あとの 音>
#   PUSH の 音は 0秒（PUSH が 出た とき）から・押した あとの 音は 動画が 動きだした とき（info.json の film0）から
#   （アプリでも 動きだした ときに PUSH の 音を 止めて 鳴らす：fx.js の sfx は layer で ない とき hush）
import json, os, subprocess, sys
D, OUT, A1, A2 = sys.argv[1:5]
info = json.load(open(os.path.join(D, 'info.json'), encoding='utf8'))
n = info['frames']; dur = n / 30.0; t2 = float(info['film0'])
ms = int(round(t2 * 1000))
fc = (f"[1:a]atrim=0:{t2:.3f},afade=t=out:st={max(0, t2 - 0.05):.3f}:d=0.05,apad[a1];"
      f"[2:a]adelay={ms}|{ms},apad[a2];"
      f"[a1][a2]amix=inputs=2:duration=longest:normalize=0,atrim=0:{dur:.3f}[a]")
cmd = ['ffmpeg', '-v', 'error', '-y', '-framerate', '30', '-i', os.path.join(D, 'f%05d.png'), '-i', A1, '-i', A2,
       '-filter_complex', fc, '-map', '0:v', '-map', '[a]',
       '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
       '-c:a', 'aac', '-b:a', '192k', '-shortest', OUT]
subprocess.run(cmd, check=True)
p = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration,size', '-of', 'compact', OUT], capture_output=True, text=True)
print(OUT, p.stdout.strip())
