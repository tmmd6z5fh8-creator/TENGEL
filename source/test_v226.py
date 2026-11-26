# 第4.226版（まさちゃん 2026/11/26 15:11「友達バトルはお互いにカードをセットするまでの制限時間を10秒にして！ 過ぎたら勝手に出して！」）の テスト：
#   App Store版（TARGET=app）を localhost で アプリ版として 開いて、2つの 画面（ホスト・ゲスト）を にせの 部屋（BroadcastChannel：test_cb.py の FAKE）で つなぐ
#   ・ふだんの 時間は 10秒（SET_LIMIT）・部屋の 画面に「⏱ カードを セットする までは 10秒」・遊び方にも
#   ・セットできる ように なったら 2人とも 時計（自分と 相手の のこり・のこり 3秒で 赤）
#   ・時間切れ → 手札から 自動で 1枚（ホストも ゲストも）・カードを タップして 窓を 開いて いれば その カード・「⏱ 時間切れ！」
#   ・カードの 動き・効果の 札の 間は 時計が 止まる（7 の 効果を 使って、ふつうの 速さの 演出を 見せる）
#   ・コンピュータとの 対戦には 時計は 出ない
#   python3 test_v226.py   （SHOT=フォルダ で 画面を 写す）
import os, re, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
from toys_for_test import open_toys
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W); sys.path.insert(0, os.path.join(W, 'kisekae'))
SRV = os.path.join(W, 'srv_v226'); PORT = 8843; APP = f'http://localhost:{PORT}/APP/'
SHOT = os.environ.get('SHOT')
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, TARGET='app'))
pth = os.path.join(SRV, 'APP', 'index.html'); html = open(pth, encoding='utf8').read()
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
import cb_art, cb_sfx
CBA = os.path.join(W, 'ios', 'cb_assets'); CBF = cb_art.files() + cb_sfx.files()
if all(os.path.isfile(os.path.join(CBA, f)) for f in CBF):
    for f in CBF: shutil.copy(os.path.join(CBA, f), os.path.join(SRV, 'APP', f))
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
FAKE = re.search(r'\nFAKE = """(.*?)"""', open(os.path.join(W, 'test_cb.py'), encoding='utf8').read(), re.S).group(1)      # アプリの 窓口の にせもの（部屋は BroadcastChannel）
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c: fails.append(label)


def shot(pg, name):
    if SHOT: os.makedirs(SHOT, exist_ok=True); pg.screenshot(path=os.path.join(SHOT, name + '.png'))


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


def open_cb(pg):
    open_toys(pg, ('cb',))
    pg.locator('#cbFab .fabi').click()
    pg.wait_for_function("() => !!window.CBApp && !!document.querySelector('#cbOv.on')", timeout=30000)
    pg.evaluate("() => { CBApp._t.speed(0.03); CBApp._guard = 0; }"); pg.wait_for_timeout(150)
    # 出て すぐ 消える ふきだし（.cbtoast）を 覚えて おく
    pg.evaluate("""() => { if (window.__toasts) return; window.__toasts = []; const e = document.querySelector('#cbOv .cbtoast'); let last = '';
      new MutationObserver(() => { const s = e.classList.contains('on') ? e.textContent : ''; if (s && s !== last) window.__toasts.push(s); last = s; }).observe(e, { childList: true, subtree: true, attributes: true, characterData: true }); }""")


TOASTS = "() => { const a = window.__toasts.slice(); window.__toasts.length = 0; return a; }"
V = "() => CBApp._t.view"
TLV = """() => { const q = s => { const e = document.querySelector('#cbOv .cbtl[data-p=' + s + ']'); return e ? { hid: e.hidden, n: e.querySelector('.n').textContent, lo: e.classList.contains('lo'), al: e.getAttribute('aria-label'), p: e.querySelector('i').style.getPropertyValue('--p') } : null; };
  return { my: q('my'), op: q('op'), tl: CBApp._t.tl }; }"""


def tap(pg, k):
    pg.locator(f'#cbOv .cbhand .cbc:has(img[src="cb_s{k}.webp"])').first.click(); pg.wait_for_timeout(80)


def play(pg, k):
    tap(pg, k); pg.locator('#cbOv .cbmod [data-cb=set]').click(); idle(pg)


