# 第4.241版の テスト（まさちゃん 2026/11/28 21:58）
#   「結果入力の時に、買い目を非表示な状態から表示して、隠れている買い目のところに、買い目を表示、オン、オフを選べるボタンをつけて！」→ 22:07「非表示な状態からスタートしてほしい！」
#   「一枚目の日付が翌日になってても、締め切り済みレースに登録されちゃうんだけど、改善できる？新しいバージョンで改善されているか確認して！」
#   App Store版（TARGET=app）を localhost で アプリ版として 開いて、画像を 読む（Vision の かわりに 読めた 文字と 位置を わたす：test_native.py の FAKE）。
#   ページの いまは 2026/11/28 21:55（日本）
#   ■ 締切済み（1枚目＝架空の 出馬表 i_card：見出し「2026年11月29日(日曜) 5回東京8日」・発走 9:55・上の 時計 21:55 ／ 2枚目＝架空の オッズの 画面）
#     ① あすの レース → 締切済みに しない・「買い目を予約」が 出る
#     ② オッズの 画面に「前日最終オッズ」→ 締切済みに しない（前の 版の 読み取りは「最終オッズ」で 締切済み：下の ⑩ で くらべる）
#     ③ オッズの 画面に「最終オッズ」でも、日付が あす → 締切済みに しない
#     ④ 前と 同じ：日付が きょう（11/28）・発走 9:55 → 締切済み（時刻）／日付が きょう・発走 22:30・「最終オッズ」→ 締切済み（言葉）
#     ⑤ 日付なし・発走 22:30：「前日発売は締め切りました」→ 締切済みに しない／「発売締切」→ 締切済み（言葉）
#   ■ 結果の 欄の 買い目（記録タブで 予約した レースを 開く）
#     ⑥ 買い目は 非表示から スタート・「買い目を表示 オン／オフ」（オフ）・前の「買い目を確認」の たたみは ない
#     ⑦ オン → 買い目が 出る（欄は 書き直さない：打った 着順は 消えない）→ オフ → かくれる → オン
#     ⑧ 行を 閉じて 開き直す → また 非表示から（この 端末には 覚えない）・オンで 結果を 決める → 金額の 欄でも オンの まま・ページを 開き直す → 非表示から
#     ⑨ 判定タブの「買い目を確認」（予約した ときの 確認）は 前の まま（たたみ）
#   ■ ⑩ 前の 版（git の 第4.240版）の 読み取りと くらべる（node）
#   python3 test_v241.py   （SHOT=フォルダ で 画面を 写す）
import json, os, re, shutil, subprocess, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv_v241'); PORT = 8876; APP = f'http://localhost:{PORT}/APP/'
SHOT = os.environ.get('SHOT')
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL,
               env=dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, HIST='hist_280.json', DROP='', TARGET='app'))
pth = os.path.join(SRV, 'APP', 'index.html'); html = open(pth, encoding='utf8').read()
assert "window.__NATIVE = location.protocol === 'tengel:';" in html
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
FAKE = re.search(r'\nFAKE = """(.*?)"""', open(os.path.join(W, 'test_native.py'), encoding='utf8').read(), re.S).group(1)      # アプリの 窓口の にせもの（画像の 読み取りは window.__ocrLines）
OCR_DIR = os.path.join(W, 'testdata', 'ocr'); JPG = os.path.join(OCR_DIR, 'i_card.jpg'), os.path.join(OCR_DIR, 'a_tanfuku_waku.jpg')
I = json.load(open(os.path.join(OCR_DIR, 'i_card.json'), encoding='utf-8'))['lines']
A = json.load(open(os.path.join(OCR_DIR, 'a_tanfuku_waku.json'), encoding='utf-8'))['lines']
KD = '2026年11月29日(日曜) 5回東京8日'
fails, errs = [], []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c:
        fails.append(label)


def shot(pg, name):
    if SHOT: os.makedirs(SHOT, exist_ok=True); pg.screenshot(path=os.path.join(SHOT, name + '.png'))


