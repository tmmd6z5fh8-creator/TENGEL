# テンゲルBGM は なし（第4.172版）・神様馬の BGM（第4.171版）の テスト
#   まさちゃん 2026/11/14 22:05「やっぱりテンゲルBGMも消して！無しでいいや！」
#   ・テンゲルBGM（第4.171版の bgm.js・設定の 札「BGM」・説明書の 行）は アプリに 入って いない・音の ファイル（bgm_tengel<番号>.m4a）も 入れない（もとの フォルダには 残す）・
#     アプリを 開いても しかけは ない・設定に 札は ない・音の ファイルを 読みに いかない・エラー なし。Web版にも ない
#     （bgm.js と 曲を 作る 道具 kisekae/tc/snd/bgm_tengel.py は リポジトリに 残して ある：もどす ときは build_pwa.py・src.html〈コミット 8bec612〉・assets_dir.py）
#   まさちゃん 11/14 16:18「トレーニングセンターの神様馬出現中のBGM:もっとアップテンポで掻き立てられるようなBGM」・17:08「神様馬のBGMもう少しカッコよく！もう少し神様ぽさを混ぜて！」
#   ・神様馬の BGM：新しい 曲（tc_bgm_divine2.m4a）を まん中の 1回り だけ くり返す（LOOPS）・前の 曲は アプリに 入れない・新しい 曲が ない ときだけ 前の 曲
#   ・音の ファイル：長さ＝1回り＋前後 0.5秒・前後の つづきは 同じ 音・大きさ
#   python3 test_bgm.py   （ios/tc_assets/ が ない とき（CI）は 形 だけ 確かめる）
import math, os, re, shutil, subprocess, sys, time
import numpy as np
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv_bgm'); PORT = 8811; APP = f'http://localhost:{PORT}/APP/'; WEB = f'http://localhost:{PORT}/TENGEL/'
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'TENGEL')], check=True, stdout=subprocess.DEVNULL, env={k: v for k, v in os.environ.items() if k not in ('TENGEL_TEST', 'TARGET')})
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, TARGET='app'))
from assets_dir import adir, superseded
TCA = adir('tc_assets'); HAVE = os.path.isdir(TCA) and len(os.listdir(TCA)) > 100
DIV_F, DIV_OLD = 'tc_bgm_divine2.m4a', 'tc_bgm_divine.m4a'
BGM_ALL = ['bgm_tengel.m4a'] + [f'bgm_tengel{i}.m4a' for i in range(2, 10)]            # 作った 稿（第1稿〜第9稿）：どれも アプリには 入れない（もとの フォルダに 残す）
HAVE_DIV = HAVE and os.path.exists(os.path.join(TCA, DIV_F))
pth = os.path.join(SRV, 'APP', 'index.html'); html = open(pth, encoding='utf8').read()
assert "window.__NATIVE = location.protocol === 'tengel:';" in html
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
if HAVE:
    for f in os.listdir(TCA): shutil.copy(os.path.join(TCA, f), os.path.join(SRV, 'APP', f))
else: print('※ トレーニングセンターの 絵と 音（ios/tc_assets）が ない ので、音なしの 形 だけ 確かめる')
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c: fails.append(label)


FAKE = open(os.path.join(W, 'test_tc.py'), encoding='utf8').read().split('FAKE = """')[1].split('"""')[0]      # アプリの 窓口の にせもの（test_tc.py と 同じ）
# 消音スイッチの きまり（navigator.audioSession）の にせもの：iOS 16.4 から ある。Chromium には ない ＝ 入れない ページは「古い iOS」の 形
ASFAKE = "(() => { let t = 'auto'; window.__asLog = []; try { Object.defineProperty(navigator, 'audioSession', { configurable: true, value: { get type() { return t; }, set type(v) { t = v; window.__asLog.push(v); } } }); } catch (e) { /* なし */ } })();"
PRE = 0.5
DLEN = 32 * 4 * 60 / 156
READY = "() => !!document.querySelector('#tcFab .fabi') && !!window.TengelWallet"      # アプリが 立ち上がった 印
NOBGM = "() => ({ api: typeof window.TengelBgm, card: !!document.getElementById('setBgm'), files: performance.getEntriesByType('resource').filter(e => /bgm_tengel/.test(e.name)).length, saved: localStorage.getItem('tengel.bgm') })"


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


