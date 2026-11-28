# 第4.238版の テスト（まさちゃん 2026/11/28 14:46「漢字は、ひらがな打って変換させることはできない？ 種類が固定されてるよね！
#   あと牧場の名前変えてる時に電源落とすとまた、ビヨーンて変な音なってる！ 漢字の変換ができないなら、漢字は牧場に関連する漢字だけいれて！
#   注意事項にカタカナがローマ字で名前も決めてね！みたいな感じで入れて！」）
#   ①② かなキーボードの 漢字・注意の 字 は 第4.242版で なくした（かなキーボードを アプリから 外した：まさちゃん 11/29 00:03「牧場の名前普通に打てるからキーボード消して！」）
#   ③ 電源を 切る ときの 音：アプリ（iOS）の 知らせ audio（why: resign：willResignActive）・画面が かくれた・pagehide で、鳴って いる 出口を すぐ 止める（suspend）
#      ・止めて いる 間は とぎれが おわった 知らせ（interruption）で 起こさない・active／画面が 見えた／さわった で 起こす
#      ・トレーニングセンター：resign で すぐ 止まる・active で 同じ 音の まま つづく・画面が かくれたら 0.06秒で 止まる（前は 0.3秒 あと）・見えたら また 鳴る
#   ④ アプリ（Swift）：willResignActive → audio（resign）・とぎれが おわった 知らせは アプリが 前に いる ときだけ 起こす
#   ⑤ GitHub の Mac の たしかめ（selftest.js の audioQuiet・run.sh の AUDPY の 行）
#   python3 test_v238.py
import json, os, re, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
sys.path.insert(0, W)
SHOT = os.path.join(W, 't4'); os.makedirs(SHOT, exist_ok=True)
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c:
        fails.append(label)


nocom = lambda s: re.sub(r'(?m)^\s*//.*$', '', s)
fx = open('fx.js', encoding='utf8').read(); fxc = nocom(fx)
check('function quiet() {' in fxc and "if (document.hidden) { hid = true; quiet(); return; }" in fxc and "window.addEventListener('pagehide', quiet);" in fxc
      and "if (why === 'resign') quiet(); else if (why === 'interruption' && hushed) return; else wake();" in fxc and 'wake, quiet,' in fxc,
      '③ fx.js：resign・画面が かくれた・pagehide で すぐ 止める・止めて いる 間の interruption は 起こさない')
sw = open(os.path.join('ios', 'Tengel.swiftpm', 'TengelWebView.swift'), encoding='utf8').read()
blk = sw[sw.index('AVAudioSession.interruptionNotification'):sw.index('webView.load(URLRequest(url: AppSchemeHandler.startURL))')]
check(re.search(r'forName: UIApplication\.willResignActiveNotification, object: nil, queue: \.main\) \{ \[weak self\] _ in\n\s+Task \{ @MainActor in self\?\.event\("audio", \["why": "resign"\]\) \}', sw)
      and blk.index('guard UIApplication.shared.applicationState == .active else { return }') < blk.index('AudioWake.activate()') < blk.index('"why": "interruption"')
      and sw.count('AudioWake.activate()') == 2 and '"why": "active"' in sw,
      '④ アプリ（TengelWebView.swift）：willResignActive → audio（resign）・とぎれが おわった 知らせは アプリが 前に いる ときだけ 起こす')

