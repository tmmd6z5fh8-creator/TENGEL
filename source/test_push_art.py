# PUSHボタンの 絵（第4.148版・まさちゃん 2026/11/10 20:36「（画像は1枚だけもらって、「光る・へこむ・はじける」はコードで動かす）これがいいかも！」→ 11/11 に 31まい）
#   python3 test_push_art.py   （ios/push_assets/ が ある とき だけ。ない とき（CI）は「絵が ない」と 出して おわる）
#   ・台帳（pb.json）：テーマ 30こ（第4.160版：ネオンを 外した。ネオンの 絵は 手元に のこす・アプリに 入れない）ぜんぶに 絵・出す 大きさ（面積が そろう・幅 264／高さ 186 まで）・絵の 大きさ（いちばん 大きく 出す ときにも 足りる）・ぜんぶで 4MB より 小さい・もとの 絵は そのまま
#   ・30テーマ × 的中：PUSH は その テーマの 絵（読めて いる・大きさ・まん中・四角の 色／影／輪は 出ない・字の <span> は 読み上げ用に のこる・うしろの 光と 光の すじ・影の 幅）
#     → 押す：押された PUSH も 同じ 絵（テーマの へこむ 動き）・はじける かけら（テーマの もの）→ その テーマの ボード
#   ・大きさの 段：デカ的中 1.2倍・ど的中 1.4倍・虹色 1.6倍（幅 372px で 頭打ち）＝30テーマ とも 画面（390px）に おさまる。虹色は 絵の 形で 切りぬいた 虹（mask）
#   ・ど的中の 押した 画面（.ndt）：押された PUSH は 絵・光の 輪は 絵の 大きさ
#   ・控えめ：絵は 出る・うしろの 光は 動かない・光の すじは 出ない
#   ・テーマを かえた すぐ あと：新しい テーマの 絵（前の テーマの 絵は 出ない）
#   ・絵が 読めない（ファイルが ない）：いつもの 赤い PUSH（コードの PUSH）で 押せる・ボードまで 出る・エラーなし
import json, os, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
sys.path.insert(0, os.path.join(W, 'kisekae')); import push_art as _pa
PB = _pa.files()
if not PB:
    print('※ PUSHボタンの 絵（ios/push_assets）が ない ので、この テストは しない'); print('結果： OK'); sys.exit(0)
SRV = os.path.join(W, 'srv_pb'); PORT = 8798; APP = f'http://localhost:{PORT}/APP/'
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, HIST='hist_280.json', DROP='', TARGET='app'))
pth = os.path.join(SRV, 'APP', 'index.html'); html = open(pth, encoding='utf8').read()
assert "window.__NATIVE = location.protocol === 'tengel:';" in html
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
for e in PB.values(): shutil.copy(os.path.join(_pa.ROOT, e['f']), os.path.join(SRV, 'APP', e['f']))
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
fails, errs = [], []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label)
    if not c:
        fails.append(label)


RK = {str(i): i for i in range(1, 15)}
HIT = {'r': 9, 'n': 14, 'ranks': RK, 'rows': [{'t': '馬単', 'state': '的中', 'hits': [[6, 2]], 'n': 9}, {'t': '単勝', 'state': '的中', 'hits': [[6]], 'n': 3}, {'t': '3連単', 'state': '不的中', 'hits': [], 'n': 18}]}
TRI = {'r': 9, 'n': 14, 'ranks': RK, 'rows': [{'t': '3連単', 'state': '的中', 'hits': [[11, 6, 2]], 'n': 18}]}
ST = """() => { const b = document.querySelector('#fxOv .push'); if (!b) return null; const r = b.getBoundingClientRect(), im = b.querySelector('.pimg'), cs = getComputedStyle(b), af = getComputedStyle(b, '::after'),
  sh = document.querySelector('#fxOv .pshadow'), rf = b.querySelector('.rbf'), sn = b.querySelector('.pshn'), gl = b.querySelector('.pglow'), sp = b.querySelector('span'), box = b.closest('.pbox'), tap = document.querySelector('#fxOv .tap');
  const mk = e => (e ? (getComputedStyle(e).webkitMaskImage || getComputedStyle(e).maskImage || '') : '').replace(/^.*\\//, '').replace(/"?\\)$/, '');
  return { cls: b.className, w: +r.width.toFixed(1), h: +r.height.toFixed(1), l: +r.left.toFixed(1), r: +r.right.toFixed(1), t: +r.top.toFixed(1), b: +r.bottom.toFixed(1), ow: b.offsetWidth, oh: b.offsetHeight,
    img: im ? [im.getAttribute('src'), im.complete ? im.naturalWidth : 0, im.naturalHeight] : null, bg: cs.backgroundImage, bc: cs.backgroundColor, bs: cs.boxShadow, br: cs.borderTopLeftRadius, after: af.display,
    span: sp ? [sp.textContent, sp.offsetWidth, getComputedStyle(sp).opacity] : null, aria: b.getAttribute('aria-label'), glow: gl ? [gl.getAttribute('src'), getComputedStyle(gl).animationName, getComputedStyle(gl).filter.slice(0, 4)] : null,
    shn: sn ? [mk(sn), getComputedStyle(sn).display, getComputedStyle(sn, '::before').animationName] : null, rbf: rf ? mk(rf) : null, rba: box ? box.querySelectorAll('.rba').length : 0, rbw: !!(box && box.classList.contains('rbw')),
    rbwo: b.querySelectorAll('svg .rbwo').length, kids: [...b.children].map(c => c.tagName + '.' + c.className).join(), shw: sh ? parseFloat(getComputedStyle(sh).width) : 0, pz: box ? getComputedStyle(box).getPropertyValue('--pz').trim() : '',
    tap: tap ? tap.textContent : '', cur: TengelFx.current(), sw: document.documentElement.scrollWidth }; }"""
