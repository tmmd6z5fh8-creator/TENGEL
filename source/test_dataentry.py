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


# アプリを開いた時の画面（19章・App Store版）は、このテストでは見ないので、出たらすぐ閉じる
GATE_SKIP = "try { localStorage.setItem('tengel.gateSeen', '1'); } catch (e) {} document.addEventListener('DOMContentLoaded', function () { var t = setInterval(function () { var g = document.querySelector('#gate'); if (!g) return; if (g.hidden) { clearInterval(t); return; } var b = document.querySelector('#gateGo'); (b || g).click(); }, 100); setTimeout(function () { clearInterval(t); }, 8000); });"

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
# 第4.124版：データの更新の ファイルは スクランブル（そのままでは レースの 中身が 読めない・アプリが 鍵で 戻す）
_rm = open(os.path.join(SRV, 'remote', 'mother_app.json'), encoding='utf8').read(); _rj = json.loads(_rm)
_scr_ok = _rj.get('sc') == 1 and '"rows"' not in _rm and '2026-07-20' not in _rm and re.fullmatch(r'[0-9a-f]+', _rj.get('data', '')) is not None


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


def rec_month(pg, m=10):
    """記録タブの 月を その レースの 月（10月）に（記録タブは はじめ 今月 → 11月に なると 10/14 の 行が 見えない）"""
    b = pg.locator(f'#ymRec button[data-ym=m][data-v="{m}"]')
    if b.count() and b.get_attribute('aria-pressed') != 'true': b.click(); pg.wait_for_timeout(300)


