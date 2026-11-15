# 馬カードバトル（第4.176版）の 画面の テスト：App Store版（TARGET=app）を localhost で アプリ版として 開く
#   まさちゃん 2026/11/15 21:41「TENGER馬カードバトル …アイコンは推し馬の上に設置して！」・21:54「・コンピュータと対戦 ・部屋を作成して、友達と対戦 これをやりたい！」
#   ・入口：右下の 丸い ボタンの 列（たてに 4つ：上から トレーニングセンター → 推し馬 → カードバトル → 思い出フィギュア。まさちゃん 11/16 00:34「丸のアイコン組を少し小さくして！ピッタリ収まるように」・
#       00:47「トレーニングセンターを一番上、カードバトルを思い出フィギュアの上にして」・01:15「この青四角下の空間気になる。大きさ調整して空間があかないようにして！」・
#       01:16「カードバトルを、TENGERカードバトルに名前変えて！」）・丸の 大きさは「壁紙&ボード着せ替え」の すぐ 下 〜 下の タブの すぐ 上 を ぴったり うめる 大きさ（66px まで）・
#       たての 短い 画面（2列 × 2段）でも 右上の ボタンに 重ならない
#   ・メニュー・あそび方・コンピュータと 対戦（出す・オープン・捨て札・効果 6つ を 画面で）・結果と ごほうび（お世話トークン 1こ・5連勝で 3こ・25こ まで）・とちゅうで やめる
#   ・部屋：2つの 画面（ホスト・ゲスト）を、にせの アプリ側（Room.swift の かわり：BroadcastChannel）で つないで さいごまで 対戦・もう 1回・やめる
#   python3 test_cb.py   （ios/cb_assets/ が ある とき だけ 絵の 確かめ。ない とき（CI）も 画面は 動く）
#   ルールの 計算は test_cb_rules.js・対戦の 進め役は test_cb_net.js（node）
import json, os, re, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W); sys.path.insert(0, os.path.join(W, 'kisekae'))
SRV = os.path.join(W, 'srv_cb'); PORT = 8813; APP = f'http://localhost:{PORT}/APP/'
SHOT = os.environ.get('SHOT')          # 画面を 写す フォルダ（見る 用）
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, TARGET='app'))
pth = os.path.join(SRV, 'APP', 'index.html'); html = open(pth, encoding='utf8').read()
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
import cb_art, cb_sfx
CBA = os.path.join(W, 'ios', 'cb_assets'); CBF = cb_art.files() + cb_sfx.files()
HAVE = all(os.path.isfile(os.path.join(CBA, f)) for f in CBF)
if HAVE:
    for f in CBF: shutil.copy(os.path.join(CBA, f), os.path.join(SRV, 'APP', f))
else:
    print('※ 馬カードバトルの 絵と 音（ios/cb_assets）が ない ので、絵の 確かめは とばす（画面は 動く）')
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c: fails.append(label)


# アプリの 窓口の にせもの。部屋（name: 'room'）は Room.swift と 同じ 知らせ方：同じ 部屋番号の 2つの 画面を BroadcastChannel で つなぐ
FAKE = """
window.__NATIVE_INFO = { version: '1.0', build: '7', device: 'phone' };
window.__marks = {};
(function () {
  var st = { mode: '', room: '', ch: null, peer: null, tm: 0, id: Math.random().toString(36).slice(2) };
  function ev(p) { setTimeout(function () { window.__nativeEvent('room', p); }, 5); }
  function stop() { clearInterval(st.tm); if (st.ch) { if (st.peer) st.ch.postMessage({ t: 'gone', id: st.id }); st.ch.close(); } st.ch = null; st.peer = null; st.mode = ''; }
  window.__room = { calls: [], st: st, deny: false };
  window.__roomOp = function (P) {
    window.__room.calls.push(P.op + (P.room ? ':' + P.room : ''));
    if (P.op === 'host' || P.op === 'join') {
      if (!/^[0-9]{4}$/.test(P.room || '')) return { ok: false, why: 'room' };
      stop(); st.mode = P.op; st.room = P.room;
      if (window.__room.deny) { ev({ ev: 'error', why: P.op === 'host' ? 'advertise' : 'browse' }); return { ok: true, state: 'x' }; }
      st.ch = new BroadcastChannel('cbroom' + P.room);
      st.ch.onmessage = function (e) {
        var m = e.data;
        if (st.mode === 'host' && m.t === 'knock' && !st.peer) { st.peer = m.id; st.ch.postMessage({ t: 'welcome', to: m.id, id: st.id }); ev({ ev: 'state', state: 'connecting' }); setTimeout(function () { ev({ ev: 'state', state: 'connected' }); }, 40); }
        else if (st.mode === 'join' && m.t === 'welcome' && m.to === st.id && !st.peer) { st.peer = m.id; clearInterval(st.tm); ev({ ev: 'state', state: 'connecting' }); setTimeout(function () { ev({ ev: 'state', state: 'connected' }); }, 40); }
        else if (m.t === 'data' && m.to === st.id && m.id === st.peer) ev({ ev: 'data', data: m.data });
        else if (m.t === 'gone' && m.id === st.peer) { st.peer = null; ev({ ev: 'state', state: 'idle' }); stop(); }
      };
      if (P.op === 'join') st.tm = setInterval(function () { if (st.ch && !st.peer) st.ch.postMessage({ t: 'knock', id: st.id }); }, 80);
      ev({ ev: 'state', state: P.op === 'host' ? 'hosting' : 'searching' });
      return { ok: true, state: P.op === 'host' ? 'hosting' : 'searching' };
    }
    if (P.op === 'send') { if (!st.peer) return { ok: false }; st.ch.postMessage({ t: 'data', to: st.peer, id: st.id, data: P.data }); return { ok: true }; }
    if (P.op === 'stop') { stop(); return { ok: true }; }
    return { ok: false, why: 'op' };
  };
})();
window.webkit = { messageHandlers: { tengel: { postMessage: function (m) {
  var P = m.payload, val = true;
  if (m.name === 'notify') val = P.op === 'status' ? { ok: true, auth: 'notDetermined' } : P.op === 'opened' ? { ok: true, opened: null } : { ok: true, list: [], scheduled: 0, auth: 'notDetermined' };
  if (m.name === 'iap') val = P.op === 'products' ? { ok: true, products: [] } : { ok: true, list: [], current: [], unfinished: [], active: [] };
  if (m.name === 'marker') { var k = P.key || 'm', M = window.__marks; if (P.op === 'set') { M[k] = P.value || '1'; val = { ok: true }; } else if (P.op === 'del') { delete M[k]; val = { ok: true }; } else val = { ok: true, has: k in M, value: M[k] }; }
  if (m.name === 'room') val = window.__roomOp(P);
  setTimeout(function () { window.__nativeReply(m.id, true, val); }, 15);
} } } };
"""


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


def idle(pg, t=30000):
    pg.wait_for_function("() => window.CBApp && CBApp._t.idle", timeout=t); pg.wait_for_timeout(60)


def open_cb(pg, speed=0.03):
    pg.locator('#cbFab .fabi').click()
    pg.wait_for_function("() => !!window.CBApp && !!document.querySelector('#cbOv.on')", timeout=30000)
    pg.evaluate(f"() => CBApp._t.speed({speed})"); pg.wait_for_timeout(150)
    # 出て すぐ 消える ことば（帯＝.cbban・ふきだし＝.cbtoast）を 覚えて おく（said() で 読んで 空に する）
    pg.evaluate("""() => { if (window.__said) return; window.__said = [];
      const W = (sel, tag) => { const e = document.querySelector('#cbOv ' + sel); let last = ''; new MutationObserver(() => { const s = e.classList.contains('on') ? e.textContent : ''; if (s && s !== last) window.__said.push(tag + ':' + s); last = s; }).observe(e, { childList: true, subtree: true, attributes: true, characterData: true }); };
      W('.cbban', 'ban'); W('.cbtoast', 'toast'); }""")


def said(pg):
    return pg.evaluate("() => { const a = window.__said.slice(); window.__said.length = 0; return a; }")


def acts(pg):
    return [x.inner_text().replace('\n', '') for x in pg.locator('#cbOv .cbact .cbb').all()]


def modbtns(pg):
    return pg.evaluate("() => [...document.querySelectorAll('#cbOv .cbmod .cbb')].map(b => b.textContent.trim())")


def start(pg, h0, h1, deck=''):
    """手札を 決めて コンピュータと 対戦を はじめる。コンピュータは 自分では 動かない（テストが opp() で 相手の 手を 打つ）"""
    pg.evaluate("""([h0, h1, dk]) => { CBApp._think = () => 1e9; CBApp._opt = { hands: [h0.split(''), h1.split('')], deck: dk ? dk.split('') : undefined }; }""", [h0, h1, deck])
    if pg.evaluate("() => CBApp._t.screen") != 'menu': pg.evaluate("() => CBApp._t.menu()")      # 前の 対戦を（勝ち負けに 数えずに）片付けて メニューへ
    pg.locator('#cbOv .cbmenu [data-cb=cpu]').click(); idle(pg)


def opp(pg, a):
    """相手の 席の 手を 打つ（k＝手札の カードの 種類 で 番号を さがす）"""
    r = pg.evaluate("""a => { const m = CBApp._t.match, S = m._.state(), h = S.p[1].hand, U = k => { const c = h.find(x => x.k === String(k)); return c ? c.u : -1; };
      const b = Object.assign({}, a); if (b.k != null) { b.u = U(b.k); delete b.k; } if (b.dropk != null) { b.drop = Array.isArray(b.dropk) ? b.dropk.map(U) : U(b.dropk); delete b.dropk; }
      if (b.pickk != null) { const c = S.p[0].hand.find(x => x.k === String(b.pickk)); b.pick = c ? c.u : -1; delete b.pickk; }
      if (b.use) { const w = Object.assign({}, b.use); if (w.p6k != null) { const c = S.p[0].hand.find(x => x.k === String(w.p6k)); w.p6 = c ? c.u : -1; delete w.p6k; } if (w.u5k != null) { w.u5 = U(w.u5k); delete w.u5k; } b.use = w; }
      return m._.apply(1, b); }""", a)
    idle(pg)
    return r


def fab_ok(rc, vw, tab, two=False):
    """右下の 丸い ボタン（順：トレーニングセンター・推し馬・カードバトル・思い出フィギュア）の ならび。
       two=False：たてに 1列（上から 順に・まん中が そろう・すきまは 8px まで）／two=True（たての 短い 画面）：2列 × 2段＝左の 列：トレーニングセンターの すぐ 下に 推し馬／右の 列：カードバトルの すぐ 下に 思い出フィギュア。
       どれも 重ならない・画面の 中・下の タブの 上"""
    if len(rc) != 4: return False
    mid = lambda r: (r[0] + r[2]) / 2
    under = lambda a, b: a[3] <= b[1] + 1 and b[1] - a[3] <= 8 and abs(mid(a) - mid(b)) <= 2
    tc, oshi, cb, fig = rc
    if two: ok = under(tc, oshi) and under(cb, fig) and abs(cb[1] - tc[1]) <= 1 and cb[0] >= tc[2] - 1 and cb[0] - tc[2] <= 8 and fig[0] >= oshi[2] - 1
    else: ok = under(tc, oshi) and under(oshi, cb) and under(cb, fig)
    lap = any(a[0] < c[2] - 1 and c[0] < a[2] - 1 and a[1] < c[3] - 1 and c[1] < a[3] - 1 for i, a in enumerate(rc) for c in rc[i + 1:])
    return bool(ok and not lap and min(r[0] for r in rc) >= 0 and max(r[2] for r in rc) <= vw and max(r[3] for r in rc) <= tab - 3)


