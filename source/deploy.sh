#!/bin/sh
# テンゲルⅢ iPhoneアプリ：source/ からアプリを作って、リポジトリの一番上（公開されるファイル）に置く
# 使い方：  cd source && APP_VER=2026.10.12-8 sh deploy.sh
#   基盤データ（hist.json）を入れ直したときは MOTHER_VER も前と違う値にする（例：最後のレースの日付）
set -e
cd "$(dirname "$0")"
node build.js
OUT="$(mktemp -d)/pwa"
python3 build_pwa.py "$OUT"
cp "$OUT"/index.html "$OUT"/manifest.webmanifest "$OUT"/sw.js "$OUT"/version.json "$OUT"/icon3-*.png ..
# 説明書（manual.html と写真の manual/）
cp "$OUT"/manual.html ..
rm -rf ../manual && cp -r "$OUT"/manual ..
# App Store版の「データの更新」で読むデータ（data/mother_app.json：開催場の名前なし）
rm -rf ../data && cp -r "$OUT"/data ..
# CM（紹介動画と表紙。cm_media/ から）
rm -rf ../cm && if [ -d "$OUT"/cm ]; then cp -r "$OUT"/cm ..; fi
# 公開するページ（プライバシーポリシー・特定商取引法に基づく表記・サポート）：legal/legal.json の販売する人の欄が入っているものだけできる
rm -rf ../legal && if [ -d "$OUT"/legal ]; then cp -r "$OUT"/legal ..; echo "公開するページ: $(ls "$OUT"/legal | tr '\n' ' ')"; else echo "公開するページ: まだなし（legal/legal.json の seller・email が空）"; fi
rm -f chk*.js
echo "公開用ファイルを更新したよ: $(cat "$OUT"/version.json)"
