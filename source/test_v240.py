# 第4.240版の テスト（まさちゃん 2026/11/28 20:51「紫四角のアイコン達、結果を打ち込むときや、レースの記録を行う時は表示されなくできる？」）
#   丸い ボタンの 列（#fabCol：トレーニングセンター・推し馬・TENGERカードバトル・思い出フィギュア）を 消す とき（html.fabhide：tc/tc_launch.js）
#   ① 字・数字の 欄に 入って いる あいだ（どの タブでも：判定の 入力・単勝5連勝の 結果・テンキーの とき）→ 欄から 出ると もどる
#   ② 欄から 欄へ 移る（テンキーの「次へ」・つぎの 欄を 押す）ときは 出たり 消えたり しない
#   ③ 記録タブで 記録を 開いて いる あいだ（予約した レースの 結果の 欄：.ledit）→ 閉じる・ほかの タブへ 行くと もどる・記録タブに もどると また 消える
#   ④ 消えても 場所・大きさ・まわり（判定の 帯・main の 下の 余白・--fabt）は 動かない・消えて いる あいだは 押せない（後ろの 画面に とどく）
#   ⑤ 選ぶ だけの 欄（select）・読む だけの 欄（書き出しの 字）・ボタンでは 消えない
#   ⑥ 欄が 窓ごと 消えた（フォーカスが のこった まま）ときも もどる・作戦会議の 窓で 字を 打って 閉じた あとも もどる
#   ⑦ もどった あとは ふつうに 押せる（推し馬 → 作戦会議）・Web版には 入らない
#   python3 test_v240.py   （SHOT=フォルダ で 画面を 写す）
import json, os, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv_v240'); PORT = 8872; APP = f'http://localhost:{PORT}/APP/'
SHOT = os.environ.get('SHOT')
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
ENV = dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, HIST='hist_280.json', DROP='')
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict(ENV, TARGET='app'))
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'WEB')], check=True, stdout=subprocess.DEVNULL, env=dict(ENV, TARGET='web'))
pth = os.path.join(SRV, 'APP', 'index.html'); html = open(pth, encoding='utf8').read()
web = open(os.path.join(SRV, 'WEB', 'index.html'), encoding='utf8').read()
assert "window.__NATIVE = location.protocol === 'tengel:';" in html
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
FAKE = open(os.path.join(W, 'test_tc.py'), encoding='utf8').read().split('FAKE = """')[1].split('"""')[0]      # アプリの 窓口の にせもの（test_tc.py と 同じ）
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


def shot(pg, name):
    if SHOT: os.makedirs(SHOT, exist_ok=True); pg.screenshot(path=os.path.join(SHOT, name + '.png'))


# 判定した レース（test_dataentry.py と 同じ：開催場は 空）→ 判定タブの「買い目を予約」→ 記録タブの 予約レース
form = {"venue": "", "date": "2026-10-14", "r": "8", "dist": "1400", "surface": "ダ", "baba": "稍重", "n": "14", "s1": "41.3", "s1combo": "6-2-10", "s5": "58.2", "s10": "84.0",
        "rows": [{"no": no, "tan": str(t), "fuku": f} for no, t, f in [(1, 12.4, '3.0-4.6'), (2, 4.1, '1.6-2.2'), (3, 31.5, '6.1-9.8'), (4, 9.8, '2.6-3.9'), (5, 18.2, '4.0-6.2'), (6, 2.4, '1.1-1.3'), (7, 7.6, '2.1-3.1'),
                                                                 (8, 54.0, '9.4-15.0'), (9, 25.9, '5.2-8.1'), (10, 6.3, '1.9-2.7'), (11, 14.7, '3.3-5.1'), (12, 88.6, '13.2-21.1'), (13, 40.2, '7.7-12.2'), (14, 120.5, '18.4-29.6')]]}
