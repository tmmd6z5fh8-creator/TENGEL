# トレーニングセンターの「激馬熱馬」（第4.175版）の テスト
#   まさちゃん 2026/11/15 13:56「トレーニングセンターに激馬熱馬当選を追加　1/299999 ・当選時、馬バレの画像一枚目 ・馬バレ保留の画像二枚目
#     ・新しいプチュン一個目の動画と同じ速度、線の細さで線を赤と金で作成 ・演出時に使用する背景、三枚目 ・演出時に使う40000Pの3D一個目ファイル(演出は2秒程度)
#     ボタン抽選演出：1/299999に抽選の場合、当選した瞬間にいきなり画面プチュンして、ブラックアウト、天国のような画面に切り替わり、上から40000Pと書かれた立体の文字が降りてきて、
#       40、00、0Pでそれぞれを色々な角度から映すカットが入って、テデーンとデカ文字で40000P獲得と出てきて終わり！
#     パチンコ抽選演出：1/299999に抽選した瞬間に馬バレのところがプチュンして、激馬熱馬が表示される　保留結果を見る、で天国のような画面に切り替わり、…テデーンとデカ文字で40000P獲得と出てきて終わり！」
#   14:04「プチュンの音は、動画の音にかなり近く作成して！ パチンコ抽選の当選時、プチュンしたら激馬熱馬の馬バレを表示する時、虹色当選と同じ音を使用して！」
#   14:58「これ40000Pの全体が見える前に、40、00、0Pのカットイン入れて！全体が見える時は背景切れてもいいからもっとアップにして迫力ある演出にして！」
#   ・中身の 見くらべ（絵が なくても：CI）：確率 1/299999・40,000P・時刻の 数字（コード・音を 作る 道具・動画を 作る 道具が 同じ）・Web版には 入らない
#   ・App Store版（TARGET=app）：くじ・PUSH（プチュン → 真っ暗 → 天国の 動画 → テデーンと「40000P獲得」→ 40,000P）・途中で 閉じた とき・
#     お世話チャレンジ（馬バレの 丸が プチュン → 虹と 同じ 音で 激馬熱馬 → 保留 → 保留結果を見る → 天国）・途中で 閉じた とき・「演出を控えめにする」・動画や 絵が ない とき
#   python3 test_tc_geki.py   （ios/tc_assets/ に 激馬熱馬の 動画（tc_gk_film2.mp4）と 台の 絵が ある とき だけ 画面の テスト。ない とき（CI）は 中身の 見くらべ だけ）
#   光の 点めつは test_tc_geki_flash.py（PUSH：コマを 写すので 時間が かかる）と test_tc_drop_flash.py（馬バレの 丸）
import json, os, re, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
from toys_for_test import open_toys      # 第4.212版：おもちゃ（TENGERカードバトル・お世話チャレンジ）を 0P で 解放した ことに する（テスト用）
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv_tc'); PORT = 8814; APP = f'http://localhost:{PORT}/APP/'; TESTB = f'http://localhost:{PORT}/TEST/'
SHOT = os.environ.get('SHOT')          # 画面を 写す フォルダ（見る 用）
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, TARGET='app'))
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'TEST')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, TARGET='app', TENGEL_TEST='1'))
from assets_dir import adir
TCA = adir('tc_assets')
GKF = ['tc_gk_film2.mp4', 'tc_gk_end2.webp', 'tc_se_gk_pchun.m4a', 'tc_se_gk_heaven.m4a', 'tc_se_gk_tedeen.m4a', 'tc_dp_uma7.webp', 'tc_dp_hold7.webp']      # 激馬熱馬の 素材 7こ
HAVE = os.path.isfile(os.path.join(TCA, 'tc_dp.json')) and len(os.listdir(TCA)) > 100 and all(os.path.isfile(os.path.join(TCA, f)) for f in GKF)
for d in ('APP', 'TEST'):
    pth = os.path.join(SRV, d, 'index.html'); html = open(pth, encoding='utf8').read()
    open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
    if HAVE:
        for f in os.listdir(TCA): shutil.copy(os.path.join(TCA, f), os.path.join(SRV, d, f))
if not HAVE: print('※ 激馬熱馬の 素材（ios/tc_assets の tc_gk_film2.mp4 など）が ない ので、中身の 見くらべ だけ')
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


# 鳴らした 音と BGM の 切りかえを 時刻（秒）つきで おぼえる（アプリの 音の 口を 包む：開いた あと 1回）
REC = """() => { if (window.__rec) return; const S = TCApp._snd, se0 = S.se.bind(S), bgm0 = S.bgm.bind(S), R = window.__rec = [];
  S.se = (name, gain, at) => { R.push([performance.now() / 1000, name.replace('tc_se_', '').replace('.m4a', '')]); return se0(name, gain, at); };
  S.bgm = name => { R.push([performance.now() / 1000, 'bgm:' + (name === null ? 'null' : name)]); return bgm0(name); }; }"""
RECS = "() => { const a = window.__rec.slice(); window.__rec.length = 0; return a; }"


def open_tc(pg, url, wait_drop=True):
    pg.goto(url); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(600)
    open_toys(pg, ('drop',))      # 第4.212版：お世話チャレンジは おもちゃ（3,000P で 解放）→ 解放ずみに する
    pg.evaluate("() => document.querySelectorAll('.tabbar button')[2].click()"); pg.wait_for_timeout(300)
    pg.locator('#tcFab').click()
    pg.wait_for_function("() => window.TCApp && TCApp.state && window.TCCare && TCCare.on && !document.querySelector('#tcOv .tcld')", timeout=90000); pg.wait_for_timeout(1000)
    if wait_drop: pg.wait_for_function("() => window.TCDrop && TCDrop.ready()", timeout=30000)
    pg.evaluate(REC)


def reopen(pg, wait_drop=True):       # アプリを 閉じて 開き直した ことに する（ページを 読み直して トレーニングセンターを ひらく）
    pg.reload(); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(600)
    pg.evaluate("() => document.querySelectorAll('.tabbar button')[2].click()"); pg.wait_for_timeout(300)
    pg.locator('#tcFab').click()
    pg.wait_for_function("() => window.TCApp && document.querySelector('#tcOv.on') && !document.querySelector('#tcOv .tcld')", timeout=90000); pg.wait_for_timeout(1200)
    if wait_drop: pg.wait_for_function("() => window.TCDrop && TCDrop.ready()", timeout=30000)
    pg.evaluate(REC)


# ---- ページの 中で 使う 小さな 道具 ----
INFO = "() => TCDrop.info()"
ST = """() => { const s = TCApp.state, sv = JSON.parse(localStorage.getItem('tengel.tc')) || {}, S = TCCare.S; return { stock: S.stock, sstock: sv.stock, cares: s.cares, total: s.total || 0, tickets: s.tickets || 0,
  dp: (s.dp && s.dp.holds || []).map(z => [z.k, z.c]), sdp: (sv.dp && sv.dp.holds || []).map(z => [z.k, z.c]), wal: TengelWallet.total() + TengelWallet.hold().total,
  push: !!(S.push && S.push.hideT == null), fxHold: !!S.fxHold, open: TCDrop.isOpen(), pend: s.pend ? [s.pend.k, s.pend.v, s.pend.id] : null, spend: sv.pend ? [sv.pend.k, sv.pend.v, sv.pend.id] : null,
  ev: TengelWallet.events().filter(e => /激馬熱馬/.test(e.what || '')).map(e => [e.amount, e.what, e.id]) }; }"""
SETTOK = "n => { const S = TCCare.S, s = TCApp.state; S.stock = n; S.stockShow = n; s.stock = n; s.stockAt = Date.now(); S.high = 0; s.high = 0; }"
PUSH_ON = "() => { const S = TCCare.S; if (!(S.push && S.push.hideT == null)) TCCare.pushShow(S.lastT + 0.05); }"
# その 当たりが 出る くじの 数（いまの 馬の 表の 中で、その 当たりの 幅の まん中。高確ゾーンは なしで）
RND_FOR = """(want) => { const T = TCApp._t, tab = TCApp.state.visit ? T.PRIZES_VISIT[TCApp.state.visit.kind] : T.PRIZES; let a = 0;
  for (const [p, z] of tab) { if (z.k === want.k) return a + p / 2; a += p; } return null; }"""
