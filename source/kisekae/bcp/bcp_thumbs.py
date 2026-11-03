# 結果ボードカスタム（絵の ボード）：設定の タイルの 見本 bcp_t_<id>.webp を 作る（第4.121版）
#   python3 kisekae/bcp/bcp_thumbs.py <アプリの 画面の フォルダ> <出力フォルダ（ios/bcp_assets）> [シートの png]
#   アプリの 画面の フォルダ：TARGET=app python3 build_pwa.py <フォルダ> で 作って、index.html の
#     window.__NATIVE = location.protocol === 'tengel:'; を window.__NATIVE = true; に かえ、絵（bcp_<デザイン>.webp・_fg.webp）を 置いた もの
#   いちばん はじめの 段（1連勝・1回目）の 結果の 画面を 2倍で 写して、たて 3:4（舞台の 390×520）を 切り出す（360×480・webp）
import json, os, re, subprocess, sys, tempfile, time
from PIL import Image
import numpy as np
from playwright.sync_api import sync_playwright
H = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(os.path.dirname(H))
sys.path.insert(0, H)
import bcp_app
app, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
os.makedirs(out, exist_ok=True)
FAKE = re.search(r'^FAKE = """(.*?)"""', open(os.path.join(SRC, 'test_native.py'), encoding='utf8').read(), re.S | re.M).group(1)
D = bcp_app.data()
W, HT, OUTW, OUTH = 390, 520, 360, 480
TOP = {}                         # 切り出す 上の はし（舞台の pt）を デザインごとに 決める とき：{ id: pt }。ふつうは 板の まん中から 少し 上
SPEC = {'hit': [{'t': '3連単', 'state': '不的中', 'hits': [], 'n': 18}, {'t': '馬単', 'state': '的中', 'hits': [[11, 8]], 'n': 9}, {'t': 'ワイド', 'state': '不的中', 'hits': [], 'n': 6}],
        'miss': [{'t': '3連単', 'state': '不的中', 'hits': [], 'n': 18}, {'t': '馬単', 'state': '不的中', 'hits': [], 'n': 9}, {'t': 'ワイド', 'state': '不的中', 'hits': [], 'n': 6}]}
PORT = int(os.environ.get('PORT', '8797'))
root = os.path.dirname(app)
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', root], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(0.8)
sheet = []
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP')
        ctx.add_init_script(FAKE)
        pg = ctx.new_page()
        pg.goto(f'http://localhost:{PORT}/{os.path.basename(app)}/'); pg.wait_for_timeout(1500)
        g = pg.locator('#gateGo')
        if g.count():
            try: g.click(timeout=1500)
            except Exception: pass
        pg.wait_for_timeout(600)
        tmp = tempfile.mkdtemp()
        for iid, kind, st in bcp_app.ITEMS:
            name = st[0][1]
            spec = {'r': 9, 'n': 14, 'rows': SPEC[kind], 'ranks': {'11': 11, '8': 8, '2': 2, '6': 1, '10': 3}}
            pg.evaluate("([s, k, id]) => window.TengelFx.preview(s, k, { item: id, streak: 1 })", [spec, kind, iid])
            pg.wait_for_function("() => { const o = document.querySelector('#fxOv .ov.bcpdone'), bg = document.querySelector('#fxOv .bcpbg'); return !!(o && bg && bg.naturalWidth); }", timeout=15000)
            pg.wait_for_timeout(1800)                      # 行と 見出しの 出る 動きが おわるまで
            f = os.path.join(tmp, name + '.png'); pg.screenshot(path=f)
            pg.evaluate("() => window.TengelFx.close()"); pg.wait_for_timeout(150)
            im = Image.open(f).convert('RGB'); k = im.width / 390.0
            q = np.array(D['d'][name]['q']); cy = (q[:, 1].min() + q[:, 1].max()) / 2
            y0 = float(np.clip(TOP.get(iid, cy - HT * 0.47), 0, 844 - HT))
            c = im.crop((0, int(round(y0 * k)), int(round(W * k)), int(round((y0 + HT) * k)))).resize((OUTW, OUTH), Image.LANCZOS)
            fo = os.path.join(out, bcp_app.THUMB.format(iid)); c.save(fo, quality=84, method=6)
            sheet.append(c); print(iid, name, 'y0', round(y0), os.path.getsize(fo))
        b.close()
finally:
    srv.terminate()
if len(sys.argv) > 3:
    cols, sw, sh = 7, 180, 240
    S = Image.new('RGB', (cols * (sw + 8) + 8, ((len(sheet) + cols - 1) // cols) * (sh + 8) + 8), (40, 40, 48))
    for i, c in enumerate(sheet):
        S.paste(c.resize((sw, sh), Image.LANCZOS), (8 + (i % cols) * (sw + 8), 8 + (i // cols) * (sh + 8)))
    S.save(sys.argv[3])
