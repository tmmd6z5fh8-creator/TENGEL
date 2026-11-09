# 思い出フィギュア（第4.134版）の テスト：App Store版（TARGET=app）を localhost で アプリ版として 開いて、思い出のレース → フィギュアを 作る → ブースに 飾る → 部屋 → 一覧
#   python3 test_fig.py   （ios/fig_assets/ が ある とき だけ 全部。ない とき（CI）は ボタンと 読みこめない ときの 形だけ）
import json, os, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv_fig'); PORT = 8796; APP = f'http://localhost:{PORT}/APP/'
SHOT = os.environ.get('SHOT')          # 画面を 写す フォルダ（見る 用）
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, TARGET='app'))
pth = os.path.join(SRV, 'APP', 'index.html'); html = open(pth, encoding='utf8').read()
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
FGA = os.path.join(W, 'ios', 'fig_assets'); HAVE = os.path.isdir(FGA) and len(os.listdir(FGA)) > 60
if HAVE:
    for f in os.listdir(FGA): shutil.copy(os.path.join(FGA, f), os.path.join(SRV, 'APP', f))
else:
    print('※ 思い出フィギュアの 形と 絵（ios/fig_assets）が ない ので、ボタンと 読みこめない 形だけ')
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
# 思い出のレース 2つ（予約した 買い目・結果が 決まって いる・思い出の しるし）
SEED = """async () => {
  const mk = (id, r, rname, bets, res, fx, stake, pay) => ({ id, date: '2026-11-0' + (r === 11 ? '9' : '8'), venue: '', r, rname, n: 14, types: Object.keys(bets),
    n1: res[0], n2: res[1], n3: res[2], p1: 3, p2: 1, p3: 2, stake: String(stake), payout: String(pay), horses: [],
    rsv: { state: 'done', types: Object.keys(bets), bets, result: { p: [[res[0]], [res[1]], [res[2]]] }, fx, at: new Date().toISOString() },
    mem: { at: new Date().toISOString(), v: 'a' } });
  await TengelLocal.putBets([mk('figm1', 11, 'テンゲル記念', { '3連単': [[5, 2, 1], [5, 1, 2], [2, 5, 1]], '馬単': [[5, 2]] }, [5, 2, 1], 'nd', 1000, 45600),
    mk('figm2', 9, 'はなまる特別', { '馬単': [[3, 7], [7, 3]] }, [8, 4, 6], 'miss', 600, 0)]);
}"""


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


def shot(pg, name):
    if SHOT: os.makedirs(SHOT, exist_ok=True); pg.screenshot(path=os.path.join(SHOT, name + '.png'))


def wait_scene(pg, t=120000):          # ブースの 絵が 出るまで（よみこみ中が 消える）→ 1コマ 書いて 待つ（写真が まっ黒に ならない ように）
    pg.wait_for_function("() => FigApp._t.mode === 'booth' && document.querySelector('#fgOv .fgld').hidden", timeout=t); pg.wait_for_timeout(600)
    pg.evaluate("() => FigApp._t.draw()"); pg.wait_for_timeout(400)


def wait_room(pg, t=120000):
    pg.wait_for_function("() => FigApp._t.room && FigApp._t.room.F && document.querySelector('#fgOv .fgld').hidden", timeout=t); pg.wait_for_timeout(1700)


