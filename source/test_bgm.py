# テンゲルBGM と 神様馬の BGM（第4.171版）の テスト
#   まさちゃん 2026/11/14 16:18「②テンゲルのBGMを考える
#     ・テンゲルBGM(トレーニングセンター、思い出フィギュア、作戦会議、推し馬の画面では流れない)
#     ・トレーニングセンターの神様馬出現中のBGM:もっとアップテンポで掻き立てられるようなBGM」・17:08「神様馬のBGMもう少しカッコよく！もう少し神様ぽさを混ぜて！」
#   ・テンゲルBGM（bgm.js）：判定・記録・実測・設定の 画面で 鳴る／トレーニングセンター・思い出フィギュア・作戦会議・推し馬の 画面、的中の 演出の 間、アプリが うしろの 間は 止まる
#     → もどったら つづきから（曲の 頭に もどらない）・設定の「BGM」で オン／オフ（おぼえる）・消音スイッチの きまり（ambient）を 決められない 端末は 念のため はじめ オフ・
#     音の ファイルが ない ときは 何も しない（エラーも 出さない）・3D の 画面に 20秒 いたら ほどいた 音を 手ばなす
#   ・神様馬の BGM：新しい 曲（tc_bgm_divine2.m4a）を まん中の 1回り だけ くり返す（LOOPS）・前の 曲は アプリに 入れない・新しい 曲が ない ときだけ 前の 曲
#   ・音の ファイル：長さ＝1回り＋前後 0.5秒・前後の つづきは 同じ 音・大きさ（BGM は うしろで 鳴る 大きさ）
#   ・Web版には 入れない
#   python3 test_bgm.py   （ios/tc_assets/ が ない とき（CI）は 音なしの 形 だけ 確かめる）
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
BGM_N = 9                                                                              # アプリに 入れる テンゲルBGM の 稿（第9稿：bgm_tengel9.m4a）
BGM_F, DIV_F, DIV_OLD = f'bgm_tengel{BGM_N}.m4a', 'tc_bgm_divine2.m4a', 'tc_bgm_divine.m4a'
BGM_OLDS = ['bgm_tengel.m4a'] + [f'bgm_tengel{i}.m4a' for i in range(2, BGM_N)]         # 前の 稿（もとの フォルダに 残す・アプリには 入れない）
BGM_OLD = BGM_OLDS[0]
HAVE_BGM = HAVE and os.path.exists(os.path.join(TCA, BGM_F)); HAVE_DIV = HAVE and os.path.exists(os.path.join(TCA, DIV_F))
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
BPM = 36; LEN, PRE = 16 * 4 * 60 / BPM, 0.5                                             # 第9稿：16小節・36 BPM＝約106.7秒
DLEN = 32 * 4 * 60 / 156
ST = "() => { const s = TengelBgm.state(); s.type = navigator.audioSession ? navigator.audioSession.type : null; s.saved = localStorage.getItem('tengel.bgm'); s.files = performance.getEntriesByType('resource').filter(e => /bgm_tengel%d[.]m4a/.test(e.name)).length; return s; }".replace('%d', str(BGM_N))


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