# PUSH を 本物の 指の 出来事（pointerdown：お世話の キャンバスへ）で 押す。その 間 だけ くじ（Math.random）を 決めた 数の 列に する。返り値＝押した その 瞬間の ようす
PUSHJS = """([seq]) => { const R = Math.random, q = (seq || []).slice(); let last = q.length ? q[q.length - 1] : 0.995; TCCare.S.high = 0; TCApp.state.high = 0;
  const G = TCCare.PUSHG, st = document.querySelector('#tcOv .tcst'), cv = st.querySelector('.tco'), r = st.getBoundingClientRect();
  const o = { bubbles: true, cancelable: true, clientX: r.left + G.x / 1052 * r.width, clientY: r.top + G.y / 1657 * r.height, pointerId: 7, pointerType: 'touch', isPrimary: true };
  const t = performance.now() / 1000;
  Math.random = () => (q.length ? (last = q.shift()) : last);
  try { cv.dispatchEvent(new PointerEvent('pointerdown', o)); } finally { Math.random = R; }
  cv.dispatchEvent(new PointerEvent('pointerup', o));
  const s = TCApp.state, sv = JSON.parse(localStorage.getItem('tengel.tc')) || {}, k = TCFX.gkState, gk = st.querySelector('.tcgk');
  return { t, res: TCCare.S.push ? TCCare.S.push.res : null, pend: s.pend ? [s.pend.k, s.pend.v] : null, spend: sv.pend ? [sv.pend.k, sv.pend.v, sv.pend.id] : null, stock: TCCare.S.stock, sstock: sv.stock,
    on: !!st.querySelector('.tcfx.on'), gk: k ? { calm: k.calm, puchun: k.puchun } : null, el: gk ? [gk.style.opacity, gk.querySelectorAll('video').length, gk.nextElementSibling ? gk.nextElementSibling.className.split(' ')[0] : ''] : null,
    rec: window.__rec.slice() }; }"""
GO = """([seq]) => { const R = Math.random, q = (seq || []).slice(); let last = q.length ? q[q.length - 1] : 0.995; TCCare.S.high = 0; TCApp.state.high = 0;
  Math.random = () => (q.length ? (last = q.shift()) : last);
  try { return TCDrop.tap('go'); } finally { Math.random = R; } }"""
# 台の 時計を 手で 進める（1/60秒ずつ）。cond（文字列の 式）が 本当に なったら そこで 止まる。返り値＝進めた 秒
TICK = """async ([sec, cond]) => { const T = TCDrop._t, f = cond ? new Function('return (' + cond + ')') : null; let n = 0;
  for (; n < Math.round(sec * 60); n++) { if (f && f()) break; if (!T.tick(1 / 60)) break; await null; } return n / 60; }"""
DREC = "() => TCDrop._t.rec.map(q => [q[0], q[1]])"      # 台が 鳴らした 音（台の 時計の 時刻・名前）
# 激馬熱馬の 演出の ようす：場面（mode）・天国が 出た 時（hv）・デカ文字が 出た 時（textAt）＝演出の はじめから 数えた 秒／幕（.tcgk）・動画・さいごの コマの 絵
GKST = """() => { const k = TCFX.gkState, st = document.querySelector('#tcOv .tcst'), el = st.querySelector('.tcgk'), v = el && el.querySelector('video'), im = el && el.querySelector('img');
  return { on: !!st.querySelector('.tcfx.on'), k: k ? { calm: k.calm, puchun: k.puchun, mode: k.mode, hv: k.hv, textAt: k.textAt } : null, now: performance.now() / 1000,
    el: el ? +el.style.opacity : null, v: v ? { t: v.currentTime, w: v.videoWidth, h: v.videoHeight, d: v.duration, paused: v.paused, ended: v.ended, muted: v.muted, inl: v.playsInline, err: v.error ? v.error.code : 0 } : null,
    im: im ? { o: +im.style.opacity, w: im.naturalWidth, h: im.naturalHeight } : null, n: st.querySelectorAll('.tcgk').length }; }"""
# 演出の キャンバス（.tcfx）の 色を 数える：金の 字（黄色〜金）・赤い ふち・黒（不透明）の 割合（y0〜y1：高さの 割合）
FXPX = """([y0, y1]) => { const cv = document.querySelector('#tcOv .tcfx'), g = cv.getContext('2d'), a = Math.round(cv.height * y0), b = Math.round(cv.height * y1), d = g.getImageData(0, a, cv.width, b - a).data;
  let gold = 0, red = 0, black = 0, any = 0, x0 = 1e9, x1 = -1; const N = d.length / 4;
  for (let i = 0; i < d.length; i += 4) { const R = d[i], G = d[i + 1], B = d[i + 2], A = d[i + 3], x = (i / 4) % cv.width; if (A > 20) any++;
    if (A > 200 && R > 235 && G > 170 && B < 150) gold++; if (A > 200 && R > 130 && R < 190 && G < 40 && B < 40) { red++; if (x < x0) x0 = x; if (x > x1) x1 = x; } if (A > 245 && R < 6 && G < 6 && B < 6) black++; }
  return { gold: gold / N, red: red / N, black: black / N, any: any / N, x0: x0 / cv.width, x1: x1 / cv.width }; }"""      # x0〜x1＝赤い ふち（字の はし）の 左右（紙ふぶきにも 金色が ある ので 字の はしは 赤で 見る）
# 台の 馬バレの 丸の 中の 色：まん中・線の 上（左へ 半径の 0.6）・線の 外（上へ 半径の 0.6）・丸の 中の 平均の 明るさ
LENS = """() => { const cv = document.querySelector('#tcOv canvas.tcdp'), g = cv.getContext('2d'), k = cv.width / 1052, [X, Y, Rr] = TCDrop.geo().lcd, px = (x, y) => [...g.getImageData(Math.round(x * k), Math.round(y * k), 1, 1).data].slice(0, 3);
  const r = Math.floor(Rr * 0.8 * k), d = g.getImageData(Math.round(X * k) - r, Math.round(Y * k) - r, r * 2, r * 2).data; let s = 0, n = 0;
  for (let j = 0; j < r * 2; j++) for (let i = 0; i < r * 2; i++) { if ((i - r) * (i - r) + (j - r) * (j - r) > r * r) continue; const o = (j * r * 2 + i) * 4; s += 0.2126 * d[o] + 0.7152 * d[o + 1] + 0.0722 * d[o + 2]; n++; }
  const lm = c => 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]; let on = [0, 0, 0];
  for (let j = -2; j <= 2; j++) { const c = [...g.getImageData(Math.round((X - Rr * 0.6) * k), Math.round(Y * k) + j, 1, 1).data].slice(0, 3); if (lm(c) > lm(on)) on = c; }
  return { c: px(X, Y), on, off: px(X, Y - Rr * 0.6), mean: s / n }; }"""      # on＝線の 上（左へ 半径の 0.6：その 列の 上下 2画素で いちばん 明るい 所。線は 細い）
LAMP = "() => { const S = TCDrop.state, L = S && S.lcd; return { c: L ? L.c : -1, t0: L ? L.t0 : null }; }"
FX_ON = "() => !!document.querySelector('#tcOv .tcfx.on')"
CALM = "c => TengelFx.set({ calm: !!c })"


def fx_tap(pg):                        # 演出の 画面（.tcfx）の まん中より 少し 下を タップ
    q = pg.evaluate("() => { const r = document.querySelector('#tcOv .tcfx').getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; }")
    pg.mouse.click(q[0] + q[2] / 2, q[1] + q[3] * 0.62)


def recs(pg):
    return [(round(t, 3), n) for t, n in pg.evaluate(RECS)]


def at(rec, name, last=False):         # その 音が 鳴った 時刻（ない ときは None）
    ts = [t for t, n in rec if n == name]
    return (ts[-1] if last else ts[0]) if ts else None


