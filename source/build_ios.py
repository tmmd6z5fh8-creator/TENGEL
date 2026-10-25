# テンゲル iPhone・iPadアプリ（Swift Playgrounds の App）を組み立てる
#   python3 build_ios.py <出力フォルダ>
#   → <出力フォルダ>/Tengel.swiftpm（Swift Playgrounds・Xcodeで開ける）と Tengel.swiftpm.zip（iPadに送る用）
# 画面はWeb版と同じもの（build_pwa.py を TARGET=app で作る index.html・説明書・CMの表紙・フォント）を Resources/ に入れる。
# TARGET=app：フォントはアプリの中のもの（ios/fonts・Google に通信しない）・説明書はApp Store版（「iPhoneに入れる」などなし）・お客さん向けの言い方
# アプリの中では tengel://localhost/ で開くので、pwa_shim.js がアプリ版（window.__NATIVE）として動く。
# Swiftの枠は ios/Tengel.swiftpm（Package.swift・TengelApp.swift・TengelWebView.swift・AppFiles.swift・Assets.xcassets）。
# アプリの版（App Storeの版）は ios/Tengel.swiftpm/Package.swift の displayVersion・bundleVersion。
# 新しい版をApp Storeに出すとき（アップデート）は、版の番号を上げて作る：
#   IOS_VERSION=1.1 IOS_BUILD=2 python3 build_ios.py <出力フォルダ>
#   （IOS_VERSION＝お客さんに見える版「1.1」・IOS_BUILD＝出すたびに1ずつ上げる番号。どちらも前より大きく）
import os, re, shutil, subprocess, sys, tempfile, zipfile
from PIL import Image
W = os.path.dirname(os.path.abspath(__file__))
out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(W, 'ios_out'))
IOS_VERSION, IOS_BUILD = os.environ.get('IOS_VERSION', ''), os.environ.get('IOS_BUILD', '')
if IOS_VERSION and not re.fullmatch(r'\d+(\.\d+){0,2}', IOS_VERSION): sys.exit('IOS_VERSION は 1.1 のような数字だよ')
if IOS_BUILD and not re.fullmatch(r'\d+', IOS_BUILD): sys.exit('IOS_BUILD は 2 のような数字だよ')
if os.path.exists(os.path.join(out, '.git')): sys.exit('出力先にgitの作業フォルダは指定できないよ')
os.makedirs(out, exist_ok=True)
tmp = tempfile.mkdtemp()
web = os.path.join(tmp, 'web')
subprocess.run(['node', 'build.js'], cwd=W, check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', web], cwd=W, check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, TARGET='app'))

TEST = os.environ.get('TENGEL_TEST') == '1'   # テスト版（第4.59版）：TENGEL_TEST=1 python3 build_ios.py <出力>（はじめから 10,000P・設定に「テスト版の道具」・名前は「テンゲル テスト」・TengelTest.swiftpm）。App Store には 出さない
pkg = os.path.join(out, 'TengelTest.swiftpm' if TEST else 'Tengel.swiftpm')
shutil.rmtree(pkg, ignore_errors=True)
shutil.copytree(os.path.join(W, 'ios', 'Tengel.swiftpm'), pkg, ignore=shutil.ignore_patterns('.DS_Store', 'Resources', 'AppIcon.png', '.build', '.swiftpm'))
# 版の番号（アップデートのとき）
pk = os.path.join(pkg, 'Package.swift'); ps = open(pk, encoding='utf8').read()
cur_v = re.search(r'displayVersion: "([^"]+)"', ps).group(1); cur_b = re.search(r'bundleVersion: "([^"]+)"', ps).group(1)
if IOS_VERSION:
    ps = ps.replace(f'displayVersion: "{cur_v}"', f'displayVersion: "{IOS_VERSION}"')
if IOS_BUILD:
    ps = ps.replace(f'bundleVersion: "{cur_b}"', f'bundleVersion: "{IOS_BUILD}"')
if TEST:
    assert ps.count('name: "テンゲル",') == 2, 'Package.swift の 名前の 形が かわった'
    ps = ps.replace('        .iOSApplication(\n            name: "テンゲル",', '        .iOSApplication(\n            name: "テンゲル テスト",')
    assert 'テンゲル テスト' in ps
open(pk, 'w', encoding='utf8').write(ps)
VER = (IOS_VERSION or cur_v, IOS_BUILD or cur_b)

# 画面のファイル：Resources/ に名前だけで並べる（Swift Playgrounds は Resources の中のフォルダを平らにするので、名前がかぶらないようにする）
files = {'index.html': 'index.html', 'manual.html': 'manual.html'}
for f in sorted(os.listdir(os.path.join(web, 'manual'))):
    files[f] = 'manual/' + f
for f in sorted(os.listdir(os.path.join(web, 'fonts'))):
    files[f] = 'fonts/' + f   # フォント（SIL OFL 1.1・ファイルはそのまま。ライセンスは「このアプリについて」）
if os.path.exists(os.path.join(web, 'cm', 'poster.jpg')):
    files['poster.jpg'] = 'cm/poster.jpg'   # CMの表紙（動画は大きいので入れない。見るときに公開中のWeb版から読む）
for f in sorted(os.listdir(web)):
    if f.startswith('ks_') and (f.endswith('.json') or f.endswith('.svg')):
        files[f] = f   # 着せ替え（第4弾）：テーマごとの壁紙・PUSH・ボード（ks_<id>.json）と 定番4の止まった絵
names = [n.lower() for n in files]
assert len(names) == len(set(names)), '同じ名前のファイルがあるよ'
assert not any(n.endswith('.png') for n in names), 'PNGは入れない（Xcodeが変換してしまうことがある）'
res = os.path.join(pkg, 'Resources'); os.makedirs(res)
for name, src in files.items():
    shutil.copy(os.path.join(web, src), os.path.join(res, name))
# 日本語の 言葉の ファイル（第4.62版）：Package.swift の defaultLocalization: "ja" と いっしょに、アプリが「日本語に 対応している」と iOS に 伝える
# → 写真を 選ぶ 窓（フォトライブラリ・写真を撮る・ファイルを選択）など iOS の 部品が 日本語に なる（まさちゃん「画像読み込みの案内、日本語にして！」）。中身は 使わない
os.makedirs(os.path.join(res, 'ja.lproj'))
open(os.path.join(res, 'ja.lproj', 'Localizable.strings'), 'w', encoding='utf8').write('/* テンゲル：日本語 */\n"tengel" = "テンゲル";\n')
# 的中ボタンの絵と音（第3弾）：手元で作ったもの（kisekae/build_fx_assets.py → ios/fx_assets/ か FX_ASSETS=<フォルダ>）を入れる。
# リポジトリには入れない（1章の11）ので、ないときは入れずに作る（CIはこの形。アプリは音なし・ネオンの線画なしで動く）
sys.path.insert(0, os.path.join(W, 'kisekae'))
from build_fx import ASSET_FILES
fx_dir = os.environ.get('FX_ASSETS') or os.path.join(W, 'ios', 'fx_assets')
fx_have = [f for f in ASSET_FILES if os.path.exists(os.path.join(fx_dir, f))]
for f in fx_have:
    assert f.lower() not in names, f
    shutil.copy(os.path.join(fx_dir, f), os.path.join(res, f)); files[f] = f
if len(fx_have) != len(ASSET_FILES):
    print('※ 的中ボタンの絵と音が', len(ASSET_FILES) - len(fx_have), 'こ ない（', fx_dir, '）。python3 kisekae/build_fx_assets.py で作れるよ（CIではなしのまま）')
# 着せ替えの絵（第4弾・16.1）：キャンバスから集めた見本の絵（ios/kisekae_blobs/<id>.webp か KISEKAE_ASSETS=<フォルダ>）を ks_<id>.<形> の名前で入れる。
# リポジトリには入れない（1章の11）ので、ないときは入れずに作る（CIはこの形。アプリは上の絵なし・いつものボードの飾りで動く）
import build_kisekae as _ks
ks_dir = _ks.BLOB_DIR
import re as _re
ks_ids = set()
for f in list(files):
    if f.startswith('ks_') and f.endswith('.json'):
        ks_ids |= set(_re.findall(r'ks_([0-9a-f]{32})\.', open(os.path.join(web, f), encoding='utf8').read()))
ks_ids |= set(t['thumb'][3:-5] for t in _ks.theme_list() if _re.fullmatch(r'ks_[0-9a-f]{32}\.webp', t['thumb']))
ks_have = 0
for bid in sorted(ks_ids):
    name = _ks.asset_name(bid)
    src_f = os.path.join(ks_dir, name[3:])
    if os.path.exists(src_f):
        assert name.lower() not in names, name
        shutil.copy(src_f, os.path.join(res, name)); files[name] = name; ks_have += 1
if ks_have != len(ks_ids):
    print('※ 着せ替えの絵が', len(ks_ids) - ks_have, 'こ ない（', ks_dir, '）。キャンバスから集める（アップデート指示書 16.1 の 絵の入れ方）。CIではなしのまま')

# アイコン（1024×1024・透明なし）
icon = Image.open(os.path.join(W, 'icons', 'icon_master_en.png'))
assert icon.size == (1024, 1024), icon.size
icon.convert('RGB').save(os.path.join(pkg, 'Assets.xcassets', 'AppIcon.appiconset', 'AppIcon.png'), optimize=True)

# iPadに送る用のzip（フォルダごと。Macの「._」ファイルなどは入れない）
zpath = os.path.join(out, ('TengelTest' if TEST else 'Tengel') + '.swiftpm.zip')
if os.path.exists(zpath): os.remove(zpath)
with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
    for root, dirs, fs in os.walk(pkg):
        dirs.sort()
        for f in sorted(fs):
            p = os.path.join(root, f)
            z.write(p, os.path.relpath(p, out))
shutil.rmtree(tmp, ignore_errors=True)
size = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(pkg) for f in fs)
print('built', pkg, f'{size / 1e6:.1f}MB', 'files', len(files), 'zip', f'{os.path.getsize(zpath) / 1e6:.1f}MB', 'version', VER[0], 'build', VER[1])
