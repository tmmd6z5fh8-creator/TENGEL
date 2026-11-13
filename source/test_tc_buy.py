# トレーニングセンター：お世話トークンの 購入（第4.165版）の テスト
#   まさちゃん 2026/11/13 11:46「3.お世話トークンは、購入できるようにする。①1個を80Pで購入 ②5個を400Pで購入 ③10個を800Pで購入 ④15個を1200Pで購入 ②25個を2000Pで購入
#     お世話トークン購入、のアイコンを左下のお世話などの項目の上に設置　アイコンは一枚目」・聞いて 決めた：持てる 数は 25こ まで（こえる 組は その ときは 買えない）
#   → 12:33「お世話トークン呼ぶのすぐ上にして！」→ 12:36「お世話トークン購入のアイコンやっぱりこっちで！（丸い 絵）お世話とかのところに上手く入れられない？」
#   → 12:38「1番右側に入れて！」→ 12:46「周りの大きさと合わせて！バランス調整して！」
#   ・下の 列（撫でる・ごはん・おそうじ・呼ぶ）の 1番 右に まさちゃんの 丸い 絵の ボタン（ほかと 同じ 大きさ・同じ 間かく・下に 名前「トークン購入」：tc_care.js が 描く）
#     → 購入の 窓（組 6つ・2回 押して 決める）→ ポイントが へって トークンが ふえる（台帳に 1件）
#   ・25こを こえる 組・ポイントが 足りない 組は 買えない・途中で 閉じても ずれない（買い物の しるし）・App Store版にも 入る
#   第4.168版（まさちゃん 2026/11/14 01:26「6.お世話トークン購入金額 ・1個100P ・5個500P ・10個1000P ・15個1500P ・20個2000P ・25個2500P」）：組は 6つ（20こが ふえた）・1こ あたり 100P
#   python3 test_tc_buy.py   （ios/tc_assets/ が ある とき だけ 画面の テスト。ない とき（CI）は 中身の 見くらべ と 絵が ない ときの 形）
import json, os, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv_tc'); PORT = 8797; APP = f'http://localhost:{PORT}/APP/'; STORE = f'http://localhost:{PORT}/STORE/'
SHOT = os.environ.get('SHOT')          # 画面を 写す フォルダ（見る 用）
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, TARGET='app', TENGEL_TEST='1'))
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'STORE')], check=True, stdout=subprocess.DEVNULL, env=dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, TARGET='app'))
from assets_dir import adir
TCA = adir('tc_assets'); HAVE = os.path.isdir(TCA) and len(os.listdir(TCA)) > 100
for d in ('APP', 'STORE'):
    pth = os.path.join(SRV, d, 'index.html'); html = open(pth, encoding='utf8').read()
    open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
    if HAVE:
        for f in os.listdir(TCA): shutil.copy(os.path.join(TCA, f), os.path.join(SRV, d, f))
if not HAVE: print('※ トレーニングセンターの 絵と 音（ios/tc_assets）が ない ので、中身の 見くらべ だけ')
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c: fails.append(label)


FAKE = open(os.path.join(W, 'test_tc.py'), encoding='utf8').read().split('FAKE = """')[1].split('"""')[0]      # アプリの 窓口の にせもの（test_tc.py と 同じ）
PACKS = [[1, 100], [5, 500], [10, 1000], [15, 1500], [20, 2000], [25, 2500]]


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


def stage_xy(pg, x, y):               # フィールドの 座標（1052×1657）→ 画面
    r = pg.evaluate("() => { const b = document.querySelector('#tcOv .tcst').getBoundingClientRect(); return [b.left, b.top, b.width, b.height]; }")
    return r[0] + x / 1052 * r[2], r[1] + y / 1657 * r[3]


def stage_click(pg, x, y):
    pg.mouse.click(*stage_xy(pg, x, y))


def shot(pg, name):
    if SHOT: os.makedirs(SHOT, exist_ok=True); pg.screenshot(path=os.path.join(SHOT, name + '.png'))


def open_tc(pg, url):
    pg.goto(url); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(600)
    pg.locator('#tcFab .fabi').click()
    pg.wait_for_function("() => window.TCApp && document.querySelector('#tcOv.on') && !document.querySelector('#tcOv .tcld')", timeout=120000)
    pg.evaluate("() => TCApp._t.govSet(0, true)"); pg.wait_for_timeout(1200)      # 絵の 細かさは かえない（おそい テストの 機械で 下がらない ように）
    pg.evaluate("() => { TCApp.state.stockAt = Date.now() + 7200000; }")          # テストの 間に 時間で たまらない ように（たまる ところは 下で 時刻を 決めて ためす）


def set_stock(pg, n):
    pg.evaluate("(n) => { const st = TCApp.state, S = TCCare.S; st.stock = n; S.stock = S.stockShow = n; st.stockAt = Date.now() + 7200000; }", n)


BUYXY = (924, 1494)                    # 下の 列の 1番 右の「お世話トークン購入」（フィールドの 座標：tc_care.js の BUYG）
OVPX = "(pts) => { const cv = document.querySelector('#tcOv .tco'), g = cv.getContext('2d'), k = cv.width / 1052; return pts.map(([x, y]) => Array.from(g.getImageData(Math.round(x * k), Math.round(y * k), 1, 1).data)); }"


def sheet(pg, want=True):             # 購入の 窓を ひらく（ボタンを 押す）／とじる
    if pg.evaluate("() => TCBuy.isOpen()") == want: return
    if want: stage_click(pg, *BUYXY); pg.wait_for_timeout(450)
    else: pg.wait_for_timeout(400); pg.locator('#tcb .bx').click(); pg.wait_for_timeout(250)