def geki_run(pg, tap=True, limit=40):
    """PUSH の あと：激馬熱馬の 演出が 進むのを 見て おく → { hv, text, close, taps… }。tap＝False なら 押さずに 自分で とじるのを 待つ"""
    out = {}
    pg.wait_for_function("() => { const k = TCFX.gkState; return !!(k && k.hv != null); }", timeout=20000); out['hv'] = pg.evaluate(GKST)
    pg.wait_for_timeout(350); out['hv2'] = pg.evaluate(GKST)
    # デカ文字が 出た その 場で（ページの 中で 待って）すぐ タップ：まだ とじない（着いて から 1.1秒 たつ まで）
    early = pg.evaluate("""async (tap) => { const t0 = performance.now(); while (performance.now() - t0 < 25000) { const k = TCFX.gkState; if (k && k.textAt != null) break; await new Promise(r => requestAnimationFrame(r)); }
      const k = TCFX.gkState, cv = document.querySelector('#tcOv .tcfx'), r = cv.getBoundingClientRect(), mode = k && k.mode, v = document.querySelector('#tcOv .tcgk video'), vt = v ? v.currentTime : null;
      if (tap) cv.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, cancelable: true, clientX: r.left + r.width / 2, clientY: r.top + r.height * 0.6, pointerId: 5, pointerType: 'touch', isPrimary: true }));
      return { mode, vt, now: performance.now() / 1000, ok: !!(k && k.textAt != null) }; }""", tap)
    out['early'] = early
    pg.wait_for_timeout(450); out['text'] = pg.evaluate(GKST); out['px'] = pg.evaluate(FXPX, [0.66, 1.0]); out['px_top'] = pg.evaluate(FXPX, [0.0, 0.6])
    if SHOT: os.makedirs(SHOT, exist_ok=True); pg.screenshot(path=os.path.join(SHOT, f'gk_telop_{len(os.listdir(SHOT))}.png'))
    if tap:
        pg.wait_for_function("t => performance.now() / 1000 > t + 1.45", arg=early['now'], timeout=10000)      # 着いて（0.17秒）から 1.1秒 より あと
        out['before'] = pg.evaluate(GKST); fx_tap(pg); out['tapAt'] = pg.evaluate("() => performance.now() / 1000")
    t0 = time.time(); pg.wait_for_function("() => !document.querySelector('#tcOv .tcfx.on')", timeout=limit * 1000)
    out['closed'] = pg.evaluate("() => performance.now() / 1000"); out['wait'] = time.time() - t0
    pg.wait_for_timeout(700); out['after'] = pg.evaluate(GKST)
    return out


