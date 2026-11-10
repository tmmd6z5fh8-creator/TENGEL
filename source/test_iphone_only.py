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
for pid in ('points500', 'points1000', 'points2000', 'points4000', 'sub2000', 'sub4400', 'sub9200', 'boardcustom', 'wallpack1', 'bundle1'):   # 第4.114版：お得パック bundle1
    check(f'"jp.tengel.app.{pid}"' in st, f'App内課金の商品ID：jp.tengel.app.{pid}')
check('static let unlockIDs = ["jp.tengel.app.boardcustom", "jp.tengel.app.wallpack1", "jp.tengel.app.bundle1"]' in st and 'packIDs + subIDs + unlockIDs' in st and 'return "unlock"' in st and 'case "current": return ["ok": true, "list": await current()]' in st, '第4.91版：結果ボードカスタム・第4.92版：壁紙パック（非消耗型・買い切り）：商品の 一覧に 入る・取引の 種類は unlock・いま 有効な もの（current）を Webの 画面に 渡す')
check('Transaction.updates' in st and 'Transaction.unfinished' in st and 'AppStore.sync()' in st and '.finish()' in st, 'StoreKit 2：取引の更新・終わっていない取引・購入を復元・終わらせる')
# build_ios.py が作る Package.swift
out = tempfile.mkdtemp()
r = subprocess.run([sys.executable, 'build_ios.py', out], capture_output=True, text=True)
check(r.returncode == 0, 'build_ios.py が通る' + ('' if r.returncode == 0 else '：' + (r.stderr or r.stdout)[-300:]))
if r.returncode == 0:
    bp = nocom(open(os.path.join(out, 'Tengel.swiftpm', 'Package.swift'), encoding='utf8').read())
    check(families(bp) == ['.phone'] and orientations(bp) == ['.portrait'], '作ったアプリの Package.swift も iPhone だけ・縦だけ')
    check('bundleIdentifier: "jp.tengel.app",' in bp and 'jp.tengel.app.test' not in bp, '本番の アプリの ID は jp.tengel.app の まま（テスト版だけ jp.tengel.app.test：第4.122版）')
    res = sorted(os.listdir(os.path.join(out, 'Tengel.swiftpm', 'Resources')))
    _tp = os.path.join(out, 'Tengel.swiftpm', 'Resources', 'mother_template.xlsx')
    try:
        import zipfile as _zf
        import html as _h
        _z = _zf.ZipFile(_tp); _wb = _z.read('xl/workbook.xml').decode('utf8'); _ss = _h.unescape(''.join(_z.read(n).decode('utf8') for n in _z.namelist() if n.startswith('xl/worksheets/')))
        _tok = '検証データ' in _wb and all(h in _ss for h in ('日付', '単勝1位', '3連単1位', '1着人気', '2着人気', '集計対象')) and not any(w in _ss for w in ('大井', 'JRA', '船橋'))
    except Exception as _e:
        _tok = False
    check('mother_template.xlsx' in res and _tok, '第4.123版：マザーデータの 入力用 Excel の ひな形（シート「検証データ」・A〜P列の 見出し・開催場の 名前なし）が 入っている')
    html = open(os.path.join(out, 'Tengel.swiftpm', 'Resources', 'index.html'), encoding='utf8').read()
    check('TengelPoints' in html and 'TengelWallet' in html and 'id="gate"' in html and 'touch-action:manipulation' in html, 'アプリの画面に ポイント・アプリを開いた時の画面・拡大の決まりが入っている')
    check(all(os.path.exists(os.path.join(out, 'Tengel.swiftpm', f)) for f in ('Markers.swift', 'Store.swift', 'Notify.swift')), 'Markers.swift・Store.swift・Notify.swift が入っている')
    check('TengelReserve' in html and 'TengelCustomRate' in html and 'parseResult' in html and 'omakaseBtn' in html, 'アプリの画面に 買い目の予約・%・結果の画像の読み取り・テンゲルにお任せ が入っている（第2弾）')
    # 第3弾：的中ボタン（見本の CSS/HTML を束ねた __FX・fx.js・設定のカード）。絵と音は手元の ios/fx_assets/ から Resources/ へ（リポジトリには入れない）
    check('window.__FX=' in html and 'window.TengelFx' in html and "'tengel.fxhidden'" not in html and 'setFx' in html and 'fz_nglow.webp' not in html and 'fz_ncore.webp' not in html and 'sfx_fz.m4a' not in html and 'sfx_fz_push.m4a' in html and '/_blob/' not in html, 'アプリの画面に 的中ボタン（__FX・fx.js・設定の「的中の演出」）が入っている・見本の絵の場所（/_blob/）が残っていない（第3弾）・隠れど的中の 数（tengel.fxhidden）は 使わない（第4.86版）・前の ど的中の ネオンの 絵と 音は 入れない（第4.109版）')
    sys.path.insert(0, os.path.join(W, 'kisekae')); from build_fx import ASSET_FILES
    have = [f for f in ASSET_FILES if f in res]
    check(len(have) in (0, len(ASSET_FILES)) and (not os.path.isdir(os.path.join(W, 'ios', 'fx_assets')) or len(have) == len(ASSET_FILES)), f'的中ボタンの絵と音：手元にあれば{len(ASSET_FILES)}こ全部 Resources/ に入る・なければ入れずに作れる（{len(have)}こ）')
    # 第5弾：特別な 演出（16.3）。見本の CSS と HTML を 束ねた __FX の reveal（pc・sgd・spg・sd・nd）・絵と 音と 動画の 名前・動画の <video>（fx.js）・Swift の Range（動画の 部分読み）
    # 第4.86版：隠れど的中・超プレミアムど的中・神様的中は なし（押したあと・神様の 絵と 音・CSS は 入れない。超プレミアムの CSS と 音は 超プレミアム神様が 使うので のこる）
    from build_fx import FILMS, STILL, ART, SFX
    import json as _json
    FXJ = _json.JSONDecoder().raw_decode(html.split('window.__FX=')[1])[0]
    check(all(f"'{k}'" in html or f'"{k}"' in html for k in ('pc', 'sgd', 'spg', 'sd', 'nd', 'gk')) and all(v in html for v in list(FILMS.values()) + list(STILL.values()) + [SFX[k] for k in ('pc', 'zp', 'sgd', 'spg_up', 'spg', 'sd', 'sdp', 'nd', 'ndt', 'gk')]) and 'pm_face_F.webp' in html and 'sd_last.webp' in html and 'sd_t_hit.webp' not in html and 'sd_horse.webp' not in html and 'sd_film.mp4' in html
          and 'nd_film.mp4' in html and 'nd_last.webp' in html and '.fxs .ov.fz.nd' in html
          and 'gk_film.mp4' in html and 'gk_last.webp' in html and 'sfx_gk.m4a' in html and '.fxs .ov.fz.gk' in html and FXJ['board']['titles'].get('gk') == '神様極的中！！！' and FXJ['t'].get('GKB') == 12.0   # 第4.117版：神様極的中
          and '.fxs .ov.fz.sgd' in html and '.fxs .ov.fz.pm' in html and '.fxs .ov.fz.zp' in html and '.fxs .ov.fz.sd' in html and "data-film" in html and 'WAIT_MAX' in html and '.ph ' not in html.split('window.__FX=')[1][:400000]
          and sorted(FXJ['reveal']) == ['big', 'gk', 'hit', 'hit_t', 'miss', 'nd', 'pc', 'sd', 'sgd', 'spg'] and sorted(FXJ['push']) == ['big_t', 'fz_t', 'hit', 'hit_t'] and 'fz' not in FXJ['sfx'] and '.nic' not in FXJ['css'] and 'gd' not in FXJ['art'] and 'gd' not in FXJ['sfx'] and 'gd' not in FXJ['board']['titles'] and 'hidden' not in FXJ['board']['titles']
          and 'gd_dome.webp' not in html and 'sfx_gd.m4a' not in html and '.fxs .ov.fz.gd' not in html and 'GD' not in FXJ['t'] and 'ZP' not in FXJ['t'],
          'アプリの画面に 特別な 演出（プレミアム・超神様・超プレミアム神様・紫電・ノーマルど的中・神様極的中の CSS と HTML・絵と 音と 動画の 名前・動画の しくみ）が入っている（第5弾・第4.66版・第4.71版・第4.77版・第4.117版）・第4.86版：隠れど的中・超プレミアムど的中・神様的中は 入って いない')
    check(len(ART['pm']) == 43 and all(f'pm_fin{x}.webp' in ART['pm'] for x in ('', '_n', '_g', '_w', '_s', '_sh')) and 'gd' not in ART and 'gd' not in SFX and ART['sd'] == ['sd_last.webp'] and ART['nd'] == ['nd_last.webp'] and ART['gk'] == ['gk_last.webp'] and len(FILMS) == 5 and len(ASSET_FILES) == 15 + 43 + 4 + 5 + 5 and ASSET_FILES[:5] == ['bcx_hb_eye.webp', 'bcx_hb_fore.webp', 'bcx_hb_head.webp', 'bcx_hb_hind.webp', 'bcx_hb_tail.webp'] and not [f for f in ASSET_FILES if f.startswith('bcx_ph')], f'絵と音と動画の 数：音 15（第4.86版：神様的中の 音は なし・第4.109版：前の ど的中の 音と ネオンの 絵 2まいは 入れない・第4.117版：神様極的中の 音）・プレミアム 43（第4.80版：最後の ゼリーの ハートは 体・星空・つや・字・小さな ハート・かげの 6まい）・さいごの 1まい 4（超神様・紫電・ノーマルど的中・神様極的中）・動画 5・ボードを持つ馬の 部品 5（第4.108版）・結果ボードカスタムの 幻の 馬の 絵 2まいは 入れない（第4.113版：出世馬と いっしょに 消した）（{len(ASSET_FILES)}）')
    check('root.TengelBoardArt = {' in html and 'window.TengelBoard = {' in html and 'setBoard' in html and 'jp.tengel.app.boardcustom' in html
          and html.index('root.TengelBoardArt = {') < html.index('window.TengelBoard = {') and html.index('window.TengelKisekae') < html.index('window.TengelBoard = {')
          and 'TengelBoardPhantom' not in html and 'bcx_ph0.webp' not in html and 'bcx_ph1.webp' not in html and 'bcxph' not in html and not os.path.exists(os.path.join(W, 'bcx_phantom.js')),
          'アプリの画面に 結果ボードカスタム（絵・飾りの しくみ・設定の カード・商品）が入っている（第4.91版）・第4.113版：出世馬の 幻の 馬（形・絵）は 入って いない')
    # 第4.108版：結果ボードカスタム「ボードを持つ馬」（第4.113版から 16番）：部品の 四角（bcx.js の HBX）と 絵を 作る 道具（kisekae/r3d/fx/board_horse_parts.py の HBX）が 同じ・アプリの 画面に 絵の 名前
    import re as _re2
    def _hbx(txt, pat):
        m = _re2.search(pat, txt, _re2.S)
        return {k: [int(x) for x in v.split(',')] for k, v in _re2.findall(r'(\w+)[:=]\s*\[([-\d,\s]+)\]', m.group(1))} if m else None
    hbx_js = _hbx(open(os.path.join(W, 'bcx.js'), encoding='utf8').read(), r'const HBX = \{(.*?)\};')
    hbx_py = _hbx(open(os.path.join(W, 'kisekae', 'r3d', 'fx', 'board_horse_parts.py'), encoding='utf8').read(), r'HBX = dict\((.*?)\)\n')
    check(bool(hbx_js) and hbx_js == hbx_py and len(hbx_js) == 11 and all(v in html for v in ('bcx_hb_head.webp', 'bcx_hb_fore.webp', 'bcx_hb_hind.webp', 'bcx_hb_tail.webp', 'bcx_hb_eye.webp')) and 'bcECarry' in html,
          f'結果ボードカスタム 16「ボードを持つ馬」：部品の 四角が 絵を 作る 道具と 同じ（{hbx_js}）・絵の 名前と 登場の 動き（bcECarry）が 入って いる（第4.108版）')
    # 第4.121版：まさちゃんの 絵の ボード 14こ（window.__BCP：kisekae/bcp/bcp_app.py）。絵（bcp_*.webp）は 手元の ios/bcp_assets/ から Resources/ へ（リポジトリには 入れない・CI は なし）
    sys.path.insert(0, os.path.join(W, 'kisekae', 'bcp')); import bcp_app as _bcp
    BCPJ = _json.JSONDecoder().raw_decode(html.split('window.__BCP=')[1])[0] if 'window.__BCP=' in html else {}
    bfiles = _bcp.files(); bhave = [f for f in bfiles if f in res]; bdir = os.path.join(W, 'ios', 'bcp_assets')
    check(len(BCPJ.get('items', {})) == 14 and len(BCPJ.get('d', {})) == 59 and html.index('window.__BCP=') < html.index('window.TengelBoard = {')
          and [i for i, _, _ in _bcp.ITEMS] == ['ring', 'toast', 'race', 'snap', 'seal', 'cup', 'hoist', 'bloom', 'climb', 'rain', 'next', 'cover', 'wait', 'pen']
          and [len(BCPJ['items'][i]['st']) for i in ('ring', 'climb', 'rain')] == [4, 7, 4] and BCPJ['items']['climb']['st'][-1] == [24, 'shusse24'] and len(bfiles) == 14 + 11 + 346 and len(bfiles) == len(set(bfiles))
          and len(bhave) in (0, len(bfiles)) and (not os.path.isdir(bdir) or len(bhave) == len(bfiles)) and not any(f.endswith('.png') for f in bhave),
          f'第4.121版：アプリの画面に 絵の ボード 14こ（段 59・出世馬は 1〜24連勝の 7段）・絵 {len(bhave)}/{len(bfiles)}こ（見本 14＋止まった 絵 11＋動く 絵 346：第4.145版・手元に あれば ぜんぶ・CI は なし）')
    # 第4.129版：動く 絵の ボード（キャラが 動く）52段＝出世馬の 7段 いがい ぜんぶ。動きの データ（mo）は 段ごと・絵は 動く 絵の 名前 だけ（第4.145版：トロフィーの 向きの 絵を 1組に して 355 → 346）
    mo_d = [k for k, v in BCPJ.get('d', {}).items() if v.get('mo')]
    mo_f = sorted({f for n in _bcp.MOTION for f in _bcp.motion_files(n)})
    check(len(mo_d) == 52 and sorted(mo_d) == sorted(_bcp.MOTION) and not any(k.startswith('shusse') for k in mo_d) and len(mo_f) == 346 and set(mo_f) <= set(bfiles)
          and all(BCPJ['d'][k]['mo'] == _bcp.MOTION[k] for k in mo_d) and all(len(BCPJ['d'][k]['mo']['layers']) > 0 or BCPJ['d'][k]['mo'].get('amb') for k in mo_d)
          and 'function picParts(' in html and 'function ambStart(' in html and '.chrgo' in html,
          f'第4.129版：動く 絵の ボード {len(mo_d)}段（出世馬 いがい）・動く 絵 {len(mo_f)}こ・picParts（キャラ）・ambStart（まわりの 光と 雲）が 入って いる')
    # 第4.145版（まさちゃん 11/10「やって！」）：止まった 版を 入れない。キャラなしの 背景（bgx）が ある 48段は 止まった 絵（背景 48・前の 絵 35＝83まい・約13.5MB）を Resources に 入れず、
    #   部品を 重ねて 同じ 絵を 出す（bcx.js の picBg・picFg・.bcpld）。トロフィー 4段（光と 雲だけ）と 出世馬 7段は 止まった 絵の まま。トロフィーの 光と 雲の 向きの 絵（m1〜m3）は 4段で 1組
    so = _bcp.stills_out(); par = [k for k in mo_d if BCPJ['d'][k]['mo'].get('bgx')]
    amb_m = {BCPJ['d'][k]['mo']['amb'][m] for k in mo_d if BCPJ['d'][k]['mo'].get('amb') for m in ('m1', 'm2', 'm3')}
    bsz = sum(os.path.getsize(os.path.join(bdir, f)) for f in bhave) if bhave else 0
    check(len(par) == 48 and len(so) == 83 and not any(f in res for f in so) and not (set(so) & set(bfiles)) and all((f'bcp_{k}.webp' in so) == (k in par) for k in BCPJ['d'])
          and all(bool(BCPJ['d'][k].get('fg')) == bool(BCPJ['d'][k]['mo'].get('fgx')) for k in par) and all(f'bcp_{k}.webp' in bfiles for k in BCPJ['d'] if k not in par)
          and amb_m == {'bcp_trophy1a_m1.webp', 'bcp_trophy1a_m2.webp', 'bcp_trophy1a_m3.webp'} and not any(f in res for f in ('bcp_trophy2a_m1.webp', 'bcp_trophy3a_m2.webp', 'bcp_trophy4a_m3.webp'))
          and (not bhave or 21.0e6 < bsz < 22.5e6) and 'bcpld' in html and "decoding = 'sync'" in html and 'bcp_${name}.webp' in html,
          f'第4.145版：止まった 版 {len(so)}まい（部品を 重ねる {len(par)}段の 背景と 前の 絵）は アプリに 入れない・のこりの 11段（トロフィー・出世馬）は 入れる・'
          f'トロフィーの 光と 雲の 向きの 絵は 1組（{len(amb_m)}まい）・絵 ぜんぶで {bsz / 1e6:.1f}MB（前は 約36.0MB）')
    fxd = os.path.join(W, 'ios', 'fx_assets')
    if os.path.isdir(fxd) and all(os.path.exists(os.path.join(fxd, f)) for f in ASSET_FILES):
        sz = sum(os.path.getsize(os.path.join(fxd, f)) for f in ASSET_FILES)
        films_sz = sum(os.path.getsize(os.path.join(fxd, f)) for f in FILMS.values())
        gk_sz = os.path.getsize(os.path.join(fxd, 'gk_film.mp4'))
        check(37.9e6 < films_sz < 41.5e6 and 43.6e6 < sz < 47.3e6 and 8.0e6 < gk_sz < 11.2e6, f'絵と音と動画の 大きさ：動画 5本 約39.5MB（第4.77版：ノーマルど的中の 動画 約5.0MB・10.5秒／第4.117版：神様極的中の 動画 12秒：第4.136版 さいごの 字を 入れかえ・第4.137版 極の 雷で 約9.3MB）・ぜんぶで 約45.2MB（第4.86版：神様的中の 絵と 音 約2MB を 入れない）（{films_sz / 1e6:.1f}MB・{sz / 1e6:.1f}MB・神様極的中 {gk_sz / 1e6:.2f}MB）')
    af = open(os.path.join(W, 'ios', 'Tengel.swiftpm', 'AppFiles.swift'), encoding='utf8').read()
    check('byteRange' in af and 'Content-Range' in af and 'Accept-Ranges' in af and '"mp4": return "video/mp4"' in af and 'statusCode: status' in af and 'options: .alwaysMapped' in af, 'AppFiles.swift：動画の 部分読み（Range → 206・Content-Range）と mp4 の MIME・ファイルは メモリに 写す だけ（第4.109版：Range の たびに まるごと 読まない）')
    # 第4.109版：基本の フォント（BIZ UDPGothic 2つ・Dela Gothic One）は 字は そのままで WOFF2（ios/fonts/make_woff2.py）・IBM Plex Mono（予約名「Plex」）は TTF の まま
    check(all(f in res for f in ('BIZUDPGothic-Regular.woff2', 'BIZUDPGothic-Bold.woff2', 'DelaGothicOne-Regular.woff2', 'IBMPlexMono-Medium.ttf', 'IBMPlexMono-SemiBold.ttf'))
          and not any(f in res for f in ('BIZUDPGothic-Regular.ttf', 'BIZUDPGothic-Bold.ttf', 'DelaGothicOne-Regular.ttf'))
          and "url('fonts/BIZUDPGothic-Regular.woff2') format('woff2')" in html and "url('fonts/DelaGothicOne-Regular.woff2') format('woff2')" in html and "url('fonts/IBMPlexMono-Medium.ttf') format('truetype')" in html
          and subprocess.run(['python3', os.path.join(W, 'ios', 'fonts', 'make_woff2.py'), '--check'], capture_output=True).returncode == 0,
          '基本の フォント：BIZ UDPGothic・Dela Gothic One は WOFF2（字の 形は もとの TTF と 同じ）・IBM Plex Mono は TTF の まま（第4.109版）')
    # 第4.59版：iPad で 画面いっぱいに 動かす とき（時計の 帯の 高さが 0 と 伝わる）の あき（Swift と Web の 両方）・ふつうの 作り方には テスト版の 印が ない
    wv = open(os.path.join(out, 'Tengel.swiftpm', 'TengelWebView.swift'), encoding='utf8').read()
    check('userInterfaceIdiom == .pad' in wv and 'safeAreaInsets.bottom > 0 ? 24 : 20' in wv and '--top-inset2' in html and 'var(--top-inset2,0px)' in html, 'iPad で 画面いっぱいの とき 上の帯を 時計の 帯の ぶん あける（Swift の 24/20pt・Web の 24px）')
    check('window.__TEST=true;' not in html and 'テスト版の道具' in html and 'gift-test' in html, 'ふつうの 作り方：テスト版の 印（__TEST=true）は 入って いない（道具の コードは あるが 動かない）')
    gi = open(os.path.join(W, '.gitignore'), encoding='utf8').read()
    check('ios/fx_assets/' in gi and subprocess.run(['git', 'check-ignore', '-q', 'source/ios/fx_assets/sfx_fz_push.m4a'], cwd=os.path.dirname(W)).returncode == 0, '絵と音のフォルダ（ios/fx_assets/）は git に入らない（source/.gitignore）')
    # 第4弾：着せ替え（30テーマの変数と @font-face を束ねた __KS・kisekae.js・設定のカード・テーマごとの ks_<id>.json・しぼった字・見本の絵は手元の ios/kisekae_blobs/ から）
    import json as _json, re as _re
    ks_json = [f for f in res if _re.fullmatch(r'ks_[a-z]+\.json', f)]
    check('window.__KS=' in html and 'window.TengelKisekae' in html and "'tengel.kisekae'" in html and 'setKisekae' in html and 'html[data-ks=\\"sakura\\"]' in html and "@font-face{font-family:'Kaisei Decol'" in html and 'fonts/KaiseiDecol-700.woff2' in html,
          'アプリの画面に 着せ替え（__KS・kisekae.js・設定の「着せ替え」・テーマの変数・テーマの字の @font-face）が入っている（第4弾）')
    sys.path.insert(0, os.path.join(W, 'kisekae')); import pack as _pack
    n_ks = 29 + len(_pack.IDS)                                           # 第4.92版：壁紙パックの 11枚・第4.109版：いつもの（default）の ks_default.json は 入れない（kisekae.js が 読まない）
    check(len(ks_json) == n_ks and all(f in res for f in ('ks_banner_ranch.svg', 'ks_banner_cute.svg', 'ks_banner_kids.svg', 'ks_banner_gold.svg')) and all(f'ks_{t}.json' in res for t in _pack.IDS),
          f'テーマごとの ks_<id>.json が {n_ks}こ（いつもの 以外の 29＋壁紙パック {len(_pack.IDS)}・ks_default.json は なし）と 定番4の止まった絵（{len(ks_json)}）')
    rsvg = open(os.path.join(out, 'Tengel.swiftpm', 'Resources', 'ks_banner_ranch.svg'), encoding='utf8').read(); gsvg = open(os.path.join(out, 'Tengel.swiftpm', 'Resources', 'ks_banner_gold.svg'), encoding='utf8').read()
    check('*{animation:none!important}</style>' in rsvg and '*{animation:none!important}</style>' in gsvg and '.kslive{' in html and '.kslv{' in html and 'rescope' in html and 'rbwSvg' in html and 'mask-type:alpha' in html,
          '第4.89版：選ぶ画面の 牧場・ぷりけつの 小さな絵は 止めた SVG・選んだ タイルだけ 動く 壁紙（.kslive）・形の ある PUSH の 虹は SVG の 中（rbwSvg・mask）')
    sk = _json.load(open(os.path.join(out, 'Tengel.swiftpm', 'Resources', 'ks_sakura.json'), encoding='utf8'))
    check(sk['bnr'] and '<div class="bnrw">' in sk['bnr']['html'] and 'ks_cbcbaeebec4470155b1587d5a5c8fe00.webp' in sk['bnr']['html'] and '#ksBnr .bnrw' in sk['bnr']['css'] and '@keyframes kb' in sk['bnr']['css'] and '/_blob/' not in _json.dumps(sk)
          and sk['push']['pc'] == 'sk' and '<svg' in sk['push']['svg'] and 'class="clips sk"' in sk['push']['burst'] and '.fxs .push.sk' in sk['push']['css'] and '.fxs .rb.t-sakura{' in sk['board']['css'] and '<svg class="orn"' in sk['board']['orn'],
          'ks_sakura.json：上の絵（#ksBnr の中だけ・@keyframes に kb）・桜の PUSH（面・はじける花びら・.fxs の中だけ）・ボードの変数と飾り・見本の絵の場所（/_blob/）が残っていない')
    # 第4.87版：雪の 白い 息（ページが いつも 動かす・鼻に ついて いく・視差効果を減らす ときは 止まった 3つ）・ネオンの 光のつぶ（236こ ばらばら・keyframes に 変数なし・光のつぶの 絵なし）
    sn = _json.load(open(os.path.join(out, 'Tengel.swiftpm', 'Resources', 'ks_snow.json'), encoding='utf8'))
    nn = _json.load(open(os.path.join(out, 'Tengel.swiftpm', 'Resources', 'ks_neon.json'), encoding='utf8'))
    sh, sc, nh, nc = sn['bnr']['html'], sn['bnr']['css'], nn['bnr']['html'], nn['bnr']['css']
    check('<div class="ykb" aria-hidden="true">' in sh and sh.count('animation-name:kbykbP0') == 5 and '<div class="ykbs" aria-hidden="true">' in sh and sh.count('<i style="left:') >= 3
          and '#ksBnr .ykb{' in sc and '@keyframes kbykbA{' in sc and '@keyframes kbykbP04{' in sc and '.ykbs{display:block}' in sc,
          'ks_snow.json：白い 息は ページで（鼻の 前で 玉 5こが じゅんに 生まれて 流れる・鼻に ついて いく keyframes・視差効果を減らす ときは 止まった 3つ）（第4.87版）')
    kfb = _re.findall(r'@keyframes ([\w-]+)\{((?:[^{}]*\{[^{}]*\})*)\}', nc)
    check(nh.count('<i class="') == 236 and nh.count('<b class="ln s') == 63 and 'nqd' not in nh + nc and '70fc21205005d11eddef8ebd6c78ee31' not in nh + nc
          and [len([k for k, _ in kfb if _re.fullmatch(pre + r'\d+', k)]) for pre in ('kbnqL', 'kbnqM', 'kbnqS')] == [16, 16, 8] and all('var(' not in body for _, body in kfb)
          and '.nqw .nqp i,#ksBnr .nqw .nqp .ln{animation:none!important}' in nc,
          f'ks_neon.json：光のつぶ 236こ（点 173・筋 63）が ばらばらに 動く（予定 16本・keyframes の 中に CSS の 変数なし・視差効果を減らす ときは 止まる）・光のつぶの 絵（dust）は 使わない（第4.87版）・光の 横線（筋）は 長く ランダムに のびちぢみ（予定 8本・第4.88版）')
    # 第4.90版：お正月の 馬に 羊の 着ぐるみ（上の 絵の 前の 1まいと 止まった 絵を 入れかえ・絵の 説明も）
    nyj = _json.load(open(os.path.join(out, 'Tengel.swiftpm', 'Resources', 'ks_newyear.json'), encoding='utf8'))
    nys = _json.dumps(nyj, ensure_ascii=False)
    check('ks_71103dfe1944fc7f65705100d4c4455b.webp' in nys and 'ks_8a0dd088ce2e9027f40cbf18a14bf4f1.webp' in nys and 'ac724e18f8d2213f131e7dd2c347cfd0' not in nys
          and '羊の着ぐるみ' in nyj['bnr']['html'] and '金のたてがみ' not in nys,
          'ks_newyear.json：お正月の 馬は 羊の 着ぐるみ（光より 前の 絵 71103dfe…・うしろの 絵は 同じ・絵の 説明に「羊の着ぐるみ」）（第4.90版）')
    for f in ks_json:
        txt = open(os.path.join(out, 'Tengel.swiftpm', 'Resources', f), encoding='utf8').read()
        for w in ('大井', 'JRA', 'まさちゃん', '第13', '改訂'):
            if w in txt: fails.append(f'{f} に {w}')
    fonts_ks = _json.load(open(os.path.join(W, 'ios', 'fonts', 'ks', 'fonts.json'), encoding='utf8'))
    check(len(fonts_ks['fonts']) >= 40 and all(r['file'] in res for r in fonts_ks['fonts']) and all(os.path.exists(os.path.join(W, 'ios', 'fonts', 'ks', 'OFL-' + r['family'].replace(' ', '') + '.txt')) for r in fonts_ks['fonts']) and fonts_ks['total'] < 4_500_000,   # 第4.92版：壁紙パックの 見出しの 字 7つ（約0.4MB）を 足して 約4.1MB
          f'テーマの字（しぼった WOFF2 {len(fonts_ks["fonts"])}こ・{fonts_ks["total"] / 1e6:.1f}MB）が Resources/ に入る・OFL の全文がある')
    # しぼった字に 画面の言葉が ぜんぶ入っている（UI の文字がふえたら kisekae/build_fonts.py を もう一度）
    sys.path.insert(0, os.path.join(W, 'kisekae')); import build_fonts as _bf
    have_b = set(open(os.path.join(W, 'ios', 'fonts', 'ks', 'chars_body.txt'), encoding='utf8').read())
    need_b = set(_bf.body_chars()) - have_b
    check(not need_b, f'しぼった字に 画面の言葉が ぜんぶ入っている（足りない字 {len(need_b)}：{"".join(sorted(need_b))[:30]}）→ 足りなければ python3 kisekae/build_fonts.py')
    ks_imgs = [f for f in res if _re.fullmatch(r'ks_[0-9a-f]{32}\.(webp|svg)', f)]
    n_pk = len({v['id'] for t in _pack.IDS for v in _pack.blobs(t).values()})   # 第4.92版：壁紙パックの 絵（馬の コマの シート・止まった 絵：pack/blobs.json）
    check(len(ks_imgs) in (0, 99 + n_pk) and (not os.path.isdir(os.path.join(W, 'ios', 'kisekae_blobs')) or len(ks_imgs) == 99 + n_pk), f'着せ替えの絵：手元にあれば99こ全部 Resources/ に入る・なければ入れずに作れる（{len(ks_imgs)}こ。第4.63版：勝負服の tile2・ネオンの dust と つぶなしの 止まった絵が 足された。第4.64版：ネオンの 止まった絵は 背景だけの 絵に 入れかわり・桜の 止まった絵と シートも 入れかわり＝数は 同じ。第4.87版：ネオンの dust（光のつぶの 絵）は 使わない＝光のつぶは 1つずつ ページが 動かす → 99こ。第4.92版：壁紙パックの 絵 {n_pk}こ を 足す）')
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
    # 第4.122版：テスト版は 本番と 別の アプリ（jp.tengel.app.test）・ビルド番号は あげる たびに 大きく（APP_VER から・ない ときは 日時）＝ TestFlight で iPhone に 本番と 並べて 入れる
    check('name: "テンゲル テスト",' in ps2 and 'bundleIdentifier: "jp.tengel.app.test",' in ps2 and 'bundleIdentifier: "jp.tengel.app",' not in ps2 and re.search(r'bundleVersion: "\d{8}\.\d+",', ps2) and 'supportedDeviceFamilies: [\n                .phone\n            ]' in ps2,
          'テスト版：アプリの 名前は「テンゲル テスト」・bundle id は jp.tengel.app.test（本番と 並べて 入れられる）・ビルド番号は 日付から・iPhone用は ふつうと 同じ')
    check('window.__TEST=true;' in h2 and 'テスト版の道具' in h2, 'テスト版：画面に __TEST（はじめから 10,000P・設定の いちばん上に テスト版の道具）')
shutil.rmtree(out2, ignore_errors=True)
shutil.rmtree(out, ignore_errors=True)   # 2026/11/04：作った アプリ（約190MB）を 残さない（前は /tmp に 1回ごとに 残って いた）
print('結果：', 'OK' if not fails else f'{len(fails)}件おかしい')
raise SystemExit(1 if fails else 0)
