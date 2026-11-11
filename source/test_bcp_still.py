# 結果ボードカスタム（第4.150版・まさちゃん 2026/11/11 02:36「結果カスタムボードの動き全部無くして！ボードを持つ馬も含めて！その代わり、画質あげて！」）：動かない・絵は もとの 画質
#   python3 test_bcp_still.py   （ios/bcp_assets/ が ある とき だけ。ない とき（CI）は「絵が ない」と 出して おわる）
#   （第4.145版〜第4.149版の test_bcp_parts.py＝部品を 重ねて 動かす 出し方の テスト の かわり）
#   ・アプリに 入れる 絵：見本 14＋止まった 絵 59＋前の 絵 35＝108まい だけ（動く 絵の 部品は 入れない）・軽い 版（ios/lite）も もとと 同じ 中身（軽く しない）・止まった 絵は 1170×2532
#   ・59段 × 控えめ／通常：止まった 絵（と 前の 絵）だけで 出る・いつも 止まった 形（.bcst）・キャラの 入れもの／光と 雲／動きの CSS は ない・絵に 動きが ついて いない・
#     絵は ボードが 出はじめる 前には 見えない
#   ・結果の 字（見出し・行）と「とじる」が 出おわった あとの 画面は 1秒 たっても 1点も かわらない（通常の 演出でも）・ボードを持つ馬（15）も 止まった まま
#   ・画質：3倍の 画面で、絵は もとの 絵（ios/bcp_assets の WebP）と 同じ 画素（ボードと「とじる」と 前の 絵の 所を のぞく）
#   ・絵が おそい：読める まで 絵を 出さない（背景 だけ 先に 出ない・ほかの 絵も かくさない）→ そろったら いっしょに 出る
#   ・背景の 絵が 読めない → いつもの ボード／前の 絵 だけ 読めない → 背景 だけで 出る／いつまでも こない → 8秒で いつもの ボード
#   ・読んで いる 間に とじる・つぎつぎ 出して とじる（40回）→ エラーなし・のこり物なし
import hashlib, io, os, random, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
sys.path.insert(0, os.path.join(W, 'kisekae', 'bcp')); import bcp_app as _bcp
from assets_dir import adir, master
BCP_DIR = adir('bcp_assets')   # アプリに 入れる フォルダ（軽い 版 ios/lite/… が あれば そちら：assets_dir.py）
if not all(os.path.exists(os.path.join(BCP_DIR, f)) for f in _bcp.files()):
    print('※ 結果ボードカスタムの 絵（ios/bcp_assets）が ない ので、この テストは しない'); print('結果： OK'); sys.exit(0)
SRV = os.path.join(W, 'srv_bcpp'); PORT = 8796
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, HIST='hist_280.json', DROP='', TARGET='app'))
pth = os.path.join(SRV, 'APP', 'index.html'); html = open(pth, encoding='utf8').read()
assert "window.__NATIVE = location.protocol === 'tengel:';" in html
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
for f in _bcp.files(): shutil.copy(os.path.join(BCP_DIR, f), os.path.join(SRV, 'APP', f))
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
SPEC = {'r': 9, 'n': 14, 'ranks': {str(i): i for i in range(1, 15)},
        'rows': [{'t': '3連単', 'state': '的中', 'hits': [[11, 8, 2]], 'n': 18}, {'t': '馬単', 'state': '的中', 'hits': [[11, 8]], 'n': 9}, {'t': 'ワイド', 'state': '不的中', 'hits': [], 'n': 6}]}
