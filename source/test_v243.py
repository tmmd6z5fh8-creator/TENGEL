# 第4.243版の テスト（まさちゃん 2026/11/29 01:11・01:14）
#   ① 01:11「判定の画像読み込みの横にもビックリマークつけて、タップすると、どんな画像を読み込めばいいか(画像をつけて)、買い目予約の仕方(画像をつけて)、結果入力、結果記録の説明が出てくるようにして！」
#      判定の「オッズ画像から読み取る」の 横の 金の 丸の「！」（#ocrHelp）→ 使い方（pt_note.js の TengelHelp.open('judge')：① 読み込む 画像 ② 買い目予約 ③ 結果入力 ④ 結果記録・絵つき）
#   ② 同「作戦会議の画像読み込みの横にもビックリマークをつけて、タップするとどんな画像を読み込めばいいか(画像つけて)どんなことができるか画像つきで説明が出てくるようにして！」
#      作戦会議の「📷 画像から読み取る」の 横の「！」（.ocq）→ 使い方（読み込む 画像・作戦会議で できること・絵つき）。作戦会議（#planHost 90）の 上に 出る・入力中の 中身は 残る
#   ③ 01:14「トレーニングセンターの玉落とし抽選の横にもビックリマークをつけて、画像をつけて説明が出てくるようにして！確率とかはいらないから、何色が何に当選してるかとか！
#      激馬熱馬の当選した瞬間もちょっと紹介してほしい！ 基本的には画像付きでお願い！」
#      お世話チャレンジの 入口の 横の「！」（tc_care.js の PUSHG.dpq）・台の 上の「！ 遊び方」（tc_drop.js の HELPC）→ 遊び方（TengelHelp.open('drop')：遊び方・色と 当たり・激馬熱馬の 瞬間）。
#      色ごとの 当たりは tc_app.js の 数と 同じ・確率は 書かない。トレーニングセンター（#tcOv 90）の 上に 出る・閉じても 台は その まま
#   ④ 絵：help/img/hp_*.webp（help/help_art.py：架空の 画面と 今の アプリ）が App Store版の manual/ に 入る・大きさは pt_note.js の HPI と 同じ・Web版には 入らない
#   python3 test_v243.py   （SHOT=フォルダ で 画面を 写す）
import json, os, re, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
from PIL import Image
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
pn = open('pt_note.js', encoding='utf8').read()
hp = pn[pn.index('// ===================== 使い方'):]
HPI = json.loads(re.sub(r'(\w+):', r'"\1":', re.search(r'const HPI = (\{.*?\});', hp).group(1)))
imgs = {f[:-5]: Image.open(os.path.join('help', 'img', f)).size for f in sorted(os.listdir(os.path.join('help', 'img'))) if f.startswith('hp_') and f.endswith('.webp')}
used = sorted(set(re.findall(r"pic\('(hp_\w+)\.webp'", hp)))      # 名前は そのまま（app_unused.py が さがせる）
check(set(imgs) == set(used) == set(HPI) and all(list(imgs[k]) == HPI[k] for k in imgs),
      f'④ 絵（help/img）{len(imgs)}まい ＝ 使い方で 使う 絵 ＝ pt_note.js の HPI（大きさも 同じ）')
check(all(os.path.getsize(os.path.join('help', 'img', k + '.webp')) < 120 * 1024 for k in imgs) and sum(os.path.getsize(os.path.join('help', 'img', k + '.webp')) for k in imgs) < 700 * 1024,
      f'④ 絵は 小さい（1まい 120KB 未満・ぜんぶで {sum(os.path.getsize(os.path.join("help", "img", k + ".webp")) for k in imgs) // 1024}KB）')
check("window.TengelHelp = { open: hOpen, close: hClose" in hp and "const HELP = { judge: ['判定の 使い方', hJudge], plan: ['作戦会議の 使い方', hPlan], drop: ['お世話チャレンジの 遊び方', hDrop] };" in hp
      and "'#tgHelp{z-index:96}'" in hp and "CSS.replace(/#ptNote/g, ':is(#ptNote,#tgHelp)') + HCSS" in hp and "q.addEventListener('click', () => hOpen('judge', q));" in hp and "b.insertAdjacentElement('afterend', q);" in hp,
      '①②③ pt_note.js：TengelHelp（judge・plan・drop）・いちばん 上（z 96）・お知らせと 同じ 見た目（:is(#ptNote,#tgHelp)）・判定の「！」は ボタンの すぐ 横')
