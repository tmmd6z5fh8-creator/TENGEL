# CMの映像を作る：cm.html の render(t) を1コマずつ撮って ffmpeg に渡す（1080×1920・30fps・30秒）
#   python3 render.py test 1.5 5 7 …   → frames/f_<t>.png（確認用）
#   python3 render.py full              → video.mp4（音なし）
#   CMQ='?v=app' SHOTS=shots_app OUTV=video_app.mp4 python3 render.py full  → App Store版のアプリの中で見せる版（cm2.html の APPV・画面はApp Store版で撮ったもの）
import base64, json, os, subprocess, sys, time
from playwright.sync_api import sync_playwright
CM = os.path.dirname(os.path.abspath(__file__))
PORT = 8802; FPS = 30; DUR = 30.0
CMQ = os.environ.get('CMQ', ''); OUTV = os.environ.get('OUTV', 'video.mp4'); SHOTS = os.environ.get('SHOTS', 'shots')
mode = sys.argv[1] if len(sys.argv) > 1 else 'test'
meta = json.load(open(CM + '/' + SHOTS + '/meta.json', encoding='utf-8'))
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--bind', '127.0.0.1', '--directory', CM], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(0.8)
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': 540, 'height': 960}, device_scale_factor=2)
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
        pg.add_init_script('window.__META = ' + json.dumps(meta) + '; window.__SHOTS = ' + json.dumps(SHOTS) + ';')
        pg.goto(f'http://127.0.0.1:{PORT}/cm2.html{CMQ}')
        pg.evaluate('window.__ready')
        pg.wait_for_timeout(300)
        if errs:
            print('ERR', errs); sys.exit(1)
        cdp = pg.context.new_cdp_session(pg)

        def shot():   # 速い撮り方（PNGのまま・1080×1920）。古いコマが返らないことは確認ずみ
            d = cdp.send('Page.captureScreenshot', {'format': 'png', 'optimizeForSpeed': True,
                                                     'clip': {'x': 0, 'y': 0, 'width': 540, 'height': 960, 'scale': 2}})
            return base64.b64decode(d['data'])
        if mode == 'test':
            os.makedirs(CM + '/frames', exist_ok=True)
            for a in sys.argv[2:]:
                t = float(a)
                pg.evaluate(f'render({t})')
                open(f'{CM}/frames/f{"_app" if CMQ else ""}_{a}.png', 'wb').write(shot())
            print('frames ok')
        else:
            ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'png', '-i', '-',
                                   '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', str(FPS),
                                   '-movflags', '+faststart', CM + '/' + OUTV], stdin=subprocess.PIPE)
            n = int(round(DUR * FPS)); t0 = time.time()
            for i in range(n):
                pg.evaluate(f'render({i / FPS})')
                ff.stdin.write(shot())
                if i % 150 == 0:
                    print(f'{i}/{n}  {time.time() - t0:.0f}s', flush=True)
            ff.stdin.close(); ff.wait()
            if errs:
                print('ERR', errs)
            print('video ok', ff.returncode, f'{time.time() - t0:.0f}s')
        b.close()
finally:
    srv.terminate(); srv.wait()
