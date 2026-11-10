# 結果ボードカスタムの 絵の ボード（第4.145版）：止まった 版を 持たない 絵（部品を 重ねて 同じ 絵を 出す）の 出し方
#   python3 test_bcp_parts.py   （ios/bcp_assets/ が ある とき だけ。ない とき（CI）は「絵が ない」と 出して おわる）
#   置く 絵は アプリに 入れる もの だけ（kisekae/bcp/bcp_app.py の files()：キャラが 動く 絵の 止まった 版 83まいは 置かない）
#   ・ふつう：部品が そろって 絵が 出る（控えめ＝かさねた まま 動かさない／通常＝動く）。読む 絵は アプリに 入れる もの だけ・絵は ぜんぶ decoding=sync（同じ コマで 出す）
#   ・部品が おそい：そろう まで 絵を 出さない（キャラの いない 背景 だけが 見える コマが ない）・そろったら いっしょに 出る・ほかの 絵を かくす のは 絵が 出て から
#   ・部品が 1まい 読めない → いつもの ボード
#   ・部品が いつまでも こない → 8秒で いつもの ボード（あとから 届いても そのまま）
#   ・読んで いる 間に とじる → エラーなし・つぎは ふつうに 出る
#   ・つぎつぎ 出して とじる（40回・段と 控えめを まぜる）→ エラーなし・のこり物なし
#   ・控えめ と 通常（動きを はじめの 形で 止める）で 同じ 絵（3倍の 大きさで 色の 差 4 まで：重ね方の 丸めの ちがい だけ）
import os, random, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
sys.path.insert(0, os.path.join(W, 'kisekae', 'bcp')); import bcp_app as _bcp
BCP_DIR = os.path.join(W, 'ios', 'bcp_assets')
if not all(os.path.exists(os.path.join(BCP_DIR, f)) for f in _bcp.files()):
    print('※ 結果ボードカスタムの 絵（ios/bcp_assets）が ない ので、この テストは しない'); print('結果： OK'); sys.exit(0)
SRV = os.path.join(W, 'srv_bcpp'); PORT = 8796
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, HIST='hist_280.json', DROP='', TARGET='app'))
pth = os.path.join(SRV, 'APP', 'index.html'); html = open(pth, encoding='utf8').read()
assert "window.__NATIVE = location.protocol === 'tengel:';" in html
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
for f in _bcp.files(): shutil.copy(os.path.join(BCP_DIR, f), os.path.join(SRV, 'APP', f))
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
SPEC = {'r': 9, 'n': 14, 'ranks': {str(i): i for i in range(1, 15)},
        'rows': [{'t': '3連単', 'state': '的中', 'hits': [[11, 8, 2]], 'n': 18}, {'t': '馬単', 'state': '的中', 'hits': [[11, 8]], 'n': 9}, {'t': 'ワイド', 'state': '不的中', 'hits': [], 'n': 6}]}
MISS = dict(SPEC, rows=[dict(x, state='不的中', hits=[]) for x in SPEC['rows']])
STAGES = [(iid, kind, n, name) for iid, kind, st in _bcp.ITEMS for n, name in st]          # 59段
BY = {name: (iid, kind, n) for iid, kind, n, name in STAGES}
SO = set(_bcp.stills_out())


def mw(name):      # キャラの 入れものの 数（キャラ＋ボードの 前に 出る 所）
    L = (_bcp.MOTION.get(name) or {}).get('layers') or []
    return len(L) + sum(1 for l in L if l.get('f'))


def need(name):    # 絵を 出す のに いる もの（まわりの 光と 雲は あとから）
    m = _bcp.MOTION.get(name) or {}
    amb = [m['amb'][k] for k in ('m1', 'm2', 'm3', 'f')] if m.get('amb') else []
    return [f for f in _bcp.stage_files(name) if f not in amb]


