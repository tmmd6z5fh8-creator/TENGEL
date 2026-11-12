# ルーレットの 絵（第4.158版・まさちゃん 2026/11/12 08:59「このルーレットの神様馬、目が怖いから金色に光らせて！あと、画像がなんかまだらに色がついてるから綺麗にできる？」・
#   09:00「幻の馬のルーレットは、目を紫に光らせて！」）
#   python3 test_rt_art.py   （ios/tc_assets/ が ある とき だけ。ない とき（CI）は コードと 台帳の 確かめ だけ）
#   ・コード：アプリ（tc/tc_fx.js）は 新しい 絵（rt_<絵>_<部品>2.webp）を 読む（ない とき だけ 前の 絵）・目の 場所は 絵を 作る 道具（kisekae/tc/rt_clean.py の EYE）と 同じ・
#     目の 光は ゆっくり（2.4秒で 1回）・前の 絵は アプリにも 軽い 版にも 入れない（assets_dir.superseded）
#   ・もとの 絵（マスター）：前の 絵 12まいは 消して いない・1バイトも かわって いない（新しい 絵は 別の 名前で 足した）
#   ・新しい 絵 12まい（ノーマル・幻の馬・神様馬 × 台紙・レバーの 玉・レバーの 棒・矢印）：大きさと 形（すき通し）は 前と 同じ・
#     **まだら（紙の もよう）が 半分より 小さい**・折り目と ふちは のこって いる・面の 色は かわらない
#   ・目：神様馬＝金色の 光・幻の馬＝紫の 光（前は 暗い 色の ひとみ）。ノーマルには 目の 光を 足して いない
#   ・軽い 版（アプリに 入る 絵）：新しい 12まい だけ（前の 12まいは ない）・中身は もとと 同じ
#   ・絵（まさちゃんの もとの 絵・作った 絵）は リポジトリに 入って いない
#   ・アプリの 画面：新しい 絵が 読めない とき だけ 前の 絵で 出る（絵が 出ない ままに ならない）・読める ときは 新しい 絵 だけ
import hashlib, json, os, re, subprocess, sys
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
sys.path.insert(0, W); sys.path.insert(0, os.path.join(W, 'kisekae', 'tc'))
import assets_dir
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label)
    if not c:
        fails.append(label)


THEMES = ('normal', 'maboroshi', 'kamisama'); PARTS = ('plate', 'knob', 'stick', 'ptr')
OLD = {'rt_kamisama_knob.webp': 'ea48a2c6effa067e3db133a51a11a445', 'rt_kamisama_plate.webp': 'd3736e54e31724e310b0759754031080', 'rt_kamisama_ptr.webp': 'b1cb0283fc5f9b7dfaa579adbbfcea12',
       'rt_kamisama_stick.webp': '8e00496018620800e2c62780f337bbb0', 'rt_maboroshi_knob.webp': 'b9064a065bf12e7d5d84977802a8b570', 'rt_maboroshi_plate.webp': 'a7225b5271871425ec3e6c367ec50d81',
       'rt_maboroshi_ptr.webp': 'f579e546a61e16a6516cd141eee095a3', 'rt_maboroshi_stick.webp': '9d78e639cf16cc29764475aa186f7cc9', 'rt_normal_knob.webp': '3fa10076870adaa943b900e13ee3f577',
       'rt_normal_plate.webp': '8c1c554d741f3f5daff49573f364963a', 'rt_normal_ptr.webp': '7757bca55e2b6309c5cd270cad024871', 'rt_normal_stick.webp': '48c0ae1ea8a21b78aa4e3a78fd468f49'}      # 前の 絵（第4.157版まで）の md5
NEW = [f'rt_{t}_{p}2.webp' for t in THEMES for p in PARTS]
print('■ コード')
fx = open(os.path.join(W, 'tc', 'tc_fx.js'), encoding='utf8').read()
tool = open(os.path.join(W, 'kisekae', 'tc', 'rt_clean.py'), encoding='utf8').read()
eye_js = {m.group(1): [float(v) for v in m.group(2).split(',')] for m in re.finditer(r"(\w+): \{ glow: [^}]*?eye: \[([^\]]+)\]", fx)}
eye_py = {m.group(1): (float(m.group(2)), float(m.group(3)), m.group(4)) for m in re.finditer(r"'(\w+)': dict\(c=\(([\d.]+), ([\d.]+)\), kind='(\w+)'\)", tool)}
check('I[p] = await img(`rt_${th}_${p}2.webp`) || await img(`rt_${th}_${p}.webp`)' in fx and fx.count('`rt_${th}_${p}.webp`') == 1 and sorted(eye_js) == ['kamisama', 'maboroshi'] and 'drawEye(r, u)' in fx
      and all(abs(eye_js[k][0] - eye_py[k][0]) < 0.01 and abs(eye_js[k][1] - eye_py[k][1]) < 0.01 for k in eye_js) and eye_py['kamisama'][2] == 'gold' and eye_py['maboroshi'][2] == 'purple',
      f'アプリは 新しい 絵（rt_<絵>_<部品>2.webp）を 読む（ない とき だけ 前の 絵＝絵が 出ない ままに ならない）・目の 光は 神様馬と 幻の馬 だけ（ノーマルは なし）・目の 場所は 絵を 作る 道具と 同じ（{ {k: v[:2] for k, v in eye_js.items()} }）')
