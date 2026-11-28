# 第4.235版の テスト（まさちゃん 2026/11/28 08:41「競馬新聞の壁紙、数字切り替わる速度15秒から7秒に変えて！
#   あと、牧場の名前変えようとしても入力するところが出てこないから改善して！」）
#   ① 競馬新聞：数字が かわるのは 7秒ごと（news_wall.TK_S）・説明（aria-label・着せ替えの 一覧）も 7秒・CSS の 動き（7秒で 1回り・うすく なるのは 0.4秒）
#   ② アプリの 中身（ks_news.json）：kbnsTk 7s・前の 15秒は ない
#   ③ アプリの 画面で ほんとうの 時間：数字の 層の 動きは 7000ms・速めない まま 17秒 見て、かわる あいだは 7秒（±0.3秒）・馬単は 3連単の 1着→2着
#   ④ 牧場の 看板：アプリ（iOS）の 中では 押すと iOS の 窓（TengelNative.call('prompt')）を 1回 たのむ：題・説明・いまの 名前・12文字・ボタンの 字・空の ときの 字
#      → 返って きた 名前を 看板と 保存へ（画面の 中の 窓は 出さない）・お知らせ
#   ⑤ やめる・もう 出て いる（busy）・「テンゲル牧場」に もどす（いまが ちがう 名前の ときだけ ボタン）・空・見えない 字・タグの 形・13文字 より 長い（12文字に 切る）
#   ⑥ 窓が 出て いる 間に 何回 押しても たのむのは 1回・返事の あとは また たのめる
#   ⑦ アプリの 窓が 使えない（たのむ ところで エラー・返事の 形が ちがう）→ 画面の 中の 窓（前の 形）で 打てる
#   ⑧ アプリ（Swift）：TengelWebView.swift の "prompt"（UIAlertController の 1行の 欄・字の 数・こえたら「決める」を 押せない・Return＝決める・2回目は ことわる・
#      テストの 道〈SelfTest〉は DEBUG だけ・内部の 決まり〈private API〉は 使わない）・GitHub の Mac の たしかめ（selftest.js・run.sh：P1 の 合図の 順と 合う）
#   ⑨ 写真：t4/v235_tc_sign.png（名前を かえた 看板）
#   python3 test_v235.py
import json, os, re, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
K = os.path.join(W, 'kisekae'); sys.path.insert(0, K); sys.path.insert(0, W)
BL = os.environ.get('KISEKAE_ASSETS') or os.path.join(W, 'ios', 'kisekae_blobs')
SHOT = os.path.join(W, 't4'); os.makedirs(SHOT, exist_ok=True)
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c:
        fails.append(label)


import news_wall
# ---- ① 競馬新聞の 時間
TK = json.load(open(os.path.join(K, 'news_tk.json'), encoding='utf8'))
html, css = news_wall.inline(news_wall.load_blobs(os.path.join(K, 'news_blobs.json')), TK)
th = open(os.path.join(K, 'themes20.py'), encoding='utf8').read()
news_th = th[th.index("dict(id='news'"):th.index("dict(id='news'") + 4000]
check(news_wall.TK_S == 7 and news_wall.TK_FADE == 0.4 and '7秒ごと' in news_wall.ALT and '15秒' not in news_wall.ALT
      and f'aria-label="{news_wall.ALT}"' in html and 'animation:nsTk 7s linear infinite' in css
      and '@keyframes nsTk{0%{opacity:0}5.7143%{opacity:1}94.2857%{opacity:1}100%{opacity:0}}' in css and '15s' not in css,
      f'① 数字が かわるのは 7秒ごと（TK_S {news_wall.TK_S}・うすく なるのは 0.4秒）・説明「{news_wall.ALT[-14:]}」・CSS：7秒で 1回り（5.7143%〜94.2857% が こい）')
check("馬券の数字は7秒ごとにかわる" in news_th and '数字は7秒ごとに25組からランダム' in news_th and '馬券の数字は15秒' not in news_th,
      '① 着せ替えの 一覧の 説明（themes20.py の alt と 説明の 絵の 字）も 7秒')

