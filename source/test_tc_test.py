# トレーニングセンター：テスト版の 道具箱（第4.154版）の テスト
#   まさちゃん 2026/11/11 20:00「テスト版で、トレーニングセンターの幻の馬と神様馬の出現テストできるようにして！お世話の当選パターン全種類テストできるようにして！」
#   ・テスト版（TENGEL_TEST=1）：上の 帯に「🧪 テスト」→ 道具箱 → 幻の馬・神様馬を 出す／ごはん・おそうじの 当たりを ぜんぶ えらべる／そのほかの 当たり
#   ・App Store版：道具箱は 中身に 入らない・入口も ない・よんでも 何も おきない
#   python3 test_tc_test.py   （ios/tc_assets/ が ある とき だけ 画面の テスト。ない とき（CI）は 中身の 見くらべ だけ）
#   きまり（S.test：次の 1回 だけ）は test_tc_care.js・いつもの トレーニングセンターは test_tc.py
#   第4.165版（まさちゃん 2026/11/13 11:46「トレーニングセンターのルーレット抽選や幻の馬、神様馬のテストができるようにする」）：「えらんだら すぐ PUSH を 出す」の スイッチ（はじめは オン）・
#     「PUSH を すぐ 出す」・お世話トークンを 0こに・トークンの 時計を 5分 進める・設定の「テスト版の道具」から 道具箱を 開く。
#     この テストの 前の 方（第4.154版〜の 流れ：えらんで から 本物の ごはんで 出す）は スイッチを オフに して ためす（SKIP_OFF）・おわりの 方で オンに して ためす
import json, os, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv_tc'); PORT = 8796; APP = f'http://localhost:{PORT}/APP/'; STORE = f'http://localhost:{PORT}/STORE/'
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


def sheet(pg, want=True):             # 道具箱を ひらく／とじる
    if pg.evaluate("() => TCTest.isOpen()") != want: pg.locator('#tcOv [data-tc="test"]').click(); pg.wait_for_timeout(300)


def tool(pg, a, o=None):              # 道具箱を ひらいて、ボタン（data-a・data-o）を 押す
    sheet(pg)
    i = pg.evaluate("([a, o]) => [...document.querySelectorAll('#tct .ttb')].findIndex(b => b.dataset.a === a && (o == null || JSON.stringify(JSON.parse(b.dataset.o || '{}')) === JSON.stringify(o)))", [a, o])
    assert i >= 0, (a, o)
    b = pg.locator('#tct .ttb').nth(i); b.scroll_into_view_if_needed(); b.click(); pg.wait_for_timeout(250)


# 第4.159版：お世話（ごはん・おそうじ）の あとは PUSH が 出る。押す まで「途中」（道具箱は 馬を かえない）・当たりは 押した ときに 出る
PUSH_XY = "() => { const S = TCCare.S, G = TCCare.PUSHG; return S.push && S.push.hideT == null && !S.fxHold && S.lastT >= S.push.lock + 0.05 ? [G.x, G.y] : null; }"


def push(pg):                         # PUSH が 出て いたら 1回 押す（押せたら True）
    q = pg.evaluate(PUSH_XY)
    if not q: return False
    stage_click(pg, q[0], q[1]); pg.wait_for_timeout(250); return True


def free(pg, sec=90):                 # お世話・PUSH・当たりの 演出・馬の 入れかえが おわる まで 待つ（PUSH が 出て いたら 押す：「1個 使う」＝1回で 消える）
    for _ in range(int(sec * 2)):
        if pg.evaluate("() => TCApp.test.info().free && !TCCare.S.feed && !document.querySelector('#tcOv .tcfx').classList.contains('on')"): return True
        push(pg)
        pg.wait_for_timeout(500)
    return False


def awake(pg):                        # 第4.156版：馬は もう ねない（前は 夜に ねて いる 馬を 道具箱の wake で 起こして 待った）。念のため 立って いる ことを 見る
    pg.wait_for_function("() => { const BR = TCCare._hb[1]; return BR.mode !== 'sleep' && !(BR.sl > 0.001); }", timeout=40000)


def feed(pg, item=1):                 # ごはん：0＝エサ・1＝リンゴ・2＝ニンジン
    awake(pg); stage_click(pg, 327, 1494)
    pg.wait_for_function("() => !!TCCare.S.chooser", timeout=20000); pg.wait_for_timeout(700)
    stage_click(pg, 270 + 256 * item, 1262)


def fx_done(pg, sec=90):              # ルーレット・チケットの 演出：出たら ときどき タップして おわる まで
    on = False
    for i in range(int(sec * 2)):
        v = pg.evaluate("() => document.querySelector('#tcOv .tcfx').classList.contains('on')")
        if not v and not on: push(pg)      # 第4.159版：ルーレット・チケットは PUSH を 押した ときに 出る
        if v and not on: on = True; pg.wait_for_timeout(1500); shot(pg, f'tct_fx_{int(time.time()) % 100000}')
        if on and not v: return True
        if on and i % 3 == 2: stage_click(pg, 526, 1000)
        pg.wait_for_timeout(500)
    return False