PRS = """() => { const p = document.querySelector('#fxOv .pressed'); if (!p) return null; const im = p.querySelector('.pimg'), nt = document.querySelector('#fxOv .ndt'), ring = nt && nt.querySelector('.ndtr');
  return { cls: p.className, pw: p.style.getPropertyValue('--pw'), ph: p.style.getPropertyValue('--ph'), cw: getComputedStyle(p).width, chh: getComputedStyle(p).height, img: im ? [im.getAttribute('src'), im.complete ? im.naturalWidth : 0] : null, kids: p.children.length,
    an: getComputedStyle(p).animationName, bs: getComputedStyle(p).boxShadow, bg: getComputedStyle(p).backgroundImage, burst: document.querySelectorAll('#fxOv .clips i').length,
    ndt: nt ? [nt.classList.contains('pimb'), ring ? getComputedStyle(ring).width : '', ring ? getComputedStyle(ring).height : ''] : null }; }"""


def show(pg, spec, kind, wait=450):
    pg.evaluate("([s, k]) => TengelFx.show(Object.assign({ force: k }, s))", [spec, kind]); pg.wait_for_timeout(wait)


def close(pg):
    pg.evaluate('TengelFx.close()'); pg.wait_for_timeout(120)


def apply(pg, tid):
    pg.evaluate("(id) => TengelKisekae.apply(id, false)", tid)
    pg.wait_for_function("(id) => TengelKisekae.current() === id && TengelKisekae.loaded() && !!TengelKisekae.pushArt()", arg=tid, timeout=8000)


