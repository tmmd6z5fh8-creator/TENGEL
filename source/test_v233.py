# 第4.233版の テスト（まさちゃん 11/27）
#   20:10「買い目選択の方法変更 一枚目、ニ枚目の所で買い目選択を無くして！ あくまで推奨買い目の提示だけ 買い目を予約の所で、3枚目の画像の様に、ゾーンごとに分けて(層に合わせて配置する)
#          1着、2着とか券種によって分かる … 券種ごとに打ち込む様にする 例えば 馬単① 1着、2着で選べる 3連単① 1着、2着、3着で選べる」
#          （答え：行は 自分で 足していく・足した 行は 推奨ゾーンの 馬が 全部 選ばれた 形・着ごとに 全部の ゾーンを 出して 推奨を 目立たせる・推奨は 設定の「買い目編集」に 合わせる）
#   20:20「あと、一枚目を送ってるのに二枚目になる理由を見つけて改善して！」（名古屋 11R の 画面が 9R に なった：上の レースの 切りかえ「9R 10R 11R 12R」の 9R を 読んで いた）
#   App Store版（TARGET=app）を localhost で アプリ版として 開く（test_native.py の FAKE）。レースは test_native.py と 同じ 8R（B層：第1 中穴→人気・第2 人気→大穴・3着 人気・大穴）
#   ① 判定の ゾーン：押せる 番号・お任せ・「選んだ馬で ○%」が ない（番号は 出す）
#   ② 買い目の カード：「＋券種」9つ（🔒6つ）・はじめは 行なし（予約は 押せない）
#   ③ ＋馬単 → 馬単①（第1 中穴→人気）：1着・2着の 段・推奨の 段（中穴・人気）は 色つきで ぜんぶ 選ばれて いる・ほかの 段は 選ばれて いない・9点・「選んだ馬で 馬単 ○%」
#   ④ ＋馬単 → 馬単②（第2 人気→大穴）・＋3連単 → 3連単①（第1：3着 人気・大穴）45点
#   ⑤ 番号を 外す・推奨の 外の 馬を 入れる（✏️）・ゾーンの 名前で まとめて・推奨を 押すと もどる・行を 消す・開き直しても 下書きが のこる
#   ⑥ 予約 → rsv.lines・rsv.legs（券種つき）・券種ごとに 組を あわせる・推奨の 外の 馬が あれば rsv.zones に「自己入力」→ 結果待ちの 一覧に 行ごとの 馬
#   ⑦ 選び直す → 予約の 行が もどる・お任せ（行ごとに 1点 以上）
#   ⑧ 前の 版の 予約（券種 × ゾーン・hp・自己入力）を 選び直す → 行に 直る
#   ⑨ 画像の 読み取り：上に「名古屋 9R 10R 11R 12R」・見出しに「11R」→ 11R・名古屋
#   python3 test_v233.py
import json, os, re, shutil, subprocess, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv_v233'); PORT = 8859; APP = f'http://localhost:{PORT}/APP/'
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL,
               env=dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, HIST='hist_280.json', DROP='', TARGET='app'))
pth = os.path.join(SRV, 'APP', 'index.html'); html = open(pth, encoding='utf8').read()
assert "window.__NATIVE = location.protocol === 'tengel:';" in html
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
NT = open(os.path.join(W, 'test_native.py'), encoding='utf8').read()
FAKE = re.search(r'\nFAKE = """(.*?)"""', NT, re.S).group(1)      # アプリの 窓口の にせもの（画像の 読み取りは window.__ocrLines）
FORM = {"venue": "大井", "date": "2026-10-10", "r": "8", "dist": "1400", "surface": "ダ", "baba": "稍重", "n": "14", "s1": "41.3", "s1combo": "6-2-10", "s5": "58.2", "s10": "84.0", "rname": "はなまる特別", "start": "15:40",
        "rows": [{"no": no, "tan": str(t), "fuku": f} for no, t, f in [(1, 12.4, '3.0-4.6'), (2, 4.1, '1.6-2.2'), (3, 31.5, '6.1-9.8'), (4, 9.8, '2.6-3.9'), (5, 18.2, '4.0-6.2'), (6, 2.4, '1.1-1.3'), (7, 7.6, '2.1-3.1'), (8, 54.0, '9.4-15.0'), (9, 25.9, '5.2-8.1'), (10, 6.3, '1.9-2.7'), (11, 14.7, '3.3-5.1'), (12, 88.6, '13.2-21.1'), (13, 40.2, '7.7-12.2'), (14, 120.5, '18.4-29.6')]]}
