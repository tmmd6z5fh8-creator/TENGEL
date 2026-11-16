#!/bin/bash
# テンゲル iOSアプリの確認（GitHubのMacで動かす。.github/workflows/ios.yml から呼ぶ）
#  1) Swift 5（いまの Package.swift）でシミュレーター用に作る
#  2) Swift 6 の厳しいチェックでも作れるか（Swift Playgrounds が Package.swift を作り直したとき用）
#  3) 実機（iPhone・iPad）用に Release で作れるか（署名なし）
#  4) iPhoneのシミュレーター：1回目（買い目を予約・的中ボタンの演出・自動バックアップ・画面のスクショ）→ 2回目（開き直しても記録が残る・保存場所を消す）→ 3回目（「戻す？」→ 戻す）
#  5) iPadのシミュレーター：1回目だけ（iPhone用のアプリなので、互換モードで iPhone の大きさの画面になる。スクショで確かめる）
#  6) iPadの 広い 窓（第4.156版）：Package.swift に .pad を 足して 作った もの（Swift Playgrounds の ▶ と 同じ＝iPad の 画面いっぱいの 窓）で、
#     アプリが iPhone の 大きさ（390×844）で まん中に 出るか（Webの 画面の 幅 390・まわりは 黒・スクショ）。出す アプリ（1〜5）は .phone だけの まま
#  7) テスト版の「ぜんぶ リセット」（第4.169版）：消す しかけ（ci/reset_all.js）を テストの スクリプトと いっしょに 入れて、iPhone の シミュレーターで
#     「リセット する」→ 開き直す → 保存場所・端末の おぼえが 空・「はじめる」の 画面・「前の記録が見つかったよ」が 出ない を 見る（出す アプリには 入れない）
#  8) 馬カードバトルの「部屋」（第4.176版）：iPhone と iPad の シミュレーターを 同時に 起こして、iPhone が 部屋を 作る・iPad が 同じ 部屋番号で 入る
#     ＝本物の つなぎ役（Room.swift：MultipeerConnectivity）で つながって、2台とも 自動で さいごまで 対戦する（結果が うらおもてに なって いるか）。
#     つながらない ときは とちゅうの ようす（つながりの できごと・画面の 写真・ログ）を 残す（GitHub の Mac では 近くの 端末を さがす しくみが 止められて いる ことが ある）
#     1回目の 中でも コンピュータとの 対戦を 最後まで 動かす（cb-menu・cb-game・cb-end の 写真）
# 結果は results/（summary.txt・ログ・report-*.json・スクショ）。ワークフローが ios-ci-<ランナー> ブランチに置く
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/results"; rm -rf "$OUT"; mkdir -p "$OUT/shots"
PKG="$ROOT/Tengel.swiftpm"
S="$OUT/summary.txt"
say() { echo "$*" | tee -a "$S"; }

say "== runner: macOS $(sw_vers -productVersion) $(uname -m) (${RUNNER_LABEL:-?})"
say "== xcode: $(xcodebuild -version 2>&1 | tr '\n' ' ')"
ls /Applications | grep -i xcode > "$OUT/xcodes.txt" 2>&1
xcrun simctl list runtimes > "$OUT/runtimes.txt" 2>&1
xcrun simctl list devices available > "$OUT/devices.txt" 2>&1

# いちばん新しいiOSのシミュレーター（好みの機種があればそれ）
pick() {
  xcrun simctl list devices available -j | python3 -c '
import json, re, sys
kind, prefer = sys.argv[1], sys.argv[2]
best = None
for rt, devs in json.load(sys.stdin)["devices"].items():
    m = re.search(r"iOS-(\d+)-(\d+)", rt)
    if not m:
        continue
    v = (int(m.group(1)), int(m.group(2)))
    for d in devs:
        if not d["name"].startswith(kind) or not d.get("isAvailable", True):
            continue
        key = (v, 1 if re.search(prefer, d["name"]) else 0)
        if best is None or key > best[0]:
            best = (key, d["udid"], d["name"])
print("%s|%s|iOS %d.%d" % (best[1], best[2], best[0][0][0], best[0][0][1]) if best else "")
' "$1" "$2"
}
IP=$(pick "iPhone" '^iPhone 1[6-9]$'); PD=$(pick "iPad" '^iPad Air 11|^iPad \(|^iPad Pro 11')
IPHONE=${IP%%|*}; IPAD=${PD%%|*}
say "== iPhone: $IP"
say "== iPad: $PD"

cd "$PKG" || exit 0
xcodebuild -list > "$OUT/xcodebuild-list.txt" 2>&1
SCHEME="テンゲル"
if ! grep -q "テンゲル" "$OUT/xcodebuild-list.txt"; then
  SCHEME=$(awk '/Schemes:/{f=1;next} f&&NF{sub(/^ +/,"");print;exit}' "$OUT/xcodebuild-list.txt")