ROWS = "() => [...document.querySelectorAll('#tcb .brow')].map(r => [+r.dataset.n, r.dataset.s, r.querySelector('.bc').textContent, (r.querySelector('.bb, .bwhy') || {}).textContent || ''])"
NOW = "() => ({ stock: document.querySelector('#tcb [data-v=stock]').textContent, pts: document.querySelector('#tcb [data-v=points]').textContent, msg: document.querySelector('#tcb .bmsg').textContent, ng: document.querySelector('#tcb .bmsg').classList.contains('ng') })"
LED = "() => TengelWallet.events().filter(e => /^unlock-tctok:/.test(e.id)).map(e => [e.kind, e.amount, e.what.split(':').slice(0, 2).join(':'), e.id.split(':').length])"
try:
    # ---------- 中身の 見くらべ（絵が なくても）----------
    print('■ 中身：購入の 窓は App Store版にも テスト版にも 入る')
    tb = open(os.path.join(SRV, 'APP', 'tc_bundle.js'), encoding='utf8').read(); sb = open(os.path.join(SRV, 'STORE', 'tc_bundle.js'), encoding='utf8').read()
    si = open(os.path.join(SRV, 'STORE', 'index.html'), encoding='utf8').read()
    check(all('const TCBuy' in x and 'window.TCBuy = TCBuy' in x and "'tc_icon_buy2.webp'" in x and 'tc_icon_buy.webp' not in x and 'お世話トークン購入' in x and 'onBuy' in x and 'BUYG' in x and 'data-tc="buy"' not in x and 'tcby' not in x for x in (tb, sb)),
          'tc_bundle.js（App Store版・テスト版）に 購入の 窓（TCBuy）と 下の 列の ボタン（丸い 絵 tc_icon_buy2.webp・はじめの 横長の 絵と うかぶ ボタンは もう ない）')
    check('TOKEN_PACKS' in si and json.dumps(PACKS) in si.replace(json.dumps(PACKS, separators=(',', ':')), json.dumps(PACKS)) and '[1, 80]' not in si and '[1,80]' not in si and 'tctok:' in si,
          'index.html：組と 値段の 表（points.js の TOKEN_PACKS＝1こ 100P・5こ 500P・10こ 1,000P・15こ 1,500P・20こ 2,000P・25こ 2,500P：前の 80P の 表は ない）・台帳の 窓口（tctok）')
    check('confirm(' not in open(os.path.join(W, 'tc', 'tc_buy.js'), encoding='utf8').read().split('const TCBuy')[1] and 'alert(' not in open(os.path.join(W, 'tc', 'tc_buy.js'), encoding='utf8').read().split('const TCBuy')[1],
          '購入の 窓は confirm()・alert() の 窓を 使わない（アプリの 中では 出ない：2回 押して 決める）')
    lst = subprocess.run(['git', 'ls-files'], cwd=os.path.dirname(W), capture_output=True, text=True).stdout.split('\n')
    check(not any(f.endswith(('tc_icon_buy.webp', 'tc_icon_buy2.webp', 'src_buy_icon.png', 'src_buy_icon2.png')) or '/tc_assets/' in f or '/tc_buy/' in f for f in lst) and os.path.exists(os.path.join(W, 'kisekae', 'tc', 'buy_asset.py')),
          'まさちゃんの ボタンの 絵（もとの PNG・tc_icon_buy2.webp）は リポジトリに 入って いない・絵を 置く 道具（kisekae/tc/buy_asset.py）は ある')
    import assets_dir as _ad
    ex = _ad.expected('tc_assets') if os.path.isdir(_ad.master('tc_assets')) else None
    check(_ad.superseded('tc_assets', ['tc_icon_buy.webp', 'tc_icon_buy2.webp', 'tc_icon_plan.webp']) == {'tc_icon_buy.webp'} and _ad.superseded('tc_assets', ['tc_icon_buy.webp', 'tc_icon_plan.webp']) == set()
          and (ex is None or ('tc_icon_buy2.webp' in ex and 'tc_icon_buy.webp' not in ex)),
          'はじめの 横長の 絵（tc_icon_buy.webp）は、丸い 絵が ある ときは アプリに 入れない（もとの フォルダには 残す：assets_dir.superseded）')
    if HAVE:
        ic = os.path.join(TCA, 'tc_icon_buy2.webp')
        from PIL import Image
        im = Image.open(ic) if os.path.exists(ic) else None
        check(im is not None and im.size[0] == 480 and abs(im.size[1] - 480) <= 2 and im.mode == 'RGBA' and os.path.getsize(ic) < 120000 and im.getpixel((3, 3))[3] == 0 and im.getpixel((240, 200))[3] >= 250,
              f'ボタンの 絵（アプリに 入る もの）：丸い 絵 {im.size if im else None}・すき通し あり（かどは すき通る・まん中は 見える）・{os.path.getsize(ic) if im else 0:,}B')
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'])
        if HAVE:
            ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo', has_touch=True)
            ctx.add_init_script(FAKE)
            pg = ctx.new_page(); errs = []; seen = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.on('response', lambda r: seen.append(r.url.split('/')[-1].split('?')[0]) if r.status == 200 and 'tc_icon_buy' in r.url else None)
            dialogs = []; pg.on('dialog', lambda d: (dialogs.append(d.type), d.dismiss()))
            open_tc(pg, APP)
            print('■ 下の 列の 1番 右の ボタン（お世話トークン購入）')
            set_stock(pg, 5); pg.wait_for_timeout(400)
            geo = pg.evaluate("() => ({ B: TCCare.BTN, Q: TCCare.BUYG, R: TCCare.BTN_R })")
            xs = [geo['B'][k][0] for k in ('pet', 'feed', 'clean', 'call')] + [geo['Q']['x']]
            check(xs == [128, 327, 526, 725, 924] and all(geo['B'][k][1] == 1494 for k in geo['B']) and geo['Q']['y'] == 1494 and 138 <= geo['Q']['d'] <= 146 and geo['R'] == 70 and geo['Q']['name'] == 'トークン購入'
                  and (geo['Q']['x'], geo['Q']['y']) == BUYXY and xs[0] - 70 == 1052 - (xs[4] + 70) == 58,
                  f'場所：下の 列の 1番 右・5つを 同じ 間かく（まん中 {xs}：199 ずつ・左右の はし 58）・同じ 高さ（1494）・絵の 幅 {geo["Q"]["d"]}（ほかの 丸 140 と 同じ 大きさ）')
            ins = [[924 + dx, 1494 + dy] for dx in (-34, 0, 34) for dy in (-34, 0, 34)]; lab = [[x, y] for x in range(842, 1008, 6) for y in (1594, 1600, 1606)]; lab2 = [[x, y] for x in range(680, 772, 6) for y in (1594, 1600, 1606)]
            px = pg.evaluate(OVPX, ins + lab + lab2 + [[924, 1412], [1012, 1494]])
            pin, pl, pl2, out = px[:9], px[9:9 + len(lab)], px[9 + len(lab):9 + len(lab) + len(lab2)], px[-2:]
            col = sum(1 for q in pin if q[3] >= 245 and max(q[:3]) - min(q[:3]) > 40); ink = sum(1 for q in pl if q[3] > 200); ink2 = sum(1 for q in pl2 if q[3] > 200)
            check(all(q[3] >= 245 for q in pin) and col >= 6 and ink >= 30 and ink2 >= 8 and ink > ink2 and all(q[3] < 60 for q in out) and seen.count('tc_icon_buy2.webp') >= 1 and 'tc_icon_buy.webp' not in seen,
                  f'絵：まさちゃんの 丸い 絵（tc_icon_buy2.webp を 読んで いる・丸の 中は 色つき {col}/9）・下に 名前「トークン購入」（字の 点 {ink}：となりの「呼ぶ」は {ink2}）・丸の 外は すき通る')
            shot(pg, 'buy_btn')
            # 押す → 購入の 窓。お世話の 途中（ごはんを えらぶ）は 開かない（札）・お世話の あとの PUSH が 出て いる 間は 列ごと かくれる
            stage_click(pg, *BUYXY); pg.wait_for_timeout(450); c0 = pg.evaluate("() => [TCBuy.isOpen(), TCApp._t.buyShow()]"); sheet(pg, False)
            stage_click(pg, 327, 1494); pg.wait_for_function("() => !!TCCare.S.chooser", timeout=20000); pg.wait_for_timeout(500)
            stage_click(pg, *BUYXY); pg.wait_for_timeout(350)
            c1 = pg.evaluate("() => [TCBuy.isOpen(), TCApp._t.buyShow(), TCCare.S.fx.some(f => f.k === 'tagUI' && f.txt === 'お世話が おわってから 買えるよ'), !!TCCare.S.chooser]")
            pg.evaluate("() => TCApp.test.prize(null)"); stage_click(pg, 270 + 256, 1262)
            pg.wait_for_function("() => !!(TCCare.S.push && TCCare.S.push.hideT == null) && TCCare.S.phase === 'idle'", timeout=120000); pg.wait_for_timeout(700)
            stage_click(pg, 924, 1566); pg.wait_for_timeout(350)
            c2 = pg.evaluate("() => [TCBuy.isOpen(), TCApp._t.buyShow(), TCCare.S.stock, TCCare.S.bulk]"); pp = pg.evaluate(OVPX, [[924, 1600], [128, 1600]])
            shot(pg, 'buy_push')
            check(c0 == [True, False] and c1 == [False, False, True, True] and c2[:2] == [False, False] and c2[3] is False and pp[0][3] == 0 and pp[1][3] == 0,
                  f'押すと 購入の 窓・お世話の 途中（ごはんを えらぶ）は 開かない（札「お世話が おわってから 買えるよ」）・PUSH が 出て いる 間は 列ごと かくれて 押せない {c0} {c1} {c2}')
            q = pg.evaluate("() => { const G = TCCare.PUSHG, st = document.querySelector('#tcOv .tcst').getBoundingClientRect(); return [st.left + G.x / 1052 * st.width, st.top + G.y / 1657 * st.height]; }")
            pg.mouse.click(q[0], q[1]); pg.wait_for_timeout(1500)
            pg.wait_for_function("() => TCApp.test.info().free", timeout=60000); pg.wait_for_timeout(400)
            pb = pg.evaluate(OVPX, [[924, 1494]])
            check(pb[0][3] >= 245 and pg.evaluate("() => TCApp._t.buyShow()"), 'PUSH を 押して おわると 列が もどる（購入の ボタンも）')

            print('■ 購入の 窓')
            set_stock(pg, 5); w0 = pg.evaluate("() => TengelWallet.total()")
            sheet(pg); shot(pg, 'buy_sheet')
            sh = pg.evaluate("""() => { const r = document.querySelector('#tcb'), s = r.querySelector('.bsh').getBoundingClientRect(), st = document.querySelector('#tcOv .tcst').getBoundingClientRect(), y = r.querySelector('.bbd');
              return { open: TCBuy.isOpen(), title: r.querySelector('.bhd b').textContent, role: r.getAttribute('role'), inside: s.left >= st.left && s.right <= st.right + 0.5 && s.top >= st.top && s.bottom <= st.bottom + 0.5,
                scroll: y.scrollHeight - y.clientHeight, wide: y.scrollWidth - y.clientWidth, minH: Math.min(...[...r.querySelectorAll('.bb')].map(e => e.getBoundingClientRect().height)), notes: [...r.querySelectorAll('.bnote')].map(e => e.textContent), guide: !!r.querySelector('[data-b=guide]'),
                font: getComputedStyle(r.querySelector('.bn')).fontFamily.split(',')[0] }; }""")
            rows = pg.evaluate(ROWS); now = pg.evaluate(NOW)
            check(sh['open'] and sh['title'] == 'お世話トークン購入' and sh['role'] == 'dialog' and sh['inside'] and sh['scroll'] <= 0 and sh['wide'] <= 0 and sh['minH'] >= 40 and 'BIZ' in sh['font'],
                  f'窓：「お世話トークン購入」・フィールドの 中に おさまる（スクロール なし・横に はみ出さない）・ボタンの 高さ {sh["minH"]:.0f}px 以上')
            check([r[0] for r in rows] == [x[0] for x in PACKS] and [r[2] for r in rows] == ['100P', '500P', '1,000P', '1,500P', '2,000P', '2,500P'] and [r[1] for r in rows] == ['ok', 'ok', 'ok', 'ok', 'ok', 'full']
                  and rows[5][3] == '25こを こえる' and all(r[3] == '買う' for r in rows[:5]) and w0 >= 2500
                  and pg.evaluate("() => JSON.stringify(TengelPoints.TOKEN_PACKS)") == json.dumps(PACKS, separators=(',', ':')),
                  f'組は 6つ（1こ 100P・5こ 500P・10こ 1,000P・15こ 1,500P・20こ 2,000P・25こ 2,500P：points.js の 表と 同じ）・いま 5こ・{w0:,}P → 20こ までは 買える・25こは「25こを こえる」で 買えない {rows}')
            check(now['stock'] == '5 / 25こ' and now['pts'] == f'{w0:,}P' and now['msg'] == '' and any('持てるのは 25こまで' in t and 'あと 20こ' in t for t in sh['notes']) and any('5分ごとに 5つ' in t for t in sh['notes']) and any('もどせない' in t for t in sh['notes']) and sh['guide'],
                  f'いまの トークン（{now["stock"]}）・使える ポイント（{now["pts"]}）・きまりの 説明（25こまで／5分ごとに 5つ／もどせない）・「説明書を 見る（当たりの 確率）」')
            # 2回 押して 決める
            pg.locator('#tcb [data-b=ask][data-n="5"]').click(); pg.wait_for_timeout(200)
            cf = pg.evaluate("() => { const r = document.querySelector('#tcb .brow.cf'); return r ? [+r.dataset.n, [...r.querySelectorAll('.bb')].map(b => b.textContent), TCApp.state.stock, TengelWallet.total()] : null; }")
            shot(pg, 'buy_confirm')
            pg.locator('#tcb [data-b=no]').click(); pg.wait_for_timeout(200)
            cf2 = pg.evaluate("() => [document.querySelectorAll('#tcb .brow.cf').length, TCApp.state.stock, TengelWallet.total()]")
            check(cf == [5, ['やめる', '500Pで 買う'], 5, w0] and cf2 == [0, 5, w0], f'「買う」→ その 行が「やめる／500Pで 買う」に（まだ 買わない）→「やめる」で もどる（トークンも ポイントも そのまま）{cf}')
            pg.locator('#tcb [data-b=ask][data-n="5"]').click(); pg.wait_for_timeout(150); pg.locator('#tcb [data-b=go]').click(); pg.wait_for_timeout(800)
            a1 = pg.evaluate("() => ({ st: TCApp.state.stock, S: TCCare.S.stock, show: Math.round(TCCare.S.stockShow), tot: TengelWallet.total(), buy: TCApp.state.buy, saved: JSON.parse(localStorage.getItem('tengel.tc')), plus: TCCare.S.fx.filter(f => f.k === 'plus').map(f => f.txt), open: TCBuy.isOpen() })")
            now = pg.evaluate(NOW); led = pg.evaluate(LED); shot(pg, 'buy_done')
            check(a1['st'] == 10 and a1['S'] == 10 and a1['tot'] == w0 - 500 and a1['buy'] is None and a1['saved']['stock'] == 10 and a1['saved'].get('buy') is None and '+5' in a1['plus'] and a1['open'],
                  f'「500Pで 買う」→ トークン 5 → {a1["st"]}・ポイント {w0:,} → {a1["tot"]:,}（−500）・すぐ 保存・右上に「＋5」・窓は 開いた まま')
            check(now['stock'] == '10 / 25こ' and now['pts'] == f'{w0 - 500:,}P' and '5こ 買ったよ' in now['msg'] and '500P' in now['msg'] and not now['ng'] and led == [['unlock', -500, 'tctok:5', 3]],
                  f'窓の 数も かわる（{now["stock"]}・{now["pts"]}）・「{now["msg"]}」・台帳に 1件（unlock-tctok:5:<番号>・−500P）{led}')
            # 台帳の 履歴（設定 › ポイント › 詳しく）の 名前
            hist = pg.evaluate("""() => { const e = TengelWallet.events().find(x => /^unlock-tctok:/.test(x.id)); return { use: e.use, dev: !!e.device, n: e.n > 0 }; }""")
            check(sum(hist['use'].values()) == 500 and hist['dev'] and hist['n'], f'台帳の 1件に 使った ポイントの 内わけ（買った ポイントから 先に）・端末・書いた 順の 番号 {hist["use"]}')

            # 第4.168版：4けたの 値段の 組（1,000P より 上）を「買う」→「やめる／1,500Pで 買う」の 行は、左の 値段の 字を かくす（前は「やめる」の 下に もぐって 切れて 見えた）
            pg.locator('#tcb [data-b=ask][data-n="15"]').click(); pg.wait_for_timeout(250)
            cfg = pg.evaluate("""() => { const r = document.querySelector('#tcb .brow.cf'), R = e => e.getBoundingClientRect(), q = R(r), bn = R(r.querySelector('.bn')), bs = [...r.querySelectorAll('.bb')].map(R);
              return { n: +r.dataset.n, bc: getComputedStyle(r.querySelector('.bc')).display, txt: [...r.querySelectorAll('.bb')].map(b => b.textContent), inside: bs.every(b => b.left >= q.left && b.right <= q.right + 0.5), gap: Math.round(bs[0].left - bn.right), order: bs[0].right <= bs[1].left, right: Math.round(q.right - bs[1].right) }; }""")
            shot(pg, 'buy_confirm_1500'); pg.locator('#tcb [data-b=no]').click(); pg.wait_for_timeout(200)
            check(cfg == {'n': 15, 'bc': 'none', 'txt': ['やめる', '1,500Pで 買う'], 'inside': True, 'gap': cfg['gap'], 'order': True, 'right': cfg['right']} and cfg['gap'] >= 8 and 0 <= cfg['right'] <= 12
                  and pg.evaluate("() => getComputedStyle(document.querySelector('#tcb .brow:not(.cf) .bc')).display") != 'none',
                  f'第4.168版：「買う」を 押した 行は「15こ ［やめる］［1,500Pで 買う］」（左の 値段の 字は かくす＝ボタンと 重ならない：こ数から ボタンまで {cfg["gap"]}px）・ほかの 行の 値段は そのまま')
            print('■ 25こ まで')
            set_stock(pg, 21); pg.wait_for_timeout(700)
            rows = pg.evaluate(ROWS); now = pg.evaluate(NOW)
            check([r[1] for r in rows] == ['ok', 'full', 'full', 'full', 'full', 'full'] and now['stock'] == '21 / 25こ' and 'あと 4こ' in ''.join(pg.evaluate("() => [...document.querySelectorAll('#tcb .bnote')].map(e => e.textContent)")),
                  f'いま 21こ → 買えるのは 1こ だけ（5こ より 上は「25こを こえる」）・窓は 開いた まま 数が かわる（{now["stock"]}）')
            for _ in range(4):
                pg.locator('#tcb [data-b=ask][data-n="1"]').click(); pg.wait_for_timeout(120); pg.locator('#tcb [data-b=go]').click(); pg.wait_for_timeout(500)
            rows = pg.evaluate(ROWS); a2 = pg.evaluate("() => [TCApp.state.stock, TCCare.S.stock, TengelWallet.total()]")
            r_full = pg.evaluate("async () => { const t0 = TengelWallet.total(); const r = await TCApp.buy.buy(1); return [r.ok, r.why, r.room, TCApp.state.stock, TengelWallet.total() - t0, TCApp.state.buy]; }")
            check(a2 == [25, 25, w0 - 500 - 400] and [r[1] for r in rows] == ['full'] * 6 and r_full == [False, 'full', 0, 25, 0, None],
                  f'1こ ずつ 4回 買う → 25こ（−400P）・25この ときは どの 組も 買えない・窓口を よんでも 買えない（ポイントも へらない）{r_full}')
            shot(pg, 'buy_full')
            r_bad = pg.evaluate("async () => { const t0 = TengelWallet.total(), a = []; for (const n of [0, 2, 3, 7, 21, 26, -5, 'x', 1.5]) { const r = await TCApp.buy.buy(n); a.push(r.ok + ':' + r.why); } const w = await TengelWallet.tc.buy('zz-bad-1', 7); return [a, w, TengelWallet.total() - t0]; }")
            check(set(r_bad[0]) == {'false:off'} and r_bad[1] == {'ok': False, 'why': 'bad'} and r_bad[2] == 0, f'表に ない 数（0・2・3・7・21・26…）は 買えない（トレーニングセンターの 窓口も 台帳の 窓口も）{r_bad[0][:3]}')

            print('■ ポイントが 足りない')
            set_stock(pg, 0)
            left = pg.evaluate("""async () => { const P = TengelPoints, W = TengelWallet; const t = W.total(); if (t > 550) { const id = 'unlock-test-drain-' + Date.now(); await W.unlock('test-drain-' + Date.now(), t - 550); } return W.total(); }""")
            pg.wait_for_timeout(900); rows = pg.evaluate(ROWS); now = pg.evaluate(NOW)
            check(left == 550 and [r[1] for r in rows] == ['ok', 'ok', 'short', 'short', 'short', 'short'] and rows[2][3] == 'ポイントが 足りない' and now['pts'] == '550P',
                  f'ポイント 550P・トークン 0こ → 1こ・5こは 買える・10こ より 上は「ポイントが 足りない」{[r[1] for r in rows]}')
            r_short = pg.evaluate("async () => { const r = await TCApp.buy.buy(10); return [r.ok, r.why, r.need, TCApp.state.stock, TengelWallet.total(), TCApp.state.buy]; }")
            check(r_short == [False, 'short', 450, 0, 550, None], f'窓口を よんでも 買えない（あと 450P・トークンも ポイントも そのまま・買い物の しるしも のこらない）{r_short}')
            shot(pg, 'buy_short')
            pg.locator('#tcb [data-b=ask][data-n="5"]').click(); pg.wait_for_timeout(120); pg.locator('#tcb [data-b=go]').click(); pg.wait_for_timeout(600)
            rows = pg.evaluate(ROWS); a3 = pg.evaluate("() => [TCApp.state.stock, TengelWallet.total()]")
            check(a3 == [5, 50] and [r[1] for r in rows] == ['short'] * 5 + ['full'], f'5こ 買う → 5こ・のこり 50P → もう どれも 買えない（1〜20こは ポイントが 足りない・25こは 25こを こえる）{a3}')
            # あずかりポイント（上限を こえて 届いた ぶん）は 先に 補充して 使う：台帳の 窓口が ensure を よぶ（ここでは 名前 だけ 見る）
            check('ensure(pk[1])' in open(os.path.join(W, 'points_ui.js'), encoding='utf8').read(), '台帳の 窓口：足りない ときは あずかりポイントから 先に 補充して から 買う（ensure）')

            print('■ とちゅうで 閉じても ずれない')
            pg.evaluate("""async () => { const W = TengelWallet; const e = TengelPoints.giftEvent(Date.now(), 5000, 'gift-test-buy-' + Date.now(), 'テスト'); const s = W.snapshot(); s.events.push(e); await W.restore(s).catch(() => {}); }""")
            pg.wait_for_timeout(600)
            tot = pg.evaluate("() => TengelWallet.total()")
            if tot < 2600:      # restore は 台帳が 空の とき だけ 入る → 入らなければ テスト版の ポイントを 足す ボタンと 同じ 形で
                pg.evaluate("() => { document.querySelector('.tabbar button[data-tab=set]').click(); }"); pg.wait_for_timeout(500)
                pg.evaluate("() => { const b = document.querySelector('#setTest [data-test=pts]'); if (b) b.click(); }"); pg.wait_for_timeout(900)
                tot = pg.evaluate("() => TengelWallet.total()")
            check(tot >= 2600, f'（じゅんび）テスト用に ポイントを 足した（{tot:,}P）')
            # 同じ 番号の 買い物は 1回 だけ
            r_dup = pg.evaluate("async () => { const W = TengelWallet, t0 = W.total(); const a = await W.tc.buy('b-dup-test-1', 5), t1 = W.total(), b = await W.tc.buy('b-dup-test-1', 5), t2 = W.total(); return [a.ok, !!a.dup, t0 - t1, b.ok, !!b.dup, t1 - t2, W.tc.paid('b-dup-test-1'), W.tc.paid('b-dup-test-2'), W.tc.paid('')]; }")
            check(r_dup == [True, False, 500, True, True, 0, True, False, False], f'台帳：同じ 番号の 買い物は 1回 だけ（2回目は 何も へらない）・その 買い物が 入って いるかを 見られる {r_dup}')
            # 台帳に 入った あと・トークンを わたす 前に 閉じた → 次に 開いた とき わたす
            set_stock(pg, 3)
            r_rec = pg.evaluate("""async () => { const st = TCApp.state, t0 = TengelWallet.total(); st.buy = { id: 'b-dup-test-1', n: 5 }; localStorage.setItem('tengel.tc', JSON.stringify(st));
              await TCApp._t.recoverBuy(); await new Promise(r => setTimeout(r, 500));
              return [st.stock, TCCare.S.stock, st.buy, JSON.parse(localStorage.getItem('tengel.tc')).buy || null, TengelWallet.total() - t0, document.querySelector('#tcOv .tcmsg').textContent]; }""")
            check(r_rec[:5] == [8, 8, None, None, 0] and '前に 買った' in r_rec[5] and '5こ' in r_rec[5], f'台帳に 入った あと 閉じた 買い物（しるしが のこって いる）→ 開いた ときに トークンを わたす（3 → {r_rec[0]}・ポイントは もう へらない）「{r_rec[5]!r}」')
            r_rec2 = pg.evaluate("""async () => { const st = TCApp.state, t0 = TengelWallet.total(); st.buy = { id: 'b-never-paid-9', n: 25 }; localStorage.setItem('tengel.tc', JSON.stringify(st));
              await TCApp._t.recoverBuy(); await new Promise(r => setTimeout(r, 300)); const a = [st.stock, st.buy, JSON.parse(localStorage.getItem('tengel.tc')).buy || null, TengelWallet.total() - t0];
              st.buy = { id: '', n: 5 }; await TCApp._t.recoverBuy(); st.buy = { id: 'b-dup-test-1', n: 0 }; await TCApp._t.recoverBuy(); return a.concat([st.buy, st.stock]); }""")
            check(r_rec2 == [8, None, None, 0, None, 8], f'台帳に 入って いない 買い物の しるし → しるし だけ 消す（トークンは ふえない・ポイントも そのまま）・こわれた しるしも 消す {r_rec2}')
            # 買う 前に、たまって いる ぶんを 先に 入れる → その あとで 25こを こえるかを 見る
            r_acc = pg.evaluate("""async () => { const st = TCApp.state, S = TCCare.S, now = Math.max(Date.now(), +st.seen || 0), out = [];
              st.stock = 15; S.stock = S.stockShow = 15; st.stockAt = now - 5 * 60000 - 800; let r = await TCApp.buy.buy(5); out.push([r.ok, r.why || '', st.stock]);       // 15 → たまって 20 → 買って 25
              st.stock = 20; S.stock = S.stockShow = 20; st.stockAt = now - 5 * 60000 - 800; r = await TCApp.buy.buy(5); out.push([r.ok, r.why || '', st.stock]);            // 20 → たまって 25 → 買えない（こえる）
              S.stock = 18; st.stock = 19; st.stockAt = now + 7200000; r = await TCApp.buy.buy(5); out.push([r.ok, r.why || '', st.stock, S.stock]);                          // お世話で 使った ぶん（S が 少ない）を 先に 写す：18 → 23
              st.stockAt = now + 7200000; return out; }""")
            check(r_acc == [[True, '', 25], [False, 'full', 25], [True, '', 23, 23]], f'買う 前に たまって いる ぶん（5分ごとの ＋5）を 入れて から 数える（15 → 20 → 買って 25／20 → 25 → 買えない）・お世話で 使った ぶんも 先に 写す {r_acc}')
            # 2つ いっしょに 買おうと しても 1つずつ
            set_stock(pg, 0)
            r_two = pg.evaluate("async () => { const t0 = TengelWallet.total(); const [a, b] = await Promise.all([TCApp.buy.buy(5), TCApp.buy.buy(5)]); return [a.ok, b.ok, b.why, TCApp.state.stock, t0 - TengelWallet.total()]; }")
            check(r_two == [True, False, 'busy', 5, 500], f'買って いる 途中に もう 1回 → 待たせる（2重に 買わない）{r_two}')

            print('■ 窓を 開いて いる 間・説明書')
            sheet(pg, False); pg.wait_for_function("() => TCApp.test.info().free", timeout=60000)
            sheet(pg); pg.evaluate("() => { TCApp._t.force(null); TCApp.state.rs = { n: 5, at: Date.now() - 6 * 60000, el: 0 }; }"); pg.wait_for_timeout(1200)
            h1 = pg.evaluate("() => [TCApp.state.rs.n, TCApp.state.rs.at > 0]"); sheet(pg, False); pg.wait_for_timeout(1500)
            h2 = pg.evaluate("() => [TCApp.state.rs.n, TCApp.state.rs.at > 0]")
            check(h1 == [5, True] and h2 == [0, False], f'購入の 窓を ひらいて いる 間は 馬の リセットを 待つ → とじると リセット（説明書・作戦会議と 同じ）（{h1} → {h2}）')
            pg.wait_for_function("() => TCApp.test.info().free", timeout=60000)
            # 指で 押した とき（タッチ）：開いた 指の クリックで すぐ 閉じない
            #   ボタンは フィールドの 絵（指を はなした ときに 開く）→ その 指の クリックが、開いた ばかりの 窓の 中（ちょうど 下に「説明書を 見る」・組の「買う」）に とどいても 何も おきない
            r = stage_xy(pg, *BUYXY); under = pg.evaluate("([x, y]) => { TCBuy.open(document.querySelector('#tcOv .tcst'), TCApp.buy); const e = document.elementFromPoint(x, y); const r = e ? [e.tagName, e.className, e.dataset.b || ''] : null; TCBuy.close(); return r; }", list(r))
            pg.touchscreen.tap(r[0], r[1]); pg.wait_for_timeout(120); o1 = pg.evaluate("() => [TCBuy.isOpen(), TCGuide.isOpen(), document.querySelectorAll('#tcb .brow.cf').length]"); pg.wait_for_timeout(700); o2 = pg.evaluate("() => [TCBuy.isOpen(), TCGuide.isOpen(), document.querySelectorAll('#tcb .brow.cf').length]")
            g0 = pg.evaluate("() => { TCBuy.open(document.querySelector('#tcOv .tcst'), TCApp.buy); document.querySelector('#tcb [data-b=guide]').click(); document.querySelector('#tcb [data-b=ask]').click(); return [TCBuy.isOpen(), TCGuide.isOpen(), document.querySelectorAll('#tcb .brow.cf').length]; }")      # 開いた 瞬間の クリック（説明書・買う）→ 受けつけない
            pg.touchscreen.tap(*stage_xy(pg, 14, 800)); pg.wait_for_timeout(300); pg.wait_for_timeout(200); pg.touchscreen.tap(*stage_xy(pg, 14, 800)); pg.wait_for_timeout(300); o3 = pg.evaluate("() => TCBuy.isOpen()")      # 第4.168版：組が 6つに なって 窓が 高く なった（上下の 暗い 所は 10px ほど）→ 左の 暗い 所を 押す
            check(o1 == [True, False, 0] and o2 == [True, False, 0] and g0 == [True, False, 0] and not o3 and under is not None,
                  f'指で 押して 開く → 開いた まま（すぐ 閉じない・下に 出た「{under and under[2] or under and under[1]}」も 押されない）→ 外がわ（暗い 所）を 押すと とじる（{o1} {o2} {g0} {o3}）')
            sheet(pg); pg.locator('#tcb [data-b=guide]').click(); pg.wait_for_timeout(900)
            gd = pg.evaluate("""() => { const e = document.querySelector('#tcg'), secs = [...e.querySelectorAll('.sec')].map(x => [x.querySelector('h3').textContent, x.textContent]), f = k => (secs.find(x => x[0].includes(k)) || [0, ''])[1];
              return { buy: TCBuy.isOpen(), guide: TCGuide.isOpen(), sec: f('お世話トークンの購入'), rows: [...e.querySelectorAll('table[data-tab=packs] tr')].map(r => [+r.dataset.n, r.cells[0].textContent, r.cells[1].textContent]), tok: f('お世話トークン') }; }""")
            check(not gd['buy'] and gd['guide'] and gd['rows'] == [[1, '1こ', '100P'], [5, '5こ', '500P'], [10, '10こ', '1,000P'], [15, '15こ', '1,500P'], [20, '20こ', '2,000P'], [25, '25こ', '2,500P']]
                  and all(x in gd['sec'] for x in ['下の列の1番右の「お世話トークン購入」', '最大25こ', '2回押すと決まり', 'ポイントにもどせない', 'ポイント特化ゾーン']) and '5分ごとに5つ' in gd['tok'],
                  f'「説明書を 見る（当たりの 確率）」→ 窓が とじて 説明書が ひらく・説明書に「お世話トークンの購入」の 項目（組の 表 6行・25こまで・2回 押す・もどせない）{gd["rows"]}')
            pg.evaluate("() => TCGuide.close()"); pg.wait_for_timeout(400)
            # トレーニングセンターを 閉じると 窓も とじる
            sheet(pg); pg.locator('#tcOv [data-tc="back"]').click(); pg.wait_for_timeout(500)
            check(pg.evaluate("() => [TCBuy.isOpen(), document.querySelector('#tcOv').classList.contains('on')]") == [False, False], '「← もどる」で トレーニングセンターを 閉じると 購入の 窓も とじる')
            # 設定 › ポイント › 詳しく：履歴に 名前が 出る
            pg.evaluate("() => { document.querySelector('.tabbar button[data-tab=set]').click(); }"); pg.wait_for_timeout(600)
            pg.evaluate("() => { const b = document.querySelector('#setPoints [data-pt=show][data-v=hist]'); if (b) b.click(); }"); pg.wait_for_timeout(500)
            hs = pg.evaluate("() => [...document.querySelectorAll('#setPoints .pthist li')].map(li => li.textContent).filter(t => t.includes('お世話トークン')).slice(0, 3)")
            check(len(hs) >= 1 and all('トレーニングセンターの お世話トークン' in t and 'こを購入' in t and '解放：' not in t for t in hs) and any('-500P' in t or '−500P' in t for t in hs),
                  f'設定の ポイントの 履歴に「トレーニングセンターの お世話トークン ○こを購入　−○P」（「解放：」は つかない）{hs[:2]}')
            check(not errs and not dialogs, f'エラー なし・confirm()／alert() の 窓は 出て いない {errs[:3]} {dialogs[:3]}')
            ctx.close()

            print('■ App Store版にも ある')
            c2 = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo'); c2.add_init_script(FAKE)
            p2 = c2.new_page(); e2 = []; p2.on('pageerror', lambda e: e2.append(str(e)))
            open_tc(p2, STORE); set_stock(p2, 3); p2.wait_for_timeout(400)
            t0 = p2.evaluate("() => TengelWallet.total()")
            stage_click(p2, *BUYXY); p2.wait_for_timeout(450)
            p2.locator('#tcb [data-b=ask][data-n="10"]').click(); p2.wait_for_timeout(150); p2.locator('#tcb [data-b=go]').click(); p2.wait_for_timeout(800)
            q = p2.evaluate("() => [TCApp.state.stock, TengelWallet.total(), typeof window.TCTest, document.querySelectorAll('#tcOv [data-tc=test]').length]")
            check(q == [13, t0 - 1000, 'undefined', 0] and t0 == 1500, f'App Store版（はじめの 1,500P）：下の 列の ボタン → 10こ 買う → 3 → {q[0]}こ・{t0:,} → {q[1]:,}P（道具箱は ない）')
            check(not e2, f'エラー なし {e2[:3]}')
            c2.close()
        # ---------- 絵が ない とき（CI）：緑の 紙の 丸に ＋ ----------
        print('■ 絵が ない とき（CI）')
        c3 = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo'); c3.add_init_script(FAKE)
        c3.route('**/tc_icon_buy2.webp', lambda route: route.fulfill(status=404, body='not found'))
        p3 = c3.new_page()
        if HAVE:
            open_tc(p3, STORE); p3.wait_for_timeout(600)
            fb = p3.evaluate(OVPX, [[924 - 40, 1494 - 30], [924 + 40, 1494 + 30], [924, 1494 - 62]]); lb = p3.evaluate(OVPX, [[x, y] for x in range(842, 1008, 6) for y in (1594, 1600, 1606)])
            stage_click(p3, *BUYXY); p3.wait_for_timeout(450)
            grn = all(q[3] == 255 and q[1] > q[0] and q[1] > q[2] for q in fb[:2])
            check(grn and fb[2][3] == 255 and sum(1 for q in lb if q[3] > 200) >= 30 and p3.evaluate("() => TCBuy.isOpen()"), f'ボタンの 絵が 読めない → 緑の 紙の 丸に ＋（下に 名前「トークン購入」・押すと 窓が ひらく）{fb}')
        else:
            check("label('＋', 0, 2, 76" in sb and "name: 'トークン購入'" in sb and 'buyIm.naturalWidth' in sb, 'ボタンの 絵が 読めない ときは 緑の 紙の 丸に ＋ を 描く 形（CI は 絵が ない ので 画面は ためさない）')
        c3.close()
        b.close()
finally:
    srv.terminate()
print('NG' if fails else 'OK', len(fails), fails)
sys.exit(1 if fails else 0)
