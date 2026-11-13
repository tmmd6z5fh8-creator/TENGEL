# トレーニングセンター：ポイント特化ゾーン（第4.165版）の テスト
#   まさちゃん 2026/11/13 12:51「トレーニングセンターの抽選に ・ポイントの特化ゾーンを作る (レバーを押し込め！で、60%で上乗せ) 1回の抽選の1/699で入る スタート1000P MAX25000P
#     レバーの画像は、一個目のファイル　上乗せの場合は、虹色の光とドゥルルルン！ギュウィーンンン！の効果音 は上乗せ失敗の場合は、ピューン…とエネルギーが落ちた時のような効果音つけて！
#     ・ゾーン1回の平均獲得、約4000P ・MAXまでに必要な成功回数、12回連続上乗せ　特化ゾーンも、トレーニングセンターの説明書に追加」
#   ・抽選：いつもの 表・幻の馬・神様馬の どの 表にも 1/699（高確ゾーンは ほかと 同じ 4倍）。入った ときに 上乗せの 回数（1回ごとに 60%・12回まで）と 合計（1,000P ＋ 2,000P × 回数）を 決めて 保存
#     → 演出の 途中で 閉じても 次に 開いた ときに もらえる・2回 もらえない
#   ・演出（tc/tc_fx.js の zone）：レバーを タップ → 上乗せ（虹色の 光・音 tc_se_zn_up）／失敗（音 tc_se_zn_down）→ 合計の 札 → とじる。押さなくても 進む（20秒で 自動）
#   ・ちかちか しない：1/30秒ごとに 描いて（TCFX.zoneFrame：時計を 使わない）明るさを 測る（光の 点めつは 1秒に 3回 まで ＝ 向きがえ 6回 まで・画面 ぜんぶは 1秒に 1回 まで）
#   ・絵が ない とき（CI）：かんたんな 絵で 同じ 流れ
#   説明書の 項目は test_tc.py・道具箱の ボタンは test_tc_test.py で 見る
#   python3 test_tc_zone.py   （ios/tc_assets/ が ある とき だけ 画面の テスト。ない とき（CI）は 中身の 見くらべ と 数の 確かめ）
import json, math, os, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv_tc'); PORT = 8799; STORE = f'http://localhost:{PORT}/STORE/'
SHOT = os.environ.get('SHOT')          # 画面を 写す フォルダ（見る 用）
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'STORE')], check=True, stdout=subprocess.DEVNULL, env=dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, TARGET='app'))
from assets_dir import adir
TCA = adir('tc_assets'); HAVE = os.path.isdir(TCA) and len(os.listdir(TCA)) > 100
pth = os.path.join(SRV, 'STORE', 'index.html'); html = open(pth, encoding='utf8').read()
assert "window.__NATIVE = location.protocol === 'tengel:';" in html
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
if HAVE:
    for f in os.listdir(TCA): shutil.copy(os.path.join(TCA, f), os.path.join(SRV, 'STORE', f))
else: print('※ トレーニングセンターの 絵と 音（ios/tc_assets）が ない ので、中身の 見くらべ と 数の 確かめ だけ')
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c: fails.append(label)


_tc = open(os.path.join(W, 'test_tc.py'), encoding='utf8').read()
FAKE = _tc.split('FAKE = """')[1].split('"""')[0]                      # アプリの 窓口の にせもの（test_tc.py と 同じ）
D, START, ADD, RATE, MAX = 699, 1000, 2000, 0.6, 12                    # まさちゃんの きまり（tc/tc_app.js の ZONE と 同じ）
ZV = lambda n: START + ADD * n
ZP = lambda n: RATE ** n * (1 - RATE) if n < MAX else RATE ** MAX      # 上乗せ n回で おわる 確率
ZN = dict(ready=1.3, cyc=1.5, buf=0.3, r0=0.16, fail=1.9, maxEnd=1.75, auto=20, hold=1.0, close=3.2)      # 演出の 時間の きまり（tc/tc_fx.js の ZN と 同じ）


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


def stage_xy(pg, x, y):               # フィールドの 座標（1052×1657）→ 画面
    r = pg.evaluate("() => { const b = document.querySelector('#tcOv .tcst').getBoundingClientRect(); return [b.left, b.top, b.width, b.height]; }")
    return r[0] + x / 1052 * r[2], r[1] + y / 1657 * r[3]


def stage_click(pg, x, y):
    pg.mouse.click(*stage_xy(pg, x, y))


def shot(pg, name):
    if SHOT: os.makedirs(SHOT, exist_ok=True); pg.screenshot(path=os.path.join(SHOT, name + '.png'))


def open_tc(pg, url):
    pg.goto(url); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(600)
    pg.locator('#tcFab .fabi').click()
    pg.wait_for_function("() => window.TCApp && document.querySelector('#tcOv.on') && !document.querySelector('#tcOv .tcld')", timeout=120000)
    pg.evaluate("() => TCApp._t.govSet(0, true)"); pg.wait_for_timeout(1200)      # 絵の 細かさは かえない（おそい テストの 機械で 下がらない ように）
    pg.evaluate("() => { const st = TCApp.state, S = TCCare.S; st.stock = 20; S.stock = S.stockShow = 20; st.stockAt = Date.now() + 7200000; }")      # トークンは 20こ（時間で たまらない ように）


