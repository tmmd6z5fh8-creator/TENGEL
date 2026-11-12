# 作戦会議の 入口（判定タブの「レース情報」の カードの 右上の 札）の テスト（第4.160版）
#   まさちゃん 2026/11/12 14:58「作戦会議は、1番左の項目判定のページでも開けるようにして！アイコンは右上に設置して！」
#   ・App Store版（TARGET=app）：判定タブの いちばん 上の カード「レース情報」の 右上に 作戦会議の 札（tc_icon_plan.webp）→ 指で 押すと 判定タブの 上に 作戦会議が 開く
#     （トレーニングセンターは 開かない・開いた まま 表示される・うしろの 判定タブは 動かない・「とじる」で 判定タブに もどる）
#   ・どの 壁紙でも 札は カードの 中・見出しの 字と 下の 行に 重ならない
#   ・トレーニングセンターの 中の 作戦会議とは 同じ もの（予約した レースは どちらからも 見える・行ったり 来たり しても こわれない）
#   ・Web版：札は 出ない（tc_launch.js は アプリ だけ）
#   python3 test_plan_entry.py   （ios/tc_assets/ が ない とき（CI）は 絵なしの 札〈字〉で 同じ ことを 確かめる。壁紙の 絵 ios/kisekae_blobs/ が ない ときは 標準の 見た目 だけ）
import datetime as _dt, json, os, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv_tc'); PORT = 8802; APP = f'http://localhost:{PORT}/APP/'; WEB = f'http://localhost:{PORT}/TENGEL/'
SHOT = os.environ.get('SHOT')          # 画面を 写す フォルダ（見る 用）
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'TENGEL')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, HIST='hist_280.json', DROP=''))
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, HIST='hist_280.json', DROP='', TARGET='app'))
from assets_dir import adir
TCA = adir('tc_assets'); HAVE = os.path.isdir(TCA) and len(os.listdir(TCA)) > 100
BL = os.environ.get('KISEKAE_ASSETS') or os.path.join(W, 'ios', 'kisekae_blobs'); WALL = os.path.isdir(BL) and len(os.listdir(BL)) > 50
pth = os.path.join(SRV, 'APP', 'index.html'); html = open(pth, encoding='utf8').read()
assert "window.__NATIVE = location.protocol === 'tengel:';" in html
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
if HAVE:
    for f in os.listdir(TCA): shutil.copy(os.path.join(TCA, f), os.path.join(SRV, 'APP', f))
else: print('※ トレーニングセンターの 絵と 音（ios/tc_assets）が ない ので、絵なしの 札（字）で 確かめる')
if WALL:
    for f in os.listdir(BL): shutil.copy(os.path.join(BL, f), os.path.join(SRV, 'APP', 'ks_' + f))
else: print('※ 壁紙の 絵（ios/kisekae_blobs）が ない ので、標準の 見た目 だけ')
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c: fails.append(label)


FAKE = open(os.path.join(W, 'test_tc.py'), encoding='utf8').read().split('FAKE = """')[1].split('"""')[0]      # アプリの 窓口の にせもの（test_tc.py と 同じ）
PW, PH, INK = 118, 47, (16 / 500, 30 / 200, 483 / 500, 170 / 200)      # 絵の 大きさ・絵の 中の 札の 場所（tc/tc_launch.js と 同じ）


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


# 札・カード・見出しの 字・下の 行の 場所（画面の 上の ほうへ 寄せてから 測る：上の 帯の 下に 札が 出る）
GEO = """() => { const b = document.getElementById('planBtn'); if (!b) return null; const card = b.parentNode, h = card.querySelector('h2');
  window.scrollTo(0, 0); const c0 = card.getBoundingClientRect(), hd = document.querySelector('header').getBoundingClientRect(); window.scrollTo(0, Math.max(0, c0.top - hd.bottom - 30));
  let nx = h.nextElementSibling; while (nx && !(nx.getBoundingClientRect().height > 0)) nx = nx.nextElementSibling;
  const R = e => { const r = e.getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom]; };
  const g = document.createRange(); g.selectNodeContents(h); const t = g.getBoundingClientRect();
  const im = b.querySelector('img'), tx = b.querySelector('.plt'), r = b.getBoundingClientRect(), cs = getComputedStyle(card);
  const hit = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
  return { btn: R(b), card: R(card), h2: [t.left, t.top, t.right, t.bottom], next: nx ? R(nx) : null, img: im ? [im.naturalWidth, im.naturalHeight] : null, txt: tx ? [tx.textContent].concat(R(tx)) : null,
    padR: parseFloat(cs.paddingRight) + parseFloat(cs.borderRightWidth), hdr: hd.bottom, hit: hit === b || (hit && b.contains(hit)), first: card === document.querySelector('#v-judge .card'),
    label: b.getAttribute('aria-label'), dis: b.disabled, pos: getComputedStyle(card).position }; }"""


