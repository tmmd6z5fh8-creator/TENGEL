# 大井のデータを入れ直した版への更新のテスト（今の公開版 → source/ から作った新しい版）
#  A) アプリに入っている大井データのまま使っている → 更新 → 新しいデータになる・お知らせ（重複を消したときはそれも）・記録は消えない
#  B1) 前のマザーデータExcel（最後の日付が古い）を入れていた → 更新 → アプリの新しいデータに入れ替わる・お知らせ・「ひとつ前に戻す」でExcelの版に戻せる
#  B2) 重複（dropped.json のレース）入りのExcel（最後の日付は同じ）を入れていた → 更新 → Excelのデータのまま、重複だけ消える・お知らせ
#  C) 新しい版で、重複入りのExcelを選ぶ → 「重複していた…は入れないよ」・入れても重複は入らない
#  D) 新しいマザーデータのExcelを選ぶ → 「いまと同じ内容」
#  E) 判定の参考的中率が新しい母数で出る
# 使い方：OLD_APP=<今の公開版> XL_OLD=<最後の日付が古いマザーデータExcel> XL_NEW=<新しいマザーデータExcel> [XL_DUP=<重複入りのExcel>] NEW_VER=… python3 test_update.py
import json, os, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv'); APPDIR = os.path.join(SRV, 'TENGEL'); OUT = os.path.join(W, 't5'); os.makedirs(OUT, exist_ok=True)
PORT = 8772; URL = f'http://localhost:{PORT}/TENGEL/'
OLD, XL_OLD, XL_NEW, XL_DUP = os.environ['OLD_APP'], os.environ['XL_OLD'], os.environ['XL_NEW'], os.environ.get('XL_DUP')
NEW = os.environ.get('NEW_VER', '2026.10.11-6')
hist = json.load(open('hist.json', encoding='utf8'))
dropped = json.load(open('dropped.json', encoding='utf8')) if os.path.exists('dropped.json') else []
N_DROP = sum(len(g['rs']) for g in dropped)
dup_ids = [g['date'].replace('-', '') + '-oi-%02d' % r for g in dropped for r in g['rs']]
HAS_DUP = f"{json.dumps(dup_ids)}.filter(id => TengelLocal.mem.races.has(id)).length"
N_ALL, N_USE = len(hist), sum(1 for r in hist if r.get('cnt', 1) == 1 and r.get('p1') and r.get('p2'))
LAST = max(r['date'] for r in hist); LAST_MD = '%d/%d' % (int(LAST[5:7]), int(LAST[8:10]))
LAYER_N = json.loads(subprocess.run(['node', '-e', "const T=require('./engine.js');const h=require('./hist.json');const c={};h.map(T.derive).filter(d=>d.inStats).forEach(d=>c[d.L]=(c[d.L]||0)+1);console.log(JSON.stringify(c))"], capture_output=True, text=True, check=True).stdout)
print('新しいデータ:', N_ALL, '走・集計対象', N_USE, '走・', LAST, '| 層ごと', LAYER_N, '| 重複で消したレース', N_DROP)

def deploy_dir(src):
    shutil.rmtree(APPDIR, ignore_errors=True); shutil.copytree(src, APPDIR, ignore=shutil.ignore_patterns('.git', 'README.md', 'source'))
def build(app_ver, out='pwa_t'):
    subprocess.run(['python3', 'build_pwa.py', out], check=True, env=dict(os.environ, APP_VER=app_ver), stdout=subprocess.DEVNULL)   # hist.json・MOTHER_VER・dropped.json はふだんの値
    return out
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
deploy_dir(OLD)
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
errs, fails = [], []
def check(cond, label):
    print(('  ✅ ' if cond else '  ❌ ') + label)
    if not cond: fails.append(label)
def info(pg):
    return pg.evaluate("async () => { await TengelLocal.ready; return TengelLocal.slots.info().map(s => `${s.n}:${s.count}/${s.usable}${s.active ? '*' : ''}`).join(' ') }")
