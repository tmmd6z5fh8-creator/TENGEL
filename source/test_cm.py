# CM（紹介動画）のテスト（iPhoneアプリ版）
#  設定タブの説明書の下に「テンゲルのCM」・押すと全画面で動画・×／外側／Escで閉じる
#  動画はしまわない（大きいので。iPhoneが少しずつ読むのをじゃましない）・表紙はしまう・電波がないときはお知らせ
import os, shutil, subprocess, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv'); PORT = 8782; BASE = f'http://localhost:{PORT}/TENGEL/'
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'TENGEL')], check=True, stdout=subprocess.DEVNULL)
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
fails, errs = [], []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label)
    if not c:
        fails.append(label)


try:
    with sync_playwright() as p:
        b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP')
        pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(BASE); pg.wait_for_timeout(1800)
        CM = pg.evaluate('window.__CM')
        check(bool(CM) and CM['src'].startswith('cm/tengel3_cm.mp4?v=') and CM['poster'].startswith('cm/poster.jpg?v='), 'CMの動画と表紙の場所（版つき）')
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(700)
        ids = pg.evaluate("[...document.querySelectorAll('#v-set > .card')].slice(0, 3).map(c => c.id)")
        check(ids[:2] == ['setManual', 'setCM'], f'設定タブ：説明書のすぐ下に「テンゲルのCM」（{ids}）')
        c = pg.locator('#setCM')
        check(c.locator('h2').inner_text() == 'テンゲルのCM' and c.locator('button.btn.primary[data-cm=play]').inner_text().strip() == '▶ CMを見る', '見出しと「▶ CMを見る」')
        pg.wait_for_function("document.querySelector('#setCM .cmthumb img').complete")
        check(pg.evaluate("document.querySelector('#setCM .cmthumb img').naturalWidth") > 0, '表紙の絵が出る')
        bx = c.bounding_box(); z = pg.locator('#zoneCard').bounding_box(); m = pg.locator('#setManual').bounding_box()
        check(bx['y'] >= m['y'] + m['height'] + 8 and z['y'] >= bx['y'] + bx['height'] + 8 and bx['x'] + bx['width'] <= 390, 'カードが重ならない・はみ出さない')
        # ---- 開く・閉じる ----
        c.locator('button.btn.primary').click(); pg.wait_for_timeout(400)
        md = pg.locator('#cmModal'); v = md.locator('video')
        check(md.count() == 1 and md.is_visible(), '押すと全画面で開く')
        check(v.get_attribute('src') == CM['src'] and v.get_attribute('playsinline') is not None and v.get_attribute('controls') is not None, '動画（その場で再生・操作ボタンつき）')
        vb = v.bounding_box()
        check(vb['width'] <= 390 and vb['y'] >= 50, f'動画が画面に収まる（{round(vb["width"])}×{round(vb["height"])}）')
        check(pg.evaluate("document.activeElement && document.activeElement.classList.contains('cmclose')"), '閉じるボタンにフォーカス')
        check(pg.evaluate('document.documentElement.style.overflow') == 'hidden', '開いている間はうしろが動かない')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        check(pg.locator('#cmModal').count() == 0 and pg.evaluate('document.documentElement.style.overflow') == '', 'Escで閉じる（もとに戻る）')
        c.locator('.cmthumb').click(); pg.wait_for_timeout(300)
        check(pg.locator('#cmModal').count() == 1, '表紙の絵を押しても開く')
        pg.locator('#cmModal .cmclose').click(); pg.wait_for_timeout(200)
        check(pg.locator('#cmModal').count() == 0, '×で閉じる')
        c.locator('button.btn.primary').click(); pg.wait_for_timeout(300)
        pg.mouse.click(4, 420); pg.wait_for_timeout(200)   # 動画のまわりの黒いところ
        check(pg.locator('#cmModal').count() == 0, '動画の外側を押すと閉じる')
        # ---- しまう／しまわない ----
        pg.wait_for_function('navigator.serviceWorker && navigator.serviceWorker.controller', timeout=15000)
        sw = pg.evaluate("fetch('sw.js').then(r => r.text())")
        check('/cm\\/[^/]+\\.mp4$/' in sw, 'サービスワーカー：CMの動画はしまわない')
        res = pg.evaluate("""async (src) => { const r = await fetch(src); const ok = r.ok; await r.body.cancel();
          const keys = await caches.keys(); let hit = false; for (const k of keys) if (await (await caches.open(k)).match(src)) hit = true; return { ok, hit }; }""", CM['src'])
        check(res['ok'] and not res['hit'], '動画は読めて、iPhoneにはしまわない')
        check(pg.evaluate("(p) => caches.match(p).then(h => !!h)", CM['poster']), '表紙はしまう（電波がなくても出る）')
        # ---- 電波がないとき ----
        ctx.set_offline(True)
        pg.reload(); pg.wait_for_timeout(1500)
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(500)
        pg.wait_for_function("document.querySelector('#setCM .cmthumb img') && document.querySelector('#setCM .cmthumb img').complete")
        check(pg.evaluate("document.querySelector('#setCM .cmthumb img').naturalWidth") > 0, '電波がなくても表紙が出る')
        pg.locator('#setCM button.btn.primary').click(); pg.wait_for_timeout(300)
        check(pg.locator('#cmModal').count() == 0 and 'CMは電波があるときに見られるよ' in pg.locator('#toast').inner_text(), '電波がないときは「電波があるときに見られるよ」')
        ctx.set_offline(False)
        b.close()
finally:
    srv.terminate()
check(not errs, 'ページのエラーなし' + (f'：{errs[:2]}' if errs else ''))
print('結果：', 'OK' if not fails else f'{len(fails)}件おかしい')
raise SystemExit(1 if fails else 0)
