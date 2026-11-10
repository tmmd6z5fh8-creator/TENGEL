# 思い出フィギュアの 見本の 動画（App Store版を アプリ版として 開いて 1コマずつ 写す）
#   python3 kisekae/fig/fig_preview_cap.py <出す mp4>   （ios/fig_assets/ が いる）
#   記録タブ → フィギュアを作る → レース → デザイン（何も 書いて いない ボード）→ 3D で まわす → 作る → 飾る → ブースを かたむける → 一覧 → 部屋で まわす・近づく
import os, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.dirname(os.path.dirname(H)); os.chdir(W)
OUT = os.path.abspath(sys.argv[1]); FPS = 24
SRV = os.path.join(W, 'srv_figcap'); FR = os.path.join(SRV, 'frames'); PORT = 8797
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(FR)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, TARGET='app'))
pth = os.path.join(SRV, 'APP', 'index.html'); html = open(pth, encoding='utf8').read()
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
FGA = os.path.join(W, 'ios', 'fig_assets')
for f in os.listdir(FGA): shutil.copy(os.path.join(FGA, f), os.path.join(SRV, 'APP', f))
TCA = os.path.join(W, 'ios', 'tc_assets')         # 右上の トレーニングセンターの ボタンの 絵（ないと こわれた 絵の 印が 写る）
if os.path.isdir(TCA):
    for f in os.listdir(TCA): shutil.copy(os.path.join(TCA, f), os.path.join(SRV, 'APP', f))
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
sys.path.insert(0, W)
import importlib.util
spec = importlib.util.spec_from_file_location('tf', os.path.join(W, 'test_fig.py'))
src = open(os.path.join(W, 'test_fig.py'), encoding='utf8').read()
FAKE = src.split('FAKE = """')[1].split('"""')[0]; SEED = src.split('SEED = """')[1].split('"""')[0]
n = 0


def snap(pg, k=1):                     # 今の 画面を k コマぶん
    global n
    p = os.path.join(FR, f'f{n:05d}.jpg'); pg.screenshot(path=p, type='jpeg', quality=92); n += 1
    for _ in range(k - 1): shutil.copy(p, os.path.join(FR, f'f{n:05d}.jpg')); n += 1


def hold(pg, sec): snap(pg, max(1, round(sec * FPS)))


def gate(pg):
    g = pg.locator('#gate')
    for _ in range(40):
        if not g.count() or g.evaluate('e => e.hidden'): return
        try:
            if pg.locator('#gateGo').count(): pg.locator('#gateGo').click(timeout=2000)
            else: g.click(timeout=500)
        except Exception: pass
        pg.wait_for_timeout(150)


def idle(pg, fn, t=180000): pg.wait_for_function(fn, timeout=t); pg.wait_for_timeout(400)