# 色ごとの 当たり：tc_app.js と 同じ 数（確率は 書かない）
tca = nocom(open('tc/tc_app.js', encoding='utf8').read())
rt = re.search(r"const RT = \{ normal: \[(\d+), (\d+)\], maboroshi: \[(\d+), (\d+)\], kamisama: \[(\d+), (\d+)\] \};", tca).groups()
zone = re.search(r"const ZONE = \{ d: \d+, start: (\d+), add: (\d+), rate: [\d.]+, max: (\d+) \};", tca).groups()
pts = sorted(int(x) for x in re.findall(r"\{ k: 'pt', v: (\d+) \}", tca[tca.index('const PRIZES = ['):tca.index('const RT = ')]))
pv = tca[tca.index('const PRIZES_VISIT = {'):tca.index('const AP = p =>')]
mab = [int(x) for x in re.findall(r"tier: 'maboroshi', v: \[(\d+), (\d+)\]", pv.split('kamisama:')[0]) for x in x]
kam = [int(x) for x in re.findall(r"tier: 'kamisama', v: \[(\d+), (\d+)\]", pv.split('kamisama:')[1]) for x in x]
geki = int(re.search(r"const GEKI = \{ d: \d+, v: (\d+) \};", tca).group(1))
dt = re.search(r"const dropTone = z => \((.*?)\);\n", tca).group(1)
f = lambda n: f'{n:,}'
want = {1: f'{pts[0]}P〜{pts[-1]}P', 2: f'{f(int(rt[0]))}P か {f(int(rt[1]))}P', 3: f'{f(int(rt[2]))}P か {f(int(rt[3]))}P', 4: f'{f(int(rt[4]))}P か {f(int(rt[5]))}P',
        5: f'{f(int(zone[0]))}P〜最大 {f(int(zone[0]) + int(zone[1]) * int(zone[2]))}P', 7: f'{f(geki)}P'}
dc = {int(c): v for c, v in re.findall(r"\{ c: (\d), n: '[^']+', k: '[^']*', v: '([^']*)'", hp)}
check(all(dc.get(c) == v for c, v in want.items()), f'③ 色と 当たり：tc_app.js の 数と 同じ {want}')
check(f'幻の馬ルーレット（{f(min(mab))}P〜{f(max(mab))}P）' in hp and f'神様馬ルーレット（{f(min(kam))}P〜{f(max(kam))}P）' in hp,
      f'③ 幻の馬・神様馬が 来て いる 間の ルーレット：金（{f(min(mab))}〜{f(max(mab))}P）・虹（{f(min(kam))}〜{f(max(kam))}P）')
check(dt == "!z ? 0 : z.k === 'gk' ? 7 : z.k === 'tk' ? 6 : z.k === 'zn' ? 5 : z.k === 'rt' ? (z.vis === 'kamisama' ? 6 : z.vis === 'maboroshi' ? 5 : z.tier === 'kamisama' ? 4 : z.tier === 'maboroshi' ? 3 : 2) : 1",
      '③ 色の 決め方（tc_app.js の dropTone）は 使い方と 同じ（はずれ 白・ポイント 青・ルーレット 緑／紫／赤・特化ゾーン 金・チケット扉 虹・激馬熱馬）')
hd = hp[hp.index('function hDrop()'):hp.index('const HELP = {')] + hp[hp.index('const DC = ['):hp.index('const RBG')]
check('確率' not in hd and not re.search(r'1/\d', hd) and '%' not in hd.replace('100%', '').replace("'%'", ''), '③ 遊び方に 確率は 書かない（1/○・％ なし）')
from assets_dir import adir
TCA = adir('tc_assets'); HAVE_TC = os.path.isfile(os.path.join(TCA, 'tc_dp.json')) and os.path.isfile(os.path.join(TCA, 'tc_dp_uma7.webp'))
if HAVE_TC:
    dj = json.load(open(os.path.join(TCA, 'tc_dp.json'), encoding='utf8'))
    dpg = re.search(r"const DPG = \{ img: \[(\d+), (\d+)\], lcd: \[([\d.]+), ([\d.]+), ([\d.]+), ([\d.]+)\], hold: \{ x: \[([\d., ]+)\], y: ([\d.]+), w: (\d+) \}, go: \[([\d, ]+)\], see: \[([\d, ]+)\] \};", hp).groups()
    num = lambda s: [float(x) for x in s.split(',')]
    check([float(x) for x in dpg[:2]] == dj['img'] and [float(x) for x in dpg[2:6]] == dj['lcd'] and num(dpg[6]) == dj['hold']['x'] and float(dpg[7]) == dj['hold']['y'] and float(dpg[8]) == dj['hold']['w']
          and num(dpg[9]) == dj['go']['box'] and num(dpg[10]) == dj['see']['box'], '③ 台の 絵の 置き方（DPG）は tc_dp.json と 同じ（馬バレ・保留・玉を落とす・保留結果を見る）')
tp = nocom(open('tc/tc_plan.js', encoding='utf8').read())
check('<div class="ocw"><button type="button" class="ocr" data-p="ocr">📷 画像から読み取る（3枚まで）</button>${window.TengelHelp ? \'<button type="button" class="ocq" data-p="help"' in tp
      and "if (k === 'help') { readForm(); if (window.TengelHelp) window.TengelHelp.open('plan', a); return; }" in tp, '② tc_plan.js：「📷 画像から読み取る」の 横の「！」→ 使い方（入力中の 中身は 残す）')
