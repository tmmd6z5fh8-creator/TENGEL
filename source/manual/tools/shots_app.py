# 説明書（App Store版）の 画面の 写真を、いまの アプリの 画面で 撮る（第4.123版〜：テンゲルデータ・マザーデータ①〜③・予約から 記録まで）
#   python3 manual/tools/shots_app.py <作業フォルダ>   → <作業フォルダ>/man_app/raw（png・meta.json）
#   python3 manual/tools/conv.py <作業フォルダ> app    → <作業フォルダ>/man_app/img（webp）・man_app/dims.json・man_app/raw/meta2.json
#   → manual/img_app/・dims_app.json・meta_app.json に 入れる（MERGE=1 python3 manual/tools/shots_app.py --merge <作業フォルダ>）
#   架空の レースだけ（開催場の 名前は 出さない・アプリに 入っている データの 中身は 写さない）。マザーデータ①には 架空の レース 40走を 入れて 撮る
import json, os, random, re, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright

SRC = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MAN = os.path.join(SRC, 'manual')
if sys.argv[1] == '--merge':   # 撮った 写真を 説明書の フォルダへ（撮らなかった 写真は 前の まま）
    SP = sys.argv[2]; IMG = SP + '/man_app/img'
    dims = json.load(open(MAN + '/dims_app.json', encoding='utf-8')); meta = json.load(open(MAN + '/meta_app.json', encoding='utf-8'))
    nd = json.load(open(SP + '/man_app/dims.json', encoding='utf-8')); nm = json.load(open(SP + '/man_app/raw/meta2.json', encoding='utf-8'))
    for k, v in nd.items():
        shutil.copy(f'{IMG}/s_{k}.webp', f'{MAN}/img_app/s_{k}.webp'); dims[k] = v
        if k in nm: meta[k] = nm[k]
    json.dump(dims, open(MAN + '/dims_app.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(meta, open(MAN + '/meta_app.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('merged', sorted(nd)); sys.exit(0)
SP = sys.argv[1]
SRV = SP + '/mansrv_app'; PORT = int(os.environ.get('PORT', '8796')); BASE = f'http://localhost:{PORT}'
RAW = SP + '/man_app/raw'; shutil.rmtree(RAW, ignore_errors=True); os.makedirs(RAW)
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], cwd=SRC, check=True, stdout=subprocess.DEVNULL)


def build(out, **env):
    subprocess.run(['python3', 'build_pwa.py', out], cwd=SRC, check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, MANUAL_SHOTS_BOOTSTRAP='1', **env))


def as_app(d):
    pth = d + '/index.html'; h = open(pth, encoding='utf8').read()
    assert "window.__NATIVE = location.protocol === 'tengel:';" in h
    open(pth, 'w', encoding='utf8').write(h.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))


build(SRV + '/APP', TARGET='app', DATA_URL=f'{BASE}/remote/none.json'); as_app(SRV + '/APP')
# アップデートの 写真用：前の 版の データ（280走）の アプリと、新しい データ（「データの更新」で 読む）
build(SRV + '/OLDAPP', TARGET='app', HIST='hist_280.json', DROP='', MOTHER_VER='2026-10-07', DATA_URL=f'{BASE}/remote/mother_app.json'); as_app(SRV + '/OLDAPP')
build(SRV + '/_w', TARGET='web', MOTHER_VER='2026-10-20')
# 第4.155版：公開の ファイル（data/mother_app2.json）は AES-GCM で 封じて ある。写真用の にせものの アプリは 開けない ので、開いた 中身（ふつうの JSON：アプリは これも 読める）を 置く
sys.path.insert(0, SRC); import dataseal as _ds
os.makedirs(SRV + '/remote'); open(SRV + '/remote/mother_app.json', 'w', encoding='utf8').write(_ds.open_doc(open(SRV + '/_w/data/mother_app2.json', encoding='utf8').read(), _ds.load_key()))

