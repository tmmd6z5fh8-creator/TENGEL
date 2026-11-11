# 壁紙の 走る コマを 画面の 3倍に（第4.156版・まさちゃん 2026/11/12 04:20「Aにして！」：A／B の 見くらべの 見本を 見て）
#   python3 test_wall_hq.py   （壁紙の 絵 ios/kisekae_blobs/ が 手元に ある とき だけ 絵と 画面も。ない とき（CI）は 台帳と ページの 形 だけ）
#   この 版は 競馬新聞・勝負服・夕焼け の 3つ（のこり：花火・ナイター・水墨画・ネオン は 次の 版）
#   ・台帳：走る コマの id は 新しい 絵・切りぬく 場所と コマの 数は 前と 同じ・絵の 細かさ scale＝1.5（＝画面の 3倍）
#   ・ページ（news_wall.py・silks_wall.py・sunset_wall.py）：シートの 大きさは pt の まま（前と 同じ 場所・同じ 動き）
#   ・絵は リポジトリに 入って いない・作る 道具（flat/hq_*.py）と 入れる 道具（flat/hq_install.py）は ある
#   ・絵：名前は 中身の md5・1コマは pt の 3倍・前の 絵（2倍）も 手元に のこって いる（消して いない）・同じ 絵（小さく すると 前の 絵と 同じ・馬の 場所も 同じ）・前より 細かい
#   ・アプリの 画面（iPhone と 同じ 3倍）：絵の 3px を 1pt に 出す・動く・前の 絵（2倍）に さしかえた ときより くっきり・エラー なし
#     iPad の「iPhone の 大きさ」（2倍の 画面）でも 同じ 場所に 出る
import hashlib, io, json, os, re, shutil, subprocess, sys, time
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
K = os.path.join(W, 'kisekae')
BL = os.environ.get('KISEKAE_ASSETS') or os.path.join(W, 'ios', 'kisekae_blobs')
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label)
    if not c:
        fails.append(label)


#           台帳の キー・id の 前に つく もの・run.json の どこ・前の 絵（2倍）・切りぬく 場所・絵の 形・ページの 動く 所／その 窓・絵の 大きさ（バイト）の はんい
SET = {'news': dict(jp='競馬新聞', key='run', pre='', sub=None, old='90c9d3f81a75c530c5dcaf297f8bfafb', cell=[208, 76, 360, 200], mode='RGB', el='.nsw .nsr', win='.nsw .nsh', anim='nsRun', kb=(70, 140)),
       'silks': dict(jp='勝負服', key='run', pre='', sub=None, old='a6f4674ee0a8a396c3f9df8527b92f77', cell=[70, 24, 612, 292], mode='RGBA', el='.sbw .sbr', win='.sbw .sbh', anim='sbRun', kb=(280, 480)),
       'sunset': dict(jp='夕焼け', key='horse', pre='/_blob/', sub='horse', old='3f932ad749f07e3a3d47e32e8004914e', cell=[204, 26, 430, 228], mode='RGBA', el='.ssw .sxr', win='.ssw .sxh', anim='sxRun', kb=(130, 250))}
