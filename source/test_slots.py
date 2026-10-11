# マザーデータ（3つ）のテスト：今の公開版 → 新しい版に更新 → 2つ目にJRA、3つ目に船橋を入れて切り替え・名前変更・空にする・バックアップ
import json, os, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv'); APPDIR = os.path.join(SRV, 'TENGEL'); OUT = os.path.join(W, 't5'); os.makedirs(OUT, exist_ok=True)
URL = 'http://localhost:8766/TENGEL/'
def deploy_dir(src):
    shutil.rmtree(APPDIR, ignore_errors=True); shutil.copytree(src, APPDIR, ignore=shutil.ignore_patterns('.git', 'README.md', 'source'))
def build(app_ver, out='pwa_t'):
    subprocess.run(['python3', 'build_pwa.py', out], check=True, env=dict(os.environ, APP_VER=app_ver, HIST='hist_280.json', MOTHER_VER='2026-10-07'), stdout=subprocess.DEVNULL)
    return out
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
deploy_dir(os.environ.get('OLD_APP', os.path.dirname(W)))   # 今の公開版（2026.10.11）
srv = subprocess.Popen(['python3', '-m', 'http.server', '8766', '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
form = {"venue":"大井","date":"2026-10-10","r":"8","dist":"1400","surface":"ダ","baba":"稍重","n":"14","s1":"41.3","s5":"58.2","s10":"84.0",
 "rows":[{"no":no,"tan":str(t),"fuku":f} for no,t,f in [(1,12.4,'3.0-4.6'),(2,4.1,'1.6-2.2'),(3,31.5,'6.1-9.8'),(4,9.8,'2.6-3.9'),(5,18.2,'4.0-6.2'),(6,2.4,'1.1-1.3'),(7,7.6,'2.1-3.1'),(8,54.0,'9.4-15.0'),(9,25.9,'5.2-8.1'),(10,6.3,'1.9-2.7'),(11,14.7,'3.3-5.1'),(12,88.6,'13.2-21.1'),(13,40.2,'7.7-12.2'),(14,120.5,'18.4-29.6')]]}
errs = []
def st(pg):
    return pg.evaluate("""async () => { await TengelLocal.ready; const L = TengelLocal.slots;
      return { app: window.__APP_VER, bets: TengelLocal.mem.bets.size, active: L ? L.active() : 'n/a', slots: L ? L.info().map(s => `${s.n}:${s.name}:${s.count}/${s.usable}${s.active ? '*' : ''}`).join(' ') : 'n/a',
        pill: document.querySelector('#dbpill').textContent, zonesB: ((await TengelLocal.getSetting('zones')) || {}).B ? 'custom' : 'default' } }""")
def chips(pg, sel):
    return [x.inner_text().replace('\n', ' ') for x in pg.locator(sel + ' .slotchip').all()]
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, accept_downloads=True)
        pg = ctx.new_page()
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' and 'fonts.g' not in m.text and 'ERR_' not in m.text else None)
        ctx.add_init_script("if (!sessionStorage.getItem('seeded')) { localStorage.setItem('tengel.form', %s); sessionStorage.setItem('seeded', '1'); }" % json.dumps(json.dumps(form, ensure_ascii=False)))
        pg.goto(URL); pg.wait_for_timeout(1500); pg.reload(); pg.wait_for_timeout(1500)
        # 今の公開版で：記録1件・B層の買い目をカスタム・大井をExcelで284走に
        card = pg.locator('#recCard'); card.locator('[data-k=stake]').fill('1000'); card.locator('[data-k=res]').fill('7-6-2'); card.locator('[data-act=save]').click(); pg.wait_for_timeout(500)
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(300)
        pg.click('#zoneCard [data-zk=B]'); pg.click('#zoneCard [data-zact=add]')
        pg.locator('#zoneCard .zrow').nth(2).locator('.zpick[data-f=b] button[data-z="中穴"]').click(); pg.click('#zoneCard [data-zact=save]'); pg.wait_for_timeout(300)
        pg.set_input_files('#smFile', os.path.join(W, 'xt', 'test_excel_like.xlsx')); pg.wait_for_timeout(1500); pg.click('#smApply'); pg.wait_for_timeout(800)
        print('[0 old app state]', pg.evaluate("({app: window.__APP_VER, bets: TengelLocal.mem.bets.size, races: TengelLocal.mem.races.size})"))
        # 新しい版を公開 → アプリの中の「更新する」
        deploy_dir(build('2026.10.11-2'))
        pg.click('#suCheck'); pg.wait_for_timeout(800)
        with pg.expect_navigation(timeout=15000): pg.click('#updGo')
        pg.wait_for_timeout(2000)
        s1 = st(pg); print('[1 after update]', s1)
        assert s1['app'] == '2026.10.11-2' and s1['bets'] == 1 and s1['active'] == 1 and s1['zonesB'] == 'custom' and s1['slots'].startswith('1:大井競馬:284/272*')
        print('    judge chips:', chips(pg, '#slotJudge'))
        pg.screenshot(path=os.path.join(OUT, 'judge_top.png'))
        # 2つ目にJRAのExcelを入れて使う
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(300)
        pg.screenshot(path=os.path.join(OUT, 'set_slots.png'))
        pg.click('#slotList .slotrow[data-n="2"] [data-sact=edit]'); pg.wait_for_timeout(300)
        print('    edit title:', pg.locator('#seTitle').inner_text())
        pg.set_input_files('#smFile', os.path.join(W, 'xt', 'jra_test.xlsx')); pg.wait_for_timeout(1500)
        print('[2 JRA preview]', pg.locator('#smPreview').inner_text().replace('\n', ' | ')[:240])
        pg.click('#smApply'); pg.wait_for_timeout(800)
        print('    after apply:', pg.locator('#smPreview').inner_text().replace('\n', ' | ')[:160])
        pg.click('#smUse'); pg.wait_for_timeout(600)
        s2 = st(pg); print('[2 JRA in use]', s2)
        assert s2['active'] == 2 and '2:JRA:192/192*' in s2['slots']
        pg.locator('#setMother').screenshot(path=os.path.join(OUT, 'set_slots_jra.png'))
        # 判定：大井のレース → 参考判定（参考値はJRA）。東京にすると地元
        pg.click('.tabbar button[data-tab=judge]'); pg.wait_for_timeout(400)
        print('[3 judge 大井 w/ JRA] chips:', pg.locator('#result .chips').inner_text().replace('\n', ' '), '| zones:', [x.inner_text().replace('\n', '') for x in pg.locator('#result .zflow').all()])
        txt = pg.locator('#outText').text_content(); print('    text:', [l for l in txt.split('\n') if '参考値' in l or 'マザーデータ' in l][:3])
        pg.fill('#fVenue', '東京'); pg.fill('#fDate', '2026-01-03'); pg.select_option('#fR', '5'); pg.wait_for_timeout(500)
        print('[3 judge 東京 w/ JRA] chips:', pg.locator('#result .chips').inner_text().replace('\n', ' '), '| excluded?', pg.locator('#result', has_text='このレース自身は外して').count())
        txt = pg.locator('#outText').text_content(); print('    text:', [l for l in txt.split('\n') if '参考値' in l or 'マザーデータ' in l][:3])
        pg.locator('#result').screenshot(path=os.path.join(OUT, 'judge_jra.png'))
        # 記録を保存（JRAで判定）
        card = pg.locator('#recCard'); card.locator('[data-k=stake]').fill('500'); card.locator('[data-act=save]').click(); pg.wait_for_timeout(500)
        print('    saved bet mother:', pg.evaluate("[...TengelLocal.mem.bets.values()].map(b => (b.snap && b.snap.mother) || '-')"))
        # 実測タブ
        pg.click('.tabbar button[data-tab=stats]'); pg.wait_for_timeout(500)
        print('[4 stats] title:', pg.locator('#motherTitle').inner_text(), '| note:', pg.locator('#motherNote').inner_text()[:80], '| chips:', chips(pg, '#slotStats'))
        print('    ③ A row:', pg.locator('#statsBody table').nth(2).locator('tbody tr').first.inner_text().replace('\t', ' ')[:120])
        print('    review items:', [x.inner_text().split('\n')[0] for x in pg.locator('.pi .pl').all()][-3:])
        pg.screenshot(path=os.path.join(OUT, 'stats_jra.png'))
        # 3つ目：名前を「船橋」にして貼り付けで入れる
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(300)
        pg.click('#slotList .slotrow[data-n="3"] [data-sact=edit]'); pg.wait_for_timeout(300)
        pg.fill('#seName', '船橋'); pg.click('#seNameSave'); pg.wait_for_timeout(400)
        pg.locator('#slotEdit details summary').click(); pg.fill('#smText', open(os.path.join(W, 'xt', 'funabashi_test.tsv'), encoding='utf8').read()); pg.click('#smParse'); pg.wait_for_timeout(300)
        print('[5 船橋 paste preview]', pg.locator('#smPreview').inner_text().replace('\n', ' | ')[:200])
        pg.click('#smApply'); pg.wait_for_timeout(600)
        print('    slots:', st(pg)['slots'])
        # 判定で開催場を船橋に → 切り替えのおすすめ → 切り替える
        pg.click('.tabbar button[data-tab=judge]'); pg.wait_for_timeout(300)
        pg.fill('#fVenue', '船橋'); pg.fill('#fDate', '2026-09-02'); pg.select_option('#fR', '7'); pg.wait_for_timeout(500)
        print('[6 nudge]', pg.locator('#result .banner.info', has_text='開催場が船橋').inner_text().replace('\n', ' ') if pg.locator('#result .banner.info', has_text='開催場が船橋').count() else 'NO NUDGE')
        pg.click('#result .slotchip-go'); pg.wait_for_timeout(700)
        print('    after switch:', st(pg)['slots'], '| chips:', pg.locator('#result .chips').inner_text().replace('\n', ' '), '| excluded?', pg.locator('#result', has_text='このレース自身は外して').count())
        # 開き直しても残る
        pg.reload(); pg.wait_for_timeout(1500)
        s7 = st(pg); print('[7 after reload]', s7)
        assert s7['active'] == 3 and '3:船橋:60/60*' in s7['slots']
        # 使っている3つ目を空にする → 1つ目に戻る
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(300)
        pg.click('#slotList .slotrow[data-n="3"] [data-sact=edit]'); pg.wait_for_timeout(200)
        pg.click('#seClear'); pg.click('#seClear'); pg.wait_for_timeout(600)
        s8 = st(pg); print('[8 cleared 3]', s8)
        assert s8['active'] == 1 and '3:船橋:0/0' in s8['slots']
        # 空のマザーデータは選べない
        pg.click('.tabbar button[data-tab=judge]'); pg.wait_for_timeout(300)
        pg.click('#slotJudge .slotchip[data-slot="3"]'); pg.wait_for_timeout(300)
        print('[9 empty chip] toast:', pg.locator('#toast').inner_text(), '| active:', st(pg)['active'])
        # バックアップ → まっさらなiPhoneで戻す
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(300)
        with pg.expect_download() as dl: pg.click('#pwaBackup')
        bpath = os.path.join(OUT, 'backup.json'); dl.value.save_as(bpath)
        bk = json.load(open(bpath, encoding='utf8'))
        print('[10 backup]', pg.locator('#pwaBkInfo').inner_text(), '| slots:', {k: (v if k != 'data' else {n: len(d['rows']) for n, d in v.items()}) for k, v in bk['slots'].items()}, '| mother rows:', len(bk.get('mother', {}).get('rows', [])))
        ctx2 = b.new_context(viewport={'width': 390, 'height': 844}); p2 = ctx2.new_page(); p2.on('pageerror', lambda e: errs.append('PAGEERR2 ' + str(e)))
        p2.goto(URL); p2.wait_for_timeout(1800)
        print('[10 fresh]', st(p2))
        p2.click('.tabbar button[data-tab=set]'); p2.wait_for_timeout(300); p2.set_input_files('#pwaRestoreFile', bpath); p2.wait_for_timeout(1500)
        print('[10 restored]', p2.locator('#pwaBkInfo').inner_text(), '|', st(p2))
        # さらに新しい版に更新しても、マザーデータ3つはそのまま
        deploy_dir(build('2026.10.12'))
        pg.reload(); pg.wait_for_timeout(2500); pg.reload(); pg.wait_for_timeout(1500)
        print('[11 after next update]', st(pg))
        b.close()
finally:
    srv.terminate()
print('ERRORS:', errs)
