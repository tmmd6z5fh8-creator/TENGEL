# 馬カードバトルの「決戦調査」（第4.196版・まさちゃん 2026/11/18 15:09）の 画面の テスト：App Store版（TARGET=app）を localhost で アプリ版として 開く
#   ・メニューの「⚔️ 決戦調査」→ マップ（エリア 1 だけ 開いて いる・ほかは 鍵）→ エリアを タップ → その 場に ふきだし（まさちゃん 16:47：開いて いる →「決戦調査に 行く」／「もどる」・鍵／討伐済み → わけ と「もどる」・マップは 見えた まま）
#   ・フィールド：セリフ（字が 1つずつ・タップで ぜんぶ → 次へ）→ テロップ「レベル○の 敵 出現！」→ 敵（蹄の 線が フィールドの 決めた 高さ）→ 名前 →「タップで バトル開始！」
#   ・バトル：上は 敵HP ゲージ（盾の 中に 顔・名前・HP のこま：赤い 帯は 枠の 中に ぴったり〈角も 枠と 同じ 形〉）・「ターン」は 出ない・相手の 名前は 敵の 短い 名前・BGM は 決戦調査の 曲（フィールドでは 止まる）
#   ・勝ち → HP が へる（あいだの 窓「第2戦へ」）→ 討伐（勝利の 演出 3段階・バトルコイン GET）→ マップ（次の エリアが 開く・討伐の はんこ）
#   ・同点 → 同じ 戦を やり直し（HP は そのまま）／負け → 調査 失敗（もう 一度 → HP は 満タン）／とちゅうで やめる → マップ（ミッションの 連勝 0・いつもの 負けには 数えない）
#   ・確定カード（レベル 5〜12：決まった 戦で 敵の 手札に かならず）・ミッション（コンピュータに 連続勝利）は 数える・いつもの 勝ち負け・連勝・お世話トークン・いつもの コインは かわらない
#   ・毎月 1日に リセット・戦の とちゅうで 月が かわった・戦の とちゅうで アプリを 閉じた（つぎに 開いた とき 調査 失敗）・テスト版の 道具（1ターンで 勝てる 手札 など）
#   python3 test_cb_quest.py   （SHOT=<フォルダ> で 画面を 写す。ios/cb_assets/ が ない とき（CI）は 絵の 確かめを とばす）
import json, os, re, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W); sys.path.insert(0, os.path.join(W, 'kisekae'))
SRV = os.path.join(W, 'srv_cbq'); PORT = 8815; APP = f'http://localhost:{PORT}/APP/'
SHOT = os.environ.get('SHOT')
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, TARGET='app'))
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'TST')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, TARGET='app', TENGEL_TEST='1'))      # テスト版（道具 あり）
for d in ('APP', 'TST'):
    pth = os.path.join(SRV, d, 'index.html'); html = open(pth, encoding='utf8').read()
    open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
import cb_art, cb_sfx, cb_quest_art
CBA = os.path.join(W, 'ios', 'cb_assets'); CBF = cb_art.files() + cb_sfx.files()
HAVE = all(os.path.isfile(os.path.join(CBA, f)) for f in CBF)
if HAVE:
    for d in ('APP', 'TST'):
        for f in CBF: shutil.copy(os.path.join(CBA, f), os.path.join(SRV, d, f))
else:
    print('※ 馬カードバトルの 絵と 音（ios/cb_assets）が ない ので、絵の 確かめは とばす（画面は 動く）')
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c: fails.append(label)


FAKE = open(os.path.join(W, 'test_cb.py'), encoding='utf8').read().split('FAKE = """')[1].split('"""')[0]      # アプリの 窓口の にせもの（test_cb.py と 同じ）
OPP = """a => { const m = CBApp._t.match, S = m._.state(), h = S.p[1].hand, b = Object.assign({}, a); if (b.k != null) { b.u = h.find(x => x.k === String(b.k)).u; delete b.k; } return m._.apply(1, b); }"""
# 1ターンの 戦の 手札（あなた／敵）：勝つ・負ける・同点（相手の カードは OPP で 決める）
WIN = [['k', '1', '2', '3', '4', '5', '6'], ['7', '7', '6', '2', '3', '1', 'm']]
LOSE = [['7', '6', '5', '4', '3', '2', '1'], ['k', 'm', '1', '1', '2', '3', '6']]
DRAW = [['k', '1', '2', '3', '4', '5', '6'], ['m', '7', '7', '6', '2', '3', '1']]


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


def idle(pg, t=30000):
    pg.wait_for_function("() => window.CBApp && CBApp._t.idle", timeout=t); pg.wait_for_timeout(60)


def open_cb(pg, speed=0.03):
    pg.locator('#cbFab .fabi').click()
    pg.wait_for_function("() => !!window.CBApp && !!document.querySelector('#cbOv.on')", timeout=30000)
    pg.evaluate(f"() => {{ CBApp._t.speed({speed}); CBApp._guard = 0; CBApp._think = () => 1e9; CBApp._now = () => new Date(window.__now || '2026-11-18T12:00:00'); }}"); pg.wait_for_timeout(150)
    pg.evaluate("""() => { if (window.__said) return; window.__said = [];
      const W = (sel, tag) => { const e = document.querySelector('#cbOv ' + sel); let last = ''; new MutationObserver(() => { const s = e.classList.contains('on') ? e.textContent : ''; if (s && s !== last) window.__said.push(tag + ':' + s); last = s; }).observe(e, { attributes: true, childList: true, subtree: true, characterData: true }); };
      W('.cbban', 'ban'); W('.cbtoast', 'toast'); }""")


def said(pg):
    return pg.evaluate("() => { const a = window.__said.slice(); window.__said.length = 0; return a; }")


def st(pg):
    return pg.evaluate("() => JSON.parse(JSON.stringify(CBApp._t.state))")


def q(pg):
    return pg.evaluate("() => { const x = CBApp._t.quest; return { run: x.run, st: x.st, scene: x.scene, open: x.open, track: x.track }; }")


def scr(pg):
    return pg.evaluate("() => CBApp._t.screen")


def mod_text(pg):
    return pg.evaluate("() => { const m = document.querySelector('#cbOv .cbmod'); return m.classList.contains('on') ? m.innerText : ''; }")


def hp(pg):
    return pg.evaluate("""() => { const g = document.querySelector('#cbOv .qhp'), f = g.querySelector('.fill'), b = g.querySelector('.qbar');
      return { w: Math.round(parseFloat(f.style.width) * 10) / 10, style: f.style.width, n: g.querySelectorAll('.sg i').length, ko: g.classList.contains('ko'), lv: g.dataset.lv, img: g.querySelector('.l').getAttribute('src'), nm: g.querySelector('.nm').textContent }; }""")


