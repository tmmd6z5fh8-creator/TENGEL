import hashlib, importlib.util, json, os, shutil, sys
out = sys.argv[1] if len(sys.argv) > 1 else 'pwa'
HERE = os.path.dirname(os.path.abspath(__file__))
# 作る形：web＝Web版（ホーム画面のアプリ・GitHub Pages）／app＝App Store版のアプリの中身（build_ios.py が使う）
TARGET = os.environ.get('TARGET', 'web')
assert TARGET in ('web', 'app'), TARGET


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


_bm = _load('build_manual', os.path.join(HERE, 'manual', 'build_manual.py'))   # 説明書
_bl = _load('build_legal', os.path.join(HERE, 'legal', 'build_legal.py'))      # このアプリについて・公開するページ
_at = _load('app_target', os.path.join(HERE, 'app_target.py'))                 # App Store版：競馬場・団体・版の名前を出さない
# 出力先はまるごと作り直すので、gitの作業フォルダ（.gitがある所）は指定させない
if os.path.exists(os.path.join(out, '.git')): sys.exit('出力先にgitの作業フォルダは指定できないよ（一時フォルダに作ってからコピーしてね）')
shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
page = open('tengel3.html', encoding='utf8').read()
hist = json.load(open(os.environ.get('HIST', 'hist.json'), encoding='utf8'))
# アプリの版：アプリを直したら上げる（iPhoneの「新しい版があるよ」のお知らせに使う）
APP_VER = os.environ.get('APP_VER', '2026.10.14-2')
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
if TARGET == 'app':
    # App Store版：フォントはアプリの中のものを使う（Google に通信しない）・「姫に送って」「まさちゃんの」はお客さん向けの言い方に
    for a, b in [(_bm.FONTS, _bm.APP_FONTS),
                 ('（姫に送ってくれてもOK）', ''),
                 ('<p class="hint">Excel（検証データ）を更新したら姫に送ってね。アプリの中の基盤データを入れ直すよ。</p>', '<p class="hint">マザーデータは「設定」タブの「マザーデータ」で入れ替えられるよ。</p>'),
                 ('※まさちゃんのカスタム買い目（設定タブで変更）', '※カスタム買い目（設定タブで変更）')]:
        assert a in page, a[:40]; page = page.replace(a, b)
mother = [{k: v for k, v in r.items()} for r in hist]
MOTHER_HOME = None
# データの更新（App Store版がアプリの更新なしで新しいデータを読む）：公開するデータの場所。Web版が data/mother_app.json に置く
DATA_URL = os.environ.get('DATA_URL', 'https://tmmd6z5fh8-creator.github.io/TENGEL/data/mother_app.json')
if TARGET == 'app':
    # App Store版：アプリに入れるデータは開催場の名前を消して「しるし」だけ残す・消したレースの印（DROP）は使わない（入れるデータが別の開催場でも消さないように）
    mother, MOTHER_HOME = _at.mother(mother)
    DROP_IDS = []
ICONS = ('icon3-180.png', 'icon3-192.png', 'icon3-512.png', 'icon3-maskable-512.png')
# CM（紹介動画）：設定タブから見る。cm_media/ にある動画と表紙を cm/ に置く。中身が変わったら ?v= が変わるので古いのは使われない
CM_SRC = os.path.join(HERE, 'cm_media')
CM = None
if os.path.exists(os.path.join(CM_SRC, 'tengel3_cm.mp4')):
    _h = lambda f: hashlib.md5(open(os.path.join(CM_SRC, f), 'rb').read()).hexdigest()[:8]
    CM = {'src': 'cm/tengel3_cm.mp4?v=' + _h('tengel3_cm.mp4'), 'poster': 'cm/poster.jpg?v=' + _h('poster.jpg'), 'dur': '0:45'}
    # App Store版のアプリの中で見せる版（最後の案内がアプリの言い方）。アプリはこれを公開中のWeb版から読む
    if os.path.exists(os.path.join(CM_SRC, 'tengel3_cm_app.mp4')):
        CM['srcApp'] = 'cm/tengel3_cm_app.mp4?v=' + _h('tengel3_cm_app.mp4')
# App Store版だけ：アプリを開いた時の画面（19章）の入れ物を最初から出しておく（画面が一瞬見えないように。中身は points_ui.js）・
# 2本指の拡大はOK・ダブルタップでは拡大しない（touch-action: manipulation）
APP_HEAD = ('<style>body{touch-action:manipulation}#gate{position:fixed;inset:0;z-index:70;background:#16203D;color:#F3F0E6;display:flex;align-items:center;justify-content:center;font-family:"Dela Gothic One","Hiragino Sans",sans-serif;font-size:40px;letter-spacing:.06em}#gate em{font-style:normal;color:#E2A23B;font-family:"Hiragino Sans",sans-serif}</style>'
            if TARGET == 'app' else '')
