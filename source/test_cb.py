# 馬カードバトル（第4.176版）の 画面の テスト：App Store版（TARGET=app）を localhost で アプリ版として 開く
#   まさちゃん 2026/11/15 21:41「TENGER馬カードバトル …アイコンは推し馬の上に設置して！」・21:54「・コンピュータと対戦 ・部屋を作成して、友達と対戦 これをやりたい！」
#   ・入口：右下の 丸い ボタンの 列（たてに 4つ：上から トレーニングセンター → 推し馬 → カードバトル → 思い出フィギュア。まさちゃん 11/16 00:34「丸のアイコン組を少し小さくして！ピッタリ収まるように」・
#       00:47「トレーニングセンターを一番上、カードバトルを思い出フィギュアの上にして」・01:15「この青四角下の空間気になる。大きさ調整して空間があかないようにして！」・
#       01:16「カードバトルを、TENGERカードバトルに名前変えて！」）・丸の 大きさは「壁紙&ボード着せ替え」の すぐ 下 〜 下の タブの すぐ 上 を ぴったり うめる 大きさ（66px まで）・
#       たての 短い 画面（2列 × 2段）でも 右上の ボタンに 重ならない
#   ・メニュー・あそび方・コンピュータと 対戦（出す・オープン・捨て札・効果 6つ を 画面で）・結果と ごほうび（お世話トークン 1こ・5連勝で 3こ・25こ まで）・とちゅうで やめる
#   ・部屋：2つの 画面（ホスト・ゲスト）を、にせの アプリ側（Room.swift の かわり：BroadcastChannel）で つないで さいごまで 対戦・もう 1回・やめる
#   python3 test_cb.py   （ios/cb_assets/ が ある とき だけ 絵の 確かめ。ない とき（CI）も 画面は 動く）
#   第4.177版（まさちゃん 2026/11/16 10:40）：②説明の 字が 2行に なっても 画面が 上下しない・③5 の 効果は どの ターンでも（使った あとの 手札が のこりの ターンの 数より 少なく ならない とき）・
#     ④お世話トークンを もらった ときは さいごの 画面に「＋○こ GET！」の 札・⑤3 が 3まい → 見せて 1まい 交換・⑥効果を 使うか 聞く 窓（カードの 絵・大きい「使わない」「使う」）
#   第4.178版（まさちゃん 2026/11/16 14:43・15:33）：①BGM（設定で オン／オフ・うしろに 行ったら 止まる）・②5ターン・手札 7まい・③設定の 窓（BGM・効果音・エフェクト）・
#     ④6 の 効果は もう 見た カード しか ない ときは 聞かれない・⑤夜の フィールド（火の あかりの ゆれ）・逆転勝利（1 が 3まい → 神様馬・幻の馬に／2 が 3まい → 1 に：オープンしてから 聞く）
#     前から ある 場面（効果の しくみ）は「3ターン・手札 5まい」の まま 動かす（start() が turns: 3 を わたす）。本番の 形（5ターン・手札 7まい）は「■ 5ターン・手札 7まい」で 見る
#   第4.179版（まさちゃん 2026/11/16 15:47・16:01・16:10・16:18）：バトルコイン（買えない・コンピュータに 勝つと 1枚・5連勝 ごとに 5枚）・部屋の 参加コインと 勝者の 獲得コイン（2倍 まで）
#     ・入れない（足りない）・参加する → 2人とも 出す → 勝者が もらう・同点は もどる・とちゅうで やめた 人は もどらない（相手が もらう）・つながりが 切れたら もどる
#   第4.182版（まさちゃん 2026/11/16 20:00・20:09）：デザインカスタム（カードの おもて 18種・うら 7種：バトルコインで 解放＝おもて 300枚・神様馬／幻の馬 500枚・うら 300枚）
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
window.__abs = 0; (function () { var C = window.AudioContext || window.webkitAudioContext; if (!C) return; var o = C.prototype.createBufferSource; C.prototype.createBufferSource = function () { window.__abs++; return o.apply(this, arguments); }; })();
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
    pg.evaluate(f"() => {{ CBApp._t.speed({speed}); CBApp._guard = 0; }}"); pg.wait_for_timeout(150)      # _guard 0：聞く 窓が 出て すぐでも 押せる（テストは すぐ 押す。うっかり 押し 防止は 下で 別に 見る）
    # 出て すぐ 消える ことば（帯＝.cbban・ふきだし＝.cbtoast）を 覚えて おく（said() で 読んで 空に する）
    pg.evaluate("""() => { if (window.__said) return; window.__said = [];
      const W = (sel, tag) => { const e = document.querySelector('#cbOv ' + sel); let last = ''; new MutationObserver(() => { const s = e.classList.contains('on') ? e.textContent : ''; if (s && s !== last) window.__said.push(tag + ':' + s); last = s; }).observe(e, { childList: true, subtree: true, attributes: true, characterData: true }); };
      W('.cbban', 'ban'); W('.cbtoast', 'toast'); }""")


def said(pg):
    return pg.evaluate("() => { const a = window.__said.slice(); window.__said.length = 0; return a; }")


def acts(pg):
    return [x.inner_text().replace('\n', '') for x in pg.locator('#cbOv .cbact .cbb').all()]


# 効果を 使うか 聞く 窓（第4.177版：まん中に カードの 絵・質問・大きい「使わない」「使う」・「手札と ボードを 見る」）
ASKQ = """() => { const m = document.querySelector('#cbOv .cbmod.cbask'); if (!m) return null; const b = m.querySelector('.askq b'), q = m.querySelector('.askq');
  return { head: m.querySelector('h3').textContent, q: b.textContent, text: q.textContent.slice(b.textContent.length), btns: [...m.querySelectorAll('.cbb')].map(x => x.textContent.trim()), img: m.querySelector('.big img').getAttribute('src') }; }"""


def asked(pg):
    """聞く 窓が 出て いれば [質問, 説明]・出て いなければ None"""
    a = pg.evaluate(ASKQ)
    return [a['q'], a['text']] if a else None


def peek(pg):
    """聞く 窓の「手札と ボードを 見る」を 押す（窓が 下がって、下の 行の ボタンで 答える 形に なる）"""
    pg.locator('#cbOv .cbmod.cbask [data-cb=askpeek]').click(); pg.wait_for_timeout(80)


def modbtns(pg):
    return pg.evaluate("() => [...document.querySelectorAll('#cbOv .cbmod .cbb')].map(b => b.textContent.trim())")