def tap(pg, k):
    """自分の 手札の カード（種類 k）を タップ"""
    pg.locator(f'#cbOv .cbhand .cbc:has(img[src="cb_s{k}.webp"])').first.click(); pg.wait_for_timeout(80)


def play(pg, k, btn='set'):
    tap(pg, k); pg.locator(f'#cbOv .cbmod [data-cb={btn}]').click(); idle(pg)


V = "() => CBApp._t.view"
HAND = "() => CBApp._t.view.my.hand.map(c => c.k).sort().join('')"
DOMHAND = "() => [...document.querySelectorAll('#cbOv .cbhand .cbc img')].map(i => i.getAttribute('src').replace('cb_s', '').replace('.webp', '')).join('')"
MSG = "() => document.querySelector('#cbOv .cbmsg').textContent"
TOAST = "() => { const t = document.querySelector('#cbOv .cbtoast'); return t.classList.contains('on') ? t.textContent : ''; }"
SLOT = "() => ['op', 'my'].map(s => { const e = document.querySelector('#cbOv .cbslot.' + s), i = e.querySelector('img'), t = e.querySelector('.tag'); return (i ? i.getAttribute('src').replace('cb_s', '').replace('.webp', '') : '-') + (t ? ':' + t.textContent : ''); }).join(' ')"
PIPS = "() => ['op', 'my'].map(p => document.querySelectorAll('#cbOv .cbpips[data-p=' + p + '] i.on').length).join('-')"
TC = "() => { const s = JSON.parse(localStorage.getItem('tengel.tc') || 'null'); return window.TCApp && TCApp.state ? TCApp.state.stock : s ? s.stock : null; }"

