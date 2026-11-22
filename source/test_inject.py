# 字の 入口の 総当たり（第4.211版・まさちゃん 2026/11/22 21:36「不正にポイントやバトルコイン、お世話トークンを手に入れる抜け穴は無いか全部細かく徹底的に確認して！」）
#   打った 字・画像から 読んだ 字・ファイルから 読んだ 字が、どこかの 画面で「タグ」に ならない（＝スクリプトを 動かせない → ポイントを 作れない）ことを 総当たりで 見る：
#   ① 保存場所（記録・作戦会議の お気に入りレースと 推し馬・判定の 入力の 途中・マザーデータの 枠の 名前と ファイルの 名前・ポイントの 台帳に 残る 字）に じかに「タグに なる 字」を 入れる
#      （入口の そうじ〈区切りの 字・全角に かえる〉を ぬけた と した とき＝いちばん きびしい 形）
#   ② 画面を ぜんぶ 開いて（判定・単勝5連勝・記録・実測・設定・ポイント・ミッション・予約済みの 窓・推し馬・フィギュア・作戦会議・カードバトル）、押せる ものを 順に 押す
#   ③ そのつど [data-xss] の タグが できて いないか（1つでも できたら ❌：その 所を 字と して 出す ように 直す）
#   python3 test_inject.py   （App Store版〈TARGET=app〉を localhost で アプリ版と して 開く・絵と 音は なくて よい）
import json, os, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv_inj'); PORT = 8829
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, TARGET='app', HIST='hist_280.json', DROP=''))
pth = os.path.join(SRV, 'APP', 'index.html'); html = open(pth, encoding='utf8').read()
assert "window.__NATIVE = location.protocol === 'tengel:';" in html
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
FAKE = open(os.path.join(W, 'test_cb.py'), encoding='utf8').read().split('FAKE = """')[1].split('"""')[0]      # アプリの 窓口の にせもの（test_cb.py と 同じ）
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c: fails.append(label)


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


def boot(p, port):
    b = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo', has_touch=True, is_mobile=True)
    ctx.route('**/__native/autobackup.json', lambda route: route.fulfill(status=404, body='not found'))
    ctx.add_init_script(FAKE)
    pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto(f'http://localhost:{port}/APP/'); pg.wait_for_function("() => window.TengelWallet && TengelWallet.on", timeout=40000); pg.wait_for_timeout(700); gate(pg); pg.wait_for_timeout(800)
    return b, ctx, pg, errs


