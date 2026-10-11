# 大井のデータを足した版への更新のテスト（例：2026.10.11-4・10/7まで280走 → 2026.10.11-5・10/9まで302走）
#  A) アプリに入っている大井データのまま使っている → 更新 → 新しいデータになる・お知らせが出る・記録は消えない
#  B) マザーデータのExcel（古い版）を入れていた → 更新 → アプリの新しいデータに入れ替わる・お知らせ・「ひとつ前に戻す」でExcelの版に戻せる
#  C) 新しい版で、新しいマザーデータのExcelを選ぶ → 「いまと同じ内容」
#  D) 判定の参考的中率が新しい母数で出る
# 使い方：OLD_APP=<今の公開版> XL_OLD=<前のマザーデータExcel> XL_NEW=<新しいマザーデータExcel> NEW_VER=2026.10.11-5 python3 test_update.py
import json, os, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv'); APPDIR = os.path.join(SRV, 'TENGEL'); OUT = os.path.join(W, 't5'); os.makedirs(OUT, exist_ok=True)
PORT = 8772; URL = f'http://localhost:{PORT}/TENGEL/'
OLD, XL_OLD, XL_NEW = os.environ['OLD_APP'], os.environ['XL_OLD'], os.environ['XL_NEW']
NEW = os.environ.get('NEW_VER', '2026.10.11-5')
hist = json.load(open('hist.json', encoding='utf8'))
N_ALL, N_USE = len(hist), sum(1 for r in hist if r.get('cnt', 1) == 1 and r.get('p1') and r.get('p2'))
LAST = max(r['date'] for r in hist); LAST_MD = '%d/%d' % (int(LAST[5:7]), int(LAST[8:10]))
# 層ごとの母数（エンジンで数える）
LAYER_N = json.loads(subprocess.run(['node', '-e', "const T=require('./engine.js');const h=require('./hist.json');const c={};h.map(T.derive).filter(d=>d.inStats).forEach(d=>c[d.L]=(c[d.L]||0)+1);console.log(JSON.stringify(c))"], capture_output=True, text=True, check=True).stdout)
print('新しいデータ:', N_ALL, '走・集計対象', N_USE, '走・', LAST, '| 層ごと', LAYER_N)

def deploy_dir(src):
    shutil.rmtree(APPDIR, ignore_errors=True); shutil.copytree(src, APPDIR, ignore=shutil.ignore_patterns('.git', 'README.md', 'source'))
