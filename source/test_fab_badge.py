# 第4.221版の テスト：右下の 丸い ボタンの 数と 🔔・作戦会議の 行き先の 札・画面の 上の データの 札・壁紙の 組
#   まさちゃん 2026/11/25 12:07「・トレーニングセンターのアイコンにお世話トークンの数が分かるように表示することって可能？ ・調査隊切符も同じようにしてほしい！
#     ・推し馬からも作戦会議に飛べるようにして！時間がやりたいレースの通知時間が来たら、推し馬のアイコンのところにも、通知が来てることが分かるようにして！」
#   12:11「壁紙のところ、無課金のポイントでGETできる組は、定番じゃなくてポイント壁紙カスタムにして、項目ごとに分けずに並べて！」
#   12:13「テンゲルデータのみは、記録数載せなくていい！他の解放したマザーデータは全て表示して！」（答え「使っているデータだけ」）
#   ・トレーニングセンターの 丸：今の お世話トークンの 数（tc_app.js の accrue と 同じ 数え方：5分ごとに 5個・25個 まで・はじめは 5個・数が かわる 時刻に 書き直す）
#   ・TENGERカードバトルの 丸：今の 調査隊切符の 枚数（cb_app.js の qtNow と 同じ：30分で 1枚・15枚 まで・はじめは 15枚）・解放 して いない（🔒）ときは 出さない
#   ・推し馬の 丸：通知が オンで、予約した レースの 選んだ お知らせの 時刻が 来て から 発走 まで 🔔（作戦会議を 開いたら 消える）。🔔 の ときに 押すと 予約した レースの 方が 開く
#   ・作戦会議：行き先の 札（📋 作戦会議／🐴 推し馬）は 見出しの すぐ 下に 止まる・見て いる 方の 色・まもなく 発走の レースに「🔔 まもなく発走」
#   ・データの 札（#dbpill）：テンゲルデータは 名前 だけ・マザーデータは 走数と 記録数も
#   ・着せ替え：壁紙パック・ポイント壁紙カスタム（17：組に 分けない）・帯 の 3つ
#   python3 test_fab_badge.py   （SHOT=<フォルダ> で 画面を 写す）
import json, os, re, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv_fb'); PORT = 8783; APP = f'http://localhost:{PORT}/APP/'
SHOT = os.environ.get('SHOT')
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, TARGET='app'))
from assets_dir import adir
from toys_for_test import open_toys
pth = os.path.join(SRV, 'APP', 'index.html'); html = open(pth, encoding='utf8').read()
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c: fails.append(label)


print('■ 作った index.html（App Store版）')
check("motherName() : 'テンゲルデータ'}${st.canWrite ? '' : '（閲覧のみ）'}`" in html and "'テンゲルデータ'}・記録" not in html and "走・記録 ${st.bets.size}件" in html,
      'データの 札：テンゲルデータは 名前 だけ（「・記録 ○件」を 外す）・マザーデータは「○走・記録 ○件」の まま')
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
ICONS = [('tc_assets', ('tc_icon_tc.webp', 'tc_icon_oshi.webp', 'tc_icon_plan.webp', 'tc_icon_kise2.webp')), ('fig_assets', ('fg_icon.webp',))]
for d, fs in ICONS:
    try: a = adir(d)
    except Exception: a = None
    for f in fs:
        if a and os.path.exists(os.path.join(a, f)): shutil.copy(os.path.join(a, f), os.path.join(SRV, 'APP', f))
for f in ('cb_icon.webp',):
    a = os.path.join(W, 'ios', 'cb_assets', f)
    if os.path.exists(a): shutil.copy(a, os.path.join(SRV, 'APP', f))
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
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


def shot(pg, name, clip=None):
    if SHOT: os.makedirs(SHOT, exist_ok=True); pg.screenshot(path=os.path.join(SHOT, name + '.png'), clip=clip)


# 丸の 右上の 札（見えて いる もの）
BADGE = """id => { const b = document.getElementById(id); if (!b) return null; const i = b.querySelector('.fabi'), m = i && [...i.querySelectorAll('.fabc, .fabb')].find(e => !e.hidden);
  const al = b.getAttribute('aria-label'); if (!m) return { t: null, al };
  const r = m.getBoundingClientRect(), f = i.getBoundingClientRect(), cs = getComputedStyle(m);
  return { t: m.textContent, cls: m.className, al, ah: m.getAttribute('aria-hidden'), fs: Math.round(parseFloat(cs.fontSize) * 10) / 10, h: Math.round(r.height), w: Math.round(r.width),
    corner: r.top < f.top + f.height * 0.3 && r.bottom > f.top && r.right > f.right - f.width * 0.3, inView: r.left >= 0 && r.right <= innerWidth && r.top >= 0, pe: cs.pointerEvents }; }"""