# ---- ②〜⑦ アプリ
SRV = os.path.join(W, 'srv_v235'); PORT = 8862; APP = f'http://localhost:{PORT}/APP/'
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL,
               env=dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, HIST='hist_280.json', DROP='', TARGET='app'))
pth = os.path.join(SRV, 'APP', 'index.html'); page = open(pth, encoding='utf8').read()
assert "window.__NATIVE = location.protocol === 'tengel:';" in page
open(pth, 'w', encoding='utf8').write(page.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
if os.path.isdir(BL):
    for f in os.listdir(BL):
        shutil.copy(os.path.join(BL, f), os.path.join(SRV, 'APP', 'ks_' + f))
from assets_dir import adir
TCA = adir('tc_assets'); HAVE_TC = os.path.isdir(TCA) and len(os.listdir(TCA)) > 100 and os.path.exists(os.path.join(TCA, 'tc_sign.webp'))
if HAVE_TC:
    for f in os.listdir(TCA): shutil.copy(os.path.join(TCA, f), os.path.join(SRV, 'APP', f))
kj = json.load(open(os.path.join(SRV, 'APP', 'ks_news.json'), encoding='utf8'))
check('animation:kbnsTk 7s linear infinite' in kj['bnr']['css'] and 'kbnsTk 15s' not in kj['bnr']['css'] and '7秒ごと' in kj['bnr']['html'] and '15秒' not in json.dumps(kj, ensure_ascii=False),
      '② アプリの 中身（ks_news.json）：数字の 層の 動き kbnsTk 7s・説明も 7秒・前の 15秒は どこにも ない')
NT = open(os.path.join(W, 'test_native.py'), encoding='utf8').read()
FAKE = re.search(r'\nFAKE = """(.*?)"""', NT, re.S).group(1)      # アプリの 窓口の にせもの
# iOS の 窓（prompt）の にせもの：window.__promptAns が ある ときだけ 答える（関数・'__throw'＝たのむ ところで エラー・'__hold'＝あとで 答える）。ない ときは FAKE の まま（true）
PROMPT = """(() => { const h = window.webkit.messageHandlers.tengel, orig = h.postMessage;
  window.__prompts = []; window.__promptHold = null;
  h.postMessage = function (m) {
    if (m && m.name === 'prompt' && window.__promptAns !== undefined) {
      window.__prompts.push(JSON.parse(JSON.stringify(m.payload)));
      const a = window.__promptAns, v = typeof a === 'function' ? a(m.payload) : a;
      if (v === '__throw') throw new Error('fake: no prompt');
      if (v === '__hold') { window.__promptHold = val => window.__nativeReply(m.id, true, val); return; }
      setTimeout(() => window.__nativeReply(m.id, true, v), 30); return;
    }
    return orig.call(this, m);
  }; })();"""
GATE_GONE = "() => { const g = document.querySelector('#gate'); return !g || g.hidden || getComputedStyle(g).display === 'none'; }"
TC_OPEN = "() => window.TCApp && document.querySelector('#tcOv.on') && !document.querySelector('#tcOv .tcld')"
SIGN = """() => { const n = document.querySelector('#tcOv .tcnm'), i = n.querySelector('.tcnmi'), o = n.querySelector('.tcnmt'), d = document.querySelector('#tcnmd'), m = document.querySelector('#tcOv .tcmsg');
  return { txt: i.textContent, kids: i.children.length, need: i.scrollWidth, room: o.clientWidth, label: n.getAttribute('aria-label'), name: TCApp.farm.name(), asking: TCApp.farm.asking,
    saved: (JSON.parse(localStorage.getItem('tengel.tc') || '{}') || {}).farm, dlg: !!(d && d.classList.contains('on')), msg: m ? m.textContent : '', msgOn: !!(m && m.classList.contains('on')),
    n: window.__prompts.length, last: window.__prompts[window.__prompts.length - 1] || null }; }"""


def boot(pg):
    pg.goto(APP); pg.wait_for_timeout(1500)
    if pg.locator('#gateGo').count(): pg.click('#gateGo'); pg.wait_for_timeout(700)
    pg.wait_for_function(GATE_GONE, timeout=10000); pg.wait_for_timeout(400)


def ask(pg, ans, wait=350):
    pg.evaluate("(a) => { window.__promptAns = a; }", ans)
    pg.locator('#tcOv .tcnm').click(); pg.wait_for_timeout(wait)
    return pg.evaluate(SIGN)


errs, bad = [], []
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
try:
    with sync_playwright() as p:
        # ---- ③ ほんとうの 時間（速めない）
        br = p.chromium.launch()
        ctx = br.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo')
        pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        boot(pg)
        pg.evaluate("(id) => TengelKisekae.apply(id, false)", 'news')
        pg.wait_for_function("() => TengelKisekae.current() === 'news' && TengelKisekae.loaded() && !!document.querySelector('#ksBnr .nsq')", timeout=8000)
        pg.evaluate("window.scrollTo(0, 0)")
        an = pg.evaluate("() => document.querySelector('#ksBnr .nsq').getAnimations().map(a => [a.animationName, a.playState, a.effect.getComputedTiming().duration])")
        w = pg.evaluate("""(ms) => new Promise(res => { const q = document.querySelector('#ksBnr .nsq'), ch = [], bad = []; let last = q.dataset.tkn; const t0 = performance.now();
          const tick = () => { const k = q.dataset.tkn; if (k !== last) { last = k; ch.push(performance.now()); const v = [...q.querySelectorAll('[data-tki]')].map(e => e.textContent);
              if (v[0] !== v[2] || v[1] !== v[3] || v.some(x => !/^([1-9]|1[0-6])$/.test(x))) bad.push(v.join(' ')); }
            if (performance.now() - t0 < ms) requestAnimationFrame(tick); else res({ ch, bad }); }; tick(); })""", 17000)
        gaps = [round((b - a) / 1000, 2) for a, b in zip(w['ch'], w['ch'][1:])]
        check(an == [['kbnsTk', 'running', 7000]] and len(w['ch']) >= 2 and gaps and all(abs(g - 7) <= 0.3 for g in gaps) and not w['bad'],
              f'③ アプリの 画面（速めない）：数字の 層の 動き {an}・17秒で {len(w["ch"])}回 かわった・かわる あいだ {gaps}秒（7秒 ±0.3）・馬単は 3連単の 1着→2着・1〜16')
        check(not errs, f'③ エラー なし {errs[:2]}')
        ctx.close(); br.close()
        # ---- ④〜⑦ 牧場の 看板（トレーニングセンターの 絵が ある とき）
        if not HAVE_TC:
            print('※ トレーニングセンターの 絵（ios/tc_assets・tc_sign.webp）が ない ので、看板の 確かめは しない')
        else:
            b2 = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'])
            c2 = b2.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=3, locale='ja-JP', timezone_id='Asia/Tokyo', has_touch=True)
            c2.add_init_script(FAKE); c2.add_init_script(PROMPT)
            pg = c2.new_page(); e2 = []; pg.on('pageerror', lambda e: e2.append(str(e)))
            boot(pg)
            pg.locator('#tcFab').click(); pg.wait_for_function(TC_OPEN, timeout=90000); pg.wait_for_timeout(1500)
            q = ask(pg, {'ok': True, 'text': 'まさちゃん牧場'})
            want = {'title': '🪧 牧場の名前', 'message': '看板に 書く 名前を 入れてね（12文字まで）', 'text': 'テンゲル牧場', 'placeholder': 'テンゲル牧場', 'max': 12,
                    'empty': '空なら「テンゲル牧場」になるよ', 'ok': '決める', 'cancel': 'やめる', 'reset': ''}
            check(q['n'] == 1 and q['last'] == want, f'④ 看板を 押すと iOS の 窓を 1回 たのむ：題「{q["last"] and q["last"]["title"]}」・いまの 名前・12文字・ボタン「決める」「やめる」・もどす ボタンは なし（いまが はじめの 名前）')
            check(q['txt'] == 'まさちゃん牧場' and q['saved'] == 'まさちゃん牧場' and q['name'] == 'まさちゃん牧場' and not q['dlg'] and '看板の 名前を「まさちゃん牧場」に したよ' in q['msg'] and q['msgOn']
                  and '「まさちゃん牧場」' in q['label'] and q['need'] <= q['room'] and q['asking'] is False,
                  f'④ 返って きた 名前 →看板「{q["txt"]}」・保存（tengel.tc の farm）・お知らせ「{q["msg"]}」・画面の 中の 窓は 出さない')
            pg.screenshot(path=os.path.join(SHOT, 'v235_tc_sign.png'), clip=dict(x=0, y=40, width=390, height=200))
            # ⑤ やめる・busy・もどす・空・見えない 字・長い
            q1 = ask(pg, {'ok': False})
            q2 = ask(pg, {'ok': False, 'busy': True})
            check(q1['n'] == 2 and q1['last']['text'] == 'まさちゃん牧場' and q1['last']['reset'] == '「テンゲル牧場」に もどす' and q1['txt'] == 'まさちゃん牧場' and q1['saved'] == 'まさちゃん牧場'
                  and q2['n'] == 3 and q2['txt'] == 'まさちゃん牧場' and not q1['dlg'] and not q2['dlg'],
                  f'⑤ やめる・もう 出て いる（busy）→ かわらない・いまの 名前が はじめと ちがう ときは「{q1["last"]["reset"]}」の ボタンも たのむ')
            q3 = ask(pg, {'ok': True, 'reset': True})
            check(q3['txt'] == 'テンゲル牧場' and q3['saved'] == '' and '看板の 名前を「テンゲル牧場」に したよ' in q3['msg'], f'⑤「テンゲル牧場」に もどす → 看板「{q3["txt"]}」・保存は 空')
            q4 = ask(pg, {'ok': True, 'text': '‮あ\u0007い<b>う</b>\n'})
            q5 = ask(pg, {'ok': True, 'text': 'アイウエオカキクケコサシスセ'})
            q6 = ask(pg, {'ok': True, 'text': '   '})
            check(q4['txt'] == 'あい<b>う</b>' and q4['kids'] == 0 and q4['saved'] == 'あい<b>う</b>' and q5['txt'] == 'アイウエオカキクケコサシ' and q5['saved'] == 'アイウエオカキクケコサシ'
                  and q5['need'] <= q5['room'] and q6['txt'] == 'テンゲル牧場' and q6['saved'] == '',
                  f'⑤ 見えない 字は 入れない・タグの 形は 字の まま（「{q4["txt"]}」）・13文字 より 長い 名前は 12文字に 切る（「{q5["txt"]}」）・空なら「{q6["txt"]}」')
            # ⑥ 窓が 出て いる 間の 2回目
            pg.evaluate("() => { window.__promptAns = '__hold'; }")
            for _ in range(3): pg.locator('#tcOv .tcnm').click(); pg.wait_for_timeout(120)
            h1 = pg.evaluate(SIGN)
            pg.evaluate("() => window.__promptHold({ ok: true, text: '星空ファーム' })"); pg.wait_for_timeout(250)
            h2 = pg.evaluate(SIGN)
            h3 = ask(pg, {'ok': False})
            check(h1['n'] == q6['n'] + 1 and h1['asking'] is True and h2['txt'] == '星空ファーム' and h2['asking'] is False and h3['n'] == h2['n'] + 1,
                  f'⑥ 窓が 出て いる 間に 3回 押しても たのむのは 1回・返事の あと（看板「{h2["txt"]}」）は また たのめる')
            # ⑦ アプリの 窓が 使えない → 画面の 中の 窓
            f1 = ask(pg, '__throw', 450)
            dl = pg.evaluate("() => { const d = document.querySelector('#tcnmd'), i = d && d.querySelector('.nin'); return d ? { on: d.classList.contains('on'), val: i.value } : null; }")
            pg.fill('#tcnmd .nin', 'ペガサス牧場'); pg.locator('#tcnmd [data-nm=ok]').click(); pg.wait_for_timeout(300)
            f2 = pg.evaluate(SIGN)
            f3 = ask(pg, True, 450)
            dl2 = pg.evaluate("() => document.querySelector('#tcnmd').classList.contains('on')")
            pg.locator('#tcnmd .nb[data-nm=no]').click(); pg.wait_for_timeout(200)
            f4 = pg.evaluate(SIGN)
            check(bool(dl) and dl['on'] and dl['val'] == '星空ファーム' and f2['txt'] == 'ペガサス牧場' and f2['saved'] == 'ペガサス牧場' and not f2['dlg'] and dl2 and not f4['dlg'] and f4['txt'] == 'ペガサス牧場',
                  '⑦ アプリの 窓が 使えない（たのむ ところで エラー・返事の 形が ちがう）→ 画面の 中の 窓で 打てる（前の 形）')
            check(not e2, f'④〜⑦ エラー なし {e2[:2]}')
            c2.close(); b2.close()
