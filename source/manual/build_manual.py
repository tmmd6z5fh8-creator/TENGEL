# テンゲルⅢ 説明書を組み立てる（2つの形）
#   python3 build_manual.py artifact <出力フォルダ> [アプリの版]  … claude.aiのアーティファクト用（tengel-manual.html と img/）
#   python3 build_manual.py pwa <出力フォルダ> [アプリの版]       … iPhoneアプリ用（manual.html と manual/）。build_pwa.py から呼ぶ
# 中身は content.html（<!--@項目のid--> で区切る）・manual.css・manual.js。画面の写真は img/（tools/shots.py → tools/conv.py で作る）
import hashlib, html, json, os, re, shutil, sys
D = os.path.dirname(os.path.abspath(__file__))


def icon(name, cls=''):
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"{(" class=" + chr(34) + cls + chr(34)) if cls else ""}>{ICONS[name]}</svg>'


ICONS = {
    'bookopen': '<path d="M2 4h6a4 4 0 0 1 4 4v13a3 3 0 0 0-3-3H2z"/><path d="M22 4h-6a4 4 0 0 0-4 4v13a3 3 0 0 1 3-3h7z"/>',
    'phone': '<rect x="6" y="2" width="12" height="20" rx="2.5"/><path d="M12 7v7"/><path d="m9 11 3 3 3-3"/>',
    'edit': '<path d="M4 20h4L19 9l-4-4L4 16z"/><path d="m13.5 6.5 4 4"/>',
    'camera': '<path d="M4 7h3l2-3h6l2 3h3v13H4z"/><circle cx="12" cy="13" r="4"/>',
    'layers': '<path d="m12 3 9 5-9 5-9-5z"/><path d="m3 13 9 5 9-5"/>',
    'pick': '<rect x="3" y="7" width="7" height="10" rx="2"/><rect x="14" y="7" width="7" height="10" rx="2" stroke-dasharray="2.4 2.2"/><path d="m5 12 1.5 1.5L8.5 11"/>',
    'yen': '<circle cx="12" cy="12" r="9"/><path d="m8.5 6.5 3.5 5 3.5-5M12 11.5V18M9 12.5h6M9 15.5h6"/>',
    'check': '<circle cx="12" cy="12" r="9"/><path d="m8 12.2 2.8 2.8L16 9.5"/>',
    'list': '<path d="M9 6h12M9 12h12M9 18h12"/><circle cx="4.5" cy="6" r="1.2"/><circle cx="4.5" cy="12" r="1.2"/><circle cx="4.5" cy="18" r="1.2"/>',
    'ticket': '<path d="M3 7a1 1 0 0 1 1-1h16a1 1 0 0 1 1 1v3a2 2 0 0 0 0 4v3a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1v-3a2 2 0 0 0 0-4z"/><path d="M14 6v12" stroke-dasharray="2 2.5"/>',
    'trophy': '<path d="M8 4h8v5a4 4 0 0 1-8 0z"/><path d="M16 5h3v2a3 3 0 0 1-3 3M8 5H5v2a3 3 0 0 0 3 3"/><path d="M12 13v4M8 20h8M9.5 17h5"/>',
    'chart': '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    'db': '<ellipse cx="12" cy="5.5" rx="8" ry="3"/><path d="M4 5.5v13c0 1.7 3.6 3 8 3s8-1.3 8-3v-13"/><path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
    'sync': '<path d="M20 11a8 8 0 0 0-14.3-4.9L4 8"/><path d="M4 3v5h5"/><path d="M4 13a8 8 0 0 0 14.3 4.9L20 16"/><path d="M20 21v-5h-5"/>',
    'sliders': '<path d="M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12"/><circle cx="16" cy="6" r="2"/><circle cx="10" cy="12" r="2"/><circle cx="18" cy="18" r="2"/>',
    'key': '<circle cx="8" cy="15" r="4"/><path d="m10.8 12.2 8.7-8.7M16 7l3 3M14 9l2 2"/>',
    'shield': '<path d="M12 3 4 6v6c0 4.5 3.4 8.3 8 9 4.6-.7 8-4.5 8-9V6z"/><path d="m8.5 12 2.5 2.5 4.5-5"/>',
    'buoy': '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4"/><path d="m5.6 5.6 3.6 3.6M14.8 14.8l3.6 3.6M18.4 5.6l-3.6 3.6M9.2 14.8l-3.6 3.6"/>',
    'book': '<path d="M4 4.5A1.5 1.5 0 0 1 5.5 3H20v16H5.5A1.5 1.5 0 0 0 4 20.5z"/><path d="M4 20.5A1.5 1.5 0 0 0 5.5 22H20"/><path d="M8.5 8h7M8.5 12h5"/>',
    'search': '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    'chev': '<path d="m9 5 7 7-7 7"/>',
    'left': '<path d="m15 5-7 7 7 7"/>',
    'spark': '<path d="M12 3c.6 4.4 2.6 6.4 7 7-4.4.6-6.4 2.6-7 7-.6-4.4-2.6-6.4-7-7 4.4-.6 6.4-2.6 7-7z"/>',
    'alert': '<path d="M12 3 2.5 20h19z"/><path d="M12 10v4.5M12 17.2v.3"/>',
    'copy': '<rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V5a1 1 0 0 1 1-1h10"/>',
    'plusbox': '<rect x="4" y="4" width="16" height="16" rx="3"/><path d="M12 8v8M8 12h8"/>',
    'palette': '<path d="M12 3a9 9 0 0 0 0 18c1.4 0 2.2-.9 2.2-2 0-.6-.3-1-.7-1.4-.4-.4-.6-.8-.6-1.3 0-1 .9-1.8 2-1.8H16a5 5 0 0 0 5-5c0-3.6-4-6.5-9-6.5z"/><circle cx="7.5" cy="11" r="1.2"/><circle cx="10.5" cy="7.5" r="1.2"/><circle cx="15" cy="7.5" r="1.2"/><circle cx="17.5" cy="11" r="1.2"/>',
    'x': '<path d="M6 6l12 12M18 6 6 18"/>',
    'send': '<path d="M21 3 3 10.5l7 2.5 2.5 7z"/><path d="m10 13 5-5"/>',
}


