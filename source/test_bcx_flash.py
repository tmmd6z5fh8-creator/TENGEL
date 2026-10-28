# 結果ボードカスタム（App Store版 第4.91版）の 出世馬 8連続（幻の 馬・暗い 雷）の 光の 点めつ（16.6）
#   python3 test_bcx_flash.py   （時間が かかるので、ふだんの テストとは 別に 動かす。コマは t5/fx_frames/bcx_rise8/ に 残す）
#   幻の 馬は 時刻の しかけ（setTimeout）で 幕・馬・雷・ボードの 飛んで もどる 動きを つけるので、その しかけを 1/60秒ずつ 進める しかけに かえて（TengelBoard._phantom）、
#   その 時に 生まれた CSS の アニメーションは 生まれた 時刻から の 時間に そろえて 止めて 写す（test_fx_flash.py と 同じ 60コマ/秒）→ kisekae/flash_px.py で 数える
#   （1秒に 4回 以上 光る 点が 画面の 10% を こえる 1秒が ない こと）。絵（ios/fx_assets/bcx_ph0・bcx_ph1.webp）が なければ SVG の 紫の 馬で 数える
import os, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv_bcx'); PORT = 8794
OUT = os.path.join(W, 't5', 'fx_frames', 'bcx_rise8')
FX_DIR = os.path.join(W, 'ios', 'fx_assets')
SEC = 4.9   # 幻の 馬（0.03秒）→ ボードが 飛ぶ（0.86秒）→ 雷 3回 → もどる（3.88秒）→ 冠と 札束（4.44秒）→ 幕が 消える（4.56秒）
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, HIST='hist_280.json', DROP='', TARGET='app'))
pth = os.path.join(SRV, 'APP', 'index.html'); html = open(pth, encoding='utf8').read()
assert "window.__NATIVE = location.protocol === 'tengel:';" in html
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
art = False
if os.path.isdir(FX_DIR):
    for f in os.listdir(FX_DIR):
        if f.endswith('.webp'): shutil.copy(os.path.join(FX_DIR, f), os.path.join(SRV, 'APP', f))
    art = all(os.path.exists(os.path.join(FX_DIR, f)) for f in ('bcx_ph0.webp', 'bcx_ph1.webp'))
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
SPEC = {'r': 9, 'n': 14, 'ranks': {str(i): i for i in range(1, 15)},
        'rows': [{'t': '3連単', 'state': '的中', 'hits': [[11, 8, 2]], 'n': 18}, {'t': '馬単', 'state': '的中', 'hits': [[11, 8]], 'n': 9}, {'t': 'ワイド', 'state': '不的中', 'hits': [], 'n': 6}]}
