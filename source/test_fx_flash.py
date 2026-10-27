# 的中ボタン（App Store版 第3弾）の光の点めつ（16.6）：画面を 60コマ/秒の絵にして kisekae/flash_px.py で数える（1秒に4回以上光る点が画面の10%をこえる1秒がないこと）
#   python3 test_fx_flash.py [hit,big,fz,miss,pc,sd,nd,film]   （時間がかかるので、ふだんのテストとは別に動かす。コマは t5/fx_frames/<種類>/ に残す）
#   第4.86版：隠れど的中（hidden）・超プレミアムど的中（zp）・神様的中（gd）は アプリから 消した（押したあとの 形が ない）
#   動きは CSS のアニメーションだけなので、Web Animations API で全部止めて 1/60秒ずつ進めながら写す（見本と同じ秒で数えられる）。
#   PUSHの画面を1秒 → タップ → 押したあと（的中 2.5秒・デカ 2.5秒・ハズレ 1.5秒・ど的中／隠れど的中 9.5秒）
#   第5弾（16.3）：プレミアムど的中 pc 13.1秒・超プレミアムど的中 zp 12.6秒・神様的中 gd 10.4秒（CSS と SVG：同じ やり方）。第4.66版：ど的中・紫電 sd
#   第4.70版：紫電の ② は 動画（sd_film.mp4）→ ③ は CSS。第4.71版：紫電は 押した 瞬間の プチュン（CSS）→ はじめから おわりまで 動画 → ボード（CSS）。
#     sd は 動画が 動いた 形（go）で、幕（.ov.sd）の 背景に その 時刻の 動画の コマ（60コマ/秒）を 入れて プチュン・ボードと いっしょに 写して 数える（動画が 手元に ある とき）
#   第4.77版：ノーマルど的中 nd（押すと 1秒 真っ暗 → はじめから おわりまで 動画 nd_film.mp4（10.5秒）→ ボード 10.05秒）：sd と 同じ やり方で 数える
#   第4.77版：極ど的中（紫電 sd）は ノーマルど的中の 動画から 入る → 5.34秒（白い 光に つつまれた 瞬間）で すぐ 極ど的中（プチュン → 動画）。
#     sd は 押した あと まず ノーマルど的中の 動画の コマ（5.34秒ぶん）を ならべて から、極ど的中の 幕を 写す（SD_UP の BLACK が あれば 真っ黒の コマも）
#     nd：第4.79版 押した 画面（.ndt：PUSH の 画面とは 別・押された PUSH が へこんで 光って はじける・火花 → 暗く → 1.05秒で 消える）も CSS なので いっしょに 進める
#   film＝超神様の 動画（sgd_film.mp4・超神様的中と 超プレミアム神様的中）と 昇格の 動画（spg_up.mp4）を ffmpeg で 60コマ/秒の 絵に して 数える（手元の ios/fx_assets/ に ある とき）
import os, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv_fx'); PORT = 8796
OUT = os.path.join(W, 't5', 'fx_frames')
KINDS = (sys.argv[1].split(',') if len(sys.argv) > 1 else ['hit', 'big', 'fz', 'miss'])
AFTER = dict(hit=2.5, big=2.5, miss=1.5, fz=9.5, pc=12.5, sd=11.5, nd=11.2)   # 第4.66版：ど的中・紫電（第4.71版：プチュン → 動画 10.5秒 → ボード 10.05秒）
SDBG = "([u, c]) => new Promise(ok => { const im = new Image(); im.onload = im.onerror = () => { const o = document.querySelector('#fxOv .ov.' + c); if (o) o.style.background = '#000 url(' + u + ') center / cover no-repeat'; requestAnimationFrame(() => ok(1)); }; im.src = u; })"
FX_DIR = os.path.join(W, 'ios', 'fx_assets')
sys.path.insert(0, os.path.join(W, 'kisekae')); from normal_do import SD_UP as SDUP   # 第4.77版：極ど的中の 入り
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, HIST='hist_280.json', DROP='', TARGET='app'))
pth = os.path.join(SRV, 'APP', 'index.html'); html = open(pth, encoding='utf8').read()
assert "window.__NATIVE = location.protocol === 'tengel:';" in html
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
if os.path.isdir(FX_DIR):   # ネオンの線画・プレミアムと 神様の 絵（手元で作ったもの。なければ 絵なしで数える）
    for f in os.listdir(FX_DIR):
        if f.endswith('.webp'): shutil.copy(os.path.join(FX_DIR, f), os.path.join(SRV, 'APP', f))
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
SPEC = {'r': 9, 'n': 12, 'ranks': {'6': 1, '2': 2, '10': 3, '4': 5, '7': 4, '11': 11, '1': 9, '3': 8, '5': 7, '9': 6, '8': 12, '12': 10},
        'rows': [{'t': '3連単', 'state': '的中', 'hits': [[11, 6, 2]], 'n': 18}, {'t': '馬単', 'state': '的中', 'hits': [[11, 6]], 'n': 9}, {'t': 'ワイド', 'state': '不的中', 'hits': [], 'n': 9}]}
