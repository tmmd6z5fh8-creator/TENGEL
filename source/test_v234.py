# 第4.234版の テスト（まさちゃん 11/28 02:44「壁紙の競馬新聞は、馬の絵を消して、2枚目みたいなデザインで、三枚目の馬券入れて！
#   馬券の中の数字を15秒起きにランダムに変えて！合計25種類の組み合わせが欲しいけどデータ的には大丈夫かな？」・02:46「数字に0は入れないで！」・
#   02:49「いや！10はいいよ！」「数字の前に0を入れないでってこと！」）
#   ① 台帳と 道具：news_blobs.json の paper・tickets（新しい 絵）・news_tk.json（置く 場所・数字の 枠 5つ）・blobs20.json の news（止まった 絵）・
#      もとの 絵と できた 絵は リポジトリに 入れない
#   ② 絵：新聞の 紙と 字（馬なし：前の 絵と 馬の 所 だけ ちがう）・馬券 2まい（まさちゃんの 絵から：pt の 3倍・すき通し）・止まった 絵（780×320）
#   ③ 25組：1〜16番・頭に 0 なし・3頭 ちがう・3連単も 馬単も 25とおり ちがう・1組目は 見本の 番号・10番も ある
#   ④ ページ（news_wall.inline）：紙・馬券・数字の 層（data-tkc＝25組・data-tki）・15秒・視差効果を減らす なら 動きなし・前の 走る 馬は ない
#   ⑤ アプリの 中身：ks_news.json・一覧の 小さな 絵・アプリに 入る 絵（走る コマと 前の 止まった 絵は 入らない）
#   ⑥ アプリの 画面（iPhone の 3倍）：絵が 出る・字は Kaisei Tokumin・数字は 枠の 中（25組の どの 数字でも はみ出さない）・数字が 描かれて いる
#   ⑦ 数字が かわる（動きを 0.25秒に して）：はじめの 25回は 25組 ぜんぶ ちがう・同じ 組が つづかない・馬単は 3連単の 1着→2着・頭に 0 なし
#   ⑧ 止める（.pause）・控えめ（.calm）・視差効果を減らす の 間は かわらない（数字は こく 出た まま）・また 動く
#   ⑨ 出す たびに ちがう 組から・設定の タイル（.kslv）でも 同じ（kpkbnsTk）・タイルの 絵は 新しい 止まった 絵
#   ⑩ 写真：t4/v234_news.png（上の絵）・t4/v234_news_top.png（判定タブの 上）
#   02:59「トレーニングセンターの牧場の名前をユーザーが決められるようにできる？一枚目の黄四角のところに、二枚目みたいに、看板置いて！三枚目が看板のモデル！
#          ユーザーが名前打ち込んで決められるようにして！」
#   ⑪ 看板：フィールドの すぐ 上の 帯・まさちゃんの 看板の 絵・はじめは「テンゲル牧場」・字は 板の 中・フィールドは 前と 同じ 大きさ（390×844）
#   ⑫ 看板を 押すと 名前の 窓（いまの 名前・数・キーボード）→ 打ちこんで「決める」→ 看板と 保存（localStorage の tengel.tc の farm）・Enter でも 決まる
#   ⑬ 12文字 まで（13文字 から「決める」が 押せない）・12文字は 字を 小さく して 板の 中・空なら「テンゲル牧場」・「テンゲル牧場」に もどす
#   ⑭ やめる・✕・うしろの 幕は かえない・開いた すぐ あとの 幕の クリックでは 閉じない・見えない 字は 入れない・タグの 形の 字も 字の まま
#   ⑮ 閉じて 開き直しても・ページを 読み直しても のこる・遊び方に「牧場の看板」・iPhone SE（375×667）でも 看板と フィールドが 重ならない
#   ⑯ 写真：t4/v234_tc_sign.png（看板）・t4/v234_tc_name.png（名前の 窓）
#   第4.235版から：数字が かわる 秒は news_wall.TK_S（7秒：まさちゃん 11/28 08:41）・看板を 押すと アプリでは iOS の 窓（test_v235.py）。
#     この テストの にせものの アプリ（test_native.py の FAKE）は 窓を 出せない ので、画面の 中の 窓（nameDialog）に なる ＝ その 窓の たしかめ
#   python3 test_v234.py
import hashlib, io, json, os, re, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
K = os.path.join(W, 'kisekae'); sys.path.insert(0, K); sys.path.insert(0, os.path.join(K, 'flat'))
BL = os.environ.get('KISEKAE_ASSETS') or os.path.join(W, 'ios', 'kisekae_blobs')
SHOT = os.path.join(W, 't4'); os.makedirs(SHOT, exist_ok=True)
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c:
        fails.append(label)


HEX = lambda v: bool(re.fullmatch(r'[0-9a-f]{32}', str(v)))
import news_wall, news_ticket
NB = json.load(open(os.path.join(K, 'news_blobs.json'), encoding='utf8')); TK = json.load(open(os.path.join(K, 'news_tk.json'), encoding='utf8'))
B20 = json.load(open(os.path.join(K, 'blobs20.json'), encoding='utf8'))
OLD_STATIC, OLD_RUN = '045aff74c918d326216c6658f2bcdf93', '2621145cc2fdd4ce6c1836427b87ad0a'
PAPER, TICKETS, THUMB = NB.get('paper'), NB.get('tickets'), B20.get('news')

# ---- ① 台帳と 道具
check(HEX(PAPER) and HEX(TICKETS) and HEX(THUMB) and len({PAPER, TICKETS, THUMB, OLD_STATIC, OLD_RUN}) == 5 and NB.get('static') == OLD_STATIC and NB.get('run') == OLD_RUN,
      f'① 台帳：news_blobs.json に 新聞の 紙（paper {PAPER[:8]}…）・馬券（tickets {TICKETS[:8]}…）・前の 止まった 絵と 走る コマは のこす（もう 使わない）・'
      f'blobs20.json の news（選ぶ 画面の 小さな 絵）は 新しい 止まった 絵（{THUMB[:8]}…）')
