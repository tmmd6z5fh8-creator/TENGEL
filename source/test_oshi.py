# 作戦会議の「推し馬」（第4.165版）の テスト
#   まさちゃん 2026/11/13 11:46「1.作戦会議の中に、推し馬、の欄を作成して、推し馬を25頭まで登録できるようにして！できること ・名前 ・親(2頭)、おじいちゃん(4頭)、ひいおじいちゃん(8頭) ・備考欄」
#   11:59「推し馬は、一頭ごとの欄に、この推し馬を消す、をつけて！」
#   ・レースの ボードの 下に「推し馬」の ボード・25頭まで・1頭ごとの 札（名前・父と 母・血統の 表・備考・「直す」「この推し馬を消す」）・登録／直す の 入力・2回 押して 消す
#   ・日が かわっても 消えない（レースは 消える）・判定タブの 作戦会議からも 同じ・置き場は TCOshi（tc_launch.js）
#   python3 test_oshi.py   （画面は 絵が なくても ためせる：作戦会議は 字と CSS だけ。バックアップは test_native.py）
import json, os, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv_tc'); PORT = 8798; APP = f'http://localhost:{PORT}/APP/'
SHOT = os.environ.get('SHOT')          # 画面を 写す フォルダ（見る 用）
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'APP')], check=True, stdout=subprocess.DEVNULL, env=dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, TARGET='app'))
from assets_dir import adir
TCA = adir('tc_assets'); HAVE = os.path.isdir(TCA) and len(os.listdir(TCA)) > 100
pth = os.path.join(SRV, 'APP', 'index.html'); html = open(pth, encoding='utf8').read()
open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
if HAVE:
    for f in ('tc_icon_plan.webp', 'tc_icon_tc.webp'): shutil.copy(os.path.join(TCA, f), os.path.join(SRV, 'APP', f))
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c: fails.append(label)


FAKE = open(os.path.join(W, 'test_tc.py'), encoding='utf8').read().split('FAKE = """')[1].split('"""')[0]      # アプリの 窓口の にせもの（test_tc.py と 同じ）
PED_LB = ['父', '母', '父の父', '父の母', '母の父', '母の母', '父の父の父', '父の父の母', '父の母の父', '父の母の母', '母の父の父', '母の父の母', '母の母の父', '母の母の母']


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


def open_plan(pg):                    # 判定タブの「作戦会議」の 札から 開く（トレーニングセンターは 開かない：絵が なくても ためせる）
    pg.locator('#planBtn').click()
    pg.wait_for_function("() => window.TCPlan && TCPlan.isOpen()", timeout=60000); pg.wait_for_timeout(400)


BOARD = """() => { const r = document.querySelector('#tcPlan'), ob = r.querySelector('.oboard'); if (!ob) return null;
  return { title: ob.querySelector('.bdt').textContent, sub: ob.querySelector('.bsub').textContent, empty: !!ob.querySelector('.empty'), cards: [...ob.querySelectorAll('.oc')].map(c => ({ id: c.dataset.oid, name: c.querySelector('.onm').textContent, sum: (c.querySelector('.osum') || {}).textContent || '',
      tog: c.querySelector('.otg').textContent, open: c.querySelector('.oh').getAttribute('aria-expanded'), ped: !!c.querySelector('.ped'), memo: c.querySelector('textarea.mm').value, btns: [...c.querySelectorAll('.ra .sb')].map(b => b.textContent) })),
    add: ob.querySelector('.oadd').textContent, addOff: ob.querySelector('.oadd').disabled, jump: [...r.querySelectorAll('.jump button')].map(b => b.textContent), order: [...r.querySelectorAll('.pb > *')].map(e => e.className) }; }"""
