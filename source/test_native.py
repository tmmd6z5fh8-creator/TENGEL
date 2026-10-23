# アプリ版（iPhone・iPadのアプリの中の画面）のテスト。アプリ（Swift）のかわりに、にせもののアプリをつなぐ
#  ・設定タブ：「アプリの更新」（App Storeの版を確かめる・Web版の更新の確認はしない）・「データの更新」・自動バックアップの欄
#  ・記録を保存すると、アプリの中に自動バックアップ（APIキーは入れない）
#  ・バックアップを保存／CSVで保存 → 共有シート（アプリ）に渡す・コピーはアプリへ
#  ・保存場所が消えた（記録0件）のに自動バックアップに記録がある → 「戻す？」→ 戻す／戻さない
#  ・CMの動画は公開中のWeb版から読む
#  ・Web版（ブラウザ）は今までどおり（アプリの印は出ない）
#  ・App Store版の中身（TARGET=app）：Google に通信しない（フォントはアプリの中）・「このアプリについて」（免責・20歳・相談先・非公式と商標・プライバシー・フォントのライセンス）
#    ・お客さん向けの言い方（まさちゃん・姫に送って・iPhone を出さない）・説明書はApp Store版（「iPhoneに入れる」なし）
import json, os, shutil, subprocess, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv'); PORT = 8791; BASE = f'http://localhost:{PORT}/TENGEL/'
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'TENGEL')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, HIST='hist_280.json', DROP=''))
# App Store版の中身（TARGET=app）。アプリの中（tengel://）のかわりに、localhost でアプリ版として開く
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, HIST='hist_280.json', DROP='', TARGET='app'))
for f in ('index.html', 'manual.html'):
    pth = os.path.join(SRV, 'APP', f); html = open(pth, encoding='utf8').read()
    if f == 'index.html':
        assert "window.__NATIVE = location.protocol === 'tengel:';" in html
        html = html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;')
    open(pth, 'w', encoding='utf8').write(html)
APPURL = f'http://localhost:{PORT}/APP/'
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
fails, errs = [], []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label)
    if not c:
        fails.append(label)


form = {"venue": "大井", "date": "2026-10-10", "r": "8", "dist": "1400", "surface": "ダ", "baba": "稍重", "n": "14", "s1": "41.3", "s1combo": "6-2-10", "s5": "58.2", "s10": "84.0", "rname": "はなまる特別", "start": "15:40",
        "rows": [{"no": no, "tan": str(t), "fuku": f} for no, t, f in [(1, 12.4, '3.0-4.6'), (2, 4.1, '1.6-2.2'), (3, 31.5, '6.1-9.8'), (4, 9.8, '2.6-3.9'), (5, 18.2, '4.0-6.2'), (6, 2.4, '1.1-1.3'), (7, 7.6, '2.1-3.1'), (8, 54.0, '9.4-15.0'), (9, 25.9, '5.2-8.1'), (10, 6.3, '1.9-2.7'), (11, 14.7, '3.3-5.1'), (12, 88.6, '13.2-21.1'), (13, 40.2, '7.7-12.2'), (14, 120.5, '18.4-29.6')]]}
# にせもののアプリ：お願い（共有・コピー・バックアップ）を記録して、少しあとに返事をする
FAKE = """
window.__NATIVE_INFO = { version: '1.0', build: '7', device: 'phone' };
window.__bridge = [];
window.__ocrLines = [];   // 画像の文字の読み取り（Vision）のかわり：順に返す「読めた文字と位置」
window.__zoom = [];       // 拡大のお願い（{reset, lock}）
window.__notify = { auth: 'notDetermined', items: [], calls: [], opened: null };   // お知らせ（第2弾）
// App内課金のかわり：商品・買った結果・届いているのにまだ台帳に入れていない取引・終わらせた取引
window.__iap = { products: [
  { id: 'jp.tengel.app.points500', title: '500ポイント', price: '¥176', kind: 'pack' }, { id: 'jp.tengel.app.points1000', title: '1,000ポイント', price: '¥352', kind: 'pack' },
  { id: 'jp.tengel.app.points2000', title: '2,000ポイント', price: '¥704', kind: 'pack' }, { id: 'jp.tengel.app.points4000', title: '4,000ポイント', price: '¥1,408', kind: 'pack' },
  { id: 'jp.tengel.app.sub2000', title: '月2,000Pプラン', price: '¥638', kind: 'sub' }, { id: 'jp.tengel.app.sub4400', title: '月4,400Pプラン', price: '¥1,276', kind: 'sub' }, { id: 'jp.tengel.app.sub9200', title: '月9,200Pプラン', price: '¥1,914', kind: 'sub' }],
  buy: {}, unfinished: [], finished: [], current: [], active: [] };
window.webkit = { messageHandlers: { tengel: { postMessage: function (m) {
  window.__bridge.push({ name: m.name, payload: m.payload && m.payload.data ? { data: '(' + m.payload.data.length + ')' } : m.payload });
  var P = m.payload, val = true;
  if (m.name === 'backup') window.__saveBackup(P.text);
  if (m.name === 'share') val = !window.__shareCancel;
  if (m.name === 'ocr') { var L = window.__ocrLines.shift(); val = L ? { ok: true, lines: L, w: 1170, h: 2532, ms: 900 } : { ok: false, error: 'image_rejected' }; }
  if (m.name === 'zoom') { window.__zoom.push(P); val = { zoom: 1, pinch: !P.lock }; }
  if (m.name === 'iap') {
    var I = window.__iap;
    if (P.op === 'products') val = { ok: true, products: I.products };
    else if (P.op === 'buy') { var bf = I.buy[P.id]; val = typeof bf === 'function' ? bf() : (bf || { ok: false, state: 'cancelled' }); }
    else if (P.op === 'unfinished') val = { ok: true, list: I.unfinished };
    else if (P.op === 'finish') { I.finished.push(P.id); I.unfinished = I.unfinished.filter(function (t) { return String(t.id) !== String(P.id); }); val = { ok: true }; }
    else if (P.op === 'restore') val = { ok: true, current: I.current, unfinished: I.unfinished };
    else if (P.op === 'status') val = { ok: true, active: I.active };
    else val = { ok: false, error: 'unknown op' };
  }
  if (m.name === 'notify') {   // 結果確認のお知らせのかわり：許可の状態・入れ直した一覧・押されたお知らせ
    window.__notify = window.__notify || { auth: 'notDetermined', items: [], calls: [], opened: null }; var NN = window.__notify; NN.calls.push(P);
    if (P.op === 'status') val = { ok: true, auth: NN.auth };
    else if (P.op === 'permission') { NN.auth = NN.deny ? 'denied' : 'authorized'; val = { ok: true, granted: NN.auth === 'authorized', auth: NN.auth }; }
    else if (P.op === 'sync') { NN.items = P.items; val = { ok: true, scheduled: P.items.length, auth: NN.auth }; }
    else if (P.op === 'opened') { val = { ok: true, opened: NN.opened }; NN.opened = null; }
    else val = { ok: true, list: NN.items };
  }
  if (m.name === 'marker') {   // キーチェーンのかわり（Python側に持つので、開き直しても残る）
    window.__marker(P).then(function (v) { window.__nativeReply(m.id, true, v); });
    return;
  }
  setTimeout(function () { window.__nativeReply(m.id, true, val); }, 30);
} } } };
"""
OCR_DIR = os.path.join(W, 'testdata', 'ocr')
OCR_LINES = {k: json.load(open(os.path.join(OCR_DIR, k + '.json'), encoding='utf-8'))['lines'] for k in ('a_tanfuku_waku', 'c_sanrentan')}
store = {'backup': None, 'writes': 0, 'markers': {}}
# 結果の画面（にせもの）：6→2→10・払戻（単勝 240円・馬単 1,120円・3連単 12,340円）
RESULT_LINES = [{'text': t, 'x': 0.05, 'y': 0.05 + i * 0.035, 'w': 0.8, 'h': 0.025} for i, t in enumerate(['レース結果 第9競走', '着順 枠 馬番 馬名 性齢 斤量 騎手 タイム 人気', '1 3 6 ハナ 牡4 56.0 きしゅ 1:25.3 1', '2 1 2 フタ 牝3 54.0 きしゅ 1:25.5 2', '3 6 10 トオ 牡5 57.0 きしゅ 1:25.9 3', '4 2 4 ヨン 牡4 56.0 きしゅ 1:26.0 5',
    '払戻金', '単勝 6 240円 1人気', '複勝 6 120円', '馬連 2-6 530円', '馬単 6-2 1,120円', '3連単 6-2-10 12,340円'])]


def gate(pg):
    """アプリを開いた時の画面（19章）：はじめては「はじめる」を押す・2回目からは短い画面をタップ"""
    g = pg.locator('#gate')
    for _ in range(40):
        if not g.count() or g.evaluate('e => e.hidden'):
            return
        if pg.locator('#gateGo').count():
            pg.locator('#gateGo').click()
        else:
            try:
                g.click(timeout=500)
            except Exception:
                pass
        pg.wait_for_timeout(150)

