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
        # 第4.140版（11/10 14:14 まさちゃん「あと項目ごとに%を説明書に載せるようにして！」）：項目ごとに ％（表の 左に ％・その 下に 小さく 分数）。分数は 抽選の 表（tc_app.js）と 同じ
        gd = pg.evaluate("""() => { const T = TCApp._t, e = document.querySelector('#tcg');
          const rows = t => [...e.querySelectorAll(`table[data-tab=${t}] tr`)].map(r => ({ d: +r.dataset.d, pc: r.cells[0].childNodes[0].textContent, fr: r.cells[0].querySelector('small').textContent, lab: r.cells[1].textContent }));
          const key = z => z.k === 'pt' ? z.v + 'P GET' : z.k === 'tk' ? 'チケット' : (z.v || T.RT[z.tier]).join('P か ') + 'P';
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
        check(same(gd['care'], gd['wCare']) and [(r['d'], r['pc']) for r in gd['care']][:6] == [(10, '10%'), (20, '5%'), (50, '2%'), (85, '約1.18%'), (99, '約1.01%'), (121, '約0.83%')] and len(gd['care']) == 10
              and [(r['d'], r['pc']) for r in gd['care']][6:] == [(125, '0.8%'), (245, '約0.41%'), (399, '約0.25%'), (600, '約0.17%')],      # 第4.142版：ルーレット 1/125・1/245・1/399・チケット 1/600
              f"説明書：お世話の 当たりは 項目ごとに ％（10P 10%・20P 5%・50P 2%・100P 約1.18% … ルーレット 0.8%・約0.41%・約0.25%・チケット 約0.17%）・分数と 中身は 抽選の 表と 同じ（{[(r['pc'], r['fr']) for r in gd['care']]}）")
        check(same(gd['mab'], gd['wMab']) and same(gd['kami'], gd['wKami']) and [(r['d'], r['pc']) for r in gd['mab']] == [(15, '約6.67%'), (30, '約3.33%'), (60, '約1.67%')] and [(r['d'], r['pc']) for r in gd['kami']] == [(8, '12.5%'), (16, '6.25%'), (32, '約3.13%')],      # 第4.142版
              f"説明書：幻の馬・神様馬が いる 間の 当たりも ％（幻の馬 1/15・1/30・1/60／神様馬 1/8・1/16・1/32：{[(r['pc'], r['fr']) for r in gd['mab'] + gd['kami']]}）")
        od = gd['odds']; D = lambda k: round(1 / od[k])
        wantTx = ['ぜんぶ 合わせて 約21.6%', 'ルーレットは どちらも 50%', '3枚 12.5%・2枚 約33.3%・1枚 約54.2%', 'チケット（壁紙 or 7,000P・1〜3枚）', 'チケット1枚で、カギの壁紙を1つ解放するか、7,000Pにかえるか、選べるよ', '約1.52%・1/66', '約33.3%ずつ・1/3', 'ニンジンの約3.33%・1/30',
                  f'{pc(D("poop"))}（1/{D("poop")}）', f'うんちの{pc(D("gold"))}・1/{D("gold")}', f'高確ゾーン {pc(D("high"))}（1/{D("high")}', f'幻の馬 {pc(D("mab"))}（1/{D("mab")}）', f'神様馬 {pc(D("kami"))}（1/{D("kami")}）']
        check(all(x in gd['text'] for x in wantTx) and gd['fit'] and [D(k) for k in ('poop', 'gold', 'high', 'mab', 'kami')] == [7, 20, 50, 245, 399],
              f"説明書：合わせた ％・ルーレット 50%・チケットの 枚数・ハートの 抽選・呼ぶ・金のニンジン・うんち・金のうんち・高確ゾーン・幻の馬・神様馬（左の 欄に おさまる {gd['fit']}・ない もの {[x for x in wantTx if x not in gd['text']]}）")
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
        check(ks(lot['mab']) <= {'rt:800/1600', 'rt:1600/3200', 'rt:3200/6400'} and abs(lot['mab'].get('rt:800/1600', 0) / 20000 - 1 / 15) < 0.008 and abs(lot['mab'].get('rt:1600/3200', 0) / 20000 - 1 / 30) < 0.006 and abs(lot['mab'].get('rt:3200/6400', 0) / 20000 - 1 / 60) < 0.004,
              f"幻の馬：ルーレット だけ・1/15・1/30・1/60（第4.142版）{lot['mab']}")
        check(ks(lot['kami']) <= {'rt:2000/4000', 'rt:5000/10000', 'rt:10000/20000'} and abs(lot['kami'].get('rt:2000/4000', 0) / 20000 - 1 / 8) < 0.012 and abs(lot['kami'].get('rt:5000/10000', 0) / 20000 - 1 / 16) < 0.008 and abs(lot['kami'].get('rt:10000/20000', 0) / 20000 - 1 / 32) < 0.006,
              f"神様馬：ルーレット だけ・1/8・1/16・1/32（第4.142版）{lot['kami']}")
        check(any(k.startswith('pt:') or k == 'pt:' for k in lot['normal']) or any(k.startswith('pt') for k in lot['normal']), f"いつもは ポイント {lot['normal']}")
        # 第4.140版（11/10 14:14 まさちゃん「足す：10P 1/10・20P 1/20・50P 1/50 これだけ足して！」）：小さい 当たり 3つを 足した（ほかは そのまま）
        tabS = pg.evaluate("() => TCApp._t.PRIZES.map(([p, z]) => Math.round(1 / p) + ':' + z.k + ':' + (z.k === 'pt' ? z.v : z.tier || ''))")
        #   第4.142版（11/10 17:20 まさちゃん「ノーマルのルーレット抽選、幻の馬ルーレット当選と神様馬ルーレット抽選の確率だけ変えたい！」）：ルーレット 1/125・1/245・1/399・チケット 1/600（ポイントの 当たりは そのまま）
        check(tabS == ['600:tk:', '399:rt:kamisama', '245:rt:maboroshi', '125:rt:normal', '121:pt:300', '99:pt:200', '85:pt:100', '50:pt:50', '20:pt:20', '10:pt:10'], f'お世話の 抽選の 表：ルーレット 1/125・1/245・1/399・チケット 1/600・ポイントの 当たり 6つは そのまま（{tabS}）')
        tabV = pg.evaluate("() => { const T = TCApp._t, f = t => t.map(([p, z]) => Math.round(1 / p) + ':' + z.v.join('/')), sum = t => t.reduce((a, [p]) => a + p, 0); return { mab: f(T.PRIZES_VISIT.maboroshi), kami: f(T.PRIZES_VISIT.kamisama), rt: T.RT, x: T.ODDS.highX, sums: [sum(T.PRIZES), sum(T.PRIZES_VISIT.maboroshi), sum(T.PRIZES_VISIT.kamisama)] }; }")
        check(tabV['mab'] == ['60:3200/6400', '30:1600/3200', '15:800/1600'] and tabV['kami'] == ['32:10000/20000', '16:5000/10000', '8:2000/4000'] and tabV['rt'] == {'normal': [800, 1600], 'maboroshi': [1600, 3200], 'kamisama': [3200, 6400]},
              f"幻の馬・神様馬の 表：1/15・1/30・1/60／1/8・1/16・1/32（ポイントの 数は そのまま）（{tabV['mab']}・{tabV['kami']}）")
        check(all(x * tabV['x'] < 1 for x in tabV['sums']) and abs(tabV['sums'][0] - 0.21638) < 0.0001 and abs(tabV['sums'][1] - 7 / 60) < 1e-9 and abs(tabV['sums'][2] - 7 / 32) < 1e-9,
              f"高確ゾーン（×{tabV['x']}）でも 当たりの 合計は 1 を こえない（いつも {tabV['sums'][0] * tabV['x']:.1%}・幻の馬 {tabV['sums'][1] * tabV['x']:.1%}・神様馬 {tabV['sums'][2] * tabV['x']:.1%}）")
        nm = lot['normal']; rate = lambda c, k: c.get(k, 0) / 20000
        check(abs(rate(nm, 'pt:10') - 0.10) < 0.008 and abs(rate(nm, 'pt:20') - 0.05) < 0.006 and abs(rate(nm, 'pt:50') - 0.02) < 0.004 and abs(rate(nm, 'pt:100') - 1 / 85) < 0.0035 and abs(1 - rate(nm, '-') - 0.2164) < 0.012
              and abs(rate(nm, 'rt:normal') - 1 / 125) < 0.003 and abs(rate(nm, 'rt:maboroshi') - 1 / 245) < 0.0022 and abs(rate(nm, 'rt:kamisama') - 1 / 399) < 0.0018 and abs(rate(nm, 'tk:') - 1 / 600) < 0.0015,
              f"2万回 ひくと：10P {rate(nm, 'pt:10'):.1%}・20P {rate(nm, 'pt:20'):.1%}・50P {rate(nm, 'pt:50'):.1%}・100P {rate(nm, 'pt:100'):.2%}・ルーレット {rate(nm, 'rt:normal'):.2%}（0.8%）・{rate(nm, 'rt:maboroshi'):.2%}（約0.41%）・{rate(nm, 'rt:kamisama'):.2%}（約0.25%）・チケット {rate(nm, 'tk:'):.2%}（約0.17%）・何か 当たる {1 - rate(nm, '-'):.1%}（約21.6%）")
        hz = pg.evaluate("""() => { const T = TCApp._t, st = TCApp.state, S = TCCare.S, n = 20000, c = {}; st.visit = null;
          for (let i = 0; i < n; i++) { S.high = 3; const z = T.draw(); const k = z ? z.k + ':' + (z.k === 'pt' ? z.v : (z.tier || '')) : '-'; c[k] = (c[k] || 0) + 1; }
          S.high = 0; st.high = 0; return c; }""")
        check(abs(rate(hz, 'pt:10') - 0.40) < 0.015 and abs(rate(hz, 'pt:100') - 4 / 85) < 0.006 and abs(1 - rate(hz, '-') - 0.8655) < 0.012 and abs(rate(hz, 'rt:normal') - 4 / 125) < 0.006 and abs(rate(hz, 'tk:') - 4 / 600) < 0.003,
              f"高確ゾーン（4倍）：10P {rate(hz, 'pt:10'):.1%}（40%）・100P {rate(hz, 'pt:100'):.1%}（約4.7%）・ルーレット {rate(hz, 'rt:normal'):.1%}（3.2%）・チケット {rate(hz, 'tk:'):.2%}（約0.67%）・何か 当たる {1 - rate(hz, '-'):.1%}（約87%：1 を こえない ので まれな 当たりも 4倍の まま）")
        print('■ 当たりを とりこぼさない・トークンの 数え方（第4.140版の バグ直し）')
        #   当たりは お世話の はじめに 決まる → すぐ 保存（pend）→ 演出の あとで わたして 消す
        pd = pg.evaluate("""async () => { const T = TCApp._t, st = TCApp.state, S = TCCare.S, W = TengelWallet, rnd = Math.random; st.visit = null; S.high = 0; st.high = 0; st.pend = null;
          const sv = () => (JSON.parse(localStorage.getItem('tengel.tc')) || {}).pend || null, t0 = W.total();
          Math.random = () => 0.04; const z = T.lottery(); Math.random = rnd;                    // 100P の 当たりを ひく（第4.142版の 表：0.0346〜0.0464 が 100P）
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
        #   お世話で 1つ 使った ちょうど その とき 10分 たって 1つ たまる → 使った ぶんは 消えない（5 → 4 → 5。前は 6）
        tr = pg.evaluate("""async () => { const st = TCApp.state, S = TCCare.S, now = Math.max(Date.now(), +st.seen || 0);
          st.stock = 5; S.stock = S.stockShow = 5; st.stockAt = now; await new Promise(r => setTimeout(r, 200));
          S.stock = 4; st.stockAt = now - 10 * 60000 - 500; await new Promise(r => setTimeout(r, 400));
          return [st.stock, S.stock]; }""")
        check(tr == [5, 5], f'お世話で 使った トークンは、同じ 瞬間に 1つ たまっても 消えない（5こ → 使って 4 → たまって 5：{tr}）')
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
        b.close()
finally:
    srv.terminate()
print('NG' if fails else 'OK', len(fails), fails)
sys.exit(1 if fails else 0)