SRV = os.path.join(W, 'srv_v238'); PORT = 8866; APP = f'http://localhost:{PORT}/APP/'
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
env0 = {k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict(env0, HIST='hist_280.json', DROP='', TARGET='app'))
pth = os.path.join(SRV, 'APP', 'index.html'); page = open(pth, encoding='utf8').read()
assert "window.__NATIVE = location.protocol === 'tengel:';" in page
open(pth, 'w', encoding='utf8').write(page.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
BL = os.environ.get('KISEKAE_ASSETS') or os.path.join(W, 'ios', 'kisekae_blobs')
if os.path.isdir(BL):
    for f in os.listdir(BL):
        shutil.copy(os.path.join(BL, f), os.path.join(SRV, 'APP', 'ks_' + f))
from assets_dir import adir
TCA = adir('tc_assets'); HAVE_TC = os.path.isdir(TCA) and len(os.listdir(TCA)) > 100 and os.path.exists(os.path.join(TCA, 'tc_sign.webp'))
if HAVE_TC:
    for f in os.listdir(TCA): shutil.copy(os.path.join(TCA, f), os.path.join(SRV, 'APP', f))
NT = open(os.path.join(W, 'test_native.py'), encoding='utf8').read()
FAKE = re.search(r'\nFAKE = """(.*?)"""', NT, re.S).group(1)
GATE_GONE = "() => { const g = document.querySelector('#gate'); return !g || g.hidden || getComputedStyle(g).display === 'none'; }"
TC_OPEN = "() => window.TCApp && document.querySelector('#tcOv.on') && !document.querySelector('#tcOv .tcld')"
HID = "(h) => { Object.defineProperty(document, 'hidden', { configurable: true, get: () => h }); document.dispatchEvent(new Event('visibilitychange')); }"
FXS = "() => { const W = window.TengelAudioWake, i = W.list.findIndex(q => q.name === 'fx'), c = i >= 0 ? W._ctx(i) : null; return { st: c ? c.state : null, h: W.hushed }; }"
TCS = "() => { const S = TCApp._snd; return { st: S.ac ? S.ac.state : null, bed: S.bed, h: TengelAudioWake.hushed }; }"
NAT = "(w) => window.__nativeEvent('audio', { why: w })"


def boot(pg):
    pg.goto(APP); pg.wait_for_timeout(1500)
    if pg.locator('#gateGo').count(): pg.click('#gateGo'); pg.wait_for_timeout(700)
    pg.wait_for_function(GATE_GONE, timeout=10000); pg.wait_for_timeout(400)


errs = []
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
try:
    with sync_playwright() as p:
        # ---- ③ 音の 出口（ここの 効果音：fx）
        br = p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
        ctx = br.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo')
        ctx.add_init_script(FAKE)
        pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        boot(pg)
        pg.mouse.click(5, 420); pg.evaluate("() => TengelFx.prime()"); pg.wait_for_timeout(600)
        a0 = pg.evaluate(FXS)
        pg.evaluate(NAT, 'resign'); pg.wait_for_timeout(60); a1 = pg.evaluate(FXS)
        pg.evaluate(NAT, 'interruption'); pg.wait_for_timeout(1200); a2 = pg.evaluate(FXS)
        pg.evaluate(NAT, 'active'); pg.wait_for_timeout(1200); a3 = pg.evaluate(FXS)
        check(a0['st'] == 'running' and a1 == {'st': 'suspended', 'h': True} and a2 == {'st': 'suspended', 'h': True} and a3 == {'st': 'running', 'h': False},
              f'③ アプリの 知らせ resign → 出口を すぐ 止める（0.06秒で {a1["st"]}）・interruption では 起こさない（{a2["st"]}）・active で 起こす（{a3["st"]}）')
        pg.evaluate(HID, True); pg.wait_for_timeout(60); b1 = pg.evaluate(FXS)
        pg.evaluate(HID, False); pg.wait_for_timeout(1200); b2 = pg.evaluate(FXS)
        pg.evaluate(NAT, 'resign'); pg.wait_for_timeout(60); b3 = pg.evaluate(FXS)
        pg.mouse.click(5, 420); pg.wait_for_timeout(500); b4 = pg.evaluate(FXS)
        pg.evaluate("() => window.dispatchEvent(new Event('pagehide'))"); pg.wait_for_timeout(60); b5 = pg.evaluate(FXS)
        pg.evaluate(NAT, 'active'); pg.wait_for_timeout(1200); b6 = pg.evaluate(FXS)
        pg.evaluate("() => { delete document.hidden; }")
        check(b1['st'] == 'suspended' and b1['h'] and b2 == {'st': 'running', 'h': False} and b3['st'] == 'suspended' and b4 == {'st': 'running', 'h': False}
              and b5['st'] == 'suspended' and b6 == {'st': 'running', 'h': False},
              '③ 画面が かくれた → すぐ 止める・見えたら 起こす／止めた まま 画面に さわった（アプリは 前に いる）→ 起こす／pagehide → 止める')
        check(not errs, f'③ エラー なし {errs[:2]}')
        ctx.close(); br.close()
        if not HAVE_TC:
            print('※ トレーニングセンターの 絵（ios/tc_assets・tc_sign.webp）が ない ので、トレーニングセンターの 確かめは しない')
        else:
            b2r = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'])
            for (vw, vh, tag) in ((390, 844, 'iphone'), (375, 667, 'se')):
                c2 = b2r.new_context(viewport={'width': vw, 'height': vh}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo', has_touch=True)
                c2.add_init_script(FAKE)
                pg = c2.new_page(); e2 = []; pg.on('pageerror', lambda e: e2.append(str(e)))
                boot(pg)
                pg.locator('#tcFab').click(); pg.wait_for_function(TC_OPEN, timeout=90000); pg.wait_for_timeout(1500)
                if tag == 'iphone':
                    # ---- ③ トレーニングセンターの 音
                    pg.wait_for_function("() => TCApp._snd.bed && TCApp._snd.ac && TCApp._snd.ac.state === 'running'", timeout=15000)
                    t0 = pg.evaluate(TCS)
                    pg.evaluate(NAT, 'resign'); pg.wait_for_timeout(60); t1 = pg.evaluate(TCS)
                    pg.evaluate(NAT, 'active'); pg.wait_for_timeout(1200); t2 = pg.evaluate(TCS)
                    check(t0['st'] == 'running' and bool(t0['bed']) and t1['st'] == 'suspended' and t1['bed'] == t0['bed'] and t2['st'] == 'running' and t2['bed'] == t0['bed'] and not t2['h'],
                          f'③ トレーニングセンター：resign → フィールドの 音（{t0["bed"]}）の 出口が すぐ 止まる（0.06秒で {t1["st"]}）・active で 同じ 音の まま つづく（{t2["st"]}）')
                    pg.evaluate(HID, True); pg.wait_for_timeout(60); t3 = pg.evaluate(TCS)
                    pg.evaluate(HID, False); pg.wait_for_timeout(1500); t4 = pg.evaluate(TCS)
                    pg.evaluate("() => { delete document.hidden; }")
                    check(t3['st'] == 'suspended' and t3['bed'] is None and t4['st'] == 'running' and bool(t4['bed']),
                          f'③ トレーニングセンター：画面が かくれたら 0.06秒で 止まる（{t3["st"]}：前は 0.3秒 あと）・見えたら また 鳴る（{t4["bed"]}）')
                check(not e2, f'③ {tag}：エラー なし {e2[:2]}')
                c2.close()
            b2r.close()
finally:
    srv.terminate()
shutil.rmtree(SRV, ignore_errors=True)

# ---- ⑤ GitHub の Mac
st = open(os.path.join(W, 'ios', 'ci', 'selftest.js'), encoding='utf8').read(); rs = open(os.path.join(W, 'ios', 'ci', 'run.sh'), encoding='utf8').read()
check("step(R, 'audioQuiet'" in st and "window.__nativeEvent('audio', { why: 'resign' })" in st and "window.__nativeEvent('audio', { why: 'interruption' })" in st and "window.__nativeEvent('audio', { why: 'active' })" in st
      and st.index("step(R, 'audioQuiet'") < st.index("report('1', R);"),
      '⑤ selftest.js：audioQuiet（resign → interruption → active：本物の iOS の WebKit の 出口で）・report-1 の 前')
check('AUDPY=' in rs and 'audio quiet: $(python3 -c "$AUDPY"' in rs and 'audio quiet (ipad): $(python3 -c "$AUDPY"' in rs, '⑤ run.sh：audio quiet の 行（iPhone・iPad）')
pya = re.search(r"\nAUDPY='\n(.*?)\n'\n", rs, re.S).group(1)
q = lambda st, on=True, name='fx': {'name': name, 'state': st, 'on': on}
good = {'audioQuiet': {'api': True, 's0': [q('running'), q('suspended', False, 'cb')], 's1': [q('suspended'), q('suspended', False, 'cb')], 'h1': True,
                       's2': [q('suspended'), q('suspended', False, 'cb')], 'h2': True, 's3': [q('running'), q('suspended', False, 'cb')], 'h3': False}}
tmp = os.path.join(SHOT, '_audpy.json')
json.dump(good, open(tmp, 'w', encoding='utf8')); r1 = subprocess.run(['python3', '-c', pya, tmp], capture_output=True, text=True).stdout.strip()
good['audioQuiet']['s2'] = [q('running'), q('suspended', False, 'cb')]
json.dump(good, open(tmp, 'w', encoding='utf8')); r2 = subprocess.run(['python3', '-c', pya, tmp], capture_output=True, text=True).stdout.strip(); os.remove(tmp)
check(r1.endswith('-> OK') and '-> CHECK' in r2, f'⑤ AUDPY：よい 結果は OK・interruption で 起きたら CHECK（{r1[:90]}）')

print('合計', len(fails), 'NG' if fails else 'OK')
sys.exit(1 if fails else 0)