STEP = """(t) => { const ov = document.getElementById('fxOv'); if (!ov) return -1; const as = ov.getAnimations({ subtree: true }); as.forEach(a => { try { a.pause(); a.currentTime = t * 1000; } catch (e) {} }); return as.length; }"""
fails = []
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', reduced_motion='no-preference')
        pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(f'http://localhost:{PORT}/APP/'); pg.wait_for_timeout(1500)
        if pg.locator('#gateGo').count(): pg.click('#gateGo'); pg.wait_for_timeout(600)
        for kind in KINDS:
            d = os.path.join(OUT, kind); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
            if kind == 'film':   # 動画：1コマずつ 描いた 絵（30コマ/秒）→ 60コマ/秒の 絵に して 数える（タップは 0コマ目）
                for f in ('sgd_film', 'spg_up', 'sd_film', 'nd_film'):
                    mp4 = os.path.join(FX_DIR, f + '.mp4')
                    if not os.path.exists(mp4) or not shutil.which('ffmpeg'):
                        print(f'  ⚠️ {f}.mp4 が ない（ios/fx_assets/）か ffmpeg が ない'); continue
                    fd = os.path.join(d, f); os.makedirs(fd); t0 = time.time()
                    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', mp4, '-vf', 'scale=390:844,fps=60', '-start_number', '0', os.path.join(fd, 'f%04d.png')], check=True)
                    nfr = len(os.listdir(fd))
                    r = subprocess.run(['python3', os.path.join(W, 'kisekae', 'flash_px.py'), fd, '0'], capture_output=True, text=True, env=dict(os.environ, AREA='.1'))
                    out = r.stdout.strip().split('\n'); worst = out[-1] if out else ''; bad = out[0] if out else ''
                    ok = r.returncode == 0 and '窓 0個' in bad
                    print(('  ✅ ' if ok else '  ❌ ') + f'{f}.mp4：{nfr}コマ（{time.time() - t0:.0f}秒）… {bad}／{worst}')
                    if not ok: fails.append(f + ': ' + (r.stderr[-300:] if r.returncode else bad))
                continue
            sdf = 0
            pre = []   # 極ど的中の 入り（ノーマルど的中の 動画の コマ）
            if kind == 'sd':
                mp4 = os.path.join(FX_DIR, 'nd_film.mp4')
                if os.path.exists(mp4) and shutil.which('ffmpeg'):
                    pd = os.path.join(OUT, '_sd_pre'); shutil.rmtree(pd, ignore_errors=True); os.makedirs(pd)
                    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', mp4, '-vf', 'scale=390:844,fps=60', '-start_number', '0', os.path.join(pd, 'p%04d.png')], check=True)
                    n_at = int(round(SDUP['AT'] * 60))
                    pre = [os.path.join(pd, f'p{i:04d}.png') for i in range(n_at)]
                    assert all(os.path.exists(x) for x in pre)
                    print(f'  sd：入りの ノーマルど的中の コマ {n_at}（{SDUP["AT"]}秒）→ 真っ黒 {int(round(SDUP["BLACK"] * 60))}コマ → 極ど的中')
                else:
                    print('  ⚠️ nd_film.mp4 が ない（極ど的中の 入りは 数えない）')
            if kind in ('sd', 'nd'):   # 紫電・ノーマルど的中の 動画の コマ（60コマ/秒・390×844）を 置いて、写す ときに 幕の 背景に する
                mp4 = os.path.join(FX_DIR, kind + '_film.mp4')
                if os.path.exists(mp4) and shutil.which('ffmpeg'):
                    fd = os.path.join(SRV, 'APP', '_sdf'); shutil.rmtree(fd, ignore_errors=True); os.makedirs(fd)
                    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', mp4, '-vf', 'scale=390:844,fps=60', '-start_number', '0', os.path.join(fd, 'g%04d.png')], check=True)
                    sdf = len(os.listdir(fd))
                    print(f'  {kind}：動画の コマ {sdf}（60コマ/秒）を 幕の 背景に して 写す')
                else:
                    print(f'  ⚠️ {kind}_film.mp4 が ない（CSS と ボードだけ 数える）')
            pg.evaluate("(s) => TengelFx.show(Object.assign({ force: %r }, s))" % kind, SPEC); pg.wait_for_timeout(400)
            idx = 0; t0 = time.time()
            if kind != 'miss':
                for i in range(60):
                    n = pg.evaluate(STEP, i / 60); pg.screenshot(path=os.path.join(d, f'f{idx:04d}.png'), clip={'x': 0, 'y': 0, 'width': 390, 'height': 844}); idx += 1
                tap = idx
                if pre:   # 極ど的中の 入り：ノーマルど的中の 動画の コマ → ブラックアウト（真っ黒）
                    from PIL import Image
                    for x in pre:
                        shutil.copy(x, os.path.join(d, f'f{idx:04d}.png')); idx += 1
                    blk = Image.new('RGB', (390, 844), (0, 0, 0))
                    for _ in range(int(round(SDUP['BLACK'] * 60))):
                        blk.save(os.path.join(d, f'f{idx:04d}.png')); idx += 1
                pg.evaluate('TengelFx.tap()'); pg.wait_for_timeout(300)
                if kind == 'sd':   # 第4.77版：ここでは 動画が 読めない → すぐ ブラックアウト → 0.5秒 → 極ど的中の 幕
                    pg.wait_for_function("() => !!document.querySelector('#fxOv .ov.sd')", timeout=10000)
                if kind in ('sd', 'nd'):   # 動画が 動いた 形（go）の ③ を 写す（動画は あとで コマを おきかえる）
                    pg.evaluate("(c) => { const o = document.querySelector('#fxOv .ov.' + c); o.classList.remove('still'); o.classList.add('go'); }", kind); pg.wait_for_timeout(200)
            else:
                tap = 0
            frames = int(AFTER[kind] * 60)
            for i in range(frames):
                n = pg.evaluate(STEP, i / 60)
                if kind in ('sd', 'nd') and sdf:   # 幕の 背景に その 時刻の 動画の コマ（おわった あとは さいごの コマ）
                    pg.evaluate(SDBG, [f'_sdf/g{min(i, sdf - 1):04d}.png', kind])
                pg.screenshot(path=os.path.join(d, f'f{idx:04d}.png'), clip={'x': 0, 'y': 0, 'width': 390, 'height': 844}); idx += 1
            pg.evaluate('TengelFx.close()')
            if kind in ('sd', 'nd'):
                shutil.rmtree(os.path.join(SRV, 'APP', '_sdf'), ignore_errors=True)
            if pre:
                shutil.rmtree(os.path.join(OUT, '_sd_pre'), ignore_errors=True)
            r = subprocess.run(['python3', os.path.join(W, 'kisekae', 'flash_px.py'), d, str(tap)], capture_output=True, text=True, env=dict(os.environ, AREA='.1'))
            out = r.stdout.strip().split('\n')
            worst = out[-1] if out else ''
            bad = out[0] if out else ''
            ok = r.returncode == 0 and '窓 0個' in bad
            print(('  ✅ ' if ok else '  ❌ ') + f'{kind}：{idx}コマ（{time.time() - t0:.0f}秒）… {bad}／{worst}')
            if not ok: fails.append(kind + ': ' + (r.stderr[-300:] if r.returncode else bad))
        if errs: print('  ⚠️ ページのエラー:', errs[:5]); fails.append('pageerror')
        b.close()
finally:
    srv.terminate()
print('結果：', 'NG ' + str(len(fails)) if fails else 'OK')
sys.exit(1 if fails else 0)