N = 10; SC = 1.5
sys.path.insert(0, K)
import news_wall, silks_wall, sunset_wall
MOD = dict(news=news_wall, silks=silks_wall, sunset=sunset_wall)
ID = {}; RUN = {}
for nm, s in SET.items():
    blobs = json.load(open(os.path.join(K, nm + '_blobs.json'), encoding='utf8')); run = json.load(open(os.path.join(K, nm + '_run.json'), encoding='utf8'))
    info = run[s['sub']] if s['sub'] else run
    v = blobs[s['key']]; ID[nm] = v[len(s['pre']):]; RUN[nm] = run
    check(v.startswith(s['pre']) and bool(re.fullmatch(r'[0-9a-f]{32}', ID[nm])) and ID[nm] != s['old'] and info['cell'] == s['cell'] and info['frames'] == N and info.get('scale') == SC
          and s['old'] not in json.dumps(blobs),
          f'台帳（{s["jp"]}）：走る コマは 新しい 絵・切りぬく 場所 {s["cell"]} と コマの 数 {N} は 前と 同じ・絵の 細かさ {info.get("scale")}倍（＝画面の 3倍）')
    x0, y0, cw, ch = (v // 2 for v in s['cell'])
    html, css = MOD[nm].inline(MOD[nm].load_blobs(os.path.join(K, nm + '_blobs.json')), run)
    check(f'{s["el"]}{{width:{N * cw}px;height:{ch}px;background:url(/_blob/{ID[nm]}) 0 0/{N * cw}px {ch}px no-repeat;' in css and f'steps({N})' in css and f'translateX(-{N * cw}px)' in css
          and f'left:{x0}px;top:{y0}px;width:{cw}px;height:{ch}px;overflow:hidden' in css and s['old'] not in css + html,
          f'ページ（{s["jp"]}）：窓は 左 {x0}・上 {y0}・{cw}×{ch}pt・シートは {N * cw}×{ch}pt（pt の まま＝場所と 動きは 前と 同じ）・絵は 新しい id')
gi = subprocess.run(['git', 'ls-files'], capture_output=True, text=True, cwd=W).stdout.split('\n')
tools = ['hq_news.py', 'hq_silks.py', 'hq_sunset.py', 'hq_install.py']
check(not any(f.startswith('ios/kisekae_blobs/') for f in gi) and all(os.path.exists(os.path.join(K, 'flat', f)) for f in tools)
      and all('/home/claude' not in open(os.path.join(K, 'flat', f), encoding='utf8').read() for f in tools),
      '壁紙の 絵は リポジトリに 入って いない・作る 道具（flat/hq_news.py・hq_silks.py・hq_sunset.py）と 入れる 道具（flat/hq_install.py）が ある')
have = os.path.isdir(BL) and all(os.path.exists(os.path.join(BL, ID[nm] + '.webp')) for nm in SET)
if not have:
    print('※ 壁紙の 絵（ios/kisekae_blobs）が ない ので、絵と アプリの 画面の 確かめは しない')
    print('結果：', 'NG ' + str(len(fails)) if fails else 'OK'); sys.exit(1 if fails else 0)
import numpy as np
from PIL import Image
P = lambda i: os.path.join(BL, i + '.webp')


def load(p):
    """0〜1 の 数。すき通しの ある 絵は 色×濃さ（＋濃さ）で くらべる"""
    im = Image.open(p); im = im.convert('RGBA') if im.mode == 'RGBA' else im.convert('RGB')
    a = np.asarray(im).astype(np.float32) / 255
    return np.dstack([a[..., :3] * a[..., 3:], a[..., 3]]) if a.shape[2] == 4 else a


def psnr(x, y):
    m = float(((x - y) ** 2).mean()); return 99.0 if m < 1e-12 else 10 * np.log10(1 / m)


def detail(a):
    """絵の 細かさ（となりの 点との 差の 大きさ：ぼやけた 絵ほど 小さい）"""
    g = a[..., :3].mean(2)
    return float(np.abs(4 * g[1:-1, 1:-1] - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]).mean())


def resize(a, size, how):
    return np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255 + .5).astype(np.uint8)).resize(size, how)).astype(np.float32) / 255