try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP')

        def save_backup(source, text):
            store['backup'] = text; store['writes'] += 1
        ctx.expose_binding('__saveBackup', save_backup)

        def marker(source, p):
            op, key = p.get('op'), p.get('key')
            if op == 'set':
                store['markers'][key] = p.get('value', '1'); return {'ok': True}
            if op == 'del':
                store['markers'].pop(key, None); return {'ok': True}
            v = store['markers'].get(key)
            return {'ok': True, 'has': v is not None, 'value': v}
        ctx.expose_binding('__marker', marker)
        ctx.route('**/__native/autobackup.json', lambda route: route.fulfill(status=200, content_type='application/json', body=store['backup']) if store['backup'] else route.fulfill(status=404, body='not found'))
        ctx.add_init_script(FAKE)
        ctx.add_init_script("if (!sessionStorage.getItem('seeded')) { localStorage.setItem('tengel.form', %s); sessionStorage.setItem('seeded', '1'); }" % json.dumps(json.dumps(form, ensure_ascii=False)))
        outside = []   # アプリから外への通信（Google のフォントなど）
        ctx.on('request', lambda r: outside.append(r.url) if not r.url.startswith('http://localhost') and not r.url.startswith('data:') and not r.url.startswith('blob:') else None)
        pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(APPURL); pg.wait_for_timeout(1200)
        # ---- アプリを開いた時の画面（19章）：はじめては3つの文と「はじめる」。拡大は止めている ----
        g = pg.locator('#gate')
        gt = g.inner_text() if g.count() else ''
        check(g.count() == 1 and g.is_visible() and pg.locator('#gateGo').count() == 1 and '競馬の注意' in gt and 'アプリの注意' in gt and 'テンゲルの楽しみ方' in gt and '20歳未満' in gt and 'もどせません' in gt and 'お客様が自由に選べます' in gt,
              'はじめて開いた：競馬の注意・アプリの注意・楽しみ方と「はじめる」')
        vp0 = pg.evaluate("document.querySelector('meta[name=viewport]').content")
        check('maximum-scale=1' in vp0 and 'user-scalable=no' in vp0 and any(z.get('lock') for z in pg.evaluate('window.__zoom')), f'開いた時の画面の間は拡大を止める（{vp0}）')
        check(not [w for w in ('大井', 'JRA', 'まさちゃん') if w in gt], '開いた時の画面に出さない言葉がない')
        pg.screenshot(path=os.path.join(W, 't4', 'native_gate.png'))
        gate(pg); pg.wait_for_timeout(500)
        vp1 = pg.evaluate("document.querySelector('meta[name=viewport]').content")
        check(pg.evaluate("document.querySelector('#gate').hidden") and 'maximum-scale=3' in vp1 and 'user-scalable=no' not in vp1 and pg.evaluate('window.__zoom').pop().get('lock') is False and pg.evaluate("getComputedStyle(document.body).touchAction") == 'manipulation',
              f'「はじめる」→ 画面が開く・2本指で3倍まで拡大できる・ダブルタップでは拡大しない（{vp1}）')
        pg.reload(); pg.wait_for_timeout(600)
        g = pg.locator('#gate')
        check(g.count() == 1 and g.is_visible() and pg.locator('#gateGo').count() == 0 and '20歳' in g.inner_text(), '2回目から：短い注意だけ（タップでとばせる）')
        pg.wait_for_timeout(2400)
        check(pg.evaluate("document.querySelector('#gate').hidden"), '約2秒で自動で消える')
        pg.wait_for_timeout(600)
        st = pg.evaluate("({ native: window.__NATIVE, bridge: !!window.TengelNative, sw: !!(navigator.serviceWorker && navigator.serviceWorker.controller), info: window.TengelNative && window.TengelNative.info })")
        check(st['native'] and st['bridge'] and st['info']['version'] == '1.0', f'アプリ版として動く（{st}）')
        pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(300)
        fam = pg.evaluate("[...new Set([...document.fonts].filter(f => f.status === 'loaded').map(f => f.family.replace(/[\"']/g, '')))]")
        check({'BIZ UDPGothic', 'Dela Gothic One'} <= set(fam) and not [u for u in outside if 'fonts.g' in u], f'フォントはアプリの中のもの（{fam}）・Google に通信しない（{[u for u in outside if "fonts.g" in u][:2]}）')
        # ---- 設定タブ ----
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(500)
        up = pg.locator('#setUpdate')
        check(up.locator('h2').inner_text() == 'アプリの更新' and '1.0（7）' in up.inner_text() and pg.locator('#suCheck').count() == 0 and pg.locator('#nuCheck').count() == 1, '「アプリの更新」：版が出て、Web版の更新ボタン（version.json）はない・App Storeの版を確かめるボタンがある')
        check(pg.locator('#setData h2').inner_text() == 'データの更新', '「データの更新」のカードがある')
        check('アプリを削除すると' in up.inner_text() and 'ホーム画面のアイコン' not in up.inner_text(), 'アプリを削除すると記録が消える注意')
        check(pg.locator('#sbAuto').count() == 1 and '自動でバックアップ' in pg.locator('#setBackup').inner_text(), 'バックアップに「自動バックアップ」の欄')
        # ---- ポイント（4〜8章）：初回プレゼント 1,500P・カードの並び・Pカスタム・ミッション ----
        pg.wait_for_timeout(400)
        order = pg.evaluate("[...document.querySelectorAll('#v-set > .card')].slice(0, 3).map(c => c.id)")
        check(order == ['setPoints', 'setCustom', 'setMission'], f'設定タブの上に ポイント・Pカスタム・ミッション（{order}）')
        pt = pg.locator('#setPoints').inner_text()
        check(pg.evaluate('TengelWallet.total()') == 1500 and '1,500P' in pt and 'もらったP 1,500' in pt and store['markers'].get('gift-first'), f'はじめてのプレゼント 1,500P（もらったP）・キーチェーンにしるし（{list(store["markers"])}）')
        check('アプリを消すと、ポイント・解放したもの・記録はすべて消えて、もどせません' in pt and '200P' in pt and '買ったPから先に使う' in pt, 'ポイントのカード：消えることの注意・1レース200P・使う順')
        cu = pg.locator('#setCustom').inner_text()
        check('Pカスタムで、自分だけのテンゲルを育てよう！' in cu and 'はじめから：単勝・馬単・3連単' in cu and cu.count('500P') >= 6 and '15,000P' in cu and pg.locator('#setCustom [data-pt=unlock1]').count() == 8, 'Pカスタム：券種6つ（1つ500P）・マザーデータの枠2つ（15,000P）')
        ms = pg.locator('#setMission').inner_text()
        check('いま 0レース' in ms and '8レース記録' in ms and '500P' in ms and pg.locator('#setMission [data-pt=claim]').count() == 0, 'ミッション：0レース・次は8レースで500P')
        pg.locator('#setPoints [data-pt=show][data-v=buy]').click(); pg.wait_for_timeout(400)
        pt = pg.locator('#setPoints').inner_text()
        check(pg.locator('#setPoints [data-pt=buy]').count() == 4 and '¥352' in pt and '4,000P' in pt and '期限なし' in pt, '「ポイントを買う」：パック4つ・App Storeの値段')
        pg.locator('#setPoints [data-pt=show][data-v=sub]').click(); pg.wait_for_timeout(400)
        pt = pg.locator('#setPoints').inner_text()
        check(pg.locator('#setPoints [data-pt=buy]').count() == 3 and '月4,400Pプラン' in pt and 'うち 400P おまけ' in pt and '無料トライアルはないよ' in pt and '30日' in pt, '「サブスク」：3つ・おまけ・無料トライアルなし・30日')
        pg.locator('#setPoints [data-pt=show][data-v=sub]').click(); pg.wait_for_timeout(200)
        check(pg.locator('#slotList .slotrow.lock').count() == 2 and pg.locator('#slotList .slotrow.lock [data-gopt=custom]').count() == 2, 'マザーデータの2つ目・3つ目は🔒（Pカスタムで解放）')
        pg.screenshot(path=os.path.join(W, 't4', 'native_points.png'), full_page=False)
        pg.wait_for_timeout(1200)
        check(store['writes'] >= 1, f'開いたら自動バックアップを書く（{store["writes"]}回）')
        # ---- このアプリについて ----
        ab = pg.locator('#setAbout')
        last = pg.evaluate("[...document.querySelectorAll('#setExtra > .card')].pop().id")
        check(ab.count() == 1 and last == 'setAbout', f'設定タブのいちばん下に「このアプリについて」（{last}）')
        at = ab.inner_text()
        check('テンゲル 1.0（7）' in at and 'ご利用にあたって' in at and '約束するものではありません' in at and '馬券は20歳になってから' in at and '0120-683-705' in at, '版・ご利用にあたって（参考情報・20歳・相談先）')
        check(pg.locator('#setAbout a[href^="https://www.cas.go.jp"]').count() == 1 and pg.locator('#setAbout a[href="tel:0120683705"]').count() == 1, '相談窓口のリンクと電話')
        pg.locator('#abNotice summary').click(); pg.wait_for_timeout(100)
        nt = pg.locator('#abNotice').inner_text()
        check('非公式' in nt and '競馬の主催者・団体とは関係ありません' in nt and 'アイホン株式会社のライセンス' in nt and 'Anthropic' not in nt and 'JRA' not in nt and 'WIN5' not in nt,
              '非公式のアプリ・商標の表記（iPhone・Excel。App Store版は競馬の団体・商標の名前を出さない・Claudeも使わない）')
        pg.locator('#abPrivacy summary').click(); pg.wait_for_timeout(100)
        pv = pg.locator('#abPrivacy').inner_text()
        check('開発者が集めることも、受け取ることもありません' in pv and 'GitHub Pages' in pv and 'Google' not in pv and '自動バックアップ' in pv and 'Anthropic' not in pv and 'APIキー' not in pv and '端末の中（iOS・iPadOS の文字認識の機能）で読み取ります' in pv,
              'プライバシーポリシー（App Store版：Googleなし・自動バックアップ・CM・画像の読み取りは端末の中でAPIキーなし）')
        pg.locator('#abFonts summary').click(); pg.wait_for_timeout(100)
        fo = pg.locator('#abFonts').inner_text()
        check('BIZ UDPGothic' in fo and 'Dela Gothic One' in fo and 'IBM Plex Mono' in fo and 'SIL OPEN FONT LICENSE' in fo and 'Reserved Font Name "Plex"' in fo, 'フォントのライセンス（3つ・OFLの全文）')
        check(pg.locator('#abTokusho').count() == 0 and 'お問い合わせ' not in at, '販売する人の欄が空のうちは、特商法の表記・お問い合わせは出さない')
        # ---- 画像の読み取り：App Store版はAPIキーなし（端末の中の文字認識） ----
        oc = pg.locator('#setOcr')
        check(oc.count() == 1 and pg.locator('#soKey').count() == 0 and 'この端末の中' in oc.inner_text() and '料金もかからない' in oc.inner_text() and 'APIキー' not in oc.inner_text(),
              '「画像の読み取り」のカード：APIキーの欄がなく、端末の中で読む・無料と書いてある')
        seturl = pg.evaluate("[...document.querySelectorAll('#v-set .card')].filter(c => c.id !== 'setAbout').map(c => c.innerText).join('\\n')")
        check(not [w for w in ('まさちゃん', '姫に送', 'iPhone', 'LINE') if w in seturl], f'設定タブにお客さん向けでない言い方がない（{[w for w in ("まさちゃん", "姫に送", "iPhone", "LINE") if w in seturl]}）')
        bk0 = json.loads(store['backup'] or '{}')
        check(bk0.get('auto') is True and bk0.get('bets') == [], '最初の自動バックアップは記録0件')
        pg.screenshot(path=os.path.join(W, 't4', 'native_set.png'), full_page=False)
        # ---- 買い目を予約（第2弾・11章）→ 記録に入る → 自動バックアップ ----
        pg.click('.tabbar button[data-tab=judge]'); pg.wait_for_timeout(400)
        card = pg.locator('#recCard')
        ct = card.inner_text()
        check(card.locator('h2').inner_text() == '買い目' and pg.locator('#saveJudge').count() == 0 and card.locator('[data-rsv=reserve]').count() == 1 and card.locator('[data-rsv=give]').count() == 1 and '発走 15:40 → 15:55 にお知らせ' in ct and card.locator('[data-k=rtypes] button').count() == 9 and card.locator('[data-k=rzones] button').count() == 2,
              '判定画面の下は「買い目」のカード：券種9つ・ゾーン2つ・「買い目を予約」「このレースを諦める」・お知らせの時刻（「判定と結果を保存」はない）')
        pct = [t for t in pg.locator('#result .zref').all_inner_texts() if '選んだ馬で' in t]
        check(len(pct) == 2 and '6.5%' in pct[0] and '3連単 5.4%' in pct[0] and 'ゾーンと同じ' in pct[0] and '7.6%' in pct[1], f'ゾーンごとに「選んだ馬で ○%」（全部選んだ時はゾーンの値：{pct[0][:40]}）')
        check(pg.locator('#omakaseBtn').count() == 1 and pg.locator('#result .rnav').count() == 0, '「テンゲルにお任せ」がある・1つ前のレースはまだない（矢印なし）')
        pg.locator('#result .hp[data-no="6"][data-hs="b"]').first.click(); pg.wait_for_timeout(300)
        pct2 = [t for t in pg.locator('#result .zref').all_inner_texts() if '選んだ馬で' in t]
        check('6.5%' not in pct2[0] and 'ゾーンと同じ' not in pct2[0], f'馬を外すと%がかわる（{pct2[0][:30]}）')
        card.locator('details[data-k=betsee] summary').click(); pg.wait_for_timeout(200)
        bl = card.locator('.betlist').inner_text()
        check('馬単' in bl and '3連単' in bl and '→' in bl and '合計' in card.locator('.rsvnote').first.inner_text() and '点' not in pg.locator('#result').inner_text(), '「買い目を確認」：券種ごとの組と点数（点数はここだけ・判定の画面には出ない）')
        n0 = store['writes']; card.locator('[data-rsv=reserve]').click(); pg.wait_for_timeout(900)
        check(pg.evaluate('TengelLocal.mem.bets.size') == 1 and pg.evaluate("[...TengelLocal.mem.bets.values()][0].rsv.state") == 'reserved' and pg.evaluate("[...TengelLocal.mem.bets.values()][0].rsv.types.join()") == '馬単,3連単', '「買い目を予約」→ 記録（bets）に rsv（予約中・馬単と3連単）が入る')
        nn = pg.evaluate('window.__notify')
        check([c['op'] for c in nn['calls']][-3:] == ['status', 'permission', 'sync'] and nn['auth'] == 'authorized' and len(nn['items']) == 1 and nn['items'][0]['body'] == '大井 8R はなまる特別' and nn['items'][0]['title'] == '結果を確認しよう！', f'最初の予約で通知を許可 → 発走15分後のお知らせを入れる（{nn["items"][0]["body"] if nn["items"] else "なし"}）')
        import datetime as _dt
        check(nn['items'] and _dt.datetime.utcfromtimestamp(nn['items'][0]['at'] / 1000).strftime('%Y-%m-%d %H:%M') == '2026-10-10 06:55', 'お知らせの時刻＝発走15:40（日本時間）の15分後')
        check('予約ずみ（結果待ち）' in card.inner_text() and card.locator('[data-rsv=cancel]').count() == 1 and card.locator('[data-rsv=redo]').count() == 1, '予約ずみのカード（結果を入れる・予約し直す・予約を消す）')
        check(store['writes'] == n0, 'すぐには書かない（少し待ってまとめて書く）')
        pg.wait_for_timeout(1600)
        bk = json.loads(store['backup'])
        check(store['writes'] == n0 + 1 and len(bk['bets']) == 1 and bk['bets'][0]['id'].startswith('20261010') and bk['bets'][0]['rsv']['state'] == 'reserved', f'予約した記録が自動バックアップに入る（{store["writes"] - n0}回）')
        # APIキーはバックアップに入れない
        pg.evaluate("TengelLocal.ocr.save('sk-ant-test-secret-key', 'std')"); pg.wait_for_timeout(1900)
        check('sk-ant-test-secret-key' not in (store['backup'] or ''), 'APIキーは自動バックアップに入らない')
        pg.evaluate("TengelLocal.ocr.clear()")
        # ---- 画像の読み取り（端末の中）：スクショ2枚（単勝・複勝＋3連単の人気順）→ 入力欄に入る。外には何も送らない ----
        pg.evaluate("window.__ocrLines = %s; window.__bridge = []" % json.dumps([OCR_LINES['a_tanfuku_waku'], OCR_LINES['c_sanrentan']], ensure_ascii=False))
        n_out = len(outside)
        check(pg.locator('#ocrRow').is_visible() and pg.evaluate("typeof window.TengelOCR === 'object' && !!window.TengelOCR.parse"), '「オッズ画像から読み取る」が出ている・表を組み立てる仕組みが入っている')
        pg.locator('#ocrBtn').click(); pg.wait_for_timeout(200)
        check('APIキー' not in pg.locator('#ocrMsg').inner_text(), '押してもAPIキーの案内は出ない（写真を選ぶ）')
        pg.set_input_files('#ocrFile', [os.path.join(OCR_DIR, 'a_tanfuku_waku.jpg'), os.path.join(OCR_DIR, 'c_sanrentan.jpg')]); pg.wait_for_timeout(2500)
        calls = [x for x in pg.evaluate('window.__bridge') if x['name'] == 'ocr']
        got = pg.evaluate("(() => { const f = JSON.parse(localStorage.getItem('tengel.form')); return { venue: document.querySelector('#fVenue').value, r: document.querySelector('#fR').value, dist: document.querySelector('#fDist').value, n: document.querySelector('#fN').value, baba: f.baba, surface: f.surface, rows: f.rows.length, tan6: (f.rows.find(x => x.no === 6) || {}).tan, fuku6: (f.rows.find(x => x.no === 6) || {}).fuku, s1: f.s1, s1c: f.s1combo, s5: f.s5, s10: f.s10, msg: document.querySelector('#ocrMsg').innerText }; })()")
        print('   読み取り:', got)
        check(len(calls) == 2 and all(c['payload']['data'].startswith('(') for c in calls), f'画像2枚をアプリ（端末の中の文字認識）に渡した（{len(calls)}回）')
        check(got['venue'] == '大井' and got['r'] == '9' and got['dist'] == '1400' and got['n'] == '12' and got['baba'] == '良' and got['surface'] == 'ダ', f'レース情報が入力欄に入る（{got["venue"]} {got["r"]}R {got["dist"]}m {got["n"]}頭 {got["baba"]}）')
        check(got['rows'] == 12 and got['tan6'] == '2.4' and got['fuku6'] == '1.1-1.3' and got['s1'] == '18.5' and got['s1c'] == '6-2-10' and got['s5'] == '41.3' and got['s10'] == '84', '単勝・複勝12頭と3連単1位・5位・10位が入る')
        check('読み取った' in got['msg'] and '単勝12頭' in got['msg'] and '読めなかった' not in got['msg'], f'読み取れたもののお知らせ（{got["msg"][:60]}）')
        check(len(outside) == n_out, '読み取りで外に通信しない')
        # 何も読めない画像（表がない）→ いまの入力はそのまま
        pg.evaluate("window.__ocrLines = [[{ text: 'ようこそ', x: 0.1, y: 0.1, w: 0.3, h: 0.03 }]]")
        pg.set_input_files('#ocrFile', [os.path.join(OCR_DIR, 'c_sanrentan.jpg')]); pg.wait_for_timeout(1500)
        check('見つからなかった' in pg.locator('#ocrMsg').inner_text() and pg.evaluate("JSON.parse(localStorage.getItem('tengel.form')).rows.length") == 12 and pg.locator('#fR').input_value() == '9', '表のない画像：案内を出して、いまの入力はそのまま')
        pg.screenshot(path=os.path.join(W, 't4', 'native_ocr.png'), full_page=False)
        # ---- 読み込みで 200P を使う・同じレースの読み直しは 0P・券種の🔒・マザーデータの🔒 ----
        check(pg.evaluate('TengelWallet.total()') == 1300 and '200P 使ったよ' in got['msg'] and '1レース 200P' in pg.locator('#ocrHint').inner_text(), f'読み込みで200P使った（残り {pg.evaluate("TengelWallet.total()")}P）・ボタンの横に残りのP')
        pid = pg.evaluate("JSON.parse(localStorage.getItem('tengel.form')).pid")
        check(bool(pid) and pg.evaluate("TengelWallet.events().filter(e => e.kind === 'spend').length") == 1, '読み込んだしるし（pid）が入力に残る')
        pg.evaluate("window.__ocrLines = %s" % json.dumps([OCR_LINES['a_tanfuku_waku']], ensure_ascii=False))
        pg.set_input_files('#ocrFile', [os.path.join(OCR_DIR, 'a_tanfuku_waku.jpg')]); pg.wait_for_timeout(1800)
        check(pg.evaluate('TengelWallet.total()') == 1300 and '0P' in pg.locator('#ocrMsg').inner_text() and pg.evaluate("JSON.parse(localStorage.getItem('tengel.form')).pid") == pid, '同じレースをもう一度読んでも 0P（同じ pid）')
        check(pg.locator('#fRname').is_visible() and pg.locator('#fStart').input_value() == '18:05', '発走時刻（18:05）が入る・レース名の欄がある')
        # 別のレース（10R）を読む → また200P
        def lines_r(src, r):
            return [dict(l, text=l['text'].replace('第9競走', f'第{r}競走').replace('9R', f'{r}R')) for l in src]
        pg.evaluate("window.__ocrLines = %s" % json.dumps([lines_r(OCR_LINES['a_tanfuku_waku'], 10)], ensure_ascii=False))
        pg.set_input_files('#ocrFile', [os.path.join(OCR_DIR, 'a_tanfuku_waku.jpg')]); pg.wait_for_timeout(1800)
        check(pg.evaluate('TengelWallet.total()') == 1100 and pg.locator('#fR').input_value() == '10' and pg.evaluate("JSON.parse(localStorage.getItem('tengel.form')).pid") != pid, '別のレース（10R）を読むと また200P・新しい pid')
        # 9Rに戻して記録 → ミッションに数える（200Pを使ったレース）
        pg.evaluate("window.__ocrLines = %s" % json.dumps([OCR_LINES['a_tanfuku_waku']], ensure_ascii=False))
        pg.set_input_files('#ocrFile', [os.path.join(OCR_DIR, 'a_tanfuku_waku.jpg')]); pg.wait_for_timeout(1800)
        check(pg.evaluate('TengelWallet.total()') == 1100 and pg.locator('#fR').input_value() == '9', '9Rに戻しても 0P（払ったレース）')
        check(pg.locator('#result .rnav').count() == 1 and '前のレース（大井10R）' in pg.locator('#result .rnav').inner_text() and pg.locator('#result [data-rnav=next]').is_disabled(), '1つ前のレース（10R）に戻る矢印が出る')
        card = pg.locator('#recCard')
        tb = card.locator('[data-k=rtypes] button')
        check(tb.count() == 9 and card.locator('[data-k=rtypes] button.lock').count() == 6 and card.locator('[data-k=rtypes] button[data-v=枠複]').count() == 1 and card.locator('[data-k=rtypes] button[data-v=単勝]:not(.lock)').count() == 1,
              '券種は9つ（枠複・枠単も）。単勝・馬単・3連単のほかは🔒')
        card.locator('[data-k=rtypes] button[data-v=複勝]').click(); pg.wait_for_timeout(200)
        check(card.locator('[data-k=rtypes] button[data-v=複勝]').get_attribute('aria-pressed') == 'false' and 'Pカスタム' in pg.locator('#toast').inner_text(), '🔒の券種は選べない（Pカスタムの案内）')
        chips = pg.locator('#slotJudge .slotchip')
        check(chips.count() == 3 and pg.locator('#slotJudge .slotchip.lock').count() == 2, '判定画面のマザーデータの切り替えも 2・3は🔒')
        pg.locator('#slotJudge .slotchip.lock').first.click(); pg.wait_for_timeout(200)
        check('Pカスタム' in pg.locator('#toast').inner_text() and pg.evaluate('TengelLocal.slots.active()') == 1, '🔒の枠は使えない（Pカスタムの案内）')
        card.locator('[data-k=rtypes] button[data-v=単勝]').click(); pg.wait_for_timeout(200)
        card.locator('[data-k=rtypes] button[data-v="3連単"]').click(); pg.wait_for_timeout(200)
        card.locator('[data-rsv=reserve]').click(); pg.wait_for_timeout(900)
        b9 = pg.evaluate("[...TengelLocal.mem.bets.values()].find(b => b.r === 9) || null")
        check(b9 and b9.get('pid') == pid and b9.get('start') == '18:05' and b9['rsv']['types'] == ['単勝', '馬単'] and pg.evaluate('TengelWallet.countedN()') == 1, f'9Rを予約（単勝・馬単）：記録に pid・発走時刻が入る・ミッションに1レース数えた（{pg.evaluate("TengelWallet.countedN()")}）')
        check(pg.evaluate('TengelLocal.mem.bets.size') == 2 and len(pg.evaluate('window.__notify.items')) == 2, '最初の8R（200Pを使っていない）は数えない・お知らせは2件（8R・9R）')
        # ---- 一つ前のレース（11.3）：← で 10R に戻る・→ で 9R へ。ポイントは使わない ----
        pg.locator('#result [data-rnav=prev]').click(); pg.wait_for_timeout(400)
        check(pg.locator('#fR').input_value() == '10' and '1つ前のレース（大井10R）を見ています' in pg.locator('#result .rnav').inner_text() and pg.locator('#result [data-rnav=prev]').is_disabled() and pg.evaluate('TengelWallet.total()') == 1100, '← 前のレース → 10R（ポイントは使わない）')
        pg.locator('#recCard [data-rsv=give]').click(); pg.wait_for_timeout(700)
        b10 = pg.evaluate("[...TengelLocal.mem.bets.values()].find(b => b.r === 10) || null")
        check(b10 and b10['rsv']['state'] == 'given' and '諦めたレース' in pg.locator('#recCard').inner_text() and pg.evaluate('TengelWallet.countedN()') == 2, '戻った10Rを「このレースを諦める」→ 諦めたレース・ミッションに数える（2レース）')
        pg.locator('#result [data-rnav=next]').click(); pg.wait_for_timeout(400)
        check(pg.locator('#fR').input_value() == '9' and 'いまのレース' in pg.locator('#result .rnav').inner_text(), '次のレース → 9R に戻る')
        # ---- テンゲルにお任せ：ゾーンの中からランダム・頭一つ残し ----
        pg.locator('#omakaseBtn').click(); pg.wait_for_timeout(300)
        hp = pg.evaluate("JSON.parse(localStorage.getItem('tengel.form')).hp")
        allok = pg.evaluate("(() => { const f = JSON.parse(localStorage.getItem('tengel.form')); return Object.values(f.hp || {}).every(z => Object.values(z).every(a => Array.isArray(a) && a.length >= 1)); })()")
        check(allok and 'お任せで選んだよ' in pg.locator('#toast').inner_text(), f'テンゲルにお任せ：側ごとに1頭以上（{json.dumps(hp, ensure_ascii=False)[:60]}）')
        pg.locator('#recCard [data-rsv=redo]').click(); pg.wait_for_timeout(300)
        pg.locator('#recCard [data-rsv=reserve]').click(); pg.wait_for_timeout(900)
        b9b = pg.evaluate("[...TengelLocal.mem.bets.values()].find(b => b.r === 9)")
        check(pg.evaluate('TengelLocal.mem.bets.size') == 3 and b9b['rsv']['hp'] == hp and pg.evaluate('TengelWallet.countedN()') == 2, '選び直して予約し直す → 同じレースは1つ（上書き）・ミッションは1回のまま')
        # 全部選んだ状態（単勝・馬単）で予約し直す（結果のテストを決まった形にするため）
        pg.evaluate("(() => { const f = JSON.parse(localStorage.getItem('tengel.form')); f.hp = null; localStorage.setItem('tengel.form', JSON.stringify(f)); })()")
        pg.reload(); pg.wait_for_timeout(700); gate(pg); pg.wait_for_timeout(1200)
        pg.locator('#recCard [data-rsv=redo]').click(); pg.wait_for_timeout(300)
        pg.locator('#recCard [data-rsv=reserve]').click(); pg.wait_for_timeout(900)
        b9c = pg.evaluate("[...TengelLocal.mem.bets.values()].find(b => b.r === 9)")
        check(b9c['rsv']['points'] == 18 and b9c['stake'] == 1800 and len(b9c['rsv']['bets']['単勝']) == 3 and len(b9c['rsv']['bets']['馬単']) == 15, f'A層（人気→人気・人気→中穴）全部で 単勝3点・馬単15点（{b9c["rsv"]["points"]}点・{b9c["stake"]}円）')
        # ---- 記録タブ：予約レース／諦めたレースの欄 → 結果入力（結果の画像・払戻）→ 券種ごとの結果（12章） ----
        pg.click('.tabbar button[data-tab=rec]'); pg.wait_for_timeout(600)
        top = pg.locator('#recList .rsvtop')
        tt = top.inner_text() if top.count() else ''
        check(top.count() == 1 and '予約レース' in tt and '結果待ち 2件' in tt and '諦めたレース（1件）' in tt and top.locator('.lrow').count() == 3 and pg.locator('#recList .dgroup').count() == 0, f'記録タブの上に 予約レース（8R・9R）と 諦めたレース（10R）。月の一覧には出ない（{tt[:40]}）')
        top.locator(f'.lrow[data-id="{b9c["id"]}"] .lmain').click(); pg.wait_for_timeout(500)
        f9 = pg.locator('#recList .rsvf')
        check(f9.count() == 1 and f9.locator('[data-k=p1]').count() == 1 and f9.locator('[data-k=res]').count() == 0 and f9.locator('details[data-k=betsee]').count() == 1 and f9.locator('[data-k=stake][data-t="単勝"]').input_value() == '300' and f9.locator('[data-k=stake][data-t="馬単"]').input_value() == '1500' and '結果待ち' in f9.locator('[data-k=status]').inner_text(),
              '結果入力の欄：1〜3着の馬番・買い目は出さない（「買い目を確認」で見る）・購入額は点数×100円・結果待ち')
        pg.evaluate("window.__ocrLines = %s" % json.dumps([RESULT_LINES], ensure_ascii=False))
        f9.locator('[data-k=rimgfile]').set_input_files([os.path.join(OCR_DIR, 'c_sanrentan.jpg')]); pg.wait_for_timeout(1800)
        vals = {k: f9.locator(f'[data-k={k}]').input_value() for k in ('p1', 'p2', 'p3', 'cancel')}
        check(vals == {'p1': '6', 'p2': '2', 'p3': '10', 'cancel': ''} and '読み取った' in f9.locator('[data-k=hint]').inner_text() and '1着 6（1番人気）' in f9.locator('[data-k=plab]').inner_text(), f'結果の画像から 1〜3着の馬番が入る（{vals}）')
        check(f9.locator('[data-k=payout][data-t="単勝"]').input_value() == '240' and f9.locator('[data-k=payout][data-t="馬単"]').input_value() == '1120' and '的中' in f9.locator('[data-k=status]').inner_text() and f9.locator('.betlist .hitc').count() == 2, '当たった組（単勝 6・馬単 6→2）の払戻が入る・的中')
        pg.evaluate("window.__fxEv = []; document.addEventListener('tengel:fx', e => window.__fxEv.push(e.detail.phase + ':' + e.detail.kind))")
        f9.locator('[data-act=rsave]').click(); pg.wait_for_timeout(1200)
        b9d = pg.evaluate("[...TengelLocal.mem.bets.values()].find(b => b.r === 9)")
        check(b9d['rsv']['state'] == 'done' and b9d['rsv']['judged']['state'] == '的中' and b9d['rsv']['judged']['per'] == {'単勝': '的中', '馬単': '的中'} and [b9d['n1'], b9d['n2'], b9d['n3']] == [6, 2, 10] and [b9d['p1'], b9d['p2'], b9d['p3']] == [1, 2, 3] and b9d['payout'] == 1360 and b9d['stake'] == 1800, '保存 → 券種ごとに的中・着順（馬番と人気）・払戻の合計が記録に入る')
        # ---- 的中ボタン（第3弾・10章）：単勝・馬単の当たり（3連単なし）→ 的中の PUSH → タップ → いつものボード（券種ごとの結果・お金なし）→ とじる ----
        ov = pg.locator('#fxOv')
        sx = pg.evaluate('TengelFx.sfxState()')
        check(ov.count() == 1 and ov.locator('.fxs .ov .push').count() == 1 and ov.locator('.push.big').count() == 0 and pg.evaluate('TengelFx.current()') == {'kind': 'hit', 'phase': 'push', 'quiet': False} and pg.evaluate('document.documentElement.classList.contains("fxon")') and pg.evaluate('window.__zoom').pop().get('lock') is True,
              f'保存 → 的中の PUSH が出る（3連単なしの当たり＝的中）・拡大は止める（{pg.evaluate("TengelFx.current()")}）')
        check(sx['ctx'] and sx['fetched'] and 'sfx_hit_push.m4a' in pg.evaluate("performance.getEntriesByType('resource').map(e => e.name).join()"), f'「結果を保存」を押したときに音の準備（AudioContext・音のファイルを読む）（{sx}）')
        check(pg.locator('#toast').is_hidden() or '保存できたよ' not in pg.locator('#toast').inner_text(), '演出が出るときは、お知らせの帯は出さない（ボードが結果を見せる）')
        check('保存できたよ（的中）' in f9.locator('[data-k=savemsg]').inner_text() and '単勝 的中' in f9.locator('[data-k=savemsg]').inner_text(), '欄の下には 保存できたよ（券種ごとの結果）')
        ov.locator('.push').click(force=True); pg.wait_for_timeout(2300)
        rb = ov.locator('.rb')
        rows = ov.locator('.rb .brows li')
        check(ov.locator('.fxs .ov.hit').count() == 1 and rb.count() == 1 and 'hit' in rb.get_attribute('class') and 't-default' in rb.get_attribute('class') and rb.locator('.bh').inner_text() == '的中！' and rb.locator('.bsub').inner_text() == '9R の券種ごとの結果',
              f'タップ → 的中の演出 → いつものボード「的中！」「9R の券種ごとの結果」（{rb.locator(".bh").inner_text()}）')
        check(rows.count() == 2 and rows.nth(0).locator('.bt').inner_text() == '単勝' and rows.nth(0).locator('.rs').inner_text() == '的中' and rows.nth(0).locator('.bc .n').all_inner_texts() == ['6'] and rows.nth(1).locator('.bt').inner_text() == '馬単' and rows.nth(1).locator('.bc .n').all_inner_texts() == ['6', '2'] and rows.nth(1).locator('.bc .ar').inner_text() == '→' and '円' not in rb.inner_text() and rb.locator('.btot').count() == 0,
              f'ボードの行は 券種ごと（単勝 的中 6・馬単 的中 6→2）・お金は出さない（{rb.inner_text()[:60]!r}）')
        check(pg.evaluate('window.__fxEv') == ['push:hit', 'reveal:hit'], f'合図：push → reveal（{pg.evaluate("window.__fxEv")}）')
        ov.locator('.close').click(force=True); pg.wait_for_timeout(400)
        b9e = pg.evaluate("[...TengelLocal.mem.bets.values()].find(b => b.r === 9)")
        check(pg.locator('#fxOv').count() == 0 and pg.evaluate('TengelFx.current()') is None and not pg.evaluate('document.documentElement.classList.contains("fxon")') and pg.evaluate('window.__zoom').pop().get('lock') is False and b9e['rsv'].get('fx') == 'hit',
              f'「とじる」→ 記録の画面にもどる・拡大できる・記録に出した印（rsv.fx）（{b9e["rsv"].get("fx")}）')
        # 同じ記録を保存し直しても、もう出さない（あとで記録を直したとき）
        f9.locator('[data-act=rsave]').click(); pg.wait_for_timeout(900)
        check(pg.locator('#fxOv').count() == 0 and '保存できたよ' in pg.locator('#toast').inner_text(), '結果を記録ずみの記録を保存し直す → 演出は出ない（お知らせの帯だけ）')
        pg.wait_for_timeout(500)
        # どれが出るか（10章・18.2）：3連単の当たりの3頭に 10〜12番人気 → ど的中／9番人気・13番人気・人気がわからない → デカ／3連単なし → 的中／当たりなし → ハズレ
        RK = {str(i): i for i in range(1, 15)}   # 馬番＝人気順位（18.2 の例と同じ読み方）
        def spec(tri, others=(), ranks=RK):
            rows = [{'t': '3連単', 'state': '的中' if tri else '不的中', 'hits': [tri] if tri else [], 'n': 18}] + [{'t': t, 'state': st_, 'hits': h, 'n': 9} for t, st_, h in others]
            return {'r': 9, 'n': 14, 'rows': rows, 'ranks': ranks}
        D = lambda sp: pg.evaluate("(s) => { const d = TengelFx.decide(s); return d.kind + (d.supers.length ? ':' + d.supers.map(x => x.no + '/' + x.rank).join(',') : ''); }", sp)
        got = [D(spec([11, 8, 2])), D(spec([11, 12, 2])), D(spec([11, 6, 2])), D(spec([8, 5, 2])), D(spec([13, 8, 2])), D(spec([1, 6, 2])), D(spec([11, 6, 99])), D(spec(None, [('馬単', '的中', [[6, 2]])])), D(spec(None, [('馬単', '不的中', [])])), D(spec(None, [('馬単', '返還', [])]))]
        check(got == ['fz:11/11', 'fz:11/11,12/12', 'fz:11/11', 'big', 'big', 'big', 'big', 'hit', 'miss', 'miss'], f'どれが出るか：11・8・2／11・12・2／11・6・2 → ど的中（超大穴の馬番と人気）・8・5・2／13・8・2／1・6・2／人気がわからない馬 → デカ・3連単なし → 的中・当たりなし → ハズレ（{got}）')
        # 隠れど的中（※仮）：デカ的中の 2〜7回に1回（乱数を固定して 2回目）。本物のど的中は数えない。数は端末の中（localStorage）だけ・バックアップには入れない
        pg.evaluate("localStorage.removeItem('tengel.fxhidden'); TengelFx._rand = () => 0")
        seq = []
        for tri in ([8, 5, 2], [8, 5, 2], [11, 6, 2], [8, 5, 2], [8, 5, 2]):
            seq.append(pg.evaluate("(s) => TengelFx.show(s)", spec(tri))); pg.wait_for_timeout(150)
            if seq[-1] == 'hidden':
                hp = pg.locator('#fxOv')
                check(hp.locator('.push.big').count() == 1 and pg.evaluate('TengelFx.current()')['kind'] == 'hidden', '隠れど的中：見た目はデカの PUSH')
                hp.locator('.push').click(force=True); pg.wait_for_timeout(500)
                check(hp.locator('.fxs .ov.fz').count() == 1 and hp.locator('.rb.fz .bh').text_content() == '隠れど的中！！！' and '隠れ' in hp.locator('.rb .zrib').text_content() and hp.locator('.rb .brows li.top .bt').text_content() == '3連単', '隠れど的中：押すと ど的中の演出 → 見出し「隠れど的中！！！」・帯「隠れ」・3連単の行がいちばん上')
            pg.evaluate('TengelFx.close()'); pg.wait_for_timeout(100)
        hs = pg.evaluate("JSON.parse(localStorage.getItem('tengel.fxhidden'))")
        check(seq == ['big', 'hidden', 'fz', 'big', 'hidden'] and hs == {'c': 0, 'n': 2}, f'隠れど的中の数え方：デカ→隠れ（2回目）→ど的中（数えない）→デカ→隠れ（{seq}・{hs}）')
        pg.evaluate("TengelFx._rand = null")
        pg.wait_for_timeout(1900)
        check('fxhidden' not in (store['backup'] or '') and 'fxhidden' not in pg.evaluate("JSON.stringify([...TengelLocal.mem.bets.values()])"), '隠れど的中の数は 記録・自動バックアップに入らない')
        # ど的中：虹色の超デカ PUSH → 押した瞬間にフリーズ → 結果（超大穴の帯・3連単の行の超大穴の馬番に輪）
        pg.evaluate("(s) => TengelFx.show(s)", spec([11, 6, 2], [('馬単', '的中', [[11, 6], [6, 2]]), ('ワイド', '不的中', [])])); pg.wait_for_timeout(200)
        fo = pg.locator('#fxOv')
        check(fo.locator('.push.fz').count() == 1 and fo.locator('.tap.fz').inner_text() == 'タップ!!' and 'k-fz' in fo.get_attribute('class'), 'ど的中：虹色の超デカ PUSH（タップ!!）')
        fo.locator('.push').click(force=True); pg.wait_for_timeout(300)
        check(fo.locator('.fxs .ov.fz .pc').count() == 1 and fo.locator('.fxs .ov.fz .mt .sc').count() == 5 and fo.locator('.fxs .ov.fz .fin .dlg').count() == 1 and fo.locator('.rb.fz').count() == 1,
              'ど的中の押したあと：フリーズ（.pc）・ネオンのカット5つ・結果（ど的中の筆の字・ボード）が重なっている')
        zx = fo.locator('.rb .brows li.top .n.zx')
        check(fo.locator('.rb.fz .bh').text_content() == 'ど的中！！！' and '超大穴' in fo.locator('.rb .zrib').text_content() and '11番人気が3連単に！' in fo.locator('.rb .zrib').text_content() and zx.count() == 1 and zx.text_content() == '11' and fo.locator('.rb .brows li').nth(1).locator('.bc').count() == 2,
              f'ど的中のボード（結果の画面は6.9秒から）：「ど的中！！！」・帯「超大穴 11 11番人気が3連単に！」・3連単の 11 に虹色の輪・馬単の当たり2つ（{fo.locator(".rb .zrib").text_content()}）')
        pg.evaluate('TengelFx.close()'); pg.wait_for_timeout(100)
        # 設定：的中エフェクト オフ → PUSH・演出なしでボードだけ静かに／演出を控えめにする → .calm／効果音
        pg.evaluate("TengelFx.set({ effects: false })"); pg.wait_for_timeout(100)
        k = pg.evaluate("(s) => TengelFx.show(s)", spec([8, 5, 2])); pg.wait_for_timeout(300)
        qo = pg.locator('#fxOv')
        check(k == 'big' and qo.locator('.push').count() == 0 and qo.locator('.fxs .ov.miss.quiet').count() == 1 and qo.locator('.rb.big .bh').inner_text() == 'デカ的中!!' and pg.evaluate('TengelFx.current()')['quiet'] is True and pg.evaluate("JSON.parse(localStorage.getItem('tengel.fxhidden'))") == {'c': 0, 'n': 2},
              '的中エフェクト オフ：PUSH・演出なしで、ボード（見出しは当たりの強さのまま）だけ静かに・隠れど的中のくじはひかない')
        pg.evaluate('TengelFx.close()')
        pg.evaluate("TengelFx.set({ effects: true, calm: true })"); pg.wait_for_timeout(100)
        pg.evaluate("(s) => TengelFx.show(s)", spec([11, 6, 2])); pg.wait_for_timeout(200)
        check(pg.locator('#fxOv .fxs.calm .push.fz').count() == 1 and pg.evaluate("getComputedStyle(document.querySelector('#fxOv .push.fz')).animationName") == 'none', '演出を控えめにする：PUSHの動きが止まる（視差効果を減らすと同じ形）')
        pg.evaluate('TengelFx.tap()'); pg.wait_for_timeout(200)
        check(pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.fz .pc')).display") == 'none' and pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.fz .mt')).display") == 'none', '控えめ：フリーズ・ネオンのカットは出さない（1秒真っ暗 → 結果をふわっと）')
        pg.evaluate('TengelFx.close()')
        pg.evaluate("TengelFx.set({ calm: null })")
        sv = pg.evaluate("TengelLocal.getSetting('fx')")
        check(sv == {'effects': True, 'calm': None, 'sound': True} and pg.evaluate('TengelFx.calm()') is False, f'設定は保存される（{sv}）')
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(500)
        fc = pg.locator('#setFx')
        check(fc.count() == 1 and fc.locator('.seg[data-fx]').count() == 3 and fc.locator('.seg[data-fx=effects] button[data-v="1"]').get_attribute('aria-pressed') == 'true' and fc.locator('.seg[data-fx=calm] button[data-v="0"]').get_attribute('aria-pressed') == 'true' and fc.locator('.seg[data-fx=sound] button[data-v="1"]').get_attribute('aria-pressed') == 'true' and pg.evaluate("document.querySelector('#setNotify').nextElementSibling.id") == 'setFx',
              '設定に「的中の演出」（的中エフェクト オン・控えめ オフ・効果音 オン）が、お知らせのカードの次にある')
        fc.locator('.seg[data-fx=sound] button[data-v="0"]').click(); pg.wait_for_timeout(300)
        check(pg.evaluate("TengelLocal.getSetting('fx')")['sound'] is False and '効果音をオフ' in pg.locator('#toast').inner_text() and fc.locator('.seg[data-fx=sound] button[data-v="0"]').get_attribute('aria-pressed') == 'true', '効果音 オフ → 保存・お知らせ')
        fc.locator('.seg[data-fx=sound] button[data-v="1"]').click(); pg.wait_for_timeout(200)
        pg.click('.tabbar button[data-tab=rec]'); pg.wait_for_timeout(400)
        tt2 = pg.locator('#recList .rsvtop').inner_text()
        check('結果待ち 1件' in tt2 and pg.locator('#recList .dgroup').count() == 1 and len(pg.evaluate('window.__notify.items')) == 1 and pg.evaluate('window.__notify.items')[0]['race'] != b9c['id'], '結果を記録した9Rは月の一覧へ・予約レースは8Rだけ・9Rのお知らせは消える')
        # 押されたお知らせ → そのレースの結果入力へ
        b8id = pg.evaluate("[...TengelLocal.mem.bets.values()].find(b => b.r === 8).id")
        pg.click('.tabbar button[data-tab=judge]'); pg.wait_for_timeout(300)
        pg.evaluate("window.__nativeEvent('notify', { race: %s })" % json.dumps(b8id)); pg.wait_for_timeout(600)
        check(pg.locator('#v-rec').is_visible() and pg.locator(f'#recList .lrow[data-id="{b8id}"] .rsvf').count() == 1, 'お知らせを押す → 記録タブで そのレース（8R）の結果入力が開く')
        # 諦めたレース → やっぱり予約する
        pg.locator('#recList .rsvtop details.given summary').click(); pg.wait_for_timeout(200)
        pg.locator(f'#recList .lrow[data-id="{b10["id"]}"] [data-act=load]').click(); pg.wait_for_timeout(600)
        check(pg.locator('#v-judge').is_visible() and pg.locator('#fR').input_value() == '10' and pg.locator('#recCard [data-rsv=redo]').inner_text() == 'やっぱり予約する', '諦めたレース →「やっぱり予約する」→ 判定画面で10R')
        pg.locator('#recCard [data-rsv=redo]').click(); pg.wait_for_timeout(300); pg.locator('#recCard [data-rsv=reserve]').click(); pg.wait_for_timeout(900)
        check(pg.evaluate("[...TengelLocal.mem.bets.values()].find(b => b.r === 10).rsv.state") == 'reserved' and len(pg.evaluate('window.__notify.items')) == 2, '10Rを予約 → 予約中・お知らせ2件')
        # 結果を記録したレースは上書きしない
        pg.click('.tabbar button[data-tab=rec]'); pg.wait_for_timeout(400)
        pg.locator(f'#recList .lrow[data-id="{b9c["id"]}"] .lmain').click(); pg.wait_for_timeout(300)
        pg.locator(f'#recList .lrow[data-id="{b9c["id"]}"] [data-act=load]').click(); pg.wait_for_timeout(600)
        check(pg.locator('#fR').input_value() == '9' and '結果を記録ずみ（的中）' in pg.locator('#recCard').inner_text() and pg.locator('#recCard [data-rsv=reserve]').count() == 0, '結果を記録した9R：判定画面では「結果を記録ずみ」（予約し直せない）')
        # 設定：結果確認のお知らせ オフ → 待っていたお知らせが消える → オン
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(500)
        nc = pg.locator('#setNotify')
        check(nc.count() == 1 and '発走15分後' in nc.inner_text() and '通知は許可されているよ' in nc.inner_text() and '2件' in nc.inner_text(), f'設定に「結果確認のお知らせ」（許可ずみ・予約中2件）')
        nc.locator('#notifySeg button[data-v="0"]').click(); pg.wait_for_timeout(700)
        check(pg.evaluate('window.__notify.items') == [] and pg.evaluate("TengelLocal.getSetting('notify')") is False, 'オフ → 待っていたお知らせを全部消す')
        nc.locator('#notifySeg button[data-v="1"]').click(); pg.wait_for_timeout(700)
        check(len(pg.evaluate('window.__notify.items')) == 2, 'オン → 入れ直す（2件）')
        # 予約中の8Rを判定画面に戻しておく（このあとの券種のテストは買い目のカードで）
        pg.click('.tabbar button[data-tab=rec]'); pg.wait_for_timeout(400)
        pg.locator(f'#recList .lrow[data-id="{b8id}"] .lmain').click(); pg.wait_for_timeout(300)
        pg.locator(f'#recList .lrow[data-id="{b8id}"] [data-act=load]').click(); pg.wait_for_timeout(600)
        check(pg.locator('#fR').input_value() == '8' and '予約ずみ' in pg.locator('#recCard').inner_text(), '予約中の8Rを判定画面で開く')
        # 足りないとき：Pカスタムで2つ解放（500P×2）→ 100P → 新しいレースは読めない → ポイントを買う
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(400)
        for tp in ('複勝', '枠複'):
            pg.locator(f'#setCustom [data-pt=unlock1][data-key="type:{tp}"]').click(); pg.wait_for_timeout(150)
            pg.locator(f'#setCustom [data-pt=unlock2][data-key="type:{tp}"]').click(); pg.wait_for_timeout(500)
        check(pg.evaluate('TengelWallet.total()') == 100 and pg.evaluate("TengelWallet.unlocked('type:複勝') && TengelWallet.unlocked('type:枠複') && !TengelWallet.unlocked('type:馬連')") and '解放ずみ' in pg.locator('#setCustom').inner_text(), '券種を2つ解放（500P×2）→ 残り100P')
        check(pg.locator('#setCustom [data-pt=unlock1]').count() == 6 and pg.locator('#setCustom [data-pt=unlock1]').first.inner_text() == 'Pが足りない', '足りないときは「Pが足りない」')
        pg.click('.tabbar button[data-tab=judge]'); pg.wait_for_timeout(400)
        card = pg.locator('#recCard')
        if card.locator('[data-rsv=redo]').count(): card.locator('[data-rsv=redo]').click(); pg.wait_for_timeout(300)
        check(card.locator('[data-k=rtypes] button.lock').count() == 4 and card.locator('[data-k=rtypes] button[data-v=複勝]:not(.lock)').count() == 1, '解放した複勝・枠複は🔒が取れる')
        card.locator('[data-rsv=back]').click(); pg.wait_for_timeout(200)
        pg.evaluate("window.__ocrLines = %s" % json.dumps([lines_r(OCR_LINES['a_tanfuku_waku'], 11)], ensure_ascii=False))
        pg.set_input_files('#ocrFile', [os.path.join(OCR_DIR, 'a_tanfuku_waku.jpg')]); pg.wait_for_timeout(1800)
        om = pg.locator('#ocrMsg').inner_text()
        check('ポイントが足りないよ' in om and '200P' in om and pg.locator('#ocrMsg [data-gopt=points]').count() == 1 and pg.locator('#fR').input_value() == '8' and pg.evaluate('TengelWallet.total()') == 100, '100Pでは新しいレースを読めない（入力はそのまま＝8R・「ポイントを買う」）')
        pg.locator('#ocrMsg [data-gopt=points]').click(); pg.wait_for_timeout(600)
        check(pg.locator('#v-set').is_visible() and pg.locator('#setPoints [data-pt=buy][data-id="jp.tengel.app.points1000"]').count() == 1, '「ポイントを買う」→ 設定タブのポイント（買う一覧が開いている）')
        # 買う（App内課金のかわり）：1,000P → 届く → finish
        pg.evaluate("window.__txn = 500; window.__iap.buy['jp.tengel.app.points1000'] = () => ({ ok: true, state: 'ok', tx: { id: String(++window.__txn), originalId: 'o1', product: 'jp.tengel.app.points1000', kind: 'pack', date: new Date().toISOString(), revoked: false } }); 0")
        pg.evaluate("window.__bridge = []")
        pg.locator('#setPoints [data-pt=buy][data-id="jp.tengel.app.points1000"]').click(); pg.wait_for_timeout(700)
        fin = [x for x in pg.evaluate('window.__bridge') if x['name'] == 'iap' and x['payload']['op'] == 'finish']
        check(pg.evaluate('TengelWallet.total()') == 1100 and len(fin) == 1 and fin[0]['payload']['id'] == '501' and '買ったP 1,000' in pg.locator('#setPoints').inner_text(), '1,000Pのパックを買う → 1,100P・台帳に書いてから取引を終わらせる（finish）')
        pg.locator('#setPoints [data-pt=buy][data-id="jp.tengel.app.points1000"]').click(); pg.wait_for_timeout(700)
        check(pg.evaluate('TengelWallet.total()') == 2100, 'もう一度買う（別の取引）→ 2,100P')
        pg.evaluate("window.__iap.buy['jp.tengel.app.points500'] = () => ({ ok: false, state: 'cancelled' }); 0")
        pg.locator('#setPoints [data-pt=buy][data-id="jp.tengel.app.points500"]').click(); pg.wait_for_timeout(500)
        check(pg.evaluate('TengelWallet.total()') == 2100, 'やめたら何も変わらない')
        # 届いているのにまだ台帳に入れていない取引（サブスク 4,400P）→ 開き直すと入る。同じ取引は2回入れない
        pg.evaluate("window.__iap.unfinished = [{ id: '900', originalId: 'o9', product: 'jp.tengel.app.sub4400', kind: 'sub', date: new Date().toISOString(), revoked: false }]")
        sub_tx = "[{ id: '900', originalId: 'o9', product: 'jp.tengel.app.sub4400', kind: 'sub', date: new Date().toISOString(), revoked: false }]"
        pg.add_init_script("window.__iap.unfinished = %s;" % sub_tx)
        pg.reload(); pg.wait_for_timeout(800); gate(pg); pg.wait_for_timeout(1500)
        check(pg.evaluate('TengelWallet.total()') == 6500 and pg.evaluate("TengelWallet.balance().paid_sub") == 4400 and json.loads(store['markers'].get('granted-sub', '[]')) == ['900'], f'サブスクの取引（4,400P）が開いたときに入る・キーチェーンに取引の番号（{store["markers"].get("granted-sub")}）')
        pg.reload(); pg.wait_for_timeout(800); gate(pg); pg.wait_for_timeout(1500)
        check(pg.evaluate('TengelWallet.total()') == 6500, '同じ取引がまた届いても2回入れない')
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(400)
        pt = pg.locator('#setPoints').inner_text()
        check('うちサブスク 4,400' in pt and 'まで' in pt, f'ポイントのカード：サブスクのPと期限（{pt[:80]}…）')
        pg.locator('#setPoints [data-pt=show][data-v=hist]').click(); pg.wait_for_timeout(300)
        hist = pg.locator('#setPoints .pthist').inner_text()
        check('初回プレゼント' in hist and '+1,000P' in hist and '-400P' in hist and '解放' in hist and '月4,400Pプラン' in hist and pg.locator('#setPoints [data-pt=restore]').count() == 1, 'くわしく：履歴（プレゼント・買った・使った・解放・サブスク）と「購入を復元」')
        # ミッション：8レース数えた状態にして受け取る（数え方は test_points.js。ここは画面）
        pg.evaluate("""(async () => { const w = await TengelLocal.getMeta('wallet'); for (let i = 1; i <= 8; i++) w.counted['2026-10-0' + i + '||1'] = new Date().toISOString(); await TengelLocal.putMeta(w); })()""")
        pg.reload(); pg.wait_for_timeout(800); gate(pg); pg.wait_for_timeout(1200)
        check(pg.locator('.tabbar [data-tab=set] .tbdg').count() == 1, '受け取れるミッションがあると設定タブに印')
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(400)
        ms = pg.locator('#setMission')
        check('いま 10レース' in ms.inner_text() and ms.locator('[data-pt=claim]').count() == 1 and '受け取れるよ' in ms.inner_text(), 'ミッション：10レース（8＋予約・諦めた2）で「受け取る」')
        ms.locator('[data-pt=claim]').click(); pg.wait_for_timeout(600)
        check(pg.evaluate('TengelWallet.total()') == 7000 and pg.evaluate("TengelWallet.balance().free") == 600 and ms.locator('[data-pt=claim]').count() == 0 and pg.locator('.tabbar [data-tab=set] .tbdg').count() == 0 and '次は 15レース' in ms.inner_text(), '受け取ると 500P（無償の枠）・印が消える・次は15レース')
        pg.screenshot(path=os.path.join(W, 't4', 'native_mission.png'), full_page=False)
        pg.click('.tabbar button[data-tab=judge]'); pg.wait_for_timeout(300)
        # ---- バックアップを保存（共有シート） ----
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(300)
        pg.evaluate('window.__bridge = []')
        pg.click('#pwaBackup'); pg.wait_for_timeout(500)
        sh = [x for x in pg.evaluate('window.__bridge') if x['name'] == 'share']
        check(len(sh) == 1 and sh[0]['payload']['name'].startswith('テンゲル記録_') and sh[0]['payload']['name'].endswith('.json'), 'バックアップを保存 → 共有シートにファイルを渡す')
        shared = json.loads(sh[0]['payload']['text']) if sh else {}
        check(len(shared.get('bets', [])) == 3 and 'sk-ant' not in sh[0]['payload']['text'] and 'wallet' not in shared, 'ファイルの中身（記録3件・APIキーなし・ポイントの台帳は入れない）')
        check('wallet' in json.loads(store['backup']) and json.loads(store['backup'])['wallet']['events'], 'アプリの中の自動バックアップにはポイントの台帳が入る')
        check('記録3件' in pg.locator('#pwaBkInfo').inner_text() and pg.locator('#sbLast').inner_text() != 'まだしてないよ', f'保存したらお知らせ・最後のバックアップ（{pg.locator("#pwaBkInfo").inner_text()}）')
        pg.evaluate('window.__shareCancel = true; window.__bridge = []; document.querySelector("#pwaBkInfo").textContent = ""')
        pg.click('#pwaBackup'); pg.wait_for_timeout(500)
        check(pg.locator('#pwaBkInfo').inner_text() == '', '共有シートを閉じただけなら「保存した」と言わない')
        pg.evaluate('window.__shareCancel = false')
        auto_txt = pg.locator('#sbAuto').inner_text()
        check('記録3件' in auto_txt, f'自動バックアップの欄（{auto_txt}）')
        # ---- CSVで保存・コピー ----
        pg.click('.tabbar button[data-tab=rec]'); pg.wait_for_timeout(500)
        pg.click('#recExportBtn'); pg.wait_for_timeout(300)
        check(pg.locator('#recSave').is_visible(), '記録タブの書き出しに「CSVで保存」が出る')
        pg.evaluate('window.__bridge = []'); pg.click('#recSave'); pg.wait_for_timeout(500)
        sh = [x for x in pg.evaluate('window.__bridge') if x['name'] == 'share']
        check(len(sh) == 1 and sh[0]['payload']['name'].endswith('.csv') and sh[0]['payload']['text'].startswith('﻿日付') and sh[0]['payload']['text'].split('\r\n')[0].endswith('予約'), 'CSVで保存 → 共有シートにCSVを渡す（App Store版は「予約」の列つき）')
        pg.evaluate('window.__bridge = []'); pg.click('#recCopy'); pg.wait_for_timeout(400)
        cp = [x for x in pg.evaluate('window.__bridge') if x['name'] == 'copy']
        check(len(cp) == 1 and cp[0]['payload'].startswith('日付') and 'コピーしたよ' in pg.locator('#toast').inner_text(), 'コピー → アプリのクリップボードへ')
        # ---- CM：動画は公開中のWeb版から ----
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(300)
        pg.route('https://tmmd6z5fh8-creator.github.io/**', lambda route: route.fulfill(status=404, body=''))
        pg.locator('#setCM button.btn.primary').click(); pg.wait_for_timeout(300)
        src = pg.locator('#cmModal video').get_attribute('src')
        cmd = pg.evaluate('window.__CM')
        want = 'https://tmmd6z5fh8-creator.github.io/TENGEL/' + (cmd.get('srcApp') or cmd['src'])
        check(src == want and (not cmd.get('srcApp') or 'tengel3_cm_app.mp4?v=' in src), f'CMの動画は公開中のWeb版から・アプリ用の版（{src[44:90]}…）')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        # ---- 保存場所が消えた → 「戻す？」 → 戻す ----
        before = store['backup']
        pg.evaluate("new Promise(r => { const q = indexedDB.deleteDatabase('tengel3'); q.onsuccess = q.onerror = q.onblocked = () => r(); })")
        pg.reload(); pg.wait_for_timeout(800); gate(pg); pg.wait_for_timeout(900)
        box = pg.locator('#nativeRestore')
        check(box.count() == 1 and '3件' in box.inner_text() and 'ポイントの台帳が' in box.inner_text(), f'記録0件で自動バックアップに記録 → 「戻す？」（{box.inner_text()[:60] if box.count() else "なし"}）')
        check(pg.evaluate('TengelWallet.total()') == 0 and pg.evaluate('TengelWallet.isEmpty()'), '保存場所が消えても、初回の1,500Pはもう一度は出ない（キーチェーンのしるし）')
        pg.screenshot(path=os.path.join(W, 't4', 'native_restore.png'))
        pg.wait_for_timeout(2200)
        check(store['backup'] == before, '聞いている間は自動バックアップを書かない（前の記録を守る）')
        box.locator('[data-nr=yes]').click(); pg.wait_for_timeout(1200)
        check(pg.locator('#nativeRestore').count() == 0 and pg.evaluate('TengelLocal.mem.bets.size') == 3 and '記録3件を戻したよ' in pg.locator('#toast').inner_text() and 'ポイント（7,000P）も戻したよ' in pg.locator('#toast').inner_text() and pg.evaluate('TengelWallet.total()') == 7000, '「記録を戻す」→ 記録とポイントの台帳が戻る')
        pg.wait_for_timeout(800)
        check(len(json.loads(store['backup'])['bets']) == 3 and json.loads(store['backup'])['wallet']['events'], '戻したあとも自動バックアップに記録と台帳')
        # ---- もう一度消えた → 「戻さない」 ----
        pg.evaluate("new Promise(r => { const q = indexedDB.deleteDatabase('tengel3'); q.onsuccess = q.onerror = q.onblocked = () => r(); })")
        pg.reload(); pg.wait_for_timeout(800); gate(pg); pg.wait_for_timeout(900)
        check(pg.locator('#nativeRestore').count() == 1, 'また「戻す？」')
        pg.locator('#nativeRestore [data-nr=no]').click(); pg.wait_for_timeout(1900)
        check(pg.locator('#nativeRestore').count() == 0 and json.loads(store['backup'])['bets'] == [], '「戻さない」→ いまの状態（0件）をバックアップ')
        pg.reload(); pg.wait_for_timeout(800); gate(pg); pg.wait_for_timeout(900)
        check(pg.locator('#nativeRestore').count() == 0, 'もう聞かない')
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(400)
        check(pg.evaluate('TengelWallet.total()') == 0 and '受け取りずみだよ' in pg.locator('#setPoints').inner_text(), '戻さなかったので 0P・はじめてのプレゼントは受け取りずみの案内')
        check(pg.locator('#setAbout #abGate').count() == 1 and '競馬の注意' in pg.locator('#setAbout #abGate').inner_text(), '「このアプリについて」にも、はじめの文（競馬の注意など）')
        # ---- Web版（ブラウザ）は今までどおり ----
        ctx2 = b.new_context(viewport={'width': 390, 'height': 844}, locale='ja-JP')
        p2 = ctx2.new_page(); p2.on('pageerror', lambda e: errs.append('WEB ' + str(e)))
        p2.goto(BASE); p2.wait_for_timeout(1500)
        w = p2.evaluate("({ native: window.__NATIVE, bridge: window.TengelNative, dl: null })")
        p2.click('.tabbar button[data-tab=set]'); p2.wait_for_timeout(400)
        check(w['native'] is False and w['bridge'] is None and p2.locator('#suCheck').count() == 1 and p2.locator('#sbAuto').count() == 0 and p2.locator('#setUpdate h2').inner_text() == 'アプリの更新', 'Web版：アプリの印は出ない（更新の確認・バックアップは今までどおり）')
        check(p2.locator('#setNotify').count() == 0 and p2.evaluate("typeof window.TengelReserve === 'undefined' && typeof window.TengelCustomRate === 'undefined'"), 'Web版：お知らせの設定・予約の仕組みは入らない')
        check(p2.locator('#setFx').count() == 0 and p2.evaluate("typeof window.TengelFx === 'undefined' && typeof window.__FX === 'undefined' && !document.querySelector('#fxCss')"), 'Web版：的中ボタン（演出・設定）は入らない')
        p2.click('.tabbar button[data-tab=judge]'); p2.wait_for_timeout(400)
        check(p2.locator('#recCard h2').inner_text().startswith('結果・収支の記録') and p2.locator('#omakaseBtn').count() == 0 and p2.locator('#result .rnav').count() == 0 and not [t for t in p2.locator('#result .zref').all_inner_texts() if '選んだ馬で' in t] and p2.locator('#saveJudge').count() == 1, 'Web版：判定画面は今までどおり（結果・収支の記録・お任せなし・矢印なし・%なし・判定と結果を保存）')
        p2.click('.tabbar button[data-tab=rec]'); p2.wait_for_timeout(300); p2.click('#recExportBtn'); p2.wait_for_timeout(300)
        check(not p2.locator('#recSave').is_visible(), 'Web版：「CSVで保存」は出ない（今までどおり）')
        p2.click('.tabbar button[data-tab=set]'); p2.wait_for_timeout(300)
        p2.locator('#abPrivacy summary').click(); p2.wait_for_timeout(100)
        wv = p2.locator('#setAbout').inner_text()
        check('ご利用にあたって' in wv and 'Google Fonts' in wv and p2.locator('#abFonts').count() == 0, 'Web版の「このアプリについて」（Google Fonts の説明・フォントのライセンスはなし）')
        # ---- App Store版の説明書 ----
        p3 = ctx.new_page(); p3.on('pageerror', lambda e: errs.append('MANUAL ' + str(e)))
        p3.goto(APPURL + 'manual.html'); p3.wait_for_timeout(1200)
        mt = p3.locator('#home').inner_text()
        check('iPhoneに入れる' not in mt and '大井のデータを新しくする' not in mt and '記録を守る' in mt and '姫に送' not in p3.content(), '説明書（App Store版）：「iPhoneに入れる」「大井のデータを新しくする」なし・姫に送るなし')
        p3.goto(APPURL + 'manual.html#backup'); p3.wait_for_timeout(600)
        check('自動バックアップ' in p3.locator('#s-backup').inner_text() and 'LINE' not in p3.locator('#s-backup').inner_text(), '説明書：バックアップの項目はアプリ版（自動バックアップ・LINEなし）')
        check(not [u for u in outside if 'fonts.g' in u], '説明書もGoogleに通信しない')
        b.close()
finally:
    srv.terminate()
check(not errs, 'ページのエラーなし' + (f'：{errs[:3]}' if errs else ''))
print('結果：', 'OK' if not fails else f'{len(fails)}件おかしい')
raise SystemExit(1 if fails else 0)
