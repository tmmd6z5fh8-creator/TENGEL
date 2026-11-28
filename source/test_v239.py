# 第4.239版の テスト（まさちゃん 2026/11/28 15:40「作戦会議で、このパターンは名前だけが読み取れないみたいだから、名前は読み取れなくても、場所とRだけは読み取れるようにできる？
#   名前が読み取れる場合はそのまま読み取ってほしい！」「名前が読み取れる場合も、場所とRは入れてね！」：画像 2枚＝出馬表の 画面〈日付ごとの 開催場の ボタン・
#   「開催選択へ レース選択へ」・1R〜12R の 切りかえ・「2026年11月28日(土曜) 5回京都7日」・大きく「12R」と「3歳以上 2勝クラス」〉）
#   ① 読み取り（ocr_local.js）：架空の 出馬表（make_mock.py の g_card・g_card_t・h_card）→ 開催場 京都／東京（「5回京都7日」：前は「ス選択へ」）・12R／11R・
#      レース名「3歳以上2勝クラス」（特別で ない レースは クラス：前は「(混合)(特指) 定量」）／「テンゲルステークス」・距離・発走。前の 見本（a〜f）は 1つも かわらない
#   ② 作戦会議の レースの 予約：レース名の 欄は「開催場＋R」と 読めた レース名（そのまま）＝「京都12R 3歳以上2勝クラス」「京都11R テンゲルステークス」・
#      名前だけ 読めた ときは 名前の まま・案内に「開催場・R」も。説明の 字・入れる 例
#   ③ お気に入りレースの 札：名前に 開催場と R が ある ときは 下の 行に もう 書かない・名前が ない ときは「京都12R」。お知らせの 字も
#   ④ GitHub の Mac（selftest.js の ocrcard・run.sh の CARDPY・ci/ocr の 画像は testdata と 同じ）
#   ⑤ 写真：t4/v239_plan.png
#   python3 test_v239.py
import json, os, re, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
sys.path.insert(0, W)
SHOT = os.path.join(W, 't4'); os.makedirs(SHOT, exist_ok=True)
D = os.path.join(W, 'testdata', 'ocr')
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c:
        fails.append(label)


# ---- ① 読み取り
JS = r"""
const O = require('./ocr_local.js'), fs = require('fs'), path = require('path');
const out = {};
for (const f of fs.readdirSync(process.argv[1]).filter(f => f.endsWith('.json'))) {
  const L = JSON.parse(fs.readFileSync(path.join(process.argv[1], f), 'utf8')).lines, d = O.parse([L]);
  out[f.replace('.json', '')] = { venue: d.venue, r: d.r, rname: d.rname, date: d.date, dist: d.dist, start: d.start, n: d.n };
}
console.log(JSON.stringify(out));
"""
res = json.loads(subprocess.run(['node', '-e', JS, D], capture_output=True, text=True, check=True).stdout)
want = {'g_card': ('京都', 12, '3歳以上2勝クラス', 1200, '16:15'), 'g_card_t': ('東京', 12, '3歳以上1勝クラス', 2400, '16:01'), 'h_card': ('京都', 11, 'テンゲルステークス', 1600, '15:35')}
for k, (v, r, nm, dist, st) in want.items():
    d = res.get(k) or {}
    check(d.get('venue') == v and d.get('r') == r and d.get('rname') == nm and d.get('dist') == dist and d.get('start') == st and d.get('date') == '2026-11-28',
          f'① 架空の 出馬表 {k} → 開催場 {d.get("venue")}・{d.get("r")}R・レース名「{d.get("rname")}」・{d.get("dist")}m・発走 {d.get("start")}')
old = subprocess.run(['git', '-C', os.path.dirname(W), 'show', '250b4048:source/ocr_local.js'], capture_output=True, text=True, check=True).stdout
tmp = os.path.join(SHOT, '_ocr_old.js'); open(tmp, 'w', encoding='utf8').write(old)
res0 = json.loads(subprocess.run(['node', '-e', JS.replace("require('./ocr_local.js')", 'require(' + json.dumps(tmp) + ')'), D], capture_output=True, text=True, check=True).stdout); os.remove(tmp)
LATER = {'i_card'}      # 第4.241版で 足した 見本（あすの 出馬表：test_v241・test_ocr_local.js で 見る）は 前の 版とは くらべない
prev = [k for k in res if k not in want and k not in LATER]
same = [k for k in prev if res[k] == res0.get(k)]
check(len(same) == len(prev) and res0['g_card']['venue'] == 'ス選択へ' and res0['g_card']['rname'] == '(混合)(特指) 定量',
      f'① 前の 見本 {len(same)}こ（{", ".join(sorted(same))}）は 1つも かわらない・前の 版では 開催場「{res0["g_card"]["venue"]}」・レース名「{res0["g_card"]["rname"]}」だった')

