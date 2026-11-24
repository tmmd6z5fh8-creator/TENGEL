# 第4.219版：壁紙の 動きは 見えて いる 間 だけ（まさちゃん 2026/11/25 00:00「なんか全体的にめちゃくちゃ重い！理由見つけて改善して！」）
#   python3 test_seen.py   （App Store版の 画面 TARGET=app を localhost で アプリ版として 開く）
#   重さの もと：判定タブの 上の絵・設定タブの 動く タイル（いま 使って いる 壁紙と 同じ 動き まるごと）・見本は、多い 壁紙で 200〜300 の 動きを 毎コマ 動かす。
#     iPhone（WebKit）は SVG の 中の 動き・steps() の コマ送り・visibility などを 毎コマ 計算して 描き直す。前は タブが 見えて いれば、
#     下へ スクロール して 画面の 外の ときも、トレーニングセンター・カードバトル・フィギュア・作戦会議・的中の 演出の 窓の 下でも、設定タブの 上や 下でも 動いて いた
#   たしかめる こと（kisekae.js の seen・look・watch）：
#   ・判定タブの 一番 上：動く（.pause なし・動きの 数は 前と 同じ）。少し だけ 見えて いる ときも 動く
#   ・下へ スクロール して 画面の 外：止まる（.pause・動いて いる 動き 0）→ もどすと 動く（コマの さかい目も 合わせ直す）
#   ・画面 ぜんぶを おおう 窓（作戦会議・的中の 演出・ログインボーナス・ためしの 窓）の 下：止まる → 閉じると 動く（タップで 閉じた ときは 0.4秒 以内）。半分 だけ おおう 窓：動く
#   ・うすく なって いる 途中の 窓（消える・出る とき）の 下は 動く・2回目の 起動の はじめの 画面の 下では 止まって、消えたら すぐ 動く（body の 子の 出入りを 見る）
#   ・止まって いる 間の 画面の 仕事は 動いて いる ときの 1割 より 少ない（Chromium の TaskDuration）
#   ・テストが 手で つけた .pause は さわらない・判定タブ以外では 止まる・控えめ（.calm）は 前と 同じ
#   ・設定タブ：動く タイルと 見本は 画面に ある とき だけ 動く（一番 上・下では 止まる）
#   ・止める ときは かざり（::before・::after）の 動きも 止める（海賊の 旗 32こ・見本の PUSH の 光：前は 止まって いなかった）
import json, os, re, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
BL = os.environ.get('KISEKAE_ASSETS') or os.path.join(W, 'ios', 'kisekae_blobs')
SRV = os.path.join(W, 'srv_seen'); PORT = 8827; APP = f'http://localhost:{PORT}/APP/'
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, HIST='hist_280.json', DROP='', TARGET='app'))
pth = os.path.join(SRV, 'APP', 'index.html'); page = open(pth, encoding='utf8').read()
assert "window.__NATIVE = location.protocol === 'tengel:';" in page
open(pth, 'w', encoding='utf8').write(page.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
if os.path.isdir(BL):
    for f in os.listdir(BL): shutil.copy(os.path.join(BL, f), os.path.join(SRV, 'APP', 'ks_' + f))
FAKE = open(os.path.join(W, 'test_cb.py'), encoding='utf8').read().split('FAKE = """')[1].split('"""')[0]
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c: fails.append(label)


RUN = """(sel) => { const e = document.querySelector(sel); return e ? e.getAnimations({ subtree: true }).filter(a => a.playState === 'running').length : -1; }"""
ALL = """(sel) => { const e = document.querySelector(sel); return e ? e.getAnimations({ subtree: true }).length : -1; }"""
PAUSED = "(sel) => { const e = document.querySelector(sel); return e ? e.classList.contains('pause') : null; }"
# 動きの ようす（running・paused・finished）と かざり（::before・::after）の 動き
ST = """(sel) => { const e = document.querySelector(sel); if (!e) return null; const o = { running: 0, paused: 0, finished: 0, pseudoRun: 0, pseudo: 0 };
  for (const a of e.getAnimations({ subtree: true })) { o[a.playState] = (o[a.playState] || 0) + 1; if (a.effect && a.effect.pseudoElement) { o.pseudo++; if (a.playState === 'running') o.pseudoRun++; } } return o; }"""


def wait_cls(pg, sel, want, ms=1600):
    """sel の .pause が want に なるまで 待つ（なった ときの ms・ならなければ None）"""
    t0 = time.time()
    while (time.time() - t0) * 1000 < ms:
        if pg.evaluate(PAUSED, sel) == want: return round((time.time() - t0) * 1000)
        pg.wait_for_timeout(50)
    return None


srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo')
        ctx.add_init_script(FAKE)
        ctx.route('**/__native/autobackup.json', lambda route: route.fulfill(status=404, body='not found'))
        pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        cdp = ctx.new_cdp_session(pg); cdp.send('Performance.enable')
        pg.goto(APP); pg.wait_for_timeout(1500)
        if pg.locator('#gateGo').count(): pg.click('#gateGo'); pg.wait_for_timeout(700)
        pg.wait_for_function("() => window.TengelKisekae && TengelKisekae.list().length > 0", timeout=15000)
        pg.evaluate("TengelFx.set({ calm: false })")
        pg.evaluate("(id) => TengelKisekae.apply(id, false)", 'paddock')
        pg.wait_for_function("(id) => TengelKisekae.current() === id && TengelKisekae.loaded()", arg='paddock', timeout=8000)
        pg.evaluate("window.scrollTo(0, 0)"); pg.wait_for_timeout(900)
        B = '#ksBnr'
        n_all, n_run = pg.evaluate(ALL, B), pg.evaluate(RUN, B)
        check(n_all > 200 and n_run == n_all and pg.evaluate(PAUSED, B) is False, f'判定タブの 一番 上：上の絵は 動く（パドック：動き {n_run}/{n_all}・.pause なし）')

        def task(ms=2000):
            m0 = {x['name']: x['value'] for x in cdp.send('Performance.getMetrics')['metrics']}
            pg.wait_for_timeout(ms)
            m1 = {x['name']: x['value'] for x in cdp.send('Performance.getMetrics')['metrics']}
            return round(m1['TaskDuration'] - m0['TaskDuration'], 3), int(m1['RecalcStyleCount'] - m0['RecalcStyleCount'])
        t_run = task()
        # ---- 下へ スクロール：画面の 外 → 止まる
        y_out = pg.evaluate(f"(() => {{ const r = document.querySelector('{B}').getBoundingClientRect(); return Math.ceil(r.bottom + scrollY + 40); }})()")
        pg.evaluate(f"window.scrollTo(0, {y_out})")
        ms_out = wait_cls(pg, B, True)
        bot = pg.evaluate(f"document.querySelector('{B}').getBoundingClientRect().bottom")
        check(ms_out is not None and bot < 0 and pg.evaluate(RUN, B) == 0, f'下へ スクロール して 上の絵が 画面の 外（下の はし {bot:.0f}px）：止まる（.pause・動いて いる 動き 0・{ms_out}ms）')
        t_out = task()
        check(t_out[0] < max(0.03, t_run[0] * 0.1), f'止まって いる 間の 画面の 仕事は 動いて いる ときの 1割 より 少ない（2秒で {t_run[0]}秒・スタイル {t_run[1]}回 → {t_out[0]}秒・{t_out[1]}回）')
        # ---- 少し だけ 見えて いる（上の 帯の 下に 24px）→ 動く
        hd = pg.evaluate("(() => { const h = document.querySelector('header.top'); if (!h) return 0; const s = getComputedStyle(h); return (s.position === 'fixed' || s.position === 'sticky') ? Math.max(0, h.getBoundingClientRect().bottom) : 0; })()")
        y_peek = pg.evaluate(f"(() => {{ const r = document.querySelector('{B}').getBoundingClientRect(); return Math.floor(r.bottom + scrollY - {hd} - 24); }})()")
        pg.evaluate(f"window.scrollTo(0, {y_peek})")
        ms_peek = wait_cls(pg, B, False)
        vis = pg.evaluate(f"(() => {{ const r = document.querySelector('{B}').getBoundingClientRect(); return Math.round(r.bottom - Math.max(r.top, {hd})); }})()")
        check(ms_peek is not None and 0 < vis <= 40 and pg.evaluate(RUN, B) == n_all, f'上の 帯の 下に 少し だけ（{vis}px）見えて いる：動く（{ms_peek}ms）')
        # ---- 一番 上に もどす → 動く・コマの さかい目を 合わせ直す
        pg.evaluate(f"window.scrollTo(0, {y_out})"); wait_cls(pg, B, True)
        pg.evaluate("window.scrollTo(0, 0)")
        ms_back = wait_cls(pg, B, False)
        pg.wait_for_timeout(200)
        ph = pg.evaluate("() => TengelKisekae.phase()")
        check(ms_back is not None and pg.evaluate(RUN, B) == n_all and bool(ph) and ph['n'] == n_all, f'もどすと すぐ 動く（{ms_back}ms・動き {pg.evaluate(RUN, B)}）・コマの さかい目も 合わせる（{ph}）')
        # ---- 画面 ぜんぶを おおう 窓 → 止まる・タップで 閉じる → すぐ 動く
        pg.evaluate("""() => { const d = document.createElement('div'); d.id = 'tsCover'; d.style.cssText = 'position:fixed;inset:0;z-index:99999;background:#203040';
          d.addEventListener('click', () => d.remove()); document.body.appendChild(d); }""")
        ms_cov = wait_cls(pg, B, True, 1800)
        check(ms_cov is not None and pg.evaluate(RUN, B) == 0, f'画面 ぜんぶを おおう 窓の 下：止まる（{ms_cov}ms・1秒ごとの 見直し）')
        pg.click('#tsCover', position={'x': 200, 'y': 400})
        ms_unc = wait_cls(pg, B, False, 1600)
        check(ms_unc is not None and ms_unc <= 400 and pg.evaluate(RUN, B) == n_all, f'タップで 窓を 閉じる → すぐ 動く（{ms_unc}ms）')
        # ---- 左 半分 だけ おおう 窓 → 動く
        pg.evaluate("""() => { const d = document.createElement('div'); d.id = 'tsHalf'; d.style.cssText = 'position:fixed;left:0;top:0;bottom:0;width:50%;z-index:99999;background:#203040'; document.body.appendChild(d); }""")
        pg.wait_for_timeout(1500)
        check(pg.evaluate(PAUSED, B) is False and pg.evaluate(RUN, B) == n_all, '左 半分 だけ おおう 窓：見えて いる 所が ある ので 動く')
        pg.evaluate("document.getElementById('tsHalf').remove()")
        # ---- うすく なって いる 途中の 窓（すき通し 50%：消える・出る とき）→ 動く
        pg.evaluate("""() => { const d = document.createElement('div'); d.id = 'tsThin'; d.style.cssText = 'position:fixed;inset:0;z-index:99999;background:#203040;opacity:.5'; document.body.appendChild(d); }""")
        pg.wait_for_timeout(1300)
        th = pg.evaluate(PAUSED, B)
        pg.evaluate("document.getElementById('tsThin').style.opacity = '1'"); ms_th = wait_cls(pg, B, True, 1800)
        pg.evaluate("document.getElementById('tsThin').remove()"); ms_th2 = wait_cls(pg, B, False, 1800)
        check(th is False and ms_th is not None and ms_th2 is not None and ms_th2 <= 400, f'うすく なって いる 途中の 窓（50%）の 下：動く・すき通らなく なる → 止まる（{ms_th}ms）・窓を 消す（タップ なし）→ すぐ 動く（{ms_th2}ms：body の 子の 出入りを 見る）')
        # ---- 作戦会議（本物の 窓）→ 止まる → 「閉じる」→ 動く
        if pg.locator('#planBtn').count():
            pg.click('#planBtn'); ms_pl = wait_cls(pg, B, True, 2500)
            check(ms_pl is not None and pg.evaluate(RUN, B) == 0, f'作戦会議を 開く → うしろの 上の絵は 止まる（{ms_pl}ms）')
            pg.evaluate("""() => { const c = [...document.querySelectorAll('button')].filter(e => { const r = e.getBoundingClientRect(); return r.width && /閉じる/.test(e.getAttribute('aria-label') || e.innerText || ''); }); c[c.length - 1].click(); }""")
            ms_pc = wait_cls(pg, B, False, 1800)
            check(ms_pc is not None and pg.evaluate(RUN, B) == n_all, f'作戦会議を 閉じる → 動く（{ms_pc}ms）')
        else:
            check(False, '作戦会議の ボタン（#planBtn）が ない')
        # ---- 的中の 演出（PUSH）→ 止まる → 閉じる（タップ なし）→ 1秒ごとの 見直しで 動く
        pg.evaluate("""() => TengelFx.show({ r: '9R', n: 12, rows: [{ t: '馬単', rs: 'hit', c: ['1→2'] }], ranks: [1, 2, 3], force: 'hit' })""")
        ms_fx = wait_cls(pg, B, True, 2500)
        check(ms_fx is not None and pg.evaluate(RUN, B) == 0 and pg.locator('#fxOv').count() == 1, f'的中の 演出（PUSH）の 窓の 下：止まる（{ms_fx}ms）')
        pg.evaluate("TengelFx.close()")
        ms_fc = wait_cls(pg, B, False, 1800)
        check(ms_fc is not None and pg.evaluate(RUN, B) == n_all, f'演出を 閉じる → 動く（{ms_fc}ms）')
        # ---- ログインボーナス（本物の 窓：うしろが 暗く なる・出る ときは うすい → こく なる）→ 止まる → OK → すぐ 動く
        #   自動の ブラウザでは 自分からは 出ない ので、アプリが 開いた ときと 同じ たしかめ（TengelLogin.check）を 呼ぶ（Mac の run 192 は この 窓が 出た まま だった）
        dlg = pg.evaluate("() => window.TengelLogin ? TengelLogin.check() : -2")
        pg.wait_for_function("() => !!document.querySelector('#lgOv')", timeout=5000)
        #   ためしの 壁紙（パドック）は 解放して いない ので、ボーナスで 財布が かわると いつもの 絵に もどる（tengel:wallet・前と 同じ）→ 窓の 下で もう一度 つける
        pg.evaluate("(id) => TengelKisekae.apply(id, false)", 'paddock')
        pg.wait_for_function("(id) => TengelKisekae.current() === id && TengelKisekae.loaded()", arg='paddock', timeout=8000)
        ms_lg = wait_cls(pg, B, True, 2500)
        check(dlg == 0 and ms_lg is not None and pg.evaluate(RUN, B) == 0, f'ログインボーナスの 窓（{dlg + 1}日目）の 下：止まる（{ms_lg}ms：出る ときの うすい 間は 動く）')
        pg.click('#lgOv [data-lg=ok]')
        ms_lgo = wait_cls(pg, B, False, 1600)
        check(ms_lgo is not None and ms_lgo <= 400 and pg.evaluate(RUN, B) == n_all and pg.locator('#lgOv').count() == 0, f'OK で 閉じる → すぐ 動く（{ms_lgo}ms）')
        # ---- テストが 手で つけた .pause は さわらない（変わった ときだけ さわる）
        pg.evaluate(f"document.querySelector('{B}').classList.add('pause')"); pg.wait_for_timeout(2600)
        keep = pg.evaluate(PAUSED, B)
        pg.evaluate(f"document.querySelector('{B}').classList.remove('pause')"); pg.wait_for_timeout(1300)
        check(keep is True and pg.evaluate(PAUSED, B) is False and pg.evaluate(RUN, B) == n_all, '手で つけた .pause は 2.6秒 たっても そのまま・はずすと 動く（1秒ごとの 見直しは 変わった ときだけ）')
        # ---- 控えめ（.calm）・ほかの タブ（前と 同じ）
        pg.evaluate("TengelFx.set({ calm: true })"); pg.wait_for_timeout(150)
        cm = pg.evaluate(f"document.querySelector('{B}').classList.contains('calm')")
        pg.evaluate("TengelFx.set({ calm: false })"); pg.wait_for_timeout(150)
        check(cm and not pg.evaluate(f"document.querySelector('{B}').classList.contains('calm')"), '控えめに する → .calm（前と 同じ）・もどす → なし')
        pg.click('.tabbar button[data-tab=rec]'); pg.wait_for_timeout(300)
        p_rec = pg.evaluate(PAUSED, B)
        pg.click('.tabbar button[data-tab=judge]'); pg.wait_for_timeout(300); pg.evaluate("window.scrollTo(0, 0)")
        ms_j = wait_cls(pg, B, False, 1600)
        check(p_rec is True and ms_j is not None, f'判定タブ以外では 止まる・判定タブに もどると 動く（前と 同じ・{ms_j}ms）')
        # ---- 海賊：かざり（::after の 旗 32こ）の 動きも 止まる（前は 中の 要素 だけ 止めて いた）
        pg.evaluate("(id) => TengelKisekae.apply(id, false)", 'pirate')
        pg.wait_for_function("(id) => TengelKisekae.current() === id && TengelKisekae.loaded()", arg='pirate', timeout=8000)
        pg.evaluate("window.scrollTo(0, 0)"); pg.wait_for_timeout(900)
        s1 = pg.evaluate(ST, B)
        pg.evaluate(f"window.scrollTo(0, {y_out})"); wait_cls(pg, B, True); pg.wait_for_timeout(100); s2 = pg.evaluate(ST, B)
        pg.click('.tabbar button[data-tab=rec]'); pg.wait_for_timeout(300); s3 = pg.evaluate(ST, B)
        pg.click('.tabbar button[data-tab=judge]'); pg.wait_for_timeout(300); pg.evaluate("window.scrollTo(0, 0)"); wait_cls(pg, B, False); pg.wait_for_timeout(100); s4 = pg.evaluate(ST, B)
        check(s1['pseudo'] >= 30 and s1['pseudoRun'] == s1['pseudo'] and s1['running'] > 80 and s2['running'] == 0 and s3['running'] == 0 and s4['running'] == s1['running'],
              f'海賊：かざり（::after）の 動き {s1["pseudo"]}こも、画面の 外・ほかの タブで 止まる（{s1} → 外 {s2} → 記録タブ {s3} → もどる {s4}）')
        pg.evaluate("(id) => TengelKisekae.apply(id, false)", 'paddock')
        pg.wait_for_function("(id) => TengelKisekae.current() === id && TengelKisekae.loaded()", arg='paddock', timeout=8000); pg.wait_for_timeout(600)
        # ---- 設定タブ：動く タイル（.kslive › .kslv）
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(1500)
        L = '#setKisekae .kst .kslv'
        pg.wait_for_function(f"() => document.querySelector('{L}') && document.querySelector('{L}').getAnimations({{ subtree: true }}).length > 100", timeout=8000)
        pg.evaluate("document.querySelector('#setKisekae .kst .kslive').scrollIntoView({ block: 'center' })")
        ms_l = wait_cls(pg, L, False, 1600); l_all = pg.evaluate(ALL, L)
        check(ms_l is not None and pg.evaluate(RUN, L) == l_all > 100, f'設定タブ：動く タイルが 画面に ある → 動く（{pg.evaluate(RUN, L)}/{l_all}）')
        pg.evaluate("window.scrollTo(0, 0)")
        lt = pg.evaluate("document.querySelector('#setKisekae .kst .kslive').getBoundingClientRect().top")
        ms_l0 = wait_cls(pg, L, True, 1600)
        check(lt > 844 and ms_l0 is not None and pg.evaluate(RUN, L) == 0, f'設定タブの 一番 上（タイルは {lt:.0f}px・画面の 外）：止まる（{ms_l0}ms）')
        pg.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
        lb = pg.evaluate("document.querySelector('#setKisekae .kst .kslive').getBoundingClientRect().bottom")
        pg.wait_for_timeout(1300)
        check(lb < 0 and pg.evaluate(PAUSED, L) is True and pg.evaluate(RUN, L) == 0, f'設定タブの 一番 下（タイルは {lb:.0f}px）：止まった まま')
        pg.evaluate("document.querySelector('#setKisekae .kst .kslive').scrollIntoView({ block: 'center' })")
        ms_l1 = wait_cls(pg, L, False, 1600)
        check(ms_l1 is not None and pg.evaluate(RUN, L) == l_all, f'タイルに もどる → 動く（{ms_l1}ms）')
        # ---- 見本（.kspv）：タイルを タップ → 見本 → 画面の 外で 止まる → もどると 動く
        pg.locator('#setKisekae .kst[data-ks="paddock"]').click(position={'x': 18, 'y': 18})
        pg.wait_for_function("() => document.querySelector('#setKisekae .kspv [data-pvk=board] .fxs')", timeout=8000); pg.wait_for_timeout(800)
        V = '#setKisekae .kspv'
        pg.evaluate(f"document.querySelector('{V}').scrollIntoView({{ block: 'center' }})")
        ms_v = wait_cls(pg, V, False, 1600); sv = pg.evaluate(ST, V)
        check(ms_v is not None and sv['running'] > 0 and sv['paused'] == 0, f'見本が 画面に ある → 動く（{sv}：一度 きりの 動きは 終わって いる）')
        pg.evaluate("window.scrollTo(0, 0)")
        ms_v0 = wait_cls(pg, V, True, 1600); sv0 = pg.evaluate(ST, V)
        check(ms_v0 is not None and sv0['running'] == 0 and sv0['pseudoRun'] == 0, f'見本が 画面の 外：止まる（PUSH の 光の ::before も・{sv0}・{ms_v0}ms）')
        pg.evaluate(f"document.querySelector('{V}').scrollIntoView({{ block: 'center' }})")
        ms_v1 = wait_cls(pg, V, False, 1600); sv1 = pg.evaluate(ST, V)
        check(ms_v1 is not None and sv1['running'] > 0 and sv1['paused'] == 0 and sv1['running'] + sv1['finished'] == sv['running'] + sv['finished'], f'見本に もどる → 動く（{sv1}・{ms_v1}ms：回数の 決まった 動きは 見て いる 間に 終わる ことが ある）')
        # ---- 判定タブに もどる：上の絵は 動く・設定タブの タイルは 止まる（前と 同じ）
        pg.click('.tabbar button[data-tab=judge]'); pg.wait_for_timeout(300); pg.evaluate("window.scrollTo(0, 0)")
        ms_j2 = wait_cls(pg, B, False, 1600)
        check(ms_j2 is not None and pg.evaluate(RUN, B) == n_all and pg.evaluate(PAUSED, L) in (True, None), f'判定タブに もどる → 上の絵は 動く（{ms_j2}ms）・設定タブの タイルは 止まる')
        # ---- 2回目の 起動：はじめの 画面（ボタン なしで 自分で 消える）の 下では 止まる → 消えたら すぐ 動く
        pg3 = ctx.new_page(); pg3.on('pageerror', lambda e: errs.append(str(e)[:200])); pg3.goto(APP)
        pg3.wait_for_function("() => window.TengelKisekae && TengelKisekae.list().length > 0", timeout=15000)
        pg3.evaluate("(id) => TengelKisekae.apply(id, false)", 'paddock')
        pg3.wait_for_function("(id) => TengelKisekae.current() === id && TengelKisekae.loaded()", arg='paddock', timeout=8000)
        g0 = pg3.evaluate("(() => { const g = document.querySelector('#gate'); return g && !g.hidden && getComputedStyle(g).display !== 'none' ? parseFloat(getComputedStyle(g).opacity) : null; })()")
        p0 = pg3.evaluate(PAUSED, B)
        pg3.wait_for_function("() => { const g = document.querySelector('#gate'); return !g || g.hidden || getComputedStyle(g).display === 'none'; }", timeout=10000)
        t0 = time.time()
        while (time.time() - t0) < 1.5 and pg3.evaluate(PAUSED, B): pg3.wait_for_timeout(30)
        ms_g = round((time.time() - t0) * 1000)
        check(g0 is not None and (g0 < 0.99 or p0 is True) and pg3.evaluate(PAUSED, B) is False and ms_g <= 400 and pg3.evaluate(RUN, B) == n_all,
              f'2回目の 起動：はじめの 画面（すき通し {g0}）の 下では 止まる（{p0}）→ 消えたら すぐ 動く（{ms_g}ms・動き {pg3.evaluate(RUN, B)}）')
        pg3.close()
        check(not errs, f'エラー なし {errs[:3]}')
        ctx.close(); b.close()
finally:
    srv.terminate()
    shutil.rmtree(SRV, ignore_errors=True)
print('結果：', 'NG ' + str(len(fails)) if fails else 'OK')
sys.exit(1 if fails else 0)
