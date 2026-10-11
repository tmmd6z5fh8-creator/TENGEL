# 買った券種（単勝・複勝・馬連・馬単・ワイド・3連複・3連単）と券種ごとの金額のテスト（iPhoneアプリ版）
#  馬単・3連単はテンゲルの買ったゾーンで判定（今までどおり）、ほかの券種は回収額で判定。どれか当たればレースは的中
#  券種ごとの金額を保存（合計は stake/payout）・記録タブで直せる・収支は券種ごと・前の記録（券種ごとに分けていない）もそのまま・書き出しに券種ごとの金額
import json, os, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv'); PORT = 8778; URL = f'http://localhost:{PORT}/TENGEL/'; OUT = os.path.join(W, 't5'); os.makedirs(OUT, exist_ok=True)
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'TENGEL')], check=True, stdout=subprocess.DEVNULL)
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
odds = [1.5, 3.2, 4.8, 6.5, 8.9, 12.1, 15.6, 20.3, 28.4, 35.0, 48.2, 66.0]; nos = [6, 2, 10, 7, 1, 4, 11, 5, 9, 3, 8, 12]
FORM = {"id": None, "venue": "大井", "date": "2026-10-13", "r": "9", "dist": "1400", "surface": "ダ", "baba": "良", "n": "12", "tan1": "", "s1": "9.0", "s1combo": "", "s5": "", "s5combo": "", "s10": "", "s10combo": "",
        "rows": [{"no": no, "tan": str(t), "fuku": ""} for no, t in zip(nos, odds)]}   # A層（第1 人気→人気・第2 人気→中穴）
fails, errs = [], []
def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label)
    if not c: fails.append(label)
