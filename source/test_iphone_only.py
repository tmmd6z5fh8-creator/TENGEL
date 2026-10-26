# iPhone用のアプリ（21章）の確かめ：python3 test_iphone_only.py
#   ・ios/Tengel.swiftpm/Package.swift が iPhone だけ（supportedDeviceFamilies: [.phone]）・向きは縦だけ（.portrait）
#     Swift Playgrounds の「App の設定」を変えると Package.swift が作り直されて .pad や横向きがもどることがあるので、アップロードの前にも通す
#   ・アプリ（Swift）に、拡大（zoom）・キーチェーンのしるし（marker）・App内課金（iap）のお願いの受け口がある
#   ・build_ios.py が作る Package.swift も同じ
import os, re, shutil, subprocess, sys, tempfile
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
    check(len(have) in (0, len(ASSET_FILES)) and (not os.path.isdir(os.path.join(W, 'ios', 'fx_assets')) or len(have) == len(ASSET_FILES)), f'的中ボタンの絵と音：手元にあれば{len(ASSET_FILES)}こ全部 Resources/ に入る・なければ入れずに作れる（{len(have)}こ）')
    # 第5弾：特別な 演出（16.3）。見本の CSS と HTML を 束ねた __FX の reveal（pc・zp・gd・sgd・spg）・絵と 音と 動画の 名前・動画の <video>（fx.js）・Swift の Range（動画の 部分読み）
    from build_fx import FILMS, STILL, ART, SFX
    check(all(f"'{k}'" in html or f'"{k}"' in html for k in ('pc', 'zp', 'gd', 'sgd', 'spg', 'sd')) and all(v in html for v in list(FILMS.values()) + list(STILL.values()) + [SFX[k] for k in ('pc', 'zp', 'gd', 'sgd', 'spg_up', 'spg', 'sd', 'sdp')]) and 'pm_face_F.webp' in html and 'gd_dome.webp' in html and 'sd_last.webp' in html and 'sd_t_hit.webp' not in html and 'sd_horse.webp' not in html and 'sd_film.mp4' in html
          and '.fxs .ov.fz.sgd' in html and '.fxs .ov.fz.pm' in html and '.fxs .ov.fz.zp' in html and '.fxs .ov.fz.gd' in html and '.fxs .ov.fz.sd' in html and "data-film" in html and 'WAIT_MAX' in html and '.ph ' not in html.split('window.__FX=')[1][:400000],
          'アプリの画面に 特別な 演出（プレミアム・超プレミアム・神様・超神様・超プレミアム神様・紫電の CSS と HTML・絵と 音と 動画の 名前・動画の しくみ）が入っている（第5弾・第4.66版・第4.71版：紫電は 動画と さいごの 1まい・プチュンの 音）')
    check(len(ART['pm']) == 38 and len(ART['gd']) == 24 and ART['sd'] == ['sd_last.webp'] and len(FILMS) == 3 and len(ASSET_FILES) == 2 + 14 + 38 + 24 + 2 + 3, f'絵と音と動画の 数：ネオン 2・音 14（第4.71版：紫電の プチュン）・プレミアム 38・神様 24・さいごの 1まい 2（超神様・紫電）・動画 3（{len(ASSET_FILES)}）')
    fxd = os.path.join(W, 'ios', 'fx_assets')
    if os.path.isdir(fxd) and all(os.path.exists(os.path.join(fxd, f)) for f in ASSET_FILES):
        sz = sum(os.path.getsize(os.path.join(fxd, f)) for f in ASSET_FILES)
        films_sz = sum(os.path.getsize(os.path.join(fxd, f)) for f in FILMS.values())
        check(22.8e6 < films_sz < 24.8e6 and 29.5e6 < sz < 31.5e6, f'絵と音と動画の 大きさ：動画 3本 約23.8MB（第4.72版：紫電の 動画 約7.5MB・10.5秒）・ぜんぶで 約30.5MB（{films_sz / 1e6:.1f}MB・{sz / 1e6:.1f}MB）')
    af = open(os.path.join(W, 'ios', 'Tengel.swiftpm', 'AppFiles.swift'), encoding='utf8').read()
    check('byteRange' in af and 'Content-Range' in af and 'Accept-Ranges' in af and '"mp4": return "video/mp4"' in af and 'statusCode: status' in af, 'AppFiles.swift：動画の 部分読み（Range → 206・Content-Range）と mp4 の MIME')
    # 第4.59版：iPad で 画面いっぱいに 動かす とき（時計の 帯の 高さが 0 と 伝わる）の あき（Swift と Web の 両方）・ふつうの 作り方には テスト版の 印が ない
    wv = open(os.path.join(out, 'Tengel.swiftpm', 'TengelWebView.swift'), encoding='utf8').read()
    check('userInterfaceIdiom == .pad' in wv and 'safeAreaInsets.bottom > 0 ? 24 : 20' in wv and '--top-inset2' in html and 'var(--top-inset2,0px)' in html, 'iPad で 画面いっぱいの とき 上の帯を 時計の 帯の ぶん あける（Swift の 24/20pt・Web の 24px）')
    check('window.__TEST=true;' not in html and 'テスト版の道具' in html and 'gift-test' in html, 'ふつうの 作り方：テスト版の 印（__TEST=true）は 入って いない（道具の コードは あるが 動かない）')
    gi = open(os.path.join(W, '.gitignore'), encoding='utf8').read()
    check('ios/fx_assets/' in gi and subprocess.run(['git', 'check-ignore', '-q', 'source/ios/fx_assets/sfx_fz.m4a'], cwd=os.path.dirname(W)).returncode == 0, '絵と音のフォルダ（ios/fx_assets/）は git に入らない（source/.gitignore）')
    # 第4弾：着せ替え（30テーマの変数と @font-face を束ねた __KS・kisekae.js・設定のカード・テーマごとの ks_<id>.json・しぼった字・見本の絵は手元の ios/kisekae_blobs/ から）
    import json as _json, re as _re
    ks_json = [f for f in res if _re.fullmatch(r'ks_[a-z]+\.json', f)]
    check('window.__KS=' in html and 'window.TengelKisekae' in html and "'tengel.kisekae'" in html and 'setKisekae' in html and 'html[data-ks=\\"sakura\\"]' in html and "@font-face{font-family:'Kaisei Decol'" in html and 'fonts/KaiseiDecol-700.woff2' in html,
          'アプリの画面に 着せ替え（__KS・kisekae.js・設定の「着せ替え」・テーマの変数・テーマの字の @font-face）が入っている（第4弾）')
    check(len(ks_json) == 30 and all(f in res for f in ('ks_banner_ranch.svg', 'ks_banner_cute.svg', 'ks_banner_kids.svg', 'ks_banner_gold.svg')), f'テーマごとの ks_<id>.json が 30こ と 定番4の止まった絵（{len(ks_json)}）')
    sk = _json.load(open(os.path.join(out, 'Tengel.swiftpm', 'Resources', 'ks_sakura.json'), encoding='utf8'))
    check(sk['bnr'] and '<div class="bnrw">' in sk['bnr']['html'] and 'ks_39558c280310609ad0a65971ed217991.webp' in sk['bnr']['html'] and '#ksBnr .bnrw' in sk['bnr']['css'] and '@keyframes kb' in sk['bnr']['css'] and '/_blob/' not in _json.dumps(sk)
          and sk['push']['pc'] == 'sk' and '<svg' in sk['push']['svg'] and 'class="clips sk"' in sk['push']['burst'] and '.fxs .push.sk' in sk['push']['css'] and '.fxs .rb.t-sakura{' in sk['board']['css'] and '<svg class="orn"' in sk['board']['orn'],
          'ks_sakura.json：上の絵（#ksBnr の中だけ・@keyframes に kb）・桜の PUSH（面・はじける花びら・.fxs の中だけ）・ボードの変数と飾り・見本の絵の場所（/_blob/）が残っていない')
    for f in ks_json:
        txt = open(os.path.join(out, 'Tengel.swiftpm', 'Resources', f), encoding='utf8').read()
        for w in ('大井', 'JRA', 'まさちゃん', '第13', '改訂'):
            if w in txt: fails.append(f'{f} に {w}')
    fonts_ks = _json.load(open(os.path.join(W, 'ios', 'fonts', 'ks', 'fonts.json'), encoding='utf8'))
    check(len(fonts_ks['fonts']) >= 40 and all(r['file'] in res for r in fonts_ks['fonts']) and all(os.path.exists(os.path.join(W, 'ios', 'fonts', 'ks', 'OFL-' + r['family'].replace(' ', '') + '.txt')) for r in fonts_ks['fonts']) and fonts_ks['total'] < 4_000_000,
          f'テーマの字（しぼった WOFF2 {len(fonts_ks["fonts"])}こ・{fonts_ks["total"] / 1e6:.1f}MB）が Resources/ に入る・OFL の全文がある')
    # しぼった字に 画面の言葉が ぜんぶ入っている（UI の文字がふえたら kisekae/build_fonts.py を もう一度）
    sys.path.insert(0, os.path.join(W, 'kisekae')); import build_fonts as _bf
    have_b = set(open(os.path.join(W, 'ios', 'fonts', 'ks', 'chars_body.txt'), encoding='utf8').read())
    need_b = set(_bf.body_chars()) - have_b
    check(not need_b, f'しぼった字に 画面の言葉が ぜんぶ入っている（足りない字 {len(need_b)}：{"".join(sorted(need_b))[:30]}）→ 足りなければ python3 kisekae/build_fonts.py')
    ks_imgs = [f for f in res if _re.fullmatch(r'ks_[0-9a-f]{32}\.(webp|svg)', f)]
    check(len(ks_imgs) in (0, 100) and (not os.path.isdir(os.path.join(W, 'ios', 'kisekae_blobs')) or len(ks_imgs) == 100), f'着せ替えの絵：手元にあれば100こ全部 Resources/ に入る・なければ入れずに作れる（{len(ks_imgs)}こ。第4.63版：勝負服の tile2・ネオンの dust と つぶなしの 止まった絵が 足された。第4.64版：ネオンの 止まった絵は 背景だけの 絵に 入れかわり・桜の 止まった絵と シートも 入れかわり＝数は 同じ）')
    check('ios/kisekae_blobs/' in gi and subprocess.run(['git', 'check-ignore', '-q', 'source/ios/kisekae_blobs/x.webp'], cwd=os.path.dirname(W)).returncode == 0, '着せ替えの絵のフォルダ（ios/kisekae_blobs/）は git に入らない（source/.gitignore）')
    # 第4.62版：アプリの 言葉は 日本語（Package.swift の defaultLocalization: "ja" と Resources/ja.lproj/Localizable.strings）→ 写真を 選ぶ 窓など iOS の 部品が 日本語に
    check('defaultLocalization: "ja",' in pk and os.path.exists(os.path.join(out, 'Tengel.swiftpm', 'Resources', 'ja.lproj', 'Localizable.strings')), 'アプリの 言葉は 日本語（defaultLocalization: "ja"・ja.lproj）：写真を 選ぶ 窓も 日本語に')
