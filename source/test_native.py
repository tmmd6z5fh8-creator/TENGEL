# アプリ版（iPhone・iPadのアプリの中の画面）のテスト。アプリ（Swift）のかわりに、にせもののアプリをつなぐ
#  ・設定タブ：「アプリの版」（更新の確認はしない）・自動バックアップの欄
#  ・記録を保存すると、アプリの中に自動バックアップ（APIキーは入れない）
#  ・バックアップを保存／CSVで保存 → 共有シート（アプリ）に渡す・コピーはアプリへ
#  ・保存場所が消えた（記録0件）のに自動バックアップに記録がある → 「戻す？」→ 戻す／戻さない
#  ・CMの動画は公開中のWeb版から読む
#  ・Web版（ブラウザ）は今までどおり（アプリの印は出ない）
import json, os, shutil, subprocess, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv'); PORT = 8791; BASE = f'http://localhost:{PORT}/TENGEL/'
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'TENGEL')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, HIST='hist_280.json', DROP=''))
idx = os.path.join(SRV, 'TENGEL', 'index.html'); html = open(idx, encoding='utf8').read()
assert "window.__NATIVE = location.protocol === 'tengel:';" in html
# アプリの中（tengel://）のかわりに、別の名前のページをアプリ版として開く
open(os.path.join(SRV, 'TENGEL', 'app.html'), 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
fails, errs = [], []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label)
    if not c:
        fails.append(label)


form = {"venue": "大井", "date": "2026-10-10", "r": "8", "dist": "1400", "surface": "ダ", "baba": "稍重", "n": "14", "s1": "41.3", "s1combo": "6-2-10", "s5": "58.2", "s10": "84.0",
        "rows": [{"no": no, "tan": str(t), "fuku": f} for no, t, f in [(1, 12.4, '3.0-4.6'), (2, 4.1, '1.6-2.2'), (3, 31.5, '6.1-9.8'), (4, 9.8, '2.6-3.9'), (5, 18.2, '4.0-6.2'), (6, 2.4, '1.1-1.3'), (7, 7.6, '2.1-3.1'), (8, 54.0, '9.4-15.0'), (9, 25.9, '5.2-8.1'), (10, 6.3, '1.9-2.7'), (11, 14.7, '3.3-5.1'), (12, 88.6, '13.2-21.1'), (13, 40.2, '7.7-12.2'), (14, 120.5, '18.4-29.6')]]}
