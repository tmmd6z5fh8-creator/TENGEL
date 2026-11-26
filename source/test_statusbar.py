# 第4.224版の テスト：時計・電池の 帯（ステータスバー）の 色と 字の 白／黒（kisekae.js が アプリに 知らせる 値）
#   まさちゃん 2026/11/26 10:55「青四角のところ色壁紙の色と合わせることって可能？」（iPhone の いちばん 上の 時計・電池の 帯）
#   ・30テーマ × ライト／ダーク：送る 色＝上の 帯（header.top）の いちばん 上の 色（テーマの CSS から べつに 計算した 値と 同じ）
#   ・字の 白／黒：上の 帯の 字と 同じ 白／黒・その 色の 上で 読みにくい（明るさの 差 3 未満）ときは 反対
#   ・同じ 色を 2回 送らない・ダークモードを かえたら 送り直す・グラデーションの 向き（上むき・横・すき通る 色）
#   ・Web版には 入らない（kisekae.js は App Store版 だけ）
#   python3 test_statusbar.py   （SHOT=<フォルダ> で 画面を 写す）
#   ZIP=<App Store版 zip> python3 test_statusbar.py ：zip の 中の 本物の index.html（コメントを 消した あと）で 同じ ことを 確かめる
import os, re, shutil, subprocess, sys, time, zipfile
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv_sb'); PORT = 8791; APP = f'http://localhost:{PORT}/APP/'
SHOT = os.environ.get('SHOT'); ZIP = os.environ.get('ZIP')
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, TARGET='app'))
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'WEB')], check=True, stdout=subprocess.DEVNULL, env={k: v for k, v in os.environ.items() if k not in ('TENGEL_TEST', 'TARGET')})
pth = os.path.join(SRV, 'APP', 'index.html')
if ZIP:
    with zipfile.ZipFile(ZIP) as z:
        n = next(i for i in z.namelist() if i.endswith('/Resources/index.html'))
        open(pth, 'wb').write(z.read(n))
    print('■ zip の index.html：', os.path.basename(ZIP))
html = open(pth, encoding='utf8').read()
web = open(os.path.join(SRV, 'WEB', 'index.html'), encoding='utf8').read()
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c: fails.append(label)


print('■ 作った index.html')
check("call('statusBar', p)" in html and 'sbMeasure' in html, 'App Store版：上の 帯の 色を アプリに 知らせる（kisekae.js）')
check('statusBar' not in web and 'sbMeasure' not in web, 'Web版には 入らない')
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))

# ---- テーマの CSS から、上の 帯の いちばん 上の 色を べつに 計算する（kisekae.js とは べつの 書き方） ----
THEMES = {}
for tid, body in re.findall(r'html\[data-ks=\\?"([a-z0-9_]+)\\?"\]\{([^}]*)\}', html):
    d = dict(re.findall(r'--([a-zA-Z0-9-]+):([^;]*)', body))
    if 'ks-hd' in d: THEMES[tid] = d['ks-hd']
# 帯の 壁紙（シルバー・ゴールド）は 上の 帯に そのテーマ だけの グラデーション（.top{background-image:…}）が 上書きで 入る
for tid, img in re.findall(r'html\[data-ks=\\?"([a-z0-9_]+)\\?"\] \.top\{background-image:([^}]*)\}', html):
    if tid in THEMES: THEMES[tid] = img


def hex3(h):
    h = h.lstrip('#'); h = ''.join(c * 2 for c in h) if len(h) == 3 else h
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def split_top(s):
    out, d, cur = [], 0, ''
    for ch in s:
        d += ch == '('; d -= ch == ')'
        if ch == ',' and d == 0: out.append(cur.strip()); cur = ''
        else: cur += ch
    return out + ([cur.strip()] if cur.strip() else [])


def colors(s):
    return [hex3(m) if m.startswith('#') else [float(x) for x in re.findall(r'[\d.]+', m)][:3] + ([float(re.findall(r'[\d.]+', m)[3])] if len(re.findall(r'[\d.]+', m)) > 3 else [])
            for m in re.findall(r'#[0-9A-Fa-f]{6}\b|#[0-9A-Fa-f]{3}\b|rgba?\([^)]*\)', s)]