# にせものの アプリ（test_native.py と 同じ。App Store の 版は 1.1 が 出ている ことに）
t = open(os.path.join(SRC, 'test_native.py'), encoding='utf8').read()
FAKE = re.search(r'^FAKE = """(.*?)"""', t, re.S | re.M).group(1)
FAKE = FAKE.replace("  if (m.name === 'backup') window.__saveBackup(P.text);",
                    "  if (m.name === 'backup') window.__saveBackup(P.text);\n  if (m.name === 'store') val = { found: true, version: '1.1', url: 'https://apps.apple.com/jp/app/id0000000000', notes: '', date: '', error: '' };")
assert "m.name === 'store'" in FAKE
OCR_DIR = os.path.join(SRC, 'testdata', 'ocr')
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(0.8)


def rows(nos, odds, fuku=None):
    fuku = fuku or [None] * len(nos)
    return [{"no": n, "tan": str(t), "fuku": (str(f) if f else "")} for n, t, f in zip(nos, odds, fuku)]


def form(r, dist, n, baba, nos, odds, fuku, s1, s1c, s5, s10, date='2026-11-14', start=''):
    return {"id": None, "venue": '', "date": date, "r": str(r), "dist": str(dist), "surface": "ダ", "baba": baba, "n": str(n), "tan1": "",
            "s1": str(s1), "s1combo": s1c, "s5": str(s5), "s5combo": "", "s10": str(s10), "s10combo": "", "rows": rows(nos, odds, fuku), "rname": "", "start": start}


# 9R：A層（比8.8）・10R：B層（比13.9）・11R：C層・第2段階（14頭）＝ shots.py と 同じ 架空の レース
F9 = form(9, 1400, 12, '良', [6, 2, 10, 7, 1, 4, 11, 5, 9, 3, 8, 12], [2.1, 3.4, 5.2, 7.8, 9.5, 12.4, 16.8, 22.5, 31.0, 45.6, 58.3, 82.1],
          [1.1, 1.3, 1.6, 2.0, 2.4, 2.9, 3.6, 4.5, 5.8, 7.9, 9.8, 13.5], 18.5, '6-2-10', 42.6, 78.9, start='18:05')
F11 = form(11, 1800, 14, '稍重', [5, 12, 3, 9, 1, 14, 7, 10, 2, 13, 6, 11, 4, 8], [3.6, 4.4, 5.9, 7.2, 9.0, 11.8, 14.6, 18.9, 24.1, 30.5, 41.2, 55.0, 73.8, 99.9], None, 95.2, '', 210.4, 355.0)


def w5odds(n, tan1):
    xs = [tan1] + [round(tan1 + 1.9 * i + 0.35 * i * i, 1) for i in range(1, n)]
    return [{"no": (i * 5) % n + 1, "tan": str(x), "fuku": ""} for i, x in enumerate(xs)]


V1, V2 = 'ひがし', 'にし'
RACES = [(V1, 9, 1600, 12, '良', 1.8, 12.0), (V2, 10, 1800, 14, '良', 2.0, 30.0), (V1, 10, 1400, 12, '稍重', 3.0, 70.0), (V2, 11, 2000, 16, '良', 3.2, 80.0), (V1, 11, 1600, 12, '良', 1.5, 9.0)]
W5 = {"id": None, "fixed": False, "date": "2026-11-15", "budget": "3000", "mode": "pick", "randAll": False, "stake": "", "payout": "", "other": "", "note": "",
      "races": [{"form": {"venue": v, "date": "2026-11-15", "r": str(r), "dist": str(d), "surface": "芝", "baba": b, "n": str(n), "rows": w5odds(n, t1), "tan1": "",
                          "s1": str(s1), "s1combo": "", "s5": "", "s5combo": "", "s10": "", "s10combo": ""}, "sel": None, "win": "", "picks": None, "man": None}
                for v, r, d, n, b, t1, s1 in RACES]}

