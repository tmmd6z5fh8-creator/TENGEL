# App Store版（TARGET=app）に、競馬場・団体・商標・版の名前が出ないか、開催場の扱いが正しいかのテスト
#  ・作ったファイル（index.html・manual.html・このアプリについて）に、出さない言葉がない（app_target.FORBIDDEN）
#  ・画面のどこにも出ない（タブを全部まわって、文字・入力欄・ボタンの説明・開いた説明を見る）
#  ・開催場：はじめは空・空ならふつうの判定・アプリに入っているデータの開催場（しるし）ならふつうの判定・ちがえば【参考判定】
#  ・マザーデータの名前ははじめ「マザーデータ1〜3」・自分で入れたデータは名前に開催場が入っていればふつうの判定・切り替えの案内
#  ・アプリに入っているレースを判定すると、そのレース自身を外して参考値を出す（自己参照の除外）
#  ・期間の「最新」・5重勝・上の版の表示（カスタムのときだけ）
#  ・記録：開催場を入れたレースの「（参考）」・収支の「うち参考判定のレース」・CSVの開催場は入れたものだけ
#  ・Web版は今までどおり（大井・第13改訂版・WIN5 のまま）
import importlib.util, json, os, re, shutil, subprocess, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
spec = importlib.util.spec_from_file_location('app_target', os.path.join(W, 'app_target.py')); AT = importlib.util.module_from_spec(spec); spec.loader.exec_module(AT)
SRV = os.path.join(W, 'srv'); PORT = 8793
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'TENGEL')], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, TARGET='app'))
fails, errs = [], []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label)
    if not c:
        fails.append(label)


def bad_words(text):
    return sorted({w for w in AT.FORBIDDEN if w in text})


# ---- 作ったファイル ----
app_html = open(os.path.join(SRV, 'APP', 'index.html'), encoding='utf8').read()
man_html = open(os.path.join(SRV, 'APP', 'manual.html'), encoding='utf8').read()
check(not bad_words(app_html), f'App Store版の index.html に出さない言葉がない（{bad_words(app_html)}）')
check(not bad_words(man_html), f'App Store版の説明書に出さない言葉がない（{bad_words(man_html)}）')
check('/*' not in re.sub(r'"[^"\n]*"|\'[^\'\n]*\'', '', app_html.split('<script>', 2)[2][:3000]), 'プログラムのメモ（コメント）は消してある')
home = re.search(r'window\.__MOTHER_HOME=(\[[^\]]*\]);', app_html)
mom = json.loads(re.search(r'window\.__MOTHER=(\[.*?\]);window\.__MOTHER_DROP', app_html).group(1))
check(home and json.loads(home.group(1)) == [AT.fnv('大井')] and all(r['venue'] == '' and '-m1-' in r['id'] for r in mom) and len(mom) == 290,
      f'アプリに入れるデータ：開催場の名前なし・しるしだけ（{home.group(1) if home else None}・{len(mom)}走）')
web_html = open(os.path.join(SRV, 'TENGEL', 'index.html'), encoding='utf8').read()
check('大井 第13改訂版' in web_html and '>WIN5<' in web_html and 'window.__MOTHER_HOME=[' not in web_html and 'window.__DATA_URL=' not in web_html, 'Web版は今までどおり（大井 第13改訂版・WIN5・開催場のしるしやデータの更新先は入れない）')
for f in ('index.html', 'manual.html'):
    pth = os.path.join(SRV, 'APP', f); h = open(pth, encoding='utf8').read()
    if f == 'index.html':
        h = h.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;')
    open(pth, 'w', encoding='utf8').write(h)
APPURL = f'http://localhost:{PORT}/APP/'
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
# アプリを開いた時の画面（19章・App Store版）は、このテストでは見ないので、出たらすぐ閉じる
GATE_SKIP = "try { localStorage.setItem('tengel.gateSeen', '1'); } catch (e) {} document.addEventListener('DOMContentLoaded', function () { var t = setInterval(function () { var g = document.querySelector('#gate'); if (!g) return; if (g.hidden) { clearInterval(t); return; } var b = document.querySelector('#gateGo'); (b || g).click(); }, 100); setTimeout(function () { clearInterval(t); }, 8000); });"