def want_color(hd):
    grads = [l for l in split_top(hd) if re.match(r'(repeating-)?linear-gradient\(', l)]
    if not grads: return colors(hd)[0][:3]
    g = grads[-1]; inner = g[g.index('(') + 1:g.rindex(')')]; args = split_top(inner); cs = colors(inner)
    head = args[0].strip(); up = False
    m = re.fullmatch(r'(-?[\d.]+)deg', head)
    if m: import math; up = math.cos(math.radians(float(m.group(1)))) > .01
    elif head.startswith('to '): up = 'top' in head
    c = cs[-1] if up else cs[0]
    return [round(x) for x in c[:3]]


def lum(c):
    f = lambda v: (v / 255) / 12.92 if v / 255 <= .04045 else ((v / 255 + .055) / 1.055) ** 2.4
    return .2126 * f(c[0]) + .7152 * f(c[1]) + .0722 * f(c[2])


def con(a, b):
    x, y = lum(a), lum(b); return (max(x, y) + .05) / (min(x, y) + .05)


def want_light(bg, ink):
    w = con(ink, [255] * 3) < con(ink, [0] * 3)
    mine, other = con(bg, [255] * 3 if w else [0] * 3), con(bg, [0] * 3 if w else [255] * 3)
    return w if (mine >= 3 or mine >= other) else (not w)


hexs = lambda c: '#' + ''.join(f'{round(v):02X}' for v in c[:3])
print(f'■ テーマ {len(THEMES)}こ（上の 帯の CSS）')
check(len(THEMES) == 30, f'着せ替えは 30テーマ（{len(THEMES)}）')

srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
FAKE = open(os.path.join(W, 'test_tc.py'), encoding='utf8').read().split('FAKE = """')[1].split('"""')[0]
FAKE = FAKE.replace('var P = m.payload, val = true;', "var P = m.payload, val = true; if (m.name === 'statusBar') { (window.__sb = window.__sb || []).push(P); val = P; }")
assert "m.name === 'statusBar'" in FAKE


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