def save_result_app(pg, res, upay='', spay=''):
    """App Store版（第2弾）：判定画面で「買い目を予約」→ 記録タブの予約レースで着順を入れて「結果を保存」（マザーデータにも入れるは、はじめの入れ先のまま）"""
    card = pg.locator('#recCard')
    if card.locator('[data-rsv=redo]').count(): card.locator('[data-rsv=redo]').click(); pg.wait_for_timeout(200)
    card.locator('[data-rsv=reserve]').click(); pg.wait_for_timeout(900)
    rid = pg.evaluate("(() => { const b = [...TengelLocal.mem.bets.values()].find(x => x.rsv && x.rsv.state === 'reserved'); return b ? b.id : null; })()")
    pg.click('.tabbar button[data-tab=rec]'); pg.wait_for_timeout(500); rec_month(pg)
    row = pg.locator(f'#recList .lrow[data-id="{rid}"]')
    if not row.locator('.rsvf').count(): row.locator('.lmain').click(); pg.wait_for_timeout(400)
    f = row.locator('.rsvf'); nos = res.split('.')
    for k, v in zip(('p1', 'p2', 'p3'), nos): f.locator(f'[data-k={k}]').fill(v)
    f.locator('[data-k=p3]').dispatch_event('input'); pg.wait_for_timeout(250)
    f.locator('[data-act=rsave]').click(); pg.wait_for_timeout(900)
    pg.evaluate("window.TengelFx && TengelFx.close()")   # 的中ボタン（第3弾）の画面をとじる
    pg.wait_for_timeout(300)
    # 第4.65版から 金額の 欄は 結果の あと。第4.123版：テンゲルデータで 判定した レースは「マザーデータ①に記録する？」→ 押して 記録する
    f = pg.locator(f'#recList .lrow[data-id="{rid}"] .rsvf')
    if f.count() and f.locator('[data-mpick]').count():
        f.locator('[data-mpick="2"]').click(); pg.wait_for_timeout(250)
        if upay and f.locator('[data-k=upay]').count(): f.locator('[data-k=upay]').fill(upay)
        if spay and f.locator('[data-k=spay]').count(): f.locator('[data-k=spay]').fill(spay)
        f.locator('[data-k=mslot]').dispatch_event('input'); pg.wait_for_timeout(200)
        f.locator('[data-act=rsave]').click(); pg.wait_for_timeout(900)
    pg.click('.tabbar button[data-tab=judge]'); pg.wait_for_timeout(300)


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
        pg.click('.tabbar button[data-tab=rec]'); pg.wait_for_timeout(500); rec_month(pg)
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
        check(_scr_ok, f'第4.124版：データの更新の ファイルは スクランブル（中身の 文字が 見えない・16進・{len(_rm)}文字）')
        FAKE = """
window.__NATIVE_INFO = { version: '1.0', build: '3', device: 'phone' };
window.__bridge = [];
window.webkit = { messageHandlers: { tengel: { postMessage: function (m) {
  window.__bridge.push(m.name);
  if (m.name === 'share') (window.__shares = window.__shares || []).push(m.payload);   // 第4.123版：ひな形の 中身を 確かめる
  var val = true;
  if (m.name === 'store') val = window.__storeAns || { found: true, version: '1.1', url: 'https://apps.apple.com/jp/app/id0000000000', notes: '新しい版', date: '2026-10-20T00:00:00Z', error: '' };
  setTimeout(function () { window.__nativeReply(m.id, true, val); }, 30);
} } } };
"""
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, locale='ja-JP')
        ctx.add_init_script(FAKE)
        ctx.add_init_script(GATE_SKIP)
        form_app = dict(form, venue='')
        ctx.add_init_script(SEED % json.dumps(json.dumps(form_app, ensure_ascii=False)))
        ctx.route('**/__native/autobackup.json', lambda route: route.fulfill(status=404, body='not found'))
        pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append('C:' + str(e)))
        pg.goto(APPURL); pg.wait_for_timeout(4200)
        ba, bd = pg.locator('#nBar_app'), pg.locator('#nBar_data')
        check(ba.is_visible() and '1.1' in ba.inner_text() and ba.locator('a.btn').get_attribute('href').startswith('https://apps.apple.com/'), f'上に「App Storeに新しい版（1.1）」→ App Storeを開く（{ba.inner_text() if ba.count() else None}）')
        check(bd.is_visible() and '新しいデータがあるよ' in bd.inner_text() and '走' not in bd.inner_text(), f'上に「テンゲルデータの新しいデータがあるよ」（第4.123版：数は 出さない）（{bd.inner_text() if bd.count() else None}）')
        check(count(pg, 1) == 280 and pg.evaluate("TengelLocal.slots.info()[0].name") == 'テンゲルデータ' and pg.evaluate("TengelLocal.slots.info().length") == 4, 'はじめはアプリに入っている280走（テンゲルデータ）・枠は 4つ')
        # 判定したレースを入れる（開催場は空）。App Store版は 予約 → 記録タブで結果（第2弾）→ 金額の 欄で「マザーデータ①に記録する」（第4.123版）
        save_result_app(pg, '6.2.10', '1230', '')
        check(count(pg, 1) == 280 and count(pg, 2) == 1 and row(pg, 2, '20261014-m2-08') and row(pg, 2, '20261014-m2-08')['venue'] == '' and row(pg, 2, '20261014-m2-08')['umatanPay'] == 1230,
              f'テンゲルデータには 入らない・マザーデータ①（2つ目）に 入る（id 20261014-m2-08・開催場は空・馬単払戻 1230：{count(pg, 1)}走／{count(pg, 2)}走）')
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
        check(dc.is_visible() and 'テンゲルデータ' in pg.locator('#sdCur').inner_text() and '走' not in pg.locator('#sdCur').inner_text(), f'「データの更新」：いまのデータ（第4.123版：数・期間・版は 出さない）（{pg.locator("#sdCur").inner_text()}）')
        pg.click('#sdCheck'); pg.wait_for_timeout(700)
        check('新しいデータがあるよ' in pg.locator('#sdMsg').inner_text() and '走' not in pg.locator('#sdMsg').inner_text() and pg.locator('#sdApply').is_visible(), f'確かめると「新しいデータがあるよ」（数は 出さない）（{pg.locator("#sdMsg").inner_text()}）')
        pg.click('#sdApply'); pg.wait_for_timeout(900)
        meta = pg.evaluate("TengelLocal.slots.doc(1)")
        check(count(pg, 1) == 290 and count(pg, 2) == 1 and meta['dataVer'] == '2026-10-20' and meta['source'] == 'app', f'入れた：テンゲルデータは 290走・マザーデータ①の 1走は そのまま（{count(pg, 1)}走・版 {meta.get("dataVer")}）')
        check('テンゲルデータを新しくしたよ' in pg.locator('#sdMsg').inner_text() and '走' not in pg.locator('#sdMsg').inner_text(), f'お知らせ（数は 出さない）（{pg.locator("#sdMsg").inner_text()}）')
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
        # 一覧に出さない言葉がない（第4.123版：テンゲルデータには 編集・一覧が ない → マザーデータ①の 一覧）
        check(pg.locator('#slotList .slotrow[data-n="1"] [data-sact=edit]').count() == 0 and pg.locator('#slotList .slotrow[data-n="1"]').count() == 1 and '走' not in pg.locator('#slotList .slotrow[data-n="1"]').inner_text(), 'テンゲルデータの 行には 編集が ない・数も 出さない')
        pg.locator('#slotList .slotrow[data-n="2"] [data-sact=edit]').click(); pg.wait_for_timeout(300)
        pg.locator('#mdOpenBtn').click(); pg.wait_for_timeout(400)
        pg.locator('#mdSheet .mdrow').first.locator('.mdmain').click(); pg.wait_for_timeout(300)
        txt = pg.evaluate('document.body.innerText') + pg.evaluate("[...document.querySelectorAll('input,textarea,select,option')].map(e => e.value + ' ' + (e.placeholder || '')).join(' ')")
        bad = [w for w in AT.FORBIDDEN if w in txt]
        check(not bad, f'App Store版の画面（一覧を開いたところ）に出さない言葉がない（{bad}）')
        pg.locator('#mdSheet .mdx').click(); pg.wait_for_timeout(300)
        # 第4.123版：入力用の Excel の ひな形（設定 → マザーデータ①の 編集）→ 共有シートで そのまま 渡す・空の ままだと 断る・入れれば 読める
        import base64 as _b64, datetime as _dt, openpyxl as _ox
        TPL = os.path.join(W, 'templates', 'mother_template.xlsx'); tpl = open(TPL, 'rb').read()
        check(pg.locator('#smTpl').count() == 1 and '入力用のExcel（ひな形）' in pg.locator('#smTplNote').inner_text(), '編集の 中に「入力用のExcel（ひな形）を保存」と 説明')
        pg.evaluate("window.__shares = []"); pg.locator('#smTpl').click(); pg.wait_for_timeout(900)
        sh = pg.evaluate("window.__shares")
        check(len(sh) == 1 and sh[0]['name'] == 'テンゲル_マザーデータ_入力用.xlsx' and 'text' not in sh[0] and _b64.b64decode(sh[0]['base64']) == tpl and 'spreadsheetml' in sh[0]['mime'] and 'ひな形を保存したよ' in toast(pg),
              f'押すと ひな形（.xlsx）を そのまま 共有シートへ（{[(x.get("name"), len(x.get("base64") or "")) for x in sh]}）')
        pg.set_input_files('#smFile', TPL); pg.wait_for_timeout(1200)
        pv = pg.locator('#smPreview').inner_text()
        check(pg.locator('#smApply').count() == 0 and 'レースの行' in pv and '5行目から' in pv and 'いまのデータはそのまま' in pv, f'空の ひな形を 選ぶと「黄色い行（5行目から）に入れてね」（記入例・説明の シートは 読まない）（{pv[:120]}）')
        wb = _ox.load_workbook(TPL); ws = wb['検証データ']
        for i, v in enumerate([[_dt.datetime(2026, 9, 20), 3, '稍重', 1200, 11, 2.4, 22.8, 2, 1, 5, '', '', 640, 3880, 'ひな形', 1],
                               [_dt.datetime(2026, 9, 20), 4, '良', 1600, 12, 3.1, 61.0, 1, 7, 2, '', '', 2450, 9870, '', 1]]):
            for j, x in enumerate(v): ws.cell(row=5 + i, column=j + 1, value=(x if x != '' else None))
        fp = os.path.join(TMP, '入力済み.xlsx'); wb.save(fp)
        pg.set_input_files('#smFile', fp); pg.wait_for_timeout(1200)
        pv = pg.locator('#smPreview').inner_text()
        check('2走' in pv and '検証データ' in pv and pg.locator('#smApply').count() == 1, f'ひな形に 2レース 入れると 読める（検証データの シート・2走）（{pv[:140].replace(chr(10), " | ")}）')
        if pg.locator('#smCancel').count(): pg.locator('#smCancel').click(); pg.wait_for_timeout(300)
        check(count(pg, 2) == 1, 'やめると マザーデータ①は そのまま（1走）')
        # アプリの更新（中のデータの版 2026-10-15）でも、データの更新で入れた新しいデータ（2026-10-20）を古いデータに戻さない
        build('app', os.path.join(SRV, 'APP'), MOTHER_VER='2026-10-15'); native(os.path.join(SRV, 'APP'))
        pg.reload(); pg.wait_for_timeout(1500)
        meta = pg.evaluate("TengelLocal.slots.doc(1)")
        check(count(pg, 1) == 290 and meta['dataVer'] == '2026-10-20' and meta['embedded'] == '2026-10-15', f'アプリの更新で、データの更新で入れた新しいデータは古いデータに戻らない（{count(pg, 1)}走・{meta.get("dataVer")}）')
        # 中のデータのほうが新しいアプリ（2026-10-25）なら、それに入れ替わる（自分で入れたレースは残る）
        build('app', os.path.join(SRV, 'APP'), HIST='hist.json', MOTHER_VER='2026-10-25'); native(os.path.join(SRV, 'APP'))
        pg.reload(); pg.wait_for_timeout(1500)
        meta = pg.evaluate("TengelLocal.slots.doc(1)")
        check(count(pg, 1) == 290 and meta['dataVer'] == '2026-10-25' and count(pg, 2) == 1 and row(pg, 2, '20261014-m2-08'), f'中のデータのほうが新しいアプリなら入れ替わる・マザーデータ①の レースは そのまま（{count(pg, 1)}走・{meta.get("dataVer")}）')
        # 第4.124版：まとめて入力（カード）：1レースずつ カードで 下書きに ためて「まとめて入れる」（まさちゃん「2.かな！ iPhoneでやりやすい方にして！」）
        # App Store版の テンキー（numpad.js）が 開くと 下の ボタンを ふさぐ ことが ある → とじてから 押す
        calm = lambda: pg.evaluate("() => { try { document.activeElement && document.activeElement.blur && document.activeElement.blur(); window.TengelNumpad && TengelNumpad.hide(); } catch (e) {} }")

        def press(sel):
            calm(); pg.wait_for_timeout(80); pg.locator(sel).click()
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(600)
        pg.locator('#slotList .slotrow[data-n="2"] [data-sact=edit]').click(); pg.wait_for_timeout(400)
        check(pg.locator('#mdBulkBtn').count() == 1 and pg.locator('#mdBulkBtn').inner_text() == 'まとめて入力', '編集の 中に「まとめて入力」')
        press('#mdBulkBtn'); pg.wait_for_timeout(500)
        bk = pg.locator('#bkSheet')
        check(bk.is_visible() and pg.locator('#bkTitle').inner_text() == '「マザーデータ①」にまとめて入力' and '1レース目' in bk.locator('.bkcard h4').inner_text()
              and pg.locator('#bkFoot [data-bk=apply]').is_disabled(), 'まとめて入力の 窓（1レース目・下書きが ない 間は「まとめて入れる」は 押せない）')

        def card(d=None, r=None, baba=None, dist='', n='', tan1='', s1='', res=''):
            fm = pg.locator('#bkBody .mdform')
            if d: fm.locator('[data-k=date]').fill(d)
            if r: fm.locator('[data-k=r]').select_option(str(r))
            if baba: fm.locator(f'[data-k=baba] button[data-v="{baba}"]').click()
            for k, v in (('dist', dist), ('n', n), ('tan1', tan1), ('s1', s1)):
                if v: fm.locator(f'[data-k={k}]').fill(v)
            if res: fm.locator('[data-k=res]').fill(res)
            fm.locator('[data-k=res]').dispatch_event('input'); pg.wait_for_timeout(150)
        bkrows = lambda: pg.evaluate("[...document.querySelectorAll('#bkBody .bkrow')].length")
        card('2026-09-21', 5, '良', '1400', '12', '2.2', '19.5', '1.3.2')
        pv = pg.locator('#bkBody [data-k=pv]').inner_text()
        press('#bkBody [data-bk=add]'); pg.wait_for_timeout(400)
        fm = pg.locator('#bkBody .mdform')
        check(bkrows() == 1 and '下書きに足したよ（1走）' in toast(pg) and '2レース目' in pg.locator('#bkBody .bkcard h4').inner_text()
              and fm.locator('[data-k=date]').input_value() == '2026-09-21' and fm.locator('[data-k=r]').input_value() == '6' and fm.locator('[data-k=baba] button[aria-pressed="true"]').inner_text() == '良'
              and fm.locator('[data-k=dist]').input_value() == '' and '→' in pv, f'足して 次へ：下書き 1走・次の カードは 日付・馬場・R（＋1）を 引きつぐ・距離は 空（{pv}）')
        press('#bkBody [data-bk=add]'); pg.wait_for_timeout(300)
        check(bkrows() == 1 and '入れてね' in toast(pg), '足りない ときは「入れてね：○○」で 下書きに 入らない')
        card(dist='1800', n='14', tan1='3.4', s1='88.0', res='7.1.2')
        press('#bkBody [data-bk=add]'); pg.wait_for_timeout(400)
        check(bkrows() == 2 and pg.locator('#bkFoot [data-bk=apply]').inner_text() == 'まとめて入れる（2走）', '2走目も 足す →「まとめて入れる（2走）」')
        press('#bkBody .bkrow[data-i="0"] [data-bk=edit]'); pg.wait_for_timeout(300)
        check('1行目を直す' in pg.locator('#bkBody .bkcard h4').inner_text() and pg.locator('#bkBody .mdform [data-k=dist]').input_value() == '1400', '「直す」で その行が カードに 出る')
        pg.locator('#bkBody .mdform [data-k=dist]').fill('1600'); press('#bkBody [data-bk=upd]'); pg.wait_for_timeout(300)
        drafts = pg.evaluate("JSON.parse(localStorage.getItem('tengel.bulk') || '{}')['2'] || []")
        check(len(drafts) == 2 and drafts[0]['dist'] == 1600 and drafts[1]['r'] == 6 and drafts[1]['p1'] == 7, f'直すと 下書きの その行が かわる（{[(d["r"], d["dist"]) for d in drafts]}）')
        # 同じ 日付・R → 入れ替える？（もう一度）
        card(r=6, dist='1800', n='14', tan1='3.5', s1='90.0', res='7.1.2')
        press('#bkBody [data-bk=add]'); pg.wait_for_timeout(200)
        t1 = pg.locator('#bkBody [data-bk=add]').inner_text()
        press('#bkBody [data-bk=add]'); pg.wait_for_timeout(300)
        drafts = pg.evaluate("JSON.parse(localStorage.getItem('tengel.bulk') || '{}')['2'] || []")
        check('もうあるよ' in t1 and len(drafts) == 2 and [d for d in drafts if d['r'] == 6][0]['tan1'] == 3.5, f'下書きに 同じ 日付・R が ある ときは 確かめて 入れ替え（{t1}）')
        # とじても 下書きは 残る
        press('#bkSheet .mdx'); pg.wait_for_timeout(300)
        check(pg.locator('#bkSheet').count() == 0 and pg.locator('#mdBulkBtn').inner_text() == 'まとめて入力（下書き 2走）', 'とじても 下書きは 残る（ボタンに「下書き 2走」）')
        press('#mdBulkBtn'); pg.wait_for_timeout(400)
        check(bkrows() == 2 and '3レース目' in pg.locator('#bkBody .bkcard h4').inner_text(), 'もう一度 開くと 下書きの つづき（3レース目）')
        press('#bkFoot [data-bk=apply]'); pg.wait_for_timeout(900)
        t = toast(pg); r5 = row(pg, 2, '20260921-m2-05'); r6 = row(pg, 2, '20260921-m2-06')
        check(count(pg, 2) == 3 and r5 and r5['src'] == 'input' and r5['dist'] == 1600 and [r5['p1'], r5['p2'], r5['p3']] == [1, 3, 2] and r6 and r6['tan1'] == 3.5 and pg.locator('#bkSheet').count() == 0
              and '「マザーデータ①」に 2走 入れたよ' in t and not pg.evaluate("(JSON.parse(localStorage.getItem('tengel.bulk') || '{}'))['2']"),
              f'「まとめて入れる」→ マザーデータ①に 2走（自分で入力）・下書きは 空に（{count(pg, 2)}走・{t}）')
        # もう 入って いる レース → 上書きの 確かめ
        press('#mdBulkBtn'); pg.wait_for_timeout(400)
        card('2026-09-21', 5, '重', '1600', '12', '2.2', '19.5', '1.3.2')
        press('#bkBody [data-bk=add]'); pg.wait_for_timeout(300)
        press('#bkFoot [data-bk=apply]'); pg.wait_for_timeout(300)
        t2 = pg.locator('#bkFoot [data-bk=apply]').inner_text()
        press('#bkFoot [data-bk=apply]'); pg.wait_for_timeout(900)
        check('上書き' in t2 and count(pg, 2) == 3 and row(pg, 2, '20260921-m2-05')['baba'] == '重', f'もう 入って いる レースは「上書き」を 確かめてから（{t2}）')
        txt = pg.evaluate('document.body.innerText')
        check(not [w for w in AT.FORBIDDEN if w in txt], 'まとめて入力の あとも 出さない言葉が ない')
        b.close()
finally:
    srv.terminate()
print('errors', errs[:5])
print('FAILS', len(fails), fails)
sys.exit(1 if fails or errs else 0)