fi
say "== scheme: $SCHEME"

issues() { grep -E "(error|warning):" "$1" | grep -v "^ld: warning" | sed -E 's#^/[^ ]*/(Tengel[^/]*\.swiftpm|pkg[0-9])/##' | sort -u > "$2"; say "   errors: $(grep -c 'error:' "$2")  warnings: $(grep -c 'warning:' "$2")"; }

# 1) Swift 5（いまの形）・シミュレーター
T0=$(date +%s)
xcodebuild -scheme "$SCHEME" -destination "platform=iOS Simulator,id=$IPHONE" -derivedDataPath "$ROOT/dd" -configuration Debug CODE_SIGNING_ALLOWED=NO build > "$OUT/build.log" 2>&1
BUILD=$?
say "== build Swift5 Debug simulator: exit $BUILD ($(( $(date +%s) - T0 ))s)"
issues "$OUT/build.log" "$OUT/build-issues.txt"
tail -60 "$OUT/build.log" > "$OUT/build-tail.txt"

# 2) Swift 6 の厳しいチェック
rm -rf /tmp/p6 && mkdir -p /tmp/p6 && cp -R "$PKG" /tmp/p6/Tengel.swiftpm
sed -i '' '1s#.*#// swift-tools-version: 6.0#' /tmp/p6/Tengel.swiftpm/Package.swift
(cd /tmp/p6/Tengel.swiftpm && xcodebuild -scheme "$SCHEME" -destination "generic/platform=iOS Simulator" -derivedDataPath "$ROOT/dd6" -configuration Debug CODE_SIGNING_ALLOWED=NO build > "$OUT/build6.log" 2>&1)
B6=$?
say "== build Swift6 Debug simulator: exit $B6"
issues "$OUT/build6.log" "$OUT/build6-issues.txt"
[ $B6 -ne 0 ] && tail -60 "$OUT/build6.log" > "$OUT/build6-tail.txt"

# 3) 実機用 Release（App Storeに出すときと同じ形・署名なし）
xcodebuild -scheme "$SCHEME" -destination "generic/platform=iOS" -derivedDataPath "$ROOT/ddr" -configuration Release CODE_SIGNING_ALLOWED=NO build > "$OUT/build-release.log" 2>&1
BR=$?
say "== build Swift5 Release device: exit $BR"
issues "$OUT/build-release.log" "$OUT/build-release-issues.txt"
[ $BR -ne 0 ] && tail -60 "$OUT/build-release.log" > "$OUT/build-release-tail.txt"
RAPP=$(find "$ROOT/ddr/Build/Products" -maxdepth 2 -name "*.app" -type d 2>/dev/null | head -1)
if [ -n "$RAPP" ]; then
  (cd "$RAPP" && find . | sort) > "$OUT/app-files-release.txt"
  say "   release app: $(du -sh "$RAPP" | cut -f1)  selftest in release: $(strings "$RAPP"/* 2>/dev/null | grep -c tengelSelfTest)"
fi

[ $BUILD -ne 0 ] && { say "== build failed: simulator runs skipped"; exit 0; }
APP=$(find "$ROOT/dd/Build/Products" -maxdepth 2 -name "*.app" -type d | head -1)
say "== app: $(basename "$APP")"
(cd "$APP" && find . | sort) > "$OUT/app-files.txt"
plutil -convert xml1 -o "$OUT/Info.plist.xml" "$APP/Info.plist"
BID=$(/usr/libexec/PlistBuddy -c "Print CFBundleIdentifier" "$APP/Info.plist")
say "   bundle id: $BID  version: $(/usr/libexec/PlistBuddy -c 'Print CFBundleShortVersionString' "$APP/Info.plist") ($(/usr/libexec/PlistBuddy -c 'Print CFBundleVersion' "$APP/Info.plist"))"
# iPhone用のアプリ（21章）：UIDeviceFamily は 1（iPhone）だけ・向きは縦だけ・起動の画面の設定（UILaunchScreen。iOS 27 の SDK で作るときに必要）がある
FAM=$(/usr/libexec/PlistBuddy -c "Print UIDeviceFamily" "$APP/Info.plist" 2>/dev/null | grep -E '^\s*[0-9]+' | tr -d ' ' | tr '\n' ',')
ORI=$(/usr/libexec/PlistBuddy -c "Print UISupportedInterfaceOrientations~iphone" "$APP/Info.plist" 2>/dev/null | grep -c UIInterfaceOrientation)
ORIPAD=$(/usr/libexec/PlistBuddy -c "Print UISupportedInterfaceOrientations~ipad" "$APP/Info.plist" 2>/dev/null | grep -c UIInterfaceOrientation)
LS=$(/usr/libexec/PlistBuddy -c "Print UILaunchScreen" "$APP/Info.plist" > /dev/null 2>&1 && echo yes || echo no)
say "   iphone-only: UIDeviceFamily=${FAM:-?} orientations(iphone)=${ORI:-0} orientations(ipad)=${ORIPAD:-0} launchscreen=$LS $([ "$FAM" = "1," ] && [ "${ORI:-0}" = "1" ] && [ "$LS" = "yes" ] && echo OK || echo CHECK)"
say "   web files: $(grep -cE '\.(html|webp|jpg)$' "$OUT/app-files.txt")  index.html at: $(grep 'index.html' "$OUT/app-files.txt" | tr '\n' ' ')"
# 第4.62版：アプリの 言葉は 日本語（写真を 選ぶ 窓などが 日本語に なる）：CFBundleDevelopmentRegion=ja・ja.lproj が 入っている
REG=$(/usr/libexec/PlistBuddy -c "Print CFBundleDevelopmentRegion" "$APP/Info.plist" 2>/dev/null)
LPROJ=$(grep -c 'ja.lproj' "$OUT/app-files.txt")
say "   language: CFBundleDevelopmentRegion=${REG:-?} ja.lproj files=$LPROJ localizations=$(/usr/libexec/PlistBuddy -c 'Print CFBundleLocalizations' "$APP/Info.plist" 2>/dev/null | grep -vE '^\s*(Array|\{|\}|\(|\))' | tr -d ' ' | tr '\n' ',') $([ "$REG" = "ja" ] && [ "$LPROJ" -ge 1 ] && echo OK || echo CHECK)"

