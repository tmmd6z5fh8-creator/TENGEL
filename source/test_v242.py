# 第4.242版の テスト（まさちゃん 2026/11/29 00:03〜00:52）
#   ① 00:03「牧場の名前普通に打てるからキーボード消して！」：アプリに かなキーボード（kanapad.js）を 入れない・牧場の 名前の 欄は ふつうの 文字の 欄（⌨️ ボタン・注意の 字 なし）・打って 決められる
#   ② 00:03「アプリをいきなりスクロールすると、ピーンて音なってる！」・00:20「牧場の名前を決めてる時にスクロールするとなる」：トレーニングセンターの 音（tc/tc_app.js の SND）
#      ・出口（AudioContext）が 動いて いない 間の 効果音は 鳴らさない（あとで まとめて 鳴らない）・指で 押して 起こした 直後は 待つ
#      ・しばらく 止まって いた 出口が 動き出したら 大きさ 0 から 0.4秒で もどす・牧場の 名前の 窓が 開いて いる 間は 効果音を 鳴らさない（看板を 押した 音は 鳴る）
#   ③ 00:09「ポイントが2500ポイント切ったら、ポイントの項目のところにびっくりマークつけてお知らせして！…」：上の 帯の ポイントの 札の「！」（使える ポイントが 2,500P より 少ない とき）→
#      押すと ポイントの お知らせ（pt_note.js：説明書と 同じ 見た目・ルーレット・チケット扉・特化ゾーン・カードバトルの 勝ちの 絵）。「！」が ない とき・ほかの「ポイントを買う」は ポイントの 窓
#      00:43「下の方にポイントを購入の欄も作ってほしい！」：いちばん 下に「ポイントを 購入」（パック・サブスク・買う ボタン＝ポイントの 窓と 同じ 動き・知らせは お知らせの 上）
#      00:50「この、赤四角の文書いらない！」：「ポイントが 2,500P を 切ったよ。」と 今の ポイント・「お知らせは …」の 札は 出さない
#   ④ 00:49・00:52：作戦会議の 札の 下に「やりたいレースを予約！」の テロップ（着せ替えの 名前の 札と 同じ 形）→ 押すと 作戦会議の「レースを予約」の 入力
#   python3 test_v242.py   （SHOT=フォルダ で 画面を 写す）
import json, os, re, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W); sys.path.insert(0, W)
SHOT = os.environ.get('SHOT')
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c: fails.append(label)


def shot(pg, name, full=False):
    if SHOT: os.makedirs(SHOT, exist_ok=True); pg.screenshot(path=os.path.join(SHOT, name + '.png'), full_page=full)


nocom = lambda s: re.sub(r'(?m)^\s*//.*$', '', s)
# ---------- 静かな たしかめ ----------
bp = open('build_pwa.py', encoding='utf8').read()
check("open('kanapad.js'" not in bp and "open('pt_note.js', encoding='utf8')" in bp and bp.index("os.path.join('cb', 'cb_launch.js')") < bp.index("open('pt_note.js'") < bp.index("open('login_bonus.js'"),
      '① build_pwa.py：かなキーボード（kanapad.js）は 入れない・ポイントの お知らせ（pt_note.js）は カードバトルの 入口の あと（App Store版 だけ）')
tca = nocom(open('tc/tc_app.js', encoding='utf8').read())
check('data-kana' not in tca and 'nkb' not in tca and 'nnote' not in tca and 'kanapadon' not in tca and 'TengelKana' not in tca and '<input class="nin" type="text" enterkeyhint="done"' in tca,
      '① tc_app.js：牧場の 名前の 欄は ふつうの 文字の 欄（data-kana・⌨️ ボタン・注意の 字 なし）')
check("if (!ac || !on || !live() || nameIsOpen()) return;" in tca and "const live = () => !!ac && (ac.state === 'running' || performance.now() - askAt < 700);" in tca
      and "askAt = performance.now(); const q = ac.resume();" in tca and 'watchState(ac);' in tca and 'master.gain.linearRampToValueAtTime(on ? 1 : 0, n + 0.4)' in tca,
      '② tc_app.js：出口が 動いて いない 間・名前の 窓の 間は 効果音を 鳴らさない・動き出したら 0.4秒で 大きく')
tl = nocom(open('tc/tc_launch.js', encoding='utf8').read())
check("var RV_NAME = 'やりたいレースを予約！'" in tl and "planOpen({ add: true })" in tl and "opt && opt.add ? { add: true } : null" in tl and '[b, k, rvB].forEach' in tl and '[planB, kiseB, rvB].forEach' in tl,
      '④ tc_launch.js：「やりたいレースを予約！」の テロップ（上の 帯の 中・カードの 右上・見せる／かくす）→ 作戦会議の add')
