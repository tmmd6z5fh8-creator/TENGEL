# 第4.235版の テスト（まさちゃん 2026/11/28 08:41「競馬新聞の壁紙、数字切り替わる速度15秒から7秒に変えて！
#   あと、牧場の名前変えようとしても入力するところが出てこないから改善して！」）
#   ① 競馬新聞：数字が かわるのは 7秒ごと（news_wall.TK_S）・説明（aria-label・着せ替えの 一覧）も 7秒・CSS の 動き（7秒で 1回り・うすく なるのは 0.4秒）
#   ② アプリの 中身（ks_news.json）：kbnsTk 7s・前の 15秒は ない
#   ③ アプリの 画面で ほんとうの 時間：数字の 層の 動きは 7000ms・速めない まま 17秒 見て、かわる あいだは 7秒（±0.3秒）・馬単は 3連単の 1着→2着
#   ④〜⑨（牧場の 看板の iOS の 窓：TengelNative.call('prompt')）は 第4.237版で やめた（iPadOS 27 の Swift Playgrounds で 動かした アプリは iOS の 窓でも
#      キーボードが 出ない：Apple の 不具合）→ 画面の 中の 窓＋かなキーボード（kanapad.js）の たしかめは test_v237.py
#   ⑧ GitHub の Mac の たしかめ（selftest.js・run.sh：ks-news の 合図・news tickets は 7000ms）
#   python3 test_v235.py
import json, os, re, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
K = os.path.join(W, 'kisekae'); sys.path.insert(0, K); sys.path.insert(0, W)
BL = os.environ.get('KISEKAE_ASSETS') or os.path.join(W, 'ios', 'kisekae_blobs')
SHOT = os.path.join(W, 't4'); os.makedirs(SHOT, exist_ok=True)
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c:
        fails.append(label)


import news_wall
# ---- ① 競馬新聞の 時間
TK = json.load(open(os.path.join(K, 'news_tk.json'), encoding='utf8'))
html, css = news_wall.inline(news_wall.load_blobs(os.path.join(K, 'news_blobs.json')), TK)
th = open(os.path.join(K, 'themes20.py'), encoding='utf8').read()
news_th = th[th.index("dict(id='news'"):th.index("dict(id='news'") + 4000]
check(news_wall.TK_S == 7 and news_wall.TK_FADE == 0.4 and '7秒ごと' in news_wall.ALT and '15秒' not in news_wall.ALT
      and f'aria-label="{news_wall.ALT}"' in html and 'animation:nsTk 7s linear infinite' in css
      and '@keyframes nsTk{0%{opacity:0}5.7143%{opacity:1}94.2857%{opacity:1}100%{opacity:0}}' in css and '15s' not in css,
      f'① 数字が かわるのは 7秒ごと（TK_S {news_wall.TK_S}・うすく なるのは 0.4秒）・説明「{news_wall.ALT[-14:]}」・CSS：7秒で 1回り（5.7143%〜94.2857% が こい）')
check("馬券の数字は7秒ごとにかわる" in news_th and '数字は7秒ごとに25組からランダム' in news_th and '馬券の数字は15秒' not in news_th,
      '① 着せ替えの 一覧の 説明（themes20.py の alt と 説明の 絵の 字）も 7秒')

# ---- ②〜③ アプリ
SRV = os.path.join(W, 'srv_v235'); PORT = 8862; APP = f'http://localhost:{PORT}/APP/'
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
kj = json.load(open(os.path.join(SRV, 'APP', 'ks_news.json'), encoding='utf8'))
check('animation:kbnsTk 7s linear infinite' in kj['bnr']['css'] and 'kbnsTk 15s' not in kj['bnr']['css'] and '7秒ごと' in kj['bnr']['html'] and '15秒' not in json.dumps(kj, ensure_ascii=False),
      '② アプリの 中身（ks_news.json）：数字の 層の 動き kbnsTk 7s・説明も 7秒・前の 15秒は どこにも ない')