PARTS = [nm for _i, _k, _n, nm in STAGES if (_bcp.MOTION.get(nm) or {}).get('bgx')]       # 部品を 重ねる 48段
STATE = """() => { const hb = document.querySelector('#fxOv .hb'), ov = hb && hb.parentNode, w = hb && hb.querySelector('.bcpw');
  if (!hb) return null;
  if (!w) return { w: 0, pic: hb.classList.contains('bcpic'), name: hb.dataset.bcp || '', rb: !!hb.querySelector('.rb'), bcp: !!hb.querySelector('.rb.bcp') };
  const ims = [...w.querySelectorAll('img')], bg = w.querySelector('.bcpbg');
  return { w: 1, pic: hb.classList.contains('bcpic'), done: ov.classList.contains('bcpdone'), ld: w.classList.contains('bcpld'), vis: bg ? getComputedStyle(bg).visibility : '',
    ok: ims.length > 0 && ims.every(i => i.complete && i.naturalWidth > 0), go: w.classList.contains('chrgo'), mo: w.dataset.mo || '', chr: w.querySelectorAll('.chrw').length,
    an: [...w.querySelectorAll('.chrw')].filter(e => e.getAnimations({ subtree: true }).length).length, sync: ims.every(i => i.decoding === 'sync'),
    srcs: ims.map(i => (i.getAttribute('src') || '').split('/').pop()), name: hb.dataset.bcp || '', st: hb.classList.contains('bcst'), rb: !!w.querySelector('.rb.bcp') }; }"""
# コマごとに 見る（絵が 見えて いる のに キャラが そろって いない コマ・絵が 出る 前に ほかの 絵を かくした コマ が ない こと）
PROBE = """(want) => { const P = window.__probe = { on: true, n: 0, bare: 0, early: 0, first: -1, t0: performance.now() };
  (function tick() { if (!P.on) return; const hb = document.querySelector('#fxOv .hb'), w = hb && hb.querySelector('.bcpw');
    if (w) { P.n++; const bg = w.querySelector('.bcpbg'), ld = w.classList.contains('bcpld'), vis = bg && getComputedStyle(bg).visibility === 'visible', chr = w.querySelectorAll('.chrw').length;
      if (vis && chr !== want) P.bare++;
      if (ld && hb.parentNode.classList.contains('bcpdone')) P.early++;
      if (vis && P.first < 0) P.first = Math.round(performance.now() - P.t0); }
    requestAnimationFrame(tick); })(); }"""
PROBE_END = "() => { const P = window.__probe; P.on = false; return { n: P.n, bare: P.bare, early: P.early, first: P.first }; }"
FREEZE = """() => { document.getElementById('fxOv').getAnimations({ subtree: true }).forEach(a => { const nm = a.animationName || '';
    try { if (/^bcm_/.test(nm)) { a.pause(); a.currentTime = 0; } else { const t = a.effect.getComputedTiming(); if (isFinite(t.endTime)) a.finish(); else { a.pause(); a.currentTime = 0; } } } catch (e) { /* なし */ } }); }"""
fails = []


def check(ok, msg):
    print(('  ✅ ' if ok else '  ❌ ') + msg, flush=True)
    if not ok: fails.append(msg)