try:
    # ---------- 中身の 見くらべ（絵が なくても）----------
    print('■ 中身')
    src = {n: open(os.path.join(W, 'tc', n), encoding='utf8').read() for n in ('tc_fx.js', 'tc_drop.js', 'tc_app.js', 'tc_care.js', 'tc_guide.js', 'tc_test.js')}
    bundle = open(os.path.join(SRV, 'APP', 'tc_bundle.js'), encoding='utf8').read(); bundle_t = open(os.path.join(SRV, 'TEST', 'tc_bundle.js'), encoding='utf8').read()
    web = open(os.path.join(W, 'tengel3.html'), encoding='utf8').read() if os.path.exists(os.path.join(W, 'tengel3.html')) else ''
    a, f, d = src['tc_app.js'], src['tc_fx.js'], src['tc_drop.js']
    check('const GEKI = { d: 299999, v: 40000 };' in a and a.count("[1 / GEKI.d, { k: 'gk' }]") == 3 and a.index("[1 / GEKI.d, { k: 'gk' }],") < a.index('[1 / ZONE.d,'),
          '激馬熱馬：確率 1/299999・40,000P。くじの 表（いつもの 馬・幻の馬・神様馬）の はじめの 行に 1つずつ')
    check("if (z.k === 'gk') z.v = GEKI.v;" in a and "else if (z.k === 'gk') { v = GEKI.v; grant(v, 'トレーニングセンターの 激馬熱馬', z.id); }" in a,
          'わたす ポイントは いつも 40,000P（保存の 中の 数字を 使わない）・台帳には「トレーニングセンターの 激馬熱馬」')
    gk = re.search(r"const GK = \{[^}]*line: ([0-9.]+), dim: ([0-9.]+), dark: ([0-9.]+), darkNo: ([0-9.]+), calm: ([0-9.]+), fade: ([0-9.]+), len: ([0-9.]+), text: (\d+) / (\d+), land: ([0-9.]+)", f)
    pc = re.search(r'const PC_LINE = ([0-9.]+), PC_DARK = ([0-9.]+), PC_DIM = ([0-9.]+), PC_CALM = ([0-9.]+);', d)
    sx = open(os.path.join(W, 'kisekae', 'tc', 'snd', 'sfx_geki.py'), encoding='utf8').read(); fm = open(os.path.join(W, 'kisekae', 'tc', 'geki_film.py'), encoding='utf8').read()
    s_len = re.search(r'^PCHUN_LEN = ([0-9.]+)', sx, re.M); s_film = re.search(r'^FILM = dict\(cuts=\((\d+) / 30, (\d+) / 30, (\d+) / 30\), text=(\d+) / 30, len=([0-9.]+)\)', sx, re.M)
    f_len = re.search(r'^FPS, LEN, W, H = (\d+), ([0-9.]+), (\d+), (\d+)', fm, re.M); f_cut = re.search(r'^CUT_F = \((\d+), (\d+), (\d+)\)', fm, re.M); f_txt = re.search(r'^TEXT_F = (\d+)', fm, re.M)
    ok_all = all(x is not None for x in (gk, pc, s_len, s_film, f_len, f_cut, f_txt))
    check(ok_all, '時刻の 数字が 読める（tc_fx.js の GK・tc_drop.js の PC_…・sfx_geki.py・geki_film.py）')
    if ok_all:
        G_ = [float(x) for x in gk.groups()]; P_ = [float(x) for x in pc.groups()]
        check(G_[0] == P_[0] == 0.243 and G_[1] == P_[2] == 0.043 and G_[2] == P_[1] == float(s_len.group(1)) == 1.67 and G_[4] == P_[3] == 0.4,
              f'プチュン：線が 消える まで 0.243秒・はじめの 0.043秒 だけ 明るい・音が 切れる 1.67秒で 次へ（PUSH と 馬バレの 丸・音を 作る 道具が 同じ 数字：{G_[:3]}・{P_}・{s_len.group(1)}）')
        check(G_[6] == float(s_film.group(5)) == float(f_len.group(2)) == 2.4 and int(f_len.group(1)) == 30 and (int(f_len.group(3)), int(f_len.group(4))) == (1170, 1842)
              and [int(x) for x in f_cut.groups()] == [int(x) for x in s_film.groups()[:3]] == [18, 32, 45] and int(gk.group(8)) == int(s_film.group(4)) == int(f_txt.group(1)) == 59 and int(gk.group(9)) == 30,
              '天国の 動画：2.4秒・30コマ／秒・1170×1842。カット 0.6秒（「40」→「00」）・1.07秒（→「0P」）・1.5秒（→ ぜんぶ）・デカ文字 1.97秒（コード・音・動画を 作る 道具が 同じ 数字）')
        gkl = eval(re.search(r'const GKL = (\[\[.*?\]\]);', f).group(1))
        check(gkl[0][:2] == [0, 48] and gkl[-1][0] == G_[0] and [q[0] for q in gkl] == sorted(q[0] for q in gkl) and all(gkl[i][1] >= gkl[i + 1][1] and gkl[i][3] >= gkl[i + 1][3] for i in range(len(gkl) - 1)) and gkl[3][1] == 9 and gkl[-1][3] == 0,
              f'プチュンの 線（見本の 動画を 測った 形）：太さ 48 → 28 → 11 → 9（横幅 582 の とき）と 細く なって・明るさは 下がる だけ・0.243秒で 消える（{[q[:2] for q in gkl]}）')
    check("se('dp_umb' + Math.min(c, 6));" in d and "later(WIN_AT, () => (b.c === 7 ? gekiPc(b) : reveal(b)));" in d and "if (!cm) se('gk_pchun');" in d and 'later(dark, () => reveal(b));' in d,
          'お世話チャレンジ：激馬熱馬（7）は 馬バレの 丸が プチュン → 音が 切れたら 虹と 同じ 音（dp_umb6）で 激馬熱馬の 絵（まさちゃん 14:04）')
    check('if (pcOn) se(o, GK.sePc, 1, 0);' in f and 'if (!calm) gkWake(gk);' in f and "if (mode === 'film' && !hvSe && gk.v.currentTime > 0) { hvSe = true; se(o, GK.seHv, 1, 0); }" in f
          and "if (mode === 'film' && mv == null && gk.v.currentTime > 0.02) { mv = u; R.mv = u; }" in f and "if (mode === 'film' && mv == null && (gk.dead || u > hv + GK.wait)) { mode = 'still'; gk.im.style.opacity = '1'; }" in f
          and "if (mode === 'film' && mv != null && textAt == null && u > mv + GK.text + GK.stall) { mode = 'still'; gk.im.style.opacity = '1'; }" in f and 'wait: 1.0, stall: 0.8' in f,
          '動画：はじめに 起こして おく（PUSH は 指の 中・「保留結果を見る」からも）・流れはじめるのを 1.0秒まで 待つ・天国の 音は 動画が 動きはじめた 時・途中で 止まったら（動きはじめて から 字の 時刻 ＋ 0.8秒）さいごの コマの 絵に かえて 先へ')
    check("z.k === 'gk' ? 7 :" in a and "const pc = !z.c;" in a and "TCFX.geki(cvFx, { v: GEKI.v, se: SND.se, puchun: pc })" in a and "finally { SND.bgm(null); got = give(z);" in a,
          'PUSH＝プチュン あり・「保留結果を見る」から（色 z.c が ある）＝プチュン なし。演出が おわったら（途中で 止まっても）40,000P を わたす')
    check("const GEKI_SE = ['tc_se_gk_pchun.m4a', 'tc_se_gk_heaven.m4a', 'tc_se_gk_tedeen.m4a'];" in a and all(n in f for n in ("sePc: 'tc_se_gk_pchun.m4a'", "seHv: 'tc_se_gk_heaven.m4a'", "seTd: 'tc_se_gk_tedeen.m4a'", "film: 'tc_gk_film2.mp4'", "end: 'tc_gk_end2.webp'")),
          '音 3つ（プチュン・天国・テデーン）と 動画・さいごの コマの 絵の 名前')
    check('tc_gk_film2.mp4' in bundle and '激馬熱馬' in bundle and 'window.TCFX = TCFX' in bundle and 'gkLine' in bundle, 'アプリの 束（tc_bundle.js）に 激馬熱馬の 演出が 入って いる')
    check('激馬熱馬（PUSH で プチュン' in bundle_t and '激馬熱馬（PUSH で プチュン' not in bundle, 'テスト版の 道具箱の「激馬熱馬」の ボタンは テスト版 だけ')
    check('tc_gk' not in web and '激馬熱馬' not in web and 'gkLine' not in web, 'Web版（tengel3.html）には 入らない')

    if HAVE:
        with sync_playwright() as p:
            b = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'])

            def page(block=None):
                ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo'); ctx.add_init_script(FAKE)
                for pat in (block or []): ctx.route(pat, lambda r: r.abort())
                pg = ctx.new_page(); pg.errs = []; pg.bad = []
                pg.on('pageerror', lambda e: pg.errs.append(str(e)))
                pg.on('response', lambda r: pg.bad.append(r.url.split('/')[-1]) if r.status >= 400 and 'tc_' in r.url else None)
                return ctx, pg

            def shot(pg, name):
                if SHOT: os.makedirs(SHOT, exist_ok=True); pg.screenshot(path=os.path.join(SHOT, name + '.png'))

            # ================= くじ =================
            print('■ App Store版：くじ')
            ctx, pg = page(); open_tc(pg, APP)
            T = pg.evaluate("""() => { const T = TCApp._t, P = T.PRIZES, V = T.PRIZES_VISIT, tabs = [P, V.maboroshi, V.kamisama];
              return { d: T.GEKI.d, v: T.GEKI.v, i: tabs.map(t => t.findIndex(q => q[1].k === 'gk')), n: tabs.map(t => t.filter(q => q[1].k === 'gk').length), p: tabs.map(t => t[0][0] * 299999),
                sum: tabs.map(t => t.reduce((s, q) => s + q[0], 0)), tone: T.dropTone({ k: 'gk' }), tone2: T.dropTone({ k: 'gk', vis: 'kamisama' }), se: T.GEKI_SE, prep: (z => [z.k, z.v, /^tc-/.test(z.id)])(T.prep({ k: 'gk' })),
                name: TCDrop.NAME[7], art: TCDrop.gekiArt(), pcd: [TCDrop.PC_LINE, TCDrop.PC_DARK, TCDrop.PC_CALM], gk: [TCFX.GK.line, TCFX.GK.dark, TCFX.GK.len, TCFX.GK.text, TCFX.GK.v] }; }""")
            check(T['d'] == 299999 and T['v'] == 40000 and T['i'] == [0, 0, 0] and T['n'] == [1, 1, 1] and all(abs(x - 1) < 1e-9 for x in T['p']) and all(s < 1 for s in T['sum']),
                  f'くじの 表：激馬熱馬は 1/299999（いつもの 馬・幻の馬・神様馬の どの 表にも 1行・表の 合計は 1 より 小さい：{[round(s, 4) for s in T["sum"]]}）')
            check(T['tone'] == 7 and T['tone2'] == 7 and T['prep'] == ['gk', 40000, True] and T['name'] == '激馬熱馬' and T['art'] and T['pcd'] == [0.243, 1.67, 0.4] and T['gk'][:3] == [0.243, 1.67, 2.4] and abs(T['gk'][3] - 59 / 30) < 1e-9 and T['gk'][4] == 40000,
                  f'中身：40,000P・お世話チャレンジの 色は 7（激馬熱馬：どの 馬が いても）・絵（馬バレ・保留）が 読めて いる（{T["prep"]}・{T["name"]}）')
            # くじを 決めた 数で ひく：はじめの 1/299999 だけ 激馬熱馬。高確ゾーン（4倍）の 間は 4/299999 まで
            dr = pg.evaluate("""(rs) => { const R = Math.random, out = []; for (const [r, hi] of rs) { TCCare.S.high = hi; TCApp.state.high = hi; let first = true;
                Math.random = () => { if (first) { first = false; return r; } return 0.3; }; try { const z = TCApp._t.draw(); out.push(z ? z.k : null); } finally { Math.random = R; } }
              TCCare.S.high = 0; TCApp.state.high = 0; return out; }""", [[0.0, 0], [0.99 / 299999, 0], [1.01 / 299999, 0], [3.99 / 299999, 1], [4.01 / 299999, 1], [0.999, 0]])
            check(dr[0] == 'gk' and dr[1] == 'gk' and dr[2] not in ('gk', None) and dr[3] == 'gk' and dr[4] not in ('gk', None) and dr[5] is None,
                  f'くじ：0〜1/299999 の 数で 激馬熱馬・その すぐ 上は 次の 当たり（ポイント特化ゾーン）。高確ゾーンの 間は ほかの 当たりと 同じく 4倍（4/299999 まで）（{dr}）')

            # プチュンの 線（TCFX.gkLine：PUSH と 馬バレの 丸が 同じ 部品）を 黒い 紙（横幅 582）に 描いて 測る：太さ（明るさが 半分に なる 幅）・色（芯は 白っぽい 金 → 金 → 外は 赤）・0.243秒で 消える
            #   明るさ＝赤・緑・青の いちばん 大きい 数（線の 外がわは 赤：緑を 重く 見る 明るさ〈輝度〉で 測ると 赤い 所が 暗く 出て、見た目の 太さより 細く なる）
            ln = pg.evaluate("""(us) => us.map(u => { const cv = document.createElement('canvas'); cv.width = 582; cv.height = 400; const g = cv.getContext('2d', { willReadFrequently: true }); g.fillStyle = '#000'; g.fillRect(0, 0, 582, 400);
              const I = TCFX.gkLine(g, 291, 200, 291, u), col = g.getImageData(100, 0, 1, 400).data, lum = j => Math.max(col[j * 4], col[j * 4 + 1], col[j * 4 + 2]); let mx = 0, n = 0, red = 0, gold = 0;
              for (let j = 0; j < 400; j++) mx = Math.max(mx, lum(j));
              for (let j = 0; j < 400; j++) { const R = col[j * 4], G = col[j * 4 + 1], B = col[j * 4 + 2]; if (mx > 0 && lum(j) >= mx / 2) n++; if (R > 60 && G < 0.38 * R && B < 0.3 * R) red++; if (R > 90 && G > 0.5 * R && G < 0.86 * R && B < 0.45 * R) gold++; }
              const c = [...g.getImageData(100, 200, 1, 1).data].slice(0, 3), f = [...g.getImageData(291, 200, 1, 1).data].slice(0, 3), far = [...g.getImageData(100, 60, 1, 1).data].slice(0, 3);
              return { u, I: +I.toFixed(3), half: n, red, gold, c, f, far }; })""", [0.0, 0.043, 0.11, 0.2, 0.243, 0.4])
            want_half = [48, 28, 9, 9]
            check(all(abs(ln[i]['half'] - want_half[i]) <= max(3, want_half[i] * 0.3) for i in range(4)) and [q['I'] for q in ln[:4]] == sorted([q['I'] for q in ln[:4]], reverse=True) and ln[0]['I'] == 1 and ln[4]['I'] == 0 and ln[5]['I'] == 0
                  and max(ln[4]['c'] + ln[4]['f'] + ln[5]['c']) == 0,
                  f'プチュンの 線の 太さ（明るさが 半分の 幅）：{[q["half"] for q in ln[:4]]}（見本 48 → 28 → 9 → 9）・明るさ {[q["I"] for q in ln[:4]]} と 下がる だけ・0.243秒で 消える')
            check(all(q['red'] >= 2 and q['gold'] >= 1 for q in ln[:3]) and ln[0]['c'][0] > 240 and ln[0]['c'][1] > 220 and ln[0]['c'][2] > 150 and ln[0]['c'][0] >= ln[0]['c'][1] >= ln[0]['c'][2] and max(ln[0]['far']) < 8 and min(ln[0]['f']) > 235,
                  f'線の 色：芯は 白っぽい 金 {ln[0]["c"]}・その 外が 金・いちばん 外が 赤（赤 {[q["red"] for q in ln[:3]]}・金 {[q["gold"]for q in ln[:3]]}画素）・まん中に 白い 光 {ln[0]["f"]}・線の 外は 黒')
            # 説明書
            pg.evaluate("() => TCGuide.open(document.querySelector('#tcOv .tcst'), {})"); pg.wait_for_timeout(900)
            gd = pg.evaluate("""() => { const r = document.querySelector('#tcg'), q = s => r.querySelector(s), t = e => (e ? e.textContent.replace(/\\s+/g, ' ').trim() : null);
              const sec = [...r.querySelectorAll('h3')].map(h => h.textContent.trim()), gk = [...r.querySelectorAll('.gk')].map(e => t(e.closest('tr') || e.parentNode));
              return { nolot: t(q('[data-n=nolot]')), gekiv: t(q('[data-n=gekiv]')), dp: t(q('[data-dp=geki]')), sec, gk, txt: r.textContent }; }""")
            pg.evaluate("() => TCGuide.close()"); pg.wait_for_timeout(600)
            check(gd['gekiv'] == '・40,000P GET' and gd['dp'] and 'プチュン' in gd['dp'] and '激馬熱馬' in gd['dp'] and '1/299999' in gd['txt'] and '約0.00033%' in gd['txt'] and len(gd['gk']) >= 3 and any('激馬熱馬' in h for h in gd['sec']),
                  f'説明書：「激馬熱馬」の 項目（1/299999・約0.00033%・40,000P GET）・当たりの 表（いつもの 馬・幻の馬・神様馬）に 1行ずつ・お世話チャレンジの 説明に「馬バレが プチュン！」')
            check(gd['nolot'] and '数えない' in gd['nolot'] and '抽選を する' in gd['txt'] and '抽選を しない' in gd['txt'], f'説明書：「抽選をする／しない」の 項目（しない＝トークンは へらない・お世話の 回数に 数えない：「{(gd["nolot"] or "")[:30]}…」）')

            # ================= PUSH =================
            print('■ App Store版：PUSH で 激馬熱馬（プチュン → 真っ暗 → 天国 → 40000P獲得）')
            gkr = pg.evaluate(RND_FOR, {'k': 'gk'})
            pg.evaluate(SETTOK, 12); pg.evaluate(PUSH_ON); pg.wait_for_timeout(900); recs(pg)
            w0 = pg.evaluate(ST)
            pr = pg.evaluate(PUSHJS, [[gkr, 0.3, 0.3]])
            rc0 = [(round(t - pr['t'], 3), n) for t, n in pr['rec']]
            check(pr['res'] == 'gk' and pr['pend'] == ['gk', 40000] and pr['spend'] and pr['spend'][:2] == ['gk', 40000] and pr['stock'] == 11 and pr['sstock'] == 11,
                  f'PUSH を 押した 瞬間：激馬熱馬・当たりは その場で 保存（演出の 途中で 閉じても なくならない）・お世話トークン −1（{pr["pend"]}・のこり {pr["stock"]}こ）')
            check(pr['on'] and pr['gk'] == {'calm': False, 'puchun': True} and pr['el'] is not None and pr['el'][1] == 1 and pr['el'][2] == 'tcfx' and float(pr['el'][0]) == 0,
                  f'押した その場で 演出が はじまる（待ち時間 なし：いきなり プチュン）。天国の 動画は 演出の キャンバスの 下に 用意（まだ 見せない）（{pr["el"]}）')
            check(('gk_pchun' in [n for _, n in rc0]) and ('bgm:' in [n for _, n in rc0]) and 'kyuin' not in [n for _, n in rc0] and all(t < 0.05 for t, _ in rc0),
                  f'押した 瞬間に プチュンの 音・フィールドの 音楽は その場で 止まる（キュインキュイーンは なし）（{rc0}）')
            pg.wait_for_timeout(450); mid = pg.evaluate(GKST); mpx = pg.evaluate(FXPX, [0.0, 1.0]); shot(pg, 'gk_dark')
            um = mid['now'] - pr['t']
            if 0.26 < um < 1.6:
                check(mpx['black'] > 0.995 and mid['el'] == 0 and mid['k']['hv'] is None and mid['on'], f'プチュンの あと（{um:.2f}秒め）：画面は 真っ暗（黒 {mpx["black"]:.1%}）・天国は まだ 出て いない')
            else:
                print(f'  ・（真っ暗の 間を 見そこねた：{um:.2f}秒め。テストの 機械が おそい）')
            R = geki_run(pg, tap=True)
            rc = [(round(t - pr['t'], 3), n) for t, n in recs(pg)]; names = [n for _, n in rc]
            hv, tx = R['hv']['k']['hv'], R['text']['k']['textAt']
            check(1.67 <= hv <= 2.3 and R['hv']['k']['mode'] == 'film' and R['hv']['el'] == 1 and 'gk_heaven' in names and hv - 0.02 <= at(rc, 'gk_heaven') <= hv + 0.6,
                  f'真っ暗は プチュンの 音が 切れる まで（1.67秒）→ 天国の 場面（動画）・動画が 動きはじめたら 天国の 音（{hv:.2f}秒め・音 {at(rc, "gk_heaven")}秒め）')
            v1, v2 = R['hv']['v'], R['hv2']['v']
            check(v1 and v2 and (v1['w'], v1['h']) == (1170, 1842) and abs(v1['d'] - 2.4) < 0.06 and v1['muted'] and v1['inl'] and v1['err'] == 0 and v2['t'] > v1['t'] + 0.05 and R['hv2']['k']['mode'] == 'film',
                  f'天国の 動画が 流れて いる（1170×1842・2.4秒・音なし・画面の 中で 再生：{v1["t"]:.2f} → {v2["t"]:.2f}秒）')
            check(R['early']['ok'] and R['early']['mode'] == 'film' and R['early']['vt'] is not None and R['early']['vt'] >= 59 / 30 - 0.03 and 1.9 <= tx - hv <= 3.4 and 'gk_tedeen' in names and abs(at(rc, 'gk_tedeen') - tx) < 0.25,
                  f'動画の 1.97秒め（ぜんぶが 見えた あと）に テデーン！と デカ文字（天国から {tx - hv:.2f}秒・動画の {R["early"]["vt"]:.2f}秒め・音 {at(rc, "gk_tedeen")}秒め）')
            px, pt = R['px'], R['px_top']
            check(px['gold'] > 0.035 and px['red'] > 0.004 and px['x0'] > 0.03 and px['x1'] < 0.97 and pt['red'] < 0.0005,
                  f'デカ文字「40000P」「獲得」：金の 字に 赤い ふち・画面の 下 1/3 に おさまる（金 {px["gold"]:.1%}・赤 {px["red"]:.1%}・左右 {px["x0"]:.2f}〜{px["x1"]:.2f}・上 2/3〈3D の「40000P」の 所〉には 字を 重ねない {pt["red"]:.2%}）')
            check(R['text']['on'] and R['text']['el'] == 1 and R['before']['on'], 'デカ文字が 出た すぐ あとの タップでは とじない（着いて から 1.1秒 たつ まで）')
            check(R['closed'] - R['tapAt'] < 2.0 and not R['after']['on'] and R['after']['n'] == 0 and R['after']['v'] is None, f'その あとの タップで とじる（{R["closed"] - R["tapAt"]:.2f}秒）・幕と 動画は かたづける')
            s1 = pg.evaluate(ST)
            check(s1['wal'] == w0['wal'] + 40000 and s1['pend'] is None and s1['spend'] is None and len(s1['ev']) == len(w0['ev']) + 1 and s1['ev'][-1][:2] == [40000, 'トレーニングセンターの 激馬熱馬'],
                  f'40,000P を 受け取る（財布 ＋{s1["wal"] - w0["wal"]:,}P・台帳「{s1["ev"][-1][1] if s1["ev"] else ""}」・保存の 当たりは 消える）')
            check(all(n in names for n in ('bgm:', 'gk_pchun', 'gk_heaven', 'gk_tedeen', 'bgm:null')) and names.index('bgm:') < names.index('gk_pchun') < names.index('gk_heaven') < names.index('gk_tedeen') < len(names) - 1 - names[::-1].index('bgm:null')
                  and [names.count(n) for n in ('gk_pchun', 'gk_heaven', 'gk_tedeen')] == [1, 1, 1],
                  f'音の 順：音楽 止まる・プチュン → 天国 → テデーン → おわったら フィールドの 音楽に もどる（どれも 1回ずつ：{[n for n in names if n.startswith("gk_") or n.startswith("bgm")]}）')
            check(not s1['push'] and s1['stock'] == 11 and s1['cares'] == w0['cares'] + 1, f'お世話は 1回に 数える・PUSH は 消える（1個 使う）（お世話 {w0["cares"]} → {s1["cares"]}）')
            check(pg.errs == [] and pg.bad == [], f'エラーなし・読めない ファイルなし（{pg.errs[:2]}・{pg.bad[:3]}）')

            # ================= 途中で 閉じた（PUSH）=================
            print('■ App Store版：演出の 途中で アプリを 閉じた（PUSH）')
            pg.evaluate(SETTOK, 12); pg.evaluate(PUSH_ON); pg.wait_for_timeout(900)
            w1 = pg.evaluate(ST); pr2 = pg.evaluate(PUSHJS, [[gkr, 0.3, 0.3]]); pid = pr2['spend'][2] if pr2['spend'] else None
            pg.wait_for_timeout(500)                                   # 真っ暗の 間に 閉じる
            reopen(pg)
            s2 = pg.evaluate(ST); m2 = pg.evaluate("() => { const e = document.querySelector('#tcOv .tcmsg'); return [e.textContent, e.classList.contains('on')]; }")
            check(pr2['res'] == 'gk' and pid and s2['wal'] == w1['wal'] + 40000 and s2['pend'] is None and s2['spend'] is None and [e for e in s2['ev'] if e[2] == pid] == [[40000, 'トレーニングセンターの 激馬熱馬', pid]] and '前の 当たり（40,000P）を 受け取ったよ' in m2[0],
                  f'真っ暗の 間に 閉じても、開き直すと 40,000P を 受け取る（お知らせ「{m2[0].strip()[:24]}」・財布 ＋{s2["wal"] - w1["wal"]:,}P）')
            reopen(pg); s3 = pg.evaluate(ST)
            check(s3['wal'] == s2['wal'] and len(s3['ev']) == len(s2['ev']), '2回は もらえない（もう一度 開き直しても ふえない）')

            # ================= お世話チャレンジ =================
            print('■ App Store版：お世話チャレンジで 激馬熱馬（馬バレの 丸が プチュン → 激馬熱馬）')
            pg.evaluate(SETTOK, 12); pg.evaluate(PUSH_ON); pg.wait_for_timeout(1000)
            G = pg.evaluate("() => TCCare.PUSHG"); geo = pg.evaluate("() => TCDrop.geo()")
            stage_click(pg, *G['dp']); pg.wait_for_function("() => TCDrop.isOpen()", timeout=8000)
            pg.evaluate("() => { const T = TCDrop._t; T.manual = true; T.rec = []; }"); pg.evaluate(TICK, [0.7, None]); recs(pg)
            C = pg.evaluate("() => ({ win: TCDrop.WIN_AT, lead: TCDrop.LEAD, lock7: TCDrop.TONE[7].lock, hold7: TCDrop.TONE[7].hold, t6: TCDrop.TONE[6], t7: TCDrop.TONE[7], beats: [TCDrop.beats(6), TCDrop.beats(7)] })")
            check(C['t7']['pip'] == C['t6']['pip'] and C['t7']['long'] == C['t6']['long'] and C['beats'][0] == C['beats'][1] and C['t7']['R'] > C['t6']['R'] and C['t7']['rgb'] == [255, 255, 255],
                  f'激馬熱馬の 光：拍は 虹と 同じ（同じ 音に 合わせる：{C["t7"]["pip"]}拍）・オーラは 虹より 少し 大きい（{C["t6"]["R"]} → {C["t7"]["R"]}）')
            w4 = pg.evaluate(ST)
            ok = pg.evaluate(GO, [[gkr, 0.3, 0.3]]); i_a = pg.evaluate(INFO); s_a = pg.evaluate(ST)
            check(ok and i_a['phase'] == 'fall' and i_a['ball']['c'] == 7 and s_a['sdp'] == [['gk', 7]] and s_a['stock'] == 11 and s_a['sstock'] == 11,
                  f'玉を 落とした 瞬間に 当たりを 保存（色 7＝激馬熱馬・お世話トークン −1）（{s_a["sdp"]}）')
            pg.evaluate(TICK, [8, "TCDrop.state.ball && TCDrop.state.ball.inT != null"]); tin = pg.evaluate("() => TCDrop.state.ball.inT")
            pg.evaluate(TICK, [1, "!!TCDrop.state.pc"]); i_p = pg.evaluate(INFO); tpc = pg.evaluate("() => TCDrop.state.pc.t0"); dr0 = pg.evaluate(DREC); rq = [n for _, n in recs(pg)]
            check(abs(tpc - tin - C['win']) < 0.02 and i_p['quiet'] and ('gk_pchun' in [n for _, n in dr0]) and not any(n.startswith('dp_um') for _, n in dr0) and 'bgm:' in rq and pg.evaluate(LAMP)['c'] == -1,
                  f'コップに 入った 瞬間（{tpc - tin:.2f}秒）：プチュンの 音・フィールドの 音楽は 止まる・馬バレ音と 馬バレの 光は まだ（{[n for _, n in dr0 if not n.startswith("dp_peg")]}）')
            pg.evaluate(TICK, [1 / 60, None]); l1 = pg.evaluate(LENS); shot(pg, 'gk_lens1')
            pg.evaluate(TICK, [0.1 - 2 / 60, None]); l2 = pg.evaluate(LENS); u2 = pg.evaluate(INFO)['pc']; shot(pg, 'gk_lens2')
            lum = lambda c: 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
            check(lum(l1['c']) > 200 and lum(l1['off']) > 60 and lum(l2['c']) > 150 and lum(l2['off']) < 30 and l2['on'][0] > 90 and l2['on'][0] >= l2['on'][2] + 12 and l2['mean'] < 60,
                  f'馬バレの 丸：はじめは 明るい 中に 太い 線 → 真っ暗の 丸に 赤と 金の 細い 線（{u2:.2f}秒め：線の 上 {l2["on"]}・線の 外 {l2["off"]}・丸の 明るさ {l2["mean"]:.0f}）')
            pg.evaluate(TICK, [0.5 - u2, None]); l3 = pg.evaluate(LENS); nogo = pg.evaluate("() => TCDrop.tap('go')"); noquit = pg.evaluate("() => TCDrop.tap('quit')"); shot(pg, 'gk_lens3')
            check(l3['mean'] < 20 and lum(l3['c']) < 20 and not nogo and not noquit and pg.evaluate(LAMP)['c'] == -1, f'線が 消えた あと（0.5秒め）：丸は 真っ暗の まま（明るさ {l3["mean"]:.1f}）・次の 玉は 落とせない・やめられない')
            pg.evaluate(TICK, [3, "TCDrop._t.rec.some(q => q[1] === 'dp_umb6')"]); dr1 = pg.evaluate(DREC); tum = [t for t, n in dr1 if n == 'dp_umb6'][0]; tp_ = [t for t, n in dr1 if n == 'gk_pchun'][0]
            lp0 = pg.evaluate(LAMP); pg.evaluate(TICK, [C['lead'] + 2 / 60, None]); lp1 = pg.evaluate(LAMP)
            check(abs(tum - tp_ - 1.67) < 0.02 and lp0['c'] == -1 and lp1['c'] == 7 and abs(lp1['t0'] - tum - C['lead']) < 0.02 and not any(n.startswith('dp_um') and n != 'dp_umb6' for _, n in dr1),
                  f'プチュンの 音が 切れる 1.67秒で 虹と 同じ 音（dp_umb6）→ 0.1秒 あとに 激馬熱馬の 馬バレが つく（{tum - tp_:.2f}秒・{lp1["t0"] - tum:.2f}秒）')
            pg.evaluate(TICK, [0.6, None]); l4 = pg.evaluate(LENS); i_l = pg.evaluate(INFO); shot(pg, 'gk_uma')
            check(l4['mean'] > 50 and i_l['lcd'] == 7 and i_l['lamp'] > 0.3 and i_l['quiet'], f'馬バレの 丸に 激馬熱馬の 絵（丸の 明るさ {l4["mean"]:.0f}）')
            pg.evaluate(TICK, [8, "TCDrop.state.phase !== 'fall'"]); t_end = pg.evaluate("() => TCDrop.state.t"); i_e = pg.evaluate(INFO); rq2 = [n for _, n in recs(pg)]
            check(abs(t_end - tp_ - (1.67 + C['lead'] + C['lock7'])) < 0.04 and not i_e['quiet'] and 'bgm:null' in rq2 and i_e['holds'] == [[7, 'in', 'gk']],
                  f'馬バレが つき おわると（プチュンから {t_end - tp_:.2f}秒）フィールドの 音楽が もどる・保留の ますに 激馬熱馬（{i_e["holds"]}）')
            shot(pg, 'gk_hold')
            # --- 投入終了 → 保留結果を見る → 天国（プチュンは なし）---
            print('■ App Store版：保留結果を見る → 天国 → 40000P獲得')
            pg.evaluate(TICK, [0.4, None]); q_ok = pg.evaluate("() => TCDrop.tap('quit')"); pg.evaluate(TICK, [0.6, None]); i_w = pg.evaluate(INFO)
            pg.evaluate("() => { TCDrop._t.manual = false; }"); recs(pg)
            stage_click(pg, *geo['see']); t_see = pg.evaluate("() => performance.now() / 1000"); pg.wait_for_timeout(250)
            check(q_ok and i_w['phase'] == 'wait' and pg.evaluate(INFO)['phase'] == 'res', '投入終了 →「保留結果を見る」を 指で 押すと はじまる')
            pg.wait_for_function("() => { const k = TCFX.gkState; return !!(k && k.puchun === false && k.hv != null) && !!document.querySelector('#tcOv .tcfx.on'); }", timeout=25000)
            g0 = pg.evaluate(GKST); hid = pg.evaluate(INFO)['hold']
            R2 = geki_run(pg, tap=True)
            rc2 = [(round(t - t_see, 3), n) for t, n in recs(pg)]; n2 = [n for _, n in rc2]
            check(g0['k']['puchun'] is False and 0.3 <= g0['k']['hv'] <= 0.9 and 'gk_pchun' not in n2 and 'bgm:none' in n2 and n2.count('gk_heaven') == 1 and n2.count('gk_tedeen') == 1 and hid,
                  f'「保留結果を見る」から：プチュンは なし（馬バレで もう 見せた）・すっと 暗く なって 0.3秒で 天国（{g0["k"]["hv"]:.2f}秒め）・台は かくれる（{[n for n in n2 if n.startswith("gk_") or n.startswith("bgm")]}）')
            check(R2['early']['mode'] == 'film' and R2['early']['vt'] >= 59 / 30 - 0.03 and R2['px']['gold'] > 0.035, f'天国の 動画 → デカ文字（動画の {R2["early"]["vt"]:.2f}秒め）は PUSH と 同じ')
            pg.wait_for_function("() => TCDrop.info() && TCDrop.info().phase === 'end'", timeout=20000); pg.wait_for_timeout(700)
            i_f = pg.evaluate(INFO); s5 = pg.evaluate(ST); shot(pg, 'gk_end')
            check(i_f['sum'] == 40000 and s5['wal'] == w4['wal'] + 40000 and s5['sdp'] == [] and s5['dp'] == [] and len(s5['ev']) == len(w4['ev']) + 1 and [h[1] for h in i_f['holds']] == ['done'],
                  f'40,000P を 受け取る（財布 ＋{s5["wal"] - w4["wal"]:,}P・おしまいの 札「今回の 当たり」＋{i_f["sum"]:,}P・保存の 保留は 空に）')
            stage_click(pg, *(geo['end2'] if i_f['more'] else geo['end1'])); pg.wait_for_timeout(900)
            check(not pg.evaluate("() => TCDrop.isOpen()") and pg.errs == [] and pg.bad == [], f'「終わり」で 台を 閉じる・エラーなし（{pg.errs[:2]}・{pg.bad[:3]}）')

            # ================= 途中で 閉じた（お世話チャレンジ）=================
            print('■ App Store版：馬バレの プチュンの 途中で 閉じた')
            pg.evaluate(SETTOK, 12); pg.evaluate(PUSH_ON); pg.wait_for_timeout(1000)
            stage_click(pg, *G['dp']); pg.wait_for_function("() => TCDrop.isOpen()", timeout=8000)
            pg.evaluate("() => { const T = TCDrop._t; T.manual = true; T.rec = []; }"); pg.evaluate(TICK, [0.7, None]); recs(pg)
            w6 = pg.evaluate(ST); pg.evaluate(GO, [[gkr, 0.3, 0.3]])
            pg.evaluate(TICK, [8, "!!TCDrop.state.pc"]); pg.evaluate(TICK, [0.5, None]); q6 = pg.evaluate(INFO)['quiet']
            pg.evaluate("() => { TCDrop._t.manual = false; TCDrop.close(); }"); pg.wait_for_timeout(500); rq6 = [n for _, n in recs(pg)]; s6 = pg.evaluate(ST)
            check(q6 and 'bgm:null' in rq6 and not s6['open'] and s6['sdp'] == [['gk', 7]] and s6['wal'] == w6['wal'],
                  f'真っ暗の 丸の 途中で 台を 閉じた：フィールドの 音楽は もどる・当たりは 保存に 残って いる（{s6["sdp"]}）')
            reopen(pg)
            pg.wait_for_function("() => TCDrop.isOpen() && TCDrop.info().phase === 'wait'", timeout=30000); pg.wait_for_timeout(900)
            i7 = pg.evaluate(INFO); geo = pg.evaluate("() => TCDrop.geo()")
            check([[h[0], h[2]] for h in i7['holds']] == [[7, 'gk']] and i7['used'] == 0 and not pg.evaluate("() => TCDrop.tap('go')"), f'開き直すと 台が「保留結果を見る」から 出る（保留に 激馬熱馬：{i7["holds"]}）・玉は 落とせない（先に 受け取る）')
            stage_click(pg, *geo['see']); pg.wait_for_function("() => { const k = TCFX.gkState; return !!(k && k.hv != null) && !!document.querySelector('#tcOv .tcfx.on'); }", timeout=25000)
            R3 = geki_run(pg, tap=True)
            pg.wait_for_function("() => TCDrop.info() && TCDrop.info().phase === 'end'", timeout=20000); pg.wait_for_timeout(700); s7 = pg.evaluate(ST)
            check(s7['wal'] == w6['wal'] + 40000 and s7['sdp'] == [] and len(s7['ev']) == len(w6['ev']) + 1, f'天国の 演出の あと 40,000P を 受け取る（1回 だけ：財布 ＋{s7["wal"] - w6["wal"]:,}P）')
            stage_click(pg, *pg.evaluate("() => { const g = TCDrop.geo(), i = TCDrop.info(); return i.more ? g.end2 : g.end1; }")); pg.wait_for_timeout(900)
            check(not pg.evaluate("() => TCDrop.isOpen()") and pg.errs == [], f'台を 閉じる・エラーなし（{pg.errs[:2]}）')

            # ================= 動画が 途中で 止まった =================
            print('■ App Store版：天国の 動画が 途中で 止まった とき（アプリが うしろに 回った など）')
            pg.evaluate(SETTOK, 12); pg.evaluate(PUSH_ON); pg.wait_for_timeout(1000); recs(pg)
            wb = pg.evaluate(ST); prb = pg.evaluate(PUSHJS, [[gkr, 0.3, 0.3]])
            pg.wait_for_function("() => { const k = TCFX.gkState, v = document.querySelector('#tcOv .tcgk video'); return !!(k && k.mode === 'film' && v && v.currentTime > 0.15); }", timeout=20000)
            stall = pg.evaluate("() => { const v = document.querySelector('#tcOv .tcgk video'); v.pause(); return v.currentTime; }")      # 動画を 止める（「40」の 場面の 途中）
            Rb = geki_run(pg, tap=True); kb = Rb['text']['k']; sb = pg.evaluate(ST); nb = [n for _, n in recs(pg)]
            check(prb['res'] == 'gk' and stall < 1.6 and kb['mode'] == 'still' and 59 / 30 + 0.75 <= kb['textAt'] - kb['hv'] <= 59 / 30 + 1.5 and Rb['text']['im']['o'] == 1 and Rb['px']['gold'] > 0.035 and nb.count('gk_tedeen') == 1
                  and sb['wal'] == wb['wal'] + 40000 and sb['pend'] is None,
                  f'動画が {stall:.2f}秒めで 止まっても、演出は 止まった ままに ならない：さいごの コマの 絵に かえて テデーンと 字（天国から {kb["textAt"] - kb["hv"]:.2f}秒）→ 40,000P を 受け取る')

            # ================= 演出を控えめにする =================
            print('■ App Store版：「演出を控えめにする」')
            pg.evaluate(CALM, 1)
            pg.evaluate(SETTOK, 12); pg.evaluate(PUSH_ON); pg.wait_for_timeout(1000); recs(pg)
            w8 = pg.evaluate(ST); pr8 = pg.evaluate(PUSHJS, [[gkr, 0.3, 0.3]])
            R8 = geki_run(pg, tap=False)
            rc8 = [(round(t - pr8['t'], 3), n) for t, n in recs(pg)]; n8 = [n for _, n in rc8]
            k8 = R8['text']['k']; s8 = pg.evaluate(ST)
            check(pr8['gk'] == {'calm': True, 'puchun': False} and 'gk_pchun' not in n8 and 'gk_heaven' not in n8 and n8.count('gk_tedeen') == 1 and k8['mode'] == 'still' and 0.4 <= k8['hv'] <= 1.0 and 0.45 <= k8['textAt'] - k8['hv'] <= 1.0,
                  f'控えめ：プチュンの 線と 音・天国の 動画と 音は なし。すっと 暗く なって（{k8["hv"]:.2f}秒）さいごの コマの 絵 → テデーンと 字（{[n for n in n8 if n.startswith("gk_")]}）')
            check(R8['text']['im'] and R8['text']['im']['o'] == 1 and R8['text']['im']['w'] == 1170 and (R8['text']['v'] is None or R8['text']['v']['paused']) and R8['px']['gold'] > 0.035,
                  f'絵（3D の「40000P」が ぜんぶ 見える さいごの コマ：{R8["text"]["im"]}）と デカ文字が 出る・動画は 流さない')
            tl = R8['closed'] - (pr8['t'] + k8['textAt'])
            check(3.4 <= tl <= 7.5 and s8['wal'] == w8['wal'] + 40000 and s8['pend'] is None, f'タップ しなくても 自分で とじる（字が 出て から {tl:.1f}秒）・40,000P を 受け取る')
            # 台（控えめ）：線も プチュンの 音も なし・丸が 暗く なる だけ → 0.4秒で 虹と 同じ 音と 絵
            pg.evaluate(SETTOK, 12); pg.evaluate(PUSH_ON); pg.wait_for_timeout(1000)
            stage_click(pg, *G['dp']); pg.wait_for_function("() => TCDrop.isOpen()", timeout=8000)
            pg.evaluate("() => { const T = TCDrop._t; T.manual = true; T.rec = []; }"); pg.evaluate(TICK, [0.7, None])
            pg.evaluate(GO, [[gkr, 0.3, 0.3]]); pg.evaluate(TICK, [8, "!!TCDrop.state.pc"]); t9 = pg.evaluate("() => TCDrop.state.pc.t0")
            pg.evaluate(TICK, [0.1, None]); l9 = pg.evaluate(LENS); pg.evaluate(TICK, [0.2, None]); l9b = pg.evaluate(LENS)
            pg.evaluate(TICK, [3, "TCDrop._t.rec.some(q => q[1] === 'dp_umb6')"]); dr9 = pg.evaluate(DREC); tu9 = [t for t, n in dr9 if n == 'dp_umb6']
            pg.evaluate(TICK, [0.3, None]); lp9 = pg.evaluate(LAMP)
            check('gk_pchun' not in [n for _, n in dr9] and max(l9['c']) < 140 and max(l9['on']) < 140 and l9b['mean'] < 25 and tu9 and abs(tu9[0] - t9 - 0.4) < 0.02 and lp9['c'] == 7,
                  f'台（控えめ）：線も プチュンの 音も なし（丸が 暗く なる だけ：まん中 {l9["c"]}）→ 0.4秒で 虹と 同じ 音と 激馬熱馬の 絵（{tu9[0] - t9 if tu9 else None}秒）')
            pg.evaluate("() => { TCDrop._t.manual = false; TCDrop.close(); }"); pg.wait_for_timeout(400)
            pg.evaluate("() => { for (const z of (TCApp.state.dp && TCApp.state.dp.holds || []).slice()) TCApp._t.give(z); TCCare.pushDone(TCCare.S.lastT); }"); pg.wait_for_timeout(400)
            pg.evaluate(CALM, 0)
            check(pg.errs == [] and pg.bad == [], f'エラーなし（{pg.errs[:2]}・{pg.bad[:3]}）')
            ctx.close()

            # ================= 動画・絵が ない =================
            print('■ App Store版：動画が 読めない・絵も 読めない とき')
            for pats, nm in ((['**/tc_gk_film2.mp4'], '動画が ない'), (['**/tc_gk_film2.mp4', '**/tc_gk_end2.webp'], '動画も 絵も ない')):
                ctx, pg = page(block=pats); open_tc(pg, APP)
                gkr = pg.evaluate(RND_FOR, {'k': 'gk'})
                pg.evaluate(SETTOK, 12); pg.evaluate(PUSH_ON); pg.wait_for_timeout(1000); recs(pg)
                wa = pg.evaluate(ST); pra = pg.evaluate(PUSHJS, [[gkr, 0.3, 0.3]])
                Ra = geki_run(pg, tap=True); sa = pg.evaluate(ST); ka = Ra['text']['k']
                na = [n for _, n in recs(pg)]
                okim = (Ra['text']['im']['o'] == 1 and Ra['text']['im']['w'] == 1170) if len(pats) == 1 else (Ra['text']['im']['w'] == 0)
                check(pra['res'] == 'gk' and ka['mode'] == 'still' and ka['textAt'] is not None and ka['textAt'] - ka['hv'] <= 1.6 and okim and Ra['px']['gold'] > 0.035 and 'gk_tedeen' in na and 'gk_pchun' in na
                      and sa['wal'] == wa['wal'] + 40000 and sa['pend'] is None and pg.errs == [],
                      f'{nm}：プチュン → 真っ暗 → {"さいごの コマの 絵" if len(pats) == 1 else "暗い 舞台"}に デカ文字（{ka["textAt"] - ka["hv"]:.2f}秒）・40,000P は 受け取る・エラーなし')
                shot(pg, 'gk_nofilm' + str(len(pats)))
                ctx.close()

            # ================= テスト版の 道具箱 =================
            print('■ テスト版：道具箱')
            ctx, pg = page(); open_tc(pg, TESTB)
            w_t = pg.evaluate(ST)
            r_t = pg.evaluate("async () => await TCApp.test.drop([7], true)"); pg.wait_for_function("() => TCDrop.isOpen()", timeout=10000)
            pg.evaluate("() => { const T = TCDrop._t; T.manual = true; T.rec = []; }"); pg.evaluate(TICK, [0.7, None])
            okt = pg.evaluate("() => TCDrop.tap('go')"); pg.evaluate(TICK, [8, "!!TCDrop.state.pc"]); pg.evaluate(TICK, [1.67 + 0.1 + 0.3, None]); lt = pg.evaluate(LAMP); st_ = pg.evaluate(ST)
            check(r_t == 'ok' and okt and lt['c'] == 7 and st_['sdp'] == [['gk', 7]], f'道具箱「④ お世話チャレンジ」で 7（激馬熱馬）を 決めて 落とす → 馬バレが プチュン → 激馬熱馬（{st_["sdp"]}）')
            pg.evaluate("() => { TCDrop._t.manual = false; TCDrop.close(); }"); pg.wait_for_timeout(400)
            pg.evaluate("() => { for (const z of (TCApp.state.dp && TCApp.state.dp.holds || []).slice()) TCApp._t.give(z); TCCare.pushDone(TCCare.S.lastT); }"); pg.wait_for_timeout(500)
            s_t = pg.evaluate(ST)
            check(s_t['wal'] == w_t['wal'] + 40000 and s_t['sdp'] == [] and pg.errs == [], f'その 当たりは 本番と 同じ 中身（40,000P）（財布 ＋{s_t["wal"] - w_t["wal"]:,}P）')
            ctx.close(); b.close()
finally:
    srv.terminate()
print('\n' + ('❌ ' + str(len(fails)) + ' こ 失敗：\n  ' + '\n  '.join(fails) if fails else '✅ ぜんぶ OK'))
sys.exit(1 if fails else 0)
