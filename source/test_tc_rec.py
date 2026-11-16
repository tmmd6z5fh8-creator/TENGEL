# トレーニングセンターの「軽さ」の テスト（第4.177版・まさちゃん 2026/11/16 10:40「トレーニングセンターがカクカク重くなっている、原因を見つけて改善して！」）
#   ① お世話の 札（.tco）：描く 命令を 書きとめて、前の コマと 同じ なら 紙に さわらない（tc/tc_care.js の REC）
#        ・書きとめて から 流した 絵が、じかに 描いた 絵（前の 作り）と 1画素も ちがわない か（たしかめ REC.check：2まいの 紙を 毎コマ くらべる）
#        ・読んだ 値（globalAlpha など）・字の 幅が 本物の 紙と 同じ か
#        ・何も して いない 間は ほとんどの コマを 描かない か（「！」・PUSH・降臨の バナーの ゆっくり した ゆれは 時間を きざむ）
#        ・あとから 中身の かわる 紙（かじった リンゴ）を 使う コマは その場で 流す か
#   ② お世話チャレンジの 台が 画面を おおって いる 間：下の フィールド・馬（WebGL）と お世話の 札を 描かない（計算は つづける）・台が 消えたら すぐ 描く
#   ③ WebGL：値の 場所（getUniformLocation）を 毎コマ 聞き直さない
#   python3 test_tc_rec.py   （ios/tc_assets/ に 絵が ある とき だけ 画面の テスト。ない とき（CI）は 中身の 見くらべ だけ）
import json, os, re, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv_tc'); PORT = 8816; APP = f'http://localhost:{PORT}/APP/'
SHOT = os.environ.get('SHOT')
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, TARGET='app'))
from assets_dir import adir
TCA = adir('tc_assets'); HAVE = os.path.isfile(os.path.join(TCA, 'tc_dp.json')) and len(os.listdir(TCA)) > 100
pth = os.path.join(SRV, 'APP', 'index.html'); html = open(pth, encoding='utf8').read()
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
if HAVE:
    for f in os.listdir(TCA): shutil.copy(os.path.join(TCA, f), os.path.join(SRV, 'APP', f))
else: print('※ トレーニングセンターの 絵と 音（ios/tc_assets）が ない ので、中身の 見くらべ だけ')
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c: fails.append(label)


TD = open(os.path.join(W, 'test_tc_drop.py'), encoding='utf8').read()
FAKE = TD.split('FAKE = """')[1].split('"""')[0]
# WebGL の 命令を 数える（描く 命令・値の 場所を 聞く 命令）。描く 命令は 数える だけで 実行しない（window.__noGL）：
#   この テストの 機械は WebGL を CPU で まねる ので 1秒に 5コマ ほどしか 出ない（iPhone は 60コマ）→ 1コマの 間が あきすぎて「ゆっくり した ゆれ」が 毎コマ かわって しまう。
#   アプリは WebGL の 絵を 読み返さない ので、描く 命令を とばしても お世話の 札・台・計算の 動きは 同じ（フィールドと 馬の 絵は 出ない だけ）
COUNT = r"""(() => { const C = window.__gl = { draw: 0, uloc: 0, aloc: 0 }; window.__noGL = true;
  for (const G of [window.WebGLRenderingContext, window.WebGL2RenderingContext]) { if (!G) continue; const Q = G.prototype;
    for (const [k, n] of [['drawArrays', 'draw'], ['drawElements', 'draw'], ['getUniformLocation', 'uloc'], ['getAttribLocation', 'aloc']]) { const o = Q[k]; Q[k] = function () { C[n]++; if (n === 'draw' && window.__noGL) return; return o.apply(this, arguments); }; } } })();"""


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


def stage_xy(pg, x, y):
    r = pg.evaluate("() => { const b = document.querySelector('#tcOv .tcst').getBoundingClientRect(); return [b.left, b.top, b.width, b.height]; }")
    return r[0] + x / 1052 * r[2], r[1] + y / 1657 * r[3]


