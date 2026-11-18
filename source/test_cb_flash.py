# 馬カードバトル（第4.176版）の 光の 点めつ：対戦の 動き（配る・セット・「効果タイム」の 帯・効果・オープン・勝ち負けの 字・「ターン」「神様馬の 効果」の 帯・結果）を 60コマ／秒の 絵に して kisekae/flash_px.py で 数える
#   決まり：画面の 10% 以上の 広さで 1秒に 3回 まで（もっと きびしい 3% でも 数えて 出す）。「演出を控えめにする」（動きを へらす 設定）でも 数える
#   時計は 手で 進める（CBApp._t.manual・tick：1/60秒 ずつ）。CSS の 動き（transition・animation）は 出て きた 時刻を 覚えて、同じ 時計で 進める
#   第4.177版：2つ目の 対戦（3 の 効果）＝効果を 使うか 聞く 窓が 出る（ask3）・3 を 3まい 見せる 窓 → もらった カード → 交換 → オープン（eff3_open）・勝ち → さいごの 画面の「お世話トークン ＋1こ GET！」の 札（end_win）
#   第4.178版：1つ目・2つ目の 対戦は 前の 形（3ターン・手札 5まい）の まま。3つ目の 対戦＝本番の 形（5ターン・手札 7まい）：7まい ずつ 配る（deal7）・何も しない 6秒＝夜の フィールドの 火の あかりの ゆれ（fire）・
#     逆転勝利（自分：rev_open＝めくった 窓「チャンス！」→ 聞く 窓／rev_use＝3まい 見せる 窓 →「逆転勝利！」。相手：rev_op_open＝「勝負は まだ！」／rev_op_use＝「逆転負け…」）。
#     3回目の 通し＝カードバトルの 設定で「エフェクト オフ」（3つ目の 対戦 だけ）
#   第4.185版：効果を 使った ときの 札（ボードの まん中・約 2秒）が 入る ぶん 効果の 場面を 長く 写す。設定の「エフェクト オフ」は なくした ので、3回目の 通しは
#     プレイボード『白亜の宮殿』（いちばん 明るい ボード：暗い 窓や 札との 明るさの ちがいが いちばん 大きい）。4つ目の 対戦（3ターン）：相手が 7 を 4まい 見せて 強さ 逆転（x7r）
#   第4.187版：7 の 4まい 公開は セットの 前（x7r：まだ だれも セットして いない ときに 相手が 使う）→ 自分が セット → 相手が ふせて セット → オープン（x7r_open）。
#     セットした カードは 自分の 画面でも うら（ふせて セット：うらで とんで、うら ＋ しるしで 置く）
#   第4.189版：5つ目＝カードパック（ふつう・動きを へらす の 2回）：タブの パックの 絵（光の すじ：pk_tab）→「開ける」→ パックが 出る（pk_pack）→ タップ → 上が 切れて とぶ → カードが 1まいずつ 出て パックの うしろに ならぶ → パックが 下へ 消える → ノーマル 4まいを めくる → くじが ゆっくり ひかる（pk_open）→
#     くじを めくる：神様馬の 超レア（光の すじ・光が ひろがる：pk_rev_gsr）／もう 1パック：レア（pk_rev_r）
#   第4.189版：時計を 進める ときに、CSS から 消えた 動き（idle：animation: none に した・transition が とりけされた）の 時刻を 入れない（入れると その 動きが 生きかえって、
#     うしろの 動きを 上書きする：パックが 消えずに のこって 写って いた）。前の 場面も この 形で 数え直した
#   第4.190版：6 の 効果は ターンの はじめ（1つ目の 対戦）：配る → 「6 の 効果」の 帯 → 聞く 窓（deal）・見る カードを えらぶ → 効果の 札 → 見た カードを 大きく（six_peek）・
#     オープン（勝ち）→「ターン 2」→「6 の 効果」の 帯（open_win）・6 を 使わない →「神様馬の 効果」の 帯（six_pre）・相手の 5 で「効果タイム」の 帯（set_efft）→ 負け（open_lose）。
#     前の efft・eff6_open（効果タイムの 6）は なくなった
#   第4.197版：6つ目＝決戦宝石（gem_deal：ケースの 宝石が ゆっくり 光る・gem_ask：宝石の 窓・gem_use：宝石が はねる・トークンが 手札へ・帯・gem_tokgone：使わなかった トークンが 消える）
#   第4.199版：7つ目＝7トークンで 7 の 効果（gem7_x7：効果の 札 → 7トークン 1枚を 見せる 窓 → 捨て札へ → 山札から 3枚：まさちゃん 22:01）
#   python3 test_cb_flash.py [場面の 名前,…]   （時間が かかる ので ふだんの テストとは 別に 動かす。コマは t5/cb_frames/<場面>/ に 残す）
import os, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W); sys.path.insert(0, os.path.join(W, 'kisekae'))
SRV = os.path.join(W, 'srv_cbf'); PORT = 8814; APP = f'http://localhost:{PORT}/APP/'
ONLY = sys.argv[1].split(',') if len(sys.argv) > 1 else None
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, TARGET='app'))
pth = os.path.join(SRV, 'APP', 'index.html'); html = open(pth, encoding='utf8').read()
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
import cb_art, cb_sfx
CBA = os.path.join(W, 'ios', 'cb_assets'); CBF = cb_art.files() + cb_sfx.files()
if not all(os.path.isfile(os.path.join(CBA, f)) for f in CBF):
    print('※ 馬カードバトルの 絵（ios/cb_assets）が ない ので、数えない'); sys.exit(0)