def icon(name, cls=''):
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"{(" class=" + chr(34) + cls + chr(34)) if cls else ""}>{ICONS[name]}</svg>'


GROUPS = [('start', 'はじめに'), ('judge', '判定する（判定タブ）'), ('rec', '記録する'), ('win5', 'WIN5'), ('data', '数字とデータ'), ('set', '設定'), ('help', '困ったとき・ことば')]
ITEMS = [
    dict(id='about', g='start', t='このアプリでできること', d='5つのタブと、おぼえておいてほしいこと', ic='bookopen', kw='タブ 使い方 できること'),
    dict(id='install', g='start', t='iPhoneに入れる・更新する', d='ホーム画面に追加／新しい版にする', ic='phone', kw='インストール ホーム画面 Safari 更新 アップデート'),
    dict(id='input', g='judge', t='レースとオッズを入れる', d='必ず入れるもの・入れ方のコツ', ic='edit', kw='入力 単勝 複勝 3連単 馬場 頭数 距離 クリア 入力例'),
    dict(id='ocr', g='judge', t='オッズ画像から読み取る', d='スクショ1〜3枚で入力欄が埋まる', ic='camera', kw='画像 スクショ 写真 読み取り OCR'),
    dict(id='result', g='judge', t='判定結果の見方', d='層・推奨ゾーン・3着・参考的中率', ic='layers', kw='判定 層 ゾーン 推奨 3着 参考的中率 旧本線 A層 B層 C層'),
    dict(id='pick', g='judge', t='買う馬を選ぶ', d='番号を押して「買う／買わない」を切り替え', ic='pick', kw='馬番 選ぶ うすい 買う馬'),
    dict(id='record', g='rec', t='結果と収支を記録する', d='券種・金額・買ったゾーン・着順', ic='yen', kw='記録 保存 券種 購入額 回収額 着順 未購入 払い戻し'),
    dict(id='hit', g='rec', t='当たり外れの決まり方', d='例で見る「的中」と「不的中」', ic='check', kw='的中 不的中 結果待ち 当たり 外れ 的中ボタン PUSH 演出 デカ的中 ど的中 ボード 効果音 控えめ'),
    dict(id='records', g='rec', t='記録タブ', d='一覧・直す・判定画面で開く・書き出し', ic='list', kw='一覧 書き出し コピー Excel 削除'),
    dict(id='win5', g='win5', t='WIN5の組み立て方', d='5レース・予算・1着ゾーン・買う馬', ic='ticket', kw='WIN5 予算 点数 ランダム 推奨'),
    dict(id='win5rec', g='win5', t='WIN5の結果と記録', d='1着の馬番で○×・払戻を保存', ic='trophy', kw='WIN5 結果 払戻 記録'),
    dict(id='stats', g='data', t='実測・回収タブ', d='自分の収支と、実測①〜⑦', ic='chart', kw='収支 回収率 実測 期間 本線'),
    dict(id='mother', g='data', t='マザーデータ', d='参考的中率のもとになるデータ（3つ）', ic='db', kw='マザーデータ 基盤データ Excel JRA 船橋'),
    dict(id='racedata', g='data', t='レースのデータを入れる', d='判定＋着順でマザーデータに1行・一覧で直す', ic='plusbox', kw='マザーデータ 入れる 着順 払戻 一覧 直す 消す 手で入れる CSV 書き出す 足す 入れ替える'),
    dict(id='dataupdate', g='data', t='大井のデータを新しくする', d='分析シートと分析表を姫に送るだけ', ic='sync', kw='更新 分析シート 分析表 姫 突き合わせ'),
    dict(id='points', g='set', t='ポイント・Pカスタム・ミッション', d='1レース200P・買う・解放・記録でもらう', ic='yen', kw='ポイント 200P 買う サブスク Pカスタム 解放 券種 ミッション 消える 復元'),
    dict(id='kisekae', g='set', t='着せ替え（壁紙）', d='41のテーマ・ポイントで解放・帯の壁紙・壁紙パック・結果ボードカスタム', ic='palette', kw='壁紙パック 海賊 競馬場 宇宙 パドック 深海 恐竜時代 切り絵 浮世絵風 スチームパンク 近未来都市 七夕 結果ボードカスタム ボードの飾り 出世馬 ボードを持つ馬 買い切り 着せ替え 壁紙 テーマ 解放 帯 シルバー帯 ゴールド帯 マスター帯 色 字 上の絵 的中ボタン ボード'),
    dict(id='zones', g='set', t='買い目編集', d='区分ごとの馬単と3着を変える', ic='sliders', kw='カスタム 買い目 編集 初期'),
    dict(id='apikey', g='set', t='画像の読み取り（APIキー）', d='キーの作り方と料金', ic='key', kw='APIキー Anthropic 料金 モデル'),
    dict(id='backup', g='set', t='アプリの更新とバックアップ', d='記録を守る・機種変更', ic='shield', kw='バックアップ 機種変更 戻す 更新'),
    dict(id='update', g='set', t='アップデート（新しい版・データ）', d='App Storeの新しい版と、データの更新', ic='sync', kw='アップデート 更新 新しい版 App Store データの更新 お知らせ'),
    dict(id='trouble', g='help', t='困ったとき', d='よくあるメッセージと直し方', ic='buoy', kw='エラー 困った 直し方 できない'),
    dict(id='glossary', g='help', t='用語集', d='層・比・ゾーン・旧本線…', ic='book', kw='用語 ことば 意味'),
]