try:
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo')
        ctx.add_init_script(FAKE); pg = ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(f'http://localhost:{PORT}/APP/'); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(600)
        pg.evaluate(SEED); pg.wait_for_timeout(600)
        # 前に 作った 7体（ブース 1 に 飾る）：①〜⑦
        pg.evaluate("""async () => { await TengelWallet.grant('cap-pts', 900000, 'テスト');
          for (let n = 1; n <= 7; n++) { const r = TengelMem.get(n % 2 ? 'figm1' : 'figm2'); await TengelWallet.fig.buy({ id: 'cap' + n, n, bet: r.id, info: r.info }, 22000, n - 1); } }""")
        pg.evaluate("() => { const b = [...document.querySelectorAll('.tabbar button')].find(x => /記録/.test(x.textContent)); b.click(); }"); pg.wait_for_timeout(900)
        pg.evaluate("() => document.querySelector('#recList .memtop').scrollIntoView({ block: 'center' })"); pg.wait_for_timeout(400)
        hold(pg, 1.6)
        pg.locator('#recList [data-act=figmake]').click(); idle(pg, "() => window.FigApp && FigApp._t.mode === 'make'")
        hold(pg, 1.3)
        pg.locator('#fgOv .fgrace').first.click(); idle(pg, "() => [...document.querySelectorAll('#fgOv .fgd img')].every(i => i.complete && i.naturalWidth > 0)")
        hold(pg, 1.8)
        pg.evaluate("() => document.querySelector('#fgOv .fgpn').scrollTo(0, 400)"); pg.wait_for_timeout(300); hold(pg, 1.2)
        pg.locator('#fgOv .fgd[data-n="8"]').click(); idle(pg, "() => FigApp._t.room && FigApp._t.room.F && document.querySelector('#fgOv .fgld').hidden")
        R = "FigApp._t.room"
        pg.evaluate(f"() => {{ {R}.intro = null; }}")
        for i in range(FPS * 4):            # 3D で まわす
            pg.evaluate(f"(a) => {{ {R}.yaw = a; {R}.pitch = 8; FigApp._t.draw(); }}", -30 + 360 * i / (FPS * 4)); snap(pg)
        pg.locator('#fgOv [data-fg=buy1]').click(); pg.wait_for_timeout(200); hold(pg, 0.8)
        pg.locator('#fgOv [data-fg=buy2]').click(); idle(pg, "() => FigApp._t.mode === 'booth' && document.querySelector('#fgOv .fgld').hidden")
        pg.evaluate("() => FigApp._t.draw()"); hold(pg, 1.8)
        pg.evaluate("() => FigApp._t.tapSlot(7)"); idle(pg, "() => FigApp._t.mode === 'booth' && document.querySelector('#fgOv .fgld').hidden")
        pg.evaluate("() => FigApp._t.draw()"); hold(pg, 1.2)
        pg.evaluate("() => FigApp._t.hold(true)")
        import math
        for i in range(FPS * 3):            # ブースを かたむける（奥行き）
            t = i / (FPS * 3); pg.evaluate("(a) => { const v = FigApp._t.view; v.yaw = a[0]; v.pitch = a[1]; FigApp._t.draw(); }", [11 * math.sin(t * 2 * math.pi), 4 * math.sin(t * 4 * math.pi)]); snap(pg)
        pg.evaluate("() => { const v = FigApp._t.view; v.yaw = 0; v.pitch = 0; FigApp._t.hold(false); FigApp._t.draw(); }")
        pg.locator('#fgOv [data-fg=over]').click()
        idle(pg, "() => { const c = document.querySelectorAll('#fgOv .fgoc canvas'); if (c.length !== 7) return false; return c[6].getContext('2d').getImageData(150, 200, 1, 1).data[3] > 0; }", 300000)
        hold(pg, 2.2)
        pg.locator('#fgOv .fgoc[data-p="0"]').click(); idle(pg, "() => FigApp._t.mode === 'booth' && document.querySelector('#fgOv .fgld').hidden")
        pg.evaluate("() => FigApp._t.draw()"); hold(pg, 0.8)
        pg.evaluate("() => FigApp._t.tapSlot(5)"); idle(pg, "() => FigApp._t.room && FigApp._t.room.F && document.querySelector('#fgOv .fgld').hidden")
        pg.evaluate(f"() => {{ {R}.intro = null; }}")
        for i in range(FPS * 5):            # 部屋で まわす
            pg.evaluate(f"(a) => {{ {R}.yaw = a; {R}.pitch = 10; {R}.zoom = 1; FigApp._t.draw(); }}", 360 * i / (FPS * 5)); snap(pg)
        for i in range(FPS * 2):            # ボードに 近づく
            t = i / (FPS * 2 - 1); e = t * t * (3 - 2 * t)
            pg.evaluate(f"(a) => {{ {R}.yaw = 0; {R}.pitch = 10 - 6 * a; {R}.zoom = 1 - 0.5 * a; FigApp._t.draw(); }}", e); snap(pg)
        hold(pg, 1.5)
        print('frames', n, 'errors', errs[:3], flush=True)
        b.close()
finally:
    srv.terminate()
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS), '-i', os.path.join(FR, 'f%05d.jpg'), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21',
                '-pix_fmt', 'yuv420p', '-movflags', '+faststart', OUT], check=True)
shutil.rmtree(SRV, ignore_errors=True)
print(OUT, os.path.getsize(OUT))
