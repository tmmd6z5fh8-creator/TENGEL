# 聞きくらべの ページを 手元の Chromium で 動かして たしかめる（音の 出口は にせもの：時間は 進む）
#   python3 kisekae/qsnd_ab/test_page.py <ページの フォルダ> <スクショの フォルダ> <作業フォルダ>
import http.server, json, os, socketserver, sys, threading
from playwright.sync_api import sync_playwright
ROOT, SHOT, W = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(SHOT, exist_ok=True)
class Q(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
srv = Q(('127.0.0.1', 0), type('H2', (http.server.SimpleHTTPRequestHandler,), {'log_message': lambda *a: None, '__init__': lambda self, *a, **k: http.server.SimpleHTTPRequestHandler.__init__(self, *a, directory=ROOT, **k)}))
port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = f'http://127.0.0.1:{port}/_local.html'
ok = ng = 0
def chk(c, t, extra=''):
    global ok, ng
    if c: ok += 1; print('✅', t)
    else: ng += 1; print('❌', t, extra)

with sync_playwright() as pw:
    br = pw.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    def page(w, h, scheme='light', scale=1):
        cx = br.new_context(viewport={'width': w, 'height': h}, color_scheme=scheme, device_scale_factor=scale, permissions=['clipboard-read', 'clipboard-write'])
        pg = cx.new_page()
        errs = []
        pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
        pg.on('pageerror', lambda e: errs.append('pageerror ' + str(e)))
        pg.route('**/fonts.googleapis.com/**', lambda r: r.fulfill(status=200, content_type='text/css', body=''))      # 手元では 字の 取り寄せは しない
        pg.goto(URL); pg.wait_for_function('!!window.__kiki')
        return cx, pg, errs
    cx, pg, errs = page(390, 844)
    K = lambda js: pg.evaluate('(() => { const k = window.__kiki; return ' + js + '; })()')
    gains = lambda: K('k.cur() ? [k.cur().ga.gain.value, k.cur().gb.gain.value, k.cur().mg.gain.value] : null')
    # ---- はじめの 画面 ----
    chk(pg.locator('#list .area').count() == 12, 'エリアの カード 12')
    chk(pg.locator('#list button.row').count() == 30 and pg.locator('#list .row.off').count() == 7, 'くらべる 行 30・今の まま 7')
    chk(pg.inner_text('#f-n') == '30' and pg.inner_text('#f-mb') == '3.1' and pg.inner_text('#f-mb2') == 'zip 195.0 → 191.8MB' and pg.inner_text('#f-n2') == 'BGM 12・効果音 18', '帯の 数字', pg.inner_text('.facts'))
    chk(pg.inner_text('#p-name') == 'Lv1 若草の原・BGM' and pg.inner_text('#p-time') == '0:00 / 0:09', 'はじめは Lv1 BGM が えらばれて いる（止まって いる）', pg.inner_text('#p-name') + ' ' + pg.inner_text('#p-time'))
    chk(K('document.documentElement.scrollWidth <= window.innerWidth'), '横に はみ出さない（390）', str(K('[document.documentElement.scrollWidth, window.innerWidth]')))
    chk(pg.locator('#tb tr').count() == 37, 'くわしい 数字の 表 37行')
    chk(pg.inner_text('#k-off') == '7' and '軽くしてもほとんどへらないので、今のまま' in pg.inner_text('#list') and '軽くしても 0KB' not in pg.inner_text('#list'), '今の ままの 7こ の 説明')
    ph = K('document.getElementById("player").offsetHeight'); print('   プレーヤーの 高さ', ph)
    chk(K('getComputedStyle(document.documentElement).getPropertyValue("--ph").trim()') == f'{ph}px', '本文の 下の あき＝プレーヤーの 高さ')
    pg.screenshot(path=f'{SHOT}/phone_light_top.png')
    # ---- 鳴らす：Lv1 BGM ----
    pg.click('#row-bgm01'); pg.wait_for_function('window.__kiki.st.playing')
    c = K('({id: k.cur().id, off: k.cur().off, loop: [k.cur().sa.loop, k.cur().sa.loopStart, k.cur().sa.loopEnd], lb: [k.cur().sb.loop, k.cur().sb.loopStart, k.cur().sb.loopEnd], la: k.dec.get("bgm01").a.length, lbn: k.dec.get("bgm01").b.length, sr: k.ctx().sampleRate, state: k.ctx().state})')
    chk(c['id'] == 'bgm01' and c['off'] == 0 and c['loop'] == [True, 3.0, 9.95] and c['lb'] == c['loop'], 'Lv1 BGM：頭から・くり返し 3.0〜9.95秒（2つとも 同じ）', json.dumps(c))
    chk(c['la'] == c['lbn'] and c['state'] == 'running', f"ほどいた 長さが 同じ（{c['la']} サンプル・{c['sr']}Hz）", json.dumps(c))
    pg.wait_for_timeout(900)
    g = gains(); chk(g[0] == 1 and g[1] == 0 and abs(g[2] - 0.45) < 0.01, '今の 音 だけ 鳴る・大きさ 0.45（0.6秒で 入る）', str(g))
    chk(pg.locator('#row-bgm01.is-cur.is-play').count() == 1 and pg.get_attribute('#b-play', 'aria-label') == '止める', '行と ボタンが 鳴って いる 形')
    p0 = K('k.pos()'); pg.click('#b-b'); pg.wait_for_timeout(120); p1 = K('k.pos()'); g = gains()
    chk(g[0] < 0.01 and g[1] > 0.99 and 0.05 < p1 - p0 < 0.6 and K('k.st.sel') == 'b', '軽い 音へ：同じ 場所の まま（頭に もどらない）', f'{g} {p0} {p1}')
    chk(K('k.mem().heard.bgm01.a === 1 && k.mem().heard.bgm01.b === 1') and pg.inner_text('#row-bgm01 .chip') == '聞いた', '2つとも 聞いた → 行に「聞いた」')
    # ---- 当てっこ ----
    pg.click('#b-x'); pg.wait_for_timeout(120)
    x = K('k.st.x.bgm01'); g = gains()
    chk(x in ('a', 'b') and ((g[0] > 0.99) == (x == 'a')) and ((g[1] > 0.99) == (x == 'b')), '？：どちらかが 鳴る', f'{x} {g}')
    chk(pg.is_visible('#p-abx') and not pg.is_visible('#p-judge') and '？はどちらか' in pg.inner_text('#p-msg'), '？の とき：答えの ボタンが 出る')
    pg.click('#b-a'); pg.wait_for_timeout(80); pg.click('#b-x'); pg.wait_for_timeout(80)
    chk(K('k.st.x.bgm01') == x, '今の音 → ？ と もどっても、？の 正体は かわらない（答える まで）')
    pg.click('#b-ga' if x == 'a' else '#b-gb'); pg.wait_for_timeout(80)
    g2 = gains()
    chk(K('k.mem().abx.bgm01.n === 1 && k.mem().abx.bgm01.ok === 1') and K('k.st.sel') == x and '当たり！' in pg.inner_text('#p-msg') and K('k.st.x.bgm01 === undefined'), '当てた：1回中 1回・正体の ボタンに 光が うつる・次は 引き直す', pg.inner_text('#p-msg'))
    chk(abs(g2[0] - g[0]) < 0.01 and abs(g2[1] - g[1]) < 0.01 and K('k.st.playing'), '答えても 鳴って いる 音は かわらない')
    pg.click('#b-x'); pg.wait_for_timeout(60); x2 = K('k.st.x.bgm01'); pg.click('#b-gb' if x2 == 'a' else '#b-ga'); pg.wait_for_timeout(60)
    chk(K('k.mem().abx.bgm01.n === 2 && k.mem().abx.bgm01.ok === 1') and 'はずれ' in pg.inner_text('#p-msg'), 'はずした：2回中 1回', pg.inner_text('#p-msg'))
    # ---- しるし ----
    pg.click('#b-same')
    chk(pg.inner_text('#row-bgm01 .chip') == '同じ' and pg.inner_text('#f-done') == '1' and pg.inner_text('#s-same') == '1' and pg.inner_text('#s-rest') == '29', '「同じ」→ 行・帯・まとめに 出る')
    # ---- バーで 場所を えらぶ ----
    bb = pg.locator('#bar').bounding_box(); pg.mouse.click(bb['x'] + bb['width'] * 0.5, bb['y'] + bb['height'] / 2); pg.wait_for_timeout(150)
    p = K('k.pos()'); chk(abs(p - 9.95 / 2) < 0.5 and K('k.st.playing'), f'バーの まん中 → その 場所から 鳴る（{p:.2f}秒）')
    pg.wait_for_timeout(5400); p = K('k.pos()'); chk(3.0 <= p < 9.95, f'くり返しの おわりを こえたら 3.0秒へ もどる（{p:.2f}秒）')
    # ---- つぎの 音 ----
    pg.click('#b-next'); pg.wait_for_function('window.__kiki.st.playing && window.__kiki.st.cur === "bgm02"')
    chk(K('k.st.sel') == 'a' and pg.inner_text('#p-name') == 'Lv2 風見峠・BGM', 'つぎの 音：Lv2 BGM（今の 音から）')
    # ---- 効果音：おわったら 止まる → 押した 方が 頭から ----
    pg.click('#row-se12b'); pg.wait_for_function('window.__kiki.st.playing && window.__kiki.st.cur === "se12b"')
    g = gains(); chk(g[0] == 1 and g[1] == 0 and abs(g[2] - 0.9) < 0.001 and K('k.cur().sa.loop === false'), '効果音：今の 音から・大きさ 0.9（いきなり）・くり返さない', str(g))
    pg.wait_for_function('!window.__kiki.st.playing', timeout=6000)
    chk(pg.inner_text('#p-time') == '0:00 / 0:02' and pg.get_attribute('#b-play', 'aria-label') == '鳴らす', '効果音が おわったら 止まる')
    pg.click('#b-b'); pg.wait_for_function('window.__kiki.st.playing'); g = gains()
    chk(g[1] == 1 and g[0] == 0 and K('k.cur().off') == 0, '止まって いる ときに「軽い音」→ 軽い 音が 頭から')
    pg.click('#b-diff'); chk(pg.inner_text('#row-se12b .chip') == 'ちがう' and pg.inner_text('#s-diff') == '1', '「ちがう」')
    chk('ちがう音：Lv12 日蝕の玉座・2タップ目の音' in pg.inner_text('#s-text') and '当てっこ：2回中 1回当たり' in pg.inner_text('#s-text') and '約3.1MB' in pg.inner_text('#s-say'), 'まとめの 文', pg.inner_text('#s-text') + ' / ' + pg.inner_text('#s-say'))
    # ---- 行を もう 1回 → 止まる ----
    pg.click('#row-se12b') if K('k.st.playing') else None
    pg.click('#row-bgm11'); pg.wait_for_function('window.__kiki.st.playing && window.__kiki.st.cur === "bgm11"', timeout=15000)
    pg.click('#row-bgm11'); chk(not K('k.st.playing') and K('k.cur() === null'), '鳴って いる 行を もう 1回 → 止まる')
    # ---- しぼりこみ ----
    pg.click('#t-hot')
    chk(pg.locator('#list button.row:visible').count() == 9 and pg.locator('#list .row.off:visible').count() == 0 and pg.locator('#list .area:visible').count() == 8, '◆ だけ：9行（エリア 8）', str([pg.locator('#list button.row:visible').count(), pg.locator('#list .area:visible').count()]))
    pg.click('#b-next'); pg.wait_for_function('window.__kiki.st.playing'); chk(K('k.st.cur') == 'se12b', '◆ だけの とき：つぎの 音は ◆ の 中で（Lv11 BGM → Lv12 2タップ目）', K('k.st.cur'))
    pg.click('#b-play'); pg.click('#t-all'); chk(pg.locator('#list button.row:visible').count() == 30, 'ぜんぶに もどす')
    # ---- コピー・消す ----
    pg.click('#b-copy'); pg.wait_for_timeout(200)
    chk(pg.evaluate('navigator.clipboard.readText()') == pg.inner_text('#s-text') and pg.inner_text('#b-copy') == 'コピーしたよ', 'まとめを コピー')
    pg.click('#b-reset'); chk(pg.inner_text('#b-reset') == 'もう一回押すと消えるよ' and pg.inner_text('#s-same') == '1', '消す：1回目は たしかめ だけ')
    pg.click('#b-reset'); chk(pg.inner_text('#s-same') == '0' and pg.inner_text('#s-diff') == '0' and pg.inner_text('#f-done') == '0' and pg.inner_text('#row-bgm01 .chip') == '', '消す：2回目で 消える')
    # ---- おぼえて いる（開き直し）----
    pg.click('#row-bgm03'); pg.wait_for_function('window.__kiki.st.playing'); pg.click('#b-diff'); pg.click('#b-play')
    pg.reload(); pg.wait_for_function('!!window.__kiki')
    chk(pg.inner_text('#row-bgm03 .chip') == 'ちがう' and pg.inner_text('#s-diff') == '1', '開き直しても しるしは のこる')
    # ---- ほどいた 2つの 音の 位置（このブラウザで）：ぜんぶの 音で 長さが 同じ・ずれ 0 ----
    r = pg.evaluate('''async () => {
      const k = window.__kiki, C = new (window.AudioContext || window.webkitAudioContext)(), out = [];
      const ids = Array.from(document.querySelectorAll('#list button.row')).map(e => e.dataset.id);
      for (const id of ids) {
        const f = 'cb_q_' + id + '.mp3';
        const [a, b] = await Promise.all(['a/', 'b/'].map(d => fetch(d + f).then(r => r.arrayBuffer()).then(x => C.decodeAudioData(x))));
        const x = a.getChannelData(0), y = b.getChannelData(0), n = Math.min(x.length, y.length, C.sampleRate * 3);
        let best = -1e9, lag = 0;
        for (let L = -40; L <= 40; L++) { let s = 0; for (let i = 40; i < n - 40; i += 3) s += x[i] * y[i + L]; if (s > best) { best = s; lag = L; } }
        let e = 0, d = 0; for (let i = 0; i < Math.min(x.length, y.length); i++) { e += x[i] * x[i]; d += (x[i] - y[i]) * (x[i] - y[i]); }
        out.push([id, a.length, b.length, lag, Math.round(10 * Math.log10(e / Math.max(d, 1e-30)) * 10) / 10, a.numberOfChannels, b.numberOfChannels]);
      }
      return out;
    }''')
    bad = [x for x in r if x[1] != x[2] or x[3] != 0 or x[5] != x[6]]
    chk(len(r) == 30 and not bad, 'Chromium で ほどいた 2つの 音：30こ とも 長さが 同じ・ずれ 0・チャンネルの 数が 同じ', str(bad))
    meta = {m['f']: m for m in json.load(open(W + '/meta_raw.json'))}
    far = [(x[0], x[4], meta['cb_q_' + x[0] + '.mp3']['snr']) for x in r if abs(x[4] - meta['cb_q_' + x[0] + '.mp3']['snr']) > 3]
    chk(not far, 'ちがいの 小ささ（dB）が ffmpeg で 測った 数と 合う（左の 音・3dB より ずれない）', str(far))
    chk(not errs, 'コンソールの エラー なし', str(errs[:5]))
    # ---- 見た目（1回 だけ）----
    pg.click('#row-se07a'); pg.wait_for_function('window.__kiki.st.playing'); pg.click('#b-b'); pg.wait_for_timeout(700)
    pg.screenshot(path=f'{SHOT}/phone_light_play.png')
    pg.click('#b-x'); pg.wait_for_timeout(200); pg.screenshot(path=f'{SHOT}/phone_light_abx.png')
    pg.click('#b-play')
    pg.evaluate('document.getElementById("h-sum").scrollIntoView()'); pg.wait_for_timeout(200); pg.screenshot(path=f'{SHOT}/phone_light_sum.png')
    cx.close()
    cx, pg, errs2 = page(390, 844, 'dark')
    pg.click('#row-bgm09'); pg.wait_for_function('window.__kiki.st.playing'); pg.click('#b-same'); pg.wait_for_timeout(500)
    pg.evaluate('window.scrollTo(0, 560)'); pg.wait_for_timeout(200); pg.screenshot(path=f'{SHOT}/phone_dark_list.png')
    chk(pg.evaluate('document.documentElement.scrollWidth <= window.innerWidth') and not errs2, '暗い 画面：はみ出さない・エラー なし', str(errs2[:3]))
    cx.close()
    cx, pg, errs3 = page(1280, 800)
    pg.screenshot(path=f'{SHOT}/desk_light_top.png')
    pg.evaluate('window.scrollTo(0, 420)'); pg.wait_for_timeout(200); pg.screenshot(path=f'{SHOT}/desk_light_list.png')
    chk(pg.evaluate('document.documentElement.scrollWidth <= window.innerWidth') and not errs3, '広い 画面：はみ出さない・エラー なし', str(errs3[:3]))
    cx.close()
    cx, pg, errs4 = page(320, 640)
    chk(pg.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'せまい 画面（320）：はみ出さない', str(pg.evaluate('[document.documentElement.scrollWidth, window.innerWidth]')))
    cx.close(); br.close()
srv.shutdown()
print(f'\n合計 OK {ok}・NG {ng}')
sys.exit(1 if ng else 0)
