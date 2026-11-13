# ログインボーナス（第4.168版）の テスト
#   まさちゃん 2026/11/14 01:26「7.毎日ログインボーナスを作る！１週間単位 ・１日目、200P ・２日目、300P ・３日目、400P ・４日目、500P ・５日目、600P ・６日目、1000P ・７日目、1300P」
#   ・その 日に はじめて アプリを 開いた とき 1回 だけ（開いた ときの 画面〈#gate〉が 消えて から）→ 獲得ポイントに 入る・まん中に 小さな 窓（7日ぶんの 札）
#   ・7日で ひとまわり（200・300・400・500・600・1,000・1,300P → また 1日目）・開かない 日が あっても つづきから
#   ・同じ 日は 2回 もらえない（開き直しても・端末の 時計を もどしても・おぼえを 消しても＝財布の 台帳から 作り直す）
#   ・開いた まま 日付が かわった ときも もらえる（もどって きた とき）
#   ・字は いまの 壁紙の 字（しぼった 字に 入って いる 字 だけ）・窓は confirm()／alert() を 使わない
#   ・App Store版：テスト版の ボタン（つぎの 日を ためす）は 出ない・日付を ずらす しかけは 効かない／Web版には 入れない
#   python3 test_login.py
import json, os, re, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv_tc'); PORT = 8806; APP = f'http://localhost:{PORT}/APP/'; STORE = f'http://localhost:{PORT}/STORE/'; WEB = f'http://localhost:{PORT}/TENGEL/'
SHOT = os.environ.get('SHOT')          # 画面を 写す フォルダ（見る 用）
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'TENGEL')], check=True, stdout=subprocess.DEVNULL, env={k: v for k, v in os.environ.items() if k not in ('TENGEL_TEST', 'TARGET')})
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, TARGET='app', TENGEL_TEST='1'))
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'STORE')], check=True, stdout=subprocess.DEVNULL, env=dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, TARGET='app'))
for d in ('APP', 'STORE'):
    pth = os.path.join(SRV, d, 'index.html'); html = open(pth, encoding='utf8').read()
    assert "window.__NATIVE = location.protocol === 'tengel:';" in html
    open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c: fails.append(label)


FAKE = open(os.path.join(W, 'test_tc.py'), encoding='utf8').read().split('FAKE = """')[1].split('"""')[0]      # アプリの 窓口の にせもの（test_tc.py と 同じ）
# 端末の 時計を 日に ちで ずらす（window.__dayOff）。ログインボーナスは Date.now() から 日付を 作る
CLOCK = "(() => { const R = Date.now.bind(Date); window.__realNow = R; window.__dayOff = 0; Date.now = () => R() + window.__dayOff * 86400000; })();"
AUTO = 'window.__LOGIN_AUTO = true;'      # テストの ブラウザ（navigator.webdriver）でも、アプリと 同じ ように 自分から 出す
BONUS = [200, 300, 400, 500, 600, 1000, 1300]
INFO = """() => { const o = document.getElementById('lgOv'), s = window.TengelLogin ? TengelLogin.state() : null, d = new Date(Date.now()), p2 = n => (n < 10 ? '0' : '') + n;
  return { open: !!o, title: o ? o.querySelector('.lgh').textContent : null, line: o ? o.querySelector('.lgs').textContent : null, tiles: o ? [...o.querySelectorAll('.lgd li')].map(e => (e.className || '-') + ':' + e.textContent) : null,
    ck: o ? o.querySelectorAll('.lgd .ck').length : 0, n: s && s.n, last: s && s.last, off: s && s.off, total: TengelWallet.total(), today: d.getFullYear() + '-' + p2(d.getMonth() + 1) + '-' + p2(d.getDate()),
    ev: TengelWallet.events().filter(e => /^login-/.test(e.id)).map(e => [e.id, e.amount, e.what, e.kind]), shown: window.TengelLogin ? TengelLogin.shown() : null }; }"""


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


def shot(pg, name):
    if SHOT: os.makedirs(SHOT, exist_ok=True); pg.screenshot(path=os.path.join(SHOT, name + '.png'))