def icard(r=2, kd=KD, start='9:55'):
    """1枚目：架空の 出馬表（i_card）の 読めた 文字。R・見出し（日付）・発走を かえる"""
    out = []
    for ln in I:
        t = ln['text']
        if t == KD: t = kd
        elif t == '2R' and ln['y'] > 0.45: t = f'{r}R'
        elif t.startswith('コース 1400m'): t = f'コース 1400m ダート・左 発走{start}'
        out.append(dict(ln, text=t))
    assert sum(1 for x in out if x['text'] == kd) == 1 and sum(1 for x in out if x['text'] == f'{r}R') >= 1
    return out


def odds(extra=(), first=None, second='ダ1400m　12頭　馬場:稍重'):
    """2枚目：架空の オッズの 画面（A）。上の 2行（開催場と R・距離〜日付）を かえる（はじめは 日付も 発走も なし）・下に 言葉"""
    out = []
    for k, ln in enumerate(A):
        t = ln['text']
        if k == 0: t = first if first is not None else 'オッズ'
        elif k == 1: t = second
        out.append(dict(ln, text=t))
    for e in extra:
        out.append({'text': e, 'x': 0.08, 'y': 0.955, 'w': 0.6, 'h': 0.03})
    return out


CL = """() => { const q = s => document.querySelector(s), t = s => (q(s) || {}).innerText || ''; const f = JSON.parse(localStorage.getItem('tengel.form') || '{}');
  return { msg: t('#ocrMsg'), chips: [...document.querySelectorAll('#result .chip')].map(c => c.innerText), reserve: document.querySelectorAll('#recCard [data-rsv=reserve]').length,
    card: t('#recCard'), closed: f.closed || null, r: q('#fR').value, date: f.date, start: f.start || '', venue: f.venue || '' }; }"""
# いまを 2026/11/28 21:55（日本）＝ 12:55（UTC）に する
DATE_AT = """(() => { const D = Date, OFF = Date.UTC(2026, 10, 28, 12, 55, 0) - D.now();
  class FD extends D { constructor(...a) { if (a.length) super(...a); else super(D.now() + OFF); } static now() { return D.now() + OFF; } }
  FD.UTC = D.UTC; FD.parse = D.parse; window.Date = FD; })();"""
BOX = """(id) => { const f = document.querySelector(`#recList .lrow[data-id="${id}"] .rsvf`); if (!f) return null; const s = f.querySelector('[data-k=betsee]'), bl = s && s.querySelector('[data-k=betlist]');
  return { mode: f.dataset.mode, has: !!s, det: f.querySelectorAll('details[data-k=betsee]').length, head: s ? s.querySelector('.bsh').innerText.replace(/\\s+/g, ' ') : '',
    on: s ? [...s.querySelectorAll('[data-k=betshow] button')].map(b => [b.textContent, b.getAttribute('aria-pressed')]) : null,
    shown: !!bl && !bl.hidden && bl.getBoundingClientRect().height > 0, rows: bl ? bl.querySelectorAll('.betrow').length : 0, txt: bl ? bl.innerText : '',
    p1: (f.querySelector('[data-k=p1]') || {}).value, mark: !!(f.querySelector('[data-k=p1]') || {}).__v241, store: localStorage.getItem('tengel.betshow') }; }"""


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
    """買い目の 行が ない ときは、推奨ごとに 馬単（3着の ある 推奨は 3連単も）の 行を「＋券種」で 足す（test_v227.py と 同じ）"""
    card = pg.locator('#recCard')
    if card.locator('.rline').count() or not card.locator('[data-k=radd]').count(): return
    nz = pg.locator('#result ol.zones > li').count(); t3 = pg.locator('#result .zthird .zref').count() > 0
    for t in ['馬単'] * nz + (['3連単'] * nz if t3 else []):
        card.locator(f'[data-k=radd] button[data-v="{t}"]').click(); pg.wait_for_timeout(120)