ap2 = open(os.path.join(W, 'ios', 'Tengel.swiftpm', 'TengelApp.swift'), encoding='utf8').read(); af = open(os.path.join(W, 'ios', 'Tengel.swiftpm', 'AppFiles.swift'), encoding='utf8').read()
check('import AVFoundation' in ap2 and 'setCategory(.ambient' in ap2 and '.mixWithOthers' in ap2, '効果音：消音スイッチなら鳴らさない・ほかのアプリの音楽は止めない（AVAudioSession ambient）')
check('case "m4a": return "audio/mp4"' in af, 'アプリの中の音のファイル（m4a）を Web の画面に渡せる')
# 第4.59版：テスト版（TENGEL_TEST=1）：TengelTest.swiftpm・名前「テンゲル テスト」・index.html に __TEST・絵と 音と 動画は ふつうと 同じ 入れ方（ここでは なしで 作る）
out2 = tempfile.mkdtemp()
r2 = subprocess.run([sys.executable, 'build_ios.py', out2], capture_output=True, text=True, env=dict(os.environ, TENGEL_TEST='1', FX_ASSETS='/nonexistent', KISEKAE_ASSETS='/nonexistent'))
check(r2.returncode == 0 and os.path.isdir(os.path.join(out2, 'TengelTest.swiftpm')) and os.path.exists(os.path.join(out2, 'TengelTest.swiftpm.zip')), 'テスト版：TENGEL_TEST=1 python3 build_ios.py → TengelTest.swiftpm（.zip）' + ('' if r2.returncode == 0 else '：' + (r2.stderr or r2.stdout)[-300:]))
if r2.returncode == 0:
    ps2 = open(os.path.join(out2, 'TengelTest.swiftpm', 'Package.swift'), encoding='utf8').read()
    h2 = open(os.path.join(out2, 'TengelTest.swiftpm', 'Resources', 'index.html'), encoding='utf8').read()
    check('name: "テンゲル テスト",' in ps2 and 'bundleIdentifier: "jp.tengel.app"' in ps2 and 'supportedDeviceFamilies: [\n                .phone\n            ]' in ps2, 'テスト版：アプリの 名前は「テンゲル テスト」・bundle id と iPhone用は ふつうと 同じ')
    check('window.__TEST=true;' in h2 and 'テスト版の道具' in h2, 'テスト版：画面に __TEST（はじめから 10,000P・設定の いちばん上に テスト版の道具）')
shutil.rmtree(out2, ignore_errors=True)
print('結果：', 'OK' if not fails else f'{len(fails)}件おかしい')
raise SystemExit(1 if fails else 0)
