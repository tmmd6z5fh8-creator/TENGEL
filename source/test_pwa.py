import json, os, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv'); APPDIR = os.path.join(SRV, 'TENGEL'); OUT = os.path.join(W, 't4'); os.makedirs(OUT, exist_ok=True)
URL = 'http://localhost:8765/TENGEL/'
def deploy_dir(src):
    shutil.rmtree(APPDIR, ignore_errors=True); shutil.copytree(src, APPDIR, ignore=shutil.ignore_patterns('.git', 'README.md', 'source'))
def build(app_ver, mother_ver='2026-10-07', hist='hist.json', out='pwa_t'):
    env = dict(os.environ, APP_VER=app_ver, MOTHER_VER=mother_ver, HIST=hist)
    subprocess.run(['python3', 'build_pwa.py', out], check=True, env=env, stdout=subprocess.DEVNULL)
    return out
# 1) いま公開中の版（GitHubのgh-pages）を、localhostでもService Workerが動くようにして置く
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
deploy_dir(os.environ.get('OLD_APP', os.path.dirname(W)))
old = open(os.path.join(APPDIR, 'index.html'), encoding='utf8').read()
assert "location.protocol === 'https:'" in old
open(os.path.join(APPDIR, 'index.html'), 'w', encoding='utf8').write(old.replace("location.protocol === 'https:'", "(location.protocol === 'https:' || location.hostname === 'localhost')"))
srv = subprocess.Popen(['python3', '-m', 'http.server', '8765', '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(0.8)
form = {"venue":"大井","date":"2026-10-10","r":"8","dist":"1400","surface":"ダ","baba":"稍重","n":"14","s1":"41.3","s1combo":"6-2-10","s5":"58.2","s10":"84.0",
 "rows":[{"no":no,"tan":str(t),"fuku":f} for no,t,f in [(1,12.4,'3.0-4.6'),(2,4.1,'1.6-2.2'),(3,31.5,'6.1-9.8'),(4,9.8,'2.6-3.9'),(5,18.2,'4.0-6.2'),(6,2.4,'1.1-1.3'),(7,7.6,'2.1-3.1'),(8,54.0,'9.4-15.0'),(9,25.9,'5.2-8.1'),(10,6.3,'1.9-2.7'),(11,14.7,'3.3-5.1'),(12,88.6,'13.2-21.1'),(13,40.2,'7.7-12.2'),(14,120.5,'18.4-29.6')]]}
errs = []
def ev(pg, js): return pg.evaluate(js)
def state(pg):
    return ev(pg, """async () => { await TengelLocal.ready; const m = await TengelLocal.motherMeta(); const z = TengelLocal.getSetting ? await TengelLocal.getSetting('zones') : 'n/a';
      return { app: window.__APP_VER || '(old)', bets: TengelLocal.mem.bets.size, races: TengelLocal.mem.races.size, src: m && (m.source || m.ver), emb: m && m.embedded,
        zonesB: z && z !== 'n/a' ? (z.B || []).map(r => r.a + '→' + r.b.join('/')).join(',') : String(z), sw: navigator.serviceWorker.controller ? navigator.serviceWorker.controller.scriptURL.split('/').pop() : null,
        caches: (await caches.keys()).join(','), ver: document.querySelector('.brand .ver').textContent } }""")
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, accept_downloads=True)
        pg = ctx.new_page()
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
        pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' and 'fonts.g' not in m.text and 'ERR_' not in m.text else None)
        ctx.add_init_script("if (!sessionStorage.getItem('seeded')) { localStorage.setItem('tengel.form', %s); sessionStorage.setItem('seeded', '1'); }" % json.dumps(json.dumps(form, ensure_ascii=False)))
        pg.goto(URL); pg.wait_for_timeout(1500); pg.reload(); pg.wait_for_timeout(1500)
        print('[1 old app]', state(pg))
        card = pg.locator('#recCard')
        card.locator('[data-k=types] button[data-v="3連単"]').click()
        card.locator('[data-k=stake]').fill('1800'); card.locator('[data-k=res]').fill('7-6-2'); card.locator('[data-k=payout]').fill('5230')
        pg.wait_for_timeout(200); card.locator('[data-act=save]').click(); pg.wait_for_timeout(700)
        print('[1 saved bet]', state(pg)['bets'])
        # 2) 新しい版（今回の設定タブ入り）を公開 → アプリを開き直す
        deploy_dir(build('2026.10.11'))
        pg.reload(); pg.wait_for_timeout(2500); pg.reload(); pg.wait_for_timeout(1500)
        s2 = state(pg); print('[2 after update]', s2)
        assert s2['app'] == '2026.10.11' and s2['bets'] == 1 and s2['races'] == 280
        # 3) 買い目編集：B層に 人気→中穴（3着 人気・中穴）を足して保存 → localStorageを消して開き直しても残る
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(300)
        pg.screenshot(path=os.path.join(OUT, 'set_top.png'))
        pg.click('#zoneCard [data-zk=B]'); pg.click('#zoneCard [data-zact=add]')
        r3 = lambda: pg.locator('#zoneCard .zrow').nth(2)
        r3().locator('.zpick[data-f=b] button[data-z="中穴"]').click(); r3().locator('.zpick[data-f=t] button[data-z="人気"]').click(); r3().locator('.zpick[data-f=t] button[data-z="中穴"]').click()
        pg.click('#zoneCard [data-zact=save]'); pg.wait_for_timeout(500)
        ev(pg, "localStorage.removeItem('tengel.zones')")
        pg.reload(); pg.wait_for_timeout(1500)
        s3 = state(pg); print('[3 zones after reload]', s3['zonesB'], '|', s3['ver'])
        print('    judge zones:', [x.inner_text().replace('\n', ' ') for x in pg.locator('#result .zflow').all()])
        # 4) Excelファイルから基盤データを入れ替える
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(300)
        for f in ['test_13.xlsx', 'test_textdates.xlsx']:
            pg.set_input_files('#smFile', os.path.join(W, 'xt', f)); pg.wait_for_timeout(1500)
            print(f'[4 preview {f}]', pg.locator('#smPreview').inner_text().replace('\n', ' | ')[:220])
            pg.click('#smCancel')
        pg.set_input_files('#smFile', os.path.join(W, 'xt', 'test_excel_like.xlsx')); pg.wait_for_timeout(1500)
        print('[4 preview excel_like]', pg.locator('#smPreview').inner_text().replace('\n', ' | ')[:260])
        pg.locator('#setMother').screenshot(path=os.path.join(OUT, 'mother_preview.png'))
        pg.click('#smApply'); pg.wait_for_timeout(1000)
        print('[4 applied]', pg.locator('#smMeta').inner_text().replace('\n', ' '), '| pill:', pg.locator('#dbpill').inner_text())
        chk = ev(pg, """() => { const r = TengelLocal.mem.races; const a = r.get('20261008-oi-01'), c = r.get('20261008-oi-03'), s = r.get('20260720-oi-01'), f = r.get('20260720-oi-12'); return { a, c3: c && c.p3, sBaba: s && s.baba, fBaba: f && f.baba, bad: [...r.values()].filter(x => !['良','稍重','重','不良'].includes(x.baba)).length, n0: [...r.values()].filter(x => x.cnt === 0).length } }""")
        print('    check rows:', chk)
        # 貼り付けでも読める
        tsv = '\n'.join(['日付\tR\t馬場', '2026/10/08\t1\t良\t1200\t12\t2.1\t18.5\t1\t3\t2', '10/08\t2\t稍重\t1400\t14\t1.8\t25\t4\t1\t3', '2026/10/08\tx\t良'])
        pg.locator('#setMother details summary').click(); pg.fill('#smText', tsv); pg.click('#smParse'); pg.wait_for_timeout(300)
        print('[4 paste preview]', pg.locator('#smPreview').inner_text().replace('\n', ' | ')[:200]); pg.click('#smCancel')
        pg.reload(); pg.wait_for_timeout(1500)
        s4 = state(pg); print('[4 after reload]', s4['races'], s4['src'])
        assert s4['races'] == 284 and s4['src'] == 'excel'
        # 5) さらに新しい版（基盤データは同じ）を公開 → アプリの中の「確認」→「更新する」
        deploy_dir(build('2026.10.11-2'))
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(300)
        pg.click('#suCheck'); pg.wait_for_timeout(800)
        print('[5 check]', pg.locator('#suMsg').inner_text(), '| bar:', pg.locator('#updBar').inner_text().replace('\n', ' ') if pg.locator('#updBar').count() else None)
        pg.screenshot(path=os.path.join(OUT, 'update_bar.png'))
        with pg.expect_navigation(timeout=15000): pg.click('#updGo')
        pg.wait_for_timeout(2000)
        s5 = state(pg); print('[5 after in-app update]', s5)
        assert s5['app'] == '2026.10.11-2' and s5['bets'] == 1 and s5['races'] == 284 and '人気→中穴' in s5['zonesB']
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(300); pg.click('#suCheck'); pg.wait_for_timeout(800)
        print('    re-check:', pg.locator('#suMsg').inner_text())
        # 6) アプリの更新で、アプリの中の基盤データが古い版のまま（版名だけ変わる）→ Excelで入れた284走を残す
        deploy_dir(build('2026.10.12', mother_ver='2026-10-07b'))
        pg.reload(); pg.wait_for_timeout(2500); pg.reload(); pg.wait_for_timeout(1500)
        s6 = state(pg); print('[6 older embedded]', s6['app'], s6['races'], s6['src'], s6['emb'])
        assert s6['races'] == 284 and s6['src'] == 'excel'
        # 7) アプリの中の基盤データのほうが新しい（10/9まで290走）→ 入れ替わってお知らせ
        h = json.load(open('hist.json', encoding='utf8'))
        add = [dict(id='20261008-oi-%02d' % r, date='2026-10-08', venue='大井', r=r, baba='良', dist=1200, surface='ダ', n=12, tan1=2.0, s1=20.0, p1=1, p2=2, p3=3, cnt=1, note='') for r in range(1, 5)]
        add += [dict(id='20261009-oi-%02d' % r, date='2026-10-09', venue='大井', r=r, baba='良', dist=1200, surface='ダ', n=12, tan1=2.0, s1=20.0, p1=1, p2=2, p3=3, cnt=1, note='') for r in range(1, 7)]
        json.dump(h + add, open(os.path.join(W, 'hist_test.json'), 'w', encoding='utf8'), ensure_ascii=False)
        deploy_dir(build('2026.10.13', mother_ver='2026-10-09', hist='hist_test.json'))
        pg.reload(); pg.wait_for_timeout(2500); pg.reload(); pg.wait_for_timeout(600)
        toast_txt = pg.locator('#toast').inner_text() if pg.locator('#toast').is_visible() else ''
        pg.wait_for_timeout(1000)
        s7 = state(pg); print('[7 newer embedded]', s7['app'], s7['races'], s7['src'], '| bets', s7['bets'], '| toast:', toast_txt)
        assert s7['races'] == 290 and s7['src'] == 'app' and s7['bets'] == 1
        # 8) バックアップを保存 → まっさらなiPhone（新しい保存領域）で戻す
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(300)
        with pg.expect_download() as dl: pg.click('#pwaBackup')
        bpath = os.path.join(OUT, 'backup.json'); dl.value.save_as(bpath)
        bk = json.load(open(bpath, encoding='utf8')); print('[8 backup]', {k: (len(v) if isinstance(v, list) else v) for k, v in bk.items() if k != 'settings'}, '| zones B:', [r['a'] + '→' + '/'.join(r['b']) for r in bk['settings']['zones']['B']])
        print('    last backup:', pg.locator('#sbLast').inner_text(), '|', pg.locator('#pwaBkInfo').inner_text())
        pg.screenshot(path=os.path.join(OUT, 'set_full.png'), full_page=True)
        ctx2 = b.new_context(viewport={'width': 390, 'height': 844})
        p2 = ctx2.new_page(); p2.on('pageerror', lambda e: errs.append('PAGEERR2 ' + str(e)))
        p2.goto(URL); p2.wait_for_timeout(1800)
        print('[8 fresh phone]', state(p2))
        p2.click('.tabbar button[data-tab=set]'); p2.wait_for_timeout(300)
        p2.set_input_files('#pwaRestoreFile', bpath); p2.wait_for_timeout(1200)
        print('[8 restored]', p2.locator('#pwaBkInfo').inner_text(), '|', state(p2))
        p2.click('.tabbar button[data-tab=judge]'); p2.wait_for_timeout(300)
        print('    judge zones on restored:', [x.inner_text().replace('\n', ' ') for x in p2.locator('#result .zflow').all()])
        b.close()
finally:
    srv.terminate()
print('ERRORS:', errs)