DATE_AT = """(() => { const D = Date, OFF = Date.UTC(2026, 9, 1, 3, 0, 0) - D.now();
  class FD extends D { constructor(...a) { if (a.length) super(...a); else super(D.now() + OFF); } static now() { return D.now() + OFF; } }
  FD.UTC = D.UTC; FD.parse = D.parse; window.Date = FD; })();"""
SHOT = os.path.join(W, 't4'); os.makedirs(SHOT, exist_ok=True)
fails, errs = [], []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c:
        fails.append(label)


def gate(pg):
    g = pg.locator('#gate')
    for _ in range(40):
        if not g.count() or g.evaluate('e => e.hidden'):
            return
        try:
            (pg.locator('#gateGo') if pg.locator('#gateGo').count() else g).click(timeout=1500)
        except Exception:
            pass
        pg.wait_for_timeout(150)


# 買い目の カードの 中身（行・着・段）
CARD = """() => { const c = document.querySelector('#recCard'), q = s => [...c.querySelectorAll(s)];
  const lines = q('.rline').map(l => ({ i: +l.dataset.i, open: l.classList.contains('open'), t: (l.querySelector('.rlt') || {}).innerText, z: (l.querySelector('.rlz') || {}).innerText, n: (l.querySelector('.rln') || {}).innerText, sum: (l.querySelector('.rls') || {}).innerText,
    pos: [...l.querySelectorAll('.rpos')].map(p => ({ side: p.dataset.side, lab: (p.querySelector('.rph b') || {}).innerText, note: (p.querySelector('.rph span') || {}).innerText || '',
      rows: [...p.querySelectorAll('.rzr')].map(r => ({ z: r.dataset.z, rec: r.classList.contains('rec'), nos: [...r.querySelectorAll('button.num')].map(b => +b.dataset.no), on: [...r.querySelectorAll('button.num[aria-pressed=true]')].map(b => +b.dataset.no) })) })),
    tpl: [...l.querySelectorAll('[data-k=rltpl] button')].map(b => [b.innerText, b.getAttribute('aria-pressed')]), pct: (l.querySelector('.rlpct') || {}).innerText || '', warn: (l.querySelector('.rlw') || {}).innerText || '' }));
  const res = document.querySelector('#rsvBtn');
  return { add: q('[data-k=radd] button').map(b => [b.dataset.v, b.classList.contains('lock')]), lines, empty: (c.querySelector('.rempty') || {}).innerText || '', reserveOff: !!(c.querySelector('[data-rsv=reserve]') || {}).disabled,
    omk: !!c.querySelector('#omakaseBtn'), text: c.innerText, sumT: (c.querySelector('details[data-k=betsee] summary') || {}).innerText || '' }; }"""
JUDGE = """() => { const r = document.querySelector('#result'); return { hp: r.querySelectorAll('button.hp, button.num').length, omk: !!r.querySelector('#omakaseBtn, .omakase'), pct: [...r.querySelectorAll('.zref')].map(e => e.innerText).filter(t => t.includes('選んだ馬で')).length,
  nums: r.querySelectorAll('.zones .znums .num').length, note: (r.querySelector('.hpnote') || {}).innerText || '', zones: [...r.querySelectorAll('.zones .zflow')].map(e => e.innerText.replace(/\\s+/g, '')) }; }"""
