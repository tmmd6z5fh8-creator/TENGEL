# 帯の 壁紙 3つ（シルバー帯・ゴールド帯・マスター帯）：まさちゃんの 3D の 像（第4.149版・まさちゃん 2026/11/11 00:39「これシルバー帯の馬の3D これゴールド帯にゴールドに変えて使える？」・
#   02:14「マスター帯の壁紙変える！シルバー帯、ゴールド帯のようにこのファイルの3Dモデルが中央に合って光っているようにして！背景の色は、3Dモデルに合う色で合わせてみて！
#   元々あったマスター帯の壁紙と雷の演出とかは消していいよ！」）
#   python3 test_band_wall.py   （壁紙の 絵 ios/kisekae_blobs/ が 手元に ある とき だけ。ない とき（CI）は 台帳の 確かめ だけ）
#   ・台帳：metal_blobs.json に 9まい（銀・金・マスター帯 × いまの 絵／きらめきを ぬいた 絵／**馬 だけの 高画質の 絵**）・選ぶ 画面の 小さい 絵（blobs20.json）は いまの 絵・metal_run.json に 3つの 形と きらめき
#     （マスター帯は 形を 自分の 中に・台の 上の はし ped・きらめきと 光の 粒は 馬の 所 だけ＝台と 台の 字の 上に 出ない）・絵は 780×320 の WebP・手元の 絵は 消して いない（前の 絵も ある）
#   ・3D（GLB）と そこから 作る もとは リポジトリに 入って いない（flat/metal_glb.py は 場所 だけ 知って いる）
#   ・馬（主役）だけ 高画質（まさちゃん 11/11 02:36「壁紙は、馬(主役)だけ画質良くなるようにして！」）：像 だけの すき通った 絵（背景の 絵の 2倍の 細かさ）を 同じ 場所に 重ねる・背景は 780×320 の まま
#   ・マスター帯：台は 正面から まっすぐ（02:40「テンゲルの台が正面に真っ直ぐ見えるようにして！」）
#     第4.150版（03:46「マスター帯が、シルバー帯、ゴールド帯より馬のサイズが小さいのが気になる！もっと大きくできる？」→ 見本 A・B・C → 04:03「Aにして！」）：
#     馬は シルバー帯・ゴールド帯と 同じ 大きさ（前は 77%）。台の いちばん 下は 絵の 外（台は「TENGER」の 字の すぐ 下で 切れる・カタカナの 札は 絵の 外）・
#     床は シルバー帯・ゴールド帯と 同じ 高さ（262）から＝台は 床の 手前に 立つ
#     （第4.149版は 台を ぜんぶ 入れて、床に うつる 台と 影を 描いて いた：02:33「台が地面から浮いてるからちゃんと地面につけて！」）
#   ・アプリ：3つの 壁紙とも 判定タブの 上の 絵は 像＋きらめき（mxs／mxg／mxt）：絵 2まいが 読める・きらめき 14・こまかい 光の 粒 26・うしろへ 流れる 粒・光の 輪・動きが ある・横に はみ出さない
#     マスター帯：前の 壁紙（動く 数字・緑の 雷＝tq…）は ない・光の 粒は 左へ 流れる（像が 右向き）・シルバー帯と ゴールド帯は 右へ
#   ・選ぶ 画面の 小さい 絵（3つ）が 新しい 絵で 読める
#   ・視差効果を 減らす：動かさない（いまの 絵 だけ）
import hashlib, json, os, re, shutil, subprocess, sys, time
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
K = os.path.join(W, 'kisekae')
BL = os.environ.get('KISEKAE_ASSETS') or os.path.join(W, 'ios', 'kisekae_blobs')
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label)
    if not c:
        fails.append(label)