SEED = "if (!sessionStorage.getItem('seeded')) { localStorage.setItem('tengel.form', %s); localStorage.setItem('tengel.tab', '\"judge\"'); sessionStorage.setItem('seeded', '1'); }"
# 列の いま：h＝html.fabhide・vis／op＝見え方・hit＝トレーニングセンターの 丸の まん中を 押すと 列に とどく か・box＝列の 四角・まわり（--fabt・main の 下の 余白・判定の 帯）
ST = """() => { const c = document.getElementById('fabCol'), cs = getComputedStyle(c), b = document.querySelector('#tcFab .fabi'), r = b.getBoundingClientRect();
  const t = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2), cr = c.getBoundingClientRect(), mn = document.querySelector('main'), mb = document.getElementById('minibar'), a = document.activeElement;
  return { h: document.documentElement.classList.contains('fabhide'), vis: cs.visibility, op: Math.round(parseFloat(cs.opacity) * 100) / 100, hit: !!t && c.contains(t),
    box: [cr.left, cr.top, cr.right, cr.bottom].map(v => Math.round(v * 10) / 10), fd: cs.getPropertyValue('--fd').trim(), fabt: getComputedStyle(document.documentElement).getPropertyValue('--fabt').trim(),
    pb: mn ? mn.style.paddingBottom : null, mini: mb && !mb.hidden ? Math.round(mb.getBoundingClientRect().top * 10) / 10 : null, act: a ? (a.id || a.tagName) : null }; }"""
# html.fabhide の 出たり 消えたり の 記録（__fh：かわる たびに 1つ）
WATCH = """() => { window.__fh = [document.documentElement.classList.contains('fabhide')];
  new MutationObserver(() => { const on = document.documentElement.classList.contains('fabhide'); if (window.__fh[window.__fh.length - 1] !== on) window.__fh.push(on); })
    .observe(document.documentElement, { attributes: true, attributeFilter: ['class'] }); }"""
# 押しても なにも おきない 所（main の 中の ふつうの 字・地：ボタン・リンク・欄・ラベルの 外）
PLAIN = """() => { const NG = 'button,a,label,input,select,textarea,summary,details,[role=button],[data-act],[data-k],[tabindex],#fabCol,#minibar,header,.tabbar';
  for (let y = 160; y < innerHeight - 200; y += 8) for (let x = 12; x < innerWidth - 12; x += 16) { const e = document.elementFromPoint(x, y);
    if (e && e.closest('main') && !e.closest(NG)) return [x, y]; } return [8, 400]; }"""
SHOWN = lambda s: (not s['h']) and s['vis'] == 'visible' and s['op'] == 1 and s['hit']
GONE = lambda s: s['h'] and s['vis'] == 'hidden' and s['op'] == 0 and not s['hit']
SAME = lambda a, b: a['box'] == b['box'] and a['fd'] == b['fd'] and a['fabt'] == b['fabt'] and a['pb'] == b['pb'] and a['mini'] == b['mini']


def rsv_lines(pg):
    """買い目の 行が ない ときは、推奨ごとに 馬単（3着の ある 推奨は 3連単も）の 行を「＋券種」で 足す（test_dataentry.py と 同じ）"""
    card = pg.locator('#recCard')
    if card.locator('.rline').count() or not card.locator('[data-k=radd]').count(): return
    nz = pg.locator('#result ol.zones > li').count(); t3 = pg.locator('#result .zthird .zref').count() > 0
    for t in ['馬単'] * nz + (['3連単'] * nz if t3 else []):
        card.locator(f'[data-k=radd] button[data-v="{t}"]').click(); pg.wait_for_timeout(120)


