# 激馬熱馬（第4.175版）の 光の 点めつ：画面 ぜんぶの 演出を 60コマ／秒の 絵に して kisekae/flash_px.py で 数える（1秒に 3回 まで・画面の 10%）
#   ① PUSH：押す 前 0.3秒 → プチュン（赤と 金の 線）→ 真っ暗（1.67秒 まで）→ 天国の 動画（カット 3回：「40」→「00」→「0P」→ ぜんぶ）→ テデーンと デカ文字 → タップで とじる → フィールド
#   ② PUSH（演出を控えめにする）：すっと 暗く → さいごの コマの 絵 → 字 → 自分で とじる
#   ③ お世話チャレンジの「保留結果を見る」から：台 → すっと 暗く → 天国の 動画 → デカ文字 → とじる → 台（おしまいの 札）
#   （馬バレの 丸の プチュンと 激馬熱馬の 光は test_tc_drop_flash.py の 7）
#   ページの 時計を 手で 進めて 1コマずつ 写す（Playwright の clock）。動画（<video>）は その 時計では 進まない ので、play() された 時刻を おぼえて コマごとに その 所へ とばす。
#   とびとびに 見るには サーバーが Range（bytes=…）に 答える ことが いる（python -m http.server は 答えない ＝ 動画が 進まない）→ この 中の 小さな サーバーを 使う
#   （アプリの 中の しくみ〈AppFiles.swift〉は 206 で 答える）
#   python3 test_tc_geki_flash.py [1,2,3]   （時間が かかる ので ふだんの テストとは 別に 動かす。コマは t5/gk_frames/<名前>/ に 残す）
import functools, http.server, json, os, re, shutil, subprocess, sys, threading, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv_tc'); PORT = 8815; APP = f'http://localhost:{PORT}/APP/'
ONLY = [int(x) for x in sys.argv[1].split(',')] if len(sys.argv) > 1 else None
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, TARGET='app'))
from assets_dir import adir
TCA = adir('tc_assets'); HAVE = os.path.isfile(os.path.join(TCA, 'tc_gk_film2.mp4')) and os.path.isfile(os.path.join(TCA, 'tc_dp.json')) and len(os.listdir(TCA)) > 100
pth = os.path.join(SRV, 'APP', 'index.html'); html = open(pth, encoding='utf8').read()
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
if not HAVE: print('※ 激馬熱馬の 動画（ios/tc_assets の tc_gk_film2.mp4）が ない ので、数えない'); sys.exit(0)
for f in os.listdir(TCA): shutil.copy(os.path.join(TCA, f), os.path.join(SRV, 'APP', f))


class RangeHandler(http.server.SimpleHTTPRequestHandler):      # Range: bytes=a-b に 206 で 答える（ほかは いつもの 答え）
    def log_message(self, *a): pass

    def send_head(self):
        rng = self.headers.get('Range'); path = self.translate_path(self.path)
        if not rng or not os.path.isfile(path): return super().send_head()
        m = re.match(r'bytes=(\d*)-(\d*)$', rng.strip()); size = os.path.getsize(path)
        if not m or (m.group(1) == '' and m.group(2) == ''): return super().send_head()
        if m.group(1) == '': a, b = max(0, size - int(m.group(2))), size - 1
        else: a, b = int(m.group(1)), (min(int(m.group(2)), size - 1) if m.group(2) else size - 1)
        if a > b or a >= size:
            self.send_response(416); self.send_header('Content-Range', f'bytes */{size}'); self.end_headers(); return None
        fh = open(path, 'rb'); fh.seek(a); self._left = b - a + 1
        self.send_response(206); self.send_header('Content-Type', self.guess_type(path)); self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Range', f'bytes {a}-{b}/{size}'); self.send_header('Content-Length', str(b - a + 1)); self.end_headers()
        return fh

    def copyfile(self, src, dst):
        left = getattr(self, '_left', None)
        if left is None: return super().copyfile(src, dst)
        self._left = None
        while left > 0:
            buf = src.read(min(65536, left))
            if not buf: break
            dst.write(buf); left -= len(buf)