LS = "() => JSON.parse(localStorage.getItem('tengel.oshi') || 'null')"
try:
    print('■ 中身')
    tb = open(os.path.join(SRV, 'APP', 'tc_bundle.js'), encoding='utf8').read(); si = open(os.path.join(SRV, 'APP', 'index.html'), encoding='utf8').read()
    check('window.TCOshi' in si and "'tengel.oshi'" in si and 'この推し馬を消す' in tb and '推し馬を登録' in tb and 'ひいおじいちゃん（8頭）' in tb and 'おじいちゃん（4頭）' in tb and '親（2頭）' in tb,
          'index.html に 推し馬の 置き場（TCOshi・tengel.oshi）・tc_bundle.js の 作戦会議に 推し馬（登録・親 2頭・おじいちゃん 4頭・ひいおじいちゃん 8頭・「この推し馬を消す」）')
    src = open(os.path.join(W, 'tc', 'tc_plan.js'), encoding='utf8').read().split('const TCPlan')[1]
    code = '\n'.join(l.split('//')[0] for l in src.split('\n'))      # 説明の 文（// の あと）は のぞく
    check('confirm(' not in code and 'alert(' not in code, '作戦会議は confirm()・alert() の 窓を 使わない（アプリの 中では 出ない：消す ときは 2回 押す）')
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo')
        ctx.add_init_script(FAKE)
        pg = ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        dialogs = []; pg.on('dialog', lambda d: (dialogs.append(d.type), d.dismiss()))
        pg.goto(APP); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(600)

        print('■ 置き場（TCOshi）')
        o = pg.evaluate("""() => { const O = TCOshi, out = {}; out.k = [O.MAX, O.PED, O.NAME_MAX, O.MEMO_MAX, typeof O.load, typeof O.save, typeof O.merge];
          out.empty = O.load();
          out.norm = O.norm({ id: 'a 1!', name: '  なまえ\\n二行目  ', ped: ['ち ち', 'x'.repeat(50), 3], memo: 'め\\r\\nも\\u0001' + 'y'.repeat(400), extra: 1 });
          out.bad = [O.norm(null), O.norm({ id: 'a', name: '   ' }), O.norm({ id: '', name: 'n' }), O.norm('x')];
          out.saved = O.save([{ id: 'x1', name: 'A' }, { id: 'x1', name: 'かぶり' }, { id: 'x2', name: '' }, { id: 'x3', name: 'C', ped: ['p'], memo: 'm' }]).map(q => q.id + ':' + q.name);
          out.ls = JSON.parse(localStorage.getItem('tengel.oshi'));
          out.m1 = O.merge([{ id: 'x3', name: 'べつの 名前' }, { id: 'x4', name: 'D' }]); out.after = O.load().map(q => q.id + ':' + q.name);
          const many = []; for (let i = 0; i < 40; i++) many.push({ id: 'm' + i, name: 'N' + i }); out.m2 = O.merge(many); out.n = O.load().length; out.m3 = O.merge(many);
          const cut = O.str('あ'.repeat(29) + '\\uD83D\\uDC34', 30); out.cut = [cut.length, /[\\uD800-\\uDBFF]$/.test(cut)];
          localStorage.setItem('tengel.oshi', '{こわれた'); out.broken = O.load(); localStorage.setItem('tengel.oshi', JSON.stringify({ v: 1, list: 'x' })); out.broken2 = O.load();
          localStorage.removeItem('tengel.oshi'); return out; }""")
        check(o['k'] == [25, 14, 30, 300, 'function', 'function', 'function'] and o['empty'] == [], f'TCOshi：25頭まで・血統 14頭・名前 30字・備考 300字（はじめは 0頭）{o["k"][:4]}')
        n = o['norm']
        check(n['id'] == 'a1' and n['name'] == 'なまえ 二行目' and n['ped'][:3] == ['ち ち', 'x' * 30, '3'] and len(n['ped']) == 14 and all(x == '' for x in n['ped'][3:]) and n['memo'].startswith('め\nも') and len(n['memo']) == 300 and 'extra' not in n and o['bad'] == [None] * 4,
              f'そろえる：名前は 1行・30字まで／血統は 14こ（足りない ぶんは 空）／備考は 改行を のこして 300字まで・見えない 字は 消す／名前か 番号が ない ものは すてる')
        check(o['saved'] == ['x1:A', 'x3:C'] and o['ls']['v'] == 1 and len(o['ls']['list']) == 2 and o['m1'] == 1 and o['after'] == ['x1:A', 'x3:C', 'x4:D'] and o['m2'] == 22 and o['n'] == 25 and o['m3'] == 0,
              f'保存：同じ 番号は 1つ・名前の ない ものは 入れない／もどす（merge）：もう いる 馬は そのまま・いない 馬を 足す（{o["m1"]}頭）・25頭で 止まる（40頭 → ＋{o["m2"]}＝25頭）')
        check(o['cut'] == [29, False] and o['broken'] == [] and o['broken2'] == [], '絵文字の 途中では 切らない・こわれた データは 0頭として 読む（止まらない）')

        print('■ 作戦会議の「推し馬」の ボード')
        open_plan(pg); bd = pg.evaluate(BOARD); shot(pg, 'oshi_empty')
        check(bd is not None and bd['title'] == '推し馬' and '0頭' in bd['sub'] and '25頭まで' in bd['sub'] and bd['empty'] and bd['cards'] == [] and bd['add'] == '＋ 推し馬を登録' and not bd['addOff'],
              f'レースの ボードの 下に「推し馬」の ボード（0頭・25頭まで 登録できるよ・「＋ 推し馬を登録」）')
        check(bd['order'] == ['jump', 'nt', 'board', 'board oboard'] and len(bd['jump']) == 2 and '推し馬 0/25' in bd['jump'][1], f'ならび：上から 行き先の 札（お気に入りレース／推し馬 0/25）・通知・お気に入りレース一覧・推し馬 {bd["order"]}')
        # 登録の 入力
        pg.locator('#tcPlan [data-p=oadd]').click(); pg.wait_for_timeout(250); shot(pg, 'oshi_form')
        fm = pg.evaluate("""() => { const r = document.querySelector('#tcPlan .ofm'), pb = document.querySelector('#tcPlan .pb'); return { h3: r.querySelector('h3').textContent, h4: [...r.querySelectorAll('h4')].map(e => e.textContent), labels: [...r.querySelectorAll('label')].map(e => e.textContent),
          inputs: [...r.querySelectorAll('input')].map(i => [i.dataset.o, i.maxLength, parseFloat(getComputedStyle(i).fontSize), getComputedStyle(i).userSelect || getComputedStyle(i).webkitUserSelect]), memo: [r.querySelector('textarea').dataset.o, r.querySelector('textarea').maxLength],
          btns: [...r.querySelectorAll('.fa button')].map(b => b.textContent), wide: pb.scrollWidth - pb.clientWidth, over: [...r.querySelectorAll('input, textarea')].every(i => i.getBoundingClientRect().right <= r.getBoundingClientRect().right + 0.5) }; }""")
        check(fm['h3'] == '推し馬を登録' and fm['h4'] == ['親（2頭）', 'おじいちゃん（4頭）', 'ひいおじいちゃん（8頭）'] and fm['labels'] == ['名前'] + PED_LB + ['備考'] and [i[0] for i in fm['inputs']] == ['name'] + [f'p{i}' for i in range(14)] and fm['memo'] == ['memo', 300] and fm['btns'] == ['やめる', '保存'],
              f'入力：名前／親（2頭）父・母／おじいちゃん（4頭）父の父・父の母・母の父・母の母／ひいおじいちゃん（8頭）父の父の父 … 母の母の母／備考／「やめる」「保存」')
        check(all(i[1] == 30 and i[2] >= 16 and i[3] == 'text' for i in fm['inputs']) and fm['wide'] <= 0 and fm['over'], f'入力の 欄：30字まで・字は 16px（押しても 画面が 拡大 しない）・字を 書ける（選べる）・右へ はみ出さない')
        pg.locator('#tcPlan [data-p=osave]').click(); pg.wait_for_timeout(200)
        m0 = pg.evaluate("() => [document.querySelector('#tcPlan .ofm .om').textContent, !!document.querySelector('#tcPlan .ofm'), localStorage.getItem('tengel.oshi')]")
        check(m0[0] == '名前を 入れてね' and m0[1] and m0[2] is None, f'名前が 空の まま「保存」→「名前を 入れてね」（入らない）')
        vals = {'name': 'テストホース', 'p0': 'チチウマ', 'p1': 'ハハウマ', 'p2': 'チチノチチ', 'p3': 'チチノハハ', 'p4': 'ハハノチチ', 'p5': 'ハハノハハ', 'p6': 'ヒイジイイチ', 'p13': 'ヒイバアハチ'}
        for k, v in vals.items(): pg.locator(f'#tcPlan [data-o={k}]').fill(v)
        pg.locator('#tcPlan [data-o=memo]').fill('ダートの 短い 距離が 得意\n雨の 日に 強い')
        pg.locator('#tcPlan [data-p=osave]').click(); pg.wait_for_timeout(300); bd = pg.evaluate(BOARD); ls = pg.evaluate(LS); shot(pg, 'oshi_saved')
        c = bd['cards'][0] if bd['cards'] else {}
        check(len(bd['cards']) == 1 and c['name'] == '🐴 テストホース' and c['sum'] == '父：チチウマ　母：ハハウマ' and c['tog'] == '血統を見る ▼' and c['open'] == 'false' and not c['ped'] and c['memo'] == 'ダートの 短い 距離が 得意\n雨の 日に 強い'
              and c['btns'] == ['直す', 'この推し馬を消す'] and '1頭' in bd['sub'] and '推し馬 1/25' in bd['jump'][1] and not bd['empty'],
              f'「保存」→ 札が 1まい：名前・父と 母・備考（そのまま 書ける 欄）・「直す」「この推し馬を消す」・数は 1頭（上の 札も 1/25）{c.get("btns")}')
        check(ls['v'] == 1 and len(ls['list']) == 1 and ls['list'][0]['name'] == 'テストホース' and ls['list'][0]['ped'] == ['チチウマ', 'ハハウマ', 'チチノチチ', 'チチノハハ', 'ハハノチチ', 'ハハノハハ', 'ヒイジイイチ', '', '', '', '', '', '', 'ヒイバアハチ'] and ls['list'][0]['memo'].startswith('ダート') and ls['list'][0]['id'] == c['id'] and ls['list'][0]['at'],
              f'端末に 保存（tengel.oshi：名前・血統 14こ・備考・登録した 時）')
        # 血統の 表
        pg.locator('#tcPlan [data-p=otog]').click(); pg.wait_for_timeout(250); shot(pg, 'oshi_ped')
        pd = pg.evaluate("""() => { const c = document.querySelector('#tcPlan .oc'), R = e => e.getBoundingClientRect(), cells = [...c.querySelectorAll('.pc')].map(e => ({ i: +e.dataset.i, lb: e.querySelector('small').textContent, v: e.querySelector('b').textContent, f: e.classList.contains('f'), e: e.classList.contains('e'), x: Math.round(R(e).left), y: Math.round(R(e).top), h: Math.round(R(e).height), r: R(e).right }));
          return { head: [...c.querySelectorAll('.pedh span')].map(e => e.textContent), cells, tog: c.querySelector('.otg').textContent, open: c.querySelector('.oh').getAttribute('aria-expanded'), sum: !!c.querySelector('.osum'), right: R(c).right, wide: document.querySelector('#tcPlan .pb').scrollWidth - document.querySelector('#tcPlan .pb').clientWidth }; }""")
        cs = sorted(pd['cells'], key=lambda q: q['i']); xs = sorted({q['x'] for q in cs})
        check(pd['head'] == ['親', 'おじいちゃん', 'ひいおじいちゃん'] and [q['lb'] for q in cs] == PED_LB and [q['v'] for q in cs] == ['チチウマ', 'ハハウマ', 'チチノチチ', 'チチノハハ', 'ハハノチチ', 'ハハノハハ', 'ヒイジイイチ'] + ['—'] * 6 + ['ヒイバアハチ']
              and [q['e'] for q in cs] == [False] * 7 + [True] * 6 + [False] and [q['f'] for q in cs] == [i % 2 == 1 for i in range(14)] and pd['tog'] == 'とじる ▲' and pd['open'] == 'true' and not pd['sum'],
              f'「血統を見る」→ 表：左から 親・おじいちゃん・ひいおじいちゃん（14ます：入れて いない ますは「—」・父は 青・母は 桃）')
        check(len(xs) == 3 and [q['x'] for q in cs] == [xs[0]] * 2 + [xs[1]] * 4 + [xs[2]] * 8 and cs[0]['y'] == cs[2]['y'] == cs[6]['y'] and cs[1]['y'] == cs[4]['y'] == cs[10]['y'] and cs[0]['h'] > cs[2]['h'] > cs[6]['h']
              and cs[3]['y'] == cs[8]['y'] and cs[5]['y'] == cs[12]['y'] and all(q['r'] <= pd['right'] + 0.5 for q in cs) and pd['wide'] <= 0,
              f'表の 形：3れつ（親 2ます・おじいちゃん 4ます・ひいおじいちゃん 8ます）・父の ますの 右に その 父と 母が ならぶ・札から はみ出さない')
        pg.locator('#tcPlan [data-p=otog]').click(); pg.wait_for_timeout(200)
        check(pg.evaluate("() => [!!document.querySelector('#tcPlan .ped'), document.querySelector('#tcPlan .otg').textContent]") == [False, '血統を見る ▼'], 'もう一度 押すと 表を とじる')
        # 備考：札の 中で そのまま 書く（書いた そばから 保存）
        mm = pg.locator('#tcPlan .oc textarea.mm'); mm.fill('かきなおした 備考'); pg.wait_for_timeout(200)
        ls2 = pg.evaluate(LS); st2 = pg.evaluate("() => [document.activeElement && document.activeElement.dataset.p, document.querySelectorAll('#tcPlan .oc').length]")
        check(ls2['list'][0]['memo'] == 'かきなおした 備考' and st2 == ['omemo', 1], f'備考の 欄に 書く → 書いた そばから 保存（欄は 消えない・書きつづけられる）')
        mm.fill('x' * 400); pg.wait_for_timeout(150)
        check(len(pg.evaluate(LS)['list'][0]['memo']) == 300, '備考は 300字まで')
        mm.fill('ダートが 得意'); pg.wait_for_timeout(150)
        # 直す
        pg.locator('#tcPlan [data-p=oedit]').click(); pg.wait_for_timeout(250)
        ed = pg.evaluate("() => { const r = document.querySelector('#tcPlan .ofm'); return [r.querySelector('h3').textContent, r.querySelector('[data-o=name]').value, r.querySelector('[data-o=p0]').value, r.querySelector('[data-o=p13]').value, r.querySelector('[data-o=memo]').value]; }")
        pg.locator('#tcPlan [data-o=name]').fill('テストホース二世'); pg.locator('#tcPlan [data-o=p7]').fill('ヒイバアニ'); pg.locator('#tcPlan [data-p=ocancel]').click(); pg.wait_for_timeout(200)
        keep = pg.evaluate(LS)['list'][0]
        pg.locator('#tcPlan [data-p=oedit]').click(); pg.wait_for_timeout(200)
        pg.locator('#tcPlan [data-o=name]').fill('テストホース二世'); pg.locator('#tcPlan [data-o=p7]').fill('ヒイバアニ'); pg.locator('#tcPlan [data-p=osave]').click(); pg.wait_for_timeout(300)
        ls3 = pg.evaluate(LS)['list']; bd = pg.evaluate(BOARD)
        check(ed == ['推し馬を直す', 'テストホース', 'チチウマ', 'ヒイバアハチ', 'ダートが 得意'] and keep['name'] == 'テストホース' and keep['ped'][7] == ''
              and len(ls3) == 1 and ls3[0]['name'] == 'テストホース二世' and ls3[0]['ped'][7] == 'ヒイバアニ' and ls3[0]['ped'][0] == 'チチウマ' and ls3[0]['id'] == c['id'] and ls3[0]['at'] == ls['list'][0]['at'] and bd['cards'][0]['name'] == '🐴 テストホース二世',
              f'「直す」→ いまの 中身が 入った 入力 →「やめる」は かえない・「保存」で かわる（同じ 馬の まま：番号と 登録した 時は そのまま）')

        print('■ 「この推し馬を消す」（2回 押して 消す）')
        pg.evaluate("""() => { const l = TCOshi.load(); l.push({ id: 'k2', name: 'のこる 馬', ped: ['ちち'], memo: '' }); TCOshi.save(l); }""")
        pg.locator('#tcPlan [data-p=close]').click(); pg.wait_for_timeout(200); open_plan(pg)
        dl = pg.locator(f'#tcPlan .oc[data-oid="{c["id"]}"] [data-p=odel]')
        dl.click(); pg.wait_for_timeout(200)
        d1 = pg.evaluate("(id) => { const b = document.querySelector(`#tcPlan .oc[data-oid=\"${id}\"] [data-p=odel]`); return [b.textContent, b.classList.contains('ask'), TCOshi.load().length, [...document.querySelectorAll('#tcPlan [data-p=odel]')].map(x => x.textContent)]; }", c['id'])
        shot(pg, 'oshi_delask')
        pg.locator('#tcPlan .oboard .bdt').click(); pg.wait_for_timeout(200)
        d2 = pg.evaluate("(id) => { const b = document.querySelector(`#tcPlan .oc[data-oid=\"${id}\"] [data-p=odel]`); return [b.textContent, b.classList.contains('ask'), TCOshi.load().length]; }", c['id'])
        check(d1 == ['ほんとに 消す？', True, 2, ['ほんとに 消す？', 'この推し馬を消す']] and d2 == ['この推し馬を消す', False, 2], f'「この推し馬を消す」を 1回 押す →「ほんとに 消す？」（まだ 消えない・ほかの 馬の ボタンは そのまま）→ ほかの 所を 押すと もどる')
        dl.click(); pg.wait_for_timeout(150)
        pg.locator('#tcPlan .oc[data-oid="k2"] textarea.mm').click(); pg.wait_for_timeout(150)
        d3 = pg.evaluate("(id) => { const b = document.querySelector(`#tcPlan .oc[data-oid=\"${id}\"] [data-p=odel]`); return [b.textContent, b.classList.contains('ask'), TCOshi.load().length, document.activeElement.dataset.p]; }", c['id'])
        check(d3 == ['この推し馬を消す', False, 2, 'omemo'], '「ほんとに 消す？」の あと 備考の 欄を 押す → もどる（欄は 消えない＝書ける）')
        dl.click(); pg.wait_for_timeout(150); dl.click(); pg.wait_for_timeout(250)
        bd = pg.evaluate(BOARD); ls4 = pg.evaluate(LS)['list']
        check([q['name'] for q in bd['cards']] == ['🐴 のこる 馬'] and [q['id'] for q in ls4] == ['k2'] and '1頭' in bd['sub'], f'もう一度 押す → その 馬 だけ 消える（ほかの 馬は のこる）・端末の 保存からも 消える')
        check(not dialogs, f'confirm()・alert() の 窓は 出て いない {dialogs}')

        print('■ 25頭まで')
        pg.evaluate("""() => { const l = []; for (let i = 1; i <= 24; i++) l.push({ id: 'h' + i, name: '推し馬' + i, ped: ['父' + i, '母' + i], memo: '' }); TCOshi.save(l); }""")
        pg.locator('#tcPlan [data-p=close]').click(); pg.wait_for_timeout(200); open_plan(pg); bd = pg.evaluate(BOARD)
        check(len(bd['cards']) == 24 and '24頭' in bd['sub'] and not bd['addOff'] and '推し馬 24/25' in bd['jump'][1], '24頭：まだ 登録できる')
        pg.locator('#tcPlan [data-p=jo]').click(); pg.wait_for_timeout(200)
        jo = pg.evaluate("() => { const pb = document.querySelector('#tcPlan .pb'), ob = document.querySelector('#tcPlan .oboard'); return [pb.scrollTop > 100, Math.abs(ob.getBoundingClientRect().top - pb.getBoundingClientRect().top) < 30]; }")
        pg.locator('#tcPlan [data-p=jr]').click(); pg.wait_for_timeout(150); jr = pg.evaluate("() => document.querySelector('#tcPlan .pb').scrollTop")
        check(jo == [True, True] and jr == 0, '上の 札「推し馬」→ 推し馬の ボードへ・「お気に入りレース」→ いちばん 上へ')
        pg.locator('#tcPlan [data-p=oadd]').click(); pg.wait_for_timeout(200); pg.locator('#tcPlan [data-o=name]').fill('25頭目'); pg.locator('#tcPlan [data-p=osave]').click(); pg.wait_for_timeout(300)
        bd = pg.evaluate(BOARD); shot(pg, 'oshi_full')
        vis = pg.evaluate("() => { const pb = document.querySelector('#tcPlan .pb').getBoundingClientRect(), c = [...document.querySelectorAll('#tcPlan .oc')].pop().getBoundingClientRect(); return c.top >= pb.top - 1 && c.top < pb.bottom; }")
        check(len(bd['cards']) == 25 and bd['cards'][-1]['name'] == '🐴 25頭目' and bd['addOff'] and '25頭まで' in bd['add'] and 'いっぱい' in bd['add'] and '推し馬 25/25' in bd['jump'][1] and vis,
              f'25頭目を 登録 → 25頭・「＋ 推し馬を登録」は 押せない（「{bd["add"]}」）・登録した 馬の 札が 見える 所へ 動く')
        r26 = pg.evaluate("() => { const l = TCOshi.load(); l.push({ id: 'h26', name: '26頭目' }); return [TCOshi.save(l).length, TCOshi.load().length]; }")
        check(r26 == [25, 25], '置き場も 25頭まで（26頭目は 入らない）')

        print('■ 日が かわっても 消えない・開き直しても のこる')
        pg.locator('#tcPlan [data-p=close]').click(); pg.wait_for_timeout(200)
        pg.evaluate("""() => { const d = new Date(), pad = n => String(n).padStart(2, '0'), day = d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
          localStorage.setItem('tengel.plan', JSON.stringify({ v: 1, on: false, races: [{ id: 'r1', date: day, time: '23:59', name: 'きょうの レース', n: '', dist: '', memo: '', notify: [] }] })); }""")
        open_plan(pg); r0 = pg.evaluate("() => [document.querySelectorAll('#tcPlan .rc').length, document.querySelectorAll('#tcPlan .oc').length]")
        pg.locator('#tcPlan [data-p=close]').click(); pg.wait_for_timeout(200)
        pg.evaluate("() => { const D = Date, OFF = 2 * 86400000; class FD extends D { constructor(...a) { if (a.length) super(...a); else super(D.now() + OFF); } static now() { return D.now() + OFF; } } FD.UTC = D.UTC; FD.parse = D.parse; window.Date = FD; }")
        open_plan(pg); r1 = pg.evaluate("() => [document.querySelectorAll('#tcPlan .rc').length, document.querySelectorAll('#tcPlan .oc').length, TCOshi.load().length]")
        check(r0 == [1, 25] and r1 == [0, 25, 25], f'2日 たつと 予約した レースは 消える（{r0[0]} → {r1[0]}）・推し馬は のこる（{r1[1]}頭）')
        pg.locator('#tcPlan [data-p=close]').click(); pg.wait_for_timeout(200)
        pg.reload(); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(600); open_plan(pg)
        r2 = pg.evaluate("() => [document.querySelectorAll('#tcPlan .oc').length, document.querySelector('#tcPlan .oc .onm').textContent]")
        check(r2 == [25, '🐴 推し馬1'], f'アプリを 開き直しても のこる（{r2[0]}頭）')
        pg.locator('#tcPlan [data-p=close]').click(); pg.wait_for_timeout(200)

        # 第4.165版（まさちゃん 2026/11/13 12:47「推し馬はすぐに確認できるように、トレーニングセンターと思い出フィギュアのアイコンのところの1番上に配置して！
        #   推し馬のアイコンをタップしたら、推し馬の欄に飛ぶように設定して！」）：右下の 丸い ボタンの 列（#fabCol）の 1番 上に 推し馬 → 押すと 作戦会議が 開いて「推し馬」の 欄が 上に 出る
        print('■ 右下の 列の 1番 上：推し馬の アイコン')
        FABS = """() => { const R = e => { const r = e.getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom]; }, ks = [...document.querySelectorAll('#fabCol > button')].sort((a, b) => getComputedStyle(a).order - getComputedStyle(b).order);
          const o = document.querySelector('#oshiFab'), im = o && o.querySelector('.fabi img'), ft = o && o.querySelector('.fabt'), ir = o ? o.querySelector('.fabi').getBoundingClientRect() : null;
          return { ids: ks.map(b => b.id), rects: ks.map(R), name: o && o.querySelector('.fabl').textContent, aria: o && o.getAttribute('aria-label'), img: im ? [im.getAttribute('src'), im.naturalWidth, im.naturalHeight] : null, fb: ft ? ft.textContent : null,
            tab: document.querySelector('.tabbar').getBoundingClientRect().top, iw: ir ? [ir.width, ir.height] : null, vis: !!o && getComputedStyle(document.querySelector('#fabCol')).display !== 'none' }; }"""
        JUMP = """() => { const pb = document.querySelector('#tcPlan .pb'), ob = document.querySelector('#tcPlan .oboard'), sp = pb.querySelector('.osp'); const p = pb.getBoundingClientRect();
          return { open: TCPlan.isOpen(), host: document.querySelector('#tcPlan').parentNode.id, top: ob ? Math.round(ob.getBoundingClientRect().top - p.top) : null, st: Math.round(pb.scrollTop), sp: sp ? Math.round(sp.getBoundingClientRect().height) : 0,
            tc: !!document.querySelector('#tcOv.on'), n: document.querySelectorAll('#tcPlan .oc').length, vis: ob ? ob.getBoundingClientRect().top < p.bottom - 100 : false }; }"""
        if HAVE:
            for f in os.listdir(TCA):
                if not os.path.exists(os.path.join(SRV, 'APP', f)): shutil.copy(os.path.join(TCA, f), os.path.join(SRV, 'APP', f))
            pg.reload(); pg.wait_for_timeout(1500); gate(pg); pg.wait_for_timeout(700)
        fb = pg.evaluate(FABS); rc = fb['rects']
        check(fb['ids'][:2] == ['oshiFab', 'tcFab'] and (len(fb['ids']) < 3 or fb['ids'][2] == 'figFab') and all(rc[i][3] <= rc[i + 1][1] + 1 for i in range(len(rc) - 1)) and rc[-1][3] <= fb['tab'] - 4 and rc[0][2] <= 390
              and fb['name'] == '推し馬' and '推し馬' in (fb['aria'] or '') and fb['iw'] and abs(fb['iw'][0] - 66) < 1 and abs(fb['iw'][1] - 66) < 1 and fb['vis'],
              f'列の ならび：上から 推し馬 → トレーニングセンター → 思い出フィギュア（{fb["ids"]}）・重ならない・下の タブの 上・絵は 66px・名前「推し馬」')
        if HAVE:
            check(fb['img'] == ['tc_icon_oshi.webp', 240, 240] and fb['fb'] is None, f'絵：まさちゃんの 推し馬の アイコン（tc_icon_oshi.webp・240×240：ほかの 2つと 同じ 作り方）{fb["img"]}')
            from PIL import Image as _Im
            _a, _b = _Im.open(os.path.join(TCA, 'tc_icon_oshi.webp')), _Im.open(os.path.join(TCA, 'tc_icon_tc.webp'))
            ba, bb = _a.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox(), _b.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox()
            check(_a.size == _b.size == (240, 240) and max(ba[2] - ba[0], ba[3] - ba[1]) in (231, 232, 233) and abs(max(ba[2] - ba[0], ba[3] - ba[1]) - max(bb[2] - bb[0], bb[3] - bb[1])) <= 2, f'丸の 大きさは トレーニングセンターの アイコンと 同じ（{ba}・{bb}）')
        else:
            check(fb['fb'] == '推し馬' and fb['img'] is None, f'絵が ない とき（CI）：字の 丸「推し馬」{fb["fb"]}')
        lst2 = subprocess.run(['git', 'ls-files'], cwd=os.path.dirname(W), capture_output=True, text=True).stdout.split('\n')
        check(not any(f.endswith(('tc_icon_oshi.webp', 'src_oshi_icon.png')) for f in lst2) and os.path.exists(os.path.join(W, 'kisekae', 'tc', 'oshi_asset.py')), 'まさちゃんの アイコンの 絵は リポジトリに 入って いない・絵を 置く 道具（kisekae/tc/oshi_asset.py）は ある')
        # 押す（まだ 作戦会議を 読んで いない：開き直した すぐ あと）→ 作戦会議が 開いて 推し馬の 欄が 上（25頭：中身が 長い）
        pg.locator('#oshiFab .fabi').click(); pg.wait_for_function("() => window.TCPlan && TCPlan.isOpen()", timeout=30000); pg.wait_for_timeout(500)
        j1 = pg.evaluate(JUMP); shot(pg, 'oshi_fab_open')
        check(j1['open'] and j1['host'] == 'planHost' and not j1['tc'] and j1['n'] == 25 and j1['top'] is not None and 0 <= j1['top'] <= 12 and j1['st'] > 200,
              f'推し馬の アイコンを 押す → 作戦会議が 開いて「推し馬」の 欄が いちばん 上（上から {j1["top"]}px・トレーニングセンターは 開かない）')
        pg.locator('#tcPlan [data-p=jr]').click(); pg.wait_for_timeout(200); j2 = pg.evaluate(JUMP)
        pg.locator('#tcPlan [data-p=jo]').click(); pg.wait_for_timeout(200); j3 = pg.evaluate(JUMP)
        check(j2['st'] == 0 and j2['sp'] == 0 and 0 <= j3['top'] <= 12, f'上の「📋 お気に入りレース」で いちばん 上へ・「🐴 推し馬」で また 推し馬の 欄へ（{j2["st"]} → 上から {j3["top"]}px）')
        pg.locator('#tcPlan [data-p=close]').click(); pg.wait_for_timeout(200)
        open_plan(pg); j4 = pg.evaluate(JUMP)
        check(j4['open'] and j4['st'] == 0 and j4['sp'] == 0, f'判定タブの「作戦会議」の 札から 開いた ときは いつも 上から（推し馬の 欄へ 進めた 所は のこらない：{j4["st"]}）')
        pg.locator('#tcPlan [data-p=close]').click(); pg.wait_for_timeout(200)
        # 推し馬が 少ない とき（中身が 1画面に おさまる）でも 推し馬の 欄が 上まで 上がる（下に 余白を 足す）
        pg.evaluate("() => TCOshi.save(TCOshi.load().slice(0, 1))")
        pg.locator('#oshiFab .fabi').click(); pg.wait_for_timeout(700); j5 = pg.evaluate(JUMP)
        check(j5['open'] and j5['n'] == 1 and 0 <= j5['top'] <= 12 and j5['sp'] > 50, f'推し馬が 1頭 だけ（中身が 短い）でも「推し馬」の 欄が いちばん 上（上から {j5["top"]}px・下の 余白 {j5["sp"]}px）')
        pg.locator('#tcPlan .oc [data-p=otog]').first.click(); pg.wait_for_timeout(250); j6 = pg.evaluate(JUMP)
        check(0 <= j6['top'] <= 12, f'血統を ひらいても 推し馬の 欄は 上の まま（上から {j6["top"]}px）')
        pg.locator('#tcPlan [data-p=close]').click(); pg.wait_for_timeout(200)
        # ほかの タブでも 押せる
        pg.evaluate("() => document.querySelectorAll('.tabbar button')[2].click()"); pg.wait_for_timeout(400)
        pg.locator('#oshiFab .fabi').click(); pg.wait_for_timeout(700); j7 = pg.evaluate(JUMP)
        check(j7['open'] and 0 <= j7['top'] <= 12 and pg.evaluate("() => !document.querySelector('#v-judge') || document.querySelector('#v-judge').hidden"), '記録タブでも 押せる（とじると 記録タブの まま）')
        pg.locator('#tcPlan [data-p=close]').click(); pg.wait_for_timeout(200)
        pg.evaluate("() => document.querySelectorAll('.tabbar button')[0].click()"); pg.wait_for_timeout(300)

        # トレーニングセンターの 中の 作戦会議でも 同じ（絵が ある とき）
        if HAVE:
            print('■ トレーニングセンターの 中の 作戦会議')
            pg.locator('#tcFab .fabi').click()
            pg.wait_for_function("() => window.TCApp && document.querySelector('#tcOv.on') && !document.querySelector('#tcOv .tcld')", timeout=120000); pg.wait_for_timeout(1200)
            pg.locator('#tcOv [data-tc="plan"]').click(); pg.wait_for_timeout(600)
            t1 = pg.evaluate("() => { const r = document.querySelector('#tcPlan'); return [r.parentNode.id, document.querySelectorAll('#tcPlan .oc').length, getComputedStyle(r.querySelector('.oc textarea')).userSelect || getComputedStyle(r.querySelector('.oc textarea')).webkitUserSelect]; }")
            shot(pg, 'oshi_in_tc')
            check(t1 == ['tcOv', 1, 'text'], f'トレーニングセンターの「作戦会議」でも 同じ 推し馬（{t1[1]}頭）・備考の 欄は 書ける（トレーニングセンターの 画面は 字を 選べない ように して ある）')
            pg.locator('#tcPlan [data-p=close]').click(); pg.wait_for_timeout(200); pg.locator('#tcOv [data-tc="back"]').click(); pg.wait_for_timeout(400)
        check(not errs, f'エラー なし {errs[:3]}')
        b.close()
finally:
    srv.terminate()
print('NG' if fails else 'OK', len(fails), fails)
sys.exit(1 if fails else 0)
