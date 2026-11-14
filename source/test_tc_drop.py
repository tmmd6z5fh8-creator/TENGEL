# トレーニングセンターの「お世話チャレンジ」（玉を 落とす 台：第4.173版）の テスト
#   まさちゃん 2026/11/14 23:34「トレーニングセンターの抽選を、今のボタンと、もう一つボール落としができるようにしたい！…パチンコを選択すると5個玉を落とすことができる。
#     お世話トークンが5個以上ある場合は、5回の抽選が終わったら、続けてやる、終わり、を選べるボタンがでてくる。…確率とかは、今の抽選のまま…
#     先バレの光る色(示唆) 10P〜300Pは、青／ルーレット1/125は、緑／1/245は、紫／1/399は、赤／幻の馬ルーレットは、金／神様馬ルーレットとチケット扉は、虹色」
#   23:40「1個1トークン・5マス・（特化ゾーンは）金色」／11/15 00:40「コップに玉が入って、当選した瞬間に、音と一緒に…当選の色のデザインと光が付く…青から虹色にかけて光りは激しく大きく」
#   ・App Store版（TARGET=app）：PUSH の 左下の 入口 → 台 → 玉（くじは 決めた 数で）→ 馬バレ → 保留 → 保留結果を見る → 続けてやる／終わり・途中で 閉じた とき・絵が ない とき・光の 点めつ
#   ・テスト版（TENGEL_TEST=1）：道具箱の「④ お世話チャレンジ」
#   python3 test_tc_drop.py   （ios/tc_assets/ に 台の 絵（tc_dp.json）が ある とき だけ 画面の テスト。ない とき（CI）は 中身の 見くらべ だけ）
#   光の 点めつ（馬バレ 6色）は test_tc_drop_flash.py（コマを 写すので 時間が かかる：ふだんの テストとは 別）
import json, os, re, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv_tc'); PORT = 8812; APP = f'http://localhost:{PORT}/APP/'; TESTB = f'http://localhost:{PORT}/TEST/'
SHOT = os.environ.get('SHOT')          # 画面を 写す フォルダ（見る 用）
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, TARGET='app'))
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'TEST')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, TARGET='app', TENGEL_TEST='1'))
from assets_dir import adir
TCA = adir('tc_assets'); HAVE = os.path.isfile(os.path.join(TCA, 'tc_dp.json')) and len(os.listdir(TCA)) > 100
for d in ('APP', 'TEST'):
    pth = os.path.join(SRV, d, 'index.html'); html = open(pth, encoding='utf8').read()
    open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
    if HAVE:
        for f in os.listdir(TCA): shutil.copy(os.path.join(TCA, f), os.path.join(SRV, d, f))
if not HAVE: print('※ お世話チャレンジの 絵と 音（ios/tc_assets の tc_dp.json）が ない ので、中身の 見くらべ だけ')
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


def drop_ball(pg, want):
    """玉を 1こ 落として、コップに 入って 馬バレ（か はずれ）が 出て、次を 押せる ように なる まで 進める → (押した 直後, 入る 直前, 出た 直後, 音, おわった あと)"""
    ok = pg.evaluate(GO, [seq_for(pg, want)]); a = pg.evaluate(INFO); sa = pg.evaluate(ST)
    pg.evaluate(TICK, [8, "TCDrop.state.ball && (TCDrop.state.t - TCDrop.state.ball.t0) * 60 >= TCDrop.state.ball.p.tin - 2"]); b = pg.evaluate(INFO); pg.evaluate(SES)
    pg.evaluate(TICK, [0.4, None]); c = pg.evaluate(INFO); snd = pg.evaluate(SES)
    pg.evaluate(TICK, [6, "TCDrop.state.phase !== 'fall'"]); pg.evaluate(TICK, [0.2, None]); d = pg.evaluate(INFO)
    return dict(ok=ok, a=a, sa=sa, b=b, c=c, snd=snd, d=d)


def finish_fx(pg, limit=150):
    """「保留結果を見る」の あと：いつもの 演出（ルーレット・特化ゾーン・チケット）は タップで 進めて、おしまいの 札まで 待つ"""
    t0 = time.time(); ops = []
    while time.time() - t0 < limit:
        s = pg.evaluate(INFO)
        if not s or s['phase'] == 'end': break
        fx = pg.evaluate(FX_ON); ops.append(s['op'])
        if fx:
            q = pg.evaluate("() => { const r = document.querySelector('#tcOv .tcfx').getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; }")
            pg.mouse.click(q[0] + q[2] / 2, q[1] + q[3] * 0.62)
        pg.wait_for_timeout(250)
    return ops


