# 的中の 演出（PUSH → 押す → 動画 → ボード）を アプリと 同じ 見た目で 1コマずつ 写す（30コマ／秒）
#   python3 shots_fx.py <出力の フォルダ> <種類 sgd など> <PUSH の 秒> <押した あとの 秒>
#   ・CSS の アニメーションは 止めて 時刻を すすめる（自分の 時計）。SVG の SMIL も 同じ 時刻に
#   ・動画は 止めて currentTime を その コマに（seeked を 待つ）。ブラウザは H.264 が 読めない ので webm（FILM 環境変数：名前=ファイル）
#   ・音は 入れない（make_fx_video.py で 元の 音を かさねる）。押した 時刻・動きだした 時刻は info.json に
import json, os, re, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
SRC = '/home/claude/tengel/source'; MO = os.path.dirname(os.path.abspath(__file__))
OUT, KIND, PUSH_S, AFTER_S = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
FPS = 30; DPR = float(os.environ.get('DPR', '2')); PORT = int(os.environ.get('PORT', '8807'))
FILMS = dict(kv.split('=') for kv in os.environ.get('FILM', 'sgd_film=sgd_film.webm').split(',') if kv)
SRV = os.path.join(MO, 'srv')
t = open(os.path.join(SRC, 'test_native.py'), encoding='utf8').read()
FAKE = re.search(r'^FAKE = """(.*?)"""', t, re.S | re.M).group(1)
SPEC = {'r': 11, 'n': 14, 'ranks': {'11': 11, '8': 8, '2': 2, '6': 1, '10': 3}, 'force': KIND,
        'rows': [{'t': '3連単', 'state': '的中', 'hits': [[11, 8, 2]], 'n': 18}, {'t': '馬単', 'state': '的中', 'hits': [[11, 8]], 'n': 9},
                 {'t': 'ワイド', 'state': '不的中', 'hits': [], 'n': 6}]}
CLOCK = """() => {
  const ov = () => document.getElementById('fxOv');
  const V = window.__fc = { seen: new Set(), track: [], t: 0 };
  V.reg = ms => { const o = ov(); if (!o) return; o.getAnimations({ subtree: true }).forEach(a => { if (V.seen.has(a)) return; V.seen.add(a); try { a.pause(); } catch (e) {} V.track.push({ a, at: ms }); }); };
  V.step = ms => {
    V.t = ms; V.reg(ms);
    V.track = V.track.filter(o => { try { const el = o.a.effect && o.a.effect.target; if (el && !el.isConnected) { o.a.cancel(); return false; } o.a.currentTime = Math.max(0, ms - o.at); return true; } catch (e) { return false; } });
    const o = ov(); if (o) o.querySelectorAll('svg').forEach(s => { try { if (!s.__p) { s.pauseAnimations(); s.__p = ms; } s.setCurrentTime(Math.max(0, (ms - s.__p) / 1000)); } catch (e) {} });
    return V.track.length;
  };
  return true;
}"""
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    if f.endswith('.png'): os.remove(os.path.join(OUT, f))
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
info = {}
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=DPR, locale='ja-JP', reduced_motion='no-preference')
        ctx.add_init_script(FAKE); ctx.add_init_script("localStorage.setItem('tengel.gateSeen','1');")
        pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(f'http://localhost:{PORT}/APP/'); pg.wait_for_timeout(2000)
        if pg.locator('#gateGo').count():
            try: pg.click('#gateGo', timeout=1500)
            except Exception: pass
        pg.wait_for_timeout(600)
        # 動画は blob の URL で（http.server は Range に こたえない＝そのままでは 止めた 動画の 時刻を うごかせない）
        pg.evaluate("""async (f) => { for (const k of Object.keys(f)) { const r = await fetch(f[k]); const bl = await r.blob(); window.__FX.films[k] = URL.createObjectURL(bl); } }""", FILMS)
        pg.evaluate(CLOCK)
        k = pg.evaluate("(s) => TengelFx.show(s)", SPEC)
        info['kind'] = k
        # 動画を 先に 読み おわらせる（アプリは 押す 前から 読んで いる）
        pg.wait_for_function("() => { const v = document.querySelector('video[data-film]'); return !v || v.readyState >= 3; }", timeout=20000)
        n = 0
        NP = int(round(PUSH_S * FPS))
        for i in range(NP):
            pg.evaluate('(ms) => window.__fc.step(ms)', i * 1000 / FPS)
            pg.screenshot(path=os.path.join(OUT, f'f{n:05d}.png')); n += 1
        # 押す（タップ）
        t_tap = NP * 1000 / FPS; info['tap'] = NP / FPS
        pg.evaluate('(ms) => window.__fc.step(ms)', t_tap)
        pg.evaluate("() => { const b = document.querySelector('#fxOv [data-fx=\"tap\"]'); if (b) b.click(); }")
        film = pg.evaluate("() => { const v = document.querySelector('#fxOv video'); return v ? v.dataset.film : null; }")
        info['film'] = film
        if film:
            pg.wait_for_function("() => { const v = document.querySelector('#fxOv video'); return v && v.classList.contains('on'); }", timeout=15000)
            pg.evaluate("() => { const v = document.querySelector('#fxOv video'); v.pause(); }")
            dur = pg.evaluate("() => document.querySelector('#fxOv video').duration"); info['film_dur'] = dur
        info['film0'] = NP / FPS
        pg.evaluate('(ms) => window.__fc.reg(ms)', t_tap)
        NA = int(round(AFTER_S * FPS))
        for j in range(NA):
            ms = t_tap + j * 1000 / FPS
            if film:
                ft = min((j + 0.5) / FPS, dur - 0.5 / FPS)
                pg.evaluate("""(ft) => new Promise(res => { const v = document.querySelector('#fxOv video'); if (!v) return res(0);
                  if (Math.abs(v.currentTime - ft) < 1e-4 && v.readyState >= 2) return res(1);
                  let ok = 0; const fin = () => { if (ok) return; ok = 1; requestAnimationFrame(() => requestAnimationFrame(() => res(1))); };
                  if (v.requestVideoFrameCallback) v.requestVideoFrameCallback(() => fin());      // 新しい コマが 画面に 出た とき
                  const sk = () => { v.removeEventListener('seeked', sk); setTimeout(fin, 400); }; v.addEventListener('seeked', sk);
                  v.currentTime = ft; })""", ft)
            pg.evaluate('(ms) => window.__fc.step(ms)', ms)
            pg.screenshot(path=os.path.join(OUT, f'f{n:05d}.png')); n += 1
            if j % 60 == 0: print('frame', n, 'film t', round(j / FPS, 2), flush=True)
        info['frames'] = n; info['errors'] = errs[:5]
        info['classes'] = pg.evaluate("() => { const o = document.getElementById('fxOv'); return o ? o.className + ' | ' + (o.querySelector('.ov') || {}).className : null; }")
        b.close()
finally:
    srv.terminate()
json.dump(info, open(os.path.join(OUT, 'info.json'), 'w'), ensure_ascii=False)
print(json.dumps(info, ensure_ascii=False))
