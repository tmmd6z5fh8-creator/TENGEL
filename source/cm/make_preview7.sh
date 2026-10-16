#!/bin/sh
# App Storeのプレビュー動画・ポイント版（preview7.html）：iPhone 886×1920・iPad 1200×1600・29.5秒
#   sh make_preview7.sh <出力フォルダ>
# 先に画面を撮る（store_shots7.py の先頭のコメントの2行）。音はCM第7弾の音（bgm7.wav）の同じところをつなぐ：
#   CM 15.6〜29.6（14.0秒）＋ 36.0〜42.4（6.4秒）＋ 52.8〜60.8（8.0秒）＋ 71.2〜72.3（1.1秒）＝ 29.5秒
# Appleの決まり：15〜30秒・30fpsまで・H.264・ステレオ。7Mbps（2パス）でチャットで送れる大きさにする
set -e
OUT="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"; mkdir -p "$OUT"
cd "$(dirname "$0")"
[ -n "$NORENDER" ] || HTML=preview7.html SHOTS=shots_prev7 VW=443 VH=960 DPR=2 DUR=29.5 OUTV=prev7_iphone_noaudio.mp4 python3 render.py full
[ -n "$NORENDER" ] || IPAD=1 HTML=preview7.html SHOTS=shots_prev7_ipad VW=1032 VH=1376 DPR=1.1627907 DUR=29.5 OUTV=prev7_ipad_noaudio.mp4 python3 render.py full
# 音：4つのところを切ってつなぐ（つなぎ目は10ミリ秒だけ小さくして、ぷちっと鳴らないように）・はじめは0.12秒で出す（AACで頭が割れないように）・最後は0.6秒で消す
# 描き出しをやり直さないで音とエンコードだけ：NORENDER=1 sh make_preview7.sh <出力>
ffmpeg -y -loglevel error -i bgm7.wav -filter_complex "\
[0:a]atrim=15.6:29.6,asetpts=PTS-STARTPTS,afade=t=in:d=0.12,afade=t=out:st=13.99:d=0.01[a1];\
[0:a]atrim=36.0:42.4,asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st=6.39:d=0.01[a2];\
[0:a]atrim=52.8:60.8,asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st=7.99:d=0.01[a3];\
[0:a]atrim=71.2:72.3,asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st=0.5:d=0.6[a4];\
[a1][a2][a3][a4]concat=n=4:v=0:a=1[a]" -map "[a]" -ar 48000 -ac 2 prev7_audio.wav
for V in "iphone:886x1920" "ipad:1200x1600"; do
  D=${V%%:*}; S=${V#*:}
  ffmpeg -y -loglevel error -i prev7_${D}_noaudio.mp4 -c:v libx264 -profile:v high -level:v 4.0 -pix_fmt yuv420p -r 30 -b:v 7M -maxrate 9M -bufsize 14M -preset slow \
    -pass 1 -passlogfile prev7log -an -t 29.5 -f mp4 /dev/null
  ffmpeg -y -loglevel error -i prev7_${D}_noaudio.mp4 -i prev7_audio.wav -map 0:v:0 -map 1:a:0 \
    -c:v libx264 -profile:v high -level:v 4.0 -pix_fmt yuv420p -r 30 -b:v 7M -maxrate 9M -bufsize 14M -preset slow -pass 2 -passlogfile prev7log \
    -c:a aac -b:a 256k -ar 48000 -ac 2 -movflags +faststart -t 29.5 "$OUT/tengel_preview7_${D}_${S}.mp4"
done
ls -la "$OUT"
