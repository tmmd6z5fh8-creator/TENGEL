# 馬カードバトル（第4.176版）の 光の 点めつ：対戦の 動き（配る・セット・「効果タイム」の 帯・効果・オープン・勝ち負けの 字・「ターン」「神様馬の 効果」の 帯・結果）を 60コマ／秒の 絵に して kisekae/flash_px.py で 数える
#   決まり：画面の 10% 以上の 広さで 1秒に 3回 まで（もっと きびしい 3% でも 数えて 出す）。「演出を控えめにする」（動きを へらす 設定）でも 数える
#   時計は 手で 進める（CBApp._t.manual・tick：1/60秒 ずつ）。CSS の 動き（transition・animation）は 出て きた 時刻を 覚えて、同じ 時計で 進める
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
  V.track = V.track.filter(o => { try { o.a.currentTime = Math.max(0, now - o.at); return true; } catch (e) { return false; } });
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
        for calm in (0, 1):
            tag = '_calm' if calm else ''
            ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo', reduced_motion='reduce' if calm else 'no-preference')
            ctx.add_init_script(FAKE)
            pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.goto(APP); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(5200)
            pg.locator('#cbFab .fabi').click(); pg.wait_for_function("() => !!window.CBApp && !!document.querySelector('#cbOv.on')", timeout=30000); pg.wait_for_timeout(600)
            print('■ ' + ('「演出を控えめにする」（動きを へらす）' if calm else 'ふつう'))
            pg.evaluate("() => { CBApp._t.manual(true); CBApp._think = () => 1e9; CBApp._opt = { hands: [['k', '1', '6', '6', '7'], ['2', '3', '6', '5', '7']] }; }")
            want = lambda n: (not ONLY) or (n in ONLY)
            def seg(name, sec, pre):
                if want(name): run(pg, name + tag, sec, pre=pre)
                else: pre(); settle(pg, sec)
                settle(pg, 0.5)
            # ① はじまり：「対戦 スタート」→ 配る → 手札が 入る
            seg('deal', 3.2, lambda: pg.locator('#cbOv .cbmenu [data-cb=cpu]').click())
            # ② 1ターン目：自分が 神様馬を セット → 相手も セット →「効果タイム」の 帯 →「6 の 効果を 使う？」
            tap_play(pg, 'k'); settle(pg, 0.8)
            seg('efft', 2.4, lambda: pg.evaluate(OPP, {'t': 'set', 'k': 2}))
            # ③ 6 の 効果を 使う → 見た カードを 大きく → オープン（勝ち！）→ 片付け →「ターン 2」→「神様馬の 効果」の 帯
            pg.locator('#cbOv .cbact [data-cb=effyes]').click(); pg.wait_for_timeout(60)
            seg('eff6_open', 8.6, lambda: pg.locator('#cbOv .cbmod .pick .cbc').first.click())
            pg.locator('#cbOv .cbact [data-cb=kskip]').click(); settle(pg, 0.6)      # 2ターン目の はじめ：神様馬の 効果は 使わない
            # ④ 2ターン目：相手が 先に セット → 自分が セット →「効果タイム」→ 使わない → オープン（負け…）→「ターン 3」
            pg.evaluate(OPP, {'t': 'set', 'k': 3}); settle(pg, 0.8)
            seg('set_efft', 2.6, lambda: tap_play(pg, '7'))
            seg('open_lose', 5.4, lambda: pg.locator('#cbOv .cbact [data-cb=effno]').click())
            # ⑤ 3ターン目：かぶり → 片付け → 結果（同点）
            pg.evaluate(OPP, {'t': 'set', 'k': 6}); settle(pg, 0.8)
            if want('end'): run(pg, 'end' + tag, 6.4, pre=lambda: tap_play(pg, '6'))
            v = pg.evaluate("() => { const v = CBApp._t.view; return v ? [v.phase, v.res, v.my.wins, v.op.wins, v.discard.length] : null; }")
            check(v == ['end', 'draw', 1, 1, 6], f'場面の とおりに 進んだ（さいごまで：1勝 1勝 の 同点・捨て札 6まい）{v}')
            check(not errs, f'エラー なし {errs[:3]}')
            ctx.close()
finally:
    srv.terminate()
print('\n' + ('全部 OK' if not fails else f'NG {len(fails)}こ：' + ' / '.join(fails)))
sys.exit(1 if fails else 0)