try:
    print('■ ⑩ 前の 版（git：第4.240版）の 読み取りと くらべる')
    old = subprocess.run(['git', 'show', '79a3455b:./ocr_local.js'], capture_output=True, check=True).stdout      # 第4.240版の ソース
    OLD = os.path.join(SRV, 'ocr_old.js'); open(OLD, 'wb').write(old)
    NODE = """const O = require(process.argv[1]), N = require(process.argv[2]), L = JSON.parse(require('fs').readFileSync(0, 'utf8'));
      const f = M => L.map(ims => { const d = M.parse(ims); return { date: d.date, start: d.start, r: d.r, closed: d.closed }; });
      console.log(JSON.stringify({ old: f(O), new: f(N) }));"""
    cases = [[icard(), odds()], [icard(3), odds(['前日最終オッズ'])], [icard(4), odds(['最終オッズ'])], [odds(['前日発売は締め切りました'], '第7競走', 'ダ1400m　12頭　発走 22:30')]]
    cmp = json.loads(subprocess.run(['node', '-e', NODE, OLD, os.path.join(W, 'ocr_local.js')], input=json.dumps(cases, ensure_ascii=False), capture_output=True, text=True, check=True).stdout)
    print('   ', cmp)
    o, n = cmp['old'], cmp['new']
    check(all(x['date'] == '2026-11-29' and x['start'] == '09:55' for x in n[:3]) and [x['r'] for x in n[:3]] == [2, 3, 4] and n[0]['closed'] is None,
          f'⑩ あすの 出馬表（i_card）：日付 2026-11-29・発走 09:55・R は 前の 版も 今の 版も 読める（前 {[(x["date"], x["start"]) for x in o[:3]]}）')
    check(o[1]['closed'] == '最終オッズ' and n[1]['closed'] is None and o[3]['closed'] == '締め切りました' and n[3]['closed'] is None and n[2]['closed'] == '最終オッズ',
          f'⑩「前日最終オッズ」「前日発売は締め切りました」：前の 版は 締切の 言葉（{o[1]["closed"]}・{o[3]["closed"]}）→ 今の 版は 言葉に しない（{n[1]["closed"]}・{n[3]["closed"]}）・'
          f'「最終オッズ」だけ なら 今も 言葉（{n[2]["closed"]}：あすの 日付で 締切済みに しないのは src.html の closedOf）')
    src = open('src.html', encoding='utf8').read()
    check("if (d && /^\\d{4}-\\d{2}-\\d{2}$/.test(d.date || '') && d.date > today) return null;" in src and 'const betShowOn = id => !!id && st.betShow === id && st.open === id;' in src
          and '<span class="seg" data-k="betshow" role="group" aria-label="買い目を表示">' in src and "if (grp === 'betshow') { setBetShow(box.dataset.id, b.dataset.v === '1'); return; }" in src
          and "if (st.betShow && st.betShow !== st.open) st.betShow = null;" in src and 'tengel.betshow' not in src,
          '中身：closedOf（画像の 日付が あした 以降 → 締切済みに しない）・結果の 欄の 買い目（非表示から スタート・オンは その 行を 開いて いる あいだ だけ・この 端末には 覚えない）')

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
        check(pg.evaluate("() => new Date().toISOString()").startswith('2026-11-28T12:5'), 'ページの いまは 2026/11/28 21:55（日本）')
        g0 = pg.evaluate('TengelWallet.total()')
        check(pg.evaluate("TengelWallet.grant('test-v241-read', 4000, 'テストの 足し')") is True, f'テスト用に 4,000P 足す（7レース 読む ぶん：{g0} → {g0 + 4000}P）')

        def read(ims, wait=2600):
            pg.evaluate("(L) => { window.__ocrLines = L; }", ims)
            pg.set_input_files('#ocrFile', list(JPG[:len(ims)])); pg.wait_for_timeout(wait)
            return pg.evaluate(CL)

        def open_ok(c):
            return c['closed'] is None and '締切済み' not in c['chips'] and '締切済み' not in c['msg'] and c['reserve'] == 1

        print('■ ① あすの 出馬表（1枚目）＋ オッズ（2枚目）')
        c1 = read([icard(2), odds()])
        print('   ①', {k: c1[k] for k in ('closed', 'date', 'start', 'r', 'venue', 'reserve', 'chips')})
        check(c1['date'] == '2026-11-29' and c1['start'] == '09:55' and c1['r'] == '2' and open_ok(c1),
              f'① あすの レース（11/29 2R 発走 9:55・いまは 11/28 21:55）→ 締切済みに しない・「買い目を予約」が 出る')
        shot(pg, 'v241_1_tomorrow')
        # 予約 → 記録タブ（⑥〜⑨ で 使う）
        card = pg.locator('#recCard')
        rsv_lines(pg); card.locator('[data-rsv=reserve]').click(); pg.wait_for_timeout(900)
        rid = pg.evaluate("(() => { const b = [...TengelLocal.mem.bets.values()].find(x => x.rsv && x.rsv.state === 'reserved'); return b ? b.id : null; })()")
        check(bool(rid) and pg.locator('#recCard details[data-k=betsee]').count() == 1, f'① 予約できる（{rid}）・⑨ 判定タブの「買い目を確認」は 前の まま（たたみ）')

        print('■ ②〜⑤ 締切済みの 言葉と 時刻')
        c2 = read([icard(3), odds(['前日最終オッズ'])])
        check(c2['date'] == '2026-11-29' and c2['r'] == '3' and open_ok(c2), f'② 2枚目に「前日最終オッズ」→ 締切済みに しない（{c2["closed"]}）')
        c3 = read([icard(4), odds(['最終オッズ'])])
        check(c3['date'] == '2026-11-29' and c3['r'] == '4' and open_ok(c3), f'③ 2枚目に「最終オッズ」でも 日付が あす → 締切済みに しない（{c3["closed"]}）')
        c4 = read([icard(5, '2026年11月28日(土曜) 5回東京7日'), odds()])
        check(c4['date'] == '2026-11-28' and c4['r'] == '5' and bool(c4['closed']) and c4['closed'].get('by') == 'time' and c4['closed'].get('start') == '09:55' and c4['reserve'] == 0
              and '発走 09:55 を過ぎている' in c4['msg'], f'④ 日付が きょう（11/28）・発走 9:55 → 締切済み（時刻：前と 同じ）')
        c4b = read([icard(6, '2026年11月28日(土曜) 5回東京7日', '22:30'), odds(['最終オッズ'])])
        check(c4b['r'] == '6' and c4b['start'] == '22:30' and bool(c4b['closed']) and c4b['closed'].get('by') == 'kw' and c4b['closed'].get('word') == '最終オッズ' and c4b['reserve'] == 0,
              f'④ 日付が きょう・発走 22:30・「最終オッズ」→ 締切済み（言葉：前と 同じ）')
        c5 = read([odds(['前日発売は締め切りました'], '第7競走', 'ダ1400m　12頭　発走 22:30')])
        check(c5['r'] == '7' and c5['start'] == '22:30' and open_ok(c5), f'⑤ 日付なし・発走 22:30・「前日発売は締め切りました」→ 締切済みに しない（{c5["closed"]}）')
        c5b = read([odds(['発売締切'], '第8競走', 'ダ1400m　12頭　発走 22:30')])
        check(c5b['r'] == '8' and bool(c5b['closed']) and c5b['closed'].get('by') == 'kw' and c5b['closed'].get('word') == '発売締切', f'⑤ 日付なし・「発売締切」→ 締切済み（言葉：前と 同じ）')

        print('■ ⑥〜⑧ 結果の 欄の 買い目')
        OFF, ON = [['オン', 'false'], ['オフ', 'true']], [['オン', 'true'], ['オフ', 'false']]
        pg.click('.tabbar button[data-tab=rec]'); pg.wait_for_timeout(600)
        row = pg.locator(f'#recList .lrow[data-id="{rid}"]')
        row.locator('.lmain').click(); pg.wait_for_timeout(500)
        x1 = pg.evaluate(BOX, rid)
        check(x1 and x1['mode'] == 'result' and x1['has'] and x1['det'] == 0 and not x1['shown'] and x1['rows'] >= 1 and x1['on'] == OFF
              and x1['head'].startswith('買い目（') and '買い目を表示' in x1['head'],
              f'⑥ 結果の 欄：買い目は 非表示から スタート・「買い目を表示 オン／オフ」は オフ・「買い目を確認」の たたみは ない（{x1 and x1["head"]}）')
        shot(pg, 'v241_2_bets_off')
        row.locator('.rsvf [data-k=p1]').fill('6'); pg.evaluate("(id) => { document.querySelector(`#recList .lrow[data-id=\"${id}\"] .rsvf [data-k=p1]`).__v241 = 1; }", rid)
        row.locator('.rsvf [data-k=betshow] button[data-v="1"]').click(); pg.wait_for_timeout(250)
        x2 = pg.evaluate(BOX, rid)
        check(x2['on'] == ON and x2['shown'] and x2['p1'] == '6' and x2['mark'] and x2['store'] is None,
              f'⑦「オン」→ 買い目が 出る（{x2["rows"]}行）・打った 着順（{x2["p1"]}）は そのまま（欄を 書き直さない）・この 端末には 覚えない')
        shot(pg, 'v241_3_bets_on')
        row.locator('.rsvf [data-k=betshow] button[data-v="0"]').click(); pg.wait_for_timeout(250); x3 = pg.evaluate(BOX, rid)
        row.locator('.rsvf [data-k=betshow] button[data-v="1"]').click(); pg.wait_for_timeout(250); x4 = pg.evaluate(BOX, rid)
        check(x3['on'] == OFF and not x3['shown'] and x4['on'] == ON and x4['shown'] and x4['p1'] == '6', '⑦「オフ」→ かくれる →「オン」→ 出る')
        row.locator('.lmain').click(); pg.wait_for_timeout(400); row.locator('.lmain').click(); pg.wait_for_timeout(500)
        x5 = pg.evaluate(BOX, rid)
        check(x5['on'] == OFF and not x5['shown'], '⑧ 行を 閉じて 開き直す → また 非表示から スタート')
        # オンで 結果を 決める → 金額の 欄（書き直し）でも オンの まま
        row.locator('.rsvf [data-k=betshow] button[data-v="1"]').click(); pg.wait_for_timeout(200)
        f = row.locator('.rsvf')
        for k, v in (('p1', '6'), ('p2', '2'), ('p3', '10')): f.locator(f'[data-k={k}]').fill(v)
        f.locator('[data-k=p3]').dispatch_event('input'); pg.wait_for_timeout(250)
        f.locator('[data-act=rsave]').click(); pg.wait_for_timeout(900)
        pg.evaluate("window.TengelFx && TengelFx.close()"); pg.wait_for_timeout(400)
        x6 = pg.evaluate(BOX, rid)
        check(bool(x6) and x6['mode'] == 'amount' and x6['on'] == ON and x6['shown'],
              f'⑧ オンで「結果を決める」→ 金額の 欄（{x6 and x6["mode"]}）でも オンの まま（買い目が 出て いる）')
        pg.reload(); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(700)
        pg.click('.tabbar button[data-tab=rec]'); pg.wait_for_timeout(600)
        row = pg.locator(f'#recList .lrow[data-id="{rid}"]')
        if not row.locator('.rsvf').count(): row.locator('.lmain').click(); pg.wait_for_timeout(500)
        x7 = pg.evaluate(BOX, rid)
        check(x7 and x7['on'] == OFF and not x7['shown'], f'⑧ ページを 開き直す → 非表示から（{x7 and x7["mode"]}）')
        check(not errs, f'ページの エラー なし {errs[:3]}')
        b.close()
finally:
    srv.terminate(); shutil.rmtree(SRV, ignore_errors=True)
print('合計', len(fails), 'NG' if fails else 'OK')
raise SystemExit(1 if fails else 0)
