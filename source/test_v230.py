# 第4.230版の テスト（まさちゃん 2026/11/26 22:46・23:16・23:21）：ボタンの 並び
#   22:46「アイコンの並びなんだけど、紫四角の中のアイコンを、青四角のところに配置して、赤四角のアイコンを黄四角の位置に大きさいい感じに調整して入れられない？」
#   23:16「大きさもう少し隙間なく入るようにして！後、白の背景いらないよ！前と同じでくり抜いてる感じでいい！推し馬の文字だけ小さく見えるから周りと合わせて！」
#   23:21「あと作戦会議と、着せ替えは、判定のところ以外、単勝5連勝、記録、実測・回収、設定のところでも表示されるようにして！」
#   ■ 丸い ボタン 4つ（トレーニングセンター・推し馬・TENGERカードバトル・思い出フィギュア）：下の タブの すぐ 上に 横 1列
#     ① 左から 同じ 順・画面の 幅を 4つで 等分（480px まで）・丸は 1つ ぶんの 幅の 80%（44〜80px）・上が そろう・下の タブから 3〜5px
#     ② うしろの 地は なし（中身の 上に うかぶ：丸の あいだを 押すと うしろの 中身に 届く）
#     ③ 名前の 札は 4つとも 同じ 大きさ・1行の「推し馬」は 字を 大きく して 札の まん中
#     ④ 判定の 帯（判定へ）・お知らせ・買い目の 保存の 帯は 列の 上。ページの いちばん 下で 最後の 中身は 判定の 帯の 上まで 上がる
#     ⑤ 画面の 幅が かわると 丸の 大きさも かわる・ページを 動かしても 同じ 所
#   23:23「あと、アイコンの位置について結果待ちの下に作戦会議、ミッションの下に着せ替えボードのアイコン入れて！テンゲルデータは、テンゲルⅢの文字の下に入れて！全体的に大きさなど違和感なく揃えて！」
#   23:25「あと、解放前の鍵マークアイコンから離れ過ぎてるから、ちゃんとアイコンに乗せて！」
#   ■ 上の 帯：1段目＝ロゴ・ポイント・説明書／2段目＝テンゲルデータの 札（ロゴの 下）・結果待ち・ミッション／3段目＝作戦会議（結果待ちの 下）・壁紙&ボード着せ替え（ミッションの 下）
#     ⑥ 大きさは 結果待ち・ミッションの 幅に 合わせる・帯の ほかの もの に 重ならない・帯の 中・押せる
#     ⑦ 5つの タブ どれでも 出る（同じ 場所）・ほかの タブで 押しても 作戦会議が 開く・着せ替えへ 行ける
#     ⑧ 壁紙を かえる（ロゴが 大きい 壁紙）→ 置き直す
#   ■ ⑩ カードバトルの 鍵（解放 前）は 丸の 右上に 乗せる
#     ⑨ 広い 画面（上の 帯が 1段）→ 前の 場所（レース情報の カードの 右上：判定タブ だけ）
#   python3 test_v230.py   （SHOT=フォルダ で 画面を 写す）
import json, os, re, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv_v230'); PORT = 8851; APP = f'http://localhost:{PORT}/APP/'
SHOT = os.environ.get('SHOT')
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL,
               env=dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, HIST='hist_280.json', DROP='', TARGET='app'))
from assets_dir import adir
pth = os.path.join(SRV, 'APP', 'index.html'); html = open(pth, encoding='utf8').read()
assert "window.__NATIVE = location.protocol === 'tengel:';" in html
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
A = os.path.join(SRV, 'APP')
for d in ('tc_assets', 'fig_assets'):
    try: a = adir(d)
    except Exception: a = None
    if a and os.path.isdir(a):
        for f in os.listdir(a):
            if f.endswith('.webp') and not os.path.exists(os.path.join(A, f)): shutil.copy(os.path.join(a, f), os.path.join(A, f))