def tiles_ok(tl, day):          # 7つの 札：day より 前＝もらった（got）・day＝今日（now）・あとは 何も なし
    want = [('got' if i < day else 'now' if i == day else '-') + f':{i + 1}日目{BONUS[i]:,}P' for i in range(7)]
    return tl == want


try:
    print('■ 中身（ビルド）')
    src = open(os.path.join(W, 'login_bonus.js'), encoding='utf8').read(); code = re.sub(r'//[^\n]*', '', src)
    app = open(os.path.join(SRV, 'APP', 'index.html'), encoding='utf8').read(); store = open(os.path.join(SRV, 'STORE', 'index.html'), encoding='utf8').read(); web = open(os.path.join(SRV, 'TENGEL', 'index.html'), encoding='utf8').read()
    check(all('window.TengelLogin = {' in x and "'tengel.login'" in x and 'BONUS = [200, 300, 400, 500, 600, 1000, 1300]' in x for x in (app, store)) and sum(BONUS) == 4300,
          'App Store版・テスト版の index.html に ログインボーナス（login_bonus.js）が 入って いる・表は 200・300・400・500・600・1,000・1,300P（1週間で 4,300P）')
    check('TengelLogin' not in web and 'ログインボーナス' not in web and 'tengel.login' not in web, 'Web版には 入って いない（かわらない）')
    check('confirm(' not in code and 'alert(' not in code and 'prompt(' not in code, '窓は confirm()・alert() を 使わない（アプリの 中では 出ない）')
    body = set(open(os.path.join(W, 'ios', 'fonts', 'ks', 'chars_body.txt'), encoding='utf8').read()); disp = set(open(os.path.join(W, 'ios', 'fonts', 'ks', 'chars_disp.txt'), encoding='utf8').read())
    strs = ''.join(re.findall(r"'((?:[^'\\]|\\.)*)'", code)); lack = sorted({c for c in strs if ord(c) > 0x2000 and c not in body}); lackd = [c for c in 'ログインボーナス' if c not in disp]
    sys.path.insert(0, os.path.join(W, 'kisekae')); import build_fonts as _bf
    check(not lack and not lackd and 'login_bonus.js' in open(os.path.join(W, 'kisekae', 'build_fonts.py'), encoding='utf8').read() and not (set(_bf.body_chars()) - body),
          f'画面の 言葉は しぼった 字（本文 {len(body)}字・見出し {len(disp)}字）に 入って いる 字 だけ（足りない 字 {lack}{lackd}）・字を しぼる 道具（kisekae/build_fonts.py）も login_bonus.js を 見る')
    man = re.sub(r'<[^>]+>', '', open(os.path.join(W, 'manual', 'content_app.html'), encoding='utf8').read())      # タグを とった 文
    check('ログインボーナス' in man and all(f'{i + 1}日目 {BONUS[i]:,}P' in man for i in range(7)) and '7日でひとまわり' in man.replace(' ', ''),
          '説明書（ポイントの もらい方）に ログインボーナスの 行（1日目 200P 〜 7日目 1,300P・7日で ひとまわり）')
    pu = open(os.path.join(W, 'points_ui.js'), encoding='utf8').read()
    check("/^(rel-)?back-theme:|^login-/.test(String(e.id)) ? '' : 'ミッション：'" in pu, 'ポイントの 履歴：ログインボーナスには「ミッション：」を つけない')

    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'])
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo', has_touch=True, is_mobile=True)
        ctx.add_init_script(FAKE); ctx.add_init_script(CLOCK + AUTO)
        pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        dialogs = []; pg.on('dialog', lambda d: (dialogs.append(d.type), d.dismiss()))
        print('■ はじめて 開いた とき（テスト版）')
        pg.goto(APP); pg.wait_for_timeout(1500)
        pg.wait_for_function("() => window.TengelWallet && TengelWallet.on && TengelWallet.total() >= 10000", timeout=20000); pg.wait_for_timeout(1100)      # テスト版は はじめから 10,000P（それが 入って から 数える）
        g0 = pg.evaluate(INFO); gon = pg.evaluate("() => document.documentElement.classList.contains('gateon')")
        check(gon and not g0['open'] and g0['ev'] == [] and g0['n'] == 0 and g0['last'] == '', f'開いた ときの 画面（スタートの 画面）が 出て いる 間は まだ もらわない・窓も 出ない（{g0["ev"]}）')
        t0 = g0['total']; gate(pg)
        pg.wait_for_function("() => !!document.getElementById('lgOv')", timeout=20000); pg.wait_for_timeout(700); a = pg.evaluate(INFO); shot(pg, 'login_day1')
        check(a['open'] and a['title'] == 'ログインボーナス' and a['line'] == '1日目 の ボーナス+200Pを もらったよ' and tiles_ok(a['tiles'], 0) and a['ck'] == 1 and a['shown'] == 0,
              f'スタートの 画面が 消えると 窓「ログインボーナス」：「{a["line"]}」・7日ぶんの 札（今日＝1日目に しるし）{a["tiles"]}')
        check(a['ev'] == [[f'login-{a["today"]}', 200, 'ログインボーナス（1日目）', 'mission']] and a['total'] == t0 + 200 and a['n'] == 1 and a['last'] == a['today'],
              f'獲得ポイントに 200P 入る（{t0:,} → {a["total"]:,}P）・台帳に 1件（login-<今日>）・おぼえ（1回・今日）{a["ev"]}')
        lay = pg.evaluate("""() => { const o = document.getElementById('lgOv'), c = o.querySelector('.lgc').getBoundingClientRect(), bt = o.querySelector('.lgb').getBoundingClientRect(), cs = getComputedStyle(o), t = document.elementFromPoint(c.left + c.width / 2, c.top + 20);
          const li = [...o.querySelectorAll('.lgd li')], lr = li.map(e => e.getBoundingClientRect()), fam = e => getComputedStyle(e).fontFamily.split(',')[0].trim().replace(/"/g, ''), tb = document.elementFromPoint(8, innerHeight - 8);
          return { z: +cs.zIndex, pos: cs.position, inside: c.left >= 0 && c.right <= innerWidth && c.top >= 0 && c.bottom <= innerHeight, top: !!t && o.contains(t), bh: bt.height, role: o.getAttribute('role'), modal: o.getAttribute('aria-modal'), label: o.getAttribute('aria-label'),
            font: fam(o.querySelector('.lgc')), hfont: fam(o.querySelector('.lgh')), bodyFont: fam(document.querySelector('.card') || document.body), rows: new Set(lr.map(r => Math.round(r.top))).size, wide7: lr[6].width > lr[5].width * 1.6,
            over: li.some(e => [...e.querySelectorAll('.d, .p')].some(c => { const g = document.createRange(); g.selectNodeContents(c); const t = g.getBoundingClientRect(), q = e.getBoundingClientRect(); return t.right > q.right - 1 || t.left < q.left + 1; })),      // 札の 字（○日目・○P）が 札の 中に おさまる（かどの しるしは 札の 外へ 少し 出る 形）
             test: !!o.querySelector('[data-lg=next]'), tabz: +getComputedStyle(document.querySelector('.tabbar')).zIndex, cover: !!tb && o.contains(tb), w: c.width, h: c.height }; }""")
        check(lay['pos'] == 'fixed' and lay['z'] == 60 and lay['z'] > lay['tabz'] and lay['inside'] and lay['top'] and lay['cover'] and lay['bh'] >= 40 and lay['role'] == 'dialog' and lay['modal'] == 'true' and lay['label'] == 'ログインボーナス'
              and lay['rows'] == 2 and lay['wide7'] and not lay['over'],
              f'窓：画面の まん中（{lay["w"]:.0f}×{lay["h"]:.0f}・画面の 中に おさまる）・下の タブより 上（うしろは 押せない）・札は 4つ＋3つの 2段（7日目は 広い）・字は はみ出さない・「OK」の 高さ {lay["bh"]:.0f}px {"" if lay["cover"] and lay["top"] and not lay["over"] and lay["rows"] == 2 and lay["wide7"] else lay}')
        check(lay['font'] == lay['bodyFont'] == 'BIZ UDPGothic' and lay['hfont'] == 'Dela Gothic One' and lay['test'], f'字は いまの 壁紙の 字（本文 {lay["font"]}・見出し {lay["hfont"]}）・テスト版 だけ「つぎの 日を ためす」が ある')
        pg.locator('#lgOv [data-lg=ok]').click(); pg.wait_for_timeout(300)
        c1 = pg.evaluate(INFO); r1 = pg.evaluate("() => TengelLogin.check()"); pg.wait_for_timeout(400); c2 = pg.evaluate(INFO)
        check(not c1['open'] and c1['shown'] is None and r1 == -1 and not c2['open'] and len(c2['ev']) == 1 and c2['total'] == a['total'], f'「OK」で とじる・同じ 日に もう 1回 確かめても もらえない（{r1}・{c2["total"]:,}P の まま）')

        print('■ 開き直し・時計を もどす・おぼえを 消す')
        pg.goto(APP); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(2800); d1 = pg.evaluate(INFO)
        check(not d1['open'] and len(d1['ev']) == 1 and d1['total'] == a['total'] and d1['n'] == 1, f'同じ 日に 開き直しても 窓は 出ない・もらえない（{d1["total"]:,}P の まま）')
        pg.evaluate("() => { window.__dayOff = -3; }"); r2 = pg.evaluate("() => TengelLogin.check()"); pg.wait_for_timeout(300); d2 = pg.evaluate(INFO)
        check(r2 == -1 and len(d2['ev']) == 1 and d2['total'] == a['total'] and d2['today'] < a['today'] and d2['last'] == a['today'], f'端末の 時計を 3日 もどしても もらえない（さいごに もらった 日より あとの 日 だけ：{d2["today"]} < {d2["last"]}）')
        pg.evaluate("() => { window.__dayOff = 0; localStorage.removeItem('tengel.login'); }"); d3s = pg.evaluate("() => TengelLogin.state()"); r3 = pg.evaluate("() => TengelLogin.check()"); pg.wait_for_timeout(300); d3 = pg.evaluate(INFO)
        check(d3s['n'] == 1 and d3s['last'] == a['today'] and r3 == -1 and len(d3['ev']) == 1 and d3['total'] == a['total'], f'おぼえ（localStorage）が 消えても、財布の 台帳から 作り直す（{d3s["n"]}回・{d3s["last"]}）→ 同じ 日に 2回 もらえない')

        print('■ 7日で ひとまわり')
        seq = []; tot = a['total']
        for k in range(1, 9):               # 2日目 … 7日目 → 1日目 → 2日目
            pg.evaluate("(k) => { window.__dayOff = k; }", k); r = pg.evaluate("() => TengelLogin.check()")
            pg.wait_for_function("() => !!document.getElementById('lgOv')", timeout=10000); pg.wait_for_timeout(250); q = pg.evaluate(INFO); tot += BONUS[k % 7]
            seq.append((r, q['line'], tiles_ok(q['tiles'], k % 7), q['ck'] == k % 7 + 1, q['total'] == tot, q['n'] == k + 1, q['last'] == q['today'], q['ev'][-1][:3] == [f'login-{q["today"]}', BONUS[k % 7], f'ログインボーナス（{k % 7 + 1}日目）']))
            if k in (3, 6): shot(pg, f'login_day{k + 1}')
            pg.evaluate("() => TengelLogin.close()")
        check([x[0] for x in seq] == [1, 2, 3, 4, 5, 6, 0, 1] and [x[1] for x in seq] == [f'{d + 1}日目 の ボーナス+{BONUS[d]:,}Pを もらったよ' for d in (1, 2, 3, 4, 5, 6, 0, 1)] and all(all(x[2:]) for x in seq),
              f'日付が かわる たびに 1回：2日目 300P → … → 7日目 1,300P → また 1日目 200P → 2日目 300P（札の しるし・ポイント・台帳の 名前も 合って いる）{[x[0] + 1 for x in seq]}')
        e9 = pg.evaluate(INFO)
        check(len(e9['ev']) == 9 and len({x[0] for x in e9['ev']}) == 9 and sum(x[1] for x in e9['ev']) == 4300 + 200 + 300 and e9['total'] == t0 + 4800, f'9日ぶん：台帳に 9件（日付は ぜんぶ ちがう）・合わせて {sum(x[1] for x in e9["ev"]):,}P（1週間 4,300P＋200＋300）')
        pg.evaluate("() => { window.__dayOff = 20; }"); r5 = pg.evaluate("() => TengelLogin.check()"); pg.wait_for_function("() => !!document.getElementById('lgOv')", timeout=10000); pg.wait_for_timeout(250); f1 = pg.evaluate(INFO)
        check(r5 == 2 and f1['line'] == '3日目 の ボーナス+400Pを もらったよ' and f1['n'] == 10, f'開かない 日が あっても（11日 あいた）つづきから：「{f1["line"]}」（1日目に もどさない）')
        # 外（暗い 所）を 押すと とじる・窓の 中を 押しても とじない
        cc = pg.evaluate("() => { const c = document.querySelector('#lgOv .lgc').getBoundingClientRect(); return [c.left + c.width / 2, c.top + 30]; }")
        pg.touchscreen.tap(*cc); pg.wait_for_timeout(250); k1 = pg.evaluate("() => !!document.getElementById('lgOv')")
        pg.touchscreen.tap(12, 60); pg.wait_for_timeout(300); k2 = pg.evaluate("() => !!document.getElementById('lgOv')")
        check(k1 and not k2, '窓の 中を 押しても とじない・外（暗い 所）を 押すと とじる')

        print('■ 開いた まま 日付が かわった とき・テスト版の ボタン')
        pg.evaluate("() => { window.__dayOff = 21; document.dispatchEvent(new Event('visibilitychange')); }")
        pg.wait_for_function("() => !!document.getElementById('lgOv')", timeout=10000); pg.wait_for_timeout(250); v1 = pg.evaluate(INFO)
        check(v1['line'] == '4日目 の ボーナス+500Pを もらったよ' and v1['n'] == 11 and v1['last'] == v1['today'], f'アプリに もどって きた とき（日付が かわって いた）にも もらえる：「{v1["line"]}」')
        pg.locator('#lgOv [data-lg=next]').click(); pg.wait_for_timeout(900); v2 = pg.evaluate(INFO)
        check(v2['open'] and v2['line'] == '5日目 の ボーナス+600Pを もらったよ' and v2['n'] == 12 and v2['off'] == 1 and v2['last'] > v1['last'] and len(v2['ev']) == 12,
              f'テスト版の「つぎの 日を ためす」→ 日付を 1日 先に 進めた ことに して つぎの ボーナス：「{v2["line"]}」（ずらした 日数 {v2["off"]}）')
        pg.evaluate("() => TengelLogin.close()")
        # 壁紙を かえると 窓の 字も かわる（ポイントで 解放した 壁紙で：持って いない 壁紙は 財布が かわった ときに 標準へ もどる）
        if pg.evaluate("() => !!(window.TengelKisekae && TengelKisekae.on)"):
            FAM = """() => { const fam = e => getComputedStyle(e).fontFamily.split(',')[0].trim().replace(/"/g, ''), pr = document.createElement('span'); pr.style.fontFamily = 'var(--font-display)'; document.body.appendChild(pr);
              const r = { body: fam(document.querySelector('.card') || document.body), disp: fam(pr), cur: TengelKisekae.current() }; pr.remove(); return r; }"""
            f0 = pg.evaluate(FAM)
            th = pg.evaluate("""async () => { const ts = TengelKisekae.list().filter(t => t.id !== 'default' && t.price).sort((a, b) => a.price - b.price), fam = e => getComputedStyle(e).fontFamily.split(',')[0].trim().replace(/"/g, '');
              for (const t of ts.slice(0, 6)) { if (!(TengelKisekae.usable(t.id) || await TengelWallet.unlock('theme:' + t.id, t.price))) continue; await TengelKisekae.apply(t.id, false); await new Promise(r => setTimeout(r, 500));
                if (fam(document.querySelector('.card') || document.body) !== 'BIZ UDPGothic') return t.id; } return null; }""")
            pg.wait_for_timeout(900); f1 = pg.evaluate(FAM)
            pg.evaluate("() => { TengelLogin.next(); }"); pg.wait_for_function("() => !!document.getElementById('lgOv')", timeout=10000); pg.wait_for_timeout(500)
            kf = pg.evaluate("""() => { const o = document.getElementById('lgOv'), fam = e => getComputedStyle(e).fontFamily.split(',')[0].trim().replace(/"/g, ''), c = o.querySelector('.lgc').getBoundingClientRect();
              return { font: fam(o.querySelector('.lgc')), hfont: fam(o.querySelector('.lgh')), cur: TengelKisekae.current(), inside: c.top >= 0 && c.bottom <= innerHeight && c.left >= 0 && c.right <= innerWidth, over: [...o.querySelectorAll('.lgd li')].some(e => [...e.querySelectorAll('.d, .p')].some(c => { const g = document.createRange(); g.selectNodeContents(c); const t = g.getBoundingClientRect(), q = e.getBoundingClientRect(); return t.right > q.right - 1 || t.left < q.left + 1; })) }; }""")
            shot(pg, 'login_theme')
            check(th is not None and kf['cur'] == th and f1['body'] != f0['body'] and kf['font'] == f1['body'] and kf['hfont'] == f1['disp'] and kf['inside'] and not kf['over'],
                  f'壁紙を かえる（{th}）→ 窓の 字も その 壁紙の 字（本文 {f0["body"]} → {kf["font"]}・見出し {f0["disp"]} → {kf["hfont"]}）・はみ出さない')
            pg.evaluate("() => { TengelLogin.close(); TengelKisekae.apply('default', false); }"); pg.wait_for_timeout(700)
        # 小さい 画面（320×568）でも おさまる
        pg.set_viewport_size({'width': 320, 'height': 568}); pg.evaluate("() => { TengelLogin.next(); }"); pg.wait_for_function("() => !!document.getElementById('lgOv')", timeout=10000); pg.wait_for_timeout(500)
        sm = pg.evaluate("""() => { const o = document.getElementById('lgOv'), c = o.querySelector('.lgc'), r = c.getBoundingClientRect(), bt = o.querySelector('.lgb').getBoundingClientRect();
          return { inside: r.top >= 0 && r.bottom <= innerHeight + 0.5 && r.left >= 0 && r.right <= innerWidth + 0.5, ok: bt.bottom <= innerHeight && bt.top >= 0, sc: c.scrollHeight - c.clientHeight, over: [...o.querySelectorAll('.lgd li')].some(e => [...e.querySelectorAll('.d, .p')].some(c => { const g = document.createRange(); g.selectNodeContents(c); const t = g.getBoundingClientRect(), q = e.getBoundingClientRect(); return t.right > q.right - 1 || t.left < q.left + 1; })) }; }""")
        shot(pg, 'login_small')
        check(sm['inside'] and sm['ok'] and not sm['over'], f'小さい 画面（320×568）でも 窓は 画面の 中・「OK」が 押せる 所に ある・札の 字は はみ出さない（中の スクロール {sm["sc"]}px）')
        pg.evaluate("() => TengelLogin.close()"); pg.set_viewport_size({'width': 390, 'height': 844})
        # 設定 › ポイント › 履歴
        pg.evaluate("() => { document.querySelector('.tabbar button[data-tab=set]').click(); }"); pg.wait_for_timeout(600)
        pg.evaluate("() => { const b = document.querySelector('#setPoints [data-pt=show][data-v=hist]'); if (b) b.click(); }"); pg.wait_for_timeout(500)
        hs = pg.evaluate("() => [...document.querySelectorAll('#setPoints .pthist li')].map(li => li.textContent).filter(t => t.includes('ログインボーナス')).slice(0, 4)")
        check(len(hs) >= 1 and all('ミッション：' not in t and re.search(r'ログインボーナス（[1-7]日目）', t) for t in hs) and any(re.search(r'\+\s?[\d,]+P', t) for t in hs),
              f'設定の ポイントの 履歴に「ログインボーナス（○日目）　+○P」（「ミッション：」は つかない）{hs[:2]}')
        check(not errs and not dialogs, f'エラー なし・confirm()／alert() の 窓は 出て いない {errs[:3]} {dialogs[:3]}')
        ctx.close()

        print('■ App Store版')
        c2 = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo'); c2.add_init_script(FAKE); c2.add_init_script(CLOCK + AUTO)
        p2 = c2.new_page(); e2 = []; p2.on('pageerror', lambda e: e2.append(str(e)))
        p2.goto(STORE); p2.wait_for_timeout(1500); s0 = p2.evaluate("() => TengelWallet.total()"); gate(p2)
        p2.wait_for_function("() => !!document.getElementById('lgOv')", timeout=20000); p2.wait_for_timeout(600); s1 = p2.evaluate(INFO)
        st_btn = p2.evaluate("() => !!document.querySelector('#lgOv [data-lg=next]')")
        check(s1['line'] == '1日目 の ボーナス+200Pを もらったよ' and s1['total'] == s0 + 200 == 1700 and tiles_ok(s1['tiles'], 0) and not st_btn,
              f'App Store版（はじめの 1,500P）：スタートの 画面の あと「{s1["line"]}」→ {s1["total"]:,}P・テスト版の ボタンは 出ない')
        r6 = p2.evaluate("async () => { const a = await TengelLogin.next(); const s = JSON.parse(localStorage.getItem('tengel.login')); s.off = 5; localStorage.setItem('tengel.login', JSON.stringify(s)); const b = await TengelLogin.check(); return [a, b, TengelLogin.state().off, TengelWallet.total()]; }")
        check(r6 == [-1, -1, 0, 1700], f'App Store版：日付を ずらす しかけ（つぎの 日を ためす・おぼえの 中の ずれ）は 効かない {r6}')
        p2.evaluate("() => TengelLogin.close()")
        check(not e2, f'エラー なし {e2[:3]}')
        c2.close()

        print('■ テストの ブラウザでは 自分からは 出さない／Web版')
        c3 = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo'); c3.add_init_script(FAKE)
        p3 = c3.new_page(); p3.goto(STORE); p3.wait_for_timeout(1500); gate(p3); p3.wait_for_timeout(3000)
        n1 = p3.evaluate(INFO); wd = p3.evaluate("() => navigator.webdriver")
        r7 = p3.evaluate("() => TengelLogin.check()"); p3.wait_for_timeout(500); n2 = p3.evaluate(INFO)
        check(wd is True and not n1['open'] and n1['ev'] == [] and r7 == 0 and n2['open'] and len(n2['ev']) == 1,
              f'テストの 道具の ブラウザ（navigator.webdriver）では 自分からは 出さない（ほかの テストの 画面を ふさがない）・よべば もらえる（{r7}）')
        c3.close()
        c4 = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo'); c4.add_init_script(AUTO)
        p4 = c4.new_page(); e4 = []; p4.on('pageerror', lambda e: e4.append(str(e))); p4.goto(WEB); p4.wait_for_timeout(1500); gate(p4); p4.wait_for_timeout(2500)
        check(p4.evaluate("() => typeof window.TengelLogin === 'undefined' && !document.getElementById('lgOv') && !document.getElementById('lgCss') && localStorage.getItem('tengel.login') === null") and not e4, f'Web版：ログインボーナスは ない（窓も おぼえも ない）・エラー なし {e4[:3]}')
        c4.close()
        b.close()
finally:
    srv.terminate()
print('NG' if fails else 'OK', len(fails), fails)
sys.exit(1 if fails else 0)