# にせもののアプリ：お願い（共有・コピー・バックアップ）を記録して、少しあとに返事をする
FAKE = """
window.__NATIVE_INFO = { version: '1.0', build: '7', device: 'phone' };
window.__bridge = [];
window.webkit = { messageHandlers: { tengel: { postMessage: function (m) {
  window.__bridge.push({ name: m.name, payload: m.payload });
  var P = m.payload, val = true;
  if (m.name === 'backup') window.__saveBackup(P.text);
  if (m.name === 'share') val = !window.__shareCancel;
  setTimeout(function () { window.__nativeReply(m.id, true, val); }, 30);
} } } };
"""
store = {'backup': None, 'writes': 0}
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP')

        def save_backup(source, text):
            store['backup'] = text; store['writes'] += 1
        ctx.expose_binding('__saveBackup', save_backup)
        ctx.route('**/__native/autobackup.json', lambda route: route.fulfill(status=200, content_type='application/json', body=store['backup']) if store['backup'] else route.fulfill(status=404, body='not found'))
        ctx.add_init_script(FAKE)
        ctx.add_init_script("if (!sessionStorage.getItem('seeded')) { localStorage.setItem('tengel.form', %s); sessionStorage.setItem('seeded', '1'); }" % json.dumps(json.dumps(form, ensure_ascii=False)))
        pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(BASE + 'app.html'); pg.wait_for_timeout(1500); pg.reload(); pg.wait_for_timeout(1500)
        st = pg.evaluate("({ native: window.__NATIVE, bridge: !!window.TengelNative, sw: !!(navigator.serviceWorker && navigator.serviceWorker.controller), info: window.TengelNative && window.TengelNative.info })")
        check(st['native'] and st['bridge'] and st['info']['version'] == '1.0', f'アプリ版として動く（{st}）')
        # ---- 設定タブ ----
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(500)
        up = pg.locator('#setUpdate')
        check(up.locator('h2').inner_text() == 'アプリの版' and '1.0（7）' in up.inner_text() and pg.locator('#suCheck').count() == 0, '「アプリの版」：版が出て、更新の確認ボタンはない')
        check('アプリを削除すると' in up.inner_text() and 'ホーム画面のアイコン' not in up.inner_text(), 'アプリを削除すると記録が消える注意')
        check(pg.locator('#sbAuto').count() == 1 and '自動でバックアップ' in pg.locator('#setBackup').inner_text(), 'バックアップに「自動バックアップ」の欄')
        pg.wait_for_timeout(1200)
        check(store['writes'] >= 1, f'開いたら自動バックアップを書く（{store["writes"]}回）')
        bk0 = json.loads(store['backup'] or '{}')
        check(bk0.get('auto') is True and bk0.get('bets') == [], '最初の自動バックアップは記録0件')
        pg.screenshot(path=os.path.join(W, 't4', 'native_set.png'), full_page=False)
        # ---- 記録を保存 → 自動バックアップ ----
        pg.click('.tabbar button[data-tab=judge]'); pg.wait_for_timeout(400)
        card = pg.locator('#recCard')
        card.locator('[data-k=stake][data-t="馬単"]').fill('1800'); card.locator('[data-k=res]').fill('7-6-2'); card.locator('[data-k=payout][data-t="馬単"]').fill('5230')
        pg.wait_for_timeout(200); n0 = store['writes']; card.locator('[data-act=save]').click(); pg.wait_for_timeout(700)
        check(pg.evaluate('TengelLocal.mem.bets.size') == 1, '記録を保存できた')
        check(store['writes'] == n0, 'すぐには書かない（少し待ってまとめて書く）')
        pg.wait_for_timeout(1600)
        bk = json.loads(store['backup'])
        check(store['writes'] == n0 + 1 and len(bk['bets']) == 1 and bk['bets'][0]['id'].startswith('20261010'), f'保存した記録が自動バックアップに入る（{store["writes"] - n0}回）')
        # APIキーはバックアップに入れない
        pg.evaluate("TengelLocal.ocr.save('sk-ant-test-secret-key', 'std')"); pg.wait_for_timeout(1900)
        check('sk-ant-test-secret-key' not in (store['backup'] or ''), 'APIキーは自動バックアップに入らない')
        pg.evaluate("TengelLocal.ocr.clear()")
        # ---- バックアップを保存（共有シート） ----
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(300)
        pg.evaluate('window.__bridge = []')
        pg.click('#pwaBackup'); pg.wait_for_timeout(500)
        sh = [x for x in pg.evaluate('window.__bridge') if x['name'] == 'share']
        check(len(sh) == 1 and sh[0]['payload']['name'].startswith('テンゲル記録_') and sh[0]['payload']['name'].endswith('.json'), 'バックアップを保存 → 共有シートにファイルを渡す')
        shared = json.loads(sh[0]['payload']['text']) if sh else {}
        check(len(shared.get('bets', [])) == 1 and 'sk-ant' not in sh[0]['payload']['text'], 'ファイルの中身（記録1件・APIキーなし）')
        check('記録1件' in pg.locator('#pwaBkInfo').inner_text() and pg.locator('#sbLast').inner_text() != 'まだしてないよ', f'保存したらお知らせ・最後のバックアップ（{pg.locator("#pwaBkInfo").inner_text()}）')
        pg.evaluate('window.__shareCancel = true; window.__bridge = []; document.querySelector("#pwaBkInfo").textContent = ""')
        pg.click('#pwaBackup'); pg.wait_for_timeout(500)
        check(pg.locator('#pwaBkInfo').inner_text() == '', '共有シートを閉じただけなら「保存した」と言わない')
        pg.evaluate('window.__shareCancel = false')
        auto_txt = pg.locator('#sbAuto').inner_text()
        check('記録1件' in auto_txt, f'自動バックアップの欄（{auto_txt}）')
        # ---- CSVで保存・コピー ----
        pg.click('.tabbar button[data-tab=rec]'); pg.wait_for_timeout(500)
        pg.click('#recExportBtn'); pg.wait_for_timeout(300)
        check(pg.locator('#recSave').is_visible(), '記録タブの書き出しに「CSVで保存」が出る')
        pg.evaluate('window.__bridge = []'); pg.click('#recSave'); pg.wait_for_timeout(500)
        sh = [x for x in pg.evaluate('window.__bridge') if x['name'] == 'share']
        check(len(sh) == 1 and sh[0]['payload']['name'].endswith('.csv') and sh[0]['payload']['text'].startswith('﻿日付'), 'CSVで保存 → 共有シートにCSVを渡す')
        pg.evaluate('window.__bridge = []'); pg.click('#recCopy'); pg.wait_for_timeout(400)
        cp = [x for x in pg.evaluate('window.__bridge') if x['name'] == 'copy']
        check(len(cp) == 1 and cp[0]['payload'].startswith('日付') and 'コピーしたよ' in pg.locator('#toast').inner_text(), 'コピー → アプリのクリップボードへ')
        # ---- CM：動画は公開中のWeb版から ----
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(300)
        pg.route('https://tmmd6z5fh8-creator.github.io/**', lambda route: route.fulfill(status=404, body=''))
        pg.locator('#setCM button.btn.primary').click(); pg.wait_for_timeout(300)
        src = pg.locator('#cmModal video').get_attribute('src')
        check(src.startswith('https://tmmd6z5fh8-creator.github.io/TENGEL/cm/tengel3_cm.mp4?v='), f'CMの動画は公開中のWeb版から（{src[:60]}…）')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        # ---- 保存場所が消えた → 「戻す？」 → 戻す ----
        before = store['backup']
        pg.evaluate("new Promise(r => { const q = indexedDB.deleteDatabase('tengel3'); q.onsuccess = q.onerror = q.onblocked = () => r(); })")
        pg.reload(); pg.wait_for_timeout(1500)
        box = pg.locator('#nativeRestore')
        check(box.count() == 1 and '1件' in box.inner_text(), f'記録0件で自動バックアップに記録 → 「戻す？」（{box.inner_text()[:60] if box.count() else "なし"}）')
        pg.screenshot(path=os.path.join(W, 't4', 'native_restore.png'))
        pg.wait_for_timeout(2200)
        check(store['backup'] == before, '聞いている間は自動バックアップを書かない（前の記録を守る）')
        box.locator('[data-nr=yes]').click(); pg.wait_for_timeout(1200)
        check(pg.locator('#nativeRestore').count() == 0 and pg.evaluate('TengelLocal.mem.bets.size') == 1 and '記録1件を戻したよ' in pg.locator('#toast').inner_text(), '「記録を戻す」→ 記録が戻る')
        pg.wait_for_timeout(800)
        check(len(json.loads(store['backup'])['bets']) == 1, '戻したあとも自動バックアップに記録')
        # ---- もう一度消えた → 「戻さない」 ----
        pg.evaluate("new Promise(r => { const q = indexedDB.deleteDatabase('tengel3'); q.onsuccess = q.onerror = q.onblocked = () => r(); })")
        pg.reload(); pg.wait_for_timeout(1500)
        check(pg.locator('#nativeRestore').count() == 1, 'また「戻す？」')
        pg.locator('#nativeRestore [data-nr=no]').click(); pg.wait_for_timeout(1900)
        check(pg.locator('#nativeRestore').count() == 0 and json.loads(store['backup'])['bets'] == [], '「戻さない」→ いまの状態（0件）をバックアップ')
        pg.reload(); pg.wait_for_timeout(1500)
        check(pg.locator('#nativeRestore').count() == 0, 'もう聞かない')
        # ---- Web版（ブラウザ）は今までどおり ----
        ctx2 = b.new_context(viewport={'width': 390, 'height': 844}, locale='ja-JP')
        p2 = ctx2.new_page(); p2.on('pageerror', lambda e: errs.append('WEB ' + str(e)))
        p2.goto(BASE); p2.wait_for_timeout(1500)
        w = p2.evaluate("({ native: window.__NATIVE, bridge: window.TengelNative, dl: null })")
        p2.click('.tabbar button[data-tab=set]'); p2.wait_for_timeout(400)
        check(w['native'] is False and w['bridge'] is None and p2.locator('#suCheck').count() == 1 and p2.locator('#sbAuto').count() == 0 and p2.locator('#setUpdate h2').inner_text() == 'アプリの更新', 'Web版：アプリの印は出ない（更新の確認・バックアップは今までどおり）')
        p2.click('.tabbar button[data-tab=rec]'); p2.wait_for_timeout(300); p2.click('#recExportBtn'); p2.wait_for_timeout(300)
        check(not p2.locator('#recSave').is_visible(), 'Web版：「CSVで保存」は出ない（今までどおり）')
        b.close()
finally:
    srv.terminate()
check(not errs, 'ページのエラーなし' + (f'：{errs[:3]}' if errs else ''))
print('結果：', 'OK' if not fails else f'{len(fails)}件おかしい')
raise SystemExit(1 if fails else 0)
