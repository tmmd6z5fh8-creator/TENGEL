# アプリの中でレースのデータを入れる仕組み・アップデートの仕組みのテスト（2026/10/13〜）
#  A. Web版：判定したレース＋着順 →「マザーデータにも入れる」で1行入る（馬番→人気・払戻・自己参照の除外・記録タブの「マザー入り」・直すと入れ直し）
#     マザーデータの一覧（見る・直す・消す・1つずつ入れる・まちがいの案内・同じレースの上書き）・書き出す（A〜P列のCSV）・CSVから入れる／足す・バックアップに入る
#  B. Web版：アプリの更新でアプリに入っているデータが新しくなっても、自分で入れたレースは残る
#  C. App Store版（にせもののアプリ）：App Storeの新しい版のお知らせ・「データの更新」（新しいデータを入れる・自分で入れたレースは残る・ひとつ前に戻せる・
#     アプリの更新で古いデータに戻さない・形のちがうデータは入れない）・出さない言葉がない
import csv, io, json, os, re, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
sys.path.insert(0, W)
import app_target as AT
SRV = os.path.join(W, 'srv'); PORT = 8795; BASE = f'http://localhost:{PORT}/TENGEL/'; APPURL = f'http://localhost:{PORT}/APP/'
REMOTE = f'http://localhost:{PORT}/remote/mother_app.json'
TMP = os.path.join(SRV, '_tmp')
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(TMP)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)


def build(target, out, **env):
    e = dict(os.environ, HIST='hist_280.json', DROP='', TARGET=target, DATA_URL=REMOTE); e.update(env)
    shutil.rmtree(out, ignore_errors=True)
    subprocess.run(['python3', 'build_pwa.py', out], check=True, stdout=subprocess.DEVNULL, env=e)


def native(out):
    p = os.path.join(out, 'index.html'); h = open(p, encoding='utf8').read()
    assert "window.__NATIVE = location.protocol === 'tengel:';" in h
    open(p, 'w', encoding='utf8').write(h.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))


build('web', os.path.join(SRV, 'TENGEL'))
build('app', os.path.join(SRV, 'APP')); native(os.path.join(SRV, 'APP'))
# 「データの更新」で読む新しいデータ（290走・版 2026-10-20）
build('web', os.path.join(TMP, 'w290'), HIST='hist.json', MOTHER_VER='2026-10-20')
os.makedirs(os.path.join(SRV, 'remote'))
shutil.copy(os.path.join(TMP, 'w290', 'data', 'mother_app.json'), os.path.join(SRV, 'remote', 'mother_app.json'))
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
fails, errs = [], []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label)
    if not c:
        fails.append(label)


form = {"venue": "大井", "date": "2026-10-14", "r": "8", "dist": "1400", "surface": "ダ", "baba": "稍重", "n": "14", "s1": "41.3", "s1combo": "6-2-10", "s5": "58.2", "s10": "84.0",
        "rows": [{"no": no, "tan": str(t), "fuku": f} for no, t, f in [(1, 12.4, '3.0-4.6'), (2, 4.1, '1.6-2.2'), (3, 31.5, '6.1-9.8'), (4, 9.8, '2.6-3.9'), (5, 18.2, '4.0-6.2'), (6, 2.4, '1.1-1.3'), (7, 7.6, '2.1-3.1'), (8, 54.0, '9.4-15.0'), (9, 25.9, '5.2-8.1'), (10, 6.3, '1.9-2.7'), (11, 14.7, '3.3-5.1'), (12, 88.6, '13.2-21.1'), (13, 40.2, '7.7-12.2'), (14, 120.5, '18.4-29.6')]]}
SEED = "if (!sessionStorage.getItem('seeded')) { localStorage.setItem('tengel.form', %s); localStorage.setItem('tengel.tab', '\"judge\"'); sessionStorage.setItem('seeded', '1'); }"
rows = lambda pg, n: pg.evaluate(f'TengelLocal.slots.rows({n})')
count = lambda pg, n: pg.evaluate(f'TengelLocal.slots.rows({n}).length')
row = lambda pg, n, i: pg.evaluate(f'TengelLocal.slots.rows({n}).find(r => r.id === {json.dumps(i)}) || null')
toast = lambda pg: pg.locator('#toast').inner_text() if pg.locator('#toast').is_visible() else ''


