# 結果ボードカスタム（App Store版 第4.91版）の 光の 点めつ（16.6）
#   python3 test_bcx_flash.py [carry]   （時間が かかるので、ふだんの テストとは 別に 動かす。コマは t5/fx_frames/bcx_<名前>/ に 残す）
#   第4.108版：「ボードを持つ馬」（carry・第4.113版から 16番）：「▶ 見る」の すぐ あと から 6秒（下から 出てくる 1秒 → 頭と首・後ろ足の ぷるぷる・しっぽ・まばたき → 1.5秒後に 1回 落としそうに なって あせる）を
#     1/60秒ずつ（その 時に ある アニメーションは 今の 時刻から 進める）写して kisekae/flash_px.py で 数える（1秒に 4回 以上 光る 点が 画面の 10% を こえる 1秒が ない こと）。
#     絵（ios/fx_assets/bcx_hb_*.webp）が なければ SVG の 馬
#   第4.113版：出世馬 8連続（幻の 馬・暗い 雷：rise8）は 出世馬と いっしょに 消した
import os, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv_bcx'); PORT = 8794
CASES = sys.argv[1].split(',') if len(sys.argv) > 1 else ['carry']
FX_DIR = os.path.join(W, 'ios', 'fx_assets')
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, HIST='hist_280.json', DROP='', TARGET='app'))
pth = os.path.join(SRV, 'APP', 'index.html'); html = open(pth, encoding='utf8').read()
assert "window.__NATIVE = location.protocol === 'tengel:';" in html
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
if os.path.isdir(FX_DIR):
    for f in os.listdir(FX_DIR):
        if f.startswith('bcx_hb_') and f.endswith('.webp'): shutil.copy(os.path.join(FX_DIR, f), os.path.join(SRV, 'APP', f))
art22 = os.path.isdir(FX_DIR) and all(os.path.exists(os.path.join(FX_DIR, f'bcx_hb_{k}.webp')) for k in ('head', 'fore', 'hind', 'tail', 'eye'))
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
SPEC = {'r': 9, 'n': 14, 'ranks': {str(i): i for i in range(1, 15)},
        'rows': [{'t': '3連単', 'state': '的中', 'hits': [[11, 8, 2]], 'n': 18}, {'t': '馬単', 'state': '的中', 'hits': [[11, 8]], 'n': 9}, {'t': 'ワイド', 'state': '不的中', 'hits': [], 'n': 6}]}
# 16「ボードを持つ馬」：その 時に ある アニメーションは 今の 時刻から 進める（at＝−今の 時刻）・あとで 生まれた もの（.bcgo の ぷるぷる など）は 生まれた 時刻から
SETUP22 = """() => {
  const ov = document.getElementById('fxOv'), stage = ov.querySelector('.fxs'), hb = stage.querySelector('.hb');
  const V = window.__vt = { seen: new Set(), track: [], go: -1 };
  ov.getAnimations({ subtree: true }).forEach(a => { V.seen.add(a); const c = a.currentTime || 0; a.pause(); V.track.push({ a, at: -c }); });
  const key = a => (a.effect && a.effect.target ? a.effect.target : null);
  const gone = a => { try { const el = key(a); if (!el || !a.animationName || !el.isConnected) return !el || !el.isConnected; return getComputedStyle(el, a.effect.pseudoElement || null).animationName.split(/,\\s*/).indexOf(a.animationName) < 0; } catch (e) { return true; } };
  const reg = ms => {
    V.track = V.track.filter(o => { if (gone(o.a)) { try { o.a.cancel(); } catch (e) { /* なし */ } return false; } return true; });
    ov.getAnimations({ subtree: true }).forEach(a => { if (V.seen.has(a)) return; V.seen.add(a); a.pause(); V.track.push({ a, at: ms }); });
  };
  V.step = t => {
    reg(t);
    V.track.forEach(o => { try { o.a.currentTime = Math.max(0, t - o.at); } catch (e) { /* 消えた */ } });
    if (V.go < 0 && hb.classList.contains('bcgo')) V.go = t;
    const sh = hb.querySelector('.bc-hbh:not(.bc-hbsv *)') || hb.querySelector('.bc-hbh');
    const rb = hb.querySelector('.rb'), mt = new DOMMatrix(getComputedStyle(rb).transform);
    if (V.go >= 0 && t - V.go > 1400) V.slip = Math.max(V.slip || 0, Math.abs(mt.f));     // 第4.108版：落としそうに なる（出おわって 1.5秒後）
    return { go: V.go, n: V.track.length, vec: hb.classList.contains('bchbv'), tr: sh ? getComputedStyle(sh).animationName.split(',')[0].trim() : '', slip: V.slip || 0 };
  };
  return { hb: hb.className };
}"""
fails = []
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', reduced_motion='no-preference')
        pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(f'http://localhost:{PORT}/APP/'); pg.wait_for_timeout(1500)
        if pg.locator('#gateGo').count(): pg.click('#gateGo'); pg.wait_for_timeout(600)
        if 'carry' in CASES:
            OUT = os.path.join(W, 't5', 'fx_frames', 'bcx_carry')
            pg.evaluate("(s) => TengelFx.preview(s, 'hit', { item: 'carry' })", SPEC)
            st = pg.evaluate(SETUP22)
            shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
            t0 = time.time(); n = int(6.0 * 60); r = {}
            for i in range(n + 1):
                r = pg.evaluate('(t) => window.__vt.step(t)', i * 1000 / 60)
                pg.screenshot(path=os.path.join(OUT, f'f{i:04d}.png'), clip={'x': 0, 'y': 0, 'width': 390, 'height': 844})
            pg.evaluate('TengelFx.close()')
            ok_seq = 900 < r['go'] < 1800 and r['tr'] == 'bcHbH' and r['vec'] == (not art22) and r['slip'] > 5
            print(('  ✅ ' if ok_seq else '  ❌ ') + f'ボードを持つ馬の 流れ：出おわって ぷるぷる {r["go"]:.0f}ms・頭と首の 動き {r["tr"]}・落としそうに なる（いちばん 下がって {r["slip"]:.1f}px）（絵：{"部品 5まい" if not r["vec"] else "SVG"}）（{st}）')
            if not ok_seq: fails.append('carry seq')
            rr = subprocess.run(['python3', os.path.join(W, 'kisekae', 'flash_px.py'), OUT, '0'], capture_output=True, text=True, env=dict(os.environ, AREA='.1'))
            out = rr.stdout.strip().split('\n'); worst = out[-1] if out else ''; bad = out[0] if out else ''
            ok = rr.returncode == 0 and '窓 0個' in bad
            print(('  ✅ ' if ok else '  ❌ ') + f'ボードを持つ馬（下から 出てくる → ぷるぷる・しっぽ・まばたき・落としそうに なって あせる）：{n + 1}コマ（{time.time() - t0:.0f}秒）… {bad}／{worst}')
            if not ok: fails.append('carry flash: ' + (rr.stderr[-300:] if rr.returncode else bad))
        if errs: print('  ⚠️ ページのエラー:', errs[:5]); fails.append('pageerror')
        b.close()
finally:
    srv.terminate()
    shutil.rmtree(SRV, ignore_errors=True)
print('結果：', 'NG ' + str(len(fails)) if fails else 'OK')
sys.exit(1 if fails else 0)
