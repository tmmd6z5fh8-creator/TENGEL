# 使い方の 絵（第4.243版：判定の「オッズ画像から読み取る」・作戦会議の「📷 画像から読み取る」の 横の「！」から 開く 使い方：pt_note.js の TengelHelp）
#   まさちゃん 2026/11/29 01:11「判定の画像読み込みの横にもビックリマークつけて、タップすると、どんな画像を読み込めばいいか(画像をつけて)、買い目予約の仕方(画像をつけて)、
#     結果入力、結果記録の説明が出てくるようにして！ あと、作戦会議の画像読み込みの横にもビックリマークをつけて、タップするとどんな画像を読み込めばいいか(画像つけて)
#     どんなことができるか画像つきで説明が出てくるようにして！」
#   ・読み込む 画像の 見本＝架空の オッズ画面・出馬表（testdata/ocr/make_mock.py の 画面。開催場は 架空の「青空」「星空」〈出馬表の「5回青空7日」は 漢字で 読む〉・馬の 名前・騎手は 架空）
#   ・アプリの 画面＝いまの アプリ（App Store版）を 架空の レースで 動かして 撮る（説明書の 写真〈manual/tools/shots_app.py〉と 同じ やり方：画像の 読み取りは
#     見本の 画面の「読めた 文字」〈testdata/ocr/*.json〉を 返す にせものの 端末・開催場の 名前は 写さない）
#   出す もの：help/img/hp_*.webp（リポジトリに 入れる：まさちゃんの 絵は 入って いない）→ build_pwa.py が App Store版の manual/ に 入れる（アプリの Resources）
#     hp_odds（単勝の 画面）・hp_tri（3連単の 人気順）・hp_ocr（読み込んだ あとの 入力）・hp_buy（買い目）・hp_rsv（記録タブの 結果待ち）・hp_res（1〜3着）・
#     hp_pay（購入額 → 払戻）・hp_rec（記録に 残った 行）・hp_stat（実測・回収の 札）・hp_card（出馬表）・hp_pform（作戦会議の 予約の 欄）・hp_plan（やりたい レースの ボード）・hp_oshi（推し馬）
#   python3 help/help_art.py   → 作り直したら pt_note.js の HPI（絵の 大きさ）を 合わせる（さいごに 出る 1行：test_v243.py が 見くらべる）
import json, os, re, shutil, subprocess, sys, time
from datetime import datetime, timedelta, timezone
from playwright.sync_api import sync_playwright
from PIL import Image
H = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.dirname(H); OUT = os.path.join(H, 'img'); os.makedirs(OUT, exist_ok=True)
TMP = os.path.join(SRC, 'srv', 'help_art'); PORT = int(os.environ.get('PORT', '8797')); BASE = f'http://localhost:{PORT}'
Q = int(os.environ.get('Q', '82')); WMAX = 720
JST = timezone(timedelta(hours=9)); D1 = datetime.now(JST) + timedelta(days=1)      # あした（締切済みに ならない 日）
WD = '月火水木金土日'
md = lambda d: f'{d.month}月{d.day}日'
ONLY = [x for x in os.environ.get('ONLY', '').split(',') if x]
DIMS = {}