def save_result(pg, res, upay='', spay='', other=None):
    card = pg.locator('#recCard')
    card.locator('[data-k=res]').fill(''); card.locator('[data-k=res]').press_sequentially(res, delay=10)
    if upay: card.locator('[data-k=upay]').fill(upay)
    if spay: card.locator('[data-k=spay]').fill(spay)
    if other: card.locator(f'[data-k=other] button[data-v="{other}"]').click()
    pg.wait_for_timeout(250)
    card.locator('[data-act=save]').click(); pg.wait_for_timeout(900)


def open_set(pg):
    pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(500)


try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        # ================= A. Web版 =================
        print('[A] Web版：判定 → 着順 → マザーデータにも入れる')
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP', accept_downloads=True)
        ctx.add_init_script(SEED % json.dumps(json.dumps(form, ensure_ascii=False)))
        pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append('A:' + str(e)))
        pg.goto(BASE); pg.wait_for_timeout(1800)
        card = pg.locator('#recCard')
        check(count(pg, 1) == 280, f'はじめは280走（{count(pg, 1)}）')
        ms = card.locator('[data-k=mslot]')
        check(ms.count() == 1 and ms.input_value() == '1', f'「マザーデータにも入れる」：はじめは1つ目（{ms.input_value() if ms.count() else None}）')
        check('着順（1着・2着）を入れて保存すると' in card.locator('[data-k=mstate]').inner_text(), '着順がまだなら案内')
        card.locator('[data-k=res]').press_sequentially('6.2.10', delay=10); pg.wait_for_timeout(250)
        check('280走 → 281走' in card.locator('[data-k=mstate]').inner_text(), f'着順を入れると「保存すると入るよ（280走 → 281走）」（{card.locator("[data-k=mstate]").inner_text()}）')
        card.locator('[data-k=res]').fill('')
        save_result(pg, '6.2.10', '1230', '45670', other='未購入')
        t = toast(pg); print('    →', t)
        check('マザーデータ「大井競馬」にも入れたよ（281走）' in t, 'ほぞんすると「マザーデータにも入れたよ（281走）」')
        r = row(pg, 1, '20261014-oi-08')
        check(r and r['src'] == 'input' and [r['p1'], r['p2'], r['p3']] == [1, 2, 3] and r['umatanPay'] == 1230 and r['sanrenPay'] == 45670 and r['tan1'] == 2.4 and r['s1'] == 41.3 and r['n'] == 14 and r['dist'] == 1400 and r['baba'] == '稍重' and r['venue'] == '大井',
              f'入った1行：馬番6-2-10→1-2-3人気・払戻・オッズ・頭数・距離・馬場（{r}）')
        pg.wait_for_timeout(400)
        check('自己参照の除外' in pg.locator('#result').inner_text(), '同じレースを判定すると、自分自身は外して参考値を計算')
        pill = pg.evaluate("document.getElementById('dbpill').textContent")
        check('269走' in pill, f'上の表示（集計できるレース）も268走→269走（{pill}）')
        # 記録タブ
        pg.click('.tabbar button[data-tab=rec]'); pg.wait_for_timeout(500)
        lr = pg.locator('#recList .lrow[data-id="20261014-oi-08"]')
        check(lr.count() == 1 and 'マザー入り' in lr.inner_text(), '記録タブの行に「マザー入り」')
        lr.locator('.lmain').click(); pg.wait_for_timeout(300)
        check(lr.locator('[data-k=mslot]').input_value() == '1' and lr.locator('[data-k=upay]').input_value() == '1230', '記録を開くと、入れ先と払戻が残っている')
        rr = lr.locator('[data-k=res]'); rr.fill(''); rr.press_sequentially('2.6.10', delay=10); pg.wait_for_timeout(250)
        check('保存すると直すよ' in lr.locator('[data-k=mstate]').inner_text(), '入っているレースは「保存すると直すよ」')
        lr.locator('[data-act=save]').click(); pg.wait_for_timeout(900)
        r = row(pg, 1, '20261014-oi-08')
        check(r and [r['p1'], r['p2'], r['p3']] == [2, 1, 3] and count(pg, 1) == 281 and '入れ直した' in toast(pg), f'着順を直して保存 → マザーデータも直る（{r and [r["p1"], r["p2"], r["p3"]]}・{count(pg, 1)}走）')
        # ---- マザーデータの一覧 ----
        print('[A2] マザーデータの一覧：見る・直す・消す・1つずつ入れる')
        open_set(pg)
        pg.locator('#mdOpenBtn').click(); pg.wait_for_timeout(500)
        sh = pg.locator('#mdSheet')
        check(sh.is_visible() and '「大井競馬」のレース' in pg.locator('#mdTitle').inner_text() and pg.locator('#mdYM').input_value() == '2026-10', f'一覧が開く（{pg.locator("#mdYM").input_value()}）')
        mr = sh.locator('.mdrow[data-id="20261014-oi-08"]')
        check(mr.count() == 1 and '自分で入力' in mr.inner_text() and '2-1-3人気' in mr.inner_text() and '1,230円' in mr.inner_text(), f'入れたレースが一覧にある（{mr.inner_text()[:80] if mr.count() else None}）')
        mr.locator('.mdmain').click(); pg.wait_for_timeout(300)
        fm = mr.locator('.mdform')
        check(fm.locator('[data-k=res]').input_value() == '2-1-3' and fm.locator('[data-k=sanrenPay]').input_value() == '45670', 'レースを押すと直す欄（中身が入っている）')
        check('→' in fm.locator('[data-k=pv]').inner_text() and '層' in fm.locator('[data-k=pv]').inner_text(), f'判定と結果を見せる（{fm.locator("[data-k=pv]").inner_text()}）')
        fm.locator('[data-k=sanrenPay]').fill('52340'); fm.locator('[data-md=save]').click(); pg.wait_for_timeout(600)
        check(row(pg, 1, '20261014-oi-08')['sanrenPay'] == 52340 and '直した' in toast(pg), '直して保存')
        mr = sh.locator('.mdrow[data-id="20261014-oi-08"]'); mr.locator('.mdmain').click(); pg.wait_for_timeout(300)
        d = mr.locator('[data-md=del]'); d.click(); check('ほんとに消す' in d.inner_text(), '消すときは確かめる'); d.click(); pg.wait_for_timeout(600)
        check(count(pg, 1) == 280 and not row(pg, 1, '20261014-oi-08'), '消せる（280走に戻る）')
        # 1つずつ入れる
        pg.locator('#mdNew').click(); pg.wait_for_timeout(300)
        nf = pg.locator('#mdNewBox .mdform')
        nf.locator('[data-md=save]').click(); pg.wait_for_timeout(300)
        check('入れてね' in nf.locator('[data-k=pv]').inner_text() and '馬場状態' in nf.locator('[data-k=pv]').inner_text(), f'足りないと案内（{nf.locator("[data-k=pv]").inner_text()}）')
        nf.locator('[data-k=date]').fill('2026-10-15'); nf.locator('[data-k=r]').select_option('3'); nf.locator('[data-k=baba] button[data-v="良"]').click()
        nf.locator('[data-k=dist]').fill('1200'); nf.locator('[data-k=n]').fill('12'); nf.locator('[data-k=tan1]').fill('2.1'); nf.locator('[data-k=s1]').fill('20.0')
        nf.locator('[data-k=res]').press_sequentially('1.4.2', delay=10); nf.locator('[data-k=umatanPay]').fill('780'); pg.wait_for_timeout(250)
        pv = nf.locator('[data-k=pv]').inner_text(); print('    preview:', pv)
        check('A層' in pv and '人気→中穴' in pv and '第2ゾーン的中' in pv and '3連単ゾーンも的中' in pv, '入れる前に、判定（A層）と結果（人気→中穴→人気・第2ゾーン的中・3連単も）を見せる')
        nf.locator('[data-md=save]').click(); pg.wait_for_timeout(600)
        r = row(pg, 1, '20261015-oi-03')
        check(r and r['src'] == 'input' and r['cnt'] == 1 and [r['p1'], r['p2'], r['p3']] == [1, 4, 2] and r['umatanPay'] == 780 and r['sanrenPay'] is None and count(pg, 1) == 281, f'1つ入れた（{r}）')
        # 同じレースをもう一度 → 上書きを確かめる
        pg.locator('#mdNew').click(); pg.wait_for_timeout(300); nf = pg.locator('#mdNewBox .mdform')
        nf.locator('[data-k=date]').fill('2026-10-15'); nf.locator('[data-k=r]').select_option('3'); nf.locator('[data-k=baba] button[data-v="良"]').click()
        nf.locator('[data-k=dist]').fill('1200'); nf.locator('[data-k=n]').fill('12'); nf.locator('[data-k=tan1]').fill('2.6'); nf.locator('[data-k=s1]').fill('30.1'); nf.locator('[data-k=res]').press_sequentially('3.1.2', delay=10)
        sv = nf.locator('[data-md=save]'); sv.click(); pg.wait_for_timeout(300)
        check('もう入っているよ' in sv.inner_text(), '同じ日付・Rは「もう入っているよ。上書きする？」')
        sv.click(); pg.wait_for_timeout(600)
        r = row(pg, 1, '20261015-oi-03')
        check(r and r['tan1'] == 2.6 and count(pg, 1) == 281, '2回押すと上書き（増えない）')
        pg.locator('#mdSheet .mdx').click(); pg.wait_for_timeout(300)
        check(pg.locator('#mdSheet').count() == 0, '×で閉じる')
        # ---- 書き出す ----
        print('[A3] 書き出す・CSVから入れる・足す')
        pg.locator('#mdExpBtn').click(); pg.wait_for_timeout(300)
        tx = pg.locator('#mdExport textarea').input_value().split('\n')
        check(tx[0].split('\t') == ['日付', 'R', '馬場', '距離', '頭数', '単勝1位', '3連単1位', '1着人気', '2着人気', '3着人気', '3連単5位', '3連単10位', '馬単払戻', '3連単払戻', '備考', '集計対象'] and len(tx) == 282,
              f'A〜P列で書き出す（見出し＋281行：{len(tx)}）')
        check('2026/10/15\t3\t良\t1200\t12\t2.6\t30.1\t3\t1\t2' in '\n'.join(tx), '入れたレースも書き出される')
        with pg.expect_download() as dl:
            pg.locator('#mdExport [data-mx=csv]').click()
        csvp = os.path.join(TMP, 'out.csv'); dl.value.save_as(csvp)
        raw = open(csvp, 'rb').read()
        check(raw.startswith(b'\xef\xbb\xbf') and dl.value.suggested_filename.endswith('.csv') and raw.count(b'\r\n') == 281, f'CSVで保存（{dl.value.suggested_filename}・BOMつき）')
        # CSV → 2つ目（空）に入れる
        pg.locator('#slotList .slotrow[data-n="2"] [data-sact=edit]').click(); pg.wait_for_timeout(300)
        pg.set_input_files('#smFile', csvp); pg.wait_for_timeout(900)
        check('281走' in pg.locator('#smPreview').inner_text() and pg.locator('#smMerge').count() == 0, '空のマザーデータにCSVを入れる（足すボタンなし）')
        pg.click('#smApply'); pg.wait_for_timeout(700)
        check(count(pg, 2) == 281 and row(pg, 2, '20261015-m2-03')['tan1'] == 2.6, f'2つ目に281走が入った（{count(pg, 2)}）')
        # 足す：新しいレース1走＋変わったレース1走のCSVを1つ目に
        lines = [['日付', 'R', '馬場', '距離', '頭数', '単勝1位', '3連単1位', '1着人気', '2着人気', '3着人気', '3連単5位', '3連単10位', '馬単払戻', '3連単払戻', '備考', '集計対象'],
                 ['2026/10/16', '1', '重', '1000', '10', '1.8', '12.5', '1', '2', '3', '', '', '450', '1560', 'テスト', '1'],
                 ['2026/10/15', '3', '良', '1200', '12', '2.6', '30.1', '3', '1', '4', '', '', '', '', '', '1']]
        mp = os.path.join(TMP, 'add.csv'); bio = io.StringIO(); csv.writer(bio, lineterminator='\r\n').writerows(lines); open(mp, 'w', encoding='utf-8-sig').write(bio.getvalue())
        pg.locator('#slotList .slotrow[data-n="1"] [data-sact=edit]').click(); pg.wait_for_timeout(300)
        pg.set_input_files('#smFile', mp); pg.wait_for_timeout(900)
        mg = pg.locator('#smMerge'); print('    preview:', pg.locator('#smPreview').inner_text().replace('\n', ' | ')[:200])
        check(mg.count() == 1 and '新しい1走' in mg.inner_text() and '変わる1走' in mg.inner_text() and '入れ替える' in pg.locator('#smApply').inner_text(), '「足す（新しい1走・変わる1走）」と「入れ替える」')
        mg.click(); pg.wait_for_timeout(700)
        r16, r15 = row(pg, 1, '20261016-oi-01'), row(pg, 1, '20261015-oi-03')
        check(count(pg, 1) == 282 and r16 and r16['src'] == 'file' and r16['note'] == 'テスト' and r15['p3'] == 4, f'足す：いまのレースは残して、新しいレース・変わったレースだけ（{count(pg, 1)}走）')
        # バックアップに、自分で入れたレースも入る
        with pg.expect_download() as dl2:
            pg.click('#pwaBackup')
        bk = json.load(open(dl2.value.path(), encoding='utf8'))
        ids = sorted(x['id'] for x in bk.get('motherAdd', []))
        check(ids == ['20261015-oi-03', '20261016-oi-01'], f'バックアップに、1つ目に自分で入れたレースも入る（{ids}）')
        pg.close(); ctx.close()

        # ================= B. アプリの更新：アプリに入っているデータが新しくなっても、自分で入れたレースは残る =================
        print('[B] アプリの更新（データが290走に）→ 自分で入れたレースは残る')
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, locale='ja-JP')
        ctx.add_init_script(SEED % json.dumps(json.dumps(form, ensure_ascii=False)))
        pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append('B:' + str(e)))
        pg.goto(BASE); pg.wait_for_timeout(1500)
        save_result(pg, '6.2.10', other='未購入')
        check(count(pg, 1) == 281, f'280走＋自分で1走（{count(pg, 1)}）')
        build('web', os.path.join(SRV, 'TENGEL'), HIST='hist.json', MOTHER_VER='2026-10-20')
        pg.reload(); pg.wait_for_timeout(1800)
        t = toast(pg); print('    →', t)
        check(count(pg, 1) == 291 and row(pg, 1, '20261014-oi-08') and '自分で入れたレース（1走）はそのまま' in t, f'新しいデータ290走＋自分で入れた1走＝291走（{count(pg, 1)}）・お知らせ')
        pg.close(); ctx.close()
        build('web', os.path.join(SRV, 'TENGEL'))   # もとに戻す

        # ================= C. App Store版（にせもののアプリ） =================
        print('[C] App Store版：App Storeの新しい版・データの更新')
        FAKE = """
window.__NATIVE_INFO = { version: '1.0', build: '3', device: 'phone' };
window.__bridge = [];
window.webkit = { messageHandlers: { tengel: { postMessage: function (m) {
  window.__bridge.push(m.name);
  var val = true;
  if (m.name === 'store') val = window.__storeAns || { found: true, version: '1.1', url: 'https://apps.apple.com/jp/app/id0000000000', notes: '新しい版', date: '2026-10-20T00:00:00Z', error: '' };
  setTimeout(function () { window.__nativeReply(m.id, true, val); }, 30);
} } } };
"""
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, locale='ja-JP')
        ctx.add_init_script(FAKE)
        form_app = dict(form, venue='')
        ctx.add_init_script(SEED % json.dumps(json.dumps(form_app, ensure_ascii=False)))
        ctx.route('**/__native/autobackup.json', lambda route: route.fulfill(status=404, body='not found'))
        pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append('C:' + str(e)))
        pg.goto(APPURL); pg.wait_for_timeout(4200)
        ba, bd = pg.locator('#nBar_app'), pg.locator('#nBar_data')
        check(ba.is_visible() and '1.1' in ba.inner_text() and ba.locator('a.btn').get_attribute('href').startswith('https://apps.apple.com/'), f'上に「App Storeに新しい版（1.1）」→ App Storeを開く（{ba.inner_text() if ba.count() else None}）')
        check(bd.is_visible() and '290走' in bd.inner_text(), f'上に「新しいデータがあるよ（290走）」（{bd.inner_text() if bd.count() else None}）')
        check(count(pg, 1) == 280 and pg.evaluate("TengelLocal.slots.info()[0].name") == 'マザーデータ1', 'はじめはアプリに入っている280走（マザーデータ1）')
        # 判定したレースを入れる（開催場は空）
        save_result(pg, '6.2.10', '1230', '', other='未購入')
        check(count(pg, 1) == 281 and row(pg, 1, '20261014-m1-08') and row(pg, 1, '20261014-m1-08')['venue'] == '', f'開催場が空でも、1つ目に入る（id 20261014-m1-08・開催場は空：{count(pg, 1)}走）')
        open_set(pg)
        up = pg.locator('#setUpdate')
        check(up.locator('h2').inner_text() == 'アプリの更新' and '1.0（3）' in up.inner_text(), '設定：「アプリの更新」にいまの版')
        pg.click('#nuCheck'); pg.wait_for_timeout(500)
        check('新しい版 1.1' in pg.locator('#nuStore').inner_text() and pg.locator('#nuOpen').is_visible() and 'apps.apple.com' in pg.locator('#nuOpen').get_attribute('href'), '「新しい版があるか確認」→ 1.1・「App Storeで更新する」')
        pg.evaluate("window.__storeAns = { found: true, version: '1.0', url: 'https://apps.apple.com/jp/app/id0000000000', notes: '', date: '', error: '' }")
        pg.click('#nuCheck'); pg.wait_for_timeout(500)
        check('最新' in pg.locator('#nuMsg').inner_text() and not pg.locator('#nuOpen').is_visible(), 'いまの版が最新なら「最新だよ」')
        pg.evaluate("window.__storeAns = { found: false, version: '', url: '', notes: '', date: '', error: '' }")
        pg.click('#nuCheck'); pg.wait_for_timeout(500)
        check('まだ' in pg.locator('#nuStore').inner_text(), 'App Storeにまだ出ていないとき')
        # データの更新
        dc = pg.locator('#setData')
        check(dc.is_visible() and '281走' in pg.locator('#sdCur').inner_text() and '自分で入れた 1走' in pg.locator('#sdCur').inner_text(), f'「データの更新」：いまのデータ（{pg.locator("#sdCur").inner_text()}）')
        pg.click('#sdCheck'); pg.wait_for_timeout(700)
        check('新しいデータ（290走・10/9まで）' in pg.locator('#sdMsg').inner_text() and pg.locator('#sdApply').is_visible(), f'確かめると「新しいデータ（290走）」（{pg.locator("#sdMsg").inner_text()}）')
        pg.click('#sdApply'); pg.wait_for_timeout(900)
        meta = pg.evaluate("TengelLocal.slots.doc(1)")
        check(count(pg, 1) == 291 and row(pg, 1, '20261014-m1-08') and meta['dataVer'] == '2026-10-20' and meta['source'] == 'app', f'入れた：290走＋自分で入れた1走（{count(pg, 1)}走・版 {meta.get("dataVer")}）')
        check('自分で入れたレース（1走）はそのまま' in pg.locator('#sdMsg').inner_text() and pg.evaluate("!!TengelLocal.slots.prev(1)"), 'お知らせ・前のデータは「ひとつ前」に残る')
        check(not pg.locator('#nBar_data').is_visible(), '上の「新しいデータ」のお知らせは消える')
        pg.click('#sdCheck'); pg.wait_for_timeout(600)
        check('最新' in pg.locator('#sdMsg').inner_text(), 'もう一度確かめると「最新」')
        # 形のちがうデータは入れない
        RM = re.compile(r'/remote/mother_app\.json')
        ctx.route(RM, lambda route: route.fulfill(status=200, content_type='application/json', body=json.dumps({'app': 'other', 'rows': []})))
        pg.click('#sdCheck'); pg.wait_for_timeout(600)
        check('形がちがう' in pg.locator('#sdMsg').inner_text(), f'形のちがうデータは入れない（{pg.locator("#sdMsg").inner_text()}）')
        ctx.unroute(RM)
        RN = re.compile(r'/remote/mother_app\.json')
        ctx.route(RN, lambda route: route.fulfill(status=404, body='not found'))
        pg.click('#sdCheck'); pg.wait_for_timeout(600)
        check('新しいデータはないよ' in pg.locator('#sdMsg').inner_text() and not pg.locator('#sdApply').is_visible(), f'公開しているデータがない（404）ときは「新しいデータはないよ」（{pg.locator("#sdMsg").inner_text()}）')
        ctx.unroute(RN)
        # 一覧に出さない言葉がない
        pg.locator('#slotList .slotrow[data-n="1"] [data-sact=edit]').click(); pg.wait_for_timeout(300)
        pg.locator('#mdOpenBtn').click(); pg.wait_for_timeout(400)
        pg.locator('#mdSheet .mdrow').first.locator('.mdmain').click(); pg.wait_for_timeout(300)
        txt = pg.evaluate('document.body.innerText') + pg.evaluate("[...document.querySelectorAll('input,textarea,select,option')].map(e => e.value + ' ' + (e.placeholder || '')).join(' ')")
        bad = [w for w in AT.FORBIDDEN if w in txt]
        check(not bad, f'App Store版の画面（一覧を開いたところ）に出さない言葉がない（{bad}）')
        pg.locator('#mdSheet .mdx').click()
        # アプリの更新（中のデータの版 2026-10-15）でも、データの更新で入れた新しいデータ（2026-10-20）を古いデータに戻さない
        build('app', os.path.join(SRV, 'APP'), MOTHER_VER='2026-10-15'); native(os.path.join(SRV, 'APP'))
        pg.reload(); pg.wait_for_timeout(1500)
        meta = pg.evaluate("TengelLocal.slots.doc(1)")
        check(count(pg, 1) == 291 and meta['dataVer'] == '2026-10-20' and meta['embedded'] == '2026-10-15', f'アプリの更新で、データの更新で入れた新しいデータは古いデータに戻らない（{count(pg, 1)}走・{meta.get("dataVer")}）')
        # 中のデータのほうが新しいアプリ（2026-10-25）なら、それに入れ替わる（自分で入れたレースは残る）
        build('app', os.path.join(SRV, 'APP'), HIST='hist.json', MOTHER_VER='2026-10-25'); native(os.path.join(SRV, 'APP'))
        pg.reload(); pg.wait_for_timeout(1500)
        meta = pg.evaluate("TengelLocal.slots.doc(1)")
        check(count(pg, 1) == 291 and meta['dataVer'] == '2026-10-25' and row(pg, 1, '20261014-m1-08'), f'中のデータのほうが新しいアプリなら入れ替わる・自分で入れたレースは残る（{count(pg, 1)}走・{meta.get("dataVer")}）')
        b.close()
finally:
    srv.terminate()
print('errors', errs[:5])
print('FAILS', len(fails), fails)
sys.exit(1 if fails or errs else 0)
