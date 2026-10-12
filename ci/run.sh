#!/bin/bash
# テンゲル iOSアプリの確認（GitHubのMacで動かす。.github/workflows/ios.yml から呼ぶ）
#  1) Swift 5（いまの Package.swift）でシミュレーター用に作る
#  2) Swift 6 の厳しいチェックでも作れるか（Swift Playgrounds が Package.swift を作り直したとき用）
#  3) 実機（iPhone・iPad）用に Release で作れるか（署名なし）
#  4) iPhoneのシミュレーター：1回目（記録を保存・自動バックアップ・画面のスクショ）→ 2回目（開き直しても記録が残る・保存場所を消す）→ 3回目（「戻す？」→ 戻す）
#  5) iPadのシミュレーター：1回目だけ
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
say "   web files: $(grep -cE '\.(html|webp|jpg)$' "$OUT/app-files.txt")  index.html at: $(grep 'index.html' "$OUT/app-files.txt" | tr '\n' ' ')"

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
  { echo "window.__ST_PHASE = $PH; window.__ST_DEVICE = '$DEV';"; cat "$ROOT/ci/selftest.js"; } > "$D/Documents/selftest.js"
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

P1="main settings backup cm rec report-1 manual manual-item report-manual back report-back"
# 4) iPhone
if [ -n "$IPHONE" ]; then
  xcrun simctl boot "$IPHONE" > /dev/null 2>&1; xcrun simctl bootstatus "$IPHONE" -b > /dev/null 2>&1
  xcrun simctl ui "$IPHONE" appearance light > /dev/null 2>&1
  xcrun simctl install "$IPHONE" "$APP" > "$OUT/iphone-install.txt" 2>&1 && say "== iPhone: installed"
  phase "$IPHONE" iphone 1 700 $P1
  phase "$IPHONE" iphone 2 700 report-2
  phase "$IPHONE" iphone 3 700 offer restored report-3 report-link
  sleep 3; shot "$IPHONE" "iphone-3-link-safari" 700
  # ダークモードで1枚
  xcrun simctl ui "$IPHONE" appearance dark > /dev/null 2>&1
  xcrun simctl launch "$IPHONE" "$BID" > /dev/null 2>&1; sleep 8; shot "$IPHONE" "iphone-dark" 700
  xcrun simctl terminate "$IPHONE" "$BID" > /dev/null 2>&1
  applog "$IPHONE" iphone
  xcrun simctl shutdown "$IPHONE" > /dev/null 2>&1
fi
# 5) iPad
if [ -n "$IPAD" ]; then
  xcrun simctl boot "$IPAD" > /dev/null 2>&1; xcrun simctl bootstatus "$IPAD" -b > /dev/null 2>&1
  xcrun simctl ui "$IPAD" appearance light > /dev/null 2>&1
  xcrun simctl install "$IPAD" "$APP" > "$OUT/ipad-install.txt" 2>&1 && say "== iPad: installed"
  phase "$IPAD" ipad 1 1000 $P1
  applog "$IPAD" ipad
  xcrun simctl shutdown "$IPAD" > /dev/null 2>&1
fi
find "$HOME/Library/Logs/DiagnosticReports" -name "*.ips" -newer "$S" 2> /dev/null | while read -r f; do grep -q "テンゲル\|AppModule" "$f" && cp "$f" "$OUT/crash-$(basename "$f")"; done
say "== done"
exit 0
