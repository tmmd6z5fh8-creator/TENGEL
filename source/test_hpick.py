# 買う馬を自分で選ぶテスト（iPhoneアプリ版）
#  通常の判定：ゾーンの番号を押して選ぶ・外す → 馬単・3連単は買ったゾーンの「選んだ馬」で判定（馬番でも人気でも）・保存・記録タブ・判定画面で開くと戻る・レースが変わるとリセット
#  WIN5：買う馬を押して選ぶ（そのレースは固定、ほかは残りの予算で自動）・予算オーバーの案内・おまかせに戻す・ランダムで戻る・選んだ馬で○×
#  WIN5の日付と予算の欄が重ならない
import json, os, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv'); PORT = 8780; URL = f'http://localhost:{PORT}/TENGEL/'; OUT = os.path.join(W, 't5'); os.makedirs(OUT, exist_ok=True)
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'TENGEL')], check=True, stdout=subprocess.DEVNULL)
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
odds = [1.5, 3.2, 4.8, 6.5, 8.9, 12.1, 15.6, 20.3, 28.4, 35.0, 48.2, 66.0]; nos = [6, 2, 10, 7, 1, 4, 11, 5, 9, 3, 8, 12]   # 人気順の馬番
FORM = {"id": None, "venue": "大井", "date": "2026-10-14", "r": "9", "dist": "1400", "surface": "ダ", "baba": "良", "n": "12", "tan1": "", "s1": "9.0", "s1combo": "", "s5": "", "s5combo": "", "s10": "", "s10combo": "",
        "rows": [{"no": no, "tan": str(t), "fuku": ""} for no, t in zip(nos, odds)]}   # A層：第1 人気→人気・第2 人気→中穴
def w5odds(n, tan1):
    xs = [tan1] + [round(tan1 + 1.9 * i + 0.35 * i * i, 1) for i in range(1, n)]
    return [{"no": (i * 5) % n + 1, "tan": str(x), "fuku": ""} for i, x in enumerate(xs)]
RACES = [('東京', 9, 1600, 12, '良', 1.8, 12.0), ('京都', 10, 1800, 14, '良', 2.0, 30.0), ('東京', 10, 1400, 12, '稍重', 3.0, 70.0), ('京都', 11, 2000, 16, '良', 3.2, 80.0), ('東京', 11, 1600, 12, '良', 1.5, 9.0)]
W5 = {"id": None, "fixed": False, "date": "2026-10-18", "budget": "3000", "mode": "pick", "randAll": False, "stake": "", "payout": "", "other": "", "note": "",
      "races": [{"form": {"venue": v, "date": "2026-10-18", "r": str(r), "dist": str(d), "surface": "芝", "baba": b, "n": str(n), "rows": w5odds(n, t1), "tan1": "", "s1": str(s1), "s1combo": "", "s5": "", "s5combo": "", "s10": "", "s10combo": ""}, "sel": None, "win": "", "picks": None, "man": None} for v, r, d, n, b, t1, s1 in RACES]}
fails, errs = [], []
def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label)
    if not c: fails.append(label)