SETTC = """o => { localStorage.setItem('tengel.tc', JSON.stringify(Object.assign({ v: 1 }, o.s, { stockAt: Date.now() + o.at * 60000 }, o.seen != null ? { seen: Date.now() + o.seen * 60000 } : {}))); document.dispatchEvent(new CustomEvent('tengel:tc')); }"""
SETQT = """o => { const s = Object.assign(JSON.parse(localStorage.getItem('tengel.cb') || '{}'), { v: 1 }); if (o.n == null) delete s.qt; else s.qt = { n: o.n, at: Date.now() + o.at * 60000 }; localStorage.setItem('tengel.cb', JSON.stringify(s)); document.dispatchEvent(new CustomEvent('tengel:cb')); }"""
# 作戦会議の レース 1つ：start 分 あと（分の はじめに そろえる）に 発走・notify＝[m]（lead 秒 あとに お知らせが 来る ように m を 決める ことも できる）・seen 分 あとを 見た 時刻に
SETPLAN = """o => { const pad = n => String(n).padStart(2, '0'); const s = new Date(Date.now() + o.start * 60000); s.setSeconds(0, 0);
  const date = s.getFullYear() + '-' + pad(s.getMonth() + 1) + '-' + pad(s.getDate()), time = pad(s.getHours()) + ':' + pad(s.getMinutes());
  const m = o.lead != null ? (s.getTime() - (Date.now() + o.lead * 1000)) / 60000 : o.m;
  localStorage.setItem('tengel.plan', JSON.stringify({ v: 1, on: o.on !== false, races: [{ id: 'p1', date, time, name: 'テスト特別', n: 12, dist: 1600, venue: '', r: '', memo: '', notify: [m] }] }));
  if (o.seen != null) localStorage.setItem('tengel.planseen', String(Date.now() + o.seen * 60000));
  document.dispatchEvent(new CustomEvent('tengel:plan')); return { date, time, m, left: Math.round((s.getTime() - Date.now()) / 1000) }; }"""
PLAN = """() => { const r = document.querySelector('#tcPlan'); if (!r || r.style.display === 'none') return { open: false };
  const pb = r.querySelector('.pb'), pj = r.querySelector('.pj'), q = pb.getBoundingClientRect(), ob = r.querySelector('.oboard'), sn = r.querySelector('.rc .sn');
  return { open: true, st: Math.round(pb.scrollTop), ob: ob ? Math.round(ob.getBoundingClientRect().top - q.top) : null, sn: sn ? !sn.hidden : null, snt: sn ? sn.textContent : null,
    pj: pj && !pj.hidden ? { see: pj.getBoundingClientRect().bottom <= q.top + 1 && pj.getBoundingClientRect().height > 20, on: [...pj.querySelectorAll('button')].map(b => b.getAttribute('aria-pressed')), t: [...pj.querySelectorAll('button')].map(b => b.innerText) } : null }; }"""
