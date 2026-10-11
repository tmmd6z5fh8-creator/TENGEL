import json, os, shutil, sys
out = sys.argv[1] if len(sys.argv) > 1 else 'pwa'
# 出力先はまるごと作り直すので、gitの作業フォルダ（.gitがある所）は指定させない
if os.path.exists(os.path.join(out, '.git')): sys.exit('出力先にgitの作業フォルダは指定できないよ（一時フォルダに作ってからコピーしてね）')
shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
page = open('tengel3.html', encoding='utf8').read()
hist = json.load(open(os.environ.get('HIST', 'hist.json'), encoding='utf8'))
# アプリの版：アプリを直したら上げる（iPhoneの「新しい版があるよ」のお知らせに使う）
APP_VER = os.environ.get('APP_VER', '2026.10.11-7')
# アプリに入れておく基盤データの版：Excelから入れ直したら上げる
MOTHER_VER = os.environ.get('MOTHER_VER', '2026-10-09b')
# 重複転記などで消したレース（dropped.json）。iPhoneの中の大井データに残っていたら消す・Excelで入れても入れない（DROP= で無し）
_dp = os.environ.get('DROP', 'dropped.json')
DROP_IDS = [g['date'].replace('-', '') + '-oi-%02d' % r for g in json.load(open(_dp, encoding='utf8')) for r in g['rs']] if _dp else []
# 文言をiPhoneアプリ版に
rep = [
 ("`まさちゃんのExcel（検証データ）から入れた${motherName()}のデータ：", "`このiPhoneに入っている${motherName()}のデータ："),
 ("Excelを更新したら姫に送ってね、入れ直すよ。`", "Excelを更新したら「設定」タブの「マザーデータ」から入れ替えてね（姫に送ってくれてもOK）。`"),
 ("Claudeの画面でこのアプリを開くと、買ったレースの記録が使えるよ。", "アプリを開き直してね。"),
 ("この画面ではデータに接続できないよ。claude.aiでアプリを開いてね", "データが読み込めなかったよ。アプリを開き直してね"),
]
for a, b in rep:
    assert a in page, a; page = page.replace(a, b)
page = page.replace('claude.aiのアプリ画面で開いてね', 'アプリを開き直してね')
mother = [{k: v for k, v in r.items()} for r in hist]
ICONS = ('icon3-180.png', 'icon3-192.png', 'icon3-512.png', 'icon3-maskable-512.png')
head = f'''<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default"><meta name="apple-mobile-web-app-title" content="テンゲルⅢ">
<meta name="theme-color" content="#16203D"><link rel="manifest" href="manifest.webmanifest"><link rel="apple-touch-icon" href="icon3-180.png"><link rel="icon" href="icon3-192.png">
<style>:root{{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}body{{margin:0;font-size:14px;-webkit-tap-highlight-color:transparent}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
<script>window.__APP_VER={json.dumps(APP_VER)};window.__MOTHER_VER={json.dumps(MOTHER_VER)};window.__MOTHER={json.dumps(mother, ensure_ascii=False)};window.__MOTHER_DROP={json.dumps(DROP_IDS)};</script>
<script>
{open('pwa_shim.js', encoding='utf8').read()}
</script></head><body>
'''
html = head + page + '\n<script>\n' + open('pwa_ui.js', encoding='utf8').read() + '\n</script>\n</body></html>\n'
open(f'{out}/index.html', 'w', encoding='utf8').write(html)
json.dump({"name": "テンゲルⅢ", "short_name": "テンゲルⅢ", "start_url": "./", "scope": "./", "display": "standalone", "background_color": "#16203D", "theme_color": "#16203D", "lang": "ja",
  "icons": [{"src": "icon3-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "icon3-512.png", "sizes": "512x512", "type": "image/png"}, {"src": "icon3-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]},
  open(f'{out}/manifest.webmanifest', 'w', encoding='utf8'), ensure_ascii=False, indent=1)
# 新しい版があるかの確認用（アプリはこのファイルだけを毎回ネットから読む）
json.dump({"app": APP_VER, "mother": MOTHER_VER}, open(f'{out}/version.json', 'w', encoding='utf8'))
open(f'{out}/sw.js', 'w', encoding='utf8').write('''// テンゲルⅢ：電波がなくても開けるようにする。ネットにつながったら、いつも最新の版を読む
// （記録・買い目・基盤データはiPhoneの中のデータベースにあって、ここでは触らない）
const CACHE = 'tengel3-''' + APP_VER + '-' + MOTHER_VER + '''';
const SHELL = ['./', './index.html', './manifest.webmanifest', ''' + ', '.join("'./%s'" % f for f in ICONS) + '''];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL.map(u => new Request(u, { cache: 'reload' })))).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const u = new URL(e.request.url);
  if (u.origin === location.origin && u.pathname.endsWith('/version.json')) return; // 更新の確認は毎回ネットへ
  if (e.request.mode === 'navigate') {
    e.respondWith(fetch(u.href, { cache: 'no-cache', credentials: 'same-origin' }).then(r => { if (r.ok) { const c = r.clone(); caches.open(CACHE).then(x => x.put('./index.html', c)); } return r; })
      .catch(() => caches.match('./index.html').then(h => h || caches.match('./'))));
    return;
  }
  if (u.origin === location.origin || /fonts\\.(googleapis|gstatic)\\.com$/.test(u.hostname)) {
    e.respondWith(caches.match(e.request).then(hit => hit || fetch(e.request).then(r => { if (r.ok || r.type === 'opaque') { const c = r.clone(); caches.open(CACHE).then(x => x.put(e.request, c)); } return r; })));
  }
});
''')
# アイコン：まさちゃんのエンブレム＋金の「TENGER」（icons/ に作ってある）
for f in ICONS:
    shutil.copy(f'icons/{f}', f'{out}/{f}')
print('built', out, sorted(os.listdir(out)), len(html), 'APP_VER', APP_VER, 'MOTHER_VER', MOTHER_VER)