try:
    # ---------- 中身の 見くらべ（絵が なくても）----------
    print('■ 中身')
    src = {n: open(os.path.join(W, 'tc', n), encoding='utf8').read() for n in ('tc_drop.js', 'tc_app.js', 'tc_care.js', 'tc_guide.js', 'tc_test.js')}
    bundle = open(os.path.join(SRV, 'APP', 'tc_bundle.js'), encoding='utf8').read(); bundle_t = open(os.path.join(SRV, 'TEST', 'tc_bundle.js'), encoding='utf8').read()
    check('window.TCDrop = TCDrop' in bundle and 'canvas.tcdp' in bundle and 'tc_dp.json' in bundle, 'アプリの 束（tc_bundle.js）に 台（TCDrop）が 入って いる')
    check('data-sec="drop"' in bundle_t and 'data-sec="drop"' not in bundle and 'testList' in bundle, 'テスト版の 道具箱の「④ お世話チャレンジ」は テスト版 だけ（App Store版の 束には 入らない）')
    web = open(os.path.join(W, 'tengel3.html'), encoding='utf8').read() if os.path.exists(os.path.join(W, 'tengel3.html')) else ''
    check('TCDrop' not in web and 'tc_dp' not in web, 'Web版（tengel3.html）には 入らない')
    low = bundle.lower()
    check(not any(w in low for w in ('パチンコ', 'pachinko', 'ぱちんこ', 'gambl', 'ギャンブル')), 'アプリの 束に その 言葉（遊技機・かけごとの 名前）は 入れない')
    a = src['tc_app.js']
    check('const z = draw();' in a[a.index('const DROP = {'):a.index('async function dropOpen')] and 'const z = draw(); if (!z) return null;' in a,
          '抽選は PUSH と 同じ くじ（draw）を 1回 ひく（PUSH＝lottery・玉＝DROP.drop：確率は 今の まま）')
    check("TCCare.dropUse(clock())" in a and "ev(t, 'token', { mute: true })" in src['tc_care.js'] and "if (e.k === 'token') { st.cares += 1;" in a,
          '玉 1こ＝お世話トークン 1こ＝お世話 1回（PUSH を 1回 押したのと 同じ 数え方：ev token）')

    if HAVE:
        dp = json.load(open(os.path.join(TCA, 'tc_dp.json')))
        P = dp['paths']; cups = [p['cup'] for p in P]
        check(dp['v'] == 1 and len(P) == 16 and all(cups.count(c) == 4 for c in range(4)) and len(dp['pegs']) == 18 and len(dp['cups']) == 4 and len(dp['hold']['x']) == 5,
              f'データ：落ち方 16とおり（コップごとに 4つ）・釘 18本・コップ 4つ・当選の ます 5つ（{len(P)}・{cups}）')
        okp = []
        for p in P:
            f = p['f']; n = p['n']; x0, y0 = f[0] / 10, f[1] / 10; xe, ye = f[3 * (n - 1)] / 10, f[3 * (n - 1) + 1] / 10; cx, cy = dp['cups'][p['cup']]
            step = max(((f[3 * i] - f[3 * i - 3]) ** 2 + (f[3 * i + 1] - f[3 * i - 2]) ** 2) ** 0.5 / 10 for i in range(1, n))
            okp.append(len(f) == 3 * n and 60 < p['tin'] < n and n <= 200 and abs(x0 - dp['ball']['start'][0]) < 3 and abs(y0 - dp['ball']['start'][1]) < 3
                       and abs(xe - cx) < 70 and ye > cy and step < 40 and all(h[0] <= n and h[1] in (0, 1, 2, 3) for h in p['h']) and sum(1 for h in p['h'] if h[1] == 0) >= 3)
        check(all(okp), f'落ち方：受け皿から 出て・釘に 3回 以上 当たって・その コップの 中で おわる・3.4秒 以内・1コマに 40画素より 動かない（{okp.count(True)}/16）')
        need = ['tc_dp.json', 'tc_dp_base.webp', 'tc_dp_front.webp', 'tc_dp_see.webp', 'tc_dp_ball.webp', 'tc_dp_icon.webp'] + [f'tc_dp_{k}{i}.webp' for k in ('uma', 'hold') for i in range(1, 7)]
        snds = [f'tc_se_dp_{n}.m4a' for n in ['uma1', 'uma2', 'uma3', 'uma4', 'uma5', 'uma6', 'out', 'peg1', 'peg2', 'peg3', 'cup', 'miss', 'hold', 'open']]
        have = set(os.listdir(TCA)); used = set(re.findall(r"dp_[a-z]+\d?", ' '.join(re.findall(r"se\('(dp_[a-z0-9']*)", src['tc_drop.js']))))
        check(all(f in have for f in need + snds) and not [f for f in have if '_dp' in f and f not in need + snds],
              f'素材：絵と データ 18こ・音 14こが そろって いる（ほかの tc_dp の ファイルは ない）')
        sz = sum(os.path.getsize(os.path.join(TCA, f)) for f in need + snds)
        check(sz < 1.2e6 and not any(f.endswith('.png') for f in need), f'素材の 大きさ：合わせて {sz / 1e6:.2f}MB（1.2MB より 小さい・PNG は なし）')

        with sync_playwright() as p:
            b = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'])

            def page(url_ok=True, dsf=1):
                ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=dsf, locale='ja-JP', timezone_id='Asia/Tokyo'); ctx.add_init_script(FAKE)
                pg = ctx.new_page(); pg.errs = []; pg.bad = []
                pg.on('pageerror', lambda e: pg.errs.append(str(e)))
                pg.on('response', lambda r: pg.bad.append(r.url.split('/')[-1]) if r.status >= 400 and 'tc_' in r.url else None)
                return ctx, pg

            def shot(pg, name):
                if SHOT: os.makedirs(SHOT, exist_ok=True); pg.screenshot(path=os.path.join(SHOT, name + '.png'))

            # ================= App Store版 =================
            print('■ App Store版：入口・台・色')
            ctx, pg = page(); open_tc(pg, APP)
            T = pg.evaluate("() => ({ tone: TCDrop.TONE.slice(1), balls: TCDrop.BALLS, name: TCDrop.NAME.slice(1), test: typeof TCApp.test.drop === 'function' ? 1 : 0 })")
            inc = lambda k: all(T['tone'][i][k] < T['tone'][i + 1][k] for i in range(5))
            check(T['balls'] == 5 and T['name'] == ['青', '緑', '紫', '赤', '金', '虹'] and all(inc(k) for k in ('R', 'a', 'dim', 'nt', 'tl', 'len', 'lock')),
                  '光は 青 → 緑 → 紫 → 赤 → 金 → 虹の 順に 大きく・こく・長く なる（オーラの 大きさ R・こさ・暗さ・炎の 数と 長さ・はげしい 間）')
            check([t['rays'] for t in T['tone']] == sorted(t['rays'] for t in T['tone']) and T['tone'][0]['rays'] == 0 and T['tone'][5]['rays'] > T['tone'][3]['rays'] > 0, '光の すじ：青・緑は なし → 紫 から ふえる')
            tone = pg.evaluate("""() => { const f = TCApp._t.dropTone; return [f(null), f({ k: 'pt', v: 10 }), f({ k: 'pt', v: 300 }), f({ k: 'rt', tier: 'normal' }), f({ k: 'rt', tier: 'maboroshi' }), f({ k: 'rt', tier: 'kamisama' }),
              f({ k: 'rt', tier: 'maboroshi', vis: 'maboroshi' }), f({ k: 'zn' }), f({ k: 'zn', vis: 'kamisama' }), f({ k: 'rt', tier: 'kamisama', vis: 'kamisama' }), f({ k: 'tk', n: 1 })]; }""")
            check(tone == [0, 1, 1, 2, 3, 4, 5, 5, 5, 6, 6], f'色：10〜300P＝青・ルーレット 1/125＝緑・1/245＝紫・1/399＝赤・幻の馬の ルーレット＝金・特化ゾーン＝金・神様馬の ルーレット＝虹・チケット＝虹（{tone}）')
            odds = pg.evaluate("() => TCApp._t.PRIZES.filter(q => q[1].k === 'rt').map(q => [Math.round(1 / q[0]), q[1].tier])")
            check(sorted(odds) == [[125, 'normal'], [245, 'maboroshi'], [399, 'kamisama']], f'その ルーレットの 確率は 今の 表の まま（{odds}）')
            check(pg.evaluate("async () => await TCApp.test.drop([1], true)") == 'off' and not pg.evaluate("() => TCDrop.isOpen()"), 'App Store版：テスト版の 道具（玉の 結果を 決める）は 動かない')

            # --- 入口 ---
            pg.evaluate(SETTOK, 12); pg.evaluate(PUSH_ON); pg.wait_for_timeout(120)
            stage_click(pg, *pg.evaluate("() => TCCare.PUSHG.dp")); pg.wait_for_timeout(250)
            check(not pg.evaluate("() => TCDrop.isOpen()") and pg.evaluate(PUSH_LIVE), 'PUSH が 出た すぐ あと（0.4秒）は 入口を 押しても 開かない（撫でるの ボタンの あった 所：お世話が おわる 瞬間に さわって いた 指で 開かない）')
            pg.wait_for_timeout(700)
            G = pg.evaluate("() => TCCare.PUSHG"); geo = pg.evaluate("() => TCDrop.geo()")
            px = pg.evaluate("""([x, y, w, h]) => { const cv = document.querySelector('#tcOv .tco'), g = cv.getContext('2d'), k = cv.width / 1052; const d = g.getImageData(Math.round((x - w / 2) * k), Math.round((y - h / 2) * k), Math.round(w * k), Math.round(h * k)).data;
              let n = 0, gold = 0; for (let i = 0; i < d.length; i += 4) { if (d[i + 3] > 200 && d[i] > 235 && d[i + 1] > 225 && d[i + 2] > 190) n++; if (d[i] > 200 && d[i + 1] > 140 && d[i + 1] < 200 && d[i + 2] < 90) gold++; } return [n / (d.length / 4), gold]; }""", [G['dp'][0], G['dp'][1], G['dpw'], G['dph']])
            check(px[0] > 0.3 and px[1] > 50 and G['dp'][1] + G['dph'] / 2 < 1657 and G['end'][1] + G['eh'] / 2 < 1657 and G['dp'][0] - G['dpw'] / 2 > 0,
                  f'PUSH の 左下に 入口の 札（紙の 色 {px[0]:.0%}・金の ふち）が 出る・画面の 中に おさまる')
            shot(pg, 'dp_push')
            s0 = pg.evaluate(ST)
            stage_click(pg, *G['dp']); pg.wait_for_function("() => TCDrop.isOpen()", timeout=8000); pg.wait_for_timeout(900)
            i0 = pg.evaluate(INFO); s1 = pg.evaluate(ST)
            order = pg.evaluate("() => [...document.querySelector('#tcOv .tcst').children].map(e => e.className.split(' ')[0])")
            check(i0['phase'] == 'ready' and i0['max'] == 5 and i0['n'] == 0 and i0['next'] and s1['fxHold'] and s1['stock'] == 12 and s1['cares'] == s0['cares'],
                  f'入口を 押すと 台が 出る：玉 5こ・まだ 落として いない・トークンは へって いない・PUSH は かくれる（{i0["phase"]}・あと {i0["max"]}こ）')
            check(order.index('tcdp') > order.index('tco') and order.index('tcdp') < order.index('tcfx'), f'重なり：お世話の 絵の 上・当たりの 演出（tcfx）の 下（{order}）')
            shot(pg, 'dp_open')
            # --- やめる（まだ 落として いない）---
            pg.wait_for_function("() => TCDrop.info().t > 0.6"); stage_click(pg, *geo['quit']); pg.wait_for_timeout(700)
            s2 = pg.evaluate(ST)
            check(not s2['open'] and s2['push'] and s2['stock'] == 12 and s2['cares'] == s0['cares'] and not s2['fxHold'], '「やめる」（落とす 前）：台を 閉じて PUSH に もどる・トークンも お世話の 数も そのまま')

            # --- 1回り：青（100P）・はずれ・緑（ルーレット）・金（特化ゾーン）・虹（チケット）---
            print('■ App Store版：玉 5こ → 馬バレ → 保留')
            stage_click(pg, *G['dp']); pg.wait_for_function("() => TCDrop.isOpen()", timeout=8000)
            pg.evaluate("() => { const T = TCDrop._t; T.manual = true; T.rec = []; }"); pg.evaluate(TICK, [0.7, None])
            w0 = pg.evaluate(ST); wants = [{'k': 'pt', 'v': 100}, None, {'k': 'rt', 'tier': 'normal'}, {'k': 'zn'}, {'k': 'tk'}]; exp = [1, 0, 2, 5, 6]; res = []
            check(not pg.evaluate("() => TCDrop.tap('see')") and pg.evaluate(INFO)['phase'] == 'ready', '「保留結果を見る」は かぎが かかって いる（玉を 落とし おわる まで 押せない）')
            for i, wnt in enumerate(wants):
                if i == 0:      # 1こめは 本物の 指で
                    pressed = pg.evaluate(GO_PTR, [seq_for(pg, wnt)])
                    a_ = pg.evaluate(INFO); sa_ = pg.evaluate(ST); again = pg.evaluate("() => TCDrop.tap('go')")
                    pg.evaluate(TICK, [8, "TCDrop.state.ball && (TCDrop.state.t - TCDrop.state.ball.t0) * 60 >= TCDrop.state.ball.p.tin - 2"]); b_ = pg.evaluate(INFO); pre = pg.evaluate(SES)
                    pg.evaluate(TICK, [0.4, None]); c_ = pg.evaluate(INFO); snd_ = pg.evaluate(SES)
                    pg.evaluate(TICK, [6, "TCDrop.state.phase !== 'fall'"]); pg.evaluate(TICK, [0.2, None]); d_ = pg.evaluate(INFO)
                    r = dict(ok=pressed and a_['phase'] == 'fall', a=a_, sa=sa_, b=b_, c=c_, snd=snd_, d=d_)
                    check(r['ok'] and not again and 'dp_out' in pre and sum(1 for n in pre if n.startswith('dp_peg')) >= 3, f'「玉を落とす」を 指で 押すと 玉が 1こ 出る（ポンッ）・落ちて いる 間は もう 押せない・釘に 当たる 音（{sum(1 for n in pre if n.startswith("dp_peg"))}回）')
                    shot(pg, 'dp_uma1')
                else:
                    r = drop_ball(pg, wnt)
                res.append(r)
            ok_cnt = all(r['ok'] and r['sa']['stock'] == 12 - (i + 1) and r['sa']['sstock'] == 12 - (i + 1) and r['sa']['cares'] == w0['cares'] + i + 1 and r['sa']['total'] == w0['total'] + i + 1 and r['sa']['rs'] == w0['rs'] + i + 1 for i, r in enumerate(res))
            check(ok_cnt, f'玉 1こ ごとに：お世話トークン −1（すぐ 保存）・お世話の 数 ＋1（育ち・ミッション・リセットの 数え）（{[r["sa"]["stock"] for r in res]}）')
            held = [len(r['sa']['sdp']) for r in res]
            check(held == [1, 1, 2, 3, 4] and [q[1] for q in res[4]['sa']['sdp']] == [1, 2, 5, 6], f'当たりは 玉を 落とした 瞬間に 保存（コップに 入る 前に 閉じても なくならない）（{held}・色 {[q[1] for q in res[4]["sa"]["sdp"]]}）')
            check(all(r['b']['lcd'] == 0 for r in res) and all(r['a']['lcd'] == 0 or r['a']['lcdOff'] for r in res),
                  'コップに 入る 前は 馬バレは ついて いない（前の 玉の 馬バレは 次の 玉を 落とすと 消える）')
            lc = [r['c']['lcd'] for r in res]
            check(lc == exp, f'コップに 入った 瞬間に 馬バレが その 色に つく：青・（はずれは つかない）・緑・金・虹（{lc}）')
            sd = [[n for n in r['snd'] if n.startswith('dp_uma') or n in ('dp_miss', 'dp_cup')] for r in res]
            check(sd == [['dp_cup', 'dp_uma1'], ['dp_cup', 'dp_miss'], ['dp_cup', 'dp_uma2'], ['dp_cup', 'dp_uma5'], ['dp_cup', 'dp_uma6']], f'音：コトン → 当たりは その 色の 馬バレ音（色と いっしょに）・はずれは ポスッ だけ（{sd}）')
            hs = [[h[0] for h in r['d']['holds']] for r in res]
            check(hs == [[1], [1], [1, 2], [1, 2, 5], [1, 2, 5, 6]] and all(h[1] == 'in' for h in res[4]['d']['holds']), f'当たりは「当選」の ますに 左から たまる（{hs[-1]}）')
            fin = pg.evaluate(INFO)
            check(fin['phase'] == 'wait' and fin['n'] == 5 and not fin['next'] and not pg.evaluate("() => TCDrop.tap('go')") and not pg.evaluate("() => TCDrop.tap('quit')"),
                  '5こ 落とし おわると「保留結果を見る」の かぎが あく（もう 玉は 落とせない）')
            pg.evaluate(TICK, [0.8, None]); snd_w = pg.evaluate(SES); shot(pg, 'dp_wait')
            # --- 保留結果を見る ---
            print('■ App Store版：保留結果を見る')
            pg.evaluate("() => { const S = TCApp._snd; window.__seL = []; const o = S.se.bind(S); S.se = (n, g, l) => { window.__seL.push(n.replace('tc_se_', '').replace('.m4a', '')); return o(n, g, l); }; TCDrop._t.manual = false; }")
            stage_click(pg, *geo['see']); pg.wait_for_timeout(300)
            check(pg.evaluate(INFO)['phase'] == 'res', '「保留結果を見る」を 指で 押すと はじまる')
            ops = finish_fx(pg); pg.wait_for_timeout(1200)
            e1 = pg.evaluate(INFO); s3 = pg.evaluate(ST); sl = pg.evaluate("() => window.__seL")
            check(e1['phase'] == 'end' and [h[1] for h in e1['holds']] == ['done'] * 4 and s3['dp'] == [] and s3['sdp'] == [] and s3['wal'] == w0['wal'] + 100 + 800 + 1000 and s3['tickets'] == w0['tickets'] + 1,
                  f'順に わたす：100P ＋ ルーレット 800P ＋ 特化ゾーン 1,000P ＋ チケット 1枚（財布 ＋{s3["wal"] - w0["wal"]}P・チケット ＋{s3["tickets"] - w0["tickets"]}）・保存の 保留は 空に')
            check(e1['sum'] == 1900 and e1['tk'] == 1, f'おしまいの 札の「今回の 当たり」＝＋1,900P・チケット 1枚（{e1["sum"]}・{e1["tk"]}）')
            ix = lambda n: sl.index(n) if n in sl else -1
            check(0 <= ix('piron') < ix('kyuin') < ix('rt_lever') and sl.count('kyuin') == 2 and any(n.startswith('zn_') for n in sl),
                  f'わたす ときの 音・演出は PUSH と 同じ（ピロン → キュインキュイーン → ルーレット → キュインキュイーン → 特化ゾーン → チケット）（{[n for n in sl if not n.startswith("dp_")][:14]}）')
            check(min(ops) == 0 and ops[0] == 1 and e1['op'] == 1, 'ルーレット・特化ゾーン・チケットの 演出の 間は 台を かくす（いつもの 見え方）→ おわると もどる')
            shot(pg, 'dp_end')
            check(e1['more'] and s3['stock'] == 7, f'トークンが 5こ 以上 のこって いる（{s3["stock"]}こ）→「続けてやる」「終わり」')
            # --- 続けてやる → ぜんぶ はずれ → 終わり だけ ---
            stage_click(pg, *geo['more']); pg.wait_for_timeout(500)
            i2 = pg.evaluate(INFO)
            check(i2['phase'] == 'ready' and i2['max'] == 5 and i2['n'] == 0 and i2['holds'] == [], '「続けてやる」を 指で 押すと 新しい 5こ')
            pg.evaluate("() => { TCDrop._t.manual = true; TCDrop._t.rec = []; }"); pg.evaluate(TICK, [0.6, None])
            for i in range(5): drop_ball(pg, None)
            pg.evaluate(TICK, [0.3, None]); n1 = pg.evaluate(INFO); pg.evaluate(TICK, [2.2, None]); n2 = pg.evaluate(INFO); s4 = pg.evaluate(ST)
            check(n1['phase'] == 'none' and n2['phase'] == 'end' and not n2['more'] and s4['stock'] == 2 and s4['wal'] == s3['wal'] and n2['sum'] == 0,
                  f'ぜんぶ はずれ：「ざんねん…」→ おしまいの 札（当たり なし）・トークン {s4["stock"]}こ（5こ ない）→「終わり」だけ')
            check(not pg.evaluate("() => TCDrop.tap('more')"), '「続けてやる」は 出ない・押せない')
            pg.evaluate("() => { TCDrop._t.manual = false; }"); pg.wait_for_timeout(500)
            stage_click(pg, *geo['end1']); pg.wait_for_timeout(900)
            s5 = pg.evaluate(ST)
            check(not s5['open'] and not s5['push'] and not s5['fxHold'] and s5['cares'] == w0['cares'] + 10, f'「終わり」を 指で 押すと 台を 閉じる・PUSH も 消える（お世話の あとの 抽選は すんだ）・お世話 ＋10回')
            check(pg.errs == [] and not [f for f in pg.bad if '_dp' in f], f'エラーなし・読めない ファイルなし（{pg.errs[:2]}・{pg.bad[:3]}）')

            # --- トークンが 5こ ない・途中で「投入終了」---
            print('■ App Store版：トークンが 少ない・途中で やめる・馬の 抽選の 上限')
            pg.evaluate(SETTOK, 3); pg.evaluate(PUSH_ON); pg.wait_for_timeout(900)
            stage_click(pg, *G['dp']); pg.wait_for_function("() => TCDrop.isOpen()", timeout=8000)
            pg.evaluate("() => { TCDrop._t.manual = true; TCDrop._t.rec = []; }"); pg.evaluate(TICK, [0.7, None])
            t3 = pg.evaluate(INFO); r = drop_ball(pg, {'k': 'pt', 'v': 10})
            check(t3['max'] == 3 and r['d']['phase'] == 'ready' and r['d']['n'] == 1, f'トークン 3こ：玉は 3こ まで（あと {t3["max"]}こ）')
            q1 = pg.evaluate("() => TCDrop.tap('quit')"); pg.evaluate(TICK, [0.5, None]); t4 = pg.evaluate(INFO); s6 = pg.evaluate(ST)
            check(q1 and t4['phase'] == 'wait' and s6['stock'] == 2 and len(s6['dp']) == 1, '1こ 落とした あとの「投入終了」：のこりの 玉は 落とさずに「保留結果を見る」へ（トークンは 使った 分 だけ）')
            pg.evaluate("() => TCDrop.tap('see')"); pg.evaluate(TICK, [6, "TCDrop.state.phase === 'end'"]); pg.evaluate(TICK, [0.5, None]); t5 = pg.evaluate(INFO)
            check(t5['phase'] == 'end' and not t5['more'] and t5['sum'] == 10, 'ポイントの 当たり だけ なら その まま おしまいの 札へ（＋10P）')
            pg.evaluate("() => TCDrop.tap('end')"); pg.evaluate("() => { TCDrop._t.manual = false; }"); pg.wait_for_timeout(600)

            # --- 神様馬：抽選の 上限（5回）・色 ---
            pg.evaluate("() => TCApp._t.startVisit('kamisama')"); pg.wait_for_function("() => TCCare.vinfoBox() && TCCare.S.vinfo", timeout=60000); pg.wait_for_timeout(800)
            pg.evaluate("() => { TCApp.state.rs.n = 3; }"); pg.evaluate(SETTOK, 20); pg.evaluate(PUSH_ON); pg.wait_for_timeout(900)
            stage_click(pg, *G['dp']); pg.wait_for_function("() => TCDrop.isOpen()", timeout=8000)
            pg.evaluate("() => { TCDrop._t.manual = true; TCDrop._t.rec = []; }"); pg.evaluate(TICK, [0.7, None])
            va = pg.evaluate("() => TCApp._t.PRIZES_VISIT.kamisama.find(q => q[1].k === 'rt')[1].v[0]")
            k0 = pg.evaluate(INFO); r1 = drop_ball(pg, {'k': 'rt', 'tier': 'kamisama'}); r2 = drop_ball(pg, {'k': 'zn'}); k2 = pg.evaluate(INFO)
            check(k0['max'] == 2 and r1['c']['lcd'] == 6 and r2['c']['lcd'] == 5 and k2['phase'] == 'wait' and r1['sa']['dp'][0][2] == 'kamisama',
                  f'神様馬（抽選は 5回 まで・もう 3回 使った）：玉は 2こ まで・神様馬の ルーレット＝虹・特化ゾーン＝金（あと {k0["max"]}こ・色 {[r1["c"]["lcd"], r2["c"]["lcd"]]}）')
            pg.evaluate("() => { TCDrop._t.manual = false; }")
            pg.evaluate("() => TCDrop.tap('see')"); finish_fx(pg, 240); pg.wait_for_timeout(1000); k3 = pg.evaluate(INFO)
            check(k3['phase'] == 'end' and not k3['more'] and k3['sum'] == va + 1000, f'抽選を つかい切った：トークンが のこって いても「終わり」だけ（＋{k3["sum"]}P）')
            pg.evaluate("() => TCDrop.tap('end')"); pg.wait_for_timeout(600)
            pg.wait_for_function("() => !TCApp.state.visit", timeout=60000); pg.wait_for_timeout(1500)      # 抽選を つかい切った 神様馬は 帰る
            check(pg.evaluate("() => !TCApp.state.visit && !TCDrop.isOpen()"), '台を 閉じると（抽選を つかい切った）神様馬は 帰る')
            pg.evaluate("() => TCApp._t.startVisit('maboroshi')"); pg.wait_for_function("() => TCCare.vinfoBox() && TCCare.S.vinfo && TCApp.state.visit.kind === 'maboroshi'", timeout=60000); pg.wait_for_timeout(1200)
            pg.evaluate(SETTOK, 20); pg.evaluate(PUSH_ON); pg.wait_for_timeout(900)
            stage_click(pg, *G['dp']); pg.wait_for_function("() => TCDrop.isOpen()", timeout=8000)
            pg.evaluate("() => { TCDrop._t.manual = true; TCDrop._t.rec = []; }"); pg.evaluate(TICK, [0.7, None])
            m0 = pg.evaluate(INFO); m1 = drop_ball(pg, {'k': 'rt', 'tier': 'maboroshi'})
            check(m0['max'] == 5 and m1['c']['lcd'] == 5 and 'dp_uma5' in m1['snd'], f'幻の馬の ルーレット＝金（色 {m1["c"]["lcd"]}）')
            # 台を 開いた まま タイムリミットを すぎた：その 馬の 表では もう ひけない（台を 開いて 待つ 抜け穴を 作らない）→ 保留結果を 見て 閉じると 馬は 帰る
            pg.evaluate("() => { TCApp.state.visit.until = Date.now() - 1000; }")
            l0 = pg.evaluate("() => [TCApp._t.drawLeft(), TCApp._t.dropLeft()]"); g0 = pg.evaluate(GO, [seq_for(pg, {'k': 'rt', 'tier': 'maboroshi'})]); pg.evaluate(TICK, [0.5, None]); x0 = pg.evaluate(INFO); sx = pg.evaluate(ST)
            check(l0 == [9, 0] and not g0 and x0['phase'] == 'wait' and x0['n'] == 1 and sx['stock'] == 19, f'幻の馬の タイムリミットを すぎた あと：玉は もう 落とせない（トークンは へらない）→「保留結果を見る」へ（上限の のこり {l0[0]}・落とせる 数 {l0[1]}）')
            pg.evaluate("() => { TCDrop._t.manual = false; }")
            pg.evaluate("() => TCDrop.tap('see')"); finish_fx(pg, 240); pg.wait_for_timeout(1000); x1 = pg.evaluate(INFO)
            check(x1['phase'] == 'end' and not x1['more'], 'おしまいの 札：トークンが のこって いても「終わり」だけ')
            pg.evaluate("() => TCDrop.tap('end')"); pg.wait_for_function("() => !TCApp.state.visit", timeout=60000); pg.wait_for_timeout(800)
            check(pg.evaluate("() => !TCApp.state.visit && !TCDrop.isOpen() && TCApp._t.dropLeft() === Infinity"), '台を 閉じると 幻の馬は 帰る（いつもの 馬は 上限 なし）')
            ctx.close()

            # ================= 途中で 閉じる・開き直す =================
            print('■ App Store版：途中で 閉じた とき')
            ctx, pg = page(); open_tc(pg, APP)
            pg.evaluate(SETTOK, 9); pg.evaluate(PUSH_ON); pg.wait_for_timeout(900); G = pg.evaluate("() => TCCare.PUSHG")
            stage_click(pg, *G['dp']); pg.wait_for_function("() => TCDrop.isOpen()", timeout=8000)
            pg.evaluate("() => { TCDrop._t.manual = true; TCDrop._t.rec = []; }"); pg.evaluate(TICK, [0.7, None])
            w0 = pg.evaluate(ST); drop_ball(pg, {'k': 'pt', 'v': 200})
            pg.evaluate(GO, [seq_for(pg, {'k': 'rt', 'tier': 'maboroshi'})]); pg.evaluate(TICK, [0.3, None])       # 2こめは 落ちて いる 途中
            pg.evaluate("() => { TCDrop._t.manual = false; }")
            pg.evaluate("() => TCApp.close()"); pg.wait_for_timeout(700)
            c1 = pg.evaluate("() => { const sv = JSON.parse(localStorage.getItem('tengel.tc')); return { open: TCDrop.isOpen(), dp: sv.dp.holds.map(z => [z.k, z.c]), stock: sv.stock, wal: TengelWallet.total() + TengelWallet.hold().total }; }")
            check(not c1['open'] and c1['dp'] == [['pt', 1], ['rt', 3]] and c1['stock'] == 7 and c1['wal'] == w0['wal'], f'玉が 落ちて いる 途中で 閉じる：当たり 2つは 保存に のこる・まだ わたして いない（{c1["dp"]}）')
            pg.reload(); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(600)
            pg.evaluate("() => document.querySelectorAll('.tabbar button')[2].click()"); pg.wait_for_timeout(300); pg.locator('#tcFab').click()
            pg.wait_for_function("() => window.TCDrop && TCDrop.isOpen()", timeout=90000); pg.wait_for_timeout(1500)
            r0 = pg.evaluate(INFO); geo = pg.evaluate("() => TCDrop.geo()"); shot(pg, 'dp_resume')
            check(r0['phase'] == 'wait' and [h[0] for h in r0['holds']] == [1, 3] and r0['max'] == 0 and r0['used'] == 0, f'アプリを 開き直して トレーニングセンターを 開くと、台が「保留結果を見る」から 出る（保留 {[h[0] for h in r0["holds"]]}）')
            check(not pg.evaluate("() => TCDrop.tap('go')") and not pg.evaluate("() => TCDrop.tap('quit')"), 'その ときは 玉は 落とせない（先に 受け取る）')
            stage_click(pg, *geo['see']); finish_fx(pg, 120); pg.wait_for_timeout(1000)
            r1 = pg.evaluate(INFO); s1 = pg.evaluate(ST)
            check(r1['phase'] == 'end' and s1['wal'] == w0['wal'] + 200 + 1600 and s1['dp'] == [] and s1['sdp'] == [], f'受け取る：200P ＋ ルーレット 1,600P（財布 ＋{s1["wal"] - w0["wal"]}P）・保存の 保留は 空に')
            check(r1['more'] and s1['stock'] == 7, 'トークンが 5こ 以上 あれば そのまま「続けてやる」も できる')
            pg.evaluate("() => TCDrop.tap('end')"); pg.wait_for_timeout(700); s2 = pg.evaluate(ST)
            check(not s2['open'] and s2['stock'] == 7, '「終わり」→ 閉じる（玉を 落として いない ので トークンは そのまま）')
            pg.evaluate("() => TCApp.close()"); pg.wait_for_timeout(500); pg.locator('#tcFab').click(); pg.wait_for_function("() => TCCare.on", timeout=60000); pg.wait_for_timeout(2500)
            s3 = pg.evaluate(ST)
            check(not s3['open'] and s3['wal'] == s1['wal'], 'もう一度 開いても 台は 出ない・同じ 当たりを 2回 もらえない')
            check(pg.errs == [], f'エラーなし（{pg.errs[:2]}）')
            ctx.close()

            # ================= 絵が 読めない とき =================
            print('■ App Store版：台の 絵が 読めない とき')
            ctx, pg = page(); ctx.route('**/tc_dp.json', lambda r: r.fulfill(status=404, body=''))
            pg.goto(APP); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(600)
            pg.evaluate("""() => { const s = JSON.parse(localStorage.getItem('tengel.tc') || 'null') || { v: 1 }; s.dp = { holds: [{ k: 'pt', v: 300, id: 'tc-dp-test-1', c: 1 }, { k: 'tk', n: 2, id: 'tc-dp-test-2', c: 6 }] }; localStorage.setItem('tengel.tc', JSON.stringify(s)); }""")
            pg.reload(); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(600)
            w0 = pg.evaluate("() => TengelWallet.total() + TengelWallet.hold().total")
            pg.evaluate("() => document.querySelectorAll('.tabbar button')[2].click()"); pg.wait_for_timeout(300); pg.locator('#tcFab').click()
            pg.wait_for_function("() => window.TCApp && TCApp.state && window.TCCare && TCCare.on && !document.querySelector('#tcOv .tcld')", timeout=90000); pg.wait_for_timeout(2500)
            n0 = pg.evaluate("() => ({ ready: TCDrop.ready(), open: TCDrop.isOpen(), dp: (TCApp.state.dp && TCApp.state.dp.holds || []).length, tk: TCApp.state.tickets || 0, wal: TengelWallet.total() + TengelWallet.hold().total, msg: document.querySelector('#tcOv .tcmsg').textContent })")
            check(not n0['ready'] and not n0['open'] and n0['dp'] == 0 and n0['wal'] == w0 + 300 and n0['tk'] >= 2 and '300P' in n0['msg'] and 'チケット 2枚' in n0['msg'],
                  f'台の 絵が 読めない：残って いた 当たり（300P・チケット 2枚）は その場で わたす（{n0["msg"]}）')
            pg.evaluate(SETTOK, 6); pg.evaluate(PUSH_ON); pg.wait_for_timeout(900); G = pg.evaluate("() => TCCare.PUSHG")
            stage_click(pg, *G['dp']); pg.wait_for_timeout(600)
            n1 = pg.evaluate(ST)
            check(not n1['open'] and n1['push'] and n1['stock'] == 6, '入口は 出ない・その 所を 押しても 何も おきない（PUSH は いつも どおり）')
            gd = pg.evaluate("() => { TCGuide.open(document.querySelector('#tcOv .tcst'), { anim: false }); const t = [...document.querySelectorAll('#tcg .sec h3')].map(e => e.textContent); TCGuide.close(); return t; }")
            check(not any('お世話チャレンジ' in t for t in gd) and len(gd) >= 12, f'説明書にも「お世話チャレンジ」の 項目は 出さない（項目 {len(gd)}）')
            ctx.close()

            # ================= 説明書 =================
            print('■ 説明書')
            ctx, pg = page(); open_tc(pg, APP)
            gd = pg.evaluate("""() => { TCGuide.open(document.querySelector('#tcOv .tcst'), { anim: false }); const sec = [...document.querySelectorAll('#tcg .sec')].find(e => e.querySelector('h3').textContent.includes('お世話チャレンジ'));
              const r = sec ? { rows: [...sec.querySelectorAll('table[data-tab=tone] tr')].map(tr => [tr.dataset.c, tr.children[1].textContent]), txt: sec.textContent, idx: [...document.querySelectorAll('#tcg .sec h3')].map(e => e.textContent.slice(1)) } : null; TCGuide.close(); return r; }""")
            want_rows = [['青', '10P〜300P'], ['緑', 'ルーレット（800P か 1600P）'], ['紫', 'ルーレット（1600P か 3200P）'], ['赤', 'ルーレット（3200P か 6400P）'], ['金', '幻の馬のルーレット・ポイント特化ゾーン'], ['虹', '神様馬のルーレット・チケット']]
            check(gd is not None and gd['rows'] == want_rows, f'説明書「お世話チャレンジ」：馬バレの 色の 表（{gd and gd["rows"]}）')
            check(gd is not None and all(x in gd['txt'] for x in ['玉を落とす台で抽選できるよ', 'トークンを1つ使って', '1回で5こまで', 'PUSHとまったく同じ', '「保留結果を見る」で順に受け取ろう', '「続けてやる」か「終わり」', '玉1こ＝トークン1つ＝お世話1回', 'たまった当たりはなくならないよ'])
                  and gd['idx'].index('お世話チャレンジ') == gd['idx'].index('お世話のあとのPUSH') + 1, '説明書の 文：入口・玉 1こ＝トークン 1つ・5こ まで・確率は PUSH と 同じ・保留結果・続けてやる／終わり・途中で 閉じても なくならない（PUSH の 項目の すぐ 下）')
            if SHOT:
                pg.evaluate("() => { TCGuide.open(document.querySelector('#tcOv .tcst'), { anim: false }); [...document.querySelectorAll('#tcg .sec h3')].find(e => e.textContent.includes('お世話チャレンジ')).scrollIntoView(); }"); pg.wait_for_timeout(400); shot(pg, 'dp_guide'); pg.evaluate("() => TCGuide.close()")

            check(pg.errs == [], f'エラーなし（{pg.errs[:2]}）')
            ctx.close()

            # ================= テスト版：道具箱 =================
            print('■ テスト版：道具箱の「④ お世話チャレンジ」')
            ctx, pg = page(); open_tc(pg, TESTB)
            pg.evaluate("() => document.querySelector('#tcOv [data-tc=test]').click()"); pg.wait_for_timeout(500)
            tb = pg.evaluate("() => { const s = document.querySelector('#tct [data-sec=drop]'); return s ? { h: s.querySelector('h3').textContent, btn: [...s.querySelectorAll('.ttb')].map(b => b.textContent) } : null; }")
            check(tb is not None and tb['h'].startswith('④ お世話チャレンジ') and len(tb['btn']) == 13 and tb['btn'][0] == 'くじどおりで 開く' and '青（100P）' in tb['btn'] and '虹（チケット）' in tb['btn']
                  and '青 → 緑 → 紫 → 赤 → 金' in tb['btn'] and any('幻の馬の ルーレット' in t for t in tb['btn']) and any('神様馬の ルーレット' in t for t in tb['btn']), f'道具箱に ④（ボタン {tb and len(tb["btn"])}こ）')
            if SHOT: pg.evaluate("() => document.querySelector('#tct [data-sec=drop]').scrollIntoView()"); pg.wait_for_timeout(300); shot(pg, 'dp_tool')
            pg.evaluate("() => { const b = [...document.querySelectorAll('#tct [data-sec=drop] .ttb')].find(b => b.textContent === '青 → 緑 → 紫 → 赤 → 金'); b.click(); }")
            pg.wait_for_function("() => TCDrop.isOpen()", timeout=20000)
            pg.evaluate("() => { TCDrop._t.manual = true; TCDrop._t.rec = []; }"); pg.evaluate(TICK, [0.7, None])
            cols = []
            for i in range(5):
                pg.evaluate("() => TCDrop.tap('go')"); pg.evaluate(TICK, [8, "TCDrop.state.ball && TCDrop.state.ball.inT != null"]); pg.evaluate(TICK, [0.3, None]); cols.append(pg.evaluate(INFO)['lcd'])
                pg.evaluate(TICK, [6, "TCDrop.state.phase !== 'fall'"]); pg.evaluate(TICK, [0.2, None])
            st_t = pg.evaluate(ST)
            check(cols == [1, 2, 3, 4, 5] and [q[0] for q in st_t['dp']] == ['pt', 'rt', 'rt', 'rt', 'zn'], f'「青 → 緑 → 紫 → 赤 → 金」：お世話を とばして 台が 開く・玉の 順に その 色（{cols}・中身 {[q[0] for q in st_t["dp"]]}）')
            pg.evaluate("() => { TCDrop._t.manual = false; TCDrop.close(); }"); pg.wait_for_timeout(500)
            pg.evaluate("() => { for (const z of (TCApp.state.dp && TCApp.state.dp.holds || []).slice()) TCApp._t.give(z); TCCare.pushDone(TCCare.S.lastT); }"); pg.wait_for_timeout(600)
            r6 = pg.evaluate("async () => await TCApp.test.drop([6, 6, 6], true)"); pg.wait_for_function("() => TCDrop.isOpen()", timeout=20000)
            pg.evaluate("() => { TCDrop._t.manual = true; }"); pg.evaluate(TICK, [0.7, None]); pg.evaluate("() => TCDrop.tap('go')")
            pg.evaluate(TICK, [8, "TCDrop.state.ball && TCDrop.state.ball.inT != null"]); pg.evaluate(TICK, [0.3, None]); c6 = pg.evaluate(INFO)['lcd']
            pg.evaluate("() => { TCDrop._t.manual = false; TCDrop.close(); }"); pg.wait_for_timeout(500)
            pg.evaluate("() => { for (const z of (TCApp.state.dp && TCApp.state.dp.holds || []).slice()) TCApp._t.give(z); TCCare.pushDone(TCCare.S.lastT); }"); pg.wait_for_timeout(600)
            lot = pg.evaluate("""() => { const R = Math.random; Math.random = () => 0.995; try { return TCApp._t.draw(); } finally { Math.random = R; } }""")
            check(r6 == 'ok' and c6 == 6 and lot is None, f'決めた 結果（虹 3こ）の うち 1こ だけ 落として 閉じる → のこりは 消える（あとの PUSH は いつもの くじ）（色 {c6}・{lot}）')
            r = pg.evaluate("async () => await TCApp.test.drop([{ k: 'rt', tier: 'kamisama', v: [2000, 4000] }], true, 'kamisama')")
            pg.wait_for_function("() => TCDrop.isOpen()", timeout=60000)
            pg.evaluate("() => { TCDrop._t.manual = true; }"); pg.evaluate(TICK, [0.7, None]); pg.evaluate("() => TCDrop.tap('go')")
            pg.evaluate(TICK, [8, "TCDrop.state.ball && TCDrop.state.ball.inT != null"]); pg.evaluate(TICK, [0.3, None]); kc = pg.evaluate(INFO)['lcd']; kv = pg.evaluate("() => TCApp.state.visit && TCApp.state.visit.kind")
            check(r == 'ok' and kc == 6 and kv == 'kamisama', f'「✨ 虹（神様馬の ルーレット）」：神様馬が 来て から 台が 開く → 虹（{r}・{kv}・色 {kc}）')
            pg.evaluate("() => { TCDrop._t.manual = false; TCDrop.close(); }"); pg.wait_for_timeout(300)
            check(pg.errs == [], f'エラーなし（{pg.errs[:2]}）')
            ctx.close(); b.close()
finally:
    srv.terminate()
print('\n' + ('❌ ' + str(len(fails)) + ' こ 失敗：\n  ' + '\n  '.join(fails) if fails else '✅ ぜんぶ OK'))
sys.exit(1 if fails else 0)
