# ログインボーナス（第4.168版）の テスト
#   まさちゃん 2026/11/14 01:26「7.毎日ログインボーナスを作る！１週間単位 ・１日目、200P ・２日目、300P ・３日目、400P ・４日目、500P ・５日目、600P ・６日目、1000P ・７日目、1300P」
#   ・その 日に はじめて アプリを 開いた とき 1回 だけ（開いた ときの 画面〈#gate〉が 消えて から）→ 獲得ポイントに 入る・まん中に 小さな 窓（7日ぶんの 札）
#   ・7日で ひとまわり（200・300・400・500・600・1,000・1,300P → また 1日目）・開かない 日が あっても つづきから
#   ・同じ 日は 2回 もらえない（開き直しても・端末の 時計を もどしても・おぼえを 消しても＝財布の 台帳から 作り直す）
#   ・開いた まま 日付が かわった ときも もらえる（もどって きた とき）
#   ・字は いまの 壁紙の 字（しぼった 字に 入って いる 字 だけ）・窓は confirm()／alert() を 使わない
#   ・App Store版：テスト版の ボタン（つぎの 日を ためす）は 出ない・日付を ずらす しかけは 効かない／Web版には 入れない
#   第4.188版（まさちゃん 2026/11/17 11:22「毎日ログインにも、バトルコイン1日2枚 7日ログインで10枚貰えるようにして！」）：
#   ・ポイントと いっしょに バトルコイン（1〜6日目 2枚・7日目 12枚）→ localStorage 'tengel.cbgift' に ためる（同じ 日は 1回）・窓と 7日ぶんの 札にも 出る
#   第4.191版（まさちゃん 2026/11/17 21:23「お願い！」＝ 21:11「アプリ内のポイントとか、バトルコインとか不正に受け取ることできないようになってる？」）：
#   ・第4.211版：トレーニングセンターの お世話トークン（時間で たまる）も 時計の 番人で 数える（iPhone の 時刻を 進めても ふえない）
#   ・時計の 番人（clock_guard.js の TengelClock）：アプリの 時計（Clock.swift：お願い「clock」）の にせもので、iPhone の 日付を 進めても・アプリを 開き直しても
#     つぎの 日の ボーナスは もらえない・本当に 1日 たつと 本当の 日付の ボーナス・もどしても もらえない・サブスクの ポイントの 期限は 日付を もどしても もどらない・
#     アプリの 時計が ない ときは 前と 同じ（ほかの 場面は この まま）
#   第4.212版（まさちゃん 2026/11/23 10:12「③毎日ログインボーナスポイント変更 １週間単位 １日目、500P ２日目、500P ３日目、1000P ４日目、1000P ５日目、1500P ６日目、1500P ７日目、3000P」・
#     「1.それでやって！」＝ 電源を 入れ直した あとの 抜け穴を インターネットの 時刻で ふさぐ）：
#   ・ボーナスは 500・500・1,000・1,000・1,500・1,500・3,000P（1週間で 9,000P）
#   ・電源を 入れ直した あとは iPhone の 時計を 信じない（前に 見た 時刻 ＋ 電源を 入れてからの 時間）→ 日付を 進めて 入れ直しても もらえない。
#     インターネットの 時刻（アプリの お願い「clock」に net:1）が 届いたら 本当の 時刻に 合わせる（切れて いた あいだの ぶんは つながったら 追いつく）
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
    if os.path.isfile(os.path.join(W, 'ios', 'cb_assets', 'cb_coin.webp')): shutil.copy(os.path.join(W, 'ios', 'cb_assets', 'cb_coin.webp'), os.path.join(SRV, d, 'cb_coin.webp'))      # 第4.188版：バトルコインの 絵（アプリでは Resources に ある）
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c: fails.append(label)


FAKE = open(os.path.join(W, 'test_tc.py'), encoding='utf8').read().split('FAKE = """')[1].split('"""')[0]      # アプリの 窓口の にせもの（test_tc.py と 同じ）
# 端末の 時計を 日に ちで ずらす（window.__dayOff）。ログインボーナスは Date.now() から 日付を 作る
CLOCK = "(() => { const R = Date.now.bind(Date); window.__realNow = R; window.__dayOff = 0; Date.now = () => R() + window.__dayOff * 86400000; })();"
AUTO = 'window.__LOGIN_AUTO = true;'      # テストの ブラウザ（navigator.webdriver）でも、アプリと 同じ ように 自分から 出す
BONUS = [500, 500, 1000, 1000, 1500, 1500, 3000]      # 第4.212版（前は 200・300・400・500・600・1,000・1,300P）
CB = [2, 2, 2, 2, 2, 2, 12]      # 第4.188版：バトルコイン（毎日 2枚・7日目は ＋10枚）
LINE = lambda d: f'{d + 1}日目 の ボーナス+{BONUS[d]:,}Pとバトルコイン+{CB[d]}枚を もらったよ'
INFO = """() => { const o = document.getElementById('lgOv'), s = window.TengelLogin ? TengelLogin.state() : null, d = new Date(Date.now()), p2 = n => (n < 10 ? '0' : '') + n;
  return { open: !!o, title: o ? o.querySelector('.lgh').textContent : null, line: o ? o.querySelector('.lgs').textContent : null, tiles: o ? [...o.querySelectorAll('.lgd li')].map(e => (e.className || '-') + ':' + e.textContent) : null,
    ck: o ? o.querySelectorAll('.lgd .ck').length : 0, n: s && s.n, last: s && s.last, off: s && s.off, total: TengelWallet.total(), today: d.getFullYear() + '-' + p2(d.getMonth() + 1) + '-' + p2(d.getDate()),
    ev: TengelWallet.events().filter(e => /^login-/.test(e.id)).map(e => [e.id, e.amount, e.what, e.kind]), shown: window.TengelLogin ? TengelLogin.shown() : null,
    gift: JSON.parse(localStorage.getItem('tengel.cbgift') || 'null') }; }"""


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
    want = [('got' if i < day else 'now' if i == day else '-') + f':{i + 1}日目{BONUS[i]:,}P{CB[i]}枚' for i in range(7)]
    return tl == want