# 画面の写真：番号の位置（その要素の高さのどこか fy）・左の余白に番号を出す
SHOTS = {
    'tabbar': ('画面の下の5つのタブ（判定・WIN5・記録・実測・回収・設定）', None, []),
    'update_bar': ('新しい版のお知らせと「更新する」ボタン', '新しい版があるときのお知らせ（画面は例）', []),
    'judge_info': ('判定タブのレース情報の欄', '判定タブ「レース情報」（画面は例・架空のレース）', [('#slotJudge',), ('#ocrRow', .3), ('#fVenue',), ('#fR',), ('#fN',), ('#fBaba',)]),
    'judge_odds': ('単勝・複勝オッズの欄', '馬番ごとに単勝と複勝を入れる（途中は省略）', []),
    'judge_tri': ('3連単の人気順の欄', None, [('#fS1',), ('#fS5',), ('#clearBtn',)]),
    'bottom_bars': ('入力中に下に出る判定のバー', '「判定へ↓」を押すと判定結果まで移動するよ', []),
    'ocr_need': ('オッズ画像から読み取るボタンと、キーがないときの案内', None, [('#ocrRow', .3), ('#ocrMsg', .28)]),
    'ocr_done': ('オッズ画像から読み取るボタンと、読み取ったあとの案内', '読み取ったあと（画面は例・架空のレース）', [('#ocrRow', .3), ('#ocrMsg', .3)]),
    'result_a1': ('判定結果の画面の上半分（A層の例）', 'A層の例・上半分（画面は例・架空のレース）', [
        ('.vhead .vkubun',), ('.vhead .vratio', .45), ('.vhead .chips', .3), ('ol.zones > li:nth-child(1) .zflow',), ('ol.zones > li:nth-child(1) .znums',),
        ('ol.zones > li:nth-child(1) .zref', .25), ('ol.zones > li:nth-child(1) .zthird', .09)]),
    'result_a2': ('判定結果の画面の下半分', '下半分（第2のゾーンと、その下）', [('.numbers', .14), ('.vfoot', .045), ('.oldline',), ('.w5push',), ('#copyAll',), ('details.full',)], 8),
    'result_c': ('判定結果の画面（C層・第2段階の例）', 'C層・第2段階の例。推奨ゾーンが3本になって、大穴・超大穴の番号も出るよ（画面は例）', []),
    'pick_before': ('ゾーンの番号（押す前）', '押す前：はじめは全部選んだ状態', []),
    'pick_after': ('ゾーンの番号（4番を外したあと）', '2着の4番を押すと、うすくなる＝買わない馬', [], 1, ['button.hp.off']),
    'record_1': ('結果・収支の記録の欄（上）', '馬単と3連単を買って的中した例（画面は例）', [('[data-k=status]', .2), ('[data-k=types]',), ('[data-k=amts]',)]),
    'record_2': ('結果・収支の記録の欄（下）', 'つづき', [('[data-k=buyzf]',), ('[data-k=mode]',), ('[data-k=mfld]',), ('[data-k=other]',), ('[data-act=save]',)], 4),
    'st_hit': ('的中の表示', None, []), 'st_notbought': ('買っていないゾーンで不的中の表示', None, []), 'st_notpicked': ('選んでいない馬で不的中の表示', None, []),
    'st_outside': ('推奨ゾーンの外で不的中の表示', None, []), 'st_wait': ('結果待ちの表示', None, []),
    'records': ('記録タブの一覧', '記録タブ（画面は例）', [('#ymRec',), ('#rFilters',), ('#recSummary',), ('#recExportBtn',), ('@', 390), ('#recList .dgroup h3',), ('#recList .lrow:nth-child(1)',)]),
    'record_open': ('開いた記録のボタン', '行を押して開いたときの下のボタン', []),
    'w5_top': ('WIN5タブの上の部分', 'WIN5タブ（画面は例）', [('details.full',), ('#w5Date',), ('#w5Mode',), ('#w5Sum', .2)]),
    'w5_race': ('WIN5の1レース分', '1レース分のカード', [('.w5h', .25), ('.w5zones',), ('.w5picks',), ('.zref', .3), ('[data-w5act=edit]',)]),
    'w5_res': ('WIN5の結果・記録', '③が外れて不的中の例', [('.w5res', .55), ('#w5Status',), ('#w5Stake',), ('#w5Other',), ('[data-w5act=save]',)]),
    'stats_money': ('買ったレースの収支', '上の数字（例）', []),
    'stats_type': ('券種別の収支の表', '券種別の収支（例）', []),
    'stats_period': ('期間のボタン', '期間のボタン', []),
    'stats_t1': ('① 層別実測の表', '① 層別実測（例）', []),
    'set_mother': ('マザーデータ（3つ）', '設定 → マザーデータ', [('#slotList', .17), ('#slotList', .55), ('#slotEdit', .075)]),
    'set_zone': ('買い目編集', '設定 → 買い目編集（A層）', [('.zk-tabs', .2), ('.zk-head',), ('ol.zedit > li:nth-child(1)', .06), ('.zr-line',), ('.zr-stat',)]),
    'set_zone_save': ('保存するボタン', '変えたら「保存する」', []),
    'set_ocr': ('画像の読み取りの設定', '設定 → 画像の読み取り', [('#soKey',), ('#soModel',)]),
    'set_backup': ('バックアップ', '設定 → バックアップ', [('#pwaBackup',), ('#pwaRestore',)]),
    'set_update': ('アプリの更新', '設定 → アプリの更新', []),
    # アプリの中でレースのデータを入れる（2026.10.13-1〜）
    'md_record': ('結果の記録の「マザーデータにも入れる」の欄', '「マザーデータにも入れる」（画面は例・架空のレース）', []),
    'md_tools': ('マザーデータの編集の中の、レースのデータのボタン', '設定 → マザーデータ → 編集', [('#mdOpenBtn',), ('#mdAddBtn',), ('#mdExpBtn',)]),
    'md_list': ('マザーデータのレースの一覧', 'レースの一覧（画面は例）', [('#mdYM',), ('.mdrow', .3)]),
    'md_form': ('レースを1つ入れる欄', '手で1つ入れる（画面は例・架空のレース）', [('[data-k=date]',), ('[data-k=dist]',), ('[data-k=res]',), ('[data-k=umatanPay]',), ('[data-k=cnt]',), ('[data-k=pv]',)]),
    'md_export': ('書き出す欄', '書き出す（CSV・コピー）', []),
    'md_merge': ('ファイルを読んだあとの「足す」と「入れ替える」', 'Excel・CSVを選んだところ（画面は例）', []),
    # App Store版だけ：アップデート（2026.10.13-1〜）
    'upd_bars': ('App Storeの新しい版と新しいデータのお知らせ', '開いたときのお知らせ（画面は例）', []),
    'upd_app': ('設定のアプリの更新', '設定 → アプリの更新（画面は例）', [('dl.kvs dd',), ('#nuStore',), ('#nuCheck',)]),
    'upd_data': ('設定のデータの更新', '設定 → データの更新（画面は例）', [('#sdCur',), ('#sdCheck',), ('#sdApply',)]),
}
# App Store版だけの写真（Web版では使わない）
APP_ONLY_SHOTS = {'upd_bars', 'upd_app', 'upd_data', 'ocr_done'}

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=BIZ+UDPGothic:wght@400;700&family=Dela+Gothic+One&family=IBM+Plex+Mono:wght@500;600&display=swap">')
# App Store版：Google に通信しないで、アプリに入れたフォントを使う（ios/fonts）。
# 第4.109版：BIZ UDPGothic と Dela Gothic One は 字は そのままで WOFF2 に（ios/fonts/make_woff2.py・約11.8MB → 約5.6MB・しぼらない）。
#   IBM Plex Mono は 予約名「Plex」が ある ので もとの TTF の まま（OFL 1.1：形式を かえるのは 改変）
APP_FONT_FILES = ['BIZUDPGothic-Regular.woff2', 'BIZUDPGothic-Bold.woff2', 'DelaGothicOne-Regular.woff2', 'IBMPlexMono-Medium.ttf', 'IBMPlexMono-SemiBold.ttf']
APP_FONTS = ('<style>'
             "@font-face{font-family:'BIZ UDPGothic';src:url('fonts/BIZUDPGothic-Regular.woff2') format('woff2');font-weight:400;font-style:normal;font-display:swap}"
             "@font-face{font-family:'BIZ UDPGothic';src:url('fonts/BIZUDPGothic-Bold.woff2') format('woff2');font-weight:700;font-style:normal;font-display:swap}"
             "@font-face{font-family:'Dela Gothic One';src:url('fonts/DelaGothicOne-Regular.woff2') format('woff2');font-weight:400;font-style:normal;font-display:swap}"
             "@font-face{font-family:'IBM Plex Mono';src:url('fonts/IBMPlexMono-Medium.ttf') format('truetype');font-weight:500;font-style:normal;font-display:swap}"
             "@font-face{font-family:'IBM Plex Mono';src:url('fonts/IBMPlexMono-SemiBold.ttf') format('truetype');font-weight:600;font-style:normal;font-display:swap}"
             '</style>')
