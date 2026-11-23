# 古い 台帳の リセット（第4.212版）の テスト：old_reset.js・points.js の compact・points_ui.js の TengelWallet.old・app_target.py の V212_INDEX（TengelLocal.delBets）
#   まさちゃん 2026/11/23 10:14「古い台帳は、3年おきにリセットされるようにして！注意書も入れて！そのかわり、思い出レースや思い出フィギュアは残るようによろしく！」
#     答え：消す もの＝「両方」（記録タブの 古い レース・ポイントの 履歴）／消し方＝「いつも直近3年分を残す」
#   10:26「3年経ってなくても、古い台帳をリセットする、ができる項目を追加して … 最後リセットをする前に、本当にリセットする？リセットを一度するともう消した台帳は戻せないよ！を注意書で入れて！」
#   10:30「でも3年に一回は自動リセットするのはつけてね！ やっぱり、選択は古い台帳の2年分、1年分、全て、を選べるようにして！」
#   見る もの：
#   ・設定の カード「古い台帳をリセットする」（バックアップの 下）：数・注意書き・「古い方から2年分／古い方から1年分／全て」・さいごの たしかめ（「本当にリセットする？」「リセットを一度すると、もう消した台帳は戻せないよ！」）
#   ・手で リセット：えらんだ 所 まで の 記録（予約中の レースも）と 履歴 だけ 消える。思い出の レース・思い出フィギュア・ポイントの 残高・解放した もの・数えた レース・マザーデータは 残る
#   ・自動（3年）：消える 30日前から 記録タブの 上で 知らせる → 30日 たったら 消す。知らせた あとに 入れた・直した 記録／戻した 古い 記録は そこから 30日は 消えない。
#     インターネットの 時刻で たしかめて ある とき だけ 動く（電源を 入れ直して つながって いない ときは 消さない）。ポイントの 履歴は 3年より 前を 1行に まとめる
#   ・Web版には 入って いない
#   python3 test_old_reset.py
import json, os, re, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv_old'); PORT = 8813; STORE = f'http://localhost:{PORT}/STORE/'; TESTB = f'http://localhost:{PORT}/TEST/'; WEB = f'http://localhost:{PORT}/TENGEL/'
SHOT = os.environ.get('SHOT')
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'TENGEL')], check=True, stdout=subprocess.DEVNULL, env={k: v for k, v in os.environ.items() if k not in ('TENGEL_TEST', 'TARGET')})
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'STORE')], check=True, stdout=subprocess.DEVNULL, env=dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, TARGET='app'))
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'TEST')], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, TARGET='app', TENGEL_TEST='1'))      # テスト版（自動の リセットを ためす ボタン）
for d in ('STORE', 'TEST'):
    pth = os.path.join(SRV, d, 'index.html'); html = open(pth, encoding='utf8').read()
    assert "window.__NATIVE = location.protocol === 'tengel:';" in html
    open(pth, 'w', encoding='utf8').write(html.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c: fails.append(label)


FAKE = open(os.path.join(W, 'test_tc.py'), encoding='utf8').read().split('FAKE = """')[1].split('"""')[0]      # アプリの 窓口の にせもの（test_tc.py と 同じ：時計は わたさない）
FAKE2 = FAKE.replace("  if (m.name === 'iap')", "  if (m.name === 'clock' && window.__clk) val = window.__clk(P);\n  if (m.name === 'iap')"); assert FAKE2 != FAKE
# にせものの アプリの 時計（test_login.py と 同じ 作り）：本当の 時刻 ＝ 本物の 時計 ＋ st.real・電源を 入れてからの 時間 ＝ st.mb ＋ 本物の 時計 ＋ st.real・インターネットの 時刻（st.net＝つながって いる とき）
CLK2 = """(() => { const R = Date.now.bind(Date), K = '__clkw', st = JSON.parse(sessionStorage.getItem(K) || 'null') || { real: 0, day: 0, boot: 'B1', mb: 5 * 86400000 - R(), net: 1, nets: 0 };
  const put = () => sessionStorage.setItem(K, JSON.stringify(st)); put(); const proc = 'P' + R() + Math.random();
  Date.now = () => R() + st.real + st.day * 86400000;
  window.__clk = P => { const mono = st.mb + R() + st.real, o = { wall: Date.now(), mono: mono, boot: st.boot, proc: proc, dev: 'D1' };
    if (P && P.net) { st.nets++; put(); o.net = st.net ? { ok: true, t: R() + st.real, mono: mono - 20, rt: 40, why: '' } : { ok: false, t: 0, mono: 0, rt: 0, why: 'net' }; } return o; };
  window.__pass = ms => { st.real += ms; put(); }; window.__reboot = off => { st.real += off || 0; st.boot = 'B' + R() + Math.random(); st.mb = 60000 - R() - st.real; put(); };
  window.__netOn = v => { st.net = v ? 1 : 0; put(); }; window.__real = () => R() + st.real; })();"""


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


def tab(pg, t):
    pg.evaluate("(t) => { const b = document.querySelector('.tabbar button[data-tab=' + t + ']'); if (b) b.click(); }", t); pg.wait_for_timeout(450)


# 記録 1件（結果を 入れた レース）。mem＝思い出の レース・kind＝'win5' なら 5連の 記録・state＝予約の 状態
BET = """(o) => ({ id: o.id, date: o.date, venue: 'テスト場', r: o.r || 7, rname: 'テストの レース', n: 14, types: ['馬単'], n1: 5, n2: 2, n3: 1, p1: 3, p2: 1, p3: 2, stake: '600', payout: '0', horses: [],
  snap: { L: 'A', kubun: 'A' }, rsv: { state: o.state || 'done', types: ['馬単'], bets: { '馬単': [[5, 2]] }, at: o.stamp, start: '23:59' }, createdAt: o.stamp, updatedAt: o.stamp,
  ...(o.mem ? { mem: { at: o.stamp, v: 'a' } } : {}), ...(o.kind ? { kind: o.kind } : {}) })"""
# いまの ようす
INFO = """() => { const W = TengelWallet, L = TengelLocal, bets = [...L.mem.bets.values()], c = document.querySelector('#setOld'), t = s => { const e = document.querySelector(s); return e ? e.innerText.replace(/\\s+/g, ' ').trim() : null; };
  return { ids: bets.map(b => b.id).sort(), mem: bets.filter(b => b.mem).map(b => b.id).sort(), total: W.total(), rows: W.old.rows(), first: W.old.first(), carry: W.old.carry(), unl: ['type:複勝', 'toy:cb', 'type:馬連'].map(k => W.unlocked(k)),
    figs: W.fig.items().length, counted: W.countedN(), mother: L.slots.rows(2).length, memList: window.TengelMem ? TengelMem.list().map(x => x.id).sort() : null,
    rec: t('#soRec'), hist: t('#soHist'), firstTxt: t('#soFirst'), auto: t('#soAuto'), note: t('#oldNote'), st: window.TengelOld ? TengelOld.state() : null, pend: window.TengelOld ? TengelOld.pending().sort() : null,
    opts: c ? [...c.querySelectorAll('#soPick .ptitem')].map(e => e.innerText.replace(/\\s+/g, ' ').trim()) : null, dis: c ? [...c.querySelectorAll('#soPick [data-so=pick]')].map(b => b.disabled) : null, toast: t('#toast') }; }"""


try:
    print('■ 中身（ビルド）')
    app = open(os.path.join(SRV, 'STORE', 'index.html'), encoding='utf8').read(); web = open(os.path.join(SRV, 'TENGEL', 'index.html'), encoding='utf8').read()
    src = open(os.path.join(W, 'old_reset.js'), encoding='utf8').read(); code = re.sub(r'//[^\n]*', '', src)
    check('window.TengelOld = {' in app and 'delBets: function (ids)' in app and "kind: 'carry'" in app and 0 < app.find('window.TengelWallet = {') < app.find('window.TengelOld = {') and app.find('window.TengelClock = {') < app.find('window.TengelOld = {'),
          'App Store版の index.html に 古い 台帳の リセット（old_reset.js）・まとめて 消す 口（TengelLocal.delBets）・履歴を まとめる しくみ（carry）が 入って いる（時計の 番人・財布の あと）')
    check('TengelOld' not in web and 'oldreset' not in web and 'delBets' not in web and '古い台帳' not in web and "'carry'" not in web, 'Web版には 入って いない（かわらない）')
    check('confirm(' not in code and 'alert(' not in code and 'prompt(' not in code, '窓は confirm()・alert() を 使わない（アプリの 中では 出ない）')
    check('本当にリセットする？' in src and 'リセットを一度すると、もう消した台帳は戻せないよ！' in src and all(w in src for w in ('古い方から', '年分', "'全て'")) and '[2, 1, \'all\']' in src,
          'まさちゃんの 言葉：「本当にリセットする？」「リセットを一度すると、もう消した台帳は戻せないよ！」・えらぶ ものは 古い方から2年分・古い方から1年分・全て')
    body = set(open(os.path.join(W, 'ios', 'fonts', 'ks', 'chars_body.txt'), encoding='utf8').read())
    strs = ''.join(re.findall(r"'((?:[^'\\]|\\.)*)'", code)); lack = sorted({c for c in strs if ord(c) > 0x2000 and c not in body and not (0x1F000 <= ord(c) <= 0x1FAFF or 0x2600 <= ord(c) <= 0x27BF or ord(c) == 0xFE0F)})
    check(not lack and 'old_reset.js' in open(os.path.join(W, 'kisekae', 'build_fonts.py'), encoding='utf8').read(), f'画面の 言葉は しぼった 字（本文 {len(body)}字）に 入って いる 字 だけ（足りない 字 {lack}）・字を しぼる 道具も old_reset.js を 見る')
    man = re.sub(r'<[^>]+>', '', open(os.path.join(W, 'manual', 'content_app.html'), encoding='utf8').read())
    check('古い台帳のリセット' in man and '3年たったレースの記録は、自動で消えるよ' in man and '思い出のレースは消えないよ' in man and '古い方から2年分・古い方から1年分・全て' in man and 'リセットを一度すると、もう消した台帳は戻せないよ' in man and '30日前から' in man,
          '説明書（記録タブ）に 古い 台帳の リセット（3年で 自動・30日前から お知らせ・思い出は 残る・自分でも：2年分・1年分・全て・戻せない 注意）')
    sys.path.insert(0, os.path.join(W, 'legal')); import build_legal as _bl
    ab = json.dumps(_bl.about('app'), ensure_ascii=False); abw = json.dumps(_bl.about('web'), ensure_ascii=False)
    check('3年' in ab and '古い台帳をリセットする' in ab and '時刻の確認' in ab and '古い台帳' not in abw and '時刻の確認' not in abw, 'このアプリについて（プライバシー）：3年で 自動で 消える こと・時刻の 確認（Apple に 問い合わせる）が 書いて ある（App Store版 だけ）')

    with sync_playwright() as p:
        b = p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
        # ================= 手で リセット（時計の 番人なし＝自動は 動かない）=================
        print('■ 設定の カード・手で リセット')
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo'); ctx.add_init_script(FAKE)
        pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); dialogs = []; pg.on('dialog', lambda d: (dialogs.append(d.type), d.dismiss()))
        pg.goto(STORE); pg.wait_for_timeout(1500); pg.wait_for_function("() => window.TengelWallet && TengelWallet.on && window.TengelOld", timeout=20000); gate(pg); pg.wait_for_timeout(700)
        # 記録 10件（思い出 2件・予約中 1件）・ポイントの 履歴 12行（2023年1月 〜）・思い出フィギュア 1つ・数えた レース 1つ・マザーデータ①に 1走
        seed = pg.evaluate("""async (BET) => {
          const mk = eval(BET), L = TengelLocal, W = TengelWallet, P = TengelPoints, T = s => new Date(s + 'T03:00:00.000Z');
          await L.putBets([['b1', '2023-01-10'], ['b2', '2023-03-03', 1], ['b3', '2023-06-15'], ['b4', '2023-12-28'], ['b5', '2024-01-05'], ['b6', '2024-07-07'], ['b7', '2025-02-02', 1], ['b8', '2025-03-03'], ['b9', '2026-10-10', 0, '', 'reserved'], ['b10', '2026-11-20']]
            .map(([id, date, mem, kind, state]) => mk({ id, date, mem, kind, state, stamp: date + 'T03:00:00.000Z' })));
          let ev = [P.giftEvent(T('2023-01-05'), 5000)]; P.stamp(ev);
          ev = P.spend(ev, 400, '読み込み', 'd', T('2023-01-10'));
          ev.push(P.rowEvent({ id: 'login-2023-02-01', reward: 500, label: 'ログインボーナス（1日目）' }, T('2023-02-01'))); P.stamp(ev);
          ev = P.unlock(ev, 'type:複勝', 500, 'd', T('2023-03-01'));
          ev.push(P.rowEvent({ id: 'tc-a1', reward: 100, label: 'トレーニングセンター' }, T('2023-06-01'))); ev.push(P.rowEvent({ id: 'mission-x1', reward: 500, label: 'テストの ミッション' }, T('2023-08-01'))); P.stamp(ev);
          ev = P.spend(ev, 400, '読み込み', 'd', T('2024-02-02'));
          ev.push(P.rowEvent({ id: 'login-2024-03-03', reward: 500, label: 'ログインボーナス（2日目）' }, T('2024-03-03'))); P.stamp(ev);
          ev = P.unlock(ev, 'toy:cb', 3000, 'd', T('2025-01-15'));
          ev = P.spend(ev, 400, '読み込み', 'd', T('2025-05-05'));
          ev.push(P.rowEvent({ id: 'login-2026-10-10', reward: 500, label: 'ログインボーナス（3日目）' }, T('2026-10-10'))); P.stamp(ev);
          ev = P.spend(ev, 400, '読み込み', 'd', T('2026-11-01'));
          const s = W.snapshot(); s.events = ev; s.counted = { '2023-01-10|テスト場|7': '2023-01-10T03:00:00.000Z' };
          s.figs = { items: [{ id: 'f1', n: 1, name: 'テストの フィギュア', at: '2023-04-04T03:00:00.000Z', cost: 22000 }], slots: ['f1'] };
          await W.restore(s);
          await L.slots.upsert(2, [{ id: 'x1', date: '2023-01-10', venue: 'テスト場', r: 3, baba: '良', dist: 1400, surface: 'ダ', n: 12, tan1: 2.4, s1: 18.5, p1: 1, p2: 2, p3: 3 }]);
          return { n: L.mem.bets.size, total: W.total(), rows: W.old.rows(), sure: TengelClock.sure(), now: TengelClock.now() }; }""", BET)
        pg.wait_for_timeout(400); tab(pg, 'set'); pg.wait_for_timeout(300)
        i0 = pg.evaluate(INFO)
        pos = pg.evaluate("() => { const c = document.querySelector('#setOld'), bk = document.querySelector('#setBackup'), ab = document.querySelector('#setAbout'); return { after: !!bk && bk.nextElementSibling === c, before: !!ab && !!(c.compareDocumentPosition(ab) & Node.DOCUMENT_POSITION_FOLLOWING), h2: c.querySelector('h2').textContent, t: c.innerText.replace(/\\s+/g, ' '), btn: [...c.querySelectorAll('button')].map(x => x.textContent), w: c.getBoundingClientRect().width, sw: document.documentElement.scrollWidth }; }")
        check(seed['n'] == 10 and seed['total'] == 2000 and seed['rows'] == 12 and not seed['sure'], f'用意：記録 10件・ポイント 2,000P・履歴 12行（時計の 番人は 動いて いない＝自動は 動かない）（{seed}）')
        check(pos['after'] and pos['before'] and pos['h2'] == '古い台帳をリセットする' and pos['btn'] == ['古い台帳をリセットする'] and pos['sw'] <= 390
              and '思い出のレース・思い出フィギュア・ポイントの残高・解放したもの・マザーデータは残るよ' in pos['t'] and '⚠️ 3年たった記録と履歴は、自動でリセットされるよ。' in pos['t'] and '消える30日前から、記録タブの上で知らせるよ' in pos['t'],
              f'設定に カード「古い台帳をリセットする」（バックアップの すぐ 下・このアプリについての 前）：残る もの・注意書き（3年で 自動・30日前から 知らせる）・ボタン 1つ・横に はみ出さない')
        check(i0['rec'] == '10件（うち思い出 2件）' and i0['hist'] == '12行' and i0['firstTxt'] == '2023年1月' and i0['auto'] == 'インターネットで時刻を確かめた後に動くよ' and i0['opts'] == [] and i0['note'] is None,
              f'カードの 数：レースの記録 {i0["rec"]}・ポイントの履歴 {i0["hist"]}・いちばん古い月 {i0["firstTxt"]}・自動リセット「{i0["auto"]}」')
        shot(pg, 'old_card')
        pg.locator('#setOld [data-so=open]').click(); pg.wait_for_timeout(300)
        i1 = pg.evaluate(INFO)
        check(i1['opts'] == ['古い方から2年分 2023年1月〜2024年12月・記録 5件・履歴 8行 選ぶ', '古い方から1年分 2023年1月〜2023年12月・記録 3件・履歴 6行 選ぶ', '全て 2023年1月〜今・記録 8件・履歴 12行 選ぶ'] and i1['dis'] == [False, False, False] and i1['ids'] == i0['ids'],
              f'ボタンを 押すと「古い方から2年分・古い方から1年分・全て」（いちばん 古い 月から 数える・消える 数を 出す）：まだ 何も 消えない（{i1["opts"]}）')
        shot(pg, 'old_pick')
        # 1年分 → さいごの たしかめ → 出て すぐの 押しまちがいは 効かない → やめる
        early = pg.evaluate("() => { document.querySelector('#setOld [data-so=pick][data-k=\"1\"]').click(); const o = document.querySelector('#oldOv'); if (!o) return null; o.querySelector('[data-old=go]').click(); return { open: !!document.querySelector('#oldOv') }; }")
        pg.wait_for_timeout(300)
        ov = pg.evaluate("""() => { const o = document.querySelector('#oldOv'); if (!o) return null; const bx = o.querySelector('.oldbox').getBoundingClientRect(), cs = getComputedStyle(o), go = o.querySelector('[data-old=go]'), e = document.elementFromPoint(bx.left + bx.width / 2, bx.top + 10);
          return { t: o.innerText.replace(/\\s+/g, ' ').trim(), h2: o.querySelector('h2').textContent, warn: o.querySelector('.oldwarn').textContent, role: o.getAttribute('role'), modal: o.getAttribute('aria-modal'), z: +cs.zIndex, tabz: +getComputedStyle(document.querySelector('.tabbar')).zIndex,
            inside: bx.left >= 0 && bx.right <= innerWidth && bx.top >= 0 && bx.bottom <= innerHeight, top: !!e && o.contains(e), btn: [...o.querySelectorAll('button')].map(x => x.dataset.old + ':' + x.textContent), goH: go.getBoundingClientRect().height, warnColor: getComputedStyle(o.querySelector('.oldwarn')).color,
            font: getComputedStyle(o.querySelector('.oldbox')).fontFamily.split(',')[0].trim().replace(/"/g, ''), bodyFont: getComputedStyle(document.querySelector('.card')).fontFamily.split(',')[0].trim().replace(/"/g, '') }; }""")
        i2 = pg.evaluate(INFO)
        check(early == {'open': True} and ov is not None and i2['ids'] == i0['ids'] and i2['rows'] == 12, '窓が 出て すぐ（0.6秒 より 前）の「リセットする」は 効かない（押しまちがいで 消さない）')
        check(ov and ov['h2'] == '本当にリセットする？' and ov['warn'] == 'リセットを一度すると、もう消した台帳は戻せないよ！' and '消すもの：古い方から1年分（2023年1月〜2023年12月）' in ov['t'] and 'レースの記録 3件・ポイントの履歴 6行' in ov['t']
              and '思い出のレース・思い出フィギュア・ポイントの残高・解放したもの・マザーデータは残るよ。' in ov['t'] and ov['btn'] == ['go:リセットする', 'no:やめる'],
              f'さいごの たしかめ：「本当にリセットする？」「リセットを一度すると、もう消した台帳は戻せないよ！」・消す もの（1年分・記録 3件・履歴 6行）・残る もの・「リセットする」「やめる」（{ov and ov["t"][:70]}…）')
        check(ov and ov['role'] == 'alertdialog' and ov['modal'] == 'true' and ov['z'] > ov['tabz'] and ov['inside'] and ov['top'] and ov['goH'] >= 40 and ov['font'] == ov['bodyFont'] and not dialogs,
              f'窓：画面の 中に おさまる・下の タブより 上・字は いまの 壁紙の 字（{ov and ov["font"]}）・confirm() は 使わない')
        shot(pg, 'old_confirm')
        pg.locator('#oldOv [data-old=no]').click(); pg.wait_for_timeout(300)
        i3 = pg.evaluate(INFO)
        check(pg.locator('#oldOv').count() == 0 and i3['ids'] == i0['ids'] and i3['rows'] == 12 and i3['total'] == 2000 and len(i3['opts']) == 3, '「やめる」→ 何も 消えない（えらぶ ところに 戻る）')
        # 1年分を リセット
        pg.locator('#setOld [data-so=pick][data-k="1"]').click(); pg.wait_for_timeout(800)
        pg.locator('#oldOv [data-old=go]').click(); pg.wait_for_timeout(900)
        a = pg.evaluate(INFO)
        check(pg.locator('#oldOv').count() == 0 and a['ids'] == ['b10', 'b2', 'b5', 'b6', 'b7', 'b8', 'b9'] and '古い台帳をリセットしたよ（記録 3件・履歴 6行）' in (a['toast'] or ''),
              f'古い方から1年分を リセット：2023年の 記録 3件（b1・b3・b4）が 消える・思い出の レース（2023年3月の b2）は 残る（{a["ids"]}・「{a["toast"]}」）')
        check(a['mem'] == ['b2', 'b7'] and a['memList'] == ['b2', 'b7'] and a['figs'] == 1 and a['counted'] == 1 and a['mother'] == 1 and a['total'] == 2000 and a['unl'] == [True, True, False],
              f'残る もの：思い出の レース 2件・思い出フィギュア 1つ・数えた レース 1つ・マザーデータ①の 1走・ポイント 2,000P・解放した もの（複勝・TENGERカードバトル）（{a["total"]}P・{a["unl"]}）')
        check(a['rows'] == 6 and a['carry'] and a['carry']['cnt'] == 6 and a['rec'] == '7件（うち思い出 2件）' and a['hist'] == '6行' and a['firstTxt'] == '2024年1月' and a['opts'] == [],
              f'ポイントの 履歴は 12行 → 6行（2023年の 6行を 1行に まとめた）・カードの 数も 新しく（{a["rec"]}・{a["hist"]}・いちばん古い月 {a["firstTxt"]}）')
        pg.evaluate("() => { const b = document.querySelector('#setPoints [data-pt=show][data-v=hist]'); if (b) b.click(); }"); pg.wait_for_timeout(400)
        hs = pg.evaluate("() => [...document.querySelectorAll('#setPoints .pthist li')].map(li => li.textContent.replace(/\\s+/g, ' ').trim())")
        check(len(hs) == 7 and hs[-1].startswith('2023/8/1 までの履歴（6行）は、1行にまとめたよ') and not any('複勝' in t or '初回プレゼント' in t for t in hs) and any('TENGERカードバトル' in t for t in hs),
              f'設定の ポイントの 履歴：残った 6行 ＋ いちばん 下に「2023/8/1 までの履歴（6行）は、1行にまとめたよ」（まとめた 行は 出ない・日付は まとめた さいごの 行の 日）（{hs[-1]}）')
        tab(pg, 'rec'); pg.wait_for_timeout(300)
        check(pg.evaluate("() => !document.querySelector('#oldNote')") and not errs, f'記録タブ：自動の 知らせは 出ない（時刻を たしかめて いない）・エラー なし {errs[:2]}')
        # 2年分（いまの いちばん 古い 月 2024年1月 から）→ 全て
        tab(pg, 'set'); pg.locator('#setOld [data-so=open]').click(); pg.wait_for_timeout(300)
        b1 = pg.evaluate(INFO)
        check(b1['opts'] == ['古い方から2年分 2024年1月〜2025年12月・記録 3件・履歴 4行 選ぶ', '古い方から1年分 2024年1月〜2024年12月・記録 2件・履歴 2行 選ぶ', '全て 2024年1月〜今・記録 5件・履歴 6行 選ぶ'],
              f'もう 1回 開く：いまの いちばん 古い 月（2024年1月）から 数え直す（{b1["opts"]}）')
        pg.locator('#setOld [data-so=pick][data-k="2"]').click(); pg.wait_for_timeout(800)
        t2 = pg.evaluate("() => document.querySelector('#oldOv').innerText.replace(/\\s+/g, ' ')")
        pg.locator('#oldOv [data-old=go]').click(); pg.wait_for_timeout(900)
        c = pg.evaluate(INFO)
        check('消すもの：古い方から2年分（2024年1月〜2025年12月）' in t2 and 'レースの記録 3件・ポイントの履歴 4行' in t2 and c['ids'] == ['b10', 'b2', 'b7', 'b9'] and c['rows'] == 2 and c['carry']['cnt'] == 10 and c['total'] == 2000 and c['unl'] == [True, True, False] and c['figs'] == 1,
              f'古い方から2年分：2024〜2025年の 記録 3件・履歴 4行が 消える（思い出の b7 は 残る・解放した おもちゃも そのまま）（{c["ids"]}・履歴 {c["rows"]}行）')
        pg.locator('#setOld [data-so=open]').click(); pg.wait_for_timeout(300)
        pg.locator('#setOld [data-so=pick][data-k="all"]').click(); pg.wait_for_timeout(800)
        t3 = pg.evaluate("() => document.querySelector('#oldOv').innerText.replace(/\\s+/g, ' ')")
        pg.locator('#oldOv [data-old=go]').click(); pg.wait_for_timeout(900)
        d = pg.evaluate(INFO)
        check('消すもの：全て' in t3 and 'レースの記録 2件・ポイントの履歴 2行' in t3 and d['ids'] == ['b2', 'b7'] and d['mem'] == ['b2', 'b7'] and d['rows'] == 0 and d['carry']['cnt'] == 12 and d['total'] == 2000 and d['unl'] == [True, True, False]
              and d['figs'] == 1 and d['counted'] == 1 and d['mother'] == 1 and d['rec'] == '2件（うち思い出 2件）' and d['hist'] == '0行' and d['firstTxt'] == 'まだないよ',
              f'全て：思い出で ない 記録（予約中の レースも）と 履歴が ぜんぶ 消える。思い出の レース 2件・思い出フィギュア・ポイント 2,000P・解放した もの・マザーデータは 残る（{d["ids"]}・{d["total"]}P）')
        pg.locator('#setOld [data-so=open]').click(); pg.wait_for_timeout(300)
        e0 = pg.evaluate(INFO)
        check(all(x.endswith('消すものがないよ') for x in e0['opts']) and e0['dis'] == [True, True, True], f'消す ものが ない ときは えらべない（{e0["opts"]}）')
        pg.locator('#setOld [data-so=close]').click(); pg.wait_for_timeout(200)
        # リセットの あとも ふつうに 使える：読み込み（400P）・開き直しても 同じ
        r1 = pg.evaluate("async () => { const x = await TengelWallet.readCharge({ form: { date: '2026-11-22', venue: 'テスト場', r: 1 }, ocr: {} }); return [x.ok, x.charged, TengelWallet.total(), TengelWallet.old.rows()]; }")
        pg.reload(); pg.wait_for_function("() => window.TengelWallet && TengelWallet.on && window.TengelOld", timeout=20000); pg.wait_for_timeout(900); gate(pg); pg.wait_for_timeout(500); tab(pg, 'set')
        f = pg.evaluate(INFO)
        check(r1 == [True, True, 1600, 1] and f['total'] == 1600 and f['rows'] == 1 and f['ids'] == ['b2', 'b7'] and f['unl'] == [True, True, False] and f['figs'] == 1 and f['carry']['cnt'] == 12 and not errs and not dialogs,
              f'リセットの あとも ふつうに 使える（読み込み 400P → 1,600P・履歴 1行）・開き直しても 同じ・エラー なし {errs[:2]}')
        ctx.close()

        # ================= 自動（3年）=================
        print('■ 自動の リセット（いつも 直近 3年分を 残す）')
        c5 = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo'); c5.add_init_script(FAKE2); c5.add_init_script(CLK2)
        p5 = c5.new_page(); e5 = []; p5.on('pageerror', lambda e: e5.append(str(e)))
        p5.goto(STORE); p5.wait_for_timeout(1500); p5.wait_for_function("() => window.TengelWallet && TengelWallet.on && window.TengelOld && TengelClock.sure()", timeout=20000); gate(p5); p5.wait_for_timeout(700)
        # いまの 時刻（番人）から：3年と 40日前（o1）・3年と 10日前（o2）・2年11か月と 10日前（o3：30日 あとには 3年 たつ）・2年10か月と 20日前（o4：まだ）・3年と 60日前の 思い出（om）・さいきん（n1）
        SEED5 = """async ([BET, list]) => { const mk = eval(BET), now = TengelClock.now(), D = 86400000, p2 = n => (n < 10 ? '0' : '') + n, ymd = ms => { const d = new Date(ms); return d.getFullYear() + '-' + p2(d.getMonth() + 1) + '-' + p2(d.getDate()); };
          const y3 = (() => { const d = new Date(now); d.setFullYear(d.getFullYear() - 3); return d.getTime(); })();
          await TengelLocal.putBets(list.map(([id, off, mem, stampOff]) => { const t = off == null ? now - 5 * D : y3 + off * D; return mk({ id, date: ymd(t), mem, stamp: new Date(stampOff == null ? t : now + stampOff).toISOString() }); }));
          return { now, y3: ymd(y3), line: ymd(y3 + 30 * D), dates: [...TengelLocal.mem.bets.values()].map(b => b.id + ':' + b.date).sort() }; }"""
        s5 = p5.evaluate(SEED5, [BET, [['o1', -40], ['o2', -10], ['o3', 20], ['o4', 40], ['om', -60, 1], ['n1', None]]])
        # ポイントの 履歴：3年と 50日前の 2行（まとめる）・さいきんの 1行
        p5.evaluate("""async () => { const W = TengelWallet, P = TengelPoints, now = TengelClock.now(), D = 86400000, y3 = (() => { const d = new Date(now); d.setFullYear(d.getFullYear() - 3); return d.getTime(); })();
          let ev = [P.giftEvent(new Date(y3 - 50 * D), 5000)]; P.stamp(ev); ev = P.spend(ev, 400, '読み込み', 'd', new Date(y3 - 45 * D)); ev = P.spend(ev, 400, '読み込み', 'd', new Date(now - 3 * D));
          const s = W.snapshot(); s.events = ev; await W.restore(s); }""")
        r0 = p5.evaluate("async () => { await TengelOld.check(); await new Promise(r => setTimeout(r, 300)); return null; }"); tab(p5, 'rec'); p5.wait_for_timeout(300)
        g0 = p5.evaluate(INFO); note0 = g0['note'] or ''
        check(g0['st'] and g0['st']['f'] and g0['st']['f']['line'] == s5['line'] and g0['st']['f']['n'] == 3 and g0['pend'] == ['o1', 'o2', 'o3'] and len(g0['ids']) == 6,
              f'はじめの たしかめ：知らせを 始める（{s5["line"]} より 前の 記録 3件：3年 たった o1・o2 と、30日 あとに 3年 たつ o3）。まだ 消さない（{g0["pend"]}）')
        check('古い記録のお知らせ' in note0 and 'より前のレースの記録 3件が、あと30日（' in note0 and 'ごろ）で自動で消えるよ' in note0 and '思い出のレースは残るよ' in note0 and '設定の「バックアップ」でファイルに保存してね' in note0
              and p5.evaluate("() => { const n = document.querySelector('#oldNote'), v = document.querySelector('#v-rec'); return v.firstElementChild === n && n.classList.contains('warn') && n.getBoundingClientRect().width <= 390; }"),
              f'記録タブの いちばん 上に 知らせ（○件が あと30日で 自動で 消える・思い出は 残る・残したい ときは バックアップ）（{note0[:70]}…）')
        shot(p5, 'old_note')
        check(g0['rows'] == 1 and g0['total'] == 4200 and g0['carry'] and g0['carry']['cnt'] == 2, f'ポイントの 履歴：3年より 前の 2行は 自動で 1行に まとめる（残り {g0["rows"]}行・ポイント {g0["total"]:,}P は そのまま）')
        tab(p5, 'set'); p5.wait_for_timeout(300); g0b = p5.evaluate(INFO)
        check('より前の記録 3件が、' in (g0b['auto'] or '') and 'ごろに消えるよ' in g0b['auto'] and 'インターネット' not in g0b['auto'], f'設定の カードにも 予定（自動リセット：{g0b["auto"]}）')
        # 29日 たった：まだ 消えない（あと 1日）
        PASS = "async (d) => { __pass(d * 86400000); await TengelClock.sync(); await TengelOld.check(); await new Promise(r => setTimeout(r, 300)); }"
        p5.evaluate(PASS, 29); tab(p5, 'rec'); g1 = p5.evaluate(INFO)
        check(g1['pend'] == ['o1', 'o2', 'o3'] and len(g1['ids']) == 6 and 'あと1日（' in (g1['note'] or '') and g1['st']['f']['line'] == s5['line'], f'29日 たった：まだ 消えない（「{(g1["note"] or "")[20:60]}…」）')
        # 知らせた あとに 直した 記録（o2）は 次の 回・戻した 古い 記録（o5：前の 日付の まま）が 増えたら 知らせを 始めから
        p5.evaluate("async () => { const b = Object.assign({}, TengelLocal.mem.bets.get('o2'), { updatedAt: new Date(TengelClock.now()).toISOString(), note: '直した' }); await TengelLocal.putBets([b]); await TengelOld.check(); await new Promise(r => setTimeout(r, 300)); }")
        g2 = p5.evaluate(INFO)
        check(g2['pend'] == ['o1', 'o3'] and g2['st']['f']['n'] == 2 and g2['st']['f']['line'] == s5['line'], f'知らせた あとに 直した 記録（o2）は この 回では 消さない（知らせて いる のは {g2["pend"]}）')
        p5.evaluate(SEED5, [BET, [['o5', -50]]]); tab(p5, 'rec'); p5.wait_for_timeout(700)
        g3 = p5.evaluate(INFO)
        check(g3['pend'] == ['o1', 'o2', 'o3', 'o4', 'o5'] and g3['st']['f']['n'] == 5 and g3['st']['f']['line'] > s5['line'] and 'あと30日（' in (g3['note'] or '') and '5件' in g3['note'] and len(g3['ids']) == 7,
              f'戻した 古い 記録（o5）が 増えた → 知らせを 始めから（あと30日・{g3["pend"]}：タブを 開いた ときに 見直す）＝どの 記録も 知らせて から 30日は 消えない')
        p5.evaluate(PASS, 2); g4 = p5.evaluate(INFO)
        check(len(g4['ids']) == 7 and g4['pend'] == g3['pend'], 'はじめの 知らせから 31日 たっても、知らせ直した ので まだ 消えない')
        # 知らせ直して から 30日：消える（思い出・さいきんの 記録は 残る）
        p5.evaluate(PASS, 29); g5 = p5.evaluate(INFO); tab(p5, 'rec'); p5.wait_for_timeout(300); g5n = p5.evaluate(INFO)
        check(g5['ids'] == ['n1', 'om'] and g5['mem'] == ['om'] and '3年たった記録 5件を消したよ（思い出のレースは残っているよ）' in (g5['toast'] or '') and g5['st']['last'] and g5['st']['last']['n'] == 5 and g5['st']['f'] and g5['st']['f']['n'] == 0
              and g5n['note'] is None and g5['total'] == 4200,
              f'知らせて から 30日 たった：5件を 消す（「{g5["toast"]}」）・思い出の レース（3年 より 前の om）と さいきんの 記録は 残る・次の 知らせは なし（{g5["ids"]}）')
        # 電源を 入れ直して つながって いない（時刻を たしかめて いない）：古い 記録が あっても 消さない・知らせも 始めない
        p5.evaluate("() => { __netOn(0); __reboot(0); }"); p5.goto(STORE); p5.wait_for_timeout(1500); p5.wait_for_function("() => window.TengelWallet && TengelWallet.on && window.TengelOld", timeout=20000); gate(p5); p5.wait_for_timeout(2500)
        p5.evaluate(SEED5, [BET, [['o6', -70]]])
        p5.evaluate("async () => { __pass(40 * 86400000); await TengelClock.sync(); await TengelOld.check(); await new Promise(r => setTimeout(r, 300)); }"); tab(p5, 'set'); p5.wait_for_timeout(300)
        g6 = p5.evaluate(INFO)
        check(not p5.evaluate("() => TengelClock.sure()") and g6['ids'] == ['n1', 'o6', 'om'] and g6['st']['f']['n'] == 0 and 'インターネットで時刻を確かめた後に' in (g6['auto'] or ''),
              f'電源を 入れ直して つながって いない あいだは 消さない・知らせも 進めない（自動リセット：{g6["auto"]}）')
        # つながった（「online」の 知らせ → 時計の 番人が すぐ インターネットの 時刻を 聞き直す）：知らせを 始める（そこから 30日）→ 30日 たったら 消える
        p5.evaluate("async () => { __netOn(1); window.dispatchEvent(new Event('online')); await new Promise(r => setTimeout(r, 900)); await TengelOld.check(); await new Promise(r => setTimeout(r, 300)); }"); tab(p5, 'rec'); p5.wait_for_timeout(500)
        g7 = p5.evaluate(INFO)
        check(p5.evaluate("() => TengelClock.sure()") and g7['pend'] == ['o6'] and g7['st']['f']['n'] == 1 and 'あと30日（' in (g7['note'] or '') and g7['ids'] == ['n1', 'o6', 'om'], f'つながると 知らせを 始める（{g7["pend"]}・あと30日）：すぐには 消さない')
        p5.evaluate(PASS, 31); g8 = p5.evaluate(INFO)
        check(g8['ids'] == ['n1', 'om'] and '3年たった記録 1件を消したよ' in (g8['toast'] or '') and not e5, f'30日 たって 消える（{g8["ids"]}）・エラー なし {e5[:2]}')
        # App Store版には テスト版の しかけ（30日 たった ことに する）は ない
        p5.evaluate(SEED5, [BET, [['o7', -80]]]); p5.evaluate("async () => { await TengelOld.check(); await new Promise(r => setTimeout(r, 300)); }")
        sk = p5.evaluate("async () => { const r = await TengelOld.testSkip(); await new Promise(r => setTimeout(r, 300)); return [r, !!document.querySelector('#setOld [data-so=test30]'), [...TengelLocal.mem.bets.keys()].sort(), TengelOld.pending()]; }")
        check(sk == [False, False, ['n1', 'o7', 'om'], ['o7']], f'App Store版：テスト版の しかけ（お知らせから 30日 たった ことに する）は 効かない・ボタンも 出ない（{sk}）')
        c5.close()

        print('■ テスト版：自動の リセットを ためす ボタン')
        c6 = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo'); c6.add_init_script(FAKE2); c6.add_init_script(CLK2)
        p6 = c6.new_page(); e6 = []; p6.on('pageerror', lambda e: e6.append(str(e)))
        p6.goto(TESTB); p6.wait_for_timeout(1500); p6.wait_for_function("() => window.TengelWallet && TengelWallet.on && window.TengelOld && TengelClock.sure()", timeout=20000); gate(p6); p6.wait_for_timeout(700)
        tab(p6, 'set'); p6.wait_for_timeout(300)
        tb0 = p6.evaluate("() => { const b = document.querySelector('#setOld [data-so=test30]'); return b ? b.textContent : null; }")
        p6.locator('#setOld [data-so=test30]').click(); p6.wait_for_timeout(400); tt0 = p6.evaluate("() => document.querySelector('#toast').textContent")
        check(tb0 == 'テスト版：お知らせから30日たったことにする' and '今は、お知らせしている記録がないよ' in tt0, f'テスト版の カードに ボタン「{tb0}」・知らせて いる 記録が ない ときは 何も しない（「{tt0}」）')
        p6.evaluate(SEED5, [BET, [['t1', -30], ['tm', -30, 1], ['t2', None]]]); p6.evaluate("async () => { await TengelOld.check(); await new Promise(r => setTimeout(r, 300)); }"); tab(p6, 'rec'); p6.wait_for_timeout(400)
        h0 = p6.evaluate(INFO)
        tab(p6, 'set'); p6.wait_for_timeout(300); p6.locator('#setOld [data-so=test30]').click(); p6.wait_for_timeout(900)
        h1 = p6.evaluate(INFO)
        check(h0['pend'] == ['t1'] and 'あと30日（' in (h0['note'] or '') and h1['ids'] == ['t2', 'tm'] and '3年たった記録 1件を消したよ（思い出のレースは残っているよ）' in (h1['toast'] or '') and not e6,
              f'テスト版：3年 より 前の 記録を 入れると 知らせ（あと30日）→ ボタンで 30日 たった ことに すると 消える（思い出は 残る：{h1["ids"]}）・エラー なし {e6[:2]}')
        c6.close()

        print('■ Web版')
        c4 = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo')
        p4 = c4.new_page(); e4 = []; p4.on('pageerror', lambda e: e4.append(str(e))); p4.goto(WEB); p4.wait_for_timeout(1500); gate(p4); p4.wait_for_timeout(1500)
        check(p4.evaluate("() => typeof window.TengelOld === 'undefined' && !document.getElementById('setOld') && !document.getElementById('oldNote') && !(window.TengelLocal && TengelLocal.delBets)") and not e4, f'Web版：古い 台帳の リセットは ない（カードも 口も ない）・エラー なし {e4[:2]}')
        c4.close()
        b.close()
finally:
    srv.terminate()
print('NG' if fails else 'OK', len(fails), fails)
sys.exit(1 if fails else 0)
