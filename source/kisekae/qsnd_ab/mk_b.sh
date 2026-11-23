#!/bin/bash
# 聞きくらべ用：今の 音（アプリに 入って いる もの＝a）と、軽い 音（LAME V0 で 包み直した もの＝b）を 作る
#   kisekae/qsnd_ab/mk_b.sh <作業フォルダ>          → <作業フォルダ>/snd/a・snd/b（37こ ずつ）
#   a＝ios/cb_assets/cb_q_*.mp3 の コピー（マスター〈ios/cb_assets/src/qsnd〉と 音は 1ビットも ちがわない：第4.212版で つめものを ぬいた だけ）
#   b＝a を ほどいて V0 で 包み直す（第4.212版の 見つもりの「v0」と 同じ 作り方：同じ 長さ・同じ 位置・チャンネルの 数も 同じ）
#   音は リポジトリに 入れない（作業フォルダは リポジトリの 外に）
set -e
[ -n "$1" ] || { echo "使い方：$0 <作業フォルダ>"; exit 1; }
APP="$(cd "$(dirname "$0")/../../ios/cb_assets" && pwd)"
OUT="$1/snd"
mkdir -p "$OUT/a" "$OUT/b"
n=0
for f in "$APP"/cb_q_bgm*.mp3 "$APP"/cb_q_se*.mp3; do
  b=$(basename "$f")
  cp "$f" "$OUT/a/$b"
  ch=$(ffprobe -v error -show_entries stream=channels -of csv=p=0 "$f")
  ffmpeg -v error -y -i "$f" -map 0:a:0 -map_metadata -1 -c:a libmp3lame -q:a 0 -ac "$ch" -ar 44100 -write_xing 1 "$OUT/b/$b"
  n=$((n+1))
done
echo "made $n"
