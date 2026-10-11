# 「買ったゾーン」を選んで、選んだゾーンだけで当たり外れを判定するテスト（iPhoneアプリ版）
#  A層（第1 人気→人気・第2 人気→中穴）で、買ったのは 人気→中穴 だけ → 人気→人気 の決着は「不的中」
#  ゾーンを選んでいないときは「結果待ち（選んでね）」／3連単は買ったゾーンの3着2本で判定／記録タブで直せる／前の記録（buyZ なし）は推奨ゾーン全部／書き出しに「買ったゾーン」
import json, os, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv'); PORT = 8774; URL = f'http://localhost:{PORT}/TENGEL/'; OUT = os.path.join(W, 't5'); os.makedirs(OUT, exist_ok=True)
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'TENGEL')], check=True, stdout=subprocess.DEVNULL)
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
odds = [1.5, 3.2, 4.8, 6.5, 8.9, 12.1, 15.6, 20.3, 28.4, 35.0, 48.2, 66.0]; nos = [6, 2, 10, 7, 1, 4, 11, 5, 9, 3, 8, 12]
FORM = {"id": None, "venue": "大井", "date": "2026-10-12", "r": "9", "dist": "1400", "surface": "ダ", "baba": "良", "n": "12", "tan1": "", "s1": "9.0", "s1combo": "", "s5": "", "s5combo": "", "s10": "", "s10combo": "",
        "rows": [{"no": no, "tan": str(t), "fuku": ""} for no, t in zip(nos, odds)]}   # 比6.0 → A層
fails, errs = [], []
def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label)
    if not c: fails.append(label)