tcc = nocom(open('tc/tc_care.js', encoding='utf8').read())
check("dp: [158, 1556], dpw: 270, dph: 172, dpq: [318, 1490], dpqr: 25 };" in tcc and tcc.index("return 'pdq';") < tcc.index("return 'pdrop';")
      and "else if (what === 'pdq') { if (pushLive() && !S.fxHold && dropOk() && O.onDropHelp) { S.press.dpq = t; ev(t, 'button'); O.onDropHelp(); } }" in tcc, '③ tc_care.js：入口の 横の「！」（dpq）・入口より 先に 見る・押すと O.onDropHelp')
tcd = nocom(open('tc/tc_drop.js', encoding='utf8').read())
check("HELPC = { x: 343, y: 62, w: 170, h: 84 }" in tcd and "if (what === 'help') return pressHelp();" in tcd and "help: API && API.help ? [HELPC.x, HELPC.y] : null" in tcd and "chip(HELPC.x, HELPC.y, HELPC.w, HELPC.h, '遊び方', 34" in tcd,
      '③ tc_drop.js：台の 上の「！ 遊び方」（やめるの 右）・押すと api.help')
check("help: typeof window !== 'undefined' && window.TengelHelp ? () => { window.TengelHelp.open('drop'); } : null," in tca and "onDropHelp: window.TengelHelp ? () => { window.TengelHelp.open('drop'); } : null," in tca,
      '③ tc_app.js：台（DROP.help）と 入口（onDropHelp）→ TengelHelp.open(\'drop\')')
bp = open('build_pwa.py', encoding='utf8').read()
check("_hp = os.path.join(HERE, 'help', 'img')" in bp and "shutil.copy(os.path.join(_hp, _f), f'{out}/manual/{_f}')" in bp and bp.index("MAN_IMGS, MAN_VER = _bm.build(") < bp.index("_hp = os.path.join(HERE, 'help', 'img')"),
      '④ build_pwa.py：使い方の 絵を App Store版の manual/ に 入れる（説明書の あと）')
# 「！」の 場所：フィールド（PUSH の だ円に かからない・入口の 札の 右）・台（やめる と トークンの 札の あいだ）
G = {'x': 526, 'y': 1436, 'w': 360, 'ar': 646 / 660}
q = (318, 1490, 25)
edge = (((q[0] + q[2] + 3) - G['x']) / (G['w'] * 0.5 + 4)) ** 2 + ((q[1] - G['y']) / (G['w'] * G['ar'] * 0.5 + 4)) ** 2      # PUSH を 押せる だ円（＋4）
check(edge > 1 and q[0] - q[2] - 3 >= 158 + 135 - 6, f'③ 入口の 横の「！」は PUSH を 押せる だ円に かからない・入口の 札に ほとんど かからない（{edge:.2f}）')
check(343 - 85 > 122 + 22 + 102 and 343 + 85 < 1052 - 148 - 130, '③ 台の「！ 遊び方」は やめるの 札と トークンの 札の あいだ')

# ---------- アプリを 作る（App Store版・テスト版・Web版）----------
SRV = os.path.join(W, 'srv', 'v243'); PORT = 8874; URL = f'http://localhost:{PORT}/'
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
ENV = dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, HIST='hist_280.json', DROP='')
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict(ENV, TARGET='app'))
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'TEST')], check=True, stdout=subprocess.DEVNULL, env=dict(ENV, TARGET='app', TENGEL_TEST='1'))
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'WEB')], check=True, stdout=subprocess.DEVNULL, env=dict(ENV, TARGET='web'))
app = open(os.path.join(SRV, 'APP', 'index.html'), encoding='utf8').read(); web = open(os.path.join(SRV, 'WEB', 'index.html'), encoding='utf8').read()
tcb = open(os.path.join(SRV, 'APP', 'tc_bundle.js'), encoding='utf8').read()
man = lambda d: sorted(f[:-5] for f in os.listdir(os.path.join(SRV, d, 'manual')) if f.startswith('hp_'))
check('TengelHelp' in app and 'ocrHelp' in app and '#tgHelp{z-index:96}' in app and 'TengelHelp' not in web and 'ocrHelp' not in web,
      '①②③ App Store版の index.html に 使い方・判定の「！」／Web版には 入らない')
check(man('APP') == man('TEST') == sorted(imgs) and not os.path.isdir(os.path.join(SRV, 'WEB', 'manual')) or man('WEB') == [] if os.path.isdir(os.path.join(SRV, 'WEB', 'manual')) else man('APP') == sorted(imgs),
      f'④ 使い方の 絵 {len(imgs)}まい：App Store版・テスト版の manual/ に 入る・Web版には 入らない')
