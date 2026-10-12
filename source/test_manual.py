# 説明書のテスト（iPhoneアプリ版）
#  アプリの上と設定タブに「説明書」・押すと manual.html・項目を押すと説明・もくじ・アプリに戻る（タブもそのまま）
#  電波がなくても：説明書も写真も開ける・アプリのページは説明書で上書きされない
import json, os, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv'); PORT = 8781; BASE = f'http://localhost:{PORT}/TENGEL/'
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'TENGEL')], check=True, stdout=subprocess.DEVNULL)
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
fails, errs = [], []
def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label)
    if not c: fails.append(label)
try:
    with sync_playwright() as p:
        b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP')
        pg = ctx.new_page()
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(BASE); pg.wait_for_timeout(1800)
        # ---- 入口 ----
        mb = pg.locator('#manBtn')
        check(mb.count() == 1 and mb.is_visible() and mb.get_attribute('href') == 'manual.html', 'アプリの上に「説明書」ボタン')
        br, bb, pl = pg.locator('header .brand').bounding_box(), mb.bounding_box(), pg.locator('#dbpill').bounding_box()
        print('   brand y', round(br['y']), '説明書', round(bb['x']), round(bb['y']), '〜', round(bb['x'] + bb['width']), '／pill y', round(pl['y']))
        check(abs((bb['y'] + bb['height'] / 2) - (br['y'] + br['height'] / 2)) < 12 and bb['x'] + bb['width'] <= 390 - 10, '「説明書」はタイトルの横（はみ出さない）')
        check(pl['y'] > bb['y'] + bb['height'] - 2, '接続の表示は次の段')
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(600)
        first = pg.locator('#v-set > .card').first
        check(first.get_attribute('id') == 'setManual' and first.locator('a[href="manual.html"]').count() == 1, '設定タブの一番上に「説明書を開く」')
        z = pg.locator('#zoneCard').bounding_box(); m = pg.locator('#setManual').bounding_box()
        check(z['y'] >= m['y'] + m['height'] + 8, '説明書のカードと買い目編集が重ならない')
        # ---- 説明書を開く（設定タブから） ----
        pg.locator('#setManual a').click(); pg.wait_for_load_state(); pg.wait_for_timeout(700)
        check(pg.url.endswith('/manual.html') and pg.title() == 'テンゲルⅢ 説明書', '押すと説明書が開く')
        check(pg.locator('#toApp').is_visible() and pg.locator('.mrow').count() == 19, 'もくじ（19項目）と「アプリに戻る」')
        n0 = pg.evaluate('history.length')
        pg.locator('#m-record').click(); pg.wait_for_timeout(400)
        check(pg.locator('#s-record').is_visible() and pg.locator('#back').is_visible() and pg.locator('#closeApp').is_visible(), '項目を押すと説明（もくじ・×）')
        pg.locator('#s-record .pager .next').click(); pg.wait_for_timeout(300)
        check(pg.locator('#s-hit').is_visible(), '次の項目')
        check(pg.evaluate('history.length') == n0, '説明書の中の移動は履歴を増やさない')
        pg.locator('#back').click(); pg.wait_for_timeout(300)
        check(pg.locator('#home').is_visible(), '「もくじ」でもくじ')
        pg.locator('#m-input').click(); pg.wait_for_timeout(300)
        pg.locator('#closeApp').click(); pg.wait_for_timeout(1500)
        check(pg.url.rstrip('/').endswith('/TENGEL') and pg.locator('#v-set').is_visible(), '×でアプリに戻る（設定タブのまま）')
        # ---- 上の「説明書」から開いて戻る ----
        pg.click('.tabbar button[data-tab=win5]'); pg.wait_for_timeout(500)
        pg.locator('#manBtn').click(); pg.wait_for_load_state(); pg.wait_for_timeout(600)
        check(pg.url.endswith('/manual.html'), '上の「説明書」で開く')
        pg.locator('#toApp').click(); pg.wait_for_timeout(1500)
        check(pg.locator('#v-win5').is_visible(), '「アプリに戻る」でWIN5タブに戻る')
        # ---- 直接開いたときの「アプリに戻る」 ----
        pg2 = ctx.new_page(); pg2.on('pageerror', lambda e: errs.append(str(e)))
        pg2.goto(BASE + 'manual.html#glossary'); pg2.wait_for_timeout(700)
        check(pg2.locator('#s-glossary').is_visible(), '#項目つきで開くと、その項目')
        pg2.locator('#closeApp').click(); pg2.wait_for_timeout(1500)
        check(pg2.url.rstrip('/').endswith('/TENGEL') and pg2.locator('#v-judge').count() == 1, '直接開いても「アプリに戻る」でアプリへ')
        pg2.close()
        # ---- 電波がないとき ----
        pg.evaluate("navigator.serviceWorker.ready.then(() => true)"); pg.wait_for_timeout(1500)
        keys = pg.evaluate("caches.keys()"); print('   caches:', keys)
        nman = pg.evaluate("caches.keys().then(ks => ks.find(k => k.startsWith('tengel3-manual-'))).then(k => k ? caches.open(k).then(c => c.keys()).then(r => r.length) : 0)")
        check(nman == 36, f'説明書の写真がしまってある（{nman}枚）')
        ctx.set_offline(True)
        pg.goto(BASE + 'manual.html'); pg.wait_for_timeout(800)
        check(pg.title() == 'テンゲルⅢ 説明書' and pg.locator('.mrow').count() == 19, '電波がなくても説明書が開く')
        pg.locator('#m-input').click(); pg.wait_for_timeout(500)
        im = pg.locator('#s-input img').first; im.scroll_into_view_if_needed(); pg.wait_for_timeout(500)
        check(pg.evaluate("(el) => el.complete && el.naturalWidth > 0", im.element_handle()), '電波がなくても写真が出る')
        pg.goto(BASE); pg.wait_for_timeout(1500)
        check(pg.title() == 'テンゲルⅢ' and pg.locator('#v-judge').count() == 1 and pg.locator('#manBtn').count() == 1, '電波がなくてもアプリが開く（説明書で上書きされない）')
        ctx.set_offline(False)
        b.close()
finally:
    srv.terminate()
check(not errs, 'エラーなし ' + str(errs[:3]))
print('結果：', '全部OK' if not fails else f'{len(fails)}件NG {fails}')
sys.exit(1 if fails else 0)