try:
    print('■ 中身（ビルド）')
    src = open(os.path.join(W, 'login_bonus.js'), encoding='utf8').read(); code = re.sub(r'//[^\n]*', '', src)
    app = open(os.path.join(SRV, 'APP', 'index.html'), encoding='utf8').read(); store = open(os.path.join(SRV, 'STORE', 'index.html'), encoding='utf8').read(); web = open(os.path.join(SRV, 'TENGEL', 'index.html'), encoding='utf8').read()
    check(all('window.TengelLogin = {' in x and "'tengel.login'" in x and 'BONUS = [500, 500, 1000, 1000, 1500, 1500, 3000]' in x and 'BONUS = [200, 300' not in x and "var CBK = 'tengel.cbgift', CBDAY = 2, CB7 = 10;" in x for x in (app, store)) and sum(BONUS) == 9000 and sum(CB) == 24,
          'App Store版・テスト版の index.html に ログインボーナス（login_bonus.js）が 入って いる・表は 500・500・1,000・1,000・1,500・1,500・3,000P（1週間で 9,000P：第4.212版）・バトルコイン 毎日 2枚・7日目 ＋10枚（第4.188版）')
    cba = open(os.path.join(W, 'cb', 'cb_app.js'), encoding='utf8').read()
    check('const COIN = { win: 2, bonus: [[3, 6], [5, 10]], day: 2, day7: 10, max: 9999 };' in cba and "const GK = 'tengel.cbgift';" in cba, 'カードバトルの 説明の 数（day 2・day7 10）と 受け取る 場所（tengel.cbgift）が ログインボーナスと 同じ')
    check('tengel.cbgift' not in web, 'Web版には バトルコインの しくみも ない')
    check('TengelLogin' not in web and 'ログインボーナス' not in web and 'tengel.login' not in web, 'Web版には 入って いない（かわらない）')
    check(all(0 < x.find('window.TengelClock = {') < x.find('window.TengelWallet = {') and x.find('window.TengelClock = {') < x.find('window.TengelLogin = {') and "N.call('clock', {})" in x and "N.call('clock', { net: 1 })" in x for x in (app, store))
          and 'TengelClock' not in web and 'tengel.clock' not in web,
          '第4.191版：時計の 番人（clock_guard.js）は App Store版・テスト版の ポイント・ログインボーナスより 前に 入って いる（Web版には ない）・第4.212版：インターネットの 時刻も 聞く（net:1）')
    check('confirm(' not in code and 'alert(' not in code and 'prompt(' not in code, '窓は confirm()・alert() を 使わない（アプリの 中では 出ない）')
    body = set(open(os.path.join(W, 'ios', 'fonts', 'ks', 'chars_body.txt'), encoding='utf8').read()); disp = set(open(os.path.join(W, 'ios', 'fonts', 'ks', 'chars_disp.txt'), encoding='utf8').read())
    strs = ''.join(re.findall(r"'((?:[^'\\]|\\.)*)'", code)); lack = sorted({c for c in strs if ord(c) > 0x2000 and c not in body}); lackd = [c for c in 'ログインボーナス' if c not in disp]
    sys.path.insert(0, os.path.join(W, 'kisekae')); import build_fonts as _bf
    check(not lack and not lackd and 'login_bonus.js' in open(os.path.join(W, 'kisekae', 'build_fonts.py'), encoding='utf8').read() and not (set(_bf.body_chars()) - body),
          f'画面の 言葉は しぼった 字（本文 {len(body)}字・見出し {len(disp)}字）に 入って いる 字 だけ（足りない 字 {lack}{lackd}）・字を しぼる 道具（kisekae/build_fonts.py）も login_bonus.js を 見る')
    man = re.sub(r'<[^>]+>', '', open(os.path.join(W, 'manual', 'content_app.html'), encoding='utf8').read())      # タグを とった 文
    check('ログインボーナス' in man and all(f'{i + 1}日目 {BONUS[i]:,}P' in man for i in range(7)) and '7日で一回り' in man.replace(' ', ''),
          '説明書（ポイントの もらい方）に ログインボーナスの 行（1日目 500P 〜 7日目 3,000P・7日で ひとまわり）')
    pu = open(os.path.join(W, 'points_ui.js'), encoding='utf8').read()
    check("/^(rel-)?back-(theme|fig):|^login-/.test(String(e.id)) ? '' : 'ミッション：'" in pu, 'ポイントの 履歴：ログインボーナスには「ミッション：」を つけない（第4.176版から 思い出フィギュアの 返した ぶんも）')

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
        check(a['open'] and a['title'] == 'ログインボーナス' and a['line'] == LINE(0) and tiles_ok(a['tiles'], 0) and a['ck'] == 1 and a['shown'] == 0,
              f'スタートの 画面が 消えると 窓「ログインボーナス」：「{a["line"]}」・7日ぶんの 札（今日＝1日目に しるし）{a["tiles"]}')
        check(a['ev'] == [[f'login-{a["today"]}', 500, 'ログインボーナス（1日目）', 'mission']] and a['total'] == t0 + 500 and a['n'] == 1 and a['last'] == a['today'],
              f'獲得ポイントに 500P 入る（{t0:,} → {a["total"]:,}P）・台帳に 1件（login-<今日>）・おぼえ（1回・今日）{a["ev"]}')
        ci = pg.evaluate("() => { const o = document.getElementById('lgOv'); return [...o.querySelectorAll('img.lgci')].map(i => [i.getAttribute('src'), i.complete && i.naturalWidth > 0, Math.round(i.getBoundingClientRect().width)]); }")
        check(a['gift'] == {'v': 1, 'list': [{'id': f'login-{a["today"]}', 'c': 2}]} and len(ci) == 8 and all(x[0] == 'cb_coin.webp' and x[1] and x[2] >= 14 for x in ci),
              f'バトルコイン 2枚を ためる（tengel.cbgift：カードバトルが 受け取る）・窓の 字と 7日ぶんの 札に コインの 絵（{len(ci)}こ）{a["gift"]}')
        lay = pg.evaluate("""() => { const o = document.getElementById('lgOv'), c = o.querySelector('.lgc').getBoundingClientRect(), bt = o.querySelector('.lgb').getBoundingClientRect(), cs = getComputedStyle(o), t = document.elementFromPoint(c.left + c.width / 2, c.top + 20);
          const li = [...o.querySelectorAll('.lgd li')], lr = li.map(e => e.getBoundingClientRect()), fam = e => getComputedStyle(e).fontFamily.split(',')[0].trim().replace(/"/g, ''), tb = document.elementFromPoint(8, innerHeight - 8);
          return { z: +cs.zIndex, pos: cs.position, inside: c.left >= 0 && c.right <= innerWidth && c.top >= 0 && c.bottom <= innerHeight, top: !!t && o.contains(t), bh: bt.height, role: o.getAttribute('role'), modal: o.getAttribute('aria-modal'), label: o.getAttribute('aria-label'),
            font: fam(o.querySelector('.lgc')), hfont: fam(o.querySelector('.lgh')), bodyFont: fam(document.querySelector('.card') || document.body), rows: new Set(lr.map(r => Math.round(r.top))).size, wide7: lr[6].width > lr[5].width * 1.6,
            over: li.some(e => [...e.querySelectorAll('.d, .p, .c')].some(c => { const g = document.createRange(); g.selectNodeContents(c); const t = g.getBoundingClientRect(), q = e.getBoundingClientRect(); return t.right > q.right - 1 || t.left < q.left + 1; })),      // 札の 字（○日目・○P）が 札の 中に おさまる（かどの しるしは 札の 外へ 少し 出る 形）
             test: !!o.querySelector('[data-lg=next]'), tabz: +getComputedStyle(document.querySelector('.tabbar')).zIndex, cover: !!tb && o.contains(tb), w: c.width, h: c.height }; }""")
        check(lay['pos'] == 'fixed' and lay['z'] == 60 and lay['z'] > lay['tabz'] and lay['inside'] and lay['top'] and lay['cover'] and lay['bh'] >= 40 and lay['role'] == 'dialog' and lay['modal'] == 'true' and lay['label'] == 'ログインボーナス'
              and lay['rows'] == 2 and lay['wide7'] and not lay['over'],
              f'窓：画面の まん中（{lay["w"]:.0f}×{lay["h"]:.0f}・画面の 中に おさまる）・下の タブより 上（うしろは 押せない）・札は 4つ＋3つの 2段（7日目は 広い）・字は はみ出さない・「OK」の 高さ {lay["bh"]:.0f}px {"" if lay["cover"] and lay["top"] and not lay["over"] and lay["rows"] == 2 and lay["wide7"] else lay}')
        check(lay['font'] == lay['bodyFont'] == 'BIZ UDPGothic' and lay['hfont'] == 'Dela Gothic One' and lay['test'], f'字は いまの 壁紙の 字（本文 {lay["font"]}・見出し {lay["hfont"]}）・テスト版 だけ「つぎの 日を ためす」が ある')
        pg.locator('#lgOv [data-lg=ok]').click(); pg.wait_for_timeout(300)
        c1 = pg.evaluate(INFO); r1 = pg.evaluate("() => TengelLogin.check()"); pg.wait_for_timeout(400); c2 = pg.evaluate(INFO)
        check(not c1['open'] and c1['shown'] is None and r1 == -1 and not c2['open'] and len(c2['ev']) == 1 and c2['total'] == a['total'] and c2['gift'] == a['gift'], f'「OK」で とじる・同じ 日に もう 1回 確かめても もらえない（{r1}・{c2["total"]:,}P の まま・バトルコインも ふえない）')

        print('■ 開き直し・時計を もどす・おぼえを 消す')
        pg.goto(APP); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(2800); d1 = pg.evaluate(INFO)
        check(not d1['open'] and len(d1['ev']) == 1 and d1['total'] == a['total'] and d1['n'] == 1, f'同じ 日に 開き直しても 窓は 出ない・もらえない（{d1["total"]:,}P の まま）')
        pg.evaluate("() => { window.__dayOff = -3; }"); r2 = pg.evaluate("() => TengelLogin.check()"); pg.wait_for_timeout(300); d2 = pg.evaluate(INFO)
        check(r2 == -1 and len(d2['ev']) == 1 and d2['total'] == a['total'] and d2['today'] < a['today'] and d2['last'] == a['today'], f'端末の 時計を 3日 もどしても もらえない（さいごに もらった 日より あとの 日 だけ：{d2["today"]} < {d2["last"]}）')
        pg.evaluate("() => { window.__dayOff = 0; localStorage.removeItem('tengel.login'); }"); d3s = pg.evaluate("() => TengelLogin.state()"); r3 = pg.evaluate("() => TengelLogin.check()"); pg.wait_for_timeout(300); d3 = pg.evaluate(INFO)
        check(d3s['n'] == 1 and d3s['last'] == a['today'] and r3 == -1 and len(d3['ev']) == 1 and d3['total'] == a['total'] and d3['gift'] == a['gift'], f'おぼえ（localStorage）が 消えても、財布の 台帳から 作り直す（{d3s["n"]}回・{d3s["last"]}）→ 同じ 日に 2回 もらえない')

        print('■ 7日で ひとまわり')
        seq = []; tot = a['total']
        for k in range(1, 9):               # 2日目 … 7日目 → 1日目 → 2日目
            pg.evaluate("(k) => { window.__dayOff = k; }", k); r = pg.evaluate("() => TengelLogin.check()")
            pg.wait_for_function("() => !!document.getElementById('lgOv')", timeout=10000); pg.wait_for_timeout(250); q = pg.evaluate(INFO); tot += BONUS[k % 7]
            seq.append((r, q['line'], tiles_ok(q['tiles'], k % 7), q['ck'] == k % 7 + 1, q['total'] == tot, q['n'] == k + 1, q['last'] == q['today'], q['ev'][-1][:3] == [f'login-{q["today"]}', BONUS[k % 7], f'ログインボーナス（{k % 7 + 1}日目）'],
                        q['gift']['list'][-1] == {'id': f'login-{q["today"]}', 'c': CB[k % 7]}))
            if k in (3, 6): shot(pg, f'login_day{k + 1}')
            pg.evaluate("() => TengelLogin.close()")
        check([x[0] for x in seq] == [1, 2, 3, 4, 5, 6, 0, 1] and [x[1] for x in seq] == [LINE(d) for d in (1, 2, 3, 4, 5, 6, 0, 1)] and all(all(x[2:]) for x in seq),
              f'日付が かわる たびに 1回：2日目 500P → … → 7日目 3,000P → また 1日目 500P → 2日目 500P（札の しるし・ポイント・台帳の 名前・バトルコイン 2枚〈7日目 12枚〉も 合って いる）{[x[0] + 1 for x in seq]}')
        e9 = pg.evaluate(INFO)
        check([x['c'] for x in e9['gift']['list']] == [2, 2, 2, 2, 2, 2, 12, 2, 2] and len({x['id'] for x in e9['gift']['list']}) == 9 and sum(x['c'] for x in e9['gift']['list']) == 24 + 4,
              f'バトルコイン 9日ぶん：2・2・2・2・2・2・12（7日目は 2枚 ＋10枚）・2・2 ＝ {sum(x["c"] for x in e9["gift"]["list"])}枚（日付は ぜんぶ ちがう）')
        check(len(e9['ev']) == 9 and len({x[0] for x in e9['ev']}) == 9 and sum(x[1] for x in e9['ev']) == 9000 + 500 + 500 and e9['total'] == t0 + 10000, f'9日ぶん：台帳に 9件（日付は ぜんぶ ちがう）・合わせて {sum(x[1] for x in e9["ev"]):,}P（1週間 9,000P＋500＋500）')
        pg.evaluate("() => { window.__dayOff = 20; }"); r5 = pg.evaluate("() => TengelLogin.check()"); pg.wait_for_function("() => !!document.getElementById('lgOv')", timeout=10000); pg.wait_for_timeout(250); f1 = pg.evaluate(INFO)
        check(r5 == 2 and f1['line'] == LINE(2) and f1['n'] == 10, f'開かない 日が あっても（11日 あいた）つづきから：「{f1["line"]}」（1日目に もどさない）')
        # 外（暗い 所）を 押すと とじる・窓の 中を 押しても とじない
        cc = pg.evaluate("() => { const c = document.querySelector('#lgOv .lgc').getBoundingClientRect(); return [c.left + c.width / 2, c.top + 30]; }")
        pg.touchscreen.tap(*cc); pg.wait_for_timeout(250); k1 = pg.evaluate("() => !!document.getElementById('lgOv')")
        pg.touchscreen.tap(12, 60); pg.wait_for_timeout(300); k2 = pg.evaluate("() => !!document.getElementById('lgOv')")
        check(k1 and not k2, '窓の 中を 押しても とじない・外（暗い 所）を 押すと とじる')

        print('■ 開いた まま 日付が かわった とき・テスト版の ボタン')
        pg.evaluate("() => { window.__dayOff = 21; document.dispatchEvent(new Event('visibilitychange')); }")
        pg.wait_for_function("() => !!document.getElementById('lgOv')", timeout=10000); pg.wait_for_timeout(250); v1 = pg.evaluate(INFO)
        check(v1['line'] == LINE(3) and v1['n'] == 11 and v1['last'] == v1['today'], f'アプリに もどって きた とき（日付が かわって いた）にも もらえる：「{v1["line"]}」')
        pg.locator('#lgOv [data-lg=next]').click(); pg.wait_for_timeout(900); v2 = pg.evaluate(INFO)
        check(v2['open'] and v2['line'] == LINE(4) and v2['n'] == 12 and v2['off'] == 1 and v2['last'] > v1['last'] and len(v2['ev']) == 12,
              f'テスト版の「つぎの 日を ためす」→ 日付を 1日 先に 進めた ことに して つぎの ボーナス：「{v2["line"]}」（ずらした 日数 {v2["off"]}）')
        pg.evaluate("() => TengelLogin.close()")
        # 壁紙を かえると 窓の 字も かわる（ポイントで 解放した 壁紙で：持って いない 壁紙は 財布が かわった ときに 標準へ もどる）
        if pg.evaluate("() => !!(window.TengelKisekae && TengelKisekae.on)"):
            FAM = """() => { const fam = e => getComputedStyle(e).fontFamily.split(',')[0].trim().replace(/"/g, ''), pr = document.createElement('span'); pr.style.fontFamily = 'var(--font-display)'; document.body.appendChild(pr);
              const r = { body: fam(document.querySelector('.card') || document.body), disp: fam(pr), cur: TengelKisekae.current() }; pr.remove(); return r; }"""
            f0 = pg.evaluate(FAM)
            #   第4.230版：ポイントで 解放する 壁紙は ぜんぶ ＋2,000P（いちばん 安い のが 6,500P）＝ 今の ポイントより 高い ときは、足りない ぶんを テスト用に 足して から 解放する
            th = pg.evaluate("""async () => { const ts = TengelKisekae.list().filter(t => t.id !== 'default' && t.price).sort((a, b) => a.price - b.price), fam = e => getComputedStyle(e).fontFamily.split(',')[0].trim().replace(/"/g, '');
              if (ts.length && TengelWallet.total() < ts[0].price) await TengelWallet.grant('test-login-wall', ts[0].price - TengelWallet.total(), 'テストの 当たり');
              for (const t of ts.slice(0, 6)) { if (!(TengelKisekae.usable(t.id) || await TengelWallet.unlock('theme:' + t.id, t.price))) continue; await TengelKisekae.apply(t.id, false); await new Promise(r => setTimeout(r, 500));
                if (fam(document.querySelector('.card') || document.body) !== 'BIZ UDPGothic') return t.id; } return null; }""")
            pg.wait_for_timeout(900); f1 = pg.evaluate(FAM)
            pg.evaluate("() => { TengelLogin.next(); }"); pg.wait_for_function("() => !!document.getElementById('lgOv')", timeout=10000); pg.wait_for_timeout(500)
            kf = pg.evaluate("""() => { const o = document.getElementById('lgOv'), fam = e => getComputedStyle(e).fontFamily.split(',')[0].trim().replace(/"/g, ''), c = o.querySelector('.lgc').getBoundingClientRect();
              return { font: fam(o.querySelector('.lgc')), hfont: fam(o.querySelector('.lgh')), cur: TengelKisekae.current(), inside: c.top >= 0 && c.bottom <= innerHeight && c.left >= 0 && c.right <= innerWidth, over: [...o.querySelectorAll('.lgd li')].some(e => [...e.querySelectorAll('.d, .p, .c')].some(c => { const g = document.createRange(); g.selectNodeContents(c); const t = g.getBoundingClientRect(), q = e.getBoundingClientRect(); return t.right > q.right - 1 || t.left < q.left + 1; })) }; }""")
            shot(pg, 'login_theme')
            check(th is not None and kf['cur'] == th and f1['body'] != f0['body'] and kf['font'] == f1['body'] and kf['hfont'] == f1['disp'] and kf['inside'] and not kf['over'],
                  f'壁紙を かえる（{th}）→ 窓の 字も その 壁紙の 字（本文 {f0["body"]} → {kf["font"]}・見出し {f0["disp"]} → {kf["hfont"]}）・はみ出さない')
            pg.evaluate("() => { TengelLogin.close(); TengelKisekae.apply('default', false); }"); pg.wait_for_timeout(700)
        # 小さい 画面（320×568）でも おさまる
        pg.set_viewport_size({'width': 320, 'height': 568}); pg.evaluate("() => { TengelLogin.next(); }"); pg.wait_for_function("() => !!document.getElementById('lgOv')", timeout=10000); pg.wait_for_timeout(500)
        sm = pg.evaluate("""() => { const o = document.getElementById('lgOv'), c = o.querySelector('.lgc'), r = c.getBoundingClientRect(), bt = o.querySelector('.lgb').getBoundingClientRect();
          return { inside: r.top >= 0 && r.bottom <= innerHeight + 0.5 && r.left >= 0 && r.right <= innerWidth + 0.5, ok: bt.bottom <= innerHeight && bt.top >= 0, sc: c.scrollHeight - c.clientHeight, over: [...o.querySelectorAll('.lgd li')].some(e => [...e.querySelectorAll('.d, .p, .c')].some(c => { const g = document.createRange(); g.selectNodeContents(c); const t = g.getBoundingClientRect(), q = e.getBoundingClientRect(); return t.right > q.right - 1 || t.left < q.left + 1; })) }; }""")
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

        print('■ 時計の 番人（第4.191版：iPhone の 日付を 進めても・もどしても ずるは できない）')
        FAKE2 = FAKE.replace("  if (m.name === 'iap')", "  if (m.name === 'clock' && window.__clk) val = window.__clk(P);\n  if (m.name === 'iap')"); assert FAKE2 != FAKE
        # 本当の 時刻 ＝ 本物の 時計 ＋ st.real（テストで 時間を たたせる）・iPhone の 時計 ＝ 本当の 時刻 ＋ st.day 日（設定で かえた）・電源を 入れてからの 時間 ＝ st.mb ＋ 本物の 時計 ＋ st.real
        #   第4.212版：インターネットの 時刻（st.net＝つながって いる とき：お願い「clock」に net:1 が ついて いたら 本当の 時刻を 返す。つながって いない ときは net なし）・
        #   __reboot(off)＝電源を 切って off ミリ秒 たってから 入れ直した（本当の 時刻は off 進む・電源を 入れてからの 時間は 1分から）
        CLK2 = """(() => { const R = Date.now.bind(Date), K = '__clkw', st = JSON.parse(sessionStorage.getItem(K) || 'null') || { real: 0, day: 0, boot: 'B1', mb: 5 * 86400000 - R(), net: 0, nets: 0 };
  const put = () => sessionStorage.setItem(K, JSON.stringify(st)); put(); const proc = 'P' + R() + Math.random();
  Date.now = () => R() + st.real + st.day * 86400000;
  window.__clk = P => { const mono = st.mb + R() + st.real, o = { wall: Date.now(), mono: mono, boot: st.boot, proc: proc, dev: 'D1' };
    if (P && P.net) { st.nets++; put(); o.net = st.net ? { ok: true, t: R() + st.real + (st.skew || 0), mono: mono - 20, rt: 40, why: '' } : { ok: false, t: 0, mono: 0, rt: 0, why: 'net' }; } return o; };
  window.__pass = ms => { st.real += ms; put(); }; window.__setDay = d => { st.day = d; put(); }; window.__reboot = off => { st.real += off || 0; st.boot = 'B' + R() + Math.random(); st.mb = 60000 - R() - st.real; put(); };
  window.__netOn = (v, skew) => { st.net = v ? 1 : 0; st.skew = skew || 0; put(); }; window.__nets = () => st.nets; window.__real = () => R() + st.real;
  window.__hows = []; document.addEventListener('tengel:clock', e => window.__hows.push(e.detail.how)); })();"""
        CLKI = """() => { const p2 = n => (n < 10 ? '0' : '') + n, ymd = ms => { const d = new Date(ms); return d.getFullYear() + '-' + p2(d.getMonth() + 1) + '-' + p2(d.getDate()); };
  return { how: TengelClock.how(), hows: window.__hows.slice(), st: TengelClock.state(), wall: ymd(Date.now()), trusted: ymd(TengelClock.now()), open: !!document.getElementById('lgOv'), sure: TengelClock.sure(), real: ymd(window.__real()), lag: Math.round((window.__real() - TengelClock.now()) / 1000), nets: window.__nets(),
    ev: TengelWallet.events().filter(e => /^login-/.test(e.id)).map(e => e.id), gift: (JSON.parse(localStorage.getItem('tengel.cbgift') || 'null') || { list: [] }).list.map(x => x.id) }; }"""
        c5 = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo'); c5.add_init_script(FAKE2); c5.add_init_script(CLK2 + AUTO)
        p5 = c5.new_page(); e5 = []; p5.on('pageerror', lambda e: e5.append(str(e)))
        p5.goto(APP); p5.wait_for_timeout(1500); p5.wait_for_function("() => window.TengelWallet && TengelWallet.on && TengelWallet.total() >= 10000", timeout=20000); p5.wait_for_timeout(1100); gate(p5)
        p5.wait_for_function("() => !!document.getElementById('lgOv')", timeout=20000); p5.wait_for_timeout(400); k0 = p5.evaluate(CLKI); p5.evaluate("() => TengelLogin.close()")
        check(k0['how'] in ('first', 'ok') and k0['ev'] == [f'login-{k0["wall"]}'] and k0['trusted'] == k0['wall'] and k0['st']['boot'] == 'B1' and k0['st']['dev'] == 'D1' and k0['gift'] == k0['ev']
              and k0['st']['u'] == 1 and k0['st']['nv'] == 0 and not k0['sure'] and k0['nets'] >= 1,
              f'アプリの 時計で たしかめて 今日の ボーナス（{k0["how"]}・{k0["ev"]}）・おぼえ（tengel.clock）に 起動の 番号と 端末の 番号・インターネットの 時刻は 聞いた が まだ 届いて いない（つながって いない：u=1・聞いた {k0["nets"]}回）')
        p5.evaluate("() => __setDay(1)"); r1 = p5.evaluate("() => TengelLogin.check()"); p5.wait_for_timeout(400); k1 = p5.evaluate(CLKI)
        check(r1 == -1 and not k1['open'] and k1['ev'] == k0['ev'] and k1['gift'] == k0['gift'] and k1['how'] == 'ahead' and k1['wall'] > k1['trusted'] == k0['wall'],
              f'iPhone の 日付を 1日 進めても、つぎの 日の ボーナス（ポイント・バトルコイン）は もらえない（{k1["how"]}・iPhone {k1["wall"]}・本当 {k1["trusted"]}）')
        p5.goto(APP); p5.wait_for_timeout(1500); gate(p5); p5.wait_for_timeout(2500); k2 = p5.evaluate(CLKI)
        check(not k2['open'] and k2['ev'] == k0['ev'] and k2['hows'] and set(k2['hows']) == {'ahead'} and k2['trusted'] == k0['wall'] and k2['st']['proc'] != k1['st']['proc'] and k2['st']['hi'] < k2['st']['t'] + 600000,
              f'進めた まま アプリを 開き直しても もらえない（{k2["hows"]}：起動の 番号が 同じ ＝ 電源を 入れ直して いない・開いた すぐ あとの iPhone の 時計は おぼえない）')
        p5.evaluate("() => __pass(86400000)"); r3 = p5.evaluate("() => TengelLogin.check()")
        p5.wait_for_function("() => !!document.getElementById('lgOv')", timeout=10000); p5.wait_for_timeout(300); k3 = p5.evaluate(CLKI); p5.evaluate("() => TengelLogin.close()")
        check(r3 == 1 and k3['ev'] == k0['ev'] + [f'login-{k3["trusted"]}'] and k3['trusted'] > k0['wall'] and k3['trusted'] < k3['wall'],
              f'本当に 1日 たつと 本当の 日付（{k3["trusted"]}）の 2日目の ボーナス（iPhone は {k3["wall"]}：進めた ぶんは 先どり できない）')
        p5.evaluate("() => __setDay(0)"); r4 = p5.evaluate("() => TengelLogin.check()"); p5.wait_for_timeout(400); k4 = p5.evaluate(CLKI)
        p5.evaluate("() => __setDay(-3)"); r5 = p5.evaluate("() => TengelLogin.check()"); p5.wait_for_timeout(400); k5 = p5.evaluate(CLKI)
        check(r4 == -1 and k4['how'] == 'ok' and r5 == -1 and k5['how'] == 'back' and k5['trusted'] == k4['trusted'] == k3['trusted'] and k5['ev'] == k3['ev'],
              f'日付を もとに もどす（{k4["how"]}）・3日 もどす（{k5["how"]}：本当の 日付は {k5["trusted"]} の まま）→ もらえない')
        p5.evaluate("() => __setDay(0)")
        # サブスクの ポイントの 期限（30日）：31日 たって 切れた → iPhone の 日付を 31日 もどしても 使えない
        sub = p5.evaluate("""async () => { window.__nativeEvent('iap', { id: '77001', originalId: '77001', product: 'jp.tengel.app.sub9200', kind: 'sub', date: new Date(Date.now()).toISOString(), revoked: false, env: 'Xcode' });
          await new Promise(r => setTimeout(r, 800)); return TengelWallet.balance().paid_sub; }""")
        p5.evaluate("() => __pass(31 * 86400000)"); x1 = p5.evaluate("async () => { await TengelClock.sync(); return [TengelWallet.balance().paid_sub, TengelClock.how()]; }")
        p5.evaluate("() => __setDay(-31)"); x2 = p5.evaluate("async () => { await TengelClock.sync(); return [TengelWallet.balance().paid_sub, TengelClock.how()]; }")
        p5.evaluate("() => __setDay(0)"); p5.evaluate("() => TengelLogin.close()")
        check(sub >= 9200 and x1 == [0, 'ok'] and x2 == [0, 'back'], f'サブスクの ポイント（{sub:,}P）：31日 たって 期限が 切れた（{x1}）→ iPhone の 日付を 31日 もどしても 使えない（{x2}）')
        # 第4.211版（抜け穴を ふさぐ）：トレーニングセンターの お世話トークン（5分で 5個・第4.230版から 8分で 5個・25個 まで）も 時計の 番人で 数える。
        #   前は iPhone の 時計（Date.now）だった ので、時刻を 25分 進める たびに 満タン（＝抽選 25回）に できた
        TKN = ("async (sync) => { if (sync) await TengelClock.sync(); await TengelClock.ready; "      # 第4.212版：トークンを わたす 口（TCGift）は なくした → トレーニングセンターの 部品を 読んで、いまの 数を 読む（tokens.now：ふやさない）
               "if (!window.TCApp) await new Promise((ok, ng) => { const s = document.createElement('script'); s.src = 'tc_bundle.js'; s.onload = ok; s.onerror = ng; document.head.appendChild(s); }); "
               "const r = TCApp.tokens.now(); return [r && r.stock, TengelClock.how()]; }")
        t0 = p5.evaluate(TKN, True)
        p5.evaluate("() => { const s = TCApp.state; s.stock = 0; s.stockAt = TengelClock.now(); s.seen = TengelClock.now(); localStorage.setItem('tengel.tc', JSON.stringify(s)); }")
        ta = p5.evaluate(TKN, True)
        p5.evaluate("() => __setDay(1)"); tb = p5.evaluate(TKN, False); tc_ = p5.evaluate(TKN, True)      # iPhone の 日付を 1日 進めた すぐ あと（たしかめる 前）・たしかめた あと
        p5.goto(APP); p5.wait_for_timeout(1500); gate(p5); p5.wait_for_timeout(600); p5.evaluate("() => TengelLogin.close()"); td = p5.evaluate(TKN, False)      # 進めた まま アプリを 開き直した（開いた すぐ あとの TCGift は 番人が たしかめ おわる のを 待つ）
        p5.evaluate("() => __pass(8 * 60000 + 2000)"); te = p5.evaluate(TKN, True)      # 本当に 8分 たった（第4.230版：8分で 5個）
        p5.evaluate("() => __setDay(-2)"); tf = p5.evaluate(TKN, True)                  # 日付を もどした
        p5.evaluate("() => __setDay(0)"); p5.evaluate("() => __pass(60 * 60000)"); tg = p5.evaluate(TKN, True)      # 本当に 1時間 たった
        sv = p5.evaluate("() => { const s = JSON.parse(localStorage.getItem('tengel.tc')); return [s.stock, s.seen <= TengelClock.now() + 1000, s.stockAt <= TengelClock.now() + 1000]; }")
        check(t0[0] == 5 and ta == [0, 'ok'] and tb[0] == 0 and tc_ == [0, 'ahead'] and td[0] == 0 and te[0] == 5 and tf == [5, 'back'] and tg == [25, 'ok'] and sv == [25, True, True],
              f'お世話トークン：iPhone の 日付を 1日 進めても ふえない（たしかめる 前 {tb[0]}個・あと {tc_}・開き直しても {td[0]}個）→ 本当に 8分 たつと 5個（{te}）・日付を もどしても そのまま（{tf}）・1時間で 満タン（{tg}）')
        p5.evaluate("() => TengelLogin.close()")
        # 第4.212版：電源を 入れ直した（日付を 進めた まま・つながって いない）→ iPhone の 時計は 信じない：前に 見た 時刻 ＋ 電源を 入れてからの 時間（1分）→ もらえない
        #   （前の 版：わからない ので iPhone の 時計を 信じた ＝ 日付を 進めて 入れ直す たびに 1日ぶん もらえた）
        p5.evaluate("async () => { await TengelLogin.check(); TengelLogin.close(); }"); p5.wait_for_timeout(300); k6 = p5.evaluate(CLKI)
        p5.evaluate("() => { __setDay(1); __reboot(0); }"); p5.goto(APP); p5.wait_for_timeout(1500); gate(p5); p5.wait_for_timeout(3200); k7 = p5.evaluate(CLKI)
        check(k7['hows'][:1] == ['boot'] and k7['st']['boot'] not in ('', 'B1') and k7['st']['u'] == 1 and not k7['sure'] and not k7['open'] and k7['ev'] == k6['ev'] and k7['trusted'] == k6['trusted'] and k7['wall'] > k7['trusted'],
              f'日付を 1日 進めた まま 電源を 入れ直す（つながって いない）→ iPhone の 時計は 信じない（{k7["hows"][:3]}・iPhone {k7["wall"]}・番人 {k7["trusted"]}）→ ボーナスは もらえない（前の 版は もらえた）')
        p5.evaluate("() => { __setDay(3); __reboot(0); }"); p5.goto(APP); p5.wait_for_timeout(1500); gate(p5); p5.wait_for_timeout(3200); k8 = p5.evaluate(CLKI)
        t8 = p5.evaluate(TKN, True)
        check(k8['hows'][:1] == ['boot'] and not k8['open'] and k8['ev'] == k6['ev'] and k8['trusted'] == k6['trusted'] and t8[0] == tg[0],
              f'もっと 進めて（3日）もう 1回 入れ直しても 同じ（入れ直しを くり返しても もらえない・お世話トークンも ふえない：{t8}）')
        # つながった → インターネットの 時刻が 届く：本当の 日付は まだ 同じ 日（もらった 日）→ もらえない・たしかめずみ（sure）
        p5.evaluate("() => { __setDay(3); __netOn(1); }"); p5.goto(APP); p5.wait_for_timeout(1500); gate(p5); p5.wait_for_timeout(3200); k9 = p5.evaluate(CLKI)
        check('net' in k9['hows'] and k9['st']['u'] == 0 and k9['st']['nv'] > 0 and k9['sure'] and not k9['open'] and k9['ev'] == k6['ev'] and k9['trusted'] == k9['real'] == k6['trusted'] and abs(k9['lag']) <= 200,
              f'つながると インターネットの 時刻で 合わせる（{k9["hows"][:4]}・ずれ {k9["lag"]}秒・たしかめずみ）：本当の 日付は まだ {k9["real"]} → もらえない（iPhone は {k9["wall"]}）')
        n9 = k9['nets']; p5.evaluate("async () => { await TengelClock.sync(); await TengelClock.sync(); }"); p5.wait_for_timeout(300)
        check(p5.evaluate("() => __nets()") == n9, f'たしかめた あとは インターネットに 聞き直さない（7日に 1回・電源を 入れ直した あと だけ：聞いた 数 {n9} の まま）')
        # 電源を 切って いる あいだに 本当に 2日 たった（つながって いない）→ まだ 追いつかない（もらえない）→ つながると 追いついて その 日の ボーナス
        p5.evaluate("() => { __setDay(0); __netOn(0); __reboot(2 * 86400000); }"); p5.goto(APP); p5.wait_for_timeout(1500); gate(p5); p5.wait_for_timeout(3200); k10 = p5.evaluate(CLKI)
        check(k10['hows'][:1] == ['boot'] and k10['st']['u'] == 1 and not k10['sure'] and not k10['open'] and k10['ev'] == k6['ev'] and k10['trusted'] == k6['trusted'] and k10['real'] > k10['trusted'] and k10['lag'] > 86400,
              f'電源を 切って いる あいだに 2日 たった（つながって いない）：切れて いた あいだの 時間は まだ 足さない（番人 {k10["trusted"]}・本当 {k10["real"]}・おくれ {k10["lag"] // 3600}時間）→ まだ もらえない')
        p5.evaluate("() => __netOn(1)"); p5.goto(APP); p5.wait_for_timeout(1500); gate(p5)
        p5.wait_for_function("() => !!document.getElementById('lgOv')", timeout=20000); p5.wait_for_timeout(400); k11 = p5.evaluate(CLKI); p5.evaluate("() => TengelLogin.close()")
        t11 = p5.evaluate(TKN, True)
        check('net' in k11['hows'] and k11['sure'] and k11['trusted'] == k11['real'] == k11['wall'] and k11['ev'] == k6['ev'] + [f'login-{k11["real"]}'] and abs(k11['lag']) <= 3 and t11[0] == 25,
              f'つながると 追いつく（{k11["hows"][:4]}）→ 本当の 日付（{k11["real"]}）の ボーナスが もらえる・お世話トークンも たまって いる（{t11}）')
        # インターネットの 時刻が 番人より 10分 より 前（はじめに 見た iPhone の 時計が 進んで いた）→ そこへ もどす（進んだ ままに しない）
        c6 = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo'); c6.add_init_script(FAKE2)
        c6.add_init_script(CLK2 + AUTO + "if (!sessionStorage.getItem('__d5')) { sessionStorage.setItem('__d5', '1'); window.__setDay(5); }")      # はじめて 入れた とき iPhone の 日付が 5日 進んで いた
        p6 = c6.new_page(); e6 = []; p6.on('pageerror', lambda e: e6.append(str(e)))
        p6.goto(APP); p6.wait_for_timeout(1500); p6.wait_for_function("() => window.TengelWallet && TengelWallet.on && TengelWallet.total() >= 10000", timeout=20000); p6.wait_for_timeout(1100); gate(p6)
        p6.wait_for_function("() => !!document.getElementById('lgOv')", timeout=20000); p6.wait_for_timeout(400); m0 = p6.evaluate(CLKI); p6.evaluate("() => TengelLogin.close()")
        p6.evaluate("() => __netOn(1)"); p6.goto(APP); p6.wait_for_timeout(1500); gate(p6); p6.wait_for_timeout(3200); m1 = p6.evaluate(CLKI)
        check(m0['hows'][:1] == ['first'] and m0['how'] in ('first', 'ok') and m0['trusted'] == m0['wall'] > m0['real'] and m0['ev'] == [f'login-{m0["wall"]}'] and 'net' in m1['hows'] and m1['trusted'] == m1['real'] < m1['wall'] and abs(m1['lag']) <= 3 and m1['sure']
              and not m1['open'] and m1['ev'] == m0['ev'],
              f'はじめて 入れた とき iPhone の 日付が 5日 進んで いた（{m0["wall"]}：その 日の ボーナス 1回）→ つながると 本当の 時刻（{m1["real"]}）に もどす・進めた ぶんの 日が すぎる まで つぎの ボーナスは ない（{m1["ev"]}・{m0["hows"][:3]} → {m1["hows"][:4]}・ずれ {m1["lag"]}秒・たしかめずみ {m1["sure"]}・窓 {m1["open"]}）')
        p6.evaluate("() => { __netOn(1, Date.UTC(2026, 9, 1) - __real()); }"); bad = p6.evaluate("async () => { const a = TengelClock.now(); const r = await TengelClock.net(); return [r, Math.round((TengelClock.now() - a) / 1000), TengelClock.sure()]; }")
        check(bad[0] is False and abs(bad[1]) <= 3 and bad[2] is True, f'ありえない 時刻（アプリを 出す 前の 日付：2026年10月）の 返事は 受けとらない（時刻は かわらない：{bad}）')
        check(not e6, f'エラー なし {e6[:3]}')
        c6.close()
        check(not e5, f'エラー なし {e5[:3]}')
        c5.close()

        print('■ App Store版')
        c2 = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo'); c2.add_init_script(FAKE); c2.add_init_script(CLOCK + AUTO)
        p2 = c2.new_page(); e2 = []; p2.on('pageerror', lambda e: e2.append(str(e)))
        p2.goto(STORE); p2.wait_for_timeout(1500); s0 = p2.evaluate("() => TengelWallet.total()"); gate(p2)
        p2.wait_for_function("() => !!document.getElementById('lgOv')", timeout=20000); p2.wait_for_timeout(600); s1 = p2.evaluate(INFO)
        st_btn = p2.evaluate("() => !!document.querySelector('#lgOv [data-lg=next]')")
        check(s1['line'] == LINE(0) and s1['total'] == s0 + 500 == 5500 and tiles_ok(s1['tiles'], 0) and not st_btn and s1['gift'] == {'v': 1, 'list': [{'id': f'login-{s1["today"]}', 'c': 2}]},
              f'App Store版（はじめの 5,000P）：スタートの 画面の あと「{s1["line"]}」→ {s1["total"]:,}P・テスト版の ボタンは 出ない')
        r6 = p2.evaluate("async () => { const a = await TengelLogin.next(); const s = JSON.parse(localStorage.getItem('tengel.login')); s.off = 5; localStorage.setItem('tengel.login', JSON.stringify(s)); const b = await TengelLogin.check(); return [a, b, TengelLogin.state().off, TengelWallet.total()]; }")
        check(r6 == [-1, -1, 0, 5500] and p2.evaluate(INFO)['gift'] == s1['gift'], f'App Store版：日付を ずらす しかけ（つぎの 日を ためす・おぼえの 中の ずれ）は 効かない（バトルコインも ふえない）{r6}')
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
        check(p4.evaluate("() => typeof window.TengelClock === 'undefined' && localStorage.getItem('tengel.clock') === null") and p4.evaluate("() => typeof window.TengelLogin === 'undefined' && !document.getElementById('lgOv') && !document.getElementById('lgCss') && localStorage.getItem('tengel.login') === null && localStorage.getItem('tengel.cbgift') === null") and not e4, f'Web版：ログインボーナスは ない（窓も おぼえも ない）・エラー なし {e4[:3]}')
        c4.close()
        b.close()
finally:
    srv.terminate()
print('NG' if fails else 'OK', len(fails), fails)
sys.exit(1 if fails else 0)