MB = json.load(open(os.path.join(K, 'metal_blobs.json'))); B20 = json.load(open(os.path.join(K, 'blobs20.json'))); RUN = json.load(open(os.path.join(K, 'metal_run.json')))
KEYS = ['silver_banner', 'silver_base', 'gold_banner', 'gold_base', 'tengel_banner', 'tengel_base']
HERO = ['silver_statue', 'gold_statue', 'tengel_statue']      # 馬（主役）だけの 高画質の 絵
NAMES = (('silver', 'silver', 'mxs', 1), ('golden', 'gold', 'mxg', 1), ('tengel', 'tengel', 'mxt', -1))      # テーマの id・絵の 名前・クラス・光の 粒が 流れる 向き
OLD = ['9504cde9557dd15164d7ea4c2fe29e8e', '6aa961c2be4422888172ea9689ef7cf0', '03691f51ad78a7922baf6b6a1d19d5ab', '681b968a52b39a9ec4076a934471596b', '0f58da915ffceb4dc05ffccb4b103100']   # 前の 絵（銀 2・金 2・マスター帯）
check(sorted(MB) == sorted(KEYS + HERO) and len(set(MB.values())) == 9 and all(re.fullmatch(r'[0-9a-f]{32}', v) for v in MB.values()) and not (set(MB.values()) & set(OLD))
      and B20['silver'] == MB['silver_banner'] and B20['golden'] == MB['gold_banner'] and B20['tengel'] == MB['tengel_banner'],
      '台帳：metal_blobs.json に 9まい（銀・金・マスター帯 × いまの 絵／きらめきを ぬいた 絵／馬 だけの 高画質の 絵）・前の 絵とは ちがう・選ぶ 画面の 小さい 絵（blobs20.json）は いまの 絵')
sh, T = RUN['shape'], RUN['tengel']
ts = T['shape']
pts = lambda r: [p[:2] for p in r['spark']] + [p[:2] for p in r['glint']] + [p[:2] for p in r['dots']]
in_box = lambda r, b: all(b[0] <= x <= b[2] and b[1] <= y <= b[3] for x, y in pts(r))
check(RUN['size'] == [780, 320] and all(len(RUN[n]['spark']) == 4 and len(RUN[n]['glint']) == 10 and len(RUN[n]['dots']) == 26 for n in ('silver', 'gold', 'tengel'))
      and sh['floor'] == 261 and 120 <= sh['box'][0] <= 160 and 620 <= sh['box'][2] <= 660 and sh['box'][3] in (sh['floor'], sh['floor'] + 1) and sh['ring'] == [390.0, 135.7, 150] and in_box(RUN['silver'], sh['box']) and in_box(RUN['gold'], sh['box'])
      and 'shape' not in RUN['silver'] and len(sh['d']) > 1500,
      f'metal_run.json：シルバー帯・ゴールド帯は 同じ 形（3D の 馬：箱 {sh["box"]}・床 261・光の 輪は 前と 同じ）・きらめき 4＋またたく 10＋光の 粒 26 は 像の 中')
HW = (ts['box'][2] - ts['box'][0]) / (sh['box'][2] - sh['box'][0])      # マスター帯の 馬の 幅 ÷ シルバー帯・ゴールド帯の 馬の 幅
check(ts['base'] > 320 and ts['box'][3] == 320 and ts['floor'] == 262 and ts['ped'] < ts['floor'] - 15 and 130 <= ts['box'][0] <= 150 and 630 <= ts['box'][2] <= 650 and ts['box'][1] >= 4
      and abs((ts['box'][0] + ts['box'][2]) / 2 - 390) <= 3 and abs(ts['ring'][0] - 390) <= 3 and 0.96 <= HW <= 1.02 and 150 <= ts['ring'][2] <= 165
      and all(y < ts['ped'] - 5 for _x, y in pts(T)) and in_box(T, ts['box']) and len(ts['d']) > 1500,
      f'metal_run.json：マスター帯は 自分の 形（台の 上の 金の 馬：箱 {ts["box"]}・台の 上の はし {ts["ped"]}・まん中）・**馬は シルバー帯・ゴールド帯と 同じ 大きさ**（幅 {ts["box"][2] - ts["box"][0]}px ÷ {sh["box"][2] - sh["box"][0]}px＝{HW * 100:.0f}%：前は 77%）・'
      f'台の いちばん 下（{ts["base"]}）は 絵の 外＝台は「TENGER」の 字の 下で 切れる・床は {ts["floor"]} から（シルバー帯・ゴールド帯の 床 {sh["floor"]} と そろえる）・光の 輪 {ts["ring"][2]}・きらめきと 光の 粒は 馬の 所 だけ（台と 台の 字の 上には 出ない）')
