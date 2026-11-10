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
TCA = os.path.join(W, 'ios', 'tc_assets'); HAVE = os.path.isdir(TCA) and len(os.listdir(TCA)) > 100
if HAVE:
    for f in os.listdir(TCA): shutil.copy(os.path.join(TCA, f), os.path.join(SRV, 'APP', f))
else:
    print('※ トレーニングセンターの 絵と 音（ios/tc_assets）が ない ので、ボタンと 読みこめない 形だけ')
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


def shot(pg, name):
    if SHOT: os.makedirs(SHOT, exist_ok=True); pg.screenshot(path=os.path.join(SHOT, name + '.png'))


try:
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'])
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo')
        ctx.add_init_script(FAKE)
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
            ff: cs.fontFamily, fw: cs.fontWeight, fs: cs.fontSize, bg: cs.backgroundImage + cs.backgroundColor, ink: cs.color, line: cs.borderTopColor, order: getComputedStyle(f).order, bnb: bn && !bn.hidden ? R(bn).bottom : 0 }; }"""
        #   はじめの 判定タブは 入力例の 判定の 帯（#minibar）が 出て いて 列は その 上に いる（下の「かくれた ままに ならない」で 見る）→ いつもの 場所は 記録タブで 見る
        pg.evaluate("() => document.querySelectorAll('.tabbar button')[2].click()"); pg.wait_for_timeout(500)
        pos = pg.evaluate(POS)
        check(pos is not None and 4 <= pos['tab'] - pos['cb'] <= 14 and pos['cr'] <= 390 and pos['cl'] >= 390 - 84 and pos['ct'] > pos['hb'] + 200 and pos['top'] == pos['ct'],
              f'ボタンの 列は 下の タブの すぐ 上・右はし（上の 帯からは はなれて いる）・トレーニングセンターが いちばん 上（{pos and [round(pos["ct"]), round(pos["cb"]), round(pos["tab"]), round(pos["cl"]), round(pos["cr"])]}）')
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
        check(q is not None and 4 <= q['tab'] - q['cb'] <= 14 and pg.locator('#tcFab').is_visible(), 'スクロール しても 下の タブの すぐ 上に いる')
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
        check(m0['mt'] is None and 4 <= m0['tab'] - m0['cb'] <= 14 and m1['mt'] is not None and 2 <= m1['mt'] - m1['cb'] <= 10 and m1['cb'] < m0['cb'] - 20 and abs(m2['cb'] - m0['cb']) < 1 and m1['pb'] == m0['pb'],
              f'判定タブの 下の 帯（判定の 要点）が 出ると 列は その 上へ（帯の 上 {m1["mt"] and round(m1["mt"])}・列の 下 {round(m1["cb"])}）・帯が 消えると もどる（{round(m0["cb"])} → {round(m1["cb"])} → {round(m2["cb"])}）・ページの 下の 余白は かわらない')
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
        px = pg.evaluate("() => { const c = document.querySelector('#tcOv .tcgl'); const g = c.getContext('webgl'); const p = new Uint8Array(4); g.readPixels(c.width >> 1, c.height >> 1, 1, 1, g.RGBA, g.UNSIGNED_BYTE, p); return [c.width, c.height, Array.from(p)]; }")
        check(px[0] > 100 and px[1] > 100, f'フィールドの キャンバス {px}')
        # 第4.138版（11/10 10:48 まさちゃん「作戦会議のアイコン、一枚目の赤四角のところにして！」）：お世話の 板（44〜150）の すぐ 下・屋根（241〜）の 上
        pp = pg.evaluate("() => { const s = document.querySelector('#tcOv .tcst').getBoundingClientRect(), p = document.querySelector('#tcOv .tcpl').getBoundingClientRect(); return [(p.top - s.top) / s.height * 1657, (p.bottom - s.top) / s.height * 1657, (p.left - s.left) / s.width * 1052, (p.right - s.left) / s.width * 1052]; }")
        vt, vb, vl, vr = pp[0] + (pp[1] - pp[0]) * 31 / 200, pp[0] + (pp[1] - pp[0]) * 170 / 200, pp[2] + (pp[3] - pp[2]) * 16 / 500, pp[2] + (pp[3] - pp[2]) * 483 / 500
        check(155 <= vt <= 175 and vb <= 244 and 760 <= vl and 1010 <= vr <= 1026, f'作戦会議の ボタン（見える 板）は お世話の 板の すぐ 下（上 {vt:.0f}・下 {vb:.0f}・左 {vl:.0f}・右 {vr:.0f}：板は 730〜1026 × 44〜150・屋根は 241 から）')
        shot(pg, 'tc_open')
        print('■ ごはん（エサ・3D の バケツ）')
        stock0 = pg.evaluate("() => TCCare.S.stock")
        stage_click(pg, 407, 1494); pg.wait_for_timeout(1200)
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
        tot = pg.evaluate("() => [TCCare.S.stock, TCApp.state.total, TCApp.state.cares]")
        check(tot[0] == stock0 - 1 and tot[1] >= 1, f'お世話トークンを 1つ 使って、お世話の 合計が ふえた {stock0} → {tot}')
        # 第4.139版（抜け穴を ふさぐ）：端末の 時計を 先へ 進めて お世話トークンを ためる → 時計を もどす、を ふせぐ（tc_app.js の tnow：もどらない 時計）
        print('■ 時計を 進めて もどす ズルを ふせぐ')
        TS = "() => { const s = TCApp.state; return { stock: s.stock, at: s.stockAt, seen: s.seen, now: Date.now() }; }"
        k0 = pg.evaluate(TS)
        check(k0['seen'] is not None and abs(k0['seen'] - k0['now']) < 5000, f'開いて いる あいだ、いままでに 見た いちばん 先の 時刻（seen）を おぼえる（{k0["stock"]}こ）')
        pg.evaluate("() => { window.__realNow = Date.now.bind(Date); const r = window.__realNow; Date.now = () => r() + 200 * 60000; }"); pg.wait_for_timeout(700)
        k1 = pg.evaluate(TS)
        check(k1['stock'] == 20 and k1['seen'] - k0['now'] >= 199 * 60000, f'時計を 200分 進める → トークンは 満タン（20こ）：ここまでは 止められない（{k0["stock"]} → {k1["stock"]}）')
        pg.evaluate("() => { Date.now = window.__realNow; }"); pg.wait_for_timeout(700)
        k2 = pg.evaluate(TS)
        check(k2['stock'] == 20 and k2['at'] >= k1['seen'] - 3000 and 0 <= k2['seen'] - k1['seen'] < 5000 and k2['at'] - k2['now'] >= 190 * 60000,
              f'時計を もどしても、数えはじめの 時刻は 先の 時刻の まま（前は 満タンの とき いまの 時刻に 書きかえて いた）（あと {round((k2["at"] - k2["now"]) / 60000)}分）')
        pg.evaluate("() => { TCApp.state.stock = 5; TCCare.S.stock = TCCare.S.stockShow = 5; const r = window.__realNow; Date.now = () => r() + 30 * 60000; }"); pg.wait_for_timeout(800)
        k3 = pg.evaluate(TS)
        check(k3['stock'] == 5 and k3['seen'] == k2['seen'], f'トークンを 使って（5こ）30分 たっても ふえない（本当の 時刻が 先に 見た 時刻に 追いつくまで）（{k3["stock"]}こ）')
        pg.evaluate("() => { const r = window.__realNow; Date.now = () => r() + 231 * 60000; }"); pg.wait_for_timeout(800)
        k4 = pg.evaluate(TS)
        check(k4['stock'] == 8 and k4['seen'] > k2['seen'], f'先に 見た 時刻を こえたら また ふえる（30分ぶん＝3こ：5 → {k4["stock"]}）')
        pg.evaluate("() => { Date.now = window.__realNow; const s = TCApp.state, n = Date.now(); s.seen = n; s.stockAt = n; }"); pg.wait_for_timeout(300)
        print('■ 説明書')
        stage_click(pg, 678, 97); pg.wait_for_timeout(1200)
        g = pg.evaluate("() => { const e = document.querySelector('#tcg'); return e ? [e.style.display, e.textContent.includes('幻の馬・神様馬がいるあいだ'), e.textContent.includes('10000P か 20000P')] : null; }")
        check(g and g[0] != 'none' and g[1] and g[2], f'説明書に 幻の馬・神様馬の 当たり {g}')
        shot(pg, 'tc_guide')
        pg.evaluate("() => TCGuide.close()"); pg.wait_for_timeout(500)
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
        pg.locator('#tcPlan [data-p=close]').click(); pg.wait_for_timeout(300)
        print('■ 当たりの 抽選（幻の馬・神様馬が いる 間は その 表だけ）')
        lot = pg.evaluate("""() => { const T = TCApp._t, st = TCApp.state, S = TCCare.S, n = 20000, cnt = (kind) => { st.visit = kind ? { kind, until: Date.now() + 6e5 } : null; S.high = 0; const c = {}; for (let i = 0; i < n; i++) { const z = T.lottery(); const k = z ? z.k + ':' + (Array.isArray(z.v) ? z.v.join('/') : z.k === 'pt' ? z.v : (z.tier || '')) : '-'; c[k] = (c[k] || 0) + 1; } return c; };
          const r = { normal: cnt(null), mab: cnt('maboroshi'), kami: cnt('kamisama') }; st.visit = null; return r; }""")
        ks = lambda c: set(k for k in c if k != '-')
        check(ks(lot['mab']) <= {'rt:800/1600', 'rt:1600/3200', 'rt:3200/6400'} and 'rt:800/1600' in lot['mab'], f"幻の馬：ルーレット だけ {lot['mab']}")
        check(ks(lot['kami']) <= {'rt:2000/4000', 'rt:5000/10000', 'rt:10000/20000'} and abs(lot['kami'].get('rt:2000/4000', 0) / 20000 - 1 / 85) < 0.004, f"神様馬：ルーレット だけ {lot['kami']}")
        check(any(k.startswith('pt:') or k == 'pt:' for k in lot['normal']) or any(k.startswith('pt') for k in lot['normal']), f"いつもは ポイント {lot['normal']}")
        print('■ ルーレット（神様馬：10000P か 20000P）')
        pg.evaluate("() => { window.__rtDone = false; TCFX.roulette(document.querySelector('#tcOv .tcfx'), { th: 'kamisama', a: 10000, b: 20000, win: 1, bg: 'divine', se: TCApp._snd.se }).then(() => { window.__rtDone = true; }); }")
        pg.wait_for_timeout(2500); shot(pg, 'tc_rt_wait')
        check(pg.evaluate("() => document.querySelector('#tcOv .tcfx').classList.contains('on') && !window.__rtDone"), 'タップを 待つ')
        pg.mouse.click(300, 600); pg.wait_for_timeout(5600); shot(pg, 'tc_rt_get')
        pg.mouse.click(200, 400)
        pg.wait_for_function("() => window.__rtDone", timeout=20000)
        check(True, 'タップで 回って GET → タップで とじた')
        print('■ チケット（2まい）')
        pg.evaluate("() => { window.__tkDone = false; TCFX.ticket(document.querySelector('#tcOv .tcfx'), { n: 2, bg: 'morning', se: TCApp._snd.se }).then(() => { window.__tkDone = true; }); }")
        pg.wait_for_timeout(2200); pg.mouse.click(200, 700); pg.wait_for_timeout(4600); shot(pg, 'tc_tk_get'); pg.mouse.click(200, 400)
        pg.wait_for_function("() => window.__tkDone", timeout=20000)
        check(True, '扉 → タップ → チケット GET → とじた')
        print('■ 着せ替えで チケットを 使う')
        pg.evaluate("() => { const s = TCApp.state; s.tickets = 1; localStorage.setItem('tengel.tc', JSON.stringify(s)); }")
        pg.locator('#tcOv [data-tc=back]').click(); pg.wait_for_timeout(600)
        check(pg.evaluate("() => !document.querySelector('#tcOv.on') && TCInfo.tickets() === 1 && TCInfo.total() >= 1"), 'もどる → チケット 1まい・お世話の 合計')
        check(not errs, f'エラー なし {errs[:3]}')
        b.close()
finally:
    srv.terminate()
print('NG' if fails else 'OK', len(fails), fails)
sys.exit(1 if fails else 0)
