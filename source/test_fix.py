# 2026.10.11-3 のテスト
#  1) 今の公開版で大井に「分析シート」を入れて壊す → アプリ内で更新 → 大井が自動で元に戻る（記録はそのまま）
#  2) 形のちがうファイル（分析シート・分析表・馬場フィルター・貼り付け）は入らない（いまのデータはそのまま）
#  3) ひとつ前に戻す（1つ目・2つ目、空にしたあとも）
#  4) 画像の読み取り：APIキーなし→案内、キーの保存（偽API）、読み取り→入力欄に入る、エラーの案内、バックアップにキーが入らない
#  5) 保存場所が開けないとき：判定はできる（大井の参考値が出る）
import json, os, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv'); APPDIR = os.path.join(SRV, 'TENGEL'); OUT = os.path.join(W, 't5'); os.makedirs(OUT, exist_ok=True)
PORT = 8768; URL = f'http://localhost:{PORT}/TENGEL/'
NEW = os.environ.get('NEW_VER', '2026.10.11-3')
def deploy_dir(src):
    shutil.rmtree(APPDIR, ignore_errors=True); shutil.copytree(src, APPDIR, ignore=shutil.ignore_patterns('.git', 'README.md', 'source'))
def build(app_ver, out='pwa_t'):
    subprocess.run(['python3', 'build_pwa.py', out], check=True, env=dict(os.environ, APP_VER=app_ver, HIST='hist_280.json', MOTHER_VER='2026-10-07'), stdout=subprocess.DEVNULL)
    return out
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
deploy_dir(os.environ.get('OLD_APP', os.path.dirname(W)))   # 今の公開版
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
errs, fails, api_calls = [], [], []
def check(cond, label):
    print(('  ✅ ' if cond else '  ❌ ') + label)
    if not cond: fails.append(label)
def info(pg):
    return pg.evaluate("async () => { await TengelLocal.ready; return TengelLocal.slots.info().map(s => `${s.n}:${s.count}/${s.usable}${s.active ? '*' : ''}`).join(' ') }")
def text(pg, sel): return pg.locator(sel).inner_text().replace('\n', ' | ')
OCR = {"venue": "大井", "date": "2026-10-12", "r": 9, "dist": 1600, "surface": "ダ", "baba": "良", "n": 12,
       "horses": [{"no": i + 1, "tan": t, "fuku": f} for i, (t, f) in enumerate([(5.1, '1.6-2.4'), (2.3, '1.1-1.3'), (12.8, '3.0-5.1'), (8.4, '2.2-3.4'), (31.0, '6.0-9.9'), (3.9, '1.4-2.0'), (18.5, '4.1-6.6'), (45.2, '8.8-14.0'), (6.6, '1.9-2.8'), (70.1, '11.0-18.2'), (24.4, '5.0-8.0'), (99.9, '15.5-25.1')])],
       "s1": {"combo": "2-6-1", "odds": 21.4}, "s5": {"combo": "6-2-9", "odds": 48.0}, "s10": {"combo": "2-1-4", "odds": 75.5}}
