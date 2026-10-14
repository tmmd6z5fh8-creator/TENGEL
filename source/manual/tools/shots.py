# 説明書用：アプリ（iPhone版）の画面を撮る。架空のレースで、記録はこのテスト用ブラウザの中だけ
#   python3 shots.py <作業フォルダ>              … Web版（ホーム画面のアプリ）の画面 → <作業フォルダ>/man/raw
#   TARGET=app python3 shots.py <作業フォルダ>   … App Store版の画面（アプリの中として開く・競馬場や版の名前が出ない）→ <作業フォルダ>/man_app/raw
import json, os, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright

SRC = '/home/claude/tengel/source'
SP = sys.argv[1]
APP = os.environ.get('TARGET') == 'app'
SRV = SP + '/mansrv'; PORT = 8791; URL = f'http://localhost:{PORT}/TENGEL/'
RAW = SP + ('/man_app/raw' if APP else '/man/raw'); os.makedirs(RAW, exist_ok=True)
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], cwd=SRC, check=True, stdout=subprocess.DEVNULL)
# 説明書の写真がまだなくても作れるように（MANUAL_SHOTS_BOOTSTRAP）
subprocess.run(['python3', 'build_pwa.py', SRV + '/TENGEL'], cwd=SRC, check=True, stdout=subprocess.DEVNULL,
               env=dict(os.environ, MANUAL_SHOTS_BOOTSTRAP='1', **({'TARGET': 'app', 'DATA_URL': f'http://localhost:{PORT}/remote/none.json'} if APP else {'TARGET': 'web'})))
# App Store版：アプリの中（tengel://）のかわりに、localhost でアプリ版として開く
def as_app(d):
    pth = d + '/index.html'; h = open(pth, encoding='utf8').read()
    assert "window.__NATIVE = location.protocol === 'tengel:';" in h
    open(pth, 'w', encoding='utf8').write(h.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))


if APP:
    as_app(SRV + '/TENGEL')
    # アップデートの写真用：アプリに入っているデータが前の版（280走）のアプリと、新しいデータ（290走）
    subprocess.run(['python3', 'build_pwa.py', SRV + '/OLDAPP'], cwd=SRC, check=True, stdout=subprocess.DEVNULL,
                   env=dict(os.environ, TARGET='app', MANUAL_SHOTS_BOOTSTRAP='1', HIST='hist_280.json', DROP='', MOTHER_VER='2026-10-07', DATA_URL=f'http://localhost:{PORT}/remote/mother_app.json'))
    as_app(SRV + '/OLDAPP')
    subprocess.run(['python3', 'build_pwa.py', SRV + '/_w'], cwd=SRC, check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, TARGET='web', MANUAL_SHOTS_BOOTSTRAP='1', MOTHER_VER='2026-10-20'))
    os.makedirs(SRV + '/remote'); shutil.copy(SRV + '/_w/data/mother_app.json', SRV + '/remote/mother_app.json')
# にせもののアプリ（共有・コピー・バックアップに、すぐ「できた」と返事をする）
FAKE = """
window.__NATIVE_INFO = { version: '1.0', build: '1', device: 'phone' };
window.__ocrLines = [];   // 画像の文字の読み取り（端末の中の文字認識）のかわり：順に返す「読めた文字と位置」
window.webkit = { messageHandlers: { tengel: { postMessage: function (m) {
  var val = true;
  if (m.name === 'ocr') { var L = window.__ocrLines.shift(); val = L ? { ok: true, lines: L, w: 1170, h: 2532, ms: 900 } : { ok: false, error: 'image_rejected' }; }
  setTimeout(function () { window.__nativeReply(m.id, true, val); }, 30);
} } } };
"""
OCR_DIR = os.path.join(SRC, 'testdata', 'ocr')
# App Storeに新しい版（1.1）が出ている、にせもののアプリ（アップデートの写真用）
FAKE_STORE = """
window.__NATIVE_INFO = { version: '1.0', build: '1', device: 'phone' };
window.webkit = { messageHandlers: { tengel: { postMessage: function (m) {
  var v = m.name === 'store' ? { found: true, version: '1.1', url: 'https://apps.apple.com/jp/app/id0000000000', notes: '', date: '', error: '' } : true;
  setTimeout(function () { window.__nativeReply(m.id, true, v); }, 30);
} } } };
"""
VENUE = '' if APP else '大井'
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(0.8)


