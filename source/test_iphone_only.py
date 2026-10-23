# iPhone用のアプリ（21章）の確かめ：python3 test_iphone_only.py
#   ・ios/Tengel.swiftpm/Package.swift が iPhone だけ（supportedDeviceFamilies: [.phone]）・向きは縦だけ（.portrait）
#     Swift Playgrounds の「App の設定」を変えると Package.swift が作り直されて .pad や横向きがもどることがあるので、アップロードの前にも通す
#   ・アプリ（Swift）に、拡大（zoom）・キーチェーンのしるし（marker）・App内課金（iap）のお願いの受け口がある
#   ・build_ios.py が作る Package.swift も同じ
import os, re, subprocess, sys, tempfile
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label)
    if not c:
        fails.append(label)


def families(src):
    m = re.search(r'supportedDeviceFamilies:\s*\[([^\]]*)\]', src)
    return sorted(x.strip() for x in m.group(1).split(',') if x.strip()) if m else None


def orientations(src):
    m = re.search(r'supportedInterfaceOrientations:\s*\[([^\]]*)\]', src)
    return [x.strip() for x in m.group(1).split(',') if x.strip()] if m else None


nocom = lambda t: re.sub(r'//[^\n]*', '', t)   # メモ（コメント）は見ない
pk = nocom(open(os.path.join(W, 'ios', 'Tengel.swiftpm', 'Package.swift'), encoding='utf8').read())
check(families(pk) == ['.phone'], f'Package.swift：iPhone だけ（{families(pk)}）')
check(orientations(pk) == ['.portrait'], f'Package.swift：向きは縦だけ（{orientations(pk)}）')
check('.pad' not in pk and 'portraitUpsideDown' not in pk and 'landscape' not in pk.lower(), 'Package.swift：.pad・横向き・さかさまが残っていない')
wv = open(os.path.join(W, 'ios', 'Tengel.swiftpm', 'TengelWebView.swift'), encoding='utf8').read()
for name in ('zoom', 'marker', 'iap', 'notify'):
    check(f'case "{name}":' in wv, f'アプリの受け口：{name}')
# 第2弾：結果確認のお知らせ（ローカル通知）
nf = open(os.path.join(W, 'ios', 'Tengel.swiftpm', 'Notify.swift'), encoding='utf8').read()
check('UNUserNotificationCenter' in nf and 'UNTimeIntervalNotificationTrigger' in nf and 'notifyMax = 64' in nf and 'requestAuthorization' in nf and 'removePendingNotificationRequests' in nf, 'Notify.swift：ローカル通知（許可・64件まで・入れ直し）')
check('willPresent' in nf and 'didReceive' in nf and 'Notify.shared.onOpen' in wv, 'お知らせを押したらWebの画面に知らせる（開いているときも出す）')
ap = open(os.path.join(W, 'ios', 'Tengel.swiftpm', 'TengelApp.swift'), encoding='utf8').read()
check('UIApplicationDelegateAdaptor' in ap and 'Notify.shared.install()' in ap, '起動のときにお知らせの受け口を入れる（AppDelegate）')
check('setZoomScale(1' in wv and 'pinchGestureRecognizer' in wv, '拡大を1倍にもどす・2本指の拡大を止める')
check('__nativeEvent' in wv and 'Store.shared.start()' in wv, 'App内課金の新しい取引をWebの画面に知らせる')
mk = nocom(open(os.path.join(W, 'ios', 'Tengel.swiftpm', 'Markers.swift'), encoding='utf8').read())
check('kSecAttrSynchronizable' in mk and 'kSecClassGenericPassword' in mk and 'ThisDeviceOnly' not in mk, 'キーチェーンのしるしは iCloudキーチェーンで同期する形')
st = open(os.path.join(W, 'ios', 'Tengel.swiftpm', 'Store.swift'), encoding='utf8').read()
for pid in ('points500', 'points1000', 'points2000', 'points4000', 'sub2000', 'sub4400', 'sub9200'):
    check(f'"jp.tengel.app.{pid}"' in st, f'App内課金の商品ID：jp.tengel.app.{pid}')