def stage_click(pg, x, y):
    pg.mouse.click(*stage_xy(pg, x, y))


SETTOK = "n => { const S = TCCare.S, s = TCApp.state; S.stock = n; S.stockShow = n; s.stock = n; s.stockAt = Date.now(); S.high = 0; s.high = 0; }"
STAT = "() => { const R = TCCare.REC, s = R.stat; return { ok: R.ok, off: R.off, frames: s.frames, drawn: s.drawn, same: s.same, hidden: s.hidden, forced: s.forced, bad: s.bad, notes: s.notes.slice(), checks: R.checks, hid: TCApp._t.hidN, gl: Object.assign({}, window.__gl) }; }"
FRAMES = "async n => { for (let i = 0; i < n; i++) await new Promise(r => requestAnimationFrame(r)); }"


def span(pg, ms):
    """ms の 間の 数の ふえ方"""
    a = pg.evaluate(STAT); pg.wait_for_timeout(ms); b = pg.evaluate(STAT)
    d = {k: b[k] - a[k] for k in ('frames', 'drawn', 'same', 'hidden', 'forced', 'bad', 'checks', 'hid')}
    d['gl'] = {k: b['gl'][k] - a['gl'][k] for k in b['gl']}; d['notes'] = b['notes']
    return d


try:
    print('■ 中身')
    care = open(os.path.join(W, 'tc', 'tc_care.js'), encoding='utf8').read(); app = open(os.path.join(W, 'tc', 'tc_app.js'), encoding='utf8').read()
    drop = open(os.path.join(W, 'tc', 'tc_drop.js'), encoding='utf8').read(); field = open(os.path.join(W, 'tc', 'tc_field.js'), encoding='utf8').read(); horse = open(os.path.join(W, 'tc', 'tc_horse.js'), encoding='utf8').read()
    bundle = open(os.path.join(SRV, 'APP', 'tc_bundle.js'), encoding='utf8').read()
    check('const REC = (() => {' in care and 'function post(t, hide) {' in care and 'rec = REC.begin(G0, hide)' in care and 'if (!rec) { g = G0; REC.resync(); paint(t); return; }' in care and 'try { paint(t); REC.end(); } catch (e) { bad = true; }' in care and 'function paint(t) {' in care
          and 'REC.ok = false' in care and 'const KEEP = 60;' in care and 'if (!hide && mutable(src)) flush();' in care and 'c._fix = true;' in care,
          'お世話の 札：描く 命令を 書きとめる 役（REC）・同じ コマは 流さない・使えない ときは じかに 描く 作りに もどる・1秒に 1回は 描き直す')
    check("Math.sin(tq(t, 7.5) * 2.2)" in care and "const uq = tq(t, 30) - Pn.t0;" in care and "const uq = tq(t, 15) - B.showT, bob = 4 * Math.sin(TAU * uq / 3.4)" in care and 'const tq = (t, hz) => Math.floor(t * hz) / hz;' in care,
          'ゆっくり した ゆれ（おそうじの「！」7.5回／秒・PUSH 30回／秒・降臨の バナー 15回／秒）は 同じ 時計を きざむ')
    check('let hid = !!(window.TCDrop && TCDrop.covers && TCDrop.covers());' in app and 'if (!hid) field.render(t, ZV);' in app and 'dry: hid });' in app and 'TCCare.post(t, hid);' in app and 'mustDraw = 3;' in app
          and 'if (mustDraw > 0) { mustDraw--; hid = false; }' in app and 'if (view.dry) return;' in horse,
          'アプリ：台が おおって いる 間は フィールド・馬・お世話の 札を 描かない（紙の 大きさが かわった・裏から もどった あとの 3コマは 描く）')
    check("const covers = () => !!S && !S.hold && S.op === 1 && S.t >= 0.34;" in drop and "g.globalCompositeOperation = 'copy'; g.drawImage(stillCv, 0, 0); g.globalCompositeOperation = 'source-over';" in drop
          and 'if (op === 0) {' in drop and 'veilFill(s2, 1); s2.drawImage(cache, 0, 0);' in drop and 'if (veil >= 1 && ba >= 1 && rise === 0) {' in drop and "'tcdb'" not in drop,
          'お世話チャレンジの 台：動かない 所（幕 ＋ 台の 絵）は 重ねた 絵を 1回 だけ 作って 毎コマ 写す（消す・幕・台の 3回 ぬりを やめた）・すっかり 消えて いる 間は 描かない・おおって いる か を 知らせる（covers）')
    check('UL[n] = gl.getUniformLocation(PR, n)' in field and 'new Float32Array(all.slice(0, 18 * 16))' not in horse and 'h.ub || (h.ub = {' in horse,
          'WebGL：値の 場所は 1回 だけ 聞く・骨の 行列の 配列は 使い回す（毎コマ 新しく 作らない）')
    check('const REC = (() => {' in bundle and 'TCDrop.covers()' in bundle and 'g.drawImage(stillCv, 0, 0)' in bundle, 'アプリの 束（tc_bundle.js）に 入って いる')

    if HAVE:
        with sync_playwright() as p:
            b = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'])
            ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo'); ctx.add_init_script(COUNT); ctx.add_init_script(FAKE)
            pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.goto(APP); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(600)
            pg.evaluate("() => document.querySelectorAll('.tabbar button')[2].click()"); pg.wait_for_timeout(300)
            pg.locator('#tcFab').click()
            pg.wait_for_function("() => window.TCApp && TCApp.state && window.TCCare && TCCare.on && !document.querySelector('#tcOv .tcld')", timeout=120000); pg.wait_for_timeout(1500)
            pg.wait_for_function("() => window.TCDrop && TCDrop.ready()", timeout=60000)

            def shot(name):
                if SHOT: os.makedirs(SHOT, exist_ok=True); pg.screenshot(path=os.path.join(SHOT, name + '.png'))

            print('■ お世話の 札：何も して いない 間は 描かない')
            s0 = pg.evaluate(STAT)
            check(s0['ok'] and not s0['off'] and s0['frames'] >= 3 and s0['drawn'] >= 1, f'書きとめ役が 動いて いる（{s0["frames"]}コマ 中 {s0["drawn"]}コマ 描いた）')
            pg.evaluate("() => TCCare.REC.check(true)"); pg.evaluate(FRAMES, 4)
            d = span(pg, 4000)
            check(d['frames'] >= 60 and d['drawn'] <= d['frames'] * 0.25 + 2 and d['same'] >= d['frames'] * 0.7 and d['forced'] == 0 and d['hidden'] == 0,
                  f'馬が 歩いて いる だけの 間：{d["frames"]}コマ 中 描いたのは {d["drawn"]}コマ（同じ 絵の コマ {d["same"]}こは 紙に さわらない）')
            check(d['bad'] == 0 and d['checks'] >= d['frames'] - 2, f'描いた コマも 描かなかった コマも、じかに 描いた 絵と 1画素も ちがわない（くらべた {d["checks"]}コマ・ちがい {d["bad"]}）{d["notes"][:2]}')
            check(d['gl']['uloc'] == 0 and d['gl']['aloc'] == 0 and d['gl']['draw'] >= d['frames'] * 10, f'WebGL：値の 場所を 聞き直さない（{d["frames"]}コマで 聞いた 回数 {d["gl"]["uloc"]}・描く 命令 {d["gl"]["draw"]}）')
            px = pg.evaluate("() => { const c = document.querySelector('#tcOv .tco'), g = c.getContext('2d'), d = g.getImageData(0, 0, c.width, c.height).data; let n = 0; for (let i = 3; i < d.length; i += 4) if (d[i] > 200) n++; return n / (d.length / 4); }")
            check(0.03 < px < 0.6, f'札の 紙に 絵が 入って いる（色の ある 所 {px:.1%}）')
            shot('rec_idle')

            print('■ 撫でる（手・ハート）・呼ぶ')
            a0 = pg.evaluate(STAT)
            pg.evaluate("() => { const S = TCCare.S; S.coolUntil = -1e9; TCCare.press(S.lastT, 'pet'); }")
            pg.wait_for_function("() => TCCare.S.phase === 'pet'", timeout=30000); pg.wait_for_timeout(500)
            x0, y0 = stage_xy(pg, 430, 800); pg.mouse.move(x0, y0); pg.mouse.down()
            for i in range(24):
                x, y = stage_xy(pg, 430 + 200 * (i % 2), 800 + 20 * ((i // 2) % 2)); pg.mouse.move(x, y, steps=5)
            pg.mouse.up(); pg.wait_for_timeout(1500)
            hd = pg.evaluate("() => !!TCCare.S.hand")
            pg.wait_for_function("() => TCCare.S.phase === 'idle'", timeout=40000); pg.wait_for_timeout(800)
            a1 = pg.evaluate(STAT)
            check(a1['bad'] == 0 and a1['drawn'] - a0['drawn'] > 30 and a1['checks'] - a0['checks'] > 60, f'撫でる（ズーム・手・ハート・札）：動いて いる 間は 描く（{a1["drawn"] - a0["drawn"]}コマ）・じかに 描いた 絵と 同じ（ちがい {a1["bad"]}）{a1["notes"][:2]}')
            pg.evaluate("() => { const S = TCCare.S; S.callCoolUntil = -1e9; TCCare.press(S.lastT, 'call'); }"); pg.wait_for_timeout(1500)
            pg.wait_for_function("() => TCCare.S.phase === 'idle'", timeout=40000); pg.wait_for_timeout(500)
            a2 = pg.evaluate(STAT)
            check(a2['bad'] == 0 and a2['drawn'] > a1['drawn'], f'呼ぶ：じかに 描いた 絵と 同じ（ちがい {a2["bad"]}）{a2["notes"][:2]}')

            print('■ ごはん（かじった リンゴ＝あとから 中身の かわる 紙）')
            pg.evaluate(SETTOK, 8)
            pg.evaluate("() => { const S = TCCare.S; TCCare.press(S.lastT, 'feed'); }")
            pg.wait_for_function("() => !!TCCare.S.ask || !!TCCare.S.chooser", timeout=20000); pg.wait_for_timeout(500)
            if pg.evaluate("() => !!TCCare.S.ask"): pg.evaluate("() => TCCare.press(TCCare.S.lastT, 'ask:n')")      # 「抽選を しない」
            pg.wait_for_function("() => !!TCCare.S.chooser", timeout=20000); pg.wait_for_timeout(600)
            f0 = pg.evaluate(STAT)
            pg.evaluate("() => TCCare.press(TCCare.S.lastT, 'pick:apple')")
            pg.wait_for_function("() => TCCare.S.phase === 'idle' && !TCCare.S.chooser", timeout=90000); pg.wait_for_timeout(800)
            f1 = pg.evaluate(STAT)
            check(f1['forced'] - f0['forced'] > 10 and f1['bad'] == 0, f'リンゴを 食べる：かじった リンゴの 紙を 使う コマは その場で 流す（{f1["forced"] - f0["forced"]}コマ）・じかに 描いた 絵と 同じ（ちがい {f1["bad"]}）{f1["notes"][:2]}')

            print('■ PUSH・降臨の バナー（ゆっくり した ゆれ）')
            pg.evaluate(SETTOK, 12); pg.evaluate("() => { const S = TCCare.S; if (!(S.push && S.push.hideT == null)) TCCare.pushShow(S.lastT + 0.05); }"); pg.wait_for_timeout(1500)
            d = span(pg, 3000)
            check(d['bad'] == 0 and d['drawn'] <= d['frames'] * 0.6 + 2 and d['drawn'] >= 5, f'PUSH が 出て いる 間：ゆれは 1秒に 30回（{d["frames"]}コマ 中 描いたのは {d["drawn"]}コマ）・じかに 描いた 絵と 同じ（ちがい {d["bad"]}）{d["notes"][:2]}')
            shot('rec_push')
            pg.evaluate("() => TCCare.pushDone(TCCare.S.lastT)"); pg.wait_for_timeout(700)
            pg.evaluate("() => TCApp._t.startVisit('kamisama')"); pg.wait_for_function("() => TCCare.vinfoBox() && TCCare.S.vinfo", timeout=60000); pg.wait_for_timeout(3500)
            d = span(pg, 3000)
            check(d['bad'] == 0 and d['drawn'] <= d['frames'] * 0.4 + 2 and d['drawn'] >= 5, f'神様馬が 来て いる 間（降臨の バナー）：ゆれは 1秒に 15回（{d["frames"]}コマ 中 描いたのは {d["drawn"]}コマ）・じかに 描いた 絵と 同じ（ちがい {d["bad"]}）{d["notes"][:2]}')
            shot('rec_visit')

            print('■ お世話チャレンジの 台が おおって いる 間：下は 描かない')
            pg.evaluate(SETTOK, 12); pg.evaluate("() => { const S = TCCare.S; if (!(S.push && S.push.hideT == null)) TCCare.pushShow(S.lastT + 0.05); }"); pg.wait_for_timeout(900)
            G = pg.evaluate("() => TCCare.PUSHG"); stage_click(pg, *G['dp']); pg.wait_for_function("() => TCDrop.isOpen()", timeout=10000)
            pg.wait_for_function("() => TCDrop.covers()", timeout=10000); pg.evaluate(FRAMES, 6)
            tco0 = pg.evaluate("() => { const c = document.querySelector('#tcOv .tco'); return c.toDataURL().length; }")
            d = span(pg, 2500)
            check(d['frames'] >= 20 and d['hidden'] == d['frames'] and d['drawn'] == 0 and d['hid'] >= d['frames'] - 1 and d['gl']['draw'] == 0 and d['bad'] == 0,
                  f'台が 出て いる 間（{d["frames"]}コマ）：お世話の 札は 1コマも 描かない（書きとめる だけ {d["hidden"]}コマ）・WebGL の 描く 命令は 0（フィールド・馬）')
            live = pg.evaluate("async () => { const [h, b] = TCCare._hb, x0 = b.x, y0 = b.y, t0 = TCCare.S.lastT; await new Promise(r => setTimeout(r, 1200)); return { dt: TCCare.S.lastT - t0, last: !!h.last, info: !!TCDrop.info() }; }")
            check(live['dt'] > 0.5 and live['last'] and live['info'], f'その 間も 計算は つづく（時計が 進む：{live["dt"]:.1f}秒・馬の 場所の 計算も）')
            check(pg.evaluate("() => document.querySelector('#tcOv .tco').toDataURL().length") == tco0, '札の 紙は 前の 絵の まま（さわって いない）')
            shot('rec_drop')
            # 台を 閉じる → すぐ 描く
            geo = pg.evaluate("() => TCDrop.geo()"); pg.wait_for_function("() => TCDrop.info().t > 0.6"); g0 = pg.evaluate(STAT)
            stage_click(pg, *geo['quit']); pg.wait_for_function("() => !TCDrop.isOpen()", timeout=10000); pg.evaluate(FRAMES, 5); g1 = pg.evaluate(STAT)
            check(g1['drawn'] > g0['drawn'] and g1['gl']['draw'] > g0['gl']['draw'] and g1['bad'] == 0 and g1['hidden'] - g0['hidden'] <= 3, f'台を 閉じると すぐ 描く（札 {g1["drawn"] - g0["drawn"]}コマ・WebGL の 描く 命令 {g1["gl"]["draw"] - g0["gl"]["draw"]}）・じかに 描いた 絵と 同じ（ちがい {g1["bad"]}）{g1["notes"][:2]}')
            # 紙の 大きさが かわった（なめらかさを 守る しくみが 絵の 細かさを 下げた）：台の 下でも 描き直す
            pg.evaluate(SETTOK, 12); pg.evaluate("() => { const S = TCCare.S; if (!(S.push && S.push.hideT == null)) TCCare.pushShow(S.lastT + 0.05); }"); pg.wait_for_timeout(900)
            stage_click(pg, *G['dp']); pg.wait_for_function("() => TCDrop.isOpen() && TCDrop.covers()", timeout=10000); pg.evaluate(FRAMES, 6)
            w0 = pg.evaluate("() => document.querySelector('#tcOv .tco').width"); r0 = pg.evaluate(STAT)
            pg.evaluate("() => { const G = TCApp._t.gov; TCApp._t.govSet ? TCApp._t.govSet(1, false) : null; }")
            has_gov = pg.evaluate("() => typeof TCApp._t.govSet === 'function'")
            if has_gov:
                pg.evaluate(FRAMES, 8); r1 = pg.evaluate(STAT); w1 = pg.evaluate("() => [...document.querySelectorAll('#tcOv canvas')].map(c => c.width)")
                px2 = pg.evaluate("() => { const c = document.querySelector('#tcOv .tco'), g = c.getContext('2d'), d = g.getImageData(0, 0, c.width, c.height).data; let n = 0; for (let i = 3; i < d.length; i += 4) if (d[i] > 200) n++; return n / (d.length / 4); }")
                check(w1[0] < w0 and len(set(w1)) == 1 and r1['drawn'] - r0['drawn'] >= 1 and r1['gl']['draw'] > r0['gl']['draw'] and px2 > 0.03 and r1['bad'] == 0,
                      f'絵の 細かさが かわった（紙の 幅 {w0} → {w1[0]}：台の 紙も 同じ 幅）：台の 下でも 描き直す（札 {r1["drawn"] - r0["drawn"]}コマ・絵が 入って いる {px2:.1%}）')
                pg.evaluate("() => TCApp._t.govSet(0, true)"); pg.evaluate(FRAMES, 6)
            pg.wait_for_function("() => TCDrop.info().t > 0.6"); stage_click(pg, *geo['quit']); pg.wait_for_function("() => !TCDrop.isOpen()", timeout=10000); pg.wait_for_timeout(500)

            print('■ じかに 描く 作り（前の 作り）に もどしても 動く')
            tot = pg.evaluate(STAT)                                # たしかめを 切る 前の 数（くらべた コマ・ちがい）
            pg.evaluate("() => TCCare.REC.check(false)")
            pg.evaluate("() => { TCCare.REC.off = true; }"); pg.evaluate(FRAMES, 3); n0 = pg.evaluate(STAT); pg.evaluate(FRAMES, 30); n1 = pg.evaluate(STAT)
            px3 = pg.evaluate("() => { const c = document.querySelector('#tcOv .tco'), g = c.getContext('2d'), d = g.getImageData(0, 0, c.width, c.height).data; let n = 0; for (let i = 3; i < d.length; i += 4) if (d[i] > 200) n++; return n / (d.length / 4); }")
            check(n1['frames'] == n0['frames'] and px3 > 0.03, f'書きとめ役を 切る（REC.off）→ 前の 作りで 描く（絵が 入って いる {px3:.1%}）')
            pg.evaluate("() => { TCCare.REC.off = false; }"); pg.evaluate(FRAMES, 10); n2 = pg.evaluate(STAT)
            check(n2['frames'] > n1['frames'] and n2['ok'], 'もどす → また 書きとめて 描く')
            # もどした あと：紙の ようすを 読み直して いる（じかに 描いた 間に かわった かも しれない）→ じかに 描いた 絵と 同じ
            pg.evaluate("() => TCCare.REC.check(true)"); pg.evaluate(FRAMES, 24); n3 = pg.evaluate(STAT)
            check(n3['bad'] == 0 and n3['checks'] >= 20 and 'out.resync = () => { base = null; };' in care, f'もどした あとも じかに 描いた 絵と 同じ（くらべた {n3["checks"]}コマ・ちがい {n3["bad"]}）{n3["notes"][:2]}')
            pg.evaluate("() => TCCare.REC.check(false)")
            # 書きとめ役が とちゅうで つまずいた（この 端末の ブラウザと 合わない など）：その コマから じかに 描く・画面は 止まらない
            PXH = "() => { const c = document.querySelector('#tcOv .tco'), g = c.getContext('2d'), d = g.getImageData(0, 0, c.width, c.height).data; let n = 0, h = 0; for (let i = 3; i < d.length; i += 4) if (d[i] > 200) { n++; h = (h * 31 + d[i - 3] + d[i - 2] * 3 + d[i - 1] * 7 + i) | 0; } return [n / (d.length / 4), h]; }"
            pg.evaluate(FRAMES, 70); h0 = pg.evaluate(PXH)                                   # 何も して いない 間の 札の 絵（1秒に 1回の 描き直しも すんだ あと）
            pg.evaluate("() => { const R = TCCare.REC; window.__end = R.end; window.__endN = 0; R.end = () => { window.__endN++; throw new Error('test'); }; }")
            t0 = pg.evaluate("() => TCCare.S.lastT"); pg.evaluate(FRAMES, 12); f1 = pg.evaluate("() => ({ ok: TCCare.REC.ok, n: window.__endN, t: TCCare.S.lastT })"); h1 = pg.evaluate(PXH)
            check(not f1['ok'] and f1['n'] == 1 and f1['t'] > t0 and abs(h1[0] - h0[0]) < 0.02 and h1[0] > 0.03 and errs == [],
                  f'書きとめ役が とちゅうで つまずいた（1回）→ もう 使わない・その コマから じかに 描く・画面は 止まらない・エラーも 出ない（絵が 入って いる {h0[0]:.2%} → {h1[0]:.2%}・つまずいた 回数 {f1["n"]}・時計 {t0:.2f} → {f1["t"]:.2f}）')
            pg.evaluate("() => { const R = TCCare.REC; R.end = window.__end; R.ok = true; }"); pg.evaluate("() => TCCare.REC.check(true)"); pg.evaluate(FRAMES, 24); n4 = pg.evaluate(STAT)
            check(n4['ok'] and n4['bad'] == 0 and n4['checks'] >= 20, f'（テスト用に もどす）また 書きとめて 描く：じかに 描いた 絵と 同じ（くらべた {n4["checks"]}コマ・ちがい {n4["bad"]}）{n4["notes"][:2]}')
            pg.evaluate("() => TCCare.REC.check(false)")
            fin = pg.evaluate(STAT)
            check(fin['bad'] == 0 and fin['notes'] == [] and fin['ok'] and tot['bad'] == 0 and tot['checks'] > 500, f'ぜんぶ 通して：くらべた {tot["checks"]}コマ・ちがい 0・読んだ 値と 字の 幅も 本物と 同じ')
            check(errs == [], f'エラーなし（{errs[:3]}）')
            ctx.close(); b.close()
finally:
    srv.terminate()
print('\n' + ('✅ ぜんぶ OK' if not fails else f'❌ {len(fails)}件おかしい'))
for f in fails: print('  - ' + f)
sys.exit(1 if fails else 0)