def rows(nos, odds, fuku=None):
    fuku = fuku or [None] * len(nos)
    return [{"no": n, "tan": str(t), "fuku": (str(f) if f else "")} for n, t, f in zip(nos, odds, fuku)]


def form(r, dist, n, baba, nos, odds, fuku, s1, s1c, s5, s10):
    return {"id": None, "venue": VENUE, "date": "2026-10-14", "r": str(r), "dist": str(dist), "surface": "ダ", "baba": baba, "n": str(n), "tan1": "",
            "s1": str(s1), "s1combo": s1c, "s5": str(s5), "s5combo": "", "s10": str(s10), "s10combo": "", "rows": rows(nos, odds, fuku)}


# 9R：A層（比8.8）
F9 = form(9, 1400, 12, '良', [6, 2, 10, 7, 1, 4, 11, 5, 9, 3, 8, 12],
          [2.1, 3.4, 5.2, 7.8, 9.5, 12.4, 16.8, 22.5, 31.0, 45.6, 58.3, 82.1],
          [1.1, 1.3, 1.6, 2.0, 2.4, 2.9, 3.6, 4.5, 5.8, 7.9, 9.8, 13.5], 18.5, '6-2-10', 42.6, 78.9)
# 10R：B層（比13.9）
F10 = form(10, 1600, 12, '良', [3, 8, 1, 11, 5, 2, 12, 7, 4, 9, 6, 10],
           [2.8, 3.6, 4.9, 6.7, 8.8, 11.5, 15.2, 19.8, 26.4, 38.0, 52.5, 70.3], None, 39.0, '', 88.0, 140.5)
# 11R：C層・第2段階（3連単1位95.2・14頭）
F11 = form(11, 1800, 14, '稍重', [5, 12, 3, 9, 1, 14, 7, 10, 2, 13, 6, 11, 4, 8],
           [3.6, 4.4, 5.9, 7.2, 9.0, 11.8, 14.6, 18.9, 24.1, 30.5, 41.2, 55.0, 73.8, 99.9], None, 95.2, '', 210.4, 355.0)


def w5odds(n, tan1):
    xs = [tan1] + [round(tan1 + 1.9 * i + 0.35 * i * i, 1) for i in range(1, n)]
    return [{"no": (i * 5) % n + 1, "tan": str(x), "fuku": ""} for i, x in enumerate(xs)]


# 5重勝（WIN5）の5レース。App Store版は架空の開催場の名前（ひがし・にし）
V1, V2 = ('ひがし', 'にし') if APP else ('東京', '京都')
RACES = [(V1, 9, 1600, 12, '良', 1.8, 12.0), (V2, 10, 1800, 14, '良', 2.0, 30.0), (V1, 10, 1400, 12, '稍重', 3.0, 70.0),
         (V2, 11, 2000, 16, '良', 3.2, 80.0), (V1, 11, 1600, 12, '良', 1.5, 9.0)]
W5 = {"id": None, "fixed": False, "date": "2026-10-18", "budget": "3000", "mode": "pick", "randAll": False, "stake": "", "payout": "", "other": "", "note": "",
      "races": [{"form": {"venue": v, "date": "2026-10-18", "r": str(r), "dist": str(d), "surface": "芝", "baba": b, "n": str(n), "rows": w5odds(n, t1), "tan1": "",
                          "s1": str(s1), "s1combo": "", "s5": "", "s5combo": "", "s10": "", "s10combo": ""}, "sel": None, "win": "", "picks": None, "man": None}
                for v, r, d, n, b, t1, s1 in RACES]}

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
    el.scroll_into_view_if_needed(); pg.wait_for_timeout(200)
    META[name] = pg.evaluate(BOX_JS, [root, list(sels)])
    el.screenshot(path=f'{RAW}/{name}.png', animations='disabled')
    print('  📸', name, META[name]['W'], 'x', META[name]['H'])


