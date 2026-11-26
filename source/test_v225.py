# 第4.225版（まさちゃん 2026/11/26 13:57）の テスト：App Store版（TARGET=app）を localhost で アプリ版として 開く
#   ①「トレーニングセンターから戻る時に、変な音がなる。」→ 閉じる ときは 音を 0.15秒で 小さく してから 止める・音の 出口（AudioContext）は 0.3秒 あとに 休ませる
#      （前は いきなり 止めて すぐ 休ませて いた：ブツッ・ジジッ）。すぐ また 開いた ときは 休ませない・元の 大きさに もどる・音 オフの ときは オフの まま
#   ②「ダブルタップすると拡大される時がある。」③「タップが重なると、web版のようにコピーみたいな字が出てくることがある。」
#      → App Store版の 画面・説明書：ぜんぶの 所で touch-action:manipulation（ダブルタップで 拡大しない）・字の 選択と 長押しの 吹き出しを 止める（入力欄は 選べる）
#   ④「カードが効果を使う時は、カードが光るように演出できる？」→ TENGERカードバトル：えらべる カード（tg）・かかわる カード（src：金の ふち）・効果で かわった カード（fl：1.6秒）
#   ⑤「テンゲルカードバトルの分かりやすい説明書を作成する。」→ 遊び方を 絵の 説明書に（強さの 順位表・5ターン 手札 7枚・効果 9つ・決戦宝石・そのほか）
#   python3 test_v225.py   （SHOT=フォルダ で 画面を 写す。ios/cb_assets・tc_assets が ない とき（CI）は 絵と 音の 確かめを とばす）
import os, re, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
from toys_for_test import open_toys
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W); sys.path.insert(0, os.path.join(W, 'kisekae'))
SRV = os.path.join(W, 'srv_v225'); PORT = 8841; APP = f'http://localhost:{PORT}/APP/'
SHOT = os.environ.get('SHOT')
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, TARGET='app'))
pth = os.path.join(SRV, 'APP', 'index.html'); html = open(pth, encoding='utf8').read()
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
import cb_art, cb_sfx
from assets_dir import adir
CBA = os.path.join(W, 'ios', 'cb_assets'); CBF = cb_art.files() + cb_sfx.files()
HAVE_CB = all(os.path.isfile(os.path.join(CBA, f)) for f in CBF)
if HAVE_CB:
    for f in CBF: shutil.copy(os.path.join(CBA, f), os.path.join(SRV, 'APP', f))
TCA = adir('tc_assets'); HAVE_TC = os.path.isdir(TCA) and len(os.listdir(TCA)) > 100
if HAVE_TC:
    for f in os.listdir(TCA): shutil.copy(os.path.join(TCA, f), os.path.join(SRV, 'APP', f))
if not (HAVE_CB and HAVE_TC): print('※ 絵と 音（ios/cb_assets・tc_assets）が ない ので、絵と 音の 確かめは とばす')
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c: fails.append(label)


def shot(pg, name):
    if SHOT: os.makedirs(SHOT, exist_ok=True); pg.screenshot(path=os.path.join(SHOT, name + '.png'))