for f in CBF: shutil.copy(os.path.join(CBA, f), os.path.join(SRV, 'APP', f))
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c: fails.append(label)


FAKE = open(os.path.join(W, 'test_cb.py'), encoding='utf8').read().split('FAKE = """')[1].split('"""')[0]      # アプリの 窓口の にせもの（test_cb.py と 同じ）
# 1コマ（dt ミリ秒）進める：時計 → 待って いる 続き（await）を 流す → CSS の 動きを 同じ 時計に 合わせる
STEP = """async (dt) => {
  const T = CBApp._t; T.tick(dt);
  for (let i = 0; i < 40; i++) await null;
  const now = T.now, ov = document.getElementById('cbOv'), V = window.__cbv || (window.__cbv = { track: [], seen: new WeakSet() });
  ov.getAnimations({ subtree: true }).forEach(a => { if (V.seen.has(a)) return; V.seen.add(a); try { a.pause(); } catch (e) { } V.track.push({ a, at: now }); });
  V.track = V.track.filter(o => { try { if (o.a.playState === 'idle') return false; o.a.currentTime = Math.max(0, now - o.at); return true; } catch (e) { return false; } });      // 第4.189版：CSS から 消えた 動き（animation: none・transition の とりけし）は 生きかえらせない
  return V.track.length; }"""
OPP = """a => { const m = CBApp._t.match, S = m._.state(), h = S.p[1].hand, b = Object.assign({}, a); if (b.k != null) { b.u = h.find(x => x.k === String(b.k)).u; delete b.k; } return m._.apply(1, b); }"""


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


FD = os.path.join(W, 't5', 'cb_frames')


def run(pg, name, sec, pre=None):
    """いまから sec 秒を 60コマ／秒で 写して 数える。pre＝写しはじめる 直前に する こと（画面の 中の 関数）"""
    d = os.path.join(FD, name); shutil.rmtree(d, ignore_errors=True); os.makedirs(d); t0 = time.time()
    if pre: pre()
    N = int(round(sec * 60)); na = 0
    for i in range(N):
        na = max(na, pg.evaluate(STEP, 1000 / 60))
        pg.screenshot(path=os.path.join(d, f'f{i:04d}.png'), clip={'x': 0, 'y': 0, 'width': 390, 'height': 844})
    outs = []
    for area in ('.1', '.03'):
        r = subprocess.run(['python3', os.path.join(W, 'kisekae', 'flash_px.py'), d, '0'], capture_output=True, text=True, env=dict(os.environ, AREA=area))
        o = r.stdout.strip().split('\n'); outs.append((r.returncode, o[-1] if o else r.stderr[-200:]))
    check(outs[0][0] == 0, f'{name}（{sec:.1f}秒・{N}コマ・CSS の 動き {na}こ）：画面の 10% で 1秒に 3回 まで → {outs[0][1]}')
    check(outs[1][0] == 0, f'{name}：もっと きびしく（画面の 3%）→ {outs[1][1]}')
    print(f'    （{time.time() - t0:.0f}秒）', flush=True)


