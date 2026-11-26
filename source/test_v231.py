# 第4.231版の テスト：GitHub の Mac（run 206・第4.230版）の 報告に 出た「ResizeObserver loop completed with undelivered notifications」
#   第4.230版で 作戦会議と 壁紙&ボード着せ替えを 上の 帯の 3段目に 置いた（tc/tc_launch.js の dockPut：帯の 下の 余白〈.top-in の padding-bottom〉を 広げる）。
#   その 置き直しを 大きさの 見張り（ResizeObserver：上の 帯・レース情報の カード）の 中で その場で して いた ＝ 見張って いる 上の 帯の 高さが 見張りの 中で かわる
#   → ブラウザが「とどけきれなかった 知らせが ある」と エラーに する（アプリの 動きは かわらないが、run 206 では 7つの 報告に 出て「ぜんぶ リセット」の たしかめが CHECK）
#   直し：見張りからは 次の 描画の 前（planSoon：requestAnimationFrame）に まわす（上の 帯の 中に 置く／置いて いる とき）。カードの 右上（広い 画面）は 前の とおり その場で
#   ① iPhone の 3つの 大きさ（402×874・390×844・iPad の iPhone 用の 画面 375×647）と 広い 画面（820×1180）：
#      開く → 最初の 画面 → ログインボーナス → 5つの タブ → 上下に 動かす → 30この 壁紙 ぜんぶ → 開き直す の あいだ、このエラーが 0回
#   ② そのあとも 作戦会議・着せ替えは 上の 帯の 3段目（iPhone）／前の 場所（広い 画面：判定タブ）・帯の 下の 余白は 3段目の ぶん
#   python3 test_v231.py
import os, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv_v231'); PORT = 8858; APP = f'http://localhost:{PORT}/APP/'
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL,
               env=dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, HIST='hist_280.json', DROP='', TARGET='app'))
from assets_dir import adir
pth = os.path.join(SRV, 'APP', 'index.html'); html = open(pth, encoding='utf8').read()
assert "window.__NATIVE = location.protocol === 'tengel:';" in html
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
A = os.path.join(SRV, 'APP')
for d in ('tc_assets', 'fig_assets'):
    try: a = adir(d)
    except Exception: a = None
    if a and os.path.isdir(a):
        for f in os.listdir(a):
            if f.endswith('.webp') and not os.path.exists(os.path.join(A, f)): shutil.copy(os.path.join(a, f), os.path.join(A, f))
for f in ('cb_icon.webp',):
    a = os.path.join(W, 'ios', 'cb_assets', f)
    if os.path.exists(a): shutil.copy(a, os.path.join(A, f))
BL = os.environ.get('KISEKAE_ASSETS') or os.path.join(W, 'ios', 'kisekae_blobs'); WALL = os.path.isdir(BL) and len(os.listdir(BL)) > 50
if WALL:
    for f in os.listdir(BL): shutil.copy(os.path.join(BL, f), os.path.join(A, 'ks_' + f))
else: print('※ 壁紙の 絵（ios/kisekae_blobs）が ない ので、標準の 見た目 だけ')
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
FAKE = open(os.path.join(W, 'test_tc.py'), encoding='utf8').read().split('FAKE = """')[1].split('"""')[0]      # アプリの 窓口の にせもの（test_tc.py と 同じ）
# ブラウザが 出す エラー（window の error）の うち ResizeObserver の もの（どこで 出たか の 印 つき）
RO = """window.__ro = []; window.__ev = []; window.addEventListener('error', e => { const m = String(e && e.message || ''); (/ResizeObserver/.test(m) ? window.__ro : window.__ev).push([Math.round(performance.now()), m.slice(0, 90), window.__roTag || '']); });"""
fails, errs = [], []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c: fails.append(label)


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


# 作戦会議・着せ替えの 場所と 上の 帯（.top-in の 下の 余白）
DOCK = """() => { const R = e => { const r = e.getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom].map(v => Math.round(v * 10) / 10); };
  const hd = document.querySelector('header.top'), ti = hd.querySelector('.top-in'), b = document.getElementById('planBtn'), k = document.getElementById('kiseBtn'), rs = document.getElementById('rsvBtn'), ms = document.getElementById('msBtn');
  const vis = e => !!e && !e.hidden && e.getBoundingClientRect().width > 0;
  return { dk: [b.classList.contains('dk'), k.classList.contains('dk')], par: [b.parentNode === hd, k.parentNode === hd], vis: [vis(b), vis(k)], b: R(b), k: R(k), hd: R(hd), rs: R(rs), ms: R(ms),
    dk3: ti.classList.contains('dk3'), pb: ti.style.paddingBottom, tab: (document.querySelector('.tabbar button[aria-selected="true"]') || { dataset: {} }).dataset.tab || null }; }"""

