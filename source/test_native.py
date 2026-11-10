# アプリ版（iPhone・iPadのアプリの中の画面）のテスト。アプリ（Swift）のかわりに、にせもののアプリをつなぐ
#  ・設定タブ：「アプリの更新」（App Storeの版を確かめる・Web版の更新の確認はしない）・「データの更新」・自動バックアップの欄
#  ・記録を保存すると、アプリの中に自動バックアップ（APIキーは入れない）
#  ・バックアップを保存／CSVで保存 → 共有シート（アプリ）に渡す・コピーはアプリへ
#  ・保存場所が消えた（記録0件）のに自動バックアップに記録がある → 「戻す？」→ 戻す／戻さない
#  ・CMの動画は公開中のWeb版から読む
#  ・Web版（ブラウザ）は今までどおり（アプリの印は出ない）
#  ・App Store版の中身（TARGET=app）：Google に通信しない（フォントはアプリの中）・「このアプリについて」（免責・20歳・相談先・非公式と商標・プライバシー・フォントのライセンス）
#    ・お客さん向けの言い方（まさちゃん・姫に送って・iPhone を出さない）・説明書はApp Store版（「iPhoneに入れる」なし）
import json, os, re, shutil, subprocess, time
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
for f in ('sgd_film', 'spg_up', 'sd_film', 'nd_film', 'gk_film'):   # 第4.70版〜：紫電の 動画も・第4.77版：ノーマルど的中の 動画も・第4.117版：神様極的中の 動画も
    mp4, webm = os.path.join(W, 'ios', 'fx_assets', f + '.mp4'), os.path.join(FILMS_DIR, f + '.webm')
    if not os.path.exists(webm) and os.path.exists(mp4) and shutil.which('ffmpeg'):
        os.makedirs(FILMS_DIR, exist_ok=True)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', mp4, '-vf', 'scale=390:844', '-c:v', 'libvpx-vp9', '-deadline', 'realtime', '-cpu-used', '8', '-crf', '40', '-b:v', '0', '-an', '-row-mt', '1', webm], check=False)
    if os.path.exists(webm):
        shutil.copy(webm, os.path.join(SRV, 'APP', f + '.webm'))
# 第4.121版：結果ボードカスタムの 絵の ボード（ios/bcp_assets/：まさちゃんの 絵・リポジトリには 入れない）。手元に ある とき だけ 置く。
#   ハズレ⑤「書き換え参戦」（pen）の 絵は わざと 置かない（読めない とき いつもの ボードに もどる 形・CI と 同じ）
import sys; sys.path.insert(0, os.path.join(W, 'kisekae', 'bcp')); import bcp_app as _bcp
BCP_DIR = os.path.join(W, 'ios', 'bcp_assets')
BCP_ON = all(os.path.exists(os.path.join(BCP_DIR, f)) for f in _bcp.files())
BCP_OFF = [f for iid, _k, st in _bcp.ITEMS if iid == 'pen' for _n, n in st for f in [f'bcp_{n}.webp', f'bcp_{n}_fg.webp'] + _bcp.motion_files(n)] + [_bcp.THUMB.format('pen')]   # 第4.129版：動く 絵も
if BCP_ON:
    for f in _bcp.files():
        if f not in BCP_OFF:
            shutil.copy(os.path.join(BCP_DIR, f), os.path.join(SRV, 'APP', f))
else:
    print('※ 結果ボードカスタムの 絵（ios/bcp_assets）が ない ので、絵の ボードの テストは 読めない 形だけ')
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
  { id: 'jp.tengel.app.sub2000', title: '月2,000Pプラン', price: '¥638', kind: 'sub' }, { id: 'jp.tengel.app.sub4400', title: '月4,400Pプラン', price: '¥1,276', kind: 'sub' }, { id: 'jp.tengel.app.sub9200', title: '月9,200Pプラン', price: '¥1,914', kind: 'sub' },
  { id: 'jp.tengel.app.boardcustom', title: '結果ボードカスタム', price: '¥1,500', kind: 'unlock' }, { id: 'jp.tengel.app.wallpack1', title: '壁紙パック', price: '¥1,500', kind: 'unlock' },
  { id: 'jp.tengel.app.bundle1', title: 'お得パック', price: '¥2,200', kind: 'unlock' }],   // 第4.114版：結果ボードカスタム 2,200 → 1,500円・お得パック（2つの セット）2,200円
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
    else if (P.op === 'current') val = { ok: true, list: I.current };
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
            if not g.evaluate("e => e.classList.contains('fade')"):   # 消えて いく 間（fade）は もう 押さない（消えると ボタンが なくなって 待ちつづける）
                try:
                    pg.locator('#gateGo').click(timeout=3000)
                except Exception:
                    pass
        else:
            try:
                g.click(timeout=500)
            except Exception:
                pass
        pg.wait_for_timeout(150)

