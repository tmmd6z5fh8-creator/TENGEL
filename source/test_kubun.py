import json, os
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
os.makedirs(os.path.join(W, 't3'), exist_ok=True)
page_html = open('tengel3.html', encoding='utf8').read()
hist = json.load(open('hist.json', encoding='utf8'))
harness = open('harness2.py', encoding='utf8').read()
mock = harness.split('mock = """', 1)[1].split('""" %', 1)[0] % json.dumps(hist, ensure_ascii=False)
skeleton = '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>[hidden]{display:none!important}</style>%s</head><body>%s</body></html>'
open('t3/h.html', 'w', encoding='utf8').write(skeleton % (mock, page_html))
Z = lambda a, b, t: {'a': a, 'b': b, 't': t}
cfg = {
 'A': [Z('人気', ['人気'], ['人気', '中穴']), Z('人気', ['中穴'], []), Z('中穴', ['人気'], ['人気'])],
 'B': [Z('人気', ['大穴', '超大穴'], ['人気', '大穴'])],
 'C0': [Z('人気', ['人気'], ['中穴']), Z('人気', ['中穴'], [])],
 'C1': [Z('人気', ['大穴'], ['人気', '中穴']), Z('中穴', ['中穴'], ['人気', '大穴']), Z('大穴', ['人気'], ['人気', '中穴']), Z('人気', ['中穴'], []), Z('超大穴', ['人気'], ['人気'])],
}
def form(r, n, baba, tan1, s1):
    odds = [tan1] + [round(tan1 + 1.7 * i + 0.3 * i * i, 1) for i in range(1, n)]
    rows = [{'no': i + 1, 'tan': str(odds[(i * 5) % n]), 'fuku': ''} for i in range(n)]
    return {"venue": "大井", "date": "2026-10-10", "r": str(r), "dist": "1400", "surface": "ダ", "baba": baba, "n": str(n), "s1": str(s1), "rows": rows}
cases = {'A': form(8, 12, '良', 1.5, 9.0), 'B': form(8, 12, '良', 2.0, 30.0), 'C0': form(2, 12, '良', 3.0, 70.0), 'C1': form(8, 12, '良', 3.0, 70.0), 'C2': form(8, 14, '良', 3.0, 70.0)}
errs = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for custom in (False, True):
        for k, f in cases.items():
            ctx = b.new_context(viewport={'width': 390, 'height': 900})
            pg = ctx.new_page(); pg.on('pageerror', lambda e, k=k: errs.append(f'{k}: {e}'))
            init = "localStorage.setItem('tengel.form', %s);" % json.dumps(json.dumps(f, ensure_ascii=False))
            if custom: init += "localStorage.setItem('tengel.zones', %s);" % json.dumps(json.dumps(cfg, ensure_ascii=False))
            pg.add_init_script(init)
            pg.goto('file://' + os.path.join(W, 't3/h.html')); pg.wait_for_timeout(700)
            kub = pg.locator('#result .vkubun').inner_text()
            zones = [x.inner_text().replace('\n', '') for x in pg.locator('#result .zflow').all()]
            thirds = [x.inner_text() for x in pg.locator('#result .zthird .t3').all()]
            txt = pg.locator('#outText').text_content()
            t3 = txt[txt.find('■STEP T3'):][:500].replace('\n', ' ⏎ ')
            print(('CUSTOM ' if custom else 'DEFAULT ') + k, '|', kub, '|', zones, '|', thirds)
            if custom and k in ('A', 'C1', 'C0'): print('   T3:', t3[:420]); print('   nums:', pg.locator('#result .numbers').inner_text().replace('\n', ' ')[:200])
            ctx.close()
    b.close()
print('ERRORS:', errs)