for f in ('cb_icon.webp',):
    a = os.path.join(W, 'ios', 'cb_assets', f)
    if os.path.exists(a): shutil.copy(a, os.path.join(A, f))
BL = os.environ.get('KISEKAE_ASSETS') or os.path.join(W, 'ios', 'kisekae_blobs'); WALL = os.path.isdir(BL) and len(os.listdir(BL)) > 50
if WALL:
    for f in os.listdir(BL): shutil.copy(os.path.join(BL, f), os.path.join(A, 'ks_' + f))
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
FAKE = open(os.path.join(W, 'test_tc.py'), encoding='utf8').read().split('FAKE = """')[1].split('"""')[0]      # アプリの 窓口の にせもの（test_tc.py と 同じ）
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c: fails.append(label)


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


def fdx(w):            # 丸の 大きさ（tc/tc_launch.js の fabFit：1つ ぶんの 幅の 80%・44〜80px・列の 幅は 480px まで）
    return max(44, min(80, int((min(w, 480) - 8) / 4 * 0.8)))


def lfx(d):            # 名前の 字の 大きさ（--lf：丸の 14.5%・8〜11.5px）
    return max(8, min(11.5, d * 0.145))


# 丸い ボタンの 列（#fabCol）・名前の 札・判定の 帯・下の タブ・main の 下の 余白
ROW = """() => { const R = e => { const r = e.getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom].map(v => Math.round(v * 10) / 10); };
  const col = document.getElementById('fabCol'), ks = [...col.children].sort((a, b) => getComputedStyle(a).order - getComputedStyle(b).order), tb = document.querySelector('.tabbar'), mb = document.getElementById('minibar');
  const tbOn = getComputedStyle(tb).display !== 'none', bf = getComputedStyle(col, '::before');
  return { ids: ks.map(b => b.id), btn: ks.map(R), ico: ks.map(b => R(b.querySelector('.fabi'))), lab: ks.map(b => R(b.querySelector('.fabl'))), l1: ks.map(b => b.querySelector('.fabl').classList.contains('l1')),
    lfs: ks.map(b => parseFloat(getComputedStyle(b.querySelector('.fabl')).fontSize)), names: ks.map(b => b.querySelector('.fabl').textContent), col: R(col), rw: col.classList.contains('rw'), g2: col.classList.contains('g2'),
    fd: parseFloat(getComputedStyle(col).getPropertyValue('--fd')), before: bf.content, tab: tbOn ? R(tb)[1] : null, vw: innerWidth, cw: document.documentElement.clientWidth, vh: innerHeight,
    mini: mb && !mb.hidden ? R(mb) : null, miniBtn: mb && !mb.hidden ? R(mb.querySelector('button')) : null, miniOver: mb && !mb.hidden ? (z => z ? z.scrollWidth - z.clientWidth : 0)(mb.querySelector('.mz')) : null,
    fabt: getComputedStyle(document.documentElement).getPropertyValue('--fabt').trim(), pb: parseFloat(getComputedStyle(document.querySelector('main')).paddingBottom),
    marks: [...col.querySelectorAll('.fabc, .fabb')].filter(e => !e.hidden && e.getClientRects().length).map(R) }; }"""
