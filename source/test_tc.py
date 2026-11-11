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
        print('■ お世話：早く 始まる・ごろんで 浮かない（第4.151版）')
        fl = pg.evaluate("""() => { const [HO, BR] = TCCare._hb, t = TCCare.S.lastT;
          const y = (st, tt) => { const q = TCHorse.wherePose(HO, TCHorse.pose(HO, st, tt), 'withers'); return q ? q[1] : NaN; };
          const lie = Object.assign({}, BR, { mode: 'sleep', sl: 0.6, rise: 0, flop: t, lieDur: 2.4, reacts: [] }), lieF = Object.assign({}, lie, { reacts: [{ k: 'frisk', t0: t - 0.5, dur: 2.2 }] });
          const st0 = Object.assign({}, BR, { sl: 0, rise: 0, reacts: [] }), stF = Object.assign({}, st0, { reacts: [{ k: 'frisk', t0: t - 0.5, dur: 2.2 }] }), stC = Object.assign({}, st0, { reacts: [{ k: 'frisk', t0: t - 0.5, dur: 2.2, cut: t - 0.3 }] });
          const d = (a, b) => Math.max(...[0, 0.06, 0.12, 0.18, 0.24, 0.3].map(k => Math.abs(y(a, t + k) - y(b, t + k))));
          return { lie: d(lieF, lie), stand: d(stF, st0), cut: d(stC, st0), down: y(lie, t) - y(st0, t) }; }""")
        check(fl['lie'] < 0.3 and fl['stand'] > 1.5 and fl['cut'] < 0.3 and fl['down'] > 10,
              f'横に なった 馬は はしゃぐ 反応で 浮かない（体の 上下 {fl["lie"]:.2f}px。立って いる ときは {fl["stand"]:.1f}px はずむ）・とちゅうで 止めた 反応（cut）は 0.25秒で 消える（{fl["cut"]:.2f}px）')
        lat = pg.evaluate("""async () => { const [HO, BR] = TCCare._hb, S = TCCare.S; Object.assign(BR, { x: 526, y: 820, dir: -1.2, mode: 'idle', until: S.lastT + 60 }); await new Promise(r => setTimeout(r, 400));
          const t0 = S.lastT; TCCare.press(t0, 'pet'); const h = BR.hurry, m0 = BR.mode, zb = S.zB ? S.zB.z : 0;
          for (let i = 0; i < 1200 && S.phase !== 'pet'; i++) await new Promise(r => requestAnimationFrame(r));
          const t1 = S.lastT, ph = S.phase, y1 = BR.y, x1 = BR.x, side = Math.abs(Math.sin(BR.dir)); S.petIdle = -1e9;
          for (let i = 0; i < 400 && S.phase !== 'idle'; i++) await new Promise(r => setTimeout(r, 50));
          return { lat: t1 - t0, ph, h, m0, zb, y1, x1, side, end: S.phase, cool: S.coolUntil > S.lastT, z: S.zoom.z }; }""")
        check(lat['ph'] == 'pet' and lat['h'] == 2.8 and lat['m0'] == 'idle' and lat['zb'] > 2.2 and lat['lat'] < 2.0 and abs(lat['y1'] - 820) < 25 and abs(lat['x1'] - 526) < 60 and lat['side'] < 0.4 and lat['end'] == 'idle' and not lat['cool'] and lat['z'] == 1,
              f'「撫でる」を 押して から 撫でられる まで {lat["lat"]:.2f}秒（いちばん 奥で むこう向き：歩かないで その場で 横向きに・カメラは 押した ときから 寄る {lat["zb"]:.2f}倍。第4.150版は 14.8秒）・撫でずに もどっても 7秒の 待ちは ない')
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
            stage_click(pg, 644, 1494); pg.wait_for_timeout(600)
            if pg.evaluate("() => TCCare.S.mode === 'clean'"): break
        for _ in range(40):
            pg.wait_for_timeout(250)
            if pg.evaluate("() => TCCare.S.phase === 'clean' && !!TCCare._hb[1].props"): break
        cs = pg.evaluate("""() => { const [HO, BR] = TCCare._hb, S = TCCare.S, C = S.clean, s = TCApp.state;
          return { phase: S.phase, n: C ? C.tg.length : 0, props: (BR.props || []).map(q => q.P.meta.i), st: s.trash.length, left: (s.trashAt - Date.now()) / 60000, stock: S.stock, live: (BR.trash || []).length, z: S.zoom.z }; }""")
        check(cs['phase'] == 'clean' and cs['n'] == 5 and cs['props'] == [6888, 21000] and cs['st'] == 0 and 14.5 < cs['left'] <= 15.01 and cs['stock'] == tr['stock'] - 1 and cs['live'] == 5,
              f'「おそうじ」を 押す → 3D の ちりとりと ほうきが 出る（三角 {[v // 3 for v in cs["props"]]}こ）・トークン −1・その ときに「片付けた」（次の ゴミまで {cs["left"]:.1f}分）・ゴミは まだ 見えて いる')
        shot(pg, 'tc_clean_tools')
        sw = pg.evaluate("""async () => { const S = TCCare.S, C = S.clean, raf = () => new Promise(r => requestAnimationFrame(r)); let n = 0; const mid = [];
          while (C.tg.some(q => !q.done) && n < 12) { const T = C.tg.find(q => !q.done), o = T.o, from = [o.x + 130, o.y + 8]; TCCare.input('down', from[0], from[1], S.lastT); const pn = { x: C.pan.x, y: C.pan.y }, g0 = C.got;
            for (let i = 1; i <= 16 && C.got === g0; i++) { await raf(); TCCare.input('move', from[0] + (pn.x - from[0]) * i / 16, from[1] + (pn.y - from[1]) * i / 16, S.lastT); }
            mid.push([Math.round(pn.x), Math.round(pn.y), C.got - g0]); TCCare.input('up', pn.x, pn.y, S.lastT); n++; await new Promise(r => setTimeout(r, 150)); }
          return { n, got: C.got, phase: S.phase, mid }; }""")
        check(sw['n'] <= 5 and sw['got'] == 5 and sw['phase'] == 'cleanwait' and all(90 <= m[0] <= 962 and 790 <= m[1] <= 1430 and m[2] >= 1 for m in sw['mid']),
              f'ほうきで 山を 押して ちりとりへ：なぞる たびに 入る（{sw["n"]}回 なぞって {sw["got"]}こ）・ちりとりは いつも フィールドの 中')
        for _ in range(60):
            pg.wait_for_timeout(250)
            if pg.evaluate("() => TCCare.S.phase === 'idle' && !TCCare.S.clean"): break
        af = pg.evaluate(TR)
        check(af['phase'] == 'idle' and af['n'] == 0 and len(af['live']) == 0 and 14.4 < af['left'] <= 15 and 860 < af['trashIn'] <= 900,
              f'片付いた：ゴミは ない・次の ゴミまで {af["left"]:.1f}分（片付ける までは 次が 出ない）')
        for _ in range(16):
            stage_click(pg, 644, 1494); pg.wait_for_timeout(600)
            if pg.evaluate("() => TCCare.S.fx.some(f => f.k === 'tagUI' && /ゴミ/.test(f.txt))"): break
        ag = pg.evaluate("() => { const S = TCCare.S; return { phase: S.phase, mode: S.mode, stock: S.stock, tags: S.fx.filter(f => f.k === 'tagUI').map(f => f.txt) }; }")
        check(ag['phase'] == 'idle' and ag['mode'] is None and ag['stock'] == af['stock'] and 'ゴミは あと 15分で 出るよ' in ag['tags'],
              f'つづけては できない：「{ag["tags"][-1] if ag["tags"] else ""}」・トークンは 使わない（{ag["stock"]}こ の まま）')
        pg.evaluate("() => { const [HO, BR] = TCCare._hb; BR.poops = [{ x: 470, y: 1230, img: 1, t0: -10, h0: 1.05, w: 0.5 * (HO.opt.stage || 1), gold: false }]; }"); pg.wait_for_timeout(600)
        for _ in range(16):
            stage_click(pg, 644, 1494); pg.wait_for_timeout(600)
            if pg.evaluate("() => TCCare.S.mode === 'clean'"): break
        for _ in range(40):
            pg.wait_for_timeout(250)
            if pg.evaluate("() => TCCare.S.phase === 'clean'"): break
        pc_ = pg.evaluate("""async () => { const S = TCCare.S, C = S.clean, raf = () => new Promise(r => requestAnimationFrame(r)); if (!C) return null; const T = C.tg[0], o = T.o, from = [o.x + 130, o.y + 8], z = S.zoom.z, left = (TCApp.state.trashAt - Date.now()) / 60000;
          TCCare.input('down', from[0], from[1], S.lastT); const pn = { x: C.pan.x, y: C.pan.y };
          for (let i = 1; i <= 16 && !T.done; i++) { await raf(); TCCare.input('move', from[0] + (pn.x - from[0]) * i / 16, from[1] + (pn.y - from[1]) * i / 16, S.lastT); }
          TCCare.input('up', pn.x, pn.y, S.lastT); return { n: C.tg.length, poop: !!T.poop, done: !!T.done, z, left, saved: TCApp.state.poops.length }; }""")
        check(pc_ and pc_['n'] == 1 and pc_['poop'] and pc_['done'] and pc_['z'] > 1.3 and 14.2 < pc_['left'] <= 15 and pc_['saved'] == 0,
              f'ゴミが なくても うんちが 出たら おそうじ できる（カメラが 寄る {pc_["z"]:.2f}倍・ゴミの 15分は そのまま {pc_["left"]:.1f}分）')
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
        wantTx = ['ぜんぶ 合わせて 約21.6%', 'ルーレットは どちらも 50%', '3枚 12.5%・2枚 約33.3%・1枚 約54.2%', 'チケット（壁紙 or 7,000P・1〜3枚）', 'チケット1枚で、カギの壁紙を1つ解放するか、7,000Pにかえるか、選べるよ', 'お世話（ごはん・おそうじ）を5回すると、リセットのタイマーがスタート', 'タイマーが5分たつとリセット → 次の馬を抽選', 'それ以外は いつもの馬のまま', 'お世話をしないと 馬はかわらないよ（開いているだけでは 抽選しないよ）', 'お世話のとちゅうは リセットしないよ',
                  '帰るのは、お世話5回のあと5分（リセット）か、来てから30分（タイムリミット）の どちらか早いほう', '左上の「なかよし」の下に「タイムリミット・お世話の回数・切り替わりタイマー」が出るよ', '約1.52%・1/66', '約33.3%ずつ・1/3', 'ニンジンの約3.33%・1/30',
                  f'{pc(D("poop"))}（1/{D("poop")}）', f'うんちの{pc(D("gold"))}・1/{D("gold")}', f'高確ゾーン {pc(D("high"))}（1/{D("high")}', f'幻の馬 {pc(D("mab"))}（1/{D("mab")}）', f'神様馬 {pc(D("kami"))}（1/{D("kami")}）']
        check(all(x in gd['text'] for x in wantTx) and gd['fit'] and [D(k) for k in ('poop', 'gold', 'high', 'mab', 'kami')] == [7, 20, 50, 245, 399],
              f"説明書：合わせた ％・ルーレット 50%・チケットの 枚数・ハートの 抽選・呼ぶ・金のニンジン・うんち・金のうんち・高確ゾーン・幻の馬・神様馬（左の 欄に おさまる {gd['fit']}・ない もの {[x for x in wantTx if x not in gd['text']]}）")
        od = pg.evaluate("() => [TCApp._t.ODDS.trashMin, TCApp._t.ODDS.trashN]")
        check(od == [15, 5] and all(x in gd['text'] for x in ['15分ごとにゴミが5か所に散らばる', '片付けるまで次のゴミは出ない', 'おそうじできるのはゴミかうんちがあるときだけ', 'ちりとりへ はき入れよう']) and 'うんちがない時は落ち葉' not in gd['text'],
              f'説明書：おそうじは「15分ごとに ゴミが 5か所」「ゴミか うんちが ある とき だけ」「ちりとりへ はき入れる」（きまりの 数 {od} と 同じ・前の「3回はく・落ち葉」は ない）')
        #   第4.144版（11/10 18:19 まさちゃん「この仕組みもトレーニングセンターの説明書に記載して！」）：「馬のリセット（次の馬の抽選）」の 項目・2分ごとの チャンスは 高確ゾーン だけ
        g2 = pg.evaluate("() => { const s = [...document.querySelectorAll('#tcg .sec')].map(x => [x.querySelector('h3').textContent, x.textContent]); const f = k => (s.find(x => x[0].includes(k)) || [0, ''])[1]; return { tick: f('2分ごとのチャンス'), reset: f('馬のリセット'), visit: f('幻の馬・神様馬がいるあいだ'), heads: s.map(x => x[0]) }; }")
        check('幻の馬' not in g2['tick'] and '神様馬' not in g2['tick'] and '高確ゾーン' in g2['tick'] and '幻の馬' in g2['reset'] and '神様馬' in g2['reset'] and '10分' not in g2['visit'] and len(g2['heads']) == 11
              and g2['heads'].index('替馬のリセット（次の馬の抽選）') == g2['heads'].index('★2分ごとのチャンス') + 1,
              f"説明書：「馬のリセット（次の馬の抽選）」の 項目が ある・幻の馬／神様馬の 抽選は そこに 書く（2分ごとの チャンスは 高確ゾーン だけ）・「いるのは10分」は ない（{g2['heads']}）")
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
        # 第4.144版（11/10 18:04 まさちゃん「馬のリセットは5分に切り替えよう！…最低5回お世話をした段階でリセットタイマーが作動して(お世話をしてる間はリセットなし)5分経ったらリセット。
        #   …開きっぱなしでもお世話の操作をしない限りは馬は変わらないでいて！ただ、幻の馬と神様馬は…開いてから30分経過すると切り替わる仕組みにして！
        #   幻の馬と神様馬は、上のバナーの下に切り替わる条件を表示して！・タイムリミット・お世話の回数 お世話5回完了後の切り替わりタイマー」・18:13「幻の馬と神様馬も最低5回お世話完了後はリセットタイマー作動で5分でリセットね！」）
        print('■ 馬の リセット（第4.144版）')
        RS = "() => { const st = TCApp.state, v = TCCare.S.vinfo; return { rs: Object.assign({}, st.rs), visit: st.visit ? st.visit.kind : null, left: st.visit ? Math.round((st.visit.until - Date.now()) / 1000) : null, vinfo: v ? { n: v.n, need: v.need, left: Math.round(v.left), timer: v.timer == null ? null : Math.round(v.timer) } : null, rows: v ? TCCare.vinfoRows(v).map(r => [r[0], r[1], r[2]]) : null, box: TCCare.vinfoBox(), msg: document.querySelector('#tcOv .tcmsg').textContent, msgOn: document.querySelector('#tcOv .tcmsg').classList.contains('on') }; }"
        od = pg.evaluate("() => { const o = TCApp._t.ODDS; return [o.resetCares, o.resetMin, o.visitMin, o.tick, Math.round(1 / o.mab), Math.round(1 / o.kami)]; }")
        check(od == [5, 5, 30, 120, 245, 399], f'きまりの 数：お世話 5回 → タイマー 5分・幻の馬／神様馬の タイムリミット 30分・抽選は 幻の馬 1/245・神様馬 1/399（{od}）')
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
        check(v0['visit'] == 'kamisama' and 1780 <= v0['left'] <= 1800 and v0['rs']['n'] == 0 and v0['rs']['at'] == 0 and '神様馬が やってきた' in v0['msg']
              and v0['rows'][0][0] == 'タイムリミット' and v0['rows'][0][1].startswith('29:') and v0['rows'][1][:2] == ['お世話', '0/5回'] and v0['rows'][2][:2] == ['切り替わりタイマー', '5回で スタート'],
              f'リセットの 抽選で 神様馬が やってくる・タイムリミット 30分・バナーの 下に「タイムリミット 29:xx／お世話 0/5回／切り替わりタイマー 5回で スタート」（{v0["rows"]}）')
        #   場所と 大きさ：11/10 18:31 まさちゃん「馬と被らないようにもっと上にして！あと、テロップもう少し大きさ小さくして…大きいと背景も分かりにくい！」
        #   → 18:44「リセット条件バナーの下から左上のハートのトークンの下に表示するようにして！」：左上の なかよしの 板の すぐ 下・左そろえ・小さく（420×125）。バナーは その 下
        bx = v0['box']; gz = bx['gauge'] if bx else None
        check(bx and gz == [26, 34, 600, 126] and bx['x'] == gz[0] and gz[1] + gz[3] < bx['y'] <= gz[1] + gz[3] + 20 and bx['x'] + bx['w'] <= gz[0] + gz[2] and bx['w'] <= 460 and bx['h'] <= 130
              and bx['banTop'] == 290 and bx['y'] + bx['h'] <= bx['banTop'] + 17 and bx['y'] + bx['h'] <= 300,
              f'条件の 札は 左上の なかよしの 板の すぐ 下（左そろえ・{bx["w"]}×{bx["h"]}・上 {bx["y"]}〜下 {bx["y"] + bx["h"]}）・バナー（上 {bx["banTop"]}）は その 下で 重ならない（はじめは バナーの 下 640×180・606〜786）')
        pg.evaluate("() => { TCApp.state.rs.n = 3; }"); pg.wait_for_timeout(500); v1 = pg.evaluate(RS)
        pg.evaluate("() => { TCApp.state.rs.n = 7; }"); pg.wait_for_timeout(800); v2 = pg.evaluate(RS)
        check(v1['rows'][1][1] == '3/5回' and v1['rows'][2][1] == '5回で スタート' and v2['rows'][1][1] == '5/5回' and v2['rows'][2][1] in ('5:00', '4:59') and v2['vinfo']['timer'] >= 298,
              f'お世話 3回 → 3/5回・5回 こえたら 5/5回で タイマーが 動く（{v1["rows"][1][1]}・{v2["rows"][1][1]}・{v2["rows"][2][1]}）')
        pg.evaluate("() => { const st = TCApp.state; st.rs.at = Date.now() - (4 * 60 + 15) * 1000; st.visit.until = Date.now() + 50 * 1000; }"); pg.wait_for_timeout(600); v3 = pg.evaluate(RS)
        check(v3['rows'][2][1] in ('0:45', '0:44') and v3['rows'][2][2] is True and v3['rows'][0][1] in ('0:50', '0:49') and v3['rows'][0][2] is True, f'のこり 1分は 赤（タイマー {v3["rows"][2][1]}・タイムリミット {v3["rows"][0][1]}）')
        #   幻の馬・神様馬も お世話 5回の あと 5分で リセット（→ 抽選：いつもの 馬に もどる）
        pg.evaluate("() => { TCApp._t.force(null); const st = TCApp.state; st.visit.until = Date.now() + 20 * 60000; st.rs.at = Date.now() - 6 * 60000; }")
        pg.wait_for_function("() => !TCApp.state.visit", timeout=30000); pg.wait_for_timeout(2500)
        v4 = pg.evaluate(RS)
        check(v4['visit'] is None and v4['rs'] == {'n': 0, 'at': 0, 'el': 0} and '帰って いったよ' in v4['msg'] and v4['vinfo'] is None and v4['box'] is None,
              f'神様馬も お世話 5回の あと 5分で リセット → いつもの 馬に もどる・条件の 札は 消える（{v4["msg"]!r}・{v4["rs"]}）')
        #   タイムリミット（来てから 30分）：お世話を しなくても 帰る
        pg.evaluate("() => TCApp._t.startVisit('maboroshi')"); pg.wait_for_function("() => TCCare.vinfoBox() && TCCare.S.vinfo", timeout=60000); pg.wait_for_timeout(800)
        m0 = pg.evaluate(RS)
        pg.evaluate("() => { const st = TCApp.state; st.rs.n = 2; st.visit.until = Date.now() - 1000; }")
        pg.wait_for_function("() => !TCApp.state.visit", timeout=30000); pg.wait_for_timeout(2500)
        m1 = pg.evaluate(RS)
        check(m0['visit'] == 'maboroshi' and m0['rows'][0][1].startswith('29:') and m1['visit'] is None and m1['rs'] == {'n': 0, 'at': 0, 'el': 0} and '帰って いったよ' in m1['msg'],
              f'幻の馬：タイムリミット（30分）で 帰る（お世話を して いなくても）・数えは 0 から（{m0["rows"][0]}・{m1["rs"]}）')
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
            c3.close()
        b.close()
finally:
    srv.terminate()
print('NG' if fails else 'OK', len(fails), fails)
sys.exit(1 if fails else 0)
