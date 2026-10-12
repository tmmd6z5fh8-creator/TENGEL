#!/bin/sh
# テンゲルのCM（前置き15秒＋スロット新台CM風30秒＝45秒）を作り直す → ../cm_media/ に2つ
#   tengel3_cm.mp4      … Web版（ホーム画面のアプリ）で見せる版（最後に「ホーム画面に追加して使える」）
#   tengel3_cm_app.mp4  … App Store版のアプリの中で見せる版（最後に「iPhone・iPadで、いつでも判定」。cm2.html?v=app）
#   どちらも最後に注意書き（架空のレース・約束しない・APIキー・20歳・非公式・iPhoneの商標。Web版はJRA/WIN5の商標も）
#   App Store版は、画面もApp Store版で撮る（shots_app：競馬場・団体・版の名前が出ない。WIN5→5重勝・マザーデータ2）
#   1) アプリの画面を撮る（架空のレース・架空のデータ。テスト用ブラウザの中だけ）
#   2) 映像（cm2.html＝本編、pro.html＝前置き）を1コマずつ撮る  3) 音を作る  4) つないで、送れる大きさ（30MB以下）にする
# CMでは「大井」「第13改訂版」の文字は出さない（cm2_shots.py の SCRUB_JS で画面の文字だけ置きかえる）
set -e
cd "$(dirname "$0")"
python3 cm2_shots.py                                                    # → shots/（Web版の画面）
TARGET=app python3 cm2_shots.py                                         # → shots_app/（App Store版の画面）
python3 render.py full                                                  # → video.mp4（本編30秒・Web版）
CMQ='?v=app' SHOTS=shots_app OUTV=video_app.mp4 python3 render.py full   # → video_app.mp4（本編30秒・App Store版）
HTML=pro.html DUR=15.0 OUTV=pro_video.mp4 python3 render_pro.py full   # → pro_video.mp4（前置き15秒・共通）
python3 bgm2.py; GAIN_DB=-3.6 python3 pro_bgm.py         # → bgm2.wav・pro_bgm.wav（どちらも -14 LUFS くらい）
ffmpeg -y -loglevel error -i pro_bgm.wav -i bgm2.wav -filter_complex "[0:a][1:a]concat=n=2:v=0:a=1[a]" -map "[a]" full.wav
for V in "" "_app"; do
  printf "file 'pro_video.mp4'\nfile 'video$V.mp4'\n" > concat.txt
  ffmpeg -y -loglevel error -f concat -safe 0 -i concat.txt -c copy full_video$V.mp4
  ffmpeg -y -loglevel error -i full_video$V.mp4 -i full.wav -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart full45$V.mp4
  ffmpeg -y -loglevel error -i full45$V.mp4 -c:v libx264 -preset slow -b:v 4500k -maxrate 7000k -bufsize 9000k -pix_fmt yuv420p -pass 1 -passlogfile p2log -an -f mp4 /dev/null
  ffmpeg -y -loglevel error -i full45$V.mp4 -c:v libx264 -preset slow -b:v 4500k -maxrate 7000k -bufsize 9000k -pix_fmt yuv420p -pass 2 -passlogfile p2log -c:a copy -movflags +faststart ../cm_media/tengel3_cm$V.mp4
done
ffmpeg -y -loglevel error -ss 7.6 -i ../cm_media/tengel3_cm.mp4 -frames:v 1 -vf scale=540:960 -q:v 4 ../cm_media/poster.jpg
echo "できたよ: ../cm_media/tengel3_cm.mp4・tengel3_cm_app.mp4"
