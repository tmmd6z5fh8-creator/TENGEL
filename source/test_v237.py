# 第4.237版の テスト（まさちゃん 2026/11/28 12:33「牧場の名前やっぱり打てないよ！」：iPad の テスト版の 写真 ＝ 第4.235版の iOS の 窓の 欄に カーソルは あるのに キーボードが 出て いない）
#   わけ：iPadOS 27 の Swift Playgrounds で 動かした アプリは、文字の 欄を 押しても キーボードが 出ない（Apple の 不具合・Apple の 見本の アプリでも 同じ）
#   ① かなキーボード（kanapad.js）は App Store版の 画面だけに 入る（Web版には 入らない）・iOS の 窓（"prompt"）は やめた（TengelWebView.swift は 第4.234版と 同じ バイト）
#   ② 文字の 欄（data-kana）に 入って 0.65秒 キーボードが 出なければ 出る（0.3秒では まだ）・字は ぜんぶ 選んだ 所に 上書き・゛ ゜ 小（もう 1回で もどる・ぱ↔ば）・英字の 大／小
#      ・◀ ▶・⌫（絵文字は 1字ずつ）・クリア・入らない（48字を こえる）ときは ゆれる・完了で しまう・欄の フォーカスは 外れない
#   ③ キーボードが 出た（アプリの 知らせ）→ しまう・出て いる 間は 出さない・しまったら また 出る・ハードの キーボードで 打った → しまう（知らせが ない ときは その あとも 出さない）
#   ④ 4つの 表（あ・ア・A・漢）・67の ます・画面の 下に つく・幅 320〜430 で はみ出さない
#   ⑤ 牧場の 看板：押すと 画面の 中の 窓（iOS の 窓は たのまない）→ かなキーボードが 出る → 窓は 上へ（重ならない）→ 打って「決める」→ 看板と 保存
#      12文字を こえると「決める」を 押せない・やめる で しまう（iPhone 390×844・iPhone SE 375×667・iPad の Swift Playgrounds の 画面の 大きさ 375×812）
#   ⑥ GitHub の Mac の たしかめ（selftest.js の kanaPad・run.sh の P1 の 合図 kana-pad・KANAPY の 行）
#   ⑦ 写真：t4/v237_kana_*.png
#   python3 test_v237.py
import json, os, re, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
sys.path.insert(0, W)
SHOT = os.path.join(W, 't4'); os.makedirs(SHOT, exist_ok=True)
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c:
        fails.append(label)


# ---- ① 入る 所・iOS の 窓は やめた
SRV = os.path.join(W, 'srv_v237'); PORT = 8864; APP = f'http://localhost:{PORT}/APP/'
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
env0 = {k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict(env0, HIST='hist_280.json', DROP='', TARGET='app'))
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'WEB')], check=True, stdout=subprocess.DEVNULL, env=dict(env0, HIST='hist_280.json', DROP='', TARGET='web'))
pth = os.path.join(SRV, 'APP', 'index.html'); page = open(pth, encoding='utf8').read()
web = open(os.path.join(SRV, 'WEB', 'index.html'), encoding='utf8').read()
kp = open('kanapad.js', encoding='utf8').read()
KP = ("const SEL = 'input[data-kana],textarea[data-kana]';", "st.id = 'kanaPadCss';", "pad.id = 'kanaPad';", 'function modify(map, kind) {')
check(all(page.count(x) == 1 for x in KP) and page.count('window.TengelKana = {') == 1 and 'TengelKana' not in web and 'kanaPad' not in web and page.index('window.TengelNumpad') < page.index('window.TengelKana'),
      '① かなキーボード（kanapad.js）は App Store版の 画面だけ（テンキーの すぐ あと）・Web版には 入らない')
