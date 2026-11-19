# 馬カードバトルの「決戦調査」（第4.196版・まさちゃん 2026/11/18 15:09）の 画面の テスト：App Store版（TARGET=app）を localhost で アプリ版として 開く
#   ・メニューの「⚔️ 決戦調査」→ マップ（エリア 1 だけ 開いて いる・ほかは 鍵）→ エリアを タップ → その 場に ふきだし（まさちゃん 16:47：開いて いる →「決戦調査に 行く」／「もどる」・鍵／討伐済み → わけ と「もどる」・マップは 見えた まま）
#   ・フィールド：セリフ（字が 1つずつ・タップで ぜんぶ → 次へ）→ テロップ「レベル○の 敵 出現！」→ 敵（蹄の 線が フィールドの 決めた 高さ）→ 名前 →「タップで バトル開始！」
#   ・バトル：上は 敵HP ゲージ（盾の 中に 顔・名前・HP のこま：赤い 帯は 枠の 中に ぴったり〈角も 枠と 同じ 形〉）・「ターン」は 出ない・相手の 名前は 敵の 短い 名前・BGM は 決戦調査の 曲（フィールドでは 止まる）
#   ・勝ち → HP が へる（あいだの 窓「第2戦へ」）→ 討伐（勝利の 演出 3段階・バトルコイン GET）→ マップ（次の エリアが 開く・討伐の はんこ）
#   ・同点 → 同じ 戦を やり直し（HP は そのまま）／負け → 調査 失敗（もう 一度 → HP は 満タン）／とちゅうで やめる → マップ（ミッションの 連勝 0・いつもの 負けには 数えない）
#   ・確定カード（レベル 5〜12：決まった 戦で 敵の 手札に かならず）・ミッション（コンピュータに 連続勝利）は 数える・いつもの 勝ち負け・連勝・お世話トークン・いつもの コインは かわらない
#   ・毎月 1日に リセット・戦の とちゅうで 月が かわった・窓を 開いた まま 月が 進んだ（第4.206版：バトル開始・第○戦へ・もう 一度 挑戦 の 前に 止める・切符は 使わない）・戦の とちゅうで アプリを 閉じた（つぎに 開いた とき 調査 失敗）・テスト版の 道具（1ターンで 勝てる 手札 など）
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
# 第4.200版：まさちゃんの セリフの 表（11/18 22:54「セリフ変更と、タップ数、何タップ目に敵表示するか書いてるからこれ通り入れて！」）＝ [[セリフ（1タップで 1行）], 何行目で 敵が 出るか]（レベル 1〜12）
SAY = [[["「ふぅ、ここでひと休み……」　チリン♪", "チリンチリンッ！　ダダダッ！　「わっ、子馬がこっちに！」"], 2], [["バタバタバタッ！　「すごい風だ。……坂の上に馬？」", "ビュンッ！　「早い！こいつも敵か！」"], 2], [["ザク、ザク……。　「茨で行き止まりか。」", "ガサ……ガサッ。　「ん？　茨が動いたぞ。」", "ブルルッ！　「森番だ！　その茨、鎧だったのか！」"], 3], [["ジャラララ……。　「よし、門が開くぞ！」", "ギギギ……ガシャン！　門の奥から、カツン……カツン……ダンッ！", "関守のひと踏みで、門の鎖が揺れる。　「明らかに今までより強そうだ！」"], 3], [["ヒュゥゥ……。霧の奥で、ぴちゃん。……ぴちゃん。　「水面に、馬が映ってる。」", "そっと振り向く。　「……誰もいない。」", "背後で、ちゃぷ……。すぐ後ろで、ポチャン、、、すぐ後ろに何かいる…ブルルッ！　「……湖霊だ！」"], 3], [["ヒュオォ……。振り返ると、足跡が砂に消えていく。　「砂の王国……？　さっきもこの門を通ったぞ。」", "王墓の奥で、コン……コン……。大砂時計のガラスが内側から鳴る。　「なんだ、あれ……。砂が上に落ちてる？」", "――ドゴォンッ！　真横で砂が噴き上がり、黄金の馬が飛び出す！　「うわっ！　刻砂の時守だ！」"], 3], [["ハァ……ハァ……。震える足で、吊り橋を踏む。ギシッ。　「やっと六戦……。少し、息を――」", "ズドォン！ズドォンン！！ズドォン！そこらじゅうに落雷が落ちている…ズドドドォンッ！！　「うわっ！」", "キィィン……。爆煙が晴れる。パチッ。青い火花が、たてがみを走る。　「……雷鳴峡の迅雷だ！」"], 3], [["ヒュウゥ……。　「寒っ。息が真っ白だ。」", "門の裏で何かが。ズン、ズン…。ズシィンッ！「自分の足元まで揺れてるぞ……。」", "守将が頭をかがめて門をくぐる。蹄から足元へ、ピキピキピキッ！　「靴の先が凍っている！とてつもない大きさだ！」"], 3], [["カーン……カーン……。　「炉の奥で、誰かが鉄を打ってる。」", "カン、カン、カカカンッ！　音が止まった…？火の向こうで、蹄が鉄をこする。ギリッ……。　「……来る。」", "ガァンッ！　鉄床を蹴り、火花の幕を突き破って突進してくる！　「紅蓮の鉄槌だ！　来るぞ！」"], 3], [["ふわり。　「白い羽……どこから？」", "夜空の星が、すうっと動く。　「あの星座、翼だ……！」", "ファサ……バサッ、バサァッ！　風が頬を打つ。青い石床に、蹄がカツン。　「天馬が目の前に、こんなにデカいのか！」"], 3], [["ギィ……クルクルクルッ。　「天球儀が、勝手に……！」", "キリ……キリキリキリッ！　カチッ、カチッ、カチン！　金の輪が一直線に重なる。　「あれは…王冠？」", "コツ……コツ……。紫水晶が低くうなる。ヴゥゥン……。ダンッ！　王冠の馬が光の中へ踏み出す。　「こいつが、黒曜の覇王か！」"], 3], [["ギィィ……。　「ここが、最後の玉座か。」", "ザワ……ザワザワッ。薔薇が一斉に揺れる。玉座の陰から、羽のこすれる音。ファサ……。　「……そこにいるのか。」", "一瞬、静まり返る。――バサァァッ！！　黒い翼が花びらを払い、女王の蹄が最後の一段を降りる。　薔薇女王「十一勝、お見事。あと一勝、取れるかしら？」", "シャッ！　カードを構える。　「お前が最後だ！行くぞ！」"], 3]]


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


TKFULL = "() => { const T = CBApp._t; T.state.qt = { n: 15, at: Date.now() }; T.save(); }"      # 第4.203版：調査隊切符を 満タンに（たくさん 戦う テストで 切符が なくならない ように：切符 そのものは「■ 調査隊切符」で 見る）


def go_field(pg, lv, fill=True):
    """マップの エリア lv を タップ →「決戦調査に 行く」→ セリフを ぜんぶ 進めて 敵が 出る まで（fill：調査隊切符を 満タンに して から）"""
    if fill: pg.evaluate(TKFULL)
    pg.locator(f'#cbOv .qnd[data-lv="{lv}"]').click(); pg.wait_for_timeout(120)
    pg.locator('#cbOv .qpo [data-cb=qgo]').click()
    pg.wait_for_function("() => CBApp._t.quest.scene && CBApp._t.quest.scene.i >= 0", timeout=10000)
    n = len(pg.evaluate(f"() => CBApp._t.quest.data[{lv - 1}].say"))
    for i in range(n):
        pg.wait_for_function(f"() => CBApp._t.quest.scene.i === {i} && !CBApp._t.quest.scene.typing", timeout=10000)
        pg.locator('#cbOv .qfw').click(); pg.wait_for_timeout(40)
    pg.wait_for_function("() => document.querySelector('#cbOv .qtap.on')", timeout=10000)


def use(pg, hands, fill=True):
    """次に 配る 戦の 手札（1ターン）：配る 前に 決める（フィールドの 敵を タップ・「第○戦へ」・「もう 一度 挑戦」の 前）。fill：調査隊切符も 満タンに"""
    pg.evaluate(f"() => {{ window.__qh = {json.dumps({'turns': 1, 'hands': hands})}; CBApp._qopt = () => window.__qh; }}")
    if fill: pg.evaluate(TKFULL)


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