# マザーデータ①に 入れる 架空の レース（40走・アプリに 入っている データとは 関係ない 数字）
rnd = random.Random(20261104)
MINE = []
for i in range(40):
    d = f'2026-09-{(i // 4) + 2:02d}' if i < 112 else '2026-09-30'
    r, n = i % 4 * 3 + 1 + (i // 4) % 3, rnd.choice([10, 11, 12, 12, 13, 14])
    tan1 = round(rnd.uniform(1.4, 4.6), 1); s1 = round(tan1 * rnd.uniform(5, 30), 1)
    ws = [max(1, n - k) ** 2.2 for k in range(n)]; picks = []
    while len(picks) < 3:
        x = rnd.choices(range(1, n + 1), weights=ws)[0]
        if x not in picks: picks.append(x)
    MINE.append({'id': d.replace('-', '') + f'-m2-{r:02d}', 'date': d, 'venue': '', 'r': r, 'baba': rnd.choice(['良', '良', '良', '稍重', '重']), 'dist': rnd.choice([1200, 1400, 1600, 1800]),
                 'surface': 'ダ', 'n': n, 'tan1': tan1, 's1': s1, 's5': round(s1 * 2.4, 1), 's10': round(s1 * 4.1, 1), 'p1': picks[0], 'p2': picks[1], 'p3': picks[2],
                 'umatanPay': None, 'sanrenPay': None, 'note': '', 'cnt': 1})

HIDE = ".tabbar,.minibar,#toast{display:none!important}.top{position:static!important}"
META, errs = {}, []
BOX_JS = """([root, sels]) => { const re = document.querySelector(root); if (!re) return null; const R = re.getBoundingClientRect(); const out = {};
 for (const s of sels) { const el = re.querySelector(s) || document.querySelector(s); if (!el) { out[s] = null; continue; }
   const b = el.getBoundingClientRect(); out[s] = { x: +(b.left - R.left).toFixed(1), y: +(b.top - R.top).toFixed(1), w: +b.width.toFixed(1), h: +b.height.toFixed(1) }; }
 return { W: +R.width.toFixed(1), H: +R.height.toFixed(1), b: out }; }"""


def hide(pg, on=True):
    pg.evaluate("([css, on]) => { let s = document.getElementById('shotcss'); if (on && !s) { s = document.createElement('style'); s.id = 'shotcss'; s.textContent = css; document.head.appendChild(s); } if (!on && s) s.remove(); }", [HIDE, on])


def shot(pg, name, root, sels=()):
    el = pg.locator(root).first
    el.scroll_into_view_if_needed(); pg.wait_for_timeout(250)
    META[name] = pg.evaluate(BOX_JS, [root, list(sels)])
    miss = [k for k, v in META[name]['b'].items() if v is None]
    el.screenshot(path=f'{RAW}/{name}.png', animations='disabled')
    print('  📸', name, META[name]['W'], 'x', META[name]['H'], ('（ない：' + '・'.join(miss) + '）') if miss else '')


def shot_top(pg, name, root, max_h, sels=()):
    info = pg.evaluate(BOX_JS, [root, list(sels)])
    top = pg.evaluate("(r) => { const b = document.querySelector(r).getBoundingClientRect(); return { x: b.left + scrollX, y: b.top + scrollY }; }", root)
    h = min(max_h, info['H'])
    pg.screenshot(path=f'{RAW}/{name}.png', full_page=True, clip={'x': top['x'], 'y': top['y'], 'width': info['W'], 'height': h}, animations='disabled')
    info['H'] = h; META[name] = info; print('  📸', name, info['W'], 'x', h)


def shot_pad(pg, name, root, sels=(), padx=12, pady=6):
    el = pg.locator(root).first
    el.scroll_into_view_if_needed(); pg.wait_for_timeout(250)
    info = pg.evaluate(BOX_JS, [root, list(sels)])
    bb = pg.evaluate("(r) => { const b = document.querySelector(r).getBoundingClientRect(); return { x: b.left + scrollX, y: b.top + scrollY, w: b.width, h: b.height }; }", root)
    pg.screenshot(path=f'{RAW}/{name}.png', full_page=True, clip={'x': bb['x'] - padx, 'y': bb['y'] - pady, 'width': bb['w'] + 2 * padx, 'height': bb['h'] + 2 * pady}, animations='disabled')
    for v in info['b'].values():
        if v: v['x'] += padx; v['y'] += pady
    info['W'] = round(info['W'] + 2 * padx, 1); info['H'] = round(info['H'] + 2 * pady, 1)
    META[name] = info; print('  📸', name, info['W'], 'x', info['H'])


def tab(pg, name):
    # App Store版の テンキー（numpad.js）が 開いて いると 下の タブを ふさぐ → とじてから
    pg.evaluate("() => { try { document.activeElement && document.activeElement.blur && document.activeElement.blur(); window.TengelNumpad && TengelNumpad.hide(); } catch (e) {} }"); pg.wait_for_timeout(150)
    hide(pg, False); pg.click(f'.tabbar button[data-tab={name}]'); pg.wait_for_timeout(800); hide(pg, True)


def gate(pg):
    g = pg.locator('#gate')
    for _ in range(40):
        if not g.count() or g.evaluate('e => e.hidden'): return
        if pg.locator('#gateGo').count():
            if not g.evaluate("e => e.classList.contains('fade')"):
                try: pg.locator('#gateGo').click(timeout=3000)
                except Exception: pass
        else:
            try: g.click(timeout=500)
            except Exception: pass
        pg.wait_for_timeout(150)


def load_form(pg, f):
    pg.evaluate("(f) => localStorage.setItem('tengel.form', f)", json.dumps(f, ensure_ascii=False))
    pg.reload(); pg.wait_for_timeout(1800); gate(pg); pg.wait_for_timeout(600); hide(pg, True)


def new_ctx(b):
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, color_scheme='light', locale='ja-JP', timezone_id='Asia/Tokyo')
    mk = {}

    def marker(source, q):
        op, key = q.get('op'), q.get('key')
        if op == 'set': mk[key] = q.get('value', '1'); return {'ok': True}
        if op == 'del': mk.pop(key, None); return {'ok': True}
        v = mk.get(key); return {'ok': True, 'has': v is not None, 'value': v}
    ctx.expose_binding('__saveBackup', lambda s, t: None); ctx.expose_binding('__marker', marker)
    ctx.add_init_script(FAKE)
    ctx.route('**/__native/autobackup.json', lambda route: route.fulfill(status=404, body='not found'))
    return ctx