MSG = "() => document.querySelector('#tcOv .tcmsg').textContent"
WAL = "() => TengelWallet.total() + TengelWallet.hold().total"
try:
    # ---------- 中身の 見くらべ（絵が なくても）----------
    print('■ 中身：テスト版に だけ 道具箱が 入る')
    tb = open(os.path.join(SRV, 'APP', 'tc_bundle.js'), encoding='utf8').read(); sb = open(os.path.join(SRV, 'STORE', 'tc_bundle.js'), encoding='utf8').read()
    ti = open(os.path.join(SRV, 'APP', 'index.html'), encoding='utf8').read(); si = open(os.path.join(SRV, 'STORE', 'index.html'), encoding='utf8').read()
    check('const TCTest' in tb and 'window.TCTest = TCTest' in tb and 'テスト版の道具' in tb and 'window.__TEST=true' in ti, 'テスト版：tc_bundle.js に 道具箱（TCTest）・index.html に テスト版の しるし')
    check('const TCTest' not in sb and 'window.TCTest =' not in sb and 'tct-css' not in sb and '🧪' not in sb and 'テスト版' not in sb and '__TEST=true' not in si,
          f'App Store版：tc_bundle.js に 道具箱は 入らない・index.html に テスト版の しるしも ない（{len(tb) - len(sb)}文字 ちがう）')
    check('testOn()' in sb and "if (!testOn()) return 'off';" in sb, 'App Store版に のこる 入口（TCApp.test）は、道具箱が ない と 何も しない 形')
    if HAVE:
        with sync_playwright() as p:
            b = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'])
            ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo')
            ctx.add_init_script(FAKE)
            ctx.add_init_script("try { if (localStorage.getItem('tengel.tctest.skip') == null) localStorage.setItem('tengel.tctest.skip', '0'); } catch (e) { }")      # SKIP_OFF：前の 方は「えらんだら すぐ PUSH」を オフに（第4.165版）
            pg = ctx.new_page(); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            open_tc(pg, APP)
            print('■ 入口と 道具箱')
            hb = pg.evaluate("""() => { const b = document.querySelector('#tcOv [data-tc="test"]'), h = document.querySelector('#tcOv .tch'), R = e => e.getBoundingClientRect(); if (!b) return null;
              const r = R(b), s = R(document.querySelector('#tcOv .tcsd')), k = R(document.querySelector('#tcOv .tcbk')); return { txt: b.textContent, l: r.left, r: r.right, h: r.height, sl: s.left, kr: k.right, hw: R(h).width }; }""")
            check(hb is not None and hb['txt'] == '🧪 テスト' and hb['l'] > hb['kr'] + 8 and hb['r'] < hb['sl'] and hb['h'] >= 32, f'上の 帯に「🧪 テスト」（「← もどる」と 音の ボタンの 間・ほかの ボタンに 重ならない）{hb}')
            sheet(pg); shot(pg, 'tct_sheet1')
            sh = pg.evaluate("""() => { const r = document.querySelector('#tct'), y = r.querySelector('.tty'), st = document.querySelector('#tcOv .tcst').getBoundingClientRect(), s = r.querySelector('.tth').getBoundingClientRect();
              const bs = [...r.querySelectorAll('.ttb')], by = a => bs.filter(x => x.dataset.a === a).length;
              const rows = [...r.querySelectorAll('.ttr')].filter(q => q.querySelector('.ttl.w')).map(q => { const t = [...q.children].map(e => Math.round(e.getBoundingClientRect().top + e.getBoundingClientRect().height / 2)); return Math.max(...t) - Math.min(...t); });
              return { open: TCTest.isOpen(), secs: [...r.querySelectorAll('.tts')].map(e => e.dataset.sec), n: bs.length, prize: by('prize'), visit: by('visit'), heart: by('heart'), flag: by('flag'), poop: by('poop'),
                zone: bs.filter(x => x.classList.contains('z')).map(x => [x.textContent, JSON.parse(x.dataset.o).z]), zhead: [...r.querySelectorAll('.ttg')].map(e => e.textContent).filter(t => t.includes('特化ゾーン')),
                extra: [by('skip'), by('push'), by('tokens'), by('ahead')], skip: [TCTest.skip, r.querySelector('[data-a=skip]').getAttribute('aria-pressed'), r.querySelector('[data-a=skip]').textContent.slice(0, 1)],
                wide: y.scrollWidth - y.clientWidth, sc: y.scrollHeight > y.clientHeight, inside: s.left >= st.left && s.right <= st.right + 0.5 && s.bottom <= st.bottom + 0.5, rows, minH: Math.min(...bs.map(e => e.getBoundingClientRect().height)),
                font: getComputedStyle(r.querySelector('.ttl')).fontFamily.split(',')[0], now: r.querySelector('[data-now]').innerText }; }""")
            check(sh['open'] and sh['secs'] == ['horse', 'prize', 'other'] and sh['visit'] == 3 and sh['prize'] == 36 and sh['heart'] == 2 and sh['flag'] == 7 and sh['poop'] == 2 and sh['n'] == 58
                  and sh['extra'] == [1, 1, 3, 1] and sh['skip'] == [False, 'false', '☐'],
                  f'道具箱：① 馬 3・② 当たり 36（くじ・はずれ・ポイント 6・ルーレット 6＋6＋6・チケット 3・ポイント特化ゾーン 7）・③ そのほか（{sh["n"]}こ の ボタン）・'
                  f'第4.165版：すぐ PUSH の スイッチ（ここでは オフに して ある {sh["skip"]}）・「PUSH を すぐ 出す」・トークン 25／19／0こ・時計を 5分 進める {sh["extra"]}')
            #   第4.165版（まさちゃん 11/13 12:51「ポイントの特化ゾーンを作る」）：上乗せ できる 回数を えらぶ ボタン 6つ ＋ くじどおり
            zw = [[f'{n}回{"（MAX）" if n == 12 else ""} → {1000 + 2000 * n:,}P', {'k': 'zn', 'n': n}] for n in (0, 1, 3, 6, 11, 12)] + [['くじどおり（1回ごとに 60%）', {'k': 'zn'}]]
            check(sh['zone'] == zw and len(sh['zhead']) == 1 and 'いまの 馬の まま' in sh['zhead'][0], f'道具箱の ポイント特化ゾーン：上乗せ 0・1・3・6・11・12回（MAX 25,000P）と「くじどおり」（{[z[0] for z in sh["zone"]]}）')
            check(sh['wide'] <= 0 and sh['sc'] and sh['inside'] and max(sh['rows']) <= 2 and len(sh['rows']) == 9 and sh['minH'] >= 36 and 'BIZ' in sh['font'],
                  f'フィールドの 中に おさまる・横に はみ出さない・下へ スクロール・ルーレットの 9行は 1行ずつ（ずれ {max(sh["rows"])}px）・ボタンの 高さ {sh["minH"]:.0f}px 以上・字は 本文の 字')
            check('いつもの 馬' in sh['now'] and 'くじ（本番と 同じ 確率）' in sh['now'] and 'トークン' in sh['now'], f'いちばん 上に いまの ようす（{sh["now"]!r}）')
            tab = pg.evaluate("""() => { const t = TCApp._t, pts = t.PRIZES.filter(q => q[1].k === 'pt').map(q => q[1].v).sort((a, b) => a - b), rt = t.PRIZES.filter(q => q[1].k === 'rt').map(q => [q[1].tier].concat(t.RT[q[1].tier]));
              const vis = k => t.PRIZES_VISIT[k].filter(q => q[1].k === 'rt').map(q => [q[1].tier].concat(q[1].v)).sort((a, b) => a[1] - b[1]), srt = a => a.slice().sort((x, y) => x[1] - y[1]);
              return { pts: JSON.stringify(pts) === JSON.stringify(TCTest.PTS), rt: JSON.stringify(srt(rt)) === JSON.stringify(srt(TCTest.RTS.normal)), mab: JSON.stringify(vis('maboroshi')) === JSON.stringify(TCTest.RTS.maboroshi), kami: JSON.stringify(vis('kamisama')) === JSON.stringify(TCTest.RTS.kamisama),
                tk: t.PRIZES.filter(q => q[1].k === 'tk').length, all: t.PRIZES.length, zn: [t.PRIZES, t.PRIZES_VISIT.maboroshi, t.PRIZES_VISIT.kamisama].map(a => a.filter(q => q[1].k === 'zn').length),
                zv: TCTest.ZNS.every(n => TCTest.ZV(n) === t.zoneV(n)) && JSON.stringify(TCTest.ZNS) === '[0,1,3,6,11,12]' && t.ZONE.max === 12 }; }""")
            check(tab['pts'] and tab['rt'] and tab['mab'] and tab['kami'] and tab['tk'] == 1 and tab['all'] == 11 and tab['zn'] == [1, 1, 1] and tab['zv'],
                  f'道具箱の 当たりの 表は 本番の 表（ポイント 6・ルーレット 3・チケット・ポイント特化ゾーン／幻の馬 3・神様馬 3〈どちらも ポイント特化ゾーンも〉）と 同じ 数・特化ゾーンの 合計も 本番と 同じ {tab}')
            for y in (430, 860, 1300):
                pg.evaluate("(y) => { document.querySelector('#tct .tty').scrollTop = y; }", y); pg.wait_for_timeout(150); shot(pg, f'tct_sheet_{y}')
            pg.locator('#tct .ttx').click(); pg.wait_for_timeout(200); c1 = pg.evaluate("() => TCTest.isOpen()")
            sheet(pg); pg.mouse.click(*stage_xy(pg, 526, 60)); pg.wait_for_timeout(200); c2 = pg.evaluate("() => TCTest.isOpen()")
            check(c1 is False and c2 is False, '✕ と 外がわ（暗い 所）で とじる')
            # ひらいて いる 間は 馬の リセットを 待つ（説明書・作戦会議と 同じ）
            free(pg); sheet(pg); pg.evaluate("() => { TCApp._t.force(null); TCApp.state.rs = { n: 5, at: Date.now() - 6 * 60000, el: 0 }; }"); pg.wait_for_timeout(1200)
            h1 = pg.evaluate("() => [TCApp.state.rs.n, TCApp.state.rs.at > 0]"); sheet(pg, False); pg.wait_for_timeout(1500)
            h2 = pg.evaluate("() => [TCApp.state.rs.n, TCApp.state.rs.at > 0]")
            check(h1 == [5, True] and h2 == [0, False], f'道具箱を ひらいて いる 間は 馬の リセットを 待つ → とじると リセット（{h1} → {h2}）')

            print('■ ① 馬を かえる（出現の テスト）')
            free(pg); t0 = time.time(); tool(pg, 'visit', {'k': 'maboroshi'})
            c0 = pg.evaluate("() => TCTest.isOpen()")
            pg.wait_for_function("() => TCApp.state.visit && TCApp.state.visit.kind === 'maboroshi' && TCApp.test.info().free", timeout=90000)
            pg.wait_for_function("() => TCCare.S.ban && TCCare.S.ban.shown", timeout=60000); pg.wait_for_timeout(1200); shot(pg, 'tct_maboroshi')
            v = pg.evaluate("""() => { const st = TCApp.state, [HO, BR] = TCCare._hb; return { kind: st.visit.kind, left: Math.round(TCApp._t.visitLeft(Date.now())), rs: st.rs, field: TCApp._t.fieldName(), ban: TCCare.S.ban.kind, shown: TCCare.S.ban.shown,
              msg: document.querySelector('#tcOv .tcmsg').textContent, stand: !!BR.stand, light: BR.light || '', saved: (JSON.parse(localStorage.getItem('tengel.tc')).visit || {}).kind, vinfo: !!TCCare.S.vinfo }; }""")
            check(c0 is False and v['kind'] == 'maboroshi' and 1770 <= v['left'] <= 1800 and v['rs'] == {'n': 0, 'at': 0, 'el': 0} and v['field'] == 'abyss' and v['ban'] == 'maboroshi' and v['shown'] and '幻の馬が やってきた' in v['msg'] and v['saved'] == 'maboroshi' and v['vinfo'],
                  f'「🌙 幻の馬を 出す」→ 道具箱が とじて、本番と 同じ ように やってくる（フィールド・降臨の バナー・お知らせ・タイムリミット 30分・切り替わる 条件の 札・保存）（{time.time() - t0:.1f}秒・{v["msg"]!r}）')
            tool(pg, 'visit', {'k': 'maboroshi'}); pg.wait_for_timeout(400); m = pg.evaluate(MSG)
            check('もう 幻の馬が' in m and pg.evaluate("() => TCApp.state.visit.kind") == 'maboroshi', f'もう いる 馬を 押した → そのまま（{m!r}）')
            tool(pg, 'visit', {'k': 'kamisama'})
            pg.wait_for_function("() => TCApp.state.visit && TCApp.state.visit.kind === 'kamisama' && TCApp.test.info().free", timeout=90000)
            pg.wait_for_function("() => TCCare.S.ban && TCCare.S.ban.kind === 'kamisama' && TCCare.S.ban.shown", timeout=60000); pg.wait_for_timeout(1200); shot(pg, 'tct_kamisama')
            v = pg.evaluate("() => ({ field: TCApp._t.fieldName(), msg: document.querySelector('#tcOv .tcmsg').textContent, left: Math.round(TCApp._t.visitLeft(Date.now())) })")
            check(v['field'] == 'divine' and '神様馬が やってきた' in v['msg'] and 1770 <= v['left'] <= 1800, f'幻の馬が いる ときに「✨ 神様馬を 出す」→ 神様馬に かわる（タイムリミットは はじめから）（{v}）')
            # お世話の 途中（えらぶ 札が 出て いる）は かえない
            pg.evaluate("() => TCApp.test.prize(null)")      # この ごはんは はずれ（くじで ルーレットが 出ない ように）
            awake(pg); stage_click(pg, 327, 1494); pg.wait_for_function("() => !!TCCare.S.chooser", timeout=20000)
            r = pg.evaluate("async () => [await TCApp.test.visit(null), TCApp.state.visit.kind, await TCApp.test.prize({ k: 'pt', v: 10 }, 'normal'), TCApp.test.info().prize === null]")
            sheet(pg); pg.locator('#tct .ttb[data-a="visit"]').nth(2).click(); pg.wait_for_timeout(400); m = pg.evaluate(MSG)
            check(r[0] == 'busy' and r[1] == 'kamisama' and r[2] == 'busy' and r[3] is True and 'お世話が おわったら' in m and pg.evaluate("() => TCApp.state.visit.kind") == 'kamisama', f'お世話の 途中は 馬を かえない・当たりも かえない（{m!r}）{r}')
            stage_click(pg, 270 + 256, 1262); free(pg)
            tool(pg, 'visit', {'k': None}); pg.wait_for_function("() => !TCApp.state.visit && TCApp.test.info().free", timeout=90000); pg.wait_for_timeout(1500)
            v = pg.evaluate("() => ({ field: TCApp._t.fieldName(), msg: document.querySelector('#tcOv .tcmsg').textContent, rs: TCApp.state.rs, vinfo: TCCare.S.vinfo, stand: !!TCCare._hb[1].stand })")
            check(v['field'] in ('morning', 'evening', 'night') and '帰って いったよ' in v['msg'] and v['rs'] == {'n': 0, 'at': 0, 'el': 0} and v['vinfo'] is None and not v['stand'], f'「いつもの 馬に もどす」→ 帰る（本番と 同じ お知らせ・フィールドも もどる）（{v["msg"]!r}）')

            print('■ ② 次の ごはん・おそうじの 当たり（ぜんぶ）')
            ONE = """async ([z, h]) => { const T = TCApp.test, t = TCApp._t, st = TCApp.state, S = TCCare.S, W = TengelWallet, tot = () => W.total() + W.hold().total; S.high = 0; st.high = 0;
              const r = await T.prize(z, h), set = JSON.stringify(T.info().prize) === JSON.stringify(z), got = t.lottery(), after = T.info().prize === undefined;
              const pend = (JSON.parse(localStorage.getItem('tengel.tc')) || {}).pend || null, w0 = tot(), k0 = st.tickets || 0, v = got ? t.give(got) : 0; await new Promise(q => setTimeout(q, 400));
              return { r, set, got, after, pend: !!(pend && got && pend.id === got.id), v, dw: tot() - w0, dk: (st.tickets || 0) - k0, visit: st.visit ? st.visit.kind : null, left: (JSON.parse(localStorage.getItem('tengel.tc')) || {}).pend || null }; }"""
            bad = []
            cases = [({'k': 'pt', 'v': v}, 'normal', v, 0) for v in (10, 20, 50, 100, 200, 300)]
            cases += [({'k': 'rt', 'tier': tr, 'v': [a, c], 'win': w}, 'normal', (c if w else a), 0) for tr, a, c in (('normal', 800, 1600), ('maboroshi', 1600, 3200), ('kamisama', 3200, 6400)) for w in (0, 1)]
            cases += [({'k': 'tk', 'n': n}, 'normal', 0, n) for n in (1, 2, 3)]
            cases += [({'k': 'zn', 'n': n}, 'normal', 1000 + 2000 * n, 0) for n in (0, 1, 3, 6, 11, 12)]      # 第4.165版：ポイント特化ゾーン（上乗せ n回 → 1,000P ＋ 2,000P × n）
            cases += [({'k': 'rt', 'tier': 'maboroshi', 'v': [a, c], 'win': w}, 'maboroshi', (c if w else a), 0) for a, c in ((800, 1600), (1600, 3200), (3200, 6400)) for w in (0, 1)]
            cases += [({'k': 'rt', 'tier': 'kamisama', 'v': [a, c], 'win': w}, 'kamisama', (c if w else a), 0) for a, c in ((2000, 4000), (5000, 10000), (10000, 20000)) for w in (0, 1)]
            seen = set()
            for z, h, pts, tk in cases:
                q = pg.evaluate(ONE, [z, h]); g = q['got'] or {}
                ok = (q['r'] == 'ok' and q['set'] and q['after'] and q['pend'] and q['left'] is None and g.get('k') == z['k'] and q['v'] == pts and q['dw'] == pts and q['dk'] == tk
                      and q['visit'] == (None if h == 'normal' else h) and (z['k'] != 'rt' or (g.get('win') == z['win'] and [g.get('a'), g.get('b')] == z['v'] and g.get('tier') == z['tier'])) and (z['k'] != 'tk' or g.get('n') == z['n'])
                      and (z['k'] != 'zn' or (g.get('n') == z['n'] and g.get('v') == pts)))
                seen.add(h)
                if not ok: bad.append((z, h, q))
            check(not bad and len(cases) == 33 and seen == {'normal', 'maboroshi', 'kamisama'},
                  f'当たり 33とおり（ポイント 6・ルーレット 3×2・チケット 1〜3枚・ポイント特化ゾーン 6／幻の馬の ルーレット 3×2／神様馬の ルーレット 3×2）：えらんだ 当たりが 次の 抽選で 出て、本番と 同じ わたし方（ポイント・チケットの 数）・1回 だけ・その 当たりが 出る 馬に かわる {bad[:2]}')
            #   ポイント特化ゾーンは 馬を かえない（いまは 神様馬）・「くじどおり」は 上乗せの 回数を 本番の くじ（1回ごとに 60%・12回まで）で 決める
            zq = pg.evaluate("""async () => { const T = TCApp.test, t = TCApp._t, st = TCApp.state, out = [];
              const k0 = st.visit ? st.visit.kind : null, r = await T.prize({ k: 'zn', n: 3 }), g = t.lottery(), k1 = st.visit ? st.visit.kind : null; st.pend = null;
              for (let i = 0; i < 300; i++) { await T.prize({ k: 'zn' }); const z = t.lottery(); st.pend = null; out.push([z.k, z.n, z.v]); } localStorage.setItem('tengel.tc', JSON.stringify(st));      // 当たりは わたさない（数える だけ）
              return { k0, k1, r, g: g && [g.k, g.n, g.v], bad: out.filter(z => z[0] !== 'zn' || !(z[1] >= 0 && z[1] <= 12) || z[2] !== 1000 + 2000 * z[1]).length, n0: out.filter(z => z[1] === 0).length, big: out.filter(z => z[1] >= 3).length, after: T.info().prize === undefined }; }""")
            check(zq['k0'] == zq['k1'] == 'kamisama' and zq['r'] == 'ok' and zq['g'] == ['zn', 3, 7000] and zq['bad'] == 0 and 80 <= zq['n0'] <= 160 and 35 <= zq['big'] <= 100 and zq['after'],
                  f'ポイント特化ゾーンは 馬を かえない（神様馬の まま → 上乗せ 3回 7,000P）・「くじどおり」300回：ぜんぶ 特化ゾーン・合計は 1,000P ＋ 2,000P × 回数・0回 {zq["n0"]}（40%：120 ぐらい）・3回以上 {zq["big"]}（21.6%：65 ぐらい）')
            q = pg.evaluate("""async () => { const T = TCApp.test, t = TCApp._t, S = TCCare.S; const k0 = TCApp.state.visit.kind; const r = await T.prize(null); const set = T.info().prize === null, got = t.lottery(), after = T.info().prize === undefined;
              S.high = 3; await T.prize({ k: 'pt', v: 10 }, 'kamisama'); const g2 = t.lottery(), hi = S.high;      // 高確ゾーンの のこりは 本番と 同じ ように 1つ へる
              await T.prize({ k: 'pt', v: 50 }, 'kamisama'); const r3 = await T.prize(undefined), back = T.info().prize === undefined; S.high = 0; TCApp.state.high = 0; if (g2) t.give(g2);
              return { r, set, got, after, k0, k1: TCApp.state.visit.kind, g2: g2 && g2.v, hi, r3, back }; }""")
            check(q['r'] == 'ok' and q['set'] and q['got'] is None and q['after'] and q['k0'] == q['k1'] == 'kamisama' and q['g2'] == 10 and q['hi'] == 2 and q['r3'] == 'ok' and q['back'],
                  f'「はずれ」は 馬を かえない で 次の 1回が はずれ・高確ゾーンの のこりは 本番と 同じ ように へる・「くじに もどす」で もとの くじ {q}')
            q = pg.evaluate("async () => { const S = TCCare.S; S.stock = 0; const a = TCApp.test.info().stock; const r = await TCApp.test.prize({ k: 'pt', v: 10 }); await TCApp.test.prize(undefined); return [a, r, S.stock, TCApp.state.stock]; }")
            check(q == [0, 'ok', 25, 25], f'お世話トークンが 0 の ときに 当たりを えらぶ → 25こに（ためせる ように）{q}')

            print('■ ② 本物の ごはんで 出る（ポイント・ルーレット・チケット）')
            pg.evaluate("() => TCApp.test.tokens()")
            w0 = pg.evaluate(WAL); tool(pg, 'prize', {'h': 'normal', 'z': {'k': 'pt', 'v': 300}})
            pg.wait_for_function("() => !TCApp.state.visit && TCApp.test.info().free", timeout=90000); pg.wait_for_timeout(500); m = pg.evaluate(MSG); shot(pg, 'tct_msg_prize')
            sheet(pg); now = pg.evaluate("() => document.querySelector('#tct [data-now]').innerText"); sheet(pg, False)
            # 第4.156版（まさちゃん 2026/11/12 04:20「トレーニングセンターの馬の寝転ぶ演出は全部消して！」）：馬は もう ねない ＝ 道具箱の「ねて いる 馬を 起こす」も なくした。
            #   外から ねる 形（mode 'sleep'）を 入れても 立った まま（横に なる しるしは 0）・道具箱の お知らせに「起こすよ」は 出ない
            pg.evaluate("() => { const BR = TCCare._hb[1], t = TCCare.S.lastT; Object.assign(BR, { mode: 'sleep', until: t + 600 }); }")
            pg.wait_for_timeout(500); z0 = pg.evaluate("() => { const BR = TCCare._hb[1]; return [BR.mode === 'sleep', BR.sl || 0, BR.rise || 0, typeof TCApp.test.wake]; }")
            tool(pg, 'prize', {'h': 'normal', 'z': {'k': 'pt', 'v': 300}}); pg.wait_for_timeout(300); m2 = pg.evaluate(MSG)
            check(z0 == [False, 0, 0, 'undefined'] and '300P が 当たる' in m2 and '起こすよ' not in m2, f'馬は ねない：ねる 形を 入れても 立った まま・道具箱の「起こす」は なくした（{z0}・{m2!r}）')
            feed(pg, 1)
            # 第4.159版：ごはんが おわると PUSH が 出る（当たりは まだ）。出て いる 間、道具箱は 馬を かえない（「先に PUSH を 押して」）・いまの 馬の 当たりは えらび直せる
            pg.wait_for_function("() => !!(TCCare.S.push && TCCare.S.push.hideT == null)", timeout=120000); pg.wait_for_timeout(700); shot(pg, 'tct_push')
            pq = pg.evaluate("() => { const i = TCApp.test.info(); return [i.push, i.free, JSON.stringify(i.prize), TengelWallet.total() + TengelWallet.hold().total]; }")
            tool(pg, 'visit', {'k': 'maboroshi'}); pg.wait_for_timeout(300); mb = pg.evaluate(MSG)
            pr = pg.evaluate("async () => [await TCApp.test.prize({ k: 'pt', v: 300 }), !!TCApp.state.visit]")
            check(pq[0] is True and pq[1] is False and json.loads(pq[2]) == {'k': 'pt', 'v': 300} and pq[3] == w0 and '先に PUSH を 押して' in mb and pr == ['ok', False],
                  f'ごはんの あとは PUSH（当たりは まだ：ポイントは そのまま）・PUSH が 出て いる 間は 馬を かえない（{mb!r}）・いまの 馬の 当たりは えらべる {pq} {pr}')
            ok = free(pg, 120); pg.wait_for_timeout(800); w1 = pg.evaluate(WAL)
            ev = pg.evaluate("() => TengelWallet.events().filter(e => /^tc-/.test(e.id)).slice(-1).map(e => [e.amount, e.what])")
            check('いつもの 馬に' in m and '300P が 当たる' in m and '次の PUSH（ごはん・おそうじの あと）：300P' in now.replace('\n', ' ') and ok and w1 - w0 == 300 and ev and 'お世話' in ev[0][1],
                  f'道具箱で「300P」→（神様馬 → いつもの 馬に かわって）ごはん 1回 → PUSH を 押すと 300P（台帳「{ev and ev[0][1]}」・{w0} → {w1}）・道具箱の 上にも 出る')
            check(pg.evaluate("() => TCApp.test.info().prize === undefined"), 'その 次の お世話は いつもの くじ（決めた 当たりは 1回 だけ）')
            w0 = pg.evaluate(WAL); tool(pg, 'prize', {'h': 'kamisama', 'z': {'k': 'rt', 'tier': 'kamisama', 'v': [10000, 20000], 'win': 1}})
            pg.wait_for_function("() => TCApp.state.visit && TCApp.state.visit.kind === 'kamisama' && TCApp.test.info().free", timeout=90000); pg.wait_for_timeout(500); m = pg.evaluate(MSG)
            feed(pg, 1); done = fx_done(pg, 150); free(pg, 60); pg.wait_for_timeout(800); w1 = pg.evaluate(WAL)
            ev = pg.evaluate("() => [...TengelWallet.events().filter(e => /^tc-/.test(e.id)).slice(-1).map(e => [e.amount, e.what]), ['', '']]")
            check('神様馬に' in m and 'ルーレット' in m and '→ 20,000P' in m and done and w1 - w0 == 20000 and ev and 'ルーレット' in ev[0][1],
                  f'道具箱で 神様馬の「10,000P か 20,000P → 20,000P」→ 神様馬が 来て、ごはん 1回 → PUSH で ルーレット → 20,000P（{w0} → {w1}・台帳「{ev and ev[0][1]}」）')
            #   第4.165版：道具箱で「1回 → 3,000P」→（神様馬の まま）ごはん 1回 → PUSH で ポイント特化ゾーン → レバーを 2回 タップ（1回め 上乗せ・2回め 失敗）→ 3,000P
            w0 = pg.evaluate(WAL); tool(pg, 'prize', {'z': {'k': 'zn', 'n': 1}}); pg.wait_for_timeout(400); m = pg.evaluate(MSG); zk = pg.evaluate("() => TCApp.state.visit && TCApp.state.visit.kind")
            pg.wait_for_function("() => TCApp.test.info().free", timeout=90000)
            feed(pg, 1); done = fx_done(pg, 150); free(pg, 60); pg.wait_for_timeout(800); w1 = pg.evaluate(WAL)
            ev = pg.evaluate("() => [...TengelWallet.events().filter(e => /^tc-/.test(e.id)).slice(-1).map(e => [e.amount, e.what]), ['', '']]")
            check('ポイント特化ゾーン' in m and '上乗せ 1回' in m and '→ 3,000P' in m and 'かわったよ' not in m and zk == 'kamisama' and done and w1 - w0 == 3000 and 'ポイント特化ゾーン' in ev[0][1],      # 台帳の 1件の 数は 見ない（上限を こえた ぶんは あずかりポイントに 入る：合計で 見る）
                  f'道具箱で 特化ゾーン「1回 → 3,000P」→ 馬は そのまま（{zk}）・ごはん 1回 → PUSH で ポイント特化ゾーン → レバーを タップ → 3,000P（{w0} → {w1}・台帳「{ev[0][1]}」）')
            k0 = pg.evaluate("TCInfo.tickets()"); tool(pg, 'prize', {'h': 'normal', 'z': {'k': 'tk', 'n': 2}})
            pg.wait_for_function("() => !TCApp.state.visit && TCApp.test.info().free", timeout=90000); pg.wait_for_timeout(400)
            feed(pg, 1); done = fx_done(pg, 150); free(pg, 60); pg.wait_for_timeout(600); k1 = pg.evaluate("TCInfo.tickets()")
            check(done and k1 - k0 == 2 and pg.evaluate("() => document.querySelectorAll('#tcOv .tcpc').length") == 0, f'道具箱で「チケット 2枚」→ ごはん 1回 → PUSH で プチュン → チケットの 演出 → 2枚（{k0} → {k1}）・プチュンの 幕は 片付いて いる')
            pg.wait_for_timeout(1500); bn = pg.evaluate("() => { const B = TCCare.S.ban; return [!!B, !!(B && B.hideT == null && B.showT != null), TCCare.vinfoBox()]; }"); shot(pg, 'tct_after_ticket')
            check(bn[1] is False and bn[2] is None, f'神様馬が 帰った あとの チケットの 演出：おわっても 神様馬の 降臨の バナーは また 出ない（バグ直し：前は 出て 残って いた）{bn[:2]}')

            print('■ ③ そのほかの 当たり・めずらしい 動き')
            pg.evaluate("() => { TCCare.S.stock = 3; }"); tool(pg, 'tokens'); pg.wait_for_timeout(300)
            q = pg.evaluate("() => [TCCare.S.stock, TCApp.state.stock, document.querySelector('#tcOv .tcmsg').textContent]")
            check(q[0] == 25 and q[1] == 25 and '25こに' in q[2], f'「お世話トークンを 25こに」{q}')
            # 第4.159版（まさちゃん 11/12 13:27）：ハートの 抽選は トークンが 20こ未満の とき だけ → 道具箱に「19こに」（すぐ 抽選を ためす 用）・ハートの 道具は 20こ以上の とき そう 知らせる
            tool(pg, 'heart', {'win': False}); pg.wait_for_timeout(250); mh = pg.evaluate(MSG); pg.evaluate("() => { const S = TCCare.S; S.heart = S.heartShow = 0; TCApp.state.heart = 0; if (S.test) delete S.test.win; }")
            tool(pg, 'tokens', {'n': 19}); pg.wait_for_timeout(300); q19 = pg.evaluate("() => [TCCare.S.stock, TCApp.state.stock, document.querySelector('#tcOv .tcmsg').textContent, JSON.parse(localStorage.getItem('tengel.tc')).stock]")
            check('20こ以上' in mh and '20こを 切ってから' in mh and q19[0] == 19 and q19[1] == 19 and q19[3] == 19 and '19こに' in q19[2], f'「お世話トークンを 19こに」（{q19[:2]}）・ハートの 道具は トークンが 20こ以上の とき「抽選は 20こを 切ってから」と 知らせる')
            tool(pg, 'tokens'); pg.wait_for_timeout(300)
            tool(pg, 'high'); pg.wait_for_timeout(300); q = pg.evaluate("() => [TCCare.S.high, TCApp.state.high, TCCare.S.fx.some(f => f.k === 'luck')]")
            check(q == [5, 5, True], f'「高確ゾーン」→ お世話 5回（「運がついた！」の 演出も）{q}')
            pg.evaluate("() => { TCCare.S.high = 0; TCApp.state.high = 0; }")
            # 呼ぶ
            for k, nm in (('turn', '振り向く'), ('come', '近づいてくる'), ('amae', '甘える')):
                free(pg); pg.evaluate("() => { const S = TCCare.S; S.callN = 0; S.callCoolUntil = -1e9; }"); tool(pg, 'flag', {'k': 'call', 'v': k}); pg.wait_for_timeout(200); m = pg.evaluate(MSG)
                awake(pg); stage_click(pg, 725, 1494); pg.wait_for_timeout(400); q = pg.evaluate("() => [TCCare.S.callKind, TCCare.S.mode, JSON.stringify(TCCare.S.test || {})]")
                check(nm in m and q[0] == k and q[1] == 'call' and 'call' not in q[2], f'呼ぶ：「{nm}」を えらぶ → 次の 呼ぶは {k}（1回 だけ）')
            free(pg)
            # ごはん：金のニンジン・おかわりの目
            pg.evaluate("() => { const S = TCCare.S; S.got = []; S.heart = S.heartShow = 2; TCApp.state.heart = 2; }")
            pg.evaluate("() => TCApp.test.prize(null)")      # この ごはんは はずれ
            tool(pg, 'flag', {'k': 'gold', 'v': True}); m = pg.evaluate(MSG); tool(pg, 'flag', {'k': 'beg', 'v': True}); pg.wait_for_timeout(200)
            sheet(pg); now = pg.evaluate("() => document.querySelector('#tct [data-now]').innerText"); sheet(pg, False)
            feed(pg, 2); pg.wait_for_function("() => TCCare.S.feed && TCCare.S.phase === 'feed'", timeout=30000); g = pg.evaluate("() => TCCare.S.feed.gold"); pg.wait_for_timeout(1500); shot(pg, 'tct_gold_carrot')
            pg.wait_for_function("() => TCCare.S.phase === 'beg' || (TCCare.S.phase === 'idle' && !TCCare.S.feed)", timeout=60000); bg = pg.evaluate("() => TCCare.S.phase"); free(pg, 60); pg.wait_for_timeout(1200)
            q = pg.evaluate("() => [TCCare.S.heart, JSON.stringify(TCCare.S.test || {})]")
            check('金のニンジン' in m and '金のニンジン' in now and 'おかわりの目' in now and g is True and bg == 'beg' and q[0] == 5 and q[1] == '{}', f'「金のニンジン」「おかわりの目」→ 次の ニンジンは 金（なかよし ＋3：2 → {q[0]}）・食べた あと おかわりの目（どちらも 1回 だけ）')
            # 撫でる：ハートの 抽選（当たり → ぴょん！・トークン ＋5）
            pg.evaluate("() => { TCCare.S.stock = 7; TCApp.state.stock = 7; TCApp.state.stockAt = Date.now() + 7200000; }"); tool(pg, 'heart', {'win': True}); pg.wait_for_timeout(250); m = pg.evaluate(MSG)      # （10分ごとに 5つ たまる：この 確かめの 間に たまらない ように 数えはじめを 先に）
            q0 = pg.evaluate("() => [TCCare.S.heart, TCCare.S.heartShow, TCApp.state.heart, TCCare.S.test && TCCare.S.test.win, TCCare.S.got.length]")
            awake(pg); stage_click(pg, 128, 1494); pg.wait_for_function("() => TCCare.S.phase === 'pet'", timeout=30000); pg.wait_for_timeout(700)
            PTS = """() => { const [HO] = TCCare._hb, z = TCCare.view(), r = document.querySelector('#tcOv .tcst').getBoundingClientRect();
              return ['poll', 'withers'].map(n => { const p = TCHorse.where(HO, n); return [r.left + ((p[0] - z.cx) * z.z + 526) / 1052 * r.width, r.top + ((p[1] - z.cy) * z.z + 828.5) / 1657 * r.height]; }); }"""
            for i in range(3):
                if pg.evaluate("() => TCCare.S.heart >= 10"): break
                a, c = pg.evaluate(PTS); pg.mouse.move(a[0], a[1]); pg.mouse.down(); pg.mouse.move(c[0], c[1], steps=10); pg.mouse.up(); pg.wait_for_timeout(250)
            ok = True
            try: pg.wait_for_function("() => TCCare.S.lot && TCCare.S.lot.win === true", timeout=40000)
            except Exception: ok = False
            pg.wait_for_timeout(2600); shot(pg, 'tct_heart_win')
            free(pg, 60); pg.wait_for_timeout(600); q1 = pg.evaluate("() => [TCCare.S.stock, TCCare.S.heart, JSON.stringify(TCCare.S.test || {})]")
            check('ハートを 9こに' in m and 'ぴょん！' in m and q0 == [9, 9, 9, True, 0] and ok and q1 == [12, 0, '{}'], f'「当たり → ぴょん！」→ ハート 9こ・1回 なでると 抽選は 当たり（お世話トークン 7 → {q1[0]}）{q0}')
            tool(pg, 'heart', {'win': False}); tool(pg, 'flag', {'k': 'rare', 'v': True}); tool(pg, 'flag', {'k': 'nibble', 'v': True}); pg.wait_for_timeout(200)
            q = pg.evaluate("() => [TCCare.S.heart, JSON.stringify(TCCare.S.test)]")
            check(q[0] == 9 and json.loads(q[1]) == {'win': False, 'rare': True, 'nibble': True}, f'「ハズレ → ふぅ〜」「首を かしげる」「ほうきを かじる」も えらべる（動きの きまりは test_tc_care.js）{q[1]}')
            pg.evaluate("() => { const S = TCCare.S; S.test = null; S.heart = S.heartShow = 0; }")
            # おそうじ：ゴミ・うんち・金のうんち
            free(pg); pg.evaluate("() => { const st = TCApp.state, BR = TCCare._hb[1]; st.trash = []; BR.trash = []; st.trashAt = Date.now() + 9e5; BR.poops = []; st.poops = []; }"); pg.wait_for_timeout(400)
            tool(pg, 'trash'); pg.wait_for_timeout(500); q = pg.evaluate("() => [TCApp.state.trash.length, TCCare._hb[1].trash.length, document.querySelector('#tcOv .tcmsg').textContent]")
            tool(pg, 'trash'); pg.wait_for_timeout(300); m2 = pg.evaluate(MSG)
            check(q[0] == 5 and q[1] == 5 and 'ゴミが 出たよ' in q[2] and 'ゴミは もう' in m2 and pg.evaluate("() => TCApp.state.trash.length") == 5, f'「ゴミを 出す」→ 5か所（本番と 同じ お知らせ）・もう 出て いる ときは そのまま（{m2!r}）')
            tool(pg, 'poop', {'gold': True}); m = pg.evaluate(MSG)
            okp = True
            try: pg.wait_for_function("() => (TCCare._hb[1].poops || []).some(q => q.gold === true)", timeout=60000)
            except Exception: okp = False
            pg.wait_for_timeout(800); shot(pg, 'tct_gold_poop')
            q = pg.evaluate("() => [TCCare._hb[1].poops.length, TCApp.test.info().gold, TCApp.state.poops.map(p => p.gold)]")
            check('金のうんち' in m and okp and q[0] >= 1 and q[1] is False and q[2][0] is True, f'「金のうんちを させる」→ 馬が うんちを して、それが 金のうんち（1回 だけ）{q}')
            n0 = q[0]; tool(pg, 'poop', {'gold': False})
            try: pg.wait_for_function("(n) => (TCCare._hb[1].poops || []).length > n && TCApp.state.poops.length > n", arg=n0, timeout=60000)
            except Exception: pass
            q = pg.evaluate("() => TCApp.state.poops.map(p => p.gold)")
            check(len(q) > n0 and q[0] is True, f'「うんちを させる」→ もう 1つ（金か どうかは いつもの くじ）{q}')
            r = pg.evaluate("async () => { await TCApp.test.visit('maboroshi'); return [TCApp.test.poop(true), TCApp.test.info().gold]; }")
            check(r == ['visit', False], f'幻の馬・神様馬は うんちを しない（「いつもの 馬に もどしてね」）{r}')
            check(not errs, f'エラー なし {errs[:3]}')
            # 閉じて ひらき直しても、決めた 当たりは のこる（アプリを 閉じる まで）・馬も そのまま
            pg.evaluate("async () => { await TCApp.test.prize({ k: 'pt', v: 100 }, 'maboroshi'); }"); pg.locator('#tcOv [data-tc="back"]').click(); pg.wait_for_timeout(500)
            pg.locator('#tcFab .fabi').click(); pg.wait_for_function("() => document.querySelector('#tcOv.on')", timeout=60000); pg.wait_for_timeout(1500)
            q = pg.evaluate("() => [TCApp.test.info().prize, TCApp.state.visit && TCApp.state.visit.kind, TCTest.isOpen()]")
            check(q[0] == {'k': 'pt', 'v': 100} and q[1] == 'maboroshi' and q[2] is False, f'「← もどる」→ ひらき直し：決めた 当たりと 馬は そのまま {q}')

            print('■ 第4.165版：すぐ PUSH を 出す・トークンの 道具・設定から 開く')
            check("localStorage.getItem(SKIP_KEY) !== '0'" in tb and 'tengel.tctest.skip' in tb, '「えらんだら すぐ PUSH を 出す」は はじめは オン（端末に「0」と おぼえて いる とき だけ オフ）')
            pg.evaluate("async () => { await TCApp.test.prize(undefined); await TCApp.test.visit(null); }"); free(pg); pg.wait_for_timeout(600)
            pg.evaluate("() => { const st = TCApp.state, S = TCCare.S; st.stock = 6; S.stock = S.stockShow = 6; st.stockAt = Date.now() + 7200000; S.high = 0; st.high = 0; }")
            # スイッチを オンに（道具箱は 閉じない・端末に おぼえる）
            sheet(pg); sw = pg.locator('#tct [data-a=skip]'); sw.scroll_into_view_if_needed(); sw.click(); pg.wait_for_timeout(200)
            q = pg.evaluate("() => [TCTest.isOpen(), TCTest.skip, document.querySelector('#tct [data-a=skip]').getAttribute('aria-pressed'), document.querySelector('#tct [data-a=skip]').textContent.slice(0, 1), localStorage.getItem('tengel.tctest.skip')]")
            check(q == [True, True, 'true', '☑', '1'], f'スイッチを 押す → オン（道具箱は 開いた まま・端末に おぼえる）{q}')
            # はずれ：えらぶと PUSH が すぐ 出る（ごはん・おそうじは しない）→ 押すと はずれ（トークン −1・お世話 1回）
            c0 = pg.evaluate("() => [TCApp.state.cares, TCApp.state.stock]"); tool(pg, 'prize', {'z': None}); pg.wait_for_timeout(900); m = pg.evaluate(MSG)
            p0 = pg.evaluate("() => { const S = TCCare.S; return [!!(S.push && S.push.hideT == null), S.phase, !!S.feed, TCApp.test.info().prize === null, TCTest.isOpen()]; }")
            pg.evaluate("() => { const S = TCApp._snd; window.__seT = []; if (!S.__wt) { S.__wt = 1; const o = S.se.bind(S); S.se = (n, g, l) => { window.__seT.push(String(n).replace('tc_se_', '').replace('.m4a', '')); return o(n, g, l); }; } }")
            okp = push(pg); pg.wait_for_timeout(700)
            p1 = pg.evaluate("() => [TCApp.state.cares, TCApp.state.stock, TCApp.test.info().prize === undefined, (window.__seT || []).slice()]")
            check('PUSH を 押すと' in m and 'はずれ' in m and p0 == [True, 'idle', False, True, False] and okp and p1[0] == c0[0] + 1 and p1[1] == c0[1] - 1 and p1[2] and 'pfo' in p1[3],
                  f'オン：「はずれ」を えらぶ → お世話を しなくても PUSH が すぐ 出る → 押すと はずれ（プフォ・トークン {c0[1]} → {p1[1]}・お世話 ＋1）（{m!r}・{p0}・{okp}・{p1[2:]}）')
            free(pg)
            # ルーレット：えらぶ → PUSH → 押す → キュインキュイーン → ルーレット → ポイント
            w0 = pg.evaluate(WAL); tool(pg, 'prize', {'h': 'normal', 'z': {'k': 'rt', 'tier': 'normal', 'v': [800, 1600], 'win': 1}}); pg.wait_for_timeout(900); m = pg.evaluate(MSG)
            p0 = pg.evaluate("() => { const S = TCCare.S; return [!!(S.push && S.push.hideT == null), !!S.feed]; }")
            done = fx_done(pg, 150); free(pg, 60); pg.wait_for_timeout(800); w1 = pg.evaluate(WAL)
            check('PUSH を 押すと' in m and 'ルーレット' in m and '→ 1,600P' in m and p0 == [True, False] and done and w1 - w0 == 1600,
                  f'オン：ルーレット「800P か 1,600P → 1,600P」を えらぶ → PUSH が すぐ 出る → 押すと ルーレット → 1,600P（{w0} → {w1}）')
            # 馬が かわる 当たり（幻の馬の ルーレット）：馬が 来て から PUSH
            w0 = pg.evaluate(WAL); tool(pg, 'prize', {'h': 'maboroshi', 'z': {'k': 'rt', 'tier': 'maboroshi', 'v': [800, 1600], 'win': 0}})
            pg.wait_for_function("() => TCApp.state.visit && TCApp.state.visit.kind === 'maboroshi' && !!(TCCare.S.push && TCCare.S.push.hideT == null)", timeout=90000); pg.wait_for_timeout(600); m = pg.evaluate(MSG)
            done = fx_done(pg, 150); free(pg, 60); pg.wait_for_timeout(800); w1 = pg.evaluate(WAL)
            check('幻の馬に' in m and 'PUSH を 押すと' in m and done and w1 - w0 == 800, f'オン：幻の馬の ルーレットを えらぶ → 幻の馬が 来て PUSH が 出る → 押すと ルーレット → 800P（{w0} → {w1}）')
            pg.evaluate("async () => { await TCApp.test.visit(null); }"); free(pg); pg.wait_for_timeout(500)
            # 「PUSH を すぐ 出す」：出る・もう 出て いる ときは そのまま
            pg.evaluate("() => TCApp.test.prize(null)"); tool(pg, 'push'); pg.wait_for_timeout(700); m1 = pg.evaluate(MSG); a1 = pg.evaluate("() => !!(TCCare.S.push && TCCare.S.push.hideT == null)")
            tool(pg, 'push'); pg.wait_for_timeout(300); m2 = pg.evaluate(MSG); push(pg); free(pg)
            check('PUSH を 出したよ' in m1 and a1 and 'もう' in m2, f'「PUSH を すぐ 出す」→ PUSH が 出る・もう 出て いる ときは そのまま（{m1!r}・{m2!r}）')
            # トークン：0こに・時計を 5分 進める（＋5）・最大の ときは そのまま
            tool(pg, 'tokens', {'n': 0}); pg.wait_for_timeout(300); t0_ = pg.evaluate("() => [TCCare.S.stock, TCApp.state.stock, document.querySelector('#tcOv .tcmsg').textContent]")
            pg.evaluate("() => { TCApp.state.stockAt = Date.now(); }"); tool(pg, 'ahead'); pg.wait_for_timeout(700); t1_ = pg.evaluate("() => [TCCare.S.stock, TCApp.state.stock, document.querySelector('#tcOv .tcmsg').textContent]")
            tool(pg, 'ahead'); pg.wait_for_timeout(700); t2_ = pg.evaluate("() => TCApp.state.stock")
            tool(pg, 'tokens'); pg.wait_for_timeout(300); tool(pg, 'ahead'); pg.wait_for_timeout(500); t3_ = pg.evaluate("() => [TCApp.state.stock, document.querySelector('#tcOv .tcmsg').textContent]")
            check(t0_[:2] == [0, 0] and '0こに' in t0_[2] and t1_[:2] == [5, 5] and '5分 進めたよ' in t1_[2] and t2_ == 10 and t3_[0] == 25 and 'もう 最大' in t3_[1],
                  f'「お世話トークンを 0こに」→ 0・「トークンの 時計を 5分 進める」→ ＋5 ずつ（0 → {t1_[0]} → {t2_}）・最大の ときは「もう 最大だよ」（{t3_[1]!r}）')
            # 設定の「テスト版の道具」から：トレーニングセンターを 開いて 道具箱を 出す
            pg.locator('#tcOv [data-tc="back"]').click(); pg.wait_for_timeout(500)
            pg.evaluate("() => { document.querySelector('.tabbar [data-tab=set]').click(); }"); pg.wait_for_timeout(600)
            tb_ = pg.locator('#setTest [data-test=tcopen]'); n_tb = tb_.count()
            if n_tb: tb_.scroll_into_view_if_needed(); tb_.click()
            try: pg.wait_for_function("() => document.querySelector('#tcOv.on') && window.TCTest && TCTest.isOpen()", timeout=60000); o1 = True
            except Exception: o1 = False
            hint = pg.evaluate("() => (document.querySelector('#testTcHint') || {}).textContent || ''")
            check(n_tb == 1 and o1 and 'ルーレット' in hint and 'ノーマルど的中' not in pg.evaluate("() => document.querySelector('#setTest').textContent"),
                  f'設定の「テスト版の道具」に「トレーニングセンターの テスト道具を ひらく」→ トレーニングセンターが 開いて 道具箱が 出る（{o1}）・的中ボタンの 道具に「ノーマルど的中」は ない')
            sheet(pg, False)
            check(not errs, f'エラー なし（第4.165版の 道具）{errs[:3]}')
            ctx.close()

            print('■ App Store版：入口が ない・よんでも 何も おきない')
            c2 = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo'); c2.add_init_script(FAKE)
            p2 = c2.new_page(); e2 = []; p2.on('pageerror', lambda e: e2.append(str(e)))
            open_tc(p2, STORE)
            q = p2.evaluate("""async () => { const T = TCApp.test, st = TCApp.state, S = TCCare.S, s0 = S.stock, h0 = S.heart;
              const r = [await T.visit('kamisama'), await T.prize({ k: 'pt', v: 300 }, 'normal'), T.tokens(), T.heart(true), T.flag('gold', true), T.high(), T.trash(), T.poop(true), T.ahead(5), T.push()];
              const z = []; for (let i = 0; i < 40; i++) z.push(TCApp._t.draw());
              return { btn: document.querySelectorAll('#tcOv [data-tc="test"]').length, test: typeof window.TCTest, flag: window.__TEST === undefined, r, visit: st.visit, prize: T.info().prize === undefined, gold: T.info().gold, st: S.test, same: S.stock === s0 && S.heart === h0, high: S.high,
                tag: !!document.querySelector('#testTag'), card: !!document.querySelector('#setTest'), n300: z.filter(q => q && q.k === 'pt' && q.v === 300).length }; }""")
            check(q['btn'] == 0 and q['test'] == 'undefined' and q['flag'] and not q['tag'] and not q['card'], f'App Store版：上の 帯に「🧪 テスト」が ない・道具箱（TCTest）も テスト版の しるしも ない')
            check(q['r'] == ['off'] * 10 and q['visit'] is None and q['prize'] and q['gold'] is False and q['st'] is None and q['same'] and q['high'] == 0 and q['n300'] <= 3,
                  f'App Store版：入口を よんでも 何も おきない（馬・当たり・トークン・ハート・高確ゾーン・ゴミ・うんち・時計を 進める・PUSH を 出す：どれも「off」）{q["r"]}')
            check(not e2, f'エラー なし {e2[:3]}')
            b.close()
finally:
    srv.terminate()
print('NG' if fails else 'OK', len(fails), fails)
sys.exit(1 if fails else 0)