def pair(pg, gp, hands, turns=3):
    """ホスト（pg）が 部屋を 作って、ゲスト（gp）が 入る → 2人とも 対戦の 画面"""
    pg.evaluate("([h, t]) => { CBApp._opt = { hands: h, turns: t, full: true }; }", [[list(hands[0]), list(hands[1])], turns])
    for q in (pg, gp):
        if q.evaluate("() => CBApp._t.screen") != 'menu': q.evaluate("() => CBApp._t.menu()")
    pg.locator('#cbOv .cbmenu [data-cb=host]').click(); pg.wait_for_timeout(250)
    if pg.locator('#cbOv .cbroom [data-cb=stkgo]').count(): pg.locator('#cbOv .cbroom [data-cb=stkgo]').click(); pg.wait_for_timeout(250)
    num = pg.evaluate("() => document.querySelector('#cbOv .cbroom .num').textContent")
    ht = pg.evaluate("() => document.querySelector('#cbOv .cbroom').textContent")
    gp.locator('#cbOv .cbmenu [data-cb=join]').click(); gp.wait_for_timeout(150)
    gt = gp.evaluate("() => document.querySelector('#cbOv .cbroom').textContent")
    for d in num: gp.locator(f'#cbOv .cbkeys [data-key="{d}"]').click()
    gp.locator('#cbOv .cbkeys [data-key=go]').click()
    for q in (pg, gp): q.wait_for_function("() => CBApp._t.screen === 'game' && CBApp._t.view && CBApp._t.view.can.set && CBApp._t.idle", timeout=30000)
    return ht, gt