LINES = "() => { const f = JSON.parse(localStorage.getItem('tengel.form') || '{}'); return f.rl || null; }"
BET = "(r) => { const b = [...TengelLocal.mem.bets.values()].find(x => +x.r === r); return b ? { id: b.id, rsv: b.rsv, types: b.types, buyZ: b.buyZ, stake: b.stake, amt: b.amt } : null; }"
try:
    with sync_playwright() as p:
        br = p.chromium.launch()
        ctx = br.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo', has_touch=True, is_mobile=True)
        ctx.add_init_script(DATE_AT); ctx.add_init_script(FAKE)
        ctx.add_init_script("if (!sessionStorage.getItem('seeded')) { localStorage.setItem('tengel.form', %s); sessionStorage.setItem('seeded', '1'); }" % json.dumps(json.dumps(FORM, ensure_ascii=False)))
        marks = {}

        def marker(source, q):
            op, key = q.get('op'), q.get('key')
            if op == 'set': marks[key] = q.get('value', '1'); return {'ok': True}
            if op == 'del': marks.pop(key, None); return {'ok': True}
            v = marks.get(key); return {'ok': True, 'has': v is not None, 'value': v}
        ctx.expose_binding('__saveBackup', lambda s, t: None); ctx.expose_binding('__marker', marker)
        pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        pg.goto(APP); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(1200)
        try: pg.evaluate("() => { const o = document.querySelector('#lgOv [data-lg=ok]'); if (o) o.click(); }")
        except Exception: pass
        pg.wait_for_timeout(500)
        card = pg.locator('#recCard')
        # ① 判定の ゾーン
        pg.locator('#result .zones').screenshot(path=os.path.join(SHOT, 'v233_judge.png'))
        j = pg.evaluate(JUDGE)
        print('   判定:', j)
        check(j['zones'] == ['中穴→人気', '人気→大穴'] and j['hp'] == 0 and not j['omk'] and j['pct'] == 0 and j['nums'] >= 12 and '下の「買い目」' in j['note'],
              f'①判定の ゾーン（B層：第1 中穴→人気・第2 人気→大穴）は 推奨の 提示だけ：押せる 番号 0・お任せなし・「選んだ馬で ○%」なし・番号は 出る（{j["nums"]}こ）・「買う 馬は 下の「買い目」で」')
        # ② はじめの カード
        c0 = pg.evaluate(CARD)
        print('   カード:', c0['add'], c0['empty'][:50])
        check(len(c0['add']) == 9 and sum(1 for _, lk in c0['add'] if lk) == 6 and [t for t, lk in c0['add'] if not lk] == ['単勝', '馬単', '3連単'] and c0['add'][0][0] == '単勝'
              and not c0['lines'] and '＋で 券種の 行を 足してね' in c0['empty'] and '第1 中穴→人気・第2 人気→大穴' in c0['empty'] and c0['reserveOff'] and c0['omk'],
              '②買い目の カード：「＋券種」9つ（🔒6つ：単勝・馬単・3連単の ほか）・はじめは 行なし（案内）・「買い目を予約」は 押せない・お任せは カードの 中')
        card.locator('[data-k=radd] button[data-v=複勝]').click(); pg.wait_for_timeout(200)
        check(not pg.evaluate(CARD)['lines'] and 'Pカスタム' in pg.locator('#toast').inner_text(), '🔒の 券種（複勝）は 足せない（Pカスタムの 案内）')
        # ③ ＋馬単 → 馬単①
        card.locator('[data-k=radd] button[data-v=馬単]').click(); pg.wait_for_timeout(300)
        c1 = pg.evaluate(CARD); L1 = c1['lines'][0] if c1['lines'] else {}
        print('   馬単①:', {k: L1.get(k) for k in ('t', 'z', 'n', 'sum', 'pct')})
        pos = L1.get('pos') or []
        rows1 = {r['z']: r for r in (pos[0]['rows'] if pos else [])}; rows2 = {r['z']: r for r in (pos[1]['rows'] if len(pos) > 1 else [])}
        check(len(c1['lines']) == 1 and L1['t'] == '馬単①' and L1['z'].startswith('第1 中穴→人気') and L1['open'] and L1['n'] == '9点' and [x['lab'] for x in pos] == ['1着', '2着'],
              f'③＋馬単 → 馬単①（第1 中穴→人気）：開いて いる・1着／2着・9点（{L1.get("z")}・{L1.get("n")}）')
        check(list(rows1) == ['人気', '中穴', '大穴', '超大穴', '対象外'] and rows1['中穴']['rec'] and not rows1['人気']['rec'] and rows1['中穴']['nos'] == [7, 4, 1] and sorted(rows1['中穴']['on']) == [1, 4, 7]
              and not rows1['人気']['on'] and not rows1['大穴']['on'] and rows1['対象外']['nos'] == [12, 14] and rows2['人気']['rec'] and sorted(rows2['人気']['on']) == [2, 6, 10] and not rows2['中穴']['on'],
              '③着ごとに 全部の ゾーンの 段（人気・中穴・大穴・超大穴・対象外）：推奨の 段（1着 中穴・2着 人気）は 色つきで ぜんぶ 選ばれて いる・ほかは 選ばれて いない')
        check(pos and pos[0]['note'] == '推奨 中穴' and pos[1]['note'] == '推奨 人気' and L1['tpl'] == [['第1 中穴→人気', 'true'], ['第2 人気→大穴', 'false']] and L1['sum'] == '1着 1・4・7　2着 2・6・10',
              f'③着の 見出しに「推奨 中穴」・推奨を えらぶ ボタン（第1 が おされて いる）・まとめの 行「1着 1・4・7　2着 2・6・10」（{L1.get("sum")}）')
        check(L1['pct'].startswith('選んだ馬で 馬単') and '6.5%' in L1['pct'] and not c1['reserveOff'], f'③「選んだ馬で 馬単 6.5%」（推奨ゾーンを ぜんぶ ＝ 判定の 参考的中率と 同じ 数え方：{L1.get("pct")}）・予約が 押せる')
        card.screenshot(path=os.path.join(SHOT, 'v233_line1.png'))
        # ④ ＋馬単 → 馬単②（第2）・＋3連単 → 3連単①（第1）
        card.locator('[data-k=radd] button[data-v=馬単]').click(); pg.wait_for_timeout(250)
        card.locator('[data-k=radd] button[data-v="3連単"]').click(); pg.wait_for_timeout(300)
        c2 = pg.evaluate(CARD); Ls = c2['lines']
        print('   行:', [(l['t'], l['z'], l['n'], l['open']) for l in Ls])
        L3 = Ls[2] if len(Ls) > 2 else {}
        r3 = {r['z']: r for r in (L3.get('pos') or [{}, {}, {'rows': []}])[2]['rows']} if L3 else {}
        check([(l['t'], l['z'][:9], l['n']) for l in Ls] == [('馬単①', '第1 中穴→人気', '9点'), ('馬単②', '第2 人気→大穴', '9点'), ('3連単①', '第1 中穴→人気', '45点')] and [l['open'] for l in Ls] == [False, False, True],
              f'④＋馬単 → 馬単②（第2 人気→大穴・9点）・＋3連単 → 3連単①（第1・45点）。足した 行だけ 開く（{[(l["t"], l["n"]) for l in Ls]}）')
        check(L3 and [x['lab'] for x in L3['pos']] == ['1着', '2着', '3着'] and L3['pos'][2]['note'] == '推奨 人気・大穴' and r3['人気']['rec'] and r3['大穴']['rec'] and sorted(r3['人気']['on'] + r3['大穴']['on']) == [2, 5, 6, 9, 10, 11]
              and '3連単' in L3['pct'], '④3連単①：1着・2着・3着の 段・3着は 推奨 人気・大穴（色つき・ぜんぶ 選ばれて いる）・「選んだ馬で 3連単 ○%」')
        check(c2['sumT'] == '買い目を確認（馬単・3連単）', f'④「買い目を確認（馬単・3連単）」（{c2["sumT"]}）')
        card.locator('.rline[data-i="0"] [data-k=rlsum]').click(); pg.wait_for_timeout(200)
        check([l['open'] for l in pg.evaluate(CARD)['lines']] == [True, False, False], '④まとめの 行（1着 …　2着 …）を 押しても 開く（ほかは 閉じる）')
        card.locator('.rline[data-i="2"] [data-k=rlopen]').click(); pg.wait_for_timeout(200)
        # ⑤ 番号・ゾーンの 名前・推奨・消す
        L3loc = card.locator('.rline[data-i="2"]')
        L3loc.locator('.rpos[data-side=b] button.num[data-no="6"]').click(); pg.wait_for_timeout(200)
        c3 = pg.evaluate(CARD); L3b = c3['lines'][2]
        check(L3b['n'] == '30点' and '✏️' not in L3b['z'] and '2着 2・10' in L3b['sum'], f'⑤3連単① の 2着から 6番を 外す → 30点（推奨の 中 だけ ＝ ✏️ なし：{L3b["n"]}・{L3b["sum"]}）')
        L3loc.locator('.rpos[data-side=a] .rzr[data-z=大穴] [data-k=rzall]').click(); pg.wait_for_timeout(200)
        c4 = pg.evaluate(CARD); L3c = c4['lines'][2]
        check('✏️' in L3c['z'] and L3c['sum'].startswith('1着 1・4・5・7・9・11') and L3c['n'] == '54点', f'⑤1着の「大穴」を 押す → 大穴の 3頭を まとめて 入れる・推奨の 外 ＝ ✏️（{L3c["z"]}・{L3c["n"]}）')
        L3loc.locator('.rpos[data-side=a] .rzr[data-z=大穴] [data-k=rzall]').click(); pg.wait_for_timeout(200)
        check(pg.evaluate(CARD)['lines'][2]['sum'].startswith('1着 1・4・7　'), '⑤もう一度 押す → まとめて 外す')
        L3loc.locator('[data-k=rltpl] button[data-v="1"]').click(); pg.wait_for_timeout(200)
        c5 = pg.evaluate(CARD); L3d = c5['lines'][2]
        check(L3d['z'].startswith('第2 人気→大穴') and L3d['sum'] == '1着 2・6・10　2着 5・9・11　3着 2・5・6・9・10・11' and L3d['n'] == '36点', f'⑤推奨の「第2」を 押す → 第2 の 馬 ぜんぶ に そろう（{L3d["sum"]}・{L3d["n"]}）')
        L3loc.locator('[data-k=rltpl] button[data-v="0"]').click(); pg.wait_for_timeout(200)
        check(pg.evaluate(CARD)['lines'][2]['n'] == '45点', '⑤「第1」に もどす → 45点')
        # 開き直しても 下書きが のこる
        rl0 = pg.evaluate(LINES)
        pg.reload(); pg.wait_for_timeout(900); gate(pg); pg.wait_for_timeout(1000)
        c6 = pg.evaluate(CARD)
        check(rl0 and len(rl0['lines']) == 3 and [(l['t'], l['n']) for l in c6['lines']] == [('馬単①', '9点'), ('馬単②', '9点'), ('3連単①', '45点')], f'⑤アプリを 開き直しても 行が のこる（入力の 下書き rl：{len(rl0["lines"]) if rl0 else None}行）')
        # 行を 足して 消す
        card.locator('[data-k=radd] button[data-v=単勝]').click(); pg.wait_for_timeout(200)
        c7 = pg.evaluate(CARD); L4 = c7['lines'][0]
        check(L4['t'] == '単勝①' and L4['open'] and L4['n'] == '3点' and [x['lab'] for x in L4['pos']] == ['1着'] and L4['pos'][0]['note'] == '推奨 中穴' and [l['t'] for l in c7['lines']] == ['単勝①', '馬単①', '馬単②', '3連単①'],
              f'⑤＋単勝 → 単勝①（第1：1着 中穴 3頭・3点）は 券種の 順で いちばん 上に 入る（{[l["t"] for l in c7["lines"]]}）')
        card.locator('.rline[data-i="0"] [data-k=rldel]').click(); pg.wait_for_timeout(200)
        check([l['t'] for l in pg.evaluate(CARD)['lines']] == ['馬単①', '馬単②', '3連単①'], '⑤✕ で 行を 消す')
        card.locator('[data-k=radd] button[data-v=馬単]').click(); pg.wait_for_timeout(200)
        c8 = pg.evaluate(CARD); L5 = c8['lines'][2]
        check([l['t'] for l in c8['lines']] == ['馬単①', '馬単②', '馬単③', '3連単①'] and L5['open'] and L5['t'] == '馬単③' and L5['z'] == '推奨なし' and L5['n'] == '0点' and not any(r['on'] for x in L5['pos'] for r in x['rows']) and '1着を 選んでね' in L5['warn'],
              f'⑤推奨を ぜんぶ 使った あとの ＋馬単 → 馬単③（推奨なし・空・0点・「1着を 選んでね」：{L5["z"]}）')
        L5loc = card.locator('.rline[data-i="2"]')
        for side, no in (('a', 3), ('a', 9), ('b', 1), ('b', 6), ('b', 12)):
            L5loc.locator(f'.rpos[data-side={side}] button.num[data-no="{no}"]').click(); pg.wait_for_timeout(120)
        c9 = pg.evaluate(CARD)
        check(c9['lines'][2]['n'] == '6点' and c9['lines'][2]['sum'] == '1着 3・9　2着 1・6・12', f'⑤推奨なしの 行で 好きな 馬を 選ぶ（超大穴 3・大穴 9 → 中穴 1・人気 6・対象外 12）→ 6点（{c9["lines"][2]["sum"]}）')
        card.screenshot(path=os.path.join(SHOT, 'v233_lines.png'))
        # ⑥ 予約
        card.locator('[data-rsv=reserve]').click(); pg.wait_for_timeout(1200)
        b8 = pg.evaluate(BET, 8)
        rs = (b8 or {}).get('rsv') or {}
        print('   予約:', {k: rs.get(k) for k in ('types', 'zones', 'points')}, [(l['ty'], l.get('k'), l.get('pts'), l.get('own')) for l in rs.get('lines', [])])
        check(rs.get('state') == 'reserved' and rs.get('types') == ['馬単', '3連単'] and len(rs['bets']['馬単']) == 24 and len(rs['bets']['3連単']) == 45 and rs['points'] == 69 and b8['stake'] == 6900
              and b8['amt'] == {'馬単': {'stake': 2400, 'payout': None}, '3連単': {'stake': 4500, 'payout': None}},
              f'⑥予約：券種ごとに 行の 組を あわせる（馬単 9＋9＋6＝24点・3連単 45点・合計 69点・6,900円：{rs.get("points")}）')
        check([(l['ty'], l['k'], l['pts'], l['own']) for l in rs.get('lines', [])] == [('馬単', '中穴→人気', 9, False), ('馬単', '人気→大穴', 9, False), ('馬単', None, 6, True), ('3連単', '中穴→人気', 45, False)]
              and rs['zones'] == ['中穴→人気', '人気→大穴', '自己入力'] and b8['buyZ'] == rs['zones'] and 'hp' not in rs and 'self' not in rs,
              f'⑥rsv.lines（行ごと：券種・推奨の ゾーン・点数・推奨の 外）・rsv.zones に「自己入力」（推奨なしの 行が ある ＝ 収支の 層別では 自己入力の 行）（{rs.get("zones")}）')
        lg = rs.get('legs') or []
        check([(x['l'], x['ty'], x['z']) for x in lg] == [('馬単①', '馬単', '第1 中穴→人気'), ('馬単②', '馬単', '第2 人気→大穴'), ('馬単③', '馬単', '推奨なし'), ('3連単①', '3連単', '第1 中穴→人気')] and lg[2]['a'] == [3, 9] and lg[2]['b'] == [1, 6, 12],
              f'⑥rsv.legs（結果待ちの 一覧）：行の 名前・券種・推奨・馬（{[(x["l"], x["z"]) for x in lg]}）')
        rl1 = pg.evaluate(LINES)
        check('予約済み（結果待ち）' in card.inner_text() and card.locator('.rline').count() == 0 and (rl1 is None or len(rl1['lines']) == 4), f'⑥予約済みの カード（行は 出さない）・下書きは 予約から 作り直す（{None if rl1 is None else len(rl1["lines"])}行）')
        pg.locator('#rsvBtn').click(); pg.wait_for_timeout(600)
        ov = pg.locator('#rsvOv'); legs = ov.locator('.rvleg')
        lt = [legs.nth(i).inner_text().replace('\n', ' ') for i in range(legs.count())]
        print('   結果待ち:', lt)
        check(legs.count() == 4 and lt[0].startswith('馬単①　第1 中穴→人気') and '1着' in lt[0] and '2着' in lt[0] and '3着' not in lt[0] and lt[3].startswith('3連単①') and '3着' in lt[3] and '✏️' in lt[2]
              and ov.locator('.rvleg .rvl.self').count() == 1, f'⑥上の「結果待ち」の 一覧：行ごと（馬単①…）に その 券種の 着だけ・推奨の 外の 行は ✏️（{lt[0][:30]}…）')
        pg.screenshot(path=os.path.join(SHOT, 'v233_rsvov.png'), full_page=False)
        pg.locator('#rsvOv [data-rv=close]').click(); pg.wait_for_timeout(300)
        # ⑦ 選び直す → 予約の 行が もどる → お任せ
        card.locator('[data-rsv=redo]').click(); pg.wait_for_timeout(300)
        c10 = pg.evaluate(CARD)
        check([(l['t'], l['z'][:9], l['n']) for l in c10['lines']] == [('馬単①', '第1 中穴→人気', '9点'), ('馬単②', '第2 人気→大穴', '9点'), ('馬単③', '推奨なし', '6点'), ('3連単①', '第1 中穴→人気', '45点')],
              f'⑦「選び直して予約し直す」→ 予約の 行が もどる（{[(l["t"], l["n"]) for l in c10["lines"]]}）')
        card.locator('#omakaseBtn').click(); pg.wait_for_timeout(300)
        c11 = pg.evaluate(CARD)
        pts = [int(l['n'][:-1]) for l in c11['lines']]
        check(all(x >= 1 for x in pts) and c11['lines'][2]['sum'] == '1着 3・9　2着 1・6・12' and 'お任せで選んだよ' in pg.locator('#toast').inner_text(), f'⑦お任せ：推奨の ある 行は 推奨ゾーンの 中から ランダム（どの 行も 1点 以上：{pts}）・推奨なしの 行は そのまま')
        card.locator('[data-rsv=back]').click(); pg.wait_for_timeout(300)
        check('予約済み（結果待ち）' in card.inner_text(), '⑦「やめる」→ 予約済みの まま')
        # ⑧ 前の 版の 予約（券種 × ゾーン・hp・自己入力）→ 選び直す と 行に 直る
        pg.evaluate("""async () => { const b = JSON.parse(JSON.stringify([...TengelLocal.mem.bets.values()].find(x => +x.r === 8))); const rs = b.rsv;
          delete rs.lines; rs.types = ['馬単', '3連単']; rs.zones = ['中穴→人気', '人気→大穴', '自己入力']; rs.hp = { '中穴→人気': { a: [7, 4] } }; rs.self = { a: [3], b: [1, 6], t: [13] };
          rs.legs = [{ k: '中穴→人気', l: '中穴→人気', a: [7, 4], b: [6, 2, 10], t: [6, 2, 10, 11, 5, 9] }]; b.updatedAt = new Date().toISOString();
          await TengelLocal.putBets([b]); }""")
        pg.wait_for_timeout(900)
        card.locator('[data-rsv=redo]').click(); pg.wait_for_timeout(300)
        c12 = pg.evaluate(CARD)
        got = [(l['t'], l['z'][:9], l['sum']) for l in c12['lines']]
        print('   前の 版:', got)
        check(got == [('馬単①', '第1 中穴→人気', '1着 4・7　2着 2・6・10'), ('馬単②', '第2 人気→大穴', '1着 2・6・10　2着 5・9・11'), ('馬単③', '推奨なし', '1着 3　2着 1・6'),
                      ('3連単①', '第1 中穴→人気', '1着 4・7　2着 2・6・10　3着 2・5・6・9・10・11'), ('3連単②', '第2 人気→大穴', '1着 2・6・10　2着 5・9・11　3着 2・5・6・9・10・11'), ('3連単③', '推奨なし', '1着 3　2着 1・6　3着 13')],
              '⑧前の 版の 予約（券種 × 使った ゾーン・選んだ 馬・自己入力）を 選び直す → 券種ごとの 行に 直る（選んだ 馬も そのまま）')
        card.locator('[data-rsv=back]').click(); pg.wait_for_timeout(300)
        # ⑨ 画像の 読み取り：上に レースの 切りかえ（9R 10R 11R 12R）
        Wd = lambda t, x, y, w, h=0.014: {'text': t, 'x': x, 'y': y, 'w': w, 'h': h}
        L = [Wd('名古屋', 0.08, 0.145, 0.16, 0.016), Wd('9R', 0.42, 0.146, 0.05), Wd('10R', 0.55, 0.146, 0.07), Wd('11R', 0.70, 0.146, 0.07), Wd('12R', 0.84, 0.146, 0.07),
             Wd('11R', 0.07, 0.203, 0.08, 0.018), Wd('2026年10月14日(水)', 0.21, 0.200, 0.32), Wd('テンゲル特別 A1', 0.21, 0.227, 0.4, 0.016), Wd('発走予定時刻:20:15 ダート1700m 12頭', 0.21, 0.255, 0.65), Wd('間もなく締切です', 0.21, 0.281, 0.27),
             Wd('天候:晴 馬場状態: 稍重', 0.03, 0.335, 0.4), Wd('単勝オッズ', 0.11, 0.40, 0.24, 0.02), Wd('人気', 0.05, 0.44, 0.03), Wd('馬番', 0.11, 0.44, 0.03), Wd('馬名', 0.47, 0.44, 0.05), Wd('オッズ', 0.83, 0.44, 0.08)]
        for k, (no, od) in enumerate([(10, 1.3), (1, 11.0), (4, 12.5), (7, 15.0), (2, 18.0), (9, 25.0), (3, 30.0), (5, 41.0), (12, 55.0), (6, 70.0), (8, 90.0), (11, 120.0)]):
            y = 0.48 + k * 0.04
            L += [Wd(str(k + 1), 0.06, y, 0.02), Wd(str(no), 0.11, y, 0.03), Wd(f'{od:.1f}', 0.85, y, 0.05)]
        pg.evaluate("window.__ocrLines = %s" % json.dumps([L], ensure_ascii=False))
        pg.set_input_files('#ocrFile', [os.path.join(W, 'testdata', 'ocr', 'a_tanfuku_waku.jpg')]); pg.wait_for_timeout(2600)
        o = pg.evaluate("(() => { const f = JSON.parse(localStorage.getItem('tengel.form')); return { r: document.querySelector('#fR').value, venue: document.querySelector('#fVenue').value, date: f.date, dist: f.dist, n: f.n, baba: f.baba, start: f.start, rl: f.rl || null, msg: document.querySelector('#ocrMsg').innerText }; })()")
        print('   読み取り:', {k: o[k] for k in ('r', 'venue', 'date', 'dist', 'n', 'baba', 'start')})
        check(o['r'] == '11' and o['venue'] == '名古屋' and o['date'] == '2026-10-14' and o['dist'] == '1700' and o['n'] == '12' and o['baba'] == '稍重' and o['start'] == '20:15' and '開催場' in o['msg'],
              f'⑨上に「名古屋 9R 10R 11R 12R」・見出しに「11R」の 画面 → 11R（9R に しない）・開催場 名古屋・1700m・12頭・稍重・発走 20:15（{o["r"]}R {o["venue"]}）')
        c13 = pg.evaluate(CARD)
        check(not c13['lines'] and not (o['rl'] and o['rl'].get('lines')), '⑨べつの レースを 読む → 買い目の 行は 空から（前の レースの 行は 持って こない）')
        # ⑩ 作戦会議の レースの 予約：画像は 3枚まで（21:48）・頭数と レース名を 読みやすく
        pg.evaluate("() => window.TCPlanOpen()"); pg.wait_for_function("() => document.querySelector('#tcPlan [data-p=add]')", timeout=30000); pg.wait_for_timeout(300)
        pl = pg.locator('#tcPlan')
        pl.locator('[data-p=add]').click(); pg.wait_for_timeout(400)
        fin = pl.locator('input[data-p=file]')
        check(pl.locator('[data-p=ocr]').inner_text().strip() == '📷 画像から読み取る（3枚まで）' and fin.get_attribute('multiple') is not None, '⑩作戦会議の「レースを予約」：「📷 画像から読み取る（3枚まで）」・写真を まとめて 選べる（multiple）')
        I1 = [Wd('名古屋', 0.08, 0.145, 0.16, 0.016), Wd('9R', 0.42, 0.146, 0.05), Wd('10R', 0.55, 0.146, 0.07), Wd('11R', 0.70, 0.146, 0.07), Wd('12R', 0.84, 0.146, 0.07),
              Wd('11R', 0.07, 0.203, 0.08, 0.018), Wd('2026年10月14日(水)', 0.21, 0.200, 0.32), Wd('テンゲルの日特別 A(1 a)', 0.21, 0.240, 0.52, 0.016), Wd('発走予定時刻:20:15 ダート1700m', 0.21, 0.275, 0.6)]
        I2 = [Wd('11R 出馬表', 0.05, 0.05, 0.4), Wd('出走頭数：12', 0.05, 0.10, 0.4)]
        I3 = [Wd('単勝オッズ', 0.05, 0.05, 0.3)]
        JP = os.path.join(W, 'testdata', 'ocr', 'a_tanfuku_waku.jpg')

        def plan_read(images):
            pg.evaluate("(L) => { window.__ocrLines = L; }", images)
            fin.set_input_files([JP] * len(images)); pg.wait_for_timeout(2200)
            return pg.evaluate("""() => { const r = document.querySelector('#tcPlan'), v = k => (r.querySelector(`[data-f="${k}"]`) || {}).value || '';
              return { name: v('name'), n: v('n'), dist: v('dist'), time: v('time'), date: v('date'), msg: (r.querySelector('.om') || {}).innerText || '', left: window.__ocrLines.length }; }""")
        q1 = plan_read([I1, I2, I3])
        print('   作戦会議①:', q1)
        check(q1['left'] == 0 and q1['name'] == 'テンゲルの日特別 A(1 a)' and q1['n'] == '12' and q1['dist'] == '1700' and q1['time'] == '20:15' and q1['date'] == '2026-10-14'
              and '読み取ったよ（レース名・頭数・距離・発走時間）' in q1['msg'] and '読めなかった' not in q1['msg'],
              f'⑩3枚 まとめて 読む：レース名（見出しの「11R 日付」の 下の 行）・頭数（2枚目の「出走頭数：12」）・距離・発走 → 入る（{q1["name"]}・{q1["n"]}頭）')
        names = [Wd('11R', 0.05, 0.03, 0.1)] + [Wd(f'{k} {nm}', 0.05, 0.08 + k * 0.04, 0.6) for k, nm in enumerate(['サンライズゴールド', 'テンゲルクイーン', 'ナイトレイン', 'ブルーハーバー', 'コスモスカイ', 'ミラクルアロー', 'ハッピーデイズ', 'シルバーウィンド', 'ドリームキャッチャー', 'ロイヤルステップ'], 1)]
        pl.locator('[data-f=name]').fill(''); pl.locator('[data-f=n]').fill('')
        q2 = plan_read([names])
        print('   作戦会議②:', q2)
        check(q2['n'] == '10' and '頭数（写って いた 馬の 数）' in q2['msg'] and '読めなかった：レース名・距離・発走時間' in q2['msg'],
              f'⑩頭数の 字が ない 出馬表（馬番と 名前 1〜10）→ 頭数は 写って いた 馬の 数（10頭）と 書いて 入る・読めなかった 項目も 出す（{q2["msg"][:60]}）')
        pl.locator('[data-f=n]').fill('')
        gap = [Wd('11R', 0.05, 0.03, 0.1)] + [Wd(f'{k} {nm}', 0.05, 0.08 + k * 0.04, 0.6) for k, nm in ((1, 'サンライズゴールド'), (2, 'テンゲルクイーン'), (4, 'ブルーハーバー'), (5, 'コスモスカイ'), (6, 'ミラクルアロー'))]
        q3 = plan_read([gap])
        check(q3['n'] == '' and ('読み取れなかったよ' in q3['msg'] or ('読めなかった：' in q3['msg'] and '頭数' in q3['msg'].split('読めなかった：')[1])), f'⑩馬番が とぎれて いる（3番が ない）ときは 頭数を 決めない（{q3["msg"][:50]}）')
        pl.locator('[data-p=cancel]').click(); pg.wait_for_timeout(300)
        check(not errs, f'画面の エラー なし（{errs[:2]}）')
        ctx.close(); br.close()
finally:
    srv.terminate()
    shutil.rmtree(SRV, ignore_errors=True)
print('合計', len(fails), 'NG' if fails else 'OK', flush=True)
print('FAILS', len(fails), fails)