XS = '"\'><i data-xss="1">X</i>'
SEED = r"""async (XS) => {
  const P = s => String(s) + XS, now = new Date().toISOString();
  const horses = [1,2,3,4,5,6,7,8,9,10,11,12,13,14].map(no => ({ no: no, tan: (no * 1.7 + 1).toFixed(1), fuku: P('1.' + no), name: P('馬' + no) }));
  const names = {}; horses.forEach(h => { names[h.no] = P('ナマエ' + h.no); });
  const mk = (i, st_, extra) => Object.assign({ id: P('2026' + '110' + (i + 1) + '-V-' + (7 + i)), date: '2026-11-0' + (i + 1), venue: P('V'), r: P(String(7 + i)), rname: P('レース名'), n: P('14'), dist: P('1200'), surface: P('ダ'), baba: P('良'),
    start: P('12:3' + i), types: [P('馬単'), '3連単'], amt: { [P('馬単')]: { stake: 600, payout: 0 } }, other: P('購入'), note: P('メモ'), judgeText: P('判定の 文'), buyZ: P('第1'), hp: P('hp'),
    s1combo: P('1-2-3'), s5combo: P('1-2-4'), s10combo: P('1-2-5'), tan1: 2.1, s1: 30.5, s5: 60, s10: 90,
    n1: 5, n2: 2, n3: 1, p1: 3, p2: 1, p3: 2, stake: P('600'), payout: P('0'), horses: horses, names: names, pn: [P('一着'), P('二着'), P('三着')],
    snap: { L: P('B'), kubun: P('B'), zones: [P('人気→人気')], band: P('固定'), ratio: P('12.3') },
    rsv: { state: st_, types: [P('馬単')], bets: { [P('馬単')]: [[5, 2]] }, zones: [P('z')], word: P('ことば'), legs: [P('leg')], self: { [P('馬単')]: [[P('5'), P('2')]] }, by: P('by'), at: now, start: P('23:59'),
      result: st_ === 'done' ? { p: [[5], [2], [1]], names: [P('一'), P('二'), P('三')], cancel: [P('4')], pay: { [P('馬単')]: P('1230') } } : undefined, fx: st_ === 'done' ? (i % 2 ? 'hit' : 'miss') : undefined, judged: st_ === 'done' ? { [P('馬単')]: P('hit') } : undefined },
    mem: { at: now, v: P('a'), bets: [P('m')] }, pid: P('pid'), mslot: 0, updatedAt: now, createdAt: now }, extra || {});
  const list = [mk(0, 'done'), mk(1, 'done'), mk(2, 'reserved'), mk(3, 'given'), mk(4, 'done', { rsv: undefined, mem: undefined })];
  // 今月の 記録も（記録タブは 今月を 開く）
  const d = new Date(), ym = d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0');
  [0, 1, 2].forEach(i => { const b = mk(5 + i, ['done', 'reserved', 'given'][i]); b.id = P('cur' + i); b.date = ym + '-0' + (i + 1); list.push(b); });
  await TengelLocal.putBets(list);
  // 作戦会議（お気に入りレース・推し馬）
  localStorage.setItem('tengel.plan', JSON.stringify({ v: 1, on: true, races: [0, 1].map(i => ({ id: P('p' + i), date: ym + '-2' + i, time: P('12:0' + i), name: P('予約レース'), venue: P('V'), r: P('8'), n: P('14'), dist: P('1200'), memo: P('さくせん'), notify: [20] })) }));
  localStorage.setItem('tengel.oshi', JSON.stringify([0, 1].map(i => ({ id: P('o' + i), name: P('推し馬'), ped: Array(14).fill(0).map((_, k) => P('血' + k)), memo: P('びこう'), at: now }))));
  // 判定の 入力の とちゅう（画像から 読んだ 字が 入る 所）
  try { const f = JSON.parse(localStorage.getItem('tengel.form') || '{}'); Object.assign(f, { venue: P('V'), rname: P('レース名'), start: P('12:30'), s1combo: P('1-2-3'), s5combo: P('1-2-4'), s10combo: P('1-2-5'), names: names, baba: P('良'), surface: P('ダ'), hp: P('hp') }); localStorage.setItem('tengel.form', JSON.stringify(f)); } catch (e) { }
  // マザーデータの 枠の 名前・読んだ ファイルの 名前
  const out = { slots: null, mother: null, charge: null };
  try { const S = TengelLocal.slots; out.slotsKeys = Object.keys(S || {}); if (S && S.rename) { await S.rename(2, P('わく2')); out.slots = 'ok'; } } catch (e) { out.slots = String(e); }
  try { const S = TengelLocal.slots; if (S && S.replace) { await S.replace(2, [{ id: P('r1'), date: '2026-10-01', r: 8, baba: P('良'), dist: 1200, surface: P('ダ'), n: 14, tan1: 2.1, s1: 30, s5: 60, s10: 90, p1: 1, p2: 2, p3: 3, src: P('app') }], { source: P('excel'), file: P('ファイル名.xlsx') }); out.mother = 'ok'; } } catch (e) { out.mother = String(e); }
  // ポイントの 台帳に 残る 字（読み込み：開催場・R）
  try { const W = TengelWallet; const a = await W.readCharge({ form: { date: '2026-11-20', venue: P('V'), r: 8, rname: P('名') }, ocr: { date: '2026-11-20', venue: P('V'), r: 8 } }); out.charge = a && a.ok; } catch (e) { out.charge = String(e); }
  return out;
}"""
XN = "() => document.querySelectorAll('[data-xss]').length"
WHERE = """() => [...document.querySelectorAll('[data-xss]')].slice(0, 6).map(e => { const path = []; let n = e.parentElement; for (let i = 0; i < 6 && n; i++, n = n.parentElement) path.push(n.tagName.toLowerCase() + (n.id ? '#' + n.id : '') + (n.className && typeof n.className === 'string' ? '.' + n.className.trim().split(/\\s+/).slice(0, 2).join('.') : '')); return path.join(' < ') + ' :: ' + (e.parentElement ? e.parentElement.outerHTML.slice(0, 200) : ''); })"""
found = []


shown = {}      # 画面の 名前 → 入れた 字が「字と して」見えた 回数（data-xss の 字が 画面に 出て いる＝その 画面は 入れた 字を 本当に 出して いる）


def scan(pg, where):
    try:
        if pg.evaluate("() => ((document.body && document.body.innerText) || '').indexOf('data-xss') >= 0 || [...document.querySelectorAll('input, textarea')].some(e => (e.value || '').indexOf('data-xss') >= 0)"):
            k = where.split(' → ')[0]; shown[k] = shown.get(k, 0) + 1
    except Exception: pass
    n = pg.evaluate(XN)
    if n:
        w = pg.evaluate(WHERE)
        key = (where, w[0].split(' :: ')[0] if w else '')
        if key not in [f[0] for f in found]:
            found.append((key, w)); print('  ❌ タグが できた：', where, '\n     ', '\n      '.join(w)[:900], flush=True)
        pg.evaluate("() => document.querySelectorAll('[data-xss]').forEach(e => e.remove())")
    return n