OSHI0 = '推し馬（押すと 作戦会議の 推し馬の 欄を 開くよ）'
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 402, 'height': 874}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo')
        ctx.add_init_script(FAKE)
        pg = ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        pg.goto(APP); pg.wait_for_function("() => window.TengelWallet && TengelWallet.on && window.TengelFab && document.querySelector('#cbFab')", timeout=60000)
        pg.wait_for_timeout(800); gate(pg); pg.wait_for_timeout(600)
        pg.evaluate("() => { const o = document.querySelector('#lgOv [data-lg=ok]'); if (o) o.click(); }"); pg.wait_for_timeout(300)

        print('■ トレーニングセンターの 丸：お世話トークンの 数')
        t0 = pg.evaluate(BADGE, 'tcFab')
        check(t0['t'] == '5' and t0['cls'] == 'fabc tk' and t0['al'] == 'トレーニングセンター（お世話トークン 5個・押すと 開くよ）' and t0['ah'] == 'true' and t0['corner'] and t0['inView'] and t0['pe'] == 'none' and t0['fs'] >= 10.5 and t0['h'] >= 18,
              f'まだ 開いた ことが ない：丸の 右上に はじめの 5（読み上げは「お世話トークン 5個」・押しても 丸が 押される）（{t0}）')
        res = []
        for s, at, seen, want in (({'stock': 7}, -11, None, '17'), ({'stock': 25}, -1, None, '25'), ({'stock': 20}, -30, None, '25'), ({'stock': 0}, 0, None, '0'),
                                  ({'stock': 10}, -1, 10, '20'), ({'stock': 10}, 3, None, '10')):
            pg.evaluate(SETTC, {'s': s, 'at': at, 'seen': seen}); pg.wait_for_timeout(80); g = pg.evaluate(BADGE, 'tcFab'); res.append((g['t'], want, g['cls']))
        check(all(a == w for a, w, _ in res) and res[3][2] == 'fabc tk z' and res[0][2] == 'fabc tk',
              f'たまる 数（5分ごとに 5個・25個 まで・もどらない 時計・時計が 先の とき は ふえない）・0 は うすく：{[(a, w) for a, w, _ in res]}')
        pg.evaluate(SETTC, {'s': {'stock': 10}, 'at': -5 + 2.5 / 60}); pg.wait_for_timeout(100); a1 = pg.evaluate(BADGE, 'tcFab')['t']
        pg.wait_for_timeout(3600); a2 = pg.evaluate(BADGE, 'tcFab')
        check(a1 == '10' and a2['t'] == '15' and '15個' in a2['al'], f'5分 たった 時刻に 自分で 書き直す（何も しなくても 10 → 15・読み上げも：{a1} → {a2["t"]}）')
        # トレーニングセンターの 中の 数と 同じ（tc_bundle.js の TCApp.tokens.now：アプリの 中と 同じ 数え方）
        pg.evaluate(SETTC, {'s': {'stock': 3}, 'at': -17}); pg.wait_for_timeout(80); b1 = pg.evaluate(BADGE, 'tcFab')['t']
        tcn = pg.evaluate("async () => { await new Promise((ok, ng) => { const s = document.createElement('script'); s.src = 'tc_bundle.js'; s.onload = ok; s.onerror = ng; document.head.appendChild(s); }); return TCApp.tokens.now().stock; }")
        pg.evaluate("() => document.dispatchEvent(new CustomEvent('tengel:tc'))"); pg.wait_for_timeout(80); b2 = pg.evaluate(BADGE, 'tcFab')['t']
        check(b1 == '18' and tcn == 18 and b2 == '18', f'トレーニングセンターの 中の 数（TCApp.tokens.now {tcn}）と 同じ（読む 前 {b1}・読んだ あと {b2}）')

        print('■ TENGERカードバトルの 丸：調査隊切符の 枚数')
        c0 = pg.evaluate(BADGE, 'cbFab')
        check(c0['t'] is None and 'おもちゃ' in c0['al'], f'まだ 解放して いない：枚数は 出さない（🔒 だけ）（{c0}）')
        open_toys(pg, ('cb',)); pg.wait_for_timeout(300)
        c1 = pg.evaluate(BADGE, 'cbFab')
        check(c1['t'] == '15' and c1['cls'] == 'fabc qt' and c1['al'] == 'TENGERカードバトル（調査隊切符 15枚・押すと 開くよ）' and c1['corner'] and c1['inView'] and c1['ah'] == 'true',
              f'解放 したら 丸の 右上に 枚数（まだ 開いた ことが ない：はじめの 15枚）（{c1}）')
        res = []
        for n, at, want in ((4, -65, '6'), (0, 0, '0'), (15, -300, '15'), (14, -45, '15'), (7, 10, '7')):
            pg.evaluate(SETQT, {'n': n, 'at': at}); pg.wait_for_timeout(80); g = pg.evaluate(BADGE, 'cbFab'); res.append((g['t'], want, g['cls']))
        check(all(a == w for a, w, _ in res) and res[1][2] == 'fabc qt z', f'たまる 枚数（30分で 1枚・15枚 まで・時計が もどった ときは ふえない）・0 は うすく：{[(a, w) for a, w, _ in res]}')
        pg.evaluate(SETQT, {'n': 3, 'at': -30 + 2.5 / 60}); pg.wait_for_timeout(100); q1 = pg.evaluate(BADGE, 'cbFab')['t']
        pg.wait_for_timeout(3600); q2 = pg.evaluate(BADGE, 'cbFab')
        check(q1 == '3' and q2['t'] == '4' and '4枚' in q2['al'], f'30分 たった 時刻に 自分で 書き直す（3 → 4：{q1} → {q2["t"]}）')
        pg.evaluate(SETQT, {'n': 9, 'at': -95}); pg.wait_for_timeout(80); d1 = pg.evaluate(BADGE, 'cbFab')['t']
        cbn = pg.evaluate("async () => { await new Promise((ok, ng) => { const s = document.createElement('script'); s.src = 'cb_bundle.js'; s.onload = ok; s.onerror = ng; document.head.appendChild(s); }); CBApp._t.load(); return CBApp._t.qt.n; }")
        pg.evaluate("() => document.dispatchEvent(new CustomEvent('tengel:cb'))"); pg.wait_for_timeout(80); d2 = pg.evaluate(BADGE, 'cbFab')['t']
        check(d1 == '12' and cbn == 12 and d2 == '12', f'カードバトルの 中の 枚数（CBApp の qtNow {cbn}）と 同じ（読む 前 {d1}・読んだ あと {d2}）')

        print('■ 推し馬の 丸：お知らせの 時刻が 来たら 🔔')
        o0 = pg.evaluate(BADGE, 'oshiFab')
        check(o0['t'] is None and o0['al'] == OSHI0, f'予約した レースが ない：🔔 なし（{o0}）')
        cases = []
        for o, want in (({'start': 4, 'm': 5, 'seen': -10}, True), ({'start': 4, 'm': 5, 'seen': -10, 'on': False}, False), ({'start': 4, 'm': 5, 'seen': 0}, False),
                        ({'start': -1, 'm': 5, 'seen': -30}, False), ({'start': 30, 'm': 5, 'seen': -10}, False), ({'start': 4, 'm': 5, 'seen': -10}, True)):
            pg.evaluate(SETPLAN, o); pg.wait_for_timeout(80); g = pg.evaluate(BADGE, 'oshiFab'); cases.append(((g['t'] == '🔔'), want))
        g = pg.evaluate(BADGE, 'oshiFab')
        check(all(a == w for a, w in cases) and g['cls'] == 'fabb' and g['al'].startswith('推し馬（🔔') and '作戦会議の レースを 開くよ' in g['al'] and g['corner'] and g['inView'] and g['ah'] == 'true',
              f'🔔：通知 オン・お知らせの 時刻が 来た・発走 前・見た あとに 来た ときだけ（通知 オフ・もう 見た・発走 後・まだ 時刻 前 は 出ない：{cases}）・読み上げにも（{g["al"]}）')
        shot(pg, 'fab_badges', {'x': 402 - 110, 'y': 874 - 420, 'width': 110, 'height': 420})
        # 押すと 作戦会議の 上（予約した レース）が 開く・まもなく 発走の 札・🔔 は 消える
        pg.locator('#oshiFab .fabi').click(); pg.wait_for_function("() => window.TCPlan && TCPlan.isOpen()", timeout=30000); pg.wait_for_timeout(700)
        p1 = pg.evaluate(PLAN); o1 = pg.evaluate(BADGE, 'oshiFab'); jb = pg.evaluate("() => { const j = document.querySelector('#tcPlan .pj .jb'); return j ? !j.hidden : null; }")
        shot(pg, 'plan_soon')
        check(p1['open'] and p1['st'] == 0 and p1['sn'] is True and p1['snt'] == '🔔 まもなく発走' and jb is True and p1['pj'] and p1['pj']['see'] and p1['pj']['on'] == ['true', 'false'] and p1['pj']['t'][0] == '📋 作戦会議 🔔'
              and o1['t'] is None and o1['al'] == OSHI0,
              f'🔔 の ときに 押す → 作戦会議の 上（予約した レース）が 開く・レースに「🔔 まもなく発走」・「📋 作戦会議 🔔」・開いたら 丸の 🔔 は 消える（{p1}・{o1["t"]}）')
        pg.locator('#tcPlan [data-p=jo]').click(); pg.wait_for_timeout(300); p2 = pg.evaluate(PLAN)
        shot(pg, 'plan_oshi')
        pg.locator('#tcPlan [data-p=jr]').click(); pg.wait_for_timeout(300); p3 = pg.evaluate(PLAN)
        check(p2['pj']['see'] and p2['pj']['on'] == ['false', 'true'] and p2['st'] > 0 and 0 <= p2['ob'] <= 12 and p3['st'] == 0 and p3['pj']['on'] == ['true', 'false'],
              f'推し馬の 欄でも 行き先の 札は 見えた まま →「📋 作戦会議」で 予約した レースへ もどれる（{p2["pj"]} → {p3["pj"]["on"]}）')
        pg.locator('#tcPlan [data-p=close]').click(); pg.wait_for_timeout(300)
        o2 = pg.evaluate(BADGE, 'oshiFab')
        pg.locator('#oshiFab .fabi').click(); pg.wait_for_function("() => window.TCPlan && TCPlan.isOpen()", timeout=30000); pg.wait_for_timeout(700); p4 = pg.evaluate(PLAN)
        check(o2['t'] is None and p4['st'] > 0 and 0 <= p4['ob'] <= 12 and p4['pj']['on'] == ['false', 'true'], f'閉じても 🔔 は 出ない（見た）・次に 押すと いつもの「推し馬」の 欄（{o2["t"]}・{p4["ob"]}px）')
        # 開いて いる 間に 時刻が すぎて「まもなく発走」が 出る（15秒 ごとに 見直す：ここは 自分で 呼ぶ かわりに 時刻を 進めて 待つ）
        pg.locator('#tcPlan [data-p=close]').click(); pg.wait_for_timeout(200)
        pg.evaluate(SETPLAN, {'start': 30, 'm': 5, 'seen': -10}); pg.locator('#planBtn').click(); pg.wait_for_function("() => TCPlan.isOpen()"); pg.wait_for_timeout(400)
        p5 = pg.evaluate(PLAN); pg.locator('#tcPlan [data-p=close]').click(); pg.wait_for_timeout(200)
        check(p5['sn'] is False and p5['pj']['t'][0] == '📋 作戦会議', f'まだ お知らせの 時刻 前の レースには「まもなく発走」なし（{p5["sn"]}・{p5["pj"]["t"]}）')
        # 開いて いない 間に お知らせの 時刻が 来る（何も しなくても 🔔 が 出る）
        info = pg.evaluate(SETPLAN, {'start': 3, 'lead': 3, 'seen': -10}); pg.wait_for_timeout(100); e1 = pg.evaluate(BADGE, 'oshiFab')['t']
        pg.wait_for_timeout(3800); e2 = pg.evaluate(BADGE, 'oshiFab')['t']
        check(e1 is None and e2 == '🔔', f'お知らせの 時刻（{info}）に 自分で 🔔 を 出す（{e1} → {e2}）')
        nt = pg.evaluate("() => TCPlanNotify().map(x => x.id)")
        check(nt == [], f'作戦会議の 通知の 予定（TCPlanNotify）は 前と 同じ（すぎた お知らせは 入れない：{nt}）')
        pg.evaluate("() => { localStorage.removeItem('tengel.plan'); document.dispatchEvent(new CustomEvent('tengel:plan')); }"); pg.wait_for_timeout(80)

        print('■ 画面の 上の データの 札')
        d0 = pg.evaluate("() => document.querySelector('#dbpill').textContent")
        shot(pg, 'pill', {'x': 0, 'y': 0, 'width': 402, 'height': 150})
        pg.evaluate("(async () => { const L = TengelLocal.slots; const rows = L.rows(1).slice(0, 40).map(r => Object.assign({}, r, { id: r.id.replace('-m1-', '-m2-'), src: undefined })); await L.replace(2, rows, { source: 'excel', file: 'テスト.xlsx' }); await L.setActive(2); })()")
        pg.wait_for_timeout(1500); d1 = pg.evaluate("() => document.querySelector('#dbpill').textContent")
        pg.evaluate("TengelLocal.slots.setActive(1)"); pg.wait_for_timeout(1200); d2 = pg.evaluate("() => document.querySelector('#dbpill').textContent")
        check(d0 == 'テンゲルデータ' and re.fullmatch(r'マザーデータ① 40走・記録 \d+件', d1 or '') and d2 == 'テンゲルデータ',
              f'テンゲルデータは 名前 だけ（{d0!r}）・マザーデータ①に すると「○走・記録 ○件」（{d1!r}）・もどすと また 名前 だけ（{d2!r}）')

        print('■ 着せ替え：壁紙の 組')
        pg.click('.tabbar button[data-tab=set]'); pg.wait_for_timeout(800)
        ks = pg.evaluate("""() => [...document.querySelectorAll('#setKisekae .ksg')].map(h => { let g = h.nextElementSibling; while (g && !g.classList.contains('ksgrid')) g = g.nextElementSibling;
          return [h.firstChild.textContent, h.querySelector('small').textContent, g ? [...g.querySelectorAll('.kst .ksn')].map(e => e.textContent) : null]; })""")
        PT = ['いつもの', '牧場', 'かわいいお馬さん', '毛糸のお馬とロボット', 'ぷりけつのお馬', '夕焼け', '花火', 'ナイター', '競馬新聞', '勝負服', '招き馬', '水墨画', '大理石の馬', 'ドット', '黒板', 'メリーゴーランド', '星座']
        check([k[:2] for k in ks] == [['壁紙パック', '10'], ['ポイント壁紙カスタム', '17'], ['帯', '3']] and ks[1][2] == PT and ks[2][2] == ['シルバー帯', 'ゴールド帯', 'マスター帯'],
              f'組は 3つ（壁紙パック・ポイント壁紙カスタム 17・帯）・ポイント壁紙カスタムは 組に 分けずに 並べる（前の 並びの まま：{ks[1][2][:3]} … {ks[1][2][-2:]}）')
        hs = pg.evaluate("() => [...document.querySelectorAll('#setKisekae h3')].map(h => h.firstChild.textContent)")
        check(not any(h in ('定番', '季節・行事', '競馬', '和・アート', 'レトロ・ポップ') for h in hs), f'前の 組の 見出し（定番・季節・行事 など）は ない（{hs}）')
        pg.evaluate("() => { const h = document.querySelectorAll('#setKisekae .ksg')[1]; h.scrollIntoView({ block: 'start' }); window.scrollBy(0, -120); }"); pg.wait_for_timeout(300)
        shot(pg, 'kisekae_groups')
        check(not errs, f'エラー なし {errs[:3]}')
        ctx.close()

        print('■ 小さい 画面（iPhone SE：2列 × 2段 に なる ことが ある）')
        ctx2 = b.new_context(viewport={'width': 375, 'height': 667}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo')
        ctx2.add_init_script(FAKE)
        p2_ = ctx2.new_page(); errs2 = []; p2_.on('pageerror', lambda e: errs2.append(str(e)[:200]))
        p2_.goto(APP); p2_.wait_for_function("() => window.TengelWallet && TengelWallet.on && document.querySelector('#cbFab')", timeout=60000); p2_.wait_for_timeout(800); gate(p2_); p2_.wait_for_timeout(600)
        p2_.evaluate("() => { const o = document.querySelector('#lgOv [data-lg=ok]'); if (o) o.click(); }"); open_toys(p2_, ('cb',)); p2_.wait_for_timeout(300)
        p2_.evaluate(SETPLAN, {'start': 4, 'm': 5, 'seen': -10}); p2_.wait_for_timeout(300)
        sm = p2_.evaluate("""() => { const R = e => { const r = e.getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom]; };
          const ms = [...document.querySelectorAll('#fabCol .fabc, #fabCol .fabb')].filter(e => !e.hidden), fi = [...document.querySelectorAll('#fabCol .fabi')];
          return { g2: document.querySelector('#fabCol').classList.contains('g2'), fd: getComputedStyle(document.querySelector('#fabCol')).getPropertyValue('--fd'), n: ms.length,
            inView: ms.every(m => { const r = m.getBoundingClientRect(); return r.left >= 0 && r.right <= innerWidth && r.top >= 0; }),
            over: ms.some(m => { const a = R(m), own = m.closest('.fabi'); return fi.some(f => f !== own && (() => { const c = R(f); return a[0] < c[2] - 2 && c[0] < a[2] - 2 && a[1] < c[3] - 2 && c[1] < a[3] - 2; })()); }) }; }""")
        shot(p2_, 'fab_badges_se', {'x': 375 - 130, 'y': 667 - 330, 'width': 130, 'height': 330})
        check(sm['n'] == 3 and sm['inView'] and not sm['over'] and not errs2, f'小さい 画面でも 3つの 札（数・数・🔔）は 画面の 中・ほかの 丸に 重ならない（{sm}）')
        ctx2.close()
        b.close()
finally:
    srv.terminate()
print('NG' if fails else 'OK', len(fails), fails)
sys.exit(1 if fails else 0)
