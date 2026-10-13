# App Storeのスクリーンショットを作る（store_shots.html を1枚ずつ撮る）
#   python3 store_shots.py <出力フォルダ>
#   → <出力フォルダ>/iphone_6.9/01.png …（1320×2868）・iphone_6.3/（1206×2622）・ipad_13/（2064×2752）
# 画面の写真は cm2_shots.py の App Store用（TARGET=app CM_PREV=1 …）で撮ったもの（shots_prev・shots_prev_ipad）
# App Storeは透明（アルファ）のある画像を受けつけないので、RGBで保存する
import json, os, subprocess, sys, time
from PIL import Image
from playwright.sync_api import sync_playwright
CM = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(CM, 'store_out'))
PORT = 8803
DEVS = [  # 名前・CSSの大きさ・倍率・iPhoneかiPadか・写真のフォルダ・できる画像の大きさ
    ('iphone_6.9', 440, 956, 3, 'phone', 'shots_prev', (1320, 2868)),
    ('iphone_6.3', 402, 874, 3, 'phone', 'shots_prev', (1206, 2622)),
    ('ipad_13', 1032, 1376, 2, 'pad', 'shots_prev_ipad', (2064, 2752)),
]
N = int(os.environ.get('N', '6'))
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--bind', '127.0.0.1', '--directory', CM], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(0.8)
errs = []
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        for name, w, h, dpr, dev, shots, size in DEVS:
            meta = json.load(open(os.path.join(CM, shots, 'meta.json'), encoding='utf-8'))
            os.makedirs(os.path.join(OUT, name), exist_ok=True)
            for n in range(1, N + 1):
                pg = b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=dpr)
                pg.on('pageerror', lambda e: errs.append(str(e)))
                pg.add_init_script('window.__META = ' + json.dumps(meta) + '; window.__SHOTS = ' + json.dumps(shots) + '; window.__SHOT = ' + json.dumps({'dev': dev, 'n': n}) + ';')
                pg.goto(f'http://127.0.0.1:{PORT}/store_shots.html')
                pg.evaluate('window.__ready'); pg.wait_for_timeout(250)
                raw = os.path.join(OUT, name, f'_{n:02d}.png')
                pg.screenshot(path=raw)
                im = Image.open(raw).convert('RGB')
                assert im.size == size, (name, n, im.size)
                im.save(os.path.join(OUT, name, f'{n:02d}.png'), optimize=True)
                os.remove(raw)
                pg.close()
                print('  📸', name, n, size)
        b.close()
finally:
    srv.terminate(); srv.wait()
print('errors', errs[:3])
