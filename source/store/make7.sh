#!/bin/sh
# App Storeの製品ページ（紹介ページ）の素材・ポイント版（CM第7弾の内容）を全部作る
#   sh store/make7.sh <出力フォルダ>
#   → screenshots/iphone_6.9/01〜10.png（1320×2868）・screenshots/ipad_13/01〜10.png（2064×2752）
#     tengel_preview7_iphone_886x1920.mp4・tengel_preview7_ipad_1200x1600.mp4（29.5秒・アプリの画面だけ）
#     listing7.json・掲載テキスト_ポイント版.txt・kit7.html＋media/（掲載キットのページ：claude.ai のアーティファクトで公開）
# ポイントの帯・ロック・購入の画面はイメージ（cm2_shots.py の CM7=1 がテスト用ブラウザの中で足して撮る）。アプリができたら本物の画面で撮り直す
set -e
OUT="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"; mkdir -p "$OUT"
cd "$(dirname "$0")/../cm"
# 1) アプリの画面を撮る（App Store版・架空のレース・保有ポイント1,100P）
TARGET=app CM_PREV=1 CM7=1 CM_PTS_BAL='1,100' CM_VW=443 CM_VH=960 CM_DPR=2 CM_OUT=shots_prev7 python3 cm2_shots.py
TARGET=app CM_PREV=1 CM7=1 CM_PTS_BAL='1,100' CM_IPAD=1 CM_VW=1032 CM_VH=1376 CM_DPR=1.1627907 CM_OUT=shots_prev7_ipad python3 cm2_shots.py
# 2) 画面写真（10枚ずつ）
python3 store_shots7.py "$OUT/screenshots"
# 3) プレビュー動画（音は bgm7.wav の同じところ。先に cm/bgm7.py で bgm7.wav を作っておく）
sh make_preview7.sh "$OUT"
# 4) 貼る文（文字数・バイト数・出さない言葉を確かめる）と、掲載キットのページ
python3 ../store/listing7.py "$OUT"
mkdir -p "$OUT/media"
ffmpeg -y -loglevel error -i "$OUT/tengel_preview7_iphone_886x1920.mp4" -vf scale=444:962 -c:v libx264 -crf 27 -preset slow -pix_fmt yuv420p -c:a aac -b:a 96k -movflags +faststart "$OUT/media/prev_iphone.mp4"
ffmpeg -y -loglevel error -i "$OUT/tengel_preview7_ipad_1200x1600.mp4" -vf scale=600:800 -c:v libx264 -crf 27 -preset slow -pix_fmt yuv420p -c:a aac -b:a 96k -movflags +faststart "$OUT/media/prev_ipad.mp4"
ffmpeg -y -loglevel error -ss 9.6 -i "$OUT/tengel_preview7_iphone_886x1920.mp4" -frames:v 1 -vf scale=444:962 -q:v 3 "$OUT/media/prev_iphone.jpg"
ffmpeg -y -loglevel error -ss 9.6 -i "$OUT/tengel_preview7_ipad_1200x1600.mp4" -frames:v 1 -vf scale=600:800 -q:v 3 "$OUT/media/prev_ipad.jpg"
python3 - "$OUT" <<'EOF'
import os, sys
from PIL import Image
O = sys.argv[1]; K = O + '/media'
for d, w, p in [('iphone_6.9', 360, 'ip'), ('ipad_13', 480, 'pad')]:
    for f in sorted(os.listdir(f'{O}/screenshots/{d}')):
        im = Image.open(f'{O}/screenshots/{d}/{f}'); h = round(im.height * w / im.width)
        im.resize((w, h), Image.LANCZOS).save(f'{K}/{p}_{f[:2]}.jpg', quality=84, optimize=True)
Image.open(os.path.join(os.path.dirname(os.path.abspath('.')), 'icons', 'icon_master_en.png')).convert('RGB').resize((256, 256), Image.LANCZOS).save(f'{K}/icon.png', optimize=True)
EOF
python3 ../store/kit7.py "$OUT"
echo "できたよ: $OUT（kit7.html を media/ といっしょにアーティファクトで公開）"