def pop(pg):
    """マップの ふきだし：文・場所（マップの 中か）・しっぽが さす 丸・上か 下か"""
    return pg.evaluate("""() => { const e = document.querySelector('#cbOv .qmap .qpo'); if (!e) return null;
      const m = document.querySelector('#cbOv .qmap').getBoundingClientRect(), r = e.getBoundingClientRect(), t = e.querySelector('.qpot').getBoundingClientRect();
      const lv = +(document.querySelector('#cbOv .qnd.sel') || { dataset: {} }).dataset.lv || 0, rg = lv && document.querySelector(`#cbOv .qnd[data-lv="${lv}"] .ring`).getBoundingClientRect();
      return { t: e.innerText, lv: lv, n: document.querySelectorAll('#cbOv .qpo').length, go: !!e.querySelector('[data-cb=qgo]'), back: (e.querySelector('[data-cb=qpx]') || {}).textContent || '',
        inside: r.left >= m.left + 7 && r.right <= m.right - 7 && r.top >= m.top + 7 && r.bottom <= m.bottom - 7, dn: e.classList.contains('dn'),
        tx: t.left + t.width / 2, rx: rg ? rg.left + rg.width / 2 : -1, gap: rg ? (e.classList.contains('dn') ? r.top - rg.bottom : rg.top - r.bottom) : -1, mod: document.querySelector('#cbOv .cbmod').classList.contains('on') }; }""")


def go_field(pg, lv):
    """マップの エリア lv を タップ →「決戦調査に 行く」→ セリフを ぜんぶ 進めて 敵が 出る まで"""
    pg.locator(f'#cbOv .qnd[data-lv="{lv}"]').click(); pg.wait_for_timeout(120)
    pg.locator('#cbOv .qpo [data-cb=qgo]').click()
    pg.wait_for_function("() => CBApp._t.quest.scene && CBApp._t.quest.scene.i >= 0", timeout=10000)
    n = len(pg.evaluate(f"() => CBApp._t.quest.data[{lv - 1}].say"))
    for i in range(n):
        pg.wait_for_function(f"() => CBApp._t.quest.scene.i === {i} && !CBApp._t.quest.scene.typing", timeout=10000)
        pg.locator('#cbOv .qfw').click(); pg.wait_for_timeout(40)
    pg.wait_for_function("() => document.querySelector('#cbOv .qtap.on')", timeout=10000)


def use(pg, hands):
    """次に 配る 戦の 手札（1ターン）：配る 前に 決める（フィールドの 敵を タップ・「第○戦へ」・「もう 一度 挑戦」の 前）"""
    pg.evaluate(f"() => {{ window.__qh = {json.dumps({'turns': 1, 'hands': hands})}; CBApp._qopt = () => window.__qh; }}")


def battle(pg, hands, opp):
    """配られた 1ターンの 戦（use で 決めた 手札）：あなたは 手札の 1まい目を セット・敵は opp → 結果の 窓が 出る まで"""
    pg.wait_for_function("() => CBApp._t.screen === 'game' && CBApp._t.view && CBApp._t.view.can.set", timeout=20000); idle(pg)
    k = hands[0][0]
    pg.locator(f'#cbOv .cbhand .cbc[data-ck="{k}"]').first.click(); pg.wait_for_timeout(60)
    pg.locator('#cbOv .cbmod [data-cb=set]').click(); pg.wait_for_timeout(80)
    pg.evaluate(OPP, {'t': 'set', 'k': opp})
    pg.wait_for_function("() => CBApp._t.ended && document.querySelector('#cbOv .cbmod.on.qend, #cbOv .cbmod.on.qvic')", timeout=30000)
    pg.wait_for_timeout(150)


def next_fight(pg):
    pg.locator('#cbOv .cbmod [data-cb=qnext]').click()
    pg.wait_for_function("() => CBApp._t.view && CBApp._t.view.phase !== 'end'", timeout=20000)