tc = open(os.path.join('tc', 'tc_app.js'), encoding='utf8').read()
nocom = re.sub(r'(?m)^\s*//.*$', '', tc)
check("TengelNative.call('prompt'" not in nocom and 'farmAsk' not in nocom and 'nmAsk' not in nocom and re.search(r'function nameOpen\(\) \{\n    if \(!ov\) return;\n    nameDialog\(\);\n  \}', tc)
      and 'type="text" data-kana="1"' in tc and 'html.kanapadon #tcnmd{padding-top:calc(env(safe-area-inset-top) + 12px)}' in tc,
      '① トレーニングセンター：看板を 押すと 画面の 中の 窓（iOS の 窓は たのまない）・名前の 欄に data-kana・かなキーボードが 出て いる 間は 窓を 上へ')
sw = open(os.path.join('ios', 'Tengel.swiftpm', 'TengelWebView.swift'), 'rb').read()
old = subprocess.run(['git', 'show', '838970df:./ios/Tengel.swiftpm/TengelWebView.swift'], capture_output=True, check=True).stdout
check(sw == old and b'prompt' not in sw and b'UIAlertController' not in sw and b'self?.event("keyboard", ["open": open' in sw,
      f'① アプリ（TengelWebView.swift）は 第4.234版と 同じ バイト（{len(sw):,} B：iOS の 窓 "prompt" は ない）・キーボードの 知らせ（keyboardWillShow／Hide）は そのまま')
bad = [w for w in ('まさちゃん', 'Claude', 'Anthropic', '大井', 'JRA', 'NAR', 'WIN5') if w in kp]
check(not bad, f'① kanapad.js に 出しては いけない 字 なし（{bad or "なし"}）')