have = os.path.isdir(BL) and all(os.path.exists(os.path.join(BL, MB[k] + '.webp')) for k in KEYS + HERO)
gi = subprocess.run(['git', 'ls-files'], capture_output=True, text=True, cwd=W).stdout.split('\n')
src = open(os.path.join(K, 'flat', 'metal_glb.py'), encoding='utf8').read()
check(not any(f.lower().endswith(('.glb', '.gltf')) for f in gi) and not any(f.startswith('ios/kisekae_blobs/') for f in gi) and 'METAL_HORSE_GLB' in src and 'TENGEL_STATUE_GLB' in src,
      '3D（GLB）と 壁紙の 絵は リポジトリに 入って いない（flat/metal_glb.py は 場所（METAL_HORSE_GLB・TENGEL_STATUE_GLB）だけ）')
if not have:
    print('※ 壁紙の 絵（ios/kisekae_blobs）が ない ので、アプリの 画面の 確かめは しない')
    print('結果：', 'NG ' + str(len(fails)) if fails else 'OK'); sys.exit(1 if fails else 0)
from PIL import Image
ok_img = []
for k in KEYS:
    pth = os.path.join(BL, MB[k] + '.webp'); im = Image.open(pth)
    ok_img.append(im.size == (780, 320) and im.format == 'WEBP' and hashlib.md5(open(pth, 'rb').read()).hexdigest() == MB[k] and 8_000 < os.path.getsize(pth) < 60_000)
check(all(ok_img) and all(os.path.exists(os.path.join(BL, o + '.webp')) for o in OLD),
      f'絵 6まい：780×320 の WebP・名前は 中身の md5・1まい 8〜60KB（ぜんぶで {sum(os.path.getsize(os.path.join(BL, MB[k] + ".webp")) for k in KEYS) / 1e3:.0f}KB）・前の 絵 5まいも 手元に のこって いる（消して いない）')
import numpy as np
hero_ok, hero_note = [], []
for nm in ('silver', 'gold', 'tengel'):
    pth = os.path.join(BL, MB[nm + '_statue'] + '.webp'); im = Image.open(pth); x, y, w, h = RUN[nm]['statue']
    a = np.array(im.convert('RGBA'))[..., 3]; box = (RUN[nm].get('shape') or RUN['shape'])['box']
    hero_ok.append(im.mode == 'RGBA' and im.size == (w * 2, h * 2) and hashlib.md5(open(pth, 'rb').read()).hexdigest() == MB[nm + '_statue'] and 30_000 < os.path.getsize(pth) < 200_000
                   and x <= box[0] and y <= box[1] and x + w >= box[2] and y + h >= box[3] and x >= 0 and y >= 0 and x + w <= 780 and y + h <= 320
                   and a[0].max() < 40 and (a[-1].max() < 255 or y + h == 320) and (a == 255).mean() > 0.12 and (a == 0).mean() > 0.3)      # いちばん 下の 行：マスター帯は 絵の 下で 切れた 台
    hero_note.append(f'{nm} {im.size[0]}×{im.size[1]}・{os.path.getsize(pth) / 1e3:.0f}KB')
check(all(hero_ok) and RUN['silver']['statue'] == RUN['gold']['statue'],
      f'馬（主役）だけの 高画質の 絵 3まい：すき通った WebP・背景の 絵の 2倍の 細かさ（置く 場所 × 2）・像の 箱を ぜんぶ おおう・銀と 金は 同じ 場所（{"／".join(hero_note)}）')