def shot_top(pg, name, root, max_h, sels=()):
    # 要素の上から max_h までを切り出す
    info = pg.evaluate(BOX_JS, [root, list(sels)])
    top = pg.evaluate("(r) => { const b = document.querySelector(r).getBoundingClientRect(); return { x: b.left + scrollX, y: b.top + scrollY }; }", root)
    h = min(max_h, info['H'])
    pg.screenshot(path=f'{RAW}/{name}.png', full_page=True, clip={'x': top['x'], 'y': top['y'], 'width': info['W'], 'height': h}, animations='disabled')
    info['H'] = h
    META[name] = info
    print('  📸', name, info['W'], 'x', h)


def shot_pad(pg, name, root, sels=(), padx=12, pady=6):
    # まわりに余白（左右 padx・上下 pady）をつけて撮る（余白のない要素用）。座標は余白の分ずらす
    el = pg.locator(root).first
    el.scroll_into_view_if_needed(); pg.wait_for_timeout(200)
    info = pg.evaluate(BOX_JS, [root, list(sels)])
    bb = pg.evaluate("(r) => { const b = document.querySelector(r).getBoundingClientRect(); return { x: b.left + scrollX, y: b.top + scrollY, w: b.width, h: b.height }; }", root)
    pg.screenshot(path=f'{RAW}/{name}.png', full_page=True, clip={'x': bb['x'] - padx, 'y': bb['y'] - pady, 'width': bb['w'] + 2 * padx, 'height': bb['h'] + 2 * pady}, animations='disabled')
    for v in info['b'].values():
        if v:
            v['x'] += padx; v['y'] += pady
    info['W'] = round(info['W'] + 2 * padx, 1); info['H'] = round(info['H'] + 2 * pady, 1)
    META[name] = info
    print('  📸', name, info['W'], 'x', info['H'])


def tab(pg, name):
    hide(pg, False); pg.click(f'.tabbar button[data-tab={name}]'); pg.wait_for_timeout(700); hide(pg, True)


def load_form(pg, f):
    pg.evaluate("(f) => localStorage.setItem('tengel.form', f)", json.dumps(f, ensure_ascii=False))
    pg.reload(); pg.wait_for_timeout(2200); hide(pg, True)


