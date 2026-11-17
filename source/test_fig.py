# 思い出フィギュア（第4.134版）の テスト：App Store版（TARGET=app）を localhost で アプリ版として 開いて、思い出のレース → フィギュアを 作る → ブースに 飾る → 部屋 → 一覧
#   第4.138版：右上の 丸い ボタン（トレーニングセンターの 下・名前の 札「思い出フィギュア」）→ フィギュアブース → 下の「＋ フィギュアを作る」→ 作る 画面 → もどる・ミッション（1つ・5つ・8つ 完成させる）
#   python3 test_fig.py   （ios/fig_assets/ が ある とき だけ 全部。ない とき（CI）は ボタンと 読みこめない ときの 形だけ）
import json, os, re, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv_fig'); PORT = 8796; APP = f'http://localhost:{PORT}/APP/'
SHOT = os.environ.get('SHOT')          # 画面を 写す フォルダ（見る 用）
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, TARGET='app'))
pth = os.path.join(SRV, 'APP', 'index.html'); html = open(pth, encoding='utf8').read()
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
from assets_dir import adir
FGA = adir('fig_assets'); HAVE = os.path.isdir(FGA) and len(os.listdir(FGA)) > 45      # 第4.176版：デザインが 5種に なって 56こ（前は 8種で 83こ）
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
  // 第4.170版：1つ目は 距離・コース・1着と 2着の 名前（pn）つき／2つ目は 距離も 名前も ない 記録（前の 版で 作った 記録と 同じ 形）
  const a = mk('figm1', 11, 'テンゲル記念', { '3連単': [[5, 2, 1], [5, 1, 2], [2, 5, 1]], '馬単': [[5, 2]] }, [5, 2, 1], 'nd', 1000, 45600);
  Object.assign(a, { dist: 1600, surface: 'ダ', pn: ['テンゲルいち', 'テンゲルに', ''] });
  await TengelLocal.putBets([a, mk('figm2', 9, 'はなまる特別', { '馬単': [[3, 7], [7, 3]] }, [8, 4, 6], 'miss', 600, 0)]);
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
        reqs = []; pg.on('request', lambda r: reqs.append(r.url.split('/')[-1].split('?')[0]))      # 読みに いった ファイルの 名前（第4.153版：棚の 形と 絵）
        pg.goto(APP); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(600)
        print('■ 入口')
        check(pg.evaluate("() => typeof window.TengelFig === 'object' && typeof TengelFig.booth === 'function' && typeof window.TengelMem === 'object' && !!TengelWallet.fig"), 'TengelFig（入口）・TengelMem（思い出のレース）・TengelWallet.fig（台帳）')
        # 第4.138版（11/10 09:45・09:55・09:57）：丸い ボタン（トレーニングセンターの 下）＋ 名前の 札「思い出フィギュア」
        #   第4.139版（11/10 11:32「アイコンが壁紙と重なってるから、右下に移動して！」）：列は 右下（下の タブの すぐ 上）。上から トレーニングセンター → 思い出フィギュア
        FAB = """() => { const R = e => e ? e.getBoundingClientRect() : null, t = document.querySelector('#tcFab'), f = document.querySelector('#figFab'), h = document.querySelector('header.top'), tb = document.querySelector('.tabbar');
          if (!t || !f || !h || !tb) return null; const a = R(t), c = R(f), l = f.querySelector('.fabl'), i = f.querySelector('.fabi'), q = R(l), ii = R(i);
          const cbf = R(document.querySelector('#cbFab'));
          return { hb: R(h).bottom, tab: R(tb).top, bottom: c.bottom, tcTop: a.top, tcBottom: a.bottom, tcCx: (a.left + a.right) / 2, top: c.top, right: c.right, cx: (c.left + c.right) / 2, name: l.textContent, lt: q.top, ib: ii.bottom, iw: ii.width, cbBottom: cbf ? cbf.bottom : null,
            aria: f.getAttribute('aria-label'), img: (i.querySelector('img') || {}).src || '' }; }"""
        #   第4.168版：列は 判定の 帯（#minibar）が 出ても 消えても 同じ 所（帯の 上の 高さ：test_tc.py）。ここは 帯を かくして 見る
        pg.evaluate("() => { const m = document.getElementById('minibar'); if (m) m.hidden = true; }"); pg.wait_for_timeout(600)
        fb = pg.evaluate(FAB)
        #   第4.176版（まさちゃん 11/16 00:47「①トレーニングセンター ②推し馬 ③カードバトル ④思い出フィギュア」）：たてに 4つの いちばん 下＝カードバトルの すぐ 下。丸は 画面に 合わせた 大きさ（ここは 上の絵が ない ので 66px）・
        #     01:15「この青四角下の空間気になる」：列の 下は 下の タブの すぐ 上（前は 判定の 帯の 上＝下の タブから 約43px 上）
        check(fb is not None and pg.locator('#figFab').is_visible() and fb['cbBottom'] is not None and 0 <= fb['top'] - fb['cbBottom'] <= 10 and fb['top'] > fb['tcBottom'] + 60 and abs(fb['cx'] - fb['tcCx']) < 1 and fb['right'] <= 390 and 3 <= fb['tab'] - fb['bottom'] <= 6 and fb['tcTop'] > fb['hb'] + 200,      # 第4.176版：列の 下は 下の タブの すぐ 上（帯が 出ても 消えても 動かない のは 同じ）
              f'右下の ボタン：列の 一番 下（カードバトルの すぐ 下・トレーニングセンターと 同じ 列）に 思い出フィギュア・その すぐ 下が 下の タブ（{fb and [round(fb["tcTop"]), round(fb["tcBottom"]), round(fb["top"]), round(fb["bottom"]), round(fb["tab"])]}）')
        check(fb is not None and fb['name'] == '思い出\nフィギュア' and fb['ib'] - 9 <= fb['lt'] <= fb['ib'] + 4 and abs(fb['iw'] - 66) < 1 and 'フィギュアブース' in fb['aria'], '絵（66px）の 下に 名前の 札「思い出／フィギュア」（2行）')
        pg.evaluate(SEED); pg.wait_for_timeout(800)
        pg.evaluate("() => { const b = document.querySelector('.tabbar [data-tab=rec]') || [...document.querySelectorAll('.tabbar button')].find(x => /記録/.test(x.textContent)); b.click(); }"); pg.wait_for_timeout(900)
        L = pg.evaluate("() => TengelMem.list()")
        # 第4.170版（まさちゃん 11/14 12:07・12:36）：ボードに 書く 文＝レース名／日付／出馬数・コース／1〜3着（馬番＋名前。名前が ない 着順は 馬番＋人気）／購入 → 回収。的中の 種類・買い目は 書かない
        check(len(L) == 2 and L[0]['id'] == 'figm1' and L[0]['info'] == {'v': 2, 'race': '11R　テンゲル記念', 'date': '2026年11月9日（月）', 'sub': '14頭・ダート 1,600m',
                                                                    'lines': ['1着　5番 テンゲルいち', '2着　2番 テンゲルに', '3着　1番（2番人気）'], 'money': '購入 1,000円 → 回収 45,600円'}
              and L[1]['info'] == {'v': 2, 'race': '9R　はなまる特別', 'date': '2026年11月8日（日）', 'sub': '14頭', 'lines': ['1着　8番（3番人気）', '2着　4番（1番人気）', '3着　6番（2番人気）'], 'money': '購入 600円 → 回収 0円'},
              f'思い出のレース 2つ・ボードに 書く 文（第4.170版の 形：的中の 種類・買い目は ない） {L[0]["info"] if L else None}')
        mf = pg.locator('#recList .memfig')
        check(mf.count() == 1 and 'フィギュアブース' in mf.inner_text() and 'フィギュアを作る' in mf.inner_text(), f'記録タブの 思い出のレースの 欄に「フィギュアブース」「フィギュアを作る」（{mf.inner_text() if mf.count() else ""}）')
        shot(pg, 'fig_rec')
        if not HAVE:
            pg.locator('#recList [data-act=figbooth]').click(); pg.wait_for_timeout(4000)
            check(pg.evaluate("() => !!window.FigApp && document.querySelector('#fgOv.on') !== null"), 'ブースは 開く（絵が ない ときは「読みこめなかった」の 知らせ）')
            check(not errs, f'エラー なし {errs[:2]}')
            raise SystemExit
        print('■ 右下の ボタン → フィギュアブース → フィギュアを作る → 戻る')
        check(pg.evaluate("() => { const im = document.querySelector('#figFab .fabi img'); return !!im && im.complete && im.naturalWidth === 240; }") and fb['img'].endswith('fg_icon.webp'), 'ボタンの 絵（fg_icon.webp・240×240）')
        pg.locator('#figFab').click(); pg.wait_for_function("() => !!window.FigApp", timeout=30000); wait_scene(pg)
        check(pg.evaluate("() => FigApp._t.mode") == 'booth' and pg.locator('#fgOv [data-fg=make]').is_visible() and 'フィギュアを作る' in pg.locator('#fgOv [data-fg=make]').inner_text(),
              '思い出フィギュアの ボタンを 押す → フィギュアブース（下に「＋ フィギュアを作る」）')
        # 第4.153版（まさちゃん 11/11 12:10「やって！」＝棚の 3D の 貼り方を 作り直して 軽く）：棚は 貼り直した 形（fg_shelf2.*・kisekae/fig/shelf_reuv.py）。前の fg_shelf.* は 読まない。
        #   絵の 左上の 大きな 島（fg_shelf2.json の front）＝正面から 見た 棚 そのもの → 画面の 棚（正面）と 同じ 見え方に なって いる はず（貼り方と 絵が 合って いる 確かめ）
        import base64 as _b64, io as _io, json as _js
        import numpy as _np
        from PIL import Image as _I
        mj = _js.load(open(os.path.join(FGA, 'fg_shelf2.json')))
        durl = pg.evaluate("() => { FigApp._t.draw(); return document.querySelector('#fgOv .fgst canvas').toDataURL('image/png'); }")
        cva = _np.asarray(_I.open(_io.BytesIO(_b64.b64decode(durl.split(',')[1]))).convert('RGBA'), _np.float32)
        ys, xs = _np.nonzero(cva[..., 3] > 128); bx = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1) if len(xs) else (0, 0, 1, 1)
        scr = _np.asarray(_I.fromarray(cva[..., :3].astype(_np.uint8)).crop(bx).resize((96, 128), _I.LANCZOS), _np.float32)
        fr = mj['front']; tex = _np.asarray(_I.open(os.path.join(FGA, 'fg_shelf2_c1.webp')).convert('RGB').crop((int(fr[0]), int(fr[1]), int(round(fr[2])), int(round(fr[3])))).resize((96, 128), _I.LANCZOS), _np.float32)
        cor = float(_np.corrcoef(scr.reshape(-1), tex.reshape(-1))[0, 1]); mad = float(_np.abs(scr - tex).mean()); asp = (bx[2] - bx[0]) / max(1, bx[3] - bx[1])
        old = [f for f in reqs if re.fullmatch(r'fg_shelf(\.json|\.bin|_c\d+\.webp)', f)]
        check('fg_shelf2.json' in reqs and 'fg_shelf2.bin' in reqs and 'fg_shelf2_c1.webp' in reqs and not old and mj['v'] < 65536 and cor > 0.93 and mad < 14 and 0.70 < asp < 0.82,
              f'第4.153版：棚は 貼り直した 形（fg_shelf2・頂点 {mj["v"]}）・前の 棚は 読まない {old}・正面の 棚は 絵の 大きな 島と 同じ 見え方（似かた {cor:.3f}・色の 差 平均 {mad:.1f}/255・たて横 {asp:.2f}）')
        shot(pg, 'fig_fab_booth')
        pg.locator('#fgOv [data-fg=make]').click(); pg.wait_for_timeout(500)
        check(pg.evaluate("() => [FigApp._t.mode, FigApp._t.mk.step, FigApp._t.mk.back].join()") == 'make,race,booth' and pg.locator('#fgOv .fgrace').count() == 2 and 'ブースへ' in pg.locator('#fgOv [data-fg=back]').inner_text(),
              'ブースの「＋ フィギュアを作る」→ 1. 思い出のレースを 選ぶ（2つ・「← ブースへ」）')
        pg.locator('#fgOv .fgrace').first.click(); pg.wait_for_timeout(600)
        check(pg.evaluate("() => FigApp._t.mk.step") == 'design' and pg.locator('#fgOv .fgd').count() == 5, '→ 2. デザインを 選ぶ（5種：第4.176版）')
        pg.locator('#fgOv [data-fg=back]').click(); pg.wait_for_timeout(300); pg.locator('#fgOv [data-fg=back]').click(); wait_scene(pg)
        check(pg.evaluate("() => FigApp._t.mode") == 'booth', '戻る → 戻る → ブース')
        pg.locator('#fgOv [data-fg=back]').click(); pg.wait_for_timeout(500)
        check(pg.evaluate("() => !document.querySelector('#fgOv').classList.contains('on')") and pg.locator('#figFab').is_enabled(), 'ブースを 閉じる → 元の 画面（ボタンは また 押せる）')
        print('■ 作る：レース → デザイン → 3D で 見る')
        # 第4.139版：ポイントの 上限は 99,999P。テストの 400,000P は 98,499P だけ 台帳に 入って、のこりは あずかりポイントに（足りなく なったら 作る ときに あずかりから 補充される）
        #   → 持って いる ポイントは「台帳＋あずかり」で 数える（ALL）
        ALL = "() => TengelWallet.total() + TengelWallet.hold().total"
        pg.evaluate("() => TengelWallet.grant('test-fig-pts', 400000, 'テスト')"); pg.wait_for_timeout(400)
        p0 = pg.evaluate(ALL)
        w0 = pg.evaluate("() => [TengelWallet.total(), TengelWallet.hold().free, TengelWallet.avail()]")
        check(p0 == 401500 and w0 == [99999, 301501, 99999], f'テストの ポイント：台帳は 上限の 99,999P・残り 301,501P は 預かり（{w0}）')
        pg.locator('#recList [data-act=figmake]').click()
        pg.wait_for_function("() => window.FigApp && FigApp._t.mode === 'make'", timeout=30000); pg.wait_for_timeout(500)
        check(pg.locator('#fgOv .fgrace').count() == 2 and 'デザインは 5種類' in pg.locator('#fgOv .fgmk .lead').inner_text(), '1. 思い出のレースを 選ぶ（2つ・「デザインは 5種類」）')
        shot(pg, 'fig_make_race')
        pg.locator('#fgOv .fgrace').first.click(); pg.wait_for_timeout(800)
        ds = pg.evaluate("() => [...document.querySelectorAll('#fgOv .fgd')].map(d => d.querySelector('.pr').textContent)")
        check(ds == ['22,000P'] * 4 + ['36,000P'], f'2. デザイン 5種と 値段（通常 22,000・幻の馬＆神様馬 36,000）{ds}')
        # 第4.176版（まさちゃん 11/15 21:53 → 11/16 00:07「間違えた！ 思い出フィギュアは、スタンプボードと神様馬ボードと幻の馬ボードを消して！ 神様馬&幻の馬ボードは残して！」）：
        #   番号 2（ゴールデンスカラー）・6（神様馬）・7（幻の馬）は ない。番号 8（幻の馬＆神様馬）は ある。出す 番号は ①〜⑤ に 詰める
        dn = pg.evaluate("() => [...document.querySelectorAll('#fgOv .fgd')].map(d => [+d.dataset.n, d.querySelector('b').textContent, d.querySelector('img').getAttribute('src')])")
        check(dn == [[1, '① ロイヤルポニー', 'fg1_t.webp'], [3, '② フローラルゴールド', 'fg3_t.webp'], [4, '③ ロイヤルゴールデン', 'fg4_t.webp'], [5, '④ ロイヤルフォーチュン', 'fg5_t.webp'], [8, '⑤ 幻の馬＆神様馬', 'fg8_t.webp']]
              and pg.evaluate("() => FigApp.LIST.join()") == '1,3,4,5,8' and pg.locator('#fgOv .fgd .kd.both').count() == 1 and pg.locator('#fgOv .fgd .kd').count() == 1, f'デザインは ①〜⑤（番号 1・3・4・5・8）：スタンプの ボード（番号 2）・神様馬（番号 6）・幻の馬（番号 7）は ない。幻の馬＆神様馬（番号 8）は ある {dn}')
        pg.wait_for_function("() => [...document.querySelectorAll('#fgOv .fgd img')].every(i => i.complete && i.naturalWidth > 0)", timeout=20000)
        shot(pg, 'fig_make_design')
        # ボードの 絵に 書いた 文字を 見る（キャンバスの fillText を のぞく）
        pg.evaluate("() => { const P = CanvasRenderingContext2D.prototype; window.__ft = []; window.__ft0 = P.fillText; P.fillText = function (t) { window.__ft.push(String(t)); return window.__ft0.apply(this, arguments); }; }")
        pg.locator('#fgOv .fgd[data-n="1"]').click(); wait_room(pg)
        ft = pg.evaluate("() => { CanvasRenderingContext2D.prototype.fillText = window.__ft0; return [...new Set(window.__ft)]; }")
        check(ft == ['11R　テンゲル記念', '2026年11月9日（月）　14頭・ダート 1,600m', '1着　5番 テンゲルいち', '2着　2番 テンゲルに', '3着　1番（2番人気）', '購入 1,000円 → 回収 45,600円'],
              f'第4.170版 ボードの 絵に 書く 行：レース名／日付・出馬数・コース（1行）／1着・2着・3着／購入 → 回収 {ft}')
        old = pg.evaluate("""() => { const P = CanvasRenderingContext2D.prototype, o = P.fillText, out = []; P.fillText = function (t) { out.push(String(t)); return o.apply(this, arguments); };
          const c = FigGL.boardCanvas({ kind: 'ど的中', race: '11R　テンゲル記念', date: '2026年11月9日（月）', lines: ['3連単　5 → 2 → 1　的中', '馬単　5 → 2　的中'], result: '1着 5（3番人気）・2着 2（1番人気）・3着 1（2番人気）', money: '購入 1,000円 → 回収 45,600円' }, 1.4, 'gold', 256);
          P.fillText = o; return { rows: [...new Set(out)], w: c.width }; }""")
        check(old['w'] == 256 and old['rows'] == ['ど的中', '11R　テンゲル記念', '2026年11月9日（月）', '3連単　5 → 2 → 1　的中', '馬単　5 → 2　的中', '1着 5（3番人気）・2着 2（1番人気）・3着 1（2番人気）', '購入 1,000円 → 回収 45,600円'],
              f'前の 版で 作った フィギュアの 文（的中の 種類・買い目・結果の 行の ある 形）は そのまま 描ける {old["rows"][:2]}')
        px = pg.evaluate("() => { const c = document.querySelector('#fgOv canvas'), g = c.getContext('webgl'), p = new Uint8Array(4); FigApp._t.need(); return [c.width, c.height]; }")
        check(px[0] > 100 and pg.locator('#fgOv [data-fg=buy1]').is_enabled(), f'3. 3D で 見る（キャンバス {px}）・作る ボタン')
        shot(pg, 'fig_make_prev')
        pg.locator('#fgOv [data-fg=buy1]').click(); pg.wait_for_timeout(200)
        check('22,000Pを使って作る' in pg.locator('#fgOv [data-fg=buy2]').inner_text(), 'もう一度 確かめる（22,000Pを使って作る）')
        pg.locator('#fgOv [data-fg=buy2]').click(); wait_scene(pg)
        it = pg.evaluate("() => TengelWallet.fig.items()")
        ev = pg.evaluate("() => TengelWallet.events().filter(e => /^unlock-fig:/.test(e.id)).map(e => [e.amount, e.what])")
        check(len(it) == 1 and it[0]['n'] == 1 and it[0]['info']['race'] == '11R　テンゲル記念' and it[0]['info'].get('v') == 2 and it[0]['info']['lines'][0] == '1着　5番 テンゲルいち' and it[0]['info']['sub'] == '14頭・ダート 1,600m' and pg.evaluate(ALL) == p0 - 22000 and pg.evaluate("() => TengelWallet.total()") == 99999 - 22000 and len(ev) == 1 and ev[0][0] == -22000,
              f'作った：ポイント −22,000（unlock-fig）・ボードの 文は 作った ときの まま {ev}')
        check(pg.evaluate("() => document.querySelector('#fgOv').classList.contains('pick') && /飾る 場所を 選んでね/.test(document.querySelector('#fgOv .fgf').textContent)"), 'ブースへ：飾る 場所を 選んでね')
        shot(pg, 'fig_pick')
        pg.evaluate("() => FigApp._t.tapSlot(0)"); wait_scene(pg)
        check(pg.evaluate("() => TengelWallet.fig.slots()[0]") == it[0]['id'], '上の 左に 飾った')
        check(pg.evaluate("() => TengelPoints.figMissions(TengelWallet.fig.items().length, TengelWallet.events()).map(m => m.claimable ? 1 : 0).join('')") == '100', '1つ 作った → ミッション「思い出フィギュアを1つ完成させる」が 受け取れる（5つ・8つは まだ）')
        print('■ 8体 作って 飾る（デザイン 5種 全部 ＋ 同じ デザインを もう 3体）')
        ORDER = [3, 4, 5, 8, 1, 3, 4]              # 1体目（番号 1）の あと：上から 2つ目の 場所から 順に 飾る → 5つ目の 場所が 幻の馬＆神様馬（番号 8）
        for k, n in enumerate(ORDER):
            pg.evaluate("() => FigApp.make({ race: 'figm" + ('2' if k % 2 else '1') + "' })"); pg.wait_for_timeout(500)
            pg.locator(f'#fgOv .fgd[data-n="{n}"]').click(); wait_room(pg, 180000)
            pg.locator('#fgOv [data-fg=buy1]').click(); pg.locator('#fgOv [data-fg=buy2]').click(); wait_scene(pg, 180000)
            pg.evaluate(f"() => FigApp._t.tapSlot({k + 1})"); wait_scene(pg, 180000)
        sl = pg.evaluate("() => TengelWallet.fig.slots().slice(0, 8).map(Boolean)")
        cost = sum([22000] * 7 + [36000])
        wl = pg.evaluate("() => [TengelWallet.total(), TengelWallet.hold().total, TengelWallet.events().filter(e => e.from === 'hold').length]")
        check(sl == [True] * 8 and pg.evaluate(ALL) == p0 - cost and wl[0] == 77999 and wl[1] == 133501 and wl[2] == 2 and wl[0] + wl[1] == 211500 and pg.evaluate("() => TengelWallet.fig.items().map(x => x.n).join()") == '1,3,4,5,8,1,3,4',
              f'8体 飾った・ポイントは 合計 −{cost:,}（{sl}）。台帳が 足りなく なった 2回は 預かりから 先に 補充してから 作れた（台帳 {wl[0]:,}P・預かり {wl[1]:,}P・補充 {wl[2]}回）')
        shot(pg, 'fig_booth1')
        print('■ 部屋（押すと 3D で 見る）')
        pg.evaluate("() => FigApp._t.tapSlot(4)"); wait_room(pg, 180000)
        check(pg.evaluate("() => FigApp._t.mode") == 'room' and pg.locator('#fgOv .fgt b').inner_text() == '⑤ 幻の馬＆神様馬', f'5つ目の 場所（⑤ 幻の馬＆神様馬）の 部屋（{pg.locator("#fgOv .fgt b").inner_text()}）')
        shot(pg, 'fig_room7')
        r = pg.locator('#fgOv .fgst').bounding_box()
        pg.mouse.move(r['x'] + 200, r['y'] + 300); pg.mouse.down(); pg.mouse.move(r['x'] + 120, r['y'] + 280, steps=6); pg.mouse.up(); pg.wait_for_timeout(1500)
        check(abs(pg.evaluate("() => FigApp._t.room.yaw")) > 5, f'指で まわる（yaw {pg.evaluate("() => FigApp._t.room.yaw"):.1f}）')
        shot(pg, 'fig_room7b')
        print('■ 場所を 変える・しまう')
        pg.locator('#fgOv [data-fg=move]').click(); wait_scene(pg)
        id7 = pg.evaluate("() => TengelWallet.fig.slots()[4]")
        pg.evaluate("() => FigApp._t.goPage(1)"); pg.wait_for_timeout(900); wait_scene(pg)
        pg.evaluate("() => FigApp._t.tapSlot(3)"); wait_scene(pg)
        s2 = pg.evaluate("() => TengelWallet.fig.slots()")
        check(s2[4] is None and s2[8 + 3] == id7, 'ブース 2 の 2段目 右へ 動かした')
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
        check(all(f'fg_shelf2_c{i}.webp' in reqs for i in range(1, 8)), '第4.153版：7つの ブースの 棚の 絵（fg_shelf2_c1〜7.webp）を 全部 読んだ')
        shot(pg, 'fig_over')
        pg.locator('#fgOv .fgoc[data-p="0"]').click(); wait_scene(pg)
        print('■ しまってある → 空きに 飾る')
        pg.evaluate("() => FigApp._t.tapSlot(4)"); pg.wait_for_timeout(600)
        check(pg.locator('#fgOv .fgsh.on .fgsr').count() == 1 and '⑤ 幻の馬＆神様馬' in pg.locator('#fgOv .fgsh .fgsr small').inner_text(), '空きを 押すと しまってある フィギュア（⑤ 幻の馬＆神様馬）')
        pg.locator('#fgOv .fgsh .fgsr').click(); wait_scene(pg)
        check(pg.evaluate("() => TengelWallet.fig.slots()[4]") == id7, '戻して 飾った')
        print('■ ポイントが 足りない')
        pg.evaluate("() => { window.__tot = TengelWallet.total; window.__av = TengelWallet.avail; TengelWallet.total = () => 1000; TengelWallet.avail = () => 1000; FigApp.make({ race: 'figm1' }); }"); pg.wait_for_timeout(500)
        pg.locator('#fgOv .fgd[data-n="8"]').click(); pg.wait_for_timeout(600)
        fb = pg.locator('#fgOv .fgbuy').inner_text()
        check('あと 35,000P 足りないよ' in fb and not pg.locator('#fgOv [data-fg=buy1]').is_enabled(), f'足りない ときは 作れない（{fb!r}）')
        pg.evaluate("() => { TengelWallet.total = window.__tot; TengelWallet.avail = window.__av; }")
        pg.locator('#fgOv [data-fg=back]').click(); pg.wait_for_timeout(300); pg.locator('#fgOv [data-fg=back]').click(); pg.wait_for_timeout(500)
        check(pg.evaluate("() => !document.querySelector('#fgOv').classList.contains('on')"), 'レースを 決めて 開いた ときは 戻るで 記録タブへ')
        pg.locator('#recList [data-act=figbooth]').click(); wait_scene(pg)
        print('■ 台帳・バックアップ')
        snap = pg.evaluate("() => TengelWallet.snapshot()")
        check(len(snap['figs']['items']) == 8 and len([x for x in snap['figs']['slots'] if x]) == 8, '自動バックアップ（台帳）に フィギュアと 置き場所')
        hist = pg.evaluate("() => TengelWallet.events().filter(e => /^unlock-fig:/.test(e.id)).length")
        check(hist == 8, f'ポイントの 記録に 8件（{hist}）')
        pg.locator('#fgOv [data-fg=back]').click(); pg.wait_for_timeout(800)
        check(pg.evaluate("() => !document.querySelector('#fgOv').classList.contains('on')") and 'フィギュアブース（8）' in pg.locator('#recList .memfig').inner_text(), '閉じると 記録タブの ボタンに（8）')
        # 第4.138版（11/10 10:50 まさちゃん「ミッション 思い出フィギュアを１つ完成させる 5000p／5つ完成させる 5000p／8つ完成させる 10000p」）
        print('■ ミッション（思い出フィギュアを 1つ・5つ・8つ 完成させる）')
        t0 = pg.evaluate("() => TengelWallet.total()")
        pg.locator('#msBtn').click(); pg.wait_for_timeout(500)
        ROWS = "() => [...document.querySelectorAll('#msFig .msrow')].map(r => [r.dataset.mid, r.querySelector('.mn').innerText.replace(/\\s+/g, ' ').trim(), r.querySelector('.md').innerText.trim(), !!r.querySelector('[data-pt=claim]')])"
        rows = pg.evaluate(ROWS)
        check(pg.locator('#msOv').count() == 1 and '思い出フィギュアミッション' in pg.locator('#msOv').inner_text() and '今 8個' in pg.locator('#msFig .hint').inner_text()
              and rows == [['mission-fig-1', '思い出フィギュアを1つ完成させる 5,000P', '受け取れるよ！', True], ['mission-fig-5', '思い出フィギュアを5つ完成させる 5,000P', '受け取れるよ！', True], ['mission-fig-8', '思い出フィギュアを8つ完成させる 10,000P', '受け取れるよ！', True]],
              f'ミッションの 窓に「思い出フィギュアミッション」：1つ 5,000P・5つ 5,000P・8つ 10,000P（8個 作った → 3つとも 受け取れる）{rows}')
        msn = pg.locator('#msOv .msn').inner_text()
        check(msn.replace('\n', '・') == '達成 3/35・受け取れるのが 4つ！' and pg.locator('#msHoldCard').is_visible() and '今 補充できるのは 22,000P' in pg.locator('#msHold').inner_text(),
              f'上は「達成 3/35」（第4.147版：壁紙の 枚数の 2行が 減って 37 → 35）・受け取れる 数は 4つ（フィギュアの 3つ＋預かりポイントの 補充）（{msn!r}）')
        pg.locator('#msFig [data-pt=claim][data-id="mission-fig-1"]').click(); pg.wait_for_timeout(800)
        e1 = pg.evaluate("() => TengelWallet.events().filter(e => /^mission-fig-/.test(e.id)).map(e => e.id + ':' + e.amount + ':' + e.bucket).join()")
        check(pg.evaluate("() => TengelWallet.total()") == t0 + 5000 and e1 == 'mission-fig-1:5000:free', f'「1つ完成させる」を 受け取る → +5,000P（もらったP・{e1}）')
        pg.locator('#msFig [data-pt=claim][data-id="mission-fig-5"]').click(); pg.wait_for_timeout(800)
        pg.locator('#msFig [data-pt=claim][data-id="mission-fig-8"]').click(); pg.wait_for_timeout(800)
        rows = pg.evaluate(ROWS)
        check(pg.evaluate("() => TengelWallet.total()") == t0 + 20000 and [r[2] for r in rows] == ['受け取り済み'] * 3 and not any(r[3] for r in rows) and pg.locator('#msFig [data-pt=claim]').count() == 0,
              f'5つ・8つも 受け取る → 合計 +20,000P・3つとも 受け取り済み（もう 受け取れない）')
        pg.locator('#msOv [data-ms=close]').click(); pg.wait_for_timeout(400)
        pg.evaluate("() => { const b = document.querySelector('.tabbar [data-tab=set]') || [...document.querySelectorAll('.tabbar button')].find(x => /設定/.test(x.textContent)); b.click(); }"); pg.wait_for_timeout(700)
        sm = pg.locator('#setMission').inner_text()
        check('思い出フィギュアのミッション' in sm and '思い出フィギュアを8つ完成させる' in sm and pg.locator('#setMission .msrow[data-mid="mission-fig-8"] .md').inner_text().strip() == '受け取り済み', '設定タブの ミッションにも「思い出フィギュアのミッション」')
        # ---------- 第4.176版：なくした デザイン（番号 2 ゴールデンスカラー・番号 6 神様馬・番号 7 幻の馬）----------
        print('■ 第4.176版：なくした デザインの 形と 絵は アプリに ない・読みに 行かない')
        gone_f = sorted(f for f in os.listdir(FGA) if re.match(r'fg[267][._]', f)); gone_r = sorted({f for f in reqs if re.match(r'fg[267][._]', f)})
        check(not gone_f and not gone_r and all(os.path.isfile(os.path.join(FGA, f'fg{n}{x}')) for n in (1, 3, 4, 5, 8) for x in ('.json', '.bin', '_c.webp', '_t.webp')),
              f'fg2…・fg6…・fg7… は アプリに 入れる フォルダに ない {gone_f[:3]}・画面は 読みに 行かなかった {gone_r[:3]}・残りの 5種（番号 8 も）は ある')
        print('■ 第4.176版：作って いた 人の フィギュアは 外して、使った ポイントを 返す（1体に 1回 だけ）')
        # 前の 版で 作った 台帳（番号 2 を 22,000P・番号 6 を 32,000P・番号 7 を 30,000P で 作って 飾って いた）を 読みこむ（自動バックアップから 戻す のと 同じ 入口）
        g0 = pg.evaluate("""async () => {
          const s = TengelWallet.snapshot(), base = s.figs.items[0], t0 = TengelWallet.total() + TengelWallet.hold().total, n0 = s.figs.items.length;
          const mk = (id, n, cost) => Object.assign(JSON.parse(JSON.stringify(base)), { id, n, cost });
          s.figs.items.push(mk('gone2', 2, 22000), mk('gone6', 6, 32000), mk('gone7', 7, 30000)); s.figs.slots[20] = 'gone2'; s.figs.slots[21] = 'gone6'; s.figs.slots[22] = 'gone7';
          s.events.push({ id: 'x-marker-176', kind: 'mission', bucket: 'free', amount: 0, at: new Date().toISOString(), what: 'テスト' });
          const tt = document.getElementById('toast'); if (tt) { tt.textContent = ''; tt.hidden = true; }
          await TengelWallet.restore(s);
          const ev = TengelWallet.events(), W2 = TengelWallet.snapshot();
          return { t0, n0, t1: TengelWallet.total() + TengelWallet.hold().total, items: TengelWallet.fig.items().map(x => x.id + ':' + x.n), raw: W2.figs.items.map(x => x.n).join(), s20: W2.figs.slots[20], s21: W2.figs.slots[21], s22: W2.figs.slots[22],
            back: ev.filter(e => /^back-fig:/.test(e.id)).map(e => [e.id, e.kind, e.bucket, (+e.amount || 0) + (+e.held || 0), e.what]), held: W2.hold.filter(h => /^back-fig:/.test(String(h.id))).length,
            toast: (document.getElementById('toast') || {}).textContent || '', again: await TengelWallet.goneFigBack(), t2: TengelWallet.total() + TengelWallet.hold().total };
        }""")
        check(g0['t1'] == g0['t0'] + 84000 and g0['t2'] == g0['t1'] and g0['again'] is None and len(g0['items']) == g0['n0'] and not any(x.endswith((':2', ':6', ':7')) for x in g0['items']) and any(x.endswith(':8') for x in g0['items'])
              and g0['raw'] == '1,3,4,5,8,1,3,4' and g0['s20'] is None and g0['s21'] is None and g0['s22'] is None
              and g0['back'] == [['back-fig:gone2', 'mission', 'free', 22000, 'なくなったフィギュア「ゴールデンスカラー」のポイントを返した'], ['back-fig:gone6', 'mission', 'free', 32000, 'なくなったフィギュア「神様馬」のポイントを返した'], ['back-fig:gone7', 'mission', 'free', 30000, 'なくなったフィギュア「幻の馬」のポイントを返した']]
              and 'なくなったフィギュア（ゴールデンスカラー・神様馬・幻の馬）の 84,000P を返したよ' in g0['toast'],
              f'番号 2・6・7 の フィギュアを 外した（飾って いた 場所は 空き）・+84,000P（22,000＋32,000＋30,000）・幻の馬＆神様馬（番号 8）は そのまま・もう一度 よんでも 返さない・お知らせ（{g0["t1"] - g0["t0"]}・{g0["back"]}・{g0["toast"][:40]}）')
        bs = [pg.evaluate("async ([n, c]) => await TengelWallet.fig.buy({ id: 'fx176_' + n, n: n, bet: 'figm1', info: {} }, c)", [n, c]) for n, c in ((2, 22000), (6, 32000), (7, 30000))]
        check(all(x == {'ok': False, 'why': 'bad'} for x in bs), f'なくした 番号（2・6・7）は もう 作れない（{bs}）')
        pg.wait_for_timeout(400)
        check(not errs, f'エラー なし {errs[:3]}')
finally:
    srv.terminate()
print('\n' + ('全部 OK' if not fails else f'NG {len(fails)}こ：' + ' / '.join(fails)))
sys.exit(1 if fails else 0)