# 作戦会議の 札・着せ替えの ボタン・上の 帯の 中の もの
DOCK = """() => { const R = e => { const r = e.getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom].map(v => Math.round(v * 10) / 10); };
  const hd = document.querySelector('header.top'), ti = hd.querySelector('.top-in'), brand = ti.querySelector('.brand'), b = document.getElementById('planBtn'), k = document.getElementById('kiseBtn');
  if (!b || !k) return null; const vis = e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
  const ink = b.querySelector('img, .plt'), kc = k.querySelector('img, .kft'), kl = k.querySelector('.kisel');
  const at = (e, own) => { const q = e.getBoundingClientRect(), t = document.elementFromPoint(q.left + q.width / 2, q.top + q.height / 2); return !!t && (t === own || own.contains(t)); };
  return { dk: [b.classList.contains('dk'), k.classList.contains('dk')], par: [b.parentNode === hd, k.parentNode === hd], pos: [getComputedStyle(b).position, getComputedStyle(k).position],
    sc: [parseFloat(b.style.getPropertyValue('--dk')), parseFloat(k.style.getPropertyValue('--dk'))], vis: [vis(b), vis(k)], btn: vis(b) ? R(b) : null, kise: vis(k) ? [R(kc), R(kl)] : null,
    hit: vis(b) && vis(k) ? [at(ink, b), at(kc, k), at(kl, k)] : null, hd: R(hd), brand: R(brand),
    kids: [...ti.children].filter(e => e !== brand && vis(e)).map(e => [e.id || e.className, R(e)]), sy: Math.round(scrollY),
    tab: (document.querySelector('.tabbar button[aria-selected="true"]') || {}).dataset ? document.querySelector('.tabbar button[aria-selected="true"]').dataset.tab : null }; }"""
PW, PH, INK = 118, 47, (16 / 500, 30 / 200, 483 / 500, 170 / 200)      # tc/tc_launch.js と 同じ
KW, KH, KUNDER = 100, 36, 3


def lap(a, r, mx=0, my=0):
    return r[2] > a[0] - mx and r[0] < a[2] + mx and r[3] > a[1] - my and r[1] < a[3] + my


def row_ok(q):
    """① 並び・大きさ ③ 名前の 札：(ok, くわしく)"""
    b, ic, lb = q['btn'], q['ico'], q['lab']; d = fdx(q['cw'])
    slot = (min(q['cw'], 480) - 8) / 4
    det = dict(fd=q['fd'], want=d, low=round(q['tab'] - max(x[3] for x in b), 1) if q['tab'] is not None else None, lab=lb[0][2] - lb[0][0] if lb else None)
    ok = (q['ids'] == ['tcFab', 'oshiFab', 'cbFab', 'figFab'] and q['rw'] and not q['g2'] and q['fd'] == d
          and all(abs((x[2] - x[0]) - slot) <= 0.6 for x in b) and all(abs(b[i][2] - b[i + 1][0]) <= 0.6 for i in range(3)) and all(abs(x[1] - b[0][1]) <= 0.6 for x in b)
          and all(abs((x[2] - x[0]) - d) <= 0.6 and abs((x[3] - x[1]) - d) <= 0.6 for x in ic) and all(abs((ic[i][0] + ic[i][2]) / 2 - (b[i][0] + b[i][2]) / 2) <= 0.6 for i in range(4))
          and len({(round(x[2] - x[0], 1), round(x[3] - x[1], 1)) for x in lb}) == 1 and q['l1'] == [False, True, False, False]
          and all(abs(f - lfx(d)) <= 0.05 for i, f in enumerate(q['lfs']) if i != 1) and abs(q['lfs'][1] - lfx(d) * 1.25) <= 0.06
          and not any(lap(lb[i], lb[i + 1], -0.5, -0.5) for i in range(3)) and min(x[0] for x in b) >= 0 and max(x[2] for x in b) <= q['vw'] and q['before'] in ('none', 'normal'))
    if q['tab'] is not None: ok = ok and 3 <= det['low'] <= 5
    return bool(ok), det


