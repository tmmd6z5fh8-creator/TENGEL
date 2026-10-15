# CM第2弾用：アプリの画面を撮る（架空のレース・架空のJRAデータ。このテスト用ブラウザの中だけ）
#  追加：買い目編集（タップ前後）・カスタム買い目の判定・マザーデータ（JRAに入れる流れ）・JRAデータでの判定・収支
#   python3 cm2_shots.py              … Web版の画面 → shots/
#   TARGET=app python3 cm2_shots.py   … App Store版の画面（アプリの中として開く・競馬場や団体・版の名前が出ない）→ shots_app/
#   TARGET=app CM_PREV=1 CM_VW=443 CM_VH=960 CM_DPR=2 CM_OUT=shots_prev python3 cm2_shots.py
#        … App Storeのプレビュー動画用（画面いっぱいに使うので、6.9インチのiPhoneと同じ幅443・886×1920にそのまま合う大きさ。買う馬を選ぶ前後の画面も撮る）
import json, os, random, shutil, subprocess, time
from playwright.sync_api import sync_playwright
SRC = '/home/claude/tengel/source'
APP = os.environ.get('TARGET') == 'app'
PREV = os.environ.get('CM_PREV') == '1'
# CM第7弾（CM7=1）：3枚の読み取り・券種とマザーデータのロック（ポイントで解放するイメージ）・単勝5連予想（0〜5レース・ランダム）・ポイント購入（イメージ）
#   ロックや購入の画面は、このテスト用ブラウザの中で画面に足して撮るだけ（アプリのソースは変えない）。「5重勝」は CM の画面だけ「単勝5連予想」に置きかえる
CM7 = os.environ.get('CM7') == '1'
# iPad（13インチ・幅1032）：タブは上（下のタブバーはない）。上の帯（タブつき）を場面ごとに撮る
IPAD = os.environ.get('CM_IPAD') == '1'
VW, VH, DPR = int(os.environ.get('CM_VW', '390')), int(os.environ.get('CM_VH', '844')), float(os.environ.get('CM_DPR', '2'))
CM = os.path.dirname(os.path.abspath(__file__)); OUT = CM + '/' + os.environ.get('CM_OUT', 'shots_app' if APP else 'shots'); os.makedirs(OUT, exist_ok=True)
SRV = CM + '/srv'; PORT = 8799; URL = f'http://localhost:{PORT}/TENGEL/'
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], cwd=SRC, check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', SRV + '/TENGEL'], cwd=SRC, check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, TARGET='app') if APP else None)
if APP:   # アプリの中（tengel://）のかわりに、localhost でアプリ版として開く
    pth = SRV + '/TENGEL/index.html'; h = open(pth, encoding='utf8').read()
    assert "window.__NATIVE = location.protocol === 'tengel:';" in h
    open(pth, 'w', encoding='utf8').write(h.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
FAKE = """
window.__NATIVE_INFO = { version: '1.0', build: '1', device: 'phone' };
window.webkit = { messageHandlers: { tengel: { postMessage: function (m) { setTimeout(function () { window.__nativeReply(m.id, true, true); }, 30); } } } };
"""
# App Store版：開催場は空（空なら、使っているマザーデータの開催場として判定）・5重勝は架空の開催場
V0 = '' if APP else '大井'
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--bind', '127.0.0.1', '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(0.8)


def rows(nos, odds, fuku=None):
    fuku = fuku or [None] * len(nos)
    return [{"no": n, "tan": str(t), "fuku": (str(f) if f else "")} for n, t, f in zip(nos, odds, fuku)]


def form(r, dist, n, baba, nos, odds, fuku, s1, s1c, s5, s10, venue=V0, date='2026-10-14', surface='ダ'):
    return {"id": None, "venue": venue, "date": date, "r": str(r), "dist": str(dist), "surface": surface, "baba": baba, "n": str(n), "tan1": "",
            "s1": str(s1), "s1combo": s1c, "s5": str(s5), "s5combo": "", "s10": str(s10), "s10combo": "", "rows": rows(nos, odds, fuku)}


# F9 は CM の「例のオッズ画面」（example_odds.html：架空）と同じ数字。複勝は画面と同じ幅表示（下の数字は前と同じなので、大穴・超大穴の並びは変わらない）
F9 = form(9, 1400, 12, '良', [6, 2, 10, 7, 1, 4, 11, 5, 9, 3, 8, 12], [2.1, 3.4, 5.2, 7.8, 9.5, 12.4, 16.8, 22.5, 31.0, 45.6, 58.3, 82.1],
          ['1.1-1.3', '1.3-1.8', '1.6-2.3', '2.0-2.9', '2.4-3.6', '2.9-4.4', '3.6-5.5', '4.5-6.9', '5.8-8.9', '7.9-12.1', '9.8-15.0', '13.5-20.6'], 18.5, '6-2-10', 42.6, 78.9)
F9.update(s5combo='6-7-2', s10combo='10-6-2')   # 例の画面の3連単5位・10位の組番（読み取りで入る）
F10 = form(10, 1600, 12, '良', [3, 8, 1, 11, 5, 2, 12, 7, 4, 9, 6, 10], [2.8, 3.6, 4.9, 6.7, 8.8, 11.5, 15.2, 19.8, 26.4, 38.0, 52.5, 70.3], None, 39.0, '', 88.0, 140.5)
F11 = form(11, 1800, 14, '稍重', [5, 12, 3, 9, 1, 14, 7, 10, 2, 13, 6, 11, 4, 8], [3.6, 4.4, 5.9, 7.2, 9.0, 11.8, 14.6, 18.9, 24.1, 30.5, 41.2, 55.0, 73.8, 99.9], None, 95.2, '', 210.4, 355.0)
# 架空のJRAのレース（東京11R・芝1600・16頭・A層）
FJ = form(11, 1600, 16, '良', [7, 3, 12, 1, 9, 15, 5, 10, 2, 14, 6, 11, 4, 16, 8, 13],
          [2.3, 4.1, 5.6, 7.9, 9.8, 12.5, 15.1, 19.7, 24.3, 31.2, 38.5, 47.0, 58.2, 72.4, 95.1, 130.6],
          [1.2, 1.5, 1.8, 2.3, 2.7, 3.2, 3.9, 4.6, 5.5, 6.8, 8.1, 9.9, 12.2, 14.8, 18.5, 24.0], 19.6, '7-3-12', 48.2, 96.5, venue='' if APP else '東京', date='2026-10-17', surface='芝')
BLANK = {"id": None, "venue": V0, "date": "2026-10-14", "r": "", "dist": "", "surface": "ダ", "baba": "", "n": "", "tan1": "", "s1": "", "s1combo": "", "s5": "", "s5combo": "", "s10": "", "s10combo": "", "rows": []}


def w5odds(n, tan1):
    xs = [tan1] + [round(tan1 + 1.9 * i + 0.35 * i * i, 1) for i in range(1, n)]
    return [{"no": (i * 5) % n + 1, "tan": str(x), "fuku": ""} for i, x in enumerate(xs)]


V1, V2 = ('ひがし', 'にし') if APP else ('東京', '京都')
RACES = [(V1, 9, 1600, 12, '良', 1.8, 12.0), (V2, 10, 1800, 14, '良', 2.0, 30.0), (V1, 10, 1400, 12, '稍重', 3.0, 70.0), (V2, 11, 2000, 16, '良', 3.2, 80.0), (V1, 11, 1600, 12, '良', 1.5, 9.0)]
W5 = {"id": None, "fixed": False, "date": "2026-10-18", "budget": "3000", "mode": "pick", "randAll": False, "stake": "", "payout": "", "other": "", "note": "",
      "races": [{"form": {"venue": v, "date": "2026-10-18", "r": str(r), "dist": str(d), "surface": "芝", "baba": b, "n": str(n), "rows": w5odds(n, t1), "tan1": "", "s1": str(s1), "s1combo": "", "s5": "", "s5combo": "", "s10": "", "s10combo": ""},
                 "sel": None, "win": "", "picks": None, "man": None} for v, r, d, n, b, t1, s1 in RACES]}


# 架空のJRAデータ（検証データと同じA〜P列・タブ区切り）：4/4〜10/11の土日、180走
def jra_tsv(nrace=180, seed=7):
    rnd = random.Random(seed)
    import datetime as dt
    days, d = [], dt.date(2026, 4, 4)
    while d <= dt.date(2026, 10, 11):
        if d.weekday() in (5, 6):
            days.append(d)
        d += dt.timedelta(days=1)
    per = [nrace // len(days)] * len(days)
    for i in rnd.sample(range(len(days)), nrace - sum(per)):
        per[i] += 1
    W = [32, 19, 13, 9, 7, 5, 4, 3, 2.5, 2, 1.5, 1.2, 1, .8, .6, .5, .4, .3]
    out = []
    for day, k in zip(days, per):
        for r in sorted(rnd.sample(range(1, 13), k)):
            n = rnd.randint(10, 18)
            baba = rnd.choices(['良', '稍重', '重', '不良'], [75, 15, 7, 3])[0]
            dist = rnd.choice([1200, 1400, 1600, 1800, 2000, 2400])
            tan1 = round(rnd.uniform(1.4, 4.6), 1)
            s1 = round(tan1 * rnd.lognormvariate(2.2, 0.45), 1)
            ps = []
            while len(ps) < 3:
                p = rnd.choices(range(1, n + 1), W[:n])[0]
                if p not in ps:
                    ps.append(p)
            s5 = round(s1 * rnd.uniform(1.8, 2.6), 1); s10 = round(s5 * rnd.uniform(1.4, 1.9), 1)
            uma = int(round((180 + 95 * ps[0] * ps[1] * rnd.uniform(0.6, 1.6)) / 10) * 10)
            san = int(round((900 + 260 * ps[0] * ps[1] * ps[2] * rnd.uniform(0.6, 1.6)) / 10) * 10)
            out.append('\t'.join(map(str, [day.strftime('%Y/%m/%d'), r, baba, dist, n, tan1, s1, ps[0], ps[1], ps[2], s5, s10, uma, san, '', 1])))
    return '\n'.join(out)


# ---- CM第7弾：ポイントのイメージ（このブラウザの中で画面に足すだけ・アプリのソースは変えない） ----
BETS7 = ['単勝', '複勝', '枠複', '枠単', '馬連', '馬単', 'ワイド', '3連複', '3連単']
LOCK_SVG = '<svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>'
LOCK_CSS = """.cmlk{color:#8d94a6!important;background:#eceef3!important;border:1px dashed #b8bfcc!important;display:inline-flex!important;align-items:center;gap:4px}
.cmlk .cmp{font-size:11.5px;font-weight:800;color:#b7791f;letter-spacing:.02em;margin-left:1px}"""
REC_LOCK_JS = """([svg, css, open]) => {
  let s = document.getElementById('cmlkcss'); if (!s) { s = document.createElement('style'); s.id = 'cmlkcss'; s.textContent = css; document.head.appendChild(s); }
  const box = document.querySelector('#recCard [data-k=types]'); if (!box) return 'no types';
  if (!box.querySelector('[data-v="枠複"]')) { const f = box.querySelector('[data-v="複勝"]'); for (const t of ['枠単', '枠複']) { const b = document.createElement('button'); b.type = 'button'; b.dataset.v = t; b.textContent = t; f.after(b); } }
  const LOCKABLE = ['複勝', '枠複', '枠単', '馬連', 'ワイド', '3連複'];
  for (const b of box.querySelectorAll('button')) {
    const t = b.dataset.v; b.setAttribute('aria-pressed', 'false');
    if (LOCKABLE.includes(t) && !open.includes(t)) { b.classList.add('cmlk'); b.innerHTML = svg + t + '<span class="cmp">500P</span>'; }
    else { b.classList.remove('cmlk'); b.textContent = t; }
  }
  return [...box.querySelectorAll('button')].map(b => b.dataset.v + (b.classList.contains('cmlk') ? '🔒' : '')).join(' ');
}"""
SLOT_CSS = """#slotList .slotrow.cmlks{position:relative;overflow:hidden}
.cmlkc{position:absolute;inset:0;background:rgba(236,238,243,.96);display:flex;align-items:center;justify-content:center;gap:8px;font-weight:800;color:#5a6175;font-size:14px;border-radius:10px;border:1.5px dashed #b8bfcc}
.cmlkc b{color:#b7791f;font-size:15px}"""
SLOT_JS = """([svg, css, ns]) => {
  let s = document.getElementById('cmlkcss2'); if (!s) { s = document.createElement('style'); s.id = 'cmlkcss2'; s.textContent = css; document.head.appendChild(s); }
  for (const r of document.querySelectorAll('#slotList .slotrow')) {
    const c = r.querySelector('.cmlkc'); if (c) c.remove(); r.classList.remove('cmlks');
    if (ns.includes(+r.dataset.n)) { r.classList.add('cmlks'); const d = document.createElement('div'); d.className = 'cmlkc'; d.innerHTML = svg + '<span>新しいマザーデータ　<b>15,000P</b>で作れる</span>'; r.appendChild(d); }
  }
  return document.querySelectorAll('#slotList .cmlkc').length;
}"""


def slot_lock(pg, ns):
    if not CM7:
        return 0
    return pg.evaluate(SLOT_JS, [LOCK_SVG.replace('width="13" height="13"', 'width="17" height="17"'), SLOT_CSS, ns])


def w5state(pg, k, mode):   # 単勝5連予想：k レースだけ入れた状態（のこりは空）
    w = json.loads(json.dumps(W5)); w['mode'] = mode
    for i in range(k, 5):
        w['races'][i] = {"form": None, "sel": None, "win": "", "picks": None, "man": None}
    pg.evaluate("(w) => localStorage.setItem('tengel.win5', w)", json.dumps(w, ensure_ascii=False))
    pg.reload(); pg.wait_for_timeout(2400)
    hide(pg, False); pg.click('.tabbar button[data-tab=win5]'); pg.wait_for_timeout(900)


# ポイントのカード（イメージ）：保有ポイント・ポイントを買う（通常）・サブスク・繰り越し（まさちゃんの指定の金額）
PTS_CSS = """#cmPts{margin-bottom:var(--gap,14px)}
#cmPts .cmp-bal{display:flex;align-items:center;justify-content:space-between;background:var(--night,#16203D);color:#F3F0E6;border-radius:10px;padding:12px 14px;margin-bottom:14px}
#cmPts .cmp-bal span{font-size:13px;font-weight:700;letter-spacing:.06em;opacity:.85}
#cmPts .cmp-bal b{font-family:var(--font-display);font-weight:400;font-size:26px;color:var(--lamp,#E2A23B);letter-spacing:.02em}
#cmPts .cmp-bal b small{font-size:15px;margin-left:3px}
#cmPts .cmp-h{display:flex;align-items:center;gap:8px;font-weight:800;font-size:14.5px;margin:4px 0 8px}
#cmPts .cmp-h .tag{font-size:11.5px;font-weight:800;color:#fff;background:#d6261d;border-radius:999px;padding:2px 9px}
#cmPts .cmp-list{display:grid;gap:8px;margin-bottom:14px}
#cmPts .cmp-row{display:flex;align-items:center;gap:8px;border:1px solid var(--line);border-radius:10px;padding:9px 10px 9px 12px;background:var(--surface-2)}
#cmPts .cmp-row .pt{font-family:var(--font-mono);font-weight:600;font-size:17px}
#cmPts .cmp-row .pv{display:flex;flex-direction:column;align-items:flex-start;gap:3px}
#cmPts .cmp-row .bn{font-size:11.5px;font-weight:800;color:#b7791f;background:#fff4dc;border:1px solid #f1d39a;border-radius:999px;padding:1px 8px;white-space:nowrap}
#cmPts .cmp-row .btn.yen{margin-left:auto;min-width:112px;padding:5px 10px;flex-direction:column;gap:0;line-height:1.25}
#cmPts .cmp-row .btn.yen b{font-size:14.5px}
#cmPts .cmp-row .btn.yen small{font-size:10.5px;font-weight:700;opacity:.8}
#cmPts .cmp-sub .cmp-row{background:#fffaf0;border-color:#f1d39a}
#cmPts .cmp-note{margin:0;font-size:12.5px;color:var(--muted);line-height:1.6}"""
PTS_HTML = """<div class="card" id="cmPts"><h2>ポイント</h2>
  <div class="cmp-bal"><span>保有ポイント</span><b>100<small>P</small></b></div>
  <div class="cmp-h">ポイントを買う</div>
  <div class="cmp-list cmp-buy">
    <div class="cmp-row"><span class="pv"><span class="pt">500P</span></span><span class="btn yen"><b>176円</b><small>税抜160円</small></span></div>
    <div class="cmp-row"><span class="pv"><span class="pt">1,000P</span></span><span class="btn yen"><b>352円</b><small>税抜320円</small></span></div>
    <div class="cmp-row"><span class="pv"><span class="pt">2,000P</span></span><span class="btn yen"><b>704円</b><small>税抜640円</small></span></div>
    <div class="cmp-row"><span class="pv"><span class="pt">4,000P</span></span><span class="btn yen"><b>1,408円</b><small>税抜1,280円</small></span></div>
  </div>
  <div class="cmp-h">サブスク（月額）<span class="tag">おトク</span></div>
  <div class="cmp-list cmp-sub">
    <div class="cmp-row"><span class="pv"><span class="pt">2,000P</span></span><span class="btn primary yen"><b>638円/月</b><small>税抜580円</small></span></div>
    <div class="cmp-row"><span class="pv"><span class="pt">4,400P</span><span class="bn">うちボーナス400P</span></span><span class="btn primary yen"><b>1,276円/月</b><small>税抜1,160円</small></span></div>
    <div class="cmp-row"><span class="pv"><span class="pt">9,200P</span><span class="bn">うちボーナス1,000P</span></span><span class="btn primary yen"><b>1,914円/月</b><small>税抜1,740円</small></span></div>
  </div>
  <p class="cmp-note">サブスクなら、ポイントを<b>購入日から30日間</b>繰り越せる。<br>価格は税込（下の小さい数字は税抜）。</p>
</div>"""
PTS_JS = """([html, css]) => {
  let s = document.getElementById('cmptscss'); if (!s) { s = document.createElement('style'); s.id = 'cmptscss'; s.textContent = css; document.head.appendChild(s); }
  const v = document.getElementById('v-set'); const old = document.getElementById('cmPts'); if (old) old.remove();
  v.insertAdjacentHTML('afterbegin', html); return document.getElementById('cmPts').getBoundingClientRect().height;
}"""


HIDE = ".tabbar,.minibar,#toast{display:none!important}.top{display:none!important}main{padding-bottom:0!important}.zsave.sticky{position:static!important;box-shadow:none!important}"
META = {}
BOX_JS = """([root, sels]) => { const re = document.querySelector(root); const R = re.getBoundingClientRect(); const out = {};
 for (const s of sels) { const el = document.querySelector(s); if (!el) { out[s] = null; continue; } const b = el.getBoundingClientRect();
   out[s] = { x: +(b.left - R.left).toFixed(1), y: +(b.top - R.top).toFixed(1), w: +b.width.toFixed(1), h: +b.height.toFixed(1) }; }
 return { W: +R.width.toFixed(1), H: +R.height.toFixed(1), b: out }; }"""


# CMでは「大井」「第13改訂版」などの文字を出さない（画面の文字だけ置きかえる。アプリの中身は変えない）
SCRUB_JS = r"""() => {
  const R = [[/大井 第13改訂版・カスタム|第13改訂版・カスタム/g, 'カスタム'], [/大井 第13改訂版/g, ''], [/第13改訂版の初期/g, '初期設定'], [/（第13改訂版）/g, ''], [/第13改訂版/g, ''],
    [/基盤データ（大井）/g, '基盤データ'], [/アプリに入っていた大井データ/g, 'アプリに入っていたデータ'], [/アプリに入っている大井データ/g, 'アプリに入っているデータ'],
    [/大井の姫フィルター（Excel）/g, 'Excel'], [/大井の検証データ/g, '検証データ'], [/大井競馬/g, '基本データ'], [/大井 /g, ''], [/大井/g, ''], [/改訂版/g, '']];
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT), nodes = [];
  while (w.nextNode()) nodes.push(w.currentNode);
  for (const n of nodes) { let t = n.nodeValue; if (!/大井|改訂版/.test(t)) continue; for (const [re, to] of R) t = t.replace(re, to); n.nodeValue = t; }
  for (const el of document.querySelectorAll('input, textarea')) {
    if (/大井/.test(el.value)) el.value = el.value.replace(/大井競馬/g, '基本データ').replace(/大井/g, '');
    if (/大井/.test(el.placeholder || '')) el.placeholder = '';
  }
  const v = document.querySelector('.brand .ver'); if (v) v.style.display = v.textContent.trim() ? '' : 'none';
  const left = [...document.querySelectorAll('body *')].filter(e => e.children.length === 0 && /大井|改訂版/.test(e.textContent)).length;
  return left;
}"""


RENAME_JS = r"""() => { const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let n = 0;
  while (w.nextNode()) { const t = w.currentNode; if (/5重勝/.test(t.nodeValue)) { t.nodeValue = t.nodeValue.replace(/5重勝/g, '単勝5連予想'); n++; } } return n; }"""


def scrub(pg):
    if CM7:
        pg.evaluate(RENAME_JS)
    left = pg.evaluate(SCRUB_JS)
    if left:
        print('  ⚠️ まだ残っている文字', left)


def hide(pg, on):
    pg.evaluate("([css, on]) => { let s = document.getElementById('cmcss'); if (on && !s) { s = document.createElement('style'); s.id = 'cmcss'; s.textContent = css; document.head.appendChild(s); } if (!on && s) s.remove(); }", [HIDE, on])


def content(pg, name, sels=()):
    hide(pg, True); pg.evaluate("scrollTo(0,0)"); pg.wait_for_timeout(300)
    scrub(pg); pg.wait_for_timeout(100)
    META[name] = pg.evaluate(BOX_JS, ['main', list(sels)])
    pg.locator('main').screenshot(path=f'{OUT}/{name}.png', animations='disabled')
    hide(pg, False); pg.wait_for_timeout(150)
    miss = [k for k, v in META[name]['b'].items() if v is None]
    print('  📸', name, META[name]['W'], 'x', META[name]['H'], ('（見つからない：' + ', '.join(miss) + '）') if miss else '')


def bar_shot(pg, sel, name):
    if IPAD and sel == '.tabbar':
        return
    hide(pg, False); pg.evaluate("scrollTo(0,0)"); pg.wait_for_timeout(250)
    scrub(pg); pg.wait_for_timeout(100)
    pg.locator(sel).screenshot(path=f'{OUT}/{name}.png', animations='disabled')
    key = 'header' if sel == 'header.top' else 'tabbar'
    META[key] = pg.evaluate("(s) => { const b = document.querySelector(s).getBoundingClientRect(); return { W: b.width, H: b.height }; }", sel)


def tab(pg, name):
    hide(pg, False); pg.click(f'{".tabs-top" if IPAD else ".tabbar"} button[data-tab={name}]'); pg.wait_for_timeout(900)


def load_form(pg, f):
    pg.evaluate("(f) => localStorage.setItem('tengel.form', f)", json.dumps(f, ensure_ascii=False))
    pg.reload(); pg.wait_for_timeout(2400)


def record(pg, buy, res, stake, pay):
    card = pg.locator('#recCard')
    card.locator('[data-k=stake][data-t="馬単"]').fill(stake)
    card.locator('[data-k=buyz] button').nth(buy).click(); pg.wait_for_timeout(200)
    card.locator('[data-k=mode] button[data-v=nin]').click(); pg.wait_for_timeout(200)
    r = card.locator('[data-k=res]'); r.fill(''); r.press_sequentially(res, delay=20); pg.wait_for_timeout(300)
    card.locator('[data-k=payout][data-t="馬単"]').fill(pay); pg.wait_for_timeout(300); r.click()
    card.locator('[data-act=save]').click(); pg.wait_for_timeout(1200)


Z1 = '#zoneCard ol.zedit > li:nth-child(1)'
ZSEL = ['#zoneCard', '#zoneCard .zk-tabs', '#zoneCard .zk-head', '#zoneCard .zk-head .chip', Z1, Z1 + ' .zr-top', Z1 + ' .zr-label',
        Z1 + ' .zpick[data-f="a"]', Z1 + ' .zpick[data-f="b"]', Z1 + ' .zpick[data-f="t"]',
        Z1 + ' .zpick[data-f="b"] button[data-z="大穴"]', Z1 + ' .zpick[data-f="t"] button[data-z="大穴"]', Z1 + ' .zr-stat',
        '#zoneCard ol.zedit > li:nth-child(2)', '#zoneCard .zsave', '#zmsg']
RSEL = ['#result', '#result .vhead', '#result .lbadge', '#result .vhead .chips', '#result .vhead .chip.cus', '#result ol.zones > li:nth-child(1)',
        '#result ol.zones > li:nth-child(1) .zflow', '#result ol.zones > li:nth-child(1) .znums', '#result ol.zones > li:nth-child(1) .zref',
        '#result ol.zones > li:nth-child(1) .zthird', '#result ol.zones > li:nth-child(2)', '#result .numbers']
S2 = '#slotList .slotrow[data-n="2"]'
MSEL = ['#setMother', '#slotList', '#slotList .slotrow[data-n="1"]', S2, '#slotList .slotrow[data-n="3"]', '#slotEdit', '#smPreview', '#smApply', '#smUse', S2 + ' .sr-sub', S2 + ' [data-sact=edit]']

# 架空のJRAデータをExcel（検証データシート・A〜P列）にする
import openpyxl
XLSX = CM + ('/マイデータ.xlsx' if APP else '/JRA_マザーデータ.xlsx')
wb = openpyxl.Workbook(); ws = wb.active; ws.title = '検証データ'
ws.append(['日付', 'R', '馬場', '距離', '頭数', '単勝1位', '3連単1位', '1着人気', '2着人気', '3着人気', '3連単5位', '3連単10位', '馬単払戻', '3連単払戻', '備考', '集計対象'])
for line in jra_tsv().split('\n'):
    c = line.split('\t')
    ws.append([c[0], int(c[1]), c[2], int(c[3]), int(c[4]), float(c[5]), float(c[6]), int(c[7]), int(c[8]), int(c[9]), float(c[10]), float(c[11]), int(c[12]), int(c[13]), c[14], int(c[15])])
wb.save(XLSX)

errs = []
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': VW, 'height': VH}, device_scale_factor=DPR, color_scheme='light', locale='ja-JP', timezone_id='Asia/Tokyo')
        if APP:
            ctx.add_init_script(FAKE)
            ctx.route('**/__native/autobackup.json', lambda route: route.fulfill(status=404, body='not found'))
        pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.add_init_script("if (!sessionStorage.getItem('x')) { sessionStorage.setItem('x', '1'); localStorage.setItem('tengel.form', %s); localStorage.setItem('tengel.win5', %s); }"
                           % (json.dumps(json.dumps(BLANK, ensure_ascii=False)), json.dumps(json.dumps(W5, ensure_ascii=False))))
        pg.goto(URL); pg.wait_for_timeout(2600)
        # ---- 判定：空 → 読み取り中 → 読み取ったあと ----
        content(pg, 'judge_empty', ['#ocrBtn', '#ocrRow', '.input-col > .card:nth-child(1)', '#result'])
        # 読み取り中・読み取ったあとの文は、アプリと同じ（src.html の ocrFile・applyOCR）。App Store版は端末の中で読む（10秒くらい）
        # 例のオッズ画面には開催場が無いので「開催場」は読み取った物に入らない（複勝は入る）
        pg.evaluate("""([n, t]) => { document.getElementById('ocrMsg').innerHTML = '<div class="banner info"><span class="spin" aria-hidden="true"></span> ' + n + '枚の画像を読み取り中…' + t + '</div>'; }""", [3 if CM7 else 2, '（この中で読むよ・10秒くらい）' if APP else '（20〜60秒くらい）'])   # 第7弾は3枚（出馬表・単勝・3連単）
        pg.wait_for_timeout(300)
        content(pg, 'judge_reading', ['#ocrMsg', '#ocrBtn'])
        load_form(pg, F9)
        pg.evaluate("""document.getElementById('ocrMsg').innerHTML = '<div class="banner info">読み取った：R・距離・頭数・馬場・単勝12頭・3連単1位・3連単5位・3連単10位<br><span class="small">読み間違いがないか、オッズと頭数だけは画面と見比べてね。</span></div>'""")
        pg.wait_for_timeout(300)
        content(pg, 'judge_filled', ['#ocrMsg', '.input-col > .card:nth-child(1) .fields'] + RSEL
                + ['.input-col > .card:nth-child(1)', '.input-col > .card:nth-child(2)', '.input-col > .card:nth-child(3)', '.input-col > .card:nth-child(2) .oheads', '#oddsGrid', '#fS1', '#fS5', '#fS10',
                   '.f:has(> #fDist)', '.f:has(> #fBaba)', '.f:has(> #fN)'])   # CM第5弾：入れる3つ（レース情報・単勝・3連単）。第6弾：距離と馬場の欄も。第7弾：頭数も
        bar_shot(pg, 'header.top', 'header_oi0'); bar_shot(pg, '.tabbar', 'tabbar_judge')
        if CM7:   # 記録できる券種：はじめは単勝・馬単・3連単。ほかは500Pで解放（イメージ）
            for k, opened in (('rec_lk0', []), ('rec_lk1', ['複勝']), ('rec_lk2', ['複勝', '馬連'])):
                print('   券種のロック', pg.evaluate(REC_LOCK_JS, [LOCK_SVG, LOCK_CSS, opened]))
                content(pg, k, ['#recCard', '#recCard [data-k=types]'] + [f'#recCard [data-k=types] button[data-v="{t}"]' for t in BETS7])
            load_form(pg, F9)
        if PREV:   # プレビュー動画用：買う馬を選ぶ前と、2つ目のゾーンの2着の4番を押したあと（画面全体）
            PSEL = ['#result ol.zones > li:nth-child(2)', '#result ol.zones > li:nth-child(2) .znums', '#result ol.zones > li:nth-child(2) button.hp[data-hs="b"][data-no="4"]']
            content(pg, 'judge_pick0', PSEL)
            pg.locator('#result button.hp[data-hz="人気→中穴"][data-hs="b"][data-no="4"]').click(); pg.wait_for_timeout(400)
            content(pg, 'judge_pick1', PSEL)
            load_form(pg, F9)
        # ---- 買う馬（大きく） ----
        ctx3 = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=3, color_scheme='light', locale='ja-JP', timezone_id='Asia/Tokyo')
        if APP:
            ctx3.add_init_script(FAKE)
            ctx3.route('**/__native/autobackup.json', lambda route: route.fulfill(status=404, body='not found'))
        p3 = ctx3.new_page()
        p3.add_init_script("localStorage.setItem('tengel.form', %s);" % json.dumps(json.dumps(F9, ensure_ascii=False)))
        p3.goto(URL); p3.wait_for_timeout(2600)
        z = p3.locator('#result ol.zones > li:nth-child(2)')
        z.scroll_into_view_if_needed(); p3.wait_for_timeout(300); scrub(p3)
        META['pick'] = p3.evaluate(BOX_JS, ['#result ol.zones > li:nth-child(2)', ['#result ol.zones > li:nth-child(2) button.hp[data-hs="b"][data-no="4"]',
                                                                                     '#result ol.zones > li:nth-child(2) .znums']])
        z.screenshot(path=f'{OUT}/pick_before.png', animations='disabled')
        p3.locator('#result button.hp[data-hz="人気→中穴"][data-hs="b"][data-no="4"]').click(); p3.wait_for_timeout(400); scrub(p3)
        z.screenshot(path=f'{OUT}/pick_after.png', animations='disabled')
        ctx3.close()
        # ---- 記録を3つ ----
        record(pg, 1, '2.5.1', '600', '1860')
        load_form(pg, F10); record(pg, 0, '1.2.3', '400', '0')
        load_form(pg, F11); record(pg, 0, '2.4.1', '600', '0')
        if PREV:   # App Storeのスクショ用：C層・第2段階の判定（推奨ゾーン3本・大穴と超大穴の番号）
            content(pg, 'judge_c', RSEL + ['#result ol.zones > li:nth-child(3)'])
        # ---- WIN5・記録・収支 ----
        tab(pg, 'win5')
        content(pg, 'win5', ['.w5top', '#w5Sum', '#w5Races .w5race[data-i="0"]', '#w5Races .w5race[data-i="0"] .w5zones', '#w5Races .w5race[data-i="0"] .w5picks'])
        bar_shot(pg, '.tabbar', 'tabbar_win5')
        if IPAD: bar_shot(pg, 'header.top', 'header_w5')
        tab(pg, 'rec')
        content(pg, 'records', ['#ymRec', '#rFilters', '#recSummary', '#recList .dgroup', '#recList .lrow:nth-child(1)', '#recList .lrow:nth-child(1) .stc'])
        bar_shot(pg, '.tabbar', 'tabbar_rec'); bar_shot(pg, 'header.top', 'header_oi3')
        tab(pg, 'stats')
        content(pg, 'stats', ['#moneyBody', '#moneyBody .money-tiles', '#statsBody'])
        bar_shot(pg, '.tabbar', 'tabbar_stats')
        if IPAD: bar_shot(pg, 'header.top', 'header_st')
        # ---- 買い目編集：A層の第1に「2着 大穴」「3着 大穴」を足す ----
        tab(pg, 'set')
        bar_shot(pg, '.tabbar', 'tabbar_set')
        if IPAD: bar_shot(pg, 'header.top', 'header_set0')
        content(pg, 'set_z0', ZSEL + MSEL)
        pg.locator(Z1 + ' .zpick[data-f="b"] button[data-z="大穴"]').click(); pg.wait_for_timeout(400)
        content(pg, 'set_z1', ZSEL)
        pg.locator(Z1 + ' .zpick[data-f="t"] button[data-z="大穴"]').click(); pg.wait_for_timeout(400)
        content(pg, 'set_z2', ZSEL)
        pg.locator('#zoneCard [data-zact=save]').click(); pg.wait_for_timeout(900)
        content(pg, 'set_z3', ZSEL)
        bar_shot(pg, 'header.top', 'header_oi3c')
        # ---- カスタム買い目で判定（大井のデータ） ----
        load_form(pg, F9)
        tab(pg, 'judge')
        content(pg, 'judge_custom', RSEL)
        if IPAD: bar_shot(pg, 'header.top', 'header_jc')
        # ---- マザーデータ：2つ目「JRA」に架空のデータを入れて使う ----
        tab(pg, 'set')
        content(pg, 'set_m0', MSEL)
        if CM7:   # 新しいマザーデータは15,000Pで解放（イメージ）：2と3にロック → 2を解放
            print('   マザーデータのロック', slot_lock(pg, [2, 3])); content(pg, 'set_m0_lk23', MSEL)
            print('   マザーデータのロック', slot_lock(pg, [3])); content(pg, 'set_m0_lk3', MSEL)
        pg.locator(S2 + ' [data-sact=edit]').click(); pg.wait_for_timeout(500)
        pg.locator('#smFile').set_input_files(XLSX); pg.wait_for_timeout(1500)
        slot_lock(pg, [3]); content(pg, 'set_m1', MSEL)
        pg.locator('#smApply').click(); pg.wait_for_timeout(1500)
        slot_lock(pg, [3]); content(pg, 'set_m2', MSEL)
        pg.locator('#smUse').click(); pg.wait_for_timeout(1200)
        slot_lock(pg, [3]); content(pg, 'set_m3', MSEL)
        bar_shot(pg, 'header.top', 'header_jra')
        # ---- JRAのデータで判定（東京11R） ----
        load_form(pg, FJ)
        tab(pg, 'judge')
        content(pg, 'judge_jra', RSEL)
        if IPAD: bar_shot(pg, 'header.top', 'header_jj')
        if CM7:
            # ---- 単勝5連予想：5レースを1つずつ入れる（0〜5）→ 自分で選ぶ／ランダム ----
            W5SEL = ['.w5top', '#w5Mode', '#w5Mode button[data-v="pick"]', '#w5Mode button[data-v="rand"]', '#w5Sum', '#w5RandRow', '#w5Races'] + \
                    [f'#w5Races > .card:nth-child({i})' for i in range(1, 6)] + ['#w5Races .w5race[data-i="0"] .w5zones', '#w5Races .w5race[data-i="0"] .w5picks', '#w5Date', '#w5Budget']
            for k in range(6):
                w5state(pg, k, 'pick'); content(pg, f'w5_{k}', W5SEL)
            w5state(pg, 5, 'rand'); content(pg, 'w5_rand', W5SEL)
            bar_shot(pg, '.tabbar', 'tabbar_win5')
            # ---- ポイント（イメージ）：設定タブのいちばん上に「ポイント」のカード ----
            tab(pg, 'set')
            print('   ポイントのカード', pg.evaluate(PTS_JS, [PTS_HTML, PTS_CSS]))
            content(pg, 'set_points', ['#cmPts', '#cmPts .cmp-bal', '#cmPts .cmp-buy', '#cmPts .cmp-sub', '#cmPts .cmp-note'] +
                    [f'#cmPts .cmp-buy .cmp-row:nth-child({i})' for i in range(1, 5)] + [f'#cmPts .cmp-sub .cmp-row:nth-child({i})' for i in range(1, 4)])
            bar_shot(pg, '.tabbar', 'tabbar_set')
        b.close()
finally:
    srv.terminate(); srv.wait()
json.dump(META, open(OUT + '/meta.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('errors', errs[:3])