check("'pdq'" in tcb and 'HELPC' in tcb and "window.TengelHelp.open('drop')" in tcb and "data-p=\"help\"" in tcb, '③② tc_bundle.js：入口の「！」・台の「！ 遊び方」・作戦会議の「！」')
for d in ('APP', 'TEST'):
    p = os.path.join(SRV, d, 'index.html'); h = open(p, encoding='utf8').read()
    assert "window.__NATIVE = location.protocol === 'tengel:';" in h
    open(p, 'w', encoding='utf8').write(h.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
    if HAVE_TC:
        for f_ in os.listdir(TCA): shutil.copy(os.path.join(TCA, f_), os.path.join(SRV, d, f_))
NT = open(os.path.join(W, 'test_native.py'), encoding='utf8').read()
FAKE_N = re.search(r'\nFAKE = """(.*?)"""', NT, re.S).group(1)
FAKE_T = open(os.path.join(W, 'test_tc.py'), encoding='utf8').read().split('FAKE = """')[1].split('"""')[0]
GATE_GONE = "() => { const g = document.querySelector('#gate'); return !g || g.hidden || getComputedStyle(g).display === 'none'; }"
HINFO = """() => { const o = document.getElementById('tgHelp'); if (!o) return null; const cs = getComputedStyle(o), t = s => [...o.querySelectorAll(s)].map(e => e.textContent.trim()), bd = o.querySelector('.pnbd');
  const im = [...o.querySelectorAll('.hpf > img')];
  return { kind: o.dataset.kind, z: +cs.zIndex, ff: cs.fontFamily, bg: cs.backgroundColor, h2: t('h2'), sec: t('.pnsec'), h3: t('h3'), txt: o.innerText, act: document.activeElement && document.activeElement.className,
    imgs: im.map(i => i.getAttribute('src')), ok: im.filter(i => i.complete && i.naturalWidth > 0).length, ar: im.map(i => Math.abs(i.getBoundingClientRect().height - i.getBoundingClientRect().width * i.naturalHeight / Math.max(1, i.naturalWidth)) < 1.5),
    wide: bd.scrollWidth <= bd.clientWidth + 1, mson: document.documentElement.classList.contains('mson'), rows: o.querySelectorAll('.hpc').length,
    pin: Math.round(o.querySelector('.pnin').getBoundingClientRect().width), g2: [...o.querySelectorAll('.hpg2')].map(g => { const f = g.querySelectorAll('.hpf'); return f.length === 2 && Math.abs(f[0].getBoundingClientRect().top - f[1].getBoundingClientRect().top) < 1; }) }; }"""
errs = []


def boot(pg, d):
    pg.goto(URL + d + '/'); pg.wait_for_timeout(1500)
    if pg.locator('#gateGo').count(): pg.click('#gateGo'); pg.wait_for_timeout(700)
    pg.wait_for_function(GATE_GONE, timeout=15000); pg.wait_for_timeout(800)


srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
try:
    with sync_playwright() as p:
        br = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'])
        # ===== ① 判定の「！」=====
        for (vw, vh, tag) in ((390, 844, 'iphone'), (320, 640, 'se'), (820, 1180, 'ipad')):
            c = br.new_context(viewport={'width': vw, 'height': vh}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo', has_touch=True, is_mobile=tag != 'ipad')
            c.add_init_script(FAKE_N)
            pg = c.new_page(); e1 = []; pg.on('pageerror', lambda e: e1.append(str(e)))
            boot(pg, 'APP'); pg.wait_for_function("() => { const r = document.querySelector('#ocrRow'); return r && !r.hidden; }", timeout=20000); pg.wait_for_timeout(300)
            L = pg.evaluate("""() => { const q = document.getElementById('ocrHelp'), b = document.getElementById('ocrBtn'), R = e => { const r = e.getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom]; }, cs = getComputedStyle(q);
              return { q: R(q), b: R(b), next: b.nextElementSibling === q, txt: q.textContent, al: q.getAttribute('aria-label'), bg: cs.backgroundImage, w: q.offsetWidth, h: q.offsetHeight, row: q.parentElement.id }; }""")
            mid = lambda r: (r[1] + r[3]) / 2
            check(L['next'] and L['row'] == 'ocrRow' and L['txt'] == '!' and L['w'] == 34 and L['h'] == 34 and 'linear-gradient' in L['bg'] and L['q'][0] >= L['b'][2] and L['q'][0] - L['b'][2] < 14 and abs(mid(L['q']) - mid(L['b'])) < 2
                  and L['q'][2] <= vw, f'① [{tag}] 「オッズ画像から読み取る」の すぐ 右に 金の 丸の「！」（34px・高さの まん中が そろう）{[round(v) for v in L["q"]]} {[round(v) for v in L["b"]]}')
            pg.click('#ocrHelp'); pg.wait_for_timeout(1500)
            i1 = pg.evaluate(HINFO)
            check(i1 and i1['kind'] == 'judge' and i1['z'] == 96 and i1['h2'] == ['画像を 読み込んで 判定 → 予約 → 記録！'] and i1['sec'] == ['① 読み込む 画像', '② 買い目予約', '③ 結果入力', '④ 結果記録'] and i1['mson'],
                  f'① [{tag}] 「！」→ 判定の 使い方（① 読み込む 画像 ② 買い目予約 ③ 結果入力 ④ 結果記録）・いちばん 上（z 96）')
            check(i1['imgs'] == ['manual/hp_odds.webp', 'manual/hp_tri.webp', 'manual/hp_ocr.webp', 'manual/hp_buy.webp', 'manual/hp_rsv.webp', 'manual/hp_res.webp', 'manual/hp_pay.webp', 'manual/hp_rec.webp', 'manual/hp_stat.webp']
                  and i1['ok'] == 9 and all(i1['ar']), f'① [{tag}] 絵 9まい（単勝の 画面・3連単の 人気順・読み込んだ あと・買い目・結果待ち・1〜3着・金額・記録・実測回収）が 出る・形の まま {i1["ok"]}')
            check('同じ レースの スクショを 1〜3枚' in i1['txt'] and '買い目を予約' in i1['txt'] and '結果を決める' in i1['txt'] and '記録する' in i1['txt'] and '1レース 800P' in i1['txt'] and '実測・回収' in i1['txt'],
                  f'① [{tag}] 中身：1〜3枚・「買い目を予約」・「結果を決める」・「記録する」・読み込みは 800P・実測・回収')
            check(i1['wide'] and i1['g2'] == [True], f'① [{tag}] 横に はみ出さない・見本の 画面 2まいは 横に 並ぶ（{vw}px）')
            if tag == 'ipad': check(i1['pin'] == 560, f'① [iPad] 中身の 幅 560px（説明書と 同じ）{i1["pin"]}')
            shot(pg, f'v243_judge_{tag}')
            if tag == 'iphone':
                hh = pg.evaluate("() => document.querySelector('#tgHelp .pnbd').scrollHeight")
                for k in range(0, min(hh, 9000), 760):
                    pg.evaluate("(y) => { document.querySelector('#tgHelp .pnbd').scrollTop = y; }", k); pg.wait_for_timeout(250); shot(pg, f'v243_judge_s{k // 760:02d}')
            pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
            a1 = pg.evaluate("() => ({ open: !!document.getElementById('tgHelp'), mson: document.documentElement.classList.contains('mson'), f: document.activeElement && document.activeElement.id })")
            pg.click('#ocrHelp'); pg.wait_for_timeout(500); pg.click('#tgHelp .pnx'); pg.wait_for_timeout(300); a2 = pg.evaluate("() => !!document.getElementById('tgHelp')")
            pg.click('#ocrHelp'); pg.wait_for_timeout(500); pg.click('#tgHelp .pnfoot [data-hp=close]'); pg.wait_for_timeout(300); a3 = pg.evaluate("() => !!document.getElementById('tgHelp')")
            check(not a1['open'] and not a1['mson'] and a1['f'] == 'ocrHelp' and not a2 and not a3, f'① [{tag}] Esc・✕・「閉じる」で 閉じる・「！」に フォーカスが もどる・後ろが 動く {a1}')
            # ポイントの お知らせ（同じ 見た目の 窓）：前と 同じ（z 72）・両方 開いても 使い方が 上
            pg.evaluate("() => TengelPtNote.open()"); pg.wait_for_timeout(600); pg.click('#ocrHelp', force=True) if False else pg.evaluate("() => TengelHelp.open('judge')"); pg.wait_for_timeout(600)
            zz = pg.evaluate("() => [+getComputedStyle(document.getElementById('ptNote')).zIndex, +getComputedStyle(document.getElementById('tgHelp')).zIndex, (() => { const e = document.elementFromPoint(innerWidth / 2, innerHeight / 2); return !!e && !!e.closest('#tgHelp'); })(), getComputedStyle(document.getElementById('ptNote')).backgroundColor]")
            pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
            z2 = pg.evaluate("() => [!!document.getElementById('tgHelp'), !!document.getElementById('ptNote')]")
            pg.evaluate("() => TengelPtNote.close()"); pg.wait_for_timeout(200)
            check(zz[0] == 72 and zz[1] == 96 and zz[2] and zz[3] == 'rgb(10, 27, 34)' and z2 == [False, True], f'① [{tag}] ポイントの お知らせ（z 72・同じ 色）の 上に 使い方（z 96）・Esc は 上の 使い方 だけ 閉じる {zz} {z2}')
            check(not e1, f'① [{tag}] エラー なし {e1[:2]}')
            c.close()

        # ===== ② 作戦会議の「！」=====
        for (vw, vh, tag) in ((390, 844, 'iphone'), (820, 1180, 'ipad')):
            c = br.new_context(viewport={'width': vw, 'height': vh}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo', has_touch=True, is_mobile=tag != 'ipad')
            c.add_init_script(FAKE_N)
            pg = c.new_page(); e2 = []; pg.on('pageerror', lambda e: e2.append(str(e)))
            boot(pg, 'APP')
            pg.evaluate("() => { localStorage.removeItem('tengel.plan'); window.TCPlanOpen(); }")
            pg.wait_for_function("() => document.querySelector('#tcPlan [data-p=add]')", timeout=60000); pg.wait_for_timeout(400)
            pg.locator('#tcPlan [data-p=add]').first.click(); pg.wait_for_timeout(400)
            pg.locator('#tcPlan [data-f=name]').fill('テンゲル特別')
            L = pg.evaluate("""() => { const q = document.querySelector('#tcPlan .ocq'), b = document.querySelector('#tcPlan .ocr'), R = e => { const r = e.getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom]; };
              return { q: R(q), b: R(b), same: q.parentElement === b.parentElement && q.parentElement.className === 'ocw', txt: q.textContent, w: q.offsetWidth, hint: !!document.querySelector('#tcPlan .ocw + .ocrh') }; }""")
            check(L['same'] and L['txt'] == '!' and L['w'] == 40 and L['q'][0] >= L['b'][2] and L['q'][0] - L['b'][2] < 12 and abs(mid(L['q']) - mid(L['b'])) < 2 and L['hint'],
                  f'② [{tag}] 「📷 画像から読み取る」の すぐ 右に「！」（40px・高さの まん中が そろう）・下の 説明は そのまま {[round(v) for v in L["q"]]}')
            pg.locator('#tcPlan .ocq').click(); pg.wait_for_timeout(1500)
            i2 = pg.evaluate(HINFO)
            top = pg.evaluate("() => { const e = document.elementFromPoint(innerWidth / 2, innerHeight / 2); return [!!e && !!e.closest('#tgHelp'), +getComputedStyle(document.getElementById('planHost')).zIndex]; }")
            check(i2 and i2['kind'] == 'plan' and i2['z'] == 96 and top[0] and top[1] == 90 and i2['sec'] == ['読み込む 画像', '作戦会議で できること'] and i2['h2'] == ['出馬表の 画像で やりたい レースを 予約！'],
                  f'② [{tag}] 「！」→ 作戦会議の 使い方（読み込む 画像・作戦会議で できること）が 作戦会議（z {top[1]}）の 上')
            check(i2['imgs'] == ['manual/hp_card.webp', 'manual/hp_odds.webp', 'manual/hp_pform.webp', 'manual/hp_plan.webp', 'manual/hp_oshi.webp'] and i2['ok'] == 5 and all(i2['ar']) and i2['wide'] and i2['g2'] == [True],
                  f'② [{tag}] 絵 5まい（出馬表・オッズの 画面・予約の 欄・レースの ボード・推し馬）・横に はみ出さない')
            check('20・15・10・8・5分前' in i2['txt'] and '推し馬を 25頭まで 登録' in i2['txt'] and 'ポイントは 使わないよ' in i2['txt'] and 'やりたいレースを予約！' in i2['txt'],
                  '② 中身：通知（20・15・10・8・5分前）・推し馬 25頭・ポイントは 使わない・上の「やりたいレースを予約！」')
            shot(pg, f'v243_plan_{tag}')
            if tag == 'iphone':
                hh = pg.evaluate("() => document.querySelector('#tgHelp .pnbd').scrollHeight")
                for k in range(0, min(hh, 6000), 760):
                    pg.evaluate("(y) => { document.querySelector('#tgHelp .pnbd').scrollTop = y; }", k); pg.wait_for_timeout(250); shot(pg, f'v243_plan_s{k // 760:02d}')
            pg.click('#tgHelp .pnx'); pg.wait_for_timeout(300)
            a = pg.evaluate("() => ({ open: !!document.getElementById('tgHelp'), name: document.querySelector('#tcPlan [data-f=name]').value, form: !!document.querySelector('#tcPlan .fm'), f: document.activeElement && document.activeElement.className })")
            check(not a['open'] and a['name'] == 'テンゲル特別' and a['form'] and a['f'] == 'ocq', f'② [{tag}] 閉じると 作戦会議の 予約の 欄に もどる（入れた 名前は そのまま・「！」に フォーカス）{a}')
            check(not e2, f'② [{tag}] エラー なし {e2[:2]}')
            c.close()

        # ===== ③ トレーニングセンターの お世話チャレンジ（玉落とし）=====
        c = br.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo', has_touch=True, is_mobile=True)
        c.add_init_script(FAKE_T)
        pg = c.new_page(); e3 = []; pg.on('pageerror', lambda e: e3.append(str(e)))
        boot(pg, 'APP')
        pg.evaluate("() => TengelHelp.open('drop')"); pg.wait_for_timeout(1500)
        i3 = pg.evaluate(HINFO)
        dd = pg.evaluate("""() => { const o = document.getElementById('tgHelp'), rows = [...o.querySelectorAll('.hpc')];
          return { rows: rows.map(r => [+r.dataset.c, r.querySelector('.hpct b').textContent, r.querySelector('.hpct span').textContent]),
            uma: [...o.querySelectorAll('.hpu img')].filter(i => i.complete && i.naturalWidth > 0).length, hold: [...o.querySelectorAll('.hph img')].filter(i => i.complete && i.naturalWidth > 0).length,
            boards: [...o.querySelectorAll('.hpbd')].map(b => b.classList.contains('hpnone') ? 'none' : (b.querySelector('.hpbase').complete && b.querySelector('.hpbase').naturalWidth > 0 ? 'ok' : '?')),
            mk: o.querySelectorAll('.hpmk').length, dim: o.querySelectorAll('.hpbd .hpdim').length, st: [...o.querySelectorAll('.hpst b')].map(e => e.textContent), end: !!o.querySelector('.hpend'), big: (o.querySelector('.hpbig') || {}).textContent }; }""")
        check(i3 and i3['kind'] == 'drop' and i3['z'] == 96 and i3['sec'] == ['遊び方', '色と 当たり', '激馬熱馬の 瞬間'] and i3['h2'] == ['玉の 光る 色で 当たりが わかる！'] and i3['wide'],
              '③ 遊び方（遊び方・色と 当たり・激馬熱馬の 瞬間）・いちばん 上・横に はみ出さない')
        check([r[1] for r in dd['rows']] == ['白', '青', '緑', '紫', '赤', '金', '虹', '激馬熱馬'] and dd['rows'][6][2] == 'チケット扉：壁紙チケット か 7,000P' and dd['rows'][1][2] == 'ポイント：10P〜300P'
              and dd['rows'][7][2] == '40,000P' and dd['mk'] == 4 and dd['dim'] == 1 and dd['st'] == ['赤と 金の プチュン！', '真っ暗…', '激馬熱馬！'] and dd['big'] == '40,000P 獲得！',
              f'③ 色と 当たり 8つ（白 ハズレ〜激馬熱馬 40,000P）・台の 番号 ①〜④・激馬熱馬の 瞬間（プチュン → 真っ暗 → 激馬熱馬）・40,000P 獲得')
        check('確率' not in i3['txt'] and not re.search(r'1/\d', i3['txt']) and '%' not in i3['txt'], '③ 遊び方に 確率は ない')
        if HAVE_TC: check(dd['uma'] == 7 and dd['hold'] == 7 and dd['boards'] == ['ok', 'ok'], f'③ 絵：馬バレ 7・保留 7・台の 絵 2つ（遊び方・激馬熱馬の 瞬間）{dd["uma"]} {dd["hold"]} {dd["boards"]}')
        else: check(dd['boards'] == ['none', 'none'] and dd['rows'] and i3['wide'], '③ 絵が ない（CI と 同じ）ときも 色の 丸と 字で 出る')
        shot(pg, 'v243_drop')
        hh = pg.evaluate("() => document.querySelector('#tgHelp .pnbd').scrollHeight")
        for k in range(0, min(hh, 9000), 760):
            pg.evaluate("(y) => { document.querySelector('#tgHelp .pnbd').scrollTop = y; }", k); pg.wait_for_timeout(300); shot(pg, f'v243_drop_s{k // 760:02d}')
        pg.evaluate("() => TengelHelp.close()"); pg.wait_for_timeout(200)
        if HAVE_TC:
            from toys_for_test import open_toys
            open_toys(pg, ('drop',))
            pg.evaluate("() => document.querySelectorAll('.tabbar button')[2].click()"); pg.wait_for_timeout(300)
            pg.locator('#tcFab').click()
            pg.wait_for_function("() => window.TCApp && TCApp.state && window.TCCare && TCCare.on && !document.querySelector('#tcOv .tcld')", timeout=90000); pg.wait_for_timeout(1000)
            pg.wait_for_function("() => window.TCDrop && TCDrop.ready()", timeout=30000)
            pg.evaluate("() => { const S = TCCare.S, s = TCApp.state; S.stock = 8; S.stockShow = 8; s.stock = 8; }")
            pg.evaluate("() => { const S = TCCare.S; if (!(S.push && S.push.hideT == null)) TCCare.pushShow(S.lastT + 0.05); }"); pg.wait_for_timeout(1800)
            st = pg.evaluate("() => { const b = document.querySelector('#tcOv .tcst').getBoundingClientRect(); return [b.left, b.top, b.width, b.height]; }")
            G2 = pg.evaluate("() => TCCare.PUSHG")
            tap = lambda x, y: pg.mouse.click(st[0] + x / 1052 * st[2], st[1] + y / 1657 * st[3])
            shot(pg, 'v243_push')
            tap(*G2['dpq']); pg.wait_for_timeout(1200)
            f1 = pg.evaluate("() => ({ help: !!document.getElementById('tgHelp'), kind: window.TengelHelp && TengelHelp.kind(), tc: !!(window.TCCare && TCCare.on), drop: TCDrop.isOpen(), top: (() => { const e = document.elementFromPoint(innerWidth / 2, innerHeight / 2); return !!e && !!e.closest('#tgHelp'); })(), z: +getComputedStyle(document.getElementById('tcOv')).zIndex })")
            shot(pg, 'v243_push_help')
            pg.keyboard.press('Escape'); pg.wait_for_timeout(400)
            f2 = pg.evaluate("() => ({ help: !!document.getElementById('tgHelp'), tc: !!(window.TCCare && TCCare.on), push: !!(TCCare.S.push && TCCare.S.push.hideT == null), drop: TCDrop.isOpen() })")
            check(f1['help'] and f1['kind'] == 'drop' and f1['tc'] and not f1['drop'] and f1['top'] and f1['z'] == 90 and not f2['help'] and f2['tc'] and f2['push'] and not f2['drop'],
                  f'③ フィールド：お世話チャレンジの 入口の 横の「！」→ 遊び方（トレーニングセンター z 90 の 上）→ 閉じると PUSH の 画面の まま（台は 開かない）{f1} {f2}')
            # 台の 上の「！ 遊び方」
            pg.evaluate("() => { TCApp._t.dropOpen(false); }"); pg.wait_for_timeout(3000)
            gg = pg.evaluate("() => TCDrop.geo()")
            shot(pg, 'v243_board')
            tap(*gg['help']); pg.wait_for_timeout(1200)
            b1 = pg.evaluate("() => ({ help: !!document.getElementById('tgHelp'), kind: window.TengelHelp && TengelHelp.kind(), drop: TCDrop.isOpen(), phase: TCDrop.info().phase })")
            pg.click('#tgHelp .pnx'); pg.wait_for_timeout(400)
            b2 = pg.evaluate("() => ({ help: !!document.getElementById('tgHelp'), drop: TCDrop.isOpen(), phase: TCDrop.info().phase })")
            check(gg['help'] and b1['help'] and b1['kind'] == 'drop' and b1['drop'] and b1['phase'] == 'ready' and not b2['help'] and b2['drop'] and b2['phase'] == 'ready',
                  f'③ 台：「やめる」の 右の「！ 遊び方」→ 遊び方 → 閉じても 台は その まま（玉を 落とせる）{gg["help"]} {b1} {b2}')
            ok_q = pg.evaluate("() => TCDrop.tap('quit')"); pg.wait_for_timeout(800)
            check(ok_q and not pg.evaluate("() => TCDrop.isOpen()"), '③ 台の「やめる」は 今までどおり（閉じる）')
        check(not e3, f'③ エラー なし {e3[:2]}')
        c.close()
        br.close()
finally:
    srv.terminate()
shutil.rmtree(SRV, ignore_errors=True)
# ---------- GitHub の Mac（selftest.js の help・run.sh の HELPPY・P1 の 印）----------
st = open(os.path.join(W, 'ios', 'ci', 'selftest.js'), encoding='utf8').read(); rs = open(os.path.join(W, 'ios', 'ci', 'run.sh'), encoding='utf8').read()
if "step(R, 'help'" in st:
    check(st.index("step(R, 'ptNote'") < st.index("step(R, 'help'") < st.index("step(R, 'manualOv'") and "await mark('help-judge');" in st and "await mark('help-plan');" in st and "await mark('help-drop');" in st
          and ' pt-note pt-note-shop help-judge help-plan help-drop manual-ov ' in rs and 'help: $(python3 -c "$HELPPY"' in rs and 'help (ipad): $(python3 -c "$HELPPY"' in rs,
          '⑤ selftest.js の help（お知らせと 説明書の あいだ・印 help-judge → help-plan → help-drop）・run.sh の HELPPY の 行（iPhone・iPad）・P1 の 印の 順')
    pya = re.search(r"\nHELPPY='\n(.*?)\n'\n", rs, re.S).group(1)
    J = {'open': True, 'z': 96, 'secs': ['① 読み込む 画像', '② 買い目予約', '③ 結果入力', '④ 結果記録'], 'imgs': 9, 'ok': 9, 'rows': 0, 'wide': True}
    P2 = {'open': True, 'z': 96, 'secs': ['読み込む 画像', '作戦会議で できること'], 'imgs': 5, 'ok': 5, 'rows': 0, 'wide': True}
    Dd = {'open': True, 'z': 96, 'secs': ['遊び方', '色と 当たり', '激馬熱馬の 瞬間'], 'imgs': 0, 'ok': 0, 'rows': 8, 'wide': True}
    good = {'help': {'api': True, 'q': [262, 330, 296, 364], 'ob': [16, 330, 250, 364], 'qTxt': '!', 'judge': J, 'plan': P2, 'drop': Dd, 'closed': True}}
    tmp = os.path.join(W, 't4', '_helppy.json'); os.makedirs(os.path.dirname(tmp), exist_ok=True)

    def runpy(d):
        json.dump(d, open(tmp, 'w', encoding='utf8')); return subprocess.run(['python3', '-c', pya, tmp], capture_output=True, text=True).stdout.strip()
    r1 = runpy(good)
    bad1 = json.loads(json.dumps(good)); bad1['help']['judge']['ok'] = 7                        # 絵が 出ない
    bad2 = json.loads(json.dumps(good)); bad2['help']['q'] = [262, 380, 296, 414]                # 「！」が ボタンと ずれた
    ok3 = json.loads(json.dumps(good)); ok3['help']['q'] = None; ok3['help']['ob'] = None         # 読み取りの 行が かくれて いる（読み取れない 端末）
    r2, r3, r4 = runpy(bad1), runpy(bad2), runpy(ok3)
    check(r1.endswith('-> OK') and 'CHECK' in r2 and 'CHECK' in r3 and r4.endswith('-> OK'), f'⑤ HELPPY：よい 形 → OK・絵が 出ない／「！」が ずれた → CHECK・読み取りの 行が ない → OK {r1[-40:]!r}')
else:
    check(False, '⑤ selftest.js に help の 手順が ない')
print('FAILS', len(fails), fails)
sys.exit(1 if fails else 0)