def settle(pg, sec=0.4):
    for i in range(int(sec * 60)): pg.evaluate(STEP, 1000 / 60)


def tap_play(pg, k, btn='set'):
    pg.locator(f'#cbOv .cbhand .cbc:has(img[src="cb_s{k}.webp"])').first.click(); pg.wait_for_timeout(60)
    pg.locator(f'#cbOv .cbmod [data-cb={btn}]').click(); pg.wait_for_timeout(60)


try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        for calm in (0, 1, 2):      # 0＝ふつう・1＝iPhone の「視差効果を減らす」・2＝プレイボード『白亜の宮殿』（第4.185版：3つ目・4つ目の 対戦 だけ）
            tag = ['', '_calm', '_marble'][calm]
            ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo', reduced_motion='reduce' if calm == 1 else 'no-preference')
            ctx.add_init_script(FAKE)
            pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.goto(APP); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(5200)
            pg.locator('#cbFab .fabi').click(); pg.wait_for_function("() => !!window.CBApp && !!document.querySelector('#cbOv.on')", timeout=30000); pg.wait_for_timeout(600)
            pg.evaluate("() => { CBApp._guard = 0; }")      # 聞く 窓が 出て すぐでも 押せる（うっかり 押し 防止は test_cb.py で 見る）
            print('■ ' + ['ふつう', '「演出を控えめにする」（動きを へらす）', 'プレイボード『白亜の宮殿』'][calm])
            pg.evaluate("() => { CBApp._t.manual(true); CBApp._think = () => 1e9; CBApp._opt = { hands: [['k', '1', '6', '6', '7'], ['2', '3', '6', '5', '7']], turns: 3 }; }")
            if calm == 2: pg.evaluate("() => { const T = CBApp._t; T.state.boards = ['marble']; T.state.board = 'marble'; T.save(); }"); pg.wait_for_timeout(100)
            want = lambda n: (not ONLY) or (n in ONLY)
            def seg(name, sec, pre):
                if want(name): run(pg, name + tag, sec, pre=pre)
                else: pre(); settle(pg, sec)
                settle(pg, 0.5)
            if calm < 2:
                # ① はじまり：「対戦 スタート」→ 配る → 手札が 入る →（第4.190版）ターンの はじめ：「6 の 効果」の 帯 → 聞く 窓「6 の 効果を 使う？」
                seg('deal', 4.6, lambda: pg.locator('#cbOv .cbmenu [data-cb=cpu]').click())
                # ② 6 の 効果を 使う → 見る カードを えらぶ → 効果の 札 → 見た カードを 大きく → セットへ
                pg.locator('#cbOv [data-cb=sixyes]').click(); pg.wait_for_timeout(60)
                seg('six_peek', 5.2, lambda: pg.locator('#cbOv .cbmod .pick .cbc').first.click())
                # ③ 1ターン目：自分が 神様馬を セット → 相手も セット → オープン（勝ち！）→ 片付け →「ターン 2」→「6 の 効果」の 帯 → 聞く 窓
                tap_play(pg, 'k'); settle(pg, 0.8)
                seg('open_win', 7.4, lambda: pg.evaluate(OPP, {'t': 'set', 'k': 2}))
                # ④ 2ターン目の はじめ：6 は 使わない →「神様馬の 効果」の 帯 → 聞く 窓 → 使わない
                seg('six_pre', 2.6, lambda: pg.locator('#cbOv [data-cb=sixno]').click())
                pg.locator('#cbOv [data-cb=kskip]').click(); settle(pg, 0.6)
                # ⑤ 2ターン目：相手が 先に 5 を セット → 自分が セット →「効果タイム」の 帯（相手の 5）→ 相手は 使わない → オープン（負け…）→「ターン 3」→「6 の 効果」
                pg.evaluate(OPP, {'t': 'set', 'k': 5}); settle(pg, 0.8)
                seg('set_efft', 2.6, lambda: tap_play(pg, '7'))
                seg('open_lose', 7.4, lambda: pg.evaluate(OPP, {'t': 'eff', 'use': {}}))
                # ⑥ 3ターン目：6 は 使わない → かぶり → 片付け → 結果（同点）
                pg.locator('#cbOv [data-cb=sixno]').click(); settle(pg, 0.6)
                pg.evaluate(OPP, {'t': 'set', 'k': 6}); settle(pg, 0.8)
                if want('end'): run(pg, 'end' + tag, 6.4, pre=lambda: tap_play(pg, '6'))
                else: tap_play(pg, '6'); settle(pg, 6.4)      # 第4.194版：場面を えらんで 写す とき（ONLY）も さいごまで 進める（前は 1つ目の 対戦が 終わらず「場面の とおり」が NG に なった）
                v = pg.evaluate("() => { const v = CBApp._t.view; return v ? [v.phase, v.res, v.my.wins, v.op.wins, v.discard.length] : null; }")
                check(v == ['end', 'draw', 1, 1, 6], f'場面の とおりに 進んだ（さいごまで：1勝 1勝 の 同点・捨て札 6まい）{v}')
                # ---- 2つ目の 対戦（第4.177版）：3 の 効果（聞く 窓 → 3まい 見せる → 交換）・勝ち → GET の 札 ----
                settle(pg, 1.0)
                pg.evaluate("() => { CBApp._t.menu(); CBApp._rng = () => 0.1; CBApp._opt = { hands: [['3', '3', '3', '1', '2'], ['4', '5', '6', '7', '7']], turns: 3 }; }"); pg.wait_for_timeout(100)
                pg.locator('#cbOv .cbmenu [data-cb=cpu]').click(); settle(pg, 3.4)
                tap_play(pg, '1'); settle(pg, 0.8)
                seg('ask3', 2.6, lambda: pg.evaluate(OPP, {'t': 'set', 'k': 7}))      # 「効果タイム」の 帯 → 聞く 窓（3 の カードの 絵・「3 の 効果を 使う？」）
                a3 = pg.evaluate("() => { const m = document.querySelector('#cbOv .cbmod.cbask'); return m ? m.querySelector('.askq b').textContent : null; }")
                seg('eff3_open', 12.6, lambda: pg.locator('#cbOv [data-cb=effyes]').click())      # 3 を 3まい 見せる 窓 → もらった カードを 大きく → 交換 → オープン（勝ち！）→「ターン 2」
                h2 = pg.evaluate("() => CBApp._t.view.my.hand.map(c => c.k).sort().join('')")
                tap_play(pg, '2'); settle(pg, 0.8); pg.evaluate(OPP, {'t': 'set', 'k': 6}); settle(pg, 5.6)      # 2ターン目：2 と 6 → 勝ち
                pg.evaluate(OPP, {'t': 'set', 'k': 7}); settle(pg, 0.8)
                if want('end_win'): run(pg, 'end_win' + tag, 7.0, pre=lambda: tap_play(pg, '3'))      # 3ターン目：3 と 7 → 勝ち → 結果「あなたの 勝ち！」→ GET の 札が ぽんと 出る
                else: tap_play(pg, '3'); settle(pg, 7.0)
                v2 = pg.evaluate("() => { const v = CBApp._t.view, b = document.querySelector('#cbOv .cbend .cbget'); return v ? [v.phase, v.res, v.my.wins, v.op.wins, b ? b.querySelector('.n').textContent : null] : null; }")
                # 第4.193版：GET の 札は 第4.192版の 漢字（＋1こ → ＋1個）に そろえた 文（test_cb.py と 同じ）
                check(a3 == '3 の 効果を 使う？' and h2 == '2334' and v2 == ['end', 'win', 3, 0, '＋1個 GET！'], f'2つ目の 対戦も 場面の とおり（聞く 窓「{a3}」・交換の あとの 手札 {h2}・3勝 0勝・GET の 札）{v2}')
            # ---- 3つ目の 対戦（第4.178版）：本番の 形（5ターン・手札 7まい）・夜の フィールド（火の あかりの ゆれ）・逆転勝利（自分 → 相手）----
            settle(pg, 1.0)
            pg.evaluate("() => { if (CBApp._t.screen !== 'menu') CBApp._t.menu(); CBApp._rng = () => 0.1; CBApp._opt = { hands: [['1', '1', '1', '2', '3', '6', '7'], ['m', '2', '2', '2', '4', '5', '6']] }; }"); pg.wait_for_timeout(100)
            seg('deal7', 3.8, lambda: pg.locator('#cbOv .cbmenu [data-cb=cpu]').click())      # 「対戦 スタート」→ 7まい ずつ 配る → 手札が 入る
            d7 = pg.evaluate("() => { const v = CBApp._t.view; return v ? [v.turns, v.my.hand.length, v.op.hand.length, v.deckN, document.querySelectorAll('#cbOv .cbfire').length, document.querySelector('#cbOv .cbboard').classList.contains('cust')] : null; }")
            seg('fire', 6.0, lambda: None)                                                    # 何も しない 6秒：火の あかりの ゆれ（5.6秒・4.3秒で 1回り）と 自分の わくの 光 だけ
            tap_play(pg, '1'); settle(pg, 0.8)
            seg('rev_open', 5.0, lambda: pg.evaluate(OPP, {'t': 'set', 'k': 'm'}))              # オープン：1 と 幻の馬 →「チャンス！」→ 聞く 窓「逆転の チャンス！／1 の 効果を 使う？」
            ar = pg.evaluate("() => { const m = document.querySelector('#cbOv .cbmod.cbask'); return m ? m.querySelector('h3').textContent + '｜' + m.querySelector('.askq b').textContent : null; }")
            seg('rev_use', 8.8, lambda: pg.locator('#cbOv .cbask [data-cb=revyes]').click())    # 1 を 3まい 見せる 窓 → 1まいが 捨て札へ →「逆転勝利！」→ 片付け →「ターン 2」
            r1 = pg.evaluate("() => { const v = CBApp._t.view; return [v.turn, v.my.wins, v.op.wins, v.my.hand.map(c => c.k).sort().join('')]; }")
            tap_play(pg, '1'); settle(pg, 0.8)
            seg('rev_op_open', 5.0, lambda: pg.evaluate(OPP, {'t': 'set', 'k': '2'}))           # オープン：1 と 2（相手は 2 が 3まい）→「勝負は まだ！」→ 相手を 待つ
            seg('rev_op_use', 8.8, lambda: pg.evaluate(OPP, {'t': 'rev', 'use': True}))         # 相手が 2 を 3まい 見せる 窓 → 捨て札へ →「逆転負け…」→ 片付け →「ターン 3」
            r2 = pg.evaluate("() => { const v = CBApp._t.view; return [v.turn, v.my.wins, v.op.wins, v.op.hand.length, v.phase]; }")
            check(d7 == [5, 7, 7, 16, 2, calm == 2] and ar == '逆転の チャンス！｜1 の 効果を 使う？' and r1 == [2, 1, 0, '12367'] and r2 == [3, 1, 1, 4, 'set'],
                  f'3つ目の 対戦も 場面の とおり（5ターン・手札 7まい・山札 16・火の あかり 2つ・『白亜の宮殿』の とき だけ ボードが cust {d7}・聞く 窓「{ar}」・自分の 逆転勝利 {r1}・相手の 逆転勝利 {r2}）')
            # ---- 4つ目の 対戦（第4.185版）：相手が 7 を 4まい 見せて 強さ 逆転 ----
            settle(pg, 1.0)
            pg.evaluate("() => { CBApp._t.menu(); CBApp._rng = () => 0.1; CBApp._opt = { hands: [['2', '3', '4', '5', '6', '1', 'k'], ['7', '7', '7', '7', '1', '2', '3']], turns: 3 }; }"); pg.wait_for_timeout(100)
            pg.locator('#cbOv .cbmenu [data-cb=cpu]').click(); settle(pg, 3.4)
            seg('x7r', 8.0, lambda: pg.evaluate(OPP, {'t': 'x7r'}))      # 第4.187版：セットの 前に 相手が 使う：効果の 札 → 4まいの 窓 → 1まい 捨て札へ →「強さ 逆転！」
            tap_play(pg, '2'); settle(pg, 0.8)
            seg('x7r_open', 6.0, lambda: pg.evaluate(OPP, {'t': 'set', 'k': '1'}))      # 相手が ふせて セット → オープン（2 が 1 に 勝つ・強さ 逆転中）→「ターン 2」
            r7 = pg.evaluate("() => { const v = CBApp._t.view; return v ? [v.rv, v.turn, v.my.wins, v.op.wins, v.op.hand.filter(c => c.k === '7').length, document.querySelector('#cbOv .cbturn').textContent.indexOf('強さ 逆転中') >= 0] : null; }")
            check(r7 == [True, 2, 1, 0, 3, True], f'4つ目の 対戦も 場面の とおり（相手が セットの 前に 7 を 4まい 見せて 逆転 → 2 が 1 に 勝つ・相手の 7 が 3まい 見える・「強さ 逆転中」{r7}）')
            # ---- 6つ目（第4.197版）：決戦宝石：配る → ケース（使える 宝石が ゆっくり 光る）→ 宝石を タップ → 窓 → 使う（宝石が はねる・トークンが 手札へ・帯）→ 使わなかった トークンが ターンの 終わりに 消える ----
            settle(pg, 1.0)
            pg.evaluate("() => { const T = CBApp._t; if (T.screen !== 'menu') T.menu(); CBApp._rng = () => 0.1; CBApp._opt = { hands: [['1', '2', '3', '6', '7'], ['2', '3', '4', '5', '6']], turns: 3, gems: [['m', 'k', '1', '3', '7'], []] }; }"); pg.wait_for_timeout(100)
            seg('gem_deal', 4.6, lambda: pg.locator('#cbOv .cbmenu [data-cb=cpu]').click())      # 配る → 手札の 下に 宝石ケース（使える 宝石が ゆっくり 光る：2.4秒で 1回）
            seg('gem_ask', 1.6, lambda: pg.locator('#cbOv .cbgem .g[data-g="1"]').click())        # 宝石を タップ →「双炎のルビー」の 窓（宝石 ▶ トークン）
            seg('gem_use', 3.6, lambda: pg.locator('#cbOv .cbmod.cbgemm [data-cb=gemgo]').click())   # 使う → 宝石が はねる・トークンが 手札へ とぶ・帯「双炎のルビー！」
            tap_play(pg, '2'); settle(pg, 0.8)
            seg('gem_tokgone', 7.0, lambda: pg.evaluate(OPP, {'t': 'set', 'k': 3}))      # オープン（負け）→ 片付け → 使わなかった トークンが 消える →「ターン 2」
            g6 = pg.evaluate("() => { const v = CBApp._t.view; return v ? [v.turn, v.my.hand.filter(c => c.tok).length, v.my.gem.used.join(''), document.querySelectorAll('#cbOv .cbgem .g').length] : null; }")
            check(g6 == [2, 0, '1', 5], f'6つ目の 対戦（決戦宝石）も 場面の とおり（2ターン目・トークンは 消えた・使った 宝石 1・ケースに 5つ）{g6}')
            # ---- 7つ目（第4.199版・まさちゃん 22:01）：7トークンで 7 の 効果 ＝ 7トークンを 見せて 捨てる → 山札から 3枚 引く ----
            settle(pg, 1.0)
            pg.evaluate("() => { const T = CBApp._t; if (T.screen !== 'menu') T.menu(); CBApp._rng = () => 0.1; CBApp._opt = { hands: [['1', '2', '3', '4', '5'], ['2', '3', '4', '5', '6']], turns: 3, gems: [['7'], []] }; }"); pg.wait_for_timeout(100)
            pg.locator('#cbOv .cbmenu [data-cb=cpu]').click(); settle(pg, 4.6)
            pg.locator('#cbOv .cbgem .g[data-g="7"]').click(); settle(pg, 0.6)
            pg.locator('#cbOv .cbmod.cbgemm [data-cb=gemgo]').click(); settle(pg, 3.0)
            tap_play(pg, '1'); settle(pg, 0.8)
            pg.evaluate(OPP, {'t': 'set', 'k': 2}); settle(pg, 2.2)                          # 2人とも セット →「効果タイム」→ 7 の 効果を 使う？
            seg('gem7_x7', 6.0, lambda: pg.locator('#cbOv [data-cb=effyes]').click())      # 使う → 効果の 札 → 7トークン 1枚を 見せる 窓 → 捨て札へ とぶ → 山札から 3枚
            g7 = pg.evaluate("() => { const v = CBApp._t.view; return v ? [v.my.hand.filter(c => c.tok).length, v.discard.filter(d => d.tok && d.k === '7' && d.why === '7').length, v.my.gem.used.join('')] : null; }")
            check(g7 == [0, 1, '7'], f'7つ目の 対戦（7トークンで 7 の 効果）も 場面の とおり（トークンは 捨て札へ・使った 宝石 7）{g7}')
            if calm < 2:
                # ---- 5つ目（第4.189版）：カードパック ----
                settle(pg, 1.0)
                pg.evaluate("() => { const T = CBApp._t; T.menu(); T.state.coin = 1000; T.state.pkh = []; T.state.packs = 0; T.save(); window.__q = [0, 3, 6, 9, 225, 0, 1, 4, 7, 10, 100, 2]; CBApp._randInt = n => (n === 1679616 ? 1 : window.__q.shift()); }"); pg.wait_for_timeout(100)
                pg.locator('#cbOv .cbmenu [data-cb=dz]').click(); settle(pg, 0.5)
                seg('pk_tab', 5.2, lambda: None)                                                        # カードパックの タブ：パックの 絵（光の すじが 5秒に 1回 ゆっくり 通る）
                pg.locator('#cbOv .cbdz [data-cb=pkask]').click(); settle(pg, 0.3)
                seg('pk_pack', 3.0, lambda: pg.locator('#cbOv .cbmod [data-cb=pkgo]').click())         # 「開ける」→ パックの 画面：パックが 出る（ゆれる）
                seg('pk_open', 6.0, lambda: pg.locator('#cbOv .cbpk .pkart.big').click())               # タップ → 上の ギザギザが 切れて とぶ → カードが 1まいずつ 出て パックの うしろに ならぶ → パックが 下へ 消える → ノーマル 4まいを めくる → くじが ゆっくり ひかる
                seg('pk_rev_gsr', 3.2, lambda: pg.locator('#cbOv .cbpk [data-cb=pklast]').click())     # くじを めくる：神様馬の 超レア（光の すじ・光が ひろがる）
                pg.locator('#cbOv .cbpk [data-cb=pkmore]').click(); settle(pg, 0.3); pg.locator('#cbOv .cbmod [data-cb=pkgo]').click(); settle(pg, 0.8)
                pg.locator('#cbOv .cbpk .pkart.big').click(); settle(pg, 5.4)
                seg('pk_rev_r', 3.0, lambda: pg.locator('#cbOv .cbpk [data-cb=pklast]').click())       # もう 1パック：レアの くじ
                pk = pg.evaluate("() => { const s = CBApp._t.state, p = CBApp._t.pk; return [p && p.st, s.pkh.map(h => h.g + ':' + h.cards.join(',')), s.coin]; }")
                check(pk == ['done', ['gsr:ka,mb,2a,3b,ksr', 'r:kb,1a,2b,4a,3r'], 776], f'カードパックも 場面の とおり（神様馬の 超レア → レア・コイン 1000 → 776）{pk}')
                pg.evaluate("() => { CBApp._randInt = null; CBApp._t.menu(); }")
            check(not errs, f'エラー なし {errs[:3]}')
            ctx.close()
finally:
    srv.terminate()
print('\n' + ('全部 OK' if not fails else f'NG {len(fails)}こ：' + ' / '.join(fails)))
sys.exit(1 if fails else 0)