cells = TK.get('cells') or []
check(TK.get('box') == [117, 18, 175, 140] and TK.get('scale') == 3 and TK.get('font') == 0.92 and [(c['t'], c['i']) for c in cells] == [('umatan', 0), ('umatan', 1), ('sanrentan', 0), ('sanrentan', 1), ('sanrentan', 2)]
      and all(len(c['quad']) == 4 for c in cells) and TK['src']['sha1'] == news_ticket.SRC_SHA1 and TK['src']['crop'] == list(news_ticket.CROP),
      f'① 置く 場所（news_tk.json）：壁紙の 左 117・上 18・175×140pt（左の 記事と 右の 印の 表の あいだ）・数字の 枠 5つ（馬単 1着・2着／3連単 1着・2着・3着）・字の 大きさ 枠の 0.92')
quad_ok = all(abs(q[1][1] - q[0][1]) < 6 and 15 < q[1][0] - q[0][0] < 22 and 11 < q[3][1] - q[0][1] < 16 for q in (c['quad'] for c in cells))
check(quad_ok and cells[0]['quad'][0][1] < 60 < cells[2]['quad'][0][1] and cells[2]['quad'][0][0] < cells[3]['quad'][0][0] < cells[4]['quad'][0][0],
      '① 数字の 枠：どれも 横 15〜22pt・たて 11〜16pt・少し かたむいた 四角（馬券の 絵の かたむき）・馬単は 上の 馬券・3連単は 下の 馬券 で 左から')
ign = lambda p: subprocess.run(['git', 'check-ignore', '-q', p], cwd=W).returncode == 0
tracked = subprocess.run(['git', 'ls-files', 'ios/wall_src', 'ios/kisekae_blobs'], capture_output=True, text=True, cwd=W).stdout.strip()
check(ign('ios/wall_src/news_tickets.png') and ign(f'ios/kisekae_blobs/{TICKETS}.webp') and not tracked and os.path.exists(os.path.join(K, 'flat', 'news_ticket.py'))
      and '/home/claude' not in open(os.path.join(K, 'flat', 'news_ticket.py'), encoding='utf8').read(),
      '① まさちゃんの 馬券の 絵（ios/wall_src/news_tickets.png）と できた 絵（ios/kisekae_blobs）は リポジトリに 入れない・作る 道具（kisekae/flat/news_ticket.py）は ある')

# ---- ② 絵（手元に ある とき）
have = all(os.path.exists(os.path.join(BL, i + '.webp')) for i in (PAPER, TICKETS, THUMB, OLD_STATIC))
if have:
    import numpy as np
    from PIL import Image
    rd = lambda i: open(os.path.join(BL, i + '.webp'), 'rb').read()
    md = all(hashlib.md5(rd(i)).hexdigest() == i for i in (PAPER, TICKETS, THUMB))
    ip, it, ih = (Image.open(io.BytesIO(rd(i))) for i in (PAPER, TICKETS, THUMB))
    check(md and ip.size == (780, 320) and ip.mode == 'RGB' and it.size == (525, 420) and it.mode == 'RGBA' and ih.size == (780, 320),
          f'② 絵：名前は 中身の md5・新聞の 紙 780×320（いままでの 止まった 絵と 同じ 大きさ）・馬券 525×420（175×140pt の 3倍・すき通し）・止まった 絵 780×320（{len(rd(PAPER)) / 1e3:.1f}KB・{len(rd(TICKETS)) / 1e3:.1f}KB・{len(rd(THUMB)) / 1e3:.1f}KB）')
    a_new = np.asarray(ip.convert('RGB')).astype(np.float32); a_old = np.asarray(Image.open(io.BytesIO(rd(OLD_STATIC))).convert('RGB')).astype(np.float32)
    d = np.abs(a_new - a_old).mean(2); horse = np.zeros_like(d, bool); horse[60:300, 200:585] = True
    hz = np.zeros_like(d, bool); hz[60:300, 240:585] = True      # 墨を 数える 所：左の 題字の 黒い 箱・二重線（x 236 まで）に かからない 所
    ink = float(((a_old.mean(2) < 80) & hz).mean() / hz.mean()); ink_new = float(((a_new.mean(2) < 80) & hz).mean() / hz.mean())
    check(float(d[~horse].mean()) < 3 and float(d[horse].mean()) > 15 and ink > 0.1 and ink_new < 0.002,
          f'② 新聞の 紙：馬の 所の ほかは 前の 絵と 同じ（ちがい {float(d[~horse].mean()):.1f}）・馬の 所は 墨が ない（前 {ink * 100:.0f}% → {ink_new * 100:.2f}%）')
    same_paper = news_ticket.paper_webp() == rd(PAPER)
    srcok = os.path.exists(news_ticket.SRC) and news_ticket.sha1(news_ticket.SRC) == news_ticket.SRC_SHA1
    same_tk = srcok and news_ticket.tickets_webp(news_ticket.source()) == rd(TICKETS) and news_ticket.layout(news_ticket.source()) == TK
    check(same_paper and same_tk, '② 道具で 作り直すと 同じ 絵（紙・馬券）・同じ 置く 場所（news_tk.json）になる（まさちゃんの 絵は 読む だけ）')
    al = np.asarray(it)[..., 3]
    check(al.max() >= 250 and al.min() == 0 and 0.45 < float((al > 200).mean()) < 0.75, f'② 馬券：まわりは すき通し・馬券は すき通さない（{float((al > 200).mean()) * 100:.0f}%）')
else:
    print('※ 壁紙の 絵（ios/kisekae_blobs）が ない ので、絵の 確かめは しない')