assert "window.__NATIVE = location.protocol === 'tengel:';" in page
open(pth, 'w', encoding='utf8').write(page.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
BL = os.environ.get('KISEKAE_ASSETS') or os.path.join(W, 'ios', 'kisekae_blobs')
if os.path.isdir(BL):
    for f in os.listdir(BL):
        shutil.copy(os.path.join(BL, f), os.path.join(SRV, 'APP', 'ks_' + f))
from assets_dir import adir
TCA = adir('tc_assets'); HAVE_TC = os.path.isdir(TCA) and len(os.listdir(TCA)) > 100 and os.path.exists(os.path.join(TCA, 'tc_sign.webp'))
if HAVE_TC:
    for f in os.listdir(TCA): shutil.copy(os.path.join(TCA, f), os.path.join(SRV, 'APP', f))
NT = open(os.path.join(W, 'test_native.py'), encoding='utf8').read()
FAKE = re.search(r'\nFAKE = """(.*?)"""', NT, re.S).group(1)      # アプリの 窓口の にせもの（たのみごとは window.__bridge に のこる）
GATE_GONE = "() => { const g = document.querySelector('#gate'); return !g || g.hidden || getComputedStyle(g).display === 'none'; }"
TC_OPEN = "() => window.TCApp && document.querySelector('#tcOv.on') && !document.querySelector('#tcOv .tcld')"
FIELD = """() => { let f = document.querySelector('#kpT'); if (f) f.remove();
  f = document.createElement('input'); f.id = 'kpT'; f.type = 'text'; f.setAttribute('data-kana', '1'); f.setAttribute('aria-label', '牧場の名前'); f.maxLength = 48; f.value = 'テンゲル牧場';
  f.style.cssText = 'position:fixed;left:16px;right:16px;top:96px;z-index:96;height:48px;font-size:20px'; document.body.appendChild(f); return true; }"""
ST = """() => { const f = document.querySelector('#kpT'), p = document.querySelector('#kanaPad'), s = TengelKana.state();
  return { open: s.open, mode: s.mode, target: s.target, hw: s.hw, kb: s.kb, v: f ? f.value : null, ss: f ? f.selectionStart : null, se: f ? f.selectionEnd : null,
    active: !!f && document.activeElement === f, head: p ? p.querySelector('.kpt').textContent : '', lab: p ? p.querySelector('.kpf').textContent : '', on: document.documentElement.classList.contains('kanapadon') }; }"""


def boot(pg):
    pg.goto(APP); pg.wait_for_timeout(1500)
    if pg.locator('#gateGo').count(): pg.click('#gateGo'); pg.wait_for_timeout(700)
    pg.wait_for_function(GATE_GONE, timeout=10000); pg.wait_for_timeout(400)


def K(pg, *keys):
    for k in keys:
        pg.locator(f'#kanaPad button[data-k="{k}"]').click()
    return pg.evaluate(ST)


errs = []
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
try:
    with sync_playwright() as p:
        br = p.chromium.launch()
        ctx = br.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo')
        ctx.add_init_script(FAKE)
        pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        boot(pg)
        # ---- ② 出る まで・打つ
        pg.evaluate(FIELD); pg.evaluate("() => { const f = document.querySelector('#kpT'); f.focus(); f.select(); }")
        pg.wait_for_timeout(300); s0 = pg.evaluate(ST)
        pg.wait_for_timeout(600); s1 = pg.evaluate(ST)
        check(not s0['open'] and s1['open'] and s1['active'] and s1['mode'] == 'h' and s1['target'] == 'kpT' and s1['lab'] == '牧場の名前' and s1['on']
              and s1['head'] == 'かなキーボード（キーボードが 出ない ときに）' and s1['ss'] == 0 and s1['se'] == 6,
              f'② 欄に 入って 0.3秒では まだ・0.9秒で 出る（0.65秒）・上の 字「{s1["head"]}」・欄の 名前「{s1["lab"]}」・はじめは ひらがな・欄は ぜんぶ 選んだ まま')
        a = K(pg, 'm:k', 'c:ヘ', 'f:hd', 'c:カ', 'f:dk', 'c:サ', 'c:ス', 'm:j', 'c:牧', 'c:場')
        b = K(pg, 'f:left', 'f:left', 'm:h', 'c:の')
        check(a['v'] == 'ペガサス牧場' and a['active'] and b['v'] == 'ペガサスの牧場' and b['ss'] == b['se'] == 5 and b['active'] and b['open'],
              f'② ア ヘ゜カ゛サス 漢 牧場 →「{a["v"]}」（ぜんぶ 選んだ 所に 上書き）・◀◀ あ の →「{b["v"]}」・押しても 欄の フォーカスは 外れない')
        pg.evaluate("() => { const f = document.querySelector('#kpT'); f.setSelectionRange(f.value.length, f.value.length); }")
        c1 = K(pg, 'c:か', 'f:dk'); c2 = K(pg, 'f:dk'); c3 = K(pg, 'f:bs', 'c:は', 'f:hd'); c4 = K(pg, 'f:dk'); c5 = K(pg, 'f:hd'); c6 = K(pg, 'f:hd')
        c7 = K(pg, 'f:bs', 'c:つ', 'f:sm'); c8 = K(pg, 'f:sm'); c9 = K(pg, 'f:bs', 'm:a', 'c:Q', 'f:sm'); c10 = K(pg, 'f:sm')
        ng = pg.evaluate("() => { const f = document.querySelector('#kpT'), v = f.value; f.setSelectionRange(0, 0); return v; }")
        c11 = K(pg, 'f:dk')
        shake = pg.evaluate("() => document.querySelector('#kanaPad button[data-k=\"f:dk\"]').classList.contains('ng')")
        tail = lambda q: q['v'][-1]
        check([tail(x) for x in (c1, c2, c3, c4, c5, c6, c7, c8, c9, c10)] == ['が', 'か', 'ぱ', 'ば', 'ぱ', 'は', 'っ', 'つ', 'q', 'Q'] and c11['v'] == ng and shake,
              '② ゛ ゜ 小 は 前の 字に：か→が→か・は→ぱ→（゛）ば→（゜）ぱ→は・つ→っ→つ・英字 Q→q→Q（小）・前に 字が ない ときは 入らず ゆれる')
        pg.evaluate("() => { const f = document.querySelector('#kpT'); f.value = 'う🐴ま'; f.setSelectionRange(3, 3); }")
        e1 = K(pg, 'f:left'); e2 = K(pg, 'f:right'); e3 = K(pg, 'f:bs')
        pg.evaluate("() => { const f = document.querySelector('#kpT'); f.value = 'あ'.repeat(47); f.setSelectionRange(47, 47); }")
        e4 = K(pg, 'm:h', 'c:い'); e5 = K(pg, 'c:う')
        shake2 = pg.evaluate("() => document.querySelector('#kanaPad button[data-k=\"c:う\"]').classList.contains('ng')")
        e6 = K(pg, 'f:clr'); e7 = K(pg, 'c: ')
        check(e1['ss'] == 1 and e2['ss'] == 3 and e3['v'] == 'うま' and e3['ss'] == 1 and len(e4['v']) == 48 and e5['v'] == e4['v'] and shake2 and e6['v'] == '' and e7['v'] == ' ',
              '② ◀ ▶ と ⌫ は 絵文字を 1字と して（う🐴ま：3 → 1 → 3・⌫ で 🐴 を 消して「うま」）・48字を こえる 字は 入らず ゆれる・クリアで 空・空白')
        d = K(pg, 'f:done'); pg.wait_for_timeout(120); d = pg.evaluate(ST)
        check(not d['open'] and not d['active'] and not d['on'], '② 完了 → しまう・欄から 出る')
        # ---- ④ 4つの 表・形
        pg.evaluate("() => { const f = document.querySelector('#kpT'); f.value = ''; f.focus(); }"); pg.wait_for_timeout(900)
        tb = {}
        for m in ('h', 'k', 'a', 'j'):
            pg.locator(f'#kanaPad button[data-k="m:{m}"]').click()
            tb[m] = pg.evaluate("""() => ({ cells: document.querySelectorAll('#kanaPad .kpg > *').length, chars: [...document.querySelectorAll('#kanaPad button[data-k^="c:"]')].map(b => b.dataset.k.slice(2)).join(''),
              on: [...document.querySelectorAll('#kanaPad button.fn.on')].map(b => b.dataset.k), head: document.querySelector('#kanaPad .kpt').textContent,
              sm: document.querySelector('#kanaPad button[data-k="f:sm"]').getAttribute('aria-label') })""")
        base = 'ー・！？ '
        check(all(tb[m]['cells'] == 67 for m in tb) and tb['h']['chars'] == 'あかさたなはまやらわいきしちにひみりうくすつぬふむゆるをえけせてねへめれおこそとのほもよろん' + base
              and tb['k']['chars'] == 'アカサタナハマヤラワイキシチニヒミリウクスツヌフムユルヲエケセテネヘメレオコソトノホモヨロン' + base
              and tb['a']['chars'] == "ABCDEFGHIJKLMNOPQRSTUVWXYZ&.-'1234567890()#@★☆♡♪+_" + base
              and tb['j']['chars'] == '牧場馬駒厩舎第号大地新天空星月日光夢王神金銀白黒赤青緑紅桜花山川海森風雷北南東西田野原島竜虎鷹幸福勝' + base
              and [tb[m]['on'] for m in ('h', 'k', 'a', 'j')] == [['m:h'], ['m:k'], ['m:a'], ['m:j']] and tb['a']['head'] == '英数（小 で 小文字・大文字）' and tb['j']['head'] == 'よく 使う 漢字'
              and tb['a']['sm'] == '大文字と 小文字' and tb['h']['sm'] == '小さい 字',
              '④ 4つの 表（あ 46字・ア 46字・A 50字・漢 50字）＋ ー ・ ！ ？ 空白・どれも 67の ます（空きの ますを ふくむ）・えらんだ 表は 金色')
        lay = {}
        for wv, hv in ((390, 844), (320, 568), (430, 932)):
            pg.set_viewport_size({'width': wv, 'height': hv}); pg.wait_for_timeout(250)
            lay[wv] = pg.evaluate("""() => { const p = document.querySelector('#kanaPad').getBoundingClientRect(), bs = [...document.querySelectorAll('#kanaPad button')].map(b => b.getBoundingClientRect());
              return { top: Math.round(p.top), h: Math.round(p.height), bottom: Math.round(innerHeight - p.bottom), w: Math.round(p.width), minW: Math.round(Math.min(...bs.map(r => r.width))),
                minH: Math.round(Math.min(...bs.map(r => r.height))), out: bs.filter(r => r.left < 0 || r.right > innerWidth + 0.5).length, sw: document.documentElement.scrollWidth <= innerWidth }; }""")
        pg.set_viewport_size({'width': 390, 'height': 844}); pg.wait_for_timeout(200)
        pg.locator('#kanaPad button[data-k="m:h"]').click()
        pg.screenshot(path=os.path.join(SHOT, 'v237_kana_pad.png'), clip=dict(x=0, y=844 - lay[390]['h'] - 2, width=390, height=lay[390]['h'] + 2))
        check(all(l['bottom'] == 0 and l['out'] == 0 and l['sw'] and l['minH'] >= 40 and l['minW'] >= 24 for l in lay.values()) and 280 <= lay[390]['h'] <= 340,
              f'④ 画面の 下に つく・幅 320／390／430 で はみ出さない（キーの 幅 いちばん 小さい {lay[320]["minW"]}／{lay[390]["minW"]}／{lay[430]["minW"]}px・高さ 40px）・高さ {lay[390]["h"]}px')
        # ---- ③ キーボードの 知らせ・ハードの キーボード
        pg.evaluate("() => window.__nativeEvent('keyboard', { open: true, height: 320 })"); pg.wait_for_timeout(100); k1 = pg.evaluate(ST)
        pg.evaluate("() => { document.activeElement.blur(); document.querySelector('#kpT').focus(); }"); pg.wait_for_timeout(900); k2 = pg.evaluate(ST)
        pg.evaluate("() => window.__nativeEvent('keyboard', { open: false, height: 0 })")
        pg.evaluate("() => { document.activeElement.blur(); document.querySelector('#kpT').focus(); }"); pg.wait_for_timeout(900); k3 = pg.evaluate(ST)
        check(not k1['open'] and not k2['open'] and k2['kb'] is True and k3['open'] and k3['kb'] is False,
              '③ アプリの 知らせ「キーボードが 出た」→ しまう・出て いる 間は 出さない・「しまった」の あとは また 出る')
        pg.evaluate("() => TengelKana._reset()")
        pg.keyboard.type('x'); pg.wait_for_timeout(100); h1 = pg.evaluate(ST)
        pg.evaluate("() => { document.activeElement.blur(); document.querySelector('#kpT').focus(); }"); pg.wait_for_timeout(900); h2 = pg.evaluate(ST)
        pg.evaluate("() => { TengelKana._reset(); document.activeElement.blur(); document.querySelector('#kpT').focus(); }"); pg.wait_for_timeout(900); h3 = pg.evaluate(ST)
        check(not h1['open'] and h1['hw'] and h1['v'].endswith('x') and not h2['open'] and h3['open'],
              '③ ハードの キーボードで 打った → しまう・知らせが ない ときは その あとも 出さない（_reset で また 出る）')
        z0 = pg.evaluate("() => TengelKana.state().open")
        pg.evaluate("() => { document.activeElement.blur(); }"); pg.wait_for_timeout(150)
        check(z0 and not pg.evaluate("() => TengelKana.state().open"), '③ 欄から 出たら しまう')
        check(not errs, f'②〜④ エラー なし {errs[:2]}')
        ctx.close(); br.close()
        # ---- ⑤ 牧場の 看板
        if not HAVE_TC:
            print('※ トレーニングセンターの 絵（ios/tc_assets・tc_sign.webp）が ない ので、看板の 確かめは しない')
        else:
            b2 = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'])
            for (vw, vh, tag) in ((390, 844, 'iphone'), (375, 667, 'se'), (375, 812, 'ipad')):
                c2 = b2.new_context(viewport={'width': vw, 'height': vh}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo', has_touch=True)
                c2.add_init_script(FAKE)
                pg = c2.new_page(); e2 = []; pg.on('pageerror', lambda e: e2.append(str(e)))
                boot(pg)
                pg.locator('#tcFab').click(); pg.wait_for_function(TC_OPEN, timeout=90000); pg.wait_for_timeout(1500)
                pg.evaluate("() => { window.__bridge.length = 0; }")
                pg.locator('#tcOv .tcnm').click(); pg.wait_for_timeout(250)
                g0 = pg.evaluate("""() => { const d = document.querySelector('#tcnmd'), i = d && d.querySelector('.nin');
                  return { on: !!d && d.classList.contains('on'), active: document.activeElement === i, sel: i ? [i.selectionStart, i.selectionEnd] : null, kana: i ? i.dataset.kana : null,
                    prompt: window.__bridge.filter(m => m.name === 'prompt').length, pad: TengelKana.state().open }; }""")
                pg.wait_for_timeout(700)
                LAY = """() => { const s = document.querySelector('#tcnmd .nsh').getBoundingClientRect(), p = document.querySelector('#kanaPad').getBoundingClientRect(), ok = document.querySelector('#tcnmd [data-nm=ok]').getBoundingClientRect();
                  const hit = document.elementFromPoint(ok.left + ok.width / 2, ok.top + ok.height / 2);
                  return { pad: TengelKana.state().open, top: Math.round(s.top), bottom: Math.round(s.bottom), padTop: Math.round(p.top), okHit: !!hit && !!hit.closest('[data-nm=ok]'),
                    cnt: document.querySelector('#tcnmd .ncnt').textContent, okDis: document.querySelector('#tcnmd [data-nm=ok]').disabled, v: document.querySelector('#tcnmd .nin').value }; }"""
                g1 = pg.evaluate(LAY)
                for k in ('m:k', 'c:ヘ', 'f:hd', 'c:カ', 'f:dk', 'c:サ', 'c:ス', 'm:j', 'c:牧', 'c:場'):
                    pg.locator(f'#kanaPad button[data-k="{k}"]').tap()
                g2 = pg.evaluate(LAY)
                if tag == 'iphone':
                    pg.screenshot(path=os.path.join(SHOT, 'v237_kana_farm.png'))
                    pg.locator('#kanaPad button[data-k="m:h"]').tap(); pg.wait_for_timeout(100)
                pg.screenshot(path=os.path.join(SHOT, f'v237_kana_{tag}.png'))
                check(g0['on'] and g0['active'] and g0['sel'] == [0, 6] and g0['kana'] == '1' and g0['prompt'] == 0 and not g0['pad'] and g1['pad'] and g1['bottom'] < g1['padTop'] and g1['okHit']
                      and g2['v'] == 'ペガサス牧場' and g2['cnt'] == '6/12文字' and not g2['okDis'] and g2['okHit'],
                      f'⑤ {vw}×{vh}：看板を 押すと 画面の 中の 窓（iOS の 窓は たのまない：{g0["prompt"]}回）・名前は ぜんぶ 選んだ まま → 0.95秒で かなキーボード・'
                      f'窓は 上へ（{g1["top"]}〜{g1["bottom"]}px・キーボードは {g1["padTop"]}px から：重ならない・「決める」が 押せる）・指で 打って「{g2["v"]}」（{g2["cnt"]}）')
                if tag == 'iphone':
                    pg.locator('#tcnmd [data-nm=ok]').tap(); pg.wait_for_timeout(350)
                    q = pg.evaluate("""() => ({ txt: document.querySelector('#tcOv .tcnmi').textContent, saved: (JSON.parse(localStorage.getItem('tengel.tc') || '{}') || {}).farm,
                      dlg: document.querySelector('#tcnmd').classList.contains('on'), pad: TengelKana.state().open, on: document.documentElement.classList.contains('kanapadon'), msg: document.querySelector('#tcOv .tcmsg').textContent })""")
                    check(q['txt'] == 'ペガサス牧場' and q['saved'] == 'ペガサス牧場' and not q['dlg'] and not q['pad'] and not q['on'] and '看板の 名前を「ペガサス牧場」に したよ' in q['msg'],
                          f'⑤「決める」→ 看板「{q["txt"]}」・保存・お知らせ・窓も かなキーボードも しまう')
                    pg.locator('#tcOv .tcnm').click(); pg.wait_for_timeout(950)
                    for k in ('f:right',) + ('c:あ',) * 7: pg.locator(f'#kanaPad button[data-k="{k}"]').tap()
                    o1 = pg.evaluate(LAY)
                    pg.locator('#tcnmd .nb[data-nm=no]').tap(); pg.wait_for_timeout(250)
                    o2 = pg.evaluate("() => ({ dlg: document.querySelector('#tcnmd').classList.contains('on'), pad: TengelKana.state().open, txt: document.querySelector('#tcOv .tcnmi').textContent })")
                    check(o1['v'] == 'ペガサス牧場' + 'あ' * 7 and o1['cnt'] == '13/12文字（12文字までだよ）' and o1['okDis'] and not o2['dlg'] and not o2['pad'] and o2['txt'] == 'ペガサス牧場',
                          f'⑤ 12文字を こえると「決める」を 押せない（{o1["cnt"]}）・やめる → 窓も かなキーボードも しまう・看板は そのまま')
                if tag == 'iphone':
                    # ⑤ かなキーボードの ボタン：アプリの 知らせが「キーボードが 出た」の ままでも、押せば 出る（知らせが まちがって いる とき の 予備）・もう 1回で しまう
                    KB = """() => { const b = document.querySelector('#tcnmd .nkb'), r = b.getBoundingClientRect(), i = document.querySelector('#tcnmd .nin');
                      return { vis: !b.hidden && r.width > 0, on: b.classList.contains('on'), pad: TengelKana.state().open, forced: TengelKana.state().forced, active: document.activeElement === i, v: i.value, txt: b.textContent }; }"""
                    pg.evaluate("() => window.__nativeEvent('keyboard', { open: true, height: 300 })")
                    pg.locator('#tcOv .tcnm').click(); pg.wait_for_timeout(950); t1 = pg.evaluate(KB)
                    pg.locator('#tcnmd .nkb').tap(); pg.wait_for_timeout(150); t2 = pg.evaluate(KB)
                    pg.evaluate("() => window.__nativeEvent('keyboard', { open: true, height: 300 })"); pg.wait_for_timeout(100); t3 = pg.evaluate(KB)
                    pg.locator('#kanaPad button[data-k="f:right"]').tap(); pg.locator('#kanaPad button[data-k="c:ん"]').tap(); t4 = pg.evaluate(KB)
                    pg.locator('#tcnmd .nkb').tap(); pg.wait_for_timeout(800); t5 = pg.evaluate(KB)
                    pg.locator('#tcnmd .nb[data-nm=no]').tap(); pg.wait_for_timeout(250)
                    pg.evaluate("() => window.__nativeEvent('keyboard', { open: false, height: 0 })")
                    check(t1['vis'] and not t1['pad'] and not t1['on'] and t1['active'] and t1['txt'] == '⌨️ かなキーボード' and t2['pad'] and t2['on'] and t2['forced'] and t2['active']
                          and t3['pad'] and t4['v'] == 'ペガサス牧場ん' and t4['active'] and not t5['pad'] and not t5['on'] and t5['active'],
                          '⑤「⌨️ かなキーボード」の ボタン：アプリの 知らせが「キーボードが 出た」で 出て こない ときも 押せば 出る（知らせが 来ても しまわない）・打てる・もう 1回 押すと しまう（0.8秒 たっても 出ない）・欄の フォーカスは そのまま')
                check(not e2, f'⑤ {tag}：エラー なし {e2[:2]}')
                c2.close()
            b2.close()
finally:
    srv.terminate()
shutil.rmtree(SRV, ignore_errors=True)

# ---- ⑥ GitHub の Mac の たしかめ
st = open(os.path.join(W, 'ios', 'ci', 'selftest.js'), encoding='utf8').read(); rs = open(os.path.join(W, 'ios', 'ci', 'run.sh'), encoding='utf8').read()
P1 = re.search(r'\nP1="([^"]+)"', rs).group(1).split()
marks = set(re.findall(r"mark\('([a-z0-9-]+)'\)", st)) | {'gate-first'}
nomark = [m for m in P1 if not m.startswith('report-') and m not in marks]
check(not nomark and P1.index('cb-end') + 1 == P1.index('kana-pad') and P1.index('kana-pad') + 1 == P1.index('report-1') and 'farm-prompt' not in P1
      and "step(R, 'kanaPad'" in st and st.count("mark('kana-pad')") == 2 and "if (!marked) await mark('kana-pad');" in st and 'farmPrompt' not in st and "TengelNative.call('prompt'" not in st,
      f'⑥ GitHub の Mac：P1 の 合図の 順（cb-end → kana-pad → report-1）・どの 合図も selftest.js に ある（ない もの：{nomark or "なし"}）・kana-pad の 合図は どの 道でも 1回・iOS の 窓の たしかめは ない')
check('KANAPY=' in rs and 'kana pad: $(python3 -c "$KANAPY"' in rs and 'kana pad (ipad): $(python3 -c "$KANAPY"' in rs and 'FARMPY' not in rs,
      '⑥ run.sh：kana pad の 行（iPhone・iPad）・farm prompt の 行は ない')
pyk = re.search(r"\nKANAPY='\n(.*?)\n'\n", rs, re.S).group(1)
sample = {'kanaPad': {'api': True, 'early': False, 'shown': True, 'target': '牧場の名前', 'kb': None, 'hw': False, 'mode0': 'h', 'active': True, 'keys': 10, 'v1': 'ペガサス牧場', 'v2': 'ペガサスの牧場',
                      'box': {'top': 470, 'h': 340, 'bottom': 0, 'w': 390}, 'cells': 67, 'mode1': 'h', 'activeAfter': True, 'v3': 'ペガサスの牧場ョ', 'v4': 'ペガサスの牧場ヨ', 'v5': 'ペガサスの牧場',
                      'v6': 'ペガサスの牧場a', 'v7': '', 'closed': True, 'blurred': True}}
tmp = os.path.join(SHOT, '_kanapy.json'); json.dump(sample, open(tmp, 'w', encoding='utf8'), ensure_ascii=False)
r1 = subprocess.run(['python3', '-c', pyk, tmp], capture_output=True, text=True).stdout.strip()
sample['kanaPad']['v2'] = 'x'; json.dump(sample, open(tmp, 'w', encoding='utf8'), ensure_ascii=False)
r2 = subprocess.run(['python3', '-c', pyk, tmp], capture_output=True, text=True).stdout.strip(); os.remove(tmp)
check(r1.endswith('-> OK') and '-> CHECK' in r2, f'⑥ KANAPY：よい 結果は OK・ちがう 字は CHECK（{r1[-60:]}）')

print('合計', len(fails), 'NG' if fails else 'OK')
sys.exit(1 if fails else 0)