try:
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])

        def page(dpr=1):
            ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=dpr, locale='ja-JP', timezone_id='Asia/Tokyo', reduced_motion='no-preference')
            pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
            bad = []; pg.on('response', lambda r: bad.append(r.url.split('/')[-1]) if r.status >= 400 and '/bcp_' in r.url else None)
            req = []; pg.on('request', lambda r: req.append(r.url.split('/')[-1]) if '/bcp_' in r.url else None)
            pg.goto(f'http://localhost:{PORT}/APP/'); pg.wait_for_timeout(1500)
            if pg.locator('#gateGo').count(): pg.click('#gateGo'); pg.wait_for_timeout(600)
            pg.evaluate('() => document.fonts.ready'); pg.wait_for_timeout(300)
            return ctx, pg, errs, bad, req

        def show(pg, name, calm=False):
            iid, kind, n = BY[name]
            pg.evaluate("(c) => TengelFx.set({ calm: c })", calm)
            pg.evaluate("([s, k, id, n]) => TengelFx.preview(s, k, { item: id, streak: n })", [MISS if kind == 'miss' else SPEC, 'miss' if kind == 'miss' else 'hit', iid, n])

        def ready(pg, name, calm, tmo=60):
            s = None; mot = name in _bcp.MOTION
            for _ in range(tmo):
                pg.wait_for_timeout(100); s = pg.evaluate(STATE)
                if s and s.get('w') and s['pic'] and s['done'] and not s['ld'] and s['ok'] and (calm or not mot or s['go']): return s
            return s

        def close(pg):
            pg.evaluate('TengelFx.close()'); pg.wait_for_timeout(200)

        # ---- 1) ふつう：59段 ぜんぶ（控えめ と 通常）----
        ctx, pg, errs, bad, req = page()
        t0 = time.time(); ng = []
        for iid, kind, n, name in STAGES:
            for calm in (True, False):
                pg.evaluate(PROBE, mw(name) if name in PARTS else 0)
                show(pg, name, calm); s = ready(pg, name, calm); pr = pg.evaluate(PROBE_END)
                mot = name in _bcp.MOTION; par = name in PARTS
                ok = bool(s) and s.get('w') == 1 and s['name'] == name and s['pic'] and s['done'] and not s['ld'] and s['vis'] == 'visible' and s['ok'] and s['sync'] and s['rb'] and s['st'] == calm
                ok = ok and sorted(s['srcs']) == sorted(need(name)) and not (set(s['srcs']) & SO)
                ok = ok and s['chr'] == (mw(name) if par else 0)                                    # 部品を 重ねる 絵は 控えめ でも キャラを かさねる
                ok = ok and s['go'] == (mot and not calm) and s['mo'] == (name if mot and not calm else '') and s['an'] == (s['chr'] if not calm else 0)
                ok = ok and pr['bare'] == 0 and pr['early'] == 0 and pr['first'] >= 0
                if not ok: ng.append((name, 'calm' if calm else 'go', s and {k: v for k, v in s.items() if k != 'srcs'}, pr))
                close(pg)
        check(not ng and not errs and not bad and not (set(req) & SO) and len(PARTS) == 48,
              f'59段 × 控えめ／通常：絵が 出る（部品を 重ねる 48段は 控えめ でも キャラを かさねて 止めた まま・通常は 動く）・読む 絵は アプリに 入れる もの だけ（止まった 版は 読まない）・'
              f'キャラの いない 背景 だけの コマ なし・エラーなし（{time.time() - t0:.0f}秒・読んだ 絵 {len(set(req))}こ・だめ {ng[:3]}・{errs[:2]}・{bad[:3]}）')
        ctx.close()

        # ---- 2) 部品が おそい（二人でしょんぼり 1回目：キャラ 1まいを 1.2秒 おくらせる）----
        ctx, pg, errs, bad, req = page()
        late = _bcp.MOTION['miss1']['layers'][1]['src']; held = []
        pg.route('**/' + late, lambda route: held.append(route))
        pg.evaluate(PROBE, mw('miss1')); show(pg, 'miss1', False); pg.wait_for_timeout(1200)
        s1 = pg.evaluate(STATE)
        for r in held: r.continue_()
        s2 = ready(pg, 'miss1', False); pr = pg.evaluate(PROBE_END)
        check(len(held) >= 1 and s1 and s1['w'] == 1 and s1['pic'] and s1['ld'] and s1['vis'] == 'hidden' and s1['chr'] == 0 and not s1['done'] and not s1['go'] and s1['rb']
              and s2 and not s2['ld'] and s2['vis'] == 'visible' and s2['chr'] == mw('miss1') and s2['done'] and s2['go'] and s2['ok'] and pr['bare'] == 0 and pr['early'] == 0 and pr['first'] >= 1100 and not errs,
              f'部品が おそい：そろう まで 絵を 出さない（背景も 見せない・ほかの 絵も かくさない・字の ボードは 出て いる）→ そろったら いっしょに 出て 動く'
              f'（待つ 間 {s1 and {k: s1[k] for k in ("ld", "vis", "chr", "done")}}・出た あと {s2 and {k: s2[k] for k in ("ld", "vis", "chr", "done", "go")}}・絵が 見えた のは {pr["first"]}ms・だめな コマ {pr["bare"]}／{pr["n"]}）')
        close(pg); pg.unroute('**/' + late)
        # 控えめ でも 同じ（2回目：キャラなしの 背景を おくらせる）
        late2 = _bcp.MOTION['miss1_2']['bgx']; held2 = []
        pg.route('**/' + late2, lambda route: held2.append(route))
        pg.evaluate(PROBE, mw('miss1_2')); show(pg, 'miss1_2', True); pg.wait_for_timeout(900)
        s1 = pg.evaluate(STATE)
        for r in held2: r.continue_()
        s2 = ready(pg, 'miss1_2', True); pr = pg.evaluate(PROBE_END)
        check(len(held2) >= 1 and s1 and s1['ld'] and s1['vis'] == 'hidden' and s1['chr'] == 0 and not s1['done'] and s2 and not s2['ld'] and s2['vis'] == 'visible' and s2['chr'] == mw('miss1_2')
              and s2['done'] and not s2['go'] and s2['an'] == 0 and pr['bare'] == 0 and pr['early'] == 0 and not errs,
              f'部品が おそい（控えめ・背景が おそい）：そろう まで 出さない → そろったら かさねた まま 止めて 出す（{s1 and {k: s1[k] for k in ("ld", "vis", "chr", "done")}} → {s2 and {k: s2[k] for k in ("ld", "vis", "chr", "done", "go", "an")}}）')
        close(pg); pg.unroute('**/' + late2)

        # ---- 3) 部品が 1まい 読めない → いつもの ボード（次…！ 1回目：前の 絵／隠蔽作戦 1回目：キャラ）----
        res3 = []
        for name, miss_f in (('miss2', _bcp.MOTION['miss2']['fgx']), ('miss3', _bcp.MOTION['miss3']['layers'][0]['src']), ('carry1', _bcp.MOTION['carry1']['bgx'])):
            pg.route('**/' + miss_f, lambda route: route.fulfill(status=404, body=''))
            show(pg, name, False); pg.wait_for_timeout(1500); s = pg.evaluate(STATE)
            res3.append((name, s)); close(pg); pg.unroute('**/' + miss_f)
        check(all(s and s['w'] == 0 and not s['pic'] and s['name'] == '' and s['rb'] and not s['bcp'] for _n, s in res3) and not errs,
              f'部品が 1まい 読めない（前の 絵・キャラ・背景）→ いつもの ボードに もどる（絵の 入れものは 消える・エラーなし）（{res3}）')

        # ---- 4) 部品が いつまでも こない → 8秒で いつもの ボード（あとから 届いても そのまま）----
        hang = _bcp.MOTION['miss4']['layers'][2]['src']; held4 = []
        pg.route('**/' + hang, lambda route: held4.append(route))
        show(pg, 'miss4', False); pg.wait_for_timeout(6500); s1 = pg.evaluate(STATE); pg.wait_for_timeout(2300); s2 = pg.evaluate(STATE)
        for r in held4:
            try: r.continue_()
            except Exception: pass
        pg.wait_for_timeout(800); s3 = pg.evaluate(STATE)
        check(len(held4) >= 1 and s1 and s1['w'] == 1 and s1['ld'] and s1['vis'] == 'hidden' and not s1['done'] and s2 and s2['w'] == 0 and not s2['pic'] and s2['rb'] and not s2['bcp']
              and s3 and s3['w'] == 0 and not s3['pic'] and not errs,
              f'部品が いつまでも こない：6.5秒は 待つ → 8秒で いつもの ボード → あとから 届いても そのまま（{s1 and {k: s1[k] for k in ("ld", "vis", "done")}} → {s2} → {s3}）')
        close(pg); pg.unroute('**/' + hang)

        # ---- 5) 読んで いる 間に とじる → エラーなし・つぎは ふつうに 出る ----
        slow = _bcp.MOTION['miss5']['bgx']; held5 = []
        pg.route('**/' + slow, lambda route: held5.append(route))
        show(pg, 'miss5', False); pg.wait_for_timeout(400); s1 = pg.evaluate(STATE); close(pg)
        gone = pg.evaluate("() => !document.getElementById('fxOv')")
        for r in held5:
            try: r.continue_()
            except Exception: pass      # とじた ときに 読むのを やめて いる ことも ある
        pg.wait_for_timeout(600); pg.unroute('**/' + slow)
        show(pg, 'miss5', False); s2 = ready(pg, 'miss5', False); close(pg)
        pg.wait_for_timeout(8200)      # 前の 待つ 時計（8秒）が あとで 何か こわさない
        show(pg, 'miss5_2', True); s3 = ready(pg, 'miss5_2', True)
        check(s1 and s1['ld'] and gone and s2 and not s2['ld'] and s2['chr'] == mw('miss5') and s2['go'] and s3 and not s3['ld'] and s3['chr'] == mw('miss5_2') and s3['pic'] and not errs,
              f'読んで いる 間に とじる → エラーなし・つぎは ふつうに 出る・前の 待つ 時計（8秒）の あとも こわれない（{s1 and s1["ld"]}・{gone}・{s2 and s2["chr"]}・{s3 and s3["chr"]}・{errs[:2]}）')
        close(pg); ctx.close()

        # ---- 6) つぎつぎ 出して とじる（40回）----
        ctx, pg, errs, bad, req = page()
        rnd = random.Random(4145); t0 = time.time(); last = None
        for i in range(40):
            name = rnd.choice([nm for _i, _k, _n, nm in STAGES]); calm = rnd.random() < .4
            show(pg, name, calm); pg.wait_for_timeout(rnd.choice([0, 30, 80, 150, 300, 700, 1300]))
            if i % 7 == 3: show(pg, rnd.choice(PARTS), not calm); pg.wait_for_timeout(120)       # とじずに つぎを 出す
            close(pg); last = name
        left = pg.evaluate("() => ({ ov: !!document.getElementById('fxOv'), w: document.querySelectorAll('.bcpw').length, css: document.querySelectorAll('style.bcmCss').length, cv: document.querySelectorAll('canvas.chramb').length })")
        show(pg, 'bouquet3', False); s = ready(pg, 'bouquet3', False); close(pg)
        check(not errs and not bad and not left['ov'] and left['w'] == 0 and left['cv'] == 0 and left['css'] <= 52 and s and s['chr'] == mw('bouquet3') and s['go'] and not (set(req) & SO),
              f'つぎつぎ 出して とじる（40回・{time.time() - t0:.0f}秒）：エラーなし・のこり物なし（{left}）・その あとも ふつうに 出る（花束 3連勝：キャラ {s and s["chr"]}）（{errs[:2]}・{bad[:3]}）')
        ctx.close()

        # ---- 7) 控えめ と 通常 で 同じ 絵（3倍の 大きさ）----
        ctx, pg, errs, bad, req = page(3)
        import numpy as np
        from PIL import Image
        import io
        res7 = []
        for name in ('ring2', 'toast3', 'race4', 'selfie1', 'stamp2', 'carry4', 'bouquet1', 'miss1_4', 'miss3_2', 'miss4_3', 'shusse8'):
            shots = []
            for calm in (True, False):
                show(pg, name, calm); ready(pg, name, calm); pg.wait_for_timeout(500); pg.evaluate(FREEZE); pg.wait_for_timeout(200)
                shots.append(np.asarray(Image.open(io.BytesIO(pg.screenshot(clip={'x': 0, 'y': 0, 'width': 390, 'height': 844}))).convert('RGB')).astype(np.int16)); close(pg)
            d = np.abs(shots[0] - shots[1]).max(-1); res7.append((name, int(d.max()), int((d > 0).sum())))
        check(all(mx <= 4 for _n, mx, _c in res7) and not errs, f'控えめ（かさねた まま）と 通常（動きを はじめの 形で 止める）は 同じ 絵（3倍の 大きさ・色の 差 4 まで）（{res7}）')
        ctx.close(); b.close()
finally:
    srv.terminate()
    shutil.rmtree(SRV, ignore_errors=True)
print('結果：', 'NG ' + str(len(fails)) if fails else 'OK')
sys.exit(1 if fails else 0)
