# 第4.229版の テスト（まさちゃん 2026/11/26 22:19・22:27）
#   ■ 判定タブの 下の 帯（#minibar：判定の 要点・「判定へ」）
#     22:27「1番下までスクロールして、更に下にスクロールするとなんか重くなる！ 判定は下には無いのに、判定へ↓が表示されてる！」
#     前は 判定（#result）が 画面に 少しでも 入って いれば「見えて いる」と 数えて いた（上に くっつく 帯 header.top の 下に かくれた 所も）。
#     締切済みの カード（短い）の とき、いちばん 下で 判定の 下の はしが 上の 帯の 下に のこり、さらに 下へ 引っぱる（はね返り）たびに 帯が 出る → もどると 消える を くり返した（字は いつも ↓）
#     ① 上の 帯の 下に かくれた 判定は「見えて いない」→ 帯は 出た まま・字は「判定へ↑」
#     ② 引っぱって（ページを 少し 上へ ずらして）もどしても 帯は 出たり 消えたり しない・同じ 値も 書かない（右の 丸い ボタンの 列が 測り直さない）
#     ③ はね返りの とちゅう（scrollY が いちばん 下より 先）は 数え直さない → 止まって から 見直す
#     ④ ページの 上（入力）では「判定へ↓」・判定が 見えて いる ときは 出ない・帯を 押すと 判定の 上の はしが 上の 帯の すぐ 下（8px）
#   ■ TENGERカードバトルの 3 の 効果（22:19「テンゲルカードバトルの3の効果は、相手の見えてるカードに対しても使用できるようにして！」）
#     ⑤ 相手の 手札が ぜんぶ 見えて いても 使える・選ぶ 窓で 見えて いる カードも 押せる（暗く しない・光る）・選んだ カードが 来る
#     ⑥ 見えて いる トークン（友達バトルの 決戦宝石）は 押せない（暗い・「トークンは 選べないよ」）
#   python3 test_v229.py   （SHOT=フォルダ で 画面を 写す）
import json, os, re, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
from toys_for_test import open_toys
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W); sys.path.insert(0, os.path.join(W, 'kisekae'))
SRV = os.path.join(W, 'srv_v229'); PORT = 8849; APP = f'http://localhost:{PORT}/APP/'
SHOT = os.environ.get('SHOT')
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
BENV = dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, HIST='hist_280.json', DROP='', TARGET='app')
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=BENV)
NAT = ("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;')
for d in ['APP']:
    pth = os.path.join(SRV, d, 'index.html'); html = open(pth, encoding='utf8').read()
    assert NAT[0] in html
    open(pth, 'w', encoding='utf8').write(html.replace(*NAT))
import cb_art, cb_sfx
CBA = os.path.join(W, 'ios', 'cb_assets'); CBF = cb_art.files() + cb_sfx.files()
if all(os.path.isfile(os.path.join(CBA, f)) for f in CBF):
    for f in CBF: shutil.copy(os.path.join(CBA, f), os.path.join(SRV, 'APP', f))
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
NFAKE = re.search(r'\nFAKE = """(.*?)"""', open(os.path.join(W, 'test_native.py'), encoding='utf8').read(), re.S).group(1)      # 画像の 読み取り（window.__ocrLines）
CFAKE = re.search(r'\nFAKE = """(.*?)"""', open(os.path.join(W, 'test_cb.py'), encoding='utf8').read(), re.S).group(1)          # カードバトル（部屋）
OCR_DIR = os.path.join(W, 'testdata', 'ocr'); JPG = os.path.join(OCR_DIR, 'a_tanfuku_waku.jpg')
A = json.load(open(os.path.join(OCR_DIR, 'a_tanfuku_waku.json'), encoding='utf-8'))['lines']
DATE_AT = """(() => { const D = Date, OFF = Date.UTC(2026, 9, 1, 3, 0, 0) - D.now();
  class FD extends D { constructor(...a) { if (a.length) super(...a); else super(D.now() + OFF); } static now() { return D.now() + OFF; } }
  FD.UTC = D.UTC; FD.parse = D.parse; window.Date = FD; })();"""
fails, errs = [], []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c: fails.append(label)


def shot(pg, name):
    if SHOT: os.makedirs(SHOT, exist_ok=True); pg.screenshot(path=os.path.join(SHOT, name + '.png'))


def gate(pg):
    g = pg.locator('#gate')
    for _ in range(40):
        if not g.count() or g.evaluate('e => e.hidden'): return
        try: (pg.locator('#gateGo') if pg.locator('#gateGo').count() else g).click(timeout=1500)
        except Exception: pass
        pg.wait_for_timeout(150)


def lines(r, date='10月1日(木)', start='09:00'):
    out = []
    for ln in A:
        t = ln['text'].replace('第9競走', f'第{r}競走').replace('9R', f'{r}R').replace('10月14日(水)', date).replace('発走 18:05', f'発走 {start}')
        out.append(dict(ln, text=t))
    return out


# 帯の ようす：出て いるか・字・判定の 場所・上の 帯の 下・下の タブの 上
BAR = """() => { const m = document.getElementById('minibar'), r = document.getElementById('result').getBoundingClientRect(), h = document.querySelector('header.top').getBoundingClientRect(),
  t = document.querySelector('.tabbar').getBoundingClientRect(), go = m.querySelector('.go');
  return { on: !m.hidden, go: go ? go.textContent : '', rt: r.top, rb: r.bottom, hb: h.bottom, tt: t.top, y: scrollY, max: document.documentElement.scrollHeight - innerHeight }; }"""
# 帯の hidden が かわった 回数を 数える
FLIPS = """() => { if (window.__flips) { window.__flips.n = 0; window.__flips.w = 0; return; } window.__flips = { n: 0, w: 0 }; const m = document.getElementById('minibar'); let was = m.hidden;
  new MutationObserver(rs => rs.forEach(r => { if (r.attributeName !== 'hidden') return; window.__flips.w++; const now = m.hasAttribute('hidden'); if (now !== was) { window.__flips.n++; was = now; } })).observe(m, { attributes: true, attributeFilter: ['hidden'] }); }"""


def judge_page(b, url, marks):
    def marker(source, q):
        op, key = q.get('op'), q.get('key')
        if op == 'set': marks[key] = q.get('value', '1'); return {'ok': True}
        if op == 'del': marks.pop(key, None); return {'ok': True}
        v = marks.get(key); return {'ok': True, 'has': v is not None, 'value': v}
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo', reduced_motion='reduce')
    ctx.add_init_script(DATE_AT); ctx.add_init_script(NFAKE)
    ctx.expose_binding('__saveBackup', lambda s, t: None); ctx.expose_binding('__marker', marker)
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(url); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(700)
    pg.evaluate("window.__ocrLines = %s" % json.dumps([lines(6)], ensure_ascii=False))
    pg.set_input_files('#ocrFile', [JPG]); pg.wait_for_timeout(2800)
    return ctx, pg


def room(pg, on):
    """ページの 下に あきを 足す（判定の 下の はしを 画面の 上の ほうまで 動かせる ように：テスト用）"""
    pg.evaluate("(on) => { const e = document.getElementById('__sp'); if (on && !e) document.querySelector('main').insertAdjacentHTML('beforeend', '<div id=\"__sp\" style=\"height:1400px\"></div>'); if (!on && e) e.remove(); }", on)
    pg.wait_for_timeout(300)


def put_result_bottom(pg, y):
    """判定の 下の はしが 画面の 上から y px に 来る ように ページを 動かす"""
    pg.evaluate("(y) => { const r = document.getElementById('result').getBoundingClientRect(); window.scrollTo(0, window.scrollY + r.bottom - y); }", y); pg.wait_for_timeout(450)


def pull(pg, px, over=False):
    """さらに 引っぱった ときの ように、ページの 中身を px だけ 上へ ずらして もどす（帯が かわった 回数・書いた 回数）。
       over＝iPhone の はね返りと 同じ ように scrollY も いちばん 下より px 先に する"""
    pg.evaluate(FLIPS)
    pg.evaluate("([px, over]) => { if (over) { const max = document.documentElement.scrollHeight - innerHeight; window.__syd = Object.getOwnPropertyDescriptor(window, 'scrollY'); Object.defineProperty(window, 'scrollY', { configurable: true, get: () => max + px }); } document.querySelector('main').style.transform = 'translateY(-' + px + 'px)'; }", [px, over]); pg.wait_for_timeout(400)
    mid = pg.evaluate(BAR)
    pg.evaluate("() => { document.querySelector('main').style.transform = ''; if (window.__syd) { Object.defineProperty(window, 'scrollY', window.__syd); window.__syd = null; } }"); pg.wait_for_timeout(500)
    return mid, pg.evaluate(BAR), pg.evaluate("() => window.__flips.n"), pg.evaluate("() => window.__flips.w")


try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        print('■ 判定タブの 下の 帯（判定へ）：締切済みの 短い カードで いちばん 下（まさちゃん 11/26 22:27）')
        ctx, pg = judge_page(b, APP, {})
        st0 = pg.evaluate("() => ({ chips: [...document.querySelectorAll('#result .chip')].map(c => c.innerText), card: (document.querySelector('#recCard') || {}).innerText || '' })")
        check(any('締切済み' in c for c in st0['chips']) and '締切済み' in st0['card'], f'（締切済みの レース：6R・10月1日 発走 09:00・いまは 12:00 → 下の カードは「締切済み」）')
        # ① 判定の 下の はしが 上の 帯の 下（画面の 上から 40px）
        room(pg, True); put_result_bottom(pg, 40); a = pg.evaluate(BAR)
        check(a['rb'] < a['hb'] and a['rb'] > 0 and a['on'] and a['go'] == '判定へ↑',
              f'①判定の 下の はしが 上の 帯の 下に かくれて いる（{round(a["rb"])}px ＜ 帯の 下 {round(a["hb"])}px）→ 見えて いない ので 帯が 出る・字は「判定へ↑」（{a["go"]}）')
        shot(pg, 'v229_bar_up')
        # ② 引っぱって もどす
        mid, aft, n, w = pull(pg, 80)
        check(mid['on'] and aft['on'] and mid['go'] == aft['go'] == '判定へ↑' and n == 0 and w == 0, f'②さらに 80px 引っぱって もどしても 帯は 出た まま（かわった 回数 {n}・書いた 回数 {w}・字 {mid["go"]} → {aft["go"]}）')
        # ③ はね返りの とちゅう（scrollY が いちばん 下より 先）は 数え直さない → 止まって から 見直す
        put_result_bottom(pg, 500); c = pg.evaluate(BAR)
        check(not c['on'], f'（判定が 見えて いる ＝ 帯は 出ない：判定の 下の はし {round(c["rb"])}px）')
        pg.evaluate(FLIPS)
        pg.evaluate("() => { const max = document.documentElement.scrollHeight - innerHeight; window.__syd = Object.getOwnPropertyDescriptor(window, 'scrollY'); Object.defineProperty(window, 'scrollY', { configurable: true, get: () => max + 60 }); document.querySelector('main').style.transform = 'translateY(-1500px)'; }")
        pg.wait_for_timeout(700); o1 = pg.evaluate(BAR); n1 = pg.evaluate("() => window.__flips.n"); w1 = pg.evaluate("() => window.__flips.w")
        pg.evaluate("() => { document.querySelector('main').style.transform = ''; if (window.__syd) Object.defineProperty(window, 'scrollY', window.__syd); else delete window.scrollY; }"); pg.wait_for_timeout(700)
        o2 = pg.evaluate(BAR); n2 = pg.evaluate("() => window.__flips.n")
        check(not o1['on'] and n1 == 0 and w1 == 0 and not o2['on'] and n2 == 0,
              f'③はね返りの とちゅう（scrollY が いちばん 下より 60px 先）に 判定が 画面の 外へ 出ても 帯は 出さない → もどったら 見直す（判定は 見えて いる ＝ 出ない：かわった 回数 {n1}・{n2}）')
        # ④ ページの 上（入力）・判定が 見えて いる・帯を 押す
        pg.evaluate("() => window.scrollTo(0, 0)"); pg.wait_for_timeout(450); t = pg.evaluate(BAR)
        check(t['on'] and t['go'] == '判定へ↓' and t['rt'] > t['tt'], f'④ページの 上（入力）：判定は 下（{round(t["rt"])}px）→ 帯は「判定へ↓」')
        shot(pg, 'v229_bar_down')
        pg.locator('#miniBtn').click(); pg.wait_for_timeout(600); k = pg.evaluate(BAR)
        check(not k['on'] and 4 <= k['rt'] - k['hb'] <= 12, f'④帯を 押す → 判定の 上の はしが 上の 帯の すぐ 下（{round(k["rt"] - k["hb"], 1)}px）・帯は 消える')
        put_result_bottom(pg, 40); pg.locator('#miniBtn').click(); pg.wait_for_timeout(600); k2 = pg.evaluate(BAR)
        check(not k2['on'] and 4 <= k2['rt'] - k2['hb'] <= 12, f'④「判定へ↑」を 押す → 上へ もどって 判定の 上の はしが 上の 帯の すぐ 下（{round(k2["rt"] - k2["hb"], 1)}px）')
        # いちばん 下（本当の 下）：見えて いる 所が 16px より 少なければ「判定へ↑」・48px 以上なら 出ない
        room(pg, False); pg.evaluate("() => window.scrollTo(0, document.documentElement.scrollHeight)"); pg.wait_for_timeout(500); z = pg.evaluate(BAR)
        vis = max(0, min(z['rb'], z['tt']) - max(z['rt'], z['hb']))
        check((vis < 16 and z['on'] and z['go'] == '判定へ↑') or (vis >= 48 and not z['on']) or (16 <= vis < 48),
              f'いちばん 下：判定の 見えて いる 所 {round(vis)}px → 帯 {"出る（" + z["go"] + "）" if z["on"] else "出ない"}')
        mid, aft, n, w = pull(pg, 80, over=True)
        check(n == 0 and w == 0 and mid['on'] == aft['on'] == z['on'], f'いちばん 下から さらに 80px 引っぱって（iPhone の はね返り：scrollY が いちばん 下より 80px 先）もどす：帯は かわらない（かわった 回数 {n}・書いた 回数 {w}）')
        ctx.close()
        print('■ TENGERカードバトルの 3 の 効果：見えて いる カードも 選べる（まさちゃん 11/26 22:19）')
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo')
        ctx.add_init_script(CFAKE)
        pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(APP); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(700)
        open_toys(pg, ('cb',)); pg.locator('#cbFab .fabi').click()
        pg.wait_for_function("() => !!window.CBApp && !!document.querySelector('#cbOv.on')", timeout=30000)
        pg.evaluate("() => { CBApp._t.speed(0.03); CBApp._guard = 0; CBApp._limit = 0; }"); pg.wait_for_timeout(150)

        def idle():
            pg.wait_for_function("() => window.CBApp && CBApp._t.idle", timeout=30000); pg.wait_for_timeout(60)

        def start(h0, h1):
            pg.evaluate("([h0, h1]) => { CBApp._think = () => 1e9; CBApp._opt = { hands: [h0.split(''), h1.split('')], turns: 3, full: true }; }", [h0, h1])
            if pg.evaluate("() => CBApp._t.screen") != 'menu': pg.evaluate("() => CBApp._t.menu()")
            pg.locator('#cbOv .cbmenu [data-cb=cpu]').click(); idle()
        PK = """() => { const m = document.querySelector('#cbOv .cbmod.on.cbx3'); if (!m) return null; const cs = [...m.querySelectorAll('.pick .cbc')];
          return { t: m.querySelector('p').innerText, cards: cs.map(c => ({ src: c.querySelector('img').getAttribute('src'), pick: c.dataset.cb === 'pick', dis: c.disabled, knw: c.classList.contains('knw'), tg: c.classList.contains('tg'), tok: c.classList.contains('tok') })) }; }"""
        # ⑤ 相手の 手札が ぜんぶ 見えて いる（前は 3 の 効果が 使えなかった）
        start('33312', '4567k')
        pg.evaluate("() => { const S = CBApp._t.match._.state(); S.p[1].hand.forEach(c => S.p[0].known.push(c.u)); CBApp._t.match._.apply(1, { t: 'set', u: S.p[1].hand.find(c => c.k === '6').u }); }")
        idle(); pg.wait_for_timeout(200)
        v = pg.evaluate("() => CBApp._t.view")
        check(v['can']['x3'] and len(v['can']['x3p']) == 4 and all(c['k'] for c in v['op']['hand']), f'⑤相手の 手札が ぜんぶ 見えて いる（4枚）でも「3 の 効果」を 使える（前は 使えなかった）')
        pg.locator('#cbOv [data-cb=p3yes]').first.click(); pg.wait_for_timeout(200); pk = pg.evaluate(PK)
        check(pk and len(pk['cards']) == 4 and all(c['pick'] and not c['dis'] and not c['knw'] and c['tg'] for c in pk['cards']) and sorted(c['src'] for c in pk['cards']) == ['cb_s4.webp', 'cb_s5.webp', 'cb_s7.webp', 'cb_sk.webp']
              and '見えて いる カードも 選べるよ' in pk['t'] and 'もう 見た カードは 選べないよ' not in pk['t'],
              f'⑤選ぶ 窓：見えて いる 4枚（4・5・7・神様馬）が ぜんぶ 押せる（暗く しない・光る）・「見えて いる カードも 選べるよ」')
        shot(pg, 'v229_pick3_all_seen')
        pg.locator('#cbOv .cbmod.cbx3 .pick .cbc[data-cb=pick]:has(img[src="cb_sk.webp"])').click(); idle()
        hand = pg.evaluate("() => CBApp._t.view.my.hand.map(c => c.k).sort().join('')")
        check(hand == '1233k', f'⑤神様馬を 選ぶ → 神様馬が 来る（手札 {hand}）')
        # ⑥ 見えて いる トークン（友達バトルの 決戦宝石）は 押せない
        start('33312', '4567k')
        pg.evaluate("() => { const S = CBApp._t.match._.state(), u = ++S.uid; S.p[1].hand.push({ u: u, k: 'm', tok: 1 }); S.p[0].known.push(u); S.p[0].known.push(S.p[1].hand.find(c => c.k === '4').u); CBApp._t.match._.apply(1, { t: 'set', u: S.p[1].hand.find(c => c.k === '6').u }); }")
        idle(); pg.wait_for_timeout(200)
        pg.locator('#cbOv [data-cb=p3yes]').first.click(); pg.wait_for_timeout(200); pk = pg.evaluate(PK)
        tk = [c for c in (pk or {}).get('cards', []) if c['tok']]
        check(pk and len(pk['cards']) == 5 and len(tk) == 1 and tk[0]['dis'] and tk[0]['knw'] and not tk[0]['tg'] and not tk[0]['pick'] and sum(1 for c in pk['cards'] if c['pick']) == 4 and 'トークンは 選べないよ' in pk['t'],
              f'⑥見えて いる 幻の馬トークンは 押せない（暗い・光らない）・ほかの 4枚（見えて いる 4 も）は 押せる・「トークンは 選べないよ」')
        shot(pg, 'v229_pick3_token')
        pg.locator('#cbOv .cbmod.cbx3 .pick .cbc[data-cb=pick]:has(img[src="cb_s4.webp"])').click(); idle()
        hand = pg.evaluate("() => CBApp._t.view.my.hand.map(c => c.k).sort().join('')")
        check(hand == '12334', f'⑥見えて いる 4 を 選ぶ → 4 が 来る（手札 {hand}）')
        ctx.close()
        b.close()
finally:
    srv.terminate(); shutil.rmtree(SRV, ignore_errors=True)
print('page errors:', errs[:3])
if errs: fails.append('page errors')
print('合計', len(fails), 'NG' if fails else 'OK', flush=True)
sys.exit(1 if fails else 0)