check('Transaction.updates' in st and 'Transaction.unfinished' in st and 'AppStore.sync()' in st and '.finish()' in st, 'StoreKit 2：取引の更新・終わっていない取引・購入を復元・終わらせる')
# build_ios.py が作る Package.swift
out = tempfile.mkdtemp()
r = subprocess.run([sys.executable, 'build_ios.py', out], capture_output=True, text=True)
check(r.returncode == 0, 'build_ios.py が通る' + ('' if r.returncode == 0 else '：' + (r.stderr or r.stdout)[-300:]))
if r.returncode == 0:
    bp = nocom(open(os.path.join(out, 'Tengel.swiftpm', 'Package.swift'), encoding='utf8').read())
    check(families(bp) == ['.phone'] and orientations(bp) == ['.portrait'], '作ったアプリの Package.swift も iPhone だけ・縦だけ')
    res = sorted(os.listdir(os.path.join(out, 'Tengel.swiftpm', 'Resources')))
    html = open(os.path.join(out, 'Tengel.swiftpm', 'Resources', 'index.html'), encoding='utf8').read()
    check('TengelPoints' in html and 'TengelWallet' in html and 'id="gate"' in html and 'touch-action:manipulation' in html, 'アプリの画面に ポイント・アプリを開いた時の画面・拡大の決まりが入っている')
    check(all(os.path.exists(os.path.join(out, 'Tengel.swiftpm', f)) for f in ('Markers.swift', 'Store.swift', 'Notify.swift')), 'Markers.swift・Store.swift・Notify.swift が入っている')
    check('TengelReserve' in html and 'TengelCustomRate' in html and 'parseResult' in html and 'omakaseBtn' in html, 'アプリの画面に 買い目の予約・%・結果の画像の読み取り・テンゲルにお任せ が入っている（第2弾）')
    # 第3弾：的中ボタン（見本の CSS/HTML を束ねた __FX・fx.js・設定のカード）。絵と音は手元の ios/fx_assets/ から Resources/ へ（リポジトリには入れない）
    check('window.__FX=' in html and 'window.TengelFx' in html and "'tengel.fxhidden'" in html and 'setFx' in html and 'fz_nglow.webp' in html and 'sfx_fz.m4a' in html and '/_blob/' not in html, 'アプリの画面に 的中ボタン（__FX・fx.js・設定の「的中の演出」）が入っている・見本の絵の場所（/_blob/）が残っていない（第3弾）')
    sys.path.insert(0, os.path.join(W, 'kisekae')); from build_fx import ASSET_FILES
    have = [f for f in ASSET_FILES if f in res]
    check(len(have) in (0, len(ASSET_FILES)) and (not os.path.isdir(os.path.join(W, 'ios', 'fx_assets')) or len(have) == len(ASSET_FILES)), f'的中ボタンの絵と音：手元にあれば8こ全部 Resources/ に入る・なければ入れずに作れる（{len(have)}こ）')
    gi = open(os.path.join(W, '.gitignore'), encoding='utf8').read()
    check('ios/fx_assets/' in gi and subprocess.run(['git', 'check-ignore', '-q', 'source/ios/fx_assets/sfx_fz.m4a'], cwd=os.path.dirname(W)).returncode == 0, '絵と音のフォルダ（ios/fx_assets/）は git に入らない（source/.gitignore）')
ap2 = open(os.path.join(W, 'ios', 'Tengel.swiftpm', 'TengelApp.swift'), encoding='utf8').read(); af = open(os.path.join(W, 'ios', 'Tengel.swiftpm', 'AppFiles.swift'), encoding='utf8').read()
check('import AVFoundation' in ap2 and 'setCategory(.ambient' in ap2 and '.mixWithOthers' in ap2, '効果音：消音スイッチなら鳴らさない・ほかのアプリの音楽は止めない（AVAudioSession ambient）')
check('case "m4a": return "audio/mp4"' in af, 'アプリの中の音のファイル（m4a）を Web の画面に渡せる')
print('結果：', 'OK' if not fails else f'{len(fails)}件おかしい')
raise SystemExit(1 if fails else 0)