def dock_ok(q):
    """⑥ 上の 帯の 3段目：作戦会議は 結果待ちの 下・着せ替えは ミッションの 下（まん中を そろえる・大きさ k＝ min(1, 結果待ち・ミッションの 幅 ÷ 110)）・
       テンゲルデータの 札は ロゴの 下（左と 幅を ロゴに そろえる・2段目の 高さの まん中）・ほかの ものに 重ならない・帯の 中・押せる：(ok, くわしく)"""
    if not q or not q['btn'] or not q['kise']: return False, 'ない'
    kd = dict(q['kids']); rv, ms, dp = kd.get('rsvBtn'), kd.get('msBtn'), kd.get('dbpill')
    if not rv or not ms or not dp: return False, f'結果待ち {rv}・ミッション {ms}・データの 札 {dp}'
    k = q['sc'][0]; l, t = q['btn'][0], q['btn'][1]
    p = [l + PW * k * INK[0], t + PH * k * INK[1], l + PW * k * INK[2], t + PH * k * INK[3]]
    c, kl = q['kise']; box = [min(c[0], kl[0]), c[1], max(c[2], kl[2]), max(c[3], kl[3])]
    hits = [n for n, r in q['kids'] if lap(p, r, 4, 2) or lap(box, r, 4, 2)]
    kw = int(min(1, (rv[2] - rv[0]) / 110, (ms[2] - ms[0]) / 110) * 100) / 100
    r2t, r2b = min(rv[1], ms[1]), max(rv[3], ms[3]); dh = dp[3] - dp[1]
    det = dict(k=k, want=kw, pmid=round((p[0] + p[2]) / 2 - (rv[0] + rv[2]) / 2, 1), kmid=round((box[0] + box[2]) / 2 - (ms[0] + ms[2]) / 2, 1), cy=round((c[1] + c[3]) / 2 - (p[1] + p[3]) / 2, 1),
               under=round(c[1] - r2b, 1), hdr=round(q['hd'][3] - max(box[3], p[3]), 1), hits=hits,
               db=[round(dp[0] - q['brand'][0], 1), round(dp[2] - (rv[0] - 8), 1), round((dp[1] + dp[3]) / 2 - (r2t + r2b) / 2, 1), round(dh, 1)])
    ok = (q['dk'] == [True, True] and q['par'] == [True, True] and q['pos'] == ['absolute', 'absolute'] and q['sc'][0] == q['sc'][1] and abs(k - kw) <= 0.011 and 0.6 <= k <= 1
          and abs((c[2] - c[0]) - KW * k) <= 0.6 and abs((c[3] - c[1]) - KH * k) <= 0.6 and abs(det['pmid']) <= 1 and abs(det['kmid']) <= 1 and abs(det['cy']) <= 1 and abs(det['under'] - 8) <= 1
          and det['hdr'] >= 2 and not hits and not lap(box, q['brand']) and not lap(p, q['brand']) and q['hit'] == [True, True, True]
          and abs(det['db'][0]) <= 1 and abs(det['db'][1]) <= 1 and (abs(det['db'][2]) <= 1 or dh > r2b - r2t + 2) and dp[1] >= q['brand'][3] + 2)
    return bool(ok), det

