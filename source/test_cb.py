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
#   第4.188版（まさちゃん 2026/11/17 11:22）：バトルコイン（コンピュータに 勝つと 2枚・3連勝 ごとに ＋6枚・5連勝 ごとに ＋10枚・さいごの 画面の「🔥 ○連勝 ボーナス！」の 札・ログインボーナスで 毎日 2枚〈7日目 ＋10枚〉を 受け取る）
#     ・入れない（足りない）・参加する → 2人とも 出す → 勝者が もらう・同点は もどる・とちゅうで やめた 人は もどらない（相手が もらう）・つながりが 切れたら もどる
#   第4.183版（まさちゃん 2026/11/16 20:51・20:53）：ミッション（コンピュータ／友だちバトルで 連続勝利 → バトルコイン・毎月 リセット）・友だちバトルは それぞれの デザイン
#   第4.182版（まさちゃん 2026/11/16 20:00・20:09）：デザインカスタム（カードの おもて 18種・うら 7種：バトルコインで 解放＝おもて 300枚・神様馬／幻の馬 500枚・うら 300枚）
#   第4.185版（まさちゃん 2026/11/16 22:39・22:45）：7 の 4まい 公開で 強さ 逆転（効果タイムで 聞く・見せる 窓・捨て札・「強さ 逆転中」・その 対戦が 終わる まで・コンピュータも 使う）・7 の 新しい 絵と カスタムの 名前
#     （23:04）設定の「エフェクト」を なくした（BGM・効果音 だけ・前の 版の fx は すてる）／（23:06）効果を 使った ときの 札（だれが・どの 効果・何を する）／
#     （23:20）プレイボード 7種（デザインカスタムの 3つ目の タブ・1つ 300枚・対戦の ボードの 絵・いつもの 以外は 火の あかりの ゆれ なし）
#   第4.186版（まさちゃん 2026/11/17 00:52）：プレイボード 4つを 新しい 絵に（山札の 札が 左へ 5.86% → この 4つの とき だけ 山札も 左へ：.cbboard.dl）
#   第4.187版（まさちゃん 2026/11/17 09:39）：7 の 4まい 公開は セットの 前（聞く 窓・使わない の あとの 下の ボタン）・セットは いつも ふせて（自分の 場の カードは うら ＋ しるし・相手が 7 を ふせても 見え方は 同じ）
#   第4.188版（まさちゃん 2026/11/17 11:05・11:16）：効果の 順 6 → 7 → 3 → 5 → 4（聞く 順も・4 は いちばん あと）・5 で 捨てる カードは 7・3 の 効果の 分を のこす・相手の 5 の 効果で 来た カードでも 逆転勝利
#   第4.189版（まさちゃん 2026/11/17 15:00・15:18・15:39）：カードパック（1パック 112枚・5まい＝ノーマル 4まい ＋ くじ 1まい：0〜229 の 番号・コイン／カード／記録を いっしょに 保存・2回 しない・記録から もう 1回 見る・パックの 絵）。おもては パックで 集める（コインで 解放は うら・ボード だけ）
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
      W('.cbban', 'ban'); W('.cbtoast', 'toast'); W('.cbuse', 'use'); }""")      # 第4.185版：効果を 使った ときの 札（use）


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
SLOT = "() => ['op', 'my'].map(s => { const e = document.querySelector('#cbOv .cbslot.' + s), i = e.querySelector('img'), t = e.querySelector('.tag'), mk = e.querySelector('.mk'); return (i ? i.getAttribute('src').replace('cb_s', '').replace('.webp', '') : '-') + (mk ? '[' + mk.textContent + ']' : '') + (t ? ':' + t.textContent : ''); }).join(' ')"      # 第4.187版：自分の ふせた カード＝うら ＋ しるし［数字］
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
        check(m['scr'] == 'menu' and m['h1'].replace('\n', '').replace(' ', '') == 'TENGERカードバトル' and m['btn'] == ['← もどる', 'コンピュータと 対戦', '部屋を 作る友だちと 対戦', '部屋に 入る友だちと 対戦', 'あそび方', '設定BGM・効果音', '🎯ミッション今月 0／14 達成', 'デザインカスタムカードパック・うら・ボード'] and not any(m['dis']),
              f'メニュー：コンピュータと 対戦・部屋を 作る・部屋に 入る・あそび方・設定（第4.178版）・ミッション（第4.183版）・デザインカスタム（第4.182版）（{m["btn"]}）')
        check(m['rec'] == '勝つと お世話トークン 1こ・5連勝 ごとに 3こ' and (not HAVE or m['lg'] == 720), f'ごほうびの 説明（{m["rec"]}）')
        cl = pg.evaluate("() => { const e = document.querySelector('#cbOv .cbmenu .cbcoinl'); return e ? [e.textContent, e.querySelectorAll('img[src=\"cb_coin.webp\"]').length] : null; }")
        check(cl == ['バトルコイン 0枚コンピュータに 勝つと 2枚（3連勝 ＋6枚・5連勝 ＋10枚）毎日の ログインボーナスで 2枚（7日目 ＋10枚）', 1], f'メニューに バトルコイン（第4.179版：コインの 絵・持って いる 数・もらい方 → 第4.188版：勝つと 2枚・3連勝 ＋6・5連勝 ＋10・ログインボーナス）（{cl}）')
        check(reqs.count('cb_bundle.js') == 1 and 'cb_bundle.js' not in reqs[:reqs.index('cb_bundle.js')][:5], '本体（cb_bundle.js）は ボタンを 押した ときに 1回 だけ 読む')
        shot(pg, 'cb_menu')
        pg.locator('#cbOv .cbmenu [data-cb=help]').click(); pg.wait_for_timeout(200)
        ht = pg.locator('#cbOv .cbhelp .bd').inner_text()
        need = ['手札は 7まい。5ターンで 勝負', '5ターン 終わって', '2まいは 使わずに のこるよ', '強い カードの 勝ち', '勝った 数が 多い 人の 勝ち', '神様馬と 幻の馬が いちばん 強い', '1 が いちばん 強くて、7 が いちばん 弱い', '「かぶり」＝どちらも 負け', '4 どうしで 2人とも 4 の 効果を 使った ときは ドロー', '2人とも 4 を 出して、2人とも 効果を 使ったら、打ち消して その ターンは ドロー', '1〜7 が 4まい ずつ・神様馬 1まい・幻の馬 1まい',
                '① セット', 'セットしたら もう 変えられない', '② 効果タイム', '2人とも セットしたら、使える 効果が ある 人に「効果を 使う？」と 聞くよ', '③ オープン', '次の ターンの はじめに、使うか えらぶよ', '効果タイムで 効果が 出る 順番は 6 → 7 → 3 → 5 → 4（聞く 順番も 同じ）', '効果が 出る 順番：① ターンの はじめ（神様馬・幻の馬）→ ② 手札の 効果（7 の 4まい 公開は セットの 前・効果タイムは 6 → 7 → 3）→ ③ セットした カードの 効果（5 → 4：4 は いちばん あと）', '4 の 効果は いちばん あと：相手が 5 の 効果で 山札から ふせた カードも 交換に なるよ', '「使う」「使わない」は 自分で えらべる', '使うか 使わないかは 自分で えらべる',
                '終わった ターンの 捨て札', '効果で 捨てた カード',
                '7：3まい 交換・4まい 公開で 逆転', '【4まい】手札に 7 が 4まい あれば、セットの 前に 4まい 見せて 1まい 捨てると、その 対戦が 終わる まで 数字の 強さが 逆に なるよ', '【4まい】を 使った ターンは【3まい】は 使えない（どちらか 1つ）',
                'ふせて（うらで）出すよ（自分の カードには 数字の しるし・タップで 見られる）', '手札に 7 が 4まい ある ときは、セットの 前に「7 を 4まい 見せて 逆転する？」と 聞くよ', '7 の 4まい 公開（強さ 逆転）は、セットの 前に 使うか えらぶよ（セットしなくて いい）',
                'セットした カードは、前に 見た カードでも うら（4 の 効果で 見せる か、オープン するまで）', '見た カードは オープンまで 手札に ある ように 見えるよ',
                '7 の 効果（4まい 公開）で 強さ 逆転したら、その 対戦が 終わる まで 7 が いちばん 強くて、1 が いちばん 弱い', '6：2まい 見せて 手札を 見る',
                '効果を 使うと、ボードの まん中に だれが・どの 効果を・何を するかの 札が 出るよ（タップすると すぐ 次へ）', '5：2まい 捨てて 山札から セット', 'のこりの ターンの 数より 少なく ならない とき', 'さいごの ターンは、手札が 1まい あれば 使える', '4：見せて 強制交換',
                '3：3まい 見せて 手札を 交換', 'ランダムに えらんだ 1まいを 交換できるよ', '7（3まい 交換）・6・5・4・3 の 効果は', '神様馬：勝ったら 手札を 見る', '幻の馬：勝ったら 手札を 交換', 'お世話トークン 1こ', '5連勝 ごとに 3こ', '部屋番号（4けた）', '近くに いる 友だち',
                'もう 見た カード だけの ときは 使えないよ', 'まだ 見て いない カードが ある とき', 'メニューの「デザインカスタム」で、カードの おもて・うらと プレイボードの デザインを かえられるよ', 'コンピュータと 対戦する ときは、コンピュータの カード（うら・おもて）も あなたが えらんだ デザインに なるよ',
                '友だちと 対戦する ときは、あなたの カードは あなたの デザイン・友だちの カードは 友だちが えらんだ デザインで 出るよ（山札は あなたの うら）',
                'メニューの「ミッション」：コンピュータに 連続勝利・友だちバトルで 連続勝利で バトルコインが もらえるよ', 'コンピュータ：3連勝 30枚・5連勝 60枚・6連勝 90枚・7連勝 120枚・8連勝 150枚・9連勝 200枚・10連勝 300枚',
                '友だちバトル：3連勝 20枚・5連勝 40枚・6連勝 60枚・7連勝 80枚・8連勝 100枚・9連勝 120枚・10連勝 140枚', '毎月 1日に リセット（達成も 連勝も 0 に もどる）', 'コンピュータと 友だちバトルの 連勝は 別に 数えるよ',
                'カードの おもては カードパックで 集めるよ：1パック バトルコイン 112枚・5まい入り（ノーマル 4まい ＋ くじの 1まい）', 'くじの 1まい：レア 2パックに 1まい・超レア 5パックに 1まい（どちらも 神様馬・幻の馬を ふくむ）・神様馬／幻の馬の レア 10パックに 1まい・神様馬／幻の馬の 超レア 23パックに 1まい（どれも 平均。くわしい 確率は カードパックの「出る 確率」）', '新しい カードは 持って いる カードに 入るよ（同じ カードが 出ても、数は ふえないよ）。開けた パックは「パックの 記録」で もう 1回 見られるよ', 'カードの うら 300枚・プレイボード 300枚は バトルコインで 1つずつ 解放できるよ。いつもの デザインは はじめから 使えるよ', '音（設定）', 'BGM・効果音を オン／オフ',
                'プレイボードは、あなたの 画面に 出るよ（友だちと 対戦する ときも、あなたの 画面は あなたが えらんだ ボード）',
                '1：3まい 見せて 逆転勝利', '2：3まい 見せて 逆転勝利', '神様馬・幻の馬に 負けた とき、手札に 1 が 2まい あれば', '1 に 負けた とき、手札に 2 が 2まい あれば', '勝ちに できるよ', '1・2 の 効果（逆転勝利）は、オープンした あと、負けた 人が 使うか えらぶよ',
                '1・2 の「逆転勝利」は、めくった あとに 使うか えらぶよ', '逆転勝利：1 が 3まい あれば 神様馬・幻の馬に、2 が 3まい あれば 1 に 勝てる',
                'バトルコイン', 'コンピュータに 勝つと 2枚 もらえるよ', '連勝すると ボーナス：3連勝 ごとに ＋6枚・5連勝 ごとに ＋10枚（15連勝 など、両方の ときは 両方）', '毎日の ログインボーナスでも 2枚（7日目は ＋10枚）もらえるよ', '買う ことは できない', '参加コイン', '参加コインの 2倍 まで', '同じ 数の 参加コインを 持って いないと 入れない', 'テンゲルから 獲得コインを プレゼントで もらえる',
                '同点は 参加コインが もどる', 'とちゅうで やめると、参加コインは もどらない']
        miss = [x for x in need if x not in ht] + [x for x in ('エフェクト', '光や 動きの 演出') if x in ht]      # 第4.185版：エフェクトの 設定は なくした
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
        check(v['my']['set'] and v['my']['set']['k'] == '1' and pg.evaluate(SLOT) == '- b[1]:ふせて セット' and pg.locator('#cbOv .cbslot.my .cbc').get_attribute('aria-label') == 'あなたが ふせて セットした カード（1）' and pg.evaluate(DOMHAND) == '2367' and 'コンピュータが えらんで いるよ' in pg.evaluate(MSG) and pg.locator('#cbOv .cbglow.on').count() == 0,
              f'セットした：自分の わくに ふせた カード（第4.187版：うら ＋ しるし「1」・「ふせて セット」）・手札 4まい・「コンピュータが えらんで いるよ…」（{pg.evaluate(SLOT)}）')
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
              and asked(pg) == ['7 の 効果を 使う？', '7 を 3まい 山札に もどして、新しく 3まい 引けるよ'] and acts(pg) == [] and pg.evaluate(MSG) == '効果を 使うか えらんでね' and pg.evaluate(SLOT) == 'b b[1]:ふせて セット' and pg.evaluate("() => window.__seen.length") == 0,
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
        iu = [i for i, x in enumerate(sd) if x.startswith('use:')]; it = [i for i, x in enumerate(sd) if '7 を 3まい もどして、新しく 3まい 引いたよ' in x]
        check(len(iu) == 1 and sd[iu[0]] == 'use:あなたが 使った！7 の 効果3まい 交換7 を 3まい 山札に もどして、新しく 3まい 引くよ' and it and iu[0] < it[0],
              f'第4.185版：効果を 使う とき、まず 効果の 札「あなたが 使った！ 7 の 効果 3まい 交換 …」→ その あと カードが 動いて「…3まい 引いたよ」（{sd[iu[0]] if iu else None}）')
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
              and any('コンピュータが 6 の 効果で、' in s and 'あなたの 2 を 見たよ' in s for s in sd) and any(s == 'use:コンピュータが 使った！6 の 効果手札を 1まい 見る6 を 2まい 見せて、あなたの 手札を 1まい 見るよ' for s in sd),
              '相手が 6 の 効果：効果の 札「コンピュータが 使った！ 6 の 効果」→「あなたの 2 を 見たよ」（第4.185版：見られた カードの 名前）・相手の 6 が 2まい 表に・見られた 自分の カード（2）に 目の しるし')
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
        us = [x[4:].split('！')[0] + '！' + x.split('！')[1][:6] for x in sd if x.startswith('use:')]
        check(us == ['あなたが 使った！6 の 効果', 'コンピュータが 使った！7 の 効果'], f'効果の 札も 6 → 7 の 順（{us}）')
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
        check(any('コンピュータが 神様馬の 効果で、' in s and 'あなたの 2 を 見たよ' in s for s in sd) and any(s == 'use:コンピュータが 使った！神様馬の 効果手札を 1まい 見る前の ターンに 神様馬で 勝った ので、あなたの 手札を 1まい 見るよ' for s in sd) and pg.locator('#cbOv .cbhand .cbc:has(.eye) img').get_attribute('src') == 'cb_s2.webp' and pg.evaluate(V)['phase'] == 'set' and pg.evaluate(V)['can']['set'], '相手が 効果を 使った → 見られた カードに 目の しるし → セットへ')

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
        check(asked(pg) == ['4 の 効果を 使う？', '4 を 見せて、相手に カードを 交換させるよ'] and pg.evaluate(ASKQ)['img'] == 'cb_c4.webp' and pg.evaluate(SLOT) == 'b b[4]:ふせて セット', f'4 を セットした あと →「4 の 効果を 使う？」（まだ ふせた まま：{pg.evaluate(SLOT)}）')
        said(pg)
        pg.locator('#cbOv [data-cb=effyes]').click(); idle(pg)
        v = pg.evaluate(V); sd = said(pg)
        check(v['phase'] == 'swap' and v['pend']['mine'] is False and pg.evaluate(SLOT) == 'b 4:4 の 効果' and 'コンピュータが カードを 交換して いるよ' in pg.evaluate(MSG) and any(s == 'use:あなたが 使った！4 の 効果強制 交換4 を 先に 見せたよ。コンピュータは セットした カードを 交換するよ' for s in sd) and not any(s.startswith('ban:4 の 効果') for s in sd),
              f'「使う」：効果の 札「あなたが 使った！ 4 の 効果 強制 交換」（第4.185版：前の 帯の かわり）→ 4 が 表に なって 相手の 交換を 待つ（{pg.evaluate(SLOT)}）')
        pg.evaluate("() => { window.__seen = []; }")
        opp(pg, {'t': 'swap', 'k': 5}); opp(pg, {'t': 'u5', 'drop': None})      # 第4.183版：交換で 出した 5 の 効果は 使わない
        seen = pg.evaluate("() => window.__seen")
        check(any('勝ち！' in s and '4 が 5 に 勝ったよ' in s for s in seen) and pg.evaluate(V)['my']['wins'] == 1 and pg.locator('#cbOv .cbohand .cbc').count() == 4, '相手は 1 を もどして 5 を 出した（5 の 効果は 使わない）→ 4 の 勝ち（相手の 手札は 4まいの まま）')
        start(pg, '41236', '15677'); play(pg, '4'); opp(pg, {'t': 'set', 'k': 1}); pg.evaluate("() => { window.__seen = []; }")
        pg.locator('#cbOv [data-cb=effno]').click(); idle(pg)
        check(any('負け…' in s and '1 の ほうが 強いよ' in s for s in pg.evaluate("() => window.__seen")), '「使わない」→ そのまま オープン（4 と 1 → 負け）')
        # 相手が 4 の 効果：自分が 交換する
        start(pg, '15677', '41236'); play(pg, '1'); opp(pg, {'t': 'set', 'k': 4}); said(pg)
        opp(pg, {'t': 'eff', 'use': {'u4': True}})
        v = pg.evaluate(V); sd = said(pg)
        check(v['phase'] == 'swap' and v['pend']['mine'] and pg.evaluate(SLOT) == '4:4 の 効果 b[1]:ふせて セット' and 'コンピュータが 4 の 効果を 使ったよ！' in pg.evaluate(MSG) and pg.locator('#cbOv .cbglow.on').count() == 1 and any(s.startswith('use:コンピュータが 使った！4 の 効果強制 交換') and 'あなたは セットした カードを、手札の 別の カードと 交換してね' in s for s in sd),
              f'相手が 4 の 効果：自分が 交換する 番（{pg.evaluate(SLOT)}）')
        shot(pg, 'cb_pend_swap')
        tap(pg, '5')
        check(modbtns(pg) == ['この カードと 交換する', 'もどる'], '手札を タップ →「この カードと 交換する」')
        pg.evaluate("() => { window.__seen = []; }")
        pg.locator('#cbOv .cbmod [data-cb=swap]').click(); idle(pg)
        a5x = pg.evaluate(ASKQ); pg.locator('#cbOv .cbmod.cbask [data-cb=u5no]').click(); idle(pg)      # 第4.183版：交換で 出した 5 → 5 の 効果を 使うか 聞かれる → 使わない
        seen = pg.evaluate("() => window.__seen")
        check(a5x and a5x['q'] == '5 の 効果を 使う？' and any('負け…' in s for s in seen) and pg.evaluate(HAND) == '1677' and pg.evaluate(V)['op']['wins'] == 1, f'5 と 交換（1 は 手札に もどる）→「5 の 効果を 使う？」→ 使わない → 4 と 5 で 負け（手札 {pg.evaluate(HAND)}）')

        # 第4.181版（まさちゃん 19:05「4をお互いに出して効果を発動した場合、ドローになる」）：2人とも 4 → 2人とも 効果を 使う → 打ち消して ドロー
        start(pg, '41236', '41567'); play(pg, '4'); opp(pg, {'t': 'set', 'k': 4})
        check(asked(pg) == ['4 の 効果を 使う？', '4 を 見せて、相手に カードを 交換させるよ'], '2人とも 4 を セット → 自分にも「4 の 効果を 使う？」')
        opp(pg, {'t': 'eff', 'use': {'u4': True}}); said(pg)
        pg.evaluate("""() => { window.__seen = []; window.__cls = []; const m = document.querySelector('#cbOv .cbmod');
          const mo = new MutationObserver(() => { const r = m.querySelector('.cbres.on'); if (m.classList.contains('cbopen') && r) window.__cls.push(['my', 'op'].map(x => m.querySelector('[data-sd=' + x + ']').className).join('|')); });
          mo.observe(m, { childList: true, subtree: true, attributes: true }); window.__mo4 = mo; }""")
        pg.locator('#cbOv [data-cb=effyes]').click(); idle(pg)
        seen = pg.evaluate("() => window.__seen"); sd = said(pg); cls = pg.evaluate("() => { window.__mo4.disconnect(); return window.__cls; }"); v = pg.evaluate(V)
        check(any('ドロー！' in x and 'どちらも 4 の 効果を 使った ので 引き分け' in x for x in seen) and any(x == 'use:どちらも 使った！4 の 効果打ち消して ドロー2人とも 4 の 効果を 使った ので、打ち消しあって この ターンは ドロー（引き分け）だよ' for x in sd)
              and v['turn'] == 2 and v['my']['wins'] == 0 and v['op']['wins'] == 0 and v['last']['res'] == 'tie' and v['last']['d4'] is True and pg.evaluate(PIPS) == '0-0' and pg.evaluate(HAND) == '1236',
              f'2人とも 4 の 効果を 使った → 効果の 札「どちらも 使った！ 4 の 効果 打ち消して ドロー」→ オープンは「ドロー！ どちらも 4 の 効果を 使った ので 引き分け」（しるしは ふえない・交換なし：手札 {pg.evaluate(HAND)}）')
        check(bool(cls) and all('ls' not in c.split('|')[0].split() and 'ls' not in c.split('|')[1].split() for c in cls), f'ドローの ときは どちらの カードも 暗く しない（{cls[-1] if cls else None}）')
        start(pg, '41236', '41567'); play(pg, '4'); opp(pg, {'t': 'set', 'k': 4}); opp(pg, {'t': 'eff', 'use': {}})
        pg.evaluate("() => { window.__seen = []; }")
        pg.locator('#cbOv [data-cb=effno]').click(); idle(pg)
        check(any('かぶり！' in x and '同じ カード（4）＝どちらも 負け' in x for x in pg.evaluate("() => window.__seen")) and pg.evaluate(V)['last']['d4'] is False, '2人とも 4 で、2人とも 効果を 使わない → いままで どおり「かぶり！ どちらも 負け」')

        print('■ 効果タイム：使える 効果が 2つ（7 と 5）→ 1つ ずつ 聞く（第4.188版：手札の 効果〈7〉が 先・セットした カードの 効果〈5〉が あと）')
        start(pg, '57771', '12346', '2346'); play(pg, '5'); opp(pg, {'t': 'set', 'k': 1})
        check(pg.evaluate("() => CBApp._t.mode.q") == '7' and asked(pg)[0] == '7 の 効果を 使う？', '1つ目：「7 の 効果を 使う？」（手札の 効果が 先）')
        pg.locator('#cbOv [data-cb=effyes]').click(); pg.wait_for_timeout(120)
        check(pg.evaluate(V)['phase'] == 'eff' and pg.evaluate("() => CBApp._t.mode.q") == '5' and asked(pg)[0] == '5 の 効果を 使う？' and pg.evaluate(ASKQ)['img'] == 'cb_c5.webp' and pg.evaluate(DOMHAND) == '1777',
              '7 の 答え（使う）の あと、2つ目：「5 の 効果を 使う？」（まだ 何も おきて いない：答え終わって から まとめて）')
        pg.locator('#cbOv [data-cb=effyes]').click(); pg.wait_for_timeout(80); tap(pg, '7'); m7 = modbtns(pg); t7 = pg.locator('#cbOv .cbmod').inner_text()
        check(m7 == ['もどる'] and '7 の 効果で もどす 7 なので、捨てられないよ' in t7, f'5 で 捨てる カード：7 の 効果で もどす 7（3まい）は えらべない（{m7}）')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        said(pg); pg.evaluate("() => { window.__seen = []; }")
        tap(pg, '1'); pg.locator('#cbOv .cbmod [data-cb=drop5]').click(); idle(pg); sd = said(pg)
        i5 = [i for i, s in enumerate(sd) if '5 と 1 を 捨てて' in s]; i7 = [i for i, s in enumerate(sd) if '7 を 3まい もどして' in s]
        check(i5 and i7 and i7[0] < i5[0] and pg.evaluate(HAND) == '234' and pg.evaluate(V)['last']['c'][1] == '1' and pg.evaluate(V)['turn'] == 2, f'両方 使う → 7 → 5 の 順に 出て オープン（手札 {pg.evaluate(HAND)}：7 で 2・3・4 を 引いて、5 で 1 を 捨てた）')
        start(pg, '57771', '12346', '2346'); play(pg, '5'); opp(pg, {'t': 'set', 'k': 1})
        pg.locator('#cbOv [data-cb=effno]').click(); pg.wait_for_timeout(80)
        check(asked(pg)[0] == '5 の 効果を 使う？', '7 を「使わない」→「5 の 効果を 使う？」')
        pg.locator('#cbOv [data-cb=effyes]').click(); pg.wait_for_timeout(80); tap(pg, '7'); pg.locator('#cbOv .cbmod [data-cb=drop5]').click(); idle(pg)
        check(pg.evaluate(V)['turn'] == 2 and pg.evaluate(HAND) == '177', '7 の 効果を 使わない ときは、5 で 7 を 捨てても いい（7 が 2まいに なる）')

        print('■ うっかり 押し 防止：聞く 窓が 出て すぐ（0.35秒）は 答えを 受けつけない（すばやく 2回 押しても 2つ目の 質問は 答えた ことに ならない）')
        pg.evaluate("() => { CBApp._guard = null; }")      # ふだんの 動き（0.35秒）
        start(pg, '57771', '12346', '2346'); play(pg, '5'); opp(pg, {'t': 'set', 'k': 1}); pg.wait_for_timeout(450)
        g = pg.evaluate("""() => { const T = CBApp._t, q0 = T.mode.q; document.querySelector('#cbOv .cbask [data-cb=effno]').click(); const q1 = T.mode.q, b = document.querySelector('#cbOv .cbask [data-cb=effno]');
          if (b) b.click(); const pk = document.querySelector('#cbOv .cbask [data-cb=askpeek]'); return { q0, q1, q2: T.mode.q, ask: T.ask, has: !!b, peek: !!pk }; }""")
        check(g == {'q0': '7', 'q1': '5', 'q2': '5', 'ask': True, 'has': True, 'peek': True} and asked(pg)[0] == '5 の 効果を 使う？' and pg.evaluate(V)['phase'] == 'eff',
              f'「使わない」を すばやく 2回：1回目で 7 の 質問に 答える → 同じ 所に 出た「5 の 効果を 使う？」は 2回目では 答えた ことに ならない（まだ 聞いて いる：{g}）')
        pg.wait_for_timeout(420); pg.locator('#cbOv .cbask [data-cb=effno]').click(); idle(pg)
        check(pg.evaluate(V)['turn'] == 2 and pg.evaluate(HAND) == '1777', f'0.35秒 たてば 押せる：5 の 効果も「使わない」→ そのまま オープン（手札 {pg.evaluate(HAND)}）')
        start(pg, '57771', '12346', '2346'); play(pg, '5'); opp(pg, {'t': 'set', 'k': 1}); pg.wait_for_timeout(450)
        pg.locator('#cbOv .cbask [data-cb=effno]').click()
        g2 = pg.evaluate("() => { const b = document.querySelector('#cbOv .cbask [data-cb=askpeek]'); if (b) b.click(); return { had: !!b, ask: CBApp._t.ask, bar: [...document.querySelectorAll('#cbOv .cbact .cbb')].map(x => x.textContent.trim()) }; }")
        check(g2['had'] and not g2['ask'] and g2['bar'] == ['使わない', '5 の 効果を 使う'], f'「手札と ボードを 見る」は 出て すぐでも 押せる（何も 決まらない：下の 行で 答える {g2["bar"]}）')
        pg.locator('#cbOv .cbact [data-cb=effno]').click(); idle(pg)
        check(pg.evaluate(V)['turn'] == 2 and pg.evaluate(HAND) == '1777', '下の 行の「使わない」は すぐ 押せる（手札は そのまま）')
        pg.evaluate("() => { CBApp._guard = 0; }")

        print('■ 4 は いちばん あと（第4.188版・まさちゃん 11:16「4は効果発動最後にして！」）')
        start(pg, '51237', '41236', 'k'); play(pg, '5'); opp(pg, {'t': 'set', 'k': 4})
        pg.locator('#cbOv [data-cb=effyes]').click(); pg.wait_for_timeout(80); tap(pg, '7'); pg.locator('#cbOv .cbmod [data-cb=drop5]').click(); idle(pg)
        said(pg); opp(pg, {'t': 'eff', 'use': {'u4': True}}); sd = said(pg); v = pg.evaluate(V)
        i5 = [i for i, x in enumerate(sd) if '5 と 7 を 捨てて、山札から 1まい セットしたよ' in x]; i4 = [i for i, x in enumerate(sd) if x.startswith('use:コンピュータが 使った！4 の 効果')]
        check(i5 and i4 and i5[0] < i4[0] and v['phase'] == 'swap' and v['pend']['mine'] and v['my']['set']['blind'] is True and pg.evaluate(SLOT) == '4:4 の 効果 b:山札から' and pg.evaluate(HAND) == '123',
              f'自分は 5 の 効果（5 と 7 を 捨てて 山札から ふせて セット）→ 相手の 4 の 効果（いちばん あと）→ 山札から 来た カードを 交換する 番（{pg.evaluate(SLOT)}）')
        shot(pg, 'cb_4last')
        tap(pg, '1'); pg.locator('#cbOv .cbmod [data-cb=swap]').click(); idle(pg); v = pg.evaluate(V)
        check(v['turn'] == 2 and v['my']['wins'] == 1 and pg.evaluate(HAND) == '23k', f'交換して 1 を 出す → 1 が 4 に 勝つ（山札から 来て いた 神様馬は 手札に：{pg.evaluate(HAND)}）')

        print('■ 逆転勝利：相手の 5 の 効果で 入れ替わった カードでも（第4.188版の 確かめ・まさちゃん 11:05「1と2の効果は、5の効果でカードが入れ替わった際もオープンしたあとに使用できるようになってる？」）')
        start(pg, '11123', '54672', 'k'); play(pg, '1'); opp(pg, {'t': 'set', 'k': 5}); said(pg); pg.evaluate("() => { window.__seen = []; }")
        opp(pg, {'t': 'eff', 'use': {'u5k': 7}}); seen = pg.evaluate("() => window.__seen"); aw = pg.evaluate(ASKQ); v = pg.evaluate(V)
        check(any('チャンス！' in s and '神様馬 の ほうが 強い…でも 1 の「逆転勝利」を 使えるよ' in s for s in seen) and aw and aw['q'] == '1 の 効果を 使う？' and aw['text'] == '手札の 1 を 2まい 見せて、1まい 捨てると、神様馬に 勝てるよ' and v['phase'] == 'rev',
              '相手の 5 の 効果 → 山札の 神様馬が 場に → オープン「チャンス！」→ 聞く 窓「1 の 効果を 使う？」')
        shot(pg, 'cb_rev_after5')
        pg.locator('#cbOv .cbask [data-cb=revyes]').click(); idle(pg); v = pg.evaluate(V); sd = said(pg)
        check(v['my']['wins'] == 1 and v['op']['wins'] == 0 and v['turn'] == 2 and any(s.startswith('ban:逆転勝利！') and '1 が 神様馬 に 勝ったよ' in s for s in sd), '使う →「逆転勝利！ 1 が 神様馬 に 勝ったよ」（大逆転）')
        start(pg, '22234', '54673', '1'); play(pg, '2'); opp(pg, {'t': 'set', 'k': 5}); opp(pg, {'t': 'eff', 'use': {'u5k': 7}})
        aw = pg.evaluate(ASKQ)
        check(aw and aw['q'] == '2 の 効果を 使う？' and aw['text'] == '手札の 2 を 2まい 見せて、1まい 捨てると、1 に 勝てるよ', '2 は 1 に 対して 同じ（相手の 5 の 効果で 山札の 1 が 出ても「2 の 効果を 使う？」）')
        pg.locator('#cbOv .cbask [data-cb=revyes]').click(); idle(pg)
        check(pg.evaluate(V)['my']['wins'] == 1 and pg.evaluate(V)['op']['wins'] == 0, '使う → 2 が 1 に 逆転勝利')

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

        print('■ 設定の 窓：BGM・効果音（第4.178版・まさちゃん「プレイボードの右下の設定ボタンを押すと、BGMオンかオフと効果エフェクトオンかオフを選べるようにして！」・第4.185版：23:04「設定のエフェクトオフもいらない！」→ エフェクトは なくした）')
        pg.evaluate("() => { localStorage.removeItem('tengel.cb'); CBApp._t.load(); CBApp._as = null; }")
        s0 = pg.evaluate("() => ({ sets: CBApp._t.sets, app: !!(window.TengelFx && TengelFx.get && TengelFx.get().sound !== false) })")
        check(s0['sets']['raw'] == {'bgm': None, 'se': None} and s0['sets']['se'] == s0['app'] and 'fx' not in s0['sets'] and s0['sets']['bgm'] == (s0['app'] and s0['sets']['as']),
              f'まだ 決めて いない とき：効果音＝アプリの 効果音の 設定（{s0["app"]}）・BGM＝アプリの 効果音が オン で、消音スイッチに 合わせられる iOS（16.4 から）の とき だけ オン（ここ {s0["sets"]["as"]} → {s0["sets"]["bgm"]}）')
        pg.evaluate("() => { CBApp._as = true; }")
        check(pg.evaluate("() => CBApp._t.sets.bgm") == s0['app'], '（消音スイッチに 合わせられる iOS と 同じ 形に して 見る：BGM は はじめから オン）')
        pg.evaluate("() => { CBApp._as = null; }")
        SETM = """() => { const m = document.querySelector('#cbOv .cbmod.cbset'); if (!m) return null; const R = e => { const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; };
          return { h: m.querySelector('h3').textContent, rows: [...m.querySelectorAll('.cbsw')].map(r => r.dataset.set + ':' + r.querySelector('span').textContent + ':' + [...r.querySelectorAll('.cbseg button')].map(b => b.textContent + (b.classList.contains('on') ? '*' : '') + (b.getAttribute('aria-pressed') === 'true' ? '!' : '')).join('/')),
            btns: [...m.querySelectorAll('.cbb')].map(b => b.textContent.trim()), seg: [...m.querySelectorAll('.cbseg button')].map(R), box: R(m), vh: innerHeight, vw: innerWidth, last: R([...m.querySelectorAll('.cbb')].pop()), h3: R(m.querySelector('h3')), bg: getComputedStyle(m).backgroundColor }; }"""
        pg.locator('#cbOv .cbmenu [data-cb=gear]').click(); pg.wait_for_timeout(120)
        sm = pg.evaluate(SETM); app = '*!' if s0['app'] else ''; napp = '' if s0['app'] else '*!'
        check(sm and sm['h'] == '設定' and sm['rows'] == ['bgm:BGM音楽:オン/オフ*!', f'se:効果音カードや ボタンの 音:オン{app}/オフ{napp}'] and sm['btns'] == ['もどる'],
              f'メニューの「設定」→ 設定の 窓：BGM・効果音 の 2つ（それぞれ オン／オフ・第4.185版：エフェクトは なくした）・「もどる」（{sm and sm["rows"]}）')
        check(sm and all(b[2] - b[0] >= 56 and b[3] - b[1] >= 40 for b in sm['seg']) and sm['h3'][1] >= 0 and sm['last'][3] <= sm['vh'] and all(b[0] >= 0 and b[2] <= sm['vw'] for b in sm['seg']), 'オン／オフの ボタンは 押しやすい 大きさ（幅 56px・高さ 40px 以上）・窓は 画面の 中')
        shot(pg, 'cb_set_menu')
        # 第4.185版：エフェクトの オン／オフは ない（窓に ボタンが ない・火の あかりは いつも ゆれる）。前の 版で「オフ」に して いた 人も（fx:false は すてる）
        FIRE = "() => [...document.querySelectorAll('#cbOv .cbfire')].map(e => { const c = getComputedStyle(e); return c.animationName + ' ' + c.animationDuration + ' ' + c.pointerEvents; })"
        f_on = pg.evaluate(FIRE); nb = pg.locator('#cbOv .cbset [data-k=fx]').count()
        pg.evaluate("() => { const s = JSON.parse(localStorage.getItem('tengel.cb') || JSON.stringify({ v: 1 })); s.fx = false; localStorage.setItem('tengel.cb', JSON.stringify(s)); CBApp._t.load(); CBApp._t.save(); }")
        st1 = pg.evaluate("() => ({ ls: JSON.parse(localStorage.getItem('tengel.cb')), nofx: document.querySelector('#cbOv').classList.contains('nofx'), sets: CBApp._t.sets, has: 'fx' in CBApp._t.state })")
        check(f_on == ['cbfire 5.6s none', 'cbfire 4.3s none'] and nb == 0 and pg.evaluate(FIRE) == f_on and not st1['nofx'] and 'fx' not in st1['ls'] and 'fx' not in st1['sets'] and not st1['has'],
              f'エフェクトの オン／オフは ない：窓に ボタンが ない（{nb}）・火の あかりは いつも ゆれる（{f_on}）・前の 版の「エフェクト オフ」（fx:false）は 読み直すと すてる')
        # 効果音：オフに すると 鳴らさない（音を 鳴らした 数＝__abs が ふえない）／オンに すると 鳴る
        pg.locator('#cbOv .cbset [data-cb=tg][data-k=bgm][data-v="0"]').click(); pg.locator('#cbOv .cbset [data-cb=tg][data-k=se][data-v="0"]').click(); pg.wait_for_timeout(150)
        pg.locator('#cbOv .cbset [data-cb=modx]').click(); pg.wait_for_timeout(100)
        a0 = pg.evaluate("() => window.__abs")
        start(pg, '1234567', '1234567', turns=5); tap(pg, '1'); pg.locator('#cbOv .cbmod [data-cb=set]').click(); idle(pg); pg.wait_for_timeout(250)
        a1 = pg.evaluate("() => window.__abs")
        check(a1 == a0 and pg.evaluate("() => CBApp._t.sets.se") is False and pg.evaluate("() => JSON.parse(localStorage.getItem('tengel.cb')).se") is False, f'効果音 オフ：配る・カードを 押す・セットしても 音を 鳴らさない（鳴らした 数 {a0} → {a1}）')
        pg.locator('#cbOv .cbgear').click(); pg.wait_for_timeout(120)
        sg = pg.evaluate(SETM)
        check(sg and sg['rows'] == ['bgm:BGM音楽:オン/オフ*!', 'se:効果音カードや ボタンの 音:オン/オフ*!'] and sg['btns'] == ['対戦に もどる', 'あそび方', '対戦を やめる'] and sg['last'][3] <= sg['vh'],
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
        check(pg.evaluate("() => CBApp._t.sets.raw") == {'bgm': True, 'se': True}, '読み直しても えらんだ 設定の まま')
        pg.evaluate("() => { CBApp._t.setSet('bgm', false); localStorage.removeItem('tengel.cb'); CBApp._t.load(); }"); pg.wait_for_timeout(150)
        check(pg.evaluate("() => CBApp._t.sets.raw") == {'bgm': None, 'se': None} and not pg.evaluate("() => CBApp._t.bgm.on"), '（設定を 消して もとに もどした：BGM は 止まって いる）')

        print('■ 効果を 使った ときの 札（第4.185版・まさちゃん 23:06「効果を使っている時が分かりにくいから、何の効果を使っていて、何をするのか分かるようにして！ テンゲルカードバトルの雰囲気は壊さないようにね！」）')
        pg.evaluate("""() => { window.__use = []; const e = document.querySelector('#cbOv .cbuse'); new MutationObserver(() => { if (!e.classList.contains('on')) return;
          const s = e.className + '|' + [...e.querySelectorAll('.cd img')].map(i => i.getAttribute('src')).join(','); if (window.__use[window.__use.length - 1] !== s) window.__use.push(s); }).observe(e, { attributes: true, attributeFilter: ['class'] }); }""")
        UG = """() => { const e = document.querySelector('#cbOv .cbuse'), i = e.querySelector('.in'), b = document.querySelector('#cbOv .cbboard'); const R = x => { const r = x.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; };
          const ts = q => parseFloat(getComputedStyle(e.querySelector(q)).fontSize), p = R(i), hit = document.elementFromPoint((p[0] + p[2]) / 2, (p[1] + p[3]) / 2);
          return { cls: e.className, p: p, b: R(b), vw: innerWidth, vh: innerHeight, who: e.querySelector('.who').textContent, t: e.querySelector('b').textContent, n: e.querySelector('em').textContent, d: e.querySelector('small').textContent,
            img: e.querySelector('.cd img').getAttribute('src'), z: +getComputedStyle(e).zIndex, fs: [ts('b'), ts('em'), ts('small'), ts('.who')], gold: e.querySelector('b').classList.contains('gold'), bd: getComputedStyle(i).borderTopColor,
            top: !!hit && hit.closest('.cbuse') === e, msg: document.querySelector('#cbOv .cbmsg').textContent, fit: [...e.querySelectorAll('.tx > *')].every(x => x.scrollWidth <= x.clientWidth + 1) }; }"""
        start(pg, '77712', '12345', '346'); play(pg, '1'); opp(pg, {'t': 'set', 'k': 2})
        pg.evaluate("() => CBApp._t.speed(1)"); pg.locator('#cbOv [data-cb=effyes]').click()
        pg.wait_for_function("() => document.querySelector('#cbOv .cbuse.on')", timeout=10000); pg.wait_for_timeout(450); g = pg.evaluate(UG)
        check(g['cls'] == 'cbuse me on' and g['who'] == 'あなたが 使った！' and g['t'] == '7 の 効果' and g['n'] == '3まい 交換' and g['d'] == '7 を 3まい 山札に もどして、新しく 3まい 引くよ' and g['img'] == 'cb_s7.webp' and g['gold'] and g['msg'] == '',
              f'効果の 札：だれが（あなたが 使った！）・どの 効果（7 の カードの 絵・「7 の 効果」・金の 字）・何を する（3まい 交換：…）。下の 行の 前の 文は 消える（{g["who"]}｜{g["t"]}｜{g["n"]}）')
        check(abs((g['p'][1] + g['p'][3]) / 2 - (g['b'][1] + g['b'][3]) / 2) <= 2 and g['p'][0] >= 8 and g['p'][2] <= g['vw'] - 8 and g['p'][3] - g['p'][1] <= g['b'][3] - g['b'][1] and g['z'] == 7 and g['top'] and g['fit']
              and g['fs'][0] >= 20 and g['fs'][1] >= 14 and g['fs'][2] >= 12 and g['fs'][3] >= 11 and g['bd'] == 'rgb(201, 163, 90)',
              f'札は ボードの まん中（{g["p"]}・ボード {g["b"]}）・画面の 中・ボードの 高さに おさまる・いちばん 上に 見える（窓〈z 8〉より 下）・字 {g["fs"]}px・金の ふち（{g["bd"]}）')
        shot(pg, 'cb_use_x7')
        pg.locator('#cbOv .cbuse').click(); pg.wait_for_timeout(300); off = pg.evaluate("() => !document.querySelector('#cbOv .cbuse.on')")
        idle(pg); pg.evaluate("() => CBApp._t.speed(0.03)")
        check(off and pg.evaluate(HAND) == '2346' and pg.evaluate(V)['turn'] == 2, '札を タップ → すぐ 消えて 次へ（7 を 3まい 交換 → オープン → 2ターン目）')
        # 相手の 効果・2人とも・5・3・逆転勝利・幻の馬
        pg.evaluate("() => { window.__use.length = 0; }")
        start(pg, '12345', '77712', '346'); play(pg, '1'); said(pg); opp(pg, {'t': 'set', 'k': 2}); opp(pg, {'t': 'eff', 'use': {'x7': True}}); sd = said(pg)
        check(any(x == 'use:コンピュータが 使った！7 の 効果3まい 交換7 を 3まい 山札に もどして、新しく 3まい 引くよ' for x in sd) and pg.evaluate("() => window.__use") == ['cbuse op on|cb_s7.webp'],
              f'相手の 効果：「コンピュータが 使った！」（あかがねの しるし：class op）（{pg.evaluate("() => window.__use")}）')
        pg.evaluate("() => { window.__use.length = 0; }")
        pg.evaluate("() => { window.__use.length = 0; }")
        start(pg, '41236', '41567'); play(pg, '4'); opp(pg, {'t': 'set', 'k': 4}); opp(pg, {'t': 'eff', 'use': {'u4': True}}); said(pg); pg.locator('#cbOv [data-cb=effyes]').click(); idle(pg)
        check(pg.evaluate("() => window.__use") == ['cbuse both on|cb_s4.webp,cb_s4.webp'], f'2人とも 4：「どちらも 使った！」・4 の カードが 2まい（{pg.evaluate("() => window.__use")}）')
        start(pg, '51237', '12346', 'k'); play(pg, '5'); opp(pg, {'t': 'set', 'k': 1}); pg.locator('#cbOv [data-cb=effyes]').click(); pg.wait_for_timeout(80); tap(pg, '7'); said(pg)
        pg.locator('#cbOv .cbmod [data-cb=drop5]').click(); idle(pg); sd = said(pg)
        iu = [i for i, x in enumerate(sd) if x == 'use:あなたが 使った！5 の 効果捨てて 山札から セットセットした 5 と 手札 1まいを 捨てて、山札から 1まい ふせて セットするよ']; it = [i for i, x in enumerate(sd) if '5 と 7 を 捨てて、山札から 1まい セットしたよ' in x]
        check(iu and it and iu[0] < it[0], f'5 の 効果：札 →「5 と 7 を 捨てて、山札から 1まい セットしたよ」の 順（{[x[:30] for x in sd]}）')
        start(pg, '12456', '33312'); play(pg, '1'); said(pg); opp(pg, {'t': 'set', 'k': 2}); opp(pg, {'t': 'eff', 'use': {'x3': True}}); sd = said(pg)
        check(any(x == 'use:コンピュータが 使った！3 の 効果手札を 交換3 を 3まい 見せて、その 1まいと あなたの 手札の 1まい（ランダム）を 交換するよ' for x in sd), '3 の 効果（相手）：「…その 1まいと あなたの 手札の 1まい（ランダム）を 交換するよ」')
        start(pg, '11123', 'm4567'); play(pg, '1'); said(pg); opp(pg, {'t': 'set', 'k': 'm'}); pg.locator('#cbOv .cbmod.cbask [data-cb=revyes]').click(); idle(pg); sd = said(pg)
        check(any(x == 'use:あなたが 使った！1 の 効果逆転勝利1 を 3まい（場の 1まい ＋ 手札の 2まい）見せて、手札の 1 を 1まい 捨てると、幻の馬に 勝ち！' for x in sd), '逆転勝利（1）：「1 の 効果 逆転勝利 … 幻の馬に 勝ち！」')
        start(pg, 'm6712', '12345', '13'); play(pg, 'm'); opp(pg, {'t': 'set', 'k': 1}); pg.locator('#cbOv [data-cb=mpick]').click(); pg.wait_for_timeout(80); tap(pg, '6'); tap(pg, '7'); said(pg)
        pg.locator('#cbOv .cbact [data-cb=mgo]').click(); idle(pg); sd = said(pg)
        check(any(x == 'use:あなたが 使った！幻の馬の 効果捨てて 引きなおす前の ターンに 幻の馬で 勝った ので、手札を 2まい 捨てて、山札から 2まい 引くよ' for x in sd), '幻の馬：「前の ターンに 幻の馬で 勝った ので、手札を 2まい 捨てて、山札から 2まい 引くよ」')
        # 効果を 使わない ときは 出ない・対戦を はなれたら 消える
        start(pg, '77712', '12345'); play(pg, '1'); opp(pg, {'t': 'set', 'k': 2}); said(pg); pg.locator('#cbOv [data-cb=effno]').click(); idle(pg)
        check(not any(x.startswith('use:') for x in said(pg)), '「使わない」→ 札は 出ない')
        start(pg, '77712', '12345', '346'); play(pg, '1'); opp(pg, {'t': 'set', 'k': 2}); pg.evaluate("() => CBApp._t.speed(1)"); pg.locator('#cbOv [data-cb=effyes]').click()
        pg.wait_for_function("() => document.querySelector('#cbOv .cbuse.on')", timeout=10000); pg.evaluate("() => CBApp._t.menu()"); pg.wait_for_timeout(300)
        check(pg.evaluate("() => [CBApp._t.screen, !!document.querySelector('#cbOv .cbuse.on')]") == ['menu', False], '札が 出て いる 時に 対戦を やめて メニューへ → 札は 消える')
        pg.evaluate("() => CBApp._t.speed(0.03)")

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
        check(e['st']['coin'] == 2 and 'バトルコイン ＋2枚（いま 2枚）' in e['g'] and pg.locator('#cbOv .cbend .gift .cbcl img[src="cb_coin.webp"]').count() == 1 and 'ボーナス！＋' not in e['g'] and pg.locator('#cbOv .cbend .gift .cbsbn').count() == 0,
              f'バトルコイン：コンピュータに 勝つと 2枚（いま {e["st"]["coin"]}枚）（第4.179版 → 第4.188版：1枚 → 2枚）・1連勝では ボーナスの 札は 出ない')
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
        e = win_game()
        check(e['st']['coin'] == 4 and 'バトルコイン ＋2枚（いま 4枚）' in e['g'] and pg.locator('#cbOv .cbend .gift .cbsbn').count() == 0, f'2連勝目：バトルコイン ＋2枚（いま {e["st"]["coin"]}枚）・ボーナスの 札は 出ない')
        e = win_game()
        sb3 = pg.evaluate("""() => { const g = document.querySelector('#cbOv .cbend .gift'), b = g.querySelector('.cbsbn'), m = g.querySelector('.cbmsn'), R = e => { const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; };
          return b ? { t: b.textContent, lab: b.getAttribute('aria-label'), img: b.querySelectorAll('img[src="cb_coin.webp"]').length, anim: getComputedStyle(b).animationName + '/' + getComputedStyle(b).animationIterationCount, box: R(b), mbox: m ? R(m) : null,
            gift: R(g), h: Math.round(g.getBoundingClientRect().height), minh: parseFloat(getComputedStyle(g).minHeight), vw: innerWidth, bc: getComputedStyle(b).borderTopColor } : null; }""")
        check(e['st']['coin'] == 42 and e['st']['streak'] == 3 and 'バトルコイン ＋2枚（いま 42枚）' in e['g'] and '🎯ミッション達成！3連勝＋30枚' in e['g'] and sb3 and sb3['t'] == '🔥3連勝 ボーナス！＋6枚' and sb3['lab'] == '3連勝 ボーナス バトルコイン 6枚' and sb3['img'] == 1
              and sb3['anim'] == 'cbget/1' and sb3['mbox'] and sb3['box'][3] <= sb3['mbox'][1] and sb3['box'][0] >= 0 and sb3['box'][2] <= sb3['vw'] and sb3['h'] == sb3['minh'],
              f'3連勝目（第4.188版）：いつもの 2枚 ＋ 3連勝 ボーナス 6枚 ＋ ミッション 30枚（2＋2＋8＋30＝{e["st"]["coin"]}枚）・さいごの 画面に「🔥 3連勝 ボーナス！ 🪙＋6枚」の 札（ミッションの 札の 上・1回 ふくらむ だけ・札の 場所に おさまる {sb3 and sb3["h"]}／{sb3 and sb3["minh"]}px）')
        shot(pg, 'cb_end_bonus3')
        win_game()
        e = win_game(); t5 = pg.evaluate(TC)
        check(e['st']['coin'] == 116 and 'バトルコイン ＋2枚（いま 116枚）' in e['g'] and '🔥5連勝 ボーナス！＋10枚' in e['g'] and '🎯ミッション達成！5連勝＋60枚' in e['g'] and e['st']['ms']['cpu'] == 5 and e['st']['ms']['got']['cpu'] == [3, 5],
              f'バトルコイン：5連勝目は 2枚 ＋ 5連勝 ボーナス 10枚（2・2・8・2・12）＋ ミッション（3連勝 30枚・5連勝 60枚：第4.183版）＝ {e["st"]["coin"]}枚・さいごの 画面に「🔥 5連勝 ボーナス！ ＋10枚」「🎯 ミッション達成！ 5連勝 ＋60枚」')
        check(e['st']['streak'] == 5 and e['st']['win'] == 5 and t5 == t1 + 3 + 3 and '5連勝 ボーナス！ お世話トークン＋3こ GET！' in e['g'] and '5連勝中！' in e['g']
              and pg.evaluate("() => { const g = document.querySelector('#cbOv .cbend .gift'); return Math.round(g.getBoundingClientRect().height) === parseFloat(getComputedStyle(g).minHeight); }"), f'5連勝：5回目は ＋3（{t1} → 2・3・4回目 ＋1 ずつ → 5回目 ＋3 ＝ {t5}）（{e["g"]}）')
        e = win_game()
        check(e['st']['streak'] == 6 and pg.evaluate(TC) == t5 + 1 and 'あと 4勝で 3こ' in e['g'] and e['st']['coin'] == 214 and 'バトルコイン ＋2枚（いま 214枚）' in e['g'] and '🔥6連勝 ボーナス！＋6枚' in e['g'] and '🎯ミッション達成！6連勝＋90枚' in e['g'],
              '6連勝目は また ＋1（つぎの ＋3 は 10連勝）・バトルコインは ＋2 と 3連勝 ごとの ボーナス ＋6（6連勝）・ミッション 6連勝 ＋90枚')
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
        check(e['st']['coin'] == 1008 and 'バトルコイン ＋2枚（いま 1008枚）' in e['g'] and '🔥10連勝 ボーナス！＋10枚' in e['g'] and '🎯ミッション達成！10連勝＋300枚' in e['g'] and e['st']['ms']['got']['cpu'] == [3, 5, 6, 7, 8, 9, 10] and e['st']['ms']['cpu'] == 10,
              f'10連勝目は バトルコイン 2枚 ＋ 5連勝 ごとの ボーナス 10枚 ＋ ミッション 10連勝 300枚（勝つ ぶん 2×10＝20・ボーナス 6×3＋10×2＝38・ミッション 950：いま {e["st"]["coin"]}枚）・字は 札の 場所に おさまる')
        shot(pg, 'cb_end_coin')
        # 負け：連勝 0
        start(pg, '23677', '12356'); play(pg, '3'); opp(pg, {'t': 'set', 'k': 1}); play(pg, '6'); opp(pg, {'t': 'set', 'k': 2}); play(pg, '7'); opp(pg, {'t': 'set', 'k': 3})
        pg.wait_for_function("() => { const g = document.querySelector('#cbOv .cbend .gift'); return CBApp._t.ended && g && g.textContent.length > 3; }", timeout=30000)
        e = pg.evaluate("() => ({ h: document.querySelector('#cbOv .cbend h3').textContent, g: document.querySelector('#cbOv .cbend .gift').textContent, st: Object.assign({}, CBApp._t.state) })")
        check(e['h'] == 'あなたの 負け…' and e['st']['streak'] == 0 and e['st']['lose'] == 1 and '連勝は 0 に もどったよ' in e['g'] and pg.evaluate(TC) == 25 and pg.locator('#cbOv .cbend .cbget').count() == 0, f'負け：連勝は 0 に もどる・トークンは かわらない・GET の 札は 出ない（{e["g"]}）')
        pg.locator('#cbOv .cbend [data-cb=menu]').click(); pg.wait_for_timeout(120)
        rec = pg.locator('#cbOv .cbmenu .rec').inner_text()
        check(pg.evaluate("() => CBApp._t.screen") == 'menu' and '10勝 1敗 0分' in rec.replace('\n', ' '), f'メニューに 勝ち負けの 数（{rec!r}）')
        check(e['st']['coin'] == 1008 and 'バトルコイン' not in e['g'] and 'バトルコイン 1008枚' in pg.locator('#cbOv .cbmenu .cbcoinl').inner_text() and e['st']['ms']['cpu'] == 0 and e['st']['ms']['got']['cpu'] == [3, 5, 6, 7, 8, 9, 10],
              '負け：バトルコインは かわらない（へらない）・メニューに いまの 数（1008枚）・ミッションの 連勝は 0（達成した ものは のこる）')

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
            stt = pg.evaluate("() => { const v = CBApp._t.view; return CBApp._t.ended ? 'end' : !v ? 'none' : v.pend && v.pend.mine ? v.pend.type : v.can.eff ? 'eff' : v.can.set ? (v.can.x7r && CBApp._t.ask ? 'x7' : 'set') : 'wait'; }")
            if stt == 'end': done = True; break
            if stt == 'x7': pg.locator('#cbOv .cbask [data-cb=x7no]').click()      # 第4.187版：7 が 4まい（セットの 前）→ 使わない
            elif stt in ('k', 'm'): pg.locator(f'#cbOv [data-cb={stt}skip]').click()
            elif stt == 'rev': pg.locator('#cbOv [data-cb=revyes]').first.click()
            elif stt == 'u5': pg.locator('#cbOv [data-cb=u5no]').first.click()      # 第4.183版
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
        check(pg.evaluate(SLOT) == 'b -' and 'ともだちは もう セットしたよ' in pg.evaluate(MSG) and gp.evaluate(SLOT) == '- b[3]:ふせて セット' and 'ともだちが えらんで いるよ' in gp.evaluate(MSG), 'ゲストが セットした → ホストの 画面に うらの カード・ゲストは 待つ')
        pg.evaluate("() => { window.__seen = []; const mo = new MutationObserver(() => { const m = document.querySelector('#cbOv .cbmod'); if (m.classList.contains('cbopen')) { const t = m.querySelector('.cbres'); window.__seen.push((m.querySelector('h3') || {}).textContent + '|' + (t ? t.textContent : '')); } }); mo.observe(document.querySelector('#cbOv .cbmod'), { childList: true, subtree: true, attributes: true, characterData: true }); }")
        gp.evaluate("() => { window.__seen = []; const mo = new MutationObserver(() => { const m = document.querySelector('#cbOv .cbmod'); if (m.classList.contains('cbopen')) { const t = m.querySelector('.cbres'); window.__seen.push((m.querySelector('h3') || {}).textContent + '|' + (t ? t.textContent : '')); } }); mo.observe(document.querySelector('#cbOv .cbmod'), { childList: true, subtree: true, attributes: true, characterData: true }); }")
        said(pg); said(gp)
        play(pg, 'k'); idle(gp)
        check(pg.evaluate(V)['phase'] == 'eff' and asked(pg)[0] == '6 の 効果を 使う？' and 'ともだちが 効果を 使うか えらんで いるよ' in gp.evaluate(MSG) and acts(gp) == [] and gp.evaluate(SLOT) == 'b b[3]:ふせて セット'
              and any(s.startswith('ban:効果タイム') and 'カードの 効果を 使うか えらんでね' in s for s in said(pg)) and any(s.startswith('ban:効果タイム') and 'ともだちが 効果を 使うか えらぶよ' in s for s in said(gp)) and not pg.evaluate("() => window.__seen.length") and not gp.evaluate("() => window.__seen.length"),
              'ホストも セットした → 2人の 画面に「効果タイム」：ホスト（6 が 2まい）は「6 の 効果を 使う？」・ゲストは 待つ（オープンは まだ）')
        pg.locator('#cbOv [data-cb=effyes]').click(); pg.wait_for_timeout(80); pg.locator('#cbOv .cbmod .pick .cbc').last.click(); idle(pg); idle(gp)
        check(any('勝ち！' in s for s in pg.evaluate("() => window.__seen")) and any('負け…' in s for s in gp.evaluate("() => window.__seen")) and pg.evaluate(V)['turn'] == 2 and pg.evaluate(V)['pend']['mine'] and asked(pg)[0] == '神様馬の 効果を 使う？'
              and 'ともだちが 神様馬の 効果を 使うか えらんで いるよ' in gp.evaluate(MSG) and gp.locator('#cbOv .cbohand .cbc img[src="cb_s6.webp"]').count() == 2 and gp.locator('#cbOv .cbhand .cbc .eye').count() == 1 and (lambda sg: any('ともだちが 6 の 効果で、' in s and 'を 見たよ' in s for s in sg) and any(s.startswith('use:ともだちが 使った！6 の 効果手札を 1まい 見る') for s in sg))(said(gp)),
              'ホストが 6 の 効果 → 2人の 画面で オープン（ホスト「勝ち！」・ゲスト「負け…」）→ 2ターン目の はじめ：神様馬の 効果は ホストが えらぶ・ゲストは 待つ')
        pg.locator('#cbOv [data-cb=kgo]').click(); pg.wait_for_timeout(80); pg.locator('#cbOv .cbmod .pick .cbc').first.click(); idle(pg); idle(gp)
        check(len([c for c in pg.evaluate(V)['op']['hand'] if c['k']]) >= 1 and gp.locator('#cbOv .cbhand .cbc .eye').count() >= 1 and pg.evaluate(V)['turn'] == 2 and gp.evaluate(V)['turn'] == 2 and pg.evaluate(V)['can']['set'] and gp.evaluate(V)['can']['set'], 'ホストが ゲストの 手札を 1まい 見た → ゲストの その カードに 目の しるし・2人とも 2ターン目の セットへ')
        gp.locator('#cbOv [data-cb=discard]').click(); gp.wait_for_timeout(80)
        gd = gp.evaluate("() => [...document.querySelectorAll('#cbOv .cbmod .cbdl .row[data-dt]')].map(r => r.querySelector('b').textContent + '|' + [...r.querySelectorAll('.pr')].map(p => p.querySelector('span').textContent + '=' + [...p.querySelectorAll('img')].map(i => i.getAttribute('src').replace('cb_s', '').replace('.webp', '')).join('')).join('|'))")
        check(gd == ['ターン 1|あなた=3|ともだち=k'], f'ゲストの 捨て札の 窓：自分から 見た 形（{gd}）')
        gp.locator('#cbOv .cbmod [data-cb=modx]').click(); gp.wait_for_timeout(60)
        def step(q):
            idle(q)
            stt = q.evaluate("() => { const v = CBApp._t.view; return CBApp._t.ended ? 'end' : !v ? 'none' : v.pend && v.pend.mine ? v.pend.type : v.can.eff ? 'eff' : v.can.set ? (v.can.x7r && CBApp._t.ask ? 'x7' : 'set') : 'wait'; }")
            if stt == 'x7': q.locator('#cbOv .cbask [data-cb=x7no]').click()      # 第4.187版
            elif stt in ('k', 'm'): q.locator(f'#cbOv [data-cb={stt}skip]').click()
            elif stt == 'rev': q.locator('#cbOv [data-cb=revno]').first.click()
            elif stt == 'u5': q.locator('#cbOv [data-cb=u5no]').first.click()      # 第4.183版
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
        check(gp.evaluate("() => CBApp._t.screen") == 'menu' and s1['lose'] == s0['lose'] + 1 and 'ともだちが 部屋を 出たよ' in pg.locator('#cbOv .cbmod').inner_text() and '勝ち負けに 数えないよ' in pg.locator('#cbOv .cbmod').inner_text() and {k: x for k, x in h1.items() if k != 'ms'} == {k: x for k, x in h0.items() if k != 'ms'}
              and h0['ms']['live'] == 'fr' and h1['ms']['live'] == '' and h1['ms']['fr'] == h0['ms']['fr'] and s1['ms']['fr'] == 0 and s1['ms']['live'] == '',
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
        MSZ = "() => { const s = CBApp._t.state.ms; s.cpu = 0; s.fr = 0; s.got = { cpu: [], fr: [] }; s.live = ''; }"      # 第4.183版：ミッションを 0 から（この 場面の コインの 数を ミッションで かえない）
        pg.evaluate(MSZ); gp.evaluate(MSZ)
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
        print('■ デザインカスタム・カードパック（第4.189版・まさちゃん 11/17 15:00「1パックコイン112枚 カード購入ではなく、パック式にする … 1パック5枚にする レアは2パックに1枚 超レアは5パックに1枚 神様馬と幻の馬のレアは10パックに1枚 神様馬と幻の馬の超レアは23パックに1枚」・'
              '15:18「…毎回0〜229の番号を均等に1つ選ぶ… 112コインの消費・5枚の付与・購入履歴の保存をまとめて確定… 購入履歴から同じ結果を再表示… 連打しても、同じ購入を二重処理しない」・15:39 パックの 絵）')
        pg.evaluate("() => { const T = CBApp._t; T.state.coin = 0; T.state.backs = []; T.state.faces = []; T.state.back = ''; T.state.face = {}; T.state.pkh = []; T.state.packs = 0; T.save(); T.menu(); }"); pg.wait_for_timeout(200)
        pg.locator('#cbOv .cbmenu [data-cb=dz]').click(); pg.wait_for_timeout(250)
        DZ = """() => { const s = document.querySelector('#cbOv .cbdz'), T = x => x.textContent.replace(/\\s+/g, ' ').trim(); return { scr: CBApp._t.screen, coin: T(s.querySelector('.cbcoinl')), tab: [...s.querySelectorAll('.tabs button')].map(b => b.textContent + (b.classList.contains('on') ? '*' : '')),
          h4: [...s.querySelectorAll('h4')].map(T), h3: [...s.querySelectorAll('h3.pkh3')].map(T),
          tiles: [...s.querySelectorAll('.dzt')].map(t => (t.dataset.ck || '-') + ':' + (t.dataset.id || 'base') + ':' + t.querySelector(':scope > img').getAttribute('src') + ':' + t.querySelector('em').textContent + (t.classList.contains('on') ? '*' : '') + (t.classList.contains('lk') ? '!' : '')),
          chips: [...s.querySelectorAll('.dzt')].map(t => { const c = t.querySelector(':scope > .rr'); return c ? c.textContent : ''; }),
          ask: (() => { const b = s.querySelector('[data-cb=pkask]'); return b ? T(b) + (b.disabled ? '!' : '') : null; })(), need: (() => { const n = s.querySelector('.pkbox .cbneed'); return n ? T(n) : ''; })(),
          box: [...s.querySelectorAll('.pkbox .pkc0, .pkbox .pkc1')].map(T), art: [...s.querySelectorAll('.pkbox .pkart img')].map(i => i.getAttribute('src') + ':' + i.naturalWidth), un: (() => { const u = s.querySelector('.pkun span'); return u ? T(u) : ''; })(),
          hist: [...s.querySelectorAll('.pkhi')].map(h => h.dataset.id + ':' + [...h.querySelectorAll('.cs img')].map(i => i.getAttribute('src').replace('cb_fc_', '').replace('_s.webp', '')).join(',') + ':' + h.querySelector(':scope > .rr').textContent + (h.classList.contains('un') ? '!' : '')) }; }"""
        MZ = """() => { const m = document.querySelector('#cbOv .cbmod.cbdzm'); if (!m) return null; return { h: m.querySelector('h3').textContent, img: (m.querySelector('.big img') || {}).getAttribute ? m.querySelector('.big img').getAttribute('src') : '', btns: [...m.querySelectorAll('.cbb')].map(b => b.textContent.trim() + (b.disabled ? '!' : '')), need: (m.querySelector('.cbneed') || {}).textContent || '', t: m.textContent.replace(/\\s+/g, ' ').trim() }; }"""
        # パックの 画面：いまの ようす・ことば・下の ボタン・5まい（おもての 絵:しるし:NEW／持って いる・^＝めくった・*＝くじの 演出）
        PK = """() => { const s = document.querySelector('#cbOv .cbpk'), p = CBApp._t.pk; return { scr: CBApp._t.screen, st: p && p.st, ready: p && p.ready, msg: s.querySelector('.pkmsg').textContent, hd: s.querySelector('.pkhd').textContent,
          ft: [...s.querySelectorAll('.pkft .cbb')].map(b => b.textContent.replace(/\\s+/g, '') + (b.disabled ? '!' : '')), need: (s.querySelector('.pkft .cbneed') || {}).textContent || '',
          cards: [...s.querySelectorAll('.pkc')].map(c => c.querySelector('.fr').getAttribute('src').replace('cb_fc_', '').replace('_s.webp', '') + ':' + c.querySelector('.rr').textContent + ':' + (c.querySelector('.nw') ? 'NEW' : c.querySelector('.hv').textContent) + (c.classList.contains('up') ? '^' : '') + (c.classList.contains('rv') ? '*' : '')),
          g: [...s.querySelectorAll('.pkc')].map(c => (c.className.match(/\\bg-(\\w+)/) || [])[1]), art: [...s.querySelectorAll('.pkart.big img')].map(i => i.className + ':' + i.getAttribute('src')), out: s.classList.contains('out') }; }"""
        S1 = """() => { const T = CBApp._t, s = T.state, ls = JSON.parse(localStorage.getItem('tengel.cb')), H = a => a.map(h => [h.id, h.g, h.k, h.cards.join(','), h.nw.map(x => x ? 1 : 0).join(''), h.v]);
          return { scr: T.screen, coin: s.coin, lsc: ls.coin, faces: s.faces, lsf: ls.faces, packs: s.packs, lsp: ls.packs, pkh: H(s.pkh), lsh: H(ls.pkh), q: (window.__q || []).length }; }"""
        NIDS = ['ka', 'kb', 'ma', 'mb', '1a', '1b', '2a', '2b', '3a', '3b', '4a', '4b', '5a', '5b', '6a', '6b', '7a', '7b']
        RIDS = [f'{i}r' for i in range(1, 8)]; GRIDS = ['kr', 'mr']; SRIDS = [f'{i}sr' for i in range(1, 8)]; GSRIDS = ['ksr', 'msr']
        PIDS = NIDS + RIDS + GRIDS + SRIDS + GSRIDS
        d0 = pg.evaluate(DZ)
        tw = pg.evaluate("() => [...document.querySelectorAll('#cbOv .cbdz .tabs button')].map(b => b.scrollWidth <= b.clientWidth + 1)")
        check(d0['scr'] == 'dz' and d0['coin'] == 'バトルコイン 0枚' and d0['tab'] == ['カードパック*', 'おもて', 'うら', 'ボード'] and len(tw) == 4 and all(tw),
              f'メニューの「デザインカスタム」→ はじめは「カードパック」の タブ（タブは カードパック・おもて・うら・ボード：字は 4つとも おさまる）（{d0["tab"]}）')
        check(d0['box'] == ['1パック 112枚・5まい入り', 'ノーマル 4まい ＋ くじの 1まい'] and d0['ask'] == '112枚で パックを 開ける!' and d0['need'] == 'あと 112枚 たりないよ（コンピュータに 勝つ・毎日の ログインボーナスで もらえるよ）'
              and not d0['un'] and not d0['hist'] and d0['art'] == ['cb_pack.webp:' + ('600' if HAVE else '0')],
              f'カードパック：パックの 絵（まさちゃんの 絵 cb_pack.webp）・「1パック 112枚・5まい入り」「ノーマル 4まい ＋ くじの 1まい」・コインが 0枚 なので「112枚で パックを 開ける」は 押せない・あと 112枚（{d0["box"]}・{d0["ask"]}）')
        check(d0['h3'] == ['この パックで 出る カード36種・持って いる 0／36'] and d0['h4'] == ['ノーマル4まいは ここから・くじ 30%・持って いる 0／18', 'レア（1〜7）くじ 40%・持って いる 0／7', '神様馬・幻の馬の レアくじ 10%・持って いる 0／2', '超レア（1〜7）くじ 15.65%・持って いる 0／7', '神様馬・幻の馬の 超レアくじ 4.35%・持って いる 0／2']
              and [t.split(':')[1] for t in d0['tiles']] == PIDS and all(t.endswith(':パックで 出る!') for t in d0['tiles']) and all(t.split(':')[2] == 'cb_fc_' + t.split(':')[1] + '_s.webp' for t in d0['tiles']) and d0['chips'] == ['N'] * 18 + ['R'] * 9 + ['SR'] * 9,
              f'「この パックで 出る カード」36種：ノーマル 18（N）・レア 1〜7（R）・神様馬／幻の馬の レア（R）・超レア 1〜7（SR）・神様馬／幻の馬の 超レア（SR）・くじの 確率と 持って いる 数（{d0["h3"]}・{d0["h4"]}）')
        shot(pg, 'cb_pk_tab')
        pg.locator('#cbOv .cbdz [data-cb=pkodds]').click(); pg.wait_for_timeout(150)
        od = pg.evaluate("""() => { const m = document.querySelector('#cbOv .cbmod.cbodm'); if (!m) return null; const r = m.querySelector('.pkod').getBoundingClientRect();
          return { h: m.querySelector('h3').textContent, cap: m.querySelector('.pkod caption').textContent, rows: [...m.querySelectorAll('.pkod tr')].map(r => r.querySelector('th').textContent + '|' + r.querySelector('td').textContent), t: m.textContent.replace(/\\s+/g, ' '),
            btn: [...m.querySelectorAll('.cbb')].map(b => b.textContent.trim()), w: [Math.round(r.left), Math.round(r.right), innerWidth] }; }""")
        check(od and od['h'] == '出る 確率' and od['cap'] == 'くじの 1まい（0〜229 の 番号を ひとしく 1つ）'
              and od['rows'] == ['ノーマル18種・番号 0〜68（69こ）|30%1種 1.67%', 'レア（1〜7）7種・番号 69〜160（92こ）|40%1種 5.71%', '神様馬・幻の馬の レア2種・番号 161〜183（23こ）|10%1種 5%', '超レア（1〜7）7種・番号 184〜219（36こ）|15.65%1種 2.24%', '神様馬・幻の馬の 超レア2種・番号 220〜229（10こ）|4.35%1種 2.17%']
              and '1パック 5まい：ノーマル 4まい（18種から 同じ 確率・1種 5.56%。同じ カードが かさなる ことも あるよ）＋ くじの 1まい' in od['t'] and 'レア ぜんぶ 50%（2パックに 1まい）・超レア ぜんぶ 20%（5パックに 1まい）' in od['t']
              and '23パック 開けても かならず 出る わけでは ないよ' in od['t'] and od['btn'] == ['とじる'] and od['w'][0] >= 0 and od['w'][1] <= od['w'][2],
              f'「出る 確率」：くじの 番号の はんいと 確率（1種ごとも）・ノーマル 4まいの 確率・どれも 平均（{od and od["rows"]}）')
        shot(pg, 'cb_pk_odds')
        pg.locator('#cbOv .cbmod [data-cb=dzback]').click(); pg.wait_for_timeout(80)
        mp = pg.evaluate("""() => { const T = CBApp._t, P = CBApp.PACK, c = {}; for (let k = 0; k < P.lot; k++) { const g = T.pkGroup(k); c[g] = (c[g] || 0) + 1; }
          const pools = {}; ['n', 'r', 'gr', 'sr', 'gsr'].forEach(g => { pools[g] = T.pkPool(g).map(f => f.id); });
          return { c: c, lot: P.lot, size: P.size, cost: P.cost, pools: pools, n: CBApp.FACES.length, edge: [0, 68, 69, 160, 161, 183, 184, 219, 220, 229].map(k => T.pkGroup(k)) }; }""")
        c = mp['c']
        check(mp['lot'] == 230 and mp['size'] == 5 and mp['cost'] == 112 and c == {'n': 69, 'r': 92, 'gr': 23, 'sr': 36, 'gsr': 10} and mp['edge'] == ['n', 'n', 'r', 'r', 'gr', 'gr', 'sr', 'sr', 'gsr', 'gsr']
              and c['n'] * 10 == 3 * 230 and c['r'] * 10 == 4 * 230 and (c['r'] + c['gr']) * 2 == 230 and (c['sr'] + c['gsr']) * 5 == 230 and c['gr'] * 10 == 230 and c['gsr'] * 23 == 230,
              f'くじの 番号 0〜229：ノーマル 69こ（30%）・レア 92こ（40%）・神様馬／幻の馬の レア 23こ（10%＝10パックに 1まい）・超レア 36こ（≒15.65%）・神様馬／幻の馬の 超レア 10こ（1/23）→ レア ぜんぶ 1/2・超レア ぜんぶ 1/5（丸めて いない）（{c}）')
        check(mp['pools'] == {'n': NIDS, 'r': RIDS, 'gr': GRIDS, 'sr': SRIDS, 'gsr': GSRIDS} and mp['n'] == 36 and len(set(PIDS)) == 36,
              f'グループの カード：ノーマル 18・レア 7・神様馬／幻の馬の レア 2・超レア 7・神様馬／幻の馬の 超レア 2 ＝ 36種（{[len(v) for v in mp["pools"].values()]}）')
        un = pg.evaluate("""() => { const T = CBApp._t, N = 230, R = 230000, c = new Array(N).fill(0); let bad = 0; CBApp._randInt = null;
          for (let i = 0; i < R; i++) { const x = T.randInt(N); if (x >= 0 && x < N && x === Math.floor(x)) c[x]++; else bad++; }
          const e = R / N, chi = c.reduce((a, x) => a + (x - e) * (x - e) / e, 0), g = {}; c.forEach((x, k) => { const q = T.pkGroup(k); g[q] = (g[q] || 0) + x; });
          return { bad: bad, chi: Math.round(chi * 10) / 10, g: g }; }""")
        gq = {k: v / 230000 for k, v in un['g'].items()}
        check(un['bad'] == 0 and 130 < un['chi'] < 345 and abs(gq['n'] - .3) < .005 and abs(gq['r'] - .4) < .005 and abs(gq['gr'] - .1) < .003 and abs(gq['sr'] - 36 / 230) < .004 and abs(gq['gsr'] - 10 / 230) < .0025,
              f'くじの 番号は ひとしく 出る（23万回：0〜229 の どれも ほぼ 1000回・カイ二乗 {un["chi"]}〈自由度 229〉・{"・".join(f"{k} {v * 100:.2f}%" for k, v in gq.items())}）')
        dd = pg.evaluate("""() => { const T = CBApp._t, R = 46000, c = {}, N = T.pkPool('n').map(f => f.id), P = {}; let bad = 0; CBApp._randInt = null; ['n', 'r', 'gr', 'sr', 'gsr'].forEach(g => { P[g] = T.pkPool(g).map(f => f.id); });
          for (let i = 0; i < R; i++) { const d = T.pkDraw(); if (d.cards.length !== 5 || d.g !== T.pkGroup(d.k) || d.cards.slice(0, 4).some(id => N.indexOf(id) < 0) || P[d.g].indexOf(d.cards[4]) < 0) bad++; d.cards.forEach(id => { c[id] = (c[id] || 0) + 1; }); }
          return { bad: bad, c: c }; }""")
        exp = {i: 46000 * 4.3 / 18 for i in NIDS}; exp.update({i: 46000 * .4 / 7 for i in RIDS}); exp.update({i: 46000 * .1 / 2 for i in GRIDS}); exp.update({i: 46000 * 36 / 230 / 7 for i in SRIDS}); exp.update({i: 46000 * 10 / 230 / 2 for i in GSRIDS})
        tol = lambda i: .05 if i in NIDS else .10 if i in RIDS + GRIDS else .15
        far = [f'{i} {dd["c"].get(i, 0)}／{exp[i]:.0f}' for i in PIDS if abs(dd['c'].get(i, 0) - exp[i]) > exp[i] * tol(i)]
        check(dd['bad'] == 0 and set(dd['c']) == set(PIDS) and not far, f'パックを 4万6千回：5まい（ノーマル 4まい ＋ くじの グループの 1まい）・どの カードも 決めた 確率どおりに 出る（はずれ {far}）')
        dr = pg.evaluate("""() => { const T = CBApp._t, run = seq => { const q = seq.slice(); CBApp._randInt = () => q.shift(); const d = T.pkDraw(); CBApp._randInt = null; return d.cards.join(',') + '|' + d.g + '|' + d.k + '|' + q.length; };
          return [run([0, 17, 5, 5, 0, 0]), run([1, 1, 1, 1, 68, 17]), run([2, 3, 4, 5, 69, 0]), run([0, 0, 0, 0, 160, 6]), run([0, 0, 0, 0, 161, 0]), run([0, 0, 0, 0, 183, 1]), run([0, 0, 0, 0, 184, 0]), run([0, 0, 0, 0, 219, 6]), run([0, 0, 0, 0, 220, 0]), run([0, 0, 0, 0, 229, 1])]; }""")
        check(dr == ['ka,7b,1b,1b,ka|n|0|0', 'kb,kb,kb,kb,7b|n|68|0', 'ma,mb,1a,1b,1r|r|69|0', 'ka,ka,ka,ka,7r|r|160|0', 'ka,ka,ka,ka,kr|gr|161|0', 'ka,ka,ka,ka,mr|gr|183|0', 'ka,ka,ka,ka,1sr|sr|184|0', 'ka,ka,ka,ka,7sr|sr|219|0', 'ka,ka,ka,ka,ksr|gsr|220|0', 'ka,ka,ka,ka,msr|gsr|229|0'],
              f'くじの さかい目：0・68＝ノーマル／69・160＝レア／161・183＝神様馬・幻の馬の レア／184・219＝超レア／220・229＝神様馬・幻の馬の 超レア・ノーマルは 同じ カードが かさなっても よい（{dr}）')
        # 開ける：たしかめる 窓 → うっかり 押し 防止 → すばやく 2回 → 1回 だけ（コイン・カード・記録を いっしょに）
        pg.evaluate("() => { const T = CBApp._t; T.state.coin = 300; T.save(); T.dz('p'); window.__q = [0, 0, 2, 17, 200, 2]; CBApp._randInt = n => (n === 1679616 ? 4242 : window.__q.shift()); }"); pg.wait_for_timeout(150)
        a1 = pg.evaluate(DZ)
        pg.locator('#cbOv .cbdz [data-cb=pkask]').click(); pg.wait_for_timeout(150); k1 = pg.evaluate(MZ)
        rq = pg.evaluate("() => document.querySelector('#cbOv .cbmod [data-cb=pkgo]').dataset.rq")
        ka = pg.evaluate("() => [...document.querySelectorAll('#cbOv .cbmod .pkart img')].map(i => i.getAttribute('src'))")
        check(a1['ask'] == '112枚で パックを 開ける' and not a1['need'] and k1 and k1['h'] == 'パックを 開ける？' and 'カードパック（5まい）を 1つ 開けるよ' in k1['t'] and '300枚→のこり 188枚' in k1['t'] and k1['btns'] == ['やめる', '開ける'] and re.fullmatch(r'p[0-9a-z]+-39u', rq or '') and ka == ['cb_pack.webp'],
              f'300枚 ある：「112枚で パックを 開ける」→ たしかめる 窓（パックの 絵・300枚 → のこり 188枚・やめる／開ける・この 窓だけの 番号 {rq}）')
        shot(pg, 'cb_pk_ask')
        pg.evaluate("() => { CBApp._guard = 1e9; }"); pg.locator('#cbOv .cbmod [data-cb=pkgo]').click(); pg.wait_for_timeout(100)
        g0 = pg.evaluate("() => { const s = CBApp._t.state; return [s.coin, s.pkh.length, s.faces.length, CBApp._t.screen, CBApp._t.modOn(), document.querySelector('#cbOv .cbmod [data-cb=pkgo]').disabled]; }")
        check(g0 == [300, 0, 0, 'dz', True, False], f'窓が 出て すぐ（0.45秒）は「開ける」を 受けつけない（うっかり 押し 防止）（{g0}）')
        pg.evaluate("() => { CBApp._guard = 0; const b = document.querySelector('#cbOv .cbmod [data-cb=pkgo]'); b.click(); b.click(); }"); pg.wait_for_timeout(150)
        p1 = pg.evaluate(S1); v1 = pg.evaluate(PK)
        check(p1['scr'] == 'pk' and p1['coin'] == 188 and p1['lsc'] == 188 and p1['faces'] == ['ka', 'ma', '7b', '3sr'] and p1['lsf'] == p1['faces'] and p1['packs'] == 1 and p1['lsp'] == 1
              and p1['pkh'] == [[rq, 'sr', 200, 'ka,ka,ma,7b,3sr', '10111', False]] and p1['lsh'] == p1['pkh'] and p1['q'] == 0,
              f'「開ける」を すばやく 2回：1回 だけ 開ける ＝ コイン 112枚（300 → 188）・5まい（朱の鳥居が 2まい：2まい目は 数えない → 持って いる カード 4種）・パックの 記録を いっしょに 保存（{p1["pkh"]}）')
        check(v1['st'] == 'pack' and v1['msg'] == 'タップで パックを 開けよう' and v1['ft'] == ['パックを開ける'] and v1['art'] == ['bd:cb_pack.webp', 'tp:cb_pack.webp'] and not v1['out'] and v1['g'] == ['n', 'n', 'n', 'n', 'sr'] and v1['hd'] == 'カードパック',
              f'パックの 画面：パックが 出る（タップで 開ける：上の ギザギザが 切れて とぶ 2まい かさね）（{v1["msg"]}）')
        shot(pg, 'cb_pk_pack')
        pg.evaluate("rq => { const b = document.createElement('button'); b.dataset.cb = 'pkgo'; b.dataset.rq = rq; document.querySelector('#cbOv').appendChild(b); b.click(); b.remove(); }", rq); pg.wait_for_timeout(150)
        p2 = pg.evaluate(S1); v2 = pg.evaluate(PK)
        check(p2 == p1 and v2['st'] == 'pack' and v2['scr'] == 'pk', f'同じ 番号の「開ける」が もう 1回 来ても 開けない（記録の 同じ 結果を 見せる・コインも 記録も そのまま）（{p2["coin"]}枚・{len(p2["pkh"])}こ）')
        pg.evaluate("() => { const b = document.createElement('button'); b.dataset.cb = 'pkgo'; b.dataset.rq = 'pzzz-1'; document.querySelector('#cbOv').appendChild(b); b.click(); b.remove(); }"); pg.wait_for_timeout(100)
        check(pg.evaluate(S1) == p1, '窓の 番号と ちがう「開ける」は 何も しない')
        # 開ける ところを 見ずに アプリを 閉じた → つぎに 開いた とき：メニューで 知らせる・タブの 上に「見る」→ 同じ 結果を 開ける ところから
        said(pg); pg.evaluate("() => { const T = CBApp._t; T.load(); T.menu(); }"); pg.wait_for_timeout(250); s3 = said(pg)
        check(any('🎴 開けた パックの 結果は\n「デザインカスタム」→「カードパック」で 見られるよ' in x for x in s3) and pg.evaluate("() => CBApp._t.state.pkh.length") == 1,
              f'開ける ところを 見おわる 前に 閉じた パック：つぎに 開いた ときの メニューで「開けた パックの 結果は …「カードパック」で 見られるよ」（{s3}）')
        pg.locator('#cbOv .cbmenu [data-cb=dz]').click(); pg.wait_for_timeout(200); a2 = pg.evaluate(DZ)
        check(a2['tab'][0] == 'カードパック*' and a2['coin'] == 'バトルコイン 188枚' and a2['un'] == '🎴 まだ 見おわって いない パックが 1つ あるよ' and a2['hist'] == [f'{rq}:ka,ka,ma,7b,3sr:SR!']
              and a2['h3'] == ['この パックで 出る カード36種・持って いる 4／36', 'パックの 記録開けた パック 1つ・さいごの 1つ'] and a2['h4'][0].endswith('持って いる 3／18') and a2['h4'][3].endswith('持って いる 1／7')
              and 'k:ka:cb_fc_ka_s.webp:持って いる' in a2['tiles'] and '3:3sr:cb_fc_3sr_s.webp:持って いる' in a2['tiles'],
              f'カードパックの タブ：「まだ 見おわって いない パックが 1つ」＋「見る」・パックの 記録・出た カードは「持って いる」（{a2["hist"]}）')
        shot(pg, 'cb_pk_unseen')
        pg.locator('#cbOv .cbdz .pkun [data-cb=pkhis]').click(); pg.wait_for_timeout(150); v3 = pg.evaluate(PK)
        check(v3['st'] == 'pack' and v3['art'] and [c.split(':')[0] for c in v3['cards']] == ['ka', 'ka', 'ma', '7b', '3sr'] and pg.evaluate(S1)['coin'] == 188, '「見る」→ 同じ パックを 開ける ところから（コインは もう へらない）')
        # 第4.189版（まさちゃん 16:35「一枚ずつパックから出て、カードが後ろに5枚並ぶ感じにして！」・16:37「背景に5枚カードが並んだらパックの袋は消えないと…」）：時計を 手で 進めて 1つずつ 見る
        pg.evaluate("() => CBApp._t.manual(true)"); pg.locator('#cbOv .cbpk .pkart.big').click()
        DEAL = """() => { const p = CBApp._t.pk, a = document.querySelector('#cbOv .cbpk .pkart.big'), cs = [...document.querySelectorAll('#cbOv .cbpk .pkc')];
          return [p.st, cs.filter(c => c.classList.contains('got')).length, a.classList.contains('gone'), cs.filter(c => c.classList.contains('up')).length]; }"""
        seq = []
        for _ in range(800):
            pg.evaluate("async () => { CBApp._t.tick(1); for (let i = 0; i < 20; i++) await null; }"); x = pg.evaluate(DEAL)
            if not seq or seq[-1] != x: seq.append(x)
            if pg.evaluate("() => CBApp._t.pk.ready"): break
        zi = pg.evaluate("() => getComputedStyle(document.querySelector('#cbOv .cbpk .pkart.big')).zIndex")
        pg.evaluate("() => CBApp._t.manual(false)")
        gots = [x[1] for x in seq]
        check(seq and seq[0][:2] == ['rip', 0] and sorted(set(gots)) == [0, 1, 2, 3, 4, 5] and all(0 <= b_ - a_ <= 1 for a_, b_ in zip(gots, gots[1:])) and [x[1] for x in seq if x[0] == 'deal'][:5] == [1, 2, 3, 4, 5]
              and all((not x[2]) or x[1] == 5 for x in seq) and all(x[3] == 0 or x[2] for x in seq) and seq[-1] == ['out', 5, True, 4] and zi == '5',
              f'パックを タップ → 上が 切れる → カードが 1まいずつ 出て パックの うしろに ならぶ（パックが 前：z-index {zi}）→ 5まい ならんでから パックが 消える → それから めくる（{seq}）')
        pg.wait_for_timeout(100); v4 = pg.evaluate(PK)
        gl = pg.evaluate("() => [...document.querySelectorAll('#cbOv .cbpk .pkc')].map(c => getComputedStyle(c.querySelector('.gl')).animationName)")
        check(v4['st'] == 'out' and v4['out'] and v4['msg'] == 'さいごの 1まい（くじ）… タップで めくろう！' and v4['ft'] == ['さいごの1まいをめくる'] and [c.endswith('^') for c in v4['cards']] == [True] * 4 + [False] and gl == ['none'] * 4 + ['pkgl'],
              f'パックを タップ → 5まいが 出て ふせて ならぶ → ノーマル 4まいを めくる → さいごの 1まい（くじ）は ふせた まま（超レアの くじ：うらの まわりが ゆっくり ひかる）（{v4["cards"]}）')
        shot(pg, 'cb_pk_ready')
        pg.locator('#cbOv .cbpk .pkc[data-i="4"]').click()
        pg.wait_for_function("() => CBApp._t.pk && CBApp._t.pk.st === 'done'", timeout=10000); pg.wait_for_timeout(150); v5 = pg.evaluate(PK); s5 = pg.evaluate(S1)
        check(v5['msg'] == '🌟 超レア！『碧玉の温室』\nNEW 4まい！（持って いる カード 4／36）' and v5['cards'] == ['ka:N:NEW^', 'ka:N:持って いる^', 'ma:N:NEW^', '7b:N:NEW^', '3sr:SR:NEW^*'] and v5['ft'] == ['とじる', 'もう1パック112枚'] and not v5['need']
              and s5['pkh'][0][5] is True and s5['lsh'][0][5] is True and s5['coin'] == 188,
              f'さいごの 1まいを タップ → めくる（超レア：光の すじ・光が ひろがる）→「🌟 超レア！『碧玉の温室』」・NEW 4まい・2まい目の 朱の鳥居は「持って いる」・見おわった ことを 記録（{v5["msg"]!r}・{v5["cards"]}）')
        shot(pg, 'cb_pk_done')
        pg.locator('#cbOv .cbpk .pkc[data-i="4"]').click(); pg.wait_for_timeout(150); z7 = pg.evaluate(MZ)
        said(pg); pg.locator('#cbOv .cbmod [data-cb=dzuse]').click(); pg.wait_for_timeout(150); s7 = said(pg)
        f7 = pg.evaluate("() => [CBApp._t.screen, CBApp._t.state.face, JSON.parse(localStorage.getItem('tengel.cb')).face, CBApp._t.modOn()]")
        check(z7 and z7['h'] == '碧玉の温室3 の カードの おもて・超レア' and z7['img'] == 'cb_fc_3sr_c.webp' and z7['btns'] == ['この デザインを 使う', 'もどる'] and f7 == ['pk', {'3': '3sr'}, {'3': '3sr'}, False] and any('3 の カードの おもてを『碧玉の温室』に したよ' in x for x in s7),
              f'出た カードを タップ → 大きい 絵・「この デザインを 使う」→ すぐ 使える（パックの 画面の まま）（{f7}）')
        pg.evaluate("() => { window.__q = [5, 5, 5, 5, 229, 1]; }")
        pg.locator('#cbOv .cbpk [data-cb=pkmore]').click(); pg.wait_for_timeout(150); k8 = pg.evaluate(MZ)
        pg.locator('#cbOv .cbmod [data-cb=pkgo]').click(); pg.wait_for_timeout(150)
        pg.locator('#cbOv .cbpk .pkft [data-cb=pkrip]').click(); pg.wait_for_function("() => CBApp._t.pk && CBApp._t.pk.ready", timeout=10000)
        gl8 = pg.evaluate("() => getComputedStyle(document.querySelector('#cbOv .cbpk .pkc[data-i=\"4\"] .gl')).animationName")
        pg.locator('#cbOv .cbpk [data-cb=pklast]').click(); pg.wait_for_function("() => CBApp._t.pk && CBApp._t.pk.st === 'done'", timeout=10000); pg.wait_for_timeout(150)
        v8 = pg.evaluate(PK); s8 = pg.evaluate(S1); rq2 = s8['pkh'][-1][0]
        check('188枚→のこり 76枚' in k8['t'] and s8['coin'] == 76 and s8['lsc'] == 76 and s8['faces'] == ['ka', 'ma', '7b', '3sr', '1b', 'msr'] and s8['packs'] == 2 and len(s8['pkh']) == 2 and s8['pkh'][1][1:] == ['gsr', 229, '1b,1b,1b,1b,msr', '10001', True] and rq2 != rq
              and v8['msg'] == '🌟 幻の馬の 超レア！『紫電の魔城』\nNEW 2まい！（持って いる カード 6／36）' and v8['ft'] == ['とじる', 'もう1パック112枚!'] and v8['need'] == 'あと 36枚 たりないよ（コンピュータに 勝つ・毎日の ログインボーナスで もらえるよ）' and gl8 == 'pkgl' and v8['g'][4] == 'gsr',
              f'「もう 1パック」（188 → 76枚）・下の「パックを 開ける」「さいごの 1まいを めくる」でも 開けられる：幻の馬の 超レア『紫電の魔城』・同じ ノーマルが 4まい（数は 1）・のこり 76枚 なので「もう 1パック」は 押せない（あと 36枚）（{v8["msg"]!r}）')
        shot(pg, 'cb_pk_gsr')
        pg.locator('#cbOv .cbpk [data-cb=pkx]').click(); pg.wait_for_timeout(200); a9 = pg.evaluate(DZ)
        check(a9['scr'] == 'dz' and a9['tab'][0] == 'カードパック*' and not a9['un'] and a9['hist'] == [f'{rq2}:1b,1b,1b,1b,msr:SR', f'{rq}:ka,ka,ma,7b,3sr:SR'] and a9['h3'][1] == 'パックの 記録開けた パック 2つ・さいごの 2つ' and a9['ask'] == '112枚で パックを 開ける!' and 'あと 36枚' in a9['need'],
              f'「とじる」→ カードパックの タブ：パックの 記録（あたらしい 順）・見おわって いない パックは ない（{a9["hist"]}）')
        pg.locator(f'#cbOv .cbdz .pkhi[data-id="{rq}"]').click(); pg.wait_for_timeout(200); v9 = pg.evaluate(PK)
        check(v9['st'] == 'done' and not v9['art'] and v9['out'] and v9['cards'] == ['ka:N:NEW^', 'ka:N:持って いる^', 'ma:N:NEW^', '7b:N:NEW^', '3sr:SR:NEW^'] and re.fullmatch(r'カードパック\d+/\d+ \d+:\d\d に 開けた パック', v9['hd']) and v9['msg'].startswith('🌟 超レア！『碧玉の温室』\nNEW 4まい！'),
              f'記録を タップ → その パックを もう 1回（5まい ぜんぶ おもて・開けた 日時）（{v9["hd"]}）')
        shot(pg, 'cb_pk_static')
        pg.locator('#cbOv .cbpk [data-cb=pkx]').click(); pg.wait_for_timeout(150)
        # 保存が できない とき：ぜんぶ もとの まま（コイン・カード・記録は いっしょに 決まる）
        pg.evaluate("() => { const T = CBApp._t; T.state.coin = 500; T.save(); T.dz('p'); window.__q = [0, 0, 0, 0, 100, 0]; }"); pg.wait_for_timeout(120)
        r0 = pg.evaluate(S1)
        for how in ('throw', 'noop'):
            pg.locator('#cbOv .cbdz [data-cb=pkask]').click(); pg.wait_for_timeout(120); said(pg)
            pg.evaluate("how => { window.__si = Storage.prototype.setItem; Storage.prototype.setItem = function (k, v) { if (k === 'tengel.cb') { if (how === 'throw') throw new Error('QuotaExceededError'); return; } return window.__si.call(this, k, v); }; }", how)
            pg.locator('#cbOv .cbmod [data-cb=pkgo]').click(); pg.wait_for_timeout(150)
            pg.evaluate("() => { Storage.prototype.setItem = window.__si; }")
            rr = pg.evaluate(S1); tt = said(pg)
            check({k: v for k, v in rr.items() if k != 'q'} == {k: v for k, v in r0.items() if k != 'q'} and rr['q'] == 0 and any('保存が できなかったので、パックは 開けなかったよ\n（コインは へって いないよ）' in x for x in tt) and not pg.evaluate("() => CBApp._t.modOn()"),
                  f'保存が できない とき（{"書けない" if how == "throw" else "書いた 中身が のこらない"}）：パックは 開けない・コイン・カード・記録は ぜんぶ もとの まま（{rr["coin"]}枚・{len(rr["pkh"])}こ）')
            pg.evaluate("() => { window.__q = [0, 0, 0, 0, 100, 0]; }"); pg.wait_for_timeout(900)      # ふきだしが 消えて から（同じ ことばの ふきだしを 2回目も 数える）
        # 「おもて」の タブ：パックで 集めた カードを 使う（コインでは 解放しない）
        pg.evaluate("() => { const T = CBApp._t; T.state.coin = 0; T.save(); }")
        pg.locator('#cbOv .cbdz [data-cb=dztab][data-t=f]').click(); pg.wait_for_timeout(150); f0 = pg.evaluate(DZ)
        check(f0['tab'] == ['カードパック', 'おもて*', 'うら', 'ボード'] and f0['h4'] == ['神様馬持って いる 1／4', '幻の馬持って いる 2／4', '1 の カード持って いる 1／4', '2 の カード持って いる 0／4', '3 の カード持って いる 1／4', '4 の カード持って いる 0／4', '5 の カード持って いる 0／4', '6 の カード持って いる 0／4', '7 の カード持って いる 1／4']
              and len(f0['tiles']) == 45 and f0['tiles'][:5] == ['k:base:cb_sk.webp:使って いる*', 'k:ka:cb_fc_ka_s.webp:持って いる', 'k:kb:cb_fc_kb_s.webp:パックで 出る!', 'k:kr:cb_fc_kr_s.webp:パックで 出る!', 'k:ksr:cb_fc_ksr_s.webp:パックで 出る!'] and f0['chips'][:5] == ['', 'N', 'N', 'R', 'SR']
              and 'm:msr:cb_fc_msr_s.webp:持って いる' in f0['tiles'] and '3:3sr:cb_fc_3sr_s.webp:使って いる*' in f0['tiles'] and '3:base:cb_s3.webp:持って いる' in f0['tiles'],
              f'「おもて」の タブ：9種類 ×（いつもの ＋ ノーマル 2・レア 1・超レア 1）＝ 45・N／R／SR の しるし・持って いない ものは「パックで 出る」（{f0["h4"]}）')
        shot(pg, 'cb_dz_faces')
        pg.locator('#cbOv .cbdz .dzt[data-id="ksr"]').click(); pg.wait_for_timeout(150); z8 = pg.evaluate(MZ)
        check(z8 and z8['h'] == '白金の聖殿神様馬の おもて・超レア' and z8['img'] == 'cb_fc_ksr_c.webp' and z8['btns'] == ['カードパックへ', 'もどる'] and z8['need'] == 'カードパックで 出るよ（神様馬・幻の馬の 超レア）',
              f'持って いない おもてを タップ：大きい 絵・「カードパックで 出るよ（神様馬・幻の馬の 超レア）」・「カードパックへ」（コインで 解放は ない）（{z8 and z8["btns"]}）')
        pg.locator('#cbOv .cbmod [data-cb=dztab][data-t=p]').click(); pg.wait_for_timeout(150)
        check(pg.evaluate(DZ)['tab'][0] == 'カードパック*' and not pg.evaluate("() => CBApp._t.modOn()"), '「カードパックへ」→ カードパックの タブ')
        pg.locator('#cbOv .cbdz .dzt[data-id="kr"]').click(); pg.wait_for_timeout(120); z9 = pg.evaluate(MZ); pg.locator('#cbOv .cbmod [data-cb=dzback]').click(); pg.wait_for_timeout(80)
        check(z9 and z9['h'] == '聖光の神馬神様馬の おもて・レア' and z9['btns'] == ['もどる'] and z9['need'] == 'カードパックで 出るよ（神様馬・幻の馬の レア）', f'カードパックの タブで 持って いない カードを タップ：大きい 絵と どの くじで 出るか（{z9 and z9["need"]}）')
        pg.evaluate("() => { const T = CBApp._t; T.state.coin = 999; T.save(); }")
        bad = pg.evaluate("""() => { const o = document.querySelector('#cbOv'), r = []; for (const [cb, ck, id] of [['dzopen', 'k', 'kb'], ['dzgo', 'k', 'kb'], ['dzopen', '7', '7sr'], ['dzgo', '7', '7sr']]) {
          const b = document.createElement('button'); b.dataset.cb = cb; b.dataset.ck = ck; b.dataset.id = id; o.appendChild(b); b.click(); b.remove(); r.push(CBApp._t.modOn()); } const s = CBApp._t.state; return [r, s.coin, s.faces.slice()]; }""")
        check(bad == [[False, False, False, False], 999, ['ka', 'ma', '7b', '3sr', '1b', 'msr']], f'おもては コインでは 解放できない（前の 版の「解放」の ボタンが 来ても 何も しない）（{bad}）')
        # 「うら」の タブ（いままで どおり コインで 解放）
        pg.evaluate("() => { const T = CBApp._t; T.state.coin = 300; T.save(); }")
        pg.locator('#cbOv .cbdz [data-cb=dztab][data-t=b]').click(); pg.wait_for_timeout(150); d2 = pg.evaluate(DZ)
        check(d2['tab'] == ['カードパック', 'おもて', 'うら*', 'ボード'] and d2['h4'] == ['カードの うら1つ 300枚'] and len(d2['tiles']) == 8 and d2['tiles'][0] == '-:base:cb_sb.webp:使って いる*' and all(t.endswith('300枚!') for t in d2['tiles'][1:])
              and [t.split(':')[1] for t in d2['tiles'][1:]] == ['sky', 'star', 'ice', 'wa', 'ori', 'crown', 'heart'] and d2['chips'] == [''] * 8,
              f'「うら」：いつもの ＋ 7種（1つ 300枚：いままで どおり コインで 解放）（{[t.split(":")[1] for t in d2["tiles"]]}）')
        shot(pg, 'cb_dz_backs')
        pg.locator('#cbOv .cbdz .dzt[data-id="sky"]').click(); pg.wait_for_timeout(120); pg.locator('#cbOv .cbmod [data-cb=dzopen]').click(); pg.wait_for_timeout(120); z3 = pg.evaluate(MZ)
        pg.evaluate("() => { CBApp._guard = 1e9; }"); pg.locator('#cbOv .cbmod [data-cb=dzgo]').click(); pg.wait_for_timeout(100); g1 = pg.evaluate("() => [CBApp._t.state.coin, CBApp._t.state.backs.slice()]")
        said(pg); pg.evaluate("() => { CBApp._guard = 0; }"); pg.locator('#cbOv .cbmod [data-cb=dzgo]').click(); pg.wait_for_timeout(200)
        d3 = pg.evaluate(DZ); tt = said(pg)
        pg.locator('#cbOv .cbdz .dzt[data-id="star"]').click(); pg.wait_for_timeout(120); z4 = pg.evaluate(MZ); pg.locator('#cbOv .cbmod [data-cb=dzback]').click(); pg.wait_for_timeout(80)
        check(z3['h'] == '解放する？' and '『天馬の光』（カードの うら）を 解放するよ' in z3['t'] and '300枚→のこり 0枚' in z3['t'] and z3['btns'] == ['やめる', '解放する'] and g1 == [300, []]
              and d3['coin'] == 'バトルコイン 0枚' and d3['tiles'][1] == '-:sky:cb_bk_sky_s.webp:使って いる*' and d3['tiles'][0] == '-:base:cb_sb.webp:持って いる' and any('『天馬の光』を 解放したよ！' in x for x in tt)
              and z4['btns'] == ['バトルコイン 300枚で 解放!', 'もどる'] and 'あと 300枚 たりないよ' in z4['need'] and pg.evaluate("() => [CBApp._t.state.backs, CBApp._t.state.back]") == [['sky'], 'sky'],
              f'うら『天馬の光』：たしかめる 窓（窓が 出て すぐは 受けつけない）→ 300枚で 解放（300 → 0）・すぐ その うらに・ほかは あと 300枚（{d3["coin"]}）')
        pg.locator('#cbOv .cbdz [data-cb=dztab][data-t=f]').click(); pg.wait_for_timeout(120)
        pg.locator('#cbOv .cbdz .dzt[data-id="ka"]').click(); pg.wait_for_timeout(120); z10 = pg.evaluate(MZ); pg.locator('#cbOv .cbmod [data-cb=dzuse]').click(); pg.wait_for_timeout(150)
        check(z10['btns'] == ['この デザインを 使う', 'もどる'] and pg.evaluate("() => CBApp._t.state.face") == {'k': 'ka', '3': '3sr'}, 'パックで 出た『朱の鳥居』を「この デザインを 使う」（コインは 使わない）')
        pg.locator('#cbOv .cbdz [data-cb=dzx]').click(); pg.wait_for_timeout(150)
        check(pg.evaluate("() => CBApp._t.screen") == 'menu' and 'バトルコイン 0枚' in pg.evaluate("() => document.querySelector('#cbOv .cbmenu .cbcoinl').textContent"), '「← もどる」→ メニュー（コインの 数も 0枚）')
        start(pg, 'k1234', '15677')
        IM = """() => ({ deck: document.querySelector('#cbOv .cbdeck img').getAttribute('src'), op: [...document.querySelectorAll('#cbOv .cbohand img')].map(i => i.getAttribute('src')), my: [...document.querySelectorAll('#cbOv .cbhand .cbc')].map(c => c.dataset.ck + '=' + c.querySelector('img').getAttribute('src')) })"""
        im = pg.evaluate(IM)
        check(im['deck'] == 'cb_bk_sky_d.webp' and set(im['op']) == {'cb_bk_sky_s.webp'} and 'k=cb_fc_ka_s.webp' in im['my'] and '3=cb_fc_3sr_s.webp' in im['my'] and '1=cb_s1.webp' in im['my'] and not any('cb_sk.webp' in x for x in im['my']),
              f'対戦：山札と 相手の 手札は えらんだ うら『天馬の光』・神様馬は パックの『朱の鳥居』・3 は 超レアの『碧玉の温室』・ほかは いつもの（{im["deck"]}・{im["my"]}）')
        shot(pg, 'cb_dz_game')
        pg.evaluate("() => { window.__seen = []; }")
        pg.locator('#cbOv .cbhand .cbc[data-ck="k"]').click(); pg.wait_for_timeout(80); pg.locator('#cbOv .cbmod [data-cb=set]').click(); idle(pg)
        opp(pg, {'t': 'set', 'k': 1})
        seen = pg.evaluate("() => window.__seen")
        check(any('勝ち！' in x and 'cb_fc_ka_c.webp,cb_c1.webp' in x for x in seen) and pg.evaluate(V)['my']['wins'] == 1, f'めくった とき：神様馬は えらんだ おもての 大きい 絵（{seen[-1] if seen else None}）')
        pg.evaluate("() => CBApp._t.menu()"); pg.wait_for_timeout(150)
        pg.locator('#cbOv .cbmenu [data-cb=dz]').click(); pg.wait_for_timeout(150); pg.locator('#cbOv .cbdz [data-cb=dztab][data-t=f]').click(); pg.wait_for_timeout(150)
        pg.locator('#cbOv .cbdz .dzt[data-ck="k"][data-id=""]').click(); pg.wait_for_timeout(120); z5 = pg.evaluate(MZ)
        pg.locator('#cbOv .cbmod [data-cb=dzuse]').click(); pg.wait_for_timeout(150)
        st2 = pg.evaluate("() => [CBApp._t.state.coin, CBApp._t.state.face, CBApp._t.state.faces.length, JSON.parse(localStorage.getItem('tengel.cb')).face]")
        check(z5['btns'] == ['この デザインを 使う', 'もどる'] and st2 == [0, {'3': '3sr'}, 6, {'3': '3sr'}] and pg.evaluate(DZ)['tiles'][0] == 'k:base:cb_sk.webp:使って いる*', f'いつもの に もどす：コインは 使わない・集めた カードは のこる（{st2}）')
        pg.evaluate("() => { const s = JSON.parse(localStorage.getItem('tengel.cb')); s.faces = ['zz', 'ka', 'ka']; s.face = { k: 'kb', '1': 'ka', m: 'ma' }; s.backs = ['sky', 'nope']; s.back = 'ice'; localStorage.setItem('tengel.cb', JSON.stringify(s)); CBApp._t.load(); }")
        st3 = pg.evaluate("() => { const s = CBApp._t.state; return [s.faces, s.face, s.backs, s.back]; }")
        check(st3 == [['ka'], {}, ['sky'], ''], f'おぼえた 中身が おかしい ときは なおす（ない 名前・持って いない もの・ちがう 種類は すてる）（{st3}）')
        pg.evaluate("""() => { const s = JSON.parse(localStorage.getItem('tengel.cb')), ok = { id: 'pok', t: 5, g: 'r', k: 100, cards: ['ka', 'kb', 'ma', 'mb', '3r'], v: 1 };
          s.pkh = [null, 5, { id: 'p1', g: 'r', cards: ['ka', 'kb', 'ma', 'mb'] }, { id: 'p2', g: 'r', cards: ['ka', 'kb', 'ma', 'mb', 'zz'] }, { id: 'p3', g: 'x', cards: ['ka', 'kb', 'ma', 'mb', '3r'] }, { id: 7, g: 'r', cards: ['ka', 'kb', 'ma', 'mb', '3r'] }, ok]; s.packs = 'abc';
          localStorage.setItem('tengel.cb', JSON.stringify(s)); CBApp._t.load(); }""")
        ph = pg.evaluate("() => [CBApp._t.state.pkh, CBApp._t.state.packs]")
        check(ph == [[{'id': 'pok', 't': 5, 'g': 'r', 'k': 100, 'cards': ['ka', 'kb', 'ma', 'mb', '3r'], 'nw': [False] * 5, 'v': True}], 1],
              f'パックの 記録が おかしい ときは なおす（5まい ない・ない カード・ない グループ・番号が 文字で ない ものは すてる・開けた 数は 記録の 数より 少なく しない）（{ph}）')
        pg.evaluate("""() => { const s = JSON.parse(localStorage.getItem('tengel.cb')); s.pkh = []; for (let i = 0; i < 105; i++) s.pkh.push({ id: 'p' + i, t: i, g: 'n', k: 0, cards: ['ka', 'ka', 'ka', 'ka', 'ka'], nw: [false, false, false, false, false], v: true });
          s.packs = 105; s.coin = 112; localStorage.setItem('tengel.cb', JSON.stringify(s)); CBApp._t.load(); CBApp._t.dz('p'); window.__q = [1, 1, 1, 1, 0, 0]; }"""); pg.wait_for_timeout(150)
        pm = pg.evaluate("() => [CBApp._t.state.pkh.length, CBApp._t.state.pkh[0].id, CBApp._t.state.pkh[99].id, CBApp._t.state.packs]")
        pg.locator('#cbOv .cbdz [data-cb=pkask]').click(); pg.wait_for_timeout(120); pg.locator('#cbOv .cbmod [data-cb=pkgo]').click(); pg.wait_for_timeout(150)
        p100 = pg.evaluate(S1)
        check(pm == [100, 'p5', 'p104', 105] and len(p100['pkh']) == 100 and p100['pkh'][0][0] == 'p6' and p100['pkh'][-1][1:4] == ['n', 0, 'kb,kb,kb,kb,ka'] and p100['packs'] == 106 and p100['coin'] == 0 and p100['lsh'] == p100['pkh'],
              f'パックの 記録は さいごの 100こ まで（開けた 数は そのまま 105 → 106・のこりの コインが ちょうど 112枚でも 開けられる）（{pm}・{len(p100["pkh"])}こ）')
        pg.evaluate("() => CBApp._t.menu()"); pg.wait_for_timeout(150)
        pg.evaluate("() => { const s = JSON.parse(localStorage.getItem('tengel.cb')); delete s.pkh; delete s.packs; s.faces = ['ka', '6a', 'mb']; s.face = { k: 'ka', '6': '6a' }; localStorage.setItem('tengel.cb', JSON.stringify(s)); CBApp._t.load(); }")
        mg = pg.evaluate("() => { const s = CBApp._t.state; return [s.faces, s.face, s.pkh, s.packs]; }")
        check(mg == [['ka', '6a', 'mb'], {'k': 'ka', '6': '6a'}, [], 0], f'前の 版で コインで 解放した おもては そのまま 持って いる（使って いる ものも そのまま・パックの 記録は 空から）（{mg}）')
        pg.evaluate("() => { CBApp._randInt = null; const T = CBApp._t; T.state.backs = []; T.state.faces = []; T.state.back = ''; T.state.face = {}; T.state.pkh = []; T.state.packs = 0; T.save(); T.menu(); }")

        print('■ プレイボード（第4.185版・まさちゃん 23:20「バトルコインで、プレイボード7種類購入できるようにして！ 1個バトルコイン300枚で解放できるようにして！」）')
        BIMG = "() => { const b = document.querySelector('#cbOv .cbboard'), f = getComputedStyle(b.querySelector('.cbfire')), i = b.querySelector(':scope > img'); return [i.getAttribute('src'), b.classList.contains('cust'), f.display, f.animationName, i.complete && i.naturalWidth, b.classList.contains('dl')]; }"
        start(pg, '12345', '12345'); b0 = pg.evaluate(BIMG); pg.evaluate("() => CBApp._t.menu()"); pg.wait_for_timeout(100)
        check(b0[:4] == ['cb_board.webp', False, 'block', 'cbfire'] and (not HAVE or b0[4] == 1254), f'はじめは いつもの ボード（夜の 光・火の あかりの ゆれ あり）（{b0}）')
        pg.evaluate("() => { const T = CBApp._t; T.state.coin = 250; T.state.boards = []; T.state.board = ''; T.save(); T.menu(); }"); pg.wait_for_timeout(150)
        pg.locator('#cbOv .cbmenu [data-cb=dz]').click(); pg.wait_for_timeout(200)
        pg.locator('#cbOv .cbdz [data-cb=dztab][data-t=d]').click(); pg.wait_for_timeout(250); e0 = pg.evaluate(DZ)
        bn = pg.evaluate("() => [...document.querySelectorAll('#cbOv .cbdz .dzt span')].map(s => s.textContent)")
        tw = pg.evaluate("() => [...document.querySelectorAll('#cbOv .cbdz .tabs button')].map(b => b.scrollWidth <= b.clientWidth + 1)")
        ti = pg.evaluate("() => [...document.querySelectorAll('#cbOv .cbdz .dzt > img')].map(i => { const r = i.getBoundingClientRect(); return Math.round(r.width / r.height * 100) / 100; })")
        check(e0['tab'] == ['カードパック', 'おもて', 'うら', 'ボード*'] and all(tw) and e0['h4'] == ['プレイボード1つ 300枚'] and len(e0['tiles']) == 8 and e0['tiles'][0] == '-:base:cb_board.webp:使って いる*'
              and [t.split(':')[1] for t in e0['tiles'][1:]] == ['marble', 'frost', 'sakura', 'violet', 'crimson', 'starry', 'steam'] and all(t.endswith('300枚!') for t in e0['tiles'][1:])
              and all(t.split(':')[2] == 'cb_bd_' + t.split(':')[1] + '_s.webp' for t in e0['tiles'][1:]) and bn == ['いつもの', '白亜の宮殿', '蒼氷の宮', '桜の舞踏会', '紫月の夜', '紅蓮の闘技場', '黄金の星空', '歯車の工房'] and all(1.7 <= r <= 1.85 for r in ti),
              f'デザインカスタムの 4つ目の タブ「ボード」（第4.189版：タブの 字は 4つとも おさまる）：いつもの ＋ 7種（1つ 300枚・横長の 絵）（{bn}）')
        shot(pg, 'cb_dz_boards')
        pg.locator('#cbOv .cbdz .dzt[data-cb=bdi][data-id="sakura"]').click(); pg.wait_for_timeout(150); y1 = pg.evaluate(MZ)
        bg = pg.evaluate("() => { const r = document.querySelector('#cbOv .cbmod .big.bd').getBoundingClientRect(); return [Math.round(r.left), Math.round(r.right), Math.round(r.width / r.height * 100) / 100, innerWidth]; }")
        check(y1 and y1['h'] == '桜の舞踏会プレイボード' and y1['img'] == 'cb_bd_sakura.webp' and y1['btns'] == ['バトルコイン 300枚で 解放!', 'もどる'] and y1['need'] == 'あと 50枚 たりないよ（コンピュータに 勝つ・毎日の ログインボーナスで もらえるよ）'
              and bg[0] >= 0 and bg[1] <= bg[3] and 1.7 <= bg[2] <= 1.85,
              f'コインが 足りない（250枚）：大きい ボードの 絵・「バトルコイン 300枚で 解放」は 押せない・あと 50枚（{y1 and y1["btns"]}・{bg}）')
        shot(pg, 'cb_dz_board_item')
        pg.locator('#cbOv .cbmod [data-cb=dzback]').click(); pg.wait_for_timeout(80)
        pg.evaluate("() => { CBApp._t.state.coin = 700; }"); pg.locator('#cbOv .cbdz [data-cb=dztab][data-t=d]').click(); pg.wait_for_timeout(150)
        pg.locator('#cbOv .cbdz .dzt[data-cb=bdi][data-id="sakura"]').click(); pg.wait_for_timeout(120); y2 = pg.evaluate(MZ)
        pg.locator('#cbOv .cbmod [data-cb=bdopen]').click(); pg.wait_for_timeout(120); y3 = pg.evaluate(MZ)
        check(y2['btns'] == ['バトルコイン 300枚で 解放', 'もどる'] and y3['h'] == '解放する？' and '『桜の舞踏会』（プレイボード）を 解放するよ' in y3['t'] and '700枚→のこり 400枚' in y3['t'] and y3['btns'] == ['やめる', '解放する'] and y3['img'] == 'cb_bd_sakura_s.webp',
              f'700枚 ある：「解放」→ たしかめる 窓（700枚 → のこり 400枚・やめる／解放する）（{y3["t"]}）')
        pg.evaluate("() => { CBApp._guard = 1e9; }"); pg.locator('#cbOv .cbmod [data-cb=bdgo]').click(); pg.wait_for_timeout(100); h0 = pg.evaluate("() => [CBApp._t.state.coin, CBApp._t.state.boards.slice()]")
        pg.evaluate("() => { CBApp._guard = 0; }"); pg.locator('#cbOv .cbmod [data-cb=bdgo]').click(); pg.wait_for_timeout(200)
        e1 = pg.evaluate(DZ); s1 = pg.evaluate("() => { const s = CBApp._t.state, ls = JSON.parse(localStorage.getItem('tengel.cb')); return [s.coin, s.boards, s.board, ls.coin, ls.boards, ls.board]; }"); tt = pg.evaluate(TOAST)
        check(h0 == [700, []] and s1 == [400, ['sakura'], 'sakura', 400, ['sakura'], 'sakura'] and e1['tiles'][0] == '-:base:cb_board.webp:持って いる' and e1['tiles'][3] == '-:sakura:cb_bd_sakura_s.webp:使って いる*'
              and tt == '『桜の舞踏会』を 解放したよ！\nプレイボードが この デザインに なったよ' and not pg.evaluate("() => CBApp._t.modOn()"),
              f'「解放する」：窓が 出て すぐは 受けつけない → 300枚 へって（700 → 400）解放・すぐ その ボードに・おぼえる（{s1}）')
        pg.locator('#cbOv .cbdz [data-cb=dzx]').click(); pg.wait_for_timeout(100)
        start(pg, '12345', '12345'); pg.wait_for_timeout(300 if HAVE else 0); b1 = pg.evaluate(BIMG)
        check(b1[:4] == ['cb_bd_sakura.webp', True, 'none', 'cbfire'] and (not HAVE or b1[4] == 1254) and b1[5] is True, f'対戦の ボードが『桜の舞踏会』（まさちゃんの 絵の まま：ボードの 上の 火の あかりの ゆれは 出さない・第4.186版の 新しい 絵：山札は 左へ〈dl〉）（{b1}）')
        GEO = "() => ['.cbslot.op', '.cbslot.my', '.cbdeck', '.cbdis', '.cbgear', '.cbboard'].map(q => { const r = document.querySelector('#cbOv ' + q).getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)]; })"
        g1 = pg.evaluate(GEO); shot(pg, 'cb_board_sakura')
        pg.evaluate("() => CBApp._t.menu()"); pg.wait_for_timeout(100)
        pg.locator('#cbOv .cbmenu [data-cb=dz]').click(); pg.wait_for_timeout(150); pg.locator('#cbOv .cbdz [data-cb=dztab][data-t=d]').click(); pg.wait_for_timeout(150)
        pg.locator('#cbOv .cbdz .dzt[data-cb=bdi][data-id=""]').click(); pg.wait_for_timeout(120); y5 = pg.evaluate(MZ)
        pg.locator('#cbOv .cbmod [data-cb=bduse]').click(); pg.wait_for_timeout(150); tt5 = pg.evaluate(TOAST)
        s2 = pg.evaluate("() => [CBApp._t.state.coin, CBApp._t.state.boards, CBApp._t.state.board, JSON.parse(localStorage.getItem('tengel.cb')).board]")
        pg.locator('#cbOv .cbdz [data-cb=dzx]').click(); pg.wait_for_timeout(100)
        start(pg, '12345', '12345'); b2 = pg.evaluate(BIMG); g2 = pg.evaluate(GEO); pg.evaluate("() => CBApp._t.menu()"); pg.wait_for_timeout(100)
        check(y5['h'] == 'いつものプレイボード' and y5['img'] == 'cb_board.webp' and y5['btns'] == ['この ボードを 使う', 'もどる'] and s2 == [400, ['sakura'], '', ''] and tt5 == 'プレイボードを『いつもの』に したよ'
              and b2[:4] == ['cb_board.webp', False, 'block', 'cbfire'] and b2[5] is False and g1[:2] + g1[3:] == g2[:2] + g2[3:] and g1[2][1:] == g2[2][1:] and abs((g2[2][0] - g1[2][0]) - g2[5][2] * 0.0586) <= 1.5,
              f'いつもの に もどす：コインは 使わない・解放した ものは のこる・火の あかりが もどる・カードを 置く 所・捨て札・歯車の 場所は ボードを かえても 同じ・'
              f'山札は『桜の舞踏会』〈第4.186版の 新しい 絵〉の とき だけ ボードの 幅の 5.86% 左（{g2[2][0] - g1[2][0]}px／幅 {g2[5][2]}px）（{s2}）')
        pg.evaluate("() => { const T = CBApp._t; T.state.boards = ['sakura', 'violet']; T.state.board = 'violet'; T.save(); }")
        start(pg, '12345', '12345'); b3 = pg.evaluate(BIMG); g3 = pg.evaluate(GEO); pg.evaluate("() => CBApp._t.menu()"); pg.wait_for_timeout(100)
        check(b3[0] == 'cb_bd_violet.webp' and b3[1] is True and b3[5] is False and g3 == g2, f'『紫月の夜』（前の 絵の まま）：山札は いつもの 場所（{g3[2]}）')
        pg.evaluate("() => { const s = JSON.parse(localStorage.getItem('tengel.cb')); s.boards = ['zz', 'sakura', 'sakura', 7]; s.board = 'frost'; localStorage.setItem('tengel.cb', JSON.stringify(s)); CBApp._t.load(); }")
        s3 = pg.evaluate("() => [CBApp._t.state.boards, CBApp._t.state.board]")
        check(s3 == [['sakura'], ''], f'おぼえた 中身が おかしい ときは なおす（ない 名前・2つ目・解放して いない ボードは すてる）（{s3}）')
        pg.evaluate("() => { const T = CBApp._t; T.state.boards = []; T.state.board = ''; T.state.coin = 0; T.save(); T.menu(); }")

        print('■ 7 の 4まい 公開：強さ 逆転（第4.185版・まさちゃん 22:39「7は、手札に7が4枚ある場合、4枚公開し内1枚を捨てると、数字の強さ順が逆転する」・22:45「1.その試合は終わるまで」／第4.187版・11/17 09:39「手札に7が4枚ある段階で発動できる…フィールドセット必要ないからね！」＝セットの 前に 聞く）')
        pg.evaluate("() => { window.__seen = []; }"); start(pg, '77771', '23456', '345'); said(pg)
        a7 = pg.evaluate(ASKQ); v0 = pg.evaluate(V)
        check(a7 and a7['head'] == '7 が 4まい！' and a7['q'] == '7 を 4まい 見せて 逆転する？' and a7['img'] == 'cb_c7.webp' and a7['btns'][:2] == ['使わない', '使う'] and 'セットの 前に 使えるよ（セットは いらない）' in a7['text'] and 'この 対戦が 終わる まで 数字の 強さが 逆に なるよ' in a7['text']
              and v0['phase'] == 'set' and v0['my']['set'] is None and v0['op']['set'] is None and v0['can']['x7r'] is True,
              f'第4.187版：7 が 4まい → ターンの はじめ（セットの 前・まだ だれも セットして いない）に 聞く 窓「7 が 4まい！ 7 を 4まい 見せて 逆転する？」（{a7 and a7["head"]}・{a7 and a7["q"]}）')
        shot(pg, 'cb_x7r_ask')
        peek(pg); m7 = pg.evaluate(MSG); b7 = acts(pg)
        check(m7 == 'セットする カードを えらんでね（カードを タップ）\n7 が 4まい！ セットの 前なら 逆転を 使えるよ' and b7 == ['使わない', '4まい 見せて 逆転'], f'「手札と ボードを 見る」→ 下の 行でも 答えられる（{m7}・{b7}）')
        pg.locator('#cbOv .cbact [data-cb=x7no]').click(); pg.wait_for_timeout(120)
        check(asked(pg) is None and acts(pg) == ['7 を 4まい 見せて 逆転'] and pg.evaluate(V)['can']['x7r'] is True and pg.evaluate(V)['rv'] is False, f'「使わない」→ 窓は もう 出ない・セットする まで 下の ボタン「7 を 4まい 見せて 逆転」で 使える（{acts(pg)}）')
        tap(pg, '1'); pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(100)
        check(asked(pg) is None and acts(pg) == ['7 を 4まい 見せて 逆転'], 'カードを 見て もどっても 窓は 出ない（下の ボタンは のこる）')
        pg.locator('#cbOv .cbact [data-cb=x7yes]').click(); idle(pg)
        seen = pg.evaluate("() => window.__seen"); sd = said(pg); v7 = pg.evaluate(V); tb = pg.evaluate("() => document.querySelector('#cbOv .cbturn').textContent")
        check(any(x.startswith('7 の 効果！ 強さ 逆転|') for x in seen) and any(x.startswith('ban:強さ 逆転！') for x in sd) and v7['rv'] is True and v7['phase'] == 'set' and v7['turn'] == 1 and v7['my']['set'] is None and v7['can']['set'] is True and v7['can']['x7r'] is False
              and any(x == 'use:あなたが 使った！7 の 効果強さ 逆転7 を 4まい 見せて 1まい 捨てるよ。この 対戦が 終わる まで、数字の 強さが 逆に なる！' for x in sd)
              and pg.evaluate(HAND) == '1777' and pg.evaluate(DOMHAND) == '7771' and [d['k'] for d in v7['discard'] if d['why'] == '7'] == ['7'] and '強さ 逆転中' in tb and asked(pg) is None and acts(pg) == [] and pg.evaluate(MSG) == 'セットする カードを えらんでね（カードを タップ）',
              f'「使う」→ 効果の 札「強さ 逆転」→ 7 を 4まい 見せる 窓 → 1まい 捨て札へ →「強さ 逆転！」→ まだ セットの 前（手札は 逆の 強さで ならぶ・上に「強さ 逆転中」・「セットする カードを えらんでね」）（{pg.evaluate(DOMHAND)}・{tb}）')
        shot(pg, 'cb_x7r_after')
        play(pg, '1'); pg.evaluate("() => { window.__seen = []; }"); opp(pg, {'t': 'set', 'k': 2})
        seen = pg.evaluate("() => window.__seen"); sd = said(pg); v7 = pg.evaluate(V)
        check(any('負け…' in x and '2 の ほうが 強いよ（強さ 逆転中）' in x for x in seen) and v7['op']['wins'] == 1 and v7['my']['wins'] == 0 and v7['turn'] == 2 and not any('効果タイム' in x for x in sd) and not any('3まい もどして' in x for x in sd),
              'セット → オープン：1 は 2 に 負ける（もう 逆：「（強さ 逆転中）」）・7 が 3まい のこって いても、この ターンは 3まい 交換を 聞かない（どちらか 1つ）')
        pg.locator('#cbOv [data-cb=discard]').click(); pg.wait_for_timeout(100)
        dl = pg.evaluate("() => [...document.querySelectorAll('#cbOv .cbmod .cbdl .row[data-de]')].map(r => r.dataset.de + '|' + r.textContent.replace(/\\s+/g, ' ').trim())")
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        check(any(x.startswith('7|') and 'あなたの 7 の 効果' in x for x in dl), f'捨て札の 窓：「あなたの 7 の 効果」に 捨てた 7（{dl}）')
        check(asked(pg) is None and acts(pg) == [], '2ターン目：もう 逆転ちゅう なので 聞かない')
        pg.evaluate("() => { window.__seen = []; }"); play(pg, '7'); opp(pg, {'t': 'set', 'k': 3}); v8 = pg.evaluate(V); s8 = pg.evaluate("() => window.__seen")
        play(pg, '7'); opp(pg, {'t': 'set', 'k': 6}); v9 = pg.evaluate(V)
        check(v8['my']['wins'] == 1 and v8['turn'] == 3 and v8['rv'] is True and any('7 が 3 に 勝ったよ（強さ 逆転中）' in x for x in s8) and v9['phase'] == 'end' and v9['res'] == 'win' and v9['my']['wins'] == 2,
              f'2ターン目・3ターン目も 逆：7 は 3 にも 6 にも 勝つ → 2勝 1敗で 勝ち（逆転は その 対戦が 終わる まで）')
        pg.wait_for_function("() => { const g = document.querySelector('#cbOv .cbend .gift'); return g && g.textContent.length > 3; }", timeout=30000)
        # 相手（コンピュータ）が セットの 前に 4まい 公開 → 7 を セット：場の カードは うら・相手の 手札は 7 が 3まいの まま 見える（どれを 出したか わからない）
        OPH = "() => [...document.querySelectorAll('#cbOv .cbohand .cbc')].map(c => c.dataset.ck || '-').join('')"
        for hk in ('7', '1'):
            start(pg, '23456', '77771', '345'); said(pg); pg.evaluate("() => { window.__seen = []; }")
            opp(pg, {'t': 'x7r'})
            seen = pg.evaluate("() => window.__seen"); vo = pg.evaluate(V); tb2 = pg.evaluate("() => document.querySelector('#cbOv .cbturn').textContent"); sd = said(pg); o1 = pg.evaluate(OPH); hs = pg.evaluate(DOMHAND)
            opp(pg, {'t': 'set', 'k': hk}); o2 = pg.evaluate(OPH); sl = pg.evaluate(SLOT); m2 = pg.evaluate(MSG)
            if hk == '7':
                check(any(x.startswith('7 の 効果！ 強さ 逆転|') for x in seen) and vo['rv'] is True and vo['phase'] == 'set' and vo['can']['set'] is True and o1 == '777-' and '強さ 逆転中' in tb2
                      and any(x.startswith('use:コンピュータが 使った！7 の 効果強さ 逆転') for x in sd) and hs == '65432' and asked(pg) is None,
                      f'相手が セットの 前に 4まい 公開 → 相手の 手札に のこった 7 の 3まいは 表で 見える・自分の 手札は 強い 順（逆）に ならぶ・自分は これから セット（{hs}・{o1}）')
            check(o2 == '777' and sl == 'b -' and 'コンピュータは もう セットしたよ' in m2,
                  f'相手が {"7" if hk == "7" else "1"} を セット：場の カードは うら・相手の 手札は 7 が 3まいの まま（どちらを 出しても 同じ 見え方：{o2}・{sl}）')
            play(pg, '2'); vx = pg.evaluate(V); o3 = pg.evaluate(OPH)
            check(vx['last']['c'] == ['2', hk] and vx['last']['res'] == ('lose' if hk == '7' else 'win') and o3 == ('77-' if hk == '7' else '777'),
                  f'オープン：{"逆転ちゅうの 7 が 2 に 勝つ" if hk == "7" else "逆転ちゅうの 2 が 1 に 勝つ"}・その あと 相手の 手札は ほんとうの 形（{o3}）')
        pg.evaluate("() => CBApp._t.menu()"); pg.wait_for_timeout(100)
        # 7 の 新しい 絵・カスタムの 名前（前の『緑の森』『天空の都』は 消した）
        pg.locator('#cbOv .cbmenu [data-cb=dz]').click(); pg.wait_for_timeout(150); pg.locator('#cbOv .cbdz [data-cb=dztab][data-t=f]').click(); pg.wait_for_timeout(150)
        n7 = pg.evaluate("() => [...document.querySelectorAll('#cbOv .cbdz .dzt[data-ck=\"7\"]')].map(t => t.dataset.id + ':' + t.querySelector('span').textContent)")
        pg.locator('#cbOv .cbdz [data-cb=dzx]').click(); pg.wait_for_timeout(100)
        check(n7 == [':いつもの', '7a:疾風の草原', '7b:翡翠の馬', '7r:翠玉の輝き', '7sr:天空の楽園'], f'7 の カスタム：『疾風の草原』『翡翠の馬』（新しい 絵：前の 2つは 消した）・第4.189版：パックの レア『翠玉の輝き』・超レア『天空の楽園』（{n7}）')

        print('■ 4 の 効果で 交換して 5 を 出したら 5 の 効果（第4.183版・まさちゃん 21:24「バトルカード、4で交換したあとに5を相手がフィールドにセットした場合、五の効果を使える」）')
        # 自分が 交換させられて 5 を 出す → 聞く 窓 → 使う → 捨てる カード → 山札の 神様馬で 勝ち
        start(pg, '15623', '47712', 'k'); play(pg, '1'); opp(pg, {'t': 'set', 'k': 4}); opp(pg, {'t': 'eff', 'use': {'u4': True}}); idle(pg)
        pg.evaluate("() => { window.__seen = []; }")
        tap(pg, '5'); pg.locator('#cbOv .cbmod [data-cb=swap]').click(); idle(pg)
        a5 = pg.evaluate(ASKQ); v5 = pg.evaluate(V)
        check(a5 and a5['head'] == '交換で 5 を セット！' and a5['q'] == '5 の 効果を 使う？' and a5['img'] == 'cb_c5.webp' and a5['btns'][:2] == ['使わない', '使う'] and v5['pend'] == {'type': 'u5', 'mine': True} and pg.evaluate(SLOT) == '4:4 の 効果 b[5]:ふせて セット',
              f'4 の 効果で 交換して 5 を 出した → まん中に「交換で 5 を セット！ 5 の 効果を 使う？」（使わない／使う）・オープンは まだ（{a5 and a5["head"]}）')
        shot(pg, 'cb_swap5_ask')
        pg.locator('#cbOv .cbmod.cbask [data-cb=u5yes]').click(); pg.wait_for_timeout(100)
        m5 = pg.evaluate(MSG); b5 = acts(pg)
        tap(pg, '6'); mb5 = modbtns(pg)
        check('5 と いっしょに 捨てる カードを えらんでね' in m5 and b5 == ['もどる'] and mb5[0].startswith('この カードを 捨てる'), f'「使う」→ いっしょに 捨てる カードを えらぶ（{m5}）')
        pg.locator('#cbOv .cbmod [data-cb=u5drop]').click(); idle(pg)
        v6 = pg.evaluate(V)
        check(any('勝ち！' in s for s in pg.evaluate("() => window.__seen")) and v6['my']['wins'] == 1 and v6['turn'] == 2 and [d['k'] for d in v6['discard'] if d['why'] == '5'] == ['5', '6'] and pg.evaluate(HAND) == '123',
              f'5 と 6 を 捨てて 山札から ふせて セット → オープン：山札の 神様馬で 4 に 勝ち（{[d["k"] for d in v6["discard"]]}）')
        # 相手（コンピュータ）が 交換させられて 5 を 出す → 自分の 画面は「交換して いるよ」の まま → 相手が 5 の 効果
        start(pg, '41236', '15677', 'k'); opp(pg, {'t': 'set', 'k': 1}); play(pg, '4')
        pg.locator('#cbOv [data-cb=effyes]').click(); idle(pg)
        opp(pg, {'t': 'swap', 'k': 5}); idle(pg)
        m6 = pg.evaluate(MSG); v7 = pg.evaluate(V)
        check(v7['pend'] == {'type': 'swap', 'mine': False} and v7['phase'] == 'swap' and 'コンピュータが カードを 交換して いるよ' in m6 and pg.evaluate(ASKQ) is None, f'相手が 交換で 5 を 出して えらんで いる 間も、自分の 画面は「交換して いるよ…」の まま（5 だと わからない）（{m6}）')
        said(pg); opp(pg, {'t': 'u5', 'dropk': 6}); idle(pg)
        sd6 = said(pg); v8 = pg.evaluate(V)
        check(any('コンピュータが 5 の 効果を 使ったよ' in s for s in sd6) and v8['op']['wins'] == 1 and [d['k'] for d in v8['discard'] if d['why'] == '5'] == ['5', '6'],
              f'相手が 5 の 効果を 使った → 「コンピュータが 5 の 効果を 使ったよ」→ オープン（相手の 山札の 神様馬が 4 に 勝ち）（{[s for s in sd6 if "5 の 効果" in s][:1]}）')
        pg.evaluate("() => CBApp._t.menu()"); pg.wait_for_timeout(100)

        print('■ ミッション（第4.183版・まさちゃん 20:51「TENGERカードバトルミッション追加 1ヶ月に一回リセットされる CPUに連続勝利 3連勝達成30枚 … 10連勝達成で300枚 お友達バトルで連続勝利 3連勝20枚 … 10連勝140枚」）')
        MSS = """() => { const s = document.querySelector('#cbOv .cbms'); if (!s || !s.classList.contains('on')) return null; const t = e => e.textContent.replace(/\\s+/g, ' ').trim();
          return { coin: t(s.querySelector('.cbcoinl')), m: t(s.querySelector('.msm')), tab: [...s.querySelectorAll('.tabs button')].map(b => t(b) + (b.classList.contains('on') ? '*' : '')), h4: t(s.querySelector('h4')), cur: t(s.querySelector('.cur')),
            rows: [...s.querySelectorAll('.msr')].map(r => t(r) + (r.classList.contains('done') ? '*' : r.classList.contains('next') ? '>' : '')), note: t(s.querySelector('.note')), tool: !!s.querySelector('.cbtst') }; }"""
        MSB = "() => document.querySelector('#cbOv .cbmenu [data-cb=ms]').textContent"
        MST = "() => JSON.parse(JSON.stringify(CBApp._t.state.ms))"
        pg.evaluate("() => { CBApp._now = () => new Date(2026, 10, 16, 20, 51); const T = CBApp._t; T.state.coin = 0; T.state.ms = { m: '2026-11', cpu: 0, fr: 0, got: { cpu: [], fr: [] }, live: '' }; T.save(); T.menu(); }"); pg.wait_for_timeout(150)
        check(pg.evaluate(MSB) == '🎯ミッション今月 0／14 達成', f'メニューの「ミッション」：今月 0／14 達成（{pg.evaluate(MSB)}）')
        pg.locator('#cbOv .cbmenu [data-cb=ms]').click(); pg.wait_for_timeout(200); m0 = pg.evaluate(MSS)
        check(m0 and pg.evaluate("() => CBApp._t.screen") == 'ms' and m0['coin'] == 'バトルコイン 0枚' and m0['m'] == '11月の ミッション12月1日に リセット（あと 15日）' and m0['tab'] == ['コンピュータ0／7 達成*', '友だちバトル0／7 達成'] and m0['h4'] == 'コンピュータに 連続勝利'
              and m0['cur'] == 'いま0連勝つぎは 3連勝で 30枚（あと 3勝）' and m0['rows'] == ['3連勝30枚あと 3勝>', '5連勝60枚', '6連勝90枚', '7連勝120枚', '8連勝150枚', '9連勝200枚', '10連勝300枚'] and not m0['tool']
              and '毎月 1日に リセット' in m0['note'] and '同点は そのまま' in m0['note'] and '部屋を 出た' not in m0['note'],
              f'ミッションの 画面：11月の ミッション（12月1日に リセット・あと 15日）・コンピュータに 連続勝利 7つ（3・5・6・7・8・9・10連勝 → 30〜300枚）・いま 0連勝（{m0 and m0["rows"]}）')
        shot(pg, 'cb_ms_cpu')
        pg.locator('#cbOv .cbms [data-cb=mstab][data-t=fr]').click(); pg.wait_for_timeout(150); m1 = pg.evaluate(MSS)
        check(m1['tab'] == ['コンピュータ0／7 達成', '友だちバトル0／7 達成*'] and m1['h4'] == '友だちバトルで 連続勝利' and m1['rows'] == ['3連勝20枚あと 3勝>', '5連勝40枚', '6連勝60枚', '7連勝80枚', '8連勝100枚', '9連勝120枚', '10連勝140枚'] and '部屋を 出た・つながりが 切れた ときは 数えないよ' in m1['note'],
              f'「友だちバトル」：3・5・6・7・8・9・10連勝 → 20〜140枚・友だちが 部屋を 出た／切れた ときは 数えない（{m1["rows"]}）')
        shot(pg, 'cb_ms_fr')
        pg.locator('#cbOv .cbms [data-cb=mstab][data-t=cpu]').click(); pg.locator('#cbOv .cbms [data-cb=msx]').click(); pg.wait_for_timeout(150)
        check(pg.evaluate("() => CBApp._t.screen") == 'menu', '「← もどる」→ メニュー')
        # 2連勝 → 3連勝目で 達成（その場で 30枚）
        pg.evaluate("() => { const T = CBApp._t; T.state.ms.cpu = 2; T.state.streak = 0; T.save(); }")      # 第4.188版：いつもの 連勝は 0 から（この 勝ちは 1連勝目：ボーナスなし）
        def ckey(q, k):      # 手札の カードを 種類で えらんで セット（べつの デザインでも：data-ck）
            q.locator(f'#cbOv .cbhand .cbc[data-ck="{k}"]').first.click(); q.wait_for_timeout(60); q.locator('#cbOv .cbmod [data-cb=set]').click(); idle(q)
        start(pg, 'k1234', '76543')
        lv = pg.evaluate(MST)['live']
        ckey(pg, 'k'); opp(pg, {'t': 'set', 'k': 7}); pg.locator('#cbOv .cbmod [data-cb=kskip]').click(); idle(pg)
        ckey(pg, '1'); opp(pg, {'t': 'set', 'k': 6}); ckey(pg, '2'); opp(pg, {'t': 'set', 'k': 3})
        pg.wait_for_function("() => { const g = document.querySelector('#cbOv .cbend .gift'); return CBApp._t.ended && g && g.textContent.length > 3; }", timeout=30000); pg.wait_for_timeout(700)
        eg = pg.evaluate("() => { const g = document.querySelector('#cbOv .cbend .gift'), b = g.querySelector('.cbmsn'); return { t: g.textContent, h: Math.round(g.getBoundingClientRect().height), minh: parseFloat(getComputedStyle(g).minHeight), lab: b ? b.getAttribute('aria-label') : null, anim: b ? getComputedStyle(b).animationName + '/' + getComputedStyle(b).animationIterationCount : null, w: b ? Math.round(b.getBoundingClientRect().width) : 0, vw: innerWidth }; }")
        s3 = pg.evaluate(MST)
        check(lv == 'cpu' and s3['cpu'] == 3 and s3['got']['cpu'] == [3] and s3['live'] == '' and pg.evaluate("() => CBApp._t.state.coin") == 32 and '🎯ミッション達成！3連勝＋30枚' in eg['t'] and 'バトルコイン ＋2枚（いま 32枚）' in eg['t']
              and eg['lab'] == 'ミッション達成 3連勝 バトルコイン 30枚' and eg['anim'] == 'cbget/1' and eg['h'] == eg['minh'] and 0 < eg['w'] <= eg['vw'] - 32,
              f'3連勝目：その場で ミッション達成（＋30枚 ＋ いつもの 2枚 ＝ 32枚）・さいごの 画面に「🎯 ミッション達成！ 3連勝 🪙＋30枚」（1回 ふくらむ だけ・札の 場所に おさまる {eg["h"]}／{eg["minh"]}px）・配った とき「対戦 ちゅう」の しるし → 終わって 消える')
        shot(pg, 'cb_ms_end3')
        pg.locator('#cbOv .cbend [data-cb=menu]').click(); pg.wait_for_timeout(150)
        pg.locator('#cbOv .cbmenu [data-cb=ms]').click(); pg.wait_for_timeout(150); m2 = pg.evaluate(MSS)
        check(m2['coin'] == 'バトルコイン 32枚' and m2['tab'][0] == 'コンピュータ1／7 達成*' and m2['cur'] == 'いま3連勝つぎは 5連勝で 60枚（あと 2勝）' and m2['rows'][:2] == ['3連勝30枚✓ 達成*', '5連勝60枚あと 2勝>'],
              f'ミッションの 画面：3連勝 ✓ 達成・つぎは 5連勝（あと 2勝）（{m2["rows"][:2]}）')
        pg.locator('#cbOv .cbms [data-cb=msx]').click(); pg.wait_for_timeout(100)
        check(pg.evaluate(MSB) == '🎯ミッション今月 1／14 達成', 'メニュー：今月 1／14 達成')
        # 同点 → そのまま／負け → 0
        start(pg, 'k1234', 'm1234'); ckey(pg, 'k'); opp(pg, {'t': 'set', 'k': 'm'}); ckey(pg, '1'); opp(pg, {'t': 'set', 'k': 1}); ckey(pg, '2'); opp(pg, {'t': 'set', 'k': 2})
        pg.wait_for_function("() => CBApp._t.ended", timeout=30000); pg.wait_for_timeout(300)
        d3 = [pg.evaluate("() => CBApp._t.view.res"), pg.evaluate(MST)['cpu']]
        start(pg, '23677', '12356'); play(pg, '3'); opp(pg, {'t': 'set', 'k': 1}); play(pg, '6'); opp(pg, {'t': 'set', 'k': 2}); play(pg, '7'); opp(pg, {'t': 'set', 'k': 3})
        pg.wait_for_function("() => CBApp._t.ended", timeout=30000); pg.wait_for_timeout(300)
        l3 = [pg.evaluate("() => CBApp._t.view.res"), pg.evaluate(MST)]
        check(d3 == ['draw', 3] and l3[0] == 'lose' and l3[1]['cpu'] == 0 and l3[1]['got']['cpu'] == [3] and pg.evaluate("() => CBApp._t.state.coin") == 32, f'同点 → 連勝は そのまま（{d3}）・負け → 0（達成した 3連勝と コインは のこる）')
        # とちゅうで やめる → 0
        pg.evaluate("() => { const T = CBApp._t; T.state.ms.cpu = 4; T.save(); }")
        start(pg, 'k1234', '76543'); pg.locator('#cbOv .cbtop [data-cb=quit]').click(); pg.locator('#cbOv .cbmod [data-cb=quitgo]').click(); pg.wait_for_timeout(150)
        q0 = pg.evaluate(MST)
        check(q0['cpu'] == 0 and q0['live'] == '' and pg.evaluate("() => CBApp._t.screen") == 'menu', f'対戦の とちゅうで やめた → ミッションの 連勝も 0（{q0["cpu"]}）')
        # 対戦の とちゅうで アプリが 閉じられた（つぎに 開いた とき）→ 0・知らせる
        pg.evaluate("() => { const T = CBApp._t; T.state.ms.cpu = 4; T.save(); }")
        start(pg, 'k1234', '76543'); ckey(pg, 'k')
        lv2 = json.loads(pg.evaluate("() => localStorage.getItem('tengel.cb')"))['ms']
        pg.evaluate("() => { CBApp._t.load(); CBApp._t.menu(); }"); pg.wait_for_timeout(150); tt = pg.evaluate(TOAST); q1 = pg.evaluate(MST)
        check(lv2['live'] == 'cpu' and lv2['cpu'] == 4 and q1['cpu'] == 0 and q1['live'] == '' and '前の 対戦が とちゅうで 終わった ので、' in tt and 'ミッションの 連勝（コンピュータ）は 0 に もどったよ' in tt,
              f'対戦 ちゅうに アプリが 閉じられた → つぎに 開いた とき ミッションの 連勝は 0・「ミッションの 連勝（コンピュータ）は 0 に もどったよ」（{tt!r}）')
        # 月が かわる → リセット（達成も 連勝も 0）
        pg.evaluate("() => { const T = CBApp._t; T.state.ms.cpu = 3; T.state.ms.fr = 2; T.state.ms.got = { cpu: [3], fr: [] }; T.save(); CBApp._now = () => new Date(2026, 11, 1, 0, 0, 5); T.menu(); }"); pg.wait_for_timeout(150)
        r0 = pg.evaluate(MST); mb = pg.evaluate(MSB)
        pg.locator('#cbOv .cbmenu [data-cb=ms]').click(); pg.wait_for_timeout(150); m3 = pg.evaluate(MSS)
        check(r0 == {'m': '2026-12', 'cpu': 0, 'fr': 0, 'got': {'cpu': [], 'fr': []}, 'live': ''} and mb == '🎯ミッション今月 0／14 達成' and m3['m'] == '12月の ミッション1月1日に リセット（あと 31日）' and m3['rows'][0] == '3連勝30枚あと 3勝>' and pg.evaluate("() => CBApp._t.state.coin") == 32,
              f'月が かわった（12月1日）→ ミッションを リセット（達成も 連勝も 0・コインは のこる）・「12月の ミッション（1月1日に リセット）」（{r0}）')
        pg.locator('#cbOv .cbms [data-cb=msx]').click(); pg.wait_for_timeout(100)
        # 前の 月の 連勝の まま 月が かわって 勝つ → 新しい 月の 1連勝（前の 月の 続きに しない）
        pg.evaluate("() => { const T = CBApp._t; T.state.ms = { m: '2026-11', cpu: 9, fr: 0, got: { cpu: [3, 5, 6, 7, 8, 9], fr: [] }, live: '' }; T.save(); }")
        start(pg, 'k1234', '76543'); ckey(pg, 'k'); opp(pg, {'t': 'set', 'k': 7}); pg.locator('#cbOv .cbmod [data-cb=kskip]').click(); idle(pg)
        ckey(pg, '1'); opp(pg, {'t': 'set', 'k': 6}); ckey(pg, '2'); opp(pg, {'t': 'set', 'k': 3})
        pg.wait_for_function("() => { const g = document.querySelector('#cbOv .cbend .gift'); return CBApp._t.ended && g && g.textContent.length > 3; }", timeout=30000)
        r1 = pg.evaluate(MST)
        check(r1 == {'m': '2026-12', 'cpu': 1, 'fr': 0, 'got': {'cpu': [], 'fr': []}, 'live': ''} and 'ミッション達成' not in pg.locator('#cbOv .cbend .gift').inner_text(), f'11月の 9連勝の まま 12月に 勝つ → 12月の 1連勝（10連勝の 達成には ならない）（{r1}）')
        # おぼえた 中身が おかしい ときは なおす
        pg.evaluate("() => { const s = JSON.parse(localStorage.getItem('tengel.cb')); s.ms = { m: 'xx', cpu: -5, fr: 'a', got: { cpu: [3, 3, 4, 5, 'x'], fr: null }, live: 'zz' }; localStorage.setItem('tengel.cb', JSON.stringify(s)); CBApp._t.load(); }")
        check(pg.evaluate(MST) == {'m': '2026-12', 'cpu': 0, 'fr': 0, 'got': {'cpu': [3, 5], 'fr': []}, 'live': ''}, f'おぼえた ミッションが おかしい ときは なおす（{pg.evaluate(MST)}）')

        print('■ ログインボーナスの バトルコイン（第4.188版・まさちゃん 11:22「毎日ログインにも、バトルコイン1日2枚 7日ログインで10枚貰えるようにして！」）')
        GIFT = "() => JSON.parse(localStorage.getItem('tengel.cbgift') || 'null')"
        COINS4 = "() => [CBApp._t.state.coin, CBApp._t.state.gifts.slice(), JSON.parse(localStorage.getItem('tengel.cb')).coin, document.querySelector('#cbOv .cbmenu .cbcoinl b').textContent]"
        pg.evaluate("() => { const T = CBApp._t; T.state.coin = 5; T.state.gifts = []; T.save(); localStorage.removeItem('tengel.cbgift'); T.menu(); }"); pg.wait_for_timeout(200); said(pg)
        TS = lambda: [x[6:] for x in said(pg) if x.startswith('toast:')]      # 出た ふきだし（テストの 速さでは すぐ 消える ので 出た ものを ぜんぶ 覚えて おく）
        today = pg.evaluate("() => { const d = new Date(), p = n => String(n).padStart(2, '0'); return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate()); }")
        d0 = pg.evaluate("() => TengelLogin.check()"); pg.wait_for_function("() => !!document.getElementById('lgOv')", timeout=10000); pg.wait_for_timeout(400)
        lg1 = pg.evaluate("""() => { const o = document.getElementById('lgOv'), c = o.querySelector('.lgc').getBoundingClientRect(), q = o.querySelector('.lgq').getBoundingClientRect();
          return { line: o.querySelector('.lgs').textContent, img: o.querySelectorAll('img.lgci[src="cb_coin.webp"]').length, tiles: [...o.querySelectorAll('.lgd li')].map(e => e.textContent), cb: TengelLogin.CB,
            inside: c.top >= 0 && c.bottom <= innerHeight && c.left >= 0 && c.right <= innerWidth, q: q.left >= c.left && q.right <= c.right, z: +getComputedStyle(o).zIndex, cbz: +getComputedStyle(document.getElementById('cbOv')).zIndex }; }""")
        pg.evaluate("() => TengelLogin.close()"); pg.wait_for_timeout(150)
        g1 = pg.evaluate(GIFT); tt = TS(); c1 = pg.evaluate(COINS4)
        check(d0 == 0 and lg1['line'] == '1日目 の ボーナス+200Pとバトルコイン+2枚を もらったよ' and lg1['img'] == 8 and lg1['tiles'][0] == '1日目200P2枚' and lg1['tiles'][6] == '7日目1,300P12枚' and lg1['cb'] == [2, 2, 2, 2, 2, 2, 12] and lg1['inside'] and lg1['q']
              and g1 == {'v': 1, 'list': [{'id': f'login-{today}', 'c': 2}]} and c1 == [7, [f'login-{today}'], 7, '7'] and tt == ['🎁 ログインボーナスの バトルコイン\n2枚を 受け取ったよ'],
              f'カードバトルの メニューを 開いて いる ときに ログインボーナス（1日目）→ 窓に「バトルコイン +2枚」（7日ぶんの 札にも：1〜6日目 2枚・7日目 12枚）・すぐ 受け取る（5 → {c1[0]}枚）・メニューで 知らせる（{tt!r}）')
        pg.evaluate("() => { CBApp._t.load(); CBApp._t.menu(); }"); pg.wait_for_timeout(150); c2 = pg.evaluate(COINS4); r2 = pg.evaluate("() => TengelLogin.check()"); pg.wait_for_timeout(300); c3 = pg.evaluate(COINS4)
        check(c2 == c1 and r2 == -1 and c3 == c1 and pg.evaluate(GIFT) == g1, f'読み直しても・同じ 日に もう 1回 確かめても 2回は 入らない（{c3[0]}枚 の まま）')
        # 閉じて いる あいだに 7日目（2枚 ＋10枚）→ つぎに 開いた とき 受け取る
        pg.evaluate("() => { CBApp.close(); const g = JSON.parse(localStorage.getItem('tengel.cbgift')); g.list.push({ id: 'login-2099-01-07', c: 12 }); localStorage.setItem('tengel.cbgift', JSON.stringify(g)); }"); pg.wait_for_timeout(200)
        pg.evaluate("() => CBApp.open()"); pg.wait_for_timeout(400); tt4 = TS(); c4 = pg.evaluate(COINS4)
        shot(pg, 'cb_login_menu')
        check(c4 == [19, [f'login-{today}', 'login-2099-01-07'], 19, '19'] and tt4 == ['🎁 ログインボーナスの バトルコイン\n12枚を 受け取ったよ'], f'カードバトルを 閉じて いる あいだの ログインボーナス（7日目 12枚）→ つぎに 開いた とき 受け取る（7 → {c4[0]}枚・{tt4!r}）')
        # 持てる 数（9999枚）で 止まる・おかしな 中身は 入れない
        pg.evaluate("() => { const T = CBApp._t; T.state.coin = 9995; T.save(); const g = JSON.parse(localStorage.getItem('tengel.cbgift')); g.list.push({ id: 'login-2099-01-08', c: 12 }, { id: 5, c: 3 }, { id: 'x', c: -4 }, null); localStorage.setItem('tengel.cbgift', JSON.stringify(g)); document.dispatchEvent(new CustomEvent('tengel:cbgift')); }")
        pg.wait_for_timeout(300); tt5 = TS(); c5 = pg.evaluate(COINS4)
        check(c5[0] == 9999 and c5[2] == 9999 and c5[1][-1] == 'login-2099-01-08' and len(c5[1]) == 3 and tt5 == ['🎁 ログインボーナスの バトルコイン\n4枚を 受け取ったよ（9999枚 まで）'],
              f'持てる 数（9999枚）を こえる ぶんは 入らない・おかしな 中身（id が ない・枚数が マイナス）は 入れない（{c5[0]}枚・{tt5!r}）')
        pg.evaluate("() => { const T = CBApp._t; T.state.coin = 0; T.save(); T.menu(); }"); pg.wait_for_timeout(150)

        print('■ 部屋：それぞれの デザイン（第4.183版・まさちゃん 20:53「①相手の背面デザインは、CPUと戦う時は、カスタムしているデザインにして！ ②お友達バトルの時は、それぞれがカスタムしている背面デザイン、カードデザインにして！」）')
        OPN = "() => { window.__op = []; if (window.__mo3) window.__mo3.disconnect(); const mo = new MutationObserver(() => { const m = document.querySelector('#cbOv .cbmod'); if (m.classList.contains('cbopen')) { const t = m.querySelector('.cbres'); window.__op.push((t ? t.textContent : '') + '|' + [...m.querySelectorAll('.cbflip .in img')].map(i => i.getAttribute('src')).join(',')); } }); mo.observe(document.querySelector('#cbOv .cbmod'), { childList: true, subtree: true, attributes: true, characterData: true }); window.__mo3 = mo; }"
        IMS = "() => ({ deck: document.querySelector('#cbOv .cbdeck img').getAttribute('src'), op: [...new Set([...document.querySelectorAll('#cbOv .cbohand img')].map(i => i.getAttribute('src')))], my: [...document.querySelectorAll('#cbOv .cbhand .cbc')].map(c => c.dataset.ck + '=' + c.querySelector('img').getAttribute('src')), os: (document.querySelector('#cbOv .cbslot.op img') || { getAttribute: () => '-' }).getAttribute('src'), dis: (document.querySelector('#cbOv .cbdis .pl img') || { getAttribute: () => '-' }).getAttribute('src') })"
        pg.evaluate("() => { CBApp._now = null; const T = CBApp._t; T.state.backs = ['sky', 'star']; T.state.faces = ['ka', 'mb', '6a', '3b']; T.state.back = 'sky'; T.state.face = { k: 'ka', '6': '6a' }; T.save(); T.menu(); }")
        pg.evaluate(OPN)
        # ① コンピュータ：相手の うら・おもても 自分の デザイン
        start(pg, 'k1234', '6m577'); i0 = pg.evaluate(IMS)
        ckey(pg, 'k'); opp(pg, {'t': 'set', 'k': 6}); pg.wait_for_timeout(100); o0 = pg.evaluate("() => window.__op.slice()")
        check(i0['deck'] == 'cb_bk_sky_d.webp' and i0['op'] == ['cb_bk_sky_s.webp'] and 'k=cb_fc_ka_s.webp' in i0['my'] and any(x.startswith('勝ち！') and x.endswith('|cb_bk_sky_c.webp,cb_fc_ka_c.webp,cb_bk_sky_c.webp,cb_fc_6a_c.webp') for x in o0),
              f'① コンピュータとの 対戦：相手（コンピュータ）の 手札・ふせた カードも 自分が えらんだ うら『天馬の光』・めくった 6 も 自分の デザイン『赤の書庫』（{i0["op"]}・{o0[-1] if o0 else None}）')
        pg.evaluate("() => CBApp._t.menu()"); pg.wait_for_timeout(100)
        # ② 友だち：自分の カード＝自分の デザイン・友だちの カード＝友だちの デザイン（ホスト：うら 天馬の光・神様馬 朱の鳥居／ゲスト：うら 星座の馬・幻の馬 紅い雷・3 星の遺跡）
        gp.evaluate("() => { const T = CBApp._t; T.state.backs = ['star']; T.state.faces = ['mb', '3b']; T.state.back = 'star'; T.state.face = { m: 'mb', '3': '3b' }; T.state.coin = 0; T.state.ms = { m: T.msKey(), cpu: 0, fr: 0, got: { cpu: [], fr: [] }, live: '' }; T.menu(); }")
        gp.evaluate(OPN)
        pg.evaluate("() => { const T = CBApp._t; T.state.coin = 0; T.state.ms = { m: T.msKey(), cpu: 0, fr: 2, got: { cpu: [], fr: [] }, live: '' }; CBApp._opt = { hands: [['k', '1', '2', '6', '7'], ['m', '3', '4', '5', '7']], turns: 3 }; CBApp._think = null; }")
        pg.locator('#cbOv .cbmenu [data-cb=host]').click(); pg.wait_for_timeout(300)
        num = pg.evaluate("() => document.querySelector('#cbOv .cbroom .num').textContent")
        gp.locator('#cbOv .cbmenu [data-cb=join]').click(); gp.wait_for_timeout(150)
        for d in num: gp.locator(f'#cbOv .cbkeys [data-key="{d}"]').click()
        gp.locator('#cbOv .cbkeys [data-key=go]').click()
        pg.wait_for_function("() => CBApp._t.screen === 'game' && CBApp._t.view && CBApp._t.idle", timeout=30000); gp.wait_for_function("() => CBApp._t.screen === 'game' && CBApp._t.view && CBApp._t.idle", timeout=30000)
        hi, gi = pg.evaluate(IMS), gp.evaluate(IMS)
        hz, gz = pg.evaluate("() => CBApp._t.match.opDz"), gp.evaluate("() => CBApp._t.match.opDz")
        check(hz == {'b': 'star', 'f': {'3': '3b', 'm': 'mb'}} and gz == {'b': 'sky', 'f': {'6': '6a', 'k': 'ka'}}, f'部屋に 入った とき、おたがいの えらんだ デザインが 届く（ホスト ← {hz}・ゲスト ← {gz}）')
        check(hi['deck'] == 'cb_bk_sky_d.webp' and hi['op'] == ['cb_bk_star_s.webp'] and 'k=cb_fc_ka_s.webp' in hi['my'] and '6=cb_fc_6a_s.webp' in hi['my'] and '1=cb_s1.webp' in hi['my']
              and gi['deck'] == 'cb_bk_star_d.webp' and gi['op'] == ['cb_bk_sky_s.webp'] and 'm=cb_fc_mb_s.webp' in gi['my'] and '3=cb_fc_3b_s.webp' in gi['my'] and '4=cb_s4.webp' in gi['my'],
              f'② 友だちとの 対戦：自分の 手札・山札は 自分の デザイン・友だちの 手札は 友だちが えらんだ うら（ホスト：相手 {hi["op"]}・ゲスト：相手 {gi["op"]}）')
        shot(pg, 'cb_room_dz_host'); shot(gp, 'cb_room_dz_guest')
        ckey(gp, 'm'); idle(pg)
        hs1 = pg.evaluate(IMS)['os']
        ckey(pg, 'k'); idle(gp); idle(pg); pg.wait_for_timeout(150)
        ho, go = pg.evaluate("() => window.__op.slice()"), gp.evaluate("() => window.__op.slice()")
        check(hs1 == 'cb_bk_star_s.webp' and any(x.endswith('|cb_bk_sky_c.webp,cb_fc_ka_c.webp,cb_bk_star_c.webp,cb_fc_mb_c.webp') for x in ho) and any(x.endswith('|cb_bk_star_c.webp,cb_fc_mb_c.webp,cb_bk_sky_c.webp,cb_fc_ka_c.webp') for x in go),
              f'友だちが ふせた カードは 友だちの うら・めくると：自分の 神様馬『朱の鳥居』／友だちの 幻の馬『紅い雷』（ゲストの 画面は その 反対）（{ho[-1] if ho else None}）')
        ckey(gp, '3'); idle(pg); ckey(pg, '1'); idle(gp); idle(pg)
        pg.locator('#cbOv [data-cb=discard]').click(); pg.wait_for_timeout(100)
        hd = pg.evaluate("() => [...document.querySelectorAll('#cbOv .cbmod .cbdl .row[data-dt]')].map(r => r.querySelector('b').textContent + '|' + [...r.querySelectorAll('.pr')].map(p => p.querySelector('span').textContent + '=' + [...p.querySelectorAll('img')].map(i => i.getAttribute('src')).join(',')).join('|'))")
        pg.locator('#cbOv .cbmod .cbdl .row[data-dt="2"] .pr:last-child .cbc').click(); pg.wait_for_timeout(80); big = pg.evaluate("() => document.querySelector('#cbOv .cbmod .big img').getAttribute('src')")
        pg.locator('#cbOv .cbmod [data-cb=discard]').click(); pg.wait_for_timeout(60); pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        check(hd == ['ターン 1|あなた=cb_fc_ka_s.webp|ともだち=cb_fc_mb_s.webp', 'ターン 2|あなた=cb_s1.webp|ともだち=cb_fc_3b_s.webp'] and big == 'cb_fc_3b_c.webp' and pg.evaluate(IMS)['dis'] == 'cb_fc_3b_s.webp' and gp.evaluate(IMS)['dis'] == 'cb_fc_3b_s.webp',
              f'捨て札：自分の カードは 自分の デザイン・友だちの カードは 友だちの デザイン（大きく 見ても 同じ）（{hd}）')
        ckey(gp, '7'); idle(pg); ckey(pg, '2'); idle(gp); idle(pg)
        pg.wait_for_function("() => { const g = document.querySelector('#cbOv .cbend .gift'); return CBApp._t.ended && g && g.textContent.length > 3; }", timeout=30000); gp.wait_for_function("() => CBApp._t.ended", timeout=30000); pg.wait_for_timeout(500)
        hg = pg.locator('#cbOv .cbend .gift').inner_text().replace('\n', ''); hm, gm = pg.evaluate(MST), gp.evaluate(MST)
        check(pg.evaluate("() => CBApp._t.view.res") == 'win' and hm['fr'] == 3 and hm['got']['fr'] == [3] and hm['live'] == '' and pg.evaluate("() => CBApp._t.state.coin") == 20 and '🎯ミッション達成！3連勝＋20枚' in hg and 'バトルコイン（いま 20枚）' in hg
              and gm['fr'] == 0 and gm['live'] == '' and hm['cpu'] == 0,
              f'友だちバトルで 3連勝目 → ミッション達成（＋20枚：コインなしの 部屋でも）・負けた ゲストの 友だちバトルの 連勝は 0・コンピュータの 連勝は かわらない（{hg[-40:]!r}）')
        shot(pg, 'cb_room_ms_end')
        pg.locator('#cbOv .cbend [data-cb=menu]').click(); pg.wait_for_timeout(150)      # ホストが メニューへ → ゲストには「ともだちが 部屋を 出たよ」の 窓
        gp.locator('#cbOv .cbmod [data-cb=menu]').click(); gp.wait_for_timeout(150)
        for q in (pg, gp): q.evaluate("() => { const T = CBApp._t; T.state.backs = []; T.state.faces = []; T.state.back = ''; T.state.face = {}; T.save(); T.menu(); }")
        check(not errs and not gerrs, f'エラー なし {errs[:3]} {gerrs[:3]}')
        if HAVE:
            miss = sorted(set(f for f in reqs if f.startswith('cb_') and f != 'cb_bundle.js' and f not in CBF))
            used = sorted(set(f for f in reqs if f in CBF))
            check(not miss and all(f in used for f in ['cb_board.webp', 'cb_deck.webp', 'cb_logo.webp', 'cb_icon.webp', 'cb_sb.webp', 'cb_s1.webp', 'cb_c1.webp', 'cb_ck.webp', 'cb_coin.webp', 'cb_bgm.m4a']), f'読んだ 絵と 音は ぜんぶ アプリに 入れる ファイル（ない 名前 {miss}・読んだ {len(used)}こ）')
finally:
    srv.terminate()
print('\n' + ('全部 OK' if not fails else f'NG {len(fails)}こ：' + ' / '.join(fails)))
sys.exit(1 if fails else 0)