# マスター帯の 台：正面から まっすぐ（台の 上の ふちが 水平・左右 対称）。台の 下は 絵の 外 なので、台の 上の 左はし・右はしの 高さと、前の 面の まん中で 見る
ta = np.array(Image.open(os.path.join(BL, MB['tengel_statue'] + '.webp')).convert('RGBA'))[..., 3] > 128
sx_, sy_, sw_, sh_ = T['statue']
P0 = int(round((ts['ped'] - sy_) * 2))                                                # 台の 上の はし（高画質の 絵の 行）
cen, wid = [], []
for r in range(P0 + 40, ta.shape[0] - 4, 20):                                        # 台の 前の 面の 行ごと：左はしと 右はしの まん中・幅
    c = np.nonzero(ta[r])[0]; cen.append(sx_ + (c.min() + c.max() + 1) / 4); wid.append((c.max() + 1 - c.min()) / 2)
c6 = np.nonzero(ta[P0 + 8])[0]                                                       # 台の 上の 板の 行
tops = [int(np.nonzero(ta[P0 - 24:P0 + 24, c])[0].min()) + P0 - 24 for c in (c6.min() + 14, c6.max() - 14)]      # 上の 板の 左はし・右はしの いちばん 上
check(len(cen) >= 5 and max(cen) - min(cen) <= 2 and max(abs(c - 390) for c in cen) <= 6 and abs(tops[0] - tops[1]) <= 2 and min(wid) > 300 and ta[-1].sum() / 2 > 300,      # まん中が どの 行でも 同じ＝左右 対称（正面）
      f'マスター帯の 台：正面から まっすぐ（台の 上の ふちは 左と 右で 同じ 高さ：{tops}・前の 面の まん中 x={min(cen):.1f}〜{max(cen):.1f}・幅 {min(wid):.0f}〜{max(wid):.0f}px・絵の いちばん 下まで 台＝{ta[-1].sum() / 2:.0f}px）')

from playwright.sync_api import sync_playwright
SRV = os.path.join(W, 'srv_band'); PORT = 8799; APP = f'http://localhost:{PORT}/APP/'
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, HIST='hist_280.json', DROP='', TARGET='app'))
pth = os.path.join(SRV, 'APP', 'index.html'); html = open(pth, encoding='utf8').read()
assert "window.__NATIVE = location.protocol === 'tengel:';" in html
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
for f in os.listdir(BL):
    shutil.copy(os.path.join(BL, f), os.path.join(SRV, 'APP', 'ks_' + f))
