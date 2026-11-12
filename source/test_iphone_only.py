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
    # 第4.162版（まさちゃん 2026/11/12 22:56「プレミアムど的中／超プレミアム神様的中／この二つ消して！」・22:32「一枚目の球体のシーン消して！…鳥居とか文字関係はこのファイルのデータを使って！」）：
    #   プレミアムど的中（pc）・超プレミアム神様的中（spg）の 押したあと・CSS（.pm・.zp・.spu）・絵（pm_…）・音（pc・zp・spg・spg_up）・昇格の 動画（spg_up）は 入れない。
    #   超神様の 動画・さいごの 1まい・音は 新しい もの（sgd_film2.mp4・sgd_last2.webp・sfx_sgd2.m4a：12.83秒・ボード 12.93秒）。前の もの（sgd_film.mp4 など）は 入れない
    from build_fx import FILMS, STILL, ART, SFX
    import json as _json
    FXJ = _json.JSONDecoder().raw_decode(html.split('window.__FX=')[1])[0]
    check(all(f"'{k}'" in html or f'"{k}"' in html for k in ('sgd', 'sd', 'nd', 'gk')) and all(v in html for v in list(FILMS.values()) + list(STILL.values()) + [SFX[k] for k in ('sgd', 'sd', 'sdp', 'nd', 'ndt', 'gk')]) and 'sd_last.webp' in html
          and sorted(SFX) == ['big', 'big_push', 'fz_push', 'gk', 'hit', 'hit_push', 'nd', 'ndt', 'sd', 'sdp', 'sgd'] and sorted(FILMS) == ['gk_film', 'nd_film', 'sd_film', 'sgd_film'] and sorted(FXJ['sfx']) == sorted(SFX) and sorted(FXJ['films']) == sorted(FILMS)
          and [FILMS['sgd_film'], STILL['sgd_last'], SFX['sgd']] == ['sgd_film2.mp4', 'sgd_last2.webp', 'sfx_sgd2.m4a'] and FXJ['t']['SG'] == {'FILM': 12.8333, 'RES': 12.9333, 'STILL_FROM': 12.8333, 'STILL_WAIT': 1.0, 'STILL_BOARD': 1.3, 'WAIT_MAX': 4.0} and 'PC' not in FXJ['t']
          and not any(x in html for x in ('pm_face_F.webp', 'pm_fin.webp', 'sfx_pc.m4a', 'sfx_zp.m4a', 'sfx_spg.m4a', 'sfx_spg_up.m4a', 'spg_up.mp4', 'sgd_film.mp4', 'sgd_last.webp', 'sfx_sgd.m4a', '.fxs .ov.fz.pm', '.fxs .ov.fz.zp', '.fxs .spu', '.fxs .zpdefs', 'spgGo', 'spzOv')) and 'sd_t_hit.webp' not in html and 'sd_horse.webp' not in html and 'sd_film.mp4' in html
          and 'nd_film.mp4' in html and 'nd_last.webp' in html and '.fxs .ov.fz.nd' in html
          and 'gk_film.mp4' in html and 'gk_last.webp' in html and 'sfx_gk.m4a' in html and '.fxs .ov.fz.gk' in html and FXJ['board']['titles'].get('gk') == '神様極的中！！！' and FXJ['t'].get('GKB') == 12.0   # 第4.117版：神様極的中
          and '.fxs .ov.fz.sgd' in html and '.fxs .ov.fz.sd' in html and "data-film" in html and 'WAIT_MAX' in html and '.ph ' not in html.split('window.__FX=')[1][:400000]
          and sorted(FXJ['reveal']) == ['big', 'gk', 'hit', 'hit_t', 'miss', 'nd', 'sd', 'sgd'] and sorted(FXJ['push']) == ['big_t', 'fz_t', 'hit', 'hit_t'] and 'fz' not in FXJ['sfx'] and '.nic' not in FXJ['css'] and 'gd' not in FXJ['art'] and 'gd' not in FXJ['sfx'] and 'gd' not in FXJ['board']['titles'] and 'hidden' not in FXJ['board']['titles']
          and 'gd_dome.webp' not in html and 'sfx_gd.m4a' not in html and '.fxs .ov.fz.gd' not in html and 'GD' not in FXJ['t'] and 'ZP' not in FXJ['t'],
          'アプリの画面に 特別な 演出（超神様・紫電・ノーマルど的中・神様極的中の CSS と HTML・絵と 音と 動画の 名前・動画の しくみ）が入っている（第5弾・第4.66版・第4.71版・第4.77版・第4.117版）・第4.86版：隠れど的中・超プレミアムど的中・神様的中は 入って いない・'
          '第4.162版：プレミアムど的中・超プレミアム神様的中（押したあと・CSS・絵・音・昇格の 動画・くじ）は 入って いない・超神様の 動画／さいごの 1まい／音は 新しい もの（sgd_film2.mp4・sgd_last2.webp・sfx_sgd2.m4a：12.83秒）')
    check('pm' not in ART and not [f for f in ASSET_FILES if f.startswith(('pm_', 'spg', 'sfx_pc', 'sfx_zp', 'sfx_spg'))] and 'gd' not in ART and 'gd' not in SFX and ART['sd'] == ['sd_last.webp'] and ART['nd'] == ['nd_last.webp'] and ART['gk'] == ['gk_last.webp'] and ART['sgd'] == ['sgd_last2.webp'] and len(FILMS) == 4 and len(ASSET_FILES) == 11 + 4 + 4 + 5 and ASSET_FILES[:5] == ['bcx_hb_eye.webp', 'bcx_hb_fore.webp', 'bcx_hb_head.webp', 'bcx_hb_hind.webp', 'bcx_hb_tail.webp'] and not [f for f in ASSET_FILES if f.startswith('bcx_ph')], f'絵と音と動画の 数：音 11（第4.86版：神様的中の 音は なし・第4.109版：前の ど的中の 音と ネオンの 絵 2まいは 入れない・第4.117版：神様極的中の 音・第4.162版：プレミアム／超プレミアム／超プレミアム神様／昇格の 音 4こは なし）・プレミアムの 絵 43まいは なし（第4.162版）・さいごの 1まい 4（超神様・紫電・ノーマルど的中・神様極的中）・動画 4（第4.162版：昇格の 動画は なし）・ボードを持つ馬の 部品 5（第4.108版）・結果ボードカスタムの 幻の 馬の 絵 2まいは 入れない（第4.113版：出世馬と いっしょに 消した）（{len(ASSET_FILES)}）')
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
          and [len(BCPJ['items'][i]['st']) for i in ('ring', 'climb', 'rain')] == [4, 7, 4] and BCPJ['items']['climb']['st'][-1] == [24, 'shusse24_3d'] and 't' not in BCPJ['items']['climb'] and BCPJ.get('thumb') == 'bcp_t_{}_b.webp' and len(bfiles) == 14 + 59 + 35 and len(bfiles) == len(set(bfiles))
          and len(bhave) in (0, len(bfiles)) and (not os.path.isdir(bdir) or len(bhave) == len(bfiles)) and not any(f.endswith('.png') for f in bhave),
          f'第4.121版：アプリの画面に 絵の ボード 14こ（段 59・出世馬は 1〜24連勝の 7段）・絵 {len(bhave)}/{len(bfiles)}こ（見本 14＋止まった 絵 59＋前の 絵 35：第4.150版・手元に あれば ぜんぶ・CI は なし）')
    # 第4.150版（まさちゃん 2026/11/11 02:36「結果カスタムボードの動き全部無くして！ボードを持つ馬も含めて！その代わり、画質あげて！」）：絵の ボードは 動かない。
    #   アプリの データ（window.__BCP）に 動きの データ（mo）は ない・動く 絵の 部品（キャラなしの 背景・キャラ・光と 雲：346まい）は Resources に 入れない・
    #   59段 ぜんぶ 止まった 絵（bcp_<デザイン>.webp）と 前の 絵（_fg.webp：35段）を 入れる。絵は もとの 画質の まま（軽く しない：下の 第4.146版の 所）。
    #   （第4.129版〜第4.149版：キャラが 動く 52段は 部品を 重ねて 出して いた・第4.145版から その 止まった 版 83まいは 入れて いなかった）
    mo_d = [k for k, v in BCPJ.get('d', {}).items() if v.get('mo')]
    mo_f = sorted({f for n in _bcp.MOTION for f in _bcp.motion_files(n)})
    so = _bcp.stills_out()
    bsz = sum(os.path.getsize(os.path.join(bdir, f)) for f in bhave) if bhave else 0
    check(mo_d == [] and len(mo_f) == 346 and not (set(mo_f) & set(bfiles)) and not any(f in res for f in mo_f) and so == []
          and all((BCPJ['d'][k].get('p') or f'bcp_{k}.webp') in bfiles for k in BCPJ['d']) and sum(1 for k in BCPJ['d'] if BCPJ['d'][k].get('p') == f'bcp_{k}_bl.webp') == 52 and 'D.p ||' in html and all((f'bcp_{k}_fg.webp' in bfiles) == bool(BCPJ['d'][k].get('fg')) for k in BCPJ['d']) and sum(1 for k in BCPJ['d'] if BCPJ['d'][k].get('fg')) == 35
          and (not bhave or 16.2e6 < bsz < 17.3e6) and 'bcpld' in html and "decoding = 'sync'" in html and 'bcp_${name}.webp' in html and 'const st = true' in html,
          f'第4.150版：絵の ボードは 動かない：動きの データ なし（{len(mo_d)}段）・動く 絵の 部品 {len(mo_f)}まいは アプリに 入れない・59段 ぜんぶ 止まった 絵と 前の 絵（35段）を 入れる・'
          f'絵 ぜんぶで {bsz / 1e6:.1f}MB（もとの 画質の まま。第4.149版は 軽く した 部品で 約14.0MB）')
    fxd = os.path.join(W, 'ios', 'fx_assets')
    if os.path.isdir(fxd) and all(os.path.exists(os.path.join(fxd, f)) for f in ASSET_FILES):
        sz = sum(os.path.getsize(os.path.join(fxd, f)) for f in ASSET_FILES)
        films_sz = sum(os.path.getsize(os.path.join(fxd, f)) for f in FILMS.values())
        gk_sz = os.path.getsize(os.path.join(fxd, 'gk_film.mp4'))
        check(38.5e6 < films_sz < 43.0e6 and 41.0e6 < sz < 45.5e6 and 8.0e6 < gk_sz < 11.2e6, f'絵と音と動画の 大きさ（もと）：動画 4本 約40.8MB（第4.162版：昇格の 動画を 外した・超神様の 新しい 動画の もとは CRF 20 で 17.6MB〈アプリに 入る 軽い 版は 10.9MB〉。前は 5本 約39.5MB・第4.77版：ノーマルど的中の 動画 約5.0MB・10.5秒／第4.117版：神様極的中の 動画 12秒：第4.136版 さいごの 字を 入れかえ・第4.137版 極の 雷で 約9.3MB）・ぜんぶで 約43.2MB（第4.162版：プレミアムど的中の 絵と なくした 演出の 音を 入れない。前は 約45.2MB・第4.86版：神様的中の 絵と 音 約2MB を 入れない）（{films_sz / 1e6:.1f}MB・{sz / 1e6:.1f}MB・神様極的中 {gk_sz / 1e6:.2f}MB）')
    # 第4.146版（まさちゃん 11/10 21:26「圧縮少しやわらか−45Mbの方でやって！」）：アプリに 入る のは 軽い 版（ios/lite/<名前>：kisekae/lite_assets.py・assets_dir.py）。
    #   動画 5本は CRF 24（第4.156版・まさちゃん 2026/11/12「的中の演出も大分画質落ちているから綺麗な状態にしてほしい！」「ほぼ見た目同じより、少し綺麗にしてみるのはどう？」：第4.155版までは CRF 29。
    #   さいごの 1まいに つながる 4本は さいごの 30コマ だけ CRF 23 → 22 → 21）・馬の 色／フィギュアと 棚の 色 は WebP quality 75。もと（ios/<名前>）は そのまま 残す（上の 大きさの 確かめは もとの もの）。
    #   でこぼこ（tc_n_*・fgN_n*）・つや（fgN_m*）は もとと 1バイトも ちがわない。台帳（lite.info）は アプリに 入れない
    #   第4.150版：結果ボードの 絵（止まった 絵 だけに なった）は 軽く しない＝もとと 1バイトも ちがわない（まさちゃん「その代わり、画質あげて！」）
    import assets_dir as _ad
    import hashlib as _hl
    _pb_on = any(f.startswith('pb_') and f.endswith('.webp') for f in res)      # 第4.148版：PUSHボタンの 絵（31まい・約3.2MB。第4.160版：ネオンを 外して 30まい・約3.1MB）が 入って いる とき
    if all(_ad.is_lite(n) for n in _ad.NAMES):
        RES = os.path.join(out, 'Tengel.swiftpm', 'Resources')
        _man = {n: _ad.manifest(n) for n in _ad.NAMES}
        _all = [(n, f, e) for n in _ad.NAMES for f, e in _man[n]['files'].items() if f in res]
        _sz = lambda fl: sum(os.path.getsize(os.path.join(RES, f)) for f in fl)
        _h = lambda pth: _hl.sha1(open(pth, 'rb').read()).hexdigest()
        p_films = _sz(FILMS.values()); p_bcp = _sz([f for f in res if f.startswith('bcp_')]); p_tcc = _sz([f for f in res if f.startswith('tc_c_')])
        p_fgc = _sz([f for f in res if re.fullmatch(r'fg\d+_cs?\.webp', f)]); p_shelf = _sz([f for f in res if re.fullmatch(r'fg_shelf2_c\d+\.webp', f)]); p_all = _sz(res)
        # 第4.151版（まさちゃん 11/11 09:07「ア、をお願い！」「棚の7個とも画質がかなり悪くなってるから、改善して！」）：
        #   番号が 32bit の 形（フィギュア 8体・神様馬・幻の馬）は 番号を 詰めた 入れもの（how＝idxz・もとに もどすと 1バイトも ちがわない）・棚の 絵 7まいは 劣化なしの WebP（how＝shelf・色は 6bit）→ 棚は 第4.153版で 貼り直した（下）
        import importlib as _il; sys.path.insert(0, os.path.join(W, 'kisekae')) if os.path.join(W, 'kisekae') not in sys.path else None; _la = _il.import_module('lite_assets')
        _iz = [(n, f, e) for n, f, e in _all if e['how'] == 'idxz']
        iz_ok = sorted(f for _n, f, _e in _iz) == sorted([f'fg{i}.bin' for i in range(1, 9)] + ['tc_horse_bk_kamisama2.bin', 'tc_horse_bk_maboroshi2.bin']) and all(
            open(os.path.join(RES, f), 'rb').read(4) == b'TGIZ' and _la.unpack_idx(open(os.path.join(RES, f), 'rb').read()) == open(os.path.join(_ad.master(n), f), 'rb').read() for n, f, _e in _iz)
        iz_save = sum(e['src'][0] - e['size'] for _n, _f, e in _iz)
        # 第4.153版（まさちゃん 11/11 12:10「やって！」＝棚の 貼り方を 作り直して 軽く）：棚は fg_shelf2.*（kisekae/fig/shelf_reuv.py）。前の fg_shelf.* は アプリに 入れない（もとの フォルダには 残す）
        #   絵 7まいは 劣化ありの WebP（2048²・もとと 1バイトも ちがわない＝軽い 版でも 作り直さない）・形は 16bit の 番号・貼り方（UV）は 0〜1・写真の 島（front）は 絵の 中
        def _sh2():
            from PIL import Image as _I
            import numpy as _np, json as _js
            names = [f'fg_shelf2_c{i}.webp' for i in range(1, 8)]
            if any(f not in res for f in names + ['fg_shelf2.json', 'fg_shelf2.bin']) or any(re.fullmatch(r'fg_shelf(\.json|\.bin|_c\d+\.webp)', f) for f in res): return False, 0, 0
            m = _js.load(open(os.path.join(RES, 'fg_shelf2.json'))); raw = open(os.path.join(RES, 'fg_shelf2.bin'), 'rb').read(); L = m['layout']
            uv = _np.frombuffer(raw, _np.uint16, m['v'] * 2, L['uv'][0]); idx = _np.frombuffer(raw, _np.uint16, m['i'], L['idx'][0]); fr = m['front']
            ok = m['tex'] == names and not m['idx32'] and m['v'] < 65536 and m['i'] == 72000 and L['idx'][0] + L['idx'][1] == len(raw) and int(idx.max()) == m['v'] - 1 and 0 <= fr[0] < fr[2] <= 2048 and 0 <= fr[1] < fr[3] <= 2048 and fr[2] - fr[0] > 900 and fr[3] - fr[1] > 1200
            for f in names:
                pth = os.path.join(RES, f); im = _I.open(pth); hd = open(pth, 'rb').read(40)
                ok = ok and im.size == (2048, 2048) and hd.find(b'VP8 ') >= 0 and hd.find(b'VP8L') < 0 and _h(pth) == _h(os.path.join(_ad.master('fig_assets'), f))
            return bool(ok), m['v'], os.path.getsize(os.path.join(RES, 'fg_shelf2.bin'))
        sh_ok, sh_v, sh_bin = _sh2()
        same_sz = all(os.path.getsize(os.path.join(RES, f)) == e['size'] for _n, f, e in _all)
        keep_fl = [(n, f) for n, f, e in _all if re.fullmatch(r'tc_n_.+\.webp|fg\d+_(n|ns|m|ms)\.webp|bcp_.+\.webp', f)]
        keep_ok = len(keep_fl) == 7 + 32 + 108 and all(e['how'] == 'copy' for n, f, e in _all if (n, f) in keep_fl) and all(_h(os.path.join(RES, f)) == _h(os.path.join(_ad.master(n), f)) for n, f in keep_fl)
        how = {}
        for _n, f, e in _all: how[e['how']] = how.get(e['how'], 0) + 1
        src_ok = all(os.path.getsize(os.path.join(_ad.master(n), f)) == e['src'][0] for n, f, e in _all)      # もとは そのまま（大きさが 台帳と 同じ）
        check(25.5e6 < p_films < 28.0e6 and 16.2e6 < p_bcp < 17.3e6 and 7.0e6 < p_tcc < 8.2e6 and 5.3e6 < p_fgc < 6.3e6 and 2.4e6 < p_shelf < 3.3e6 and 0.25e6 < sh_bin < 0.4e6 and iz_ok and 5.7e6 < iz_save < 6.5e6 and sh_ok and ((144e6 < p_all < 153e6) if _pb_on else (141e6 < p_all < 150e6)) and same_sz and keep_ok and src_ok
              and how.get('film') == 4 and how.get('webp', 0) + how.get('keep', 0) == 43 and how.get('idxz') == 10 and how.get('shelf', 0) == 0 and _ad.INFO not in res and all(_man[n]['params'] == {'crf': 24, 'preset': 'slow', 'tail': [[30, 23], [20, 22], [10, 21]], 'q': 75, 'method': 6, 'keep': 0.97} for n in _ad.NAMES)
              and all(_man['fx_assets']['files'][f]['p'].startswith('crf24-slow') for f in FILMS.values()),
              f'第4.146版：アプリに 入る のは 軽い 版（動画 4本 {p_films / 1e6:.1f}MB：もとは 40.8MB〈第4.162版：昇格の 動画を 外して 4本・超神様の 新しい 動画は 前と 同じ 10.9MB。前は 5本 31.0MB／第4.156版：CRF 29 → 24 に 上げた。第4.155版までは 18.5MB〉・結果ボードの 絵 {p_bcp / 1e6:.1f}MB：第4.150版から 止まった 絵を もとの 画質で・馬の 色 {p_tcc / 1e6:.1f}MB：前は 15.0MB・'
              f'フィギュアの 色 {p_fgc / 1e6:.1f}MB・棚の 絵 7まい {p_shelf / 1e6:.1f}MB（第4.153版：貼り直した 形 fg_shelf2・頂点 {sh_v}・前の 棚 fg_shelf.* は 入れない／第4.151版は 劣化なし 6bit で 8.9MB）・形の 番号を 詰めて −{iz_save / 1e6:.2f}MB（10こ・もどすと もとと 同じ）・中身 ぜんぶで {p_all / 1e6:.1f}MB：前は 191.6MB → 148.1MB → 第4.147版で 壁紙を 10枚 外して 約143MB → 第4.148版で PUSHボタンの 絵 31まいを 入れて 約145MB）→ 第4.150版で 結果ボードの 絵を もとの 画質に して 約148MB → 第4.153版で 棚を 貼り直して 約143MB → …… → 第4.162版で プレミアムど的中・超プレミアム神様的中の 絵と 音と 昇格の 動画を 外して 約149MB）・でこぼこ／つや／結果ボードの 絵（{len(keep_fl)}こ）は もとと 同じ・台帳は 入れない（{how}）')
        # 第4.161版（まさちゃん 11/12 18:00「神様馬、赤丸の位置から動く変なパーツが飛び出てる／幻の馬は…立髪の毛の色がブラック…身体の表面…ボヤけて…全て改善して！」・19:47「幻の馬、肩幅狭くして！」）：
        #   神様馬・幻の馬の 形は 直した 新しい 形（tc_horse_bk_<名前>2.json＋.bin：kisekae/tc/horse_fix.py）。前の 形は アプリに 入れない（もとの フォルダには 残す）
        import json as _j161
        _hn = [f'tc_horse_bk_{h}2.{e}' for h in ('kamisama', 'maboroshi') for e in ('json', 'bin')]; _ho = [f'tc_horse_bk_{h}.{e}' for h in ('kamisama', 'maboroshi') for e in ('json', 'bin')]
        _mm = _j161.load(open(os.path.join(RES, 'tc_horse_bk_maboroshi2.json'), encoding='utf8')) if 'tc_horse_bk_maboroshi2.json' in res else {}
        _km = _j161.load(open(os.path.join(RES, 'tc_horse_bk_kamisama2.json'), encoding='utf8')) if 'tc_horse_bk_kamisama2.json' in res else {}
        _tb = open(os.path.join(RES, 'tc_bundle.js'), encoding='utf8').read() if 'tc_bundle.js' in res else ''
        check(all(f in res for f in _hn) and not any(f in res for f in _ho) and all(os.path.isfile(os.path.join(_ad.master('tc_assets'), f)) for f in _ho)
              and (_mm.get('fix') or {}).get('two') == 1 and (_mm.get('fix') or {}).get('nfix') == 1 and 'fx' in _mm.get('layout', {}) and abs(((_mm.get('slim') or {}).get('w') or [0, 0])[1] - 0.62) < 0.003
              and (_km.get('skinfix2') or {}).get('verts') == 983 and 'fx' not in _km.get('layout', {}) and 'fix' not in _km
              and "tc_horse_bk_kamisama2'" in _tb and "tc_horse_bk_maboroshi2'" in _tb and "tc_horse_bk_kamisama'" not in _tb and "tc_horse_bk_maboroshi'" not in _tb and 'uniform vec3 uFix;' in _tb,
              f'第4.161版：神様馬・幻の馬は 直した 形（…2.json＋.bin）が 入って いる・前の 形 4つは 入って いない（もとの フォルダには ある）・幻の馬＝たてがみの 面と 法線の 直し・にじむ 膜の 色・肩幅 {((_mm.get("slim") or {}).get("w") or [0, 0])[0]} → {((_mm.get("slim") or {}).get("w") or [0, 0])[1]}／'
              f'神様馬＝マントの 先の 骨（{(_km.get("skinfix2") or {}).get("verts")}頂点）・アプリの コードは 新しい 名前を 読む')
        # 第4.153版（まさちゃん 11/11 13:59「出世馬の結果ボードカスタム3Dに絵を入れ替えて！」・14:23「ボードは何も書いていないように編集して！」）：
        #   出世馬の 7段は 3D の 絵（bcp_shusseN_3d.webp：kisekae/bcp/shusse3d.py）。ボードの 中は 何も 書いて いない（まん中が ほぼ 1色）・板の 四すみと 字の 置き方は 前の 絵と 同じ・前の 絵（bcp_shusseN.webp）は アプリに 入れない（もとの フォルダには 残す）
        sys.path.insert(0, os.path.join(W, 'kisekae', 'bcp')) if os.path.join(W, 'kisekae', 'bcp') not in sys.path else None
        import bcp_app as _B3
        def _sh3():
            from PIL import Image as _I
            import numpy as _np
            out = []
            for n in (1, 2, 3, 4, 8, 16, 24):
                f = f'bcp_shusse{n}_3d.webp'
                if f not in res or f'bcp_shusse{n}.webp' in res or not os.path.isfile(os.path.join(_ad.master('bcp_assets'), f'bcp_shusse{n}.webp')): return None
                d3, d0 = _B3.design(f'shusse{n}_3d'), _B3.design(f'shusse{n}')
                im = _I.open(os.path.join(RES, f)); a = _np.asarray(im.convert('RGB'), _np.float32); q = _np.array(d3['q']) * 3
                x0, y0, x1, y1 = q[:, 0].min(), q[:, 1].min(), q[:, 0].max(), q[:, 1].max()
                c = a[int(y0 + (y1 - y0) * 0.14):int(y1 - (y1 - y0) * 0.14), int(x0 + (x1 - x0) * 0.18):int(x1 - (x1 - x0) * 0.18)].mean(2)
                old = _np.asarray(_I.open(os.path.join(_ad.master('bcp_assets'), f'bcp_shusse{n}.webp')).convert('RGB'), _np.float32)
                out.append((im.size == (1170, 2532), d3['q'] == d0['q'] and d3['hp'] == d0['hp'] and d3['L'] == d0['L'], float(c.std()), float(_np.percentile(c, 99.9)), float(_np.abs(a - old).mean())))
            return out
        s3 = _sh3()
        check(s3 is not None and all(o[0] and o[1] and o[2] < 8 and o[3] < 75 and o[4] > 4 for o in s3) and 'bcp_t_climb_b.webp' in res and 'bcp_t_climb.webp' not in res and 'bcp_t_climb3d.webp' not in res,
              f'第4.153版：出世馬の 7段は 3D の 絵（1170×2532・板の 四すみと 字の 置き方は 前と 同じ）・ボードの 中は 何も 書いて いない（まん中の 明るさの ばらつき {max(o[2] for o in s3) if s3 else -1:.1f}・いちばん 明るい 所 {max(o[3] for o in s3) if s3 else -1:.0f}/255）・前の 絵と 見本は 入れない・見本は bcp_t_climb_b.webp')
        # 第4.153版（まさちゃん 11/11 15:39「他の結果ボードカスタムのボードも、綺麗に何も書いていないようにして！的中スタンプボードの…的中スタンプは消さなくていいよ！」）：
        #   出世馬の ほかの 52段は ボードの 中を ぬり直した 絵（bcp_<デザイン>_bl.webp：kisekae/bcp/bcp_blank.py）。前の 絵（bcp_<デザイン>.webp）は アプリに 入れない（もとの フォルダには 残す）。
        #   板の 紺の 所の「なめらかな 面からの ずれ」の ばらつきが 前より 小さい（52まい ぜんぶ）・パネルの 段だけ だった 板（廻る・祝杯・馬レース・トロフィー・馬が運ぶ・花束・結果待ち）は ほぼ 1色。
        #   スタンプ：鎖の 帯に 色の 点が ない・ハンコの 所は 前の 絵と 同じ。前の 絵（キャラ）の 所は 1点も かわらない
        def _bl():
            from PIL import Image as _I
            import numpy as _np, cv2 as _cv
            MD_ = _ad.master('bcp_assets'); rat = []; simple = []; fgd = 0; chain = []; stampd = []
            def _q(n):
                q = _np.array(_B3.design(n)['q'], _np.float64) * 3; m = _np.zeros((2532, 1170), _np.uint8); _cv.fillConvexPoly(m, _np.round(q).astype(_np.int32), 1); return q, m
            def _std(P, core):
                R_, G_, B_ = P[..., 0], P[..., 1], P[..., 2]; nv = core & (B_ > R_ + 10) & (B_ >= G_ + 2) & (P.max(2) < 150); ys, xs = _np.nonzero(nv)
                u = (xs - xs.mean()) / _np.ptp(xs); v = (ys - ys.mean()) / _np.ptp(ys); Bm = _np.stack([_np.ones_like(u), u, v, u * u, v * v, u * v], 1); col = P[ys, xs].astype(_np.float64)
                return float((col - Bm @ _np.linalg.lstsq(Bm, col, rcond=None)[0]).std())
            for _i, _k, st in _B3.ITEMS:
                for _c, n in st:
                    if not _B3.blank(n): continue
                    f = f'bcp_{n}_bl.webp'
                    if f not in res or f'bcp_{n}.webp' in res or not os.path.isfile(os.path.join(MD_, f'bcp_{n}.webp')): return None
                    im = _I.open(os.path.join(RES, f))
                    if im.size != (1170, 2532): return None
                    a = _np.asarray(im.convert('RGB'), _np.float32); o = _np.asarray(_I.open(os.path.join(MD_, f'bcp_{n}.webp')).convert('RGB'), _np.float32); q, m = _q(n)
                    core = _cv.erode(m, _cv.getStructuringElement(_cv.MORPH_ELLIPSE, (121, 121))) > 0; sn, so_ = _std(a, core), _std(o, core); rat.append(sn / so_)
                    if n.startswith(('ring', 'toast', 'race', 'trophy', 'carry', 'bouquet', 'miss4')): simple.append(sn)
                    fgp = os.path.join(MD_, f'bcp_{n}_fg.webp')
                    if _B3.cfg(n).get('fg') and os.path.isfile(fgp):       # 前の 絵（キャラ）の 所は ぬり直さない（色の 差は 圧縮し直した 分 だけ）
                        fa = _np.asarray(_I.open(fgp).convert('RGBA'))[..., 3] > 200; fgd = max(fgd, float(_np.abs(a - o).max(2)[fa].mean()))
                    if n.startswith('stamp'):
                        f_ = lambda u, v: (q[0] * (1 - u) + q[1] * u) * (1 - v) + (q[3] * (1 - u) + q[2] * u) * v
                        def _box(u0, v0, u1, v1):
                            b = _np.zeros((2532, 1170), _np.uint8); _cv.fillConvexPoly(b, _np.round(_np.array([f_(u0, v0), f_(u1, v0), f_(u1, v1), f_(u0, v1)])).astype(_np.int32), 1); return b > 0
                        cb = _box(0.5, 0.385, 0.95, 0.435); sat = lambda P: float(((P.max(2) - P.min(2))[cb] > 90).mean()); chain.append((round(sat(o), 3), round(sat(a), 3)))      # 鎖の 帯（右の 半分）：色の こい 点の 割合
                        sb = _box(0.1, 0.05, 0.3, 0.3); stampd.append(float(_np.abs(a - o).max(2)[sb].mean()))                                                                      # ハンコの まん中
            return rat, simple, fgd, chain, stampd
        bl = _bl()
        check(bl is not None and len(bl[0]) == 52 and max(bl[0]) < 1.0 and sum(1 for r_ in bl[0] if r_ < 0.75) >= 40 and len(bl[1]) == 28 and max(bl[1]) < 1.8 and bl[2] < 6.0
              and len(bl[3]) == 4 and all(o_ > 0.05 and a_ < 0.004 for o_, a_ in bl[3]) and max(bl[4]) < 7.0,      # 色の 差 6・7 まで＝圧縮し直した 分（ぬり直したら 20 より 大きい）
              f'第4.153版：ほかの 52段は ボードの 中を ぬり直した 絵（bcp_<デザイン>_bl.webp・前の 絵は 入れない）・板の ずれの ばらつきは 前の {min(bl[0]) if bl else 0:.2f}〜{max(bl[0]) if bl else 0:.2f}倍（0.75倍より 小さい もの {sum(1 for r_ in bl[0] if r_ < 0.75) if bl else 0}/52）・'
              f'パネルの 段だけ だった 板 28まいは ほぼ 1色（ばらつき {max(bl[1]) if bl else -1:.2f} まで）・前の 絵（キャラ）の 所は かわらない（色の 差 {bl[2] if bl else -1:.2f}）・スタンプ：鎖が ない（色の こい 点 前 → 今：{bl[3] if bl else None}）・ハンコは そのまま（色の 差 {max(bl[4]) if bl else -1:.2f}）')
        # 第4.152版（まさちゃん 11/11 09:43・10:13）：おそうじの 絵と 形（ゴミの 絵 4まい・3D の ほうき・3D の ちりとり：kisekae/tc/clean_assets.py）
        _cl = ['tc_trash1.webp', 'tc_trash2.webp', 'tc_trash3.webp', 'tc_trash4.webp', 'tc_prop_broom.json', 'tc_prop_broom.bin', 'tc_prop_broom_c.webp', 'tc_prop_broom_n.webp', 'tc_prop_pan.json', 'tc_prop_pan.bin', 'tc_prop_pan_c.webp']
        import json as _jc
        _mb = _jc.load(open(os.path.join(RES, 'tc_prop_broom.json'))) if 'tc_prop_broom.json' in res else {}; _mp = _jc.load(open(os.path.join(RES, 'tc_prop_pan.json'))) if 'tc_prop_pan.json' in res else {}
        check(all(f in res for f in _cl) and 0.4e6 < _sz(_cl) < 0.8e6 and _mb.get('fmt') == 2 and _mb.get('i') == 21000 and _mb.get('ntex') == 'tc_prop_broom_n.webp' and _mp.get('fmt') == 2 and _mp.get('i') == 6888 and not _mp.get('ntex')
              and all(_h(os.path.join(RES, f)) == _h(os.path.join(_ad.master('tc_assets'), f)) for f in _cl if f in res),
              f'第4.152版：おそうじの 絵と 形（ゴミの 絵 4まい・3D の ほうき 7000三角・ちりとり 2296三角）が Resources に 入る（11こ・{_sz([f for f in _cl if f in res]) / 1e3:.0f}KB・もとと 同じ 中身）')
        # 第4.156版（まさちゃん 2026/11/12 04:20「トレーニングセンターの馬の寝転ぶ演出は全部消して！」「いないデータの削除」）：
        #   トレーニングセンターの 音は、コードが 鳴らす もの と Resources に 入って いる もの が ぴったり 同じ（足りない 音も、鳴らさない 音も ない）。
        #   入れない 5つ：横に なる 動きの 音 3つ（flop・goron・lie）・鳴らして いなかった hop・piron と 中身が 同じ unlock。もとの フォルダには 残す
        _care = open(os.path.join(W, 'tc', 'tc_care.js'), encoding='utf8').read(); _tapp = open(os.path.join(W, 'tc', 'tc_app.js'), encoding='utf8').read()
        _tall = ''.join(open(os.path.join(W, 'tc', f), encoding='utf8').read() for f in sorted(os.listdir(os.path.join(W, 'tc'))) if f.endswith('.js'))
        _evs = set(re.findall(r"\bev\([^;]{0,60}?,\s*'([a-z0-9_]+)'", _care))
        _zr = re.search(r"const ZR = \{([^}]*)\}", _care); _evs |= set(re.findall(r"\['([a-z]+)',", _zr.group(1))) if _zr else set(); _evs.add('tilt')      # 撫でた 場所ごとの 反応（ev(tt, rk)）
        _skip = dict((k, v) for k, v, _q in re.findall(r"(\w+): (null|'(\w+)')", re.search(r"const SE_SKIP = \{([^}]*)\}", _tapp).group(1)))
        _want = set(re.findall(r"tc_se_([a-z0-9_]+)\.m4a", _tall))
        for _e in _evs:
            if _e == 'slot': _want |= {f'slot_{i}' for i in range(1, 11)}
            elif _e == 'bite': _want |= {'bite_apple', 'bite_carrot'}
            elif _e == 'banin': _want |= {'banin_maboroshi', 'banin_kamisama'}
            elif _e in _skip:
                if _skip[_e] != 'null': _want.add(_skip[_e].strip("'"))
            else: _want.add(_e)
        _got = {f[6:-4] for f in res if f.startswith('tc_se_') and f.endswith('.m4a')}
        _gone = ['flop', 'goron', 'lie', 'hop', 'unlock']
        check(_got == _want and len(_got) == 73 and not any(g in _got for g in _gone) and all(os.path.exists(os.path.join(_ad.master('tc_assets'), f'tc_se_{g}.m4a')) for g in _gone)
              and _skip.get('unlock') == "'piron'" and _skip.get('callcool') == 'null' and sorted(_ad.TC_GONE) == sorted(f'tc_se_{g}.m4a' for g in _gone)
              and open(os.path.join(_ad.master('tc_assets'), 'tc_se_unlock.m4a'), 'rb').read() == open(os.path.join(RES, 'tc_se_piron.m4a'), 'rb').read()
              and not re.search(r"mode: 'sleep'|ev\(tt, '(flop|goron|lie)'\)|TEST\.wake|wake\(\)", _tall) and 'ごろん' not in open(os.path.join(RES, 'tc_bundle.js'), encoding='utf8').read(),
              f'第4.156版：トレーニングセンターの 音は 鳴らす もの と 入って いる もの が 同じ（{len(_got)}こ〈第4.159版：＋4＝プフォ・デデーン・キュインキュイーン・ドーン／−1＝ルーレットの 前の 確定の 音〉・足りない {sorted(_want - _got)}・あまり {sorted(_got - _want)}）・'
              f'横に なる 動きの 音（flop・goron・lie）と 使わない 音（hop・unlock＝piron と 同じ 中身）は 入れない（もとの フォルダには 残る）・馬を 横に する コードと「ごろん」の 字は ない')
        # 第4.158版（まさちゃん 2026/11/12 08:59「このルーレットの神様馬、目が怖いから金色に光らせて！あと、画像がなんかまだらに色がついてるから綺麗にできる？」・09:00「幻の馬のルーレットは、目を紫に光らせて！」）：
        #   ルーレットの 絵は きれいに した 新しい 絵 12まい（rt_<絵>_<部品>2.webp：kisekae/tc/rt_clean.py）。前の 12まい（rt_<絵>_<部品>.webp）は 入れない（もとの フォルダには 残す）
        _rtn = [f'rt_{t}_{q}2.webp' for t in ('normal', 'maboroshi', 'kamisama') for q in ('plate', 'knob', 'stick', 'ptr')]; _rto = [f[:-6] + '.webp' for f in _rtn]
        _tb = open(os.path.join(RES, 'tc_bundle.js'), encoding='utf8').read()
        check(all(f in res for f in _rtn) and not any(f in res for f in _rto) and all(os.path.exists(os.path.join(_ad.master('tc_assets'), f)) for f in _rto)
              and all(_h(os.path.join(RES, f)) == _h(os.path.join(_ad.master('tc_assets'), f)) for f in _rtn if f in res) and bool(re.search(r'img\(`rt_\$\{\w+\}_\$\{\w+\}2\.webp`\)\s*\|\|\s*await img\(`rt_\$\{\w+\}_\$\{\w+\}\.webp`\)', _tb))
              and 0.5e6 < _sz([f for f in _rtn if f in res]) < 0.8e6,
              f'第4.158版：ルーレットの 絵は きれいに した 新しい 12まい（rt_<絵>_<部品>2.webp・{_sz([f for f in _rtn if f in res]) / 1e3:.0f}KB・もとと 同じ 中身）・前の 12まいは 入って いない（もとの フォルダには 残る）・コードは 新しい 名前を 先に 読む（ない とき だけ 前の 名前）')
        # 第4.159版（まさちゃん 2026/11/12 10:37「お世話が終わったあとに、pushボタンが出てくるようにして(pushボタンは俺が準備する)」・11:56「プチュンは、極ど的中と超プレミアム神様的中で使用してたプチュンの演出入れてね！」）：
        #   PUSH の 絵は 赤い ボタン（cap）と 黒い 台（base）の 2まい（kisekae/tc/push_asset.py）。はじめに 作った 1まい（tc_push.webp）は 入れない（もとの フォルダには 残す）。
        #   音：プフォ・デデーン・キュインキュイーン（トレーニングセンターの 音）＋ 的中の 演出の 音 2つ（プチュン sfx_sdp・デカ的中 sfx_big：もう 入って いる もの を 使う）。
        #   プチュンは 的中の 演出の 束（window.__FX の reveal.sd）の 中の 部品（.pc）を とり出して 使う ＝ 束の 中に 1つ ある こと
        _pu = ['tc_push_cap.webp', 'tc_push_base.webp']; _ps = ['tc_se_pfo.m4a', 'tc_se_dedeen.m4a', 'tc_se_kyuin.m4a']
        from PIL import Image as _PI
        _pz = [_PI.open(os.path.join(RES, f)).size for f in _pu if f in res]
        _ix = open(os.path.join(RES, 'index.html'), encoding='utf8').read()
        check(all(f in res for f in _pu + _ps) and 'tc_push.webp' not in res and os.path.exists(os.path.join(_ad.master('tc_assets'), 'tc_push.webp'))
              and all(_h(os.path.join(RES, f)) == _h(os.path.join(_ad.master('tc_assets'), f)) for f in _pu + _ps if f in res) and len(set(_pz)) == 1 and _pz and _pz[0][0] == 660
              and 40e3 < _sz([f for f in _pu if f in res]) < 120e3 and 30e3 < _sz([f for f in _ps if f in res]) < 90e3
              and 'sfx_sdp.m4a' in res and 'sfx_big.m4a' in res and "'tc_push_cap.webp'" in _tb and "'tc_push_base.webp'" in _tb and 'tc_push.webp' not in _tb
              and 'pcOpen' in _tb and "querySelector('.pc')" in _tb and 'puchun: true' in _tb and _ix.count('<div class=\\"pc\\"') + _ix.count('<div class="pc"') == 1,
              f'第4.159版：お世話の あとの PUSH の 絵 2まい（赤い ボタン・黒い 台：{_pz[0] if _pz else None}・{_sz([f for f in _pu if f in res]) / 1e3:.0f}KB）と 音 3つ（{_sz([f for f in _ps if f in res]) / 1e3:.0f}KB）が 入る（もとと 同じ 中身）・'
              f'はじめの 1まい（tc_push.webp）は 入らない・プチュンと デカ的中の 音は 的中の 演出の もの（sfx_sdp・sfx_big）・プチュンの 部品（.pc）は 的中の 演出の 束に 1つ（それを 使う）')
        # 第4.159版（まさちゃん 11/12 13:27「ルーレット高い方が当たった時に…光輝きながら獲得ポイントを表示するようにして！一枚目がテロップの画像！」・13:30「ドーン！！みたいな音と一緒にテロップ出して！」）：
        #   テロップ「大量ポイント」の 絵（tc_telop_big.webp：kisekae/tc/telop_asset.py・まわりの うすい もやは 消して ある）と ドーン！！の 音（tc_se_doon.m4a）が 入る。
        #   前の 確定の 音（tc_se_rt_confirm.m4a）は もう 鳴らさない ので 入れない（もとの フォルダには 残す）
        import numpy as _np2, cv2 as _cv2
        _szs = lambda fl: _sz([f for f in fl if f in res])
        _tp = 'tc_telop_big.webp'; _ti = _PI.open(os.path.join(RES, _tp)).convert('RGBA') if _tp in res else None
        _ta = _np2.array(_ti)[..., 3] if _ti else _np2.zeros((1, 1), _np2.uint8)
        _far = int(((_ta > 0) & ~(_cv2.dilate((_ta >= 200).astype(_np2.uint8), _np2.ones((17, 17), _np2.uint8)) > 0)).sum())      # はっきり した 所から 8px より 遠い のに すき通って いない 画素（うすい もや）
        check(_tp in res and 'tc_se_doon.m4a' in res and 'tc_se_rt_confirm.m4a' not in res and os.path.exists(os.path.join(_ad.master('tc_assets'), 'tc_se_rt_confirm.m4a'))
              and all(_h(os.path.join(RES, f)) == _h(os.path.join(_ad.master('tc_assets'), f)) for f in (_tp, 'tc_se_doon.m4a') if f in res) and _ti is not None and _ti.size == (1110, 742) and _far == 0 and int((_ta >= 200).sum()) > 500000
              and 100e3 < _szs([_tp]) < 260e3 and 15e3 < _szs(['tc_se_doon.m4a']) < 60e3 and "'tc_telop_big.webp'" in _tb and "'tc_se_doon.m4a'" in _tb and 'rt_confirm' not in _tb and 'drawBig' in _tb and 'lotStock: 20' in _tb,
              f'第4.159版：テロップ「大量ポイント」の 絵（{_ti.size if _ti else None}・{_szs([_tp]) / 1e3:.0f}KB・まわりの うすい もや {_far}画素）と ドーン！！の 音（{_szs(["tc_se_doon.m4a"]) / 1e3:.0f}KB）が 入る（もとと 同じ 中身）・'
              f'前の 確定の 音（tc_se_rt_confirm.m4a）は 入らない（もとの フォルダには 残る・コードも 鳴らさない）・ハートの 抽選は トークン 20こ未満の とき だけ（lotStock）')
    else:
        print('  ※ 軽い 版（ios/lite）が ない ので、その 確かめは しない（CI・LITE=0）')
    # assets_dir の きまり（にせの フォルダで）：軽い 版が ない → もと／新しい → 軽い 版／LITE=0 → もと／もとに ファイルが ふえた・もとが かわった・軽い 版が 欠けた → 古い（adir は 止まって lite_assets.py を 教える）
    import json as _j2
    _tmp = tempfile.mkdtemp(); _W0 = _ad.W; _P0 = os.environ.pop('LITE', None)
    try:
        _ad.W = _tmp; _m = _ad.master('tc_assets'); _p = _ad.lite('tc_assets'); os.makedirs(_m)
        for f, bts in (('a.webp', b'12345'), ('b.bin', b'xyz')): open(os.path.join(_m, f), 'wb').write(bts)
        r0 = (_ad.stale('tc_assets') is None, _ad.adir('tc_assets') == _m, _ad.is_lite('tc_assets'))
        os.makedirs(_p); _mn = {'v': 1, 'params': {}, 'files': {}}
        for f in ('a.webp', 'b.bin'):
            _st = os.stat(os.path.join(_m, f)); open(os.path.join(_p, f), 'wb').write(b'pk'); _mn['files'][f] = {'how': 'copy', 'src': [_st.st_size, _st.st_mtime_ns, ''], 'size': 2}
        _j2.dump(_mn, open(os.path.join(_p, _ad.INFO), 'w'))
        r1 = (_ad.stale('tc_assets') == '', _ad.adir('tc_assets') == _p, _ad.is_lite('tc_assets'))
        os.environ['LITE'] = '0'; r2 = (_ad.adir('tc_assets') == _m, _ad.is_lite('tc_assets')); del os.environ['LITE']
        open(os.path.join(_m, 'c.m4a'), 'wb').write(b'new'); r3 = _ad.stale('tc_assets'); os.remove(os.path.join(_m, 'c.m4a'))
        os.remove(os.path.join(_p, 'b.bin')); r4 = _ad.stale('tc_assets'); open(os.path.join(_p, 'b.bin'), 'wb').write(b'pk')
        r4b = _ad.stale('tc_assets') == ''
        open(os.path.join(_m, 'a.webp'), 'wb').write(b'123456'); r5 = _ad.stale('tc_assets')
        try:
            _ad.adir('tc_assets'); r6 = False
        except SystemExit as e:
            r6 = '古い' in str(e) and 'lite_assets.py' in str(e) and 'LITE=0' in str(e)
        check(r0 == (True, True, False) and r1 == (True, True, True) and r2 == (True, False) and 'ならびが かわった' in r3 and '軽い 版が ない' in r4 and r4b and 'もとが かわった' in r5 and r6,
              f'第4.146版：assets_dir：軽い 版が ない → もと・新しい → 軽い 版・LITE=0 → もと・ファイルが ふえた／軽い 版が 欠けた／もとが かわった → 古い（ビルドと テストは 止まって 作り直しを 教える）（{r0}・{r1}・{r2}・{r3}・{r4}・{r5}・{r6}）')
    finally:
        _ad.W = _W0; shutil.rmtree(_tmp, ignore_errors=True)
        if _P0 is not None: os.environ['LITE'] = _P0
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
    # 第4.156版（まさちゃん 2026/11/12 04:53「アプリ自体、iPadでもiPhoneと同じ大きさで表示されるようにして！」）：広い 画面（幅 480pt より 広い＝iPad の 画面いっぱいの 窓）では
    #   Webの 画面を iPhone の 大きさ（390×844）で まん中に 置く（まわりは 黒・時計の 帯は かくす）。iPhone（幅 440pt まで）と iPad の 細い 窓では 今までどおり 窓いっぱい。
    #   出す アプリは iPhone用の まま（Package.swift は .phone だけ：上で 確かめて いる）。本物の 動きは CI（iPad の シミュレーター・.pad を 足して 作った もの）で 見る
    ap2 = open(os.path.join(out, 'Tengel.swiftpm', 'TengelApp.swift'), encoding='utf8').read(); wvc = nocom(wv); apc = nocom(ap2)
    ci_run = open(os.path.join(W, 'ios', 'ci', 'run.sh'), encoding='utf8').read(); ci_st = open(os.path.join(W, 'ios', 'ci', 'selftest.js'), encoding='utf8').read()
    check('enum PhoneFrame' in wvc and 'static let size = CGSize(width: 390, height: 844)' in wvc and 'static let wideWidth: CGFloat = 480' in wvc and 'width > wideWidth' in wvc
          and 'var framed: Bool { PhoneFrame.isWide(bounds.width) }' in wvc and 'let frame = wide ? phoneRect() : bounds' in wvc and 'framed ? (0, 0) : overlap' in wvc
          and 'backgroundColor = wide ? .black : .tengelPage' in wvc and '"framed": framed' in wvc and '"webWidth": webView.frame.width' in wvc
          and 'WideBackdrop()' in apc and 'struct WideBackdrop: View' in apc and 'PhoneFrame.isWide(geo.size.width)' in apc and '.opacity(wide ? 1 : 0)' in apc and '.statusBarHidden(wide)' in apc
          and apc.index('Color(uiColor: .tengelPage)') < apc.index('WideBackdrop()') < apc.index('TengelWebView()') and 'TengelWebView()\n                .ignoresSafeArea(edges: .bottom)' in ap2,
          '第4.156版：広い 画面（iPad の 画面いっぱいの 窓）では アプリを iPhone の 大きさ（390×844）で まん中に（まわりは 黒・重なりの あきは 0）・iPhone（幅 480pt まで）は 今までどおり 窓いっぱい')
    check("supportedDeviceFamilies: [.pad, .phone]" in ci_run and 'phase "$IPAD" ipadwide 4 1000 wide-main report-4' in ci_run and 'L.get("framed") is True' in ci_run and 'b.get("w") == 390' in ci_run
          and 'async function phase4()' in ci_st and "PH === 4 ? phase4" in ci_st and "report('4', R)" in ci_st and "await mark('wide-main')" in ci_st
          and '.pad' not in open(os.path.join(out, 'Tengel.swiftpm', 'Package.swift'), encoding='utf8').read().split('supportedDeviceFamilies')[1].split(']')[0],
          '第4.156版：CI は .pad を 足して 作った もの（Swift Playgrounds の ▶ と 同じ 形）を iPad の シミュレーターで 動かして、Webの 画面が 390pt 幅に なるか 見る（出す アプリの Package.swift は .phone だけの まま）')
    check('window.__TEST=true;' not in html and 'テスト版の道具' in html and 'gift-test' in html, 'ふつうの 作り方：テスト版の 印（__TEST=true）は 入って いない（道具の コードは あるが 動かない）')
    gi = open(os.path.join(W, '.gitignore'), encoding='utf8').read()
    check('ios/fx_assets/' in gi and subprocess.run(['git', 'check-ignore', '-q', 'source/ios/fx_assets/sfx_fz_push.m4a'], cwd=os.path.dirname(W)).returncode == 0, '絵と音のフォルダ（ios/fx_assets/）は git に入らない（source/.gitignore）')
    # 第4弾：着せ替え（30テーマの変数と @font-face を束ねた __KS・kisekae.js・設定のカード・テーマごとの ks_<id>.json・しぼった字・見本の絵は手元の ios/kisekae_blobs/ から）
    import json as _json, re as _re
    ks_json = [f for f in res if _re.fullmatch(r'ks_[a-z]+\.json', f)]
    check('window.__KS=' in html and 'window.TengelKisekae' in html and "'tengel.kisekae'" in html and 'setKisekae' in html and 'html[data-ks=\\"sunset\\"]' in html and "@font-face{font-family:'Kaisei Opti'" in html and 'fonts/KaiseiOpti-700.woff2' in html,
          'アプリの画面に 着せ替え（__KS・kisekae.js・設定の「着せ替え」・テーマの変数・テーマの字の @font-face）が入っている（第4弾）')
    sys.path.insert(0, os.path.join(W, 'kisekae')); import pack as _pack
    n_ks = 19 + len(_pack.IDS)                                           # 第4.92版：壁紙パック・第4.109版：いつもの（default）の ks_default.json は 入れない（kisekae.js が 読まない）・第4.147版：壁紙を 10枚 外した（ポイント 26 → 17・壁紙パック 11 → 10）・第4.160版：ネオンを 外した（ポイント 17 → 16）
    check(len(ks_json) == n_ks and len(_pack.IDS) == 10 and all(f in res for f in ('ks_banner_ranch.svg', 'ks_banner_cute.svg', 'ks_banner_kids.svg', 'ks_banner_gold.svg')) and all(f'ks_{t}.json' in res for t in _pack.IDS),
          f'テーマごとの ks_<id>.json が {n_ks}こ（いつもの 以外の 19＝ポイント 16＋帯 3 ＋壁紙パック {len(_pack.IDS)}・ks_default.json は なし）と 定番4の止まった絵（{len(ks_json)}）')
    # 第4.147版（まさちゃん 2026/11/10 22:12「壁紙 ホワイトデー・バレンタインデー・ハロウィン・正月・クリスマス・雪・紅葉・桜・海 これら全部消して！」「七夕も消して！」）：
    #   外した 10枚は アプリに 入って いない（ks_<名前>.json・テーマの 変数・一覧・その 壁紙 だけの 絵と 字）。もとの 絵（ios/kisekae_blobs/）と 作る 道具（kisekae/）は そのまま 残す
    import build_kisekae as _bk
    GONE = list(_bk.REMOVED)
    _pjs = open(os.path.join(W, 'points.js'), encoding='utf8').read()
    gone_js = _re.findall(r"'([a-z]+)'", _re.search(r'var GONE_THEMES = \[([^\]]*)\];', _pjs).group(1))      # points.js の 外した 壁紙（解放して いた 人に ポイントを 返す 表）と 同じ
    ksd = _json.JSONDecoder().raw_decode(html, html.index('window.__KS=') + len('window.__KS='))[0]
    gone_blobs = {v for t in GONE if t in _bk.BLOBS20 for v in [_bk.BLOBS20[t]]} | {v['id'] for v in _pack.blobs('tanabata').values()}
    keep_blobs = {_bk.BLOBS20[t] for t in _bk.BLOBS20 if t in _bk.BY_ID} | {v['id'] for t in _pack.IDS for v in _pack.blobs(t).values()}
    check(len(GONE) == 11 and GONE[-1] == 'neon' and GONE == gone_js and not any(f'ks_{t}.json' in res for t in GONE) and not any(f'html[data-ks=\\"{t}\\"]' in html for t in GONE)
          and len(ksd['themes']) == 30 and not any(t['id'] in GONE for t in ksd['themes']) and len(ksd['paid']) == 16 and not (set(ksd['paid']) & set(GONE))
          and ksd['pack']['ids'] == ksd['pack']['order'] == ['pirate', 'course', 'space', 'paddock', 'deepsea', 'dino', 'kirie', 'ukiyoe', 'steam', 'future'] and ksd['pack']['every'] == 5
          and "var WALLPACK = { product: 'jp.tengel.app.wallpack1', every: 5, n: 10 };" in _pjs and 'var WALL_TOTAL = 29;' in _pjs and ksd['band'] == {'silver': 5, 'golden': 10, 'tengel': 15}
          and sorted(t['price'] for t in ksd['themes'] if t.get('price')) == [2000] * 6 + [3000] * 3 + [4000] * 4 + [7000] * 3
          and not any(('ks_' + b + '.webp') in res or ('ks_' + b + '.svg') in res for b in gone_blobs - keep_blobs)
          and not any(f in res for f in ('KaiseiDecol-700.woff2', 'YujiSyuku-400.woff2', 'YuseiMagic-400.woff2', 'ReggaeOne-400.woff2', 'Murecho-800.woff2', 'ZenOldMincho-900.woff2')),
          f'第4.147版・第4.160版：外した 壁紙 11枚（{"・".join(GONE)}）は アプリに 入って いない（ks_<名前>.json・テーマの 変数・一覧・その 壁紙 だけの 絵と 字）・のこりは 30テーマ（ポイント 16枚＝2,000P×6・3,000P×3・4,000P×4・7,000P×3／壁紙パック 10枚／帯 5・10・15枚）')
    rsvg = open(os.path.join(out, 'Tengel.swiftpm', 'Resources', 'ks_banner_ranch.svg'), encoding='utf8').read(); gsvg = open(os.path.join(out, 'Tengel.swiftpm', 'Resources', 'ks_banner_gold.svg'), encoding='utf8').read()
    check('*{animation:none!important}</style>' in rsvg and '*{animation:none!important}</style>' in gsvg and '.kslive{' in html and '.kslv{' in html and 'rescope' in html and 'rbwSvg' in html and 'mask-type:alpha' in html,
          '第4.89版：選ぶ画面の 牧場・ぷりけつの 小さな絵は 止めた SVG・選んだ タイルだけ 動く 壁紙（.kslive）・形の ある PUSH の 虹は SVG の 中（rbwSvg・mask）')
    # 第4.147版：桜を 外した ので、同じ 確かめを 夕焼け（のこった「季節・行事」の 壁紙）で
    sk = _json.load(open(os.path.join(out, 'Tengel.swiftpm', 'Resources', 'ks_sunset.json'), encoding='utf8'))
    check(sk['bnr'] and '<div class="ssw"' in sk['bnr']['html'] and 'ks_5f93d2cbb5295e4148858bf5daf03c5a.webp' in sk['bnr']['html'] and '#ksBnr .ssw' in sk['bnr']['css'] and '@keyframes kb' in sk['bnr']['css'] and '/_blob/' not in _json.dumps(sk)
          and sk['push']['pc'] == 'ss' and ((sk['push']['svg'] == '' and sk['push']['pressed'] == '' and sk['push'].get('img') == 1) if 'pb_sunset.webp' in res else ('<svg' in sk['push']['svg'] and '<svg' in sk['push']['pressed'] and 'img' not in sk['push'])) and 'class="clips ss"' in sk['push']['burst'] and '.fxs .push.ss' in sk['push']['css'] and '.fxs .rb.t-sunset{' in sk['board']['css'] and '<svg class="orn"' in sk['board']['orn'],
          'ks_sunset.json：上の絵（#ksBnr の中だけ・@keyframes に kb）・夕焼けの PUSH（面：第4.148版から 絵が あれば コードの 面は 入れない・はじける 光・.fxs の中だけ）・ボードの変数と飾り・見本の絵の場所（/_blob/）が残っていない')
    # 第4.148版（まさちゃん 2026/11/10 20:36「（画像は1枚だけもらって、「光る・へこむ・はじける」はコードで動かす）これがいいかも！」→ 11/11 00:02・00:05・00:16 に 31まい＝テーマ 1つに 1まい・いつもの も）：
    #   PUSHボタンの 絵（ios/push_assets/pb_<id>.webp：kisekae/push_art.py が もとの 絵 src/<id>.png から 作る）は、手元に あれば 31まい（第4.160版：ネオンを 外して 30まい）ぜんぶ Resources に 入る。もとの 絵・台帳（pb.json）・PNG は 入れない。
    #   一覧（__KS の themes[].pa＝ファイルの 名前と 出す 大きさ）・テーマの ks_<id>.json（push.img＝1・コードの 面 svg／pressed は 入れない）。なければ 入れずに 作れる（今までの コードの PUSH：下の テスト版の 作り方で 確かめる）
    import push_art as _pa
    PB = _pa.files(); pb_res = sorted(f for f in res if f.startswith('pb_')); RES2 = os.path.join(out, 'Tengel.swiftpm', 'Resources')
    pa_ok = all((t.get('pa') == {'f': PB[t['id']]['f'], 'w': PB[t['id']]['w'], 'h': PB[t['id']]['h']}) if t['id'] in PB else ('pa' not in t) for t in ksd['themes'])
    kj = {t['id']: _json.load(open(os.path.join(RES2, f"ks_{t['id']}.json"), encoding='utf8')) for t in ksd['themes'] if t['id'] != 'default'}
    img_ok = all(((j['push'].get('img') == 1 and j['push']['svg'] == '' and j['push']['pressed'] == '' and j['push']['css'] != '') if tid in PB else ('img' not in j['push'] and '<svg' in j['push']['svg'])) for tid, j in kj.items() if j.get('push'))
    pb_sz = sum(os.path.getsize(os.path.join(RES2, f)) for f in pb_res)
    same_pb = all(open(os.path.join(RES2, e['f']), 'rb').read() == open(os.path.join(_pa.ROOT, e['f']), 'rb').read() for e in PB.values()) if PB else True
    check(len(PB) in (0, 30) and 'pb_neon.webp' not in res and pb_res == sorted(e['f'] for e in PB.values()) and (not PB or sorted(PB) == sorted(t['id'] for t in ksd['themes'])) and pa_ok and img_ok and same_pb and pb_sz < 4_000_000
          and 'pb.json' not in res and not any(f.lower().endswith('.png') for f in res) and 'pushArt' in html and '.push.pim' in html and 'fxpimGlow' in html
          and 'ios/push_assets/' in gi and subprocess.run(['git', 'check-ignore', '-q', 'source/ios/push_assets/pb_default.webp'], cwd=os.path.dirname(W)).returncode == 0
          and subprocess.run(['git', 'check-ignore', '-q', 'source/ios/push_assets/src/default.png'], cwd=os.path.dirname(W)).returncode == 0,
          f'第4.148版：PUSHボタンの 絵 {len(pb_res)}まい（{pb_sz / 1e6:.2f}MB・テーマ 30こ ぜんぶ＝いつもの も。第4.160版：ネオンの 絵は 入れない）が Resources に 入る・一覧に 絵の 名前と 出す 大きさ（pa）・テーマの ファイルは 面を 絵に（img＝1・コードの 面なし）・'
          f'もとの 絵／台帳／PNG は 入れない・絵の フォルダ（ios/push_assets/）は git に 入らない（手元に なければ 0まい＝今までの コードの PUSH）')
    # 第4.160版（まさちゃん 2026/11/12 14:31「壁紙のネオン消して！」）：ネオンは アプリに 入れない（テーマの ファイル・絵 3まい・PUSH の 絵・一覧）。もとの 絵は 手元に のこす（消さない）
    #   （第4.87版の ネオンの 光のつぶの 確かめ・第4.147版より 前の 雪の 白い 息の 確かめは、壁紙を 外した ので なし）
    _nb = list(_json.load(open(os.path.join(W, 'kisekae', 'neon_blobs.json'))).values()) + [_json.load(open(os.path.join(W, 'kisekae', 'blobs20.json')))['neon']]
    _bl = os.path.join(W, 'ios', 'kisekae_blobs')
    check('ks_neon.json' not in res and not any(f'ks_{b}.webp' in res for b in _nb) and len(_nb) == 3 and 'pb_neon.webp' not in res and not any(t['id'] == 'neon' for t in ksd['themes']) and len(ksd['themes']) == 30
          and 'neon' in _bk.REMOVED and ksd['band'] == dict(silver=5, golden=10, tengel=15) and len(ksd['paid']) == 16 and 'neon' not in ksd['paid']
          and (not os.path.isdir(_bl) or all(os.path.exists(os.path.join(_bl, b + '.webp')) for b in _nb))
          and (not os.path.isdir(_pa.IN) or (os.path.exists(os.path.join(_pa.IN, 'neon.png')) and os.path.exists(os.path.join(_pa.ROOT, 'pb_neon.webp')))),
          '第4.160版：ネオンは アプリに 入って いない（ks_neon.json・絵 3まい・PUSH の 絵・一覧＝30テーマ・ポイントの 壁紙 16枚・帯は 5・10・15枚）・もとの 絵は 手元に のこって いる')
    # 第4.160版（まさちゃん 2026/11/12 14:31「星座の馬、一枚目の写真の馬を使用して！」）：星座の 壁紙の 馬は まさちゃんの ペガサスの 絵（kisekae/flat/pegasus_art.py）
    #   下の 絵＝夜空・天の川・三日月 だけ（1170×480）・その 上に 流れる 星・ペガサスの 絵（すき通し・画面の 3倍）・キラキラ。一覧の 小さい 絵も 新しい ペガサス。前の 絵 2まいは 入れない（手元には のこす）
    _sb = _json.load(open(os.path.join(W, 'kisekae', 'stars_blobs.json'))); _sp = _json.load(open(os.path.join(W, 'kisekae', 'stars_pts.json')))
    _sj = _json.load(open(os.path.join(out, 'Tengel.swiftpm', 'Resources', 'ks_stars.json'), encoding='utf8')); _sh, _sc = _sj['bnr']['html'], _sj['bnr']['css']
    _st = _json.load(open(os.path.join(W, 'kisekae', 'blobs20.json')))['stars']; _sold = ['0bbb4fcd668d2b6b036a2e8fd08aa876', 'b0dbe73ee41b9865222b901ace7eb073']
    _pl, _pt, _pw, _ph = _sp['peg']
    from PIL import Image as _SI
    _ksi = [f for f in res if _re.fullmatch(r'ks_[0-9a-f]{32}\.(webp|svg)', f)]      # 着せ替えの 絵が 入って いる（手元に 絵が ある）とき だけ 絵を 見る
    check(sorted(_sb) == ['base', 'peg'] and f'<img class="bnr" src="ks_{_sb["base"]}.webp"' in _sh and f'<img class="szpg" src="ks_{_sb["peg"]}.webp" alt="">' in _sh
          and _sh.index('class="szs"') < _sh.index('class="szpg"') < _sh.index('class="szx"') and f'.szw .szpg{{position:absolute;left:{_pl:g}px;top:{_pt:g}px;width:{_pw:g}px;height:{_ph:g}px' in _sc
          and 0 < _pl and _pl + _pw < 330 and 0 < _pt and _pt + _ph < 160 and abs(_pw / _ph - 665 / 444) < 0.01
          and len(_sp['con']) == 21 and sum(c[2] for c in _sp['con']) == 8 and len(_sp['dots']) == 64 and len(_sp['spine']) == 16 and len(_sp['bg']) == 700 and 'links' not in _sp
          and _sp['spine'][0][0] > _sp['spine'][-1][0] + 400 and all(a[0] > b[0] - 30 for a, b in zip(_sp['spine'], _sp['spine'][1:]))
          and _sh.count('class="szk"') == 21 and _sh.count('class="szg"') == 64 and _sh.count('class="szv"') == 21 + 64 + 30 and _sh.count('class="szc"') == 5
          and [t['thumb'] for t in ksd['themes'] if t['id'] == 'stars'] == [f'ks_{_st}.webp'] and _st not in _sold and not any(o in _sh + _sc for o in _sold)
          and (not _ksi or (all(f'ks_{b}.webp' in res for b in (_sb['base'], _sb['peg'], _st)) and not any(f'ks_{o}.webp' in res for o in _sold)
                            and _SI.open(os.path.join(RES2, f'ks_{_sb["base"]}.webp')).size == (1170, 480) and _SI.open(os.path.join(RES2, f'ks_{_sb["peg"]}.webp')).size == (665, 444)
                            and _SI.open(os.path.join(RES2, f'ks_{_sb["peg"]}.webp')).mode == 'RGBA' and _SI.open(os.path.join(RES2, f'ks_{_st}.webp')).size == (780, 320)))
          and (not os.path.isdir(_bl) or all(os.path.exists(os.path.join(_bl, o + '.webp')) for o in _sold)),
          f'第4.160版：星座の 壁紙の 馬は まさちゃんの ペガサス（夜空 1170×480・ペガサスの 絵 665×444〈すき通し・画面の 3倍〉を 流れる 星の 上・キラキラの 下に 置く：左 {_pl:g}・上 {_pt:g}・幅 {_pw:g}・高さ {_ph:g}pt）・'
          f'明るい 星 21（大 8）・小さい 星 64・鼻の頭 → しっぽの先の 道すじ 16点（右 → 左）・一覧の 小さい 絵も 新しい・前の 絵 2まいは 入って いない（手元には のこる）')
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
    n_face = 1 if PB else 0      # 第4.148版：PUSHボタンの 絵が ある ときは、コードの PUSH の 面 だけが 使って いた 絵（マスター帯の PUSH の 面：tengel_blobs.json の push・132KB）を 入れない
    # 第4.149版（まさちゃん 2026/11/11 00:39・02:14）：帯の 壁紙 3つ（シルバー帯・ゴールド帯・マスター帯）は まさちゃんの 3D の 像の 絵（kisekae/flat/metal_run.py：metal_blobs.json の 6まい）。
    #   前の 絵（銀 2・金 2・マスター帯の エンブレムの 絵 1）は アプリに 入れない（手元の ios/kisekae_blobs/ には のこす）＝5 → 9まい
    #   （銀・金・マスター帯 × いまの 絵／きらめきを ぬいた 絵／馬（主役）だけの 高画質の 絵：02:36「壁紙は、馬(主役)だけ画質良くなるようにして！」）
    _mb = _json.load(open(os.path.join(W, 'kisekae', 'metal_blobs.json')))
    _old_band = ['9504cde9557dd15164d7ea4c2fe29e8e', '6aa961c2be4422888172ea9689ef7cf0', '03691f51ad78a7922baf6b6a1d19d5ab', '681b968a52b39a9ec4076a934471596b', '0f58da915ffceb4dc05ffccb4b103100',
                 'fe75d71d3f3e61735f3ecd4f1cd7a9a6', '05f4939aa13b86c08f22f66271ac5bdd', '76742f3c9b5e6ee06e0c943008c6bd4a']      # 第4.158版：前の マスター帯の 像（Tenger：第4.149〜4.157版）の 3まい
    _tg = _json.load(open(os.path.join(out, 'Tengel.swiftpm', 'Resources', 'ks_tengel.json'), encoding='utf8'))
    check(len(_mb) == 9 and (not ks_imgs or (all(f'ks_{v}.webp' in res for v in _mb.values()) and not any(f'ks_{v}.webp' in res for v in _old_band)))
          and 'mxtw' in _tg['bnr']['html'] and 'tqw' not in _json.dumps(_tg['bnr']) and f"ks_{_mb['tengel_banner']}.webp" in _tg['bnr']['html'] and f'class="mxtH" href="ks_{_mb["tengel_statue"]}.webp"' in _tg['bnr']['html']
          and [t['desc'] for t in ksd['themes'] if t['id'] == 'tengel'] == ['テンゲル・光る像'] and [t['thumb'] for t in ksd['themes'] if t['id'] in ('silver', 'golden', 'tengel')] == [f"ks_{_mb[k]}.webp" for k in ('silver_banner', 'gold_banner', 'tengel_banner')],
          '第4.149版：帯の 壁紙 3つは 3D の 像の 絵（9まい：背景 6＋馬 だけの 高画質の 絵 3）・前の 絵 8まい（第4.158版：前の マスター帯の 像の 3まいも）は 入って いない・マスター帯の 上の 絵は 像＋きらめき（mxt：動く 数字と 緑の 雷は なし）・一覧の 説明と 小さい 絵も 新しい')
    # 第4.157版（まさちゃん 2026/11/12「課金の壁紙は全部馬の画質が悪いから同じように画質を上げてほしい！」）：花火の 馬の 足す光 だけ 別の 絵（3倍・fireworks_blobs.json の scatter_h）が 1まい 足された＝73 → 74こ
    check(len(ks_imgs) in (0, 72 - n_face + n_pk) and n_pk == 62 and (not os.path.isdir(os.path.join(W, 'ios', 'kisekae_blobs')) or len(ks_imgs) == 72 - n_face + n_pk)
          and (('ks_38c796c9e27ea6f52001b6605ca607a0.webp' not in res) if PB else True),
          f'着せ替えの絵：手元にあれば{72 - n_face}こ全部 Resources/ に入る・なければ入れずに作れる（{len(ks_imgs)}こ。第4.160版：ネオンの 3まいを 外して、星座は 2 → 3まい（夜空・ペガサス・止まった 絵）＝74 → 72こ。第4.157版：花火の 馬 だけの 絵（3倍）が 1まい 足された＝73 → 74こ。第4.149版：帯の 壁紙の 絵 5 → 9まい＝69 → 73こ。第4.148版：PUSHボタンの 絵が ある ときは マスター帯の コードの PUSH の 面の 絵 1こ を 入れない＝73 → 72こ。第4.147版：壁紙を 10枚 外した ので 99 → 69こ・壁紙パックの 絵は 74 → 62こ。第4.63版：勝負服の tile2・ネオンの dust と つぶなしの 止まった絵が 足された。第4.64版：ネオンの 止まった絵は 背景だけの 絵に 入れかわり・桜の 止まった絵と シートも 入れかわり＝数は 同じ。第4.87版：ネオンの dust（光のつぶの 絵）は 使わない＝光のつぶは 1つずつ ページが 動かす → 99こ。第4.92版：壁紙パックの 絵 {n_pk}こ を 足す）')
    check('ios/kisekae_blobs/' in gi and subprocess.run(['git', 'check-ignore', '-q', 'source/ios/kisekae_blobs/x.webp'], cwd=os.path.dirname(W)).returncode == 0, '着せ替えの絵のフォルダ（ios/kisekae_blobs/）は git に入らない（source/.gitignore）')
    # 第4.62版：アプリの 言葉は 日本語（Package.swift の defaultLocalization: "ja" と Resources/ja.lproj/Localizable.strings）→ 写真を 選ぶ 窓など iOS の 部品が 日本語に
    check('defaultLocalization: "ja",' in pk and os.path.exists(os.path.join(out, 'Tengel.swiftpm', 'Resources', 'ja.lproj', 'Localizable.strings')), 'アプリの 言葉は 日本語（defaultLocalization: "ja"・ja.lproj）：写真を 選ぶ 窓も 日本語に')