try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = new_ctx(b)
        pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.add_init_script("if (!sessionStorage.getItem('x')) { sessionStorage.setItem('x', '1'); localStorage.setItem('tengel.form', %s); localStorage.setItem('tengel.win5', %s); }"
                           % (json.dumps(json.dumps(F9, ensure_ascii=False)), json.dumps(json.dumps(W5, ensure_ascii=False))))
        pg.goto(BASE + '/APP/'); pg.wait_for_timeout(1800); gate(pg); pg.wait_for_timeout(800)
        pg.evaluate("TengelFx.set({ effects: false })")
        pg.evaluate("(rows) => TengelLocal.slots.replace(2, rows, { source: 'excel', file: 'マイデータ.xlsx' })", MINE); pg.wait_for_timeout(600)
        pg.evaluate("scrollTo(0, 0)"); pg.wait_for_timeout(300)
        pg.screenshot(path=f'{RAW}/bottom_bars.png', clip={'x': 0, 'y': 844 - 150, 'width': 390, 'height': 150}); META['bottom_bars'] = {'W': 390, 'H': 150, 'b': {}}
        shot(pg, 'tabbar', '.tabbar')
        hide(pg, True)
        # ---- 判定タブ：入力欄・判定（A層） ----
        shot(pg, 'judge_info', '.input-col > .card:nth-child(1)', ['#slotJudge', '#ocrRow', '#fVenue', '#fDate', '#fR', '#fDist', '#fN', '#fSurf', '#fBaba'])
        shot(pg, 'judge_odds', '.input-col > .card:nth-child(2)', ['.oheads', '#oddsGrid', '#addRow'])
        shot(pg, 'judge_tri', '.input-col > .card:nth-child(3)', ['#fS1', '#fS1c', '#fS5', '#fS10', '#clearBtn', '#sampleBtn'])
        shot(pg, 'result_a', '#result', ['.vhead .lbadge', '.vhead .vkubun', '.vhead .vratio', '.vhead .chips', '.hpnote', 'ol.zones > li:nth-child(1) .zflow', 'ol.zones > li:nth-child(1) .znums', 'ol.zones > li:nth-child(1) .zref',
                                         'ol.zones > li:nth-child(1) .zthird', 'ol.zones > li:nth-child(2)', '.numbers', '.vfoot', '.oldline', '.w5push', '#copyAll', '.rankbox'])
        # ---- 予約 → 記録タブで 結果 → 金額の 欄の「マザーデータにも入れる」（テンゲルデータで 判定した ので「マザーデータ①に記録する？」）----
        pg.locator('#recCard [data-rsv=reserve]').click(); pg.wait_for_timeout(1200)
        bid = pg.evaluate("[...TengelLocal.mem.bets.values()].find(x => x.rsv && x.rsv.state === 'reserved').id")
        tab(pg, 'rec')
        pg.locator(f'#recList .lrow[data-id="{bid}"] .lmain').click(); pg.wait_for_timeout(500)
        f = pg.locator('#recList .rsvf')
        for k, v in (('p1', '6'), ('p2', '7'), ('p3', '2')): f.locator(f'[data-k={k}]').fill(v)
        f.locator('[data-k=p3]').dispatch_event('input'); pg.wait_for_timeout(300)
        f.locator('[data-act=rsave]').click(); pg.wait_for_timeout(1500)
        if pg.locator('#fxOv').count(): pg.evaluate("TengelFx.close()"); pg.wait_for_timeout(500)
        f = pg.locator('#recList .rsvf')
        f.locator('[data-k=payout][data-t="馬単"]').fill('2280'); f.locator('[data-k=payout][data-t="馬単"]').dispatch_event('input'); pg.wait_for_timeout(200)
        if f.locator('[data-k=payout][data-t="3連単"]').count():   # 3連単も 当たり（6→7→2）：回収額を 入れて おく（実測・回収の 写真が 「的中なのに 回収 0」に ならない ように）
            f.locator('[data-k=payout][data-t="3連単"]').fill('4350'); f.locator('[data-k=payout][data-t="3連単"]').dispatch_event('input')
        pg.wait_for_timeout(300)
        shot(pg, 'md_record', '#recList .rsvf [data-k=mfld]')
        f.locator('[data-mpick="2"]').click(); pg.wait_for_timeout(300)
        f.locator('[data-act=rsave]').click(); pg.wait_for_timeout(1200)
        # ---- C層・第2段階 ----
        tab(pg, 'judge'); load_form(pg, F11)
        shot(pg, 'result_c', '#result', ['.vhead .lbadge', '.vhead .chips', 'ol.zones', '.numbers', '.vfoot'])
        # ---- オッズ画像（端末の 中の 文字認識の かわりに、架空の オッズ画面の 文字を 返す） ----
        pg.evaluate("scrollTo(0, 0)")
        # 架空の 開催場（ひがし）・まだ 締め切って いない 日（11/14）に して 読ませる（開催場の 名前と「締切済み」を 写さない）
        ocr = json.dumps([json.load(open(os.path.join(OCR_DIR, k + '.json'), encoding='utf-8'))['lines'] for k in ('a_tanfuku_waku', 'c_sanrentan')], ensure_ascii=False)
        for a_, b_ in (('大井競馬場', 'ひがし競馬場'), ('大井競馬', 'ひがし競馬'), ('10月14日(水)', '11月14日(土)')):
            assert a_ in ocr, a_
            ocr = ocr.replace(a_, b_)
        assert '大井' not in ocr
        pg.evaluate("window.__ocrLines = %s" % ocr)
        pg.set_input_files('#ocrFile', [os.path.join(OCR_DIR, 'a_tanfuku_waku.jpg'), os.path.join(OCR_DIR, 'c_sanrentan.jpg')]); pg.wait_for_timeout(2500)
        pg.evaluate("scrollTo(0, 0)"); pg.wait_for_timeout(200)
        shot(pg, 'ocr_done', '.input-col > .card:nth-child(1)', ['#ocrRow', '#ocrMsg'])
        load_form(pg, F9)
        # ---- 実測・回収（テンゲルデータの ときは 実測を 出さない → マザーデータ①で 撮る） ----
        tab(pg, 'stats')
        shot(pg, 'stats_money', '#moneyBody .money-tiles')
        shot(pg, 'stats_type', '#moneyBody .stat-grid > .card:nth-child(2)')
        pg.evaluate("TengelLocal.slots.setActive(2)"); pg.wait_for_timeout(1200); tab(pg, 'judge'); tab(pg, 'stats')
        shot(pg, 'stats_period', '#perChips')
        shot(pg, 'stats_t1', '#statsBody .card:first-child')
        pg.evaluate("TengelLocal.slots.setActive(1)"); pg.wait_for_timeout(1000)
        # ---- 単勝5連勝 ----
        tab(pg, 'win5')
        shot(pg, 'w5_top', '.w5top', ['details.full', '#w5Date', '#w5Budget', '#w5Mode', '#w5Sum'])
        shot(pg, 'w5_race', '#w5Races .w5race[data-i="0"]', ['.w5h', '.w5zones', '.w5picks', '.zref', '[data-w5act=edit]', '[data-w5act=clear]'])
        picks = [[x.inner_text() for x in pg.locator(f'#w5Races .w5race[data-i="{i}"] .w5picks .num:not(.off)').all()] for i in range(5)]
        if all(picks):
            for i in range(5):
                win = picks[i][0] if i != 2 else str(max(int(x) for x in [h['no'] for h in W5['races'][2]['form']['rows']] if str(x) not in picks[2]))
                pg.locator(f'#w5Win{i}').fill(win); pg.wait_for_timeout(120)
            pg.locator('#w5Pay').fill('0'); pg.wait_for_timeout(400)
            shot(pg, 'w5_res', '#w5ResCard', ['.w5res', '#w5Status', '#w5Stake', '#w5Pay', '#w5Other', '[data-w5act=save]'])
        else:
            print('  ※ 単勝5連勝の 買う馬が 出ない', picks)
        # ---- 設定 ----
        tab(pg, 'set')
        shot_top(pg, 'set_zone', '#zoneCard', 640, ['.zk-tabs', '.zk-head', 'ol.zedit > li:nth-child(1)', '.zr-line', '.zr-stat'])
        shot(pg, 'set_zone_save', '#zoneCard .zsave')
        shot(pg, 'set_mother', '#setMother', ['#slotList', '#slotEdit', '#slotEdit .mdtools'])
        shot(pg, 'set_backup', '#setBackup', ['#pwaBackup', '#pwaRestore'])
        # ---- マザーデータ①の 中身：ボタン・書き出す・ファイルから足す・一覧・1つ入れる ----
        shot(pg, 'md_tools', '#slotEdit .mdtools', ['#mdOpenBtn', '#mdAddBtn', '#mdExpBtn'])
        pg.locator('#mdExpBtn').click(); pg.wait_for_timeout(400)
        shot_pad(pg, 'md_export', '#mdExport')
        pg.locator('#mdExpBtn').click(); pg.wait_for_timeout(200)
        csvp = RAW + '/追加分.csv'
        open(csvp, 'w', encoding='utf-8-sig').write('\r\n'.join(','.join(r) for r in [
            ['日付', 'R', '馬場', '距離', '頭数', '単勝1位', '3連単1位', '1着人気', '2着人気', '3着人気', '3連単5位', '3連単10位', '馬単払戻', '3連単払戻', '備考', '集計対象'],
            ['2026/10/15', '1', '良', '1200', '11', '1.9', '15.2', '1', '3', '2', '', '', '560', '2240', '', '1'],
            ['2026/10/15', '2', '良', '1400', '12', '2.6', '33.8', '2', '1', '5', '', '', '840', '5670', '', '1']]) + '\r\n')
        pg.set_input_files('#smFile', csvp); pg.wait_for_timeout(1000)
        shot_pad(pg, 'md_merge', '#smPreview')
        pg.locator('#smCancel').click(); pg.wait_for_timeout(200); os.remove(csvp)
        pg.locator('#mdOpenBtn').click(); pg.wait_for_timeout(800)
        info = pg.evaluate(BOX_JS, ['#mdSheet .mdbox', ['#mdYM', '#mdNew', '.mdrow']])
        bb = pg.locator('#mdSheet .mdbox').bounding_box(); hh = min(740, info['H'])
        pg.screenshot(path=f'{RAW}/md_list.png', clip={'x': bb['x'], 'y': bb['y'], 'width': bb['width'], 'height': hh}, animations='disabled')
        info['H'] = hh; META['md_list'] = info; print('  📸 md_list', info['W'], 'x', hh)
        pg.locator('#mdNew').click(); pg.wait_for_timeout(300)
        nf = pg.locator('#mdNewBox .mdform')
        nf.locator('[data-k=date]').fill('2026-10-14'); nf.locator('[data-k=r]').select_option('12'); nf.locator('[data-k=baba] button[data-v="良"]').click()
        nf.locator('[data-k=dist]').fill('1200'); nf.locator('[data-k=n]').fill('12'); nf.locator('[data-k=tan1]').fill('2.1'); nf.locator('[data-k=s1]').fill('20.0')
        nf.locator('[data-k=res]').press_sequentially('1.4.2', delay=20); nf.locator('[data-k=umatanPay]').fill('780'); nf.locator('[data-k=sanrenPay]').fill('2150')
        pg.locator('#mdSheet .mdhead h3').click(); pg.wait_for_timeout(300)
        pg.set_viewport_size({'width': 390, 'height': 1500}); pg.wait_for_timeout(500)
        shot(pg, 'md_form', '#mdNewBox .mdnew', ['[data-k=date]', '[data-k=dist]', '[data-k=res]', '[data-k=umatanPay]', '[data-k=cnt]', '[data-k=pv]'])
        pg.set_viewport_size({'width': 390, 'height': 844}); pg.wait_for_timeout(300)
        nf.locator('[data-md=cancel]').click(); pg.wait_for_timeout(200)
        pg.locator('#mdSheet .mdx').click(); pg.wait_for_timeout(300)
        # ---- まとめて入力（カード・第4.124版）：2レース 下書きに 足して、3レース目を 入れて いる ところ ----
        pg.evaluate("() => { try { localStorage.removeItem('tengel.bulk'); } catch (e) {} }")
        calm = lambda: pg.evaluate("() => { try { document.activeElement && document.activeElement.blur && document.activeElement.blur(); window.TengelNumpad && TengelNumpad.hide(); } catch (e) {} }")
        pg.locator('#mdBulkBtn').click(); pg.wait_for_timeout(500)

        def bkcard(r, dist, n, tan1, s1, res, first=False):
            fm = pg.locator('#bkBody .mdform')
            if first:
                fm.locator('[data-k=date]').fill('2026-10-18'); fm.locator('[data-k=baba] button[data-v="良"]').click()
            fm.locator('[data-k=r]').select_option(str(r))
            for k, v in (('dist', dist), ('n', n), ('tan1', tan1), ('s1', s1), ('res', res)): fm.locator(f'[data-k={k}]').fill(v)
            fm.locator('[data-k=res]').dispatch_event('input'); pg.wait_for_timeout(150); calm()
        bkcard(1, '1200', '11', '1.9', '15.2', '1.3.2', True); pg.locator('#bkBody [data-bk=add]').click(); pg.wait_for_timeout(400)
        bkcard(2, '1400', '12', '2.6', '33.8', '2.1.5'); pg.locator('#bkBody [data-bk=add]').click(); pg.wait_for_timeout(400)
        bkcard(3, '1600', '14', '3.1', '61.0', '1.7.2'); calm(); pg.wait_for_timeout(300)
        pg.set_viewport_size({'width': 390, 'height': 1600}); pg.wait_for_timeout(400); calm()
        hh = pg.evaluate("() => { const q = s => document.querySelector(s), b = q('#bkBody'); const c = b.lastElementChild.getBoundingClientRect().bottom - b.getBoundingClientRect().top + 18; return Math.ceil(q('#bkSheet .mdhead').offsetHeight + c + q('#bkFoot').offsetHeight + 12); }")
        pg.set_viewport_size({'width': 390, 'height': min(1600, hh)}); pg.wait_for_timeout(400); calm()
        info = pg.evaluate(BOX_JS, ['#bkSheet .mdbox', ['.bkcard h4', '.bkcard [data-k=baba]', '.bkcard [data-k=res]', '[data-bk=add]', '.bklist', '#bkFoot [data-bk=apply]']])
        bb = pg.locator('#bkSheet .mdbox').bounding_box()
        pg.screenshot(path=f'{RAW}/md_bulk.png', clip={'x': bb['x'], 'y': bb['y'], 'width': bb['width'], 'height': bb['height']}, animations='disabled')
        META['md_bulk'] = info; print('  📸 md_bulk', info['W'], 'x', info['H'])
        pg.set_viewport_size({'width': 390, 'height': 844}); pg.wait_for_timeout(300)
        pg.locator('#bkSheet .mdx').click(); pg.wait_for_timeout(300)
        pg.evaluate("() => { try { localStorage.removeItem('tengel.bulk'); } catch (e) {} }")
        ctx.close()
        # ---- アップデート：App Storeに 新しい版（1.1）・新しい データが ある とき ----
        ctx2 = new_ctx(b)
        p2 = ctx2.new_page(); p2.on('pageerror', lambda e: errs.append('UPD ' + str(e)))
        p2.add_init_script("if (!sessionStorage.getItem('x')) { sessionStorage.setItem('x', '1'); localStorage.setItem('tengel.form', %s); }" % json.dumps(json.dumps(F9, ensure_ascii=False)))
        p2.goto(BASE + '/OLDAPP/'); p2.wait_for_timeout(1800); gate(p2); p2.wait_for_timeout(4200); hide(p2, True)
        p2.evaluate("scrollTo(0, 0)")
        shot(p2, 'upd_bars', 'header.top')
        for k in ('app', 'data'):
            if p2.locator(f'#nBar_{k} .nbx').count(): p2.locator(f'#nBar_{k} .nbx').click()
        tab(p2, 'set')
        p2.locator('#nuCheck').click(); p2.locator('#sdCheck').click(); p2.wait_for_timeout(1000)
        shot(p2, 'upd_app', '#setUpdate', ['dl.kvs dd', '#nuStore', '#nuCheck', '#nuOpen'])
        shot(p2, 'upd_data', '#setData', ['#sdCur', '#sdCheck', '#sdApply'])
        ctx2.close()
        b.close()
finally:
    srv.terminate()
json.dump(META, open(f'{RAW}/meta.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('errors:', errs[:5])