try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo')
        ctx.add_init_script(FAKE)
        pg = ctx.new_page(); gp = ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append('host:' + str(e))); gp.on('pageerror', lambda e: errs.append('guest:' + str(e)))
        for q in (pg, gp):
            q.goto(APP); q.wait_for_timeout(1300); gate(q); q.wait_for_timeout(600); open_cb(q)

        print('■ ふだんの 時間・部屋の 画面と 遊び方の ことば')
        t0 = pg.evaluate("() => CBApp._t.tl")
        check(t0['SET_LIMIT'] == 10000 and t0['max'] == 10000 and not t0['on'], f'ふだんの セットの 時間は 10秒（{t0}）')
        pg.locator('#cbOv .cbmenu [data-cb=help]').click(); pg.wait_for_timeout(200)
        hl = pg.evaluate("() => document.querySelector('#cbOv .cbhelp .bd').textContent")
        check('友達バトルは 10秒 まで（すぎたら 自動で 1枚）' in hl and '⏱ 友達バトルは、カードを セットする までの 時間が 10秒（名前の よこに 自分と 友達の のこりが 出るよ）。すぎたら 手札から 自動で 1枚 セット（タップして 開いて いた カード・なければ ランダム）' in hl
              and '相手の 4 の 効果で 交換する カードを 選ぶ ときも 10秒' in hl and '自動で 出した カードの 効果は 使わないよ。ほかの「効果を 使う？」には 時間の 決まりは ないよ' in hl,
              '遊び方：③ 1ターンの 流れ（セット）と ⑥ 友達と 対戦 に 10秒の 決まり（4 の 交換も・自動で 出した カードの 効果は 使わない）')
        pg.locator('#cbOv [data-cb=helpx]').click(); pg.wait_for_timeout(150)
        for q in (pg, gp): q.evaluate("() => { CBApp._limit = 2000; }")      # ここからは 2秒（テストを 短く）
        ht, gt = pair(pg, gp, ('12345', '23457'))
        check('⏱ カードを セットする までは 10秒（すぎたら 自動で 1枚）' in ht and '⏱ カードを セットする までは 10秒（すぎたら 自動で 1枚）' in gt, '部屋を 作った 画面・部屋に 入る 画面に「⏱ カードを セットする までは 10秒（すぎたら 自動で 1枚）」')

        print('■ 時計：2人とも・相手の のこりも・のこり 3秒で 赤')
        for q in (pg, gp): q.wait_for_function("() => CBApp._t.tl.my && CBApp._t.tl.op", timeout=5000)      # 時計が 1回 進む まで（うしろの ページは 時計が おそい）
        th, tg = pg.evaluate(TLV), gp.evaluate(TLV)
        check(not th['my']['hid'] and not th['op']['hid'] and not tg['my']['hid'] and not tg['op']['hid'] and th['my']['n'] in ('1', '2') and th['my']['lo'] and th['tl']['on']
              and th['my']['al'].startswith('あなたの のこり ') and th['op']['al'].startswith('友達の のこり '),
              f'セットできる ように なったら 2人の 画面に 自分と 友達の のこり（2秒 → 3秒 より 少ない ので 赤）（ホスト {th["my"]}／{th["op"]}・ゲスト {tg["my"]}／{tg["op"]}）')
        shot(pg, 'v226_timer_host'); shot(gp, 'v226_timer_guest')
        pg.evaluate(TOASTS); gp.evaluate(TOASTS)
        play(gp, '2')      # ゲストは すぐ セット
        idle(pg)
        th2, tg2 = pg.evaluate(TLV), gp.evaluate(TLV)
        check(th2['op']['hid'] and tg2['my']['hid'] and not tg2['op']['hid'] and not th2['my']['hid'], f'ゲストが セット → ゲストの 時計は 消える（ホストの 画面の 友達の 時計も）・ホストの 時計は のこる')
        for q in (pg, gp): q.evaluate("() => { CBApp._limit = 4000; }")      # 次の ターンの 時間（いまの ターンは 始まった 時の 2秒の まま）
        # ホストは 何も しない → 2秒で 自動で 1枚
        s0 = time.time()
        pg.wait_for_function("() => CBApp._t.view && CBApp._t.view.turn === 2 && CBApp._t.idle", timeout=15000); el = time.time() - s0
        hv = pg.evaluate(V); toh = pg.evaluate(TOASTS); tog = gp.evaluate(TOASTS)
        check(any(t.startswith('⏱ 時間切れ！') and 'を 自動で セットしたよ' in t for t in toh) and not any('時間切れ' in t for t in tog) and hv['last']['c'][0] in list('12345') and 1.0 <= el <= 6,
              f'ホストは 何も しない → 時間切れで 手札から 自動で 1枚（{hv["last"]["c"][0]}）→ オープン → 2ターン目（{el:.1f}秒）・ホストに「⏱ 時間切れ！ ○ を 自動で セットしたよ」（{toh}）・ゲストには 出ない')

        print('■ タップして 開いて いた カードを 出す（2ターン目：4秒）')
        pg.wait_for_function("() => CBApp._t.view.can.set && CBApp._t.tl.my", timeout=10000)
        th3 = pg.evaluate(TLV)
        check(th3['my']['n'] in ('3', '4') and not th3['my']['lo'], f'4秒：はじめは 赤 では ない（{th3["my"]}）')
        hand = [c['k'] for c in pg.evaluate(V)['my']['hand']]
        pick = sorted(hand)[-1]
        tap(pg, pick)      # 窓を 開いた まま（セットは 押さない）
        pg.wait_for_timeout(250)
        mm = pg.evaluate("() => { const e = document.querySelector('#cbOv .cbmod.on .cbtl[data-p=mym]'); return e ? { first: e.parentNode.firstElementChild === e, n: e.querySelector('.n').textContent, al: e.getAttribute('aria-label'), vis: e.getBoundingClientRect().height > 0 } : null; }")
        check(mm is not None and mm['first'] and mm['vis'] and mm['n'] in ('2', '3', '4') and mm['al'].startswith('あなたの のこり '), f'カードの 窓を 開いて いる 間は 窓の いちばん 上にも 自分の のこり（{mm}）')
        pg.wait_for_function("() => document.querySelector('#cbOv .cbtl[data-p=my]').classList.contains('lo')", timeout=6000)
        shot(pg, 'v226_timer_low')
        for q in (pg, gp): q.evaluate("() => { CBApp._limit = 2000; }")      # 3ターン目の 時間
        play(gp, '3')
        pg.wait_for_function("() => CBApp._t.view && CBApp._t.view.turn === 3 && CBApp._t.idle", timeout=15000)
        hv = pg.evaluate(V); toh = pg.evaluate(TOASTS)
        check(hv['last']['c'][0] == pick and any(t.startswith(f'⏱ 時間切れ！') for t in toh), f'窓を 開いて いた カード（{pick}）を 自動で セット（出た カード {hv["last"]["c"][0]}）')

        print('■ ゲストの 時間切れ（3ターン目：2秒）')
        pg.wait_for_function("() => CBApp._t.view.can.set && CBApp._t.tl.my", timeout=10000)
        gp.evaluate(TOASTS)
        hand_g = [c['k'] for c in gp.evaluate(V)['my']['hand']]
        play(pg, sorted(c['k'] for c in pg.evaluate(V)['my']['hand'])[0])      # ホストは すぐ セット
        gp.wait_for_function("() => CBApp._t.ended || (CBApp._t.view && CBApp._t.view.turn === 4)", timeout=15000)
        gp.wait_for_timeout(300)
        tog = gp.evaluate(TOASTS); gv = gp.evaluate(V)
        check(any(t.startswith('⏱ 時間切れ！') for t in tog) and gv['last']['c'][0] in hand_g, f'ゲストも 何も しない と 時間切れで 自動で 1枚（{gv["last"]["c"][0]}）（{tog}）')
        pg.wait_for_function("() => CBApp._t.ended", timeout=15000); gp.wait_for_function("() => CBApp._t.ended", timeout=15000)
        te = pg.evaluate(TLV)
        check(te['my']['hid'] and te['op']['hid'], '対戦が 終わったら 時計は 出ない')

        print('■ カードの 動き・効果の 札の 間は 時計が 止まる（7 の 効果・ふつうの 速さ）')
        for q in (pg, gp): q.evaluate("() => { CBApp._limit = 9000; }")
        pair(pg, gp, ('77712', '23456'))
        pg.wait_for_function("() => CBApp._t.ask && CBApp._t.tl.my", timeout=10000)
        pg.evaluate("() => { CBApp._t.speed(1); }")
        a0 = pg.evaluate("() => ({ left: CBApp._t.tl.my.left, t: performance.now() })")
        pg.locator('#cbOv .cbmod.cbask [data-cb=p7yes]').click()
        pg.wait_for_function("() => !CBApp._t.idle", timeout=5000)
        pg.wait_for_function("() => CBApp._t.idle && CBApp._t.tl.my", timeout=30000)
        a1 = pg.evaluate("() => ({ left: CBApp._t.tl.my.left, t: performance.now() })")
        pg.evaluate("() => { CBApp._t.speed(0.03); }")
        used, wall = a0['left'] - a1['left'], a1['t'] - a0['t']
        check(wall >= 1500 and used <= 900, f'7 の 効果の 演出の 間（{wall / 1000:.1f}秒）は 時計が ほとんど 進まない（へった のは {used / 1000:.2f}秒）')
        play(pg, '1'); play(gp, '2')
        for q in (pg, gp): q.evaluate("() => { CBApp._t.menu(); }")
        pg.wait_for_timeout(300)

        print('■ 自動で 出した 4・5 の 効果は 自動で「使わない」（はなれて いても 止まらない）')
        for q in (pg, gp): q.evaluate("() => { CBApp._limit = 1500; }")
        pair(pg, gp, ('44555', '12367')); pg.evaluate(TOASTS)
        play(gp, '7')
        pg.wait_for_function("() => CBApp._t.view && CBApp._t.view.turn === 2 && CBApp._t.idle", timeout=15000)
        hv = pg.evaluate(V); toh = pg.evaluate(TOASTS)
        check(hv['last']['c'][0] in ('4', '5') and any(t.startswith('⏱ 時間切れ！') for t in toh),
              f'ホストの 手札は 4・5 だけ → 時間切れで 自動で {hv["last"]["c"][0]} → その 効果は 聞かずに「使わない」→ オープン → 2ターン目（{toh}）')
        print('■ 相手の 4 の 効果で 交換する カードを 選ぶ ときも 時間（すぎたら 自動で 交換）')
        pair(pg, gp, ('15677', '41236')); pg.evaluate(TOASTS)
        play(pg, '1'); play(gp, '4')
        gp.wait_for_function("() => CBApp._t.ask", timeout=10000); gp.locator('#cbOv .cbmod.cbask [data-cb=effyes]').click()
        pg.wait_for_function("() => { const v = CBApp._t.view; return v && v.pend && v.pend.type === 'swap' && v.pend.mine && CBApp._t.tl.my; }", timeout=10000)
        tsw, tsg = pg.evaluate(TLV), gp.evaluate(TLV)
        check(not tsw['my']['hid'] and not tsg['op']['hid'] and tsw['tl']['my']['key'].endswith(':swap'), f'友達が 4 の 効果 → 交換する カードを 選ぶ 時計（ホスト：自分／ゲスト：友達）（{tsw["my"]}）')
        shot(pg, 'v226_swap_timer')
        pg.wait_for_function("() => CBApp._t.view && CBApp._t.view.turn === 2 && CBApp._t.idle", timeout=15000)
        toh = pg.evaluate(TOASTS); hv = pg.evaluate(V)
        check(any(t.startswith('⏱ 時間切れ！') and 'と 自動で 交換したよ' in t for t in toh) and hv['last']['c'][0] in list('567') and '1' in [c['k'] for c in hv['my']['hand']],
              f'交換する カードを 選ばない → 時間切れで 自動で 交換（場の カード {hv["last"]["c"][0]}・1 は 手札に 戻る：{toh}）')
        for q in (pg, gp): q.evaluate("() => { CBApp._t.menu(); }")
        pg.wait_for_timeout(300)

        print('■ コンピュータとの 対戦には 時計は ない')
        pg.evaluate("() => { CBApp._limit = 2000; CBApp._think = () => 1e9; CBApp._opt = { hands: [['1','2','3','4','5'], ['2','3','4','5','7']], turns: 3, full: true }; }")
        pg.locator('#cbOv .cbmenu [data-cb=cpu]').click(); idle(pg); pg.wait_for_timeout(2600)
        tc = pg.evaluate(TLV); vc = pg.evaluate(V)
        check(not tc['tl']['on'] and tc['my']['hid'] and tc['op']['hid'] and vc['can']['set'] and vc['my']['set'] is None, f'コンピュータと 対戦：時計は 出ない・2.6秒 たっても 自動で 出さない（{tc["tl"]}）')
        check(not errs, f'エラー なし {errs[:3]}')
finally:
    srv.terminate()
print('\n結果：' + ('全部 OK' if not fails else f'{len(fails)}こ だめ：' + ' / '.join(fails)))
sys.exit(1 if fails else 0)