# App Store版で出さない項目（ホーム画面に追加・チャットでデータを送る流れはWeb版だけ）
APP_SKIP = ('install', 'dataupdate', 'apikey')   # App Store版は画像の読み取りにAPIキーを使わない（端末の中で読む）
# Web版で出さない項目（App Storeのアップデート・データの更新はApp Store版だけ）
WEB_SKIP = ('update', 'points', 'kisekae')   # ポイント・Pカスタム・ミッション・着せ替えも App Store版だけ
# App Store版だけ名前を変える項目（アプリの更新は「アップデート」の項目にあるので）
APP_ITEM = {'backup': {'t': 'バックアップ', 'd': '記録を守る・機種変更・自動バックアップ'}}
SHOT_CSS = ('\n.ring{position:absolute;border:2.5px solid var(--gold);border-radius:9px;box-shadow:0 0 0 2px rgba(10,27,34,.55),0 0 14px rgba(217,180,90,.55);pointer-events:none}'
            '\n.shot.has-mk .shot-in{padding-left:30px}\n.shot.has-mk .mk{left:2px;margin-left:0}'
            '\n.shot.has-mk .mk::after{content:"";position:absolute;left:23px;top:10px;width:6px;height:2px;border-radius:1px;background:var(--gold)}\n')


def _app_target():
    import importlib.util
    spec = importlib.util.spec_from_file_location('app_target', os.path.join(os.path.dirname(D), 'app_target.py'))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def build(mode, out, app_ver='2026.10.12-4', mother=None):
    """説明書を作る。返り値：(使った画像のファイル名, 説明書の画像の版)
    mother：アプリに入れるマザーデータ（App Store版の「はじめのデータ ○走」に使う）"""
    assert mode in ('artifact', 'pwa', 'app'), mode
    app = mode == 'app'
    items = [dict(it) for it in ITEMS if not (app and it['id'] in APP_SKIP) and not (not app and it['id'] in WEB_SKIP)]
    # App Store版：画面の写真はApp Store版の画面で撮ったもの（img_app/・名前の出ない画面）
    IMG = 'img_app' if app else 'img'
    boot = os.environ.get('MANUAL_SHOTS_BOOTSTRAP') == '1'   # 写真を撮るためにだけ作るとき（tools/shots.py）
    if app and boot:   # App Store版の写真がまだなくても作れるように、Web版の写真を仮に使う
        IMG = 'img'
    sfx = '_app' if IMG == 'img_app' else ''
    meta = json.load(open(D + f'/meta{sfx}.json', encoding='utf-8'))
    dims = json.load(open(D + f'/dims{sfx}.json', encoding='utf-8'))
    imgdir = 'img' if mode == 'artifact' else 'manual'
    if app:
        AT = _app_target()
        for it in items:
            it['kw'] = it['kw'].replace(' JRA 船橋', ' 開催場')
            it.update(APP_ITEM.get(it['id'], {}))
    used, imgs = set(), set(['banner.webp', 'emblem-160.webp'])

    def shot_html(name):
        if boot and name not in dims:   # 写真を撮るためにだけ作るとき：まだ撮っていない写真は入れない
            return ''
        spec = SHOTS[name]; alt, cap, marks = spec[:3]; start = spec[3] if len(spec) > 3 else 1; rings = spec[4] if len(spec) > 4 else []
        d = dims[name]; m = meta.get(name, {}); H = m.get('H', d['h']); top = m.get('cropTop', 0)
        mk = []
        for i, sp in enumerate(marks, start):
            if sp[0] == '@':
                y = sp[1]
            else:
                b = m['b'].get(sp[0])
                if boot and not b:   # 写真を撮るためにだけ作るとき：前の写真にない場所の番号は出さない
                    continue
                assert b, (name, sp)
                y = b['y'] + b['h'] * (sp[1] if len(sp) > 1 else .5) - top
            if boot and not 0 <= y <= H:
                continue
            assert 0 <= y <= H, (name, sp, y, H)
            mk.append(f'<i class="mk" style="top:{y / H * 100:.2f}%">{i}</i>')
        for sel in rings:
            b = m['b'][sel]; pad = 4
            mk.append(f'<i class="ring" style="left:{(b["x"] - pad) / d["w"] * 100:.2f}%;top:{(b["y"] - pad - top) / H * 100:.2f}%;width:{(b["w"] + 2 * pad) / d["w"] * 100:.2f}%;height:{(b["h"] + 2 * pad) / H * 100:.2f}%"></i>')
        cls = 'shot has-mk' if marks else 'shot'
        imgs.add(f's_{name}.webp')
        fig = f'<figure class="{cls}"><div class="shot-in"><img src="{imgdir}/s_{name}.webp" width="{d["w"]}" height="{d["h"]}" alt="{html.escape(alt)}" loading="lazy" decoding="async">{"".join(mk)}</div>'
        if cap:
            fig += f'<figcaption>{html.escape(cap)}</figcaption>'
        return fig + '</figure>'

    def fill(s):
        def sh(mo):
            used.add(mo.group(1)); return shot_html(mo.group(1))
        s = re.sub(r'\{\{shot:([a-z0-9_]+)\}\}', sh, s)
        s = re.sub(r'\{\{i:([a-z]+)\|ic\}\}', lambda mo: f'<span class="ic">{icon(mo.group(1))}</span>', s)
        s = re.sub(r'\{\{i:([a-z]+)\}\}', lambda mo: icon(mo.group(1)), s)
        assert '{{' not in s, s[s.index('{{'):s.index('{{') + 40]
        return s

    content = open(D + '/content.html', encoding='utf-8').read()
    parts = re.split(r'<!--@([a-z0-9]+)-->', content)
    sec = {parts[i]: parts[i + 1].strip() for i in range(1, len(parts), 2)}
    assert set(sec) == {it['id'] for it in ITEMS}, set(sec) ^ {it['id'] for it in ITEMS}
    if app:   # App Store版：content_app.html の項目で入れ替える・端末の言い方・競馬場や版の名前を出さない
        ap = re.split(r'<!--@([a-z0-9]+)-->', open(D + '/content_app.html', encoding='utf-8').read())
        over = {ap[i]: ap[i + 1].strip() for i in range(1, len(ap), 2)}
        assert set(over) <= set(sec), set(over) - set(sec)
        sec.update(over)
        for x in APP_SKIP:
            sec.pop(x)
    else:   # Web版：App Store版だけの項目（アップデート）は出さない
        for x in WEB_SKIP:
            sec.pop(x)
    if app:
        for a, b in [('iPhoneの数字キーでは', '数字のキーボードでは')]:
            k = [x for x in sec if a in sec[x]]; assert k, a
            for x in k: sec[x] = sec[x].replace(a, b)
        sec = AT.app_manual_sections(sec)
        rows = mother or []
        last = max((r['date'] for r in rows), default='')
        minfo = f'{len(rows)}走' + (f'（{int(last[5:7])}/{int(last[8:10])}まで）' if last else '')
        for x in sec:
            sec[x] = sec[x].replace('{{mother}}', minfo)
    gname = dict(GROUPS)
    sections = []
    for k, it in enumerate(items):
        prev = items[k - 1] if k else None; nxt = items[k + 1] if k + 1 < len(items) else None
        pg = '<nav class="pager" aria-label="前後の項目">'
        pg += f'<a class="prev" href="#{prev["id"]}"><small>‹ 前の項目</small><b>{prev["t"]}</b></a>' if prev else '<span class="none"></span>'
        pg += f'<a class="next" href="#{nxt["id"]}"><small>次の項目 ›</small><b>{nxt["t"]}</b></a>' if nxt else '<span class="none"></span>'
        pg += '</nav><div class="tomenu"><a href="#menu">' + icon('list') + 'もくじに戻る</a></div>'
        sections.append(f'<section class="item" id="s-{it["id"]}" data-id="{it["id"]}" hidden aria-labelledby="h-{it["id"]}">'
                        f'<p class="eyebrow">{gname[it["g"]]}</p><h2 id="h-{it["id"]}">{it["t"]}</h2>{fill(sec[it["id"]])}{pg}</section>')
    unused = set(SHOTS) - used
    assert app or not (unused - APP_ONLY_SHOTS), unused   # App Store版は「iPhoneに入れる」などを出さないので、使わない写真がある
    menu = []
    for g, gl in GROUPS:
        rows = ''.join(f'<a class="mrow" id="m-{it["id"]}" href="#{it["id"]}"><span class="ic">{icon(it["ic"])}</span><span><b>{it["t"]}</b><small>{it["d"]}</small></span>{icon("chev", "chev")}</a>'
                       for it in items if it['g'] == g)
        menu.append(f'<section class="group" aria-label="{gl}"><h2 class="sec">{gl}</h2><div class="rows">{rows}</div></section>')

    css = open(D + '/manual.css', encoding='utf-8').read() + SHOT_CSS
    js = open(D + '/manual.js', encoding='utf-8').read()
    items_js = json.dumps([{k: it[k] for k in ('id', 't', 'd', 'kw')} for it in items], ensure_ascii=False)
    in_app = mode in ('pwa', 'app')
    start = ('<li><a href="#input"><span class="n">1</span><b>レースを判定する</b><small>オッズを入れるだけ</small></a></li>\n'
             '<li><a href="#record"><span class="n">2</span><b>結果を記録する</b><small>当たり外れと収支</small></a></li>\n'
             '<li><a href="#backup"><span class="n">3</span><b>記録を守る</b><small>自動バックアップとファイル保存</small></a></li>') if app else (
             '<li><a href="#install"><span class="n">1</span><b>iPhoneに入れる</b><small>ホーム画面に追加</small></a></li>\n'
             '<li><a href="#input"><span class="n">2</span><b>レースを判定する</b><small>オッズを入れるだけ</small></a></li>\n'
             '<li><a href="#record"><span class="n">3</span><b>結果を記録する</b><small>当たり外れと収支</small></a></li>')
    foot = ('<span>わからないことは、設定 →「このアプリについて」のお問い合わせ先へ。参考的中率は過去の実測で、的中を約束するものではないよ。</span>' if app else
            '<span>わからないことは、画面のスクショを姫に送ってね。</span>')
    body = f'''<div class="topbar" id="topbar" hidden><div class="wrap">
<button class="back" id="back" type="button" hidden>{icon('left')}もくじ</button>
{f'<a class="back" id="toApp" href="./">{icon("left")}アプリに戻る</a>' if in_app else ''}
<span class="tb-title" id="tbTitle"></span>
{f'<a class="tb-close" id="closeApp" href="./" aria-label="アプリに戻る" hidden>{icon("x")}</a>' if in_app else ''}
<img class="tb-emblem" src="{imgdir}/emblem-160.webp" width="38" height="38" alt="">
</div></div>

<main id="home" class="wrap">
<header class="hero">
<img class="banner" src="{imgdir}/banner.webp" width="1200" height="655" alt="TENGER テンゲル　独自の統計・オッズ分析による競馬検討支援システム">
<div class="hero-text">
<p class="eyebrow">アプリの使い方</p>
<h1><span class="gold">テンゲルⅢ</span> 説明書</h1>
<p class="lead">知りたい項目を押すと、その説明が出るよ。画面の写真に番号をつけて、順番に読めるようにしてあるよ。</p>
<ul class="meta"><li>アプリ {html.escape(app_ver)}</li>{f'<li>はじめのデータ {minfo}</li>' if app else '<li>第13改訂版</li><li>大井 290走（10/9まで）</li>'}</ul>
</div>
</header>

<div class="search" role="search">{icon('search')}<label class="sr" for="q">説明書の中をさがす</label><input id="q" type="search" placeholder="{'さがす（例：単勝5連勝、読み取り、的中率）' if app else 'さがす（例：WIN5、APIキー、的中率）'}" autocomplete="off" enterkeyhint="search"><button class="qx" id="qx" type="button" aria-label="さがす言葉を消す" hidden>×</button></div>
<p class="qinfo" id="qinfo" hidden></p>

<section id="start" aria-labelledby="st-h">
<h2 class="sec" id="st-h">はじめての人は、この順番で</h2>
<ol class="start-steps">
{start}
</ol>
</section>

<nav id="menu" aria-label="もくじ">
{''.join(menu)}
</nav>

<footer class="foot">
{foot}
<span>画面の写真は、架空のレースで撮ったアプリの画面だよ。写真の数字は例だよ。</span>
</footer>
</main>

<main id="page" class="wrap" hidden>
{''.join(sections)}
</main>
<script>window.__ITEMS = {items_js};{' window.__IN_APP = true;' if in_app else ''}</script>
<script>
{js}
</script>
'''
    os.makedirs(out, exist_ok=True)
    os.makedirs(os.path.join(out, imgdir), exist_ok=True)
    for f in sorted(imgs):
        shutil.copy(os.path.join(D, IMG if f.startswith('s_') else 'img', f), os.path.join(out, imgdir, f))
    if mode == 'artifact':
        page = f'<title>テンゲルⅢ 説明書</title>\n{FONTS}\n<style>\n{css}\n</style>\n{body}'
        path = os.path.join(out, 'tengel-manual.html')
    elif app:
        page = f'''<!DOCTYPE html>
<html lang="ja" data-app="1" data-hint="単勝5連勝、読み取り、的中"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>テンゲル 説明書</title>
{APP_FONTS}
<style>:root{{--sat:max(env(safe-area-inset-top,0px),var(--top-inset,0px));--sab:max(env(safe-area-inset-bottom,0px),var(--bottom-inset,0px));padding-top:var(--sat);padding-bottom:var(--sab)}}body{{margin:0}}[hidden]{{display:none!important}}
{css}
</style></head><body>
{body}</body></html>
'''
        path = os.path.join(out, 'manual.html')
        page = AT.app_manual_page(page)   # コメントを消す・WIN5→単勝5連勝・出さない言葉が残っていたら止める
    else:
        page = f'''<!DOCTYPE html>
<html lang="ja" data-hint="WIN5、APIキー、的中"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default"><meta name="apple-mobile-web-app-title" content="テンゲルⅢ">
<meta name="theme-color" content="#0a1b22"><link rel="manifest" href="manifest.webmanifest"><link rel="apple-touch-icon" href="icon3-180.png"><link rel="icon" href="icon3-192.png">
<title>テンゲルⅢ 説明書</title>
{FONTS}
<style>:root{{--sat:max(env(safe-area-inset-top,0px),var(--top-inset,0px));--sab:max(env(safe-area-inset-bottom,0px),var(--bottom-inset,0px));padding-top:var(--sat);padding-bottom:var(--sab)}}body{{margin:0}}[hidden]{{display:none!important}}
{css}
</style></head><body>
{body}</body></html>
'''
        path = os.path.join(out, 'manual.html')
    open(path, 'w', encoding='utf-8').write(page)
    h = hashlib.md5()
    for f in sorted(imgs):
        h.update(f.encode()); h.update(open(os.path.join(D, IMG if f.startswith('s_') else 'img', f), 'rb').read())
    return sorted(imgs), h.hexdigest()[:8]


if __name__ == '__main__':
    mode, out = sys.argv[1], sys.argv[2]
    ver = sys.argv[3] if len(sys.argv) > 3 else '2026.10.12-4'
    imgs, mv = build(mode, out, ver)
    print('説明書', mode, out, '画像', len(imgs), '版', mv)