def playing(pg, want, ms=6000):
    try: pg.wait_for_function(f"() => TengelBgm.state().playing === {'true' if want else 'false'}", timeout=ms); return True
    except Exception: return False


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
    src = open(os.path.join(W, 'bgm.js'), encoding='utf8').read(); code = re.sub(r'//[^\n]*', '', src)
    app = open(os.path.join(SRV, 'APP', 'index.html'), encoding='utf8').read(); web = open(os.path.join(SRV, 'TENGEL', 'index.html'), encoding='utf8').read()
    check('window.TengelBgm = {' in app and f"'{BGM_F}'" in app and "'tengel.bgm'" in app and 'id = \'setBgm\'' in app.replace('"', "'"), 'App Store版の index.html に テンゲルBGM（bgm.js）と 設定の 札（bgmCard）が 入って いる')
    check(BGM_F not in web and 'window.TengelBgm = {' not in web, 'Web版には テンゲルBGM（bgm.js）を 入れない')
    check('confirm(' not in code and 'alert(' not in code and 'prompt(' not in code, 'bgm.js は confirm()・alert() を 使わない')
    sh = open(os.path.join(W, 'src.html'), encoding='utf8').read(); card = sh.split('function bgmCard() {')[1].split('function paintBgmCard()')[0]
    body = set(open(os.path.join(W, 'ios', 'fonts', 'ks', 'chars_body.txt'), encoding='utf8').read())
    strs = ''.join(re.findall(r'>([^<>`${}]+)<', card)) + ''.join(re.findall(r"'((?:[^'\\]|\\.)*)'", card)); lack = sorted({c for c in strs if ord(c) > 0x2000 and c not in body})
    sys.path.insert(0, os.path.join(W, 'kisekae')); import build_fonts as _bf
    check(not lack and 'テンゲルの音楽だよ' in strs and 'BGMをオフにしたよ' in strs and not (set(_bf.body_chars()) - body), f'設定の 札の 言葉は しぼった 字（本文 {len(body)}字）に 入って いる 字 だけ（足りない 字 {lack}）')
    check(all(k in card for k in ('トレーニングセンター', '思い出フィギュア', '作戦かいぎ', '推し馬', '的中の演出の間は鳴らないよ', '消音スイッチがオンのときは鳴らないよ')),
          '札の 説明：鳴らない 画面（トレーニングセンター・思い出フィギュア・作戦会議・推し馬・的中の 演出の 間）と 消音スイッチ')
    ta = open(os.path.join(W, 'tc', 'tc_app.js'), encoding='utf8').read()
    check(f"divine: '{DIV_F}'" in ta and "divine: { pre: 0.5, len: 32 * 4 * 60 / 156 }" in ta and f"AMB_OLD = {{ divine: '{DIV_OLD}' }}" in ta,
          '神様馬の フィールドの BGM は 新しい 曲（tc_bgm_divine2.m4a）・まん中の 1回り（32小節・156 BPM）だけを くり返す・新しい 曲が ない とき だけ 前の 曲')
    old = superseded('tc_assets', [DIV_F, DIV_OLD, 'tc_bgm_abyss.m4a', BGM_F] + BGM_OLDS + ['tc_rt_boom.mp4'])
    check(old == {DIV_OLD} | set(BGM_OLDS) and superseded('tc_assets', BGM_OLDS) == set(BGM_OLDS[:-1]) and superseded('tc_assets', [DIV_OLD, BGM_OLD, 'tc_bgm_abyss.m4a']) == set() and superseded('tc_assets', BGM_OLDS[:2]) == {BGM_OLD}
          and superseded('tc_assets', BGM_OLDS[:3]) == set(BGM_OLDS[:2]) and superseded('tc_assets', ['bgm_tengel10.m4a', BGM_F, 'bgm_tengel9.m4a']) == {BGM_F, 'bgm_tengel9.m4a'},
          f'新しい 曲が ある とき、前の 曲（神様馬の 前の BGM・テンゲルBGM の 第1稿〜第{BGM_N - 1}稿）は アプリに 入れない（番号の いちばん 大きい 稿 だけ 入れる・ない ときは 前の 曲を 入れる）：{sorted(old)}')
    bi = open(os.path.join(W, 'build_ios.py'), encoding='utf8').read()
    check("in ('webp', 'json', 'bin', 'm4a', 'mp4'))" in bi, 'アプリには 同じ フォルダ（ios/tc_assets）の 音（m4a）と 爆発の 動画（mp4）も 入る')
    if HAVE_BGM:
        sr, y = wav(os.path.join(TCA, BGM_F)); dur = len(y) / sr; rms = db(math.sqrt(float(np.mean(y ** 2)))); pk = db(float(np.abs(y).max())); sm_ = seam(y, sr, LEN, PRE)
        check(abs(dur - (LEN + 2 * PRE)) < 0.08 and sm_ > 0.9, f'テンゲルBGM の ファイル：長さ {dur:.2f}秒＝1回り {LEN:.2f}秒（16小節・{BPM} BPM）＋前後 0.5秒・前後の つづきは 同じ 音（似かた {sm_:.3f}）')
        check(-33 <= rms <= -26 and pk <= -9, f'テンゲルBGM の 大きさ：全体 {rms:.1f}dB・山 {pk:.1f}dB（うしろで 鳴る 大きさ：的中の 演出の 音〈山 −2〜−7dB〉より ずっと 小さい）')
        # 第4稿（まさちゃん 11/14 19:09「一回、鳥の声と笛の音だけにしてみて！もっとゆったりで！」）：笛の ひと息（3小節）→ 休み（1小節：鳥の 番）×4。太鼓・ベースは ない ＝ 低い 音（250Hz より 下）が ない
        # 第5稿（19:25「ここに馬の走る音と、もう少し太い音の笛を混ぜて！ゆったりね！」）：形は 同じ。太い 笛の 低い 音・馬の ひづめの「ドッ」が 少し 入る（それでも 低い 音は 全体より ずっと 小さい）
        # 第6稿（19:41「もう一段階太い笛と、かなり音が低い笛も重ねて音入れて！」・19:42「馬の鳴き声と、馬が走る音追加して！」）：形は 同じ。かなり 低い 笛（147〜247Hz）が 入る ＝ 250Hz より 下にも 音が ある。
        #   太鼓・ベースの ような もっと 低い 音（110Hz より 下）は 馬の ひづめの「ドッ」だけ ＝ 全体より ずっと 小さい
        # 第8稿（20:12「ごめん！笛に戻して！もっとゆったりで！」・20:15「あと風の音も入れて！」）：形は 同じ（48 BPM・80秒）。休みには 風も 吹く
        # 第9稿（20:27「もっと笛の音ゆっくりして！」）：形は 同じ（36 BPM・約106.7秒）
        k = int(sr * LEN / 16); bars = [db(math.sqrt(float(np.mean(y[int(PRE * sr) + i * k:int(PRE * sr) + (i + 1) * k] ** 2)))) for i in range(16)]
        fl = [b for i, b in enumerate(bars) if i % 4 != 3]; rs = [b for i, b in enumerate(bars) if i % 4 == 3]
        k1 = sr; secs = [db(math.sqrt(float(np.mean(y[int(PRE * sr) + i * k1:int(PRE * sr) + (i + 1) * k1] ** 2)))) for i in range(int(LEN))]
        check(max(fl) - min(fl) <= 7.5 and min(fl) > -34 and all(-50 < b < float(np.median(fl)) - 6 for b in rs) and min(secs) > -56,
              f'テンゲルBGM：笛の 小節の 大きさは そろって いる（{min(fl):.0f}〜{max(fl):.0f}dB）・4小節めごとは 笛が 休んで 鳥と 馬と 風の 番（{min(rs):.0f}〜{max(rs):.0f}dB）・1秒より 長く 音が 消える 所は ない（いちばん 小さい 1秒 {min(secs):.0f}dB）')
        from scipy import signal as _sg
        _m1 = y.mean(1) if y.ndim > 1 else y; lo = db(math.sqrt(float(np.mean(_sg.sosfilt(_sg.butter(4, 110 / (sr / 2), 'low', output='sos'), _m1) ** 2)))); lo2 = db(math.sqrt(float(np.mean(_sg.sosfilt(_sg.butter(4, [130 / (sr / 2), 260 / (sr / 2)], 'band', output='sos'), _m1) ** 2))))
        check(lo < rms - 17 and rms - 14 < lo2 < rms - 4, f'テンゲルBGM：鳴るのは 笛（4本）・鳥の 声・馬の 鳴き声と 走る 音 だけ ＝ 太鼓・ベースの 高さ（110Hz より 下）は 少ししか ない（{lo:.1f}dB：全体より {rms - lo:.0f}dB 小さい）・かなり 低い 笛の 高さ（130〜260Hz）には 音が ある（{lo2:.1f}dB）')
    else: print(f'  ⚠️ テンゲルBGM の ファイル（ios/tc_assets/{BGM_F}）が ない')
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
        ctx = mk(True); pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        dialogs = []; pg.on('dialog', lambda d: (dialogs.append(d.type), d.dismiss()))
        print('■ 鳴る（判定の 画面）')
        pg.goto(APP); pg.wait_for_function("() => !!window.TengelBgm", timeout=20000); gate(pg)
        if HAVE_BGM:
            ok = playing(pg, True, 12000); s0 = pg.evaluate(ST)
            check(ok and s0['on'] and s0['ctx'] == 'running' and s0['loaded'] and not s0['gone'] and s0['saved'] is None and s0['files'] == 1 and abs(s0['len'] - LEN) < 1e-6,
                  f'アプリを 開くと テンゲルBGM が 鳴る（決めて いない ときは オン・音の ファイルは 1回 だけ 読む：{ {k: s0[k] for k in ("on", "playing", "ctx", "loaded", "files")} }）')
            check(s0['type'] == 'ambient' and pg.evaluate('() => window.__asLog') == ['ambient'], '消音スイッチなら 鳴らない きまり（audioSession＝ambient：ほかの アプリの 音楽は 止めない）に する')
            pg.wait_for_timeout(1000); s1 = pg.evaluate(ST); d = (s1['pos'] - s0['pos']) % LEN
            check(0.8 <= d <= 1.4, f'曲は 進む（1秒で {d:.2f}秒）')
            print('■ 鳴らない 所')
            # 的中の 演出の 間（html.fxon）
            pg.evaluate("() => document.documentElement.classList.add('fxon')"); ok1 = playing(pg, False, 2000); pa = pg.evaluate(ST)['pos']; pg.wait_for_timeout(700); pb = pg.evaluate(ST)['pos']
            pg.evaluate("() => document.documentElement.classList.remove('fxon')"); ok2 = playing(pg, True, 3000); pc_ = pg.evaluate(ST)['pos']
            check(ok1 and abs(pb - pa) < 1e-6 and ok2 and 0 <= (pc_ - pb) % LEN < 0.6, f'的中の 演出の 間は 止まる（{pa:.2f}秒の 所で 止まった まま）→ おわったら つづきから（{pc_:.2f}秒：頭に もどらない）')
            # アプリが うしろに いる 間
            pg.evaluate("() => { Object.defineProperty(document, 'hidden', { configurable: true, get: () => true }); document.dispatchEvent(new Event('visibilitychange')); }"); ok1 = playing(pg, False, 1500)
            pg.evaluate("() => { delete document.hidden; document.dispatchEvent(new Event('visibilitychange')); }"); ok2 = playing(pg, True, 3000)
            check(ok1 and ok2, 'アプリが うしろに いる 間は 止まる → もどったら 鳴る')
            # 作戦会議・推し馬
            r = pg.evaluate("() => { const r = document.querySelector('#planBtn').getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }"); pg.touchscreen.tap(*r)
            pg.wait_for_function("() => window.TCPlan && TCPlan.isOpen()", timeout=60000); ok1 = playing(pg, False, 2500)
            pg.evaluate("() => TCPlan.close()"); ok2 = playing(pg, True, 3000)
            check(ok1 and ok2, '作戦会議の 画面では 止まる → 閉じたら 鳴る')
            if pg.locator('#oshiFab').count():
                pg.locator('#oshiFab .fabi').click(); pg.wait_for_function("() => TCPlan.isOpen()", timeout=20000); ok1 = playing(pg, False, 2500)
                jo = pg.evaluate("() => !!document.querySelector('#tcPlan .oboard')"); pg.evaluate("() => TCPlan.close()"); ok2 = playing(pg, True, 3000)
                check(ok1 and ok2 and jo, '推し馬の 画面（作戦会議の 中の 推し馬の ボード）では 止まる → 閉じたら 鳴る')
            else: check(False, '推し馬の ボタン（#oshiFab）が ない')
            # トレーニングセンター
            pg.locator('#tcFab .fabi').click(); pg.wait_for_function("() => document.querySelector('#tcOv.on')", timeout=60000); ok1 = playing(pg, False, 2500); pa = pg.evaluate(ST)['pos']
            pg.wait_for_timeout(1500); sT = pg.evaluate(ST)
            pg.locator('#tcOv [data-tc=back]').click(); pg.wait_for_function("() => !document.querySelector('#tcOv.on')", timeout=10000); ok2 = playing(pg, True, 3000); pb = pg.evaluate(ST)['pos']
            check(ok1 and ok2 and not sT['playing'] and 0 <= (pb - pa) % LEN < 0.8, f'トレーニングセンターでは 止まる（トレーニングセンターの 音と 重ならない）→ 出たら つづきから（{pa:.2f} → {pb:.2f}秒）')
            # 思い出フィギュア
            pg.locator('#figFab').click(); pg.wait_for_function("() => document.querySelector('#fgOv.on')", timeout=60000); ok1 = playing(pg, False, 2500)
            pg.locator('#fgOv [data-fg=back]').first.click(); pg.wait_for_function("() => !document.querySelector('#fgOv.on')", timeout=10000); ok2 = playing(pg, True, 3000)
            check(ok1 and ok2, '思い出フィギュアの 画面では 止まる → 出たら 鳴る')
            print('■ 設定の 札')
            pg.locator('.tabbar button[data-tab=set]').click(); pg.wait_for_timeout(500)
            cd = pg.evaluate("() => { const c = document.getElementById('setBgm'); if (!c) return null; const on = c.querySelector('.seg[data-bgm] button[data-v=\"1\"]'), off = c.querySelector('.seg[data-bgm] button[data-v=\"0\"]');"
                             " return { prev: c.previousElementSibling && c.previousElementSibling.id, h2: c.querySelector('h2').textContent, on: on.getAttribute('aria-pressed'), off: off.getAttribute('aria-pressed'), n: document.querySelectorAll('#setBgm').length, w: c.scrollWidth <= c.clientWidth + 1 }; }")
            check(cd is not None and cd['prev'] == 'setFx' and cd['h2'] == 'BGM' and cd['on'] == 'true' and cd['off'] == 'false' and cd['n'] == 1 and cd['w'] and playing(pg, True, 2000),
                  f'設定に 札「BGM」（「的中の演出」の すぐ 下・オンが 押されて いる・はみ出さない）・設定の 画面でも 鳴って いる（{cd}）')
            pg.locator('#setBgm .seg[data-bgm] button[data-v="0"]').click(); ok1 = playing(pg, False, 2000); pg.wait_for_timeout(300); s2 = pg.evaluate(ST)
            tx = pg.evaluate("() => document.getElementById('toast').textContent"); pr = pg.evaluate("() => document.querySelector('#setBgm .seg[data-bgm] button[data-v=\"0\"]').getAttribute('aria-pressed')")
            check(ok1 and not s2['on'] and s2['saved'] == '0' and not s2['loaded'] and tx == 'BGMをオフにしたよ' and pr == 'true', f'オフを 押すと 止まる・おぼえる（{s2["saved"]}）・ほどいた 音は 手ばなす・お知らせ「{tx}」')
            pg.wait_for_timeout(1600); s3 = pg.evaluate(ST)
            check(not s3['playing'] and s3['ctx'] in ('suspended', 'interrupted'), f'オフの 間は 音の 出口を 休ませる（{s3["ctx"]}）')
            pg.reload(); pg.wait_for_function("() => !!window.TengelBgm", timeout=20000); gate(pg); pg.mouse.click(195, 300); pg.wait_for_timeout(2500); s4 = pg.evaluate(ST)
            check(not s4['on'] and not s4['playing'] and s4['files'] == 0 and s4['ctx'] is None, f'開き直しても オフの まま（音の ファイルも 読まない：{s4["files"]}回）')
            pg.locator('.tabbar button[data-tab=set]').click(); pg.wait_for_timeout(400)
            pg.locator('#setBgm .seg[data-bgm] button[data-v="1"]').click(); ok1 = playing(pg, True, 8000); s5 = pg.evaluate(ST); tx = pg.evaluate("() => document.getElementById('toast').textContent")
            check(ok1 and s5['on'] and s5['saved'] == '1' and tx == 'BGMをオンにしたよ', f'オンを 押すと 鳴る・おぼえる（{s5["saved"]}）・お知らせ「{tx}」')
            print('■ 3D の 画面に 長く いる とき')
            pg.locator('.tabbar button[data-tab=judge]').click(); pg.wait_for_timeout(300)
            pg.locator('#tcFab .fabi').click(); pg.wait_for_function("() => document.querySelector('#tcOv.on')", timeout=60000); playing(pg, False, 2500); l0 = pg.evaluate(ST)['loaded']
            pg.wait_for_timeout(21500); l1 = pg.evaluate(ST)['loaded']
            pg.locator('#tcOv [data-tc=back]').click(); pg.wait_for_function("() => !document.querySelector('#tcOv.on')", timeout=10000); ok2 = playing(pg, True, 8000); s6 = pg.evaluate(ST)
            check(l0 and not l1 and ok2 and s6['loaded'] and s6['files'] == 1, f'トレーニングセンターに 20秒 いたら ほどいた 音（約38MB）を 手ばなす → 出たら ほどき直して 鳴る（ファイルは 読み直さない：{s6["files"]}回）')
        else:
            pg.mouse.click(195, 300); pg.wait_for_timeout(3000); s0 = pg.evaluate(ST)
            check(s0['on'] and not s0['playing'] and s0['gone'], f'音の ファイルが ない ビルド：何も 鳴らさない（{s0}）')
        check(not errs and not dialogs, f'エラーなし・窓（confirm／alert）なし（{errs[:2]}{dialogs[:2]}）')
        ctx.close()

        print('■ 消音スイッチの きまり（ambient）を アプリから 決められない 端末（古い iOS）')
        ctx = mk(False); pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(APP); pg.wait_for_function("() => !!window.TengelBgm", timeout=20000); gate(pg); pg.mouse.click(195, 300); pg.wait_for_timeout(2500); s0 = pg.evaluate(ST)
        check(not s0['on'] and not s0['ambient'] and not s0['playing'] and s0['files'] == 0, f'決めて いない ときは 念のため オフ：{ {k: s0[k] for k in ("on", "ambient", "playing", "files")} }')
        pg.locator('.tabbar button[data-tab=set]').click(); pg.wait_for_timeout(500)
        pr = pg.evaluate("() => { const c = document.getElementById('setBgm'); return c ? c.querySelector('.seg[data-bgm] button[data-v=\"0\"]').getAttribute('aria-pressed') : null; }")
        pg.locator('#setBgm .seg[data-bgm] button[data-v="1"]').click(); ok1 = playing(pg, True, 8000) if HAVE_BGM else True; s1 = pg.evaluate(ST)
        check(pr == 'true' and s1['on'] and s1['saved'] == '1' and ok1 and not errs, f'設定の 札は オフ → オンを 押せば 鳴る（{s1["saved"]}）')
        ctx.close()

        print('■ 音の ファイルが ない・読めない とき')
        ctx = mk(True); pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.route('**/' + BGM_F, lambda r: r.abort())
        pg.goto(APP); pg.wait_for_function("() => !!window.TengelBgm", timeout=20000); gate(pg); pg.mouse.click(195, 300); pg.wait_for_timeout(2500); s0 = pg.evaluate(ST)
        pg.locator('.tabbar button[data-tab=set]').click(); pg.wait_for_timeout(400); has = pg.evaluate("() => !!document.getElementById('setBgm')")
        check(s0['on'] and s0['gone'] and not s0['playing'] and not s0['loaded'] and has and not errs, f'何も 鳴らさない・エラーも 出さない・設定の 札は 出る（{ {k: s0[k] for k in ("on", "gone", "playing", "loaded")} }{errs[:2]}）')
        ctx.close()

        if HAVE_DIV:
            print('■ 神様馬の BGM（トレーニングセンター）')
            ctx = mk(True); pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.goto(APP); pg.wait_for_function("() => !!window.TengelBgm", timeout=20000); gate(pg)
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
            pg.goto(APP); pg.wait_for_function("() => !!window.TengelBgm", timeout=20000); gate(pg)
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
        check(pw.evaluate("() => typeof window.TengelBgm === 'undefined' && !document.getElementById('setBgm') && performance.getEntriesByType('resource').filter(e => /bgm_tengel/.test(e.name)).length === 0") and not e3, f'Web版：BGM は ない・設定の 札も 出ない（{e3[:2]}）')
        ctx.close(); b.close()
finally:
    srv.terminate()
print()
print('結果：', 'ぜんぶ OK' if not fails else f'{len(fails)} こ ❌')
for f in fails: print('  ❌', f)
sys.exit(1 if fails else 0)
