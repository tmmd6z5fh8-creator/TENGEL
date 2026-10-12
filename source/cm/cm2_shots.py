# CM第2弾用：アプリの画面を撮る（架空のレース・架空のJRAデータ。このテスト用ブラウザの中だけ）
#  追加：買い目編集（タップ前後）・カスタム買い目の判定・マザーデータ（JRAに入れる流れ）・JRAデータでの判定・収支
#   python3 cm2_shots.py              … Web版の画面 → shots/
#   TARGET=app python3 cm2_shots.py   … App Store版の画面（アプリの中として開く・競馬場や団体・版の名前が出ない）→ shots_app/
import json, os, random, shutil, subprocess, time
from playwright.sync_api import sync_playwright
SRC = '/home/claude/tengel/source'
APP = os.environ.get('TARGET') == 'app'
CM = os.path.dirname(os.path.abspath(__file__)); OUT = CM + ('/shots_app' if APP else '/shots'); os.makedirs(OUT, exist_ok=True)
SRV = CM + '/srv'; PORT = 8799; URL = f'http://localhost:{PORT}/TENGEL/'
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], cwd=SRC, check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', SRV + '/TENGEL'], cwd=SRC, check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, TARGET='app') if APP else None)
if APP:   # アプリの中（tengel://）のかわりに、localhost でアプリ版として開く
    pth = SRV + '/TENGEL/index.html'; h = open(pth, encoding='utf8').read()
    assert "window.__NATIVE = location.protocol === 'tengel:';" in h
    open(pth, 'w', encoding='utf8').write(h.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
FAKE = """
window.__NATIVE_INFO = { version: '1.0', build: '1', device: 'phone' };
window.webkit = { messageHandlers: { tengel: { postMessage: function (m) { setTimeout(function () { window.__nativeReply(m.id, true, true); }, 30); } } } };
"""
# App Store版：開催場は空（空なら、使っているマザーデータの開催場として判定）・5重勝は架空の開催場
V0 = '' if APP else '大井'
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--bind', '127.0.0.1', '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(0.8)


def rows(nos, odds, fuku=None):
    fuku = fuku or [None] * len(nos)
    return [{"no": n, "tan": str(t), "fuku": (str(f) if f else "")} for n, t, f in zip(nos, odds, fuku)]


def form(r, dist, n, baba, nos, odds, fuku, s1, s1c, s5, s10, venue=V0, date='2026-10-14', surface='ダ'):
    return {"id": None, "venue": venue, "date": date, "r": str(r), "dist": str(dist), "surface": surface, "baba": baba, "n": str(n), "tan1": "",
            "s1": str(s1), "s1combo": s1c, "s5": str(s5), "s5combo": "", "s10": str(s10), "s10combo": "", "rows": rows(nos, odds, fuku)}


F9 = form(9, 1400, 12, '良', [6, 2, 10, 7, 1, 4, 11, 5, 9, 3, 8, 12], [2.1, 3.4, 5.2, 7.8, 9.5, 12.4, 16.8, 22.5, 31.0, 45.6, 58.3, 82.1],
          [1.1, 1.3, 1.6, 2.0, 2.4, 2.9, 3.6, 4.5, 5.8, 7.9, 9.8, 13.5], 18.5, '6-2-10', 42.6, 78.9)
F10 = form(10, 1600, 12, '良', [3, 8, 1, 11, 5, 2, 12, 7, 4, 9, 6, 10], [2.8, 3.6, 4.9, 6.7, 8.8, 11.5, 15.2, 19.8, 26.4, 38.0, 52.5, 70.3], None, 39.0, '', 88.0, 140.5)
F11 = form(11, 1800, 14, '稍重', [5, 12, 3, 9, 1, 14, 7, 10, 2, 13, 6, 11, 4, 8], [3.6, 4.4, 5.9, 7.2, 9.0, 11.8, 14.6, 18.9, 24.1, 30.5, 41.2, 55.0, 73.8, 99.9], None, 95.2, '', 210.4, 355.0)
# 架空のJRAのレース（東京11R・芝1600・16頭・A層）
FJ = form(11, 1600, 16, '良', [7, 3, 12, 1, 9, 15, 5, 10, 2, 14, 6, 11, 4, 16, 8, 13],
          [2.3, 4.1, 5.6, 7.9, 9.8, 12.5, 15.1, 19.7, 24.3, 31.2, 38.5, 47.0, 58.2, 72.4, 95.1, 130.6],
          [1.2, 1.5, 1.8, 2.3, 2.7, 3.2, 3.9, 4.6, 5.5, 6.8, 8.1, 9.9, 12.2, 14.8, 18.5, 24.0], 19.6, '7-3-12', 48.2, 96.5, venue='' if APP else '東京', date='2026-10-17', surface='芝')
BLANK = {"id": None, "venue": V0, "date": "2026-10-14", "r": "", "dist": "", "surface": "ダ", "baba": "", "n": "", "tan1": "", "s1": "", "s1combo": "", "s5": "", "s5combo": "", "s10": "", "s10combo": "", "rows": []}


def w5odds(n, tan1):
    xs = [tan1] + [round(tan1 + 1.9 * i + 0.35 * i * i, 1) for i in range(1, n)]
    return [{"no": (i * 5) % n + 1, "tan": str(x), "fuku": ""} for i, x in enumerate(xs)]


V1, V2 = ('ひがし', 'にし') if APP else ('東京', '京都')
RACES = [(V1, 9, 1600, 12, '良', 1.8, 12.0), (V2, 10, 1800, 14, '良', 2.0, 30.0), (V1, 10, 1400, 12, '稍重', 3.0, 70.0), (V2, 11, 2000, 16, '良', 3.2, 80.0), (V1, 11, 1600, 12, '良', 1.5, 9.0)]
W5 = {"id": None, "fixed": False, "date": "2026-10-18", "budget": "3000", "mode": "pick", "randAll": False, "stake": "", "payout": "", "other": "", "note": "",
      "races": [{"form": {"venue": v, "date": "2026-10-18", "r": str(r), "dist": str(d), "surface": "芝", "baba": b, "n": str(n), "rows": w5odds(n, t1), "tan1": "", "s1": str(s1), "s1combo": "", "s5": "", "s5combo": "", "s10": "", "s10combo": ""},
                 "sel": None, "win": "", "picks": None, "man": None} for v, r, d, n, b, t1, s1 in RACES]}


# 架空のJRAデータ（検証データと同じA〜P列・タブ区切り）：4/4〜10/11の土日、180走
def jra_tsv(nrace=180, seed=7):
    rnd = random.Random(seed)
    import datetime as dt
    days, d = [], dt.date(2026, 4, 4)
    while d <= dt.date(2026, 10, 11):
        if d.weekday() in (5, 6):
            days.append(d)
        d += dt.timedelta(days=1)
    per = [nrace // len(days)] * len(days)
    for i in rnd.sample(range(len(days)), nrace - sum(per)):
        per[i] += 1
    W = [32, 19, 13, 9, 7, 5, 4, 3, 2.5, 2, 1.5, 1.2, 1, .8, .6, .5, .4, .3]
    out = []
    for day, k in zip(days, per):
        for r in sorted(rnd.sample(range(1, 13), k)):
            n = rnd.randint(10, 18)
            baba = rnd.choices(['良', '稍重', '重', '不良'], [75, 15, 7, 3])[0]
            dist = rnd.choice([1200, 1400, 1600, 1800, 2000, 2400])
            tan1 = round(rnd.uniform(1.4, 4.6), 1)
            s1 = round(tan1 * rnd.lognormvariate(2.2, 0.45), 1)
            ps = []
            while len(ps) < 3:
                p = rnd.choices(range(1, n + 1), W[:n])[0]
                if p not in ps:
                    ps.append(p)
            s5 = round(s1 * rnd.uniform(1.8, 2.6), 1); s10 = round(s5 * rnd.uniform(1.4, 1.9), 1)
            uma = int(round((180 + 95 * ps[0] * ps[1] * rnd.uniform(0.6, 1.6)) / 10) * 10)
            san = int(round((900 + 260 * ps[0] * ps[1] * ps[2] * rnd.uniform(0.6, 1.6)) / 10) * 10)
            out.append('\t'.join(map(str, [day.strftime('%Y/%m/%d'), r, baba, dist, n, tan1, s1, ps[0], ps[1], ps[2], s5, s10, uma, san, '', 1])))
    return '\n'.join(out)


HIDE = ".tabbar,.minibar,#toast{display:none!important}.top{display:none!important}main{padding-bottom:0!important}.zsave.sticky{position:static!important;box-shadow:none!important}"
META = {}
BOX_JS = """([root, sels]) => { const re = document.querySelector(root); const R = re.getBoundingClientRect(); const out = {};
 for (const s of sels) { const el = document.querySelector(s); if (!el) { out[s] = null; continue; } const b = el.getBoundingClientRect();
   out[s] = { x: +(b.left - R.left).toFixed(1), y: +(b.top - R.top).toFixed(1), w: +b.width.toFixed(1), h: +b.height.toFixed(1) }; }
 return { W: +R.width.toFixed(1), H: +R.height.toFixed(1), b: out }; }"""


# CMでは「大井」「第13改訂版」などの文字を出さない（画面の文字だけ置きかえる。アプリの中身は変えない）
SCRUB_JS = r"""() => {
  const R = [[/大井 第13改訂版・カスタム|第13改訂版・カスタム/g, 'カスタム'], [/大井 第13改訂版/g, ''], [/第13改訂版の初期/g, '初期設定'], [/（第13改訂版）/g, ''], [/第13改訂版/g, ''],
    [/基盤データ（大井）/g, '基盤データ'], [/アプリに入っていた大井データ/g, 'アプリに入っていたデータ'], [/アプリに入っている大井データ/g, 'アプリに入っているデータ'],
    [/大井の姫フィルター（Excel）/g, 'Excel'], [/大井の検証データ/g, '検証データ'], [/大井競馬/g, '基本データ'], [/大井 /g, ''], [/大井/g, ''], [/改訂版/g, '']];
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT), nodes = [];
  while (w.nextNode()) nodes.push(w.currentNode);
  for (const n of nodes) { let t = n.nodeValue; if (!/大井|改訂版/.test(t)) continue; for (const [re, to] of R) t = t.replace(re, to); n.nodeValue = t; }
  for (const el of document.querySelectorAll('input, textarea')) {
    if (/大井/.test(el.value)) el.value = el.value.replace(/大井競馬/g, '基本データ').replace(/大井/g, '');
    if (/大井/.test(el.placeholder || '')) el.placeholder = '';
  }
  const v = document.querySelector('.brand .ver'); if (v) v.style.display = v.textContent.trim() ? '' : 'none';
  const left = [...document.querySelectorAll('body *')].filter(e => e.children.length === 0 && /大井|改訂版/.test(e.textContent)).length;
  return left;
}"""


def scrub(pg):
    left = pg.evaluate(SCRUB_JS)
    if left:
        print('  ⚠️ まだ残っている文字', left)


def hide(pg, on):
    pg.evaluate("([css, on]) => { let s = document.getElementById('cmcss'); if (on && !s) { s = document.createElement('style'); s.id = 'cmcss'; s.textContent = css; document.head.appendChild(s); } if (!on && s) s.remove(); }", [HIDE, on])


def content(pg, name, sels=()):
    hide(pg, True); pg.evaluate("scrollTo(0,0)"); pg.wait_for_timeout(300)
    scrub(pg); pg.wait_for_timeout(100)
    META[name] = pg.evaluate(BOX_JS, ['main', list(sels)])
    pg.locator('main').screenshot(path=f'{OUT}/{name}.png', animations='disabled')
    hide(pg, False); pg.wait_for_timeout(150)
    miss = [k for k, v in META[name]['b'].items() if v is None]
    print('  📸', name, META[name]['W'], 'x', META[name]['H'], ('（見つからない：' + ', '.join(miss) + '）') if miss else '')


def bar_shot(pg, sel, name):
    hide(pg, False); pg.evaluate("scrollTo(0,0)"); pg.wait_for_timeout(250)
    scrub(pg); pg.wait_for_timeout(100)
    pg.locator(sel).screenshot(path=f'{OUT}/{name}.png', animations='disabled')
    key = 'header' if sel == 'header.top' else 'tabbar'
    META[key] = pg.evaluate("(s) => { const b = document.querySelector(s).getBoundingClientRect(); return { W: b.width, H: b.height }; }", sel)


def tab(pg, name):
    hide(pg, False); pg.click(f'.tabbar button[data-tab={name}]'); pg.wait_for_timeout(900)


def load_form(pg, f):
    pg.evaluate("(f) => localStorage.setItem('tengel.form', f)", json.dumps(f, ensure_ascii=False))
    pg.reload(); pg.wait_for_timeout(2400)


def record(pg, buy, res, stake, pay):
    card = pg.locator('#recCard')
    card.locator('[data-k=stake][data-t="馬単"]').fill(stake)
    card.locator('[data-k=buyz] button').nth(buy).click(); pg.wait_for_timeout(200)
    card.locator('[data-k=mode] button[data-v=nin]').click(); pg.wait_for_timeout(200)
    r = card.locator('[data-k=res]'); r.fill(''); r.press_sequentially(res, delay=20); pg.wait_for_timeout(300)
    card.locator('[data-k=payout][data-t="馬単"]').fill(pay); pg.wait_for_timeout(300); r.click()
    card.locator('[data-act=save]').click(); pg.wait_for_timeout(1200)


Z1 = '#zoneCard ol.zedit > li:nth-child(1)'
ZSEL = ['#zoneCard', '#zoneCard .zk-tabs', '#zoneCard .zk-head', '#zoneCard .zk-head .chip', Z1, Z1 + ' .zr-top', Z1 + ' .zr-label',
        Z1 + ' .zpick[data-f="a"]', Z1 + ' .zpick[data-f="b"]', Z1 + ' .zpick[data-f="t"]',
        Z1 + ' .zpick[data-f="b"] button[data-z="大穴"]', Z1 + ' .zpick[data-f="t"] button[data-z="大穴"]', Z1 + ' .zr-stat',
        '#zoneCard ol.zedit > li:nth-child(2)', '#zoneCard .zsave', '#zmsg']
RSEL = ['#result', '#result .vhead', '#result .lbadge', '#result .vhead .chips', '#result .vhead .chip.cus', '#result ol.zones > li:nth-child(1)',
        '#result ol.zones > li:nth-child(1) .zflow', '#result ol.zones > li:nth-child(1) .znums', '#result ol.zones > li:nth-child(1) .zref',
        '#result ol.zones > li:nth-child(1) .zthird', '#result ol.zones > li:nth-child(2)', '#result .numbers']
S2 = '#slotList .slotrow[data-n="2"]'
MSEL = ['#setMother', '#slotList', '#slotList .slotrow[data-n="1"]', S2, '#slotList .slotrow[data-n="3"]', '#slotEdit', '#smPreview', '#smApply', '#smUse', S2 + ' .sr-sub', S2 + ' [data-sact=edit]']

# 架空のJRAデータをExcel（検証データシート・A〜P列）にする
import openpyxl
XLSX = CM + ('/マイデータ.xlsx' if APP else '/JRA_マザーデータ.xlsx')
wb = openpyxl.Workbook(); ws = wb.active; ws.title = '検証データ'
ws.append(['日付', 'R', '馬場', '距離', '頭数', '単勝1位', '3連単1位', '1着人気', '2着人気', '3着人気', '3連単5位', '3連単10位', '馬単払戻', '3連単払戻', '備考', '集計対象'])
for line in jra_tsv().split('\n'):
    c = line.split('\t')
    ws.append([c[0], int(c[1]), c[2], int(c[3]), int(c[4]), float(c[5]), float(c[6]), int(c[7]), int(c[8]), int(c[9]), float(c[10]), float(c[11]), int(c[12]), int(c[13]), c[14], int(c[15])])
wb.save(XLSX)

errs = []
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, color_scheme='light', locale='ja-JP', timezone_id='Asia/Tokyo')
        if APP:
            ctx.add_init_script(FAKE)
            ctx.route('**/__native/autobackup.json', lambda route: route.fulfill(status=404, body='not found'))
        pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.add_init_script("if (!sessionStorage.getItem('x')) { sessionStorage.setItem('x', '1'); localStorage.setItem('tengel.form', %s); localStorage.setItem('tengel.win5', %s); }"
                           % (json.dumps(json.dumps(BLANK, ensure_ascii=False)), json.dumps(json.dumps(W5, ensure_ascii=False))))
        pg.goto(URL); pg.wait_for_timeout(2600)
        # ---- 判定：空 → 読み取り中 → 読み取ったあと ----
        content(pg, 'judge_empty', ['#ocrBtn', '#ocrRow', '.input-col > .card:nth-child(1)', '#result'])
        pg.evaluate("""document.getElementById('ocrMsg').innerHTML = '<div class="banner info"><span class="spin" aria-hidden="true"></span> 2枚の画像を読み取り中…（20〜60秒くらい）</div>'""")
        pg.wait_for_timeout(300)
        content(pg, 'judge_reading', ['#ocrMsg', '#ocrBtn'])
        load_form(pg, F9)
        pg.evaluate("""document.getElementById('ocrMsg').innerHTML = '<div class="banner info">読み取った：開催場・R・距離・頭数・馬場・単勝12頭・3連単1位・3連単5位・3連単10位<br><span class="small">読み間違いがないか、オッズと頭数だけは画面と見比べてね。</span></div>'""")
        pg.wait_for_timeout(300)
        content(pg, 'judge_filled', ['#ocrMsg', '.input-col > .card:nth-child(1) .fields'] + RSEL)
        bar_shot(pg, 'header.top', 'header_oi0'); bar_shot(pg, '.tabbar', 'tabbar_judge')
        # ---- 買う馬（大きく） ----
        ctx3 = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=3, color_scheme='light', locale='ja-JP', timezone_id='Asia/Tokyo')
        if APP:
            ctx3.add_init_script(FAKE)
            ctx3.route('**/__native/autobackup.json', lambda route: route.fulfill(status=404, body='not found'))
        p3 = ctx3.new_page()
        p3.add_init_script("localStorage.setItem('tengel.form', %s);" % json.dumps(json.dumps(F9, ensure_ascii=False)))
        p3.goto(URL); p3.wait_for_timeout(2600)
        z = p3.locator('#result ol.zones > li:nth-child(2)')
        z.scroll_into_view_if_needed(); p3.wait_for_timeout(300); scrub(p3)
        META['pick'] = p3.evaluate(BOX_JS, ['#result ol.zones > li:nth-child(2)', ['#result ol.zones > li:nth-child(2) button.hp[data-hs="b"][data-no="4"]',
                                                                                     '#result ol.zones > li:nth-child(2) .znums']])
        z.screenshot(path=f'{OUT}/pick_before.png', animations='disabled')
        p3.locator('#result button.hp[data-hz="人気→中穴"][data-hs="b"][data-no="4"]').click(); p3.wait_for_timeout(400); scrub(p3)
        z.screenshot(path=f'{OUT}/pick_after.png', animations='disabled')
        ctx3.close()
        # ---- 記録を3つ ----
        record(pg, 1, '2.5.1', '600', '1860')
        load_form(pg, F10); record(pg, 0, '1.2.3', '400', '0')
        load_form(pg, F11); record(pg, 0, '2.4.1', '600', '0')
        # ---- WIN5・記録・収支 ----
        tab(pg, 'win5')
        content(pg, 'win5', ['.w5top', '#w5Sum', '#w5Races .w5race[data-i="0"]', '#w5Races .w5race[data-i="0"] .w5zones', '#w5Races .w5race[data-i="0"] .w5picks'])
        bar_shot(pg, '.tabbar', 'tabbar_win5')
        tab(pg, 'rec')
        content(pg, 'records', ['#ymRec', '#rFilters', '#recSummary', '#recList .dgroup', '#recList .lrow:nth-child(1)', '#recList .lrow:nth-child(1) .stc'])
        bar_shot(pg, '.tabbar', 'tabbar_rec'); bar_shot(pg, 'header.top', 'header_oi3')
        tab(pg, 'stats')
        content(pg, 'stats', ['#moneyBody', '#moneyBody .money-tiles', '#statsBody'])
        bar_shot(pg, '.tabbar', 'tabbar_stats')
        # ---- 買い目編集：A層の第1に「2着 大穴」「3着 大穴」を足す ----
        tab(pg, 'set')
        bar_shot(pg, '.tabbar', 'tabbar_set')
        content(pg, 'set_z0', ZSEL + MSEL)
        pg.locator(Z1 + ' .zpick[data-f="b"] button[data-z="大穴"]').click(); pg.wait_for_timeout(400)
        content(pg, 'set_z1', ZSEL)
        pg.locator(Z1 + ' .zpick[data-f="t"] button[data-z="大穴"]').click(); pg.wait_for_timeout(400)
        content(pg, 'set_z2', ZSEL)
        pg.locator('#zoneCard [data-zact=save]').click(); pg.wait_for_timeout(900)
        content(pg, 'set_z3', ZSEL)
        bar_shot(pg, 'header.top', 'header_oi3c')
        # ---- カスタム買い目で判定（大井のデータ） ----
        load_form(pg, F9)
        tab(pg, 'judge')
        content(pg, 'judge_custom', RSEL)
        # ---- マザーデータ：2つ目「JRA」に架空のデータを入れて使う ----
        tab(pg, 'set')
        content(pg, 'set_m0', MSEL)
        pg.locator(S2 + ' [data-sact=edit]').click(); pg.wait_for_timeout(500)
        pg.locator('#smFile').set_input_files(XLSX); pg.wait_for_timeout(1500)
        content(pg, 'set_m1', MSEL)
        pg.locator('#smApply').click(); pg.wait_for_timeout(1500)
        content(pg, 'set_m2', MSEL)
        pg.locator('#smUse').click(); pg.wait_for_timeout(1200)
        content(pg, 'set_m3', MSEL)
        bar_shot(pg, 'header.top', 'header_jra')
        # ---- JRAのデータで判定（東京11R） ----
        load_form(pg, FJ)
        tab(pg, 'judge')
        content(pg, 'judge_jra', RSEL)
        b.close()
finally:
    srv.terminate(); srv.wait()
json.dump(META, open(OUT + '/meta.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('errors', errs[:3])