GATE_GONE = "() => { const g = document.querySelector('#gate'); return !g || g.hidden || getComputedStyle(g).display === 'none'; }"


def boot(pg):
    pg.goto(APP); pg.wait_for_timeout(1500)
    if pg.locator('#gateGo').count(): pg.click('#gateGo'); pg.wait_for_timeout(700)
    pg.wait_for_function(GATE_GONE, timeout=10000); pg.wait_for_timeout(400)


errs, bad = [], []
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
try:
    with sync_playwright() as p:
        # ---- ③ ほんとうの 時間（速めない）
        br = p.chromium.launch()
        ctx = br.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo')
        pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        boot(pg)
        pg.evaluate("(id) => TengelKisekae.apply(id, false)", 'news')
        pg.wait_for_function("() => TengelKisekae.current() === 'news' && TengelKisekae.loaded() && !!document.querySelector('#ksBnr .nsq')", timeout=8000)
        pg.evaluate("window.scrollTo(0, 0)")
        an = pg.evaluate("() => document.querySelector('#ksBnr .nsq').getAnimations().map(a => [a.animationName, a.playState, a.effect.getComputedTiming().duration])")
        w = pg.evaluate("""(ms) => new Promise(res => { const q = document.querySelector('#ksBnr .nsq'), ch = [], bad = []; let last = q.dataset.tkn; const t0 = performance.now();
          const tick = () => { const k = q.dataset.tkn; if (k !== last) { last = k; ch.push(performance.now()); const v = [...q.querySelectorAll('[data-tki]')].map(e => e.textContent);
              if (v[0] !== v[2] || v[1] !== v[3] || v.some(x => !/^([1-9]|1[0-6])$/.test(x))) bad.push(v.join(' ')); }
            if (performance.now() - t0 < ms) requestAnimationFrame(tick); else res({ ch, bad }); }; tick(); })""", 17000)
        gaps = [round((b - a) / 1000, 2) for a, b in zip(w['ch'], w['ch'][1:])]
        check(an == [['kbnsTk', 'running', 7000]] and len(w['ch']) >= 2 and gaps and all(abs(g - 7) <= 0.3 for g in gaps) and not w['bad'],
              f'③ アプリの 画面（速めない）：数字の 層の 動き {an}・17秒で {len(w["ch"])}回 かわった・かわる あいだ {gaps}秒（7秒 ±0.3）・馬単は 3連単の 1着→2着・1〜16')
        check(not errs, f'③ エラー なし {errs[:2]}')
        ctx.close(); br.close()
finally:
    srv.terminate()
shutil.rmtree(SRV, ignore_errors=True)

# ---- ⑧ GitHub の Mac の たしかめ（第4.237版：iOS の 窓の たしかめ farm-prompt は やめた → test_v237.py の kana-pad）
st = open(os.path.join(W, 'ios', 'ci', 'selftest.js'), encoding='utf8').read(); rs = open(os.path.join(W, 'ios', 'ci', 'run.sh'), encoding='utf8').read()
P1 = re.search(r'\nP1="([^"]+)"', rs).group(1).split()
marks = set(re.findall(r"mark\('([a-z0-9-]+)'\)", st)) | {'gate-first'}
nomark = [m for m in P1 if not m.startswith('report-') and m not in marks]
check(not nomark and P1.index('ks-pack-wall') + 1 == P1.index('ks-news') and "else { res.newsTk = null; await mark('ks-news'); }" in st,
      f'⑧ GitHub の Mac：P1 の 合図の 順（ks-pack-wall → ks-news）・どの 合図も selftest.js に ある（ない もの：{nomark or "なし"}）・ks-news の 合図は どの 道でも 1回')
check('an[0][2] == 7000' in rs, '⑧ run.sh：news tickets は 7000ms')

print('合計', len(fails), 'NG' if fails else 'OK')
sys.exit(1 if fails else 0)
