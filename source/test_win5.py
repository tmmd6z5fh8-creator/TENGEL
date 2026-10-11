# WIN5タブのテスト（iPhoneアプリ版）
#  ①〜⑤を判定画面で入れる（入れた内容はそのままWIN5に入る・WIN5に戻ると前の入力に戻る）／判定画面の「WIN5に入れる」
#  1着ゾーン（馬単ゾーンの1着側）・予算の中で頭数を決める・自分で選ぶ／ランダム・予算が足りないとき
#  1着の馬番 → ○×・的中／不的中、保存（bets に kind:'win5'・ふつうの記録には出ない）、開き直し・開く・上書き・消す
import json, os, re, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv'); PORT = 8776; URL = f'http://localhost:{PORT}/TENGEL/'; OUT = os.path.join(W, 't5'); os.makedirs(OUT, exist_ok=True)
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'TENGEL')], check=True, stdout=subprocess.DEVNULL)
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
fails, errs = [], []
def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label)
    if not c: fails.append(label)
ZN = ['人気', '中穴', '大穴', '超大穴']
def odds(n, tan1):
    xs = [tan1] + [round(tan1 + 1.9 * i + 0.35 * i * i, 1) for i in range(1, n)]
    nos = [(i * 5) % n + 1 for i in range(n)]            # 馬番は人気順とずらす
    return list(zip(nos, xs))
RACES = [  # 開催場, R, 距離, 頭数, 馬場, 単勝1位, 3連単1位 → 期待する区分
    ('東京', 9, 1600, 12, '良', 1.8, 12.0, 'A'),
    ('京都', 10, 1800, 14, '良', 2.0, 30.0, 'B'),
    ('東京', 10, 1400, 12, '稍重', 3.0, 70.0, 'C1'),
    ('京都', 11, 2000, 16, '良', 3.2, 80.0, 'C2'),
    ('東京', 11, 1600, 12, '良', 1.5, 9.0, 'A'),
]
CANDS = {'A': ['人気'], 'B': ['中穴', '人気'], 'C1': ['人気', '中穴', '大穴'], 'C2': ['人気', '中穴', '大穴']}
def fill_race(pg, venue, r, dist, n, baba, tan1, s1):
    pg.fill('#fVenue', venue); pg.fill('#fDate', '2026-10-18'); pg.select_option('#fR', str(r)); pg.fill('#fDist', str(dist))
    pg.fill('#fN', str(n)); pg.wait_for_timeout(100); pg.click(f'#fBaba button[data-v="{baba}"]'); pg.click('#fSurf button[data-v="芝"]')
    for no, t in odds(n, tan1): pg.fill(f'#oddsGrid input[data-no="{no}"][data-k="tan"]', str(t))
    pg.fill('#fS1', str(s1)); pg.wait_for_timeout(400)
def w5state(pg): return pg.evaluate("JSON.parse(localStorage.getItem('tengel.win5'))")
def zone_of(no, n, tan1):   # 馬番 → ゾーン（単勝オッズの低い順）
    ranked = [x[0] for x in sorted(odds(n, tan1), key=lambda x: (x[1], x[0]))]
    k = ranked.index(no) + 1
    return '人気' if k <= 3 else '中穴' if k <= 6 else '大穴' if k <= 9 else '超大穴' if k <= 12 else '対象外'
def card_info(pg, i):
    c = pg.locator(f'#w5Races .w5race[data-i="{i}"]')
    chips = [(b.inner_text().replace('推奨', '').strip(), b.get_attribute('aria-pressed'), '推奨' in b.inner_text(), b.is_disabled()) for b in c.locator('.w5zones button').all()]
    picks = [int(x.inner_text()) for x in c.locator('.w5picks .num:not(.off)').all()]
    return c.locator('.w5h').inner_text().replace('\n', ' '), chips, picks