tp = nocom(open('tc/tc_plan.js', encoding='utf8').read())
check("if (!oshi && opt && opt.add) addNew();" in tp and "if (k === 'add') { addNew(); return; }" in tp, '④ tc_plan.js：open の add ＝「レースを予約」の 入力（＋ ボタンと 同じ）')
have = set(open(os.path.join('ios', 'fonts', 'ks', 'chars_body.txt'), encoding='utf8').read())
check(all(c in have for c in 'やりたいレースを予約！'), '④ テロップの 字は テーマの しぼった 字に ある（着せ替えの 名前の 札と 同じ 字で 出る）')
pn = open('pt_note.js', encoding='utf8').read()
check('切ったよ' not in pn and 'pnmeta' not in pn and 'お知らせは ${' not in pn and '今 ${yen(' not in pn, '③ お知らせ：「ポイントが 2,500P を 切ったよ。」・今の ポイント・「お知らせは …」の 札は ない（00:50）')

# ---------- アプリを 作る（App Store版・テスト版・Web版）----------
SRV = os.path.join(W, 'srv_v242'); PORT = 8873; URL = f'http://localhost:{PORT}/'
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
ENV = dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, HIST='hist_280.json', DROP='')
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict(ENV, TARGET='app'))
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'TEST')], check=True, stdout=subprocess.DEVNULL, env=dict(ENV, TARGET='app', TENGEL_TEST='1'))
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'WEB')], check=True, stdout=subprocess.DEVNULL, env=dict(ENV, TARGET='web'))
app = open(os.path.join(SRV, 'APP', 'index.html'), encoding='utf8').read(); web = open(os.path.join(SRV, 'WEB', 'index.html'), encoding='utf8').read()
tcb = open(os.path.join(SRV, 'APP', 'tc_bundle.js'), encoding='utf8').read()
check('TengelKana' not in app and 'kanaPad' not in app and 'TengelPtNote' in app and 'id="ptNoteCss"' not in app and 'TengelPtNote' not in web and 'rvBtn' not in web and 'ptsPill' not in web,
      '①③ App Store版の index.html：かなキーボード なし・ポイントの お知らせ あり／Web版には 入らない（お知らせ・テロップ・ポイントの 札）')