try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo')
        ctx.add_init_script(FAKE)
        pg = ctx.new_page(); errs = []; reqs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('request', lambda r: reqs.append(r.url.split('/')[-1].split('?')[0]))
        pg.goto(APP); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(700)

        print('■ 入口：右下の 丸い ボタン（たてに 4つ）の 上から 3番目 ＝ 推し馬の 下・思い出フィギュアの 上')
        pg.evaluate("() => { const m = document.getElementById('minibar'); if (m) m.hidden = true; }"); pg.wait_for_timeout(500)
        FAB = """() => { const R = e => { const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; };
          const ks = [...document.querySelectorAll('#fabCol > button')].sort((a, b) => getComputedStyle(a).order - getComputedStyle(b).order), c = document.querySelector('#cbFab');
          if (!c) return null; const im = c.querySelector('.fabi img'), ir = c.querySelector('.fabi').getBoundingClientRect();
          const top = ['planBtn', 'kiseBtn'].map(i => document.getElementById(i)).filter(Boolean).map(R);
          return { ids: ks.map(k => k.id), rc: ks.map(R), order: getComputedStyle(c).order, iws: ks.map(k => Math.round(k.querySelector('.fabi').getBoundingClientRect().width)), g2: document.querySelector('#fabCol').classList.contains('g2'), lfs: parseFloat(getComputedStyle(c.querySelector('.fabl')).fontSize), name: c.querySelector('.fabl').textContent, aria: c.getAttribute('aria-label'), img: im ? im.getAttribute('src') : '', nat: im ? im.naturalWidth : 0,
            iw: Math.round(ir.width), tab: Math.round(document.querySelector('.tabbar').getBoundingClientRect().top), hb: Math.round(document.querySelector('header.top').getBoundingClientRect().bottom), top: top, vw: innerWidth, vh: innerHeight, api: typeof window.TengelCB }; }"""
        pg.wait_for_function("() => !TengelFab.busy()", timeout=8000); pg.wait_for_timeout(300)      # はじめの 2秒は 丸の 大きさを 決め直さない（落ち着いて から）
        fb = pg.evaluate(FAB)
        check(fb is not None and fb['ids'] == ['tcFab', 'oshiFab', 'cbFab', 'figFab'] and fb['order'] == '2' and fb['api'] == 'object',
              f'順は トレーニングセンター → 推し馬 → カードバトル → 思い出フィギュア（まさちゃん 11/16 00:47）{fb and fb["ids"]}')
        low0 = fb['tab'] - max(r[3] for r in fb['rc'])
        check(fb['name'] == 'TENGER\nカードバトル' and fb['aria'].startswith('TENGERカードバトル') and fb['iws'] == [66] * 4 and not fb['g2'] and fb['lfs'] == 9.5 and fab_ok(fb['rc'], 390, fb['tab']) and 3 <= low0 <= 5,
              f'たてに 4つ（1列）・丸い 絵は 4つとも 同じ 大きさ（ここは 上の絵が ない ので もとの 66px）・下に 名前の 札「TENGER／カードバトル」（まさちゃん 11/16 01:16・字 {fb["lfs"]}px）・重ならない・'
              f'列の 下は 下の タブの すぐ 上（すきま {low0}px：下に 空間を あけない）（{fb["rc"]}）')
        gap0 = min(r[1] for r in fb['rc']) - max(t[3] for t in fb['top'])
        check(all(r[1] >= t[3] + 3 or r[0] >= t[2] or r[2] <= t[0] for r in fb['rc'] for t in fb['top']) and min(r[1] for r in fb['rc']) > fb['hb'] + 60 and gap0 >= 3,
              f'右上の「作戦会議」「壁紙&ボード着せ替え」に 重ならない（列の 上 {min(r[1] for r in fb["rc"])}・右上の ボタンの 下 {[t[3] for t in fb["top"]]}。壁紙ごとの すきまは test_plan_entry.py が 測る）')
        if HAVE:
            check(fb['img'] == 'cb_icon.webp' and fb['nat'] == 240, f'ボタンの 絵（cb_icon.webp・240×240）')
        else:
            check(pg.locator('#cbFab .fabt').count() == 1 and pg.locator('#cbFab .fabt').inner_text() == 'バトル', '絵が ない とき：字の 丸「バトル」')
        shot(pg, 'cb_fab')
        # たての 短い 画面（iPhone SE：375×647）でも 重ならない
        pg2 = ctx.new_page(); pg2.set_viewport_size({'width': 375, 'height': 647}); pg2.goto(APP); pg2.wait_for_timeout(1300); gate(pg2); pg2.wait_for_timeout(600)
        pg2.evaluate("() => { const m = document.getElementById('minibar'); if (m) m.hidden = true; }"); pg2.wait_for_timeout(400)
        pg2.wait_for_function("() => !TengelFab.busy()", timeout=8000); pg2.wait_for_timeout(300)
        f2 = pg2.evaluate(FAB); g2 = min(r[1] for r in f2['rc']) - max(t[3] for t in f2['top']); low2 = f2['tab'] - max(r[3] for r in f2['rc'])
        check(f2['ids'] == ['tcFab', 'oshiFab', 'cbFab', 'figFab'] and f2['iws'] == [66] * 4 and not f2['g2'] and fab_ok(f2['rc'], 375, f2['tab']) and 3 <= g2 <= 10 and 3 <= low2 <= 5,
              f'たての 短い 画面（iPhone SE：375×647・上の絵なし）：たてに 4つ・丸 {f2["iws"][0]}px で「壁紙&ボード着せ替え」の すぐ 下（すきま {g2}px）〜 下の タブの すぐ 上（すきま {low2}px）を ぴったり うめる')
        shot(pg2, 'cb_fab_small')
        # 上の絵が ある とき（壁紙。ここでは 同じ 高さの 箱を 入れて ためす：上の絵 160px − 上の よせ 16px ＋ 下の あき 14px）：着せ替えの ボタンが 下がる → 丸を 小さく して ぴったり うめる。
        #   本物の iPhone の 大きさ（アプリの 画面＝iPhone の 高さ − 上の 時計の 帯・下は ホームバーの ぶん）で：丸の 大きさは 画面ごとに 決まる。iPhone SE は たてに 入らない → 2列 × 2段（判定の 帯の 上）
        pg2.evaluate("() => { const v = document.getElementById('v-judge'), s = document.createElement('div'); s.id = 'cbSp'; s.style.height = '158px'; v.insertBefore(s, v.firstChild); }")
        sizes = {}
        for dn, vw3, vh3, sab3, two3 in (('iPhone SE', 375, 647, 0, True), ('iPhone 12/13 mini', 375, 762, 34, False), ('iPhone 12〜14', 390, 797, 34, False), ('iPhone 16 Pro', 402, 812, 34, False), ('iPhone Plus／Pro Max', 430, 873, 34, False)):
            pg2.set_viewport_size({'width': vw3, 'height': vh3}); pg2.evaluate("(s) => document.documentElement.style.setProperty('--bottom-inset', s + 'px')", sab3); pg2.wait_for_timeout(500)
            pg2.wait_for_function("() => !TengelFab.busy()", timeout=8000); pg2.wait_for_timeout(300)
            f3 = pg2.evaluate(FAB); g3 = min(r[1] for r in f3['rc']) - max(t[3] for t in f3['top']); low3 = f3['tab'] - max(r[3] for r in f3['rc']); d3 = f3['iws'][0]; sizes[dn] = d3
            if two3:
                check(f3['iws'] == [d3] * 4 and 36 <= d3 <= 66 and f3['g2'] and fab_ok(f3['rc'], vw3, f3['tab'], two=True) and g3 >= 3 and 33 <= low3 <= 50,
                      f'{dn}（アプリの 画面 {vw3}×{vh3}・上の絵 あり）：たてに 4つは 入らない（丸を 36px に しても）→ 2列 × 2段（左：トレーニングセンター・推し馬／右：カードバトル・思い出フィギュア）・丸 {d3}px・'
                      f'右上の ボタンに 重ならない（すきま {g3}px）・判定の 帯の 上（下の タブから {low3}px）')
            else:
                check(f3['iws'] == [d3] * 4 and 36 <= d3 <= 66 and not f3['g2'] and fab_ok(f3['rc'], vw3, f3['tab']) and (3 <= g3 <= 10 or d3 == 66) and 3 <= low3 <= 5 and f3['lfs'] >= 7,
                      f'{dn}（アプリの 画面 {vw3}×{vh3}・下の あき {sab3}・上の絵 あり）：たてに 4つ・丸 {d3}px（名前の 字 {round(f3["lfs"], 1)}px）で「壁紙&ボード着せ替え」の すぐ 下（すきま {g3}px）〜 下の タブの すぐ 上（すきま {low3}px）を ぴったり うめる')
        check(sizes['iPhone 12/13 mini'] < sizes['iPhone 12〜14'] < sizes['iPhone Plus／Pro Max'] and 50 <= sizes['iPhone 12〜14'] <= 62, f'丸の 大きさは 画面が 大きい ほど 大きい {sizes}')
        pg2.evaluate("() => { document.documentElement.style.removeProperty('--bottom-inset'); document.getElementById('cbSp').remove(); }")

        print('■ メニュー・あそび方')
        open_cb(pg)
        m = pg.evaluate("() => ({ scr: CBApp._t.screen, h1: document.querySelector('#cbOv .cbmenu h1').textContent, rec: document.querySelector('#cbOv .cbmenu .rec').textContent, btn: [...document.querySelectorAll('#cbOv .cbmenu .cbb')].map(b => b.textContent.replace(/\\s+/g, ' ').trim()), dis: [...document.querySelectorAll('#cbOv .cbmenu .cbb')].map(b => b.disabled), lg: document.querySelector('#cbOv .cbmenu .lg').naturalWidth })")
        check(m['scr'] == 'menu' and m['h1'].replace('\n', '').replace(' ', '') == 'TENGERカードバトル' and m['btn'] == ['← もどる', 'コンピュータと 対戦', '部屋を 作る友だちと 対戦', '部屋に 入る友だちと 対戦', 'あそび方'] and not any(m['dis']),
              f'メニュー：コンピュータと 対戦・部屋を 作る・部屋に 入る・あそび方（{m["btn"]}）')
        check(m['rec'] == '勝つと お世話トークン 1こ・5連勝 ごとに 3こ' and (not HAVE or m['lg'] == 720), f'ごほうびの 説明（{m["rec"]}）')
        check(reqs.count('cb_bundle.js') == 1 and 'cb_bundle.js' not in reqs[:reqs.index('cb_bundle.js')][:5], '本体（cb_bundle.js）は ボタンを 押した ときに 1回 だけ 読む')
        shot(pg, 'cb_menu')
        pg.locator('#cbOv .cbmenu [data-cb=help]').click(); pg.wait_for_timeout(200)
        ht = pg.locator('#cbOv .cbhelp .bd').inner_text()
        need = ['手札は 5まい。3ターンで 勝負', '強い カードの 勝ち', '勝った 数が 多い 人の 勝ち', '神様馬と 幻の馬が いちばん 強い', '1 が いちばん 強くて、7 が いちばん 弱い', '「かぶり」＝どちらも 負け', '1〜7 が 4まい ずつ・神様馬 1まい・幻の馬 1まい',
                '① セット', 'セットしたら もう 変えられない', '② 効果タイム', '2人とも セットしたら、使える 効果が ある 人に「効果を 使う？」と 聞くよ', '③ オープン', '次の ターンの はじめに、使うか えらぶよ', '効果が 出る 順番は 6 → 5 → 7 → 4',
                '終わった ターンの 捨て札', '効果で 捨てた カード',
                '7：3まい そろえて 交換', '6：2まい 見せて 手札を 見る', '5：山札から セット', '4：見せて 強制交換', '神様馬：勝ったら 手札を 見る', '幻の馬：勝ったら 手札を 交換', 'お世話トークン 1こ', '5連勝 ごとに 3こ', '部屋番号（4けた）', '近くに いる 友だち']
        miss = [x for x in need if x not in ht]
        check(pg.evaluate("() => CBApp._t.screen") == 'help' and not miss and pg.locator('#cbOv .cbhelp .ord img').count() == 9 and pg.locator('#cbOv .cbhelp .ef').count() == 6, f'あそび方：勝負の しかた・1ターンの 流れ（セット → 効果タイム → オープン）・強さ（9まいの 並び）・効果 6つ・捨て札・ごほうび・部屋（ない 文 {miss}）')
        shot(pg, 'cb_help')
        pg.locator('#cbOv [data-cb=helpx]').click(); pg.wait_for_timeout(150)
        check(pg.evaluate("() => CBApp._t.screen") == 'menu', 'もどる → メニュー')

        print('■ コンピュータと 対戦：セット → オープン → 3ターン')
        start(pg, '12367', '23567')
        v = pg.evaluate(V)
        check(pg.evaluate("() => CBApp._t.screen") == 'game' and v['turn'] == 1 and pg.evaluate(DOMHAND) == '12367' and pg.locator('#cbOv .cbohand .cbc').count() == 5 and pg.locator('#cbOv .cbdeck .cbn').inner_text() == '20' and pg.locator('#cbOv .cbdis .cbn').inner_text() == '0'
              and pg.locator('#cbOv .cbturn').inner_text().replace('\n', '') == 'ターン 1／3' and pg.locator('#cbOv .cbopp .cbwho b').inner_text() == 'コンピュータ' and pg.evaluate(PIPS) == '0-0',
              f'はじめ：手札 5まい（強い 順）・相手の 手札 5まい（うら）・山札 20・捨て札 0・ターン 1／3（{pg.evaluate(DOMHAND)}）')
        check(all(s == 'cb_sb.webp' for s in pg.evaluate("() => [...document.querySelectorAll('#cbOv .cbohand .cbc img')].map(i => i.getAttribute('src'))")) and 'セットする カードを えらんでね' in pg.evaluate(MSG) and pg.locator('#cbOv .cbglow.on').count() == 1 and acts(pg) == [],
              '相手の 手札は ぜんぶ うら・「セットする カードを えらんでね」・自分の わくが 光る')
        geo = pg.evaluate("""() => { const R = s => { const r = document.querySelector('#cbOv ' + s).getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; };
          const cs = [...document.querySelectorAll('#cbOv .cbhand .cbc')].map(c => c.getBoundingClientRect());
          return { top: R('.cbtop'), opp: R('.cbohand'), board: R('.cbboard'), msg: R('.cbmsg'), hand: R('.cbhand'), act: R('.cbact'), cw: Math.round(cs[0].width), ch: Math.round(cs[0].height), left: Math.round(cs[0].left), right: Math.round(cs[4].right), step: Math.round(cs[1].left - cs[0].left) }; }""")
        check(geo['top'][3] <= geo['opp'][1] and geo['opp'][3] <= geo['board'][1] + 30 and geo['board'][3] <= geo['msg'][1] + 20 and geo['msg'][3] <= geo['hand'][1] + 30 and geo['hand'][3] <= geo['act'][1] + 1 and geo['act'][3] <= 844
              and geo['board'][0] == 0 and geo['board'][2] == 390 and abs((geo['board'][3] - geo['board'][1]) - 390 * 941 / 1672) < 2 and geo['left'] >= 0 and geo['right'] <= 390 and abs(geo['ch'] - geo['cw'] * 1.5) < 1.5 and geo['step'] >= geo['cw'] * 0.69,
              f'ならび：上から 相手の 手札 → ボード（幅 いっぱい・絵の たて横の まま）→ ことば → 手札 → ボタン。手札は 画面の 中・重なりは 30% まで（カード {geo["cw"]}×{geo["ch"]}・ずれ {geo["step"]}）')
        shot(pg, 'cb_turn1')
        tap(pg, '1')
        md = pg.evaluate("() => ({ on: CBApp._t.modOn(), img: document.querySelector('#cbOv .cbmod .big img').getAttribute('src') })")
        check(md['on'] and md['img'] == 'cb_c1.webp' and modbtns(pg) == ['この カードを セットするセットしたら もう 変えられないよ', 'もどる'], f'カードを タップ → 大きい カード（cb_c1.webp）と「この カードを セットする（セットしたら もう 変えられないよ）」「もどる」（{modbtns(pg)}）')
        shot(pg, 'cb_card')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(80)
        check(not pg.evaluate("() => CBApp._t.modOn()") and pg.evaluate(V)['my']['set'] is None, 'もどる → 何も セットして いない（押す までは えらび直せる）')
        print('■ セットしたら もう 変えられない（まさちゃん 23:12）')
        play(pg, '1')
        v = pg.evaluate(V)
        check(v['my']['set'] and v['my']['set']['k'] == '1' and pg.evaluate(SLOT) == '- 1:セット ずみ' and pg.evaluate(DOMHAND) == '2367' and 'コンピュータが えらんで いるよ' in pg.evaluate(MSG) and pg.locator('#cbOv .cbglow.on').count() == 0,
              f'セットした：自分の わくに カード（「セット ずみ」）・手札 4まい・「コンピュータが えらんで いるよ…」（{pg.evaluate(SLOT)}）')
        tap(pg, '2')
        check(modbtns(pg) == ['もどる'], 'セットした あとは 手札を タップしても 見る だけ（「セットする」は 出ない）')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        pg.locator('#cbOv .cbslot.my .cbc').click(); pg.wait_for_timeout(80)
        check(modbtns(pg) == ['もどる'] and 'もう 変えられない' in pg.locator('#cbOv .cbmod').inner_text() and pg.locator('#cbOv .cbmod .big img').get_attribute('src') == 'cb_c1.webp', 'セットした カードを タップ → 見る だけ（「もう 変えられない」）')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        r2 = pg.evaluate("async () => { const v = CBApp._t.view, a = await CBApp._t.match.act({ t: 'set', u: v.my.hand[0].u }), b = await CBApp._t.match.act({ t: 'swap', u: v.my.hand[0].u }); return [a.ok, b.ok, CBApp._t.match._.state().p[0].set.c.k, CBApp._t.match._.state().p[0].hand.length]; }")
        check(r2 == [False, False, '1', 4], f'もう 1まい セットする 手・入れかえる 手を 送っても 受けつけない（セットした 1 の まま）{r2}')
        pg.evaluate("() => { window.__seen = []; const mo = new MutationObserver(() => { const m = document.querySelector('#cbOv .cbmod'); if (m.classList.contains('cbopen')) { const t = m.querySelector('.cbres'); window.__seen.push((m.querySelector('h3') || {}).textContent + '|' + (t ? t.textContent : '') + '|' + [...m.querySelectorAll('.cbflip img.fc')].map(i => i.getAttribute('src')).join(',')); } }); mo.observe(document.querySelector('#cbOv .cbmod'), { childList: true, subtree: true, attributes: true, characterData: true }); window.__mo = mo; }")
        said(pg)
        r = opp(pg, {'t': 'set', 'k': 2})
        seen = pg.evaluate("() => window.__seen"); sd = said(pg)
        v = pg.evaluate(V)
        check(r['ok'] and any('ターン 1　オープン！' in s and '勝ち！' in s and '1 が 2 に 勝ったよ' in s and 'cb_c1.webp,cb_c2.webp' in s for s in seen) and not any('効果タイム' in s for s in sd),
              f'相手も セットした（使える 効果は ない）→ そのまま オープン：大きい カード 2まい（自分 1・相手 2）「勝ち！ 1 が 2 に 勝ったよ」（{seen[-1] if seen else None}）')
        check(v['turn'] == 2 and v['my']['wins'] == 1 and pg.evaluate(PIPS) == '0-1' and pg.evaluate(SLOT) == '- -' and pg.locator('#cbOv .cbdis .cbn').inner_text() == '2' and pg.locator('#cbOv .cbturn').inner_text().replace('\n', '') == 'ターン 2／3' and pg.locator('#cbOv .cbohand .cbc').count() == 4,
              f'2ターン目：勝った しるし 1つ・出した 2まいは 捨て札（2）・わくは 空（しるし {pg.evaluate(PIPS)}）')
        print('■ 捨て札を タップ → 確認できる（まさちゃん 23:15）')
        dg = pg.evaluate("""() => { const R = s => { const e = document.querySelector('#cbOv ' + s); if (!e) return null; const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)]; };
          const b = document.querySelector('#cbOv .cbdis'), c = b.getBoundingClientRect(), hit = document.elementFromPoint(c.left + c.width / 2, c.top + c.height / 2);
          return { btn: R('.cbdis'), pile: R('.cbdis .pl img'), src: document.querySelector('#cbOv .cbdis .pl img').getAttribute('src'), n: b.querySelector('.cbn').textContent, aria: b.getAttribute('aria-label'), hit: !!hit && (hit === b || b.contains(hit)), slot: R('.cbslot.my'), deck: R('.cbdeck'), board: R('.cbboard') }; }""")
        check(dg['src'] == 'cb_s2.webp' and dg['n'] == '2' and dg['aria'] == '捨て札を 見る（2まい）' and dg['pile'][2] >= 30 and dg['hit'] and dg['btn'][2] >= 44 and dg['btn'][3] >= 44
              and dg['btn'][0] + dg['btn'][2] <= dg['slot'][0] and dg['btn'][0] >= 0 and dg['btn'][1] >= dg['board'][1] and dg['btn'][1] + dg['btn'][3] <= dg['board'][1] + dg['board'][3],
              f'ボードの 捨て札：1番 上の カード（さいごに 捨てた 2）が 見える・数（2）・押せる 広さ {dg["btn"][2]}×{dg["btn"][3]}（44 以上）・まん中の わくに かからない')
        pg.locator('#cbOv [data-cb=discard]').click(); pg.wait_for_timeout(80)
        DM = """() => { const m = document.querySelector('#cbOv .cbmod'); return { h: (m.querySelector('h3') || {}).textContent, h4: [...m.querySelectorAll('.cbdl h4')].map(x => x.textContent),
          turns: [...m.querySelectorAll('.cbdl .row[data-dt]')].map(r => r.querySelector('b').textContent + '|' + [...r.querySelectorAll('.pr')].map(p => p.querySelector('span').textContent + '=' + [...p.querySelectorAll('img')].map(i => i.getAttribute('src').replace('cb_s', '').replace('.webp', '')).join('')).join('|')),
          effs: [...m.querySelectorAll('.cbdl .row[data-de]')].map(r => r.querySelector('b').textContent + '|' + [...r.querySelectorAll('.pr')].map(p => p.querySelector('span').textContent + '=' + [...p.querySelectorAll('img')].map(i => i.getAttribute('src').replace('cb_s', '').replace('.webp', '')).join('')).join('|')),
          none: [...m.querySelectorAll('.cbdl .none')].map(x => x.textContent), t: m.textContent }; }"""
        dm = pg.evaluate(DM)
        check(dm['h'] == '捨て札（2まい）' and dm['h4'] == ['終わった ターンの 捨て札', '効果で 捨てた カード'] and dm['turns'] == ['ターン 1|あなた=1|コンピュータ=2'] and dm['effs'] == [] and len(dm['none']) == 1 and 'まだ ないよ' in dm['none'][0] and '山札の のこり 20まい' in dm['t'],
              f'捨て札を タップ → 「終わった ターンの 捨て札」（ターン 1：あなた 1・コンピュータ 2）と「効果で 捨てた カード」（まだ ない）に 分けて 出る（{dm["turns"]}）')
        shot(pg, 'cb_discard')
        pg.locator('#cbOv .cbmod .cbdl .cbc').first.click(); pg.wait_for_timeout(80)
        check(pg.locator('#cbOv .cbmod .big img').get_attribute('src') == 'cb_c1.webp' and '捨て札の カード' in pg.locator('#cbOv .cbmod').inner_text() and modbtns(pg) == ['もどる'], '捨て札の カードを タップ → 大きく 見られる')
        pg.locator('#cbOv .cbmod .cbb').click(); pg.wait_for_timeout(80)
        check(pg.evaluate(DM)['h'] == '捨て札（2まい）', '「もどる」→ 捨て札の 窓に もどる')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        check(not pg.evaluate("() => CBApp._t.modOn()"), '「もどる」→ 対戦の 画面')
        opp(pg, {'t': 'set', 'k': 3})
        check(pg.evaluate(SLOT) == 'b -' and 'コンピュータは もう セットしたよ' in pg.evaluate(MSG) and pg.locator('#cbOv .cbohand .cbc').count() == 3, f'相手が 先に セットした：相手の わくに うらの カード・「コンピュータは もう セットしたよ」（{pg.evaluate(SLOT)}）')
        pg.evaluate("() => { window.__seen = []; }")
        play(pg, '3')
        seen = pg.evaluate("() => window.__seen")
        check(any('かぶり！' in s and '同じ カード（3）＝どちらも 負け' in s for s in seen) and pg.evaluate(PIPS) == '0-1' and pg.evaluate(V)['turn'] == 3, f'3 と 3 → 「かぶり！ どちらも 負け」（しるしは ふえない）（{seen[-1] if seen else None}）')
        pg.locator('#cbOv [data-cb=discard]').click(); pg.wait_for_timeout(80); dm = pg.evaluate(DM)
        check(dm['h'] == '捨て札（4まい）' and dm['turns'] == ['ターン 1|あなた=1|コンピュータ=2', 'ターン 2|あなた=3|コンピュータ=3'], f'2ターン目が 終わった → 捨て札の 窓に ターン 2 が ふえる（{dm["turns"]}）')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        pg.evaluate("() => { window.__seen = []; }")
        play(pg, '6'); opp(pg, {'t': 'set', 'k': 5})
        seen = pg.evaluate("() => window.__seen")
        check(any('負け…' in s and '5 の ほうが 強いよ' in s for s in seen), f'6 と 5 → 「負け… 5 の ほうが 強いよ」')
        pg.wait_for_function("() => { const g = document.querySelector('#cbOv .cbend .gift'); return CBApp._t.ended && g && g.textContent.length > 3; }", timeout=30000)
        e = pg.evaluate("() => ({ h: document.querySelector('#cbOv .cbend h3').textContent, sc: document.querySelector('#cbOv .cbend .sc').textContent, g: document.querySelector('#cbOv .cbend .gift').textContent, btn: [...document.querySelectorAll('#cbOv .cbend .cbb')].map(b => b.textContent), st: CBApp._t.state, turn: document.querySelector('#cbOv .cbturn').textContent })")
        check(e['h'] == '同点！' and e['sc'].startswith('1 － 1') and e['btn'] == ['もう 1回', 'メニューへ'] and e['st']['draw'] == 1 and e['st']['streak'] == 0 and e['st']['win'] == 0 and '同点' in e['g'] and e['turn'] == 'けっか',
              f'3ターン 終わり：1勝 1勝 →「同点！」・「もう 1回」「メニューへ」（{e["h"]}・{e["sc"]}・{e["g"]}）')
        shot(pg, 'cb_end_draw')

        print('■ 効果タイム：2人とも セットしたら、効果を 使うか えらぶ（まさちゃん 23:12）― 7（3まい 交換）')
        start(pg, '77712', '12345', '346')
        tap(pg, '7')
        check(acts(pg) == [] and modbtns(pg) == ['この カードを セットするセットしたら もう 変えられないよ', 'もどる'], 'セットの 前：効果の ボタンは どこにも 出ない（7 が 3まい あっても、まず セット）')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        play(pg, '1')
        check(acts(pg) == [] and 'コンピュータが えらんで いるよ' in pg.evaluate(MSG), '自分だけ セットした：まだ 効果は 聞かれない（相手の セットを 待つ）')
        said(pg); pg.evaluate("() => { window.__seen = []; }")
        opp(pg, {'t': 'set', 'k': 2})
        sd = said(pg); md = pg.evaluate("() => CBApp._t.mode")
        check(any(s.startswith('ban:効果タイム') and 'カードの 効果を 使うか えらんでね' in s for s in sd) and pg.evaluate(V)['phase'] == 'eff' and md['k'] == 'eff' and md['q'] == '7' and md['step'] == 'ask'
              and pg.evaluate(MSG) == '効果タイム！ 7 の 効果を 使う？\n7 を 3まい 山札に もどして、新しく 3まい 引けるよ' and acts(pg) == ['使わない', '7 の 効果を 使う'] and pg.evaluate(SLOT) == 'b 1:セット ずみ' and pg.evaluate("() => window.__seen.length") == 0,
              f'2人とも セットした →「効果タイム」→「7 の 効果を 使う？」（使わない／7 の 効果を 使う）。オープンは まだ（{pg.evaluate(SLOT)}）')
        shot(pg, 'cb_eff_ask')
        tap(pg, '7'); check(modbtns(pg) == ['もどる'], '効果タイムの あいだ：手札を タップしても 見る だけ（セットし直せない）')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        pg.locator('#cbOv .cbact [data-cb=effyes]').click(); idle(pg)
        sd = said(pg); seen = pg.evaluate("() => window.__seen")
        check(pg.evaluate(HAND) == '2346' and pg.evaluate(DOMHAND) == '2346' and pg.locator('#cbOv .cbdeck .cbn').inner_text() == '20' and any('7 を 3まい もどして、新しく 3まい 引いたよ' in s for s in sd)
              and any('勝ち！' in s for s in seen) and pg.evaluate(V)['turn'] == 2 and acts(pg) == [],
              f'「使う」→ 7 を 3まい もどして 3まい 引いた（手札 {pg.evaluate(DOMHAND)}・山札 20 の まま）→ オープン → 2ターン目')
        start(pg, '77712', '12345'); play(pg, '1'); opp(pg, {'t': 'set', 'k': 2}); pg.evaluate("() => { window.__seen = []; }")
        pg.locator('#cbOv .cbact [data-cb=effno]').click(); idle(pg)
        check(pg.evaluate(HAND) == '2777' and any('勝ち！' in s for s in pg.evaluate("() => window.__seen")) and pg.evaluate(V)['turn'] == 2, '「使わない」→ 手札は そのまま オープン')

        print('■ 効果タイム：6（2まい 見せて 相手の 手札を 見る）')
        start(pg, '66123', '12345'); play(pg, '1'); opp(pg, {'t': 'set', 'k': 2})
        check(pg.evaluate(MSG) == '効果タイム！ 6 の 効果を 使う？\n6 を 2まい 見せて、相手の 手札を 1まい 見られるよ' and acts(pg) == ['使わない', '6 の 効果を 使う'], '6 が 2まい →「6 の 効果を 使う？」')
        pg.locator('#cbOv .cbact [data-cb=effyes]').click(); pg.wait_for_timeout(80)
        pm = pg.evaluate("() => ({ h: document.querySelector('#cbOv .cbmod h3').textContent, n: document.querySelectorAll('#cbOv .cbmod .pick .cbc').length, t: document.querySelector('#cbOv .cbmod p').textContent })")
        check(pm['h'] == '6 の 効果' and pm['n'] == 4 and '6 を 2まい 相手に 見せるよ' in pm['t'], f'「使う」→ えらぶ 窓：相手の 手札 4まい（うら）から 1まい')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        check(pg.evaluate("() => CBApp._t.mode.step") == 'ask' and acts(pg) == ['使わない', '6 の 効果を 使う'] and pg.evaluate(V)['phase'] == 'eff', '「もどる」→ まだ 決まって いない（もう一度 えらべる）')
        pg.locator('#cbOv .cbact [data-cb=effyes]').click(); pg.wait_for_timeout(80)
        pg.evaluate("() => { window.__seen = []; }")
        pg.locator('#cbOv .cbmod .pick .cbc').nth(2).click(); idle(pg)
        seen = pg.evaluate("() => window.__seen"); v = pg.evaluate(V)
        kn = [c['k'] for c in v['op']['hand'] if c['k']]
        check(len(kn) == 1 and any('6 の 効果' in s and f'cb_c{kn[0]}.webp' in s for s in seen) and pg.locator(f'#cbOv .cbohand .cbc img[src="cb_s{kn[0]}.webp"]').count() == 1 and pg.locator('#cbOv .cbohand .cbc img[src="cb_sb.webp"]').count() == 3 and v['turn'] == 2,
              f'見た カード（{kn}）を 大きく 見せる → オープン → 相手の 手札の 中で その 1まい だけ 表')
        pg.locator(f'#cbOv .cbohand .cbc img[src="cb_s{kn[0]}.webp"]').locator('..').click(); pg.wait_for_timeout(80)
        check('効果で 見た 相手の カード' in pg.locator('#cbOv .cbmod').inner_text(), '見た カードは タップで 大きく 見られる')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click()
        # 相手が 6 の 効果を 使う：自分は 待つ → 見られた カードに 目の しるし
        start(pg, '12367', '66123'); play(pg, '1'); said(pg)
        opp(pg, {'t': 'set', 'k': 2}); sd = said(pg)
        check(any(s.startswith('ban:効果タイム') and 'コンピュータが 効果を 使うか えらぶよ' in s for s in sd) and 'コンピュータが 効果を 使うか えらんで いるよ' in pg.evaluate(MSG) and acts(pg) == [] and pg.evaluate(V)['wait'] is True,
              '相手だけ 使える 効果が ある：「コンピュータが 効果を 使うか えらんで いるよ…」（自分は 待つ）')
        r = opp(pg, {'t': 'eff', 'use': {'p6k': 2}}); sd = said(pg)
        check(r['ok'] and pg.locator('#cbOv .cbhand .cbc .eye').count() == 1 and pg.locator('#cbOv .cbhand .cbc:has(.eye) img').get_attribute('src') == 'cb_s2.webp' and pg.locator('#cbOv .cbohand .cbc img[src="cb_s6.webp"]').count() == 2
              and any('あなたの 手札を 1まい 見たよ' in s for s in sd), '相手が 6 の 効果：相手の 6 が 2まい 表に・見られた 自分の カード（2）に 目の しるし')
        tap(pg, '2'); check('この カードは 相手に 見られて いるよ' in pg.locator('#cbOv .cbmod').inner_text(), '見られた カードを タップ →「相手に 見られて いるよ」')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click()
        shot(pg, 'cb_seen')
        # 2人とも えらぶ：相手が 先に 決めても、自分の えらび とちゅうは 消えない・相手が 何を 使うかは わからない
        start(pg, '66123', '77712', '345'); play(pg, '1'); opp(pg, {'t': 'set', 'k': 2})
        pg.locator('#cbOv .cbact [data-cb=effyes]').click(); pg.wait_for_timeout(80); said(pg)
        r = opp(pg, {'t': 'eff', 'use': {'x7': True}}); sd = said(pg)
        check(r['ok'] and pg.evaluate("() => CBApp._t.modOn()") and pg.locator('#cbOv .cbmod .pick .cbc').count() == 4 and pg.evaluate("() => CBApp._t.mode.k") == 'eff' and pg.evaluate(V)['phase'] == 'eff' and not any('7 の 効果' in s for s in sd),
              '相手が 先に 決めた：自分の えらぶ 窓は 消えない・相手が 何を 使うかは まだ 出ない')
        pg.locator('#cbOv .cbmod .pick .cbc').first.click(); idle(pg); sd = said(pg)
        check(any('コンピュータが 7 の 効果を 使ったよ' in s for s in sd) and pg.evaluate(V)['turn'] == 2 and len([c for c in pg.evaluate(V)['op']['hand'] if c['k']]) <= 1, '自分も 決めた → 2人の 効果が いっしょに 出て（6 → 7 の 順）、オープン')

        print('■ 効果タイム：5（5 と 手札 1まいを 捨てて 山札から 1まい）')
        start(pg, '51237', '12346', 'k')
        tap(pg, '5')
        check(modbtns(pg) == ['この カードを セットするセットしたら もう 変えられないよ', 'もどる'], '5 を タップ：セットの 前は「セットする」だけ（効果は セットの あと）')
        pg.locator('#cbOv .cbmod [data-cb=set]').click(); idle(pg)
        opp(pg, {'t': 'set', 'k': 1})
        check(pg.evaluate(MSG) == '効果タイム！ 5 の 効果を 使う？\n5 と 手札 1まいを 捨てて、山札から 1まい セットできるよ' and acts(pg) == ['使わない', '5 の 効果を 使う'], '5 を セットして 手札 4まい →「5 の 効果を 使う？」')
        pg.locator('#cbOv .cbact [data-cb=effyes]').click(); pg.wait_for_timeout(80)
        check(pg.evaluate("() => CBApp._t.mode.step") == 'drop5' and '5 と いっしょに 捨てる カードを えらんでね' in pg.evaluate(MSG) and acts(pg) == ['もどる'], '「使う」→ 捨てる カードを えらぶ')
        pg.locator('#cbOv .cbact [data-cb=effback]').click(); pg.wait_for_timeout(80)
        check(pg.evaluate("() => CBApp._t.mode.step") == 'ask' and acts(pg) == ['使わない', '5 の 効果を 使う'], '「もどる」→「使う？」に もどれる')
        pg.locator('#cbOv .cbact [data-cb=effyes]').click(); pg.wait_for_timeout(80)
        tap(pg, '7')
        check(modbtns(pg) == ['この カードを 捨てる5 と いっしょに 捨てて、山札から 1まい セット', 'もどる'], '手札を タップ →「この カードを 捨てる」')
        said(pg)
        pg.locator('#cbOv .cbmod [data-cb=drop5]').click(); idle(pg)
        v = pg.evaluate(V); sd = said(pg)
        check(any('5 と 7 を 捨てて、山札から 1まい セットしたよ' in s for s in sd) and v['turn'] == 2 and v['my']['wins'] == 1 and v['last']['c'] == ['k', '1'] and pg.locator('#cbOv .cbdis .cbn').inner_text() == '4' and pg.evaluate(HAND) == '123',
              f'5 と 7 を 捨てて 山札の 上（神様馬）が セットされた → オープンで 勝ち（捨て札 4まい・手札 {pg.evaluate(HAND)}）')
        pg.locator('#cbOv [data-cb=discard]').click(); pg.wait_for_timeout(80); dm = pg.evaluate(DM)
        check(dm['turns'] == ['ターン 1|あなた=k|コンピュータ=1'] and dm['effs'] == ['ターン 1|あなたの 5 の 効果=57'] and dm['none'] == [], f'捨て札の 窓：終わった ターン（神様馬・1）と、効果で 捨てた カード（あなたの 5 の 効果：5・7）（{dm["effs"]}）')
        shot(pg, 'cb_discard_eff')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)

        print('■ 神様馬：勝った 次の ターンの はじめに、効果を 使うか えらぶ（まさちゃん 23:12）')
        v = pg.evaluate(V)
        check(v['phase'] == 'pre' and v['pend']['mine'] and v['pend']['type'] == 'k' and any(s == 'ban:ターン 2' for s in sd) and any(s.startswith('ban:神様馬の 効果') and '使うか えらんでね' in s for s in sd)
              and sd.index('ban:ターン 2') < [i for i, s in enumerate(sd) if s.startswith('ban:神様馬の 効果')][0]
              and pg.evaluate(MSG) == '神様馬で 勝った！ 効果を 使う？\n相手の 手札を 1まい 見られるよ' and acts(pg) == ['使わない', '神様馬の 効果を 使う'] and pg.evaluate(SLOT) == '- -' and pg.locator('#cbOv .cbturn').inner_text().replace('\n', '') == 'ターン 2／3',
              f'2ターン目に 入って から「神様馬で 勝った！ 効果を 使う？」（使わない／神様馬の 効果を 使う）・ボードは 片付いて いる（{pg.evaluate(SLOT)}）')
        shot(pg, 'cb_pend_k')
        tap(pg, '1'); check(modbtns(pg) == ['もどる'] and pg.locator('#cbOv .cbglow.on').count() == 0, '決める までは セットできない（手札は 見る だけ）')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        pg.locator('#cbOv .cbact [data-cb=kgo]').click(); pg.wait_for_timeout(80)
        pg.evaluate("() => { window.__seen = []; }")
        pg.locator('#cbOv .cbmod .pick .cbc').first.click(); idle(pg)
        seen = pg.evaluate("() => window.__seen"); v = pg.evaluate(V)
        check(any('神様馬の 効果' in s for s in seen) and len([c for c in v['op']['hand'] if c['k']]) == 1 and v['turn'] == 2 and v['phase'] == 'set' and 'セットする カードを えらんでね' in pg.evaluate(MSG) and pg.locator('#cbOv .cbglow.on').count() == 1 and acts(pg) == [],
              '相手の 手札を 1まい 見た → 2ターン目の セットへ')
        start(pg, 'k2367', '12345'); play(pg, 'k'); opp(pg, {'t': 'set', 'k': 1})
        pg.locator('#cbOv .cbact [data-cb=kskip]').click(); idle(pg)
        check(pg.evaluate(V)['turn'] == 2 and pg.evaluate(V)['phase'] == 'set' and all(c['k'] is None for c in pg.evaluate(V)['op']['hand']), '「使わない」→ 何も 見ないで 2ターン目の セットへ')
        start(pg, '12367', 'k2345'); play(pg, '1'); said(pg); opp(pg, {'t': 'set', 'k': 'k'}); sd = said(pg)
        check(pg.evaluate(V)['phase'] == 'pre' and pg.evaluate(V)['pend']['mine'] is False and 'コンピュータが 神様馬の 効果を 使うか えらんで いるよ' in pg.evaluate(MSG) and acts(pg) == [] and any(s.startswith('ban:神様馬の 効果') and 'コンピュータが 使うか えらぶよ' in s for s in sd),
              '相手が 神様馬で 勝った：2ターン目の はじめに「コンピュータが 神様馬の 効果を 使うか えらんで いるよ…」（自分は 待つ）')
        opp(pg, {'t': 'k', 'pickk': 2}); sd = said(pg)
        check(any('コンピュータが 神様馬の 効果で、' in s and 'あなたの 手札を 1まい 見たよ' in s for s in sd) and pg.locator('#cbOv .cbhand .cbc:has(.eye) img').get_attribute('src') == 'cb_s2.webp' and pg.evaluate(V)['phase'] == 'set' and pg.evaluate(V)['can']['set'], '相手が 効果を 使った → 見られた カードに 目の しるし → セットへ')

        print('■ 幻の馬：勝った 次の ターンの はじめに、2まい 捨てて 2まい 引く')
        start(pg, 'm6712', '12345', '13'); play(pg, 'm'); opp(pg, {'t': 'set', 'k': 1})
        check(pg.evaluate(V)['phase'] == 'pre' and pg.evaluate(V)['turn'] == 2 and pg.evaluate(MSG) == '幻の馬で 勝った！ 効果を 使う？\n手札を 2まい 捨てて、山札から 2まい 引けるよ' and acts(pg) == ['使わない', '幻の馬の 効果を 使う'], '2ターン目の はじめ：「幻の馬で 勝った！ 効果を 使う？」（使わない／幻の馬の 効果を 使う）')
        pg.locator('#cbOv .cbact [data-cb=mpick]').click(); pg.wait_for_timeout(80)
        check(pg.evaluate("() => CBApp._t.mode.k") == 'dropm' and '（0／2）' in pg.evaluate(MSG) and pg.locator('#cbOv .cbact [data-cb=mgo]').is_disabled(), '捨てる 2まいを えらぶ（えらぶ まで ボタンは 押せない）')
        tap(pg, '6'); tap(pg, '7'); tap(pg, '1')      # 3まい目は えらべない
        check(pg.locator('#cbOv .cbhand .cbc.sel').count() == 2 and '（2／2）' in pg.evaluate(MSG) and pg.locator('#cbOv .cbact [data-cb=mgo]').is_enabled(), '2まい えらんだ（3まい目は えらべない）')
        tap(pg, '7'); tap(pg, '7')                     # はずして もう一度
        pg.locator('#cbOv .cbact [data-cb=mgo]').click(); idle(pg)
        check(pg.evaluate(HAND) == '1123' and pg.evaluate(V)['turn'] == 2 and pg.evaluate(V)['phase'] == 'set' and pg.locator('#cbOv .cbdeck .cbn').inner_text() == '18' and pg.locator('#cbOv .cbdis .cbn').inner_text() == '4',
              f'6 と 7 を 捨てて 2まい（1・3）引いた（手札 {pg.evaluate(HAND)}・山札 18・捨て札 4）→ セットへ')
        pg.locator('#cbOv [data-cb=discard]').click(); pg.wait_for_timeout(80); dm = pg.evaluate(DM)
        check(dm['turns'] == ['ターン 1|あなた=m|コンピュータ=1'] and dm['effs'] == ['ターン 2はじめ|あなたの 幻の馬の 効果=67'], f'捨て札の 窓：効果で 捨てた カード（ターン 2 の はじめ・あなたの 幻の馬の 効果：6・7）（{dm["effs"]}）')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        start(pg, 'm6712', '12345'); play(pg, 'm'); opp(pg, {'t': 'set', 'k': 1}); pg.locator('#cbOv .cbact [data-cb=mskip]').click(); idle(pg)
        check(pg.evaluate(HAND) == '1267' and pg.evaluate(V)['phase'] == 'set' and pg.locator('#cbOv .cbdeck .cbn').inner_text() == '20', '「使わない」→ 手札は そのまま セットへ')

        print('■ 効果タイム：4（見せて 強制交換）')
        start(pg, '41236', '15677'); opp(pg, {'t': 'set', 'k': 1})
        tap(pg, '4')
        check(modbtns(pg) == ['この カードを セットするセットしたら もう 変えられないよ', 'もどる'], '4 を タップ：セットの 前は「セットする」だけ')
        pg.locator('#cbOv .cbmod [data-cb=set]').click(); idle(pg)
        check(pg.evaluate(MSG) == '効果タイム！ 4 の 効果を 使う？\n4 を 見せて、相手に カードを 交換させるよ' and acts(pg) == ['使わない', '4 の 効果を 使う'] and pg.evaluate(SLOT) == 'b 4:セット ずみ', f'4 を セットした あと →「4 の 効果を 使う？」（まだ ふせた まま：{pg.evaluate(SLOT)}）')
        said(pg)
        pg.locator('#cbOv .cbact [data-cb=effyes]').click(); idle(pg)
        v = pg.evaluate(V); sd = said(pg)
        check(v['phase'] == 'swap' and v['pend']['mine'] is False and pg.evaluate(SLOT) == 'b 4:4 の 効果' and 'コンピュータが カードを 交換して いるよ' in pg.evaluate(MSG) and any(s.startswith('ban:4 の 効果！') for s in sd), f'「使う」：4 が 表に なって 相手の 交換を 待つ（{pg.evaluate(SLOT)}）')
        pg.evaluate("() => { window.__seen = []; }")
        opp(pg, {'t': 'swap', 'k': 5})
        seen = pg.evaluate("() => window.__seen")
        check(any('勝ち！' in s and '4 が 5 に 勝ったよ' in s for s in seen) and pg.evaluate(V)['my']['wins'] == 1 and pg.locator('#cbOv .cbohand .cbc').count() == 4, '相手は 1 を もどして 5 を 出した → 4 の 勝ち（相手の 手札は 4まいの まま）')
        start(pg, '41236', '15677'); play(pg, '4'); opp(pg, {'t': 'set', 'k': 1}); pg.evaluate("() => { window.__seen = []; }")
        pg.locator('#cbOv .cbact [data-cb=effno]').click(); idle(pg)
        check(any('負け…' in s and '1 の ほうが 強いよ' in s for s in pg.evaluate("() => window.__seen")), '「使わない」→ そのまま オープン（4 と 1 → 負け）')
        # 相手が 4 の 効果：自分が 交換する
        start(pg, '15677', '41236'); play(pg, '1'); opp(pg, {'t': 'set', 'k': 4}); said(pg)
        opp(pg, {'t': 'eff', 'use': {'u4': True}})
        v = pg.evaluate(V); sd = said(pg)
        check(v['phase'] == 'swap' and v['pend']['mine'] and pg.evaluate(SLOT) == '4:4 の 効果 1:セット ずみ' and 'コンピュータが 4 の 効果を 使ったよ！' in pg.evaluate(MSG) and pg.locator('#cbOv .cbglow.on').count() == 1 and any('あなたは セットした カードを 交換してね' in s for s in sd),
              f'相手が 4 の 効果：自分が 交換する 番（{pg.evaluate(SLOT)}）')
        shot(pg, 'cb_pend_swap')
        tap(pg, '5')
        check(modbtns(pg) == ['この カードと 交換する', 'もどる'], '手札を タップ →「この カードと 交換する」')
        pg.evaluate("() => { window.__seen = []; }")
        pg.locator('#cbOv .cbmod [data-cb=swap]').click(); idle(pg)
        seen = pg.evaluate("() => window.__seen")
        check(any('負け…' in s for s in seen) and pg.evaluate(HAND) == '1677' and pg.evaluate(V)['op']['wins'] == 1, f'5 と 交換（1 は 手札に もどる）→ 4 と 5 で 負け（手札 {pg.evaluate(HAND)}）')

        print('■ 効果タイム：使える 効果が 2つ（5 と 7）→ 1つ ずつ 聞く')
        start(pg, '57771', '12346', '2346'); play(pg, '5'); opp(pg, {'t': 'set', 'k': 1})
        check(pg.evaluate("() => CBApp._t.mode.q") == '5' and acts(pg) == ['使わない', '5 の 効果を 使う'], '1つ目：「5 の 効果を 使う？」')
        pg.locator('#cbOv .cbact [data-cb=effyes]').click(); pg.wait_for_timeout(80); tap(pg, '1'); pg.locator('#cbOv .cbmod [data-cb=drop5]').click(); pg.wait_for_timeout(120)
        check(pg.evaluate(V)['phase'] == 'eff' and pg.evaluate("() => CBApp._t.mode.q") == '7' and pg.evaluate(MSG).startswith('効果タイム！ 7 の 効果を 使う？') and acts(pg) == ['使わない', '7 の 効果を 使う'] and pg.evaluate(DOMHAND) == '1777',
              '5 の 答え（1 を 捨てる）の あと、2つ目：「7 の 効果を 使う？」（まだ 何も おきて いない：答え終わって から まとめて）')
        said(pg); pg.evaluate("() => { window.__seen = []; }")
        pg.locator('#cbOv .cbact [data-cb=effyes]').click(); idle(pg); sd = said(pg)
        i5 = [i for i, s in enumerate(sd) if '5 と 1 を 捨てて' in s]; i7 = [i for i, s in enumerate(sd) if '7 を 3まい もどして' in s]
        check(i5 and i7 and i5[0] < i7[0] and pg.evaluate(HAND) == '346' and pg.evaluate(V)['last']['c'] == ['2', '1'] and pg.evaluate(V)['turn'] == 2, f'両方 使う → 5 → 7 の 順に 出て オープン（手札 {pg.evaluate(HAND)}・出たのは 山札の 2）')
        start(pg, '57771', '12346', '2346'); play(pg, '5'); opp(pg, {'t': 'set', 'k': 1})
        pg.locator('#cbOv .cbact [data-cb=effyes]').click(); pg.wait_for_timeout(80); tap(pg, '7'); pg.locator('#cbOv .cbmod [data-cb=drop5]').click(); idle(pg)
        check(pg.evaluate(V)['turn'] == 2 and pg.evaluate(HAND) == '177', '5 の 効果で 7 を 捨てた（7 が 2まいに なる）→ 7 の 効果は 聞かれない')

        print('■ 結果と ごほうび（お世話トークン）')
        # 勝ち：+1（はじめの 5こ → 6こ）
        pg.evaluate("() => { localStorage.removeItem('tengel.cb'); CBApp._t.load(); }")
        def win_game():
            start(pg, 'k1236', '23567'); play(pg, 'k'); opp(pg, {'t': 'set', 'k': 6}); pg.locator('#cbOv .cbact [data-cb=kskip]').click(); idle(pg)      # 2ターン目の はじめ：神様馬の 効果は 使わない
            play(pg, '1'); opp(pg, {'t': 'set', 'k': 7}); play(pg, '2'); opp(pg, {'t': 'set', 'k': 3})
            pg.wait_for_function("() => { const g = document.querySelector('#cbOv .cbend .gift'); return CBApp._t.ended && g && g.textContent.length > 3; }", timeout=30000)
            return pg.evaluate("() => ({ h: document.querySelector('#cbOv .cbend h3').textContent, sc: document.querySelector('#cbOv .cbend .sc').textContent, g: document.querySelector('#cbOv .cbend .gift').textContent, st: Object.assign({}, CBApp._t.state) })")
        t0 = pg.evaluate(TC)
        e = win_game(); t1 = pg.evaluate(TC)
        check(e['h'] == 'あなたの 勝ち！' and e['sc'].startswith('3 － 0') and t1 == (t0 or 5) + 1 and e['st']['streak'] == 1 and e['st']['win'] == 1 and e['st']['owe'] == 0 and f'お世話トークン ＋1' in e['g'] and f'いま {t1}こ／25こ' in e['g'] and '1連勝中！' in e['g'] and 'あと 4勝で 3こ' in e['g'],
              f'勝ち：お世話トークン ＋1（{t0 or 5} → {t1}）・1連勝中・あと 4勝で 3こ（{e["g"]}）')
        shot(pg, 'cb_end_win')
        pg.locator('#cbOv .cbend [data-cb=again]').click(); idle(pg)
        check(pg.evaluate(V)['turn'] == 1 and pg.evaluate(V)['phase'] == 'set' and not pg.evaluate("() => CBApp._t.ended") and pg.evaluate(PIPS) == '0-0' and not pg.evaluate("() => CBApp._t.modOn()"), '「もう 1回」→ すぐ 新しい 対戦（しるしも 0 に）')
        for k in range(3): win_game()
        e = win_game(); t5 = pg.evaluate(TC)
        check(e['st']['streak'] == 5 and e['st']['win'] == 5 and t5 == t1 + 3 + 3 and 'お世話トークン ＋3' in e['g'] and '5連勝 ボーナス！' in e['g'] and '5連勝中！' in e['g'], f'5連勝：5回目は ＋3（{t1} → 2・3・4回目 ＋1 ずつ → 5回目 ＋3 ＝ {t5}）（{e["g"]}）')
        e = win_game()
        check(e['st']['streak'] == 6 and pg.evaluate(TC) == t5 + 1 and 'あと 4勝で 3こ' in e['g'], '6連勝目は また ＋1（つぎの ＋3 は 10連勝）')
        # 上限 25こ
        pg.evaluate("() => { TCApp.state.stock = 25; TCApp.state.stockAt = Date.now(); }")
        e = win_game()
        check(pg.evaluate(TC) == 25 and 'お世話トークンが いっぱい（25こ）なので、今回は もらえなかったよ' in e['g'] and e['st']['streak'] == 7 and e['st']['owe'] == 0, f'お世話トークンが 25こ の とき：ふえない（連勝は 数える）（{e["g"]}）')
        pg.evaluate("() => { TCApp.state.stock = 22; TCApp.state.stockAt = Date.now(); }")
        for k in range(2): win_game()
        e = win_game()      # 10連勝：＋3 の はずが、あと 1こ しか 入らない
        check(e['st']['streak'] == 10 and pg.evaluate(TC) == 25 and 'お世話トークン ＋1' in e['g'] and '25こ まで なので 1こ だけ' in e['g'] and e['st']['owe'] == 0, f'10連勝（＋3）で あと 1こ しか 入らない とき：入る 分 だけ（{e["g"]}）')
        # 負け：連勝 0
        start(pg, '23677', '12356'); play(pg, '3'); opp(pg, {'t': 'set', 'k': 1}); play(pg, '6'); opp(pg, {'t': 'set', 'k': 2}); play(pg, '7'); opp(pg, {'t': 'set', 'k': 3})
        pg.wait_for_function("() => { const g = document.querySelector('#cbOv .cbend .gift'); return CBApp._t.ended && g && g.textContent.length > 3; }", timeout=30000)
        e = pg.evaluate("() => ({ h: document.querySelector('#cbOv .cbend h3').textContent, g: document.querySelector('#cbOv .cbend .gift').textContent, st: Object.assign({}, CBApp._t.state) })")
        check(e['h'] == 'あなたの 負け…' and e['st']['streak'] == 0 and e['st']['lose'] == 1 and '連勝は 0 に もどったよ' in e['g'] and pg.evaluate(TC) == 25, f'負け：連勝は 0 に もどる・トークンは かわらない（{e["g"]}）')
        pg.locator('#cbOv .cbend [data-cb=menu]').click(); pg.wait_for_timeout(120)
        rec = pg.locator('#cbOv .cbmenu .rec').inner_text()
        check(pg.evaluate("() => CBApp._t.screen") == 'menu' and '10勝 1敗 0分' in rec.replace('\n', ' '), f'メニューに 勝ち負けの 数（{rec!r}）')

        print('■ とちゅうで やめる')
        start(pg, '12367', '23567'); play(pg, '1')
        s0 = pg.evaluate("() => Object.assign({}, CBApp._t.state)")
        pg.locator('#cbOv .cbtop [data-cb=quit]').click(); pg.wait_for_timeout(80)
        check('とちゅうで やめると 負けに なるよ' in pg.locator('#cbOv .cbmod').inner_text(), '「やめる」→ たしかめる 窓（とちゅうで やめると 負け）')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        check(pg.evaluate("() => CBApp._t.screen") == 'game' and pg.evaluate(V)['my']['set'] is not None, '「つづける」→ 対戦に もどる')
        pg.locator('#cbOv .cbgear').click(); pg.wait_for_timeout(80)
        check([x.inner_text() for x in pg.locator('#cbOv .cbmod .cbb').all()] == ['対戦に もどる', 'あそび方', '対戦を やめる'], 'ボードの 歯車 → メニュー（対戦に もどる・あそび方・対戦を やめる）')
        pg.locator('#cbOv .cbmod [data-cb=help]').click(); pg.wait_for_timeout(80)
        check(pg.evaluate("() => CBApp._t.screen") == 'help', '歯車 → あそび方')
        pg.locator('#cbOv [data-cb=helpx]').click(); pg.wait_for_timeout(80)
        check(pg.evaluate("() => CBApp._t.screen") == 'game' and pg.evaluate(DOMHAND) == '2367', 'あそび方から もどる → 対戦の つづき')
        pg.locator('#cbOv .cbtop [data-cb=quit]').click(); pg.locator('#cbOv .cbmod [data-cb=quitgo]').click(); pg.wait_for_timeout(120)
        s1 = pg.evaluate("() => Object.assign({}, CBApp._t.state)")
        check(pg.evaluate("() => CBApp._t.screen") == 'menu' and s1['lose'] == s0['lose'] + 1 and s1['streak'] == 0 and pg.evaluate("() => CBApp._t.match") is None, 'とちゅうで やめた → 負けに 数える・メニューへ')
        pg.locator('#cbOv .cbmenu [data-cb=close]').click(); pg.wait_for_timeout(120)
        check(pg.evaluate("() => !document.querySelector('#cbOv').classList.contains('on')") and pg.locator('#cbFab').is_enabled(), '「← もどる」→ カードバトルを 閉じる（ボタンは また 押せる）')

        print('■ コンピュータが 自分で 考えて 出す（ふつうの 対戦）')
        open_cb(pg)
        pg.evaluate("() => { CBApp._think = () => 30; CBApp._opt = null; CBApp._rng = null; }")
        pg.locator('#cbOv .cbmenu [data-cb=cpu]').click()
        done = False
        for step in range(90):
            idle(pg, 60000)
            stt = pg.evaluate("() => { const v = CBApp._t.view; return CBApp._t.ended ? 'end' : !v ? 'none' : v.pend && v.pend.mine ? v.pend.type : v.can.eff ? 'eff' : v.can.set ? 'set' : 'wait'; }")
            if stt == 'end': done = True; break
            if stt in ('k', 'm'): pg.locator(f'#cbOv .cbact [data-cb={stt}skip]').click()
            elif stt == 'eff': pg.locator('#cbOv .cbact [data-cb=effno]').click()
            elif stt == 'swap': pg.locator('#cbOv .cbhand .cbc').first.click(); pg.wait_for_timeout(60); pg.locator('#cbOv .cbmod [data-cb=swap]').click()
            elif stt == 'set': pg.locator('#cbOv .cbhand .cbc').first.click(); pg.wait_for_timeout(60); pg.locator('#cbOv .cbmod [data-cb=set]').click()
            else: pg.wait_for_timeout(120)
        v = pg.evaluate(V)
        check(done and v['phase'] == 'end' and v['res'] in ('win', 'lose', 'draw') and len(v['discard']) >= 6, f'コンピュータと さいごまで 対戦できる（{v["res"]} {v["my"]["wins"]}－{v["op"]["wins"]}・捨て札 {len(v["discard"])}まい）')
        pg.wait_for_function("() => { const g = document.querySelector('#cbOv .cbend .gift'); return g && g.textContent.length > 3; }", timeout=30000)
        pg.locator('#cbOv .cbend [data-cb=menu]').click(); pg.wait_for_timeout(120)

        print('■ 部屋：2つの 画面（ホスト・ゲスト）で 対戦')
        gp = ctx.new_page(); gerrs = []; gp.on('pageerror', lambda e: gerrs.append(str(e)))
        gp.goto(APP); gp.wait_for_timeout(1300); gate(gp); gp.wait_for_timeout(600); open_cb(gp)
        pg.evaluate("() => { CBApp._opt = { hands: [['k', '1', '2', '6', '6'], ['m', '3', '4', '5', '7']] }; }")
        pg.locator('#cbOv .cbmenu [data-cb=host]').click(); pg.wait_for_timeout(300)
        hr = pg.evaluate("() => ({ scr: CBApp._t.screen, num: document.querySelector('#cbOv .cbroom .num').textContent, stt: document.querySelector('#cbOv .cbroom .stt').textContent, t: document.querySelector('#cbOv .cbroom').textContent, calls: window.__room.calls.slice() })")
        check(hr['scr'] == 'room' and re.fullmatch(r'[1-9][0-9]{3}', hr['num']) is not None and '友だちを 待って いるよ' in hr['stt'] and 'この 番号を 友だちに 教えてね' in hr['t'] and hr['calls'] == ['host:' + hr['num']],
              f'部屋を 作る：4けたの 部屋番号（{hr["num"]}）・「友だちを 待って いるよ…」・アプリに「部屋を 作る」を お願い（{hr["calls"]}）')
        shot(pg, 'cb_room_host')
        gp.locator('#cbOv .cbmenu [data-cb=join]').click(); gp.wait_for_timeout(150)
        check(gp.locator('#cbOv .cbkeys button').count() == 12 and gp.locator('#cbOv .cbkeys [data-key=go]').is_disabled(), '部屋に 入る：数字の ボタン（4けた 入れる まで「入る」は 押せない）')
        for d in '00': gp.locator(f'#cbOv .cbkeys [data-key="{d}"]').click()
        gp.locator('#cbOv .cbkeys [data-key=del]').click()
        gp.locator('#cbOv .cbkeys [data-key=del]').click()
        for d in hr['num']: gp.locator(f'#cbOv .cbkeys [data-key="{d}"]').click()
        gp.locator('#cbOv .cbkeys [data-key="9"]').click()      # 5けた目は 入らない
        check(gp.locator('#cbOv .cbroom .num').inner_text().replace('\n', '') == hr['num'] and gp.locator('#cbOv .cbkeys [data-key=go]').is_enabled(), f'番号を 入れる（消す・4けた まで）→「入る」が 押せる')
        shot(gp, 'cb_room_join')
        gp.locator('#cbOv .cbkeys [data-key=go]').click()
        pg.wait_for_function("() => CBApp._t.screen === 'game' && CBApp._t.view && CBApp._t.idle", timeout=30000); gp.wait_for_function("() => CBApp._t.screen === 'game' && CBApp._t.view && CBApp._t.idle", timeout=30000)
        hv, gv = pg.evaluate(V), gp.evaluate(V)
        check(pg.evaluate("() => CBApp._t.match.kind") == 'host' and gp.evaluate("() => CBApp._t.match.kind") == 'guest' and hv['me'] == 0 and gv['me'] == 1 and pg.evaluate(DOMHAND) == 'k1266' and gp.evaluate(DOMHAND) == 'm3457'
              and pg.locator('#cbOv .cbopp .cbwho b').inner_text() == 'ともだち' and gp.locator('#cbOv .cbopp .cbwho b').inner_text() == 'ともだち' and gp.evaluate("() => window.__room.calls[0]") == 'join:' + hr['num'] and set(gp.evaluate("() => window.__room.calls.slice(1)")) <= {'send'},
              f'つながった → 2人とも 対戦の 画面（ホストの 手札 {pg.evaluate(DOMHAND)}・ゲストの 手札 {gp.evaluate(DOMHAND)}・相手の 名前は「ともだち」）')
        play(gp, '3'); idle(pg)
        check(pg.evaluate(SLOT) == 'b -' and 'ともだちは もう セットしたよ' in pg.evaluate(MSG) and gp.evaluate(SLOT) == '- 3:セット ずみ' and 'ともだちが えらんで いるよ' in gp.evaluate(MSG), 'ゲストが セットした → ホストの 画面に うらの カード・ゲストは 待つ')
        pg.evaluate("() => { window.__seen = []; const mo = new MutationObserver(() => { const m = document.querySelector('#cbOv .cbmod'); if (m.classList.contains('cbopen')) { const t = m.querySelector('.cbres'); window.__seen.push((m.querySelector('h3') || {}).textContent + '|' + (t ? t.textContent : '')); } }); mo.observe(document.querySelector('#cbOv .cbmod'), { childList: true, subtree: true, attributes: true, characterData: true }); }")
        gp.evaluate("() => { window.__seen = []; const mo = new MutationObserver(() => { const m = document.querySelector('#cbOv .cbmod'); if (m.classList.contains('cbopen')) { const t = m.querySelector('.cbres'); window.__seen.push((m.querySelector('h3') || {}).textContent + '|' + (t ? t.textContent : '')); } }); mo.observe(document.querySelector('#cbOv .cbmod'), { childList: true, subtree: true, attributes: true, characterData: true }); }")
        said(pg); said(gp)
        play(pg, 'k'); idle(gp)
        check(pg.evaluate(V)['phase'] == 'eff' and acts(pg) == ['使わない', '6 の 効果を 使う'] and 'ともだちが 効果を 使うか えらんで いるよ' in gp.evaluate(MSG) and acts(gp) == [] and gp.evaluate(SLOT) == 'b 3:セット ずみ'
              and any(s.startswith('ban:効果タイム') and 'カードの 効果を 使うか えらんでね' in s for s in said(pg)) and any(s.startswith('ban:効果タイム') and 'ともだちが 効果を 使うか えらぶよ' in s for s in said(gp)) and not pg.evaluate("() => window.__seen.length") and not gp.evaluate("() => window.__seen.length"),
              'ホストも セットした → 2人の 画面に「効果タイム」：ホスト（6 が 2まい）は「6 の 効果を 使う？」・ゲストは 待つ（オープンは まだ）')
        pg.locator('#cbOv .cbact [data-cb=effyes]').click(); pg.wait_for_timeout(80); pg.locator('#cbOv .cbmod .pick .cbc').last.click(); idle(pg); idle(gp)
        check(any('勝ち！' in s for s in pg.evaluate("() => window.__seen")) and any('負け…' in s for s in gp.evaluate("() => window.__seen")) and pg.evaluate(V)['turn'] == 2 and pg.evaluate(V)['pend']['mine'] and acts(pg) == ['使わない', '神様馬の 効果を 使う']
              and 'ともだちが 神様馬の 効果を 使うか えらんで いるよ' in gp.evaluate(MSG) and gp.locator('#cbOv .cbohand .cbc img[src="cb_s6.webp"]').count() == 2 and gp.locator('#cbOv .cbhand .cbc .eye').count() == 1 and any('あなたの 手札を 1まい 見たよ' in s for s in said(gp)),
              'ホストが 6 の 効果 → 2人の 画面で オープン（ホスト「勝ち！」・ゲスト「負け…」）→ 2ターン目の はじめ：神様馬の 効果は ホストが えらぶ・ゲストは 待つ')
        pg.locator('#cbOv .cbact [data-cb=kgo]').click(); pg.wait_for_timeout(80); pg.locator('#cbOv .cbmod .pick .cbc').first.click(); idle(pg); idle(gp)
        check(len([c for c in pg.evaluate(V)['op']['hand'] if c['k']]) >= 1 and gp.locator('#cbOv .cbhand .cbc .eye').count() >= 1 and pg.evaluate(V)['turn'] == 2 and gp.evaluate(V)['turn'] == 2 and pg.evaluate(V)['can']['set'] and gp.evaluate(V)['can']['set'], 'ホストが ゲストの 手札を 1まい 見た → ゲストの その カードに 目の しるし・2人とも 2ターン目の セットへ')
        gp.locator('#cbOv [data-cb=discard]').click(); gp.wait_for_timeout(80)
        gd = gp.evaluate("() => [...document.querySelectorAll('#cbOv .cbmod .cbdl .row[data-dt]')].map(r => r.querySelector('b').textContent + '|' + [...r.querySelectorAll('.pr')].map(p => p.querySelector('span').textContent + '=' + [...p.querySelectorAll('img')].map(i => i.getAttribute('src').replace('cb_s', '').replace('.webp', '')).join('')).join('|'))")
        check(gd == ['ターン 1|あなた=3|ともだち=k'], f'ゲストの 捨て札の 窓：自分から 見た 形（{gd}）')
        gp.locator('#cbOv .cbmod [data-cb=modx]').click(); gp.wait_for_timeout(60)
        def step(q):
            idle(q)
            stt = q.evaluate("() => { const v = CBApp._t.view; return CBApp._t.ended ? 'end' : !v ? 'none' : v.pend && v.pend.mine ? v.pend.type : v.can.eff ? 'eff' : v.can.set ? 'set' : 'wait'; }")
            if stt in ('k', 'm'): q.locator(f'#cbOv .cbact [data-cb={stt}skip]').click()
            elif stt == 'eff': q.locator('#cbOv .cbact [data-cb=effno]').click()
            elif stt == 'swap': q.locator('#cbOv .cbhand .cbc').first.click(); q.wait_for_timeout(60); q.locator('#cbOv .cbmod [data-cb=swap]').click()
            elif stt == 'set': q.locator('#cbOv .cbhand .cbc').last.click(); q.wait_for_timeout(60); q.locator('#cbOv .cbmod [data-cb=set]').click()
            return stt
        for n in range(60):
            a1, a2 = step(pg), step(gp)
            if a1 == 'end' and a2 == 'end': break
            if a1 in ('wait', 'end', 'none') and a2 in ('wait', 'end', 'none'): pg.wait_for_timeout(120)
        pg.wait_for_function("() => CBApp._t.ended", timeout=30000); gp.wait_for_function("() => CBApp._t.ended", timeout=30000)
        pg.wait_for_function("() => { const g = document.querySelector('#cbOv .cbend .gift'); return g && g.textContent.length > 3; }", timeout=30000); gp.wait_for_function("() => { const g = document.querySelector('#cbOv .cbend .gift'); return g && g.textContent.length > 3; }", timeout=30000)
        hv, gv = pg.evaluate(V), gp.evaluate(V)
        check(hv['res'] in ('win', 'lose', 'draw') and {'win': 'lose', 'lose': 'win', 'draw': 'draw'}[hv['res']] == gv['res'] and hv['my']['wins'] == gv['op']['wins'] and hv['op']['wins'] == gv['my']['wins'],
              f'さいごまで：2人の 結果は うらおもて（ホスト {hv["res"]} {hv["my"]["wins"]}－{hv["op"]["wins"]}・ゲスト {gv["res"]}）')
        shot(pg, 'cb_room_end')
        gp.locator('#cbOv .cbend [data-cb=again]').click(); gp.wait_for_timeout(250)
        check(gp.locator('#cbOv .cbend [data-cb=again]').is_disabled() and 'ともだちを 待って いるよ' in gp.locator('#cbOv .cbend .gift2').inner_text() and 'ともだちが「もう 1回」を 押したよ' in pg.locator('#cbOv .cbend .gift2').inner_text(),
              'ゲストが「もう 1回」→ ゲストは 待つ・ホストに「ともだちが もう 1回 を 押したよ」')
        pg.locator('#cbOv .cbend [data-cb=again]').click()
        pg.wait_for_function("() => !CBApp._t.ended && CBApp._t.view && CBApp._t.view.turn === 1 && CBApp._t.idle", timeout=30000); gp.wait_for_function("() => !CBApp._t.ended && CBApp._t.view && CBApp._t.view.turn === 1 && CBApp._t.idle", timeout=30000)
        check(pg.evaluate(V)['phase'] == 'set' and gp.evaluate(V)['phase'] == 'set' and len(gp.evaluate(V)['my']['hand']) == 5, 'ホストも「もう 1回」→ 2人とも 新しい 対戦')
        s0 = gp.evaluate("() => Object.assign({}, CBApp._t.state)"); h0 = pg.evaluate("() => Object.assign({}, CBApp._t.state)")
        gp.locator('#cbOv .cbtop [data-cb=quit]').click(); gp.locator('#cbOv .cbmod [data-cb=quitgo]').click()
        pg.wait_for_function("() => CBApp._t.modOn() && /部屋を 出たよ/.test(document.querySelector('#cbOv .cbmod').textContent)", timeout=20000)
        s1 = gp.evaluate("() => Object.assign({}, CBApp._t.state)"); h1 = pg.evaluate("() => Object.assign({}, CBApp._t.state)")
        check(gp.evaluate("() => CBApp._t.screen") == 'menu' and s1['lose'] == s0['lose'] + 1 and 'ともだちが 部屋を 出たよ' in pg.locator('#cbOv .cbmod').inner_text() and '勝ち負けに 数えないよ' in pg.locator('#cbOv .cbmod').inner_text() and h1 == h0,
              'ゲストが とちゅうで やめた → ゲストは 負け・ホストには「ともだちが 部屋を 出たよ（勝ち負けに 数えない）」')
        pg.locator('#cbOv .cbmod [data-cb=menu]').click(); pg.wait_for_timeout(150)
        check(pg.evaluate("() => CBApp._t.screen") == 'menu' and pg.evaluate("() => window.__room.calls[window.__room.calls.length - 1]") == 'stop', 'メニューへ（アプリの 部屋も とじる）')
        # 部屋を 作れない（ローカルネットワークを 許可して いない など）
        pg.evaluate("() => { window.__room.deny = true; }")
        pg.locator('#cbOv .cbmenu [data-cb=host]').click(); pg.wait_for_function("() => /部屋を 作れなかったよ/.test(document.querySelector('#cbOv .cbroom').textContent)", timeout=10000)
        check(pg.locator('#cbOv .cbroom [data-cb=roomre]').count() == 1, '部屋を 作れない とき：「部屋を 作れなかったよ」と「もう一度 作る」')
        pg.evaluate("() => { window.__room.deny = false; }")
        pg.locator('#cbOv .cbroom [data-cb=roomx]').click(); pg.wait_for_timeout(100)
        # 部屋番号が ちがう：さがした まま → やめる
        pg.locator('#cbOv .cbmenu [data-cb=join]').click(); pg.wait_for_timeout(100)
        for d in '1234': pg.locator(f'#cbOv .cbkeys [data-key="{d}"]').click()
        pg.locator('#cbOv .cbkeys [data-key=go]').click(); pg.wait_for_timeout(500)
        check('部屋を さがして いるよ' in pg.locator('#cbOv .cbroom .stt').inner_text() and pg.locator('#cbOv .cbkeys').count() == 0, 'ない 部屋番号：「部屋を さがして いるよ…」の まま（数字の ボタンは 出ない）')
        pg.locator('#cbOv .cbroom [data-cb=roomx]').click(); pg.wait_for_timeout(150)
        check(pg.evaluate("() => CBApp._t.screen") == 'menu' and pg.evaluate("() => window.__room.calls[window.__room.calls.length - 1]") == 'stop', '「← やめる」→ メニュー（さがすのを やめる）')
        check(not errs and not gerrs, f'エラー なし {errs[:3]} {gerrs[:3]}')
        if HAVE:
            miss = sorted(set(f for f in reqs if f.startswith('cb_') and f != 'cb_bundle.js' and f not in CBF))
            used = sorted(set(f for f in reqs if f in CBF))
            check(not miss and all(f in used for f in ['cb_board.webp', 'cb_deck.webp', 'cb_logo.webp', 'cb_icon.webp', 'cb_sb.webp', 'cb_s1.webp', 'cb_c1.webp', 'cb_ck.webp']), f'読んだ 絵と 音は ぜんぶ アプリに 入れる ファイル（ない 名前 {miss}・読んだ {len(used)}こ）')
finally:
    srv.terminate()
print('\n' + ('全部 OK' if not fails else f'NG {len(fails)}こ：' + ' / '.join(fails)))
sys.exit(1 if fails else 0)