# ---- ②③ 作戦会議
SRV = os.path.join(W, 'srv_v239'); PORT = 8868; APP = f'http://localhost:{PORT}/APP/'
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
env0 = {k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict(env0, HIST='hist_280.json', DROP='', TARGET='app'))
pth = os.path.join(SRV, 'APP', 'index.html'); page = open(pth, encoding='utf8').read()
assert "window.__NATIVE = location.protocol === 'tengel:';" in page
open(pth, 'w', encoding='utf8').write(page.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
NT = open(os.path.join(W, 'test_native.py'), encoding='utf8').read()
FAKE = re.search(r'\nFAKE = """(.*?)"""', NT, re.S).group(1)
GATE_GONE = "() => { const g = document.querySelector('#gate'); return !g || g.hidden || getComputedStyle(g).display === 'none'; }"
load = lambda n: json.load(open(os.path.join(D, n + '.json'), encoding='utf8'))['lines']
Wd = lambda t, x, y, w, h=0.014: {'text': t, 'x': x, 'y': y, 'w': w, 'h': h}
errs = []
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
try:
    with sync_playwright() as p:
        br = p.chromium.launch()
        ctx = br.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo')
        ctx.add_init_script(FAKE)
        pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(APP); pg.wait_for_timeout(1500)
        if pg.locator('#gateGo').count(): pg.click('#gateGo'); pg.wait_for_timeout(700)
        pg.wait_for_function(GATE_GONE, timeout=10000); pg.wait_for_timeout(400)
        pg.evaluate("() => { localStorage.removeItem('tengel.plan'); window.TCPlanOpen(); }")
        pg.wait_for_function("() => document.querySelector('#tcPlan [data-p=add]')", timeout=30000); pg.wait_for_timeout(300)
        pl = pg.locator('#tcPlan')
        pl.locator('[data-p=add]').click(); pg.wait_for_timeout(400)
        fin = pl.locator('input[data-p=file]')
        hint = pg.evaluate("() => ({ h: document.querySelector('#tcPlan .ocrh').innerText, ph: document.querySelector('#tcPlan [data-f=name]').placeholder })")
        check('開催場・R・レース名・出走頭数・距離・発走時間を 読み取るよ' in hint['h'] and hint['ph'] == '例）〇〇11R 〇〇特別',
              f'② 説明「…開催場・R・レース名・出走頭数・距離・発走時間を 読み取るよ」・レース名の 欄の 例「{hint["ph"]}」')

        def read(lines, img='g_card'):
            pg.evaluate("(L) => { window.__ocrLines = L; }", [lines])
            fin.set_input_files([os.path.join(D, img + '.jpg')]); pg.wait_for_timeout(2200)
            return pg.evaluate("""() => { const r = document.querySelector('#tcPlan'), v = k => (r.querySelector(`[data-f="${k}"]`) || {}).value || '';
              return { name: v('name'), n: v('n'), dist: v('dist'), time: v('time'), msg: (r.querySelector('.om') || {}).innerText || '', left: window.__ocrLines.length }; }""")
        q1 = read(load('g_card'))
        check(q1['left'] == 0 and q1['name'] == '京都12R 3歳以上2勝クラス' and q1['dist'] == '1200' and q1['time'] == '16:15'
              and '読み取ったよ（開催場・R・レース名・距離・発走時間）' in q1['msg'] and '読めなかった：頭数' in q1['msg'],
              f'② 出馬表（特別で ない レース）→ レース名の 欄「{q1["name"]}」（開催場＋R＋クラス）・{q1["dist"]}m・{q1["time"]}・案内「{q1["msg"][:40]}…」')
        pg.screenshot(path=os.path.join(SHOT, 'v239_plan.png'))
        q2 = read(load('h_card'), 'h_card')
        check(q2['name'] == '京都11R テンゲルステークス' and q2['dist'] == '1600' and q2['time'] == '15:35', f'② 出馬表（特別の レース）→「{q2["name"]}」（名前は そのまま・前に 開催場と R）')
        q3 = read([Wd('テンゲル特別 A1', 0.05, 0.05, 0.4), Wd('ダート1400m', 0.05, 0.10, 0.3)])
        check(q3['name'] == 'テンゲル特別 A1' and '読めなかった：開催場・R・頭数・発走時間' in q3['msg'], f'② 名前だけ 読めた → 名前の まま「{q3["name"]}」・案内に「読めなかった：開催場・R…」')
        q4 = read([Wd('東京 京都', 0.05, 0.10, 0.6), Wd('2026年11月28日(土曜) 5回東京7日', 0.05, 0.40, 0.8), Wd('12R', 0.05, 0.45, 0.1), Wd('コース 2400m 芝・左 発走16:01', 0.05, 0.5, 0.7)])
        check(q4['name'] == '東京12R' and '読み取ったよ（開催場・R・距離・発走時間）' in q4['msg'] and '読めなかった：レース名・頭数' in q4['msg'],
              f'② 名前が 読めない → 開催場と R だけ「{q4["name"]}」')
        # 保存 → 札
        read(load('g_card')); pl.locator('[data-p=save]').click(); pg.wait_for_timeout(500)
        pg.evaluate("""() => { const P = JSON.parse(localStorage.getItem('tengel.plan')); P.on = true;
          P.races.push({ id: 'noname', date: P.races[0].date, time: '16:40', name: '', n: '', dist: 1400, venue: '京都', r: 12, memo: '', notify: [10] });
          P.races.forEach(r => { r.date = '2099-12-31'; r.notify = [10]; });
          localStorage.setItem('tengel.plan', JSON.stringify(P)); document.dispatchEvent(new CustomEvent('tengel:plan')); }""")
        pg.evaluate("() => { const c = document.querySelector('#tcPlan [data-p=close]'); if (c) c.click(); }"); pg.wait_for_timeout(300)
        pg.evaluate("() => window.TCPlanOpen()"); pg.wait_for_function("() => document.querySelector('#tcPlan .rc')", timeout=30000); pg.wait_for_timeout(300)
        cards = pg.evaluate("() => [...document.querySelectorAll('#tcPlan .rc')].map(c => ({ nm: c.querySelector('.nm').textContent, mt: (c.querySelector('.mt') || {}).textContent || '' }))")
        nts = pg.evaluate("() => window.TCPlanNotify().map(x => x.body)")
        c1 = next((c for c in cards if c['nm'].startswith('京都12R 3歳以上')), None); c2 = next((c for c in cards if c['nm'] == '京都12R'), None)
        check(bool(c1) and c1['mt'] == '1200m' and bool(c2) and c2['mt'] == '1400m',
              f'③ 札：「{c1 and c1["nm"]}」の 下の 行は「{c1 and c1["mt"]}」（開催場と R を もう 書かない）・名前が ない 札は「{c2 and c2["nm"]}」（下の 行「{c2 and c2["mt"]}」）')
        check(any(b.startswith('京都12R 3歳以上2勝クラス　16:15 発走') for b in nts) and any(b.startswith('京都12R　16:40 発走') for b in nts),
              f'③ お知らせの 字：{nts}')
        check(not errs, f'②③ エラー なし {errs[:2]}')
        ctx.close(); br.close()
finally:
    srv.terminate()
shutil.rmtree(SRV, ignore_errors=True)

# ---- ④ GitHub の Mac
st = open(os.path.join(W, 'ios', 'ci', 'selftest.js'), encoding='utf8').read(); rs = open(os.path.join(W, 'ios', 'ci', 'run.sh'), encoding='utf8').read()
same_img = all(open(os.path.join(W, 'ios', 'ci', 'ocr', n), 'rb').read() == open(os.path.join(D, n), 'rb').read() for n in ('g_card.jpg', 'h_card.jpg'))
check("step(R, 'ocrcard'" in st and "list = ['g_card', 'h_card']" in st and 'CARDPY=' in rs and 'ocr card: $(python3 -c "$CARDPY"' in rs and same_img,
      '④ GitHub の Mac：架空の 出馬表 2枚（ci/ocr：testdata と 同じ）を 本物の Vision で 読む（selftest.js の ocrcard・run.sh の ocr card の 行）')
pyc = re.search(r"\nCARDPY='\n(.*?)\n'\n", rs, re.S).group(1)
good = {'ocrcard': {'g_card': {'venue': '京都', 'r': 12, 'rname': '3歳以上2勝クラス', 'date': '2026-11-28', 'dist': 1200, 'start': '16:15'},
                    'h_card': {'venue': '京都', 'r': 11, 'rname': 'テンゲルステークス', 'date': '2026-11-28', 'dist': 1600, 'start': '15:35'}}}
tj = os.path.join(SHOT, '_cardpy.json')
json.dump(good, open(tj, 'w', encoding='utf8'), ensure_ascii=False); r1 = subprocess.run(['python3', '-c', pyc, tj], capture_output=True, text=True).stdout.strip()
good['ocrcard']['g_card']['venue'] = 'ス選択へ'
json.dump(good, open(tj, 'w', encoding='utf8'), ensure_ascii=False); r2 = subprocess.run(['python3', '-c', pyc, tj], capture_output=True, text=True).stdout.strip(); os.remove(tj)
check(r1.endswith('-> OK') and '-> CHECK' in r2, f'④ CARDPY：よい 結果は OK・開催場「ス選択へ」は CHECK（{r1[:80]}）')

print('合計', len(fails), 'NG' if fails else 'OK')
sys.exit(1 if fails else 0)