SKIP = ['消', '削除', 'リセット', '戻す', 'はじめから', '購入', '買う', '復元', 'バックアップ', '保存', '共有', 'コピー', '写真', '画像', 'カメラ', '読み取', 'ファイル', '更新', 'レビュー', 'お問い合わせ', '確かめる', 'ストア']
# 押せる もの を 順に 押す（1つの 画面で max 回まで）。押す たびに タグが できて いないか 見る
MONKEY = """(arg) => {
  const [seen, skip, root] = arg;
  const shown = e => { const r = e.getBoundingClientRect(); if (r.width < 4 || r.height < 4) return false; const cs = getComputedStyle(e); return !(cs.visibility === 'hidden' || cs.display === 'none'); };
  const vis = e => { if (!shown(e) || getComputedStyle(e).pointerEvents === 'none') return false; const r = e.getBoundingClientRect(); const x = Math.min(innerWidth - 1, Math.max(0, r.left + r.width / 2)), y = Math.min(innerHeight - 1, Math.max(0, r.top + r.height / 2)); const t = document.elementFromPoint(x, y); return !!t && (t === e || e.contains(t) || t.contains(e)); };
  // いちばん 上に 開いて いる 窓（あれば その 中 だけ を 押す）
  const ovs = [...document.querySelectorAll('.tgov, #tcPlan, #fgOv, #fxOv, #ptOv, #msOv, #mdSheet, #lgOv, #nativeRestore, #cbOv, [role=dialog], .modal, .sheet')].filter(e => e.id !== 'gate' && e.id !== 'manOv' && shown(e) && !e.hidden);
  const ov = ovs.length ? ovs[ovs.length - 1] : null;
  const base = ov || (root ? document.querySelector(root) : document.body) || document.body;
  const els = [...base.querySelectorAll('button, summary, [role=button], [role=tab], [role=switch], a[href], [data-act], [data-rsv], [data-p], [data-cb], [data-ks], [data-ms], [data-go], [data-open], select, .lmain, .lrow, li[data-id], tr[data-id], div[data-id]')];
  for (const e of els) {
    if (e.disabled || e.type === 'file' || e.id === 'manBtn' || e.closest('.tabbar') || (!ov && e.closest('#fabCol, header, .top, #minibar'))) continue;
    const txt = ((e.getAttribute('aria-label') || '') + ' ' + (e.textContent || '')).replace(/\\s+/g, ' ').trim().slice(0, 40);
    const key = (ov ? (ov.id || ov.className.split(' ')[0]) + '>' : '') + e.tagName + '|' + (e.id || '') + '|' + [...e.attributes].filter(a => a.name.startsWith('data-')).map(a => a.name + '=' + a.value.slice(0, 20)).join(',') + '|' + txt.slice(0, 24);
    if (seen.indexOf(key) >= 0) continue;
    seen.push(key);
    if (skip.some(w => txt.indexOf(w) >= 0)) continue;
    if (e.tagName === 'A' && /^(https?:|mailto:)/.test(e.getAttribute('href') || '')) continue;
    try { e.scrollIntoView({ block: 'center' }); } catch (x) { }
    if (!vis(e)) continue;
    try { if (e.tagName === 'SELECT') { const o = [...e.options]; if (o.length > 1) { e.selectedIndex = (e.selectedIndex + 1) % o.length; e.dispatchEvent(new Event('change', { bubbles: true })); } } else e.click(); } catch (x) { }
    return { key: key, seen: seen, ov: ov ? (ov.id || ov.className) : '' };
  }
  // この 窓の 中は ぜんぶ 押した → 窓を 閉じる
  if (ov) {
    const c = [...ov.querySelectorAll('button, [data-ms=close], [data-p=close]')].filter(e => /閉じる|とじる|×|✕|キャンセル|やめる|もどる|戻る|OK|はい|いいえ/.test((e.getAttribute('aria-label') || '') + e.textContent) && shown(e));
    if (c.length) c[0].click(); else ov.remove();
    return { key: '(close ' + (ov.id || ov.className) + ')', seen: seen, closed: true };
  }
  return { key: null, seen: seen };
}"""