# アプリの 窓口の にせもの ＋ 音の 記録（音の 大きさを かえた・止めた・音の 出口を 休ませた）
FAKE = """
window.__NATIVE_INFO = { version: '1.0', build: '7', device: 'phone' };
window.__marks = {};
(function () { var C = window.AudioContext || window.webkitAudioContext; if (!C) return;
  window.__gains = []; window.__sus = []; window.__ramps = []; window.__stops = [];
  var cg = C.prototype.createGain; C.prototype.createGain = function () { var g = cg.apply(this, arguments); window.__gains.push(g); return g; };
  var su = C.prototype.suspend; C.prototype.suspend = function () { window.__sus.push({ at: performance.now(), ac: this }); return su.apply(this, arguments); };
  var P = AudioParam.prototype, lr = P.linearRampToValueAtTime; P.linearRampToValueAtTime = function (v, t) { window.__ramps.push({ p: this, v: v, t: t, at: performance.now(), ct: window.__tcAC ? window.__tcAC.currentTime : null }); return lr.apply(this, arguments); };
  var B = AudioBufferSourceNode.prototype, bs = B.stop; B.stop = function (w) { window.__stops.push({ loop: this.loop, w: w == null ? null : w, ct: this.context.currentTime, ac: this.context }); return bs.apply(this, arguments); };
})();
window.webkit = { messageHandlers: { tengel: { postMessage: function (m) {
  var P = m.payload, val = true;
  if (m.name === 'notify') val = P.op === 'status' ? { ok: true, auth: 'notDetermined' } : P.op === 'opened' ? { ok: true, opened: null } : { ok: true, list: [], scheduled: 0, auth: 'notDetermined' };
  if (m.name === 'iap') val = P.op === 'products' ? { ok: true, products: [] } : { ok: true, list: [], current: [], unfinished: [], active: [] };
  if (m.name === 'marker') { var k = P.key || 'm', M = window.__marks; if (P.op === 'set') { M[k] = P.value || '1'; val = { ok: true }; } else if (P.op === 'del') { delete M[k]; val = { ok: true }; } else val = { ok: true, has: k in M, value: M[k] }; }
  if (m.name === 'room') val = { ok: false, why: 'op' };
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


def idle(pg, t=30000):
    pg.wait_for_function("() => window.CBApp && CBApp._t.idle", timeout=t); pg.wait_for_timeout(60)


def start(pg, h0, h1, deck='', turns=3):
    """手札を 決めて コンピュータと 対戦（コンピュータは 自分では 動かない：opp() で 相手の 手を 打つ）"""
    pg.evaluate("""([h0, h1, dk, tn]) => { CBApp._think = () => 1e9; CBApp._opt = { hands: [h0.split(''), h1.split('')], deck: dk ? dk.split('') : undefined, turns: tn, full: true }; }""", [h0, h1, deck, turns])
    if pg.evaluate("() => CBApp._t.screen") != 'menu': pg.evaluate("() => CBApp._t.menu()")
    pg.locator('#cbOv .cbmenu [data-cb=cpu]').click(); idle(pg)


def opp(pg, a):
    r = pg.evaluate("""a => { const m = CBApp._t.match, S = m._.state(), h = S.p[1].hand, U = k => { const c = h.find(x => x.k === String(k)); return c ? c.u : -1; };
      const b = Object.assign({}, a); if (b.k != null) { b.u = U(b.k); delete b.k; }
      if (b.pickk != null) { const c = S.p[0].hand.find(x => x.k === String(b.pickk)); b.pick = c ? c.u : -1; delete b.pickk; }
      return m._.apply(1, b); }""", a)
    idle(pg)
    return r


def tap(pg, k):
    pg.locator(f'#cbOv .cbhand .cbc:has(img[src="cb_s{k}.webp"])').first.click(); pg.wait_for_timeout(80)


def play(pg, k):
    tap(pg, k); pg.locator('#cbOv .cbmod [data-cb=set]').click(); idle(pg)


# いま 光って いる カード（tg＝えらべる・src＝金の ふち）：場所ごとに カードの 種類を ならべる（b＝裏）
GL = """() => { const q = s => [...document.querySelectorAll('#cbOv ' + s)].map(e => { const i = e.querySelector('img'); return i ? i.getAttribute('src').replace(/^cb_[sc]/, '').replace('.webp', '') : '?'; }).sort().join('');
  return { htg: q('.cbhand .cbc.tg'), hsrc: q('.cbhand .cbc.src'), otg: q('.cbohand .cbc.tg'), osrc: q('.cbohand .cbc.src'), smy: q('.cbslot.my .cbc.src'), sop: q('.cbslot.op .cbc.src'), mtg: q('.cbmod.on .cbc.tg'), fl: q('.cbc.fl') }; }"""
# 1.6秒 だけ 強く 光った カード（fl）を 覚える（場所:種類）
FLW = """() => { window.__fl = []; if (window.__flmo) return; const tagOf = el => { const w = el.closest('.cbhand') ? 'hand' : el.closest('.cbohand') ? 'ohand' : el.closest('.cbslot.my') ? 'slotmy' : el.closest('.cbslot.op') ? 'slotop' : 'other';
    const i = el.querySelector('img'); return w + ':' + (i ? i.getAttribute('src').replace(/^cb_[sc]/, '').replace('.webp', '') : '?'); };
  window.__flmo = new MutationObserver(ms => ms.forEach(m => { const el = m.target; if (el.classList && el.classList.contains('cbc') && el.classList.contains('fl') && !(m.oldValue || '').split(/\\s+/).includes('fl')) window.__fl.push(tagOf(el)); }));
  window.__flmo.observe(document.querySelector('#cbOv'), { subtree: true, attributes: true, attributeFilter: ['class'], attributeOldValue: true }); }"""
FLS = "() => { const a = window.__fl.slice(); window.__fl.length = 0; return a; }"
NONE = {'htg': '', 'hsrc': '', 'otg': '', 'osrc': '', 'smy': '', 'sop': '', 'mtg': '', 'fl': ''}


def gl(pg, **kw):
    d = dict(NONE); d.update(kw); return d


try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo')
        ctx.add_init_script(FAKE)
        pg = ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(APP); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(700)

        print('■ ②③ ダブルタップで 拡大しない・字の 選択（コピーの 字）が 出ない：App Store版の 画面')
        TOUCH = """() => { const cs = e => getComputedStyle(e), q = s => document.querySelector(s);
          const els = [document.body, q('header.top'), q('.tabbar button'), q('#cbFab'), q('#tcFab')].filter(Boolean);
          const inp = document.createElement('input'), ta = document.createElement('textarea'), pr = document.createElement('pre'); pr.innerHTML = '<b>全文</b>'; document.body.append(inp, ta, pr);
          const r = { n: els.length, ta: els.map(e => cs(e).touchAction), us: els.map(e => cs(e).webkitUserSelect || cs(e).userSelect), inp: [inp, ta, pr, pr.firstChild].map(e => cs(e).webkitUserSelect || cs(e).userSelect), inpTa: cs(inp).touchAction,
            css: [...document.querySelectorAll('style')].some(s => s.textContent.includes('*{touch-action:manipulation;-webkit-user-select:none;user-select:none;-webkit-touch-callout:none}')) };
          inp.remove(); ta.remove(); pr.remove(); return r; }"""
        t0 = pg.evaluate(TOUCH)
        check(t0['n'] == 5 and set(t0['ta']) == {'manipulation'} and set(t0['us']) == {'none'} and t0['inp'] == ['text'] * 4 and t0['inpTa'] == 'manipulation' and t0['css'],
              f'画面の どこでも touch-action:manipulation（ダブルタップで 拡大しない）・字は 選べない（長押しの 吹き出しも 出さない）・入力欄は 今までどおり 選べる（{t0}）')
        app_html = open(os.path.join(SRV, 'APP', 'index.html'), encoding='utf8').read()
        man_html = open(os.path.join(SRV, 'APP', 'manual.html'), encoding='utf8').read()
        RULE = '*{touch-action:manipulation;-webkit-user-select:none;user-select:none;-webkit-touch-callout:none}'
        check(app_html.count(RULE) == 1 and man_html.count(RULE) == 1 and 'input,textarea,select,pre,pre *,[contenteditable],[contenteditable] *{-webkit-user-select:text;user-select:text;-webkit-touch-callout:default}' in man_html,
              'アプリの 画面（index.html）と 説明書（manual.html）に 1つずつ（入力欄・判定の 全文〈pre〉は 選べる）')
        tcsrc = {f: re.sub(r'//[^\n]*', '', open(os.path.join('tc', f), encoding='utf8').read()) for f in ('tc_buy.js', 'tc_test.js')}      # 説明の 行（//）は のぞく
        check(all('touch-action:auto' not in s for s in tcsrc.values()) and all('touch-action:manipulation' in s for s in tcsrc.values()),
              'トレーニングセンターの 買う 窓・テスト版の 道具箱：touch-action:auto（ダブルタップで 拡大する）→ manipulation')
        pm = ctx.new_page(); pm.goto(APP + 'manual.html'); pm.wait_for_timeout(800)
        mt = pm.evaluate("() => { const cs = getComputedStyle(document.body), h = document.querySelector('h1,h2,p'); return [cs.touchAction, cs.webkitUserSelect || cs.userSelect, h ? getComputedStyle(h).touchAction : '']; }")
        check(mt == ['manipulation', 'none', 'manipulation'], f'説明書（manual.html）も 同じ（{mt}）')
        pm.close()

        print('■ ① トレーニングセンターから 戻る ときの 音')
        if HAVE_TC:
            pg.locator('#tcFab').click()
            pg.wait_for_function("() => window.TCApp && document.querySelector('#tcOv.on') && !document.querySelector('#tcOv .tcld')", timeout=90000)
            pg.wait_for_timeout(2600)
            S0 = pg.evaluate("() => { const S = TCApp._snd, M = window.__gains.find(g => g.context === S.ac); window.__tcM = M; window.__tcAC = S.ac; return { bed: S.bed, st: S.ac && S.ac.state, g: M && M.gain.value }; }")
            check(S0['bed'] and S0['st'] == 'running' and S0['g'] == 1, f'開いた：フィールドの 音が 鳴って いる（{S0}）')
            pg.evaluate("() => { window.__t0 = performance.now(); window.__c0 = TCApp._snd.ac.currentTime; window.__nsus = window.__sus.length; window.__nst = window.__stops.length; window.__nr = window.__ramps.length; }")
            pg.locator('#tcOv [data-tc=back]').click()
            c1 = pg.evaluate("""() => { const S = TCApp._snd, M = window.__tcM, ac = S.ac, rs = window.__ramps.slice(window.__nr).filter(r => r.p === M.gain); window.__fade = rs.length ? rs[rs.length - 1].at : 0; const _ = 0, st = window.__stops.slice(window.__nst).filter(s => s.ac === ac && s.loop);
              return { st: ac.state, sus: window.__sus.length - window.__nsus, ramp: rs.length ? [rs[rs.length - 1].v, +(rs[rs.length - 1].t - rs[rs.length - 1].ct).toFixed(3)] : null, stop: st.map(s => s.w == null ? null : +(s.w - s.ct).toFixed(3)), bed: S.bed, on: document.querySelector('#tcOv').classList.contains('on') }; }""")
            check(not c1['on'] and c1['st'] == 'running' and c1['sus'] == 0 and c1['ramp'] and c1['ramp'][0] == 0 and 0.12 <= c1['ramp'][1] <= 0.3 and c1['stop'] and all(w is not None and 0.15 <= w <= 0.3 for w in c1['stop']) and c1['bed'] is None,
                  f'「← 戻る」の すぐ あと：音を 0.15秒で 小さく する（いきなり 止めない）・鳴って いた 音は 小さく なって から 止まる・音の 出口は まだ 休ませない（{c1}）')
            pg.wait_for_timeout(650)
            c2 = pg.evaluate("() => { const S = TCApp._snd, sus = window.__sus.slice(window.__nsus).filter(s => s.ac === S.ac); return { st: S.ac.state, sus: sus.map(s => Math.round(s.at - window.__fade)), g: +window.__tcM.gain.value.toFixed(3) }; }")
            check(c2['st'] == 'suspended' and len(c2['sus']) == 1 and 280 <= c2['sus'][0] <= 600 and c2['g'] == 0, f'小さく しはじめて 0.3秒 あとに 音の 出口を 休ませる（{c2["sus"]}ms あと・音の 大きさ {c2["g"]}）')
            pg.locator('#tcFab').click(); pg.wait_for_function("() => document.querySelector('#tcOv.on')", timeout=30000); pg.wait_for_timeout(2600)
            c3 = pg.evaluate("() => { const S = TCApp._snd; return { st: S.ac.state, g: window.__tcM.gain.value, bed: S.bed }; }")
            check(c3['st'] == 'running' and c3['g'] == 1 and c3['bed'], f'また 開く：音の 大きさは 元に もどって、フィールドの 音が 鳴る（{c3}）')
            # 閉じて すぐ また 開いた（0.3秒 たつ 前）：休ませない
            pg.evaluate("() => { window.__nsus = window.__sus.length; }")
            pg.locator('#tcOv [data-tc=back]').click(); pg.wait_for_timeout(80); pg.evaluate("() => TCApp.open()"); pg.wait_for_timeout(700)
            c4 = pg.evaluate("() => { const S = TCApp._snd; return { st: S.ac.state, sus: window.__sus.slice(window.__nsus).filter(s => s.ac === S.ac).length, g: window.__tcM.gain.value }; }")
            check(c4 == {'st': 'running', 'sus': 0, 'g': 1}, f'閉じて すぐ（0.3秒 たつ 前に）また 開いた：音の 出口は 休ませない・音の 大きさは 元に もどる（{c4}）')
            # 音 オフ：閉じて 開いても オフの まま
            pg.locator('#tcOv [data-tc=snd]').click(); pg.wait_for_timeout(200)
            g5 = pg.evaluate("() => window.__tcM.gain.value")
            pg.locator('#tcOv [data-tc=back]').click(); pg.wait_for_timeout(600); pg.locator('#tcFab').click(); pg.wait_for_function("() => document.querySelector('#tcOv.on')", timeout=30000); pg.wait_for_timeout(800)
            g6 = pg.evaluate("() => window.__tcM.gain.value")
            pg.locator('#tcOv [data-tc=snd]').click(); pg.wait_for_timeout(200); g7 = pg.evaluate("() => window.__tcM.gain.value")
            check(g5 == 0 and g6 == 0 and g7 == 1, f'音 オフ（右上の ボタン）：閉じて また 開いても オフの まま（{g5} → {g6}）・オンに もどすと 鳴る（{g7}）')
            pg.locator('#tcOv [data-tc=back]').click(); pg.wait_for_timeout(500)
        else:
            print('  ⚠️ トレーニングセンターの 絵と 音が ない（音の 確かめは とばす）')

        print('■ ④ TENGERカードバトル：効果の ときに 対象の カードが 光る')
        open_toys(pg, ('cb',))
        pg.locator('#cbFab .fabi').click()
        pg.wait_for_function("() => !!window.CBApp && !!document.querySelector('#cbOv.on')", timeout=30000)
        pg.evaluate("() => { CBApp._t.speed(0.03); CBApp._guard = 0; }"); pg.wait_for_timeout(150)
        pg.evaluate(FLW)
        css = pg.evaluate("() => document.getElementById('cbCss').textContent")
        check(all(x in css for x in ('#cbOv .cbc.tg::after', '#cbOv .cbc.src::after', '#cbOv .cbc.fl::after', '@keyframes cbtg', '@keyframes cbfl', '@keyframes cbusg', '#cbOv .cbuse.on .cd')) and re.search(r'prefers-reduced-motion:reduce\)\{#cbOv \.cbc\.tg::after', css),
              '光り方の 形：tg（金色に ゆっくり 明るく なる）・src（金の ふち）・fl（1.6秒 強く 光る）・効果の 札の カードも 光る（動きを へらす 設定では 点めつ しない）')
        start(pg, '12345', '12346')
        g = pg.evaluate(GL)
        check(g == NONE, f'効果が ない とき：どの カードも 光らない（{g}）')

        # 5 の 効果：場の 5 が 金の ふち → 使う → 手札が 光る（捨てる カードを えらぶ）→ 山札から 来た 場の カードが 光る
        start(pg, '51234', '12346', '6'); play(pg, '5'); opp(pg, {'t': 'set', 'k': 2})
        g1 = pg.evaluate(GL)
        check(g1 == gl(pg, smy='b'), f'効果タイム「5 の 効果を 使う？」：セットした 5（伏せた カード）に 金の ふち（{g1}）')
        shot(pg, 'v225_5ask')
        pg.locator('#cbOv [data-cb=effyes]').click(); pg.wait_for_timeout(150)
        g2 = pg.evaluate(GL)
        check(g2 == gl(pg, htg='1234', smy='b'), f'「使う」→ 一緒に 捨てる カードを えらぶ：手札が 全部 光る（えらべる）・場の 5 は 金の ふち（{g2}）')
        shot(pg, 'v225_5drop')
        pg.evaluate(FLS); tap(pg, '4'); pg.locator('#cbOv .cbmod [data-cb=drop5]').click(); idle(pg)
        f2 = pg.evaluate(FLS)
        check('slotmy:b' in f2, f'山札から 伏せて セットした カードが 光る（{f2}）')

        # 4 の 効果（相手）：自分が 交換する → 手札が 光る・場の 2枚に 金の ふち → 交換 → 場の カードと 手札に もどった カードが 光る
        start(pg, '15677', '41236'); play(pg, '1'); opp(pg, {'t': 'set', 'k': 4}); pg.evaluate(FLS)
        opp(pg, {'t': 'eff', 'use': {'u4': True}})
        g3 = pg.evaluate(GL); f3 = pg.evaluate(FLS)
        check(g3['htg'] == '5677' and g3['smy'] == 'b' and g3['sop'] == '4' and g3['hsrc'] == '' and 'slotop:4' in f3,
              f'相手が 4 の 効果：見せた 4 が 光る（{f3}）→ 交換する 手札が 全部 光る・場の 2枚（自分の 伏せた カード・相手の 4）に 金の ふち（{g3}）')
        shot(pg, 'v225_swap')
        tap(pg, '5'); pg.locator('#cbOv .cbmod [data-cb=swap]').click(); idle(pg)
        f4 = pg.evaluate(FLS); g4 = pg.evaluate(GL)
        check('slotmy:b' in f4 and 'hand:1' in f4 and g4['smy'] == 'b' and g4['htg'] == '',
              f'交換した：場に 出した カードと 手札に もどった 1 が 光る（{f4}）→ 交換で 出した 5 の 効果を 聞く ときは 場の 5 に 金の ふち（{g4}）')
        pg.locator('#cbOv .cbmod.cbask [data-cb=u5no]').click(); idle(pg)

        # 4 の 効果（自分）：見せた 4 が 光る・相手が 交換する 間は 場の 2枚に 金の ふち
        start(pg, '41236', '15677'); opp(pg, {'t': 'set', 'k': 1}); play(pg, '4')
        g5 = pg.evaluate(GL)
        check(g5 == gl(pg, smy='b'), f'「4 の 効果を 使う？」：セットした 4 に 金の ふち（{g5}）')
        pg.evaluate(FLS); pg.locator('#cbOv [data-cb=effyes]').click(); idle(pg)
        f6 = pg.evaluate(FLS); g6 = pg.evaluate(GL)
        check('slotmy:4' in f6 and g6['smy'] == '4' and g6['sop'] == 'b' and g6['htg'] == '', f'「使う」：見せた 4 が 光る（{f6}）・相手が 交換する 間は 場の 2枚に 金の ふち（{g6}）')
        opp(pg, {'t': 'swap', 'k': 5}); opp(pg, {'t': 'u5', 'drop': None})

        # 6 の 効果（自分）：6 の 2枚 と まだ 見て いない 相手の 手札に 金の ふち → 使う → えらぶ 窓の カードが 光る → 見た カードが 光る
        start(pg, '66123', '12345')
        g7 = pg.evaluate(GL)
        check(g7 == gl(pg, hsrc='66', osrc='bbbbb'), f'ターンの 始め「6 の 効果を 使う？」：手札の 6 の 2枚と、見られる 相手の 手札（裏の 5枚）に 金の ふち（{g7}）')
        pg.locator('#cbOv [data-cb=sixyes]').click(); pg.wait_for_timeout(120)
        g8 = pg.evaluate(GL)
        check(g8['mtg'] == 'bbbbb', f'「使う」→ えらぶ 窓：えらべる 相手の カード 5枚が 光る（{g8["mtg"]}）')
        shot(pg, 'v225_6pick')
        pg.evaluate(FLS); pg.locator('#cbOv .cbmod .pick .cbc').nth(2).click(); idle(pg)
        f8 = pg.evaluate(FLS); kn = [c['k'] for c in pg.evaluate("() => CBApp._t.view.op.hand") if c['k']]
        check(len(kn) == 1 and f'ohand:{kn[0]}' in f8, f'見た 相手の カード（{kn}）が 光る（{f8}）')
        # 6 の 効果（相手）：見られた 自分の カードが 光る
        start(pg, '12367', '66123'); pg.evaluate(FLS); opp(pg, {'t': 'p6', 'pickk': 2})
        f9 = pg.evaluate(FLS)
        check('hand:2' in f9, f'相手が 6 の 効果：見られた 自分の 2 が 光る（{f9}）')

        # 7 の 効果：手札の 7 に 金の ふち → 使う → 引いた 3枚が 光る
        start(pg, '57771', '12346', '2346')
        g10 = pg.evaluate(GL)
        check(g10 == gl(pg, hsrc='777'), f'「7 の 効果を 使う？」：手札の 7 の 3枚に 金の ふち（{g10}）')
        pg.evaluate(FLS); pg.locator('#cbOv .cbmod.cbask [data-cb=p7yes]').click(); idle(pg)
        f10 = pg.evaluate(FLS)
        check(sorted(set(x for x in f10 if x.startswith('hand:'))) == ['hand:2', 'hand:3', 'hand:4'] and not [x for x in f10 if not x.startswith('hand:')], f'7 を 3枚 戻して 引いた 3枚（2・3・4）が 光る（{f10}）')

        # 3 の 効果：手札の 3 と 相手の 裏の カードに 金の ふち → 使う → えらぶ 窓の 裏の カードが 光る → もらった カードが 光る
        start(pg, '33312', '4567k')
        g11 = pg.evaluate(GL)
        check(g11 == gl(pg, hsrc='333', osrc='bbbbb'), f'「3 の 効果を 使う？」：手札の 3 の 3枚と、交換できる 相手の 手札（裏の 5枚）に 金の ふち（{g11}）')
        pg.locator('#cbOv .cbmod.cbask [data-cb=p3yes]').click(); pg.wait_for_timeout(150)
        g12 = pg.evaluate(GL)
        check(g12['mtg'] == 'bbbbb', f'「使う」→ えらぶ 窓：裏の 5枚が 光る（{g12["mtg"]}）')
        pg.evaluate(FLS); pg.locator('#cbOv .cbmod.cbx3 .pick .cbc[data-cb=pick]').nth(1).click(); idle(pg)
        f12 = pg.evaluate(FLS); got = sorted(c['k'] for c in pg.evaluate("() => CBApp._t.view.my.hand") if c['k'] not in '123')
        check(len(got) == 1 and f'hand:{got[0]}' in f12, f'もらった カード（{got}）が 光る（{f12}）')

        # 幻の馬：手札に 金の ふち → 使う → 捨てる 2枚を えらぶ 間は 手札が 光る（えらんだ カードは 光らない：上がる）→ 引いた 2枚が 光る
        start(pg, 'm6712', '12345', '13'); play(pg, 'm'); opp(pg, {'t': 'set', 'k': 1})
        g13 = pg.evaluate(GL)
        check(g13 == gl(pg, hsrc='1267'), f'「幻の馬の 効果を 使う？」：手札（捨てる 2枚を えらぶ）に 金の ふち（{g13}）')
        pg.locator('#cbOv [data-cb=mpick]').click(); pg.wait_for_timeout(100); tap(pg, '6')
        g14 = pg.evaluate(GL)
        check(g14 == gl(pg, htg='127'), f'捨てる 2枚を えらぶ：まだ えらべる 手札が 光る（えらんだ 6 は 光らない：{g14}）')
        shot(pg, 'v225_dropm')
        tap(pg, '7'); pg.evaluate(FLS); pg.locator('#cbOv .cbact [data-cb=mgo]').click(); idle(pg)
        f14 = pg.evaluate(FLS)
        check(sorted(set(f14)) == ['hand:1', 'hand:3'], f'引いた 2枚（1・3）が 光る（{f14}）')
        pg.wait_for_timeout(1800)
        check(pg.evaluate(GL)['fl'] == '', '1.6秒 たつと 強い 光は 消える')

        print('■ ⑤ 遊び方（絵の 説明書）')
        pg.evaluate("() => CBApp._t.menu()"); pg.wait_for_timeout(200)
        pg.locator('#cbOv .cbmenu [data-cb=help]').click(); pg.wait_for_timeout(400)
        H = pg.evaluate("""() => { const h = document.querySelector('#cbOv .cbhelp'), bd = h.querySelector('.bd'), src = e => e.getAttribute('src');
          return { scr: CBApp._t.screen, secs: [...bd.querySelectorAll('h4[data-h]')].map(e => e.dataset.h + ':' + e.textContent), toc: [...bd.querySelectorAll('.htoc [data-cb=hgo]')].map(e => e.dataset.h),
            hero: bd.querySelector('.hhero').textContent, pips: bd.querySelectorAll('.hhero .hturns i').length, fan: bd.querySelectorAll('.hhero .hfan img').length,
            rank0: [...bd.querySelectorAll('.hrank .hrk0 .hcd img')].map(src), rank: [...bd.querySelectorAll('.hrank .hrk:not(.hrk0) .hcd img')].map(src), crown: (bd.querySelector('.hrank .hcrown') || {}).textContent,
            ef: [...bd.querySelectorAll('.hef')].map(e => src(e.querySelector('.hcd img')) + '|' + e.querySelector('.hwhen').textContent + '|' + e.querySelectorAll('.hneed .hmany img').length),
            where: [...bd.querySelectorAll('.hwhere>div')].map(e => e.className + ':' + e.querySelector('b').textContent), caseN: bd.querySelectorAll('.hcase img').length,
            gems: [...bd.querySelectorAll('.hgm')].map(e => e.querySelector('b').textContent + '|' + src(e.querySelector('.hcd img'))), dt: bd.querySelectorAll('details.hdt').length,
            big: bd.querySelectorAll('[data-cb=hbig]').length, imgs: [...bd.querySelectorAll('img')].length, bad: [...bd.querySelectorAll('img')].filter(i => i.complete && !i.naturalWidth).map(src) }; }""")
        check(H['scr'] == 'help' and [s.split(':')[0] for s in H['secs']] == ['st', 'rule', 'flow', 'ef', 'gem', 'etc'] and H['toc'] == ['st', 'rule', 'flow', 'ef', 'gem', 'etc'],
              f'6つの 章（① カードの 強さ ② 勝負の 仕方 ③ 1ターンの 流れ ④ カードの 効果 ⑤ 決戦宝石 ⑥ そのほか）と もくじ（{H["secs"]}）')
        check('5ターン' in H['hero'] and '手札 7枚' in H['hero'] and '強い 方の 勝ち' in H['hero'] and H['pips'] == 5 and H['fan'] == 7,
              f'上の 3つの ポイント：5ターン（丸 5つ）・手札 7枚（カード 7枚の 絵）・強い 方の 勝ち（{H["hero"]}）')
        check(H['rank0'] == ['cb_sk.webp', 'cb_sm.webp'] and H['rank'] == [f'cb_s{k}.webp' for k in '1234567'] and H['crown'] == 'いちばん 強い！',
              f'① 強さの 順位表：いちばん 上に 神様馬＝幻の馬（いちばん 強い！）→ 1＞2＞3＞4 → 5＞6＞7（カードの 絵：{H["rank0"]}・{H["rank"]}）')
        check(H['ef'] == ['cb_sk.webp|勝った 次の ターンの 始め|1', 'cb_sm.webp|勝った 次の ターンの 始め|1', 'cb_s1.webp|オープンの 後|3', 'cb_s2.webp|オープンの 後|3', 'cb_s3.webp|セットの 前|3',
                          'cb_s4.webp|効果タイム（いちばん 後）|1', 'cb_s5.webp|効果タイム|1', 'cb_s6.webp|ターンの 始め|2', 'cb_s7.webp|セットの 前|3'],
              f'④ 効果 9つ：カードの 絵・使える とき・いる カードの 絵（1 は 3枚・6 は 2枚 など）（{H["ef"]}）')
        check(H['where'] == ['ok:⚔️ 決戦調査', 'ok:🤝 友達バトル', 'no:コンピュータとの 対戦'] and H['caseN'] == 6 and H['gems'] == ['幻影のアメジスト|cb_stm.webp', '日輪の黄金石|cb_stk.webp', '双炎のルビー|cb_st1.webp', '双葉のエメラルド|cb_st3.webp', '三峰の翡翠|cb_st7.webp'],
              f'⑤ 決戦宝石：使える 所（決戦調査・友達バトル ○／コンピュータ ×）・ケースの 絵（宝石 5つ）・宝石 → トークンの カード（{H["gems"]}）')
        check(H['dt'] == 9 and H['big'] >= 9 + 9 + 5 and not H['bad'], f'⑥ そのほか：開いて 読む 9つ・カードの 絵は タップで 大きく（{H["big"]}こ）・読めない 絵 なし（{H["bad"]}）')
        shot(pg, 'v225_help_top')
        # もくじ → その 章へ
        pg.locator('#cbOv .cbhelp .htoc [data-h=gem]').click(); pg.wait_for_timeout(300)
        pg.wait_for_function("() => { const bd = document.querySelector('#cbOv .cbhelp .bd'), y = bd.scrollTop, ok = window.__sy === y; window.__sy = y; return ok && y > 0; }", polling=200, timeout=8000)      # なめらかに 動いて 止まる まで
        jy = pg.evaluate("() => { const bd = document.querySelector('#cbOv .cbhelp .bd'), h = bd.querySelector('h4[data-h=gem]'); return Math.round(h.getBoundingClientRect().top - bd.getBoundingClientRect().top); }")
        check(0 <= jy <= 30, f'もくじ「⑤ 決戦宝石」→ その 章が いちばん 上に（{jy}px）')
        shot(pg, 'v225_help_gem')
        # カードの 絵を タップ → 大きく 見る → 戻る（遊び方の まま）
        pg.locator('#cbOv .cbhelp .hrank [data-cb=hbig][data-k="1"]').click(); pg.wait_for_timeout(250)
        bg = pg.evaluate("() => { const m = document.querySelector('#cbOv .cbmod.on'); return m ? { img: m.querySelector('img') && m.querySelector('img').getAttribute('src'), scr: CBApp._t.screen } : null; }")
        check(bg is not None and bg['img'] == 'cb_c1.webp' and bg['scr'] == 'help', f'カードの 絵を タップ → 大きい カード（{bg}）')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(200)
        check(pg.evaluate("() => CBApp._t.screen") == 'help' and not pg.evaluate("() => CBApp._t.modOn()"), '戻る → 遊び方の まま')
        pg.locator('#cbOv .cbhelp .hgm [data-cb=hbig]').first.click(); pg.wait_for_timeout(250)
        tk = pg.evaluate("() => { const m = document.querySelector('#cbOv .cbmod.on'); return m ? m.querySelector('img').getAttribute('src') : null; }")
        check(tk == 'cb_ctm.webp', f'トークンの カードも 大きく 見られる（{tk}）')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(200)
        # 横に はみ出さない（390・375・320）
        for vw in (390, 375, 320):
            pg.set_viewport_size({'width': vw, 'height': 700 if vw == 320 else 844}); pg.wait_for_timeout(300)
            ov = pg.evaluate("""() => { const bd = document.querySelector('#cbOv .cbhelp .bd'), R = bd.getBoundingClientRect();
              const out = [...bd.querySelectorAll('.hrk,.hef,.hgm,.hcase,.hwhere,.hst,.hflow li,.hpts')].filter(e => { const r = e.getBoundingClientRect(); return r.right > R.right + 0.5 || r.left < R.left - 0.5; }).map(e => e.className);
              return { sw: bd.scrollWidth, cw: bd.clientWidth, out: out.slice(0, 4) }; }""")
            check(ov['sw'] <= ov['cw'] + 1 and not ov['out'], f'幅 {vw}px：横に はみ出さない（{ov}）')
        pg.set_viewport_size({'width': 390, 'height': 844}); pg.wait_for_timeout(300)
        pg.locator('#cbOv [data-cb=helpx]').click(); pg.wait_for_timeout(150)
        check(pg.evaluate("() => CBApp._t.screen") == 'menu', '戻る → メニュー')
        # 対戦の とちゅうの「？」→ 遊び方 → 戻る → 対戦
        start(pg, '12345', '12346'); pg.locator('#cbOv .cbtop [data-cb=help]').click(); pg.wait_for_timeout(250)
        s1 = pg.evaluate("() => CBApp._t.screen"); pg.locator('#cbOv [data-cb=helpx]').click(); pg.wait_for_timeout(150)
        check(s1 == 'help' and pg.evaluate("() => CBApp._t.screen") == 'game', '対戦の とちゅうの「？」→ 遊び方 → 戻る → 対戦に もどる')

        check(not errs, f'エラー なし {errs[:3]}')
finally:
    srv.terminate()
print('\n結果：' + ('全部 OK' if not fails else f'{len(fails)}こ だめ：' + ' / '.join(fails)))
sys.exit(1 if fails else 0)