FAKE = """
window.__NATIVE_INFO = { version: '1.0', build: '1', device: 'phone' };
window.__bridge = [];
window.webkit = { messageHandlers: { tengel: { postMessage: function (m) { window.__bridge.push({ name: m.name, payload: m.payload }); setTimeout(function () { window.__nativeReply(m.id, true, true); }, 20); } } } };
"""
# 画面の中の文字（見える文字・入力欄・ボタンの説明・画像の説明・選べる候補）を全部集める
DOM_TEXT = """() => { document.querySelectorAll('details').forEach(d => d.open = true);
  const out = [document.body.innerText];
  for (const el of document.querySelectorAll('*')) for (const a of ['placeholder', 'aria-label', 'title', 'alt', 'value', 'label', 'data-v']) { const v = el.getAttribute(a); if (v) out.push(v); }
  for (const el of document.querySelectorAll('input, textarea, select')) out.push(el.value || '');
  out.push(document.title); return out.join('\\n'); }"""
# 判定画面から読む：【参考判定】の印・切り替えの案内・判定の全文（STEP0〜T3）
RES = """(() => { const refs = [...document.querySelectorAll('#result .chip.ref')]; const go = document.querySelector('#result .slotchip-go');
  const full = (document.querySelector('#outText') || {}).textContent || '';
  return { isOi: !refs.length, ref: refs.length, refTxt: refs.map(c => c.textContent).join(), alt: go ? go.dataset.slot : null, full,
    chips: [...document.querySelectorAll('#result .vhead .chip')].map(c => c.textContent).join('|') }; })()"""
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, locale='ja-JP', timezone_id='Asia/Tokyo')
        ctx.add_init_script(FAKE)
        ctx.add_init_script(GATE_SKIP)
        ctx.route('**/__native/autobackup.json', lambda route: route.fulfill(status=404, body='not found'))
        pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(APPURL); pg.wait_for_timeout(1800)
        # ---- 画面のどこにも出ない（はじめの状態・入力例） ----
        seen = []
        for t in ('judge', 'win5', 'rec', 'stats', 'set'):
            pg.click(f'.tabbar button[data-tab={t}]'); pg.wait_for_timeout(500)
            txt = pg.evaluate(DOM_TEXT); seen.append(txt)
            check(not bad_words(txt), f'タブ「{t}」に出さない言葉がない（{bad_words(txt)}）')
        pg.click('.tabbar button[data-tab=judge]'); pg.wait_for_timeout(300)
        pg.click('#sampleBtn'); pg.wait_for_timeout(300)
        full = pg.locator('#outText').text_content()
        check(not bad_words(full), f'判定の全文（STEP0〜T3）に出さない言葉がない（{bad_words(full)}）')
        check('5重勝' in ''.join(seen) and pg.locator('.tabbar button[data-tab=win5]').inner_text().strip() == '5重勝', 'WIN5 は「5重勝」')
        check(pg.locator('.brand .ver').inner_text().strip() == '', f'上の版の表示はなし（「{pg.locator(".brand .ver").inner_text()}」）')
        check(pg.input_value('#fVenue') == '' and pg.get_attribute('#fVenue', 'placeholder') == '空でもOK', '開催場ははじめ空（空でもOK）')
        names = pg.evaluate('TengelLocal.slots.names()')
        check(names == {'1': 'マザーデータ1', '2': 'マザーデータ2', '3': 'マザーデータ3'}, f'マザーデータの名前ははじめ「マザーデータ1〜3」（{names}）')
        per = pg.evaluate("[...document.querySelectorAll('#perChips .fchip')].map(b => b.textContent)")
        check(per == ['全期間', '前半', '後半', '新規', '最新'], f'期間のボタン（{per}）')
        # カスタム買い目のときだけ、上に「カスタム買い目」
        pg.evaluate("(() => { const c = JSON.parse(JSON.stringify(T.DEFAULT_CFG)); c.A[0].t = ['人気']; document.dispatchEvent(new CustomEvent('tengel:zones', { detail: c })); })()")
        pg.wait_for_timeout(300)
        check(pg.locator('.brand .ver').inner_text().strip() == 'カスタム買い目', 'カスタム買い目のときは上に「カスタム買い目」')
        pg.evaluate("document.dispatchEvent(new CustomEvent('tengel:zones', { detail: null }))"); pg.wait_for_timeout(300)
        check(pg.locator('.brand .ver').inner_text().strip() == '', '初期の買い目に戻すと、上の表示も消える')

        # ---- 開催場と【参考判定】 ----
        def judge(venue):
            pg.fill('#fVenue', venue); pg.wait_for_timeout(350)
            return pg.evaluate(RES)
        j = judge('')
        check(j['isOi'] and j['ref'] == 0 and '開催場：—' in j['full'] and '【参考判定】' not in j['full'], '開催場が空 → ふつうの判定（開催場：—）')
        for v in ('大井', '大井競馬場', '大井競馬', ' 大井 '):
            j = judge(v)
            check(j['isOi'] and j['ref'] == 0, f'アプリに入っているデータの開催場（「{v}」と入れた）→ ふつうの判定（名前はアプリの中にない・しるしで比べる）')
        j = judge('船橋')
        check(not j['isOi'] and j['refTxt'] == '【参考判定】船橋' and '【参考判定】船橋8R／参考値はすべてマザーデータ1' in j['full'], f'ちがう開催場 → 【参考判定】（{j["refTxt"]}）')
        # ---- アプリに入っているレース：そのレース自身を外す（日付とRで探す） ----
        r0 = mom[0]
        f0 = {"venue": "", "date": r0['date'], "r": str(r0['r']), "dist": str(r0['dist']), "surface": "ダ", "baba": r0['baba'], "n": str(r0['n']), "tan1": str(r0['tan1']), "s1": str(r0['s1']),
              "s1combo": "", "s5": "", "s5combo": "", "s10": "", "s10combo": "", "rows": []}
        pg.evaluate("(f) => { localStorage.setItem('tengel.form', f); }", json.dumps(f0, ensure_ascii=False)); pg.reload(); pg.wait_for_timeout(1500)
        ex = pg.evaluate(RES)
        check('このレース自身を除外して参考値を再計算（自己参照の除外）' in ex['full'] and '開催場：—' in ex['full'], f'アプリに入っているレース（{r0["date"]} {r0["r"]}R・開催場は空）→ 日付とRで見つけて、そのレースを外して参考値')
        # ---- 自分で入れたマザーデータ：名前に開催場が入っていればふつうの判定・切り替えの案内 ----
        pg.evaluate("""async () => { const L = TengelLocal.slots; const rows = L.rows(1).slice(0, 60).map(r => Object.assign({}, r, { id: r.id.replace('-m1-', '-m2-') }));
          await L.replace(2, rows, { source: 'excel', file: 'test.xlsx' }); await L.rename(2, '船橋競馬'); }""")
        pg.wait_for_timeout(500)
        f0.update(venue='船橋', date='2026-10-20', r='8')
        pg.evaluate("(f) => { localStorage.setItem('tengel.form', f); }", json.dumps(f0, ensure_ascii=False)); pg.reload(); pg.wait_for_timeout(1500)
        j = pg.evaluate(RES)
        check(not j['isOi'] and j['alt'] == '2', f'1つ目で「船橋」→【参考判定】・「船橋競馬」（2つ目）に切り替える案内（{ {k: j[k] for k in ("isOi", "alt")} }）')
        pg.click('#result .slotchip-go'); pg.wait_for_timeout(900)
        j = pg.evaluate(RES)
        check(j['isOi'] and 'マザー：船橋競馬' in j['chips'] and j['ref'] == 0, f'2つ目「船橋競馬」に切り替え → 船橋のレースはふつうの判定（{j["chips"]}）')
        j = judge('大井')
        check(not j['isOi'] and j['ref'] == 1, '2つ目（自分で入れたデータ）で「大井」→【参考判定】（名前に入っていない）')
        j = judge('')
        check(j['isOi'] and j['ref'] == 0, '2つ目でも開催場が空ならふつうの判定')
        pg.evaluate("TengelLocal.slots.setActive(1)"); pg.wait_for_timeout(600)
        # ---- 記録：（参考）・収支・CSV ----
        def save(venue, date, r, res, stake, pay):
            # App Store版（第2弾）：判定画面で「買い目を予約」→ 記録タブの予約レースで着順（馬番）と払戻を入れて「結果を保存」
            f = dict(f0, venue=venue, date=date, r=str(r), rows=[{"no": no, "tan": str(t), "fuku": fk} for no, t, fk in [(1, 12.4, '3.0-4.6'), (2, 4.1, '1.6-2.2'), (3, 31.5, '6.1-9.8'), (4, 9.8, '2.6-3.9'), (5, 18.2, '4.0-6.2'), (6, 2.4, '1.1-1.3'), (7, 7.6, '2.1-3.1'), (8, 54.0, '9.4-15.0'), (9, 25.9, '5.2-8.1'), (10, 6.3, '1.9-2.7'), (11, 14.7, '3.3-5.1'), (12, 88.6, '13.2-21.1')]], n='12')
            pg.evaluate("(f) => { localStorage.setItem('tengel.form', f); }", json.dumps(f, ensure_ascii=False)); pg.reload(); pg.wait_for_timeout(1400)
            card = pg.locator('#recCard')
            card.locator('[data-rsv=reserve]').click(); pg.wait_for_timeout(900)
            rid = pg.evaluate("(() => { const b = [...TengelLocal.mem.bets.values()].find(x => x.rsv && x.rsv.state === 'reserved'); return b ? b.id : null; })()")
            pg.click('.tabbar button[data-tab=rec]'); pg.wait_for_timeout(500)
            row = pg.locator(f'#recList .lrow[data-id="{rid}"]'); row.locator('.lmain').click(); pg.wait_for_timeout(400)
            fm = row.locator('.rsvf')
            for k, v in zip(('p1', 'p2', 'p3'), res.split('-')): fm.locator(f'[data-k={k}]').fill(v)
            fm.locator('[data-k=stake][data-t="馬単"]').fill(stake); fm.locator('[data-k=payout][data-t="馬単"]').fill(pay)
            fm.locator('[data-k=p3]').dispatch_event('input'); pg.wait_for_timeout(200); fm.locator('[data-act=rsave]').click(); pg.wait_for_timeout(900)
            pg.evaluate("window.TengelFx && TengelFx.close()")   # 的中ボタン（第3弾）の画面をとじる
            pg.click('.tabbar button[data-tab=judge]'); pg.wait_for_timeout(300)
        save('船橋', '2026-10-21', 9, '1-2-3', '600', '0')
        save('', '2026-10-21', 10, '1-2-3', '400', '0')
        pg.click('.tabbar button[data-tab=rec]'); pg.wait_for_timeout(600)
        rows = pg.evaluate("[...document.querySelectorAll('#recList .lrow')].map(r => r.innerText.replace(/\\s+/g, ' '))")
        check(any('船橋（参考）' in x for x in rows) and sum('（参考）' in x for x in rows) == 1, f'記録の一覧：開催場を入れた参考判定のレースだけ「（参考）」（{[x[:40] for x in rows]}）')
        pg.evaluate("window.__bridge = []"); pg.click('#recExportBtn'); pg.wait_for_timeout(300); pg.click('#recCopy'); pg.wait_for_timeout(400)
        cp = [x for x in pg.evaluate('window.__bridge') if x['name'] == 'copy']
        csv = cp[0]['payload'] if cp else ''
        lines = [l for l in csv.split('\n') if l.startswith('2026/10/21')]
        check(len(lines) == 2 and any('\t船橋\t' in l or ',船橋,' in l for l in lines) and any(re.match(r'2026/10/21[\t,][\t,]10[\t,]', l) for l in lines), f'書き出し：開催場は入れたものだけ（{[l[:24] for l in lines]}）')
        pg.click('.tabbar button[data-tab=stats]'); pg.wait_for_timeout(800)
        mt = pg.locator('#moneyBody').inner_text()
        check('うち参考判定のレース' in mt, '収支の層別：「うち参考判定のレース」')
        st_txt = pg.evaluate(DOM_TEXT)
        check(not [w for w in bad_words(st_txt) if w not in ('船橋',)], f'実測・回収タブ：入れた開催場のほかに出さない言葉がない（{bad_words(st_txt)}）')
        # ---- 説明書 ----
        p3 = ctx.new_page(); p3.on('pageerror', lambda e: errs.append('MANUAL ' + str(e)))
        p3.goto(APPURL + 'manual.html'); p3.wait_for_timeout(900)
        ids = p3.evaluate("window.__ITEMS.map(i => i.id)")
        allt = [p3.evaluate(DOM_TEXT)]
        for i in ids:
            p3.goto(APPURL + 'manual.html#' + i); p3.wait_for_timeout(250)
            allt.append(p3.evaluate(DOM_TEXT))
        mtxt = '\n'.join(allt)
        check(not bad_words(mtxt), f'説明書（全部の項目）に出さない言葉がない（{bad_words(mtxt)}）')
        check('はじめのデータ 290走（10/9まで）' in mtxt and 'アプリに入っているデータ（290走（10/9まで））' in mtxt, '説明書：アプリに入っているデータの走数')
        b.close()
finally:
    srv.terminate()
check(not errs, 'ページのエラーなし' + (f'：{errs[:3]}' if errs else ''))
print('結果：', 'OK' if not fails else f'{len(fails)}件おかしい')
raise SystemExit(1 if fails else 0)
