# 作戦会議の 入口（判定タブの「レース情報」の カードの 右上の 札）の テスト（第4.160版）
#   まさちゃん 2026/11/12 14:58「作戦会議は、1番左の項目判定のページでも開けるようにして！アイコンは右上に設置して！」
#   ・App Store版（TARGET=app）：判定タブの いちばん 上の カード「レース情報」の 右上に 作戦会議の 札（tc_icon_plan.webp）→ 指で 押すと 判定タブの 上に 作戦会議が 開く
#     （トレーニングセンターは 開かない・開いた まま 表示される・うしろの 判定タブは 動かない・「とじる」で 判定タブに もどる）
#   第4.165版（まさちゃん 2026/11/13 13:55「赤枠の作戦会議のアイコンを青四角のあたりに設置して！黄丸のところに、タップすると壁紙や結果ボードカスタムのところに飛べるアイコン設置して！アイコン二枚目！」）：
#     ・札は カードの 右上の かど（見える 札の 上は カードの 上の ふちより 5px 上・右は カードの 右はしより 11px 外＝画面の 右はしから 5px）
#     → 14:16「何か変だから、2枚目のアイコンにして、作戦会議のすぐ下に設置してみて！あと下にテロップ入れて！壁紙&ボード着せ替え、って！」：
#     ・作戦会議の 札の すぐ 下に 横長の カプセルの ボタン（#kiseBtn・tc_icon_kise2.webp：100×36）＋ その 下に 名前の 札「壁紙&ボード着せ替え」
#       → 押すと 設定タブの「着せ替え」が 上の 帯の すぐ 下に 出る
#       「着せ替え」の カードの 右上の「結果ボードカスタムへ↓」（#kiseJump）→ 押すと「結果ボードカスタム」が 上の 帯の すぐ 下に 出る
#     ・データの チップは ボタンに かからない（1行めは ボタンの 手前で 折り返す：すきまの 部品 .kisesp。2行めも かかる ときは 行 ぜんぶの 右を あける）・
#       データの 行を 作り直しても（アプリが 中身を 入れかえる）すぐ もとどおり
#   ・どの 壁紙でも 札と ボタンは 見出しの 字・データの チップ・壁紙の 上の絵に 重ならない・画面から 出ない
#   ・トレーニングセンターの 中の 作戦会議とは 同じ もの（予約した レースは どちらからも 見える・行ったり 来たり しても こわれない）
#   ・Web版：札は 出ない（tc_launch.js は アプリ だけ）
#   python3 test_plan_entry.py   （ios/tc_assets/ が ない とき（CI）は 絵なしの 札〈字〉で 同じ ことを 確かめる。壁紙の 絵 ios/kisekae_blobs/ が ない ときは 標準の 見た目 だけ）
import datetime as _dt, json, math, os, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv_tc'); PORT = 8802; APP = f'http://localhost:{PORT}/APP/'; WEB = f'http://localhost:{PORT}/TENGEL/'
SHOT = os.environ.get('SHOT')          # 画面を 写す フォルダ（見る 用）
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'TENGEL')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, HIST='hist_280.json', DROP=''))
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, HIST='hist_280.json', DROP='', TARGET='app'))
from assets_dir import adir
TCA = adir('tc_assets'); HAVE = os.path.isdir(TCA) and len(os.listdir(TCA)) > 100
BL = os.environ.get('KISEKAE_ASSETS') or os.path.join(W, 'ios', 'kisekae_blobs'); WALL = os.path.isdir(BL) and len(os.listdir(BL)) > 50
pth = os.path.join(SRV, 'APP', 'index.html'); html = open(pth, encoding='utf8').read()
assert "window.__NATIVE = location.protocol === 'tengel:';" in html
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
if HAVE:
    for f in os.listdir(TCA): shutil.copy(os.path.join(TCA, f), os.path.join(SRV, 'APP', f))
else: print('※ トレーニングセンターの 絵と 音（ios/tc_assets）が ない ので、絵なしの 札（字）で 確かめる')
if WALL:
    for f in os.listdir(BL): shutil.copy(os.path.join(BL, f), os.path.join(SRV, 'APP', 'ks_' + f))
else: print('※ 壁紙の 絵（ios/kisekae_blobs）が ない ので、標準の 見た目 だけ')
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c: fails.append(label)


FAKE = open(os.path.join(W, 'test_tc.py'), encoding='utf8').read().split('FAKE = """')[1].split('"""')[0]      # アプリの 窓口の にせもの（test_tc.py と 同じ）
PW, PH, INK = 118, 47, (16 / 500, 30 / 200, 483 / 500, 170 / 200)      # 絵の 大きさ・絵の 中の 札の 場所（tc/tc_launch.js と 同じ）
UP, OVER, EDGE, CLEAR = 5, 11, 5, 6                                    # 札：上へ はみ出す 長さ・右へ はみ出す 長さ・画面の 右はしから あける 長さ・すぐ 上の ものから あける 長さ（tc/tc_launch.js と 同じ）
KBOX, KW, KH, KUNDER, KLAP, KGAP = 110, 100, 36, 3, 3, 4               # 「壁紙&ボード着せ替え」の ボタン：幅（作戦会議の 見える 札と 同じ）・カプセルの 幅と 高さ・札の 下から あける 長さ・名前の 札が 重なる 長さ・チップから あける 長さ
KNAME = '壁紙&ボード着せ替え'; KLABEL = KNAME + '（押すと 設定の 着せ替え・結果ボードカスタムを ひらくよ）'


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