try:
    print('■ 中身（App Store版の index.html）')
    code = open(os.path.join(W, 'tc', 'tc_launch.js'), encoding='utf8').read()
    check("html.fabhide #fabCol{opacity:0;visibility:hidden}" in html and 'function fabHideNow() {' in html and 'hidden: fabHideNow' in html
          and "document.addEventListener('focusout', function () { fabHideAsk(80); }, true);" in html and 'hideP = setInterval(function () { if (!hideT) fabHideNow(); }, 400);' in html
          and "var e = v.querySelector('.ledit'); return !!(e && e.getClientRects().length);" in html and 'まさちゃん' not in html,
          'App Store版：丸い ボタンの 列を 消す しかけ（字の 欄・記録を 開いて いる あいだ・0.08秒 待つ・0.4秒ごとの 見直し）が 入って いる')
    check('fabhide' not in web and 'fabHideNow' not in web, 'Web版には 入らない（丸い ボタンの 列は App Store版 だけ）')
    st_js = open(os.path.join(W, 'ios', 'ci', 'selftest.js'), encoding='utf8').read(); run_sh = open(os.path.join(W, 'ios', 'ci', 'run.sh'), encoding='utf8').read()
    check("await step(R, 'fabHide', async function () {" in st_js and run_sh.count('python3 -c "$FABPY"') == 2 and "FABPY='" in run_sh,
          'GitHub の Mac（本物の WebKit）でも たしかめる（selftest の fabHide・run.sh の fab hide：iPhone・iPad）')

    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo', has_touch=True)
        ctx.add_init_script(FAKE); ctx.add_init_script(SEED % json.dumps(json.dumps(form, ensure_ascii=False)))
        pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(APP); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(600)
        pg.wait_for_function("() => document.querySelectorAll('#fabCol > button').length >= 2 && document.querySelector('#recCard [data-rsv=reserve]') && window.TengelFab && !TengelFab.busy()", timeout=30000)
        pg.wait_for_timeout(2600)                                                     # はじめの 2秒（fitHold）が すぎて 列の 大きさが 落ち着く まで
        pg.evaluate(WATCH)

        print('■ ① 判定タブ：字・数字の 欄に 入る → 消える・出る → もどる')
        s0 = pg.evaluate(ST)
        check(SHOWN(s0) and pg.locator('#tcFab').is_visible(), f'はじめは 見える・押せる（{s0["vis"]}・{s0["op"]}・押すと 列に とどく {s0["hit"]}）')
        pg.evaluate("() => document.querySelector('#fDist').focus()"); pg.wait_for_timeout(350); s1 = pg.evaluate(ST)
        check(GONE(s1) and not pg.locator('#tcFab').is_visible() and s1['act'] == 'fDist', f'距離の 欄に 入る → 消える（{s1["vis"]}・{s1["op"]}・押すと うしろに とどく）')
        check(SAME(s0, s1), f'④ 消えても 列の 場所・大きさ・まわりは 同じ（列 {s1["box"]}・丸 {s1["fd"]}・--fabt {s1["fabt"]}・main の 下 {s1["pb"]}・判定の 帯 {s1["mini"]}）')
        shot(pg, 'v240_1_typing')
        pg.evaluate("() => document.querySelector('#fN').focus()"); pg.wait_for_timeout(300); s2 = pg.evaluate(ST)
        pg.locator('#fRname').click(); pg.wait_for_timeout(300); s3 = pg.evaluate(ST)
        check(GONE(s2) and GONE(s3) and pg.evaluate('window.__fh') == [False, True], f'② となりの 欄（頭数・レース名を 押す）へ → 消えた まま（出たり 消えたり しない：{pg.evaluate("window.__fh")}）')
        # 出た すぐ と 0.03秒 あと（ページの 中の 時計で 測る：0.08秒 待って から もどる）
        s4a = pg.evaluate("() => new Promise(res => { const C = () => document.documentElement.classList.contains('fabhide'); document.activeElement.blur(); const a = C(); setTimeout(() => res([a, C()]), 30); })")
        pg.wait_for_timeout(300); s4 = pg.evaluate(ST)
        check(s4a == [True, True] and SHOWN(s4) and SAME(s0, s4) and pg.evaluate('window.__fh') == [False, True, False],
              f'欄から 出る → 0.08秒 まって もどる（出た すぐ・0.03秒 あと {s4a} → {s4["h"]}・{s4["vis"]}・{s4["op"]}・押せる {s4["hit"]}）')
        pg.locator('#fRname').click(); pg.wait_for_timeout(300); s5a = pg.evaluate(ST)
        pt = pg.evaluate(PLAIN); pg.mouse.click(pt[0], pt[1]); pg.wait_for_timeout(400); s5 = pg.evaluate(ST)
        check(GONE(s5a) and SHOWN(s5), f'欄を 押す → 消える・欄の 外を 押す → もどる（{s5a["h"]} → {s5["h"]}）')

        print('■ ⑤ 選ぶ だけの 欄・ボタンでは 消えない')
        pg.evaluate("() => document.querySelector('#fR').focus()"); pg.wait_for_timeout(300); s6 = pg.evaluate(ST)
        pg.evaluate("() => document.querySelector('#planBtn') && document.querySelector('#planBtn').focus()"); pg.wait_for_timeout(300); s7 = pg.evaluate(ST)
        check(SHOWN(s6) and s6['act'] == 'fR' and SHOWN(s7), f'R の 選ぶ 欄（select）・作戦会議の 札（ボタン）では 消えない（{s6["act"]} {s6["h"]}・{s7["act"]} {s7["h"]}）')
        pg.evaluate("() => document.activeElement.blur()"); pg.wait_for_timeout(200)

        print('■ ① 単勝5連勝タブ：1着の 欄（テンキー）')
        pg.click('.tabbar button[data-tab=win5]'); pg.wait_for_timeout(600)
        pg.evaluate("() => { document.activeElement.blur(); window.scrollTo(0, 0); }"); pg.wait_for_timeout(300); w0 = pg.evaluate(ST)
        pg.evaluate("() => { const f = document.querySelector('#w5Win0'); f.scrollIntoView({ block: 'center' }); f.focus(); }"); pg.wait_for_timeout(1000)
        np = pg.evaluate("() => window.TengelNumpad ? TengelNumpad.state() : null"); w1 = pg.evaluate(ST)
        check(SHOWN(w0) and np and np['open'] and np['target'] == 'w5Win0' and GONE(w1), f'1着の 欄に 入る → テンキーが 出る・列は 消える（テンキー {np and np["open"]}・{w1["vis"]}）')
        shot(pg, 'v240_2_numpad')
        fh0 = len(pg.evaluate('window.__fh'))
        pg.locator('#numPad button[data-k=next]').click(); pg.wait_for_timeout(300); np2 = pg.evaluate("() => TengelNumpad.state()"); w2 = pg.evaluate(ST)
        check(np2['open'] and np2['target'] == 'w5Win1' and GONE(w2) and len(pg.evaluate('window.__fh')) == fh0, f'② テンキーの「次へ」→ つぎの 欄（{np2["target"]}）・消えた まま（出たり 消えたり しない）')
        pg.locator('#numPad button[data-k=done]').click(); pg.wait_for_timeout(400); np3 = pg.evaluate("() => TengelNumpad.state()"); w3 = pg.evaluate(ST)
        check(not np3['open'] and SHOWN(w3) and w3['box'] == w0['box'], f'「完了」→ テンキーを しまう → もどる（{w3["vis"]}・押せる {w3["hit"]}）')
        pg.evaluate("() => { const f = document.querySelector('#w5Pay'); f.scrollIntoView({ block: 'center' }); f.focus(); }"); pg.wait_for_timeout(300); w4 = pg.evaluate(ST)
        pg.evaluate("() => document.activeElement.blur()"); pg.wait_for_timeout(300); w5 = pg.evaluate(ST)
        check(GONE(w4) and SHOWN(w5), f'払戻の 欄 → 消える・出る → もどる（{w4["h"]} → {w5["h"]}）')

        print('■ ⑤ 記録タブ：書き出しの 字（読む だけ）では 消えない')
        pg.click('.tabbar button[data-tab=rec]'); pg.wait_for_timeout(600)
        pg.locator('#recExportBtn').click(); pg.wait_for_timeout(300)
        pg.evaluate("() => document.querySelector('#recExportText').focus()"); pg.wait_for_timeout(300); r0 = pg.evaluate(ST)
        check(SHOWN(r0) and r0['act'] == 'recExportText', f'書き出しの 字（readonly）に 入っても 消えない（{r0["act"]} {r0["h"]}）')
        pg.locator('#recExportBtn').click(); pg.wait_for_timeout(200); pg.evaluate("() => document.activeElement.blur()")

        print('■ ③ 記録を 開いて いる あいだ（予約した レースの 結果の 欄）')
        pg.click('.tabbar button[data-tab=judge]'); pg.wait_for_timeout(500)
        card = pg.locator('#recCard')
        if card.locator('[data-rsv=redo]').count(): card.locator('[data-rsv=redo]').click(); pg.wait_for_timeout(200)
        rsv_lines(pg); card.locator('[data-rsv=reserve]').click(); pg.wait_for_timeout(900)
        rid = pg.evaluate("(() => { const b = [...TengelLocal.mem.bets.values()].find(x => x.rsv && x.rsv.state === 'reserved'); return b ? b.id : null; })()")
        check(bool(rid), f'判定タブで「買い目を予約」→ 予約レースが できた（{rid}）')
        pg.evaluate("() => document.activeElement && document.activeElement.blur()")
        pg.click('.tabbar button[data-tab=rec]'); pg.wait_for_timeout(600)
        row = pg.locator(f'#recList .lrow[data-id="{rid}"]')
        e0 = pg.evaluate(ST)
        check(row.count() == 1 and not row.locator('.ledit').count() and SHOWN(e0), f'記録タブ：予約レースの 行（閉じて いる）→ 見える（{e0["h"]}）')
        row.locator('.lmain').click(); pg.wait_for_timeout(500); e1 = pg.evaluate(ST)
        has = row.locator('.ledit .rsvf').count() == 1
        check(has and GONE(e1) and e1['act'] in ('BUTTON', 'BODY') and SAME(e0, e1), f'行を 開く（結果の 欄）→ 欄に 入って いなくても 消える（{e1["act"]}・{e1["vis"]}・場所 同じ {SAME(e0, e1)}）')
        shot(pg, 'v240_3_record')
        fh1 = len(pg.evaluate('window.__fh'))
        f1 = row.locator('.rsvf [data-k=p1]'); f1.click(); pg.wait_for_timeout(250); e2 = pg.evaluate(ST)
        pg.evaluate("() => document.activeElement.blur()"); pg.wait_for_timeout(400); e3 = pg.evaluate(ST)
        check(GONE(e2) and GONE(e3) and len(pg.evaluate('window.__fh')) == fh1, f'開いた まま 1着の 欄に 入る・出る → 消えた まま（出たり 消えたり しない）')
        row.locator('.lmain').click(); pg.wait_for_timeout(500); e4 = pg.evaluate(ST)
        check(not row.locator('.ledit').count() and SHOWN(e4) and SAME(e0, e4), f'行を 閉じる → もどる（{e4["vis"]}・押せる {e4["hit"]}）')
        row.locator('.lmain').click(); pg.wait_for_timeout(500); e5 = pg.evaluate(ST)
        pg.click('.tabbar button[data-tab=judge]'); pg.wait_for_timeout(500); e6 = pg.evaluate(ST)
        pg.click('.tabbar button[data-tab=rec]'); pg.wait_for_timeout(600); e7 = pg.evaluate(ST)
        row = pg.locator(f'#recList .lrow[data-id="{rid}"]')
        check(GONE(e5) and SHOWN(e6) and GONE(e7) and row.locator('.ledit').count() == 1, f'開いた まま ほかの タブへ → もどる・記録タブに もどる（開いた まま）→ また 消える（{e5["h"]} → {e6["h"]} → {e7["h"]}）')
        row.locator('.lmain').click(); pg.wait_for_timeout(500); e8 = pg.evaluate(ST)
        check(SHOWN(e8), f'閉じる → もどる（{e8["h"]}）')

        print('■ ⑥ 欄が 窓ごと 消えた とき')
        pg.evaluate("() => { const d = document.createElement('div'); d.id = 'v240box'; d.style.cssText = 'position:fixed;left:10px;top:200px;z-index:50;background:#fff;padding:8px'; d.innerHTML = '<input id=\"v240in\">'; document.body.appendChild(d); document.querySelector('#v240in').focus(); }")
        pg.wait_for_timeout(300); g1 = pg.evaluate(ST)
        pg.evaluate("() => { document.querySelector('#v240box').style.display = 'none'; }"); pg.wait_for_timeout(700); g2 = pg.evaluate(ST)
        pg.evaluate("() => document.querySelector('#v240box').remove()")
        check(GONE(g1) and SHOWN(g2), f'欄に 入る → 消える・欄の 窓を かくす（フォーカスの 知らせが なくても）→ 0.7秒の うちに もどる（{g1["h"]} → {g2["h"]}・{g2["act"]}）')

        print('■ ⑦ もどった あとは ふつうに 押せる：推し馬 → 作戦会議（字を 打って 閉じる）')
        pg.click('.tabbar button[data-tab=judge]'); pg.wait_for_timeout(500)
        pg.locator('#oshiFab .fabi').click(); pg.wait_for_function("() => window.TCPlan && TCPlan.isOpen()", timeout=30000); pg.wait_for_timeout(500)
        inp = pg.locator('#tcPlan input:visible, #tcPlan textarea:visible').first
        typed = inp.count() > 0
        if typed: inp.click(); pg.keyboard.type('ab'); pg.wait_for_timeout(300)
        k1 = pg.evaluate(ST)
        pg.locator('#tcPlan [data-p=close]').click(); pg.wait_for_timeout(800); k2 = pg.evaluate(ST)
        check(pg.evaluate("() => !TCPlan.isOpen()") and (not typed or k1['h']) and SHOWN(k2), f'推し馬を 押す → 作戦会議が 開く（{"字を 打つ と 列は 消える " + str(k1["h"]) if typed else "字の 欄は 出て いない"}）→ 閉じる → もどる（{k2["h"]}・{k2["act"]}）')
        check(pg.evaluate("() => TengelFab.hidden()") is False, 'TengelFab.hidden()：いまは 消さない（false）')
        shot(pg, 'v240_4_back')
        check(not errs, f'ページの エラー なし {errs[:3]}')
        b.close()
finally:
    srv.terminate(); shutil.rmtree(SRV, ignore_errors=True)
print('合計', len(fails), 'NG' if fails else 'OK')
sys.exit(1 if fails else 0)