try:
    with sync_playwright() as p:
        br = p.chromium.launch()
        for scheme in ('light', 'dark'):
            print(f'■ {scheme}')
            ctx = br.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, color_scheme=scheme)
            ctx.add_init_script(FAKE)
            pg = ctx.new_page(); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.goto(APP); pg.wait_for_function('window.TengelKisekae && window.__sb && window.__sb.length > 0', timeout=20000)
            first = pg.evaluate('window.__sb.slice()')
            base = '#16203D' if scheme == 'light' else '#090E1C'
            check(len(first) == 1 and first[0] == {'color': base, 'light': True}, f'起動の 瞬間に 1回：いつもの 上の 帯の 色 {base}・白い 字（{first}）')
            gate(pg); pg.wait_for_timeout(600)
            check(len(pg.evaluate('window.__sb')) == 1, '入口の 画面を 閉じても 同じ 色は 送り直さない')
            bad = []
            for tid in sorted(THEMES):
                n0 = pg.evaluate('window.__sb.length')
                pg.evaluate("id => { if (id === 'default') delete document.documentElement.dataset.ks; else document.documentElement.dataset.ks = id; }", tid)
                pg.wait_for_timeout(120)
                got = pg.evaluate('window.__sb[window.__sb.length - 1]')
                info = pg.evaluate("() => { const h = document.querySelector('header.top'), s = getComputedStyle(h); return { ink: s.color, img: s.backgroundImage.slice(0, 120), bgc: s.backgroundColor }; }")
                ink = [float(x) for x in re.findall(r'[\d.]+', info['ink'])][:3]
                wc = hex3(base) if tid == 'default' else want_color(THEMES[tid])
                wl = want_light(wc, ink)
                ok = got['color'] == hexs(wc) and got['light'] is wl
                same = pg.evaluate('window.__sb.length') - n0 <= 1
                print(f"    {tid:10} {got['color']} {'白' if got['light'] else '黒'}  上の帯の字 {hexs(ink)}  {'' if ok and same else '← ちがう（' + hexs(wc) + ' ' + ('白' if wl else '黒') + '）'}")
                if not (ok and same): bad.append(tid)
                if SHOT and tid in ('ranch', 'carousel', 'cute', 'kirie', 'sunset', 'default', 'lucky', 'golden'):
                    os.makedirs(SHOT, exist_ok=True); pg.screenshot(path=os.path.join(SHOT, f'sb_{scheme}_{tid}.png'), clip={'x': 0, 'y': 0, 'width': 390, 'height': 140})
            check(not bad, f'30テーマ：色と 字の 白／黒（{bad or "ぜんぶ OK"}）')
            # 同じ テーマを もう一度 → 送らない
            n0 = pg.evaluate('window.__sb.length'); pg.evaluate("() => { const v = document.documentElement.dataset.ks; if (v) document.documentElement.dataset.ks = v; }"); pg.wait_for_timeout(150)
            check(pg.evaluate('window.__sb.length') == n0, '同じ テーマを 入れ直しても 送らない')
            # TengelKisekae.apply（本物の 着せ替え）でも 送る・statusBar()／statusBarNow() が 同じ
            pg.evaluate("() => window.TengelKisekae.apply('sunset')"); pg.wait_for_timeout(400)
            sb, now, last = pg.evaluate('[window.TengelKisekae.statusBar(), window.TengelKisekae.statusBarNow(), window.__sb[window.__sb.length - 1]]')
            check(sb == now == last == {'color': '#24123A', 'light': True}, f"着せ替え（夕焼け）：送った 色・はかり直した 色・アプリに 届いた 色が 同じ（{sb}）")
            pg.evaluate("() => window.TengelKisekae.apply('default')"); pg.wait_for_timeout(400)
            check(pg.evaluate('window.__sb[window.__sb.length - 1]') == {'color': base, 'light': True}, 'いつもの に もどすと 元の 色')
            # ダークモードを かえる → 送り直す
            other = 'dark' if scheme == 'light' else 'light'; ob = '#090E1C' if other == 'dark' else '#16203D'
            pg.emulate_media(color_scheme=other); pg.wait_for_timeout(300)
            check(pg.evaluate('window.__sb[window.__sb.length - 1]') == {'color': ob, 'light': True}, f'{other} に かえたら 送り直す（{ob}）')
            pg.emulate_media(color_scheme=scheme); pg.wait_for_timeout(300)
            # グラデーションの 向き・すき通る 色（上の 帯に 直接 書いて ためす）
            cases = [('linear-gradient(to top, rgb(255, 0, 0), rgb(0, 0, 255))', '#0000FF'), ('linear-gradient(0deg, rgb(255, 0, 0), rgb(0, 0, 255))', '#0000FF'),
                     ('linear-gradient(90deg, rgb(255, 0, 0), rgb(0, 0, 255))', '#FF0000'), ('linear-gradient(rgb(10, 20, 30), rgb(200, 200, 200))', '#0A141E'),
                     ('linear-gradient(to bottom right, rgb(1, 2, 3), rgb(9, 9, 9))', '#010203'), ('linear-gradient(-45deg, rgb(1, 2, 3), rgb(9, 9, 9))', '#090909'),
                     ('radial-gradient(rgba(255, 255, 255, 0.5) 1px, transparent 2px) 0 0/10px 10px, linear-gradient(rgb(40, 50, 60), rgb(0, 0, 0))', '#28323C'),
                     ('linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)) rgb(255, 255, 255)', '#808080'), ('rgb(18, 52, 86)', '#123456')]
            got = []
            for bg, want in cases:
                r = pg.evaluate("bg => { const h = document.querySelector('header.top'); h.style.background = bg; const v = window.TengelKisekae.statusBarNow(); h.style.background = ''; return v; }", bg)
                got.append((bg[:40], r and r['color'], want))
            check(all(g == w for _, g, w in got), 'グラデーションの 向き（上むき・横・ななめ）・模様の 層・すき通る 色：' + ('OK' if all(g == w for _, g, w in got) else str([x for x in got if x[1] != x[2]])))
            check(not errs, f'画面の エラーなし（{errs[:3]}）')
            ctx.close()
        br.close()
finally:
    srv.terminate()
print('合計', len(fails), 'NG' if fails else 'OK')
sys.exit(1 if fails else 0)