try:
    with sync_playwright() as p:
        b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 900}, device_scale_factor=2); pg = ctx.new_page()
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(URL); pg.wait_for_timeout(1500)
        before_r, before_venue = pg.input_value('#fR'), pg.input_value('#fVenue')
        pg.click('.tabbar button[data-tab=win5]'); pg.wait_for_timeout(300)
        check(pg.locator('#w5Races .w5race').count() == 5 and pg.locator('#w5Races').inner_text().count('まだ入っていないよ') == 5, 'WIN5タブ：①〜⑤が空で並ぶ')
        # ①〜④は「判定画面で入れる」から
        for i, (v, r, d, n, baba, t1, s1, k) in enumerate(RACES[:4]):
            pg.click('.tabbar button[data-tab=win5]'); pg.wait_for_timeout(200)
            pg.locator(f'#w5Races [data-w5act=edit][data-i="{i}"]').click(); pg.wait_for_timeout(400)
            if i == 0:
                bn = pg.locator('#w5Banner').inner_text().replace('\n', ' '); print('[1] 入力中の案内:', bn[:90])
                check(pg.locator('#w5Banner').is_visible() and 'WIN5の①レース目を入力中' in bn, '判定画面にWIN5入力中の案内が出る')
                check(not pg.locator('#recCard').is_visible(), 'WIN5の入力中は「結果・収支の記録」を出さない')
            fill_race(pg, v, r, d, n, baba, t1, s1)
            kub = pg.locator('#result .vkubun').inner_text()
            print(f'    {"①②③④"[i]} {v}{r}R →', kub.replace('\n', ' '))
        st = w5state(pg); print('    WIN5に入ったレース:', [(x['form'] or {}).get('venue', '') + str((x['form'] or {}).get('r', '')) for x in st['races']])
        check([bool(x['form']) for x in st['races']] == [True, True, True, True, False], '①〜④に入った（入れた内容がそのままWIN5に入る）')
        pg.locator('#w5Banner [data-w5back]').click(); pg.wait_for_timeout(400)
        print('    戻ったあとの判定画面:', pg.input_value('#fVenue'), pg.input_value('#fR'), '| 前:', before_venue, before_r)
        check(pg.input_value('#fR') == before_r and pg.input_value('#fVenue') == before_venue, 'WIN5に戻ると、判定画面は前の入力に戻る')
        check(not pg.locator('#w5Banner').is_visible() and pg.locator('#v-win5').is_visible(), 'WIN5タブに戻った')
        # ⑤は判定画面でふつうに入れて「WIN5に入れる ⑤」
        pg.click('.tabbar button[data-tab=judge]'); pg.wait_for_timeout(200); pg.click('#clearBtn'); pg.wait_for_timeout(200)
        v, r, d, n, baba, t1, s1, k = RACES[4]; fill_race(pg, v, r, d, n, baba, t1, s1)
        pg.locator('#result [data-w5push="5"]').click(); pg.wait_for_timeout(300)
        print('[2] WIN5に入れる⑤ →', pg.locator('#toast').inner_text() if pg.locator('#toast').is_visible() else '')
        check(w5state(pg)['races'][4]['form']['r'] == '11', '判定画面の「WIN5に入れる ⑤」で入った')
        # 予算3000円 → 30点以内
        pg.click('.tabbar button[data-tab=win5]'); pg.wait_for_timeout(300)
        pg.fill('#w5Budget', '3000'); pg.wait_for_timeout(300)
        sumt = pg.locator('#w5Sum').inner_text().replace('\n', ' '); print('[3] 予算3000円:', sumt)
        infos = [card_info(pg, i) for i in range(5)]
        pts = 1
        for i, (h, chips, picks) in enumerate(infos):
            k = RACES[i][7]; cands = [c[0] for c in chips if c[2]]
            print(f'    {"①②③④⑤"[i]}', h[:40], '| 推奨', cands, '| 選択', [c[0] for c in chips if c[1] == 'true'], '| 買う', picks)
            check(cands == [z for z in ZN if z in CANDS[k]], f'{"①②③④⑤"[i]} 推奨の1着ゾーン {CANDS[k]}')
            zs = {zone_of(no, RACES[i][3], RACES[i][5]) for no in picks}
            check(picks and zs <= set(CANDS[k]), f'{"①②③④⑤"[i]} 買う馬は選んだゾーンの中（{zs}）')
            pts *= len(picks)
        check(pts <= 30 and f'{pts}点' in sumt, f'5レースの点数 {pts}点 ≤ 30点（予算3000円）')
        check(pts >= 20, f'予算をほどよく使う（{pts}点）')
        pg.locator('#w5Body').screenshot(path=os.path.join(OUT, 'win5_plan.png'))
        # 自分で選ぶ：②（B層）の人気を外す → 中穴だけ
        pg.locator('#w5Races .w5race[data-i="1"] [data-w5z="人気"]').click(); pg.wait_for_timeout(300)
        h, chips, picks = card_info(pg, 1)
        check([c[0] for c in chips if c[1] == 'true'] == ['中穴'] and {zone_of(no, 14, 2.0) for no in picks} == {'中穴'}, f'②の人気を外すと中穴だけ（{picks}）')
        # ランダム
        pg.click('#w5Mode button[data-v=rand]'); pg.wait_for_timeout(300)
        st = w5state(pg); sels = [x['sel'] for x in st['races']]; print('[4] ランダム:', sels)
        check(st['mode'] == 'rand' and all(len(s_) == 1 and s_[0] in CANDS[RACES[i][7]] for i, s_ in enumerate(sels)), 'ランダム：各レース、推奨の1着ゾーンから1つ')
        seen = set()
        for _ in range(12):
            pg.locator('[data-w5act=roll]').click(); pg.wait_for_timeout(120); seen.add(json.dumps([x['sel'] for x in w5state(pg)['races']]))
        check(len(seen) >= 3, f'「ランダムでもう一回」で変わる（{len(seen)}通り）')
        pg.check('#w5RandAll'); pg.wait_for_timeout(100)
        allz = set()
        for _ in range(25):
            pg.locator('[data-w5act=roll]').click(); pg.wait_for_timeout(60); allz.update(x['sel'][0] for x in w5state(pg)['races'])
        check('超大穴' in allz or len(allz) == 4, f'「推奨以外もまぜる」で推奨以外のゾーンも出る（{sorted(allz)}）')
        pg.uncheck('#w5RandAll')
        # 自分で選ぶに戻して、ゾーンを推奨に
        pg.click('#w5Mode button[data-v=pick]'); pg.wait_for_timeout(200)
        for i in range(5):
            st = w5state(pg); want = CANDS[RACES[i][7]]
            for z in ZN:
                on = z in st['races'][i]['sel']
                if (z in want) != on and not (on and len(st['races'][i]['sel']) == 1 and z not in want):
                    pg.locator(f'#w5Races .w5race[data-i="{i}"] [data-w5z="{z}"]').click(); pg.wait_for_timeout(120); st = w5state(pg)
            st = w5state(pg)
            if st['races'][i]['sel'] != want and [z for z in st['races'][i]['sel'] if z not in want]:
                for z in [z for z in st['races'][i]['sel'] if z not in want]: pg.locator(f'#w5Races .w5race[data-i="{i}"] [data-w5z="{z}"]').click(); pg.wait_for_timeout(120)
        check([sorted(x['sel']) for x in w5state(pg)['races']] == [sorted(CANDS[r[7]]) for r in RACES], '自分で選ぶ：推奨のゾーンに戻した')
        # 予算が足りない・多いとき
        pg.fill('#w5Budget', '50'); pg.wait_for_timeout(250); t = pg.locator('#w5Sum').inner_text(); print('[5] 予算50円:', t.replace('\n', ' '))
        check('100円以上' in t, '予算が100円未満なら案内')
        pg.fill('#w5Budget', '1000000'); pg.wait_for_timeout(250); t = pg.locator('#w5Sum').inner_text().replace('\n', ' ')
        full = 1
        for i in range(5): full *= len(card_info(pg, i)[2])
        print('    予算100万円:', t[:60], '| 全部買うと', full, '点'); check(full == 3 * 6 * 9 * 9 * 3, '予算が多ければ、選んだゾーンの馬を全部買う（3×6×9×9×3）')
        pg.fill('#w5Budget', '2000'); pg.wait_for_timeout(300)
        infos = [card_info(pg, i) for i in range(5)]; pts = 1
        for x in infos: pts *= len(x[2])
        check(pts <= 20, f'予算2000円 → {pts}点')
        # 結果：1着の馬番 → ○×
        picks = [x[2] for x in infos]
        for i in range(4): pg.fill(f'#w5Win{i}', str(picks[i][0])); pg.wait_for_timeout(80)
        t = pg.locator('#w5Status').inner_text().replace('\n', ' '); print('[6] 4レース当たり:', t, [pg.locator(f'[data-w5mk="{i}"]').inner_text() for i in range(5)])
        check('結果待ち' in t and [pg.locator(f'[data-w5mk="{i}"]').inner_text() for i in range(4)] == ['○'] * 4, '4レースまで○で結果待ち')
        notpick = next(no for no, _ in odds(12, 1.5) if no not in picks[4])
        pg.fill('#w5Win4', str(notpick)); pg.wait_for_timeout(150)
        t = pg.locator('#w5Status').inner_text().replace('\n', ' '); print('    ⑤が外れ:', t); check('不的中' in t and pg.locator('[data-w5mk="4"]').inner_text() == '×', '1つ外れたら不的中（⑤×）')
        pg.fill('#w5Win4', str(picks[4][0])); pg.wait_for_timeout(150)
        t = pg.locator('#w5Status').inner_text().replace('\n', ' '); print('    全部当たり:', t); check('的中' in t and '不的中' not in t, '5レース全部当たりで的中')
        pg.fill('#w5Pay', '125000'); pg.wait_for_timeout(150)
        check(f'{pts * 100:,}→125,000' in pg.locator('#w5Status').inner_text().replace('\n', ' '), '購入額は点数×100円で自動・払戻から収支')
        # 保存
        pg.locator('[data-w5act=save]').click(); pg.wait_for_timeout(900)
        rec = pg.evaluate("[...TengelLocal.mem.bets.values()].find(b => b.kind === 'win5')")
        print('[7] 保存:', rec and {k: rec[k] for k in ('id', 'kind', 'date', 'points', 'stake', 'payout')}, '| picks', rec and [r['picks'] for r in rec['races']])
        check(rec and rec['id'] == '20261018-win5' and rec['points'] == pts and rec['stake'] == pts * 100 and rec['payout'] == 125000, 'WIN5の記録を保存（bets に kind:win5）')
        lst = pg.locator('#w5ListCard').inner_text().replace('\n', ' '); print('    WIN5の記録:', lst[:160])
        check('的中' in lst and '1回' in lst, 'WIN5の記録に並ぶ（的中・1回）')
        pg.click('.tabbar button[data-tab=rec]'); pg.wait_for_timeout(400)
        check('この月の記録はまだないよ' in pg.locator('#recList').inner_text() or pg.locator('#recList .lrow').count() == 0, 'ふつうの記録タブには出ない')
        check('記録 0件' in pg.locator('#dbpill').inner_text(), f'上の「記録 N件」はふつうの記録だけ（{pg.locator("#dbpill").inner_text()}）')
        # 開き直しても残る
        pg.reload(); pg.wait_for_timeout(1500); pg.click('.tabbar button[data-tab=win5]'); pg.wait_for_timeout(400)
        check(pg.locator('#w5Races .w5race .w5picks').count() == 5 and pg.locator('#w5Win0').input_value() == str(picks[0][0]), '開き直しても5レース・結果が残る')
        # 新しいWIN5 → 記録を開く → 払戻を直して上書き
        nb = pg.locator('[data-w5act=new]'); nb.click(); nb.click(); pg.wait_for_timeout(300)
        check(pg.locator('#w5Races').inner_text().count('まだ入っていないよ') == 5, '新しいWIN5にすると空になる')
        pg.locator('#w5ListCard .w5rec [data-w5act=open]').first.click(); pg.wait_for_timeout(400)
        check(pg.locator('#w5Races .w5race .w5picks').count() == 5 and '保存した記録' in pg.locator('#w5Body').inner_text(), '記録を開くと5レースと買い目が戻る')
        pg.fill('#w5Pay', '130000'); pg.wait_for_timeout(100); pg.locator('[data-w5act=save]').click(); pg.wait_for_timeout(900)
        rec = pg.evaluate("TengelLocal.mem.bets.get('20261018-win5')")
        check(rec and rec['payout'] == 130000 and len([b for b in pg.evaluate("[...TengelLocal.mem.bets.values()]") if b.get('kind') == 'win5']) == 1, '開いた記録を上書き保存（1件のまま）')
        # 消す
        pg.locator('#w5ListCard [data-w5act=del1]').first.click(); pg.wait_for_timeout(100); pg.locator('#w5ListCard [data-w5act=del2]').click(); pg.wait_for_timeout(700)
        check(pg.evaluate("TengelLocal.mem.bets.has('20261018-win5')") is False, '記録を消せる')
        check(not errs, 'ページのエラーなし ' + str(errs[:3]))
finally:
    srv.terminate()
print('\nFAILS:', fails); sys.exit(1 if fails else 0)