api_mode = {'m': 'ok'}
def api_route(route):
    req = route.request
    cors = {'access-control-allow-origin': '*', 'access-control-allow-headers': 'x-api-key,anthropic-version,content-type,anthropic-dangerous-direct-browser-access', 'access-control-allow-methods': 'POST, OPTIONS'}
    if req.method == 'OPTIONS': return route.fulfill(status=200, headers=cors, body='')
    body = json.loads(req.post_data or '{}'); h = req.headers
    api_calls.append({'model': body.get('model'), 'key': h.get('x-api-key'), 'cors': h.get('anthropic-dangerous-direct-browser-access'), 'ver': h.get('anthropic-version'),
                      'imgs': [(c['source']['media_type'], len(c['source']['data'])) for m in body.get('messages', []) for c in (m['content'] if isinstance(m['content'], list) else []) if c.get('type') == 'image']})
    m = api_mode['m']
    if m == 'badkey': return route.fulfill(status=401, headers=cors, content_type='application/json', body=json.dumps({"type": "error", "error": {"type": "authentication_error", "message": "invalid x-api-key"}}))
    if m == 'credit': return route.fulfill(status=400, headers=cors, content_type='application/json', body=json.dumps({"type": "error", "error": {"type": "invalid_request_error", "message": "Your credit balance is too low to access the Anthropic API."}}))
    out = 'OK' if not any(c.get('type') == 'image' for mm in body.get('messages', []) for c in (mm['content'] if isinstance(mm['content'], list) else [])) else '```json\n' + json.dumps(OCR, ensure_ascii=False) + '\n```'
    return route.fulfill(status=200, headers=cors, content_type='application/json', body=json.dumps({"content": [{"type": "text", "text": out}], "stop_reason": "end_turn"}))
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, accept_downloads=True)
        ctx.route('https://api.anthropic.com/**', api_route)
        pg = ctx.new_page()
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' and 'fonts.g' not in m.text and 'ERR_' not in m.text else None)
        pg.goto(URL); pg.wait_for_timeout(1500)
        print('[1] 今の公開版', pg.evaluate('window.__APP_VER'), info(pg))
        # 記録を1件
        pg.click('#sampleBtn'); pg.wait_for_timeout(300); pg.fill('#fDate', '2026-10-10'); pg.wait_for_timeout(400)   # 入力例のままだと保存できないので日付を入れて本番扱いに
        card = pg.locator('#recCard'); card.locator('[data-k=stake]').fill('1000'); card.locator('[data-k=res]').fill('7-6-2'); card.locator('[data-act=save]').click(); pg.wait_for_timeout(500)
        print('    記録', pg.evaluate('TengelLocal.mem.bets.size'), '件')
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(300)
        pg.set_input_files('#smFile', os.path.join(W, 'xt', 'raw_bunseki_sheet.xlsx')); pg.wait_for_timeout(1200); pg.click('#smApply'); pg.wait_for_timeout(800)
        broken = info(pg); print('    分析シートを入れたあと:', broken)
        check(broken.startswith('1:280/0*'), '公開版では分析シートで大井が壊れる（再現）')
        # 新しい版を公開 → アプリ内で更新
        deploy_dir(build(NEW))
        pg.click('#suCheck'); pg.wait_for_timeout(800)
        with pg.expect_navigation(timeout=15000): pg.click('#updGo')
        toasts = []
        for _ in range(12):
            pg.wait_for_timeout(250)
            t = pg.locator('#toast')
            if t.is_visible(): toasts.append(t.inner_text())
        after = info(pg); print('[1] 更新後', pg.evaluate('window.__APP_VER'), after, '| toast:', list(dict.fromkeys(toasts)))
        check(pg.evaluate('window.__APP_VER') == NEW, '新しい版になった')
        check(after.startswith('1:280/268*'), '大井が自動で元に戻った（280走・集計対象268走）')
        check(any('判定に使えない形' in t for t in toasts), '戻したことをお知らせした')
        check(pg.evaluate('TengelLocal.mem.bets.size') == 1, '記録は消えていない')
        check(pg.evaluate('TengelLocal.slots.prev(1)') is None, '壊れたデータは「ひとつ前」に残さない')
        pg.click('.tabbar button[data-tab=judge]'); pg.wait_for_timeout(300); pg.click('#sampleBtn'); pg.wait_for_timeout(500)
        z = [x.inner_text() for x in pg.locator('#result .zref').all()][:1]
        print('    判定の参考値:', z); check(z and 'n=0' not in z[0] and '—' not in z[0].split('参考的中率')[1][:4], '判定の参考的中率が出る')

        # 2) 形のちがうファイルは入らない
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(300)
        for f, kw in [('raw_bunseki_sheet.xlsx', '分析シート'), ('raw_bunseki_hyo.xlsx', '分析表'), ('raw_baba_filter.xlsx', 'フィルター')]:
            pg.set_input_files('#smFile', os.path.join(W, 'xt', f)); pg.wait_for_timeout(1200)
            t = text(pg, '#smPreview'); print(f'[2] {f} →', t[:150])
            check(kw in t and 'いまのデータはそのまま' in t and pg.locator('#smApply').count() == 0, f'{f} は入れられない（{kw}と案内）')
        pg.locator('#slotEdit details summary').click()
        pg.fill('#smText', '2026/10/08\t1\t良\t1200\t12\t1位-2位-5位\n2026/10/08\t2\t良\t1400\t11\t3位-1位-4位'); pg.click('#smParse'); pg.wait_for_timeout(300)
        t = text(pg, '#smPreview'); print('[2] 貼り付け（分析シートの行）→', t[:120]); check('入れられない' in t, '形のちがう貼り付けも入らない')
        check(info(pg).startswith('1:280/268*'), '大井はそのまま')
        pg.locator('#setMother').screenshot(path=os.path.join(OUT, 'fix_refuse.png'))

        # 3) ひとつ前に戻す
        pg.set_input_files('#smFile', os.path.join(W, 'xt', 'test_excel_like.xlsx')); pg.wait_for_timeout(1200)
        print('[3] 正しいExcel →', text(pg, '#smPreview')[:160]); pg.click('#smApply'); pg.wait_for_timeout(800)
        i1 = info(pg); print('    入れたあと', i1)
        ud = pg.locator('#seUndo'); check(ud.is_visible() and '280走' in ud.inner_text(), f'「ひとつ前に戻す」が出る（{ud.inner_text()}）')
        ud.click(); ud.click(); pg.wait_for_timeout(800)
        i2 = info(pg); print('    戻したあと', i2, '| src:', text(pg, '#seMeta')[:80]); check(i2.startswith('1:280/268*'), '大井が前のデータに戻った')
        check(pg.locator('#seUndo').is_visible() and i1.split()[0].split(':')[1].split('/')[0] + '走' in pg.locator('#seUndo').inner_text(), 'もう一度押せば入れたデータに戻せる')
        # 2つ目：JRAを入れる → 空にする → 戻す
        pg.click('#slotList .slotrow[data-n="2"] [data-sact=edit]'); pg.wait_for_timeout(300)
        pg.set_input_files('#smFile', os.path.join(W, 'xt', 'jra_test.xlsx')); pg.wait_for_timeout(1200); pg.click('#smApply'); pg.wait_for_timeout(800)
        pg.click('#seClear'); pg.click('#seClear'); pg.wait_for_timeout(800)
        i3 = info(pg); print('[3] JRAを空にした', i3)
        u2 = pg.locator('#seUndo'); check(u2.is_visible() and '192走' in u2.inner_text(), '空にしたあとも「ひとつ前に戻す」が出る')
        u2.click(); u2.click(); pg.wait_for_timeout(800)
        check('2:192/192' in info(pg), 'JRAのデータが戻った')

        # 4) 画像の読み取り
        pg.click('.tabbar button[data-tab=judge]'); pg.wait_for_timeout(300)
        check(pg.locator('#ocrRow').is_visible(), '判定タブに「オッズ画像から読み取る」がある')
        pg.screenshot(path=os.path.join(OUT, 'fix_judge_top.png'))
        pg.click('#ocrBtn'); pg.wait_for_timeout(300)
        t = text(pg, '#ocrMsg'); print('[4] キーなしで押す →', t[:100]); check('APIキー' in t, 'キーがないと案内が出る（写真は選ばせない）')
        pg.locator('#ocrMsg').screenshot(path=os.path.join(OUT, 'fix_ocr_need.png'))
        pg.click('#ocrMsg [data-goset=ocr]'); pg.wait_for_timeout(600)
        check(pg.locator('#v-set').is_visible() and pg.locator('#setOcr').is_visible(), '設定タブの「画像の読み取り」に飛ぶ')
        pg.fill('#soKey', 'abc'); pg.click('#soSave'); pg.wait_for_timeout(200); print('    ちがう形のキー →', text(pg, '#soMsg'))
        api_mode['m'] = 'badkey'; pg.fill('#soKey', 'sk-ant-api03-wrongkey'); pg.click('#soSave'); pg.wait_for_timeout(1000)
        t = text(pg, '#soMsg'); print('    401 →', t, '|', text(pg, '#soState')); check('使えない' in t and 'まだ' in text(pg, '#soState'), '使えないキーは保存しない')
        api_mode['m'] = 'ok'; pg.fill('#soKey', 'sk-ant-api03-GOODKEY-1234abcd'); pg.click('#soSave'); pg.wait_for_timeout(1000)
        t = text(pg, '#soMsg'); print('    200 →', t, '|', text(pg, '#soState')); check('保存した' in t and 'abcd' in text(pg, '#soState'), 'キーを保存した（伏せ字で表示）')
        pg.locator('#setOcr').screenshot(path=os.path.join(OUT, 'fix_ocr_set.png'))
        pg.click('.tabbar button[data-tab=judge]'); pg.wait_for_timeout(300)
        n0 = len(api_calls)
        with pg.expect_file_chooser() as fc: pg.click('#ocrBtn')
        fc.value.set_files([os.path.join(W, 'xt', 'odds_shot.png'), os.path.join(W, 'xt', 'odds_shot.png')])
        pg.wait_for_selector('#ocrMsg .banner:not(:has(.spin))', timeout=15000); pg.wait_for_timeout(400)
        t = text(pg, '#ocrMsg'); c = api_calls[-1] if len(api_calls) > n0 else {}
        print('[4] 読み取り →', t[:140]); print('    APIへ:', {k: c.get(k) for k in ('model', 'cors', 'ver', 'imgs')})
        check(c.get('model') == 'claude-sonnet-5-5' and c.get('cors') == 'true' and c.get('key') == 'sk-ant-api03-GOODKEY-1234abcd' and len(c.get('imgs', [])) == 2 and all(m == 'image/jpeg' and 50000 < n < 3000000 for m, n in c.get('imgs', [])), 'スクショ2枚をJPEGにしてClaudeへ送った')
        vals = pg.evaluate("({r: document.querySelector('#fR').value, dist: document.querySelector('#fDist').value, n: document.querySelector('#fN').value, s1: document.querySelector('#fS1').value, baba: document.querySelector('#fBaba [aria-pressed=true]')?.dataset.v, t2: document.querySelector('#oddsGrid [data-no=\"2\"][data-k=tan]').value})")
        print('    入力欄:', vals); check(vals == {'r': '9', 'dist': '1600', 'n': '12', 's1': '21.4', 'baba': '良', 't2': '2.3'}, '読み取った値が入力欄に入った')
        check(pg.locator('#result .vkubun').count() == 1, '判定が出た：' + (pg.locator('#result .vkubun').inner_text() if pg.locator('#result .vkubun').count() else '—'))
        pg.screenshot(path=os.path.join(OUT, 'fix_ocr_done.png'))
        api_mode['m'] = 'credit'
        with pg.expect_file_chooser() as fc: pg.click('#ocrBtn')
        fc.value.set_files([os.path.join(W, 'xt', 'odds_shot.png')]); pg.wait_for_timeout(2500)
        t = text(pg, '#ocrMsg'); print('[4] 残高不足 →', t[:100]); check('クレジット' in t and pg.locator('#ocrMsg [data-goset=ocr]').count() == 1, '残高不足の案内が出る')
        api_mode['m'] = 'ok'
        # 節約モデル
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(300); pg.click('#soModel button[data-v=eco]'); pg.wait_for_timeout(300)
        pg.click('.tabbar button[data-tab=judge]'); pg.wait_for_timeout(200)
        with pg.expect_file_chooser() as fc: pg.click('#ocrBtn')
        fc.value.set_files([os.path.join(W, 'xt', 'odds_shot.png')]); pg.wait_for_timeout(2500)
        check(api_calls[-1].get('model') == 'claude-haiku-5-5', '節約にするとHaikuで読む')
        # バックアップにキーが入らない
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(300)
        pg.evaluate("navigator.canShare = undefined")
        with pg.expect_download() as dl: pg.click('#pwaBackup')
        bk = open(dl.value.path(), encoding='utf8').read()
        check('GOODKEY' not in bk and 'sk-ant' not in bk, 'バックアップのファイルにAPIキーが入っていない')
        # 開き直してもキーと大井は残る
        pg.reload(); pg.wait_for_timeout(1500)
        check(pg.evaluate("TengelLocal.ocr.get() && TengelLocal.ocr.get().model") == 'eco' and info(pg).startswith('1:280/268*'), '開き直してもキーと大井はそのまま')
        print('    最後:', info(pg))

        # 5) 保存場所が開けないとき
        ctx2 = b.new_context(viewport={'width': 390, 'height': 844})
        ctx2.add_init_script("""(() => { const o = indexedDB.open.bind(indexedDB); indexedDB.open = function () { const r = {}; setTimeout(() => { r.error = new Error('UnknownError: Connection to Indexed Database server lost'); r.onerror && r.onerror(); }, 5); return r; }; })();""")
        p2 = ctx2.new_page(); e2 = []; p2.on('pageerror', lambda e: e2.append(str(e)))
        p2.goto(URL); p2.wait_for_timeout(2500)
        bar = p2.locator('#memOnlyBar')
        print('[5] 保存場所なし →', bar.inner_text()[:80] if bar.count() else 'バーなし', '| pill:', p2.locator('#dbpill').inner_text())
        check(bar.count() == 1, '保存できないことを知らせる')
        p2.click('#sampleBtn'); p2.wait_for_timeout(500)
        z = [x.inner_text() for x in p2.locator('#result .zref').all()][:1]; print('    判定の参考値:', z)
        check(z and 'n=0' not in z[0], '保存できなくても大井の参考値で判定できる')
        check(not e2, 'エラーなし ' + str(e2))
        ctx2.close()
        print('page errors:', errs)
        check(not [e for e in errs if 'PAGEERR' in e], 'ページのエラーなし')
finally:
    srv.terminate()
print('\nFAILS:', fails)
sys.exit(1 if fails else 0)