def start(pg, h0, h1, deck='', turns=3):
    """手札を 決めて コンピュータと 対戦を はじめる。コンピュータは 自分では 動かない（テストが opp() で 相手の 手を 打つ）。
       turns＝ターンの 数（決めなければ 3：前から ある 場面は「3ターン・手札 5まい」の まま。本番の 形は turns=5 で 手札 7まい）"""
    pg.evaluate("""([h0, h1, dk, tn]) => { CBApp._think = () => 1e9; CBApp._opt = { hands: [h0.split(''), h1.split('')], deck: dk ? dk.split('') : undefined, turns: tn }; }""", [h0, h1, deck, turns])
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
        check(m['scr'] == 'menu' and m['h1'].replace('\n', '').replace(' ', '') == 'TENGERカードバトル' and m['btn'] == ['← もどる', 'コンピュータと 対戦', '部屋を 作る友だちと 対戦', '部屋に 入る友だちと 対戦', 'あそび方', '設定BGM・効果音', 'デザインカスタムカードの おもて・うら（バトルコインで 解放）'] and not any(m['dis']),
              f'メニュー：コンピュータと 対戦・部屋を 作る・部屋に 入る・あそび方・設定（第4.178版）・デザインカスタム（第4.182版）（{m["btn"]}）')
        check(m['rec'] == '勝つと お世話トークン 1こ・5連勝 ごとに 3こ' and (not HAVE or m['lg'] == 720), f'ごほうびの 説明（{m["rec"]}）')
        cl = pg.evaluate("() => { const e = document.querySelector('#cbOv .cbmenu .cbcoinl'); return e ? [e.textContent, e.querySelectorAll('img[src=\"cb_coin.webp\"]').length] : null; }")
        check(cl == ['バトルコイン 0枚コンピュータに 勝つと 1枚・5連勝 ごとに 5枚', 1], f'メニューに バトルコイン（第4.179版：コインの 絵・持って いる 数・もらい方）（{cl}）')
        check(reqs.count('cb_bundle.js') == 1 and 'cb_bundle.js' not in reqs[:reqs.index('cb_bundle.js')][:5], '本体（cb_bundle.js）は ボタンを 押した ときに 1回 だけ 読む')
        shot(pg, 'cb_menu')
        pg.locator('#cbOv .cbmenu [data-cb=help]').click(); pg.wait_for_timeout(200)
        ht = pg.locator('#cbOv .cbhelp .bd').inner_text()
        need = ['手札は 7まい。5ターンで 勝負', '5ターン 終わって', '2まいは 使わずに のこるよ', '強い カードの 勝ち', '勝った 数が 多い 人の 勝ち', '神様馬と 幻の馬が いちばん 強い', '1 が いちばん 強くて、7 が いちばん 弱い', '「かぶり」＝どちらも 負け', '4 どうしで 2人とも 4 の 効果を 使った ときは ドロー', '2人とも 4 を 出して、2人とも 効果を 使ったら、打ち消して その ターンは ドロー', '1〜7 が 4まい ずつ・神様馬 1まい・幻の馬 1まい',
                '① セット', 'セットしたら もう 変えられない', '② 効果タイム', '2人とも セットしたら、使える 効果が ある 人に「効果を 使う？」と 聞くよ', '③ オープン', '次の ターンの はじめに、使うか えらぶよ', '効果が 出る 順番は 6 → 5 → 7 → 3 → 4', '「使う」「使わない」は 自分で えらべる', '使うか 使わないかは 自分で えらべる',
                '終わった ターンの 捨て札', '効果で 捨てた カード',
                '7：3まい そろえて 交換', '6：2まい 見せて 手札を 見る', '5：2まい 捨てて 山札から セット', 'のこりの ターンの 数より 少なく ならない とき', 'さいごの ターンは、手札が 1まい あれば 使える', '4：見せて 強制交換',
                '3：3まい 見せて 手札を 交換', 'ランダムに えらんだ 1まいを 交換できるよ', '7・6・5・4・3 の 効果は', '神様馬：勝ったら 手札を 見る', '幻の馬：勝ったら 手札を 交換', 'お世話トークン 1こ', '5連勝 ごとに 3こ', '部屋番号（4けた）', '近くに いる 友だち',
                'もう 見た カード だけの ときは 使えないよ', 'まだ 見て いない カードが ある とき', 'メニューの「デザインカスタム」で、カードの おもてと うらの デザインを かえられるよ',
                '新しい デザインは バトルコインで 1つずつ 解放できるよ：カードの おもて 300枚（神様馬・幻の馬は 500枚）・カードの うら 300枚', '音と エフェクト（設定）', 'BGM・効果音・エフェクト（光や 動きの 演出）を オン／オフ',
                '1：3まい 見せて 逆転勝利', '2：3まい 見せて 逆転勝利', '神様馬・幻の馬に 負けた とき、手札に 1 が 2まい あれば', '1 に 負けた とき、手札に 2 が 2まい あれば', '勝ちに できるよ', '1・2 の 効果（逆転勝利）は、オープンした あと、負けた 人が 使うか えらぶよ',
                '1・2 の「逆転勝利」は、めくった あとに 使うか えらぶよ', '逆転勝利：1 が 3まい あれば 神様馬・幻の馬に、2 が 3まい あれば 1 に 勝てる',
                'バトルコイン', 'コンピュータに 勝つと 1枚', '5連勝 ごとに 5枚', '買う ことは できない', '参加コイン', '参加コインの 2倍 まで', '同じ 数の 参加コインを 持って いないと 入れない', 'テンゲルから 獲得コインを プレゼントで もらえる',
                '同点は 参加コインが もどる', 'とちゅうで やめると、参加コインは もどらない']
        miss = [x for x in need if x not in ht]
        check(pg.evaluate("() => CBApp._t.screen") == 'help' and not miss and pg.locator('#cbOv .cbhelp .ord img').count() == 9 and pg.locator('#cbOv .cbhelp .ef').count() == 9 and pg.locator('#cbOv .cbhelp .ef img[src="cb_s3.webp"]').count() == 1 and pg.locator('#cbOv .cbhelp .ef img[src="cb_s1.webp"]').count() == 1 and pg.locator('#cbOv .cbhelp .ef img[src="cb_s2.webp"]').count() == 1,
              f'あそび方：勝負の しかた（手札 7まい・5ターン）・1ターンの 流れ（セット → 効果タイム → オープン）・強さ（9まいの 並び）・効果 9つ（第4.178版：1・2 の 逆転勝利を 足した）・どの 効果も 自分で えらべる・捨て札・ごほうび・設定・部屋（ない 文 {miss}）')
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
              and geo['board'][0] == 0 and geo['board'][2] == 390 and abs((geo['board'][3] - geo['board'][1]) - 390 * 941 / 1672) < 2 and geo['left'] >= 0 and geo['right'] <= 390 and abs(geo['ch'] - geo['cw'] * 1.5) < 1.5 and geo['step'] >= geo['cw'] * 0.59,
              f'ならび：上から 相手の 手札 → ボード（幅 いっぱい・絵の たて横の まま）→ ことば → 手札 → ボタン。手札は 画面の 中・重なりは 40% まで（カード {geo["cw"]}×{geo["ch"]}・ずれ {geo["step"]}）')
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
        # 第4.177版：相手は 3ターン目に 5 を セットした（手札が 1まい 以上 のこって いる）→ 相手が 5 の 効果を 使うか えらぶ（自分は 待つ）。ここでは 使わない
        check(pg.evaluate(V)['phase'] == 'eff' and pg.evaluate(V)['can']['eff'] is None and 'コンピュータが 効果を 使うか えらんで いるよ' in pg.evaluate(MSG) and asked(pg) is None, '相手が 3ターン目に 5 を セット → 相手の 効果タイム（自分は 待つ：聞かれない）')
        opp(pg, {'t': 'eff', 'use': None})
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
              and asked(pg) == ['7 の 効果を 使う？', '7 を 3まい 山札に もどして、新しく 3まい 引けるよ'] and acts(pg) == [] and pg.evaluate(MSG) == '効果を 使うか えらんでね' and pg.evaluate(SLOT) == 'b 1:セット ずみ' and pg.evaluate("() => window.__seen.length") == 0,
              f'2人とも セットした →「効果タイム」→ 聞く 窓「7 の 効果を 使う？」。オープンは まだ（{pg.evaluate(SLOT)}）')
        # 第4.177版（まさちゃん「カードの効果は使うか使わないか選べるようにして！」）：聞く 窓＝まん中に カードの 絵・質問・大きい「使わない」「使う」
        aw = pg.evaluate(ASKQ)
        geo = pg.evaluate("""() => { const m = document.querySelector('#cbOv .cbmod.cbask'), R = e => { const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; };
          const bs = [...m.querySelectorAll('.rowb .cbb')], cs = getComputedStyle(bs[1]); return { vw: innerWidth, vh: innerHeight, img: R(m.querySelector('.big')), no: R(bs[0]), yes: R(bs[1]), peek: R(m.querySelector('[data-cb=askpeek]')), h3: R(m.querySelector('h3')),
            fs: parseFloat(cs.fontSize), qfs: parseFloat(getComputedStyle(m.querySelector('.askq b')).fontSize), z: +getComputedStyle(m).zIndex, cover: document.elementFromPoint(innerWidth / 2, innerHeight - 30).closest('.cbmod') === m }; }""")
        check(aw['head'] == '効果タイム！' and aw['btns'] == ['使わない', '使う', '手札と ボードを 見る'] and aw['img'] == 'cb_c7.webp', f'聞く 窓：見出し「効果タイム！」・7 の カードの 大きい 絵・ボタンは「使わない」「使う」「手札と ボードを 見る」（{aw["btns"]}）')
        check(geo['yes'][3] - geo['yes'][1] >= 56 and geo['no'][3] - geo['no'][1] >= 56 and geo['yes'][2] - geo['yes'][0] >= 130 and geo['no'][2] - geo['no'][0] >= 130 and geo['fs'] >= 18 and geo['qfs'] >= 19
              and geo['no'][2] <= geo['yes'][0] and abs(geo['no'][1] - geo['yes'][1]) <= 1 and geo['img'][2] - geo['img'][0] >= 150 and geo['h3'][1] >= 0 and geo['peek'][3] <= geo['vh'] and geo['img'][3] <= geo['no'][1] and geo['cover'],
              f'「使わない」「使う」は 大きい ボタン（高さ {geo["yes"][3] - geo["yes"][1]}px・幅 {geo["yes"][2] - geo["yes"][0]}px・字 {geo["fs"]}px）が 横に ならぶ・質問の 字 {geo["qfs"]}px・カードの 絵 幅 {geo["img"][2] - geo["img"][0]}px・ぜんぶ 画面の 中')
        shot(pg, 'cb_eff_ask')
        peek(pg)
        check(asked(pg) is None and not pg.evaluate("() => CBApp._t.modOn()") and pg.evaluate(MSG) == '効果タイム！ 7 の 効果を 使う？\n7 を 3まい 山札に もどして、新しく 3まい 引けるよ' and acts(pg) == ['使わない', '7 の 効果を 使う'] and pg.evaluate(V)['phase'] == 'eff',
              '「手札と ボードを 見る」→ 窓が 下がって 手札と ボードが 見える・下の 行の「使わない」「7 の 効果を 使う」で 答えられる（まだ 決まって いない）')
        shot(pg, 'cb_eff_bar')
        tap(pg, '7'); check(modbtns(pg) == ['もどる'], '効果タイムの あいだ：手札を タップしても 見る だけ（セットし直せない）')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        check(asked(pg) is None and acts(pg) == ['使わない', '7 の 効果を 使う'], 'カードを 見て もどっても、下げた 窓は また 出て こない（下の ボタンの まま）')
        pg.locator('#cbOv [data-cb=effyes]').click(); idle(pg)
        sd = said(pg); seen = pg.evaluate("() => window.__seen")
        check(pg.evaluate(HAND) == '2346' and pg.evaluate(DOMHAND) == '2346' and pg.locator('#cbOv .cbdeck .cbn').inner_text() == '20' and any('7 を 3まい もどして、新しく 3まい 引いたよ' in s for s in sd)
              and any('勝ち！' in s for s in seen) and pg.evaluate(V)['turn'] == 2 and acts(pg) == [],
              f'「使う」→ 7 を 3まい もどして 3まい 引いた（手札 {pg.evaluate(DOMHAND)}・山札 20 の まま）→ オープン → 2ターン目')
        start(pg, '77712', '12345'); play(pg, '1'); opp(pg, {'t': 'set', 'k': 2}); pg.evaluate("() => { window.__seen = []; }")
        pg.locator('#cbOv [data-cb=effno]').click()
        hs = pg.evaluate("() => [document.querySelector('#cbOv .cbact').children.length, document.querySelector('#cbOv .cbmsg').textContent, CBApp._t.idle]"); idle(pg)
        check(pg.evaluate(HAND) == '2777' and any('勝ち！' in s for s in pg.evaluate("() => window.__seen")) and pg.evaluate(V)['turn'] == 2, '「使わない」→ 手札は そのまま オープン')
        check(hs == [0, '', False], f'「使わない」を 押した すぐ あと：前の 質問「効果を 使う？」と ボタンは 消える（結果を 見せ終わる まで のこさない：前は 5秒 ほど のこって いた）{hs}')

        print('■ 効果タイム：6（2まい 見せて 相手の 手札を 見る）')
        start(pg, '66123', '12345'); play(pg, '1'); opp(pg, {'t': 'set', 'k': 2})
        check(asked(pg) == ['6 の 効果を 使う？', '6 を 2まい 見せて、相手の 手札を 1まい 見られるよ'] and pg.evaluate(ASKQ)['img'] == 'cb_c6.webp', '6 が 2まい →「6 の 効果を 使う？」')
        pg.locator('#cbOv [data-cb=effyes]').click(); pg.wait_for_timeout(80)
        pm = pg.evaluate("() => ({ h: document.querySelector('#cbOv .cbmod h3').textContent, n: document.querySelectorAll('#cbOv .cbmod .pick .cbc').length, t: document.querySelector('#cbOv .cbmod p').textContent })")
        check(pm['h'] == '6 の 効果' and pm['n'] == 4 and '6 を 2まい 相手に 見せるよ' in pm['t'], f'「使う」→ えらぶ 窓：相手の 手札 4まい（うら）から 1まい')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        check(pg.evaluate("() => CBApp._t.mode.step") == 'ask' and asked(pg) == ['6 の 効果を 使う？', '6 を 2まい 見せて、相手の 手札を 1まい 見られるよ'] and pg.evaluate(V)['phase'] == 'eff', '「もどる」→ まだ 決まって いない（聞く 窓に もどる：もう一度 えらべる）')
        pg.locator('#cbOv [data-cb=effyes]').click(); pg.wait_for_timeout(80)
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
        check(any(s.startswith('ban:効果タイム') and 'コンピュータが 効果を 使うか えらぶよ' in s for s in sd) and 'コンピュータが 効果を 使うか えらんで いるよ' in pg.evaluate(MSG) and acts(pg) == [] and asked(pg) is None and pg.evaluate(V)['wait'] is True,
              '相手だけ 使える 効果が ある：「コンピュータが 効果を 使うか えらんで いるよ…」（自分は 待つ）')
        r = opp(pg, {'t': 'eff', 'use': {'p6k': 2}}); sd = said(pg)
        check(r['ok'] and pg.locator('#cbOv .cbhand .cbc .eye').count() == 1 and pg.locator('#cbOv .cbhand .cbc:has(.eye) img').get_attribute('src') == 'cb_s2.webp' and pg.locator('#cbOv .cbohand .cbc img[src="cb_s6.webp"]').count() == 2
              and any('あなたの 手札を 1まい 見たよ' in s for s in sd), '相手が 6 の 効果：相手の 6 が 2まい 表に・見られた 自分の カード（2）に 目の しるし')
        tap(pg, '2'); check('この カードは 相手に 見られて いるよ' in pg.locator('#cbOv .cbmod').inner_text(), '見られた カードを タップ →「相手に 見られて いるよ」')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click()
        shot(pg, 'cb_seen')
        # 2人とも えらぶ：相手が 先に 決めても、自分の えらび とちゅうは 消えない・相手が 何を 使うかは わからない
        start(pg, '66123', '77712', '345'); play(pg, '1'); opp(pg, {'t': 'set', 'k': 2})
        pg.locator('#cbOv [data-cb=effyes]').click(); pg.wait_for_timeout(80); said(pg)
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
        check(asked(pg) == ['5 の 効果を 使う？', '5 と 手札 1まいを 捨てて、山札から 1まい セットできるよ'] and pg.evaluate(ASKQ)['img'] == 'cb_c5.webp', '5 を セットして 手札 4まい →「5 の 効果を 使う？」')
        pg.locator('#cbOv [data-cb=effyes]').click(); pg.wait_for_timeout(80)
        check(pg.evaluate("() => CBApp._t.mode.step") == 'drop5' and '5 と いっしょに 捨てる カードを えらんでね' in pg.evaluate(MSG) and acts(pg) == ['もどる'] and asked(pg) is None and not pg.evaluate("() => CBApp._t.modOn()"), '「使う」→ 窓が 閉じて、捨てる カードを えらぶ')
        pg.locator('#cbOv .cbact [data-cb=effback]').click(); pg.wait_for_timeout(80)
        check(pg.evaluate("() => CBApp._t.mode.step") == 'ask' and asked(pg) == ['5 の 効果を 使う？', '5 と 手札 1まいを 捨てて、山札から 1まい セットできるよ'], '「もどる」→「使う？」（聞く 窓）に もどれる')
        pg.locator('#cbOv [data-cb=effyes]').click(); pg.wait_for_timeout(80)
        tap(pg, '7')
        check(modbtns(pg) == ['この カードを 捨てる5 と いっしょに 捨てて、山札から 1まい セット', 'もどる'], '手札を タップ →「この カードを 捨てる」')
        said(pg)
        pg.locator('#cbOv .cbmod [data-cb=drop5]').click(); idle(pg)
        v = pg.evaluate(V); sd = said(pg)
        check(any('5 と 7 を 捨てて、山札から 1まい セットしたよ' in s for s in sd) and v['turn'] == 2 and v['my']['wins'] == 1 and v['last']['c'] == ['k', '1'] and pg.locator('#cbOv .cbdis .cbn').inner_text() == '4' and pg.evaluate(HAND) == '123',
              f'5 と 7 を 捨てて 山札の 上（神様馬）が セットされた → オープンで 勝ち（捨て札 4まい・手札 {pg.evaluate(HAND)}）')
        # 神様馬で 勝った → 2ターン目の はじめに 聞く 窓が 出て いる（下の「神様馬」の 所で 見る）。捨て札を 見る ために 窓を 下げる
        awk = pg.evaluate(ASKQ); akacts = acts(pg); shot(pg, 'cb_pend_k'); peek(pg)
        pg.locator('#cbOv [data-cb=discard]').click(); pg.wait_for_timeout(80); dm = pg.evaluate(DM)
        check(dm['turns'] == ['ターン 1|あなた=k|コンピュータ=1'] and dm['effs'] == ['ターン 1|あなたの 5 の 効果=57'] and dm['none'] == [], f'捨て札の 窓：終わった ターン（神様馬・1）と、効果で 捨てた カード（あなたの 5 の 効果：5・7）（{dm["effs"]}）')
        shot(pg, 'cb_discard_eff')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)

        print('■ 神様馬：勝った 次の ターンの はじめに、効果を 使うか えらぶ（まさちゃん 23:12）')
        v = pg.evaluate(V)
        check(v['phase'] == 'pre' and v['pend']['mine'] and v['pend']['type'] == 'k' and any(s == 'ban:ターン 2' for s in sd) and any(s.startswith('ban:神様馬の 効果') and '使うか えらんでね' in s for s in sd)
              and sd.index('ban:ターン 2') < [i for i, s in enumerate(sd) if s.startswith('ban:神様馬の 効果')][0]
              and awk and [awk['q'], awk['text']] == ['神様馬の 効果を 使う？', '相手の 手札を 1まい 見られるよ'] and awk['head'] == '神様馬で 勝った！' and awk['img'] == 'cb_ck.webp' and awk['btns'] == ['使わない', '使う', '手札と ボードを 見る']
              and akacts == [] and pg.evaluate(SLOT) == '- -' and pg.locator('#cbOv .cbturn').inner_text().replace('\n', '') == 'ターン 2／3',
              f'2ターン目に 入って から 聞く 窓「神様馬で 勝った！／神様馬の 効果を 使う？」（使わない／使う）・ボードは 片付いて いる（{pg.evaluate(SLOT)}）')
        check(asked(pg) is None and pg.evaluate(MSG) == '神様馬で 勝った！ 効果を 使う？\n相手の 手札を 1まい 見られるよ' and acts(pg) == ['使わない', '神様馬の 効果を 使う'], '「手札と ボードを 見る」（さっき 押した）→ 捨て札の 窓を 閉じた あとも、下の 行の「使わない」「神様馬の 効果を 使う」で 答えられる')
        tap(pg, '1'); check(modbtns(pg) == ['もどる'] and pg.locator('#cbOv .cbglow.on').count() == 0, '決める までは セットできない（手札は 見る だけ）')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        pg.locator('#cbOv [data-cb=kgo]').click(); pg.wait_for_timeout(80)
        pg.evaluate("() => { window.__seen = []; }")
        pg.locator('#cbOv .cbmod .pick .cbc').first.click(); idle(pg)
        seen = pg.evaluate("() => window.__seen"); v = pg.evaluate(V)
        check(any('神様馬の 効果' in s for s in seen) and len([c for c in v['op']['hand'] if c['k']]) == 1 and v['turn'] == 2 and v['phase'] == 'set' and 'セットする カードを えらんでね' in pg.evaluate(MSG) and pg.locator('#cbOv .cbglow.on').count() == 1 and acts(pg) == [],
              '相手の 手札を 1まい 見た → 2ターン目の セットへ')
        start(pg, 'k2367', '12345'); play(pg, 'k'); opp(pg, {'t': 'set', 'k': 1})
        pg.locator('#cbOv [data-cb=kskip]').click(); idle(pg)
        check(pg.evaluate(V)['turn'] == 2 and pg.evaluate(V)['phase'] == 'set' and all(c['k'] is None for c in pg.evaluate(V)['op']['hand']), '「使わない」→ 何も 見ないで 2ターン目の セットへ')
        start(pg, '12367', 'k2345'); play(pg, '1'); said(pg); opp(pg, {'t': 'set', 'k': 'k'}); sd = said(pg)
        check(pg.evaluate(V)['phase'] == 'pre' and pg.evaluate(V)['pend']['mine'] is False and 'コンピュータが 神様馬の 効果を 使うか えらんで いるよ' in pg.evaluate(MSG) and acts(pg) == [] and any(s.startswith('ban:神様馬の 効果') and 'コンピュータが 使うか えらぶよ' in s for s in sd),
              '相手が 神様馬で 勝った：2ターン目の はじめに「コンピュータが 神様馬の 効果を 使うか えらんで いるよ…」（自分は 待つ）')
        opp(pg, {'t': 'k', 'pickk': 2}); sd = said(pg)
        check(any('コンピュータが 神様馬の 効果で、' in s and 'あなたの 手札を 1まい 見たよ' in s for s in sd) and pg.locator('#cbOv .cbhand .cbc:has(.eye) img').get_attribute('src') == 'cb_s2.webp' and pg.evaluate(V)['phase'] == 'set' and pg.evaluate(V)['can']['set'], '相手が 効果を 使った → 見られた カードに 目の しるし → セットへ')

        print('■ 幻の馬：勝った 次の ターンの はじめに、2まい 捨てて 2まい 引く')
        start(pg, 'm6712', '12345', '13'); play(pg, 'm'); opp(pg, {'t': 'set', 'k': 1})
        check(pg.evaluate(V)['phase'] == 'pre' and pg.evaluate(V)['turn'] == 2 and asked(pg) == ['幻の馬の 効果を 使う？', '手札を 2まい 捨てて、山札から 2まい 引けるよ'] and pg.evaluate(ASKQ)['head'] == '幻の馬で 勝った！' and pg.evaluate(ASKQ)['img'] == 'cb_cm.webp', '2ターン目の はじめ：聞く 窓「幻の馬で 勝った！／幻の馬の 効果を 使う？」（使わない／使う）')
        pg.locator('#cbOv [data-cb=mpick]').click(); pg.wait_for_timeout(80)
        check(pg.evaluate("() => CBApp._t.mode.k") == 'dropm' and '（0／2）' in pg.evaluate(MSG) and pg.locator('#cbOv .cbact [data-cb=mgo]').is_disabled() and asked(pg) is None, '「使う」→ 窓が 閉じて、捨てる 2まいを えらぶ（えらぶ まで ボタンは 押せない）')
        pg.locator('#cbOv .cbact [data-cb=modex]').click(); pg.wait_for_timeout(80)
        check(asked(pg) == ['幻の馬の 効果を 使う？', '手札を 2まい 捨てて、山札から 2まい 引けるよ'] and pg.evaluate("() => CBApp._t.mode.k") == 'idle', '「もどる」→ 聞く 窓に もどる（まだ 決まって いない）')
        pg.locator('#cbOv [data-cb=mpick]').click(); pg.wait_for_timeout(80)
        tap(pg, '6'); tap(pg, '7'); tap(pg, '1')      # 3まい目は えらべない
        check(pg.locator('#cbOv .cbhand .cbc.sel').count() == 2 and '（2／2）' in pg.evaluate(MSG) and pg.locator('#cbOv .cbact [data-cb=mgo]').is_enabled(), '2まい えらんだ（3まい目は えらべない）')
        tap(pg, '7'); tap(pg, '7')                     # はずして もう一度
        pg.locator('#cbOv .cbact [data-cb=mgo]').click(); idle(pg)
        check(pg.evaluate(HAND) == '1123' and pg.evaluate(V)['turn'] == 2 and pg.evaluate(V)['phase'] == 'set' and pg.locator('#cbOv .cbdeck .cbn').inner_text() == '18' and pg.locator('#cbOv .cbdis .cbn').inner_text() == '4',
              f'6 と 7 を 捨てて 2まい（1・3）引いた（手札 {pg.evaluate(HAND)}・山札 18・捨て札 4）→ セットへ')
        pg.locator('#cbOv [data-cb=discard]').click(); pg.wait_for_timeout(80); dm = pg.evaluate(DM)
        check(dm['turns'] == ['ターン 1|あなた=m|コンピュータ=1'] and dm['effs'] == ['ターン 2はじめ|あなたの 幻の馬の 効果=67'], f'捨て札の 窓：効果で 捨てた カード（ターン 2 の はじめ・あなたの 幻の馬の 効果：6・7）（{dm["effs"]}）')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        start(pg, 'm6712', '12345'); play(pg, 'm'); opp(pg, {'t': 'set', 'k': 1}); pg.locator('#cbOv [data-cb=mskip]').click(); idle(pg)
        check(pg.evaluate(HAND) == '1267' and pg.evaluate(V)['phase'] == 'set' and pg.locator('#cbOv .cbdeck .cbn').inner_text() == '20', '「使わない」→ 手札は そのまま セットへ')

        print('■ 効果タイム：4（見せて 強制交換）')
        start(pg, '41236', '15677'); opp(pg, {'t': 'set', 'k': 1})
        tap(pg, '4')
        check(modbtns(pg) == ['この カードを セットするセットしたら もう 変えられないよ', 'もどる'], '4 を タップ：セットの 前は「セットする」だけ')
        pg.locator('#cbOv .cbmod [data-cb=set]').click(); idle(pg)
        check(asked(pg) == ['4 の 効果を 使う？', '4 を 見せて、相手に カードを 交換させるよ'] and pg.evaluate(ASKQ)['img'] == 'cb_c4.webp' and pg.evaluate(SLOT) == 'b 4:セット ずみ', f'4 を セットした あと →「4 の 効果を 使う？」（まだ ふせた まま：{pg.evaluate(SLOT)}）')
        said(pg)
        pg.locator('#cbOv [data-cb=effyes]').click(); idle(pg)
        v = pg.evaluate(V); sd = said(pg)
        check(v['phase'] == 'swap' and v['pend']['mine'] is False and pg.evaluate(SLOT) == 'b 4:4 の 効果' and 'コンピュータが カードを 交換して いるよ' in pg.evaluate(MSG) and any(s.startswith('ban:4 の 効果！') for s in sd), f'「使う」：4 が 表に なって 相手の 交換を 待つ（{pg.evaluate(SLOT)}）')
        pg.evaluate("() => { window.__seen = []; }")
        opp(pg, {'t': 'swap', 'k': 5})
        seen = pg.evaluate("() => window.__seen")
        check(any('勝ち！' in s and '4 が 5 に 勝ったよ' in s for s in seen) and pg.evaluate(V)['my']['wins'] == 1 and pg.locator('#cbOv .cbohand .cbc').count() == 4, '相手は 1 を もどして 5 を 出した → 4 の 勝ち（相手の 手札は 4まいの まま）')
        start(pg, '41236', '15677'); play(pg, '4'); opp(pg, {'t': 'set', 'k': 1}); pg.evaluate("() => { window.__seen = []; }")
        pg.locator('#cbOv [data-cb=effno]').click(); idle(pg)
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

        # 第4.181版（まさちゃん 19:05「4をお互いに出して効果を発動した場合、ドローになる」）：2人とも 4 → 2人とも 効果を 使う → 打ち消して ドロー
        start(pg, '41236', '41567'); play(pg, '4'); opp(pg, {'t': 'set', 'k': 4})
        check(asked(pg) == ['4 の 効果を 使う？', '4 を 見せて、相手に カードを 交換させるよ'], '2人とも 4 を セット → 自分にも「4 の 効果を 使う？」')
        opp(pg, {'t': 'eff', 'use': {'u4': True}}); said(pg)
        pg.evaluate("""() => { window.__seen = []; window.__cls = []; const m = document.querySelector('#cbOv .cbmod');
          const mo = new MutationObserver(() => { const r = m.querySelector('.cbres.on'); if (m.classList.contains('cbopen') && r) window.__cls.push(['my', 'op'].map(x => m.querySelector('[data-sd=' + x + ']').className).join('|')); });
          mo.observe(m, { childList: true, subtree: true, attributes: true }); window.__mo4 = mo; }""")
        pg.locator('#cbOv [data-cb=effyes]').click(); idle(pg)
        seen = pg.evaluate("() => window.__seen"); sd = said(pg); cls = pg.evaluate("() => { window.__mo4.disconnect(); return window.__cls; }"); v = pg.evaluate(V)
        check(any('ドロー！' in x and 'どちらも 4 の 効果を 使った ので 引き分け' in x for x in seen) and any('どちらも 4 の 効果 → 打ち消して ドロー' in x for x in sd)
              and v['turn'] == 2 and v['my']['wins'] == 0 and v['op']['wins'] == 0 and v['last']['res'] == 'tie' and v['last']['d4'] is True and pg.evaluate(PIPS) == '0-0' and pg.evaluate(HAND) == '1236',
              f'2人とも 4 の 効果を 使った →「4 の 効果！ どちらも 4 の 効果 → 打ち消して ドロー」→ オープンは「ドロー！ どちらも 4 の 効果を 使った ので 引き分け」（しるしは ふえない・交換なし：手札 {pg.evaluate(HAND)}）')
        check(bool(cls) and all('ls' not in c.split('|')[0].split() and 'ls' not in c.split('|')[1].split() for c in cls), f'ドローの ときは どちらの カードも 暗く しない（{cls[-1] if cls else None}）')
        start(pg, '41236', '41567'); play(pg, '4'); opp(pg, {'t': 'set', 'k': 4}); opp(pg, {'t': 'eff', 'use': {}})
        pg.evaluate("() => { window.__seen = []; }")
        pg.locator('#cbOv [data-cb=effno]').click(); idle(pg)
        check(any('かぶり！' in x and '同じ カード（4）＝どちらも 負け' in x for x in pg.evaluate("() => window.__seen")) and pg.evaluate(V)['last']['d4'] is False, '2人とも 4 で、2人とも 効果を 使わない → いままで どおり「かぶり！ どちらも 負け」')

        print('■ 効果タイム：使える 効果が 2つ（5 と 7）→ 1つ ずつ 聞く')
        start(pg, '57771', '12346', '2346'); play(pg, '5'); opp(pg, {'t': 'set', 'k': 1})
        check(pg.evaluate("() => CBApp._t.mode.q") == '5' and asked(pg)[0] == '5 の 効果を 使う？', '1つ目：「5 の 効果を 使う？」')
        pg.locator('#cbOv [data-cb=effyes]').click(); pg.wait_for_timeout(80); tap(pg, '1'); pg.locator('#cbOv .cbmod [data-cb=drop5]').click(); pg.wait_for_timeout(120)
        check(pg.evaluate(V)['phase'] == 'eff' and pg.evaluate("() => CBApp._t.mode.q") == '7' and asked(pg)[0] == '7 の 効果を 使う？' and pg.evaluate(ASKQ)['img'] == 'cb_c7.webp' and pg.evaluate(DOMHAND) == '1777',
              '5 の 答え（1 を 捨てる）の あと、2つ目：「7 の 効果を 使う？」（まだ 何も おきて いない：答え終わって から まとめて）')
        said(pg); pg.evaluate("() => { window.__seen = []; }")
        pg.locator('#cbOv [data-cb=effyes]').click(); idle(pg); sd = said(pg)
        i5 = [i for i, s in enumerate(sd) if '5 と 1 を 捨てて' in s]; i7 = [i for i, s in enumerate(sd) if '7 を 3まい もどして' in s]
        check(i5 and i7 and i5[0] < i7[0] and pg.evaluate(HAND) == '346' and pg.evaluate(V)['last']['c'] == ['2', '1'] and pg.evaluate(V)['turn'] == 2, f'両方 使う → 5 → 7 の 順に 出て オープン（手札 {pg.evaluate(HAND)}・出たのは 山札の 2）')
        start(pg, '57771', '12346', '2346'); play(pg, '5'); opp(pg, {'t': 'set', 'k': 1})
        pg.locator('#cbOv [data-cb=effyes]').click(); pg.wait_for_timeout(80); tap(pg, '7'); pg.locator('#cbOv .cbmod [data-cb=drop5]').click(); idle(pg)
        check(pg.evaluate(V)['turn'] == 2 and pg.evaluate(HAND) == '177', '5 の 効果で 7 を 捨てた（7 が 2まいに なる）→ 7 の 効果は 聞かれない')

        print('■ うっかり 押し 防止：聞く 窓が 出て すぐ（0.35秒）は 答えを 受けつけない（すばやく 2回 押しても 2つ目の 質問は 答えた ことに ならない）')
        pg.evaluate("() => { CBApp._guard = null; }")      # ふだんの 動き（0.35秒）
        start(pg, '57771', '12346', '2346'); play(pg, '5'); opp(pg, {'t': 'set', 'k': 1}); pg.wait_for_timeout(450)
        g = pg.evaluate("""() => { const T = CBApp._t, q0 = T.mode.q; document.querySelector('#cbOv .cbask [data-cb=effno]').click(); const q1 = T.mode.q, b = document.querySelector('#cbOv .cbask [data-cb=effno]');
          if (b) b.click(); const pk = document.querySelector('#cbOv .cbask [data-cb=askpeek]'); return { q0, q1, q2: T.mode.q, ask: T.ask, has: !!b, peek: !!pk }; }""")
        check(g == {'q0': '5', 'q1': '7', 'q2': '7', 'ask': True, 'has': True, 'peek': True} and asked(pg)[0] == '7 の 効果を 使う？' and pg.evaluate(V)['phase'] == 'eff',
              f'「使わない」を すばやく 2回：1回目で 5 の 質問に 答える → 同じ 所に 出た「7 の 効果を 使う？」は 2回目では 答えた ことに ならない（まだ 聞いて いる：{g}）')
        pg.wait_for_timeout(420); pg.locator('#cbOv .cbask [data-cb=effyes]').click(); idle(pg)
        check(pg.evaluate(V)['turn'] == 2 and pg.evaluate(HAND) == '1234', f'0.35秒 たてば 押せる：7 の 効果を「使う」→ 7 を 3まい 交換（手札 {pg.evaluate(HAND)}）')
        start(pg, '57771', '12346', '2346'); play(pg, '5'); opp(pg, {'t': 'set', 'k': 1}); pg.wait_for_timeout(450)
        pg.locator('#cbOv .cbask [data-cb=effno]').click()
        g2 = pg.evaluate("() => { const b = document.querySelector('#cbOv .cbask [data-cb=askpeek]'); if (b) b.click(); return { had: !!b, ask: CBApp._t.ask, bar: [...document.querySelectorAll('#cbOv .cbact .cbb')].map(x => x.textContent.trim()) }; }")
        check(g2['had'] and not g2['ask'] and g2['bar'] == ['使わない', '7 の 効果を 使う'], f'「手札と ボードを 見る」は 出て すぐでも 押せる（何も 決まらない：下の 行で 答える {g2["bar"]}）')
        pg.locator('#cbOv .cbact [data-cb=effno]').click(); idle(pg)
        check(pg.evaluate(V)['turn'] == 2 and pg.evaluate(HAND) == '1777', '下の 行の「使わない」は すぐ 押せる（手札は そのまま）')
        pg.evaluate("() => { CBApp._guard = 0; }")

        print('■ 5：2ターン目・3ターン目でも 使える（第4.177版：使った あとの 手札が のこりの ターンの 数より 少なく ならない とき）')
        start(pg, '55123', '12346', '2k'); play(pg, '1'); opp(pg, {'t': 'set', 'k': 2})
        check(pg.evaluate(V)['turn'] == 2 and pg.evaluate(HAND) == '2355', '（1ターン目は 1 を 出して 勝ち → 2ターン目：手札 2・3・5・5）')
        play(pg, '5'); opp(pg, {'t': 'set', 'k': 1})
        check(pg.evaluate(V)['phase'] == 'eff' and pg.evaluate(V)['turn'] == 2 and asked(pg) == ['5 の 効果を 使う？', '5 と 手札 1まいを 捨てて、山札から 1まい セットできるよ'], '2ターン目に 5 を セット（手札 3まい）→「5 の 効果を 使う？」と 聞かれる（前は 1ターン目 だけ）')
        pg.locator('#cbOv [data-cb=effyes]').click(); pg.wait_for_timeout(80); tap(pg, '2'); said(pg); pg.locator('#cbOv .cbmod [data-cb=drop5]').click(); idle(pg); sd = said(pg)
        check(any('5 と 2 を 捨てて、山札から 1まい セットしたよ' in s for s in sd) and pg.evaluate(V)['turn'] == 3 and pg.evaluate(HAND) == '35' and pg.evaluate(V)['last']['c'] == ['2', '1'], f'2ターン目に 使う：5 と 2 を 捨てて 山札の 上（2）で 勝負 → 3ターン目（手札 {pg.evaluate(HAND)}）')
        play(pg, '5'); opp(pg, {'t': 'set', 'k': 3})
        check(pg.evaluate(V)['phase'] == 'eff' and pg.evaluate(V)['turn'] == 3 and pg.evaluate(HAND) == '3' and asked(pg) and asked(pg)[0] == '5 の 効果を 使う？',
              '3ターン目：5 と もう 1まい だけ（まさちゃんの 例）→ 5 を セット（手札 1まい）でも「5 の 効果を 使う？」と 聞かれる')
        pg.locator('#cbOv [data-cb=effyes]').click(); pg.wait_for_timeout(80); tap(pg, '3'); said(pg); pg.evaluate("() => { window.__seen = []; }"); pg.locator('#cbOv .cbmod [data-cb=drop5]').click()
        pg.wait_for_function("() => CBApp._t.ended", timeout=30000); idle(pg); sd = said(pg); v = pg.evaluate(V)
        check(any('5 と 3 を 捨てて、山札から 1まい セットしたよ' in s for s in sd) and v['my']['hand'] == [] and v['last']['c'] == ['k', '3'] and v['res'] == 'win' and any('cb_ck.webp' in s for s in pg.evaluate("() => window.__seen")),
              '使う：5 と さいごの 手札（3）を 捨てて、山札から 来た 神様馬で 勝ち（手札 0まいで おわり）')
        pg.wait_for_function("() => { const g = document.querySelector('#cbOv .cbend .gift'); return g && g.textContent.length > 3; }", timeout=30000)
        pg.locator('#cbOv .cbend [data-cb=menu]').click(); pg.wait_for_timeout(120)
        start(pg, '51237', '12346'); play(pg, '1'); opp(pg, {'t': 'set', 'k': 2}); play(pg, '2'); opp(pg, {'t': 'set', 'k': 1}); play(pg, '3'); opp(pg, {'t': 'set', 'k': 3})
        pg.wait_for_function("() => CBApp._t.ended", timeout=30000); idle(pg)
        check(pg.evaluate(V)['res'] is not None and not any('5 の 効果' in s for s in said(pg)), '5 を セットしなければ 効果タイムは 出ない（5 を 手札に 持って いる だけでは 聞かれない）')
        pg.locator('#cbOv .cbend [data-cb=menu]').click(); pg.wait_for_timeout(120)

        print('■ 3：手札に 3 が 3まい → 3まいを 見せて、その 1まいと 相手の 手札の 1まい（ランダム）を 交換（第4.177版）')
        pg.evaluate("""() => { if (window.__win) return; window.__win = []; new MutationObserver(() => { const m = document.querySelector('#cbOv .cbmod'); if (!m.classList.contains('cbopen')) return;
          const s = (m.querySelector('h3') || {}).textContent + '|' + (m.querySelector('p') ? m.querySelector('p').textContent : '') + '|' + [...m.querySelectorAll('img')].map(i => i.getAttribute('src')).join(','); if (window.__win[window.__win.length - 1] !== s) window.__win.push(s); })
          .observe(document.querySelector('#cbOv .cbmod'), { childList: true, subtree: true, attributes: true }); }""")
        start(pg, '33312', '4567k'); play(pg, '1'); opp(pg, {'t': 'set', 'k': 7})
        aw = pg.evaluate(ASKQ)
        check(pg.evaluate(V)['can']['eff']['e3'] is True and aw and aw['q'] == '3 の 効果を 使う？' and aw['text'] == '3 を 3まい 見せて、その 1まいと 相手の 手札の 1まい（ランダム）を 交換できるよ' and aw['img'] == 'cb_c3.webp' and aw['head'] == '効果タイム！',
              '3 が 3まい（セットした あとの 手札）→ 聞く 窓「3 の 効果を 使う？」（3 の カードの 絵）')
        shot(pg, 'cb_ask3')
        peek(pg)
        fit = pg.evaluate("() => { const m = document.querySelector('#cbOv .cbmsg'); return [m.textContent, m.scrollHeight <= m.clientHeight, m.clientHeight, getComputedStyle(m).fontSize]; }")
        check(fit[0] == '効果タイム！ 3 の 効果を 使う？\n3 を 3まい 見せて、手札を 1まい 交換できるよ' and fit[1] and fit[2] == 44 and acts(pg) == ['使わない', '3 の 効果を 使う'], f'窓を 下げた とき：下の 行に 短い 文（2行に おさまる：字 {fit[3]}）・「使わない」「3 の 効果を 使う」')
        said(pg); pg.evaluate("() => { window.__win.length = 0; }"); h0 = pg.evaluate("() => CBApp._t.view.op.hand.length")
        pg.locator('#cbOv [data-cb=effyes]').click(); idle(pg)
        win = pg.evaluate("() => window.__win"); v = pg.evaluate(V); mine = sorted(c['k'] for c in v['my']['hand']); got = [c for c in v['my']['hand'] if c['k'] not in ('3', '2')] or [c for c in v['my']['hand'] if c['seen'] and c['k'] != '3']
        w3 = [s for s in win if s.startswith('3 の 効果！|')]; wx = [s for s in win if s.startswith('3 の 効果：交換！|')]
        check(w3 and '手札の 3 を 3まい 見せたよ' in w3[0] and w3[0].count('cb_s3.webp') == 3 and wx and len(got) == 1 and f'cb_c{got[0]["k"]}.webp' in wx[0] and 'を もらったよ' in wx[0] and win.index(w3[0]) < win.index(wx[0]),
              f'「使う」→ 3 の カードを 3まい 見せる 窓 → もらった カード（{got[0]["k"] if got else "?"}）を 大きく 見せる 窓')
        check(len(v['my']['hand']) == 4 and mine.count('3') == 2 and '2' in mine and got and got[0]['k'] in ('4', '5', '6', 'k') and len(v['op']['hand']) == h0 and [c['k'] for c in v['op']['hand'] if c['k']] == ['3'] and v['turn'] == 2,
              f'交換した あと：自分の 手札は 3 が 2まい・2・もらった カード（{mine}）・相手の 手札は 4まいの まま で、わたした 3 だけ 表に 見える → オープン → 2ターン目')
        eyes = pg.evaluate("() => [...document.querySelectorAll('#cbOv .cbhand .cbc')].filter(c => c.querySelector('.eye')).map(c => c.querySelector('img').getAttribute('src').replace('cb_s', '').replace('.webp', '')).sort().join('')")
        check(eyes == ''.join(sorted(['3', '3', got[0]['k']])) and pg.locator('#cbOv .cbohand .cbc img[src="cb_s3.webp"]').count() == 1 and pg.locator('#cbOv .cbohand .cbc img[src="cb_sb.webp"]').count() == 3,
              f'見せた 3（2まい）と もらった カードに 目の しるし（相手が 知って いる：{eyes}）・相手の 手札の 中に 3 が 1まい 表で 見える')
        shot(pg, 'cb_after3')
        start(pg, '33312', '4567k'); play(pg, '1'); opp(pg, {'t': 'set', 'k': 7}); pg.locator('#cbOv [data-cb=effno]').click(); idle(pg)
        check(pg.evaluate(HAND) == '2333' and pg.evaluate(V)['turn'] == 2 and all(c['k'] is None for c in pg.evaluate(V)['op']['hand']), '「使わない」→ 交換しないで オープン（手札は 3・3・3・2 の まま）')
        # 相手が 3 の 効果を 使う
        start(pg, '12456', '33312'); play(pg, '1'); said(pg); pg.evaluate("() => { window.__win.length = 0; }")
        opp(pg, {'t': 'set', 'k': 2})
        check(pg.evaluate(V)['phase'] == 'eff' and pg.evaluate(V)['can']['eff'] is None and asked(pg) is None and 'コンピュータが 効果を 使うか えらんで いるよ' in pg.evaluate(MSG), '相手だけ 3 が 3まい：自分は 待つ（聞かれない）')
        b0 = pg.evaluate(HAND); r = opp(pg, {'t': 'eff', 'use': {'x3': True}}); sd = said(pg); win = pg.evaluate("() => window.__win"); v = pg.evaluate(V); b1 = pg.evaluate(HAND)
        lost = [k for k in '2456' if b0.count(k) > b1.count(k)]
        check(r['ok'] and any(s.startswith('3 の 効果！|') and 'コンピュータが 手札の 3 を 3まい 見せたよ' in s and s.count('cb_s3.webp') == 3 for s in win) and len(lost) == 1 and b1.count('3') == 1 and len(b1) == 4
              and any('コンピュータが 3 の 効果を 使ったよ' in s and f'あなたの {lost[0]} と 3 を 交換した' in s for s in sd),
              f'相手が 3 の 効果：3 を 3まい 見せる 窓 →「あなたの {lost[0] if lost else "?"} と 3 を 交換した」・自分の 手札は {b0} → {b1}')
        check(pg.locator('#cbOv .cbohand .cbc img[src="cb_s3.webp"]').count() == 2 and len([c for c in v['op']['hand'] if c['k'] == lost[0]]) == 1 and pg.locator('#cbOv .cbohand .cbc img[src="cb_sb.webp"]').count() == 1
              and pg.locator('#cbOv .cbhand .cbc .eye').count() == 1 and pg.locator('#cbOv .cbhand .cbc:has(.eye) img').get_attribute('src') == 'cb_s3.webp' and v['turn'] == 2,
              '相手の 手札の 中に、見せた 3（2まい）と もと 自分の カードが 表で 見える（のこりの 1まいは うら）・自分に 来た 3 には 目の しるし（相手が 知って いる カード）')

        print('■ 説明の 字が 2行に なっても 画面は 動かない（第4.177版・まさちゃん「説明の文字が二行になると画面が上下して、不自然」）')
        POS = """() => { const R = s => { const r = document.querySelector('#cbOv ' + s).getBoundingClientRect(); return [Math.round(r.top * 10) / 10, Math.round(r.height * 10) / 10]; }, m = document.querySelector('#cbOv .cbmsg');
          const rg = document.createRange(); rg.selectNodeContents(m); const lines = new Set([...rg.getClientRects()].map(q => Math.round(q.top))).size;
          return { opp: R('.cbopp'), board: R('.cbboard'), msg: R('.cbmsg'), me: R('.cbme'), hand: R('.cbhand'), act: R('.cbact'), lines: lines, fit: m.scrollHeight <= m.clientHeight, text: m.textContent }; }"""
        same = lambda a, b: all(a[k] == b[k] for k in ('opp', 'board', 'msg', 'me', 'hand', 'act'))
        start(pg, '41236', '15677'); q1 = pg.evaluate(POS)                                                       # 1行：セットする カードを えらんでね
        play(pg, '4'); opp(pg, {'t': 'set', 'k': 1}); qa = pg.evaluate(POS); peek(pg); q2 = pg.evaluate(POS)     # 聞く 窓の うしろ（1行）→ 窓を 下げる（2行）
        pg.locator('#cbOv [data-cb=effyes]').click(); idle(pg); q3 = pg.evaluate(POS)                            # コンピュータが カードを 交換して いるよ…
        start(pg, '15677', '41236'); play(pg, '1'); opp(pg, {'t': 'set', 'k': 4}); opp(pg, {'t': 'eff', 'use': {'u4': True}}); q4 = pg.evaluate(POS)      # 2行：…4 の 効果を 使ったよ！／セットした カードと 交換する 手札を えらんでね
        start(pg, 'm6712', '12345'); play(pg, 'm'); opp(pg, {'t': 'set', 'k': 1}); peek(pg); q5 = pg.evaluate(POS); pg.locator('#cbOv [data-cb=mpick]').click(); pg.wait_for_timeout(80); q6 = pg.evaluate(POS)
        qs = [q1, qa, q2, q3, q4, q5, q6]
        check(q1['lines'] == 1 and q2['lines'] == 2 and q4['lines'] == 2 and q5['lines'] == 2 and all(q['fit'] for q in qs), f'（くらべる 場面：1行 {[q["lines"] for q in qs].count(1)}こ・2行 {[q["lines"] for q in qs].count(2)}こ・どれも 行の 中に おさまる）')
        check(all(same(q1, q) for q in qs) and q1['msg'][1] == 44 and q1['act'][1] == 48, f'字が 1行でも 2行でも、ボード・手札・ボタンの 場所は 1画素も 動かない（ことばの 行 {q1["msg"][1]}px・ボタンの 行 {q1["act"][1]}px・ボードの 上 {sorted(set(q["board"][0] for q in qs))}）')
        TEXTS = ['コンピュータが 4 の 効果を 使ったよ！\nセットした カードと 交換する 手札を えらんでね', 'コンピュータが カードを 交換して いるよ…', '神様馬で 勝った！ 効果を 使う？\n相手の 手札を 1まい 見られるよ', 'コンピュータが 神様馬の 効果を 使うか えらんで いるよ…',
                 '幻の馬で 勝った！ 効果を 使う？\n手札を 2まい 捨てて、山札から 2まい 引けるよ', 'コンピュータが 幻の馬の 効果を 使うか えらんで いるよ…', 'コンピュータが 効果を 使うか えらんで いるよ…', 'コンピュータは もう セットしたよ。セットする カードを えらんでね',
                 'セットする カードを えらんでね（カードを タップ）', '5 と いっしょに 捨てる カードを えらんでね（カードを タップ）', '捨てる カードを 2まい えらんでね（2／2）', '効果を 使うか えらんでね', '相手を 待って いるよ…',
                 '逆転の チャンス！ 1 の 効果を 使う？\n手札の 1 を 1まい 捨てて、幻の馬に 勝てるよ', '逆転の チャンス！ 1 の 効果を 使う？\n手札の 1 を 1まい 捨てて、神様馬に 勝てるよ', '逆転の チャンス！ 2 の 効果を 使う？\n手札の 2 を 1まい 捨てて、1 に 勝てるよ',
                 'コンピュータが 逆転勝利を 使うか えらんで いるよ…', 'ともだちが 逆転勝利を 使うか えらんで いるよ…']
        TEXTS += [f'効果タイム！ {k} の 効果を 使う？\n{t}' for k, t in (('6', '6 を 2まい 見せて、相手の 手札を 1まい 見られるよ'), ('5', '5 と 手札 1まいを 捨てて、山札から 1まい セットできるよ'), ('7', '7 を 3まい 山札に もどして、新しく 3まい 引けるよ'), ('3', '3 を 3まい 見せて、手札を 1まい 交換できるよ'), ('4', '4 を 見せて、相手に カードを 交換させるよ'))]
        FIT = """(ts) => ts.map(t => { CBApp._t.say(t); const m = document.querySelector('#cbOv .cbmsg'), r = m.getBoundingClientRect(); return [m.scrollHeight <= m.clientHeight, parseFloat(getComputedStyle(m).fontSize), Math.round(r.height), Math.round(document.querySelector('#cbOv .cbboard').getBoundingClientRect().top * 10) / 10]; })"""
        f390 = pg.evaluate(FIT, TEXTS)
        check(all(x[0] and x[2] == 44 for x in f390) and len(set(x[3] for x in f390)) == 1 and min(x[1] for x in f390) >= 12.5, f'ことばの 行に 出る 文 {len(TEXTS)}こ：どれも 行の 中に おさまる・行の 高さは 44px の まま（幅 390px：字 {min(x[1] for x in f390)}〜{max(x[1] for x in f390)}px）')
        for vw, vh in ((375, 667), (320, 568)):
            pg.set_viewport_size({'width': vw, 'height': vh}); pg.wait_for_timeout(250); ff = pg.evaluate(FIT, TEXTS)
            check(all(x[0] and x[2] == 44 for x in ff) and len(set(x[3] for x in ff)) == 1 and min(x[1] for x in ff) >= 10.5, f'幅 {vw}px でも：どれも おさまる・ボードは 動かない（入らない 文は 字を 小さく：{min(x[1] for x in ff)}〜{max(x[1] for x in ff)}px）')
        # 小さい 画面（iPhone SE：375×647）でも 聞く 窓・GET の 札が 画面に おさまる
        pg.set_viewport_size({'width': 375, 'height': 647}); pg.wait_for_timeout(250)
        start(pg, '33312', '4567k'); play(pg, '1'); opp(pg, {'t': 'set', 'k': 7})
        se_ = pg.evaluate("""() => { const m = document.querySelector('#cbOv .cbmod.cbask'), R = e => { const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; };
          return { h3: R(m.querySelector('h3')), img: R(m.querySelector('.big')), q: R(m.querySelector('.askq')), row: R(m.querySelector('.rowb')), peek: R(m.querySelector('[data-cb=askpeek]')), vh: innerHeight, vw: innerWidth }; }""")
        order = [se_['h3'], se_['img'], se_['q'], se_['row'], se_['peek']]
        check(se_['h3'][1] >= 0 and se_['peek'][3] <= se_['vh'] and all(a[3] <= b[1] + 1 for a, b in zip(order, order[1:])) and all(r[0] >= 0 and r[2] <= se_['vw'] for r in order) and se_['img'][2] - se_['img'][0] >= 130,
              f'iPhone SE（375×647）：聞く 窓は 上から 見出し・絵・質問・ボタン・「見る」が 重ならずに 画面の 中（絵の 幅 {se_["img"][2] - se_["img"][0]}px・下の はし {se_["peek"][3]}／{se_["vh"]}）')
        shot(pg, 'cb_ask_se')
        pg.locator('#cbOv [data-cb=effno]').click(); idle(pg)
        pg.set_viewport_size({'width': 390, 'height': 844}); pg.wait_for_timeout(250)

        print('■ 5ターン・手札 7まい（第4.178版・まさちゃん「カードバトル５ターン勝負にする 手札7枚にして！」）')
        start(pg, '1234567', '1234567', turns=5)
        v = pg.evaluate(V)
        G7 = """() => { const R = s => { const r = document.querySelector('#cbOv ' + s).getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; };
          const cc = [...document.querySelectorAll('#cbOv .cbhand .cbc')], cs = cc.map(c => c.getBoundingClientRect()), os = [...document.querySelectorAll('#cbOv .cbohand .cbc')].map(c => c.getBoundingClientRect());
          const hit = cc.map((c, i) => { const r = cs[i], nx = cs[i + 1] ? cs[i + 1].left : r.right, e = document.elementFromPoint((r.left + nx) / 2, r.top + r.height / 2); return !!e && (e === c || c.contains(e)); });
          return { vw: innerWidth, vh: innerHeight, n: cs.length, on: os.length, cw: Math.round(cs[0].width * 10) / 10, ch: Math.round(cs[0].height * 10) / 10, left: Math.round(cs[0].left), right: Math.round(cs[cs.length - 1].right), step: Math.round((cs[1].left - cs[0].left) * 10) / 10,
            top: Math.round(Math.min(...cs.map(c => c.top))), bottom: Math.round(Math.max(...cs.map(c => c.bottom))), oleft: Math.round(os[0].left), oright: Math.round(os[os.length - 1].right), ow: Math.round(os[0].width), hit: hit,
            msg: R('.cbmsg'), hand: R('.cbhand'), act: R('.cbact'), board: R('.cbboard'), opp: R('.cbohand'), topbar: R('.cbtop'), me: R('.cbme') }; }"""
        g = pg.evaluate(G7)
        check(v['turns'] == 5 and v['turn'] == 1 and len(v['my']['hand']) == 7 and len(v['op']['hand']) == 7 and v['deckN'] == 16 and pg.evaluate(DOMHAND) == '1234567' and pg.locator('#cbOv .cbohand .cbc').count() == 7 and pg.locator('#cbOv .cbdeck .cbn').inner_text() == '16'
              and pg.locator('#cbOv .cbturn').inner_text().replace('\n', '') == 'ターン 1／5' and pg.evaluate("() => ['op', 'my'].map(p => document.querySelectorAll('#cbOv .cbpips[data-p=' + p + '] i').length).join()") == '5,5' and pg.evaluate(PIPS) == '0-0',
              f'はじめ：手札 7まい（強い 順）・相手の 手札 7まい（うら）・山札 16・ターン 1／5・勝ちの しるしは 5つ ずつ（{pg.evaluate(DOMHAND)}）')
        fits = lambda q, vw, vh: (q['n'] == 7 and q['on'] == 7 and q['left'] >= 0 and q['right'] <= vw and q['oleft'] >= 0 and q['oright'] <= vw and abs(q['ch'] - q['cw'] * 1.5) < 1.5 and q['step'] >= q['cw'] * 0.59 and q['top'] >= q['me'][3] - 1 and q['bottom'] <= q['act'][1] + 1
                                  and q['act'][3] <= vh and q['topbar'][1] >= 0 and q['opp'][3] <= q['board'][1] + 30 and q['board'][3] <= q['msg'][1] + 20 and q['msg'][3] <= q['me'][1] + 1 and all(q['hit']))
        check(fits(g, 390, 844) and g['cw'] >= 76 and g['step'] >= 44, f'手札 7まいの ならび（390×844）：ぜんぶ 画面の 中・重なりは 40% まで（カード {g["cw"]}×{g["ch"]}・見える 幅 {g["step"]}px：44px 以上）・どの カードも 見える 所を 押せば その カード・ボタンの 行まで 画面の 中')
        shot(pg, 'cb7_turn1')
        for vw, vh, cwmin in ((375, 647, 72), (375, 667, 72), (320, 568, 60)):
            pg.set_viewport_size({'width': vw, 'height': vh}); pg.wait_for_timeout(300); q = pg.evaluate(G7)
            check(fits(q, vw, vh) and q['cw'] >= cwmin, f'手札 7まいの ならび（{vw}×{vh}）：ぜんぶ 画面の 中（カード {q["cw"]}×{q["ch"]}・見える 幅 {q["step"]}px・相手の カード {q["ow"]}px・下の はし {q["act"][3]}／{vh}）')
            if (vw, vh) == (375, 647): shot(pg, 'cb7_se')
        pg.set_viewport_size({'width': 390, 'height': 844}); pg.wait_for_timeout(300)
        # 5ターン ぜんぶ やる：1・2・3・6・7 を 出す（4・5 は 出さない：効果タイムに ならない ように）。相手は 2・3・1・7・6
        said(pg); log5 = []
        for mine, his in (('1', '2'), ('2', '3'), ('3', '1'), ('6', '7'), ('7', '6')):
            play(pg, mine); opp(pg, {'t': 'set', 'k': his}); vv = pg.evaluate(V); log5.append((vv['turn'], vv['my']['wins'], vv['op']['wins'], vv['phase']))
        pg.wait_for_function("() => { const g = document.querySelector('#cbOv .cbend .gift'); return CBApp._t.ended && g && g.textContent.length > 3; }", timeout=30000)
        sd = said(pg); v = pg.evaluate(V)
        e = pg.evaluate("() => ({ h: document.querySelector('#cbOv .cbend h3').textContent, sc: document.querySelector('#cbOv .cbend .sc').textContent, pips: [...document.querySelectorAll('#cbOv .cbpips')].map(p => p.querySelectorAll('i.on').length + '/' + p.querySelectorAll('i').length).join() })")
        check(log5 == [(2, 1, 0, 'set'), (3, 2, 0, 'set'), (4, 2, 1, 'set'), (5, 3, 1, 'set'), (5, 3, 2, 'end')] and v['res'] == 'win' and len(v['discard']) == 10 and len(v['my']['hand']) == 2 and len(v['op']['hand']) == 2,
              f'5ターン ぜんぶ やる（3ターンで 勝ちが 決まっても つづく）：1ターンに 1まい ずつ 出して 5ターンで おわり・手札は 2まい のこる・捨て札 10まい（{log5}）')
        bans = [s for s in sd if s.startswith('ban:ターン')]
        check(bans == ['ban:ターン 2', 'ban:ターン 3', 'ban:ターン 4', 'ban:ターン 5さいごの 勝負！'] and e['h'] == 'あなたの 勝ち！' and e['sc'].startswith('3 － 2') and e['pips'] == '2/5,3/5',
              f'ターンの 帯：2〜4 は「ターン n」・5ターン目に「さいごの 勝負！」・結果「あなたの 勝ち！ 3 － 2」・勝ちの しるし（相手 2／5・自分 3／5）（{bans}・{e["pips"]}）')
        shot(pg, 'cb7_end')
        pg.locator('#cbOv .cbend [data-cb=menu]').click(); pg.wait_for_timeout(150)

        print('■ 設定の 窓：BGM・効果音・エフェクト（第4.178版・まさちゃん「プレイボードの右下の設定ボタンを押すと、BGMオンかオフと効果エフェクトオンかオフを選べるようにして！」）')
        pg.evaluate("() => { localStorage.removeItem('tengel.cb'); CBApp._t.load(); CBApp._as = null; }")
        s0 = pg.evaluate("() => ({ sets: CBApp._t.sets, app: !!(window.TengelFx && TengelFx.get && TengelFx.get().sound !== false) })")
        check(s0['sets']['raw'] == {'bgm': None, 'se': None, 'fx': None} and s0['sets']['se'] == s0['app'] and s0['sets']['fx'] is True and s0['sets']['bgm'] == (s0['app'] and s0['sets']['as']),
              f'まだ 決めて いない とき：効果音＝アプリの 効果音の 設定（{s0["app"]}）・エフェクト＝オン・BGM＝アプリの 効果音が オン で、消音スイッチに 合わせられる iOS（16.4 から）の とき だけ オン（ここ {s0["sets"]["as"]} → {s0["sets"]["bgm"]}）')
        pg.evaluate("() => { CBApp._as = true; }")
        check(pg.evaluate("() => CBApp._t.sets.bgm") == s0['app'], '（消音スイッチに 合わせられる iOS と 同じ 形に して 見る：BGM は はじめから オン）')
        pg.evaluate("() => { CBApp._as = null; }")
        SETM = """() => { const m = document.querySelector('#cbOv .cbmod.cbset'); if (!m) return null; const R = e => { const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; };
          return { h: m.querySelector('h3').textContent, rows: [...m.querySelectorAll('.cbsw')].map(r => r.dataset.set + ':' + r.querySelector('span').textContent + ':' + [...r.querySelectorAll('.cbseg button')].map(b => b.textContent + (b.classList.contains('on') ? '*' : '') + (b.getAttribute('aria-pressed') === 'true' ? '!' : '')).join('/')),
            btns: [...m.querySelectorAll('.cbb')].map(b => b.textContent.trim()), seg: [...m.querySelectorAll('.cbseg button')].map(R), box: R(m), vh: innerHeight, vw: innerWidth, last: R([...m.querySelectorAll('.cbb')].pop()), h3: R(m.querySelector('h3')), bg: getComputedStyle(m).backgroundColor }; }"""
        pg.locator('#cbOv .cbmenu [data-cb=gear]').click(); pg.wait_for_timeout(120)
        sm = pg.evaluate(SETM); app = '*!' if s0['app'] else ''; napp = '' if s0['app'] else '*!'
        check(sm and sm['h'] == '設定' and sm['rows'] == ['bgm:BGM音楽:オン/オフ*!', f'se:効果音カードや ボタンの 音:オン{app}/オフ{napp}', 'fx:エフェクト光や 動きの 演出:オン*!/オフ'] and sm['btns'] == ['もどる'],
              f'メニューの「設定」→ 設定の 窓：BGM・効果音・エフェクト の 3つ（それぞれ オン／オフ）・「もどる」（{sm and sm["rows"]}）')
        check(sm and all(b[2] - b[0] >= 56 and b[3] - b[1] >= 40 for b in sm['seg']) and sm['h3'][1] >= 0 and sm['last'][3] <= sm['vh'] and all(b[0] >= 0 and b[2] <= sm['vw'] for b in sm['seg']), 'オン／オフの ボタンは 押しやすい 大きさ（幅 56px・高さ 40px 以上）・窓は 画面の 中')
        shot(pg, 'cb_set_menu')
        # エフェクト：オフ → 光の ゆれ・動きを 止める（nofx）／オン → もどる。おぼえる
        FIRE = "() => [...document.querySelectorAll('#cbOv .cbfire')].map(e => { const c = getComputedStyle(e); return c.animationName + ' ' + c.animationDuration + ' ' + c.pointerEvents; })"
        f_on = pg.evaluate(FIRE)
        pg.locator('#cbOv .cbset [data-cb=tg][data-k=fx][data-v="0"]').click(); pg.wait_for_timeout(100)
        f_off = pg.evaluate(FIRE); st1 = pg.evaluate("() => ({ ls: JSON.parse(localStorage.getItem('tengel.cb')), nofx: document.querySelector('#cbOv').classList.contains('nofx'), sets: CBApp._t.sets })")
        check(f_on == ['cbfire 5.6s none', 'cbfire 4.3s none'] and f_off == ['none 0s none', 'none 0s none'] and st1['nofx'] and st1['ls']['fx'] is False and st1['sets']['fx'] is False and pg.evaluate(SETM)['rows'][2] == 'fx:エフェクト光や 動きの 演出:オン/オフ*!',
              f'エフェクト オフ：火の あかりの ゆれ（{f_on}）が 止まる（{f_off}）・おぼえる（tengel.cb の fx:false）・窓の しるしも「オフ」')
        pg.locator('#cbOv .cbset [data-cb=tg][data-k=fx][data-v="1"]').click(); pg.wait_for_timeout(100)
        check(pg.evaluate(FIRE) == f_on and not pg.evaluate("() => document.querySelector('#cbOv').classList.contains('nofx')") and pg.evaluate("() => JSON.parse(localStorage.getItem('tengel.cb')).fx") is True, 'エフェクト オン：ゆれが もどる')
        # 効果音：オフに すると 鳴らさない（音を 鳴らした 数＝__abs が ふえない）／オンに すると 鳴る
        pg.locator('#cbOv .cbset [data-cb=tg][data-k=bgm][data-v="0"]').click(); pg.locator('#cbOv .cbset [data-cb=tg][data-k=se][data-v="0"]').click(); pg.wait_for_timeout(150)
        pg.locator('#cbOv .cbset [data-cb=modx]').click(); pg.wait_for_timeout(100)
        a0 = pg.evaluate("() => window.__abs")
        start(pg, '1234567', '1234567', turns=5); tap(pg, '1'); pg.locator('#cbOv .cbmod [data-cb=set]').click(); idle(pg); pg.wait_for_timeout(250)
        a1 = pg.evaluate("() => window.__abs")
        check(a1 == a0 and pg.evaluate("() => CBApp._t.sets.se") is False and pg.evaluate("() => JSON.parse(localStorage.getItem('tengel.cb')).se") is False, f'効果音 オフ：配る・カードを 押す・セットしても 音を 鳴らさない（鳴らした 数 {a0} → {a1}）')
        pg.locator('#cbOv .cbgear').click(); pg.wait_for_timeout(120)
        sg = pg.evaluate(SETM)
        check(sg and sg['rows'] == ['bgm:BGM音楽:オン/オフ*!', 'se:効果音カードや ボタンの 音:オン/オフ*!', 'fx:エフェクト光や 動きの 演出:オン*!/オフ'] and sg['btns'] == ['対戦に もどる', 'あそび方', '対戦を やめる'] and sg['last'][3] <= sg['vh'],
              f'対戦の 画面：ボードの 右下の 歯車 → 同じ 設定の 窓（えらんだ 形の まま）＋「対戦に もどる」「あそび方」「対戦を やめる」（{sg and sg["btns"]}）')
        shot(pg, 'cb_set_game')
        pg.locator('#cbOv .cbset [data-cb=tg][data-k=se][data-v="1"]').click(); pg.wait_for_timeout(350)
        a2 = pg.evaluate("() => window.__abs")
        pg.locator('#cbOv .cbset [data-cb=modx]').click(); pg.wait_for_timeout(100)
        tap(pg, '2'); pg.wait_for_timeout(300); a3 = pg.evaluate("() => window.__abs"); pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(80)
        if HAVE:
            check(a2 == a1 + 1 and a3 == a2 + 1 and pg.evaluate("() => CBApp._t.sets.se") is True, f'効果音 オン：オンに した とき 1回 鳴る・カードを 押すと 鳴る（{a1} → {a2} → {a3}）')
        else:
            check(pg.evaluate("() => CBApp._t.sets.se") is True, '効果音 オン（音の ファイルが ない ので 鳴らした 数は 見ない）')
        check(pg.evaluate("() => CBApp._t.screen") == 'game' and pg.evaluate(V)['my']['set'] is not None and pg.evaluate(V)['turn'] == 1, '設定の 窓を 開いても 対戦は そのまま（セットした カードも そのまま）')
        # BGM：オン → 鳴る（くり返す 所は まん中の 1回り）／アプリが うしろ → 止まる・もどる → つづきから／オフ → 止まる／カードバトルを 閉じる → 止まる
        pg.locator('#cbOv .cbgear').click(); pg.wait_for_timeout(120)
        pg.locator('#cbOv .cbset [data-cb=tg][data-k=bgm][data-v="1"]').click()
        b0 = pg.evaluate("() => ({ want: CBApp._t.bgm.want, raw: CBApp._t.sets.raw.bgm, ls: JSON.parse(localStorage.getItem('tengel.cb')).bgm })")
        check(b0 == {'want': True, 'raw': True, 'ls': True} and pg.evaluate(SETM)['rows'][0] == 'bgm:BGM音楽:オン*!/オフ', 'BGM オン：おぼえる（tengel.cb の bgm:true）・窓の しるしも「オン」')
        if HAVE:
            pg.wait_for_function("() => CBApp._t.bgm.on", timeout=30000)
            b1 = pg.evaluate("() => CBApp._t.bgm"); pg.wait_for_timeout(700); b2 = pg.evaluate("() => CBApp._t.bgm")
            check(b1['file'] == 'cb_bgm.m4a' and abs(b1['len'] - 34 * 3 * 60 / 76) < 1e-6 and b1['pre'] == 0.5 and b1['loop'] and abs(b1['loop'][0] - 0.25) < 1e-6 and abs(b1['loop'][1] - (0.25 + b1['len'])) < 1e-6 and 0 < b1['vol'] <= 0.6 and b1['ctx'] == 'running' and b2['pos'] > b1['pos'] + 0.4,
                  f'BGM が 鳴る：cb_bgm.m4a・くり返すのは まん中の 1回り（{b1["loop"] and [round(x, 2) for x in b1["loop"]]}秒：約 {b1["len"]:.1f}秒）・音の 大きさ {b1["vol"]}・曲が 進む（{b1["pos"]:.2f} → {b2["pos"]:.2f}秒）')
            HID = "(h) => { Object.defineProperty(document, 'hidden', { configurable: true, get: () => h }); document.dispatchEvent(new Event('visibilitychange')); }"
            pg.evaluate(HID, True); pg.wait_for_timeout(150); b3 = pg.evaluate("() => CBApp._t.bgm"); pg.wait_for_timeout(600); b4 = pg.evaluate("() => CBApp._t.bgm")
            check(not b3['on'] and not b3['want'] and b3['have'] and abs(b4['pos'] - b3['pos']) < 1e-6 and b3['pos'] >= b2['pos'], f'アプリが うしろに 行った：BGM は 止まる（曲の 場所は {b3["pos"]:.2f}秒で 止まった まま）')
            pg.evaluate(HID, False); pg.wait_for_function("() => CBApp._t.bgm.on", timeout=10000); pg.wait_for_timeout(300); b5 = pg.evaluate("() => CBApp._t.bgm")
            check(b5['on'] and b3['pos'] <= b5['pos'] <= b3['pos'] + 2.5, f'もどった：つづきから 鳴る（{b3["pos"]:.2f} → {b5["pos"]:.2f}秒：曲の 頭に もどらない）')
            pg.evaluate("() => { delete document.hidden; }")
            pg.locator('#cbOv .cbset [data-cb=tg][data-k=bgm][data-v="0"]').click(); pg.wait_for_timeout(120)
            check(not pg.evaluate("() => CBApp._t.bgm.on") and pg.evaluate("() => JSON.parse(localStorage.getItem('tengel.cb')).bgm") is False, 'BGM オフ：止まる・おぼえる')
            pg.locator('#cbOv .cbset [data-cb=tg][data-k=bgm][data-v="1"]').click(); pg.wait_for_function("() => CBApp._t.bgm.on", timeout=10000)
            pg.locator('#cbOv .cbset [data-cb=quit]').click(); pg.locator('#cbOv .cbmod [data-cb=quitgo]').click(); pg.wait_for_timeout(150)
            check(pg.evaluate("() => CBApp._t.screen") == 'menu' and pg.evaluate("() => CBApp._t.bgm.on"), '対戦を やめて メニューに もどっても BGM は つづく（カードバトルを 開いて いる 間）')
            pg.locator('#cbOv .cbmenu [data-cb=close]').click(); pg.wait_for_timeout(200)
            c1 = pg.evaluate("() => CBApp._t.bgm"); pg.wait_for_timeout(1200); c2 = pg.evaluate("() => CBApp._t.bgm")
            check(not c1['on'] and not c1['want'] and not c2['have'] and c2['ctx'] == 'suspended', f'カードバトルを 閉じた：BGM は 止まる・ほどいた 音は 手ばなす・音の 出口は 休む（{c2["ctx"]}）')
            open_cb(pg); pg.wait_for_function("() => CBApp._t.bgm.on", timeout=30000)
            check(pg.evaluate("() => CBApp._t.bgm.ctx") == 'running', 'もう一度 開く：おぼえた 設定（オン）で また 鳴る')
        else:
            pg.wait_for_timeout(800); bn = pg.evaluate("() => CBApp._t.bgm")
            check(not bn['on'] and bn['gone'] and bn['want'], 'BGM の ファイルが ない ビルド：オンに しても 何も 鳴らさない（止まらない・エラーに ならない）')
            pg.locator('#cbOv .cbset [data-cb=quit]').click(); pg.locator('#cbOv .cbmod [data-cb=quitgo]').click(); pg.wait_for_timeout(150)
        # おぼえた 設定は 読み直しても 同じ → もとに もどす（あとの 場面は 決めて いない 形で）
        pg.evaluate("() => CBApp._t.load()")
        check(pg.evaluate("() => CBApp._t.sets.raw") == {'bgm': True, 'se': True, 'fx': True}, '読み直しても えらんだ 設定の まま')
        pg.evaluate("() => { CBApp._t.setSet('bgm', false); localStorage.removeItem('tengel.cb'); CBApp._t.load(); }"); pg.wait_for_timeout(150)
        check(pg.evaluate("() => CBApp._t.sets.raw") == {'bgm': None, 'se': None, 'fx': None} and not pg.evaluate("() => CBApp._t.bgm.on"), '（設定を 消して もとに もどした：BGM は 止まって いる）')

        print('■ 6：相手の 手札が もう 見た カード だけの ときは 聞かれない（第4.178版・まさちゃん「6.の効果は、もう見てるカードしかない場合は、発動しなくして！」）')
        KNOW = "(ks) => { const S = CBApp._t.match._.state(); S.p[1].hand.filter(c => ks.indexOf(c.k) >= 0).forEach(c => { if (S.p[0].known.indexOf(c.u) < 0) S.p[0].known.push(c.u); }); }"      # テスト用：相手の 手札の ks を「もう 見た」ことに する
        start(pg, '66123', '12345'); pg.evaluate(KNOW, ['3', '4']); play(pg, '1'); opp(pg, {'t': 'set', 'k': 2})
        check(asked(pg) == ['6 の 効果を 使う？', '6 を 2まい 見せて、相手の 手札を 1まい 見られるよ'] and pg.locator('#cbOv .cbohand .cbc img[src="cb_sb.webp"]').count() == 2, '相手の 手札 4まいの うち 2まいを もう 見た：まだ 見て いない カードが ある ので 6 の 効果は 聞かれる')
        pg.locator('#cbOv [data-cb=effyes]').click(); pg.wait_for_timeout(80)
        pm = pg.evaluate("() => ({ n: document.querySelectorAll('#cbOv .cbmod .pick .cbc').length, dis: [...document.querySelectorAll('#cbOv .cbmod .pick .cbc')].filter(b => b.disabled).map(b => b.querySelector('img').getAttribute('src')).sort().join(), can: document.querySelectorAll('#cbOv .cbmod .pick .cbc[data-cb=pick]').length, t: document.querySelector('#cbOv .cbmod p').textContent })")
        check(pm == {'n': 4, 'dis': 'cb_s3.webp,cb_s4.webp', 'can': 2, 't': pm['t']} and 'もう 見た カードは えらべないよ' in pm['t'], f'えらぶ 窓：もう 見た カード（3・4：表・暗く）は 押せない・えらべるのは まだ 見て いない 2まい だけ（{pm["dis"]}）')
        pg.evaluate("() => { document.querySelector('#cbOv .cbmod .pick .cbc:disabled').click(); }"); pg.wait_for_timeout(80)
        check(pg.evaluate("() => CBApp._t.modOn()") and pg.evaluate(V)['phase'] == 'eff', 'もう 見た カードを 押しても 何も おきない')
        pg.locator('#cbOv .cbmod .pick .cbc[data-cb=pick]').first.click(); idle(pg)
        check(pg.evaluate(V)['turn'] == 2 and len([c for c in pg.evaluate(V)['op']['hand'] if c['k']]) == 3, 'まだ 見て いない カードを えらぶ → 見た カードが 3まいに')
        shot(pg, 'cb_pick_known')
        start(pg, '66123', '12345'); pg.evaluate(KNOW, ['1', '2', '3', '4', '5']); play(pg, '1'); said(pg); pg.evaluate("() => { window.__seen = []; }")
        opp(pg, {'t': 'set', 'k': 2}); sd = said(pg); v = pg.evaluate(V)
        check(not any('効果タイム' in s for s in sd) and asked(pg) is None and v['turn'] == 2 and v['phase'] == 'set' and any('勝ち！' in s for s in pg.evaluate("() => window.__seen")) and pg.locator('#cbOv .cbohand .cbc img[src="cb_sb.webp"]').count() == 0 and pg.evaluate(HAND) == '2366',
              '相手の 手札を ぜんぶ もう 見た：6 が 2まい あっても 効果タイムに ならない（聞かれない）→ そのまま オープン')
        start(pg, 'k2367', '12345'); pg.evaluate(KNOW, ['1', '2', '3', '4', '5']); play(pg, 'k'); said(pg); opp(pg, {'t': 'set', 'k': 1}); sd = said(pg); v = pg.evaluate(V)
        check(v['turn'] == 2 and v['phase'] == 'set' and v['pend'] is None and asked(pg) is None and not any('神様馬の 効果' in s for s in sd) and v['my']['wins'] == 1, '神様馬で 勝っても、相手の 手札を ぜんぶ もう 見た ときは 効果を 聞かれない（見る ものが ない）')

        print('■ 夜の フィールド（第4.178版・まさちゃん「フィールドの雰囲気を夜の月あかりと火のライトに照らされてるイメージにして！(デザインは変えないで、差し込んでる光りの色を変えてみて)」）')
        nf = pg.evaluate("""() => { const b = document.querySelector('#cbOv .cbboard'), im = b.querySelector(':scope > img'), fires = [...document.querySelectorAll('#cbOv .cbfire')], g = document.querySelector('#cbOv .cbgear').getBoundingClientRect();
          const hit = document.elementFromPoint(g.left + g.width / 2, g.top + g.height / 2), bg = getComputedStyle(document.querySelector('#cbOv .cbbg')).backgroundImage;
          return { src: im.getAttribute('src'), nat: [im.naturalWidth, im.naturalHeight], fires: fires.map(e => e.parentElement.className.split(' ')[0]), gear: !!hit && hit.classList.contains('cbgear'), bg: bg.slice(0, 200), kids: [...b.children].map(e => e.tagName + '.' + e.className.split(' ')[0]) }; }""")
        check(nf['src'] == 'cb_board.webp' and nf['fires'] == ['cbbg', 'cbboard'] and nf['gear'] and nf['kids'][:3] == ['IMG.', 'DIV.cbfire', 'DIV.cbglow'] and 'radial-gradient' in nf['bg'] and (not HAVE or nf['nat'] == [1254, 706]),
              f'ボードの 絵は 同じ 大きさ・同じ 場所（cb_board.webp {nf["nat"]}）・火の あかり（.cbfire）は 画面と ボードの 上に 1つ ずつ・押す じゃまを しない（歯車を 押せる）')
        if HAVE:
            col = pg.evaluate("""async () => { const im = new Image(); im.src = 'cb_board.webp'; await im.decode(); const c = document.createElement('canvas'); c.width = 200; c.height = 112; const x = c.getContext('2d'); x.drawImage(im, 0, 0, 200, 112);
              const Q = (x0, y0, x1, y1) => { const d = x.getImageData(x0, y0, x1 - x0, y1 - y0).data; let r = 0, g = 0, b = 0; for (let i = 0; i < d.length; i += 4) { r += d[i]; g += d[i + 1]; b += d[i + 2]; } const n = d.length / 4; return [r / n, g / n, b / n]; };
              return { tl: Q(0, 0, 100, 56), br: Q(100, 56, 200, 112), felt: Q(60, 39, 140, 67) }; }""")
            check(col['tl'][2] > col['tl'][0] * 0.75 and col['br'][0] > col['tl'][0] * 1.2 and col['br'][0] > col['br'][2] * 2 and col['felt'][1] > col['felt'][0] * 1.3 and col['felt'][1] > col['felt'][2] * 1.3,
                  f'光の 色：左上は 月あかり（青み：赤 {col["tl"][0]:.0f}・青 {col["tl"][2]:.0f}）・右下は 火の あかり（だいだい：赤 {col["br"][0]:.0f}・青 {col["br"][2]:.0f}）・まん中の フェルトは 緑の まま（{[round(q) for q in col["felt"]]}）')
        pg.emulate_media(reduced_motion='reduce'); pg.wait_for_timeout(100); rm = pg.evaluate(FIRE); pg.emulate_media(reduced_motion='no-preference'); pg.wait_for_timeout(100)
        check(len(rm) == 2 and all(x.startswith('none ') for x in rm) and pg.evaluate(FIRE) == ['cbfire 5.6s none', 'cbfire 4.3s none'], f'iPhone の「視差効果を減らす」が オンの ときは ゆれない（動きの 名前が none：{rm}）')

        print('■ 逆転勝利：1 が 3まい → 神様馬・幻の馬に 勝てる ／ 2 が 3まい → 1 に 勝てる（第4.178版・まさちゃん 15:33・15:41「A、オープンしてから」）')
        start(pg, '11123', 'm4567'); play(pg, '1'); said(pg); pg.evaluate("() => { window.__seen = []; window.__win.length = 0; }")
        opp(pg, {'t': 'set', 'k': 'm'}); seen = pg.evaluate("() => window.__seen"); v = pg.evaluate(V); aw = pg.evaluate(ASKQ)
        check(any('ターン 1　オープン！' in s and 'チャンス！' in s and '幻の馬 の ほうが 強い…でも 1 の「逆転勝利」を 使えるよ' in s and 'cb_c1.webp,cb_cm.webp' in s for s in seen) and not any('負け…' in s for s in seen) and pg.evaluate(PIPS) == '0-0'
              and v['phase'] == 'rev' and v['turn'] == 1 and v['pend'] == {'type': 'rev', 'mine': True} and v['op']['wins'] == 0,
              f'1（手札に 1 が あと 2まい）と 幻の馬 → めくった 窓に「チャンス！ …1 の「逆転勝利」を 使えるよ」（「負け…」は まだ 出ない・勝ちの しるしも まだ）（{seen[-1] if seen else None}）')
        check(aw and aw['head'] == '逆転の チャンス！' and aw['q'] == '1 の 効果を 使う？' and aw['text'] == '手札の 1 を 2まい 見せて、1まい 捨てると、幻の馬に 勝てるよ' and aw['img'] == 'cb_c1.webp' and aw['btns'] == ['使わない', '使う', '手札と ボードを 見る']
              and pg.evaluate(SLOT) == 'm 1' and acts(pg) == [] and pg.evaluate(MSG) == '効果を 使うか えらんでね',
              f'つづけて 聞く 窓「逆転の チャンス！／1 の 効果を 使う？」（1 の カードの 絵・使わない／使う）。ボードには 2まいとも 表（{pg.evaluate(SLOT)}）')
        shot(pg, 'cb_rev_ask')
        peek(pg)
        check(asked(pg) is None and pg.evaluate(MSG) == '逆転の チャンス！ 1 の 効果を 使う？\n手札の 1 を 1まい 捨てて、幻の馬に 勝てるよ' and acts(pg) == ['使わない', '1 の 効果を 使う'], '「手札と ボードを 見る」→ 下の 行の「使わない」「1 の 効果を 使う」で 答えられる')
        tap(pg, '1'); check(modbtns(pg) == ['もどる'], '決める までは 手札を タップしても 見る だけ'); pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        pg.locator('#cbOv .cbact [data-cb=revyes]').click(); idle(pg)
        win = pg.evaluate("() => window.__win"); sd = said(pg); v = pg.evaluate(V)
        w1 = [s for s in win if s.startswith('1 の 効果！|')]
        check(w1 and '1 を 3まい（場の 1まい ＋ 手札の 2まい）見せたよ' in w1[0] and '手札の 1 を 1まい 捨てて、幻の馬に 逆転！' in w1[0] and w1[0].count('cb_s1.webp') == 3 and any(s.startswith('ban:逆転勝利！') and '1 が 幻の馬 に 勝ったよ' in s for s in sd),
              f'「使う」→ 1 の カードを 3まい 見せる 窓 →「逆転勝利！ 1 が 幻の馬 に 勝ったよ」（{w1[0] if w1 else None}）')
        check(v['turn'] == 2 and v['phase'] == 'set' and v['pend'] is None and v['my']['wins'] == 1 and v['op']['wins'] == 0 and pg.evaluate(PIPS) == '0-1' and pg.evaluate(HAND) == '123' and pg.evaluate(DOMHAND) == '123' and pg.locator('#cbOv .cbdis .cbn').inner_text() == '3'
              and v['last'] == {'turn': 1, 'c': ['1', 'm'], 'res': 'win', 'rev': True, 'd4': False} and not any('幻の馬の 効果' in s for s in sd),
              f'勝ちの しるしが 1つ・手札は 1・2・3（1 を 1まい 捨てた）・捨て札 3まい・幻の馬の 効果は 出ない → 2ターン目の セットへ（手札 {pg.evaluate(HAND)}）')
        eye = pg.evaluate("""() => { const es = [...document.querySelectorAll('#cbOv .cbhand .cbc .eye')]; return es.map(e => { const r = e.getBoundingClientRect(), h = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2), c = e.closest('.cbc'), cr = c.getBoundingClientRect();
          return { k: c.querySelector('img').getAttribute('src'), vis: !!h && (h === e || h === c || c.contains(h)), in: r.left >= cr.left - 4 && r.right <= cr.left + cr.width * 0.62 }; }); }""")
        check(eye == [{'k': 'cb_s1.webp', 'vis': True, 'in': True}], f'見せて 手札に のこった 1 に 目の しるし（相手が 知って いる）：しるしは カードの 見える 所（左から 60% の 内がわ）に ある（{eye}）')
        pg.locator('#cbOv [data-cb=discard]').click(); pg.wait_for_timeout(80); dm = pg.evaluate(DM)
        check(dm['turns'] == ['ターン 1|あなた=1|コンピュータ=m'] and dm['effs'] == ['ターン 1|あなたの 1 の 効果=1'], f'捨て札の 窓：効果で 捨てた カードに「あなたの 1 の 効果」（{dm["effs"]}）')
        shot(pg, 'cb_rev_discard')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        # 使わない → そのまま 負け・相手の 幻の馬の 効果
        start(pg, '11123', 'm4567'); play(pg, '1'); opp(pg, {'t': 'set', 'k': 'm'}); said(pg)
        pg.locator('#cbOv .cbask [data-cb=revno]').click(); idle(pg); sd = said(pg); v = pg.evaluate(V)
        check(any(s.startswith('ban:負け…') and '幻の馬 が 1 に 勝ったよ' in s for s in sd) and v['turn'] == 2 and v['phase'] == 'pre' and v['pend'] == {'type': 'm', 'mine': False} and v['op']['wins'] == 1 and v['my']['wins'] == 0 and pg.evaluate(PIPS) == '1-0'
              and pg.evaluate(HAND) == '1123' and pg.locator('#cbOv .cbhand .cbc .eye').count() == 0 and 'コンピュータが 幻の馬の 効果を 使うか えらんで いるよ' in pg.evaluate(MSG),
              '「使わない」→「負け…」・手札は そのまま（何も 見せない）・相手の 幻の馬の 効果（次の ターンの はじめ）は いつも どおり')
        # 神様馬にも・7まいの 手札でも
        start(pg, '1112345', 'mk23456', turns=5); play(pg, '1'); opp(pg, {'t': 'set', 'k': 'k'})
        aw = pg.evaluate(ASKQ)
        check(aw and aw['text'] == '手札の 1 を 2まい 見せて、1まい 捨てると、神様馬に 勝てるよ' and pg.evaluate(V)['phase'] == 'rev', '本番の 形（手札 7まい・5ターン）：1 と 神様馬 →「…神様馬に 勝てるよ」')
        pg.locator('#cbOv .cbask [data-cb=revyes]').click(); idle(pg); v = pg.evaluate(V)
        check(v['turn'] == 2 and v['my']['wins'] == 1 and pg.evaluate(HAND) == '12345' and pg.locator('#cbOv .cbhand .cbc .eye').count() == 1 and v['phase'] == 'set', '使う → 勝ち・手札 5まい（1 が 1まい のこる）')
        play(pg, '1'); pg.evaluate("() => { window.__seen = []; }"); opp(pg, {'t': 'set', 'k': 'm'}); v = pg.evaluate(V)
        check(any('負け…' in s and '幻の馬 の ほうが 強いよ' in s for s in pg.evaluate("() => window.__seen")) and v['turn'] == 3 and v['pend'] == {'type': 'm', 'mine': False} and v['op']['wins'] == 1, '2ターン目：のこった 1 を 出して 幻の馬 → 手札に 1 が ない ので 聞かれない（ふつうに 負け）')
        # 相手が 使う：2 が 3まいで 自分の 1 に 勝つ
        start(pg, '1m345', '22214'); play(pg, '1'); said(pg); pg.evaluate("() => { window.__seen = []; window.__win.length = 0; }")
        opp(pg, {'t': 'set', 'k': 2}); seen = pg.evaluate("() => window.__seen"); v = pg.evaluate(V)
        check(any('勝負は まだ！' in s and 'コンピュータは 2 の「逆転勝利」を 使えるよ' in s for s in seen) and not any('勝ち！' in s for s in seen) and v['phase'] == 'rev' and v['pend'] == {'type': 'rev', 'mine': False} and v['wait'] is True and asked(pg) is None and acts(pg) == []
              and 'コンピュータが 逆転勝利を 使うか えらんで いるよ' in pg.evaluate(MSG) and pg.evaluate(PIPS) == '0-0' and pg.evaluate(SLOT) == '2 1',
              f'自分の 1 と 相手の 2（相手は 2 を 3まい）→ めくった 窓に「勝負は まだ！ コンピュータは 2 の「逆転勝利」を 使えるよ」・自分は 待つ（「勝ち！」は まだ 出ない）')
        shot(pg, 'cb_rev_wait')
        MSGLOG = "() => { window.__msgs = []; const m = document.querySelector('#cbOv .cbmsg'); window.__mo2 = new MutationObserver(() => window.__msgs.push(m.textContent)); window.__mo2.observe(m, { childList: true, characterData: true, subtree: true }); }"
        pg.evaluate(MSGLOG)
        r = opp(pg, {'t': 'rev', 'use': True}); win = pg.evaluate("() => window.__win"); sd = said(pg); v = pg.evaluate(V); msgs = pg.evaluate("() => { window.__mo2.disconnect(); return window.__msgs; }")
        w2 = [s for s in win if s.startswith('2 の 効果！|')]
        check(r['ok'] and w2 and 'コンピュータが 2 を 3まい（場の 1まい ＋ 手札の 2まい）見せたよ' in w2[0] and '手札の 2 を 1まい 捨てて、1 に 逆転！' in w2[0] and w2[0].count('cb_s2.webp') == 3 and any(s.startswith('ban:逆転負け…') and '2 が 1 に 勝ったよ' in s for s in sd),
              f'相手が 使った → 2 の カードを 3まい 見せる 窓 →「逆転負け… 2 が 1 に 勝ったよ」（{w2[0] if w2 else None}）')
        check(v['turn'] == 2 and v['op']['wins'] == 1 and v['my']['wins'] == 0 and pg.evaluate(PIPS) == '1-0' and pg.locator('#cbOv .cbohand .cbc').count() == 3 and pg.locator('#cbOv .cbohand .cbc img[src="cb_s2.webp"]').count() == 1 and pg.locator('#cbOv .cbohand .cbc img[src="cb_sb.webp"]').count() == 2
              and msgs and msgs[0] == '' and v['last']['rev'] is True,
              f'相手の 勝ち・相手の 手札は 3まい（見せて のこった 2 は 表で 見える）・動きの あいだ「…使うか えらんで いるよ…」は 消える（{msgs[:2]}）')
        pg.locator('#cbOv [data-cb=discard]').click(); pg.wait_for_timeout(80); dm = pg.evaluate(DM)
        check(dm['effs'] == ['ターン 1|コンピュータの 2 の 効果=2'], f'捨て札の 窓：「コンピュータの 2 の 効果」（{dm["effs"]}）')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        start(pg, '1m345', '22214'); play(pg, '1'); opp(pg, {'t': 'set', 'k': 2}); said(pg)
        opp(pg, {'t': 'rev', 'use': False}); sd = said(pg); v = pg.evaluate(V)
        check(any('コンピュータは 逆転勝利を 使わなかったよ' in s for s in sd) and any(s.startswith('ban:勝ち！') and '1 が 2 に 勝ったよ' in s for s in sd) and v['my']['wins'] == 1 and pg.evaluate(PIPS) == '0-1' and v['turn'] == 2 and pg.locator('#cbOv .cbohand .cbc img[src="cb_sb.webp"]').count() == 4,
              '相手が 使わなかった →「コンピュータは 逆転勝利を 使わなかったよ」→「勝ち！」（相手の 手札は 見えない まま）')
        # うっかり 押し 防止：聞く 窓が 出て すぐは 受けつけない
        pg.evaluate("() => { CBApp._guard = null; }")
        start(pg, '11123', 'm4567'); play(pg, '1'); opp(pg, {'t': 'set', 'k': 'm'})
        g = pg.evaluate("() => { const b = document.querySelector('#cbOv .cbask [data-cb=revyes]'); if (b) b.click(); return { had: !!b, phase: CBApp._t.view.phase, ask: CBApp._t.ask, idle: CBApp._t.idle }; }")
        check(g == {'had': True, 'phase': 'rev', 'ask': True, 'idle': True}, f'聞く 窓が 出て すぐ（0.35秒）の「使う」は 受けつけない（まだ 聞いて いる：{g}）')
        pg.wait_for_timeout(420); pg.locator('#cbOv .cbask [data-cb=revyes]').click(); idle(pg)
        check(pg.evaluate(V)['turn'] == 2 and pg.evaluate(V)['my']['wins'] == 1, '0.35秒 たてば 押せる（逆転勝利）')
        pg.evaluate("() => { CBApp._guard = 0; }")
        # 小さい 画面（iPhone SE：375×647）でも 聞く 窓・見せる 窓が 画面に おさまる
        pg.set_viewport_size({'width': 375, 'height': 647}); pg.wait_for_timeout(250)
        start(pg, '2221345', '1m34567', turns=5); play(pg, '2'); opp(pg, {'t': 'set', 'k': 1})
        se_ = pg.evaluate("""() => { const m = document.querySelector('#cbOv .cbmod.cbask'), R = e => { const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; };
          return { h3: R(m.querySelector('h3')), img: R(m.querySelector('.big')), q: R(m.querySelector('.askq')), row: R(m.querySelector('.rowb')), peek: R(m.querySelector('[data-cb=askpeek]')), vh: innerHeight, vw: innerWidth, t: m.querySelector('.askq').textContent }; }""")
        order = [se_['h3'], se_['img'], se_['q'], se_['row'], se_['peek']]
        check(se_['t'] == '2 の 効果を 使う？手札の 2 を 2まい 見せて、1まい 捨てると、1 に 勝てるよ' and se_['h3'][1] >= 0 and se_['peek'][3] <= se_['vh'] and all(a[3] <= b[1] + 1 for a, b in zip(order, order[1:])) and all(r[0] >= 0 and r[2] <= se_['vw'] for r in order) and se_['img'][2] - se_['img'][0] >= 120,
              f'iPhone SE（375×647）：2 の 逆転勝利の 聞く 窓「…1 に 勝てるよ」も 重ならずに 画面の 中（絵の 幅 {se_["img"][2] - se_["img"][0]}px・下の はし {se_["peek"][3]}／{se_["vh"]}）')
        shot(pg, 'cb_rev_ask_se')
        pg.locator('#cbOv .cbask [data-cb=revyes]').click(); idle(pg)
        check(pg.evaluate(V)['my']['wins'] == 1 and pg.evaluate(HAND) == '12345' and pg.evaluate(V)['last'] == {'turn': 1, 'c': ['2', '1'], 'res': 'win', 'rev': True, 'd4': False}, '2 の 効果を 使う → 1 に 勝ち（手札 7まいの 形）')
        pg.set_viewport_size({'width': 390, 'height': 844}); pg.wait_for_timeout(250)

        print('■ 結果と ごほうび（お世話トークン）')
        # 勝ち：+1（はじめの 5こ → 6こ）
        pg.evaluate("() => { localStorage.removeItem('tengel.cb'); CBApp._t.load(); }")
        def win_game():
            start(pg, 'k1236', '23567'); play(pg, 'k'); opp(pg, {'t': 'set', 'k': 6}); pg.locator('#cbOv [data-cb=kskip]').click(); idle(pg)      # 2ターン目の はじめ：神様馬の 効果は 使わない
            play(pg, '1'); opp(pg, {'t': 'set', 'k': 7}); play(pg, '2'); opp(pg, {'t': 'set', 'k': 3})
            pg.wait_for_function("() => { const g = document.querySelector('#cbOv .cbend .gift'); return CBApp._t.ended && g && g.textContent.length > 3; }", timeout=30000)
            return pg.evaluate("() => ({ h: document.querySelector('#cbOv .cbend h3').textContent, sc: document.querySelector('#cbOv .cbend .sc').textContent, g: document.querySelector('#cbOv .cbend .gift').textContent, st: Object.assign({}, CBApp._t.state) })")
        t0 = pg.evaluate(TC)
        e = win_game(); t1 = pg.evaluate(TC)
        check(e['st']['coin'] == 1 and 'バトルコイン ＋1枚（いま 1枚）' in e['g'] and pg.locator('#cbOv .cbend .gift .cbcl img[src="cb_coin.webp"]').count() == 1, f'バトルコイン：コンピュータに 勝つと 1枚（いま {e["st"]["coin"]}枚）（第4.179版）')
        check(e['h'] == 'あなたの 勝ち！' and e['sc'].startswith('3 － 0') and t1 == (t0 or 5) + 1 and e['st']['streak'] == 1 and e['st']['win'] == 1 and e['st']['owe'] == 0 and 'お世話トークン＋1こ GET！' in e['g'] and f'いま {t1}こ／25こ' in e['g'] and '1連勝中！' in e['g'] and 'あと 4勝で 3こ' in e['g'],
              f'勝ち：お世話トークン ＋1（{t0 or 5} → {t1}）・1連勝中・あと 4勝で 3こ（{e["g"]}）')
        # 第4.177版（まさちゃん「お世話トークンGETした場合、最後の画面でGETしたことをもう少し分かりやすく」）：金の わくの 札「お世話トークン ＋1こ GET！」
        pg.wait_for_timeout(750)      # 札が ふくらみ おわる まで（0.55秒）
        gb = pg.evaluate("""() => { const m = document.querySelector('#cbOv .cbmod.cbend'), b = m.querySelector('.cbget'), R = e => { const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; };
          if (!b) return null; const n = b.querySelector('.n'), cs = getComputedStyle(b), g = m.querySelector('.gift');
          return { box: R(b), n: n.textContent, nfs: parseFloat(getComputedStyle(n).fontSize), small: b.querySelector('small').textContent, tk: b.querySelector('.tk').textContent, bw: parseFloat(cs.borderTopWidth), bc: cs.borderTopColor, label: b.getAttribute('aria-label'),
            gift: R(g), minh: parseFloat(getComputedStyle(g).minHeight), h3: R(m.querySelector('h3')), again: R(m.querySelector('[data-cb=again]')), vh: innerHeight, vw: innerWidth, anim: cs.animationName, iter: cs.animationIterationCount }; }""")
        check(gb and gb['n'] == '＋1こ GET！' and gb['small'] == 'お世話トークン' and gb['label'] == 'お世話トークン 1こ GET' and gb['nfs'] >= 30 and gb['bw'] >= 2 and gb['box'][2] - gb['box'][0] >= 250 and gb['box'][3] - gb['box'][1] >= 70
              and gb['box'][0] >= 0 and gb['box'][2] <= gb['vw'] and gb['box'][1] >= gb['gift'][1] and gb['box'][3] <= gb['gift'][3],
              f'さいごの 画面に「お世話トークン ＋1こ GET！」の 金の わくの 札（字 {gb and gb["nfs"]}px・幅 {gb and gb["box"][2] - gb["box"][0]}px・高さ {gb and gb["box"][3] - gb["box"][1]}px）')
        check(gb and gb['gift'][3] - gb['gift'][1] == gb['minh'] and gb['minh'] >= 150 and gb['again'][3] <= gb['vh'] and gb['h3'][1] >= 0 and gb['anim'] == 'cbget' and gb['iter'] == '1',
              f'札の 場所は 先に あけて ある（高さ {gb and gb["minh"]}px：札が 出ても「あなたの 勝ち！」や ボタンは 動かない）・札は 1回 ふくらんで 止まる（点めつ しない）')
        shot(pg, 'cb_end_win')
        pg.locator('#cbOv .cbend [data-cb=again]').click(); idle(pg)
        check(pg.evaluate(V)['turn'] == 1 and pg.evaluate(V)['phase'] == 'set' and not pg.evaluate("() => CBApp._t.ended") and pg.evaluate(PIPS) == '0-0' and not pg.evaluate("() => CBApp._t.modOn()"), '「もう 1回」→ すぐ 新しい 対戦（しるしも 0 に）')
        for k in range(3): win_game()
        e = win_game(); t5 = pg.evaluate(TC)
        check(e['st']['coin'] == 9 and 'バトルコイン ＋5枚（いま 9枚）' in e['g'], f'バトルコイン：5連勝目は 5枚（1・1・1・1・5 ＝ {e["st"]["coin"]}枚）')
        check(e['st']['streak'] == 5 and e['st']['win'] == 5 and t5 == t1 + 3 + 3 and '5連勝 ボーナス！ お世話トークン＋3こ GET！' in e['g'] and '5連勝中！' in e['g']
              and pg.evaluate("() => { const g = document.querySelector('#cbOv .cbend .gift'); return Math.round(g.getBoundingClientRect().height) === parseFloat(getComputedStyle(g).minHeight); }"), f'5連勝：5回目は ＋3（{t1} → 2・3・4回目 ＋1 ずつ → 5回目 ＋3 ＝ {t5}）（{e["g"]}）')
        e = win_game()
        check(e['st']['streak'] == 6 and pg.evaluate(TC) == t5 + 1 and 'あと 4勝で 3こ' in e['g'] and e['st']['coin'] == 10 and 'バトルコイン ＋1枚（いま 10枚）' in e['g'], '6連勝目は また ＋1（つぎの ＋3 は 10連勝）・バトルコインも ＋1')
        # 上限 25こ
        pg.evaluate("() => { TCApp.state.stock = 25; TCApp.state.stockAt = Date.now(); }")
        e = win_game()
        check(pg.evaluate(TC) == 25 and 'お世話トークンが いっぱい（25こ）なので、今回は もらえなかったよ' in e['g'] and e['st']['streak'] == 7 and e['st']['owe'] == 0 and pg.locator('#cbOv .cbend .cbget').count() == 0
              and pg.evaluate("() => { const g = document.querySelector('#cbOv .cbend .gift'); return Math.round(g.getBoundingClientRect().height) === parseFloat(getComputedStyle(g).minHeight); }"),
              f'お世話トークンが 25こ の とき：ふえない（連勝は 数える）・GET の 札は 出ない（{e["g"]}）')
        pg.evaluate("() => { TCApp.state.stock = 22; TCApp.state.stockAt = Date.now(); }")
        for k in range(2): win_game()
        e = win_game()      # 10連勝：＋3 の はずが、あと 1こ しか 入らない
        check(e['st']['streak'] == 10 and pg.evaluate(TC) == 25 and 'お世話トークン＋1こ GET！' in e['g'] and '25こ まで なので 1こ だけ' in e['g'] and e['st']['owe'] == 0
              and pg.evaluate("() => { const g = document.querySelector('#cbOv .cbend .gift'); return Math.round(g.getBoundingClientRect().height) === parseFloat(getComputedStyle(g).minHeight); }"), f'10連勝（＋3）で あと 1こ しか 入らない とき：入る 分 だけ（{e["g"]}）')
        check(e['st']['coin'] == 18 and 'バトルコイン ＋5枚（いま 18枚）' in e['g'], f'10連勝目も バトルコイン 5枚（いま {e["st"]["coin"]}枚）・字は 札の 場所に おさまる')
        shot(pg, 'cb_end_coin')
        # 負け：連勝 0
        start(pg, '23677', '12356'); play(pg, '3'); opp(pg, {'t': 'set', 'k': 1}); play(pg, '6'); opp(pg, {'t': 'set', 'k': 2}); play(pg, '7'); opp(pg, {'t': 'set', 'k': 3})
        pg.wait_for_function("() => { const g = document.querySelector('#cbOv .cbend .gift'); return CBApp._t.ended && g && g.textContent.length > 3; }", timeout=30000)
        e = pg.evaluate("() => ({ h: document.querySelector('#cbOv .cbend h3').textContent, g: document.querySelector('#cbOv .cbend .gift').textContent, st: Object.assign({}, CBApp._t.state) })")
        check(e['h'] == 'あなたの 負け…' and e['st']['streak'] == 0 and e['st']['lose'] == 1 and '連勝は 0 に もどったよ' in e['g'] and pg.evaluate(TC) == 25 and pg.locator('#cbOv .cbend .cbget').count() == 0, f'負け：連勝は 0 に もどる・トークンは かわらない・GET の 札は 出ない（{e["g"]}）')
        pg.locator('#cbOv .cbend [data-cb=menu]').click(); pg.wait_for_timeout(120)
        rec = pg.locator('#cbOv .cbmenu .rec').inner_text()
        check(pg.evaluate("() => CBApp._t.screen") == 'menu' and '10勝 1敗 0分' in rec.replace('\n', ' '), f'メニューに 勝ち負けの 数（{rec!r}）')
        check(e['st']['coin'] == 18 and 'バトルコイン' not in e['g'] and 'バトルコイン 18枚' in pg.locator('#cbOv .cbmenu .cbcoinl').inner_text(), '負け：バトルコインは かわらない（へらない）・メニューに いまの 数（18枚）')

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
        done = False; first = None
        for step in range(160):
            idle(pg, 60000)
            if first is None: first = pg.evaluate("() => { const v = CBApp._t.view; return v ? [v.turns, v.my.hand.length + (v.my.set ? 1 : 0), v.op.hand.length + (v.op.set ? 1 : 0), v.deckN] : null; }")
            stt = pg.evaluate("() => { const v = CBApp._t.view; return CBApp._t.ended ? 'end' : !v ? 'none' : v.pend && v.pend.mine ? v.pend.type : v.can.eff ? 'eff' : v.can.set ? 'set' : 'wait'; }")
            if stt == 'end': done = True; break
            if stt in ('k', 'm'): pg.locator(f'#cbOv [data-cb={stt}skip]').click()
            elif stt == 'rev': pg.locator('#cbOv [data-cb=revyes]').first.click()
            elif stt == 'eff': pg.locator('#cbOv [data-cb=effno]').click()
            elif stt == 'swap': pg.locator('#cbOv .cbhand .cbc').first.click(); pg.wait_for_timeout(60); pg.locator('#cbOv .cbmod [data-cb=swap]').click()
            elif stt == 'set': pg.locator('#cbOv .cbhand .cbc').first.click(); pg.wait_for_timeout(60); pg.locator('#cbOv .cbmod [data-cb=set]').click()
            else: pg.wait_for_timeout(120)
        v = pg.evaluate(V)
        check(done and first == [5, 7, 7, 16] and v['phase'] == 'end' and v['turns'] == 5 and v['res'] in ('win', 'lose', 'draw') and len(v['discard']) >= 10 and len([d for d in v['discard'] if d['why'] == 't']) == 10,
              f'コンピュータと さいごまで 対戦できる（ふつうの 形：5ターン・手札 7まい ずつ・山札 16 {first}。{v["res"]} {v["my"]["wins"]}－{v["op"]["wins"]}・捨て札 {len(v["discard"])}まい）')
        pg.wait_for_function("() => { const g = document.querySelector('#cbOv .cbend .gift'); return g && g.textContent.length > 3; }", timeout=30000)
        pg.locator('#cbOv .cbend [data-cb=menu]').click(); pg.wait_for_timeout(120)

        print('■ 部屋：2つの 画面（ホスト・ゲスト）で 対戦')
        gp = ctx.new_page(); gerrs = []; gp.on('pageerror', lambda e: gerrs.append(str(e)))
        gp.goto(APP); gp.wait_for_timeout(1300); gate(gp); gp.wait_for_timeout(600); open_cb(gp)
        pg.evaluate("() => { CBApp._opt = { hands: [['k', '1', '2', '6', '6'], ['m', '3', '4', '5', '7']], turns: 3 }; }")
        pg.evaluate("() => { CBApp._t.state.coin = 10; }"); gp.evaluate("() => { CBApp._t.state.coin = 2; }")      # 2つの 画面は 保存の 場所が 同じ → 数は 画面の 中で 決める（読み直さない）
        c0 = pg.evaluate("() => window.__room.calls.length")
        pg.locator('#cbOv .cbmenu [data-cb=host]').click(); pg.wait_for_timeout(300)
        STK = """() => { const r = document.querySelector('#cbOv .cbroom'), q = s => r.querySelector(s); if (!q('[data-cb=stkgo]')) return null;
          return { chips: [...r.querySelectorAll('[data-cb=stke]')].map(b => b.textContent + (b.classList.contains('on') ? '*' : '')).join(','), w: q('.cbstp b').textContent, minus: q('[data-cb=stkw][data-d="-1"]').disabled, plus: q('[data-cb=stkw][data-d="1"]').disabled,
            go: q('[data-cb=stkgo]').textContent, have: q('.cbcoinl').textContent, calls: window.__room.calls.length, h2: q('h2').textContent }; }"""
        k0 = pg.evaluate(STK)
        check(k0 and k0['h2'] == '部屋を 作る' and k0['chips'] == '0*,1,2,3,5,10' and k0['w'] == '0枚' and k0['minus'] and k0['plus'] and k0['go'] == 'コインなしで 部屋を 作る' and '持って いる バトルコイン 10枚' in k0['have'] and k0['calls'] == c0,
              f'バトルコインを 持って いる 人が「部屋を 作る」→ 先に 参加コインを 決める（えらべるのは 持って いる 数 まで：{k0 and k0["chips"]}・まだ 部屋は 作らない）（第4.179版）')
        shot(pg, 'cb_room_stake')
        pg.locator('#cbOv .cbroom [data-cb=stke][data-n="3"]').click(); k1 = pg.evaluate(STK)
        pg.locator('#cbOv .cbroom [data-cb=stkw][data-d="-1"]').click(); k2 = pg.evaluate(STK)
        for _ in range(3): pg.locator('#cbOv .cbroom [data-cb=stkw][data-d="-1"]').click(force=True)
        k3 = pg.evaluate(STK)
        for _ in range(5): pg.locator('#cbOv .cbroom [data-cb=stkw][data-d="1"]').click(force=True)
        k4 = pg.evaluate(STK)
        pg.locator('#cbOv .cbroom [data-cb=stke][data-n="10"]').click(); k5 = pg.evaluate(STK)
        check(k1['chips'] == '0,1,2,3*,5,10' and k1['w'] == '6枚' and k1['plus'] and not k1['minus'] and k1['go'] == '参加 3枚・勝者 6枚で 部屋を 作る' and k2['w'] == '5枚' and not k2['plus']
              and k3['w'] == '3枚' and k3['minus'] and k4['w'] == '6枚' and k4['plus'] and k5['w'] == '20枚' and k5['go'] == '参加 10枚・勝者 20枚で 部屋を 作る',
              f'参加コイン 3 → 勝者の 獲得コインは 2倍の 6枚から・−で へらせる（参加コインより 少なく ならない：3枚）・＋は 2倍 まで（6枚）・参加 10 → 勝者 20（{[k["w"] for k in (k1, k2, k3, k4, k5)]}）')
        pg.locator('#cbOv .cbroom [data-cb=stke][data-n="0"]').click()
        check(pg.evaluate(STK)['go'] == 'コインなしで 部屋を 作る', '参加コイン 0 → コインなしの 部屋（前の 版と 同じ）')
        pg.locator('#cbOv .cbroom [data-cb=stkgo]').click(); pg.wait_for_timeout(300)
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
        check(pg.evaluate(V)['phase'] == 'eff' and asked(pg)[0] == '6 の 効果を 使う？' and 'ともだちが 効果を 使うか えらんで いるよ' in gp.evaluate(MSG) and acts(gp) == [] and gp.evaluate(SLOT) == 'b 3:セット ずみ'
              and any(s.startswith('ban:効果タイム') and 'カードの 効果を 使うか えらんでね' in s for s in said(pg)) and any(s.startswith('ban:効果タイム') and 'ともだちが 効果を 使うか えらぶよ' in s for s in said(gp)) and not pg.evaluate("() => window.__seen.length") and not gp.evaluate("() => window.__seen.length"),
              'ホストも セットした → 2人の 画面に「効果タイム」：ホスト（6 が 2まい）は「6 の 効果を 使う？」・ゲストは 待つ（オープンは まだ）')
        pg.locator('#cbOv [data-cb=effyes]').click(); pg.wait_for_timeout(80); pg.locator('#cbOv .cbmod .pick .cbc').last.click(); idle(pg); idle(gp)
        check(any('勝ち！' in s for s in pg.evaluate("() => window.__seen")) and any('負け…' in s for s in gp.evaluate("() => window.__seen")) and pg.evaluate(V)['turn'] == 2 and pg.evaluate(V)['pend']['mine'] and asked(pg)[0] == '神様馬の 効果を 使う？'
              and 'ともだちが 神様馬の 効果を 使うか えらんで いるよ' in gp.evaluate(MSG) and gp.locator('#cbOv .cbohand .cbc img[src="cb_s6.webp"]').count() == 2 and gp.locator('#cbOv .cbhand .cbc .eye').count() == 1 and any('あなたの 手札を 1まい 見たよ' in s for s in said(gp)),
              'ホストが 6 の 効果 → 2人の 画面で オープン（ホスト「勝ち！」・ゲスト「負け…」）→ 2ターン目の はじめ：神様馬の 効果は ホストが えらぶ・ゲストは 待つ')
        pg.locator('#cbOv [data-cb=kgo]').click(); pg.wait_for_timeout(80); pg.locator('#cbOv .cbmod .pick .cbc').first.click(); idle(pg); idle(gp)
        check(len([c for c in pg.evaluate(V)['op']['hand'] if c['k']]) >= 1 and gp.locator('#cbOv .cbhand .cbc .eye').count() >= 1 and pg.evaluate(V)['turn'] == 2 and gp.evaluate(V)['turn'] == 2 and pg.evaluate(V)['can']['set'] and gp.evaluate(V)['can']['set'], 'ホストが ゲストの 手札を 1まい 見た → ゲストの その カードに 目の しるし・2人とも 2ターン目の セットへ')
        gp.locator('#cbOv [data-cb=discard]').click(); gp.wait_for_timeout(80)
        gd = gp.evaluate("() => [...document.querySelectorAll('#cbOv .cbmod .cbdl .row[data-dt]')].map(r => r.querySelector('b').textContent + '|' + [...r.querySelectorAll('.pr')].map(p => p.querySelector('span').textContent + '=' + [...p.querySelectorAll('img')].map(i => i.getAttribute('src').replace('cb_s', '').replace('.webp', '')).join('')).join('|'))")
        check(gd == ['ターン 1|あなた=3|ともだち=k'], f'ゲストの 捨て札の 窓：自分から 見た 形（{gd}）')
        gp.locator('#cbOv .cbmod [data-cb=modx]').click(); gp.wait_for_timeout(60)
        def step(q):
            idle(q)
            stt = q.evaluate("() => { const v = CBApp._t.view; return CBApp._t.ended ? 'end' : !v ? 'none' : v.pend && v.pend.mine ? v.pend.type : v.can.eff ? 'eff' : v.can.set ? 'set' : 'wait'; }")
            if stt in ('k', 'm'): q.locator(f'#cbOv [data-cb={stt}skip]').click()
            elif stt == 'rev': q.locator('#cbOv [data-cb=revno]').first.click()
            elif stt == 'eff': q.locator('#cbOv [data-cb=effno]').click()
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
        pg.locator('#cbOv .cbmenu [data-cb=host]').click(); pg.wait_for_timeout(150); pg.locator('#cbOv .cbroom [data-cb=stkgo]').click()      # バトルコインを 持って いる：コインなしで 作る
        pg.wait_for_function("() => /部屋を 作れなかったよ/.test(document.querySelector('#cbOv .cbroom').textContent)", timeout=10000)
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

        print('■ 部屋：バトルコイン（参加コイン・勝者の 獲得コイン）（第4.179版・まさちゃん 16:18「お友達との部屋を作成する場合は、バトルコインで参加枚数を指定する・勝者獲得コインは、参加枚数の2倍まで」）')
        COINS = "() => [CBApp._t.state.coin, CBApp._t.state.stake ? CBApp._t.state.stake.e + '/' + CBApp._t.state.stake.w : null]"
        def make_room(e, w=None):
            pg.locator('#cbOv .cbmenu [data-cb=host]').click(); pg.wait_for_timeout(200)
            pg.locator(f'#cbOv .cbroom [data-cb=stke][data-n="{e}"]').click()
            if w is not None:
                while pg.evaluate("() => parseInt(document.querySelector('#cbOv .cbroom .cbstp b').textContent)") > w: pg.locator('#cbOv .cbroom [data-cb=stkw][data-d="-1"]').click()
            pg.locator('#cbOv .cbroom [data-cb=stkgo]').click(); pg.wait_for_timeout(300)
            return pg.evaluate("() => document.querySelector('#cbOv .cbroom .num').textContent")
        def join_room(num):
            gp.locator('#cbOv .cbmenu [data-cb=join]').click(); gp.wait_for_timeout(150)
            for d in num: gp.locator(f'#cbOv .cbkeys [data-key="{d}"]').click()
            gp.locator('#cbOv .cbkeys [data-key=go]').click()
            gp.wait_for_function("() => CBApp._t.screen === 'game' && document.querySelector('#cbOv .cbmod.cbjoin')", timeout=30000); gp.wait_for_timeout(150)
        JOINM = "() => { const m = document.querySelector('#cbOv .cbmod.cbjoin'); return m ? { t: m.textContent, btns: [...m.querySelectorAll('.cbb')].map(b => b.textContent.trim()), coin: !!m.querySelector('img[src=\"cb_coin.webp\"]') } : null; }"
        pg.evaluate("() => { CBApp._t.state.coin = 10; CBApp._opt = { hands: [['1', '2', '3', '6', '7'], ['2', '3', '6', '7', '7']], turns: 3 }; }"); gp.evaluate("() => { CBApp._t.state.coin = 2; }")
        num = make_room(3)
        rs = pg.evaluate("() => ({ t: document.querySelector('#cbOv .cbroom .cbstkl').textContent, last: window.__room.calls[window.__room.calls.length - 1] })")
        check(rs['t'] == '参加コイン 3枚・勝者 6枚' and rs['last'] == 'host:' + num and pg.evaluate(COINS) == [10, None], f'参加 3枚・勝者 6枚の 部屋を 作った：部屋番号の 下に 決まり（{rs["t"]}）・まだ コインは 出さない')
        join_room(num)
        jm = gp.evaluate(JOINM); hm = pg.evaluate(MSG)
        check(jm and 'この 部屋の 決まり' in jm['t'] and '参加コイン 3枚→勝者 6枚' in jm['t'] and 'あなたの バトルコイン 2枚' in jm['t'] and 'あと 1枚 足りない ので、この 部屋には 入れないよ' in jm['t'] and jm['btns'] == ['メニューへ'] and jm['coin']
              and pg.evaluate("() => CBApp._t.screen") == 'game' and hm == 'ともだちが 参加するか えらんで いるよ…' and pg.evaluate("() => CBApp._t.view") is None,
              f'入る 人の バトルコインが 足りない（2枚）：「この 部屋の 決まり」・「あと 1枚 足りない ので、この 部屋には 入れないよ」（ボタンは メニューへ だけ）・作った 人は「ともだちが 参加するか えらんで いるよ…」（まだ 配らない）')
        shot(gp, 'cb_join_short')
        gp.locator('#cbOv .cbjoin [data-cb=joinno]').click(); gp.wait_for_timeout(200)
        pg.wait_for_function("() => CBApp._t.modOn() && /部屋を 出たよ/.test(document.querySelector('#cbOv .cbmod').textContent)", timeout=20000)
        check(gp.evaluate("() => CBApp._t.screen") == 'menu' and gp.evaluate(COINS) == [2, None] and pg.evaluate(COINS) == [10, None] and '勝ち負けに 数えないよ' not in pg.locator('#cbOv .cbmod').inner_text(),
              '入らずに メニューへ → 作った 人に「ともだちが 部屋を 出たよ」（2人とも コインは かわらない）')
        pg.locator('#cbOv .cbmod [data-cb=menu]').click(); pg.wait_for_timeout(200)
        # 足りる：参加する → 2人とも 出す → 勝った 人が 6枚
        gp.evaluate("() => { CBApp._t.state.coin = 5; }")
        num = make_room(3); join_room(num)
        jm = gp.evaluate(JOINM)
        check(jm and 'あなたの バトルコイン 5枚' in jm['t'] and '足りない' not in jm['t'] and jm['btns'] == ['やめる', '参加する'] and '同点は もどる・とちゅうで やめると もどらないよ' in jm['t'], f'足りる（5枚）：「やめる」「参加する」（{jm and jm["btns"]}）')
        shot(gp, 'cb_join_ask')
        gp.locator('#cbOv .cbjoin [data-cb=joinyes]').click()
        pg.wait_for_function("() => CBApp._t.screen === 'game' && CBApp._t.view && CBApp._t.idle", timeout=30000); gp.wait_for_function("() => CBApp._t.view && CBApp._t.idle", timeout=30000)
        tl = [q.locator('#cbOv .cbturn').inner_text().replace('\n', '') for q in (pg, gp)]
        check(pg.evaluate(COINS) == [7, '3/6'] and gp.evaluate(COINS) == [2, '3/6'] and all('勝者 6枚' in t for t in tl) and pg.evaluate(V)['turns'] == 3,
              f'「参加する」→ 配る → 2人とも 参加コイン 3枚を 出す（作った 人 10 → 7・入った 人 5 → 2）・ターンの 字の よこに「勝者 6枚」（{tl}）')
        shot(pg, 'cb_room_coin_game')
        pg.locator('#cbOv .cbtop [data-cb=quit]').click(); pg.wait_for_timeout(80)
        check('参加コイン 3枚も もどらないよ' in pg.locator('#cbOv .cbmod').inner_text(), '「やめる」の 窓：参加コインも もどらない ことを 出す')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        for mine, his in (('1', '2'), ('2', '3'), ('3', '6')):
            idle(pg); idle(gp); play(pg, mine); idle(gp); play(gp, his); idle(pg); idle(gp)
        for q in (pg, gp): q.wait_for_function("() => { const g = document.querySelector('#cbOv .cbend .gift'); return CBApp._t.ended && g && g.textContent.length > 3; }", timeout=30000)
        eh = pg.evaluate("() => ({ g: document.querySelector('#cbOv .cbend .gift').textContent, again: document.querySelector('#cbOv .cbend [data-cb=again]').disabled })")
        eg = gp.evaluate("() => ({ g: document.querySelector('#cbOv .cbend .gift').textContent, g2: document.querySelector('#cbOv .cbend .gift2').textContent, again: document.querySelector('#cbOv .cbend [data-cb=again]').disabled, h: document.querySelector('#cbOv .cbend h3').textContent })")
        check(pg.evaluate(V)['res'] == 'win' and 'バトルコイン ＋6枚（いま 13枚）' in eh['g'] and pg.evaluate(COINS) == [13, None] and not eh['again'],
              f'作った 人の 勝ち（3 － 0）：勝者の 獲得コイン 6枚（7 → 13枚）（{eh["g"]}）')
        check(eg['h'] == 'あなたの 負け…' and '参加コイン 3枚は もどらないよ（いま 2枚）' in eg['g'] and gp.evaluate(COINS) == [2, None] and eg['again'] and eg['g2'] == 'バトルコインが 足りない ので、もう 1回は できないよ' and gp.evaluate("() => { const g = document.querySelector('#cbOv .cbend .gift2'); return Math.round(g.getBoundingClientRect().height) <= 20; }"),
              f'入った 人の 負け：参加コインは もどらない（いま 2枚）・バトルコインが 足りない ので「もう 1回」は 押せない（{eg["g2"]}）')
        shot(gp, 'cb_room_coin_lose')
        gp.locator('#cbOv .cbend [data-cb=menu]').click(); gp.wait_for_timeout(200)
        pg.wait_for_function("() => CBApp._t.modOn() && /部屋を 出たよ/.test(document.querySelector('#cbOv .cbmod').textContent)", timeout=20000)
        check(pg.evaluate(COINS) == [13, None] and 'バトルコイン' not in pg.locator('#cbOv .cbmod').inner_text(), '終わった あとに 相手が 出ても、コインは かわらない')
        pg.locator('#cbOv .cbmod [data-cb=menu]').click(); pg.wait_for_timeout(200)
        # とちゅうで やめた 人の 参加コインは もどらない・相手は 獲得コインを もらう
        gp.evaluate("() => { CBApp._t.state.coin = 4; }")
        num = make_room(1); join_room(num); gp.locator('#cbOv .cbjoin [data-cb=joinyes]').click()
        pg.wait_for_function("() => CBApp._t.view && CBApp._t.idle", timeout=30000); gp.wait_for_function("() => CBApp._t.view && CBApp._t.idle", timeout=30000)
        check(pg.evaluate(COINS) == [12, '1/2'] and gp.evaluate(COINS) == [3, '1/2'], '参加 1枚・勝者 2枚の 部屋：2人とも 1枚 出した（13 → 12・4 → 3）')
        lose0 = gp.evaluate("() => CBApp._t.state.lose")
        gp.locator('#cbOv .cbtop [data-cb=quit]').click(); gp.wait_for_timeout(80)
        check('参加コイン 1枚も もどらないよ' in gp.locator('#cbOv .cbmod').inner_text(), '入った 人の「やめる」の 窓にも 出る')
        gp.locator('#cbOv .cbmod [data-cb=quitgo]').click(); gp.wait_for_timeout(200)
        pg.wait_for_function("() => CBApp._t.modOn() && /部屋を 出たよ/.test(document.querySelector('#cbOv .cbmod').textContent)", timeout=20000)
        mt = pg.locator('#cbOv .cbmod').inner_text()
        check(gp.evaluate(COINS) == [3, None] and gp.evaluate("() => CBApp._t.state.lose") == lose0 + 1 and pg.evaluate(COINS) == [14, None] and 'ともだちが とちゅうで やめた ので、バトルコイン 2枚を もらったよ' in mt and '勝ち負けに 数えないよ' in mt,
              f'とちゅうで やめた 人：参加コインは もどらない（3枚の まま・負けに 数える）・相手は 勝者の 獲得コイン 2枚（12 → 14）（{mt[:80]!r}）')
        pg.locator('#cbOv .cbmod [data-cb=menu]').click(); pg.wait_for_timeout(200)
        # つながりが 切れた：2人とも 参加コインが もどる
        num = make_room(1); join_room(num); gp.locator('#cbOv .cbjoin [data-cb=joinyes]').click()
        pg.wait_for_function("() => CBApp._t.view && CBApp._t.idle", timeout=30000); gp.wait_for_function("() => CBApp._t.view && CBApp._t.idle", timeout=30000)
        mid = [pg.evaluate(COINS), gp.evaluate(COINS)]
        for q in (pg, gp): q.evaluate("() => window.__nativeEvent('room', { ev: 'state', state: 'idle' })")
        for q in (pg, gp): q.wait_for_function("() => CBApp._t.modOn() && /つながりが 切れたよ/.test(document.querySelector('#cbOv .cbmod').textContent)", timeout=20000)
        check(mid == [[13, '1/2'], [2, '1/2']] and pg.evaluate(COINS) == [14, None] and gp.evaluate(COINS) == [3, None] and all('参加コイン 1枚は もどったよ' in q.locator('#cbOv .cbmod').inner_text() for q in (pg, gp)),
              f'つながりが 切れた：2人とも 参加コインが もどる（{mid} → 14・3）')
        for q in (pg, gp): q.locator('#cbOv .cbmod [data-cb=menu]').click(); q.wait_for_timeout(150)
        # 同点は もどる・負けは もどらない・勝ちは 獲得コイン（数える 所 だけ）／とちゅうで アプリが 閉じた ときの 参加コインは もどらない（つぎに 開いた とき 知らせる）
        r3 = pg.evaluate("""async () => { const T = CBApp._t, out = []; for (const res of ['draw', 'lose', 'win']) { const c0 = T.state.coin; T.state.stake = { e: 2, w: 4 }; const r = await T.settle(res); out.push([res, r.pot.add, T.state.coin - c0, T.state.stake]); } return out; }""")
        check(r3 == [['draw', 2, 2, None], ['lose', 0, 0, None], ['win', 4, 4, None]], f'参加 2・勝者 4：同点＝2枚 もどる・負け＝0・勝ち＝4枚（{r3}）')
        pg.evaluate("() => { const T = CBApp._t; T.state.stake = { e: 5, w: 10 }; T.save(); T.load(); }")
        c5 = pg.evaluate(COINS); pg.evaluate("() => CBApp._t.menu()"); pg.wait_for_timeout(200); tt = pg.evaluate(TOAST)
        check(c5[1] is None and '前の 対戦が とちゅうで 終わった ので、' in tt and '参加コイン 5枚は もどらなかったよ' in tt, f'参加コインを 出した まま アプリが 閉じた → つぎに 開いた とき「参加コイン 5枚は もどらなかったよ」（{tt!r}）')
        print('■ デザインカスタム（第4.182版・まさちゃん 20:00「…背面カスタム1枚 バトルコイン300枚」・20:09「…デザイン一枚解放、バトルコイン300枚 神様馬カードと幻の馬カード500枚」）')
        pg.evaluate("() => { const T = CBApp._t; T.state.coin = 0; T.state.backs = []; T.state.faces = []; T.state.back = ''; T.state.face = {}; T.save(); T.menu(); }"); pg.wait_for_timeout(200)
        pg.locator('#cbOv .cbmenu [data-cb=dz]').click(); pg.wait_for_timeout(250)
        DZ = """() => { const s = document.querySelector('#cbOv .cbdz'); return { scr: CBApp._t.screen, coin: s.querySelector('.cbcoinl').textContent.replace(/\\s+/g, ' ').trim(), tab: [...s.querySelectorAll('.tabs button')].map(b => b.textContent + (b.classList.contains('on') ? '*' : '')),
          h4: [...s.querySelectorAll('h4')].map(h => h.textContent.replace(/\\s+/g, ' ').trim()),
          tiles: [...s.querySelectorAll('.dzt')].map(t => (t.dataset.ck || '-') + ':' + (t.dataset.id || 'base') + ':' + t.querySelector(':scope > img').getAttribute('src') + ':' + t.querySelector('em').textContent + (t.classList.contains('on') ? '*' : '') + (t.classList.contains('lk') ? '!' : '')) }; }"""
        MZ = """() => { const m = document.querySelector('#cbOv .cbmod.cbdzm'); if (!m) return null; return { h: m.querySelector('h3').textContent, img: (m.querySelector('.big img') || {}).getAttribute ? m.querySelector('.big img').getAttribute('src') : '', btns: [...m.querySelectorAll('.cbb')].map(b => b.textContent.trim() + (b.disabled ? '!' : '')), need: (m.querySelector('.cbneed') || {}).textContent || '', t: m.textContent.replace(/\\s+/g, ' ').trim() }; }"""
        d0 = pg.evaluate(DZ)
        check(d0['scr'] == 'dz' and d0['coin'] == 'バトルコイン 0枚' and d0['tab'] == ['カードの おもて*', 'カードの うら'] and len(d0['h4']) == 9 and d0['h4'][0] == '神様馬1つ 500枚' and d0['h4'][1] == '幻の馬1つ 500枚' and d0['h4'][2] == '1 の カード1つ 300枚'
              and len(d0['tiles']) == 27 and d0['tiles'][0] == 'k:base:cb_sk.webp:使って いる*' and d0['tiles'][1] == 'k:ka:cb_fc_ka_s.webp:500枚!' and d0['tiles'][-1] == '7:7b:cb_fc_7b_s.webp:300枚!'
              and sum(1 for t in d0['tiles'] if t.endswith('300枚!')) == 14 and sum(1 for t in d0['tiles'] if t.endswith('500枚!')) == 4 and sum(1 for t in d0['tiles'] if t.endswith('使って いる*')) == 9,
              f'メニューの「デザインカスタム」→「カードの おもて」：9種類（神様馬・幻の馬は 1つ 500枚・ほかは 300枚）・いつもの 9 ＋ べつの デザイン 18（{len(d0["tiles"])}こ）')
        shot(pg, 'cb_dz_faces')
        pg.locator('#cbOv .cbdz .dzt[data-id="ka"]').click(); pg.wait_for_timeout(150); z1 = pg.evaluate(MZ)
        check(z1 and z1['h'] == '朱の鳥居神様馬の おもて' and z1['img'] == 'cb_fc_ka_c.webp' and z1['btns'] == ['バトルコイン 500枚で 解放!', 'もどる'] and z1['need'] == 'あと 500枚 たりないよ（コンピュータに 勝つと 1枚・5連勝 ごとに 5枚）',
              f'コインが 足りない：大きい 絵・「バトルコイン 500枚で 解放」は 押せない・あと 500枚（{z1 and z1["btns"]}）')
        pg.locator('#cbOv .cbmod [data-cb=dzback]').click(); pg.wait_for_timeout(80)
        pg.evaluate("() => { CBApp._t.state.coin = 800; }"); pg.locator('#cbOv .cbdz [data-cb=dztab][data-t=f]').click(); pg.wait_for_timeout(150)
        pg.locator('#cbOv .cbdz .dzt[data-id="ka"]').click(); pg.wait_for_timeout(150); z2 = pg.evaluate(MZ)
        pg.locator('#cbOv .cbmod [data-cb=dzopen]').click(); pg.wait_for_timeout(150); z3 = pg.evaluate(MZ)
        check(z2['btns'] == ['バトルコイン 500枚で 解放', 'もどる'] and z3['h'] == '解放する？' and '『朱の鳥居』（神様馬の おもて）を 解放するよ' in z3['t'] and '800枚→のこり 300枚' in z3['t'] and z3['btns'] == ['やめる', '解放する'],
              f'800枚 ある：「解放」→ たしかめる 窓（800枚 → のこり 300枚・やめる／解放する）（{z3["t"]}）')
        shot(pg, 'cb_dz_ask')
        pg.evaluate("() => { CBApp._guard = 1e9; }"); pg.locator('#cbOv .cbmod [data-cb=dzgo]').click(); pg.wait_for_timeout(100); g0 = pg.evaluate("() => [CBApp._t.state.coin, CBApp._t.state.faces.slice()]")
        pg.evaluate("() => { CBApp._guard = 0; }"); pg.locator('#cbOv .cbmod [data-cb=dzgo]').click(); pg.wait_for_timeout(200)
        d1 = pg.evaluate(DZ); st1 = pg.evaluate("() => { const s = CBApp._t.state, ls = JSON.parse(localStorage.getItem('tengel.cb')); return [s.coin, s.faces, s.face, ls.coin, ls.faces, ls.face]; }"); tt = pg.evaluate(TOAST)
        check(g0 == [800, []] and st1 == [300, ['ka'], {'k': 'ka'}, 300, ['ka'], {'k': 'ka'}] and d1['coin'] == 'バトルコイン 300枚' and d1['tiles'][0] == 'k:base:cb_sk.webp:持って いる' and d1['tiles'][1] == 'k:ka:cb_fc_ka_s.webp:使って いる*'
              and not pg.evaluate("() => CBApp._t.modOn()") and '『朱の鳥居』を 解放したよ！' in tt,
              f'「解放する」：窓が 出て すぐは 受けつけない → 500枚 へって（800 → 300）解放・すぐ その デザインに・おぼえる（{st1}）')
        pg.locator('#cbOv .cbdz [data-cb=dztab][data-t=b]').click(); pg.wait_for_timeout(150); d2 = pg.evaluate(DZ)
        check(d2['tab'] == ['カードの おもて', 'カードの うら*'] and d2['h4'] == ['カードの うら1つ 300枚'] and len(d2['tiles']) == 8 and d2['tiles'][0] == '-:base:cb_sb.webp:使って いる*' and all(t.endswith('300枚!') for t in d2['tiles'][1:])
              and [t.split(':')[1] for t in d2['tiles'][1:]] == ['sky', 'star', 'ice', 'wa', 'ori', 'crown', 'heart'],
              f'「カードの うら」：いつもの ＋ 7種（1つ 300枚）（{[t.split(":")[1] for t in d2["tiles"]]}）')
        shot(pg, 'cb_dz_backs')
        pg.locator('#cbOv .cbdz .dzt[data-id="sky"]').click(); pg.wait_for_timeout(120); pg.locator('#cbOv .cbmod [data-cb=dzopen]').click(); pg.wait_for_timeout(120); pg.locator('#cbOv .cbmod [data-cb=dzgo]').click(); pg.wait_for_timeout(200)
        d3 = pg.evaluate(DZ)
        pg.locator('#cbOv .cbdz .dzt[data-id="star"]').click(); pg.wait_for_timeout(120); z4 = pg.evaluate(MZ); pg.locator('#cbOv .cbmod [data-cb=dzback]').click(); pg.wait_for_timeout(80)
        check(d3['coin'] == 'バトルコイン 0枚' and d3['tiles'][1] == '-:sky:cb_bk_sky_s.webp:使って いる*' and d3['tiles'][0] == '-:base:cb_sb.webp:持って いる' and z4['btns'] == ['バトルコイン 300枚で 解放!', 'もどる'] and 'あと 300枚 たりないよ' in z4['need']
              and pg.evaluate("() => [CBApp._t.state.backs, CBApp._t.state.back]") == [['sky'], 'sky'],
              f'うら『天馬の光』を 300枚で 解放（300 → 0）・ほかは あと 300枚（{d3["coin"]}）')
        pg.locator('#cbOv .cbdz [data-cb=dzx]').click(); pg.wait_for_timeout(150)
        check(pg.evaluate("() => CBApp._t.screen") == 'menu' and 'バトルコイン 0枚' in pg.evaluate("() => document.querySelector('#cbOv .cbmenu .cbcoinl').textContent"), '「← もどる」→ メニュー（コインの 数も 0枚）')
        start(pg, 'k1234', '15677')
        IM = """() => ({ deck: document.querySelector('#cbOv .cbdeck img').getAttribute('src'), op: [...document.querySelectorAll('#cbOv .cbohand img')].map(i => i.getAttribute('src')), my: [...document.querySelectorAll('#cbOv .cbhand .cbc')].map(c => c.dataset.ck + '=' + c.querySelector('img').getAttribute('src')) })"""
        im = pg.evaluate(IM)
        check(im['deck'] == 'cb_bk_sky_d.webp' and set(im['op']) == {'cb_bk_sky_s.webp'} and 'k=cb_fc_ka_s.webp' in im['my'] and '1=cb_s1.webp' in im['my'] and not any('cb_sk.webp' in x for x in im['my']),
              f'対戦：山札と 相手の 手札は えらんだ うら『天馬の光』・神様馬は えらんだ おもて『朱の鳥居』・ほかは いつもの（{im["deck"]}・{im["my"]}）')
        shot(pg, 'cb_dz_game')
        pg.evaluate("() => { window.__seen = []; }")
        pg.locator('#cbOv .cbhand .cbc[data-ck="k"]').click(); pg.wait_for_timeout(80); pg.locator('#cbOv .cbmod [data-cb=set]').click(); idle(pg)
        opp(pg, {'t': 'set', 'k': 1})
        seen = pg.evaluate("() => window.__seen"); dt = pg.evaluate("() => { const d = document.querySelector('#cbOv .cbdis img'); return d ? d.getAttribute('src') : null; }")
        check(any('勝ち！' in x and 'cb_fc_ka_c.webp,cb_c1.webp' in x for x in seen) and pg.evaluate(V)['my']['wins'] == 1, f'めくった とき：神様馬は えらんだ おもての 大きい 絵（{seen[-1] if seen else None}）')
        pg.evaluate("() => CBApp._t.menu()"); pg.wait_for_timeout(150)
        pg.locator('#cbOv .cbmenu [data-cb=dz]').click(); pg.wait_for_timeout(150)
        pg.locator('#cbOv .cbdz .dzt[data-ck="k"][data-id=""]').click(); pg.wait_for_timeout(120); z5 = pg.evaluate(MZ)
        pg.locator('#cbOv .cbmod [data-cb=dzuse]').click(); pg.wait_for_timeout(150)
        st2 = pg.evaluate("() => [CBApp._t.state.coin, CBApp._t.state.face, CBApp._t.state.faces, JSON.parse(localStorage.getItem('tengel.cb')).face]")
        check(z5['btns'] == ['この デザインを 使う', 'もどる'] and st2 == [0, {}, ['ka'], {}] and pg.evaluate(DZ)['tiles'][0] == 'k:base:cb_sk.webp:使って いる*', f'いつもの に もどす：コインは 使わない・解放した ものは のこる（{st2}）')
        pg.locator('#cbOv .cbdz .dzt[data-id="ka"]').click(); pg.wait_for_timeout(120); z6 = pg.evaluate(MZ); pg.locator('#cbOv .cbmod [data-cb=dzuse]').click(); pg.wait_for_timeout(150)
        check(z6['btns'] == ['この デザインを 使う', 'もどる'] and pg.evaluate("() => CBApp._t.state.face") == {'k': 'ka'}, '解放した デザインは コインなしで また 使える')
        pg.evaluate("() => { const s = JSON.parse(localStorage.getItem('tengel.cb')); s.faces = ['zz', 'ka', 'ka']; s.face = { k: 'kb', '1': 'ka', m: 'ma' }; s.backs = ['sky', 'nope']; s.back = 'ice'; localStorage.setItem('tengel.cb', JSON.stringify(s)); CBApp._t.load(); }")
        st3 = pg.evaluate("() => { const s = CBApp._t.state; return [s.faces, s.face, s.backs, s.back]; }")
        check(st3 == [['ka'], {}, ['sky'], ''], f'おぼえた 中身が おかしい ときは なおす（ない 名前・解放して いない もの・ちがう 種類は すてる）（{st3}）')
        pg.evaluate("() => { const T = CBApp._t; T.state.backs = []; T.state.faces = []; T.state.back = ''; T.state.face = {}; T.save(); T.menu(); }")
        check(not errs and not gerrs, f'エラー なし {errs[:3]} {gerrs[:3]}')
        if HAVE:
            miss = sorted(set(f for f in reqs if f.startswith('cb_') and f != 'cb_bundle.js' and f not in CBF))
            used = sorted(set(f for f in reqs if f in CBF))
            check(not miss and all(f in used for f in ['cb_board.webp', 'cb_deck.webp', 'cb_logo.webp', 'cb_icon.webp', 'cb_sb.webp', 'cb_s1.webp', 'cb_c1.webp', 'cb_ck.webp', 'cb_coin.webp', 'cb_bgm.m4a']), f'読んだ 絵と 音は ぜんぶ アプリに 入れる ファイル（ない 名前 {miss}・読んだ {len(used)}こ）')
finally:
    srv.terminate()
print('\n' + ('全部 OK' if not fails else f'NG {len(fails)}こ：' + ' / '.join(fails)))
sys.exit(1 if fails else 0)