kj = json.load(open(os.path.join(SRV, 'APP', 'ks_tengel.json'), encoding='utf8'))
check('mxtw' in kj['bnr']['html'] and 'tqw' not in json.dumps(kj['bnr']) and not re.search(r'[." ]tq[A-Za-z0-9]', kj['bnr']['html'] + kj['bnr']['css']) and f"ks_{MB['tengel_banner']}.webp" in kj['bnr']['html'] and f"ks_{MB['tengel_base']}.webp" in kj['bnr']['html']
      and 'ks_0f58da915ffceb4dc05ffccb4b103100' not in json.dumps(kj),
      'マスター帯の ファイル（ks_tengel.json）：上の 絵は 新しい 像（mxt）・前の 壁紙（エンブレムの 絵・動く 数字・緑の 雷）は 入って いない')
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
ST = """async (p) => { const bn = document.querySelector('#ksBnr'), w = bn && bn.querySelector('.bnr'); if (!w) return null; const r = bn.getBoundingClientRect();
  const hrefs = [...w.querySelectorAll('image')].map(i => i.getAttribute('href'));
  const ok = await Promise.all(hrefs.map(h => new Promise(res => { const im = new Image(); im.onload = () => res([im.naturalWidth, im.naturalHeight]); im.onerror = () => res(null); im.src = h; })));
  const css = [...document.querySelectorAll('style')].map(s => s.textContent).join('\\n'); const m = css.match(new RegExp('@keyframes \\\\w*' + p + 'P0\\\\{[^@]*'));      // アプリの 中では @keyframes の 名前の 前に しるしが つく
  const an = w.getAnimations({ subtree: true });
  const he = w.querySelector('.' + p + 'H'), hb = he ? he.getBoundingClientRect() : null, sv = w.querySelector('svg').getBoundingClientRect();
  const kids = [...w.querySelector('svg').children].map(e => e.tagName + (e.getAttribute('class') ? '.' + e.getAttribute('class') : ''));
  return { cls: w.className, hidden: bn.hidden, box: [Math.round(r.width), Math.round(r.height)], hrefs: hrefs, ok: ok, kids: kids.join(' '),
    hero: he ? [+he.getAttribute('x'), +he.getAttribute('y'), +he.getAttribute('width'), +he.getAttribute('height')] : null, heroPx: hb ? [+(hb.left - sv.left).toFixed(1), +(hb.top - sv.top).toFixed(1), +hb.width.toFixed(1), +hb.height.toFixed(1)] : null,
    still: w.querySelectorAll('.' + p + 'S use').length, stillShown: w.querySelector('.' + p + 'S') ? getComputedStyle(w.querySelector('.' + p + 'S')).display : '', tw: w.querySelectorAll('.' + p + 'F').length, dots: w.querySelectorAll('.' + p + 'D').length,
    trail: w.querySelectorAll('.' + p + 'P').length, ring: w.querySelectorAll('.' + p + 'R').length, clip: !!w.querySelector('#' + p + 'O path'), anims: an.length, run: an.filter(a => a.playState === 'running').length,
    kf: m ? m[0].slice(0, 400) : '', tq: bn.querySelectorAll('[class^="tq"], [class*=" tq"]').length, aria: w.getAttribute('aria-label') || '', aHid: getComputedStyle(w.querySelector('.' + p + 'A')).visibility,
    sw: document.documentElement.scrollWidth }; }"""
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo')
        pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        bad = []; pg.on('response', lambda r: bad.append(r.url.split('/')[-1]) if r.status >= 400 and '/ks_' in r.url else None)
        pg.goto(APP); pg.wait_for_timeout(1500)
        if pg.locator('#gateGo').count(): pg.click('#gateGo'); pg.wait_for_timeout(700)
        pg.wait_for_function("() => window.TengelKisekae && TengelKisekae.list().length > 0", timeout=10000)
        res = {}
        for tid, nm, pre, flow in NAMES:
            pg.evaluate("(id) => TengelKisekae.apply(id, false)", tid)
            pg.wait_for_function("(id) => TengelKisekae.current() === id && TengelKisekae.loaded()", arg=tid, timeout=8000); pg.wait_for_timeout(700)
            s = pg.evaluate(ST, pre); res[tid] = s
            dx = [float(v) for v in re.findall(r'translate\(([-\d.]+)px', s['kf'] if s else '')]
            hx, hy_, hw, hh = RUN[nm]['statue']
            ok = (bool(s) and s['cls'] == f'bnr {pre}w' and s['hidden'] is False and s['box'] == [390, 160]
                  and s['hrefs'] == [f"ks_{MB[nm + '_banner']}.webp", f"ks_{MB[nm + '_base']}.webp", f"ks_{MB[nm + '_statue']}.webp"] and s['ok'] == [[780, 320], [780, 320], [hw * 2, hh * 2]]
                  and s['hero'] == [hx, hy_, hw, hh] and s['heroPx'] == [hx / 2, hy_ / 2, hw / 2, hh / 2] and s['ok'][2][0] / s['heroPx'][2] >= 3.99      # 馬の 絵：画面の 1px に 絵の 4px（iPhone の 3倍の 画面でも 足りる）
                  and s['kids'] == f'defs image g.{pre}A image.{pre}H g.{pre}A g.{pre}S' and s['still'] == 4 and s['stillShown'] == 'none'
                  and s['tw'] == 14 and s['dots'] == 26 and s['trail'] >= 8 and s['ring'] == 1 and s['clip'] and s['anims'] >= 50 and s['run'] >= 50 and s['tq'] == 0 and s['aHid'] == 'visible' and s['sw'] <= 390
                  and len(dx) >= 3 and all(v * flow > 0 for v in dx) and ('TENGER' in s['aria']) == (tid == 'tengel'))
            check(ok and not errs, f'{tid}：上の 絵は 像＋きらめき（{pre}w）：背景の 絵 2まい（780×320）＋**馬 だけの 高画質の 絵**（{s and s["ok"][2]}px を {s and s["heroPx"][2:]}pt に＝4倍・きらめきを ぬいた 絵と 光の 輪の 上／きらめきと 光の 粒の 下）・きらめき 14・光の 粒 26・うしろへ 流れる 粒 {s and s["trail"]}（{"右" if flow > 0 else "左"}へ）・光の 輪・動き {s and s["anims"]}こ・'
                  f'前の マスター帯の 数字と 雷は ない・横に はみ出さない' + ('' if ok else f'（{s}・{dx[:4]}）'))
        # 選ぶ 画面の 小さい 絵
        pg.locator('.tabbar [data-tab=set]').click(); pg.wait_for_timeout(500)
        th = pg.evaluate("""async (ids) => { const out = {}; for (const id of ids) { const im = document.querySelector('#setKisekae .kst[data-ks="' + id + '"] img.ksth'); if (!im) { out[id] = null; continue; }
          im.loading = 'eager'; im.scrollIntoView({ block: 'center' }); for (let i = 0; i < 40 && !(im.complete && im.naturalWidth); i++) await new Promise(r => setTimeout(r, 100)); out[id] = [im.getAttribute('src'), im.naturalWidth, im.naturalHeight]; } return out; }""", ['silver', 'golden', 'tengel'])
        check(th == {'silver': [f"ks_{MB['silver_banner']}.webp", 780, 320], 'golden': [f"ks_{MB['gold_banner']}.webp", 780, 320], 'tengel': [f"ks_{MB['tengel_banner']}.webp", 780, 320]} and not bad,
              f'選ぶ 画面の 小さい 絵（シルバー帯・ゴールド帯・マスター帯）が 新しい 絵で 読める・読めない 絵 なし（{th}・{bad[:3]}）')
        desc = pg.evaluate("TengelKisekae.list().filter(t => ['silver', 'golden', 'tengel'].includes(t.id)).map(t => t.id + ':' + t.desc).join()")
        check(desc == 'silver:銀・光る像,golden:金・光る像,tengel:テンゲル・光る像', f'一覧の 説明：{desc}')
        ctx.close()
        # 視差効果を 減らす：動かさない（いまの 絵 だけ）
        ctx2 = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo', reduced_motion='reduce')
        p2 = ctx2.new_page(); e2 = []; p2.on('pageerror', lambda e: e2.append(str(e)))
        p2.goto(APP); p2.wait_for_timeout(1500)
        if p2.locator('#gateGo').count(): p2.click('#gateGo'); p2.wait_for_timeout(700)
        rm = []
        for tid, nm, pre, flow in NAMES:
            p2.evaluate("(id) => TengelKisekae.apply(id, false)", tid)
            p2.wait_for_function("(id) => TengelKisekae.current() === id && TengelKisekae.loaded()", arg=tid, timeout=8000); p2.wait_for_timeout(600)
            s = p2.evaluate(ST, pre); rm.append((tid, bool(s) and s['run'] == 0 and s['aHid'] == 'hidden' and s['ok'][0] == [780, 320] and s['hero'] is not None and s['still'] == 4 and s['stillShown'] != 'none', s and (s['run'], s['aHid'], s['stillShown'])))
        check(all(o for _t, o, _s in rm) and not e2, f'視差効果を 減らす：3つ とも 動かさない（きらめきを ぬいた 絵と 動く 光は かくして、いまの 絵＋馬 だけの 高画質の 絵＋動かない きらめき 4つ）（{[(t, s) for t, o, s in rm if not o]}・{e2[:2]}）')
        ctx2.close()
        check(not errs, f'ページの エラーなし（{errs[:3]}）')
        b.close()
finally:
    srv.terminate()
    shutil.rmtree(SRV, ignore_errors=True)
print('結果：', 'NG ' + str(len(fails)) if fails else 'OK')
sys.exit(1 if fails else 0)