# 第4.176版：馬カードバトルの 部屋（Room.swift）：近くの iPhone と つながる ための 設定（説明の 文・Bonjour の 名前 2つ）が Info.plist に 入って いる
LNP=$(/usr/libexec/PlistBuddy -c "Print NSLocalNetworkUsageDescription" "$APP/Info.plist" 2>/dev/null)
BJN=$(/usr/libexec/PlistBuddy -c "Print NSBonjourServices" "$APP/Info.plist" 2>/dev/null | grep -c '_tengel-cb\._')
say "   local network: purpose=$([ -n "$LNP" ] && echo yes || echo no) bonjour=${BJN:-0} $([ -n "$LNP" ] && [ "${BJN:-0}" = "2" ] && echo OK || echo CHECK)"
CBPY='
# start の op（相手の 手札）は 7 か 6：コンピュータが もう セットして いれば 6（セットは すぐ 確定する：第4.176版の 流れ。run 143 では 4〈手札 5まいの とき〉だった）
# 第4.178版：5ターン・手札 7まい（山札 16）・メニューの ボタン 6つ（「設定」が ふえた）・設定の 窓（BGM・効果音・エフェクト）・火の あかりの ゆれ・エフェクト オフ／オン・捨て札は 10まい 以上
# 第4.179版：メニューに バトルコインの 行（はじめ 0枚）・コンピュータに 勝ったら 1枚
import json, sys
o = json.load(open(sys.argv[1])).get("cb") or {}
rm = o.get("room") or {}; rb = o.get("roomBad") or {}; st = o.get("start") or {}; au = o.get("auto") or {}; s = o.get("state") or {}
fd = o.get("fd") or []
ok = (o.get("fab") or [])[:4] == ["tcFab", "oshiFab", "cbFab", "figFab"] and (o.get("col") is True or o.get("g2") is True) and len(fd) == 4 and len(set(fd)) == 1 and 36 <= fd[0] <= 66 and o.get("clear") is True and o.get("api") == "object" and rm.get("ok") is True and rm.get("state") == "idle" and rb.get("ok") is False and rb.get("why") == "room" \
     and o.get("open") is True and len(o.get("menu") or []) == 6 and o.get("roomBtn") == [True, True] and st.get("hand") == 7 and st.get("op") in (6, 7) and st.get("deck") == 16 and st.get("turn") == 1 and st.get("turns") == 5 and au.get("ended") is True \
     and o.get("res") in ("win", "lose", "draw") and (o.get("discard") or 0) >= 10 and bool(o.get("gift")) and (s.get("win", 0) + s.get("lose", 0) + s.get("draw", 0)) == 1 and o.get("closed") is True \
     and (o.get("res") != "win" or o.get("tokens") == 6) and "バトルコイン 0" in (o.get("coinl") or "") and s.get("coin") == (1 if o.get("res") == "win" else 0)
se = o.get("sets") or {}; bg = o.get("bgm") or {}; fire = o.get("fire") or []
ok2 = se.get("fx") is True and isinstance(se.get("se"), bool) and isinstance(se.get("bgm"), bool) and bg.get("on") is False and abs((bg.get("len") or 0) - 80.53) < 0.02 and len(fire) == 2 and all(f.startswith("cbfire ") for f in fire) \
      and o.get("gear") == "bgm,se,fx" and o.get("nofx") is True and o.get("fxBack") is True and not o.get("setsErr")