try:
    with sync_playwright() as p:
        br = p.chromium.launch()
        for vw, vh, wide in ((402, 874, False), (390, 844, False), (375, 647, False), (820, 1180, True)):
            ctx = br.new_context(viewport={'width': vw, 'height': vh}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo', has_touch=True, is_mobile=not wide)
            ctx.add_init_script(FAKE); ctx.add_init_script(RO)
            pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
            tag = lambda t: pg.evaluate(f"() => {{ window.__roTag = {t!r}; }}")
            pg.goto(APP); pg.wait_for_function("() => window.TengelFab && document.querySelector('#figFab') && document.getElementById('kiseBtn')", timeout=60000)
            tag('gate'); pg.wait_for_timeout(800); gate(pg); pg.wait_for_timeout(2500)
            tag('login'); pg.evaluate("() => { const o = document.querySelector('#lgOv [data-lg=ok]'); if (o) o.click(); }"); pg.wait_for_timeout(1500)
            tabs = []
            for t in ('win5', 'rec', 'stats', 'set', 'judge'):
                tag('tab-' + t)
                pg.evaluate(f"() => {{ const x = document.querySelector('.tabbar button[data-tab={t}]') || document.querySelector('.tabs-top [data-tab={t}]'); if (x) x.click(); }}"); pg.wait_for_timeout(900)
                tabs.append(pg.evaluate(DOCK)['dk'])
            tag('scroll'); pg.mouse.wheel(0, 1500); pg.wait_for_timeout(800); pg.mouse.wheel(0, -3000); pg.wait_for_timeout(800)
            nw = 0
            if WALL:
                ids = pg.evaluate("() => TengelKisekae.list().map(t => t.id || t)")
                for tid in ids:
                    tag('wall-' + tid); pg.evaluate("(id) => TengelKisekae.apply(id, false)", tid)
                    try: pg.wait_for_function("(id) => TengelKisekae.current() === id && TengelKisekae.loaded()", arg=tid, timeout=8000); nw += 1
                    except Exception: pass
                    pg.wait_for_timeout(1300)
                pg.evaluate("(id) => TengelKisekae.apply(id, false)", 'default'); pg.wait_for_timeout(1500)
            q = pg.evaluate(DOCK)
            r0, e0 = pg.evaluate('() => window.__ro'), pg.evaluate('() => window.__ev')
            tag('reload'); pg.reload(); pg.wait_for_function("() => window.TengelFab && document.querySelector('#figFab') && document.getElementById('kiseBtn')", timeout=60000)
            pg.wait_for_timeout(800); gate(pg); pg.wait_for_timeout(2500)
            r, ev = r0 + pg.evaluate('() => window.__ro'), e0 + pg.evaluate('() => window.__ev')
            q2 = pg.evaluate(DOCK)
            print(f'■ {vw}×{vh}{"（広い 画面）" if wide else ""}')
            check(not r and not ev, f'開く・最初の 画面・ログインボーナス・5つの タブ・上下・壁紙 {nw}こ・開き直す の あいだ ResizeObserver の エラー {len(r)} 回（{r[:3]}）・ほかの エラー {len(ev)} 回（{ev[:2]}）')
            if not wide:
                okd = all(x == [True, True] for x in tabs) and q['dk'] == [True, True] and q['par'] == [True, True] and q['vis'] == [True, True] and q['dk3'] and q2['dk'] == [True, True] and q2['dk3']
                cb, ck = (q['b'][0] + q['b'][2]) / 2, (q['k'][0] + q['k'][2]) / 2
                below = q['b'][1] >= q['rs'][3] - 12 and q['k'][1] >= q['ms'][3] - 0.5 and q['k'][3] <= q['hd'][3] + 0.5 and (q['b'][1] + q['b'][3]) / 2 < q['hd'][3]
                check(okd and below and q['pb'] not in ('', '0px') and q2['pb'] == q['pb'],
                      f'作戦会議・着せ替えは 5つの タブで 上の 帯の 3段目（結果待ち・ミッションの 下・帯の 中：作戦会議 {q["b"]}・着せ替え {q["k"]}・帯の 下 {q["hd"][3]}）・帯の 下の 余白 {q["pb"]}（開き直しても {q2["pb"]}）')
            else:
                check(q['dk'] == [False, False] and not q['dk3'] and q['tab'] in ('judge', None) and q['vis'] == [True, True] and q2['dk'] == [False, False],
                      f'広い 画面は 前の 場所（上の 帯に 入れない：{q["dk"]}・判定タブで 出る {q["vis"]}）')
            ctx.close()
        br.close()
finally:
    srv.terminate(); shutil.rmtree(SRV, ignore_errors=True)
if errs: print('page errors:', errs[:3]); fails.append('page errors')
print('合計', len(fails), 'NG' if fails else 'OK', flush=True)
sys.exit(1 if fails else 0)
