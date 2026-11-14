# お世話チャレンジ（第4.173版）の 光の 点めつ：馬バレ 6色（青・緑・紫・赤・金・虹）＋ 虹の「演出を控えめにする」を 60コマ／秒の 絵に して kisekae/flash_px.py で 数える
#   まさちゃん 2026/11/15 00:40「青から虹色にかけて光りは激しく大きくして！」→ 大きく・こく しても、ちかちかは させない（1秒に 3回 まで・画面の 10%）
#   コップに 入る 0.5秒 前から、馬バレが ついて・保留が たまって・光が 落ちつく まで（色ごとに 長さが ちがう）。画面 ぜんぶ（390×844）を 写す
#   python3 test_tc_drop_flash.py [1,6,…]   （時間が かかる ので ふだんの テストとは 別に 動かす。コマは t5/dp_frames/<色>/ に 残す）
#   写して いる 間は トレーニングセンターの フィールドを 描くのを 止める（止まった 絵の まま：台の うしろで 9割 かくれて いる・写すのが 速く なる）
import json, os, re, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv_tc'); PORT = 8813; APP = f'http://localhost:{PORT}/APP/'
ONLY = [int(x) for x in sys.argv[1].split(',')] if len(sys.argv) > 1 else None      # 数える 色（1 青 … 6 虹）
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, TARGET='app'))
from assets_dir import adir
TCA = adir('tc_assets'); HAVE = os.path.isfile(os.path.join(TCA, 'tc_dp.json')) and len(os.listdir(TCA)) > 100
for d in ('APP',):
    pth = os.path.join(SRV, d, 'index.html'); html = open(pth, encoding='utf8').read()
    open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
    if HAVE:
        for f in os.listdir(TCA): shutil.copy(os.path.join(TCA, f), os.path.join(SRV, d, f))
if not HAVE: print('※ お世話チャレンジの 絵と 音（ios/tc_assets の tc_dp.json）が ない ので、数えない'); sys.exit(0)
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c: fails.append(label)


FAKE = """
window.__NATIVE_INFO = { version: '1.0', build: '7', device: 'phone' };
window.__notify = { auth: 'notDetermined', items: [], calls: [] };
window.__marks = {};
window.webkit = { messageHandlers: { tengel: { postMessage: function (m) {
  var P = m.payload, val = true;
  if (m.name === 'notify') { var NN = window.__notify; NN.calls.push(P);
    if (P.op === 'status') val = { ok: true, auth: NN.auth };
    else if (P.op === 'permission') { NN.auth = 'authorized'; val = { ok: true, granted: true, auth: NN.auth }; }
    else if (P.op === 'sync') { NN.items = P.items; val = { ok: true, scheduled: P.items.length, auth: NN.auth }; }
    else if (P.op === 'opened') val = { ok: true, opened: null };
    else val = { ok: true, list: NN.items }; }
  if (m.name === 'iap') val = P.op === 'products' ? { ok: true, products: [] } : { ok: true, list: [], current: [], unfinished: [], active: [] };
  if (m.name === 'marker') { var k = P.key || 'm', M = window.__marks; if (P.op === 'set') { M[k] = P.value || '1'; val = { ok: true }; } else if (P.op === 'del') { delete M[k]; val = { ok: true }; } else val = { ok: true, has: k in M, value: M[k] }; }
  setTimeout(function () { window.__nativeReply(m.id, true, val); }, 20);
} } } };
"""


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


def stage_click(pg, x, y):            # フィールドの 座標（1052×1657）で タップ
    r = pg.evaluate("() => { const b = document.querySelector('#tcOv .tcst').getBoundingClientRect(); return [b.left, b.top, b.width, b.height]; }")
    pg.mouse.click(r[0] + x / 1052 * r[2], r[1] + y / 1657 * r[3])


def open_tc(pg, url, wait_drop=True):
    pg.goto(url); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(600)
    pg.evaluate("() => document.querySelectorAll('.tabbar button')[2].click()"); pg.wait_for_timeout(300)
    pg.locator('#tcFab').click()
    pg.wait_for_function("() => window.TCApp && TCApp.state && window.TCCare && TCCare.on && !document.querySelector('#tcOv .tcld')", timeout=90000); pg.wait_for_timeout(1000)
    if wait_drop: pg.wait_for_function("() => window.TCDrop && TCDrop.ready()", timeout=30000)