try:
    with sync_playwright() as p:
        b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2); pg = ctx.new_page()
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.add_init_script("if (!sessionStorage.getItem('x')) { sessionStorage.setItem('x', '1'); localStorage.setItem('tengel.form', %s); }" % json.dumps(json.dumps(FORM)))
        pg.goto(URL); pg.wait_for_timeout(1600)
        card = pg.locator('#recCard'); status = card.locator('[data-k=status]'); res = card.locator('[data-k=res]')
        print('[0] 区分:', pg.locator('#result .vkubun').inner_text().replace('\n', ' '))
        chips = card.locator('[data-k=buyz] button')
        labels = [c.inner_text() for c in chips.all()]; pressed = [c.get_attribute('aria-pressed') for c in chips.all()]
        print('    買ったゾーンのボタン:', labels, pressed)
        check(labels == ['第1　人気→人気', '第2　人気→中穴'] and pressed == ['false', 'false'], 'A層の2ゾーンが出て、最初はどれも選んでいない')
        card.locator('[data-k=mode] button[data-v=nin]').click(); pg.wait_for_timeout(200)
        def typ(s):
            res.fill(''); res.press_sequentially(s, delay=15); pg.wait_for_timeout(250); return status.inner_text().replace('\n', ' ')
        t = typ('1.2.3'); print('[1] 選ぶ前・1-2-3 →', t); check('結果待ち' in t and '買ったゾーンを押して選んでね' in t, 'ゾーンを選ぶ前は「結果待ち（選んでね）」')
        chips.nth(1).click(); pg.wait_for_timeout(250)
        t = status.inner_text().replace('\n', ' '); print('[2] 第2だけ買った・1-2-3 →', t)
        check('不的中' in t and '第1（人気→人気）に入ったけど、買っていないゾーン' in t, '人気→人気の決着は「不的中」（買っていないゾーン）')
        t = typ('1.5.2'); print('[3] 1-5-2 →', t); check('的中' in t and '不的中' not in t and '買ったゾーン第2（人気→中穴）に入った' in t, '人気→中穴の決着は「的中」')
        t = typ('7.1.2'); print('    7-1-2 →', t); check('不的中' in t and '推奨ゾーンの外' in t, 'ゾーン外の決着は「不的中」')
        # 3連単（買ったゾーンの3着2本：人気・中穴）
        card.locator('[data-k=types] button[data-v="3連単"]').click(); card.locator('[data-k=types] button[data-v="馬単"]').click(); pg.wait_for_timeout(200)
        t = typ('1.5.9'); print('[4] 3連単だけ・1-5-9 →', t); check('不的中' in t and '3連単ゾーンは外れ' in t, '3連単：3着が大穴なら外れ')
        t = typ('1.5.2'); print('    1-5-2 →', t); check('的中' in t and '不的中' not in t and '3連単ゾーンも的中' in t, '3連単：3着が人気なら的中')
        chips.nth(1).click(); chips.nth(0).click(); pg.wait_for_timeout(250)   # 第1だけに
        t = status.inner_text().replace('\n', ' '); print('    第1だけ・1-5-2 →', t); check('不的中' in t, '3連単も、買っていないゾーンの決着は「不的中」')
        chips.nth(0).click(); chips.nth(1).click()   # 第2だけに戻す
        card.locator('[data-k=types] button[data-v="馬単"]').click(); card.locator('[data-k=types] button[data-v="3連単"]').click(); pg.wait_for_timeout(200)
        # 保存
        typ('1.5.2'); card.locator('[data-k=stake]').fill('900'); card.locator('[data-k=payout]').fill('2350'); pg.wait_for_timeout(200)
        card.locator('[data-act=save]').click(); pg.wait_for_timeout(800)
        bet = pg.evaluate("TengelLocal.mem.bets.get('20261012-oi-09')")
        print('[5] 保存:', {k: bet.get(k) for k in ('buyZ', 'types', 'p1', 'p2', 'p3', 'stake', 'payout')} if bet else None)
        check(bet and bet['buyZ'] == ['人気→中穴'], '買ったゾーンが保存された（人気→中穴）')
        msg = pg.locator('#toast').inner_text() if pg.locator('#toast').is_visible() else ''
        check('保存できたよ（的中）' in msg, '保存した記録は「的中」 ' + msg)
        pg.locator('#recCard').screenshot(path=os.path.join(OUT, 'buyzone_card.png'))
        # 記録タブ：一覧に買ったゾーン → 開いて第1も足して 1-2-3 に直す
        pg.click('.tabbar button[data-tab=rec]'); pg.wait_for_timeout(500)
        row = pg.locator('#recList .lrow[data-id="20261012-oi-09"]'); s_line = row.locator('.lmid .s').inner_text()
        print('[6] 記録タブ:', s_line, '|', row.locator('.stc').first.inner_text()); check('買った：人気→中穴' in s_line, '一覧に「買った：人気→中穴」')
        row.locator('.lmain').click(); pg.wait_for_timeout(400)
        rch = pg.locator('#recList .recf [data-k=buyz] button')
        check([c.get_attribute('aria-pressed') for c in rch.all()] == ['false', 'true'], '記録タブでも第2だけ押してある')
        rch.nth(0).click(); r2 = pg.locator('#recList .recf [data-k=res]'); r2.fill(''); r2.press_sequentially('1.2.3', delay=15); pg.wait_for_timeout(250)
        print('    第1も足して 1-2-3 →', pg.locator('#recList .recf [data-k=status]').inner_text().replace('\n', ' '))
        pg.locator('#recList .recf [data-act=save]').click(); pg.wait_for_timeout(800)
        bet = pg.evaluate("TengelLocal.mem.bets.get('20261012-oi-09')")
        st9 = pg.locator('#recList .lrow[data-id="20261012-oi-09"] .lend .stc').inner_text()
        check(bet['buyZ'] == ['人気→人気', '人気→中穴'] and st9 == '的中', f'記録タブで直すと、第1・第2を買って 1-2-3 で「的中」（{st9}）')
        # 前の記録（buyZ なし）は推奨ゾーン全部で判定
        pg.evaluate("""async () => { const b = JSON.parse(JSON.stringify(TengelLocal.mem.bets.get('20261012-oi-09'))); delete b.buyZ; delete b.id; b.r = 10; b.p1 = 2; b.p2 = 3; b.p3 = 1; b.n1 = null; b.n2 = null; b.n3 = null;
          const db = await window.claude.use('db'); await db.collection('bets').doc('20261012-oi-10').set(b); }""")
        pg.wait_for_timeout(700)
        row10 = pg.locator('#recList .lrow[data-id="20261012-oi-10"]'); legacy = row10.locator('.lend .stc').inner_text()
        print('[7] 前の記録（buyZなし）:', legacy, '|', row10.locator('.lmid .s').inner_text())
        check(legacy == '的中' and '買った：' not in row10.locator('.lmid .s').inner_text(), '前の記録は推奨ゾーン全部で判定（人気→人気で的中）')
        row10.locator('.lmain').click(); pg.wait_for_timeout(400)
        check([c.get_attribute('aria-pressed') for c in pg.locator('#recList .lrow[data-id="20261012-oi-10"] [data-k=buyz] button').all()] == ['true', 'true'], '前の記録を開くと、ゾーンは全部押してある')
        # 書き出し
        pg.click('#recExportBtn'); pg.wait_for_timeout(300)
        txt = pg.locator('#recExportText').input_value().split('\n')
        print('[8] 書き出し:', txt[0]); print('   ', txt[1]); check('買ったゾーン' in txt[0].split('\t') and '人気→人気・人気→中穴' in txt[1], '書き出しに「買ったゾーン」')
        # ゾーンを選ばずに保存 → 結果待ち（選んでね）
        pg.click('.tabbar button[data-tab=judge]'); pg.wait_for_timeout(300)
        pg.select_option('#fR', '11'); pg.wait_for_timeout(600)
        card = pg.locator('#recCard'); card.locator('[data-k=mode] button[data-v=nin]').click(); r = card.locator('[data-k=res]'); r.fill(''); r.press_sequentially('1.2.3', delay=15); pg.wait_for_timeout(200)
        card.locator('[data-k=stake]').fill('600'); card.locator('[data-act=save]').click(); pg.wait_for_timeout(800)
        msg = pg.locator('#toast').inner_text() if pg.locator('#toast').is_visible() else ''
        print('[9] 選ばずに保存:', msg, '|', pg.evaluate("TengelLocal.mem.bets.get('20261012-oi-11') && TengelLocal.mem.bets.get('20261012-oi-11').buyZ"))
        check('保存できたよ（結果待ち）' in msg and '買ったゾーンを選んでね' in msg and pg.evaluate("TengelLocal.mem.bets.get('20261012-oi-11').buyZ.length") == 0, '選ばずに保存すると「結果待ち・選んでね」')
        # 収支タブ
        pg.click('.tabbar button[data-tab=stats]'); pg.wait_for_timeout(500)
        tile = pg.locator('#moneyBody .tile').first.inner_text().replace('\n', ' '); print('[10] 収支:', tile)
        check('的中2' in tile and '結果待ち1' in tile, '収支：的中2・結果待ち1')
        check(not errs, 'ページのエラーなし ' + str(errs))
finally:
    srv.terminate()
print('\nFAILS:', fails); sys.exit(1 if fails else 0)
