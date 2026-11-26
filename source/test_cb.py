# 馬カードバトル（第4.176版）の 画面の テスト：App Store版（TARGET=app）を localhost で アプリ版として 開く
#   まさちゃん 2026/11/15 21:41「TENGER馬カードバトル …アイコンは推し馬の上に設置して！」・21:54「・コンピュータと対戦 ・部屋を作成して、友達と対戦 これをやりたい！」
#   ・入口：右下の 丸い ボタンの 列（たてに 4つ：上から トレーニングセンター → 推し馬 → カードバトル → 思い出フィギュア。まさちゃん 11/16 00:34「丸のアイコン組を少し小さくして！ピッタリ収まるように」・
#       00:47「トレーニングセンターを一番上、カードバトルを思い出フィギュアの上にして」・01:15「この青四角下の空間気になる。大きさ調整して空間があかないようにして！」・
#       01:16「カードバトルを、TENGERカードバトルに名前変えて！」）・丸の 大きさは「壁紙&ボード着せ替え」の すぐ 下 〜 下の タブの すぐ 上 を ぴったり うめる 大きさ（66px まで）・
#       たての 短い 画面（2列 × 2段）でも 右上の ボタンに 重ならない
#   ・メニュー・あそび方・コンピュータと 対戦（出す・オープン・捨て札・効果 6つ を 画面で）・結果と ごほうび（第4.212版：お世話トークンは なし・コンピュータに 3連勝 ごとに 調査隊切符 1枚・5連勝 ごとに 2枚・15枚 まで）・とちゅうで やめる
#   第4.212版（まさちゃん 2026/11/23）：TENGERカードバトルは「おもちゃ」（3,000P で 解放）。丸い ボタンに 🔒 → 押すと 解放の 窓（やめる／解放する）→ 解放したら 開く
#   ・部屋：2つの 画面（ホスト・ゲスト）を、にせの アプリ側（Room.swift の かわり：BroadcastChannel）で つないで さいごまで 対戦・もう 1回・やめる
#   python3 test_cb.py   （ios/cb_assets/ が ある とき だけ 絵の 確かめ。ない とき（CI）も 画面は 動く）
#   第4.177版（まさちゃん 2026/11/16 10:40）：②説明の 字が 2行に なっても 画面が 上下しない・③5 の 効果は どの ターンでも（使った あとの 手札が のこりの ターンの 数より 少なく ならない とき）・
#     ④お世話トークンを もらった ときは さいごの 画面に「＋○こ GET！」の 札・⑤3 が 3まい → 見せて 1まい 交換・⑥効果を 使うか 聞く 窓（カードの 絵・大きい「使わない」「使う」）
#   第4.178版（まさちゃん 2026/11/16 14:43・15:33）：①BGM（設定で オン／オフ・うしろに 行ったら 止まる）・②5ターン・手札 7まい・③設定の 窓（BGM・効果音・エフェクト）・
#     ④6 の 効果は もう 見た カード しか ない ときは 聞かれない・⑤夜の フィールド（火の あかりの ゆれ）・逆転勝利（1 が 3まい → 神様馬・幻の馬に／2 が 3まい → 1 に：オープンしてから 聞く）
#     前から ある 場面（効果の しくみ）は「3ターン・手札 5まい」の まま 動かす（start() が turns: 3 を わたす）。本番の 形（5ターン・手札 7まい）は「■ 5ターン・手札 7まい」で 見る
#   第4.179版（まさちゃん 2026/11/16 15:47・16:01・16:10・16:18）：バトルコイン（買えない・コンピュータに 勝つと 1枚・5連勝 ごとに 5枚）・部屋の 参加コインと 勝者の 獲得コイン（2倍 まで）
#   第4.188版（まさちゃん 2026/11/17 11:22）：バトルコイン（コンピュータに 勝つと 2枚・3連勝 ごとに ＋6枚・5連勝 ごとに ＋10枚・さいごの 画面の「🔥 ○連勝 ボーナス！」の 札・ログインボーナスで 毎日 2枚〈7日目 ＋10枚〉を 受け取る）
#     ・入れない（足りない）・参加する → 2人とも 出す → 勝者が もらう・同点は もどる・とちゅうで やめた 人は もどらない（相手が もらう：第4.211版から 相手が 3回 セットした あと だけ。その前は 相手に もどる だけ）・つながりが 切れたら もどる
#   第4.183版（まさちゃん 2026/11/16 20:51・20:53）：ミッション（コンピュータ／友だちバトルで 連続勝利 → バトルコイン・毎月 リセット）・友だちバトルは それぞれの デザイン
#   第4.182版（まさちゃん 2026/11/16 20:00・20:09）：デザインカスタム（カードの おもて 18種・うら 7種：バトルコインで 解放＝おもて 300枚・神様馬／幻の馬 500枚・うら 300枚）
#   第4.185版（まさちゃん 2026/11/16 22:39・22:45）：7 の 4まい 公開で 強さ 逆転（効果タイムで 聞く・見せる 窓・捨て札・「強さ 逆転中」・その 対戦が 終わる まで・コンピュータも 使う）・7 の 新しい 絵と カスタムの 名前
#     （23:04）設定の「エフェクト」を なくした（BGM・効果音 だけ・前の 版の fx は すてる）／（23:06）効果を 使った ときの 札（だれが・どの 効果・何を する）／
#     （23:20）プレイボード 7種（デザインカスタムの 3つ目の タブ・1つ 300枚・対戦の ボードの 絵・いつもの 以外は 火の あかりの ゆれ なし）
#   第4.186版（まさちゃん 2026/11/17 00:52）：プレイボード 4つを 新しい 絵に（山札の 札が 左へ 5.86% → この 4つの とき だけ 山札も 左へ：.cbboard.dl）
#   第4.194版（まさちゃん 2026/11/18 10:15「馬と山札重なってる！」）：のこりの 3つ（紫月の夜・黄金の星空・歯車の工房）も 札を 左へ うつした 絵 → 7つ ぜんぶ dl
#   第4.187版（まさちゃん 2026/11/17 09:39）：7 の 4まい 公開は セットの 前（聞く 窓・使わない の あとの 下の ボタン）・セットは いつも ふせて（自分の 場の カードは うら ＋ しるし・相手が 7 を ふせても 見え方は 同じ）
#   第4.188版（まさちゃん 2026/11/17 11:05・11:16）：効果の 順 6 → 7 → 3 → 5 → 4（聞く 順も・4 は いちばん あと）・5 で 捨てる カードは 7・3 の 効果の 分を のこす・相手の 5 の 効果で 来た カードでも 逆転勝利
#   第4.189版（まさちゃん 2026/11/17 15:00・15:18・15:39）：カードパック（1パック 112枚・5まい＝ノーマル 4まい ＋ くじ 1まい：0〜229 の 番号・コイン／カード／記録を いっしょに 保存・2回 しない・記録から もう 1回 見る・パックの 絵）。おもては パックで 集める（コインで 解放は うら・ボード だけ）
#   第4.190版（まさちゃん 2026/11/17 17:14）：6 は ターンの はじめ（配った あとの「6 の 効果」の 帯・聞く 窓「ターンの はじめ！」・相手は 待つ・2人とも 6 が 2まい・使わなかった ふきだし）・
#     効果タイムは 1つずつ（7 を 行って から 5 を 聞く・7 で 引いた カードも 5 で 捨てられる・うっかり 押し 防止は 次の 質問が 出て すぐ）
#   第4.211版（まさちゃん 2026/11/22 21:36「不正にポイントやバトルコイン、お世話トークンを手に入れる抜け穴は無いか全部細かく徹底的に確認して！」）：
#     ・ごほうび（お世話トークン）を わたして いる 途中に もう 1回 よばれても 2回 わたさない（結果の 画面・メニューの 両方が わたす）
#     ・部屋の 相手が にせもの（本物の アプリで ない）でも ズルが できない：「配った → あなたの 勝ち」を くり返し 送られても 勝ち・お世話トークン・ミッション・バトルコインは ふえない・
#       参加コインは もどる・タグに なる 字の 入った 知らせは 画面に 出ない・参加コインの 上限 100枚
#   ルールの 計算は test_cb_rules.js・対戦の 進め役は test_cb_net.js（node）
import json, os, re, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
from toys_for_test import open_toys      # 第4.212版：おもちゃを 0P で 解放した ことに する（テスト用）
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
    open_toys(pg, ('cb',))      # 第4.212版：おもちゃ（3,000P で 解放）。ここでは 0P で 解放した ことに する（解放の 窓は「■ 入口」で 本物の 流れを 見る）
    pg.locator('#cbFab .fabi').click()
    pg.wait_for_function("() => !!window.CBApp && !!document.querySelector('#cbOv.on')", timeout=30000)
    pg.evaluate(f"() => {{ CBApp._t.speed({speed}); CBApp._guard = 0; CBApp._limit = 0; }}"); pg.wait_for_timeout(150)      # 第4.226版：_limit 0＝友達バトルの セットの 時間を 止める（ここの 部屋の 場面は 時間で 自動に ならない ように：時間の 決まりは test_v226.py）。_guard 0：聞く 窓が 出て すぐでも 押せる（テストは すぐ 押す。うっかり 押し 防止は 下で 別に 見る）
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


def start(pg, h0, h1, deck='', turns=3, full=True):
    """手札を 決めて コンピュータと 対戦を はじめる。コンピュータは 自分では 動かない（テストが opp() で 相手の 手を 打つ）。
       turns＝ターンの 数（決めなければ 3：前から ある 場面は「3ターン・手札 5まい」の まま。本番の 形は turns=5 で 手札 7まい）
       full＝決着しても さいごの ターンまで（第4.202版：前から ある 場面の まま 動かす テスト用。本番と 同じ「決着で おわり」は full=False）"""
    pg.evaluate("""([h0, h1, dk, tn, fu]) => { CBApp._think = () => 1e9; CBApp._opt = { hands: [h0.split(''), h1.split('')], deck: dk ? dk.split('') : undefined, turns: tn, full: fu }; }""", [h0, h1, deck, turns, full])
    if pg.evaluate("() => CBApp._t.screen") != 'menu': pg.evaluate("() => CBApp._t.menu()")      # 前の 対戦を（勝ち負けに 数えずに）片付けて メニューへ
    pg.locator('#cbOv .cbmenu [data-cb=cpu]').click(); idle(pg)


def opp(pg, a):
    """相手の 席の 手を 打つ（k＝手札の カードの 種類 で 番号を 探す）"""
    r = pg.evaluate("""a => { const m = CBApp._t.match, S = m._.state(), h = S.p[1].hand, U = k => { const c = h.find(x => x.k === String(k)); return c ? c.u : -1; };
      const b = Object.assign({}, a); if (b.k != null) { b.u = U(b.k); delete b.k; } if (b.dropk != null) { b.drop = Array.isArray(b.dropk) ? b.dropk.map(U) : U(b.dropk); delete b.dropk; }
      if (b.pickk != null) { const c = S.p[0].hand.find(x => x.k === String(b.pickk)); b.pick = c ? c.u : -1; delete b.pickk; }
      if (b.use) { const w = Object.assign({}, b.use); if (w.p6k != null) { const c = S.p[0].hand.find(x => x.k === String(w.p6k)); w.p6 = c ? c.u : -1; delete w.p6k; } if (w.u5k != null) { w.u5 = U(w.u5k); delete w.u5k; } b.use = w; }
      return m._.apply(1, b); }""", a)
    idle(pg)
    return r


def fab_ok(rc, vw, tab):
    """丸い ボタン（順：トレーニングセンター・推し馬・カードバトル・思い出フィギュア）の ならび（第4.230版：下の タブの すぐ 上に 横 1列）。
       左から 順に・となり あう（1つ ぶんの 幅は 同じ・すきま なし）・上が そろう・重ならない・画面の 中・下の タブの すぐ 上（3〜5px）"""
    if len(rc) != 4: return False
    ok = all(abs(rc[i][2] - rc[i + 1][0]) <= 1 and abs(rc[i][1] - rc[i + 1][1]) <= 1 and abs((rc[i][2] - rc[i][0]) - (rc[i + 1][2] - rc[i + 1][0])) <= 1 for i in range(3))
    lap = any(a[0] < c[2] - 1 and c[0] < a[2] - 1 and a[1] < c[3] - 1 and c[1] < a[3] - 1 for i, a in enumerate(rc) for c in rc[i + 1:])
    return bool(ok and not lap and min(r[0] for r in rc) >= 0 and max(r[2] for r in rc) <= vw and 3 <= tab - max(r[3] for r in rc) <= 5)


def fdx(w):
    """横 1列の 丸の 大きさ（tc/tc_launch.js の fabFit と 同じ：1つ ぶんの 幅の 80%・44〜80px・列の 幅は 480px まで）"""
    return max(44, min(80, int((min(w, 480) - 8) / 4 * 0.8)))

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

        print('■ 入口：下の タブの すぐ 上の 丸い ボタン（第4.230版：横 1列）の 左から 3番目 ＝ 推し馬の 右・思い出フィギュアの 左')
        pg.evaluate("() => { const m = document.getElementById('minibar'); if (m) m.hidden = true; }"); pg.wait_for_timeout(500)
        FAB = """() => { const R = e => { const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; };
          const ks = [...document.querySelectorAll('#fabCol > button')].sort((a, b) => getComputedStyle(a).order - getComputedStyle(b).order), c = document.querySelector('#cbFab'), col = document.querySelector('#fabCol');
          if (!c) return null; const im = c.querySelector('.fabi img'), ir = c.querySelector('.fabi').getBoundingClientRect(), hd = document.querySelector('header.top');
          const top = ['planBtn', 'kiseBtn'].map(i => document.getElementById(i)).filter(Boolean);
          return { ids: ks.map(k => k.id), rc: ks.map(R), order: getComputedStyle(c).order, iws: ks.map(k => Math.round(k.querySelector('.fabi').getBoundingClientRect().width)), g2: col.classList.contains('g2'), rw: col.classList.contains('rw'),
            lfs: parseFloat(getComputedStyle(c.querySelector('.fabl')).fontSize), name: c.querySelector('.fabl').textContent, aria: c.getAttribute('aria-label'), img: im ? im.getAttribute('src') : null, nat: im ? im.naturalWidth : 0,
            iw: Math.round(ir.width), tab: Math.round(document.querySelector('.tabbar').getBoundingClientRect().top), hb: Math.round(hd.getBoundingClientRect().bottom), top: top.map(R),
            inHd: top.map(e => e.parentNode === hd && e.classList.contains('dk')), vw: innerWidth, cw: document.documentElement.clientWidth, vh: innerHeight, api: typeof window.TengelCB }; }"""
        pg.wait_for_function("() => !TengelFab.busy()", timeout=8000); pg.wait_for_timeout(300)      # はじめの 2秒は 丸の 大きさを 決め直さない（落ち着いて から）
        fb = pg.evaluate(FAB)
        check(fb is not None and fb['ids'] == ['tcFab', 'oshiFab', 'cbFab', 'figFab'] and fb['order'] == '2' and fb['api'] == 'object',
              f'順は 左から トレーニングセンター → 推し馬 → カードバトル → 思い出フィギュア（まさちゃん 11/16 00:47 の 順・第4.230版：横に）{fb and fb["ids"]}')
        low0 = fb['tab'] - max(r[3] for r in fb['rc'])
        check(fb['name'] == 'TENGER\nカードバトル' and fb['aria'].startswith('TENGERカードバトル') and fb['iws'] == [fdx(fb['cw'])] * 4 and fb['rw'] and not fb['g2'] and 8 <= fb['lfs'] <= 11.5 and fab_ok(fb['rc'], 390, fb['tab']) and 3 <= low0 <= 5,
              f'第4.230版（まさちゃん 11/26 22:46）：下の タブの すぐ 上に 横 1列（すきま {low0}px）・丸い 絵は 4つとも 同じ 大きさ（幅 390 で {fb["iws"][0]}px：1つ ぶんの 幅の 80%）・'
              f'下に 名前の 札「TENGER／カードバトル」（字 {fb["lfs"]}px）・重ならない（{fb["rc"]}）')
        check(len(fb['top']) == 2 and all(fb['inHd']) and all(t[3] <= fb['hb'] + 0.5 for t in fb['top']) and min(r[1] for r in fb['rc']) > fb['hb'] + 300,
              f'作戦会議・壁紙&ボード着せ替えは 上の 帯の 中（下の はし {[t[3] for t in fb["top"]]} ≦ 帯の 下 {fb["hb"]}）＝ 丸い ボタンの 列（上の はし {min(r[1] for r in fb["rc"])}）とは はなれて いる')
        if HAVE:
            check(fb['img'] == 'cb_icon.webp' and fb['nat'] == 240, f'ボタンの 絵（cb_icon.webp・240×240）')
        else:
            check(pg.locator('#cbFab .fabt').count() == 1 and pg.locator('#cbFab .fabt').inner_text() == 'バトル', '絵が ない とき：字の 丸「バトル」')
        shot(pg, 'cb_fab')
        # たての 短い 画面（iPhone SE：375×647）でも 横 1列
        pg2 = ctx.new_page(); pg2.set_viewport_size({'width': 375, 'height': 647}); pg2.goto(APP); pg2.wait_for_timeout(1300); gate(pg2); pg2.wait_for_timeout(600)
        pg2.evaluate("() => { const m = document.getElementById('minibar'); if (m) m.hidden = true; }"); pg2.wait_for_timeout(400)
        pg2.wait_for_function("() => !TengelFab.busy()", timeout=8000); pg2.wait_for_timeout(300)
        f2 = pg2.evaluate(FAB); low2 = f2['tab'] - max(r[3] for r in f2['rc'])
        check(f2['ids'] == ['tcFab', 'oshiFab', 'cbFab', 'figFab'] and f2['iws'] == [fdx(f2['cw'])] * 4 and f2['rw'] and not f2['g2'] and fab_ok(f2['rc'], 375, f2['tab']) and 3 <= low2 <= 5 and all(f2['inHd']),
              f'たての 短い 画面（iPhone SE：375×647）：横 1列・丸 {f2["iws"][0]}px・下の タブの すぐ 上（すきま {low2}px）・作戦会議と 着せ替えは 上の 帯の 中')
        shot(pg2, 'cb_fab_small')
        # 上の絵が ある とき（壁紙。ここでは 同じ 高さの 箱を 入れて ためす）：第4.230版から 丸の 大きさは 画面の 幅 だけで 決まる（前は 着せ替えの ボタンの 下に おさまる 大きさ）。
        #   本物の iPhone の 大きさ（アプリの 画面＝iPhone の 高さ − 上の 時計の 帯・下は ホームバーの ぶん）で
        pg2.evaluate("() => { const v = document.getElementById('v-judge'), s = document.createElement('div'); s.id = 'cbSp'; s.style.height = '158px'; v.insertBefore(s, v.firstChild); }")
        sizes = {}
        for dn, vw3, vh3, sab3 in (('iPhone SE', 375, 647, 0), ('iPhone 12/13 mini', 375, 762, 34), ('iPhone 12〜14', 390, 797, 34), ('iPhone 16 Pro', 402, 812, 34), ('iPhone Plus／Pro Max', 430, 873, 34)):
            pg2.set_viewport_size({'width': vw3, 'height': vh3}); pg2.evaluate("(s) => document.documentElement.style.setProperty('--bottom-inset', s + 'px')", sab3); pg2.wait_for_timeout(500)
            pg2.wait_for_function("() => !TengelFab.busy()", timeout=8000); pg2.wait_for_timeout(300)
            f3 = pg2.evaluate(FAB); low3 = f3['tab'] - max(r[3] for r in f3['rc']); d3 = f3['iws'][0]; sizes[dn] = d3
            check(f3['iws'] == [fdx(f3['cw'])] * 4 and 44 <= d3 <= 80 and f3['rw'] and not f3['g2'] and fab_ok(f3['rc'], vw3, f3['tab']) and 3 <= low3 <= 5 and f3['lfs'] >= 8 and all(f3['inHd']),
                  f'{dn}（アプリの 画面 {vw3}×{vh3}・下の あき {sab3}・上の絵 あり）：横 1列・丸 {d3}px（名前の 字 {round(f3["lfs"], 1)}px）・下の タブの すぐ 上（すきま {low3}px）')
        check(sizes['iPhone 12/13 mini'] < sizes['iPhone 12〜14'] < sizes['iPhone Plus／Pro Max'] and 70 <= sizes['iPhone 12〜14'] <= 80 and sizes['iPhone SE'] == sizes['iPhone 12/13 mini'], f'丸の 大きさは 画面の 幅が 広い ほど 大きい（たての 長さには よらない）{sizes}')
        pg2.evaluate("() => { document.documentElement.style.removeProperty('--bottom-inset'); document.getElementById('cbSp').remove(); }")

        print('■ おもちゃの 解放（第4.212版：TENGERカードバトルは 3,000P で 解放）')
        tl0 = pg.evaluate("() => ({ lock: document.querySelector('#cbFab').classList.contains('lock'), cbl: TengelCB.locked(), al: document.querySelector('#cbFab').getAttribute('aria-label'), mark: getComputedStyle(document.querySelector('#cbFab'), '::before').content, total: TengelWallet.total(), has: TengelWallet.toy.has('cb') })")
        check(tl0['lock'] and tl0['cbl'] and not tl0['has'] and '🔒' in tl0['mark'] and 'おもちゃ' in tl0['al'] and tl0['total'] == 5000, f'まだ 解放して いない：丸い ボタンに 🔒・読み上げは「おもちゃ：ポイントで 解放すると 遊べるよ」（{tl0}）')
        qt0 = pg.evaluate("() => [...document.querySelectorAll('#cbFab .fabc')].filter(e => !e.hidden).length")
        check(qt0 == 0, f'第4.221版：まだ 解放して いない ときは 調査隊切符の 枚数を 出さない（🔒 だけ：{qt0}）')
        pg.locator('#cbFab .fabi').click(); pg.wait_for_selector('#toyOv', timeout=10000); pg.wait_for_timeout(200)
        td0 = pg.evaluate("() => { const o = document.querySelector('#toyOv'), b = o.querySelector('.toybox').getBoundingClientRect(), cs = getComputedStyle(o); return { t: o.innerText.replace(/\\s+/g, ' '), role: o.getAttribute('role'), modal: o.getAttribute('aria-modal'), z: +cs.zIndex, inside: b.left >= 0 && b.right <= innerWidth && b.top >= 0 && b.bottom <= innerHeight, btn: [...o.querySelectorAll('[data-toy]')].map(x => x.dataset.toy + ':' + x.textContent), cb: !!document.querySelector('#cbOv.on'), bundle: !!window.CBApp, fab: document.querySelector('#cbFab').disabled }; }")
        check('TENGERカードバトル' in td0['t'] and '3,000Pで解放すると、ずっと遊べるよ' in td0['t'] and '今 5,000P' in td0['t'] and td0['btn'] == ['go:3,000Pを使って解放する', 'no:やめる'] and td0['role'] == 'dialog' and td0['modal'] == 'true' and td0['z'] >= 100 and td0['inside'] and not td0['cb'] and not td0['bundle'],
              f'押すと 解放の 窓（「3,000Pを使って解放する」「やめる」・今の ポイント）：カードバトルは まだ 開かない・本体も まだ 読まない（{td0["t"][:60]}…・{td0["btn"]}）')
        shot(pg, 'cb_toy_ask')
        pg.locator('#toyOv [data-toy=no]').click(); pg.wait_for_timeout(300)
        td1 = pg.evaluate("() => ({ ov: !!document.querySelector('#toyOv'), cb: !!document.querySelector('#cbOv.on'), total: TengelWallet.total(), has: TengelWallet.toy.has('cb'), fab: document.querySelector('#cbFab').disabled, lock: document.querySelector('#cbFab').classList.contains('lock') })")
        check(td1 == {'ov': False, 'cb': False, 'total': 5000, 'has': False, 'fab': False, 'lock': True}, f'「やめる」→ 何も 減らない・開かない・ボタンは また 押せる（{td1}）')
        # 足りない とき（2,900P）：「ポイントを買う」
        pg.evaluate("async () => { const s = TengelWallet.snapshot(); s.events.push({ id: 'spend-test-cb', kind: 'spend', bucket: '', amount: -2100, at: new Date().toISOString(), what: 'テスト', device: 'test', use: { paid_sub: 0, paid_pack: 0, free: 2100 }, n: 99 }); await TengelWallet.restore(s); }"); pg.wait_for_timeout(200)
        pg.locator('#cbFab .fabi').click(); pg.wait_for_selector('#toyOv', timeout=10000); pg.wait_for_timeout(200)
        td2 = pg.evaluate("() => { const o = document.querySelector('#toyOv'); return { t: o.innerText.replace(/\\s+/g, ' '), btn: [...o.querySelectorAll('[data-toy]')].map(x => x.dataset.toy + ':' + x.textContent), total: TengelWallet.total() }; }")
        check(td2['total'] == 2900 and 'ポイントが足りないよ（あと 100P）' in td2['t'] and td2['btn'] == ['buy:ポイントを買う', 'no:やめる'], f'足りない とき（今 2,900P）：「ポイントが足りないよ（あと 100P）」・「ポイントを買う」「やめる」（解放する は 出ない）（{td2["btn"]}）')
        pg.locator('#toyOv [data-toy=buy]').click(); pg.wait_for_timeout(600)
        td3 = pg.evaluate("() => ({ toy: !!document.querySelector('#toyOv'), pt: !!document.querySelector('#ptOv'), z: document.querySelector('#ptOv') ? +getComputedStyle(document.querySelector('#ptOv')).zIndex : 0, cb: !!document.querySelector('#cbOv.on') })")
        check(not td3['toy'] and td3['pt'] and td3['z'] >= 100 and not td3['cb'], f'「ポイントを買う」→ 解放の 窓は 閉じて ポイントの 窓が 出る（{td3}）')
        pg.evaluate("() => TengelWallet.closePoints()"); pg.wait_for_timeout(300)
        pg.evaluate("async () => { const s = TengelWallet.snapshot(); s.events = s.events.filter(e => e.id !== 'spend-test-cb'); await TengelWallet.restore(s); }"); pg.wait_for_timeout(200)
        # 解放する（本物の 流れ：5,000 → 2,000P）→ そのまま 開く
        pg.locator('#cbFab .fabi').click(); pg.wait_for_selector('#toyOv', timeout=10000); pg.wait_for_timeout(200)
        pg.locator('#toyOv [data-toy=go]').click()
        pg.wait_for_function("() => !!window.CBApp && !!document.querySelector('#cbOv.on')", timeout=30000); pg.wait_for_timeout(300)
        td4 = pg.evaluate("() => ({ toy: !!document.querySelector('#toyOv'), total: TengelWallet.total(), has: TengelWallet.toy.has('cb'), drop: TengelWallet.toy.has('drop'), lock: document.querySelector('#cbFab').classList.contains('lock'), ev: TengelWallet.events().filter(e => e.id === 'unlock-toy:cb').map(e => e.amount + ':' + e.what).join(), al: document.querySelector('#cbFab').getAttribute('aria-label'), scr: CBApp._t.screen })")
        check(td4 == {'toy': False, 'total': 2000, 'has': True, 'drop': False, 'lock': False, 'ev': '-3000:toy:cb', 'al': 'TENGERカードバトル（調査隊切符 15枚・押すと 開くよ）', 'scr': 'menu'},
              f'「3,000Pを使って解放する」→ 5,000 → 2,000P・台帳に 1件・🔒 が 消えて、そのまま カードバトルが 開く（お世話チャレンジは べつ：まだ）（{td4}）')
        pg.evaluate("() => CBApp.close()"); pg.wait_for_timeout(300)
        qt1 = pg.evaluate("() => { const e = document.querySelector('#cbFab .fabc.qt'), r = e && e.getBoundingClientRect(), f = document.querySelector('#cbFab .fabi').getBoundingClientRect(); return e ? { t: e.textContent, hid: e.hidden, ah: e.getAttribute('aria-hidden'), in: r.right <= innerWidth && r.top >= f.top - 8 && r.right <= f.right + 8 && r.width > 15 } : null; }")
        check(qt1 == {'t': '15', 'hid': False, 'ah': 'true', 'in': True}, f'第4.221版（まさちゃん 11/25 12:07「調査隊切符も同じようにしてほしい！」）：解放 したら 丸の 右上に 今の 調査隊切符の 枚数（はじめは 15枚・画面から はみ出さない：{qt1}）')

        print('■ メニュー・遊び方')
        open_cb(pg)
        m = pg.evaluate("() => ({ scr: CBApp._t.screen, h1: document.querySelector('#cbOv .cbmenu h1').textContent, rec: document.querySelector('#cbOv .cbmenu .rec').textContent, btn: [...document.querySelectorAll('#cbOv .cbmenu .cbb')].map(b => b.textContent.replace(/\\s+/g, ' ').trim()), dis: [...document.querySelectorAll('#cbOv .cbmenu .cbb')].map(b => b.disabled), lg: document.querySelector('#cbOv .cbmenu .lg').naturalWidth })")
        check(m['scr'] == 'menu' and m['h1'].replace('\n', '').replace(' ', '') == 'TENGERカードバトル' and m['btn'] == ['← 戻る', 'コンピュータと 対戦', '⚔️ 決戦調査今月 0／12 討伐・次は レベル1', '部屋を 作る友達と 対戦', '部屋に 入る友達と 対戦', '遊び方', '設定BGM・効果音', '🎯ミッション今月 0／23 達成', 'デザインカスタムカードパック・裏・ボード'] and not any(m['dis']),
              f'メニュー：コンピュータと 対戦・⚔️ 決戦調査（第4.196版）・部屋を 作る・部屋に 入る・遊び方・設定（第4.178版）・ミッション（第4.183版）・デザインカスタム（第4.182版）（{m["btn"]}）')
        check(m['rec'] == 'コンピュータに 3連勝 ごとに 調査隊切符 1枚・5連勝 ごとに 調査隊切符 2枚' and 'お世話トークン' not in m['rec'] and (not HAVE or m['lg'] == 720), f'ご褒美の 説明（第4.212版：お世話トークンは なし・連勝で 調査隊切符）（{m["rec"]}）')
        cl = pg.evaluate("() => { const e = document.querySelector('#cbOv .cbmenu .cbcoinl'); return e ? [e.textContent, e.querySelectorAll('img[src=\"cb_coin.webp\"]').length] : null; }")
        check(cl == ['バトルコイン 0枚コンピュータに 勝つと 2枚（3連勝 ＋6枚・5連勝 ＋10枚）毎日の ログインボーナスで 2枚（7日目 ＋10枚）', 1], f'メニューに バトルコイン（第4.179版：コインの 絵・持って いる 数・もらい方 → 第4.188版：勝つと 2枚・3連勝 ＋6・5連勝 ＋10・ログインボーナス）（{cl}）')
        check(reqs.count('cb_bundle.js') == 1 and 'cb_bundle.js' not in reqs[:reqs.index('cb_bundle.js')][:5], '本体（cb_bundle.js）は ボタンを 押した ときに 1回 だけ 読む')
        shot(pg, 'cb_menu')
        pg.locator('#cbOv .cbmenu [data-cb=help]').click(); pg.wait_for_timeout(200)
        ht = pg.evaluate("() => document.querySelector('#cbOv .cbhelp .bd').textContent")      # 第4.225版：「そのほか」は 開いて 読む（閉じて いても 中の 字は ある）
        need = ['5ターン 終わって', '2枚は 使わずに 残るよ', '勝った 数が 多い 人の 勝ち', '1 が 一番 強くて、7 が 一番 弱い', '4 同士で 2人とも 4 の 効果を 使った ときは ドロー', '1〜7 が 4枚 ずつ・神様馬 1枚・幻の馬 1枚', 'セットしたら もう 変えられない', '同じ 効果を 2人とも 使える ときは、2人とも 決めて から 一緒に 出る',
                '終わった ターンの 捨て札', '効果で 捨てた カード', '【3枚】と【4枚】は 1ターンに どちらか 1つ', 'セットした カードは 裏（4 の 効果で 見せる か、オープン するまで）', '相手の 手札は いつも 本当の 手札の まま 見えるよ（見た カードを 相手が セットしたら、その カードは 相手の 手札から 消える）',
                '効果を 使うと、ボードの 真ん中に 誰が・どの 効果を・何を するかの 札が 出るよ（タップすると すぐ 次へ）', '残りの ターンの 数より 少なく ならない とき', '最後の ターンは、手札が 1枚 あれば 使える', '4：見せて 強制交換', 'コンピュータに 勝つと バトルコイン', 'コンピュータに 3連勝 ごとに 調査隊切符 1枚・5連勝 ごとに 調査隊切符 2枚（15連勝 など、両方の ときは 両方。調査隊切符は 15枚 まで）',
                '部屋番号（4桁）', '近くに いる 友達', 'もう 見た カード だけの ときは 使えないよ', 'まだ 見て いない カードが ある とき', 'メニューの「デザインカスタム」で、カードの 表・裏と プレイボードの デザインを 変えられるよ', 'コンピュータと 対戦する ときは、コンピュータの カード（裏・表）も あなたが 選んだ デザインに なるよ',
                '友達と 対戦する ときは、あなたの カードは あなたの デザイン・友達の カードは 友達が 選んだ デザインで 出るよ（山札は あなたの 裏）', 'メニューの「ミッション」：コンピュータに 連続勝利・友達バトルで 連続勝利・決戦調査（決戦宝石を 残して 連続勝利）で バトルコインが もらえるよ', '決戦調査（1つの 調査で 数える・宝石を ○個 以上 残せば 達成）：宝石 3個 残し 3連勝 30枚・5連勝 60枚・6連勝 90枚／宝石 4個 残し 3連勝 50枚・5連勝 100枚・6連勝 150枚／宝石 5個 残し 3連勝 90枚・5連勝 180枚・6連勝 270枚',
                'コンピュータ：3連勝 30枚・5連勝 60枚・6連勝 90枚・7連勝 120枚・8連勝 150枚・9連勝 200枚・10連勝 300枚', '友達バトル：3連勝 20枚・5連勝 40枚・6連勝 60枚・7連勝 80枚・8連勝 100枚・9連勝 120枚・10連勝 140枚', '毎月 1日に リセット（達成も 連勝も 0 に 戻る）',
                'コンピュータ・友達バトル・決戦調査は 別に 数えるよ（決戦調査の 勝ち負けは いつもの ミッションに 数えない）', 'カードの 表は カードパックで 集めるよ：1パック バトルコイン 112枚・5枚入り（ノーマル 4枚 ＋ くじの 1枚）', 'くじの 1枚：レア 2パックに 1枚・超レア 5パックに 1枚（どちらも 神様馬・幻の馬を 含む）・神様馬／幻の馬の レア 10パックに 1枚・神様馬／幻の馬の 超レア 23パックに 1枚（どれも 平均。詳しい 確率は カードパックの「出る 確率」）',
                '新しい カードは 持って いる カードに 入るよ（同じ カードが 出ても、数は 増えないよ）。開けた パックは「パックの 記録」で もう 1回 見られるよ', 'カードの 裏 300枚・プレイボード 300枚は バトルコインで 1つずつ 解放できるよ。いつもの デザインは 初めから 使えるよ', '音（設定）', 'BGM・効果音を オン／オフ',
                'プレイボードは、あなたの 画面に 出るよ（友達と 対戦する ときも、あなたの 画面は あなたが 選んだ ボード）', '勝ちに できるよ', 'バトルコイン', 'コンピュータに 勝つと 2枚 もらえるよ', '連勝すると ボーナス：3連勝 ごとに ＋6枚・5連勝 ごとに ＋10枚（15連勝 など、両方の ときは 両方）', '毎日の ログインボーナスでも 2枚（7日目は ＋10枚）もらえるよ',
                '買う ことは できない', '参加コイン', '参加コインの 2倍 まで', '同じ 数の 参加コインを 持って いないと 入れない', 'テンゲルから 獲得コインを プレゼントで もらえる', '同点は 参加コインが 戻る', '途中で やめると、参加コインは 戻らない', 'TENGERカードバトルは、馬の カードで 戦う ゲームだよ', '5ターンで 勝負',
                '手札 7枚から 1枚ずつ 出す', '勝った 数が 多い 人の 優勝', 'いちばん 強い！', '数字の 最強', '一番 弱い', '数字は 1 が 一番 強くて、7 が 一番 弱いよ', '同じ 数字が ぶつかったら「かぶり」＝ どちらも 負け（4 同士で 2人とも 4 の 効果を 使った ときは ドロー）', '神様馬 と 幻の馬が ぶつかったら 引き分け',
                '7 の 効果（4枚 公開）で 強さ 逆転したら、その 対戦が 終わる まで 7＞6＞5＞4＞3＞2＞1（神様馬・幻の馬は 一番 強い まま。上に「強さ 逆転中」と 出るよ）', 'カードは 全部で 30枚：1〜7 が 4枚 ずつ・神様馬 1枚・幻の馬 1枚', '手札は 7枚（2人とも 山札から 配られるよ）', '5ターン 戦うよ。1ターンに 1枚ずつ 出すから、2枚は 使わずに 残るよ（ターンの 間に 山札から 引かない）',
                '2人とも カードを 伏せて セット → 一緒に めくって、強い 方の 勝ち', '5ターン 終わって 勝った 数が 多い 人の 勝ち（同じ なら 同点）。先に 勝ちが 決まったら（3勝した・残りを 全部 勝っても 追いつけない）その ターンで 試合終了', '相手は コンピュータ か、近くに いる 友達（部屋を 作って 対戦）。決戦調査では 強い 敵と 連続で 戦うよ',
                'ターンの 始め手札に 6 が 2枚 ある 人は「6 の 効果」・前の ターンに 神様馬・幻の馬で 勝った 人は その 効果を 使えるよ', 'セット手札から 1枚 選んで 伏せて 出す（自分の カードには 数字の 印・タップで 見られる）。セットしたら もう 変えられないよ。7・3 の 効果と 決戦宝石は セットの 前に 使えるよ（使った 後で セットする カードを 選べる）',
                '効果タイム2人とも セットしたら、セットした 5 → 4 の 順に 効果を 使うか 聞かれるよ（1つ 終わってから 次。同じ 効果を 2人とも 使える ときは、2人とも 決めて から 一緒に 出る）', 'オープン2枚 一緒に めくって 勝ち負け。負けた 人は 1・2 の 逆転勝利を 使えるかも', '効果は 使うか 使わないか 自分で 選べるよ',
                '選べる カードが 金色に 光る', '金の ふち＝その 効果に かかわる カード', '効果で 来た カード・見た カード・見られた カードは 少しの 間 強く 光るよ', '神様馬：相手の 手札を 見る', '勝った 次の ターンの 始め', '相手の 手札を 1枚 選んで 見られるよ（まだ 見て いない カードが ある とき）', '幻の馬：手札を 入れかえ',
                '手札を 2枚 捨てて、山札から 2枚 引けるよ', '1：逆転勝利', '場の 1 ＋ 手札の 1 が 2枚', '1 を 出して 神様馬・幻の馬に 負けた とき、手札の 1 を 2枚 見せて 1枚 捨てると 勝ちに できるよ', '2：逆転勝利', '2 を 出して 1 に 負けた とき、手札の 2 を 2枚 見せて 1枚 捨てると 勝ちに できるよ',
                '1・2 とも、捨てた 後の 手札が 残りの ターンの 数より 少なく ならない とき だけ', '3：3枚 見せて 交換', '手札に 3 が 3枚', '3枚を 見せて、その 1枚と、相手の 手札から 自分で 選んだ 1枚を 交換。見えて いる カード（もう 見た カード）も 選べるよ（裏の カードは 何が 来るか わからない）', '手札に あれば 使える（3 を セットしなくて いい）・トークンは 選べない',
                '4：見せて 強制交換', '効果タイム（いちばん 後）', '4 を 先に 見せる かわりに、相手は セットした カードを 手札の 別の カードと 交換しないと いけないよ。2人とも 4 の 効果を 使ったら その ターンは ドロー。交換で 5 を セットしたら、5 の 効果も 使えるよ', '4 は 一番 後：相手が 5 の 効果で 山札から 伏せた カードも 交換に なるよ',
                '5：山札から 伏せて セット', '5 と 手札 1枚を 捨てて、山札から 1枚を 伏せて セット。何が 出るかは オープンまで 分からない！', '使った 後の 手札が 残りの ターンの 数より 少なく ならない とき だけ（最後の ターンは、手札が 1枚 あれば 使える）', '6：相手の 手札を 見る', '手札に 6 が 2枚',
                '2枚を 相手に 見せて、相手の 手札を 1枚 選んで 見るよ。見てから セットする カードを 選べる。相手の 手札が もう 見た カード だけの ときは 使えないよ', '7：3枚 交換・4枚で 強さ 逆転', '【3枚】3枚を 山札に 戻して、新しく 3枚 引くよ', '【4枚】4枚 見せて 1枚 捨てると、その 対戦が 終わる まで 強さが 逆（7＞6＞…＞1）',
                '【3枚】と【4枚】は 1ターンに どちらか 1つ。手札に あれば 使える（7 を セットしなくて いい）', '効果の 順番', 'ターンの 始め：6 → 神様馬・幻の馬', 'セットの 前：7・3・決戦宝石', '効果タイム：5 → 4', 'オープンの 後：1・2', '手札の 数は、6・7・3 は セットする 前、5 は セットした あとの 手札で 数えるよ',
                '最後の ターンに 神様馬・幻の馬で 勝った ときは、次の ターンが ない ので 効果は ないよ', '効果は 1つ 終わってから 次の 効果を 聞くよ（前の 効果で 変わった 手札で 決められる。例：7 で 引いた 後の 手札で セットする カードを 選ぶ・5 で 捨てる カードを 選ぶ）', 'いつも 使える！1つの 調査（連勝が 続く 間）で 5つを 1回ずつ',
                '部屋を 作る 人が「決戦宝石 あり」に した とき。2人とも 1試合で 5つを 1回ずつ（おたがいの 宝石が 見える）', 'コンピュータとの 対戦使えないよ', '手札の 下の ケースに 宝石が 並ぶよ。タップ →「使う」で、トークンの カードが 手札に 1枚 来るよ', '使えるのは 手札が 6枚 以下・セットの 前・1ターンに 1つ',
                'トークンは その ターン だけ（使わないと ターンの 終わりに 消えるよ）', '決戦調査の 敵は 宝石を 使わないよ（あなたが 使った ことも 敵には わからない）', 'カードの 絵を タップすると 大きく 見られるよ']
        miss = [x for x in need if x not in ht] + [x for x in ('エフェクト', '光や 動きの 演出', 'お世話トークン') if x in ht]      # 第4.185版：エフェクトの 設定は なくした・第4.212版：お世話トークンの ごほうびも なくした
        check(pg.evaluate("() => CBApp._t.screen") == 'help' and not miss and pg.locator('#cbOv .cbhelp .hrank .hcd img').count() == 9 and pg.locator('#cbOv .cbhelp .hef').count() == 9 and pg.locator('#cbOv .cbhelp .hef > .hcd img[src="cb_s3.webp"]').count() == 1 and pg.locator('#cbOv .cbhelp .hef > .hcd img[src="cb_s1.webp"]').count() == 1 and pg.locator('#cbOv .cbhelp .hef > .hcd img[src="cb_s2.webp"]').count() == 1,
              f'遊び方（第4.225版：絵の 説明書）：勝負の 仕方（手札 7枚・5ターン）・1ターンの 流れ（セット → 効果タイム → オープン）・強さの 順位表（カード 9枚の 絵）・効果 9つ（カードの 絵つき）・どの 効果も 自分で 選べる・決戦宝石・捨て札・ご褒美・設定・部屋（ない 文 {miss}）')
        shot(pg, 'cb_help')
        pg.locator('#cbOv [data-cb=helpx]').click(); pg.wait_for_timeout(150)
        check(pg.evaluate("() => CBApp._t.screen") == 'menu', '戻る → メニュー')

        print('■ コンピュータと 対戦：セット → オープン → 3ターン')
        start(pg, '12367', '23567')
        v = pg.evaluate(V)
        check(pg.evaluate("() => CBApp._t.screen") == 'game' and v['turn'] == 1 and pg.evaluate(DOMHAND) == '12367' and pg.locator('#cbOv .cbohand .cbc').count() == 5 and pg.locator('#cbOv .cbdeck .cbn').inner_text() == '20' and pg.locator('#cbOv .cbdis .cbn').inner_text() == '0'
              and pg.locator('#cbOv .cbturn').inner_text().replace('\n', '') == 'ターン 1／3' and pg.locator('#cbOv .cbopp .cbwho b').inner_text() == 'コンピュータ' and pg.evaluate(PIPS) == '0-0',
              f'はじめ：手札 5枚（強い 順）・相手の 手札 5枚（裏）・山札 20・捨て札 0・ターン 1／3（{pg.evaluate(DOMHAND)}）')
        check(all(s == 'cb_sb.webp' for s in pg.evaluate("() => [...document.querySelectorAll('#cbOv .cbohand .cbc img')].map(i => i.getAttribute('src'))")) and 'セットする カードを 選んでね' in pg.evaluate(MSG) and pg.locator('#cbOv .cbglow.on').count() == 1 and acts(pg) == [],
              '相手の 手札は 全部 裏・「セットする カードを 選んでね」・自分の わくが 光る')
        geo = pg.evaluate("""() => { const R = s => { const r = document.querySelector('#cbOv ' + s).getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; };
          const cs = [...document.querySelectorAll('#cbOv .cbhand .cbc')].map(c => c.getBoundingClientRect());
          return { top: R('.cbtop'), opp: R('.cbohand'), board: R('.cbboard'), msg: R('.cbmsg'), hand: R('.cbhand'), act: R('.cbact'), cw: Math.round(cs[0].width), ch: Math.round(cs[0].height), left: Math.round(cs[0].left), right: Math.round(cs[4].right), step: Math.round(cs[1].left - cs[0].left) }; }""")
        check(geo['top'][3] <= geo['opp'][1] and geo['opp'][3] <= geo['board'][1] + 30 and geo['board'][3] <= geo['msg'][1] + 20 and geo['msg'][3] <= geo['hand'][1] + 30 and geo['hand'][3] <= geo['act'][1] + 1 and geo['act'][3] <= 844
              and geo['board'][0] == 0 and geo['board'][2] == 390 and abs((geo['board'][3] - geo['board'][1]) - 390 * 941 / 1672) < 2 and geo['left'] >= 0 and geo['right'] <= 390 and abs(geo['ch'] - geo['cw'] * 1.5) < 1.5 and geo['step'] >= geo['cw'] * 0.59,
              f'並び：上から 相手の 手札 → ボード（幅 いっぱい・絵の たて横の まま）→ 言葉 → 手札 → ボタン。手札は 画面の 中・重なりは 40% まで（カード {geo["cw"]}×{geo["ch"]}・ずれ {geo["step"]}）')
        shot(pg, 'cb_turn1')
        tap(pg, '1')
        md = pg.evaluate("() => ({ on: CBApp._t.modOn(), img: document.querySelector('#cbOv .cbmod .big img').getAttribute('src') })")
        check(md['on'] and md['img'] == 'cb_c1.webp' and modbtns(pg) == ['この カードを セットするセットしたら もう 変えられないよ', '戻る'], f'カードを タップ → 大きい カード（cb_c1.webp）と「この カードを セットする（セットしたら もう 変えられないよ）」「戻る」（{modbtns(pg)}）')
        shot(pg, 'cb_card')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(80)
        check(not pg.evaluate("() => CBApp._t.modOn()") and pg.evaluate(V)['my']['set'] is None, '戻る → 何も セットして いない（押す までは 選び直せる）')
        print('■ セットしたら もう 変えられない（まさちゃん 23:12）')
        play(pg, '1')
        v = pg.evaluate(V)
        check(v['my']['set'] and v['my']['set']['k'] == '1' and pg.evaluate(SLOT) == '- b[1]:伏せて セット' and pg.locator('#cbOv .cbslot.my .cbc').get_attribute('aria-label') == 'あなたが 伏せて セットした カード（1）' and pg.evaluate(DOMHAND) == '2367' and 'コンピュータが 選んで いるよ' in pg.evaluate(MSG) and pg.locator('#cbOv .cbglow.on').count() == 0,
              f'セットした：自分の わくに 伏せた カード（第4.187版：裏 ＋ 印「1」・「伏せて セット」）・手札 4枚・「コンピュータが 選んで いるよ…」（{pg.evaluate(SLOT)}）')
        tap(pg, '2')
        check(modbtns(pg) == ['戻る'], 'セットした あとは 手札を タップしても 見る だけ（「セットする」は 出ない）')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        pg.locator('#cbOv .cbslot.my .cbc').click(); pg.wait_for_timeout(80)
        check(modbtns(pg) == ['戻る'] and 'もう 変えられない' in pg.locator('#cbOv .cbmod').inner_text() and pg.locator('#cbOv .cbmod .big img').get_attribute('src') == 'cb_c1.webp', 'セットした カードを タップ → 見る だけ（「もう 変えられない」）')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        r2 = pg.evaluate("async () => { const v = CBApp._t.view, a = await CBApp._t.match.act({ t: 'set', u: v.my.hand[0].u }), b = await CBApp._t.match.act({ t: 'swap', u: v.my.hand[0].u }); return [a.ok, b.ok, CBApp._t.match._.state().p[0].set.c.k, CBApp._t.match._.state().p[0].hand.length]; }")
        check(r2 == [False, False, '1', 4], f'もう 1枚 セットする 手・入れかえる 手を 送っても 受けつけない（セットした 1 の まま）{r2}')
        pg.evaluate("() => { window.__seen = []; const mo = new MutationObserver(() => { const m = document.querySelector('#cbOv .cbmod'); if (m.classList.contains('cbopen')) { const t = m.querySelector('.cbres'); window.__seen.push((m.querySelector('h3') || {}).textContent + '|' + (t ? t.textContent : '') + '|' + [...m.querySelectorAll('.cbflip img.fc')].map(i => i.getAttribute('src')).join(',')); } }); mo.observe(document.querySelector('#cbOv .cbmod'), { childList: true, subtree: true, attributes: true, characterData: true }); window.__mo = mo; }")
        said(pg)
        r = opp(pg, {'t': 'set', 'k': 2})
        seen = pg.evaluate("() => window.__seen"); sd = said(pg)
        v = pg.evaluate(V)
        check(r['ok'] and any('ターン 1　オープン！' in s and '勝ち！' in s and '1 が 2 に 勝ったよ' in s and 'cb_c1.webp,cb_c2.webp' in s for s in seen) and not any('効果タイム' in s for s in sd),
              f'相手も セットした（使える 効果は ない）→ そのまま オープン：大きい カード 2枚（自分 1・相手 2）「勝ち！ 1 が 2 に 勝ったよ」（{seen[-1] if seen else None}）')
        check(v['turn'] == 2 and v['my']['wins'] == 1 and pg.evaluate(PIPS) == '0-1' and pg.evaluate(SLOT) == '- -' and pg.locator('#cbOv .cbdis .cbn').inner_text() == '2' and pg.locator('#cbOv .cbturn').inner_text().replace('\n', '') == 'ターン 2／3' and pg.locator('#cbOv .cbohand .cbc').count() == 4,
              f'2ターン目：勝った 印 1つ・出した 2枚は 捨て札（2）・わくは 空（印 {pg.evaluate(PIPS)}）')
        print('■ 捨て札を タップ → 確認できる（まさちゃん 23:15）')
        dg = pg.evaluate("""() => { const R = s => { const e = document.querySelector('#cbOv ' + s); if (!e) return null; const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)]; };
          const b = document.querySelector('#cbOv .cbdis'), c = b.getBoundingClientRect(), hit = document.elementFromPoint(c.left + c.width / 2, c.top + c.height / 2);
          return { btn: R('.cbdis'), pile: R('.cbdis .pl img'), src: document.querySelector('#cbOv .cbdis .pl img').getAttribute('src'), n: b.querySelector('.cbn').textContent, aria: b.getAttribute('aria-label'), hit: !!hit && (hit === b || b.contains(hit)), slot: R('.cbslot.my'), deck: R('.cbdeck'), board: R('.cbboard') }; }""")
        check(dg['src'] == 'cb_s2.webp' and dg['n'] == '2' and dg['aria'] == '捨て札を 見る（2枚）' and dg['pile'][2] >= 30 and dg['hit'] and dg['btn'][2] >= 44 and dg['btn'][3] >= 44
              and dg['btn'][0] + dg['btn'][2] <= dg['slot'][0] and dg['btn'][0] >= 0 and dg['btn'][1] >= dg['board'][1] and dg['btn'][1] + dg['btn'][3] <= dg['board'][1] + dg['board'][3],
              f'ボードの 捨て札：1番 上の カード（最後に 捨てた 2）が 見える・数（2）・押せる 広さ {dg["btn"][2]}×{dg["btn"][3]}（44 以上）・真ん中の わくに かからない')
        pg.locator('#cbOv [data-cb=discard]').click(); pg.wait_for_timeout(80)
        DM = """() => { const m = document.querySelector('#cbOv .cbmod'); return { h: (m.querySelector('h3') || {}).textContent, h4: [...m.querySelectorAll('.cbdl h4')].map(x => x.textContent),
          turns: [...m.querySelectorAll('.cbdl .row[data-dt]')].map(r => r.querySelector('b').textContent + '|' + [...r.querySelectorAll('.pr')].map(p => p.querySelector('span').textContent + '=' + [...p.querySelectorAll('img')].map(i => i.getAttribute('src').replace('cb_s', '').replace('.webp', '')).join('')).join('|')),
          effs: [...m.querySelectorAll('.cbdl .row[data-de]')].map(r => r.querySelector('b').textContent + '|' + [...r.querySelectorAll('.pr')].map(p => p.querySelector('span').textContent + '=' + [...p.querySelectorAll('img')].map(i => i.getAttribute('src').replace('cb_s', '').replace('.webp', '')).join('')).join('|')),
          none: [...m.querySelectorAll('.cbdl .none')].map(x => x.textContent), t: m.textContent }; }"""
        dm = pg.evaluate(DM)
        check(dm['h'] == '捨て札（2枚）' and dm['h4'] == ['終わった ターンの 捨て札', '効果で 捨てた カード'] and dm['turns'] == ['ターン 1|あなた=1|コンピュータ=2'] and dm['effs'] == [] and len(dm['none']) == 1 and 'まだ ないよ' in dm['none'][0] and '山札の 残り 20枚' in dm['t'],
              f'捨て札を タップ → 「終わった ターンの 捨て札」（ターン 1：あなた 1・コンピュータ 2）と「効果で 捨てた カード」（まだ ない）に 分けて 出る（{dm["turns"]}）')
        shot(pg, 'cb_discard')
        pg.locator('#cbOv .cbmod .cbdl .cbc').first.click(); pg.wait_for_timeout(80)
        check(pg.locator('#cbOv .cbmod .big img').get_attribute('src') == 'cb_c1.webp' and '捨て札の カード' in pg.locator('#cbOv .cbmod').inner_text() and modbtns(pg) == ['戻る'], '捨て札の カードを タップ → 大きく 見られる')
        pg.locator('#cbOv .cbmod .cbb').click(); pg.wait_for_timeout(80)
        check(pg.evaluate(DM)['h'] == '捨て札（2枚）', '「戻る」→ 捨て札の 窓に 戻る')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        check(not pg.evaluate("() => CBApp._t.modOn()"), '「戻る」→ 対戦の 画面')
        opp(pg, {'t': 'set', 'k': 3})
        check(pg.evaluate(SLOT) == 'b -' and 'コンピュータは もう セットしたよ' in pg.evaluate(MSG) and pg.locator('#cbOv .cbohand .cbc').count() == 3, f'相手が 先に セットした：相手の わくに 裏の カード・「コンピュータは もう セットしたよ」（{pg.evaluate(SLOT)}）')
        pg.evaluate("() => { window.__seen = []; }")
        play(pg, '3')
        seen = pg.evaluate("() => window.__seen")
        check(any('かぶり！' in s and '同じ カード（3）＝どちらも 負け' in s for s in seen) and pg.evaluate(PIPS) == '0-1' and pg.evaluate(V)['turn'] == 3, f'3 と 3 → 「かぶり！ どちらも 負け」（印は 増えない）（{seen[-1] if seen else None}）')
        pg.locator('#cbOv [data-cb=discard]').click(); pg.wait_for_timeout(80); dm = pg.evaluate(DM)
        check(dm['h'] == '捨て札（4枚）' and dm['turns'] == ['ターン 1|あなた=1|コンピュータ=2', 'ターン 2|あなた=3|コンピュータ=3'], f'2ターン目が 終わった → 捨て札の 窓に ターン 2 が 増える（{dm["turns"]}）')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        pg.evaluate("() => { window.__seen = []; }")
        play(pg, '6'); opp(pg, {'t': 'set', 'k': 5})
        # 第4.177版：相手は 3ターン目に 5 を セットした（手札が 1まい 以上 のこって いる）→ 相手が 5 の 効果を 使うか えらぶ（自分は 待つ）。ここでは 使わない
        check(pg.evaluate(V)['phase'] == 'eff' and pg.evaluate(V)['can']['eff'] is None and 'コンピュータが 効果を 使うか 選んで いるよ' in pg.evaluate(MSG) and asked(pg) is None, '相手が 3ターン目に 5 を セット → 相手の 効果タイム（自分は 待つ：聞かれない）')
        opp(pg, {'t': 'eff', 'use': None})
        seen = pg.evaluate("() => window.__seen")
        check(any('負け…' in s and '5 の ほうが 強いよ' in s for s in seen), f'6 と 5 → 「負け… 5 の ほうが 強いよ」')
        pg.wait_for_function("() => { const g = document.querySelector('#cbOv .cbend .gift'); return CBApp._t.ended && g && g.textContent.length > 3; }", timeout=30000)
        e = pg.evaluate("() => ({ h: document.querySelector('#cbOv .cbend h3').textContent, sc: document.querySelector('#cbOv .cbend .sc').textContent, g: document.querySelector('#cbOv .cbend .gift').textContent, btn: [...document.querySelectorAll('#cbOv .cbend .cbb')].map(b => b.textContent), st: CBApp._t.state, turn: document.querySelector('#cbOv .cbturn').textContent })")
        check(e['h'] == '同点！' and e['sc'].startswith('1 － 1') and e['btn'] == ['もう 1回', 'メニューへ'] and e['st']['draw'] == 1 and e['st']['streak'] == 0 and e['st']['win'] == 0 and '同点' in e['g'] and e['turn'] == '結果',
              f'3ターン 終わり：1勝 1勝 →「同点！」・「もう 1回」「メニューへ」（{e["h"]}・{e["sc"]}・{e["g"]}）')
        shot(pg, 'cb_end_draw')

        print('■ セットの 前の 手札の 効果：7（3枚 交換）（第4.202版・まさちゃん 23:42「手札から使える効果は、カードセット前に使えるようにして！」）')
        start(pg, '77712', '12345', '346'); said(pg); pg.evaluate("() => { window.__seen = []; }")
        aw = pg.evaluate(ASKQ); md = pg.evaluate("() => CBApp._t.mode"); v0 = pg.evaluate(V)
        check(aw and aw['head'] == '7 が 3枚！' and [aw['q'], aw['text']] == ['7 の 効果を 使う？', 'セットの 前に 使えるよ。7 を 3枚 山札に 戻して、新しく 3枚 引けるよ'] and aw['img'] == 'cb_c7.webp' and aw['btns'] == ['使わない', '使う', '手札と ボードを 見る']
              and md['k'] == 'idle' and v0['phase'] == 'set' and v0['can']['x7'] is True and v0['can']['eff'] is None and pg.evaluate(SLOT) == '- -',
              f'配った すぐ あと（セットの 前）：聞く 窓「7 が 3枚！／7 の 効果を 使う？」（7 の カードの 絵・セットの 前に 使えるよ）（{aw and aw["text"]}）')
        # 第4.177版（まさちゃん「カードの効果は使うか使わないか選べるようにして！」）：聞く 窓＝まん中に カードの 絵・質問・大きい「使わない」「使う」
        geo = pg.evaluate("""() => { const m = document.querySelector('#cbOv .cbmod.cbask'), R = e => { const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; };
          const bs = [...m.querySelectorAll('.rowb .cbb')], cs = getComputedStyle(bs[1]); return { vw: innerWidth, vh: innerHeight, img: R(m.querySelector('.big')), no: R(bs[0]), yes: R(bs[1]), peek: R(m.querySelector('[data-cb=askpeek]')), h3: R(m.querySelector('h3')),
            fs: parseFloat(cs.fontSize), qfs: parseFloat(getComputedStyle(m.querySelector('.askq b')).fontSize), z: +getComputedStyle(m).zIndex, cover: document.elementFromPoint(innerWidth / 2, innerHeight - 30).closest('.cbmod') === m }; }""")
        check(geo['yes'][3] - geo['yes'][1] >= 56 and geo['no'][3] - geo['no'][1] >= 56 and geo['yes'][2] - geo['yes'][0] >= 130 and geo['no'][2] - geo['no'][0] >= 130 and geo['fs'] >= 18 and geo['qfs'] >= 19
              and geo['no'][2] <= geo['yes'][0] and abs(geo['no'][1] - geo['yes'][1]) <= 1 and geo['img'][2] - geo['img'][0] >= 150 and geo['h3'][1] >= 0 and geo['peek'][3] <= geo['vh'] and geo['img'][3] <= geo['no'][1] and geo['cover'],
              f'「使わない」「使う」は 大きい ボタン（高さ {geo["yes"][3] - geo["yes"][1]}px・幅 {geo["yes"][2] - geo["yes"][0]}px・字 {geo["fs"]}px）が 横に 並ぶ・質問の 字 {geo["qfs"]}px・カードの 絵 幅 {geo["img"][2] - geo["img"][0]}px・全部 画面の 中')
        shot(pg, 'cb_pre7_ask')
        peek(pg)
        check(asked(pg) is None and not pg.evaluate("() => CBApp._t.modOn()") and pg.evaluate(MSG) == 'セットする カードを 選んでね（カードを タップ）\n7 が 3枚！ セットの 前なら 交換を 使えるよ' and acts(pg) == ['使わない', '7 の 効果を 使う'] and pg.evaluate(V)['phase'] == 'set',
              '「手札と ボードを 見る」→ 窓が 下がる・下の 行の「使わない」「7 の 効果を 使う」で 答えられる')
        shot(pg, 'cb_pre7_bar')
        tap(pg, '1'); mb = modbtns(pg)
        check(mb == ['この カードを セットするセットしたら もう 変えられないよ', '戻る'], f'まだ 決めて いなくても、手札を タップすると セットも できる（使わずに セット＝使わない）（{mb}）')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        check(asked(pg) is None and acts(pg) == ['使わない', '7 の 効果を 使う'], 'カードを 見て 戻っても、下げた 窓は また 出て こない（下の ボタンの まま）')
        pg.locator('#cbOv .cbact [data-cb=p7yes]').click(); idle(pg)
        sd = said(pg); v1 = pg.evaluate(V)
        iu = [i for i, x in enumerate(sd) if x.startswith('use:')]; it = [i for i, x in enumerate(sd) if '7 を 3枚 戻して、新しく 3枚 引いたよ' in x]
        check(len(iu) == 1 and sd[iu[0]] == 'use:あなたが 使った！7 の 効果3枚 交換7 を 3枚 山札に 戻して、新しく 3枚 引くよ' and it and iu[0] < it[0],
              f'「使う」→ 効果の 札「あなたが 使った！ 7 の 効果 3枚 交換 …」→ カードが 動いて「…3枚 引いたよ」（{sd[iu[0]] if iu else None}）')
        check(pg.evaluate(HAND) == '12346' and sorted(pg.evaluate(DOMHAND)) == sorted('12346') and pg.locator('#cbOv .cbdeck .cbn').inner_text() == '20' and v1['phase'] == 'set' and v1['turn'] == 1 and not v1['can']['x7']
              and asked(pg) is None and acts(pg) == [] and pg.evaluate(MSG) == 'セットする カードを 選んでね（カードを タップ）' and pg.evaluate(SLOT) == '- -',
              f'7 を 3枚 戻して 3枚 引いた（手札 {pg.evaluate(HAND)}・山札 20 の まま）→ まだ セットの 前（1ターンに 1回：もう 聞かない）→ セットする カードを 選ぶ')
        play(pg, '1'); opp(pg, {'t': 'set', 'k': 2})
        check(pg.evaluate(V)['turn'] == 2 and pg.evaluate(V)['my']['wins'] == 1 and any('勝ち！' in s for s in pg.evaluate("() => window.__seen")), 'その あと セット → オープン（1 と 2 → 勝ち）→ 2ターン目')
        start(pg, '77712', '12345'); pg.locator('#cbOv .cbmod.cbask [data-cb=p7no]').click(); pg.wait_for_timeout(120)
        check(asked(pg) is None and acts(pg) == ['7 を 3枚 交換'] and pg.evaluate(MSG) == 'セットする カードを 選んでね（カードを タップ）\n7 が 3枚！ セットの 前なら 交換を 使えるよ' and pg.evaluate(HAND) == '12777',
              f'「使わない」→ 窓は もう 出さない（この ターン）・下の ボタン「7 を 3枚 交換」で セットする まで 使える（{acts(pg)}）')
        play(pg, '1'); opp(pg, {'t': 'set', 'k': 2})
        a2 = pg.evaluate(ASKQ)
        check(pg.evaluate(HAND) == '2777' and pg.evaluate(V)['turn'] == 2 and a2 and a2['q'] == '7 の 効果を 使う？', '使わずに セット → オープン → 2ターン目も 7 が 3枚 → また 聞く（ターンごと）')
        pg.locator('#cbOv .cbmod.cbask [data-cb=p7no]').click(); pg.wait_for_timeout(80)
        # 効果タイムは セットした カードの 効果 だけ（5 → 4）：「使わない」を 押した すぐ あと、前の 質問と ボタンは 消える
        start(pg, '51234', '12346', '6'); play(pg, '5'); opp(pg, {'t': 'set', 'k': 2})
        a5 = pg.evaluate(ASKQ)
        check(a5 and a5['head'] == '効果タイム！' and a5['q'] == '5 の 効果を 使う？' and pg.evaluate(V)['phase'] == 'eff', '2人とも セットした →「効果タイム」→ セットした カード（5）の 効果を 聞く')
        pg.locator('#cbOv [data-cb=effno]').click()
        hs = pg.evaluate("() => [document.querySelector('#cbOv .cbact').children.length, document.querySelector('#cbOv .cbmsg').textContent, CBApp._t.idle]"); idle(pg)
        check(hs == [0, '', False] and pg.evaluate(V)['turn'] == 2, f'「使わない」を 押した すぐ あと：前の 質問「効果を 使う？」と ボタンは 消える（結果を 見せ終わる まで 残さない）{hs}')

        print('■ 6（第4.190版・まさちゃん 17:14「6は、カードをセットする前に相手のカード見れる！」：ターンの 始め）：2枚 見せて 相手の 手札を 見る')
        start(pg, '66123', '12345'); sd = said(pg); aw = pg.evaluate(ASKQ); v = pg.evaluate(V)
        check(v['phase'] == 'six' and aw and [aw['q'], aw['text']] == ['6 の 効果を 使う？', '6 を 2枚 見せて、相手の 手札を 1枚 見られるよ（セットの 前：見てから セットする カードを 選べる）'] and aw['head'] == 'ターンの 始め！' and aw['img'] == 'cb_c6.webp'
              and aw['btns'] == ['使わない', '使う', '手札と ボードを 見る'] and any(s.startswith('ban:6 の 効果') and 'セットの 前に 使うか 選んでね' in s for s in sd) and 'ban:対戦 スタートコンピュータと 勝負！' in sd and sd.index('ban:対戦 スタートコンピュータと 勝負！') < max(i for i, s in enumerate(sd) if s.startswith('ban:6 の 効果'))
              and pg.locator('#cbOv .cbglow.on').count() == 0 and pg.evaluate(SLOT) == '- -',
              '6 が 2枚 → 配った あと（ターンの 始め・セットの 前）：「6 の 効果」の 帯 → 聞く 窓「ターンの 始め！／6 の 効果を 使う？」（まだ セットできない）')
        shot(pg, 'cb_six_ask')
        pg.locator('#cbOv [data-cb=sixyes]').click(); pg.wait_for_timeout(80)
        pm = pg.evaluate("() => ({ h: document.querySelector('#cbOv .cbmod h3').textContent, n: document.querySelectorAll('#cbOv .cbmod .pick .cbc').length, t: document.querySelector('#cbOv .cbmod p').textContent })")
        check(pm['h'] == '6 の 効果' and pm['n'] == 5 and '6 を 2枚 相手に 見せるよ' in pm['t'], f'「使う」→ 選ぶ 窓：相手の 手札 5枚（裏・セットの 前）から 1枚')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        check(pg.evaluate(V)['phase'] == 'six' and asked(pg) == ['6 の 効果を 使う？', '6 を 2枚 見せて、相手の 手札を 1枚 見られるよ（セットの 前：見てから セットする カードを 選べる）'], '「戻る」→ まだ 決まって いない（聞く 窓に 戻る：もう一度 選べる）')
        peek(pg)
        check(pg.evaluate(MSG) == 'ターンの 始め！ 6 の 効果を 使う？\n6 を 2枚 見せて、相手の 手札を 1枚 見られるよ' and acts(pg) == ['使わない', '6 の 効果を 使う'], '窓を 下げた とき：下の 行に「使わない」「6 の 効果を 使う」')
        tap(pg, '1'); check(modbtns(pg) == ['戻る'] and pg.locator('#cbOv .cbglow.on').count() == 0, '決める までは セットできない（手札は 見る だけ）')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        pg.locator('#cbOv .cbact [data-cb=sixyes]').click(); pg.wait_for_timeout(80)
        pg.evaluate("() => { window.__seen = []; }"); said(pg)
        pg.locator('#cbOv .cbmod .pick .cbc').nth(2).click(); idle(pg)
        seen = pg.evaluate("() => window.__seen"); v = pg.evaluate(V); sd = said(pg)
        kn = [c['k'] for c in v['op']['hand'] if c['k']]
        check(len(kn) == 1 and any('6 の 効果' in s and f'cb_c{kn[0]}.webp' in s for s in seen) and any(s == 'use:あなたが 使った！6 の 効果手札を 1枚 見る6 を 2枚 見せて、コンピュータの 手札を 1枚 見るよ' for s in sd)
              and pg.locator(f'#cbOv .cbohand .cbc img[src="cb_s{kn[0]}.webp"]').count() == 1 and pg.locator('#cbOv .cbohand .cbc img[src="cb_sb.webp"]').count() == 4 and v['turn'] == 1 and v['phase'] == 'set'
              and pg.locator('#cbOv .cbglow.on').count() == 1 and 'セットする カードを 選んでね' in pg.evaluate(MSG),
              f'見た カード（{kn}）を 大きく 見せる → 1ターン目の セットへ（見てから 選べる）・相手の 手札の 中で その 1枚 だけ 表')
        pg.locator(f'#cbOv .cbohand .cbc img[src="cb_s{kn[0]}.webp"]').locator('..').click(); pg.wait_for_timeout(80)
        check('効果で 見た 相手の カード' in pg.locator('#cbOv .cbmod').inner_text(), '見た カードは タップで 大きく 見られる')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click()
        play(pg, '1'); opp(pg, {'t': 'set', 'k': 2})
        check(pg.evaluate(V)['turn'] == 2 and pg.evaluate(V)['phase'] == 'six' and asked(pg)[0] == '6 の 効果を 使う？', 'オープン → 2ターン目の はじめ：まだ 見て いない カードが ある ので また 6 の 効果を 聞く')
        pg.locator('#cbOv .cbask [data-cb=sixno]').click(); idle(pg)
        check(pg.evaluate(V)['phase'] == 'set' and pg.evaluate(V)['can']['set'] and asked(pg) is None, '「使わない」→ セットへ')
        # 相手が 6 の 効果を 使う：自分は 待つ → 見られた カードに 目の しるし
        start(pg, '12367', '66123'); sd = said(pg); v = pg.evaluate(V)
        check(v['phase'] == 'six' and v['wait'] is True and v['can']['six'] is None and 'コンピュータが 6 の 効果を 使うか 選んで いるよ' in pg.evaluate(MSG) and acts(pg) == [] and asked(pg) is None and pg.locator('#cbOv .cbglow.on').count() == 0
              and any(s.startswith('ban:6 の 効果') and 'コンピュータが 使うか 選ぶよ' in s for s in sd),
              '相手だけ 6 が 2枚：ターンの 始めに「コンピュータが 6 の 効果を 使うか 選んで いるよ…」（自分は 待つ・まだ セットできない）')
        tap(pg, '1'); check(modbtns(pg) == ['戻る'], '相手が 決める までは セットできない')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        r = opp(pg, {'t': 'p6', 'pickk': 2}); sd = said(pg)
        check(r['ok'] and pg.locator('#cbOv .cbhand .cbc .eye').count() == 1 and pg.locator('#cbOv .cbhand .cbc:has(.eye) img').get_attribute('src') == 'cb_s2.webp' and pg.locator('#cbOv .cbohand .cbc img[src="cb_s6.webp"]').count() == 2
              and any('コンピュータが 6 の 効果で、' in s and 'あなたの 2 を 見たよ' in s for s in sd) and any(s == 'use:コンピュータが 使った！6 の 効果手札を 1枚 見る6 を 2枚 見せて、あなたの 手札を 1枚 見るよ' for s in sd) and pg.evaluate(V)['phase'] == 'set',
              '相手が 6 の 効果：効果の 札「コンピュータが 使った！ 6 の 効果」→「あなたの 2 を 見たよ」・相手の 6 が 2枚 表に・見られた 自分の カード（2）に 目の 印 → セットへ')
        tap(pg, '2'); check('この カードは 相手に 見られて いるよ' in pg.locator('#cbOv .cbmod').inner_text(), '見られた カードを タップ →「相手に 見られて いるよ」')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click()
        shot(pg, 'cb_seen')
        start(pg, '12367', '66123'); said(pg); opp(pg, {'t': 'p6', 'pick': None}); sd = said(pg)
        check(any('コンピュータは 6 の 効果を 使わなかったよ' in s for s in sd) and pg.evaluate(V)['phase'] == 'set' and pg.evaluate(V)['can']['set'], '相手が 6 の 効果を 使わなかった →「コンピュータは 6 の 効果を 使わなかったよ」→ セットへ')
        # 2人とも 6 が 2まい：相手が 先に 決めても、自分の えらび とちゅうは 消えない・相手が 何を 見るかは わからない
        start(pg, '66123', '66345')
        pg.locator('#cbOv [data-cb=sixyes]').click(); pg.wait_for_timeout(80); said(pg)
        r = opp(pg, {'t': 'p6', 'pickk': 1}); sd = said(pg)
        check(r['ok'] and pg.evaluate("() => CBApp._t.modOn()") and pg.locator('#cbOv .cbmod .pick .cbc').count() == 5 and pg.evaluate(V)['phase'] == 'six' and not any('6 の 効果' in s for s in sd),
              '相手が 先に 決めた：自分の 選ぶ 窓は 消えない・相手が 何を 見るかは まだ 出ない')
        pg.locator('#cbOv .cbmod .pick .cbc').last.click(); idle(pg); sd = said(pg)
        us = [x[4:].split('！')[0] + '！' + x.split('！')[1][:6] for x in sd if x.startswith('use:')]
        check(us == ['あなたが 使った！6 の 効果', 'コンピュータが 使った！6 の 効果'], f'2人の 6 の 効果が 一緒に 出る（自分 → 相手：{us}）')
        check(any('コンピュータが 6 の 効果で、' in s and 'あなたの 1 を 見たよ' in s for s in sd) and pg.evaluate(V)['turn'] == 1 and pg.evaluate(V)['phase'] == 'set' and len([c for c in pg.evaluate(V)['op']['hand'] if c['k']]) == 3,
              '→ セットへ（見た カード 1枚 ＋ 相手が 見せた 6 の 2枚が 表）')

        print('■ 効果タイム：5（5 と 手札 1枚を 捨てて 山札から 1枚）')
        start(pg, '51237', '12346', 'k')
        tap(pg, '5')
        check(modbtns(pg) == ['この カードを セットするセットしたら もう 変えられないよ', '戻る'], '5 を タップ：セットの 前は「セットする」だけ（効果は セットの 後）')
        pg.locator('#cbOv .cbmod [data-cb=set]').click(); idle(pg)
        opp(pg, {'t': 'set', 'k': 1})
        check(asked(pg) == ['5 の 効果を 使う？', '5 と 手札 1枚を 捨てて、山札から 1枚 セットできるよ'] and pg.evaluate(ASKQ)['img'] == 'cb_c5.webp', '5 を セットして 手札 4枚 →「5 の 効果を 使う？」')
        pg.locator('#cbOv [data-cb=effyes]').click(); pg.wait_for_timeout(80)
        check(pg.evaluate("() => CBApp._t.mode.step") == 'drop5' and '5 と 一緒に 捨てる カードを 選んでね' in pg.evaluate(MSG) and acts(pg) == ['戻る'] and asked(pg) is None and not pg.evaluate("() => CBApp._t.modOn()"), '「使う」→ 窓が 閉じて、捨てる カードを 選ぶ')
        pg.locator('#cbOv .cbact [data-cb=effback]').click(); pg.wait_for_timeout(80)
        check(pg.evaluate("() => CBApp._t.mode.step") == 'ask' and asked(pg) == ['5 の 効果を 使う？', '5 と 手札 1枚を 捨てて、山札から 1枚 セットできるよ'], '「戻る」→「使う？」（聞く 窓）に 戻れる')
        pg.locator('#cbOv [data-cb=effyes]').click(); pg.wait_for_timeout(80)
        tap(pg, '7')
        check(modbtns(pg) == ['この カードを 捨てる5 と 一緒に 捨てて、山札から 1枚 セット', '戻る'], '手札を タップ →「この カードを 捨てる」')
        said(pg)
        pg.locator('#cbOv .cbmod [data-cb=drop5]').click(); idle(pg)
        v = pg.evaluate(V); sd = said(pg)
        check(any('5 と 7 を 捨てて、山札から 1枚 セットしたよ' in s for s in sd) and v['turn'] == 2 and v['my']['wins'] == 1 and v['last']['c'] == ['k', '1'] and pg.locator('#cbOv .cbdis .cbn').inner_text() == '4' and pg.evaluate(HAND) == '123',
              f'5 と 7 を 捨てて 山札の 上（神様馬）が セットされた → オープンで 勝ち（捨て札 4枚・手札 {pg.evaluate(HAND)}）')
        # 神様馬で 勝った → 2ターン目の はじめに 聞く 窓が 出て いる（下の「神様馬」の 所で 見る）。捨て札を 見る ために 窓を 下げる
        awk = pg.evaluate(ASKQ); akacts = acts(pg); shot(pg, 'cb_pend_k'); peek(pg)
        pg.locator('#cbOv [data-cb=discard]').click(); pg.wait_for_timeout(80); dm = pg.evaluate(DM)
        check(dm['turns'] == ['ターン 1|あなた=k|コンピュータ=1'] and dm['effs'] == ['ターン 1|あなたの 5 の 効果=57'] and dm['none'] == [], f'捨て札の 窓：終わった ターン（神様馬・1）と、効果で 捨てた カード（あなたの 5 の 効果：5・7）（{dm["effs"]}）')
        shot(pg, 'cb_discard_eff')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)

        print('■ 神様馬：勝った 次の ターンの 始めに、効果を 使うか 選ぶ（まさちゃん 23:12）')
        v = pg.evaluate(V)
        check(v['phase'] == 'pre' and v['pend']['mine'] and v['pend']['type'] == 'k' and any(s == 'ban:ターン 2' for s in sd) and any(s.startswith('ban:神様馬の 効果') and '使うか 選んでね' in s for s in sd)
              and sd.index('ban:ターン 2') < [i for i, s in enumerate(sd) if s.startswith('ban:神様馬の 効果')][0]
              and awk and [awk['q'], awk['text']] == ['神様馬の 効果を 使う？', '相手の 手札を 1枚 見られるよ'] and awk['head'] == '神様馬で 勝った！' and awk['img'] == 'cb_ck.webp' and awk['btns'] == ['使わない', '使う', '手札と ボードを 見る']
              and akacts == [] and pg.evaluate(SLOT) == '- -' and pg.locator('#cbOv .cbturn').inner_text().replace('\n', '') == 'ターン 2／3',
              f'2ターン目に 入って から 聞く 窓「神様馬で 勝った！／神様馬の 効果を 使う？」（使わない／使う）・ボードは 片付いて いる（{pg.evaluate(SLOT)}）')
        check(asked(pg) is None and pg.evaluate(MSG) == '神様馬で 勝った！ 効果を 使う？\n相手の 手札を 1枚 見られるよ' and acts(pg) == ['使わない', '神様馬の 効果を 使う'], '「手札と ボードを 見る」（さっき 押した）→ 捨て札の 窓を 閉じた あとも、下の 行の「使わない」「神様馬の 効果を 使う」で 答えられる')
        tap(pg, '1'); check(modbtns(pg) == ['戻る'] and pg.locator('#cbOv .cbglow.on').count() == 0, '決める までは セットできない（手札は 見る だけ）')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        pg.locator('#cbOv [data-cb=kgo]').click(); pg.wait_for_timeout(80)
        pg.evaluate("() => { window.__seen = []; }")
        pg.locator('#cbOv .cbmod .pick .cbc').first.click(); idle(pg)
        seen = pg.evaluate("() => window.__seen"); v = pg.evaluate(V)
        check(any('神様馬の 効果' in s for s in seen) and len([c for c in v['op']['hand'] if c['k']]) == 1 and v['turn'] == 2 and v['phase'] == 'set' and 'セットする カードを 選んでね' in pg.evaluate(MSG) and pg.locator('#cbOv .cbglow.on').count() == 1 and acts(pg) == [],
              '相手の 手札を 1枚 見た → 2ターン目の セットへ')
        start(pg, 'k2367', '12345'); play(pg, 'k'); opp(pg, {'t': 'set', 'k': 1})
        pg.locator('#cbOv [data-cb=kskip]').click(); idle(pg)
        check(pg.evaluate(V)['turn'] == 2 and pg.evaluate(V)['phase'] == 'set' and all(c['k'] is None for c in pg.evaluate(V)['op']['hand']), '「使わない」→ 何も 見ないで 2ターン目の セットへ')
        start(pg, '12367', 'k2345'); play(pg, '1'); said(pg); opp(pg, {'t': 'set', 'k': 'k'}); sd = said(pg)
        check(pg.evaluate(V)['phase'] == 'pre' and pg.evaluate(V)['pend']['mine'] is False and 'コンピュータが 神様馬の 効果を 使うか 選んで いるよ' in pg.evaluate(MSG) and acts(pg) == [] and any(s.startswith('ban:神様馬の 効果') and 'コンピュータが 使うか 選ぶよ' in s for s in sd),
              '相手が 神様馬で 勝った：2ターン目の 初めに「コンピュータが 神様馬の 効果を 使うか 選んで いるよ…」（自分は 待つ）')
        opp(pg, {'t': 'k', 'pickk': 2}); sd = said(pg)
        check(any('コンピュータが 神様馬の 効果で、' in s and 'あなたの 2 を 見たよ' in s for s in sd) and any(s == 'use:コンピュータが 使った！神様馬の 効果手札を 1枚 見る前の ターンに 神様馬で 勝った ので、あなたの 手札を 1枚 見るよ' for s in sd) and pg.locator('#cbOv .cbhand .cbc:has(.eye) img').get_attribute('src') == 'cb_s2.webp' and pg.evaluate(V)['phase'] == 'set' and pg.evaluate(V)['can']['set'], '相手が 効果を 使った → 見られた カードに 目の 印 → セットへ')

        print('■ 幻の馬：勝った 次の ターンの 始めに、2枚 捨てて 2枚 引く')
        start(pg, 'm6712', '12345', '13'); play(pg, 'm'); opp(pg, {'t': 'set', 'k': 1})
        check(pg.evaluate(V)['phase'] == 'pre' and pg.evaluate(V)['turn'] == 2 and asked(pg) == ['幻の馬の 効果を 使う？', '手札を 2枚 捨てて、山札から 2枚 引けるよ'] and pg.evaluate(ASKQ)['head'] == '幻の馬で 勝った！' and pg.evaluate(ASKQ)['img'] == 'cb_cm.webp', '2ターン目の はじめ：聞く 窓「幻の馬で 勝った！／幻の馬の 効果を 使う？」（使わない／使う）')
        pg.locator('#cbOv [data-cb=mpick]').click(); pg.wait_for_timeout(80)
        check(pg.evaluate("() => CBApp._t.mode.k") == 'dropm' and '（0／2）' in pg.evaluate(MSG) and pg.locator('#cbOv .cbact [data-cb=mgo]').is_disabled() and asked(pg) is None, '「使う」→ 窓が 閉じて、捨てる 2枚を 選ぶ（選ぶ まで ボタンは 押せない）')
        pg.locator('#cbOv .cbact [data-cb=modex]').click(); pg.wait_for_timeout(80)
        check(asked(pg) == ['幻の馬の 効果を 使う？', '手札を 2枚 捨てて、山札から 2枚 引けるよ'] and pg.evaluate("() => CBApp._t.mode.k") == 'idle', '「戻る」→ 聞く 窓に 戻る（まだ 決まって いない）')
        pg.locator('#cbOv [data-cb=mpick]').click(); pg.wait_for_timeout(80)
        tap(pg, '6'); tap(pg, '7'); tap(pg, '1')      # 3まい目は えらべない
        check(pg.locator('#cbOv .cbhand .cbc.sel').count() == 2 and '（2／2）' in pg.evaluate(MSG) and pg.locator('#cbOv .cbact [data-cb=mgo]').is_enabled(), '2枚 選んだ（3枚目は 選べない）')
        tap(pg, '7'); tap(pg, '7')                     # はずして もう一度
        pg.locator('#cbOv .cbact [data-cb=mgo]').click(); idle(pg)
        check(pg.evaluate(HAND) == '1123' and pg.evaluate(V)['turn'] == 2 and pg.evaluate(V)['phase'] == 'set' and pg.locator('#cbOv .cbdeck .cbn').inner_text() == '18' and pg.locator('#cbOv .cbdis .cbn').inner_text() == '4',
              f'6 と 7 を 捨てて 2枚（1・3）引いた（手札 {pg.evaluate(HAND)}・山札 18・捨て札 4）→ セットへ')
        pg.locator('#cbOv [data-cb=discard]').click(); pg.wait_for_timeout(80); dm = pg.evaluate(DM)
        check(dm['turns'] == ['ターン 1|あなた=m|コンピュータ=1'] and dm['effs'] == ['ターン 2始め|あなたの 幻の馬の 効果=67'], f'捨て札の 窓：効果で 捨てた カード（ターン 2 の はじめ・あなたの 幻の馬の 効果：6・7）（{dm["effs"]}）')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        start(pg, 'm6712', '12345'); play(pg, 'm'); opp(pg, {'t': 'set', 'k': 1}); pg.locator('#cbOv [data-cb=mskip]').click(); idle(pg)
        check(pg.evaluate(HAND) == '1267' and pg.evaluate(V)['phase'] == 'set' and pg.locator('#cbOv .cbdeck .cbn').inner_text() == '20', '「使わない」→ 手札は そのまま セットへ')

        print('■ 効果タイム：4（見せて 強制交換）')
        start(pg, '41236', '15677'); opp(pg, {'t': 'set', 'k': 1})
        tap(pg, '4')
        check(modbtns(pg) == ['この カードを セットするセットしたら もう 変えられないよ', '戻る'], '4 を タップ：セットの 前は「セットする」だけ')
        pg.locator('#cbOv .cbmod [data-cb=set]').click(); idle(pg)
        check(asked(pg) == ['4 の 効果を 使う？', '4 を 見せて、相手に カードを 交換させるよ'] and pg.evaluate(ASKQ)['img'] == 'cb_c4.webp' and pg.evaluate(SLOT) == 'b b[4]:伏せて セット', f'4 を セットした あと →「4 の 効果を 使う？」（まだ 伏せた まま：{pg.evaluate(SLOT)}）')
        said(pg)
        pg.locator('#cbOv [data-cb=effyes]').click(); idle(pg)
        v = pg.evaluate(V); sd = said(pg)
        check(v['phase'] == 'swap' and v['pend']['mine'] is False and pg.evaluate(SLOT) == 'b 4:4 の 効果' and 'コンピュータが カードを 交換して いるよ' in pg.evaluate(MSG) and any(s == 'use:あなたが 使った！4 の 効果強制 交換4 を 先に 見せたよ。コンピュータは セットした カードを 交換するよ' for s in sd) and not any(s.startswith('ban:4 の 効果') for s in sd),
              f'「使う」：効果の 札「あなたが 使った！ 4 の 効果 強制 交換」（第4.185版：前の 帯の 変わり）→ 4 が 表に なって 相手の 交換を 待つ（{pg.evaluate(SLOT)}）')
        pg.evaluate("() => { window.__seen = []; }")
        opp(pg, {'t': 'swap', 'k': 5}); opp(pg, {'t': 'u5', 'drop': None})      # 第4.183版：交換で 出した 5 の 効果は 使わない
        seen = pg.evaluate("() => window.__seen")
        check(any('勝ち！' in s and '4 が 5 に 勝ったよ' in s for s in seen) and pg.evaluate(V)['my']['wins'] == 1 and pg.locator('#cbOv .cbohand .cbc').count() == 4, '相手は 1 を 戻して 5 を 出した（5 の 効果は 使わない）→ 4 の 勝ち（相手の 手札は 4枚の まま）')
        start(pg, '41236', '15677'); play(pg, '4'); opp(pg, {'t': 'set', 'k': 1}); pg.evaluate("() => { window.__seen = []; }")
        pg.locator('#cbOv [data-cb=effno]').click(); idle(pg)
        check(any('負け…' in s and '1 の ほうが 強いよ' in s for s in pg.evaluate("() => window.__seen")), '「使わない」→ そのまま オープン（4 と 1 → 負け）')
        # 相手が 4 の 効果：自分が 交換する
        start(pg, '15677', '41236'); play(pg, '1'); opp(pg, {'t': 'set', 'k': 4}); said(pg)
        opp(pg, {'t': 'eff', 'use': {'u4': True}})
        v = pg.evaluate(V); sd = said(pg)
        check(v['phase'] == 'swap' and v['pend']['mine'] and pg.evaluate(SLOT) == '4:4 の 効果 b[1]:伏せて セット' and 'コンピュータが 4 の 効果を 使ったよ！' in pg.evaluate(MSG) and pg.locator('#cbOv .cbglow.on').count() == 1 and any(s.startswith('use:コンピュータが 使った！4 の 効果強制 交換') and 'あなたは セットした カードを、手札の 別の カードと 交換してね' in s for s in sd),
              f'相手が 4 の 効果：自分が 交換する 番（{pg.evaluate(SLOT)}）')
        shot(pg, 'cb_pend_swap')
        tap(pg, '5')
        check(modbtns(pg) == ['この カードと 交換する', '戻る'], '手札を タップ →「この カードと 交換する」')
        pg.evaluate("() => { window.__seen = []; }")
        pg.locator('#cbOv .cbmod [data-cb=swap]').click(); idle(pg)
        a5x = pg.evaluate(ASKQ); pg.locator('#cbOv .cbmod.cbask [data-cb=u5no]').click(); idle(pg)      # 第4.183版：交換で 出した 5 → 5 の 効果を 使うか 聞かれる → 使わない
        seen = pg.evaluate("() => window.__seen")
        check(a5x and a5x['q'] == '5 の 効果を 使う？' and any('負け…' in s for s in seen) and pg.evaluate(HAND) == '1677' and pg.evaluate(V)['op']['wins'] == 1, f'5 と 交換（1 は 手札に 戻る）→「5 の 効果を 使う？」→ 使わない → 4 と 5 で 負け（手札 {pg.evaluate(HAND)}）')

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
              f'2人とも 4 の 効果を 使った → 効果の 札「どちらも 使った！ 4 の 効果 打ち消して ドロー」→ オープンは「ドロー！ どちらも 4 の 効果を 使った ので 引き分け」（印は 増えない・交換なし：手札 {pg.evaluate(HAND)}）')
        check(bool(cls) and all('ls' not in c.split('|')[0].split() and 'ls' not in c.split('|')[1].split() for c in cls), f'ドローの ときは どちらの カードも 暗く しない（{cls[-1] if cls else None}）')
        start(pg, '41236', '41567'); play(pg, '4'); opp(pg, {'t': 'set', 'k': 4}); opp(pg, {'t': 'eff', 'use': {}})
        pg.evaluate("() => { window.__seen = []; }")
        pg.locator('#cbOv [data-cb=effno]').click(); idle(pg)
        check(any('かぶり！' in x and '同じ カード（4）＝どちらも 負け' in x for x in pg.evaluate("() => window.__seen")) and pg.evaluate(V)['last']['d4'] is False, '2人とも 4 で、2人とも 効果を 使わない → 今まで どおり「かぶり！ どちらも 負け」')

        print('■ 手札の 効果（セットの 前）と セットした カードの 効果（効果タイム）：7 を 行って から セット → 5 を 聞く（第4.202版）')
        start(pg, '57771', '12346', '2346')
        check(asked(pg)[0] == '7 の 効果を 使う？' and pg.evaluate(ASKQ)['head'] == '7 が 3枚！', 'セットの 前：「7 の 効果を 使う？」')
        said(pg); pg.locator('#cbOv .cbmod.cbask [data-cb=p7yes]').click(); idle(pg); sd = said(pg)
        check(sorted(pg.evaluate(DOMHAND)) == sorted('12345') and any('7 を 3枚 戻して' in s for s in sd) and asked(pg) is None and pg.evaluate(V)['phase'] == 'set', '7 を「使う」→ すぐ 3枚 交換（手札 1・2・3・4・5：まだ セットの 前）')
        play(pg, '5'); opp(pg, {'t': 'set', 'k': 1})
        check(pg.evaluate(V)['phase'] == 'eff' and pg.evaluate("() => CBApp._t.mode.q") == '5' and asked(pg)[0] == '5 の 効果を 使う？' and pg.evaluate(ASKQ)['img'] == 'cb_c5.webp' and pg.evaluate(ASKQ)['head'] == '効果タイム！',
              '7 で 引いた 5 を セット → 効果タイム：「5 の 効果を 使う？」')
        pg.locator('#cbOv [data-cb=effyes]').click(); pg.wait_for_timeout(80); tap(pg, '4'); m4 = modbtns(pg)
        check(m4 == ['この カードを 捨てる5 と 一緒に 捨てて、山札から 1枚 セット', '戻る'], f'5 で 捨てる カード：7 で 引いた カード（4）も 選べる（{m4}）')
        said(pg); pg.locator('#cbOv .cbmod [data-cb=drop5]').click(); idle(pg); sd = said(pg)
        check(any('5 と 4 を 捨てて' in s for s in sd) and pg.evaluate(HAND) == '123' and pg.evaluate(V)['last']['c'][1] == '1' and pg.evaluate(V)['turn'] == 2, f'5 の 効果（4 を 捨てる）→ オープン（手札 {pg.evaluate(HAND)}）')
        start(pg, '57771', '12346', '2346'); pg.locator('#cbOv .cbmod.cbask [data-cb=p7no]').click(); pg.wait_for_timeout(80)
        play(pg, '5'); opp(pg, {'t': 'set', 'k': 1})
        check(asked(pg)[0] == '5 の 効果を 使う？' and pg.evaluate(DOMHAND) == '1777', '7 を「使わない」→ 5 を セット → 効果タイムで「5 の 効果を 使う？」')
        pg.locator('#cbOv [data-cb=effyes]').click(); pg.wait_for_timeout(80); tap(pg, '7'); pg.locator('#cbOv .cbmod [data-cb=drop5]').click(); idle(pg)
        check(pg.evaluate(V)['turn'] == 2 and pg.evaluate(HAND) == '177', '7 の 効果を 使わない ときは、5 で 7 を 捨てても いい（7 が 2枚に なる）')

        print('■ うっかり 押し 防止：聞く 窓が 出て すぐ（0.35秒）は 答えを 受けつけない（すばやく 2回 押しても 次の 質問は 答えた ことに ならない）')
        pg.evaluate("() => { CBApp._guard = null; }")      # ふだんの 動き（0.35秒）
        WAIT3 = "() => CBApp._t.ask && CBApp._t.idle && !!document.querySelector('#cbOv .cbask [data-cb=p3no]')"
        start(pg, '7773331', '1224556', turns=5); pg.wait_for_timeout(450)
        q0 = pg.evaluate(ASKQ); pg.locator('#cbOv .cbask [data-cb=p7no]').click()
        pg.wait_for_function(WAIT3, timeout=10000, polling=10)
        g = pg.evaluate("() => { const T = CBApp._t, b = document.querySelector('#cbOv .cbask [data-cb=p3no]'); if (b) b.click(); const pk = document.querySelector('#cbOv .cbask [data-cb=askpeek]'); return { q: document.querySelector('#cbOv .cbask .askq b').textContent, ask: T.ask, has: !!b, peek: !!pk, ph: T.view.phase }; }")
        check(q0 and q0['q'] == '7 の 効果を 使う？' and g == {'q': '3 の 効果を 使う？', 'ask': True, 'has': True, 'peek': True, 'ph': 'set'},
              f'7 の「使わない」の あと すぐ 出た「3 の 効果を 使う？」（セットの 前の 次の 効果）は、出て すぐ 押しても 答えた ことに ならない（まだ 聞いて いる：{g}）')
        pg.wait_for_timeout(420); pg.locator('#cbOv .cbask [data-cb=p3no]').click(); pg.wait_for_timeout(120)
        check(asked(pg) is None and acts(pg) == ['セットの 前の 効果'] and pg.evaluate(HAND) == '1333777', f'0.35秒 たてば 押せる：3 も「使わない」→ 下の ボタン「セットの 前の 効果」（2つ のこって いる）（{acts(pg)}）')
        pg.locator('#cbOv .cbact [data-cb=prere]').click(); pg.wait_for_timeout(450)
        a7 = pg.evaluate(ASKQ)
        check(a7 and a7['q'] == '7 の 効果を 使う？', '「セットの 前の 効果」→ もう 一度 聞く（7 から）')
        g2 = pg.evaluate("() => { const b = document.querySelector('#cbOv .cbask [data-cb=askpeek]'); if (b) b.click(); return { had: !!b, ask: CBApp._t.ask, bar: [...document.querySelectorAll('#cbOv .cbact .cbb')].map(x => x.textContent.trim()) }; }")
        check(g2['had'] and not g2['ask'] and g2['bar'] == ['使わない', '7 の 効果を 使う'], f'「手札と ボードを 見る」は 出て すぐでも 押せる（何も 決まらない：下の 行で 答える {g2["bar"]}）')
        pg.locator('#cbOv .cbact [data-cb=p7no]').click(); pg.wait_for_timeout(450)
        check(pg.evaluate(ASKQ)['q'] == '3 の 効果を 使う？', '下の 行の「使わない」は すぐ 押せる → 次（3）を 聞く')
        pg.locator('#cbOv .cbask [data-cb=p3no]').click(); pg.wait_for_timeout(80)
        pg.evaluate("() => { CBApp._guard = 1500; }")      # ターンの はじめ：配った あと すぐ 出る 窓（テストの 待ち時間に よらない ように 1.5秒に のばして 見る）
        start(pg, '66123', '12345')
        g3 = pg.evaluate("() => { const b = document.querySelector('#cbOv .cbask [data-cb=sixno]'); if (b) b.click(); return { has: !!b, ask: CBApp._t.ask, ph: CBApp._t.view.phase }; }")
        pg.wait_for_timeout(1600); pg.locator('#cbOv .cbask [data-cb=sixno]').click(); idle(pg)
        check(g3 == {'has': True, 'ask': True, 'ph': 'six'} and pg.evaluate(V)['phase'] == 'set', f'ターンの 始めの「6 の 効果を 使う？」も 同じ（出て すぐは 受けつけない → 時間が たてば 押せる：{g3}）')
        pg.evaluate("() => { CBApp._guard = 0; }")

        print('■ 4 は 一番 あと（第4.188版・まさちゃん 11:16「4は効果発動最後にして！」）')
        start(pg, '51237', '41236', 'k'); play(pg, '5'); opp(pg, {'t': 'set', 'k': 4})
        pg.locator('#cbOv [data-cb=effyes]').click(); pg.wait_for_timeout(80); tap(pg, '7'); said(pg); pg.locator('#cbOv .cbmod [data-cb=drop5]').click(); idle(pg); sd5 = said(pg); v5 = pg.evaluate(V)
        check(any('5 と 7 を 捨てて、山札から 1枚 セットしたよ' in x for x in sd5) and v5['phase'] == 'eff' and v5['can']['eff'] is None and v5['wait'] and 'コンピュータが 効果を 使うか 選んで いるよ' in pg.evaluate(MSG) and pg.evaluate(SLOT) == 'b b:山札から',
              f'第4.190版：自分の 5 の 効果は すぐ 出る（5 と 7 を 捨てて 山札から 伏せて セット）→ 次は 相手の 4（一番 あと：自分は 待つ・どの 効果かは 出ない）（{pg.evaluate(SLOT)}）')
        opp(pg, {'t': 'eff', 'use': {'u4': True}}); sd = said(pg); v = pg.evaluate(V)
        check(any(x.startswith('use:コンピュータが 使った！4 の 効果') for x in sd) and v['phase'] == 'swap' and v['pend']['mine'] and v['my']['set']['blind'] is True and pg.evaluate(SLOT) == '4:4 の 効果 b:山札から' and pg.evaluate(HAND) == '123',
              f'相手の 4 の 効果（一番 後）→ 山札から 来た カードを 交換する 番（{pg.evaluate(SLOT)}）')
        shot(pg, 'cb_4last')
        tap(pg, '1'); pg.locator('#cbOv .cbmod [data-cb=swap]').click(); idle(pg); v = pg.evaluate(V)
        check(v['turn'] == 2 and v['my']['wins'] == 1 and pg.evaluate(HAND) == '23k', f'交換して 1 を 出す → 1 が 4 に 勝つ（山札から 来て いた 神様馬は 手札に：{pg.evaluate(HAND)}）')

        print('■ 逆転勝利：相手の 5 の 効果で 入れ替わった カードでも（第4.188版の 確かめ・まさちゃん 11:05「1と2の効果は、5の効果でカードが入れ替わった際もオープンした後に使用できるようになってる？」）')
        start(pg, '11123', '54672', 'k'); play(pg, '1'); opp(pg, {'t': 'set', 'k': 5}); said(pg); pg.evaluate("() => { window.__seen = []; }")
        opp(pg, {'t': 'eff', 'use': {'u5k': 7}}); seen = pg.evaluate("() => window.__seen"); aw = pg.evaluate(ASKQ); v = pg.evaluate(V)
        check(any('チャンス！' in s and '神様馬 の ほうが 強い…でも 1 の「逆転勝利」を 使えるよ' in s for s in seen) and aw and aw['q'] == '1 の 効果を 使う？' and aw['text'] == '手札の 1 を 2枚 見せて、1枚 捨てると、神様馬に 勝てるよ' and v['phase'] == 'rev',
              '相手の 5 の 効果 → 山札の 神様馬が 場に → オープン「チャンス！」→ 聞く 窓「1 の 効果を 使う？」')
        shot(pg, 'cb_rev_after5')
        pg.locator('#cbOv .cbask [data-cb=revyes]').click(); idle(pg); v = pg.evaluate(V); sd = said(pg)
        check(v['my']['wins'] == 1 and v['op']['wins'] == 0 and v['turn'] == 2 and any(s.startswith('ban:逆転勝利！') and '1 が 神様馬 に 勝ったよ' in s for s in sd), '使う →「逆転勝利！ 1 が 神様馬 に 勝ったよ」（大逆転）')
        start(pg, '22234', '54673', '1'); play(pg, '2'); opp(pg, {'t': 'set', 'k': 5}); opp(pg, {'t': 'eff', 'use': {'u5k': 7}})
        aw = pg.evaluate(ASKQ)
        check(aw and aw['q'] == '2 の 効果を 使う？' and aw['text'] == '手札の 2 を 2枚 見せて、1枚 捨てると、1 に 勝てるよ', '2 は 1 に 対して 同じ（相手の 5 の 効果で 山札の 1 が 出ても「2 の 効果を 使う？」）')
        pg.locator('#cbOv .cbask [data-cb=revyes]').click(); idle(pg)
        check(pg.evaluate(V)['my']['wins'] == 1 and pg.evaluate(V)['op']['wins'] == 0, '使う → 2 が 1 に 逆転勝利')

        print('■ 5：2ターン目・3ターン目でも 使える（第4.177版：使った 後の 手札が 残りの ターンの 数より 少なく ならない とき）')
        start(pg, '55123', '12346', '2k'); play(pg, '1'); opp(pg, {'t': 'set', 'k': 2})
        check(pg.evaluate(V)['turn'] == 2 and pg.evaluate(HAND) == '2355', '（1ターン目は 1 を 出して 勝ち → 2ターン目：手札 2・3・5・5）')
        play(pg, '5'); opp(pg, {'t': 'set', 'k': 1})
        check(pg.evaluate(V)['phase'] == 'eff' and pg.evaluate(V)['turn'] == 2 and asked(pg) == ['5 の 効果を 使う？', '5 と 手札 1枚を 捨てて、山札から 1枚 セットできるよ'], '2ターン目に 5 を セット（手札 3枚）→「5 の 効果を 使う？」と 聞かれる（前は 1ターン目 だけ）')
        pg.locator('#cbOv [data-cb=effyes]').click(); pg.wait_for_timeout(80); tap(pg, '2'); said(pg); pg.locator('#cbOv .cbmod [data-cb=drop5]').click(); idle(pg); sd = said(pg)
        check(any('5 と 2 を 捨てて、山札から 1枚 セットしたよ' in s for s in sd) and pg.evaluate(V)['turn'] == 3 and pg.evaluate(HAND) == '35' and pg.evaluate(V)['last']['c'] == ['2', '1'], f'2ターン目に 使う：5 と 2 を 捨てて 山札の 上（2）で 勝負 → 3ターン目（手札 {pg.evaluate(HAND)}）')
        play(pg, '5'); opp(pg, {'t': 'set', 'k': 3})
        check(pg.evaluate(V)['phase'] == 'eff' and pg.evaluate(V)['turn'] == 3 and pg.evaluate(HAND) == '3' and asked(pg) and asked(pg)[0] == '5 の 効果を 使う？',
              '3ターン目：5 と もう 1枚 だけ（まさちゃんの 例）→ 5 を セット（手札 1枚）でも「5 の 効果を 使う？」と 聞かれる')
        pg.locator('#cbOv [data-cb=effyes]').click(); pg.wait_for_timeout(80); tap(pg, '3'); said(pg); pg.evaluate("() => { window.__seen = []; }"); pg.locator('#cbOv .cbmod [data-cb=drop5]').click()
        pg.wait_for_function("() => CBApp._t.ended", timeout=30000); idle(pg); sd = said(pg); v = pg.evaluate(V)
        check(any('5 と 3 を 捨てて、山札から 1枚 セットしたよ' in s for s in sd) and v['my']['hand'] == [] and v['last']['c'] == ['k', '3'] and v['res'] == 'win' and any('cb_ck.webp' in s for s in pg.evaluate("() => window.__seen")),
              '使う：5 と 最後の 手札（3）を 捨てて、山札から 来た 神様馬で 勝ち（手札 0枚で 終わり）')
        pg.wait_for_function("() => { const g = document.querySelector('#cbOv .cbend .gift'); return g && g.textContent.length > 3; }", timeout=30000)
        pg.locator('#cbOv .cbend [data-cb=menu]').click(); pg.wait_for_timeout(120)
        start(pg, '51237', '12346'); play(pg, '1'); opp(pg, {'t': 'set', 'k': 2}); play(pg, '2'); opp(pg, {'t': 'set', 'k': 1}); play(pg, '3'); opp(pg, {'t': 'set', 'k': 3})
        pg.wait_for_function("() => CBApp._t.ended", timeout=30000); idle(pg)
        check(pg.evaluate(V)['res'] is not None and not any('5 の 効果' in s for s in said(pg)), '5 を セットしなければ 効果タイムは 出ない（5 を 手札に 持って いる だけでは 聞かれない）')
        pg.locator('#cbOv .cbend [data-cb=menu]').click(); pg.wait_for_timeout(120)

        print('■ 3：手札に 3 が 3枚 → 3枚を 見せて、その 1枚と 相手の 手札の 1枚（裏の カードから 自分で 選ぶ）を 交換（第4.177版・第4.202版：セットの 前・まさちゃん 11/19 00:38「CPUが勝手に選ぶ形にならないようにして！」）')
        pg.evaluate("""() => { if (window.__win) return; window.__win = []; new MutationObserver(() => { const m = document.querySelector('#cbOv .cbmod'); if (!m.classList.contains('cbopen')) return;
          const s = (m.querySelector('h3') || {}).textContent + '|' + (m.querySelector('p') ? m.querySelector('p').textContent : '') + '|' + [...m.querySelectorAll('img')].map(i => i.getAttribute('src')).join(','); if (window.__win[window.__win.length - 1] !== s) window.__win.push(s); })
          .observe(document.querySelector('#cbOv .cbmod'), { childList: true, subtree: true, attributes: true }); }""")
        start(pg, '33312', '4567k')
        aw = pg.evaluate(ASKQ)
        check(pg.evaluate(V)['can']['x3'] is True and aw and aw['q'] == '3 の 効果を 使う？' and aw['text'] == 'セットの 前に 使えるよ。3 を 3枚 見せて、その 1枚と 相手の 手札の 1枚（見えて いる カードも 選べる）を 交換できるよ' and aw['img'] == 'cb_c3.webp' and aw['head'] == '3 が 3枚！',
              '3 が 3枚（セットする 前の 手札：第4.202版）→ 配った あと すぐ 聞く 窓「3 が 3枚！／3 の 効果を 使う？」（3 の カードの 絵）')
        shot(pg, 'cb_ask3')
        peek(pg)
        fit = pg.evaluate("() => { const m = document.querySelector('#cbOv .cbmsg'); return [m.textContent, m.scrollHeight <= m.clientHeight, m.clientHeight, getComputedStyle(m).fontSize]; }")
        check(fit[0] == 'セットする カードを 選んでね（カードを タップ）\n3 が 3枚！ セットの 前なら 交換を 使えるよ' and fit[1] and fit[2] == 44 and acts(pg) == ['使わない', '3 の 効果を 使う'], f'窓を 下げた とき：下の 行に 短い 文（2行に おさまる：字 {fit[3]}）・「使わない」「3 の 効果を 使う」')
        said(pg); pg.evaluate("() => { window.__win.length = 0; }"); h0 = pg.evaluate("() => CBApp._t.view.op.hand.length")
        PK3 = """() => { const m = document.querySelector('#cbOv .cbmod.on.cbx3'); return m ? { h: m.querySelector('h3').textContent, t: m.querySelector('p').innerText, n: m.querySelectorAll('.pick .cbc').length, ok: m.querySelectorAll('.pick .cbc[data-cb=pick]').length,
          dis: [...m.querySelectorAll('.pick .cbc:disabled img')].map(i => i.getAttribute('src')), backs: [...m.querySelectorAll('.pick .cbc[data-cb=pick] img')].every(i => i.getAttribute('src') === 'cb_sb.webp'), btn: [...m.querySelectorAll('.col .cbb')].map(b => b.textContent.trim()) } : null; }"""
        pg.locator('#cbOv .cbact [data-cb=p3yes]').click(); pg.wait_for_timeout(150)
        pk = pg.evaluate(PK3); v_ = pg.evaluate(V)
        check(pk and pk['h'] == '3 の 効果' and '交換する カードを 1枚 選んでね' in pk['t'] and '見えて いる カードも 選べるよ。裏の カードは 何が 来るか わからないよ' in pk['t'] and '手札の 3 を 3枚 相手に 見せて、1枚 わたすよ' in pk['t'] and 'もう 見た' not in pk['t'] and 'トークン' not in pk['t']
              and pk['n'] == 5 and pk['ok'] == 5 and pk['dis'] == [] and pk['backs'] and pk['btn'] == ['戻る'] and v_['phase'] == 'set' and pg.evaluate(HAND) == '12333' and v_['can']['x3p'] and len(v_['can']['x3p']) == 5,
              '第4.202版：「3 の 効果を 使う」→ 交換する カードを 自分で 選ぶ 窓（相手の 手札の 裏の カード 5枚・何が 来るかは わからない）・まだ 何も おきない（プログラムが かってに 選ばない）')
        shot(pg, 'cb_pick3')
        pg.locator('#cbOv .cbmod.cbx3 [data-cb=modx]').click(); pg.wait_for_timeout(200)
        check(asked(pg) is None and acts(pg) == ['使わない', '3 の 効果を 使う'] and pg.evaluate(HAND) == '12333' and pg.evaluate(V)['can']['x3'], '「戻る」→ 何も おきない（下の ボタンで また 使える）')
        pg.locator('#cbOv .cbact [data-cb=p3yes]').click(); pg.wait_for_timeout(150)
        tu = pg.evaluate("() => +document.querySelectorAll('#cbOv .cbmod.cbx3 .pick .cbc[data-cb=pick]')[3].dataset.u"); tk = pg.evaluate("(u) => CBApp._t.match._.state().p[1].hand.find(c => c.u === u).k", tu)
        pg.locator('#cbOv .cbmod.cbx3 .pick .cbc[data-cb=pick]').nth(3).click(); idle(pg)
        win = pg.evaluate("() => window.__win"); v = pg.evaluate(V); mine = sorted(c['k'] for c in v['my']['hand']); got = [c for c in v['my']['hand'] if c['u'] == tu]
        w3 = [s for s in win if s.startswith('3 の 効果！|')]; wx = [s for s in win if s.startswith('3 の 効果：交換！|')]
        check(w3 and '手札の 3 を 3枚 見せたよ' in w3[0] and w3[0].count('cb_s3.webp') == 3 and wx and len(got) == 1 and got[0]['k'] == tk and f'cb_c{tk}.webp' in wx[0] and 'を もらったよ' in wx[0] and win.index(w3[0]) < win.index(wx[0]),
              f'裏の カードを 1枚 選ぶ → 3 の カードを 3枚 見せる 窓 → 選んだ カード（中身は {tk}）が 来て 大きく 見せる 窓（選んだ カードが そのまま 来る）')
        check(len(v['my']['hand']) == 5 and mine.count('3') == 2 and '2' in mine and '1' in mine and got and got[0]['k'] in ('4', '5', '6', '7', 'k') and len(v['op']['hand']) == h0 and [c['k'] for c in v['op']['hand'] if c['k']] == ['3'] and v['turn'] == 1 and v['phase'] == 'set' and asked(pg) is None,
              f'交換した あと：自分の 手札は 3 が 2枚・1・2・もらった カード（{mine}）・相手の 手札は 5枚の まま で、渡した 3 だけ 表に 見える・まだ セットの 前')
        eyes = pg.evaluate("() => [...document.querySelectorAll('#cbOv .cbhand .cbc')].filter(c => c.querySelector('.eye')).map(c => c.querySelector('img').getAttribute('src').replace('cb_s', '').replace('.webp', '')).sort().join('')")
        check(eyes == ''.join(sorted(['3', '3', got[0]['k']])) and pg.locator('#cbOv .cbohand .cbc img[src="cb_s3.webp"]').count() == 1 and pg.locator('#cbOv .cbohand .cbc img[src="cb_sb.webp"]').count() == 4,
              f'見せた 3（2枚）と もらった カードに 目の 印（相手が 知って いる：{eyes}）・相手の 手札の 中に 3 が 1枚 表で 見える')
        shot(pg, 'cb_after3')
        play(pg, '1'); opp(pg, {'t': 'set', 'k': 3})
        check(pg.evaluate(V)['turn'] == 2 and pg.evaluate(V)['my']['wins'] == 1, 'その あと セット（1）→ オープン（相手は もらった 3）→ 2ターン目')
        start(pg, '33312', '4567k'); pg.locator('#cbOv .cbmod.cbask [data-cb=p3no]').click(); pg.wait_for_timeout(80); play(pg, '1'); opp(pg, {'t': 'set', 'k': 7})
        check(pg.evaluate(HAND) == '2333' and pg.evaluate(V)['turn'] == 2 and all(c['k'] is None for c in pg.evaluate(V)['op']['hand']), '「使わない」→ 交換しないで セット → オープン（手札は 3・3・3・2 の まま）')
        start(pg, '33312', '4567k'); pg.locator('#cbOv .cbmod.cbask [data-cb=askpeek]').click(); pg.wait_for_timeout(80); play(pg, '3')
        check(pg.evaluate(V)['my']['set'] and pg.evaluate(V)['my']['set']['k'] == '3' and not pg.evaluate(V)['can']['x3'] and asked(pg) is None and acts(pg) == [], '使わずに 3 を セット → もう 使えない（セットの 前 だけ・下の ボタンも 消える）')
        opp(pg, {'t': 'set', 'k': 7})
        # 第4.229版（まさちゃん 11/26 22:19「3の効果は、相手の見えてるカードに対しても使用できるようにして！」）：もう 見た カード（表）も 選べる（前は 裏の カード だけ）・相手が 先に セットして いても 使える
        start(pg, '33312', '4567k'); pg.evaluate("() => { const S = CBApp._t.match._.state(); S.p[1].hand.filter(c => c.k === 'k' || c.k === '4').forEach(c => S.p[0].known.push(c.u)); }")      # テスト用：相手の 4 と 神様馬を「もう 見た」ことに する
        opp(pg, {'t': 'set', 'k': 7}); pg.wait_for_timeout(150)
        pg.locator('#cbOv .cbmod.cbask [data-cb=p3yes]').click(); pg.wait_for_timeout(150); pk = pg.evaluate(PK3)
        face = pg.evaluate("() => [...document.querySelectorAll('#cbOv .cbmod.cbx3 .pick .cbc[data-cb=pick]')].map(b => [b.querySelector('img').getAttribute('src'), b.classList.contains('knw'), b.classList.contains('tg')])")
        check(pk and pk['n'] == 4 and pk['ok'] == 4 and pk['dis'] == [] and 'もう 見た カードは 選べないよ' not in pk['t'] and '見えて いる カードも 選べるよ' in pk['t'] and pg.evaluate(V)['op']['set']
              and sorted(f[0] for f in face if f[0] != 'cb_sb.webp') == ['cb_s4.webp', 'cb_sk.webp'] and all(not f[1] and f[2] for f in face),
              f'相手が もう セット：もう 見た カード（表：4・神様馬）も 押せる（暗く しない・光る）＝ 4枚 ぜんぶ 選べる（{face}）')
        shot(pg, 'cb_pick3_known')
        pg.locator('#cbOv .cbmod.cbx3 .pick .cbc[data-cb=pick]:has(img[src="cb_sk.webp"])').click(); idle(pg); hb = pg.evaluate(HAND)
        win = pg.evaluate("() => window.__win"); wx = [s for s in win if s.startswith('3 の 効果：交換！|')]
        check(hb == '1233k' and not pg.evaluate(V)['can']['x3'] and wx and 'cb_ck.webp' in wx[-1] and '神様馬 を もらったよ' in wx[-1], f'見えて いる 神様馬を 選ぶ → 神様馬が 来る（{hb}・{wx[-1:] }）')
        play(pg, '1')
        # 相手が 3 の 効果を 使う（セットの 前）
        start(pg, '12456', '33312'); said(pg); pg.evaluate("() => { window.__win.length = 0; }")
        check(pg.evaluate(V)['phase'] == 'set' and not pg.evaluate(V)['can']['x3'] and asked(pg) is None, '相手だけ 3 が 3枚：自分は 聞かれない（セットできる）')
        b0 = pg.evaluate(HAND); r = opp(pg, {'t': 'x3', 'pickk': '2'}); sd = said(pg); win = pg.evaluate("() => window.__win"); v = pg.evaluate(V); b1 = pg.evaluate(HAND)      # 第4.202版：相手も 裏の カードから 選ぶ（ここでは 2）
        lost = [k for k in '12456' if b0.count(k) > b1.count(k)]
        check(r['ok'] and any(s.startswith('3 の 効果！|') and 'コンピュータが 手札の 3 を 3枚 見せたよ' in s and s.count('cb_s3.webp') == 3 for s in win) and len(lost) == 1 and b1.count('3') == 1 and len(b1) == 5
              and any('コンピュータが 3 の 効果を 使ったよ' in s and f'あなたの {lost[0]} と 3 を 交換した' in s for s in sd),
              f'相手が セットの 前に 3 の 効果：3 を 3枚 見せる 窓 →「あなたの {lost[0] if lost else "?"} と 3 を 交換した」・自分の 手札は {b0} → {b1}（まだ セットの 前）')
        check(pg.locator('#cbOv .cbohand .cbc img[src="cb_s3.webp"]').count() == 2 and len([c for c in v['op']['hand'] if c['k'] == lost[0]]) == 1 and pg.locator('#cbOv .cbohand .cbc img[src="cb_sb.webp"]').count() == 2
              and pg.locator('#cbOv .cbhand .cbc .eye').count() == 1 and pg.locator('#cbOv .cbhand .cbc:has(.eye) img').get_attribute('src') == 'cb_s3.webp' and v['turn'] == 1 and v['can']['set'],
              '相手の 手札の 中に、見せた 3（2枚）と もと 自分の カードが 表で 見える（残りは 裏）・自分に 来た 3 には 目の 印（相手が 知って いる カード）・自分は そのまま セットできる')
        play(pg, '3'); opp(pg, {'t': 'set', 'k': lost[0]})
        check(pg.evaluate(V)['turn'] == 2, '（もらった 3 を セット → オープン → 2ターン目）')

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
        check(q1['lines'] == 1 and q2['lines'] == 2 and q4['lines'] == 2 and q5['lines'] == 2 and all(q['fit'] for q in qs), f'（比べる 場面：1行 {[q["lines"] for q in qs].count(1)}個・2行 {[q["lines"] for q in qs].count(2)}個・どれも 行の 中に おさまる）')
        check(all(same(q1, q) for q in qs) and q1['msg'][1] == 44 and q1['act'][1] == 48, f'字が 1行でも 2行でも、ボード・手札・ボタンの 場所は 1画素も 動かない（言葉の 行 {q1["msg"][1]}px・ボタンの 行 {q1["act"][1]}px・ボードの 上 {sorted(set(q["board"][0] for q in qs))}）')
        TEXTS = ['コンピュータが 4 の 効果を 使ったよ！\nセットした カードと 交換する 手札を 選んでね', 'コンピュータが カードを 交換して いるよ…', '神様馬で 勝った！ 効果を 使う？\n相手の 手札を 1枚 見られるよ', 'コンピュータが 神様馬の 効果を 使うか 選んで いるよ…',
                 '幻の馬で 勝った！ 効果を 使う？\n手札を 2枚 捨てて、山札から 2枚 引けるよ', 'コンピュータが 幻の馬の 効果を 使うか 選んで いるよ…', 'コンピュータが 効果を 使うか 選んで いるよ…', 'コンピュータは もう セットしたよ。セットする カードを 選んでね',
                 'セットする カードを 選んでね（カードを タップ）', '5 と 一緒に 捨てる カードを 選んでね（カードを タップ）', '捨てる カードを 2枚 選んでね（2／2）', '効果を 使うか 選んでね', '相手を 待って いるよ…',
                 '逆転の チャンス！ 1 の 効果を 使う？\n手札の 1 を 1枚 捨てて、幻の馬に 勝てるよ', '逆転の チャンス！ 1 の 効果を 使う？\n手札の 1 を 1枚 捨てて、神様馬に 勝てるよ', '逆転の チャンス！ 2 の 効果を 使う？\n手札の 2 を 1枚 捨てて、1 に 勝てるよ',
                 'コンピュータが 逆転勝利を 使うか 選んで いるよ…', '友達が 逆転勝利を 使うか 選んで いるよ…',
                 'ターンの 始め！ 6 の 効果を 使う？\n6 を 2枚 見せて、相手の 手札を 1枚 見られるよ', 'コンピュータが 6 の 効果を 使うか 選んで いるよ…', '友達が 6 の 効果を 使うか 選んで いるよ…']
        TEXTS += [f'{h}\n{t}' for h in ('セットする カードを 選んでね（カードを タップ）', 'コンピュータは もう セットしたよ。カードを 選んでね', '友達は もう セットしたよ。カードを 選んでね')
                  for t in ('7 が 3枚！ セットの 前なら 交換を 使えるよ', '7トークン！ セットの 前なら 山札から 3枚 引けるよ', '3 が 3枚！ セットの 前なら 交換を 使えるよ', '3 が 3枚 ぶん！ セットの 前なら 交換を 使えるよ', '7 が 4枚！ セットの 前なら 逆転を 使えるよ')]      # 第4.202版：セットの 前の 手札の 効果
        TEXTS += [f'効果タイム！ {k} の 効果を 使う？\n{t}' for k, t in (('5', '5 と 手札 1枚を 捨てて、山札から 1枚 セットできるよ'), ('4', '4 を 見せて、相手に カードを 交換させるよ'))]      # 第4.202版：効果タイムは 5 と 4 だけ
        FIT = """(ts) => ts.map(t => { CBApp._t.say(t); const m = document.querySelector('#cbOv .cbmsg'), r = m.getBoundingClientRect(); return [m.scrollHeight <= m.clientHeight, parseFloat(getComputedStyle(m).fontSize), Math.round(r.height), Math.round(document.querySelector('#cbOv .cbboard').getBoundingClientRect().top * 10) / 10]; })"""
        f390 = pg.evaluate(FIT, TEXTS)
        check(all(x[0] and x[2] == 44 for x in f390) and len(set(x[3] for x in f390)) == 1 and min(x[1] for x in f390) >= 12.5, f'言葉の 行に 出る 文 {len(TEXTS)}こ：どれも 行の 中に おさまる・行の 高さは 44px の まま（幅 390px：字 {min(x[1] for x in f390)}〜{max(x[1] for x in f390)}px）')
        for vw, vh in ((375, 667), (320, 568)):
            pg.set_viewport_size({'width': vw, 'height': vh}); pg.wait_for_timeout(250); ff = pg.evaluate(FIT, TEXTS)
            check(all(x[0] and x[2] == 44 for x in ff) and len(set(x[3] for x in ff)) == 1 and min(x[1] for x in ff) >= 10.5, f'幅 {vw}px でも：どれも おさまる・ボードは 動かない（入らない 文は 字を 小さく：{min(x[1] for x in ff)}〜{max(x[1] for x in ff)}px）')
        # 小さい 画面（iPhone SE：375×647）でも 聞く 窓・GET の 札が 画面に おさまる
        pg.set_viewport_size({'width': 375, 'height': 647}); pg.wait_for_timeout(250)
        start(pg, '33312', '4567k')      # 第4.202版：3 が 3枚 → 配った あと すぐ 聞く 窓（セットの 前）
        se_ = pg.evaluate("""() => { const m = document.querySelector('#cbOv .cbmod.cbask'), R = e => { const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; };
          return { h3: R(m.querySelector('h3')), img: R(m.querySelector('.big')), q: R(m.querySelector('.askq')), row: R(m.querySelector('.rowb')), peek: R(m.querySelector('[data-cb=askpeek]')), vh: innerHeight, vw: innerWidth }; }""")
        order = [se_['h3'], se_['img'], se_['q'], se_['row'], se_['peek']]
        check(se_['h3'][1] >= 0 and se_['peek'][3] <= se_['vh'] and all(a[3] <= b[1] + 1 for a, b in zip(order, order[1:])) and all(r[0] >= 0 and r[2] <= se_['vw'] for r in order) and se_['img'][2] - se_['img'][0] >= 130,
              f'iPhone SE（375×647）：聞く 窓は 上から 見出し・絵・質問・ボタン・「見る」が 重ならずに 画面の 中（絵の 幅 {se_["img"][2] - se_["img"][0]}px・下の はし {se_["peek"][3]}／{se_["vh"]}）')
        shot(pg, 'cb_ask_se')
        pg.locator('#cbOv [data-cb=p3no]').click(); pg.wait_for_timeout(80)
        pg.set_viewport_size({'width': 390, 'height': 844}); pg.wait_for_timeout(250)

        print('■ 5ターン・手札 7枚（第4.178版・まさちゃん「カードバトル５ターン勝負にする 手札7枚にして！」）')
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
              f'はじめ：手札 7枚（強い 順）・相手の 手札 7枚（裏）・山札 16・ターン 1／5・勝ちの 印は 5つ ずつ（{pg.evaluate(DOMHAND)}）')
        fits = lambda q, vw, vh: (q['n'] == 7 and q['on'] == 7 and q['left'] >= 0 and q['right'] <= vw and q['oleft'] >= 0 and q['oright'] <= vw and abs(q['ch'] - q['cw'] * 1.5) < 1.5 and q['step'] >= q['cw'] * 0.59 and q['top'] >= q['me'][3] - 1 and q['bottom'] <= q['act'][1] + 1
                                  and q['act'][3] <= vh and q['topbar'][1] >= 0 and q['opp'][3] <= q['board'][1] + 30 and q['board'][3] <= q['msg'][1] + 20 and q['msg'][3] <= q['me'][1] + 1 and all(q['hit']))
        check(fits(g, 390, 844) and g['cw'] >= 76 and g['step'] >= 44, f'手札 7枚の 並び（390×844）：全部 画面の 中・重なりは 40% まで（カード {g["cw"]}×{g["ch"]}・見える 幅 {g["step"]}px：44px 以上）・どの カードも 見える 所を 押せば その カード・ボタンの 行まで 画面の 中')
        shot(pg, 'cb7_turn1')
        for vw, vh, cwmin in ((375, 647, 72), (375, 667, 72), (320, 568, 60)):
            pg.set_viewport_size({'width': vw, 'height': vh}); pg.wait_for_timeout(300); q = pg.evaluate(G7)
            check(fits(q, vw, vh) and q['cw'] >= cwmin, f'手札 7枚の 並び（{vw}×{vh}）：全部 画面の 中（カード {q["cw"]}×{q["ch"]}・見える 幅 {q["step"]}px・相手の カード {q["ow"]}px・下の はし {q["act"][3]}／{vh}）')
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
              f'5ターン 全部 やる（テスト用の full：決着しても さいごまで）：1ターンに 1枚 ずつ 出して 5ターンで 終わり・手札は 2枚 残る・捨て札 10枚（{log5}）')
        bans = [s for s in sd if s.startswith('ban:ターン')]
        check(bans == ['ban:ターン 2', 'ban:ターン 3', 'ban:ターン 4', 'ban:ターン 5最後の 勝負！'] and e['h'] == 'あなたの 勝ち！' and e['sc'].startswith('3 － 2') and e['pips'] == '2/5,3/5',
              f'ターンの 帯：2〜4 は「ターン n」・5ターン目に「最後の 勝負！」・結果「あなたの 勝ち！ 3 － 2」・勝ちの 印（相手 2／5・自分 3／5）（{bans}・{e["pips"]}）')
        shot(pg, 'cb7_end')
        pg.locator('#cbOv .cbend [data-cb=menu]').click(); pg.wait_for_timeout(150)

        print('■ 決着したら 試合終了（第4.202版・まさちゃん 11/18 23:55「５ターンのうち、どちらかが３ターン勝利したら、試合終了にして！ 数値的にターンを回しても勝てないなら、勝っている方の勝ちになるようにして！」）')
        EG = "() => ({ h: document.querySelector('#cbOv .cbend h3').textContent, sc: document.querySelector('#cbOv .cbend .sc').textContent, t: document.querySelector('#cbOv .cbturn').textContent.replace(/\\s+/g, ''), pips: [...document.querySelectorAll('#cbOv .cbpips')].map(p => p.querySelectorAll('i.on').length + '/' + p.querySelectorAll('i').length).join() })"
        for me_, op_, plays, who, res in (('1112345', '2233677', (('1', '2'), ('1', '3'), ('1', '6')), 'あなた', 'win'), ('2233677', '1112345', (('2', '1'), ('3', '1'), ('6', '1')), 'コンピュータ', 'lose')):
            start(pg, me_, op_, turns=5, full=False); said(pg); loge = []
            for mine, his in plays:
                play(pg, mine); opp(pg, {'t': 'set', 'k': his}); vv = pg.evaluate(V); loge.append((vv['turn'], vv['my']['wins'], vv['op']['wins'], vv['phase'], vv['early']))
            pg.wait_for_function("() => { const g = document.querySelector('#cbOv .cbend .gift'); return CBApp._t.ended && g && g.textContent.length > 3; }", timeout=30000)
            sd = said(pg); v = pg.evaluate(V); e = pg.evaluate(EG); w3 = (3, 0) if res == 'win' else (0, 3)
            check(loge == [(2, w3[0] // 3, w3[1] // 3, 'set', 0), (3, 2 * (w3[0] // 3), 2 * (w3[1] // 3), 'set', 0), (3, w3[0], w3[1], 'end', 3)] and v['res'] == res and v['turns'] == 5 and len(v['my']['hand']) == 4 and len(v['op']['hand']) == 4,
                  f'{"自分" if res == "win" else "相手"}が 3連勝：2勝 0敗では 続く（のこり 3ターンで 追いつける）→ 3勝で のこりの 2ターンでは 追いつけない → 3ターン目で 試合終了（手札は 4枚 残る）（{loge}）')
            bans = [x for x in sd if x.startswith('ban:')]
            check(bans == ['ban:ターン 2', 'ban:ターン 3', f'ban:決着！{who}の 勝ちが 決まったよ（のこりの ターンでは 追いつけない）'] and not any('最後の 勝負' in x for x in sd),
                  f'帯：「決着！ {who}の 勝ちが 決まったよ（のこりの ターンでは 追いつけない）」（{bans[-1:]}）')
            check(e['h'] == ('あなたの 勝ち！' if res == 'win' else 'あなたの 負け…') and e['sc'] == f'{w3[0]} － {w3[1]}あなた － コンピュータ（勝った 数）3ターン目で 決着！' and e['pips'] == f'{w3[1]}/5,{w3[0]}/5',
                  f'結果の 窓：「{e["h"]} {w3[0]} － {w3[1]}」の 下に「3ターン目で 決着！」・勝ちの 印（{e["pips"]}）')
            if res == 'win': shot(pg, 'cb_early_end')
            pg.locator('#cbOv .cbend [data-cb=menu]').click(); pg.wait_for_timeout(150)
        # 2勝 1敗・のこり 1ターンは 続く（追いつけば 同点）→ 3勝 1敗で 終わり
        start(pg, '1112345', '2234677', turns=5, full=False); loge = []
        for mine, his in (('1', '2'), ('1', '3'), ('3', '2'), ('1', '6')):
            play(pg, mine); opp(pg, {'t': 'set', 'k': his}); vv = pg.evaluate(V); loge.append((vv['turn'], vv['my']['wins'], vv['op']['wins'], vv['phase'], vv['early']))
        pg.wait_for_function("() => CBApp._t.ended", timeout=30000)
        check(loge == [(2, 1, 0, 'set', 0), (3, 2, 0, 'set', 0), (4, 2, 1, 'set', 0), (4, 3, 1, 'end', 4)] and pg.evaluate(EG)['sc'].endswith('4ターン目で 決着！'),
              f'2勝 1敗（のこり 2ターン）は 続く → 3勝 1敗（のこり 1ターン）で 4ターン目に 決着（{loge}）')
        pg.locator('#cbOv .cbend [data-cb=menu]').click(); pg.wait_for_timeout(150)

        print('■ 設定の 窓：BGM・効果音（第4.178版・まさちゃん「プレイボードの右下の設定ボタンを押すと、BGMオンかオフと効果エフェクトオンかオフを選べるようにして！」・第4.185版：23:04「設定のエフェクトオフもいらない！」→ エフェクトは なくした）')
        pg.evaluate("() => { localStorage.removeItem('tengel.cb'); CBApp._t.load(); CBApp._as = null; }")
        s0 = pg.evaluate("() => ({ sets: CBApp._t.sets, app: !!(window.TengelFx && TengelFx.get && TengelFx.get().sound !== false) })")
        check(s0['sets']['raw'] == {'bgm': None, 'se': None} and s0['sets']['se'] == s0['app'] and 'fx' not in s0['sets'] and s0['sets']['bgm'] == (s0['app'] and s0['sets']['as']),
              f'まだ 決めて いない とき：効果音＝アプリの 効果音の 設定（{s0["app"]}）・BGM＝アプリの 効果音が オン で、消音スイッチに 合わせられる iOS（16.4 から）の とき だけ オン（ここ {s0["sets"]["as"]} → {s0["sets"]["bgm"]}）')
        pg.evaluate("() => { CBApp._as = true; }")
        check(pg.evaluate("() => CBApp._t.sets.bgm") == s0['app'], '（消音スイッチに 合わせられる iOS と 同じ 形に して 見る：BGM は 初めから オン）')
        pg.evaluate("() => { CBApp._as = null; }")
        SETM = """() => { const m = document.querySelector('#cbOv .cbmod.cbset'); if (!m) return null; const R = e => { const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; };
          return { h: m.querySelector('h3').textContent, rows: [...m.querySelectorAll('.cbsw')].map(r => r.dataset.set + ':' + r.querySelector('span').textContent + ':' + [...r.querySelectorAll('.cbseg button')].map(b => b.textContent + (b.classList.contains('on') ? '*' : '') + (b.getAttribute('aria-pressed') === 'true' ? '!' : '')).join('/')),
            btns: [...m.querySelectorAll('.cbb')].map(b => b.textContent.trim()), seg: [...m.querySelectorAll('.cbseg button')].map(R), box: R(m), vh: innerHeight, vw: innerWidth, last: R([...m.querySelectorAll('.cbb')].pop()), h3: R(m.querySelector('h3')), bg: getComputedStyle(m).backgroundColor }; }"""
        pg.locator('#cbOv .cbmenu [data-cb=gear]').click(); pg.wait_for_timeout(120)
        sm = pg.evaluate(SETM); app = '*!' if s0['app'] else ''; napp = '' if s0['app'] else '*!'
        check(sm and sm['h'] == '設定' and sm['rows'] == ['bgm:BGM音楽:オン/オフ*!', f'se:効果音カードや ボタンの 音:オン{app}/オフ{napp}'] and sm['btns'] == ['戻る'],
              f'メニューの「設定」→ 設定の 窓：BGM・効果音 の 2つ（それぞれ オン／オフ・第4.185版：エフェクトは なくした）・「戻る」（{sm and sm["rows"]}）')
        check(sm and all(b[2] - b[0] >= 56 and b[3] - b[1] >= 40 for b in sm['seg']) and sm['h3'][1] >= 0 and sm['last'][3] <= sm['vh'] and all(b[0] >= 0 and b[2] <= sm['vw'] for b in sm['seg']), 'オン／オフの ボタンは 押しやすい 大きさ（幅 56px・高さ 40px 以上）・窓は 画面の 中')
        shot(pg, 'cb_set_menu')
        # 第4.185版：エフェクトの オン／オフは ない（窓に ボタンが ない・火の あかりは いつも ゆれる）。前の 版で「オフ」に して いた 人も（fx:false は すてる）
        FIRE = "() => [...document.querySelectorAll('#cbOv .cbfire')].map(e => { const c = getComputedStyle(e); return c.animationName + ' ' + c.animationDuration + ' ' + c.pointerEvents; })"
        f_on = pg.evaluate(FIRE); nb = pg.locator('#cbOv .cbset [data-k=fx]').count()
        pg.evaluate("() => { const s = JSON.parse(localStorage.getItem('tengel.cb') || JSON.stringify({ v: 1 })); s.fx = false; localStorage.setItem('tengel.cb', JSON.stringify(s)); CBApp._t.load(); CBApp._t.save(); }")
        st1 = pg.evaluate("() => ({ ls: JSON.parse(localStorage.getItem('tengel.cb')), nofx: document.querySelector('#cbOv').classList.contains('nofx'), sets: CBApp._t.sets, has: 'fx' in CBApp._t.state })")
        check(f_on == ['cbfire 5.6s none', 'cbfire 4.3s none'] and nb == 0 and pg.evaluate(FIRE) == f_on and not st1['nofx'] and 'fx' not in st1['ls'] and 'fx' not in st1['sets'] and not st1['has'],
              f'エフェクトの オン／オフは ない：窓に ボタンが ない（{nb}）・火の あかりは いつも ゆれる（{f_on}）・前の 版の「エフェクト オフ」（fx:false）は 読み直すと 捨てる')
        # 効果音：オフに すると 鳴らさない（音を 鳴らした 数＝__abs が ふえない）／オンに すると 鳴る
        pg.locator('#cbOv .cbset [data-cb=tg][data-k=bgm][data-v="0"]').click(); pg.locator('#cbOv .cbset [data-cb=tg][data-k=se][data-v="0"]').click(); pg.wait_for_timeout(150)
        pg.locator('#cbOv .cbset [data-cb=modx]').click(); pg.wait_for_timeout(100)
        a0 = pg.evaluate("() => window.__abs")
        start(pg, '1234567', '1234567', turns=5); tap(pg, '1'); pg.locator('#cbOv .cbmod [data-cb=set]').click(); idle(pg); pg.wait_for_timeout(250)
        a1 = pg.evaluate("() => window.__abs")
        check(a1 == a0 and pg.evaluate("() => CBApp._t.sets.se") is False and pg.evaluate("() => JSON.parse(localStorage.getItem('tengel.cb')).se") is False, f'効果音 オフ：配る・カードを 押す・セットしても 音を 鳴らさない（鳴らした 数 {a0} → {a1}）')
        pg.locator('#cbOv .cbgear').click(); pg.wait_for_timeout(120)
        sg = pg.evaluate(SETM)
        check(sg and sg['rows'] == ['bgm:BGM音楽:オン/オフ*!', 'se:効果音カードや ボタンの 音:オン/オフ*!'] and sg['btns'] == ['対戦に 戻る', '遊び方', '対戦を やめる'] and sg['last'][3] <= sg['vh'],
              f'対戦の 画面：ボードの 右下の 歯車 → 同じ 設定の 窓（選んだ 形の まま）＋「対戦に 戻る」「遊び方」「対戦を やめる」（{sg and sg["btns"]}）')
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
        check(b0 == {'want': True, 'raw': True, 'ls': True} and pg.evaluate(SETM)['rows'][0] == 'bgm:BGM音楽:オン*!/オフ', 'BGM オン：覚える（tengel.cb の bgm:true）・窓の 印も「オン」')
        if HAVE:
            pg.wait_for_function("() => CBApp._t.bgm.on", timeout=30000)
            b1 = pg.evaluate("() => CBApp._t.bgm"); pg.wait_for_timeout(700); b2 = pg.evaluate("() => CBApp._t.bgm")
            check(b1['file'] == 'cb_bgm.m4a' and abs(b1['len'] - 34 * 3 * 60 / 76) < 1e-6 and b1['pre'] == 0.5 and b1['loop'] and abs(b1['loop'][0] - 0.25) < 1e-6 and abs(b1['loop'][1] - (0.25 + b1['len'])) < 1e-6 and 0 < b1['vol'] <= 0.6 and b1['ctx'] == 'running' and b2['pos'] > b1['pos'] + 0.4,
                  f'BGM が 鳴る：cb_bgm.m4a・くり返すのは 真ん中の 1回り（{b1["loop"] and [round(x, 2) for x in b1["loop"]]}秒：約 {b1["len"]:.1f}秒）・音の 大きさ {b1["vol"]}・曲が 進む（{b1["pos"]:.2f} → {b2["pos"]:.2f}秒）')
            HID = "(h) => { Object.defineProperty(document, 'hidden', { configurable: true, get: () => h }); document.dispatchEvent(new Event('visibilitychange')); }"
            pg.evaluate(HID, True); pg.wait_for_timeout(150); b3 = pg.evaluate("() => CBApp._t.bgm"); pg.wait_for_timeout(600); b4 = pg.evaluate("() => CBApp._t.bgm")
            check(not b3['on'] and not b3['want'] and b3['have'] and abs(b4['pos'] - b3['pos']) < 1e-6 and b3['pos'] >= b2['pos'], f'アプリが うしろに 行った：BGM は 止まる（曲の 場所は {b3["pos"]:.2f}秒で 止まった まま）')
            pg.evaluate(HID, False); pg.wait_for_function("() => CBApp._t.bgm.on", timeout=10000); pg.wait_for_timeout(300); b5 = pg.evaluate("() => CBApp._t.bgm")
            check(b5['on'] and b3['pos'] <= b5['pos'] <= b3['pos'] + 2.5, f'戻った：続きから 鳴る（{b3["pos"]:.2f} → {b5["pos"]:.2f}秒：曲の 頭に 戻らない）')
            pg.evaluate("() => { delete document.hidden; }")
            pg.locator('#cbOv .cbset [data-cb=tg][data-k=bgm][data-v="0"]').click(); pg.wait_for_timeout(120)
            check(not pg.evaluate("() => CBApp._t.bgm.on") and pg.evaluate("() => JSON.parse(localStorage.getItem('tengel.cb')).bgm") is False, 'BGM オフ：止まる・覚える')
            pg.locator('#cbOv .cbset [data-cb=tg][data-k=bgm][data-v="1"]').click(); pg.wait_for_function("() => CBApp._t.bgm.on", timeout=10000)
            pg.locator('#cbOv .cbset [data-cb=quit]').click(); pg.locator('#cbOv .cbmod [data-cb=quitgo]').click(); pg.wait_for_timeout(150)
            check(pg.evaluate("() => CBApp._t.screen") == 'menu' and pg.evaluate("() => CBApp._t.bgm.on"), '対戦を やめて メニューに 戻っても BGM は 続く（カードバトルを 開いて いる 間）')
            pg.locator('#cbOv .cbmenu [data-cb=close]').click(); pg.wait_for_timeout(200)
            c1 = pg.evaluate("() => CBApp._t.bgm"); pg.wait_for_timeout(1200); c2 = pg.evaluate("() => CBApp._t.bgm")
            check(not c1['on'] and not c1['want'] and not c2['have'] and c2['ctx'] == 'suspended', f'カードバトルを 閉じた：BGM は 止まる・ほどいた 音は 手ばなす・音の 出口は 休む（{c2["ctx"]}）')
            open_cb(pg); pg.wait_for_function("() => CBApp._t.bgm.on", timeout=30000)
            check(pg.evaluate("() => CBApp._t.bgm.ctx") == 'running', 'もう一度 開く：覚えた 設定（オン）で また 鳴る')
        else:
            pg.wait_for_timeout(800); bn = pg.evaluate("() => CBApp._t.bgm")
            check(not bn['on'] and bn['gone'] and bn['want'], 'BGM の ファイルが ない ビルド：オンに しても 何も 鳴らさない（止まらない・エラーに ならない）')
            pg.locator('#cbOv .cbset [data-cb=quit]').click(); pg.locator('#cbOv .cbmod [data-cb=quitgo]').click(); pg.wait_for_timeout(150)
        # おぼえた 設定は 読み直しても 同じ → もとに もどす（あとの 場面は 決めて いない 形で）
        pg.evaluate("() => CBApp._t.load()")
        check(pg.evaluate("() => CBApp._t.sets.raw") == {'bgm': True, 'se': True}, '読み直しても 選んだ 設定の まま')
        pg.evaluate("() => { CBApp._t.setSet('bgm', false); localStorage.removeItem('tengel.cb'); CBApp._t.load(); }"); pg.wait_for_timeout(150)
        check(pg.evaluate("() => CBApp._t.sets.raw") == {'bgm': None, 'se': None} and not pg.evaluate("() => CBApp._t.bgm.on"), '（設定を 消して 元に 戻した：BGM は 止まって いる）')

        print('■ 効果を 使った ときの 札（第4.185版・まさちゃん 23:06「効果を使っている時が分かりにくいから、何の効果を使っていて、何をするのか分かるようにして！ テンゲルカードバトルの雰囲気は壊さないようにね！」）')
        pg.evaluate("""() => { window.__use = []; const e = document.querySelector('#cbOv .cbuse'); new MutationObserver(() => { if (!e.classList.contains('on')) return;
          const s = e.className + '|' + [...e.querySelectorAll('.cd img')].map(i => i.getAttribute('src')).join(','); if (window.__use[window.__use.length - 1] !== s) window.__use.push(s); }).observe(e, { attributes: true, attributeFilter: ['class'] }); }""")
        UG = """() => { const e = document.querySelector('#cbOv .cbuse'), i = e.querySelector('.in'), b = document.querySelector('#cbOv .cbboard'); const R = x => { const r = x.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; };
          const ts = q => parseFloat(getComputedStyle(e.querySelector(q)).fontSize), p = R(i), hit = document.elementFromPoint((p[0] + p[2]) / 2, (p[1] + p[3]) / 2);
          return { cls: e.className, p: p, b: R(b), vw: innerWidth, vh: innerHeight, who: e.querySelector('.who').textContent, t: e.querySelector('b').textContent, n: e.querySelector('em').textContent, d: e.querySelector('small').textContent,
            img: e.querySelector('.cd img').getAttribute('src'), z: +getComputedStyle(e).zIndex, fs: [ts('b'), ts('em'), ts('small'), ts('.who')], gold: e.querySelector('b').classList.contains('gold'), bd: getComputedStyle(i).borderTopColor,
            top: !!hit && hit.closest('.cbuse') === e, msg: document.querySelector('#cbOv .cbmsg').textContent, fit: [...e.querySelectorAll('.tx > *')].every(x => x.scrollWidth <= x.clientWidth + 1) }; }"""
        start(pg, '77712', '12345', '346')      # 第4.202版：7 の 効果は セットの 前
        pg.evaluate("() => CBApp._t.speed(1)"); pg.locator('#cbOv [data-cb=p7yes]').click()
        pg.wait_for_function("() => document.querySelector('#cbOv .cbuse.on')", timeout=10000); pg.wait_for_timeout(450); g = pg.evaluate(UG)
        check(g['cls'] == 'cbuse me on' and g['who'] == 'あなたが 使った！' and g['t'] == '7 の 効果' and g['n'] == '3枚 交換' and g['d'] == '7 を 3枚 山札に 戻して、新しく 3枚 引くよ' and g['img'] == 'cb_s7.webp' and g['gold'] and g['msg'] == '',
              f'効果の 札：誰が（あなたが 使った！）・どの 効果（7 の カードの 絵・「7 の 効果」・金の 字）・何を する（3枚 交換：…）。下の 行の 前の 文は 消える（{g["who"]}｜{g["t"]}｜{g["n"]}）')
        check(abs((g['p'][1] + g['p'][3]) / 2 - (g['b'][1] + g['b'][3]) / 2) <= 2 and g['p'][0] >= 8 and g['p'][2] <= g['vw'] - 8 and g['p'][3] - g['p'][1] <= g['b'][3] - g['b'][1] and g['z'] == 7 and g['top'] and g['fit']
              and g['fs'][0] >= 20 and g['fs'][1] >= 14 and g['fs'][2] >= 12 and g['fs'][3] >= 11 and g['bd'] == 'rgb(201, 163, 90)',
              f'札は ボードの 真ん中（{g["p"]}・ボード {g["b"]}）・画面の 中・ボードの 高さに おさまる・一番 上に 見える（窓〈z 8〉より 下）・字 {g["fs"]}px・金の ふち（{g["bd"]}）')
        shot(pg, 'cb_use_x7')
        pg.locator('#cbOv .cbuse').click(); pg.wait_for_timeout(300); off = pg.evaluate("() => !document.querySelector('#cbOv .cbuse.on')")
        idle(pg); pg.evaluate("() => CBApp._t.speed(0.03)")
        h1_ = pg.evaluate(HAND); v1_ = pg.evaluate(V); play(pg, '1'); opp(pg, {'t': 'set', 'k': 2})
        check(off and h1_ == '12346' and v1_['turn'] == 1 and v1_['phase'] == 'set' and pg.evaluate(HAND) == '2346' and pg.evaluate(V)['turn'] == 2, f'札を タップ → すぐ 消えて 次へ（7 を 3枚 交換：手札 {h1_} → まだ セットの 前 → セット → オープン → 2ターン目）')
        # 相手の 効果・2人とも・5・3・逆転勝利・幻の馬
        pg.evaluate("() => { window.__use.length = 0; }")
        start(pg, '12345', '77712', '346'); said(pg); opp(pg, {'t': 'x7'}); sd = said(pg)      # 第4.202版：相手も セットの 前に 使う
        check(any(x == 'use:コンピュータが 使った！7 の 効果3枚 交換7 を 3枚 山札に 戻して、新しく 3枚 引くよ' for x in sd) and pg.evaluate("() => window.__use") == ['cbuse op on|cb_s7.webp'],
              f'相手の 効果：「コンピュータが 使った！」（あかがねの 印：class op）（{pg.evaluate("() => window.__use")}）')
        pg.evaluate("() => { window.__use.length = 0; }")
        pg.evaluate("() => { window.__use.length = 0; }")
        start(pg, '41236', '41567'); play(pg, '4'); opp(pg, {'t': 'set', 'k': 4}); opp(pg, {'t': 'eff', 'use': {'u4': True}}); said(pg); pg.locator('#cbOv [data-cb=effyes]').click(); idle(pg)
        check(pg.evaluate("() => window.__use") == ['cbuse both on|cb_s4.webp,cb_s4.webp'], f'2人とも 4：「どちらも 使った！」・4 の カードが 2枚（{pg.evaluate("() => window.__use")}）')
        start(pg, '51237', '12346', 'k'); play(pg, '5'); opp(pg, {'t': 'set', 'k': 1}); pg.locator('#cbOv [data-cb=effyes]').click(); pg.wait_for_timeout(80); tap(pg, '7'); said(pg)
        pg.locator('#cbOv .cbmod [data-cb=drop5]').click(); idle(pg); sd = said(pg)
        iu = [i for i, x in enumerate(sd) if x == 'use:あなたが 使った！5 の 効果捨てて 山札から セットセットした 5 と 手札 1枚を 捨てて、山札から 1枚 伏せて セットするよ']; it = [i for i, x in enumerate(sd) if '5 と 7 を 捨てて、山札から 1枚 セットしたよ' in x]
        check(iu and it and iu[0] < it[0], f'5 の 効果：札 →「5 と 7 を 捨てて、山札から 1枚 セットしたよ」の 順（{[x[:30] for x in sd]}）')
        start(pg, '12456', '33312'); said(pg); opp(pg, {'t': 'x3', 'pickk': '4'}); sd = said(pg)
        check(any(x == 'use:コンピュータが 使った！3 の 効果手札を 交換3 を 3枚 見せて、その 1枚と あなたの 手札から 選んだ 1枚を 交換するよ' for x in sd), '3 の 効果（相手）：「…その 1枚と あなたの 手札から 選んだ 1枚を 交換するよ」（第4.229版：見えて いる カードも 選べる ので「裏の カード」は 言わない）')
        start(pg, '11123', 'm4567'); play(pg, '1'); said(pg); opp(pg, {'t': 'set', 'k': 'm'}); pg.locator('#cbOv .cbmod.cbask [data-cb=revyes]').click(); idle(pg); sd = said(pg)
        check(any(x == 'use:あなたが 使った！1 の 効果逆転勝利1 を 3枚（場の 1枚 ＋ 手札の 2枚）見せて、手札の 1 を 1枚 捨てると、幻の馬に 勝ち！' for x in sd), '逆転勝利（1）：「1 の 効果 逆転勝利 … 幻の馬に 勝ち！」')
        start(pg, 'm6712', '12345', '13'); play(pg, 'm'); opp(pg, {'t': 'set', 'k': 1}); pg.locator('#cbOv [data-cb=mpick]').click(); pg.wait_for_timeout(80); tap(pg, '6'); tap(pg, '7'); said(pg)
        pg.locator('#cbOv .cbact [data-cb=mgo]').click(); idle(pg); sd = said(pg)
        check(any(x == 'use:あなたが 使った！幻の馬の 効果捨てて 引き直す前の ターンに 幻の馬で 勝った ので、手札を 2枚 捨てて、山札から 2枚 引くよ' for x in sd), '幻の馬：「前の ターンに 幻の馬で 勝った ので、手札を 2枚 捨てて、山札から 2枚 引くよ」')
        # 効果を 使わない ときは 出ない・対戦を はなれたら 消える
        start(pg, '77712', '12345'); said(pg); pg.locator('#cbOv [data-cb=p7no]').click(); pg.wait_for_timeout(80); play(pg, '1'); opp(pg, {'t': 'set', 'k': 2})
        check(not any(x.startswith('use:') for x in said(pg)), '「使わない」→ 札は 出ない')
        start(pg, '77712', '12345', '346'); pg.evaluate("() => CBApp._t.speed(1)"); pg.locator('#cbOv [data-cb=p7yes]').click()
        pg.wait_for_function("() => document.querySelector('#cbOv .cbuse.on')", timeout=10000); pg.evaluate("() => CBApp._t.menu()"); pg.wait_for_timeout(300)
        check(pg.evaluate("() => [CBApp._t.screen, !!document.querySelector('#cbOv .cbuse.on')]") == ['menu', False], '札が 出て いる 時に 対戦を やめて メニューへ → 札は 消える')
        pg.evaluate("() => CBApp._t.speed(0.03)")

        print('■ 6：相手の 手札が もう 見た カード だけの ときは 聞かれない（第4.178版・まさちゃん「6.の効果は、もう見てるカードしかない場合は、発動しなくして！」）')
        KNOW = "(ks) => { const S = CBApp._t.match._.state(); S.p[1].hand.filter(c => ks.indexOf(c.k) >= 0).forEach(c => { if (S.p[0].known.indexOf(c.u) < 0) S.p[0].known.push(c.u); }); }"      # テスト用：相手の 手札の ks を「もう 見た」ことに する
        start(pg, '66123', '12345'); pg.locator('#cbOv .cbask [data-cb=sixno]').click(); idle(pg); pg.evaluate(KNOW, ['3', '4']); play(pg, '1'); opp(pg, {'t': 'set', 'k': 2})
        check(pg.evaluate(V)['turn'] == 2 and asked(pg) == ['6 の 効果を 使う？', '6 を 2枚 見せて、相手の 手札を 1枚 見られるよ（セットの 前：見てから セットする カードを 選べる）'] and pg.locator('#cbOv .cbohand .cbc img[src="cb_sb.webp"]').count() == 2,
              '2ターン目の はじめ：相手の 手札 4枚の うち 2枚を もう 見た：まだ 見て いない カードが ある ので 6 の 効果は 聞かれる')
        pg.locator('#cbOv [data-cb=sixyes]').click(); pg.wait_for_timeout(80)
        pm = pg.evaluate("() => ({ n: document.querySelectorAll('#cbOv .cbmod .pick .cbc').length, dis: [...document.querySelectorAll('#cbOv .cbmod .pick .cbc')].filter(b => b.disabled).map(b => b.querySelector('img').getAttribute('src')).sort().join(), can: document.querySelectorAll('#cbOv .cbmod .pick .cbc[data-cb=pick]').length, t: document.querySelector('#cbOv .cbmod p').textContent })")
        check(pm == {'n': 4, 'dis': 'cb_s3.webp,cb_s4.webp', 'can': 2, 't': pm['t']} and 'もう 見た カードは 選べないよ' in pm['t'], f'選ぶ 窓：もう 見た カード（3・4：表・暗く）は 押せない・選べるのは まだ 見て いない 2枚 だけ（{pm["dis"]}）')
        pg.evaluate("() => { document.querySelector('#cbOv .cbmod .pick .cbc:disabled').click(); }"); pg.wait_for_timeout(80)
        check(pg.evaluate("() => CBApp._t.modOn()") and pg.evaluate(V)['phase'] == 'six', 'もう 見た カードを 押しても 何も おきない')
        pg.locator('#cbOv .cbmod .pick .cbc[data-cb=pick]').first.click(); idle(pg)
        check(pg.evaluate(V)['turn'] == 2 and pg.evaluate(V)['phase'] == 'set' and len([c for c in pg.evaluate(V)['op']['hand'] if c['k']]) == 3, 'まだ 見て いない カードを 選ぶ → 見た カードが 3枚に（その あと セット）')
        shot(pg, 'cb_pick_known')
        start(pg, '66123', '12345'); pg.locator('#cbOv .cbask [data-cb=sixno]').click(); idle(pg); pg.evaluate(KNOW, ['1', '2', '3', '4', '5']); play(pg, '1'); said(pg); pg.evaluate("() => { window.__seen = []; }")
        opp(pg, {'t': 'set', 'k': 2}); sd = said(pg); v = pg.evaluate(V)
        check(not any(s.startswith('ban:6 の 効果') for s in sd) and asked(pg) is None and v['turn'] == 2 and v['phase'] == 'set' and any('勝ち！' in s for s in pg.evaluate("() => window.__seen")) and pg.locator('#cbOv .cbohand .cbc img[src="cb_sb.webp"]').count() == 0 and pg.evaluate(HAND) == '2366',
              '相手の 手札を 全部 もう 見た：6 が 2枚 あっても 次の ターンの 始めに 聞かれない → そのまま セット')
        start(pg, 'k2367', '12345'); pg.evaluate(KNOW, ['1', '2', '3', '4', '5']); play(pg, 'k'); said(pg); opp(pg, {'t': 'set', 'k': 1}); sd = said(pg); v = pg.evaluate(V)
        check(v['turn'] == 2 and v['phase'] == 'set' and v['pend'] is None and asked(pg) is None and not any('神様馬の 効果' in s for s in sd) and v['my']['wins'] == 1, '神様馬で 勝っても、相手の 手札を 全部 もう 見た ときは 効果を 聞かれない（見る ものが ない）')

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
                  f'光の 色：左上は 月あかり（青み：赤 {col["tl"][0]:.0f}・青 {col["tl"][2]:.0f}）・右下は 火の あかり（だいだい：赤 {col["br"][0]:.0f}・青 {col["br"][2]:.0f}）・真ん中の フェルトは 緑の まま（{[round(q) for q in col["felt"]]}）')
        pg.emulate_media(reduced_motion='reduce'); pg.wait_for_timeout(100); rm = pg.evaluate(FIRE); pg.emulate_media(reduced_motion='no-preference'); pg.wait_for_timeout(100)
        check(len(rm) == 2 and all(x.startswith('none ') for x in rm) and pg.evaluate(FIRE) == ['cbfire 5.6s none', 'cbfire 4.3s none'], f'iPhone の「視差効果を減らす」が オンの ときは ゆれない（動きの 名前が none：{rm}）')

        print('■ 逆転勝利：1 が 3枚 → 神様馬・幻の馬に 勝てる ／ 2 が 3枚 → 1 に 勝てる（第4.178版・まさちゃん 15:33・15:41「A、オープンしてから」）')
        start(pg, '11123', 'm4567'); play(pg, '1'); said(pg); pg.evaluate("() => { window.__seen = []; window.__win.length = 0; }")
        opp(pg, {'t': 'set', 'k': 'm'}); seen = pg.evaluate("() => window.__seen"); v = pg.evaluate(V); aw = pg.evaluate(ASKQ)
        check(any('ターン 1　オープン！' in s and 'チャンス！' in s and '幻の馬 の ほうが 強い…でも 1 の「逆転勝利」を 使えるよ' in s and 'cb_c1.webp,cb_cm.webp' in s for s in seen) and not any('負け…' in s for s in seen) and pg.evaluate(PIPS) == '0-0'
              and v['phase'] == 'rev' and v['turn'] == 1 and v['pend'] == {'type': 'rev', 'mine': True} and v['op']['wins'] == 0,
              f'1（手札に 1 が あと 2枚）と 幻の馬 → めくった 窓に「チャンス！ …1 の「逆転勝利」を 使えるよ」（「負け…」は まだ 出ない・勝ちの 印も まだ）（{seen[-1] if seen else None}）')
        check(aw and aw['head'] == '逆転の チャンス！' and aw['q'] == '1 の 効果を 使う？' and aw['text'] == '手札の 1 を 2枚 見せて、1枚 捨てると、幻の馬に 勝てるよ' and aw['img'] == 'cb_c1.webp' and aw['btns'] == ['使わない', '使う', '手札と ボードを 見る']
              and pg.evaluate(SLOT) == 'm 1' and acts(pg) == [] and pg.evaluate(MSG) == '効果を 使うか 選んでね',
              f'続けて 聞く 窓「逆転の チャンス！／1 の 効果を 使う？」（1 の カードの 絵・使わない／使う）。ボードには 2枚とも 表（{pg.evaluate(SLOT)}）')
        shot(pg, 'cb_rev_ask')
        peek(pg)
        check(asked(pg) is None and pg.evaluate(MSG) == '逆転の チャンス！ 1 の 効果を 使う？\n手札の 1 を 1枚 捨てて、幻の馬に 勝てるよ' and acts(pg) == ['使わない', '1 の 効果を 使う'], '「手札と ボードを 見る」→ 下の 行の「使わない」「1 の 効果を 使う」で 答えられる')
        tap(pg, '1'); check(modbtns(pg) == ['戻る'], '決める までは 手札を タップしても 見る だけ'); pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        pg.locator('#cbOv .cbact [data-cb=revyes]').click(); idle(pg)
        win = pg.evaluate("() => window.__win"); sd = said(pg); v = pg.evaluate(V)
        w1 = [s for s in win if s.startswith('1 の 効果！|')]
        check(w1 and '1 を 3枚（場の 1枚 ＋ 手札の 2枚）見せたよ' in w1[0] and '手札の 1 を 1枚 捨てて、幻の馬に 逆転！' in w1[0] and w1[0].count('cb_s1.webp') == 3 and any(s.startswith('ban:逆転勝利！') and '1 が 幻の馬 に 勝ったよ' in s for s in sd),
              f'「使う」→ 1 の カードを 3枚 見せる 窓 →「逆転勝利！ 1 が 幻の馬 に 勝ったよ」（{w1[0] if w1 else None}）')
        check(v['turn'] == 2 and v['phase'] == 'set' and v['pend'] is None and v['my']['wins'] == 1 and v['op']['wins'] == 0 and pg.evaluate(PIPS) == '0-1' and pg.evaluate(HAND) == '123' and pg.evaluate(DOMHAND) == '123' and pg.locator('#cbOv .cbdis .cbn').inner_text() == '3'
              and v['last'] == {'turn': 1, 'c': ['1', 'm'], 'res': 'win', 'rev': True, 'd4': False} and not any('幻の馬の 効果' in s for s in sd),
              f'勝ちの 印が 1つ・手札は 1・2・3（1 を 1枚 捨てた）・捨て札 3枚・幻の馬の 効果は 出ない → 2ターン目の セットへ（手札 {pg.evaluate(HAND)}）')
        eye = pg.evaluate("""() => { const es = [...document.querySelectorAll('#cbOv .cbhand .cbc .eye')]; return es.map(e => { const r = e.getBoundingClientRect(), h = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2), c = e.closest('.cbc'), cr = c.getBoundingClientRect();
          return { k: c.querySelector('img').getAttribute('src'), vis: !!h && (h === e || h === c || c.contains(h)), in: r.left >= cr.left - 4 && r.right <= cr.left + cr.width * 0.62 }; }); }""")
        check(eye == [{'k': 'cb_s1.webp', 'vis': True, 'in': True}], f'見せて 手札に 残った 1 に 目の 印（相手が 知って いる）：印は カードの 見える 所（左から 60% の 内がわ）に ある（{eye}）')
        pg.locator('#cbOv [data-cb=discard]').click(); pg.wait_for_timeout(80); dm = pg.evaluate(DM)
        check(dm['turns'] == ['ターン 1|あなた=1|コンピュータ=m'] and dm['effs'] == ['ターン 1|あなたの 1 の 効果=1'], f'捨て札の 窓：効果で 捨てた カードに「あなたの 1 の 効果」（{dm["effs"]}）')
        shot(pg, 'cb_rev_discard')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        # 使わない → そのまま 負け・相手の 幻の馬の 効果
        start(pg, '11123', 'm4567'); play(pg, '1'); opp(pg, {'t': 'set', 'k': 'm'}); said(pg)
        pg.locator('#cbOv .cbask [data-cb=revno]').click(); idle(pg); sd = said(pg); v = pg.evaluate(V)
        check(any(s.startswith('ban:負け…') and '幻の馬 が 1 に 勝ったよ' in s for s in sd) and v['turn'] == 2 and v['phase'] == 'pre' and v['pend'] == {'type': 'm', 'mine': False} and v['op']['wins'] == 1 and v['my']['wins'] == 0 and pg.evaluate(PIPS) == '1-0'
              and pg.evaluate(HAND) == '1123' and pg.locator('#cbOv .cbhand .cbc .eye').count() == 0 and 'コンピュータが 幻の馬の 効果を 使うか 選んで いるよ' in pg.evaluate(MSG),
              '「使わない」→「負け…」・手札は そのまま（何も 見せない）・相手の 幻の馬の 効果（次の ターンの 始め）は いつも どおり')
        # 神様馬にも・7まいの 手札でも
        start(pg, '1112345', 'mk23456', turns=5); play(pg, '1'); opp(pg, {'t': 'set', 'k': 'k'})
        aw = pg.evaluate(ASKQ)
        check(aw and aw['text'] == '手札の 1 を 2枚 見せて、1枚 捨てると、神様馬に 勝てるよ' and pg.evaluate(V)['phase'] == 'rev', '本番の 形（手札 7枚・5ターン）：1 と 神様馬 →「…神様馬に 勝てるよ」')
        pg.locator('#cbOv .cbask [data-cb=revyes]').click(); idle(pg); v = pg.evaluate(V)
        check(v['turn'] == 2 and v['my']['wins'] == 1 and pg.evaluate(HAND) == '12345' and pg.locator('#cbOv .cbhand .cbc .eye').count() == 1 and v['phase'] == 'set', '使う → 勝ち・手札 5枚（1 が 1枚 残る）')
        play(pg, '1'); pg.evaluate("() => { window.__seen = []; }"); opp(pg, {'t': 'set', 'k': 'm'}); v = pg.evaluate(V)
        check(any('負け…' in s and '幻の馬 の ほうが 強いよ' in s for s in pg.evaluate("() => window.__seen")) and v['turn'] == 3 and v['pend'] == {'type': 'm', 'mine': False} and v['op']['wins'] == 1, '2ターン目：残った 1 を 出して 幻の馬 → 手札に 1 が ない ので 聞かれない（普通に 負け）')
        # 相手が 使う：2 が 3まいで 自分の 1 に 勝つ
        start(pg, '1m345', '22214'); play(pg, '1'); said(pg); pg.evaluate("() => { window.__seen = []; window.__win.length = 0; }")
        opp(pg, {'t': 'set', 'k': 2}); seen = pg.evaluate("() => window.__seen"); v = pg.evaluate(V)
        check(any('勝負は まだ！' in s and 'コンピュータは 2 の「逆転勝利」を 使えるよ' in s for s in seen) and not any('勝ち！' in s for s in seen) and v['phase'] == 'rev' and v['pend'] == {'type': 'rev', 'mine': False} and v['wait'] is True and asked(pg) is None and acts(pg) == []
              and 'コンピュータが 逆転勝利を 使うか 選んで いるよ' in pg.evaluate(MSG) and pg.evaluate(PIPS) == '0-0' and pg.evaluate(SLOT) == '2 1',
              f'自分の 1 と 相手の 2（相手は 2 を 3枚）→ めくった 窓に「勝負は まだ！ コンピュータは 2 の「逆転勝利」を 使えるよ」・自分は 待つ（「勝ち！」は まだ 出ない）')
        shot(pg, 'cb_rev_wait')
        MSGLOG = "() => { window.__msgs = []; const m = document.querySelector('#cbOv .cbmsg'); window.__mo2 = new MutationObserver(() => window.__msgs.push(m.textContent)); window.__mo2.observe(m, { childList: true, characterData: true, subtree: true }); }"
        pg.evaluate(MSGLOG)
        r = opp(pg, {'t': 'rev', 'use': True}); win = pg.evaluate("() => window.__win"); sd = said(pg); v = pg.evaluate(V); msgs = pg.evaluate("() => { window.__mo2.disconnect(); return window.__msgs; }")
        w2 = [s for s in win if s.startswith('2 の 効果！|')]
        check(r['ok'] and w2 and 'コンピュータが 2 を 3枚（場の 1枚 ＋ 手札の 2枚）見せたよ' in w2[0] and '手札の 2 を 1枚 捨てて、1 に 逆転！' in w2[0] and w2[0].count('cb_s2.webp') == 3 and any(s.startswith('ban:逆転負け…') and '2 が 1 に 勝ったよ' in s for s in sd),
              f'相手が 使った → 2 の カードを 3枚 見せる 窓 →「逆転負け… 2 が 1 に 勝ったよ」（{w2[0] if w2 else None}）')
        check(v['turn'] == 2 and v['op']['wins'] == 1 and v['my']['wins'] == 0 and pg.evaluate(PIPS) == '1-0' and pg.locator('#cbOv .cbohand .cbc').count() == 3 and pg.locator('#cbOv .cbohand .cbc img[src="cb_s2.webp"]').count() == 1 and pg.locator('#cbOv .cbohand .cbc img[src="cb_sb.webp"]').count() == 2
              and msgs and msgs[0] == '' and v['last']['rev'] is True,
              f'相手の 勝ち・相手の 手札は 3枚（見せて 残った 2 は 表で 見える）・動きの 間「…使うか 選んで いるよ…」は 消える（{msgs[:2]}）')
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
        check(se_['t'] == '2 の 効果を 使う？手札の 2 を 2枚 見せて、1枚 捨てると、1 に 勝てるよ' and se_['h3'][1] >= 0 and se_['peek'][3] <= se_['vh'] and all(a[3] <= b[1] + 1 for a, b in zip(order, order[1:])) and all(r[0] >= 0 and r[2] <= se_['vw'] for r in order) and se_['img'][2] - se_['img'][0] >= 120,
              f'iPhone SE（375×647）：2 の 逆転勝利の 聞く 窓「…1 に 勝てるよ」も 重ならずに 画面の 中（絵の 幅 {se_["img"][2] - se_["img"][0]}px・下の はし {se_["peek"][3]}／{se_["vh"]}）')
        shot(pg, 'cb_rev_ask_se')
        pg.locator('#cbOv .cbask [data-cb=revyes]').click(); idle(pg)
        check(pg.evaluate(V)['my']['wins'] == 1 and pg.evaluate(HAND) == '12345' and pg.evaluate(V)['last'] == {'turn': 1, 'c': ['2', '1'], 'res': 'win', 'rev': True, 'd4': False}, '2 の 効果を 使う → 1 に 勝ち（手札 7枚の 形）')
        pg.set_viewport_size({'width': 390, 'height': 844}); pg.wait_for_timeout(250)

        print('■ 結果と ご褒美（バトルコイン・連勝で 調査隊切符）')
        # 第4.212版（まさちゃん 2026/11/23 10:19「テンゲルカードバトルの勝利時のお世話トークンは廃止しなかったっけ？」→ 廃止・「通常CPUバトルの場合、3連勝で調査隊切符1枚、5連勝で調査隊切符2枚を追加して！」）：
        #   勝っても お世話トークンは もらえない（トレーニングセンターの 部品も 読まない）・コンピュータに 3連勝 ごとに 調査隊切符 1枚・5連勝 ごとに 2枚（15枚 まで）。ここは 切符 10枚から
        QTN = "() => CBApp._t.qt.n"
        pg.evaluate("() => { localStorage.removeItem('tengel.cb'); CBApp._t.load(); const T = CBApp._t; T.state.qt = { n: 10, at: Date.now() }; T.save(); }")
        def win_game():
            start(pg, 'k1236', '23567'); play(pg, 'k'); opp(pg, {'t': 'set', 'k': 6}); pg.locator('#cbOv [data-cb=kskip]').click(); idle(pg)      # 2ターン目の はじめ：神様馬の 効果は 使わない
            play(pg, '1'); opp(pg, {'t': 'set', 'k': 7}); play(pg, '2'); opp(pg, {'t': 'set', 'k': 3})
            pg.wait_for_function("() => { const g = document.querySelector('#cbOv .cbend .gift'); return CBApp._t.ended && g && g.textContent.length > 3; }", timeout=30000)
            return pg.evaluate("() => ({ h: document.querySelector('#cbOv .cbend h3').textContent, sc: document.querySelector('#cbOv .cbend .sc').textContent, g: document.querySelector('#cbOv .cbend .gift').textContent, st: Object.assign({}, CBApp._t.state) })")
        t0 = pg.evaluate(TC)
        e = win_game(); t1 = pg.evaluate(TC)
        check(e['st']['coin'] == 2 and 'バトルコイン ＋2枚（今 2枚）' in e['g'] and pg.locator('#cbOv .cbend .gift .cbcl img[src="cb_coin.webp"]').count() == 1 and 'ボーナス！＋' not in e['g'] and pg.locator('#cbOv .cbend .gift .cbsbn').count() == 0,
              f'バトルコイン：コンピュータに 勝つと 2枚（今 {e["st"]["coin"]}枚）（第4.179版 → 第4.188版：1枚 → 2枚）・1連勝では ボーナスの 札は 出ない')
        check(e['h'] == 'あなたの 勝ち！' and e['sc'].startswith('3 － 0') and t1 == t0 and e['st']['streak'] == 1 and e['st']['win'] == 1 and 'owe' not in e['st'] and 'お世話トークン' not in e['g'] and 'GET' not in e['g'] and '1連勝中！' in e['g'] and 'あと 2勝で 調査隊切符' in e['g']
              and pg.evaluate(QTN) == 10 and pg.locator('#cbOv .cbend .cbget').count() == 0 and pg.locator('#cbOv .cbend .cbtkl').count() == 0 and pg.evaluate("() => !window.TCApp && typeof window.TCGift === 'undefined'") and 'tc_bundle.js' not in reqs,
              f'勝ち：お世話トークンは もらえない（第4.212版で 廃止：{t0} の まま・トレーニングセンターの 部品も 読まない・わたす 口 TCGift も ない）・1連勝中・あと 2勝で 調査隊切符（切符は 10枚の まま）（{e["g"]}）')
        # 第4.212版：お世話トークンの 札（第4.177版の「お世話トークン ＋1こ GET！」）は もう 出ない。ごほうびの 場所は 先に あけて ある（高さ 204px：札が 出ても まわりは 動かない）
        pg.wait_for_timeout(300)
        gb = pg.evaluate("""() => { const m = document.querySelector('#cbOv .cbmod.cbend'), g = m.querySelector('.gift'), R = e => { const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; };
          return { gift: R(g), minh: parseFloat(getComputedStyle(g).minHeight), h3: R(m.querySelector('h3')), again: R(m.querySelector('[data-cb=again]')), vh: innerHeight, get: m.querySelectorAll('.cbget').length, css: /#cbOv \\.cbget\\{/.test([...document.querySelectorAll('style')].map(x => x.textContent).join('')) }; }""")
        check(gb['get'] == 0 and not gb['css'] and gb['gift'][3] - gb['gift'][1] == gb['minh'] == 204 and gb['again'][3] <= gb['vh'] and gb['h3'][1] >= 0,
              f'最後の 画面に お世話トークンの 札は 出ない（形の きまりも ない）・ごほうびの 場所は 先に あけて ある（高さ {gb["minh"]}px：「あなたの 勝ち！」や ボタンは 動かない）')
        shot(pg, 'cb_end_win')
        pg.locator('#cbOv .cbend [data-cb=again]').click(); idle(pg)
        check(pg.evaluate(V)['turn'] == 1 and pg.evaluate(V)['phase'] == 'set' and not pg.evaluate("() => CBApp._t.ended") and pg.evaluate(PIPS) == '0-0' and not pg.evaluate("() => CBApp._t.modOn()"), '「もう 1回」→ すぐ 新しい 対戦（印も 0 に）')
        e = win_game()
        check(e['st']['coin'] == 4 and 'バトルコイン ＋2枚（今 4枚）' in e['g'] and pg.locator('#cbOv .cbend .gift .cbsbn').count() == 0 and 'あと 1勝で 調査隊切符' in e['g'] and pg.evaluate(QTN) == 10, f'2連勝目：バトルコイン ＋2枚（今 {e["st"]["coin"]}枚）・ボーナスの 札は 出ない・あと 1勝で 調査隊切符')
        e = win_game()
        sb3 = pg.evaluate("""() => { const g = document.querySelector('#cbOv .cbend .gift'), b = g.querySelector('.cbsbn'), m = g.querySelector('.cbmsn'), R = e => { const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; };
          return b ? { t: b.textContent, lab: b.getAttribute('aria-label'), img: b.querySelectorAll('img[src="cb_coin.webp"]').length, tki: b.querySelectorAll('img.tki').length, tkl: (g.querySelector('.cbtkl') || {}).textContent || '', tklbox: g.querySelector('.cbtkl') ? R(g.querySelector('.cbtkl')) : null, anim: getComputedStyle(b).animationName + '/' + getComputedStyle(b).animationIterationCount, box: R(b), mbox: m ? R(m) : null,
            gift: R(g), h: Math.round(g.getBoundingClientRect().height), minh: parseFloat(getComputedStyle(g).minHeight), vw: innerWidth, bc: getComputedStyle(b).borderTopColor } : null; }""")
        check(e['st']['coin'] == 42 and e['st']['streak'] == 3 and 'バトルコイン ＋2枚（今 42枚）' in e['g'] and '🎯ミッション達成！3連勝＋30枚' in e['g'] and sb3 and sb3['t'] == '🔥3連勝 ボーナス！＋6枚＋1枚' and sb3['lab'] == '3連勝 ボーナス バトルコイン 6枚 調査隊切符 1枚' and sb3['img'] == 1 and sb3['tki'] == 1
              and sb3['anim'] == 'cbget/1' and sb3['mbox'] and sb3['box'][3] <= sb3['mbox'][1] and sb3['box'][0] >= 0 and sb3['box'][2] <= sb3['vw'] and sb3['h'] == sb3['minh'],
              f'3連勝目（第4.188版）：いつもの 2枚 ＋ 3連勝 ボーナス 6枚 ＋ ミッション 30枚（2＋2＋8＋30＝{e["st"]["coin"]}枚）・最後の 画面に「🔥 3連勝 ボーナス！ 🪙＋6枚 🎫＋1枚」の 札（ミッションの 札の 上・1回 ふくらむ だけ・札の 場所に おさまる {sb3 and sb3["h"]}／{sb3 and sb3["minh"]}px）')
        check(pg.evaluate(QTN) == 11 and sb3 and sb3['tkl'] == '調査隊切符 今 11枚' and sb3['tklbox'] and sb3['box'][3] <= sb3['tklbox'][1] and sb3['tklbox'][3] <= sb3['mbox'][1] and 'あと 2勝で 調査隊切符' in e['g'],
              f'第4.212版：3連勝で 調査隊切符 ＋1枚（10 → {pg.evaluate(QTN)}枚）・札の 下に「調査隊切符 今 11枚」・次は あと 2勝（5連勝）')
        shot(pg, 'cb_end_bonus3')
        win_game()
        e = win_game(); t5 = pg.evaluate(TC)
        check(e['st']['coin'] == 116 and 'バトルコイン ＋2枚（今 116枚）' in e['g'] and '🔥5連勝 ボーナス！＋10枚' in e['g'] and '🎯ミッション達成！5連勝＋60枚' in e['g'] and e['st']['ms']['cpu'] == 5 and e['st']['ms']['got']['cpu'] == [3, 5],
              f'バトルコイン：5連勝目は 2枚 ＋ 5連勝 ボーナス 10枚（2・2・8・2・12）＋ ミッション（3連勝 30枚・5連勝 60枚：第4.183版）＝ {e["st"]["coin"]}枚・最後の 画面に「🔥 5連勝 ボーナス！ ＋10枚」「🎯 ミッション達成！ 5連勝 ＋60枚」')
        check(e['st']['streak'] == 5 and e['st']['win'] == 5 and t5 == t0 and pg.evaluate(QTN) == 13 and '🔥5連勝 ボーナス！＋10枚＋2枚' in e['g'] and '調査隊切符 今 13枚' in e['g'] and '5連勝中！' in e['g'] and 'あと 1勝で 調査隊切符' in e['g'] and 'お世話トークン' not in e['g']
              and pg.evaluate("() => { const g = document.querySelector('#cbOv .cbend .gift'); return Math.round(g.getBoundingClientRect().height) === parseFloat(getComputedStyle(g).minHeight); }"), f'5連勝：調査隊切符 ＋2枚（11 → {pg.evaluate(QTN)}枚）・お世話トークンは なし（{e["g"]}）')
        e = win_game()
        check(e['st']['streak'] == 6 and pg.evaluate(QTN) == 14 and 'あと 3勝で 調査隊切符' in e['g'] and '調査隊切符 今 14枚' in e['g'] and e['st']['coin'] == 214 and 'バトルコイン ＋2枚（今 214枚）' in e['g'] and '🔥6連勝 ボーナス！＋6枚＋1枚' in e['g'] and '🎯ミッション達成！6連勝＋90枚' in e['g'],
              '6連勝目（3連勝 ごと）：調査隊切符 ＋1枚（14枚）・バトルコインは ＋2 と 3連勝 ごとの ボーナス ＋6・ミッション 6連勝 ＋90枚')
        # 7連勝：切符の ボーナスは ない（3 でも 5 でも 割りきれない）
        e = win_game()
        check(e['st']['streak'] == 7 and pg.evaluate(QTN) == 14 and pg.locator('#cbOv .cbend .cbtkl').count() == 0 and pg.locator('#cbOv .cbend .cbsbn').count() == 0 and 'あと 2勝で 調査隊切符' in e['g']
              and pg.evaluate("() => { const g = document.querySelector('#cbOv .cbend .gift'); return Math.round(g.getBoundingClientRect().height) === parseFloat(getComputedStyle(g).minHeight); }"),
              f'7連勝：調査隊切符の ボーナスは ない（14枚の まま・連勝ボーナスの 札も ない）（{e["g"]}）')
        win_game()      # 8連勝
        # 上限 15枚：もう いっぱいの とき（9連勝＝3連勝 ごと ＋1）→ 増えない・札には 出さずに 1行で 知らせる
        pg.evaluate("() => { const T = CBApp._t; T.state.qt = { n: 15, at: Date.now() }; T.save(); }")
        e = win_game()
        check(e['st']['streak'] == 9 and pg.evaluate(QTN) == 15 and '調査隊切符は いっぱい（15枚）なので、今回は 増えなかったよ' in e['g'] and '🔥9連勝 ボーナス！＋6枚' in e['g'] and '＋6枚＋' not in e['g'] and pg.locator('#cbOv .cbend .cbsbn img.tki').count() == 0
              and pg.locator('#cbOv .cbend .cbsbn').get_attribute('aria-label') == '9連勝 ボーナス バトルコイン 6枚'
              and pg.evaluate("() => { const g = document.querySelector('#cbOv .cbend .gift'); return Math.round(g.getBoundingClientRect().height) === parseFloat(getComputedStyle(g).minHeight); }"),
              f'調査隊切符が 15枚の とき：増えない（連勝ボーナスの 札は バトルコイン だけ・「いっぱい なので 増えなかった」の 1行）（{e["g"]}）')
        pg.evaluate("() => { const T = CBApp._t; T.state.qt = { n: 14, at: Date.now() }; T.save(); }")
        e = win_game()      # 10連勝：＋2 の はずが、あと 1枚 しか 入らない
        check(e['st']['streak'] == 10 and pg.evaluate(QTN) == 15 and '🔥10連勝 ボーナス！＋10枚＋1枚' in e['g'] and '調査隊切符 今 15枚（15枚 まで なので 1枚 だけ）' in e['g'] and pg.evaluate(TC) == t0
              and pg.evaluate("() => { const g = document.querySelector('#cbOv .cbend .gift'); return Math.round(g.getBoundingClientRect().height) === parseFloat(getComputedStyle(g).minHeight); }"), f'10連勝（＋2）で あと 1枚 しか 入らない とき：入る 分 だけ（{e["g"]}）')
        check(e['st']['coin'] == 1008 and 'バトルコイン ＋2枚（今 1008枚）' in e['g'] and '🔥10連勝 ボーナス！＋10枚' in e['g'] and '🎯ミッション達成！10連勝＋300枚' in e['g'] and e['st']['ms']['got']['cpu'] == [3, 5, 6, 7, 8, 9, 10] and e['st']['ms']['cpu'] == 10,
              f'10連勝目は バトルコイン 2枚 ＋ 5連勝 ごとの ボーナス 10枚 ＋ ミッション 10連勝 300枚（勝つ 分 2×10＝20・ボーナス 6×3＋10×2＝38・ミッション 950：今 {e["st"]["coin"]}枚）・字は 札の 場所に おさまる')
        shot(pg, 'cb_end_coin')
        # 負け：連勝 0
        start(pg, '23677', '12356'); play(pg, '3'); opp(pg, {'t': 'set', 'k': 1}); play(pg, '6'); opp(pg, {'t': 'set', 'k': 2}); play(pg, '7'); opp(pg, {'t': 'set', 'k': 3})
        pg.wait_for_function("() => { const g = document.querySelector('#cbOv .cbend .gift'); return CBApp._t.ended && g && g.textContent.length > 3; }", timeout=30000)
        e = pg.evaluate("() => ({ h: document.querySelector('#cbOv .cbend h3').textContent, g: document.querySelector('#cbOv .cbend .gift').textContent, st: Object.assign({}, CBApp._t.state) })")
        check(e['h'] == 'あなたの 負け…' and e['st']['streak'] == 0 and e['st']['lose'] == 1 and '連勝は 0 に 戻ったよ' in e['g'] and pg.evaluate(TC) == t0 and pg.evaluate(QTN) == 15 and pg.locator('#cbOv .cbend .cbget').count() == 0 and pg.locator('#cbOv .cbend .cbtkl').count() == 0, f'負け：連勝は 0 に 戻る・お世話トークンも 調査隊切符も 変わらない・札は 出ない（{e["g"]}）')
        pg.locator('#cbOv .cbend [data-cb=menu]').click(); pg.wait_for_timeout(120)
        rec = pg.locator('#cbOv .cbmenu .rec').inner_text()
        check(pg.evaluate("() => CBApp._t.screen") == 'menu' and '10勝 1敗 0分' in rec.replace('\n', ' '), f'メニューに 勝ち負けの 数（{rec!r}）')
        check(e['st']['coin'] == 1008 and 'バトルコイン' not in e['g'] and 'バトルコイン 1008枚' in pg.locator('#cbOv .cbmenu .cbcoinl').inner_text() and e['st']['ms']['cpu'] == 0 and e['st']['ms']['got']['cpu'] == [3, 5, 6, 7, 8, 9, 10],
              '負け：バトルコインは 変わらない（減らない）・メニューに 今の 数（1008枚）・ミッションの 連勝は 0（達成した ものは 残る）')

        print('■ 途中で やめる')
        start(pg, '12367', '23567'); play(pg, '1')
        s0 = pg.evaluate("() => Object.assign({}, CBApp._t.state)")
        pg.locator('#cbOv .cbtop [data-cb=quit]').click(); pg.wait_for_timeout(80)
        check('途中で やめると 負けに なるよ' in pg.locator('#cbOv .cbmod').inner_text(), '「やめる」→ 確かめる 窓（途中で やめると 負け）')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        check(pg.evaluate("() => CBApp._t.screen") == 'game' and pg.evaluate(V)['my']['set'] is not None, '「続ける」→ 対戦に 戻る')
        pg.locator('#cbOv .cbgear').click(); pg.wait_for_timeout(80)
        check([x.inner_text() for x in pg.locator('#cbOv .cbmod .cbb').all()] == ['対戦に 戻る', '遊び方', '対戦を やめる'], 'ボードの 歯車 → メニュー（対戦に 戻る・遊び方・対戦を やめる）')
        pg.locator('#cbOv .cbmod [data-cb=help]').click(); pg.wait_for_timeout(80)
        check(pg.evaluate("() => CBApp._t.screen") == 'help', '歯車 → 遊び方')
        pg.locator('#cbOv [data-cb=helpx]').click(); pg.wait_for_timeout(80)
        check(pg.evaluate("() => CBApp._t.screen") == 'game' and pg.evaluate(DOMHAND) == '2367', '遊び方から 戻る → 対戦の 続き')
        pg.locator('#cbOv .cbtop [data-cb=quit]').click(); pg.locator('#cbOv .cbmod [data-cb=quitgo]').click(); pg.wait_for_timeout(120)
        s1 = pg.evaluate("() => Object.assign({}, CBApp._t.state)")
        check(pg.evaluate("() => CBApp._t.screen") == 'menu' and s1['lose'] == s0['lose'] + 1 and s1['streak'] == 0 and pg.evaluate("() => CBApp._t.match") is None, '途中で やめた → 負けに 数える・メニューへ')
        pg.locator('#cbOv .cbmenu [data-cb=close]').click(); pg.wait_for_timeout(120)
        check(pg.evaluate("() => !document.querySelector('#cbOv').classList.contains('on')") and pg.locator('#cbFab').is_enabled(), '「← 戻る」→ カードバトルを 閉じる（ボタンは また 押せる）')

        print('■ コンピュータが 自分で 考えて 出す（普通の 対戦）')
        open_cb(pg)
        pg.evaluate("() => { CBApp._think = () => 30; CBApp._opt = null; CBApp._rng = null; }")
        pg.locator('#cbOv .cbmenu [data-cb=cpu]').click()
        done = False; first = None
        for step in range(160):
            idle(pg, 60000)
            if first is None: first = pg.evaluate("() => { const v = CBApp._t.view; return v ? [v.turns, v.my.hand.length + (v.my.set ? 1 : 0), v.op.hand.length + (v.op.set ? 1 : 0), v.deckN] : null; }")
            stt = pg.evaluate("() => { const v = CBApp._t.view; return CBApp._t.ended ? 'end' : !v ? 'none' : v.pend && v.pend.mine ? v.pend.type : v.can.six ? 'six' : v.can.eff ? 'eff' : v.can.set ? ((v.can.x7r || v.can.x7 || v.can.x3) && CBApp._t.ask ? 'x7' : 'set') : 'wait'; }")
            if stt == 'end': done = True; break
            if stt == 'x7': pg.locator('#cbOv .cbask [data-cb=x7no], #cbOv .cbask [data-cb=p7no], #cbOv .cbask [data-cb=p3no]').first.click()      # 第4.187版：7 が 4まい・第4.202版：7 が 3まい・3 が 3まい（セットの 前）→ 使わない
            elif stt in ('k', 'm'): pg.locator(f'#cbOv [data-cb={stt}skip]').click()
            elif stt == 'rev': pg.locator('#cbOv [data-cb=revyes]').first.click()
            elif stt == 'u5': pg.locator('#cbOv [data-cb=u5no]').first.click()      # 第4.183版
            elif stt == 'six': pg.locator('#cbOv [data-cb=sixno]').first.click()      # 第4.190版：ターンの はじめの 6 → 使わない
            elif stt == 'eff': pg.locator('#cbOv [data-cb=effno]').click()
            elif stt == 'swap': pg.locator('#cbOv .cbhand .cbc').first.click(); pg.wait_for_timeout(60); pg.locator('#cbOv .cbmod [data-cb=swap]').click()
            elif stt == 'set': pg.locator('#cbOv .cbhand .cbc').first.click(); pg.wait_for_timeout(60); pg.locator('#cbOv .cbmod [data-cb=set]').click()
            else: pg.wait_for_timeout(120)
        v = pg.evaluate(V)
        nt = v['early'] or 5; dw = abs(v['my']['wins'] - v['op']['wins'])      # 第4.202版：決着したら その ターンで おわる（early＝おわった ターン）
        check(done and first == [5, 7, 7, 16] and v['phase'] == 'end' and v['turns'] == 5 and v['res'] in ('win', 'lose', 'draw') and len([d for d in v['discard'] if d['why'] == 't']) == 2 * nt and len(v['discard']) >= 2 * nt
              and (v['early'] == 0 or (3 <= v['early'] <= 4 and dw > 5 - v['early'] and v['res'] != 'draw')),
              f'コンピュータと 最後まで 対戦できる（普通の 形：5ターン・手札 7枚 ずつ・山札 16 {first}。{v["res"]} {v["my"]["wins"]}－{v["op"]["wins"]}・{nt}ターンで おわり{"（決着）" if v["early"] else ""}・捨て札 {len(v["discard"])}枚）')
        pg.wait_for_function("() => { const g = document.querySelector('#cbOv .cbend .gift'); return g && g.textContent.length > 3; }", timeout=30000)
        pg.locator('#cbOv .cbend [data-cb=menu]').click(); pg.wait_for_timeout(120)

        print('■ 部屋：2つの 画面（ホスト・ゲスト）で 対戦')
        gp = ctx.new_page(); gerrs = []; gp.on('pageerror', lambda e: gerrs.append(str(e)))
        gp.goto(APP); gp.wait_for_timeout(1300); gate(gp); gp.wait_for_timeout(600); open_cb(gp)
        gp.evaluate("() => { CBNet._t.minSets = 2; }")      # 第4.211版：前から ある 部屋の 場面は「3ターン」の 形（2勝で 決着＝セット 2回）で 動かす。アプリの 中の 形（3回 セットして から）は さいごの「■ 抜け穴」で 見る
        pg.evaluate("() => { CBApp._opt = { hands: [['k', '1', '2', '6', '6'], ['m', '3', '4', '5', '7']], turns: 3 }; }")
        pg.evaluate("() => { CBApp._t.state.coin = 10; }"); gp.evaluate("() => { CBApp._t.state.coin = 2; }")      # 2つの 画面は 保存の 場所が 同じ → 数は 画面の 中で 決める（読み直さない）
        c0 = pg.evaluate("() => window.__room.calls.length")
        pg.locator('#cbOv .cbmenu [data-cb=host]').click(); pg.wait_for_timeout(300)
        STK = """() => { const r = document.querySelector('#cbOv .cbroom'), q = s => r.querySelector(s); if (!q('[data-cb=stkgo]')) return null;
          return { chips: [...r.querySelectorAll('[data-cb=stke]')].map(b => b.textContent + (b.classList.contains('on') ? '*' : '')).join(','), w: q('.cbstp b').textContent, minus: q('[data-cb=stkw][data-d="-1"]').disabled, plus: q('[data-cb=stkw][data-d="1"]').disabled,
            go: q('[data-cb=stkgo]').textContent, have: q('.cbcoinl').textContent, calls: window.__room.calls.length, h2: q('h2').textContent }; }"""
        k0 = pg.evaluate(STK)
        check(k0 and k0['h2'] == '部屋を 作る' and k0['chips'] == '0*,1,2,3,5,10' and k0['w'] == '0枚' and k0['minus'] and k0['plus'] and k0['go'] == 'コインなしで 部屋を 作る' and '持って いる バトルコイン 10枚' in k0['have'] and k0['calls'] == c0,
              f'バトルコインを 持って いる 人が「部屋を 作る」→ 先に 参加コインを 決める（選べるのは 持って いる 数 まで：{k0 and k0["chips"]}・まだ 部屋は 作らない）（第4.179版）')
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
        check(hr['scr'] == 'room' and re.fullmatch(r'[1-9][0-9]{3}', hr['num']) is not None and '友達を 待って いるよ' in hr['stt'] and 'この 番号を 友達に 教えてね' in hr['t'] and hr['calls'] == ['host:' + hr['num']],
              f'部屋を 作る：4桁の 部屋番号（{hr["num"]}）・「友達を 待って いるよ…」・アプリに「部屋を 作る」を お願い（{hr["calls"]}）')
        shot(pg, 'cb_room_host')
        gp.locator('#cbOv .cbmenu [data-cb=join]').click(); gp.wait_for_timeout(150)
        check(gp.locator('#cbOv .cbkeys button').count() == 12 and gp.locator('#cbOv .cbkeys [data-key=go]').is_disabled(), '部屋に 入る：数字の ボタン（4桁 入れる まで「入る」は 押せない）')
        for d in '00': gp.locator(f'#cbOv .cbkeys [data-key="{d}"]').click()
        gp.locator('#cbOv .cbkeys [data-key=del]').click()
        gp.locator('#cbOv .cbkeys [data-key=del]').click()
        for d in hr['num']: gp.locator(f'#cbOv .cbkeys [data-key="{d}"]').click()
        gp.locator('#cbOv .cbkeys [data-key="9"]').click()      # 5けた目は 入らない
        check(gp.locator('#cbOv .cbroom .num').inner_text().replace('\n', '') == hr['num'] and gp.locator('#cbOv .cbkeys [data-key=go]').is_enabled(), f'番号を 入れる（消す・4桁 まで）→「入る」が 押せる')
        shot(gp, 'cb_room_join')
        gp.locator('#cbOv .cbkeys [data-key=go]').click()
        pg.wait_for_function("() => CBApp._t.screen === 'game' && CBApp._t.view && CBApp._t.idle", timeout=30000); gp.wait_for_function("() => CBApp._t.screen === 'game' && CBApp._t.view && CBApp._t.idle", timeout=30000)
        hv, gv = pg.evaluate(V), gp.evaluate(V)
        check(pg.evaluate("() => CBApp._t.match.kind") == 'host' and gp.evaluate("() => CBApp._t.match.kind") == 'guest' and hv['me'] == 0 and gv['me'] == 1 and pg.evaluate(DOMHAND) == 'k1266' and gp.evaluate(DOMHAND) == 'm3457'
              and pg.locator('#cbOv .cbopp .cbwho b').inner_text() == '友達' and gp.locator('#cbOv .cbopp .cbwho b').inner_text() == '友達' and gp.evaluate("() => window.__room.calls[0]") == 'join:' + hr['num'] and set(gp.evaluate("() => window.__room.calls.slice(1)")) <= {'send'},
              f'つながった → 2人とも 対戦の 画面（ホストの 手札 {pg.evaluate(DOMHAND)}・ゲストの 手札 {gp.evaluate(DOMHAND)}・相手の 名前は「友達」）')
        sh = said(pg); sg = said(gp)
        check(pg.evaluate(V)['phase'] == 'six' and asked(pg)[0] == '6 の 効果を 使う？' and '友達が 6 の 効果を 使うか 選んで いるよ' in gp.evaluate(MSG) and acts(gp) == [] and asked(gp) is None
              and any(s.startswith('ban:6 の 効果') and 'セットの 前に 使うか 選んでね' in s for s in sh) and any(s.startswith('ban:6 の 効果') and '友達が 使うか 選ぶよ' in s for s in sg),
              '第4.190版：配った あと すぐ（ターンの 始め）：ホスト（6 が 2枚）に「6 の 効果を 使う？」・ゲストは 待つ（2人とも まだ セットできない）')
        pg.locator('#cbOv [data-cb=sixyes]').click(); pg.wait_for_timeout(80); pg.locator('#cbOv .cbmod .pick .cbc').last.click(); idle(pg); idle(gp)
        check(gp.locator('#cbOv .cbohand .cbc img[src="cb_s6.webp"]').count() == 2 and gp.locator('#cbOv .cbhand .cbc .eye').count() == 1 and len([c for c in pg.evaluate(V)['op']['hand'] if c['k']]) == 1
              and (lambda sg: any('友達が 6 の 効果で、' in s and 'を 見たよ' in s for s in sg) and any(s.startswith('use:友達が 使った！6 の 効果手札を 1枚 見る') for s in sg))(said(gp)) and pg.evaluate(V)['can']['set'] and gp.evaluate(V)['can']['set'],
              'ホストが 6 の 効果：ゲストの 画面に 効果の 札・「友達が 6 の 効果で、…を 見たよ」・ホストの 6 が 2枚 表・見られた カードに 目の 印 → 2人とも セットへ')
        play(gp, '3'); idle(pg)
        check(pg.evaluate(SLOT) == 'b -' and '友達は もう セットしたよ' in pg.evaluate(MSG) and gp.evaluate(SLOT) == '- b[3]:伏せて セット' and '友達が 選んで いるよ' in gp.evaluate(MSG), 'ゲストが セットした → ホストの 画面に 裏の カード・ゲストは 待つ')
        pg.evaluate("() => { window.__seen = []; const mo = new MutationObserver(() => { const m = document.querySelector('#cbOv .cbmod'); if (m.classList.contains('cbopen')) { const t = m.querySelector('.cbres'); window.__seen.push((m.querySelector('h3') || {}).textContent + '|' + (t ? t.textContent : '')); } }); mo.observe(document.querySelector('#cbOv .cbmod'), { childList: true, subtree: true, attributes: true }); }")
        gp.evaluate("() => { window.__seen = []; const mo = new MutationObserver(() => { const m = document.querySelector('#cbOv .cbmod'); if (m.classList.contains('cbopen')) { const t = m.querySelector('.cbres'); window.__seen.push((m.querySelector('h3') || {}).textContent + '|' + (t ? t.textContent : '')); } }); mo.observe(document.querySelector('#cbOv .cbmod'), { childList: true, subtree: true, attributes: true }); }")
        said(pg); said(gp)
        play(pg, 'k'); idle(gp); idle(pg)
        check(any('勝ち！' in s for s in pg.evaluate("() => window.__seen")) and any('負け…' in s for s in gp.evaluate("() => window.__seen")) and pg.evaluate(V)['turn'] == 2 and pg.evaluate(V)['phase'] == 'six' and asked(pg)[0] == '6 の 効果を 使う？'
              and '友達が 6 の 効果を 使うか 選んで いるよ' in gp.evaluate(MSG) and not any(s.startswith('ban:効果タイム') for s in said(pg)),
              'ホストも セットした → 効果タイムは ない（6 は ターンの 始め）→ 2人の 画面で オープン（ホスト「勝ち！」・ゲスト「負け…」）→ 2ターン目の はじめ：まず ホストの 6')
        pg.locator('#cbOv .cbask [data-cb=sixno]').click(); idle(pg); idle(gp)
        check(pg.evaluate(V)['pend']['mine'] and asked(pg)[0] == '神様馬の 効果を 使う？' and '友達が 神様馬の 効果を 使うか 選んで いるよ' in gp.evaluate(MSG) and any('友達は 6 の 効果を 使わなかったよ' in s for s in said(gp)),
              '6 を 使わない →（ゲストに「友達は 6 の 効果を 使わなかったよ」）→ 神様馬の 効果は ホストが 選ぶ・ゲストは 待つ')
        pg.locator('#cbOv [data-cb=kgo]').click(); pg.wait_for_timeout(80); pg.locator('#cbOv .cbmod .pick .cbc').first.click(); idle(pg); idle(gp)
        check(len([c for c in pg.evaluate(V)['op']['hand'] if c['k']]) >= 1 and gp.locator('#cbOv .cbhand .cbc .eye').count() >= 1 and pg.evaluate(V)['turn'] == 2 and gp.evaluate(V)['turn'] == 2 and pg.evaluate(V)['can']['set'] and gp.evaluate(V)['can']['set'], 'ホストが ゲストの 手札を 1枚 見た → ゲストの その カードに 目の 印・2人とも 2ターン目の セットへ')
        gp.locator('#cbOv [data-cb=discard]').click(); gp.wait_for_timeout(80)
        gd = gp.evaluate("() => [...document.querySelectorAll('#cbOv .cbmod .cbdl .row[data-dt]')].map(r => r.querySelector('b').textContent + '|' + [...r.querySelectorAll('.pr')].map(p => p.querySelector('span').textContent + '=' + [...p.querySelectorAll('img')].map(i => i.getAttribute('src').replace('cb_s', '').replace('.webp', '')).join('')).join('|'))")
        check(gd == ['ターン 1|あなた=3|友達=k'], f'ゲストの 捨て札の 窓：自分から 見た 形（{gd}）')
        gp.locator('#cbOv .cbmod [data-cb=modx]').click(); gp.wait_for_timeout(60)
        def step(q):
            idle(q)
            stt = q.evaluate("() => { const v = CBApp._t.view; return CBApp._t.ended ? 'end' : !v ? 'none' : v.pend && v.pend.mine ? v.pend.type : v.can.six ? 'six' : v.can.eff ? 'eff' : v.can.set ? ((v.can.x7r || v.can.x7 || v.can.x3) && CBApp._t.ask ? 'x7' : 'set') : 'wait'; }")
            if stt == 'x7': q.locator('#cbOv .cbask [data-cb=x7no], #cbOv .cbask [data-cb=p7no], #cbOv .cbask [data-cb=p3no]').first.click()      # 第4.187版・第4.202版
            elif stt in ('k', 'm'): q.locator(f'#cbOv [data-cb={stt}skip]').click()
            elif stt == 'rev': q.locator('#cbOv [data-cb=revno]').first.click()
            elif stt == 'u5': q.locator('#cbOv [data-cb=u5no]').first.click()      # 第4.183版
            elif stt == 'six': q.locator('#cbOv [data-cb=sixno]').first.click()      # 第4.190版
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
              f'最後まで：2人の 結果は うらおもて（ホスト {hv["res"]} {hv["my"]["wins"]}－{hv["op"]["wins"]}・ゲスト {gv["res"]}）')
        shot(pg, 'cb_room_end')
        gp.locator('#cbOv .cbend [data-cb=again]').click(); gp.wait_for_timeout(250)
        check(gp.locator('#cbOv .cbend [data-cb=again]').is_disabled() and '友達を 待って いるよ' in gp.locator('#cbOv .cbend .gift2').inner_text() and '友達が「もう 1回」を 押したよ' in pg.locator('#cbOv .cbend .gift2').inner_text(),
              'ゲストが「もう 1回」→ ゲストは 待つ・ホストに「友達が もう 1回 を 押したよ」')
        pg.locator('#cbOv .cbend [data-cb=again]').click()
        pg.wait_for_function("() => !CBApp._t.ended && CBApp._t.view && CBApp._t.view.turn === 1 && CBApp._t.idle", timeout=30000); gp.wait_for_function("() => !CBApp._t.ended && CBApp._t.view && CBApp._t.view.turn === 1 && CBApp._t.idle", timeout=30000)
        check(pg.evaluate(V)['phase'] == 'six' and gp.evaluate(V)['phase'] == 'six' and len(gp.evaluate(V)['my']['hand']) == 5 and asked(pg)[0] == '6 の 効果を 使う？', 'ホストも「もう 1回」→ 2人とも 新しい 対戦（第4.190版：同じ 手札 なので ホストは ターンの 始めに 6 を 聞かれる）')
        s0 = gp.evaluate("() => Object.assign({}, CBApp._t.state)"); h0 = pg.evaluate("() => Object.assign({}, CBApp._t.state)")
        gp.locator('#cbOv .cbtop [data-cb=quit]').click(); gp.locator('#cbOv .cbmod [data-cb=quitgo]').click()
        pg.wait_for_function("() => CBApp._t.modOn() && /部屋を 出たよ/.test(document.querySelector('#cbOv .cbmod').textContent)", timeout=20000)
        s1 = gp.evaluate("() => Object.assign({}, CBApp._t.state)"); h1 = pg.evaluate("() => Object.assign({}, CBApp._t.state)")
        check(gp.evaluate("() => CBApp._t.screen") == 'menu' and s1['lose'] == s0['lose'] + 1 and '友達が 部屋を 出たよ' in pg.locator('#cbOv .cbmod').inner_text() and '勝ち負けに 数えないよ' in pg.locator('#cbOv .cbmod').inner_text() and {k: x for k, x in h1.items() if k != 'ms'} == {k: x for k, x in h0.items() if k != 'ms'}
              and h0['ms']['live'] == 'fr' and h1['ms']['live'] == '' and h1['ms']['fr'] == h0['ms']['fr'] and s1['ms']['fr'] == 0 and s1['ms']['live'] == '',
              'ゲストが 途中で やめた → ゲストは 負け・ホストには「友達が 部屋を 出たよ（勝ち負けに 数えない）」')
        pg.locator('#cbOv .cbmod [data-cb=menu]').click(); pg.wait_for_timeout(150)
        check(pg.evaluate("() => CBApp._t.screen") == 'menu' and pg.evaluate("() => window.__room.calls[window.__room.calls.length - 1]") == 'stop', 'メニューへ（アプリの 部屋も 閉じる）')
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
        check('部屋を 探して いるよ' in pg.locator('#cbOv .cbroom .stt').inner_text() and pg.locator('#cbOv .cbkeys').count() == 0, 'ない 部屋番号：「部屋を 探して いるよ…」の まま（数字の ボタンは 出ない）')
        pg.locator('#cbOv .cbroom [data-cb=roomx]').click(); pg.wait_for_timeout(150)
        check(pg.evaluate("() => CBApp._t.screen") == 'menu' and pg.evaluate("() => window.__room.calls[window.__room.calls.length - 1]") == 'stop', '「← やめる」→ メニュー（探すのを やめる）')

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
              and pg.evaluate("() => CBApp._t.screen") == 'game' and hm == '友達が 参加するか 選んで いるよ…' and pg.evaluate("() => CBApp._t.view") is None,
              f'入る 人の バトルコインが 足りない（2枚）：「この 部屋の 決まり」・「あと 1枚 足りない ので、この 部屋には 入れないよ」（ボタンは メニューへ だけ）・作った 人は「友達が 参加するか 選んで いるよ…」（まだ 配らない）')
        shot(gp, 'cb_join_short')
        gp.locator('#cbOv .cbjoin [data-cb=joinno]').click(); gp.wait_for_timeout(200)
        pg.wait_for_function("() => CBApp._t.modOn() && /部屋を 出たよ/.test(document.querySelector('#cbOv .cbmod').textContent)", timeout=20000)
        check(gp.evaluate("() => CBApp._t.screen") == 'menu' and gp.evaluate(COINS) == [2, None] and pg.evaluate(COINS) == [10, None] and '勝ち負けに 数えないよ' not in pg.locator('#cbOv .cbmod').inner_text(),
              '入らずに メニューへ → 作った 人に「友達が 部屋を 出たよ」（2人とも コインは 変わらない）')
        pg.locator('#cbOv .cbmod [data-cb=menu]').click(); pg.wait_for_timeout(200)
        # 足りる：参加する → 2人とも 出す → 勝った 人が 6枚
        gp.evaluate("() => { CBApp._t.state.coin = 5; }")
        num = make_room(3); join_room(num)
        jm = gp.evaluate(JOINM)
        check(jm and 'あなたの バトルコイン 5枚' in jm['t'] and '足りない' not in jm['t'] and jm['btns'] == ['やめる', '参加する'] and '同点は 戻る・途中で やめると 戻らないよ' in jm['t'], f'足りる（5枚）：「やめる」「参加する」（{jm and jm["btns"]}）')
        shot(gp, 'cb_join_ask')
        gp.locator('#cbOv .cbjoin [data-cb=joinyes]').click()
        pg.wait_for_function("() => CBApp._t.screen === 'game' && CBApp._t.view && CBApp._t.idle", timeout=30000); gp.wait_for_function("() => CBApp._t.view && CBApp._t.idle", timeout=30000)
        tl = [q.locator('#cbOv .cbturn').inner_text().replace('\n', '') for q in (pg, gp)]
        check(pg.evaluate(COINS) == [7, '3/6'] and gp.evaluate(COINS) == [2, '3/6'] and all('勝者 6枚' in t for t in tl) and pg.evaluate(V)['turns'] == 3,
              f'「参加する」→ 配る → 2人とも 参加コイン 3枚を 出す（作った 人 10 → 7・入った 人 5 → 2）・ターンの 字の よこに「勝者 6枚」（{tl}）')
        shot(pg, 'cb_room_coin_game')
        pg.locator('#cbOv .cbtop [data-cb=quit]').click(); pg.wait_for_timeout(80)
        check('参加コイン 3枚も 戻らないよ' in pg.locator('#cbOv .cbmod').inner_text(), '「やめる」の 窓：参加コインも 戻らない ことを 出す')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        for mine, his in (('1', '2'), ('2', '3')):      # 第4.202版：2勝 0敗・のこり 1ターン → 2ターン目で 決着（部屋でも）
            idle(pg); idle(gp); play(pg, mine); idle(gp); play(gp, his); idle(pg); idle(gp)
        for q in (pg, gp): q.wait_for_function("() => { const g = document.querySelector('#cbOv .cbend .gift'); return CBApp._t.ended && g && g.textContent.length > 3; }", timeout=30000)
        check([q.evaluate("() => [CBApp._t.view.early, CBApp._t.view.turn, document.querySelector('#cbOv .cbend .sc').textContent.indexOf('2ターン目で 決着！') >= 0]") for q in (pg, gp)] == [[2, 2, True], [2, 2, True]],
              '部屋でも 決着したら 試合終了：2勝 0敗（のこり 1ターン）→ 2人の 画面とも 2ターン目で 決着（結果の 窓に「2ターン目で 決着！」）')
        eh = pg.evaluate("() => ({ g: document.querySelector('#cbOv .cbend .gift').textContent, again: document.querySelector('#cbOv .cbend [data-cb=again]').disabled })")
        eg = gp.evaluate("() => ({ g: document.querySelector('#cbOv .cbend .gift').textContent, g2: document.querySelector('#cbOv .cbend .gift2').textContent, again: document.querySelector('#cbOv .cbend [data-cb=again]').disabled, h: document.querySelector('#cbOv .cbend h3').textContent })")
        check(pg.evaluate(V)['res'] == 'win' and 'バトルコイン ＋6枚（今 13枚）' in eh['g'] and pg.evaluate(COINS) == [13, None] and not eh['again'],
              f'作った 人の 勝ち（2 － 0）：勝者の 獲得コイン 6枚（7 → 13枚）（{eh["g"]}）')
        check(eg['h'] == 'あなたの 負け…' and '参加コイン 3枚は 戻らないよ（今 2枚）' in eg['g'] and gp.evaluate(COINS) == [2, None] and eg['again'] and eg['g2'] == 'バトルコインが 足りない ので、もう 1回は できないよ' and gp.evaluate("() => { const g = document.querySelector('#cbOv .cbend .gift2'); return Math.round(g.getBoundingClientRect().height) <= 20; }"),
              f'入った 人の 負け：参加コインは 戻らない（今 2枚）・バトルコインが 足りない ので「もう 1回」は 押せない（{eg["g2"]}）')
        shot(gp, 'cb_room_coin_lose')
        gp.locator('#cbOv .cbend [data-cb=menu]').click(); gp.wait_for_timeout(200)
        pg.wait_for_function("() => CBApp._t.modOn() && /部屋を 出たよ/.test(document.querySelector('#cbOv .cbmod').textContent)", timeout=20000)
        check(pg.evaluate(COINS) == [13, None] and 'バトルコイン' not in pg.locator('#cbOv .cbmod').inner_text(), '終わった 後に 相手が 出ても、コインは 変わらない')
        pg.locator('#cbOv .cbmod [data-cb=menu]').click(); pg.wait_for_timeout(200)
        # とちゅうで やめた 人の 参加コインは もどらない・相手は 獲得コインを もらう
        gp.evaluate("() => { CBApp._t.state.coin = 4; }")
        num = make_room(1); join_room(num); gp.locator('#cbOv .cbjoin [data-cb=joinyes]').click()
        pg.wait_for_function("() => CBApp._t.view && CBApp._t.idle", timeout=30000); gp.wait_for_function("() => CBApp._t.view && CBApp._t.idle", timeout=30000)
        check(pg.evaluate(COINS) == [12, '1/2'] and gp.evaluate(COINS) == [3, '1/2'], '参加 1枚・勝者 2枚の 部屋：2人とも 1枚 出した（13 → 12・4 → 3）')
        lose0 = gp.evaluate("() => CBApp._t.state.lose")
        gp.locator('#cbOv .cbtop [data-cb=quit]').click(); gp.wait_for_timeout(80)
        check('参加コイン 1枚も 戻らないよ' in gp.locator('#cbOv .cbmod').inner_text(), '入った 人の「やめる」の 窓にも 出る')
        gp.locator('#cbOv .cbmod [data-cb=quitgo]').click(); gp.wait_for_timeout(200)
        pg.wait_for_function("() => CBApp._t.modOn() && /部屋を 出たよ/.test(document.querySelector('#cbOv .cbmod').textContent)", timeout=20000)
        mt = pg.locator('#cbOv .cbmod').inner_text()
        # 第4.211版：相手が「序盤」（自分が まだ 3回 セットして いない）で やめた ときは、参加コインが もどる だけ（獲得コインは もらえない）。やめた 人の 参加コインは 今まで どおり もどらない
        check(gp.evaluate(COINS) == [3, None] and gp.evaluate("() => CBApp._t.state.lose") == lose0 + 1 and pg.evaluate(COINS) == [13, None] and pg.evaluate("() => CBApp._t.mySets") == 0
              and '友達が 序盤で やめた ので、参加コイン 1枚は 戻ったよ' in mt and 'もらったよ' not in mt and '勝ち負けに 数えないよ' in mt,
              f'途中で やめた 人：参加コインは 戻らない（3枚の まま・負けに 数える）・配られた すぐ あとに やめられた 相手は 参加コインが 戻る だけ（12 → 13：獲得コインは もらえない）（{mt[:80]!r}）')
        pg.locator('#cbOv .cbmod [data-cb=menu]').click(); pg.wait_for_timeout(200)
        # 自分が 3回 セットした あと（勝ち負けが つく ところまで 進んだ 対戦）に 相手が やめた → 勝者の 獲得コインを もらう
        gp.evaluate("() => { CBApp._t.state.coin = 4; }")
        num = make_room(1); join_room(num); gp.locator('#cbOv .cbjoin [data-cb=joinyes]').click()
        pg.wait_for_function("() => CBApp._t.view && CBApp._t.idle", timeout=30000); gp.wait_for_function("() => CBApp._t.view && CBApp._t.idle", timeout=30000)
        ms0 = pg.evaluate("() => CBApp._t.mySets"); pg.evaluate("() => CBApp._t.setMySets(CBNet.MIN_SETS)")
        gp.locator('#cbOv .cbtop [data-cb=quit]').click(); gp.wait_for_timeout(80); gp.locator('#cbOv .cbmod [data-cb=quitgo]').click(); gp.wait_for_timeout(200)
        pg.wait_for_function("() => CBApp._t.modOn() && /部屋を 出たよ/.test(document.querySelector('#cbOv .cbmod').textContent)", timeout=20000)
        mt = pg.locator('#cbOv .cbmod').inner_text()
        check(ms0 == 0 and gp.evaluate(COINS) == [3, None] and pg.evaluate(COINS) == [14, None] and '友達が 途中で やめた ので、バトルコイン 2枚を もらったよ' in mt,
              f'自分が 3回 セットした あとに 相手が やめた → 勝者の 獲得コイン 2枚を もらう（13 → 12 → 14・配り直すと セットの 数は 0 から）（{mt[:80]!r}）')
        pg.locator('#cbOv .cbmod [data-cb=menu]').click(); pg.wait_for_timeout(200)
        # つながりが 切れた：2人とも 参加コインが もどる
        num = make_room(1); join_room(num); gp.locator('#cbOv .cbjoin [data-cb=joinyes]').click()
        pg.wait_for_function("() => CBApp._t.view && CBApp._t.idle", timeout=30000); gp.wait_for_function("() => CBApp._t.view && CBApp._t.idle", timeout=30000)
        mid = [pg.evaluate(COINS), gp.evaluate(COINS)]
        for q in (pg, gp): q.evaluate("() => window.__nativeEvent('room', { ev: 'state', state: 'idle' })")
        for q in (pg, gp): q.wait_for_function("() => CBApp._t.modOn() && /つながりが 切れたよ/.test(document.querySelector('#cbOv .cbmod').textContent)", timeout=20000)
        check(mid == [[13, '1/2'], [2, '1/2']] and pg.evaluate(COINS) == [14, None] and gp.evaluate(COINS) == [3, None] and all('参加コイン 1枚は 戻ったよ' in q.locator('#cbOv .cbmod').inner_text() for q in (pg, gp)),
              f'つながりが 切れた：2人とも 参加コインが 戻る（{mid} → 14・3）')
        for q in (pg, gp): q.locator('#cbOv .cbmod [data-cb=menu]').click(); q.wait_for_timeout(150)
        # 同点は もどる・負けは もどらない・勝ちは 獲得コイン（数える 所 だけ）／とちゅうで アプリが 閉じた ときの 参加コインは もどらない（つぎに 開いた とき 知らせる）
        r3 = pg.evaluate("""async () => { const T = CBApp._t, out = []; for (const res of ['draw', 'lose', 'win']) { const c0 = T.state.coin; T.state.stake = { e: 2, w: 4 }; const r = await T.settle(res); out.push([res, r.pot.add, T.state.coin - c0, T.state.stake]); } return out; }""")
        check(r3 == [['draw', 2, 2, None], ['lose', 0, 0, None], ['win', 4, 4, None]], f'参加 2・勝者 4：同点＝2枚 戻る・負け＝0・勝ち＝4枚（{r3}）')
        pg.evaluate("() => { const T = CBApp._t; T.state.stake = { e: 5, w: 10 }; T.save(); T.load(); }")
        c5 = pg.evaluate(COINS); pg.evaluate("() => CBApp._t.menu()"); pg.wait_for_timeout(200); tt = pg.evaluate(TOAST)
        check(c5[1] is None and '前の 対戦が 途中で 終わった ので、' in tt and '参加コイン 5枚は 戻らなかったよ' in tt, f'参加コインを 出した まま アプリが 閉じた → 次に 開いた とき「参加コイン 5枚は 戻らなかったよ」（{tt!r}）')
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
        check(d0['scr'] == 'dz' and d0['coin'] == 'バトルコイン 0枚' and d0['tab'] == ['カードパック*', '表', '裏', 'ボード'] and len(tw) == 4 and all(tw),
              f'メニューの「デザインカスタム」→ 初めは「カードパック」の タブ（タブは カードパック・表・裏・ボード：字は 4つとも おさまる）（{d0["tab"]}）')
        check(d0['box'] == ['1パック 112枚・5枚入り', 'ノーマル 4枚 ＋ くじの 1枚'] and d0['ask'] == '112枚で パックを 開ける!' and d0['need'] == 'あと 112枚 足りないよ（コンピュータに 勝つ・毎日の ログインボーナスで もらえるよ）'
              and not d0['un'] and not d0['hist'] and d0['art'] == ['cb_pack.webp:' + ('600' if HAVE else '0')],
              f'カードパック：パックの 絵（まさちゃんの 絵 cb_pack.webp）・「1パック 112枚・5枚入り」「ノーマル 4枚 ＋ くじの 1枚」・コインが 0枚 なので「112枚で パックを 開ける」は 押せない・あと 112枚（{d0["box"]}・{d0["ask"]}）')
        check(d0['h3'] == ['この パックで 出る カード36種・持って いる 0／36'] and d0['h4'] == ['ノーマル4枚は ここから・くじ 30%・持って いる 0／18', 'レア（1〜7）くじ 40%・持って いる 0／7', '神様馬・幻の馬の レアくじ 10%・持って いる 0／2', '超レア（1〜7）くじ 15.65%・持って いる 0／7', '神様馬・幻の馬の 超レアくじ 4.35%・持って いる 0／2']
              and [t.split(':')[1] for t in d0['tiles']] == PIDS and all(t.endswith(':パックで 出る!') for t in d0['tiles']) and all(t.split(':')[2] == 'cb_fc_' + t.split(':')[1] + '_s.webp' for t in d0['tiles']) and d0['chips'] == ['N'] * 18 + ['R'] * 9 + ['SR'] * 9,
              f'「この パックで 出る カード」36種：ノーマル 18（N）・レア 1〜7（R）・神様馬／幻の馬の レア（R）・超レア 1〜7（SR）・神様馬／幻の馬の 超レア（SR）・くじの 確率と 持って いる 数（{d0["h3"]}・{d0["h4"]}）')
        shot(pg, 'cb_pk_tab')
        pg.locator('#cbOv .cbdz [data-cb=pkodds]').click(); pg.wait_for_timeout(150)
        od = pg.evaluate("""() => { const m = document.querySelector('#cbOv .cbmod.cbodm'); if (!m) return null; const r = m.querySelector('.pkod').getBoundingClientRect();
          return { h: m.querySelector('h3').textContent, cap: m.querySelector('.pkod caption').textContent, rows: [...m.querySelectorAll('.pkod tr')].map(r => r.querySelector('th').textContent + '|' + r.querySelector('td').textContent), t: m.textContent.replace(/\\s+/g, ' '),
            btn: [...m.querySelectorAll('.cbb')].map(b => b.textContent.trim()), w: [Math.round(r.left), Math.round(r.right), innerWidth] }; }""")
        check(od and od['h'] == '出る 確率' and od['cap'] == 'くじの 1枚（0〜229 の 番号を 等しく 1つ）'
              and od['rows'] == ['ノーマル18種・番号 0〜68（69個）|30%1種 1.67%', 'レア（1〜7）7種・番号 69〜160（92個）|40%1種 5.71%', '神様馬・幻の馬の レア2種・番号 161〜183（23個）|10%1種 5%', '超レア（1〜7）7種・番号 184〜219（36個）|15.65%1種 2.24%', '神様馬・幻の馬の 超レア2種・番号 220〜229（10個）|4.35%1種 2.17%']
              and '1パック 5枚：ノーマル 4枚（18種から 同じ 確率・1種 5.56%。同じ カードが 重なる ことも あるよ）＋ くじの 1枚' in od['t'] and 'レア 全部 50%（2パックに 1枚）・超レア 全部 20%（5パックに 1枚）' in od['t']
              and '23パック 開けても 必ず 出る わけでは ないよ' in od['t'] and od['btn'] == ['閉じる'] and od['w'][0] >= 0 and od['w'][1] <= od['w'][2],
              f'「出る 確率」：くじの 番号の はんいと 確率（1種ごとも）・ノーマル 4枚の 確率・どれも 平均（{od and od["rows"]}）')
        shot(pg, 'cb_pk_odds')
        pg.locator('#cbOv .cbmod [data-cb=dzback]').click(); pg.wait_for_timeout(80)
        mp = pg.evaluate("""() => { const T = CBApp._t, P = CBApp.PACK, c = {}; for (let k = 0; k < P.lot; k++) { const g = T.pkGroup(k); c[g] = (c[g] || 0) + 1; }
          const pools = {}; ['n', 'r', 'gr', 'sr', 'gsr'].forEach(g => { pools[g] = T.pkPool(g).map(f => f.id); });
          return { c: c, lot: P.lot, size: P.size, cost: P.cost, pools: pools, n: CBApp.FACES.length, edge: [0, 68, 69, 160, 161, 183, 184, 219, 220, 229].map(k => T.pkGroup(k)) }; }""")
        c = mp['c']
        check(mp['lot'] == 230 and mp['size'] == 5 and mp['cost'] == 112 and c == {'n': 69, 'r': 92, 'gr': 23, 'sr': 36, 'gsr': 10} and mp['edge'] == ['n', 'n', 'r', 'r', 'gr', 'gr', 'sr', 'sr', 'gsr', 'gsr']
              and c['n'] * 10 == 3 * 230 and c['r'] * 10 == 4 * 230 and (c['r'] + c['gr']) * 2 == 230 and (c['sr'] + c['gsr']) * 5 == 230 and c['gr'] * 10 == 230 and c['gsr'] * 23 == 230,
              f'くじの 番号 0〜229：ノーマル 69こ（30%）・レア 92こ（40%）・神様馬／幻の馬の レア 23こ（10%＝10パックに 1枚）・超レア 36こ（≒15.65%）・神様馬／幻の馬の 超レア 10こ（1/23）→ レア 全部 1/2・超レア 全部 1/5（丸めて いない）（{c}）')
        check(mp['pools'] == {'n': NIDS, 'r': RIDS, 'gr': GRIDS, 'sr': SRIDS, 'gsr': GSRIDS} and mp['n'] == 36 and len(set(PIDS)) == 36,
              f'グループの カード：ノーマル 18・レア 7・神様馬／幻の馬の レア 2・超レア 7・神様馬／幻の馬の 超レア 2 ＝ 36種（{[len(v) for v in mp["pools"].values()]}）')
        un = pg.evaluate("""() => { const T = CBApp._t, N = 230, R = 230000, c = new Array(N).fill(0); let bad = 0; CBApp._randInt = null;
          for (let i = 0; i < R; i++) { const x = T.randInt(N); if (x >= 0 && x < N && x === Math.floor(x)) c[x]++; else bad++; }
          const e = R / N, chi = c.reduce((a, x) => a + (x - e) * (x - e) / e, 0), g = {}; c.forEach((x, k) => { const q = T.pkGroup(k); g[q] = (g[q] || 0) + x; });
          return { bad: bad, chi: Math.round(chi * 10) / 10, g: g }; }""")
        gq = {k: v / 230000 for k, v in un['g'].items()}
        check(un['bad'] == 0 and 130 < un['chi'] < 345 and abs(gq['n'] - .3) < .005 and abs(gq['r'] - .4) < .005 and abs(gq['gr'] - .1) < .003 and abs(gq['sr'] - 36 / 230) < .004 and abs(gq['gsr'] - 10 / 230) < .0025,
              f'くじの 番号は 等しく 出る（23万回：0〜229 の どれも ほぼ 1000回・カイ二乗 {un["chi"]}〈自由度 229〉・{"・".join(f"{k} {v * 100:.2f}%" for k, v in gq.items())}）')
        dd = pg.evaluate("""() => { const T = CBApp._t, R = 46000, c = {}, N = T.pkPool('n').map(f => f.id), P = {}; let bad = 0; CBApp._randInt = null; ['n', 'r', 'gr', 'sr', 'gsr'].forEach(g => { P[g] = T.pkPool(g).map(f => f.id); });
          for (let i = 0; i < R; i++) { const d = T.pkDraw(); if (d.cards.length !== 5 || d.g !== T.pkGroup(d.k) || d.cards.slice(0, 4).some(id => N.indexOf(id) < 0) || P[d.g].indexOf(d.cards[4]) < 0) bad++; d.cards.forEach(id => { c[id] = (c[id] || 0) + 1; }); }
          return { bad: bad, c: c }; }""")
        exp = {i: 46000 * 4.3 / 18 for i in NIDS}; exp.update({i: 46000 * .4 / 7 for i in RIDS}); exp.update({i: 46000 * .1 / 2 for i in GRIDS}); exp.update({i: 46000 * 36 / 230 / 7 for i in SRIDS}); exp.update({i: 46000 * 10 / 230 / 2 for i in GSRIDS})
        tol = lambda i: .05 if i in NIDS else .10 if i in RIDS + GRIDS else .15
        far = [f'{i} {dd["c"].get(i, 0)}／{exp[i]:.0f}' for i in PIDS if abs(dd['c'].get(i, 0) - exp[i]) > exp[i] * tol(i)]
        check(dd['bad'] == 0 and set(dd['c']) == set(PIDS) and not far, f'パックを 4万6千回：5枚（ノーマル 4枚 ＋ くじの グループの 1枚）・どの カードも 決めた 確率どおりに 出る（外れ {far}）')
        dr = pg.evaluate("""() => { const T = CBApp._t, run = seq => { const q = seq.slice(); CBApp._randInt = () => q.shift(); const d = T.pkDraw(); CBApp._randInt = null; return d.cards.join(',') + '|' + d.g + '|' + d.k + '|' + q.length; };
          return [run([0, 17, 5, 5, 0, 0]), run([1, 1, 1, 1, 68, 17]), run([2, 3, 4, 5, 69, 0]), run([0, 0, 0, 0, 160, 6]), run([0, 0, 0, 0, 161, 0]), run([0, 0, 0, 0, 183, 1]), run([0, 0, 0, 0, 184, 0]), run([0, 0, 0, 0, 219, 6]), run([0, 0, 0, 0, 220, 0]), run([0, 0, 0, 0, 229, 1])]; }""")
        check(dr == ['ka,7b,1b,1b,ka|n|0|0', 'kb,kb,kb,kb,7b|n|68|0', 'ma,mb,1a,1b,1r|r|69|0', 'ka,ka,ka,ka,7r|r|160|0', 'ka,ka,ka,ka,kr|gr|161|0', 'ka,ka,ka,ka,mr|gr|183|0', 'ka,ka,ka,ka,1sr|sr|184|0', 'ka,ka,ka,ka,7sr|sr|219|0', 'ka,ka,ka,ka,ksr|gsr|220|0', 'ka,ka,ka,ka,msr|gsr|229|0'],
              f'くじの さかい目：0・68＝ノーマル／69・160＝レア／161・183＝神様馬・幻の馬の レア／184・219＝超レア／220・229＝神様馬・幻の馬の 超レア・ノーマルは 同じ カードが 重なっても よい（{dr}）')
        # 開ける：たしかめる 窓 → うっかり 押し 防止 → すばやく 2回 → 1回 だけ（コイン・カード・記録を いっしょに）
        pg.evaluate("() => { const T = CBApp._t; T.state.coin = 300; T.save(); T.dz('p'); window.__q = [0, 0, 2, 17, 200, 2]; CBApp._randInt = n => (n === 1679616 ? 4242 : window.__q.shift()); }"); pg.wait_for_timeout(150)
        a1 = pg.evaluate(DZ)
        pg.locator('#cbOv .cbdz [data-cb=pkask]').click(); pg.wait_for_timeout(150); k1 = pg.evaluate(MZ)
        rq = pg.evaluate("() => document.querySelector('#cbOv .cbmod [data-cb=pkgo]').dataset.rq")
        ka = pg.evaluate("() => [...document.querySelectorAll('#cbOv .cbmod .pkart img')].map(i => i.getAttribute('src'))")
        check(a1['ask'] == '112枚で パックを 開ける' and not a1['need'] and k1 and k1['h'] == 'パックを 開ける？' and 'カードパック（5枚）を 1つ 開けるよ' in k1['t'] and '300枚→残り 188枚' in k1['t'] and k1['btns'] == ['やめる', '開ける'] and re.fullmatch(r'p[0-9a-z]+-39u', rq or '') and ka == ['cb_pack.webp'],
              f'300枚 ある：「112枚で パックを 開ける」→ 確かめる 窓（パックの 絵・300枚 → 残り 188枚・やめる／開ける・この 窓だけの 番号 {rq}）')
        shot(pg, 'cb_pk_ask')
        pg.evaluate("() => { CBApp._guard = 1e9; }"); pg.locator('#cbOv .cbmod [data-cb=pkgo]').click(); pg.wait_for_timeout(100)
        g0 = pg.evaluate("() => { const s = CBApp._t.state; return [s.coin, s.pkh.length, s.faces.length, CBApp._t.screen, CBApp._t.modOn(), document.querySelector('#cbOv .cbmod [data-cb=pkgo]').disabled]; }")
        check(g0 == [300, 0, 0, 'dz', True, False], f'窓が 出て すぐ（0.45秒）は「開ける」を 受けつけない（うっかり 押し 防止）（{g0}）')
        pg.evaluate("() => { CBApp._guard = 0; const b = document.querySelector('#cbOv .cbmod [data-cb=pkgo]'); b.click(); b.click(); }"); pg.wait_for_timeout(150)
        p1 = pg.evaluate(S1); v1 = pg.evaluate(PK)
        check(p1['scr'] == 'pk' and p1['coin'] == 188 and p1['lsc'] == 188 and p1['faces'] == ['ka', 'ma', '7b', '3sr'] and p1['lsf'] == p1['faces'] and p1['packs'] == 1 and p1['lsp'] == 1
              and p1['pkh'] == [[rq, 'sr', 200, 'ka,ka,ma,7b,3sr', '10111', False]] and p1['lsh'] == p1['pkh'] and p1['q'] == 0,
              f'「開ける」を すばやく 2回：1回 だけ 開ける ＝ コイン 112枚（300 → 188）・5枚（朱の鳥居が 2枚：2枚目は 数えない → 持って いる カード 4種）・パックの 記録を 一緒に 保存（{p1["pkh"]}）')
        check(v1['st'] == 'pack' and v1['msg'] == 'タップで パックを 開けよう' and v1['ft'] == ['パックを開ける'] and v1['art'] == ['bd:cb_pack.webp', 'tp:cb_pack.webp'] and not v1['out'] and v1['g'] == ['n', 'n', 'n', 'n', 'sr'] and v1['hd'] == 'カードパック',
              f'パックの 画面：パックが 出る（タップで 開ける：上の ギザギザが 切れて とぶ 2枚 かさね）（{v1["msg"]}）')
        shot(pg, 'cb_pk_pack')
        pg.evaluate("rq => { const b = document.createElement('button'); b.dataset.cb = 'pkgo'; b.dataset.rq = rq; document.querySelector('#cbOv').appendChild(b); b.click(); b.remove(); }", rq); pg.wait_for_timeout(150)
        p2 = pg.evaluate(S1); v2 = pg.evaluate(PK)
        check(p2 == p1 and v2['st'] == 'pack' and v2['scr'] == 'pk', f'同じ 番号の「開ける」が もう 1回 来ても 開けない（記録の 同じ 結果を 見せる・コインも 記録も そのまま）（{p2["coin"]}枚・{len(p2["pkh"])}個）')
        pg.evaluate("() => { const b = document.createElement('button'); b.dataset.cb = 'pkgo'; b.dataset.rq = 'pzzz-1'; document.querySelector('#cbOv').appendChild(b); b.click(); b.remove(); }"); pg.wait_for_timeout(100)
        check(pg.evaluate(S1) == p1, '窓の 番号と 違う「開ける」は 何も しない')
        # 開ける ところを 見ずに アプリを 閉じた → つぎに 開いた とき：メニューで 知らせる・タブの 上に「見る」→ 同じ 結果を 開ける ところから
        said(pg); pg.evaluate("() => { const T = CBApp._t; T.load(); T.menu(); }"); pg.wait_for_timeout(250); s3 = said(pg)
        check(any('🎴 開けた パックの 結果は\n「デザインカスタム」→「カードパック」で 見られるよ' in x for x in s3) and pg.evaluate("() => CBApp._t.state.pkh.length") == 1,
              f'開ける ところを 見おわる 前に 閉じた パック：次に 開いた ときの メニューで「開けた パックの 結果は …「カードパック」で 見られるよ」（{s3}）')
        pg.locator('#cbOv .cbmenu [data-cb=dz]').click(); pg.wait_for_timeout(200); a2 = pg.evaluate(DZ)
        check(a2['tab'][0] == 'カードパック*' and a2['coin'] == 'バトルコイン 188枚' and a2['un'] == '🎴 まだ 見おわって いない パックが 1つ あるよ' and a2['hist'] == [f'{rq}:ka,ka,ma,7b,3sr:SR!']
              and a2['h3'] == ['この パックで 出る カード36種・持って いる 4／36', 'パックの 記録開けた パック 1つ・最後の 1つ'] and a2['h4'][0].endswith('持って いる 3／18') and a2['h4'][3].endswith('持って いる 1／7')
              and 'k:ka:cb_fc_ka_s.webp:持って いる' in a2['tiles'] and '3:3sr:cb_fc_3sr_s.webp:持って いる' in a2['tiles'],
              f'カードパックの タブ：「まだ 見おわって いない パックが 1つ」＋「見る」・パックの 記録・出た カードは「持って いる」（{a2["hist"]}）')
        shot(pg, 'cb_pk_unseen')
        pg.locator('#cbOv .cbdz .pkun [data-cb=pkhis]').click(); pg.wait_for_timeout(150); v3 = pg.evaluate(PK)
        check(v3['st'] == 'pack' and v3['art'] and [c.split(':')[0] for c in v3['cards']] == ['ka', 'ka', 'ma', '7b', '3sr'] and pg.evaluate(S1)['coin'] == 188, '「見る」→ 同じ パックを 開ける ところから（コインは もう 減らない）')
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
              f'パックを タップ → 上が 切れる → カードが 1枚ずつ 出て パックの うしろに 並ぶ（パックが 前：z-index {zi}）→ 5枚 ならんでから パックが 消える → それから めくる（{seq}）')
        pg.wait_for_timeout(100); v4 = pg.evaluate(PK)
        gl = pg.evaluate("() => [...document.querySelectorAll('#cbOv .cbpk .pkc')].map(c => getComputedStyle(c.querySelector('.gl')).animationName)")
        check(v4['st'] == 'out' and v4['out'] and v4['msg'] == '最後の 1枚（くじ）… タップで めくろう！' and v4['ft'] == ['最後の1枚をめくる'] and [c.endswith('^') for c in v4['cards']] == [True] * 4 + [False] and gl == ['none'] * 4 + ['pkgl'],
              f'パックを タップ → 5枚が 出て 伏せて 並ぶ → ノーマル 4枚を めくる → 最後の 1枚（くじ）は 伏せた まま（超レアの くじ：裏の まわりが ゆっくり 光る）（{v4["cards"]}）')
        shot(pg, 'cb_pk_ready')
        pg.locator('#cbOv .cbpk .pkc[data-i="4"]').click()
        pg.wait_for_function("() => CBApp._t.pk && CBApp._t.pk.st === 'done'", timeout=10000); pg.wait_for_timeout(150); v5 = pg.evaluate(PK); s5 = pg.evaluate(S1)
        check(v5['msg'] == '🌟 超レア！『碧玉の温室』\nNEW 4枚！（持って いる カード 4／36）' and v5['cards'] == ['ka:N:NEW^', 'ka:N:持って いる^', 'ma:N:NEW^', '7b:N:NEW^', '3sr:SR:NEW^*'] and v5['ft'] == ['閉じる', 'もう1パック112枚'] and not v5['need']
              and s5['pkh'][0][5] is True and s5['lsh'][0][5] is True and s5['coin'] == 188,
              f'最後の 1枚を タップ → めくる（超レア：光の すじ・光が ひろがる）→「🌟 超レア！『碧玉の温室』」・NEW 4枚・2枚目の 朱の鳥居は「持って いる」・見おわった ことを 記録（{v5["msg"]!r}・{v5["cards"]}）')
        shot(pg, 'cb_pk_done')
        pg.locator('#cbOv .cbpk .pkc[data-i="4"]').click(); pg.wait_for_timeout(150); z7 = pg.evaluate(MZ)
        said(pg); pg.locator('#cbOv .cbmod [data-cb=dzuse]').click(); pg.wait_for_timeout(150); s7 = said(pg)
        f7 = pg.evaluate("() => [CBApp._t.screen, CBApp._t.state.face, JSON.parse(localStorage.getItem('tengel.cb')).face, CBApp._t.modOn()]")
        check(z7 and z7['h'] == '碧玉の温室3 の カードの 表・超レア' and z7['img'] == 'cb_fc_3sr_c.webp' and z7['btns'] == ['この デザインを 使う', '戻る'] and f7 == ['pk', {'3': '3sr'}, {'3': '3sr'}, False] and any('3 の カードの 表を『碧玉の温室』に したよ' in x for x in s7),
              f'出た カードを タップ → 大きい 絵・「この デザインを 使う」→ すぐ 使える（パックの 画面の まま）（{f7}）')
        pg.evaluate("() => { window.__q = [5, 5, 5, 5, 229, 1]; }")
        pg.locator('#cbOv .cbpk [data-cb=pkmore]').click(); pg.wait_for_timeout(150); k8 = pg.evaluate(MZ)
        pg.locator('#cbOv .cbmod [data-cb=pkgo]').click(); pg.wait_for_timeout(150)
        pg.locator('#cbOv .cbpk .pkft [data-cb=pkrip]').click(); pg.wait_for_function("() => CBApp._t.pk && CBApp._t.pk.ready", timeout=10000)
        gl8 = pg.evaluate("() => getComputedStyle(document.querySelector('#cbOv .cbpk .pkc[data-i=\"4\"] .gl')).animationName")
        pg.locator('#cbOv .cbpk [data-cb=pklast]').click(); pg.wait_for_function("() => CBApp._t.pk && CBApp._t.pk.st === 'done'", timeout=10000); pg.wait_for_timeout(150)
        v8 = pg.evaluate(PK); s8 = pg.evaluate(S1); rq2 = s8['pkh'][-1][0]
        check('188枚→残り 76枚' in k8['t'] and s8['coin'] == 76 and s8['lsc'] == 76 and s8['faces'] == ['ka', 'ma', '7b', '3sr', '1b', 'msr'] and s8['packs'] == 2 and len(s8['pkh']) == 2 and s8['pkh'][1][1:] == ['gsr', 229, '1b,1b,1b,1b,msr', '10001', True] and rq2 != rq
              and v8['msg'] == '🌟 幻の馬の 超レア！『紫電の魔城』\nNEW 2枚！（持って いる カード 6／36）' and v8['ft'] == ['閉じる', 'もう1パック112枚!'] and v8['need'] == 'あと 36枚 足りないよ（コンピュータに 勝つ・毎日の ログインボーナスで もらえるよ）' and gl8 == 'pkgl' and v8['g'][4] == 'gsr',
              f'「もう 1パック」（188 → 76枚）・下の「パックを 開ける」「最後の 1枚を めくる」でも 開けられる：幻の馬の 超レア『紫電の魔城』・同じ ノーマルが 4枚（数は 1）・残り 76枚 なので「もう 1パック」は 押せない（あと 36枚）（{v8["msg"]!r}）')
        shot(pg, 'cb_pk_gsr')
        pg.locator('#cbOv .cbpk [data-cb=pkx]').click(); pg.wait_for_timeout(200); a9 = pg.evaluate(DZ)
        check(a9['scr'] == 'dz' and a9['tab'][0] == 'カードパック*' and not a9['un'] and a9['hist'] == [f'{rq2}:1b,1b,1b,1b,msr:SR', f'{rq}:ka,ka,ma,7b,3sr:SR'] and a9['h3'][1] == 'パックの 記録開けた パック 2つ・最後の 2つ' and a9['ask'] == '112枚で パックを 開ける!' and 'あと 36枚' in a9['need'],
              f'「閉じる」→ カードパックの タブ：パックの 記録（新しい 順）・見おわって いない パックは ない（{a9["hist"]}）')
        pg.locator(f'#cbOv .cbdz .pkhi[data-id="{rq}"]').click(); pg.wait_for_timeout(200); v9 = pg.evaluate(PK)
        check(v9['st'] == 'done' and not v9['art'] and v9['out'] and v9['cards'] == ['ka:N:NEW^', 'ka:N:持って いる^', 'ma:N:NEW^', '7b:N:NEW^', '3sr:SR:NEW^'] and re.fullmatch(r'カードパック\d+/\d+ \d+:\d\d に 開けた パック', v9['hd']) and v9['msg'].startswith('🌟 超レア！『碧玉の温室』\nNEW 4枚！'),
              f'記録を タップ → その パックを もう 1回（5枚 全部 表・開けた 日時）（{v9["hd"]}）')
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
            check({k: v for k, v in rr.items() if k != 'q'} == {k: v for k, v in r0.items() if k != 'q'} and rr['q'] == 0 and any('保存が できなかったので、パックは 開けなかったよ\n（コインは 減って いないよ）' in x for x in tt) and not pg.evaluate("() => CBApp._t.modOn()"),
                  f'保存が できない とき（{"書けない" if how == "throw" else "書いた 中身が 残らない"}）：パックは 開けない・コイン・カード・記録は 全部 元の まま（{rr["coin"]}枚・{len(rr["pkh"])}個）')
            pg.evaluate("() => { window.__q = [0, 0, 0, 0, 100, 0]; }"); pg.wait_for_timeout(900)      # ふきだしが 消えて から（同じ ことばの ふきだしを 2回目も 数える）
        # 「おもて」の タブ：パックで 集めた カードを 使う（コインでは 解放しない）
        pg.evaluate("() => { const T = CBApp._t; T.state.coin = 0; T.save(); }")
        pg.locator('#cbOv .cbdz [data-cb=dztab][data-t=f]').click(); pg.wait_for_timeout(150); f0 = pg.evaluate(DZ)
        check(f0['tab'] == ['カードパック', '表*', '裏', 'ボード'] and f0['h4'] == ['神様馬持って いる 1／4', '幻の馬持って いる 2／4', '1 の カード持って いる 1／4', '2 の カード持って いる 0／4', '3 の カード持って いる 1／4', '4 の カード持って いる 0／4', '5 の カード持って いる 0／4', '6 の カード持って いる 0／4', '7 の カード持って いる 1／4']
              and len(f0['tiles']) == 45 and f0['tiles'][:5] == ['k:base:cb_sk.webp:使って いる*', 'k:ka:cb_fc_ka_s.webp:持って いる', 'k:kb:cb_fc_kb_s.webp:パックで 出る!', 'k:kr:cb_fc_kr_s.webp:パックで 出る!', 'k:ksr:cb_fc_ksr_s.webp:パックで 出る!'] and f0['chips'][:5] == ['', 'N', 'N', 'R', 'SR']
              and 'm:msr:cb_fc_msr_s.webp:持って いる' in f0['tiles'] and '3:3sr:cb_fc_3sr_s.webp:使って いる*' in f0['tiles'] and '3:base:cb_s3.webp:持って いる' in f0['tiles'],
              f'「表」の タブ：9種類 ×（いつもの ＋ ノーマル 2・レア 1・超レア 1）＝ 45・N／R／SR の 印・持って いない ものは「パックで 出る」（{f0["h4"]}）')
        shot(pg, 'cb_dz_faces')
        pg.locator('#cbOv .cbdz .dzt[data-id="ksr"]').click(); pg.wait_for_timeout(150); z8 = pg.evaluate(MZ)
        check(z8 and z8['h'] == '白金の聖殿神様馬の 表・超レア' and z8['img'] == 'cb_fc_ksr_c.webp' and z8['btns'] == ['カードパックへ', '戻る'] and z8['need'] == 'カードパックで 出るよ（神様馬・幻の馬の 超レア）',
              f'持って いない 表を タップ：大きい 絵・「カードパックで 出るよ（神様馬・幻の馬の 超レア）」・「カードパックへ」（コインで 解放は ない）（{z8 and z8["btns"]}）')
        pg.locator('#cbOv .cbmod [data-cb=dztab][data-t=p]').click(); pg.wait_for_timeout(150)
        check(pg.evaluate(DZ)['tab'][0] == 'カードパック*' and not pg.evaluate("() => CBApp._t.modOn()"), '「カードパックへ」→ カードパックの タブ')
        pg.locator('#cbOv .cbdz .dzt[data-id="kr"]').click(); pg.wait_for_timeout(120); z9 = pg.evaluate(MZ); pg.locator('#cbOv .cbmod [data-cb=dzback]').click(); pg.wait_for_timeout(80)
        check(z9 and z9['h'] == '聖光の神馬神様馬の 表・レア' and z9['btns'] == ['戻る'] and z9['need'] == 'カードパックで 出るよ（神様馬・幻の馬の レア）', f'カードパックの タブで 持って いない カードを タップ：大きい 絵と どの くじで 出るか（{z9 and z9["need"]}）')
        pg.evaluate("() => { const T = CBApp._t; T.state.coin = 999; T.save(); }")
        bad = pg.evaluate("""() => { const o = document.querySelector('#cbOv'), r = []; for (const [cb, ck, id] of [['dzopen', 'k', 'kb'], ['dzgo', 'k', 'kb'], ['dzopen', '7', '7sr'], ['dzgo', '7', '7sr']]) {
          const b = document.createElement('button'); b.dataset.cb = cb; b.dataset.ck = ck; b.dataset.id = id; o.appendChild(b); b.click(); b.remove(); r.push(CBApp._t.modOn()); } const s = CBApp._t.state; return [r, s.coin, s.faces.slice()]; }""")
        check(bad == [[False, False, False, False], 999, ['ka', 'ma', '7b', '3sr', '1b', 'msr']], f'表は コインでは 解放できない（前の 版の「解放」の ボタンが 来ても 何も しない）（{bad}）')
        # 「うら」の タブ（いままで どおり コインで 解放）
        pg.evaluate("() => { const T = CBApp._t; T.state.coin = 300; T.save(); }")
        pg.locator('#cbOv .cbdz [data-cb=dztab][data-t=b]').click(); pg.wait_for_timeout(150); d2 = pg.evaluate(DZ)
        check(d2['tab'] == ['カードパック', '表', '裏*', 'ボード'] and d2['h4'] == ['カードの 裏1つ 300枚'] and len(d2['tiles']) == 8 and d2['tiles'][0] == '-:base:cb_sb.webp:使って いる*' and all(t.endswith('300枚!') for t in d2['tiles'][1:])
              and [t.split(':')[1] for t in d2['tiles'][1:]] == ['sky', 'star', 'ice', 'wa', 'ori', 'crown', 'heart'] and d2['chips'] == [''] * 8,
              f'「裏」：いつもの ＋ 7種（1つ 300枚：今まで どおり コインで 解放）（{[t.split(":")[1] for t in d2["tiles"]]}）')
        shot(pg, 'cb_dz_backs')
        pg.locator('#cbOv .cbdz .dzt[data-id="sky"]').click(); pg.wait_for_timeout(120); pg.locator('#cbOv .cbmod [data-cb=dzopen]').click(); pg.wait_for_timeout(120); z3 = pg.evaluate(MZ)
        pg.evaluate("() => { CBApp._guard = 1e9; }"); pg.locator('#cbOv .cbmod [data-cb=dzgo]').click(); pg.wait_for_timeout(100); g1 = pg.evaluate("() => [CBApp._t.state.coin, CBApp._t.state.backs.slice()]")
        said(pg); pg.evaluate("() => { CBApp._guard = 0; }"); pg.locator('#cbOv .cbmod [data-cb=dzgo]').click(); pg.wait_for_timeout(200)
        d3 = pg.evaluate(DZ); tt = said(pg)
        pg.locator('#cbOv .cbdz .dzt[data-id="star"]').click(); pg.wait_for_timeout(120); z4 = pg.evaluate(MZ); pg.locator('#cbOv .cbmod [data-cb=dzback]').click(); pg.wait_for_timeout(80)
        check(z3['h'] == '解放する？' and '『天馬の光』（カードの 裏）を 解放するよ' in z3['t'] and '300枚→残り 0枚' in z3['t'] and z3['btns'] == ['やめる', '解放する'] and g1 == [300, []]
              and d3['coin'] == 'バトルコイン 0枚' and d3['tiles'][1] == '-:sky:cb_bk_sky_s.webp:使って いる*' and d3['tiles'][0] == '-:base:cb_sb.webp:持って いる' and any('『天馬の光』を 解放したよ！' in x for x in tt)
              and z4['btns'] == ['バトルコイン 300枚で 解放!', '戻る'] and 'あと 300枚 足りないよ' in z4['need'] and pg.evaluate("() => [CBApp._t.state.backs, CBApp._t.state.back]") == [['sky'], 'sky'],
              f'うら『天馬の光』：確かめる 窓（窓が 出て すぐは 受けつけない）→ 300枚で 解放（300 → 0）・すぐ その 裏に・他は あと 300枚（{d3["coin"]}）')
        pg.locator('#cbOv .cbdz [data-cb=dztab][data-t=f]').click(); pg.wait_for_timeout(120)
        pg.locator('#cbOv .cbdz .dzt[data-id="ka"]').click(); pg.wait_for_timeout(120); z10 = pg.evaluate(MZ); pg.locator('#cbOv .cbmod [data-cb=dzuse]').click(); pg.wait_for_timeout(150)
        check(z10['btns'] == ['この デザインを 使う', '戻る'] and pg.evaluate("() => CBApp._t.state.face") == {'k': 'ka', '3': '3sr'}, 'パックで 出た『朱の鳥居』を「この デザインを 使う」（コインは 使わない）')
        pg.locator('#cbOv .cbdz [data-cb=dzx]').click(); pg.wait_for_timeout(150)
        check(pg.evaluate("() => CBApp._t.screen") == 'menu' and 'バトルコイン 0枚' in pg.evaluate("() => document.querySelector('#cbOv .cbmenu .cbcoinl').textContent"), '「← 戻る」→ メニュー（コインの 数も 0枚）')
        start(pg, 'k1234', '15677')
        IM = """() => ({ deck: document.querySelector('#cbOv .cbdeck img').getAttribute('src'), op: [...document.querySelectorAll('#cbOv .cbohand img')].map(i => i.getAttribute('src')), my: [...document.querySelectorAll('#cbOv .cbhand .cbc')].map(c => c.dataset.ck + '=' + c.querySelector('img').getAttribute('src')) })"""
        im = pg.evaluate(IM)
        check(im['deck'] == 'cb_bk_sky_d.webp' and set(im['op']) == {'cb_bk_sky_s.webp'} and 'k=cb_fc_ka_s.webp' in im['my'] and '3=cb_fc_3sr_s.webp' in im['my'] and '1=cb_s1.webp' in im['my'] and not any('cb_sk.webp' in x for x in im['my']),
              f'対戦：山札と 相手の 手札は 選んだ うら『天馬の光』・神様馬は パックの『朱の鳥居』・3 は 超レアの『碧玉の温室』・他は いつもの（{im["deck"]}・{im["my"]}）')
        shot(pg, 'cb_dz_game')
        pg.evaluate("() => { window.__seen = []; }")
        pg.locator('#cbOv .cbhand .cbc[data-ck="k"]').click(); pg.wait_for_timeout(80); pg.locator('#cbOv .cbmod [data-cb=set]').click(); idle(pg)
        opp(pg, {'t': 'set', 'k': 1})
        seen = pg.evaluate("() => window.__seen")
        check(any('勝ち！' in x and 'cb_fc_ka_c.webp,cb_c1.webp' in x for x in seen) and pg.evaluate(V)['my']['wins'] == 1, f'めくった とき：神様馬は 選んだ 表の 大きい 絵（{seen[-1] if seen else None}）')
        pg.evaluate("() => CBApp._t.menu()"); pg.wait_for_timeout(150)
        pg.locator('#cbOv .cbmenu [data-cb=dz]').click(); pg.wait_for_timeout(150); pg.locator('#cbOv .cbdz [data-cb=dztab][data-t=f]').click(); pg.wait_for_timeout(150)
        pg.locator('#cbOv .cbdz .dzt[data-ck="k"][data-id=""]').click(); pg.wait_for_timeout(120); z5 = pg.evaluate(MZ)
        pg.locator('#cbOv .cbmod [data-cb=dzuse]').click(); pg.wait_for_timeout(150)
        st2 = pg.evaluate("() => [CBApp._t.state.coin, CBApp._t.state.face, CBApp._t.state.faces.length, JSON.parse(localStorage.getItem('tengel.cb')).face]")
        check(z5['btns'] == ['この デザインを 使う', '戻る'] and st2 == [0, {'3': '3sr'}, 6, {'3': '3sr'}] and pg.evaluate(DZ)['tiles'][0] == 'k:base:cb_sk.webp:使って いる*', f'いつもの に 戻す：コインは 使わない・集めた カードは 残る（{st2}）')
        pg.evaluate("() => { const s = JSON.parse(localStorage.getItem('tengel.cb')); s.faces = ['zz', 'ka', 'ka']; s.face = { k: 'kb', '1': 'ka', m: 'ma' }; s.backs = ['sky', 'nope']; s.back = 'ice'; localStorage.setItem('tengel.cb', JSON.stringify(s)); CBApp._t.load(); }")
        st3 = pg.evaluate("() => { const s = CBApp._t.state; return [s.faces, s.face, s.backs, s.back]; }")
        check(st3 == [['ka'], {}, ['sky'], ''], f'覚えた 中身が おかしい ときは 直す（ない 名前・持って いない もの・違う 種類は 捨てる）（{st3}）')
        pg.evaluate("""() => { const s = JSON.parse(localStorage.getItem('tengel.cb')), ok = { id: 'pok', t: 5, g: 'r', k: 100, cards: ['ka', 'kb', 'ma', 'mb', '3r'], v: 1 };
          s.pkh = [null, 5, { id: 'p1', g: 'r', cards: ['ka', 'kb', 'ma', 'mb'] }, { id: 'p2', g: 'r', cards: ['ka', 'kb', 'ma', 'mb', 'zz'] }, { id: 'p3', g: 'x', cards: ['ka', 'kb', 'ma', 'mb', '3r'] }, { id: 7, g: 'r', cards: ['ka', 'kb', 'ma', 'mb', '3r'] }, ok]; s.packs = 'abc';
          localStorage.setItem('tengel.cb', JSON.stringify(s)); CBApp._t.load(); }""")
        ph = pg.evaluate("() => [CBApp._t.state.pkh, CBApp._t.state.packs]")
        check(ph == [[{'id': 'pok', 't': 5, 'g': 'r', 'k': 100, 'cards': ['ka', 'kb', 'ma', 'mb', '3r'], 'nw': [False] * 5, 'v': True}], 1],
              f'パックの 記録が おかしい ときは 直す（5枚 ない・ない カード・ない グループ・番号が 文字で ない ものは 捨てる・開けた 数は 記録の 数より 少なく しない）（{ph}）')
        pg.evaluate("""() => { const s = JSON.parse(localStorage.getItem('tengel.cb')); s.pkh = []; for (let i = 0; i < 105; i++) s.pkh.push({ id: 'p' + i, t: i, g: 'n', k: 0, cards: ['ka', 'ka', 'ka', 'ka', 'ka'], nw: [false, false, false, false, false], v: true });
          s.packs = 105; s.coin = 112; localStorage.setItem('tengel.cb', JSON.stringify(s)); CBApp._t.load(); CBApp._t.dz('p'); window.__q = [1, 1, 1, 1, 0, 0]; }"""); pg.wait_for_timeout(150)
        pm = pg.evaluate("() => [CBApp._t.state.pkh.length, CBApp._t.state.pkh[0].id, CBApp._t.state.pkh[99].id, CBApp._t.state.packs]")
        pg.locator('#cbOv .cbdz [data-cb=pkask]').click(); pg.wait_for_timeout(120); pg.locator('#cbOv .cbmod [data-cb=pkgo]').click(); pg.wait_for_timeout(150)
        p100 = pg.evaluate(S1)
        check(pm == [100, 'p5', 'p104', 105] and len(p100['pkh']) == 100 and p100['pkh'][0][0] == 'p6' and p100['pkh'][-1][1:4] == ['n', 0, 'kb,kb,kb,kb,ka'] and p100['packs'] == 106 and p100['coin'] == 0 and p100['lsh'] == p100['pkh'],
              f'パックの 記録は 最後の 100個 まで（開けた 数は そのまま 105 → 106・残りの コインが ちょうど 112枚でも 開けられる）（{pm}・{len(p100["pkh"])}個）')
        pg.evaluate("() => CBApp._t.menu()"); pg.wait_for_timeout(150)
        pg.evaluate("() => { const s = JSON.parse(localStorage.getItem('tengel.cb')); delete s.pkh; delete s.packs; s.faces = ['ka', '6a', 'mb']; s.face = { k: 'ka', '6': '6a' }; localStorage.setItem('tengel.cb', JSON.stringify(s)); CBApp._t.load(); }")
        mg = pg.evaluate("() => { const s = CBApp._t.state; return [s.faces, s.face, s.pkh, s.packs]; }")
        check(mg == [['ka', '6a', 'mb'], {'k': 'ka', '6': '6a'}, [], 0], f'前の 版で コインで 解放した 表は そのまま 持って いる（使って いる ものも そのまま・パックの 記録は 空から）（{mg}）')
        pg.evaluate("() => { CBApp._randInt = null; const T = CBApp._t; T.state.backs = []; T.state.faces = []; T.state.back = ''; T.state.face = {}; T.state.pkh = []; T.state.packs = 0; T.save(); T.menu(); }")

        print('■ プレイボード（第4.185版・まさちゃん 23:20「バトルコインで、プレイボード7種類購入できるようにして！ 1個バトルコイン300枚で解放できるようにして！」）')
        BIMG = "() => { const b = document.querySelector('#cbOv .cbboard'), f = getComputedStyle(b.querySelector('.cbfire')), i = b.querySelector(':scope > img'); return [i.getAttribute('src'), b.classList.contains('cust'), f.display, f.animationName, i.complete && i.naturalWidth, b.classList.contains('dl')]; }"
        start(pg, '12345', '12345'); b0 = pg.evaluate(BIMG); pg.evaluate("() => CBApp._t.menu()"); pg.wait_for_timeout(100)
        check(b0[:4] == ['cb_board.webp', False, 'block', 'cbfire'] and (not HAVE or b0[4] == 1254), f'初めは いつもの ボード（夜の 光・火の あかりの ゆれ あり）（{b0}）')
        pg.evaluate("() => { const T = CBApp._t; T.state.coin = 250; T.state.boards = []; T.state.board = ''; T.save(); T.menu(); }"); pg.wait_for_timeout(150)
        pg.locator('#cbOv .cbmenu [data-cb=dz]').click(); pg.wait_for_timeout(200)
        pg.locator('#cbOv .cbdz [data-cb=dztab][data-t=d]').click(); pg.wait_for_timeout(250); e0 = pg.evaluate(DZ)
        bn = pg.evaluate("() => [...document.querySelectorAll('#cbOv .cbdz .dzt span')].map(s => s.textContent)")
        tw = pg.evaluate("() => [...document.querySelectorAll('#cbOv .cbdz .tabs button')].map(b => b.scrollWidth <= b.clientWidth + 1)")
        ti = pg.evaluate("() => [...document.querySelectorAll('#cbOv .cbdz .dzt > img')].map(i => { const r = i.getBoundingClientRect(); return Math.round(r.width / r.height * 100) / 100; })")
        check(e0['tab'] == ['カードパック', '表', '裏', 'ボード*'] and all(tw) and e0['h4'] == ['プレイボード1つ 300枚'] and len(e0['tiles']) == 8 and e0['tiles'][0] == '-:base:cb_board.webp:使って いる*'
              and [t.split(':')[1] for t in e0['tiles'][1:]] == ['marble', 'frost', 'sakura', 'violet', 'crimson', 'starry', 'steam'] and all(t.endswith('300枚!') for t in e0['tiles'][1:])
              and all(t.split(':')[2] == 'cb_bd_' + t.split(':')[1] + '_s.webp' for t in e0['tiles'][1:]) and bn == ['いつもの', '白亜の宮殿', '蒼氷の宮', '桜の舞踏会', '紫月の夜', '紅蓮の闘技場', '黄金の星空', '歯車の工房'] and all(1.7 <= r <= 1.85 for r in ti),
              f'デザインカスタムの 4つ目の タブ「ボード」（第4.189版：タブの 字は 4つとも おさまる）：いつもの ＋ 7種（1つ 300枚・横長の 絵）（{bn}）')
        shot(pg, 'cb_dz_boards')
        pg.locator('#cbOv .cbdz .dzt[data-cb=bdi][data-id="sakura"]').click(); pg.wait_for_timeout(150); y1 = pg.evaluate(MZ)
        bg = pg.evaluate("() => { const r = document.querySelector('#cbOv .cbmod .big.bd').getBoundingClientRect(); return [Math.round(r.left), Math.round(r.right), Math.round(r.width / r.height * 100) / 100, innerWidth]; }")
        check(y1 and y1['h'] == '桜の舞踏会プレイボード' and y1['img'] == 'cb_bd_sakura.webp' and y1['btns'] == ['バトルコイン 300枚で 解放!', '戻る'] and y1['need'] == 'あと 50枚 足りないよ（コンピュータに 勝つ・毎日の ログインボーナスで もらえるよ）'
              and bg[0] >= 0 and bg[1] <= bg[3] and 1.7 <= bg[2] <= 1.85,
              f'コインが 足りない（250枚）：大きい ボードの 絵・「バトルコイン 300枚で 解放」は 押せない・あと 50枚（{y1 and y1["btns"]}・{bg}）')
        shot(pg, 'cb_dz_board_item')
        pg.locator('#cbOv .cbmod [data-cb=dzback]').click(); pg.wait_for_timeout(80)
        pg.evaluate("() => { CBApp._t.state.coin = 700; }"); pg.locator('#cbOv .cbdz [data-cb=dztab][data-t=d]').click(); pg.wait_for_timeout(150)
        pg.locator('#cbOv .cbdz .dzt[data-cb=bdi][data-id="sakura"]').click(); pg.wait_for_timeout(120); y2 = pg.evaluate(MZ)
        pg.locator('#cbOv .cbmod [data-cb=bdopen]').click(); pg.wait_for_timeout(120); y3 = pg.evaluate(MZ)
        check(y2['btns'] == ['バトルコイン 300枚で 解放', '戻る'] and y3['h'] == '解放する？' and '『桜の舞踏会』（プレイボード）を 解放するよ' in y3['t'] and '700枚→残り 400枚' in y3['t'] and y3['btns'] == ['やめる', '解放する'] and y3['img'] == 'cb_bd_sakura_s.webp',
              f'700枚 ある：「解放」→ 確かめる 窓（700枚 → 残り 400枚・やめる／解放する）（{y3["t"]}）')
        pg.evaluate("() => { CBApp._guard = 1e9; }"); pg.locator('#cbOv .cbmod [data-cb=bdgo]').click(); pg.wait_for_timeout(100); h0 = pg.evaluate("() => [CBApp._t.state.coin, CBApp._t.state.boards.slice()]")
        pg.evaluate("() => { CBApp._guard = 0; }"); pg.locator('#cbOv .cbmod [data-cb=bdgo]').click(); pg.wait_for_timeout(200)
        e1 = pg.evaluate(DZ); s1 = pg.evaluate("() => { const s = CBApp._t.state, ls = JSON.parse(localStorage.getItem('tengel.cb')); return [s.coin, s.boards, s.board, ls.coin, ls.boards, ls.board]; }"); tt = pg.evaluate(TOAST)
        check(h0 == [700, []] and s1 == [400, ['sakura'], 'sakura', 400, ['sakura'], 'sakura'] and e1['tiles'][0] == '-:base:cb_board.webp:持って いる' and e1['tiles'][3] == '-:sakura:cb_bd_sakura_s.webp:使って いる*'
              and tt == '『桜の舞踏会』を 解放したよ！\nプレイボードが この デザインに なったよ' and not pg.evaluate("() => CBApp._t.modOn()"),
              f'「解放する」：窓が 出て すぐは 受けつけない → 300枚 減って（700 → 400）解放・すぐ その ボードに・覚える（{s1}）')
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
        check(y5['h'] == 'いつものプレイボード' and y5['img'] == 'cb_board.webp' and y5['btns'] == ['この ボードを 使う', '戻る'] and s2 == [400, ['sakura'], '', ''] and tt5 == 'プレイボードを『いつもの』に したよ'
              and b2[:4] == ['cb_board.webp', False, 'block', 'cbfire'] and b2[5] is False and g1[:2] + g1[3:] == g2[:2] + g2[3:] and g1[2][1:] == g2[2][1:] and abs((g2[2][0] - g1[2][0]) - g2[5][2] * 0.0586) <= 1.5,
              f'いつもの に 戻す：コインは 使わない・解放した ものは 残る・火の あかりが 戻る・カードを 置く 所・捨て札・歯車の 場所は ボードを 変えても 同じ・'
              f'山札は『桜の舞踏会』〈第4.186版の 新しい 絵〉の とき だけ ボードの 幅の 5.86% 左（{g2[2][0] - g1[2][0]}px／幅 {g2[5][2]}px）（{s2}）')
        pg.evaluate("() => { const T = CBApp._t; T.state.boards = ['sakura', 'violet']; T.state.board = 'violet'; T.save(); }")
        start(pg, '12345', '12345'); b3 = pg.evaluate(BIMG); g3 = pg.evaluate(GEO); pg.evaluate("() => CBApp._t.menu()"); pg.wait_for_timeout(100)
        # 第4.194版（まさちゃん 11/18 10:15「馬と山札重なってる！」）：『紫月の夜』『黄金の星空』『歯車の工房』も「山札」の 札を 左へ うつした 絵 → 山札も 左へ（7つ ぜんぶ dl）
        check(b3[0] == 'cb_bd_violet.webp' and b3[1] is True and b3[5] is True and g3[:2] + g3[3:] == g1[:2] + g1[3:] and g3[2] == g1[2],
              f'『紫月の夜』（第4.194版：「山札」の 札を 左へ うつした 絵）：山札は『桜の舞踏会』と 同じ 左の 場所（{g3[2]}・桜 {g1[2]}）')
        bd7 = []
        for bid in ('marble', 'frost', 'sakura', 'violet', 'crimson', 'starry', 'steam'):
            pg.evaluate("(id) => { const T = CBApp._t; T.state.boards = [id]; T.state.board = id; T.save(); }", bid)
            start(pg, '12345', '12345'); pg.wait_for_timeout(300 if HAVE else 0); bb = pg.evaluate(BIMG); gg = pg.evaluate(GEO); shot(pg, f'cb_board_{bid}'); pg.evaluate("() => CBApp._t.menu()"); pg.wait_for_timeout(60)
            bd7.append([bid, bb[0], bb[5], gg[2] == g1[2]])
        check(all(r[1] == f'cb_bd_{r[0]}.webp' and r[2] is True and r[3] for r in bd7), f'プレイボード 7つ ぜんぶ：山札は 左（dl）・同じ 場所（{bd7}）')
        pg.evaluate("() => { const s = JSON.parse(localStorage.getItem('tengel.cb')); s.boards = ['zz', 'sakura', 'sakura', 7]; s.board = 'frost'; localStorage.setItem('tengel.cb', JSON.stringify(s)); CBApp._t.load(); }")
        s3 = pg.evaluate("() => [CBApp._t.state.boards, CBApp._t.state.board]")
        check(s3 == [['sakura'], ''], f'覚えた 中身が おかしい ときは 直す（ない 名前・2つ目・解放して いない ボードは 捨てる）（{s3}）')
        pg.evaluate("() => { const T = CBApp._t; T.state.boards = []; T.state.board = ''; T.state.coin = 0; T.save(); T.menu(); }")

        print('■ 7 の 4枚 公開：強さ 逆転（第4.185版・まさちゃん 22:39「7は、手札に7が4枚ある場合、4枚公開し内1枚を捨てると、数字の強さ順が逆転する」・22:45「1.その試合は終わるまで」／第4.187版・11/17 09:39「手札に7が4枚ある段階で発動できる…フィールドセット必要ないからね！」＝セットの 前に 聞く）')
        pg.evaluate("() => { window.__seen = []; }"); start(pg, '77771', '23456', '345'); said(pg)
        a7 = pg.evaluate(ASKQ); v0 = pg.evaluate(V)
        check(a7 and a7['head'] == '7 が 4枚！' and a7['q'] == '7 を 4枚 見せて 逆転する？' and a7['img'] == 'cb_c7.webp' and a7['btns'][:2] == ['使わない', '使う'] and 'セットの 前に 使えるよ（セットは いらない）' in a7['text'] and 'この 対戦が 終わる まで 数字の 強さが 逆に なるよ' in a7['text']
              and v0['phase'] == 'set' and v0['my']['set'] is None and v0['op']['set'] is None and v0['can']['x7r'] is True,
              f'第4.187版：7 が 4枚 → ターンの 始め（セットの 前・まだ 誰も セットして いない）に 聞く 窓「7 が 4枚！ 7 を 4枚 見せて 逆転する？」（{a7 and a7["head"]}・{a7 and a7["q"]}）')
        shot(pg, 'cb_x7r_ask')
        peek(pg); m7 = pg.evaluate(MSG); b7 = acts(pg)
        check(m7 == 'セットする カードを 選んでね（カードを タップ）\n7 が 4枚！ セットの 前なら 逆転を 使えるよ' and b7 == ['使わない', '4枚 見せて 逆転'], f'「手札と ボードを 見る」→ 下の 行でも 答えられる（{m7}・{b7}）')
        pg.locator('#cbOv .cbact [data-cb=x7no]').click(); pg.wait_for_timeout(120)
        a73 = pg.evaluate(ASKQ)
        check(a73 and a73['head'] == '7 が 3枚！' and a73['q'] == '7 の 効果を 使う？' and pg.evaluate(V)['can']['x7r'] is True and pg.evaluate(V)['can']['x7'] is True and pg.evaluate(V)['rv'] is False,
              '「使わない」→ 次は 7 の 3枚 交換を 聞く（第4.202版：セットの 前の 効果は 1つずつ 順に 聞く）')
        pg.locator('#cbOv .cbmod.cbask [data-cb=p7no]').click(); pg.wait_for_timeout(120)
        check(asked(pg) is None and acts(pg) == ['セットの 前の 効果'] and pg.evaluate(V)['can']['x7r'] is True and pg.evaluate(V)['rv'] is False, f'どちらも「使わない」→ 窓は もう 出ない・セットする まで 下の ボタン「セットの 前の 効果」で もう 一度 聞ける（{acts(pg)}）')
        tap(pg, '1'); pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(100)
        check(asked(pg) is None and acts(pg) == ['セットの 前の 効果'], 'カードを 見て 戻っても 窓は 出ない（下の ボタンは 残る）')
        pg.locator('#cbOv .cbact [data-cb=prere]').click(); pg.wait_for_function("() => document.querySelector('#cbOv .cbmod.on.cbask')", timeout=5000); pg.wait_for_timeout(300)
        check(pg.evaluate(ASKQ)['head'] == '7 が 4枚！', '「セットの 前の 効果」→ もう 一度 聞く（4枚の 逆転 から）')
        pg.locator('#cbOv .cbmod.cbask [data-cb=x7yes]').click(); idle(pg)
        seen = pg.evaluate("() => window.__seen"); sd = said(pg); v7 = pg.evaluate(V); tb = pg.evaluate("() => document.querySelector('#cbOv .cbturn').textContent")
        check(any(x.startswith('7 の 効果！ 強さ 逆転|') for x in seen) and any(x.startswith('ban:強さ 逆転！') for x in sd) and v7['rv'] is True and v7['phase'] == 'set' and v7['turn'] == 1 and v7['my']['set'] is None and v7['can']['set'] is True and v7['can']['x7r'] is False
              and any(x == 'use:あなたが 使った！7 の 効果強さ 逆転7 を 4枚 見せて 1枚 捨てるよ。この 対戦が 終わる まで、数字の 強さが 逆に なる！' for x in sd)
              and pg.evaluate(HAND) == '1777' and pg.evaluate(DOMHAND) == '7771' and [d['k'] for d in v7['discard'] if d['why'] == '7'] == ['7'] and '強さ 逆転中' in tb and asked(pg) is None and acts(pg) == [] and pg.evaluate(MSG) == 'セットする カードを 選んでね（カードを タップ）',
              f'「使う」→ 効果の 札「強さ 逆転」→ 7 を 4枚 見せる 窓 → 1枚 捨て札へ →「強さ 逆転！」→ まだ セットの 前（手札は 逆の 強さで 並ぶ・上に「強さ 逆転中」・「セットする カードを 選んでね」）（{pg.evaluate(DOMHAND)}・{tb}）')
        shot(pg, 'cb_x7r_after')
        play(pg, '1'); pg.evaluate("() => { window.__seen = []; }"); opp(pg, {'t': 'set', 'k': 2})
        seen = pg.evaluate("() => window.__seen"); sd = said(pg); v7 = pg.evaluate(V)
        check(any('負け…' in x and '2 の ほうが 強いよ（強さ 逆転中）' in x for x in seen) and v7['op']['wins'] == 1 and v7['my']['wins'] == 0 and v7['turn'] == 2 and not any('効果タイム' in x for x in sd) and not any('3枚 戻して' in x for x in sd),
              'セット → オープン：1 は 2 に 負ける（もう 逆：「（強さ 逆転中）」）・7 が 3枚 残って いても、この ターンは 3枚 交換を 聞かない（どちらか 1つ）')
        a8 = pg.evaluate(ASKQ)
        check(a8 and a8['head'] == '7 が 3枚！' and pg.evaluate(V)['can']['x7r'] is False and pg.evaluate(V)['can']['x7'] is True, '2ターン目：もう 逆転ちゅう なので 4枚の 逆転は 聞かない（7 が 3枚 なので 3枚 交換 だけ 聞く）')
        pg.locator('#cbOv .cbmod.cbask [data-cb=p7no]').click(); pg.wait_for_timeout(100)
        pg.locator('#cbOv [data-cb=discard]').click(); pg.wait_for_timeout(100)
        dl = pg.evaluate("() => [...document.querySelectorAll('#cbOv .cbmod .cbdl .row[data-de]')].map(r => r.dataset.de + '|' + r.textContent.replace(/\\s+/g, ' ').trim())")
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        check(any(x.startswith('7|') and 'あなたの 7 の 効果' in x for x in dl), f'捨て札の 窓：「あなたの 7 の 効果」に 捨てた 7（{dl}）')
        check(asked(pg) is None and acts(pg) == ['7 を 3枚 交換'], f'「使わない」→ 下の ボタンは「7 を 3枚 交換」（{acts(pg)}）')
        pg.evaluate("() => { window.__seen = []; }"); play(pg, '7'); opp(pg, {'t': 'set', 'k': 3}); v8 = pg.evaluate(V); s8 = pg.evaluate("() => window.__seen")
        play(pg, '7'); opp(pg, {'t': 'set', 'k': 6}); v9 = pg.evaluate(V)
        check(v8['my']['wins'] == 1 and v8['turn'] == 3 and v8['rv'] is True and any('7 が 3 に 勝ったよ（強さ 逆転中）' in x for x in s8) and v9['phase'] == 'end' and v9['res'] == 'win' and v9['my']['wins'] == 2,
              f'2ターン目・3ターン目も 逆：7 は 3 にも 6 にも 勝つ → 2勝 1敗で 勝ち（逆転は その 対戦が 終わる まで）')
        pg.wait_for_function("() => { const g = document.querySelector('#cbOv .cbend .gift'); return g && g.textContent.length > 3; }", timeout=30000)
        # 相手（コンピュータ）が セットの 前に 4まい 公開 → 7 か 1 を セット：場の カードは うら・第4.203版：相手の 手札は 本当の 手札（7 を 出したら 7 が 2まいに）
        OPH = "() => [...document.querySelectorAll('#cbOv .cbohand .cbc')].map(c => c.dataset.ck || '-').join('')"
        for hk in ('7', '1'):
            start(pg, '23456', '77771', '345'); said(pg); pg.evaluate("() => { window.__seen = []; }")
            opp(pg, {'t': 'x7r'})
            seen = pg.evaluate("() => window.__seen"); vo = pg.evaluate(V); tb2 = pg.evaluate("() => document.querySelector('#cbOv .cbturn').textContent"); sd = said(pg); o1 = pg.evaluate(OPH); hs = pg.evaluate(DOMHAND)
            opp(pg, {'t': 'set', 'k': hk}); o2 = pg.evaluate(OPH); sl = pg.evaluate(SLOT); m2 = pg.evaluate(MSG)
            if hk == '7':
                check(any(x.startswith('7 の 効果！ 強さ 逆転|') for x in seen) and vo['rv'] is True and vo['phase'] == 'set' and vo['can']['set'] is True and o1 == '777-' and '強さ 逆転中' in tb2
                      and any(x.startswith('use:コンピュータが 使った！7 の 効果強さ 逆転') for x in sd) and hs == '65432' and asked(pg) is None,
                      f'相手が セットの 前に 4枚 公開 → 相手の 手札に 残った 7 の 3枚は 表で 見える・自分の 手札は 強い 順（逆）に 並ぶ・自分は これから セット（{hs}・{o1}）')
            check(o2 == ('77-' if hk == '7' else '777') and sl == 'b -' and 'コンピュータは もう セットしたよ' in m2,
                  f'相手が {"7" if hk == "7" else "1"} を セット：場の カードは 裏・相手の 手札は 本当の 手札（第4.203版：{"見えて いた 7 が 1枚 へる" if hk == "7" else "7 は 3枚の まま・裏の 1 が 消える"}：{o2}・{sl}）')
            play(pg, '2'); vx = pg.evaluate(V); o3 = pg.evaluate(OPH)
            check(vx['last']['c'] == ['2', hk] and vx['last']['res'] == ('lose' if hk == '7' else 'win') and o3 == ('77-' if hk == '7' else '777'),
                  f'オープン：{"逆転ちゅうの 7 が 2 に 勝つ" if hk == "7" else "逆転ちゅうの 2 が 1 に 勝つ"}・その あと 相手の 手札は 本当の 形（{o3}）')
        pg.evaluate("() => CBApp._t.menu()"); pg.wait_for_timeout(100)
        # 7 の 新しい 絵・カスタムの 名前（前の『緑の森』『天空の都』は 消した）
        pg.locator('#cbOv .cbmenu [data-cb=dz]').click(); pg.wait_for_timeout(150); pg.locator('#cbOv .cbdz [data-cb=dztab][data-t=f]').click(); pg.wait_for_timeout(150)
        n7 = pg.evaluate("() => [...document.querySelectorAll('#cbOv .cbdz .dzt[data-ck=\"7\"]')].map(t => t.dataset.id + ':' + t.querySelector('span').textContent)")
        pg.locator('#cbOv .cbdz [data-cb=dzx]').click(); pg.wait_for_timeout(100)
        check(n7 == [':いつもの', '7a:疾風の草原', '7b:翡翠の馬', '7r:翠玉の輝き', '7sr:天空の楽園'], f'7 の カスタム：『疾風の草原』『翡翠の馬』（新しい 絵：前の 2つは 消した）・第4.189版：パックの レア『翠玉の輝き』・超レア『天空の楽園』（{n7}）')

        print('■ 4 の 効果で 交換して 5 を 出したら 5 の 効果（第4.183版・まさちゃん 21:24「バトルカード、4で交換した後に5を相手がフィールドにセットした場合、五の効果を使える」）')
        # 自分が 交換させられて 5 を 出す → 聞く 窓 → 使う → 捨てる カード → 山札の 神様馬で 勝ち
        start(pg, '15623', '47712', 'k'); play(pg, '1'); opp(pg, {'t': 'set', 'k': 4}); opp(pg, {'t': 'eff', 'use': {'u4': True}}); idle(pg)
        pg.evaluate("() => { window.__seen = []; }")
        tap(pg, '5'); pg.locator('#cbOv .cbmod [data-cb=swap]').click(); idle(pg)
        a5 = pg.evaluate(ASKQ); v5 = pg.evaluate(V)
        check(a5 and a5['head'] == '交換で 5 を セット！' and a5['q'] == '5 の 効果を 使う？' and a5['img'] == 'cb_c5.webp' and a5['btns'][:2] == ['使わない', '使う'] and v5['pend'] == {'type': 'u5', 'mine': True} and pg.evaluate(SLOT) == '4:4 の 効果 b[5]:伏せて セット',
              f'4 の 効果で 交換して 5 を 出した → 真ん中に「交換で 5 を セット！ 5 の 効果を 使う？」（使わない／使う）・オープンは まだ（{a5 and a5["head"]}）')
        shot(pg, 'cb_swap5_ask')
        pg.locator('#cbOv .cbmod.cbask [data-cb=u5yes]').click(); pg.wait_for_timeout(100)
        m5 = pg.evaluate(MSG); b5 = acts(pg)
        tap(pg, '6'); mb5 = modbtns(pg)
        check('5 と 一緒に 捨てる カードを 選んでね' in m5 and b5 == ['戻る'] and mb5[0].startswith('この カードを 捨てる'), f'「使う」→ 一緒に 捨てる カードを 選ぶ（{m5}）')
        pg.locator('#cbOv .cbmod [data-cb=u5drop]').click(); idle(pg)
        v6 = pg.evaluate(V)
        check(any('勝ち！' in s for s in pg.evaluate("() => window.__seen")) and v6['my']['wins'] == 1 and v6['turn'] == 2 and [d['k'] for d in v6['discard'] if d['why'] == '5'] == ['5', '6'] and pg.evaluate(HAND) == '123',
              f'5 と 6 を 捨てて 山札から 伏せて セット → オープン：山札の 神様馬で 4 に 勝ち（{[d["k"] for d in v6["discard"]]}）')
        # 相手（コンピュータ）が 交換させられて 5 を 出す → 自分の 画面は「交換して いるよ」の まま → 相手が 5 の 効果
        start(pg, '41236', '15677', 'k'); opp(pg, {'t': 'set', 'k': 1}); play(pg, '4')
        pg.locator('#cbOv [data-cb=effyes]').click(); idle(pg)
        opp(pg, {'t': 'swap', 'k': 5}); idle(pg)
        m6 = pg.evaluate(MSG); v7 = pg.evaluate(V)
        check(v7['pend'] == {'type': 'swap', 'mine': False} and v7['phase'] == 'swap' and 'コンピュータが カードを 交換して いるよ' in m6 and pg.evaluate(ASKQ) is None, f'相手が 交換で 5 を 出して 選んで いる 間も、自分の 画面は「交換して いるよ…」の まま（5 だと 分からない）（{m6}）')
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
        check(pg.evaluate(MSB) == '🎯ミッション今月 0／23 達成', f'メニューの「ミッション」：今月 0／23 達成（第4.209版：決戦調査ミッション 9つ を 足した）（{pg.evaluate(MSB)}）')
        pg.locator('#cbOv .cbmenu [data-cb=ms]').click(); pg.wait_for_timeout(200); m0 = pg.evaluate(MSS)
        check(m0 and pg.evaluate("() => CBApp._t.screen") == 'ms' and m0['coin'] == 'バトルコイン 0枚' and m0['m'] == '11月の ミッション12月1日に リセット（あと 15日）' and m0['tab'] == ['コンピュータ0／7 達成*', '友達バトル0／7 達成', '決戦調査0／9 達成'] and m0['h4'] == 'コンピュータに 連続勝利'
              and m0['cur'] == '今0連勝次は 3連勝で 30枚（あと 3勝）' and m0['rows'] == ['3連勝30枚あと 3勝>', '5連勝60枚', '6連勝90枚', '7連勝120枚', '8連勝150枚', '9連勝200枚', '10連勝300枚'] and not m0['tool']
              and '毎月 1日に リセット' in m0['note'] and '同点は そのまま' in m0['note'] and '部屋を 出た' not in m0['note'],
              f'ミッションの 画面：11月の ミッション（12月1日に リセット・あと 15日）・コンピュータに 連続勝利 7つ（3・5・6・7・8・9・10連勝 → 30〜300枚）・今 0連勝（{m0 and m0["rows"]}）')
        shot(pg, 'cb_ms_cpu')
        pg.locator('#cbOv .cbms [data-cb=mstab][data-t=fr]').click(); pg.wait_for_timeout(150); m1 = pg.evaluate(MSS)
        check(m1['tab'] == ['コンピュータ0／7 達成', '友達バトル0／7 達成*', '決戦調査0／9 達成'] and m1['h4'] == '友達バトルで 連続勝利' and m1['rows'] == ['3連勝20枚あと 3勝>', '5連勝40枚', '6連勝60枚', '7連勝80枚', '8連勝100枚', '9連勝120枚', '10連勝140枚'] and '部屋を 出た・つながりが 切れた ときは 数えないよ' in m1['note'],
              f'「友達バトル」：3・5・6・7・8・9・10連勝 → 20〜140枚・友達が 部屋を 出た／切れた ときは 数えない（{m1["rows"]}）')
        shot(pg, 'cb_ms_fr')
        pg.locator('#cbOv .cbms [data-cb=mstab][data-t=cpu]').click(); pg.locator('#cbOv .cbms [data-cb=msx]').click(); pg.wait_for_timeout(150)
        check(pg.evaluate("() => CBApp._t.screen") == 'menu', '「← 戻る」→ メニュー')
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
        check(lv == 'cpu' and s3['cpu'] == 3 and s3['got']['cpu'] == [3] and s3['live'] == '' and pg.evaluate("() => CBApp._t.state.coin") == 32 and '🎯ミッション達成！3連勝＋30枚' in eg['t'] and 'バトルコイン ＋2枚（今 32枚）' in eg['t']
              and eg['lab'] == 'ミッション達成 3連勝 バトルコイン 30枚' and eg['anim'] == 'cbget/1' and eg['h'] == eg['minh'] and 0 < eg['w'] <= eg['vw'] - 32,
              f'3連勝目：その場で ミッション達成（＋30枚 ＋ いつもの 2枚 ＝ 32枚）・最後の 画面に「🎯 ミッション達成！ 3連勝 🪙＋30枚」（1回 ふくらむ だけ・札の 場所に おさまる {eg["h"]}／{eg["minh"]}px）・配った とき「対戦 ちゅう」の 印 → 終わって 消える')
        shot(pg, 'cb_ms_end3')
        pg.locator('#cbOv .cbend [data-cb=menu]').click(); pg.wait_for_timeout(150)
        pg.locator('#cbOv .cbmenu [data-cb=ms]').click(); pg.wait_for_timeout(150); m2 = pg.evaluate(MSS)
        check(m2['coin'] == 'バトルコイン 32枚' and m2['tab'][0] == 'コンピュータ1／7 達成*' and m2['cur'] == '今3連勝次は 5連勝で 60枚（あと 2勝）' and m2['rows'][:2] == ['3連勝30枚✓ 達成*', '5連勝60枚あと 2勝>'],
              f'ミッションの 画面：3連勝 ✓ 達成・次は 5連勝（あと 2勝）（{m2["rows"][:2]}）')
        pg.locator('#cbOv .cbms [data-cb=msx]').click(); pg.wait_for_timeout(100)
        check(pg.evaluate(MSB) == '🎯ミッション今月 1／23 達成', 'メニュー：今月 1／23 達成')
        # 同点 → そのまま／負け → 0
        start(pg, 'k1234', 'm1234'); ckey(pg, 'k'); opp(pg, {'t': 'set', 'k': 'm'}); ckey(pg, '1'); opp(pg, {'t': 'set', 'k': 1}); ckey(pg, '2'); opp(pg, {'t': 'set', 'k': 2})
        pg.wait_for_function("() => CBApp._t.ended", timeout=30000); pg.wait_for_timeout(300)
        d3 = [pg.evaluate("() => CBApp._t.view.res"), pg.evaluate(MST)['cpu']]
        start(pg, '23677', '12356'); play(pg, '3'); opp(pg, {'t': 'set', 'k': 1}); play(pg, '6'); opp(pg, {'t': 'set', 'k': 2}); play(pg, '7'); opp(pg, {'t': 'set', 'k': 3})
        pg.wait_for_function("() => CBApp._t.ended", timeout=30000); pg.wait_for_timeout(300)
        l3 = [pg.evaluate("() => CBApp._t.view.res"), pg.evaluate(MST)]
        check(d3 == ['draw', 3] and l3[0] == 'lose' and l3[1]['cpu'] == 0 and l3[1]['got']['cpu'] == [3] and pg.evaluate("() => CBApp._t.state.coin") == 32, f'同点 → 連勝は そのまま（{d3}）・負け → 0（達成した 3連勝と コインは 残る）')
        # とちゅうで やめる → 0
        pg.evaluate("() => { const T = CBApp._t; T.state.ms.cpu = 4; T.save(); }")
        start(pg, 'k1234', '76543'); pg.locator('#cbOv .cbtop [data-cb=quit]').click(); pg.locator('#cbOv .cbmod [data-cb=quitgo]').click(); pg.wait_for_timeout(150)
        q0 = pg.evaluate(MST)
        check(q0['cpu'] == 0 and q0['live'] == '' and pg.evaluate("() => CBApp._t.screen") == 'menu', f'対戦の 途中で やめた → ミッションの 連勝も 0（{q0["cpu"]}）')
        # 対戦の とちゅうで アプリが 閉じられた（つぎに 開いた とき）→ 0・知らせる（第4.191版：負けに 数えて いつもの 連勝も 0）
        pg.evaluate("() => { const T = CBApp._t; T.state.ms.cpu = 4; T.state.streak = 4; T.save(); }")
        start(pg, 'k1234', '76543'); ckey(pg, 'k')
        sv2 = json.loads(pg.evaluate("() => localStorage.getItem('tengel.cb')")); lv2 = sv2['ms']
        pg.evaluate("() => { CBApp._t.load(); CBApp._t.menu(); }"); pg.wait_for_timeout(150); tt = pg.evaluate(TOAST); q1 = pg.evaluate(MST); sq1 = pg.evaluate("() => [CBApp._t.state.streak, CBApp._t.state.lose, CBApp._t.state.win]")
        check(sv2['streak'] == 4 and sq1 == [0, sv2['lose'] + 1, sv2['win']] and '負けに 数えたよ（4連勝は 0 に 戻ったよ）' in tt and pg.locator('#cbOv .cbmenu .rec').inner_text().startswith(f'{sv2["win"]}勝 {sv2["lose"] + 1}敗'),
              f'第4.191版：対戦 ちゅうに アプリが 閉じられた ＝「やめる」と 同じ：負けに 数える・いつもの 連勝（4）も 0（前は ミッションの 連勝 だけ）・「負けに 数えたよ（4連勝は 0 に 戻ったよ）」（{sq1}）')
        check(lv2['live'] == 'cpu' and lv2['cpu'] == 4 and q1['cpu'] == 0 and q1['live'] == '' and '前の 対戦が 途中で 終わった ので、' in tt and 'ミッションの 連勝（コンピュータ）は 0 に 戻ったよ' in tt,
              f'対戦 ちゅうに アプリが 閉じられた → 次に 開いた とき ミッションの 連勝は 0・「ミッションの 連勝（コンピュータ）は 0 に 戻ったよ」（{tt!r}）')
        # 第4.191版：結果は 決まった とき（'end' が 届いた とき）すぐ 数える → 最後の 札の とちゅうで アプリが 閉じられても 勝ちは 勝ち（負けを 足さない）
        sv0 = pg.evaluate("() => { const T = CBApp._t, s = T.state; return { coin: s.coin, win: s.win, lose: s.lose, draw: s.draw, streak: s.streak, owe: s.owe }; }")      # この 場面の あとで もとに もどす（あとの 場面の コインの 数を かえない）
        pg.evaluate("() => { const T = CBApp._t; T.state.ms.cpu = 0; T.state.streak = 2; T.save(); }"); w0 = pg.evaluate("() => [CBApp._t.state.win, CBApp._t.state.lose]")
        start(pg, 'k1234', '76543'); ckey(pg, 'k'); opp(pg, {'t': 'set', 'k': 7}); pg.locator('#cbOv .cbmod [data-cb=kskip]').click(); idle(pg)
        ckey(pg, '1'); opp(pg, {'t': 'set', 'k': 6}); ckey(pg, '2'); pg.evaluate("() => CBApp._t.speed(1)")      # 最後の 手は ふつうの 速さ・待たずに 読む（札を 見せて いる とちゅうを つかまえる）
        e0 = pg.evaluate("""async () => { const m = CBApp._t.match, S = m._.state(), c = S.p[1].hand.find(x => x.k === '3'); m._.apply(1, { t: 'set', u: c.u }); await new Promise(r => setTimeout(r, 150));
          return [CBApp._t.ended, !!document.querySelector('#cbOv .cbend'), JSON.parse(localStorage.getItem('tengel.cb'))]; }"""); pg.evaluate("() => CBApp._t.speed(0.03)")
        pg.evaluate("() => { CBApp._t.load(); }"); e1 = pg.evaluate("() => [CBApp._t.state.win, CBApp._t.state.lose, CBApp._t.state.streak, CBApp._t.state.ms.live]")
        pg.wait_for_function("() => CBApp._t.ended && !!document.querySelector('#cbOv .cbend .gift')", timeout=30000); pg.wait_for_timeout(300)
        g1 = pg.locator('#cbOv .cbend .gift').inner_text(); pg.evaluate("() => CBApp._t.menu()"); pg.wait_for_timeout(150); tt1 = pg.evaluate(TOAST) or ''
        check(not e0[0] and not e0[1] and e0[2]['win'] == w0[0] + 1 and e0[2]['lose'] == w0[1] and e0[2]['streak'] == 3 and e0[2]['ms']['live'] == '' and e1 == [w0[0] + 1, w0[1], 3, ''] and '負けに 数えたよ' not in tt1 and 'バトルコイン' in g1,
              f'第4.191版：最後の 手で 勝ちが 決まった とき すぐ 数えて 保存（まだ 最後の 札を 見せて いる 途中：{not e0[0] and not e0[1]}）→ そこで アプリが 閉じられても 勝ち（{e1}）・負けを 足さない')
        pg.evaluate("(v) => { const T = CBApp._t; Object.assign(T.state, v); T.state.ms.cpu = 0; T.state.ms.live = ''; T.save(); T.menu(); }", sv0); pg.wait_for_timeout(150)
        # 月が かわる → リセット（達成も 連勝も 0）
        pg.evaluate("() => { const T = CBApp._t; T.state.ms.cpu = 3; T.state.ms.fr = 2; T.state.ms.got = { cpu: [3], fr: [] }; T.save(); CBApp._now = () => new Date(2026, 11, 1, 0, 0, 5); T.menu(); }"); pg.wait_for_timeout(150)
        r0 = pg.evaluate(MST); mb = pg.evaluate(MSB)
        pg.locator('#cbOv .cbmenu [data-cb=ms]').click(); pg.wait_for_timeout(150); m3 = pg.evaluate(MSS)
        check(r0 == {'m': '2026-12', 'cpu': 0, 'fr': 0, 'got': {'cpu': [], 'fr': [], 'q': []}, 'live': ''} and mb == '🎯ミッション今月 0／23 達成' and m3['m'] == '12月の ミッション1月1日に リセット（あと 31日）' and m3['rows'][0] == '3連勝30枚あと 3勝>' and pg.evaluate("() => CBApp._t.state.coin") == 32,
              f'月が 変わった（12月1日）→ ミッションを リセット（達成も 連勝も 0・コインは 残る）・「12月の ミッション（1月1日に リセット）」（{r0}）')
        pg.locator('#cbOv .cbms [data-cb=msx]').click(); pg.wait_for_timeout(100)
        # 第4.191版：月が もどった（日付を もどした）→ リセットしない（もう 1回 達成 は できない）・ミッションの 画面の 月は おぼえた 月
        pg.evaluate("() => { const T = CBApp._t; T.state.ms.cpu = 2; T.state.ms.got = { cpu: [], fr: [] }; T.save(); CBApp._now = () => new Date(2026, 10, 20, 12, 0, 0); T.menu(); }"); pg.wait_for_timeout(150)
        b0 = pg.evaluate(MST); pg.locator('#cbOv .cbmenu [data-cb=ms]').click(); pg.wait_for_timeout(150); mb2 = pg.evaluate(MSS); pg.locator('#cbOv .cbms [data-cb=msx]').click(); pg.wait_for_timeout(100)
        check(b0['m'] == '2026-12' and b0['cpu'] == 2 and mb2['m'] == '12月の ミッション1月1日に リセット（あと 42日）',
              f'第4.191版：日付を 11月に 戻しても リセットしない（{b0["m"]}・連勝 {b0["cpu"]}）・画面は「12月の ミッション（1月1日に リセット）」（{mb2["m"]!r}）')
        # 第4.191版：テストの 時計（CBApp._now）が ない ときは 時計の 番人の 本当の 時刻（TengelClock.now）で 決める
        pg.evaluate("() => { CBApp._now = null; window.__tcNow = window.TengelClock.now; window.TengelClock.now = () => new Date(2027, 0, 3, 9, 0, 0).getTime(); CBApp._t.menu(); }"); pg.wait_for_timeout(150)
        b1 = pg.evaluate(MST); pg.evaluate("() => { window.TengelClock.now = window.__tcNow; CBApp._now = () => new Date(2026, 11, 1, 0, 0, 5); }")
        check(b1['m'] == '2027-01' and b1['cpu'] == 0, f'第4.191版：本当の 時刻（時計の 番人）が 1月 → リセット（{b1["m"]}）')
        # 前の 月の 連勝の まま 月が かわって 勝つ → 新しい 月の 1連勝（前の 月の 続きに しない）
        pg.evaluate("() => { const T = CBApp._t; T.state.ms = { m: '2026-11', cpu: 9, fr: 0, got: { cpu: [3, 5, 6, 7, 8, 9], fr: [] }, live: '' }; T.save(); }")
        start(pg, 'k1234', '76543'); ckey(pg, 'k'); opp(pg, {'t': 'set', 'k': 7}); pg.locator('#cbOv .cbmod [data-cb=kskip]').click(); idle(pg)
        ckey(pg, '1'); opp(pg, {'t': 'set', 'k': 6}); ckey(pg, '2'); opp(pg, {'t': 'set', 'k': 3})
        pg.wait_for_function("() => { const g = document.querySelector('#cbOv .cbend .gift'); return CBApp._t.ended && g && g.textContent.length > 3; }", timeout=30000)
        r1 = pg.evaluate(MST)
        check(r1 == {'m': '2026-12', 'cpu': 1, 'fr': 0, 'got': {'cpu': [], 'fr': [], 'q': []}, 'live': ''} and 'ミッション達成' not in pg.locator('#cbOv .cbend .gift').inner_text(), f'11月の 9連勝の まま 12月に 勝つ → 12月の 1連勝（10連勝の 達成には ならない）（{r1}）')
        # おぼえた 中身が おかしい ときは なおす
        pg.evaluate("() => { const s = JSON.parse(localStorage.getItem('tengel.cb')); s.ms = { m: 'xx', cpu: -5, fr: 'a', got: { cpu: [3, 3, 4, 5, 'x'], fr: null, q: ['g3w3', 'g3w3', 'x', 5, 'g5w6'] }, live: 'zz' }; localStorage.setItem('tengel.cb', JSON.stringify(s)); CBApp._t.load(); }")
        check(pg.evaluate(MST) == {'m': '2026-12', 'cpu': 0, 'fr': 0, 'got': {'cpu': [3, 5], 'fr': [], 'q': ['g3w3', 'g5w6']}, 'live': ''}, f'覚えた ミッションが おかしい ときは 直す（第4.209版：決戦調査ミッションも・{pg.evaluate(MST)}）')

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
        check(d0 == 0 and lg1['line'] == '1日目 の ボーナス+500Pとバトルコイン+2枚を もらったよ' and lg1['img'] == 8 and lg1['tiles'][0] == '1日目500P2枚' and lg1['tiles'][6] == '7日目3,000P12枚' and lg1['cb'] == [2, 2, 2, 2, 2, 2, 12] and lg1['inside'] and lg1['q']
              and g1 == {'v': 1, 'list': [{'id': f'login-{today}', 'c': 2}]} and c1 == [7, [f'login-{today}'], 7, '7'] and tt == ['🎁 ログインボーナスの バトルコイン\n2枚を 受け取ったよ'],
              f'カードバトルの メニューを 開いて いる ときに ログインボーナス（1日目）→ 窓に「バトルコイン +2枚」（7日ぶんの 札にも：1〜6日目 2枚・7日目 12枚）・すぐ 受け取る（5 → {c1[0]}枚）・メニューで 知らせる（{tt!r}）')
        pg.evaluate("() => { CBApp._t.load(); CBApp._t.menu(); }"); pg.wait_for_timeout(150); c2 = pg.evaluate(COINS4); r2 = pg.evaluate("() => TengelLogin.check()"); pg.wait_for_timeout(300); c3 = pg.evaluate(COINS4)
        check(c2 == c1 and r2 == -1 and c3 == c1 and pg.evaluate(GIFT) == g1, f'読み直しても・同じ 日に もう 1回 確かめても 2回は 入らない（{c3[0]}枚 の まま）')
        # 閉じて いる あいだに 7日目（2枚 ＋10枚）→ つぎに 開いた とき 受け取る
        pg.evaluate("() => { CBApp.close(); const g = JSON.parse(localStorage.getItem('tengel.cbgift')); g.list.push({ id: 'login-2099-01-07', c: 12 }); localStorage.setItem('tengel.cbgift', JSON.stringify(g)); }"); pg.wait_for_timeout(200)
        pg.evaluate("() => CBApp.open()"); pg.wait_for_timeout(400); tt4 = TS(); c4 = pg.evaluate(COINS4)
        shot(pg, 'cb_login_menu')
        check(c4 == [19, [f'login-{today}', 'login-2099-01-07'], 19, '19'] and tt4 == ['🎁 ログインボーナスの バトルコイン\n12枚を 受け取ったよ'], f'カードバトルを 閉じて いる 間の ログインボーナス（7日目 12枚）→ 次に 開いた とき 受け取る（7 → {c4[0]}枚・{tt4!r}）')
        # 持てる 数（9999枚）で 止まる・おかしな 中身は 入れない
        pg.evaluate("() => { const T = CBApp._t; T.state.coin = 9995; T.save(); const g = JSON.parse(localStorage.getItem('tengel.cbgift')); g.list.push({ id: 'login-2099-01-08', c: 12 }, { id: 5, c: 3 }, { id: 'x', c: -4 }, null); localStorage.setItem('tengel.cbgift', JSON.stringify(g)); document.dispatchEvent(new CustomEvent('tengel:cbgift')); }")
        pg.wait_for_timeout(300); tt5 = TS(); c5 = pg.evaluate(COINS4)
        check(c5[0] == 9999 and c5[2] == 9999 and c5[1][-1] == 'login-2099-01-08' and len(c5[1]) == 3 and tt5 == ['🎁 ログインボーナスの バトルコイン\n4枚を 受け取ったよ（9999枚 まで）'],
              f'持てる 数（9999枚）を 超える 分は 入らない・おかしな 中身（id が ない・枚数が マイナス）は 入れない（{c5[0]}枚・{tt5!r}）')
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
              f'① コンピュータとの 対戦：相手（コンピュータ）の 手札・伏せた カードも 自分が 選んだ うら『天馬の光』・めくった 6 も 自分の デザイン『赤の書庫』（{i0["op"]}・{o0[-1] if o0 else None}）')
        pg.evaluate("() => CBApp._t.menu()"); pg.wait_for_timeout(100)
        # ② 友だち：自分の カード＝自分の デザイン・友だちの カード＝友だちの デザイン（ホスト：うら 天馬の光・神様馬 朱の鳥居／ゲスト：うら 星座の馬・幻の馬 紅い雷・3 星の遺跡）
        gp.evaluate("() => { const T = CBApp._t; T.state.backs = ['star']; T.state.faces = ['mb', '3b']; T.state.back = 'star'; T.state.face = { m: 'mb', '3': '3b' }; T.state.coin = 0; T.state.ms = { m: T.msKey(), cpu: 0, fr: 0, got: { cpu: [], fr: [] }, live: '' }; T.menu(); }")
        gp.evaluate(OPN)
        pg.evaluate("() => { const T = CBApp._t; T.state.coin = 0; T.state.ms = { m: T.msKey(), cpu: 0, fr: 2, got: { cpu: [], fr: [] }, live: '' }; CBApp._opt = { hands: [['k', '1', '2', '6', '7'], ['m', '3', '4', '5', '7']], turns: 3 }; CBApp._think = null; }")
        pg.locator('#cbOv .cbmenu [data-cb=host]').click(); pg.wait_for_timeout(300)
        z0 = pg.evaluate("() => { const r = document.querySelector('#cbOv .cbroom'); return { h2: r.querySelector('h2').textContent, p: r.querySelector('h2 + p').textContent, chips: r.querySelectorAll('[data-cb=stke]').length, coin: !!r.querySelector('.cbcoinl'), gem: [...r.querySelectorAll('[data-cb=rgon]')].map(b => b.textContent + (b.classList.contains('on') ? '*' : '')).join(','), gp: !!r.querySelector('.gp'), hint: !!r.querySelector('.hint'), go: r.querySelector('[data-cb=stkgo]').textContent, calls: window.__room.calls.length }; }")
        check(z0['h2'] == '部屋を 作る' and z0['p'] == '部屋の 決まりを 決めてね' and z0['chips'] == 0 and not z0['coin'] and z0['gem'] == 'なし*,あり' and not z0['gp'] and not z0['hint'] and z0['go'] == '部屋を 作る',
              f'第4.197版：バトルコイン 0枚でも「部屋を 作る」→ 先に 部屋の 決まり（コインの 所は 出さない・決戦宝石 なし／あり だけ）（{z0}）')
        pg.locator('#cbOv .cbroom [data-cb=stkgo]').click(); pg.wait_for_timeout(300)
        num = pg.evaluate("() => document.querySelector('#cbOv .cbroom .num').textContent")
        gp.locator('#cbOv .cbmenu [data-cb=join]').click(); gp.wait_for_timeout(150)
        for d in num: gp.locator(f'#cbOv .cbkeys [data-key="{d}"]').click()
        gp.locator('#cbOv .cbkeys [data-key=go]').click()
        pg.wait_for_function("() => CBApp._t.screen === 'game' && CBApp._t.view && CBApp._t.idle", timeout=30000); gp.wait_for_function("() => CBApp._t.screen === 'game' && CBApp._t.view && CBApp._t.idle", timeout=30000)
        hi, gi = pg.evaluate(IMS), gp.evaluate(IMS)
        hz, gz = pg.evaluate("() => CBApp._t.match.opDz"), gp.evaluate("() => CBApp._t.match.opDz")
        check(hz == {'b': 'star', 'f': {'3': '3b', 'm': 'mb'}} and gz == {'b': 'sky', 'f': {'6': '6a', 'k': 'ka'}}, f'部屋に 入った とき、おたがいの 選んだ デザインが 届く（ホスト ← {hz}・ゲスト ← {gz}）')
        check(hi['deck'] == 'cb_bk_sky_d.webp' and hi['op'] == ['cb_bk_star_s.webp'] and 'k=cb_fc_ka_s.webp' in hi['my'] and '6=cb_fc_6a_s.webp' in hi['my'] and '1=cb_s1.webp' in hi['my']
              and gi['deck'] == 'cb_bk_star_d.webp' and gi['op'] == ['cb_bk_sky_s.webp'] and 'm=cb_fc_mb_s.webp' in gi['my'] and '3=cb_fc_3b_s.webp' in gi['my'] and '4=cb_s4.webp' in gi['my'],
              f'② 友達との 対戦：自分の 手札・山札は 自分の デザイン・友達の 手札は 友達が 選んだ うら（ホスト：相手 {hi["op"]}・ゲスト：相手 {gi["op"]}）')
        shot(pg, 'cb_room_dz_host'); shot(gp, 'cb_room_dz_guest')
        ckey(gp, 'm'); idle(pg)
        hs1 = pg.evaluate(IMS)['os']
        ckey(pg, 'k'); idle(gp); idle(pg); pg.wait_for_timeout(150)
        ho, go = pg.evaluate("() => window.__op.slice()"), gp.evaluate("() => window.__op.slice()")
        check(hs1 == 'cb_bk_star_s.webp' and any(x.endswith('|cb_bk_sky_c.webp,cb_fc_ka_c.webp,cb_bk_star_c.webp,cb_fc_mb_c.webp') for x in ho) and any(x.endswith('|cb_bk_star_c.webp,cb_fc_mb_c.webp,cb_bk_sky_c.webp,cb_fc_ka_c.webp') for x in go),
              f'友達が 伏せた カードは 友達の 裏・めくると：自分の 神様馬『朱の鳥居』／友達の 幻の馬『紅い雷』（ゲストの 画面は その 反対）（{ho[-1] if ho else None}）')
        ckey(gp, '3'); idle(pg); ckey(pg, '1'); idle(gp); idle(pg)
        pg.locator('#cbOv [data-cb=discard]').click(); pg.wait_for_timeout(100)
        hd = pg.evaluate("() => [...document.querySelectorAll('#cbOv .cbmod .cbdl .row[data-dt]')].map(r => r.querySelector('b').textContent + '|' + [...r.querySelectorAll('.pr')].map(p => p.querySelector('span').textContent + '=' + [...p.querySelectorAll('img')].map(i => i.getAttribute('src')).join(',')).join('|'))")
        pg.locator('#cbOv .cbmod .cbdl .row[data-dt="2"] .pr:last-child .cbc').click(); pg.wait_for_timeout(80); big = pg.evaluate("() => document.querySelector('#cbOv .cbmod .big img').getAttribute('src')")
        pg.locator('#cbOv .cbmod [data-cb=discard]').click(); pg.wait_for_timeout(60); pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        check(hd == ['ターン 1|あなた=cb_fc_ka_s.webp|友達=cb_fc_mb_s.webp', 'ターン 2|あなた=cb_s1.webp|友達=cb_fc_3b_s.webp'] and big == 'cb_fc_3b_c.webp' and pg.evaluate(IMS)['dis'] == 'cb_fc_3b_s.webp' and gp.evaluate(IMS)['dis'] == 'cb_fc_3b_s.webp',
              f'捨て札：自分の カードは 自分の デザイン・友達の カードは 友達の デザイン（大きく 見ても 同じ）（{hd}）')
        ckey(gp, '7'); idle(pg); ckey(pg, '2'); idle(gp); idle(pg)
        pg.wait_for_function("() => { const g = document.querySelector('#cbOv .cbend .gift'); return CBApp._t.ended && g && g.textContent.length > 3; }", timeout=30000); gp.wait_for_function("() => CBApp._t.ended", timeout=30000); pg.wait_for_timeout(500)
        hg = pg.locator('#cbOv .cbend .gift').inner_text().replace('\n', ''); hm, gm = pg.evaluate(MST), gp.evaluate(MST)
        check(pg.evaluate("() => CBApp._t.view.res") == 'win' and hm['fr'] == 3 and hm['got']['fr'] == [3] and hm['live'] == '' and pg.evaluate("() => CBApp._t.state.coin") == 20 and '🎯ミッション達成！3連勝＋20枚' in hg and 'バトルコイン（今 20枚）' in hg
              and gm['fr'] == 0 and gm['live'] == '' and hm['cpu'] == 0,
              f'友達バトルで 3連勝目 → ミッション達成（＋20枚：コインなしの 部屋でも）・負けた ゲストの 友達バトルの 連勝は 0・コンピュータの 連勝は 変わらない（{hg[-40:]!r}）')
        shot(pg, 'cb_room_ms_end')
        pg.locator('#cbOv .cbend [data-cb=menu]').click(); pg.wait_for_timeout(150)      # ホストが メニューへ → ゲストには「ともだちが 部屋を 出たよ」の 窓
        gp.locator('#cbOv .cbmod [data-cb=menu]').click(); gp.wait_for_timeout(150)
        for q in (pg, gp): q.evaluate("() => { const T = CBApp._t; T.state.backs = []; T.state.faces = []; T.state.back = ''; T.state.face = {}; T.save(); T.menu(); }")
        print('■ 決戦宝石：友達との 対戦（第4.197版・まさちゃん 18:58「お互いに何の石を所有してるか見える」・20:21「お友達バトルは1試合で5個使える！」）')
        GEMQ = """() => { const g = document.querySelector('#cbOv .cbgem'), o = document.querySelector('#cbOv .cbopp .ogem'), R = e => { const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; };
          const gb = g.getBoundingClientRect(), cs = [...document.querySelectorAll('#cbOv .cbhand .cbc')];
          return { hid: g.hidden, rc: g.hidden ? null : R(g), hand: R(document.querySelector('#cbOv .cbhand')), act: R(document.querySelector('#cbOv .cbact')), vh: innerHeight, vw: innerWidth,
            gs: [...g.querySelectorAll('.g')].map(b => b.dataset.g + ':' + [...b.classList].filter(c => c !== 'g').join('.')).join(' '), case: g.querySelector('.case').getAttribute('src'),
            left: [...g.querySelectorAll('.g')].map(b => b.style.left), cb: cs.length ? Math.max(...cs.map(c => Math.round(c.getBoundingClientRect().bottom))) : 0,
            ins: [...g.querySelectorAll('.g')].every(b => { const a = b.getBoundingClientRect(); return a.width > 20 && a.left >= gb.left - 1 && a.right <= gb.right + 1 && a.top >= gb.top - 1 && a.bottom <= gb.bottom + 1; }),
            og: o.hidden ? null : o.textContent, ogi: o.hidden ? null : [...o.querySelectorAll('img')].map(i => i.dataset.g + (i.classList.contains('u') ? '*' : '')).join(','), ogl: o.getAttribute('aria-label') || '', cw: parseFloat(document.querySelector('#cbOv .cbhand').style.getPropertyValue('--cw')) || 0,
            tok: [...document.querySelectorAll('#cbOv .cbhand .cbc.tok')].map(c => c.dataset.ck + '×' + c.dataset.tok + '=' + c.querySelector('img').getAttribute('src')),
            otok: [...document.querySelectorAll('#cbOv .cbohand .cbc.tok')].map(c => c.querySelector('img').getAttribute('src')),
            fit: document.querySelector('#cbOv .cbgame').scrollHeight <= document.querySelector('#cbOv .cbgame').clientHeight + 1 }; }"""
        TOKV = "() => CBApp._t.view.my.hand.filter(c => c.tok).map(c => c.k + '×' + c.tok).join(',')"
        MYG = "() => { const g = CBApp._t.view.my.gem; return g ? { list: g.list.join(''), used: g.used.join(''), can: g.can.join(''), now: g.now } : null; }"
        def gtap(q, g): q.locator(f'#cbOv .cbgem .g[data-g="{g}"]').click(); q.wait_for_timeout(90)
        def guse(q, g):
            gtap(q, g); q.locator('#cbOv .cbmod.cbgemm [data-cb=gemgo]').click(); idle(q)
        def cset(q, k, tok=False):      # 手札の カードを セット（tok＝トークン）
            q.locator(f'#cbOv .cbhand .cbc{".tok" if tok else ":not(.tok)"}[data-ck="{k}"]').first.click(); q.wait_for_timeout(70)
            q.locator('#cbOv .cbmod [data-cb=set]').click(); idle(q)
        for q in (pg, gp): q.evaluate("() => { const T = CBApp._t; T.state.coin = 0; T.state.rg = { on: false }; T.state.ms = { m: T.msKey(), cpu: 0, fr: 0, got: { cpu: [], fr: [] }, live: '' }; }")
        pg.evaluate("() => { CBApp._opt = { hands: [['1', '2', '3', '6', '7'], ['1', '2', '4', '5', '6']], turns: 3 }; CBApp._think = null; }")
        pg.locator('#cbOv .cbmenu [data-cb=host]').click(); pg.wait_for_timeout(200)
        RG = "() => { const r = document.querySelector('#cbOv .cbroom'); return { gem: [...r.querySelectorAll('[data-cb=rgon]')].map(b => b.textContent + (b.classList.contains('on') ? '*' : '')).join(','), t: r.querySelector('.cbstk').textContent, gl5: [...r.querySelectorAll('.gl5 img')].map(i => i.getAttribute('src')), pick: r.querySelectorAll('.gp, [data-cb=rgg]').length, go: r.querySelector('[data-cb=stkgo]').textContent, sc: r.scrollHeight <= r.clientHeight + 1 }; }"
        r0 = pg.evaluate(RG)
        pg.locator('#cbOv .cbroom [data-cb=rgon][data-v="1"]').click(); pg.wait_for_timeout(60); r1 = pg.evaluate(RG)
        check(r0['gem'] == 'なし*,あり' and r0['gl5'] == [] and r1['gem'] == 'なし,あり*' and r1['gl5'] == [f'cb_gm_{g}.webp' for g in 'mk137'] and r1['pick'] == 0 and '2人とも 5つの 宝石を 使えるよ（1試合で 1つ 1回ずつ・おたがいに 見える）' in r1['t']
              and pg.evaluate("() => CBApp._t.state.rg") == {'on': True} and r1['sc'] and r1['go'] == '部屋を 作る',
              f'部屋の 決まりで 決戦宝石「あり」→ 2人とも 5つ（まさちゃん 20:21「お友達バトルは1試合で5個使える！」：持ち込む 宝石を えらぶ 所は ない）・あり／なしは 覚えて おく')
        shot(pg, 'cb_room_gem')
        pg.locator('#cbOv .cbroom [data-cb=stkgo]').click(); pg.wait_for_timeout(300)
        rr = pg.evaluate("() => ({ num: document.querySelector('#cbOv .cbroom .num').textContent, l: [...document.querySelectorAll('#cbOv .cbroom .cbstkl')].map(e => e.textContent) })")
        check(rr['l'] == ['決戦宝石 あり（2人とも 5つ）'], f'部屋番号の 下に「決戦宝石 あり（2人とも 5つ）」（{rr["l"]}）')
        gp.locator('#cbOv .cbmenu [data-cb=join]').click(); gp.wait_for_timeout(150)
        for d in rr['num']: gp.locator(f'#cbOv .cbkeys [data-key="{d}"]').click()
        gp.locator('#cbOv .cbkeys [data-key=go]').click()
        gp.wait_for_function("() => CBApp._t.screen === 'game' && document.querySelector('#cbOv .cbmod.cbjoin')", timeout=30000); gp.wait_for_timeout(150)
        JG = "() => { const m = document.querySelector('#cbOv .cbmod.cbjoin'); return m ? { t: m.textContent, coin: !!m.querySelector('.cbstkv'), gl5: m.querySelectorAll('.gl5 img').length, pick: m.querySelectorAll('.gp, [data-cb=jgem]').length, btns: [...m.querySelectorAll('.cbb')].map(b => b.textContent.trim()) } : null; }"
        j1 = gp.evaluate(JG)
        check(j1 and not j1['coin'] and '決戦宝石 あり' in j1['t'] and '💎' not in j1['t'] and '2人とも 5つの 宝石を 使えるよ（1試合で 1つ 1回ずつ・おたがいに 見える）' in j1['t'] and j1['gl5'] == 5 and j1['pick'] == 0 and j1['btns'] == ['やめる', '参加する'] and 'バトルコイン' not in j1['t'],
              f'入る 人：「この 部屋の 決まり」に「決戦宝石 あり」（2人とも 5つ・えらぶ 所は ない）・「やめる」「参加する」（{j1 and j1["btns"]}）')
        shot(gp, 'cb_join_gem')
        gp.locator('#cbOv .cbmod.cbjoin [data-cb=joinyes]').click()
        for q in (pg, gp): q.wait_for_function("() => CBApp._t.screen === 'game' && CBApp._t.view && CBApp._t.idle", timeout=30000)
        hq, gq, hv, gv = pg.evaluate(GEMQ), gp.evaluate(GEMQ), pg.evaluate(V), gp.evaluate(V)
        G5 = 'm:can k:can 1:can 3:can 7:can'
        check(all(x == list('mk137') for x in (hv['my']['gem']['list'], hv['op']['gem']['list'], gv['my']['gem']['list'], gv['op']['gem']['list'])) and hq['gs'] == G5 and gq['gs'] == G5
              and hq['left'] == ['7.99%', '25.44%', '42.13%', '59.1%', '75.93%'] and hq['ogi'] == 'm,k,1,3,7' and gq['ogi'] == 'm,k,1,3,7' and hq['ogl'].startswith('友達の 決戦宝石：のこり 5つ'),
              f'対戦：2人とも ケースに 5つ（{hq["gs"]}）・相手の 名前の よこに 相手の 5つ（{hq["ogi"]}）')
        shot(pg, 'cb_room_gem_game')
        said(pg); said(gp)
        guse(pg, '1'); idle(gp); gp.wait_for_timeout(200)
        hq, gq, sg = pg.evaluate(GEMQ), gp.evaluate(GEMQ), said(gp)
        check(hq['tok'] == ['1×2=cb_st1.webp'] and hq['gs'] == 'm:off k:off 1:used 3:off 7:off' and gq['otok'] == ['cb_st1.webp'] and gq['ogi'] == 'm,k,1*,3,7' and 'のこり 4つ' in gq['ogl']
              and any(x.startswith('ban:友達が 双炎のルビーを 使った！') for x in sg) and gq['gs'] == G5,
              f'ホストが 双炎のルビーを 使う → ゲストの 画面にも 知らせ・相手の 手札の トークンは 表で 見える・相手の 宝石は 1つ 暗く（{gq["ogi"]}・{sg}）・ゲストは 5つ まだ 使える')
        shot(gp, 'cb_room_gem_op')
        guse(gp, 'k'); idle(pg); pg.wait_for_timeout(200)
        hq, gq = pg.evaluate(GEMQ), gp.evaluate(GEMQ)
        check(gq['tok'] == ['k×1=cb_stk.webp'] and hq['otok'] == ['cb_stk.webp'] and hq['ogi'] == 'm,k*,1,3,7' and gq['gs'] == 'm:off k:used 1:off 3:off 7:off', '同じ ターンに ゲストも 日輪の黄金石（2人とも 1ターンに 1つ）')
        cset(pg, '2'); idle(gp); cset(gp, '1'); idle(pg)
        for q in (pg, gp): q.wait_for_function("() => CBApp._t.view && CBApp._t.view.turn === 2 && CBApp._t.idle", timeout=30000)
        hq, gq, sh = pg.evaluate(GEMQ), gp.evaluate(GEMQ), said(pg)
        check(hq['tok'] == [] and gq['otok'] == [] and hq['otok'] == [] and pg.evaluate(TOKV) == '' and any('消えたよ' in x for x in sh) and hq['gs'] == 'm:can k:can 1:used 3:can 7:can' and gq['gs'] == 'm:can k:used 1:can 3:can 7:can',
              f'使わなかった トークンは ターンの 終わりに 消える（相手の 画面からも）・2ターン目：使った 宝石の ほかは また 使える（{hq["gs"]}）')
        pg.locator('#cbOv .cbtop [data-cb=quit]').click(); pg.wait_for_timeout(80); pg.locator('#cbOv .cbmod [data-cb=quitgo]').click(); pg.wait_for_timeout(200)
        gp.wait_for_function("() => CBApp._t.modOn() && /部屋を 出たよ/.test(document.querySelector('#cbOv .cbmod').textContent)", timeout=20000)
        gp.locator('#cbOv .cbmod [data-cb=menu]').click(); gp.wait_for_timeout(150)
        if pg.evaluate("() => CBApp._t.screen") != 'menu': pg.evaluate("() => CBApp._t.menu()")

        print('■ 決戦宝石：使える とき・トークン（第4.197版・まさちゃん「１ターンにどれか1回しか使えない」「トークンを使用するとそのターンのみ」「1枚で2枚分として使用できるが、フィールドへセットや、手札効果で捨てる場合は1枚分」・19:03「手札が6枚以下の場合」）')
        def startG(h0, h1, turns=3, deck='', g0='mk137', g1=''):
            pg.evaluate("""([h0, h1, dk, tn, g0, g1]) => { CBApp._think = () => 1e9; CBApp._opt = { hands: [h0.split(''), h1.split('')], deck: dk ? dk.split('') : undefined, turns: tn, gems: [g0.split(''), g1.split('')], full: true }; }""", [h0, h1, deck, turns, g0, g1])
            if pg.evaluate("() => CBApp._t.screen") != 'menu': pg.evaluate("() => CBApp._t.menu()")
            pg.locator('#cbOv .cbmenu [data-cb=cpu]').click(); idle(pg); said(pg)
        # A：本番の 形（5ターン・手札 7枚）：1ターン目は 手札 7枚 → 使えない。セットして 6枚 → 2ターン目から 使える
        startG('1122377', '1233456', turns=5)
        a0 = pg.evaluate(GEMQ); m0 = pg.evaluate(MSG)
        gtap(pg, 'm'); s0 = said(pg)
        check(not a0['hid'] and a0['case'] == 'cb_gmcase.webp' and a0['gs'] == 'm:off k:off 1:off 3:off 7:off' and a0['ins'] and a0['og'] is None and '💎' not in m0 and pg.evaluate(MYG) == {'list': 'mk137', 'used': '', 'can': '', 'now': False}
              and any('手札が 6枚 以下の ときに 使えるよ' in x for x in s0) and not pg.evaluate("() => CBApp._t.modOn()"),
              f'決戦宝石 あり：手札の 下に 宝石ケース（5つ）・手札 7枚の あいだは 使えない（タップ →「手札が 6枚 以下の ときに 使えるよ」）（{a0["gs"]}・{s0}）')
        check(a0['rc'][1] >= a0['cb'] - 1 and a0['rc'][1] >= a0['hand'][3] - 1 and a0['rc'][3] <= a0['act'][1] + 1 and a0['act'][3] <= a0['vh'] and a0['rc'][0] >= 0 and a0['rc'][2] <= a0['vw'] and a0['cw'] >= 60 and a0['fit'],
              f'ケースは 手札の すぐ 下・下の ボタンの 上（まさちゃんの イメージ）・画面の 中・手札は 小さく しすぎない（カード 幅 {a0["cw"]}px）（手札 {a0["hand"]}・ケース {a0["rc"]}・ボタン {a0["act"]}）')
        shot(pg, 'cb_gem_t1')
        pg.set_viewport_size({'width': 375, 'height': 667}); pg.wait_for_timeout(300)
        a5 = pg.evaluate(GEMQ)
        check(a5['rc'][1] >= a5['cb'] - 1 and a5['rc'][3] <= a5['act'][1] + 1 and a5['act'][3] <= a5['vh'] and a5['cw'] >= 50 and a5['fit'],
              f'小さい 画面（375×667）でも 手札・ケース・ボタンが 重ならず 画面の 中（カード 幅 {a5["cw"]}px・手札の 下 {a5["cb"]}・ケース {a5["rc"]}・ボタン {a5["act"]}）')
        shot(pg, 'cb_gem_se')
        pg.set_viewport_size({'width': 390, 'height': 844}); pg.wait_for_timeout(300)
        cset(pg, '2'); opp(pg, {'t': 'set', 'k': 1})
        a1 = pg.evaluate(GEMQ); m1 = pg.evaluate(MSG); v1 = pg.evaluate(V)
        check(v1['turn'] == 2 and len(v1['my']['hand']) == 6 and a1['gs'] == 'm:can k:can 1:can 3:can 7:can' and 'セットの 前なら 決戦宝石を 使えるよ（下の ケース）' in m1 and '💎' not in m1,
              f'セットして 手札 6枚 → 2ターン目は 5つとも 使える（光る）・下の 字「セットの 前なら 決戦宝石を 使えるよ」（{a1["gs"]}）')
        shot(pg, 'cb_gem_t2')
        cset(pg, '1'); gtap(pg, 'k'); s1 = said(pg)
        check(any('セットする 前に 使えるよ' in x for x in s1) and pg.evaluate(GEMQ)['gs'] == 'm:off k:off 1:off 3:off 7:off', f'セットした あとは 使えない（「セットする 前に 使えるよ」）（{s1}）')
        # B：宝石 → トークン（この ターン だけ）・1ターンに 1つ・同じ 宝石は 1戦に 1回・トークン（2頭分）で 逆転勝利・トークンを セット・使わないと 消える
        startG('12367', 'k2346')
        b0 = pg.evaluate(GEMQ)
        check(b0['gs'] == 'm:can k:can 1:can 3:can 7:can', f'手札 5枚（3ターンの 形）：1ターン目から 使える（{b0["gs"]}）')
        gtap(pg, '1')
        gm = pg.evaluate("() => { const m = document.querySelector('#cbOv .cbmod.cbgemm'); return m ? { h: m.querySelector('h3').textContent, im: [...m.querySelectorAll('img')].map(i => i.getAttribute('src')), t: m.querySelector('p').textContent, b: [...m.querySelectorAll('.cbb')].map(x => x.textContent.trim()) } : null; }")
        check(gm and gm['h'] == '双炎のルビー' and gm['im'] == ['cb_gm_1.webp', 'cb_ct1.webp'] and gm['t'].startswith('1トークン（1枚で 2頭分）が 手札に 1枚 来るよ') and 'この ターン だけ' in gm['t'] and gm['b'] == ['使わない', '使う'],
              f'宝石を タップ →「双炎のルビー」の 窓（宝石 ▶ 1トークンの カード・「使わない」「使う」）（{gm}）')
        shot(pg, 'cb_gem_ask')
        pg.locator('#cbOv .cbmod.cbgemm [data-cb=gemgo]').click(); idle(pg)
        b1 = pg.evaluate(GEMQ); s2 = said(pg)
        check(pg.evaluate(TOKV) == '1×2' and b1['tok'] == ['1×2=cb_st1.webp'] and b1['gs'] == 'm:off k:off 1:used 3:off 7:off' and pg.evaluate(MYG)['now'] is True and any(x.startswith('ban:双炎のルビー！') and '1トークン（1枚で 2頭分）が 手札に 来たよ' in x for x in s2),
              f'「使う」→ 1トークン（2頭分）が 手札に・使った 宝石は 暗く・ほかの 宝石も この ターンは 使えない（{b1["gs"]}・{b1["tok"]}）')
        shot(pg, 'cb_gem_token')
        gtap(pg, 'k'); s3 = said(pg); gtap(pg, '1'); s4 = said(pg)
        check(any('決戦宝石は 1ターンに 1つ までだよ' in x for x in s3) and any('この 試合では もう 使ったよ' in x for x in s4), f'1ターンに 1つ まで・同じ 宝石は 1戦に 1回（{s3}・{s4}）')
        pg.locator('#cbOv .cbhand .cbc.tok').click(); pg.wait_for_timeout(80)
        tm = pg.evaluate("() => { const m = document.querySelector('#cbOv .cbmod'); return { im: m.querySelector('.big img').getAttribute('src'), t: m.textContent }; }")
        check(tm['im'] == 'cb_ct1.webp' and '1トークン（1枚で 2頭分）：この ターン だけ（使わないと ターンの 終わりに 消えるよ）' in tm['t'] and 'この カードを セットする' in tm['t'], f'トークンを タップ → 大きい 絵・「この ターン だけ」（{tm["t"][:60]!r}）')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        cset(pg, '1'); opp(pg, {'t': 'set', 'k': 'k'})
        aq = pg.evaluate(ASKQ)
        check(aq and aq['q'] == '1 の 効果を 使う？' and aq['text'] == '場の 1 と 1トークン（2頭分）で 3枚 ぶん。トークンを 捨てると、神様馬に 勝てるよ' and aq['img'] == 'cb_ct1.webp',
              f'1 を セット・相手は 神様馬 → 逆転の チャンス（場の 1 ＋ 1トークン 2頭分 ＝ 3枚 ぶん）（{aq and aq["text"]}）')
        shot(pg, 'cb_gem_rev')
        pg.locator('#cbOv .cbmod.cbask [data-cb=revyes]').click(); idle(pg)
        v1 = pg.evaluate(V); s5 = said(pg)
        check(v1['my']['wins'] == 1 and pg.evaluate(TOKV) == '' and any('トークンを 捨てて、神様馬に 勝ち！' in x for x in s5 if x.startswith('use:')) and not any('消えたよ' in x for x in s5) and v1['turn'] == 2
              and any(d.get('tok') == 2 and d['k'] == '1' and d['mine'] for d in v1['discard']),
              f'使う → トークンを 捨てて 逆転勝利（捨てた トークンは 捨て札に・使った トークンは「消えた」と 言わない）（{[x for x in s5 if x.startswith("use:")]}）')
        guse(pg, 'k')
        check(pg.evaluate(TOKV) == 'k×1' and pg.evaluate(GEMQ)['gs'] == 'm:off k:used 1:used 3:off 7:off', f'2ターン目：日輪の黄金石 → 神様馬トークン（{pg.evaluate(GEMQ)["gs"]}）')
        cset(pg, 'k', tok=True)
        ms = pg.evaluate(SLOT); mt = pg.evaluate("() => !!document.querySelector('#cbOv .cbslot.my .cbc.tok')")
        opp(pg, {'t': 'set', 'k': 2})
        v2 = pg.evaluate(V)
        check(ms.split(' ')[1].startswith('b[') and mt and v2['my']['wins'] == 2 and v2['last']['c'] == ['k', '2'] and pg.evaluate(TOKV) == '',
              f'神様馬トークンを セット（伏せて：{ms}）→ オープン：神様馬 と 同じ 強さで 勝ち（{v2["last"]}）')
        pg.wait_for_function("() => document.querySelector('#cbOv .cbmod.cbask')", timeout=20000)
        aq2 = pg.evaluate(ASKQ)
        check(aq2 and aq2['q'] == '神様馬トークンの 効果を 使う？' and aq2['img'] == 'cb_ctk.webp', f'神様馬トークンで 勝った → 次の ターンの 始めに 神様馬トークンの 効果（第4.201版：絵も トークン）（{aq2 and [aq2["q"], aq2["img"]]}）')
        pg.locator('#cbOv .cbmod.cbask [data-cb=kskip]').click(); idle(pg)
        guse(pg, 'm'); b3 = pg.evaluate(GEMQ)
        check(pg.evaluate(TOKV) == 'm×1' and b3['gs'] == 'm:used k:used 1:used 3:off 7:off' and b3['tok'] == ['m×1=cb_stm.webp'], f'3ターン目：幻影のアメジスト → 幻の馬トークン（{b3["gs"]}）')
        cset(pg, '7'); opp(pg, {'t': 'set', 'k': 3})
        pg.wait_for_function("() => CBApp._t.ended", timeout=30000); idle(pg); s7 = said(pg); v3 = pg.evaluate(V)
        check(v3['res'] == 'win' and pg.evaluate(TOKV) == '' and any('トークンは この ターン だけ' in x and '消えたよ' in x for x in s7),
              f'使わなかった トークンは ターンの 終わりに 消える（「トークンは この ターン だけ… 消えたよ」）（{[x for x in s7 if "消えた" in x]}）')
        # C：7トークン（3頭分）で 7 の 効果（第4.199版・まさちゃん 22:01：7トークンを 見せて 捨てる → 山札から 3枚 引く）→ 手札 7枚（使えない）・3トークン（2頭分）＋ 3 で 3 の 交換（第4.202版：どちらも セットの 前）
        startG('12345', '2356m', deck='124')
        guse(pg, '7')
        aq = pg.evaluate(ASKQ)
        check(aq and aq['head'] == '7 が 3枚 ぶん！' and aq['q'] == '7 の 効果を 使う？' and aq['text'] == 'セットの 前に 使えるよ。7トークン（3頭分）を 見せて 捨てて、山札から 3枚 引けるよ（トークンは 山札に 戻せないので 捨てる）' and aq['img'] == 'cb_ct7.webp' and pg.evaluate(V)['phase'] == 'set',
              f'7トークン（3頭分）＝ 7 が 3枚 → すぐ（セットの 前に）7 の 効果を 聞く（{aq and [aq["head"], aq["text"]]}）')
        peek(pg); mb = pg.evaluate(MSG)
        check(mb == 'セットする カードを 選んでね（カードを タップ）\n7トークン！ セットの 前なら 山札から 3枚 引けるよ' and acts(pg) == ['使わない', '7 の 効果を 使う'], f'窓を 下げた ときの 下の 字と ボタンも トークン（{mb!r}・{acts(pg)}）')
        pg.evaluate("""() => { window.__t7 = []; const o = new MutationObserver(() => { const m = document.querySelector('#cbOv .cbmod.on.cbopen'); if (m && !window.__t7.some(x => x.t === m.innerText)) window.__t7.push({ t: m.innerText, img: [...m.querySelectorAll('.three img')].map(i => i.getAttribute('src')) }); });
          o.observe(document.querySelector('#cbOv'), { subtree: true, childList: true, attributes: true, attributeFilter: ['class'] }); window.__t7o = o; }""")
        pg.locator('#cbOv .cbact [data-cb=p7yes]').click(); idle(pg)
        s8 = said(pg); c1 = pg.evaluate(GEMQ); v4 = pg.evaluate(V); t7m = pg.evaluate("() => { window.__t7o.disconnect(); return window.__t7; }"); h8 = pg.evaluate(HAND)
        check(pg.evaluate(TOKV) == '' and h8 == '11223445' and any(x.startswith('use:') and '3枚 引く' in x and '7トークン（3頭分）を 見せて 捨てて、山札から 3枚 引くよ' in x for x in s8) and any('7トークン（3頭分）を 捨てて、山札から 3枚 引いたよ' in x for x in s8)
              and v4['turn'] == 1 and v4['phase'] == 'set' and v4['can']['set'] and c1['gs'] == 'm:off k:off 1:off 3:off 7:used' and asked(pg) is None,
              f'使う → 7トークンを 捨てて 山札から 3枚 引いた（まだ セットの 前：手札 {h8} の 8枚から セット）（{c1["gs"]}）')
        t7m = [x for x in t7m if x['t'].startswith('7 の 効果！')]      # オープンの 窓（同じ cbopen）は 数えない
        check(len(t7m) == 1 and t7m[0]['img'] == ['cb_st7.webp'] and '7トークン（3頭分）を 見せて 捨てたよ' in t7m[0]['t'] and '山札から 3枚 引くよ' in t7m[0]['t'],
              f'7トークン 1枚を 見せる 窓（「7 の 効果！」・7トークンの 絵 1枚・「7トークン（3頭分）を 見せて 捨てたよ／山札から 3枚 引くよ」）（{t7m}）')
        cset(pg, '1'); opp(pg, {'t': 'set', 'k': 2}); v4 = pg.evaluate(V)
        check(v4['turn'] == 2 and pg.evaluate(HAND) == '1223445', f'その あと 1 を セット → 2ターン目（手札 7枚：{pg.evaluate(HAND)}）')
        pg.locator('#cbOv [data-cb=discard]').click(); pg.wait_for_timeout(100)
        dt7 = pg.evaluate(DM); pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        check(dt7['h'] == '捨て札（3枚）' and 'ターン 1|あなたの 7 の 効果=t7' in dt7['effs'] and v4['my']['hand'] and not any(c.get('tok') for c in v4['my']['hand']),
              f'捨て札の 窓：「あなたの 7 の 効果」に 捨てた 7トークン（山札には 戻らない）（{dt7["h"]}・{dt7["effs"]}）')
        gtap(pg, 'm'); s9 = said(pg)
        check(any('手札が 6枚 以下の ときに 使えるよ' in x for x in s9), '手札 7枚：「手札が 6枚 以下の ときに 使えるよ」')
        cset(pg, '2'); opp(pg, {'t': 'set', 'k': 3})
        c2 = pg.evaluate(GEMQ)
        check(pg.evaluate(V)['turn'] == 3 and c2['gs'] == 'm:can k:can 1:can 3:can 7:used', f'3ターン目：手札 6枚 → また 使える（{c2["gs"]}）')
        opp(pg, {'t': 'set', 'k': 6}); guse(pg, '3')
        aq = pg.evaluate(ASKQ)
        check(aq and aq['head'] == '3 が 3枚 ぶん！' and aq['q'] == '3 の 効果を 使う？' and aq['text'] == 'セットの 前に 使えるよ。3トークン（2頭分）と 3 で 3枚 ぶん 見せて、本物の 3 と 相手の 手札の 1枚（見えて いる カードも 選べる）を 交換できるよ' and aq['img'] == 'cb_ct3.webp',
              f'3トークン（2頭分）＋ 3 ＝ 3 が 3枚 → すぐ（セットの 前に）3 の 効果を 聞く（{aq and [aq["head"], aq["text"]]}）')
        h3 = pg.evaluate(HAND)
        pg.evaluate("() => { window.__three = null; if (window.__mo3x) window.__mo3x.disconnect(); const mo = new MutationObserver(() => { const m = document.querySelector('#cbOv .cbmod.cbopen .three'); if (m && !window.__three) window.__three = { im: [...m.querySelectorAll('img')].map(i => i.getAttribute('src')), t: m.parentNode.querySelector('p').textContent }; }); mo.observe(document.getElementById('cbOv'), { childList: true, subtree: true }); window.__mo3x = mo; }")
        pg.locator('#cbOv .cbmod.cbask [data-cb=p3yes]').click(); pg.wait_for_timeout(150)
        p3t = pg.evaluate("() => { const m = document.querySelector('#cbOv .cbmod.on.cbx3'); return m ? m.querySelector('p').innerText : ''; }")
        check('3トークン（2頭分）と 3 を 見せて、本物の 3 を 1枚 わたすよ' in p3t and pg.locator('#cbOv .cbmod.cbx3 .pick .cbc[data-cb=pick]').count() >= 1, f'3トークンの ときも 裏の カードを 選ぶ 窓（{p3t[:40]!r}）')
        pg.locator('#cbOv .cbmod.cbx3 .pick .cbc[data-cb=pick]').first.click(); idle(pg); h3b = pg.evaluate(HAND)
        cset(pg, '1')
        pg.wait_for_function("() => CBApp._t.ended", timeout=30000); idle(pg); s10 = said(pg)
        th = pg.evaluate("() => { if (window.__mo3x) window.__mo3x.disconnect(); return window.__three || { im: [], t: '' }; }")
        check(sorted(th['im']) == ['cb_s3.webp', 'cb_st3.webp'] and '3トークン（2頭分）と 3 で 3枚 ぶん 見せたよ' in th['t'] and '3' not in pg.evaluate(HAND) and pg.evaluate(TOKV) == '' and any('消えたよ' in x for x in s10),
              f'使う → 見せるのは 3トークンと 3（{th["im"]}）・わたすのは 本物の 3（手札 {h3} → {h3b} → セット → {pg.evaluate(HAND)}）・トークンは ターンの 終わりに 消える')
        pg.evaluate("() => CBApp._t.menu()"); pg.wait_for_timeout(150)
        # E：神様馬トークン・幻の馬トークンで 勝った → 次の ターンの 効果も トークン（第4.201版・まさちゃん 11/18 23:23「トークンで勝ったならトークンにして！」）
        print('■ 決戦宝石：神様馬トークン・幻の馬トークンで 勝った ときの 効果は トークンの 絵と 名前（第4.201版）')
        pg.evaluate("""() => { window.__usei = []; if (window.__useo) window.__useo.disconnect(); const e = document.querySelector('#cbOv .cbuse');
          window.__useo = new MutationObserver(() => { if (!e.classList.contains('on')) return; const s = [...e.querySelectorAll('img')].map(i => i.getAttribute('src')).join(',') + '|' + e.textContent; if (window.__usei[window.__usei.length - 1] !== s) window.__usei.push(s); });
          window.__useo.observe(e, { childList: true, subtree: true, attributes: true, attributeFilter: ['class'] }); }""")
        USEI = "() => { const a = window.__usei.slice(); window.__usei.length = 0; return a; }"
        BAR = """() => { const a = document.querySelector('#cbOv .cbact'), r = a.getBoundingClientRect(); return [...a.querySelectorAll('.cbb')].map(b => { const q = b.getBoundingClientRect(); return { t: b.textContent.trim(), fit: b.scrollWidth <= b.clientWidth + 1 && q.left >= r.left - 1 && q.right <= r.right + 1 && q.right <= innerWidth }; }); }"""
        startG('12345', '23456', deck='1234')
        guse(pg, 'k'); cset(pg, 'k', tok=True); said(pg); opp(pg, {'t': 'set', 'k': 2})
        pg.wait_for_function("() => document.querySelector('#cbOv .cbmod.cbask')", timeout=20000)
        ek = pg.evaluate(ASKQ); se1 = said(pg)
        check(ek and ek['head'] == '神様馬トークンで 勝った！' and ek['q'] == '神様馬トークンの 効果を 使う？' and ek['text'] == '相手の 手札を 1枚 見られるよ' and ek['img'] == 'cb_ctk.webp'
              and any(x.startswith('ban:神様馬トークンの 効果') and '使うか 選んでね' in x for x in se1) and not any(x.startswith('ban:神様馬の 効果') for x in se1),
              f'神様馬トークンで 勝った → 2ターン目の 始めの 窓は 神様馬トークンの 絵・「神様馬トークンで 勝った！／神様馬トークンの 効果を 使う？」・帯も「神様馬トークンの 効果」（{ek and [ek["head"], ek["q"], ek["img"]]}）')
        shot(pg, 'cb_tok_kwin')
        peek(pg); mk = pg.evaluate(MSG); bk = pg.evaluate(BAR)
        pg.set_viewport_size({'width': 375, 'height': 667}); pg.wait_for_timeout(300); bk5 = pg.evaluate(BAR)
        pg.set_viewport_size({'width': 390, 'height': 844}); pg.wait_for_timeout(300)
        check(mk == '神様馬トークンで 勝った！ 効果を 使う？\n相手の 手札を 1枚 見られるよ' and [b['t'] for b in bk] == ['使わない', '神様馬トークンの 効果を 使う'] and all(b['fit'] for b in bk + bk5),
              f'窓を 下げた ときの 下の 字・ボタンも「神様馬トークン」（ボタンは はみ出ない：390・375 幅）（{mk!r}・{bk5}）')
        pg.locator('#cbOv [data-cb=kgo]').click(); pg.wait_for_timeout(80)
        pk = pg.evaluate("() => document.querySelector('#cbOv .cbmod h3').textContent")
        pg.evaluate("() => { window.__seen = []; }"); pg.evaluate(USEI)
        pg.locator('#cbOv .cbmod .pick .cbc').first.click(); idle(pg)
        seen = pg.evaluate("() => window.__seen"); uk = pg.evaluate(USEI); v5 = pg.evaluate(V)
        check(pk == '神様馬トークンの 効果' and any(x.startswith('神様馬トークンの 効果|') for x in seen) and len(uk) == 1 and uk[0].startswith('cb_stk.webp|あなたが 使った！神様馬トークンの 効果手札を 1枚 見る前の ターンに 神様馬トークンで 勝った ので、')
              and len([c for c in v5['op']['hand'] if c['k']]) == 1 and v5['turn'] == 2 and v5['phase'] == 'set',
              f'「使う」→ 選ぶ 窓「神様馬トークンの 効果」→ 効果の 札は 神様馬トークンの 絵・「神様馬トークンの 効果」→ 見た 窓も（{pk}・{uk}・{seen}）')
        guse(pg, 'm'); cset(pg, 'm', tok=True); said(pg); opp(pg, {'t': 'set', 'k': 3})
        pg.wait_for_function("() => document.querySelector('#cbOv .cbmod.cbask')", timeout=20000)
        em = pg.evaluate(ASKQ); se2 = said(pg)
        check(em and em['head'] == '幻の馬トークンで 勝った！' and em['q'] == '幻の馬トークンの 効果を 使う？' and em['text'] == '手札を 2枚 捨てて、山札から 2枚 引けるよ' and em['img'] == 'cb_ctm.webp'
              and any(x.startswith('ban:幻の馬トークンの 効果') for x in se2) and pg.evaluate(V)['turn'] == 3,
              f'幻の馬トークンで 勝った → 3ターン目の 始めの 窓は 幻の馬トークンの 絵・「幻の馬トークンで 勝った！／幻の馬トークンの 効果を 使う？」（{em and [em["head"], em["q"], em["img"]]}）')
        shot(pg, 'cb_tok_mwin')
        peek(pg); mm = pg.evaluate(MSG); am = acts(pg)
        check(mm == '幻の馬トークンで 勝った！ 効果を 使う？\n手札を 2枚 捨てて、山札から 2枚 引けるよ' and am == ['使わない', '幻の馬トークンの 効果を 使う'], f'下の 字・ボタンも「幻の馬トークン」（{mm!r}・{am}）')
        pg.locator('#cbOv [data-cb=mpick]').click(); pg.wait_for_timeout(80)
        hm = pg.evaluate(HAND); tap(pg, hm[0]); tap(pg, hm[1]); pg.evaluate(USEI); said(pg)
        pg.locator('#cbOv .cbact [data-cb=mgo]').click(); idle(pg)
        um = pg.evaluate(USEI); s11 = said(pg)
        pg.locator('#cbOv [data-cb=discard]').click(); pg.wait_for_timeout(100)
        dm2 = pg.evaluate(DM); pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(60)
        check(len(um) == 1 and um[0].startswith('cb_stm.webp|あなたが 使った！幻の馬トークンの 効果捨てて 引き直す前の ターンに 幻の馬トークンで 勝った ので、') and any(x.startswith('toast:幻の馬トークンの 効果！') for x in s11)
              and f'ターン 3始め|あなたの 幻の馬トークンの 効果={hm[0]}{hm[1]}' in dm2['effs'],
              f'2枚 捨てて 引いた：効果の 札は 幻の馬トークンの 絵・知らせ・捨て札の 窓も「あなたの 幻の馬トークンの 効果」（{um}・{dm2["effs"]}）')
        # 相手が 神様馬トークンで 勝った（友だちとの 対戦で 起きる 形：ここでは コンピュータの 席に 宝石を 持たせて テストが 手を 打つ）
        startG('12345', '23456', deck='1234', g1='mk137')
        opp(pg, {'t': 'gem', 'g': 'k'}); cset(pg, '3'); said(pg); opp(pg, {'t': 'set', 'k': 'k'})
        so = said(pg); mo = pg.evaluate(MSG)
        check(pg.evaluate(V)['pend'] == {'type': 'k', 'mine': False, 'tok': 1} and any(x.startswith('ban:神様馬トークンの 効果') and 'コンピュータが 使うか 選ぶよ' in x for x in so) and mo == 'コンピュータが 神様馬トークンの 効果を 使うか 選んで いるよ…',
              f'相手が 神様馬トークンで 勝った → 帯「神様馬トークンの 効果」・下の 字「コンピュータが 神様馬トークンの 効果を 使うか 選んで いるよ…」（{mo!r}）')
        pg.evaluate(USEI); opp(pg, {'t': 'k', 'pickk': 2}); uo = pg.evaluate(USEI); so2 = said(pg)
        check(len(uo) == 1 and uo[0].startswith('cb_stk.webp|コンピュータが 使った！神様馬トークンの 効果手札を 1枚 見る前の ターンに 神様馬トークンで 勝った ので、あなたの 手札を 1枚 見るよ')
              and any('コンピュータが 神様馬トークンの 効果で、' in x and 'あなたの 2 を 見たよ' in x for x in so2),
              f'相手が 神様馬トークンの 効果を 使った：効果の 札は 神様馬トークンの 絵・知らせも「神様馬トークンの 効果で」（{uo}）')
        pg.evaluate("() => { if (window.__useo) window.__useo.disconnect(); CBApp._t.menu(); }"); pg.wait_for_timeout(150)
        # D：決戦宝石 なし の いつもの 対戦：ケースは 出ない（画面も 前と 同じ）
        start(pg, '12345', '23456')
        d0 = pg.evaluate(GEMQ)
        check(d0['hid'] and d0['og'] is None and pg.evaluate("() => CBApp._t.view.my.gem") is None and '💎' not in pg.evaluate(MSG), '決戦宝石 なし（いつもの 対戦）：ケースは 出ない・下の 字も 前と 同じ')
        pg.evaluate("() => CBApp._t.menu()"); pg.wait_for_timeout(150)
        print('■ 抜け穴（第4.211版・まさちゃん 11/22 21:36「不正にポイントやバトルコイン、お世話トークンを手に入れる抜け穴は無いか全部細かく徹底的に確認して！」）')
        # ① 第4.212版：勝った ときの お世話トークンは 廃止 → わたす 口（pay・rewardFor・REWARD・TCGift）と、まだ わたして いない 数（owe）は もう ない。
        #    前の 版の 保存（owe が 残って いる）を 読んでも 何も わたさない（消える）
        py = pg.evaluate("""() => {
          const T = CBApp._t, s0 = localStorage.getItem('tengel.cb'), s = JSON.parse(s0); s.owe = 7; localStorage.setItem('tengel.cb', JSON.stringify(s)); T.load();
          const out = { pay: typeof T.pay, rf: typeof CBApp.rewardFor, rw: typeof CBApp.REWARD, gift: typeof window.TCGift, busy: typeof window.__cbPayBusy, owe: 'owe' in T.state, tk: [1, 2, 3, 5, 6, 9, 10, 15, 30].map(n => CBApp.tkBonus(n)), TK: JSON.stringify(CBApp.TK_BONUS) };
          T.save(); out.saved = 'owe' in JSON.parse(localStorage.getItem('tengel.cb')); T.menu(); out.tc = !!window.TCApp; return out; }""")
        check(py == {'pay': 'undefined', 'rf': 'undefined', 'rw': 'undefined', 'gift': 'undefined', 'busy': 'undefined', 'owe': False, 'tk': [0, 0, 1, 2, 1, 1, 2, 3, 3], 'TK': '[[3,1],[5,2]]', 'saved': False, 'tc': False},
              f'お世話トークンを わたす 口は もう ない（pay・rewardFor・REWARD・TCGift）・前の 版の「まだ わたして いない 数」は 読んだ ときに 消える・調査隊切符の 連勝ボーナスは 3連勝 ごと 1枚・5連勝 ごと 2枚（15連勝は 3枚）（{py}）')
        # ② にせものの ホスト（本物の アプリで ない 相手）：「配った → あなたの 勝ち」を 50回
        FKV = """{ v: 4, me: 1, turn: 1, turns: 5, phase: 'set', deckN: 20, rv: false, discard: [], my: { hand: [{ u: 1, k: '1', seen: false }, { u: 2, k: '2', seen: false }, { u: 3, k: '3', seen: false }, { u: 4, k: '4', seen: false }], set: null, wins: 0, gem: null },
          op: { hand: [{ u: 9, k: null }, { u: 10, k: null }], set: null, wins: 0, gem: null }, can: { set: true, x7r: false, x7: false, x3: false, x3p: [], gem: [], eff: null, six: null }, pend: null, wait: false, last: null, res: null, early: 0 }"""
        FK0 = """() => { const T = CBApp._t, st = T.state; return { win: st.win, lose: st.lose, draw: st.draw, streak: st.streak, owe: st.owe, coin: st.coin, fr: st.ms.fr, got: st.ms.got.fr.length, stake: st.stake, live: st.ms.live }; }"""
        pg.evaluate("() => { const T = CBApp._t, st = T.state; st.coin = 40; st.owe = 0; st.stake = null; st.ms.fr = 2; st.ms.got.fr = []; T.save(); CBApp._opt = null; CBApp._rng = null; T.menu(); }"); pg.wait_for_timeout(200)
        f0 = pg.evaluate(FK0)
        fk = pg.evaluate("""async (VS) => {
          const T = CBApp._t, wait = ms => new Promise(r => setTimeout(r, ms)), VIEW = () => (0, eval)('(' + VS + ')');
          const link = { sent: [], send(t) { this.sent.push(JSON.parse(t)); }, onText: null, onLost: null, close() { this.closed = true; } };
          const say = o => { if (link.onText) link.onText(JSON.stringify(o)); };
          T.start(CBNet.guest(link)); await wait(60);
          say({ t: 'hello', v: CBNet.PROTO, stake: { e: 0, w: 0 } }); await wait(120);
          const joined = link.sent.some(x => x.t === 'join');
          for (let i = 0; i < 50; i++) say({ t: 'up', n: i + 1, ev: [{ e: 'deal' }, { e: 'end', wins: [3, 0], res: 'win' }], view: Object.assign(VIEW(), { phase: 'end', res: 'win' }) });
          await wait(400);
          const m = document.querySelector('#cbOv .cbmod');
          return { joined: joined, min: CBNet._t.minSets, modal: m ? m.textContent.replace(/\\s+/g, ' ') : '', match: !!T.match, closed: !!link.closed }; }""", FKV)
        f1 = pg.evaluate(FK0)
        check(fk['joined'] and fk['min'] == 3 and f1 == f0 and not fk['match'] and fk['closed'] and '正しくない 知らせ' in fk['modal'] and '勝ち負けに 数えない' not in fk['modal'].replace('（この 対戦は 勝ち負けに 数えないよ）', ''),
              f'にせものの ホストが「配った → あなたの 勝ち」を 50回 送っても、勝ち・連勝・お世話トークン・バトルコイン・ミッションは ふえない（{f1}）・「{fk["modal"][:44]}…」で 終わる')
        pg.locator('#cbOv .cbmod [data-cb=menu]').click(); pg.wait_for_timeout(200)
        # ③ 参加コインの ある 部屋：にせものの ホストが 999枚の 部屋を 作る → 受けとる 決まりは 100枚 まで・足りない（40枚）ので 入れない →「参加する」を 待たずに 配って 切っても 何も ふえない
        fs = pg.evaluate("""async (VS) => {
          const T = CBApp._t, st = T.state, wait = ms => new Promise(r => setTimeout(r, ms)), VIEW = () => (0, eval)('(' + VS + ')');
          const link = { sent: [], send(t) { this.sent.push(JSON.parse(t)); }, onText: null, onLost: null, close() { this.closed = true; } };
          const say = o => { if (link.onText) link.onText(JSON.stringify(o)); };
          T.start(CBNet.guest(link)); await wait(60);
          say({ t: 'hello', v: CBNet.PROTO, stake: { e: 999, w: 1998 } }); await wait(150);
          const ask = document.querySelector('#cbOv .cbjoin'), askT = ask ? ask.textContent.replace(/\\s+/g, ' ') : '', stk = JSON.stringify(T.match.stake), yes = !!document.querySelector('#cbOv .cbjoin [data-cb=joinyes]');
          say({ t: 'up', n: 1, ev: [{ e: 'deal' }], view: VIEW() }); await wait(500);      //「参加する」を 待たずに 配る
          if (link.onLost) link.onLost(); await wait(200);                                    // すぐ 切る
          const m = document.querySelector('#cbOv .cbmod');
          return { askT: askT, stk: stk, yes: yes, joined: link.sent.filter(x => x.t === 'join').length, modal: m ? m.textContent.replace(/\\s+/g, ' ') : '', match: !!T.match }; }""", FKV)
        f2 = pg.evaluate(FK0)
        check(fs['stk'] == '{"e":100,"w":200}' and '参加コイン 100枚' in fs['askT'] and '勝者 200枚' in fs['askT'] and '足りない' in fs['askT'] and not fs['yes'] and fs['joined'] == 0,
              f'にせものの ホストが 参加コイン 999枚の 部屋を 作っても、受けとる 決まりは 100枚 まで（{fs["stk"]}）・足りなければ「参加する」は 出ない（40枚：「{fs["askT"][-32:]}」）')
        check(f2 == f0 and not fs['match'] and '正しくない 知らせ' in fs['modal'] and '戻ったよ' not in fs['modal'] and 'もらったよ' not in fs['modal'],
              f'「参加する」を 待たずに 配って すぐ 切っても、出して いない 参加コインは「戻って」こない（バトルコイン {f2["coin"]}枚の まま・前は 100枚 ふえた）')
        pg.locator('#cbOv .cbmod [data-cb=menu]').click(); pg.wait_for_timeout(200)
        fs2 = pg.evaluate("""async (VS) => {
          const T = CBApp._t, st = T.state, wait = ms => new Promise(r => setTimeout(r, ms)), VIEW = () => (0, eval)('(' + VS + ')'), until = async f => { for (let i = 0; i < 200 && !f(); i++) await wait(50); return f(); };
          const link = { sent: [], send(t) { this.sent.push(JSON.parse(t)); }, onText: null, onLost: null, close() { this.closed = true; } };
          const say = o => { if (link.onText) link.onText(JSON.stringify(o)); };
          T.start(CBNet.guest(link)); await wait(60);
          say({ t: 'hello', v: CBNet.PROTO, stake: { e: 30, w: 60 } }); await wait(150);
          const yes = document.querySelector('#cbOv .cbjoin [data-cb=joinyes]'); if (yes) yes.click(); await wait(150);
          say({ t: 'up', n: 1, ev: [{ e: 'deal' }], view: VIEW() });
          await until(() => !!st.stake && T.idle); const paid = { coin: st.coin, stake: st.stake && st.stake.e, live: st.ms.live };
          for (let i = 0; i < 2; i++) { CBApp._t.match.act({ t: 'set', u: i + 1 }); await wait(30); }      // 自分の セットは 2回 だけ
          say({ t: 'up', n: 2, ev: [{ e: 'end', wins: [3, 0], res: 'win' }], view: Object.assign(VIEW(), { phase: 'end', res: 'win' }) }); await wait(400);
          const m = document.querySelector('#cbOv .cbmod');
          return { paid: paid, modal: m ? m.textContent.replace(/\\s+/g, ' ') : '', sets: link.sent.filter(x => x.t === 'act' && x.a.t === 'set').length, joined: link.sent.filter(x => x.t === 'join').map(x => x.stake) }; }""", FKV)
        f3 = pg.evaluate(FK0)
        check(fs2['joined'] == [{'e': 30, 'w': 60}] and fs2['paid'] == {'coin': 10, 'stake': 30, 'live': 'fr'} and fs2['sets'] == 2 and f3 == f0 and '正しくない 知らせ' in fs2['modal'] and '参加コイン 30枚は 戻ったよ' in fs2['modal'],
              f'参加コイン 30枚の 部屋：配られて 30枚 出した（のこり {fs2["paid"]["coin"]}枚）→ セット 2回で「あなたの 勝ち」が 届いても 受けとらない・勝者の 60枚は もらえない・出した 30枚は 戻る（{f3["coin"]}枚）・勝ち負けも そのまま')
        pg.locator('#cbOv .cbmod [data-cb=menu]').click(); pg.wait_for_timeout(200)
        # ④ タグに なる 字の 入った 知らせ：画面には 出ない
        fx = pg.evaluate("""async (VS) => {
          const T = CBApp._t, wait = ms => new Promise(r => setTimeout(r, ms)), VIEW = () => (0, eval)('(' + VS + ')');
          const link = { sent: [], send(t) { this.sent.push(JSON.parse(t)); }, onText: null, onLost: null, close() { this.closed = true; } };
          const say = o => { if (link.onText) link.onText(JSON.stringify(o)); };
          T.start(CBNet.guest(link)); await wait(60);
          say({ t: 'hello', v: CBNet.PROTO, stake: { e: 0, w: 0 } }); await wait(120);
          const v = VIEW(); v.my.hand[0].k = '"><i data-xss="1">X</i>'; v.phase = '<b data-xss="2">';
          say({ t: 'up', n: 1, ev: [{ e: 'deal' }, { e: '<i data-xss="3">' }], view: v }); await wait(400);
          const m = document.querySelector('#cbOv .cbmod');
          return { xss: document.querySelectorAll('[data-xss]').length, html: document.querySelector('#cbOv').innerHTML.indexOf('data-xss'), modal: m ? m.textContent.replace(/\\s+/g, ' ') : '', match: !!T.match }; }""", FKV)
        check(fx['xss'] == 0 and fx['html'] == -1 and not fx['match'] and '正しくない 知らせ' in fx['modal'], f'タグに なる 字の 入った 知らせは 画面に 出ない（タグ {fx["xss"]}こ）・対戦は そこで 終わる')
        pg.locator('#cbOv .cbmod [data-cb=menu]').click(); pg.wait_for_timeout(200)
        pg.evaluate("() => { const T = CBApp._t, st = T.state; st.coin = 0; st.ms.fr = 0; T.save(); }")
        check(not errs and not gerrs, f'エラー なし {errs[:3]} {gerrs[:3]}')
        if HAVE:
            miss = sorted(set(f for f in reqs if f.startswith('cb_') and f != 'cb_bundle.js' and f not in CBF))
            used = sorted(set(f for f in reqs if f in CBF))
            check(not miss and all(f in used for f in ['cb_board.webp', 'cb_deck.webp', 'cb_logo.webp', 'cb_icon.webp', 'cb_sb.webp', 'cb_s1.webp', 'cb_c1.webp', 'cb_ck.webp', 'cb_coin.webp', 'cb_bgm.m4a']), f'読んだ 絵と 音は 全部 アプリに 入れる ファイル（ない 名前 {miss}・読んだ {len(used)}個）')
finally:
    srv.terminate()
print('\n' + ('全部 OK' if not fails else f'NG {len(fails)}こ：' + ' / '.join(fails)))
sys.exit(1 if fails else 0)