finally:
    srv.terminate()
shutil.rmtree(SRV, ignore_errors=True)

# ---- ⑧ アプリ（Swift）と GitHub の Mac の たしかめ
sw = open(os.path.join(W, 'ios', 'Tengel.swiftpm', 'TengelWebView.swift'), encoding='utf8').read()
dbg = re.findall(r'#if DEBUG\n(.*?)#endif', sw, re.S)
nodbg = re.sub(r'#if DEBUG\n.*?#endif', '', sw, flags=re.S)
need = ('case "prompt":', 'UIAlertController(title:', 'preferredStyle: .alert', 'addTextField(configurationHandler: nil)', 'field.delegate = self', '.editingChanged',
        'unicodeScalars.count', 'promptOK?.isEnabled = n <= promptMax', 'alert.preferredAction = ok', 'func textFieldShouldReturn', 'extension WebBridge: UITextFieldDelegate',
        '"busy": true', 'field.returnKeyType = .done', 'field.clearButtonMode = .whileEditing')
miss = [x for x in need if x not in nodbg]
check(not miss and 'SelfTest' not in nodbg and 'promptAuto' not in nodbg and 'promptInfo' not in nodbg and any('func promptAuto' in d for d in dbg) and any('SelfTest.enabled' in d and '"selftest"' in d for d in dbg)
      and not re.search(r'_elementDidFocus|keyboardDisplayRequiresUserAction|_keyboard|performSelector|NSSelectorFromString', sw),
      f'⑧ アプリ（TengelWebView.swift）："prompt"＝UIAlertController の 1行の 欄・字の 数（Unicode の 字）・こえたら「決める」を 押せない・Return＝決める・2回目は ことわる・'
      f'テストの 道（SelfTest・promptAuto）は DEBUG だけ・内部の 決まり（private API）は 使わない（ない もの：{miss or "なし"}）')
