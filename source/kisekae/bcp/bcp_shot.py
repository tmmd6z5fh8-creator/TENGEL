# 見本：テスト版の アプリで 結果ボードの ためし（preview）を 出して 写す。引数：出力 png・種類・行の 数・注入 JS（ファイル）
#   SRV（テスト版を 置いた フォルダの 親：<SRV>/TEST/index.html・bcp_<name>.webp）。テスト版は build_pwa.py（TARGET=app TENGEL_TEST=1）で 作って __NATIVE を true に
import json, os, re, sys, subprocess, time
from playwright.sync_api import sync_playwright
SRC = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
t = open(os.path.join(SRC, 'test_native.py'), encoding='utf8').read()
m = re.search(r'^FAKE = """(.*?)"""', t, re.S | re.M)
FAKE = m.group(1)
PORT = 8791
URL = f'http://localhost:{PORT}/TEST/'
out, kind, nrows = sys.argv[1], sys.argv[2], int(sys.argv[3])
inj = open(sys.argv[4], encoding='utf8').read() if len(sys.argv) > 4 and sys.argv[4] != '-' else ''
dpr = float(os.environ.get('DPR', '3'))
ROWS_ALL = [
  ('3連単', [[11, 8, 2]], 18), ('馬単', [[11, 8]], 9), ('ワイド', [], 6), ('3連複', [[2, 8, 11]], 7), ('馬連', [[8, 11]], 5),
  ('単勝', [[11]], 2), ('複勝', [[11], [8]], 3), ('枠連', [], 4), ('枠単', [], 1)]
def rows_for(kind, n):
    rs = []
    for i, (tt, hits, k) in enumerate(ROWS_ALL[:n]):
        st = '的中' if hits else '不的中'
        if kind == 'miss': st, hits = '不的中', []
        if kind == 'hit' and tt == '3連単': st, hits = '不的中', []
        rs.append({'t': tt, 'state': st, 'hits': hits, 'n': k})
    return rs
spec = {'r': 9, 'n': 14, 'rows': rows_for(kind, nrows), 'ranks': {'11': 11, '8': 8, '2': 2, '6': 1, '10': 3}}
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', os.environ.get('SRV_ROOT', '/home/claude/work/bcpic/srv')], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(0.8)
errs = []
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=dpr, locale='ja-JP')
        ctx.add_init_script(FAKE)
        pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(URL); pg.wait_for_timeout(1500)
        g = pg.locator('#gateGo')
        if g.count():
            try:
                g.click(timeout=1500)
            except Exception:
                pass
        pg.wait_for_timeout(600)
        k = pg.evaluate("([s, k]) => window.TengelFx.preview(s, k, { item: 'none' })", [spec, kind])
        pg.wait_for_timeout(2600)
        if inj:
            print("inj:", pg.evaluate(inj))
            pg.wait_for_timeout(900)
        info = pg.evaluate("""() => { const r = e => { if (!e) return null; const b = e.getBoundingClientRect(); return [Math.round(b.left*10)/10, Math.round(b.top*10)/10, Math.round(b.width*10)/10, Math.round(b.height*10)/10]; };
          const q = s => document.querySelector(s);
          return { kind: (q('#fxOv .ov')||{}).className, stage: r(q('#fxOv .fxs')), hb: r(q('#fxOv .hb')), rb: r(q('#fxOv .rb')), hd: r(q('#fxOv .rb .hd')), bh: r(q('#fxOv .rb .bh')), card: r(q('#fxOv .rb .card')),
                   rows: Array.from(document.querySelectorAll('#fxOv .rb .brows > li')).map(r), close: r(q('#fxOv [data-fx=close]')) || r(q('#fxOv .close')), vw: innerWidth, vh: innerHeight }; }""")
        print(json.dumps({'k': k, 'info': info}, ensure_ascii=False))
        if os.environ.get('PROBE'):
            print(json.dumps(pg.evaluate('window.__probe || null'), ensure_ascii=False, indent=0))
        pg.screenshot(path=out)
        if os.environ.get('HTML'):
            open(os.environ['HTML'], 'w', encoding='utf8').write(pg.evaluate("document.querySelector('#fxOv').outerHTML"))
        b.close()
finally:
    srv.terminate()
print('errs', errs[:5])