# App Store版だけ：買い目の組と判定（reserve.js）・買い目カスタムの%（custom_rate.js）。画面（src.html）より先に読む
APP_LIBS = ('\n<script>\n' + open('reserve.js', encoding='utf8').read() + '\n</script>\n<script>\n' + open('custom_rate.js', encoding='utf8').read() + '\n</script>') if TARGET == 'app' else ''
APP_BODY = '<div id="gate" role="dialog" aria-modal="true" aria-label="はじめに">テンゲル<em>Ⅲ</em></div>\n' if TARGET == 'app' else ''
head = f'''<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default"><meta name="apple-mobile-web-app-title" content="テンゲルⅢ">
<meta name="theme-color" content="#16203D"><link rel="manifest" href="manifest.webmanifest"><link rel="apple-touch-icon" href="icon3-180.png"><link rel="icon" href="icon3-192.png">
<style>:root{{color-scheme:light;--sat:max(env(safe-area-inset-top,0px),var(--top-inset,0px));--sab:max(env(safe-area-inset-bottom,0px),var(--bottom-inset,0px));padding-top:var(--sat);padding-bottom:var(--sab)}}body{{margin:0;font-size:14px;-webkit-tap-highlight-color:transparent}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
{APP_HEAD}
<script>window.__APP_VER={json.dumps(APP_VER)};window.__CM={json.dumps(CM)};window.__ABOUT={json.dumps(_bl.about(TARGET), ensure_ascii=False)};window.__MOTHER_VER={json.dumps(MOTHER_VER)};window.__MOTHER={json.dumps(mother, ensure_ascii=False)};window.__MOTHER_DROP={json.dumps(DROP_IDS)};{'window.__MOTHER_HOME=' + json.dumps(MOTHER_HOME) + ';window.__DATA_URL=' + json.dumps(DATA_URL) + ';' if MOTHER_HOME is not None else ''}</script>
<script>
{open('ocr_local.js', encoding='utf8').read()}
</script>{APP_LIBS}
<script>
{open('pwa_shim.js', encoding='utf8').read()}
</script></head><body>
{APP_BODY}'''
html = head + page + '\n<script>\n' + open('pwa_ui.js', encoding='utf8').read() + '\n</script>\n'
if TARGET == 'app':
    # ポイント・Pカスタム・ミッション・アプリを開いた時の画面・拡大（App Store版だけ。Web版の動きは変えない）
    html += '<script>\n' + open('points.js', encoding='utf8').read() + '\n</script>\n<script>\n' + open('points_ui.js', encoding='utf8').read() + '\n</script>\n'
    # 的中ボタン（第3弾）：見本の CSS と HTML（kisekae/gen_fx.py・boards.py）を束ねた window.__FX と、動かす fx.js。絵と音は build_ios.py が Resources/ に入れる（リポジトリには入れない）
    sys.path.insert(0, os.path.join(HERE, 'kisekae'))
    import build_fx as _fx
    html += '<script>\n' + _fx.bundle_js() + '\n</script>\n<script>\n' + open('fx.js', encoding='utf8').read() + '\n</script>\n'
html += '</body></html>\n'
if TARGET == 'app':
    html = _at.app_index(html)   # コメントを消す・競馬場・団体・商標・版の名前を置きかえる・残っていたら止める