try:
    with sync_playwright() as p:
        b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 900}, device_scale_factor=2); pg = ctx.new_page()
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.add_init_script("if (!sessionStorage.getItem('x')) { sessionStorage.setItem('x', '1'); localStorage.setItem('tengel.form', %s); localStorage.setItem('tengel.win5', %s); }" % (json.dumps(json.dumps(FORM)), json.dumps(json.dumps(W5, ensure_ascii=False))))
        pg.goto(URL); pg.wait_for_timeout(1600)
        # ---- 通常の判定 ----
        hb = pg.locator('#result button.hp'); print('[1] 押せる番号:', hb.count(), '|', pg.locator('#result .hpnote').inner_text()[:40])
        check(hb.count() == 24 and pg.locator('#result button.hp.off').count() == 0, 'ゾーンの番号が押せる（最初は全部選んだ状態）')
        z2 = lambda side, no: pg.locator(f'#result button.hp[data-hz="人気→中穴"][data-hs="{side}"][data-no="{no}"]')
        z2('b', 1).click(); pg.wait_for_timeout(250)
        check('off' in z2('b', 1).get_attribute('class') and z2('b', 1).get_attribute('aria-pressed') == 'false', '押すと外れて、うすくなる')
        card = pg.locator('#recCard'); status = card.locator('[data-k=status]')
        card.locator('[data-k=buyz] button').nth(1).click(); card.locator('[data-k=mode] button[data-v=nin]').click()
        res = card.locator('[data-k=res]')
        def typ(s_): res.fill(''); res.press_sequentially(s_, delay=15); pg.wait_for_timeout(250); return status.inner_text().replace('\n', ' ')
        t = typ('1.5.2'); print('[2] 2着が外した馬（5番人気＝1番）→', t)
        check('不的中' in t and '選んだ馬じゃないよ' in t, '2着が外した馬なら不的中（選んだ馬じゃない）')
        t = typ('1.4.2'); print('    2着が選んだ馬（4番人気＝7番）→', t); check('的中' in t and '不的中' not in t, '2着が選んだ馬なら的中')
        card.locator('[data-k=mode] button[data-v=no]').click(); pg.wait_for_timeout(200)
        print('    馬番に切り替え →', res.input_value(), '|', status.inner_text().replace('\n', ' ')[:30]); check(res.input_value() == '6-7-2' and '的中' in status.inner_text(), '馬番で入れても同じ判定（6-7-2）')
        t = typ('6.1.2'); check('選んだ馬じゃないよ' in t, '馬番で外した馬（1番）が2着なら不的中')
        typ('6.7.2')
        # 3連単：3着の馬を外す
        card.locator('[data-k=types] button[data-v="3連単"]').click(); pg.wait_for_timeout(200)
        z2('t', 2).click(); pg.wait_for_timeout(300)
        card = pg.locator('#recCard'); st3 = card.locator('[data-k=tst][data-t="3連単"]').inner_text(); stu = card.locator('[data-k=tst][data-t="馬単"]').inner_text()
        print('[3] 3着の2番を外す → 馬単', stu, '／3連単', st3); check(stu == '的中' and st3 == '不的中', '3着が外した馬なら3連単は不的中（馬単は的中）')
        card.locator('[data-k=stake][data-t="馬単"]').fill('600'); card.locator('[data-k=stake][data-t="3連単"]').fill('900')
        card.locator('[data-act=save]').click(); pg.wait_for_timeout(900)
        bet = pg.evaluate("TengelLocal.mem.bets.get('20261014-oi-09')"); print('[4] 保存:', bet.get('hp'))
        check(bet.get('hp') == {'人気→中穴': {'b': [7, 4], 't': [6, 10, 7, 1, 4]}}, '選んだ馬を保存（2着 7・4／3着 6・10・7・1・4）')
        pg.click('.tabbar button[data-tab=rec]'); pg.wait_for_timeout(500)
        row = pg.locator('#recList .lrow[data-id="20261014-oi-09"]'); s_line = row.locator('.lmid .s').inner_text(); print('[5] 記録タブ:', s_line)
        check('人気→中穴（2着 7・4／3着 6・10・7・1・4）' in s_line, '記録タブに選んだ馬')
        row.locator('.lmain').click(); pg.wait_for_timeout(300); row.locator('[data-act=load]').click(); pg.wait_for_timeout(700)
        check('off' in z2('b', 1).get_attribute('class') and 'off' in z2('t', 2).get_attribute('class'), '判定画面で開くと選んだ馬が戻る')
        pg.select_option('#fR', '10'); pg.wait_for_timeout(600)
        check(pg.locator('#result button.hp.off').count() == 0, 'レースが変わると選んだ馬はリセット')
        # ---- WIN5 ----
        pg.click('.tabbar button[data-tab=win5]'); pg.wait_for_timeout(500)
        d, bud = pg.locator('#w5Date').bounding_box(), pg.locator('#w5Budget').bounding_box()
        print('[6] 日付の欄', round(d['x']), '〜', round(d['x'] + d['width']), '／予算の欄', round(bud['x']), '〜', round(bud['x'] + bud['width']))
        check(d['x'] + d['width'] <= bud['x'] + 0.5 and abs(d['y'] - bud['y']) < 2, '日付と予算の欄が重ならない（横に並ぶ）')
        md = pg.locator('#w5Mode').bounding_box(); check(md['y'] > d['y'] + d['height'], 'ゾーンの選び方は下の段')
        sumt = lambda: pg.locator('#w5Sum').inner_text().replace('\n', ' ')
        picks = lambda i: [int(x.inner_text()) for x in pg.locator(f'#w5Races .w5race[data-i="{i}"] .w5picks .num:not(.off)').all()]
        offs = lambda i: [int(x.inner_text()) for x in pg.locator(f'#w5Races .w5race[data-i="{i}"] .w5picks .num.off').all()]
        print('[7] 自動:', sumt()[:40], [picks(i) for i in range(5)])
        p0 = [picks(i) for i in range(5)]
        add = offs(2)[0]
        pg.locator(f'#w5Races .w5race[data-i="2"] [data-w5h="{add}"]').click(); pg.wait_for_timeout(300)
        lab = pg.locator('#w5Races .w5race[data-i="2"] .w5lab').nth(1).inner_text(); print('    ③に', add, '番を足す →', picks(2), '|', lab, '|', sumt()[:60])
        check(add in picks(2) and '自分で選んだ馬' in lab and pg.locator('#w5Races .w5race[data-i="2"] [data-w5act=auto]').count() == 1, '番号を押すと自分で選べる（③は自分で選んだ馬・おまかせに戻すボタン）')
        check(json.loads(pg.evaluate("localStorage.getItem('tengel.win5')"))['races'][2]['man'] == picks(2), '自分で選んだ馬は保存される')
        pts = 1
        for i in range(5): pts *= len(picks(i))
        check(pts <= 30, f'ほかのレースは残りの予算で自動（{pts}点 ≤ 30点）')
        for no in offs(2): pg.locator(f'#w5Races .w5race[data-i="2"] [data-w5h="{no}"]').click(); pg.wait_for_timeout(150)
        pts = 1
        for i in range(5): pts *= len(picks(i))
        print('    ③を全部選ぶ →', picks(2), '|', sumt()[:90])
        check(len(picks(2)) == 9 and pts <= 30, f'自分で選んだ馬が増えたら、ほかのレースを減らして予算に合わせる（{pts}点）')
        for no in offs(3)[:4]: pg.locator(f'#w5Races .w5race[data-i="3"] [data-w5h="{no}"]').click(); pg.wait_for_timeout(150)
        pts = 1
        for i in range(5): pts *= len(picks(i))
        print('    ④も自分で選ぶ →', picks(3), '|', sumt()[:120])
        check(pts > 30 and 'こえているよ' in sumt() and 'bad' in pg.locator('#w5Sum .w5sum').get_attribute('class'), f'自分で選んだ馬だけで予算をこえたら赤で案内（{pts}点）')
        pg.locator('#w5Races .w5race[data-i="3"] [data-w5act=auto]').click(); pg.wait_for_timeout(200)
        one = picks(4)
        if len(one) == 1:
            pg.locator(f'#w5Races .w5race[data-i="4"] [data-w5h="{one[0]}"]').click(); pg.wait_for_timeout(200)
            check(picks(4) == one and '1頭は残してね' in (pg.locator('#toast').inner_text() if pg.locator('#toast').is_visible() else ''), '最後の1頭は外せない')
        pg.locator('#w5Races .w5race[data-i="2"] [data-w5act=auto]').click(); pg.wait_for_timeout(300)
        check([picks(i) for i in range(5)] == p0 and pg.locator('#w5Races [data-w5act=auto]').count() == 0, 'おまかせに戻すと予算に合わせた自動に戻る')
        pg.locator(f'#w5Races .w5race[data-i="0"] [data-w5h="{offs(0)[0]}"]').click(); pg.wait_for_timeout(200)
        pg.click('#w5Mode button[data-v=rand]'); pg.wait_for_timeout(300)
        check(all(r['man'] is None for r in json.loads(pg.evaluate("localStorage.getItem('tengel.win5')"))['races']), 'ランダムにすると自分で選んだ馬はおまかせに戻る')
        pg.click('#w5Mode button[data-v=pick]'); pg.wait_for_timeout(200)
        # 選んだ馬で○×（予算を下げて、外れている馬があるレースで試す）
        pg.fill('#w5Budget', '800'); pg.wait_for_timeout(300)
        i = next(k for k in range(5) if offs(k) and len(picks(k)) >= 1)
        mine = offs(i)[0]; pg.locator(f'#w5Races .w5race[data-i="{i}"] [data-w5h="{mine}"]').click(); pg.wait_for_timeout(250)
        pg.fill(f'#w5Win{i}', str(mine)); pg.wait_for_timeout(150)
        check(pg.locator(f'[data-w5mk="{i}"]').inner_text() == '○', f'{"①②③④⑤"[i]} 自分で足した馬（{mine}番）が1着なら○')
        drop = picks(i)[0]; pg.locator(f'#w5Races .w5race[data-i="{i}"] [data-w5h="{drop}"]').click(); pg.wait_for_timeout(250)
        pg.fill(f'#w5Win{i}', str(drop)); pg.wait_for_timeout(150)
        check(pg.locator(f'[data-w5mk="{i}"]').inner_text() == '×', f'外した馬（{drop}番）が1着なら×')
        pg.locator('#w5Body').screenshot(path=os.path.join(OUT, 'hpick_win5.png'))
        pg.click('.tabbar button[data-tab=judge]'); pg.wait_for_timeout(300)
        pg.locator('#result').screenshot(path=os.path.join(OUT, 'hpick_judge.png'))
        check(not errs, 'ページのエラーなし ' + str(errs[:3]))
finally:
    srv.terminate()
print('\nFAILS:', fails); sys.exit(1 if fails else 0)