WAL = "() => TengelWallet.total() + TengelWallet.hold().total"
EVS = "() => TengelWallet.events().filter(e => /^tc-/.test(e.id)).map(e => [e.amount, e.what])"
# 鳴らした 音の 名前を 記録（tc_se_ と .m4a は とる・音量が 1 で ない ときは ×音量）
SE_WRAP = "() => { const S = TCApp._snd; if (S.__w) return; S.__w = 1; const o = S.se.bind(S); window.__seL = []; S.se = (n, g, l) => { window.__seL.push(n.replace('tc_se_', '').replace('.m4a', '') + (g != null && g !== 1 ? '×' + g : '')); return o(n, g, l); }; }"
SES = "() => { const a = (window.__seL || []).slice(); if (window.__seL) window.__seL.length = 0; return a; }"
PUSH_LIVE = "() => { const S = TCCare.S; return !!(S.push && S.push.hideT == null && !S.fxHold && S.lastT >= S.push.lock + 0.05); }"
# PUSH を 押す（本物の 指の 出来事）。その 間 だけ くじ（Math.random）を 決めた 数の ならびに する：1つめ＝抽選・2つめ＝当たりの しるしの 番号・3つめ から＝上乗せ（0.6 より 小さければ 成功）
PRESS = """([seq]) => { const S = TCCare.S, G = TCCare.PUSHG, st = document.querySelector('#tcOv .tcst'), cv = document.querySelector('#tcOv .tco'), r = st.getBoundingClientRect();
  const o = { bubbles: true, clientX: r.left + G.x / 1052 * r.width, clientY: r.top + G.y / 1657 * r.height, pointerId: 7, pointerType: 'touch', isPrimary: true }, R = Math.random, q = (seq || []).slice(), s0 = S.stock;
  S.high = 0; TCApp.state.high = 0;
  Math.random = () => (q.length ? q.shift() : 0.5);
  try { cv.dispatchEvent(new PointerEvent('pointerdown', o)); } finally { Math.random = R; }
  cv.dispatchEvent(new PointerEvent('pointerup', o)); return [s0 - S.stock, q.length]; }"""
FX_ON = "() => document.querySelector('#tcOv .tcfx').classList.contains('on')"


def seq_for(n):                        # 上乗せ n回の 特化ゾーンが 出る くじの ならび（n＝12 は 12回とも 成功：13回めは ひかない）
    return [0.0005, 0.5] + [0.1] * n + ([0.9] if n < MAX else [])


def feed(pg, item=1):                  # ごはん（リンゴ）→ PUSH が 出る まで
    stage_click(pg, 327, 1494)
    pg.wait_for_function("() => !!TCCare.S.chooser", timeout=20000); pg.wait_for_timeout(700)
    stage_click(pg, 270 + 256 * item, 1262)
    pg.wait_for_function(PUSH_LIVE, timeout=120000); pg.wait_for_timeout(400)


def tap_fx(pg):                        # 演出の キャンバス（レバー）を タップ
    stage_click(pg, 526, 1050)


def run_zone(pg, n, taps=True, name=None, limit=120):      # PUSH を 押して 特化ゾーン（上乗せ n回）→ おわる まで。返り値＝（押した 結果・演出が 出て いた 秒・とちゅうの 絵を とったか）
    pg.evaluate(SES); r = pg.evaluate(PRESS, [seq_for(n)])
    pg.wait_for_function(FX_ON, timeout=20000); t0 = time.time(); shots = 0
    need = n + 1 if n < MAX else n
    if taps:
        pg.wait_for_timeout(int(ZN['ready'] * 1000) + 250)
        for i in range(need):
            tap_fx(pg)
            if name and i in (0, need - 1): pg.wait_for_timeout(650); shot(pg, f'{name}_tap{i + 1}'); shots += 1; pg.wait_for_timeout(int(ZN['cyc'] * 1000) - 650 + 120)
            else: pg.wait_for_timeout(int(ZN['cyc'] * 1000) + 120)
        pg.wait_for_timeout(int(((ZN['fail'] if n < MAX else ZN['maxEnd']) - ZN['cyc'] + ZN['hold']) * 1000) + 500)
        if name: shot(pg, f'{name}_card'); shots += 1
        tap_fx(pg)                     # とじる
    for _ in range(limit * 4):
        if not pg.evaluate(FX_ON): break
        pg.wait_for_timeout(250)
    return r, time.time() - t0, shots