# 札・「壁紙&ボード着せ替え」の ボタン・カード・見出しの 字・データの チップの 場所
#   第4.168版（まさちゃん 2026/11/14 02:12「青四角の項目は、表示されるページは画面を上下にスライドしても、位置がずれずそこにいるようにして！」）：札と ボタンは 画面に 止める（position:fixed・body の 下）。
#   場所は「ページを いちばん 上に した ときの カードの 右上の かど」＝ いちばん 上で 測る（前は カードの 中に あった ので 上の ほうへ 寄せてから 測った）
GEO = """() => { const b = document.getElementById('planBtn'); if (!b) return null; const card = document.querySelector('#v-judge .card.planc') || document.querySelector('#v-judge .card'), h = card.querySelector('h2'), k = document.getElementById('kiseBtn'), sj = document.getElementById('slotJudge');
  window.scrollTo(0, 0); const c0 = card.getBoundingClientRect(), hd = document.querySelector('header').getBoundingClientRect();
  let above = null;                                   // カードの すぐ 上の もの（単勝5連勝の お知らせ・壁紙の 上の絵）の 下の はし。なければ 上の 帯
  for (const e of [document.getElementById('w5Banner'), document.getElementById('ksBnr')]) { if (e && above == null) { const r = e.getBoundingClientRect(); if (r.height > 0 && r.width > 0) above = r.bottom; } }
  const gap0 = c0.top - (above == null ? hd.bottom : above);
  const R = e => { const r = e.getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom]; };
  const g = document.createRange(); g.selectNodeContents(h); const t = g.getBoundingClientRect();
  const im = b.querySelector('img'), tx = b.querySelector('.plt'), r = b.getBoundingClientRect(), cs = getComputedStyle(card);
  const hit = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
  const kim = k ? k.querySelector('img') : null, kft = k ? k.querySelector('.kft') : null, kl = k ? k.querySelector('.kisel') : null, kc = kim || kft;
  const at = e => { if (!e) return false; const q = e.getBoundingClientRect(), t = document.elementFromPoint(q.left + q.width / 2, q.top + q.height / 2); return !!t && (t === k || k.contains(t)); };
  const bar = sj ? sj.querySelector('.slotbar') : null, sp = sj ? sj.querySelector('.kisesp') : null, sl = sj ? sj.querySelector('.sl-lab') : null;
  return { btn: R(b), card: R(card), h2: [t.left, t.top, t.right, t.bottom], img: im ? [im.naturalWidth, im.naturalHeight] : null, txt: tx ? [tx.textContent].concat(R(tx)) : null,
    hdr: hd.bottom, hit: hit === b || (hit && b.contains(hit)), first: card === document.querySelector('#v-judge .card') && b.parentNode === document.body && getComputedStyle(b).position === 'fixed',
    label: b.getAttribute('aria-label'), dis: b.disabled, pos: getComputedStyle(card).position, vw: document.documentElement.clientWidth, gap0: gap0,
    chips: sj ? Array.from(sj.querySelectorAll('.slotchip')).map(R).filter(x => x[3] > x[1]) : [], pad: sj ? sj.style.paddingRight : '', sl: sl ? R(sl) : null,
    sp: sp ? R(sp) : null, spn: sj ? sj.querySelectorAll('.kisesp').length : 0, spNext: sp && sp.nextElementSibling ? sp.nextElementSibling.textContent : null, inner: [cs.paddingLeft, cs.paddingRight, cs.borderLeftWidth, cs.borderRightWidth].map(parseFloat),
    kise: k ? R(k) : null, kcap: kc ? R(kc) : null, klab: kl ? R(kl) : null, kname: kl ? kl.textContent : null, khit: at(kc) && at(kl), kimg: kim ? [kim.naturalWidth, kim.naturalHeight] : null, kft: !!kft,
    klabel: k ? k.getAttribute('aria-label') : null, kpar: !!k && k.parentNode === document.body && getComputedStyle(k).position === 'fixed', kfont: kl ? [getComputedStyle(kl).fontFamily.split(',')[0].trim().replace(/"/g, ''), getComputedStyle(kl).fontWeight, getComputedStyle(kl).backgroundColor, getComputedStyle(kl).color] : null,
    night: (() => { const h = getComputedStyle(document.querySelector('header.top')); return [h.backgroundColor, h.color]; })() }; }"""


def plate(q):          # 見える 札（左・上・右・下）
    l, t = q['btn'][0], q['btn'][1]
    return [l + PW * INK[0], t + PH * INK[1], l + PW * INK[2], t + PH * INK[3]]


def geo_ok(q):         # 札は カードの 右上の かど（上へ 5・右へ 11 はみ出す）・見出しの 字と データの チップに 重ならない・すぐ 上の ものから はなれて いる・画面の 中・押せる
    if not q: return False, 'ボタンが ない'
    p = plate(q); c = q['card']; w = [round(q['btn'][2] - q['btn'][0], 1), round(q['btn'][3] - q['btn'][1], 1)]
    up = max(0, min(UP, q['gap0'] - CLEAR)); over = max(0, min(OVER, q['vw'] - c[2] - EDGE))
    row = min((r[1] for r in q['chips']), default=None)
    d = dict(size=w, up=round(c[1] - p[1], 1), over=round(p[2] - c[2], 1), h2=round(p[0] - q['h2'][2], 1), row=round(row - p[3], 1) if row is not None else None,
             edge=round(q['vw'] - p[2], 1), above=round(q['gap0'] - (c[1] - p[1]), 1), under=round(p[1] - q['hdr'], 1))
    ok = (w == [PW, PH] and abs(d['up'] - up) <= 1 and abs(d['over'] - over) <= 1 and d['h2'] >= 40 and (d['row'] is None or d['row'] >= 6) and d['edge'] >= EDGE - 0.6 and d['above'] >= CLEAR - 0.6 and d['under'] > 0
          and q['hit'] and q['first'] and q['pos'] == 'relative' and not q['dis'])
    return ok, d


def kise_ok(q):        # 「壁紙&ボード着せ替え」の ボタン：作戦会議の 札の すぐ 下（まん中を そろえる）・カプセル 100×36・その 下に 名前の 札・データの チップと 見出しの 字に かからない・画面の 中・押せる
    if not q or not q.get('kise') or not q.get('kcap') or not q.get('klab'): return False, 'ボタンが ない'
    p = plate(q); c = q['kcap']; l = q['klab']; k = q['kise']
    box = [min(k[0], c[0], l[0]), min(k[1], c[1]), max(k[2], c[2], l[2]), max(k[3], c[3], l[3])]            # ボタン ぜんぶ（カプセル ＋ 名前の 札）
    hits = [r for r in q['chips'] + ([q['sl']] if q['sl'] else []) if r[2] > box[0] - (KGAP - 0.6) and r[0] < box[2] and r[3] > box[1] - 1 and r[1] < box[3] + 1]
    near = min((box[0] - r[2] for r in q['chips'] if r[3] > box[1] - 1 and r[1] < box[3] + 1), default=None)   # ボタンと 同じ 高さの チップの 右はしから ボタンまで
    d = dict(cap=[round(c[2] - c[0], 1), round(c[3] - c[1], 1)], under=round(c[1] - p[3], 1), mid=round((c[0] + c[2]) / 2 - (p[0] + p[2]) / 2, 1), lap=round(c[3] - l[1], 1),
             lmid=round((l[0] + l[2]) / 2 - (c[0] + c[2]) / 2, 1), lw=round(l[2] - l[0], 1), lh=round(l[3] - l[1], 1), right=round(box[2] - p[2], 1), edge=round(q['vw'] - box[2], 1),
             h2=round(box[0] - q['h2'][2], 1), chip=round(near, 1) if near is not None else None, hits=len(hits), pad=q['pad'], sp=q['spn'], rows=len({round(r[1]) for r in q['chips']}), bottom=round(box[3] - q['card'][1], 1))
    ok = (abs(d['cap'][0] - KW) <= 0.6 and abs(d['cap'][1] - KH) <= 0.6 and abs(d['under'] - KUNDER) <= 1 and abs(d['mid']) <= 1 and abs(d['lap'] - KLAP) <= 1 and abs(d['lmid']) <= 1 and 60 <= d['lw'] <= KBOX + 0.5 and 14 <= d['lh'] <= 20
          and abs(d['right']) <= 1 and d['edge'] >= EDGE - 0.6 and d['h2'] >= 8 and not hits and q['kname'] == KNAME and q['khit'] and q['kpar'] and q['klabel'] == KLABEL and abs((k[2] - k[0]) - KBOX) <= 0.6)
    return ok, d