MISS = dict(SPEC, rows=[dict(x, state='不的中', hits=[]) for x in SPEC['rows']])
STAGES = [(iid, kind, n, name) for iid, kind, st in _bcp.ITEMS for n, name in st]          # 59段
BG = lambda nm: _bcp.pics(nm)[0]          # 背景の 絵の 名前（第4.153版：出世馬の ほかは ボードの 中を ぬり直した 絵 bcp_<名前>_bl.webp）
BY = {name: (iid, kind, n) for iid, kind, n, name in STAGES}
MOVING = {f for n in _bcp.MOTION for f in _bcp.motion_files(n)}                            # 動く 絵の 部品（もう アプリに 入れない）
STATE = """() => { const hb = document.querySelector('#fxOv .hb'), ov = hb && hb.parentNode, w = hb && hb.querySelector('.bcpw');
  if (!hb) return null;
  if (!w) return { w: 0, pic: hb.classList.contains('bcpic'), name: hb.dataset.bcp || '', rb: !!hb.querySelector('.rb'), bcp: !!hb.querySelector('.rb.bcp') };
  const ims = [...w.querySelectorAll('img')], bg = w.querySelector('.bcpbg');
  return { w: 1, pic: hb.classList.contains('bcpic'), done: ov.classList.contains('bcpdone'), ld: w.classList.contains('bcpld'), vis: bg ? getComputedStyle(bg).visibility : '',
    ok: ims.length > 0 && ims.every(i => i.complete && i.naturalWidth > 0), go: w.classList.contains('chrgo'), mo: w.dataset.mo || '', chr: w.querySelectorAll('.chrw, .chroc, .chrot').length,
    an: w.getAnimations().length + ims.reduce((n, i) => n + i.getAnimations().length, 0), sync: ims.every(i => i.decoding === 'sync'), nat: bg ? [bg.naturalWidth, bg.naturalHeight] : null,
    cv: document.querySelectorAll('canvas.chramb').length, css: document.querySelectorAll('style.bcmCss').length, op: getComputedStyle(w).opacity,
    srcs: ims.map(i => (i.getAttribute('src') || '').split('/').pop()), name: hb.dataset.bcp || '', st: hb.classList.contains('bcst'), rb: !!w.querySelector('.rb.bcp') }; }"""
# コマごとに 見る：ボードが 出はじめる 前（.bcpon が つく 前）に 絵が 見えた コマ・絵が 出る 前に ほかの 絵を かくした コマ が ない こと
PROBE = """() => { const P = window.__probe = { on: true, n: 0, early: 0, hide: 0, first: -1, t0: performance.now() };
  const seen = e => { let o = 1; for (let x = e; x && x.nodeType === 1; x = x.parentElement) { const c = getComputedStyle(x); if (c.visibility === 'hidden' || c.display === 'none') return false; o *= +c.opacity; } return o > 0.02; };
  (function tick() { if (!P.on) return; const hb = document.querySelector('#fxOv .hb'), w = hb && hb.querySelector('.bcpw');
    if (w) { P.n++; const bg = w.querySelector('.bcpbg'), ld = w.classList.contains('bcpld'), vis = bg && bg.complete && bg.naturalWidth > 0 && seen(bg);
      if (vis && !hb.classList.contains('bcpon')) P.early++;
      if (ld && hb.parentNode.classList.contains('bcpdone')) P.hide++;
      if (vis && P.first < 0) P.first = Math.round(performance.now() - P.t0); }
    requestAnimationFrame(tick); })(); }"""
PROBE_END = "() => { const P = window.__probe; P.on = false; return { n: P.n, early: P.early, hide: P.hide, first: P.first }; }"
fails = []


def check(ok, msg):
    print(('  ✅ ' if ok else '  ❌ ') + msg, flush=True)
    if not ok: fails.append(msg)