def plate(q):          # 見える 札（左・上・右・下）
    l, t = q['btn'][0], q['btn'][1]
    return [l + PW * INK[0], t + PH * INK[1], l + PW * INK[2], t + PH * INK[3]]


def geo_ok(q):         # 札は カードの 中・見出しの 字と 下の 行に 重ならない・右はしは カードの 中身の 右はし・押せる
    if not q: return False, 'ボタンが ない'
    p = plate(q); c = q['card']; w = [round(q['btn'][2] - q['btn'][0], 1), round(q['btn'][3] - q['btn'][1], 1)]
    d = dict(size=w, top=round(p[1] - c[1], 1), right=round((c[2] - q['padR']) - p[2], 1), h2=round(p[0] - q['h2'][2], 1), nxt=round(q['next'][1] - p[3], 1) if q['next'] else None,
             dy=round((p[1] + p[3]) / 2 - (q['h2'][1] + q['h2'][3]) / 2, 1), under=round(p[1] - q['hdr'], 1))
    ok = (w == [PW, PH] and d['top'] >= 4 and abs(d['right']) <= 1.5 and d['h2'] >= 40 and (d['nxt'] is None or d['nxt'] >= 2) and abs(d['dy']) <= 6 and d['under'] > 0
          and q['hit'] and q['first'] and q['pos'] == 'relative' and not q['dis'])
    return ok, d


def swipe(cdp, pg, x, y0, y1):          # 指で なぞる（下から 上へ＝ページを 送る 向き）
    cdp.send('Input.dispatchTouchEvent', dict(type='touchStart', touchPoints=[dict(x=x, y=y0)]))
    for i in range(1, 11): cdp.send('Input.dispatchTouchEvent', dict(type='touchMove', touchPoints=[dict(x=x, y=y0 + (y1 - y0) * i / 10)])); pg.wait_for_timeout(16)
    cdp.send('Input.dispatchTouchEvent', dict(type='touchEnd', touchPoints=[])); pg.wait_for_timeout(450)


def tap_btn(pg):
    r = pg.evaluate("() => { const r = document.getElementById('planBtn').getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }")
    pg.touchscreen.tap(*r)


