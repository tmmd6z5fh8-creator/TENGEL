# 決戦調査（第4.196版）の 光の 点めつ：マップ（開いて いる エリアの 光る 輪・その 場に 出る ふきだし）・フィールド（セリフ・テロップ・敵が 光って 出る・土けむり）・バトルの はじまり・
#   HP が へる（ゆれ・盾の 光）・勝利の 演出 3段階（光の 筋・光の 輪・紙吹雪・コインの 雨・コインの 数が ふえる）・エリアが 開く（鍵が 消える）を 60コマ／秒で 写して 数える
#   決まり：画面の 10% 以上の 広さで 1秒に 3回 まで（もっと きびしい 3% でも 数えて 出す）。「演出を控えめにする」（動きを へらす 設定）でも 数える
#   時計は 手で 進める（CBApp._t.manual・tick：1/60秒 ずつ）。CSS の 動きも 同じ 時計で 進める（test_cb_flash.py と 同じ しくみ）
#   第4.200版：敵は まさちゃんの 表の 行で 出る（q_appear：セリフの 窓は その まま）・さいごの 行の あと 名前 と「タップで バトル開始！」（q_end）
#   python3 test_cb_quest_flash.py [場面の 名前,…]   （時間が かかる ので ふだんの テストとは 別に 動かす。コマは t5/cbq_frames/<場面>/ に 残す）
import json, os, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
from toys_for_test import open_toys      # 第4.212版：おもちゃ（TENGERカードバトル・お世話チャレンジ）を 0P で 解放した ことに する（テスト用）
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W); sys.path.insert(0, os.path.join(W, 'kisekae'))
SRV = os.path.join(W, 'srv_cbqf'); PORT = 8816; APP = f'http://localhost:{PORT}/APP/'
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


SRC = open(os.path.join(W, 'test_cb_flash.py'), encoding='utf8').read()
FAKE = open(os.path.join(W, 'test_cb.py'), encoding='utf8').read().split('FAKE = """')[1].split('"""')[0]
STEP = SRC.split('STEP = """')[1].split('"""')[0]      # 1コマ 進める（test_cb_flash.py と 同じ）
OPP = SRC.split('OPP = """')[1].split('"""')[0]
WIN = {'turns': 1, 'hands': [['k', '1', '2', '3', '4', '5', '6'], ['7', '7', '6', '2', '3', '1', 'm']]}


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


FD = os.path.join(W, 't5', 'cbq_frames')


def run(pg, name, sec, pre=None):
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


def settle(pg, sec=0.4, dt=1000 / 60):
    for i in range(int(sec * 1000 / dt)): pg.evaluate(STEP, dt)


def until(pg, js, sec=30, dt=50):
    for i in range(int(sec * 1000 / dt)):
        if pg.evaluate(js): return True
        pg.evaluate(STEP, dt)
    return False