# ---- 0) アプリに 入れる 絵 ----
from PIL import Image
import numpy as np
fl = _bcp.files(); MD = master('bcp_assets')
sha = lambda p_: hashlib.sha1(open(p_, 'rb').read()).hexdigest()
same = all(os.path.exists(os.path.join(MD, f)) and sha(os.path.join(MD, f)) == sha(os.path.join(BCP_DIR, f)) for f in fl)
sizes = {Image.open(os.path.join(BCP_DIR, BG(nm))).size for _i, _k, _n, nm in STAGES}
fgs = [f for f in fl if f.endswith('_fg.webp')]
fg_ok = all(Image.open(os.path.join(BCP_DIR, f)).mode == 'RGBA' and Image.open(os.path.join(BCP_DIR, f)).size == (1170, 2532) for f in fgs)
tot = sum(os.path.getsize(os.path.join(BCP_DIR, f)) for f in fl)
check(len(fl) == len(set(fl)) == 108 and sum(1 for f in fl if f.startswith('bcp_t_')) == 14 and all(BG(nm) in fl for _i, _k, _n, nm in STAGES) and sum(1 for f in fl if f.endswith('_bl.webp')) == 52 and not any(f'bcp_{nm}.webp' in fl for _i, _k, _n, nm in STAGES if _bcp.blank(nm)) and len(fgs) == 35 and not (set(fl) & MOVING) and len(MOVING) > 300
      and _bcp.stills_out() == [] and all('mo' not in d for d in _bcp.data()['d'].values()) and same and sizes == {(1170, 2532)} and fg_ok,
      f'アプリに 入れる 絵は 108まい（見本 14・止まった 絵 59〈ボードの 中を ぬり直した 絵 52・出世馬の 3D の 絵 7〉・前の 絵 35：{tot / 1e6:.2f}MB）・動く 絵の 部品（{len(MOVING)}まい）と 動きの データは 入れない・'
      f'中身は もとの 絵（ios/bcp_assets）と 同じ＝軽く して いない・止まった 絵と 前の 絵は 1170×2532（{sizes}）')

