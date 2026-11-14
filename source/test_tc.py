# トレーニングセンター（第4.130版）の テスト：App Store版（TARGET=app）を localhost で アプリ版として 開いて、右下の 丸い ボタン（第4.139版：下の タブの すぐ 上・絵の 下に 名前の 札）→ お世話 → 作戦会議 → 当たりの 演出
#   python3 test_tc.py   （ios/tc_assets/ が ある とき だけ 全部。ない とき（CI）は ボタンと 読みこめない ときの 形だけ）
import json, os, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv_tc'); PORT = 8795; APP = f'http://localhost:{PORT}/APP/'
SHOT = os.environ.get('SHOT')          # 画面を 写す フォルダ（見る 用）
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, TARGET='app'))
pth = os.path.join(SRV, 'APP', 'index.html'); html = open(pth, encoding='utf8').read()
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
from assets_dir import adir
TCA = adir('tc_assets'); HAVE = os.path.isdir(TCA) and len(os.listdir(TCA)) > 100
if HAVE:
    for f in os.listdir(TCA): shutil.copy(os.path.join(TCA, f), os.path.join(SRV, 'APP', f))
else:
    print('※ トレーニングセンターの 絵と 音（ios/tc_assets）が ない ので、ボタンと 読みこめない 形だけ')
# 第4.171版：ルーレットの 高い 方の 爆発の 動画（tc_rt_boom.mp4：H.264）は Chromium で 読めない ので、同じ 絵の 小さな webm を 作って かわりに 読ませる（TCFX.BOOM.src を さしかえる）
BOOM_MP4 = os.path.join(TCA, 'tc_rt_boom.mp4'); HAVE_BOOM = HAVE and os.path.exists(BOOM_MP4) and bool(shutil.which('ffmpeg'))
if HAVE_BOOM:
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', BOOM_MP4, '-vf', 'scale=390:614', '-c:v', 'libvpx-vp9', '-deadline', 'realtime', '-cpu-used', '8', '-crf', '36', '-b:v', '0', '-an', '-row-mt', '1',
                    os.path.join(SRV, 'APP', 'tc_rt_boom.webm')], check=False)
    HAVE_BOOM = os.path.exists(os.path.join(SRV, 'APP', 'tc_rt_boom.webm'))
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

