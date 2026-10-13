#!/bin/sh
# App Storeに出す素材を作る：プレビュー動画（iPhone・iPad）・スクリーンショット（iPhone 6.9／6.3・iPad 13）・掲載の文・掲載キットのページ
#   sh store/make.sh <出力フォルダ>
# 先に CM の音（cm/bgm2.wav）が要る（cm/make.sh の bgm2.py で作る）
# プレビュー動画は「アプリの画面だけ」で作る（App Store審査ガイドライン 2.3.4：プレビューはアプリの画面の録画だけ。文字を重ねるのはOK）。
#   テロップ・音楽・タイミングはCM（cm2.html）と同じ。CMの前置き・エンブレム・スロットのリール・紙吹雪は使わない（cm/preview.html）
# Appleの決まり（2026/10/13に確認）：プレビュー 15〜30秒・30fpsまで・H.264・iPhone 886×1920・iPad 1200×1600／スクショ PNG（透明なし）
#   iPhone 1320×2868（6.9インチ）・1206×2622（6.3インチ）・iPad 2064×2752（13インチ）／キーワード 100バイト
set -e
OUT="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"; mkdir -p "$OUT"
cd "$(dirname "$0")/../cm"
# 1) アプリの画面を撮る（App Store版・アプリとして開く・架空のレース）
TARGET=app CM_PREV=1 CM_VW=443 CM_VH=960 CM_DPR=2 CM_OUT=shots_prev python3 cm2_shots.py
TARGET=app CM_PREV=1 CM_IPAD=1 CM_VW=1032 CM_VH=1376 CM_DPR=1.1627907 CM_OUT=shots_prev_ipad python3 cm2_shots.py
# 2) プレビュー動画（音なし）→ 音を付けてAppleの形に
HTML=preview.html SHOTS=shots_prev VW=443 VH=960 DPR=2 DUR=29.5 OUTV=prev_iphone_noaudio.mp4 python3 render.py full
IPAD=1 HTML=preview.html SHOTS=shots_prev_ipad VW=1032 VH=1376 DPR=1.1627907 DUR=29.5 OUTV=prev_ipad_noaudio.mp4 python3 render.py full
for V in "iphone:886x1920" "ipad:1200x1600"; do
  D=${V%%:*}; S=${V#*:}
  ffmpeg -y -loglevel error -i prev_${D}_noaudio.mp4 -i bgm2.wav -filter_complex "[1:a]atrim=0:29.5,afade=t=out:st=28.2:d=1.3,asetpts=PTS-STARTPTS[a]" \
    -map 0:v:0 -map "[a]" -c:v libx264 -profile:v high -level:v 4.0 -pix_fmt yuv420p -r 30 -b:v 10M -maxrate 12M -bufsize 20M -preset slow \
    -c:a aac -b:a 256k -ar 48000 -ac 2 -movflags +faststart -t 29.5 "$OUT/tengel_preview_${D}_${S}.mp4"
done
# 3) スクリーンショット
python3 store_shots.py "$OUT/screenshots"
# 4) 掲載の文（文字数・キーワードのバイト数・出さない言葉を確かめる）と、掲載キットのページ（claude.ai のアーティファクト。media/ は小さくした動画と写真）
python3 ../store/listing.py "$OUT"
mkdir -p "$OUT/media"
ffmpeg -y -loglevel error -i "$OUT/tengel_preview_iphone_886x1920.mp4" -vf scale=444:962 -c:v libx264 -crf 27 -preset slow -pix_fmt yuv420p -c:a aac -b:a 96k -movflags +faststart "$OUT/media/prev_iphone.mp4"
ffmpeg -y -loglevel error -i "$OUT/tengel_preview_ipad_1200x1600.mp4" -vf scale=600:800 -c:v libx264 -crf 27 -preset slow -pix_fmt yuv420p -c:a aac -b:a 96k -movflags +faststart "$OUT/media/prev_ipad.mp4"
ffmpeg -y -loglevel error -ss 6.8 -i "$OUT/tengel_preview_iphone_886x1920.mp4" -frames:v 1 -vf scale=444:962 -q:v 3 "$OUT/media/prev_iphone.jpg"
ffmpeg -y -loglevel error -ss 6.8 -i "$OUT/tengel_preview_ipad_1200x1600.mp4" -frames:v 1 -vf scale=600:800 -q:v 3 "$OUT/media/prev_ipad.jpg"
python3 - "$OUT" <<'EOF'
import os, sys
from PIL import Image
O = sys.argv[1]; K = O + '/media'
for d, w in [('iphone_6.9', 360), ('ipad_13', 480)]:
    for f in sorted(os.listdir(f'{O}/screenshots/{d}')):
        im = Image.open(f'{O}/screenshots/{d}/{f}'); h = round(im.height * w / im.width)
        im.resize((w, h), Image.LANCZOS).save(f'{K}/{"ip" if d.startswith("iphone") else "pad"}_{f[:2]}.jpg', quality=84, optimize=True)
Image.open(os.path.join(os.path.dirname(os.path.abspath('.')), 'icons', 'icon_master_en.png')).convert('RGB').resize((256, 256), Image.LANCZOS).save(f'{K}/icon.png', optimize=True)
EOF
python3 ../store/kit.py "$OUT"
echo "できたよ: $OUT（kit.html を media/ といっしょにアーティファクトで公開）"