try:
    with sync_playwright() as p:
        b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 900}, device_scale_factor=2); pg = ctx.new_page()
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.add_init_script("if (!sessionStorage.getItem('x')) { sessionStorage.setItem('x', '1'); localStorage.setItem('tengel.form', %s); }" % json.dumps(json.dumps(FORM)))
        pg.goto(URL); pg.wait_for_timeout(1600)
        card = pg.locator('#recCard'); status = card.locator('[data-k=status]')
        tb = card.locator('[data-k=types] button')
        labels = [x.inner_text() for x in tb.all()]; print('[0] 券種:', labels, [x.get_attribute('aria-pressed') for x in tb.all()])
        check(labels == ['単勝', '複勝', '馬連', '馬単', 'ワイド', '3連複', '3連単'], '券種は7つ（単勝・複勝・馬連・馬単・ワイド・3連複・3連単）')
        rows = lambda: [x.get_attribute('data-t') for x in card.locator('.amts .amt').all()]
        check(rows() == ['馬単'], '最初は馬単だけ・金額の行も馬単だけ')
        def tog(t): card.locator(f'[data-k=types] button[data-v="{t}"]').click(); pg.wait_for_timeout(150)
        tog('単勝'); tog('ワイド')
        print('[1] 単勝・ワイドを足す →', rows()); check(rows() == ['単勝', '馬単', 'ワイド'], '金額の行が券種の順に増える')
        check(card.locator('[data-k=buyzf]').is_visible(), '馬単があるので「買ったゾーン」が出る')
        tog('馬単'); print('    馬単を外す →', rows())
        check(rows() == ['単勝', 'ワイド'] and not card.locator('[data-k=buyzf]').is_visible(), '馬単・3連単がないと「買ったゾーン」はかくれる')
        def amt(t, s_, p_):
            if s_ is not None: card.locator(f'[data-k=stake][data-t="{t}"]').fill(str(s_))
            if p_ is not None: card.locator(f'[data-k=payout][data-t="{t}"]').fill(str(p_))
            pg.wait_for_timeout(150)
        def tst(t): return card.locator(f'[data-k=tst][data-t="{t}"]').inner_text()
        amt('単勝', 500, None); amt('ワイド', 600, None)
        t = status.inner_text().replace('\n', ' '); print('[2] 回収額まだ →', t, '|', tst('単勝'), tst('ワイド'))
        check('結果待ち' in t and '回収額を入れると判定' in t, '単勝・ワイドは回収額が空なら結果待ち')
        amt('単勝', None, 0); amt('ワイド', None, 1450)
        t = status.inner_text().replace('\n', ' '); print('    単勝0・ワイド1450 →', t, '|', tst('単勝'), tst('ワイド'))
        check('的中' in t and '不的中' not in t.split('券種ごと')[0] and tst('単勝') == '不的中' and tst('ワイド') == '的中', 'ワイドが当たればレースは的中（単勝は不的中）')
        check('1,100→1,450（+350円）' in t, '合計 1,100円 → 1,450円')
        check('合計 1,100円 → 1,450円' in card.locator('[data-k=amtsum]').inner_text(), '金額の下に合計')
        # 馬単も足して、ゾーンと着順で判定
        tog('馬単'); card.locator('[data-k=buyz] button').nth(1).click(); pg.wait_for_timeout(100)
        card.locator('[data-k=mode] button[data-v=nin]').click(); r = card.locator('[data-k=res]'); r.fill(''); r.press_sequentially('1.5.2', delay=15); pg.wait_for_timeout(200)
        amt('馬単', 800, None)
        t = status.inner_text().replace('\n', ' '); print('[3] 馬単（第2を買った）1-5-2 →', t)
        check(tst('馬単') == '的中' and '買ったゾーン第2（人気→中穴）に入った' in t, '馬単は今までどおり買ったゾーンで的中')
        check('馬単が的中だよ！回収額を入れてね' in card.locator('[data-k=hint]').inner_text(), '馬単が的中で回収額が空なら案内')
        amt('馬単', None, 3120)
        card.locator('[data-k=note]').fill('ワイド 2-7')
        card.locator('[data-act=save]').click(); pg.wait_for_timeout(900)
        bet = pg.evaluate("TengelLocal.mem.bets.get('20261013-oi-09')")
        print('[4] 保存:', {k: bet.get(k) for k in ('types', 'amt', 'stake', 'payout')})
        check(bet['types'] == ['単勝', '馬単', 'ワイド'] and bet['amt'] == {'単勝': {'stake': 500, 'payout': 0}, '馬単': {'stake': 800, 'payout': 3120}, 'ワイド': {'stake': 600, 'payout': 1450}}, '券種ごとの金額を保存')
        check(bet['stake'] == 1900 and bet['payout'] == 4570, '合計（購入1,900円・回収4,570円）も保存')
        # 単勝だけ・着順なしでも回収額で判定
        pg.select_option('#fR', '10'); pg.wait_for_timeout(600)
        card = pg.locator('#recCard'); status = card.locator('[data-k=status]')
        tog('単勝'); tog('馬単'); amt('単勝', 300, 380)
        t = status.inner_text().replace('\n', ' '); print('[5] 単勝だけ・着順なし・回収380 →', t)
        check('的中' in t and '不的中' not in t, '単勝だけなら着順がなくても回収額で的中')
        card.locator('[data-act=save]').click(); pg.wait_for_timeout(800)
        # 払い戻し（回収額が空なら購入額）
        pg.select_option('#fR', '11'); pg.wait_for_timeout(600)
        card = pg.locator('#recCard'); tog('3連複'); amt('3連複', 1200, None); amt('馬単', 400, None)
        card.locator('[data-k=other] button[data-v="払い戻し"]').click(); pg.wait_for_timeout(150)
        card.locator('[data-act=save]').click(); pg.wait_for_timeout(800)
        b11 = pg.evaluate("TengelLocal.mem.bets.get('20261013-oi-11')"); print('[6] 払い戻し:', b11['amt'], b11['stake'], b11['payout'])
        check(b11['amt']['3連複'] == {'stake': 1200, 'payout': 1200} and b11['payout'] == 1600, '払い戻しで回収額が空なら、券種ごとに購入額と同じ')
        # 前の記録（券種ごとに分けていない：馬単＋3連単・合計1000円）
        pg.evaluate("""async () => { const db = await window.claude.use('db'); const b = JSON.parse(JSON.stringify(TengelLocal.mem.bets.get('20261013-oi-09'))); delete b.id; delete b.amt; delete b.buyZ;
          b.types = ['馬単', '3連単']; b.stake = 1000; b.payout = 0; b.r = 12; b.p1 = 7; b.p2 = 9; b.p3 = 1; b.n1 = null; b.n2 = null; b.n3 = null; b.note = '';
          await db.collection('bets').doc('20261013-oi-12').set(b); }""")
        pg.wait_for_timeout(600)
        # 記録タブ
        pg.click('.tabbar button[data-tab=rec]'); pg.wait_for_timeout(500)
        r9 = pg.locator('#recList .lrow[data-id="20261013-oi-09"]'); print('[7] 記録タブ:', r9.locator('.lmid').inner_text().replace('\n', ' '), '|', r9.locator('.lend').inner_text().replace('\n', ' '))
        check('単勝・馬単・ワイド' in r9.locator('.lmid').inner_text() and '1,900→4,570' in r9.locator('.lend').inner_text(), '一覧に券種と合計')
        r9.locator('.lmain').click(); pg.wait_for_timeout(400)
        ed = pg.locator('#recList .lrow[data-id="20261013-oi-09"] .recf')
        vals = {t: (ed.locator(f'[data-k=stake][data-t="{t}"]').input_value(), ed.locator(f'[data-k=payout][data-t="{t}"]').input_value()) for t in ['単勝', '馬単', 'ワイド']}
        print('    開いた金額:', vals); check(vals == {'単勝': ('500', '0'), '馬単': ('800', '3120'), 'ワイド': ('600', '1450')}, '記録タブで開くと券種ごとの金額が入っている')
        ed.locator('[data-k=payout][data-t="ワイド"]').fill('1500'); pg.wait_for_timeout(150); ed.locator('[data-act=save]').click(); pg.wait_for_timeout(800)
        check(pg.evaluate("TengelLocal.mem.bets.get('20261013-oi-09').payout") == 4620, '記録タブで直すと合計も直る（4,620円）')
        r12 = pg.locator('#recList .lrow[data-id="20261013-oi-12"]'); r12.locator('.lmain').click(); pg.wait_for_timeout(400)
        ed12 = pg.locator('#recList .lrow[data-id="20261013-oi-12"] .recf')
        print('[8] 前の記録:', r12.locator('.lend .stc').inner_text(), '|', ed12.locator('[data-k=stake][data-t="馬単"]').input_value(), ed12.locator('[data-k=stake][data-t="3連単"]').input_value())
        check('分けていない' in ed12.inner_text() and ed12.locator('[data-k=stake][data-t="馬単"]').input_value() == '1000', '前の記録は合計を先頭の券種に入れて、案内を出す')
        check(r12.locator('.lend .stc').inner_text() == '不的中', '前の記録の当たり外れは今までどおり（推奨ゾーン全部で判定）')
        # 収支：券種ごと
        pg.click('.tabbar button[data-tab=stats]'); pg.wait_for_timeout(500)
        tbl = [c.inner_text().replace('\n', ' ') for c in pg.locator('#moneyBody .card').all() if '券種別の収支' in c.inner_text()][0]
        print('[9] 券種別の収支:', tbl[:400])
        rows_ = {}
        for tr in pg.locator('#moneyBody .card').filter(has_text='券種別の収支').locator('tbody tr').all():
            tds = [td.inner_text() for td in tr.locator('td').all()]; rows_[tds[0]] = tds
        print('   ', rows_)
        check(rows_.get('ワイド', [None] * 8)[1:3] == ['1', '1'] and rows_['ワイド'][4] == '600' and rows_['ワイド'][5] == '1,500', 'ワイド：1回・的中1・600円→1,500円')
        check(rows_.get('単勝', [None] * 8)[1:3] == ['2', '1'] and rows_['単勝'][4] == '800' and rows_['単勝'][5] == '380', '単勝：2回・的中1・800円→380円')
        check(rows_.get('3連複', [None] * 8)[1] == '1' and rows_['3連複'][4] == '1,200' and rows_['3連複'][5] == '1,200', '3連複（払い戻し）：1,200円→1,200円')
        check('券種を分けていない記録' in rows_ and rows_['券種を分けていない記録'][4] == '1,000', '前の記録は「券種を分けていない記録」にまとめる')
        # 書き出し
        pg.click('.tabbar button[data-tab=rec]'); pg.wait_for_timeout(300); pg.click('#recExportBtn'); pg.wait_for_timeout(300)
        lines = pg.locator('#recExportText').input_value().split('\n'); head = lines[0].split('\t')
        row9 = [l for l in lines if '\t9\t' in l][0].split('\t')
        print('[10] 書き出し:', head[8], '=', row9[head.index('券種ごとの金額（購入→回収）')])
        check('券種ごとの金額（購入→回収）' in head and '単勝 500→0（不的中）／馬単 800→3120（的中）／ワイド 600→1500（的中）' == row9[head.index('券種ごとの金額（購入→回収）')], '書き出しに券種ごとの金額')
        pg.locator('#recList').screenshot(path=os.path.join(OUT, 'types_rec.png'))
        check(not errs, 'ページのエラーなし ' + str(errs[:3]))
finally:
    srv.terminate()
print('\nFAILS:', fails); sys.exit(1 if fails else 0)