try:
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo')
        ctx.add_init_script(FAKE)
        pg = ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(APP); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(600)
        print('■ 入口')
        check(pg.evaluate("() => typeof window.TengelFig === 'object' && typeof TengelFig.booth === 'function' && typeof window.TengelMem === 'object' && !!TengelWallet.fig"), 'TengelFig（入口）・TengelMem（思い出のレース）・TengelWallet.fig（台帳）')
        pg.evaluate(SEED); pg.wait_for_timeout(800)
        pg.evaluate("() => { const b = document.querySelector('.tabbar [data-tab=rec]') || [...document.querySelectorAll('.tabbar button')].find(x => /記録/.test(x.textContent)); b.click(); }"); pg.wait_for_timeout(900)
        L = pg.evaluate("() => TengelMem.list()")
        check(len(L) == 2 and L[0]['id'] == 'figm1' and L[0]['info']['race'] == '11R　テンゲル記念' and L[0]['info']['lines'][0].startswith('3連単') and '的中' in L[0]['info']['lines'][0]
              and L[0]['info']['money'] == '購入 1,000円 → 回収 45,600円' and L[1]['info']['kind'] == 'ハズレ', f'思い出のレース 2つ・ボードに 書く 文 {L[0]["info"] if L else None}')
        mf = pg.locator('#recList .memfig')
        check(mf.count() == 1 and 'フィギュアブース' in mf.inner_text() and 'フィギュアを作る' in mf.inner_text(), f'記録タブの 思い出のレースの 欄に「フィギュアブース」「フィギュアを作る」（{mf.inner_text() if mf.count() else ""}）')
        shot(pg, 'fig_rec')
        if not HAVE:
            pg.locator('#recList [data-act=figbooth]').click(); pg.wait_for_timeout(4000)
            check(pg.evaluate("() => !!window.FigApp && document.querySelector('#fgOv.on') !== null"), 'ブースは ひらく（絵が ない ときは「読みこめなかった」の 知らせ）')
            check(not errs, f'エラー なし {errs[:2]}')
            raise SystemExit
        print('■ 作る：レース → デザイン → 3D で 見る')
        pg.evaluate("() => TengelWallet.grant('test-fig-pts', 400000, 'テスト')"); pg.wait_for_timeout(300)
        p0 = pg.evaluate("() => TengelWallet.total()")
        pg.locator('#recList [data-act=figmake]').click()
        pg.wait_for_function("() => window.FigApp && FigApp._t.mode === 'make'", timeout=30000); pg.wait_for_timeout(500)
        check(pg.locator('#fgOv .fgrace').count() == 2, '1. 思い出のレースを 選ぶ（2つ）')
        shot(pg, 'fig_make_race')
        pg.locator('#fgOv .fgrace').first.click(); pg.wait_for_timeout(800)
        ds = pg.evaluate("() => [...document.querySelectorAll('#fgOv .fgd')].map(d => d.querySelector('.pr').textContent)")
        check(ds == ['22,000P'] * 5 + ['32,000P', '30,000P', '36,000P'], f'2. デザイン 8種と 値段（通常 22,000・神様馬 32,000・幻の馬 30,000・両方 36,000）{ds}')
        pg.wait_for_function("() => [...document.querySelectorAll('#fgOv .fgd img')].every(i => i.complete && i.naturalWidth > 0)", timeout=20000)
        shot(pg, 'fig_make_design')
        pg.locator('#fgOv .fgd[data-n="1"]').click(); wait_room(pg)
        px = pg.evaluate("() => { const c = document.querySelector('#fgOv canvas'), g = c.getContext('webgl'), p = new Uint8Array(4); FigApp._t.need(); return [c.width, c.height]; }")
        check(px[0] > 100 and pg.locator('#fgOv [data-fg=buy1]').is_enabled(), f'3. 3D で 見る（キャンバス {px}）・作る ボタン')
        shot(pg, 'fig_make_prev')
        pg.locator('#fgOv [data-fg=buy1]').click(); pg.wait_for_timeout(200)
        check('22,000Pを使って作る' in pg.locator('#fgOv [data-fg=buy2]').inner_text(), 'もう一度 たしかめる（22,000Pを使って作る）')
        pg.locator('#fgOv [data-fg=buy2]').click(); wait_scene(pg)
        it = pg.evaluate("() => TengelWallet.fig.items()")
        ev = pg.evaluate("() => TengelWallet.events().filter(e => /^unlock-fig:/.test(e.id)).map(e => [e.amount, e.what])")
        check(len(it) == 1 and it[0]['n'] == 1 and it[0]['info']['race'] == '11R　テンゲル記念' and pg.evaluate("() => TengelWallet.total()") == p0 - 22000 and len(ev) == 1 and ev[0][0] == -22000,
              f'作った：ポイント −22,000（unlock-fig）・ボードの 文は 作った ときの まま {ev}')
        check(pg.evaluate("() => document.querySelector('#fgOv').classList.contains('pick') && /飾る 場所を 選んでね/.test(document.querySelector('#fgOv .fgf').textContent)"), 'ブースへ：飾る 場所を 選んでね')
        shot(pg, 'fig_pick')
        pg.evaluate("() => FigApp._t.tapSlot(0)"); wait_scene(pg)
        check(pg.evaluate("() => TengelWallet.fig.slots()[0]") == it[0]['id'], '上の 左に 飾った')
        print('■ 8体 ぜんぶ 作って 飾る')
        for n in range(2, 9):
            pg.evaluate("() => FigApp.make({ race: 'figm" + ('2' if n % 2 else '1') + "' })"); pg.wait_for_timeout(500)
            pg.locator(f'#fgOv .fgd[data-n="{n}"]').click(); wait_room(pg, 180000)
            pg.locator('#fgOv [data-fg=buy1]').click(); pg.locator('#fgOv [data-fg=buy2]').click(); wait_scene(pg, 180000)
            pg.evaluate(f"() => FigApp._t.tapSlot({n - 1})"); wait_scene(pg, 180000)
        sl = pg.evaluate("() => TengelWallet.fig.slots().slice(0, 8).map(Boolean)")
        cost = sum([22000] * 5 + [32000, 30000, 36000])
        check(sl == [True] * 8 and pg.evaluate("() => TengelWallet.total()") == p0 - cost, f'8体 飾った・ポイントは 合計 −{cost:,}（{sl}）')
        shot(pg, 'fig_booth1')
        print('■ 部屋（押すと 3D で 見る）')
        pg.evaluate("() => FigApp._t.tapSlot(6)"); wait_room(pg, 180000)
        check(pg.evaluate("() => FigApp._t.mode") == 'room' and '幻の馬' in pg.locator('#fgOv .fgt b').inner_text(), '7番目（幻の馬）の 部屋')
        shot(pg, 'fig_room7')
        r = pg.locator('#fgOv .fgst').bounding_box()
        pg.mouse.move(r['x'] + 200, r['y'] + 300); pg.mouse.down(); pg.mouse.move(r['x'] + 120, r['y'] + 280, steps=6); pg.mouse.up(); pg.wait_for_timeout(1500)
        check(abs(pg.evaluate("() => FigApp._t.room.yaw")) > 5, f'指で まわる（yaw {pg.evaluate("() => FigApp._t.room.yaw"):.1f}）')
        shot(pg, 'fig_room7b')
        print('■ 場所を かえる・しまう')
        pg.locator('#fgOv [data-fg=move]').click(); wait_scene(pg)
        id7 = pg.evaluate("() => TengelWallet.fig.slots()[6]")
        pg.evaluate("() => FigApp._t.goPage(1)"); pg.wait_for_timeout(900); wait_scene(pg)
        pg.evaluate("() => FigApp._t.tapSlot(3)"); wait_scene(pg)
        s2 = pg.evaluate("() => TengelWallet.fig.slots()")
        check(s2[6] is None and s2[8 + 3] == id7, 'ブース 2 の 2段目 右へ 動かした')
        shot(pg, 'fig_booth2')
        pg.evaluate("() => FigApp._t.tapSlot(3)"); wait_room(pg, 180000)
        pg.locator('#fgOv [data-fg=unplace]').click(); pg.wait_for_timeout(600)
        check(pg.evaluate("() => TengelWallet.fig.slots().filter(Boolean).length") == 7 and pg.locator('#fgOv [data-fg=place]').count() == 1, 'しまった（部屋に「ブースに飾る」）')
        pg.locator('#fgOv [data-fg=back]').click(); wait_scene(pg)
        check('しまってある（1）' in pg.locator('#fgOv .fgf').inner_text(), 'しまってある（1）')
        print('■ 一覧（7つの ブース）')
        pg.locator('#fgOv [data-fg=over]').click()
        pg.wait_for_function("() => { const c = document.querySelectorAll('#fgOv .fgoc canvas'); if (c.length !== 7) return false; const g = c[6].getContext('2d'); return g.getImageData(150, 200, 1, 1).data[3] > 0; }", timeout=240000)
        o = pg.evaluate("() => [...document.querySelectorAll('#fgOv .fgoc small')].map(x => x.textContent)")
        a = pg.evaluate("() => { const c = document.querySelector('#fgOv .fgoc canvas'), g = c.getContext('2d'); const d = g.getImageData(0, 0, c.width, c.height).data; let n = 0; for (let i = 3; i < d.length; i += 4) if (d[i] > 0) n++; return n / (c.width * c.height); }")
        check(o == ['7 / 8'] + ['0 / 8'] * 6 and a > 0.5, f'7つの ブースの 写真・数（{o}・うまって いる 割合 {a:.2f}）')
        check('7 / 56' in pg.locator('#fgOv .fgos').inner_text(), '飾っている フィギュア 7 / 56')
        shot(pg, 'fig_over')
        pg.locator('#fgOv .fgoc[data-p="0"]').click(); wait_scene(pg)
        print('■ しまってある → 空きに 飾る')
        pg.evaluate("() => FigApp._t.tapSlot(6)"); pg.wait_for_timeout(600)
        check(pg.locator('#fgOv .fgsh.on .fgsr').count() == 1, '空きを 押すと しまってある フィギュア')
        pg.locator('#fgOv .fgsh .fgsr').click(); wait_scene(pg)
        check(pg.evaluate("() => TengelWallet.fig.slots()[6]") == id7, 'もどして 飾った')
        print('■ ポイントが 足りない')
        pg.evaluate("() => { window.__tot = TengelWallet.total; TengelWallet.total = () => 1000; FigApp.make({ race: 'figm1' }); }"); pg.wait_for_timeout(500)
        pg.locator('#fgOv .fgd[data-n="8"]').click(); pg.wait_for_timeout(600)
        fb = pg.locator('#fgOv .fgbuy').inner_text()
        check('あと 35,000P 足りないよ' in fb and not pg.locator('#fgOv [data-fg=buy1]').is_enabled(), f'足りない ときは 作れない（{fb!r}）')
        pg.evaluate("() => { TengelWallet.total = window.__tot; }")
        pg.locator('#fgOv [data-fg=back]').click(); pg.wait_for_timeout(300); pg.locator('#fgOv [data-fg=back]').click(); pg.wait_for_timeout(500)
        check(pg.evaluate("() => !document.querySelector('#fgOv').classList.contains('on')"), 'レースを 決めて 開いた ときは もどるで 記録タブへ')
        pg.locator('#recList [data-act=figbooth]').click(); wait_scene(pg)
        print('■ 台帳・バックアップ')
        snap = pg.evaluate("() => TengelWallet.snapshot()")
        check(len(snap['figs']['items']) == 8 and len([x for x in snap['figs']['slots'] if x]) == 8, '自動バックアップ（台帳）に フィギュアと 置き場所')
        hist = pg.evaluate("() => TengelWallet.events().filter(e => /^unlock-fig:/.test(e.id)).length")
        check(hist == 8, f'ポイントの 記録に 8件（{hist}）')
        pg.locator('#fgOv [data-fg=back]').click(); pg.wait_for_timeout(800)
        check(pg.evaluate("() => !document.querySelector('#fgOv').classList.contains('on')") and 'フィギュアブース（8）' in pg.locator('#recList .memfig').inner_text(), '閉じると 記録タブの ボタンに（8）')
        check(not errs, f'エラー なし {errs[:3]}')
finally:
    srv.terminate()
print('\n' + ('全部 OK' if not fails else f'NG {len(fails)}こ：' + ' / '.join(fails)))
sys.exit(1 if fails else 0)