# 時刻の しかけ：sched(fn, ms) で ためて、step(t) で t までの ものを 順に 動かす。生まれた アニメーションは その 時刻を 0 に して 止める
SETUP = """() => {
  const ov = document.getElementById('fxOv'), stage = ov.querySelector('.fxs'), hb = stage.querySelector('.hb');
  ov.getAnimations({ subtree: true }).forEach(a => { try { const t = a.effect.getComputedTiming(); if (isFinite(t.endTime)) a.finish(); else a.pause(); } catch (e) { a.pause(); } });
  const V = window.__vt = { q: [], seen: new Set(ov.getAnimations({ subtree: true })), track: [] };
  ov.getAnimations({ subtree: true }).forEach(a => V.track.push({ a, at: -1, pre: true }));
  // 止めた（pause した）CSS の アニメーションは クラスが かわっても 残るので、名前が はずれた もの・同じ 名前で 生まれ直した ものの 古い ほうは 消す
  const key = a => (a.effect && a.effect.target ? a.effect.target : null);
  const gone = a => { try { const el = key(a); if (!el || !a.animationName || !el.isConnected) return !el || !el.isConnected; return getComputedStyle(el, a.effect.pseudoElement || null).animationName.split(/,\\s*/).indexOf(a.animationName) < 0; } catch (e) { return true; } };
  const sweep = () => { V.track = V.track.filter(o => { if (gone(o.a)) { try { o.a.cancel(); } catch (e) { /* なし */ } return false; } return true; }); };
  const reg = ms => {
    sweep();
    ov.getAnimations({ subtree: true }).forEach(a => {
      if (V.seen.has(a)) return;
      V.seen.add(a); a.pause();
      V.track = V.track.filter(o => { if (o.a !== a && key(o.a) === key(a) && o.a.animationName === a.animationName) { try { o.a.cancel(); } catch (e) { /* なし */ } return false; } return true; });
      V.track.push({ a, at: ms });
    });
  };
  V.step = t => {
    V.q.sort((x, y) => x.ms - y.ms);
    while (V.q.length && V.q[0].ms <= t) { const c = V.q.shift(); c.fn(); reg(c.ms); }
    reg(t);
    V.track.forEach(o => { if (o.pre) return; try { o.a.currentTime = Math.max(0, t - o.at); } catch (e) { /* 消えた */ } });
    return { q: V.q.length, n: V.track.length, ph: !!ov.querySelector('.bcph'), fly: hb.classList.contains('bcfly'), back: hb.classList.contains('bcback') };
  };
  TengelBoard._phantom(stage, hb, (fn, ms) => { V.q.push({ fn, ms }); });
  return { hb: hb.className, q: V.q.length };
}"""
fails = []
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', reduced_motion='no-preference')
        pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(f'http://localhost:{PORT}/APP/'); pg.wait_for_timeout(1500)
        if pg.locator('#gateGo').count(): pg.click('#gateGo'); pg.wait_for_timeout(600)
        pg.evaluate("(s) => TengelFx.preview(s, 'hit', { item: 'rise', streak: 4 })", SPEC)
        pg.wait_for_function("() => { const hb = document.querySelector('#fxOv .hb'); return hb && hb.classList.contains('bcgo'); }", timeout=10000)
        pg.wait_for_timeout(2600)
        st = pg.evaluate(SETUP)
        shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
        t0 = time.time(); seen = {'ph': 0, 'fly': 0, 'back': 0}
        n = int(SEC * 60)
        for i in range(n + 1):
            r = pg.evaluate('(t) => window.__vt.step(t)', i * 1000 / 60)
            for k in seen: seen[k] += 1 if r[k] else 0
            pg.screenshot(path=os.path.join(OUT, f'f{i:04d}.png'), clip={'x': 0, 'y': 0, 'width': 390, 'height': 844})
        pg.evaluate('TengelFx.close()')
        ok_seq = seen['ph'] > 200 and 30 < seen['fly'] < 200 and 0 < seen['back'] < 60 and r['q'] == 0 and not r['ph']
        print(('  ✅ ' if ok_seq else '  ❌ ') + f'幻の 馬の 流れ：幕 {seen["ph"]}コマ・飛ぶ {seen["fly"]}コマ・もどる {seen["back"]}コマ（絵：{"動画の 2まい" if art else "SVG"}）（{st}）')
        if not ok_seq: fails.append('seq')
        rr = subprocess.run(['python3', os.path.join(W, 'kisekae', 'flash_px.py'), OUT, '0'], capture_output=True, text=True, env=dict(os.environ, AREA='.1'))
        out = rr.stdout.strip().split('\n'); worst = out[-1] if out else ''; bad = out[0] if out else ''
        ok = rr.returncode == 0 and '窓 0個' in bad
        print(('  ✅ ' if ok else '  ❌ ') + f'出世馬 8連続（幻の 馬・暗い 雷）：{n + 1}コマ（{time.time() - t0:.0f}秒）… {bad}／{worst}')
        if not ok: fails.append('flash: ' + (rr.stderr[-300:] if rr.returncode else bad))
        if errs: print('  ⚠️ ページのエラー:', errs[:5]); fails.append('pageerror')
        b.close()
finally:
    srv.terminate()
    shutil.rmtree(SRV, ignore_errors=True)
print('結果：', 'NG ' + str(len(fails)) if fails else 'OK')
sys.exit(1 if fails else 0)
