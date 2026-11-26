# 第4.228版：馬番 だけ 読めなかった 行の 読み直し・頭数より 少ない ときの 知らせ の テスト
#   GitHub の Mac（run 203）で 本物の Vision が まもなく 締切の 架空の 画面（e_soon.jpg）の 細い「11」を 読まなかった（testdata/ocr/e_soon_vision.json）→ 11番が 一覧から 抜けて いた。
#   App Store版（TARGET=app）を localhost で アプリ版として 開いて、画像を 読む（Vision の かわりに 読めた 文字と 位置を わたす：test_native.py の FAKE。
#   読み直し〈readText の opt〉は window.__ocrCrop が 返す）。ページの いまは 2026/10/01 12:00（日本）
#   ① 本物の Vision の 字（11 なし）・読み直しの 1回目（その 行の 所 2倍）は 何も 読めない・2回目（速い 読み方 3倍）で「11」→ 12頭（11番 14.7）・「読めなかった」なし・400P は 1回
#   ② 読み直しで 3回とも 読めない（3回目は 上と 下の 行も 入れた 所）→ 11頭・「読めなかった：単勝の11番 → 手で入れてね」
#   ③ 読み直しで もう ある 馬番（10）や 順に 合わない 数（13）しか 読めない → 使わない → ②と 同じ
#   ④ 人気順の 表（[人気] [枠] 馬番）で 11番の 馬番 だけ ない → 前は 枠の「6」を 馬番に して 6番が 2つ → 表 ぜんぶ 読めなかった。いまは 読み直しで 12頭
#   ⑤ 馬番が ぜんぶ 読めた 画面（A）→ 読み直さない（readText の opt なし）・「読めなかった」なし
#   ⑥ 表の 一部 だけ 写った 画面（12頭の うち 1〜8番）→ 読み直さない・「読めなかった：単勝の9・10・11・12番」
#   python3 test_v228.py
import json, os, re, shutil, subprocess, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv_v228'); PORT = 8846; APP = f'http://localhost:{PORT}/APP/'
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL,
               env=dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, HIST='hist_280.json', DROP='', TARGET='app'))
pth = os.path.join(SRV, 'APP', 'index.html'); html = open(pth, encoding='utf8').read()
assert "window.__NATIVE = location.protocol === 'tengel:';" in html
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
FAKE = re.search(r'\nFAKE = """(.*?)"""', open(os.path.join(W, 'test_native.py'), encoding='utf8').read(), re.S).group(1)      # アプリの 窓口の にせもの
OCR_DIR = os.path.join(W, 'testdata', 'ocr')
LD = lambda n: json.load(open(os.path.join(OCR_DIR, n + '.json'), encoding='utf-8'))['lines']
V, A, B = LD('e_soon_vision'), LD('a_tanfuku_waku'), LD('b_tanfuku_ninki')
B11 = [l for l in B if l['text'] == '11' and l['x'] > 0.1]       # 11番の 馬番（左の 0.021 の「11」は 人気の 11位）
assert len(B11) == 1
B2 = [l for l in B if l not in B11]
fails, errs = [], []
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c:
        fails.append(label)


CL = """() => { const f = JSON.parse(localStorage.getItem('tengel.form') || '{}');
  return { total: TengelWallet.total(), msg: (document.querySelector('#ocrMsg') || {}).innerText || '', n: f.n, r: f.r,
    rows: (f.rows || []).map(x => [x.no, x.tan]), re: (window.__ocrRe || []).slice(), err: (window.__pgErr || []).slice() }; }"""
DATE_AT = """(() => { const D = Date, OFF = Date.UTC(2026, 9, 1, 3, 0, 0) - D.now();
  class FD extends D { constructor(...a) { if (a.length) super(...a); else super(D.now() + OFF); } static now() { return D.now() + OFF; } }
  FD.UTC = D.UTC; FD.parse = D.parse; window.Date = FD; })();"""