print("fab %s column %s 2x2 %s icon %s clear-of-kise %s (view %s kise %s fabs %s) room-api %s bad-room %s open %s start %s played %s res %s wins %s discard %s tokens %s closed %s -> %s" % ((o.get("fab") or [])[:4], o.get("col"), o.get("g2"), fd[:1], o.get("clear"), o.get("view"), o.get("kise"), o.get("fabRect"), rm, rb.get("why"), o.get("open"), st, au.get("kinds"), o.get("res"), o.get("wins"), o.get("discard"), o.get("tokens"), o.get("closed"), "OK" if ok else "CHECK " + json.dumps(o, ensure_ascii=False)[:400]))
print("   card battle settings: sets %s bgm %s fire %s gear %s fx-off %s fx-back %s err %s -> %s" % (se, bg, fire, o.get("gear"), o.get("nofx"), o.get("fxBack"), o.get("setsErr"), "OK" if ok2 else "CHECK"))
'
# 第4.177版：お世話の 札の「描く 命令を 書きとめる 役」（tc/tc_care.js の REC）を 本物の WebKit で：16コマ（描く 8〈はじめの 2コマ・場面が かわった 3コマ・中身の かわる 紙の 2コマ・かくれた あとの 1コマ〉・同じ 絵で 描かない 6・かくれて いて 描かない 2）・
#   じかに 描いた 紙と 1画素も ちがわない（くらべた 14コマ・べつの 紙との 見くらべも 0）・読んだ 値（線の 太さ 2・こさ 0.375）
RECPY='
import json, sys
o = json.load(open(sys.argv[1])).get("hudrec") or {}; s = o.get("stat") or {}; rd = o.get("reads") or []
ok = o.get("have") is True and o.get("ok0") is True and o.get("ok1") is True and s == {"frames": 16, "drawn": 8, "same": 6, "hidden": 2, "forced": 2, "bad": 0} and o.get("checks") == 14 and o.get("diff") == 0 \
     and (o.get("px") or 0) > 0.05 and len(rd) == 3 and rd[0] == 2 and rd[1] == 0.375 and rd[2] == 32