tot_new = tot_old = 0
for nm, s in SET.items():
    x0, y0, cw, ch = s['cell']; pn, po = P(ID[nm]), P(s['old'])
    im = Image.open(pn); szn = os.path.getsize(pn)
    okf = hashlib.md5(open(pn, 'rb').read()).hexdigest() == ID[nm] and im.format == 'WEBP' and im.mode == s['mode'] and im.size == (int(cw * SC) * N, int(ch * SC)) == (3 * (cw // 2) * N, 3 * (ch // 2))
    oko = os.path.exists(po) and Image.open(po).size == (cw * N, ch)          # 前の 絵（キャンバスの id の まま：名前は md5 では ない）
    tot_new += szn; tot_old += os.path.getsize(po) if oko else 0
    check(okf and oko and s['kb'][0] * 1000 < szn < s['kb'][1] * 1000,
          f'絵（{s["jp"]}）：名前は 中身の md5・1コマ {int(cw * SC)}×{int(ch * SC)}px（{cw // 2}×{ch // 2}pt の 3倍）・{szn / 1e3:.0f}KB（前 {os.path.getsize(po) / 1e3 if oko else 0:.0f}KB）・前の 絵（2倍）も 手元に のこって いる')
    if not (okf and oko):
        continue
    A, O = load(pn), load(po)
    small = resize(A, (O.shape[1], O.shape[0]), Image.LANCZOS); up = resize(O, (A.shape[1], A.shape[0]), Image.BILINEAR)
    ps = psnr(O, small); dr = detail(A) / max(detail(up), 1e-9)
    off = 0.0
    if s['mode'] == 'RGBA':          # 馬の 場所（コマごとの 濃さの 重心：pt）
        for i in range(N):
            c = []
            for a, k in ((A, 3.0), (O, 2.0)):
                w = a.shape[1] // N; al = a[:, i * w:(i + 1) * w, 3]; ys, xs = np.mgrid[0:al.shape[0], 0:al.shape[1]]; m = al.sum()
                c.append(((xs * al).sum() / m / k, (ys * al).sum() / m / k))
            off = max(off, abs(c[0][0] - c[1][0]), abs(c[0][1] - c[1][1]))
    check(ps > 25 and dr > 1.3 and off < 0.3,
          f'絵（{s["jp"]}）：同じ 絵（2/3 に 小さく すると 前の 絵と 同じ：PSNR {ps:.1f}dB' + (f'・馬の 場所の ずれ {off:.2f}pt' if s['mode'] == 'RGBA' else '') + f'）・前の 絵を のばした ものより 細かい（細かさ {dr:.2f}倍）')
check(150_000 < tot_new - tot_old < 400_000, f'3まいで ＋{(tot_new - tot_old) / 1e3:.0f}KB（{tot_old / 1e3:.0f}KB → {tot_new / 1e3:.0f}KB）')

from playwright.sync_api import sync_playwright
SRV = os.path.join(W, 'srv_wallhq'); PORT = 8800; APP = f'http://localhost:{PORT}/APP/'
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, HIST='hist_280.json', DROP='', TARGET='app'))
pth = os.path.join(SRV, 'APP', 'index.html'); page = open(pth, encoding='utf8').read()
assert "window.__NATIVE = location.protocol === 'tengel:';" in page
open(pth, 'w', encoding='utf8').write(page.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
for f in os.listdir(BL):
    shutil.copy(os.path.join(BL, f), os.path.join(SRV, 'APP', 'ks_' + f))
for nm, s in SET.items():
    kj = json.load(open(os.path.join(SRV, 'APP', f'ks_{nm}.json'), encoding='utf8')); txt = kj['bnr']['html'] + kj['bnr']['css']
    check(f'ks_{ID[nm]}.webp' in txt and s['old'] not in json.dumps(kj), f'{s["jp"]}の ファイル（ks_{nm}.json）：新しい 絵・前の 絵は 入って いない')
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
ST = """async ([el, win]) => { const bn = document.querySelector('#ksBnr'), e = bn && bn.querySelector(el), w = bn && bn.querySelector(win); if (!e || !w) return null;
  const b = bn.getBoundingClientRect(), r = w.getBoundingClientRect(), c = getComputedStyle(e), u = (c.backgroundImage.match(/url\\("?([^")]+)"?\\)/) || [])[1];
  const nat = u ? await new Promise(res => { const im = new Image(); im.onload = () => res([im.naturalWidth, im.naturalHeight]); im.onerror = () => res(null); im.src = u; }) : null;
  const an = e.getAnimations();
  return { bn: [b.width, b.height], win: [r.left - b.left, r.top - b.top, r.width, r.height].map(v => +v.toFixed(2)), w: parseFloat(c.width), h: parseFloat(c.height), bs: c.backgroundSize, url: u ? u.split('/').pop() : null, nat: nat,
    an: an.map(a => [a.animationName, a.playState, a.effect.getTiming().duration]), tf: c.animationTimingFunction, k: bn.style.getPropertyValue('--ksk'), sw: document.documentElement.scrollWidth }; }"""
SEEK = "(T) => { for (const a of document.querySelector('#ksBnr').getAnimations({ subtree: true })) { a.pause(); a.currentTime = T * 1000; } }"


def open_app(ctx, tid):
    pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    bad = []; pg.on('response', lambda r: bad.append(r.url.split('/')[-1]) if r.status >= 400 and '/ks_' in r.url else None)
    pg.goto(APP); pg.wait_for_timeout(1500)
    if pg.locator('#gateGo').count(): pg.click('#gateGo'); pg.wait_for_timeout(700)
    pg.wait_for_function("() => window.TengelKisekae && TengelKisekae.list().length > 0", timeout=10000)
    use(pg, tid)
    return pg, errs, bad


def use(pg, tid):
    pg.evaluate("(id) => TengelKisekae.apply(id, false)", tid)
    pg.wait_for_function("(id) => TengelKisekae.current() === id && TengelKisekae.loaded()", arg=tid, timeout=8000); pg.wait_for_timeout(1200)
    pg.evaluate("window.scrollTo(0, 0)")


def shot(pg, win, t):
    """走る コマの 窓の 所 だけ（動きを t 秒で 止めて）"""
    pg.evaluate(SEEK, t); pg.wait_for_timeout(250)
    r = pg.evaluate("(w) => { const r = document.querySelector('#ksBnr ' + w).getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; }", win)
    return np.asarray(Image.open(io.BytesIO(pg.screenshot(clip=dict(x=r[0], y=r[1], width=r[2], height=r[3])))).convert('RGB')).astype(np.float32) / 255


try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=3, locale='ja-JP', timezone_id='Asia/Tokyo')
        pg, errs, bad = open_app(ctx, 'news')
        for nm, s in SET.items():
            if nm != 'news':
                use(pg, nm)
            x0, y0, cw, ch = (v // 2 for v in s['cell'])
            q = pg.evaluate(ST, [s['el'], s['win']])
            okq = (bool(q) and q['bn'] == [390, 160] and q['win'] == [x0, y0, cw, ch] and [q['w'], q['h']] == [N * cw, ch] and q['bs'] == f'{N * cw}px {ch}px' and q['url'] == f'ks_{ID[nm]}.webp'
                   and q['nat'] == [3 * N * cw, 3 * ch] and q['nat'][0] / q['w'] == 3.0 and any(a[0].endswith(s['anim']) and a[1] == 'running' for a in q['an']) and q['tf'].replace(' ', '') in (f'steps({N})', f'steps({N},end)') and q['sw'] <= 390)
            if not okq: print('    ', json.dumps(q, ensure_ascii=False)[:900])
            check(okq, f'アプリ（{s["jp"]}・iPhone の 3倍の 画面）：窓 {[x0, y0, cw, ch]}pt・シート {q and q["nat"]}px＝**絵の 3px を 1pt に**・走る 動き（{N}コマ）・横に はみ出さない' + ('' if okq else f'（{q}）'))
            # くっきり：いまの 絵 と、同じ 所に 前の 絵（2倍）を さしかえた とき を くらべる（動きは 同じ コマで 止める）
            dur = next((a[2] for a in (q or {}).get('an', []) if a[0].endswith(s['anim'])), 500) / 1000
            a0, a1 = shot(pg, s['win'], 0.05 * dur), shot(pg, s['win'], 0.45 * dur)
            tag = pg.add_style_tag(content=f'#ksBnr {s["el"]}{{background-image:url(ks_{s["old"]}.webp) !important}}'); pg.wait_for_timeout(500)
            o0 = shot(pg, s['win'], 0.05 * dur)
            tag.evaluate("e => e.remove()"); pg.wait_for_timeout(300)
            same = psnr(a0, o0); dr = detail(a0) / max(detail(o0), 1e-9); mv = float(np.abs(a0 - a1).mean())
            check(a0.shape == (3 * ch, 3 * cw, 3) and same > 22 and dr > 1.12 and mv > 0.004,
                  f'アプリ（{s["jp"]}）：前の 絵（2倍）に さしかえた ときと 同じ 絵（PSNR {same:.1f}dB）で、画面の 上でも くっきり（細かさ {dr:.2f}倍）・コマが 進む')
        check(not errs and not bad, f'エラー なし・読めない 絵 なし {errs[:2]} {bad[:3]}')
        ctx.close()
        # iPad の「iPhone の 大きさ」（390×844・2倍の 画面）：同じ 場所に 出る（絵は 3倍の まま 小さく 出す）
        ctx2 = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo')
        pg2, errs2, bad2 = open_app(ctx2, 'silks')
        s = SET['silks']; x0, y0, cw, ch = (v // 2 for v in s['cell'])
        q = pg2.evaluate(ST, [s['el'], s['win']])
        check(bool(q) and q['bn'] == [390, 160] and q['win'] == [x0, y0, cw, ch] and q['nat'] == [3 * N * cw, 3 * ch] and (q['k'] or '1') in ('1', '1.0000') and not errs2 and not bad2,
              f'iPad の「iPhone の 大きさ」（390×844・2倍の 画面）：壁紙は 引きのばさない（--ksk {q and q["k"]}）・走る コマは 同じ 場所 {q and q["win"]}')
        ctx2.close(); b.close()
finally:
    srv.terminate()
shutil.rmtree(SRV, ignore_errors=True)
print('結果：', 'NG ' + str(len(fails)) if fails else 'OK')
sys.exit(1 if fails else 0)