def swipe(cdp, pg, x, y0, y1):          # 指で なぞる（下から 上へ＝ページを 送る 向き）
    cdp.send('Input.dispatchTouchEvent', dict(type='touchStart', touchPoints=[dict(x=x, y=y0)]))
    for i in range(1, 11): cdp.send('Input.dispatchTouchEvent', dict(type='touchMove', touchPoints=[dict(x=x, y=y0 + (y1 - y0) * i / 10)])); pg.wait_for_timeout(16)
    cdp.send('Input.dispatchTouchEvent', dict(type='touchEnd', touchPoints=[])); pg.wait_for_timeout(450)


def tap_btn(pg, sel='#planBtn'):
    r = pg.evaluate("(s) => { const r = document.querySelector(s).getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }", sel)
    pg.touchscreen.tap(*r)


# 設定タブの 欄が 上の 帯の すぐ 下に 出て いるか（欄の 上の はし − 上の 帯の 下の はし）
SEC = """(id) => { const s = document.getElementById(id), hd = document.querySelector('header').getBoundingClientRect(), j = document.getElementById('kiseJump'), c = document.getElementById('setKisekae');
  const R = e => { const r = e.getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom]; }; let h2 = null;
  if (c) { const g = document.createRange(); g.selectNodeContents(c.querySelector('h2')); const t = g.getBoundingClientRect(); h2 = [t.left, t.top, t.right, t.bottom]; }
  const jr = j ? j.getBoundingClientRect() : null, jh = jr ? document.elementFromPoint(jr.left + jr.width / 2, jr.top + jr.height / 2) : null;
  return { tab: document.querySelector('.tabbar button[aria-selected="true"]').dataset.tab, gap: s ? s.getBoundingClientRect().top - hd.bottom : null, sy: window.scrollY,
    jump: j ? R(j) : null, jtxt: j ? j.textContent : null, jhit: !!j && jh === j, jpar: !!j && j.parentNode === c, card: c ? R(c) : null, h2: h2, next: c && c.nextElementSibling ? c.nextElementSibling.id : null,
    head: s ? s.querySelector('h2').textContent : null }; }"""