def wav(path):
    """m4a → (サンプルの 数/秒, 左右の 波：−1〜1)"""
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 's16le', '-ac', '2', '-ar', '44100', '-'], capture_output=True, check=True)
    return 44100, np.frombuffer(r.stdout, np.int16).reshape(-1, 2).astype(np.float64) / 32768


def db(x): return 20 * math.log10(max(1e-12, x))


def seam(y, sr, ln, pre):
    """くり返す 1回りの 前後の つづきが 同じ 音か：頭の pre 秒 と（1回り あとの）同じ 所・おしりの pre 秒 と（1回り 前の）同じ 所の 似かた（相関）。m4a の 頭の ずれ（数ミリ秒）は 合わせて から 比べる"""
    m = y.mean(1); n = int(pre * sr); best = -1
    for off in range(-2400, 2401, 4):
        a = m[2400:n - 2400]; i = int(round(ln * sr)) + 2400 + off
        if i < 0 or i + len(a) > len(m): continue
        b = m[i:i + len(a)]; c = float(np.corrcoef(a, b)[0, 1]); best = max(best, c)
    return best


try:
    print('■ 中身（ビルド・音の ファイル）')
    app = open(os.path.join(SRV, 'APP', 'index.html'), encoding='utf8').read(); web = open(os.path.join(SRV, 'TENGEL', 'index.html'), encoding='utf8').read()
    check(not any(k in app for k in ('TengelBgm', 'setBgm', 'bgm_tengel', 'tengel.bgm', 'data-bgm')), 'App Store版の index.html に テンゲルBGM の しかけ（bgm.js）・設定の 札・音の ファイルの 名前は ない')
    check(not any(k in web for k in ('TengelBgm', 'setBgm', 'bgm_tengel', 'tengel.bgm', 'data-bgm')), 'Web版の index.html にも ない')
    bp = re.sub(r'#[^\n]*', '', open(os.path.join(W, 'build_pwa.py'), encoding='utf8').read()); sh = open(os.path.join(W, 'src.html'), encoding='utf8').read()
    man = open(os.path.join(W, 'manual', 'content_app.html'), encoding='utf8').read()
    check('bgm.js' not in bp and 'bgmCard' not in sh and 'setBgm' not in sh and 'BGM' not in man and os.path.exists(os.path.join(W, 'bgm.js')),
          'ビルド（build_pwa.py）は bgm.js を 入れない・src.html に 設定の 札の コードは ない・説明書に「BGM」の 行は ない（bgm.js の ファイルは もどす とき の ために 残して ある）')
    ta = open(os.path.join(W, 'tc', 'tc_app.js'), encoding='utf8').read()
    check(f"divine: '{DIV_F}'" in ta and "divine: { pre: 0.5, len: 32 * 4 * 60 / 156 }" in ta and f"AMB_OLD = {{ divine: '{DIV_OLD}' }}" in ta,
          '神様馬の フィールドの BGM は 新しい 曲（tc_bgm_divine2.m4a）・まん中の 1回り（32小節・156 BPM）だけを くり返す・新しい 曲が ない とき だけ 前の 曲')
    old = superseded('tc_assets', [DIV_F, DIV_OLD, 'tc_bgm_abyss.m4a'] + BGM_ALL + ['tc_rt_boom.mp4'])
    check(old == {DIV_OLD} | set(BGM_ALL) and superseded('tc_assets', BGM_ALL[:1]) == set(BGM_ALL[:1]) and superseded('tc_assets', ['bgm_tengel12.m4a', 'tc_bgm_abyss.m4a']) == {'bgm_tengel12.m4a'}
          and superseded('tc_assets', [DIV_OLD, 'tc_bgm_abyss.m4a']) == set(),
          f'アプリに 入れない 音：テンゲルBGM は どの 稿も（{len(BGM_ALL)}こ）・神様馬の 前の BGM は 新しい 曲が ある とき だけ（ない ときは 前の 曲を 入れる）')
    mst = os.path.join(W, 'ios', 'tc_assets')
    if HAVE and 'lite' in TCA:
        check(not [f for f in os.listdir(TCA) if f.startswith('bgm_tengel')] and (not os.path.isdir(mst) or all(os.path.exists(os.path.join(mst, f)) for f in BGM_ALL)),
              f'アプリに 入れる フォルダ（軽い 版）に テンゲルBGM の ファイルは ない・もとの フォルダには {len(BGM_ALL)}稿 とも 残って いる（消して いない）')
    bi = open(os.path.join(W, 'build_ios.py'), encoding='utf8').read()
    check("in ('webp', 'json', 'bin', 'm4a', 'mp4'))" in bi, 'アプリには 同じ フォルダ（ios/tc_assets）の 音（m4a）と 爆発の 動画（mp4）も 入る')
    if HAVE_DIV:
        sr, y = wav(os.path.join(TCA, DIV_F)); dur = len(y) / sr; rms = db(math.sqrt(float(np.mean(y ** 2)))); pk = db(float(np.abs(y).max())); sm_ = seam(y, sr, DLEN, PRE)
        check(abs(dur - (DLEN + 2 * PRE)) < 0.08 and sm_ > 0.9, f'神様馬の BGM の ファイル：長さ {dur:.2f}秒＝1回り {DLEN:.2f}秒（32小節・156 BPM）＋前後 0.5秒・前後の つづきは 同じ 音（似かた {sm_:.3f}）')
        check(-31 <= rms <= -25 and pk <= -11, f'神様馬の BGM の 大きさ：全体 {rms:.1f}dB・山 {pk:.1f}dB（お世話の 音〈山 −15dB ぐらい〉が うもれない）')
        k = int(sr * DLEN / 32); bars = [db(math.sqrt(float(np.mean(y[int(PRE * sr) + i * k:int(PRE * sr) + (i + 1) * k] ** 2)))) for i in range(32)]
        check(max(bars) - min(bars) <= 6 and min(bars) > -35, f'神様馬の BGM：小節ごとの 大きさは そろって いる（{min(bars):.0f}〜{max(bars):.0f}dB）')
        check(os.path.exists(os.path.join(TCA, 'tc_bgm_abyss.m4a')) and not os.path.exists(os.path.join(TCA, DIV_OLD)) if 'lite' in TCA else True, 'アプリに 入れる フォルダ（軽い 版）に 前の 神様馬の BGM は ない')
    else: print('  ⚠️ 神様馬の BGM の ファイル（ios/tc_assets/tc_bgm_divine2.m4a）が ない')

    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'])
        mk = lambda fake: (lambda c: (c.add_init_script(FAKE), fake and c.add_init_script(ASFAKE), c)[-1])(b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo', has_touch=True, is_mobile=True))
        print('■ アプリを 開く（テンゲルBGM は ない）')
        ctx = mk(True); pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        dialogs = []; pg.on('dialog', lambda d: (dialogs.append(d.type), d.dismiss())); bad = []; pg.on('response', lambda r: bad.append(r.url.split('/')[-1]) if r.status >= 400 else None)
        pg.goto(APP); pg.wait_for_function(READY, timeout=30000); gate(pg); pg.mouse.click(195, 300); pg.wait_for_timeout(2500); n0 = pg.evaluate(NOBGM)
        check(n0 == {'api': 'undefined', 'card': False, 'files': 0, 'saved': None}, f'開いて 画面を さわっても：しかけ（window.TengelBgm）なし・音の ファイルを 読みに いかない・設定の 値も 作らない（{n0}）')
        pg.locator('.tabbar button[data-tab=set]').click(); pg.wait_for_timeout(600)
        cs = pg.evaluate("() => { const fx = document.getElementById('setFx'); return { fx: !!fx, bgm: !!document.getElementById('setBgm'), h2: [...document.querySelectorAll('#view-set h2, .setsec h2')].map(h => h.textContent.trim()).filter(t => /BGM/.test(t)), next: fx && fx.nextElementSibling ? (fx.nextElementSibling.id || fx.nextElementSibling.className) : null }; }")
        check(cs['fx'] and not cs['bgm'] and cs['h2'] == [], f'設定：札「的中の演出」は ある・札「BGM」は ない（「的中の演出」の つぎは {cs["next"]}）')
        pg.locator('.tabbar button[data-tab=judge]').click(); pg.wait_for_timeout(300)
        pg.locator('#tcFab .fabi').click(); pg.wait_for_function("() => document.querySelector('#tcOv.on')", timeout=60000); pg.wait_for_timeout(1500)
        pg.locator('#tcOv [data-tc=back]').click(); pg.wait_for_function("() => !document.querySelector('#tcOv.on')", timeout=10000); pg.wait_for_timeout(800); n1 = pg.evaluate(NOBGM)
        check(n1['api'] == 'undefined' and n1['files'] == 0 and not errs and not dialogs and not [x for x in bad if 'bgm' in x], f'トレーニングセンターに 入って 出ても 同じ・エラーなし・窓（confirm／alert）なし・読めない BGM の ファイル なし（{errs[:2]}{dialogs[:2]}）')
        ctx.close()

        if HAVE_DIV:
            print('■ 神様馬の BGM（トレーニングセンター）')
            ctx = mk(True); pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.goto(APP); pg.wait_for_function(READY, timeout=30000); gate(pg)
            pg.locator('#tcFab .fabi').click(); pg.wait_for_function("() => document.querySelector('#tcOv.on') && window.TCApp && TCApp._snd && TCApp._snd.ac", timeout=60000); pg.wait_for_timeout(1500)
            pg.evaluate("() => { TCApp._snd.field('divine'); }"); pg.wait_for_function("() => TCApp._snd.bed === 'divine'", timeout=15000); pg.wait_for_timeout(300)
            dv = pg.evaluate("() => { const S = TCApp._snd, fs = performance.getEntriesByType('resource').map(e => e.name.split('/').pop().split('?')[0]).filter(n => /^tc_bgm_divine/.test(n)); return { bed: S.bed, loop: S.loop, len: S.LOOPS.divine.len, pre: S.LOOPS.divine.pre, files: fs }; }")
            check(dv['bed'] == 'divine' and dv['files'] == [DIV_F] and abs(dv['len'] - DLEN) < 1e-6 and dv['loop'] and abs(dv['loop'][0] - 0.25) < 1e-6 and abs(dv['loop'][1] - (0.25 + DLEN)) < 1e-6,
                  f'神様馬の フィールド：新しい 曲（{dv["files"]}）を まん中の 1回り だけ くり返す（{dv["loop"][0]:.2f}〜{dv["loop"][1]:.2f}秒・前の 曲は 読まない）')
            pg.evaluate("() => { TCApp._snd.field('morning'); }"); pg.wait_for_function("() => TCApp._snd.bed === 'morning'", timeout=15000)
            lm = pg.evaluate("() => TCApp._snd.loop")
            check(lm == [0, 0] and not errs, f'ほかの フィールドの 音は いままで どおり（ファイルの はじめから おわりまでを くり返す：{lm}）')
            ctx.close()
            # 新しい 曲が ない（前の 素材の フォルダで 作った アプリ）→ 前の 曲を そのまま くり返す
            ctx = mk(True); pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.route('**/' + DIV_F, lambda r: r.abort()); pg.route('**/' + DIV_OLD, lambda r: r.fulfill(path=os.path.join(TCA, 'tc_bgm_abyss.m4a'), content_type='audio/mp4'))
            pg.goto(APP); pg.wait_for_function(READY, timeout=30000); gate(pg)
            pg.locator('#tcFab .fabi').click(); pg.wait_for_function("() => document.querySelector('#tcOv.on') && window.TCApp && TCApp._snd && TCApp._snd.ac", timeout=60000); pg.wait_for_timeout(1500)
            pg.evaluate("() => { TCApp._snd.field('divine'); }"); pg.wait_for_function("() => TCApp._snd.bed === 'divine'", timeout=15000)
            lo = pg.evaluate("() => TCApp._snd.loop")
            check(lo == [0, 0] and not errs, f'新しい 曲の ファイルが ない とき：前の 曲（tc_bgm_divine.m4a）を はじめから おわりまで くり返す（{lo}）')
            ctx.close()
        print('■ Web版')
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo'); ctx.add_init_script(ASFAKE)
        pw = ctx.new_page(); e3 = []; pw.on('pageerror', lambda e: e3.append(str(e)))
        pw.goto(WEB); pw.wait_for_timeout(1500); pw.mouse.click(195, 300); pw.wait_for_timeout(800)
        try: pw.locator('.tabbar button[data-tab=set]').click(timeout=3000); pw.wait_for_timeout(400)
        except Exception: pass
        check(pw.evaluate("() => typeof window.TengelBgm === 'undefined' && !document.getElementById('setBgm') && performance.getEntriesByType('resource').filter(e => /bgm_tengel/.test(e.name)).length === 0") and not e3, f'Web版：BGM は ない・設定の 札も ない（{e3[:2]}）')
        ctx.close(); b.close()
finally:
    srv.terminate()
print()
print('結果：', 'ぜんぶ OK' if not fails else f'{len(fails)} こ ❌')
for f in fails: print('  ❌', f)
sys.exit(1 if fails else 0)
