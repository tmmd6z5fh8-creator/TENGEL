#!/bin/sh
# テンゲルⅢ iPhoneアプリ：source/ からアプリを作って、リポジトリの一番上（公開されるファイル）に置く
# 使い方：  cd source && APP_VER=2026.10.12 sh deploy.sh
#   基盤データ（hist.json）を入れ直したときは MOTHER_VER も前と違う値にする（例：最後のレースの日付）
set -e
cd "$(dirname "$0")"
node build.js
OUT="$(mktemp -d)/pwa"
python3 build_pwa.py "$OUT"
cp "$OUT"/index.html "$OUT"/manifest.webmanifest "$OUT"/sw.js "$OUT"/version.json "$OUT"/icon3-*.png ..
rm -f chk*.js
echo "公開用ファイルを更新したよ: $(cat "$OUT"/version.json)"
