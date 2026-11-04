# 結果ボードカスタムの 動き（実験）：アプリの ためし（preview）を 1/60秒ずつ 写す（アニメーションの 時刻を すすめる＝test_bcx_flash.py と 同じ やり方）
#   python3 shots.py <出力の フォルダ> <clip の json>    clip = [{name, mode, item, kind, streak, dur, pokes:[秒…], label}, …]
import json, os, re, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
MO = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.dirname(os.path.dirname(os.path.dirname(MO)))
OUT = sys.argv[1]; CLIPS = json.loads(open(sys.argv[2], encoding='utf8').read()); DPR = float(os.environ.get('DPR', '2'))
SRV = os.environ.get('MOTION_SRV', '/home/claude/work/bcp_motion_srv'); PORT = 8802      # アプリの 画面を 置く 所（リポジトリの 外）
if not os.path.exists(os.path.join(SRV, 'APP', 'index.html')) or os.environ.get('BUILD'):
    shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
    subprocess.run(['node', 'build.js'], cwd=SRC, check=True, stdout=subprocess.DEVNULL)
    subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], cwd=SRC, check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, TARGET='app'))
    p = os.path.join(SRV, 'APP', 'index.html'); h = open(p, encoding='utf8').read()
    a = "window.__NATIVE = location.protocol === 'tengel:';"; assert a in h
    open(p, 'w', encoding='utf8').write(h.replace(a, 'window.__NATIVE = true;'))
    for f in os.listdir(os.path.join(SRC, 'ios', 'bcp_assets')):
        if f.endswith('.webp'): shutil.copy(os.path.join(SRC, 'ios', 'bcp_assets', f), os.path.join(SRV, 'APP', f))
t = open(os.path.join(SRC, 'test_native.py'), encoding='utf8').read()
FAKE = re.search(r'^FAKE = """(.*?)"""', t, re.S | re.M).group(1)
SETUP = re.search(r'^SETUP22 = """(.*?)"""', open(os.path.join(SRC, 'test_bcx_flash.py'), encoding='utf8').read(), re.S | re.M).group(1)
EXP = open(os.path.join(MO, 'bcp_motion_exp.js'), encoding='utf8').read()
SPEC_HIT = {'r': 9, 'n': 14, 'ranks': {'11': 11, '8': 8, '2': 2, '6': 1, '10': 3},
            'rows': [{'t': '3連単', 'state': '不的中', 'hits': [], 'n': 18}, {'t': '馬単', 'state': '的中', 'hits': [[11, 8]], 'n': 9}, {'t': 'ワイド', 'state': '不的中', 'hits': [], 'n': 6}]}
SPEC_MISS = dict(SPEC_HIT, rows=[dict(x, state='不的中', hits=[]) for x in SPEC_HIT['rows']])
LABEL = """(txt) => { let d = document.getElementById('mlab'); if (!d) { d = document.createElement('div'); d.id = 'mlab'; document.body.appendChild(d); }
  d.style.cssText = 'position:fixed;left:50%;top:50px;transform:translateX(-50%);z-index:2147483647;background:rgba(10,12,30,.78);color:#fff;font:700 15px/1.2 "BIZ UDPGothic",sans-serif;padding:7px 14px;border-radius:16px;border:1px solid rgba(255,255,255,.35);white-space:nowrap;pointer-events:none';
  d.textContent = txt; d.hidden = !txt; }"""
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=DPR, locale='ja-JP', reduced_motion='no-preference')
        ctx.add_init_script(FAKE); ctx.add_init_script("localStorage.setItem('tengel.gateSeen','1');"); ctx.add_init_script(EXP)
        pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(f'http://localhost:{PORT}/APP/'); pg.wait_for_timeout(2000)
        if pg.locator('#gateGo').count():
            try: pg.click('#gateGo', timeout=1500)
            except Exception: pass
        pg.wait_for_timeout(600)
        for c in CLIPS:
            d = os.path.join(OUT, c['name']); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
            pg.evaluate("(m) => { window.__bcpMotion = m; }", c['mode'])
            pg.evaluate(LABEL, c.get('label', ''))
            spec = SPEC_MISS if c['kind'] == 'miss' else SPEC_HIT
            pg.evaluate("([s, k, id, n]) => TengelFx.preview(s, k, { item: id, streak: n })", [spec, c['kind'], c['item'], c['streak']])
            pg.evaluate(SETUP)
            n = int(c['dur'] * 60); pokes = [int(round(x * 60)) for x in c.get('pokes', [])]; t0 = time.time(); on = -1
            for i in range(n + 1):
                if i in pokes: pg.evaluate('() => window.__bcpPoke()')
                pg.evaluate('(t) => window.__vt.step(t)', i * 1000 / 60)
                if on < 0 and pg.evaluate("() => !!document.querySelector('#fxOv .hb.bcpic.bcpon')"): on = i
                pg.screenshot(path=os.path.join(d, f'f{i:04d}.png'))
            info = pg.evaluate("""() => { const hb = document.querySelector('#fxOv .hb.bcpic'); if (!hb) return null; const m = hb.querySelector('.bcpm'), t = hb.querySelector('.bcpt');
              return { bcp: hb.dataset.bcp, m: m && m.className, t: t && t.className, done: !!document.querySelector('#fxOv .ov.bcpdone'), tr: t && getComputedStyle(t).transform.slice(0, 60) }; }""")
            print(c['name'], 'frames', n + 1, 'bcpon at', on, 'sec', round(time.time() - t0), info, flush=True)
            pg.evaluate('TengelFx.close()'); pg.wait_for_timeout(300)
        pg.evaluate(LABEL, '')
        print('errors', errs[:4])
        b.close()
finally:
    srv.terminate()