def tkg(pg):
    """第4.203版：調査隊切符の ゲージ（マップの 上）：枚数の 字・うめた こま（右を 何% かくすか）・次の 1枚 まで・場所（ゲージ・マップ・上の 文・枚数の 字）"""
    return pg.evaluate("""() => { const g = document.querySelector('#cbOv .qtg'), m = document.querySelector('#cbOv .qmap'), s = document.querySelector('#cbOv .qmst'), f = g.querySelector('.f');
      const r = g.getBoundingClientRect(), mr = m.getBoundingClientRect(), nr = g.querySelector('.n').getBoundingClientRect(), cp = /inset\\(\\S+ ([\\d.]+)%/.exec(f.style.clipPath);
      return { n: g.querySelector('.n').textContent, hide: cp ? parseFloat(cp[1]) : f.style.clipPath, rc: g.querySelector('.rc').textContent, aria: g.getAttribute('aria-label') || '',
        g: [r.left, r.top, r.width, r.height], m: [mr.left, mr.top, mr.width, mr.height], mst: s.getBoundingClientRect().bottom, num: [nr.right, nr.top + nr.height / 2, nr.height],
        iw: innerWidth, ih: innerHeight, img: [...g.querySelectorAll('img')].map(i => i.complete && i.naturalWidth > 0), vis: getComputedStyle(g).display !== 'none' && r.width > 0 }; }""")


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

        print('■ フィールド（第4.200版：まさちゃんの セリフの 表 → その 行で 敵 出現）')
        pg.locator('#cbOv .qnd[data-lv="1"]').click(); pg.wait_for_timeout(120)
        pg.locator('#cbOv .qpo [data-cb=qgo]').click()
        pg.wait_for_function("() => CBApp._t.quest.scene && CBApp._t.quest.scene.i === 0", timeout=10000)
        check(scr(pg) == 'qf' and q(pg)['track'] == '', 'フィールドの 画面・BGM は 止まる（敵が 出る 音を 聞かせる）')
        data = pg.evaluate("() => CBApp._t.quest.data.map(x => [x.say, x.en])")
        check(data == SAY, f'セリフ 12 エリア ぶん：まさちゃんの 表（11/18 22:54）の まま・何行目で 敵が 出るか（{[len(x[0]) for x in data]} 行・敵 {[x[1] for x in data]} 行目）')
        say = data[0][0]
        check(not pg.locator('#cbOv .qsay .who').count(), 'セリフの 窓に「あなた」の 札は 出さない（セリフに 話す 人が 入って いる）')
        pg.evaluate("() => CBApp._t.speed(1)")      # 字が 1つずつ 出る ところを 見る
        pg.wait_for_timeout(120)
        tw = pg.evaluate("() => { const p = document.querySelector('#cbOv .qsay p'); return [(p.querySelector('.sh') || p).textContent.length, CBApp._t.quest.scene.typing]; }")
        check(0 < tw[0] < len(say[0]) and tw[1], f'セリフは 字が 1つずつ 出る（{tw[0]}字 ／ {len(say[0])}字）')
        pg.locator('#cbOv .qfw').click(); pg.wait_for_timeout(60)
        check(pg.locator('#cbOv .qsay p').inner_text() == say[0] and q(pg)['scene']['i'] == 0, 'とちゅうで タップ → その 行が すぐ ぜんぶ 出る（次へは まだ）')
        fs = pg.evaluate("() => parseFloat(getComputedStyle(document.querySelector('#cbOv .qsay p')).fontSize)")
        check(fs >= 17, f'セリフの 字は 読みやすい 大きさ（{fs}px）')
        en0 = pg.evaluate("() => [getComputedStyle(document.querySelector('#cbOv .qfld .qe')).opacity, !!document.querySelector('#cbOv .qtel.on'), CBApp._t.quest.scene.rv]")
        check(float(en0[0]) == 0 and not en0[1] and en0[2] == 0, f'1行目「{say[0]}」：敵は まだ 見えない・テロップも まだ')
        shot(pg, 'q03_say')
        pg.evaluate("() => CBApp._t.speed(0.03)")
        pg.locator('#cbOv .qfw').click()
        pg.wait_for_function("() => CBApp._t.quest.scene.i === 1 && !CBApp._t.quest.scene.typing && CBApp._t.quest.scene.rv === 2", timeout=10000); pg.wait_for_timeout(900)
        tel = pg.locator('#cbOv .qtel').inner_text()
        r1 = pg.evaluate("() => [+getComputedStyle(document.querySelector('#cbOv .qfld .qe')).opacity, document.querySelector('#cbOv .qsay').classList.contains('on'), document.querySelector('#cbOv .qsay p').textContent, document.querySelector('#cbOv .qnm').classList.contains('on'), document.querySelector('#cbOv .qtap').classList.contains('on'), CBApp._t.quest.scene.step]")
        check('レベル1の 敵 出現！' in tel and '1連勝して バトルコインを 10枚 手に入れよう！' in tel and r1[0] > 0.99 and r1[1] and r1[2] == say[1],
              f'タップ → 2行目「{say[1]}」と いっしょに 上の テロップ・敵が 出る（セリフの 窓は その まま）')
        check(not r1[3] and not r1[4] and r1[5] == 'say', '敵が 出ても まだ セリフの とちゅう（名前・「タップで バトル開始！」は まだ）')
        shot(pg, 'q04_reveal')
        pg.locator('#cbOv .qfw').click()
        pg.wait_for_function("() => document.querySelector('#cbOv .qtap.on')", timeout=10000); pg.wait_for_timeout(1200)
        check(pg.locator('#cbOv .qnm').inner_text() == '若草の鈴駒' and not pg.locator('#cbOv .qsay').evaluate("e => e.classList.contains('on')") and q(pg)['scene']['step'] == 'en',
              'さいごの 行の あと タップ → セリフの 窓が 消える → 敵の 名前「若草の鈴駒」→「タップで バトル開始！」')
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
        check(q(pg)['track'] == 'quest' and q(pg)['run'] == {'lv': 1, 'won': 0, 'm': '2026-11', 'gu': []}, 'BGM は 決戦調査の 曲・いまの 調査（レベル1・0勝・第4.197版：使った 決戦宝石 なし）')
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
        # 第4.206版（まさちゃん 11/19 19:07「決戦調査で、抜け穴やバクなどないか確認して！」）：窓を 開いた まま 月が 進んだ（月末の 夜中）→
        #   バトル開始・第○戦へ・もう 一度 挑戦 の 前に 止める（この 調査は なし・調査隊切符は 使わない）。前は 切符を 使って 戦った あとで「月が 変わったよ」
        TKN = lambda: pg.evaluate("() => CBApp._t.qt.n")
        pg.evaluate("() => { window.__now = '2027-01-31T23:58:00'; }")
        go_field(pg, 1); use(pg, WIN)
        pg.evaluate("() => { window.__now = '2027-02-01T00:02:00'; }")
        n0 = TKN(); pg.locator('#cbOv .qfw').click(); pg.wait_for_timeout(250)
        t = mod_text(pg)
        check('月が 変わったよ' in t and '調査隊切符は 使って いないよ' in t and TKN() == n0 and scr(pg) == 'qf' and st(pg)['q'] == {'m': '2027-02', 'clr': 0},
              f'フィールドで 月が 進んだ：バトルに 入らない・切符は 使わない（{n0} → {TKN()}）')
        pg.locator('#cbOv .cbmod [data-cb=qmapgo]').click(); pg.wait_for_timeout(200)
        check(scr(pg) == 'qmap' and '2月の 討伐 0／12' in pg.locator('#cbOv .qmst').inner_text(), '「マップへ」→ 新しい 月の マップ')
        pg.evaluate("() => CBApp._t.qApi.clr()"); pg.wait_for_timeout(150)      # レベル1 を 討伐済みに（レベル2 ＝ 2連勝）
        pg.evaluate("() => { window.__now = '2027-02-28T23:50:00'; }")
        go_field(pg, 2); use(pg, WIN); pg.locator('#cbOv .qfw').click(); battle(pg, WIN, '7')
        check('第2戦へ' in mod_text(pg), 'レベル2 の 1戦目に 勝った（あいだの 窓）')
        pg.evaluate("() => { window.__now = '2027-03-01T00:01:00'; }")
        n0 = TKN(); pg.locator('#cbOv .cbmod [data-cb=qnext]').click(); pg.wait_for_timeout(250)
        t = mod_text(pg)
        check('月が 変わったよ' in t and TKN() == n0 and pg.evaluate("() => CBApp._t.ended") and st(pg)['q'] == {'m': '2027-03', 'clr': 0},
              f'あいだの 窓で 月が 進んだ：「第2戦へ」で 止める（次の 戦は 配らない・切符 {n0} → {TKN()}）')
        pg.locator('#cbOv .cbmod [data-cb=qmapgo]').click(); pg.wait_for_timeout(200)
        pg.evaluate("() => { window.__now = '2027-03-31T23:50:00'; }")
        go_field(pg, 1); use(pg, LOSE); pg.locator('#cbOv .qfw').click(); battle(pg, LOSE, 'k')
        check('調査 失敗…' in mod_text(pg), 'レベル1 に 負けた（負けの 窓）')
        pg.evaluate("() => { window.__now = '2027-04-01T00:01:00'; }")
        n0 = TKN(); pg.locator('#cbOv .cbmod [data-cb=qretry]').click(); pg.wait_for_timeout(250)
        t = mod_text(pg)
        check('月が 変わったよ' in t and TKN() == n0 and pg.evaluate("() => CBApp._t.ended") and st(pg)['q'] == {'m': '2027-04', 'clr': 0},
              f'負けの 窓で 月が 進んだ：「もう 一度 挑戦」で 止める（切符は 使わない {n0} → {TKN()}）')
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

        print('■ 決戦宝石（第4.197版・まさちゃん 18:58「呼び寄せの決戦宝石」・19:46「決戦調査は、決戦宝石あり、なしの選択はいらないよ！ 無条件であり！」・20:20「1クエスト連勝継続中に合計5個しか使えない！」・「決戦調査の時は、自分だけが見える」・19:03「手札が6枚以下の場合ね！」）')
        pg.evaluate("() => { const T = CBApp._t; T.state.gq = false; T.save(); T.load(); }")      # 前の テスト版で 覚えた「なし」が のこって いても いつも あり
        pg.locator('#cbOv .cbmenu [data-cb=quest]').click(); pg.wait_for_timeout(250)
        lv0 = q(pg)['open']
        pg.locator(f'#cbOv .qnd[data-lv="{lv0}"]').click(); pg.wait_for_timeout(250)
        o0 = pop(pg)
        g0 = pg.evaluate("() => { const e = document.querySelector('#cbOv .qmap .qpo'); return e ? { seg: e.querySelectorAll('[data-cb=qgem], .cbseg').length, t: e.innerText } : null; }")
        qo = pg.evaluate(f"() => CBApp._t.qopt({lv0}, 0)")
        check(o0 and o0['go'] and g0 and g0['seg'] == 0 and '決戦宝石' not in g0['t'] and 'gq' not in st(pg),
              f'ふきだしに 決戦宝石の「なし／あり」は ない（決戦調査は いつも あり・前に 覚えた 設定も すてる）{g0 and g0["t"]!r}')
        check(qo.get('gems') == [['m', 'k', '1', '3', '7'], []] and qo.get('gused') == [[], []] and qo.get('gpub') is False, f'決戦調査の 戦の 決まり：いつも あなたに 宝石 5つ・敵は なし・敵には 知らせない（gems {qo.get("gems")}・gpub {qo.get("gpub")}）')
        pg.locator('#cbOv .qpo [data-cb=qpx]').click(); pg.wait_for_timeout(120)
        H6 = {'turns': 1, 'hands': [['1', '2', '3', '4', '5', '6'], ['7', '7', '6', '2', '3', '1']]}      # 手札 6まい（1ターン目から 宝石が 使える）
        GQS = """() => { const g = document.querySelector('#cbOv .cbgem'), o = document.querySelector('#cbOv .cbopp .ogem'), R = e => e.getBoundingClientRect();
          return { hid: g.hidden, gs: [...g.querySelectorAll('.g')].map(b => b.dataset.g + ':' + [...b.classList].filter(c => c !== 'g').join('.')).join(' '), og: o.hidden, msg: document.querySelector('#cbOv .cbmsg').textContent,
            ok: R(g).top >= Math.max(...[...document.querySelectorAll('#cbOv .cbhand .cbc')].map(c => R(c).bottom)) - 1 && R(g).bottom <= R(document.querySelector('#cbOv .cbact')).top + 1 && R(document.querySelector('#cbOv .cbact')).bottom <= innerHeight }; }"""
        # レベル lv1（2連勝 以上）：1戦目に 日輪の黄金石 → 2戦目は のこりの 4つ
        lv1 = lv0 + 1 if lv0 < 12 else lv0
        pg.evaluate(f"() => {{ CBApp._t.state.q.clr = {lv1 - 1}; CBApp._t.save(); }}"); pg.locator('#cbOv [data-cb=qx]').click(); pg.locator('#cbOv .cbmenu [data-cb=quest]').click(); pg.wait_for_timeout(250)
        go_field(pg, lv1); use(pg, H6['hands'])
        pg.locator('#cbOv .qfw').click()
        pg.wait_for_function("() => CBApp._t.screen === 'game' && CBApp._t.view && CBApp._t.view.can.set", timeout=20000); idle(pg)
        bq = pg.evaluate(GQS)
        check(not bq['hid'] and bq['gs'] == 'm:can k:can 1:can 3:can 7:can' and bq['og'] and 'セットの 前なら 決戦宝石を 使えるよ' in bq['msg'] and bq['ok'],
              f'決戦調査の 1戦目：手札の 下に 宝石ケース（5つ・手札 6枚 → 使える）・敵の 宝石は 出ない（{bq["gs"]}）')
        shot(pg, 'q15_gem_battle')
        pg.locator('#cbOv .cbgem .g[data-g="k"]').click(); pg.wait_for_timeout(80); pg.locator('#cbOv .cbmod.cbgemm [data-cb=gemgo]').click(); idle(pg)
        ban = said(pg)
        lk = pg.evaluate("() => { const S = CBApp._t.match._.state(), w = CBRules.view(S, 1), t = S.p[0].hand.find(c => c.tok); return { tok: t ? t.k + '×' + t.tok : '', known: w.op.hand.some(c => c.k), n: w.op.hand.length, eg: w.op.gem }; }")
        check(lk['tok'] == 'k×1' and not lk['known'] and lk['n'] == 7 and lk['eg'] is None and any('日輪の黄金石！' in x for x in ban),
              f'日輪の黄金石 → 神様馬トークン（敵には 知らせない：敵から 見ると ふつうの 伏せた カード・宝石も 見えない {lk}）')
        pg.locator('#cbOv .cbhand .cbc.tok[data-ck="k"]').click(); pg.wait_for_timeout(60); pg.locator('#cbOv .cbmod [data-cb=set]').click(); pg.wait_for_timeout(80)
        pg.evaluate(OPP, {'t': 'set', 'k': '7'})
        pg.wait_for_function("() => CBApp._t.ended && document.querySelector('#cbOv .cbmod.on.qend')", timeout=30000); pg.wait_for_timeout(150)
        gl = pg.evaluate("() => { const e = document.querySelector('#cbOv .cbmod.qend .qgl'); return e ? { t: e.textContent, u: [...e.querySelectorAll('img')].map(i => i.classList.contains('u') ? 1 : 0).join('') } : null; }")
        check(gl and gl['t'].startswith('決戦宝石 のこり 4／5') and gl['u'] == '01000' and q(pg)['run']['gu'] == ['k'], f'勝利！の 窓に「決戦宝石 のこり 4／5」（使った 日輪の黄金石は 暗く）{gl}')
        shot(pg, 'q16_gem_left')
        next_fight(pg); pg.wait_for_function("() => CBApp._t.view && CBApp._t.view.can.set", timeout=20000); idle(pg)
        b2 = pg.evaluate(GQS); s2 = said(pg)
        pg.locator('#cbOv .cbgem .g[data-g="k"]').click(); pg.wait_for_timeout(100); s3 = said(pg)
        check(b2['gs'] == 'm:can k:used 1:can 3:can 7:can' and any('この 調査では もう 使ったよ' in x for x in s3) and pg.evaluate("() => CBApp._t.view.my.gem.used.join('')") == 'k',
              f'第2戦：1戦目で 使った 日輪の黄金石は 使えない（暗い まま・タップ →「この 調査では もう 使ったよ」）・のこり 4つは 使える（{b2["gs"]}）')
        pg.locator('#cbOv .cbgem .g[data-g="m"]').click(); pg.wait_for_timeout(80)
        mt = pg.evaluate("() => (document.querySelector('#cbOv .cbmod.cbgemm p') || {}).textContent || ''")
        check('この 宝石は この 調査で 1回（連勝が 続く 間）' in mt, f'宝石の 窓：「この 宝石は この 調査で 1回」（{mt[-40:]!r}）')
        pg.locator('#cbOv .cbmod.cbgemm [data-cb=modx]').click(); pg.wait_for_timeout(80)
        # 負けて 連勝が 切れる → もう 一度 挑戦 → 5つに 戻る
        pg.locator('#cbOv .cbgem .g[data-g="m"]').click(); pg.wait_for_timeout(80); pg.locator('#cbOv .cbmod.cbgemm [data-cb=gemgo]').click(); idle(pg)
        pg.locator('#cbOv .cbhand .cbc:not(.tok)[data-ck="6"]').first.click(); pg.wait_for_timeout(60); pg.locator('#cbOv .cbmod [data-cb=set]').click(); pg.wait_for_timeout(80)
        pg.evaluate(OPP, {'t': 'set', 'k': '1'})      # 6 と 1（数字は 小さい ほど 強い）→ 負け
        pg.wait_for_function("() => CBApp._t.ended && document.querySelector('#cbOv .cbmod.on.qend')", timeout=30000); pg.wait_for_timeout(150)
        lt = mod_text(pg)
        check('調査 失敗' in lt and '決戦宝石も 5つに 戻るよ' in lt and q(pg)['run']['gu'] == ['k', 'm'], f'負け（調査 失敗）：「もう 一度 1戦目から 挑戦できるよ（決戦宝石も 5つに 戻るよ）」（使ったのは {q(pg)["run"]["gu"]}）')
        pg.locator('#cbOv .cbmod [data-cb=qretry]').click()
        pg.wait_for_function("() => CBApp._t.view && CBApp._t.view.phase !== 'end' && CBApp._t.view.can.set", timeout=20000); idle(pg)
        b3 = pg.evaluate(GQS)
        check(b3['gs'] == 'm:can k:can 1:can 3:can 7:can' and q(pg)['run']['gu'] == [] and q(pg)['run']['won'] == 0, f'もう 一度 挑戦（1戦目から）→ 決戦宝石は 5つ ぜんぶ 使える（{b3["gs"]}）')
        # 1戦目：双炎のルビー → 同点（6 と 6）→ やり直しは 連勝が 続く ので 使った 宝石は 戻らない
        pg.locator('#cbOv .cbgem .g[data-g="1"]').click(); pg.wait_for_timeout(80); pg.locator('#cbOv .cbmod.cbgemm [data-cb=gemgo]').click(); idle(pg)
        pg.locator('#cbOv .cbhand .cbc:not(.tok)[data-ck="6"]').first.click(); pg.wait_for_timeout(60); pg.locator('#cbOv .cbmod [data-cb=set]').click(); pg.wait_for_timeout(80)
        pg.evaluate(OPP, {'t': 'set', 'k': '6'})
        pg.wait_for_function("() => CBApp._t.ended && document.querySelector('#cbOv .cbmod.on.qend')", timeout=30000); pg.wait_for_timeout(150)
        dt = mod_text(pg); gd = pg.evaluate("() => { const e = document.querySelector('#cbOv .cbmod.qend .qgl'); return e ? e.textContent : ''; }")
        next_fight(pg); pg.wait_for_function("() => CBApp._t.view && CBApp._t.view.can.set", timeout=20000); idle(pg)
        b4 = pg.evaluate(GQS)
        check('同点' in dt and gd.startswith('決戦宝石 のこり 4／5') and b4['gs'] == 'm:can k:can 1:used 3:can 7:can', f'同点 → 同じ 戦を やり直し：連勝は 続く ので 使った 双炎のルビーは 戻らない（{b4["gs"]}）')
        pg.locator('#cbOv .cbtop [data-cb=quit]').click(); pg.wait_for_timeout(80); pg.locator('#cbOv .cbmod [data-cb=quitgo]').click(); pg.wait_for_timeout(300)
        if scr(pg) != 'qmap': pg.locator('#cbOv .cbmod [data-cb=qmapgo]').click(); pg.wait_for_timeout(200)
        pg.evaluate(f"() => {{ CBApp._t.state.q.clr = {lv0 - 1}; CBApp._t.save(); }}")
        if scr(pg) == 'qmap': pg.locator('#cbOv [data-cb=qx]').click(); pg.wait_for_timeout(150)
        else: pg.evaluate("() => CBApp._t.menu()"); pg.wait_for_timeout(150)

        print('■ 12 エリアの セリフと 敵が 出る 行（第4.200版・まさちゃんの 表）')
        LAY = """() => { const b = document.querySelector('#cbOv .qsay').getBoundingClientRect(), e = document.querySelector('#cbOv .qfld .qe').getBoundingClientRect(), t = document.querySelector('#cbOv .qtel .bd').getBoundingClientRect();
          return { top: b.top, bot: b.bottom, hoof: e.top + e.height / 1.42, eh: e.height, et: e.top, tel: t.bottom, vh: innerHeight, op: +getComputedStyle(document.querySelector('#cbOv .qfld .qe')).opacity,
            on: document.querySelector('#cbOv .qsay').classList.contains('on'), telon: !!document.querySelector('#cbOv .qtel.on'), txt: document.querySelector('#cbOv .qsay p').textContent, rv: CBApp._t.quest.scene.rv }; }"""
        bad12 = []; cov = []
        for lv in range(1, 13):
            pg.evaluate(f"() => {{ CBApp._t.state.q.clr = {lv - 1}; CBApp._t.save(); }}")
            if scr(pg) == 'qmap': pg.locator('#cbOv [data-cb=qx]').click(); pg.wait_for_timeout(100)
            elif scr(pg) != 'menu': pg.evaluate("() => CBApp._t.menu()"); pg.wait_for_timeout(100)
            pg.locator('#cbOv .cbmenu [data-cb=quest]').click(); pg.wait_for_timeout(200)
            pg.locator(f'#cbOv .qnd[data-lv="{lv}"]').click(); pg.wait_for_timeout(120); pg.locator('#cbOv .qpo [data-cb=qgo]').click()
            sy, en = SAY[lv - 1]
            for i in range(len(sy)):
                pg.wait_for_function(f"() => CBApp._t.quest.scene.i === {i} && !CBApp._t.quest.scene.typing", timeout=10000)
                if i >= en - 1: pg.wait_for_function("() => CBApp._t.quest.scene.rv === 2", timeout=10000); pg.wait_for_timeout(950)
                L = pg.evaluate(LAY)
                if L['txt'] != sy[i] or not L['on']: bad12.append(f'Lv{lv} {i + 1}行目の 文')
                if i < en - 1 and (L['op'] > 0.01 or L['telon'] or L['rv']): bad12.append(f'Lv{lv} {i + 1}行目：敵が もう 見える')
                if i >= en - 1:
                    if L['op'] < 0.99 or not L['telon']: bad12.append(f'Lv{lv} {i + 1}行目：敵・テロップが 見えない')
                    cov.append(max(0.0, L['hoof'] - L['top']))
                    if L['hoof'] - L['top'] > 8 or L['et'] < L['tel'] - 2 or L['bot'] > L['vh']: bad12.append(f'Lv{lv} {i + 1}行目：窓が 敵に かかる（{L["hoof"] - L["top"]:.0f}px）')
                if lv == 12 and i == 2: shot(pg, 'q17_lv12_reveal')
                pg.locator('#cbOv .qfw').click()
            pg.wait_for_function("() => document.querySelector('#cbOv .qtap.on')", timeout=10000); pg.wait_for_timeout(300)
            e1 = pg.evaluate("() => [document.querySelector('#cbOv .qnm').textContent, document.querySelector('#cbOv .qsay').classList.contains('on'), CBApp._t.quest.scene.step]")
            if e1 != [pg.evaluate(f"() => CBApp._t.quest.data[{lv - 1}].n"), False, 'en']: bad12.append(f'Lv{lv} さいご {e1}')
            pg.locator('#cbOv [data-cb=qback]').click(); pg.wait_for_timeout(250)
            if scr(pg) != 'qmap': bad12.append(f'Lv{lv}：「← マップ」で マップに 戻らない（{scr(pg)}）')
        check(not bad12, f'12 エリア：1タップで 1行・表の 行で テロップと 敵が 出る（その 前は 見えない）・Lv12 は 3行目で 女王 → 4行目・さいごの 行の あと 名前 と「タップで バトル開始！」・'
                         f'窓は 敵の 蹄に かからない（かかって いちばん {max(cov):.0f}px）{bad12[:4]}')
        pg.evaluate("() => { CBApp._t.state.q.clr = 0; CBApp._t.save(); }")
        if scr(pg) == 'qmap': pg.locator('#cbOv [data-cb=qx]').click(); pg.wait_for_timeout(100)
        pg.evaluate("() => { const T = CBApp._t; if (T.screen !== 'menu') T.menu(); }"); pg.wait_for_timeout(100)

        print('■ セリフの 字は 行の はしで とばない（第4.208版・まさちゃん 11/20 01:42「決戦調査のセリフが、文字の段が変わる時に、文字がガタガタ段が変わってるから！おかしくならないように改善して！」）')
        WATCH = """() => new Promise(res => {
          const p = document.querySelector('#cbOv .qsay p'), box = document.querySelector('#cbOv .qsay'), rec = {}; let h0 = null, b0 = null;
          const at = k => { const w = document.createTreeWalker(p, NodeFilter.SHOW_TEXT); let n, o = k;
            while ((n = w.nextNode())) { if (o < n.length) { const r = document.createRange(); r.setStart(n, o); r.setEnd(n, o + 1); const b = r.getBoundingClientRect(), q = p.getBoundingClientRect(); return [b.left - q.left, b.top - q.top]; } o -= n.length; }
            return null; };
          const tick = () => {
            const sh = p.querySelector('.sh'), shown = sh ? sh.textContent.length : p.textContent.length;
            if (shown > 0 && h0 === null) { h0 = p.getBoundingClientRect().height; b0 = box.getBoundingClientRect().top; }
            for (let k = 0; k < shown; k++) if (!(k in rec)) rec[k] = at(k);
            if (CBApp._t.quest.scene.typing) return setTimeout(tick, 6);
            const moved = []; for (const k in rec) { const f = at(+k); if (!f || !rec[k] || Math.abs(f[0] - rec[k][0]) > 0.5 || Math.abs(f[1] - rec[k][1]) > 0.5) moved.push(+k); }
            res({ n: Object.keys(rec).length, len: p.textContent.length, moved, h0, h1: p.getBoundingClientRect().height, b0, b1: box.getBoundingClientRect().top,
                  lines: Math.round(p.getBoundingClientRect().height / parseFloat(getComputedStyle(p).lineHeight)), hd: !!p.querySelector('.hd') && getComputedStyle(p.querySelector('.hd')).visibility });
          };
          tick();
        })"""
        bad_w = []; seen_w = []
        for lv, li in ((12, 2), (5, 2), (7, 1), (6, 2), (11, 2), (9, 1)):
            pg.evaluate(f"() => {{ CBApp._t.state.q.clr = {lv - 1}; CBApp._t.save(); }}")
            if scr(pg) == 'qmap': pg.locator('#cbOv [data-cb=qx]').click(); pg.wait_for_timeout(100)
            elif scr(pg) != 'menu': pg.evaluate("() => CBApp._t.menu()"); pg.wait_for_timeout(100)
            pg.locator('#cbOv .cbmenu [data-cb=quest]').click(); pg.wait_for_timeout(200)
            pg.locator(f'#cbOv .qnd[data-lv="{lv}"]').click(); pg.wait_for_timeout(120); pg.locator('#cbOv .qpo [data-cb=qgo]').click()
            for i in range(li):
                pg.wait_for_function(f"() => CBApp._t.quest.scene.i === {i} && !CBApp._t.quest.scene.typing", timeout=10000)
                if i == li - 1: pg.evaluate("() => CBApp._t.speed(1)"); pg.wait_for_timeout(700)      # この 行は 字を ふつうの 速さで（1字 34ミリ秒）・窓が 出る 動きが おわって から
                pg.locator('#cbOv .qfw').click()
            w = pg.evaluate(WATCH); pg.evaluate("() => CBApp._t.speed(0.03)")
            seen_w.append(f'Lv{lv} {li + 1}行目 {w["lines"]}段')
            if w['moved'] or w['n'] != w['len'] or abs(w['h0'] - w['h1']) > 0.5 or abs(w['b0'] - w['b1']) > 0.5 or w['lines'] < 2 or w['hd'] != 'hidden':
                bad_w.append(f"Lv{lv} {li + 1}行目：動いた 字 {w['moved'][:6]}・{w['n']}/{w['len']}字・高さ {w['h0']:.1f}→{w['h1']:.1f}・窓 {w['b0']:.1f}→{w['b1']:.1f}・{w['lines']}段・{w['hd']}")
            pg.evaluate("() => CBApp._t.menu()"); pg.wait_for_timeout(150)
        check(not bad_w, f'セリフの 字は 出た 場所から 動かない（行の はしで 次の 段へ とばない）・窓の 高さは はじめから さいごまで 同じ・まだの 字は 見えない（{"・".join(seen_w)}）{bad_w[:3]}')
        pg.evaluate("() => { CBApp._t.state.q.clr = 0; CBApp._t.save(); }")

        print('■ あそび方・エラー')
        pg.locator('#cbOv .cbmenu [data-cb=help]').click(); pg.wait_for_timeout(200)
        hl = pg.locator('#cbOv .cbhelp').inner_text()
        check('⚔️ 決戦調査' in hl and 'Lv12 6連勝 250枚' in hl and '毎月 1日に リセット' in hl and '同じ 戦を やり直し' in hl, '遊び方に「⚔️ 決戦調査」（連勝・コイン・同点・リセット）')
        check('決戦宝石' in hl and '決戦調査では いつも 使えるよ' in hl and '5つ 1回ずつ（合計 5個）' in hl and '1試合で 5つ 1回ずつ' in hl and '幻影のアメジスト＝幻の馬トークン' in hl and '三峰の翡翠＝7トークン（1枚で 3頭分）' in hl and '手札が 6枚 以下' in hl and 'その ターン だけ' in hl, '第4.197版：遊び方に「決戦宝石」（決戦調査は いつも・1つの 調査で 5つ 1回ずつ・友達との 対戦は 1試合で 5つ・使える とき・その ターン だけ）')
        hi = pg.evaluate("() => { const h = document.querySelector('#cbOv .cbhelp'), li = [...h.querySelectorAll('li')].find(e => e.textContent.indexOf('調査隊切符') >= 0), i = li && li.querySelector('img.tki'); return { emo: /[💎🎫]/u.test(h.textContent), first: !!(li && li.firstElementChild === i), src: i && i.getAttribute('src'), ok: !!i && i.complete && i.naturalWidth > 0, gh: [...h.querySelectorAll('h4')].map(e => e.textContent).filter(x => x.indexOf('決戦宝石') >= 0) }; }")
        check(not hi['emo'] and hi['first'] and hi['src'] == 'cb_q_tk.webp' and (hi['ok'] or not HAVE) and hi['gh'] == ['決戦宝石'], f'第4.205版：遊び方に 💎・🎫 は ない（見出しは「決戦宝石」）・調査隊切符の 行の 頭は 切符の 絵 {hi}')
        check(not errs, f'画面の エラー なし {errs[:3]}')
        ctx.close()

        print('■ 調査隊切符（第4.203版・まさちゃん 01:42「調査隊切符」〜 01:53「調査隊切符ゲージの配置」：3分で 1枚 たまる・はじめ 15枚・0枚は 行けない／第4.204版 09:35：挑戦 1回に 1枚・連勝中は 使わない・負けたら 1枚／第4.207版 11/20 00:44：8分で 1枚／第4.208版 01:42：30分で 1枚 たまる）')
        src = open(os.path.join(W, 'cb', 'cb_app.js'), encoding='utf8').read()
        mq = re.search(r'const QTG = \{ cut: \[([^\]]+)\], right: ([\d.]+), mid: ([\d.]+), ar: ([\d.]+) \}', src)
        CUT = [float(x) for x in mq.group(1).split(',')]; QR, QM, QAR = (float(mq.group(i)) for i in (2, 3, 4))
        cg = re.search(r'#cbOv \.qtg\{[^}]*aspect-ratio:([\d.]+)', src); cn = re.search(r'#cbOv \.qtg \.n\{[^}]*right:([\d.]+)%;top:([\d.]+)%', src)
        check(len(CUT) == 16 and CUT[0] == 0 and CUT[-1] == 100 and all(x < y for x, y in zip(CUT, CUT[1:])) and float(cg.group(1)) == QAR and abs(float(cn.group(1)) - QR) < 0.01 and abs(float(cn.group(2)) - QM) < 0.01,
              f'ゲージの 決まり（QTG）：こまの 切れ目 16こ（0〜100%）・CSS の たて横（{cg.group(1)}）と 枚数の 字の 場所（右 {cn.group(1)}%・上 {cn.group(2)}%）が QTG と 同じ')
        if HAVE:
            from PIL import Image
            import numpy as np
            fa = np.asarray(Image.open(os.path.join(CBA, 'cb_q_tgf.webp')).convert('RGBA'))[..., 3].astype(int); gi = Image.open(os.path.join(CBA, 'cb_q_tg.webp')); FW = fa.shape[1]
            gap = [int(fa[:, max(0, int(c / 100 * FW) - 2):int(c / 100 * FW) + 3].max()) for c in CUT[1:-1]]
            box = [int((fa[:, int(np.ceil(CUT[i] / 100 * FW)):int(CUT[i + 1] / 100 * FW)] > 128).sum()) for i in range(15)]
            check(max(gap) <= 8 and min(box) > 600 and gi.size == (fa.shape[1], fa.shape[0]) and abs(gi.size[0] / gi.size[1] / QAR - 1) < 0.005,
                  f'絵：うめた こま（cb_q_tgf.webp）は 切れ目では すき通し（{max(gap)}）・こま 15こ ぜんぶ 金（いちばん 少ない こまで {min(box)}px）・ゲージ（cb_q_tg.webp）と 同じ 大きさ {gi.size}')
            if os.path.isfile(os.path.join(CBA, 'src', 'cb_quest_ticket_gauge.png')):
                import cb_ticket_art
                c = cb_ticket_art.css()
                check(c['cut'] == CUT and c['right'] == QR and c['mid'] == QM and c['ar'] == QAR, f'QTG は まさちゃんの ゲージの 絵から 出した 数（kisekae/cb_ticket_art.py css）と 同じ')
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2 if SHOT else 1, locale='ja-JP', timezone_id='Asia/Tokyo')
        ctx.add_init_script(FAKE)
        pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(APP); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(5200)
        open_cb(pg); pg.evaluate("() => { CBApp._t.load(); CBApp._t.menu(); }"); pg.wait_for_timeout(200)
        T0 = '2026-11-18T12:00:00'      # open_cb の CBApp._now（window.__now が ない とき）
        TM = lambda t: pg.evaluate("t => { window.__now = t; CBApp._t.qtPaint(); }", t)      # 時計を すすめる（テスト用の CBApp._now）→ すぐ 書き直す（ふだんは 1秒 ごと）
        MSOF = lambda t: pg.evaluate("t => new Date(t).getTime()", t)
        TK = lambda: pg.evaluate("() => CBApp._t.qt")
        TKIMG = "s => { const i = document.querySelector(s); if (!i) return null; const r = i.getBoundingClientRect(); return { src: i.getAttribute('src'), ok: i.complete && i.naturalWidth > 0, h: r.height, w: r.width, first: i.parentElement.firstElementChild === i && i.parentElement.firstChild === i }; }"      # 第4.205版：字の 横の 切符の 絵
        pg.locator('#cbOv .cbmenu [data-cb=quest]').click(); pg.wait_for_timeout(300)
        g = tkg(pg)
        check(g['vis'] and g['n'] == '15' and g['hide'] == 0 and g['rc'] == '' and TK()['n'] == 15 and '調査隊切符 15／15枚' in g['aria'], f'はじめは 15枚：マップの 上の ゲージに「15」・こま 15こ ぜんぶ 金・「次の 1枚 まで」は 出ない {[g["n"], g["hide"], g["rc"]]}')
        check(abs(g['g'][2] - g['m'][2]) <= 1 and abs(g['g'][0] - g['m'][0]) <= 1 and 4 <= g['m'][1] - g['g'][1] - g['g'][3] <= 8 and g['g'][1] >= g['mst'] - 1,
              f'ゲージは マップの すぐ 上（まさちゃんの 配置の 絵：マップと 同じ 幅 {g["g"][2]:.0f}／{g["m"][2]:.0f}px・あいだ {g["m"][1] - g["g"][1] - g["g"][3]:.1f}px・上の 文と 重ならない）')
        check(abs(g['g'][3] - g['g'][2] / QAR) <= 1 and g['g'][0] >= 0 and g['g'][0] + g['g'][2] <= g['iw'] and g['m'][1] + g['m'][3] <= g['ih'], f'ゲージの たて横は 絵の まま（{g["g"][2]:.0f}×{g["g"][3]:.1f}）・ゲージも マップも 画面の 中')
        nx, ny = g['g'][0] + g['g'][2] * (1 - QR / 100), g['g'][1] + g['g'][3] * QM / 100
        check(abs(g['num'][0] - nx) <= 2 and abs(g['num'][1] - ny) <= 3 and g['num'][2] >= 12, f'枚数の 字は 絵の 中の「0」が あった 所（右の はし {g["num"][0]:.1f}／{nx:.1f}・たての まん中 {g["num"][1]:.1f}／{ny:.1f}・字の 高さ {g["num"][2]:.0f}px）')
        if HAVE: check(g['img'] == [True, True], 'ゲージの 絵（cb_q_tg.webp・うめた こま cb_q_tgf.webp）が 出る')
        shot(pg, 'tk01_map15')
        pg.locator('#cbOv .qnd[data-lv="1"]').click(); pg.wait_for_timeout(250)
        o = pop(pg)
        check(o and '挑戦に 調査隊切符 1枚（今 15枚）' in o['t'] and '連勝中は 使わないよ' in o['t'] and o['inside'] and pg.locator('#cbOv .qpo [data-cb=qgo]').is_enabled(), f'エリアの ふきだしに「挑戦に 調査隊切符 1枚（今 15枚）連勝中は 使わないよ」・「決戦調査に 行く」は 押せる {o and o["t"]!r}')
        tq = pg.evaluate(TKIMG, '#cbOv .qpo .qpotk img.tki')
        check(tq and tq['src'] == 'cb_q_tk.webp' and (tq['ok'] or not HAVE) and 15 <= tq['h'] <= 24 and 1.9 <= tq['w'] / tq['h'] <= 2.8 and tq['first'], f'第4.205版：ふきだしの 切符は 切符の 絵（🎫 では ない）・字の 高さに 合わせた 大きさ {tq}')
        shot(pg, 'tk02_pop15')
        pg.locator('#cbOv .qpo [data-cb=qpx]').click(); pg.wait_for_timeout(80)
        go_field(pg, 1, fill=False); use(pg, WIN, fill=False)
        check(TK()['n'] == 15, '「決戦調査に 行く」・セリフの 間は まだ 使わない（15枚 の まま）')
        said(pg); pg.locator('#cbOv .qfw').click()
        pg.wait_for_function("() => CBApp._t.screen === 'game'", timeout=20000)
        tq = pg.evaluate(TKIMG, '#cbOv .cbtoast img.tki')
        check(tq and tq['src'] == 'cb_q_tk.webp' and tq['first'] and '調査隊切符を 1枚 使ったよ' in pg.locator('#cbOv .cbtoast').inner_text(), f'第4.205版：知らせ「調査隊切符を 1枚 使ったよ」の 頭も 切符の 絵 {tq}')
        battle(pg, WIN, '7')
        t1 = TK()
        check(t1['n'] == 14 and t1['at'] == MSOF(T0) and t1['left'] == 1800000 and any('調査隊切符を 1枚 使ったよ\n（のこり 14枚）' in x for x in said(pg)),
              f'バトル 開始で 1枚 使う：14枚・満タンから 使った ので そこから 30分 数える・「調査隊切符を 1枚 使ったよ（のこり 14枚）」 {t1}')
        pg.wait_for_function("() => document.querySelector('#cbOv .qget.on') && document.querySelector('#cbOv .qget .n').textContent === '10'", timeout=10000); pg.wait_for_timeout(300)
        check(TK()['n'] == 14, '討伐（勝利の 演出）では 使わない')
        pg.locator('#cbOv .cbmod [data-cb=qmapgo]').click(); pg.wait_for_timeout(400)
        g = tkg(pg)
        check(g['n'] == '14' and abs(g['hide'] - (100 - CUT[14])) < 0.01 and g['rc'] == '次の 1枚 まで 30:00' and '14／15枚・次の 1枚 まで 30:00' in g['aria'], f'マップ：ゲージ「14」・こま 14こ 金（右の 1こは 空き）・「次の 1枚 まで 30:00」 {[g["n"], g["hide"], g["rc"]]}')
        shot(pg, 'tk03_map14')
        TM('2026-11-18T12:29:59'); g = tkg(pg)
        check(g['n'] == '14' and g['rc'] == '次の 1枚 まで 0:01', f'29分59秒 あと：まだ 14枚・「次の 1枚 まで 0:01」 {g["rc"]!r}')
        TM('2026-11-18T12:30:00'); g = tkg(pg)
        check(g['n'] == '15' and g['hide'] == 0 and g['rc'] == '' and TK()['n'] == 15, '30分で 1枚 たまる → 15枚（満タン：「次の 1枚 まで」は 消える）')
        # 第4.204版（まさちゃん 09:35「1試合1枚だけど、連続勝利中は使わないになってる？ クエストが変わったら1枚使うし、負けたら1枚使う！ クエスト変わったらは、例えばLv3からLv4に移動したらってことね！」）
        pg.evaluate("() => { CBApp._t.state.q.clr = 2; CBApp._t.save(); }"); pg.locator('#cbOv [data-cb=qx]').click(); pg.wait_for_timeout(100)
        pg.locator('#cbOv .cbmenu [data-cb=quest]').click(); pg.wait_for_timeout(250)
        go_field(pg, 3, fill=False); use(pg, WIN, fill=False); said(pg); pg.locator('#cbOv .qfw').click()
        battle(pg, WIN, '7')
        t = mod_text(pg); t1 = TK()
        check(t1['n'] == 14 and t1['at'] == MSOF('2026-11-18T12:30:00') and any('調査隊切符を 1枚 使ったよ\n（のこり 14枚）' in x for x in said(pg)) and '調査隊切符 のこり 14枚' in t and '連勝中は 使わないよ' in t,
              f'レベル3 に 挑戦：1戦目の はじめに 1枚（14枚）・1勝の 窓に「調査隊切符 のこり 14枚（連勝中は 使わないよ）」')
        nb = pg.locator('#cbOv .cbmod [data-cb=qnext]')
        check(nb.is_enabled() and nb.get_attribute('data-qt') is None and nb.inner_text().strip() == '第2戦へ', f'「第2戦へ」は 切符の いらない ボタン {nb.inner_text()!r}')
        tq = pg.evaluate(TKIMG, '#cbOv .cbmod .qtl img.tki'); gl = pg.locator('#cbOv .cbmod .qgl').inner_text()
        check(tq and tq['src'] == 'cb_q_tk.webp' and (tq['ok'] or not HAVE) and tq['first'] and 15 <= tq['h'] <= 26 and '💎' not in t and '🎫' not in t and gl.startswith('決戦宝石 のこり'),
              f'第4.205版：あいだの 窓：切符の 行の 頭は 切符の 絵・決戦宝石の 行に 💎 は ない {tq} {gl!r}')
        shot(pg, 'tk04_between14')
        use(pg, DRAW, fill=False); said(pg); next_fight(pg)
        check(TK()['n'] == 14 and not any('調査隊切符' in x for x in said(pg)), '連勝中：「第2戦へ」では 使わない（14枚の まま・知らせも ない）')
        battle(pg, DRAW, 'm')
        t = mod_text(pg)
        check('同点！' in t and '調査隊切符 のこり 14枚' in t and '連勝中は 使わないよ' in t and pg.locator('#cbOv .cbmod [data-cb=qnext]').get_attribute('data-qt') is None, '同点の 窓：のこり 14枚（連勝中は 使わないよ）・「第2戦を やり直す」も 切符 なし')
        use(pg, WIN, fill=False); said(pg); next_fight(pg)
        check(TK()['n'] == 14 and not any('調査隊切符' in x for x in said(pg)), '同点の「第2戦を やり直す」でも 使わない（14枚）')
        battle(pg, WIN, '7')
        use(pg, WIN, fill=False); said(pg); next_fight(pg)
        check(TK()['n'] == 14 and not any('調査隊切符' in x for x in said(pg)), '「第3戦へ」でも 使わない（14枚）')
        battle(pg, WIN, '7')
        pg.wait_for_function("() => document.querySelector('#cbOv .qget.on') && document.querySelector('#cbOv .qget .n').textContent === '30'", timeout=10000); pg.wait_for_timeout(300)
        check(TK()['n'] == 14 and st(pg)['q']['clr'] == 3, 'レベル3 を 3連勝で 討伐：使った 切符は 挑戦の 1枚 だけ（14枚）')
        pg.locator('#cbOv .cbmod [data-cb=qmapgo]').click(); pg.wait_for_timeout(400)
        pg.locator('#cbOv .qnd[data-lv="4"]').click(); pg.wait_for_timeout(250)
        o = pop(pg)
        check(o and '挑戦に 調査隊切符 1枚（今 14枚）' in o['t'] and o['inside'], f'レベル4 の ふきだし：「挑戦に 調査隊切符 1枚（今 14枚）」 {o and o["t"]!r}')
        pg.locator('#cbOv .qpo [data-cb=qpx]').click(); pg.wait_for_timeout(80)
        go_field(pg, 4, fill=False); use(pg, LOSE, fill=False); said(pg); pg.locator('#cbOv .qfw').click()
        battle(pg, LOSE, 'k')
        check(TK()['n'] == 13 and any('調査隊切符を 1枚 使ったよ\n（のこり 13枚）' in x for x in said(pg)), 'レベル3 → レベル4（クエストが かわった）：挑戦で 1枚（13枚）')
        t = mod_text(pg); rb = pg.locator('#cbOv .cbmod [data-cb=qretry]')
        check('調査 失敗…' in t and '調査隊切符 のこり 13枚' in t and 'もう 一度 挑戦は 1枚' in t and rb.is_enabled() and rb.get_attribute('data-qt') == '1', '負けの 窓：のこり 13枚（もう 一度 挑戦は 1枚）')
        shot(pg, 'tk05_lose13')
        use(pg, WIN, fill=False); said(pg); rb.click()
        pg.wait_for_function("() => CBApp._t.view && CBApp._t.view.phase !== 'end'", timeout=20000); idle(pg)
        check(TK()['n'] == 12 and any('調査隊切符を 1枚 使ったよ\n（のこり 12枚）' in x for x in said(pg)) and q(pg)['run']['won'] == 0, '負けて「もう 一度 挑戦」：1枚（12枚）・1戦目から')
        battle(pg, WIN, '7')
        pg.evaluate("t => { const T = CBApp._t; T.state.qt = { n: 0, at: t }; T.save(); T.qtPaint(); }", MSOF('2026-11-18T12:30:00'))
        nb = pg.locator('#cbOv .cbmod [data-cb=qnext]')
        check(nb.is_enabled() and nb.inner_text().strip() == '第2戦へ' and '調査隊切符 のこり 0枚' in mod_text(pg), f'0枚でも 連勝中は「第2戦へ」を 押せる {nb.inner_text()!r}')
        shot(pg, 'tk06_between0')
        use(pg, LOSE, fill=False); said(pg); next_fight(pg)
        check(TK()['n'] == 0 and q(pg)['run']['won'] == 1 and not any('調査隊切符' in x for x in said(pg)), '0枚で「第2戦へ」：切符 なしで 進む（0枚の まま）')
        battle(pg, LOSE, 'k')
        rb = pg.locator('#cbOv .cbmod [data-cb=qretry]')
        check(rb.is_disabled() and '切符が たまるまで あと 30:00' in rb.inner_text() and '調査隊切符 のこり 0枚' in mod_text(pg), f'0枚で 負け：「もう 一度 挑戦」は 押せない・「切符が たまるまで あと 30:00」 {rb.inner_text()!r}')
        shot(pg, 'tk07_lose0')
        pg.evaluate("() => { document.querySelector('#cbOv .cbmod [data-cb=qretry]').disabled = false; }"); said(pg); rb.click(); pg.wait_for_timeout(150)
        check(TK()['n'] == 0 and q(pg)['run']['won'] == 1 and rb.is_disabled() and '調査 失敗…' in mod_text(pg) and any('切符が たまるまで あと 30:00' in x for x in said(pg)), '（もし 押せても）0枚 なら やり直さない（結果の 窓の まま）・「切符が たまるまで あと 30:00」')
        TM('2026-11-18T12:59:59')
        check(rb.is_disabled() and 'あと 0:01' in rb.inner_text(), '29分59秒 あと：まだ 押せない（あと 0:01）')
        TM('2026-11-18T13:00:00')
        check(rb.is_enabled() and rb.inner_text().strip() == 'もう 一度 挑戦' and '調査隊切符 のこり 1枚' in mod_text(pg), f'30分 たって 1枚 → 押せる（「あと」は 消える・のこり 1枚）{rb.inner_text()!r}')
        use(pg, WIN, fill=False); said(pg); rb.click()
        pg.wait_for_function("() => CBApp._t.view && CBApp._t.view.phase !== 'end'", timeout=20000); idle(pg)
        t1 = TK()
        check(t1['n'] == 0 and t1['at'] == MSOF('2026-11-18T13:00:00') and hp(pg)['w'] > 99 and any('のこり 0枚' in x for x in said(pg)), f'「もう 一度 挑戦」で 1枚（0枚）・HP 満タン {t1}')
        battle(pg, WIN, '7')
        pg.locator('#cbOv .cbmod [data-cb=qmapgo]').click(); pg.wait_for_timeout(400)
        g = tkg(pg)
        check(scr(pg) == 'qmap' and g['n'] == '0' and abs(g['hide'] - 100) < 0.01 and g['rc'] == '次の 1枚 まで 30:00', f'マップ：ゲージ「0」・こまは ぜんぶ 空き・「次の 1枚 まで 30:00」 {[g["n"], g["hide"], g["rc"]]}')
        shot(pg, 'tk08_map0')
        pg.locator('#cbOv .qnd[data-lv="4"]').click(); pg.wait_for_timeout(250)
        o = pop(pg); gb = pg.locator('#cbOv .qpo [data-cb=qgo]')
        check(o and '（今 0枚）' in o['t'] and o['inside'] and gb.is_disabled() and '切符が たまるまで あと 30:00' in gb.inner_text(), f'0枚：ふきだしの「決戦調査に 行く」は 押せない（切符が たまるまで あと 30:00）{o and o["t"]!r}')
        shot(pg, 'tk08b_pop0')
        pg.evaluate("() => { document.querySelector('#cbOv .qpo [data-cb=qgo]').disabled = false; }"); gb.click(); pg.wait_for_timeout(250)
        t = mod_text(pg)
        check(scr(pg) == 'qmap' and '切符が 足りないよ…' in t and '調査隊切符 0／15枚' in t and '次の 1枚 まで あと 30:00' in t, f'（もし 押せても）0枚 なら 行けない：切符の 窓「切符が 足りないよ…」 {t!r}')
        if HAVE: check(pg.evaluate("() => { const i = document.querySelector('#cbOv .cbmod.cbqtk .tk'); return !!i && i.complete && i.naturalWidth > 0; }"), '切符の 窓に 切符の 絵（cb_q_tk.webp）')
        shot(pg, 'tk09_lack')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(150)
        if pg.locator('#cbOv .qpo [data-cb=qpx]').count(): pg.locator('#cbOv .qpo [data-cb=qpx]').click(); pg.wait_for_timeout(80)
        pg.locator('#cbOv .qtg').click(); pg.wait_for_timeout(200)
        t = mod_text(pg)
        check('切符が 足りないよ' not in t and '調査隊切符 0／15枚' in t and '挑戦する とき 1枚' in t and '連勝中は 使わない' in t and '30分で 1枚' in t and '15枚 まで' in t and '次の 1枚 まで あと 30:00' in t, f'ゲージを タップ → 切符の 窓（枚数・挑戦する とき 1枚・連勝中は 使わない・30分で 1枚・15枚 まで・次の 1枚 まで）{t!r}')
        TM('2026-11-18T13:29:30')
        check('次の 1枚 まで あと 0:30' in mod_text(pg), '窓を 開いた まま 時間が たつと 書きかわる（あと 0:30）')
        shot(pg, 'tk10_modal')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(150)
        TM('2026-11-18T14:30:00'); g = tkg(pg); t1 = TK()
        check(g['n'] == '3' and abs(g['hide'] - (100 - CUT[3])) < 0.01 and g['rc'] == '次の 1枚 まで 30:00' and t1['at'] == MSOF('2026-11-18T14:30:00'), f'90分 たつと 3枚（こま 3こ 金）・次の 1枚 まで 30:00 {[g["n"], g["hide"], g["rc"]]}')
        shot(pg, 'tk11_map3')
        TM('2026-11-18T21:00:00'); g = tkg(pg); t1 = TK()
        check(g['n'] == '15' and g['rc'] == '' and t1['n'] == 15 and t1['left'] == 0, '長く たっても 15枚 まで（満タン）')
        pg.locator('#cbOv .qtg').click(); pg.wait_for_timeout(200)
        check('満タン！（15枚）' in mod_text(pg) and '調査隊切符 15／15枚' in mod_text(pg), '満タンの ときの 窓：「満タン！（15枚）」')
        pg.locator('#cbOv .cbmod [data-cb=modx]').click(); pg.wait_for_timeout(150)
        pg.evaluate("t => { const T = CBApp._t; T.state.qt = { n: 7, at: t }; T.save(); T.load(); }", MSOF('2026-11-18T21:00:00'))
        check(st(pg)['qt'] == {'n': 7, 'at': MSOF('2026-11-18T21:00:00')}, '枚数と 時刻は おぼえる（読み直しても 7枚）')
        pg.evaluate("() => { const s = JSON.parse(localStorage.getItem('tengel.cb')); s.qt = { n: 99.7, at: 5 }; localStorage.setItem('tengel.cb', JSON.stringify(s)); CBApp._t.load(); }")
        check(st(pg)['qt'] == {'n': 15, 'at': 5}, 'おかしな 枚数は なおす（99.7 → 15）')
        q0 = pg.evaluate("() => { const s = JSON.parse(localStorage.getItem('tengel.cb')); s.qt = { n: 'x', at: 1 }; localStorage.setItem('tengel.cb', JSON.stringify(s)); CBApp._t.load(); return CBApp._t.state.qt; }")      # 読み直した すぐ あと（1秒 ごとの 書き直しより 前）
        check(q0 is None and TK()['n'] == 15, f'読めない 記録は すてる → 15枚から {q0}')
        pg.evaluate("t => { const T = CBApp._t; T.state.qt = { n: 5, at: t }; T.save(); }", MSOF('2026-11-18T22:00:00'))
        t1 = TK()
        check(t1['n'] == 5 and t1['at'] == MSOF('2026-11-18T21:00:00') and t1['left'] == 1800000, f'時刻が もどって いたら（ふつうは ない：時計の 番人）その 時から 数え直す・枚数は そのまま {t1}')
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
        g = tkg(pg)
        check(abs(g['g'][2] - g['m'][2]) <= 1 and 4 <= g['m'][1] - g['g'][1] - g['g'][3] <= 8 and g['g'][1] >= g['mst'] - 1 and g['n'] == '15', f'SE：調査隊切符の ゲージも マップの すぐ 上（幅 {g["g"][2]:.0f}px・あいだ {g["m"][1] - g["g"][1] - g["g"][3]:.1f}px）')
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
        pg.locator('#cbOv .cbmod [data-cb=qmapgo]').click(); pg.wait_for_timeout(300)
        pg.evaluate("() => { CBApp._t.state.q.clr = 11; CBApp._t.save(); }"); pg.locator('#cbOv [data-cb=qx]').click(); pg.wait_for_timeout(100)
        pg.locator('#cbOv .cbmenu [data-cb=quest]').click(); pg.wait_for_timeout(200)
        pg.locator('#cbOv .qnd[data-lv="12"]').click(); pg.wait_for_timeout(120); pg.locator('#cbOv .qpo [data-cb=qgo]').click()
        for i in range(3):
            pg.wait_for_function(f"() => CBApp._t.quest.scene.i === {i} && !CBApp._t.quest.scene.typing", timeout=10000)
            if i < 2: pg.locator('#cbOv .qfw').click()
        pg.wait_for_function("() => CBApp._t.quest.scene.rv === 2", timeout=10000); pg.wait_for_timeout(950)
        L = pg.evaluate("""() => { const b = document.querySelector('#cbOv .qsay').getBoundingClientRect(), e = document.querySelector('#cbOv .qfld .qe').getBoundingClientRect(), t = document.querySelector('#cbOv .qtel .bd').getBoundingClientRect();
          return [b.top, b.bottom, e.top + e.height / 1.42, e.height, e.top, t.bottom, innerHeight]; }""")
        check(L[1] <= L[6] and (L[2] - L[0]) / L[3] <= 0.14 and L[4] >= L[5] - 2, f'SE：いちばん 長い セリフ（Lv12 の 3行目・{len(SAY[11][0][2])}字）でも 窓は 画面の 中・敵に かかるのは 足もと だけ（敵の 高さの {max(0, L[2] - L[0]) / L[3] * 100:.0f}%）・テロップと 敵は 重ならない')
        shot(pg, 'se5_lv12_reveal')
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
        pg.locator('#cbOv .qtt').click(); pg.locator('#cbOv [data-cb=tstq][data-t=qt0]').click(); pg.wait_for_timeout(150)
        check(st(pg)['qt']['n'] == 0 and tkg(pg)['n'] == '0', '🧪「調査隊切符を 0枚に」（ゲージも 0）')
        pg.locator('#cbOv .qtt').click(); pg.locator('#cbOv [data-cb=tstq][data-t=qtf]').click(); pg.wait_for_timeout(150)
        check(st(pg)['qt']['n'] == 15 and tkg(pg)['n'] == '15', '🧪「調査隊切符を 15枚に」（ゲージも 15）')
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