try:
    print('■ 中身')
    app = open(os.path.join(SRV, 'APP', 'index.html'), encoding='utf8').read(); web = open(os.path.join(SRV, 'TENGEL', 'index.html'), encoding='utf8').read()
    tb = open(os.path.join(SRV, 'APP', 'tc_bundle.js'), encoding='utf8').read()
    check("'planBtn'" in app and 'TCPlanOpen' in app and "'planHost'" in app and 'tc_icon_plan.webp' in app, 'App Store版：判定タブの 作戦会議の 札と 入れ物（planBtn・planHost・TCPlanOpen）が 入って いる')
    check("'kiseBtn'" in app and "'kiseJump'" in app and 'tc_icon_kise2.webp' in app and "'tc_icon_kise.webp'" not in app and 'KiseGo' in app and KNAME in app,
          'App Store版：「壁紙&ボード着せ替え」の ボタンと「結果ボードカスタムへ↓」の 札（kiseBtn・kiseJump・tc_icon_kise2.webp）が 入って いる')
    check('planBtn' not in web and 'TCPlanOpen' not in web and 'planHost' not in web and 'tc_bundle' not in web and 'kiseBtn' not in web and 'kiseJump' not in web and 'KiseGo' not in web and 'kisesp' not in web and KNAME not in web,
          'Web版：札も「壁紙&ボード着せ替え」の ボタンも 入って いない（かわらない）')
    if HAVE:
        from PIL import Image as _Im
        _k = _Im.open(os.path.join(TCA, 'tc_icon_kise2.webp')); _a = _k.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox()
        check(_k.size[0] == 440 and abs((_a[2] - _a[0]) / (_a[3] - _a[1]) - 2047 / 736) < 0.03 and abs(KW / KH - 2047 / 736) < 0.03 and not os.path.exists(os.path.join(TCA, 'tc_icon_kise.webp')),
              f'ボタンの 絵（tc_icon_kise2.webp：{_k.size}）の カプセルは よこ÷たて {(_a[2] - _a[0]) / (_a[3] - _a[1]):.3f}（画面では {KW}×{KH}）・はじめの 丸い 絵（tc_icon_kise.webp）は アプリに 入れない')
    check('window.TCPlan = TCPlan' in tb and 'planBtn' not in tb, '作戦会議の 本体は 押した ときに 読む 束（tc_bundle.js）の 中')
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'])
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo', has_touch=True, is_mobile=True)
        ctx.add_init_script(FAKE)
        pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        reqs = []; pg.on('request', lambda r: reqs.append(r.url.split('/')[-1]))
        pg.goto(APP); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(600)
        pg.evaluate("() => { const t = document.getElementById('toast'); if (t) t.hidden = true; }")
        cdp = ctx.new_cdp_session(pg)
        print('■ 判定タブの 右上の 札')
        q = pg.evaluate(GEO); ok, d = geo_ok(q)
        check(ok and q['label'] == '作戦会議（押すと ひらくよ）' and abs(d['up'] - UP) <= 1 and abs(d['over'] - OVER) <= 1,
              f'「レース情報」の カードの 右上の かどに 作戦会議の 札（絵 {PW}×{PH}＝見える 札 110×33・押せる 高さ {PH}）：カードの 上の ふちより {d["up"]} 上・右はしより {d["over"]} 外（画面の 右はしから {d["edge"]}）・'
              f'見出しの 字から {d["h2"]}・データの 行まで {d["row"]}・すぐ 上の もの（上の 帯）から {d["above"]}・上の 帯に かくれない')
        kok, kd = kise_ok(q)
        check(kok, f'作戦会議の 札の すぐ 下に「壁紙&ボード着せ替え」の ボタン：カプセル {kd["cap"]}・札の 下から {kd["under"]}・まん中の ずれ {kd["mid"]}・右はしは 札と 同じ（ずれ {kd["right"]}）・画面の 右はしから {kd["edge"]}・'
                   f'見出しの 字から {kd["h2"]}・カードの 上から 下の はしまで {kd["bottom"]}・押せる（カプセルも 名前の 札も）')
        check(kok and q['kname'] == KNAME and q['kfont'][0] == 'BIZ UDPGothic' and q['kfont'][1] == '700' and [q['kfont'][2], q['kfont'][3]] == q['night'],
              f'カプセルの 下に 名前の 札「{q["kname"]}」（幅 {kd["lw"]}・高さ {kd["lh"]}・カプセルに {kd["lap"]} 重ねる・まん中の ずれ {kd["lmid"]}）：字は 本文の 字（{q["kfont"][0]}）・太さ {q["kfont"][1]}・色は 上の 帯と 同じ')
        check(kok and kd['hits'] == 0 and kd['pad'] == '' and kd['sp'] == 1 and kd['rows'] == 3 and q['spNext'] and q['spNext'].startswith('マザーデータ') and kd['chip'] is not None and kd['chip'] >= KGAP - 0.6,
              f'データの チップは ボタンに かからない：1行めは ボタンの 手前で 折り返す（すきまの 部品 {kd["sp"]}こ・その 次は「{q["spNext"]}」・1行めの 右はしから ボタンまで {kd["chip"]}）・2行め からは カードの 幅 いっぱい（{kd["rows"]}行）')
        if HAVE: check(q['kimg'] == [440, 163] and not q['kft'], f'ボタンの 絵は まさちゃんの カプセルの アイコン（tc_icon_kise2.webp：{q["kimg"]}）')
        else: check(q['kimg'] is None and q['kft'] and q['kname'] == KNAME, f'絵が ない とき：色の カプセル ＋ 名前の 札「{q["kname"]}」')
        check(pg.evaluate("() => typeof window.TCApp === 'undefined' && typeof window.TCPlan === 'undefined' && !document.getElementById('tcOv') && !document.getElementById('planHost')")
              and 'tc_bundle.js' not in reqs, '押す 前：トレーニングセンターの 束は まだ 読んで いない（判定タブを 開く だけでは 重く ならない）')
        shot(pg, 'plan_btn')
        # ほかの タブでは 出ない
        vis = {}
        for tab in ('win5', 'rec', 'stats', 'set', 'judge'):
            pg.locator(f'.tabbar button[data-tab="{tab}"]').click(); pg.wait_for_timeout(350)
            vis[tab] = pg.evaluate("() => ['planBtn', 'kiseBtn'].map(i => { const r = document.getElementById(i).getBoundingClientRect(); return r.width > 0 && r.height > 0; })")
        check(vis == dict(win5=[False, False], rec=[False, False], stats=[False, False], set=[False, False], judge=[True, True]), f'札と「壁紙&ボード着せ替え」の ボタンは 判定タブ だけ（ほかの タブでは 出ない）{vis}')
        print('■ 第4.168版：画面を 上下に 動かしても 右の ボタン（作戦会議・壁紙&ボード着せ替え・推し馬・トレーニングセンター・思い出フィギュア）は 同じ 所')
        POS5 = "() => ['planBtn', 'kiseBtn', 'oshiFab', 'tcFab', 'figFab'].map(i => { const e = document.getElementById(i); if (!e) return null; const r = e.getBoundingClientRect(); return [r.left, r.top, r.width, r.height].map(v => Math.round(v * 10) / 10); })"
        HIT5 = "() => ['planBtn', 'kiseBtn', 'oshiFab', 'tcFab', 'figFab'].map(i => { const e = document.getElementById(i); if (!e) return null; const q = e.querySelector('img, .plt, .kft, .fabi') || e, r = q.getBoundingClientRect(), t = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2); return !!t && (t === e || e.contains(t)); })"
        pg.evaluate("() => window.scrollTo(0, 0)"); pg.wait_for_timeout(400); p0 = pg.evaluate(POS5); h0 = pg.evaluate(HIT5)
        maxY = pg.evaluate("() => document.documentElement.scrollHeight - window.innerHeight"); seen = []
        for y in (40, 180, maxY // 2, maxY):
            pg.evaluate("(y) => window.scrollTo(0, y)", y); pg.wait_for_timeout(350); seen.append((pg.evaluate("() => Math.round(window.scrollY)"), pg.evaluate(POS5), pg.evaluate(HIT5)))
        shot(pg, 'dock_scrolled')
        pg.evaluate("() => window.scrollTo(0, 0)"); pg.wait_for_timeout(350); swipe(cdp, pg, 120, 620, 260); pf = (pg.evaluate("() => Math.round(window.scrollY)"), pg.evaluate(POS5))      # 指で なぞって 送る
        lay = pg.evaluate("""() => { const z = e => e ? +getComputedStyle(e).zIndex : null, f = e => e ? getComputedStyle(e).position : null, I = i => document.getElementById(i), hd = document.querySelector('header.top').getBoundingClientRect(), tb = document.querySelector('.tabbar').getBoundingClientRect();
          return { pos: [f(I('planBtn')), f(I('kiseBtn')), f(I('fabCol'))], z: [z(I('planBtn')), z(I('kiseBtn')), z(I('fabCol')), z(document.querySelector('header.top')), z(document.querySelector('.tabbar'))], body: [I('planBtn').parentNode === document.body, I('kiseBtn').parentNode === document.body],
            hd: hd.bottom, tb: tb.top }; }""")
        pg.evaluate("() => window.scrollTo(0, 0)"); pg.wait_for_timeout(350); p1 = pg.evaluate(POS5)
        need = [p0[0], p0[1], p0[3]]
        check(maxY > 200 and all(q is not None for q in need) and all(sc[1] == p0 for sc in seen) and seen[-1][0] >= maxY - 2 and seen[1][0] == 180 and pf[0] > 100 and pf[1] == p0 and p1 == p0,
              f'ページを 40・180・{maxY // 2}・{maxY}（いちばん 下）まで 送っても、指で なぞって 送っても（{pf[0]}）、5つとも 画面の 同じ 所（1つも 動かない）{[q and q[:2] for q in p0]}')
        check(all(v for v in h0 if v is not None) and all(all(v for v in sc[2] if v is not None) for sc in seen) and lay['pos'] == ['fixed', 'fixed', 'fixed'] and lay['body'] == [True, True]
              and lay['z'][0] == 28 and lay['z'][1] == 28 and lay['z'][2] == 29 and lay['z'][3] < 28 and lay['z'][4] > 29 and p0[0][1] > lay['hd'] - 0.5 and all(q is None or q[1] + q[3] <= lay['tb'] + 0.5 for q in p0),
              f'どこまで 送っても 5つとも 押せる（上に 何も かぶらない）・画面に 止める（position:fixed）・重なりは 上の 帯（{lay["z"][3]}）より 上／下の タブ（{lay["z"][4]}）より 下・上の 帯と 下の タブの 間に おさまる')
        if WALL:
            print('■ どの 壁紙でも')
            ids = pg.evaluate("() => TengelKisekae.list().map(t => t.id || t)"); bad = []; worst = dict(above=99, h2=999, kh2=999, chip=99, lw=0, bottom=0); fonts = set(); modes = {}
            for tid in ids:
                pg.evaluate("(id) => TengelKisekae.apply(id, false)", tid)
                try: pg.wait_for_function("(id) => TengelKisekae.current() === id && TengelKisekae.loaded()", arg=tid, timeout=8000)
                except Exception: bad.append((tid, '読めない')); continue
                pg.wait_for_timeout(1400)          # 壁紙を かえた あとの 置き直し（すぐ・0.3秒・1.2秒）が おわる まで
                qq = pg.evaluate(GEO); ok, d = geo_ok(qq); kok, kd = kise_ok(qq)
                if not ok: bad.append((tid, d))
                elif not kok or kd['hits'] or [qq['kfont'][2], qq['kfont'][3]] != qq['night']: bad.append((tid, kd))
                else:
                    worst = dict(above=min(worst['above'], d['above']), h2=min(worst['h2'], d['h2']), kh2=min(worst['kh2'], kd['h2']), chip=min(worst['chip'], kd['chip'] if kd['chip'] is not None else 99), lw=max(worst['lw'], kd['lw']), bottom=max(worst['bottom'], kd['bottom']))
                    fonts.add(qq['kfont'][0]); m = '行 ぜんぶの 右を あける' if kd['pad'] else 'すきまの 部品' if kd['sp'] else 'そのまま'; modes[m] = modes.get(m, 0) + 1
            check(not bad and len(ids) >= 25, f'{len(ids)}この 壁紙 ぜんぶで 札は 右上の かど・見出しの 字と 壁紙の 上の絵に 重ならない（いちばん せまい 所：上の絵から {worst["above"]}・見出しの 字から {worst["h2"]}）{bad[:4]}')
            check(not bad and worst['lw'] <= KBOX + 0.5 and len(fonts) >= 8, f'{len(ids)}この 壁紙 ぜんぶで「壁紙&ボード着せ替え」の ボタンは 札の すぐ 下・データの チップに かからない（いちばん 近い 所 {worst["chip"]}・見出しの 字から {worst["kh2"]}）・'
                  f'名前の 札は ボタンの 幅に おさまる（いちばん 広い {worst["lw"]}）・字は その 壁紙の 本文の 字（{len(fonts)}種）・色は 上の 帯と 同じ・データの 行の 折り返し {modes}')
            pg.evaluate("(id) => TengelKisekae.apply(id, false)", 'default'); pg.wait_for_timeout(1500)
        q0 = pg.evaluate(GEO)
        check(geo_ok(q0)[0] and kise_ok(q0)[0] and q0['kfont'][0] == 'BIZ UDPGothic', 'いつもの 壁紙に もどすと 札も ボタンも もとどおり')
        print('■ データの 行を 作り直した とき・長く なった とき')
        pg.evaluate("() => { const sj = document.getElementById('slotJudge'), t = document.createElement('div'); t.innerHTML = sj.innerHTML; t.querySelectorAll('.kisesp').forEach(e => e.remove()); sj.innerHTML = t.innerHTML; }")      # アプリが 中身を 入れかえる のと 同じ（すきまの 部品は なくなる）
        gone = pg.evaluate("() => document.querySelectorAll('#slotJudge .kisesp').length"); pg.wait_for_timeout(300)
        qr = pg.evaluate(GEO); kok, kd = kise_ok(qr)
        check(kok and kd['sp'] == 1 and kd['rows'] == 3 and qr['chips'] == q0['chips'] and qr['kise'] == q0['kise'], f'データの 行を 作り直す → すぐ はさみ直して もとの 並び（部品 {kd["sp"]}こ・{kd["rows"]}行・チップの 場所は 同じ）')
        ticks = pg.evaluate("() => new Promise(done => { let n = 0; const mo = new MutationObserver(() => { n++; }); mo.observe(document.getElementById('slotJudge'), { childList: true, subtree: true, attributes: true }); setTimeout(() => { mo.disconnect(); done(n); }, 700); })")
        check(ticks == 0, f'置いた あとは データの 行を さわり続けない（0.7秒の 間の 書きかえ {ticks}回）')
        pg.evaluate("() => { const s = document.querySelectorAll('#slotJudge .slotchip span')[0]; s.dataset.was = s.textContent; s.textContent = '1234走'; }"); pg.wait_for_timeout(400)
        qw = pg.evaluate(GEO); wok, wd = geo_ok(qw); kok, kd = kise_ok(qw)
        check(wok and kok and kd['hits'] == 0 and kd['sp'] == 1 and qw['btn'] == q0['btn'] and qw['kise'] == q0['kise'], f'チップが 長く なっても（走数が 入った）ボタンに かからない（{kd["rows"]}行・札と ボタンは 動かない）')
        pg.evaluate("() => { const s = document.querySelectorAll('#slotJudge .slotchip span')[0]; s.textContent = s.dataset.was; }"); pg.wait_for_timeout(400)
        # 2行めも ボタンの 高さに かかる とき（見出しが ない）：行 ぜんぶの 右を あける
        pg.evaluate("() => { document.querySelector('#v-judge .card h2').style.display = 'none'; }"); pg.wait_for_timeout(500)
        qh = pg.evaluate("""() => { const k = document.getElementById('kiseBtn').getBoundingClientRect(), sj = document.getElementById('slotJudge');
          const cs = Array.from(sj.querySelectorAll('.slotchip')).map(e => e.getBoundingClientRect()); const hit = cs.filter(r => r.right > k.left - 3.4 && r.left < k.right && r.bottom > k.top - 1 && r.top < k.bottom + 1).length;
          return { pad: sj.style.paddingRight, sp: sj.querySelectorAll('.kisesp').length, hit: hit, rows: new Set(cs.map(r => Math.round(r.top))).size, over: cs.filter(r => r.bottom > k.top && r.top < k.bottom).length }; }""")
        check(qh['pad'] not in ('', '0px') and qh['sp'] == 0 and qh['hit'] == 0 and qh['over'] >= 2, f'見出しが ない とき（2行めも ボタンの 高さ）：行 ぜんぶの 右を あける（{qh["pad"]}）→ ボタンと 同じ 高さの チップ {qh["over"]}こ とも かからない（{qh["rows"]}行）')
        shot(pg, 'kise_pad')
        pg.evaluate("() => { document.querySelector('#v-judge .card h2').style.display = ''; }"); pg.wait_for_timeout(500)
        qb = pg.evaluate(GEO); kok, kd = kise_ok(qb)
        check(kok and kd['pad'] == '' and kd['sp'] == 1 and kd['rows'] == 3 and qb['kise'] == q0['kise'] and qb['chips'] == q0['chips'], f'もとに もどすと ボタンも データの 行も もとどおり（すきまの 部品 {kd["sp"]}こ・{kd["rows"]}行）')
        print('■「壁紙&ボード着せ替え」の ボタンを 指で 押す → 設定タブの「着せ替え」→「結果ボードカスタムへ↓」')
        pg.evaluate("() => window.scrollTo(0, 0)"); pg.wait_for_timeout(300)
        tap_btn(pg, '#kiseBtn'); pg.wait_for_timeout(900)
        g1 = pg.evaluate(SEC, 'setKisekae')
        check(g1['tab'] == 'set' and g1['gap'] is not None and abs(g1['gap'] - 8) <= 2 and g1['head'] == '着せ替え' and g1['next'] == 'setBoard',
              f'設定タブへ 移って「{g1["head"]}」が 上の 帯の すぐ 下（すきま {g1["gap"] and round(g1["gap"], 1)}）・すぐ 下の 欄は 結果ボードカスタム（#{g1["next"]}）')
        jok = bool(g1['jump']) and g1['jtxt'] == '結果ボードカスタムへ↓' and g1['jhit'] and g1['jpar'] and g1['jump'][0] - g1['h2'][2] >= 8 and g1['jump'][2] <= g1['card'][2] - 6 and g1['jump'][1] >= g1['card'][1] + 4 and g1['jump'][3] - g1['jump'][1] >= 28
        check(jok, f'「着せ替え」の カードの 右上に「{g1["jtxt"]}」の 札（見出しの 字から {g1["jump"] and round(g1["jump"][0] - g1["h2"][2], 1)}・高さ {g1["jump"] and round(g1["jump"][3] - g1["jump"][1], 1)}・押せる）')
        shot(pg, 'kise_go')
        tap_btn(pg, '#kiseJump'); pg.wait_for_timeout(500)
        g2 = pg.evaluate(SEC, 'setBoard')
        check(g2['tab'] == 'set' and g2['gap'] is not None and abs(g2['gap'] - 8) <= 2 and g2['head'] == '結果ボードカスタム' and g2['sy'] > g1['sy'] + 300, f'札を 押すと「{g2["head"]}」が 上の 帯の すぐ 下（すきま {g2["gap"] and round(g2["gap"], 1)}・{round(g1["sy"])} → {round(g2["sy"])}）')
        shot(pg, 'kise_board')
        check(pg.evaluate("() => document.querySelectorAll('#kiseJump').length === 1 && document.querySelectorAll('#kiseBtn').length === 1"), '札も ボタンも 1つずつ（何度 開いても ふえない）')
        pg.locator('.tabbar button[data-tab="judge"]').click(); pg.wait_for_timeout(500)
        qq = pg.evaluate(GEO); kok, kd = kise_ok(qq)
        check(geo_ok(qq)[0] and kok and qq['kise'] == q0['kise'] and qq['chips'] == q0['chips'], '判定タブに もどると 札と ボタンと データの 行は もとの 場所')
        # 名前の 札を 押しても 同じ（ボタンの 一部）
        r = pg.evaluate("() => { window.scrollTo(0, 0); const r = document.querySelector('#kiseBtn .kisel').getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }"); pg.wait_for_timeout(200); pg.touchscreen.tap(*r); pg.wait_for_timeout(900)
        g1b = pg.evaluate(SEC, 'setKisekae')
        check(g1b['tab'] == 'set' and g1b['gap'] is not None and abs(g1b['gap'] - 8) <= 2, f'名前の 札を 押しても 設定の「着せ替え」へ（すきま {g1b["gap"] and round(g1b["gap"], 1)}）')
        pg.locator('.tabbar button[data-tab="judge"]').click(); pg.wait_for_timeout(500)
        print('■ 指で 押す → 判定タブの 上に 作戦会議')
        pg.evaluate("() => window.scrollTo(0, 0)"); pg.wait_for_timeout(300)
        pg.evaluate("() => window.scrollTo(0, 10)"); pg.wait_for_timeout(200); sy0 = pg.evaluate('() => window.scrollY')      # ページを 少し 送って おく（札は 上の 帯の 下に 見えた まま）：開いても 位置が かわらない ことを 見る
        tap_btn(pg)
        pg.wait_for_function("() => window.TCPlan && TCPlan.isOpen()", timeout=30000); pg.wait_for_timeout(900)
        td = _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=9)))
        st = pg.evaluate("""() => { const e = document.getElementById('tcPlan'), h = document.getElementById('planHost'), r = e.getBoundingClientRect(), pp = e.querySelector('.pp').getBoundingClientRect();
          return { open: TCPlan.isOpen(), host: e.parentNode.id, tcOv: !!document.getElementById('tcOv'), app: typeof window.TCApp, rect: [r.left, r.top, r.width, r.height], pp: [pp.left, pp.top, pp.width, pp.height],
            z: +getComputedStyle(h).zIndex, pos: getComputedStyle(h).position, date: e.querySelector('.bdt').textContent, sub: e.querySelector('.bsub').textContent, tab: document.querySelector('.tabbar button[aria-selected="true"]').dataset.tab,
            top: (() => { const t = document.elementFromPoint(195, 815); return !!(t && e.contains(t)); })(), dis: document.getElementById('planBtn').disabled, sy: window.scrollY,
            head: (() => { const i = e.querySelector('.ph img'); return i ? i.getAttribute('src') : null; })() }; }""")
        check(st['open'] and st['host'] == 'planHost' and not st['tcOv'] and st['app'] == 'object' and 'tc_bundle.js' in reqs, f'押すと 束を 読んで 作戦会議が 開く・入れ物は #planHost・トレーニングセンターは 開かない（#tcOv なし）{dict(host=st["host"], tcOv=st["tcOv"])}')
        check(st['open'] and st['date'].startswith(f'{td.year}年{td.month}月{td.day}日') and st['sub'] == 'お気に入りレース一覧' and st['head'] == 'tc_icon_plan.webp', f'開いた まま 表示される（押した 指の クリックで 閉じない）・ボード「{st["date"]}」「{st["sub"]}」')
        check(st['rect'] == [0, 0, 390, 844] and st['pos'] == 'fixed' and st['z'] >= 90 and st['top'] and st['tab'] == 'judge' and abs(st['pp'][2] - 374) <= 1 and st['sy'] == sy0 and not st['dis'],
              f'画面 いっぱい（{st["rect"]}）・下の タブと 丸い ボタンの 上に 出る（z {st["z"]}）・うしろは 判定タブの まま・ページの 位置は そのまま（{sy0} → {st["sy"]}）')
        shot(pg, 'plan_open')
        print('■ うしろの 判定タブは 動かない')
        mv = {}
        swipe(cdp, pg, 120, 640, 260); mv['中身'] = pg.evaluate('() => window.scrollY')
        swipe(cdp, pg, 120, 40, 420); mv['見出し'] = pg.evaluate('() => window.scrollY')
        swipe(cdp, pg, 3, 700, 300); mv['まわりの 幕'] = pg.evaluate('() => window.scrollY')
        check(all(v == sy0 for v in mv.values()) and pg.evaluate('() => TCPlan.isOpen()'), f'中身（短くて スクロール しない）・見出し・まわりの 幕を 指で なぞっても うしろの ページは 動かない（{sy0} の まま）{mv}・作戦会議は 開いた まま')
        print('■ 予約・通知（トレーニングセンターを 開かなくても 使える）')
        pg.locator('#tcPlan [data-p=on]').click(); pg.wait_for_timeout(500)
        check(pg.evaluate("() => JSON.parse(localStorage.getItem('tengel.plan')).on === true && window.__notify.auth === 'authorized'"), '通知を オン（iPhone の 許可）')
        later = td + _dt.timedelta(days=1)
        pg.locator('#tcPlan [data-p=add]').click(); pg.wait_for_timeout(300)
        pg.fill('#tcPlan [data-f=name]', 'はなまる特別'); pg.fill('#tcPlan [data-f=time]', '15:40'); pg.fill('#tcPlan [data-f=date]', later.strftime('%Y-%m-%d'))
        pg.fill('#tcPlan [data-f=n]', '14'); pg.fill('#tcPlan [data-f=dist]', '1600'); pg.fill('#tcPlan [data-f=memo]', '本命は 5番')
        pg.locator('#tcPlan [data-p=save]').click(); pg.wait_for_timeout(500)
        P = pg.evaluate("() => JSON.parse(localStorage.getItem('tengel.plan'))")
        check(len(P['races']) == 1 and P['races'][0]['name'] == 'はなまる特別' and P['races'][0]['n'] == 14 and P['races'][0]['dist'] == 1600 and P['races'][0]['memo'] == '本命は 5番', f'レースを 予約（メモも）{P["races"]}')
        pg.locator('#tcPlan [data-p=nt][data-m="20"]').click(); pg.wait_for_timeout(200)
        pg.locator('#tcPlan [data-p=nt][data-m="5"]').click(); pg.wait_for_timeout(800)
        items = pg.evaluate("() => window.__notify.items.filter(i => /^plan-/.test(i.id)).map(i => [i.id.split('-').pop(), i.title, i.body])")
        check(len(items) == 2 and {i[0] for i in items} == {'20', '5'} and all('はなまる特別' in i[2] for i in items), f'20分前・5分前の 通知が 入る {items}')
        shot(pg, 'plan_race')
        # 中身が 長い とき：中身は 指で 送れる・うしろは 動かない
        pg.evaluate("""(d) => { const P = JSON.parse(localStorage.getItem('tengel.plan')); for (let i = 0; i < 7; i++) P.races.push({ id: 'x' + i, date: d, time: '1' + i + ':00', name: 'ならび' + i, n: 12, dist: 1200, venue: '', r: '', memo: '', notify: [] }); localStorage.setItem('tengel.plan', JSON.stringify(P)); }""", later.strftime('%Y-%m-%d'))
        pg.locator('#tcPlan [data-p=close]').click(); pg.wait_for_timeout(300)
        c1 = pg.evaluate("() => { const t = document.elementFromPoint(195, 420), h = document.getElementById('planHost'); return { open: TCPlan.isOpen(), through: !!t && !h.contains(t) && t !== h, hostPE: getComputedStyle(h).pointerEvents, tab: document.querySelector('.tabbar button[aria-selected=\"true\"]').dataset.tab, sy: window.scrollY, dis: document.getElementById('planBtn').disabled }; }")
        check(not c1['open'] and c1['through'] and c1['hostPE'] == 'none' and c1['tab'] == 'judge' and c1['sy'] == sy0 and not c1['dis'], f'「とじる」→ 判定タブに もどる（入れ物は 指を 通す・ページの 位置は そのまま）{c1}')
        swipe(cdp, pg, 120, 640, 400); s1 = pg.evaluate('() => window.scrollY')
        check(s1 > sy0, f'閉じた あとは 判定タブを ふつうに 送れる（{sy0} → {s1}）')
        pg.evaluate("(y) => window.scrollTo(0, y)", sy0); pg.wait_for_timeout(200)
        tap_btn(pg); pg.wait_for_function("() => TCPlan.isOpen()", timeout=10000); pg.wait_for_timeout(700)
        n8 = pg.evaluate("() => { const pb = document.querySelector('#tcPlan .pb'); return [document.querySelectorAll('#tcPlan .rc').length, pb.scrollHeight > pb.clientHeight + 50, pb.scrollTop]; }")
        swipe(cdp, pg, 120, 640, 300)
        n9 = pg.evaluate("() => [document.querySelector('#tcPlan .pb').scrollTop, window.scrollY]")
        for _ in range(6): swipe(cdp, pg, 120, 640, 200)       # いちばん 下まで 送って、さらに なぞる
        n10 = pg.evaluate("() => { const pb = document.querySelector('#tcPlan .pb'); return [Math.round(pb.scrollTop), pb.scrollHeight - pb.clientHeight, window.scrollY]; }")
        check(n8[0] == 8 and n8[1] and n9[0] > 50 and n9[1] == sy0 and abs(n10[0] - n10[1]) <= 2 and n10[2] == sy0,
              f'もう一度 開く（レース {n8[0]}こ：中身が 長い）→ 中身は 指で 送れる（{n8[2]} → {n9[0]:.0f}）・いちばん 下で さらに なぞっても うしろは 動かない（{sy0} の まま）')
        # まわりの 幕を 押すと 閉じる
        pg.touchscreen.tap(3, 420); pg.wait_for_timeout(400)
        check(not pg.evaluate('() => TCPlan.isOpen()'), 'まわりの 幕を 押すと 閉じる')
        if HAVE:
            print('■ トレーニングセンターの 中の 作戦会議と 行ったり 来たり')
            pg.locator('#tcFab .fabi').click()
            pg.wait_for_function("() => window.TCApp && document.querySelector('#tcOv.on') && !document.querySelector('#tcOv .tcld')", timeout=120000); pg.wait_for_timeout(1200)
            pg.locator('#tcOv .tcpl').click(); pg.wait_for_timeout(700)
            t1 = pg.evaluate("() => { const e = document.getElementById('tcPlan'); return { open: TCPlan.isOpen(), host: e.parentNode.id, n: e.querySelectorAll('.rc').length, one: document.querySelectorAll('#tcPlan').length, first: (e.querySelector('.rc .nm') || {}).textContent }; }")
            check(t1['open'] and t1['host'] == 'tcOv' and t1['n'] == 8 and t1['one'] == 1, f'トレーニングセンターの 作戦会議の 札 → 同じ 作戦会議が トレーニングセンターの 中に 開く（入れ物 #{t1["host"]}・レース {t1["n"]}こ・作戦会議は 1つ だけ）')
            pg.locator('#tcPlan [data-p=close]').click(); pg.wait_for_timeout(300)
            pg.locator('#tcOv [data-tc=back]').click(); pg.wait_for_timeout(600)
            tap_btn(pg); pg.wait_for_function("() => TCPlan.isOpen()", timeout=10000); pg.wait_for_timeout(600)
            t2 = pg.evaluate("() => { const e = document.getElementById('tcPlan'); return { open: TCPlan.isOpen(), host: e.parentNode.id, n: e.querySelectorAll('.rc').length, tc: !!document.querySelector('#tcOv.on'), names: Array.from(e.querySelectorAll('.rc .nm')).map(x => x.textContent).includes('はなまる特別') }; }")
            check(t2['open'] and t2['host'] == 'planHost' and t2['n'] == 8 and not t2['tc'] and t2['names'], f'トレーニングセンターを 閉じて、また 判定タブの 札 → 判定タブの 上に 開く（入れ物 #{t2["host"]}・予約した レースも ある）')
            pg.locator('#tcPlan [data-p=close]').click(); pg.wait_for_timeout(300)
        check(not errs, f'エラー なし {errs[:3]}')
        if HAVE:
            print('■ 絵が 読めない とき')
            pg2 = ctx.new_page(); e2 = []; pg2.on('pageerror', lambda e: e2.append(str(e)))
            pg2.route('**/tc_icon_plan.webp', lambda r: r.abort()); pg2.route('**/tc_icon_kise2.webp', lambda r: r.abort())
            pg2.goto(APP); pg2.wait_for_timeout(1500); gate(pg2); pg2.wait_for_timeout(800)
            q2 = pg2.evaluate(GEO); ok2, d2 = geo_ok(q2); k2ok, k2d = kise_ok(q2)
            check(k2ok and q2['kimg'] is None and q2['kft'] and q2['kname'] == KNAME, f'絵が 読めない → 色の カプセル ＋ 名前の 札「{q2["kname"]}」（同じ 場所・同じ 大きさ {k2d["cap"] if isinstance(k2d, dict) else k2d}）')
            check(ok2 and q2['img'] is None and q2['txt'] and q2['txt'][0] == '作戦会議' and abs((q2['txt'][3] - q2['txt'][1]) - 110) <= 1 and abs((q2['txt'][4] - q2['txt'][2]) - 33) <= 1, f'絵が 読めない → 字の 札「作戦会議」（110×33・同じ 場所）{d2}')
            tap_btn(pg2); pg2.wait_for_function("() => window.TCPlan && TCPlan.isOpen()", timeout=30000)
            check(pg2.evaluate("() => document.getElementById('tcPlan').parentNode.id === 'planHost'") and not e2, f'字の 札でも 開く・エラー なし {e2[:3]}')
            pg2.locator('#tcPlan [data-p=close]').click(); pg2.wait_for_timeout(300)
            tap_btn(pg2, '#kiseBtn'); pg2.wait_for_timeout(900); g3 = pg2.evaluate(SEC, 'setKisekae')
            check(g3['tab'] == 'set' and g3['gap'] is not None and abs(g3['gap'] - 8) <= 2 and not e2, f'色の カプセルでも 設定の「着せ替え」へ 移る（すきま {g3["gap"] and round(g3["gap"], 1)}）・エラー なし {e2[:3]}')
            pg2.close()
        print('■ 幅の せまい 画面（375）')
        c3 = b.new_context(viewport={'width': 375, 'height': 667}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo', has_touch=True, is_mobile=True); c3.add_init_script(FAKE)
        p3 = c3.new_page(); e4 = []; p3.on('pageerror', lambda e: e4.append(str(e)))
        p3.goto(APP); p3.wait_for_timeout(1500); gate(p3); p3.wait_for_timeout(800)
        p3.evaluate("() => { const t = document.getElementById('toast'); if (t) t.hidden = true; }")
        q4 = p3.evaluate(GEO); ok4, d4 = geo_ok(q4); k4ok, k4d = kise_ok(q4)
        check(ok4 and k4ok and not e4, f'幅 375：札は 右上の かど（上へ {d4["up"]}・右へ {d4["over"]}・画面の 右はしから {d4["edge"]}）・ボタンは その すぐ 下（カプセル {k4d["cap"] if isinstance(k4d, dict) else k4d}・チップから {k4d["chip"] if isinstance(k4d, dict) else "-"}・データの 行 {k4d["rows"] if isinstance(k4d, dict) else "-"}行）・エラー なし {e4[:3]}')
        if SHOT: os.makedirs(SHOT, exist_ok=True); p3.screenshot(path=os.path.join(SHOT, 'kise_375.png'))
        c3.close()
        print('■ Web版')
        pw = ctx.new_page(); e3 = []; pw.on('pageerror', lambda e: e3.append(str(e)))
        pw.goto(WEB); pw.wait_for_timeout(1500); gate(pw); pw.wait_for_timeout(500)
        check(pw.evaluate("() => !document.getElementById('planBtn') && !document.getElementById('planCss') && typeof window.TCPlanOpen === 'undefined' && !!document.querySelector('#v-judge .card h2')") and not e3, f'Web版：判定タブに 札は ない（かわらない）・エラー なし {e3[:3]}')
        pw.locator('.tabbar button[data-tab="set"]').click(); pw.wait_for_timeout(400)
        check(pw.evaluate("() => !document.getElementById('kiseBtn') && !document.getElementById('kiseJump') && typeof window.KiseGo === 'undefined' && document.getElementById('slotJudge').style.paddingRight === '' && !document.querySelector('.kisesp')") and not e3,
              f'Web版：「壁紙&ボード着せ替え」の ボタンも「結果ボードカスタムへ↓」の 札も すきまの 部品も ない（かわらない）・エラー なし {e3[:3]}')
        b.close()
finally:
    srv.terminate()
print('NG' if fails else 'OK', len(fails), fails)
sys.exit(1 if fails else 0)