try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 402, 'height': 874}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo', has_touch=True, is_mobile=True)
        ctx.add_init_script(FAKE)
        pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        pg.goto(APP); pg.wait_for_function("() => window.TengelFab && document.querySelector('#cbFab') && document.querySelector('#figFab') && document.getElementById('kiseBtn')", timeout=60000)
        pg.wait_for_timeout(800); gate(pg); pg.wait_for_timeout(600)
        pg.evaluate("() => { const o = document.querySelector('#lgOv [data-lg=ok]'); if (o) o.click(); const t = document.getElementById('toast'); if (t) t.hidden = true; }")
        pg.wait_for_function("() => !TengelFab.busy()", timeout=8000); pg.wait_for_timeout(500)

        print('■ 丸い ボタン：下の タブの すぐ 上に 横 1列（①②③）')
        q = pg.evaluate(ROW); ok, d = row_ok(q)
        check(ok, f'幅 402：左から トレーニングセンター → 推し馬 → TENGERカードバトル → 思い出フィギュア・4つで 等分・丸 {d["fd"]}px（1つ ぶんの 幅の 80%）・下の タブから {d["low"]}px・'
                  f'名前の 札は 4つとも 同じ 大きさ（幅 {d["lab"]}）・推し馬は 字を 大きく（{q["lfs"][1]}px・ほかは {q["lfs"][0]}px）・うしろの 地 なし（{q["before"]}）')
        shot(pg, 'v230_judge_top')
        # ② すきまを 押すと うしろの 中身に 届く・丸と 名前の 札は ボタン
        th = pg.evaluate("""() => { const col = document.getElementById('fabCol'), ks = [...col.children].sort((a, b) => getComputedStyle(a).order - getComputedStyle(b).order), out = [];
          for (const k of ks) { const i = k.querySelector('.fabi').getBoundingClientRect(), l = k.querySelector('.fabl').getBoundingClientRect();
            const a = document.elementFromPoint(i.left + i.width / 2, i.top + i.height / 2), c = document.elementFromPoint(l.left + l.width / 2, l.top + l.height / 2);
            out.push([!!a && k.contains(a), !!c && k.contains(c)]); }
          const r0 = ks[0].querySelector('.fabi').getBoundingClientRect(), r1 = ks[1].querySelector('.fabi').getBoundingClientRect(), g = document.elementFromPoint((r0.right + r1.left) / 2, r0.top + r0.height / 2);
          return { own: out, gap: g ? (g.closest('#fabCol') ? 'fabCol' : g.tagName) : null }; }""")
        check(all(a and c for a, c in th['own']) and th['gap'] not in (None, 'fabCol'), f'丸と 名前の 札は 押せる（{th["own"]}）・丸と 丸の あいだを 押すと うしろの 中身に 届く（{th["gap"]}：くり抜き）')

        print('■ カードバトルの 鍵（解放 前：⑩）')
        lk = pg.evaluate("""() => { const b = document.getElementById('cbFab'), i = b.querySelector('.fabi').getBoundingClientRect(), br = b.getBoundingClientRect(), cs = getComputedStyle(b, '::before');
          if (!b.classList.contains('lock')) return null; const fs = parseFloat(cs.fontSize), right = br.right - parseFloat(cs.right), top = br.top + parseFloat(cs.top);
          return { content: cs.content, fs, right: Math.round((right - i.right) * 10) / 10, top: Math.round((top - i.top) * 10) / 10, left: Math.round((right - fs - i.left) * 10) / 10, fd: i.width }; }""")
        check(lk is not None and lk['content'] == '"🔒"' and abs(lk['right']) <= 1 and abs(lk['top']) <= 1 and lk['left'] > lk['fd'] * 0.5 and abs(lk['fs'] - max(15, lk['fd'] * 0.25)) <= 0.5,
              f'解放 前の 鍵は 丸の 右上の かどに 乗る（丸の 右はしと の ずれ {lk and lk["right"]}・上はしと の ずれ {lk and lk["top"]}・大きさ {lk and lk["fs"]}px＝丸の 25%）')
        print('■ 判定の 帯・お知らせ・買い目の 保存の 帯は 列の 上（④）')
        ok4 = q['mini'] is not None and abs(q['mini'][3] - (q['col'][1] - 6)) <= 1 and q['miniOver'] == 0 and all(m[1] >= q['mini'][3] - 0.5 for m in q['marks'])
        check(ok4, f'判定の 帯（判定へ↓）は 列の すぐ 上（帯の 下 {q["mini"] and q["mini"][3]}・列の 上 {q["col"][1]}・--fabt {q["fabt"]}）・字は 全部 見える（はみ出し {q["miniOver"]}）・丸の 右上の 札にも かからない')
        want_pb = q['vh'] - q['col'][1] + 6 + 2 + 40 + 6
        check(abs(q['pb'] - want_pb) <= 1.5, f'main の 下の 余白 {q["pb"]}px ＝ 列の 上から 下まで ＋ 判定の 帯（{round(want_pb, 1)}）')
        pg.evaluate("() => window.scrollTo(0, 1e7)"); pg.wait_for_timeout(700)
        end = pg.evaluate("""() => { const v = [...document.querySelectorAll('main > .view')].find(x => !x.hidden), kids = [...v.children].filter(e => e.getBoundingClientRect().height > 0), m = document.getElementById('minibar'), h = m.hidden;
          m.hidden = false; const mt = m.getBoundingClientRect().top; m.hidden = h; return { last: kids[kids.length - 1].getBoundingClientRect().bottom, mt, atEnd: Math.abs(scrollY + innerHeight - document.documentElement.scrollHeight) < 2 }; }""")
        check(end['atEnd'] and end['last'] <= end['mt'] + 0.5, f'いちばん 下まで 動かすと 最後の 中身（下 {round(end["last"], 1)}）は 判定の 帯（上 {round(end["mt"], 1)}）の 上まで 上がる')
        shot(pg, 'v230_judge_bottom')
        pg.evaluate("() => window.scrollTo(0, 0)"); pg.wait_for_timeout(400)
        pg.evaluate("() => { const t = document.getElementById('toast'); t.textContent = 'テストの お知らせ'; t.hidden = false; }"); pg.wait_for_timeout(300)
        ts = pg.evaluate("() => { const t = document.getElementById('toast').getBoundingClientRect(), c = document.getElementById('fabCol').getBoundingClientRect(), m = document.getElementById('minibar'); return [t.bottom, c.top, m.hidden ? null : m.getBoundingClientRect().top]; }")
        pg.evaluate("() => { document.getElementById('toast').hidden = true; }")
        check(ts[0] <= ts[1] - 6 - 40, f'お知らせ（下 {round(ts[0], 1)}）は 列（上 {round(ts[1], 1)}）と 判定の 帯の 上')

        print('■ 上の 帯：作戦会議は 結果待ちの 下・着せ替えは ミッションの 下・テンゲルデータは ロゴの 下（⑥⑦）')
        dq = pg.evaluate(DOCK); ok, d6 = dock_ok(dq)
        check(ok, f'3段目：作戦会議（結果待ちと まん中の ずれ {d6.get("pmid") if isinstance(d6, dict) else d6}）・着せ替え（ミッションと まん中の ずれ {d6.get("kmid") if isinstance(d6, dict) else "-"}・'
                  f'2段目の 下から {d6.get("under") if isinstance(d6, dict) else "-"}）・大きさ {d6.get("k") if isinstance(d6, dict) else "-"} 倍（＝{d6.get("want") if isinstance(d6, dict) else "-"}）・'
                  f'高さの まん中の ずれ {d6.get("cy") if isinstance(d6, dict) else "-"}・帯の 下まで {d6.get("hdr") if isinstance(d6, dict) else "-"}・ほかの ものに 重ならない（{d6.get("hits") if isinstance(d6, dict) else "-"}）・押せる')
        check(ok and d6['db'][3] < 30, f'テンゲルデータの 札は ロゴの 下（左の ずれ {d6["db"][0]}・右は 結果待ちの 8px 手前（ずれ {d6["db"][1]}）・2段目と 高さの まん中の ずれ {d6["db"][2]}・1行：高さ {d6["db"][3]}）')
        base = (dq['btn'], dq['kise']); per = {}
        for tab in ('win5', 'rec', 'stats', 'set', 'judge'):
            pg.locator(f'.tabbar button[data-tab="{tab}"]').click(); pg.wait_for_timeout(450); pg.evaluate("() => window.scrollTo(0, 0)"); pg.wait_for_timeout(200)
            x = pg.evaluate(DOCK); per[tab] = (dock_ok(x)[0], x['btn'] == base[0] and x['kise'] == base[1], x['tab'])
            if tab == 'rec': shot(pg, 'v230_rec')
        check(all(v[0] and v[1] and v[2] == t for t, v in per.items()), f'5つの タブ どれでも 出る・同じ 場所（{per}）')
        # ほかの タブで 押す：作戦会議が 開く・着せ替えへ
        pg.locator('.tabbar button[data-tab="rec"]').click(); pg.wait_for_timeout(450)
        r = pg.evaluate("() => { const r = document.getElementById('planBtn').getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }"); pg.touchscreen.tap(*r)
        pg.wait_for_function("() => window.TCPlan && TCPlan.isOpen()", timeout=30000); pg.wait_for_timeout(700)
        po = pg.evaluate("() => ({ open: TCPlan.isOpen(), host: document.getElementById('tcPlan').parentNode.id, tab: document.querySelector('.tabbar button[aria-selected=\"true\"]').dataset.tab })")
        pg.locator('#tcPlan [data-p=close]').click(); pg.wait_for_timeout(400)
        r = pg.evaluate("() => { const r = document.querySelector('#kiseBtn .kisel').getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }"); pg.touchscreen.tap(*r); pg.wait_for_timeout(900)
        ko = pg.evaluate("() => { const s = document.getElementById('setKisekae'), hd = document.querySelector('header').getBoundingClientRect(); return { tab: document.querySelector('.tabbar button[aria-selected=\"true\"]').dataset.tab, gap: s ? Math.round(s.getBoundingClientRect().top - hd.bottom) : null }; }")
        check(po == {'open': True, 'host': 'planHost', 'tab': 'rec'} and ko['tab'] == 'set' and ko['gap'] is not None and abs(ko['gap'] - 8) <= 2,
              f'記録タブで 作戦会議を 押す → 記録タブの 上に 作戦会議（{po}）・着せ替えを 押す → 設定の「着せ替え」が 上の 帯の すぐ 下（{ko}）')
        pg.locator('.tabbar button[data-tab="judge"]').click(); pg.wait_for_timeout(500)
        # ⑤ ページを 動かしても 同じ 所
        pos0 = pg.evaluate("() => { window.scrollTo(0, 0); return ['planBtn', 'kiseBtn', 'tcFab', 'figFab'].map(i => { const r = document.getElementById(i).getBoundingClientRect(); return [r.left, r.top].map(v => Math.round(v * 10) / 10); }); }")
        moved = []
        for y in (200, 900, 100000):
            pg.evaluate("(y) => window.scrollTo(0, y)", y); pg.wait_for_timeout(350)
            moved.append(pg.evaluate("() => ['planBtn', 'kiseBtn', 'tcFab', 'figFab'].map(i => { const r = document.getElementById(i).getBoundingClientRect(); return [r.left, r.top].map(v => Math.round(v * 10) / 10); })") == pos0)
        pg.evaluate("() => window.scrollTo(0, 0)"); pg.wait_for_timeout(300)
        check(all(moved), f'ページを 動かしても 作戦会議・着せ替え（上の 帯と いっしょ）・丸い ボタンは 同じ 所（{moved}）')

        print('■ 壁紙を かえる（⑧）')
        if WALL:
            res = {}
            for tid in ('news', 'ink', 'carousel', 'default'):
                pg.evaluate("(id) => TengelKisekae.apply(id, false)", tid)
                try: pg.wait_for_function("(id) => TengelKisekae.current() === id && TengelKisekae.loaded()", arg=tid, timeout=8000)
                except Exception: res[tid] = '読めない'; continue
                pg.wait_for_timeout(1500); x = pg.evaluate(DOCK); o, dd = dock_ok(x); res[tid] = (o, dd['k'] if isinstance(dd, dict) else dd, dd.get('db') if isinstance(dd, dict) else None)
                if tid == 'news': shot(pg, 'v230_wall_news')
            check(all(isinstance(v, tuple) and v[0] for v in res.values()), f'ロゴの 大きさが ちがう 壁紙でも 置き直す（作戦会議は 結果待ちの 下・着せ替えは ミッションの 下・テンゲルデータは ロゴの 下）・重ならない（{res}）')
        else:
            print('  （壁紙の 絵が ない ので とばす）')

        print('■ 画面の 幅（⑤）')
        sz = {}
        for vw, vh in ((375, 667), (390, 844), (430, 932), (402, 874)):
            pg.set_viewport_size({'width': vw, 'height': vh}); pg.wait_for_timeout(700); pg.wait_for_function("() => !TengelFab.busy()", timeout=8000); pg.wait_for_timeout(400)
            q2 = pg.evaluate(ROW); o2, d2 = row_ok(q2); x = pg.evaluate(DOCK); o3, d3 = dock_ok(x)
            sz[vw] = (o2, d2['fd'], o3, d3['k'] if isinstance(d3, dict) else d3)
            if vw == 375: shot(pg, 'v230_375')
        check(all(v[0] and v[2] for v in sz.values()) and sz[375][1] == 73 and sz[390][1] == 76 and sz[402][1] == 78 and sz[430][1] == 80,
              f'幅を かえると 丸の 大きさも かわる（375：73・390：76・402：78・430：80px）・作戦会議・着せ替え・テンゲルデータも 置き直す（{sz}）')
        check(not errs, f'エラー なし {errs[:3]}')

        print('■ 広い 画面（⑨）')
        wide = {}
        for vw, vh in ((700, 1000), (1024, 768)):
            cx = b.new_context(viewport={'width': vw, 'height': vh}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo'); cx.add_init_script(FAKE)
            px = cx.new_page(); e2 = []; px.on('pageerror', lambda e: e2.append(str(e)[:200]))
            px.goto(APP); px.wait_for_function("() => window.TengelFab && document.querySelector('#figFab') && document.getElementById('kiseBtn')", timeout=60000)
            px.wait_for_timeout(800); gate(px); px.wait_for_timeout(1800)
            q3 = px.evaluate(ROW); x = px.evaluate(DOCK); o3, d3 = dock_ok(x)
            if not o3:      # 上の 帯に 入らない：前の 場所（レース情報の カードの 右上・判定タブ だけ）
                fb = px.evaluate("""() => { const b = document.getElementById('planBtn'), k = document.getElementById('kiseBtn'), c = document.querySelector('#v-judge .card').getBoundingClientRect(), r = b.getBoundingClientRect(), hd = document.querySelector('header.top').getBoundingClientRect();
                  return { fixed: getComputedStyle(b).position === 'fixed' && b.parentNode === document.body && !b.classList.contains('dk'), corner: Math.abs(r.right - c.right) < 30 && r.bottom > hd.bottom, kvis: k.getBoundingClientRect().height > 0 }; }""")
                px.evaluate("() => { const b = [...document.querySelectorAll('.tabbar button[data-tab=rec], .tabs-top button[data-tab=rec]')].find(x => x.offsetParent); if (b) b.click(); }"); px.wait_for_timeout(500)
                hid = px.evaluate("() => ['planBtn', 'kiseBtn'].map(i => document.getElementById(i).getBoundingClientRect().height === 0)")
                o3 = fb['fixed'] and fb['corner'] and fb['kvis'] and hid == [True, True]; mode = f'前の 場所（判定タブ だけ：{fb}・{hid}）'
            else: mode = f'上の 帯の 中（{d3["k"]} 倍）'
            mid = (q3['col'][0] + q3['col'][2]) / 2
            low = (q3['tab'] - q3['col'][3]) if q3['tab'] is not None else (q3['vh'] - q3['col'][3])
            wide[vw] = (o3, mode, round(q3['col'][2] - q3['col'][0], 1), round(mid, 1), q3['fd'], round(low, 1))
            ok_row = q3['rw'] and abs(mid - vw / 2) <= 1 and q3['col'][2] - q3['col'][0] <= 480.5 and q3['fd'] == fdx(vw) and (3 <= low <= 5 if q3['tab'] is not None else 9 <= low <= 11)
            wide[vw] = wide[vw] + (ok_row, not e2)
            if SHOT: px.screenshot(path=os.path.join(SHOT, f'v230_wide_{vw}.png'))
            cx.close()
        check(all(v[0] and v[6] and v[7] for v in wide.values()),
              f'広い 画面：丸い ボタンの 列は まん中・幅 480px まで（下の タブが ない ときは 画面の 下から 10px）・作戦会議と 着せ替えは 上の 帯に 入れば 帯の 中／入らなければ 前の 場所（{wide}）')
        b.close()
finally:
    srv.terminate()
print('NG' if fails else 'OK', len(fails), fails)
sys.exit(1 if fails else 0)