# ---- ③ 25組
C = news_wall.TK_COMBOS
NUM = r'([1-9]|1[0-6])'
okc = all(re.fullmatch(f'{NUM}-{NUM}-{NUM}', c) and len(set(c.split('-'))) == 3 for c in C)
check(len(C) == 25 and len(set(C)) == 25 and len({c.rsplit('-', 1)[0] for c in C}) == 25 and okc and C[0] == '3-7-12' and any('10' in c.split('-') for c in C)
      and not any(x.startswith('0') for c in C for x in c.split('-')),
      f'③ 25組：1〜16番・頭に 0 なし・3頭 ちがう・3連単も 馬単（1着→2着）も 25とおり ぜんぶ ちがう・1組目は 見本の 3→7→12・10番も ある（{sum("10" in c.split("-") for c in C)}組）')

# ---- ④ ページ
blobs = news_wall.load_blobs(os.path.join(K, 'news_blobs.json'))
html, css = news_wall.inline(blobs, TK)
first = C[0].split('-')
cells_html = re.findall(r'<i class="nsn k(\d)" data-tki="(\d)">(\d+)</i>', html)
check(f'src="/_blob/{PAPER}"' in html and f'src="/_blob/{TICKETS}"' in html and OLD_RUN not in html + css and OLD_STATIC not in html + css and 'nsh' not in html + css and 'nsr' not in html + css
      and f'data-tkc="{" ".join(C)}"' in html and cells_html == [('0', '0', first[0]), ('1', '1', first[1]), ('2', '0', first[0]), ('3', '1', first[1]), ('4', '2', first[2])]
      and f'aria-label="{news_wall.ALT}"' in html and f'{news_wall.TK_S}秒ごと' in news_wall.ALT,
      '④ ページ：新聞の 紙（馬なし）・馬券・数字の 層（data-tkc＝25組）・数字 5つ（馬単 2つ＝組の 1・2番目／3連単 3つ）・はじめは 1組目・前の 走る 馬（nsh・nsr・走る コマ）は ない')
FI = round(100 * news_wall.TK_FADE / news_wall.TK_S, 4)
check('.nsw .nst{position:absolute;left:117px;top:18px;width:175px;height:140px;pointer-events:none}' in css and f'.nsw .nsq{{position:absolute;left:0;top:0;width:175px;height:140px;animation:nsTk {news_wall.TK_S}s linear infinite}}' in css
      and f'@keyframes nsTk{{0%{{opacity:0}}{news_wall._f(FI, 4)}%{{opacity:1}}{news_wall._f(100 - FI, 4)}%{{opacity:1}}100%{{opacity:0}}}}' in css and '@media (prefers-reduced-motion:reduce){.nsw .nsq{animation:none}}' in css
      and 'font-family:"Kaisei Tokumin",serif;font-weight:800' in css and css.count('transform:matrix(') == 5,
      f'④ ページの CSS：馬券は 左 117・上 18・175×140pt・数字の 層は {news_wall.TK_S}秒で 1回り（はじめと おわりに 0.4秒 うすく）・視差効果を減らす なら 動きなし・字は Kaisei Tokumin 800・枠ごとの かたむき（matrix）')
h0, c0 = news_wall.inline_run(blobs, json.load(open(os.path.join(K, 'news_run.json'), encoding='utf8')))
check(f'/_blob/{OLD_RUN}' in c0 and 'class="nsh"' in h0, '④ 前の 形（墨の 馬が 走る：inline_run）は のこして ある（テスト・見本 用。アプリには 入れない）')

# ---- ⑤〜⑩ アプリ
SRV = os.path.join(W, 'srv_v234'); PORT = 8861; APP = f'http://localhost:{PORT}/APP/'
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
sys.path.insert(0, W)
from assets_dir import adir
TCA = adir('tc_assets'); HAVE_TC = os.path.isdir(TCA) and len(os.listdir(TCA)) > 100 and os.path.exists(os.path.join(TCA, 'tc_sign.webp'))
if HAVE_TC:
    for f in os.listdir(TCA): shutil.copy(os.path.join(TCA, f), os.path.join(SRV, 'APP', f))
NT = open(os.path.join(W, 'test_native.py'), encoding='utf8').read()
FAKE = re.search(r'\nFAKE = """(.*?)"""', NT, re.S).group(1)      # アプリの 窓口の にせもの
kj = json.load(open(os.path.join(SRV, 'APP', 'ks_news.json'), encoding='utf8')); kt = kj['bnr']['html'] + kj['bnr']['css']
check(f'ks_{PAPER}.webp' in kt and f'ks_{TICKETS}.webp' in kt and OLD_RUN not in json.dumps(kj) and OLD_STATIC not in json.dumps(kj)
      and '@keyframes kbnsTk{' in kj['bnr']['css'] and f'animation:kbnsTk {news_wall.TK_S}s linear infinite' in kj['bnr']['css'] and '#ksBnr.calm .nsw .nsq{animation:none}' in kj['bnr']['css']
      and '#ksBnr .nsw .nsn{' in kj['bnr']['css'],
      '⑤ アプリの ks_news.json：紙と 馬券の 絵・数字の 層の 動き（kbnsTk）・演出を控えめにする（.calm）でも 動きなし・前の 走る コマと 止まった 絵は さして いない')
import build_kisekae as BK
ids = set(BK.asset_ids())
check({PAPER, TICKETS, THUMB} <= ids and OLD_RUN not in ids and OLD_STATIC not in ids,
      '⑤ アプリに 入る 壁紙の 絵：新聞の 紙・馬券・新しい 止まった 絵は 入る・前の 走る コマと 前の 止まった 絵は 入らない')