def s1(pg): return pg.evaluate("TengelLocal.slots.info()[0]")
def text(pg, sel): return pg.locator(sel).inner_text().replace('\n', ' | ')
def n_of(i): return int(i.split()[0].split(':')[1].split('/')[0])
def update(pg, label):
    pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(300)
    pg.click('#suCheck'); pg.wait_for_timeout(800)
    print(f'    {label} 更新のお知らせ:', text(pg, '#updBar') if pg.locator('#updBar').is_visible() else '')
    with pg.expect_navigation(timeout=15000): pg.click('#updGo')
    toasts = []
    for _ in range(16):
        pg.wait_for_timeout(250)
        t = pg.locator('#toast')
        if t.is_visible(): toasts.append(t.inner_text())
    return list(dict.fromkeys(toasts))
def load_xl(pg, path):
    pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(300)
    pg.set_input_files('#smFile', path); pg.wait_for_timeout(1500)
    return text(pg, '#smPreview')
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        def newpage():
            ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, accept_downloads=True)
            pg = ctx.new_page()
            pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)))
            pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' and 'fonts.g' not in m.text and 'ERR_' not in m.text else None)
            pg.goto(URL); pg.wait_for_timeout(1500)
            return pg
        # 公開版で：A＝そのまま使う人（記録1件）、B1＝前のExcel、B2＝重複入りのExcel を入れた人
        A = newpage(); a0 = info(A); old_ver = A.evaluate('window.__APP_VER')
        print('[0] 公開版', old_ver, 'A:', a0, s1(A)['source'])
        A.click('#sampleBtn'); A.wait_for_timeout(300); A.fill('#fDate', '2026-10-10'); A.wait_for_timeout(400)
        card = A.locator('#recCard'); card.locator('[data-k=stake]').fill('1000'); card.locator('[data-k=res]').fill('7-6-2'); card.locator('[data-act=save]').click(); A.wait_for_timeout(500)
        check(A.evaluate('TengelLocal.mem.bets.size') == 1, 'Aの記録1件')
        a_dups = A.evaluate(HAS_DUP); print('    A: 公開版の大井データにある重複のレース', a_dups, '走')
        B1 = newpage(); print('    B1: 前のExcel →', load_xl(B1, XL_OLD)[:110]); B1.click('#smApply'); B1.wait_for_timeout(900)
        b1_0 = info(B1); b1_dups = B1.evaluate(HAS_DUP); print('    B1:', b1_0, s1(B1)['source'], s1(B1)['last'], '| 重複', b1_dups)
        if XL_DUP:
            B2 = newpage(); print('    B2: 重複入りのExcel →', load_xl(B2, XL_DUP)[:110]); B2.click('#smApply'); B2.wait_for_timeout(900)
            b2_0 = info(B2); print('    B2:', b2_0, s1(B2)['source'], s1(B2)['last'])

        # 新しい版を公開 → それぞれアプリ内で更新
        deploy_dir(build(NEW))
        toasts = update(A, 'A'); a1 = info(A)
        print('[A] 更新後', A.evaluate('window.__APP_VER'), a1, s1(A)['source'], '| toast:', toasts)
        check(A.evaluate('window.__APP_VER') == NEW, 'Aは新しい版になった')
        check(a1.startswith(f'1:{N_ALL}/{N_USE}*') and s1(A)['source'] == 'app', f'Aの大井が新しいデータ（{N_ALL}走・集計対象{N_USE}走）になった')
        want = f'データが新しくなったよ（{N_ALL}走・{LAST_MD}まで）'
        check(any(want in t for t in toasts), f'Aにお知らせ（{want}）')
        if a_dups: check(any(f'重複していたレース（{a_dups}走）は消したよ' in t for t in toasts), 'Aのお知らせに、重複を消したことも書いてある')
        check(A.evaluate('TengelLocal.mem.bets.size') == 1, 'Aの記録は消えていない')
        check(A.evaluate('TengelLocal.slots.prev(1)') is None, 'Aはアプリの版どうしなので「ひとつ前」は作らない')
        check(A.evaluate(HAS_DUP) == 0, 'Aに重複のレースは残っていない')

        toasts = update(B1, 'B1'); b1 = info(B1); pv = B1.evaluate('TengelLocal.slots.prev(1)')
        print('[B1] 更新後', b1, s1(B1)['source'], '| toast:', toasts, '| prev:', pv and {k2: pv[k2] for k2 in ('n', 'last', 'source')})
        check(b1.startswith(f'1:{N_ALL}/{N_USE}*') and s1(B1)['source'] == 'app', 'B1の大井はアプリの新しいデータに入れ替わった（Excelのほうが古いから）')
        check(any('新しくなったよ' in t and 'ひとつ前' in t for t in toasts), 'B1にお知らせ（ひとつ前に戻せる）')
        check(pv and pv['n'] == n_of(b1_0) - b1_dups and pv['source'] == 'excel', f'B1の前のExcelのデータは「ひとつ前」に残っている（重複を除いて{n_of(b1_0) - b1_dups}走）')
        B1.click('.tabbar button[data-tab=set]'); B1.wait_for_timeout(300); B1.click('#slotList .slotrow[data-n="1"] [data-sact=edit]'); B1.wait_for_timeout(300)
        ud = B1.locator('#seUndo'); print('    B1 ひとつ前ボタン:', ud.inner_text()); ud.click(); ud.click(); B1.wait_for_timeout(900)
        b1u = info(B1); print('    B1 ひとつ前に戻したあと', b1u, s1(B1)['source'])
        check(b1u.startswith(f'1:{n_of(b1_0) - b1_dups}/') and s1(B1)['source'] == 'excel' and B1.evaluate(HAS_DUP) == 0, 'B1は前のExcelのデータに戻せる（重複は入らない）')

        if XL_DUP:
            toasts = update(B2, 'B2'); b2 = info(B2); m = s1(B2)
            print('[B2] 更新後', b2, m['source'], m['file'], '| toast:', toasts)
            check(b2.startswith(f'1:{n_of(b2_0) - N_DROP}/') and m['source'] == 'excel', f'B2はExcelのデータのまま、重複の{N_DROP}走だけ消えた')
            check(any(f'重複していたレース（{N_DROP}走）を消したよ' in t for t in toasts), 'B2に重複を消したお知らせ')
            check(B2.evaluate(HAS_DUP) == 0, 'B2に重複のレースは残っていない')
            B2.reload(); B2.wait_for_timeout(1500)
            check(info(B2) == b2 and not B2.locator('#toast').is_visible(), '開き直しても同じ・お知らせは1回だけ')

        # C) 新しい版で重複入りのExcelを選ぶ → 重複は入れない
        if XL_DUP:
            t = load_xl(A, XL_DUP); print('[C] 重複入りのExcel →', t[:230])
            check(f'{N_DROP}走は入れないよ' in t and f'{N_ALL}走' in t, '重複のレースは入れないと案内')
            A.click('#smApply'); A.wait_for_timeout(900)
            c1 = info(A); print('    入れたあと', c1, s1(A)['source'])
            check(c1.startswith(f'1:{N_ALL}/{N_USE}*') and A.evaluate(HAS_DUP) == 0, 'Excelから入れても重複は入らない')
        # D) 新しいマザーデータのExcel → いまと同じ内容
        t = load_xl(A, XL_NEW); print('[D] 新しいExcel →', t[:200])
        check(f'{N_ALL}走' in t and 'いまと同じ内容' in t and '入れないよ' not in t, '新しいExcelはアプリの中のデータと同じ内容')
        A.locator('#setMother').screenshot(path=os.path.join(OUT, 'update_mother.png'))

        # E) 判定の参考的中率が新しい母数
        A.click('.tabbar button[data-tab=judge]'); A.wait_for_timeout(300); A.click('#sampleBtn'); A.wait_for_timeout(600)
        kub = A.locator('#result .vkubun').inner_text(); z = [x.inner_text() for x in A.locator('#result .zref').all()]
        L = 'A' if 'A層' in kub else 'B' if 'B層' in kub else 'C'
        print('[E] 入力例の区分:', kub.replace('\n', ' '), '| 参考値:', z[:1])
        check(z and f'n={LAYER_N[L]}' in z[0], f'参考的中率が新しい母数（{L}層 n={LAYER_N[L]}）で出る')
        check(not errs, 'ページのエラーなし ' + str(errs[:3]))
finally:
    srv.terminate()
print('\nFAILS:', fails); sys.exit(1 if fails else 0)