st = open(os.path.join(W, 'ios', 'ci', 'selftest.js'), encoding='utf8').read(); rs = open(os.path.join(W, 'ios', 'ci', 'run.sh'), encoding='utf8').read()
P1 = re.search(r'\nP1="([^"]+)"', rs).group(1).split()
marks = set(re.findall(r"mark\('([a-z0-9-]+)'\)", st)) | {'gate-first'}
nomark = [m for m in P1 if not m.startswith('report-') and m not in marks]
check(not nomark and P1.index('ks-pack-wall') + 1 == P1.index('ks-news') and P1.index('cb-end') + 1 == P1.index('farm-prompt') and P1.index('farm-prompt') + 1 == P1.index('report-1')
      and "step(R, 'farmPrompt'" in st and "finally { if (!marked) await mark('farm-prompt'); }" in st and "else { res.newsTk = null; await mark('ks-news'); }" in st,
      f'⑧ GitHub の Mac：P1 の 合図の 順（ks-pack-wall → ks-news・cb-end → farm-prompt → report-1）・どの 合図も selftest.js に ある（ない もの：{nomark or "なし"}）・'
      'farm-prompt と ks-news の 合図は どの 道でも 1回')
check('an[0][2] == 7000' in rs and 'FARMPY=' in rs and 'farm prompt: $(python3 -c "$FARMPY"' in rs and 'farm prompt (ipad): $(python3 -c "$FARMPY"' in rs,
      '⑧ run.sh：news tickets は 7000ms・farm prompt の 行（iPhone・iPad）')

print('合計', len(fails), 'NG' if fails else 'OK')
sys.exit(1 if fails else 0)