def gate(pg):
    g = pg.locator('#gate')
    for _ in range(40):
        if not g.count() or g.evaluate('e => e.hidden'):
            return
        try:
            (pg.locator('#gateGo') if pg.locator('#gateGo').count() else g).click(timeout=1500)
        except Exception:
            pass
        pg.wait_for_timeout(150)


def inside(opt, x, y):
    c = opt.get('crop') or [0, 0, 0, 0]
    return c[0] <= x <= c[0] + c[2] and c[1] <= y <= c[1] + c[3]


try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        marks = {}

        def marker(source, q):
            op, key = q.get('op'), q.get('key')
            if op == 'set': marks[key] = q.get('value', '1'); return {'ok': True}
            if op == 'del': marks.pop(key, None); return {'ok': True}
            v = marks.get(key); return {'ok': True, 'has': v is not None, 'value': v}
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo')
        ctx.add_init_script(DATE_AT); ctx.add_init_script(FAKE)
        ctx.expose_binding('__saveBackup', lambda s, t: None); ctx.expose_binding('__marker', marker)
        pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(APP); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(700)

        def read(L, crop_js='null', jpg='e_soon.jpg', wait=2600):
            """L＝1まい目の 読めた 字・crop_js＝読み直しの 返事（opt → { ok, lines }）を 作る 関数（JS の 文字）"""
            pg.evaluate("(a) => { window.__ocrLines = [a]; window.__ocrRe = []; window.__ocrCrop = %s; document.getElementById('ocrMsg').textContent = ''; }" % crop_js, L)
            pg.set_input_files('#ocrFile', [os.path.join(OCR_DIR, jpg)])
            pg.wait_for_function("() => (document.getElementById('ocrMsg').innerText || '').includes('読み取った')", timeout=20000); pg.wait_for_timeout(wait)
            return pg.evaluate(CL)
        t0 = pg.evaluate('TengelWallet.total()')
        # ① 2回目（速い 読み方）で「11」
        c1 = read(V, "(o) => o.fast ? { ok: true, lines: [{ text: '11', x: 0.024, y: 0.67, w: 0.04, h: 0.017 }], w: 1170, h: 2532, ms: 60 } : { ok: true, lines: [], w: 1170, h: 2532, ms: 60 }")
        print('   ①', {k: c1[k] for k in ('total', 'n', 'r')}, c1['re'], c1['msg'][:120].replace('\n', ' / '))
        rows1 = dict((no, t) for no, t in c1['rows'])
        check(len(c1['rows']) == 12 and rows1.get(11) == '14.7' and c1['n'] == '12' and '単勝12頭' in c1['msg'] and '単勝の' not in c1['msg'],
              '①本物の Vision の 字（11 なし）→ 読み直しで「11」→ 単勝 12頭（11番 14.7）・「読めなかった」に 出ない')
        r1 = c1['re']
        check(len(r1) == 2 and r1[0].get('scale') == 2 and not r1[0].get('fast') and r1[1].get('fast') is True and r1[1].get('scale') == 3 and r1[1].get('langs') == ['en-US']
              and all(inside(o, 0.03, 0.679) and o['crop'][0] + o['crop'][2] < 0.097 for o in r1),
              f'①読み直しは 2回（その 行の 馬番の 所 2倍 → 速い 読み方 3倍・英数字）・所は 11番の 行の 馬番の 列（名前に かからない） {[o.get("crop") and [round(v, 3) for v in o["crop"]] for o in r1]}')
        check(c1['total'] == t0 - 400, f'①読み込みの ポイントは 1回 だけ（400P・読み直しで ふえない：{t0} → {c1["total"]}）')
        # ② 3回とも 読めない
        c2 = read(V, "(o) => ({ ok: true, lines: [], w: 1170, h: 2532, ms: 60 })")
        print('   ②', c2['re'], c2['msg'][:160].replace('\n', ' / '))
        r2 = c2['re']
        check(len(c2['rows']) == 11 and 11 not in [x[0] for x in c2['rows']] and '読めなかった：単勝の11番' in c2['msg'] and '手で入れてね' in c2['msg'],
              '②読み直しでも 読めない → 11頭のまま・「読めなかった：単勝の11番 → 手で入れてね」')
        check(len(r2) == 3 and r2[2].get('scale') == 2 and r2[2].get('langs') == ['en-US'] and inside(r2[2], 0.03, 0.632) and inside(r2[2], 0.03, 0.723),
              '②読み直しは 3回（3回目は 上と 下の 行〈10・12〉の 馬番も 入れた 所）')
        # ③ もう ある 馬番・順に 合わない 数 だけ
        c3 = read(V, "(o) => ({ ok: true, lines: o.fast ? [{ text: '10', x: 0.022, y: 0.669, w: 0.04, h: 0.016 }] : [{ text: '13', x: 0.022, y: 0.669, w: 0.04, h: 0.016 }, { text: '1', x: 0.6, y: 0.669, w: 0.02, h: 0.016 }], w: 1170, h: 2532, ms: 60 })")
        check(len(c3['rows']) == 11 and '読めなかった：単勝の11番' in c3['msg'] and len(c3['re']) == 3, '③読み直しで もう ある 馬番（10）・順に 合わない 数（13）・馬番の 列で ない 所の 数 しか 読めない → 使わない（11頭・読めなかった：単勝の11番）')
        # ④ 人気順の 表で 11番の 馬番 だけ ない（前は 枠の 6 を 馬番に して 表 ぜんぶ 読めなかった）
        c4 = read(B2, "(o) => ({ ok: true, lines: %s, w: 1170, h: 2532, ms: 60 })" % json.dumps(B11, ensure_ascii=False), jpg='b_tanfuku_ninki.jpg')
        rows4 = dict((no, t) for no, t in c4['rows'])
        print('   ④', c4['re'], c4['msg'][:120].replace('\n', ' / '))
        check(len(c4['rows']) == 12 and rows4.get(11) == '14.7' and rows4.get(6) == '2.4' and len(c4['re']) == 1 and '単勝の' not in c4['msg'],
              '④人気順の 表（[人気] [枠] 馬番）で 11番の 馬番 だけ ない → 枠の「6」を 馬番に しない・読み直し 1回で 12頭（前は 表 ぜんぶ 読めなかった）')
        # ⑤ ぜんぶ 読めた 画面
        c5 = read(A, "(o) => ({ ok: true, lines: [], w: 1170, h: 2532, ms: 60 })", jpg='a_tanfuku_waku.jpg')
        check(len(c5['rows']) == 12 and not c5['re'] and '単勝の' not in c5['msg'] and '頭ぶん' not in c5['msg'], '⑤馬番が ぜんぶ 読めた 画面 → 読み直さない・「読めなかった」に 単勝なし')
        # ⑥ 表の 一部（1〜8番）だけ
        cut = next(l['y'] for l in A if l['text'] == '54.0') + 0.02       # 8番（単勝 54.0）の 行まで（「8」は 枠にも ある）
        A8 = [l for l in A if l['y'] < cut]
        c6 = read(A8, "(o) => ({ ok: true, lines: [], w: 1170, h: 2532, ms: 60 })", jpg='a_tanfuku_waku.jpg')
        print('   ⑥', c6['re'], c6['msg'][:160].replace('\n', ' / '))
        check(len(c6['rows']) == 8 and not c6['re'] and '読めなかった：単勝の9・10・11・12番' in c6['msg'], '⑥表の 一部（12頭の うち 1〜8番）だけ → 読み直さない・「読めなかった：単勝の9・10・11・12番」')
        check(not errs, f'画面の エラー なし（{errs[:2]}）')
        ctx.close(); b.close()
finally:
    srv.terminate()
    shutil.rmtree(SRV, ignore_errors=True)
print('FAILS', len(fails), fails)