httpd = http.server.ThreadingHTTPServer(('', PORT), functools.partial(RangeHandler, directory=SRV)); threading.Thread(target=httpd.serve_forever, daemon=True).start()
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


SETTOK = "n => { const S = TCCare.S, s = TCApp.state; S.stock = n; S.stockShow = n; s.stock = n; s.stockAt = Date.now(); S.high = 0; s.high = 0; }"
PUSH_ON = "() => { const S = TCCare.S; if (!(S.push && S.push.hideT == null)) TCCare.pushShow(S.lastT + 0.05); }"
RND_FOR = """(want) => { const T = TCApp._t, tab = TCApp.state.visit ? T.PRIZES_VISIT[TCApp.state.visit.kind] : T.PRIZES; let a = 0;
  for (const [p, z] of tab) { if (z.k === want.k) return a + p / 2; a += p; } return null; }"""
# PUSH・「玉を落とす」を 押す：その 間 だけ くじ（Math.random）を 決めた 数の 列に する
PUSHJS = """([seq]) => { const R = Math.random, q = (seq || []).slice(); let last = q.length ? q[q.length - 1] : 0.995; TCCare.S.high = 0; TCApp.state.high = 0;
  const G = TCCare.PUSHG, st = document.querySelector('#tcOv .tcst'), cv = st.querySelector('.tco'), r = st.getBoundingClientRect();
  const o = { bubbles: true, cancelable: true, clientX: r.left + G.x / 1052 * r.width, clientY: r.top + G.y / 1657 * r.height, pointerId: 7, pointerType: 'touch', isPrimary: true };
  Math.random = () => (q.length ? (last = q.shift()) : last);
  try { cv.dispatchEvent(new PointerEvent('pointerdown', o)); } finally { Math.random = R; }
  cv.dispatchEvent(new PointerEvent('pointerup', o)); return TCCare.S.push ? TCCare.S.push.res : null; }"""
GO = """([seq]) => { const R = Math.random, q = (seq || []).slice(); let last = q.length ? q[q.length - 1] : 0.995; TCCare.S.high = 0; TCApp.state.high = 0;
  Math.random = () => (q.length ? (last = q.shift()) : last);
  try { return TCDrop.tap('go'); } finally { Math.random = R; } }"""
TICK = """async ([sec, cond]) => { const T = TCDrop._t, f = cond ? new Function('return (' + cond + ')') : null; let n = 0;
  for (; n < Math.round(sec * 60); n++) { if (f && f()) break; if (!T.tick(1 / 60)) break; await null; } return n / 60; }"""
# 舞台の 座標（1052×1657）を 指で 押す（pointerdown／up：sel の キャンバスへ）
TAPJS = """([sel, x, y]) => { const st = document.querySelector('#tcOv .tcst'), cv = st.querySelector(sel), r = st.getBoundingClientRect();
  const o = { bubbles: true, cancelable: true, clientX: r.left + x / 1052 * r.width, clientY: r.top + y / 1657 * r.height, pointerId: 6, pointerType: 'touch', isPrimary: true };
  cv.dispatchEvent(new PointerEvent('pointerdown', o)); cv.dispatchEvent(new PointerEvent('pointerup', o)); return true; }"""
# 動画（<video>）：ほんとうの 再生は しない。play() された 時刻を おぼえて、写す コマ ごとに 時計に 合わせた 所を 出す
VFAKE = "() => { const P = HTMLMediaElement.prototype; P.play = function () { this.__t0 = performance.now(); this.__fake = true; return Promise.resolve(); }; P.pause = function () { this.__fake = false; }; }"      # pause：指の 中で 起こす とき（play → pause）は 進めない
VSYNC = """async () => { let n = 0; for (const v of document.querySelectorAll('video')) { if (!v.__fake) continue; const d = isFinite(v.duration) ? v.duration : 2.4, t = Math.min(d, (performance.now() - v.__t0) / 1000);
  if (Math.abs(v.currentTime - t) < 0.004) continue;
  if (!v.seekable.length || v.seekable.end(v.seekable.length - 1) < d - 0.1) throw new Error('video not seekable');      // サーバーが Range に 答えて いない（待ちつづけない ように ここで やめる）
  v.currentTime = t; while (v.seeking) await new Promise(ok => v.addEventListener('seeked', () => ok(), { once: true })); n++; } return n; }"""
