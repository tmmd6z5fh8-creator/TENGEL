# 着せ替え（App Store版 第4弾）の光の点めつ（16.6・18.2）：壁紙の動き 29テーマと テーマの的中ボタン 29 を 60コマ/秒の絵にして kisekae/flash_px.py で数える
#   python3 test_ks_flash.py [sakura,sea,…] [--push] [--wall]   （時間がかかるので、ふだんのテストとは別に動かす。コマは t5/ks_frames/<テーマ>/ に残す）
#   壁紙：判定タブの画面ぜんぶ（390×844）を写す（16.6 の「画面の10%」と同じ物差し。上の絵は画面の約19%）。KS_CLIP=bnr なら上の絵（390×160）だけを写す（上の絵の中の割合＝きびしめ）。
#        動きは CSS のアニメーションだけなので Web Animations API で止めて 1/60秒ずつ進める。
#        「ときどき」の動き（花火の一斉・ナイターのゴール・夕焼けの日没 など）も拾えるように、0秒・8秒・19秒から 2秒ずつ（3つの窓）
#   的中ボタン：PUSHの画面 1秒 → タップ → 押したあと 1.5秒（はじけるかけら・光の筋・ボード）。画面ぜんぶを写す
#   絵（ios/kisekae_blobs/）が手元にあれば入れて数える（なければ絵なしで数える）
import os, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv_fx'); PORT = 8797
OUT = os.path.join(W, 't5', 'ks_frames')
args = [a for a in sys.argv[1:] if not a.startswith('--')]
DO_PUSH = '--push' in sys.argv or '--wall' not in sys.argv
DO_WALL = '--wall' in sys.argv or '--push' not in sys.argv
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, HIST='hist_280.json', DROP='', TARGET='app'))
pth = os.path.join(SRV, 'APP', 'index.html'); html = open(pth, encoding='utf8').read()
assert "window.__NATIVE = location.protocol === 'tengel:';" in html
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
BL = os.path.join(W, 'ios', 'kisekae_blobs')
if os.path.isdir(BL):
    for f in os.listdir(BL):
        shutil.copy(os.path.join(BL, f), os.path.join(SRV, 'APP', 'ks_' + f))
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
SPEC = {'r': 9, 'n': 12, 'ranks': {'6': 1, '2': 2, '10': 3}, 'rows': [{'t': '馬単', 'state': '的中', 'hits': [[6, 2]], 'n': 9}, {'t': '単勝', 'state': '的中', 'hits': [[6]], 'n': 3}, {'t': '3連単', 'state': '不的中', 'hits': [], 'n': 18}]}
STEP_B = """(t) => { const b = document.getElementById('ksBnr'); if (!b) return -1; const as = b.getAnimations({ subtree: true }); as.forEach(a => { try { a.pause(); a.currentTime = t * 1000; } catch (e) {} }); return as.length; }"""
STEP_F = """(t) => { const ov = document.getElementById('fxOv'); if (!ov) return -1; const as = ov.getAnimations({ subtree: true }); as.forEach(a => { try { a.pause(); a.currentTime = t * 1000; } catch (e) {} }); return as.length; }"""
fails = []


def count(d, tap):
    r = subprocess.run(['python3', os.path.join(W, 'kisekae', 'flash_px.py'), d, str(tap)], capture_output=True, text=True, env=dict(os.environ, AREA='.1'))
    out = r.stdout.strip().split('\n')
    return r.returncode == 0 and '窓 0個' in (out[0] if out else ''), (out[0] if out else ''), (out[-1] if out else ''), r.stderr[-300:]


try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', reduced_motion='no-preference')
        pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(f'http://localhost:{PORT}/APP/'); pg.wait_for_timeout(1500)
        if pg.locator('#gateGo').count(): pg.click('#gateGo'); pg.wait_for_timeout(600)
        pg.evaluate('TengelKisekae.ready')
        ids = args[0].split(',') if args else [t for t in pg.evaluate('TengelKisekae.list().map(t => t.id)') if t != 'default']
        for tid in ids:
            pg.evaluate("(id) => TengelKisekae.apply(id)", tid); pg.wait_for_timeout(700)
            if DO_WALL:
                d = os.path.join(OUT, tid, 'wall'); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
                bb = pg.locator('#ksBnr').bounding_box(); t0 = time.time()
                if not bb or bb['height'] < 100:
                    print(f'  ⚠️ {tid}：上の絵がない（{bb}）')
                else:
                    clip = {'x': bb['x'], 'y': bb['y'], 'width': bb['width'], 'height': bb['height']} if os.environ.get('KS_CLIP') == 'bnr' else {'x': 0, 'y': 0, 'width': 390, 'height': 844}
                    pg.evaluate("window.scrollTo(0, 0)")
                    idx = 0; n = 0
                    for w0 in (0.0, 8.0, 19.0):
                        for i in range(120):
                            n = pg.evaluate(STEP_B, w0 + i / 60); pg.screenshot(path=os.path.join(d, f'f{idx:04d}.png'), clip=clip); idx += 1
                    ok, bad, worst, err = count(d, 0)
                    print(('  ✅ ' if ok else '  ❌ ') + f'{tid} 壁紙{"（上の絵だけ）" if os.environ.get("KS_CLIP") == "bnr" else ""}：{idx}コマ・{n}の動き（{time.time() - t0:.0f}秒）… {bad}／{worst}')
                    if not ok: fails.append(tid + ' wall: ' + (err if err else bad))
            if DO_PUSH:
                d = os.path.join(OUT, tid, 'push'); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
                pg.evaluate("(s) => TengelFx.show(Object.assign({ force: 'hit' }, s))", SPEC); pg.wait_for_timeout(400)
                pc = pg.evaluate("(() => { const b = document.querySelector('#fxOv .push'); return b ? b.className : ''; })()")
                idx = 0; t0 = time.time()
                for i in range(60):
                    pg.evaluate(STEP_F, i / 60); pg.screenshot(path=os.path.join(d, f'f{idx:04d}.png'), clip={'x': 0, 'y': 0, 'width': 390, 'height': 844}); idx += 1
                tap = idx
                pg.evaluate('TengelFx.tap()'); pg.wait_for_timeout(300)
                for i in range(90):
                    pg.evaluate(STEP_F, i / 60); pg.screenshot(path=os.path.join(d, f'f{idx:04d}.png'), clip={'x': 0, 'y': 0, 'width': 390, 'height': 844}); idx += 1
                pg.evaluate('TengelFx.close()')
                ok, bad, worst, err = count(d, tap)
                print(('  ✅ ' if ok else '  ❌ ') + f'{tid} 的中ボタン（{pc}）：{idx}コマ（{time.time() - t0:.0f}秒）… {bad}／{worst}')
                if not ok: fails.append(tid + ' push: ' + (err if err else bad))
        if errs: print('  ⚠️ ページのエラー:', errs[:5]); fails.append('pageerror')
        b.close()
finally:
    srv.terminate()
print('結果：', 'NG ' + str(len(fails)) if fails else 'OK')
sys.exit(1 if fails else 0)
