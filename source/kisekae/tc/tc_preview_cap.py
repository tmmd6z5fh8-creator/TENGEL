# 見本の 動画：tc_field_preview.html を 1/30秒ずつ 写す（朝・夕方・夜：TODS=morning,evening,night）→ mp4（音は あとで tc_amb.py の wav を かさねる）
#   python3 tc_preview_cap.py <出す mp4> [秒] [DPR]      絵は ios/tc_assets（TC_ASSETS）・作業 フォルダ（TC_WORK）に 集めて 写す
import os, subprocess, sys, time, shutil, glob
from playwright.sync_api import sync_playwright
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.dirname(os.path.dirname(H))
A = os.environ.get('TC_ASSETS', os.path.join(W, 'ios', 'tc_assets'))
D = os.environ.get('TC_WORK', '/tmp/tc_prev'); os.makedirs(D, exist_ok=True)
shutil.copy(os.path.join(H, 'tc_field_preview.html'), os.path.join(D, 'tc_preview.html'))
for f in glob.glob(os.path.join(A, 'tc_*')): shutil.copy(f, D)
shutil.copy(os.path.join(W, 'ios', 'fonts', 'BIZUDPGothic-Bold.ttf'), D)
OUT = sys.argv[1]
SEC = float(sys.argv[2]) if len(sys.argv) > 2 else 8; DPR = float(sys.argv[3]) if len(sys.argv) > 3 else 3
FR = os.path.join(D, 'frames'); shutil.rmtree(FR, ignore_errors=True); os.makedirs(FR)
PORT = 8811
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', D], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
n = 0
try:
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
        for tod in (os.environ.get('TODS') or 'morning,evening,night').split(','):
            pg = b.new_page(viewport={'width': 390, 'height': 614}, device_scale_factor=DPR)
            errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
            pg.goto(f'http://localhost:{PORT}/tc_preview.html?t={tod}&cap=1&seed=3'); pg.wait_for_function('() => window.__ready && window.__ready()', timeout=20000)
            pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(300)
            for i in range(int(SEC * 30)):
                pg.evaluate('(t) => window.__render(t)', 1.5 + i / 30)
                pg.screenshot(path=os.path.join(FR, f'f{n:05d}.jpg'), type='jpeg', quality=95); n += 1
            print(tod, 'frames', n, 'errors', errs[:3], flush=True)
            pg.close()
        b.close()
finally:
    srv.terminate()
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', '30', '-i', os.path.join(FR, 'f%05d.jpg'), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
                '-pix_fmt', 'yuv420p', '-movflags', '+faststart', OUT], check=True)
print(OUT, os.path.getsize(OUT))
