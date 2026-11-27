# 第4.227版（まさちゃん 2026/11/26 17:07「レース判定で、画像を読み込んでから、まもなく締め切りレースが締め切りレースになってる！ 改善して！」）の テスト
#   App Store版（TARGET=app）を localhost で アプリ版として 開いて、画像を 読む（Vision の かわりに 読めた 文字と 位置を わたす：test_native.py の FAKE）。
#   ページの いまは 2026/10/01 12:00（日本）。前の 版では ①②⑤ が 締切済みに なって いた
#   ① 画面に「まもなく締切」→ 締切済みに しない（馬を 選ぶ 行と「買い目を予約」が 出る）… 前は「画面に「締切」」
#   ② 入力に 前の 日の 日付（09/20）が 残って いて、画像に 日付が ない（発走 18:05）→ きょうの レースと みなす → 締切済みに しない … 前は「発走 18:05 を過ぎている」
#   ③ 同じ（日付なし）で 発走 09:00 → きょうの 09:00 は すぎた → 締切済み（時刻）
#   ④ 入力が 先の 日付（10/05）・画像に 日付なし・発走 09:00 → 締切済みに しない（前売り）
#   ⑤ 画像の いちばん 上に iPhone の 時計（11:58）・発走の 時刻なし・日付なし（入力は きょう）→ 時計を 発走に しない → 締切済みに しない … 前は 11:58 を 発走に して 締切済み
#   ⑥ 前と 同じ：画像に 日付（10月1日）と 発走 09:00 → 締切済み（時刻）・「発売締切」→ 締切済み（言葉）
#   ⑦「発売締切」で 締切済みに なった レースを「まもなく締切」の 画面で 読み直す（0P）→ 締切済みでは なくなる → 予約できる（締切済みレースの 記録は 予約に かわる）
#   python3 test_v227.py
import json, os, re, shutil, subprocess, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv_v227'); PORT = 8845; APP = f'http://localhost:{PORT}/APP/'
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL,
               env=dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, HIST='hist_280.json', DROP='', TARGET='app'))
pth = os.path.join(SRV, 'APP', 'index.html'); html = open(pth, encoding='utf8').read()
assert "window.__NATIVE = location.protocol === 'tengel:';" in html
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
FAKE = re.search(r'\nFAKE = """(.*?)"""', open(os.path.join(W, 'test_native.py'), encoding='utf8').read(), re.S).group(1)      # アプリの 窓口の にせもの（画像の 読み取りは window.__ocrLines）
OCR_DIR = os.path.join(W, 'testdata', 'ocr'); JPG = os.path.join(OCR_DIR, 'a_tanfuku_waku.jpg')
A = json.load(open(os.path.join(OCR_DIR, 'a_tanfuku_waku.json'), encoding='utf-8'))['lines']
fails, errs = [], []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c:
        fails.append(label)


def lines(r, date='10月14日(水)', start='18:05', extra=(), clock=None):
    """架空の オッズ画面（A：枠つき）の 読めた 文字。R・日付（'' で なし）・発走（None で なし）を かえる・下に 言葉・上に iPhone の 時計"""
    out = []
    for ln in A:
        t = ln['text'].replace('第9競走', f'第{r}競走').replace('9R', f'{r}R').replace('10月14日(水)', date).replace('発走 18:05', f'発走 {start}' if start else '')
        out.append(dict(ln, text=t))
    for e in extra:
        out.append({'text': e, 'x': 0.62, 'y': 0.955, 'w': 0.3, 'h': 0.03})
    if clock:
        out.insert(0, {'text': clock, 'x': 0.07, 'y': 0.004, 'w': 0.12, 'h': 0.02})
    return out


CL = """() => { const q = s => document.querySelector(s), t = s => (q(s) || {}).innerText || ''; const f = JSON.parse(localStorage.getItem('tengel.form') || '{}');
  const bets = [...TengelLocal.mem.bets.values()]; return { total: TengelWallet.total(), msg: t('#ocrMsg'), chips: [...document.querySelectorAll('#result .chip')].map(c => c.innerText),
    reserve: document.querySelectorAll('#recCard [data-rsv=reserve]').length, card: t('#recCard'), closed: f.closed || null, r: q('#fR').value, date: f.date, start: f.start || '',
    bets: bets.map(b => ({ id: b.id, r: b.r, date: b.date, state: b.rsv ? b.rsv.state : null, by: b.rsv ? b.rsv.by : null, word: b.rsv ? b.rsv.word : null })) }; }"""
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