ap2 = open(os.path.join(W, 'ios', 'Tengel.swiftpm', 'TengelApp.swift'), encoding='utf8').read(); af = open(os.path.join(W, 'ios', 'Tengel.swiftpm', 'AppFiles.swift'), encoding='utf8').read()
check('import AVFoundation' in ap2 and 'setCategory(.ambient' in ap2 and '.mixWithOthers' in ap2, '効果音：消音スイッチなら鳴らさない・ほかのアプリの音楽は止めない（AVAudioSession ambient）')
check('case "m4a": return "audio/mp4"' in af, 'アプリの中の音のファイル（m4a）を Web の画面に渡せる')
# 第4.59版：テスト版（TENGEL_TEST=1）：TengelTest.swiftpm・名前「テンゲル テスト」・index.html に __TEST・絵と 音と 動画は ふつうと 同じ 入れ方（ここでは なしで 作る）
out2 = tempfile.mkdtemp()
r2 = subprocess.run([sys.executable, 'build_ios.py', out2], capture_output=True, text=True, env=dict(os.environ, TENGEL_TEST='1', FX_ASSETS='/nonexistent', KISEKAE_ASSETS='/nonexistent', PUSH_ASSETS='/nonexistent'))
check(r2.returncode == 0 and os.path.isdir(os.path.join(out2, 'TengelTest.swiftpm')) and os.path.exists(os.path.join(out2, 'TengelTest.swiftpm.zip')), 'テスト版：TENGEL_TEST=1 python3 build_ios.py → TengelTest.swiftpm（.zip）' + ('' if r2.returncode == 0 else '：' + (r2.stderr or r2.stdout)[-300:]))
if r2.returncode == 0:
    ps2 = open(os.path.join(out2, 'TengelTest.swiftpm', 'Package.swift'), encoding='utf8').read()
    h2 = open(os.path.join(out2, 'TengelTest.swiftpm', 'Resources', 'index.html'), encoding='utf8').read()
    # 第4.122版：テスト版は 本番と 別の アプリ（jp.tengel.app.test）・ビルド番号は あげる たびに 大きく（APP_VER から・ない ときは 日時）＝ TestFlight で iPhone に 本番と 並べて 入れる
    check('name: "テンゲル テスト",' in ps2 and 'bundleIdentifier: "jp.tengel.app.test",' in ps2 and 'bundleIdentifier: "jp.tengel.app",' not in ps2 and re.search(r'bundleVersion: "\d{8}\.\d+",', ps2) and 'supportedDeviceFamilies: [\n                .phone\n            ]' in ps2,
          'テスト版：アプリの 名前は「テンゲル テスト」・bundle id は jp.tengel.app.test（本番と 並べて 入れられる）・ビルド番号は 日付から・iPhone用は ふつうと 同じ')
    check('window.__TEST=true;' in h2 and 'テスト版の道具' in h2, 'テスト版：画面に __TEST（はじめから 10,000P・設定の いちばん上に テスト版の道具）')
    # 第4.148版：PUSHボタンの 絵が ない 作り方（PUSH_ASSETS=/nonexistent＝CI）：絵は 1まいも 入らない・一覧に pa なし・テーマの ファイルは 今までの コードの 面（svg）＝今までの PUSH の まま
    import json as _j2
    res2 = os.listdir(os.path.join(out2, 'TengelTest.swiftpm', 'Resources'))
    ksd2 = _j2.JSONDecoder().raw_decode(h2, h2.index('window.__KS=') + len('window.__KS='))[0]
    sk2 = _j2.load(open(os.path.join(out2, 'TengelTest.swiftpm', 'Resources', 'ks_sunset.json'), encoding='utf8')); px2 = _j2.load(open(os.path.join(out2, 'TengelTest.swiftpm', 'Resources', 'ks_pixel.json'), encoding='utf8'))
    check(not any(f.startswith('pb_') for f in res2) and len(ksd2['themes']) == 30 and not any('pa' in t for t in ksd2['themes']) and 'img' not in sk2['push'] and '<svg' in sk2['push']['svg'] and '<svg' in sk2['push']['pressed']
          and 'img' not in px2['push'] and '<svg' in px2['push']['svg'],
          '第4.148版：PUSHボタンの 絵が ない 作り方（CI と 同じ）：絵は 入らない・一覧に pa なし・テーマの ファイルは 今までの コードの 面（svg）の まま ＝ 今までの PUSH で 作れる')
shutil.rmtree(out2, ignore_errors=True)
shutil.rmtree(out, ignore_errors=True)   # 2026/11/04：作った アプリ（約190MB）を 残さない（前は /tmp に 1回ごとに 残って いた）
print('結果：', 'OK' if not fails else f'{len(fails)}件おかしい')
raise SystemExit(1 if fails else 0)
