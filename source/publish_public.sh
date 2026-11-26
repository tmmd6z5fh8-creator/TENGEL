#!/bin/sh
# 公開の 置き場（公開の リポジトリ TENGEL・GitHub Pages：https://tmmd6z5fh8-creator.github.io/TENGEL/）を 作り直して 送る
#   2026/11/26（まさちゃん「知らない人が勝手に見たりコードコピーしたり、遊んだりできないよね？」→「1」＝コードは 非公開に お引っ越し）：
#   コード（source/・Web版の 画面・説明書・テスト）は 非公開の リポジトリ（TENGEL-dev）だけ。公開の 置き場には App Store版が 読む もの だけ を 置く：
#     ・data/mother_app2.json … 「データの更新」で 読む データ（開催場の 名前なし・AES-GCM で 封じて ある：鍵は アプリの 中だけ）
#     ・cm/tengel3_cm_app.mp4・cm/poster.jpg … アプリの CM（設定の「CMを見る」）
#     ・legal/ … プライバシーポリシー・特定商取引法に基づく表記・サポート（legal/legal.json の 販売する人の 欄が 入って から できる）
#     ・index.html（この 置き場の 説明 だけ・アプリの コードは 入れない）・robots.txt（検索に 出さない）・.nojekyll
#   前の data/mother_app.json（スクランブル：第4.124〜4.154版の テスト版用）と Web版（index.html・sw.js・manual など）は 公開しない。
#   使い方：  sh publish_public.sh <公開の リポジトリの 作業フォルダ>   （先に deploy.sh で ../data・../cm・../legal を 作って おく）
#   いつも 歴史なしの 1つの コミット（orphan）で 置きかえる ＝ 前の 版の ファイルは 公開の 歴史に のこらない
set -e
cd "$(dirname "$0")"
PUB="${1:?公開の リポジトリの 作業フォルダを 指定してね}"
ROOT="$(cd .. && pwd)"
[ -f "$ROOT/data/mother_app2.json" ] || { echo "../data/mother_app2.json が ない（deploy.sh を 先に）"; exit 1; }
[ -f "$ROOT/cm/tengel3_cm_app.mp4" ] || { echo "../cm/tengel3_cm_app.mp4 が ない"; exit 1; }
[ -d "$PUB/.git" ] || { echo "$PUB は git の 作業フォルダ では ない"; exit 1; }
TMP="$(mktemp -d)"
mkdir -p "$TMP/data" "$TMP/cm"
cp "$ROOT/data/mother_app2.json" "$TMP/data/"
cp "$ROOT/cm/tengel3_cm_app.mp4" "$ROOT/cm/poster.jpg" "$TMP/cm/"
if [ -d "$ROOT/legal" ]; then cp -r "$ROOT/legal" "$TMP/"; fi
: > "$TMP/.nojekyll"
printf 'User-agent: *\nDisallow: /\n' > "$TMP/robots.txt"
LINKS=''
[ -f "$TMP/legal/support.html" ] && LINKS="$LINKS<a href=\"legal/support.html\">サポート</a>"
[ -f "$TMP/legal/privacy.html" ] && LINKS="$LINKS<a href=\"legal/privacy.html\">プライバシーポリシー</a>"
[ -f "$TMP/legal/tokushoho.html" ] && LINKS="$LINKS<a href=\"legal/tokushoho.html\">特定商取引法に基づく表記</a>"
cat > "$TMP/index.html" <<EOF
<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>テンゲル</title>
<style>body{margin:0;min-height:100vh;display:grid;place-items:center;text-align:center;background:#16203D;color:#F3F0E6;font-family:-apple-system,BlinkMacSystemFont,'Hiragino Sans','Yu Gothic',sans-serif}main{padding:24px}h1{margin:0 0 10px;font-size:28px;letter-spacing:.06em}p{margin:0;font-size:14px;line-height:1.8;opacity:.85}nav{margin-top:18px;display:flex;gap:16px;justify-content:center;flex-wrap:wrap}a{color:#E2A23B}</style></head>
<body><main><h1>テンゲル</h1><p>iPhone アプリ「テンゲル」が 使う ファイルの 置き場です。</p>${LINKS:+<nav>$LINKS</nav>}</main></body></html>
EOF
cd "$PUB"
git checkout -q --orphan pub-new
git rm -rq --cached . 2>/dev/null || true
find . -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
cp -a "$TMP/." .
git add -A
git -c user.name="${PUB_NAME:-tengel-site}" -c user.email="${PUB_EMAIL:-tengel-site@users.noreply.github.com}" commit -q -m "テンゲル：アプリが 読む ファイル（データの更新・CM・公開する ページ）" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01D2f7uzCM9K3wiyHkskMpMi"
git branch -M pub-new gh-pages
echo "公開の 置き場：$(git ls-files | tr '\n' ' ')"
rm -rf "$TMP"