GATE_GONE = "() => { const g = document.querySelector('#gate'); return !g || g.hidden || getComputedStyle(g).display === 'none'; }"
CUR = """(sel) => { const q = document.querySelector(sel); if (!q) return null; const n = [...q.querySelectorAll('[data-tki]')].map(e => e.textContent);
  return { k: q.dataset.tkn, n, op: +getComputedStyle(q).opacity, an: q.getAnimations().map(a => [a.animationName, a.playState, a.effect.getComputedTiming().duration, a.effect.getComputedTiming().iterations]) }; }"""
WATCH = """([sel, ms]) => new Promise(res => { const q = document.querySelector(sel), seen = [], bad = []; let last = null;
  const t0 = performance.now(), tick = () => { const k = q.dataset.tkn, n = [...q.querySelectorAll('[data-tki]')].map(e => e.textContent).join(' ');
    if (k !== last) { seen.push(+k); last = k; const v = n.split(' '); if (v[0] !== v[2] || v[1] !== v[3] || v.some(x => !/^([1-9]|1[0-6])$/.test(x)) || new Set(v.slice(2)).size !== 3) bad.push(n); }
    if (performance.now() - t0 < ms) requestAnimationFrame(tick); else res({ seen, bad }); }; tick(); })"""
TC_OPEN = "() => window.TCApp && document.querySelector('#tcOv.on') && !document.querySelector('#tcOv .tcld')"
SIGN = """() => { const n = document.querySelector('#tcOv .tcnm'), st = document.querySelector('#tcOv .tcst'), wr = document.querySelector('#tcOv .tcwr'); if (!n) return null;
  const R = e => { const r = e.getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; }, im = n.querySelector('img'), o = n.querySelector('.tcnmt'), i = n.querySelector('.tcnmi');
  return { sign: R(n), stage: R(st), wr: R(wr), img: [im.complete, im.naturalWidth, im.naturalHeight, im.getAttribute('src')], txt: i.textContent, fs: parseFloat(getComputedStyle(i).fontSize),
    room: o.clientWidth, need: i.scrollWidth, ih: i.scrollHeight, oh: o.clientHeight, ff: getComputedStyle(i).fontFamily, label: n.getAttribute('aria-label'), name: TCApp.farm.name(),
    saved: (JSON.parse(localStorage.getItem('tengel.tc') || '{}') || {}).farm, kids: i.children.length }; }"""
DLG = """() => { const d = document.querySelector('#tcnmd'); if (!d) return null; const inp = d.querySelector('.nin');
  return { on: d.classList.contains('on'), val: inp.value, cnt: d.querySelector('.ncnt').textContent, ng: d.querySelector('.ncnt').classList.contains('ng'), ok: !d.querySelector('[data-nm=ok]').disabled,
    focus: document.activeElement === inp, us: getComputedStyle(inp).webkitUserSelect || getComputedStyle(inp).userSelect, fs: parseFloat(getComputedStyle(inp).fontSize) }; }"""


def tc_open(pg):
    pg.locator('#tcFab').click()
    pg.wait_for_function(TC_OPEN, timeout=90000); pg.wait_for_timeout(1500)