def monkey(pg, name, root=None, maxn=260, settle=150, tab=None):
    seen = []; n = 0; closes = 0
    while n < maxn and closes < 60:
        if tab:      # ほかの タブへ とんだ とき は もどる
            pg.evaluate("(t) => { const v = document.querySelector('#v-' + t); if (v && (v.hidden || getComputedStyle(v).display === 'none')) { const b = document.querySelector('.tabbar button[data-tab=' + t + ']'); if (b) b.click(); } }", tab)
        r = pg.evaluate(MONKEY, [seen, SKIP, root]); seen = r['seen']
        if not r['key']: break
        pg.wait_for_timeout(settle)
        if r.get('closed'): closes += 1; continue
        n += 1
        scan(pg, name + ' → ' + r['key'][:90])
    return n


try:
    with sync_playwright() as p:
        b, ctx, pg, errs = boot(p, PORT)
        pg.on('dialog', lambda d: d.dismiss())
        seedr = pg.evaluate(SEED, XS); pg.wait_for_timeout(600)
        pg.reload(); pg.wait_for_function("() => window.TengelWallet && TengelWallet.on", timeout=40000); pg.wait_for_timeout(900); gate(pg); pg.wait_for_timeout(900)
        nb = pg.evaluate("TengelLocal.mem.bets.size")
        scan(pg, 'boot')
        tot = 0
        for tab in ['judge', 'win5', 'rec', 'stats', 'set']:
            pg.evaluate("(t) => { const b = document.querySelector('.tabbar button[data-tab=' + t + ']'); if (b) b.click(); }", tab); pg.wait_for_timeout(600)
            scan(pg, 'tab ' + tab)
            pg.evaluate("() => document.querySelectorAll('details').forEach(d => { d.open = true; })"); pg.wait_for_timeout(300); scan(pg, 'tab ' + tab + ' details')
            k = monkey(pg, 'tab ' + tab, root='#v-' + tab, tab=tab); tot += k
            print(f'  ・{tab}: 押した {k}こ・いま {pg.evaluate("document.querySelector(\'.tabbar button[aria-selected=true], .tabbar button.on\') ? document.querySelector(\'.tabbar button[aria-selected=true], .tabbar button.on\').dataset.tab : \'?\'")}', flush=True)
        # 上の ボタン・右下の 丸い ボタン
        for sel in ['#ptsPill', '#msBtn', '#rsvBtn', '#oshiFab', '#figFab']:
            pg.reload(); pg.wait_for_function("() => window.TengelWallet && TengelWallet.on", timeout=40000); pg.wait_for_timeout(800); gate(pg); pg.wait_for_timeout(600)
            pg.evaluate("(s) => { const b = document.querySelector(s); if (b) b.click(); }", sel); pg.wait_for_timeout(1500)
            scan(pg, 'open ' + sel)
            k = monkey(pg, 'open ' + sel, maxn=90, settle=220); tot += k
            print(f'  ・{sel}: 押した {k}こ', flush=True)
        for nm, js in [('作戦会議', "() => window.TCPlanOpen && TCPlanOpen()"), ('カードバトル', "() => window.TengelCB && TengelCB.open()")]:
            pg.reload(); pg.wait_for_function("() => window.TengelWallet && TengelWallet.on", timeout=40000); pg.wait_for_timeout(800); gate(pg); pg.wait_for_timeout(600)
            try: pg.evaluate(js)
            except Exception as e: print('   ※', nm, str(e)[:120])
            pg.wait_for_timeout(2500); scan(pg, 'open ' + nm)
            k = monkey(pg, 'open ' + nm, maxn=120, settle=220); tot += k
            print(f'  ・{nm}: 押した {k}こ', flush=True)
        check(seedr.get('slots') == 'ok' and seedr.get('mother') == 'ok' and seedr.get('charge') is True and nb >= 8, f'タグに なる 字を じかに 入れた（記録 {nb}件・作戦会議・推し馬・枠の 名前・ファイルの 名前・台帳に 残る 字）')
        check(tot >= 150, f'画面を 回って 押せる ものを 押した（{tot}回）')
        need = ['tab judge', 'tab rec', 'tab set', 'open #rsvBtn', 'open #oshiFab', 'open 作戦会議']
        check(all(shown.get(k, 0) > 0 for k in need), f'入れた 字は 字と して 画面に 出て いる（判定・記録・設定・予約済みの 窓・推し馬・作戦会議：{ {k: shown.get(k, 0) for k in need} }・ほか {sorted(k for k in shown if k not in need)}）')
        check(not found, f'どの 画面でも タグは できない（できた 所 {len(found)}：{[k[0][:60] + " | " + k[1][:80] for (k, w) in found][:4]}）')
        check(not errs, f'ページの エラー なし {errs[:3]}')
        b.close()
finally:
    srv.terminate()
print('\n' + ('全部 OK' if not fails else f'NG {len(fails)}こ：' + ' / '.join(fails)))
sys.exit(1 if fails else 0)