# ---- ページの 中で 使う 小さな 道具 ----
INFO = "() => TCDrop.info()"
# いまの ようす（保存・財布）：wal＝財布（あずかりも）・dp＝わたして いない 当たり・saved＝localStorage の 中
ST = """() => { const s = TCApp.state, sv = JSON.parse(localStorage.getItem('tengel.tc')) || {}, S = TCCare.S; return { stock: S.stock, sstock: sv.stock, cares: s.cares, total: s.total || 0, rs: s.rs.n, tickets: s.tickets || 0,
  dp: (s.dp && s.dp.holds || []).map(z => [z.k, z.c, z.vis]), sdp: (sv.dp && sv.dp.holds || []).map(z => [z.k, z.c]), wal: TengelWallet.total() + TengelWallet.hold().total,
  push: !!(S.push && S.push.hideT == null), fxHold: !!S.fxHold, open: TCDrop.isOpen(), pend: s.pend ? s.pend.k : null }; }"""
SETTOK = "n => { const S = TCCare.S, s = TCApp.state; S.stock = n; S.stockShow = n; s.stock = n; s.stockAt = Date.now(); S.high = 0; s.high = 0; }"
PUSH_ON = "() => { const S = TCCare.S; if (!(S.push && S.push.hideT == null)) TCCare.pushShow(S.lastT + 0.05); }"
PUSH_LIVE = "() => { const S = TCCare.S; return !!(S.push && S.push.hideT == null); }"
# その 当たりが 出る くじの 数（いまの 馬の 表の 中で、その 当たりの 幅の まん中。高確ゾーンは なしで）
RND_FOR = """(want) => { const T = TCApp._t, tab = TCApp.state.visit ? T.PRIZES_VISIT[TCApp.state.visit.kind] : T.PRIZES; let a = 0;
  for (const [p, z] of tab) { if (z.k === want.k && (want.k !== 'pt' || z.v === want.v) && (want.k !== 'rt' || !want.tier || z.tier === want.tier)) return a + p / 2; a += p; } return null; }"""
# 「玉を落とす」を 押す：その 間 だけ くじ（Math.random）を 決めた 数の 列に する（列が おわったら さいごの 数）。押せた ときは true
GO = """([seq]) => { const R = Math.random, q = (seq || []).slice(); let last = q.length ? q[q.length - 1] : 0.995; TCCare.S.high = 0; TCApp.state.high = 0;
  Math.random = () => (q.length ? (last = q.shift()) : last);
  try { return TCDrop.tap('go'); } finally { Math.random = R; } }"""
# 「玉を落とす」を 本物の 指の 出来事（pointerdown：台の キャンバスへ）で 押す。その 間 だけ くじを 決めた 数の 列に する（test_tc.py の PRESS と 同じ やり方）
GO_PTR = """([seq]) => { const R = Math.random, q = (seq || []).slice(); let last = q.length ? q[q.length - 1] : 0.995; TCCare.S.high = 0; TCApp.state.high = 0;
  const st = document.querySelector('#tcOv .tcst'), cv = st.querySelector('canvas.tcdp'), r = st.getBoundingClientRect(), g = TCDrop.geo().go;
  const o = { bubbles: true, cancelable: true, clientX: r.left + g[0] / 1052 * r.width, clientY: r.top + g[1] / 1657 * r.height, pointerId: 9, pointerType: 'touch', isPrimary: true };
  Math.random = () => (q.length ? (last = q.shift()) : last);
  try { cv.dispatchEvent(new PointerEvent('pointerdown', o)); } finally { Math.random = R; }
  cv.dispatchEvent(new PointerEvent('pointerup', o)); return TCDrop.info().phase === 'fall'; }"""
# 時計を 手で 進める（1/60秒ずつ・1コマ ごとに 待って いる 続き〈await〉を 流す）。cond（文字列の 式）が 本当に なったら そこで 止まる。返り値＝進めた 秒
TICK = """async ([sec, cond]) => { const T = TCDrop._t, f = cond ? new Function('return (' + cond + ')') : null; let n = 0;
  for (; n < Math.round(sec * 60); n++) { if (f && f()) break; if (!T.tick(1 / 60)) break; await null; } return n / 60; }"""
SES = "() => { const a = TCDrop._t.rec.map(q => q[1]); TCDrop._t.rec.length = 0; return a; }"      # 台が 鳴らした 音（名前）を 取り出して 空に する
FX_ON = "() => !!document.querySelector('#tcOv .tcfx.on')"