try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2 if SHOT else 1, locale='ja-JP', timezone_id='Asia/Tokyo')
        ctx.add_init_script(FAKE)
        pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(APP); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(5200)
        open_cb(pg); pg.evaluate("() => { CBApp._t.load(); CBApp._t.menu(); }"); pg.wait_for_timeout(200)
        s0 = st(pg)
        print('■ メニュー → マップ')
        qb = pg.locator('#cbOv .cbmenu [data-cb=quest]')
        check(qb.is_visible() and '決戦調査' in qb.inner_text() and '今月 0／12 討伐・次は レベル1' in qb.inner_text(), f'メニューに「⚔️ 決戦調査」（今月の 討伐・次の レベル）：{qb.inner_text()!r}')
        mb = pg.evaluate("() => { const r = document.querySelector('#cbOv .cbmenu .btns').getBoundingClientRect(); return [r.top, r.bottom, innerHeight]; }")
        check(mb[1] <= mb[2], f'メニューの ボタンが 画面に 入る（下 {mb[1]:.0f} ≦ {mb[2]}）')
        shot(pg, 'q00_menu')
        qb.click(); pg.wait_for_timeout(300)
        nd = pg.evaluate("() => [...document.querySelectorAll('#cbOv .qnd')].map(e => e.className.replace('qnd', '').trim())")
        check(len(nd) == 12 and nd[0] == 'op' and all(c == 'lk' for c in nd[1:]), f'マップ：12エリア・1 だけ 開いて いる・ほかは 鍵 {nd}')
        mp = pg.evaluate("() => { const r = document.querySelector('#cbOv .qmap').getBoundingClientRect(); return [r.left, r.top, r.width, r.height, innerWidth, innerHeight]; }")
        check(abs(mp[3] / mp[2] - 1.5) < 0.01 and mp[0] >= 0 and mp[0] + mp[2] <= mp[4] and mp[1] >= 0 and mp[1] + mp[3] <= mp[5], f'マップは たて横 2:3 の まま 画面に 入る {[round(x) for x in mp]}')
        # 丸の 場所：マップの 中の 丸（番号）に 重なる（ボタンの 左上 ＋40 ＝ 丸の まん中）
        c1 = pg.evaluate("() => { const m = document.querySelector('#cbOv .qmap').getBoundingClientRect(), r = document.querySelector('#cbOv .qnd[data-lv=\"1\"] .ring').getBoundingClientRect(); return [(r.left + r.width / 2 - m.left) / m.width * 1024, (r.top + r.height / 2 - m.top) / m.height * 1536]; }")
        check(abs(c1[0] - 135) < 3 and abs(c1[1] - 1376) < 3, f'エリア 1 の 光る 輪は マップの 丸の 上（{c1[0]:.0f}, {c1[1]:.0f}）')
        check('11月の 討伐 0／12' in pg.locator('#cbOv .qmst').inner_text() and q(pg)['track'] == 'main', 'マップの 上に「11月の 討伐 0／12」・BGM は いつもの 曲')
        shot(pg, 'q01_map')
        said(pg); pg.locator('#cbOv .qnd[data-lv="3"]').click(); pg.wait_for_timeout(250)
        o = pop(pg)
        check(o and o['lv'] == 3 and 'レベル2「風見峠」を' in o['t'] and '討伐すると 行けるよ' in o['t'] and not o['go'] and o['back'] == 'もどる' and not o['mod'] and scr(pg) == 'qmap',
              f'鍵の エリア：その 場に ふきだし「🔒 レベル2「風見峠」を 討伐すると 行けるよ」＋「もどる」（窓は 出ない・マップの まま）{o and o["t"]!r}')
        pg.locator('#cbOv .qnd[data-lv="1"]').click(); pg.wait_for_timeout(250)
        o = pop(pg)
        check(o and o['n'] == 1 and o['lv'] == 1 and all(x in o['t'] for x in ('レベル1', '若草の原', '1連勝', '10枚', '決戦調査に 行く', 'もどる')) and o['go'] and not o['mod'],
              f'エリア 1 を タップ：ふきだしが エリア 1 に うつる（名前・1連勝で 討伐・10枚・「決戦調査に 行く」「もどる」）{o and o["t"]!r}')
        check(o and o['inside'] and abs(o['tx'] - o['rx']) < 2.5 and 4 <= o['gap'] <= 26 and not o['dn'], f'ふきだしは マップの 中・エリア 1 の 丸の 上・しっぽが 丸を さす（しっぽ {o and round(o["tx"], 1)}／丸 {o and round(o["rx"], 1)}・すきま {o and round(o["gap"], 1)}）')
        check(pg.evaluate("() => getComputedStyle(document.querySelector('#cbOv .qnd[data-lv=\"1\"] .go')).visibility") == 'hidden', 'ふきだしを 出して いる 間は 丸の 上の「挑戦！」を かくす（しっぽと かさならない）')
        check(pg.evaluate("() => !document.querySelector('#cbOv .qart') && !document.querySelector('#cbOv .cbmod.cbqa.on')"), '前の 窓（フィールドの 大きい 絵）は もう 出ない')
        shot(pg, 'q02_area')
        pg.locator('#cbOv .qpo [data-cb=qpx]').click(); pg.wait_for_timeout(120)
        check(scr(pg) == 'qmap' and pop(pg) is None and pg.evaluate("() => !document.querySelector('#cbOv .qnd.sel')"), '「もどる」→ ふきだしが 消える・マップの まま')
        pg.locator('#cbOv .qnd[data-lv="1"]').click(); pg.wait_for_timeout(150)
        pg.locator('#cbOv .qnd[data-lv="1"]').click(); pg.wait_for_timeout(150)
        check(pop(pg) is None, '同じ エリアを もう 一度 タップ → ふきだしが 消える')
        pg.locator('#cbOv .qnd[data-lv="1"]').click(); pg.wait_for_timeout(150)
        pg.locator('#cbOv .qmst').click(); pg.wait_for_timeout(120)
        check(pop(pg) is None and scr(pg) == 'qmap', 'ふきだしの 外（マップの 上の 文）を タップ → ふきだしが 消える')
        pg.locator('#cbOv .qnd[data-lv="12"]').click(); pg.wait_for_timeout(250)
        o = pop(pg)
        check(o and o['lv'] == 12 and o['dn'] and o['inside'] and abs(o['tx'] - o['rx']) < 2.5 and 4 <= o['gap'] <= 26, f'いちばん 上の エリア 12：ふきだしは 丸の 下（上に 入らない）・しっぽが 上の 丸を さす')
        pg.set_viewport_size({'width': 360, 'height': 640}); pg.wait_for_timeout(300)
        o = pop(pg)
        check(o and o['inside'] and abs(o['tx'] - o['rx']) < 2.5, f'画面の 大きさが かわっても ふきだしは マップの 中・しっぽが 丸を さす（360×640）')
        pg.set_viewport_size({'width': 390, 'height': 844}); pg.wait_for_timeout(300)
        pg.locator('#cbOv .qpo [data-cb=qpx]').click(); pg.wait_for_timeout(100)

        print('■ フィールド（セリフ → 敵 出現）')
        pg.locator('#cbOv .qnd[data-lv="1"]').click(); pg.wait_for_timeout(120)
        pg.locator('#cbOv .qpo [data-cb=qgo]').click()
        pg.wait_for_function("() => CBApp._t.quest.scene && CBApp._t.quest.scene.i === 0", timeout=10000)
        check(scr(pg) == 'qf' and q(pg)['track'] == '', 'フィールドの 画面・BGM は 止まる（敵が 出る 音を 聞かせる）')
        say = pg.evaluate("() => CBApp._t.quest.data[0].say")
        check(len(say) == 3 and 'とても 綺麗な 牧場だな〜' in say[0] and '小馬が 急に 突進してきたぞ！' in say[2], f'セリフ 3行（まさちゃんの 例の 2行を 入れた）')
        pg.evaluate("() => CBApp._t.speed(1)")      # 字が 1つずつ 出る ところを 見る
        pg.wait_for_timeout(120)
        tw = pg.evaluate("() => [document.querySelector('#cbOv .qsay p').textContent.length, CBApp._t.quest.scene.typing]")
        check(0 < tw[0] < len(say[0]) and tw[1], f'セリフは 字が 1つずつ 出る（{tw[0]}字 ／ {len(say[0])}字）')
        pg.locator('#cbOv .qfw').click(); pg.wait_for_timeout(60)
        check(pg.locator('#cbOv .qsay p').inner_text() == say[0] and q(pg)['scene']['i'] == 0, 'とちゅうで タップ → その 行が すぐ ぜんぶ 出る（次へは まだ）')
        fs = pg.evaluate("() => parseFloat(getComputedStyle(document.querySelector('#cbOv .qsay p')).fontSize)")
        check(fs >= 17, f'セリフの 字は 読みやすい 大きさ（{fs}px）')
        shot(pg, 'q03_say')
        pg.evaluate("() => CBApp._t.speed(0.03)")
        for i in (1, 2):
            pg.locator('#cbOv .qfw').click()
            pg.wait_for_function(f"() => CBApp._t.quest.scene.i === {i} && !CBApp._t.quest.scene.typing", timeout=10000)
            check(pg.locator('#cbOv .qsay p').inner_text() == say[i], f'タップ → セリフ {i + 1}行目「{say[i]}」')
        en0 = pg.evaluate("() => getComputedStyle(document.querySelector('#cbOv .qfld .qe')).opacity")
        check(float(en0) == 0, 'セリフの あいだ 敵は まだ 見えない')
        pg.locator('#cbOv .qfw').click()
        pg.wait_for_function("() => document.querySelector('#cbOv .qtel.on')", timeout=10000)
        tel = pg.locator('#cbOv .qtel').inner_text()
        check('レベル1の 敵 出現！' in tel and '1連勝して バトルコインを 10枚 手に入れよう！' in tel, f'上の テロップ：{tel!r}')
        pg.wait_for_function("() => document.querySelector('#cbOv .qtap.on')", timeout=10000); pg.wait_for_timeout(1200)
        check(pg.locator('#cbOv .qnm').inner_text() == '若草の鈴駒' and not pg.locator('#cbOv .qsay').evaluate("e => e.classList.contains('on')"), '敵の 名前「若草の鈴駒」・セリフの 窓は 消える')
        # 敵の 足もと：蹄の 線（絵の 上から 1/1.42）が フィールドの 0.80 の 高さ・横は まん中・画面に 入る
        g = pg.evaluate("""() => { const f = document.querySelector('#cbOv .qfld').getBoundingClientRect(), e = document.querySelector('#cbOv .qfld .qe').getBoundingClientRect();
          return { foot: (e.top + e.height / 1.42 - f.top) / f.height, cx: (e.left + e.width / 2 - f.left) / f.width, w: e.width / f.width, l: e.left, r: e.right, t: e.top, vw: innerWidth, op: +getComputedStyle(document.querySelector('#cbOv .qfld .qe')).opacity }; }""")
        check(abs(g['foot'] - 0.80) < 0.006 and abs(g['cx'] - 0.5) < 0.005 and abs(g['w'] - 0.74) < 0.005 and g['op'] > 0.99, f'敵の 蹄の 線は フィールドの 決めた 高さ（{g["foot"]:.3f}）・まん中（{g["cx"]:.3f}）・幅 {g["w"]:.3f}')
        check(g['l'] >= 0 and g['r'] <= g['vw'] and g['t'] > 150, f'敵は 画面の 中（左 {g["l"]:.0f}・右 {g["r"]:.0f}・上 {g["t"]:.0f}：テロップに かからない）')
        shot(pg, 'q04_enemy')

        print('■ バトル（敵HP ゲージ）')
        said(pg)
        pg.evaluate(f"() => {{ window.__qh = {json.dumps({'turns': 1, 'hands': WIN})}; CBApp._qopt = () => window.__qh; }}")
        pg.locator('#cbOv .qfw').click()
        pg.wait_for_function("() => CBApp._t.screen === 'game' && CBApp._t.view && CBApp._t.view.can.set", timeout=20000); idle(pg)
        top = pg.evaluate("""() => { const g = document.querySelector('#cbOv .cbgame'), t = g.querySelector('.cbturn'), h = g.querySelector('.qhp');
          return { qm: g.classList.contains('qm'), turn: getComputedStyle(t).display, hp: h.getBoundingClientRect().height, hw: h.getBoundingClientRect().width, who: g.querySelector('.cbopp .cbwho b').textContent, qt: g.querySelector('.cbopp .qt').textContent }; }""")
        h = hp(pg)
        check(top['qm'] and top['turn'] == 'none' and top['hp'] >= 60, f'上の「ターン」の 代わりに 敵HP ゲージ（高さ {top["hp"]:.0f}px・幅 {top["hw"]:.0f}px）')
        check(h['img'] == 'cb_q_hl01.webp' and h['nm'] == '若草の鈴駒' and h['w'] > 99 and h['n'] == 0 and not h['ko'], f'ゲージ：盾の 顔（{h["img"]}）・名前・HP 満タン（1連勝 ＝ 区切り なし）{h}')
        check(top['who'] == '鈴駒' and top['qt'] == '第1戦・ターン 1／1', f'相手の 名前は「鈴駒」・小さく「{top["qt"]}」')
        ban = said(pg)
        check(any('第1戦 スタート' in x and '若草の鈴駒と 勝負！' in x for x in ban), f'はじめの 帯「第1戦 スタート／若草の鈴駒と 勝負！」 {ban[:2]}')
        check(q(pg)['track'] == 'quest' and q(pg)['run'] == {'lv': 1, 'won': 0, 'm': '2026-11'}, 'BGM は 決戦調査の 曲・いまの 調査（レベル1・0勝）')
        if HAVE:
            fl = pg.evaluate("() => { const im = document.querySelector('#cbOv .qhp .l'); return [im.complete, im.naturalWidth, im.naturalHeight]; }")
            check(fl[0] and fl[1] == 526 and fl[2] == 294, f'盾の 絵が 読めた {fl}')
        # 赤い 帯は 枠の 中に ぴったり（まさちゃん 16:47「HPは枠ピッタリに綺麗に入れて！」）：まさちゃんの ゲージの 絵の 中の 帯の 所（絵の 294px ＝ ゲージの 高さ）
        #   左 527・右 2029.5・上 310・下 408.5（絵の 中の 灰色の ふち の 内がわ）・角は 枠と 同じ ななめ（左 14.5px・右 24.5px）
        bx = pg.evaluate("""() => { const g = document.querySelector('#cbOv .qhp'), a = g.getBoundingClientRect(), b = g.querySelector('.qbar').getBoundingClientRect(), cs = getComputedStyle(g.querySelector('.qbar'));
          return { gl: a.left, gt: a.top, gr: a.right, gh: a.height, l: b.left, t: b.top, r: b.right, h: b.height, clip: cs.clipPath || cs.webkitClipPath || '', rad: cs.borderTopLeftRadius, bd: cs.borderTopWidth, mt: cs.marginTop }; }""")
        u = bx['gh'] / 294
        exp = {'l': bx['gl'] + (527 - 34) * u, 'r': bx['gr'] - (2146 - 2029.5) * u, 't': bx['gt'] + (310 - 206) * u, 'h': 98.5 * u}
        check(all(abs(bx[k] - exp[k]) < 0.6 for k in exp) and bx['clip'].startswith('polygon(') and bx['rad'] == '0px' and bx['bd'] == '0px' and bx['mt'] == '0px',
              f'赤い 帯は 枠の 中に ぴったり（左 {bx["l"] - bx["gl"]:.1f}・右 {bx["gr"] - bx["r"]:.1f}・上 {bx["t"] - bx["gt"]:.1f}・高さ {bx["h"]:.1f}px：丸い 角・ふち なし・角は 枠と 同じ ななめ {bx["clip"][:24]}…）')
        try:
            from PIL import Image
            import io
        except Exception:
            Image = None
        if Image:
            x0, y0 = int(bx['l']) - 2, int(bx['t']) - 2
            im = Image.open(io.BytesIO(pg.screenshot(clip={'x': x0, 'y': y0, 'width': int(bx['r'] - x0) + 3, 'height': int(bx['h']) + 5}))).convert('RGB')
            sc = im.width / (int(bx['r'] - x0) + 3)
            px = lambda x, y: im.getpixel((min(im.width - 1, int((x - x0) * sc)), min(im.height - 1, int((y - y0) * sc))))
            red = lambda c: c[0] > 150 and c[1] < 110 and c[2] < 110
            mid = bx['t'] + bx['h'] / 2
            inn = [px(bx['l'] + 1.2, mid), px(bx['r'] - 1.2, mid), px(bx['r'] - 6, bx['t'] + bx['h'] * 0.3)]      # 名前の 字（白）が ない 所
            out = [px(bx['l'] + 0.4, bx['t'] + 0.4), px(bx['l'] + 0.4, bx['t'] + bx['h'] - 0.6), px(bx['r'] - 0.8, bx['t'] + 0.8), px(bx['r'] - 0.8, bx['t'] + bx['h'] - 1), px(bx['l'] - 1.5, mid), px(bx['r'] + 1.5, mid)]
            check(all(red(c) for c in inn) and not any(red(c) for c in out), f'画面でも：帯の 中は 赤・枠の 角（ななめに 切った 所）と 枠の 外には はみ出さない {inn} {out}')
        shot(pg, 'q05_battle')
        k = WIN[0][0]
        pg.locator(f'#cbOv .cbhand .cbc[data-ck="{k}"]').first.click(); pg.wait_for_timeout(60)
        pg.locator('#cbOv .cbmod [data-cb=set]').click(); pg.wait_for_timeout(80)
        pg.evaluate(OPP, {'t': 'set', 'k': '7'})
        pg.wait_for_function("() => document.querySelector('#cbOv .cbmod.on.qvic')", timeout=30000)
        h = hp(pg)
        check(h['w'] < 1 and h['ko'], f'倒した：HP 0・盾の 顔が 暗く なる {h}')
        pg.wait_for_function("() => document.querySelector('#cbOv .qget.on') && document.querySelector('#cbOv .qget .n').textContent === '10'", timeout=10000); pg.wait_for_timeout(300)
        t = mod_text(pg)
        check('討伐成功！' in t and '若草の鈴駒を 倒した！' in t and 'バトルコインを GETした！' in t and '＋10枚' in t, f'勝利の 演出：討伐成功！・バトルコインを GETした！ ＋10枚')
        check(pg.evaluate("() => [document.querySelector('#cbOv .qv').className, document.querySelectorAll('#cbOv .qpt .cf').length, document.querySelectorAll('#cbOv .qpt .cn').length]") == ['qv t1', 0, 0], 'レベル1〜5：1段階目（光の 筋・紙吹雪 なし）')
        s1 = st(pg)
        check(s1['coin'] == s0['coin'] + 10 and s1['q']['clr'] == 1 and s1['ms']['cpu'] == s0['ms']['cpu'] + 1, f'コイン ＋10（{s0["coin"]} → {s1["coin"]}）・討伐 1・ミッションの 連勝 ＋1')
        check([s1[x] for x in ('win', 'lose', 'draw', 'streak', 'owe')] == [s0[x] for x in ('win', 'lose', 'draw', 'streak', 'owe')], 'いつもの 勝ち負け・連勝・お世話トークンは かわらない')
        shot(pg, 'q06_victory1')
        said(pg)
        pg.locator('#cbOv .cbmod [data-cb=qmapgo]').click(); pg.wait_for_timeout(400)
        nd = pg.evaluate("() => [...document.querySelectorAll('#cbOv .qnd')].map(e => e.className.replace('qnd', '').trim())")
        check(scr(pg) == 'qmap' and nd[0] == 'dn' and nd[1] == 'op nw' and all(c == 'lk' for c in nd[2:]), f'マップへ：エリア 1 は 討伐の はんこ・2 が 開く（開く 動き）{nd[:3]}')
        check(any('レベル2「風見峠」が 開いたよ' in x for x in said(pg)) and q(pg)['track'] == 'main' and q(pg)['run'] is None, 'ふきだし「🔓 レベル2「風見峠」が 開いたよ！」・BGM は いつもの 曲')
        shot(pg, 'q07_map_unlock')
        pg.locator('#cbOv .qnd[data-lv="1"]').click(); pg.wait_for_timeout(250)
        o = pop(pg)
        check(o and '討伐済み' in o['t'] and '来月の リセットまで' in o['t'] and not o['go'] and o['back'] == 'もどる' and not o['mod'], f'討伐した エリア：その 場に ふきだし「討伐済み！」（今月は もう 行けない）{o and o["t"]!r}')
        pg.locator('#cbOv .qpo [data-cb=qpx]').click(); pg.wait_for_timeout(80)

        print('■ レベル2（2連勝）：HP が 半分 → 第2戦')
        go_field(pg, 2); said(pg); use(pg, WIN)
        pg.locator('#cbOv .qfw').click()
        battle(pg, WIN, '7')
        h = hp(pg); t = mod_text(pg)
        check(48 < h['w'] < 52 and h['n'] == 1 and not h['ko'], f'1勝：HP が 半分（{h["w"]}%・区切り 1本）')
        check('勝利！' in t and '1連勝' in t and 'あと 1連勝で 討伐！' in t and '第2戦へ' in t and 'マップへ 戻る' in t, 'あいだの 窓：勝利！・あと 1連勝で 討伐！・「第2戦へ」「マップへ 戻る」')
        ban = said(pg)
        check(any('ダメージ！' in x and '疾風の HP が 減った！' in x for x in ban), f'帯「ダメージ！ 疾風の HP が 減った！」')
        shot(pg, 'q08_between')
        next_fight(pg); pg.wait_for_timeout(200)
        ban = said(pg)
        check(any('第2戦 スタート' in x and 'あと 1連勝で 討伐！' in x for x in ban), f'帯「第2戦 スタート／あと 1連勝で 討伐！」')
        battle(pg, WIN, '7')
        pg.wait_for_function("() => document.querySelector('#cbOv .qget .n') && document.querySelector('#cbOv .qget .n').textContent === '20'", timeout=10000); pg.wait_for_timeout(400)
        t = mod_text(pg)
        check(st(pg)['q']['clr'] == 2 and st(pg)['ms']['cpu'] == 3 and 'ミッション達成！' in t and '3連勝' in t and '＋30枚' in t, 'レベル2 討伐：コイン ＋20・ミッション（コンピュータに 3連勝）も 数える →「🎯 ミッション達成！ 3連勝 ＋30枚」')
        check(st(pg)['coin'] == s0['coin'] + 60, f'コインは 10 ＋ 20 ＋ ミッション 30（{s0["coin"]} → {st(pg)["coin"]}）')
        pg.locator('#cbOv .cbmod [data-cb=qmapgo]').click(); pg.wait_for_timeout(300)

        print('■ レベル3（3連勝）：同点 → やり直し・負け → 1戦目から・やめる')
        ms0 = st(pg)['ms']['cpu']
        go_field(pg, 3); use(pg, WIN); pg.locator('#cbOv .qfw').click()
        battle(pg, WIN, '7')
        h = hp(pg)
        check(st(pg)['ms']['cpu'] == ms0 + 1 and 65 < h['w'] < 68 and h['n'] == 2, f'1勝：ミッションの 連勝 ＋1・HP 3分の2（区切り 2本）')
        use(pg, DRAW); next_fight(pg)
        battle(pg, DRAW, 'm')
        h = hp(pg); t = mod_text(pg)
        check('同点！' in t and '第2戦を やり直す' in t and 65 < h['w'] < 68 and q(pg)['run']['won'] == 1, f'同点：「第2戦を やり直す」・HP は そのまま（{h["w"]}%）')
        shot(pg, 'q09_draw')
        said(pg); use(pg, LOSE); next_fight(pg)
        check(any('第2戦 スタート' in x for x in said(pg)), '同じ 戦（第2戦）を やり直す')
        battle(pg, LOSE, 'k')
        t = mod_text(pg)
        check('調査 失敗…' in t and 'もう 一度 挑戦' in t and st(pg)['ms']['cpu'] == 0, '負け：「調査 失敗…」「もう 一度 挑戦」・ミッションの 連勝は 0')
        shot(pg, 'q10_lose')
        said(pg); use(pg, WIN); pg.locator('#cbOv .cbmod [data-cb=qretry]').click()
        pg.wait_for_function("() => CBApp._t.view && CBApp._t.view.phase !== 'end'", timeout=20000); idle(pg)
        h = hp(pg)
        check(h['w'] > 99 and q(pg)['run']['won'] == 0 and any('第1戦 スタート' in x for x in said(pg)), f'もう 一度：HP 満タン・第1戦から')
        s2 = st(pg)
        pg.locator('#cbOv .cbtop [data-cb=quit]').click(); pg.wait_for_timeout(100)
        t = mod_text(pg)
        check('調査を やめる？' in t and '調査 失敗' in t, f'やめる：「調査を やめる？」')
        pg.evaluate("() => { CBApp._t.state.ms.cpu = 2; CBApp._t.save(); }")
        pg.locator('#cbOv .cbmod [data-cb=quitgo]').click(); pg.wait_for_timeout(300)
        s3 = st(pg)
        check(scr(pg) == 'qmap' and s3['ms']['cpu'] == 0 and s3['lose'] == s2['lose'] and s3['streak'] == s2['streak'] and s3['q']['clr'] == 2, 'やめた → マップ・ミッションの 連勝 0・いつもの 負けには 数えない')
        check([s3[x] for x in ('win', 'lose', 'draw', 'streak', 'owe')] == [s0[x] for x in ('win', 'lose', 'draw', 'streak', 'owe')], 'ここまで いつもの 勝ち負け・連勝・お世話トークンは かわらない')

        print('■ 確定カード（レベル 5〜12）')
        want = {5: {4: ['1']}, 6: {4: ['1', '1']}, 7: {4: ['2', '2'], 5: ['2', '2']}, 8: {5: ['2', '2', '2']}, 9: {5: ['1', '1'], 6: ['1', '1']}, 10: {5: ['1', '1', '1'], 6: ['1', '1', '1']},
                11: {5: ['1', 'k'], 6: ['1', 'k']}, 12: {4: ['1', 'k'], 5: ['1', 'k'], 6: ['1', 'k']}}
        need = [1, 2, 3, 4, 4, 4, 5, 5, 6, 6, 6, 6]; coin = [10, 20, 30, 40, 50, 80, 100, 130, 160, 190, 220, 250]
        pg.evaluate("() => { CBApp._qopt = null; }")
        got = pg.evaluate("() => CBApp._t.quest.data.map(q => [q.w, q.c, Array.from({ length: q.w }, (_, i) => CBApp._t.qopt(q.lv, i + 1).rig[1])])")
        okr = all(got[i][0] == need[i] and got[i][1] == coin[i] and all(got[i][2][n - 1] == want.get(i + 1, {}).get(n, []) for n in range(1, need[i] + 1)) for i in range(12))
        check(okr, 'レベルごとの 連勝・コイン・何戦目に 敵の 手札に 必ず 入る カード（まさちゃんの 表の とおり）')
        names = pg.evaluate("() => CBApp._t.quest.data.map(q => q.n)")
        check(names == ['若草の鈴駒', '風見峠の疾風', '茨鎧の森番', '鉄門の関守', '霧鏡の湖霊', '刻砂の時守', '雷鳴峡の迅雷', '氷晶砦の守将', '紅蓮の鉄槌', '星月の天馬', '黒曜の覇王', '日蝕の薔薇女王'], f'敵の 名前（フィールドの 名前から）')
        # レベル5：1〜3戦は 勝てる 手札・4戦目は 確定カード（くじ）
        pg.evaluate("() => { CBApp._t.state.q.clr = 4; CBApp._t.save(); }"); pg.locator('#cbOv [data-cb=qx]').click(); pg.wait_for_timeout(100)
        pg.locator('#cbOv .cbmenu [data-cb=quest]').click(); pg.wait_for_timeout(200)
        go_field(pg, 5); use(pg, WIN); pg.locator('#cbOv .qfw').click()
        for n in range(1, 4):
            battle(pg, WIN, '7')
            if n < 3: next_fight(pg)
        said(pg)
        pg.evaluate("() => { CBApp._qopt = (lv, n) => (n === 4 ? null : window.__qh); }")
        next_fight(pg); idle(pg)
        cpu = pg.evaluate("() => CBApp._t.match._.state().p[1].hand.map(c => c.k)")
        ban = said(pg)
        check(cpu.count('1') >= 1 and len(cpu) == 7, f'レベル5 の 4戦目：敵の 手札に 必ず 1（{cpu}）')
        check(any('第4戦 スタート' in x and '⚠ 敵の 手札に 必ず 1 が 1枚！' in x for x in ban), f'4戦目の 帯に「⚠ 敵の 手札に 必ず 1 が 1枚！」')
        pg.evaluate("() => { const b = document.querySelector('#cbOv .cbmod.cbask [data-cb=askpeek]'); if (b) b.click(); }"); pg.wait_for_timeout(100)      # くじの 手札で 効果を 聞く 窓が 出て いたら 下げる
        shot(pg, 'q11_rig')
        pg.locator('#cbOv .cbtop [data-cb=quit]').click(); pg.wait_for_timeout(100); pg.locator('#cbOv .cbmod [data-cb=quitgo]').click(); pg.wait_for_timeout(300)

        print('■ 勝利の 演出（3段階）')
        for lv, tier, nf in ((6, 2, 4), (10, 3, 6)):
            pg.evaluate(f"() => {{ CBApp._t.state.q.clr = {lv - 1}; CBApp._t.save(); }}"); pg.locator('#cbOv [data-cb=qx]').click(); pg.wait_for_timeout(100)
            pg.locator('#cbOv .cbmenu [data-cb=quest]').click(); pg.wait_for_timeout(200)
            go_field(pg, lv); c0 = st(pg)['coin']; use(pg, WIN); pg.locator('#cbOv .qfw').click()
            for n in range(1, nf + 1):
                battle(pg, WIN, '7')
                if n < nf: next_fight(pg)
            pg.wait_for_function("() => document.querySelector('#cbOv .qget.on')", timeout=10000); pg.wait_for_timeout(900)
            v = pg.evaluate("() => [document.querySelector('#cbOv .qv').className, document.querySelectorAll('#cbOv .qpt .cf').length, document.querySelectorAll('#cbOv .qpt .cn').length, document.querySelectorAll('#cbOv .qv .wave').length]")
            exp = ['qv t2', 26, 0, 0] if tier == 2 else ['qv t3', 26, 16, 2]
            check(v == exp, f'レベル{lv}：{tier}段階目の 演出 {v}（{"紙吹雪" if tier == 2 else "紙吹雪・コインの 雨・光の 輪"}）')
            check(st(pg)['coin'] >= c0 + coin[lv - 1], f'レベル{lv}：バトルコイン ＋{coin[lv - 1]}')
            shot(pg, f'q12_victory{tier}')
            pg.locator('#cbOv .cbmod [data-cb=qmapgo]').click(); pg.wait_for_timeout(300)
        pg.evaluate("() => { CBApp._t.state.q.clr = 11; CBApp._t.save(); }"); pg.locator('#cbOv [data-cb=qx]').click(); pg.wait_for_timeout(100)
        pg.locator('#cbOv .cbmenu [data-cb=quest]').click(); pg.wait_for_timeout(200)
        go_field(pg, 12); use(pg, WIN); pg.locator('#cbOv .qfw').click()
        for n in range(1, 7):
            battle(pg, WIN, '7')
            if n < 6: next_fight(pg)
        said(pg); pg.locator('#cbOv .cbmod [data-cb=qmapgo]').click(); pg.wait_for_timeout(300)
        nd = pg.evaluate("() => [...document.querySelectorAll('#cbOv .qnd')].map(e => e.className.replace('qnd', '').trim())")
        check(all(c == 'dn' for c in nd) and '全部 討伐！' in pg.locator('#cbOv .qmst').inner_text() and not any('開いたよ' in x for x in said(pg)), 'レベル12 を 倒した：全部 討伐の はんこ・「全部 討伐！」（次は ない）')
        shot(pg, 'q13_map_all')
        pg.locator('#cbOv [data-cb=qx]').click(); pg.wait_for_timeout(100)
        check('今月は 全部 討伐！' in pg.locator('#cbOv .cbmenu [data-cb=quest]').inner_text(), 'メニュー：「今月は 全部 討伐！」')

        print('■ 毎月 1日に リセット・戦の とちゅうで 月が かわる・戦の とちゅうで 閉じた')
        pg.evaluate("() => { window.__now = '2026-12-01T00:05:00'; }")
        pg.locator('#cbOv .cbmenu [data-cb=quest]').click(); pg.wait_for_timeout(200)
        nd = pg.evaluate("() => [...document.querySelectorAll('#cbOv .qnd')].map(e => e.className.replace('qnd', '').trim())")
        check(st(pg)['q'] == {'m': '2026-12', 'clr': 0} and nd[0] == 'op' and '12月の 討伐 0／12' in pg.locator('#cbOv .qmst').inner_text(), '12月1日：リセット（討伐 0・エリア 1 から）')
        pg.evaluate("() => { window.__now = '2026-11-20T00:05:00'; }"); pg.locator('#cbOv [data-cb=qx]').click(); pg.locator('#cbOv .cbmenu [data-cb=quest]').click(); pg.wait_for_timeout(200)
        check(st(pg)['q']['m'] == '2026-12', '時計が もどっても リセットしない（月は 進んだ ときだけ）')
        pg.evaluate("() => { window.__now = '2026-12-31T23:58:00'; }")
        go_field(pg, 1); use(pg, WIN); pg.locator('#cbOv .qfw').click()
        pg.wait_for_function("() => CBApp._t.screen === 'game' && CBApp._t.view && CBApp._t.view.can.set", timeout=20000); idle(pg)
        pg.evaluate("() => { window.__now = '2027-01-01T00:02:00'; }")
        c0 = st(pg)['coin']
        pg.locator('#cbOv .cbhand .cbc[data-ck="k"]').first.click(); pg.wait_for_timeout(60); pg.locator('#cbOv .cbmod [data-cb=set]').click(); pg.wait_for_timeout(80)
        pg.evaluate(OPP, {'t': 'set', 'k': '7'})
        pg.wait_for_function("() => document.querySelector('#cbOv .cbmod.on.qend')", timeout=30000)
        t = mod_text(pg)
        check('月が 変わったよ' in t and st(pg)['q'] == {'m': '2027-01', 'clr': 0} and st(pg)['coin'] == c0, '戦の とちゅうで 月が かわった：「月が 変わったよ」・その 調査は なし（コインも なし）')
        pg.locator('#cbOv .cbmod [data-cb=qmapgo]').click(); pg.wait_for_timeout(200)
        # 戦の とちゅうで アプリを 閉じた（live 'qc'）→ つぎに 開いた とき：調査 失敗・ミッションの 連勝 0・いつもの 負けには 数えない
        go_field(pg, 1); pg.locator('#cbOv .qfw').click()
        pg.wait_for_function("() => CBApp._t.screen === 'game' && CBApp._t.view && CBApp._t.view.can.set", timeout=20000); idle(pg)
        sv = pg.evaluate("() => { CBApp._t.state.ms.cpu = 4; CBApp._t.save(); return JSON.parse(localStorage.getItem('tengel.cb')); }")
        check(sv['ms']['live'] == 'qc', f'決戦調査の 戦の とちゅうの しるし（live＝{sv["ms"]["live"]!r}）')
        pg.evaluate("() => { CBApp._t.state.ms.live = 'qc'; CBApp._t.save(); }")
        s4 = st(pg); said(pg)
        pg.evaluate("() => { CBApp._t.load(); CBApp._t.menu(); }"); pg.wait_for_timeout(300)
        s5 = st(pg); tw = said(pg)
        check(s5['ms']['cpu'] == 0 and s5['ms']['live'] == '' and s5['lose'] == s4['lose'] and s5['streak'] == s4['streak'], 'つぎに 開いた とき：ミッションの 連勝 0・いつもの 負けには 数えない')
        check(any('決戦調査は 失敗に なったよ' in x and 'ミッションの 連勝（コンピュータ）は 0 に 戻ったよ' in x for x in tw), f'メニューで 知らせる：{tw[:1]}')

        print('■ あそび方・エラー')
        pg.locator('#cbOv .cbmenu [data-cb=help]').click(); pg.wait_for_timeout(200)
        hl = pg.locator('#cbOv .cbhelp').inner_text()
        check('⚔️ 決戦調査' in hl and 'Lv12 6連勝 250枚' in hl and '毎月 1日に リセット' in hl and '同じ 戦を やり直し' in hl, '遊び方に「⚔️ 決戦調査」（連勝・コイン・同点・リセット）')
        check(not errs, f'画面の エラー なし {errs[:3]}')
        ctx.close()

        print('■ 小さい 画面（iPhone SE：375×647）')
        ctx = b.new_context(viewport={'width': 375, 'height': 647}, device_scale_factor=2 if SHOT else 1, locale='ja-JP', timezone_id='Asia/Tokyo')
        ctx.add_init_script(FAKE)
        pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(APP); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(5200)
        open_cb(pg); pg.evaluate("() => { CBApp._t.load(); CBApp._t.menu(); }"); pg.wait_for_timeout(200)
        mb = pg.evaluate("() => { const r = [...document.querySelectorAll('#cbOv .cbmenu .cbb')].map(e => e.getBoundingClientRect()); return [Math.min(...r.map(x => x.top)), Math.max(...r.map(x => x.bottom)), innerHeight]; }")
        check(mb[0] >= 0 and mb[1] <= mb[2], f'SE：メニューの ボタンが ぜんぶ 画面に 入る（{mb[0]:.0f}〜{mb[1]:.0f} ／ {mb[2]}）')
        shot(pg, 'se0_menu')
        pg.locator('#cbOv .cbmenu [data-cb=quest]').click(); pg.wait_for_timeout(300)
        mp = pg.evaluate("() => { const r = document.querySelector('#cbOv .qmap').getBoundingClientRect(), f = document.querySelector('#cbOv .qmft').getBoundingClientRect(); return [r.top, r.bottom, r.width, f.bottom, innerHeight]; }")
        check(mp[0] >= 40 and mp[3] <= mp[4] + 1 and mp[2] > 280, f'SE：マップ（幅 {mp[2]:.0f}px）と 下の 行が 画面に 入る')
        shot(pg, 'se1_map')
        go_field(pg, 1); pg.wait_for_timeout(700)      # 名前と「タップで バトル開始！」が 出おわる まで（CSS の 動きは 本当の 時間）
        g = pg.evaluate("() => { const t = document.querySelector('#cbOv .qtel').getBoundingClientRect(), e = document.querySelector('#cbOv .qfld .qe').getBoundingClientRect(), n = document.querySelector('#cbOv .qnm').getBoundingClientRect(), p = document.querySelector('#cbOv .qtap').getBoundingClientRect(); return [t.bottom, e.top, e.left, e.right, n.top, n.bottom, p.top, p.bottom, innerWidth, innerHeight]; }")
        check(g[0] <= g[1] + 40 and g[2] >= -1 and g[3] <= g[8] + 1 and g[5] <= g[6] and g[7] <= g[9], f'SE：テロップ・敵・名前・「タップで バトル開始！」が 重ならずに 画面の 中 {[round(x) for x in g]}')
        shot(pg, 'se2_enemy')
        use(pg, WIN); pg.locator('#cbOv .qfw').click()
        pg.wait_for_function("() => CBApp._t.screen === 'game' && CBApp._t.view && CBApp._t.view.can.set", timeout=20000); idle(pg)
        tb = pg.evaluate("() => { const q = document.querySelector('#cbOv .qhp').getBoundingClientRect(), a = document.querySelector('#cbOv .cbtop [data-cb=quit]').getBoundingClientRect(), h = document.querySelector('#cbOv .cbtop [data-cb=help]').getBoundingClientRect(), c = document.querySelector('#cbOv .cbhand .cbc').getBoundingClientRect(); return [a.right, q.left, q.right, h.left, q.height, c.width, c.bottom, innerHeight]; }")
        check(tb[0] <= tb[1] and tb[2] <= tb[3] and tb[4] >= 60 and tb[5] >= 44 and tb[6] <= tb[7], f'SE：上の やめる・ゲージ・？が 重ならない（ゲージ 高さ {tb[4]:.0f}px）・手札の カード 幅 {tb[5]:.0f}px')
        shot(pg, 'se3_battle')
        battle(pg, WIN, '7')
        pg.wait_for_function("() => document.querySelector('#cbOv .qg2.on')", timeout=10000)
        v = pg.evaluate("() => { const b = document.querySelector('#cbOv .cbmod [data-cb=qmapgo]').getBoundingClientRect(), h = document.querySelector('#cbOv .qv h3').getBoundingClientRect(), e = document.querySelector('#cbOv .qv .en').getBoundingClientRect(); return [e.top, h.top, b.bottom, innerHeight]; }")
        check(v[0] >= -20 and v[2] <= v[3], f'SE：勝利の 画面の「マップへ」が 画面に 入る {[round(x) for x in v]}')
        shot(pg, 'se4_victory')
        check(not errs, f'SE：画面の エラー なし {errs[:3]}')
        ctx.close()

        print('■ テスト版の 道具（右上の 🧪）・App Store版には 出ない')
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo')
        ctx.add_init_script(FAKE)
        pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(APP.replace('/APP/', '/TST/')); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(5200)
        open_cb(pg); pg.evaluate("() => { CBApp._think = null; }"); pg.locator('#cbOv .cbmenu [data-cb=quest]').click(); pg.wait_for_timeout(200)      # コンピュータは いつもの 速さで 考える
        check(pg.locator('#cbOv .qtt').is_visible(), 'テスト版：マップの 右上に「🧪」')
        pg.locator('#cbOv .qtt').click(); pg.wait_for_timeout(100)
        pg.locator('#cbOv [data-cb=tstq][data-t=qclr]').click(); pg.wait_for_timeout(150)
        check(st(pg)['q']['clr'] == 1, '🧪「次の エリアを 討伐済みに」')
        pg.locator('#cbOv .qtt').click(); pg.locator('#cbOv [data-cb=tstq][data-t=qez]').click(); pg.wait_for_timeout(150)
        go_field(pg, 2); pg.locator('#cbOv .qfw').click()
        pg.wait_for_function("() => CBApp._t.screen === 'game' && CBApp._t.view && CBApp._t.view.can.set", timeout=20000); idle(pg)
        v = pg.evaluate("() => [CBApp._t.view.turns, CBApp._t.view.my.hand.map(c => c.k).sort().join('')]")
        check(v[0] == 1 and v[1] == ''.join(sorted('k112233')), f'🧪「1ターンで 勝てる 手札」：1ターン・あなたは 神様馬・1・2・3 {v}')
        ctx.close()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo')
        ctx.add_init_script(FAKE)
        pg = ctx.new_page()
        pg.goto(APP); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(5200)
        open_cb(pg); pg.locator('#cbOv .cbmenu [data-cb=quest]').click(); pg.wait_for_timeout(200)
        check(not pg.locator('#cbOv .qtt').is_visible() and 'qHtml' not in pg.evaluate("() => typeof window.CBTest === 'undefined' ? '' : Object.keys(window.CBTest).join()"), 'App Store版：「🧪」は 出ない（道具も 入って いない）')
        ctx.close()
        b.close()
finally:
    srv.terminate()
    shutil.rmtree(SRV, ignore_errors=True)
print('結果：', 'OK' if not fails else f'NG {len(fails)}')
for f in fails: print('  ❌', f)
sys.exit(1 if fails else 0)