GK = "() => { const k = TCFX.gkState; return k ? { calm: k.calm, puchun: k.puchun, mode: k.mode, hv: k.hv, textAt: k.textAt } : null; }"
WAL = "() => TengelWallet.total() + TengelWallet.hold().total"      # 財布（上限 99,999P を こえた 分は あずかりに 入る ので 合わせて）
FX_ON = "() => !!document.querySelector('#tcOv .tcfx.on')"
STEPS = [17, 17, 16]                 # 60コマ／秒（50ミリ秒で 3コマ）
FD = os.path.join(W, 't5', 'gk_frames')
try:
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'])
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo'); ctx.add_init_script(FAKE)
        pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.clock.install()                                      # にせの 時計（ページを 開く 前に 入れる。まだ 止めない ＝ ふつうに 進む）
        pg.goto(APP); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(600)
        pg.evaluate("() => document.querySelectorAll('.tabbar button')[2].click()"); pg.wait_for_timeout(300)
        pg.locator('#tcFab').click()
        pg.wait_for_function("() => window.TCApp && TCApp.state && window.TCCare && TCCare.on && !document.querySelector('#tcOv .tcld')", timeout=90000); pg.wait_for_timeout(1200)
        pg.wait_for_function("() => window.TCDrop && TCDrop.ready()", timeout=30000)
        pg.evaluate(VFAKE)
        pg.clock.pause_at(pg.evaluate("() => Date.now() / 1000 + 0.6"))      # ここから 時計は 手で 進める（秒で わたす）
        gkr = pg.evaluate(RND_FOR, {'k': 'gk'})

        class Shots:
            def __init__(self, name):
                self.d = os.path.join(FD, name); shutil.rmtree(self.d, ignore_errors=True); os.makedirs(self.d); self.n = 0; self.k = 0; self.seeks = 0

            def step(self, shot=True):
                pg.clock.run_for(STEPS[self.k % 3]); self.k += 1
                if shot: self.seeks += pg.evaluate(VSYNC); pg.screenshot(path=os.path.join(self.d, f'f{self.n:04d}.png')); self.n += 1

            def run(self, sec, shot=True):
                for _ in range(int(round(sec * 60))): self.step(shot)

            def until(self, cond, max_sec, shot=True):
                n = 0
                while not pg.evaluate(cond) and n < max_sec * 60: self.step(shot); n += 1
                return n < max_sec * 60

        def count(S, name, t0):
            outs = []
            for area in ('.1', '.03'):
                r = subprocess.run(['python3', os.path.join(W, 'kisekae', 'flash_px.py'), S.d, '0'], capture_output=True, text=True, env=dict(os.environ, AREA=area))
                o = r.stdout.strip().split('\n'); outs.append((r.returncode, o[0] if o else r.stderr[-200:], o[-1] if o else ''))
            check(outs[0][0] == 0 and '窓 0個' in outs[0][1], f'{name}：{S.n}コマ（{time.time() - t0:.0f}秒）… {outs[0][1]}／{outs[0][2]}')
            check(outs[1][0] == 0 and '窓 0個' in outs[1][1], f'{name}：もっと きびしく（画面の 3%）… {outs[1][1]}／{outs[1][2]}')

        def push_case(name, calm):
            t0 = time.time(); S = Shots(name)
            pg.evaluate("c => TengelFx.set({ calm: !!c })", calm); pg.evaluate(SETTOK, 12); pg.evaluate(PUSH_ON); S.run(1.0, shot=False)
            w0 = pg.evaluate(WAL)
            S.run(0.3)                                             # 押す 前（フィールドと PUSH）
            res = pg.evaluate(PUSHJS, [[gkr, 0.3, 0.3]])
            ok1 = S.until("() => { const k = TCFX.gkState; return !!(k && k.textAt != null); }", 12); k = pg.evaluate(GK)
            if calm: ok2 = S.until("() => !document.querySelector('#tcOv .tcfx.on')", 9)      # 控えめ：押さずに 自分で とじるのを 待つ
            else:
                S.run(1.6); pg.evaluate(TAPJS, ['.tcfx', 526, 1000]); ok2 = S.until("() => !document.querySelector('#tcOv .tcfx.on')", 4)
            S.run(0.6)
            w1 = pg.evaluate(WAL)
            want = dict(calm=True, puchun=False, mode='still') if calm else dict(calm=False, puchun=True, mode='film')
            check(res == 'gk' and ok1 and ok2 and all(k[q] == v for q, v in want.items()) and w1 == w0 + 40000 and (calm or S.seeks >= 60),
                  f'{name}：演出を さいごまで 写した（{k["mode"]}・天国 {k["hv"]:.2f}秒・字 {k["textAt"]:.2f}秒・動画を 合わせた コマ {S.seeks}・＋{w1 - w0:,}P）')
            count(S, name, t0)

        if not ONLY or 1 in ONLY: push_case('push', 0)
        if not ONLY or 2 in ONLY: push_case('push_calm', 1)
        pg.evaluate("() => TengelFx.set({ calm: false })")
        if not ONLY or 3 in ONLY:
            t0 = time.time(); S = Shots('see')
            pg.evaluate(SETTOK, 12); pg.evaluate(PUSH_ON); S.run(1.0, shot=False)
            G = pg.evaluate("() => TCCare.PUSHG"); pg.evaluate(TAPJS, ['.tco', G['dp'][0], G['dp'][1]]); S.until("() => TCDrop.isOpen() && TCDrop.info().t > 1.2", 6, shot=False)
            geo = pg.evaluate("() => TCDrop.geo()"); w0 = pg.evaluate(WAL)
            pg.evaluate("() => { TCDrop._t.manual = true; }")      # 玉を 落とす 所は 写さない（test_tc_drop_flash.py の 7）：台の 時計を 手で 進めて 保留まで
            ok0 = pg.evaluate(GO, [[gkr, 0.3, 0.3]]); pg.evaluate(TICK, [12, "TCDrop.state.phase !== 'fall'"]); pg.evaluate(TICK, [0.4, None])
            pg.evaluate("() => TCDrop.tap('quit')"); pg.evaluate(TICK, [1.4, None]); ph = pg.evaluate("() => TCDrop.info().phase")
            pg.evaluate("() => { TCDrop._t.manual = false; }"); S.run(0.2, shot=False)
            S.run(0.3)                                             # 押す 前（台：保留に 激馬熱馬）
            pg.evaluate("() => { window.__gk0 = TCFX.gkState; }")      # 前の 演出の ようす（これと ちがう ものに かわるのを 待つ）
            pg.evaluate(TAPJS, ['canvas.tcdp', geo['see'][0], geo['see'][1]])
            ok1 = S.until("() => { const k = TCFX.gkState; return !!(k && k !== window.__gk0 && k.puchun === false && k.textAt != null); }", 14); k = pg.evaluate(GK)
            S.run(1.6); pg.evaluate(TAPJS, ['.tcfx', 526, 1000]); ok2 = S.until("() => !document.querySelector('#tcOv .tcfx.on')", 4)
            ok3 = S.until("() => TCDrop.info() && TCDrop.info().phase === 'end' && TCDrop.info().t >= TCDrop.state.endT + 0.6", 8); S.run(0.5)
            w1 = pg.evaluate(WAL)
            check(ok0 and ph == 'wait' and ok1 and ok2 and ok3 and k['mode'] == 'film' and k['puchun'] is False and w1 == w0 + 40000 and S.seeks >= 60,
                  f'保留結果を見る：演出を さいごまで 写した（{k["mode"]}・天国 {k["hv"]:.2f}秒・字 {k["textAt"]:.2f}秒・動画を 合わせた コマ {S.seeks}・＋{w1 - w0:,}P）')
            count(S, '保留結果を見る → 天国', t0)
        check(errs == [], f'エラーなし（{errs[:2]}）')
        ctx.close(); b.close()
finally:
    httpd.shutdown()
print('\n' + ('❌ ' + str(len(fails)) + ' こ 失敗：\n  ' + '\n  '.join(fails) if fails else '✅ ぜんぶ OK'))
sys.exit(1 if fails else 0)