def tc_checks(p):
    b2 = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'])
    c2 = b2.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=3, locale='ja-JP', timezone_id='Asia/Tokyo', has_touch=True)
    c2.add_init_script(FAKE)
    pg = c2.new_page(); e2 = []; pg.on('pageerror', lambda e: e2.append(str(e)))
    pg.goto(APP); pg.wait_for_timeout(1500)
    if pg.locator('#gateGo').count(): pg.click('#gateGo'); pg.wait_for_timeout(700)
    pg.wait_for_function(GATE_GONE, timeout=10000); pg.wait_for_timeout(400)
    tc_open(pg)
    q = pg.evaluate(SIGN)
    sx, sy, sw, sh = q['sign']; tx, ty, tw, th = q['stage']; wx, wy, ww, wh = q['wr']
    check(q['img'] == [True, 840, 138, 'tc_sign.webp'] and q['txt'] == 'テンゲル牧場' and q['name'] == 'テンゲル牧場' and abs(sw - 273) < 0.6 and abs(sw / sh - 2036 / 334) < 0.05
          and abs(sx + sw / 2 - 195) < 0.6 and sy >= wy and sy + sh <= ty - 1 and abs(tw - 390) < 0.6 and ty + th <= wy + wh + 0.5 and q['need'] <= q['room'] and q['ih'] <= q['oh'] + 1
          and ('Mincho' in q['ff'] or 'Serif' in q['ff']),
          f'⑪ 看板：フィールドの すぐ 上（看板 {sy - wy:.1f}〜{sy - wy + sh:.1f}pt・フィールドは {ty - wy:.1f}pt から）・まさちゃんの 看板の 絵（840×138）・幅 {sw:.0f}pt・'
          f'はじめは「テンゲル牧場」（字 {q["fs"]:.1f}px・板の 中）・フィールドは 前と 同じ 幅 390pt')
    nm_box = pg.evaluate("() => { const b = document.querySelector('#tcOv .tcnm').getBoundingClientRect(); return [b.left, b.top, b.width, b.height]; }")
    clip = dict(x=0, y=max(0, nm_box[1] - 30), width=390, height=nm_box[3] + 130)
    pg.screenshot(path=os.path.join(SHOT, 'v234_tc_sign.png'), clip=clip)
    # ⑫ 押すと 窓 → 打ちこむ → 決める
    pg.locator('#tcOv .tcnm').click(); pg.wait_for_timeout(450)
    d = pg.evaluate(DLG)
    check(bool(d) and d['on'] and d['val'] == 'テンゲル牧場' and d['cnt'] == '6/12文字' and d['ok'] and d['focus'] and d['us'] in ('text', 'auto') and d['fs'] >= 16,
          f'⑫ 看板を 押すと 名前の 窓：いまの 名前・{d and d["cnt"]}・打ちこめる（キーボード：字の 大きさ {d and d["fs"]}px＝拡大 しない）')
    pg.screenshot(path=os.path.join(SHOT, 'v234_tc_name.png'), clip=dict(x=0, y=0, width=390, height=420))
    pg.fill('#tcnmd .nin', 'まさちゃん牧場'); d = pg.evaluate(DLG)
    pg.locator('#tcnmd [data-nm=ok]').click(); pg.wait_for_timeout(300)
    q = pg.evaluate(SIGN); d2 = pg.evaluate(DLG); m = pg.evaluate("() => document.querySelector('#tcOv .tcmsg').textContent")
    check(d['cnt'] == '7/12文字' and not d2['on'] and q['txt'] == 'まさちゃん牧場' and q['saved'] == 'まさちゃん牧場' and q['need'] <= q['room'] and '「まさちゃん牧場」' in q['label']
          and '看板の 名前を「まさちゃん牧場」に したよ' in m,
          f'⑫ 打ちこんで「決める」→ 看板が「{q["txt"]}」・保存（tengel.tc の farm＝{q["saved"]}）・お知らせ「{m}」')
    pg.locator('#tcOv .tcnm').click(); pg.wait_for_timeout(450)
    pg.fill('#tcnmd .nin', 'テンゲル第2牧場'); pg.keyboard.press('Enter'); pg.wait_for_timeout(250)
    q = pg.evaluate(SIGN); d = pg.evaluate(DLG)
    check(not d['on'] and q['txt'] == 'テンゲル第2牧場' and q['saved'] == 'テンゲル第2牧場', '⑫ キーボードの 決定（Enter）でも 決まる')
    # ⑬ 12文字 まで
    pg.locator('#tcOv .tcnm').click(); pg.wait_for_timeout(450)
    pg.fill('#tcnmd .nin', 'ながいながいなまえのぼくじょう'); d = pg.evaluate(DLG)
    pg.keyboard.press('Enter'); pg.wait_for_timeout(200); d1 = pg.evaluate(DLG); q1 = pg.evaluate(SIGN)
    pg.fill('#tcnmd .nin', 'アイウエオカキクケコサシ'); d2 = pg.evaluate(DLG)
    pg.locator('#tcnmd [data-nm=ok]').click(); pg.wait_for_timeout(250); q = pg.evaluate(SIGN)
    check(d['ng'] and not d['ok'] and d['cnt'] == '15/12文字（12文字までだよ）' and d1['on'] and q1['saved'] == 'テンゲル第2牧場' and d2['cnt'] == '12/12文字' and d2['ok']
          and q['txt'] == 'アイウエオカキクケコサシ' and q['need'] <= q['room'] and q['fs'] < 24.5 * 0.9,
          f'⑬ 13文字 から「決める」が 押せない（{d["cnt"]}・Enter でも 決まらない）・12文字は 決まって 字を 小さく（{q["fs"]:.1f}px）して 板の 中（{q["need"]}≦{q["room"]}px）')
    pg.locator('#tcOv .tcnm').click(); pg.wait_for_timeout(450)
    pg.fill('#tcnmd .nin', '   '); d = pg.evaluate(DLG)
    pg.locator('#tcnmd [data-nm=ok]').click(); pg.wait_for_timeout(250); q = pg.evaluate(SIGN)
    pg.locator('#tcOv .tcnm').click(); pg.wait_for_timeout(450)
    pg.fill('#tcnmd .nin', 'abc'); pg.locator('#tcnmd [data-nm=def]').click(); d3 = pg.evaluate(DLG)
    pg.locator('#tcnmd [data-nm=no]').last.click(); pg.wait_for_timeout(200)
    check(d['cnt'] == '空なら「テンゲル牧場」になるよ' and d['ok'] and q['txt'] == 'テンゲル牧場' and q['saved'] == '' and d3['val'] == 'テンゲル牧場' and d3['focus'],
          '⑬ 空で「決める」→「テンゲル牧場」（保存は 空）・「「テンゲル牧場」に もどす」は 欄に 入れる だけ（決めるまで 保存しない）')
    # ⑭ やめる・✕・幕・すぐの クリック・見えない 字・タグの 形
    res = []
    for how in ('no', 'x', 'bk'):
        pg.locator('#tcOv .tcnm').click(); pg.wait_for_timeout(450)
        pg.fill('#tcnmd .nin', 'かえない名前')
        if how == 'no': pg.locator('#tcnmd .nb[data-nm=no]').click()
        elif how == 'x': pg.locator('#tcnmd .nx').click()
        else: pg.mouse.click(195, 820)
        pg.wait_for_timeout(200); res.append((pg.evaluate(DLG)['on'], pg.evaluate(SIGN)['txt']))
    pg.evaluate("() => { TCApp.farm.dialog(); document.querySelector('#tcnmd .nbk').click(); }"); fast = pg.evaluate(DLG)['on']      # 第4.235版：画面の 中の 窓は farm.dialog
    pg.evaluate("() => TCApp.farm.close()")
    check(res == [(False, 'テンゲル牧場')] * 3 and fast, f'⑭ やめる・✕・うしろの 幕で 閉じても 名前は かわらない・開いた すぐ あと（0.35秒）の 幕の クリックでは 閉じない（{res}）')
    pg.locator('#tcOv .tcnm').click(); pg.wait_for_timeout(450)
    pg.evaluate("() => { const i = document.querySelector('#tcnmd .nin'); i.value = '\\u202eあ\\u0007い<b>う</b>\\n'; i.dispatchEvent(new Event('input')); }")
    pg.locator('#tcnmd [data-nm=ok]').click(); pg.wait_for_timeout(250); q = pg.evaluate(SIGN)
    check(q['txt'] == 'あい<b>う</b>' and q['kids'] == 0 and q['saved'] == 'あい<b>う</b>',
          f'⑭ 見えない 字（向きを かえる 字・ベル・改行）は 入れない・タグの 形の 字は 字の まま（看板「{q["txt"]}」・中に 要素 {q["kids"]}こ）')
    # ⑮ 開き直し・読み直し
    pg.locator('#tcOv .tcnm').click(); pg.wait_for_timeout(450); pg.fill('#tcnmd .nin', '星空ファーム'); pg.locator('#tcnmd [data-nm=ok]').click(); pg.wait_for_timeout(250)
    pg.evaluate("() => TCApp.close()"); pg.wait_for_timeout(400); pg.evaluate("() => TCApp.open()"); pg.wait_for_function(TC_OPEN, timeout=30000); pg.wait_for_timeout(600)
    q1 = pg.evaluate(SIGN)
    pg.reload(); pg.wait_for_timeout(1500)
    if pg.locator('#gateGo').count(): pg.click('#gateGo'); pg.wait_for_timeout(700)
    pg.wait_for_function(GATE_GONE, timeout=10000); pg.wait_for_timeout(400)
    tc_open(pg); q2 = pg.evaluate(SIGN)
    gd = pg.evaluate("() => { const T = window.TCGuide; if (!T) return null; T.open(document.querySelector('#tcOv')); const t = (document.querySelector('#tcg') || document.body).innerText; T.close(); return t; }")
    check(q1['txt'] == '星空ファーム' and q2['txt'] == '星空ファーム' and q2['saved'] == '星空ファーム' and bool(gd) and '牧場の看板' in gd and '12文字' in gd,
          '⑮ 閉じて 開き直しても・ページを 読み直しても 名前は のこる・遊び方（？）に「牧場の看板」の 項目')
    check(not e2, f'⑮ エラー なし {e2[:2]}')
    c2.close()
    # iPhone SE（375×667）：帯が たりない ので フィールドを 少し 小さく
    c3 = b2.new_context(viewport={'width': 375, 'height': 667}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo', has_touch=True)
    c3.add_init_script(FAKE)
    p3 = c3.new_page(); e3 = []; p3.on('pageerror', lambda e: e3.append(str(e)))
    p3.goto(APP); p3.wait_for_timeout(1500)
    if p3.locator('#gateGo').count(): p3.click('#gateGo'); p3.wait_for_timeout(700)
    p3.wait_for_function(GATE_GONE, timeout=10000); p3.wait_for_timeout(400)
    tc_open(p3); q = p3.evaluate(SIGN)
    sx, sy, sw, sh = q['sign']; tx, ty, tw, th = q['stage']; wx, wy, ww, wh = q['wr']
    check(abs(sw - round(375 * 0.7 + 1e-9)) < 0.6 and sy >= wy - 0.5 and sy + sh <= ty - 1 and ty + th <= wy + wh + 0.5 and tw < 375 and abs(tw / th - 1052 / 1657) < 0.002 and not e3,
          f'⑮ iPhone SE（375×667）：看板（{sw:.0f}×{sh:.1f}pt）は フィールドの 上・フィールドは 少し 小さく（{tw:.0f}×{th:.0f}pt）して 重ならない・はみ出さない')
    c3.close(); b2.close()


errs, bad = [], []
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
try:
    with sync_playwright() as p:
        br = p.chromium.launch()
        ctx = br.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=3, locale='ja-JP', timezone_id='Asia/Tokyo')
        pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('response', lambda r: bad.append(r.url.split('/')[-1]) if r.status >= 400 and '/ks_' in r.url else None)
        pg.goto(APP); pg.wait_for_timeout(1500)
        if pg.locator('#gateGo').count(): pg.click('#gateGo'); pg.wait_for_timeout(700)
        pg.wait_for_function("() => window.TengelKisekae && TengelKisekae.list().length > 0", timeout=10000)
        pg.wait_for_function(GATE_GONE, timeout=10000)
        th = pg.evaluate("() => (TengelKisekae.list().find(t => t.id === 'news') || {}).thumb")
        check(th == f'ks_{THUMB}.webp', f'⑤ 選ぶ 画面の 小さな 絵（一覧の thumb）は 新しい 止まった 絵（{th}）')
        pg.evaluate("(id) => TengelKisekae.apply(id, false)", 'news')
        pg.wait_for_function("() => TengelKisekae.current() === 'news' && TengelKisekae.loaded()", timeout=8000)
        pg.wait_for_function("() => document.fonts.status === 'loaded' && [...document.querySelectorAll('#ksBnr img')].every(i => i.complete)", timeout=8000); pg.wait_for_timeout(1200)
        pg.evaluate("window.scrollTo(0, 0)")
        q = pg.evaluate("""() => { const b = document.querySelector('#ksBnr'), w = b.querySelector('.nsw'), r = w.getBoundingClientRect(), im = [...w.querySelectorAll('img')].map(i => [i.className, i.naturalWidth, i.naturalHeight, i.getAttribute('src')]);
          const n = w.querySelector('.nsn'), fs = getComputedStyle(n);
          return { hidden: b.hidden, box: [r.width, r.height], im, ff: fs.fontFamily, fw: fs.fontWeight, col: fs.color, font: document.fonts.check('800 12px "Kaisei Tokumin"', '0123456789'),
                   ks: document.documentElement.dataset.ks, st: w.querySelector('.nst').getBoundingClientRect().toJSON() }; }""")
        okim = q['im'] == [['bnr', 780, 320, f'ks_{PAPER}.webp'], ['nstk', 525, 420, f'ks_{TICKETS}.webp']] if have else len(q['im']) == 2
        check(not q['hidden'] and q['box'] == [390, 160] and okim and q['font'] and 'Kaisei Tokumin' in q['ff'] and q['fw'] == '800' and q['ks'] == 'news'
              and abs(q['st']['x'] - 117) < 0.01 and abs(q['st']['width'] - 175) < 0.01,
              f'⑥ アプリ（iPhone の 3倍）：上の絵は 390×160pt・新聞の 紙と 馬券の 絵が 出る（{[i[1:3] for i in q["im"]]}）・数字の 字は Kaisei Tokumin 800（読めて いる）・馬券は 左 117pt・幅 175pt')
        # 数字が 描かれて いる（数字を かくした ときと くらべる）・写真
        pg.evaluate("() => { const s = document.createElement('style'); s.id = 'tkStill'; s.textContent = '#ksBnr .nsw .nsq{animation:none!important}'; document.head.appendChild(s); }"); pg.wait_for_timeout(200)
        r = pg.evaluate("() => document.querySelector('#ksBnr .nsw').getBoundingClientRect().toJSON()")
        clip = dict(x=r['x'], y=r['y'], width=390, height=160)
        import numpy as np
        from PIL import Image
        a1 = np.asarray(Image.open(io.BytesIO(pg.screenshot(clip=clip))).convert('RGB')).astype(np.float32)
        open(os.path.join(SHOT, 'v234_news.png'), 'wb').write(pg.screenshot(clip=clip))
        pg.evaluate("() => { document.getElementById('tkStill').textContent += '#ksBnr .nsw .nsn{visibility:hidden}'; }"); pg.wait_for_timeout(150)
        a0 = np.asarray(Image.open(io.BytesIO(pg.screenshot(clip=clip))).convert('RGB')).astype(np.float32)
        pg.evaluate("() => document.getElementById('tkStill').remove()")
        dk = ((a1.mean(2) < 90) & (a0.mean(2) > 150)).sum()
        check(a1.shape == (480, 1170, 3) and dk > 600, f'⑥ 数字が 描かれて いる（数字を かくした ときより 黒い 点が {dk}点 多い）・写真 t4/v234_news.png')
        # 数字は 枠の 中：5つの 枠に 1〜16 を 書いて 写す → 数字の 黒い 点が ぜんぶ 枠の 内がわで、枠の 線から 1pt 以上 はなれて いる
        bx = TK['box']; quads = [[((bx[0] + x) * 3, (bx[1] + y) * 3) for x, y in c['quad']] for c in cells]

        def inner(px, py, q, m):
            for k in range(4):
                (x0, y0), (x1, y1) = q[k], q[(k + 1) % 4]
                ex, ey = x1 - x0, y1 - y0; L = (ex * ex + ey * ey) ** .5
                if ((px - x0) * ey - (py - y0) * ex) / L > -m: return False     # 四すみは 時計回り（左上→右上→右下→左下）＝ 内がわは 右手
            return True
        orig = pg.evaluate("() => [...document.querySelectorAll('#ksBnr .nsn')].map(e => e.textContent)")
        pg.evaluate("() => { const s = document.createElement('style'); s.id = 'tkStill'; s.textContent = '#ksBnr .nsw .nsq{animation:none!important}'; document.head.appendChild(s); }"); pg.wait_for_timeout(150)
        worst, outs = 99.0, []
        for v in [str(i) for i in range(1, 17)]:
            pg.evaluate("(v) => document.querySelectorAll('#ksBnr .nsn').forEach(e => { e.textContent = v; })", v); pg.wait_for_timeout(60)
            b1 = np.asarray(Image.open(io.BytesIO(pg.screenshot(clip=clip))).convert('RGB')).astype(np.float32)
            ys, xs = np.where((a0.mean(2) - b1.mean(2)) > 60)
            for n, q in enumerate(quads):
                xa, xb = min(p[0] for p in q) - 9, max(p[0] for p in q) + 9; ya, yb = min(p[1] for p in q) - 9, max(p[1] for p in q) + 9
                sel = (xs >= xa) & (xs <= xb) & (ys >= ya) & (ys <= yb)
                pts = list(zip(xs[sel] + .5, ys[sel] + .5))
                if len(pts) < 20: outs.append((v, n, 'ink?')); continue
                for m in (3.0,):
                    bad_ = [pt for pt in pts if not inner(pt[0], pt[1], q, m)]
                    if bad_: outs.append((v, n, len(bad_)))
                for k in range(4):
                    (x0, y0), (x1, y1) = q[k], q[(k + 1) % 4]; ex, ey = x1 - x0, y1 - y0; L = (ex * ex + ey * ey) ** .5
                    worst = min(worst, min(-((px - x0) * ey - (py - y0) * ex) / L for px, py in pts) / 3)
        pg.evaluate("(o) => { document.querySelectorAll('#ksBnr .nsn').forEach((e, i) => { e.textContent = o[i]; }); document.getElementById('tkStill').remove(); }", orig)
        check(not outs, f'⑥ 数字は 枠の 中：5つの 枠に 1〜16 を 書いて 写すと、数字の 黒い 点は ぜんぶ 枠の 内がわ・枠の 線から {worst:.1f}pt 以上 はなれて いる（1pt 以上）' + (f'（はみ出し：{outs[:4]}）' if outs else ''))
        pg.screenshot(path=os.path.join(SHOT, 'v234_news_top.png'), clip=dict(x=0, y=0, width=390, height=560))
        # ⑦ 数字が かわる
        c1 = pg.evaluate(CUR, '#ksBnr .nsq')
        check(bool(c1) and c1['an'] and c1['an'][0][0] == 'kbnsTk' and c1['an'][0][1] == 'running' and c1['an'][0][2] == news_wall.TK_S * 1000 and c1['an'][0][3] is None or (c1 and c1['an'] and c1['an'][0][3] in (None, float('inf'))),
              f'⑦ 数字の 層の 動き：kbnsTk・{news_wall.TK_S}秒で 1回り・ずっと くり返す（{c1 and c1["an"]}）')
        pg.evaluate("() => { const s = document.createElement('style'); s.id = 'tkFast'; s.textContent = '#ksBnr .nsw .nsq{animation-duration:.25s!important}'; document.head.appendChild(s); }")
        w1 = pg.evaluate(WATCH, ['#ksBnr .nsq', 9000])
        sq = w1['seen']
        rep = any(a == b for a, b in zip(sq, sq[1:]))
        check(len(sq) >= 30 and sorted(sq[:25]) == list(range(25)) and not rep and not w1['bad'],
              f'⑦ 数字が かわる（動きを 0.25秒に して 9秒）：{len(sq) - 1}回 かわった・はじめの 25回は 25組 ぜんぶ ちがう・同じ 組が つづかない・馬単は 3連単の 1着→2着・数字は 1〜16（頭に 0 なし）'
              + (f'（おかしい：{w1["bad"][:3]}）' if w1['bad'] else ''))
        # ⑧ 止める・控えめ・視差効果を減らす
        pg.evaluate("() => document.querySelector('#ksBnr').classList.add('pause')"); pg.wait_for_timeout(150)
        wp = pg.evaluate(WATCH, ['#ksBnr .nsq', 1500]); cp = pg.evaluate(CUR, '#ksBnr .nsq')
        pg.evaluate("() => document.querySelector('#ksBnr').classList.remove('pause')"); pg.wait_for_timeout(150)
        wr = pg.evaluate(WATCH, ['#ksBnr .nsq', 1500])
        check(len(wp['seen']) == 1 and cp['an'][0][1] == 'paused' and len(wr['seen']) >= 3,
              f'⑧ 止めて いる 間（.pause：画面の 外・ほかの 窓の 下・アプリが 裏）は かわらない（1.5秒で {len(wp["seen"]) - 1}回）・また 動くと かわる（{len(wr["seen"]) - 1}回）')
        pg.evaluate("() => document.querySelector('#ksBnr').classList.add('calm')"); pg.wait_for_timeout(200)
        wc = pg.evaluate(WATCH, ['#ksBnr .nsq', 1500]); cc = pg.evaluate(CUR, '#ksBnr .nsq')
        pg.evaluate("() => document.querySelector('#ksBnr').classList.remove('calm')"); pg.wait_for_timeout(200)
        pg.emulate_media(reduced_motion='reduce'); pg.wait_for_timeout(200)
        wm = pg.evaluate(WATCH, ['#ksBnr .nsq', 1500]); cm = pg.evaluate(CUR, '#ksBnr .nsq')
        pg.emulate_media(reduced_motion='no-preference'); pg.wait_for_timeout(200)
        check(len(wc['seen']) == 1 and cc['an'] == [] and cc['op'] == 1 and len(wm['seen']) == 1 and cm['an'] == [] and cm['op'] == 1,
              '⑧ 演出を控えめにする（.calm）・視差効果を減らす：動きなし ＝ 数字は かわらず こく 出た まま（うすく ならない）')
        # ⑨ 出す たびに ちがう 組から
        starts = []
        for _ in range(8):
            pg.evaluate("(id) => TengelKisekae.apply(id, false)", 'default'); pg.wait_for_function("() => TengelKisekae.current() === 'default'")
            pg.evaluate("(id) => TengelKisekae.apply(id, false)", 'news'); pg.wait_for_function("() => TengelKisekae.current() === 'news' && TengelKisekae.loaded() && !!document.querySelector('#ksBnr .nsq')")
            starts.append(pg.evaluate("() => +document.querySelector('#ksBnr .nsq').dataset.tkn"))
        check(len(set(starts)) >= 3, f'⑨ 上の絵を 出す たびに ちがう 組から（8回：{starts}）')
        # 設定の タイル
        pg.evaluate("() => document.querySelector('.tabbar [data-tab=set]').click()"); pg.wait_for_timeout(800)
        pg.evaluate("() => { const t = document.querySelector('#setKisekae .kst[data-ks=news]'); if (t) t.scrollIntoView({ block: 'center' }); }"); pg.wait_for_timeout(1200)
        tl = pg.evaluate(CUR, '#setKisekae .kst[data-ks=news] .kslv .nsq')
        tsrc = pg.evaluate("() => (document.querySelector('#setKisekae .kst[data-ks=news] img.ksth') || {}).getAttribute && document.querySelector('#setKisekae .kst[data-ks=news] img.ksth').getAttribute('src')")
        pg.evaluate("() => { const s = document.createElement('style'); s.textContent = '#setKisekae .kslv .nsw .nsq{animation-duration:.25s!important}'; document.head.appendChild(s); }")
        wt = pg.evaluate(WATCH, ['#setKisekae .kst[data-ks=news] .kslv .nsq', 2500])
        check(bool(tl) and tl['an'] and tl['an'][0][0] == 'kpkbnsTk' and len(tl['n']) == 5 and len(wt['seen']) >= 5 and not wt['bad'] and tsrc == f'ks_{THUMB}.webp',
              f'⑨ 設定の 着せ替えの タイル（動く 壁紙 .kslv）でも 同じ：動き kpkbnsTk・数字が かわる（{len(wt["seen"]) - 1}回）・タイルの 絵は 新しい 止まった 絵')
        check(not errs and not bad, f'エラー なし・読めない 絵 なし {errs[:2]} {bad[:3]}')
        ctx.close(); br.close()
        if not HAVE_TC:
            print('※ トレーニングセンターの 絵（ios/tc_assets・tc_sign.webp）が ない ので、看板の 確かめは しない')
        else:
            tc_checks(p)
finally:
    srv.terminate()
shutil.rmtree(SRV, ignore_errors=True)
print('結果：', 'NG ' + str(len(fails)) if fails else 'OK')
sys.exit(1 if fails else 0)