gold, purple = eye_js.get('kamisama', [0] * 5)[2:], eye_js.get('maboroshi', [0] * 5)[2:]
per = re.search(r'Math\.sin\(TAU \* u / ([\d.]+)', fx[fx.index('function drawEye'):fx.index('function drawEye') + 600])
check(gold[0] >= 240 and gold[0] - gold[2] >= 120 and gold[1] - gold[2] >= 80 and purple[2] >= 240 and purple[2] - purple[1] >= 100 and purple[0] - purple[1] >= 40 and per and float(per.group(1)) >= 2.0,
      f'目の 光の 色：神様馬＝金（{gold}）・幻の馬＝紫（{purple}）・ゆっくり 息を する（{per and per.group(1)}秒で 1回＝ちかちか しない）')
fs = set(OLD) | set(NEW) | {'tc_bg_morning.webp', 'tc_se_flop.m4a'}
sup = assets_dir.superseded('tc_assets', fs)
check(set(OLD) <= sup and not (set(NEW) & sup) and 'tc_bg_morning.webp' not in sup and assets_dir.superseded('tc_assets', set(OLD)) == set()
      and assets_dir.superseded('tc_assets', {'rt_normal_plate.webp', 'rt_normal_plate2.webp', 'rt_normal_knob.webp'}) == {'rt_normal_plate.webp'},
      '前の 絵は アプリにも 軽い 版にも 入れない（assets_dir.superseded）：新しい 絵が ある 部品 だけ（新しい 絵が ない 部品の 前の 絵は そのまま 入る＝絵が 消えない）')
gi = subprocess.run(['git', 'ls-files'], capture_output=True, text=True, cwd=W).stdout.split('\n')
check('kisekae/tc/rt_clean.py' in gi and not any(re.search(r'(^|/)rt_[a-z]+(_[a-z]+2?)?\.(webp|png)$', f) for f in gi) and not any(f.startswith('ios/tc_assets/') or f.startswith('ios/lite/') for f in gi),
      '絵を 作る 道具（kisekae/tc/rt_clean.py）は リポジトリに ある・絵（まさちゃんの もとの 絵・作った 絵）は 入って いない')
M = assets_dir.master('tc_assets')
if not os.path.isdir(M) or not all(os.path.isfile(os.path.join(M, f)) for f in NEW):
    print('※ ルーレットの 絵（ios/tc_assets）が ない ので、絵の 確かめは しない')
    print('結果：', 'NG ' + str(len(fails)) if fails else 'OK'); sys.exit(1 if fails else 0)