def webp(png, name):
    im = Image.open(png).convert('RGB')
    if im.width > WMAX: im = im.resize((WMAX, round(im.height * WMAX / im.width)), Image.LANCZOS)
    p = os.path.join(OUT, name + '.webp'); im.save(p, 'WEBP', quality=Q, method=6)
    DIMS[name] = list(im.size); print('  🖼', name, im.size, os.path.getsize(p) // 1024, 'KB', flush=True)


# ---------- ① 読み込む 画像の 見本（make_mock.py の 画面：開催場は 架空・日付は あした）----------
mm = open(os.path.join(SRC, 'testdata', 'ocr', 'make_mock.py'), encoding='utf8').read()
mm = mm[mm.index('W, H = 390, 844'):mm.index('PAGES = {')]
D2, D3 = D1 + timedelta(days=1), D1 + timedelta(days=2)
DAYS = [('2026年11月28日(土曜)', f'{D1.year}年{md(D1)}({WD[D1.weekday()]}曜)'), ('11月28日(土曜)', f'{md(D1)}({WD[D1.weekday()]}曜)'),
        ('11月29日(日曜)', f'{md(D2)}({WD[D2.weekday()]}曜)'), ('11月30日(月曜)', f'{md(D3)}({WD[D3.weekday()]}曜)'), ('10月14日(水)', f'{md(D1)}({WD[D1.weekday()]})')]


def subst(s, pairs, days=True):
    """言いかえ（日付は いったん @D0@〜 に して から：11/28 → 11/30 → 12/2 の ように 連鎖しない）"""
    for a, b in pairs:
        assert a in s, a
        s = s.replace(a, b)
    if days:
        for i, (a, _) in enumerate(DAYS): s = s.replace(a, f'@D{i}@')
        for i, (_, b) in enumerate(DAYS): s = s.replace(f'@D{i}@', b)
    return s


SUB = [('大井競馬 第9競走', '青空競馬 第9競走'), ('大井競馬場 9R', '青空競馬場 9R'), ("venue='京都'", "venue='青空'"), ('["東京", "京都"]', '["星空", "青空"]'), ('["東京"]', '["星空"]'), ('(栗東)', '(青空)')]
mm = subst(mm, SUB)
NS = {'json': json, 'os': os, 'sys': sys}
exec(mm, NS)
CARD = NS['page_g']('青空', 11, 'テンゲルステークス', '3歳以上 オープン (混合)(特指) 別定', 'コース 1600m 芝・右 発走15:35', '本賞金(万円):2300、920、580、350、230')
MOCK = {'hp_odds': (NS['page_a'](), 600), 'hp_tri': (NS['page_c'](), 600), 'hp_card': (CARD, 700)}
for k, (body, _) in MOCK.items():
    assert not any(w in body for w in ('大井', '京都', '東京', '栗東', 'JRA', '11月28日')), k
# 画像の 読み取りの にせもの：見本の 画面の「読めた 文字」（testdata/ocr）を 同じ 言いかえで
OCR = os.path.join(SRC, 'testdata', 'ocr')


def lines(name, subs):
    L = json.load(open(os.path.join(OCR, name + '.json'), encoding='utf8'))['lines']
    s = subst(json.dumps(L, ensure_ascii=False), subs)
    assert not any(w in s for w in ('大井', '京都', '東京', '栗東')), name
    return json.loads(s)


OCR_A = lines('a_tanfuku_waku', [('大井競馬', '青空競馬')])
OCR_C = lines('c_sanrentan', [('大井競馬場', '青空競馬場')])
OCR_G = lines('h_card', [('京都', '青空'), ('東京', '星空'), ('栗東', '青空')])

# ---------- ② アプリ（App Store版）----------
shutil.rmtree(TMP, ignore_errors=True); os.makedirs(TMP)
subprocess.run(['node', 'build.js'], cwd=SRC, check=True, stdout=subprocess.DEVNULL)
ENV = dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, TARGET='app', DATA_URL=f'{BASE}/remote/none.json')
subprocess.run(['python3', 'build_pwa.py', os.path.join(TMP, 'APP')], cwd=SRC, check=True, stdout=subprocess.DEVNULL, env=ENV)
pth = os.path.join(TMP, 'APP', 'index.html'); h = open(pth, encoding='utf8').read()
assert "window.__NATIVE = location.protocol === 'tengel:';" in h
open(pth, 'w', encoding='utf8').write(h.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
t = open(os.path.join(SRC, 'test_native.py'), encoding='utf8').read()
FAKE = re.search(r'^FAKE = """(.*?)"""', t, re.S | re.M).group(1)
HIDE = ".tabbar,.minibar,#toast{display:none!important}.top{position:static!important}"
# 読み込む 前の 入力は 空（日付は あした）
EMPTY = {"id": None, "venue": "", "date": D1.strftime('%Y-%m-%d'), "r": "", "dist": "", "surface": "ダ", "baba": "良", "n": "", "tan1": "", "s1": "", "s1combo": "", "s5": "", "s5combo": "", "s10": "", "s10combo": "", "rows": [], "rname": "", "start": ""}
PLAN = {'v': 1, 'on': True, 'races': [
    {'id': 'p1', 'date': D1.strftime('%Y-%m-%d'), 'time': '15:35', 'name': '青空11R テンゲルステークス', 'n': 16, 'dist': 1600, 'venue': '青空', 'r': 11, 'memo': 'パドックを 見てから 決める', 'notify': [10, 5]},
    {'id': 'p2', 'date': D1.strftime('%Y-%m-%d'), 'time': '16:15', 'name': '青空12R 3歳以上2勝クラス', 'n': 14, 'dist': 1200, 'venue': '青空', 'r': 12, 'memo': '', 'notify': [15]}]}
OSHI = {'v': 1, 'list': [
    {'id': 'o1', 'name': 'テンゲルクイーン', 'ped': ['サンライズゴールド', 'ナイトレイン', 'ブルーハーバー', 'コスモスカイ', 'ミラクルアロー', 'ハッピーデイズ'] + [''] * 8, 'memo': '左回りが 得意', 'at': '2026-11-01T00:00:00Z'},
    {'id': 'o2', 'name': 'ロイヤルステップ', 'ped': ['シルバーウィンド', 'ドリームキャッチャー'] + [''] * 12, 'memo': '', 'at': '2026-11-02T00:00:00Z'}]}
errs = []


def hide(pg, on=True):
    pg.evaluate("([css, on]) => { let s = document.getElementById('shotcss'); if (on && !s) { s = document.createElement('style'); s.id = 'shotcss'; s.textContent = css; document.head.appendChild(s); } if (!on && s) s.remove(); }", [HIDE, on])


def shot(pg, name, sel, pad=0, max_h=None):
    if ONLY and name not in ONLY: return
    el = pg.locator(sel).first; el.scroll_into_view_if_needed(); pg.wait_for_timeout(300)
    tmp = os.path.join(TMP, name + '.png')
    if not pad and not max_h: el.screenshot(path=tmp, animations='disabled')
    else:
        bb = pg.evaluate("(s) => { const b = document.querySelector(s).getBoundingClientRect(); return { x: b.left + scrollX, y: b.top + scrollY, w: b.width, h: b.height }; }", sel)
        hh = min(bb['h'] + 2 * pad, max_h) if max_h else bb['h'] + 2 * pad
        pg.screenshot(path=tmp, full_page=True, clip={'x': max(0, bb['x'] - pad), 'y': max(0, bb['y'] - pad), 'width': bb['w'] + 2 * pad, 'height': hh}, animations='disabled')
    webp(tmp, name)


def shot_range(pg, name, root, top_sel, bot_sel, cut_css='', pad=8, fixed=False):
    """root の 中の top_sel の 上から bot_sel の 下まで（cut_css＝撮る 間だけ かくす 所：なくても よい 欄）"""
    if ONLY and name not in ONLY: return
    if cut_css: pg.evaluate("(c) => { const s = document.createElement('style'); s.id = 'shotcut'; s.textContent = c; document.head.appendChild(s); }", cut_css)
    pg.locator(root).first.scroll_into_view_if_needed(); pg.wait_for_timeout(300)
    bb = pg.evaluate("""([r, a, b]) => { const R = document.querySelector(r), A = R.querySelector(a), B = R.querySelector(b), rr = R.getBoundingClientRect(), ra = A.getBoundingClientRect(), rb = B.getBoundingClientRect();
      return { x: rr.left + scrollX, y: ra.top + scrollY, w: rr.width, h: rb.bottom - ra.top, sx: scrollX, sy: scrollY }; }""", [root, top_sel, bot_sel])
    tmp = os.path.join(TMP, name + '.png')
    if fixed:      # 画面に 止まって いる 窓（作戦会議）の 中：見えて いる 画面の 座標で
        pg.screenshot(path=tmp, clip={'x': bb['x'] - bb['sx'], 'y': bb['y'] - bb['sy'] - pad, 'width': bb['w'], 'height': bb['h'] + 2 * pad}, animations='disabled')
    else: pg.screenshot(path=tmp, full_page=True, clip={'x': bb['x'], 'y': bb['y'] - pad, 'width': bb['w'], 'height': bb['h'] + 2 * pad}, animations='disabled')
    if cut_css: pg.evaluate("() => { const s = document.getElementById('shotcut'); if (s) s.remove(); }")
    webp(tmp, name)


def nopad(pg):      # テンキー（numpad.js）を とじる（数字の 欄に 入れた あと：下の ボタンを ふさぐ）
    pg.evaluate("() => { try { document.activeElement && document.activeElement.blur && document.activeElement.blur(); window.TengelNumpad && TengelNumpad.hide(); } catch (e) {} }"); pg.wait_for_timeout(200)


def tab(pg, name):
    pg.evaluate("() => { try { document.activeElement && document.activeElement.blur && document.activeElement.blur(); window.TengelNumpad && TengelNumpad.hide(); } catch (e) {} }"); pg.wait_for_timeout(150)
    hide(pg, False); pg.click(f'.tabbar button[data-tab={name}]'); pg.wait_for_timeout(800); hide(pg, True)


def gate(pg):
    g = pg.locator('#gate')
    for _ in range(40):
        if not g.count() or g.evaluate('e => e.hidden'): return
        if pg.locator('#gateGo').count():
            if not g.evaluate("e => e.classList.contains('fade')"):
                try: pg.locator('#gateGo').click(timeout=3000)
                except Exception: pass
        else:
            try: g.click(timeout=500)
            except Exception: pass
        pg.wait_for_timeout(150)


srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', TMP], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
try:
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--lang=ja-JP'], env=dict(os.environ, LANG='ja_JP.UTF-8', LANGUAGE='ja'))      # 日付・時刻の 欄を 日本の 形（2026/11/30・15:35：iPhone と 同じ）
        # 見本の 画面（iPhone の 幅 390・2倍）
        c = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP')
        pg = c.new_page()
        for name, (body, hh) in MOCK.items():
            if ONLY and name not in ONLY: continue
            pg.set_content('<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">' + NS['CSS'] + '</head><body>' + body + '</body></html>')
            pg.wait_for_timeout(300); tmp = os.path.join(TMP, name + '.png')
            hh = min(hh, pg.evaluate("document.body.scrollHeight"))
            pg.screenshot(path=tmp, clip={'x': 0, 'y': 0, 'width': 390, 'height': hh}); webp(tmp, name)
        c.close()
        # アプリ
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, color_scheme='light', locale='ja-JP', timezone_id='Asia/Tokyo')
        mk = {}

        def marker(source, q):
            op, key = q.get('op'), q.get('key')
            if op == 'set': mk[key] = q.get('value', '1'); return {'ok': True}
            if op == 'del': mk.pop(key, None); return {'ok': True}
            v = mk.get(key); return {'ok': True, 'has': v is not None, 'value': v}
        ctx.expose_binding('__saveBackup', lambda s, t: None); ctx.expose_binding('__marker', marker)
        ctx.add_init_script(FAKE)
        ctx.add_init_script("document.addEventListener('DOMContentLoaded', function () { var s = document.createElement('style'); s.textContent = '#fabCol,#planBtn,#kiseBtn,#rvBtn{display:none!important}'; document.head.appendChild(s); });")
        ctx.add_init_script("if (!sessionStorage.getItem('x')) { sessionStorage.setItem('x', '1'); localStorage.setItem('tengel.form', %s); localStorage.setItem('tengel.plan', %s); localStorage.setItem('tengel.oshi', %s); }"
                           % tuple(json.dumps(json.dumps(v, ensure_ascii=False)) for v in (EMPTY, PLAN, OSHI)))
        ctx.route('**/__native/autobackup.json', lambda route: route.fulfill(status=404, body='not found'))
        pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(BASE + '/APP/'); pg.wait_for_timeout(1800); gate(pg); pg.wait_for_timeout(800)
        pg.evaluate("TengelFx.set({ effects: false })")
        hide(pg, True); pg.evaluate("scrollTo(0, 0)")
        # ---- ① 画像を 読み込む（単勝の 画面 ＋ 3連単の 人気順）----
        pg.evaluate("(L) => { window.__ocrLines = L; }", [OCR_A, OCR_C])
        pg.set_input_files('#ocrFile', [os.path.join(OCR, 'a_tanfuku_waku.jpg'), os.path.join(OCR, 'c_sanrentan.jpg')]); pg.wait_for_timeout(2800)
        assert pg.locator('#ocrHelp').count() == 1, '判定の「！」が ない'
        pg.evaluate("scrollTo(0, 0)"); pg.wait_for_timeout(200)
        shot_range(pg, 'hp_ocr', '.input-col > .card:nth-child(1)', ':scope > *', '#fDist', pad=10)
        # ---- ② 買い目（推奨ごとに 馬単の 行・3着の ある 推奨は 3連単の 行）→ 予約 ----
        nz = pg.locator('#result ol.zones > li').count(); t3 = pg.locator('#result .zthird .zref').count() > 0
        for tt in ['馬単'] * nz:
            pg.locator(f'#recCard [data-k=radd] button[data-v="{tt}"]').click(); pg.wait_for_timeout(150)
        for _ in range(4):      # 開いて いる 行（さいごに 足した 行）は とじて 撮る（馬の 表で 長く なる）
            o = pg.locator('#recCard .rline.open [data-k=rlopen]')
            if not o.count(): break
            o.first.click(); pg.wait_for_timeout(250)
        shot(pg, 'hp_buy', '#recCard')
        pg.locator('#recCard [data-rsv=reserve]').click(); pg.wait_for_timeout(1400)
        if pg.locator('#fxOv').count(): pg.evaluate("TengelFx.close()"); pg.wait_for_timeout(400)
        bid = pg.evaluate("[...TengelLocal.mem.bets.values()].find(x => x.rsv && x.rsv.state === 'reserved').id")
        tab(pg, 'rec')
        shot(pg, 'hp_rsv', f'#recList .lrow[data-id="{bid}"]', pad=6)
        # ---- ③ 結果（1〜3着）----
        pg.locator(f'#recList .lrow[data-id="{bid}"] .lmain').click(); pg.wait_for_timeout(600)
        f = pg.locator('#recList .rsvf')
        for k, v in (('p1', '6'), ('p2', '2'), ('p3', '10')): f.locator(f'[data-k={k}]').fill(v)
        f.locator('[data-k=p3]').dispatch_event('input'); pg.wait_for_timeout(400); nopad(pg)
        # 着順と「結果を決める」（なくても よい 欄〈馬の 名前・取消・レース・発走時刻・結果の 画像〉は 撮る 間 かくす）
        shot_range(pg, 'hp_res', '#recList .rsvf', '.hint', '[data-act=rsave]', '#recList .rsvf .f:has(.pln),#recList .rsvf .f.s3{display:none!important}')
        f.locator('[data-act=rsave]').click(); pg.wait_for_timeout(1600)
        if pg.locator('#fxOv').count(): pg.evaluate("TengelFx.close()"); pg.wait_for_timeout(600)
        # ---- ④ 金額（購入額 → 払戻）→ 記録 ----
        f = pg.locator('#recList .rsvf')
        f.locator('[data-k=payout][data-t="馬単"]').fill('680'); f.locator('[data-k=payout][data-t="馬単"]').dispatch_event('input'); pg.wait_for_timeout(200)
        if f.locator('[data-k=payout][data-t="3連単"]').count():
            f.locator('[data-k=payout][data-t="3連単"]').fill('2150'); f.locator('[data-k=payout][data-t="3連単"]').dispatch_event('input')
        pg.wait_for_timeout(300); nopad(pg)
        shot_range(pg, 'hp_pay', '#recList .rsvf', '.banner.info', '[data-act=rsave]', '#recList .rsvf .f:has([data-k=note]),#recList .rsvf .f:has([data-k=mfld]),#recList .rsvf [data-k=mfld]{display:none!important}')
        f.locator('[data-act=rsave]').click(); pg.wait_for_timeout(1400)
        if pg.locator('#fxOv').count(): pg.evaluate("TengelFx.close()"); pg.wait_for_timeout(500)
        if pg.locator(f'#recList .lrow[data-id="{bid}"] .lmain[aria-expanded=true]').count():
            pg.locator(f'#recList .lrow[data-id="{bid}"] .lmain').click(); pg.wait_for_timeout(500)
        pg.evaluate("scrollTo(0, 0)"); pg.wait_for_timeout(300)
        shot(pg, 'hp_rec', f'#recList .lrow[data-id="{bid}"]', pad=6)
        tab(pg, 'stats')
        shot(pg, 'hp_stat', '#moneyBody .money-tiles', pad=6)
        # ---- 作戦会議：やりたい レースの ボード・推し馬・予約の 欄（出馬表を 読み込んだ あと）----
        tab(pg, 'judge'); hide(pg, False)
        pg.evaluate("() => window.TCPlanOpen()")
        pg.wait_for_function("() => document.querySelector('#tcPlan [data-p=add]')", timeout=60000); pg.wait_for_timeout(800)
        shot(pg, 'hp_plan', '#tcPlan .pb')
        pg.evaluate("() => { const pb = document.querySelector('#tcPlan .pb'), o = document.querySelector('#tcPlan .oboard'); if (pb && o) pb.scrollTop = o.getBoundingClientRect().top - pb.getBoundingClientRect().top + pb.scrollTop - 8; }"); pg.wait_for_timeout(500)
        shot(pg, 'hp_oshi', '#tcPlan .oboard')
        pg.locator('#tcPlan [data-p=add]').first.click(); pg.wait_for_timeout(500)
        assert pg.locator('#tcPlan [data-p=help]').count() == 1, '作戦会議の「！」が ない'
        pg.evaluate("(L) => { window.__ocrLines = L; }", [OCR_G])
        pg.locator('#tcPlan input[data-p=file]').set_input_files([os.path.join(OCR, 'h_card.jpg')]); pg.wait_for_timeout(2400)
        got = pg.evaluate("() => { const r = document.querySelector('#tcPlan'), v = k => (r.querySelector(`[data-f=\"${k}\"]`) || {}).value || ''; return { name: v('name'), date: v('date'), time: v('time'), dist: v('dist'), msg: (r.querySelector('.om') || {}).innerText || '' }; }")
        print('  plan ocr', got)
        assert got['name'] == '青空11R テンゲルステークス' and got['time'] == '15:35' and got['dist'] == '1600' and got['date'] == D1.strftime('%Y-%m-%d'), got
        pg.evaluate("() => { const pb = document.querySelector('#tcPlan .pb'); if (pb) pb.scrollTop = 0; }"); pg.wait_for_timeout(300)
        shot_range(pg, 'hp_pform', '#tcPlan .fm', 'h3', '[data-f=dist]', pad=12, fixed=True)      # 名前・日付・発走・頭数・距離 まで（メモ・ボタンは 入れない）
        b.close()
finally:
    srv.terminate()
shutil.rmtree(TMP, ignore_errors=True)
print('errs', errs[:3])
print('HPI', json.dumps({k: DIMS[k] for k in sorted(DIMS)}))