# 第4.161版：馬の 形の 直し（kisekae/tc/horse_fix.py）を アプリの 描いた 絵で 見る ための しかけ。
#   TCHorse が 作られた とき、brain（動き）・create（形）・draw（描く）を つつんで、描いた すぐ あとの 画素を 読めるように する。
#   __tcMetric(度)：馬を 決まった 場所・向きに 立たせて、直し あり／なし（meta.fix を 外す）で 2まい 描いて くらべる。
#     toPur＝直し なしで 黒（どの 色も 45 より 下）だった 画素が 直すと 紫に なった 数（たてがみの 黒い 穴・点）・toDark＝その 逆（紫 → 黒：直しで こわした 所）
#     くらべる 間は 描く 時刻と 馬の 動き（step）を 止める（目の 光は 2.8秒の 波で 強さが かわる・息で 体が 動く・ときどき しっぽを ふる ＝ 止めないと 直しと かかわりの ない 画素が 数に まざる）
HOOK161 = """
(() => { let th; Object.defineProperty(window, 'TCHorse', { configurable: true, get() { return th; }, set(v) { th = v;
  const b = v.brain; v.brain = function (o) { const st = b(o); window.__BR = st; return st; };
  const c = v.create; v.create = function () { const h = c.apply(this, arguments); window.__HO = h; return h; };
  const s0 = v.step; v.step = function (h) { if (window.__ft != null && h === window.__HO) return; return s0.apply(this, arguments); };
  const d = v.draw; v.draw = function (h) { const a = Array.prototype.slice.call(arguments);
    if (h === window.__HO) { if (window.__ft != null) a[2] = window.__ft; else window.__lt = a[2]; }
    const r = d.apply(this, a);
    if (window.__grab && h === window.__HO) { const gl = h.gl, w = gl.drawingBufferWidth, hh = gl.drawingBufferHeight, px = new Uint8Array(w * hh * 4); gl.readPixels(0, 0, w, hh, gl.RGBA, gl.UNSIGNED_BYTE, px); const g = window.__grab; window.__grab = null; g(px, w, hh); }
    return r; }; } });
  const grab = () => new Promise(res => { window.__grab = (px, w, h) => res({ px, w, h }); });
  const wait = ms => new Promise(r => setTimeout(r, ms));
  const pur = (px, i) => px[i + 2] > 150 && px[i + 1] < 60 && px[i] > 70, dark = (px, i) => Math.max(px[i], px[i + 1], px[i + 2]) < 45;
  const diff = (a, b) => { let toPur = 0, toDark = 0, np = 0; const n = a.w * a.h;
    for (let i = 0; i < n * 4; i += 4) { if (pur(b.px, i)) np++; if (dark(a.px, i) && pur(b.px, i)) toPur++; if (pur(a.px, i) && dark(b.px, i)) toDark++; }
    return { toPur, toDark, pur: np }; };
  window.__tcMetric = async (deg) => { const b = window.__BR, h = window.__HO;
    const set = () => { b.x = 526; b.y = 1010; b.dir = deg * Math.PI / 180; b.dirV = 0; b.turnTo = null; b.tgt = null; b.mode = 'idle'; b.reacts = []; b.want.look = [0, 0]; b.force = ['idle:30']; b.until = 0; };
    set(); await wait(700); set(); await wait(150);
    const fix = h.meta.fix; window.__ft = window.__lt;
    try { const on = await grab(), on2 = await grab();
      h.meta.fix = null; const off = await grab();
      return { same: diff(on, on2), fix: diff(off, on), err: h.gl.getError(), w: on.w, h: on.h }; }
    finally { h.meta.fix = fix; window.__ft = null; } };
})()
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


# 第4.159版：お世話の あとの PUSH（tc/tc_care.js）。押すのは 本物の 指の 出来事（pointerdown：指を 置いた 瞬間に 押される）で、その 間 だけ くじ（Math.random）を 決めた 数に する
#   （馬の 頭は 作る ときの Math.random を おぼえて いる ので、さしかえるのは 出来事を 送る 1回の 間 だけ）。返り値＝減った トークンの 数
PUSH_LIVE = "() => { const S = TCCare.S; return !!(S.push && S.push.hideT == null); }"
PRESS = """([seq]) => { const S = TCCare.S, G = TCCare.PUSHG, st = document.querySelector('#tcOv .tcst'), cv = document.querySelector('#tcOv .tco'), r = st.getBoundingClientRect();
  const o = { bubbles: true, clientX: r.left + G.x / 1052 * r.width, clientY: r.top + G.y / 1657 * r.height, pointerId: 7, pointerType: 'touch', isPrimary: true }, R = Math.random, q = (seq || []).slice(), s0 = S.stock;
  S.high = 0; TCApp.state.high = 0;      // 高確ゾーンは なしで（2分ごとの チャンスで ついて いると 当たりの 幅が かわる）
  Math.random = () => (q.length ? q.shift() : 0.5);
  try { cv.dispatchEvent(new PointerEvent('pointerdown', o)); } finally { Math.random = R; }
  cv.dispatchEvent(new PointerEvent('pointerup', o)); return s0 - S.stock; }"""
# その 当たりが 出る くじの 数（いまの 馬の 表の 中で、その 当たりの 幅の まん中。高確ゾーンは なしで）
RND_FOR = """(want) => { const T = TCApp._t, tab = TCApp.state.visit ? T.PRIZES_VISIT[TCApp.state.visit.kind] : T.PRIZES; let a = 0;
  for (const [p, z] of tab) { if (z.k === want.k && (want.k !== 'pt' || z.v === want.v) && (want.k !== 'rt' || !want.tier || z.tier === want.tier)) return a + p / 2; a += p; } return null; }"""
# お世話の 絵（上の キャンバス）の 点の 色（フィールドの 座標）
OVPX = "(pts) => { const cv = document.querySelector('#tcOv .tco'), g = cv.getContext('2d'), k = cv.width / 1052; return pts.map(([x, y]) => Array.from(g.getImageData(Math.round(x * k), Math.round(y * k), 1, 1).data)); }"
PU = """() => { const S = TCCare.S, s = TCApp.state, sv = JSON.parse(localStorage.getItem('tengel.tc')) || {}; return { live: !!(S.push && S.push.hideT == null), stock: S.stock, saved: sv.stock, total: s.total || 0, cares: s.cares, rs: s.rs.n, push: !!s.push, spush: !!sv.push,
  bulk: S.bulk, sbulk: !!sv.bulk, mode: S.mode, phase: S.phase, pop: S.fx.filter(f => f.k === 'pointpop').map(f => f.v), tags: S.fx.filter(f => f.k === 'tagUI').map(f => f.txt), wal: TengelWallet.total() + TengelWallet.hold().total, pend: s.pend ? s.pend.k : null }; }"""
SES = "() => { const a = (window.__seL || []).slice(); if (window.__seL) window.__seL.length = 0; return a; }"      # 鳴らした 音の 名前（tc_se_ と .m4a は とる・音量が 1 で ない ときは ×音量）
SE_WRAP = "() => { const S = TCApp._snd; if (S.__w) return; S.__w = 1; const o = S.se.bind(S); window.__seL = []; S.se = (n, g, l) => { window.__seL.push(n.replace('tc_se_', '').replace('.m4a', '') + (g != null && g !== 1 ? '×' + g : '')); return o(n, g, l); }; }"


# 第4.159版：プチュンの 幕（.tcpc）が 舞台に 入った・外れた 時と、演出の キャンバス（.tcfx）が 出た・消えた 時を 記録する（window.__pcLog）
PC_WATCH = """() => { if (window.__pcObs) { window.__pcLog.length = 0; return; } window.__pcLog = [];
  const st = document.querySelector('#tcOv .tcst'), cv = document.querySelector('#tcOv .tcfx');
  window.__pcObs = new MutationObserver(ms => { for (const m of ms) {
    if (m.type === 'attributes') { window.__pcLog.push({ k: cv.classList.contains('on') ? 'fxon' : 'fxoff', t: performance.now() }); continue; }
    for (const n of m.addedNodes) if (n.classList && n.classList.contains('tcpc')) { const f = n.querySelector('.fxs'), q = n.querySelector('.fxs > .ov.fz > .pc');
      window.__pcLog.push({ k: 'in', t: performance.now(), above: n.previousElementSibling === cv, under: n.nextElementSibling === cv, pc: n.querySelectorAll('.pc').length, parts: q ? q.querySelectorAll('*').length : 0, an: q ? getComputedStyle(q).animationName : '', w: f ? getComputedStyle(f).width : '',
        fxk: f ? +f.style.getPropertyValue('--fxk') : 0, sw: st.clientWidth, bg: getComputedStyle(n).backgroundColor, pe: getComputedStyle(n).pointerEvents, fxon: cv.classList.contains('on') }); }
    for (const n of m.removedNodes) if (n.classList && n.classList.contains('tcpc')) window.__pcLog.push({ k: 'out', t: performance.now(), fxon: cv.classList.contains('on') });
  } });
  window.__pcObs.observe(st, { childList: true }); window.__pcObs.observe(cv, { attributes: true, attributeFilter: ['class'] }); }"""


def press(pg, seq=(0.9999,)):          # PUSH を 押す（seq＝くじの 数：0.9999 は ハズレ）
    return pg.evaluate(PRESS, [list(seq)])


def shot(pg, name):
    if SHOT: os.makedirs(SHOT, exist_ok=True); pg.screenshot(path=os.path.join(SHOT, name + '.png'))


try:
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'])
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo')
        ctx.add_init_script(FAKE)
        ctx.add_init_script("try { performance.setResourceTimingBufferSize(4000); } catch (e) { }")      # 読んだ ファイルの 記録（はじめは 250こ まで：こえると ルーレットの 絵が 記録に のこらない）
        pg = ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(APP); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(600)
        print('■ 右下の 丸い ボタン（絵＋名前の 札）')
        check(pg.locator('#tcFab').is_visible(), '右下に トレーニングセンターの ボタン')
        check(pg.evaluate("() => typeof window.TCInfo === 'object' && TCInfo.total() === 0 && TCInfo.tickets() === 0"), 'TCInfo（お世話の 合計・チケット）')
        check(pg.evaluate("() => typeof window.TCPlanNotify === 'function' && Array.isArray(TCPlanNotify())"), '作戦会議の 通知（TCPlanNotify）')
        # 第4.139版（まさちゃん 11/10 11:32「トレーニングセンターと思い出フィギュアのアイコンが壁紙と重なってるから、右下に移動して！」）：
        #   場所＝下の タブの すぐ 上・右はし（どの タブでも・スクロール しても）。絵の 下に 名前「トレーニングセンター」の 札（第4.138版は 上の 帯の すぐ 下・右はし）
        POS = """() => { const h = document.querySelector('header.top'), t = document.querySelector('.tabbar'), col = document.querySelector('#fabCol'), f = document.querySelector('#tcFab'), l = f && f.querySelector('.fabl'), i = f && f.querySelector('.fabi');
          if (!h || !t || !col || !f || !l || !i) return null; const R = e => e.getBoundingClientRect(), a = R(h), c = R(f), q = R(l), ii = R(i), cs = getComputedStyle(l), cc = R(col), bn = document.getElementById('ksBnr');
          return { hb: a.bottom, top: c.top, left: c.left, right: c.right, bottom: c.bottom, tab: R(t).top, ct: cc.top, cb: cc.bottom, cl: cc.left, cr: cc.right, name: l.textContent, lt: q.top, lb: q.bottom, lw: q.width, lh: q.height, ib: ii.bottom, iw: ii.width, ih: ii.height,
            ff: cs.fontFamily, fw: cs.fontWeight, fs: cs.fontSize, bg: cs.backgroundImage + cs.backgroundColor, ink: cs.color, line: cs.borderTopColor, order: getComputedStyle(f).order, bnb: bn && !bn.hidden ? R(bn).bottom : 0,
            oshi: (() => { const o = document.querySelector('#oshiFab'); if (!o) return null; const r = R(o); return [r.top, r.bottom, getComputedStyle(o).order, o.querySelector('.fabl').textContent]; })() }; }"""
        #   第4.168版（まさちゃん 11/14 02:12「青四角の項目は、表示されるページは画面を上下にスライドしても、位置がずれずそこにいるようにして！」）：列は いつも 同じ 所
        #   ＝判定の 帯（#minibar）が 出る 高さの すぐ 上（下の タブから 約43px 上）。前は 帯が 出ると 上へ・消えると 下へ 動いた（ページを 送ると 帯が 出たり 消えたり する）
        pg.evaluate("() => document.querySelectorAll('.tabbar button')[2].click()"); pg.wait_for_timeout(500)
        pos = pg.evaluate(POS)
        #   第4.165版（11/13 12:47「推し馬は…トレーニングセンターと思い出フィギュアのアイコンのところの1番上に配置して！」）：列の いちばん 上は 推し馬・その 下が トレーニングセンター
        check(pos is not None and 40 <= pos['tab'] - pos['cb'] <= 50 and pos['cr'] <= 390 and pos['cl'] >= 390 - 84 and pos['ct'] > pos['hb'] + 150 and pos['oshi'] is not None and pos['oshi'][0] == pos['ct']
              and pos['oshi'][1] <= pos['top'] + 0.5 and [pos['oshi'][2], pos['order']] == ['0', '1'] and pos['oshi'][3] == '推し馬',
              f'ボタンの 列は 下の タブの 上（判定の 帯が 出る 高さの すぐ 上：下の タブから {pos and round(pos["tab"] - pos["cb"])}px）・右はし（上の 帯からは はなれて いる）・いちばん 上が 推し馬・その 下が トレーニングセンター（{pos and [round(pos["ct"]), round(pos["cb"]), round(pos["tab"]), round(pos["cl"]), round(pos["cr"])]}）')
        check(pos is not None and pos['name'] == 'トレーニング\nセンター' and pos['ib'] - 9 <= pos['lt'] <= pos['ib'] + 4 and abs(pos['iw'] - 66) < 1 and abs(pos['ih'] - 66) < 1 and 60 <= pos['lw'] <= 76 and 24 <= pos['lh'] <= 32
              and abs(pos['lb'] - pos['bottom']) < 1 and pos['right'] - pos['left'] <= 76,
              f'絵（66px）の 下に 名前の 札「トレーニング／センター」（2行・はば {pos and round(pos["lw"])}px＝絵と ほぼ 同じ はば・高さ {pos and round(pos["lh"])}px）')
        seen = []
        for i in range(5):
            pg.evaluate("(i) => { document.querySelectorAll('.tabbar button')[i].click(); const m = document.getElementById('minibar'); if (m) m.hidden = true; }", i); pg.wait_for_timeout(500)
            q = pg.evaluate(POS); seen.append(q and [round(q['tab'] - q['cb']), round(q['cr']), round(q['ct'])])
        check(len(set(map(str, seen))) == 1 and seen[0] is not None, f'どの タブでも 同じ 場所（判定タブは 下の 帯が ない とき）（{seen[0]}）')
        pg.evaluate("() => { document.querySelectorAll('.tabbar button')[2].click(); window.scrollTo(0, 400); }"); pg.wait_for_timeout(450)
        q = pg.evaluate(POS)
        check(q is not None and abs(q['cb'] - pos['cb']) < 0.6 and abs(q['ct'] - pos['ct']) < 0.6 and abs(q['cr'] - pos['cr']) < 0.6 and pg.locator('#tcFab').is_visible(), f'スクロール しても 同じ 所に いる（列の 下 {q and round(q["cb"])}）')
        pg.evaluate("() => { window.scrollTo(0, 0); document.querySelectorAll('.tabbar button')[2].click(); }"); pg.wait_for_timeout(450)
        hit = pg.evaluate("""() => { const f = document.querySelector('#tcFab'), R = e => e.getBoundingClientRect(), i = R(f.querySelector('.fabi')), l = R(f.querySelector('.fabl'));
          const at = (x, y) => { const e = document.elementFromPoint(x, y); return !!(e && f.contains(e)); };
          return { icon: at(i.left + i.width / 2, i.top + i.height / 2), plate: at(l.left + l.width / 2, l.top + l.height / 2), corner: at(i.left + 2, i.top + 2), leftOut: at(i.left - 6, i.top + i.height / 2) }; }""")
        check(hit['icon'] and hit['plate'] and not hit['corner'] and not hit['leftOut'], f'押せる のは 丸い 絵と 名前の 札だけ（丸の 外の かど・左の すきまは 下の 画面に とどく）{hit}')
        # 名前の 字は いまの 壁紙の 本文の 字・太さ 700・札の 色は 上の 帯と 同じ（壁紙を かえると いっしょに かわる）
        hd = "() => { const cs = getComputedStyle(document.querySelector('header.top')); return cs.backgroundImage + cs.backgroundColor; }"
        check(pos is not None and pos['ff'].split(',')[0].strip().strip('"') == 'BIZ UDPGothic' and pos['fw'] == '700' and pos['bg'] == pg.evaluate(hd), f'いつもの 壁紙：名前の 字は 本文の 字（BIZ UDPGothic）・太さ 700・札は 上の 帯と 同じ 色（{pos and pos["ff"][:24]}）')
        if pg.evaluate("() => !!(window.TengelKisekae && TengelKisekae.on)"):
            pg.evaluate("() => TengelKisekae.apply('pirate')"); pg.wait_for_timeout(900)
            q = pg.evaluate(POS)
            check(q is not None and q['ff'].split(',')[0].strip().strip('"') == 'Zen Kaku Gothic New' and q['fw'] == '700' and q['bg'] == pg.evaluate(hd) and q['bg'] != pos['bg'] and q['ink'] != pos['ink'] and q['line'] != pos['line'] and q['name'] == 'トレーニング\nセンター',
                  f'壁紙を かえる（海賊）→ 名前の 字体・札の 色・線が その 壁紙の ものに（{q and q["ff"][:26]}・{q and q["ink"]}）')
            # 11:32「アイコンが壁紙と重なってる」：判定タブの 上の絵（壁紙）に 列が 重ならない
            pg.evaluate("() => { document.querySelectorAll('.tabbar button')[0].click(); window.scrollTo(0, 0); }"); pg.wait_for_timeout(600); q = pg.evaluate(POS)
            check(q is not None and q['bnb'] > 100 and q['ct'] >= q['bnb'] + 100, f'壁紙（海賊）：判定タブの 上の絵（下の はし {q and round(q["bnb"])}）に ボタンの 列（上の はし {q and round(q["ct"])}）が 重ならない')
            pg.evaluate("() => TengelKisekae.apply('default')"); pg.wait_for_timeout(600)
            check(pg.evaluate(POS)['bg'] == pos['bg'], 'いつもの 壁紙に もどすと 札も もどる')
        # 第4.139版：列の 下に かくれた ままに ならない（ページの いちばん 下・判定タブの 下の 帯・買い目編集の 保存の 帯）
        print('■ 列の 下に かくれた ままに ならない')
        END = """() => { const col = document.querySelector('#fabCol').getBoundingClientRect(), v = [...document.querySelectorAll('main > .view')].find(x => !x.hidden);
          const kids = [...v.children].filter(e => e.getBoundingClientRect().height > 0), last = kids[kids.length - 1].getBoundingClientRect(), mn = document.querySelector('main');
          return { last: last.bottom, ct: col.top, pb: parseFloat(getComputedStyle(mn).paddingBottom), ch: col.height, tab: document.querySelector('.tabbar').getBoundingClientRect().top, atEnd: Math.abs(scrollY + innerHeight - document.documentElement.scrollHeight) < 2 }; }"""
        ends = []
        for i in range(5):
            pg.evaluate("(i) => document.querySelectorAll('.tabbar button')[i].click()", i); pg.wait_for_timeout(450)
            pg.evaluate("() => window.scrollTo(0, 1e7)"); pg.wait_for_timeout(350); ends.append(pg.evaluate(END))
        check(all(e['atEnd'] and e['last'] <= e['ct'] + 0.5 and e['pb'] >= e['ch'] + 60 for e in ends),
              f'5つの タブ：いちばん 下まで スクロール すると さいごの 中身が 列の 上まで 上がる（main の 下の 余白 {round(ends[0]["pb"])}px ≧ 列の 高さ {round(ends[0]["ch"])}px＋下の タブ）{[[round(e["last"]), round(e["ct"])] for e in ends][:2]}')
        pg.evaluate("() => { window.scrollTo(0, 0); document.querySelectorAll('.tabbar button')[0].click(); }"); pg.wait_for_timeout(450)
        # 判定タブの 下の 帯（#minibar：判定の 要点）が 出て いる あいだは 列を その 上へ・消えると もどる
        MB = """() => { const m = document.getElementById('minibar'), b = m.getBoundingClientRect(), c = document.querySelector('#fabCol').getBoundingClientRect(); return { mt: m.hidden ? null : b.top, cb: c.bottom, tab: document.querySelector('.tabbar').getBoundingClientRect().top, pb: document.querySelector('main').style.paddingBottom }; }"""
        pg.evaluate("() => { document.getElementById('minibar').hidden = true; }"); pg.wait_for_timeout(500)
        m0 = pg.evaluate(MB)
        pg.evaluate("() => { const m = document.getElementById('minibar'); if (!document.getElementById('miniBtn').innerHTML) document.getElementById('miniBtn').innerHTML = '<span class=\"lb LB\">B</span><span class=\"mz\">8R 第1 中穴→人気・第2 人気→大穴</span><span class=\"go\">判定へ↓</span>'; m.hidden = false; }"); pg.wait_for_timeout(500)
        m1 = pg.evaluate(MB)
        pg.evaluate("() => { document.getElementById('minibar').hidden = true; }"); pg.wait_for_timeout(500)
        m2 = pg.evaluate(MB)
        check(m0['mt'] is None and 40 <= m0['tab'] - m0['cb'] <= 50 and m1['mt'] is not None and 2 <= m1['mt'] - m1['cb'] <= 10 and abs(m1['cb'] - m0['cb']) < 0.6 and abs(m2['cb'] - m0['cb']) < 0.6 and m1['pb'] == m0['pb'],
              f'第4.168版：判定タブの 下の 帯（判定の 要点）が 出ても 消えても 列は 動かない（{round(m0["cb"])} → {round(m1["cb"])} → {round(m2["cb"])}）・帯は 列の すぐ 下に 出る（帯の 上 {m1["mt"] and round(m1["mt"])}・列の 下 {round(m1["cb"])}＝重ならない）・ページの 下の 余白は かわらない')
        # 買い目編集の 保存の 帯（変更が ある あいだ 下に はりつく）は 列の 手前で 終わる
        pg.evaluate("() => document.querySelectorAll('.tabbar button')[4].click()"); pg.wait_for_timeout(500)
        zok = pg.evaluate("() => { const b = document.querySelector('.zrow [data-act=down]:not([disabled])'); if (!b) return false; b.scrollIntoView({ block: 'center' }); b.click(); return true; }"); pg.wait_for_timeout(600)
        pg.evaluate("() => { const e = document.querySelector('.zedit'); if (e) e.scrollIntoView({ block: 'start' }); }"); pg.wait_for_timeout(600)
        zs = pg.evaluate("() => { const z = document.querySelector('.zsave.sticky'), c = document.querySelector('#fabCol').getBoundingClientRect(); if (!z) return null; const r = z.getBoundingClientRect(), bs = [...z.querySelectorAll('button')].map(b => b.getBoundingClientRect().right); return { right: r.right, cl: c.left, btn: Math.max(...bs), top: r.top, bottom: r.bottom, ct: c.top, cb: c.bottom }; }")
        check(zok and zs is not None and zs['right'] <= zs['cl'] - 3 and zs['btn'] <= zs['right'] and zs['bottom'] > zs['ct'] and zs['top'] < zs['cb'],
              f'買い目編集の 保存の 帯（下に はりついて 列と 同じ 高さ）は 列の 左で 終わる（帯の 右 {zs and round(zs["right"])} ＜ 列の 左 {zs and round(zs["cl"])}）')
        pg.evaluate("() => { const b = document.querySelector('.zsave [data-zact=undo]'); if (b) b.click(); }"); pg.wait_for_timeout(400)
        pg.evaluate("() => { window.scrollTo(0, 0); document.querySelectorAll('.tabbar button')[0].click(); }"); pg.wait_for_timeout(450)
        if not HAVE:
            pg.locator('#tcFab').click(); pg.wait_for_timeout(2500)
            check(not errs, f'エラー なし {errs[:2]}')
            raise SystemExit
        print('■ ひらく')
        pg.locator('#tcFab').click()
        pg.wait_for_function("() => window.TCApp && document.querySelector('#tcOv.on') && !document.querySelector('#tcOv .tcld')", timeout=90000)
        pg.wait_for_timeout(2500)
        st = pg.evaluate("() => ({ on: TCCare.on, horse: !!TCCare.S, field: TCApp.state && TCApp.state.stock, plan: !!document.querySelector('#tcOv .tcpl img'), snd: !!document.querySelector('#tcOv .tcsd') })")
        check(st['on'] and st['plan'] and st['snd'], f'トレーニングセンターが ひらいた（{st}）')
        # 第4.165版：お世話トークンは 5分ごとに 5つ たまる（第4.159版は 10分ごとに 5つ・その 前は 10分に 1つ）→ テストの 間に たまると 数が ずれる ので、時計の テスト（下）まで たまらない ように 数えはじめを 先に しておく
        HOLD = "() => { TCApp.state.stockAt = Date.now() + 7200000; }"
        pg.evaluate(HOLD)
        px = pg.evaluate("() => { const c = document.querySelector('#tcOv .tcgl'); const g = c.getContext('webgl'); const p = new Uint8Array(4); g.readPixels(c.width >> 1, c.height >> 1, 1, 1, g.RGBA, g.UNSIGNED_BYTE, p); return [c.width, c.height, Array.from(p)]; }")
        check(px[0] > 100 and px[1] > 100, f'フィールドの キャンバス {px}')
        # 第4.138版（11/10 10:48 まさちゃん「作戦会議のアイコン、一枚目の赤四角のところにして！」）：お世話の 板（44〜150）の すぐ 下・屋根（241〜）の 上
        pp = pg.evaluate("() => { const s = document.querySelector('#tcOv .tcst').getBoundingClientRect(), p = document.querySelector('#tcOv .tcpl').getBoundingClientRect(); return [(p.top - s.top) / s.height * 1657, (p.bottom - s.top) / s.height * 1657, (p.left - s.left) / s.width * 1052, (p.right - s.left) / s.width * 1052]; }")
        vt, vb, vl, vr = pp[0] + (pp[1] - pp[0]) * 31 / 200, pp[0] + (pp[1] - pp[0]) * 170 / 200, pp[2] + (pp[3] - pp[2]) * 16 / 500, pp[2] + (pp[3] - pp[2]) * 483 / 500
        check(155 <= vt <= 175 and vb <= 244 and 760 <= vl and 1010 <= vr <= 1026, f'作戦会議の ボタン（見える 板）は お世話の 板の すぐ 下（上 {vt:.0f}・下 {vb:.0f}・左 {vl:.0f}・右 {vr:.0f}：板は 730〜1026 × 44〜150・屋根は 241 から）')
        shot(pg, 'tc_open')
        print('■ なめらかさと 細かさ（第4.150版・まさちゃん 11/11 02:43「トレーニングセンターも今は、カクカクしてる！ヌルヌル動くことが絶対！…馬の画質は高く！」）')
        pg.evaluate("() => TCApp._t.govSet(0, true)")      # テストの 機械は 描くのが おそい ことが ある：なめらかさを 守る しくみは 止めて おく（下で 時刻を 作って ためす）
        fr = pg.evaluate("""() => new Promise(res => { const d = TCHorse.draw; let n = 0, k = 0; TCHorse.draw = function () { n++; return d.apply(this, arguments); };
          const t0 = performance.now(); const tick = () => { k++; if (performance.now() - t0 < 1500) requestAnimationFrame(tick); else { TCHorse.draw = d; res([n, k]); } }; requestAnimationFrame(tick); })""")
        check(fr[1] >= 8 and fr[0] >= fr[1] - 3, f'画面の 書きかえ ごとに 馬を 描く（1.5秒で 書きかえ {fr[1]}回・描いた {fr[0]}回：前は 30コマ／秒に おさえて いた＝2回に 1回）')
        cvs = pg.evaluate("() => { const c = document.querySelector('#tcOv .tcgl'), s = document.querySelector('#tcOv .tcst').getBoundingClientRect(); return [c.width, c.height, s.width, devicePixelRatio, [...document.querySelectorAll('#tcOv .tcst canvas')].map(x => x.width)]; }")
        check(abs(cvs[0] - round(cvs[2] * cvs[3])) <= 1 and len(set(cvs[4])) == 1 and abs(cvs[1] - cvs[0] * 1657 / 1052) <= 1, f'キャンバスは 画面の 細かさ いっぱい（幅 {cvs[0]}px＝置き場 {cvs[2]:.0f}pt × {cvs[3]}・3まい とも 同じ）')
        # なめらかさを 守る しくみ（govern）：時刻を 作って 入れる（コマの 間 16.7ms＝なめらか・34ms＝2回に 1回 落ちる）
        gv = pg.evaluate("""() => { const T = TCApp._t, G = T.gov, c = document.querySelector('#tcOv .tcgl'); let t = 1e7; const out = {};
          const feed = (ms, n) => { for (let i = 0; i < n; i++) { t += ms; T.govern(t); } return [G.step, G.q, G.off, c.width]; };
          const fresh = () => { T.govSet(0, false); G.base = 0; G.last = 0; t += 1e5; };
          fresh(); out.w0 = c.width;
          out.smooth = feed(16.7, 600);                       // なめらか：そのまま
          out.slow1 = feed(34, 1 + 45 + 120);                 // おそい → 1段 下げる
          out.better = feed(16.7, 45 + 120 + 200);            // 下げたら なめらかに なった → そのまま（見はりは つづける）
          out.slow2 = feed(34, 45 + 120);                     // また おそい → もう 1段
          out.same2 = feed(34, 45 + 120);                     // 下げても かわらない → 1段 もどして おわり
          out.after = feed(34, 600);                          // もう 下げない
          fresh(); out.lp1 = feed(33.4, 1 + 45 + 120);        // 省電力モード（いつも 30回／秒）：1段 下げる
          out.lp2 = feed(33.4, 45 + 120);                     // かわらない → もとに もどして おわり
          out.lp3 = feed(33.4, 600);
          fresh(); out.hitch = feed(16.7, 100).concat(feed(400, 1), feed(16.7, 400));      // 1コマ だけ 長く 止まった（馬を 読みこんだ など）→ かわらない
          fresh(); out.some = (() => { for (let i = 0; i < 900; i++) { t += (i % 4 === 0 ? 34 : 16.7); T.govern(t); } return [G.step, G.q, G.off, c.width]; })();      // 4回に 1回 落ちる（25%）→ かわらない
          T.govSet(0, true); out.end = [G.step, G.q, G.off, c.width];
          return out; }""")
        w0 = gv['w0']
        check(gv['smooth'] == [0, 1, False, w0] and gv['hitch'][-4:] == [0, 1, False, w0] and gv['some'] == [0, 1, False, w0],
              f'なめらかな 間は 細かさを かえない（60コマ／秒・1コマ だけ 止まった・4回に 1回 落ちる：{gv["smooth"]}・{gv["hitch"][-4:]}・{gv["some"]}）')
        check(gv['slow1'][:3] == [1, 0.82, False] and abs(gv['slow1'][3] - w0 * 0.82) <= 1 and gv['better'] == gv['slow1'],
              f'コマが 落ちる（4割 以上）→ 細かさを 1段 下げる（幅 {w0} → {gv["slow1"][3]}px）・なめらかに なったら そのまま（{gv["better"]}）')
        check(gv['slow2'][:3] == [2, 0.68, False] and abs(gv['slow2'][3] - w0 * 0.68) <= 1 and gv['same2'][:3] == [1, 0.82, True] and gv['after'] == gv['same2'],
              f'また 落ちる → もう 1段（{gv["slow2"]}）・下げても かわらない → 1段 もどして おわり（{gv["same2"]}）・その あとは かえない')
        check(gv['lp1'][:3] == [1, 0.82, False] and gv['lp2'] == [0, 1, True, w0] and gv['lp3'] == gv['lp2'] and gv['end'] == [0, 1, True, w0],
              f'いつも 30回／秒（省電力モード など）：1段 下げても かわらない → もとの 細かさに もどして おわり（{gv["lp1"]} → {gv["lp2"]}）')
        # 第4.151版（まさちゃん 11/11 09:07）：お世話の 直し。きまり（5回まで・7秒・抽選の 順・お花なし）は test_tc_care.js（画面なし）。ここは 本物の 馬で たしかめる
        print('■ お世話：早く 始まる・止めた 反応は 消える（第4.151版）／馬は 横に ならない（第4.156版）')
        fl = pg.evaluate("""() => { const [HO, BR] = TCCare._hb, t = TCCare.S.lastT;
          const y = (st, tt) => { const q = TCHorse.wherePose(HO, TCHorse.pose(HO, st, tt), 'withers'); return q ? q[1] : NaN; };
          const st0 = Object.assign({}, BR, { sl: 0, rise: 0, reacts: [] }), stF = Object.assign({}, st0, { reacts: [{ k: 'frisk', t0: t - 0.5, dur: 2.2 }] }), stC = Object.assign({}, st0, { reacts: [{ k: 'frisk', t0: t - 0.5, dur: 2.2, cut: t - 0.3 }] });
          const d = (a, b) => Math.max(...[0, 0.06, 0.12, 0.18, 0.24, 0.3].map(k => Math.abs(y(a, t + k) - y(b, t + k))));
          return { stand: d(stF, st0), cut: d(stC, st0) }; }""")
        check(fl['stand'] > 1.5 and fl['cut'] < 0.3,
              f'立って いる 馬は はしゃぐ 反応で はずむ（{fl["stand"]:.1f}px）・とちゅうで 止めた 反応（cut）は 0.25秒で 消える（{fl["cut"]:.2f}px）')
        # 第4.156版（まさちゃん 2026/11/12 04:20「トレーニングセンターの馬の寝転ぶ演出は全部消して！」）：夜の「とくべつ」・見本用の 'sleep' でも 横に ならない（顔を 上げて まわりを 見る）。
        #   本物の 馬の 形で 40秒ぶん 進めて、ねる 形（mode 'sleep'）に ならない・横に なる 強さが 0 の まま・背の 高さが 立って いる ときから 下がらない ことを 見る
        #   第4.157版（テストの 直し）：背の 高さは 体の 座標（anchorPose：地面 0・画面の 場所や 奥行きに よらない）で はかる。前の はかり方（画面の 場所 wherePose を 馬の 場所で 引いて わる）は、
        #   wherePose が「いま 画面に いる 馬」の 場所で 計算する ので、見本の 馬が 歩くと 歩いた 分が そのまま「下がった」に 見えた（乱数しだいで 落ちた・馬は 横に なって いない）。
        #   乱数は たねを 決めて 6とおり（歩く ときの 背の ゆれは 0.03 まで・横に なる 形〈道具用：sl＝1〉は 0.64 下がる）
        nl = pg.evaluate("""() => { const HO = TCCare._hb[0], out = [];
          const rng = (s) => () => { s |= 0; s = s + 0x6D2B79F5 | 0; let t = Math.imul(s ^ s >>> 15, 1 | s); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
          const y = (st, tt) => { const q = TCHorse.anchorPose(HO, TCHorse.pose(HO, st, tt), 'withers'); return q ? -q[1] : NaN; };      // 背（き甲）の 高さ（体の 座標・下が ＋）
          const st1 = TCHorse.brain({ tod: 'night', stand: false }), lie = y(Object.assign({}, st1, { sl: 1 }), 500) - y(Object.assign({}, st1), 500);
          for (let seed = 1; seed <= 6; seed++)
            for (const [nm, f, rnd] of [['special', ['special', 'special'], rng(seed * 7919)], ['sleep', ['sleep:8', 'sleep:8'], rng(seed * 104729)], ['rnd', [], () => 0.01]]) {
              const st = TCHorse.brain({ tod: 'night', force: f.slice(), stand: false }); let t = 500, lay = 0, low = -1e9; const modes = new Set(); const y0 = y(Object.assign({}, st), t);
              for (let i = 0; i < 60 * 40; i++) { t += 1 / 60; TCHorse.step(HO, st, t, 1 / 60, rnd); modes.add(st.mode); lay = Math.max(lay, st.sl || 0, st.rise || 0, st.doze || 0, st.sleep || 0);
                if (i % 12 === 0) low = Math.max(low, y(st, t) - y0); }
              out.push([nm, [...modes].sort().join('/'), lay, +low.toFixed(4), st.want.look[0]]); }
          return { out, lie: +lie.toFixed(3) }; }""")
        nlie = nl['lie']; nl = nl['out']
        check(len(nl) == 18 and all('sleep' not in o[1] and o[2] == 0 and o[3] < 0.05 for o in nl) and not any('run' in o[1] for o in nl if o[0] != 'sleep') and nlie > 0.4 and any('walk' in o[1] for o in nl),
              f'夜でも ねない：とくべつ・見本用の sleep・くじ（30回に 1回）を 乱数 6とおりで、どれも 横に ならない・夜は 走らない（動き {sorted(set(o[1] for o in nl))}・横に なる 強さ {max(o[2] for o in nl)}・'
              f'背が 下がった 分〈体の 座標〉 いちばん 大きくて {max(o[3] for o in nl)}：歩く ゆれ だけ。横に なる 形なら {nlie} 下がる）')
        lat = pg.evaluate("""async () => { const [HO, BR] = TCCare._hb, S = TCCare.S; Object.assign(BR, { x: 526, y: 820, dir: -1.2, mode: 'idle', until: S.lastT + 60 }); await new Promise(r => setTimeout(r, 400));
          const t0 = S.lastT; TCCare.press(t0, 'pet'); const h = BR.hurry, m0 = BR.mode, zb = S.zB ? S.zB.z : 0;
          for (let i = 0; i < 1200 && S.phase !== 'pet'; i++) await new Promise(r => requestAnimationFrame(r));
          const t1 = S.lastT, ph = S.phase, y1 = BR.y, x1 = BR.x, side = Math.abs(Math.sin(BR.dir)); S.petIdle = -1e9;
          for (let i = 0; i < 400 && S.phase !== 'idle'; i++) await new Promise(r => setTimeout(r, 50));
          return { lat: t1 - t0, ph, h, m0, zb, y1, x1, side, end: S.phase, cool: S.coolUntil > S.lastT, z: S.zoom.z }; }""")
        check(lat['ph'] == 'pet' and lat['h'] == 2.8 and lat['m0'] == 'idle' and lat['zb'] > 2.2 and lat['lat'] < 2.0 and abs(lat['y1'] - 820) < 25 and abs(lat['x1'] - 526) < 60 and lat['side'] < 0.4 and lat['end'] == 'idle' and not lat['cool'] and lat['z'] == 1,
              f'「撫でる」を 押して から 撫でられる まで {lat["lat"]:.2f}秒（いちばん 奥で むこう向き：歩かないで その場で 横向きに・カメラは 押した ときから 寄る {lat["zb"]:.2f}倍。第4.150版は 14.8秒）・撫でずに もどっても 7秒の 待ちは ない')
        # 第4.159版（まさちゃん 11/12 12:48「25MAXの時に撫でてても、お世話トークンが最大だよ！って表示されるようにして！」）：トークンが 25（最大）の ときに「撫でる」を 押す → 札が 出る・24こ までは 出ない
        mt = pg.evaluate("""async () => { const S = TCCare.S, s0 = S.stock, out = {};
          const go = async (n) => { S.stock = S.stockShow = n; S.coolUntil = -1e9; S.petN = 0; S.maxTagT = -9; S.fx = S.fx.filter(f => f.k !== 'tagUI'); TCCare.press(S.lastT, 'pet');
            const tags = S.fx.filter(f => f.k === 'tagUI').map(f => [f.txt, f.x, f.y]); const w0 = performance.now(); while (performance.now() - w0 < 12000 && S.phase !== 'pet') await new Promise(r => requestAnimationFrame(r));
            const ph = S.phase; S.petIdle = -1e9; const w1 = performance.now(); while (performance.now() - w1 < 12000 && S.phase !== 'idle') await new Promise(r => requestAnimationFrame(r)); return { tags, ph }; };
          out.full = await go(25); out.less = await go(24); S.stock = S.stockShow = s0; S.coolUntil = -1e9; S.petN = 0; return out; }""")
        pg.wait_for_timeout(200); pg.evaluate(HOLD)      # （最大の 間は 数えはじめが いまの 時刻に なる → もう一度 先へ）
        check(len(mt['full']['tags']) == 1 and mt['full']['tags'][0][0] == 'お世話トークンが 最大だよ！' and mt['full']['ph'] == 'pet' and mt['less']['tags'] == [] and mt['less']['ph'] == 'pet',
              f'トークンが 25（最大）の ときに「撫でる」を 押す → 札「お世話トークンが 最大だよ！」（撫でるは そのまま できる）・24こ までは 出ない（{mt["full"]["tags"]}）')
        # 第4.159版（まさちゃん 11/12 13:27「お世話トークンが25MAXの場合、なかよしハートが10個溜まっても抽選せずに、お世話トークンが20個を切ってから、お世話トークンゲットできるか抽選するようにしてほしい！」）：
        #   ハートが 10こ・トークン 25こ／20こ → 抽選は 待つ。19こ（20こを 切った）でも 説明書が 開いて いる 間は 始まらない（アプリが 止める）→ 閉じたら ひとりでに 抽選（ここでは ハズレ：ふぅ〜）→ ハートは 0に
        lh = pg.evaluate("""async () => { const S = TCCare.S, s0 = S.stock, wait = ms => new Promise(r => setTimeout(r, ms)), out = {}, stage = document.querySelector('#tcOv .tcst');
          const idle = async ms => { const w = performance.now(); while (performance.now() - w < ms && !(S.phase === 'idle' && !S.busy && !S.mode)) await wait(50); };
          await idle(20000); S.coolUntil = -1e9; S.petN = 0; S.got = []; S.test = Object.assign(S.test || {}, { win: false }); S.fx = S.fx.filter(f => f.k !== 'note');
          S.heart = S.heartShow = 10; S.stock = S.stockShow = 25; await wait(2600); out.hold = [!!S.lot, S.mode, S.heart, S.stock];
          S.stock = S.stockShow = 20; await wait(2600); out.hold20 = [!!S.lot, S.mode, S.heart, S.stock];
          TCGuide.open(stage, {}); S.stock = S.stockShow = 19; await wait(2600); out.guide = [!!S.lot, S.mode, S.heart, TCGuide.isOpen()];
          TCGuide.close(); const w0 = performance.now(); while (performance.now() - w0 < 15000 && S.mode !== 'pet') await wait(30);
          out.start = [S.mode, +((performance.now() - w0) / 1000).toFixed(2), S.fx.filter(f => f.k === 'note').map(f => f.txt)];
          const w1 = performance.now(); while (performance.now() - w1 < 20000 && !S.lot) await wait(30); out.lot = S.lot ? S.lot.win : null;
          await wait(300); await idle(40000); out.end = [S.heart, S.stock, S.phase, TCApp.state.heart];
          S.stock = S.stockShow = s0; S.coolUntil = -1e9; S.petN = 0; return out; }""")
        pg.wait_for_timeout(200); pg.evaluate(HOLD)
        check(lh['hold'] == [False, None, 10, 25] and lh['hold20'] == [False, None, 10, 20] and lh['guide'] == [False, None, 10, True] and lh['start'][0] == 'pet' and 0.8 <= lh['start'][1] <= 4.0
              and lh['start'][2] == ['なかよしハートの 抽選！'] and lh['lot'] is False and lh['end'][:3] == [0, 19, 'idle'],
              f'ハートの 抽選は トークンが 20こ未満の とき だけ：ハート 10こ・トークン 25こ／20こ＝抽選しない（待つ）→ 19こでも 説明書が 開いて いる 間は 始まらない → 閉じて {lh["start"][1]}秒で ひとりでに 抽選（{lh["start"][2]}）→ ハートは 0に（{lh["end"]}）')
        # 第4.152版（バグ直し・まさちゃん 11/11 12:10「これおかしくならないようにしてね！」）：はしを 走って いる 馬を 撫でる → 画面に 入る 所まで 少し 歩く ときに 行き先の まわりを 回りつづけて 始まらなかった
        rn = pg.evaluate("""async () => { const [HO, BR] = TCCare._hb, S = TCCare.S, out = [];
          for (const [x0, y0, d0, mode] of [[526, 1090, 0, 'run'], [935, 1000, -1.6, 'idle'], [118, 1150, 1.6, 'idle']]) {
            Object.assign(BR, { x: x0, y: y0, dir: d0, mode: 'idle', until: S.lastT + 90 }); S.coolUntil = -1e9; S.petN = 0;
            if (mode === 'run') Object.assign(BR, { mode: 'run', lap: 0.3, runV: 3.2, runEnd: 0, runT: 9, tPrev: null, toTrack: true });
            await new Promise(r => setTimeout(r, 700)); const p0 = [Math.round(BR.x), Math.round(BR.y)], t0 = S.lastT; TCCare.press(t0, 'pet');
            const w0 = performance.now(); while (performance.now() - w0 < 12000 && S.phase !== 'pet') await new Promise(r => requestAnimationFrame(r));
            const lat = S.lastT - t0, ph = S.phase; for (let i = 0; i < 20 && S.zB; i++) await new Promise(r => setTimeout(r, 50));
            const e = TCHorse.extent(HO), z = S.zoom, sx = x => (x - z.cx) * z.z + 1052 / 2;
            out.push({ p0, lat, ph, x: Math.round(BR.x), l: Math.round(sx(e[0])), r: Math.round(sx(e[2])), cos: Math.cos(BR.dir) }); S.petIdle = -1e9;
            const w1 = performance.now(); while (performance.now() - w1 < 12000 && S.phase !== 'idle') await new Promise(r => requestAnimationFrame(r));
          }
          return out; }""")
        check(all(q['ph'] == 'pet' and q['lat'] < 4.0 and q['l'] >= -6 and q['r'] <= 1058 for q in rn) and rn[1]['cos'] < -0.9 and rn[2]['cos'] > 0.9,
              '走って いる 馬・右の はし・左の はしの 馬を 撫でる：' + '／'.join(f'{q["p0"]} → {q["lat"]:.2f}秒（x {q["x"]}・画面の {q["l"]}〜{q["r"]}）' for q in rn) + '・はしの 馬は 顔を まん中へ 向ける')
        print('■ ごはん（エサ・3D の バケツ）')
        stock0 = pg.evaluate("() => TCCare.S.stock")
        stage_click(pg, 327, 1494); pg.wait_for_timeout(1200)
        check(pg.evaluate("() => !!TCCare.S.chooser"), 'ごはんを 押すと 3つ から えらぶ')
        stage_click(pg, 270, 1262)
        ok = False
        for _ in range(120):
            pg.wait_for_timeout(500)
            if pg.evaluate("() => !!(TCCare.S.feed && TCCare.S.feed.b3)"): ok = True; break
        check(ok, '馬が 来て 3D の バケツが 出た')
        if ok:
            pg.wait_for_timeout(2500); shot(pg, 'tc_feed')
            check(pg.evaluate("() => Array.isArray(window.BR_props_dummy) || true"), '（写真）')
        for _ in range(120):
            pg.wait_for_timeout(500)
            if pg.evaluate("() => TCCare.S.phase === 'idle' && !TCCare.S.feed"): break
        # 第4.159版（まさちゃん 2026/11/12 10:37「①お世話の最大トークン25回にして！②お世話が終わったあとに、pushボタンが出てくるようにして…当選なら押したタイミングで、当選した内容がでてくるようにして！
        #   ハズレは音だけで知らせて！…③…お世話トークンを1個使う、か、お世話トークンをまとめて使う、が選べるようにして欲しい！」）：きまりは test_tc_care.js・ここは 本物の 画面
        print('■ お世話の あとの PUSH（第4.159版）')
        pg.evaluate(SE_WRAP); pg.evaluate("() => { TCCare.S.high = 0; TCApp.state.high = 0; }")
        okp = True
        try: pg.wait_for_function(PUSH_LIVE, timeout=30000)
        except Exception: okp = False
        pg.wait_for_timeout(1000); shot(pg, 'tc_push')
        p0 = pg.evaluate(PU); G = pg.evaluate("() => TCCare.PUSHG"); mx = pg.evaluate("() => [TCCare.RULE.stockMax, TCApp._t.ODDS.tokenMax]")
        px = pg.evaluate(OVPX, [[G['x'], G['y'] - 40], [128, 1494], [G['m1'][0] - 100, G['m1'][1] - 20], [G['mn'][0] - 100, G['mn'][1] - 20]])
        check(okp and p0['live'] and p0['stock'] == stock0 and p0['total'] == 0 and p0['cares'] == 0 and p0['rs'] == 0 and p0['push'] and p0['spush'] and not p0['bulk'] and p0['pop'] == [] and mx == [25, 25],
              f'ごはんが おわると PUSH が 出る：トークンは まだ 使って いない（{stock0}こ の まま）・お世話の 数も まだ・「PUSH が 出て いる」を 保存・トークンの 上限は 25（{mx}）')
        check(px[0][0] > 170 and px[0][1] < 100 and px[0][3] > 240 and px[1][3] == 0 and px[2][0] > 215 and 150 < px[2][1] < 215 and px[2][2] < 130 and min(px[3][:3]) > 215 and 420 < G['y'] * 614 / 1657 and G['y'] + G['w'] * G['ar'] / 2 < 1657,
              f'画面の 下に 赤い PUSH（色 {px[0]}）・お世話の 4つの ボタンは かくれる（撫でるの 所は すきとおる {px[1]}）・スイッチは「1個 使う」が 金色（{px[2][:3]}）・「まとめて 使う」は 白（{px[3][:3]}）')
        pg.evaluate("() => TCCare.press(TCCare.S.lastT, 'pet')"); stage_click(pg, 128, 1494); pg.wait_for_timeout(300); pb = pg.evaluate(PU)
        check(pb['mode'] is None and pb['phase'] == 'idle' and '先に PUSH を 押してね' in pb['tags'] and pb['live'] and pb['stock'] == stock0, f'PUSH が 出て いる 間は ほかの お世話は 始まらない（{pb["tags"][-1:]}）')
        stage_click(pg, *G['mn']); pg.wait_for_timeout(400); s1 = pg.evaluate(PU); px1 = pg.evaluate(OVPX, [[G['mn'][0] - 100, G['mn'][1] - 20]])
        stage_click(pg, *G['m1']); pg.wait_for_timeout(400); s2 = pg.evaluate(PU)
        check(s1['bulk'] and s1['sbulk'] and s1['live'] and s1['stock'] == stock0 and px1[0][0] > 215 and px1[0][2] < 130 and not s2['bulk'] and not s2['sbulk'],
              f'スイッチ：「まとめて 使う」を 押すと 金色に（{px1[0][:3]}）・保存する → 「1個 使う」に もどす（押しても トークンは 減らない）')
        pg.evaluate(SES); d = press(pg); pg.wait_for_timeout(150); p1 = pg.evaluate(PU); se1 = pg.evaluate(SES)
        check(d == 1 and p1['stock'] == stock0 - 1 and p1['saved'] == stock0 - 1 and p1['total'] == 1 and p1['cares'] == 1 and p1['pop'] == [] and p1['wal'] == p0['wal'] and 'token' in se1 and 'pfo' in se1 and not any(x in se1 for x in ('piron', 'dedeen', 'kyuin')),
              f'PUSH に 指を 置いた 瞬間：トークン −1（{stock0} → {p1["stock"]}・すぐ 保存）・お世話 1回に 数える・ハズレは 音 だけ（プフォ：{se1}）・札は 出ない')
        pg.wait_for_timeout(1000); p2 = pg.evaluate(PU); px2 = pg.evaluate(OVPX, [[128, 1494]])
        check(not p2['live'] and not p2['push'] and not p2['spush'] and px2[0][3] > 240, f'「1個 使う」：1回 押したら PUSH は 消える（保存も）・お世話の ボタンが もどる（{px2[0]}）')
        tot = pg.evaluate("() => [TCCare.S.stock, TCApp.state.total, TCApp.state.cares]")
        check(tot[0] == stock0 - 1 and tot[1] >= 1, f'お世話トークンを 1つ 使って、お世話の 合計が ふえた {stock0} → {tot}')
        rsn = pg.evaluate("() => Object.assign({}, TCApp.state.rs)")
        check(rsn['n'] == 1 and rsn['at'] == 0, f'お世話 1回 → 馬の リセットの 数えが 1（タイマーは まだ：5回から）（{rsn}）（第4.144版）')
        # 第4.152版（まさちゃん 11/11 10:13「お掃除は、15分に一回、ゴミがフィールドに散乱する仕組みにして！片付けられない限りは、新しいゴミが出ないようにして！」
        #   「お掃除は、連続はできない。ゴミが出現した時のみ」「ゴミは落ちる場所は5箇所、ランダムに出現」・10:16「うんちが出たら掃除できるようにして！」・09:43 3D の ほうき・ちりとり）
        #   きまり（ゴミか うんちが ある とき だけ・1回で ぜんぶ・さわらない まま 25秒）は test_tc_care.js。ここは 本物の 画面：散らばる・3D の 道具・片付けた あとの 15分・時計・ひらき直し
        print('■ ゴミの おそうじ（第4.152版）')
        keep = pg.evaluate("() => { const s = TCApp.state; return JSON.stringify({ cares: s.cares, total: s.total, rs: s.rs, stock: s.stock, high: s.high }); }")
        TR = """() => { const [HO, BR] = TCCare._hb, s = TCApp.state, O = TCApp._t.ODDS, g = (a, b) => Math.hypot(a.x - b.x, (a.y - b.y) * 2); let dmin = 1e9;
          for (let i = 0; i < s.trash.length; i++) for (let j = i + 1; j < s.trash.length; j++) dmin = Math.min(dmin, g(s.trash[i], s.trash[j]));
          return { n: s.trash.length, xy: s.trash.map(q => [q.x, q.y]), live: (BR.trash || []).map(q => [q.x, q.y, q.items.length, q.items.every(it => it.k >= 0 && it.k < 4 && it.w > 0.25 && it.w < 0.7)]), dmin,
            tex: HO.trashTex.filter(Boolean).map(x => [x.w, x.h]), min: O.trashMin, N: O.trashN, trashIn: TCCare.S.trashIn, left: (s.trashAt - Date.now()) / 60000, stock: TCCare.S.stock, phase: TCCare.S.phase }; }"""
        tr = pg.evaluate(TR)
        xs = [q[0] for q in tr['xy']]; ys = [q[1] for q in tr['xy']]
        check(tr['n'] == 5 and tr['N'] == 5 and tr['min'] == 15 and len(tr['live']) == 5 and all(2 <= q[2] <= 4 and q[3] for q in tr['live']) and tr['dmin'] >= 150 and min(xs) >= 170 and max(xs) <= 882 and min(ys) >= 840 and max(ys) <= 1380
              and len(tr['tex']) == 4 and tr['trashIn'] == 0,
              f'はじめて ひらくと ゴミが 5か所に 散らばって いる（山 1つに 絵 2〜4こ・4つの 絵 {tr["tex"]}・たがいに {tr["dmin"]:.0f} 以上 はなれて いる・歩ける 所の 中）')
        sp = pg.evaluate("""() => { const T = TCApp._t.trash; let ok = 0, near = 1e9, dm = 1e9, kinds = new Set(), cnt = {};
          for (let k = 0; k < 300; k++) { const hx = 246 + Math.random() * 560, hy = 800 + Math.random() * 580, a = T.spots(Math.random, hx, hy); if (a.length === 5) ok++;
            for (const q of a) { near = Math.min(near, Math.hypot(q.x - hx, (q.y - hy) * 2)); for (const it of T.items(q.sd)) kinds.add(it.k); const n = T.items(q.sd).length; cnt[n] = (cnt[n] || 0) + 1; if (JSON.stringify(T.items(q.sd)) !== JSON.stringify(T.items(q.sd))) ok = -1e9; }
            for (let i = 0; i < a.length; i++) for (let j = i + 1; j < a.length; j++) dm = Math.min(dm, Math.hypot(a[i].x - a[j].x, (a[i].y - a[j].y) * 2)); }
          return { ok, near, dm, kinds: [...kinds].sort(), cnt }; }""")
        check(sp['ok'] == 300 and sp['near'] >= 170 and sp['dm'] >= 150 and sp['kinds'] == [0, 1, 2, 3] and sorted(sp['cnt'].keys()) == ['2', '3', '4'],
              f'散らばる 場所（300回）：いつも 5か所・馬の 足もとは さける（いちばん 近くて {sp["near"]:.0f}）・たがいに {sp["dm"]:.0f} 以上・4つの 絵が まざる・山の 中身は 種から いつも 同じ')
        for _ in range(16):                  # ごはんの あとの 当たりの 札が 出て いる 間は 押せない：押せる ように なる まで
            stage_click(pg, 526, 1494); pg.wait_for_timeout(600)
            if pg.evaluate("() => TCCare.S.mode === 'clean'"): break
        for _ in range(40):
            pg.wait_for_timeout(250)
            if pg.evaluate("() => TCCare.S.phase === 'clean' && !!TCCare._hb[1].props"): break
        cs = pg.evaluate("""() => { const [HO, BR] = TCCare._hb, S = TCCare.S, C = S.clean, s = TCApp.state;
          return { phase: S.phase, n: C ? C.tg.length : 0, props: (BR.props || []).map(q => q.P.meta.i), st: s.trash.length, left: (s.trashAt - Date.now()) / 60000, stock: S.stock, live: (BR.trash || []).length, z: S.zoom.z }; }""")
        check(cs['phase'] == 'clean' and cs['n'] == 5 and cs['props'] == [6888, 21000] and cs['st'] == 0 and 14.5 < cs['left'] <= 15.01 and cs['stock'] == tr['stock'] and cs['live'] == 5,
              f'「おそうじ」を 押す → 3D の ちりとりと ほうきが 出る（三角 {[v // 3 for v in cs["props"]]}こ）・トークンは まだ 使わない（おわった あとの PUSH で：第4.159版）・その ときに「片付けた」（次の ゴミまで {cs["left"]:.1f}分）・ゴミは まだ 見えて いる')
        shot(pg, 'tc_clean_tools')
        # 第4.165版（まさちゃん 11/13 12:59「ほうきと、ちりとりも自由に動かして、ゴミのところまで持っていってほうきで片付けられるようにして！今は、触れると瞬間移動しちゃう！」）：
        #   道具の ない 所を さわっても 何も 動かない → ほうきを つかんで 山の むこうがわへ 運ぶ → 山を ちりとりへ 押す（ちりとりは 自分では 動かない）
        tp = pg.evaluate("""async () => { const S = TCCare.S, C = S.clean, raf = () => new Promise(r => requestAnimationFrame(r)); const b0 = [C.bro.x, C.bro.y], p0 = [C.pan.x, C.pan.y];
          let fx = 0, fy = 0, best = -1;                                         // ほうきからも ちりとりからも 遠い 所（道具の ない 所）
          for (let x = 120; x <= 932; x += 58) for (let y = 820; y <= 1420; y += 60) { if (TCCare.grabAt(x, y) !== null) continue; const d = Math.min(Math.hypot(x - b0[0], y - b0[1]), Math.hypot(x - p0[0], y - p0[1])); if (d > best) { best = d; fx = x; fy = y; } }
          TCCare.input('down', fx, fy, S.lastT); for (let i = 1; i <= 8; i++) { await raf(); TCCare.input('move', fx + 6 * i, fy + 5 * i, S.lastT); }
          const g = C.grab, tag = S.fx.some(f => f.k === 'tag' && f.txt === 'ほうきか ちりとりを つかんでね'); TCCare.input('up', fx + 48, fy + 40, S.lastT); await raf();
          return { far: Math.round(best), grab: g, tag, bro: Math.hypot(C.bro.x - b0[0], C.bro.y - b0[1]), pan: Math.hypot(C.pan.x - p0[0], C.pan.y - p0[1]), got: C.got }; }""")
        check(tp['far'] > 150 and tp['grab'] is None and tp['tag'] and tp['bro'] < 0.5 and tp['pan'] < 0.5 and tp['got'] == 0,
              f'道具の ない 所（ほうき・ちりとりから {tp["far"]}）を さわって なぞる → ほうきも ちりとりも 動かない（瞬間移動 しない）・札「ほうきか ちりとりを つかんでね」')
        sw = pg.evaluate("""async () => { const S = TCCare.S, C = S.clean, raf = () => new Promise(r => requestAnimationFrame(r)); let n = 0; const mid = [], jump = [], pan0 = [C.pan.x, C.pan.y];
          const drag = async (from, to, k, stop) => { let q = from; for (let i = 1; i <= k && !(stop && stop()); i++) { await raf(); q = [from[0] + (to[0] - from[0]) * i / k, from[1] + (to[1] - from[1]) * i / k]; TCCare.input('move', q[0], q[1], S.lastT); } return q; };
          while (C.tg.some(q => !q.done) && n < 12) { const T = C.tg.find(q => !q.done), o = T.o, pn = { x: C.pan.x, y: C.pan.y }, g0 = C.got, ux = o.x - pn.x, uy = o.y - pn.y, L = Math.hypot(ux, uy) || 1, far = [o.x + ux / L * 140, o.y + uy / L * 70];
            const b0 = [C.bro.x, C.bro.y]; TCCare.input('down', b0[0], b0[1], S.lastT); const gr = C.grab; jump.push(Math.hypot(C.bro.x - b0[0], C.bro.y - b0[1]));
            const p1 = await drag(b0, far, 20), p2 = await drag(p1, [pn.x, pn.y], 36, () => C.got > g0);
            mid.push([Math.round(C.pan.x), Math.round(C.pan.y), C.got - g0, gr]); TCCare.input('up', p2[0], p2[1], S.lastT); n++; await new Promise(r => setTimeout(r, 150)); }
          return { n, got: C.got, phase: S.phase, mid, jump: Math.max.apply(null, jump), panMove: Math.hypot(C.pan.x - pan0[0], C.pan.y - pan0[1]) }; }""")
        check(sw['n'] <= 5 and sw['got'] == 5 and sw['phase'] == 'cleanwait' and all(90 <= m[0] <= 962 and 790 <= m[1] <= 1430 and m[2] >= 1 and m[3] == 'broom' for m in sw['mid']) and sw['jump'] < 0.5 and sw['panMove'] < 0.5,
              f'ほうきを つかんで 運んで 山を ちりとりへ 押す：なぞる たびに 入る（{sw["n"]}回 なぞって {sw["got"]}こ）・つかんだ 瞬間は 動かない（{sw["jump"]:.1f}）・ちりとりは 自分では 動かない（{sw["panMove"]:.1f}）・フィールドの 中')
        for _ in range(60):
            pg.wait_for_timeout(250)
            if pg.evaluate("() => TCCare.S.phase === 'idle' && !TCCare.S.clean"): break
        af = pg.evaluate(TR)
        check(af['phase'] == 'idle' and af['n'] == 0 and len(af['live']) == 0 and 13.7 < af['left'] <= 15 and 820 < af['trashIn'] <= 900,      # 第4.165版：ほうきを つかんで 運ぶ ぶん、片付けに 時間が かかる（前は 14.4分・860秒 より 上）
              f'片付いた：ゴミは ない・次の ゴミまで {af["left"]:.1f}分（片付ける までは 次が 出ない）')
        # 第4.159版：おそうじの あとも PUSH。「まとめて 使う」＝トークンが ある 間 つづけて 押せる（押した 回数ぶん 減る）・当たりは 押した 瞬間に（100P＝ピロン・200P＝デデーン）・「おわる」で 消える
        okb = True
        try: pg.wait_for_function(PUSH_LIVE, timeout=30000)
        except Exception: okb = False
        pg.wait_for_timeout(700); pg.evaluate("() => { TCCare.S.high = 0; TCApp.state.high = 0; }")
        stage_click(pg, *G['mn']); pg.wait_for_timeout(350); b0 = pg.evaluate(PU); pg.evaluate(SES)
        r100 = pg.evaluate(RND_FOR, {'k': 'pt', 'v': 100}); r200 = pg.evaluate(RND_FOR, {'k': 'pt', 'v': 200})
        d1 = press(pg); e1 = pg.evaluate(SES); q1 = pg.evaluate(PU)
        d2 = press(pg, [r100]); e2 = pg.evaluate(SES); q2 = pg.evaluate(PU)
        d3 = press(pg, [r200]); e3 = pg.evaluate(SES); q3 = pg.evaluate(PU)
        pg.wait_for_timeout(350); shot(pg, 'tc_push_bulk'); pxe = pg.evaluate(OVPX, [[G['end'][0] - 80, G['end'][1] - 14]])
        check(okb and b0['bulk'] and b0['stock'] == af['stock'] and [d1, d2, d3] == [1, 1, 1] and q3['stock'] == b0['stock'] - 3 and q3['saved'] == b0['stock'] - 3 and q3['total'] == b0['total'] + 3 and q3['live'] and q3['push'],
              f'「まとめて 使う」：つづけて 3回 押す → 押した 回数ぶん トークンが 減る（{b0["stock"]} → {q3["stock"]}）・お世話も 3回に 数える・PUSH は のこる')
        check(q1['pop'] == [] and 'pfo' in e1 and q2['pop'] == [100] and 'piron' in e2 and 'pfo' not in e2 and q2['wal'] == b0['wal'] + 100 and q3['pop'] == [200] and 'dedeen' in e3 and 'piron' not in e3 and q3['wal'] == b0['wal'] + 300 and q3['pend'] is None
              and all('token' in e for e in (e1, e2, e3)),
              f'当たりは 押した 瞬間に：ハズレ＝音 だけ（{e1}）／100P＝札と ピロン（{e2}）／200P＝札と デデーン（{e3}）・ポイントは すぐ 台帳へ（+{q3["wal"] - b0["wal"]}P）・前の 札は 消して 次の 札')
        stage_click(pg, *G['end']); pg.wait_for_timeout(900); q4 = pg.evaluate(PU); e4 = pg.evaluate(SES)
        check(pxe[0][3] > 240 and not q4['live'] and not q4['push'] and q4['stock'] == q3['stock'] and 'fold' in e4 and q4['bulk'], f'「おわる」（1回 押した あとに 出る）→ PUSH は 消える・のこりの トークンは そのまま（{q4["stock"]}こ）・スイッチは「まとめて」の まま おぼえる')
        pg.evaluate("() => { const s = TCApp.state; s.rs = { n: 1, at: 0, el: 0 }; TCCare.S.bulk = false; s.bulk = false; }")      # このあとの テストの ため：馬の リセットの 数えを もどす（まとめて 押した 分で 5回に 近づく）・スイッチは「1個 使う」に
        af = pg.evaluate(TR)
        #   馬は 2分ごとの くじ（1/7）で うんちを する：ここまでに して いたら 消して おく（うんちが あると「おそうじ」が 始まる ＝ この 確かめが ゆれる）
        NOPOOP = "() => { const [HO, BR] = TCCare._hb; BR.poopReq = false; BR.poopT = null; BR.poopE = 0; BR.poops = []; TCApp.state.poops = []; }"
        pg.evaluate(NOPOOP); pg.wait_for_timeout(200)
        for _ in range(16):
            stage_click(pg, 526, 1494); pg.wait_for_timeout(600)
            if pg.evaluate("() => TCCare.S.fx.some(f => f.k === 'tagUI' && /ゴミ/.test(f.txt))"): break
        ag = pg.evaluate("() => { const S = TCCare.S; return { phase: S.phase, mode: S.mode, stock: S.stock, tags: S.fx.filter(f => f.k === 'tagUI').map(f => f.txt), poops: (TCCare._hb[1].poops || []).length, min: Math.ceil(S.trashIn / 60) }; }")
        check(ag['phase'] == 'idle' and ag['mode'] is None and ag['stock'] == af['stock'] and ag['min'] in (14, 15) and f'ゴミは あと {ag["min"]}分で 出るよ' in ag['tags'],      # 片付けに 1分より 長く かかると「あと 14分」
              f'つづけては できない：「{ag["tags"][-1] if ag["tags"] else ""}」・トークンは 使わない（{ag["stock"]}こ の まま）{"" if ag["tags"] else ag}')
        pg.evaluate(NOPOOP)
        pg.evaluate("() => { const [HO, BR] = TCCare._hb; BR.poops = [{ x: 470, y: 1230, img: 1, t0: -10, h0: 1.05, w: 0.5 * (HO.opt.stage || 1), gold: false }]; }"); pg.wait_for_timeout(600)
        for _ in range(16):
            stage_click(pg, 526, 1494); pg.wait_for_timeout(600)
            if pg.evaluate("() => TCCare.S.mode === 'clean'"): break
        for _ in range(40):
            pg.wait_for_timeout(250)
            if pg.evaluate("() => TCCare.S.phase === 'clean'"): break
        pc_ = pg.evaluate("""async () => { const S = TCCare.S, C = S.clean, raf = () => new Promise(r => requestAnimationFrame(r)); if (!C) return null; const T = C.tg[0], o = T.o, z = S.zoom.z, left = (TCApp.state.trashAt - Date.now()) / 60000;
          const drag = async (from, to, k, stop) => { let q = from; for (let i = 1; i <= k && !(stop && stop()); i++) { await raf(); q = [from[0] + (to[0] - from[0]) * i / k, from[1] + (to[1] - from[1]) * i / k]; TCCare.input('move', q[0], q[1], S.lastT); } return q; };
          const pn = { x: C.pan.x, y: C.pan.y }, ux = o.x - pn.x, uy = o.y - pn.y, L = Math.hypot(ux, uy) || 1, far = [o.x + ux / L * 140, o.y + uy / L * 70], b0 = [C.bro.x, C.bro.y];
          TCCare.input('down', b0[0], b0[1], S.lastT); const p1 = await drag(b0, far, 20), p2 = await drag(p1, [pn.x, pn.y], 36, () => T.done);      // ほうきを つかんで うんちの むこうがわへ → ちりとりへ 押す（第4.165版）
          TCCare.input('up', p2[0], p2[1], S.lastT); return { n: C.tg.length, poop: !!T.poop, done: !!T.done, z, left, saved: TCApp.state.poops.length }; }""")
        check(pc_ and pc_['n'] == 1 and pc_['poop'] and pc_['done'] and pc_['z'] > 1.3 and 13.3 < pc_['left'] <= 15 and pc_['saved'] == 0,
              f'ゴミが なくても うんちが 出たら おそうじ できる（カメラが 寄る {pc_["z"]:.2f}倍・ゴミの 15分は そのまま {pc_["left"]:.1f}分）')
        okc = True
        try: pg.wait_for_function(PUSH_LIVE, timeout=40000)
        except Exception: okc = False
        pg.wait_for_timeout(500); c0 = pg.evaluate(PU); dc = press(pg); pg.wait_for_timeout(900); c1 = pg.evaluate(PU)
        check(okc and dc == 1 and c1['stock'] == c0['stock'] - 1 and not c1['live'] and c1['total'] == c0['total'] + 1, f'うんちの おそうじの あとも PUSH（馬が くんくん して いる 間でも 押せる：{c0["phase"]}）→ 押すと トークン −1（{c0["stock"]} → {c1["stock"]}）')
        for _ in range(80):
            pg.wait_for_timeout(250)
            if pg.evaluate("() => TCCare.S.phase === 'idle' && !TCCare.S.clean && !TCCare.S.mode"): break
        # 15分 たつ（時計を 進める）→ また 5か所に 散らばる・ひらき直しても 同じ 場所
        pg.evaluate("() => { window.__realNow = Date.now.bind(Date); const r = window.__realNow; Date.now = () => r() + 12 * 60000; }"); pg.wait_for_timeout(900)
        t14 = pg.evaluate(TR)
        pg.evaluate("() => { const r = window.__realNow; Date.now = () => r() + 15.5 * 60000; }"); pg.wait_for_timeout(1500)
        t15 = pg.evaluate(TR)
        check(t14['n'] == 0 and t15['n'] == 5 and len(t15['live']) == 5 and t15['xy'] != tr['xy'] and t15['trashIn'] == 0,
              f'12分 では 出ない（あと {t14["left"]:.1f}分）・15分 たつと また 5か所に 散らばる（前とは ちがう 場所）')
        pg.evaluate("() => { const r = window.__realNow; Date.now = () => r() + 60 * 60000; }"); pg.wait_for_timeout(900)
        t60 = pg.evaluate(TR)
        check(t60['n'] == 5 and t60['xy'] == t15['xy'], '片付けない まま 時間が たっても 新しい ゴミは 出ない（同じ 5か所の まま）')
        pg.evaluate("() => TCApp.close()"); pg.wait_for_timeout(400); pg.evaluate("() => TCApp.open()"); pg.wait_for_timeout(1500)
        ro = pg.evaluate(TR)
        check(ro['n'] == 5 and ro['xy'] == t15['xy'] and [q[:2] for q in ro['live']] == t15['xy'] and [q[2] for q in ro['live']] == [q[2] for q in t15['live']],
              'とじて ひらき直しても ゴミは 同じ 場所・同じ 中身')
        shot(pg, 'tc_trash')
        pg.evaluate("(k) => { Date.now = window.__realNow; const s = TCApp.state, n = Date.now(), K = JSON.parse(k); s.seen = n; s.stockAt = n; Object.assign(s, K); const S = TCCare.S; S.stock = S.stockShow = K.stock; S.high = K.high || 0; }", keep); pg.wait_for_timeout(400)
        # 第4.139版（抜け穴を ふさぐ）：端末の 時計を 先へ 進めて お世話トークンを ためる → 時計を もどす、を ふせぐ（tc_app.js の tnow：もどらない 時計）
        print('■ 時計を 進めて もどす ズルを ふせぐ')
        TS = "() => { const s = TCApp.state; return { stock: s.stock, at: s.stockAt, seen: s.seen, now: Date.now() }; }"
        k0 = pg.evaluate(TS)
        check(k0['seen'] is not None and abs(k0['seen'] - k0['now']) < 5000, f'開いて いる あいだ、いままでに 見た いちばん 先の 時刻（seen）を おぼえる（{k0["stock"]}こ）')
        pg.evaluate("() => { window.__realNow = Date.now.bind(Date); const r = window.__realNow; Date.now = () => r() + 260 * 60000; }"); pg.wait_for_timeout(700)
        k1 = pg.evaluate(TS)
        check(k1['stock'] == 25 and k1['seen'] - k0['now'] >= 259 * 60000, f'時計を 260分 進める → トークンは 満タン（25こ：第4.159版）：ここまでは 止められない（{k0["stock"]} → {k1["stock"]}）')
        pg.evaluate("() => { Date.now = window.__realNow; }"); pg.wait_for_timeout(700)
        k2 = pg.evaluate(TS)
        check(k2['stock'] == 25 and k2['at'] >= k1['seen'] - 3000 and 0 <= k2['seen'] - k1['seen'] < 5000 and k2['at'] - k2['now'] >= 250 * 60000,
              f'時計を もどしても、数えはじめの 時刻は 先の 時刻の まま（前は 満タンの とき いまの 時刻に 書きかえて いた）（あと {round((k2["at"] - k2["now"]) / 60000)}分）')
        pg.evaluate("() => { TCApp.state.stock = 5; TCCare.S.stock = TCCare.S.stockShow = 5; const r = window.__realNow; Date.now = () => r() + 30 * 60000; }"); pg.wait_for_timeout(800)
        k3 = pg.evaluate(TS)
        check(k3['stock'] == 5 and k3['seen'] == k2['seen'], f'トークンを 使って（5こ）30分 たっても ふえない（本当の 時刻が 先に 見た 時刻に 追いつくまで）（{k3["stock"]}こ）')
        pg.evaluate("() => { const r = window.__realNow; Date.now = () => r() + 271 * 60000; }"); pg.wait_for_timeout(800)
        k4 = pg.evaluate(TS)
        check(k4['stock'] == 15 and k4['seen'] > k2['seen'], f'先に 見た 時刻を こえたら また ふえる（こえた 11分ぶん＝5分が 2回＝10こ〈第4.165版：5分ごとに 5つ〉：5 → {k4["stock"]}）')
        pg.evaluate("() => { Date.now = window.__realNow; const s = TCApp.state, n = Date.now(); s.seen = n; s.stockAt = n; }"); pg.wait_for_timeout(300)
        print('■ 説明書')
        stage_click(pg, 678, 97); pg.wait_for_timeout(1200)
        g = pg.evaluate("() => { const e = document.querySelector('#tcg'); return e ? [e.style.display, e.textContent.includes('幻の馬・神様馬がいるあいだ'), e.textContent.includes('10000P か 20000P')] : null; }")
        check(g and g[0] != 'none' and g[1] and g[2], f'説明書に 幻の馬・神様馬の 当たり {g}')
        # 第4.140版（11/10 14:14 まさちゃん「あと項目ごとに%を説明書に載せるようにして！」）：項目ごとに ％（表の 左に ％・その 下に 小さく 分数）。分数は 抽選の 表（tc_app.js）と 同じ
        gd = pg.evaluate("""() => { const T = TCApp._t, e = document.querySelector('#tcg');
          const rows = t => [...e.querySelectorAll(`table[data-tab=${t}] tr`)].map(r => ({ d: +r.dataset.d, pc: r.cells[0].childNodes[0].textContent, fr: r.cells[0].querySelector('small').textContent, lab: r.cells[1].textContent }));
          const key = z => z.k === 'pt' ? z.v + 'P GET' : z.k === 'tk' ? 'チケット' : z.k === 'zn' ? 'ポイント特化ゾーン（最大25,000P）' : (z.v || T.RT[z.tier]).join('P か ') + 'P';
          const want = tab => tab.map(([p, z]) => ({ d: Math.round(1 / p), key: key(z) }));
          return { care: rows('care'), mab: rows('maboroshi'), kami: rows('kamisama'), wCare: want(T.PRIZES), wMab: want(T.PRIZES_VISIT.maboroshi), wKami: want(T.PRIZES_VISIT.kamisama), odds: T.ODDS, text: e.textContent,
            fit: [...e.querySelectorAll('td:first-child')].every(td => td.scrollWidth <= td.clientWidth + 1 && td.getBoundingClientRect().height < 46) }; }""")
        def pc(d, n=1):                       # tc_guide.js の pc と 同じ きまり（まるめは JS の toFixed と 同じ：ちょうど まん中は 大きい 方＝3.125 → 3.13）
            from decimal import Decimal, ROUND_HALF_UP
            x = n / d * 100; f = 1 if x >= 10 else 2 if x >= 0.1 else 3
            s_ = str(Decimal(x).quantize(Decimal(1).scaleb(-f), rounding=ROUND_HALF_UP))
            if '.' in s_: s_ = s_.rstrip('0').rstrip('.')
            return ('約' if abs(float(s_) - x) > 1e-9 else '') + s_ + '%'
        def same(rows, want):
            return (len(rows) == len(want) and all(any(r['d'] == w['d'] and w['key'] in r['lab'] for r in rows) for w in want)
                    and all(r['pc'] == pc(r['d']) and r['fr'] == f"1/{r['d']}" for r in rows))
        check(same(gd['care'], gd['wCare']) and [(r['d'], r['pc']) for r in gd['care']][:6] == [(15, '約6.67%'), (25, '4%'), (55, '約1.82%'), (95, '約1.05%'), (99, '約1.01%'), (121, '約0.83%')] and len(gd['care']) == 11      # 第4.165版：10P 1/15・20P 1/25・50P 1/55・100P 1/95
              and [(r['d'], r['pc']) for r in gd['care']][6:] == [(125, '0.8%'), (245, '約0.41%'), (399, '約0.25%'), (600, '約0.17%'), (699, '約0.14%')],      # 第4.142版：ルーレット 1/125・1/245・1/399・チケット 1/600／第4.165版：ポイント特化ゾーン 1/699
              f"説明書：お世話の 当たりは 項目ごとに ％（第4.165版：10P 約6.67%・20P 4%・50P 約1.82%・100P 約1.05% … ルーレット 0.8%・約0.41%・約0.25%・チケット 約0.17%・ポイント特化ゾーン 約0.14%）・分数と 中身は 抽選の 表と 同じ（{[(r['pc'], r['fr']) for r in gd['care']]}）")
        check(same(gd['mab'], gd['wMab']) and same(gd['kami'], gd['wKami']) and [(r['d'], r['pc']) for r in gd['mab']] == [(15, '約6.67%'), (30, '約3.33%'), (60, '約1.67%'), (699, '約0.14%')] and [(r['d'], r['pc']) for r in gd['kami']] == [(8, '12.5%'), (16, '6.25%'), (32, '約3.13%'), (699, '約0.14%')],      # 第4.142版／第4.165版：ポイント特化ゾーン 1/699
              f"説明書：幻の馬・神様馬が いる 間の 当たりも ％（幻の馬 1/15・1/30・1/60／神様馬 1/8・1/16・1/32／どちらも ポイント特化ゾーン 1/699：{[(r['pc'], r['fr']) for r in gd['mab'] + gd['kami']]}）")
        od = gd['odds']; D = lambda k: round(1 / od[k])
        wantTx = ['ぜんぶ 合わせて 約17.1%', 'ルーレットは どちらも 50%', '3枚 12.5%・2枚 約33.3%・1枚 約54.2%', 'チケット（壁紙 or 7,000P・1〜3枚）', 'チケット1枚で、カギの壁紙を1つ解放するか、7,000Pにかえるか、選べるよ', 'お世話（ごはん・おそうじ）を5回すると、リセットのタイマーがスタート', 'タイマーが5分たつとリセット → 次の馬を抽選', 'それ以外は いつもの馬のまま', 'お世話をしないと 馬はかわらないよ（開いているだけでは 抽選しないよ）', 'お世話のとちゅうは リセットしないよ',
                  '抽選（お世話のあとのPUSH）は、幻の馬 最大10回・神様馬 最大5回まで。つかい切ると帰るよ',      # 第4.168版（まさちゃん 11/14 01:26「幻の馬は、抽選最大10回まで 神様馬は、抽選最大5回まで」）
                  '帰るのは、抽選をつかい切ったとき・お世話5回のあと5分（リセット）・来てから30分（タイムリミット）の いちばん早いとき', '左上の「なかよし」の下に「タイムリミット・抽選の回数・切り替わりタイマー」が出るよ', '約1.52%・1/66', '約33.3%ずつ・1/3', 'ニンジンの約3.33%・1/30',
                  f'{pc(D("poop"))}（1/{D("poop")}）', f'うんちの{pc(D("gold"))}・1/{D("gold")}', f'高確ゾーン {pc(D("high"))}（1/{D("high")}', f'幻の馬 {pc(D("mab"))}（1/{D("mab")}）', f'神様馬 {pc(D("kami"))}（1/{D("kami")}）']
        check(all(x in gd['text'] for x in wantTx) and gd['fit'] and [D(k) for k in ('poop', 'gold', 'high', 'mab', 'kami')] == [7, 20, 50, 245, 399] and od['visitDraws'] == {'maboroshi': 10, 'kamisama': 5},
              f"説明書：合わせた ％・ルーレット 50%・チケットの 枚数・ハートの 抽選・呼ぶ・金のニンジン・うんち・金のうんち・高確ゾーン・幻の馬・神様馬（抽選の 上限 10回・5回：アプリの 数と 同じ）（左の 欄に おさまる {gd['fit']}・ない もの {[x for x in wantTx if x not in gd['text']]}）")
        od = pg.evaluate("() => [TCApp._t.ODDS.trashMin, TCApp._t.ODDS.trashN]")
        check(od == [15, 5] and all(x in gd['text'] for x in ['15分ごとにゴミが5か所に散らばる', '片付けるまで次のゴミは出ない', 'おそうじできるのはゴミかうんちがあるときだけ', 'ほうきとちりとりは、指でつかんで好きな所へ運べるよ', 'ちりとりへ はき入れよう']) and 'うんちがない時は落ち葉' not in gd['text'],
              f'説明書：おそうじは「15分ごとに ゴミが 5か所」「ゴミか うんちが ある とき だけ」「ほうきと ちりとりは 指で つかんで 運べる」（第4.165版）「ちりとりへ はき入れる」（きまりの 数 {od} と 同じ・前の「3回はく・落ち葉」は ない）')
        #   第4.165版（11/13 12:51 まさちゃん「ポイントの特化ゾーンを作る … 特化ゾーンも、トレーニングセンターの説明書に追加」）：項目「ポイント特化ゾーン」（お世話でポイントGETチャンスの すぐ 下）
        gz = pg.evaluate("""() => { const e = document.querySelector('#tcg'), s = [...e.querySelectorAll('.sec')], z = s.find(x => x.querySelector('h3').textContent.includes('ポイント特化ゾーン')); if (!z) return null;
          const T = TCApp._t, Z = T.ZONE, rows = [...z.querySelectorAll('table[data-tab=zone] tr')].map(r => [+r.dataset.n, r.cells[0].textContent, r.cells[1].textContent]);
          const P = n => n < Z.max ? Math.pow(Z.rate, n) * (1 - Z.rate) : Math.pow(Z.rate, Z.max); let avg = 0, sum = 0; for (let n = 0; n <= Z.max; n++) { avg += T.zoneV(n) * P(n); sum += P(n); }
          return { text: z.textContent, rows, heads: s.map(x => x.querySelector('h3').textContent), zavg: +z.querySelector('[data-n=zavg]').dataset.v, avg, sum, zone: Z, vs: rows.map(r => T.zoneV(r[0])), ps: rows.map(r => P(r[0])) }; }""")
        zt = ['約0.14%（1/699）で突入', 'いつもの馬・幻の馬・神様馬の どのときも', 'スタートは1,000P', '「レバーを押し込め！」', 'タップするたびに60%で＋2,000P 上乗せ', '虹色の光', '上乗せに失敗（40%）したら そこでおしまい', '12回つづけて上乗せするとMAX 25,000P', 'ゾーン1回の平均は約4,000P']
        check(gz is not None and gz['heads'].index('虹ポイント特化ゾーン') == gz['heads'].index('Pお世話でポイントGETチャンス') + 1 and all(x in gz['text'] for x in zt) and gz['zone'] == {'d': 699, 'start': 1000, 'add': 2000, 'rate': 0.6, 'max': 12},
              f"説明書：項目「ポイント特化ゾーン」（お世話でポイントGETチャンスの すぐ 下）：1/699・スタート 1,000P・レバーを押し込め！で 60% ＋2,000P・失敗で おしまい・12回で MAX 25,000P・平均 約4,000P（ない もの {gz and [x for x in zt if x not in gz['text']]}）")
        zpc = ['40%', '24%', '14.4%', '8.64%', '約5.18%', '約3.11%', '約1.87%', '約1.12%', '約0.67%', '約0.4%', '約0.24%', '約0.15%', '約0.22%']
        check(gz is not None and [r[0] for r in gz['rows']] == list(range(13)) and [r[1] for r in gz['rows']] == zpc and gz['vs'] == [1000 + 2000 * n for n in range(13)]
              and all(f'上乗せ {n}回 → {1000 + 2000 * n:,}P' in gz['rows'][n][2] for n in range(13)) and gz['rows'][12][2].endswith('（MAX）') and all(r[1] == pc(1 / q) for r, q in zip(gz['rows'], gz['ps']))
              and abs(gz['sum'] - 1) < 1e-12 and gz['zavg'] == round(gz['avg']) == 3993,
              f"説明書：上乗せの 回数ごとの ％と 合計（0回 40% → 1,000P … 12回 約0.22% → 25,000P（MAX））・％を 足すと 100%・平均 {gz and gz['avg']:.1f}P（抽選の きまりから 数えた 数と 同じ）")
        #   第4.144版（11/10 18:19 まさちゃん「この仕組みもトレーニングセンターの説明書に記載して！」）：「馬のリセット（次の馬の抽選）」の 項目・2分ごとの チャンスは 高確ゾーン だけ
        g2 = pg.evaluate("() => { const s = [...document.querySelectorAll('#tcg .sec')].map(x => [x.querySelector('h3').textContent, x.textContent]); const f = k => (s.find(x => x[0].includes(k)) || [0, ''])[1]; return { tick: f('2分ごとのチャンス'), reset: f('馬のリセット'), visit: f('幻の馬・神様馬がいるあいだ'), heads: s.map(x => x[0]) }; }")
        check('幻の馬' not in g2['tick'] and '神様馬' not in g2['tick'] and '高確ゾーン' in g2['tick'] and '幻の馬' in g2['reset'] and '神様馬' in g2['reset'] and '10分' not in g2['visit'] and len(g2['heads']) == 14
              and g2['heads'].index('替馬のリセット（次の馬の抽選）') == g2['heads'].index('★2分ごとのチャンス') + 1,
              f"説明書：「馬のリセット（次の馬の抽選）」の 項目が ある・幻の馬／神様馬の 抽選は そこに 書く（2分ごとの チャンスは 高確ゾーン だけ）・「いるのは10分」は ない（{g2['heads']}）")
        #   第4.159版：トークンの 上限 25・お世話の あとの PUSH（1個 使う／まとめて 使う・ハズレは 音 だけ）
        g3 = pg.evaluate("() => { const s = [...document.querySelectorAll('#tcg .sec')].map(x => [x.querySelector('h3').textContent, x.textContent]); const f = k => (s.find(x => x[0].includes(k)) || [0, ''])[1]; return { tok: f('お世話トークン'), push: f('お世話のあとのPUSH'), pt: f('お世話でポイントGETチャンス'), pet: f('撫でる'), heads: s.map(x => x[0]) }; }")
        check('最大25こ' in g3['tok'] and '20こ' not in g3['tok'] and '5分ごとに5つたまる' in g3['tok'] and '10分ごと' not in g3['tok'] and 'ポイントで買うこともできる' in g3['tok'] and 'お世話トークンが最大だよ！' in g3['pet'] and 'PUSHを1回押すと1つ使う' in g3['tok']
              and g3['heads'].index('買お世話トークンの購入') == g3['heads'].index('トお世話トークン') + 1 and g3['heads'].index('押お世話のあとのPUSH') == g3['heads'].index('トお世話トークン') + 2
              and all(x in g3['push'] for x in ['PUSHが出るよ', 'トークンを1つ使って抽選', 'ハズレは「プフォ」の音だけ', '「1個 使う」「まとめて 使う」', '1回押したらおしまい', '押した回数ぶんトークンがへる', 'やめるときは「おわる」', 'トークン1つがお世話1回'])
              and 'PUSHを押すたびに抽選' in g3['pt']
              and all(x in g3['pet'] for x in ['抽選はお世話トークンが20こ未満のときだけ', '20こ以上（最大の25こも）のときは', '抽選まち', '20こを切ったら抽選がはじまるよ']) and 'ふえない' not in g3['pet'],
              f"説明書（第4.159版・第4.165版）：お世話トークンは 5分ごとに 5つ・最大25こ（最大の ときに 撫でると「お世話トークンが最大だよ！」）・すぐ 下に「お世話トークンの購入」の 項目・「お世話のあとのPUSH」の 項目（押すと 抽選・ハズレは 音 だけ・1個／まとめての スイッチ・おわる・トークン 1つが お世話 1回）・"
              f"ハートの 抽選は トークンが 20こ未満の とき だけ（20こ以上は 抽選まち → 20こを 切ったら 抽選）")
        shot(pg, 'tc_guide')
        pg.evaluate("() => TCGuide.close()"); pg.wait_for_timeout(500)
        # 第4.159版（バグ直し・まさちゃん 11/12 14:54「トレーニングセンターの説明書開いたらすぐ閉じるようになってて表示されないよ！」）：指（タッチ）で「？」を 押すと、指を はなした すぐ あとに
        #   同じ 場所へ クリックが とどく（その とき いちばん 上に ある 部品＝もう 開いて いる 説明書の うしろの 幕へ）→ 前は それで すぐ 閉じた。開いて 0.45秒は 幕と ✕ で 閉じない。
        #   ここでは 指の 出来事（pointerdown → pointerup）の すぐ あとに、その 場所の いちばん 上の 部品を クリックして 同じ ことを 起こす
        gk = pg.evaluate("""async () => { const stg = document.querySelector('#tcOv .tcst'), cv = document.querySelector('#tcOv .tco'), r = stg.getBoundingClientRect(), x = r.left + 678 / 1052 * r.width, y = r.top + 97 / 1657 * r.height, w = ms => new Promise(q => setTimeout(q, ms));
          const pe = t => cv.dispatchEvent(new PointerEvent(t, { bubbles: true, cancelable: true, clientX: x, clientY: y, pointerId: 7, pointerType: 'touch', isPrimary: true, buttons: t === 'pointerup' ? 0 : 1 }));
          const raf2 = () => new Promise(q => requestAnimationFrame(() => requestAnimationFrame(q)));      // 説明書は 次の コマから 見える（開いた 瞬間は まだ かくれて いる）→ 2コマ 待って から「クリック」
          pe('pointerdown'); pe('pointerup'); await raf2(); const o0 = TCGuide.isOpen(), hit = document.elementFromPoint(x, y), hitName = hit.className + ''; hit.click(); await w(700); const o1 = TCGuide.isOpen();
          const bk = getComputedStyle(document.querySelector('#tcg .bk')).opacity, sh = document.querySelector('#tcg .sh').getBoundingClientRect(), vis = sh.top < r.bottom - 100 && sh.height > 200;
          document.querySelector('#tcg .bk').click(); await w(600); const o2 = TCGuide.isOpen();                                     // 開いて 0.45秒より あと：幕を 押すと 閉じる（前と 同じ）
          pe('pointerdown'); pe('pointerup'); await w(700); document.querySelector('#tcg .x').click(); await w(600); const o3 = TCGuide.isOpen();      // ✕ でも 閉じる
          return { o0, hitName, o1, bk: +bk, vis, o2, o3, guard: TCGuide.GUARD }; }""")
        check(gk['o0'] and gk['hitName'] == 'bk' and gk['o1'] and gk['bk'] > 0.95 and gk['vis'] and gk['o2'] is False and gk['o3'] is False and 0.3 <= gk['guard'] <= 0.6,
              f'説明書（バグ直し）：指で「？」を 押した すぐ あとの クリック（うしろの 幕「{gk["hitName"]}」に 当たる）では 閉じない ＝ 開いた まま 表示される（前は ここで すぐ 閉じた）・'
              f'{gk["guard"]}秒より あとは 幕を 押すと 閉じる・✕ でも 閉じる {gk}')
        print('■ 作戦会議')
        pg.locator('#tcOv .tcpl').click(); pg.wait_for_timeout(700)
        d = pg.evaluate("() => { const e = document.querySelector('#tcPlan'); return e ? [getComputedStyle(e).display, e.querySelector('.bdt').textContent, e.querySelector('.bsub').textContent] : null; }")
        import datetime as _dt
        td = _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=9)))
        check(d and d[0] != 'none' and d[1].startswith(f'{td.year}年{td.month}月{td.day}日') and d[2] == 'お気に入りレース一覧', f'作戦会議の ボード {d}')
        shot(pg, 'tc_plan_empty')
        pg.locator('#tcPlan [data-p=on]').click(); pg.wait_for_timeout(500)
        check(pg.evaluate("() => JSON.parse(localStorage.getItem('tengel.plan')).on === true && window.__notify.auth === 'authorized'"), '通知を オン（iPhone の 許可）')
        pg.locator('#tcPlan [data-p=add]').click(); pg.wait_for_timeout(300)
        later = td + _dt.timedelta(hours=2)
        pg.fill('#tcPlan [data-f=name]', 'はなまる特別'); pg.fill('#tcPlan [data-f=time]', later.strftime('%H:%M')); pg.fill('#tcPlan [data-f=date]', later.strftime('%Y-%m-%d'))
        pg.fill('#tcPlan [data-f=n]', '14'); pg.fill('#tcPlan [data-f=dist]', '1600')
        pg.locator('#tcPlan [data-p=save]').click(); pg.wait_for_timeout(500)
        P = pg.evaluate("() => JSON.parse(localStorage.getItem('tengel.plan'))")
        check(len(P['races']) == 1 and P['races'][0]['name'] == 'はなまる特別' and P['races'][0]['n'] == 14 and P['races'][0]['dist'] == 1600, f'レースを 予約 {P["races"]}')
        pg.locator('#tcPlan [data-p=nt][data-m="20"]').click(); pg.wait_for_timeout(200)
        pg.locator('#tcPlan [data-p=nt][data-m="5"]').click(); pg.wait_for_timeout(800)
        items = pg.evaluate("() => window.__notify.items.filter(i => /^plan-/.test(i.id)).map(i => [i.id.split('-').pop(), i.title, i.body])")
        check(len(items) == 2 and {i[0] for i in items} == {'20', '5'} and all('はなまる特別' in i[2] for i in items), f'20分前・5分前の 通知 {items}')
        shot(pg, 'tc_plan')
        pg.evaluate("() => { const P = JSON.parse(localStorage.getItem('tengel.plan')); P.races.push({ id: 'old', date: '2020-01-01', time: '10:00', name: 'むかし', notify: [5] }); localStorage.setItem('tengel.plan', JSON.stringify(P)); }")
        pg.locator('#tcPlan [data-p=close]').click(); pg.wait_for_timeout(300); pg.locator('#tcOv .tcpl').click(); pg.wait_for_timeout(500)
        check(pg.evaluate("() => JSON.parse(localStorage.getItem('tengel.plan')).races.every(r => r.id !== 'old')"), 'すぎた 日の レースは 消える')
        # 第4.143版（11/10 17:49 まさちゃん「作戦会議のやりたいレースの項目に、メモが書き込めるようにして！」）：
        #   レースの 札ごとに メモの 欄（そのまま 書ける・書いた そばから 保存・300字まで・行が ふえた ぶん だけ 広がる）。予約／直す の 画面にも メモの 欄
        print('■ 作戦会議の メモ（第4.143版）')
        rid = pg.evaluate("() => JSON.parse(localStorage.getItem('tengel.plan')).races[0].id")
        MSEL = f'#tcPlan textarea.mm[data-id="{rid}"]'
        mget = lambda: pg.evaluate("""(sel) => { const t = document.querySelector(sel); if (!t) return null; const cs = getComputedStyle(t), r = JSON.parse(localStorage.getItem('tengel.plan')).races[0];
          return { ph: t.placeholder, v: t.value, max: t.maxLength, fs: parseFloat(cs.fontSize), h: Math.round(t.getBoundingClientRect().height), us: cs.webkitUserSelect || cs.userSelect, saved: r.memo == null ? null : r.memo,
                   inj: document.querySelectorAll('#tcPlan .rc b, #tcPlan .rc script').length, focus: document.activeElement === t, clip: t.scrollHeight > t.clientHeight + 1 }; }""", MSEL)
        m0 = mget()
        check(m0 and m0['ph'] == '📝 メモを書く（作戦など）' and m0['v'] == '' and m0['max'] == 300 and m0['fs'] >= 16 and m0['h'] <= 46 and m0['us'] == 'text',
              f'レースの 札に メモの 欄（空・「📝 メモを書く（作戦など）」・300字まで・字は 16px 以上＝押しても 画面が 拡大 しない・1行ぶんの 高さ）（{m0}）')
        MEMO = '◎3番 ○7番 ▲12番\n雨なら見送り <b>"x"</b>&'
        pg.locator(MSEL).click(); pg.locator(MSEL).type(MEMO); pg.wait_for_timeout(300)
        m1 = mget()
        check(m1['saved'] == MEMO and m1['v'] == MEMO and m1['h'] > m0['h'] + 15 and not m1['clip'] and m1['inj'] == 0 and m1['focus'],
              f'書いた そばから 保存（保存ボタンは いらない）・行が ふえると 欄が 広がる（{m0["h"]} → {m1["h"]}px）・記号は そのまま 字として 出る（{m1}）')
        pg.locator('#tcPlan [data-p=nt][data-m="10"]').click(); pg.wait_for_timeout(900)
        m2 = mget(); bodies = pg.evaluate("() => window.__notify.items.filter(i => /^plan-/.test(i.id)).map(i => i.title + i.body)")
        check(m2['v'] == MEMO and m2['saved'] == MEMO and m2['h'] == m1['h'] and m2['inj'] == 0 and len(bodies) == 3 and not any('見送り' in x or '◎' in x for x in bodies),
              f'通知の ボタンを 押しても（画面の かき直し）メモは 残る・通知の 文には メモを 出さない（{m2["v"]!r}・{bodies}）')
        pg.locator('#tcPlan [data-p=nt][data-m="10"]').click(); pg.wait_for_timeout(300)
        pg.locator('#tcPlan [data-p=close]').click(); pg.wait_for_timeout(300); pg.locator('#tcOv .tcpl').click(); pg.wait_for_timeout(600)
        m3 = mget()
        check(m3['v'] == MEMO and m3['h'] == m1['h'], f'とじて ひらき直しても メモは 残る・欄の 高さも 同じ（{m3["h"]}px）')
        #   「消す」を 1回 押した あとに メモの 欄を 押す →「消す」に もどる（画面は かき直さない＝書いて いる 欄が 消えない）
        pg.locator(f'#tcPlan [data-p=del][data-id="{rid}"]').click(); pg.wait_for_timeout(250)
        a1 = pg.evaluate("(id) => document.querySelector(`#tcPlan [data-p=del][data-id=\"${id}\"]`).textContent", rid)
        pg.evaluate("(sel) => { window.__mmEl = document.querySelector(sel); }", MSEL)
        pg.locator(MSEL).click(); pg.wait_for_timeout(250)
        a2 = pg.evaluate("([id, sel]) => { const d = document.querySelector(`#tcPlan [data-p=del][data-id=\"${id}\"]`); return [d.textContent, d.classList.contains('ask'), window.__mmEl === document.querySelector(sel), document.activeElement === window.__mmEl, JSON.parse(localStorage.getItem('tengel.plan')).races.length]; }", [rid, MSEL])
        check(a1 == 'ほんとに 消す？' and a2 == ['消す', False, True, True, 1], f'「ほんとに 消す？」の あとに メモの 欄を 押すと「消す」に もどる・欄は その まま（かき直さない）・レースは 消えない（{a1}・{a2}）')
        #   300字まで（こえた ぶんは 保存しない）
        pg.locator(MSEL).fill('あ' * 320); pg.wait_for_timeout(300)
        m4 = mget()
        check(len(m4['saved']) == 300, f'メモは 300字まで（320字 入れても 保存は {len(m4["saved"])}字）')
        pg.locator(MSEL).fill(MEMO); pg.wait_for_timeout(300)
        #   予約／直す の 画面：メモの 欄に いまの メモ → 直して 保存 → 札に 出る。レース名だけ 直しても メモは 残る
        pg.locator(f'#tcPlan [data-p=edit][data-id="{rid}"]').click(); pg.wait_for_timeout(400)
        f0 = pg.evaluate("() => { const t = document.querySelector('#tcPlan [data-f=memo]'); return t ? [t.tagName, t.value, t.maxLength, parseFloat(getComputedStyle(t).fontSize)] : null; }")
        #   第4.143版（11/10 18:05 まさちゃん「作成会議の一枚目の赤丸画面から飛び出ちゃってる！調整して！」）：予約／直す の 画面の 欄（日付・発走時間も）は 右へ はみ出さない
        ff = pg.evaluate("""() => { const fm = document.querySelector('#tcPlan .fm'), fr = fm.getBoundingClientRect(), cs = getComputedStyle(fm), pb = document.querySelector('#tcPlan .pb');
          const inR = fr.right - parseFloat(cs.paddingRight) - parseFloat(cs.borderRightWidth), inL = fr.left + parseFloat(cs.paddingLeft) + parseFloat(cs.borderLeftWidth);
          const els = [...fm.querySelectorAll('input,textarea,button')].map(e => { const r = e.getBoundingClientRect(); return [e.dataset.f || e.dataset.p, +(r.left - inL).toFixed(1), +(r.right - inR).toFixed(1)]; });
          const g = k => fm.querySelector(`[data-f=${k}]`).getBoundingClientRect();
          return { els, over: [pb.scrollWidth - pb.clientWidth, fm.scrollWidth - fm.clientWidth], half: [+(g('date').width - g('time').width).toFixed(1), +(g('time').left - g('date').right).toFixed(1)] }; }""")
        check(all(e[1] >= -0.6 and e[2] <= 0.6 for e in ff['els']) and ff['over'] == [0, 0] and abs(ff['half'][0]) <= 1 and 8 <= ff['half'][1] <= 12 and {e[0] for e in ff['els']} >= {'name', 'date', 'time', 'n', 'dist', 'memo', 'save'},
              f"予約／直す の 画面：どの 欄も 画面の 中に おさまる（日付と 発走時間は 同じ 幅で 2つ ならび・右へ はみ出さない）（{ff}）")
        pg.fill('#tcPlan [data-f=memo]', '  パドックを見てから決める\n前のレースの馬場も見る  '); pg.locator('#tcPlan [data-p=save]').click(); pg.wait_for_timeout(500)
        m5 = mget()
        pg.locator(f'#tcPlan [data-p=edit][data-id="{rid}"]').click(); pg.wait_for_timeout(300)
        pg.fill('#tcPlan [data-f=name]', 'はなまる特別'); pg.locator('#tcPlan [data-p=save]').click(); pg.wait_for_timeout(500)
        m6 = mget(); r6 = pg.evaluate("() => { const r = JSON.parse(localStorage.getItem('tengel.plan')).races[0]; return [r.name, r.n, r.dist, r.notify]; }")
        check(f0 == ['TEXTAREA', MEMO, 300, 16] and m5['saved'] == 'パドックを見てから決める\n前のレースの馬場も見る' and m5['v'] == m5['saved'] and m6['saved'] == m5['saved'] and r6 == ['はなまる特別', 14, 1600, [20, 5]],
              f'「直す」の 画面にも メモの 欄（いまの メモが 入って いる）・直して 保存すると 札に 出る（前後の 空きは とる）・ほかを 直しても メモは 残る（{f0}・{m5["saved"]!r}・{r6}）')
        #   新しく 予約する ときも メモを 書ける
        pg.locator('#tcPlan [data-p=add]').click(); pg.wait_for_timeout(300)
        pg.fill('#tcPlan [data-f=name]', 'メモつき特別'); pg.fill('#tcPlan [data-f=time]', (later + _dt.timedelta(minutes=30)).strftime('%H:%M')); pg.fill('#tcPlan [data-f=date]', later.strftime('%Y-%m-%d'))
        pg.fill('#tcPlan [data-f=memo]', '本命は 5番'); pg.locator('#tcPlan [data-p=save]').click(); pg.wait_for_timeout(500)
        n1 = pg.evaluate("() => { const P = JSON.parse(localStorage.getItem('tengel.plan')), r = P.races.find(x => x.name === 'メモつき特別'); const t = r && document.querySelector(`#tcPlan textarea.mm[data-id=\"${r.id}\"]`); return r ? [r.memo, t ? t.value : null, P.races.length] : null; }")
        check(n1 == ['本命は 5番', '本命は 5番', 2], f'新しい 予約にも メモ（{n1}）')
        pg.evaluate("() => { const P = JSON.parse(localStorage.getItem('tengel.plan')); P.races = P.races.filter(x => x.name !== 'メモつき特別'); localStorage.setItem('tengel.plan', JSON.stringify(P)); }")
        pg.locator('#tcPlan [data-p=close]').click(); pg.wait_for_timeout(300); pg.locator('#tcOv .tcpl').click(); pg.wait_for_timeout(500)
        # 第4.140版（バグ直し）：「消す」は 窓（confirm）を 使わない（アプリの 中では 窓が 出なくて 消せなかった）→ もう一度 押すと 消す
        pg.evaluate("() => { const P = JSON.parse(localStorage.getItem('tengel.plan')); P.races.push({ id: 'del1', date: '2099-01-01', time: '10:00', name: 'けすレース', notify: [] }); localStorage.setItem('tengel.plan', JSON.stringify(P)); }")
        pg.locator('#tcPlan [data-p=close]').click(); pg.wait_for_timeout(300); pg.locator('#tcOv .tcpl').click(); pg.wait_for_timeout(500)
        dl = pg.locator('#tcPlan [data-p=del][data-id=del1]')
        dl.click(); pg.wait_for_timeout(300)
        d1 = pg.evaluate("() => ({ n: JSON.parse(localStorage.getItem('tengel.plan')).races.filter(r => r.id === 'del1').length, txt: document.querySelector('#tcPlan [data-p=del][data-id=del1]').textContent, ask: document.querySelector('#tcPlan [data-p=del][data-id=del1]').classList.contains('ask') })")
        pg.locator('#tcPlan [data-p=nt][data-id=del1][data-m="10"]').click(); pg.wait_for_timeout(300)      # ほかを 押すと「消す」に もどる
        d2 = pg.evaluate("() => ({ n: JSON.parse(localStorage.getItem('tengel.plan')).races.filter(r => r.id === 'del1').length, txt: document.querySelector('#tcPlan [data-p=del][data-id=del1]').textContent })")
        pg.locator('#tcPlan [data-p=del][data-id=del1]').click(); pg.wait_for_timeout(250); pg.locator('#tcPlan [data-p=del][data-id=del1]').click(); pg.wait_for_timeout(400)
        d3 = pg.evaluate("() => ({ n: JSON.parse(localStorage.getItem('tengel.plan')).races.filter(r => r.id === 'del1').length, left: JSON.parse(localStorage.getItem('tengel.plan')).races.length })")
        check(d1 == {'n': 1, 'txt': 'ほんとに 消す？', 'ask': True} and d2 == {'n': 1, 'txt': '消す'} and d3 == {'n': 0, 'left': 1},
              f'作戦会議の「消す」：1回めで「ほんとに 消す？」・ほかを 押すと もどる・もう一度 押すと 消える（窓は 出さない）（{d1}・{d2}・{d3}）')
        pg.locator('#tcPlan [data-p=close]').click(); pg.wait_for_timeout(300)
        print('■ 当たりの 抽選（幻の馬・神様馬が いる 間は その 表だけ）')
        lot = pg.evaluate("""() => { const T = TCApp._t, st = TCApp.state, S = TCCare.S, n = 20000, cnt = (kind) => { st.visit = kind ? { kind, until: Date.now() + 6e5 } : null; S.high = 0; const c = {}; for (let i = 0; i < n; i++) { const z = T.draw(); const k = z ? z.k + ':' + (Array.isArray(z.v) ? z.v.join('/') : z.k === 'pt' ? z.v : (z.tier || '')) : '-'; c[k] = (c[k] || 0) + 1; } return c; };
          const r = { normal: cnt(null), mab: cnt('maboroshi'), kami: cnt('kamisama') }; st.visit = null; return r; }""")
        ks = lambda c: set(k for k in c if k != '-')
        check(ks(lot['mab']) <= {'rt:800/1600', 'rt:1600/3200', 'rt:3200/6400', 'zn:'} and abs(lot['mab'].get('rt:800/1600', 0) / 20000 - 1 / 15) < 0.008 and abs(lot['mab'].get('rt:1600/3200', 0) / 20000 - 1 / 30) < 0.006 and abs(lot['mab'].get('rt:3200/6400', 0) / 20000 - 1 / 60) < 0.004,
              f"幻の馬：ルーレット（1/15・1/30・1/60：第4.142版）と ポイント特化ゾーン（第4.165版）だけ {lot['mab']}")
        check(ks(lot['kami']) <= {'rt:2000/4000', 'rt:5000/10000', 'rt:10000/20000', 'zn:'} and abs(lot['kami'].get('rt:2000/4000', 0) / 20000 - 1 / 8) < 0.012 and abs(lot['kami'].get('rt:5000/10000', 0) / 20000 - 1 / 16) < 0.008 and abs(lot['kami'].get('rt:10000/20000', 0) / 20000 - 1 / 32) < 0.006,
              f"神様馬：ルーレット（1/8・1/16・1/32：第4.142版）と ポイント特化ゾーン（第4.165版）だけ {lot['kami']}")
        check(any(k.startswith('pt:') or k == 'pt:' for k in lot['normal']) or any(k.startswith('pt') for k in lot['normal']), f"いつもは ポイント {lot['normal']}")
        # 第4.140版（11/10 14:14 まさちゃん「足す：10P 1/10・20P 1/20・50P 1/50 これだけ足して！」）：小さい 当たり 3つを 足した（ほかは そのまま）
        tabS = pg.evaluate("() => TCApp._t.PRIZES.map(([p, z]) => Math.round(1 / p) + ':' + z.k + ':' + (z.k === 'pt' ? z.v : z.tier || ''))")
        #   第4.142版（11/10 17:20 まさちゃん「ノーマルのルーレット抽選、幻の馬ルーレット当選と神様馬ルーレット抽選の確率だけ変えたい！」）：ルーレット 1/125・1/245・1/399・チケット 1/600（ポイントの 当たりは そのまま）
        #   第4.165版（11/13 11:46 まさちゃん「お世話でポイントGET 確率少し変える(ここだけ) 1/15で10P 1/25で20P 1/55で50P 1/95で100P」）：10P・20P・50P・100P だけ（200P・300P・ルーレット・チケットは そのまま）
        #   第4.165版（11/13 12:51「ポイントの特化ゾーンを作る … 1回の抽選の1/699で入る」）：表の あたまに ポイント特化ゾーン 1/699（いつもの 表・幻の馬・神様馬の どれにも）
        check(tabS == ['699:zn:', '600:tk:', '399:rt:kamisama', '245:rt:maboroshi', '125:rt:normal', '121:pt:300', '99:pt:200', '95:pt:100', '55:pt:50', '25:pt:20', '15:pt:10'], f'お世話の 抽選の 表：ルーレット 1/125・1/245・1/399・チケット 1/600・200P 1/99・300P 1/121 は そのまま／第4.165版：10P 1/15・20P 1/25・50P 1/55・100P 1/95・ポイント特化ゾーン 1/699（{tabS}）')
        tabV = pg.evaluate("() => { const T = TCApp._t, f = t => t.map(([p, z]) => Math.round(1 / p) + ':' + (z.v ? z.v.join('/') : z.k)), sum = t => t.reduce((a, [p]) => a + p, 0); return { mab: f(T.PRIZES_VISIT.maboroshi), kami: f(T.PRIZES_VISIT.kamisama), rt: T.RT, x: T.ODDS.highX, sums: [sum(T.PRIZES), sum(T.PRIZES_VISIT.maboroshi), sum(T.PRIZES_VISIT.kamisama)] }; }")
        check(tabV['mab'] == ['699:zn', '60:3200/6400', '30:1600/3200', '15:800/1600'] and tabV['kami'] == ['699:zn', '32:10000/20000', '16:5000/10000', '8:2000/4000'] and tabV['rt'] == {'normal': [800, 1600], 'maboroshi': [1600, 3200], 'kamisama': [3200, 6400]},
              f"幻の馬・神様馬の 表：1/15・1/30・1/60／1/8・1/16・1/32（ポイントの 数は そのまま）＋ ポイント特化ゾーン 1/699（{tabV['mab']}・{tabV['kami']}）")
        check(all(x * tabV['x'] < 1 for x in tabV['sums']) and abs(tabV['sums'][0] - 0.169995 - 1 / 699) < 0.0001 and abs(tabV['sums'][1] - 7 / 60 - 1 / 699) < 1e-9 and abs(tabV['sums'][2] - 7 / 32 - 1 / 699) < 1e-9,
              f"高確ゾーン（×{tabV['x']}）でも 当たりの 合計は 1 を こえない（いつも {tabV['sums'][0] * tabV['x']:.1%}・幻の馬 {tabV['sums'][1] * tabV['x']:.1%}・神様馬 {tabV['sums'][2] * tabV['x']:.1%}）")
        nm = lot['normal']; rate = lambda c, k: c.get(k, 0) / 20000
        check(abs(rate(nm, 'pt:10') - 1 / 15) < 0.007 and abs(rate(nm, 'pt:20') - 0.04) < 0.0055 and abs(rate(nm, 'pt:50') - 1 / 55) < 0.004 and abs(rate(nm, 'pt:100') - 1 / 95) < 0.0035 and abs(1 - rate(nm, '-') - 0.1714) < 0.011 and abs(rate(nm, 'zn:') - 1 / 699) < 0.0013
              and abs(rate(lot['mab'], 'zn:') - 1 / 699) < 0.0013 and abs(rate(lot['kami'], 'zn:') - 1 / 699) < 0.0013
              and abs(rate(nm, 'rt:normal') - 1 / 125) < 0.003 and abs(rate(nm, 'rt:maboroshi') - 1 / 245) < 0.0022 and abs(rate(nm, 'rt:kamisama') - 1 / 399) < 0.0018 and abs(rate(nm, 'tk:') - 1 / 600) < 0.0015,
              f"2万回 ひくと：10P {rate(nm, 'pt:10'):.1%}・20P {rate(nm, 'pt:20'):.1%}・50P {rate(nm, 'pt:50'):.1%}・100P {rate(nm, 'pt:100'):.2%}・ルーレット {rate(nm, 'rt:normal'):.2%}（0.8%）・{rate(nm, 'rt:maboroshi'):.2%}（約0.41%）・{rate(nm, 'rt:kamisama'):.2%}（約0.25%）・チケット {rate(nm, 'tk:'):.2%}（約0.17%）・ポイント特化ゾーン {rate(nm, 'zn:'):.2%}（約0.14%：幻の馬 {rate(lot['mab'], 'zn:'):.2%}・神様馬 {rate(lot['kami'], 'zn:'):.2%}）・何か 当たる {1 - rate(nm, '-'):.1%}（約17.1%：第4.165版）")
        hz = pg.evaluate("""() => { const T = TCApp._t, st = TCApp.state, S = TCCare.S, n = 20000, c = {}; st.visit = null;
          for (let i = 0; i < n; i++) { S.high = 3; const z = T.draw(); const k = z ? z.k + ':' + (z.k === 'pt' ? z.v : (z.tier || '')) : '-'; c[k] = (c[k] || 0) + 1; }
          S.high = 0; st.high = 0; return c; }""")
        check(abs(rate(hz, 'pt:10') - 4 / 15) < 0.014 and abs(rate(hz, 'pt:100') - 4 / 95) < 0.006 and abs(1 - rate(hz, '-') - 0.6857) < 0.013 and abs(rate(hz, 'rt:normal') - 4 / 125) < 0.006 and abs(rate(hz, 'tk:') - 4 / 600) < 0.003 and abs(rate(hz, 'zn:') - 4 / 699) < 0.0027,
              f"高確ゾーン（4倍）：10P {rate(hz, 'pt:10'):.1%}（約26.7%）・100P {rate(hz, 'pt:100'):.1%}（約4.2%）・ルーレット {rate(hz, 'rt:normal'):.1%}（3.2%）・チケット {rate(hz, 'tk:'):.2%}（約0.67%）・ポイント特化ゾーン {rate(hz, 'zn:'):.2%}（約0.57%）・何か 当たる {1 - rate(hz, '-'):.1%}（約68.6%：1 を こえない ので まれな 当たりも 4倍の まま）")
        print('■ 当たりを とりこぼさない・トークンの 数え方（第4.140版の バグ直し）')
        #   当たりは お世話の はじめに 決まる → すぐ 保存（pend）→ 演出の あとで わたして 消す
        pd = pg.evaluate("""async () => { const T = TCApp._t, st = TCApp.state, S = TCCare.S, W = TengelWallet, rnd = Math.random; st.visit = null; S.high = 0; st.high = 0; st.pend = null;
          const sv = () => (JSON.parse(localStorage.getItem('tengel.tc')) || {}).pend || null, t0 = W.total();
          Math.random = () => 0.04; const z = T.lottery(); Math.random = rnd;                    // 100P の 当たりを ひく（第4.165版の 表：0.0346〜0.0451 が 100P）
          const p1 = sv(), t1 = W.total();
          await T.onPrize(z); await new Promise(r => setTimeout(r, 500));
          const p2 = sv(), t2 = W.total();
          T.give(z); await new Promise(r => setTimeout(r, 400)); const t3 = W.total();           // 同じ 当たりを もう一度 わたしても 足さない
          Math.random = () => 0.012; const r1 = T.lottery(); Math.random = rnd; const p3 = sv(); st.pend = null; localStorage.setItem('tengel.tc', JSON.stringify(st));   // ルーレット（ふつう）：止まる 所も 決めて ある
          const tk0 = st.tickets || 0; T.give({ k: 'tk', n: 2, id: 'tc-test-tk' }); const tk1 = st.tickets || 0; st.tickets = tk0; localStorage.setItem('tengel.tc', JSON.stringify(st));
          return { z: z && [z.k, z.v, typeof z.id], p1: p1 && [p1.k, p1.v, p1.id === z.id], d1: t1 - t0, p2, d2: t2 - t0, d3: t3 - t0, r1: r1 && [r1.k, r1.tier, r1.win, r1.a, r1.b], p3: p3 && [p3.k, p3.win, p3.a, p3.b, p3.id === r1.id], tk: tk1 - tk0 }; }""")
        check(pd['z'] == ['pt', 100, 'string'] and pd['p1'] == ['pt', 100, True] and pd['d1'] == 0 and pd['p2'] is None and pd['d2'] == 100 and pd['d3'] == 100,
              f'当たり（100P）は ひいた ときに 保存 → 演出の あとで 台帳へ（+100P）→ 保存を 消す・同じ 当たりは 2回 足さない（{pd}）')
        check(pd['r1'] == ['rt', 'normal', 0, 800, 1600] and pd['p3'] == ['rt', 0, 800, 1600, True] and pd['tk'] == 2, 'ルーレットは 止まる 所（800P か 1600P）も ひいた ときに 決めて 保存・チケットは 数を 足す')
        #   お世話で 1つ 使った ちょうど その とき 5分 たって 5つ たまる（第4.165版：5分ごとに 5つ）→ 使った ぶんは 消えない（5 → 4 → 9。使った ぶんが 消えると 10）
        tr = pg.evaluate("""async () => { const st = TCApp.state, S = TCCare.S, now = Math.max(Date.now(), +st.seen || 0);
          st.stock = 5; S.stock = S.stockShow = 5; st.stockAt = now; await new Promise(r => setTimeout(r, 200));
          S.stock = 4; st.stockAt = now - 5 * 60000 - 500; await new Promise(r => setTimeout(r, 400));
          return [st.stock, S.stock]; }""")
        check(tr == [9, 9], f'お世話で 使った トークンは、同じ 瞬間に 5つ たまっても 消えない（5こ → 使って 4 → たまって 9：{tr}）')
        # 第4.165版（まさちゃん 11/13 11:46「お世話トークンに5分で5個追加に変更」）：5分 たつ ごとに 5つ・25 まで。開いて いる 間に たまると 右上に「＋N」
        #   （第4.159版：11/12 12:48「お世話トークンは25がMAXで、5分経つと5つずつ増えるようにね！」→ 14:50「10分で５つトークンが追加にして！」＝10分ごと）
        ac = pg.evaluate("""async () => { const st = TCApp.state, S = TCCare.S, now = Math.max(Date.now(), +st.seen || 0), w = ms => new Promise(r => setTimeout(r, ms)), o = TCApp._t.ODDS, pl = () => { const a = S.fx.filter(f => f.k === 'plus').map(f => f.txt); S.fx = S.fx.filter(f => f.k !== 'plus'); return a; };
          st.stock = 3; S.stock = S.stockShow = 3; st.stockAt = now - 4 * 60000 - 50000; pl(); await w(400); const a0 = [st.stock, pl()];      // 4分50秒：まだ
          st.stockAt = now - 5 * 60000 - 500; await w(400); const a1 = [st.stock, S.stock, pl()];                                     // 5分 → ＋5
          st.stockAt = now - 10 * 60000 - 900; await w(400); const a2 = [st.stock, pl()];                                             // 10分 → ＋10
          st.stockAt = now - 30 * 60000; await w(400); const a3 = [st.stock, pl()]; await w(300); const a4 = [st.stock, pl()];        // 30分 → 25 まで（18 → 25）・そのあとは ふえない
          return { a0, a1, a2, a3, a4, odds: [o.tokenMin, o.tokenStep, o.tokenMax] }; }""")
        check(ac['odds'] == [5, 5, 25] and ac['a0'] == [3, []] and ac['a1'] == [8, 8, ['+5']] and ac['a2'] == [18, ['+10']] and ac['a3'] == [25, ['+7']] and ac['a4'] == [25, []] and pg.evaluate("() => TCCare.RULE.stockEvery") == 300,
              f'お世話トークンは 5分ごとに 5つ・25 まで（第4.165版）：4分50秒＝まだ（{ac["a0"][0]}）→ 5分＝＋5（{ac["a1"][0]}）→ 10分＝＋10（{ac["a2"][0]}）→ 30分＝25 で 止まる（{ac["a3"]}）・右上に「＋N」')
        # 第4.144版（11/10 18:04 まさちゃん「馬のリセットは5分に切り替えよう！…最低5回お世話をした段階でリセットタイマーが作動して(お世話をしてる間はリセットなし)5分経ったらリセット。
        #   …開きっぱなしでもお世話の操作をしない限りは馬は変わらないでいて！ただ、幻の馬と神様馬は…開いてから30分経過すると切り替わる仕組みにして！
        #   幻の馬と神様馬は、上のバナーの下に切り替わる条件を表示して！・タイムリミット・お世話の回数 お世話5回完了後の切り替わりタイマー」・18:13「幻の馬と神様馬も最低5回お世話完了後はリセットタイマー作動で5分でリセットね！」）
        print('■ 馬の リセット（第4.144版）')
        RS = "() => { const st = TCApp.state, v = TCCare.S.vinfo; return { rs: Object.assign({}, st.rs), visit: st.visit ? st.visit.kind : null, left: st.visit ? Math.round((st.visit.until - Date.now()) / 1000) : null, vinfo: v ? { n: v.n, need: v.need, left: Math.round(v.left), timer: v.timer == null ? null : Math.round(v.timer), draws: v.draws, max: v.max } : null, rows: v ? TCCare.vinfoRows(v).map(r => [r[0], r[1], r[2]]) : null, box: TCCare.vinfoBox(), msg: document.querySelector('#tcOv .tcmsg').textContent, msgOn: document.querySelector('#tcOv .tcmsg').classList.contains('on') }; }"
        od = pg.evaluate("() => { const o = TCApp._t.ODDS; return [o.resetCares, o.resetMin, o.visitMin, o.tick, Math.round(1 / o.mab), Math.round(1 / o.kami)]; }")
        check(od == [5, 5, 30, 120, 245, 399] and pg.evaluate("() => TCApp._t.ODDS.visitDraws") == {'maboroshi': 10, 'kamisama': 5} and pg.evaluate("() => [TCApp._t.drawMax(), TCApp._t.drawLeft() === Infinity]") == [0, True],
              f'きまりの 数：お世話 5回 → タイマー 5分・幻の馬／神様馬の タイムリミット 30分・抽選は 幻の馬 1/245・神様馬 1/399（{od}）・第4.168版：来て いる 間の 抽選は 幻の馬 10回・神様馬 5回 まで（いつもの 馬は 上限 なし）')
        #   2分ごとの チャンスでは 幻の馬・神様馬は 来ない（前は ここで ひいて いた：Math.random が 0 なら 神様馬）。高確ゾーンは 今までどおり
        c1 = pg.evaluate("""() => { const T = TCApp._t, st = TCApp.state, S = TCCare.S, rnd = Math.random; let i = 0; st.visit = null; S.high = 0; st.high = 0;
          Math.random = () => (i++ === 0 ? 0 : 0.99); T.chance(S.lastT || 0); Math.random = rnd;
          const r = { visit: st.visit, high: S.high, src: /startVisit|nextHorse|doReset/.test(String(T.chance)) };
          S.high = 0; st.high = 0; S.fx = (S.fx || []).filter(f => f.k !== 'luck'); return r; }""")
        check(c1 == {'visit': None, 'high': 5, 'src': False}, f'2分ごとの チャンス：幻の馬・神様馬の 抽選は しない（高確ゾーンは 今までどおり）（{c1}）')
        #   お世話 4回までは タイマーは 動かない・5回で 動く（のこり 5:00）
        pg.evaluate("() => { const st = TCApp.state; st.visit = null; st.rs = { n: 4, at: 0, el: 0 }; }"); pg.wait_for_timeout(700)
        r4 = pg.evaluate(RS)
        pg.evaluate("() => { TCApp.state.rs.n = 5; }"); pg.wait_for_timeout(700)
        r5 = pg.evaluate("() => { const st = TCApp.state, sv = JSON.parse(localStorage.getItem('tengel.tc')); return { n: st.rs.n, on: st.rs.at > 0, left: Math.round(TCApp._t.rsLeft(Date.now())), saved: sv.rs && sv.rs.at > 0, visit: st.visit }; }")
        check(r4['rs']['at'] == 0 and r4['visit'] is None and r5['n'] == 5 and r5['on'] and 296 <= r5['left'] <= 300 and r5['saved'] and r5['visit'] is None,
              f'お世話 4回では タイマーは 動かない・5回めが おわると 動く（のこり {r5["left"]}秒・保存も する）（{r4["rs"]}・{r5}）')
        #   お世話の 途中・説明書を ひらいて いる 間は、5分 たっても リセット しない（おわってから）
        pg.evaluate("() => { TCApp._t.force(null); TCCare.S.busy = true; TCApp.state.rs.at = Date.now() - 6 * 60000; }"); pg.wait_for_timeout(900)      # 抽選の 結果は _t.force で 決める（Math.random は さしかえない：馬の 頭は 作る ときの Math.random を おぼえる）
        b1 = pg.evaluate("() => [TCApp.state.rs.n, TCApp.state.rs.at > 0]")
        pg.evaluate("() => { TCCare.S.busy = false; TCGuide.open(document.querySelector('#tcOv .tcst'), {}); }"); pg.wait_for_timeout(900)
        b2 = pg.evaluate("() => [TCApp.state.rs.n, TCApp.state.rs.at > 0, TCGuide.isOpen()]")
        pg.evaluate("() => TCGuide.close()"); pg.wait_for_timeout(1200)
        b3 = pg.evaluate(RS)
        check(b1 == [5, True] and b2 == [5, True, True] and b3['rs'] == {'n': 0, 'at': 0, 'el': 0} and b3['visit'] is None and b3['vinfo'] is None,
              f'お世話の 途中・説明書を ひらいて いる 間は リセット しない → おわると リセット（抽選 → いつもの 馬の まま・数えは 0 から）（{b1}・{b2}・{b3["rs"]}）')
        #   リセットの 抽選で 神様馬（1/399）→ やってくる・タイムリミット 30分・バナーの 下に 切り替わる 条件
        pg.evaluate("() => { TCApp._t.force('kamisama'); TCApp.state.rs = { n: 5, at: Date.now() - 6 * 60000, el: 0 }; }")
        pg.wait_for_function("() => TCApp.state.visit && TCApp.state.visit.kind === 'kamisama'", timeout=30000)
        pg.wait_for_function("() => TCCare.vinfoBox() && TCCare.S.vinfo", timeout=60000); pg.wait_for_timeout(1500)
        v0 = pg.evaluate(RS); shot(pg, 'tc_reset_kami')
        # 第4.168版（まさちゃん 11/14 01:26「神様馬は、抽選最大5回まで」）：神様馬の 札は「タイムリミット／抽選 0/5回」の 2行（5回めの 抽選で 帰る ので 切り替わりタイマーの 行は 出さない）
        check(v0['visit'] == 'kamisama' and 1780 <= v0['left'] <= 1800 and v0['rs']['n'] == 0 and v0['rs']['at'] == 0 and '神様馬が やってきた' in v0['msg']
              and len(v0['rows']) == 2 and v0['rows'][0][0] == 'タイムリミット' and v0['rows'][0][1].startswith('29:') and v0['rows'][1] == ['抽選', '0/5回', False] and [v0['vinfo']['draws'], v0['vinfo']['max']] == [0, 5],
              f'リセットの 抽選で 神様馬が やってくる・タイムリミット 30分・バナーの 下に「タイムリミット 29:xx／抽選 0/5回」（{v0["rows"]}）')
        #   場所と 大きさ：11/10 18:31 まさちゃん「馬と被らないようにもっと上にして！あと、テロップもう少し大きさ小さくして…大きいと背景も分かりにくい！」
        #   → 18:44「リセット条件バナーの下から左上のハートのトークンの下に表示するようにして！」：左上の なかよしの 板の すぐ 下・左そろえ・小さく（420×125）。バナーは その 下
        bx = v0['box']; gz = bx['gauge'] if bx else None
        check(bx and gz == [26, 34, 600, 126] and bx['x'] == gz[0] and gz[1] + gz[3] < bx['y'] <= gz[1] + gz[3] + 20 and bx['x'] + bx['w'] <= gz[0] + gz[2] and bx['w'] <= 460 and bx['h'] <= 130
              and bx['banTop'] == 290 and bx['y'] + bx['h'] <= bx['banTop'] + 17 and bx['y'] + bx['h'] <= 300,
              f'条件の 札は 左上の なかよしの 板の すぐ 下（左そろえ・{bx["w"]}×{bx["h"]}・上 {bx["y"]}〜下 {bx["y"] + bx["h"]}）・バナー（上 {bx["banTop"]}）は その 下で 重ならない（はじめは バナーの 下 640×180・606〜786）')
        pg.evaluate("() => { TCApp.state.rs.n = 3; }"); pg.wait_for_timeout(500); v1 = pg.evaluate(RS)
        pg.evaluate("() => { TCApp.state.visit.until = Date.now() + 50 * 1000; }"); pg.wait_for_timeout(600); v3 = pg.evaluate(RS)
        check(len(v1['rows']) == 2 and v1['rows'][1] == ['抽選', '3/5回', False] and v1['visit'] == 'kamisama' and v3['rows'][0][1] in ('0:50', '0:49') and v3['rows'][0][2] is True,
              f'抽選 3回 → 3/5回・タイムリミットの のこり 1分は 赤（{v1["rows"][1]}・{v3["rows"][0]}）')
        #   神様馬：5回めの 抽選（上限）→ 5/5回（赤）→ 結果を 見せて から 帰る（5分の タイマーは 待たない）→ 抽選：いつもの 馬に もどる
        pg.evaluate("() => { TCApp._t.force(null); const st = TCApp.state; st.visit.until = Date.now() + 20 * 60000; st.rs.n = 5; }"); _t0 = time.time(); pg.wait_for_timeout(600); v2 = pg.evaluate(RS)
        v2d = pg.evaluate("() => [TCApp._t.drawMax(), TCApp._t.drawLeft()]")
        pg.wait_for_function("() => !TCApp.state.visit", timeout=30000); _dt = time.time() - _t0; pg.wait_for_timeout(2500)
        v4 = pg.evaluate(RS)
        check(v2['visit'] == 'kamisama' and v2['rows'][1] == ['抽選', '5/5回', True] and v2d == [5, 0] and 2.0 <= _dt <= 12
              and v4['visit'] is None and v4['rs'] == {'n': 0, 'at': 0, 'el': 0} and '帰って いったよ' in v4['msg'] and v4['vinfo'] is None and v4['box'] is None,
              f'神様馬：5回めの 抽選で 5/5回（赤）→ 結果を 見せて から 帰る（{_dt:.1f}秒 あと・5分は 待たない）→ いつもの 馬に もどる・条件の 札は 消える（{v4["msg"]!r}・{v4["rs"]}）')
        #   幻の馬（上限 10回）：札は 3行「タイムリミット／抽選 0/10回／切り替わりタイマー 5回で スタート」・お世話 5回の あと 5分で リセット（→ 抽選：いつもの 馬に もどる）
        pg.evaluate("() => TCApp._t.startVisit('maboroshi')"); pg.wait_for_function("() => TCCare.vinfoBox() && TCCare.S.vinfo", timeout=60000); pg.wait_for_timeout(800)
        w0 = pg.evaluate(RS)
        pg.evaluate("() => { TCApp.state.rs.n = 3; }"); pg.wait_for_timeout(500); w1 = pg.evaluate(RS)
        pg.evaluate("() => { TCApp.state.rs.n = 7; }"); pg.wait_for_timeout(800); w2 = pg.evaluate(RS)
        check(w0['visit'] == 'maboroshi' and [r[0] for r in w0['rows']] == ['タイムリミット', '抽選', '切り替わりタイマー'] and w0['rows'][1] == ['抽選', '0/10回', False] and w0['rows'][2][1] == '5回で スタート' and [w0['vinfo']['draws'], w0['vinfo']['max']] == [0, 10]
              and w1['rows'][1][1] == '3/10回' and w1['rows'][2][1] == '5回で スタート' and w2['rows'][1] == ['抽選', '7/10回', False] and w2['rows'][2][1] in ('5:00', '4:59') and w2['vinfo']['timer'] >= 298 and w2['visit'] == 'maboroshi',
              f'幻の馬：札は 3行（{[r[0] for r in w0["rows"]]}）・抽選 3回 → 3/10回・5回 こえたら タイマーが 動く（{w1["rows"][1][1]}・{w2["rows"][1][1]}・{w2["rows"][2][1]}）')
        pg.evaluate("() => { const st = TCApp.state; st.rs.at = Date.now() - (4 * 60 + 15) * 1000; }"); pg.wait_for_timeout(600); w3 = pg.evaluate(RS)
        check(w3['rows'][2][1] in ('0:45', '0:44') and w3['rows'][2][2] is True, f'タイマーの のこり 1分は 赤（{w3["rows"][2][1]}）')
        pg.evaluate("() => { TCApp._t.force(null); const st = TCApp.state; st.rs.at = Date.now() - 6 * 60000; }")
        pg.wait_for_function("() => !TCApp.state.visit", timeout=30000); pg.wait_for_timeout(2500)
        w4 = pg.evaluate(RS)
        check(w4['visit'] is None and w4['rs'] == {'n': 0, 'at': 0, 'el': 0} and '帰って いったよ' in w4['msg'] and w4['vinfo'] is None and w4['box'] is None,
              f'幻の馬も お世話 5回の あと 5分で リセット → いつもの 馬に もどる・条件の 札は 消える（{w4["msg"]!r}・{w4["rs"]}）')
        #   幻の馬：10回めの 抽選（上限）→ 帰る（タイマーの 5分は 待たない）
        pg.evaluate("() => TCApp._t.startVisit('maboroshi')"); pg.wait_for_function("() => TCCare.vinfoBox() && TCCare.S.vinfo", timeout=60000); pg.wait_for_timeout(800)
        pg.evaluate("() => { TCApp._t.force(null); TCApp.state.rs.n = 9; }"); pg.wait_for_timeout(3600); x1 = pg.evaluate(RS)
        pg.evaluate("() => { TCApp.state.rs.n = 10; }"); _t0 = time.time(); pg.wait_for_timeout(500); x2 = pg.evaluate(RS)
        pg.wait_for_function("() => !TCApp.state.visit", timeout=30000); _dt = time.time() - _t0; pg.wait_for_timeout(2500); x3 = pg.evaluate(RS)
        check(x1['visit'] == 'maboroshi' and x1['rows'][1] == ['抽選', '9/10回', False] and x2['visit'] == 'maboroshi' and x2['rows'][1] == ['抽選', '10/10回', True] and 2.0 <= _dt <= 12
              and x3['visit'] is None and x3['rs'] == {'n': 0, 'at': 0, 'el': 0} and '帰って いったよ' in x3['msg'],
              f'幻の馬：9回では 帰らない（3.6秒 待っても いる）→ 10回めの 抽選で 10/10回（赤）→ {_dt:.1f}秒 あとに 帰る')
        #   上限の 抽選は 本物の PUSH で：神様馬・4回 すんで いる・「まとめて 使う」→ 1回 押すと（5回め）トークンが のこって いても PUSH は 消える → ごはん・おそうじは 始まらない（札）→ 帰る
        pg.evaluate("() => TCApp._t.startVisit('kamisama')"); pg.wait_for_function("() => TCCare.vinfoBox() && TCCare.S.vinfo", timeout=60000); pg.wait_for_timeout(800)
        pg.evaluate("() => { TCApp._t.force(null); const S = TCCare.S, s = TCApp.state; S.stock = S.stockShow = 3; s.stock = 3; s.rs.n = 4; S.bulk = true; s.bulk = true; TCCare.pushShow(S.lastT); }"); pg.wait_for_timeout(900)
        y0 = pg.evaluate(PU); yd = press(pg); pg.wait_for_timeout(150); y1 = pg.evaluate("() => [TCApp.state.rs.n, TCApp._t.drawLeft(), TCCare.S.stock]")
        pg.wait_for_timeout(700); y2 = pg.evaluate(PU); yd2 = press(pg); stage_click(pg, 327, 1494); pg.wait_for_timeout(350)
        y3 = pg.evaluate("() => ({ tags: TCCare.S.fx.filter(f => f.k === 'tagUI').map(f => f.txt), chooser: !!TCCare.S.chooser, mode: TCCare.S.mode, stock: TCCare.S.stock, visit: TCApp.state.visit && TCApp.state.visit.kind })")
        pg.wait_for_function("() => !TCApp.state.visit", timeout=30000); pg.wait_for_timeout(2500); y4 = pg.evaluate(PU); y4v = pg.evaluate("() => [TCApp.state.visit, TCApp.state.rs.n, TCApp._t.drawLeft() === Infinity]")
        pg.evaluate("() => { const S = TCCare.S, s = TCApp.state; S.bulk = false; s.bulk = false; }")
        check(y0['live'] and y0['bulk'] and y0['stock'] == 3 and yd == 1 and y1 == [5, 0, 2] and not y2['live'] and yd2 == 0 and y3['visit'] == 'kamisama' and 'この 馬の 抽選は おわったよ' in y3['tags'] and not y3['chooser'] and y3['mode'] is None and y3['stock'] == 2
              and y4v == [None, 0, True] and not y4['live'] and y4['stock'] == 2,
              f'神様馬・4回 すんで「まとめて 使う」で PUSH → 1回 押すと 5回め＝上限：トークンが のこって いても（{y1[2]}こ）PUSH は 消える・もう 押せない（{yd2}）・ごはんは 始まらない（札「{y3["tags"][-1] if y3["tags"] else ""}」）→ 帰る・トークンは そのまま')
        #   タイムリミット（来てから 30分）：お世話を しなくても 帰る
        pg.evaluate("() => TCApp._t.startVisit('maboroshi')"); pg.wait_for_function("() => TCCare.vinfoBox() && TCCare.S.vinfo", timeout=60000); pg.wait_for_timeout(800)
        m0 = pg.evaluate(RS)
        pg.evaluate("() => { const st = TCApp.state; st.rs.n = 2; st.visit.until = Date.now() - 1000; }")
        pg.wait_for_function("() => !TCApp.state.visit", timeout=30000); pg.wait_for_timeout(2500)
        m1 = pg.evaluate(RS)
        check(m0['visit'] == 'maboroshi' and m0['rows'][0][1].startswith('29:') and m1['visit'] is None and m1['rs'] == {'n': 0, 'at': 0, 'el': 0} and '帰って いったよ' in m1['msg'],
              f'幻の馬：タイムリミット（30分）で 帰る（お世話を して いなくても）・数えは 0 から（{m0["rows"][0]}・{m1["rs"]}）')
        #   第4.159版：お世話の あとの PUSH を 押さずに 置いて おいても、タイムリミットは 止まらない（神様馬を 帰さずに トークンを ためて から まとめて 押す、という 抜け穴を 作らない）。
        #   ただし 当たりを わたして いる 途中（保存に 当たりが ある：ルーレット当選の キュインキュイーンの 間・演出の 間）は 馬を 入れかえない
        pg.evaluate("() => TCApp._t.startVisit('kamisama')"); pg.wait_for_function("() => TCCare.vinfoBox() && TCCare.S.vinfo", timeout=60000); pg.wait_for_timeout(800)
        pg.evaluate("() => { const S = TCCare.S, s = TCApp.state; S.stock = S.stockShow = 3; s.stock = 3; TCCare.pushShow(S.lastT); s.pend = { k: 'rt', tier: 'kamisama', a: 10000, b: 20000, win: 0, id: 'tc-hold-test' }; s.visit.until = Date.now() - 1000; }"); pg.wait_for_timeout(1500)
        h0 = pg.evaluate("() => [!!(TCCare.S.push && TCCare.S.push.hideT == null), TCApp.state.visit && TCApp.state.visit.kind]")
        pg.evaluate("() => { TCApp.state.pend = null; }")
        okh = True
        try: pg.wait_for_function("() => !TCApp.state.visit", timeout=30000)
        except Exception: okh = False
        pg.wait_for_timeout(2500); h1 = pg.evaluate(PU); h1v = pg.evaluate("() => [TCApp.state.visit, TCApp._t.fieldName()]")
        dh = press(pg); pg.wait_for_timeout(900); h2 = pg.evaluate(PU)
        check(h0 == [True, 'kamisama'] and okh and h1['live'] and h1v[0] is None and h1v[1] in ('morning', 'evening', 'night') and dh == 1 and h2['stock'] == 2 and not h2['live'],
              f'PUSH を 出した まま 置いても タイムリミットで 帰る（当たりを わたして いる 途中 だけ 待つ：{h0}）・PUSH は のこって いて、押すと いつもの 馬の くじ（トークン 3 → {h2["stock"]}）')
        #   ひらいて いる だけ（お世話なし）では 何も おきない：タイマーは 動かない・馬は かわらない
        pg.evaluate("() => { TCApp.state.rs = { n: 0, at: 0, el: 0 }; }"); pg.wait_for_timeout(1500)
        i1 = pg.evaluate(RS)
        check(i1['rs'] == {'n': 0, 'at': 0, 'el': 0} and i1['visit'] is None, f'お世話を しなければ タイマーは 動かず 馬も かわらない（{i1["rs"]}）')
        #   抽選（nextHorse）：1/399 より 小さい → 神様馬・つぎの 1/245 → 幻の馬・それ 以外 → いつもの 馬（Math.random を その 場だけ さしかえて 見る：馬は 作らない）
        nh = pg.evaluate("() => { const T = TCApp._t, rnd = Math.random, f = v => { Math.random = () => v; const r = T.nextHorse(); Math.random = rnd; return r; }; return [f(0), f(1 / 399 - 1e-6), f(1 / 399 + 1e-6), f(1 / 399 + 1 / 245 - 1e-6), f(1 / 399 + 1 / 245 + 1e-6), f(0.5), f(0.999)]; }")
        check(nh == ['kamisama', 'kamisama', 'maboroshi', 'maboroshi', None, None, None], f'次の 馬の 抽選：神様馬 1/399・幻の馬 1/245・それ 以外は いつもの 馬（{nh}）')
        print('■ ルーレット（神様馬：10000P か 20000P）')
        pg.evaluate("() => { window.__rtDone = false; TCFX.roulette(document.querySelector('#tcOv .tcfx'), { th: 'kamisama', a: 10000, b: 20000, win: 1, bg: 'divine', se: TCApp._snd.se }).then(() => { window.__rtDone = true; }); }")
        pg.wait_for_timeout(2500); shot(pg, 'tc_rt_wait')
        check(pg.evaluate("() => document.querySelector('#tcOv .tcfx').classList.contains('on') && !window.__rtDone"), 'タップを 待つ')
        # 第4.158版（まさちゃん 11/12 08:59「このルーレットの神様馬、目が怖いから金色に光らせて！あと、画像がなんかまだらに色がついてるから綺麗にできる？」・09:00「幻の馬のルーレットは、目を紫に光らせて！」）：
        #   絵は きれいに した 新しい 絵（rt_<絵>_<部品>2.webp）・目は 光の 玉（絵の 中）＋ゆっくり 息を する 光（drawEye）。目の まん中・光の にじみ（右下へ 24, 6）・はなれた 所（70, 40）の 色を 0.1秒ごとに 2.6秒
        RTEYE = """([ex, ey]) => { const cv = document.querySelector('#tcOv .tcfx'), W = 390, H = 614, K = H / 1536, OX = (W - 1024 * K) / 2, PX = cv.width / W, g = cv.getContext('2d');
          const at = (dx, dy) => [...g.getImageData(Math.round((OX + (ex + dx) * K) * PX), Math.round((ey + dy) * K * PX), 1, 1).data].slice(0, 3);
          return { core: at(0, 0), far: at(24, 6), out: at(70, 40) }; }"""

        def rt_eye(eye):
            ser = []
            for _ in range(26):
                ser.append(pg.evaluate(RTEYE, eye)); pg.wait_for_timeout(100)
            st_ = {}
            for k in ('core', 'far', 'out'):
                v = [x[k] for x in ser]
                st_[k] = dict(lo=[min(c[i] for c in v) for i in range(3)], hi=[max(c[i] for c in v) for i in range(3)], rng=max(sum(c) for c in v) - min(sum(c) for c in v),
                              step=max(abs(v[j + 1][i] - v[j][i]) for j in range(len(v) - 1) for i in range(3)))
            return st_
        rt_files = lambda: sorted(set(pg.evaluate("() => performance.getEntriesByType('resource').map(e => e.name.split('/').pop().split('?')[0]).filter(n => n.startsWith('rt_'))")))
        ek = rt_eye([641, 271.9]); fk = rt_files()
        check(fk == [f'rt_kamisama_{p}2.webp' for p in ('knob', 'plate', 'ptr', 'stick')], f'ルーレットの 絵は きれいに した 新しい 絵 4まい（前の 絵は 読まない：{fk}）')
        kf, kc = ek['far'], ek['core']
        check(min(kc['lo']) >= 235 and kf['lo'][0] >= 220 and kf['lo'][0] - kf['hi'][2] >= 50 and kf['lo'][1] - kf['hi'][2] >= 15 and kf['rng'] >= 25 and kf['step'] <= 40 and ek['out']['rng'] <= 8,
              f'神様馬の 目：明るい 光の 玉（{kc["lo"]}）・まわりの 光は **金色**（{kf["lo"]}〜{kf["hi"]}）・ゆっくり 息を する（明るさの 幅 {kf["rng"]}・0.1秒の 変わり方 {kf["step"]}/255 まで＝ちかちか しない）・光は 目の まわり だけ（はなれた 所は 動かない：{ek["out"]["rng"]}）')
        # 第4.159版（まさちゃん 11/12 10:37「高い方なら超プレミアム神様的中のプチュンいれてポイント表示して！」・11:56「プチュンは、極ど的中と超プレミアム神様的中で使用してたプチュンの演出入れてね！」）：
        #   高い 方（20000P）で 止まる → 0.25秒 あとに プチュン（的中の 演出と 同じ 部品 .pc を 盤の 上に 重ねる・音 sfx_sdp）→ 真っ暗に なったら すぐ 幕が 明けて ポイント
        # 第4.159版（まさちゃん 11/12 13:27「ルーレット高い方が当たった時に、プチュンしてまたルーレットの画面に戻ると変だから、光輝きながら獲得ポイントを表示するようにして！一枚目がテロップの画像！」
        #   ・13:30「ドーン！！みたいな音と一緒にテロップ出して！」）：プチュンの あとは ルーレットに もどらない ＝ 暗い 舞台（キャンバスは すき通らない）に 金の 光と テロップ「大量ポイント」・音は ドーン！！
        pg.evaluate(SE_WRAP); pg.evaluate(PC_WATCH); pg.evaluate(SES)
        FXPIX = """() => { const cv = document.querySelector('#tcOv .tcfx'), g = cv.getContext('2d'), PX = cv.width / 390, at = (x, y) => [...g.getImageData(Math.round(x * PX), Math.round(y * PX), 1, 1).data];
          const T = TCFX.TELOP, w = T.w, h = w * T.ar, pc = [T.cx - w / 2 + (T.panel[0] + T.panel[2]) / 2 * w, T.cy - h / 2 + (T.panel[1] + T.panel[3]) / 2 * h];
          const box = g.getImageData(Math.round((pc[0] - 110) * PX), Math.round((pc[1] - 30) * PX), Math.round(220 * PX), Math.round(60 * PX)).data; let dark = 0, cream = 0, gold = 0, n = 0;
          for (let i = 0; i < box.length; i += 4) { const r = box[i], gg = box[i + 1], b = box[i + 2]; n++; if (r < 110 && gg < 60 && b < 40) dark++; else if (r > 235 && gg > 205 && b > 150 && r - b < 90) cream++; else if (r > 225 && gg > 130 && b < 150) gold++; }
          return { corner: [at(4, 4), at(385, 4), at(4, 609), at(385, 609)], top: at(195, 40), dark: dark / n, cream: cream / n, gold: gold / n }; }"""
        pg.mouse.click(300, 600); pg.wait_for_timeout(2200); px0 = pg.evaluate(FXPIX)
        # 第4.171版：この ブラウザが 爆発の 動画（H.264）を 読める ときは 爆発と いっしょの 流れに なる（ドーン！！は 0.6秒 あとに 鳴る ように たのむ・動画の 間は キャンバスの うしろを ぬらない）
        #   → 動画が おわった あと（3.1秒）の 絵で 見る ＝ 読めない ブラウザ（いままでの 場面）でも 同じ 絵に なって いる 時
        pg.wait_for_function("() => (window.__seL || []).includes('doon')", timeout=30000); pg.wait_for_timeout(3100); px1 = pg.evaluate(FXPIX); shot(pg, 'tc_rt_get')
        tl = pg.evaluate("() => performance.getEntriesByType('resource').map(e => e.name.split('/').pop().split('?')[0]).filter(n => n.startsWith('tc_telop')).length")
        pg.wait_for_timeout(1300); t_tap = time.time(); pg.mouse.click(200, 400)
        pg.wait_for_function("() => window.__rtDone", timeout=20000); t_close = time.time() - t_tap
        check(True, 'タップで 回って GET → タップで とじた')
        check(max(c[3] for c in px0['corner']) < 200 and all(c[3] == 255 for c in px1['corner']) and px1['top'][3] == 255 and px1['top'][0] > px1['top'][2] + 60 and tl >= 1
              and px1['dark'] > 0.08 and px1['cream'] > 0.1 and px1['gold'] > 0.08,
              f'高い 方：プチュンの あとは ルーレットに もどらない ＝ 暗い 舞台（回って いる 間は うしろの フィールドが すけて 見える {max(c[3] for c in px0["corner"])}/255 → テロップの 場面は すけない 255）に 金と 赤の 光・'
              f'まさちゃんの テロップ（tc_telop_big.webp）の 板の 中に ポイント（板の 色 {px1["cream"]:.0%}・字の ふち {px1["dark"]:.0%}・金の 字 {px1["gold"]:.0%}）')
        lg = pg.evaluate("() => window.__pcLog.slice()"); sx = pg.evaluate(SES); ins = [x for x in lg if x['k'] == 'in']; outs = [x for x in lg if x['k'] == 'out']
        dur = (outs[0]['t'] - ins[0]['t']) / 1000 if ins and outs else -1
        check(len(ins) == 1 and len(outs) == 1 and ins[0]['above'] and ins[0]['fxon'] and ins[0]['pc'] == 1 and ins[0]['parts'] > 300 and 'fxvis' in ins[0]['an'] and ins[0]['w'] == '390px' and abs(ins[0]['fxk'] - ins[0]['sw'] / 390) < 0.002
              and ins[0]['bg'] == 'rgb(0, 0, 0)' and ins[0]['pe'] == 'none' and 0.75 <= dur <= 2.4 and pg.evaluate("() => document.querySelectorAll('#tcOv .tcpc').length") == 0,
              f'高い 方：プチュンは 的中の 演出と 同じ 部品（.pc・中の 部品 {ins[0]["parts"] if ins else 0}こ・幅 390 を 舞台の 幅に 合わせる {ins[0]["fxk"] if ins else 0}倍）を 盤の 上に 重ねる → {dur:.2f}秒で 外す（真っ暗に なったら すぐ ポイント）')
        ix = lambda n: sx.index(n) if n in sx else -1
        check(0 <= ix('rt_stop') < ix('sfx_sdp×0.85') < ix('doon') and sx.count('doon') == 1 and 'rt_confirm' not in sx and not any(x.startswith('sfx_big') for x in sx),
              f'高い 方の 音：止まる → プチュン（的中の 演出の 音・小さめ）→ ドーン！！（テロップと いっしょ・前の 確定の 音は 鳴らさない）（{[x for x in sx if not x.startswith("rt_tick")]}）')
        # 大量ポイントの 場面を 1/30秒ごとに 3.5秒 描いて（TCFX.bigFrame：時計を 使わない）明るさ（相対輝度）を 測る：画面 ぜんぶ・大きい ます（3×4）・中の ます（6×10）・小さい ます（30pt：13×21）。
        #   向きがえ＝前の 山・谷 から 0.1 以上 動いて 向きが かわった 回数（2回で 点めつ 1回）。画面 ぜんぶの 明るさは 上がる だけ（1回）・大きい ますは 1秒に 2回 まで・小さい ますでも 6回（＝点めつ 3回）まで
        LUMJS = """async ([calm, noImg, val]) => {
          const cv = document.createElement('canvas'); cv.width = 390; cv.height = 614; const g = cv.getContext('2d', { willReadFrequently: true });
          const LUT = new Float32Array(256); for (let i = 0; i < 256; i++) { const c = i / 255; LUT[i] = c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); }
          const small = [], mid = [], big = [], glob = []; let img = true, amin = 255, snap = null;
          for (let k = 0; k <= 105; k++) {
            img = await TCFX.bigFrame(cv, k / 30, val, calm, noImg) && img;
            const d = g.getImageData(0, 0, 390, 614).data, s = new Float32Array(273), sn = new Uint32Array(273), m = new Float32Array(60), mn = new Uint32Array(60), b = new Float32Array(12), bn = new Uint32Array(12); let tot = 0;
            for (let y = 0; y < 614; y++) for (let x = 0; x < 390; x++) { const i = (y * 390 + x) * 4, L = 0.2126 * LUT[d[i]] + 0.7152 * LUT[d[i + 1]] + 0.0722 * LUT[d[i + 2]]; if (d[i + 3] < amin) amin = d[i + 3];
              const si = Math.min(20, (y / 30) | 0) * 13 + Math.min(12, (x / 30) | 0), mi = Math.min(9, (y / 61.4) | 0) * 6 + Math.min(5, (x / 65) | 0), bi = Math.min(3, (y / 153.5) | 0) * 3 + Math.min(2, (x / 130) | 0);
              s[si] += L; sn[si]++; m[mi] += L; mn[mi]++; b[bi] += L; bn[bi]++; tot += L; }
            small.push([...s].map((v, i) => +(v / sn[i]).toFixed(4))); mid.push([...m].map((v, i) => +(v / mn[i]).toFixed(4))); big.push([...b].map((v, i) => +(v / bn[i]).toFixed(4))); glob.push(+(tot / 239460).toFixed(4));
            if (k === 45) snap = cv.toDataURL('image/png');
          }
          return { small, mid, big, glob, img, amin, snap }; }"""

        def lum_tr(x, th=0.1):
            lo = hi = x[0]; d = 0; out = []
            for k, v in enumerate(x):
                if d == 0:
                    lo = min(lo, v); hi = max(hi, v)
                    if v - lo >= th: out.append(k); d = 1; hi = v
                    elif hi - v >= th: out.append(k); d = -1; lo = v
                elif d == 1:
                    hi = max(hi, v)
                    if hi - v >= th: out.append(k); d = -1; lo = v
                else:
                    lo = min(lo, v)
                    if v - lo >= th: out.append(k); d = 1; hi = v
            return out

        def lum_stat(r):
            G = r['glob']; mx = 0; dip = 0
            for v in G: mx = max(mx, v); dip = max(dip, mx - v)
            o = dict(g=len(lum_tr(G)), dip=dip, late=max(G[21:]) - min(G[21:]), end=G[-1], img=r['img'], amin=r['amin'])
            for key in ('big', 'mid', 'small'):
                S = r[key]; per = []
                for i in range(len(S[0])):
                    ks = lum_tr([f[i] for f in S]); per.append(max([sum(1 for q in ks if k0 <= q < k0 + 30) for k0 in ks] or [0]))
                o[key] = per
            o['still'] = max(max(abs(r['small'][k][i] - r['small'][-1][i]) for i in range(273)) for k in range(36, 106))      # 1.2秒より あと：さいごの コマとの 差（小さい ます）
            return o
        import base64 as _b64
        LN = pg.evaluate(LUMJS, [False, False, 20000]); ln = lum_stat(LN)
        if SHOT: open(os.path.join(SHOT, 'tc_big_v150.png'), 'wb').write(_b64.b64decode(LN['snap'].split(',')[1]))
        check(ln['img'] and ln['amin'] == 255 and ln['g'] == 1 and ln['dip'] <= 0.05 and ln['late'] <= 0.04 and 0.2 <= ln['end'] <= 0.45,
              f'大量ポイントの 場面：画面 ぜんぶの 明るさは 上がる だけ（向きがえ {ln["g"]}回・とちゅうで 下がるのは {ln["dip"]:.3f} まで）・0.7秒より あとは 一定（幅 {ln["late"]:.3f}）・すき通らない（{ln["amin"]}/255）・明るさ {ln["end"]:.2f}')
        n5 = sum(1 for v in ln['small'] if v >= 5); n3 = sum(1 for v in ln['mid'] if v >= 3)
        check(max(ln['big']) <= 2 and max(ln['mid']) <= 3 and n3 <= 6 and max(ln['small']) <= 6 and n5 <= 22,
              f'ちかちか しない：1秒の 向きがえ（2回で 点めつ 1回）＝大きい ます（画面の 8%）{max(ln["big"])}回 まで・中の ます（1.7%）{max(ln["mid"])}回 まで（3回は {n3}/60）・小さい ます（30pt）でも {max(ln["small"])}回 まで（5回 以上は {n5}/273）')
        LC = pg.evaluate(LUMJS, [True, False, 20000]); lc = lum_stat(LC)
        check(lc['img'] and lc['g'] == 1 and lc['dip'] <= 0.01 and max(lc['small']) <= 2 and max(lc['big']) <= 1 and lc['still'] <= 0.004 and abs(lc['end'] - ln['end']) < 0.06,
              f'「演出を控えめにする」の 場面：ふわっと 明るく なる だけ（向きがえ {lc["g"]}回・小さい ますでも {max(lc["small"])}回 まで）・1.2秒より あとは 動かない（差 {lc["still"]:.4f}）')
        LF = pg.evaluate(LUMJS, [False, True, 6400]); lf = lum_stat(LF)
        check(lf['img'] is False and lf['amin'] == 255 and lf['g'] == 1 and lf['dip'] <= 0.05 and max(lf['big']) <= 3 and 0.2 <= lf['end'] <= 0.5, f'絵が ない とき（手元に 素材が ない ビルド）：コードで 描いた 札で 出る（明るさ {lf["end"]:.2f}・画面 ぜんぶの 向きがえ {lf["g"]}回）')
        # ポイントは 板の 中 だけ（1,600P と 20,000P で 絵が ちがうのは 板の 中 だけ）・テロップの 決めごと（板の 場所・絵の たて÷よこ）は 絵と 合って いる
        dv = pg.evaluate("""async () => { const mk = async val => { const cv = document.createElement('canvas'); cv.width = 390; cv.height = 614; await TCFX.bigFrame(cv, 1.5, val, false, false); return cv.getContext('2d').getImageData(0, 0, 390, 614).data; };
          const a = await mk(1600), b = await mk(20000), T = TCFX.TELOP, w = T.w, h = w * T.ar, x0 = T.cx - w / 2 + T.panel[0] * w, x1 = T.cx - w / 2 + T.panel[2] * w, y0 = T.cy - h / 2 + T.panel[1] * h, y1 = T.cy - h / 2 + T.panel[3] * h; let inn = 0, out = 0;
          for (let y = 0; y < 614; y++) for (let x = 0; x < 390; x++) { const i = (y * 390 + x) * 4; if (Math.abs(a[i] - b[i]) + Math.abs(a[i + 1] - b[i + 1]) + Math.abs(a[i + 2] - b[i + 2]) > 24) { if (x >= x0 - 3 && x <= x1 + 3 && y >= y0 - 3 && y <= y1 + 3) inn++; else out++; } }
          return { inn, out, T: { panel: T.panel, ar: T.ar, w: T.w, src: T.src, spin: T.spin, sweep: T.sweep, hold: T.hold } }; }""")
        sys.path.insert(0, os.path.join(W, 'kisekae', 'tc')); import telop_asset as TA; from PIL import Image as _Im
        tim = _Im.open(os.path.join(TCA, 'tc_telop_big.webp')).convert('RGBA'); pb_, pin_ = TA.panel(tim); TT = dv['T']
        check(dv['inn'] > 1500 and dv['out'] == 0 and TT['src'] == 'tc_telop_big.webp' and tim.size == (1110, 742) and abs(TT['ar'] - tim.size[1] / tim.size[0]) < 0.002 and max(abs(a - b) for a, b in zip(TT['panel'], pin_)) < 0.012
              and TT['w'] <= 390 and 18 * TT['spin'] / 6.2832 < 1 and TT['sweep'][0] >= 1.2 and TT['sweep'][1] >= 2 and TT['hold'] >= 1,
              f'ポイントは 板の 中 だけ（1,600P と 20,000P の ちがい：板の 中 {dv["inn"]}画素・外 {dv["out"]}）・板の 場所は 絵と 合って いる（コード {TT["panel"]}・絵 {pin_}）・'
              f'光の すじは 同じ 所を 1秒に {18 * TT["spin"] / 6.2832:.2f}回 通る・なでる 光は {TT["sweep"][1]}秒に 1回')
        print('■ ルーレットの 高い 方の 爆発（第4.171版）')
        # まさちゃん 2026/11/14 16:18「④トレーニングセンターの神様馬、幻の馬ルーレットで高い方が当選し、プチュンした後は、リアルな爆発と一緒に獲得ポイントの表示するようにして！」
        #   プチュンで 真っ暗に なった 瞬間に 爆発の 動画（演出の キャンバスの 下の 幕 .tcbm の 中の <video>）と 爆発の 音 → 0.6秒 あとに ドーン！！と テロップが 火の 手前に 飛びこむ → 動画が おわったら いままでの 場面
        BO = pg.evaluate("() => Object.assign({}, TCFX.BOOM)")
        check(BO['src'] == 'tc_rt_boom.mp4' and BO['se'] == 'tc_se_boom.m4a' and 0.4 <= BO['telop'] <= 0.8 and BO['late'] >= BO['telop'] and BO['len'] == 2.6 and 0.3 <= BO['wait'] < BO['telop'] and BO['gain'] <= 1,
              f'爆発の 決めごと：動画 {BO["src"]}・音 {BO["se"]}・テロップは {BO["telop"]}秒 あと・金の 光は {BO["late"]}秒 から {BO["rise"]}秒 かけて・動画が {BO["wait"]}秒 動かなければ あきらめる')
        check(pg.evaluate("() => document.querySelectorAll('#tcOv .tcbm').length") == 0, '上の ルーレットの あと：幕（.tcbm）は 残って いない')
        H264 = pg.evaluate("() => document.createElement('video').canPlayType('video/mp4; codecs=\"avc1.640032\"') !== ''")      # この ブラウザが アプリの 動画（H.264）を そのまま 読めるか
        BSRC = 'tc_rt_boom.mp4' if H264 else 'tc_rt_boom.webm'                                                                   # 読めない ときは 同じ 絵の webm を かわりに
        if HAVE_BOOM:
            import io as _io, numpy as _np
            print('    爆発の 動画：' + ('アプリに 入る 動画（H.264）を そのまま 流す' if H264 else 'この ブラウザは H.264 を 読めない ので、同じ 絵の webm を かわりに 流す'))
            #   1コマごとに：幕と 動画が あるか・動画の 進み・キャンバスの すみ（6, 6）と テロップの 板の 左はしの 内がわ（字の ない 所）の 画素。
            #   動画が 0.3秒・1.05秒まで 進んだ ときの 絵（幕の 色 → 動画 → キャンバスの 順に 重ねた もの＝画面に 見える 絵）を 写して おく（写す 時は 動画の 進みで 決める：テストの 道具の おくれに 左右されない）
            BM_REC = """() => { window.__bm = []; window.__bmSnap = {}; const cv = document.querySelector('#tcOv .tcfx'), g = cv.getContext('2d'), PX = cv.width / 390, T = TCFX.TELOP, w = T.w, h = w * T.ar;
              const pl = [T.cx - w / 2 + (T.panel[0] + 0.025 * (T.panel[2] - T.panel[0])) * w, T.cy - h / 2 + (T.panel[1] + T.panel[3]) / 2 * h], A = (x, y) => [...g.getImageData(Math.round(x * PX), Math.round(y * PX), 1, 1).data];
              const snap = v => { const c = document.createElement('canvas'); c.width = 390; c.height = 614; const q = c.getContext('2d'); q.fillStyle = '#060302'; q.fillRect(0, 0, 390, 614); q.drawImage(v, 0, 0, 390, 614); q.drawImage(cv, 0, 0, 390, 614); return c.toDataURL('image/png'); };
              const f = () => { const el = document.querySelector('#tcOv .tcbm'), v = el && el.querySelector('video'), ct = v ? v.currentTime : null, S = window.__bmSnap;
                if (v && +el.style.opacity === 1) { if (!S.a && ct >= 0.3) { S.a = snap(v); S.at = ct; } if (!S.b && ct >= 1.05) { S.b = snap(v); S.bt = ct; } }
                window.__bm.push({ t: performance.now(), el: !!el, under: !!el && el.nextElementSibling === cv, op: el ? +el.style.opacity : null, ct, corner: A(6, 6)[3], panel: A(pl[0], pl[1]), on: cv.classList.contains('on') });
                if (!window.__rtDone) requestAnimationFrame(f); };
              requestAnimationFrame(f); }"""
            BM_RUN = """(src) => { window.__rtDone = false; window.__bmSe = []; TCFX.BOOM.src = src;
              const se = (n, g, l) => { window.__bmSe.push([n.replace('tc_se_', '').replace('.m4a', ''), g == null ? 1 : g, l || 0, performance.now()]); return TCApp._snd.se(n, g, l); };
              TCFX.roulette(document.querySelector('#tcOv .tcfx'), { th: 'kamisama', a: 10000, b: 20000, win: 1, bg: 'divine', se }).then(() => { window.__rtDone = true; }); }"""
            STG = "() => { const r = document.querySelector('#tcOv .tcst').getBoundingClientRect(); return { x: r.left, y: r.top, width: r.width, height: r.height }; }"

            def bm_snap(du, name):
                png = _b64.b64decode(du.split(',')[1]); im = _np.asarray(_Im.open(_io.BytesIO(png)).convert('RGB'), dtype=_np.float32)
                if SHOT: open(os.path.join(SHOT, name + '.png'), 'wb').write(png)
                return im

            def bm_go(src):
                pg.evaluate(BM_RUN, src); pg.evaluate(BM_REC); pg.wait_for_timeout(2500); pg.mouse.click(300, 600)
                pg.wait_for_function("() => window.__bmSe.some(x => x[0] === 'boom' || x[0] === 'doon')", timeout=30000)

            def bm_end(wait_ms):
                pg.wait_for_timeout(wait_ms); pg.mouse.click(200, 400); pg.wait_for_function("() => window.__rtDone", timeout=20000); pg.wait_for_timeout(200)
                r = pg.evaluate("() => ({ bm: window.__bm, se: window.__bmSe, snap: window.__bmSnap, left: document.querySelectorAll('#tcOv .tcbm').length, on: document.querySelector('#tcOv .tcfx').classList.contains('on') })")
                return r

            # ---- 動画が 流れる とき
            bm_go(BSRC); pg.wait_for_timeout(700); shot(pg, 'tc_rt_boom_scr')
            R = bm_end(3200); fr = R['bm']; se_ = R['se']; SN = R['snap']
            tb = next((x[3] for x in se_ if x[0] == 'boom'), None); nm = [x[0] for x in se_ if not x[0].startswith('rt_tick')]
            bo_ = [x for x in se_ if x[0] == 'boom']; dn_ = [x for x in se_ if x[0] == 'doon']
            ix_ = lambda n: nm.index(n) if n in nm else -1
            check(tb is not None and len(bo_) == 1 and len(dn_) == 1 and bo_[0][1] == BO['gain'] and bo_[0][2] == 0 and dn_[0][1] == 1 and abs(dn_[0][2] - BO['telop']) < 1e-9 and abs(dn_[0][3] - bo_[0][3]) < 40
                  and 0 <= ix_('rt_stop') < ix_('sfx_sdp') < ix_('boom') < ix_('doon'),
                  f'音：止まる → プチュン → 爆発（tc_se_boom・大きさ {bo_[0][1] if bo_ else None}）→ {BO["telop"]}秒 あとに ドーン！！（テロップが 飛びこむ 時：{nm}）')
            if tb is not None:
                win = lambda a_, b_: [f for f in fr if tb + a_ <= f['t'] < tb + b_]
                # 時刻は 爆発の 音を たのんだ 時（tb）から 数える。動画が 動きだす コマは 少し おくれる ことが ある（〜0.2秒：その ぶん tb は 幕が 明ける 時より おそい）→ 窓の はしに よゆうを とる
                pre = [f for f in fr if f['t'] < tb - 150]; w1 = win(80, 520); w2 = win(1100, 2150); w3 = win(2950, 3400)
                check(len(pre) > 8 and all(f['el'] and f['under'] and f['op'] == 0 for f in pre),
                      f'幕と 動画は ルーレットの はじめに 用意して かくして おく（演出の キャンバスの すぐ 下・すき通し 0：{len(pre)}コマ）')
                cts = [f['ct'] for f in w1 if f['ct'] is not None]
                check(len(w1) >= 2 and all(f['el'] and f['op'] == 1 for f in w1) and cts and max(cts) > 0.2 and all(b_ >= a_ - 1e-6 for a_, b_ in zip(cts, cts[1:]))
                      and max(f['corner'] for f in w1) == 0 and max(f['panel'][3] for f in w1) == 0,
                      f'真っ暗に なった 瞬間に 爆発の 動画が 流れる（0.5秒で {max(cts) if cts else 0:.2f}秒 ぶん 進む）・はじめの {BO["telop"]}秒は 爆発 だけ（キャンバスには 何も 描かない：すき通し {max(f["panel"][3] for f in w1)}）')
                tp = next((f['t'] - tb for f in fr if f['t'] > tb and f['panel'][3] >= 250), None)
                check(tp is not None and BO['telop'] * 1000 + 100 <= tp <= BO['telop'] * 1000 + 520, f'テロップは 爆発の {BO["telop"]}秒 あとに 飛びこんで くる（板が はっきり 見えるのは {(tp or 0) / 1000:.2f}秒）')
                # 板の まん中の 画素は、数字が 回って いる 間 字の ふち（こげ茶）に かかる コマが ある → 色は まん中の 値で 見る（すけない ことは ぜんぶの コマで）
                pr2 = sorted(f['panel'][0] for f in w2)
                check(len(w2) >= 3 and all(f['el'] and f['op'] == 1 for f in w2) and max(f['corner'] for f in w2) < 250 and min(f['panel'][3] for f in w2) >= 250 and pr2[len(pr2) // 2] > 200,      # すき通った キャンバスに 重ねる ので、板の すき通しは 254 に なる コマが ある（255 の 99.6%：見た目は 同じ）
                      f'動画の 間は キャンバスの うしろを ぬらない（すみの すき通し {max(f["corner"] for f in w2)}/255 まで＝下の 火が 見える）・テロップの 板は すけない（{len(w2)}コマ・幕が 出て いない コマ {sum(1 for f in w2 if not (f["el"] and f["op"] == 1))}・板の すき通し {min(f["panel"][3] for f in w2) if w2 else None}・板の 赤 {pr2[0] if pr2 else None}〜{pr2[-1] if pr2 else None}）')
                check(len(w3) >= 1 and not any(f['el'] for f in w3) and all(f['corner'] == 255 for f in w3),
                      f'動画が おわったら（{BO["len"]}秒）幕を 外して いままでの 場面と 同じ 描き方（すみも すけない 255）')
            check(R['left'] == 0 and not R['on'], 'とじた あと：幕（.tcbm）は 残らない')
            # 絵：0.33秒＝画面 いっぱいの 火（明るい・テロップは まだ）／1.1秒＝テロップの 板（クリーム色）の 上と 下に 火（赤〜黄）
            #   絵：動画が 0.3秒まで 進んだ とき＝画面 いっぱいの 火（明るい・テロップは まだ）／1.05秒＝テロップの 板（クリーム色）の 上と 下に 火（黄〜赤）
            if SN.get('a') and SN.get('b'):
                im_a, im_b = bm_snap(SN['a'], 'tc_rt_boom_a'), bm_snap(SN['b'], 'tc_rt_boom_b'); reg = lambda im, x0, y0, x1, y1: im[int(y0):int(y1), int(x0):int(x1)].reshape(-1, 3)
                ca = reg(im_a, 60, 150, 330, 430); fire = lambda px: float(_np.mean((px[:, 0] > 150) & (px[:, 0] > px[:, 2] + 40))); hot = lambda px: float(_np.mean(px.max(1) > 200))
                T_ = pg.evaluate("() => TCFX.TELOP"); tw, th_ = T_['w'], T_['w'] * T_['ar']; plx = T_['cx'] - tw / 2 + T_['panel'][0] * tw; pcy = T_['cy'] - th_ / 2 + (T_['panel'][1] + T_['panel'][3]) / 2 * th_
                pb = reg(im_b, plx + 3, pcy - 20, plx + 14, pcy + 20); cream = float(_np.mean((pb[:, 0] > 225) & (pb[:, 1] > 195) & (pb[:, 2] > 140)))
                up_ = reg(im_b, 60, 40, 330, T_['cy'] - th_ / 2 - 12); dn2 = reg(im_b, 60, T_['cy'] + th_ / 2 + 70, 330, 560); pa = reg(im_a, plx + 3, pcy - 20, plx + 14, pcy + 20)
                check(float(ca.mean()) > 170 and hot(ca) > 0.75 and float(_np.mean((pa[:, 0] > 225) & (pa[:, 2] > 140) & (pa[:, 0] - pa[:, 2] < 90) & (pa[:, 0] - pa[:, 2] > 20))) < 0.5,
                      f'動画が {SN["at"]:.2f}秒の とき：画面の まん中は 火の 玉（明るさ {ca.mean():.0f}/255・明るい 所 {hot(ca):.0%}）・テロップは まだ 出て いない')
                check(cream > 0.8 and fire(up_) > 0.2 and fire(dn2) > 0.1, f'動画が {SN["bt"]:.2f}秒の とき：テロップの 板（クリーム色 {cream:.0%}）の 上（火の 色 {fire(up_):.0%}）と 下（{fire(dn2):.0%}）に 火が 見える')
            else: check(False, f'爆発の 絵を 写せなかった（{sorted(SN)}）')
            # ---- 動画が 動かない とき（再生を はじめたのに コマが 進まない）：0.3秒で あきらめて 暗い 舞台 → 0.6秒で テロップ（音は 爆発 → ドーン！！の まま）
            pg.evaluate("() => { window.__playO = HTMLMediaElement.prototype.play; HTMLMediaElement.prototype.play = function () { return new Promise(() => {}); }; }")
            bm_go(BSRC); R = bm_end(2600); fr = R['bm']; se_ = R['se']
            pg.evaluate("() => { HTMLMediaElement.prototype.play = window.__playO; }")
            tb = next((x[3] for x in se_ if x[0] == 'boom'), None); dn_ = [x for x in se_ if x[0] == 'doon']
            if tb is not None:
                win = lambda a_, b_: [f for f in fr if tb + a_ <= f['t'] < tb + b_]; w2 = win(1300, 2000)
                gone = next((f['t'] - tb for f in fr if f['t'] > tb and not f['el']), None); w1 = win((gone or 0) + 20, BO['telop'] * 1000 - 5) if gone is not None else []
                check(gone is not None and BO['wait'] * 1000 - 220 <= gone <= BO['wait'] * 1000 + 150 and all(f['corner'] == 255 and f['panel'][3] == 255 and max(f['panel'][:3]) < 40 for f in w1)
                      and all(f['corner'] == 255 for f in win((gone or 0) + 20, 2500))
                      and len(w2) >= 2 and all(f['corner'] == 255 and f['panel'][3] >= 250 for f in w2) and sorted(f['panel'][0] for f in w2)[len(w2) // 2] > 200 and len(dn_) == 1 and abs(dn_[0][2] - BO['telop']) < 1e-9 and R['left'] == 0,
                      f'動画が 動かない とき：{(gone or 0) / 1000:.2f}秒で 幕を 外して 暗い 舞台（すけない：ルーレットは 見えない）→ テロップと ポイントは 出る（音は 爆発 → ドーン！！）')
            else: check(False, '動画が 動かない とき：爆発の 音が 鳴らなかった')
            # ---- 動画の ファイルが ない とき（読めない）：いままでの 場面（爆発の 音なし・ドーン！！は すぐ）
            bm_go('nai_boom.webm'); R = bm_end(2000); se_ = R['se']; dn_ = [x for x in se_ if x[0] == 'doon']
            check(not any(x[0] == 'boom' for x in se_) and len(dn_) == 1 and dn_[0][2] == 0 and R['left'] == 0 and all(f['op'] in (0, None) for f in R['bm']),
                  '動画の ファイルが ない とき：いままでの 場面（爆発の 音は 鳴らさない・ドーン！！は すぐ・幕は 見せない）')
            # ---- 「演出を控えめにする」：爆発は 出さない（幕も 用意しない）
            pg.evaluate("() => TengelFx.set({ calm: true })")
            bm_go(BSRC); R = bm_end(2000); se_ = R['se']
            pg.evaluate("() => TengelFx.set({ calm: false })")
            check(not any(x[0] == 'boom' for x in se_) and not any(f['el'] for f in R['bm']) and R['left'] == 0, '「演出を控えめにする」：爆発は 出さない（幕も 動画も 用意しない・音も いままで どおり）')
            pg.evaluate("() => { TCFX.BOOM.src = 'tc_rt_boom.mp4'; }")
            # ---- 光：動画の コマ（もとの 動画）と キャンバスの 絵（TCFX.bigFrame・時計を 使わない）を 1/30秒ごとに 重ねて 明るさを 測る（3.5秒）
            raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', BOOM_MP4, '-vf', 'scale=390:614', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True).stdout
            vid = _np.frombuffer(raw, _np.uint8).reshape(-1, 614, 390, 3); nv = len(vid)
            BFJ = """async ([vs, clear, late, rise]) => { const cv = window.__bmCv || (window.__bmCv = Object.assign(document.createElement('canvas'), { width: 390, height: 614 }));
              if (vs < 0) cv.getContext('2d').clearRect(0, 0, 390, 614); else await TCFX.bigFrame(cv, vs, 20000, false, false, { clear, late, rise });
              return cv.toDataURL('image/png'); }"""
            lin = lambda c: _np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
            G_, big_, mid_, small_ = [], [], [], []
            for k in range(106):
                v_ = k / 30; clear = v_ < BO['len'] + 0.1
                du = pg.evaluate(BFJ, [v_ - BO['telop'], clear, BO['late'] - BO['telop'], BO['rise']])
                cvs = _np.asarray(_Im.open(_io.BytesIO(_b64.b64decode(du.split(',')[1]))).convert('RGBA'), dtype=_np.float32); a_ = cvs[..., 3:4] / 255
                base = vid[k].astype(_np.float32) if k < nv else _np.zeros((614, 390, 3), _np.float32) + _np.array([6, 3, 2], _np.float32)
                out = cvs[..., :3] * a_ + base * (1 - a_) if clear else cvs[..., :3]
                L_ = lin(out / 255); L_ = 0.2126 * L_[..., 0] + 0.7152 * L_[..., 1] + 0.0722 * L_[..., 2]
                G_.append(float(L_.mean()))
                big_.append([float(L_[int(i * 153.5):int((i + 1) * 153.5), j * 130:(j + 1) * 130].mean()) for i in range(4) for j in range(3)])
                mid_.append([float(L_[int(i * 61.4):int((i + 1) * 61.4), j * 65:(j + 1) * 65].mean()) for i in range(10) for j in range(6)])
                small_.append([float(L_[i * 30:min(614, (i + 1) * 30), j * 30:(j + 1) * 30].mean()) for i in range(21) for j in range(13)])
            def per_sec(S):
                o = []
                for i in range(len(S[0])):
                    ks = lum_tr([f[i] for f in S]); o.append(max([sum(1 for q in ks if k0 <= q < k0 + 30) for k0 in ks] or [0]))
                return o
            gt = lum_tr(G_); pk = max(range(len(G_)), key=lambda i: G_[i]); pb_g, pm_g, ps_g = per_sec(big_), per_sec(mid_), per_sec(small_)
            n5 = sum(1 for v in ps_g if v >= 5)
            check(len(vid) == 78 and G_[0] < 0.01 and pk <= 18 and len(gt) <= 3 and max(G_[60:]) - min(G_[60:]) <= 0.05 and 0.2 <= G_[-1] <= 0.45,
                  f'爆発と いっしょの 場面の 明るさ（動画と キャンバスを 重ねて 測る）：まっ暗（{G_[0]:.3f}）→ 爆発で 明るく（山は {pk / 30:.2f}秒・{G_[pk]:.2f}）→ 火が おさまる → 金の 光で 明るく（向きがえ {len(gt)}回 ＝ 点めつは 1回）→ 2秒より あとは 一定（{G_[-1]:.2f}）')
            check(max(pb_g) <= 4 and max(pm_g) <= 5 and max(ps_g) <= 6 and n5 <= 30,
                  f'ちかちか しない：1秒の 向きがえ（2回で 点めつ 1回）＝大きい ます {max(pb_g)}回 まで・中の ます {max(pm_g)}回 まで・小さい ます（30pt）でも {max(ps_g)}回 まで（5回 以上は {n5}/273）')
        else: print('  ⚠️ 爆発の 動画（ios/tc_assets/tc_rt_boom.mp4）か ffmpeg が ない（爆発の 流れは 確かめて いない）')
        if HAVE:
            import numpy as _np2
            def _probe(f):
                r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,codec_name,profile,width,height,pix_fmt,r_frame_rate,nb_frames:format=duration', '-of', 'json', f], capture_output=True, text=True)
                return json.loads(r.stdout or '{}')
            bmp = os.path.join(TCA, 'tc_rt_boom.mp4'); bse = os.path.join(TCA, 'tc_se_boom.m4a')
            if os.path.exists(bmp) and os.path.exists(bse) and shutil.which('ffprobe'):
                pv = _probe(bmp); st_ = pv.get('streams', []); v0 = st_[0] if st_ else {}
                raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', bmp, '-vf', 'select=eq(n\\,0)+eq(n\\,77),scale=390:614', '-vsync', '0', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
                fb = _np2.frombuffer(raw, _np2.uint8).reshape(-1, 614, 390, 3)
                check(len(st_) == 1 and (v0.get('codec_name'), v0.get('profile'), v0.get('width'), v0.get('height'), v0.get('pix_fmt'), v0.get('r_frame_rate'), int(v0.get('nb_frames', 0))) == ('h264', 'High', 1170, 1842, 'yuv420p', '30/1', 78)
                      and len(fb) == 2 and int(fb[0].max()) <= 24 and float(fb[0].mean()) < 5 and int(fb[1].max()) <= 8 and os.path.getsize(bmp) < 4e6,
                      f'爆発の 動画：H.264 High・1170×1842（舞台 390×614 の 3倍）・30コマ/秒・78コマ（2.6秒）・音なし・はじめと さいごの コマは 真っ暗（{int(fb[0].max()) if len(fb) else "?"}・{int(fb[1].max()) if len(fb) > 1 else "?"}/255）・{os.path.getsize(bmp) / 1e6:.2f}MB')
                ps = _probe(bse); du = float(ps.get('format', {}).get('duration', 0))
                rw = subprocess.run(['ffmpeg', '-v', 'error', '-i', bse, '-f', 's16le', '-ac', '2', '-ar', '44100', '-'], capture_output=True).stdout
                ya = _np2.frombuffer(rw, _np2.int16).astype(_np2.float64) / 32768; pkd = 20 * float(_np2.log10(max(1e-9, float(_np2.abs(ya).max())))); h1 = float(_np2.sqrt(_np2.mean(ya[:44100 * 2 // 2] ** 2))); h2 = float(_np2.sqrt(_np2.mean(ya[-44100 * 2 // 2:] ** 2)))
                rd_ = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(TCA, 'tc_se_doon.m4a'), '-f', 's16le', '-ac', '2', '-ar', '44100', '-'], capture_output=True).stdout
                yd = _np2.frombuffer(rd_, _np2.int16).astype(_np2.float64) / 32768; BO2 = pg.evaluate('() => Object.assign({}, TCFX.BOOM)'); i0 = int(BO2['telop'] * 44100) * 2
                mix = _np2.zeros(max(len(ya), i0 + len(yd))); mix[:len(ya)] += ya * BO2['gain']; mix[i0:i0 + len(yd)] += yd; pkm = float(_np2.abs(mix).max())
                check(2.4 <= du <= 2.8 and -4 <= pkd <= -0.5 and h1 > 4 * h2 and pkm < 0.92 and float(_np2.abs(ya).max()) * BO2['gain'] < 0.7,
                      f'爆発の 音：{du:.2f}秒・ファイルの 山 {pkd:.1f}dB → {BO2["gain"]}倍で 鳴らす・{BO2["telop"]}秒 あとの ドーン！！と 重ねた 山は {pkm:.2f}（1 を こえない＝割れない）・はじめが 大きく だんだん 消える')
            else: print('  ⚠️ 爆発の 動画・音（ios/tc_assets）が ない')
        print('■ ルーレット（幻の馬：目は 紫に 光る）')
        pg.evaluate("() => { window.__rtDone = false; TCFX.roulette(document.querySelector('#tcOv .tcfx'), { th: 'maboroshi', a: 1600, b: 3200, win: 0, bg: 'abyss', se: TCApp._snd.se }).then(() => { window.__rtDone = true; }); }")
        pg.wait_for_timeout(2500); shot(pg, 'tc_rt_mabo')
        em = rt_eye([651.4, 286]); fm = [f for f in rt_files() if 'maboroshi' in f]
        mf, mc = em['far'], em['core']
        check(fm == [f'rt_maboroshi_{p}2.webp' for p in ('knob', 'plate', 'ptr', 'stick')] and min(mc['lo']) >= 235 and mf['lo'][2] >= 150 and mf['lo'][2] - mf['hi'][1] >= 30 and mf['lo'][0] - mf['hi'][1] >= 5 and mf['rng'] >= 25 and mf['step'] <= 45 and em['out']['rng'] <= 8,
              f'幻の馬の 目：明るい 光の 玉（{mc["lo"]}）・まわりの 光は **紫**（{mf["lo"]}〜{mf["hi"]}）・ゆっくり 息を する（明るさの 幅 {mf["rng"]}・0.1秒の 変わり方 {mf["step"]}/255 まで）・新しい 絵 4まい（{fm}）')
        pg.evaluate(PC_WATCH); pg.evaluate(SES)
        pg.mouse.click(300, 600); pg.wait_for_timeout(5600)
        pg.mouse.click(200, 400)
        pg.wait_for_function("() => window.__rtDone", timeout=20000)
        check(True, '幻の馬の ルーレットも タップで 回って とじた')
        lg = pg.evaluate("() => window.__pcLog.slice()"); sx = pg.evaluate(SES); ix = lambda n: sx.index(n) if n in sx else -1
        check(not [x for x in lg if x['k'] in ('in', 'out')] and 0 <= ix('rt_stop') < ix('sfx_big×0.5') and 'sfx_sdp×0.85' not in sx and 'rt_confirm' not in sx,
              f'安い 方（1600P）：プチュンは なし・ポイントが 出る ときに デカ的中と 同じ 音（小さめ）（{[x for x in sx if not x.startswith("rt_tick")]}）')
        # ---------- 第4.168版（まさちゃん 2026/11/14 01:26 の 改善点）----------
        print('■ 第4.168版：合計ポイントの 札・ごはんの「← もどる」')
        #   5.「トレーニングセンターでも、合計ポイントが見えるようにする。一枚目の青四角のところに、合計ポイント設置して！」：作戦会議の ボタンの すぐ 下に 合計ポイントの 札（上の 帯と 同じ 数）
        pg.evaluate("() => { TCCare.S.high = 0; TCApp.state.high = 0; }"); pg.wait_for_timeout(500)
        pt = pg.evaluate("""() => { const G = TCCare.PTG, st = document.querySelector('#tcOv .tcst').getBoundingClientRect(), b = document.querySelector('#tcOv .tcpl').getBoundingClientRect(), k = st.width / 1052;
          return { show: TCCare.S.ptShow, total: TengelWallet.total(), G, btn: [(b.left - st.left) / k, (b.top - st.top) / k, (b.right - st.left) / k, (b.bottom - st.top) / k].map(Math.round) }; }""")
        Gp = pt['G']; ppx = pg.evaluate(OVPX, [[Gp['x'] + 8, Gp['y'] + Gp['h'] / 2], [Gp['x'] + Gp['w'] - 8, Gp['y'] + Gp['h'] / 2], [Gp['x'] - 24, Gp['y'] + Gp['h'] / 2], [Gp['x'] + Gp['w'] / 2, Gp['y'] + Gp['h'] + 24]])
        pg.evaluate("() => TCApp._t.give({ k: 'pt', v: 100, id: 'tc-pt-test-168' })"); pg.wait_for_timeout(800)
        pt2 = pg.evaluate("() => ({ show: TCCare.S.ptShow, total: TengelWallet.total(), bump: TCCare.S.ptBump != null })")
        check(pt['show'] == pt['total'] and pt['total'] > 0 and Gp == {'x': 771, 'y': 250, 'w': 246, 'h': 56} and pt['btn'][0] - 14 <= Gp['x'] and Gp['x'] + Gp['w'] <= pt['btn'][2] + 14 and (pt['btn'][1] + pt['btn'][3]) / 2 < Gp['y'] <= pt['btn'][3] + 12
              and ppx[0][3] >= 240 and ppx[1][3] >= 240 and ppx[2][3] < 60 and ppx[3][3] < 60,
              f'合計ポイントの 札：作戦会議の ボタン（{pt["btn"]}）の すぐ 下（{Gp["x"]}〜{Gp["x"] + Gp["w"]} × {Gp["y"]}〜{Gp["y"] + Gp["h"]}）・数は 上の 帯の ポイントと 同じ（{pt["show"]:,}P）・札の 外は すき通る')
        check(pt2['total'] == pt['total'] + 100 and pt2['show'] == pt2['total'] and pt2['bump'], f'ポイントが ふえると 札の 数も すぐ かわる（{pt["show"]:,} → {pt2["show"]:,}P・ぽんと 1回 ふくらむ）')
        #   11.「ごはんを押しちゃうと戻れないから、戻るボタンを追加して！」：えらぶ 札の 左上の「← もどる」／もう一度「ごはん」で とじる（トークンは 使わない・PUSH も 出ない）
        pg.wait_for_function("() => TCCare.S.phase === 'idle' && !TCCare.S.mode && !TCCare.S.busy && !(TCCare.S.push && TCCare.S.push.hideT == null) && !document.querySelector('#tcOv .tcfx.on')", timeout=60000)
        CH = pg.evaluate("() => TCCare.CHBACK"); CST = "() => { const S = TCCare.S; return { chooser: !!S.chooser, phase: S.phase, mode: S.mode, stock: S.stock, hold: !!TCCare._hb[1].careHold, live: !!(S.push && S.push.hideT == null) }; }"
        cb0 = pg.evaluate(CST); stage_click(pg, 327, 1494); pg.wait_for_function("() => !!TCCare.S.chooser", timeout=20000); pg.wait_for_timeout(700)
        cpx = pg.evaluate(OVPX, [[CH['x'] - 80, CH['y']], [CH['x'] + 80, CH['y']], [CH['x'] - CH['w'] / 2 - 20, CH['y']]]); cb1 = pg.evaluate(CST); shot(pg, 'tc_chooser_back')
        stage_click(pg, CH['x'], CH['y']); pg.wait_for_timeout(800); cb2 = pg.evaluate(CST)
        stage_click(pg, 327, 1494); pg.wait_for_function("() => !!TCCare.S.chooser", timeout=20000); pg.wait_for_timeout(700); stage_click(pg, 327, 1494); pg.wait_for_timeout(800); cb3 = pg.evaluate(CST)
        idle = {'chooser': False, 'phase': 'idle', 'mode': None, 'stock': cb0['stock'], 'hold': False, 'live': False}
        check(CH == {'x': 262, 'y': 1109, 'w': 200, 'h': 58} and cb1['chooser'] and cb1['phase'] == 'choose' and min(cpx[0][:3]) > 200 and min(cpx[1][:3]) > 200 and cpx[0][3] >= 240 and cb2 == idle and cb3 == idle,
              f'ごはんの えらぶ 札の 左上に「← もどる」（クリーム色の 札 {cpx[0][:3]}）→ 押すと とじる・もう一度「ごはん」を 押しても とじる（トークンは {cb0["stock"]}こ の まま・PUSH は 出ない）')
        print('■ 第4.168版：ノーマルの ルーレット（ピン・高い 方でも プチュン なし・デデーン）・ルーレットの BGM')
        #   10.「ノーマルルーレットの赤丸の所のピンの先端が隠れてる、直して！ノーマルルーレットは、高い方を当選してもプチュン演出いらないから消して！高い方が当選した場合、300Pの的中した時の音使って！」
        #   1.「ルーレットに入った時にBGMを変える。フィールドBGMは重ねない。」：ルーレットの 間は ルーレットの BGM だけ（くり返す 音は いつも 1つ）→ おわると フィールドの 音に もどる
        pg.evaluate("""() => { const P = CanvasRenderingContext2D.prototype; if (!P.__w168) { P.__w168 = 1; const d = P.drawImage; window.__ptr = {};
            P.drawImage = function (im) { try { const m = /rt_([a-z]+)_ptr2?[.]webp/.exec((im && im.src) || ''); if (m && arguments.length === 5) window.__ptr[m[1]] = [arguments[1], arguments[2], arguments[3], arguments[4]]; } catch (e) { } return d.apply(this, arguments); }; }
          const A = AudioBufferSourceNode.prototype; if (!A.__w168) { A.__w168 = 1; window.__lp = []; window.__lp0 = null; const st = A.start, sp = A.stop;      // くり返す 音（BGM・フィールドの 音）が 鳴り出した 時・止まる 時
            A.start = function () { if (this.loop) { this.__id = window.__lp.length; window.__lp.push({ on: performance.now(), off: null }); } return st.apply(this, arguments); };
            A.stop = function (when) { if (this.loop) { const off = performance.now() + Math.max(0, (when || 0) - this.context.currentTime) * 1000; if (this.__id != null) window.__lp[this.__id].off = off; else window.__lp0 = off; } return sp.apply(this, arguments); }; }
          window.__loops = () => { const n = performance.now(); return (window.__lp0 == null || window.__lp0 > n ? 1 : 0) + window.__lp.filter(q => q.on <= n && (q.off == null || q.off > n)).length; };
          const S = TCApp._snd; window.__bl = []; let last = null; clearInterval(window.__blT);
          window.__blT = setInterval(() => { const k = (S.bed || '-') + '|' + (S.hold == null ? 'null' : S.hold); if (k !== last) { last = k; window.__bl.push(k); } }, 25); }""")
        pg.wait_for_timeout(2400); fld = pg.evaluate("() => TCApp._t.fieldName()")
        BD = "() => [TCApp._snd.bed, TCApp._snd.hold, window.__loops()]"
        bd0 = pg.evaluate(BD); acs = pg.evaluate("() => TCApp._snd.ac ? TCApp._snd.ac.state : null")
        rgeo = pg.evaluate("async () => { const g = await (await fetch('tc_rt_geom.json')).json(); return { normal: g.normal.parts.ptr, maboroshi: g.maboroshi.parts.ptr }; }")
        pg.evaluate(SE_WRAP); pg.evaluate(PC_WATCH); pg.evaluate(SES); w1 = pg.evaluate("() => TengelWallet.total()")
        pg.evaluate("() => { window.__opDone = false; TCApp._t.onPrize({ k: 'rt', tier: 'normal', win: 1, id: 'tc-rt-test-168' }).then(() => { window.__opDone = true; }); }")
        pg.wait_for_function("() => document.querySelector('#tcOv .tcfx.on')", timeout=20000); pg.wait_for_timeout(2500); shot(pg, 'tc_rt_normal')
        bd1 = pg.evaluate(BD); fnn = [f for f in rt_files() if 'normal' in f]; ptr = pg.evaluate("() => window.__ptr.normal")
        Pn = rgeo['normal']; want_ptr = [Pn['x'] + Pn['w'] / 2 - Pn['w'] * 1.2 / 2, Pn['y'], Pn['w'] * 1.2, Pn['h'] * 1.2]
        check(fnn == [f'rt_normal_{q}2.webp' for q in ('knob', 'plate', 'ptr', 'stick')] and ptr is not None and all(abs(ptr[i] - want_ptr[i]) < 0.01 for i in range(4)) and Pn == {'x': 365, 'y': 453, 'w': 129, 'h': 135},
              f'ノーマルの ピン：絵を 1.2倍で 描く（上の ふちの まん中は 同じ 所・先は 下へ {Pn["h"] * 0.2:.0f}px のびて 盤の 上に 出る：{[round(v, 1) for v in ptr] if ptr else None}）')
        pg.mouse.click(300, 600); pg.wait_for_timeout(5600); shot(pg, 'tc_rt_normal_get'); bd2 = pg.evaluate(BD)
        pg.mouse.click(200, 400)
        pg.wait_for_function("() => window.__opDone", timeout=30000); pg.wait_for_timeout(2600)
        bd3 = pg.evaluate(BD); lg = pg.evaluate("() => window.__pcLog.slice()"); sx = pg.evaluate(SES); ix = lambda n: sx.index(n) if n in sx else -1
        bl = pg.evaluate("() => { const a = window.__bl.slice(); window.__bl.length = 0; return a; }"); beds = [k.split('|')[0] for k in bl if not k.startswith('-')]; beds = [v for i, v in enumerate(beds) if i == 0 or v != beds[i - 1]]
        w2 = pg.evaluate("() => TengelWallet.total()")
        check(not [x for x in lg if x['k'] in ('in', 'out')] and 0 <= ix('rt_stop') < ix('dedeen') and 'doon' not in sx and not any(x.startswith('sfx_sdp') or x.startswith('sfx_big') for x in sx) and w2 == w1 + 1600,
              f'ノーマルの 高い 方（1,600P）：プチュンは なし・ポイントが 出る ときの 音は デデーン（お世話で 300P が 当たった ときと 同じ 音）・ドーン！！も デカ的中の 音も 鳴らない（{[x for x in sx if not x.startswith("rt_tick")]}）・ポイントは 台帳へ（+{w2 - w1:,}P）')
        check(acs == 'running' and bd0 == [fld, None, 1] and bd1 == ['roulette', 'roulette', 1] and bd2 == ['roulette', 'roulette', 1] and bd3 == [fld, None, 1] and beds == [fld, 'roulette', fld] and all(k.split('|')[1] in ('null', 'roulette') for k in bl),
              f'ルーレットの BGM：フィールドの 音（{fld}）→ ルーレットの 間は ルーレットの BGM だけ（くり返す 音は {bd1[2]}つ＝重ねない）→ おわると フィールドの 音に もどる（{beds}・くり返す 音 {bd0[2]} → {bd1[2]} → {bd3[2]}）')
        #   幻の馬の 高い 方：プチュンで ルーレットの BGM を 止める（音なし）→ ドーン！！→ おわると フィールドの 音
        pg.evaluate(PC_WATCH); pg.evaluate(SES); w3 = pg.evaluate("() => TengelWallet.total()")
        pg.evaluate("() => { window.__opDone = false; TCApp._t.onPrize({ k: 'rt', tier: 'maboroshi', win: 1, id: 'tc-rt-test-168m' }).then(() => { window.__opDone = true; }); }")
        pg.wait_for_function("() => document.querySelector('#tcOv .tcfx.on')", timeout=20000); pg.wait_for_timeout(2500); bm1 = pg.evaluate(BD); ptm = pg.evaluate("() => window.__ptr.maboroshi"); Pm = rgeo['maboroshi']
        pg.mouse.click(300, 600)
        pg.wait_for_function("() => (window.__seL || []).includes('doon')", timeout=30000); pg.wait_for_timeout(500); bm2 = pg.evaluate(BD)
        for _ in range(20):
            pg.wait_for_timeout(700)
            if pg.evaluate("() => window.__opDone"): break
            pg.mouse.click(200, 400)
        pg.wait_for_function("() => window.__opDone", timeout=30000); pg.wait_for_timeout(2600)
        bm3 = pg.evaluate(BD); lgm = pg.evaluate("() => window.__pcLog.slice()"); sm_ = pg.evaluate(SES); blm = pg.evaluate("() => window.__bl.slice()"); w4 = pg.evaluate("() => TengelWallet.total()")
        im_ = lambda n: sm_.index(n) if n in sm_ else -1; holds = [k.split('|')[1] for k in blm]; holds = [v for i, v in enumerate(holds) if i == 0 or v != holds[i - 1]]
        check(bm1 == ['roulette', 'roulette', 1] and bm2 == [None, '', 0] and bm3 == [fld, None, 1] and holds == ['roulette', '', 'null'] and 0 <= im_('rt_stop') < im_('sfx_sdp×0.85') < im_('doon') and 'dedeen' not in sm_
              and [x['k'] for x in lgm if x['k'] in ('in', 'out')][:1] == ['in'] and w4 == w3 + 3200 and ptm is not None and abs(ptm[2] - Pm['w']) < 0.01 and abs(ptm[3] - Pm['h']) < 0.01,
              f'幻の馬の 高い 方（3,200P）：プチュンで ルーレットの BGM を 止める（音なし）→ ドーン！！→ おわると フィールドの 音（{holds}）・プチュンと ドーン！！は 今までどおり・ピンは もとの 大きさ（{[round(v) for v in ptm[2:]] if ptm else None}）')
        #   第4.171版（まさちゃん 2026/11/14 17:48「神様馬のルーレット中のBGMはなしで！」）：神様馬の ルーレットの 間は BGM なし（フィールドの 音も ルーレットの BGM も 鳴らさない）→ おわると フィールドの 音
        pg.evaluate("() => { window.__bl.length = 0; }"); pg.evaluate(SES); w5 = pg.evaluate("() => TengelWallet.total()")
        pg.evaluate("() => { window.__opDone = false; TCApp._t.onPrize({ k: 'rt', tier: 'kamisama', win: 0, id: 'tc-rt-test-171k' }).then(() => { window.__opDone = true; }); }")
        pg.wait_for_function("() => document.querySelector('#tcOv .tcfx.on')", timeout=20000); pg.wait_for_timeout(2500); bk1 = pg.evaluate(BD)
        pg.mouse.click(300, 600); pg.wait_for_timeout(5600); bk2 = pg.evaluate(BD)
        for _ in range(20):
            pg.wait_for_timeout(700)
            if pg.evaluate("() => window.__opDone"): break
            pg.mouse.click(200, 400)
        pg.wait_for_function("() => window.__opDone", timeout=30000); pg.wait_for_timeout(2600)
        bk3 = pg.evaluate(BD); blk = pg.evaluate("() => window.__bl.slice()"); sk_ = pg.evaluate(SES); w6 = pg.evaluate("() => TengelWallet.total()")
        holdk = [k.split('|')[1] for k in blk]; holdk = [v for i, v in enumerate(holdk) if i == 0 or v != holdk[i - 1]]; bedk = sorted({k.split('|')[0] for k in blk})
        check(bk1 == [None, 'none', 0] and bk2 == [None, 'none', 0] and bk3 == [fld, None, 1] and holdk == ['none', 'null'] and 'roulette' not in bedk and 'rt_lever' in sk_ and 'rt_stop' in sk_ and w6 == w5 + 3200,
              f'神様馬の ルーレット：BGM なし（くり返す 音は {bk1[2]}つ：フィールドの 音も ルーレットの BGM も 鳴らさない・レバーや 止まる 音は 鳴る）→ おわると フィールドの 音に もどる（{holdk}・{bedk}）・ポイントは 台帳へ（+{w6 - w5:,}P）')
        ta_ = open(os.path.join(W, 'tc', 'tc_app.js'), encoding='utf8').read()
        check("SND.bgm(z.tier === 'kamisama' ? 'none' : 'roulette');" in ta_, 'ノーマル・幻の馬の ルーレットは いままで どおり ルーレットの BGM（上の 確かめ）・神様馬 だけ BGM なし')
        pg.evaluate("() => { clearInterval(window.__blT); }")
        print('■ チケット（2まい）')
        pg.evaluate("() => { window.__tkDone = false; TCFX.ticket(document.querySelector('#tcOv .tcfx'), { n: 2, bg: 'morning', se: TCApp._snd.se }).then(() => { window.__tkDone = true; }); }")
        pg.wait_for_timeout(2200); pg.mouse.click(200, 700); pg.wait_for_timeout(4600); shot(pg, 'tc_tk_get'); pg.mouse.click(200, 400)
        pg.wait_for_function("() => window.__tkDone", timeout=20000)
        check(True, '扉 → タップ → チケット GET → とじた')
        # 第4.159版（まさちゃん 11/12「プチュンしてから今の演出」・11:56「プチュンしたらすぐに扉が落ちてくる演出にして！」）：PUSH から 出る チケット（puchun）＝ よんだ 瞬間に プチュン（幕は キャンバスの 下）
        #   → 真っ暗に なったら（0.82秒）すぐ 扉が 落ちて くる（キャンバスが 出る）→ 扉が 着いたら 幕を 外す
        print('■ チケット（PUSH から：プチュン → すぐ 扉）')
        pg.evaluate(PC_WATCH); pg.evaluate(SES)
        pg.evaluate("() => { window.__tkDone = false; window.__tk0 = performance.now(); TCFX.ticket(document.querySelector('#tcOv .tcfx'), { n: 1, bg: 'morning', se: TCApp._snd.se, puchun: true }).then(() => { window.__tkDone = true; }); }")
        pg.wait_for_timeout(600); shot(pg, 'tc_tk_puchun'); pg.wait_for_timeout(2600); shot(pg, 'tc_tk_door')
        lg = pg.evaluate("() => window.__pcLog.map(x => Object.assign({}, x, { t: (x.t - window.__tk0) / 1000 }))"); sx = pg.evaluate(SES); ix = lambda n: sx.index(n) if n in sx else -1
        ev_ = {x['k']: x for x in lg}; order = [x['k'] for x in lg]
        check(order[:3] == ['in', 'fxon', 'out'] and ev_['in']['t'] < 0.2 and ev_['in']['under'] and not ev_['in']['fxon'] and ev_['in']['pc'] == 1 and 'fxvis' in ev_['in']['an']
              and 0.78 <= ev_['fxon']['t'] <= 1.7 and 0.4 <= ev_['out']['t'] - ev_['fxon']['t'] <= 1.6 and ev_['out']['fxon'],
              f'チケット：よんだ 瞬間に プチュン（幕は キャンバスの 下・{ev_.get("in", {}).get("t", -1):.2f}秒）→ 真っ暗に なったら すぐ 扉（{ev_.get("fxon", {}).get("t", -1):.2f}秒）→ 扉が 着いたら 幕を 外す（{ev_.get("out", {}).get("t", -1):.2f}秒）{order}')
        check(0 <= ix('sfx_sdp×0.85') < ix('tk_fall') < ix('tk_land'), f'チケットの 音：プチュン → 扉が 落ちる → 着く（{sx}）')
        pg.mouse.click(200, 700); pg.wait_for_timeout(4600); pg.mouse.click(200, 400)
        pg.wait_for_function("() => window.__tkDone", timeout=20000)
        check(pg.evaluate("() => document.querySelectorAll('#tcOv .tcpc').length") == 0 and not pg.evaluate("() => document.querySelector('#tcOv .tcfx').classList.contains('on')"), '扉 → タップ → チケット GET → とじた（幕は のこらない）')
        #   「演出を控えめにする」：光る 部品は 出さない（黒い 幕 だけ・0.4秒）・プチュンの 音も なし（的中の 演出と 同じ）
        cm = pg.evaluate("""async () => { TengelFx.set({ calm: true }); const cv = document.querySelector('#tcOv .tcfx'), n0 = window.__seL.length, t0 = performance.now(); const pc = await TCFX.puchun(cv, { se: TCApp._snd.se }); const dt = (performance.now() - t0) / 1000;
          const r = { dt, calm: pc.calm, fxs: pc.el.querySelectorAll('.fxs').length, se: window.__seL.slice(n0), bg: getComputedStyle(pc.el).backgroundColor }; await new Promise(q => setTimeout(q, 600)); r.left = document.querySelectorAll('#tcOv .tcpc').length; TengelFx.set({ calm: null }); r.back = TengelFx.calm(); return r; }""")
        check(cm['calm'] and cm['fxs'] == 0 and cm['se'] == [] and cm['bg'] == 'rgb(0, 0, 0)' and 0.35 <= cm['dt'] <= 1.3 and cm['left'] == 0 and cm['back'] is False, f'「演出を控えめにする」の とき：プチュンは 黒い 幕 だけ（{cm["dt"]:.2f}秒）・光る 部品も 音も 出さない {cm}')
        print('■ 着せ替えで チケットを 使う')
        pg.evaluate("() => { const s = TCApp.state; s.tickets = 1; localStorage.setItem('tengel.tc', JSON.stringify(s)); }")
        pg.locator('#tcOv [data-tc=back]').click(); pg.wait_for_timeout(600)
        check(pg.evaluate("() => !document.querySelector('#tcOv.on') && TCInfo.tickets() === 1 && TCInfo.total() >= 1"), 'もどる → チケット 1まい・お世話の 合計')
        # 第4.140版：チケットは 先に 1枚 使ってから 解放（解放できなければ もどす）。カギの テーマを 1枚で 解放 → チケット 0・ポイントは へらない
        pg.evaluate("() => document.querySelector('.tabbar button[data-tab=set]').click()"); pg.wait_for_timeout(500)
        lk = pg.evaluate("() => { const t = TengelKisekae.list().find(x => x.price && !x.pack && !TengelKisekae.usable(x.id)); return t ? { id: t.id, price: t.price } : null; }")
        tw0 = pg.evaluate("TengelWallet.total()")
        pg.evaluate("(id) => document.querySelector(`#setKisekae .kst[data-ks=\"${id}\"]`).click()", lk['id']); pg.wait_for_timeout(500)
        tb = pg.locator('#setKisekae [data-ksact=ticket]')
        check(tb.count() == 1 and 'のこり 1枚' in tb.inner_text(), f'カギの テーマを 押すと「チケットで解放（のこり 1枚）」が 出る（{lk}）')
        tb.click(); pg.wait_for_timeout(1500)
        tk = pg.evaluate("(id) => ({ usable: TengelKisekae.usable(id), cur: TengelKisekae.current(), tickets: TCInfo.tickets(), total: TengelWallet.total(), ev: TengelWallet.events().filter(e => e.id === 'unlock-theme:' + id).map(e => e.amount) })", lk['id'])
        check(tk['usable'] and tk['cur'] == lk['id'] and tk['tickets'] == 0 and tk['total'] == tw0 and len(tk['ev']) == 1 and tk['ev'][0] == 0, f'チケット 1枚で 解放して 着せ替えた・チケットは 0枚・ポイントは へらない（{tk}）')
        bk = pg.evaluate("() => { const a = TCInfo.tickets(); TCInfo.backTicket(); const b = TCInfo.tickets(); TCInfo.useTicket(); return [a, b, TCInfo.tickets(), TCInfo.useTicket()]; }")
        check(bk == [0, 1, 0, False], f'チケットを もどす・使う（0 → 1 → 0・ない ときは 使えない：{bk}）')
        pg.evaluate("() => TengelKisekae.apply('default')"); pg.wait_for_timeout(600)
        print('■ チケットを 7,000P に かえる（第4.141版）')
        #   11/10 15:52 まさちゃん「壁紙チケット or 8000pにして！」→ 16:08「じゃあ7000pにして！」：チケット 1枚は、壁紙の 解放に 使うか、7,000P（獲得ポイント）に かえるかを 選べる
        pg.evaluate("() => { TCInfo.backTicket(); TCInfo.backTicket(); document.dispatchEvent(new CustomEvent('tengel:tc')); }"); pg.wait_for_timeout(500)
        k0 = pg.evaluate("() => { const b = document.querySelector('#setKisekae .kstk'); return { tp: TengelPoints.TICKET_POINTS, txt: b ? b.innerText.replace(/\\s+/g, ' ') : '', btn: b ? [...b.querySelectorAll('button')].map(x => x.textContent) : [], total: TengelWallet.total(), tk: TCInfo.tickets() }; }")
        check(k0['tp'] == 7000 and '🎫 チケット 2枚' in k0['txt'] and 'カギの壁紙を1つ解放' in k0['txt'] and '7,000Pにかえる' in k0['txt'] and k0['btn'] == ['7,000Pに かえる'] and k0['tk'] == 2,
              f'着せ替えの 上に チケットの 箱：「チケット 2枚・1枚で、カギの壁紙を1つ解放か、7,000Pにかえるか、選べるよ」と「7,000Pに かえる」（{k0}）')
        pg.locator('#setKisekae [data-ksact=tkpt1]').click(); pg.wait_for_timeout(300)
        k1 = pg.evaluate("() => [...document.querySelectorAll('#setKisekae .kstk button')].map(x => x.textContent)")
        pg.locator('#setKisekae [data-ksact=tkpt0]').click(); pg.wait_for_timeout(300)
        k2 = pg.evaluate("() => [[...document.querySelectorAll('#setKisekae .kstk button')].map(x => x.textContent), TCInfo.tickets(), TengelWallet.total()]")
        check(k1 == ['1枚を 7,000Pに かえる', 'やめる'] and k2 == [['7,000Pに かえる'], 2, k0['total']], f'1回 押すと「1枚を 7,000Pに かえる」「やめる」・やめると もどる（チケットも ポイントも そのまま）（{k1}・{k2}）')
        pg.locator('#setKisekae [data-ksact=tkpt1]').click(); pg.wait_for_timeout(300); pg.locator('#setKisekae [data-ksact=tkpt2]').click(); pg.wait_for_timeout(1300)
        k3 = pg.evaluate("() => { const b = document.querySelector('#setKisekae .kstk'), ev = TengelWallet.events().filter(e => /^tkp-/.test(e.id)); return { total: TengelWallet.total(), tk: TCInfo.tickets(), toast: document.querySelector('#toast').textContent, box: b ? b.innerText.replace(/\\s+/g, ' ') : '', ev: ev.map(e => [e.kind, e.bucket, e.amount, e.what]), free: TengelWallet.balance().free }; }")
        check(k3['total'] == k0['total'] + 7000 and k3['tk'] == 1 and 'チケット 1枚を 7,000Pに かえたよ' in k3['toast'] and 'チケット のこり 1枚' in k3['toast'] and '🎫 チケット 1枚' in k3['box']
              and k3['ev'] == [['mission', 'free', 7000, 'チケットを ポイントに かえた']],
              f'チケット 1枚 → +7,000P（獲得ポイント）・チケットは 1枚 へる・箱は「チケット 1枚」（{k3}）')
        pg.locator('#setKisekae [data-ksact=tkpt1]').click(); pg.wait_for_timeout(300); pg.locator('#setKisekae [data-ksact=tkpt2]').click(); pg.wait_for_timeout(1300)
        k4 = pg.evaluate("() => ({ total: TengelWallet.total(), tk: TCInfo.tickets(), box: document.querySelectorAll('#setKisekae .kstk').length, n: TengelWallet.events().filter(e => /^tkp-/.test(e.id)).length })")
        check(k4 == {'total': k0['total'] + 14000, 'tk': 0, 'box': 0, 'n': 2}, f'もう 1枚 かえる → +7,000P・チケットが 0枚に なると 箱は 消える（{k4}）')
        print('■ アプリを 閉じても 当たりは 消えない（第4.140版）')
        #   お世話の 途中・ルーレットの 途中で アプリを 閉じた ことに する：保存に 当たり（ルーレット 1600P）が 残って いる → 開き直して トレーニングセンターを ひらくと もらえる（1回だけ）
        w0 = pg.evaluate("TengelWallet.total()")
        pg.evaluate("() => { const s = JSON.parse(localStorage.getItem('tengel.tc')); s.pend = { k: 'rt', tier: 'normal', a: 800, b: 1600, win: 1, id: 'tc-pend-test-1' }; localStorage.setItem('tengel.tc', JSON.stringify(s)); }")
        def reopen():
            pg.reload(); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(600)
            pg.locator('#tcFab').click()
            pg.wait_for_function("() => window.TCApp && document.querySelector('#tcOv.on') && !document.querySelector('#tcOv .tcld')", timeout=90000)
            pg.wait_for_timeout(1200)
            return pg.evaluate("({ total: TengelWallet.total(), pend: (JSON.parse(localStorage.getItem('tengel.tc')) || {}).pend || null, msg: document.querySelector('#tcOv .tcmsg').textContent, on: document.querySelector('#tcOv .tcmsg').classList.contains('on'), n: TengelWallet.events().filter(e => e.id === 'tc-pend-test-1').length })")
        r1 = reopen()
        check(r1['total'] == w0 + 1600 and r1['pend'] is None and '前の 当たり（1,600P）を 受け取ったよ' in r1['msg'] and r1['on'] and r1['n'] == 1, f'開き直して ひらくと 前の 当たり 1,600P を 受け取る（お知らせ つき・保存から 消える）（{r1}）')
        pg.evaluate("() => { const s = JSON.parse(localStorage.getItem('tengel.tc')); s.pend = { k: 'rt', tier: 'normal', a: 800, b: 1600, win: 1, id: 'tc-pend-test-1' }; localStorage.setItem('tengel.tc', JSON.stringify(s)); }")
        r2 = reopen()
        check(r2['total'] == w0 + 1600 and r2['pend'] is None and r2['n'] == 1, f'同じ 当たりが 保存に 残って いても 2回は 足さない（{r2["total"]}）')
        pg.evaluate("() => { const s = JSON.parse(localStorage.getItem('tengel.tc')); s.pend = { k: 'tk', n: 2, id: 'tc-pend-test-2' }; localStorage.setItem('tengel.tc', JSON.stringify(s)); }")
        r3 = reopen(); tk3 = pg.evaluate("TCInfo.tickets()")
        check(tk3 == 2 and r3['pend'] is None and 'チケット 2枚' in r3['msg'], f'チケットの 当たりも 同じ（{tk3}枚・{r3["msg"]}）')
        #   第4.159版：お世話の あと PUSH を 押す 前に アプリを 閉じた → 開き直すと また PUSH が 出る（スイッチ「まとめて 使う」も おぼえて いる）。トークンが 0 なら 出さない
        pg.evaluate("() => { const s = JSON.parse(localStorage.getItem('tengel.tc')), n = Math.max(Date.now(), +s.seen || 0); s.push = true; s.bulk = true; s.stock = 3; s.stockAt = n; s.high = 0; localStorage.setItem('tengel.tc', JSON.stringify(s)); }")
        reopen(); pg.wait_for_timeout(1500); o0 = pg.evaluate(PU); pg.evaluate(SE_WRAP)
        do = press(pg); pg.wait_for_timeout(500); o1 = pg.evaluate(PU)
        G = pg.evaluate("() => TCCare.PUSHG"); stage_click(pg, *G['end']); pg.wait_for_timeout(900); o2 = pg.evaluate(PU)
        check(o0['live'] and o0['bulk'] and o0['stock'] == 3 and o0['push'] and do == 1 and o1['stock'] == 2 and o1['saved'] == 2 and o1['live'] and not o2['live'] and not o2['spush'] and o2['stock'] == 2,
              f'PUSH を 押す 前に 閉じた → 開き直すと PUSH が また 出る（まとめて 使うも おぼえて いる）→ 押すと トークン 3 → {o1["stock"]}（PUSH は のこる）→「おわる」で 消える（保存も）')
        pg.evaluate("() => { const s = JSON.parse(localStorage.getItem('tengel.tc')), n = Math.max(Date.now(), +s.seen || 0); s.push = true; s.bulk = false; s.stock = 0; s.stockAt = n; localStorage.setItem('tengel.tc', JSON.stringify(s)); }")
        reopen(); pg.wait_for_timeout(1500); o3 = pg.evaluate(PU)
        check(not o3['live'] and not o3['push'] and o3['stock'] == 0, f'トークンが 0 の ときは PUSH を 出さない（{o3["stock"]}こ）')
        print('■ 上限の 近くで チケットを ポイントに かえる（第4.141版）')
        #   合計 96,000P で チケット 1枚（7,000P）を かえる → 財布は 上限の 99,999P まで・こえた 3,001P は あずかりポイントへ（消えない）・チケットは 1枚 へる
        k5 = pg.evaluate("""async () => { const w = TengelWallet, wait = ms => new Promise(r => setTimeout(r, ms));
          await w.grant('t-cap-fill', 96000 - w.total(), 'テスト'); document.dispatchEvent(new CustomEvent('tengel:tc')); await wait(400);
          const t0 = w.total(), h0 = w.hold().total, tk0 = TCInfo.tickets();
          document.querySelector('#setKisekae [data-ksact=tkpt1]').click(); await wait(300); document.querySelector('#setKisekae [data-ksact=tkpt2]').click(); await wait(1500);
          return { t0, tk0, total: w.total(), held: w.hold().total - h0, tk: TCInfo.tickets(), toast: document.querySelector('#toast').textContent }; }""")
        check(k5['t0'] == 96000 and k5['tk0'] == 2 and k5['total'] == 99999 and k5['held'] == 3001 and k5['tk'] == 1 and '7,000P の うち 3,001P は あずかったよ' in k5['toast'],
              f'96,000P で かえる → 財布 99,999P・3,001P は あずかり・チケット 2 → 1枚（{k5}）')
        check(not errs, f'エラー なし {errs[:3]}')
        print('■ 3倍の 画面（iPhone）・2倍の 広い 画面（iPad）での 細かさ（第4.150版）')
        for nm3, vp3, dsf3 in (('iPhone（3倍）', {'width': 390, 'height': 844}, 3), ('iPad（2倍）', {'width': 820, 'height': 1180}, 2)):
            c3 = b.new_context(viewport=vp3, device_scale_factor=dsf3, locale='ja-JP', timezone_id='Asia/Tokyo'); c3.add_init_script(FAKE)
            p3 = c3.new_page(); e3 = []; p3.on('pageerror', lambda e, e3=e3: e3.append(str(e)))
            p3.goto(APP); p3.wait_for_timeout(1500); gate(p3); p3.wait_for_timeout(600)
            p3.locator('#tcFab').click()
            p3.wait_for_function("() => window.TCApp && document.querySelector('#tcOv.on') && !document.querySelector('#tcOv .tcld')", timeout=120000)
            p3.evaluate("() => TCApp._t.govSet(0, true)"); p3.wait_for_timeout(500)
            q3 = p3.evaluate("() => { const c = document.querySelector('#tcOv .tcgl'), s = document.querySelector('#tcOv .tcst').getBoundingClientRect(); return [c.width, c.height, s.width, devicePixelRatio, TCCare.S.cs]; }")
            check(abs(q3[0] - round(q3[2] * dsf3)) <= 1 and q3[0] > 1052 and abs(q3[4] - q3[0] / 1052) < 1e-6 and not e3,
                  f'{nm3}：キャンバスの 幅 {q3[0]}px＝置き場 {q3[2]:.0f}pt × {dsf3}（前は 1052px まで）・お世話の 絵の 倍も 同じ（{q3[4]:.3f}）・エラー なし {e3[:2]}')
            if dsf3 == 3:
                # 第4.156版：夜の フィールドでも 馬は ねない（前は 夜の「とくべつ」で 60秒 ねた・第4.154版は その 起きた あとの バグを 直して いた）。
                #   アプリの 時計を 夜に して、とくべつ／見本用の sleep を させても 立った まま → 撫でるが すぐ 始まる。外から ねる 形（mode 'sleep'）を 入れても 立った まま 次へ
                wk = p3.evaluate("""async () => { const BR = TCCare._hb[1], S = TCCare.S, out = [], gh = Date.prototype.getHours; Date.prototype.getHours = function () { return 23; };
                  try { await new Promise(r => setTimeout(r, 400)); const tod = BR.tod;
                    for (const f of ['special', 'sleep:3', 'x']) { const n0 = BR.n; BR.careHold = false;
                      if (f === 'x') Object.assign(BR, { mode: 'sleep', until: S.lastT + 600, sl: 0 }); else { BR.force = [f]; BR.mode = 'idle'; BR.until = S.lastT - 1; }
                      const w0 = performance.now(); let lay = 0; const m = new Set();
                      while ((BR.n === n0 || performance.now() - w0 < 1500) && performance.now() - w0 < 30000) { await new Promise(r => setTimeout(r, 50)); if (performance.now() - w0 > 120) m.add(BR.mode); lay = Math.max(lay, BR.sl || 0, BR.rise || 0, BR.sleep || 0, BR.doze || 0); }
                      out.push([f, [...m].sort().join('/'), lay, BR.n > n0]); }
                    S.coolUntil = -1e9; TCCare.press(S.lastT, 'pet'); await new Promise(r => setTimeout(r, 300));
                    return { tod, out, pet: S.mode }; } finally { Date.prototype.getHours = gh; } }""")
                check(wk['tod'] == 'night' and all('sleep' not in o[1] and o[2] == 0 and o[3] for o in wk['out']) and wk['pet'] == 'pet',
                      f'夜の フィールドでも ねない：とくべつ・見本用の sleep・外から 入れた ねる 形 → 立った まま 次の 動きへ・横に なる しるしは 0 → 撫でるが 始まる {wk["out"]}')
            c3.close()
        print('■ 神様馬・幻の馬の 形の 直し（第4.161版）')
        #   まさちゃん 11/12 18:00「トレーニングセンターの神様馬、赤丸の位置から動く変なパーツが飛び出てる／幻の馬は、赤丸の立髪の毛の色がブラックなっている。
        #   身体の表面の赤丸の箇所がボヤけているように見える。全て改善して！」・19:47「幻の馬、肩幅狭くして！」・20:01「赤丸の大きさにして！」
        #   形の 中身（骨の 付け先・はば・にじむ 膜）は test_horse_fix.py が 数で 見る。ここは アプリが 新しい 形を 読んで、本当に 描いた 絵が 直って いるかを 見る
        c4 = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo'); c4.add_init_script(FAKE); c4.add_init_script(HOOK161)
        p4 = c4.new_page(); e4 = []; p4.on('pageerror', lambda e: e4.append(str(e)))
        got4 = []; p4.on('response', lambda r: got4.append(r.url.split('/')[-1].split('?')[0]) if 'tc_horse_bk_kamisama' in r.url or 'tc_horse_bk_maboroshi' in r.url else None)
        p4.goto(APP); p4.wait_for_timeout(1500); gate(p4); p4.wait_for_timeout(600)
        p4.locator('#tcFab').click()
        p4.wait_for_function("() => window.TCApp && document.querySelector('#tcOv.on') && !document.querySelector('#tcOv .tcld')", timeout=120000)
        p4.evaluate("() => TCApp._t.govSet(0, true)"); p4.wait_for_timeout(1200)
        HI = "() => { const h = window.__HO, m = h.meta, b = window.__BR; return { v: m.v, fix: m.fix || null, slim: m.slim || null, skin: m.skinfix2 || null, fx: !!h.B.fx, err: h.gl.getError(), stage: h.opt.stage, stance: h.opt.stance ? 1 : 0, stand: !!(b && b.stand) }; }"
        n4 = p4.evaluate(HI)
        check(n4['v'] < 40000 and n4['fix'] is None and n4['slim'] is None and n4['skin'] is None and not n4['fx'] and n4['err'] == 0,
              f'いつもの 馬：直しの 印は ない（前と 同じ 描き方）・描く ときの エラー なし（頂点 {n4["v"]}）')
        # 第4.168版（まさちゃん 2026/11/14 01:26「幻の馬と神様馬の大きさを、いつもの馬と同じ大きさに合わせる。※足の形、動き方も全て一緒にして！あくまで、外見が違うだけにして！」）：
        #   大きさ＝いつもの 馬の いまの 大きさ（お世話 0回＝0.6倍・260回＝1.0倍。前は いつも 1.7倍）・神様馬の 立ち方を 広げない・立った ままに しない（歩く・走る・うんちも 同じ）
        s4 = {}
        for kind4 in ('maboroshi', 'kamisama'):
            p4.evaluate("(k) => TCApp._t.startVisit(k)", kind4)
            p4.wait_for_function("(k) => TCApp.state.visit && TCApp.state.visit.kind === k && window.__HO && window.__HO.meta.v > 80000", arg=kind4, timeout=120000); p4.wait_for_timeout(600)
            s4[kind4] = p4.evaluate(HI)
        p4.evaluate("() => { TCApp.state.cares = 260; }")      # いちばん 大きい とき（1.0倍）で 形の 直しを はかる（前は 1.7倍で はかって いた ＝ 画素の 数は 約 1/3）
        r4 = {}
        for kind4 in ('maboroshi', 'kamisama'):
            p4.evaluate("(k) => TCApp._t.startVisit(k)", kind4)
            p4.wait_for_function("(k) => TCApp.state.visit && TCApp.state.visit.kind === k && window.__HO && window.__HO.meta.v > 80000 && window.__HO.opt.stage === 1", arg=kind4, timeout=120000); p4.wait_for_timeout(2500)
            r4[kind4] = p4.evaluate(HI)
            r4[kind4]['m'] = [p4.evaluate("(deg) => window.__tcMetric(deg)", deg4) for deg4 in (180, 0)]
        mb, km = r4['maboroshi'], r4['kamisama']
        check(n4['stage'] == 0.6 and all(s4[k]['stage'] == 0.6 and s4[k]['stance'] == 0 and not s4[k]['stand'] for k in s4) and all(r4[k]['stage'] == 1 and r4[k]['stance'] == 0 and not r4[k]['stand'] for k in r4),
              f'第4.168版：幻の馬・神様馬の 大きさは いつもの 馬と 同じ（お世話 0回＝{n4["stage"]}倍：{[s4[k]["stage"] for k in s4]}／260回＝1倍：{[r4[k]["stage"] for k in r4]}。前は いつも 1.7倍）・神様馬の 立ち方は 形の まま・立った ままに しない')
        check(sorted(set(got4)) == ['tc_horse_bk_kamisama2.bin', 'tc_horse_bk_kamisama2.json', 'tc_horse_bk_maboroshi2.bin', 'tc_horse_bk_maboroshi2.json'],
              f'アプリが 読むのは 直した 形 だけ（{sorted(set(got4))}）')
        check(mb['fix'] is not None and mb['fix'].get('two') == 1 and mb['fix'].get('nfix') == 1 and mb['fx'] and mb['slim'] is not None and mb['slim']['w'] == [0.779, 0.62] and mb['err'] == 0,
              f'幻の馬：直しの 印（裏返しの 面・こわれた 法線・にじむ 膜の 色）と はば（{mb["slim"] and mb["slim"]["w"]}）・エラー なし')
        a4, z4 = mb['m']
        #   390×614 の 絵で：直しを 切ると たてがみの 中の 黒い 所が 400画素 ほど（8回 はかって 398〜436）・時刻と 動きを 止めて いるので 同じ 絵 どうしの 差は 0。
        #   反対の 向き：三角の 向きだけ 逆で 法線は 合って いる 面まで 向きを かえると 74画素が 黒く なった（はじめの 作り）→ 法線が むこう向きの 面 だけ 直す 形に して 0
        #   第4.168版：大きさが 1.7倍 → 1.0倍 ＝ 画素の 数は 約 (1/1.7)²（400 → 140 ほど：手元で 140）
        check(a4['fix']['toPur'] >= 80 and a4['fix']['toDark'] <= 10 and a4['same']['toPur'] <= 10 and a4['same']['toDark'] <= 10 and a4['err'] == 0,
              f'幻の馬（たてがみの 見える 向き）：黒かった たてがみの 中が 紫に（{a4["fix"]["toPur"]}画素：80 以上）・紫が 黒く なった 所は ない（{a4["fix"]["toDark"]}）・同じ 絵 どうしの 差は {a4["same"]["toPur"]}・{a4["same"]["toDark"]}')
        check(z4['fix']['toPur'] <= 10 and z4['fix']['toDark'] <= 10 and z4['same']['toPur'] <= 10 and z4['same']['toDark'] <= 10 and z4['err'] == 0,
              f'幻の馬（反対の 向き）：直しで 黒く なる 所は ない（紫 → 黒 {z4["fix"]["toDark"]}画素・黒 → 紫 {z4["fix"]["toPur"]}：裏から 見えて 法線が むこう向きの 面 だけ 直す）')
        check(km['fix'] is None and not km['fx'] and km['skin'] is not None and km['skin'].get('islands') == 9 and km['skin'].get('verts') == 983 and km['err'] == 0
              and all(m4['fix']['toPur'] == 0 and m4['fix']['toDark'] == 0 and m4['err'] == 0 for m4 in km['m']),
              f'神様馬：骨の 付け直し（{km["skin"] and [km["skin"].get("islands"), km["skin"].get("verts")]}＝はなれた かたまり 9・頂点 983）だけ・見た目の 直しは 使わない（前と 同じ 描き方）・エラー なし')
        check(not e4, f'エラー なし {e4[:2]}')
        c4.close()
        b.close()
finally:
    srv.terminate()
print('NG' if fails else 'OK', len(fails), fails)
sys.exit(1 if fails else 0)