try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        # 第4.112版（2026/11/01）：テストの レースは 10月の 日付（2026-10-20・10-21 など）。記録タブは「いまの 月」を 開く ので、
        #   11月に なると 10月の レースが 見えず テストが 止まる → ページの Date だけ 2026/10/01 12:00（日本）から すすめる
        #   （第4.116版：10/30 → 10/01。画像の 読み取りの テストの レース（10月14日 18:05）が「締切済み」に ならない ように、10月の レースが みな 先に なる 日に した）
        #   （時間は ふつうに 流れる。performance・タイマー・アニメーションは そのまま＝Playwright の clock は performance の 記録を 消して しまう ので 使わない）
        _nc = b.new_context
        def _ctx_at_oct01(*a, **k):
            c = _nc(*a, **k)
            c.add_init_script("""(() => { const D = Date, OFF = Date.UTC(2026, 9, 1, 3, 0, 0) - D.now();
              class FD extends D { constructor(...a) { if (a.length) super(...a); else super(D.now() + OFF); } static now() { return D.now() + OFF; } }
              FD.UTC = D.UTC; FD.parse = D.parse; window.Date = FD; })();""")
            return c
        b.new_context = _ctx_at_oct01
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
        check(pg.evaluate('TengelWallet.total()') == 1500 and '1,500P' in pt and pg.evaluate("[...document.querySelectorAll('#setPoints .ptbk b')].map(x => x.innerText)") == ['0P', '0P', '1,500P'] and store['markers'].get('gift-first'), f'はじめてのプレゼント 1,500P（獲得ポイント）・キーチェーンにしるし（{list(store["markers"])}）')
        # 第4.59版：上の帯の 所有ポイントと 説明書の 置き場・テスト版の 印は ない
        #   第4.139版（まさちゃん 11/10 11:46「上のところに表示されてる時は、合計のポイントだけ表示するようにして！」）：札は 合計だけ「ポイント 1,500P」（前は「購入 ○P・サブスク ○P」）。内わけは 札の title と、押すと 出る「ポイントの詳細」
        hb = pg.evaluate("(() => { const p = document.querySelector('#ptsPill'), m = document.querySelector('#manBtn'), d = document.querySelector('#dbpill'), b = document.querySelector('header.top .brand'); if (!p || !m || !d) return null; const r = x => x.getBoundingClientRect(); return { txt: p.innerText.replace(/\\s+/g, ' '), afterBrand: b.nextElementSibling === p, order: m.compareDocumentPosition(d) & Node.DOCUMENT_POSITION_FOLLOWING ? 1 : 0, mRight: r(m).right, dLeft: r(d).left, dRight: r(d).right, mTop: r(m).top, dTop: r(d).top, w: innerWidth, tag: !!document.querySelector('#testTag'), gopt: p.dataset.gopt, title: p.title, al: p.getAttribute('aria-label'), segs: p.querySelectorAll('.pp').length }; })()")
        check(hb and hb['txt'] == 'ポイント 1,500P' and hb['segs'] == 1 and '購入' not in hb['txt'] and 'サブスク' not in hb['txt'] and hb['afterBrand'] and hb['gopt'] == 'points' and not hb['tag']
              and all(w in hb['title'] for w in ('合計 1,500P', '購入ポイント 0', 'サブスクポイント 0', '獲得ポイント 1,500', '上限 99,999P')) and 'ポイントの詳細' in hb['al'],
              f'上の帯：ロゴの 右に 所有ポイント「ポイント 1,500P」（合計だけ・1つの 札。内わけは title と 押した 先）・テスト版の 印は ない（{hb}）')
        # 第4.83版（まさちゃん「説明書をポイントの横に配置できない？ その下にミッション、その下にマザーデータ」）：説明書は 所有ポイントの すぐ 右（1段目）・ミッションは 2段目・マザーデータの 札は 3段目（右よせ）
        pg.wait_for_timeout(300)
        hb2 = pg.evaluate("(() => { const r = s => document.querySelector(s).getBoundingClientRect(); const p = r('#ptsPill'), m = r('#manBtn'), d = r('#dbpill'), ms = r('#msBtn'), rv = r('#rsvBtn'), br = r('header.top .brand'); return { pm: Math.abs(p.top - m.top) < 8 && m.left > p.right && m.left - p.right < 20, msBelow: ms.top > m.bottom, dBelow: d.top > ms.bottom, right: d.right >= innerWidth - 24 && ms.right >= innerWidth - 24, ptsH: Math.round(p.height), order: [...document.querySelector('header.top .top-in').children].map(e => e.id || e.className).join(','),"
                           " manR: +(innerWidth - m.right).toFixed(1), msR: +(innerWidth - ms.right).toFixed(1), pL: +p.left.toFixed(1), brR: +br.right.toFixed(1), rvL: +rv.left.toFixed(1), rvRow: Math.abs(rv.top - ms.top) < 8 && rv.right < ms.left && ms.left - rv.right < 12, pv: +document.querySelector('#ptsPill .pv').getBoundingClientRect().width.toFixed(1), pw: +p.width.toFixed(1) }; })()")
        check(hb and hb['order'] == 1 and hb2['pm'] and hb2['msBelow'] and hb2['dBelow'] and hb2['right'] and hb2['ptsH'] <= 36 and hb2['order'].startswith('brand,ptsPill,manBtn,tbrk2,rsvBtn,msBtn,tbrk,dbpill'), f'上の帯：説明書は 所有ポイントの すぐ 右 ／ 2段目に（第4.122版の「結果待ち」と）ミッション ／ 3段目に マザーデータの 札（右よせ）（{hb2}）')
        # 第4.139版（まさちゃん 11/10 11:32「ポイントと説明書→の方で、画面端に合わせて！」11:37「あと結果待ちと、ポイントの項目の端できるだけ合わせて！」11:38「この一枚目の赤線くらいに合わせて！」）：
        #   説明書は 画面の 右はし（ミッション・マザーデータの 札と 同じ）・ポイントの 札は ロゴの すぐ 右から 説明書まで のびる・結果待ちの 左はしは ポイントの 札の 左はしと 同じ 線
        check(abs(hb2['manR'] - 16) <= 1 and abs(hb2['msR'] - 16) <= 1 and 4 <= hb2['pL'] - hb2['brR'] <= 12 and abs(hb2['rvL'] - hb2['pL']) <= 1 and hb2['rvRow'] and hb2['pw'] >= 130,
              f'第4.139版：説明書・ミッションは 画面の 右はし（右から {hb2["manR"]}・{hb2["msR"]}px）・ポイントの 札は ロゴの すぐ 右（{hb2["brR"]} → {hb2["pL"]}）から のびる（はば {hb2["pw"]}px）・結果待ちの 左はし {hb2["rvL"]} は 札の 左はしと 同じ 線')
        check('アプリを消すと、ポイント・解放したもの・記録はすべて消えて、もどせません' in pt and '200P' in pt and '買ったポイントから先に使う' in pt and 'サブスクポイント → 購入ポイント → 獲得ポイント' in pt
              and all(w in pt for w in ('購入ポイント', 'サブスクポイント', '獲得ポイント', 'ポイントは 合計 99,999P まで もてるよ', 'あと 98,499P 入るよ')), 'ポイントのカード：消えることの注意・1レース200P・使う順・内わけ 3つ（購入ポイント・サブスクポイント・獲得ポイント）・上限 99,999P（あと 98,499P）')
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
        check(card.locator('h2').inner_text() == '買い目' and pg.locator('#saveJudge').count() == 0 and card.locator('[data-rsv=reserve]').count() == 1 and card.locator('[data-rsv=give]').count() == 1 and '発走 15:40 → 15:55 にお知らせ' in ct and card.locator('[data-k=rtypes] button').count() == 9 and card.locator('[data-k=rzones] button:not(.self)').count() == 2 and card.locator('[data-k=rzones] [data-k=rself]').count() == 1,
              '判定画面の下は「買い目」のカード：券種9つ・ゾーン2つ（＋第4.122版の「✏️ 自己入力」）・「買い目を予約」「このレースを諦める」・お知らせの時刻（「判定と結果を保存」はない）')
        check(pg.locator('#result [data-k=zwaku]').count() == 0, '枠複・枠単が 🔒 の 間は、判定の ゾーンに 枠を 出さない（第4.122版：解放した 人だけ）')
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
        check(chips.count() == 4 and pg.locator('#slotJudge .slotchip.lock').count() == 2 and [c.inner_text().replace('\n', ' ') for c in chips.all()] == ['テンゲルデータ', 'マザーデータ① 空', 'マザーデータ② 🔒', 'マザーデータ③ 🔒'],
              f'判定画面の データの 切り替え（第4.123版）：テンゲルデータ（数は 出さない）・マザーデータ①（はじめから・空）・②③は🔒（{[c.inner_text().replace(chr(10), " ") for c in chips.all()]}）')
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
        # 第4.109版：保存の たびに 音 15こ・動画 4本・絵 ぜんぶを 読むのを やめた → PUSH の 音 3こ ＋ 出す 演出（的中）の 音だけ・動画は 作らない
        res9 = pg.evaluate("performance.getEntriesByType('resource').map(e => e.name.split('/').pop())")
        check(sorted(sx['keys']) == ['big_push', 'fz_push', 'hit', 'hit_push'] and pg.locator('#fxVh video').count() == 0
              and not any(n.endswith('.mp4') or n.startswith(('sfx_sgd', 'sfx_spg', 'sfx_zp', 'sfx_pc', 'sfx_sd', 'sfx_nd', 'sfx_gk', 'sfx_fz.', 'fz_n', 'pm_', 'sgd_last', 'sd_last', 'nd_last', 'gk_last')) for n in res9),
              f'保存の たびに 読むのは PUSH の 音 3こと 出す 演出（的中）の 音だけ・ほかの 演出の 音・動画・絵は 読まない（第4.109版）（{sorted(sx["keys"])}・動画 {pg.locator("#fxVh video").count()}）')
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
        check(pg.evaluate("TengelWallet.board.info().streak") == 1, f'第4.91版 結果ボードカスタムの 連続的中の 数（第4.113版：出世馬は 消した・数は 残す）：結果が はじめて 決まった 的中で 1・金額の 記録・保存し直しでは 数えない（{pg.evaluate("TengelWallet.board.info().streak")}）')
        pg.wait_for_timeout(500)
        # ---- 思い出記録（第4.115版・まさちゃん「思い出記録機能を追加する。記録内容 レース名 日付 買い目 結果 金額:購入、回収」「思い出レース表示用の思い出ボードを作成する」）----
        #      記録を 直す 画面の ボタン → 記録に mem → 思い出のレースの 欄・行の 印 → 思い出ボード（種類の ボード ＋ 記録の カード）→ とじる → 絞り込み → ど的中の わく ①② → 外す → バックアップ
        f9 = pg.locator('#recList .rsvf')
        mc = pg.locator('#rFilters [data-f=mem]')
        d9 = b9c['date']; ymd9 = f'{int(d9[:4])}年{int(d9[5:7])}月{int(d9[8:10])}日'; md9 = f'{int(d9[5:7])}/{int(d9[8:10])}'   # テストの 9R の 日付（記録の まま）
        check(f9.get_attribute('data-mode') == 'edit' and f9.locator('[data-act=memtog]').inner_text() == '思い出のレースに記録する' and f9.locator('[data-act=memopen]').count() == 0 and pg.locator('#recList .memtop').count() == 0
              and mc.count() == 1 and mc.inner_text() == '思い出' and not pg.evaluate("document.querySelector('#rFilters [data-f=mem]').hidden"),
              '第4.115版 思い出記録：記録を 直す 画面（mode=edit）に「思い出のレースに記録する」・まだ 思い出の 欄は ない・絞り込みに「思い出」')
        f9.locator('[data-act=memtog]').click(); pg.wait_for_timeout(800)
        b9m = pg.evaluate("[...TengelLocal.mem.bets.values()].find(b => b.r === 9)")
        mt = pg.locator('#recList .memtop')
        check(isinstance(b9m.get('mem'), dict) and bool(b9m['mem'].get('at')) and 'v' not in b9m['mem'] and pg.locator('#recList .memchoose').count() == 0 and '思い出のレースに記録したよ' in pg.locator('#toast').inner_text(),
              f'押すと 記録に mem（記録した 時だけ・的中は ど的中の わくを 聞かない）・お知らせの 帯（{b9m.get("mem")}）')
        check(mt.count() == 1 and '思い出のレース' in mt.locator('h3').inner_text() and '1件' in mt.locator('h3').inner_text() and mt.locator('.lrow.memrow').count() == 1 and mt.locator('.memrow').get_attribute('data-mid') == b9c['id']
              and mt.locator('.memrow .k').inner_text().startswith(md9) and '的中' in mt.locator('.memrow .s').inner_text() and '1着 6（1番人気）' in mt.locator('.memrow .s').inner_text() and '1,800→1,360' in mt.locator('.memrow .lmoney').inner_text()
              and pg.locator(f'#recList .lrow:not(.memrow)[data-id="{b9c["id"]}"] .chip.memchip').inner_text() == '思い出',
              f'記録タブの 上に「思い出のレース」の 欄（{md9} 9R・的中・1〜3着・購入→回収）・月の 一覧の 行に「思い出」の 印（{mt.locator(".memrow .s").inner_text()[:40]}）')
        f9 = pg.locator('#recList .rsvf')
        check(f9.count() == 1 and f9.get_attribute('data-mode') == 'edit' and f9.locator('[data-act=memopen]').inner_text() == '思い出ボードを見る' and f9.locator('[data-act=memtog]').inner_text() == '思い出から外す',
              '記録した あとの 画面：「思い出ボードを見る」「思い出から外す」（行は 開いた まま）')
        pg.evaluate("window.__fxEv = []")
        mt.locator('.memrow .lmain').click(); pg.wait_for_timeout(1600)
        ov = pg.locator('#fxOv')
        mo = ov.locator('.fxs.mem .ov.hit.mem.f-hit')
        mx = ov.locator('.rb .card.memx')
        mxt = mx.inner_text() if mx.count() else ''
        check(ov.count() == 1 and 'k-hit' in ov.get_attribute('class') and 'mem' in ov.get_attribute('class') and mo.count() == 1 and ov.locator('.push').count() == 0 and ov.locator('.rays').count() == 1
              and ov.locator('.memhd .mlab').inner_text() == '思い出のレース' and ymd9 in ov.locator('.memhd .mname').inner_text() and '9R' in ov.locator('.memhd .mname').inner_text()
              and ov.locator('.rb.hit .bh').inner_text() == '的中！' and ov.locator('.rb .brows li').count() == 2 and ov.locator('.close').inner_text() == 'とじる'
              and pg.evaluate('TengelFx.current()') == {'kind': 'hit', 'phase': 'mem', 'quiet': True, 'theme': None, 'film': 0, 'sp': 0, 'pre': 0, 'pz': 1} and pg.evaluate('TengelFx.memInfo()') == {'v': 'a', 'frame': 'hit'}
              and pg.evaluate('window.__fxEv') == ['memory:hit'] and pg.evaluate('document.documentElement.classList.contains("fxon")') and pg.evaluate('window.__zoom').pop().get('lock') is True,
              f'思い出の 行を 押す → 思い出ボード：PUSH なし・的中の 形（光の筋・いつもの ボード「的中！」券種 2行）・上に「思い出のレース」と レース名・合図 memory・拡大は 止める（{pg.evaluate("TengelFx.current()")}）')
        check(mx.count() == 1 and all(w in mxt for w in ('日付', ymd9, 'レース', '9R', '買い目', '18点', '単勝', '3点', '馬単', '15点', '結果', '1着 6（1番人気）', '2着 2（2番人気）', '3着 10（3番人気）', '的中', '金額', '購入 1,800円', '回収 1,360円', '−440円'))
              and mx.locator('.bc').count() == 18 and mx.locator('.bc.mh').count() == 2 and mx.locator('.bc.mh').nth(0).locator('.n').all_inner_texts() == ['6'] and mx.locator('.bc.mh').nth(1).locator('.n').all_inner_texts() == ['6', '2'] and mx.locator('b.minus').inner_text() == '−440円',
              f'ボードの 中の 記録の カード：日付・レース・買い目（単勝 3点・馬単 15点＝18点。当たった 単勝 6・馬単 6→2 に わく）・結果（1〜3着と 人気）・金額（購入 1,800円 → 回収 1,360円・−440円）（{mxt[:70]!r}）')
        ov.locator('.close').click(force=True); pg.wait_for_timeout(400)
        f9 = pg.locator('#recList .rsvf')
        check(pg.locator('#fxOv').count() == 0 and pg.evaluate('TengelFx.current()') is None and pg.evaluate('TengelFx.memInfo()') is None and not pg.evaluate('document.documentElement.classList.contains("fxon")') and pg.evaluate('window.__fxEv') == ['memory:hit', 'close:hit']
              and pg.evaluate('window.__zoom').pop().get('lock') is False and f9.count() == 1 and f9.get_attribute('data-mode') == 'edit',
              '「とじる」→ 記録タブに もどる（行は 開いた まま・拡大できる・合図 close）')
        pg.click('#rFilters [data-f=mem]'); pg.wait_for_timeout(400)
        fl = pg.locator('#recList .dgroup .lrow')
        check(fl.count() == 1 and fl.get_attribute('data-id') == b9c['id'] and pg.locator('#recList .memtop').count() == 1 and pg.locator('#rFilters [data-f=mem]').get_attribute('aria-pressed') == 'true',
              f'絞り込み「思い出」→ 月の 一覧は 思い出の レースだけ（{fl.count()}行）')
        pg.click('#rFilters [data-f=all]'); pg.wait_for_timeout(400)
        fr = pg.evaluate("['hit', 'big', 'nd', 'pc', 'fz', 'sd', 'sgd', 'gd', 'spg', 'gk', 'miss', 'zzz'].map(k => TengelFx.memFrame(k, 'a') + '/' + TengelFx.memFrame(k, 'b'))")
        check(fr == ['hit/hit', 'big/big', 'turf/cute', 'turf/cute', 'turf/cute', 'phantom/phantom', 'torii/torii', 'torii/torii', 'toriicute/toriicute', 'god/god', 'miss/miss', 'hit/hit'] and pg.evaluate("['fz', 'gd', 'nd', 'gk', 'zzz'].map(k => TengelFx.memKind(k))") == ['nd', 'sgd', 'nd', 'gk', 'hit'],
              f'思い出ボードの わく：的中・デカ的中は そのまま／ど的中（ノーマル・プレミアム）は ①光の輪の芝コース（turf）か ②プレミアムかわいい馬（cute）／極ど的中は 幻の馬／超神様は 鳥居／超プレミアム神様は 鳥居＋かわいい馬／神様極的中は 神様馬（第4.117版）／ハズレ（{fr}）')
        # ど的中の レース（rsv.fx を nd に して ためす）：記録する ときに ①② を 選ぶ・やめる・② → 思い出ボードは かわいい馬の わく → 外す → ① → 光の輪の 芝コース
        pg.evaluate("(async () => { const b = [...TengelLocal.mem.bets.values()].find(b => b.r === 9); const d = JSON.parse(JSON.stringify(b)); d.rsv.fx = 'nd'; delete d.mem; await TengelLocal.putBets([d]); })()"); pg.wait_for_timeout(400)
        pg.click('#rFilters [data-f=all]'); pg.wait_for_timeout(400)
        f9 = pg.locator('#recList .rsvf')
        check(pg.locator('#recList .memtop').count() == 0 and f9.count() == 1 and f9.locator('[data-act=memtog]').inner_text() == '思い出のレースに記録する', '思い出を 消した 記録（ど的中に した）：欄は 消える・ボタンは「思い出のレースに記録する」に もどる')
        f9.locator('[data-act=memtog]').click(); pg.wait_for_timeout(500)
        ch = pg.locator('#recList .rsvf .memchoose')
        check(ch.count() == 1 and ch.locator('[data-act=memsave][data-v=a]').inner_text() == '① 光の輪の芝コース' and ch.locator('[data-act=memsave][data-v=b]').inner_text() == '② プレミアムかわいい馬' and ch.locator('[data-act=memcancel]').inner_text() == 'やめる' and 'あとから変えられないよ' in ch.inner_text()
              and 'mem' not in pg.evaluate("[...TengelLocal.mem.bets.values()].find(b => b.r === 9)") and pg.locator('#recList .memtop').count() == 0,
              'ど的中の レース → 押すと まず わくを 選ぶ 窓（① 光の輪の芝コース／② プレミアムかわいい馬／やめる）。まだ 記録しない')
        ch.locator('[data-act=memcancel]').click(); pg.wait_for_timeout(400)
        check(pg.locator('#recList .rsvf .memchoose').count() == 0 and 'mem' not in pg.evaluate("[...TengelLocal.mem.bets.values()].find(b => b.r === 9)"), '「やめる」→ 窓が 閉じる・記録しない')
        pg.locator('#recList .rsvf [data-act=memtog]').click(); pg.wait_for_timeout(400)
        pg.locator('#recList .rsvf .memchoose [data-act=memsave][data-v=b]').click(); pg.wait_for_timeout(800)
        b9n = pg.evaluate("[...TengelLocal.mem.bets.values()].find(b => b.r === 9)")
        mt = pg.locator('#recList .memtop')
        check(b9n.get('mem', {}).get('v') == 'b' and pg.locator('#recList .rsvf .memchoose').count() == 0 and mt.count() == 1 and 'ど的中' in mt.locator('.memrow .s').inner_text(),
              f'② を 選ぶ → 記録に mem.v＝b・思い出の 欄に ど的中の レース（{b9n.get("mem")}）')
        pg.locator('#recList .rsvf [data-act=memopen]').click(); pg.wait_for_timeout(1200)
        ov = pg.locator('#fxOv')
        check(ov.count() == 1 and 'k-nd' in ov.get_attribute('class') and ov.locator('.fxs.mem .ov.miss.quiet.mem.f-cute').count() == 1 and ov.locator('.mring').count() == 0 and ov.locator('.rb.fz .bh').text_content() == 'ど的中！！！' and ov.locator('.rb .zrib').count() == 0
              and pg.evaluate('TengelFx.memInfo()') == {'v': 'b', 'frame': 'cute'} and pg.evaluate('TengelFx.current()')['kind'] == 'nd' and pg.locator('#fxVh video').count() == 0,
              '「思い出ボードを見る」→ ど的中の ボード「ど的中！！！」に ② プレミアムかわいい馬の わく（動画・PUSH なし・帯は 超大穴が ないので なし）')
        ov.locator('.close').click(force=True); pg.wait_for_timeout(400)
        pg.locator('#recList .rsvf [data-act=memtog]').click(); pg.wait_for_timeout(800)
        check('mem' not in pg.evaluate("[...TengelLocal.mem.bets.values()].find(b => b.r === 9)") and pg.locator('#recList .memtop').count() == 0 and pg.locator('#recList .rsvf [data-act=memtog]').inner_text() == '思い出のレースに記録する' and '思い出から外したよ' in pg.locator('#toast').inner_text()
              and pg.locator(f'#recList .lrow:not(.memrow)[data-id="{b9c["id"]}"] .chip.memchip').count() == 0,
              '「思い出から外す」→ 記録から mem が 消える・欄と 印も 消える（レースの 記録は そのまま）')
        pg.locator('#recList .rsvf [data-act=memtog]').click(); pg.wait_for_timeout(400)
        pg.locator('#recList .rsvf .memchoose [data-act=memsave][data-v=a]').click(); pg.wait_for_timeout(800)
        pg.evaluate("TengelFx.set({ calm: true })")
        pg.locator('#recList .rsvf [data-act=memopen]').click(); pg.wait_for_timeout(1200)
        ov = pg.locator('#fxOv')
        check(pg.evaluate("[...TengelLocal.mem.bets.values()].find(b => b.r === 9).mem.v") == 'a' and ov.locator('.fxs.mem.calm .ov.miss.quiet.mem.f-turf').count() == 1 and ov.locator('.mring').count() == 1 and pg.evaluate('TengelFx.memInfo()') == {'v': 'a', 'frame': 'turf'},
              'もう一度 記録して ① を 選ぶ → 光の輪の 芝コースの わく（光の 輪）・控えめでも 同じ ボード（calm）')
        ov.locator('.close').click(force=True); pg.wait_for_timeout(300)
        pg.evaluate("TengelFx.set({ calm: null })")
        pg.evaluate("(async () => { const b = [...TengelLocal.mem.bets.values()].find(b => b.r === 9); const d = JSON.parse(JSON.stringify(b)); d.rsv.fx = 'hit'; await TengelLocal.putBets([d]); })()"); pg.wait_for_timeout(2400)
        bkm = json.loads(store['backup'] or '{}').get('bets', [])
        check(any(isinstance(x.get('mem'), dict) and x['mem'].get('v') == 'a' for x in bkm if x.get('r') == 9), f'思い出（mem）は 自動バックアップにも 入る（{[x.get("mem") for x in bkm if x.get("r") == 9]}）')
        pg.click('#rFilters [data-f=all]'); pg.wait_for_timeout(300)
        # どれが出るか（第4.118版・まさちゃんの 指定：決まった 条件）：当たった 組（どの 券種でも）ごとに 見る。G＝超大穴（10〜12）と ほかに 7〜12番人気・D＝超大穴（G で ない）・
        #   B＝大穴（7〜9）・H＝当たりは あるが 7〜12番人気が いない・M＝当たった 券種が 2つ以上。枠の 組は 枠番（人気を 見ない・M には 数える）・人気が わからない 馬と 13番人気より 下は 数えない
        RK = {str(i): i for i in range(1, 15)}   # 馬番＝人気順位（18.2 の例と同じ読み方）
        def spec(tri, others=(), ranks=RK):
            rows = [{'t': '3連単', 'state': '的中' if tri else '不的中', 'hits': [tri] if tri else [], 'n': 18}] + [{'t': t, 'state': st_, 'hits': h, 'n': 9} for t, st_, h in others]
            return {'r': 9, 'n': 14, 'rows': rows, 'ranks': ranks}
        def rsp(rows, ranks=RK):   # 3連単の 行なし（券種を 自由に）
            return {'r': 9, 'n': 14, 'rows': [{'t': t, 'state': st_, 'hits': h, 'n': 9} for t, st_, h in rows], 'ranks': ranks}
        D = lambda sp: pg.evaluate("(s) => { const d = TengelFx.decide(s); return [d.tier, d.kind, d.multi ? 'M' : '', d.trig ? d.trig.t : '', d.supers.map(x => x.no).join(','), d.bigs.map(x => x.no).join(',')].join('|'); }", sp)
        DCASES = [
            ('3連単 11・8・2', spec([11, 8, 2]), 'g|sgd||3連単|11|8'),
            ('3連単 11・12・2（超大穴 2頭 → G）', spec([11, 12, 2]), 'g|sgd||3連単|11,12|'),
            ('3連単 11・10・7', spec([11, 10, 7]), 'g|sgd||3連単|11,10|7'),
            ('3連単 11・6・2', spec([11, 6, 2]), 'd|nd||3連単|11|'),
            ('3連単 8・5・2', spec([8, 5, 2]), 'b|big||3連単||8'),
            ('3連単 8・7・2', spec([8, 7, 2]), 'b|big||3連単||8,7'),
            ('3連単 1・6・2', spec([1, 6, 2]), 'h|hit||||'),
            ('3連単 13・8・2（13番人気は 数えない）', spec([13, 8, 2]), 'b|big||3連単||8'),
            ('3連単 13・14・2', spec([13, 14, 2]), 'h|hit||||'),
            ('3連単 11・13・2（13番人気は 大穴以上で ない → D）', spec([11, 13, 2]), 'd|nd||3連単|11|'),
            ('3連単 11・6・99（人気が わからない 馬は 数えない）', spec([11, 6, 99]), 'd|nd||3連単|11|'),
            ('3連単 99・8・2', spec([99, 8, 2]), 'b|big||3連単||8'),
            ('馬単だけ 11→8', rsp([('馬単', '的中', [[11, 8]])]), 'g|sgd||馬単|11|8'),
            ('馬単だけ 11→6', rsp([('馬単', '的中', [[11, 6]])]), 'd|nd||馬単|11|'),
            ('馬単だけ 6→2', rsp([('馬単', '的中', [[6, 2]])]), 'h|hit||||'),
            ('ワイド 6-2・11-8', rsp([('ワイド', '的中', [[6, 2], [11, 8]])]), 'g|sgd||ワイド|11|8'),
            ('ワイド 8-2', rsp([('ワイド', '的中', [[8, 2]])]), 'b|big||ワイド||8'),
            ('単勝 11', rsp([('単勝', '的中', [[11]])]), 'd|nd||単勝|11|'),
            ('単勝 8', rsp([('単勝', '的中', [[8]])]), 'b|big||単勝||8'),
            ('単勝 6', rsp([('単勝', '的中', [[6]])]), 'h|hit||||'),
            ('複勝 11・6・2', rsp([('複勝', '的中', [[11], [6], [2]])]), 'd|nd||複勝|11|'),
            ('単勝 11＋複勝 11（M）', rsp([('単勝', '的中', [[11]]), ('複勝', '的中', [[11]])]), 'd|sd|M|単勝|11|'),
            ('枠単 8→7（枠番なので 人気を 見ない）', rsp([('枠単', '的中', [[8, 7]])]), 'h|hit||||'),
            ('枠複 8-7＋馬単 1→2', rsp([('枠複', '的中', [[8, 7]]), ('馬単', '的中', [[1, 2]])]), 'h|hit|M|||'),
            ('3連単 11・6・2＋枠複 8-7（枠も M に 数える）', spec([11, 6, 2], [('枠複', '的中', [[8, 7]])]), 'd|sd|M|3連単|11|'),
            ('3連単 11・8・2＋馬単 11→8', spec([11, 8, 2], [('馬単', '的中', [[11, 8]])]), 'g|spg|M|3連単|11|8'),
            ('3連単 不的中・馬単 11→8＋ワイド 11-8', spec(None, [('馬単', '的中', [[11, 8]]), ('ワイド', '的中', [[11, 8]])]), 'g|spg|M|馬単|11|8'),
            ('3連単 1・2・3＋馬単 11→8', spec([1, 2, 3], [('馬単', '的中', [[11, 8]])]), 'g|spg|M|馬単|11|8'),
            ('3連単 11・6・2（D）＋ワイド 11-8（G）', spec([11, 6, 2], [('ワイド', '的中', [[11, 8]])]), 'g|spg|M|ワイド|11|8'),
            ('3連単 8・5・2（B）＋単勝 11（D）', spec([8, 5, 2], [('単勝', '的中', [[11]])]), 'd|sd|M|単勝|11|'),
            ('3連単 1・2・3＋馬単 1→2', spec([1, 2, 3], [('馬単', '的中', [[1, 2]])]), 'h|hit|M|||'),
            ('当たりなし', spec(None, [('馬単', '不的中', [])]), 'miss|miss||||'),
            ('返還だけ', spec(None, [('馬単', '返還', [])]), 'miss|miss||||'),
        ]
        dgot = [D(sp_) for _, sp_, _ in DCASES]
        dbad = [(nm, g_, e_) for (nm, _, e_), g_ in zip(DCASES, dgot) if g_ != e_]
        check(not dbad, f'どれが出るか（第4.118版）：G／D／B／H・M・段を 決めた 券種・帯の 超大穴と 大穴（馬単だけ・ワイド・単勝・複勝・枠は 人気を 見ない・13番人気と 人気の わからない 馬は 数えない・超大穴 2頭は G・2券種で M）{len(DCASES)}こ（おかしい：{dbad}）')
        gdd = pg.evaluate("(s) => TengelFx.decide(s)", spec([11, 8, 2], [('馬単', '的中', [[11, 8]])]))
        check(gdd == {'kind': 'spg', 'tier': 'g', 'multi': True, 'supers': [{'no': 11, 'rank': 11}], 'bigs': [{'no': 8, 'rank': 8}], 'trig': {'t': '3連単', 'c': [11, 8, 2]}},
              f'decide の 中身：種類・段（tier）・M（multi）・帯の 超大穴と 大穴・段を 決めた 組（trig：券種と 組）（{gdd}）')
        # 第4.86版（まさちゃん「…赤い×が書いてある演出消して！」）：隠れど的中は なし（デカ的中は いつも デカ的中・数も 数えない）・超プレミアムど的中も なし（乱数 0 でも プレミアム）
        pg.evaluate("localStorage.removeItem('tengel.fxhidden'); TengelFx._rand = () => 0")
        seq = []
        for tri in ([8, 5, 2], [8, 5, 2], [11, 6, 2], [8, 5, 2], [8, 5, 2]):
            seq.append(pg.evaluate("(s) => TengelFx.show(s)", spec(tri))); pg.wait_for_timeout(150)
            pg.evaluate('TengelFx.close()'); pg.wait_for_timeout(100)
        check(seq == ['big', 'big', 'pc', 'big', 'big'] and pg.evaluate("localStorage.getItem('tengel.fxhidden')") is None and pg.evaluate("typeof TengelFx.hidden") == 'undefined',
              f'第4.86版：隠れど的中は なし（デカ的中は いつも デカ的中・数も 数えない）・第4.118版：ノーマルど的中の くじは 乱数 0 で プレミアム（超プレミアムど的中は なし）（{seq}）')
        pg.evaluate("TengelFx._rand = () => 0.99")   # ここからは くじを 外す（第4.77版：くじの ど的中は ノーマルど的中（nd）なので、CSS の ど的中は force で 出す）
        pg.wait_for_timeout(1900)
        # ど的中：第4.109版から 前の CSS の ど的中（fz：フリーズ・ネオンの カット）は アプリに 入れない（くじで 出ない）→ force:'fz' は ノーマルど的中（nd）。
        #   PUSH は ど的中の 形（そのテーマの PUSH を 1.4倍）・動画が 読めない（テストの mp4）→ さいごの 1まい → 1.3秒で ボード（超大穴の帯・3連単の行の超大穴の馬番に輪）
        kf = pg.evaluate("(s) => TengelFx.show(Object.assign({ force: 'fz' }, s))", spec([11, 6, 2], [('馬単', '的中', [[11, 6], [6, 2]]), ('ワイド', '不的中', [])])); pg.wait_for_timeout(200)
        fo = pg.locator('#fxOv')
        check(kf == 'nd' and fo.locator('.ov.fz .pbox.pz .push').count() == 1 and fo.locator('.push.fz').count() == 0 and fo.locator('.pbox.rbw').count() == 0 and fo.locator('.aura, .prays, .edge, .frame').count() == 4 and fo.locator('.tap').inner_text() == 'タップ！' and 'k-nd' in fo.get_attribute('class') and pg.evaluate('TengelFx.current()')['pz'] == 1.4
              and pg.evaluate("window.__FX.reveal.fz") is None and pg.evaluate("window.__FX.push.fz") is None and pg.evaluate("window.__FX.push.big") is None and pg.evaluate("window.__FX.sfx.fz") is None and pg.evaluate("window.__FX.assets.nglow") is None,
              f'ど的中（第4.109版）：force の fz は ノーマルど的中（nd）・そのテーマの PUSH を 1.4倍（虹色では ない）・前の ど的中の 押したあと・テーマの ない PUSH・音・ネオンの 絵は 入って いない（{kf}）')
        fo.locator('.push').click(force=True); pg.wait_for_timeout(2200)
        zx = fo.locator('.rb .brows li.top .n.zx')
        check(fo.locator('.fxs .ov.fz.nd').count() == 1 and fo.locator('.nic').count() == 0 and fo.locator('.rb.fz .bh').text_content() == 'ど的中！！！' and '超大穴' in fo.locator('.rb .zrib').text_content() and '11番人気が3連単に！' in fo.locator('.rb .zrib').text_content() and zx.count() == 1 and zx.text_content() == '11' and fo.locator('.rb .brows li').nth(1).locator('.bc').count() == 2
              and pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.nd .hb')).opacity") == '1',
              f'ど的中の ボード（ノーマルど的中の さいごの 1まい → 1.3秒）：「ど的中！！！」・帯「超大穴 11 11番人気が3連単に！」・3連単の 11 に虹色の輪・馬単の当たり2つ（{fo.locator(".rb .zrib").text_content()}）')
        pg.evaluate('TengelFx.close()'); pg.wait_for_timeout(100)
        # 設定：的中エフェクト オフ → PUSH・演出なしでボードだけ静かに／演出を控えめにする → .calm／効果音
        pg.evaluate("TengelFx.set({ effects: false })"); pg.wait_for_timeout(100)
        k = pg.evaluate("(s) => TengelFx.show(s)", spec([8, 5, 2])); pg.wait_for_timeout(300)
        qo = pg.locator('#fxOv')
        check(k == 'big' and qo.locator('.push').count() == 0 and qo.locator('.fxs .ov.miss.quiet').count() == 1 and qo.locator('.rb.big .bh').inner_text() == 'デカ的中!!' and pg.evaluate('TengelFx.current()')['quiet'] is True and pg.evaluate("localStorage.getItem('tengel.fxhidden')") is None,
              '的中エフェクト オフ：PUSH・演出なしで、ボード（見出しは当たりの強さのまま）だけ静かに')
        pg.evaluate('TengelFx.close()')
        pg.evaluate("TengelFx.set({ effects: true, calm: true })"); pg.wait_for_timeout(100)
        pg.evaluate("(s) => TengelFx.show(Object.assign({ force: 'fz' }, s))", spec([11, 6, 2])); pg.wait_for_timeout(200)
        check(pg.locator('#fxOv .fxs.calm .ov.fz .pbox.pz .push').count() == 1 and pg.evaluate("getComputedStyle(document.querySelector('#fxOv .aura')).animationName") == 'none', '演出を控えめにする：ど的中の まわりの 動きが止まる（視差効果を減らすと同じ形）')
        pg.evaluate('TengelFx.tap()'); pg.wait_for_timeout(200)
        cfz = pg.evaluate('TengelFx.current()')
        cfz['ndt'] = pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.nd .ndt')).display")
        check(cfz['kind'] == 'nd' and cfz['film'] == 2 and pg.locator('#fxOv .ov.nd.still').count() == 1 and pg.locator('#fxOv video.sgv').count() == 0 and cfz['ndt'] == 'none',
              f'控えめ：ど的中（ノーマル）は 押した 画面（第4.118版で 直した）も 動画も 出さず さいごの 1まい（still）→ ボード（{cfz}）')
        pg.evaluate('TengelFx.close()')
        # ---- 第5弾（16.3）・第4.118版：特別な 演出は 決まった 条件（くじは ノーマルど的中 → プレミアムど的中の 6分の1 だけ）→ PUSH は ど的中と 同じ → 押したあと → ど的中の 形の ボード ----
        pg.evaluate("window.__seq = arr => { let i = 0; TengelFx._rand = () => arr[Math.min(i++, arr.length - 1)]; }")   # 乱数を 順に 決める
        LOTS = [pg.evaluate("(a) => { const o = []; for (const k of ['nd', 'sd', 'sgd', 'spg', 'gk', 'big', 'hit', 'miss']) { window.__seq(a); o.push(TengelFx.lottery(k)); } return o; }", a) for a in ([0], [0.16], [0.17], [0.99])]
        check(LOTS == [['pc', 'sd', 'sgd', 'spg', 'gk', 'big', 'hit', 'miss']] * 2 + [['nd', 'sd', 'sgd', 'spg', 'gk', 'big', 'hit', 'miss']] * 2,
              f'くじ（第4.118版）：ノーマルど的中だけ 6分の1（乱数 0・0.16 → プレミアム／0.17・0.99 → ノーマル）・ほかの 種類は くじを ひかない（{LOTS}）')
        SHOWC = "(s) => { const k = TengelFx.show(s); TengelFx.close(); return k; }"
        PCS = []
        for a, sp_ in (([0.16], spec([11, 6, 2])), ([0.17], spec([11, 6, 2])), ([0], rsp([('単勝', '的中', [[11]])])), ([0], spec([11, 6, 2], [('馬単', '的中', [[11, 6]])])), ([0], spec([11, 8, 2])), ([0], spec([8, 5, 2])), ([0], spec([1, 6, 2]))):   # 超プレミアム神様（G・M）は 下の 神様極的中の テストで（ここで 出すと 昇格の 動画を 先に 作る）
            pg.evaluate("(a) => window.__seq(a)", a)
            PCS.append(pg.evaluate(SHOWC, sp_)); pg.wait_for_timeout(60)
        check(PCS == ['pc', 'nd', 'pc', 'sd', 'sgd', 'big', 'hit'],
              f'出す 種類（第4.118版）：D で M で ない → 乱数 0.16 で プレミアムど的中・0.17 で ノーマルど的中（単勝だけでも）／D・M → 極ど的中・G → 超神様・B → デカ・H → 的中（乱数 0 でも くじなし）（{PCS}）')
        pg.evaluate("TengelFx._rand = () => 0.99")
        kk = pg.evaluate("(s) => TengelFx.show(s)", spec([11, 8, 2], [('馬単', '不的中', []), ('ワイド', '不的中', [])])); pg.wait_for_timeout(300)
        so = pg.locator('#fxOv')
        check(kk == 'sgd' and so.locator('.ov.fz .pbox.rbw .push .rbf').count() == 1 and so.locator('.pbox .rba').count() == 1 and 'k-sgd' in so.get_attribute('class') and pg.evaluate('TengelFx.current()')['kind'] == 'sgd' and pg.evaluate('TengelFx.current()')['pz'] == 1.6, f'3連単 11・8・2 だけ（G・M で ない）→ 超神様的中（PUSH は そのテーマの PUSH を 1.6倍・虹色）（{kk}）')
        pg.evaluate('TengelFx.close()')
        # 第4.118版：帯と ボードの いちばん 上の 行は 段を 決めた 組の 券種（3連単で ない とき）・超大穴と 大穴の 輪も その 行
        RB = "(() => { const o = document.querySelector('#fxOv'); const z = o.querySelector('.rb .zrib'); return { rib: z ? z.textContent.replace(/\\s+/g, '') : '', rows: [...o.querySelectorAll('.rb .brows li')].map(li => li.querySelector('.bt').textContent + (li.classList.contains('top') ? '*' : '') + (li.querySelectorAll('.n.zx').length ? ':' + [...li.querySelectorAll('.n.zx')].map(n => n.textContent).join(',') : '')) }; })()"
        RBS = []
        for kd, sp_ in (('spg', spec(None, [('ワイド', '的中', [[11, 8]]), ('馬単', '的中', [[11, 8]]), ('単勝', '不的中', [])])),
                        ('nd', rsp([('単勝', '不的中', []), ('馬単', '的中', [[11, 6]]), ('ワイド', '不的中', [])])),
                        ('sd', spec([8, 5, 2], [('単勝', '的中', [[11]])])),
                        ('big', rsp([('単勝', '不的中', []), ('ワイド', '的中', [[8, 2]])])),
                        ('hit', rsp([('馬単', '的中', [[6, 2]]), ('単勝', '的中', [[6]])]))):
            pg.evaluate("TengelFx.set({ effects: false })")   # 静かな ボード（すぐ 出る）で 見る
            k_ = pg.evaluate("(s) => TengelFx.show(s)", sp_); pg.wait_for_timeout(250)
            RBS.append((k_, pg.evaluate(RB))); pg.evaluate('TengelFx.close()'); pg.wait_for_timeout(60)
        pg.evaluate("TengelFx.set({ effects: true })")
        check(RBS == [('spg', {'rib': '超大穴11大穴8が馬単に！', 'rows': ['馬単*:11,8', '3連単', 'ワイド', '単勝']}),
                      ('nd', {'rib': '超大穴1111番人気が馬単に！', 'rows': ['馬単*:11', '単勝', 'ワイド']}),
                      ('sd', {'rib': '超大穴1111番人気が単勝に！', 'rows': ['単勝*:11', '3連単']}),
                      ('big', {'rib': '', 'rows': ['ワイド*', '単勝']}),
                      ('hit', {'rib': '', 'rows': ['馬単', '単勝']})],
              f'帯「…が（段を 決めた 券種）に！」と その 券種の 行が いちばん上（虹色の 輪も その 行）・デカ的中は 帯なし・的中は 予約した 順（第4.118版）（{RBS}）')
        # 的中エフェクト オフ（第4.118版）：同じ 決まった 種類（プレミアムの くじは ひかない → ノーマルど的中）・見出しは その 種類の もの・PUSH なしで すぐ ボード
        pg.evaluate("TengelFx.set({ effects: false })"); pg.evaluate("TengelFx._rand = () => 0")   # くじを ひけば プレミアムに なる 乱数
        QB = "(() => { const o = document.querySelector('#fxOv'); const z = o.querySelector('.rb .zrib'); return [document.querySelectorAll('#fxOv .push').length, document.querySelectorAll('#fxOv .fxs .ov.miss.quiet').length, o.querySelector('.rb .bh').textContent.replace(/\\s+/g, ''), z ? z.textContent.replace(/\\s+/g, '') : ''].join('|'); })()"
        QKS = []
        for sp_ in (spec([11, 8, 2]), spec([11, 8, 2], [('馬単', '的中', [[11, 8]])]), dict(spec([11, 8, 2], [('馬単', '的中', [[11, 8]])]), godN=2), spec([11, 6, 2], [('馬単', '的中', [[11, 6]])]),
                    spec([11, 6, 2]), spec([8, 5, 2]), spec([1, 6, 2]), spec(None, [('馬単', '不的中', [])])):
            k_ = pg.evaluate("(s) => TengelFx.show(s)", sp_); pg.wait_for_timeout(200)
            QKS.append(k_ + '|' + pg.evaluate(QB)); pg.evaluate('TengelFx.close()'); pg.wait_for_timeout(60)
        pg.evaluate("TengelFx.set({ effects: true })"); pg.evaluate("TengelFx._rand = () => 0.99")
        check(QKS == ['sgd|0|1|超神様的中！！！|超大穴11大穴8が3連単に！', 'spg|0|1|超神様的中！！！|超大穴11大穴8が3連単に！', 'gk|0|1|神様極的中！！！|超大穴11大穴8が3連単に！', 'sd|0|1|ど的中！！！|超大穴1111番人気が3連単に！',
                      'nd|0|1|ど的中！！！|超大穴1111番人気が3連単に！', 'big|0|1|デカ的中!!|', 'hit|0|1|的中！|', 'miss|0|1|ハズレ|'],
              f'的中エフェクト オフ（第4.118版）：同じ 種類・プレミアムの くじは ひかない（乱数 0 でも ノーマルど的中）・見出しは その 種類の もの（{QKS}）')
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
        check(pg.locator('#fxOv').count() == 0 and pg.locator('#fxVh video[data-film=sgd_film]').count() == 1 and pg.locator('#fxVh video[data-film=spg_up]').count() == 0 and pg.evaluate("[...document.querySelectorAll('#fxVh video')].every(v => v.paused && v.currentTime === 0 && !v.className)"), '（第4.109版：超神様だけ 出した ときは 昇格の 動画 spg_up は 読まない）「とじる」→ 動画は 止めて はじめに もどして 置き場へ（動画は 出す 演出の 分だけ 作る）')
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
        pr0 = pg.evaluate("(() => { const o = document.querySelector('#fxOv .ov.nd'); const h = o && o.querySelector('.hb'); const pr = o && o.querySelector('.ndt .pzw .pressed'); const a = pr && pr.getAnimations ? pr.getAnimations().filter(x => x.animationName && x.animationName.endsWith('ndtP')) : []; return { nd: !!o, sd: !!document.querySelector('#fxOv .ov.sd'), pc: document.querySelectorAll('#fxOv .pc').length, hb: !h || getComputedStyle(h).visibility === 'hidden' || getComputedStyle(h).opacity === '0', pre: (TengelFx.current() || {}).pre, push: document.querySelectorAll('#fxOv .pbox .push').length, press: a.length === 1 && a[0].playState === 'running', ring: document.querySelectorAll('#fxOv .ov.nd .ndt .ndtr').length, bx: document.querySelectorAll('#fxOv .ov.nd .ndt .bx').length }; })()")
        check(pr0['nd'] and not pr0['sd'] and pr0['pc'] == 0 and pr0['hb'] and pr0['pre'] in (1, 2) and pr0['push'] == 0 and pr0['press'] and pr0['ring'] == 1 and pr0['bx'] == 0,
              f'極ど的中（第4.77版・第4.79版）：押すと まず ノーマルど的中の 幕（プチュンなし・ボードなし）・PUSH の 画面とは 別の 押した 画面（押された PUSH が ポチッと へこむ・うすい 光の 輪・爆発は なし）（{pr0}）')
        if HAVE_SD:
            pg.wait_for_function("() => (TengelFx.current() || {}).pre === 2", timeout=6000)
            v = pg.evaluate("(() => { const v = document.querySelector('#fxOv video.sgv.on'); return v ? { paused: v.paused, film: v.getAttribute('data-film') } : null; })()")
            check(v is not None and v['paused'] is False and v['film'] == 'nd_film' and pg.locator('#fxOv .ov.nd.go').count() == 1 and 'pre:sd' in pg.evaluate('window.__fxEv') and pg.evaluate('TengelFx.current()')['film'] == 0,
                  f'極ど的中：ノーマルど的中の 動画が 舞台で 動きだす（{v}）')
            pg.wait_for_function("() => getComputedStyle(document.querySelector('#fxOv .ov.nd .ndt')).visibility === 'hidden'", timeout=3000)
            check((TengelFx_pre := pg.evaluate('TengelFx.current().pre')) == 2, f'極ど的中：押した 画面は 約1秒で 消える（ノーマルの 動画が 見える）（pre {TengelFx_pre}）')
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
        kn = pg.evaluate("(s) => TengelFx.show(s)", spec([11, 6, 2], [('馬単', '不的中', [])])); pg.wait_for_timeout(300)
        po = pg.locator('#fxOv')
        check(kn == 'nd' and pg.locator('#fxVh video[data-film=nd_film]').count() == 1 and pg.evaluate("document.querySelector('#fxVh video[data-film=nd_film]').preload") == 'auto'
              and po.locator('.ov.fz .pbox.pz .push').count() == 1 and po.locator('.pbox.rbw').count() == 0 and 'k-nd' in po.get_attribute('class') and pg.evaluate('TengelFx.current()')['pz'] == 1.4,
              f'ノーマルど的中（第4.77版・第4.118版）：D で M で ない（乱数 0.5 → プレミアムで ない）→ nd・PUSH は ど的中と 同じ（1.4倍）・動画を 出る 前に 読んでおく（{kn}）')
        pg.evaluate("window.__fxEv = []"); pg.evaluate('TengelFx.tap()'); pg.wait_for_timeout(150)
        nd0 = pg.evaluate("(() => { const o = document.querySelector('#fxOv .ov.nd'); const h = getComputedStyle(document.querySelector('#fxOv .ov.nd .hb')); const t = o.querySelector('.ndt'); const pr = t && t.querySelector('.pzw .pressed'); const a = pr && pr.getAnimations ? pr.getAnimations().filter(x => x.animationName && x.animationName.endsWith('ndtP')) : []; const g = t && t.querySelector('.ndtr'); return { pc: document.querySelectorAll('#fxOv .ov.nd .pc').length, bg: getComputedStyle(o).backgroundColor, cls: o.className, hb: h.visibility === 'hidden' || h.opacity === '0', img: [...o.querySelectorAll('img')].map(i => i.src.split('/').pop()), push: document.querySelectorAll('#fxOv .pbox .push').length, press: a.length === 1 && a[0].playState === 'running', pz: t ? t.querySelector('.pzw').style.getPropertyValue('--pz') : '', glow: !!(g && g.getAnimations().length), bx: t ? t.querySelectorAll('.bx').length : 0, z: t ? getComputedStyle(t).zIndex : '', vis: t ? getComputedStyle(t).visibility : '' }; })()")
        check(nd0['pc'] == 0 and (nd0['bg'] == 'rgb(0, 0, 0)' or 'go' in nd0['cls']) and nd0['hb'] and nd0['img'] == ['nd_last.webp'] and 'fz' in nd0['cls'],   # 動画が もう 動いて いれば go（はじめの 1秒は 動画の 黒）
              f'ノーマルど的中：押すと 暗く なる（プチュンは なし）・ボードは まだ・絵は 動画の さいごの 1まい だけ（{nd0}）')
        check(nd0['push'] == 0 and nd0['press'] and nd0['pz'] == '1.4' and nd0['glow'] and nd0['bx'] == 0 and nd0['z'] == '20' and nd0['vis'] == 'visible' and pg.evaluate("window.__FX.sfx.ndt") == 'sfx_ndt.m4a',
              f'ノーマルど的中（第4.79版）：押すと PUSH の 画面とは 別の 押した 画面（押された PUSH が 1.4倍の まま ポチッと へこむ・うすい 光の 輪・爆発は なし・音 sfx_ndt）（{nd0}）')
        if HAVE_ND:
            pg.wait_for_function("() => (TengelFx.current() || {}).film === 1", timeout=6000)
            v = pg.evaluate("(() => { const v = document.querySelector('#fxOv video.sgv.on'); return v ? { paused: v.paused, film: v.getAttribute('data-film') } : null; })()")
            check(v is not None and v['paused'] is False and v['film'] == 'nd_film' and pg.locator('#fxOv .ov.nd.go').count() == 1 and pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.nd')).backgroundColor") == 'rgba(0, 0, 0, 0)' and 'film:nd' in pg.evaluate('window.__fxEv')
                  and pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.nd .hb')).opacity") == '0',
                  f'ノーマルど的中：動画が 舞台で 動きだす（go・幕が すきとおる）・ボードは まだ（{v}）')
            pg.evaluate("window.__goT = performance.now()")
            pg.wait_for_function("() => getComputedStyle(document.querySelector('#fxOv .ov.nd .ndt')).visibility === 'hidden'", timeout=3000)
            check(pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.nd .ndt')).visibility") == 'hidden', 'ノーマルど的中：押した 画面は 約1秒で 消える（動画が 見える）')
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
        # ---- 第4.117版：神様極的中（gk）----
        #   神様の 条件（decide の gd）で godN（結果を 決めた さいごの 30レースの 中の 神様の 数：src.html の godCount）が 2以上 → くじを ひかずに gk（超神様・超プレミアム神様より 先）。
        #   PUSH は 超神様と 同じ 虹色の 1.6倍（まさちゃん「金のpushボタンはいらない！今まで通りでいいよ！」）→ 押すと ノーマルど的中と 同じ 押した 画面（.ndt・音 ndt）
        #   → 動画（gk_film）→ 12秒で ボード「神様極的中！！！」（帯は 超大穴と 大穴）／読めない → さいごの 1まい（still）→ 1.3秒 ボード
        pg.evaluate("window.__FX.films = { sgd_film: 'sgd_film.webm', spg_up: 'spg_up.webm', sd_film: 'sd_film.webm', nd_film: 'nd_film.webm', gk_film: 'gk_film.webm' }")
        HAVE_GK = pg.evaluate("fetch('gk_film.webm', { method: 'HEAD' }).then(r => r.ok).catch(() => false)")
        GS = spec([11, 8, 2], [('馬単', '的中', [[11, 8]]), ('ワイド', '不的中', [])])
        gks = []
        for gn, rnd in ((None, [0]), (0, [0]), (1, [0.99]), (1, [0]), (2, [0]), (2, [0.99]), (7, [0.5])):
            pg.evaluate("(a) => window.__seq(a)", rnd)
            gks.append(pg.evaluate("(s) => { const k = TengelFx.show(s); TengelFx.close(); return k; }", GS if gn is None else dict(GS, godN=gn))); pg.wait_for_timeout(60)
        pg.evaluate("TengelFx._rand = () => 0.99")
        gfz = [pg.evaluate("(s) => { const k = TengelFx.show(s); TengelFx.close(); return k; }", dict(sp_, godN=9)) for sp_ in (spec([11, 8, 2]), spec([11, 6, 2], [('馬単', '的中', [[11, 6]])]), spec([11, 6, 2]), spec([8, 5, 2], [('馬単', '的中', [[8, 5]])]))]
        check(gks == ['spg', 'spg', 'spg', 'spg', 'gk', 'gk', 'gk'] and gfz == ['sgd', 'sd', 'nd', 'big'],
              f'神様極的中の 出かた（第4.118版）：G・M で godN 2以上 → 神様極的中（超プレミアム神様より 先）・godN 0・1・なし → 超プレミアム神様（くじなし）・G で M で ない／D／B は godN が あっても その 種類（{gks}・{gfz}）')
        kg = pg.evaluate("(s) => TengelFx.show(s)", dict(GS, godN=2)); pg.wait_for_timeout(300)
        PB = "(() => { const b = document.querySelector('#fxOv .pbox'), p = b && b.querySelector('.push'); return { box: b ? b.className : '', pz: b ? b.style.getPropertyValue('--pz') : '', push: p ? p.className : '', rbf: document.querySelectorAll('#fxOv .pbox .push .rbf').length, rba: document.querySelectorAll('#fxOv .pbox .rba').length, cur: TengelFx.current().pz, label: p ? p.getAttribute('aria-label') : '', fz: !!document.querySelector('#fxOv .ov.fz .pbox') }; })()"
        pbg = pg.evaluate(PB)
        gsx = pg.evaluate('TengelFx.sfxState()')
        check(kg == 'gk' and 'k-gk' in pg.locator('#fxOv').get_attribute('class') and pbg['fz'] and 'rbw' in pbg['box'] and pbg['rbf'] == 1 and pbg['rba'] == 1 and pbg['cur'] == 1.6 and pbg['label'] == '神様極的中ボタン'
              and pg.locator('#fxVh video[data-film=gk_film]').count() == 1 and pg.evaluate("document.querySelector('#fxVh video[data-film=gk_film]').preload") == 'auto' and {'fz_push', 'ndt', 'gk'} <= set(gsx['keys'])
              and pg.evaluate("window.__FX.sfx.gk") == 'sfx_gk.m4a' and pg.evaluate("window.__FX.sfx.fz_push") == 'sfx_fz_push.m4a',
              f'神様極的中の PUSH：超神様と 同じ 虹色の PUSH（1.6倍・まわる 虹・面に 流れる 虹）・名前「神様極的中ボタン」・音は ど的中の PUSH の 音（fz_push）・出る 前に 動画と 音（ndt・gk）を 読んでおく（{pbg}）')
        pg.evaluate('TengelFx.close()'); pg.wait_for_timeout(100)
        pg.evaluate("(s) => TengelFx.show(Object.assign({ force: 'sgd' }, s))", GS); pg.wait_for_timeout(300)
        pbs = pg.evaluate(PB)
        pg.evaluate('TengelFx.close()'); pg.wait_for_timeout(100)
        check({k: v for k, v in pbg.items() if k != 'label'} == {k: v for k, v in pbs.items() if k != 'label'} and pbs['label'] == '超神様的中ボタン',
              f'第4.117版（まさちゃん「金のpushボタンはいらない！今まで通りでいいよ！」）：神様極的中の PUSH は 超神様的中と 同じ 形・大きさ・虹色（金の PUSH は なし）（{pbs}）')
        pg.evaluate("(s) => TengelFx.show(s)", dict(GS, godN=3)); pg.wait_for_timeout(300)
        pg.evaluate("window.__fxEv = []"); pg.evaluate('TengelFx.tap()'); pg.wait_for_timeout(150)
        gk0 = pg.evaluate("(() => { const o = document.querySelector('#fxOv .ov.gk'); const h = getComputedStyle(o.querySelector('.hb')); const t = o.querySelector('.ndt'); const pr = t && t.querySelector('.pzw .pressed'); const a = pr && pr.getAnimations ? pr.getAnimations().filter(x => x.animationName && x.animationName.endsWith('ndtP')) : []; return { cls: o.className, bg: getComputedStyle(o).backgroundColor, hb: h.visibility === 'hidden' || h.opacity === '0', img: [...o.querySelectorAll('img')].map(i => i.src.split('/').pop()), press: a.length === 1 && a[0].playState === 'running', pz: t ? t.querySelector('.pzw').style.getPropertyValue('--pz') : '', ring: t ? t.querySelectorAll('.ndtr').length : 0, z: t ? getComputedStyle(t).zIndex : '', vis: t ? getComputedStyle(t).visibility : '', push: document.querySelectorAll('#fxOv .pbox .push').length, sr: (o.querySelector('.sr') || {}).textContent || '', oz: getComputedStyle(o).zIndex }; })()")
        check('fz' in gk0['cls'] and (gk0['bg'] == 'rgb(0, 0, 0)' or 'go' in gk0['cls']) and gk0['hb'] and gk0['img'] == ['gk_last.webp'] and gk0['press'] and gk0['pz'] == '1.6' and gk0['ring'] == 1 and gk0['z'] == '20' and gk0['vis'] == 'visible' and gk0['push'] == 0 and '神様極的中' in gk0['sr'] and gk0['oz'] == '31',
              f'神様極的中：押すと ノーマルど的中と 同じ 押した 画面（押された PUSH が 1.6倍の まま ポチッと へこむ・うすい 光の 輪）・黒い 幕・ボードは まだ・絵は 動画の さいごの 1まい だけ（{gk0}）')
        if HAVE_GK:
            pg.wait_for_function("() => (TengelFx.current() || {}).film === 1", timeout=6000)
            v = pg.evaluate("(() => { const v = document.querySelector('#fxOv video.sgv.on'); return v ? { paused: v.paused, film: v.getAttribute('data-film') } : null; })()")
            check(v is not None and v['paused'] is False and v['film'] == 'gk_film' and pg.locator('#fxOv .ov.gk.go').count() == 1 and pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.gk')).backgroundColor") == 'rgba(0, 0, 0, 0)' and 'film:gk' in pg.evaluate('window.__fxEv')
                  and pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.gk .hb')).opacity") == '0' and pg.locator('#fxOv video').count() == 1,
                  f'神様極的中：動画が 舞台で 動きだす（go・幕が すきとおる）・ボードは まだ（{v}）')
            pg.evaluate("window.__goT = performance.now()")
            pg.wait_for_function("() => getComputedStyle(document.querySelector('#fxOv .ov.gk .ndt')).visibility === 'hidden'", timeout=3000)
            check(pg.evaluate("performance.now() - window.__goT") < 1500, '神様極的中：押した 画面は すぐ（約0.55秒）消える（動画の はじめの 真っ暗の あいだ）')
            pg.wait_for_function("() => performance.now() - window.__goT > 11400", timeout=14000)
            hb114 = pg.evaluate("(() => { const h = getComputedStyle(document.querySelector('#fxOv .ov.gk .hb')); return { op: h.opacity, k: getComputedStyle(document.querySelector('#fxOv .ov.gk .gkk')).opacity, t: Math.round(performance.now() - window.__goT) }; })()")
            check(hb114['op'] == '0' and hb114['k'] == '0', f'神様極的中：11.4秒（さいごの 場面：虹色の 極と 雷）は まだ ボードを 出さない（{hb114}）')
            pg.wait_for_function("() => performance.now() - window.__goT > 13500", timeout=4000)
            gb = pg.evaluate("(() => { const z = document.querySelector('#fxOv .ov.gk .rb .zrib'); return { hb: getComputedStyle(document.querySelector('#fxOv .ov.gk .hb')).opacity, close: getComputedStyle(document.querySelector('#fxOv .close')).visibility, t: document.querySelector('#fxOv .rb.fz .bh').innerText, rib: z ? z.innerText.replace(/\\s+/g, '') : '', zx: [...document.querySelectorAll('#fxOv .rb .brows li.top .n.zx')].map(n => n.innerText) }; })()")
            check(gb['hb'] == '1' and gb['close'] == 'visible' and gb['t'] == '神様極的中！！！' and gb['rib'] == '超大穴11大穴8が3連単に！' and gb['zx'] == ['11', '8'],
                  f'神様極的中：12秒で ボード「神様極的中！！！」（帯は 超大穴 11 と 大穴 8・3連単の 11 と 8 に 虹色の 輪）→「とじる」（{gb}）')
        else:
            print('  ⚠️ 神様極的中の 動画の webm が ない（ffmpeg で 作ると 動画の 流れも 確かめる）')
        pg.evaluate('TengelFx.close()'); pg.wait_for_timeout(200)
        check(pg.locator('#fxOv').count() == 0 and pg.evaluate("[...document.querySelectorAll('#fxVh video')].every(v => v.paused && v.currentTime === 0 && !v.className)"), '神様極的中：「とじる」→ 動画を 止めて はじめに もどして 置き場へ')
        pg.evaluate("window.__FX.films = Object.assign({}, window.__FX.films, { gk_film: 'nai_gk_film.webm' })")   # ない 名前 → error → still
        pg.evaluate("(s) => TengelFx.show(Object.assign({ force: 'gk' }, s))", GS); pg.wait_for_timeout(200); pg.evaluate('TengelFx.tap()'); pg.wait_for_timeout(1000)
        cg = pg.evaluate('TengelFx.current()')
        check(cg['kind'] == 'gk' and cg['film'] == 2 and pg.locator('#fxOv .ov.gk.still').count() == 1 and pg.locator('#fxOv .ov.gk.go').count() == 0 and pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.gk .gks')).display") == 'block' and pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.gk .hb')).opacity") == '0',
              f'神様極的中で 動画が 読めない → 動画の さいごの 1まい（still）・ボードは まだ（{cg}）')
        pg.wait_for_timeout(1400)   # 押して 2.4秒（さいごの 1まい → 1.3秒 ボード → 1.6秒 見出し → 1.7秒 帯）
        bhg = pg.evaluate("(() => { const e = document.querySelector('#fxOv .ov.gk .rb .bh'), z = document.querySelector('#fxOv .ov.gk .rb .zrib'); const s = getComputedStyle(e); return { op: s.opacity, vis: s.visibility, t: e.innerText, rib: z ? getComputedStyle(z).opacity : null, ribt: z ? z.innerText.replace(/\\s+/g, '') : null, hb: getComputedStyle(document.querySelector('#fxOv .ov.gk .hb')).opacity, k: getComputedStyle(document.querySelector('#fxOv .ov.gk .gkk')).opacity }; })()")
        check(bhg['op'] == '1' and bhg['vis'] == 'visible' and bhg['hb'] == '1' and bhg['t'] == '神様極的中！！！' and bhg['rib'] == '1' and bhg['ribt'] == '超大穴11大穴8が3連単に！' and bhg['k'] == '1'
              and pg.evaluate("window.__FX.t.GKS") == {'FROM': 11.75, 'WAIT': 1.0} and pg.evaluate("window.__FX.t.GK") == 11.85 and pg.evaluate("window.__FX.t.GKB") == 12.0 and pg.evaluate("window.__FX.art.gk") == ['gk_last.webp']
              and pg.evaluate("window.__FX.films.gk_film") is not None and pg.evaluate("window.__FX.css.includes('fxsdBoard .5s cubic-bezier(.2,.9,.3,1.1) 12s both')"),
              f'神様極的中の still：1.3秒で ボード（うしろは 少し 暗く）・見出し「神様極的中！！！」と 帯（超大穴と 大穴）も いっしょに・音は sfx_gk の 11.75秒から・ボードは 動画の 12秒（{bhg}）')
        pg.evaluate('TengelFx.close()'); pg.wait_for_timeout(100)
        pg.evaluate("TengelFx.set({ calm: true })")
        pg.evaluate("(s) => TengelFx.show(s)", dict(GS, godN=2)); pg.wait_for_timeout(200); pg.evaluate('TengelFx.tap()'); pg.wait_for_timeout(300)
        cgc = pg.evaluate('TengelFx.current()')
        cgc['ndt'] = pg.evaluate("getComputedStyle(document.querySelector('#fxOv .ov.gk .ndt')).display")
        check(cgc['kind'] == 'gk' and cgc['film'] == 2 and pg.locator('#fxOv .fxs.calm .ov.gk.still').count() == 1 and pg.locator('#fxOv video.sgv').count() == 0 and cgc['ndt'] == 'none',
              f'控えめの 神様極的中：押した 画面も 動画も 出さず さいごの 1まい（still）→ 1.3秒 ボード（{cgc}）')
        pg.evaluate('TengelFx.close()'); pg.evaluate("TengelFx.set({ calm: null, effects: false })"); pg.wait_for_timeout(100)
        kq = [pg.evaluate("(s) => TengelFx.show(s)", dict(GS, godN=2))]; pg.wait_for_timeout(300)
        qg = pg.evaluate("(() => ({ push: document.querySelectorAll('#fxOv .push').length, quiet: document.querySelectorAll('#fxOv .fxs .ov.miss.quiet').length, t: document.querySelector('#fxOv .rb.fz .bh').textContent.replace(/\\s+/g, ''), rib: document.querySelector('#fxOv .rb .zrib').textContent.replace(/\\s+/g, '') }))()")   # 第4.118版：textContent（重い ときは 0.3秒で まだ 描かれて いない ことが ある）
        pg.evaluate('TengelFx.close()'); pg.wait_for_timeout(100)
        kq.append(pg.evaluate("(s) => { const k = TengelFx.show(s); TengelFx.close(); return k; }", dict(GS, godN=1)))
        pg.evaluate("TengelFx.set({ effects: true })")
        check(kq == ['gk', 'spg'] and qg == {'push': 0, 'quiet': 1, 't': '神様極的中！！！', 'rib': '超大穴11大穴8が3連単に！'},
              f'的中エフェクト オフ（TengelFx.show を 直接 呼んだ 時）：godN 2以上なら 静かな ボードの 見出しが「神様極的中！！！」（帯は 超大穴と 大穴）・1つ だけなら 超プレミアム神様の ボード（第4.118版）（{kq}・{qg}）')
        pg.evaluate("window.__FX.films = { sgd_film: 'sgd_film.webm', spg_up: 'spg_up.webm', sd_film: 'sd_film.webm', nd_film: 'nd_film.webm' }")
        # プレミアムど的中・紫電（CSS と SVG）：押したあとの 部品と ボード（第4.86版：超プレミアムど的中・神様的中は なし）
        check(sorted(pg.evaluate("Object.keys(window.__FX.reveal)")) == ['big', 'gk', 'hit', 'hit_t', 'miss', 'nd', 'pc', 'sd', 'sgd', 'spg'] and pg.evaluate("window.__FX.art.gd") is None and pg.evaluate("window.__FX.sfx.gd") is None
              and pg.evaluate("window.__FX.sfx.zp") == 'sfx_zp.m4a' and 'gd' not in pg.evaluate("Object.keys(window.__FX.board.titles)") and 'hidden' not in pg.evaluate("Object.keys(window.__FX.board.titles)"),
              '第4.86版：隠れど的中・超プレミアムど的中・神様的中の 押したあと・神様の 絵と 音・見出しは 入って いない（超プレミアムの 音は 超プレミアム神様の はじめに 使う）')
        for kind, cls, parts, title, ribs in (('pc', 'pm', ('.pmbg', '.pmp', '.pms', '.pmf', '.pmw'), 'ど的中！！！', '11番人気が3連単に！'),
                                              ('sd', 'sd', ('.sds', '.sdk', '.pc'), 'ど的中！！！', '11番人気が3連単に！')):
            pg.evaluate("(s) => TengelFx.show(Object.assign({ force: '%s' }, s))" % kind, spec([11, 6, 2], [('馬単', '的中', [[11, 6]])])); pg.wait_for_timeout(200)
            po = pg.locator('#fxOv')
            okp = (po.locator('.ov.fz .pbox.rbw .push .rbf').count() == (0 if kind == 'sd' else 1)) and f'k-{kind}' in po.get_attribute('class') and (kind != 'sd' or pg.evaluate('TengelFx.current()')['pz'] == 1.4)   # 紫電の PUSH は ど的中と 同じ（1.4倍・虹色なし）
            pg.evaluate('TengelFx.tap()'); pg.wait_for_timeout(400)
            if kind == 'sd':   # 第4.77版：極ど的中は ノーマルど的中の 入り（ここでは 動画の 名前が ない → すぐ 極ど的中）のあと
                pg.wait_for_function("() => !!document.querySelector('#fxOv .ov.sd')", timeout=8000)
            have = {p_: po.locator(f'.ov.{cls} {p_}').count() for p_ in parts}
            imgs_bad = pg.evaluate("[...document.querySelectorAll('#fxOv img')].filter(i => i.complete && i.naturalWidth === 0 && !/sgd_last|pm_|gd_|sd_/.test(i.src)).length")
            check(okp and po.locator(f'.fxs .ov.fz.{cls}').count() == 1 and all(have.values()) and po.locator('.rb.fz .bh').text_content() == title and ribs in po.locator('.rb .zrib').text_content() and imgs_bad == 0 and po.locator('.rb .brows li.top .bt').text_content() == '3連単',   # ボードは まだ 見えない（text_content）
                  f'{kind}：PUSH は ど的中と 同じ → 押したあとの 部品（{"・".join(parts)}）→ ボード「{title}」・3連単の 行が いちばん上（{have}）')
            if kind == 'pc':   # 第4.80版：①〜⑤は 1つ 1.0秒・ハートの 地面が できて、ゼリーの ハートが 上から 落ちて 地面に 刺さって 1/3 うまる → ぷるんぷるん・まわりの ハートが おされる／弾ける／こぼれ落ちる／ずれる・背景の ハートは ずっと ぷりんぷりん
                fsrc = pg.evaluate("[...new Set([...document.querySelectorAll('#fxOv .ov.pm .pmf img')].map(i => i.src.split('/').pop()))].sort()")
                fcss = pg.evaluate("window.__FX.css")
                pcm = pg.evaluate("""() => { const q = s => document.querySelector('#fxOv .ov.pm ' + s); const cs = s => getComputedStyle(q(s));
                    return { fj: cs('.pmf .pmfj').animationName, fw: cs('.pmf .pmfw').animationName, fg: cs('.pmf .pmfg').animationName, fs: cs('.pmf .pmfs').animationName,
                             f: cs('.pmf').animationName, fz: cs('.pmf').zIndex, hpz: cs('.pmhp').zIndex, hzz: cs('.pmhz').zIndex, hz: cs('.hb').zIndex, bob: cs('.pmbg .pmj b').animationName,
                             heap: document.querySelectorAll('#fxOv .ov.pm .pmhp > i[class^="pm"]').length, spill: document.querySelectorAll('#fxOv .ov.pm .pmsp > i').length,
                             pop: document.querySelectorAll('#fxOv .ov.pm .pmhp > i[style*="pmHP"]').length, shift: document.querySelectorAll('#fxOv .ov.pm i[style*="pmSh"]').length,
                             cush: document.querySelectorAll('#fxOv .ov.pm .pmhp > i[style*="pmCu"]').length, ring: document.querySelectorAll('#fxOv .ov.pm .pmhp .pmgr').length,
                             shadow: document.querySelectorAll('#fxOv .ov.pm .pmhp .pmfc').length, win: document.querySelectorAll('#fxOv .ov.pm .pmf .pmfw.pmfn').length,
                             push: document.querySelectorAll('#fxOv .ov.pm .pmhp > i[style*="pmPu"]').length,
                             purin: document.querySelectorAll('#fxOv .ov.pm .pmhp > i[style*="--pl:"]').length, wall: document.querySelectorAll('#fxOv .ov.pm .pmbh i[style*="pmBW"]').length,
                             pms: [...document.querySelectorAll('#fxOv .ov.pm .pms')].map(e => getComputedStyle(e).animationDelay.split(',')[0].trim()),
                             pk: (() => { const c = getComputedStyle(q('.pmpk')); return c.animationDelay.split(', ').pop() === '7.6s' && c.animationFillMode.split(', ').pop() === 'forwards'; })() }; }""")
                check(fsrc == ['pm_fin.webp', 'pm_fin_g.webp', 'pm_fin_n.webp', 'pm_fin_s.webp', 'pm_fin_sh.webp', 'pm_fin_w.webp'] and pcm['f'].startswith('fxpmDrop') and 'fxpmUp' in pcm['f']
                      and pcm['fj'].startswith('fxpmFJ') and 'fxpmFI' in pcm['fj'] and pcm['fw'] == 'fxpmFW' and pcm['fg'] == 'fxpmFG' and pcm['fs'] == 'fxpmFS' and pcm['bob'] == 'fxpmPurin'
                      and pcm['fz'] == '7' and pcm['hpz'] == '8' and pcm['hzz'] == '5' and pcm['hz'] == '9' and pcm['heap'] >= 80 and pcm['spill'] >= 10 and pcm['pop'] >= 4 and pcm['shift'] >= 15
                      and pcm['push'] >= 10 and pcm['purin'] >= 60 and pcm['wall'] >= 100 and '@keyframes fxpmPB' in fcss and '@keyframes fxpmBW' in fcss and 'fxpmPB 1.72s linear var(--pl,99s)' in fcss and '@keyframes fxpmPu{0.00%' in fcss and '@keyframes fxpmCu{0.00%' in fcss and pcm['cush'] == 1 and pcm['ring'] == 1 and pcm['shadow'] == 1 and pcm['win'] == 1 and pcm['pms'] == ['3s', '4s', '5s', '6s', '7s'] and pcm['pk']
                      and 'fxpmDrop 1.35s linear 8.15s both' in fcss and 'translateY(-45.43px)' in fcss and 'translateY(56.44px)' in fcss
                      and 'fxpmFJ 2.30s linear 8.15s both' in fcss and 'fxpmUp .5s cubic-bezier(.3,.8,.3,1) 9.95s forwards' in fcss
                      and 'fxpmBeat' not in fcss and pg.evaluate("window.__FX.t.PC") == 9.95 and pg.evaluate("window.__FX.t.ZP") is None,
                      f'プレミアムど的中（第4.80版・第4.86版 テンポ）：①〜⑤は 3・4・5・6・7秒（1つ 1.0秒）・最後の ハートは 6まいの 絵（体・星空・字・つや・小さな ハート・かげ）・8.15秒から 落ちて 8.55秒に 先が ハートの 地面に 着いて 1/3 うまる（下げ −45.43 → 56.44px：前は 8.45秒 → 8.91秒）→ ぷるんぷるん・ボードまで 大きな ハート（2.30秒・9.95秒に 上へ）・地面の ハート（pmPB）・まわりの ハートの 壁（pmBW）が 大きく ぷるんぷるん・地面の ハート（もや 5・大きな ハート 7・地面 8・ボード 9）・前へ おされる・弾ける・こぼれる・ずれる・クッション・光線は 7.6秒から 描かない・背景の ハートは ぷりんぷりん・ボードは 10.3秒（超プレミアムは 10.9秒）（{fsrc}・{pcm}）')
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
        pg.evaluate('TengelFx.close()'); pg.wait_for_timeout(100)
        # 第4.89版：ボタンの 四角が すき通った テーマ（クリスマスの ツリー）の 虹は、四角い .rbf を 重ねず、SVG の 中に 絵の 形で 切りぬいた 虹（.rbwo・mask）
        pg.evaluate("""(async () => { const w = await TengelLocal.getMeta('wallet'); w.events.push({ id: 'unlock-theme:xmas', kind: 'unlock', bucket: '', amount: 0, at: new Date().toISOString(), use: { paid_sub: 0, paid_pack: 0, free: 0 }, what: 'theme:xmas', device: 'x' }); await TengelLocal.putMeta(w); })()""")
        pg.wait_for_timeout(400); pg.evaluate("TengelKisekae.apply('xmas')"); pg.wait_for_timeout(800)
        pg.evaluate("(s) => TengelFx.show(Object.assign({ force: 'pc' }, s))", spec([11, 6, 2])); pg.wait_for_timeout(400)
        rb = pg.evaluate("""() => ({ rbf: document.querySelectorAll('#fxOv .pbox.rbw .push .rbf').length, rbw: document.querySelectorAll('#fxOv .pbox.rbw').length, svg: document.querySelectorAll('#fxOv .pbox.rbw .push svg').length,
          o: document.querySelectorAll('#fxOv .pbox.rbw .push svg .rbwo').length, mask: document.querySelectorAll('#fxOv .pbox.rbw .push svg mask use').length, anim: document.querySelectorAll('#fxOv .pbox.rbw .push svg .rbwo animateTransform').length,
          blend: getComputedStyle(document.querySelector('#fxOv .pbox.rbw .push svg .rbwo')).mixBlendMode, bg: getComputedStyle(document.querySelector('#fxOv .pbox.rbw .push')).backgroundColor })""")
        check(rb['rbw'] == 1 and rb['rbf'] == 0 and rb['svg'] == 2 and rb['o'] == 1 and rb['mask'] == 1 and rb['anim'] == 1 and rb['blend'] == 'color' and rb['bg'] in ('rgba(0, 0, 0, 0)', 'transparent'),
              f'第4.89版：クリスマスの プレミアムの PUSH は 四角い 虹（.rbf）なし・面の 絵（ツリー）だけに 絵の 形の 虹（まわりの 飾りは そのまま）（{rb}）')
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
        zw = pg.locator('#result [data-k=zwaku]')
        check(zw.count() == pg.locator('#result .zone').count() and zw.count() >= 2 and zw.first.locator('[data-t=枠複]').count() == 1 and pg.locator('#result [data-k=zwaku] [data-t=枠単]').count() == 0 and '通り' not in zw.first.inner_text() and '点' not in pg.locator('#result').inner_text(),
              f'第4.122版：枠複を 解放 → 判定の ゾーンごとに 枠と 枠複の 組（解放して いない 枠単は 出ない・通り数／点数は 判定の 画面に 出さない）（{zw.first.inner_text()[:60] if zw.count() else "なし"}）')
        card.locator('[data-rsv=back]').click(); pg.wait_for_timeout(200)
        pg.evaluate("window.__ocrLines = %s" % json.dumps([lines_r(OCR_LINES['a_tanfuku_waku'], 11)], ensure_ascii=False))
        pg.set_input_files('#ocrFile', [os.path.join(OCR_DIR, 'a_tanfuku_waku.jpg')]); pg.wait_for_timeout(1800)
        om = pg.locator('#ocrMsg').inner_text()
        check('ポイントが足りないよ' in om and '200P' in om and pg.locator('#ocrMsg [data-gopt=points]').count() == 1 and pg.locator('#fR').input_value() == '8' and pg.evaluate('TengelWallet.total()') == 100, '100Pでは新しいレースを読めない（入力はそのまま＝8R・「ポイントを買う」）')
        pg.locator('#ocrMsg [data-gopt=points]').click(); pg.wait_for_timeout(600)
        # 第4.84版（まさちゃん「このポイントの欄タップしたら、所持ポイントの確認と、ポイント&サブスクの購入選択画面が出てくるようにして！」）：「ポイントを買う」も 上の帯の 所有ポイントも ポイントの 窓
        po = pg.locator('#ptOv')
        pot = po.inner_text() if po.count() else ''
        check(po.count() == 1 and po.get_attribute('role') == 'dialog' and '合計 100P' in pot and 'ポイントの詳細' in pot and po.locator('#ptDetail h2').inner_text() == 'ポイントの詳細' and pg.evaluate("[...document.querySelectorAll('#ptOv #ptDetail .ptbk > div > span')].map(x => x.firstChild.textContent)") == ['購入ポイント', 'サブスクポイント', '獲得ポイント'] and 'ポイントは 合計 99,999P まで もてるよ' in pot and 'ポイントを買う' in pot and 'サブスク（毎月とどく）' in pot and po.locator('#ptBuy [data-pt=buy]').count() == 4 and po.locator('#ptSub [data-pt=buy]').count() == 3 and po.locator('[data-pt=buy][data-id="jp.tengel.app.points1000"]').count() == 1,
              f'「ポイントを買う」→ ポイントの窓（第4.139版：いちばん 上に「ポイントの詳細」＝合計 100P と 購入ポイント・サブスクポイント・獲得ポイントの 3つ・上限の 行 ／ パック 4つ・サブスク 3つ）')
        # 買う（App内課金のかわり）：1,000P → 届く → finish（窓の 中で）
        pg.evaluate("window.__txn = 500; window.__iap.buy['jp.tengel.app.points1000'] = () => ({ ok: true, state: 'ok', tx: { id: String(++window.__txn), originalId: 'o1', product: 'jp.tengel.app.points1000', kind: 'pack', date: new Date().toISOString(), revoked: false } }); 0")
        pg.evaluate("window.__bridge = []")
        po.locator('[data-pt=buy][data-id="jp.tengel.app.points1000"]').click(); pg.wait_for_timeout(700)
        fin = [x for x in pg.evaluate('window.__bridge') if x['name'] == 'iap' and x['payload']['op'] == 'finish']
        check(pg.evaluate('TengelWallet.total()') == 1100 and len(fin) == 1 and fin[0]['payload']['id'] == '501' and pg.evaluate("[...document.querySelectorAll('#ptOv .ptbk b')].map(x => x.innerText)") == ['1,000P', '0P', '100P'] and '合計 1,100P' in po.inner_text() and pg.locator('#ptsPill').inner_text().replace('\n', ' ') == 'ポイント 1,100P', '窓で 1,000Pのパックを買う → 1,100P（窓の 内わけ＝購入ポイント 1,000・獲得ポイント 100 と 上の帯の 合計も かわる）・台帳に書いてから取引を終わらせる（finish）')
        po.locator('[data-pt=buy][data-id="jp.tengel.app.points1000"]').click(); pg.wait_for_timeout(700)
        check(pg.evaluate('TengelWallet.total()') == 2100, 'もう一度買う（別の取引）→ 2,100P')
        pg.evaluate("window.__iap.buy['jp.tengel.app.points500'] = () => ({ ok: false, state: 'cancelled' }); 0")
        po.locator('[data-pt=buy][data-id="jp.tengel.app.points500"]').click(); pg.wait_for_timeout(500)
        check(pg.evaluate('TengelWallet.total()') == 2100, 'やめたら何も変わらない')
        po.locator('[data-ms=close]').click(); pg.wait_for_timeout(300)
        check(pg.locator('#ptOv').count() == 0 and not pg.evaluate("document.documentElement.classList.contains('mson')"), 'ポイントの窓を とじる')
        pg.click('#ptsPill'); pg.wait_for_timeout(500)
        pd = pg.evaluate("() => { const o = document.querySelector('#ptOv'), d = o && o.querySelector('#ptDetail'), b = o && o.querySelector('.msb'); if (!d) return null; const r = d.getBoundingClientRect(), h = o.querySelector('.msh').getBoundingClientRect(); return { top: Math.round(r.top - h.bottom), first: b.firstElementChild === d, st: b.scrollTop, big: d.querySelector('.ptbig').innerText.replace(/\\s+/g, ''), rows: [...d.querySelectorAll('.ptbk > div')].map(x => x.innerText.replace(/\\s+/g, ' ')) }; }")
        check(pg.locator('#ptOv').count() == 1 and '合計 2,100P' in pg.locator('#ptOv').inner_text() and bool(pd) and pd['first'] and pd['st'] == 0 and 0 <= pd['top'] <= 40 and pd['big'] == '2,100P'
              and pd['rows'] == ['購入ポイント パック・期限なし 2,000P', 'サブスクポイント 届いた日から30日 0P', '獲得ポイント はじめてのプレゼント・ミッション 100P'],
              f'上の帯の 所有ポイントを 押すと ポイントの窓（いま 2,100P）。第4.139版（まさちゃん 11/10 11:46「ポイント欄を押すと、ポイントの詳細がわかる欄を作ってそこに飛ぶようにして！」）：開くと いちばん 上が「ポイントの詳細」（購入ポイント 2,000P・サブスクポイント 0P・獲得ポイント 100P）（{pd}）')
        pg.locator('#ptOv [data-ms=hist]').click(); pg.wait_for_timeout(600)
        check(pg.locator('#ptOv').count() == 0 and pg.locator('#v-set').is_visible() and pg.locator('#setPoints [data-pt=restore]').count() == 1, '窓の「ポイントの履歴・購入を復元」→ 設定タブのポイント（詳しく）')
        pg.click('.tabbar button[data-tab=judge]'); pg.wait_for_timeout(300)
        # 上の帯の マザーデータの 札 → 設定タブの マザーデータ（まさちゃん「マザーデータをタップしたら設定のマザーデータのところに飛ぶようにして！」）
        pg.click('#dbpill'); pg.wait_for_timeout(600)
        mo = pg.evaluate("() => { const m = document.querySelector('#setMother'), r = m.getBoundingClientRect(); return { set: !document.querySelector('#v-set').hidden, top: Math.round(r.top), gopt: document.querySelector('#dbpill').dataset.gopt, role: document.querySelector('#dbpill').getAttribute('role') }; }")
        check(mo['set'] and mo['gopt'] == 'mother' and mo['role'] == 'button' and -40 <= mo['top'] <= 200, f'上の帯の マザーデータの札を 押すと 設定タブの マザーデータへ（{mo}）')
        pg.click('.tabbar button[data-tab=judge]'); pg.wait_for_timeout(300)
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
        check(pg.evaluate("[...document.querySelectorAll('#setPoints .ptbk b')].map(x => x.innerText)") == ['2,000P', '4,400P', '100P'] and 'サブスクポイント：4,400P は' in pt and 'まで' in pt and pg.locator('#ptsPill').inner_text().replace('\n', ' ') == 'ポイント 6,500P', f'ポイントのカード：内わけ（購入ポイント 2,000・サブスクポイント 4,400・獲得ポイント 100）と サブスクの期限・上の帯は 合計「ポイント 6,500P」（{pt[:120]}…）')
        pg.locator('#setPoints [data-pt=show][data-v=hist]').click(); pg.wait_for_timeout(300)
        hist = pg.locator('#setPoints .pthist').inner_text()
        check('初回プレゼント' in hist and '+1,000P' in hist and '-400P' in hist and '解放' in hist and '月4,400Pプラン' in hist and pg.locator('#setPoints [data-pt=restore]').count() == 1, 'くわしく：履歴（プレゼント・買った・使った・解放・サブスク）と「購入を復元」')
        # ミッション：8レース数えた状態にして受け取る（数え方は test_points.js。ここは画面）
        pg.evaluate("""(async () => { const w = await TengelLocal.getMeta('wallet'); for (let i = 1; i <= 8; i++) w.counted['2026-10-0' + i + '||1'] = new Date().toISOString(); await TengelLocal.putMeta(w); })()""")
        pg.reload(); pg.wait_for_timeout(800); gate(pg); pg.wait_for_timeout(1200)
        check(pg.locator('.tabbar [data-tab=set] .tbdg').count() == 1, '受け取れるミッションがあると設定タブに印')
        # 第4.82版：上の帯の「ミッション」（説明書の 左・つぎまでの 数・受け取れる 数の 赤い 印）→ 押すと ミッションの 窓（ポイント・壁紙・見直し基準）→ そこで 受け取る
        mb = pg.evaluate("() => { const b = document.querySelector('#msBtn'); if (!b) return null; const R = s => document.querySelector(s).getBoundingClientRect(); const r = R('#msBtn'), m = R('#manBtn'), pt = R('#ptsPill'), br = R('.brand'), db = R('#dbpill'); const bd = b.querySelector('.mbd'); return { t: b.innerText.replace(/\\s+/g, ' '), title: b.title, hot: b.classList.contains('hot'), bd: (bd || {}).innerText, bdc: bd && getComputedStyle(bd).color, bdbg: bd && getComputedStyle(bd).backgroundColor, bdsvg: !!(bd && bd.querySelector('svg')), row1: Math.abs(m.y - pt.y) < 8 && Math.abs(pt.y - br.y) < 8 && pt.left > br.right && m.left > pt.right && m.right <= innerWidth - 8, row2: r.y > m.bottom && r.right > innerWidth / 2, row3: db.y > r.bottom, inTop: !!b.closest('header.top'), hdr: Math.round(R('header.top').height) }; }")
        # 第4.139版（まさちゃん 11/10 11:59「上のミッションの◯/◯のところは合計ミッション分にして、追加がある場合は、追加していけるようにして！」）：
        #   ◯/◯＝達成した 数／ミッションの 合計（前は 記録の 数／つぎの 記録ミッションの 数「10/15」）。合計は 表から 数える（記録 12・帯 3・壁紙の 枚数 10・結果ボード 5・トレーニングセンター 4・思い出フィギュア 3＝37）
        mall = pg.evaluate("() => { const P = TengelPoints; return P.MISSIONS.length + P.WALL_MISSIONS.length + P.WALLP_MISSIONS.length + P.BOARD_MISSIONS.length + P.TC_MISSIONS.length + P.FIG_MISSIONS.length; }")
        check(mall == 37 and bool(mb) and mb['t'] == f'ミッション 1/{mall} 1' and mb['hot'] and mb['bd'] == '1' and mb['bdc'] == 'rgb(31, 58, 14)' and mb['bdbg'] == 'rgb(212, 245, 166)' and mb['bdsvg'] and mb['row1'] and mb['row2'] and mb['row3'] and mb['inTop'] and mb['hdr'] <= 150
              and '達成 1／ぜんぶで 37' in mb['title'],
              f'上の帯：ロゴ・所有ポイント・説明書が 1段目 ／ 2段目の 右に「ミッション」（達成 1／合計 {mall}・受け取れる 1 は うすい 黄緑の 四角に ふきだしの 絵と 数）／ 3段目の 右に マザーデータの札（{mb}）')
        rb = pg.evaluate("() => { const b = document.querySelector('#rsvBtn'), m = document.querySelector('#msBtn'); if (!b || !m) return null; const r = b.getBoundingClientRect(), q = m.getBoundingClientRect(); return { t: b.innerText.replace(/\\s+/g, ''), n: [...TengelLocal.mem.bets.values()].filter(x => x.rsv && x.rsv.state === 'reserved').length, has: b.classList.contains('has'), row: Math.abs(r.top - q.top) < 6 && r.right <= q.left + 1 && r.left >= 8, next: (b.nextElementSibling || {}).id }; }")
        check(bool(rb) and rb['n'] >= 1 and rb['t'] == f'結果待ち{rb["n"]}' and rb['has'] and rb['row'] and rb['next'] == 'msBtn', f'第4.122版：2段目の「ミッション」の 左に「結果待ち」と 予約済み・結果待ちの レースの 数（{rb}）')
        pg.click('#msBtn'); pg.wait_for_timeout(500)
        ov = pg.locator('#msOv')
        ovt = ov.inner_text() if ov.count() else ''
        check(ov.count() == 1 and ov.get_attribute('role') == 'dialog' and '受け取れるのが 1つ' in ovt and ov.locator('.msn').inner_text().replace('\n', '・') == '達成 1/37・受け取れるのが 1つ！' and 'ポイントミッション' in ovt and '壁紙ミッション' in ovt and '見直し基準の進み具合' in ovt and ov.locator('#msRev .pi').count() == 0 and 'マザーデータ①〜③のレースで進む' in ov.locator('#msRev').inner_text() and 'いま 10レース' in ovt and ov.locator('#msPts [data-pt=claim]').count() == 1 and ov.locator('#msWall .msrow').count() == 3 and pg.evaluate("document.documentElement.classList.contains('mson')"),
              '「ミッション」を押すと ミッションの窓：ポイントミッション（受け取る 1つ）・壁紙ミッション（3つ）・見直し基準の進み具合（テンゲルデータの ときは 数を 出さずに「マザーデータ①〜③のレースで進む」：第4.123版）')
        ov.locator('#msPts [data-pt=claim]').click(); pg.wait_for_timeout(700)
        mb2 = pg.evaluate("() => { const b = document.querySelector('#msBtn'); return { t: b.innerText.replace(/\\s+/g, ' '), hot: b.classList.contains('hot') }; }")
        check(pg.evaluate('TengelWallet.total()') == 7000 and pg.evaluate("TengelWallet.balance().free") == 600 and ov.locator('[data-pt=claim]').count() == 0 and '受け取りずみ' in ov.inner_text() and pg.locator('.tabbar [data-tab=set] .tbdg').count() == 0 and mb2['t'] == 'ミッション 1/37' and not mb2['hot'] and ov.locator('.msn').inner_text().strip() == '達成 1/37',
              f'窓で「受け取る」→ 500P（獲得ポイント）・窓の行は受け取りずみ・上の「ミッション」の 印と設定タブの印が消える（達成の 数 1/37 は そのまま）（{mb2}）')
        pg.screenshot(path=os.path.join(W, 't4', 'native_mission_ov.png'), full_page=False)
        ov.locator('[data-ms=close]').click(); pg.wait_for_timeout(300)
        check(pg.locator('#msOv').count() == 0 and not pg.evaluate("document.documentElement.classList.contains('mson')") and pg.evaluate("document.activeElement && document.activeElement.id") == 'msBtn', '「とじる」で窓が閉じる（「ミッション」にもどる）')
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(400)
        ms = pg.locator('#setMission')
        check('いま 10レース' in ms.inner_text() and ms.locator('[data-pt=claim]').count() == 0 and '次は 15レース' in ms.inner_text() and '画面の上の' in ms.inner_text(), '設定タブのミッションも 受け取りずみ・次は15レース（上の「ミッション」の案内つき）')
        pg.screenshot(path=os.path.join(W, 't4', 'native_mission.png'), full_page=False)
        pg.click('.tabbar button[data-tab=judge]'); pg.wait_for_timeout(300)
        # ---- 着せ替え（第4弾・9章・16.1・16.1.1・16.2.1・16.4）：設定の「着せ替え」・30テーマ・名前と値段（9.1）・解放（P）→ 着せ替わる・上の絵（動く壁紙）・テーマの的中PUSHとボード・帯のミッション（8.3） ----
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(400)
        ks = pg.locator('#setKisekae')
        NPK = pg.evaluate("TengelKisekae.pack().ids.length")                # 第4.92版：壁紙パックの テーマ（いちばん 上の 組・買う まで カギ）
        check(ks.count() == 1 and ks.locator('.kst').count() == 30 + NPK and ks.locator('.ksg').count() == 7 and ks.locator('.kst.on').get_attribute('data-ks') == 'default' and ks.locator('.kst.lock').count() == 29 + NPK and pg.evaluate("TengelKisekae.current()") == 'default' and pg.evaluate("document.documentElement.dataset.ks") is None,
              f'設定に「着せ替え」：7つの組（壁紙パック＋6）・{30 + NPK}テーマ・いつものが使用中・ほかの{29 + NPK}はカギ')
        names = ks.locator('.kst .ksn').all_inner_texts()
        PKN = ['海賊', '競馬場', '宇宙', 'パドック', '深海', '恐竜時代', '切り絵', '浮世絵風', 'スチームパンク', '近未来都市', '七夕']
        check(names[:NPK] == [n for n, t in zip(PKN, ['pirate', 'course', 'space', 'paddock', 'deepsea', 'dino', 'kirie', 'ukiyoe', 'steam', 'future', 'tanabata']) if t in pg.evaluate("TengelKisekae.pack().ids")], f'壁紙パックの 名前と 並び（{names[:NPK]}）')
        names = names[NPK:]
        check(names[:5] == ['いつもの', '牧場', 'かわいいお馬さん', '毛糸のお馬とロボット', 'ぷりけつのお馬'] and names[5:16] == ['桜', '海', '夕焼け', '紅葉', '雪', 'お正月', '花火', 'クリスマス', 'ハロウィン', 'バレンタイン', 'ホワイトデー']
              and names[16:20] == ['ナイター', '競馬新聞', '勝負服', '招き馬'] and names[20:22] == ['水墨画', '大理石の馬'] and names[22:27] == ['ネオン', 'ドット', '黒板', 'メリーゴーランド', '星座'] and names[27:] == ['シルバー帯', 'ゴールド帯', 'マスター帯'],
              f'9.1 の名前と並び（定番5・季節・行事11・競馬4・和・アート2・レトロ・ポップ5・帯3）：{names[:6]}…')
        locks = ks.locator('.kst .kslock').all_inner_texts()
        check(locks.count('🔒 1,000P') == 5 and locks.count('🔒 2,000P') == 6 and locks.count('🔒 3,000P') == 4 and locks.count('🔒 4,000P') == 8 and locks.count('🔒 7,000P') == 3 and locks.count('🔒 壁紙を8枚あつめると') == 1 and locks.count('🔒 壁紙を16枚あつめると') == 1 and locks.count('🔒 壁紙を25枚あつめると') == 1 and locks.count('🔒 壁紙パック') == NPK,
              '値段（9.1）：1,000P×5・2,000P×6・3,000P×4・4,000P×8・7,000P×3・帯は 8・16・25枚・壁紙パック（買い切り）')
        check(ks.locator('.kst[data-ks=sakura] .ksth').get_attribute('src') == 'ks_cbcbaeebec4470155b1587d5a5c8fe00.webp' and ks.locator('.kst[data-ks=ranch] .ksth').get_attribute('src') == 'ks_banner_ranch.svg' and ks.locator('.kst[data-ks=default] .ksth').get_attribute('src') == 'ks_c1fccd55173e28903228b7256479cc32.webp',
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
        # 第4.89版：選ぶ画面の 壁紙は ふだん 止まった 絵。タップして 選んだ タイル（解放前＝確認を 開いた タイル）だけ、判定タブと 同じ 動く 壁紙を 小さく 重ねて 動かす
        pg.wait_for_timeout(900)
        lv = pg.evaluate("""() => { const t = document.querySelector('#setKisekae .kst.lv'); const el = t && t.querySelector('.kslv');
          const run = el ? el.getAnimations({ subtree: true }).filter(a => a.playState === 'running').length : -1;
          const others = [...document.querySelectorAll('#setKisekae .kst:not(.lv)')].reduce((n, e) => n + e.getAnimations({ subtree: true }).length, 0);
          const st = document.querySelector('#ksPrev'); const css = st ? st.textContent : '';
          return { id: t ? t.dataset.ks : null, n: document.querySelectorAll('#setKisekae .kst.lv').length, run: run, others: others, scoped: css.indexOf('#setKisekae .kslv') >= 0 && css.indexOf('#ksBnr') < 0, kp: /@keyframes kpkb/.test(css),
            kss: el ? parseFloat(getComputedStyle(el).getPropertyValue('--kss')) : 0, img: !!document.querySelector('#setKisekae .kst.lv .ksth') }; }""")
        check(lv['id'] == 'lucky' and lv['n'] == 1 and lv['run'] > 0 and lv['others'] == 0 and lv['scoped'] and lv['kp'] and 0.3 < lv['kss'] < 1 and lv['img'],
              f'第4.89版：確認を 開いた カギの タイル（招き馬）だけ 動く 壁紙が 重なる（ほかの タイルは 止まった 絵・CSS は #setKisekae .kslv に・@keyframes は kp…）（{lv}）')
        ks.locator('.kst[data-ks=lucky]').click(position={'x': 10, 'y': 10}); pg.wait_for_timeout(200)
        check(ks.locator('.ksconf').count() == 0 and ks.locator('.kst.cf').count() == 0 and ks.locator('.kst.lv').count() == 0 and pg.evaluate("document.querySelector('#ksPrev').textContent") == '',
              'もう一度 タイルを タップ → 閉じる（動く 壁紙も 消える：いつもの は 動く 絵が ないので どの タイルも 止まった まま）')
        ks.locator('.kst[data-ks=lucky]').click(); pg.wait_for_timeout(300)
        ks.locator('.ksconf [data-ksact=cancel]').click(); pg.wait_for_timeout(200)
        check(ks.locator('.ksconf').count() == 0 and pg.evaluate('TengelWallet.total()') == 7000 and pg.evaluate("TengelKisekae.current()") == 'default', 'やめると何も変わらない')
        # 桜（1,000P）を解放 → 着せ替わる
        ks.locator('.kst[data-ks=sakura]').click(); pg.wait_for_timeout(300)
        ks.locator('.ksconf [data-ksact=unlock]').click(); pg.wait_for_timeout(1200)
        check(pg.evaluate('TengelWallet.total()') == 6000 and pg.evaluate("TengelWallet.unlocked('theme:sakura')") and pg.evaluate("document.documentElement.dataset.ks") == 'sakura' and pg.evaluate("TengelKisekae.current()") == 'sakura' and pg.evaluate("TengelKisekae.loaded()")
              and ks.locator('.kst.on').get_attribute('data-ks') == 'sakura' and ks.locator('.kst[data-ks=sakura] .kslock').count() == 0 and ks.locator('.kst[data-ks=sakura] .ksbadge').inner_text() == '使用中' and '壁紙：1/37枚' in ks.inner_text() and pg.evaluate("localStorage.getItem('tengel.kisekae')") == 'sakura',
              f'解放する → 1,000P 使って 桜に着せ替わる（台帳 unlock-theme:sakura・使用中・1/37枚（ポイントの 26枚＋壁紙パックの 11枚）・端末に覚える）')
        check(pg.evaluate("getComputedStyle(document.body).backgroundColor") == 'rgb(255, 246, 248)' and 'Zen Kaku Gothic New' in pg.evaluate("getComputedStyle(document.body).fontFamily") and 'Kaisei Decol' in pg.evaluate("getComputedStyle(document.querySelector('.brand h1')).fontFamily")
              and pg.evaluate("getComputedStyle(document.querySelector('.top')).borderBottomColor") == 'rgb(238, 157, 184)' and pg.evaluate("getComputedStyle(document.querySelector('.tabbar button[aria-selected=true]')).backgroundColor") == 'rgb(252, 227, 235)',
              '桜の色と字：背景・本文（Zen Kaku Gothic New）・見出し（Kaisei Decol）・上の帯のふち・タブ')
        pg.wait_for_timeout(900)
        lv = pg.evaluate("""() => { const t = document.querySelector('#setKisekae .kst.lv'); const el = t && t.querySelector('.kslv');
          return { id: t ? t.dataset.ks : null, on: !!(t && t.classList.contains('on')), run: el ? el.getAnimations({ subtree: true }).filter(a => a.playState === 'running').length : -1,
            others: [...document.querySelectorAll('#setKisekae .kst:not(.lv)')].reduce((n, e) => n + e.getAnimations({ subtree: true }).length, 0), ranch: document.querySelector('#setKisekae .kst[data-ks=ranch] .ksth').getAttribute('src') }; }""")
        check(lv['id'] == 'sakura' and lv['on'] and lv['run'] > 0 and lv['others'] == 0 and lv['ranch'] == 'ks_banner_ranch.svg',
              f'第4.89版：解放して 使用中に なった 桜の タイルだけ 動く（ほかは 止まった 絵）（{lv}）')
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
        check(bn.count() == 1 and not bn.evaluate('e => e.hidden') and bn.locator('.bnrw').count() == 1 and bn.locator('img.bnr').get_attribute('src') == 'ks_cbcbaeebec4470155b1587d5a5c8fe00.webp' and abs(bb['height'] - 160) < 1 and abs(bb['width'] - 390) < 1
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
        check(pg.evaluate("() => { const b = document.querySelector('#msBtn'); return b.classList.contains('hot') && b.querySelector('.mbd').innerText === '3'; }") and wm.locator('[data-pt=claim][data-id="mission-wallp-3"]').count() == 1 and wm.locator('[data-pt=claim][data-id="mission-wallp-6"]').count() == 1 and wm.locator('[data-pt=claim][data-id="mission-wallp-9"]').count() == 0,
              '上の「ミッション」にも 受け取れる 3 の印（シルバー帯・第4.114版の 壁紙 3枚と 6枚）')
        wm.locator('[data-pt=claim][data-id="mission-wall-8"]').click(); pg.wait_for_timeout(700)
        check(pg.evaluate("TengelWallet.unlocked('theme:silver')") and pg.evaluate("TengelKisekae.usable('silver')") and pg.evaluate("TengelKisekae.count()") == 8 and pg.evaluate('TengelWallet.total()') == 6000 and wm.locator('[data-pt=claim]').count() == 3 and wm.locator('[data-pt=claim][data-id="mission-wall-16"]').count() == 0 and 'シルバー帯の壁紙を受け取ったよ' in pg.locator('#toast').inner_text(),
              '受け取る → シルバー帯が使える（0P・枚数は8のまま・残りは 第4.114版の 枚数の ミッション 3つ（帯の 1枚で 9枚に））')
        # 第4.114版：壁紙の 枚数の ミッション（帯も 数える：8 ＋ シルバー 1 ＝ 9枚 → 3・6・9 が 受け取れる）
        check(wm.locator('[data-pt=claim][data-id="mission-wallp-9"]').count() == 1 and 'いま 9枚' in wm.inner_text(), '帯の 1枚も 枚数に 数える → 9枚で「壁紙 9枚解放」も 受け取れる')
        for mid, add in (('mission-wallp-3', 800), ('mission-wallp-6', 1200), ('mission-wallp-9', 1500)):
            t0 = pg.evaluate('TengelWallet.total()'); f0 = pg.evaluate('TengelWallet.balance().free')
            wm.locator(f'[data-pt=claim][data-id="{mid}"]').click(); pg.wait_for_timeout(700)
            check(pg.evaluate('TengelWallet.total()') == t0 + add and pg.evaluate('TengelWallet.balance().free') == f0 + add and f'{add:,}P' in pg.locator('#toast').inner_text() and wm.locator(f'.msrow[data-mid="{mid}"] .md').inner_text() == '受け取りずみ',
                  f'第4.114版：「{mid}」を 受け取る → +{add:,}P（もらったP）・受け取りずみ')
        check(wm.locator('[data-pt=claim]').count() == 0 and pg.locator('.tabbar [data-tab=set] .tbdg').count() == 0 and pg.evaluate('TengelWallet.total()') == 9500, '受け取れる ものが なくなると 印が 消える（合計 9,500P）')
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
        check(pg.locator('#nativeRestore').count() == 0 and pg.evaluate('TengelLocal.mem.bets.size') == 3 and '記録3件を戻したよ' in pg.locator('#toast').inner_text() and 'ポイント（9,500P）も戻したよ' in pg.locator('#toast').inner_text() and pg.evaluate('TengelWallet.total()') == 9500, '「記録を戻す」→ 記録とポイントの台帳が戻る（着せ替えで 1,000P 使って、第4.114版の 枚数の ミッションで 3,500P もらった あと）')
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
        check(p2.evaluate("(() => { const n = document.querySelector('#ocrNote'); return !n || n.hidden; })()") and p2.evaluate("(() => { const t = document.body.innerText || ''; return !t.includes('締切済み') && !document.querySelector('#recList .rsvtop details[data-k=closed]'); })()"), 'Web版：締切済みレースの ※の 注意は 出ない・締切済みの 判定も しない（第4.116版）')
        check(p2.locator('#setNotify').count() == 0 and p2.evaluate("typeof window.TengelReserve === 'undefined' && typeof window.TengelCustomRate === 'undefined'"), 'Web版：お知らせの設定・予約の仕組みは入らない')
        check(p2.locator('#setFx').count() == 0 and p2.evaluate("typeof window.TengelFx === 'undefined' && typeof window.__FX === 'undefined' && !document.querySelector('#fxCss')"), 'Web版：的中ボタン（演出・設定）は入らない')
        check(p2.locator('#ptsPill').count() == 0 and p2.locator('#testTag').count() == 0 and p2.locator('#ptsCss').count() == 0 and p2.locator('#rsvBtn').count() == 0 and p2.locator('[data-k=rself], [data-k=zwaku]').count() == 0 and p2.evaluate("getComputedStyle(document.querySelector('#dbpill')).marginLeft") != '0px', 'Web版：上の帯の 所有ポイント・説明書の 置き場は かわらない（第4.122版の「結果待ち」・自己入力・枠も ない）')
        check(p2.locator('#setKisekae').count() == 0 and p2.locator('#ksBnr').count() == 0 and p2.evaluate("typeof window.TengelKisekae === 'undefined' && typeof window.__KS === 'undefined' && !document.querySelector('#ksCss') && !document.documentElement.dataset.ks"), 'Web版：着せ替え（カード・上の絵・テーマの CSS）は入らない')
        check(p2.locator('#rFilters [data-f=mem]').count() == 1 and p2.evaluate("document.querySelector('#rFilters [data-f=mem]').hidden") is True and p2.evaluate("typeof memTopHTML === 'function' ? memTopHTML() : ''") == '' and p2.locator('#recList .memtop').count() == 0,
              'Web版：思い出記録は 入らない（絞り込みの「思い出」は かくす・思い出の 欄は 出ない）')
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
        check(p4.locator('#ptOv').count() == 1 and p4.locator('#ptOv #ptBuy [data-pt=buy]').count() == 4, '所有ポイントを 押すと ポイントの窓（第4.84版：iPad でも）')
        p4.evaluate("TengelWallet.closePoints()"); p4.wait_for_timeout(200)
        ctx4.close()
        # ---- 第4.91版：結果ボードカスタム（買い切り 2,200円・非消耗型）：設定の カード → ためす（▶ 見る）→ 買う → 読み込みで 番号の 順に 解放 → 選ぶ → 結果の ボードに つく ----
        #   第4.113版（まさちゃんの 指定）：16こ（1〜15 は じゅんび中・16「ボードを持つ馬」）・6レースごとに 1つ・的中の とき／ハズレの とき を べつべつに 選ぶ
        #   第4.120版（まさちゃんの 指定 2026/11/04）：15こ（1〜14 は じゅんび中・15「ボードを持つ馬」・全部で 90レース）
        #   出る ときの きまり（的中の 所＝ハズレ いがいの 結果 ぜんぶ・ハズレの 所＝ハズレ）・控えめは 止まった 形・「とじる」は 動かない・前の 版の 台帳（1つの 選択）・返金で 使えなくなる・購入を復元
        m6 = {}
        def marker6(source, q):
            op, key = q.get('op'), q.get('key')
            if op == 'set': m6[key] = q.get('value', '1'); return {'ok': True}
            if op == 'del': m6.pop(key, None); return {'ok': True}
            v = m6.get(key); return {'ok': True, 'has': v is not None, 'value': v}
        ctx6 = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP'); ctx6.add_init_script(FAKE)
        ctx6.expose_binding('__saveBackup', lambda s, t: None); ctx6.expose_binding('__marker', marker6)
        p6 = ctx6.new_page(); p6.on('pageerror', lambda e: errs.append('BOARD ' + str(e)))

        def reopen6():   # 台帳を 書きかえた あと 開き直す（タブの 帯が 出るまで 待つ。出なければ もう一度）
            for _ in range(3):
                p6.goto(APPURL); p6.wait_for_timeout(800); gate(p6)
                try:
                    p6.wait_for_selector('.tabbar button[data-tab=set]', timeout=15000); p6.wait_for_timeout(1000); return
                except Exception as e:
                    print('   （開き直し もう一度：', p6.evaluate("() => document.title + ' ' + location.href"), str(e)[:80], '）')
        p6.goto(APPURL); p6.wait_for_timeout(1500); gate(p6); p6.wait_for_timeout(700)
        p6.click('.tabbar button[data-tab=set]'); p6.wait_for_timeout(500)
        BCI = """() => { const c = document.querySelector('#setBoard'); if (!c) return null; return { after: c.previousElementSibling && c.previousElementSibling.id, tiles: c.querySelectorAll('.bct').length, locks: c.querySelectorAll('.bct .bclk').length,
          prep: c.querySelectorAll('.bct.prep').length, buy: (c.querySelector('[data-bcact=buy]') || {}).innerText || '', bun: (c.querySelector('[data-bcact=bundle]') || {}).innerText || '', restore: !!c.querySelector('[data-bcact=restore]'), see: c.querySelectorAll('[data-bcact=see]').length, fit: c.querySelectorAll('.bcmi.fit').length,
          on: [...c.querySelectorAll('.bct.on')].map(e => e.dataset.bc), prog: (c.querySelector('.bcprog') || {}).innerText || '', news: c.querySelectorAll('.bcnew').length,
          slots: [...c.querySelectorAll('.bcslot')].map(e => e.dataset.slot + ':' + e.querySelector('.bcsn').innerText), picks: [...c.querySelectorAll('[data-bcact=use]')].map(e => e.dataset.id + ':' + e.dataset.slot + ':' + e.getAttribute('aria-pressed')),
          names: [...c.querySelectorAll('.bct .bcn')].map(x => x.innerText.replace(/^\\d+/, '').replace('NEW', '').trim()), pics: c.querySelectorAll('.bcmini.pic').length, bad: c.querySelectorAll('.bcmini.pic.bad').length,
          thumbs: [...c.querySelectorAll('.bcmini.pic img')].filter(i => i.complete && i.naturalWidth > 0).length,
          secs: [...c.querySelectorAll('.bcsec')].map(x => x.dataset.sec + ':' + x.querySelectorAll('.bct').length + ':' + ((x.querySelector('.bck') || {}).innerText || '')) }; }"""
        BSEL = "(() => { const i = TengelWallet.board.info(); return [i.selHit, i.selMiss, i.n, TengelWallet.board.active('hit'), TengelWallet.board.active('miss')]; })()"
        SEE6 = "() => { const hb = document.querySelector('#fxOv .hb'), c = TengelFx.current(); return hb && c && { bcx: hb.dataset.bcx || '', kind: c.kind, phase: c.phase }; }"
        PIC_NAMES6 = ['結果ボードを廻る', '馬達の祝杯', '馬レース結果ボード', '自撮り結果ボード', 'スタンプ結果ボード', 'トロフィー結果ボード', '馬が運ぶ結果ボード', '花束結果ボード', '出世馬結果ボード',
                      '二人でしょんぼり', '次…！', '隠蔽作戦', 'ボード結果待ち', '書き換え参戦']
        p6.wait_for_timeout(800)
        bi = p6.evaluate(BCI)
        # 第4.125版：一覧は「的中ボード（10種：1〜9・15）」と「ハズレボード（6種：10〜14・15）」に 分ける（15「ボードを持つ馬」は どちらにも）
        check(bool(bi) and bi['after'] == 'setKisekae' and bi['tiles'] == 16 and bi['locks'] == 16 and bi['prep'] == 0 and bi['buy'] == '¥1,500で買う' and bi['bun'] == '¥2,200で買う' and bi['restore'] and bi['see'] == 16 and bi['fit'] == 2
              and bi['secs'] == ['hit:10:的中ボード（10種）', 'miss:6:ハズレボード（6種）']
              and bi['names'] == PIC_NAMES6[:9] + ['ボードを持つ馬'] + PIC_NAMES6[9:] + ['ボードを持つ馬'] and not bi['slots'] and not bi['picks'] and bi['pics'] == 14 and ((bi['thumbs'] == 13 and bi['bad'] == 1) if BCP_ON else bi['bad'] == 14),
              f'第4.121版：設定の「結果ボードカスタム」は 着せ替えの 下・15こ（1〜14 は まさちゃんの 絵の ボード・15「ボードを持つ馬」・🔒）・¥1,500で買う（第4.114版）・お得パック ¥2,200で買う・購入を復元・▶ 見る・'
              f'絵の ボードの 見本（たて 3:4 の 絵・読めない とき 名前だけ）（{bi and {k: bi[k] for k in ("after", "tiles", "locks", "prep", "buy", "see", "fit", "names", "pics", "bad", "thumbs")}}）')
        p6.locator('#setBoard .bct[data-bc=ring] .bcn').click(); p6.wait_for_timeout(300)
        t_prep = p6.locator('#toast').inner_text()
        p6.locator('#setBoard .bct[data-bc=carry][data-sec=miss] .bcn').click(); p6.wait_for_timeout(300)
        t_carry = p6.locator('#toast').inner_text()
        check('買うと' in t_prep and '「結果ボードを廻る」は 6レース' in t_prep and '買うと' in t_carry and '90レース' in t_carry, f'買う 前に タイルを 押す → 案内（「結果ボードを廻る」は 6レース・「ボードを持つ馬」は 90レース）（{t_prep}・{t_carry}）')
        # 第4.121版：絵の ボードの「▶ 見る」：押す たびに つぎの 段（的中＝1〜4連勝・出世馬＝1・2・3・4・8・16・24連勝・ハズレ＝1〜4回目）。絵が 読める（.bcpic）・読めない（pen）→ いつもの ボード
        SEEP = "() => { const hb = document.querySelector('#fxOv .hb'), c = TengelFx.current(); return hb && c ? [hb.dataset.bcx || '', hb.dataset.bcp || '', c.kind, hb.classList.contains('bcpic')] : null; }"
        def see_all(iid, n):
            out = []
            for _ in range(n):
                lab0 = p6.locator(f'#setBoard [data-bcact=see][data-id={iid}]').inner_text()
                p6.locator(f'#setBoard [data-bcact=see][data-id={iid}]').click(); p6.wait_for_timeout(900)
                out.append([lab0] + (p6.evaluate(SEEP) or [])); p6.evaluate('TengelFx.close()'); p6.wait_for_timeout(250)
            return out + [p6.locator(f'#setBoard [data-bcact=see][data-id={iid}]').inner_text()]
        sr6, sc6, sm6, sp6 = see_all('ring', 4), see_all('climb', 7), see_all('rain', 4), see_all('pen', 1)
        exp_r = [[f'▶ 見る（{l}）', 'ring', d, 'hit', True] for l, d in (('1連勝', 'ring1'), ('2連勝', 'ring2'), ('3連勝', 'ring3'), ('4連勝〜', 'ring4'))] + ['▶ 見る（1連勝）']
        exp_c = [[f'▶ 見る（{l}）', 'climb', d, 'hit', True] for l, d in (('1連勝', 'shusse1'), ('2連勝', 'shusse2'), ('3連勝', 'shusse3'), ('4連勝', 'shusse4'), ('8連勝', 'shusse8'), ('16連勝', 'shusse16'), ('24連勝〜', 'shusse24'))] + ['▶ 見る（1連勝）']
        exp_m = [[f'▶ 見る（{l}）', 'rain', d, 'miss', True] for l, d in (('1回目', 'miss1'), ('2回目', 'miss1_2'), ('3回目', 'miss1_3'), ('4回目〜', 'miss1_4'))] + ['▶ 見る（1回目）']
        if not BCP_ON:
            exp_r, exp_c, exp_m = [[(x[:2] + ['', x[3], False]) if isinstance(x, list) else x for x in e] for e in (exp_r, exp_c, exp_m)]
        check(sr6 == exp_r and sc6 == exp_c and sm6 == exp_m and sp6 == [['▶ 見る（1回目）', 'pen', '', 'miss', False], '▶ 見る（2回目）'],
              f'第4.121版：絵の ボードの「▶ 見る」は 押す たびに つぎの 段（1〜4連勝〜・出世馬 1〜24連勝〜・ハズレ 1〜4回目〜）・絵が 読めない とき（pen）は いつもの ボード（{sr6}・{sc6[-2:]}・{sm6[-2:]}・{sp6}）')
        # 第4.125版：15「ボードを持つ馬」は 的中ボード・ハズレボードの 両方に 出る → その 一覧の 結果で ためす（見本の 絵も その 結果）
        p6.locator('#setBoard .bct[data-sec=hit] [data-bcact=see][data-id=carry]').click(); p6.wait_for_timeout(1600)
        sv1 = p6.evaluate(SEE6); p6.evaluate('TengelFx.close()'); p6.wait_for_timeout(300)
        lab = p6.locator('#setBoard .bct[data-sec=hit] [data-bcact=see][data-id=carry]').inner_text()
        p6.locator('#setBoard .bct[data-sec=miss] [data-bcact=see][data-id=carry]').click(); p6.wait_for_timeout(1600)
        sv2 = p6.evaluate(SEE6); p6.evaluate('TengelFx.close()'); p6.wait_for_timeout(300)
        p6.locator('#setBoard .bct[data-sec=miss] [data-bcact=see][data-id=carry]').click(); p6.wait_for_timeout(1600)
        sv3 = p6.evaluate(SEE6); p6.evaluate('TengelFx.close()'); p6.wait_for_timeout(300)
        thh = p6.evaluate("[...document.querySelectorAll('#setBoard .bct[data-bc=carry] .bcfake .fh')].map(e => e.innerText)")
        check(sv1 == {'bcx': 'carry', 'kind': 'hit', 'phase': 'reveal'} and sv2 == {'bcx': 'carry', 'kind': 'miss', 'phase': 'reveal'} and sv3 == sv2 and lab == '▶ 見る' and thh == ['的中！', 'ハズレ'],
              f'買う 前でも「▶ 見る」で ためせる（PUSH なしで すぐ 結果の ボード）・15 は 的中ボードの 所では 的中・ハズレボードの 所では ハズレ（見本の 絵も）（{sv1}・{sv2}・{lab}・{thh}）')
        # 買う（App内課金の かわり）→ 台帳に tx-7001（0P）→ 終わらせる（finish）
        p6.evaluate("window.__iap.buy['jp.tengel.app.boardcustom'] = () => ({ ok: true, state: 'ok', tx: { id: '7001', originalId: 'o7001', product: 'jp.tengel.app.boardcustom', kind: 'unlock', date: new Date().toISOString(), revoked: false } }); window.__bridge = []; 0")
        p6.locator('#setBoard [data-bcact=buy]').click(); p6.wait_for_timeout(900)
        fin6 = [x for x in p6.evaluate('window.__bridge') if x['name'] == 'iap' and x['payload']['op'] == 'finish']
        bi = p6.evaluate(BCI)
        check(p6.evaluate("TengelWallet.board.info().owned") and p6.evaluate('TengelWallet.total()') == 1500 and len(fin6) == 1 and fin6[0]['payload']['id'] == '7001' and '買ったよ' in p6.locator('#toast').inner_text() and not bi['buy'] and not bi['bun'] and not p6.evaluate("TengelWallet.bundle.offer()") and p6.locator('#setKisekae .kspk [data-ksact=bundle]').count() == 0
              and '解放 0/15' in bi['prog'] and 'つぎの「結果ボードを廻る」まで あと 6レース' in bi['prog'] and bi['slots'] == ['hit:なし（いつもの ボード）', 'miss:なし（いつもの ボード）'] and not bi['picks'],
              f'¥1,500で買う → 持って いる（ポイントは 1,500P の まま）・取引を 終わらせる・カードは 進み具合（解放 0/15・つぎの「結果ボードを廻る」まで あと 6レース）と 的中の とき／ハズレの とき（どちらも なし）・お得パックは 2つの 買う 所から 消える（{bi["prog"]!r}・{bi["slots"]}）')
        RD = "(r) => TengelWallet.readCharge({ form: { date: '2026-10-20', venue: '大井', r: r }, ocr: {} })"
        for r in range(1, 6): p6.evaluate(RD, r)
        p6.wait_for_timeout(200)
        check(p6.evaluate("TengelWallet.board.info().reads") == 5 and p6.evaluate("TengelWallet.board.info().n") == 0 and p6.locator('#bcNote').count() == 0, '5レース 読み込む → まだ 解放 なし')
        # 結果の ボード：まだ 何も 選んで いない ときは 飾りなし（「とじる」の 場所の もと）
        SPEC6 = {'r': 9, 'n': 14, 'rows': [{'t': '3連単', 'state': '不的中', 'hits': [], 'n': 18}, {'t': '馬単', 'state': '的中', 'hits': [[6, 2]], 'n': 9}], 'ranks': {str(i): i for i in range(1, 15)}}
        MISS6 = {'r': 9, 'n': 14, 'rows': [{'t': '3連単', 'state': '不的中', 'hits': [], 'n': 18}, {'t': '馬単', 'state': '不的中', 'hits': [], 'n': 9}], 'ranks': {str(i): i for i in range(1, 15)}}
        SHOW6 = "(a) => { TengelFx.show(Object.assign({ force: a[0] }, a[1])); if (a[0] !== 'miss') TengelFx.tap(); }"
        HB6 = "() => { const hb = document.querySelector('#fxOv .hb'), c = document.querySelector('#fxOv .close'); if (!hb) return null; const r = c && c.getBoundingClientRect(); return { bcx: hb.dataset.bcx || '', cls: hb.className, parts: hb.querySelectorAll('.bcx').length, close: r && [Math.round(r.left), Math.round(r.top)], cb: r && [Math.round(r.left + r.width / 2), Math.round(r.bottom)], inHb: !!(c && hb.contains(c)) }; }"
        p6.evaluate(SHOW6, ['hit', SPEC6]); p6.wait_for_timeout(2600)
        h0 = p6.evaluate(HB6)
        p6.evaluate('TengelFx.close()'); p6.wait_for_timeout(300)
        check(h0 and h0['bcx'] == '' and h0['parts'] == 0 and not h0['inHb'], f'まだ 選んで いない → 結果の ボードは いつもの 形（{h0}）')
        rr = p6.evaluate(RD, 6); p6.wait_for_timeout(500)
        bi = p6.evaluate(BCI)
        check(rr['charged'] and p6.evaluate(BSEL) == ['ring', '', 1, 'ring', ''] and p6.locator('#bcNote').count() == 1 and '結果ボードを廻る' in p6.locator('#bcNote').inner_text() and bi['locks'] == 15 and '解放 1/15' in bi['prog'] and bi['on'] == ['ring']
              and bi['slots'] == ['hit:結果ボードを廻る', 'miss:なし（いつもの ボード）'] and bi['picks'] == ['ring:hit:true'],
              f'第4.121版：6レース目 → 1「結果ボードを廻る」が 解放：お知らせ・まだ 選んで いない 的中の とき に そのまま 使う（ハズレの とき には つかない）（{bi["prog"]!r}・{bi["slots"]}・{bi["picks"]}）')
        rr = p6.evaluate(RD, 6)
        check(not rr['charged'] and p6.evaluate("TengelWallet.board.info().reads") == 6 and p6.evaluate('TengelWallet.total()') == 300, '同じ レースの 読み直し（0P）は 数えない')
        # 解放の 順番：84レース（14こ：1〜14 の 絵の ボード）→ 15「ボードを持つ馬」は あと 6レース → 90レース目で 解放（第4.120版・第4.121版）
        p6.evaluate("""(async () => { const w = await TengelLocal.getMeta('wallet'); w.board.reads = 84; w.events.push({ id: 'gift-test6', kind: 'gift', bucket: 'free', amount: 20000, at: new Date().toISOString(), what: 'テスト' }); await TengelLocal.putMeta(w); })()""")
        reopen6()
        p6.click('.tabbar button[data-tab=set]'); p6.wait_for_timeout(500)
        p6.locator('#setBoard .bct[data-bc=carry][data-sec=hit] .bcn').click(); p6.wait_for_timeout(300)
        bi = p6.evaluate(BCI)
        pk14 = ['ring:hit:true'] + [f'{x}:hit:false' for x in ('toast', 'race', 'snap', 'seal', 'cup', 'hoist', 'bloom', 'climb')] + [f'{x}:miss:false' for x in ('rain', 'next', 'cover', 'wait', 'pen')]
        check(p6.evaluate(BSEL) == ['ring', '', 14, 'ring', ''] and 'あと 6レース' in p6.locator('#toast').inner_text() and bi['locks'] == 2 and 'つぎの「ボードを持つ馬」まで あと 6レース' in bi['prog'] and bi['picks'] == pk14,
              f'84レース → 14こ 解放（1〜9 は 的中の ボタン・10〜14 は ハズレの ボタン）・15「ボードを持つ馬」は あと 6レース（{p6.locator("#toast").inner_text()}・{bi["prog"]!r}・{bi["picks"]}）')
        for r in range(7, 12): p6.evaluate(RD, r)
        p6.wait_for_timeout(200)
        check(p6.evaluate("TengelWallet.board.info().n") == 14 and p6.locator('#bcNote').count() == 0, '89レース → まだ（お知らせも なし）')
        p6.evaluate(RD, 12); p6.wait_for_timeout(600)
        bi = p6.evaluate(BCI)
        check(p6.evaluate(BSEL) == ['ring', 'carry', 15, 'ring', 'carry'] and p6.locator('#bcNote').count() == 1 and 'ボードを持つ馬' in p6.locator('#bcNote').inner_text() and bi['on'] == ['ring', 'carry'] and bi['news'] >= 1
              and bi['slots'] == ['hit:結果ボードを廻る', 'miss:ボードを持つ馬'] and bi['picks'] == pk14[:9] + ['carry:hit:false'] + pk14[9:] + ['carry:miss:true'] and '解放 15/15' in bi['prog'] and 'ぜんぶ 解放したよ' in bi['prog'],
              f'90レース目 → 15「ボードを持つ馬」が 解放（画面の 上に お知らせ・まだ 選んで いない ハズレの とき に そのまま 使う・的中の とき は「結果ボードを廻る」の まま）（{bi["slots"]}・{bi["picks"][-2:]}）')
        p6.evaluate("TengelWallet.board.select('carry', 'hit')"); p6.wait_for_timeout(300)
        check(p6.evaluate(BSEL) == ['carry', 'carry', 15, 'carry', 'carry'], '的中の とき にも「ボードを持つ馬」を 選ぶ（ここから 下は 前の 版と 同じ ためし）')
        # 結果の ボードに つく：的中の 所は 的中・デカ的中（ハズレ いがい）・ハズレの 所は ハズレ。「とじる」は 動かない
        p6.evaluate(SHOW6, ['hit', SPEC6]); p6.wait_for_timeout(2600); h1 = p6.evaluate(HB6); p6.evaluate('TengelFx.close()'); p6.wait_for_timeout(300)
        p6.evaluate(SHOW6, ['big', SPEC6]); p6.wait_for_timeout(3600); h3 = p6.evaluate(HB6); p6.evaluate('TengelFx.close()'); p6.wait_for_timeout(300)
        p6.evaluate(SHOW6, ['miss', MISS6]); p6.wait_for_timeout(1800); h2 = p6.evaluate(HB6); p6.evaluate('TengelFx.close()'); p6.wait_for_timeout(300)
        check(h1 and h1['bcx'] == 'carry' and 'bcgo' in h1['cls'] and h3 and h3['bcx'] == 'carry' and h2 and h2['bcx'] == 'carry' and h1['close'] == h0['close'] and not h1['inHb'],
              f'結果の ボード：的中・デカ的中・ハズレに「ボードを持つ馬」・「とじる」の 場所は 同じ（ボードの 外）（{h1 and h1["bcx"]}・{h3 and h3["bcx"]}・{h2 and h2["bcx"]}）')
        # ハズレの とき →「なし」（カードの ボタン）：ハズレには つかない・的中には つく
        p6.locator('#setBoard [data-bcact=none][data-slot=miss]').click(); p6.wait_for_timeout(400)
        tn = p6.locator('#toast').inner_text()
        p6.evaluate(SHOW6, ['hit', SPEC6]); p6.wait_for_timeout(2600); h1 = p6.evaluate(HB6); p6.evaluate('TengelFx.close()'); p6.wait_for_timeout(300)
        p6.evaluate(SHOW6, ['miss', MISS6]); p6.wait_for_timeout(1800); h2 = p6.evaluate(HB6); p6.evaluate('TengelFx.close()'); p6.wait_for_timeout(300)
        bi = p6.evaluate(BCI)
        check(p6.evaluate(BSEL) == ['carry', 'none', 15, 'carry', ''] and 'ハズレの ときは いつもの ボード' in tn and h1['bcx'] == 'carry' and h2['bcx'] == ''
              and bi['slots'] == ['hit:ボードを持つ馬', 'miss:なし（いつもの ボード）'] and [x for x in bi['picks'] if x.startswith('carry:')] == ['carry:hit:true', 'carry:miss:false'],
              f'ハズレの とき →「なし」：ハズレの ボードは いつもの 形・的中は そのまま（べつべつ）（{tn}・{bi["slots"]}）')
        # タイルの「的中」を もう一度 押す → 的中も なし／「ハズレ」を 押す → ハズレだけ
        p6.locator('#setBoard [data-bcact=use][data-id=carry][data-slot=hit]').click(); p6.wait_for_timeout(400)
        p6.locator('#setBoard [data-bcact=use][data-id=carry][data-slot=miss]').click(); p6.wait_for_timeout(400)
        tm = p6.locator('#toast').inner_text()
        p6.evaluate(SHOW6, ['hit', SPEC6]); p6.wait_for_timeout(2600); h1 = p6.evaluate(HB6); p6.evaluate('TengelFx.close()'); p6.wait_for_timeout(300)
        p6.evaluate(SHOW6, ['miss', MISS6]); p6.wait_for_timeout(1800); h2 = p6.evaluate(HB6); p6.evaluate('TengelFx.close()'); p6.wait_for_timeout(300)
        bi = p6.evaluate(BCI)
        check(p6.evaluate(BSEL) == ['none', 'carry', 15, '', 'carry'] and 'ハズレの ときに「ボードを持つ馬」を 使うよ' in tm and h1['bcx'] == '' and h2['bcx'] == 'carry'
              and [x for x in bi['picks'] if x.startswith('carry:')] == ['carry:hit:false', 'carry:miss:true'] and bi['on'] == ['carry'] and bi['slots'] == ['hit:なし（いつもの ボード）', 'miss:ボードを持つ馬'],
              f'タイルの「的中」「ハズレ」：押すと その 所に 使う・もう一度 押すと なし（的中は いつもの 形・ハズレだけ「ボードを持つ馬」）（{tm}・{bi["picks"]}）')
        # 的中の とき／ハズレの とき の「▶ 見る」：選んで いる もの を その 結果の ボードで
        p6.locator('#setBoard [data-bcact=seeslot][data-slot=miss]').click(); p6.wait_for_timeout(1600); s1 = p6.evaluate(SEE6); p6.evaluate('TengelFx.close()'); p6.wait_for_timeout(300)
        p6.locator('#setBoard [data-bcact=seeslot][data-slot=hit]').click(); p6.wait_for_timeout(1600); s2 = p6.evaluate(SEE6); p6.evaluate('TengelFx.close()'); p6.wait_for_timeout(300)
        sk6 = [p6.evaluate("(a) => TengelWallet.board.select(a[0], a[1])", a) for a in (['prep3', 'hit'], ['orbit', 'miss'], ['carry', 'hit'])]
        check(s1 == {'bcx': 'carry', 'kind': 'miss', 'phase': 'reveal'} and s2 == {'bcx': '', 'kind': 'hit', 'phase': 'reveal'} and sk6 == [False, False, True] and p6.evaluate(BSEL) == ['carry', 'carry', 15, 'carry', 'carry'],
              f'的中の とき／ハズレの とき の「▶ 見る」は その 結果の ボードで（なし なら いつもの 形）・じゅんび中と 消した 飾りは 選べない（{s1}・{s2}・{sk6}）')
        # 第4.108版：16「ボードを持つ馬」：的中にも ハズレにも つく・下から ボードを かかえて 出てくる（.bce-carry → 出おわると .bcgo）・頭と首・後ろ足・しっぽ・前足の 部品・
        #   「とじる」は 動かない・控えめは 止まった 形。この テストは 絵（ios/fx_assets の bcx_hb_*.webp）を 置かないので SVG の 馬（.bchbv）
        CR6 = "() => { const hb = document.querySelector('#fxOv .hb'), c = document.querySelector('#fxOv .close'); if (!hb) return null; const r = c.getBoundingClientRect(), vis = s => [...hb.querySelectorAll(s)].filter(e => e.getClientRects().length).length; return { bcx: hb.dataset.bcx || '', cls: hb.className, an: getComputedStyle(hb).animationName, head: vis('.bc-hbh'), legs: vis('.bc-hbl'), tail: vis('.bc-hbt'), imgs: hb.querySelectorAll('img.bchbi').length, close: [Math.round(r.left), Math.round(r.top)] }; }"
        SLIP6 = "() => { const rb = document.querySelector('#fxOv .hb .rb'); return rb ? rb.getAnimations().filter(a => a.animationName === 'bcHbSlip').length : -1; }"
        CL6 = "() => { const r = document.querySelector('#fxOv .close').getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top)]; }"
        p6.evaluate(SHOW6, ['hit', SPEC6]); p6.wait_for_timeout(500); c1 = p6.evaluate(CR6); p6.wait_for_timeout(2400); c1b = p6.evaluate(CR6)
        # 第4.108版：1回だけ ボードを 落としそうに なる（出おわって 1.5秒後・1.4秒）：その 間も「とじる」は 動かない・おわったら もう 起きない
        sl = {'on': False, 'close': None, 'again': False}
        try:
            p6.wait_for_function("() => { const rb = document.querySelector('#fxOv .hb .rb'); return rb && rb.getAnimations().some(a => a.animationName === 'bcHbSlip' && a.playState === 'running' && a.currentTime > 1600); }", timeout=8000)
            sl['on'] = True; sl['close'] = p6.evaluate(CL6); sl['tf'] = p6.evaluate("getComputedStyle(document.querySelector('#fxOv .hb .rb')).transform")
            p6.wait_for_function("() => { const rb = document.querySelector('#fxOv .hb .rb'); return rb && !rb.getAnimations().some(a => a.animationName === 'bcHbSlip'); }", timeout=8000)
            p6.wait_for_timeout(2500); sl['again'] = p6.evaluate(SLIP6) != 0
        except Exception as e:
            print('   （落としそうに なる 所：', str(e)[:80], '）')
        p6.evaluate('TengelFx.close()'); p6.wait_for_timeout(300)
        p6.evaluate(SHOW6, ['miss', MISS6]); p6.wait_for_timeout(1800); c2 = p6.evaluate(CR6); p6.evaluate('TengelFx.close()'); p6.wait_for_timeout(300)
        p6.evaluate("TengelFx.set({ calm: true })")
        p6.evaluate(SHOW6, ['hit', SPEC6]); p6.wait_for_timeout(2600); c3 = p6.evaluate(CR6); p6.wait_for_timeout(2600); c3s = p6.evaluate(SLIP6); c3a = p6.evaluate("getComputedStyle(document.querySelector('#fxOv .hb .rb')).animationName")
        p6.evaluate('TengelFx.close()'); p6.wait_for_timeout(300)
        p6.evaluate("TengelFx.set({ calm: false })")
        check(c1 and c1['bcx'] == 'carry' and 'bce-carry' in c1['cls'] and c1['an'].startswith('bcECarry') and 'bcgo' in c1b['cls'] and 'bchbv' in c1b['cls'] and c1b['imgs'] == 5 and c1b['head'] >= 1 and c1b['legs'] >= 1 and c1b['tail'] >= 1
              and c2 and c2['bcx'] == 'carry' and 'bcgo' in c2['cls'] and c1b['close'] == h0['close'] and c2['close'] == h0['close'] and c3['bcx'] == 'carry' and 'bcst' in c3['cls'] and 'bce-carry' not in c3['cls'],
              f'第4.108版：「ボードを持つ馬」（第4.120版から 15）は 的中にも ハズレにも つく・下から 出てくる（bcECarry → .bcgo）・頭と首・後ろ足・しっぽ（絵が ない ときは SVG の 馬）・「とじる」は 動かない・控えめは 止まった 形（{c1 and c1["cls"]}・{c1b["cls"]}・{c3["cls"]}）')
        check(sl['on'] and sl['close'] == h0['close'] and sl.get('tf', 'none') != 'none' and not sl['again'] and c3s == 0 and c3a == 'none',
              f'第4.108版：「ボードを持つ馬」（第4.120版から 15）：1回だけ ボードを 落としそうに なる（その 間も「とじる」は 動かない・おわったら もう 起きない）・控えめなら 起きない（{sl}・{c3s}・{c3a}）')
        # 連続的中の 数（第4.113版）・続けて ハズレた 数（第4.121版：絵の ボードの 段）：同じ レースは 1回・的中で 連続的中 +1 と ハズレの 数 0・ハズレで ハズレの 数 +1 と 連続的中 0。
        #   返す 数は その 結果の 連続（的中 → 連続的中・ハズレ → 続けて ハズレた 数）
        sk = [p6.evaluate("(a) => TengelWallet.board.result(a[0], a[1])", a) for a in (['x1', True], ['x1', True], ['x2', True], ['x3', False], ['x4', True], ['x5', False], ['x6', False], ['x6', False], ['x7', True])]
        ski = p6.evaluate("(() => { const i = TengelWallet.board.info(); return [i.streak, i.mstreak]; })()")
        check(sk == [1, 1, 2, 1, 1, 1, 2, 2, 1] and ski == [1, 0], f'第4.121版：連続的中の 数と 続けて ハズレた 数（的中 +1・ハズレで 0／ハズレ +1・的中で 0・同じ レースは 1回・返す 数は その 結果の 連続）（{sk}・{ski}）')
        # 第4.121版：絵の ボードの 段は 結果の 連続の 数（spec.streak：src.html が board.result の 数を 渡す）で きまる。出世馬は 1・2・3・4・8・16・24連勝・ハズレは 4回目から 上は 4回目
        #   的中エフェクト オフ（静かな ボード）・控えめ でも 同じ 絵（止まった 形）。「とじる」の 場所は 同じ（色だけ その 絵に 合わせる）。絵が 読めない（pen）→ いつもの ボード
        p6.evaluate("TengelWallet.board.select('climb', 'hit')"); p6.evaluate("TengelWallet.board.select('rain', 'miss')"); p6.wait_for_timeout(300)
        BCP6 = """() => { const hb = document.querySelector('#fxOv .hb'), ov = hb && hb.parentNode, rb = hb && hb.querySelector('.rb'), bg = hb && hb.querySelector('.bcpbg'), c = document.querySelector('#fxOv .close'), r = c && c.getBoundingClientRect();
          return hb ? [hb.dataset.bcx || '', hb.dataset.bcp || '', hb.classList.contains('bcpic'), !!(ov && ov.classList.contains('bcpdone')), !!(bg && bg.naturalWidth), rb ? rb.style.transform.slice(0, 9) : '', hb.classList.contains('bcst'),
            r ? [Math.round(r.left + r.width / 2), Math.round(r.bottom)] : null, (document.getElementById('bcxDyn') || {}).textContent || '',
            (() => { const w = hb.querySelector('.bcpw'), ch = w ? [...w.querySelectorAll('.chrw')] : [];      // 第4.129版：動く 絵の ボード
              return { n: ch.length, go: !!(w && w.classList.contains('chrgo')), mo: (w && w.dataset.mo) || '', bg: bg ? (bg.getAttribute('src') || '').split('/').pop() : '',
                an: ch.filter(e => e.getAnimations().length).length, oc: w ? w.querySelectorAll('.chroc').length : 0, ot: w ? w.querySelectorAll('.chrot').length : 0 }; })()] : null; }"""
        stg = []
        for kd, sp_, n_, setv in (('hit', SPEC6, 1, None), ('hit', SPEC6, 3, None), ('big', SPEC6, 5, None), ('hit', SPEC6, 16, None), ('hit', SPEC6, 40, None), ('miss', MISS6, 1, None), ('miss', MISS6, 2, None), ('miss', MISS6, 7, None),
                                  ('hit', SPEC6, 2, {'effects': False}), ('miss', MISS6, 3, {'calm': True})):
            if setv: p6.evaluate("(o) => TengelFx.set(o)", setv)
            p6.evaluate(SHOW6, [kd, dict(sp_, streak=n_)]); p6.wait_for_timeout(3000 if kd == 'big' else 2600); stg.append(p6.evaluate(BCP6)); p6.evaluate('TengelFx.close()'); p6.wait_for_timeout(300)
            if setv: p6.evaluate("(o) => TengelFx.set(o)", {k: (not v) for k, v in setv.items()})
        p6.evaluate("TengelWallet.board.select('pen', 'miss')"); p6.wait_for_timeout(300)
        p6.evaluate(SHOW6, ['miss', dict(MISS6, streak=1)]); p6.wait_for_timeout(2600); stp = p6.evaluate(BCP6); p6.evaluate('TengelFx.close()'); p6.wait_for_timeout(300)
        cl16 = _bcp.design('shusse16')['cl'][0]
        want6 = ['shusse1', 'shusse3', 'shusse4', 'shusse16', 'shusse24', 'miss1', 'miss1_2', 'miss1_4', 'shusse2', 'miss1_3']
        ok6 = all(x and x[0] == ('rain' if i in (5, 6, 7, 9) else 'climb') and x[7] == h0['cb'] for i, x in enumerate(stg))   # 「とじる」の まん中と 下の はし（ふちが 太い 絵も ある）
        if BCP_ON:
            ok6 = ok6 and [x[1] for x in stg] == want6 and all(x[2] and x[3] and x[4] and x[5] == 'matrix3d(' for x in stg) and [x[6] for x in stg] == [False] * 8 + [True, True] and cl16 in stg[3][8] and cl16 not in stg[0][8]
        else:
            ok6 = ok6 and all(x[1] == '' and not x[2] and not x[3] for x in stg)
        check(ok6 and stp and stp[0] == 'pen' and stp[1] == '' and not stp[2] and not stp[3] and stp[7] == h0['cb'],
              f'第4.121版：絵の ボードの 段は 連続の 数（出世馬 1→1・3→3・5→4・16→16・40→24連勝／ハズレ 1・2・7→1・2・4回目）・オフと 控えめは 止まった 形・「とじる」の 場所は 同じ（出世馬 16連勝は その 色）・'
              f'絵が 読めない → いつもの ボード（{[x and x[:8] for x in stg]}・{stp and stp[:4]}・{h0["cb"]}・{cl16 in stg[3][8]}）')
        # 第4.129版：動く 絵の ボード（二人でしょんぼり：キャラ 2人＋ボードの 前に 出る 所・動かない 青い 線）。出世馬は まだ 動かない・控えめ／絵が 読めない ときは 動かない
        mo6 = [x and x[9] for x in stg]
        if BCP_ON:
            def _mw(n):
                L_ = _bcp.MOTION[n]['layers']; return len(L_) + sum(1 for l in L_ if l.get('f'))
            okm = all(m['n'] == 0 and not m['go'] and m['mo'] == '' for i, m in enumerate(mo6) if i not in (5, 6, 7)) and all(
                mo6[i]['go'] and mo6[i]['mo'] == want6[i] and mo6[i]['n'] == _mw(want6[i]) and mo6[i]['an'] == mo6[i]['n'] and mo6[i]['bg'] == _bcp.MOTION[want6[i]]['bgx']
                and mo6[i]['oc'] == 1 and mo6[i]['ot'] == 1 for i in (5, 6, 7)) and stg[8][9]['bg'] == 'bcp_shusse2.webp' and stg[9][9]['bg'] == 'bcp_miss1_3.webp'
        else:
            okm = all(m['n'] == 0 and not m['go'] for m in mo6)
        check(okm and stp[9]['n'] == 0 and not stp[9]['go'], f'第4.129版：動く 絵の ボード：二人でしょんぼりは キャラが 動く（キャラ・前に 出る 所が 動いて、背景は キャラなし・動かない 物は 上に）・'
              f'出世馬は 動かない・控えめは 止まった 絵・絵が 読めない → 動かない（{mo6}・{stp[9]}）')
        # 前の 版の 台帳（1つの 選択 sel）：その とき 的中にも ハズレにも ついて いた ので 両方へ・消した 飾り（1〜21）は まだ 選んで いない と 同じ
        p6.evaluate("""(async () => { const w = await TengelLocal.getMeta('wallet'); w.board = { reads: 146, sel: 'carry', streak: 3, res: [] }; await TengelLocal.putMeta(w); })()""")
        reopen6()
        lg1 = p6.evaluate(BSEL)
        p6.evaluate("""(async () => { const w = await TengelLocal.getMeta('wallet'); w.board = { reads: 146, sel: 'orbit', streak: 0, res: [] }; await TengelLocal.putMeta(w); })()""")
        reopen6()
        lg2 = p6.evaluate(BSEL)
        p6.evaluate(SHOW6, ['hit', SPEC6]); p6.wait_for_timeout(2600); h1 = p6.evaluate(HB6); p6.evaluate('TengelFx.close()'); p6.wait_for_timeout(300)
        check(lg1 == ['carry', 'carry', 15, 'carry', 'carry'] and lg2 == ['', '', 15, '', ''] and h1['bcx'] == '',
              f'前の 版の 台帳：「ボードを持つ馬」を 選んで いた → 的中・ハズレの 両方に・消した 飾り（ボードを一周 など）→ なし（{lg1}・{lg2}）')
        # 返金 → 使えなくなる（飾りなし）・購入を復元 → もどる
        p6.evaluate("TengelWallet.board.select('carry', 'hit')"); p6.wait_for_timeout(200)
        p6.evaluate("window.__nativeEvent('iap', { id: '7001', originalId: 'o7001', product: 'jp.tengel.app.boardcustom', kind: 'unlock', date: new Date().toISOString(), revoked: true, revokedAt: new Date().toISOString() })"); p6.wait_for_timeout(700)
        p6.evaluate(SHOW6, ['hit', SPEC6]); p6.wait_for_timeout(2600); h1 = p6.evaluate(HB6); p6.evaluate('TengelFx.close()'); p6.wait_for_timeout(300)
        check(not p6.evaluate("TengelWallet.board.info().owned") and h1['bcx'] == '' and '返金' in p6.locator('#toast').inner_text() and p6.locator('#setBoard [data-bcact=buy]').count() == 1, f'返金 → 使えなくなる（飾りなし・カードは また「買う」）（{p6.locator("#toast").inner_text()}）')
        p6.evaluate("window.__iap.current = [{ id: '7002', originalId: 'o7001', product: 'jp.tengel.app.boardcustom', kind: 'unlock', date: new Date().toISOString(), revoked: false }]; 0")
        p6.locator('#setBoard [data-bcact=restore]').click(); p6.wait_for_timeout(900)
        check(p6.evaluate("TengelWallet.board.info().owned") and 'もどしたよ' in p6.locator('#toast').inner_text() and p6.evaluate(BSEL) == ['carry', '', 15, 'carry', ''], f'購入を復元 → もどる（この 端末の 進み具合と 選んだ ものは そのまま）（{p6.locator("#toast").inner_text()}）')
        p6.screenshot(path=os.path.join(W, 't4', 'native_board_custom.png'), full_page=False)
        ctx6.close()
        # ---- 第4.92版：壁紙パック（買い切り 1,500円・非消耗型 jp.tengel.app.wallpack1）：着せ替えの いちばん上の 組・買う／購入を復元・読み込み 5レースごとに 1枚ずつ 解放・
        #      帯の 壁紙の ミッションに 数える・返金で 使えなくなる・復元で もどる ----
        m7 = {}

        def marker7(source, q):
            op, key = q.get('op'), q.get('key')
            if op == 'set': m7[key] = q.get('value', '1'); return {'ok': True}
            if op == 'del': m7.pop(key, None); return {'ok': True}
            v = m7.get(key); return {'ok': True, 'has': v is not None, 'value': v}
        ctx7 = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP'); ctx7.add_init_script(FAKE)
        ctx7.expose_binding('__saveBackup', lambda s, t: None); ctx7.expose_binding('__marker', marker7)
        p7 = ctx7.new_page(); p7.on('pageerror', lambda e: errs.append('PACK ' + str(e)))
        p7.goto(APPURL); p7.wait_for_timeout(1500); gate(p7); p7.wait_for_timeout(700)
        p7.click('.tabbar button[data-tab=set]'); p7.wait_for_timeout(600)
        PKI = """() => { const c = document.querySelector('#setKisekae'); if (!c) return null; const g = c.querySelector('h3.ksg'); const box = c.querySelector('.kspk');
          const pk = TengelKisekae.pack(); const tiles = pk.ids.map(id => c.querySelector(`.kst[data-ks="${id}"]`)).filter(Boolean);
          return { first: g ? g.firstChild.textContent : '', buy: (c.querySelector('.kspk [data-ksact=pkbuy]') || {}).innerText || '', bun: (c.querySelector('.kspk [data-ksact=bundle]') || {}).innerText || '', restore: !!c.querySelector('.kspk [data-ksact=pkrestore]'),
            box: box ? box.innerText : '', ids: pk.ids, order: pk.order, tiles: tiles.length, locks: tiles.filter(t => t.querySelector('.kslock')).map(t => t.querySelector('.kslock').innerText),
            owned: pk.owned, n: pk.n, reads: pk.reads }; }"""
        k0 = p7.evaluate(PKI)
        check(bool(k0) and k0['first'] == '壁紙パック' and k0['buy'] == '¥1,500で買う' and k0['bun'] == '¥2,200で買う' and k0['restore'] and k0['tiles'] == len(k0['ids']) >= 1 and all('壁紙パック' in x for x in k0['locks']) and len(k0['locks']) == len(k0['ids'])
              and k0['order'][:2] == ['pirate', 'course'] and len(k0['order']) == 11 and not k0['owned'],
              f'第4.92版：着せ替えの いちばん上に「壁紙パック」の 組（¥1,500で買う・第4.114版：お得パック ¥2,200で買う・購入を復元・カギの 壁紙 {k0 and k0["tiles"]}枚・解放の 順は 海賊 → 競馬場 → … の 11枚）（{k0 and {k: k0[k] for k in ("first", "buy", "bun", "tiles", "ids")}}）')
        check(not p7.evaluate("TengelKisekae.usable('pirate')") and p7.evaluate("TengelKisekae.usable('default')"), '買う 前は 壁紙パックの 壁紙は 使えない（ポイントでも 解放 できない）')
        p7.locator('#setKisekae .kst[data-ks=pirate]').click(); p7.wait_for_timeout(400)
        check(p7.locator('#setKisekae .kst.cf[data-ks=pirate] [data-ksact=pkbuy]').count() == 1, 'カギの 壁紙を 押すと その 下に「¥1,500で買う」')
        p7.evaluate("window.__iap.buy['jp.tengel.app.wallpack1'] = () => ({ ok: true, state: 'ok', tx: { id: '8001', originalId: 'o8001', product: 'jp.tengel.app.wallpack1', kind: 'unlock', date: new Date().toISOString(), revoked: false } }); window.__bridge = []; 0")
        p7.locator('#setKisekae .kst.cf [data-ksact=pkbuy]').click(); p7.wait_for_timeout(900)
        fin7 = [x for x in p7.evaluate('window.__bridge') if x['name'] == 'iap' and x['payload']['op'] == 'finish']
        k1 = p7.evaluate(PKI)
        check(k1['owned'] and k1['n'] == 0 and p7.evaluate('TengelWallet.total()') == 1500 and len(fin7) == 1 and fin7[0]['payload']['id'] == '8001' and '買ったよ' in p7.locator('#toast').inner_text()
              and '解放 0/11' in k1['box'] and 'あと 5レース' in k1['box'] and not k1['buy'] and not k1['bun'] and k1['locks'][0] == '🔒 あと5レース' and not p7.evaluate("TengelWallet.bundle.offer()") and p7.locator('#setBoard [data-bcact=bundle]').count() == 0 and p7.locator('#setBoard [data-bcact=buy]').inner_text() == '¥1,500で買う',
              f'¥1,500で買う → 持って いる（ポイントは 1,500P の まま）・取引を 終わらせる・箱は 進み具合（解放 0/11・つぎの「海賊」まで あと 5レース）・お得パックは 消えて 結果ボードカスタムの 単品だけ（{k1["box"]!r}）')
        p7.locator('#setKisekae .kst[data-ks=pirate]').click(); p7.wait_for_timeout(300)
        check('あと 5レース' in p7.locator('#toast').inner_text(), f'買った あと・解放 前に 押す → あと 何レースか（{p7.locator("#toast").inner_text()}）')
        RD7 = "(r) => TengelWallet.readCharge({ form: { date: '2026-10-21', venue: '大井', r: r }, ocr: {} })"
        for r in range(1, 5): p7.evaluate(RD7, r)
        p7.wait_for_timeout(200)
        check(p7.evaluate("TengelKisekae.pack().reads") == 4 and p7.evaluate("TengelKisekae.pack().n") == 0 and not p7.evaluate("TengelKisekae.usable('pirate')"), '4レース 読み込む → まだ 解放 なし')
        p7.evaluate(RD7, 5); p7.wait_for_timeout(500)
        t7 = p7.locator('#ksNote').inner_text() if p7.locator('#ksNote').count() else ''
        check(p7.evaluate("TengelKisekae.pack().n") == 1 and p7.evaluate("TengelKisekae.usable('pirate')") and '「海賊」' in t7 and p7.locator('#ksNote [data-ksnote=pirate]').count() == 1 and p7.evaluate("TengelPoints.wallCount(TengelWallet.events(), TengelWallet.pack.info().n)") == 1,
              f'5レース目 → 1枚目「海賊」が 解放（画面の 上に 小さな 絵と「着せ替える」の お知らせ・帯の ミッションの 枚数 1）（{t7!r}）')
        p7.locator('#ksNote [data-ksnote=pirate]').click(); p7.wait_for_timeout(1500)
        check(p7.evaluate("TengelKisekae.current()") == 'pirate' and p7.locator('#ksNote').count() == 0, 'お知らせの「着せ替える」→ すぐ「海賊」に 着せ替わる')
        p7.evaluate("TengelKisekae.apply('default')"); p7.wait_for_timeout(600)
        rr7 = p7.evaluate(RD7, 5)
        check(not rr7['charged'] and p7.evaluate("TengelKisekae.pack().reads") == 5, '同じ レースの 読み直し（0P）は 数えない')
        p7.locator('#setKisekae .kst[data-ks=pirate]').click(); p7.wait_for_timeout(1500)
        check(p7.evaluate("TengelKisekae.current()") == 'pirate' and p7.evaluate("document.documentElement.dataset.ks") == 'pirate' and p7.evaluate("!!document.querySelector('#ksBnr .prw')"), '解放した「海賊」に 着せ替えられる（上の 絵も）')
        # 35レース（7枚）＋ ポイントで 1枚 ＝ 8枚 → シルバー帯の ミッションが 受け取れる
        p7.evaluate("""(async () => { const w = await TengelLocal.getMeta('wallet'); w.pack.reads = 35; w.events.push({ id: 'unlock-theme:sakura', kind: 'unlock', bucket: '', amount: 0, at: new Date().toISOString(), use: { paid_sub: 0, paid_pack: 0, free: 0 }, what: 'theme:sakura', device: 'x' }); await TengelLocal.putMeta(w); })()""")
        for _ in range(3):
            p7.goto(APPURL); p7.wait_for_timeout(900); gate(p7)
            try:
                p7.wait_for_selector('.tabbar button[data-tab=set]', timeout=15000); p7.wait_for_timeout(1000); break
            except Exception:
                pass
        wm7 = p7.evaluate("(() => { const w = TengelWallet; return TengelPoints.wallMissions(TengelPoints.wallCount(w.events(), w.pack.info().n), w.events()).map(m => [m.n, m.claimable]); })()")
        check(p7.evaluate("TengelKisekae.pack().n") == 7 and wm7[0] == [8, True] and wm7[1] == [16, False], f'壁紙パックの 7枚 ＋ ポイントの 1枚 ＝ 8枚 → シルバー帯の 壁紙が ミッションで 受け取れる（{wm7}）')
        # 返金 → 使えなくなる（いつもの に もどる）・購入を復元 → もどる（この 端末の 進み具合は そのまま）
        p7.evaluate("window.__nativeEvent('iap', { id: '8001', originalId: 'o8001', product: 'jp.tengel.app.wallpack1', kind: 'unlock', date: new Date().toISOString(), revoked: true, revokedAt: new Date().toISOString() })"); p7.wait_for_timeout(900)
        check(not p7.evaluate("TengelKisekae.pack().owned") and not p7.evaluate("TengelKisekae.usable('pirate')") and p7.evaluate("TengelKisekae.current()") == 'default' and '返金' in p7.locator('#toast').inner_text(),
              f'返金 → 壁紙パックの 壁紙は 使えなくなる（いつもの に もどる）（{p7.locator("#toast").inner_text()}）')
        p7.click('.tabbar button[data-tab=set]'); p7.wait_for_timeout(500)
        p7.evaluate("window.__iap.current = [{ id: '8002', originalId: 'o8001', product: 'jp.tengel.app.wallpack1', kind: 'unlock', date: new Date().toISOString(), revoked: false }]; 0")
        p7.locator('#setKisekae .kspk [data-ksact=pkrestore]').click(); p7.wait_for_timeout(900)
        check(p7.evaluate("TengelKisekae.pack().owned") and p7.evaluate("TengelKisekae.pack().n") == 7 and 'もどしたよ' in p7.locator('#toast').inner_text(), f'購入を復元 → もどる（解放 7枚 の まま）（{p7.locator("#toast").inner_text()}）')
        p7.screenshot(path=os.path.join(W, 't4', 'native_wall_pack.png'), full_page=False)
        ctx7.close()
        # ---- 第4.114版（まさちゃん 2026/11/01）：お得パック（jp.tengel.app.bundle1・2,200円＝壁紙パックと 結果ボードカスタムの セット）：単品を どちらも 持って いない ときだけ 2つの 買う 所に 出る・
        #      買うと 2つとも 持って いる・読み込みで 2つとも 進む・返金で 2つとも 使えなくなる・購入を復元で もどる。ミッション：結果ボードカスタムの 解放の 数（3〜16こ）・壁紙の 枚数（3〜45枚・帯も 数える）----
        m8 = {}

        def marker8(source, q):
            op, key = q.get('op'), q.get('key')
            if op == 'set': m8[key] = q.get('value', '1'); return {'ok': True}
            if op == 'del': m8.pop(key, None); return {'ok': True}
            v = m8.get(key); return {'ok': True, 'has': v is not None, 'value': v}
        ctx8 = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP'); ctx8.add_init_script(FAKE)
        ctx8.expose_binding('__saveBackup', lambda s, t: None); ctx8.expose_binding('__marker', marker8)
        p8 = ctx8.new_page(); p8.on('pageerror', lambda e: errs.append('BUNDLE ' + str(e)))

        def reopen8():
            for _ in range(3):
                p8.goto(APPURL); p8.wait_for_timeout(800); gate(p8)
                try:
                    p8.wait_for_selector('.tabbar button[data-tab=set]', timeout=15000); p8.wait_for_timeout(1000); return
                except Exception as e:
                    print('   （開き直し もう一度：', str(e)[:80], '）')
        p8.goto(APPURL); p8.wait_for_timeout(1500); gate(p8); p8.wait_for_timeout(700)
        p8.click('.tabbar button[data-tab=set]'); p8.wait_for_timeout(600)
        BUN = """() => { const q = s => document.querySelector(s), t = s => (q(s) || {}).innerText || ''; const W = TengelWallet;
          return { offer: W.bundle.offer(), owned: W.bundle.owned(), bOwn: W.board.info().owned, pOwn: TengelKisekae.pack().owned, bN: W.board.info().n, bR: W.board.info().reads, pN: TengelKisekae.pack().n, pR: TengelKisekae.pack().reads,
            bBuy: t('#setBoard [data-bcact=buy]'), bBun: t('#setBoard [data-bcact=bundle]'), bBunTxt: t('#setBoard .bcbun'), pBuy: t('#setKisekae .kspk [data-ksact=pkbuy]'), pBun: t('#setKisekae .kspk [data-ksact=bundle]'), pBunTxt: t('#setKisekae .kspku'),
            bProg: t('#setBoard .bcprog'), pBox: t('#setKisekae .kspk'), total: W.total(), free: W.balance().free, badge: t('#msBtn .mbd'), hot: !!(q('#msBtn') && q('#msBtn').classList.contains('hot')) }; }"""
        u0 = p8.evaluate(BUN)
        check(u0['offer'] and not u0['owned'] and not u0['bOwn'] and not u0['pOwn'] and u0['bBuy'] == '¥1,500で買う' and u0['bBun'] == '¥2,200で買う' and u0['pBuy'] == '¥1,500で買う' and u0['pBun'] == '¥2,200で買う'
              and 'お得パック' in u0['bBunTxt'] and 'セット' in u0['bBunTxt'] and 'お得パック' in u0['pBunTxt'] and 'セット' in u0['pBunTxt'],
              f'第4.114版：どちらも 持って いない → 結果ボードカスタムの カード（¥1,500で買う）と 壁紙パックの 箱（¥1,500で買う）の 中に「お得パック」（2つの セット・¥2,200で買う）（{ {k: u0[k] for k in ("bBuy", "bBun", "pBuy", "pBun")} }）')
        p8.evaluate("window.__iap.buy['jp.tengel.app.bundle1'] = () => ({ ok: true, state: 'ok', tx: { id: '9001', originalId: 'o9001', product: 'jp.tengel.app.bundle1', kind: 'unlock', date: new Date().toISOString(), revoked: false } }); window.__bridge = []; 0")
        p8.locator('#setBoard [data-bcact=bundle]').click(); p8.wait_for_timeout(1000)
        fin8 = [x for x in p8.evaluate('window.__bridge') if x['name'] == 'iap' and x['payload']['op'] == 'finish']
        u1 = p8.evaluate(BUN); t8 = p8.locator('#toast').inner_text()
        check(u1['owned'] and u1['bOwn'] and u1['pOwn'] and not u1['offer'] and u1['total'] == 1500 and len(fin8) == 1 and fin8[0]['payload']['id'] == '9001' and 'お得パック' in t8 and '買ったよ' in t8
              and not u1['bBuy'] and not u1['bBun'] and not u1['pBuy'] and not u1['pBun'] and '解放 0/15' in u1['bProg'] and '解放 0/11' in u1['pBox'],
              f'「お得パック ¥2,200で買う」→ 壁紙パックも 結果ボードカスタムも 持って いる（ポイントは 1,500P の まま・取引を 終わらせる）・2つとも 進み具合の 表示に（買うの ボタンは 消える）（{t8}）')
        p8.locator('#setPoints [data-pt=show][data-v=hist]').click(); p8.wait_for_timeout(300)
        check('お得パック' in p8.locator('#setPoints .pthist').inner_text(), 'ポイントの 履歴に「解放：お得パック（壁紙パックと 結果ボードカスタム・買い切り）」')
        RD8 = "(r) => TengelWallet.readCharge({ form: { date: '2026-10-22', venue: '大井', r: r }, ocr: {} })"
        for r in range(1, 7): p8.evaluate(RD8, r)
        p8.wait_for_timeout(500)
        u2 = p8.evaluate(BUN)
        check(u2['bR'] == 6 and u2['bN'] == 1 and u2['pR'] == 6 and u2['pN'] == 1 and p8.evaluate("TengelKisekae.usable('pirate')") and u2['total'] == 300,
              f'6レース 読み込む → 壁紙パック 1枚（5レース目）も 結果ボードカスタム 1こ（6レース目）も 進む（{ {k: u2[k] for k in ("bR", "bN", "pR", "pN")} }）')
        # ミッション：結果ボードカスタム 14こ（84レース）・壁紙パック 11枚（55レース以上）→ 結果ボードカスタム 3・6・9・12（4つ）・壁紙の 枚数 3・6・9（3つ）・帯の シルバー（1つ）＝8つ（第4.120版：全部で 15こ）
        p8.evaluate("""(async () => { const w = await TengelLocal.getMeta('wallet'); w.board.reads = 84; w.pack.reads = 100; await TengelLocal.putMeta(w); })()""")
        reopen8()
        p8.click('.tabbar button[data-tab=set]'); p8.wait_for_timeout(600)   # 設定タブを 開く（App Store の 表示価格を 読む）
        u3 = p8.evaluate(BUN)
        check(u3['bN'] == 14 and u3['pN'] == 11 and u3['badge'] == '8' and u3['hot'] and p8.locator('.tabbar [data-tab=set] .tbdg').count() == 1,
              f'結果ボードカスタム 14こ・壁紙 11枚 → 上の「ミッション」に 受け取れる 8（結果ボードカスタム 4・壁紙の 枚数 3・シルバー帯 1）（{u3["badge"]}）')
        p8.click('#msBtn'); p8.wait_for_timeout(600)
        ov8 = p8.locator('#msOv')
        MSI = """() => { const ov = document.querySelector('#msOv'); if (!ov) return null; const rows = s => [...ov.querySelectorAll(s + ' .msrow')].map(r => r.dataset.mid + (r.classList.contains('can') ? '*' : '')); const txt = s => (ov.querySelector(s) || {}).innerText || '';
          return { n: txt('.msn'), board: rows('#msBoard'), wallp: rows('#msWallp'), wall: rows('#msWall'), h2: [...ov.querySelectorAll('h2')].map(h => h.innerText.trim()), last: txt('#msWallp .msrow[data-mid="mission-wallp-40"] .md'), has45: !!ov.querySelector('.msrow[data-mid="mission-wallp-45"]'), mp: (document.querySelector('#msBtn .mp') || {}).innerText || '', b3: txt('#msBoard .msrow[data-mid="mission-board-3"] .mn'), w3: txt('#msWallp .msrow[data-mid="mission-wallp-3"] .mn'),
            bhint: txt('#msBoard .hint'), whint: txt('#msWallp .hint'), claims: ov.querySelectorAll('[data-pt=claim]').length }; }"""
        mi = p8.evaluate(MSI)
        # 第4.139版：壁紙の 枚数の 行は 10こ（40枚まで・45枚の 行は ない）・窓の 上は「達成 n/37」と 受け取れる 数（上の「ミッション」の ◯/◯ と 同じ 数）
        check(bool(mi) and re.fullmatch(r'達成 (\d+)/37\n受け取れるのが 8つ！', mi['n']) and mi['n'].split('\n')[0] == '達成 ' + mi['mp'] and int(mi['mp'].split('/')[0]) >= 8
              and mi['board'] == ['mission-board-3*', 'mission-board-6*', 'mission-board-9*', 'mission-board-12*', 'mission-board-15'] and len(mi['wallp']) == 10 and mi['wallp'][:4] == ['mission-wallp-3*', 'mission-wallp-6*', 'mission-wallp-9*', 'mission-wallp-12']
              and mi['wallp'][-1] == 'mission-wallp-40' and not mi['has45']
              and mi['wall'] == ['mission-wall-8*', 'mission-wall-16', 'mission-wall-25'] and '（11/40）' in mi['last'] and '結果ボードカスタム 3こ解放' in mi['b3'] and '500P' in mi['b3'] and '壁紙 3枚解放' in mi['w3'] and '800P' in mi['w3']
              and 'いま 14こ' in mi['bhint'] and 'いま 11枚' in mi['whint'] and '40枚まで' in mi['whint'] and mi['claims'] == 8 and any('結果ボードカスタム' in h for h in mi['h2']),
              f'ミッションの 窓：「結果ボードカスタムミッション」（3・6・9・12 受け取れる・15 は まだ）・壁紙ミッションの 下に 枚数の 10行（3・6・9 受け取れる・さいごは 40枚・45枚の 行は ない）・帯の 3行は そのまま・上は「達成 n/37」（{mi and {k: mi[k] for k in ("n", "mp", "board", "last", "claims")}}）')
        ov8.locator('#msBoard [data-pt=claim][data-id="mission-board-3"]').click(); p8.wait_for_timeout(800)
        t8b = p8.locator('#toast').inner_text(); u4 = p8.evaluate(BUN)
        ov8.locator('#msWallp [data-pt=claim][data-id="mission-wallp-9"]').click(); p8.wait_for_timeout(800)
        t8w = p8.locator('#toast').inner_text(); u5 = p8.evaluate(BUN); mi2 = p8.evaluate(MSI)
        check('結果ボードカスタム 3こ解放' in t8b and '500P' in t8b and u4['free'] == u3['free'] + 500 and u4['badge'] == '7' and '壁紙 9枚解放' in t8w and '1,500P' in t8w and u5['free'] == u3['free'] + 2000 and u5['total'] == u3['total'] + 2000 and u5['badge'] == '6'
              and mi2['board'][0] == 'mission-board-3' and mi2['wallp'][2] == 'mission-wallp-9' and mi2['n'].endswith('受け取れるのが 6つ！') and mi2['mp'] == mi['mp'] and p8.evaluate("TengelWallet.events().filter(e => /^mission-(board|wallp)-/.test(e.id)).map(e => e.id + ':' + e.amount + ':' + e.bucket).join()") == 'mission-board-3:500:free,mission-wallp-9:1500:free',
              f'窓で 受け取る → 結果ボードカスタム 3こ 500P・壁紙 9枚 1,500P（獲得ポイント）・行は 受け取りずみ・上の 数は 8 → 7 → 6（達成の 数は 受け取っても 同じ）（{t8b}／{t8w}）')
        # 帯の シルバーを 受け取る → 帯も 枚数に 数える（11 → 12枚）→ 壁紙 12枚が 受け取れる（6 − 1 ＋ 1 ＝ 6）
        ov8.locator('#msWall [data-pt=claim][data-id="mission-wall-8"]').click(); p8.wait_for_timeout(800)
        mi3 = p8.evaluate(MSI); u6 = p8.evaluate(BUN)
        check(mi3['wall'][0] == 'mission-wall-8' and mi3['wallp'][3] == 'mission-wallp-12*' and 'いま 12枚' in mi3['whint'] and u6['badge'] == '6' and p8.evaluate("TengelKisekae.usable('silver')"),
              f'シルバー帯を 受け取る → 帯の 1枚も 枚数に 数えて 12枚 → 壁紙 12枚の ミッションが 受け取れる（上の 数は 6 の まま）（{mi3["whint"]}）')
        ov8.locator('[data-ms=close]').click(); p8.wait_for_timeout(300)
        ms8 = p8.locator('#setMission').inner_text()
        check('結果ボードカスタムのミッション' in ms8 and '壁紙 12枚解放' in ms8 and '結果ボードカスタム 6こ解放' in ms8 and p8.locator('#setMission [data-pt=claim][data-id="mission-wallp-12"]').count() == 1 and p8.locator('#setMission .msrow[data-mid="mission-board-3"] .md').inner_text() == '受け取りずみ',
              '設定タブの ミッションにも 壁紙の 枚数と 結果ボードカスタムの 行（受け取りずみ・受け取る）')
        # 返金 → 2つとも 使えなくなる（お得パックが また 出る・受け取った ミッションは そのまま）・購入を復元 → 2つとも もどる（進み具合は そのまま）
        p8.evaluate("window.__nativeEvent('iap', { id: '9001', originalId: 'o9001', product: 'jp.tengel.app.bundle1', kind: 'unlock', date: new Date().toISOString(), revoked: true, revokedAt: new Date().toISOString() })"); p8.wait_for_timeout(900)
        u7 = p8.evaluate(BUN); t8r = p8.locator('#toast').inner_text()
        check(not u7['owned'] and not u7['bOwn'] and not u7['pOwn'] and u7['offer'] and '返金' in t8r and 'お得パック' in t8r and u7['bBuy'] == '¥1,500で買う' and u7['bBun'] == '¥2,200で買う' and u7['pBuy'] == '¥1,500で買う' and u7['pBun'] == '¥2,200で買う'
              and not p8.evaluate("TengelKisekae.usable('pirate')") and u7['free'] == u6['free'] and p8.evaluate("TengelPoints.boardMissions(0, TengelWallet.events())[0].claimed") and u7["badge"] == "",
              f'お得パックの 返金 → 壁紙パックも 結果ボードカスタムも 使えなくなる（買う 所に お得パックが また 出る・受け取った ポイントと ミッションは そのまま）（{t8r}）')
        p8.evaluate("window.__iap.current = [{ id: '9002', originalId: 'o9001', product: 'jp.tengel.app.bundle1', kind: 'unlock', date: new Date().toISOString(), revoked: false }]; 0")
        p8.locator('#setKisekae .kspk [data-ksact=pkrestore]').click(); p8.wait_for_timeout(1000)
        u8 = p8.evaluate(BUN); t8s = p8.locator('#toast').inner_text()
        check(u8['owned'] and u8['bOwn'] and u8['pOwn'] and not u8['offer'] and 'もどしたよ' in t8s and '結果ボードカスタム' in t8s and '壁紙パック' in t8s and u8['bN'] == 14 and u8['pN'] == 11 and u8['badge'] == '6',
              f'購入を復元（壁紙パックの 箱から）→ お得パックで 2つとも もどる（進み具合は そのまま・ミッションも もどる）（{t8s}）')
        p8.screenshot(path=os.path.join(W, 't4', 'native_bundle.png'), full_page=False)
        ctx8.close()
        # ---- 第4.116版（まさちゃん 2026/11/01 07:50「画像読み取りで締切済みレースは締切済みレースに記録される。買い目予約と結果&記録ができない。ポイントは200p消費する。※で注意事項を表示」）：
        #      ページの いまは 2026/10/01 12:00（上の Date）。①発走時刻を すぎた レース（10月1日 09:00）→ 200P は 使う・判定は 出る（「締切済み」の 印）・馬を 選ぶ 行と「買い目を予約」は 出ない・
        #      記録タブの「締切済みレース」に 入る（ミッションに 数えない・月の 一覧と 収支に 入らない・自動バックアップには 入る）・「判定を見る」「消す」 ②画面に「発売締切」→ 同じ ③「締切 18:03」（締切の 時刻）は 締切済みに しない・ふつうに 予約できる ----
        m9 = {}

        def marker9(source, q):
            op, key = q.get('op'), q.get('key')
            if op == 'set': m9[key] = q.get('value', '1'); return {'ok': True}
            if op == 'del': m9.pop(key, None); return {'ok': True}
            v = m9.get(key); return {'ok': True, 'has': v is not None, 'value': v}
        bk9 = {'backup': None}
        ctx9 = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo'); ctx9.add_init_script(FAKE)
        ctx9.expose_binding('__saveBackup', lambda s, t: bk9.__setitem__('backup', t)); ctx9.expose_binding('__marker', marker9)
        p9 = ctx9.new_page(); p9.on('pageerror', lambda e: errs.append('CLOSED ' + str(e)))
        p9.goto(APPURL); p9.wait_for_timeout(1500); gate(p9); p9.wait_for_timeout(700)
        note9 = p9.locator('#ocrNote')
        check(note9.count() == 1 and note9.is_visible() and note9.inner_text().startswith('※') and '締切済み' in note9.inner_text() and '買い目の予約と結果の記録はできない' in note9.inner_text() and '200P' in note9.inner_text()
              and p9.evaluate("(() => { const n = document.querySelector('#ocrNote'), r = document.querySelector('#ocrRow'); return n.getBoundingClientRect().top >= r.getBoundingClientRect().bottom - 1; })()"),
              f'読み取りの ボタンの 下に ※の 注意（締切済みは 予約と 記録が できない・200P は 使う）（{note9.inner_text()[:50]}…）')

        def lines9(r, date=None, start=None, extra=None):
            L = [dict(l, text=l['text'].replace('第9競走', f'第{r}競走').replace('9R', f'{r}R')) for l in OCR_LINES['a_tanfuku_waku']]
            if date or start: L = [dict(l, text=l['text'].replace('10月14日(水)', date or '10月14日(水)').replace('発走 18:05', f'発走 {start}' if start else '発走 18:05')) for l in L]
            if extra: L.append({'text': extra, 'x': 0.62, 'y': 0.955, 'w': 0.3, 'h': 0.03})
            return L
        CL9 = """() => { const q = s => document.querySelector(s), t = s => (q(s) || {}).innerText || ''; const f = JSON.parse(localStorage.getItem('tengel.form') || '{}');
          const bets = [...TengelLocal.mem.bets.values()]; return { total: TengelWallet.total(), counted: TengelWallet.countedN(), msg: t('#ocrMsg'), chips: [...document.querySelectorAll('#result .chip')].map(c => c.innerText), hp: document.querySelectorAll('#result .hprow, #result .omakase, #result [data-hp]').length,
            reserve: document.querySelectorAll('#recCard [data-rsv=reserve], #recCard [data-rsv=give], #recCard [data-rsv=redo]').length, card: t('#recCard'), closed: f.closed || null, r: q('#fR').value, date: f.date, start: f.start, toast: t('#toast'),
            bets: bets.map(b => ({ id: b.id, r: b.r, state: b.rsv ? b.rsv.state : null, by: b.rsv ? b.rsv.by : null, word: b.rsv ? b.rsv.word : null, types: b.types, stake: b.stake, p1: b.p1 })) }; }"""
        # ① 発走時刻を すぎた レース（10月1日 発走 09:00・いまは 12:00）
        p9.evaluate("window.__ocrLines = %s" % json.dumps([lines9(9, date='10月1日(木)', start='09:00')], ensure_ascii=False))
        p9.set_input_files('#ocrFile', [os.path.join(OCR_DIR, 'a_tanfuku_waku.jpg')]); p9.wait_for_timeout(2600)
        c1 = p9.evaluate(CL9)
        print('   締切済み①:', {k: c1[k] for k in ('total', 'counted', 'chips', 'hp', 'reserve', 'closed', 'date', 'start', 'bets')})
        check(c1['total'] == 1300 and '200P 使ったよ' in c1['msg'] and c1['date'] == '2026-10-01' and c1['start'] == '09:00' and c1['r'] == '9', f'発走 09:00 の レース（10月1日）を 読む → 読み込みの 200P は 使う（残り {c1["total"]}P）・日付と 発走時刻が 入る')
        check('締切済みのレース' in c1['msg'] and '発走 09:00 をすぎている' in c1['msg'] and '買い目の予約と結果の記録はできないよ' in c1['msg'] and '200P は使うよ' in c1['msg'], f'読み取りの お知らせに「締切済みのレースだよ（発走 09:00 をすぎている）」と ※の 注意（{c1["msg"][-90:]}）')
        check(bool(c1['closed']) and c1['closed']['by'] == 'time' and c1['closed']['start'] == '09:00' and '締切済み' in c1['chips'] and c1['hp'] == 0 and c1['reserve'] == 0 and '締切済み' in c1['card'] and '発走 09:00 をすぎている' in c1['card'] and '判定は見られるよ' in c1['card'],
              f'判定は 出る（「締切済み」の 印）・馬を 選ぶ 行と お任せ・「買い目を予約」「諦める」は 出ない・買い目の カードは「締切済み」と ※の 注意（{c1["chips"]}／hp {c1["hp"]}／ボタン {c1["reserve"]}）')
        check(len(c1['bets']) == 1 and c1['bets'][0]['state'] == 'closed' and c1['bets'][0]['by'] == 'time' and c1['bets'][0]['r'] == 9 and c1['bets'][0]['types'] == [] and c1['bets'][0]['stake'] is None and c1['bets'][0]['p1'] is None and c1['counted'] == 0
              and '締切済みレース' in c1['toast'] and '「締切済みレース」に入っているよ' in c1['card'],
              f'「締切済みレース」として 記録に 入る（買い目・金額・結果は なし）・ミッションには 数えない（{c1["bets"]}／{c1["toast"]}）')
        id9 = c1['bets'][0]['id']
        bkj = json.loads(bk9['backup'] or '{}')
        check(any(x.get('id') == id9 and (x.get('rsv') or {}).get('state') == 'closed' for x in bkj.get('bets', [])), '締切済みレースも 自動バックアップに 入る')
        # 記録タブ：上の「締切済みレース」に 出る・月の 一覧と 収支には 入らない・「判定を見る」→ 判定画面・「消す」→ 消える
        p9.click('.tabbar button[data-tab=rec]'); p9.wait_for_timeout(700)
        top9 = p9.locator('#recList .rsvtop details[data-k=closed]')
        tt9 = top9.inner_text() if top9.count() else ''
        check(top9.count() == 1 and '締切済みレース（1件）' in tt9 and p9.locator('#recList .rsvtop .lrow').count() == 1 and p9.locator('#recList .dgroup').count() == 0 and '結果待ち 0件' in p9.locator('#recList .rsvtop').inner_text() and p9.locator('#recSummary').inner_text() == '',
              f'記録タブの 上に「締切済みレース（1件）」（予約レースは 0件）・月の 一覧と 収支には 出ない（{tt9[:40]}…）')
        top9.locator('summary').click(); p9.wait_for_timeout(300)
        tt9 = top9.inner_text()
        row9 = top9.locator(f'.lrow[data-id="{id9}"]')
        rt9 = row9.inner_text() if row9.count() else ''
        check(row9.count() == 1 and '9R' in rt9 and '締切済み（発走 09:00 をすぎている）' in rt9 and row9.locator('[data-act=load]').inner_text() == '判定を見る' and row9.locator('[data-act=rdel]').inner_text() == '消す' and row9.locator('.rsvf, .recf, input').count() == 0
              and '買い目の予約と結果の記録はできないよ' in tt9 and '判定だけ残しているよ' in tt9,
              f'行は 9R・締切済み（発走 09:00 をすぎている）・「判定を見る」「消す」だけ（結果の 欄は ない）・欄の 上に ※の 注意（{rt9[:60]}）')
        row9.locator('[data-act=load]').click(); p9.wait_for_timeout(800)
        c2 = p9.evaluate(CL9)
        check(p9.evaluate("document.querySelector('.tabbar button[data-tab=judge]').getAttribute('aria-selected')") == 'true' and c2['r'] == '9' and '締切済み' in c2['chips'] and c2['reserve'] == 0 and '「締切済みレース」に入っているよ' in c2['card'] and c2['total'] == 1300,
              '「判定を見る」→ 判定画面に 戻る（締切済みの 印・予約の ボタンは ない・ポイントは 使わない）')
        p9.click('.tabbar button[data-tab=rec]'); p9.wait_for_timeout(600)
        top9 = p9.locator('#recList .rsvtop details[data-k=closed]'); top9.locator('summary').click(); p9.wait_for_timeout(200)
        row9 = top9.locator(f'.lrow[data-id="{id9}"]')
        row9.locator('[data-act=rdel]').click(); p9.wait_for_timeout(200)
        check(row9.locator('[data-act=rdel]').inner_text() == 'ほんとに消す？', '「消す」→「ほんとに消す？」')
        row9.locator('[data-act=rdel]').click(); p9.wait_for_timeout(900)
        c3 = p9.evaluate(CL9)
        check(len(c3['bets']) == 0 and '締切済みレースから消したよ' in c3['toast'] and p9.locator('#recList .rsvtop details[data-k=closed]').count() == 0, f'もう一度 押す → 締切済みレースから 消える（{c3["toast"]}）')
        p9.click('.tabbar button[data-tab=judge]'); p9.wait_for_timeout(800)
        c4 = p9.evaluate(CL9)
        check(len(c4['bets']) == 0 and '締切済み' in c4['chips'] and c4['reserve'] == 0 and '締切済み' in c4['card'] and '入っているよ' not in c4['card'], '消した あとに 判定画面に 戻っても、入れ直さない（印と ※は そのまま・予約も できない）')
        # ② 画面に「発売締切」（日付は 先の 10月14日）→ 言葉で 締切済み
        p9.evaluate("window.__ocrLines = %s" % json.dumps([lines9(10, extra='発売締切')], ensure_ascii=False))
        p9.set_input_files('#ocrFile', [os.path.join(OCR_DIR, 'a_tanfuku_waku.jpg')]); p9.wait_for_timeout(2600)
        c5 = p9.evaluate(CL9)
        print('   締切済み②:', {k: c5[k] for k in ('total', 'counted', 'chips', 'reserve', 'closed', 'date', 'start', 'bets')})
        check(c5['total'] == 1100 and c5['r'] == '10' and c5['date'] == '2026-10-14' and bool(c5['closed']) and c5['closed']['by'] == 'kw' and c5['closed']['word'] == '発売締切' and '画面に「発売締切」' in c5['msg'] and '締切済み' in c5['chips'] and c5['reserve'] == 0
              and len(c5['bets']) == 1 and c5['bets'][0]['state'] == 'closed' and c5['bets'][0]['by'] == 'kw' and c5['bets'][0]['word'] == '発売締切' and c5['bets'][0]['r'] == 10 and c5['counted'] == 0,
              f'画面に「発売締切」の ある 10R（10月14日・まだ 先）→ 200P は 使う（残り {c5["total"]}P）・「画面に「発売締切」」で 締切済み → 締切済みレースに 入る（{c5["closed"]}）')
        # ③「締切 18:03」（締切の 時刻の 表示）は 締切済みに しない → ふつうに 予約できる・ミッションに 数える
        p9.evaluate("window.__ocrLines = %s" % json.dumps([lines9(11, extra='締切 18:03')], ensure_ascii=False))
        p9.set_input_files('#ocrFile', [os.path.join(OCR_DIR, 'a_tanfuku_waku.jpg')]); p9.wait_for_timeout(2600)
        c6 = p9.evaluate(CL9)
        check(c6['total'] == 900 and c6['r'] == '11' and c6['closed'] is None and '締切済み' not in c6['chips'] and '締切済み' not in c6['msg'] and c6['hp'] >= 1 and p9.locator('#recCard [data-rsv=reserve]').count() == 1 and len(c6['bets']) == 1,
              f'「締切 18:03」（締切の 時刻）の 11R は 締切済みに しない（馬を 選ぶ 行と「買い目を予約」が 出る・残り {c6["total"]}P）')
        p9.locator('#recCard [data-rsv=reserve]').click(); p9.wait_for_timeout(1000)
        c7 = p9.evaluate(CL9)
        b11 = [x for x in c7['bets'] if x['r'] == 11]
        check(len(b11) == 1 and b11[0]['state'] == 'reserved' and c7['counted'] == 1 and len(c7['bets']) == 2, f'11R は ふつうに 予約できる・ミッションに 1レース 数える（締切済みの 10R は 数えない）（{c7["counted"]}）')
        p9.click('.tabbar button[data-tab=rec]'); p9.wait_for_timeout(700)
        rt = p9.locator('#recList .rsvtop').inner_text()
        check('予約レース' in rt and '締切済みレース（1件）' in rt and p9.locator('#recList .rsvtop details[data-k=closed] .lrow').count() == 1 and p9.locator('#recList .dgroup').count() == 0, f'記録タブ：予約レース（11R）と 締切済みレース（10R）が 分かれて 出る（{rt[:60]}…）')
        p9.locator('#recList .rsvtop details[data-k=closed] summary').click(); p9.wait_for_timeout(300)
        p9.screenshot(path=os.path.join(W, 't4', 'native_closed_rec.png'), full_page=False)
        p9.click('.tabbar button[data-tab=judge]'); p9.wait_for_timeout(500)
        p9.evaluate("window.__ocrLines = %s" % json.dumps([lines9(10, extra='発売締切')], ensure_ascii=False))
        p9.set_input_files('#ocrFile', [os.path.join(OCR_DIR, 'a_tanfuku_waku.jpg')]); p9.wait_for_timeout(2200)
        c8 = p9.evaluate(CL9)
        check(c8['total'] == 900 and c8['r'] == '10' and '0P' in c8['msg'] and '締切済み' in c8['chips'] and len(c8['bets']) == 2, '締切済みの 10R を 読み直しても 0P（同じ レース）・締切済みの まま')
        p9.screenshot(path=os.path.join(W, 't4', 'native_closed_judge.png'), full_page=False)
        ctx9.close()
        # Web版（ブラウザ）には ※の 注意を 出さない（締切済みの 仕組みは App Store版だけ）→ 下の ctx2 で 見る
        # ---- 第4.122版（まさちゃん 2026/11/04 07:36「予約済み結果待ちレースの項目を作成する。予約したタップすれば買い目が一目で分かるように表示して！」
        #      「買い目、自己入力機能を追加する。判定の層とズレていても、自己入力を押すと、どの番号でも選択できるようにする」「結果、層の欄は自己入力の項目を増やす」
        #      「枠連、枠複を自動で割り出せるようにする！」）：上の帯の「結果待ち」→ 窓（ゾーンごとの 1着・2着・3着の 馬・点数・組）・買い目の カードの「✏️ 自己入力」・
        #      層別の収支の「自己入力」の 行・判定の ゾーンごとの 枠（枠複・枠単を 解放した 人だけ） ----
        mR = {}

        def markerR(source, q):
            op, key = q.get('op'), q.get('key')
            if op == 'set': mR[key] = q.get('value', '1'); return {'ok': True}
            if op == 'del': mR.pop(key, None); return {'ok': True}
            v = mR.get(key); return {'ok': True, 'has': v is not None, 'value': v}
        ctxR = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP'); ctxR.add_init_script(FAKE)
        ctxR.expose_binding('__saveBackup', lambda s, t: None); ctxR.expose_binding('__marker', markerR)
        ctxR.add_init_script("if (!sessionStorage.getItem('seeded')) { localStorage.setItem('tengel.form', %s); sessionStorage.setItem('seeded', '1'); }" % json.dumps(json.dumps(form, ensure_ascii=False)))
        pR = ctxR.new_page(); pR.on('pageerror', lambda e: errs.append('RSV ' + str(e)))
        pR.goto(APPURL); pR.wait_for_timeout(1500); gate(pR); pR.wait_for_timeout(900)
        HB = """() => { const b = document.querySelector('#rsvBtn'), m = document.querySelector('#msBtn'); if (!b || !m) return null; const r = b.getBoundingClientRect(), q = m.getBoundingClientRect();
          return { t: b.innerText.replace(/\\s+/g, ''), has: b.classList.contains('has'), svg: !!b.querySelector('svg'), top: !!b.closest('header.top'), next: (b.nextElementSibling || {}).id, row: Math.abs(r.top - q.top) < 6 && r.right <= q.left + 1, al: b.getAttribute('aria-label') }; }"""
        h0 = pR.evaluate(HB)
        check(bool(h0) and h0['t'] == '結果待ち0' and not h0['has'] and h0['svg'] and h0['top'] and h0['next'] == 'msBtn' and h0['row'] and '0件' in h0['al'], f'上の帯の「ミッション」の 左に「結果待ち 0」（{h0}）')
        pR.click('#rsvBtn'); pR.wait_for_timeout(400)
        o0 = pR.locator('#rsvOv')
        check(o0.count() == 1 and o0.get_attribute('role') == 'dialog' and '0件' in o0.inner_text() and '結果待ちの レースは ないよ' in o0.inner_text() and pR.evaluate("document.documentElement.classList.contains('mson')"), '押すと 窓「予約済み・結果待ち」（まだ 0件）')
        pR.keyboard.press('Escape'); pR.wait_for_timeout(250)
        check(pR.locator('#rsvOv').count() == 0 and not pR.evaluate("document.documentElement.classList.contains('mson')") and pR.evaluate("document.activeElement && document.activeElement.id") == 'rsvBtn', 'Esc で 窓を 閉じる（「結果待ち」に もどる）')
        # 自己入力：判定の ゾーンと 関係なく どの 番号でも（B層の 8R：ゾーンは 中穴→人気・人気→大穴）
        cR = pR.locator('#recCard')
        sb = cR.locator('[data-k=rzones] [data-k=rself]')
        check(sb.count() == 1 and sb.get_attribute('aria-pressed') == 'false' and '自己入力' in sb.inner_text() and cR.locator('.selfpk').count() == 0, '買い目の カード：使うゾーンの ならびに「✏️ 自己入力」（はじめは オフ）')
        sb.click(); pR.wait_for_timeout(300)
        pk = cR.locator('.selfpk')
        check(pk.count() == 1 and cR.locator('[data-k=rself]').get_attribute('aria-pressed') == 'true' and pk.locator('.spr').count() == 3 and [pk.locator('.spr').nth(i).get_attribute('data-side') for i in range(3)] == ['a', 'b', 't']
              and pk.locator('.spr[data-side=a] button').count() == 14 and pk.locator('.spr button[aria-pressed=true]').count() == 0 and 'まだ 選んで いないよ' in pk.inner_text() and pk.locator('[data-k=rpclear]').is_disabled(),
              '押すと 自己入力の 欄：1着・2着・3着（馬単・3連単）× 14頭 ぜんぶの 番号・はじめは 何も 選んで いない')
        for side, nos in (('a', [3, 9]), ('b', [1, 6, 12])):
            for no in nos:
                cR.locator(f'.selfpk .spr[data-side={side}] button[data-no="{no}"]').click(); pR.wait_for_timeout(120)
        pk = cR.locator('.selfpk')
        check('1着 3・9／2着 1・6・12' in pk.inner_text() and '3連単は 3着も 選ぶと 入るよ' in pk.locator('.spw').inner_text() and pR.evaluate("JSON.stringify(JSON.parse(localStorage.getItem('tengel.form')).self)") == '{"a":[3,9],"b":[1,6,12],"t":[]}',
              f'ゾーンに ない 馬（3＝10番人気・9・12＝13番人気）も 選べる・選んだ 馬の まとめ・3着が ない 間は「3連単は 3着も 選ぶと 入るよ」（{pk.inner_text()[-70:]}）')
        cR.locator('.selfpk .spr[data-side=t] button[data-no="13"]').click(); pR.wait_for_timeout(150)
        check(cR.locator('.selfpk .spw').count() == 0 and '3着 13' in cR.locator('.selfpk .spf').inner_text(), '3着も 選ぶと 注意が 消える')
        pR.screenshot(path=os.path.join(W, 't4', 'native_self_pick.png'), full_page=True)
        cR.locator('details[data-k=betsee] summary').click(); pR.wait_for_timeout(250)
        blR = cR.locator('.betlist').inner_text()
        check('3→1' in blR and '9→12' in blR and '3→6→13' in blR and '9→12→13' in blR, '買い目の 組に 自己入力の 組が 入る（馬単 3→1・9→12、3連単 3→6→13・9→12→13 など）')
        cR.locator('[data-rsv=reserve]').click(); pR.wait_for_timeout(1200)
        rR = pR.evaluate("() => { const b = [...TengelLocal.mem.bets.values()].find(x => x.r === 8); if (!b) return null; const rs = b.rsv; return { id: b.id, state: rs.state, zones: rs.zones, self: rs.self, legs: rs.legs.map(l => l.k), um: rs.bets['馬単'].length, sr: rs.bets['3連単'].length, pts: rs.points, stake: b.stake, buyZ: b.buyZ }; }")
        check(bool(rR) and rR['state'] == 'reserved' and rR['zones'] == ['中穴→人気', '人気→大穴', '自己入力'] and rR['self'] == {'a': [3, 9], 'b': [1, 6, 12], 't': [13]} and rR['legs'] == rR['zones'] and rR['um'] == 24 and rR['sr'] == 87 and rR['pts'] == 111 and rR['stake'] == 11100 and rR['buyZ'] == rR['zones'],
              f'「買い目を予約」→ 記録に 自己入力の 馬（rsv.self）と ゾーンごとの 馬（rsv.legs）・馬単 24点（ゾーン 18＋自己入力 6）・3連単 87点（ゾーン 81＋自己入力 6）（{rR}）')
        h1 = pR.evaluate(HB)
        check(h1['t'] == '結果待ち1' and h1['has'] and '1件' in h1['al'], f'予約すると 上の帯が「結果待ち 1」（{h1["t"]}）')
        pR.click('#rsvBtn'); pR.wait_for_timeout(500)
        ovR = pR.locator('#rsvOv'); otR = ovR.inner_text(); lgR = ovR.locator('.rvleg')
        check(ovR.locator('.rvcard').count() == 1 and ovR.locator('.msn').inner_text() == '1件' and '8R' in otR and 'はなまる特別' in otR and '発走 15:40' in otR and lgR.count() == 3
              and lgR.nth(0).locator('.rvl').inner_text() == '第1\u3000中穴→人気' and lgR.nth(2).locator('.rvl.self').inner_text() == '自己入力'
              and [lgR.nth(0).locator('.rvs').nth(i).locator('.num').count() for i in range(3)] == [3, 3, 6] and [x.inner_text() for x in lgR.nth(2).locator('.rvs').nth(0).locator('.num').all()] == ['3', '9'] and lgR.nth(2).locator('.rvs').count() == 3
              and [x.inner_text() for x in lgR.nth(0).locator('.rvsl').all()] == ['1着', '2着', '3着'] and '馬単 24点・3連単 87点' in otR and '合計 111点' in otR and ovR.locator('details.rvd').count() == 1 and not ovR.locator('details.rvd').evaluate('d => d.open'),
              f'「結果待ち」を 押すと 窓：レースごとに ゾーン（と 自己入力）の 1着・2着・3着の 馬（枠の 色）・点数の まとめ・「組を見る」（{otR[:150]}…）')
        pR.screenshot(path=os.path.join(W, 't4', 'native_rsv_ov.png'), full_page=False)
        ovR.locator('details.rvd summary').click(); pR.wait_for_timeout(200)
        check('3→1' in ovR.locator('details.rvd .betlist').inner_text(), '「組を見る」で 券種ごとの 組（自己入力の 組も）')
        ovR.locator('[data-rv=result]').click(); pR.wait_for_timeout(900)
        check(pR.locator('#rsvOv').count() == 0 and pR.locator('#v-rec').is_visible() and pR.locator(f'#recList .lrow[data-id="{rR["id"]}"] .rsvf').count() == 1, '「結果を入れる（記録タブ）」→ 窓が 閉じて 記録タブで その レースの 結果入力が 開く')
        check('自己入力（1着 3・9／2着 1・6・12／3着 13）' in pR.locator(f'#recList .lrow[data-id="{rR["id"]}"]').inner_text(), '記録の 行にも「自己入力（1着 …／2着 …／3着 …）」')
        # 層別の収支：自己入力を 含む レースは A・B・C に 入れずに「自己入力」の 行
        pR.click('.tabbar button[data-tab=stats]'); pR.wait_for_timeout(900)
        mo = pR.evaluate("""() => { const c = [...document.querySelectorAll('#moneyBody .card')].find(x => x.querySelector('h2') && x.querySelector('h2').innerText.startsWith('層別')); if (!c) return null;
          const rows = [...c.querySelectorAll('tbody tr')].map(r => [...r.children].map(td => td.innerText.trim().replace(/\\s+/g, ' '))); return { rows, hint: (c.querySelector('.hint') || {}).innerText || '' }; }""")
        rowsR = {r[0]: r for r in (mo or {}).get('rows', [])}
        check(bool(mo) and rowsR.get('自 自己入力', [None, None])[1] == '1' and rowsR.get('B 警戒', [None, None])[1] == '0' and rowsR['自 自己入力'][4] == '11,100' and '自己入力' in mo['hint'],
              f'層別の収支に「自己入力」の 行（購入 1・購入額 11,100）・B層の 行には 入らない・下に 説明（{mo and mo["rows"]}）')
        # 枠：枠複・枠単を Pカスタムで 解放した 人だけ、判定の ゾーンごとに 枠と 組
        pR.click('.tabbar button[data-tab=judge]'); pR.wait_for_timeout(500)
        check(pR.locator('#result [data-k=zwaku]').count() == 0, '解放する 前は 判定の ゾーンに 枠が 出ない')
        pR.click('.tabbar button[data-tab=set]'); pR.wait_for_timeout(400)
        for tp in ('枠複', '枠単'):
            pR.locator(f'#setCustom [data-pt=unlock1][data-key="type:{tp}"]').click(); pR.wait_for_timeout(150)
            pR.locator(f'#setCustom [data-pt=unlock2][data-key="type:{tp}"]').click(); pR.wait_for_timeout(500)
        pR.click('.tabbar button[data-tab=judge]'); pR.wait_for_timeout(600)
        zwR = pR.locator('#result [data-k=zwaku]')
        zr = [{'w': [[x.inner_text() for x in z.locator('.zw1').first.locator('.num').all()]], 'fk': z.locator('[data-t=枠複] .zwc').inner_text(), 'ft': z.locator('[data-t=枠単] .zwc').inner_text()} for z in zwR.all()]
        z0, z1 = (zr + [{}, {}])[:2]
        check(zwR.count() == 2 and z0.get('w') == [['5', '3', '1', '4', '2', '6']] and z0.get('fk') == '1-2・1-4・1-6・2-3・2-5・3-4・3-6・4-5・5-6' and z0.get('ft') == '1→2・1→4・1→6・3→2・3→4・3→6・5→2・5→4・5→6',
              f'設定タブで 解放して 判定タブに もどると ゾーンごとに 枠：第1 中穴→人気（7・4・1 → 6・2・10）＝ 枠 5・3・1 → 4・2・6・枠複 9つ・枠単 9つ（14頭の 枠）（{z0 or "なし"}）')
        check(z1.get('fk') == '2-4・2-6・2-7・4-4・4-6・4-7・6-6・6-7' and z1.get('ft') == '2→4・2→6・2→7・4→4・4→6・4→7・6→4・6→6・6→7' and zwR.count() and '通り' not in zwR.first.inner_text() and '点' not in pR.locator('#result').inner_text(),
              f'第2 人気→大穴：同じ 枠の 2頭（6と5＝4枠・10と9＝6枠）は 4-4・6-6 も 入る・通り数／点数は 判定の 画面に 出さない（{z1.get("fk")}）')
        if zwR.count():
            zwR.first.scroll_into_view_if_needed(); pR.wait_for_timeout(200)
            pR.locator('#result .zone').first.screenshot(path=os.path.join(W, 't4', 'native_zwaku.png'))
        ctxR.close()
        # ---- 第4.59版：テスト版（TENGEL_TEST=1）：はじめから 10,000P・テスト版の 印・設定の いちばん上に「テスト版の道具」（10,000P 足す・的中ボタンを ためす）----
        store['markers'].clear()
        ctx5 = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP'); ctx5.add_init_script(FAKE)
        ctx5.expose_binding('__saveBackup', lambda s, t: None); ctx5.expose_binding('__marker', marker)
        p5 = ctx5.new_page(); p5.on('pageerror', lambda e: errs.append('TEST ' + str(e)))
        p5.goto(TESTURL); p5.wait_for_timeout(1500); gate(p5); p5.wait_for_timeout(700)
        tb = p5.evaluate("(() => ({ total: TengelWallet.total(), tag: (document.querySelector('#testTag') || {}).innerText, pill: document.querySelector('#ptsPill').innerText.replace(/\\s+/g, ' '), first: document.querySelector('#v-set > .card').id, btns: [...document.querySelectorAll('#setTest [data-test=fx]')].map(x => x.innerText), kinds: [...document.querySelectorAll('#setTest [data-test=fx]')].map(x => x.dataset.kind), ev: TengelWallet.events().map(e => e.id + ':' + e.amount) }))()")
        check(tb['total'] == 10000 and tb['tag'] == 'テスト版' and tb['pill'] == 'ポイント 10,000P' and tb['first'] == 'setTest' and tb['btns'] == ['的中', 'デカ的中', 'ノーマルど的中', '極ど的中', 'ハズレ', 'プレミアムど的中', '超神様的中', '超プレミアム神様的中', '神様極的中'] and tb['kinds'] == ['hit', 'big', 'nd', 'sd', 'miss', 'pc', 'sgd', 'spg', 'gk'] and tb['ev'] == ['gift-first:1500', 'gift-test:8500'],
              f'テスト版：はじめから ちょうど 10,000P（初回の 1,500P＋テスト版の 8,500P）・上の帯に「テスト版」の 印・設定の いちばん上に「テスト版の道具」（的中ボタン 9こ：第4.86版 隠れど的中・超プレミアムど的中・神様的中は なし・第4.117版 神様極的中）（{tb}）')
        p5.click('.tabbar button[data-tab=set]'); p5.wait_for_timeout(300)
        p5.locator('#setTest [data-test=pts]').click(); p5.wait_for_timeout(400)
        check(p5.evaluate('TengelWallet.total()') == 20000 and p5.locator('#ptsPill').inner_text().replace('\n', ' ') == 'ポイント 20,000P', 'テスト版：「10,000P 足す」で 20,000P（上の帯の 合計も かわる）')
        # 第4.114版：テスト版の 道具「お得パック：買ったことにする」→ 壁紙パックも 結果ボードカスタムも 持って いる（App Store の 買い物は しない）
        p5.locator('#setTest [data-test=uown]').click(); p5.wait_for_timeout(600)
        ub = p5.evaluate("({ own: TengelWallet.bundle.owned(), b: TengelWallet.board.info().owned, p: TengelKisekae.pack().owned, st: document.querySelector('#testBundle').innerText, toast: document.querySelector('#toast').innerText, buy: document.querySelectorAll('#setBoard [data-bcact=buy], #setBoard [data-bcact=bundle], #setKisekae .kspk [data-ksact=pkbuy], #setKisekae .kspk [data-ksact=bundle]').length })")
        check(ub['own'] and ub['b'] and ub['p'] and ub['st'] == '買った' and 'お得パック' in ub['toast'] and ub['buy'] == 0 and p5.evaluate('TengelWallet.total()') == 20000, f'第4.114版：テスト版の「お得パック：買ったことにする」→ 2つとも 持って いる（買うの ボタンは 消える・ポイントは そのまま）（{ub}）')
        p5.locator('#setTest [data-test=fx][data-kind=sgd]').click(); p5.wait_for_timeout(500)
        check(p5.locator('#fxOv .ov.fz .pbox.rbw .push .rbf').count() == 1 and p5.evaluate("TengelFx.current().kind") == 'sgd', 'テスト版：「超神様的中」を 押すと 虹色の PUSH（超神様的中）が 出る（くじは ひかない）')
        p5.evaluate('TengelFx.close()'); p5.wait_for_timeout(200)
        for kd, nm in (('nd', 'ノーマルど的中'), ('sd', '極ど的中'), ('gk', '神様極的中')):   # 第4.81版：ノーマルど的中・極ど的中の ボタン（くじは ひかない）・第4.117版：神様極的中
            p5.locator(f'#setTest [data-test=fx][data-kind={kd}]').click(); p5.wait_for_timeout(500)
            check(p5.evaluate("TengelFx.current() && TengelFx.current().kind") == kd and p5.locator('#fxOv .ov.fz .pbox .push').count() >= 1 and (kd != 'gk' or (p5.locator('#fxOv .ov.fz .pbox.rbw .push .rbf').count() == 1 and p5.evaluate('TengelFx.current().pz') == 1.6)),
                  f'テスト版：「{nm}」を 押すと {nm}（{kd}）の PUSH が 出る（くじは ひかない{"・虹色の 1.6倍" if kd == "gk" else ""}）')
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
        #   第4.123版：テンゲルデータの ときは 実測を 出さない → マザーデータ①（2つ目）に ファイルの データを 入れて 使う
        p5.click('.tabbar button[data-tab=stats]'); p5.wait_for_timeout(800)
        fx46 = p5.evaluate("(() => ({ body: document.querySelector('#statsBody').innerText, per: document.querySelector('#perChips').hidden, title: document.querySelector('#motherTitle').innerText, tables: document.querySelectorAll('#statsBody table').length }))()")
        check(fx46['per'] and fx46['tables'] == 0 and 'テンゲルデータの実測' in fx46['title'] and '中身（レースの数・実測①〜⑦）は見られないよ' in fx46['body'] and not re.search(r'\d+走', fx46['body']), f'第4.123版：テンゲルデータの ときは 実測（①〜⑦）と 見直し基準を 出さない（期間の ボタンも かくす）（{fx46}）')
        p5.evaluate("(async () => { const L = TengelLocal.slots; const rows = L.rows(1).map(r => Object.assign({}, r, { id: r.id.replace('-m1-', '-m2-'), src: undefined })); await L.replace(2, rows, { source: 'excel', file: 'テスト.xlsx' }); await L.setActive(2); })()"); p5.wait_for_timeout(1500)
        p5.click('.tabbar button[data-tab=judge]'); p5.wait_for_timeout(300); p5.click('.tabbar button[data-tab=stats]'); p5.wait_for_timeout(1000)
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
        ksid = p5.evaluate("(() => { const t = [...document.querySelectorAll('#setKisekae .kst.lock')].find(e => (TengelKisekae.list().find(x => x.id === e.dataset.ks) || {}).price); return t ? t.dataset.ks : null; })()")   # ポイントで 解放する 壁紙（壁紙パックの カギは 買う）
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
        # ---- 第4.117版・第4.118版：神様極的中の 数え方（src.html の godCount → TengelFx.show の godN）。記録の 画面で 結果を 決める（ふつうの 流れ）----
        #   結果を 決めた さいごの 50レース（日付と 発走時刻の 順・この レースまで・この レースも 入れる）の 中の G・M の レース（第4.118版：前は 30レース・神様の 条件）。2つ以上 → 神様極的中。
        #   予約中・結果待ち・諦めた・締切済み・中止は 入れない・あとの 日付（同じ 日の あとの 発走）の レースも 入れない・
        #   的中エフェクト オフで 決めた レース（rsv.fx なし）も 記録から 決め直して 数える
        import copy as _copy
        mG = {}

        def markerG(source, q):
            op, key = q.get('op'), q.get('key')
            if op == 'set': mG[key] = q.get('value', '1'); return {'ok': True}
            if op == 'del': mG.pop(key, None); return {'ok': True}
            v = mG.get(key); return {'ok': True, 'has': v is not None, 'value': v}
        ctxG = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP'); ctxG.add_init_script(FAKE)
        ctxG.expose_binding('__saveBackup', lambda s, t: None); ctxG.expose_binding('__marker', markerG)
        pG = ctxG.new_page(); pG.on('pageerror', lambda e: errs.append('GK ' + str(e)))
        pG.goto(APPURL); pG.wait_for_timeout(1500); gate(pG); pG.wait_for_timeout(700)
        pG.evaluate("(() => { const o = TengelFx.show; TengelFx.show = s => { window.__gkSpec = JSON.parse(JSON.stringify(s)); return o(s); }; })()")
        pG.click('.tabbar button[data-tab=rec]'); pG.wait_for_timeout(600)
        H14 = [{'no': i, 'tan': round(i + 0.4, 1), 'fuku': None} for i in range(1, 15)]   # 馬番＝人気（11＝超大穴・8＝大穴）

        def grec(date, r, start, state, tri=(11, 8, 2), abandoned=False, fx=None, types=('3連単', '馬単')):
            # 第4.118版：3連単（3頭）と 馬単（はじめの 2頭）を 買って、結果が その 3頭 → 2つとも 当たり（M）。11・8・2 なら G・M
            d = _copy.deepcopy(b9c)
            for k in ('mem', 'pid', 'mslot', 'mid', 'umatanPay', 'sanrenPay'):
                d.pop(k, None)
            bets = {t: [list(tri) if t == '3連単' else list(tri[:2])] for t in types}
            d.update(id=date.replace('-', '') + '-oi-' + str(r).zfill(2), date=date, r=r, n=14, horses=H14, start=start, rname='神様テスト', types=list(types), amt={t: {'stake': 100, 'payout': None} for t in types}, stake=100 * len(types), payout=None, other='',
                     p1=None, p2=None, p3=None, n1=None, n2=None, n3=None)
            rs = {'state': state, 'at': '2026-09-01T00:00:00.000Z', 'key': f'{date}|神様テスト|1400|{start}', 'start': start}
            if state == 'closed':
                rs.update(by='time', word='')
            if state in ('given', 'closed'):
                d.update(types=[], amt={}, stake=None)
            else:
                rs.update(types=list(types), zones=_copy.deepcopy(b9c['rsv'].get('zones')), bets=bets, points=len(types), hp=None)
                if state == 'done':
                    jst = '返還' if abandoned else '的中'
                    rs.update(result={'p': [[], [], []] if abandoned else [[x] for x in tri], 'cancel': [], 'abandoned': abandoned, 'pay': {}}, judged={'state': jst, 'per': {t: jst for t in types}})
                    if fx:
                        rs['fx'] = fx
            d['rsv'] = rs
            return d
        CUR = grec('2026-09-30', 11, '20:10', 'reserved')
        G1 = grec('2026-09-10', 5, '15:00', 'done', fx='spg')                                     # G・M（3連単 11・8・2 ＋ 馬単 11→8）
        GX = grec('2026-09-15', 1, '12:00', 'done', fx='sgd', types=('3連単',))                   # G だけ（M で ない：3連単だけ）→ 数えない
        NS = [grec('2026-09-20', i + 1, '', 'done', tri=(1, 2, 3)) for i in range(48)]            # G で ない（的中・M）48レース（09/20・発走時刻なし＝その日の さいご）

        def gcycle(put, cur=CUR, rnd=0.99, shown=True):
            pG.evaluate("(a) => { TengelFx._rand = () => a; }", rnd)
            pG.evaluate("(l) => TengelLocal.putBets(l)", put + [cur]); pG.wait_for_timeout(500)
            pG.click('#rFilters [data-f=all]'); pG.wait_for_timeout(400)
            if pG.locator(f'#recList .rsvf[data-id="{cur["id"]}"]').count() == 0:
                pG.locator(f'#recList .rsvtop .lrow[data-id="{cur["id"]}"] .lmain').click(); pG.wait_for_timeout(500)
            pG.evaluate("(id) => { const f = document.querySelector('#recList .rsvf[data-id=\"' + id + '\"]'); [['p1', '11'], ['p2', '8'], ['p3', '2']].forEach(([k, v]) => { const i = f.querySelector('[data-k=' + k + ']'); i.value = v; i.dispatchEvent(new Event('input', { bubbles: true })); }); window.__gkSpec = null; }", cur['id'])
            pG.locator(f'#recList .rsvf[data-id="{cur["id"]}"] [data-act=rsave]').click()
            # 保存は 記録 → お知らせ → 連続の 数 → 演出 の 順（重い ときは 1秒より かかる）：演出が 出るまで（オフなら 記録が 決まって 少し あと まで）待つ
            if shown:
                pG.wait_for_function("() => window.__gkSpec !== null && !!TengelFx.current()", timeout=20000)
            else:
                pG.wait_for_function("(id) => { const b = TengelLocal.mem.bets.get(id); return !!(b && b.rsv && b.rsv.state === 'done'); }", arg=cur['id'], timeout=20000); pG.wait_for_timeout(2000)
            pG.wait_for_timeout(300)
            sp, cu = pG.evaluate('window.__gkSpec'), pG.evaluate('TengelFx.current()')
            sv = pG.evaluate("(id) => TengelLocal.mem.bets.get(id)", cur['id'])
            pG.evaluate('TengelFx.close()'); pG.wait_for_timeout(300)
            return (sp or {}).get('godN'), (cu or {}).get('kind'), (sv or {}).get('rsv', {}).get('state'), (sv or {}).get('rsv', {}).get('fx')
        r1 = gcycle(NS[:3] + [GX], rnd=0)
        check(r1 == (1, 'spg', 'done', 'spg'), f'神様極的中の 数え方（第4.118版）：G・M は この レースだけ（ほかは 的中 3レースと G だけ（3連単だけ）の 09/15）→ godN 1 → 超プレミアム神様的中（乱数 0 でも くじなし）（{r1}）')
        r2 = gcycle([G1], rnd=0)
        check(r2 == (2, 'gk', 'done', 'gk'), f'09/10 の G・M の レース＋この レース → godN 2 → 神様極的中・記録に 出した 印 gk（{r2}）')
        r3 = gcycle(NS[3:])
        check(r3 == (1, 'spg', 'done', 'spg'), f'あいだに G・M で ない 49レース（的中 48・09/15 の G だけ）→ 09/10 の G・M の レースは 51レース目で 外れる → godN 1 → 超プレミアム神様的中（{r3}）')
        RS_, GV_ = grec('2026-09-25', 1, '18:00', 'reserved'), grec('2026-09-25', 2, '18:30', 'given')
        r4 = gcycle([grec('2026-09-20', 1, '', 'closed'), RS_, GV_])
        check(r4 == (2, 'gk', 'done', 'gk'), f'あいだの 1つを 締切済みに（ほかに 予約中・諦めた）→ 数えない ので 09/10 の G・M の レースが ちょうど 50レース目 → godN 2 → 神様極的中（{r4}）')
        r4b = gcycle([NS[0], grec('2026-09-20', 2, '', 'done', tri=(1, 2, 3), abandoned=True)])
        check(r4b == (2, 'gk', 'done', 'gk'), f'締切済みを もどして、ほかの 1つを 中止（全部 返還）に → 中止は 数えない → 50レース目 → godN 2 → 神様極的中（{r4b}）')
        r4c = gcycle([NS[1]])
        check(r4c == (1, 'spg', 'done', 'spg'), f'中止を もどす → また 51レース目で 外れる → godN 1（{r4c}）')
        GF, GSL = grec('2026-10-01', 1, '10:00', 'done'), grec('2026-09-30', 12, '20:45', 'done')
        r5 = gcycle([grec('2026-09-10', 5, '15:00', 'given'), GF, GSL])
        check(r5 == (1, 'spg', 'done', 'spg'), f'あとの レース（10/01・同じ 日の あとの 発走 20:45）の G・M は 数えない → godN 1（{r5}）')
        pG.evaluate("TengelFx.set({ effects: false })")
        r6 = gcycle([], shown=False)
        check(r6 == (None, None, 'done', None) and pG.locator('#fxOv').count() == 0, f'的中エフェクト オフ：演出も ボードも 出さず（show は 呼ばない）・記録は 決まる（出した 印なし）（{r6}）')
        pG.evaluate("TengelFx.set({ effects: true })")
        CUR2 = grec('2026-09-30', 13, '21:20', 'reserved')
        r7 = gcycle([grec('2026-09-30', 12, '20:45', 'given')], cur=CUR2)
        check(r7 == (2, 'gk', 'done', 'gk'), f'的中エフェクト オフで 決めた G・M の レース（出した 印なし）も 記録から 決め直して 数える → godN 2 → 神様極的中（{r7}）')
        pG.evaluate("(id) => { const d = JSON.parse(JSON.stringify(TengelLocal.mem.bets.get(id))); d.mem = { at: new Date().toISOString() }; return TengelLocal.putBets([d]); }", CUR2['id']); pG.wait_for_timeout(500)
        pG.click('#rFilters [data-f=all]'); pG.wait_for_timeout(500)
        mr = pG.locator(f'#recList .memtop .memrow[data-mid="{CUR2["id"]}"]')
        mrs = mr.locator('.s').inner_text() if mr.count() else ''
        check(mr.count() == 1 and mrs.startswith('神様極的中'), f'思い出の レース：神様極的中の レースは「神様極的中」（{mrs[:30]}）')
        mr.locator('.lmain').click(); pG.wait_for_timeout(1200)
        mo = pG.evaluate("(() => { const o = document.querySelector('#fxOv'); const z = o && o.querySelector('.rb .zrib'); return o ? { cls: o.className, frame: !!o.querySelector('.fxs.mem .ov.miss.quiet.mem.f-god'), t: o.querySelector('.rb.fz .bh').innerText, rib: z ? z.innerText.replace(/\\s+/g, '') : '', push: o.querySelectorAll('.push').length, vid: document.querySelectorAll('#fxOv video').length, dim: getComputedStyle(o.querySelector('.ov.mem .dim')).backgroundImage.slice(0, 15), info: TengelFx.memInfo() } : null; })()")
        check(mo is not None and 'k-gk' in mo['cls'] and mo['frame'] and mo['t'] == '神様極的中！！！' and mo['rib'] == '超大穴11大穴8が3連単に！' and mo['push'] == 0 and mo['vid'] == 0 and mo['dim'].startswith('radial-gradient') and mo['info'] == {'v': 'a', 'frame': 'god'},
              f'神様極的中の 思い出ボード：神様馬の わく（f-god）・見出し「神様極的中！！！」・帯は 超大穴と 大穴（PUSH・動画なし）（{mo}）')
        pG.evaluate('TengelFx.close()')
        ctxG.close()
        # ---- 第4.139版：上限 99,999P・あずかりポイント（まさちゃん 11/10 11:46「ポイントの上限は、99999までにして！」「事前に、99999まで入るようにして作ってみて！」・
        #      12:27「99999pに到達しながらサブスクに入っている人は、ミッションのところで超えてしまっているポイントが溜まっていくようにして！で、使って減った分は、溜まってるポイントから補充できるようによろしく！」）----
        mC = {}
        def markerC(source, q):
            op, key = q.get('op'), q.get('key')
            if op == 'set': mC[key] = q.get('value', '1'); return {'ok': True}
            if op == 'del': mC.pop(key, None); return {'ok': True}
            v = mC.get(key); return {'ok': True, 'has': v is not None, 'value': v}
        ctxC = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP'); ctxC.add_init_script(FAKE)
        ctxC.expose_binding('__saveBackup', lambda s, t: None); ctxC.expose_binding('__marker', markerC)
        pC = ctxC.new_page(); pC.on('pageerror', lambda e: errs.append('CAP ' + str(e)))
        pC.goto(TESTURL); pC.wait_for_timeout(1500); gate(pC); pC.wait_for_timeout(700)
        pC.click('.tabbar button[data-tab=set]'); pC.wait_for_timeout(300)
        CI = """() => { const b = TengelWallet.balance(), t = document.querySelector('#toast'), m = document.querySelector('#msBtn'), bd = m.querySelector('.mbd');
          return { total: b.total, pack: b.paid_pack, sub: b.paid_sub, free: b.free, hold: TengelWallet.hold(), avail: TengelWallet.avail(), pill: document.querySelector('#ptsPill').innerText.replace(/\\s+/g, ' '),
            badge: bd ? bd.innerText : '', toast: t && !t.hidden ? t.textContent : '' }; }"""
        pC.locator('#setTest [data-test=pts100]').click(); pC.wait_for_timeout(500)
        c1 = pC.evaluate(CI)
        hg = pC.evaluate("""() => { const R = s => document.querySelector(s).getBoundingClientRect(); const p = R('#ptsPill'), v = R('#ptsPill .pv'), l = R('#ptsPill .pl'), m = R('#manBtn'), br = R('header.top .brand'), rv = R('#rsvBtn');
          return { row: Math.abs(p.top - m.top) < 8 && Math.abs(p.top - br.top) < 12, inside: l.left >= p.left + 3 && v.right <= p.right - 3 && l.right <= v.left, manR: +(innerWidth - m.right).toFixed(1), pL: +p.left.toFixed(1), rvL: +rv.left.toFixed(1), cls: document.querySelector('#ptsPill').className, sw: document.documentElement.scrollWidth }; }""")
        check(c1['total'] == 99999 and c1['pill'] == 'ポイント 99,999P' and c1['hold']['total'] == 0 and '89,999P' in c1['toast'] and pC.evaluate('TengelPoints.CAP') == 99999,
              f'テスト版：「上限（99,999P）まで 足す」→ ちょうど 99,999P（上の帯「ポイント 99,999P」）（{c1}）')
        check(hg['row'] and hg['inside'] and abs(hg['manR'] - 16) <= 1 and abs(hg['rvL'] - hg['pL']) <= 1 and hg['cls'] == '' and hg['sw'] <= 390,
              f'上の帯：99,999P でも 札の 中に 入る（「ポイント」と 数が 札の 中・つめない）・説明書は 同じ 段の 右はし・結果待ちの 左はしは 札と 同じ 線・横に はみ出さない（{hg}）')
        pC.locator('#setTest [data-test=pts]').click(); pC.wait_for_timeout(400)
        c2 = pC.evaluate(CI)
        check(c2['total'] == 99999 and 'いっぱい' in c2['toast'], f'上限の ときは「10,000P 足す」を 押しても ふえない（「いっぱい」と 知らせる）（{c2["toast"]}）')
        # 買う：上限を こえる パック・サブスクは 買う 前に 止める（App Store を よばない）
        pC.evaluate("window.__bridge = []"); pC.click('#ptsPill'); pC.wait_for_timeout(600)
        pb = pC.evaluate("""() => { const o = document.querySelector('#ptOv'); const dis = s => [...o.querySelectorAll(s + ' [data-pt=buy]')].map(b => b.disabled); o.querySelectorAll('[data-pt=buy]').forEach(b => b.click());
          return { pack: dis('#ptBuy'), sub: dis('#ptSub'), tb: o.querySelector('#ptBuy').innerText, ts: o.querySelector('#ptSub').innerText, det: o.querySelector('#ptDetail').innerText }; }""")
        pC.wait_for_timeout(300)
        buys = [x for x in pC.evaluate('window.__bridge') if x['name'] == 'iap' and x['payload'].get('op') == 'buy']
        check(pb['pack'] == [True] * 4 and pb['sub'] == [True] * 3 and '足すと こえる パックは 買えないよ' in pb['tb'] and 'プランは はじめられないよ' in pb['ts'] and 'いま いっぱい' in pb['det'] and not buys,
              f'上限の とき：ポイントの 窓の「買う」4つ・「はじめる」3つは 押せない（わけを 出す）・App Store は よばない（{len(buys)}回）')
        pC.evaluate("TengelWallet.closePoints()"); pC.wait_for_timeout(200)
        # ミッション：入らない あいだは 受け取りを 待つ（消えない）
        pC.evaluate("() => { localStorage.setItem('tengel.tc', JSON.stringify({ v: 1, total: 60 })); document.dispatchEvent(new CustomEvent('tengel:tc')); }"); pC.wait_for_timeout(300)
        pC.evaluate("TengelWallet.claim('mission-tc-50')"); pC.wait_for_timeout(500)
        c3 = pC.evaluate(CI)
        check(c3['total'] == 99999 and c3['badge'] == '1' and 'こえるよ' in c3['toast'] and 'ミッションは 消えないよ' in c3['toast'] and not pC.evaluate("TengelWallet.events().some(e => e.id === 'mission-tc-50')"),
              f'上限の とき：ミッション（500P）は 受け取れない（あとで 受け取れる・上の 数は 1 の まま）（{c3["toast"]}）')
        # サブスクの 更新が 届く（上限）→ こえた ぶんは あずかりポイント
        pC.locator('#setTest [data-test=ptsub]').click(); pC.wait_for_timeout(600)
        c4 = pC.evaluate(CI)
        check(c4['total'] == 99999 and c4['hold'] == {'total': 9200, 'paid_sub': 9200, 'paid_pack': 0, 'free': 0} and c4['avail'] == 99999 and 'あずかったよ' in c4['toast'] and '9,200P' in c4['toast'] and c4['badge'] == '1' and c4['pill'] == 'ポイント 99,999P',
              f'上限の ときに サブスク 9,200P が 届く → 台帳は 99,999P の まま・9,200P は あずかりポイント（知らせる・上の 数は まだ ふえない）（{c4["hold"]}）')
        pC.click('#msBtn'); pC.wait_for_timeout(600)
        HC = """() => { const c = document.querySelector('#msHoldCard'), b = c && c.querySelector('[data-pt=refill]'), r = c && c.querySelector('.msrow[data-mid=hold]');
          return c ? { hidden: c.hidden, first: document.querySelector('#msOv .msb').firstElementChild === c, h2: c.querySelector('h2').innerText, t: c.innerText.replace(/\\s+/g, ' '), dis: b ? b.disabled : null, can: r ? r.classList.contains('can') : null, msn: document.querySelector('#msOv .msn').innerText } : null; }"""
        h1 = pC.evaluate(HC)
        check(bool(h1) and not h1['hidden'] and h1['first'] and h1['h2'] == 'あずかりポイント' and 'あずかり中 9,200P' in h1['t'] and 'サブスクポイント 9,200P' in h1['t'] and 'いまは いっぱい' in h1['t'] and h1['dis'] is True and h1['can'] is False
              and '補充した 日から 30日' in h1['t'], f'ミッションの 窓の いちばん 上に「あずかりポイント」（あずかり中 9,200P・サブスクポイント）。いっぱいの あいだは「補充する」は 押せない（{h1 and h1["t"][-60:]}）')
        pC.evaluate("TengelWallet.closeMissions()"); pC.wait_for_timeout(200)
        # 使う（500P）→ あきが できる → 上の 数に 1つ ふえる → 補充する
        okU = pC.evaluate("TengelWallet.unlock('type:複勝', 500)"); pC.wait_for_timeout(500)
        c5 = pC.evaluate(CI)
        check(okU and c5['total'] == 99499 and c5['hold']['total'] == 9200 and c5['avail'] == 99999 and c5['badge'] == '2' and c5['pill'] == 'ポイント 99,499P', f'500P 使う → 99,499P・上の「ミッション」の 数が 1 → 2（あずかりを 補充できる）（{c5}）')
        pC.click('#msBtn'); pC.wait_for_timeout(600)
        h2 = pC.evaluate(HC)
        check(h2['dis'] is False and h2['can'] is True and 'いま 補充できるのは 500P' in h2['t'] and h2['msn'].endswith('受け取れるのが 2つ！'), f'あずかりポイント：「いま 補充できるのは 500P」・「補充する」が 押せる（{h2["msn"]}）')
        pC.locator('#msHoldCard [data-pt=refill]').click(); pC.wait_for_timeout(900)
        c6 = pC.evaluate(CI); h3 = pC.evaluate(HC)
        rel = pC.evaluate("TengelWallet.events().filter(e => e.from === 'hold').map(e => ({ id: e.id, kind: e.kind, bucket: e.bucket, amount: e.amount, days: Math.round((Date.parse(e.expires) - Date.parse(e.at)) / 86400000), product: e.product }))")
        check(c6['total'] == 99999 and c6['sub'] == 500 and c6['hold'] == {'total': 8700, 'paid_sub': 8700, 'paid_pack': 0, 'free': 0} and c6['badge'] == '1' and '補充したよ' in c6['toast'] and '500P' in c6['toast'] and 'のこり 8,700P' in c6['toast']
              and len(rel) == 1 and rel[0]['id'].startswith('rel-tx-test-') and rel[0]['id'].endswith('-1') and rel[0]['kind'] == 'sub' and rel[0]['bucket'] == 'paid_sub' and rel[0]['amount'] == 500 and rel[0]['days'] == 30 and rel[0]['product'] == 'jp.tengel.app.sub9200'
              and 'あずかり中 8,700P' in h3['t'] and h3['dis'] is True,
              f'「補充する」→ 500P が サブスクポイントに 入って 99,999P・あずかり 8,700P（期限は 補充した 日から 30日・上の 数は 2 → 1）（{c6["toast"]}・{rel}）')
        pC.evaluate("TengelWallet.closeMissions()"); pC.wait_for_timeout(200)
        # ポイントの詳細・履歴に あずかりポイント
        pC.click('#ptsPill'); pC.wait_for_timeout(500)
        dt = pC.locator('#ptOv #ptDetail').inner_text().replace('\n', ' ')
        check('あずかりポイント：8,700P' in dt and '「ミッション」で 補充できるよ' in dt and 'あずかり 8,700P' in pC.evaluate("document.querySelector('#ptsPill').title"), 'ポイントの詳細に「あずかりポイント：8,700P」（札の title にも）')
        pC.evaluate("TengelWallet.closePoints()"); pC.wait_for_timeout(200)
        pC.evaluate("() => { const b = document.querySelector('#setPoints [data-pt=show][data-v=hist]'); if (b.getAttribute('aria-pressed') !== 'true') b.click(); }"); pC.wait_for_timeout(400)
        hs = pC.evaluate("[...document.querySelectorAll('#setPoints .pthist li')].map(x => x.innerText.replace(/\\s+/g, ' '))")
        check(any('あずかりポイントから 補充（月9,200Pプラン' in x and x.endswith('+500P') for x in hs) and any('月9,200Pプラン（9,200P は あずかり）' in x for x in hs),
              f'履歴：「あずかりポイントから 補充（月9,200Pプラン…）+500P」・届いた 行は「月9,200Pプラン（9,200P は あずかり）」（{hs[:3]}）')
        # トレーニングセンターの 当たり（上限）→ あずかり（獲得ポイント）・同じ id は 2回 入らない
        g1 = pC.evaluate("TengelWallet.grant('tc-cap-1', 300, 'トレーニングセンターの お世話')"); pC.wait_for_timeout(400)
        c7 = pC.evaluate(CI); g2 = pC.evaluate("TengelWallet.grant('tc-cap-1', 300, 'トレーニングセンターの お世話')")
        check(g1 is True and g2 is False and c7['total'] == 99999 and c7['hold'] == {'total': 9000, 'paid_sub': 8700, 'paid_pack': 0, 'free': 300} and 'あずかったよ' in c7['toast'],
              f'上限の ときの トレーニングセンターの 当たり 300P → 消さずに あずかる（獲得ポイント）・同じ 当たりは 2回 入らない（{c7["hold"]}）')
        # あとから 届いた パック（上限）→ あずかり・台帳には 0P の できごと・取引は 終わらせる。返金 → あずかりも 消える
        pC.evaluate("window.__iap.finished = []; window.__nativeEvent('iap', { id: '7001', originalId: 'o7', product: 'jp.tengel.app.points1000', kind: 'pack', date: new Date().toISOString(), revoked: false })"); pC.wait_for_timeout(700)
        c8 = pC.evaluate(CI)
        e8 = pC.evaluate("(e => e && { amount: e.amount, held: e.held, kind: e.kind })(TengelWallet.events().find(e => e.id === 'tx-7001'))")
        check(c8['total'] == 99999 and c8['hold']['paid_pack'] == 1000 and c8['hold']['total'] == 10000 and e8 == {'amount': 0, 'held': 1000, 'kind': 'purchase'} and pC.evaluate("window.__iap.finished") == ['7001'] and 'あずかったよ' in c8['toast'],
              f'上限の ときに 届いた パック 1,000P → あずかり（購入ポイント）・台帳には 0P の できごと（同じ 取引は 2回 入らない）・取引は 終わらせる（{e8}）')
        pC.evaluate("window.__nativeEvent('iap', { id: '7001', originalId: 'o7', product: 'jp.tengel.app.points1000', kind: 'pack', date: new Date().toISOString(), revoked: true, revokedAt: new Date().toISOString() })"); pC.wait_for_timeout(700)
        c9 = pC.evaluate(CI)
        check(c9['total'] == 99999 and c9['hold'] == {'total': 9000, 'paid_sub': 8700, 'paid_pack': 0, 'free': 300}, f'その パックが 返金 → あずかりの 1,000P も 消える（ほかの あずかりは そのまま）（{c9["hold"]}）')
        # 足りなくて 使えない ときは、あずかりから 先に 補充してから 使う（「使えるか」は 財布＋あずかりで 見る）
        pC.evaluate("TengelWallet.unlock('test:big', 99600)"); pC.wait_for_timeout(400)
        c10 = pC.evaluate(CI)
        okA = pC.evaluate("TengelWallet.unlock('type:枠複', 500)"); pC.wait_for_timeout(500)
        c11 = pC.evaluate(CI)
        check(c10['total'] == 399 and c10['avail'] == 9399 and okA and c11['total'] == 399 + 9000 - 500 and c11['hold']['total'] == 0 and c11['badge'] == '1',
              f'財布 399P・あずかり 9,000P の ときに 500P の 解放 → あずかりから 先に 補充（9,000P）してから 使う → 8,899P・あずかり 0（{c10["total"]}／{c10["avail"]} → {c11["total"]}）')
        # あきが できた ので ミッションを 受け取れる・開き直しても あずかりは 残る
        pC.evaluate("TengelWallet.claim('mission-tc-50')"); pC.wait_for_timeout(500)
        check(pC.evaluate("TengelWallet.events().some(e => e.id === 'mission-tc-50')") and pC.evaluate('TengelWallet.total()') == 8899 + 500, 'あきが できたら 待って いた ミッション（500P）を 受け取れる')
        pC.locator('#setTest [data-test=pts100]').click(); pC.wait_for_timeout(400); pC.locator('#setTest [data-test=ptsub]').click(); pC.wait_for_timeout(600)
        pC.reload(); pC.wait_for_timeout(1500); gate(pC); pC.wait_for_timeout(900)
        c12 = pC.evaluate(CI)
        check(c12['total'] == 99999 and c12['hold']['total'] == 9200 and c12['hold']['paid_sub'] == 9200 and pC.evaluate("TengelWallet.snapshot().hold.length") == 1, f'開き直しても あずかりポイントは 残る（台帳と いっしょに 保存・自動バックアップにも 入る）（{c12["hold"]}）')
        ctxC.close()
        # ---- 第4.139版：ポイントを 不正に ふやせる 抜け穴を ふさぐ（まさちゃん 11/10 12:27「販売版で、ポイントを不正に増やせる抜け穴みたいのって今のテンゲルに存在する？防ぐための仕組みが必要ならアイディアを出してから組み込んでみて！」）----
        mS = {}
        def markerS(source, q):
            op, key = q.get('op'), q.get('key')
            if op == 'set': mS[key] = q.get('value', '1'); return {'ok': True}
            if op == 'del': mS.pop(key, None); return {'ok': True}
            v = mS.get(key); return {'ok': True, 'has': v is not None, 'value': v}
        ctxS = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP'); ctxS.add_init_script(FAKE)
        ctxS.expose_binding('__saveBackup', lambda s, t: None); ctxS.expose_binding('__marker', markerS)
        pS = ctxS.new_page(); pS.on('pageerror', lambda e: errs.append('SEC ' + str(e)))
        pS.goto(APPURL); pS.wait_for_timeout(1500); gate(pS); pS.wait_for_timeout(700)
        # ① 書きかえた バックアップの ファイル：ポイントの 台帳（auto の しるし つき）は 読まない・字は 無害に する（タグに ならない）
        XS = '"><i data-xss="1">X</i><img src="x" data-xss="2">'
        forged = {'app': 'tengel3', 'appVer': 'x', 'at': '2026-10-01T03:00:00.000Z', 'auto': True,
                  'wallet': {'id': 'wallet', 'v': 1, 'device': 'evil', 'events': [{'id': 'gift-first', 'kind': 'gift', 'bucket': 'free', 'amount': 1500, 'at': '2026-10-01T03:00:00.000Z'}, {'id': 'gift-x', 'kind': 'gift', 'bucket': 'free', 'amount': 98499, 'at': '2026-10-01T03:00:00.000Z'}], 'paid': [], 'counted': {}},
                  'bets': [{'id': 'xs' + str(i), 'date': '2026-10-0' + str(i + 1), 'venue': 'V' + XS, 'r': str(7 + i) + XS, 'rname': 'N' + XS, 'n': '14' + XS, 'types': ['馬単' + XS], 'n1': 5, 'n2': 2, 'n3': 1, 'p1': 3, 'p2': 1, 'p3': 2, 'stake': '600', 'payout': '0', 'horses': [],
                            'snap': {'L': 'A' + XS, 'kubun': 'A'}, 'rsv': {'state': st_, 'types': ['馬単'], 'bets': {'馬単' + XS: [[5, 2]]}, 'at': '2026-10-01T03:00:00.000Z', 'start': '23:59'}, 'mem': {'at': '2026-10-01T03:00:00.000Z', 'v': 'a'}}
                           for i, st_ in enumerate(['done', 'reserved', 'given'])],
                  'settings': {'zones': None}, 'slots': {'names': {'2': 'S' + XS}, 'active': 1, 'data': {}}}
        ffn = os.path.join(W, 't4', 'forged_backup.json'); open(ffn, 'w', encoding='utf8').write(json.dumps(forged, ensure_ascii=False))
        pS.click('.tabbar button[data-tab=set]'); pS.wait_for_timeout(300)
        t0 = pS.evaluate('TengelWallet.total()'); emp = pS.evaluate('TengelWallet.isEmpty()')
        pS.set_input_files('#pwaRestoreFile', ffn); pS.wait_for_timeout(1500)
        fi = pS.evaluate("""() => ({ total: TengelWallet.total(), ev: TengelWallet.events().map(e => e.id), bets: TengelLocal.mem.bets.size, info: document.querySelector('#pwaBkInfo').textContent,
          bad: [...TengelLocal.mem.bets.values()].filter(b => [b.r, b.venue, b.rname, b.n, (b.types || []).join(), Object.keys(b.rsv.bets).join(), (b.snap || {}).L].some(v => /[<>"'`]/.test(String(v)))).length,
          r: String([...TengelLocal.mem.bets.values()].map(b => b.r)[0]) })""")
        check(emp and t0 == 1500 and fi['total'] == 1500 and fi['ev'] == ['gift-first'] and fi['bets'] == 3 and '記録3件を戻したよ' in fi['info'] and 'ポイント' not in fi['info'],
              f'抜け穴①：書きかえた バックアップ（ポイントの 台帳 99,999P と auto の しるし）を「バックアップから戻す」で 読ませても ポイントは ふえない（記録だけ 戻る）（{fi["total"]}P・{fi["info"][:40]}）')
        check(fi['bad'] == 0 and '＜' in fi['r'] and '”' in fi['r'], f'ファイルから 読んだ 字は < > " \' ` を 全角に かえてから 入れる（数の 欄・券種の 名前・見出しの 名前も）（{fi["r"][:24]}…）')
        XN = "() => document.querySelectorAll('[data-xss]').length"
        pS.click('.tabbar button[data-tab=rec]'); pS.wait_for_timeout(500)
        pS.evaluate("() => { const b = document.querySelector('button[data-ym=m][data-v=\"0\"]'); if (b) b.click(); }"); pS.wait_for_timeout(500)
        x1 = pS.evaluate(XN); seen1 = pS.evaluate("() => (document.body.innerText.match(/data-xss/g) || []).length")
        pS.evaluate("() => { document.querySelectorAll('#recList details').forEach(d => { d.open = true; }); const r = document.querySelector('#recList .lrow .lmain'); if (r) r.click(); }"); pS.wait_for_timeout(500)
        x2 = pS.evaluate(XN)
        pS.evaluate("() => document.querySelector('#rsvBtn').click()"); pS.wait_for_timeout(600); x3 = pS.evaluate(XN)
        pS.evaluate("() => { const b = document.querySelector('.tgov [data-ms=close], .tgov .btn'); if (b) b.click(); }"); pS.wait_for_timeout(300)
        pS.evaluate("() => document.querySelector('.tabbar button[data-tab=stats]').click()"); pS.wait_for_timeout(500); x4 = pS.evaluate(XN)
        pS.evaluate("() => document.querySelector('.tabbar button[data-tab=set]').click()"); pS.wait_for_timeout(500); x5 = pS.evaluate(XN)
        check(seen1 >= 3 and [x1, x2, x3, x4, x5] == [0, 0, 0, 0, 0], f'読ませた 字は どの 画面でも タグに ならない（字と して 出る：記録の 一覧・開いた 行・結果待ちの 窓・実測・設定）（字 {seen1}こ・タグ {[x1, x2, x3, x4, x5]}）')
        # 台帳に じかに 入った おかしな 字（前の 版の データなど）でも、記録の 一覧の R・層の 札は タグに ならない
        pS.evaluate("""(C) => TengelLocal.putBets([{ id: 'xsraw', date: '2026-10-05', venue: 'V', r: '9' + C, rname: 'N', n: 14, types: ['馬単'], n1: 5, n2: 2, n3: 1, p1: 3, p2: 1, p3: 2, stake: '600', payout: '0', horses: [], snap: { L: 'B' + C, kubun: 'B' },
          rsv: { state: 'done', types: ['馬単'], bets: { '馬単': [[5, 2]] }, result: { p: [[5], [2], [1]] }, fx: 'miss', at: new Date().toISOString() }, mem: { at: new Date().toISOString(), v: 'a' } }])""", XS); pS.wait_for_timeout(400)
        pS.evaluate("() => document.querySelector('.tabbar button[data-tab=rec]').click()"); pS.wait_for_timeout(600)
        check(pS.evaluate(XN) == 0 and pS.evaluate("() => (document.querySelector('#recList').innerText.match(/data-xss/g) || []).length") >= 2, '台帳に じかに 入った 字でも、記録の 一覧の R・層の 札は 字と して 出る（タグに ならない）')
        # ② タグに 書いた スクリプト（onerror など）は 動かない（Content-Security-Policy）・ページに タグの スクリプトは ない
        csp = pS.evaluate("(document.querySelector('meta[http-equiv=\"Content-Security-Policy\"]') || {}).content || ''")
        pS.evaluate("() => { window.__xssRan = 0; const d = document.createElement('div'); d.id = 'cspProbe'; d.innerHTML = '<img src=\"missing-x.png\" onerror=\"window.__xssRan = 1\"><button id=\"cspBtn\" onclick=\"window.__xssRan = 2\">x</button>'; document.body.appendChild(d); document.querySelector('#cspBtn').click(); }")
        pS.wait_for_timeout(700)
        ran = pS.evaluate("window.__xssRan"); pS.evaluate("document.querySelector('#cspProbe').remove()")
        html_app = open(os.path.join(SRV, 'APP', 'index.html'), encoding='utf8').read()
        inl = re.findall('[\\s"\'<]on[a-z]{3,14}\\s*=\\s*["\'\\\\]', html_app)
        check(csp == "script-src-attr 'none'; base-uri 'none'; object-src 'none'" and ran == 0 and not inl and html_app.index('Content-Security-Policy') < html_app.index('<script'),
              f'抜け穴②の 守り：App Store版の ページは タグに 書いた スクリプト（onerror・onclick）を 動かさない（{csp}・動いた {ran}・ページの 中の タグの スクリプト {len(inl)}こ）')
        check('Content-Security-Policy' not in open(os.path.join(SRV, 'TENGEL', 'index.html'), encoding='utf8').read(), 'Web版の ページには この 守りを 入れて いない（App Store版だけ）')
        # ③ ミッション（記録の 数）：200P の 読み込み 1回で 数える のは 1レースだけ（日付・R を 手で かえて 何レースも 数えさせない）
        rc = pS.evaluate("""async () => {
          const W = TengelWallet, n0 = W.countedN(), t0 = W.total();
          const a = await W.readCharge({ form: { date: '2026-10-20', venue: 'あ', r: 8 }, ocr: { date: '2026-10-20', venue: 'あ', r: 8 } });
          const c1 = await W.countRace({ date: '2026-10-20', venue: 'あ', r: 8, pid: a.pid });
          const c2 = await W.countRace({ date: '2026-10-20', venue: 'あ', r: 9, pid: a.pid });        // R を かえた
          const c3 = await W.countRace({ date: '2026-10-21', venue: 'あ', r: 8, pid: a.pid });        // 日付を かえた
          const c4 = await W.countRace({ date: '2026-10-20', venue: 'い', r: 8, pid: a.pid });        // 開催場を かえた
          const c5 = await W.countRace({ date: '2026-10-20', venue: 'あ', r: 8, pid: a.pid });        // 同じ レースを もう一度
          const n1 = W.countedN();
          const b = await W.readCharge({ form: { date: '2026-10-20', venue: 'あ', r: 9 }, ocr: { date: '2026-10-20', venue: 'あ', r: 9 } });
          const c6 = await W.countRace({ date: '2026-10-20', venue: 'あ', r: 9, pid: b.pid });
          return { a: [a.ok, a.charged], b: [b.ok, b.charged], c: [c1, c2, c3, c4, c5, c6], n: [n0, n1, W.countedN()], spent: t0 - W.total() }; }""")
        check(rc['a'] == [True, True] and rc['b'] == [True, True] and rc['c'] == [True, False, False, False, False, True] and rc['n'] == [0, 1, 2] and rc['spent'] == 400,
              f'抜け穴③：1回の 読み込み（200P）で 数える のは 1レースだけ。同じ 読み込みの しるしで R・日付・開催場を かえた 記録は 数えない（べつの 読み込みを した レースは 数える）（{rc}）')
        # ④ 年：2026〜2036年を いつも 選べる（まさちゃん 11/10 12:47「年号2036年までできるようにして！」）
        pS.evaluate("() => document.querySelector('.tabbar button[data-tab=rec]').click()"); pS.wait_for_timeout(500)
        ys = pS.evaluate("[...document.querySelectorAll('#v-rec select[data-ym=y] option')].map(o => o.textContent)")
        pS.select_option('#v-rec select[data-ym=y]', '2036'); pS.wait_for_timeout(500)
        y2 = pS.evaluate("({ ttl: document.querySelector('#v-rec .ym-top .ttl').innerText, sel: document.querySelector('#v-rec select[data-ym=y]').value, empty: (document.querySelector('#recList .empty .big') || {}).innerText || '' })")
        pS.evaluate("() => document.querySelector('.tabbar button[data-tab=stats]').click()"); pS.wait_for_timeout(500)
        ys2 = pS.evaluate("[...document.querySelectorAll('#v-stats select[data-ym=y] option')].map(o => o.textContent)")
        check(ys == [f'{y}年' for y in range(2026, 2037)] and y2['ttl'].startswith('2036年') and y2['sel'] == '2036' and 'まだないよ' in y2['empty'] and ys2 == ys,
              f'年：2026年〜2036年（11こ・古い 順）を 選べる・2036年を 選ぶと その 年に なる（記録タブ・実測タブ）（{ys[0]}〜{ys[-1]}・{y2}）')
        # ⑤ 台帳の ならび（第4.139版）：その日 1回 使った あとに ポイントが 届いても、そのあと 使った ぶんは へる（前は その日の のこりが 0P で 読めた）
        so = pS.evaluate("""async () => {
          const W = TengelWallet, rd = r => W.readCharge({ form: { date: '2026-10-22', venue: 'う', r }, ocr: { date: '2026-10-22', venue: 'う', r } });
          let r = 1; while (W.total() >= 200 && r < 40) await rd(r++);                 // のこりが 200P より 少なく なるまで 読む
          const low = W.total();
          await W.grant('sec-order-1', 500, 'テスト');                                   // そのあとで 500P が 届く
          const t1 = W.total(), got = [];
          for (let i = 0; i < 5; i++) { const x = await rd(50 + i); got.push(x.ok && x.charged ? 1 : 0); }
          const ev = W.events();
          return { low, t1, got, total: W.total(), sp: ev.filter(e => e.kind === 'spend').map(e => e.amount), ns: ev.map(e => e.n) }; }""")
        kS = so['t1'] // 200
        check(so['low'] < 200 and so['t1'] == so['low'] + 500 and so['got'] == [1] * kS + [0] * (5 - kS) and so['total'] == so['t1'] - 200 * kS and len(so['sp']) >= 2 and so['sp'][-1] == -200 * kS
              and sorted(so['ns']) == list(range(1, len(so['ns']) + 1)),
              f'抜け穴⑤：使った あとに 届いた 500P も、使えば へる（{so["t1"]}P → 読めるのは {kS}回だけ → {so["total"]}P）・届いた あとの「使った」は 新しい 1件・できごとに 書いた 順の 番号（{so}）')
        ctxS.close()
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