try:
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])

        def page(dpr=1):
            ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=dpr, locale='ja-JP', timezone_id='Asia/Tokyo', reduced_motion='no-preference')
            pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
            bad = []; pg.on('response', lambda r: bad.append(r.url.split('/')[-1]) if r.status >= 400 and '/bcp_' in r.url else None)
            req = []; pg.on('request', lambda r: req.append(r.url.split('/')[-1]) if '/bcp_' in r.url else None)
            pg.goto(f'http://localhost:{PORT}/APP/'); pg.wait_for_timeout(1500)
            if pg.locator('#gateGo').count(): pg.click('#gateGo'); pg.wait_for_timeout(600)
            pg.evaluate('() => document.fonts.ready'); pg.wait_for_timeout(300)
            return ctx, pg, errs, bad, req

        def show(pg, name, calm=False, item=None):
            iid, kind, n = BY[name] if name in BY else (item, name, 1)
            pg.evaluate("(c) => TengelFx.set({ calm: c })", calm)
            pg.evaluate("([s, k, id, n]) => TengelFx.preview(s, k, { item: id, streak: n })", [MISS if kind == 'miss' else SPEC, 'miss' if kind == 'miss' else 'hit', iid, n])

        def ready(pg, tmo=60):
            s = None
            for _ in range(tmo):
                pg.wait_for_timeout(100); s = pg.evaluate(STATE)
                if s and s.get('w') and s['pic'] and s['done'] and not s['ld'] and s['ok']: return s
            return s

        def close(pg):
            pg.evaluate('TengelFx.close()'); pg.wait_for_timeout(200)

        def snap(pg):
            return np.asarray(Image.open(io.BytesIO(pg.screenshot(clip={'x': 0, 'y': 0, 'width': 390, 'height': 844}))).convert('RGB')).astype(np.int16)

        # ---- 1) 59段 ぜんぶ（控えめ と 通常）----
        ctx, pg, errs, bad, req = page()
        t0 = time.time(); ng = []
        for iid, kind, n, name in STAGES:
            for calm in (True, False):
                pg.evaluate(PROBE); show(pg, name, calm); s = ready(pg); pr = pg.evaluate(PROBE_END)
                ok = bool(s) and s.get('w') == 1 and s['name'] == name and s['pic'] and s['done'] and not s['ld'] and s['vis'] == 'visible' and s['ok'] and s['sync'] and s['rb'] and s['st'] is True
                ok = ok and s['srcs'] == _bcp.stage_files(name) and s['srcs'][0] == BG(name) and s['nat'] == [1170, 2532] and s['op'] == '1'
                ok = ok and s['chr'] == 0 and s['cv'] == 0 and s['css'] == 0 and not s['go'] and s['mo'] == '' and s['an'] == 0
                ok = ok and pr['early'] == 0 and pr['hide'] == 0 and pr['first'] >= 0
                if not ok: ng.append((name, 'calm' if calm else 'go', s and {k: v for k, v in s.items() if k != 'srcs'}, pr))
                close(pg)
        check(not ng and not errs and not bad and not (set(req) & MOVING) and set(req) <= set(fl),
              f'59段 × 控えめ／通常：止まった 絵（と 前の 絵）だけで 出る・いつも 止まった 形（.bcst）・キャラの 入れもの／光と 雲／動きの CSS は ない・絵に 動きが ついて いない・'
              f'ボードが 出はじめる 前には 絵が 見えない・エラーなし（{time.time() - t0:.0f}秒・読んだ 絵 {len(set(req))}こ・だめ {ng[:3]}・{errs[:2]}・{bad[:3]}）')

        # ---- 2) 出た あとの 画面は かわらない（通常の 演出・1秒 おいて 2まい）：絵の ボード 8こ と ボードを持つ馬 ----
        #   結果の 字（見出し・行）と「とじる」が 順に 出るのは いつもの ボードと 同じ（結果ボードカスタムの 動きでは ない）。それが おわった あと、画面は 1点も 動かない
        res2 = []
        for name in ('ring1', 'toast2', 'race3', 'trophy4', 'carry2', 'bouquet3', 'miss1', 'miss4_3'):
            show(pg, name, False); ready(pg); pg.wait_for_timeout(2400); a = snap(pg); pg.wait_for_timeout(1100); c = snap(pg); close(pg)      # 2.4秒：見出し・行・「とじる」が 出おわる（いつもの ボードと 同じ 出方）
            res2.append((name, int(np.abs(a - c).max())))
        TF = "() => [...document.querySelectorAll('#fxOv .hb .bcx, #fxOv .hb .rb')].map(e => getComputedStyle(e).transform + '|' + getComputedStyle(e).opacity).join(';')"
        for kind in ('hit', 'miss'):      # 15：ボードを持つ馬（絵は 置いて いない ので SVG の 馬）。前は 出おわって 1.5秒後に ボードを 落としそうに なった。うしろの 演出の 光は 動く ので、馬の 部品と ボードの 形で くらべる
            show(pg, kind, False, item='carry'); pg.wait_for_timeout(3200); a = pg.evaluate(TF)
            hb = pg.evaluate("() => { const hb = document.querySelector('#fxOv .hb'); return hb ? [hb.dataset.bcx || '', hb.classList.contains('bcst'), hb.classList.contains('bce-carry'), [...hb.querySelectorAll('.bcx')].reduce((n, e) => n + e.getAnimations({ subtree: true }).length, 0), getComputedStyle(hb.querySelector('.rb')).animationName, hb.querySelectorAll('.bcx').length] : null; }")
            pg.wait_for_timeout(1600); c = pg.evaluate(TF); close(pg)
            res2.append(('carry:' + kind, 0 if a == c and len(a) > 20 else 1, hb))
        check(all(r[1] == 0 for r in res2) and all(r[2][:5] == ['carry', True, False, 0, 'none'] and r[2][5] >= 4 for r in res2[-2:]) and not errs,
              f'出た あとの 画面は 1秒 たっても 1点も かわらない（通常の 演出でも 動かない）・ボードを持つ馬も 止まった まま（下から 出ない・部品に 動きなし・形が かわらない）（{res2}）')
        ctx.close()

        # ---- 3) 画質：3倍の 画面で、絵は もとの 絵と 同じ 画素（ボード・「とじる」・前の 絵の 所を のぞく）----
        ctx, pg, errs3, bad, req = page(3)
        res3 = []
        for name in ('ring2', 'selfie1', 'stamp3', 'miss2_2', 'shusse8_3d'):
            show(pg, name, False); ready(pg); pg.wait_for_timeout(2400); shot = snap(pg)
            box = pg.evaluate("() => { const r = e => { const b = e.getBoundingClientRect(); return [b.left, b.top, b.right, b.bottom]; }; return { rb: r(document.querySelector('#fxOv .hb .rb')), close: r(document.querySelector('#fxOv .close')) }; }")
            close(pg)
            src = np.asarray(Image.open(os.path.join(MD, BG(name))).convert('RGB')).astype(np.int16)
            keep = np.ones(src.shape[:2], bool)
            for (x0, y0, x1, y1), m in ((box['rb'], 12), (box['close'], 132)):      # 「とじる」は まわりの 光（box-shadow：出世馬 など）も のぞく
                keep[max(0, int(y0 * 3) - m):int(y1 * 3) + m, max(0, int(x0 * 3) - m):int(x1 * 3) + m] = False
            fgp = os.path.join(MD, f'bcp_{name}_fg.webp')
            if os.path.exists(fgp) and _bcp.cfg(name).get('fg'): keep &= np.asarray(Image.open(fgp).convert('RGBA'))[..., 3] == 0
            d = np.abs(shot - src).max(-1)
            res3.append((name, shot.shape[:2] == src.shape[:2], int(d[keep].max()), round(float(keep.mean()), 2)))
        check(all(ok and mx <= 2 and part > 0.25 for _n, ok, mx, part in res3) and not errs3,
              f'画質：3倍の 画面（1170×2532）で、出た 絵は もとの 絵と 同じ 画素（色の 差 2 まで・くらべた 所は 画面の {min(r[3] for r in res3) * 100:.0f}% 以上）（{res3}）')
        ctx.close()

        # ---- 4) 絵が おそい（背景を 1.2秒 おくらせる）：読める まで 出さない → そろったら いっしょに 出る ----
        ctx, pg, errs, bad, req = page()
        late = BG('miss1'); held = []
        pg.route('**/' + late, lambda route: held.append(route))
        pg.evaluate(PROBE); show(pg, 'miss1', False); pg.wait_for_timeout(1200)
        s1 = pg.evaluate(STATE)
        for r in held: r.continue_()
        s2 = ready(pg); pr = pg.evaluate(PROBE_END)
        check(len(held) >= 1 and s1 and s1['w'] == 1 and s1['pic'] and s1['ld'] and s1['vis'] == 'hidden' and not s1['done'] and s1['rb']
              and s2 and not s2['ld'] and s2['vis'] == 'visible' and s2['done'] and s2['ok'] and pr['hide'] == 0 and pr['early'] == 0 and pr['first'] >= 1100 and not errs,
              f'絵が おそい：読める まで 絵を 出さない（前の 絵 だけ 先に 出ない・ほかの 絵も かくさない・字の ボードは 出て いる）→ そろったら いっしょに 出る'
              f'（待つ 間 {s1 and {k: s1[k] for k in ("ld", "vis", "done")}}・出た あと {s2 and {k: s2[k] for k in ("ld", "vis", "done")}}・絵が 見えた のは {pr["first"]}ms）')
        close(pg); pg.unroute('**/' + late)

        # ---- 5) 読めない：背景 → いつもの ボード／前の 絵 だけ → 背景 だけで 出る／いつまでも こない → 8秒で いつもの ボード ----
        pg.route('**/' + BG('miss2'), lambda route: route.fulfill(status=404, body=''))
        show(pg, 'miss2', False); pg.wait_for_timeout(1500); s_bg = pg.evaluate(STATE); close(pg); pg.unroute('**/' + BG('miss2'))
        fgn = next(nm for _i, _k, _n, nm in STAGES if _bcp.cfg(nm).get('fg'))
        pg.route(f'**/bcp_{fgn}_fg.webp', lambda route: route.fulfill(status=404, body=''))
        show(pg, fgn, False); s_fg = ready(pg); close(pg); pg.unroute(f'**/bcp_{fgn}_fg.webp')
        check(s_bg and s_bg['w'] == 0 and not s_bg['pic'] and s_bg['name'] == '' and s_bg['rb'] and not s_bg['bcp']
              and s_fg and s_fg['w'] == 1 and s_fg['pic'] and s_fg['done'] and not s_fg['ld'] and s_fg['srcs'] == [BG(fgn)] and not errs,
              f'背景の 絵が 読めない → いつもの ボードに もどる／前の 絵 だけ 読めない（{fgn}）→ 背景 だけで 出る（{s_bg}・{s_fg and s_fg["srcs"]}）')
        held4 = []
        pg.route('**/' + BG('miss4'), lambda route: held4.append(route))
        show(pg, 'miss4', False); pg.wait_for_timeout(6500); s1 = pg.evaluate(STATE); pg.wait_for_timeout(2300); s2 = pg.evaluate(STATE)
        for r in held4:
            try: r.continue_()
            except Exception: pass
        pg.wait_for_timeout(800); s3 = pg.evaluate(STATE)
        check(len(held4) >= 1 and s1 and s1['w'] == 1 and s1['ld'] and s1['vis'] == 'hidden' and not s1['done'] and s2 and s2['w'] == 0 and not s2['pic'] and s2['rb'] and not s2['bcp']
              and s3 and s3['w'] == 0 and not s3['pic'] and not errs,
              f'絵が いつまでも こない：6.5秒は 待つ → 8秒で いつもの ボード → あとから 届いても そのまま（{s1 and {k: s1[k] for k in ("ld", "vis", "done")}} → {s2} → {s3}）')
        close(pg); pg.unroute('**/' + BG('miss4'))

        # ---- 6) 読んで いる 間に とじる → エラーなし・つぎは ふつうに 出る ----
        held5 = []
        pg.route('**/' + BG('miss5'), lambda route: held5.append(route))
        show(pg, 'miss5', False); pg.wait_for_timeout(400); s1 = pg.evaluate(STATE); close(pg)
        gone = pg.evaluate("() => !document.getElementById('fxOv')")
        for r in held5:
            try: r.continue_()
            except Exception: pass      # とじた ときに 読むのを やめて いる ことも ある
        pg.wait_for_timeout(600); pg.unroute('**/' + BG('miss5'))
        show(pg, 'miss5', False); s2 = ready(pg); close(pg)
        pg.wait_for_timeout(8200)      # 前の 待つ 時計（8秒）が あとで 何か こわさない
        show(pg, 'miss5_2', True); s3 = ready(pg)
        check(s1 and s1['ld'] and gone and s2 and not s2['ld'] and s2['done'] and s3 and not s3['ld'] and s3['pic'] and s3['name'] == 'miss5_2' and not errs,
              f'読んで いる 間に とじる → エラーなし・つぎは ふつうに 出る・前の 待つ 時計（8秒）の あとも こわれない（{s1 and s1["ld"]}・{gone}・{s2 and s2["done"]}・{s3 and s3["name"]}・{errs[:2]}）')
        close(pg); ctx.close()

        # ---- 7) つぎつぎ 出して とじる（40回）----
        ctx, pg, errs, bad, req = page()
        rnd = random.Random(4150); t0 = time.time()
        for i in range(40):
            name = rnd.choice([nm for _i, _k, _n, nm in STAGES]); calm = rnd.random() < .4
            show(pg, name, calm); pg.wait_for_timeout(rnd.choice([0, 30, 80, 150, 300, 700, 1300]))
            if i % 7 == 3: show(pg, rnd.choice([nm for _i, _k, _n, nm in STAGES]), not calm); pg.wait_for_timeout(120)       # とじずに つぎを 出す
            close(pg)
        left = pg.evaluate("() => ({ ov: !!document.getElementById('fxOv'), w: document.querySelectorAll('.bcpw').length, css: document.querySelectorAll('style.bcmCss').length, cv: document.querySelectorAll('canvas.chramb').length })")
        show(pg, 'bouquet3', False); s = ready(pg); close(pg)
        check(not errs and not bad and not left['ov'] and left['w'] == 0 and left['cv'] == 0 and left['css'] == 0 and s and s['pic'] and s['done'] and s['name'] == 'bouquet3' and not (set(req) & MOVING),
              f'つぎつぎ 出して とじる（40回・{time.time() - t0:.0f}秒）：エラーなし・のこり物なし（{left}）・その あとも ふつうに 出る（花束 3連勝）（{errs[:2]}・{bad[:3]}）')
        ctx.close(); b.close()
finally:
    srv.terminate()
    shutil.rmtree(SRV, ignore_errors=True)
print('結果：', 'NG ' + str(len(fails)) if fails else 'OK')
sys.exit(1 if fails else 0)