import numpy as np, cv2
from PIL import Image
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
print('■ もとの 絵（マスター）')
bad = [f for f, h in OLD.items() if not os.path.isfile(os.path.join(M, f)) or md5(os.path.join(M, f)) != h]
check(not bad, f'前の 絵 12まいは 消して いない・1バイトも かわって いない（新しい 絵は 別の 名前で 足した）{bad[:3] if bad else ""}')
load = lambda f, d=M: np.array(Image.open(os.path.join(d, f)).convert('RGBA'))
rows, ok_shape, ok_clean, ok_fold, ok_col = [], [], [], [], []
for th in THEMES:
    for p in PARTS:
        o, n = load(f'rt_{th}_{p}.webp'), load(f'rt_{th}_{p}2.webp')
        if o.shape != n.shape:
            ok_shape.append(False); continue
        ao, an = o[..., 3].astype(np.int32), n[..., 3].astype(np.int32)
        ok_shape.append(Image.open(os.path.join(M, f'rt_{th}_{p}2.webp')).format == 'WEBP' and np.abs(ao - an).mean() < 0.05 and np.abs(ao - an).max() <= 2 and ((ao > 128) != (an > 128)).mean() < 1e-4)
        go, gn = (cv2.cvtColor(v[..., :3], cv2.COLOR_RGB2GRAY).astype(np.float32) for v in (o, n))
        mag = lambda g: np.hypot(cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3), cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)) / 4
        mo, mn = mag(go), mag(gn)
        solid = cv2.erode((ao > 250).astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
        flat = solid & ~(cv2.dilate((mo > 14).astype(np.uint8), np.ones((9, 9), np.uint8)) > 0)          # 面の 中（折り目・ふちから はなれた 所）
        hp = lambda g: np.abs(g - cv2.GaussianBlur(g, (0, 0), 2.0))[flat].mean()                        # まだら（こまかい 明るさの むら）
        fo, fn = hp(go), hp(gn)
        strong = solid & (mo > 40)                                                                      # 折り目・ふち
        keep = float(mn[strong].mean() / mo[strong].mean())
        bo, bn = (cv2.GaussianBlur(v[..., :3].astype(np.float32), (0, 0), 12) for v in (o, n))
        shift = float(np.abs(bo - bn).max(-1)[solid].mean())
        ok_clean.append(fn / fo <= 0.5); ok_fold.append(keep >= 0.78); ok_col.append(shift < 2.0)
        rows.append((th, p, fn / fo, keep, shift))
print('■ 新しい 絵（12まい）')
check(len(ok_shape) == 12 and all(ok_shape), '大きさと 形（すき通し）は 前の 絵と 同じ（WebP・すき通しの ちがい 2/255 まで）')
check(len(ok_clean) == 12 and all(ok_clean), f'**まだら（面の 中の こまかい 明るさの むら）が 半分より 小さい**：前の {min(r[2] for r in rows) * 100:.0f}〜{max(r[2] for r in rows) * 100:.0f}%（台紙：' + '・'.join(f'{r[0]} {r[2] * 100:.0f}%' for r in rows if r[1] == 'plate') + '）')
check(all(ok_fold), f'折り目と ふちは のこって いる（強い 線の 強さ：前の {min(r[3] for r in rows) * 100:.0f}〜{max(r[3] for r in rows) * 100:.0f}%）')
check(all(ok_col), f'面の 色は かわらない（大きく ならした 色の ずれ：平均 {max(r[4] for r in rows):.1f}/255 まで）')
print('■ 目')
E = {}
for th, (cx, cy, kind) in eye_py.items():
    for tag in ('', '2'):
        im = load(f'rt_{th}_plate{tag}.webp').astype(np.float32); yy, xx = np.mgrid[0:im.shape[0], 0:im.shape[1]]; r = np.hypot(xx - cx, yy - cy)
        E[th + tag] = (im[r < 4][:, :3].mean(0), im[(r > 13) & (r < 20)][:, :3].mean(0), im[(r > 40) & (r < 50)][:, :3].mean(0))
k0, k2, m0, m2 = E['kamisama'], E['kamisama2'], E['maboroshi'], E['maboroshi2']
check(k0[0].max() < 110 and k2[0].min() > 200 and k2[1][0] - k2[1][2] > 80 and k2[1][0] > 180 and k2[1][1] > k2[1][2] + 30 and np.abs(k2[2] - k0[2]).max() < 12,
      f'神様馬：ひとみ（前は 暗い 色 {k0[0].round(0).tolist()}）が 明るい 光の 玉（{k2[0].round(0).tolist()}）・まわりは **金色**（{k2[1].round(0).tolist()}）・はなれた 所は かわらない')
check(m0[0].max() < 110 and m2[0].min() > 200 and m2[1][2] - m2[1][1] > 60 and m2[1][0] - m2[1][1] > 25 and m2[1][2] > 150 and np.abs(m2[2] - m0[2]).max() < 16,
      f'幻の馬：ひとみ（前は 暗い 色 {m0[0].round(0).tolist()}）が 明るい 光の 玉（{m2[0].round(0).tolist()}）・まわりは **紫**（{m2[1].round(0).tolist()}）・はなれた 所は かわらない')
no, nn = load('rt_normal_plate.webp').astype(np.float32), load('rt_normal_plate2.webp').astype(np.float32)
dn = cv2.GaussianBlur(np.abs(no[..., :3] - nn[..., :3]).max(-1), (0, 0), 6)
check(float(dn.max()) < 14, f'ノーマル：目の 光は 足して いない（前の 絵との ちがいは まだらを けした 分 だけ：ならした 差 {dn.max():.1f}/255 まで）')
print('■ 軽い 版（アプリに 入る 絵）')
L = assets_dir.lite('tc_assets')
if os.path.isdir(L):
    st = assets_dir.stale('tc_assets')
    have = set(os.listdir(L))
    check(not st and set(NEW) <= have and not (set(OLD) & have) and all(md5(os.path.join(L, f)) == md5(os.path.join(M, f)) for f in NEW) and assets_dir.adir('tc_assets') == L,
          f'新しい 12まい だけ（前の 12まいは ない）・中身は もとと 同じ（{sum(os.path.getsize(os.path.join(L, f)) for f in NEW):,}B：前の 12まいは {sum(os.path.getsize(os.path.join(M, f)) for f in OLD):,}B）・軽い 版は 新しい{"（" + st + "）" if st else ""}')
else:
    print('  ※ 軽い 版（ios/lite/tc_assets）が ない')
# 新しい 絵が ない とき だけ 前の 絵（アプリの 画面で：新しい 絵 4まいを 読めなく して ノーマルの ルーレットを 回す）＝絵が 出ない ままに ならない
print('■ 新しい 絵が 読めない とき（前の 絵で 出る）')
import shutil, time
from playwright.sync_api import sync_playwright
SRV = os.path.join(W, 'srv_rt'); PORT = 8801; APP = f'http://localhost:{PORT}/APP/'
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, HIST='hist_280.json', DROP='', TARGET='app'))
pth = os.path.join(SRV, 'APP', 'index.html'); html = open(pth, encoding='utf8').read()
assert "window.__NATIVE = location.protocol === 'tengel:';" in html
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
TCA = assets_dir.adir('tc_assets')
for f in os.listdir(TCA): shutil.copy(os.path.join(TCA, f), os.path.join(SRV, 'APP', f))
for f in OLD: shutil.copy(os.path.join(M, f), os.path.join(SRV, 'APP', f))            # 前の 絵（アプリには 入れない もの）を ここ だけ 置く
FAKE = open(os.path.join(W, 'test_tc.py'), encoding='utf8').read().split('FAKE = """')[1].split('"""')[0]
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
try:
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'])
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo'); ctx.add_init_script(FAKE)
        pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.route('**/rt_normal_*2.webp', lambda r: r.abort())
        pg.goto(APP); pg.wait_for_timeout(1500)
        g = pg.locator('#gate')
        for _ in range(40):
            if not g.count() or g.evaluate('e => e.hidden'): break
            if pg.locator('#gateGo').count():
                try: pg.locator('#gateGo').click(timeout=3000)
                except Exception: pass
            pg.wait_for_timeout(150)
        pg.locator('#tcFab .fabi').click()
        pg.wait_for_function("() => window.TCApp && document.querySelector('#tcOv.on') && !document.querySelector('#tcOv .tcld')", timeout=120000); pg.wait_for_timeout(1200)
        RES = "() => performance.getEntriesByType('resource').filter(e => /\\/rt_/.test(e.name)).map(e => [e.name.split('/').pop(), e.responseStatus || 0, e.decodedBodySize || 0])"
        outs = {}
        for th, bg in (('normal', 'morning'), ('kamisama', 'divine')):
            pg.evaluate("([th, bg]) => { window.__rtDone = false; TCFX.roulette(document.querySelector('#tcOv .tcfx'), { th, a: 800, b: 1600, win: 1, bg, se: () => {} }).then(() => { window.__rtDone = true; }); }", [th, bg])
            pg.wait_for_timeout(2500); wait_tap = pg.evaluate("() => document.querySelector('#tcOv .tcfx').classList.contains('on') && !window.__rtDone")
            pg.mouse.click(300, 600); pg.wait_for_timeout(5600); pg.mouse.click(200, 400)
            pg.wait_for_function("() => window.__rtDone", timeout=20000); pg.wait_for_timeout(300)
            outs[th] = (wait_tap, {n: (st_, sz) for n, st_, sz in pg.evaluate(RES) if n.startswith(f'rt_{th}_')})
        nr, kr = outs['normal'], outs['kamisama']
        check(nr[0] and all(nr[1].get(f'rt_normal_{q}.webp', (0, 0))[0] == 200 and nr[1][f'rt_normal_{q}.webp'][1] > 1000 for q in PARTS) and all(nr[1].get(f'rt_normal_{q}2.webp', (0, 0))[1] == 0 for q in PARTS) and not errs,
              f'ノーマルの 新しい 絵 4まいが 読めない → 前の 絵 4まいを 読んで ルーレットは いつもどおり（タップ待ち → 回る → とじる・エラーなし：{sorted(n for n, v in nr[1].items() if v[1] > 0)}）{errs[:2] if errs else ""}')
        check(kr[0] and sorted(kr[1]) == [f'rt_kamisama_{q}2.webp' for q in sorted(PARTS)] and all(v[0] == 200 for v in kr[1].values()),
              f'神様馬（新しい 絵が 読める）：新しい 絵 4まい だけ（前の 絵は 読みに いかない：{sorted(kr[1])}）')
        b.close()
finally:
    srv.terminate()
    shutil.rmtree(SRV, ignore_errors=True)
print('結果：', 'NG ' + str(len(fails)) if fails else 'OK')
sys.exit(1 if fails else 0)
