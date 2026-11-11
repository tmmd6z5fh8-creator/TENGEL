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

TEST = os.environ.get('TENGEL_TEST') == '1'   # テスト版（第4.59版）：TENGEL_TEST=1 python3 build_ios.py <出力>（はじめから 10,000P・設定に「テスト版の道具」・名前は「テンゲル テスト」・TengelTest.swiftpm）。App Store には 出さない（第4.122版から ID は jp.tengel.app.test＝TestFlight で iPhone に 入れる）
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
TEST_BUILD = ''
if TEST:
    assert ps.count('name: "テンゲル",') == 2, 'Package.swift の 名前の 形が かわった'
    ps = ps.replace('        .iOSApplication(\n            name: "テンゲル",', '        .iOSApplication(\n            name: "テンゲル テスト",')
    assert 'テンゲル テスト' in ps
    # 第4.122版（まさちゃん 2026/11/04「アプリのテスト版でiPhoneて動かせないの？」）：テスト版は 本番と 別の アプリ（ID jp.tengel.app.test）。
    #   iPad の Swift Playgrounds から App Store Connect に あげて、TestFlight（内部テスト）で iPhone に 入れる。本番の「テンゲル」と 並べて 入れられる・
    #   キーチェーンの しるし（初回の 1,500P）も 本番と 分かれる（しるしは アプリの ID ごと）。前の 版までは 本番と 同じ ID（入れると 入れかわった）
    assert ps.count('bundleIdentifier: "jp.tengel.app",') == 1, 'Package.swift の ID の 形が かわった'
    ps = ps.replace('bundleIdentifier: "jp.tengel.app",', 'bundleIdentifier: "jp.tengel.app.test",')
    # ビルド番号：あげる たびに 前より 大きく（App Store Connect は 同じ 番号を 2回 受けつけない）。APP_VER 2026.11.04-3 → 20261104.3（IOS_BUILD が あれば それ）
    if not IOS_BUILD:
        m = re.fullmatch(r'(\d{4})\.(\d{2})\.(\d{2})(?:-(\d+))?', os.environ.get('APP_VER', ''))
        TEST_BUILD = f'{m.group(1)}{m.group(2)}{m.group(3)}.{int(m.group(4) or 1)}' if m else __import__('time').strftime('%Y%m%d.%H%M')
        ps = ps.replace(f'bundleVersion: "{IOS_BUILD or cur_b}"', f'bundleVersion: "{TEST_BUILD}"')
        assert f'bundleVersion: "{TEST_BUILD}"' in ps
open(pk, 'w', encoding='utf8').write(ps)
VER = (IOS_VERSION or cur_v, IOS_BUILD or TEST_BUILD or cur_b)

# 画面のファイル：Resources/ に名前だけで並べる（Swift Playgrounds は Resources の中のフォルダを平らにするので、名前がかぶらないようにする）
files = {'index.html': 'index.html', 'manual.html': 'manual.html'}
for f in sorted(os.listdir(os.path.join(web, 'manual'))):
    files[f] = 'manual/' + f
for f in sorted(os.listdir(os.path.join(web, 'fonts'))):
    files[f] = 'fonts/' + f   # フォント（SIL OFL 1.1・ファイルはそのまま。ライセンスは「このアプリについて」）
if os.path.exists(os.path.join(web, 'mother_template.xlsx')):
    files['mother_template.xlsx'] = 'mother_template.xlsx'   # 第4.123版：マザーデータの 入力用 Excel の ひな形（共有シートで 渡す）
if os.path.exists(os.path.join(web, 'tc_bundle.js')):
    files['tc_bundle.js'] = 'tc_bundle.js'   # トレーニングセンターの 本体（第4.130版：丸い ボタン（第4.138版から 右上）を 押した ときに 読む）
if os.path.exists(os.path.join(web, 'fig_bundle.js')):
    files['fig_bundle.js'] = 'fig_bundle.js'   # 思い出フィギュアの 本体（第4.134版：記録タブの「フィギュアブース」「フィギュアを作る」を 押した ときに 読む）
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
# 第4.146版：絵・動画の フォルダは assets_dir.adir()＝軽い 版（ios/lite/<名前>：kisekae/lite_assets.py が 作る。動画 CRF 24・絵 WebP quality 75）が あれば そちら・なければ もと（ios/<名前>）。
#   軽い 版が 古い（もとを 作り直した）ときは ここで 止まる。LITE=0 で もとの まま 入れる。FX_ASSETS など を 決めた とき（CI）は その フォルダ
import assets_dir as _ad
fx_dir = os.environ.get('FX_ASSETS') or _ad.adir('fx_assets')
fx_have = [f for f in ASSET_FILES if os.path.exists(os.path.join(fx_dir, f))]
for f in fx_have:
    assert f.lower() not in names, f
    shutil.copy(os.path.join(fx_dir, f), os.path.join(res, f)); files[f] = f
if len(fx_have) != len(ASSET_FILES):
    print('※ 的中ボタンの絵と音が', len(ASSET_FILES) - len(fx_have), 'こ ない（', fx_dir, '）。python3 kisekae/build_fx_assets.py で作れるよ（CIではなしのまま）')