try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        for calm in (0, 1):
            tag = ['', '_calm'][calm]
            ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo', reduced_motion='reduce' if calm else 'no-preference')
            ctx.add_init_script(FAKE)
            pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.goto(APP); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(5200)
            open_toys(pg, ('cb',))      # 第4.212版：TENGERカードバトルは おもちゃ（3,000P で 解放）→ ここでは 解放ずみに する
            pg.locator('#cbFab .fabi').click(); pg.wait_for_function("() => !!window.CBApp && !!document.querySelector('#cbOv.on')", timeout=30000); pg.wait_for_timeout(600)
            pg.evaluate(f"() => {{ CBApp._guard = 0; CBApp._t.manual(true); CBApp._think = () => 1e9; CBApp._qopt = () => ({json.dumps(WIN)}); CBApp._now = () => new Date('2026-11-18T12:00:00'); CBApp._rng = () => 0.1; CBApp._t.load(); CBApp._t.menu(); }}")
            settle(pg, 0.5, 50)
            print('■ ' + ['ふつう', '「演出を控えめにする」（動きを へらす）'][calm])
            want = lambda n: (not ONLY) or (n in ONLY)
            def seg(name, sec, pre):
                if want(name): run(pg, name + tag, sec, pre=pre)
                else: pre(); settle(pg, sec, 50)
                settle(pg, 0.3, 50)
            def win_fight(capture=None, sec=11.0):
                """1ターンの 戦：神様馬を セット → 敵は 7（capture＝その 名前で 写す）"""
                until(pg, "() => CBApp._t.screen === 'game' && CBApp._t.view && CBApp._t.view.can.set && CBApp._t.idle")
                pg.locator('#cbOv .cbhand .cbc[data-ck="k"]').first.click(); pg.wait_for_timeout(40)
                pg.locator('#cbOv .cbmod [data-cb=set]').click(); settle(pg, 0.6, 50)
                if capture: seg(capture, sec, lambda: pg.evaluate(OPP, {'t': 'set', 'k': '7'}))
                else: pg.evaluate(OPP, {'t': 'set', 'k': '7'})
                until(pg, "() => !!document.querySelector('#cbOv .cbmod.on.qend, #cbOv .cbmod.on.qvic')")
            def to_field(lv, capture=False):
                pg.evaluate("() => { const T = CBApp._t; T.state.qt = { n: 15, at: Date.now() }; T.save(); }")      # 第4.203版：調査隊切符を 満タンに（戦が 多い ので）
                if capture: seg('q_pop', 1.5, lambda: pg.locator(f'#cbOv .qnd[data-lv="{lv}"]').click())      # 第4.196版：マップの その 場に ふきだし（まさちゃん 16:47）
                else: pg.locator(f'#cbOv .qnd[data-lv="{lv}"]').click(); settle(pg, 0.3, 50)
                if capture: seg('q_field', 3.4, lambda: pg.locator('#cbOv .qpo [data-cb=qgo]').click())
                else: pg.locator('#cbOv .qpo [data-cb=qgo]').click()
                n, en = pg.evaluate(f"() => {{ const x = CBApp._t.quest.data[{lv - 1}]; return [x.say.length, x.en]; }}")
                for i in range(n):
                    until(pg, f"() => CBApp._t.quest.scene.i === {i} && !CBApp._t.quest.scene.typing")
                    if capture and i == en - 2: seg('q_appear', 4.4, lambda: pg.locator('#cbOv .qfw').click())      # 第4.200版：この タップで 次の 行と いっしょに テロップ → 敵が 光って 出る（セリフの 窓は その まま）
                    elif capture and i == n - 1: seg('q_end', 2.6, lambda: pg.locator('#cbOv .qfw').click())         # さいごの 行の あと：窓が 消える → 名前 →「タップで バトル開始！」
                    else: pg.locator('#cbOv .qfw').click(); settle(pg, 0.1, 50)
                until(pg, "() => !!document.querySelector('#cbOv .qtap.on')")
            # ① マップ（開いて いる エリアの 光る 輪・「挑戦！」）
            seg('q_map', 3.0, lambda: pg.locator('#cbOv .cbmenu [data-cb=quest]').click())
            # ② フィールド：出て くる → セリフ（字が 1つずつ）／ ③ 第4.200版：敵が 出る 行（レベル1 は 2行目）→ テロップ → 敵が 光って 出る ／ ④ さいごの 行の あと → 名前 →「タップで バトル開始！」
            to_field(1, capture=True)
            # ④ バトルの はじまり（「第1戦 スタート」→ 配る）
            seg('q_start', 4.0, lambda: pg.locator('#cbOv .qfw').click())
            # ⑤ 勝つ → オープン → ダメージ（HP が へる・ゆれる・盾が 光る）→「討伐！」→ 勝利の 演出 1段階目 → コイン GET
            win_fight('q_vic1', 12.0)
            # ⑥ マップへ：次の エリアが 開く（鍵が 消える）
            seg('q_unlock', 3.0, lambda: pg.locator('#cbOv .cbmod [data-cb=qmapgo]').click())
            # ⑦ レベル2 の 1戦目：HP が 半分に → あいだの 窓
            to_field(2); pg.locator('#cbOv .qfw').click()
            win_fight('q_hit', 9.0)
            hp = pg.evaluate("() => Math.round(document.querySelector('#cbOv .qhp .fill').getBoundingClientRect().width / document.querySelector('#cbOv .qhp .qbar').getBoundingClientRect().width * 100)")
            check(hp == 50, f'場面の とおり：レベル2 の 1戦目に 勝って HP が 半分（{hp}%）')
            pg.locator('#cbOv .cbmod [data-cb=qmapgo]').click(); settle(pg, 0.5, 50)
            # ⑧ 2段階目（レベル6）・3段階目（レベル10）
            for lv, nf, name in ((6, 4, 'q_vic2'), (10, 6, 'q_vic3')):
                pg.evaluate(f"() => {{ CBApp._t.state.q.clr = {lv - 1}; CBApp._t.save(); }}")
                pg.locator('#cbOv [data-cb=qx]').click(); settle(pg, 0.2, 50); pg.locator('#cbOv .cbmenu [data-cb=quest]').click(); settle(pg, 0.4, 50)
                to_field(lv); pg.locator('#cbOv .qfw').click()
                for n in range(1, nf + 1):
                    win_fight(name if n == nf else None, 12.0)
                    if n < nf: pg.locator('#cbOv .cbmod [data-cb=qnext]').click(); settle(pg, 0.3, 50)
                v = pg.evaluate("() => [document.querySelector('#cbOv .qv') && document.querySelector('#cbOv .qv').className, CBApp._t.state.q.clr]")
                check(v == [f'qv t{2 if lv == 6 else 3}', lv], f'場面の とおり：レベル{lv} を 討伐 → {v[0]}')
                pg.locator('#cbOv .cbmod [data-cb=qmapgo]').click(); settle(pg, 0.5, 50)
            check(not errs, f'エラー なし {errs[:3]}')
            ctx.close()
finally:
    srv.terminate()
    shutil.rmtree(SRV, ignore_errors=True)
print('\n' + ('全部 OK' if not fails else f'NG {len(fails)}こ：' + ' / '.join(fails)))
sys.exit(1 if fails else 0)