try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo')
        pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        bad = []; pg.on('response', lambda r: bad.append(r.url.split('/')[-1]) if r.status >= 400 and '/pb_' in r.url else None)
        pg.goto(APP); pg.wait_for_timeout(1500)
        if pg.locator('#gateGo').count(): pg.click('#gateGo'); pg.wait_for_timeout(700)
        pg.wait_for_function("() => window.TengelKisekae && window.TengelFx && !!TengelKisekae.pushArt()", timeout=10000)
        TH = pg.evaluate("TengelKisekae.list().map(t => ({ id: t.id, name: t.name, pc: t.pc, pa: t.pa || null }))")
        man = _pa.manifest()['files']
        # ---- 台帳と ファイル ----
        sz = sum(os.path.getsize(os.path.join(_pa.ROOT, e['f'])) for e in PB.values())
        okm = []
        for t in TH:
            e, pa = man.get(t['id']), t['pa']
            ok = bool(e and pa) and pa == {'f': e['f'], 'w': e['w'], 'h': e['h']} and e['f'] == 'pb_' + t['id'] + '.webp' and e['w'] <= 264 and e['h'] <= 186 and e['w'] % 2 == 0 and e['h'] % 2 == 0
            ok = ok and abs(e['w'] / e['h'] - e['iw'] / e['ih']) < 0.03 and 27000 <= e['w'] * e['h'] <= 35500
            pz = max(1, min(1.6, 372 / e['w'], 480 / e['h'])) if ok else 0
            ok = ok and abs(pz - e['pz']) < 0.002 and e['iw'] >= e['w'] * pz * 2.5 and e['iw'] <= 1100
            okm.append((t['id'], ok))
        GONE_PB = sorted(_pa.gone())      # 第4.160版：外した テーマ（ネオン）の 絵は 手元に のこす・アプリに 入れない
        check(len(TH) == 30 and len(PB) == 30 and all(o for _i, o in okm) and _pa.stale() == '' and sz < 4_000_000
              and sorted(f for f in os.listdir(_pa.ROOT) if f.endswith('.webp') and f[len('pb_'):-len('.webp')] not in GONE_PB) == sorted(e['f'] for e in PB.values())
              and not any(f.endswith('.png') for f in os.listdir(os.path.join(SRV, 'APP')) if f.startswith('pb_')),
              f'台帳：テーマ 30こ ぜんぶに 絵（pb_<id>.webp）・出す 大きさは 面積が そろう（幅 264／高さ 186 まで）・絵は いちばん 大きく 出す ときの 2.5倍 以上・ぜんぶで {sz / 1e6:.2f}MB・もとの 絵（src）は そのまま（{[i for i, o in okm if not o]}）')
        check('neon' in GONE_PB and 'neon' not in PB and not any(t['id'] == 'neon' for t in TH) and not os.path.exists(os.path.join(SRV, 'APP', 'pb_neon.webp'))
              and os.path.exists(os.path.join(_pa.IN, 'neon.png')) and os.path.exists(os.path.join(_pa.ROOT, 'pb_neon.webp')) and 'neon' in man,
              '第4.160版：ネオンの PUSH の 絵は アプリに 入れない（一覧にも ない）・もとの 絵（src/neon.png）と できた 絵（pb_neon.webp）・台帳の 行は 手元に のこって いる')
        # ---- 30テーマ × 的中：PUSH → 押す → ボード ----
        r1, r2, r3 = [], [], []
        for t in TH:
            tid, e = t['id'], man[t['id']]
            apply(pg, tid); show(pg, HIT, 'hit', 350)
            s = pg.evaluate(ST)
            ok = (bool(s) and 'pim' in s['cls'].split() and (not t['pc'] or t['pc'] in s['cls'].split()) and [s['ow'], s['oh']] == [e['w'], e['h']] and s['img'] == [e['f'], e['iw'], e['ih']]
                  and s['bg'] == 'none' and s['bc'] in ('rgba(0, 0, 0, 0)', 'transparent') and s['bs'] == 'none' and s['br'] == '0px' and s['after'] == 'none'
                  and s['span'] and s['span'][0] == 'PUSH' and s['span'][1] <= 1 and s['aria'] == '的中ボタン' and s['kids'] == 'IMG.pglow,IMG.pimg,I.pshn,SPAN.'
                  and s['glow'] == [e['f'], 'fxpimGlow', 'blur'] and s['shn'] == [e['f'], 'block', 'fxpimShine'] and s['rbf'] is None and not s['rbw']
                  and abs((s['l'] + s['r']) / 2 - 195) <= 1 and s['l'] >= 8 and s['r'] <= 382 and abs(s['shw'] - e['w'] * .8) <= 1.5 and s['tap'] == 'タップ！' and s['cur']['art'] == e['f'] and s['cur']['pz'] == 1 and s['sw'] <= 390)
            r1.append((tid, ok, None if ok else s))
            nb = pg.evaluate("() => { const k = TengelKisekae.fx(); if (!k || !k.push) return 0; const d = document.createElement('div'); d.innerHTML = k.push.burst || ''; return d.querySelectorAll('.clips i').length; }")   # その テーマの かけらの 数
            pg.evaluate('TengelFx.tap()'); pg.wait_for_timeout(60)
            q = pg.evaluate(PRS)
            okp = (bool(q) and 'pim' in q['cls'].split() and q['pw'] == f"{e['w']}px" and q['ph'] == f"{e['h']}px" and q['cw'] == f"{e['w']}px" and q['chh'] == f"{e['h']}px" and q['img'] == [e['f'], e['iw']] and q['kids'] == 1
                   and q['bs'] == 'none' and q['bg'] == 'none' and q['an'].endswith('fxfxH') and 'ress' in q['an'].split(',')[0] and q['burst'] == nb and (nb == 0 if tid == 'default' else True))
            r2.append((tid, okp, None if okp else q))
            pg.wait_for_timeout(2300)
            bd = pg.evaluate("() => { const rb = [...document.querySelectorAll('#fxOv .rb')].find(e => e.querySelector('.bh')); return rb ? [rb.className, rb.querySelector('.bh').textContent, getComputedStyle(document.querySelector('#fxOv .close') || rb).visibility] : null; }")
            okb = bool(bd) and bd[1] == '的中！' and ('t-' + tid in bd[0]) and bd[2] == 'visible'
            r3.append((tid, okb, None if okb else bd)); close(pg)
        check(all(o for _i, o, _s in r1) and not errs, f'30テーマ × 的中：PUSH は その テーマの 絵（読めて いる・台帳の 大きさ・まん中・四角の 色／影／まわりの 輪は なし・字は 読み上げ用に のこる・うしろの 光と 光の すじ・影の 幅 8割）（{[(i, s) for i, o, s in r1 if not o][:2]}）')
        check(all(o for _i, o, _s in r2), f'30テーマ：押すと 押された PUSH も 同じ 絵（テーマの へこむ 動き）・はじける かけらは テーマの もの（いつもの は なし）（{[(i, s) for i, o, s in r2 if not o][:2]}）')
        check(all(o for _i, o, _s in r3) and not errs and not bad, f'30テーマ：そのあと その テーマの ボード（的中！・とじる）まで 出る・絵の 読みこみの 失敗なし（{[(i, s) for i, o, s in r3 if not o][:2]}・{bad[:3]}）')
        # ---- 大きさの 段（デカ 1.2・ど 1.4・虹色 1.6：幅 372／高さ 480 で 頭打ち）と 虹色 ----
        r4 = []
        for t in TH:
            tid, e = t['id'], man[t['id']]; apply(pg, tid)
            for kind, PZ, rb in (('big', 1.2, False), ('nd', 1.4, False), ('pc', 1.6, True)):
                show(pg, TRI, kind, 700); s = pg.evaluate(ST); close(pg)      # 出て くる 動き（ポンと 大きく なる）が おわって から 測る
                pz = max(1, min(PZ, 372 / e['w'], 480 / e['h']))
                ok = (bool(s) and 'pim' in s['cls'].split() and abs(float(s['pz']) - pz) < 0.002 and abs(s['cur']['pz'] - pz) < 0.002 and [s['ow'], s['oh']] == [e['w'], e['h']] and abs(s['w'] - e['w'] * pz) <= e['w'] * pz * .08 + 1.5 and abs(s['h'] - e['h'] * pz) <= e['h'] * pz * .08 + 1.5      # テーマの ゆれる 動き（ぷりけつ など）の ぶん 8% まで
                      and s['l'] >= 0 and s['r'] <= 390 and s['t'] >= 0 and s['b'] <= 844
                      and s['img'] == [e['f'], e['iw'], e['ih']] and s['rbw'] == rb and s['rba'] == (1 if rb else 0) and s['rbf'] == (e['f'] if rb else None) and s['rbwo'] == 0 and s['sw'] <= 390)
                r4.append((tid, kind, ok, None if ok else s))
        check(all(o for _i, _k, o, _s in r4) and not errs, f'30テーマ × デカ的中（1.2倍）・ど的中（1.4倍）・虹色（1.6倍）：絵の 大きさで 決まる（幅 372px で 頭打ち）・画面に おさまる・虹色は 絵の 形で 切りぬいた 虹（mask）と うしろの 虹の 光（{[(i, k, s) for i, k, o, s in r4 if not o][:2]}）')
        # ---- デカ的中・ど的中の 押した あと ----
        apply(pg, 'silks'); e = man['silks']
        show(pg, TRI, 'big', 300); pg.evaluate('TengelFx.tap()'); pg.wait_for_timeout(60); qb = pg.evaluate(PRS)
        zb = pg.evaluate("() => { const z = document.querySelector('#fxOv .pzw'); return z ? [z.style.getPropertyValue('--pz'), !!z.querySelector('.pressed.pim .pimg'), z.querySelectorAll('.clips i').length] : null; }"); close(pg)
        show(pg, TRI, 'nd', 300); pg.evaluate('TengelFx.tap()'); pg.wait_for_timeout(60); qn = pg.evaluate(PRS); close(pg)
        check(bool(qb) and qb['img'] == [e['f'], e['iw']] and qb['pw'] == f"{e['w']}px" and zb and abs(float(zb[0]) - 1.2) < 0.002 and zb[1] and zb[2] >= 8
              and bool(qn) and qn['img'] == [e['f'], e['iw']] and qn['ndt'] == [True, f"{e['w'] + 26}px", f"{e['h'] + 26}px"] and 'fxndtP' in qn['an'] and not errs,
              f'デカ的中・ど的中を 押した あと：押された PUSH は 同じ 絵（同じ 倍率の 箱の 中）・ど的中の 押した 画面の 光の 輪は 絵の 大きさ（{qb and qb["cls"]}・{qn and qn["ndt"]}）')
        # ---- 控えめ ----
        pg.evaluate("TengelFx.set({ calm: true })"); pg.wait_for_timeout(100)
        show(pg, HIT, 'hit', 300); sc = pg.evaluate(ST)
        pg.evaluate('TengelFx.tap()'); pg.wait_for_timeout(700)
        bc = pg.evaluate("() => { const rb = [...document.querySelectorAll('#fxOv .rb')].find(e => e.querySelector('.bh')); return rb ? rb.querySelector('.bh').textContent : null; }"); close(pg)
        pg.evaluate("TengelFx.set({ calm: false })"); pg.wait_for_timeout(100)
        check(bool(sc) and sc['img'] == [e['f'], e['iw'], e['ih']] and sc['glow'][1] == 'none' and sc['shn'][1] == 'none' and [sc['ow'], sc['oh']] == [e['w'], e['h']] and bc == '的中！' and not errs,
              f'控えめ：絵の PUSH は 出る・うしろの 光は 動かない・光の すじは 出ない・押すと ボード（{sc and sc["glow"]}・{sc and sc["shn"]}）')
        # ---- テーマを かえた すぐ あと ----
        pg.evaluate("(async () => { await TengelKisekae.apply('pirate'); TengelKisekae.apply('ukiyoe'); })()")
        pg.wait_for_function("() => TengelKisekae.current() === 'ukiyoe' && TengelKisekae.loaded() && !!TengelKisekae.pushArt()", timeout=8000)
        show(pg, HIT, 'hit', 300); sx = pg.evaluate(ST); close(pg)
        check(bool(sx) and sx['img'][0] == 'pb_ukiyoe.webp' and sx['cur']['theme'] == 'ukiyoe' and pg.evaluate("TengelKisekae.pushArt('pirate').src") == 'pb_pirate.webp' and pg.evaluate("TengelKisekae.pushArt('nothing')") is None,
              f'テーマを かえた すぐ あと：新しい テーマ（浮世絵風）の 絵（{sx and sx["img"]}）')
        ctx.close()
        # ---- 絵が 読めない（ファイルが ない）：今までの コードの PUSH ----
        ctx2 = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo')
        ctx2.route('**/pb_*.webp', lambda route: route.fulfill(status=404, body='not found'))
        p2 = ctx2.new_page(); e2 = []; p2.on('pageerror', lambda x: e2.append(str(x)))
        p2.goto(APP); p2.wait_for_timeout(1500)
        if p2.locator('#gateGo').count(): p2.click('#gateGo'); p2.wait_for_timeout(700)
        res = []
        for tid in ('default', 'sunset', 'pirate'):
            p2.evaluate("(id) => TengelKisekae.apply(id, false)", tid)
            p2.wait_for_function("(id) => TengelKisekae.current() === id && TengelKisekae.loaded()", arg=tid, timeout=8000); p2.wait_for_timeout(500)
            art = p2.evaluate("TengelKisekae.pushArt()")
            show(p2, HIT, 'hit', 350); s = p2.evaluate(ST)
            p2.evaluate('TengelFx.tap()'); p2.wait_for_timeout(2400)
            bh = p2.evaluate("() => { const rb = [...document.querySelectorAll('#fxOv .rb')].find(e => e.querySelector('.bh')); return rb ? rb.querySelector('.bh').textContent : null; }"); close(p2)
            ok = (art is None and bool(s) and s['cls'] == 'push' and s['img'] is None and [s['ow'], s['oh']] == [200, 100] and s['span'] and s['span'][0] == 'PUSH' and s['span'][1] > 60 and float(s['span'][2]) == 1
                  and s['bg'] != 'none' and s['after'] != 'none' and s['cur']['art'] == '' and s['cur']['theme'] is None and bh == '的中！')
            res.append((tid, ok, None if ok else s))
        check(all(o for _i, o, _s in res) and not e2, f'絵が 読めない とき（いつもの・夕焼け・海賊）：いつもの 赤い PUSH（200×100 の 四角に「PUSH」の 字・まわりの 輪）で 押せて ボードまで 出る・エラーなし（{[(i, s) for i, o, s in res if not o][:1]}・{e2[:2]}）')
        ctx2.close()
        check(not errs, f'ページの エラーなし（{errs[:3]}）')
        b.close()
finally:
    srv.terminate()
    shutil.rmtree(SRV, ignore_errors=True)
print('結果：', 'NG ' + str(len(fails)) if fails else 'OK')
sys.exit(1 if fails else 0)