print("have %s ok %s/%s frames %s drawn %s same %s hidden %s forced %s different %s (compared %s) ref-diff %s filled %s reads %s names %s -> %s" % (o.get("have"), o.get("ok0"), o.get("ok1"), s.get("frames"), s.get("drawn"), s.get("same"), s.get("hidden"), s.get("forced"), s.get("bad"), o.get("checks"), o.get("diff"), o.get("px"), rd, o.get("names"), "OK" if ok else "CHECK " + json.dumps(o, ensure_ascii=False)[:400]))
'
waitfile() { local f="$1" t="${2:-60}" i=0; while [ $i -lt $((t * 4)) ]; do [ -f "$f" ] && return 0; sleep 0.25; i=$((i + 1)); done; return 1; }
shot() {
  local u="$1" name="$2" w="${3:-700}"
  xcrun simctl io "$u" screenshot --type=png "$OUT/shots/$name.png" > /dev/null 2>&1 || return 0
  sips -s format jpeg -s formatOptions 75 --resampleWidth "$w" "$OUT/shots/$name.png" --out "$OUT/shots/$name.jpg" > /dev/null 2>&1 && rm -f "$OUT/shots/$name.png"
}
# 1回分：selftest.js を置いて起動 → 合図（mark）ごとにスクショ → 結果（report）を集める
phase() {
  local U="$1" DEV="$2" PH="$3" W="$4"; shift 4
  local D; D=$(xcrun simctl get_app_container "$U" "$BID" data 2> /dev/null)
  [ -z "$D" ] && { say "   $DEV $PH: app container not found (not installed?)"; return 0; }
  mkdir -p "$D/Documents"; rm -f "$D/Documents"/mark-* "$D/Documents"/report-* "$D/Documents"/ack-*
  # 5回目（第4.169版：テスト版の「ぜんぶ リセット」）だけ：テスト版の 印と 消す しかけ（ci/reset_all.js＝テスト版の index.html の 先頭に 入る ものと 同じ）を 先に 入れる
  { echo "window.__ST_PHASE = $PH; window.__ST_DEVICE = '$DEV';"; if [ "$PH" = "5" ]; then echo "window.__TEST = true;"; cat "$ROOT/ci/reset_all.js"; fi; cat "$ROOT/ci/selftest.js"; } > "$D/Documents/selftest.js"
  cp "$ROOT"/ci/ocr/*.jpg "$D/Documents/" 2> /dev/null   # 画像の読み取りの見本（架空のオッズ画面）
  xcrun simctl launch "$U" "$BID" -tengelSelfTest >> "$OUT/$DEV-launch.txt" 2>&1
  for m in "$@"; do
    case "$m" in
      report-*)
        if waitfile "$D/Documents/$m.json" 90; then cp "$D/Documents/$m.json" "$OUT/$DEV-$m.json"; say "   $DEV $PH: $m"
        else say "   $DEV $PH: $m TIMEOUT"; shot "$U" "$DEV-$PH-timeout-$m" "$W"; break; fi ;;
      *)
        if waitfile "$D/Documents/mark-$m.txt" 90; then sleep 0.8; shot "$U" "$DEV-$PH-$m" "$W"; echo ok > "$D/Documents/ack-$m.txt"
        else say "   $DEV $PH: mark $m TIMEOUT"; shot "$U" "$DEV-$PH-timeout-$m" "$W"; break; fi ;;
    esac
  done
  for f in "$D/Documents"/report-*.json; do [ -f "$f" ] && [ ! -f "$OUT/$DEV-$(basename "$f")" ] && cp "$f" "$OUT/$DEV-$(basename "$f")"; done
  for f in "$D/Documents"/report-crash-*.json; do [ -f "$f" ] && cp "$f" "$OUT/$DEV-$(basename "$f")" && say "   $DEV $PH: CRASH $(basename "$f")"; done
  cp "$D/Library/Application Support/tengel-autobackup.json" "$OUT/$DEV-$PH-autobackup.json" 2> /dev/null
  xcrun simctl terminate "$U" "$BID" > /dev/null 2>&1; sleep 1.5
}
applog() { xcrun simctl spawn "$1" log show --last 15m --style compact --predicate 'process CONTAINS "テンゲル" OR (process CONTAINS "WebContent" AND eventMessage CONTAINS[c] "error")' 2>/dev/null | tail -400 > "$OUT/$2-log.txt"; }

P1="gate-first main rsv-ov fx-push fx-board fx-fz-push fx-fz-result fx-sgd-still fx-sd fx-sd-board fx-gk fx-gk-board board-carry board-carry-slip board-carry-miss ks-judge ks-push ks-board ks-set ks-conf ks-tengel ks-pack ks-pack-wall points settings backup about rec numpad manual-ov manual-ov-item cb-menu cb-game cb-end report-1 manual manual-item report-manual back report-back"
# 4) iPhone
if [ -n "$IPHONE" ]; then
  xcrun simctl boot "$IPHONE" > /dev/null 2>&1; xcrun simctl bootstatus "$IPHONE" -b > /dev/null 2>&1
  xcrun simctl ui "$IPHONE" appearance light > /dev/null 2>&1
  xcrun simctl install "$IPHONE" "$APP" > "$OUT/iphone-install.txt" 2>&1 && say "== iPhone: installed"
  phase "$IPHONE" iphone 1 700 $P1
  # 第4.170版：本物の 文字認識（Vision）で、見本の 画像（架空の レース）から 馬の 名前（馬番ごと）が 読めたか。12頭の うち 10頭 以上が 見本と 同じ なら OK（読みまちがいは 中身で 見る）
  if [ -f "$OUT/iphone-report-1.json" ]; then
    say "   names: $(python3 -c '
import json, sys
o = json.load(open(sys.argv[1])).get("ocr") or {}; nm = o.get("names") or {}
want = {"1": "サンライズゴールド", "2": "テンゲルクイーン", "3": "ナイトレイン", "4": "ブルーハーバー", "5": "コスモスカイ", "6": "ミラクルアロー", "7": "ハッピーデイズ", "8": "シルバーウィンド", "9": "ドリームキャッチャー", "10": "ロイヤルステップ", "11": "スターダストメモリー", "12": "ラストサムライ"}
same = sum(1 for k, v in want.items() if nm.get(k) == v); bad = {k: nm.get(k) for k in want if nm.get(k) != want[k]}
print("read %d same %d/12 -> %s%s" % (len(nm), same, "OK" if same >= 10 else "CHECK", ("  not same: " + json.dumps(bad, ensure_ascii=False)) if bad else ""))
' "$OUT/iphone-report-1.json" 2>&1)"
    # 第4.172版：テンゲルBGM は なくした → 本物の WebKit で しかけ（window.TengelBgm）と 設定の 札が 入って いない・爆発の 動画の 形（H.264：第4.171版）を 読める
    say "   bgm: $(python3 -c '
import json, sys
o = json.load(open(sys.argv[1])).get("bgm") or {}
ok = ("has" in o) and (not o.get("has")) and (not o.get("card")) and o.get("h264")
print("tengel-bgm api %s card %s (none expected) h264 %s -> %s" % (o.get("has"), o.get("card"), o.get("h264") or "-", "OK" if ok else "CHECK"))
' "$OUT/iphone-report-1.json" 2>&1)"
  fi
  [ -f "$OUT/iphone-report-1.json" ] && say "   card battle: $(python3 -c "$CBPY" "$OUT/iphone-report-1.json" 2>&1)"
  [ -f "$OUT/iphone-report-1.json" ] && say "   care recorder: $(python3 -c "$RECPY" "$OUT/iphone-report-1.json" 2>&1)"
  phase "$IPHONE" iphone 2 700 report-2
  phase "$IPHONE" iphone 3 700 offer restored report-3 report-link
  sleep 3; shot "$IPHONE" "iphone-3-link-safari" 700
  # ダークモードで1枚
  xcrun simctl ui "$IPHONE" appearance dark > /dev/null 2>&1
  xcrun simctl launch "$IPHONE" "$BID" > /dev/null 2>&1; sleep 8; shot "$IPHONE" "iphone-dark" 700
  xcrun simctl terminate "$IPHONE" "$BID" > /dev/null 2>&1
  # 7) テスト版の「ぜんぶ リセット」（第4.169版）を 本物の WKWebView で：出す アプリには 消す しかけが ない ので、テストの スクリプトと いっしょに 入れる（phase の 5回目）。
  #    アプリの 中身を ぜんぶ 消す ので、iPhone の さいごに 動かす
  xcrun simctl ui "$IPHONE" appearance light > /dev/null 2>&1
  if [ -f "$ROOT/ci/reset_all.js" ]; then
    phase "$IPHONE" iphone 5 700 reset-confirm report-5a reset-gate reset-main report-5
    if [ -f "$OUT/iphone-report-5.json" ]; then
      say "   reset: $(python3 -c '
import json, os, sys
a = json.load(open(sys.argv[1])) if os.path.exists(sys.argv[1]) else {}; r = json.load(open(sys.argv[2]))
bf = a.get("before") or {}; af = r.get("after") or {}; g = r.get("gate") or {}; d = af.get("did") or {}; m = r.get("main") or {}; bk = r.get("backupAfter") or {}
ok = (a.get("hasReset") is True and bf.get("bets", 0) >= 1 and bf.get("setting") == "x" and "tengel.st5" in (bf.get("ls") or []) and (bf.get("backup") or {}).get("n", 0) >= 1
      and r.get("db") == "ok" and d.get("native") == 4 and g.get("first") is True and af.get("bets") == 0 and af.get("setting") is None and af.get("memOnly") == "" and af.get("offer") is False
      and "tengel.st5" not in (af.get("ls") or ["?"]) and "tengel.wipe" not in (af.get("ls") or ["?"]) and "st5" not in (af.get("ss") or ["?"]) and af.get("total") == 10000 and r.get("write") == 7
      and m.get("offer") is False and m.get("tabbar") is True and bk.get("n") == 0 and bk.get("reset") is False and not r.get("errors") and not r.get("failed"))
print("before bets %s setting %s backup %s -> after db %s native %s first-gate %s bets %s setting %s total %s offer %s write %s backup n %s errors %d -> %s" % (bf.get("bets"), bf.get("setting"), (bf.get("backup") or {}).get("n"), r.get("db"), d.get("native"),
      g.get("first"), af.get("bets"), af.get("setting"), af.get("total"), af.get("offer"), r.get("write"), bk.get("n"), len(r.get("errors") or []), "OK" if ok else "CHECK"))
' "$OUT/iphone-report-5a.json" "$OUT/iphone-report-5.json" 2>&1)"
    else
      say "   reset: report-5 not found CHECK"
    fi
  fi
  applog "$IPHONE" iphone
  xcrun simctl shutdown "$IPHONE" > /dev/null 2>&1
fi
# 5) iPad
if [ -n "$IPAD" ]; then
  xcrun simctl boot "$IPAD" > /dev/null 2>&1; xcrun simctl bootstatus "$IPAD" -b > /dev/null 2>&1
  xcrun simctl ui "$IPAD" appearance light > /dev/null 2>&1
  xcrun simctl install "$IPAD" "$APP" > "$OUT/ipad-install.txt" 2>&1 && say "== iPad: installed"
  phase "$IPAD" ipad 1 1000 $P1
  [ -f "$OUT/ipad-report-1.json" ] && say "   card battle (ipad): $(python3 -c "$CBPY" "$OUT/ipad-report-1.json" 2>&1)"
  [ -f "$OUT/ipad-report-1.json" ] && say "   care recorder (ipad): $(python3 -c "$RECPY" "$OUT/ipad-report-1.json" 2>&1)"
  applog "$IPAD" ipad
  xcrun simctl shutdown "$IPAD" > /dev/null 2>&1
fi
# 6) iPad の 広い 窓（.pad を 足して 作る：リポジトリの Package.swift は かえない）
if [ -n "$IPAD" ]; then
  rm -rf /tmp/pw && mkdir -p /tmp/pw && cp -R "$PKG" /tmp/pw/Tengel.swiftpm
  perl -0pi -e 's/supportedDeviceFamilies:\s*\[\s*\.phone\s*\]/supportedDeviceFamilies: [.pad, .phone]/' /tmp/pw/Tengel.swiftpm/Package.swift
  if grep -q 'supportedDeviceFamilies: \[.pad, .phone\]' /tmp/pw/Tengel.swiftpm/Package.swift; then
    T0=$(date +%s)
    (cd /tmp/pw/Tengel.swiftpm && xcodebuild -scheme "$SCHEME" -destination "platform=iOS Simulator,id=$IPAD" -derivedDataPath "$ROOT/ddw" -configuration Debug CODE_SIGNING_ALLOWED=NO build > "$OUT/build-wide.log" 2>&1)
    BW=$?
    say "== build wide (.pad added) Debug simulator: exit $BW ($(( $(date +%s) - T0 ))s)"
    [ $BW -ne 0 ] && tail -60 "$OUT/build-wide.log" > "$OUT/build-wide-tail.txt"
    WAPP=$(find "$ROOT/ddw/Build/Products" -maxdepth 2 -name "*.app" -type d 2>/dev/null | head -1)
    if [ $BW -eq 0 ] && [ -n "$WAPP" ]; then
      say "   wide app: UIDeviceFamily=$(/usr/libexec/PlistBuddy -c "Print UIDeviceFamily" "$WAPP/Info.plist" 2>/dev/null | grep -E '^\s*[0-9]+' | tr -d ' ' | tr '\n' ',')"
      xcrun simctl boot "$IPAD" > /dev/null 2>&1; xcrun simctl bootstatus "$IPAD" -b > /dev/null 2>&1
      xcrun simctl ui "$IPAD" appearance light > /dev/null 2>&1
      xcrun simctl install "$IPAD" "$WAPP" > "$OUT/ipadwide-install.txt" 2>&1 && say "== iPad wide: installed"
      phase "$IPAD" ipadwide 4 1000 wide-main report-4
      # ダークモードでも 1枚（まわりは 黒・アプリは まん中）
      xcrun simctl ui "$IPAD" appearance dark > /dev/null 2>&1
      xcrun simctl launch "$IPAD" "$BID" > /dev/null 2>&1; sleep 8; shot "$IPAD" "ipadwide-dark" 1000
      xcrun simctl terminate "$IPAD" "$BID" > /dev/null 2>&1
      if [ -f "$OUT/ipadwide-report-4.json" ]; then
        say "   wide: $(python3 -c '
import json, sys
r = json.load(open(sys.argv[1])); b = r.get("basic") or {}; L = r.get("layout") or {}; k = r.get("banner") or {}
ok = b.get("w") == 390 and 0 < (b.get("h") or 0) <= 844 and L.get("framed") is True and L.get("webWidth") == 390 and (L.get("hostWidth") or 0) > 480 and str(L.get("cssTop", "")).strip() in ("0px", "") and not r.get("errors")
print("web %sx%s dpr %s framed %s host %s web@(%s,%s) %sx%s ksk %s errors %d -> %s" % (b.get("w"), b.get("h"), b.get("dpr"), L.get("framed"), L.get("hostWidth"), L.get("webX"), L.get("webY"), L.get("webWidth"), L.get("webHeight"), k.get("k"), len(r.get("errors") or []), "OK" if ok else "CHECK"))
' "$OUT/ipadwide-report-4.json" 2>&1)"
      else
        say "   wide: report-4 not found CHECK"
      fi
      applog "$IPAD" ipadwide
      xcrun simctl shutdown "$IPAD" > /dev/null 2>&1
    fi
  else
    say "== build wide: Package.swift の 書きかえが できなかった CHECK"
  fi
fi
# 8) 馬カードバトルの 部屋（第4.176版）：iPhone（部屋を 作る）と iPad（部屋に 入る）を 同時に 動かす
if [ -n "$IPHONE" ] && [ -n "$IPAD" ]; then
  ROOM=$(( 1000 + RANDOM % 9000 ))
  xcrun simctl boot "$IPHONE" > /dev/null 2>&1; xcrun simctl bootstatus "$IPHONE" -b > /dev/null 2>&1
  xcrun simctl boot "$IPAD" > /dev/null 2>&1; xcrun simctl bootstatus "$IPAD" -b > /dev/null 2>&1
  xcrun simctl ui "$IPHONE" appearance light > /dev/null 2>&1; xcrun simctl ui "$IPAD" appearance light > /dev/null 2>&1
  xcrun simctl install "$IPHONE" "$APP" > /dev/null 2>&1; xcrun simctl install "$IPAD" "$APP" > /dev/null 2>&1      # iPad は 6) で .pad を 足した ものが 入って いる → 出す 形に もどす
  roomprep() {
    local U="$1" DEV="$2" PH="$3" D
    D=$(xcrun simctl get_app_container "$U" "$BID" data 2> /dev/null); [ -z "$D" ] && return 1
    mkdir -p "$D/Documents"; rm -f "$D/Documents"/mark-* "$D/Documents"/report-* "$D/Documents"/ack-*
    { echo "window.__ST_PHASE = $PH; window.__ST_DEVICE = '$DEV'; window.__ST_ROOM = '$ROOM';"; cat "$ROOT/ci/selftest.js"; } > "$D/Documents/selftest.js"
    echo "$D"
  }
  DH=$(roomprep "$IPHONE" iphone 6); DG=$(roomprep "$IPAD" ipad 7)
  if [ -n "$DH" ] && [ -n "$DG" ]; then
    T0=$(date +%s)
    xcrun simctl launch "$IPHONE" "$BID" -tengelSelfTest >> "$OUT/room-launch.txt" 2>&1
    sleep 8
    xcrun simctl launch "$IPAD" "$BID" -tengelSelfTest >> "$OUT/room-launch.txt" 2>&1
    sleep 14; shot "$IPHONE" "room-iphone-wait" 700; shot "$IPAD" "room-ipad-wait" 1000      # つなぐ とちゅう（確認の 窓が 出て いれば ここに 写る）
    waitfile "$DH/Documents/report-6.json" 300 && cp "$DH/Documents/report-6.json" "$OUT/room-iphone-report-6.json"
    waitfile "$DG/Documents/report-7.json" 60 && cp "$DG/Documents/report-7.json" "$OUT/room-ipad-report-7.json"
    sleep 1; shot "$IPHONE" "room-iphone-end" 700; shot "$IPAD" "room-ipad-end" 1000
    say "== room (iPhone hosts $ROOM, iPad joins): $(( $(date +%s) - T0 ))s"
    say "   room: $(python3 -c '
import json, os, sys
def rd(p):
    try: return json.load(open(p))
    except Exception: return None
h, g = rd(sys.argv[1]), rd(sys.argv[2])
if h is None or g is None:
    print("report host %s guest %s -> CHECK" % ("yes" if h else "NO", "yes" if g else "NO")); sys.exit(0)
flip = {"win": "lose", "lose": "win", "draw": "draw"}
ok = (h.get("connected") is True and g.get("connected") is True and h.get("kind") == "host" and g.get("kind") == "guest" and h.get("res") in flip and flip[h["res"]] == g.get("res")
      and h.get("wins") == list(reversed(g.get("wins") or [])) and (h.get("discard") or 0) >= 10 and h.get("discard") == g.get("discard") and not h.get("errors") and not g.get("errors"))      # 第4.178版：5ターン ＝ 捨て札は 10まい 以上
print("host connected %s res %s wins %s discard %s evs %s / guest connected %s res %s wins %s evs %s errors %d -> %s" % (h.get("connected"), h.get("res"), h.get("wins"), h.get("discard"), h.get("evs"), g.get("connected"), g.get("res"), g.get("wins"), g.get("evs"),
      len(h.get("errors") or []) + len(g.get("errors") or []), "OK" if ok else "CHECK " + (h.get("text") or "")[:80] + " / " + (g.get("text") or "")[:80]))
' "$OUT/room-iphone-report-6.json" "$OUT/room-ipad-report-7.json" 2>&1)"
    for f in "$DH/Documents"/report-crash-*.json "$DG/Documents"/report-crash-*.json; do [ -f "$f" ] && cp "$f" "$OUT/room-$(basename "$f")" && say "   room: CRASH $(basename "$f")"; done
    applog "$IPHONE" room-iphone; applog "$IPAD" room-ipad
    xcrun simctl spawn "$IPHONE" log show --last 8m --style compact --predicate 'subsystem CONTAINS "MultipeerConnectivity" OR eventMessage CONTAINS[c] "MCNearby" OR eventMessage CONTAINS[c] "local network" OR eventMessage CONTAINS[c] "tengel-cb"' 2>/dev/null | tail -150 > "$OUT/room-iphone-mc-log.txt"
    xcrun simctl terminate "$IPHONE" "$BID" > /dev/null 2>&1; xcrun simctl terminate "$IPAD" "$BID" > /dev/null 2>&1
  else
    say "== room: app container not found CHECK"
  fi
  xcrun simctl shutdown "$IPHONE" > /dev/null 2>&1; xcrun simctl shutdown "$IPAD" > /dev/null 2>&1
fi
find "$HOME/Library/Logs/DiagnosticReports" -name "*.ips" -newer "$S" 2> /dev/null | while read -r f; do grep -q "テンゲル\|AppModule" "$f" && cp "$f" "$OUT/crash-$(basename "$f")"; done
say "== done"
exit 0
