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
# テスト版（第4.59版：TENGEL_TEST=1）：はじめから 10,000P・設定に「テスト版の道具」。App Store には 出さない
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'TEST')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, HIST='hist_280.json', DROP='', TARGET='app', TENGEL_TEST='1'))
pth = os.path.join(SRV, 'TEST', 'index.html'); html = open(pth, encoding='utf8').read()
assert 'window.__TEST=true;' in html and 'window.__TEST=true;' not in open(os.path.join(SRV, 'APP', 'index.html'), encoding='utf8').read() and 'window.__TEST=true;' not in open(os.path.join(SRV, 'TENGEL', 'index.html'), encoding='utf8').read()
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
TESTURL = f'http://localhost:{PORT}/TEST/'
# 第5弾：超神様の 動画（H.264）は Chromium で 読めないので、手元の 動画（ios/fx_assets/*.mp4）から 同じ 絵の 小さな webm を 作って（t5/films/ に とっておく）同じ 名前の かわりに 読ませる
FILMS_DIR = os.path.join(W, 't5', 'films')
for f in ('sgd_film', 'spg_up', 'sd_film', 'nd_film'):   # 第4.70版〜：紫電の 動画も・第4.77版：ノーマルど的中の 動画も
    mp4, webm = os.path.join(W, 'ios', 'fx_assets', f + '.mp4'), os.path.join(FILMS_DIR, f + '.webm')
    if not os.path.exists(webm) and os.path.exists(mp4) and shutil.which('ffmpeg'):
        os.makedirs(FILMS_DIR, exist_ok=True)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', mp4, '-vf', 'scale=390:844', '-c:v', 'libvpx-vp9', '-deadline', 'realtime', '-cpu-used', '8', '-crf', '40', '-b:v', '0', '-an', '-row-mt', '1', webm], check=False)
    if os.path.exists(webm):
        shutil.copy(webm, os.path.join(SRV, 'APP', f + '.webm'))
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
        # 第4.59版：上の帯の 所有ポイント（購入P＝パック＋もらったP・サブスクP）と 説明書の 置き場（マザーデータの 札の すぐ 左）・テスト版の 印は ない
        hb = pg.evaluate("(() => { const p = document.querySelector('#ptsPill'), m = document.querySelector('#manBtn'), d = document.querySelector('#dbpill'), b = document.querySelector('header.top .brand'); if (!p || !m || !d) return null; const r = x => x.getBoundingClientRect(); return { txt: p.innerText.replace(/\\s+/g, ' '), afterBrand: b.nextElementSibling === p, order: m.compareDocumentPosition(d) & Node.DOCUMENT_POSITION_FOLLOWING ? 1 : 0, mRight: r(m).right, dLeft: r(d).left, dRight: r(d).right, mTop: r(m).top, dTop: r(d).top, w: innerWidth, tag: !!document.querySelector('#testTag'), gopt: p.dataset.gopt }; })()")
        check(hb and '購入 1,500P' in hb['txt'] and 'サブスク 0P' in hb['txt'] and hb['afterBrand'] and hb['gopt'] == 'points' and not hb['tag'], f'上の帯：ロゴの 右に 所有ポイント「購入 1,500P・サブスク 0P」（押すと 設定の ポイントへ）・テスト版の 印は ない（{hb}）')
        check(hb and hb['order'] == 1 and ((abs(hb['mTop'] - hb['dTop']) < 8 and hb['mRight'] <= hb['dLeft'] + 1 and hb['dLeft'] - hb['mRight'] < 24 and hb['dRight'] >= hb['w'] - 24) or (hb['mTop'] < hb['dTop'] - 8 and hb['mRight'] >= hb['w'] - 24)), f'上の帯：説明書は マザーデータの 札の すぐ 左で 右よせ（札が 2行目に 回る ときは 1行目の 右はし）（{hb}）')
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
        check('CM（紹介動画）' not in pv and '開発者が集めることも、受け取ることもありません' in pv and 'GitHub Pages' in pv and 'Google' not in pv and '自動バックアップ' in pv and 'Anthropic' not in pv and 'APIキー' not in pv and '端末の中（iOS・iPadOS の文字認識の機能）で読み取ります' in pv,
              'プライバシーポリシー（App Store版：Googleなし・自動バックアップ・CMの 項目なし・画像の読み取りは端末の中でAPIキーなし）')
        pg.locator('#abFonts summary').click(); pg.wait_for_timeout(100)
        fo = pg.locator('#abFonts').inner_text()
        check('Kaisei Decol' in fo and 'M PLUS Rounded 1c' in fo and 'Rounded M+' in fo and '画面で使う文字だけを残した版' in fo and fo.count('Copyright') >= 30, 'フォントのライセンス：着せ替えの字 29ファミリー（使う字だけの版・著作権の表示）も並ぶ（第4弾）')
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
        # 第4.65版：App Store版は 複勝を 読まない（欄は 空のまま・「読めなかった：複勝」とも 言わない）
        check(got['rows'] == 12 and got['tan6'] == '2.4' and got['fuku6'] == '' and got['s1'] == '18.5' and got['s1c'] == '6-2-10' and got['s5'] == '41.3' and got['s10'] == '84', '単勝12頭と3連単1位・5位・10位が入る・複勝は 読まない（空）')
        check('読み取った' in got['msg'] and '単勝12頭' in got['msg'] and '読めなかった' not in got['msg'] and '複勝' not in got['msg'], f'読み取れたもののお知らせ（複勝の 文字は ない）（{got["msg"][:60]}）')
        check('単勝と3連単人気順のスクショを1〜3枚' in pg.locator('#ocrHint').inner_text() and '複勝' not in pg.locator('#ocrHint').inner_text(), 'ボタンの 横の 案内は「単勝と3連単人気順のスクショを1〜3枚」')
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
        # 第4.65版：まず 結果だけ（mode=result）。金額の 欄は 結果を 決めた あと（演出の あと）に 出る
        check(f9.count() == 1 and f9.get_attribute('data-mode') == 'result' and f9.locator('[data-k=p1]').count() == 1 and f9.locator('[data-k=res]').count() == 0 and f9.locator('details[data-k=betsee]').count() == 1 and f9.locator('[data-k=stake]').count() == 0 and f9.locator('[data-k=mslot]').count() == 0 and f9.locator('[data-k=note]').count() == 0
              and f9.locator('[data-act=rsave]').inner_text() == '結果を決める' and '金額は後からでも入れられるよ' in f9.inner_text() and '結果待ち' in f9.locator('[data-k=status]').inner_text(),
              '結果入力の欄（第4.65版）：まず 結果だけ（1〜3着の馬番・取消・中止・発走・画像）。買い目は出さない・金額・マザーデータ・メモの 欄は まだ ない・「結果を決める」・結果待ち')
        check(f9.locator('[data-act=rdel]').count() == 1 and f9.locator('[data-act=load]').count() == 1 and pg.locator(f'#recList .lrow[data-id="{b9c["id"]}"]').inner_text().count('保存した判定') == 0 and '判定（' not in pg.locator(f'#recList .lrow[data-id="{b9c["id"]}"] .ledit').inner_text(),
              'App Store版：行の 下に「保存した判定（STEP0〜T3）」と 判定の 1行（層・比・ゾーン）は 出さない')
        pg.evaluate("window.__ocrLines = %s" % json.dumps([RESULT_LINES], ensure_ascii=False))
        f9.locator('[data-k=rimgfile]').set_input_files([os.path.join(OCR_DIR, 'c_sanrentan.jpg')]); pg.wait_for_timeout(1800)
        vals = {k: f9.locator(f'[data-k={k}]').input_value() for k in ('p1', 'p2', 'p3', 'cancel')}
        check(vals == {'p1': '6', 'p2': '2', 'p3': '10', 'cancel': ''} and '読み取った' in f9.locator('[data-k=hint]').inner_text() and '1着 6（1番人気）' in f9.locator('[data-k=plab]').inner_text(), f'結果の画像から 1〜3着の馬番が入る（{vals}）')
        b9pay = pg.evaluate("[...TengelLocal.mem.bets.values()].find(b => b.r === 9).rsv.result")
        check('的中' in f9.locator('[data-k=status]').inner_text() and f9.locator('.betlist .hitc').count() == 2 and f9.locator('[data-k=payout]').count() == 0 and '「結果を決める」を押してね' in f9.locator('[data-k=hint]').inner_text(),
              '当たった組（単勝 6・馬単 6→2）に色・的中。払戻の 欄は まだ ない（画像の 払戻は 次の 金額の 欄に 入る）')
        pg.evaluate("window.__fxEv = []; document.addEventListener('tengel:fx', e => window.__fxEv.push(e.detail.phase + ':' + e.detail.kind))")
        f9.locator('[data-act=rsave]').click(); pg.wait_for_timeout(1200)
        b9d = pg.evaluate("[...TengelLocal.mem.bets.values()].find(b => b.r === 9)")
        check(b9d['rsv']['state'] == 'done' and b9d['rsv']['judged']['state'] == '的中' and b9d['rsv']['judged']['per'] == {'単勝': '的中', '馬単': '的中'} and [b9d['n1'], b9d['n2'], b9d['n3']] == [6, 2, 10] and [b9d['p1'], b9d['p2'], b9d['p3']] == [1, 2, 3] and b9d['payout'] is None and b9d['stake'] == 1800 and b9d['rsv']['result']['pay']['単勝'] == {'6': 240},
              f'「結果を決める」→ 券種ごとに的中・着順（馬番と人気）が記録に入る・購入額は 予約の 点数×100円・払戻は まだ 空（画像の 払戻の 表は 記録に）（payout={b9d["payout"]}）')
        # ---- 的中ボタン（第3弾・10章）：単勝・馬単の当たり（3連単なし）→ 的中の PUSH → タップ → いつものボード（券種ごとの結果・お金なし）→ とじる ----
        ov = pg.locator('#fxOv')
        sx = pg.evaluate('TengelFx.sfxState()')
        check(ov.count() == 1 and ov.locator('.fxs .ov .push').count() == 1 and ov.locator('.push.big').count() == 0 and pg.evaluate('TengelFx.current()') == {'kind': 'hit', 'phase': 'push', 'quiet': False, 'theme': None, 'film': 0, 'sp': 0, 'pre': 0, 'pz': 1} and pg.evaluate('document.documentElement.classList.contains("fxon")') and pg.evaluate('window.__zoom').pop().get('lock') is True,
              f'保存 → 的中の PUSH が出る（3連単なしの当たり＝的中）・拡大は止める（{pg.evaluate("TengelFx.current()")}）')
        check(sx['ctx'] and sx['fetched'] and 'sfx_hit_push.m4a' in pg.evaluate("performance.getEntriesByType('resource').map(e => e.name).join()"), f'「結果を保存」を押したときに音の準備（AudioContext・音のファイルを読む）（{sx}）')
        check(pg.locator('#toast').is_hidden() or '保存できたよ' not in pg.locator('#toast').inner_text(), '演出が出るときは、お知らせの帯は出さない（ボードが結果を見せる）')
        f9 = pg.locator('#recList .rsvf')
        check(f9.get_attribute('data-mode') == 'amount' and '結果を記録したよ（的中）' in f9.locator('[data-k=savemsg]').inner_text() and '単勝 的中' in f9.locator('[data-k=savemsg]').inner_text(), '演出の うしろで 行は 金額の 欄（mode=amount）に 入れかわる・欄の下には 結果を記録したよ（券種ごとの結果）')
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
        # 第4.65版：演出の あとは 金額の 欄（結果の 欄は ない）。払戻は 結果の 画像から（単勝 240・馬単 1120）・購入額は 点数×100円・「金額の入力は後からでもできるよ」
        f9 = pg.locator('#recList .rsvf')
        check(f9.count() == 1 and f9.get_attribute('data-mode') == 'amount' and f9.locator('[data-k=p1]').count() == 0 and f9.locator('[data-k=stake][data-t="単勝"]').input_value() == '300' and f9.locator('[data-k=stake][data-t="馬単"]').input_value() == '1500'
              and f9.locator('[data-k=payout][data-t="単勝"]').input_value() == '240' and f9.locator('[data-k=payout][data-t="馬単"]').input_value() == '1120' and f9.locator('[data-k=mslot]').count() == 1 and f9.locator('[data-k=note]').count() == 1
              and '金額の入力は後からでもできるよ' in f9.inner_text() and f9.locator('[data-act=rsave]').inner_text() == '記録する' and f9.locator('[data-act=rlater]').inner_text() == 'あとで入れる' and '的中' in f9.locator('[data-k=status]').inner_text(),
              '演出の あと：金額の 欄だけ（券種ごとの 購入額 → 払戻（画像の 払戻が 入っている）・マザーデータ・メモ）・「記録する」「あとで入れる」・「金額の入力は後からでもできるよ！」')
        f9.locator('[data-act=rsave]').click(); pg.wait_for_timeout(900)
        b9f = pg.evaluate("[...TengelLocal.mem.bets.values()].find(b => b.r === 9)")
        f9 = pg.locator('#recList .rsvf')
        check(pg.locator('#fxOv').count() == 0 and b9f['payout'] == 1360 and b9f['stake'] == 1800 and b9f['amt']['単勝'] == {'stake': 300, 'payout': 240} and '金額を記録したよ（的中）' in f9.locator('[data-k=savemsg]').inner_text()
              and f9.get_attribute('data-mode') == 'edit' and f9.locator('[data-k=p1]').count() == 1 and f9.locator('[data-k=stake]').count() == 2 and f9.locator('[data-act=rsave]').inner_text() == '記録を保存' and f9.locator('[data-act=rdel]').inner_text() == '記録を消す',
              f'「記録する」→ 払戻の 合計 1,360円が 記録に 入る・演出は 出ない・行は 全部の 欄（あとから 直す 形・mode=edit）に（payout={b9f["payout"]}）')
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
        got = [D(spec([11, 8, 2])), D(spec([11, 12, 2])), D(spec([11, 6, 2])), D(spec([8, 5, 2])), D(spec([13, 8, 2])), D(spec([1, 6, 2])), D(spec([11, 6, 99])), D(spec(None, [('馬単', '的中', [[6, 2]])])), D(spec(None, [('馬単', '不的中', [])])), D(spec(None, [('馬単', '返還', [])])), D(spec([8, 7, 2])), D(spec([11, 10, 7]))]
        check(got == ['gd:11/11', 'gd:11/11,12/12', 'fz:11/11', 'big', 'big', 'big', 'big', 'hit', 'miss', 'miss', 'big', 'gd:11/11,10/10'],
              f'どれが出るか（18.2）：11・8・2／11・12・2／11・10・7 → 神様的中（超大穴と ほかに 大穴以上）・11・6・2 → ど的中（超大穴の馬番と人気）・8・5・2／8・7・2／13・8・2／1・6・2／人気がわからない馬 → デカ・3連単なし → 的中・当たりなし → ハズレ（{got}）')
        gdd = pg.evaluate("(s) => TengelFx.decide(s)", spec([11, 8, 2]))
        check(gdd == {'kind': 'gd', 'supers': [{'no': 11, 'rank': 11}], 'bigs': [{'no': 8, 'rank': 8}]} and pg.evaluate("(s) => TengelFx.decide(s).bigs", spec([11, 12, 2])) == [] and pg.evaluate("(s) => TengelFx.decide(s).bigs", spec([11, 6, 2])) == [],
              f'神様的中の 帯の もと：超大穴 11 と 大穴 8（超大穴 2頭なら 大穴なし・ど的中なら 大穴は 出さない）（{gdd}）')
        # 隠れど的中（※仮）：デカ的中の 2〜7回に1回（乱数を固定して 2回目）。本物のど的中は数えない。数は端末の中（localStorage）だけ・バックアップには入れない
        pg.evaluate("localStorage.removeItem('tengel.fxhidden'); TengelFx._rand = () => 0")
        seq = []
        for tri in ([8, 5, 2], [8, 5, 2], [11, 6, 2], [8, 5, 2], [8, 5, 2]):
            seq.append(pg.evaluate("(s) => TengelFx.show(s)", spec(tri))); pg.wait_for_timeout(150)
            if seq[-1] == 'hidden':
                hp = pg.locator('#fxOv')
                check(hp.locator('.ov.big .pbox.pz .push').count() == 1 and hp.locator('.push.big').count() == 0 and pg.evaluate('TengelFx.current()')['kind'] == 'hidden' and pg.evaluate('TengelFx.current()')['pz'] == 1.2, '隠れど的中：見た目はデカの PUSH（いつもの PUSH の 1.2倍・第4.60版）')
                hp.locator('.push').click(force=True); pg.wait_for_timeout(500)
                check(hp.locator('.fxs .ov.fz').count() == 1 and hp.locator('.rb.fz .bh').text_content() == '隠れど的中！！！' and '隠れ' in hp.locator('.rb .zrib').text_content() and hp.locator('.rb .brows li.top .bt').text_content() == '3連単', '隠れど的中：押すと ど的中の演出 → 見出し「隠れど的中！！！」・帯「隠れ」・3連単の行がいちばん上')
            pg.evaluate('TengelFx.close()'); pg.wait_for_timeout(100)
        hs = pg.evaluate("JSON.parse(localStorage.getItem('tengel.fxhidden'))")
        check(seq == ['big', 'hidden', 'zp', 'big', 'hidden'] and hs == {'c': 0, 'n': 2}, f'隠れど的中の数え方：デカ→隠れ（2回目）→ど的中（数えない・乱数 0 なので くじは 超プレミアムど的中）→デカ→隠れ（{seq}・{hs}）')
        pg.evaluate("TengelFx._rand = () => 0.99")   # ここからは くじを 外す（第4.77版：くじの ど的中は ノーマルど的中（nd）なので、CSS の ど的中（隠れど的中と 同じ 部品）は force で 出す）
        pg.wait_for_timeout(1900)
        check('fxhidden' not in (store['backup'] or '') and 'fxhidden' not in pg.evaluate("JSON.stringify([...TengelLocal.mem.bets.values()])"), '隠れど的中の数は 記録・自動バックアップに入らない')
        # ど的中：虹色の超デカ PUSH → 押した瞬間にフリーズ → 結果（超大穴の帯・3連単の行の超大穴の馬番に輪）
        pg.evaluate("(s) => TengelFx.show(Object.assign({ force: 'fz' }, s))", spec([11, 6, 2], [('馬単', '的中', [[11, 6], [6, 2]]), ('ワイド', '不的中', [])])); pg.wait_for_timeout(200)
        fo = pg.locator('#fxOv')
        check(fo.locator('.ov.fz .pbox.pz .push').count() == 1 and fo.locator('.push.fz').count() == 0 and fo.locator('.pbox.rbw').count() == 0 and fo.locator('.aura, .prays, .edge, .frame').count() == 4 and fo.locator('.tap').inner_text() == 'タップ！' and 'k-fz' in fo.get_attribute('class') and pg.evaluate('TengelFx.current()')['pz'] == 1.4, 'ど的中：そのテーマの PUSH を 1.4倍（虹色では ない）・まわりは ど的中の 虹の 光（第4.60版）')
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
        pg.evaluate("(s) => TengelFx.show(Object.assign({ force: 'fz' }, s))", spec([11, 6, 2])); pg.wait_for_timeout(200)
        check(pg.locator('#fxOv .fxs.calm .ov.fz .pbox.pz .push').count() == 1 and pg.evaluate("getComputedStyle(document.querySelector('#fxOv .aura')).animationName") == 'none', '演出を控えめにする：ど的中の まわりの 動きが止まる（視差効果を減らすと同じ形）')
        pg.evaluate('TengelFx.tap()'); pg.wait_for_timeout(200)
        check(pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.fz .pc')).display") == 'none' and pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.fz .mt')).display") == 'none', '控えめ：フリーズ・ネオンのカットは出さない（1秒真っ暗 → 結果をふわっと）')
        pg.evaluate('TengelFx.close()')
        # ---- 第5弾（16.3）：特別な 演出。くじ（※仮）→ PUSH は ど的中と 同じ → 押したあと → そのテーマの ど的中の 形の ボード ----
        pg.evaluate("window.__seq = arr => { let i = 0; TengelFx._rand = () => arr[Math.min(i++, arr.length - 1)]; }")   # 乱数を 順に 決める（1つめ：プレミアム／超神様の くじ・2つめ：超プレミアム／超プレミアム神様の くじ）
        LOTS = [pg.evaluate("(a) => { const o = []; for (const k of ['fz', 'gd', 'big']) { window.__seq(a); o.push(TengelFx.lottery(k)); } return o; }", a) for a in ([0, 0], [0.1, 0.9], [0.12, 0.3], [0.13, 0.5], [0.2], [0.99])]
        check(LOTS == [['zp', 'spg', 'big'], ['pc', 'sgd', 'big'], ['pc', 'sgd', 'big'], ['pc', 'gd', 'big'], ['sd', 'gd', 'big'], ['nd', 'gd', 'big']], f'くじ：ど的中 → 6分の1 で プレミアム → その 8分の1 で 超プレミアム・残りの 2分の1 で 紫電（第4.66版）・それ以外は ノーマルど的中（第4.77版）／神様 → 8分の1 で 超神様 → その 4分の1 で 超プレミアム神様（{LOTS}）')
        LOTS2 = [pg.evaluate("(a) => { window.__seq(a); return TengelFx.lottery('fz'); }", a) for a in ([0.5, 0.49], [0.5, 0.5], [0.2, 0.99])]
        check(LOTS2 == ['sd', 'nd', 'nd'], f'紫電の くじ：プレミアムに ならなかった ど的中の 2つめの 乱数が .5 未満なら 紫電・それ以外は ノーマルど的中（第4.77版：動画）（{LOTS2}）')
        pg.evaluate("window.__seq([0.1, 0.9])")
        kk = pg.evaluate("(s) => TengelFx.show(s)", spec([11, 8, 2], [('馬単', '的中', [[11, 8]]), ('ワイド', '不的中', [])])); pg.wait_for_timeout(300)
        so = pg.locator('#fxOv')
        check(kk == 'sgd' and so.locator('.ov.fz .pbox.rbw .push .rbf').count() == 1 and so.locator('.pbox .rba').count() == 1 and 'k-sgd' in so.get_attribute('class') and pg.evaluate('TengelFx.current()')['kind'] == 'sgd' and pg.evaluate('TengelFx.current()')['pz'] == 1.6, f'11・8・2 で 乱数 0.1・0.9 → 超神様的中（PUSH は そのテーマの PUSH を 1.6倍・虹色）（{kk}）')
        pg.evaluate('TengelFx.close()')
        pg.evaluate("TengelFx.set({ effects: false })")
        kq = pg.evaluate("(s) => TengelFx.show(s)", spec([11, 8, 2])); pg.wait_for_timeout(300)
        check(kq == 'gd' and pg.locator('#fxOv .ov.miss.quiet').count() == 1 and pg.locator('#fxOv .rb.fz .bh').inner_text() == '神様的中！！！' and '大穴' in pg.locator('#fxOv .rb .zrib').inner_text(), '的中エフェクト オフ：くじは ひかず 神様的中の ボード（見出し「神様的中！！！」）だけ 静かに')
        pg.evaluate('TengelFx.close()'); pg.evaluate("TengelFx.set({ effects: true })")
        # 控えめ（calm のまま）：プレミアム → ハートの 雨や ポニーは 出さず ボードを ふわっと／超神様 → 動画を 出さず さいごの 1まい（still）→ 1.3秒で ボード
        pg.evaluate("(s) => TengelFx.show(Object.assign({ force: 'pc' }, s))", spec([11, 6, 2])); pg.wait_for_timeout(200); pg.evaluate('TengelFx.tap()'); pg.wait_for_timeout(300)
        check(pg.locator('#fxOv .fxs.calm .ov.pm').count() == 1 and pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.pm .pmp')).display") == 'none' and pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.pm .pms')).display") == 'none' and pg.locator('#fxOv .rb.fz .bh').inner_text() == 'ど的中！！！',
              '控えめの プレミアムど的中：ハートの 雨・ポニーは 出さない・ボードは ど的中の 形')
        pg.evaluate('TengelFx.close()')
        pg.evaluate("(s) => TengelFx.show(Object.assign({ force: 'sgd' }, s))", spec([11, 8, 2])); pg.wait_for_timeout(200); pg.evaluate('TengelFx.tap()'); pg.wait_for_timeout(400)
        cst = pg.evaluate('TengelFx.current()')
        check(cst['film'] == 2 and pg.locator('#fxOv .ov.sgd.still').count() == 1 and pg.locator('#fxOv .ov.sgd.go').count() == 0 and pg.locator('#fxOv video.sgv').count() == 0 and pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.sgd .sgs')).display") == 'block' and pg.locator('#fxOv .rb.fz .bh').inner_text() == '超神様的中！！！',
              f'控えめの 超神様的中：動画を 出さず さいごの 1まい（still）・見出し「超神様的中！！！」（{cst}）')
        pg.wait_for_timeout(1500)
        check(pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.sgd .hb')).opacity") == '1' and pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.sgd .hb')).visibility") == 'visible', '控えめの 超神様的中：1.3秒で ボードが ふわっと 出る')
        pg.evaluate('TengelFx.close()')
        pg.evaluate("(s) => TengelFx.show(Object.assign({ force: 'sd' }, s))", spec([11, 6, 2])); pg.wait_for_timeout(200); pg.evaluate('TengelFx.tap()'); pg.wait_for_timeout(400)
        csd = pg.evaluate('TengelFx.current()')
        check(csd['film'] == 2 and pg.locator('#fxOv .ov.sd.still').count() == 1 and pg.locator('#fxOv video.sgv').count() == 0 and pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.sd .sds')).display") == 'block' and pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.sd .pc')).display") == 'none',
              f'控えめの 紫電：プチュンも 動画も 出さず 動画の さいごの 1まい（still）（第4.71版）（{csd}）')
        pg.wait_for_timeout(1500)
        check(pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.sd .hb')).opacity") == '1' and pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.sd .sdk')).opacity") == '1', '控えめの 紫電：1.3秒で ボードが ふわっと 出る（うしろは 少し 暗く）')
        pg.evaluate('TengelFx.close()')
        pg.evaluate("TengelFx.set({ calm: null })")
        # 動画（Chromium では H.264 が 読めないので、同じ 絵の webm を 同じ 名前の かわりに 読ませる。なければ 動かない 時の 形を 確かめる）
        pg.evaluate("window.__FX.films = { sgd_film: 'sgd_film.webm', spg_up: 'spg_up.webm' }")
        HAVE_FILMS = pg.evaluate("fetch('sgd_film.webm', { method: 'HEAD' }).then(r => r.ok).catch(() => false)")
        pg.evaluate("window.__fxEv = []; document.addEventListener('tengel:fx', e => window.__fxEv.push(e.detail.phase + ':' + e.detail.kind))")
        pg.evaluate("(s) => TengelFx.show(Object.assign({ force: 'sgd' }, s))", spec([11, 8, 2], [('馬単', '的中', [[11, 8]])])); pg.wait_for_timeout(300)
        pg.evaluate('TengelFx.prime()')
        check(pg.locator('#fxVh video[data-film=sgd_film]').count() == 1 and pg.evaluate("document.querySelector('#fxVh video').preload") == 'auto' and pg.evaluate("document.querySelector('#fxVh video').muted") is True, '超神様の 動画は 出る 前に <video>（muted・playsinline・preload=auto）を 作って 読んでおく')
        pg.evaluate('TengelFx.tap()')
        if HAVE_FILMS:
            pg.wait_for_function("() => (TengelFx.current() || {}).film === 1", timeout=6000)
            v = pg.evaluate("(() => { const v = document.querySelector('#fxOv video.sgv.on'); return v ? { paused: v.paused, t: v.currentTime, cls: v.className } : null; })()")
            check(v is not None and v['paused'] is False and pg.locator('#fxOv .ov.sgd.go').count() == 1 and pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.sgd')).backgroundColor") == 'rgba(0, 0, 0, 0)' and 'film:sgd' in pg.evaluate('window.__fxEv'),
                  f'超神様的中：押すと 動画が 舞台で 動きだす（playing）→ go（幕が すきとおる・音と ボードの 時計は ここから）（{v}）')
            check(pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.sgd .hb')).opacity") == '0', '動画の 間は ボードは まだ 見えない（14.33秒から）')
            pg.wait_for_timeout(15600)   # ボード 14.33秒 →「とじる」14.78＋0.24＋0.3秒
            v2 = pg.evaluate("(() => { const v = document.querySelector('#fxOv video.sgv'); return { ended: v.ended || v.paused, t: Math.round(v.currentTime * 10) / 10 }; })()")
            check(pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.sgd .hb')).opacity") == '1' and pg.evaluate("getComputedStyle(document.querySelector('#fxOv .close')).visibility") == 'visible' and v2['ended'] and v2['t'] >= 14, f'14.33秒 ボード →「とじる」・動画は さいごの 1まいで 止まる（{v2}）')
        else:
            print('  ⚠️ 動画の webm が ない（ffmpeg で 作ると 動画の 流れも 確かめる）')
        pg.evaluate('TengelFx.close()'); pg.wait_for_timeout(200)
        check(pg.locator('#fxOv').count() == 0 and pg.locator('#fxVh video[data-film=sgd_film]').count() == 1 and pg.locator('#fxVh video[data-film=spg_up]').count() == 1 and pg.evaluate("[...document.querySelectorAll('#fxVh video')].every(v => v.paused && v.currentTime === 0 && !v.className)"), '「とじる」→ 動画は 止めて はじめに もどして 置き場へ（prime で 2つとも 作って ある）')
        # 動画が 読めない 時（ファイルが ない）→ さいごの 1まい → 1.3秒 ボード
        pg.evaluate("window.__FX.films = { sgd_film: 'nai_sgd_film.webm', spg_up: 'nai_spg_up.webm' }")   # ない 名前 → error → still
        pg.evaluate("(s) => TengelFx.show(Object.assign({ force: 'spg' }, s))", spec([11, 8, 2])); pg.wait_for_timeout(200); pg.evaluate('TengelFx.tap()'); pg.wait_for_timeout(1200)
        cst2 = pg.evaluate('TengelFx.current()')
        check(cst2['kind'] == 'spg' and cst2['film'] == 2 and pg.locator('#fxOv .ov.sgd.spg.still').count() == 1 and pg.locator('#fxOv .ov.spz.gone').count() == 1, f'超プレミアム神様的中で 動画が 読めない → 超プレミアムの 画面を 消して さいごの 1まい → ボード（{cst2}）')
        pg.wait_for_timeout(1400)   # 押して 2.6秒（さいごの 1まい → 1.3秒 ボード → 1.6秒 見出し → 1.7秒 帯）
        bh2 = pg.evaluate("(() => { const e = document.querySelector('#fxOv .ov.sgd .rb .bh'), z = document.querySelector('#fxOv .ov.sgd .rb .zrib'); const s = getComputedStyle(e); return { op: s.opacity, vis: s.visibility, t: e.innerText, rib: z ? getComputedStyle(z).opacity : null, ribt: z ? z.innerText.replace(/\\s+/g, '') : null }; })()")
        check(bh2['op'] == '1' and bh2['vis'] == 'visible' and bh2['t'] == '超神様的中！！！' and bh2['rib'] == '1' and bh2['ribt'] == '超大穴11大穴8が3連単に！', f'さいごの 1まいの ときの ボードの 見出し「超神様的中！！！」と 帯は ボードと いっしょに 出る（ど的中の 7.2秒を 待たない）（{bh2}）')
        pg.evaluate('TengelFx.close()')
        if HAVE_FILMS:
            pg.evaluate("window.__FX.films = { sgd_film: 'sgd_film.webm', spg_up: 'spg_up.webm' }")
            pg.evaluate("(s) => TengelFx.show(Object.assign({ force: 'spg' }, s))", spec([11, 8, 2], [('馬単', '的中', [[11, 8]])])); pg.wait_for_timeout(300)
            check(pg.locator('#fxOv .ov.fz .pbox.rbw .push .rbf').count() == 1 and pg.evaluate('TengelFx.current()')['pz'] == 1.6, '超プレミアム神様的中：PUSH は 1.6倍・虹色')
            pg.evaluate("window.__fxEv = []"); pg.evaluate('TengelFx.tap()'); pg.wait_for_timeout(500)
            ovs = pg.evaluate("[...document.querySelectorAll('#fxOv .fxs .ov')].map(o => o.className)")
            vids = pg.evaluate("[...document.querySelectorAll('#fxOv video')].map(v => v.className + ':' + v.getAttribute('data-film') + ':' + (v.paused ? 'p' : 'r'))")
            check(ovs == ['ov fz zp spz', 'ov fz sgd spg'] and sorted(vids) == ['sgv:sgd_film:p', 'spu:spg_up:p'] and pg.locator('#fxOv .ov.spz .zps').count() == 3 and pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.spz')).zIndex") == '32',
                  f'押すと 超プレミアムど的中の ①〜③（いちばん上）＋ 超神様の 幕・動画 2つは 一度 動かして 止めて おく（{ovs}・{vids}）')
            pg.wait_for_timeout(6200)
            c6 = pg.evaluate('TengelFx.current()')
            check(c6['sp'] == 2 and pg.locator('#fxOv .ov.spz.stop.gone').count() == 1 and pg.evaluate("document.querySelector('#fxOv video.spu').paused") is False and pg.evaluate("document.querySelector('#fxOv video.spu').classList.contains('on')") and 'up:spg' in pg.evaluate('window.__fxEv'),
                  f'6.0秒（き！）で 超プレミアムの 画面が 止まり（stop）→ 昇格の 動画が 動きだしたら 消す（gone）・昇格の 動画が 見える（{c6}）')
            pg.wait_for_function("() => (TengelFx.current() || {}).film === 1", timeout=12000)
            c12 = pg.evaluate('TengelFx.current()')
            vv = pg.evaluate("[...document.querySelectorAll('#fxOv video')].map(v => v.className + ':' + (v.paused ? 'p' : 'r'))")
            check(c12['sp'] == 3 and 'spu:p' in vv and 'sgv on:r' in vv and pg.locator('#fxOv .ov.sgd.spg.go').count() == 1 and pg.evaluate('window.__fxEv')[-1] == 'film:spg', f'昇格の 動画が おわる → 超神様の 動画（go）（{c12}・{vv}）')
            check(pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.sgd .hb')).opacity") == '0', '超神様の 動画の 間は ボードは まだ 見えない')
            pg.wait_for_timeout(15600)
            check(pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.sgd .hb')).opacity") == '1' and pg.evaluate("getComputedStyle(document.querySelector('#fxOv .close')).visibility") == 'visible' and pg.locator('#fxOv .rb.fz .bh').inner_text() == '超神様的中！！！' and '超大穴' in pg.locator('#fxOv .rb .zrib').inner_text() and '大穴' in pg.locator('#fxOv .rb .zrib').inner_text(),
                  '超神様の 動画の 14.33秒で ボード「超神様的中！！！」（帯は 超大穴と 大穴）')
            pg.evaluate('TengelFx.close()'); pg.wait_for_timeout(200)
            check(pg.locator('#fxVh video[data-film=sgd_film]').count() == 1 and pg.locator('#fxVh video[data-film=spg_up]').count() == 1 and pg.evaluate("[...document.querySelectorAll('#fxVh video')].every(v => v.paused && v.currentTime === 0)"), '「とじる」→ 動画 2つとも 止めて 置き場へ')
        # 第4.71版：紫電は 押した 瞬間に プチュン（CSS・動画を 待たない）→ 動画（sd_film）が 動きだしたら go（幕が すきとおる）→ 10.05秒 ボード／読めない → さいごの 1まい（still）→ 1.3秒 ボード
        # 第4.77版：極ど的中（紫電）は ノーマルど的中の 幕と 動画（nd_film・音 nd）から 入る → 動画の 5.34秒（白い 光に つつまれた 瞬間）で すぐ 極ど的中（プチュン → sd_film → 10.05秒 ボード）
        pg.evaluate("window.__FX.films = { sgd_film: 'sgd_film.webm', spg_up: 'spg_up.webm', sd_film: 'sd_film.webm', nd_film: 'nd_film.webm' }")
        HAVE_SD = pg.evaluate("Promise.all(['sd_film.webm', 'nd_film.webm'].map(u => fetch(u, { method: 'HEAD' }).then(r => r.ok).catch(() => false))).then(a => a.every(x => x))")
        pg.evaluate("(s) => TengelFx.show(Object.assign({ force: 'sd' }, s))", spec([11, 6, 2], [('馬単', '的中', [[11, 6]])])); pg.wait_for_timeout(300)
        check(pg.locator('#fxVh video[data-film=sd_film]').count() == 1 and pg.evaluate("document.querySelector('#fxVh video[data-film=sd_film]').preload") == 'auto'
              and pg.locator('#fxVh video[data-film=nd_film]').count() == 1 and pg.evaluate("document.querySelector('#fxVh video[data-film=nd_film]').preload") == 'auto',
              '極ど的中（紫電）の 動画と 入りの ノーマルど的中の 動画も 出る 前に <video>（preload=auto）を 作って 読んでおく（第4.70版・第4.77版）')
        pg.evaluate("window.__fxEv = []; window.__fxT = {}; document.addEventListener('tengel:fx', e => { if (!window.__fxT[e.detail.phase]) window.__fxT[e.detail.phase] = performance.now(); })")
        pg.evaluate("window.__fxT0 = performance.now()"); pg.evaluate('TengelFx.tap()'); pg.wait_for_timeout(120)
        pr0 = pg.evaluate("(() => { const o = document.querySelector('#fxOv .ov.nd'); const h = o && o.querySelector('.hb'); const k = document.querySelector('#fxOv .ov.ndp .ndfk'); const a = k && k.getAnimations ? k.getAnimations() : []; return { nd: !!o, sd: !!document.querySelector('#fxOv .ov.sd'), pc: document.querySelectorAll('#fxOv .pc').length, hb: !h || getComputedStyle(h).visibility === 'hidden' || getComputedStyle(h).opacity === '0', pre: (TengelFx.current() || {}).pre, ndp: !!document.querySelector('#fxOv .ov.ndp .pbox .push'), dim: a.length === 1 && a[0].playState === 'running' }; })()")
        check(pr0['nd'] and not pr0['sd'] and pr0['pc'] == 0 and pr0['hb'] and pr0['pre'] in (1, 2) and pr0['ndp'] and pr0['dim'],
              f'極ど的中（第4.77版）：押すと まず ノーマルど的中の 幕（プチュンなし・ボードなし）・押した PUSH の 画面が その場で 止まって 暗く なる（{pr0}）')
        if HAVE_SD:
            pg.wait_for_function("() => (TengelFx.current() || {}).pre === 2", timeout=6000)
            v = pg.evaluate("(() => { const v = document.querySelector('#fxOv video.sgv.on'); return v ? { paused: v.paused, film: v.getAttribute('data-film') } : null; })()")
            check(v is not None and v['paused'] is False and v['film'] == 'nd_film' and pg.locator('#fxOv .ov.nd.go').count() == 1 and 'pre:sd' in pg.evaluate('window.__fxEv') and pg.evaluate('TengelFx.current()')['film'] == 0,
                  f'極ど的中：ノーマルど的中の 動画が 舞台で 動きだす（{v}）')
            pg.wait_for_function("() => !document.querySelector('#fxOv .ov.ndp')", timeout=3000)
            check(pg.locator('#fxOv .ov.ndp').count() == 0 and (TengelFx_pre := pg.evaluate('TengelFx.current().pre')) == 2, f'極ど的中：押した PUSH の 画面は 暗く なりきったら 消える（ノーマルの 動画が 見える）（pre {TengelFx_pre}）')
            pg.wait_for_function("() => (TengelFx.current() || {}).pre === 4", timeout=9000)
            up = pg.evaluate("(() => { const p = document.querySelector('#fxOv .ov.sd .pc'); const a = p && p.getAnimations ? p.getAnimations() : []; const h = getComputedStyle(document.querySelector('#fxOv .ov.sd .hb')); return { nd: !!document.querySelector('#fxOv .ov.nd'), vid: document.querySelectorAll('#fxOv video.sgv.on').length, vis: p ? getComputedStyle(p).visibility : '', run: a.length > 0 && a.every(x => x.playState === 'running'), hb: h.visibility === 'hidden' || h.opacity === '0', t: Math.round(window.__fxT.up - window.__fxT.pre), gap: Math.round(window.__fxT.up - window.__fxT.blackout), ndv: document.querySelector('#fxVh video[data-film=nd_film]').paused }; })()")
            check(not up['nd'] and up['vis'] == 'visible' and up['run'] and up['hb'] and 5100 <= up['t'] <= 5800 and up['gap'] <= 30 and up['ndv'] and 'blackout:sd' in pg.evaluate('window.__fxEv') and 'up:sd' in pg.evaluate('window.__fxEv'),
                  f'極ど的中（第4.78版）：ノーマルの 動画の 5.34秒（白い 光に つつまれた 瞬間）で 動画と 音を 止めて すぐ プチュン（押した 瞬間と 同じ・ボードは まだ）（{up}）')
            pg.wait_for_function("() => (TengelFx.current() || {}).film === 1", timeout=6000)
            v = pg.evaluate("(() => { const v = document.querySelector('#fxOv video.sgv.on'); return v ? { paused: v.paused, film: v.getAttribute('data-film') } : null; })()")
            check(v is not None and v['paused'] is False and v['film'] == 'sd_film' and pg.locator('#fxOv .ov.sd.go').count() == 1 and pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.sd')).backgroundColor") == 'rgba(0, 0, 0, 0)' and 'film:sd' in pg.evaluate('window.__fxEv')
                  and pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.sd .hb')).opacity") == '0' and pg.locator('#fxOv video').count() == 1,
                  f'極ど的中：動画が 舞台で 動きだす（go・幕が すきとおる）・ボードは まだ 出ない（{v}）')
            pg.wait_for_timeout(1500)
            check(pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.sd .pc')).visibility") == 'hidden', '紫電：プチュンは 約1秒で おわる（あとは 動画）')
            pg.wait_for_timeout(7600)
            check(pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.sd .hb')).opacity") == '0', '紫電：9秒すぎ（ど！！！的中の 2.5秒）は まだ ボードを 出さない')
            pg.wait_for_timeout(1900)
            check(pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.sd .hb')).opacity") == '1' and pg.evaluate("getComputedStyle(document.querySelector('#fxOv .close')).visibility") == 'visible' and pg.locator('#fxOv .rb.fz .bh').inner_text() == 'ど的中！！！',
                  '紫電：10.05秒で ボード「ど的中！！！」→「とじる」')
        else:
            print('  ⚠️ 紫電・ノーマルど的中の 動画の webm が ない（ffmpeg で 作ると 動画の 流れも 確かめる）')
        pg.evaluate('TengelFx.close()'); pg.wait_for_timeout(200)
        check(pg.evaluate("[...document.querySelectorAll('#fxVh video')].every(v => v.paused && v.currentTime === 0)") and pg.locator('#fxOv').count() == 0, '極ど的中：「とじる」→ 動画（入りの ノーマルも）を 止めて 置き場へ')
        # 入りの とちゅうで とじる → 動画と 時刻の しかけが のこらない
        pg.evaluate("(s) => TengelFx.show(Object.assign({ force: 'sd' }, s))", spec([11, 6, 2])); pg.wait_for_timeout(200); pg.evaluate('TengelFx.tap()'); pg.wait_for_timeout(700)
        pg.evaluate('TengelFx.close()'); pg.wait_for_timeout(6500)
        check(pg.locator('#fxOv').count() == 0 and pg.evaluate("[...document.querySelectorAll('#fxVh video')].every(v => v.paused)"), '極ど的中：入りの とちゅうで「とじる」→ あとから ブラックアウト・極ど的中が 出て こない')
        pg.evaluate("window.__FX.films = { sgd_film: 'sgd_film.webm', spg_up: 'spg_up.webm', sd_film: 'nai_sd_film.webm', nd_film: 'nai_nd_film.webm' }")   # ない 名前 → error → still
        pg.evaluate("(s) => TengelFx.show(Object.assign({ force: 'sd' }, s))", spec([11, 6, 2])); pg.wait_for_timeout(200); pg.evaluate('TengelFx.tap()'); pg.wait_for_timeout(1600)
        cst3 = pg.evaluate('TengelFx.current()')
        check(cst3['kind'] == 'sd' and cst3['film'] == 2 and cst3['pre'] == 4 and pg.locator('#fxOv .ov.sd.still').count() == 1 and pg.locator('#fxOv .ov.sd.go').count() == 0 and pg.locator('#fxOv .ov.nd').count() == 0 and pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.sd .sds')).display") == 'block',
              f'紫電で 動画が 読めない（入りの ノーマルの 動画も）→ すぐ 極ど的中の さいごの 1まい（still）（{cst3}）')
        pg.wait_for_timeout(1400)
        bh3 = pg.evaluate("(() => { const e = document.querySelector('#fxOv .ov.sd .rb .bh'); const s = getComputedStyle(e); return { op: s.opacity, vis: s.visibility, t: e.innerText, hb: getComputedStyle(document.querySelector('#fxOv .ov.sd .hb')).opacity }; })()")
        check(bh3['op'] == '1' and bh3['hb'] == '1' and bh3['t'] == 'ど的中！！！' and pg.evaluate("window.__FX.t.SDUP") == {'AT': 5.34, 'BLACK': 0}, f'紫電の still：1.3秒で ボード・見出しも ボードと いっしょに（{bh3}）')
        pg.evaluate('TengelFx.close()'); pg.wait_for_timeout(100)
        # 第4.77版：ノーマルど的中（nd）：くじの ど的中（紫電で ない）→ PUSH は ど的中と 同じ → 押すと 1秒 真っ暗（プチュンは なし）→ 動画（nd_film）が 動きだしたら go → 10.05秒 ボード（さいごの 場面を 2.3秒 のばした）／読めない → still → 1.3秒 ボード
        pg.evaluate("window.__FX.films = { sgd_film: 'sgd_film.webm', spg_up: 'spg_up.webm', sd_film: 'sd_film.webm', nd_film: 'nd_film.webm' }")
        HAVE_ND = pg.evaluate("fetch('nd_film.webm', { method: 'HEAD' }).then(r => r.ok).catch(() => false)")
        pg.evaluate("window.__seq([0.5, 0.9])")
        kn = pg.evaluate("(s) => TengelFx.show(s)", spec([11, 6, 2], [('馬単', '的中', [[11, 6]])])); pg.wait_for_timeout(300)
        po = pg.locator('#fxOv')
        check(kn == 'nd' and pg.locator('#fxVh video[data-film=nd_film]').count() == 1 and pg.evaluate("document.querySelector('#fxVh video[data-film=nd_film]').preload") == 'auto'
              and po.locator('.ov.fz .pbox.pz .push').count() == 1 and po.locator('.pbox.rbw').count() == 0 and 'k-nd' in po.get_attribute('class') and pg.evaluate('TengelFx.current()')['pz'] == 1.4,
              f'ノーマルど的中（第4.77版）：くじの ど的中（乱数 0.5・0.9）→ nd・PUSH は ど的中と 同じ（1.4倍）・動画を 出る 前に 読んでおく（{kn}）')
        pg.evaluate("window.__fxEv = []"); pg.evaluate('TengelFx.tap()'); pg.wait_for_timeout(150)
        nd0 = pg.evaluate("(() => { const o = document.querySelector('#fxOv .ov.nd'); const h = getComputedStyle(document.querySelector('#fxOv .ov.nd .hb')); const p = document.querySelector('#fxOv .ov.ndp'); const k = p && p.querySelector('.ndfk'); const a = k && k.getAnimations ? k.getAnimations() : []; const pa = p ? p.querySelector('.pbox').getAnimations({ subtree: true }).filter(x => x instanceof CSSAnimation) : []; return { pc: document.querySelectorAll('#fxOv .ov.nd .pc').length, bg: getComputedStyle(o).backgroundColor, cls: o.className, hb: h.visibility === 'hidden' || h.opacity === '0', img: [...o.querySelectorAll('img')].map(i => i.src.split('/').pop()), ndp: !!(p && p.querySelector('.pbox .push')), z: p ? getComputedStyle(p).zIndex : '', dim: a.length === 1 && a[0].playState === 'running', frozen: pa.every(x => x.playState === 'paused'), sc: p ? getComputedStyle(p.querySelector('.pbox')).scale : '' }; })()")
        check(nd0['pc'] == 0 and (nd0['bg'] == 'rgb(0, 0, 0)' or 'go' in nd0['cls']) and nd0['hb'] and nd0['img'] == ['nd_last.webp'] and 'fz' in nd0['cls'],   # 動画が もう 動いて いれば go（はじめの 1秒は 動画の 黒）
              f'ノーマルど的中：押すと 暗く なる（プチュンは なし）・ボードは まだ・絵は 動画の さいごの 1まい だけ（{nd0}）')
        check(nd0['ndp'] and nd0['z'] == '40' and nd0['dim'] and nd0['frozen'] and nd0['sc'] not in ('', 'none', '1'),
              f'ノーマルど的中（第4.78版）：押した PUSH の 画面が その場で 止まって（押した 形）上に のこり、0.1秒から 0.62秒で 暗く なる（いきなり 暗く しない）（{nd0}）')
        if HAVE_ND:
            pg.wait_for_function("() => (TengelFx.current() || {}).film === 1", timeout=6000)
            v = pg.evaluate("(() => { const v = document.querySelector('#fxOv video.sgv.on'); return v ? { paused: v.paused, film: v.getAttribute('data-film') } : null; })()")
            check(v is not None and v['paused'] is False and v['film'] == 'nd_film' and pg.locator('#fxOv .ov.nd.go').count() == 1 and pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.nd')).backgroundColor") == 'rgba(0, 0, 0, 0)' and 'film:nd' in pg.evaluate('window.__fxEv')
                  and pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.nd .hb')).opacity") == '0',
                  f'ノーマルど的中：動画が 舞台で 動きだす（go・幕が すきとおる）・ボードは まだ（{v}）')
            pg.evaluate("window.__goT = performance.now()")
            pg.wait_for_function("() => !document.querySelector('#fxOv .ov.ndp')", timeout=3000)
            check(pg.locator('#fxOv .ov.ndp').count() == 0, 'ノーマルど的中：押した PUSH の 画面は 暗く なりきったら 消える（動画が 見える）')
            pg.wait_for_function("() => performance.now() - window.__goT > 9300", timeout=12000)
            check(pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.nd .hb')).opacity") == '0', 'ノーマルど的中：9.3秒の ところ（ど！的中が 芝で 光って いる：のばした 場面）は まだ ボードを 出さない')
            pg.wait_for_function("() => performance.now() - window.__goT > 11000", timeout=4000)
            check(pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.nd .hb')).opacity") == '1' and pg.evaluate("getComputedStyle(document.querySelector('#fxOv .close')).visibility") == 'visible' and pg.locator('#fxOv .rb.fz .bh').inner_text() == 'ど的中！！！',
                  'ノーマルど的中：10.05秒で ボード「ど的中！！！」→「とじる」')
        else:
            print('  ⚠️ ノーマルど的中の 動画の webm が ない（ffmpeg で 作ると 動画の 流れも 確かめる）')
        pg.evaluate('TengelFx.close()'); pg.wait_for_timeout(200)
        pg.evaluate("window.__FX.films = { sgd_film: 'sgd_film.webm', spg_up: 'spg_up.webm', sd_film: 'sd_film.webm', nd_film: 'nai_nd_film.webm' }")   # ない 名前 → error → still
        pg.evaluate("(s) => TengelFx.show(Object.assign({ force: 'nd' }, s))", spec([11, 6, 2])); pg.wait_for_timeout(200); pg.evaluate('TengelFx.tap()'); pg.wait_for_timeout(1200)
        cst4 = pg.evaluate('TengelFx.current()')
        check(cst4['kind'] == 'nd' and cst4['film'] == 2 and pg.locator('#fxOv .ov.nd.still').count() == 1 and pg.locator('#fxOv .ov.nd.go').count() == 0 and pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.nd .nds')).display") == 'block',
              f'ノーマルど的中で 動画が 読めない → 動画の さいごの 1まい（still）（{cst4}）')
        pg.wait_for_timeout(1400)
        bh4 = pg.evaluate("(() => { const e = document.querySelector('#fxOv .ov.nd .rb .bh'); const s = getComputedStyle(e); return { op: s.opacity, t: e.innerText, hb: getComputedStyle(document.querySelector('#fxOv .ov.nd .hb')).opacity }; })()")
        check(bh4['op'] == '1' and bh4['hb'] == '1' and bh4['t'] == 'ど的中！！！' and pg.evaluate("window.__FX.art.nd") == ['nd_last.webp'] and pg.evaluate("window.__FX.t.ND") == 9.9
              and pg.evaluate("window.__FX.t.NDS") == {'FROM': 9.8, 'WAIT': 1.0} and pg.evaluate("window.__FX.sfx.nd") == 'sfx_nd.m4a' and pg.evaluate("window.__FX.films.nd_film") is not None
              and pg.evaluate("window.__FX.css.includes('fxsdBoard .5s cubic-bezier(.2,.9,.3,1.1) 10.05s both')"),
              f'ノーマルど的中の still：1.3秒で ボード・音は sfx_nd（still は 9.8秒から）・ボードは 動画の 10.05秒（{bh4}）')
        pg.evaluate('TengelFx.close()'); pg.wait_for_timeout(100)
        # プレミアムど的中・超プレミアムど的中・神様的中（CSS と SVG）：押したあとの 部品と ボード
        for kind, cls, parts, title, ribs in (('pc', 'pm', ('.pmbg', '.pmp', '.pms', '.pmf', '.pmw'), 'ど的中！！！', '11番人気が3連単に！'),
                                              ('zp', 'zp', ('.zpbg', '.zpp', '.zps', '.zpf', '.zpgr'), 'ど的中！！！', '11番人気が3連単に！'),
                                              ('gd', 'gd', ('.gdk', '.gdA', '.gdB', '.gdC'), '神様的中！！！', 'が3連単に！'),
                                              ('sd', 'sd', ('.sds', '.sdk', '.pc'), 'ど的中！！！', '11番人気が3連単に！')):
            pg.evaluate("(s) => TengelFx.show(Object.assign({ force: '%s' }, s))" % kind, spec([11, 8, 2] if kind == 'gd' else [11, 6, 2], [('馬単', '的中', [[11, 6]])])); pg.wait_for_timeout(200)
            po = pg.locator('#fxOv')
            okp = (po.locator('.ov.fz .pbox.rbw .push .rbf').count() == (0 if kind == 'sd' else 1)) and f'k-{kind}' in po.get_attribute('class') and (kind != 'sd' or pg.evaluate('TengelFx.current()')['pz'] == 1.4)   # 紫電の PUSH は ど的中と 同じ（1.4倍・虹色なし）
            pg.evaluate('TengelFx.tap()'); pg.wait_for_timeout(400)
            if kind == 'sd':   # 第4.77版：極ど的中は ノーマルど的中の 入り（ここでは 動画の 名前が ない → すぐ 極ど的中）のあと
                pg.wait_for_function("() => !!document.querySelector('#fxOv .ov.sd')", timeout=8000)
            have = {p_: po.locator(f'.ov.{cls} {p_}').count() for p_ in parts}
            imgs_bad = pg.evaluate("[...document.querySelectorAll('#fxOv img')].filter(i => i.complete && i.naturalWidth === 0 && !/sgd_last|pm_|gd_|sd_/.test(i.src)).length")
            check(okp and po.locator(f'.fxs .ov.fz.{cls}').count() == 1 and all(have.values()) and po.locator('.rb.fz .bh').text_content() == title and ribs in po.locator('.rb .zrib').text_content() and imgs_bad == 0 and po.locator('.rb .brows li.top .bt').text_content() == '3連単',   # ボードは まだ 見えない（text_content）
                  f'{kind}：PUSH は ど的中と 同じ → 押したあとの 部品（{"・".join(parts)}）→ ボード「{title}」・3連単の 行が いちばん上（{have}）')
            if kind == 'sd':   # 第4.71版：紫電は 絵を 使わない（ど！！！的中も 動画の 中の 3D）。さいごの 1まいと プチュン（ど的中と 同じ 部品）・ボードは 10.05秒
                srcs = pg.evaluate("[...new Set([...document.querySelectorAll('#fxOv .ov.sd img')].map(i => i.src.split('/').pop()))].sort()")
                check(srcs == ['sd_last.webp'] and po.locator('.ov.sd .pc .pcl').count() == 1 and po.locator('.ov.sd .pc .pca path').count() > 20
                      and po.locator('.ov.sd .sdC, .ov.sd .sdlogo, .ov.sd .sdbt, .ov.sd .sdar').count() == 0
                      and pg.evaluate("window.__FX.css.includes('fxsdBoard .5s cubic-bezier(.2,.9,.3,1.1) 10.05s both')") and pg.evaluate("window.__FX.t.SD") == 9.9
                      and pg.evaluate("window.__FX.art.sd") == ['sd_last.webp'] and pg.evaluate("window.__FX.t.SDS") == {'FROM': 9.8, 'WAIT': 1.0} and pg.evaluate("window.__FX.sfx.sdp") == 'sfx_sdp.m4a',
                      f'紫電（第4.71版）：絵は さいごの 1まい だけ（{srcs}）・押した 瞬間の プチュンは ど的中と 同じ 部品・音は sfx_sdp・ボードは 10.05秒')
            pg.evaluate('TengelFx.close()'); pg.wait_for_timeout(100)
        pg.evaluate("TengelFx._rand = null")
        # 着せ替えの テーマで：プレミアムの ボードは その テーマの ど的中の 形（第4弾・16.4）
        pg.evaluate("TengelKisekae.apply('sakura')"); pg.wait_for_timeout(600)
        pg.evaluate("(s) => TengelFx.show(Object.assign({ force: 'pc' }, s))", spec([11, 6, 2])); pg.wait_for_timeout(200); pg.evaluate('TengelFx.tap()'); pg.wait_for_timeout(300)
        rbk = pg.locator('#fxOv .rb')
        check(rbk.count() == 1 and 't-sakura' in rbk.get_attribute('class') and 'fz' in rbk.get_attribute('class') and pg.locator('#fxOv .ov.pm').count() == 1, f'桜の テーマでも プレミアムど的中は 同じ・ボードは 桜の ど的中の 形（{rbk.get_attribute("class")}）')
        pg.evaluate('TengelFx.close()'); pg.evaluate("TengelKisekae.apply('default')"); pg.wait_for_timeout(400)
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
        # ---- 着せ替え（第4弾・9章・16.1・16.1.1・16.2.1・16.4）：設定の「着せ替え」・30テーマ・名前と値段（9.1）・解放（P）→ 着せ替わる・上の絵（動く壁紙）・テーマの的中PUSHとボード・帯のミッション（8.3） ----
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(400)
        ks = pg.locator('#setKisekae')
        check(ks.count() == 1 and ks.locator('.kst').count() == 30 and ks.locator('.ksg').count() == 6 and ks.locator('.kst.on').get_attribute('data-ks') == 'default' and ks.locator('.kst.lock').count() == 29 and pg.evaluate("TengelKisekae.current()") == 'default' and pg.evaluate("document.documentElement.dataset.ks") is None,
              '設定に「着せ替え」：6つの組・30テーマ・いつものが使用中・ほかの29はカギ')
        names = ks.locator('.kst .ksn').all_inner_texts()
        check(names[:5] == ['いつもの', '牧場', 'かわいいお馬さん', '毛糸のお馬とロボット', 'ぷりけつのお馬'] and names[5:16] == ['桜', '海', '夕焼け', '紅葉', '雪', 'お正月', '花火', 'クリスマス', 'ハロウィン', 'バレンタイン', 'ホワイトデー']
              and names[16:20] == ['ナイター', '競馬新聞', '勝負服', '招き馬'] and names[20:22] == ['水墨画', '大理石の馬'] and names[22:27] == ['ネオン', 'ドット', '黒板', 'メリーゴーランド', '星座'] and names[27:] == ['シルバー帯', 'ゴールド帯', 'マスター帯'],
              f'9.1 の名前と並び（定番5・季節・行事11・競馬4・和・アート2・レトロ・ポップ5・帯3）：{names[:6]}…')
        locks = ks.locator('.kst .kslock').all_inner_texts()
        check(locks.count('🔒 1,000P') == 5 and locks.count('🔒 2,000P') == 6 and locks.count('🔒 3,000P') == 4 and locks.count('🔒 4,000P') == 8 and locks.count('🔒 7,000P') == 3 and locks.count('🔒 壁紙を8枚あつめると') == 1 and locks.count('🔒 壁紙を16枚あつめると') == 1 and locks.count('🔒 壁紙を25枚あつめると') == 1,
              '値段（9.1）：1,000P×5・2,000P×6・3,000P×4・4,000P×8・7,000P×3・帯は 8・16・25枚')
        check(ks.locator('.kst[data-ks=sakura] .ksth').get_attribute('src') == 'ks_39558c280310609ad0a65971ed217991.webp' and ks.locator('.kst[data-ks=ranch] .ksth').get_attribute('src') == 'ks_banner_ranch.svg' and ks.locator('.kst[data-ks=default] .ksth').get_attribute('src') == 'ks_c1fccd55173e28903228b7256479cc32.webp',
              '小さな絵：新しいテーマは止まった上の絵（WebP）・定番は SVG・いつものは見本と同じ')
        # 招き馬（7,000P・いま 7,000P）→ タップした タイルの 中（カギの 下）に 確認が出る（第4.64版：前は 一覧の 上の 帯）→ やめる。
        # 1,000P 使ったあと（6,000P）だと「Pが足りないよ」と「ポイントを買う」
        check(ks.locator('.kst').first.evaluate("e => e.tagName + '/' + e.getAttribute('role') + '/' + e.tabIndex") == 'DIV/button/0', '壁紙の タイルは <div role=button tabindex=0>（中に 本物の ボタンを 置くため）')
        ks.locator('.kst[data-ks=lucky]').click(); pg.wait_for_timeout(300)
        cf = ks.locator('.ksconf')
        check(cf.count() == 1 and ks.locator('.kst[data-ks=lucky].cf .ksconf').count() == 1 and ks.locator('.kst[data-ks=lucky]').get_attribute('aria-expanded') == 'true'
              and '7,000Pを使って解放する？' in cf.inner_text() and 'いま 7,000P' in cf.inner_text() and cf.locator('[data-ksact=unlock]').count() == 1 and cf.locator('[data-ksact=cancel]').count() == 1,
              f'カギの壁紙をタップ → その タイルの 中に 「○○Pを使って解放する？ いま △△P」「解放する」「やめる」（{cf.inner_text()[:50]!r}）')
        cfb = ks.locator('.kst[data-ks=lucky]').bounding_box(); unb = cf.locator('[data-ksact=unlock]').bounding_box(); lkb = ks.locator('.kst[data-ks=lucky] .kslock').bounding_box()
        check(cfb and unb and lkb and unb['y'] > lkb['y'] + lkb['height'] - 1 and unb['x'] >= cfb['x'] and unb['x'] + unb['width'] <= cfb['x'] + cfb['width'] + 1 and unb['y'] + unb['height'] <= cfb['y'] + cfb['height'] + 1,
              '「解放する」は カギ（🔒 7,000P）の 下・タイルの 中')
        check(ks.locator('.ksbody > .ksconf').count() == 0 and ks.locator('.ksbody > div.ksconf').count() == 0, '一覧の 上の 確認の 帯は ない')
        ks.locator('.kst[data-ks=lucky]').click(position={'x': 10, 'y': 10}); pg.wait_for_timeout(200)
        check(ks.locator('.ksconf').count() == 0 and ks.locator('.kst.cf').count() == 0, 'もう一度 タイルを タップ → 閉じる')
        ks.locator('.kst[data-ks=lucky]').click(); pg.wait_for_timeout(300)
        ks.locator('.ksconf [data-ksact=cancel]').click(); pg.wait_for_timeout(200)
        check(ks.locator('.ksconf').count() == 0 and pg.evaluate('TengelWallet.total()') == 7000 and pg.evaluate("TengelKisekae.current()") == 'default', 'やめると何も変わらない')
        # 桜（1,000P）を解放 → 着せ替わる
        ks.locator('.kst[data-ks=sakura]').click(); pg.wait_for_timeout(300)
        ks.locator('.ksconf [data-ksact=unlock]').click(); pg.wait_for_timeout(1200)
        check(pg.evaluate('TengelWallet.total()') == 6000 and pg.evaluate("TengelWallet.unlocked('theme:sakura')") and pg.evaluate("document.documentElement.dataset.ks") == 'sakura' and pg.evaluate("TengelKisekae.current()") == 'sakura' and pg.evaluate("TengelKisekae.loaded()")
              and ks.locator('.kst.on').get_attribute('data-ks') == 'sakura' and ks.locator('.kst[data-ks=sakura] .kslock').count() == 0 and ks.locator('.kst[data-ks=sakura] .ksbadge').inner_text() == '使用中' and '壁紙：1/26枚' in ks.inner_text() and pg.evaluate("localStorage.getItem('tengel.kisekae')") == 'sakura',
              f'解放する → 1,000P 使って 桜に着せ替わる（台帳 unlock-theme:sakura・使用中・1/26枚・端末に覚える）')
        check(pg.evaluate("getComputedStyle(document.body).backgroundColor") == 'rgb(255, 246, 248)' and 'Zen Kaku Gothic New' in pg.evaluate("getComputedStyle(document.body).fontFamily") and 'Kaisei Decol' in pg.evaluate("getComputedStyle(document.querySelector('.brand h1')).fontFamily")
              and pg.evaluate("getComputedStyle(document.querySelector('.top')).borderBottomColor") == 'rgb(238, 157, 184)' and pg.evaluate("getComputedStyle(document.querySelector('.tabbar button[aria-selected=true]')).backgroundColor") == 'rgb(252, 227, 235)',
              '桜の色と字：背景・本文（Zen Kaku Gothic New）・見出し（Kaisei Decol）・上の帯のふち・タブ')
        check(pg.evaluate("document.fonts.check('700 16px \"Kaisei Decol\"') || [...document.fonts].some(f => f.family.replace(/\"/g, '') === 'Kaisei Decol')") and 'KaiseiDecol-700.woff2' in pg.evaluate("[...document.styleSheets].map(s => { try { return [...s.cssRules].filter(r => r instanceof CSSFontFaceRule).map(r => r.cssText).join() } catch (e) { return '' } }).join()"),
              'テーマの字はアプリの中のフォント（fonts/KaiseiDecol-700.woff2・Google に通信しない）')
        # 帯：シルバー帯をタップ → ミッションの案内（まだ使えない）
        ks.locator('.kst[data-ks=silver]').click(); pg.wait_for_timeout(300)
        check('壁紙を8枚あつめて、ミッションで受け取ると使えるよ（いま 1枚）' in pg.locator('#toast').inner_text() and pg.evaluate("TengelKisekae.current()") == 'sakura', '帯の壁紙をタップ → ミッションの案内（いま 1枚）')
        pg.locator('#setPoints [data-pt=show][data-v=hist]').click(); pg.wait_for_timeout(300)
        check('解放：壁紙「桜」' in pg.locator('#setPoints .pthist').inner_text() and '-1,000P' in pg.locator('#setPoints .pthist').inner_text(), 'ポイントの履歴に「解放：壁紙「桜」」')
        pg.locator('#setPoints [data-pt=show][data-v=hist]').click(); pg.wait_for_timeout(200)
        pg.screenshot(path=os.path.join(W, 't4', 'native_kisekae_set.png'), full_page=False)
        # 判定タブ：上の帯 → 桜の上の絵（動く壁紙・390×160）→ レース情報
        pg.click('.tabbar button[data-tab=judge]'); pg.wait_for_timeout(600)
        bn = pg.locator('#ksBnr')
        bb = bn.bounding_box()
        check(bn.count() == 1 and not bn.evaluate('e => e.hidden') and bn.locator('.bnrw').count() == 1 and bn.locator('img.bnr').get_attribute('src') == 'ks_39558c280310609ad0a65971ed217991.webp' and abs(bb['height'] - 160) < 1 and abs(bb['width'] - 390) < 1
              and pg.evaluate("document.querySelector('#ksBnr').getAnimations({ subtree: true }).length") > 10 and bn.evaluate("e => e.previousElementSibling") is None and bn.evaluate("e => e.nextElementSibling.id") == 'w5Banner',
              f'判定タブのいちばん上に 桜の上の絵（390×160・花びらと馬の動き・{pg.evaluate("document.querySelector(\'#ksBnr\').getAnimations({ subtree: true }).length")}の動き）')
        check(pg.evaluate("document.documentElement.scrollWidth") <= 390 and pg.evaluate("document.querySelector('#fxCss') !== null && document.querySelector('#ksTheme').textContent.includes('.fxs .rb.t-sakura')"), '横にはみ出さない・テーマのボードの CSS が入っている')
        # 「演出を控えめにする」→ 壁紙も止まった絵（.calm）。もどすと動く。アプリが裏（判定タブ以外）では .pause
        pg.evaluate("TengelFx.set({ calm: true })"); pg.wait_for_timeout(100)
        check(bn.evaluate("e => e.classList.contains('calm')"), '演出を控えめにする → 壁紙は止まった絵（.calm）')
        pg.evaluate("TengelFx.set({ calm: false })"); pg.wait_for_timeout(100)
        check(not bn.evaluate("e => e.classList.contains('calm')"), 'もどすと動く')
        pg.click('.tabbar button[data-tab=rec]'); pg.wait_for_timeout(200)
        check(bn.evaluate("e => e.classList.contains('pause')"), '判定タブが見えていない間は壁紙の動きを止める（.pause ※仮）')
        pg.click('.tabbar button[data-tab=judge]'); pg.wait_for_timeout(200)
        check(not bn.evaluate("e => e.classList.contains('pause')"), '判定タブにもどると動く')
        # 的中ボタン：桜の PUSH（面の SVG・はじける花びら）→ 桜のボード。デカ的中の PUSH は全テーマ共通・ボードは桜
        pg.evaluate("(s) => TengelFx.show(s)", spec(None, [('馬単', '的中', [[6, 2]]), ('単勝', '的中', [[6]])])); pg.wait_for_timeout(300)
        fk = pg.locator('#fxOv')
        check(fk.locator('.push.sk svg').count() >= 1 and fk.locator('.pshadow.sk').count() == 1 and fk.locator('.tap.sk').inner_text() == 'タップ！' and pg.evaluate('TengelFx.current()')['theme'] == 'sakura', '的中 → 桜の PUSH（桜の枝と花の面・タップ！）')
        pg.screenshot(path=os.path.join(W, 't4', 'native_kisekae_push.png'), full_page=False)
        fk.locator('.push').click(force=True); pg.wait_for_timeout(2300)
        check(fk.locator('.pressed.sk svg').count() >= 1 and fk.locator('.fxs .ov.hit .petals, .fxs .ov.hit .clips, .fxs .ov.hit [class*=pet]').count() >= 1 and 't-sakura' in fk.locator('.rb').get_attribute('class') and fk.locator('.rb .bh').text_content() == '的中！' and fk.locator('.rb .orn').count() == 1 and fk.locator('.rb .brows li').count() == 3,
              '押すと 桜の花びらが舞って → 桜のボード（すみに桜の飾り・券種ごとの行）')
        pg.screenshot(path=os.path.join(W, 't4', 'native_kisekae_board.png'), full_page=False)
        pg.evaluate('TengelFx.close()'); pg.wait_for_timeout(200)
        pg.evaluate("(s) => TengelFx.show(s)", spec([8, 5, 2])); pg.wait_for_timeout(300)
        check(fk.locator('.ov.big .pbox.pz .push.sk svg').count() >= 1 and fk.locator('.push.big').count() == 0 and pg.evaluate('TengelFx.current()')['theme'] == 'sakura' and pg.evaluate('TengelFx.current()')['pz'] == 1.2 and fk.locator('.ov.big .spk').count() == 1, 'デカ的中の PUSH も 桜の PUSH（1.2倍・まわりは デカ的中の きらめき・第4.60版）')
        fk.locator('.push').click(force=True); pg.wait_for_timeout(800)
        check('t-sakura' in fk.locator('.rb').get_attribute('class') and fk.locator('.rb.big .bh').text_content() == 'デカ的中!!', 'デカ的中のボードは桜')
        pg.evaluate('TengelFx.close()'); pg.wait_for_timeout(200)
        # 開き直しても桜（起動の瞬間から色が出る）
        pg.reload()
        ks0 = pg.evaluate("document.documentElement.dataset.ks")
        pg.wait_for_timeout(800); gate(pg); pg.wait_for_timeout(1200)
        check(ks0 == 'sakura' and pg.evaluate("TengelKisekae.current()") == 'sakura' and not pg.locator('#ksBnr').evaluate('e => e.hidden'), f'開き直しても桜（開いた瞬間から：{ks0}）')
        # 壁紙のミッション（8.3）：ポイントで解放した壁紙が 8枚 → 「受け取る」→ シルバー帯が使える（帯は枚数に数えない）
        pg.evaluate("""(async () => { const w = await TengelLocal.getMeta('wallet'); for (const t of ['sea', 'autumn', 'snow', 'newyear', 'news', 'ink', 'stars']) w.events.push({ id: 'unlock-theme:' + t, kind: 'unlock', bucket: '', amount: 0, at: new Date().toISOString(), use: { paid_sub: 0, paid_pack: 0, free: 0 }, what: 'theme:' + t, device: 'x' }); await TengelLocal.putMeta(w); })()""")
        pg.reload(); pg.wait_for_timeout(800); gate(pg); pg.wait_for_timeout(1200)
        check(pg.evaluate("TengelKisekae.count()") == 8 and pg.locator('.tabbar [data-tab=set] .tbdg').count() == 1, '壁紙を8枚解放 → 受け取れるミッションの印')
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(400)
        wm = pg.locator('#setMission')
        check('壁紙のミッション' in wm.inner_text() and 'いま 8枚' in wm.inner_text() and '壁紙を8枚あつめる' in wm.inner_text() and wm.locator('[data-pt=claim][data-id="mission-wall-8"]').count() == 1 and wm.locator('[data-pt=claim][data-id="mission-wall-16"]').count() == 0 and 'あと 8枚（8/16）' in wm.inner_text(),
              'ミッションに「壁紙のミッション」：8枚で「受け取る」・16枚は あと8枚')
        wm.locator('[data-pt=claim][data-id="mission-wall-8"]').click(); pg.wait_for_timeout(700)
        check(pg.evaluate("TengelWallet.unlocked('theme:silver')") and pg.evaluate("TengelKisekae.usable('silver')") and pg.evaluate("TengelKisekae.count()") == 8 and pg.evaluate('TengelWallet.total()') == 6000 and wm.locator('[data-pt=claim]').count() == 0 and pg.locator('.tabbar [data-tab=set] .tbdg').count() == 0 and 'シルバー帯の壁紙を受け取ったよ' in pg.locator('#toast').inner_text(),
              '受け取る → シルバー帯が使える（0P・枚数は8のまま・印が消える）')
        check(ks.locator('.kst[data-ks=silver] .kslock').count() == 0 and ks.locator('.kst[data-ks=golden] .kslock').inner_text() == '🔒 壁紙を16枚あつめると', '着せ替えのカード：シルバー帯のカギが外れる・ゴールド帯は16枚')
        ks.locator('.kst[data-ks=silver]').click(); pg.wait_for_timeout(1200)
        check(pg.evaluate("TengelKisekae.current()") == 'silver' and pg.evaluate("document.documentElement.dataset.ks") == 'silver' and ks.locator('.kst.on').get_attribute('data-ks') == 'silver', 'シルバー帯に着せ替わる')
        pg.click('.tabbar button[data-tab=judge]'); pg.wait_for_timeout(500)
        check(pg.locator('#ksBnr .mxsw').count() == 1 and pg.evaluate("document.documentElement.scrollWidth") <= 390, 'シルバー帯の上の絵（像と きらめき）・横にはみ出さない')
        # 全テーマ：文字と背景のコントラスト 4.5以上（判定・設定の主な文字）・横にはみ出さない・馬番の枠の色は同じ・絵がなくても落ちない（この srv には絵がない）
        CONTRAST = """() => {
          const lum = c => { const m = c.match(/[\\d.]+/g); if (!m || m.length < 3) return null; const a = m.length > 3 ? +m[3] : 1; if (a < .99) return null; const f = v => { v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }; return .2126 * f(+m[0]) + .7152 * f(+m[1]) + .0722 * f(+m[2]); };
          const bgOf = el => { for (let e = el; e; e = e.parentElement) { const cs = getComputedStyle(e); if (cs.backgroundImage !== 'none') return 'img'; const L = lum(cs.backgroundColor); if (L != null) return L; } return lum(getComputedStyle(document.body).backgroundColor); };
          const out = [];
          const sels = ['.brand h1', '.card h2', '.f > label', '.hint', '.btn.primary', '.seg button[aria-pressed=true]', '.tabbar button', '.tabbar button[aria-selected=true]', '.chip', '.fchip', '.zrank', '.zflow', '.lbadge .ll', 'input[type=number]', '.ocrHint, #ocrHint', '.ptnote', '#setKisekae .ksn', '#setKisekae .ksd', '#setKisekae .kslock', '.msrow .md', '.pthist li'];
          sels.forEach(s => { const el = document.querySelector(s); if (!el || !el.offsetParent) return; const cs = getComputedStyle(el); const L1 = lum(cs.color), bg = bgOf(el); if (L1 == null || bg == null || bg === 'img') return; const c = (Math.max(L1, bg) + .05) / (Math.min(L1, bg) + .05); out.push([s, +c.toFixed(2)]); });
          return out; }"""
        low, wide, wk = [], [], []
        for tid in pg.evaluate("TengelKisekae.list().map(t => t.id)"):
            pg.evaluate("(id) => TengelKisekae.apply(id)", tid); pg.wait_for_timeout(350)
            for tab in ('judge', 'set'):
                pg.click(f'.tabbar button[data-tab={tab}]'); pg.wait_for_timeout(120)
                for sel, c in pg.evaluate(CONTRAST):
                    if c < (3.0 if '.lbadge' in sel else 4.5): low.append(f'{tid} {tab} {sel} {c}')   # 層の字（46px）は大きい字＝3.0 以上
                if pg.evaluate("document.documentElement.scrollWidth") > 390: wide.append(tid + ' ' + tab)
            w2 = pg.evaluate("[1,2,3,4,5,6,7,8].map(i => { const e = document.createElement('span'); e.className = 'num w' + i; document.body.appendChild(e); const c = getComputedStyle(e).backgroundColor; e.remove(); return c; })")
            if w2 != ['rgb(255, 255, 255)', 'rgb(26, 26, 26)', 'rgb(211, 35, 45)', 'rgb(30, 91, 190)', 'rgb(243, 207, 30)', 'rgb(29, 138, 59)', 'rgb(240, 126, 25)', 'rgb(243, 141, 182)']: wk.append(tid)
        check(not low, f'全30テーマ：主な文字と背景のコントラスト 4.5以上（層の大きい字は 3.0以上）（{len(low)}こ 低い：{low[:6]}）')
        check(not wide and not wk, f'全30テーマ：横にはみ出さない（{wide[:4]}）・馬番の枠の色はどのテーマでも同じ（{wk[:4]}）')
        pg.evaluate("TengelKisekae.apply('default')"); pg.wait_for_timeout(500)
        check(pg.evaluate("document.documentElement.dataset.ks") is None and pg.locator('#ksBnr').evaluate('e => e.hidden') and pg.evaluate("document.querySelector('#ksTheme').textContent === ''"), 'いつものにもどす → 上の絵なし・テーマの CSS なし')
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
        # ---- CM：App Store版の 設定には 出さない（2026/10/25 まさちゃん「設定に入ってるCMを見る機能消して！」。Web版は 今までどおり） ----
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(300)
        check(pg.locator('#setCM').count() == 0 and pg.locator('#cmModal').count() == 0 and 'CMを見る' not in pg.locator('#v-set').inner_text(), 'App Store版：設定に「テンゲルのCM」の カードは ない')
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
        check(pg.locator('#nativeRestore').count() == 0 and pg.evaluate('TengelLocal.mem.bets.size') == 3 and '記録3件を戻したよ' in pg.locator('#toast').inner_text() and 'ポイント（6,000P）も戻したよ' in pg.locator('#toast').inner_text() and pg.evaluate('TengelWallet.total()') == 6000, '「記録を戻す」→ 記録とポイントの台帳が戻る（着せ替えで 1,000P 使ったあと）')
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
        check(p2.locator('#ptsPill').count() == 0 and p2.locator('#testTag').count() == 0 and p2.locator('#ptsCss').count() == 0 and p2.evaluate("getComputedStyle(document.querySelector('#dbpill')).marginLeft") != '0px', 'Web版：上の帯の 所有ポイント・説明書の 置き場は かわらない')
        check(p2.locator('#setKisekae').count() == 0 and p2.locator('#ksBnr').count() == 0 and p2.evaluate("typeof window.TengelKisekae === 'undefined' && typeof window.__KS === 'undefined' && !document.querySelector('#ksCss') && !document.documentElement.dataset.ks"), 'Web版：着せ替え（カード・上の絵・テーマの CSS）は入らない')
        # 第4.60版：Web版は WIN5 の まま・判定画面の「全STEPを表示」も 実測④の C層×非該当も 見直し基準の 数も 今までどおり
        p2.click('.tabbar button[data-tab=stats]'); p2.wait_for_timeout(900)
        w46 = p2.evaluate("(() => { const c4 = [...document.querySelectorAll('#statsBody .card')].find(c => (c.querySelector('h2') || {}).textContent.includes('④')); return { c0: c4 ? c4.innerText.includes('C層×非該当') : null, prog: [...document.querySelectorAll('.prog .pl b')].map(b => b.textContent), hint: !!document.querySelector('.prog') && document.querySelector('.prog').previousElementSibling.tagName !== 'P' }; })()")
        check(p2.locator('.tabbar button[data-tab=win5]').inner_text().strip() == 'WIN5' and w46['c0'] is True and w46['prog'] and w46['prog'][2] != '0/20' and w46['hint'], f'Web版：WIN5・実測④に C層×非該当の 行・見直し基準は 基盤データで 数える（{w46}）')
        p2.click('.tabbar button[data-tab=judge]'); p2.wait_for_timeout(400)
        p2.click('#sampleBtn'); p2.wait_for_timeout(900)
        check(p2.locator('#result details.full').count() == 1 and p2.locator('#result .rankbox').count() == 0, 'Web版：判定画面に「全STEPを表示」が あって、人気順位の 表は ない')
        check(p2.evaluate("typeof window.TengelNumpad === 'undefined' && typeof window.TengelManual === 'undefined' && !document.querySelector('#numPad')") and p2.locator('#manBtn').get_attribute('href') == 'manual.html', 'Web版：テンキーと 説明書の 重ねた 窓は 入らない（説明書は ページを 移る）')
        check(p2.locator('#setCM').count() == 1 and '▶ CMを見る' in p2.locator('#setCM').inner_text(), 'Web版：設定の「テンゲルのCM」は 今までどおり')
        check('単勝・複勝と3連単人気順のスクショを1〜3枚' in p2.locator('#ocrHint').inner_text(), 'Web版：読み取りの 案内は 単勝・複勝の まま（複勝も 読む）')
        check(p2.locator('#recCard h2').inner_text().startswith('結果・収支の記録') and p2.locator('#omakaseBtn').count() == 0 and p2.locator('#result .rnav').count() == 0 and not [t for t in p2.locator('#result .zref').all_inner_texts() if '選んだ馬で' in t] and p2.locator('#saveJudge').count() == 1, 'Web版：判定画面は今までどおり（結果・収支の記録・お任せなし・矢印なし・%なし・判定と結果を保存）')
        p2.click('.tabbar button[data-tab=rec]'); p2.wait_for_timeout(300); p2.click('#recExportBtn'); p2.wait_for_timeout(300)
        check(not p2.locator('#recSave').is_visible(), 'Web版：「CSVで保存」は出ない（今までどおり）')
        p2.click('.tabbar button[data-tab=set]'); p2.wait_for_timeout(300)
        p2.locator('#abPrivacy summary').click(); p2.wait_for_timeout(100)
        wv = p2.locator('#setAbout').inner_text()
        check('ご利用にあたって' in wv and 'Google Fonts' in wv and p2.locator('#abFonts').count() == 0, 'Web版の「このアプリについて」（Google Fonts の説明・フォントのライセンスはなし）')
        # ---- 第4.59版：iPad で 画面いっぱいに 動かす とき（幅 700px 以上・時計の 帯の 高さが 0 と 伝わる）→ 上の帯を 24px あける ----
        ctx4 = b.new_context(viewport={'width': 820, 'height': 1180}, device_scale_factor=1, locale='ja-JP'); ctx4.add_init_script(FAKE)
        ctx4.expose_binding('__saveBackup', lambda s, t: None); ctx4.expose_binding('__marker', marker)
        p4 = ctx4.new_page(); p4.on('pageerror', lambda e: errs.append('IPAD ' + str(e)))
        p4.goto(APPURL); p4.wait_for_timeout(1200); gate(p4); p4.wait_for_timeout(400)
        ip = p4.evaluate("(() => { const r = document.querySelector('header.top').getBoundingClientRect(); return { top: r.top, ti2: document.documentElement.style.getPropertyValue('--top-inset2'), pill: !!document.querySelector('#ptsPill') }; })()")
        check(ip['ti2'] == '24px' and abs(ip['top'] - 24) < 1 and ip['pill'], f'iPad の 幅（820px）で 上の あきが 0 なら 24px あけて、上の帯が 時計と 重ならない（{ip}）')
        p4.evaluate("document.querySelector('#ptsPill').click()"); p4.wait_for_timeout(500)
        check(p4.locator('#v-set').is_visible() and p4.locator('#setPoints').is_visible(), '所有ポイントを 押すと 設定の ポイントへ')
        ctx4.close()
        # ---- 第4.59版：テスト版（TENGEL_TEST=1）：はじめから 10,000P・テスト版の 印・設定の いちばん上に「テスト版の道具」（10,000P 足す・的中ボタンを ためす）----
        store['markers'].clear()
        ctx5 = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP'); ctx5.add_init_script(FAKE)
        ctx5.expose_binding('__saveBackup', lambda s, t: None); ctx5.expose_binding('__marker', marker)
        p5 = ctx5.new_page(); p5.on('pageerror', lambda e: errs.append('TEST ' + str(e)))
        p5.goto(TESTURL); p5.wait_for_timeout(1500); gate(p5); p5.wait_for_timeout(700)
        tb = p5.evaluate("(() => ({ total: TengelWallet.total(), tag: (document.querySelector('#testTag') || {}).innerText, pill: document.querySelector('#ptsPill').innerText.replace(/\\s+/g, ' '), first: document.querySelector('#v-set > .card').id, btns: [...document.querySelectorAll('#setTest [data-test=fx]')].map(x => x.innerText), ev: TengelWallet.events().map(e => e.id + ':' + e.amount) }))()")
        check(tb['total'] == 10000 and tb['tag'] == 'テスト版' and '購入 10,000P' in tb['pill'] and tb['first'] == 'setTest' and tb['btns'] == ['的中', 'デカ的中', 'ど的中', '隠れど的中', 'ハズレ', 'プレミアムど的中', '超プレミアムど的中', '神様的中', '超神様的中', '超プレミアム神様的中', 'ど的中・紫電'] and tb['ev'] == ['gift-first:1500', 'gift-test:8500'],
              f'テスト版：はじめから ちょうど 10,000P（初回の 1,500P＋テスト版の 8,500P）・上の帯に「テスト版」の 印・設定の いちばん上に「テスト版の道具」（{tb}）')
        p5.click('.tabbar button[data-tab=set]'); p5.wait_for_timeout(300)
        p5.locator('#setTest [data-test=pts]').click(); p5.wait_for_timeout(400)
        check(p5.evaluate('TengelWallet.total()') == 20000 and '購入 20,000P' in p5.locator('#ptsPill').inner_text().replace('\n', ' '), 'テスト版：「10,000P 足す」で 20,000P（上の帯も かわる）')
        p5.locator('#setTest [data-test=fx][data-kind=gd]').click(); p5.wait_for_timeout(500)
        check(p5.locator('#fxOv .ov.fz .pbox.rbw .push .rbf').count() == 1 and p5.evaluate("TengelFx.current().kind") == 'gd', 'テスト版：「神様的中」を 押すと 虹色の PUSH（神様的中）が 出る（くじは ひかない）')
        p5.evaluate('TengelFx.close()'); p5.wait_for_timeout(200)
        p5.locator('#setTest [data-test=fx][data-kind=miss]').click(); p5.wait_for_timeout(600)
        check(p5.locator('#fxOv .rb.miss').count() == 1 and p5.locator('#fxOv .rb .bh').inner_text() == 'ハズレ', 'テスト版：「ハズレ」で ハズレの ボード')
        p5.evaluate('TengelFx.close()')
        check(p5.evaluate("!!document.querySelector('#setTest')") and pg.evaluate("!document.querySelector('#setTest') && !window.__TEST"), 'App Store版（ふつうの 作り方）には テスト版の 道具も 印も ない')
        # ---- 第4.60版：iPad の テスト（2026/10/25）の 7つの 直し ----
        # ① 5重勝 → 単勝5連勝（タブ・画面・説明書）
        p5.click('.tabbar button[data-tab=win5]'); p5.wait_for_timeout(500)
        w5t = p5.evaluate("({ tab: document.querySelector('.tabbar button[data-tab=win5]').innerText.trim(), h2: document.querySelector('#w5Body h2').innerText, has5: document.body.innerText.includes('5重勝') })")
        check(w5t['tab'] == '単勝5連勝' and w5t['h2'] == '単勝5連勝' and not w5t['has5'], f'第4.60版：「5重勝」→「単勝5連勝」（タブ・画面に 5重勝は 残らない）（{w5t}）')
        # ---- 第4.62版：テンキー（数字の 欄で キーボードが 出ない とき）。Chromium には キーボードが ないので、欄に 入って 0.65秒で 出る ----
        p5.focus('#w5Win0'); p5.wait_for_timeout(950)
        np0 = p5.evaluate('TengelNumpad.state()')
        for k in ('7', '1'): p5.click(f'#numPad button[data-k="{k}"]'); p5.wait_for_timeout(80)
        np1 = p5.evaluate("({ v: document.querySelector('#w5Win0').value, active: document.activeElement.id, open: TengelNumpad.state().open, keys: [...document.querySelectorAll('#numPad button')].map(b => b.dataset.k) })")
        check(np0['open'] and np0['target'] == 'w5Win0' and np1['v'] == '71' and np1['active'] == 'w5Win0' and np1['open'] and np1['keys'] == ['7', '8', '9', 'bs', '4', '5', '6', '-', '1', '2', '3', '.', 'next', '0', 'done'], f'第4.62版：数字の 欄に 入って キーボードが 出なければ テンキー（7 8 9 ⌫／4 5 6 -／1 2 3 .／次へ 0 完了）。押すと 欄に 入る（フォーカスは そのまま）（{np0}・{np1}）')
        p5.click('#numPad button[data-k="bs"]'); p5.wait_for_timeout(60); p5.click('#numPad button[data-k="next"]'); p5.wait_for_timeout(200)
        np2 = p5.evaluate("({ v0: document.querySelector('#w5Win0').value, active: document.activeElement.id, target: TengelNumpad.state().target })")
        p5.click('#numPad button[data-k="done"]'); p5.wait_for_timeout(150)
        np3 = p5.evaluate("({ open: TengelNumpad.state().open, active: document.activeElement.tagName })")
        check(np2['v0'] == '7' and np2['active'] == 'w5Win1' and np2['target'] == 'w5Win1' and not np3['open'] and np3['active'] == 'BODY', f'第4.62版：テンキーの ⌫・「次へ」（次の 数字の 欄へ）・「完了」（しまって 欄から 出る）（{np2}・{np3}）')
        p5.focus('#w5Stake'); p5.wait_for_timeout(950)
        for k in ('3', '0', '0', '0'): p5.click(f'#numPad button[data-k="{k}"]'); p5.wait_for_timeout(50)
        check(p5.evaluate("document.querySelector('#w5Stake').value") == '3000' and p5.evaluate("document.querySelector('#w5Stake').type") == 'number', '第4.62版：金額の 欄（type=number）にも テンキーで 入る')
        p5.click('#numPad button[data-k="done"]'); p5.wait_for_timeout(150)
        p5.focus('#w5Win1'); p5.wait_for_timeout(950); np4 = p5.evaluate('TengelNumpad.state().open')
        p5.keyboard.press('5'); p5.wait_for_timeout(150); np5 = p5.evaluate('TengelNumpad.state()')
        p5.evaluate('document.activeElement.blur()'); p5.focus('#w5Win2'); p5.wait_for_timeout(950); np6 = p5.evaluate('TengelNumpad.state().open')
        check(np4 and not np5['open'] and np5['hw'] and p5.evaluate("document.querySelector('#w5Win1').value") == '5' and not np6, f'第4.62版：キーボードで 打てたら テンキーは しまって、その あとは 出さない（{np5}）')
        p5.evaluate('TengelNumpad._reset(); document.activeElement && document.activeElement.blur()'); p5.wait_for_timeout(150)
        # アプリ（iOS）が「キーボードが 出た」と 知らせたら 出さない／出ていても しまう。「しまった」の あとは また 出る
        p5.focus('#w5Win2'); p5.evaluate("window.__nativeEvent('keyboard', { open: true, height: 320 })"); p5.wait_for_timeout(950); np7 = p5.evaluate('TengelNumpad.state()')
        p5.evaluate("window.__nativeEvent('keyboard', { open: false, height: 0 }); document.activeElement.blur()"); p5.wait_for_timeout(150)
        p5.focus('#w5Win0'); p5.wait_for_timeout(950); np8 = p5.evaluate('TengelNumpad.state().open')
        p5.evaluate("window.__nativeEvent('keyboard', { open: true, height: 320 })"); p5.wait_for_timeout(100); np9 = p5.evaluate('TengelNumpad.state()')
        check(not np7['open'] and np7['kb'] is True and np8 and not np9['open'] and np9['kb'] is True, f'第4.62版：アプリ（iOS）が「キーボードが 出た」と 知らせたら テンキーは 出さない・出ていたら しまう。「しまった」の あとは また 出る（{np7}・{np8}・{np9}）')
        p5.evaluate('TengelNumpad._reset(); document.activeElement && document.activeElement.blur()')
        # ---- 第4.62版：説明書は アプリの 中の 重ねた 窓で 開く（ページを 移らない → 戻っても アプリを 開いた 時の 画面は 出ない）----
        p5.click('#manBtn'); p5.wait_for_timeout(1800)
        mo = p5.evaluate("({ ov: !!document.querySelector('#manOv'), src: (document.querySelector('#manOv iframe') || {}).src || '', url: location.href, tab: document.querySelector('.tabbar button[aria-selected=true]').dataset.tab, over: document.documentElement.classList.contains('manon') })")
        fr = p5.frame_locator('#manOv iframe')
        check(mo['ov'] and mo['src'].endswith('/manual.html') and mo['url'] == TESTURL and mo['tab'] == 'win5' and mo['over'] and fr.locator('#toApp').is_visible() and fr.locator('#home').count() == 1, f'第4.62版：説明書は 重ねた 窓（iframe）で 開く。アプリの ページは そのまま（{mo}）')
        fr.locator('.mrow').first.click(); p5.wait_for_timeout(600)
        check(fr.locator('#page').is_visible() and fr.locator('#closeApp').is_visible(), '説明書の 項目を 開ける（窓の 中で）')
        fr.locator('#closeApp').click(); p5.wait_for_timeout(500)
        mc = p5.evaluate("({ ov: !!document.querySelector('#manOv'), url: location.href, tab: document.querySelector('.tabbar button[aria-selected=true]').dataset.tab, gate: !!document.querySelector('#gateGo'), over: document.documentElement.classList.contains('manon') })")
        check(not mc['ov'] and mc['url'] == TESTURL and mc['tab'] == 'win5' and not mc['gate'] and not mc['over'], f'第4.62版：「アプリに戻る」で 窓が 閉じて、そのまま アプリ（開いた 時の 画面は 出ない）（{mc}）')
        # ② 実測④（と ③）に C層×非該当の 行を 出さない ／ ③ 見直し基準の 進み具合は 0 から（使う人が 入れた レースだけ）
        p5.click('.tabbar button[data-tab=stats]'); p5.wait_for_timeout(1000)
        st46 = p5.evaluate("(() => { const cards = [...document.querySelectorAll('#statsBody .card')]; const f = m => cards.find(c => (c.querySelector('h2') || {}).textContent.includes(m)); const c4 = f('④'), c3 = f('③'), pr = f('見直し基準'); return { c4: c4 ? c4.innerText.includes('C層×非該当') : null, c4rows: c4 ? c4.querySelectorAll('tbody tr').length : 0, c3: c3 ? c3.innerText.includes('C層・非該当') : null, prog: [...pr.querySelectorAll('.prog .pl b')].map(b => b.textContent), hint: pr.querySelector('.hint').innerText }; })()")
        check(st46['c4'] is False and st46['c4rows'] == 4 and st46['c3'] is False, f'第4.60版：実測④（と ③）に C層×非該当の 行は 出さない（A層・B層・C層第1段階・C層第2段階の 4行）（{st46}）')
        check(st46['prog'] == ['0/30', '0/10', '0/20', '0/30', '0/10', '0/10'] and 'アプリに入っているデータは数えない' in st46['hint'], f'第4.60版：見直し基準の 進み具合は 0 から（アプリに 入っている データは 数えない・使う人が 入れた レースで 進む）（{st46}）')
        # ④「くわしく」→「詳しく」 ／ ⑦ 解放エフェクト（券種・マザーデータ・壁紙・ミッション）
        p5.click('.tabbar button[data-tab=set]'); p5.wait_for_timeout(500)
        check(p5.locator('#setPoints button[data-v=hist]').inner_text().strip() == '詳しく' and p5.evaluate("typeof TengelFx.unlock === 'function'"), '第4.60版：ポイントの「くわしく」→「詳しく」・TengelFx.unlock が ある')
        p5.locator('#setCustom .ptitem[data-key="type:複勝"] [data-pt=unlock1]').click(); p5.wait_for_timeout(200)
        p5.locator('#setCustom .ptitem[data-key="type:複勝"] [data-pt=unlock2]').click(); p5.wait_for_timeout(450)
        uf = p5.evaluate("({ unlk: !!document.querySelector('#setCustom .ptitem[data-key=\"type:複勝\"].unlk'), on: !!document.querySelector('#setCustom .ptitem[data-key=\"type:複勝\"].on'), burst: document.querySelectorAll('.unlkb i').length, text: (document.querySelector('.unlkt') || {}).innerText, css: !!document.querySelector('#fxUnlkCss') })")
        check(uf['unlk'] and uf['on'] and uf['burst'] >= 10 and uf['text'] == '解放！' and uf['css'], f'第4.60版：券種を 解放すると、その 項目の 上に 解放エフェクト（金の 輪と つや・粒・「解放！」）（{uf}）')
        p5.wait_for_timeout(2000)
        check(p5.evaluate("!document.querySelector('.unlk') && !document.querySelector('.unlkb') && !document.querySelector('.unlkt')"), '第4.60版：解放エフェクトは 2秒で 消える')
        ksid = p5.evaluate("(() => { const t = document.querySelector('#setKisekae .kst.lock'); return t ? t.dataset.ks : null; })()")
        p5.locator(f'#setKisekae .kst[data-ks="{ksid}"]').click(); p5.wait_for_timeout(300)
        p5.locator('#setKisekae [data-ksact=unlock]').click(); p5.wait_for_timeout(1100)
        kf = p5.evaluate(f"({{ unlk: !!document.querySelector('#setKisekae .kst[data-ks=\"{ksid}\"].unlk'), on: !!document.querySelector('#setKisekae .kst[data-ks=\"{ksid}\"].on'), text: (document.querySelector('.unlkt') || {{}}).innerText, cur: TengelKisekae.current() }})")
        check(kf['unlk'] and kf['on'] and kf['text'] == '解放！' and kf['cur'] == ksid, f'第4.60版：壁紙を 解放すると、その タイルの 上に 解放エフェクト（着せ替えも される）（{kf}）')
        p5.wait_for_timeout(2000)
        # ミッション：壁紙を 8枚（10,000P を 足して、安い 壁紙から 解放して から「受け取る」を 押す）→ 受け取った 行に エフェクト
        for _ in range(4): p5.locator('#setTest [data-test=pts]').click(); p5.wait_for_timeout(250)
        p5.evaluate("(async () => { const ts = TengelKisekae.list().filter(t => t.price && !TengelWallet.unlocked('theme:' + t.id)).sort((a, b) => a.price - b.price); let n = TengelKisekae.count(); for (const t of ts) { if (n >= 8) break; if (await TengelWallet.unlock('theme:' + t.id, t.price)) n++; } return n; })()")
        p5.wait_for_timeout(600)
        p5.locator('#setMission [data-pt=claim][data-id=mission-wall-8]').click(); p5.wait_for_timeout(700)
        mf = p5.evaluate("({ unlk: !!document.querySelector('#setMission .msrow[data-mid=mission-wall-8].unlk'), text: (document.querySelector('.unlkt') || {}).innerText, done: document.querySelector('#setMission .msrow[data-mid=mission-wall-8] .md').innerText })")
        check(mf['unlk'] and mf['text'] == '受け取り！' and mf['done'] == '受け取りずみ', f'第4.60版：ミッションの「受け取る」でも、その 行の 上に 解放エフェクト（「受け取り！」）（{mf}）')
        ctx5.close()
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
