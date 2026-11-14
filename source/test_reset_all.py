# ぜんぶ リセット（第4.169版）の テスト
#   まさちゃん 2026/11/14 10:32「テスト版のみに全てをリセットできる機能つけて！」
#   ・テスト版（TENGEL_TEST=1）の 設定の「テスト版の道具」に「ぜんぶ リセット」→ たしかめる 札「リセット する／やめる」（2回 たしかめる・confirm()／alert() は 使わない）
#   ・「リセット する」→ 画面を かくして 開き直す → 開き直した ページの いちばん はじめに ぜんぶ 消す（reset_all.js）：
#       localStorage・sessionStorage・IndexedDB（記録・マザーデータ・設定・ポイントの 台帳）・キーチェーンの しるし 2つ・自動バックアップ（空に）・待たせて いる お知らせ
#   ・消した あとは はじめて 入れた ときと 同じ（開いた ときの 画面は「はじめる」・10,000P・ログインボーナス 1日目・着せ替えは「いつもの」・「前の記録が見つかったよ」は 出ない）
#   ・しるしは 1回 だけ 効く（つぎに 開いても 消えない）／とちゅうで 閉じても つぎに 開いた ときに 消す（しるしが のこる）
#   ・App Store版・Web版には 消す しかけが 入って いない（ボタンも 出ない・しるしを 置いても 何も 起きない）
#   python3 test_reset_all.py
import json, os, re, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv_reset'); PORT = 8807; APP = f'http://localhost:{PORT}/APP/'; STORE = f'http://localhost:{PORT}/STORE/'
SHOT = os.environ.get('SHOT')          # 画面を 写す フォルダ（見る 用）
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'TENGEL')], check=True, stdout=subprocess.DEVNULL, env={k: v for k, v in os.environ.items() if k not in ('TENGEL_TEST', 'TARGET')})
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, TARGET='app', TENGEL_TEST='1'))
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'STORE')], check=True, stdout=subprocess.DEVNULL, env=dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, TARGET='app'))
RAW = {d: open(os.path.join(SRV, d, 'index.html'), encoding='utf8').read() for d in ('APP', 'STORE', 'TENGEL')}      # 作った ままの 中身
for d in ('APP', 'STORE'):
    assert "window.__NATIVE = location.protocol === 'tengel:';" in RAW[d]
    open(os.path.join(SRV, d, 'index.html'), 'w', encoding='utf8').write(RAW[d].replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c: fails.append(label)


# アプリ（Swift）の にせもの：キーチェーンの しるし・自動バックアップ・お知らせは Python の 側に 持つ（ページを 開き直しても のこる＝本物の アプリと 同じ）
#   番号 0 の お願い（返事は いらない）には 返事を しない（本物の アプリも しない：TengelWebView.swift の reply）
FAKE = """
window.__NATIVE_INFO = { version: '1.0', build: '7', device: 'phone' };
window.webkit = { messageHandlers: { tengel: { postMessage: function (m) {
  window.__py({ id: m.id, name: m.name, payload: m.payload && m.payload.data ? null : m.payload }).then(function (v) { if (m.id > 0 && window.__nativeReply) window.__nativeReply(m.id, true, v); });
} } } };
"""
AUTO = 'window.__LOGIN_AUTO = true;'      # テストの ブラウザ（navigator.webdriver）でも、アプリと 同じ ように ログインボーナスを 自分から 出す


class Native:
    """にせものの アプリ 1台ぶん（しるし・自動バックアップ・お知らせ・届いた お願いの 記録）"""
    def __init__(self):
        self.markers, self.backup, self.writes, self.items, self.auth, self.log = {}, None, [], [], 'notDetermined', []

    def handle(self, source, m):
        name, P = m.get('name'), m.get('payload') or {}
        self.log.append((m.get('id'), name, P))
        if name == 'backup':
            self.backup = P.get('text'); self.writes.append(self.backup); return True
        if name == 'marker':
            op, key = P.get('op'), P.get('key')
            if op == 'set': self.markers[key] = P.get('value', '1'); return {'ok': True}
            if op == 'del': self.markers.pop(key, None); return {'ok': True}
            v = self.markers.get(key); return {'ok': True, 'has': v is not None, 'value': v}
        if name == 'notify':
            op = P.get('op')
            if op == 'status': return {'ok': True, 'auth': self.auth}
            if op == 'permission': self.auth = 'authorized'; return {'ok': True, 'granted': True, 'auth': self.auth}
            if op == 'sync': self.items = P.get('items') or []; return {'ok': True, 'scheduled': len(self.items), 'auth': self.auth}
            if op == 'opened': return {'ok': True, 'opened': None}
            return {'ok': True, 'list': self.items}
        if name == 'iap':
            return {'ok': True, 'products': []} if P.get('op') == 'products' else {'ok': True, 'list': [], 'current': [], 'unfinished': [], 'active': []}
        if name == 'zoom': return {'zoom': 1, 'pinch': not P.get('lock')}
        return True

    def attach(self, ctx):
        ctx.expose_binding('__py', self.handle)
        ctx.route('**/__native/autobackup.json', lambda route: route.fulfill(status=200, content_type='application/json', body=self.backup) if self.backup else route.fulfill(status=404, body='not found'))
        ctx.add_init_script(FAKE); ctx.add_init_script(AUTO)


def gate(pg):
    g = pg.locator('#gate')
    for _ in range(40):
        if not g.count() or g.evaluate('e => e.hidden'): return
        if pg.locator('#gateGo').count():
            if not g.evaluate("e => e.classList.contains('fade')"):
                try: pg.locator('#gateGo').click(timeout=3000)
                except Exception: pass
        else:
            try: g.click(timeout=500)
            except Exception: pass
        pg.wait_for_timeout(150)


def shot(pg, name):
    if SHOT: os.makedirs(SHOT, exist_ok=True); pg.screenshot(path=os.path.join(SHOT, name + '.png'))


def boot(pg, url, want=None):
    """開く → 財布が 読める まで 待つ（want＝この ポイントに なる まで）→ 開いた ときの 画面は そのまま（まだ 押さない）"""
    pg.goto(url); pg.wait_for_timeout(1200)
    pg.wait_for_function("(w) => window.TengelWallet && TengelWallet.on && window.TengelLocal && (w == null || TengelWallet.total() >= w)", arg=want, timeout=30000)
    pg.wait_for_timeout(900)


def login_close(pg):
    """ログインボーナスの 窓が 出て いたら「OK」で とじる"""
    try: pg.wait_for_function("() => !!document.getElementById('lgOv')", timeout=6000)
    except Exception: return False
    pg.wait_for_timeout(500); pg.locator('#lgOv [data-lg=ok]').click(); pg.wait_for_timeout(400); return True


# いまの ようす（財布・記録・設定・マザーデータの 名前・着せ替え・チケット・保存場所の 鍵・開いた ときの 画面・「戻す？」の 窓）
STATE = """async () => {
  const W = window.TengelWallet, L = window.TengelLocal, K = window.TengelKisekae, R = window.TengelReset, g = document.getElementById('gate');
  await L.ready; if (W) await W.ready;
  return { total: W ? W.total() : null, ev: W ? W.events().map(e => e.id.replace(/^login-.*/, 'login').replace(/^gift-test-.*/, 'gift-test+')) : null, gift: W ? (W.events().find(e => e.id === 'gift-first') || {}).at || null : null,
    bets: L.mem.bets.size, races: L.mem.races.size, notify: await L.getSetting('notify'), names: L.slots.names(), active: L.slots.active(), memOnly: L.memOnly(),
    ls: Object.keys(localStorage).sort(), ss: Object.keys(sessionStorage).sort(), tickets: window.TCInfo ? TCInfo.tickets() : null, theme: K ? K.current() : null,
    did: R ? R.did() : null, hasReset: !!R, gate: !!g && !g.hidden, first: !!document.getElementById('gateGo'), restore: !!document.getElementById('nativeRestore'),
    login: window.TengelLogin ? TengelLogin.state() : null, card: !!document.getElementById('setTest'), wipeBtn: document.querySelectorAll('[data-test=wipe]').length,
    dbs: indexedDB.databases ? (await indexedDB.databases()).map(d => d.name).sort() : null }; }"""
# 判定タブの 入力の 中身（欄の 名前＝値）
FORMVALS = "() => [...document.querySelectorAll('#v-judge input, #v-judge select, #v-judge textarea')].map((e, i) => (e.id || e.name || e.className || i) + '=' + (e.type === 'checkbox' ? e.checked : e.value))"
# 買った レースの 記録 2つ（test_fig.py と 同じ 形）
SEED = """async () => {
  const mk = (id, r, rname, bets, res, fx, stake, pay) => ({ id, date: '2026-11-0' + (r === 11 ? '9' : '8'), venue: '', r, rname, n: 14, types: Object.keys(bets),
    n1: res[0], n2: res[1], n3: res[2], p1: 3, p2: 1, p3: 2, stake: String(stake), payout: String(pay), horses: [],
    rsv: { state: 'done', types: Object.keys(bets), bets, result: { p: [[res[0]], [res[1]], [res[2]]] }, fx, at: new Date().toISOString() } });
  await TengelLocal.putBets([mk('rsm1', 11, 'テンゲル記念', { '3連単': [[5, 2, 1], [5, 1, 2], [2, 5, 1]], '馬単': [[5, 2]] }, [5, 2, 1], 'hit', 1000, 45600),
    mk('rsm2', 9, 'はなまる特別', { '馬単': [[3, 7], [7, 3]] }, [8, 4, 6], 'miss', 600, 0)]);
  await TengelLocal.putSetting('notify', false);
  await TengelLocal.slots.rename(2, 'ためしの データ');
  localStorage.setItem('tengel.tc', JSON.stringify({ v: 1, total: 7, tickets: 2 }));
  localStorage.setItem('tengel.oshi', JSON.stringify({ v: 1, list: [{ id: 'o1', name: 'ためしの 馬', ped: [], memo: '', at: 1 }] }));
  localStorage.setItem('tengel.form', JSON.stringify({ r: '5', n: '12' }));
  sessionStorage.setItem('seeded', '1');
}"""

try:
    print('■ 中身（ビルド）')
    src = open(os.path.join(W, 'reset_all.js'), encoding='utf8').read(); code = re.sub(r'(?m)^\s*//[^\n]*\n', '', src)
    app, store, web = RAW['APP'], RAW['STORE'], RAW['TENGEL']
    first = re.search(r'<script>(.*?)</script>', app, re.S).group(1)      # テスト版の index.html の いちばん はじめの スクリプト
    check("'tengel.wipe'" in first and 'deleteDatabase' in first and 'window.TengelReset = {' in first and app.index('window.TengelReset = {') < app.index('window.__APP_VER=') < app.index('window.TengelNative'),
          'テスト版の index.html：ぜんぶ リセット（reset_all.js）が いちばん はじめの スクリプト（ほかの どの コードも 保存場所を 読む 前に 動く）')
    words = ('deleteDatabase', 'tengel.wipe', 'localStorage.clear', 'sessionStorage.clear', 'TengelReset = ', 'wipeCover', 'wipeNote')
    check(not [w for w in words if w in store] and not [w for w in words if w in web] and 'TengelReset' not in web,
          f'App Store版・Web版の index.html には 消す しかけが 1つも 入って いない（{[w for w in words if w in store or w in web]}）')
    sb = subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'STORE0')], capture_output=True, text=True, env=dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, TARGET='app', TENGEL_TEST='0'))
    check(sb.returncode == 0 and open(os.path.join(SRV, 'STORE0', 'index.html'), encoding='utf8').read() == store and app.replace(first, '', 1).count('deleteDatabase') == 0,
          'TENGEL_TEST=1 の とき だけ 入る（TENGEL_TEST=0 は App Store版と 同じ 中身）・消す しかけは はじめの スクリプトの 中 だけ')
    check('confirm(' not in code and 'alert(' not in code and 'prompt(' not in code and 'confirm(' not in first and 'alert(' not in first, 'confirm()・alert() を 使わない（アプリの 中では 出ない）')
    body = set(open(os.path.join(W, 'ios', 'fonts', 'ks', 'chars_body.txt'), encoding='utf8').read())
    pu = open(os.path.join(W, 'points_ui.js'), encoding='utf8').read(); part = pu[pu.index('data-test="wipe"') - 400:pu.index('data-test="wipeno"') + 60]
    lack = sorted({c for c in ''.join(re.findall(r"'((?:[^'\\]|\\.)*)'", code)) + part if ord(c) > 0x2000 and c not in body and not 0x1F000 <= ord(c) <= 0x1FAFF})
    check(not lack and 'ほんとうに ぜんぶ 消す？' in part and 'もとには もどせない' in part, f'画面の 言葉は しぼった 字（本文 {len(body)}字）に 入って いる 字 だけ（足りない 字 {lack}）')
    check("post('marker', { op: 'del', key: 'gift-first' })" in code and "post('marker', { op: 'del', key: 'granted-sub' })" in code and "post('backup', { text: JSON.stringify({ reset: true, bets: [] }) })" in code
          and "post('notify', { op: 'sync', items: [] })" in code and 'id: 0' in code and "DB = 'tengel3'" in code and "var DBNAME = 'tengel3'" in open(os.path.join(W, 'pwa_shim.js'), encoding='utf8').read(),
          'アプリへの お願い 4つ（しるし 2つを 消す・自動バックアップを 空に・お知らせを 消す）は 番号 0（返事なし）・消す DB の 名前は アプリの DB（tengel3）と 同じ')
    sw = open(os.path.join(W, 'ios', 'Tengel.swiftpm', 'TengelWebView.swift'), encoding='utf8').read(); mk = open(os.path.join(W, 'ios', 'Tengel.swiftpm', 'Markers.swift'), encoding='utf8').read()
    check('guard id > 0, let webView else { return }' in sw and '(body["id"] as? NSNumber)?.intValue ?? 0' in sw and 'case "del":' in mk and 'if scheme == AppSchemeHandler.scheme ||' in sw
          and all(f'"{k}"' in open(os.path.join(W, 'points_ui.js'), encoding='utf8').read() or f"'{k}'" in open(os.path.join(W, 'points_ui.js'), encoding='utf8').read() for k in ('gift-first', 'granted-sub')),
          'アプリ（Swift）：番号 0 の お願いには 返事を しない・しるしを 消す（del）が ある・開き直し（tengel: の ページ）は 通す・しるしの 名前は 財布（points_ui.js）と 同じ 2つ')

    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'])
        N = Native()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo', has_touch=True, is_mobile=True)
        N.attach(ctx)
        pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        dialogs = []; pg.on('dialog', lambda d: (dialogs.append(d.type), d.dismiss()))

        print('■ つかった あとの 形を 作る（テスト版）')
        boot(pg, APP, 10000); s0 = pg.evaluate(STATE)
        check(s0['first'] and s0['total'] == 10000 and s0['ev'] == ['gift-first', 'gift-test'] and s0['did'] is None and s0['hasReset'] and s0['bets'] == 0 and 'gift-first' in N.markers,
              f'はじめて 開いた：「はじめる」の 画面・10,000P（初回 1,500P＋テスト版 8,500P）・キーチェーンに 初回の しるし・リセットは まだ 動いて いない（{s0["ev"]}）')
        gate(pg); l0 = login_close(pg)
        F0 = pg.evaluate(FORMVALS); K0 = pg.evaluate("() => Object.keys(localStorage).sort()")      # はじめて 開いた ときの 判定タブの 入力・端末の おぼえの 名前（消した あとと くらべる）
        pg.evaluate(SEED); pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(300)
        pg.locator('#setTest [data-test=pts]').click(); pg.wait_for_timeout(500)
        N.markers['granted-sub'] = '["tx-1"]'; N.items = [{'id': 'x1', 'at': 1, 'title': 't', 'body': 'b'}]
        pg.wait_for_timeout(2600)      # 自動バックアップ（保存の 1.5秒 あと）
        s1 = pg.evaluate(STATE); bk1 = json.loads(N.backup) if N.backup else {}
        check(l0 and s1['total'] == 20200 and s1['bets'] == 2 and s1['notify'] is False and s1['names'].get('2') == 'ためしの データ' and s1['tickets'] == 2 and 'tengel.gateSeen' in s1['ls'] and 'tengel.login' in s1['ls'] and s1['ss'] == ['seeded']
              and len(bk1.get('bets') or []) == 2, f'つかった 形：20,200P（＋ログインボーナス 200P・テストの 10,000P）・記録 2件・設定・マザーデータの 名前・チケット 2枚・自動バックアップに 記録 2件（{s1["ls"]}）')
        boot(pg, APP, 20200); s2 = pg.evaluate(STATE)
        check(not s2['first'] and s2['total'] == 20200 and s2['bets'] == 2 and s2['did'] is None and not s2['restore'], '開き直しても そのまま（リセットは 押した とき だけ）・開いた ときの 画面は 短い 形')
        gate(pg); pg.wait_for_timeout(600)

        print('■ 設定の「テスト版の道具」：ぜんぶ リセット')
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(300)
        lay = pg.evaluate("""() => { const c = document.getElementById('setTest'), bt = c.querySelector('[data-test=wipe]'), w = document.getElementById('testWipe'), all = [...c.querySelectorAll('[data-test]')], r = bt.getBoundingClientRect(), cr = c.getBoundingClientRect();
          return { last: all[all.length - 3] === bt, hidden: w.hidden, txt: bt.textContent, cls: bt.className, h: r.height, inside: r.left >= cr.left && r.right <= cr.right, hint: bt.closest('.row').previousElementSibling.textContent, color: getComputedStyle(bt).color, ink: getComputedStyle(c).color }; }""")
        check(lay['last'] and lay['hidden'] and lay['txt'] == 'ぜんぶ リセット' and 'danger' in lay['cls'] and lay['color'] != lay['ink'] and lay['h'] >= 36 and lay['inside'] and 'はじめて 開いた ときの 形に もどす' in lay['hint'] and 'もとには もどせない' in lay['hint'],
              f'カードの いちばん 下に「ぜんぶ リセット」（赤い 字の ボタン・高さ {lay["h"]:.0f}px）と 説明・たしかめる 札は まだ 出て いない')
        pg.locator('#setTest [data-test=wipe]').scroll_into_view_if_needed(); pg.locator('#setTest [data-test=wipe]').click(); pg.wait_for_timeout(400); shot(pg, 'reset_confirm')
        cf = pg.evaluate("""() => { const w = document.getElementById('testWipe'), r = w.getBoundingClientRect(), go = w.querySelector('[data-test=wipego]'), no = w.querySelector('[data-test=wipeno]'), a = go.getBoundingClientRect(), n = no.getBoundingClientRect(), tb = document.querySelector('.tabbar').getBoundingClientRect();
          return { hidden: w.hidden, txt: w.textContent, go: go.textContent, no: no.textContent, gh: a.height, nh: n.height, apart: n.left - a.right, row: Math.abs(a.top - n.top) < 2, inside: r.left >= 0 && r.right <= innerWidth, seen: r.bottom <= tb.top + 1 && r.top >= 0,
            fam: getComputedStyle(w.querySelector('p')).fontFamily.split(',')[0].trim().replace(/"/g, ''), cardFam: getComputedStyle(document.querySelector('#setTest .hint')).fontFamily.split(',')[0].trim().replace(/"/g, ''), over: w.scrollWidth > w.clientWidth + 1 }; }""")
        check(not cf['hidden'] and 'ほんとうに ぜんぶ 消す？' in cf['txt'] and 'もとには もどせない' in cf['txt'] and cf['go'] == 'リセット する' and cf['no'] == 'やめる' and cf['gh'] >= 36 and cf['nh'] >= 36 and cf['row'] and cf['apart'] >= 6
              and cf['inside'] and cf['seen'] and not cf['over'] and cf['fam'] == cf['cardFam'],
              f'1回目：たしかめる 札「ほんとうに ぜんぶ 消す？」＋「リセット する」「やめる」（横に ならぶ・間 {cf["apart"]:.0f}px・画面の 中に 見える・字は カードと 同じ {cf["fam"]}）')
        s3 = pg.evaluate(STATE)
        check(s3['total'] == 20200 and s3['bets'] == 2 and 'tengel.wipe' not in s3['ls'] and s3['ss'] == ['seeded'] and not pg.locator('#wipeCover').count(), '1回目の ボタン だけでは 何も 消えない（しるしも 置かない）')
        pg.locator('#setTest [data-test=wipeno]').click(); pg.wait_for_timeout(300)
        s4 = pg.evaluate(STATE); hid = pg.evaluate("() => document.getElementById('testWipe').hidden")
        check(hid and s4['total'] == 20200 and s4['bets'] == 2 and 'tengel.wipe' not in s4['ls'] and N.markers.get('granted-sub') == '["tx-1"]' and len(json.loads(N.backup)['bets']) == 2, '「やめる」：札を しまう・何も 消えない')

        print('■ 「リセット する」→ 開き直して ぜんぶ 消す')
        # つづけて 2回 押した ゆび（札が 出て すぐ「リセット する」に 当たる）では 動かない：出て から 0.7秒は 受けない
        pg.evaluate("() => { document.querySelector('#setTest [data-test=wipe]').click(); document.querySelector('#setTest [data-test=wipego]').click(); }"); pg.wait_for_timeout(700)
        dt = pg.evaluate("() => ({ cover: !!document.getElementById('wipeCover'), mark: localStorage.getItem('tengel.wipe'), open: !document.getElementById('testWipe').hidden, dis: [...document.querySelectorAll('#testWipe button')].some(b => b.disabled) })")
        check(not dt['cover'] and dt['mark'] is None and dt['open'] and not dt['dis'] and 'const WIPE_WAIT = 700;' in pu, f'札が 出て すぐの「リセット する」（つづけて 2回 押した ゆび）では 動かない（0.7秒 待つ）{dt}')
        pg.wait_for_timeout(300)
        n_log = len(N.log); gift0 = s1['gift']; N.auth = 'authorized'
        # 開き直す までの 0.4秒を テストの 間 だけ 1.5秒に のばす（かくす 画面を 見る ひま）。__old＝前の ページの しるし（開き直すと 消える）
        pg.evaluate("() => { window.__old = true; const st = window.setTimeout; window.setTimeout = (f, ms, ...a) => st(f, ms === 400 ? 1500 : ms, ...a); }")
        pg.locator('#setTest [data-test=wipego]').click(); pg.wait_for_timeout(250)
        cv = pg.evaluate("""() => { const c = document.getElementById('wipeCover'); if (!c) return null; const r = c.getBoundingClientRect(), t = document.elementFromPoint(195, 800);
          return { txt: c.textContent, full: r.left <= 0 && r.top <= 0 && r.right >= innerWidth && r.bottom >= innerHeight, top: t === c, z: getComputedStyle(c).zIndex, ls: localStorage.getItem('tengel.wipe'), ss: sessionStorage.getItem('tengel.wipe'), dis: [...document.querySelectorAll('#testWipe button')].every(b => b.disabled) }; }""")
        shot(pg, 'reset_cover')
        check(bool(cv) and cv['txt'] == 'リセットして いるよ…' and cv['full'] and cv['top'] and cv['ls'] == '1' and cv['ss'] == '1' and cv['dis'], f'押した すぐ：画面 いっぱいに「リセットして いるよ…」（下の タブも 押せない）・しるしを 置く・ボタンは もう 押せない（{cv}）')
        pg.wait_for_function("() => !window.__old && window.TengelReset && TengelReset.did() && TengelReset.did().db === 'ok'", timeout=30000)
        nt = pg.evaluate("""() => { const n = document.getElementById('wipeNote'); if (!n) return null; const r = n.getBoundingClientRect(), g = document.getElementById('gate'); return { txt: n.textContent, inside: r.left >= 0 && r.right <= innerWidth && r.top >= 0, z: +getComputedStyle(n).zIndex > +getComputedStyle(g).zIndex, pe: getComputedStyle(n).pointerEvents }; }""")
        pg.wait_for_function("() => window.TengelWallet && TengelWallet.on && TengelWallet.total() >= 10000", timeout=30000); pg.wait_for_timeout(900)
        s5 = pg.evaluate(STATE); shot(pg, 'reset_after'); msgs = N.log[n_log:]
        head = [(i, nm, P) for i, nm, P in msgs[:4]]
        check(head == [(0, 'marker', {'op': 'del', 'key': 'gift-first'}), (0, 'marker', {'op': 'del', 'key': 'granted-sub'}), (0, 'backup', {'text': '{"reset":true,"bets":[]}'}), (0, 'notify', {'op': 'sync', 'items': []})]
              and all(i > 0 for i, _n, _p in msgs[4:]) and len(msgs) > 4 and s5['did']['native'] == 4,
              f'開き直した ページが アプリへ はじめに 送る 4つ：しるし 2つを 消す → 自動バックアップを 空に → お知らせを 消す（番号 0・この あとに ふつうの お願い {len(msgs) - 4}こ）')
        check(bool(nt) and nt['txt'] == '🧪 ぜんぶ リセットしたよ' and nt['inside'] and nt['z'] and nt['pe'] == 'none', f'上に 小さな 札「🧪 ぜんぶ リセットしたよ」（開いた ときの 画面より 上・押す じゃまに ならない）{nt}')
        check(s5['first'] and s5['gate'] and s5['total'] == 10000 and s5['ev'] == ['gift-first', 'gift-test'] and s5['gift'] and s5['gift'] != gift0 and N.markers.get('gift-first') == s5['gift'] and 'granted-sub' not in N.markers,
              f'はじめて 入れた ときと 同じ：「はじめる」の 画面・ちょうど 10,000P（初回の 1,500P を もう一度 もらう＋テスト版 8,500P）・キーチェーンの しるしは 新しい 日時・サブスクの しるしは なし（{s5["ev"]}）')
        check(s5['bets'] == 0 and s5['notify'] is None and s5['names'].get('2') != 'ためしの データ' and s5['names'] == s0['names'] and s5['active'] == s0['active'] and s5['races'] == s0['races'] and s5['memOnly'] == '' and s5['dbs'] in (None, ['tengel3']),
              f'保存場所（IndexedDB）：記録 0件・設定は なし・マザーデータは はじめの 形（{s5["races"]}走・名前 {s5["names"]}）・保存場所は ふつうに 開けて いる')
        check('tengel.wipe' not in s5['ls'] and not [k for k in s5['ls'] if k in ('tengel.gateSeen', 'tengel.login', 'tengel.tc', 'tengel.oshi', 'tengel.form', 'tengel.kisekae')] and s5['ss'] == [] and s5['tickets'] == 0 and s5['theme'] == 'default'
              and s5['login']['n'] == 0 and s5['login']['last'] == '', f'端末の おぼえ（localStorage・sessionStorage）は 空（のこり {s5["ls"]}）・しるしも 消えた・チケット 0枚・着せ替えは「いつもの」・ログインボーナスは まだ 0回')
        check(not s5['restore'] and N.items == [] and 'granted-sub' not in N.markers, '「前の記録が見つかったよ」は 出ない・待たせて いた お知らせは 消えた')
        gate(pg); l5 = login_close(pg)
        F1 = pg.evaluate(FORMVALS); K1 = pg.evaluate("() => Object.keys(localStorage).sort()")
        check(s5['ls'] == s0['ls'] and K1 == K0 and F1 == F0 and len(F0) >= 20 and 'tengel.gateSeen' in K1 and 'tengel.login' in K1,
              f'はじめて 開いた ときと 見くらべて 同じ：端末の おぼえの 名前（「はじめる」の 前 {s5["ls"]}・あと {K1}）・判定タブの 入力の 中身（{len(F0)}こ）')
        pg.wait_for_timeout(2600); s6 = pg.evaluate(STATE); bk6 = json.loads(N.backup)
        check(l5 and s6['total'] == 10200 and s6['ev'] == ['gift-first', 'gift-test', 'login'] and s6['login']['n'] == 1 and not s6['restore'] and bk6.get('bets') == [] and bk6.get('auto') is True and 'reset' not in bk6
              and len((bk6.get('wallet') or {}).get('events') or []) == 3, f'「はじめる」の あと：ログインボーナスは 1日目から（+200P＝10,200P）・自動バックアップは 新しい 形（記録 0件・台帳 3件）に 書き直される')
        check(not errs and not dialogs, f'エラーなし・confirm()／alert() の 窓は 出ない（{errs[:2]}{dialogs}）')

        print('■ しるしは 1回 だけ／消した あとも ふつうに 使える')
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(300); pg.locator('#setTest [data-test=pts]').click(); pg.wait_for_timeout(600)
        pg.evaluate("() => TengelLocal.putSetting('notify', false)"); pg.wait_for_timeout(300)
        boot(pg, APP, 20200); s7 = pg.evaluate(STATE)
        check(s7['did'] is None and not s7['first'] and s7['total'] == 20200 and s7['notify'] is False and s7['login']['n'] == 1 and not s7['restore'] and not pg.locator('#wipeNote').count(),
              f'つぎに 開いた とき：もう 消えない（リセットは 1回 だけ）・消した あとに 足した 10,000P と 設定は のこる（{s7["total"]:,}P）')
        gate(pg); pg.wait_for_timeout(500)

        print('■ とちゅうで 閉じた とき（しるしが のこって いる）→ つぎに 開いた ときに 消す')
        pg.evaluate("() => { localStorage.setItem('tengel.wipe', '1'); }")      # sessionStorage の しるしは なし（アプリを 閉じると 消える）
        n_log = len(N.log); boot(pg, APP, 10000)
        pg.wait_for_function("() => TengelReset.did() && TengelReset.did().db === 'ok'", timeout=20000); s8 = pg.evaluate(STATE); m8 = N.log[n_log:n_log + 4]
        check(s8['first'] and s8['total'] == 10000 and s8['bets'] == 0 and s8['notify'] is None and 'tengel.wipe' not in s8['ls'] and [x[1] for x in m8] == ['marker', 'marker', 'backup', 'notify'] and all(x[0] == 0 for x in m8),
              '端末に のこった しるし だけでも、開いた ときに はじめから 消す（10,000P・記録 0件）・しるしは 消える')
        ctx.close()

        print('■ 保存場所を 消すのが 終わらない とき（ほかの つながりが のこって いる）')
        Nb = Native(); ctxb = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo'); Nb.attach(ctxb)
        pa = ctxb.new_page(); eb = []; pa.on('pageerror', lambda e: eb.append(str(e)))
        boot(pa, APP, 10000); gate(pa); login_close(pa)
        hold = ctxb.new_page(); hold.goto(f'http://localhost:{PORT}/APP/manual.html'); hold.wait_for_timeout(300)      # 同じ 置き場の 別の ページが DB を つかんだ まま（versionchange でも 閉じない）
        hold.evaluate("() => new Promise((res, rej) => { const r = indexedDB.open('tengel3'); r.onsuccess = () => { window.__hold = r.result; res(1); }; r.onerror = () => rej(r.error); })")
        pa.evaluate("() => { localStorage.setItem('tengel.wipe', '1'); }"); pa.goto(APP); pa.wait_for_timeout(1500)
        b1 = pa.evaluate("() => ({ did: TengelReset.did(), mark: localStorage.getItem('tengel.wipe') })")
        check(b1['did'] and b1['did']['db'] == 'blocked' and b1['mark'] == '1', f'消すのを 待って いる 間：しるしは のこる（とちゅうで 閉じても つぎに 開いた ときに もう一度 消す）{b1["did"]}')
        pa.wait_for_timeout(4300); nb = pa.evaluate("() => { const n = document.getElementById('wipeNote'); return n ? n.textContent : null; }"); shot(pa, 'reset_blocked')
        check(nb == 'リセットの とちゅうだよ。アプリを いちど 閉じて、もう一度 開いてね', f'5秒 たっても 終わらない とき：上に「{nb}」（出した まま）')
        hold.evaluate("() => { window.__hold.close(); }")
        pa.wait_for_function("() => TengelReset.did().db === 'ok'", timeout=20000); pa.wait_for_function("() => window.TengelWallet && TengelWallet.total() >= 10000", timeout=30000); pa.wait_for_timeout(600)
        b2 = pa.evaluate(STATE); nb2 = pa.evaluate("() => { const n = document.getElementById('wipeNote'); return n ? n.textContent : null; }")
        check(b2['total'] == 10000 and b2['first'] and b2['memOnly'] == '' and 'tengel.wipe' not in b2['ls'] and nb2 == '🧪 ぜんぶ リセットしたよ' and b2['ev'] == ['gift-first', 'gift-test'] and not eb,
              f'つながりが 閉じると つづきから：消し おわって アプリが ふつうに 開く（10,000P・しるしは 消える・札は「{nb2}」）{eb[:2]}')
        ctxb.close()

        print('■ 保存場所を 消せなかった とき（エラー）')
        Ne = Native(); ctxe = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo'); Ne.attach(ctxe)
        ctxe.add_init_script("IDBFactory.prototype.deleteDatabase = function () { const r = {}; setTimeout(() => { if (r.onerror) r.onerror(new Event('error')); }, 20); return r; };")      # 消す お願いが いつも 失敗する
        pe = ctxe.new_page(); ee = []; pe.on('pageerror', lambda e: ee.append(str(e)))
        boot(pe, APP, 10000); gate(pe); login_close(pe); pe.evaluate(SEED); pe.wait_for_timeout(500)
        pe.evaluate("() => { localStorage.setItem('tengel.wipe', '1'); }"); boot(pe, APP, 10000)
        x = pe.evaluate(STATE); nx = pe.evaluate("() => { const n = document.getElementById('wipeNote'); return n ? n.textContent : null; }"); shot(pe, 'reset_error')
        check(x['did']['db'] == 'error' and 'tengel.wipe' not in x['ls'] and x['bets'] == 2 and x['memOnly'] == '' and x['total'] == 10200 and nx == '保存場所を 消せなかったよ。もう一度「ぜんぶ リセット」を 押してね' and not ee,
              f'しるしを 外す（開く たびに くり返さない）・上に「{nx}」・アプリは ふつうに 開く（記録 {x["bets"]}件は のこって いる）{ee[:2]}')
        ctxe.close()

        print('■ GitHub の Mac の 自動テスト（5回目：本物の WKWebView で 見る）を 手元の ブラウザで なぞる')
        # 出す アプリ（App Store版の 中身）＋ テストの スクリプトの 先頭に「window.__TEST = true;」と reset_all.js（ios/ci/run.sh の phase の 5回目と 同じ 組み立て）
        ci_run = open(os.path.join(W, 'ios', 'ci', 'run.sh'), encoding='utf8').read(); ci_st = open(os.path.join(W, 'ios', 'ci', 'selftest.js'), encoding='utf8').read()
        check('if [ "$PH" = "5" ]; then echo "window.__TEST = true;"; cat "$ROOT/ci/reset_all.js"; fi; cat "$ROOT/ci/selftest.js"' in ci_run and 'phase "$IPHONE" iphone 5 700 reset-confirm report-5a reset-gate reset-main report-5' in ci_run
              and ci_run.index('phase "$IPHONE" iphone 3 700') < ci_run.index('shot "$IPHONE" "iphone-dark" 700') < ci_run.index('phase "$IPHONE" iphone 5 700') < ci_run.index('applog "$IPHONE" iphone')
              and 'async function phase5()' in ci_st and 'PH === 5 ? phase5' in ci_st and "report('5', R2)" in ci_st and "report('5a', R)" in ci_st and "await mark('reset-gate')" in ci_st,
              'CI：iPhone の シミュレーターの さいごに 5回目（テスト版の 印と reset_all.js を テストの スクリプトの 先頭に 足す → リセット → 開き直した あとを 見る）')
        py = ci_run.split("say \"   reset: $(python3 -c '")[1].split("' \"$OUT/iphone-report-5a.json\"")[0]      # 結果を 1行に まとめる Python（run.sh の 中）
        Nc = Native(); files = {}
        def ci_native(source, m):
            if m.get('name') == 'selftest':
                f = (m.get('payload') or {}); files[f.get('file')] = f.get('text'); return True
            return Nc.handle(source, m)
        ctxc = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo')
        ctxc.expose_binding('__py', ci_native)
        ctxc.route('**/__native/autobackup.json', lambda route: route.fulfill(status=200, content_type='application/json', body=Nc.backup) if Nc.backup else route.fulfill(status=404, body='not found'))
        ctxc.route('**/__selftest/ack-*.txt', lambda route: route.fulfill(status=200, body='ok') if ('mark-' + route.request.url.split('/ack-')[1]) in files else route.fulfill(status=404, body='no'))
        ctxc.add_init_script(FAKE)
        ctxc.add_init_script("window.__ST_PHASE = 5; window.__ST_DEVICE = 'iphone';\nwindow.__TEST = true;\n" + src + '\n' + ci_st)
        pc = ctxc.new_page(); ec = []; pc.on('pageerror', lambda e: ec.append(str(e)))
        pc.goto(STORE)
        t0 = time.time()
        while 'report-5.json' not in files and time.time() - t0 < 90: pc.wait_for_timeout(500)
        ra = json.loads(files.get('report-5a.json') or '{}'); rb = json.loads(files.get('report-5.json') or '{}')
        os.makedirs(os.path.join(SRV, 'ci'), exist_ok=True); fa, fb = os.path.join(SRV, 'ci', 'a.json'), os.path.join(SRV, 'ci', 'b.json')
        json.dump(ra, open(fa, 'w')); json.dump(rb, open(fb, 'w'))
        line = subprocess.run(['python3', '-c', py, fa, fb], capture_output=True, text=True); out = (line.stdout + line.stderr).strip()
        af = rb.get('after') or {}
        check(line.returncode == 0 and out.endswith('-> OK') and [k for k in ('mark-reset-confirm.txt', 'mark-reset-gate.txt', 'mark-reset-main.txt', 'report-5a.json', 'report-5.json') if k not in files] == []
              and ra.get('card') == {'card': True, 'btn': True} and (ra.get('confirm') or {}).get('hidden') is False and rb.get('db') == 'ok' and (rb.get('gate') or {}).get('first') is True and af.get('bets') == 0 and af.get('total') == 10000
              and rb.get('write') == 7 and not rb.get('errors') and not ec,
              f'手元の ブラウザで なぞると ぜんぶ 通る：{out[:230]}')
        bad = dict(rb, after=dict(af, bets=1)); json.dump(bad, open(fb, 'w')); o2 = subprocess.run(['python3', '-c', py, fa, fb], capture_output=True, text=True).stdout.strip()
        bad = dict(rb, db='blocked'); json.dump(bad, open(fb, 'w')); o3 = subprocess.run(['python3', '-c', py, fa, fb], capture_output=True, text=True).stdout.strip()
        bad = dict(rb, after=dict(af, offer=True)); json.dump(bad, open(fb, 'w')); o4 = subprocess.run(['python3', '-c', py, fa, fb], capture_output=True, text=True).stdout.strip()
        check(o2.endswith('-> CHECK') and o3.endswith('-> CHECK') and o4.endswith('-> CHECK'), '結果の まとめ：記録が のこった・保存場所を 消し おわらない・「前の記録が見つかったよ」が 出た ときは CHECK と 出る')
        ctxc.close()

        print('■ App Store版：消す しかけが ない')
        N2 = Native(); ctx2 = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo'); N2.attach(ctx2)
        p2 = ctx2.new_page(); e2 = []; p2.on('pageerror', lambda e: e2.append(str(e)))
        boot(p2, STORE, 1500); gate(p2); login_close(p2); p2.evaluate(SEED); p2.wait_for_timeout(2400)
        p2.evaluate("() => { localStorage.setItem('tengel.wipe', '1'); sessionStorage.setItem('tengel.wipe', '1'); }")
        n_log = len(N2.log); boot(p2, STORE, 1700); t1 = p2.evaluate(STATE); p2.click('.tabbar button[data-tab=set]'); p2.wait_for_timeout(300); t2 = p2.evaluate(STATE)
        check(not t1['hasReset'] and t1['did'] is None and t1['total'] == 1700 and t1['bets'] == 2 and t1['notify'] is False and t1['tickets'] == 2 and 'tengel.wipe' in t1['ls'] and 'tengel.gateSeen' in t1['ls'] and not t1['first']
              and not [x for x in N2.log[n_log:] if x[0] == 0 or (x[1] == 'marker' and x[2].get('op') == 'del')] and len(json.loads(N2.backup)['bets']) == 2,
              f'しるしを 置いて 開き直しても 何も 消えない（1,700P・記録 2件・設定・チケット そのまま・アプリへ 消す お願いも 出さない）')
        check(not t2['card'] and t2['wipeBtn'] == 0 and not p2.locator('#testWipe').count() and not e2, '設定に「テスト版の道具」も「ぜんぶ リセット」も 出ない')
        ctx2.close(); b.close()
finally:
    srv.terminate()
print()
if fails:
    print(f'❌ {len(fails)}こ だめ'); [print('  -', f) for f in fails]; sys.exit(1)
print('✅ ぜんぶ リセット（テスト版 だけ）の テスト OK')