open(f'{out}/index.html', 'w', encoding='utf8').write(html)
json.dump({"name": "テンゲルⅢ", "short_name": "テンゲルⅢ", "start_url": "./", "scope": "./", "display": "standalone", "background_color": "#16203D", "theme_color": "#16203D", "lang": "ja",
  "icons": [{"src": "icon3-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "icon3-512.png", "sizes": "512x512", "type": "image/png"}, {"src": "icon3-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]},
  open(f'{out}/manifest.webmanifest', 'w', encoding='utf8'), ensure_ascii=False, indent=1)
# 説明書（manual.html・写真は manual/）。アプリの上の「説明書」と設定タブから開く
MAN_IMGS, MAN_VER = _bm.build('app' if TARGET == 'app' else 'pwa', out, APP_VER, mother=mother)
if TARGET == 'app':
    os.makedirs(f'{out}/fonts')
    for f in _bm.APP_FONT_FILES:
        shutil.copy(os.path.join(HERE, 'ios', 'fonts', f), f'{out}/fonts/{f}')
# 公開するページ（プライバシーポリシー・特定商取引法に基づく表記・サポート）：販売する人の欄（legal/legal.json）が入っているものだけ
LEGAL = _bl.pages(out) if TARGET == 'web' else []
if CM:
    os.makedirs(f'{out}/cm')
    for f in ('tengel3_cm.mp4', 'poster.jpg') + (('tengel3_cm_app.mp4',) if 'srcApp' in CM else ()):
        shutil.copy(os.path.join(CM_SRC, f), f'{out}/cm/{f}')
# 新しい版があるかの確認用（アプリはこのファイルだけを毎回ネットから読む）
json.dump({"app": APP_VER, "mother": MOTHER_VER}, open(f'{out}/version.json', 'w', encoding='utf8'))
# App Store版の「データの更新」で読むデータ（1つ目のマザーデータ）：開催場の名前は消して「しるし」だけ（App Store版に入れるのと同じ形）
if TARGET == 'web':
    _drop = set(DROP_IDS)
    _rows, _home = _at.mother([dict(r) for r in hist if r.get('id') not in _drop])
    _ds = sorted(r['date'] for r in _rows)
    _doc = {'app': 'tengel', 'kind': 'mother', 'ver': MOTHER_VER, 'n': len(_rows), 'first': _ds[0], 'last': _ds[-1], 'home': _home, 'rows': _rows}
    _txt = json.dumps(_doc, ensure_ascii=False, separators=(',', ':'))
    _at.check_clean(_txt, 'データの更新のファイル')
    os.makedirs(f'{out}/data')
    open(f'{out}/data/mother_app.json', 'w', encoding='utf8').write(_txt)
open(f'{out}/sw.js', 'w', encoding='utf8').write('''// テンゲルⅢ：電波がなくても開けるようにする。ネットにつながったら、いつも最新の版を読む
// （記録・買い目・基盤データはiPhoneの中のデータベースにあって、ここでは触らない）
const CACHE = 'tengel3-''' + APP_VER + '-' + MOTHER_VER + '''';
// 説明書の写真は別のしまい場所（写真が変わったときだけ入れ直す。アプリの更新のたびには読まない）
const MCACHE = 'tengel3-manual-''' + MAN_VER + '''';
const SHELL = ['./', './index.html', './manual.html', './manifest.webmanifest', ''' + ', '.join("'./%s'" % f for f in ICONS) + (", './" + CM['poster'] + "'" if CM else '') + '''];
const MANUAL = [''' + ', '.join("'./manual/%s'" % f for f in MAN_IMGS) + '''];
self.addEventListener('install', e => {
  const shell = caches.open(CACHE).then(c => c.addAll(SHELL.map(u => new Request(u, { cache: 'reload' })))).then(() => self.skipWaiting());
  // 説明書の写真：まだないものだけ読む。読めなくてもアプリの更新は止めない
  const man = caches.open(MCACHE).then(c => Promise.all(MANUAL.map(u => c.match(u).then(h => h || c.add(u)).catch(() => null)))).catch(() => null);
  e.waitUntil(Promise.all([shell, man]));
});
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE && k !== MCACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const u = new URL(e.request.url);
  if (u.origin === location.origin && u.pathname.endsWith('/version.json')) return; // 更新の確認は毎回ネットへ
  if (e.request.mode === 'navigate') {
    // ページごとにしまう（説明書を開いても、アプリのページは上書きしない）
    const key = /\\/manual\\.html$/.test(u.pathname) ? './manual.html' : './index.html';
    e.respondWith(fetch(u.href, { cache: 'no-cache', credentials: 'same-origin' }).then(r => { if (r.ok) { const c = r.clone(); caches.open(CACHE).then(x => x.put(key, c)); } return r; })
      .catch(() => caches.match(key).then(h => h || caches.match('./index.html')).then(h => h || caches.match('./'))));
    return;
  }
  // CMの動画は大きいのでしまわない（iPhoneが少しずつ読む＝Rangeのまま、ブラウザにまかせる）
  if (u.origin === location.origin && /\\/cm\\/[^/]+\\.mp4$/.test(u.pathname)) return;
  if (u.origin === location.origin && /\\/manual\\/[^/]+$/.test(u.pathname)) {
    e.respondWith(caches.open(MCACHE).then(c => c.match(e.request).then(hit => hit || fetch(e.request).then(r => { if (r.ok) c.put(e.request, r.clone()); return r; }))));
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
print('built', TARGET, out, sorted(os.listdir(out)), len(html), 'APP_VER', APP_VER, 'MOTHER_VER', MOTHER_VER, 'MANUAL', MAN_VER, len(MAN_IMGS), 'CM', CM, 'LEGAL', LEGAL)