try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, color_scheme='light', locale='ja-JP', timezone_id='Asia/Tokyo')
        if APP:
            ctx.add_init_script(FAKE)
            ctx.route('**/__native/autobackup.json', lambda route: route.fulfill(status=404, body='not found'))
        pg = ctx.new_page()
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.add_init_script("if (!sessionStorage.getItem('x')) { sessionStorage.setItem('x', '1'); localStorage.setItem('tengel.form', %s); localStorage.setItem('tengel.win5', %s); }"
                           % (json.dumps(json.dumps(F9, ensure_ascii=False)), json.dumps(json.dumps(W5, ensure_ascii=False))))
        pg.goto(URL); pg.wait_for_timeout(2500)

        # ---- 下のタブ・判定へ↓のバー（入力欄を見ているとき） ----
        pg.evaluate("scrollTo(0, 0)"); pg.wait_for_timeout(400)
        pg.screenshot(path=f'{RAW}/bottom_bars.png', clip={'x': 0, 'y': 844 - 150, 'width': 390, 'height': 150})
        META['bottom_bars'] = {'W': 390, 'H': 150, 'b': {}}
        shot(pg, 'tabbar', '.tabbar')
        hide(pg, True)

        # ---- 判定タブ：入力欄 ----
        shot(pg, 'judge_info', '.input-col > .card:nth-child(1)', ['#slotJudge', '#ocrRow', '#fVenue', '#fDate', '#fR', '#fDist', '#fN', '#fSurf', '#fBaba'])
        shot(pg, 'judge_odds', '.input-col > .card:nth-child(2)', ['.oheads', '#oddsGrid', '#addRow'])
        shot(pg, 'judge_tri', '.input-col > .card:nth-child(3)', ['#fS1', '#fS1c', '#fS5', '#fS10', '#clearBtn', '#sampleBtn'])

        # ---- 判定結果（A層） ----
        shot(pg, 'result_a', '#result', ['.vhead .lbadge', '.vhead .vkubun', '.vhead .vratio', '.vhead .chips', '.hpnote',
                                         'ol.zones > li:nth-child(1) .zflow', 'ol.zones > li:nth-child(1) .znums', 'ol.zones > li:nth-child(1) .zref',
                                         'ol.zones > li:nth-child(1) .zthird', 'ol.zones > li:nth-child(2)', '.numbers', '.vfoot', '.oldline', '.w5push', '#copyAll', '#saveJudge', 'details.full'])

        # ---- 買う馬を選ぶ ----
        shot(pg, 'pick_before', 'ol.zones > li:nth-child(2)', ['.znums', '.zthird'])
        pg.locator('#result button.hp[data-hz="人気→中穴"][data-hs="b"][data-no="4"]').click(); pg.wait_for_timeout(400)
        shot(pg, 'pick_after', 'ol.zones > li:nth-child(2)', ['.znums', 'button.hp.off'])

        # ---- 結果・収支の記録 ----
        card = pg.locator('#recCard')
        card.locator('[data-k=types] button[data-v="3連単"]').click(); pg.wait_for_timeout(250)
        card.locator('[data-k=stake][data-t="馬単"]').fill('600'); card.locator('[data-k=stake][data-t="3連単"]').fill('900')
        card.locator('[data-k=buyz] button').nth(1).click(); pg.wait_for_timeout(200)
        card.locator('[data-k=mode] button[data-v=nin]').click(); pg.wait_for_timeout(200)
        res = card.locator('[data-k=res]')

        def typ(s_):
            res.fill(''); res.press_sequentially(s_, delay=20); pg.wait_for_timeout(350)

        typ('1.3.2'); shot(pg, 'st_notbought', '#recCard [data-k=status]')
        typ('2.6.1'); shot(pg, 'st_notpicked', '#recCard [data-k=status]')
        typ('2.5.1')
        card.locator('[data-k=payout][data-t="馬単"]').fill('2280'); card.locator('[data-k=payout][data-t="3連単"]').fill('4350'); pg.wait_for_timeout(300)
        card.locator('[data-k=upay]').fill('380'); card.locator('[data-k=spay]').fill('1450'); pg.wait_for_timeout(200)
        res.click(); pg.wait_for_timeout(200)
        shot(pg, 'st_hit', '#recCard [data-k=status]')
        shot(pg, 'md_record', '#recCard [data-k=mfld]')
        shot(pg, 'record', '#recCard', ['[data-k=status]', '[data-k=types]', '[data-k=amts]', '[data-k=amtsum]', '[data-k=buyzf]', '[data-k=mode]', '[data-k=res]', '[data-k=hint]', '[data-k=mfld]', '[data-k=other]', '[data-k=note]', '[data-act=save]'])
        card.locator('[data-act=save]').click(); pg.wait_for_timeout(1200)

        # ---- 10R（B層）：推奨ゾーンの外で不的中 ----
        load_form(pg, F10)
        card = pg.locator('#recCard')
        card.locator('[data-k=stake][data-t="馬単"]').fill('400')
        card.locator('[data-k=buyz] button').nth(0).click(); pg.wait_for_timeout(200)
        card.locator('[data-k=mode] button[data-v=nin]').click(); pg.wait_for_timeout(200)
        res = card.locator('[data-k=res]'); res.fill(''); res.press_sequentially('1.2.3', delay=20); pg.wait_for_timeout(300)
        card.locator('[data-k=payout][data-t="馬単"]').fill('0'); pg.wait_for_timeout(300); res.click()
        shot(pg, 'st_outside', '#recCard [data-k=status]')
        shot(pg, 'result_b_head', '#result .vhead')
        card.locator('[data-act=save]').click(); pg.wait_for_timeout(1200)

        # ---- 11R（C層・第2段階）：結果待ちで保存 ----
        load_form(pg, F11)
        shot(pg, 'result_c', '#result', ['.vhead .lbadge', '.vhead .chips', 'ol.zones', '.numbers', '.vfoot'])
        card = pg.locator('#recCard')
        card.locator('[data-k=stake][data-t="馬単"]').fill('300')
        card.locator('[data-k=buyz] button').nth(0).click(); pg.wait_for_timeout(300)
        shot(pg, 'st_wait', '#recCard [data-k=status]')
        card.locator('[data-act=save]').click(); pg.wait_for_timeout(1200)

        # ---- オッズ画像：Web版はキーがないときの案内、App Store版は読み取ったあと（端末の中の文字認識のかわりに、架空のオッズ画面の文字を返す） ----
        pg.evaluate("scrollTo(0, 0)")
        if APP:
            pg.evaluate("window.__ocrLines = %s" % json.dumps([json.load(open(os.path.join(OCR_DIR, k + '.json'), encoding='utf-8'))['lines'] for k in ('a_tanfuku_waku', 'c_sanrentan')], ensure_ascii=False))
            pg.set_input_files('#ocrFile', [os.path.join(OCR_DIR, 'a_tanfuku_waku.jpg'), os.path.join(OCR_DIR, 'c_sanrentan.jpg')]); pg.wait_for_timeout(2500)
            pg.evaluate("scrollTo(0, 0)"); pg.wait_for_timeout(200)
            shot(pg, 'ocr_done', '.input-col > .card:nth-child(1)', ['#ocrRow', '#ocrMsg'])
            load_form(pg, F11)   # 読み取ったレースを消して、11R に戻す
        else:
            pg.locator('#ocrBtn').click(); pg.wait_for_timeout(500)
            shot(pg, 'ocr_need', '.input-col > .card:nth-child(1)', ['#ocrRow', '#ocrMsg'])

        # ---- 記録タブ ----
        tab(pg, 'rec')
        shot(pg, 'records', '#v-rec', ['#ymRec', '#rFilters', '#recSummary', '#recExportBtn', '#recList .dgroup h3', '#recList .lrow:nth-child(1)', '#recList .lrow:nth-child(2)', '#recList .lrow:nth-child(3)'])
        pg.locator('#recList .lrow .lmain').first.click(); pg.wait_for_timeout(600)
        shot(pg, 'record_open', '#recList .lrow:nth-child(1)', ['.ledit', '[data-act=save]', '[data-act=load]', '[data-act=del1]', 'details.full'])

        # ---- 実測・回収タブ ----
        tab(pg, 'stats')
        shot(pg, 'stats_money', '#moneyBody .money-tiles')
        shot(pg, 'stats_type', '#moneyBody .stat-grid > .card:nth-child(2)')
        shot(pg, 'stats_period', '#perChips')
        shot(pg, 'stats_t1', '#statsBody .card:first-child')

        # ---- WIN5 ----
        tab(pg, 'win5')
        shot(pg, 'w5_top', '.w5top', ['details.full', '#w5Date', '#w5Budget', '#w5Mode', '#w5Sum'])
        shot(pg, 'w5_race', '#w5Races .w5race[data-i="0"]', ['.w5h', '.w5zones', '.w5picks', '.zref', '[data-w5act=edit]', '[data-w5act=clear]'])
        picks = [[x.inner_text() for x in pg.locator(f'#w5Races .w5race[data-i="{i}"] .w5picks .num:not(.off)').all()] for i in range(5)]
        print('  WIN5 picks', picks)
        for i in range(5):
            win = picks[i][0] if i != 2 else str(max(int(x) for x in [h['no'] for h in W5['races'][2]['form']['rows']] if str(x) not in picks[2]))
            pg.locator(f'#w5Win{i}').fill(win); pg.wait_for_timeout(120)
        pg.locator('#w5Pay').fill('0'); pg.wait_for_timeout(400)
        shot(pg, 'w5_res', '#w5ResCard', ['.w5res', '#w5Status', '#w5Stake', '#w5Pay', '#w5Other', '[data-w5act=save]'])

        # ---- 設定 ----
        tab(pg, 'set')
        shot_top(pg, 'set_zone', '#zoneCard', 640, ['.zk-tabs', '.zk-head', 'ol.zedit > li:nth-child(1)', '.zr-line', '.zr-stat'])
        shot(pg, 'set_zone_save', '#zoneCard .zsave')
        shot(pg, 'set_mother', '#setMother', ['#slotList', '#slotEdit', '#slotEdit .mdtools'])
        if not APP:   # App Store版の「画像の読み取り」はAPIキーの欄がない（説明書にも出さない）
            shot(pg, 'set_ocr', '#setOcr', ['#soKey', '#soSave', '#soModel'])
        if not APP:   # App Store版の「アプリの更新」（App Storeの版）は、下のアップデートの写真で撮る
            shot(pg, 'set_update', '#setUpdate')
        shot(pg, 'set_backup', '#setBackup', ['#pwaBackup', '#pwaRestore'])

        # ---- マザーデータの中身：ボタン・書き出す・ファイルから足す・一覧・1つ入れる ----
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

        # ---- 新しい版のお知らせ（Web版だけ） ----
        if not APP:
            vj = SRV + '/TENGEL/version.json'; old = open(vj, encoding='utf-8').read()
            v = json.loads(old); v['app'] = '2026.10.20'; v['mother'] = '2026-10-18'
            open(vj, 'w', encoding='utf-8').write(json.dumps(v))
            pg.reload(); pg.wait_for_timeout(2600); hide(pg, True)
            pg.evaluate("scrollTo(0, 0)")
            shot(pg, 'update_bar', 'header.top')
            open(vj, 'w', encoding='utf-8').write(old)
        if APP:
            # ---- アップデート：App Storeに新しい版（1.1）・新しいデータ（290走）があるとき ----
            ctx2 = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, color_scheme='light', locale='ja-JP', timezone_id='Asia/Tokyo')
            ctx2.add_init_script(FAKE_STORE)
            ctx2.route('**/__native/autobackup.json', lambda route: route.fulfill(status=404, body='not found'))
            p2 = ctx2.new_page(); p2.on('pageerror', lambda e: errs.append(str(e)))
            p2.add_init_script("if (!sessionStorage.getItem('x')) { sessionStorage.setItem('x', '1'); localStorage.setItem('tengel.form', %s); }" % json.dumps(json.dumps(F9, ensure_ascii=False)))
            p2.goto(f'http://localhost:{PORT}/OLDAPP/'); p2.wait_for_timeout(4500); hide(p2, True)
            p2.evaluate("scrollTo(0, 0)")
            shot(p2, 'upd_bars', 'header.top')
            for k in ('app', 'data'):
                p2.locator(f'#nBar_{k} .nbx').click()
            tab(p2, 'set')
            p2.locator('#nuCheck').click(); p2.locator('#sdCheck').click(); p2.wait_for_timeout(900)
            shot(p2, 'upd_app', '#setUpdate', ['dl.kvs dd', '#nuStore', '#nuCheck', '#nuOpen'])
            shot(p2, 'upd_data', '#setData', ['#sdCur', '#sdCheck', '#sdApply'])
            ctx2.close()
        b.close()
finally:
    srv.terminate()
json.dump(META, open(f'{RAW}/meta.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('errors:', errs[:5])