def seq_for(pg, want):
    """その 当たりを 出す くじの 列（はずれ＝None）"""
    if want is None: return [0.995]
    r = pg.evaluate(RND_FOR, want); assert r is not None, want
    if want['k'] == 'tk': return [r, 0.9, 0.3]          # 枚数（1枚）・番号
    if want['k'] == 'zn': return [r, 0.3, 0.9]          # 番号・上乗せは 0回（1,000P）
    return [r, 0.3, 0.3]                               # 番号・ルーレットは 安い 方



# フィールドを 描くのを 止める／もどす：アプリが うしろに 回った ときと 同じ 合図（visibilitychange）を 送る
HIDE = "(h) => { Object.defineProperty(document, 'hidden', { configurable: true, get: () => !!h }); document.dispatchEvent(new Event('visibilitychange')); }"
NAMES = ['', '青', '緑', '紫', '赤', '金', '虹']
try:
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'])
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo'); ctx.add_init_script(FAKE)
        pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        open_tc(pg, APP)
        LEN = pg.evaluate("() => TCDrop.TONE.slice(1).map(t => t.len)")
        FD = os.path.join(W, 't5', 'dp_frames')
        for c, wnt, calm in [(1, {'k': 'pt', 'v': 100}, 0), (2, {'k': 'rt', 'tier': 'normal'}, 0), (3, {'k': 'rt', 'tier': 'maboroshi'}, 0), (4, {'k': 'rt', 'tier': 'kamisama'}, 0), (5, {'k': 'zn'}, 0), (6, {'k': 'tk'}, 0), (6, {'k': 'tk'}, 1)]:
            if ONLY and c not in ONLY: continue
            d = os.path.join(FD, f'c{c}{"_calm" if calm else ""}'); shutil.rmtree(d, ignore_errors=True); os.makedirs(d); t0 = time.time()
            pg.evaluate("c => TengelFx.set({ calm: !!c })", calm); pg.evaluate(SETTOK, 25); pg.evaluate(PUSH_ON); pg.wait_for_timeout(900)
            stage_click(pg, *pg.evaluate("() => TCCare.PUSHG.dp")); pg.wait_for_function("() => TCDrop.isOpen()", timeout=8000)
            pg.evaluate("() => { TCDrop._t.manual = true; TCDrop._t.rec = []; TCDrop._t.path = 5; }"); pg.evaluate(TICK, [0.8, None])
            pg.evaluate(GO, [seq_for(pg, wnt)])
            pg.evaluate(TICK, [8, "TCDrop.state.ball && (TCDrop.state.t - TCDrop.state.ball.t0) * 60 >= TCDrop.state.ball.p.tin - 30"])      # コップに 入る 0.5秒 前から
            pg.evaluate(HIDE, True); pg.wait_for_timeout(200)
            n = 0; N = int(round((0.5 + LEN[c - 1] + 1.6) * 60))      # 入る → 馬バレ（はげしい 間）→ 落ちつく（0.7秒）→ その あと 0.9秒
            for i in range(N):
                pg.evaluate(TICK, [1 / 60, None]); pg.screenshot(path=os.path.join(d, f'f{n:04d}.png')); n += 1
            lcd = pg.evaluate(INFO)['lcd']
            r = subprocess.run(['python3', os.path.join(W, 'kisekae', 'flash_px.py'), d, '0'], capture_output=True, text=True, env=dict(os.environ, AREA='.1'))
            out = r.stdout.strip().split('\n')
            check(r.returncode == 0 and '窓 0個' in (out[0] if out else '') and lcd == c, f'{NAMES[c]}{"（演出を控えめに）" if calm else ""}：{n}コマ（{time.time() - t0:.0f}秒）… {out[0] if out else r.stderr[-200:]}／{out[-1] if out else ""}')
            pg.evaluate(HIDE, False); pg.wait_for_timeout(300)
            pg.evaluate("() => { TCDrop._t.manual = false; TCDrop.close(); }"); pg.wait_for_timeout(400)
            pg.evaluate("() => { for (const z of (TCApp.state.dp && TCApp.state.dp.holds || []).slice()) TCApp._t.give(z); TCCare.pushDone(TCCare.S.lastT); }"); pg.wait_for_timeout(400)
        pg.evaluate("() => TengelFx.set({ calm: false })")
        check(errs == [], f'エラーなし（{errs[:2]}）')
        ctx.close(); b.close()
finally:
    srv.terminate()
print('\n' + ('❌ ' + str(len(fails)) + ' こ 失敗：\n  ' + '\n  '.join(fails) if fails else '✅ ぜんぶ OK'))
sys.exit(1 if fails else 0)