try:
    print('■ 中身')
    app = open(os.path.join(SRV, 'APP', 'index.html'), encoding='utf8').read(); web = open(os.path.join(SRV, 'TENGEL', 'index.html'), encoding='utf8').read()
    tb = open(os.path.join(SRV, 'APP', 'tc_bundle.js'), encoding='utf8').read()
    check("'planBtn'" in app and 'TCPlanOpen' in app and "'planHost'" in app and 'tc_icon_plan.webp' in app, 'App Store版：判定タブの 作戦会議の 札と 入れ物（planBtn・planHost・TCPlanOpen）が 入って いる')
    check('planBtn' not in web and 'TCPlanOpen' not in web and 'planHost' not in web and 'tc_bundle' not in web, 'Web版：札は 入って いない（かわらない）')
    check('window.TCPlan = TCPlan' in tb and 'planBtn' not in tb, '作戦会議の 本体は 押した ときに 読む 束（tc_bundle.js）の 中')
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'])
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo', has_touch=True, is_mobile=True)
        ctx.add_init_script(FAKE)
        pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        reqs = []; pg.on('request', lambda r: reqs.append(r.url.split('/')[-1]))
        pg.goto(APP); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(600)
        pg.evaluate("() => { const t = document.getElementById('toast'); if (t) t.hidden = true; }")
        cdp = ctx.new_cdp_session(pg)
        print('■ 判定タブの 右上の 札')
        q = pg.evaluate(GEO); ok, d = geo_ok(q)
        check(ok and q['label'] == '作戦会議（押すと ひらくよ）', f'「レース情報」の カードの 右上に 作戦会議の 札（絵 {PW}×{PH}＝見える 札 110×33・押せる 高さ {PH}）：カードの 上から {d["top"]}・右はしは 中身の 右はし（ずれ {d["right"]}）・'
              f'見出しの 字から {d["h2"]}・下の 行まで {d["nxt"]}・見出しの まん中との ずれ {d["dy"]}・上の 帯に かくれない')
        if HAVE: check(q['img'] == [500, 200] and q['txt'] is None, f'札の 絵は トレーニングセンターの 作戦会議と 同じ（tc_icon_plan.webp：{q["img"]}）')
        else: check(q['img'] is None and q['txt'] and q['txt'][0] == '作戦会議' and abs((q['txt'][3] - q['txt'][1]) - 110) <= 1 and abs((q['txt'][4] - q['txt'][2]) - 33) <= 1, f'絵が ない とき：字の 札「作戦会議」（110×33）{q["txt"]}')
        check(pg.evaluate("() => typeof window.TCApp === 'undefined' && typeof window.TCPlan === 'undefined' && !document.getElementById('tcOv') && !document.getElementById('planHost')")
              and 'tc_bundle.js' not in reqs, '押す 前：トレーニングセンターの 束は まだ 読んで いない（判定タブを 開く だけでは 重く ならない）')
        shot(pg, 'plan_btn')
        # ほかの タブでは 出ない
        vis = {}
        for tab in ('win5', 'rec', 'stats', 'set', 'judge'):
            pg.locator(f'.tabbar button[data-tab="{tab}"]').click(); pg.wait_for_timeout(350)
            vis[tab] = pg.evaluate("() => { const r = document.getElementById('planBtn').getBoundingClientRect(); return r.width > 0 && r.height > 0; }")
        check(vis == dict(win5=False, rec=False, stats=False, set=False, judge=True), f'札は 判定タブ だけ（ほかの タブでは 出ない）{vis}')
        if WALL:
            print('■ どの 壁紙でも')
            ids = pg.evaluate("() => TengelKisekae.list().map(t => t.id || t)"); bad = []; worst = dict(top=99, nxt=99, h2=999)
            for tid in ids:
                pg.evaluate("(id) => TengelKisekae.apply(id, false)", tid)
                try: pg.wait_for_function("(id) => TengelKisekae.current() === id && TengelKisekae.loaded()", arg=tid, timeout=8000)
                except Exception: bad.append((tid, '読めない')); continue
                pg.wait_for_timeout(700)
                ok, d = geo_ok(pg.evaluate(GEO))
                if not ok: bad.append((tid, d))
                else: worst = dict(top=min(worst['top'], d['top']), nxt=min(worst['nxt'], d['nxt']), h2=min(worst['h2'], d['h2']))
            check(not bad and len(ids) >= 25, f'{len(ids)}この 壁紙 ぜんぶで 札は カードの 中・見出しの 字と 下の 行に 重ならない（いちばん せまい 所：上 {worst["top"]}・下の 行まで {worst["nxt"]}・見出しの 字から {worst["h2"]}）{bad[:4]}')
            pg.evaluate("(id) => TengelKisekae.apply(id, false)", 'default'); pg.wait_for_timeout(900)
        print('■ 指で 押す → 判定タブの 上に 作戦会議')
        pg.evaluate("() => window.scrollTo(0, 0)"); pg.wait_for_timeout(300)
        pg.evaluate("() => window.scrollTo(0, 10)"); pg.wait_for_timeout(200); sy0 = pg.evaluate('() => window.scrollY')      # ページを 少し 送って おく（札は 上の 帯の 下に 見えた まま）：開いても 位置が かわらない ことを 見る
        tap_btn(pg)
        pg.wait_for_function("() => window.TCPlan && TCPlan.isOpen()", timeout=30000); pg.wait_for_timeout(900)
        td = _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=9)))
        st = pg.evaluate("""() => { const e = document.getElementById('tcPlan'), h = document.getElementById('planHost'), r = e.getBoundingClientRect(), pp = e.querySelector('.pp').getBoundingClientRect();
          return { open: TCPlan.isOpen(), host: e.parentNode.id, tcOv: !!document.getElementById('tcOv'), app: typeof window.TCApp, rect: [r.left, r.top, r.width, r.height], pp: [pp.left, pp.top, pp.width, pp.height],
            z: +getComputedStyle(h).zIndex, pos: getComputedStyle(h).position, date: e.querySelector('.bdt').textContent, sub: e.querySelector('.bsub').textContent, tab: document.querySelector('.tabbar button[aria-selected="true"]').dataset.tab,
            top: (() => { const t = document.elementFromPoint(195, 815); return !!(t && e.contains(t)); })(), dis: document.getElementById('planBtn').disabled, sy: window.scrollY,
            head: (() => { const i = e.querySelector('.ph img'); return i ? i.getAttribute('src') : null; })() }; }""")
        check(st['open'] and st['host'] == 'planHost' and not st['tcOv'] and st['app'] == 'object' and 'tc_bundle.js' in reqs, f'押すと 束を 読んで 作戦会議が 開く・入れ物は #planHost・トレーニングセンターは 開かない（#tcOv なし）{dict(host=st["host"], tcOv=st["tcOv"])}')
        check(st['open'] and st['date'].startswith(f'{td.year}年{td.month}月{td.day}日') and st['sub'] == 'お気に入りレース一覧' and st['head'] == 'tc_icon_plan.webp', f'開いた まま 表示される（押した 指の クリックで 閉じない）・ボード「{st["date"]}」「{st["sub"]}」')
        check(st['rect'] == [0, 0, 390, 844] and st['pos'] == 'fixed' and st['z'] >= 90 and st['top'] and st['tab'] == 'judge' and abs(st['pp'][2] - 374) <= 1 and st['sy'] == sy0 and not st['dis'],
              f'画面 いっぱい（{st["rect"]}）・下の タブと 丸い ボタンの 上に 出る（z {st["z"]}）・うしろは 判定タブの まま・ページの 位置は そのまま（{sy0} → {st["sy"]}）')
        shot(pg, 'plan_open')
        print('■ うしろの 判定タブは 動かない')
        mv = {}
        swipe(cdp, pg, 120, 640, 260); mv['中身'] = pg.evaluate('() => window.scrollY')
        swipe(cdp, pg, 120, 40, 420); mv['見出し'] = pg.evaluate('() => window.scrollY')
        swipe(cdp, pg, 3, 700, 300); mv['まわりの 幕'] = pg.evaluate('() => window.scrollY')
        check(all(v == sy0 for v in mv.values()) and pg.evaluate('() => TCPlan.isOpen()'), f'中身（短くて スクロール しない）・見出し・まわりの 幕を 指で なぞっても うしろの ページは 動かない（{sy0} の まま）{mv}・作戦会議は 開いた まま')
        print('■ 予約・通知（トレーニングセンターを 開かなくても 使える）')
        pg.locator('#tcPlan [data-p=on]').click(); pg.wait_for_timeout(500)
        check(pg.evaluate("() => JSON.parse(localStorage.getItem('tengel.plan')).on === true && window.__notify.auth === 'authorized'"), '通知を オン（iPhone の 許可）')
        later = td + _dt.timedelta(days=1)
        pg.locator('#tcPlan [data-p=add]').click(); pg.wait_for_timeout(300)
        pg.fill('#tcPlan [data-f=name]', 'はなまる特別'); pg.fill('#tcPlan [data-f=time]', '15:40'); pg.fill('#tcPlan [data-f=date]', later.strftime('%Y-%m-%d'))
        pg.fill('#tcPlan [data-f=n]', '14'); pg.fill('#tcPlan [data-f=dist]', '1600'); pg.fill('#tcPlan [data-f=memo]', '本命は 5番')
        pg.locator('#tcPlan [data-p=save]').click(); pg.wait_for_timeout(500)
        P = pg.evaluate("() => JSON.parse(localStorage.getItem('tengel.plan'))")
        check(len(P['races']) == 1 and P['races'][0]['name'] == 'はなまる特別' and P['races'][0]['n'] == 14 and P['races'][0]['dist'] == 1600 and P['races'][0]['memo'] == '本命は 5番', f'レースを 予約（メモも）{P["races"]}')
        pg.locator('#tcPlan [data-p=nt][data-m="20"]').click(); pg.wait_for_timeout(200)
        pg.locator('#tcPlan [data-p=nt][data-m="5"]').click(); pg.wait_for_timeout(800)
        items = pg.evaluate("() => window.__notify.items.filter(i => /^plan-/.test(i.id)).map(i => [i.id.split('-').pop(), i.title, i.body])")
        check(len(items) == 2 and {i[0] for i in items} == {'20', '5'} and all('はなまる特別' in i[2] for i in items), f'20分前・5分前の 通知が 入る {items}')
        shot(pg, 'plan_race')
        # 中身が 長い とき：中身は 指で 送れる・うしろは 動かない
        pg.evaluate("""(d) => { const P = JSON.parse(localStorage.getItem('tengel.plan')); for (let i = 0; i < 7; i++) P.races.push({ id: 'x' + i, date: d, time: '1' + i + ':00', name: 'ならび' + i, n: 12, dist: 1200, venue: '', r: '', memo: '', notify: [] }); localStorage.setItem('tengel.plan', JSON.stringify(P)); }""", later.strftime('%Y-%m-%d'))
        pg.locator('#tcPlan [data-p=close]').click(); pg.wait_for_timeout(300)
        c1 = pg.evaluate("() => { const t = document.elementFromPoint(195, 420), h = document.getElementById('planHost'); return { open: TCPlan.isOpen(), through: !!t && !h.contains(t) && t !== h, hostPE: getComputedStyle(h).pointerEvents, tab: document.querySelector('.tabbar button[aria-selected=\"true\"]').dataset.tab, sy: window.scrollY, dis: document.getElementById('planBtn').disabled }; }")
        check(not c1['open'] and c1['through'] and c1['hostPE'] == 'none' and c1['tab'] == 'judge' and c1['sy'] == sy0 and not c1['dis'], f'「とじる」→ 判定タブに もどる（入れ物は 指を 通す・ページの 位置は そのまま）{c1}')
        swipe(cdp, pg, 120, 640, 400); s1 = pg.evaluate('() => window.scrollY')
        check(s1 > sy0, f'閉じた あとは 判定タブを ふつうに 送れる（{sy0} → {s1}）')
        pg.evaluate("(y) => window.scrollTo(0, y)", sy0); pg.wait_for_timeout(200)
        tap_btn(pg); pg.wait_for_function("() => TCPlan.isOpen()", timeout=10000); pg.wait_for_timeout(700)
        n8 = pg.evaluate("() => { const pb = document.querySelector('#tcPlan .pb'); return [document.querySelectorAll('#tcPlan .rc').length, pb.scrollHeight > pb.clientHeight + 50, pb.scrollTop]; }")
        swipe(cdp, pg, 120, 640, 300)
        n9 = pg.evaluate("() => [document.querySelector('#tcPlan .pb').scrollTop, window.scrollY]")
        for _ in range(6): swipe(cdp, pg, 120, 640, 200)       # いちばん 下まで 送って、さらに なぞる
        n10 = pg.evaluate("() => { const pb = document.querySelector('#tcPlan .pb'); return [Math.round(pb.scrollTop), pb.scrollHeight - pb.clientHeight, window.scrollY]; }")
        check(n8[0] == 8 and n8[1] and n9[0] > 50 and n9[1] == sy0 and abs(n10[0] - n10[1]) <= 2 and n10[2] == sy0,
              f'もう一度 開く（レース {n8[0]}こ：中身が 長い）→ 中身は 指で 送れる（{n8[2]} → {n9[0]:.0f}）・いちばん 下で さらに なぞっても うしろは 動かない（{sy0} の まま）')
        # まわりの 幕を 押すと 閉じる
        pg.touchscreen.tap(3, 420); pg.wait_for_timeout(400)
        check(not pg.evaluate('() => TCPlan.isOpen()'), 'まわりの 幕を 押すと 閉じる')
        if HAVE:
            print('■ トレーニングセンターの 中の 作戦会議と 行ったり 来たり')
            pg.locator('#tcFab .fabi').click()
            pg.wait_for_function("() => window.TCApp && document.querySelector('#tcOv.on') && !document.querySelector('#tcOv .tcld')", timeout=120000); pg.wait_for_timeout(1200)
            pg.locator('#tcOv .tcpl').click(); pg.wait_for_timeout(700)
            t1 = pg.evaluate("() => { const e = document.getElementById('tcPlan'); return { open: TCPlan.isOpen(), host: e.parentNode.id, n: e.querySelectorAll('.rc').length, one: document.querySelectorAll('#tcPlan').length, first: (e.querySelector('.rc .nm') || {}).textContent }; }")
            check(t1['open'] and t1['host'] == 'tcOv' and t1['n'] == 8 and t1['one'] == 1, f'トレーニングセンターの 作戦会議の 札 → 同じ 作戦会議が トレーニングセンターの 中に 開く（入れ物 #{t1["host"]}・レース {t1["n"]}こ・作戦会議は 1つ だけ）')
            pg.locator('#tcPlan [data-p=close]').click(); pg.wait_for_timeout(300)
            pg.locator('#tcOv [data-tc=back]').click(); pg.wait_for_timeout(600)
            tap_btn(pg); pg.wait_for_function("() => TCPlan.isOpen()", timeout=10000); pg.wait_for_timeout(600)
            t2 = pg.evaluate("() => { const e = document.getElementById('tcPlan'); return { open: TCPlan.isOpen(), host: e.parentNode.id, n: e.querySelectorAll('.rc').length, tc: !!document.querySelector('#tcOv.on'), names: Array.from(e.querySelectorAll('.rc .nm')).map(x => x.textContent).includes('はなまる特別') }; }")
            check(t2['open'] and t2['host'] == 'planHost' and t2['n'] == 8 and not t2['tc'] and t2['names'], f'トレーニングセンターを 閉じて、また 判定タブの 札 → 判定タブの 上に 開く（入れ物 #{t2["host"]}・予約した レースも ある）')
            pg.locator('#tcPlan [data-p=close]').click(); pg.wait_for_timeout(300)
        check(not errs, f'エラー なし {errs[:3]}')
        if HAVE:
            print('■ 絵が 読めない とき')
            pg2 = ctx.new_page(); e2 = []; pg2.on('pageerror', lambda e: e2.append(str(e)))
            pg2.route('**/tc_icon_plan.webp', lambda r: r.abort())
            pg2.goto(APP); pg2.wait_for_timeout(1500); gate(pg2); pg2.wait_for_timeout(800)
            q2 = pg2.evaluate(GEO); ok2, d2 = geo_ok(q2)
            check(ok2 and q2['img'] is None and q2['txt'] and q2['txt'][0] == '作戦会議' and abs((q2['txt'][3] - q2['txt'][1]) - 110) <= 1 and abs((q2['txt'][4] - q2['txt'][2]) - 33) <= 1, f'絵が 読めない → 字の 札「作戦会議」（110×33・同じ 場所）{d2}')
            tap_btn(pg2); pg2.wait_for_function("() => window.TCPlan && TCPlan.isOpen()", timeout=30000)
            check(pg2.evaluate("() => document.getElementById('tcPlan').parentNode.id === 'planHost'") and not e2, f'字の 札でも 開く・エラー なし {e2[:3]}')
            pg2.close()
        print('■ Web版')
        pw = ctx.new_page(); e3 = []; pw.on('pageerror', lambda e: e3.append(str(e)))
        pw.goto(WEB); pw.wait_for_timeout(1500); gate(pw); pw.wait_for_timeout(500)
        check(pw.evaluate("() => !document.getElementById('planBtn') && !document.getElementById('planCss') && typeof window.TCPlanOpen === 'undefined' && !!document.querySelector('#v-judge .card h2')") and not e3, f'Web版：判定タブに 札は ない（かわらない）・エラー なし {e3[:3]}')
        b.close()
finally:
    srv.terminate()
print('NG' if fails else 'OK', len(fails), fails)
sys.exit(1 if fails else 0)