check('data-kana' not in tcb and 'kanapadon' not in tcb and '.nkb' not in tcb and 'nameIsOpen()) return;' in tcb, '①② tc_bundle.js：かなキーボードの しかけ なし・名前の 窓の 間は 効果音 なし')
for d in ('APP', 'TEST'):
    p = os.path.join(SRV, d, 'index.html'); h = open(p, encoding='utf8').read()
    assert "window.__NATIVE = location.protocol === 'tengel:';" in h
    open(p, 'w', encoding='utf8').write(h.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
from assets_dir import adir
TCA = adir('tc_assets'); HAVE_TC = os.path.isdir(TCA) and os.path.exists(os.path.join(TCA, 'rt_kamisama_plate2.webp')) and os.path.exists(os.path.join(TCA, 'tc_sign.webp'))
CBA = os.path.join(W, 'ios', 'cb_assets'); HAVE_CB = os.path.exists(os.path.join(CBA, 'cb_logo.webp'))
for d in ('APP', 'TEST'):
    if HAVE_TC:
        for f in os.listdir(TCA): shutil.copy(os.path.join(TCA, f), os.path.join(SRV, d, f))
    if HAVE_CB:
        for f in ('cb_logo.webp', 'cb_board.webp', 'cb_icon.webp'): shutil.copy(os.path.join(CBA, f), os.path.join(SRV, d, f))
FAKE = open(os.path.join(W, 'test_tc.py'), encoding='utf8').read().split('FAKE = """')[1].split('"""')[0]
# アプリへの 知らせ（postMessage）を 記録する（買う ボタン → iap の buy）・効果音の 鳴らし始め（AudioBufferSourceNode.start）・大きさの 動き（gain の ramp）を 数える
HOOK = """(() => { window.__pm = []; window.__starts = 0; window.__ramps = [];
  const S = AudioBufferSourceNode.prototype.start; AudioBufferSourceNode.prototype.start = function (...a) { window.__starts++; return S.apply(this, a); };
  const R = AudioParam.prototype.linearRampToValueAtTime; AudioParam.prototype.linearRampToValueAtTime = function (v, t) { window.__ramps.push([this, v, t]); return R.call(this, v, t); };
  const wrap = () => { const h = window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.tengel; if (!h || h.__w) return; h.__w = 1; const o = h.postMessage;
    h.postMessage = function (m) { try { window.__pm.push(m.name + ':' + ((m.payload && m.payload.op) || (m.body && m.body.op) || '')); } catch (e) { } return o.apply(this, arguments); }; };
  wrap(); document.addEventListener('DOMContentLoaded', wrap); })();"""
GATE_GONE = "() => { const g = document.querySelector('#gate'); return !g || g.hidden || getComputedStyle(g).display === 'none'; }"


def boot(pg, d):
    pg.goto(URL + d + '/'); pg.wait_for_timeout(1500)
    if pg.locator('#gateGo').count(): pg.click('#gateGo'); pg.wait_for_timeout(700)
    pg.wait_for_function(GATE_GONE, timeout=15000); pg.wait_for_function("() => window.TengelWallet && document.querySelector('#ptsPill')", timeout=20000); pg.wait_for_timeout(600)


PILL = "() => { const p = document.querySelector('#ptsPill'); return { low: p.classList.contains('low'), badge: (p.querySelector('.pwn') || {}).textContent || null, al: p.getAttribute('aria-label'), tot: TengelWallet.total(), av: TengelWallet.avail() }; }"
OV = "() => ({ note: !!document.querySelector('#ptNote'), pts: !!document.querySelector('#ptOv'), mson: document.documentElement.classList.contains('mson'), on: document.documentElement.classList.contains('ptnoteon') })"
errs = []
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
try:
    with sync_playwright() as p:
        br = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'])
        # ===== ③ ポイントの 札の「！」と お知らせ（テスト版：はじめ 10,000P → テスト版の 道具で 1,000P）=====
        c = br.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo', has_touch=True, is_mobile=True)
        c.add_init_script(FAKE); c.add_init_script(HOOK)
        pg = c.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        boot(pg, 'TEST')
        a0 = pg.evaluate(PILL)
        pg.click('#ptsPill'); pg.wait_for_timeout(500); o0 = pg.evaluate(OV)
        pg.evaluate("() => TengelWallet.closePoints()"); pg.wait_for_timeout(200)
        check(not a0['low'] and a0['badge'] is None and a0['tot'] >= 2500 and o0['pts'] and not o0['note'],
              f'③ {a0["tot"]:,}P（2,500P 以上）：札に「！」なし → 押すと ポイントの 窓（前と 同じ）')
        pg.evaluate("() => document.querySelector('.tabbar button[data-tab=set]').click()"); pg.wait_for_timeout(500)
        tb = pg.evaluate("() => [...document.querySelectorAll('#setTest [data-test=ptnote],#setTest [data-test=ptlow]')].map(b => b.textContent)")
        pg.evaluate("() => document.querySelector('#setTest [data-test=ptlow]').click()"); pg.wait_for_timeout(800)
        pg.evaluate("() => document.querySelector('.tabbar button[data-tab=judge]').click()"); pg.wait_for_timeout(500)
        a1 = pg.evaluate(PILL)
        check(tb == ['お知らせを 見る', '1,000P に する（「！」を 試す）'] and a1['tot'] == 1000 and a1['low'] and a1['badge'] == '!' and 'お知らせ' in a1['al'],
              f'③ テスト版の 道具「1,000P に する」→ 札に 赤い 丸の「！」・読み上げも「ポイントの お知らせ」（{a1["tot"]:,}P）')
        bx = pg.evaluate("() => { const p = document.querySelector('#ptsPill'), b = p.querySelector('.pwn'), r = b.getBoundingClientRect(), q = p.getBoundingClientRect(), cs = getComputedStyle(b); return { inside: r.left >= q.left - 1.5 && r.right <= q.right + 1.5 && r.top >= q.top - 1.5 && r.bottom <= q.bottom + 1.5, w: b.offsetWidth, bg: cs.backgroundColor, br: getComputedStyle(p).borderColor }; }")
        check(bx['inside'] and bx['w'] == 16 and bx['bg'] == 'rgb(229, 72, 77)', f'③ 「！」は 札の 中（はみ出さない：ゆっくり 大きく なる 動きの ぶん 1.5px まで）・16px の 赤い 丸 {bx}')
        shot(pg, 'v242_pill')
        # お知らせを 開く
        pg.click('#ptsPill'); pg.wait_for_timeout(1500); o1 = pg.evaluate(OV)
        info = pg.evaluate("""() => { const n = document.querySelector('#ptNote'), cs = getComputedStyle(n), t = s => [...n.querySelectorAll(s)].map(e => e.textContent.trim());
          const cv = n.querySelector('.pnrt canvas');
          return { ff: cs.fontFamily, bg: cs.backgroundColor, z: +cs.zIndex, h2: t('h2'), h3: t('h3'), sec: t('.pnsec'), txt: n.innerText, act: document.activeElement && document.activeElement.className,
            rt: cv ? cv.dataset.ok || (cv.closest('.pnt').classList.contains('pnnone') ? 'none' : '') : null, imgs: [...n.querySelectorAll('.pnt img')].map(i => i.complete && i.naturalWidth > 0),
            buys: [...n.querySelectorAll('.pnshop [data-pt=buy]')].map(b => b.dataset.id), pat: getComputedStyle(n.querySelector('.pnbd'), '::before').backgroundImage,
            cb: !!n.querySelector('.pncb .pnptn'), go: t('.pngo'), close: t('[data-pn=close]') }; }""")
        P_ = pg.evaluate("() => ({ packs: TengelPoints.PACKS, subs: TengelPoints.SUBS })")
        check(o1['note'] and not o1['pts'] and o1['mson'] and o1['on'] and info['z'] == 72, f'③ 「！」の 札を 押す → ポイントの お知らせ（ポイントの 窓では ない・後ろは 動かない）{o1}')
        check(info['h2'] == ['お世話をして ポイント大量ゲットを 目指そう！'] and 'TENGERカードバトルの 連続勝利でも ポイントは 貰えるぞ！' in info['h3'] and info['sec'] == ['トレーニングセンター', 'TENGERカードバトル', 'ポイントを 購入']
              and info['go'] == ['🐴 トレーニングセンターを 開く', '🃏 TENGERカードバトルを 開く'] and 'ルーレットチャンス' in info['txt'] and 'チケット扉' in info['txt'] and 'ポイント特化ゾーン' in info['txt']
              and '最大 20,000P' in info['txt'] and '最大 25,000P' in info['txt'] and '壁紙チケット か 7,000P' in info['txt'] and '4連勝で 400P' in info['txt'] and '7連勝から 1勝ごとに 300P' in info['txt'],
              f'③ お知らせの 中身：見出し・トレーニングセンター（ルーレット・チケット扉・特化ゾーン）・カードバトル（連勝の ポイント）・ポイントを 購入 {info["h3"]}')
        check('切ったよ' not in info['txt'] and 'お知らせは' not in info['txt'] and '今 1,000P' not in info['txt'], '③ 00:50 の 赤四角の 文（2,500P を 切ったよ・今の ポイント・お知らせは …）は 出ない')
        check('Hiragino Sans' in info['ff'] and info['bg'] == 'rgb(10, 27, 34)' and 'repeating-linear-gradient' in info['pat'] and 'radial-gradient' in info['pat'],
              f'③ 説明書と 同じ 色と 模様（濃い 青緑の 台紙 #0a1b22・青緑の 光と 金の 細い たての 線）・字は 端末の 字 {info["ff"][:40]} {info["bg"]} {info["pat"][:30]}')
        check(info['buys'] == P_['packs'] + P_['subs'], f'③ ポイントを 購入：パック {len(P_["packs"])}・サブスク {len(P_["subs"])} の 買う ボタン（ポイントの 窓と 同じ 商品）')
        if HAVE_TC: check(info['rt'] == '1' and all(info['imgs']), f'③ 絵：ルーレット（神様馬の 台紙に 盤を 描く）・チケット扉・特化ゾーンの 絵が 出る {info["rt"]} {info["imgs"]}')
        else: check(info['rt'] in ('none', '1'), '③ 絵が ない（CI と 同じ）ときも 開ける（絵文字と 字）')
        check(info['cb'] and 'nx' in (info['act'] or ''), f'③ カードバトルの 勝ちの 絵（「あなたの 勝ち！」・連勝の ポイントの 札）・開いたら ✕ に フォーカス {info["act"]}')
        shot(pg, 'v242_note'); shot(pg, 'v242_note_full', True)
        # 盤の 数（10000P・20000P）：盤の まん中あたりの 字の 色（白っぽい 字が ある）
        if HAVE_TC:
            px = pg.evaluate("""() => { const cv = document.querySelector('#ptNote .pnrt canvas'), g = cv.getContext('2d'), d = g.getImageData(0, 0, cv.width, cv.height).data; let n = 0; for (let i = 0; i < d.length; i += 4) if (d[i + 3] > 0) n++; return n / (cv.width * cv.height); }""")
            check(px > 0.5, f'③ ルーレットの 絵は 描けて いる（色の ある 所 {px:.2f}）')
        # 買う → アプリへ iap の buy・知らせ（toast）は お知らせの 上
        pg.evaluate("() => { window.__pm.length = 0; }")
        pg.locator('#ptNote .pnshop [data-pt=buy]').first.click(); pg.wait_for_timeout(900)
        tq = pg.evaluate("""() => { const t = document.querySelector('#toast'), r = t.getBoundingClientRect(), e = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
          return { pm: window.__pm.filter(x => x.startsWith('iap:')), shown: !t.hidden, z: getComputedStyle(t).zIndex, top: !!e && (e === t || t.contains(e)), note: !!document.querySelector('#ptNote') }; }""")
        check('iap:buy' in tq['pm'] and tq['shown'] and tq['z'] == '80' and tq['top'] and tq['note'], f'③ 買う → アプリの 買い物（iap buy）・知らせは お知らせの 上に 見える（z 80）・お知らせは 開いた まま {tq}')
        # 閉じる（✕ でも 下の ボタンでも）→ 札に フォーカス・後ろが 動く
        pg.locator('#ptNote .pnfoot [data-pn=close]').click(); pg.wait_for_timeout(300); o2 = pg.evaluate(OV); f2 = pg.evaluate("() => document.activeElement && document.activeElement.id")
        pg.click('#ptsPill'); pg.wait_for_timeout(400); pg.keyboard.press('Escape'); pg.wait_for_timeout(300); o3 = pg.evaluate(OV)
        check(not o2['note'] and not o2['mson'] and not o2['on'] and f2 == 'ptsPill' and not o3['note'], f'③ 「閉じる」・Esc で 閉じる・札に フォーカスが もどる・後ろが 動く {o2} {f2}')
        # ポイントの 詳細・履歴 → ポイントの 窓
        pg.click('#ptsPill'); pg.wait_for_timeout(400); pg.locator('#ptNote [data-pn=pts]').click(); pg.wait_for_timeout(500); o4 = pg.evaluate(OV)
        pg.evaluate("() => TengelWallet.closePoints()"); pg.wait_for_timeout(200)
        # トレーニングセンター・カードバトルの ボタン（開く 道は 丸い ボタンと 同じ：TCOpen・TengelCB.open）
        pg.evaluate("() => { const t = window.TCOpen, c = TengelCB.open; window.__go = []; window.TCOpen = function () { window.__go.push('tc'); return Promise.resolve(); }; TengelCB.open = function () { window.__go.push('cb'); return Promise.resolve(); }; window.__orig = [t, c]; }")
        pg.click('#ptsPill'); pg.wait_for_timeout(400); pg.locator('#ptNote [data-pn=tc]').click(); pg.wait_for_timeout(300); o5 = pg.evaluate(OV)
        pg.click('#ptsPill'); pg.wait_for_timeout(400); pg.locator('#ptNote [data-pn=cb]').click(); pg.wait_for_timeout(300); o6 = pg.evaluate(OV)
        go = pg.evaluate("() => { window.TCOpen = window.__orig[0]; TengelCB.open = window.__orig[1]; return window.__go; }")
        check(o4['pts'] and not o4['note'] and not o5['note'] and not o6['note'] and go == ['tc', 'cb'],
              f'③ 下の ボタン：ポイントの 詳細・履歴 → ポイントの 窓・トレーニングセンター／カードバトルを 開く（お知らせは 閉じる）{go}')
        # ほかの「ポイントを買う」（data-gopt=points）は「！」が あっても ポイントの 窓
        pg.evaluate("() => { const b = document.createElement('button'); b.id = 'xbuy'; b.setAttribute('data-gopt', 'points'); b.textContent = 'ポイントを買う'; b.style.cssText = 'position:fixed;left:10px;top:300px;z-index:40'; document.body.appendChild(b); }")
        pg.click('#xbuy'); pg.wait_for_timeout(400); o7 = pg.evaluate(OV); pg.evaluate("() => { TengelWallet.closePoints(); document.getElementById('xbuy').remove(); }")
        # 2,500P 以上に もどる → 「！」は 消える・札は ポイントの 窓
        pg.evaluate("() => document.querySelector('.tabbar button[data-tab=set]').click()"); pg.wait_for_timeout(300)
        pg.evaluate("() => document.querySelector('#setTest [data-test=pts]').click()"); pg.wait_for_timeout(700)
        pg.evaluate("() => document.querySelector('.tabbar button[data-tab=judge]').click()"); pg.wait_for_timeout(300)
        a2 = pg.evaluate(PILL); pg.click('#ptsPill'); pg.wait_for_timeout(400); o8 = pg.evaluate(OV); pg.evaluate("() => TengelWallet.closePoints()")
        check(o7['pts'] and not o7['note'] and not a2['low'] and a2['badge'] is None and a2['tot'] == 11000 and o8['pts'] and not o8['note'],
              f'③ ほかの「ポイントを買う」は ポイントの 窓・ポイントが もどる（{a2["tot"]:,}P）と「！」は 消えて 札は ポイントの 窓')
        check(not errs, f'③ エラー なし {errs[:2]}')
        c.close()
        # iPad の 幅：絵は 3つ 横に 並ぶ
        c = br.new_context(viewport={'width': 820, 'height': 1180}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo', has_touch=True)
        c.add_init_script(FAKE); c.add_init_script(HOOK)
        pg = c.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        boot(pg, 'TEST')
        pg.evaluate("() => TengelPtNote.open()"); pg.wait_for_timeout(1200)
        g3 = pg.evaluate("() => { const t = [...document.querySelectorAll('#ptNote .pnart .pnt')].map(e => e.getBoundingClientRect()); return { n: t.length, row: t.length === 3 && Math.abs(t[0].top - t[2].top) < 1, w: t.map(r => Math.round(r.width)) }; }")
        check(g3['row'], f'③ iPad の 幅：絵 3つは 横 1列 {g3}')
        shot(pg, 'v242_note_ipad')
        c.close()

        # ===== ④ 作戦会議の 下の「やりたいレースを予約！」（App Store版）=====
        for (vw, vh, tag) in ((402, 874, 'iphone'), (820, 1180, 'ipad')):
            c = br.new_context(viewport={'width': vw, 'height': vh}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo', has_touch=True, is_mobile=tag == 'iphone')
            c.add_init_script(FAKE); c.add_init_script(HOOK)
            pg = c.new_page(); e4 = []; pg.on('pageerror', lambda e: e4.append(str(e)))
            boot(pg, 'APP'); pg.wait_for_timeout(1200)
            L = pg.evaluate("""() => { const R = e => { const r = e.getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom].map(v => Math.round(v * 10) / 10); };
              const rv = document.getElementById('rvBtn'), b = document.getElementById('planBtn'), k = document.getElementById('kiseBtn'), kl = k.querySelector('.kisel'), hd = document.querySelector('header.top'), rs = document.getElementById('rsvBtn');
              const cs = getComputedStyle(rv), ks = getComputedStyle(kl);
              return { rv: R(rv), plan: R(b), kise: R(k), hd: R(hd), rsv: R(rs), txt: rv.textContent, dk: rv.classList.contains('dk'), par: rv.parentNode === hd, hid: rv.hidden,
                same: [cs.fontFamily === ks.fontFamily, cs.fontWeight === ks.fontWeight, cs.borderTopColor === ks.borderTopColor, cs.backgroundColor === ks.backgroundColor, cs.color === ks.color],
                k: parseFloat(b.style.getPropertyValue('--dk')) || 1 }; }""")
            ink = [L['plan'][0] + 118 * L['k'] * 16 / 500, L['plan'][1] + 47 * L['k'] * 30 / 200, L['plan'][0] + 118 * L['k'] * 483 / 500, L['plan'][1] + 47 * L['k'] * 170 / 200]
            lap = lambda a, r: r[2] > a[0] and r[0] < a[2] and r[3] > a[1] and r[1] < a[3]
            if tag == 'iphone':
                mid = (L['rv'][0] + L['rv'][2]) / 2 - (L['rsv'][0] + L['rsv'][2]) / 2
                pg.evaluate("() => { document.getElementById('rvBtn').hidden = true; window.dispatchEvent(new Event('resize')); }"); pg.wait_for_timeout(400)
                h0 = pg.evaluate("() => document.querySelector('header.top').getBoundingClientRect().height")
                pg.evaluate("() => { document.getElementById('rvBtn').hidden = false; window.dispatchEvent(new Event('resize')); }"); pg.wait_for_timeout(400)
                h1 = pg.evaluate("() => document.querySelector('header.top').getBoundingClientRect().height")
                check(L['txt'] == 'やりたいレースを予約！' and L['dk'] and L['par'] and not L['hid'] and all(L['same']) and abs(mid) <= 1 and L['rv'][1] >= ink[3] + 1 and not lap(L['rv'], L['kise'])
                      and L['rv'][3] <= L['hd'][3] - 1 and h1 - h0 <= 8,
                      f'④ iPhone：上の 帯の 中・作戦会議の 札の すぐ 下（まん中 ずれ {mid:.1f}・札の 下から {L["rv"][1] - ink[3]:.1f}px）・着せ替えの 名前の 札と 同じ 字・色・帯の 高さ ＋{h1 - h0:.1f}px {L["rv"]}')
            else:
                fc = pg.evaluate("() => { const c = document.getElementById('fabCol'); return c && !c.classList.contains('rw') ? c.getBoundingClientRect().top : null; }")
                check(not L['dk'] and not L['hid'] and L['rv'][1] >= ink[3] + 1 and L['kise'][1] >= L['rv'][3] + 2 and abs((L['rv'][0] + L['rv'][2]) / 2 - (ink[0] + ink[2]) / 2) <= 1
                      and (fc is None or fc >= L['kise'][3]),
                      f'④ iPad：カードの 右上 ＝ 作戦会議の 札の 下に テロップ・その 下に 着せ替え（右下の 丸の 列は その 下 {fc}）{L["rv"]} {L["kise"]}')
            shot(pg, f'v242_rv_{tag}')
            pg.click('#rvBtn'); pg.wait_for_function("() => { const p = document.querySelector('#tcPlan'); return p && getComputedStyle(p).display !== 'none'; }", timeout=60000); pg.wait_for_timeout(800)
            pl = pg.evaluate("() => { const p = document.querySelector('#tcPlan'); return { t: p.innerText.slice(0, 80), file: !!p.querySelector('[data-p=file]'), save: !!p.querySelector('[data-a=save],[data-k=save]') }; }")
            check('レースを予約' in pl['t'] and pl['file'], f'④ {tag}：押すと 作戦会議の「レースを予約」の 入力が すぐ 開く {pl["t"][:30]!r}')
            shot(pg, f'v242_rv_{tag}_plan')
            check(not e4, f'④ {tag}：エラー なし {e4[:2]}')
            c.close()

        # ===== ①② トレーニングセンター：牧場の 名前・音 =====
        if not HAVE_TC:
            print('※ トレーニングセンターの 絵が ない ので、トレーニングセンターの 確かめは しない')
        else:
            c = br.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo', has_touch=True)
            c.add_init_script(FAKE); c.add_init_script(HOOK)
            pg = c.new_page(); e5 = []; pg.on('pageerror', lambda e: e5.append(str(e)))
            boot(pg, 'APP')
            pg.locator('#tcFab').click(); pg.wait_for_function("() => window.TCApp && document.querySelector('#tcOv.on') && !document.querySelector('#tcOv .tcld')", timeout=90000); pg.wait_for_timeout(1500)
            pg.wait_for_function("() => TCApp._snd.ac && TCApp._snd.ac.state === 'running'", timeout=15000)
            SE = "async (n) => { const s0 = window.__starts; await TCApp._snd.se(n || 'tc_se_button.m4a'); await new Promise(r => setTimeout(r, 120)); return window.__starts - s0; }"
            s1 = pg.evaluate(SE)
            pg.evaluate("() => TCApp._snd.ac.suspend()"); pg.wait_for_timeout(900)
            s2 = pg.evaluate(SE); st2 = pg.evaluate("() => TCApp._snd.ac.state")
            M = "() => { const S = TCApp._snd, rs = window.__ramps.filter(r => r[0].value !== undefined && r[0] !== null); return rs.length; }"
            n0 = pg.evaluate("() => window.__ramps.length")
            pg.evaluate("() => TCApp._snd.ac.resume()"); pg.wait_for_timeout(700)
            r3 = pg.evaluate("(n0) => { const rs = window.__ramps.slice(n0); return rs.map(r => [Math.round(r[1] * 100) / 100, Math.round((r[2] - TCApp._snd.ac.currentTime) * 100) / 100]); }", n0)
            s3 = pg.evaluate("() => window.__starts")
            check(s1 == 1 and s2 == 0 and st2 == 'suspended', f'② 出口が 動いて いる → 効果音 鳴る（{s1}）・止まって いる（{st2}）→ 鳴らさない（{s2}：あとで まとめて 鳴らない）')
            check(any(v == 1 for v, _ in r3), f'② 止まって いた 出口が 動き出したら 大きさ 0 → 1（0.4秒）{r3[:3]}')
            # 牧場の 名前の 窓：看板を 押した 音は 鳴る・窓の 間は 鳴らさない・閉じたら 鳴る
            k0 = pg.evaluate("() => window.__starts")
            pg.locator('#tcOv .tcnm').click(); pg.wait_for_timeout(700)
            k1 = pg.evaluate("() => window.__starts"); op = pg.evaluate("() => TCApp.farm.isOpen()")
            s4 = pg.evaluate(SE)
            kb = pg.evaluate("() => ({ pad: !!document.getElementById('kanaPad'), kana: !!document.querySelector('#tcnmd [data-kana]'), nkb: !!document.querySelector('#tcnmd .nkb'), note: !!document.querySelector('#tcnmd .nnote'), act: document.activeElement && document.activeElement.className })")
            pg.locator('#tcnmd .nin').fill('テスト牧場'); pg.locator('#tcnmd [data-nm=ok]').click(); pg.wait_for_timeout(500)
            nm = pg.evaluate("() => ({ name: TCApp.farm.name(), open: TCApp.farm.isOpen() })")
            s5 = pg.evaluate(SE)
            check(op and k1 - k0 == 1 and s4 == 0 and s5 == 1, f'② 看板を 押した 音は 鳴る（{k1 - k0}）・名前の 窓の 間は 効果音を 鳴らさない（{s4}）・閉じたら 鳴る（{s5}）')
            check(not kb['pad'] and not kb['kana'] and not kb['nkb'] and not kb['note'] and kb['act'] == 'nin' and nm == {'name': 'テスト牧場', 'open': False},
                  f'① 牧場の 名前の 窓：かなキーボード・⌨️ ボタン・注意の 字 なし・ふつうに 打って 決められる {kb} {nm}')
            check(not e5, f'①② エラー なし {e5[:2]}')
            c.close()
        br.close()
finally:
    srv.terminate()
shutil.rmtree(SRV, ignore_errors=True)
# ---------- ⑤ GitHub の Mac（selftest.js の ptNote・run.sh の PTNPY・P1 の 印）----------
st = open(os.path.join(W, 'ios', 'ci', 'selftest.js'), encoding='utf8').read(); rs = open(os.path.join(W, 'ios', 'ci', 'run.sh'), encoding='utf8').read()
check("step(R, 'ptNote'" in st and st.index("step(R, 'fabHide'") < st.index("step(R, 'ptNote'") < st.index("step(R, 'manualOv'") and "await mark('rv-btn');" in st and "await mark('pt-note');" in st and "await mark('pt-note-shop');" in st
      and ' rec numpad rv-btn pt-note pt-note-shop manual-ov ' in rs and 'pt note: $(python3 -c "$PTNPY"' in rs and 'pt note (ipad): $(python3 -c "$PTNPY"' in rs,
      '⑤ selftest.js の ptNote（fabHide と 説明書の あいだ・印 rv-btn → pt-note → pt-note-shop）・run.sh の PTNPY の 行（iPhone・iPad）・P1 の 印の 順')
pya = re.search(r"\nPTNPY='\n(.*?)\n'\n", rs, re.S).group(1)
good = {'ptNote': {'api': True, 'rv': [138, 128, 255, 146], 'plan': [137, 86, 255, 133], 'kise': [263, 92, 373, 143], 'hd': [0, 0, 402, 160], 'rvTxt': 'やりたいレースを予約！', 'rvDk': True, 'rvSame': True,
                   'open': True, 'z': 72, 'ff': '"Hiragino Sans", "Hiragino Kaku Gothic', 'h2': 'お世話をして ポイント大量ゲットを 目指そう！', 'secs': ['トレーニングセンター', 'TENGERカードバトル', 'ポイントを 購入'],
                   'buys': 7, 'rt': 'none', 'closed': True}}
tmp = os.path.join(W, 't4', '_ptnpy.json'); os.makedirs(os.path.dirname(tmp), exist_ok=True)
def runpy(d):
    json.dump(d, open(tmp, 'w', encoding='utf8')); return subprocess.run(['python3', '-c', pya, tmp], capture_output=True, text=True).stdout.strip()
r1 = runpy(good)
bad1 = json.loads(json.dumps(good)); bad1['ptNote']['rv'] = [263, 120, 373, 150]                      # 着せ替えに 重なる
bad2 = json.loads(json.dumps(good)); bad2['ptNote']['buys'] = 4                                       # 買う ボタンが たりない
bad3 = json.loads(json.dumps(good)); bad3['ptNote']['rvDk'] = False; bad3['ptNote']['kise'] = [263, 150, 373, 200]      # カードの 右上：着せ替えが テロップの 下（OK）
r2, r3, r4 = runpy(bad1), runpy(bad2), runpy(bad3)
check(r1.endswith('-> OK') and 'CHECK' in r2 and 'CHECK' in r3 and r4.endswith('-> OK'), f'⑤ PTNPY：よい 形 → OK・着せ替えに 重なる／買う ボタンが たりない → CHECK・カードの 右上の 形 → OK {r1[-40:]!r}')
print('FAILS', len(fails), fails)
sys.exit(1 if fails else 0)