def build(app_ver, out='pwa_t'):
    subprocess.run(['python3', 'build_pwa.py', out], check=True, env=dict(os.environ, APP_VER=app_ver), stdout=subprocess.DEVNULL)   # hist.json と MOTHER_VER はふだんの値
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
def src1(pg): return pg.evaluate("TengelLocal.slots.info()[0].source")
def text(pg, sel): return pg.locator(sel).inner_text().replace('\n', ' | ')
def update(pg, label):
    pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(300)
    pg.click('#suCheck'); pg.wait_for_timeout(800)
    bar = text(pg, '#updBar') if pg.locator('#updBar').is_visible() else ''
    print(f'    {label} 更新のお知らせ:', bar)
    with pg.expect_navigation(timeout=15000): pg.click('#updGo')
    toasts = []
    for _ in range(16):
        pg.wait_for_timeout(250)
        t = pg.locator('#toast')
        if t.is_visible(): toasts.append(t.inner_text())
    return bar, list(dict.fromkeys(toasts))
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
        # 公開版で、A＝そのまま使う人（記録1件）、B＝前のマザーデータExcelを入れた人
        A = newpage(); old_ver = A.evaluate('window.__APP_VER'); a0 = info(A)
        print('[0] 公開版', old_ver, 'A:', a0, src1(A))
        A.click('#sampleBtn'); A.wait_for_timeout(300); A.fill('#fDate', '2026-10-10'); A.wait_for_timeout(400)
        card = A.locator('#recCard'); card.locator('[data-k=stake]').fill('1000'); card.locator('[data-k=res]').fill('7-6-2'); card.locator('[data-act=save]').click(); A.wait_for_timeout(500)
        check(A.evaluate('TengelLocal.mem.bets.size') == 1, 'Aの記録1件')
        B = newpage()
        B.click('.tabbar button[data-tab=set]'); B.wait_for_timeout(300)
        B.set_input_files('#smFile', XL_OLD); B.wait_for_timeout(1500)
        print('    B: 前のExcel →', text(B, '#smPreview')[:120])
        B.click('#smApply'); B.wait_for_timeout(900)
        b0 = info(B); print('    B:', b0, src1(B)); check(src1(B) == 'excel' and b0.split()[0] == a0.split()[0], 'Bは前のExcelを入れた状態（中身は公開版と同じ）')

        # 新しい版を公開 → A・B それぞれアプリ内で更新
        deploy_dir(build(NEW))
        bar, toasts = update(A, 'A')
        a1 = info(A); print('[A] 更新後', A.evaluate('window.__APP_VER'), a1, src1(A), '| toast:', toasts)
        check(A.evaluate('window.__APP_VER') == NEW, 'Aは新しい版になった')
        check(a1.startswith(f'1:{N_ALL}/{N_USE}*'), f'Aの大井が新しいデータ（{N_ALL}走・集計対象{N_USE}走）になった')
        check(any(f'データが新しくなったよ（{N_ALL}走・{LAST_MD}まで）' in t for t in toasts), 'Aにお知らせが出た')
        check(A.evaluate('TengelLocal.mem.bets.size') == 1, 'Aの記録は消えていない')
        check(A.evaluate('TengelLocal.slots.prev(1)') is None, 'Aはアプリの版どうしなので「ひとつ前」は作らない')
        bar, toasts = update(B, 'B')
        b1 = info(B); pv = B.evaluate('TengelLocal.slots.prev(1)')
        print('[B] 更新後', B.evaluate('window.__APP_VER'), b1, src1(B), '| toast:', toasts, '| prev:', pv)
        check(b1.startswith(f'1:{N_ALL}/{N_USE}*') and src1(B) == 'app', 'Bの大井もアプリの新しいデータに入れ替わった（Excelのほうが古いから）')
        check(any('新しくなったよ' in t and 'ひとつ前' in t for t in toasts), 'Bにお知らせ（ひとつ前に戻せる）が出た')
        check(pv and pv['n'] == int(b0.split()[0].split(':')[1].split('/')[0]) and pv['source'] == 'excel', 'Bの前のExcelのデータは「ひとつ前」に残っている')

        # 開き直しても入れ替わったまま（お知らせも出ない）
        A.reload(); A.wait_for_timeout(1500)
        check(info(A).startswith(f'1:{N_ALL}/{N_USE}*') and not A.locator('#toast').is_visible(), '開き直しても新しいデータのまま・お知らせは1回だけ')

        # C) 新しいマザーデータのExcel → いまと同じ内容
        A.click('.tabbar button[data-tab=set]'); A.wait_for_timeout(300)
        A.set_input_files('#smFile', XL_NEW); A.wait_for_timeout(1500)
        t = text(A, '#smPreview'); print('[C] 新しいExcel →', t[:200])
        check(f'{N_ALL}走' in t and 'いまと同じ内容' in t, '新しいExcelはアプリの中のデータと同じ内容')
        A.locator('#setMother').screenshot(path=os.path.join(OUT, 'update_mother.png'))

        # D) 判定の参考的中率が新しい母数
        A.click('.tabbar button[data-tab=judge]'); A.wait_for_timeout(300); A.click('#sampleBtn'); A.wait_for_timeout(600)
        kub = A.locator('#result .vkubun').inner_text(); z = [x.inner_text() for x in A.locator('#result .zref').all()]
        L = 'A' if 'A層' in kub else 'B' if 'B層' in kub else 'C'
        print('[D] 入力例の区分:', kub.replace('\n', ' '), '| 参考値:', z[:2])
        check(z and f'n={LAYER_N[L]}' in z[0], f'参考的中率が新しい母数（{L}層 n={LAYER_N[L]}）で出る')
        check(not errs, 'ページのエラーなし ' + str(errs[:3]))
finally:
    srv.terminate()
print('\nFAILS:', fails); sys.exit(1 if fails else 0)
