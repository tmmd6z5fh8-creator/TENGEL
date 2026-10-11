# 着順・組番の入れやすさのテスト（iPhoneの数字キーボードには「-」がない）
#  「.」で区切る → 「-」になる／区切りなし（6211）は頭数から読む／読み方が2つ以上なら区切ってと案内／馬番⇄人気の切り替え／保存／記録タブ／3連単の組番
import os, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv'); PORT = 8770; URL = f'http://localhost:{PORT}/TENGEL/'
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'TENGEL')], check=True, stdout=subprocess.DEVNULL)
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
fails, errs = [], []
def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label)
    if not c: fails.append(label)
try:
    with sync_playwright() as p:
        b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2); pg = ctx.new_page()
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(URL); pg.wait_for_timeout(1500)
        pg.click('#sampleBtn'); pg.wait_for_timeout(300); pg.fill('#fDate', '2026-10-12'); pg.wait_for_timeout(500)   # 14頭のレース（本番扱い）
        card = pg.locator('#recCard'); res = card.locator('[data-k=res]'); hint = card.locator('[data-k=hint]')
        print('[0] 空のときのヒント:', hint.inner_text()); check('「.」で区切って' in hint.inner_text(), '空のときは区切り方を案内')
        print('    placeholder:', res.get_attribute('placeholder'), '| inputmode:', res.get_attribute('inputmode'))
        check(res.get_attribute('inputmode') == 'decimal', '「.」が打てるキーボード（decimal）')
        def typ(s, blur=False):
            res.fill(''); res.press_sequentially(s, delay=20); pg.wait_for_timeout(150)
            if blur: pg.locator('#recCard h2').click(); pg.wait_for_timeout(200)
            return res.input_value(), hint.inner_text()
        v, h = typ('6.2.11'); print('[1] 6.2.11 →', v, '|', h); check(v == '6-2-11' and '番人気' in h, '「.」が「-」になる')
        v, h = typ('6 2 11'); print('    6 2 11 →', v); check(v == '6-2-11', '空白も「-」になる')
        v, h = typ('６．２．１１'); print('    全角 →', v); check(v == '6-2-11', '全角の数字と「．」も直る')
        v, h = typ('6211'); print('[2] 6211（打っている間）→', v, '|', h); check('「6-2-11」と読んだよ' in h, '区切りなし6211を6-2-11と読む')
        v, h = typ('6211', blur=True); print('    欄を離れたら →', v); check(v == '6-2-11', '欄を離れると6-2-11に直る')
        v, h = typ('1012', blur=True); print('    1012 →', v, '|', h); check(v == '10-1-2', '1012は10-1-2（14頭）')
        v, h = typ('625', blur=True); print('    625 →', v); check(v == '6-2-5', '625は6-2-5')
        v, h = typ('1112'); print('[3] 1112 →', v, '|', h); check('区切りがないと読み方がいくつか' in h, '1112は読み方が2つ→区切ってと案内')
        v, h = typ('1112', blur=True); check(v == '1112', '読み方がわからないときは勝手に直さない')
        v, h = typ('6.2.'); pg.locator('#recCard h2').click(); pg.wait_for_timeout(200); v = res.input_value(); print('    6.2. →', v); check(v == '6-2', '最後の区切りは離れたら消す')
        # 馬番 → 人気に切り替え
        typ('6.2.11')
        card.locator('[data-k=mode] button[data-v=nin]').click(); pg.wait_for_timeout(300)
        print('[4] 人気に切り替え →', res.input_value(), '| placeholder', res.get_attribute('placeholder'))
        check(res.input_value().count('-') == 2 and res.get_attribute('placeholder') == '例 1.4.2', '人気に切り替えても「-」区切り')
        card.locator('[data-k=mode] button[data-v=no]').click(); pg.wait_for_timeout(300)
        check(res.input_value() == '6-2-11', '馬番に戻すと6-2-11')
        # 保存（区切りなしのまま保存しても正しく入る）
        typ('762'); card.locator('[data-k=stake]').fill('1000'); card.locator('[data-k=payout]').fill('0')
        card.locator('[data-act=save]').click(); pg.wait_for_timeout(700)
        bet = pg.evaluate("[...TengelLocal.mem.bets.values()][0]")
        print('[5] 保存:', {k: bet.get(k) for k in ('n1', 'n2', 'n3', 'p1', 'p2', 'p3')} if bet else None)
        check(bet and (bet['n1'], bet['n2'], bet['n3']) == (7, 6, 2), '762のまま保存しても7-6-2で入る')
        # 記録タブで直す
        pg.click('.tabbar button[data-tab=rec]'); pg.wait_for_timeout(500)
        pg.locator('#recList .lmain').first.click(); pg.wait_for_timeout(400)
        r2 = pg.locator('#recList .recf [data-k=res]'); print('[6] 記録タブの欄:', r2.input_value(), r2.get_attribute('inputmode'))
        r2.fill(''); r2.press_sequentially('2.7.1', delay=20); pg.wait_for_timeout(200)
        check(r2.input_value() == '2-7-1', '記録タブでも「.」が「-」になる')
        pg.locator('#recList .recf [data-act=save]').click(); pg.wait_for_timeout(700)
        bet = pg.evaluate("[...TengelLocal.mem.bets.values()][0]")
        check(bet and (bet['n1'], bet['n2'], bet['n3']) == (2, 7, 1), '記録タブで直した着順が保存された')
        # 3連単の組番
        pg.click('.tabbar button[data-tab=judge]'); pg.wait_for_timeout(300)
        c1 = pg.locator('#fS1c'); c1.fill(''); c1.press_sequentially('3.1.5', delay=20); pg.wait_for_timeout(300)
        f = pg.evaluate("JSON.parse(localStorage.getItem('tengel.form')).s1combo")
        print('[7] 組番 3.1.5 →', c1.input_value(), '| 保存', f); check(c1.input_value() == '3-1-5' and f == '3-1-5', '組番も「.」が「-」になって入る')
        c5 = pg.locator('#fS5c'); c5.fill(''); c5.press_sequentially('6210', delay=20); pg.locator('#fS10').click(); pg.wait_for_timeout(300)
        f = pg.evaluate("JSON.parse(localStorage.getItem('tengel.form')).s5combo")
        print('    組番 6210 →', c5.input_value(), '| 保存', f); check(c5.input_value() == '6-2-10' and f == '6-2-10', '組番の区切りなしも離れたら直る')
        pg.locator('#recCard').screenshot(path=os.path.join(W, 't5', 'input_res.png'))
        check(not errs, 'ページのエラーなし ' + str(errs))
finally:
    srv.terminate()
print('\nFAILS:', fails); sys.exit(1 if fails else 0)