try:
    # ---------- 中身の 見くらべ・数の 確かめ（絵が なくても）----------
    print('■ 中身と 数')
    sb = open(os.path.join(SRV, 'STORE', 'tc_bundle.js'), encoding='utf8').read()
    check('const ZONE = { d: 699, start: 1000, add: 2000, rate: 0.6, max: 12 }' in sb and "[1 / ZONE.d, { k: 'zn' }]" in sb and sb.count("[1 / ZONE.d, { k: 'zn' }]") == 3 and "'tc_se_zn_up.m4a'" in sb and "'tc_se_zn_down.m4a'" in sb
          and 'tc_zn_geom.json' in sb and 'ポイント特化ゾーン' in sb and 'レバーを押し込め！' in sb,
          'tc_bundle.js（App Store版）：きまり（1/699・スタート 1,000P・＋2,000P・60%・12回）・3つの 表（いつも・幻の馬・神様馬）・上乗せ／失敗の 音・レバーの 絵・説明書の 言葉が 入って いる')
    E = sum(ZV(n) * ZP(n) for n in range(MAX + 1))
    check(abs(sum(ZP(n) for n in range(MAX + 1)) - 1) < 1e-12 and ZV(0) == 1000 and ZV(MAX) == 25000 and abs(E - 3993.47) < 0.01 and round(E / 100) * 100 == 4000 and abs(ZP(MAX) - 0.002177) < 1e-6,
          f'数：スタート 1,000P・12回 つづけて 上乗せで MAX 25,000P（そう なるのは {ZP(MAX):.3%}）・ゾーン 1回の 平均 {E:,.1f}P（＝約4,000P）・確率を 足すと 1')
    per = E / D
    check(abs(per - 5.713) < 0.01, f'1回の 抽選あたり ＋{per:.2f}P（1/699 × 平均 {E:,.0f}P）')
    src = open(os.path.join(W, 'tc', 'tc_fx.js'), encoding='utf8').read()
    zsrc = src.split('// ================= ポイント特化ゾーン')[1]
    check('confirm(' not in zsrc and 'alert(' not in zsrc and 'Date.now' not in zsrc.split('function znDraw')[1].split('const znZ')[0] and 'performance.now' not in zsrc.split('function znDraw')[1].split('const znZ')[0] and 'Math.random' not in zsrc,
          '演出は confirm()・alert() の 窓を 使わない・1コマの 絵は 押した 時刻と いまの 時刻 だけで 決まる（時計も くじも 使わない ＝ 測った とおりに 出る）')
    lst = subprocess.run(['git', 'ls-files'], cwd=os.path.dirname(W), capture_output=True, text=True).stdout.split('\n')
    check(not any(f.endswith(('.glb', 'tc_zn_back.webp', 'tc_zn_ball.webp', 'tc_zn_arrow.webp', 'tc_zn_geom.json', 'tc_se_zn_up.m4a', 'tc_se_zn_down.m4a')) or '/tc_assets/' in f or '/work/lever/' in f for f in lst)
          and os.path.exists(os.path.join(W, 'kisekae', 'tc', 'zone_asset.py')) and os.path.exists(os.path.join(W, 'kisekae', 'tc', 'snd', 'sfx_zone.py')),
          'まさちゃんの レバーの 3D・できた 絵と 音は リポジトリに 入って いない・作る 道具（kisekae/tc/zone_asset.py・kisekae/tc/snd/sfx_zone.py）は ある')
    if HAVE:
        from PIL import Image
        G = json.load(open(os.path.join(TCA, 'tc_zn_geom.json'), encoding='utf8')); sz = {k: Image.open(os.path.join(TCA, f'tc_zn_{k}.webp')).size for k in ('back', 'ball', 'arrow')}
        P = G['parts']; inb = all(0 <= P[k]['x'] and P[k]['x'] + P[k]['w'] <= G['w'] and 0 <= P[k]['y'] and P[k]['y'] + P[k]['h'] <= G['h'] for k in P)
        bx, by, br = G['ball']; pb = P['ball']
        check(all(list(sz[k]) == [P[k]['w'], P[k]['h']] for k in sz) and inb and 30 <= G['push'] <= 80 and abs(bx - (pb['x'] + pb['w'] / 2)) < 12 and abs(by - (pb['y'] + pb['h'] / 2)) < 16 and P['arrow']['y'] + P['arrow']['h'] <= pb['y'] + 10
              and all(os.path.getsize(os.path.join(TCA, f)) > 8000 for f in ('tc_se_zn_up.m4a', 'tc_se_zn_down.m4a')),
              f'レバーの 絵 3まい（台 {sz["back"]}・玉 {sz["ball"]}・矢印 {sz["arrow"]}）は 置き場所の 表（tc_zn_geom.json：{G["w"]}×{G["h"]}・押しこむ 長さ {G["push"]}）と 合う・矢印は 玉の 上・音 2つ')
        if shutil.which('ffprobe'):
            dur = [float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', os.path.join(TCA, f)], capture_output=True, text=True).stdout.strip() or 0) for f in ('tc_se_zn_up.m4a', 'tc_se_zn_down.m4a')]
            check(2.2 <= dur[0] <= 3.0 and 1.5 <= dur[1] <= 2.2 and dur[0] > dur[1], f'音の 長さ：上乗せ {dur[0]:.2f}秒（ドゥルルルン！ギュウィーンンン！）・失敗 {dur[1]:.2f}秒（ピューン…）')
    if HAVE:
        with sync_playwright() as p:
            b = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'])
            ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo')
            ctx.add_init_script(FAKE)
            pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
            miss = []; pg.on('response', lambda r: miss.append(r.url.split('/')[-1]) if r.status == 404 and ('tc_zn' in r.url or 'tc_se_zn' in r.url) else None)
            open_tc(pg, STORE)
            # ---------- 抽選 ----------
            print('■ 抽選の 表と 決め方')
            tb = pg.evaluate("""() => { const T = TCApp._t, f = t => t.map(([p, z]) => [Math.round(1 / p), z.k]); return { n: f(T.PRIZES)[0], m: f(T.PRIZES_VISIT.maboroshi)[0], k: f(T.PRIZES_VISIT.kamisama)[0], zone: T.ZONE, odds: T.ODDS.zone, x: T.ODDS.highX,
              vs: Array.from({ length: 13 }, (_, n) => T.zoneV(n)), edge: [T.zoneV(-3), T.zoneV(99), T.zoneV('x'), T.zoneV(2.4)] }; }""")
            check(tb['n'] == [699, 'zn'] and tb['m'] == [699, 'zn'] and tb['k'] == [699, 'zn'] and tb['zone'] == {'d': D, 'start': START, 'add': ADD, 'rate': RATE, 'max': MAX} and tb['vs'] == [ZV(n) for n in range(13)] and tb['edge'] == [1000, 25000, 1000, 5000],
                  f'いつもの 表・幻の馬・神様馬の どの 表にも ポイント特化ゾーン 1/699・合計は 1,000P ＋ 2,000P × 回数（0〜12回：{tb["vs"][0]:,}P 〜 {tb["vs"][12]:,}P・おかしな 数は 0〜12に まるめる）')
            dr = pg.evaluate("""() => { const T = TCApp._t, st = TCApp.state, S = TCCare.S, R = Math.random, one = (r, kind, high) => { st.visit = kind ? { kind, until: Date.now() + 6e5 } : null; S.high = high ? 3 : 0; Math.random = () => r; let z; try { z = T.draw(); } finally { Math.random = R; } return z ? z.k : null; };
              const o = { in: one(0.0005, null), edge: one(0.00142, null), out: one(0.00145, null), mab: one(0.0005, 'maboroshi'), mabOut: one(0.00145, 'maboroshi'), kami: one(0.0005, 'kamisama'), kamiOut: one(0.00145, 'kamisama'),
                hi: one(0.0056, null, true), hiOut: one(0.0058, null, true), hiMab: one(0.0056, 'maboroshi', true) }; st.visit = null; S.high = 0; st.high = 0; return o; }""")
            check(dr == {'in': 'zn', 'edge': 'zn', 'out': 'tk', 'mab': 'zn', 'mabOut': 'rt', 'kami': 'zn', 'kamiOut': 'rt', 'hi': 'zn', 'hiOut': 'tk', 'hiMab': 'zn'},
                  f'くじの 数が 1/699（0.00143）より 小さいと 特化ゾーン（いつも・幻の馬・神様馬）・高確ゾーンの 間は ほかの 当たりと 同じ 4倍（0.00572 まで）{dr}')
            rl = pg.evaluate("""() => { const T = TCApp._t, c = new Array(14).fill(0); let sum = 0; for (let i = 0; i < 40000; i++) { const n = T.zoneRoll(); c[Math.min(13, n)]++; sum += T.zoneV(n); } return { c, avg: sum / 40000 }; }""")
            okr = all(abs(rl['c'][n] / 40000 - ZP(n)) < max(0.012 * ZP(n) ** 0.5 * 2, 0.0012) for n in range(13)) and rl['c'][13] == 0
            check(okr and abs(rl['avg'] - E) < 110 and 30 <= rl['c'][12] <= 160,
                  f'上乗せの 回数を 4万回 決めると：0回 {rl["c"][0] / 40000:.1%}（40%）・1回 {rl["c"][1] / 40000:.1%}（24%）・3回 {rl["c"][3] / 40000:.2%}（8.64%）・12回（MAX）{rl["c"][12]}回（{ZP(12):.2%}）・13回は ない・平均 {rl["avg"]:,.0f}P（約{E:,.0f}P）')
            w0 = pg.evaluate(WAL)
            lt = pg.evaluate("""([seq]) => { const T = TCApp._t, st = TCApp.state, S = TCCare.S, R = Math.random, q = seq.slice(); st.visit = null; S.high = 0; st.high = 0; st.pend = null;
              Math.random = () => (q.length ? q.shift() : 0.5); let z; try { z = T.lottery(); } finally { Math.random = R; }
              const sv = (JSON.parse(localStorage.getItem('tengel.tc')) || {}).pend || null;
              return { z: z && [z.k, z.n, z.v, typeof z.id, /^tc-/.test(z.id)], left: q.length, pend: st.pend && [st.pend.k, st.pend.n, st.pend.v, st.pend.id === z.id], saved: sv && [sv.k, sv.n, sv.v, sv.id === z.id] }; }""", [seq_for(2)])
            w1 = pg.evaluate(WAL)
            check(lt['z'] == ['zn', 2, 5000, 'string', True] and lt['left'] == 0 and lt['pend'] == ['zn', 2, 5000, True] and lt['saved'] == ['zn', 2, 5000, True] and w1 == w0,
                  f'抽選で 入った ときに 上乗せの 回数と 合計を 決めて すぐ 保存（成功・成功・失敗 → 2回・5,000P）・ポイントは まだ（{w0} → {w1}）')
            # ---------- 途中で 閉じても もらえる ----------
            print('■ 演出の 途中で アプリを 閉じても もらえる（2回は もらえない）')
            pg.reload(); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(600)
            w2 = pg.evaluate("() => TengelWallet.total() + TengelWallet.hold().total")
            pg.locator('#tcFab .fabi').click()
            pg.wait_for_function("() => window.TCApp && document.querySelector('#tcOv.on') && !document.querySelector('#tcOv .tcld')", timeout=120000); pg.wait_for_timeout(1500)
            w3 = pg.evaluate(WAL); ev = pg.evaluate(EVS); m = pg.evaluate("() => document.querySelector('#tcOv .tcmsg').textContent"); pd = pg.evaluate("() => [TCApp.state.pend, (JSON.parse(localStorage.getItem('tengel.tc')) || {}).pend || null]")
            check(w2 == w1 and w3 - w2 == 5000 and ev and ev[-1] == [5000, 'トレーニングセンターの ポイント特化ゾーン'] and '5,000P' in m and '受け取ったよ' in m and pd == [None, None],
                  f'アプリを 開き直して トレーニングセンターを 開く → 前の 特化ゾーンの 5,000P を 受け取る（{w2} → {w3}・台帳「{ev and ev[-1][1]}」・お知らせ「{m}」）')
            pg.evaluate("() => TCApp._t.govSet(0, true)")
            pg.locator('#tcOv [data-tc=back]').click(); pg.wait_for_timeout(700); pg.locator('#tcFab .fabi').click()
            pg.wait_for_function("() => document.querySelector('#tcOv.on') && !document.querySelector('#tcOv .tcld')", timeout=120000); pg.wait_for_timeout(1200)
            w4 = pg.evaluate(WAL)
            g2 = pg.evaluate("() => { const T = TCApp._t, w = TengelWallet.total() + TengelWallet.hold().total, id = 'tc-zz-test', a = T.give({ k: 'zn', n: 3, v: 7000, id }), b = T.give({ k: 'zn', n: 3, v: 7000, id }), c = T.give({ k: 'zn', n: 4, id: 'tc-zz-test2' }); return [a, b, c, w]; }"); pg.wait_for_timeout(500)
            w5 = pg.evaluate(WAL)
            check(w4 == w3 and g2[:3] == [7000, 7000, 9000] and w5 - w4 == 16000, f'もう一度 開いても 足さない（{w3} → {w4}）・同じ 当たりを 2回 わたしても 台帳は 1回 だけ（7,000P ＋ べつの 当たり 9,000P ＝ +{w5 - w4:,}P）')
            pg.evaluate("() => { const st = TCApp.state, S = TCCare.S; st.stock = 20; S.stock = S.stockShow = 20; st.stockAt = Date.now() + 7200000; TCApp._t.govSet(0, true); }")
            # ---------- 演出：お世話 → PUSH → 特化ゾーン ----------
            print('■ お世話 → PUSH → ポイント特化ゾーン（レバーを タップ）')
            pg.evaluate(SE_WRAP)
            feed(pg); w0 = pg.evaluate(WAL); s0 = pg.evaluate("() => TCCare.S.stock")
            pg.evaluate(SES); r = pg.evaluate(PRESS, [seq_for(2)]); pg.wait_for_timeout(350)
            cue = pg.evaluate("() => { const S = TCCare.S; return { tag: S.fx.filter(f => f.k === 'rtcue').map(f => f.txt), pend: TCApp.state.pend && [TCApp.state.pend.k, TCApp.state.pend.n, TCApp.state.pend.v], wal: TengelWallet.total() + TengelWallet.hold().total, fx: document.querySelector('#tcOv .tcfx').classList.contains('on') }; }")
            shot(pg, 'zn_cue')
            check(r == [1, 0] and cue['tag'] == ['特化ゾーン！'] and cue['pend'] == ['zn', 2, 5000] and cue['wal'] == w0 and not cue['fx'],
                  f'PUSH を 押す → トークン −1・キュインキュイーンと「特化ゾーン！」の 札（ポイントは まだ・当たりは 保存 ずみ {cue["pend"]}）')
            pg.wait_for_function(FX_ON, timeout=20000); t_on = time.time()
            pg.wait_for_timeout(500); tap_fx(pg); pg.wait_for_timeout(500)            # まだ 押せない（1.3秒 たって いない）：早すぎる タップは 数えない
            early = pg.evaluate(SES)
            pg.wait_for_timeout(700); shot(pg, 'zn_ready')
            tap_fx(pg); pg.wait_for_timeout(700); shot(pg, 'zn_up1'); s1 = pg.evaluate(SES); pg.wait_for_timeout(950)      # 1回め：上乗せ
            tap_fx(pg); pg.wait_for_timeout(1650); s2 = pg.evaluate(SES)                                                   # 2回め：上乗せ
            mid = pg.evaluate(WAL)
            tap_fx(pg); pg.wait_for_timeout(900); shot(pg, 'zn_fail'); s3 = pg.evaluate(SES)                               # 3回め：失敗
            pg.wait_for_timeout(1500); s4 = pg.evaluate(SES); shot(pg, 'zn_card')                                          # 合計の 札
            still = pg.evaluate(FX_ON); tap_fx(pg); pg.wait_for_timeout(300); still2 = pg.evaluate(FX_ON)                  # 札が 出て すぐ（1秒 たつ 前）は とじない
            pg.wait_for_timeout(900); tap_fx(pg)
            pg.wait_for_function("() => !document.querySelector('#tcOv .tcfx').classList.contains('on')", timeout=20000); t_off = time.time(); pg.wait_for_timeout(700)
            w1 = pg.evaluate(WAL); ev = pg.evaluate(EVS); s5 = pg.evaluate(SES); st1 = pg.evaluate("() => [TCApp.state.pend, TCCare.S.stock]")
            check('kyuin' in early and 'luck' in early and not any(x.startswith('rt_lever') or x.startswith('zn_') for x in early),
                  f'演出の はじまり：キュインキュイーン → 「運がついた」の 音（{early}）・押せる ように なる 前（1.3秒）の 早すぎる タップは 数えない')
            check(s1 == ['rt_lever×0.9', 'zn_up'] and s2 == ['rt_lever×0.9', 'zn_up'] and s3 == ['rt_lever×0.9', 'zn_down'] and len(s4) == 1 and s4[0].startswith('sfx_big') and mid == w0,
                  f'レバーを タップ する たびに：カコン → 上乗せ（ドゥルルルン！ギュウィーンンン！）×2 → 3回めは 失敗（ピューン…）→ 合計の 札の 音（{s1}・{s2}・{s3}・{s4}）・とちゅうは まだ もらえない')
            check(still and still2 and w1 - w0 == 5000 and ev[-1] == [5000, 'トレーニングセンターの ポイント特化ゾーン'] and st1 == [None, s0 - 1] and not any(x.startswith('zn_') for x in s5),
                  f'合計の 札は 出て すぐの タップでは とじない → もう一度 タップで とじる → 5,000P（{w0} → {w1}・台帳「{ev[-1][1]}」・演出 {t_off - t_on:.1f}秒）・当たりの 保存は 消える')
            check(not miss, f'レバーの 絵と 音は ぜんぶ 読めた（読めなかった もの {miss}）')
            # 0回（1回めで 失敗）→ 1,000P ／ 押さなくても 進む
            pg.wait_for_function("() => TCApp._t && TCCare.S.phase === 'idle' && !TCCare.S.push", timeout=60000)
            feed(pg); w0 = pg.evaluate(WAL)
            r, sec, _ = run_zone(pg, 0, taps=False, limit=60); pg.wait_for_timeout(700); w1 = pg.evaluate(WAL); sx = pg.evaluate(SES)
            auto_want = ZN['ready'] + ZN['auto'] + ZN['fail'] + ZN['hold'] + ZN['close'] + 0.52
            check(r == [1, 0] and w1 - w0 == 1000 and abs(sec - auto_want) < 3.0 and 'zn_down' in sx and 'zn_up' not in sx and sx.count('rt_lever×0.9') == 1,
                  f'何も 押さなくても 進む：20秒で レバーが 自動で 入る → 1回めで 失敗 → 1,000P → 札も 自動で とじる（{sec:.1f}秒：きまりは {auto_want:.1f}秒・{w0} → {w1}）')
            # MAX（12回 つづけて 上乗せ）→ 25,000P・13回めは 押さない・ドーン！！
            pg.wait_for_function("() => TCCare.S.phase === 'idle' && !TCCare.S.push", timeout=60000)
            feed(pg); w0 = pg.evaluate(WAL)
            r, sec, _ = run_zone(pg, 12, name='zn_max'); pg.wait_for_timeout(700); w1 = pg.evaluate(WAL); sx = pg.evaluate(SES); ev = pg.evaluate(EVS)
            check(r == [1, 0] and w1 - w0 == 25000 and sx.count('zn_up') == 12 and 'zn_down' not in sx and sx.count('rt_lever×0.9') == 12 and 'doon' in sx and not any(x.startswith('sfx_big') for x in sx) and ev[-1] == [25000, 'トレーニングセンターの ポイント特化ゾーン'],
                  f'12回 つづけて 上乗せ → MAX 25,000P（{w0} → {w1}・上乗せの 音 {sx.count("zn_up")}回・失敗の 音 なし・13回めは 押さない・札の 音は ドーン！！・{sec:.0f}秒）')
            check(not errs, f'エラー なし {errs[:3]}')
            # ---------- 早めの タップを おぼえる・時間の きまり（演出 だけを 動かす）----------
            print('■ タップの 受け方（早めの タップは おぼえて おく・1.5秒に 1回）')
            tz = pg.evaluate("""async () => { const cv = document.querySelector('#tcOv .tcfx'), t0 = performance.now(), at = [], fire = s => setTimeout(() => { at.push((performance.now() - t0) / 1000); cv.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, cancelable: true, clientX: 195, clientY: 500 })); }, s * 1000);
              [0.5, 1.12, 2.05, 2.62, 4.95, 5.25, 6.2].forEach(fire);
              const r = await TCFX.zone(cv, { n: 1, start: 1000, add: 2000, max: 12, rate: 0.6, bg: 'morning', se: () => { } });
              return { taps: r.taps, total: r.total, end: (performance.now() - t0) / 1000, at, on: cv.classList.contains('on'), info: TCFX.zoneInfo({ n: 1 }, r.taps), ZN: TCFX.ZN }; }""")
            tp = tz['taps']
            check(tz['ZN']['ready'] == ZN['ready'] and tz['ZN']['cyc'] == ZN['cyc'] and tz['ZN']['buf'] == ZN['buf'] and tz['ZN']['auto'] == ZN['auto'] and tz['ZN']['fail'] == ZN['fail'] and tz['ZN']['hold'] == ZN['hold'] and tz['ZN']['close'] == ZN['close'],
                  f'時間の きまり：はじめに 押せる まで {ZN["ready"]}秒・次に 押せる まで {ZN["cyc"]}秒・早めの タップを おぼえる {ZN["buf"]}秒・自動 {ZN["auto"]}秒')
            check(len(tp) == 2 and ZN['ready'] <= tp[0] <= ZN['ready'] + 0.25 and tp[0] + ZN['cyc'] <= tp[1] <= tp[0] + ZN['cyc'] + 0.25 and tz['total'] == 3000 and tz['info']['need'] == 2 and tz['info']['total'] == 3000 and not tz['on'],
                  f'0.5秒の タップは 早すぎて 数えない・1.12秒（押せる 0.18秒前）は おぼえて おいて 1.3秒に 入る（{tp[0]:.2f}秒）・2.05秒は 早すぎ・2.62秒は おぼえて 2回め（{tp[1]:.2f}秒＝1.5秒 あと）→ 合計 3,000P')
            e_card = tp[1] + ZN['fail']
            check(e_card + ZN['hold'] < tz['end'] - 0.5 < e_card + ZN['hold'] + 1.3 and tz['end'] < e_card + ZN['hold'] + ZN['close'],
                  f'合計の 札（{e_card:.2f}秒）が 出て 1秒 たつ 前の タップ（4.95秒・5.25秒）では とじない → 6.2秒の タップで とじる（おわり {tz["end"]:.2f}秒）')
            # ---------- 1コマずつ 描いて 測る ----------
            print('■ 絵（1/30秒ごとに 描いて 測る）')
            FR = """async ([o, taps, us, calm, noImg]) => { const cv = document.createElement('canvas'); cv.width = 390; cv.height = 614; const g = cv.getContext('2d', { willReadFrequently: true }), out = [];
              for (const u of us) { const img = await TCFX.zoneFrame(cv, o, taps, u, calm, noImg), d = g.getImageData(0, 0, 390, 614).data; let rx = 0, ry = 0, rn = 0;
                for (let y = 250; y < 480; y++) for (let x = 130; x < 260; x++) { const i = (y * 390 + x) * 4; if (d[i] > 64 && d[i] > d[i + 1] * 2.2 && d[i] > d[i + 2] * 1.9) { rx += x; ry += y; rn++; } }      // 赤い 玉（暗く なっても 赤の 割合で 見つける）
                const px = (x, y) => { const i = (Math.round(y) * 390 + Math.round(x)) * 4; return [d[i], d[i + 1], d[i + 2], d[i + 3]]; };
                const lamps = Array.from({ length: 12 }, (_, i) => { const q = px(195 + (i - 5.5) * 27 + 2.5, 205 + 3); return Math.max(q[0], q[1], q[2]); });
                out.push({ u, img, red: rn ? [rx / rn, ry / rn, rn] : null, lamps, corner: [px(6, 420), px(384, 600), px(8, 8)] }); }
              return out; }"""
            O3 = {'n': 3, 'start': START, 'add': ADD, 'max': MAX, 'rate': RATE}; T3 = [1.3, 2.8, 4.3, 5.8]      # 上乗せ 3回（4回めで 失敗）・きまり どおり 1.5秒ごとに 押す
            #   測る 時刻：押す 前・1回めを 押した すぐ あと（玉が 下）・次を 押す すぐ 前（光は 消えて いる）×3・4回め（失敗）を 押した すぐ あと・失敗の 1.6秒 あと・合計の 札
            fr = pg.evaluate(FR, [O3, T3, [1.2, 1.3 + 0.12, 2.8 - 0.04, 4.3 - 0.04, 5.8 - 0.04, 5.8 + 0.12, 5.8 + 1.6, 5.8 + 1.9 + 1.2], False, False])
            lit = lambda f: sum(1 for v in f['lamps'] if v > 150)
            dy = fr[1]['red'][1] - fr[0]['red'][1]; want_dy = G['push'] * 338 / G['w']
            check(all(f['img'] for f in fr) and fr[0]['red'][2] > 2500 and abs(dy - want_dy) < 3.5 and abs(fr[1]['red'][0] - fr[0]['red'][0]) < 1.5 and all(abs(fr[i]['red'][1] - fr[0]['red'][1]) < 1.5 for i in (2, 3, 4)),
                  f'レバーの 絵（まさちゃんの 3D）：タップ すると 赤い 玉 だけ 下へ {dy:.1f}px（きまりは {want_dy:.1f}px）・よこには 動かない・上乗せの あとは もとの 高さに もどる（ずれ {max(abs(fr[i]["red"][1] - fr[0]["red"][1]) for i in (2, 3, 4)):.1f}px）')
            check([lit(f) for f in fr[:7]] == [0, 0, 1, 2, 3, 3, 3] and fr[6]['red'] is not None and abs(fr[6]['red'][1] - fr[5]['red'][1]) < 2.5 and abs(fr[5]['red'][1] - fr[1]['red'][1]) < 1.5,
                  f'ランプ（上乗せ した 数）：{[lit(f) for f in fr[:7]]}（押す 前 0 → 1回めの あと 1 → 2 → 3・失敗しても 3の まま）・失敗の あとは 玉が 押しこまれた まま（暗く なる）')
            check(all(c[3] >= 200 for f in fr for c in f['corner']) and all(max(c[:3]) < 90 for c in fr[0]['corner']),
                  f'うしろは 暗い 幕（すみの 点の こさ {min(c[3] for f in fr for c in f["corner"])}/255 以上）＝ フィールドの ボタンや ゲージが すけて 字の じゃまを しない')
            # 明るさ（相対輝度）：画面 ぜんぶ・大きい ます（3×4＝画面の 8%）・中の ます（6×10）・小さい ます（30pt）。向きがえ＝前の 山・谷から 0.1 以上 動いて 向きが かわった 回数（2回で 点めつ 1回）
            LUMJS = """async ([o, taps, nfr, calm, noImg, snapK]) => {
              const cv = document.createElement('canvas'); cv.width = 390; cv.height = 614; const g = cv.getContext('2d', { willReadFrequently: true });
              const LUT = new Float32Array(256); for (let i = 0; i < 256; i++) { const c = i / 255; LUT[i] = c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); }
              const small = [], mid = [], big = [], glob = []; let img = true, snap = null;
              for (let k = 0; k <= nfr; k++) {
                img = await TCFX.zoneFrame(cv, o, taps, k / 30, calm, noImg) && img;
                const d = g.getImageData(0, 0, 390, 614).data, s = new Float32Array(273), sn = new Uint32Array(273), m = new Float32Array(60), mn = new Uint32Array(60), b = new Float32Array(12), bn = new Uint32Array(12); let tot = 0;
                for (let y = 0; y < 614; y++) for (let x = 0; x < 390; x++) { const i = (y * 390 + x) * 4, a = d[i + 3] / 255, L = a * (0.2126 * LUT[d[i]] + 0.7152 * LUT[d[i + 1]] + 0.0722 * LUT[d[i + 2]]);
                  const si = Math.min(20, (y / 30) | 0) * 13 + Math.min(12, (x / 30) | 0), mi = Math.min(9, (y / 61.4) | 0) * 6 + Math.min(5, (x / 65) | 0), bi = Math.min(3, (y / 153.5) | 0) * 3 + Math.min(2, (x / 130) | 0);
                  s[si] += L; sn[si]++; m[mi] += L; mn[mi]++; b[bi] += L; bn[bi]++; tot += L; }
                small.push([...s].map((v, i) => +(v / sn[i]).toFixed(4))); mid.push([...m].map((v, i) => +(v / mn[i]).toFixed(4))); big.push([...b].map((v, i) => +(v / bn[i]).toFixed(4))); glob.push(+(tot / 239460).toFixed(4));
                if (k === snapK) snap = cv.toDataURL('image/png');
              }
              return { small, mid, big, glob, img, snap }; }"""

            def lum_tr(x, th=0.1):
                lo = hi = x[0]; d = 0; out = []
                for k, v in enumerate(x):
                    if d == 0:
                        lo = min(lo, v); hi = max(hi, v)
                        if v - lo >= th: out.append(k); d = 1; hi = v
                        elif hi - v >= th: out.append(k); d = -1; lo = v
                    elif d == 1:
                        hi = max(hi, v)
                        if hi - v >= th: out.append(k); d = -1; lo = v
                    else:
                        lo = min(lo, v)
                        if v - lo >= th: out.append(k); d = 1; hi = v
                return out

            def per_sec(ks):               # どの 1秒（30コマ）を とっても 向きがえは 何回 まで
                return max([sum(1 for q in ks if k0 <= q < k0 + 30) for k0 in ks] or [0])

            def lum_stat(r):
                o = dict(g=per_sec(lum_tr(r['glob'], 0.05)), gmax=max(r['glob']), gmin=min(r['glob'][20:]), img=r['img'])
                for key in ('big', 'mid', 'small'):
                    S = r[key]; o[key] = [per_sec(lum_tr([f[i] for f in S])) for i in range(len(S[0]))]
                o['n5'] = sum(1 for v in o['small'] if v >= 5); o['n7'] = sum(1 for v in o['small'] if v >= 7)      # 小さい ます（30pt）：向きがえ 5回 以上・7回 以上（＝点めつ 1秒に 3回 より 多い）の 数
                o['hot'] = sorted({(i // 13) * 30 for i, v in enumerate(o['small']) if v >= 7})                        # その ますの 高さ（y）
                return o

            def calm_ok(o, n7=4):          # 画面 ぜんぶ・大きい ます・中の ますは 1秒に 点めつ 1〜2回 まで。小さい ますで 1秒に 3回 より 多いのは 合計の 数字が 回る 所（y 90〜180）だけ・画面の 1.5% まで
                return o['g'] <= 2 and max(o['big']) <= 2 and max(o['mid']) <= 4 and o['n7'] <= n7 and o['n5'] <= 14 and all(90 <= y < 180 for y in o['hot'])
            import base64 as _b64
            nfr = int((T3[-1] + ZN['fail'] + 3.0) * 30)
            LN = pg.evaluate(LUMJS, [O3, T3, nfr, False, False, int((1.3 + ZN['r0'] + 0.45) * 30)]); ln = lum_stat(LN)
            if SHOT: os.makedirs(SHOT, exist_ok=True); open(os.path.join(SHOT, 'zn_frame_up.png'), 'wb').write(_b64.b64decode(LN['snap'].split(',')[1]))
            check(ln['img'] and calm_ok(ln),
                  f'ちかちか しない（上乗せ 3回 → 失敗 → 合計の 札・{nfr / 30:.1f}秒）：1秒の 向きがえ（2回で 点めつ 1回）＝画面 ぜんぶ {ln["g"]}回・大きい ます（画面の 8%）{max(ln["big"])}回 まで・中の ます（1.7%）{max(ln["mid"])}回 まで・'
                  f'小さい ます（30pt）で 7回 以上（点めつ 1秒に 3回 より 多い）は {ln["n7"]}/273（画面の {ln["n7"] / 273:.1%}：合計の 数字が 回る 所 だけ y={ln["hot"]}）・5回 以上は {ln["n5"]}/273')
            T12 = [1.3 + 1.5 * i for i in range(12)]; O12 = dict(O3, n=12); nfr12 = int((T12[-1] + ZN['maxEnd'] + 3.0) * 30)
            LM = pg.evaluate(LUMJS, [O12, T12, nfr12, False, False, int((T12[-1] + ZN['maxEnd'] + 1.2) * 30)]); lm = lum_stat(LM)
            if SHOT: open(os.path.join(SHOT, 'zn_frame_max.png'), 'wb').write(_b64.b64decode(LM['snap'].split(',')[1]))
            check(lm['img'] and calm_ok(lm, 6),
                  f'ちかちか しない（いちばん 速く 12回 つづけて 上乗せ → MAX の 札・{nfr12 / 30:.1f}秒）：画面 ぜんぶ {lm["g"]}回・大きい ます {max(lm["big"])}回 まで・中の ます {max(lm["mid"])}回 まで・'
                  f'小さい ますで 7回 以上は {lm["n7"]}/273（{lm["n7"] / 273:.1%}：数字の 所 y={lm["hot"]}）・5回 以上は {lm["n5"]}/273')
            LC = pg.evaluate(LUMJS, [O3, T3, nfr, True, False, -1]); lc = lum_stat(LC)
            check(lc['img'] and lc['g'] <= 2 and max(lc['big']) <= 2 and max(lc['small']) <= 4 and lc['n5'] == 0 and sum(lc['small']) < sum(ln['small']) * 0.6,
                  f'「演出を控えめにする」：光の すじ・輪・きらめき・紙ふぶきは なし・合計の 数字は 回さない（小さい ますでも 向きがえ {max(lc["small"])}回 まで・合わせて {sum(lc["small"])} ＜ ふつうの {sum(ln["small"])}）')
            LF = pg.evaluate(LUMJS, [O3, T3, nfr, False, True, int(1.25 * 30)]); lf = lum_stat(LF)
            ff = pg.evaluate(FR, [O3, T3, [1.2, 1.3 + 0.12, 4.3 + 1.2], False, True])
            if SHOT: open(os.path.join(SHOT, 'zn_frame_noimg.png'), 'wb').write(_b64.b64decode(LF['snap'].split(',')[1]))
            check(lf['img'] is False and not any(f['img'] for f in ff) and ff[0]['red'] and ff[0]['red'][2] > 1500 and ff[1]['red'][1] - ff[0]['red'][1] > 10 and [lit(f) for f in ff] == [0, 0, 3] and calm_ok(lf),
                  f'絵が ない とき（手元に 素材が ない ビルド）：かんたんな 絵（金の 台・赤い 玉・リボン）で 同じ 流れ（玉は 下へ {ff[1]["red"][1] - ff[0]["red"][1]:.1f}px・ランプ {[lit(f) for f in ff]}・ちかちか しない）')
            check(not errs, f'エラー なし（絵の 測り）{errs[:3]}')
            b.close()
    else:
        print('※ 画面の テストは とばした（ios/tc_assets が ない）')
finally:
    srv.terminate()
print('NG' if fails else 'OK', len(fails), fails)
sys.exit(1 if fails else 0)