# 結果ボードカスタムの 絵の ボード（第4.121版：まさちゃんの 絵 14こ・kisekae/bcp/bcp_app.py の files()）：ios/bcp_assets/ か BCP_ASSETS=<フォルダ>。
# 第4.145版：キャラが 動く 絵（48段）の 止まった 版（bcp_<名前>.webp・_fg.webp）は files() に 入らない（アプリは 部品を 重ねて 同じ 絵を 出す）。絵の フォルダには 残す（部品を 作り直す ときの もと）
# リポジトリには入れない（まさちゃんの 絵）ので、ないときは入れずに作る（CIはこの形。アプリは その ボードを いつもの ボードで 出す）
sys.path.insert(0, os.path.join(W, 'kisekae', 'bcp'))
import bcp_app as _bcp
bcp_dir = os.environ.get('BCP_ASSETS') or _ad.adir('bcp_assets')
bcp_all = _bcp.files()
bcp_have = [f for f in bcp_all if os.path.exists(os.path.join(bcp_dir, f))]
for f in bcp_have:
    assert f.lower() not in names and f not in files, f
    shutil.copy(os.path.join(bcp_dir, f), os.path.join(res, f)); files[f] = f
if len(bcp_have) != len(bcp_all):
    print('※ 結果ボードカスタムの 絵が', len(bcp_all) - len(bcp_have), 'こ ない（', bcp_dir, '）。kisekae/bcp の README の 作り方で 作れるよ（CIではなしのまま）')
# トレーニングセンターの 絵・形・音（第4.130版：まさちゃんの フィールド・馬・バケツの 3D など と それから 作った もの）：ios/tc_assets/ か TC_ASSETS=<フォルダ>。
# kisekae/tc/collect_assets.py で 集める。リポジトリには 入れない ので、ない ときは 入れずに 作る（CI は この 形。右上の ボタンを 押すと「読みこめなかった」に なる）
tc_dir = os.environ.get('TC_ASSETS') or _ad.adir('tc_assets')
_tc_ls = os.listdir(tc_dir) if os.path.isdir(tc_dir) else []; _tc_old = _ad.superseded('tc_assets', _tc_ls)      # 第4.156版：使わなく なった 音（横に なる 動きの 3つ）は 入れない
tc_have = sorted(f for f in _tc_ls if f not in _tc_old and f.rsplit('.', 1)[-1].lower() in ('webp', 'json', 'bin', 'm4a'))
for f in tc_have:
    assert f.lower() not in names and f not in files, f
    shutil.copy(os.path.join(tc_dir, f), os.path.join(res, f)); files[f] = f
if not tc_have:
    print('※ トレーニングセンターの 絵と 音が ない（', tc_dir, '）。kisekae/tc/collect_assets.py で 集めるよ（CIではなしのまま）')
# 思い出フィギュアの 形と 絵（第4.134版：まさちゃんの フィギュア 8体・3D の 棚 と それから 作った もの）：ios/fig_assets/ か FIG_ASSETS=<フォルダ>。
# kisekae/fig/collect_assets.py で 集める。リポジトリには 入れない ので、ない ときは 入れずに 作る（CI は この 形。ブースを 開くと「読みこめなかった」に なる）
fig_dir = os.environ.get('FIG_ASSETS') or _ad.adir('fig_assets')
# 第4.145版：fg_meta.json（集めた ときの メモ・アプリは 読まない）は 入れない
# 第4.153版：棚を 貼り直した 形（fg_shelf2.*）が ある ときは、前の 棚（fg_shelf.*）を 入れない（もとの フォルダを そのまま 使う ときも）
_fig_ls = os.listdir(fig_dir) if os.path.isdir(fig_dir) else []; _fig_old = _ad.superseded('fig_assets', _fig_ls)
fig_have = sorted(f for f in _fig_ls if f.startswith('fg') and f != 'fg_meta.json' and f not in _fig_old and f.rsplit('.', 1)[-1].lower() in ('webp', 'json', 'bin'))
for f in fig_have:
    assert f.lower() not in names and f not in files, f
    shutil.copy(os.path.join(fig_dir, f), os.path.join(res, f)); files[f] = f
if not fig_have:
    print('※ 思い出フィギュアの 形と 絵が ない（', fig_dir, '）。kisekae/fig/collect_assets.py で 集めるよ（CIではなしのまま）')
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
# PUSHボタンの 絵（第4.148版：まさちゃんの 絵 31まい＝テーマ 1つに 1まい・いつもの も）：ios/push_assets/（PUSH_ASSETS=<フォルダ>）の pb_<id>.webp（kisekae/push_art.py が 作る）。
# リポジトリには 入れない ので、ない ときは 入れずに 作る（CI は この 形：今までの コードの PUSH の まま）。もとの 絵（src/*.png）と 台帳（pb.json）は 入れない
import push_art as _pa
pb_art = _ks.push_art()
for _tid, _e in sorted(pb_art.items()):
    assert _e['f'].lower() not in names and _e['f'] not in files and _e['f'].endswith('.webp'), _e['f']
    shutil.copy(os.path.join(_pa.ROOT, _e['f']), os.path.join(res, _e['f'])); files[_e['f']] = _e['f']
if not pb_art:
    print('※ PUSHボタンの 絵が ない（', _pa.ROOT, '）。python3 kisekae/push_art.py で 作るよ（CIではなしのまま＝今までの PUSH）')

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
assert _ad.INFO not in files and not os.path.exists(os.path.join(res, _ad.INFO)), '軽い 版の 台帳は アプリに 入れない'
_pk = [n for n, d in (('fx_assets', fx_dir), ('bcp_assets', bcp_dir), ('tc_assets', tc_dir), ('fig_assets', fig_dir)) if os.path.abspath(d) == os.path.abspath(_ad.lite(n))]
print('built', pkg, f'{size / 1e6:.1f}MB', 'files', len(files), 'zip', f'{os.path.getsize(zpath) / 1e6:.1f}MB', 'version', VER[0], 'build', VER[1], '軽い 版', '・'.join(_pk) if _pk else 'なし')
