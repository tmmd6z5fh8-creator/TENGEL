# App Storeの製品ページ（紹介ページ）のスクリーンショット・ポイント版（store_shots7.html を1枚ずつ撮る・10枚）
#   先に画面を撮る：TARGET=app CM_PREV=1 CM7=1 CM_PTS_BAL='1,100' CM_VW=443 CM_VH=960 CM_DPR=2 CM_OUT=shots_prev7 python3 cm2_shots.py
#                   TARGET=app CM_PREV=1 CM7=1 CM_PTS_BAL='1,100' CM_IPAD=1 CM_VW=1032 CM_VH=1376 CM_DPR=1.1627907 CM_OUT=shots_prev7_ipad python3 cm2_shots.py
#   python3 store_shots7.py <出力フォルダ>  → iphone_6.9/01.png …（1320×2868）・ipad_13/（2064×2752）
# App Storeは透明（アルファ）のある画像を受けつけないので、RGBで保存する
import json, os, subprocess, sys, time
from PIL import Image
from playwright.sync_api import sync_playwright
CM = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(CM, 'store7_out'))
PORT = 8804
DEVS = [  # 名前・CSSの大きさ・倍率・iPhoneかiPadか・写真のフォルダ・できる画像の大きさ
    ('iphone_6.9', 440, 956, 3, 'phone', 'shots_prev7', (1320, 2868)),
    ('ipad_13', 1032, 1376, 2, 'pad', 'shots_prev7_ipad', (2064, 2752)),
]
ONLY = os.environ.get('ONLY')   # 例：ONLY=1,2 で一部だけ
NS = [int(x) for x in ONLY.split(',')] if ONLY else list(range(1, 11))
DEVONLY = os.environ.get('DEV')
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--bind', '127.0.0.1', '--directory', CM], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(0.8)
errs = []
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        for name, w, h, dpr, dev, shots, size in DEVS:
            if DEVONLY and DEVONLY != dev:
                continue
            meta = json.load(open(os.path.join(CM, shots, 'meta.json'), encoding='utf-8'))
            os.makedirs(os.path.join(OUT, name), exist_ok=True)
            for n in NS:
                pg = b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=dpr)
                pg.on('pageerror', lambda e: errs.append(str(e)))
                pg.add_init_script('window.__META = ' + json.dumps(meta) + '; window.__SHOTS = ' + json.dumps(shots) + '; window.__SHOT = ' + json.dumps({'dev': dev, 'n': n}) + ';')
                pg.goto(f'http://127.0.0.1:{PORT}/store_shots7.html')
                pg.evaluate('window.__ready'); pg.wait_for_timeout(300)
                raw = os.path.join(OUT, name, f'_{n:02d}.png')
                pg.screenshot(path=raw)
                im = Image.open(raw).convert('RGB')
                assert im.size == size, (name, n, im.size)
                im.save(os.path.join(OUT, name, f'{n:02d}.png'), optimize=True)
                os.remove(raw)
                pg.close()
                print('  📸', name, n, size, flush=True)
        b.close()
finally:
    srv.terminate(); srv.wait()
print('errors', errs[:3])