def rsv_lines(pg):
    """第4.233版：買い目の 行が ない ときは、前の 版の はじめの 形（推奨ごとに 馬単・3着の ある 推奨は 3連単も）の 行を「＋券種」で 足す"""
    card = pg.locator('#recCard')
    if card.locator('.rline').count() or not card.locator('[data-k=radd]').count(): return
    nz = pg.locator('#result ol.zones > li').count(); t3 = pg.locator('#result .zthird .zref').count() > 0
    for t in ['馬単'] * nz + (['3連単'] * nz if t3 else []):
        card.locator(f'[data-k=radd] button[data-v="{t}"]').click(); pg.wait_for_timeout(120)


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

        def read(L, date=None, wait=2600):
            if date:
                pg.fill('#fDate', date); pg.wait_for_timeout(400)
            pg.evaluate("window.__ocrLines = %s" % json.dumps([L], ensure_ascii=False))
            pg.set_input_files('#ocrFile', [JPG]); pg.wait_for_timeout(wait)
            return pg.evaluate(CL)

        def open_ok(c):
            return c['closed'] is None and '締切済み' not in c['chips'] and '締切済み' not in c['msg'] and c['reserve'] == 1
        # 第4.230版（まさちゃん 2026/11/27 01:18「1レース読み込み800Pにして！」・答え「5連も800P」）：この テストは 9レース 読む（800P × 9 ＝ 7,200P）→ はじめの 5,000P では 足りない ので テスト用に 4,000P 足す
        g0 = pg.evaluate('TengelWallet.total()')
        check(pg.evaluate("TengelWallet.grant('test-v227-read', 4000, 'テストの 足し')") is True and pg.evaluate('TengelWallet.total()') == g0 + 4000, f'テスト用に 4,000P 足す（9レース 読む ぶん：{g0} → {g0 + 4000}P）')
        t0 = pg.evaluate('TengelWallet.total()')
        # ① 画面に「まもなく締切」
        c1 = read(lines(9, extra=['まもなく締切']))
        print('   ①', {k: c1[k] for k in ('total', 'closed', 'date', 'start', 'r', 'reserve', 'chips')})
        check(c1['r'] == '9' and c1['date'] == '2026-10-14' and c1['start'] == '18:05' and open_ok(c1) and c1['total'] == t0 - 800,
              f'①「まもなく締切」の ある 9R（10月14日 18:05）→ 締切済みに しない・「買い目を予約」が 出る・読み込みは 800P（残り {c1["total"]}P）')
        c1b = read(lines(9, extra=['締切まで あと2分', '間もなく締め切ります']))
        check(c1b['total'] == c1['total'] and open_ok(c1b) and '0P' in c1b['msg'], '①「締切まで あと2分」「間もなく締め切ります」で 読み直しても 締切済みに しない（同じ レース 0P）')
        # ② 前の 日の 日付が 入力に 残って いる・画像に 日付なし・発走 18:05
        c2 = read(lines(10, date=''), date='2026-09-20')
        print('   ②', {k: c2[k] for k in ('total', 'closed', 'date', 'start', 'r', 'reserve', 'chips')})
        check(c2['r'] == '10' and c2['date'] == '2026-09-20' and c2['start'] == '18:05' and open_ok(c2),
              '②入力に 前の 日の 日付（09/20）・画像に 日付なし・発走 18:05 → きょう（10/01）の 18:05 と くらべて 締切済みに しない（前は「発走 18:05 を過ぎている」）')
        # ③ 同じで 発走 09:00 → 締切済み（時刻）
        c3 = read(lines(11, date='', start='09:00'), date='2026-09-20')
        print('   ③', {k: c3[k] for k in ('total', 'closed', 'date', 'start', 'r', 'reserve', 'chips')})
        check(bool(c3['closed']) and c3['closed'].get('by') == 'time' and c3['closed'].get('start') == '09:00' and '締切済み' in c3['chips'] and c3['reserve'] == 0 and '発走 09:00 を過ぎている' in c3['msg'],
              '③画像に 日付なし・発走 09:00（いまは 12:00）→ きょうの 09:00 を すぎて いる ので 締切済み（時刻）')
        # ④ 入力が 先の 日付・画像に 日付なし・発走 09:00 → 締切済みに しない
        c4 = read(lines(12, date='', start='09:00'), date='2026-10-05')
        check(c4['r'] == '12' and c4['date'] == '2026-10-05' and c4['start'] == '09:00' and open_ok(c4), '④入力が 先の 日付（10/05）・画像に 日付なし・発走 09:00 → 締切済みに しない（前売りの オッズ）')
        # ⑤ iPhone の 時計だけ（発走・日付なし）・入力は きょう
        c5 = read(lines(8, date='', start=None, clock='11:58'), date='2026-10-01')
        print('   ⑤', {k: c5[k] for k in ('total', 'closed', 'date', 'start', 'r', 'reserve', 'chips')})
        got5 = (c5['msg'].split('読み取った：') + [''])[1].split('\n')[0]
        check(c5['r'] == '8' and c5['date'] == '2026-10-01' and c5['start'] == '' and open_ok(c5) and '単勝' in got5 and '発走' not in got5,
              '⑤画像の 上に iPhone の 時計（11:58）・発走の 時刻なし → 時計を 発走に しない（発走は 空）・締切済みに しない（前は 11:58 を 発走に して 締切済み）')
        c5b = read(lines(7, date='', start=None, clock='11:58', extra=['発走時刻 18:40']), date='2026-10-01')
        check(c5b['start'] == '18:40' and open_ok(c5b), '⑤時計＋「発走時刻 18:40」→ 発走は 18:40（前は 時刻が 2つで 読めなかった）・締切済みに しない')
        # ⑥ 前と 同じ
        c6 = read(lines(6, date='10月1日(木)', start='09:00'))
        check(bool(c6['closed']) and c6['closed'].get('by') == 'time' and c6['date'] == '2026-10-01' and '締切済み' in c6['chips'] and c6['reserve'] == 0, '⑥画像に 日付（10月1日）と 発走 09:00 → 締切済み（時刻：前と 同じ）')
        c6b = read(lines(5, extra=['発売締切']))
        check(bool(c6b['closed']) and c6b['closed'].get('by') == 'kw' and c6b['closed'].get('word') == '発売締切' and '画面に「発売締切」' in c6b['msg'] and c6b['reserve'] == 0
              and any(x['r'] == 5 and x['state'] == 'closed' for x in c6b['bets']), '⑥画面に「発売締切」→ 締切済み（言葉：前と 同じ）・締切済みレースに 入る')
        c6c = read(lines(4, extra=['締切 まもなく発走']))
        check(bool(c6c['closed']) and c6c['closed'].get('word') == '締切', '⑥「締切 まもなく発走」（締切の あと）→ 締切済み')
        # ⑦ 締切済みに なった 5R を「まもなく締切」の 画面で 読み直す
        tb = c6c['total']
        c7 = read(lines(5, extra=['まもなく締切']))
        check(c7['r'] == '5' and c7['total'] == tb and open_ok(c7), f'⑦「発売締切」で 締切済みに なった 5R を「まもなく締切」で 読み直す（0P）→ 締切済みでは なくなる・「買い目を予約」が 出る（{c7["card"][:40]}…）')
        rsv_lines(pg)      # 第4.233版：券種ごとの 行を 足してから 予約
        pg.locator('#recCard [data-rsv=reserve]').click(); pg.wait_for_timeout(1000)
        c7b = pg.evaluate(CL)
        b5 = [x for x in c7b['bets'] if x['r'] == 5]
        check(len(b5) == 1 and b5[0]['state'] == 'reserved', f'⑦ 予約できる（締切済みレースの 記録が 予約に かわる：{b5}）')
        # ⑧ まもなく 締切の 架空の 画面（make_mock.py の e_soon：上に 時計「17:58」・2段の 札「まもなく／締切」・発走と 日付なし）を そのまま 読む（入力は 前の 日の 日付）
        E = json.load(open(os.path.join(OCR_DIR, 'e_soon.json'), encoding='utf-8'))['lines']
        pg.fill('#fDate', '2026-09-20'); pg.wait_for_timeout(400)
        pg.evaluate("window.__ocrLines = %s" % json.dumps([E], ensure_ascii=False))
        pg.set_input_files('#ocrFile', [os.path.join(OCR_DIR, 'e_soon.jpg')]); pg.wait_for_timeout(2600)
        c8 = pg.evaluate(CL)
        check(c8['r'] == '9' and c8['start'] == '' and open_ok(c8), f'⑧まもなく 締切の 架空の 画面（上に 時計・2段の 札）→ 締切済みに しない・時計（17:58）は 発走に しない（{c8["msg"][:60]}…）')
        check(not errs, f'画面の エラー なし（{errs[:2]}）')
        ctx.close(); b.close()
finally:
    srv.terminate()
    shutil.rmtree(SRV, ignore_errors=True)
print('FAILS', len(fails), fails)
