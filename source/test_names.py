# 馬の 名前・出馬数・コース（第4.170版）の テスト
#   まさちゃん 2026/11/14 12:07「思い出フィギュアはボードの大きさ的に 日付、レース名、出馬数、コースm／着順、1位、2位、3位の名前／購入金額／回収金額 のイメージ」
#   12:36「1.足す！（思い出ボードに 出馬数・コースm） 2.名前を入れる欄を足す、名前は読み込んだ画像から割り出せる？難しいようならユーザーが入力するようにして 3.外していいよ！（的中の 種類・買い目）」
#   ・オッズの 画像に 写って いた 馬の 名前（馬番ごと）を 入力と いっしょに 持つ → 予約した 記録に 入る（names）。お知らせに「馬名12頭」
#     画像に R が 写って いなくて あとから 手で 入れても 名前は 記録に 入る／手で べつの レースの オッズに 打ち直した ときは 入れない／べつの レースを 読んだら 入れかわる
#   ・結果の 欄に「1〜3着の 馬の 名前」（3つ・なくても OK）：着順の 馬番を 入れると 自動で 入る・馬番を かえると 入れ直す・同着は「・」で つなぐ・手で 直せる（18字まで）・
#     結果の 画像の 名前は 空の 欄に 入る（記録に もう ある 名前が 先）・空に した 欄は 空の まま 覚える
#   ・思い出ボード：「レース」の 行に（N頭）・「コース」の 行（ダート 1,400m）
#   ・思い出フィギュアの ボードに 書く 文（TengelMem）：レース名／日付・出馬数・コース／1〜3着（馬番＋名前。名前が ない ときは 馬番＋人気）／購入 → 回収。的中の 種類・買い目は 書かない
#   ・名前は ユーザーの データ（記録・自動バックアップ）。アプリの 中には 馬の 名前は 1つも 入って いない
#   python3 test_names.py
import json, os, shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
SRV = os.path.join(W, 'srv_names'); PORT = 8809; STORE = f'http://localhost:{PORT}/STORE/'
SHOT = os.environ.get('SHOT')          # 画面を 写す フォルダ（見る 用）
OCR = os.path.join(W, 'testdata', 'ocr')
shutil.rmtree(SRV, ignore_errors=True); os.makedirs(SRV)
subprocess.run(['node', 'build.js'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'build_pwa.py', os.path.join(SRV, 'STORE')], check=True, stdout=subprocess.DEVNULL, env=dict({k: v for k, v in os.environ.items() if k != 'TENGEL_TEST'}, TARGET='app'))
RAW = open(os.path.join(SRV, 'STORE', 'index.html'), encoding='utf8').read()
assert "window.__NATIVE = location.protocol === 'tengel:';" in RAW
open(os.path.join(SRV, 'STORE', 'index.html'), 'w', encoding='utf8').write(RAW.replace("window.__NATIVE = location.protocol === 'tengel:';", 'window.__NATIVE = true;'))
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c: fails.append(label)


# 画像の 文字（端末の 中の 文字認識の かわり）。testdata/ocr の 見本（架空の レース・架空の 名前）
A_LINES = json.load(open(os.path.join(OCR, 'a_tanfuku_waku.json'), encoding='utf8'))['lines']      # 単勝・複勝の 表（馬番・馬名・単勝）：見出しに「第9競走」
C_LINES = json.load(open(os.path.join(OCR, 'c_sanrentan.json'), encoding='utf8'))['lines']         # 3連単の 人気順（名前は ない）：見出しに「9R」
A_JPG, C_JPG = os.path.join(OCR, 'a_tanfuku_waku.jpg'), os.path.join(OCR, 'c_sanrentan.jpg')
NAMES = {1: 'サンライズゴールド', 2: 'テンゲルクイーン', 3: 'ナイトレイン', 4: 'ブルーハーバー', 5: 'コスモスカイ', 6: 'ミラクルアロー', 7: 'ハッピーデイズ', 8: 'シルバーウィンド', 9: 'ドリームキャッチャー', 10: 'ロイヤルステップ', 11: 'スターダストメモリー', 12: 'ラストサムライ'}
SNAMES = {str(k): v for k, v in NAMES.items()}
assert A_LINES[0]['text'] == '大井競馬 第9競走' and C_LINES[0]['text'] == '大井競馬場 9R　3連単'
NO_R = lambda src: [dict(l, text=l['text'].replace('大井競馬 第9競走', '大井競馬').replace('大井競馬場 9R　3連単', '大井競馬場　3連単')) for l in src]      # 見出しの R を 切った 写真
TO_R = lambda src, r: [dict(l, text=l['text'].replace('第9競走', f'第{r}競走').replace('9R', f'{r}R')) for l in src]
LN = lambda ts: [{'text': t, 'x': 0.05, 'y': 0.05 + i * 0.035, 'w': 0.8, 'h': 0.025} for i, t in enumerate(ts)]
# べつの レースの 単勝の 表（にせもの）：見出しの R を かえる・単勝の 並びを さかさに・名前を かえる（drop の 馬番は 名前の ます が 読めなかった 形）
NAMES2 = {i + 1: 'テンゲル' + x for i, x in enumerate(['アルファ', 'ベータ', 'ガンマ', 'デルタ', 'イプシロン', 'ゼータ', 'イータ', 'シータ', 'イオタ', 'カッパ', 'ラムダ', 'ミュー'])}
assert len(A_LINES) == 68 and A_LINES[8]['text'] == '1' and A_LINES[9]['text'] == NAMES[1] and A_LINES[10]['text'] == '12.4'      # 表は 8こ目から：枠・馬番・馬名・単勝・複勝 が 12頭ぶん


def OTHER(src, r, drop=()):
    L = [dict(l) for l in TO_R(src, r)]; cells = L[7:67]; tans = [cells[i * 5 + 3]['text'] for i in range(12)][::-1]; out = L[:7]
    for i in range(12):
        row = cells[i * 5:i * 5 + 5]; no = int(row[1]['text'])
        row[2] = dict(row[2], text=NAMES2[no]); row[3] = dict(row[3], text=tans[i])
        out += [c for k, c in enumerate(row) if not (k == 2 and no in drop)]
    return out + L[67:]


# 結果の 画面（にせもの）：6 → 2 → 10・名前は オッズの 画像と ちがう もの（どちらが 入ったか 見分ける）
RESULT = LN(['レース結果', '着順 枠 馬番 馬名 性齢 斤量 騎手 タイム 人気', '1 3 6 ハナ 牡4 56.0 きしゅ 1:25.3 1', '2 1 2 フタ 牝3 54.0 きしゅ 1:25.5 2', '3 6 10 トオ 牡5 57.0 きしゅ 1:25.9 3', '4 2 4 ヨン 牡4 56.0 きしゅ 1:26.0 5',
             '払戻金', '単勝 6 240円 1人気', '馬単 6-2 1,120円', '3連単 6-2-10 12,340円'])

# アプリ（Swift）の にせもの：しるし・自動バックアップ・お知らせは Python の 側（ページを 開き直しても のこる）・画像の 文字認識は window.__ocrLines から 1まい ずつ
FAKE = """
window.__NATIVE_INFO = { version: '1.0', build: '7', device: 'phone' };
window.__ocrLines = [];
window.webkit = { messageHandlers: { tengel: { postMessage: function (m) {
  if (m.name === 'ocr') { var L = window.__ocrLines.shift(), val = L ? { ok: true, lines: L, w: 1170, h: 2532, ms: 900 } : { ok: false, error: 'image_rejected' }; setTimeout(function () { window.__nativeReply(m.id, true, val); }, 20); return; }
  window.__py({ id: m.id, name: m.name, payload: m.payload && m.payload.data ? null : m.payload }).then(function (v) { if (m.id > 0 && window.__nativeReply) window.__nativeReply(m.id, true, v); });
} } } };
"""
# ページの 日付は 2026/10/01 から（見本の レースは 10/14：締切済みに ならない ように。test_native.py と 同じ 考え方）
CLOCK = """(() => { const D = Date, OFF = Date.UTC(2026, 9, 1, 3, 0, 0) - D.now();
  class FD extends D { constructor(...a) { if (a.length) super(...a); else super(D.now() + OFF); } static now() { return D.now() + OFF; } }
  FD.UTC = D.UTC; FD.parse = D.parse; window.Date = FD; })();"""


class Native:
    def __init__(self):
        self.markers, self.backup, self.items, self.auth = {}, None, [], 'notDetermined'

    def handle(self, source, m):
        name, P = m.get('name'), m.get('payload') or {}
        if name == 'backup': self.backup = P.get('text'); return True
        if name == 'marker':
            op, key = P.get('op'), P.get('key')
            if op == 'set': self.markers[key] = P.get('value', '1'); return {'ok': True}
            if op == 'del': self.markers.pop(key, None); return {'ok': True}
            v = self.markers.get(key); return {'ok': True, 'has': v is not None, 'value': v}
        if name == 'notify':
            op = P.get('op')
            if op == 'status': return {'ok': True, 'auth': self.auth}
            if op == 'permission': self.auth = 'authorized'; return {'ok': True, 'granted': True, 'auth': self.auth}
            if op == 'sync': self.items = P.get('items') or []; return {'ok': True, 'scheduled': len(self.items), 'auth': self.auth}
            if op == 'opened': return {'ok': True, 'opened': None}
            return {'ok': True, 'list': self.items}
        if name == 'iap':
            return {'ok': True, 'products': []} if P.get('op') == 'products' else {'ok': True, 'list': [], 'current': [], 'unfinished': [], 'active': []}
        if name == 'zoom': return {'zoom': 1, 'pinch': not P.get('lock')}
        return True


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


FORM = "() => { const f = JSON.parse(localStorage.getItem('tengel.form') || '{}'); return { r: f.r, n: f.n, date: f.date, rows: (f.rows || []).length, names: f.names || null, nkey: f.nkey || '', nsig: f.nsig || null, msg: document.getElementById('ocrMsg').textContent }; }"
REC = "(r) => [...TengelLocal.mem.bets.values()].find(b => b.r === r) || null"
VAL = "() => [1, 2, 3].map(i => { const x = document.querySelector('#recList .rsvf [data-k=nm' + i + ']'); return x ? x.value : null; })"
yen = lambda v: f'{int(v):,}'

try:
    with sync_playwright() as p:
        br = p.chromium.launch()
        ctx = br.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, locale='ja-JP', timezone_id='Asia/Tokyo')
        nat = Native(); ctx.expose_binding('__py', nat.handle)
        ctx.route('**/__native/autobackup.json', lambda route: route.fulfill(status=404, body='not found'))
        ctx.add_init_script(FAKE); ctx.add_init_script(CLOCK)
        pg = ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))

        def open_app():
            pg.goto(STORE); pg.wait_for_timeout(1200)
            pg.wait_for_function("() => window.TengelWallet && TengelWallet.on && window.TengelLocal", timeout=30000); pg.wait_for_timeout(600)
            gate(pg); pg.wait_for_timeout(700)
            pg.evaluate("() => { const m = document.getElementById('minibar'); if (m) m.hidden = true; try { TengelFx.set({ effects: false }); } catch (e) {} }")

        def read(lines, files):
            """画像を 読む（lines＝1まい ごとの 文字）→ 読み おわる まで 待つ"""
            pg.evaluate("(l) => { window.__ocrLines = l; document.getElementById('ocrMsg').textContent = ''; }", lines)
            pg.set_input_files('#ocrFile', files)
            pg.wait_for_function("() => !window.__ocrLines.length && document.getElementById('ocrMsg').textContent.length > 0", timeout=30000); pg.wait_for_timeout(900)
            return pg.evaluate(FORM)

        def reserve():
            card = pg.locator('#recCard'); card.scroll_into_view_if_needed(); pg.wait_for_timeout(200)
            card.locator('[data-rsv=reserve]').click(); pg.wait_for_timeout(1100)

        def open_row(rid):
            """記録タブで その レースの 行を 開く（もう 開いて いれば そのまま）"""
            if pg.locator(f'#recList .rsvf[data-id="{rid}"]').count(): return pg.locator(f'#recList .rsvf[data-id="{rid}"]')
            pg.locator(f'#recList .lrow:not(.memrow)[data-id="{rid}"] .lmain').first.click(); pg.wait_for_timeout(700)
            return pg.locator(f'#recList .rsvf[data-id="{rid}"]')

        def setp(box, k, v):
            box.locator(f'[data-k={k}]').fill(v); pg.wait_for_timeout(160)

        print('■ アプリの 中に 馬の 名前は 入って いない')
        check(not [v for v in NAMES.values() if v in RAW] and '馬の 名前' in RAW and 'data-k="nm' in RAW, 'App Store版の index.html に 見本の 馬の 名前は 1つも ない（名前の 欄の しかけは ある）')

        print('■ オッズの 画像の 名前 → 入力 → 予約した 記録')
        open_app()
        pg.click('.tabbar button[data-tab=judge]'); pg.wait_for_timeout(400)
        f0 = pg.evaluate(FORM); r0 = pg.locator('#fR').input_value()
        check(f0['names'] is None and r0 == '8', f'はじめの 入力（入力例）に 名前は ない（R={r0}）')
        # 1まい ずつ 読む：1まい目＝単勝の 表（見出しの R が 写って いない）→ R は 前の まま（入力例の 8）・名前は 読める
        f1 = read([NO_R(A_LINES)], [A_JPG])
        print('   読み取り:', f1['msg'][:150])
        check(f1['rows'] == 12 and f1['r'] == '8' and f1['names'] == SNAMES and '馬名12頭' in f1['msg'] and '単勝12頭' in f1['msg'], f'画像に 写って いた 馬の 名前（馬番ごと 12頭）が 入力に 入る・お知らせに「馬名12頭」（R は 読めず {f1["r"]} の まま）')
        check(f1['nkey'].endswith('-08') and isinstance(f1['nsig'], list) and len(f1['nsig']) == 12 and f1['nsig'][5] == '6:2.4', f'名前を 読んだ ときの レース（nkey）と 単勝の 表（nsig）を 覚える（{f1["nkey"]}・{f1["nsig"][:2]}）')
        check('ミラクルアロー' not in pg.locator('#v-judge').inner_text(), '判定の 画面に 名前は 出さない（入力と いっしょに 持つ だけ）')
        # 2まい目＝3連単の 人気順（見出しに 開催場と 9R・名前は ない）→ R が 9 に かわっても、単勝の 表は そのまま ＝ 同じ レース：名前は のこる
        f1b = read([C_LINES], [C_JPG])
        check(f1b['r'] == '9' and f1b['names'] == SNAMES and f1b['nkey'] == f1['nkey'] and '馬名' not in f1b['msg'] and '3連単1位' in f1b['msg'],
              f'2まい目（3連単の 人気順）で R が 9 に 入っても 名前は のこる（単勝の 表が そのまま＝同じ レース。はじめて 使う ときの 流れ）（R={f1b["r"]}）')
        reserve()
        b9 = pg.evaluate(REC, 9)
        check(b9 is not None and b9['rsv']['state'] == 'reserved' and b9.get('names') == SNAMES and 'pn' not in b9 and 'nkey' not in b9 and 'nsig' not in b9,
              '予約 → 記録に 名前（names：馬番ごと 12頭）が 入る・1〜3着の 名前（pn）は まだ ない・入力用の しるし（nkey・nsig）は 記録に 入れない')
        id9 = b9['id']
        # R を 手で 直す（読みまちがえて いた つもり：7R に）＋ 単勝を 1頭 直す → 単勝の 表が ほぼ 読んだ ときの まま ＝ 同じ レース：名前は 記録に 入る
        pg.select_option('#fR', '7'); pg.wait_for_timeout(300)
        tan12 = pg.locator('.orow input[data-k=tan][data-no="12"]').input_value()
        pg.fill('.orow input[data-k=tan][data-no="12"]', str(round(float(tan12) + 0.3, 1))); pg.wait_for_timeout(700)
        reserve()
        b7 = pg.evaluate(REC, 7)
        check(b7 is not None and b7.get('names') == SNAMES, f'R を 手で 直して（単勝も 1頭 直して）予約 → 名前は 記録に 入る（12番 {tan12} → 直した）')
        # 手で べつの レースに 打ち直す（R を 11 に・単勝の 7頭を 打ち直す）→ 前の レースの 名前は 持って いかない
        pg.select_option('#fR', '11'); pg.wait_for_timeout(300)
        for no, v in ((1, '13.1'), (3, '9.9'), (4, '21.0'), (5, '31.5'), (7, '16.6'), (8, '45.2'), (9, '60.3')):
            pg.fill(f'.orow input[data-k=tan][data-no="{no}"]', v); pg.wait_for_timeout(120)
        pg.wait_for_timeout(700)
        f2 = pg.evaluate(FORM)
        reserve()
        b11 = pg.evaluate(REC, 11)
        check(f2['r'] == '11' and f2['names'] == SNAMES and b11 is not None and b11['rsv']['state'] == 'reserved' and 'names' not in b11,
              f'手で べつの レース（11R・単勝を 7頭 打ち直し）に した 入力を 予約 → 記録に 名前は 入らない（前の レースの 名前を 持って いかない）（names={b11 and b11.get("names")}）')
        id11 = b11['id']
        # 見出しの ある 写真 2まい（9R）を いっしょに 読む → 名前は 9R に むすぶ
        f3 = read([A_LINES, C_LINES], [A_JPG, C_JPG])
        check(f3['r'] == '9' and f3['names'] == SNAMES and f3['nkey'] == id9 and '馬名12頭' in f3['msg'], f'見出しの ある 写真 2まい（9R）を 読む → 名前は その レースに むすぶ（nkey={f3["nkey"]}）')
        # 表の ない 写真 → いまの 入力は そのまま
        f5 = read([LN(['ようこそ'])], [C_JPG])
        check(f5['names'] == SNAMES and f5['rows'] == 12 and '見つからなかった' in f5['msg'], '表の ない 写真：名前も いまの 入力も そのまま')
        # べつの レース（10R）の 単勝の 表（オッズも 名前も ちがう・5番の 名前は 読めなかった 形）→ 前の レースの 名前は 1つも のこさない
        f7 = read([OTHER(A_LINES, 10, drop=(5,))], [A_JPG])
        want7 = {str(k): v for k, v in NAMES2.items() if k != 5}
        check(f7['r'] == '10' and f7['names'] == want7 and '5' not in f7['names'] and f7['nkey'].endswith('-10') and '馬名11頭' in f7['msg'],
              f'べつの レース（10R）の 単勝の 表を 読む → 名前は 入れかわる（前の レースの 名前は 1つも のこらない：読めなかった 5番は 空）（{len(f7["names"] or {})}頭）')
        # 同じ レース（10R）を もう一度（こんどは 5番も 読めた）→ 重ねる
        f8a = read([OTHER(A_LINES, 10)], [A_JPG])
        check(f8a['names'] == {str(k): v for k, v in NAMES2.items()} and '馬名12頭' in f8a['msg'], '同じ レースの 読み直しは 名前を 重ねる（5番も 入る）')
        shot(pg, 'names_1_judge')

        print('■ 結果の 欄：1〜3着の 馬の 名前')
        pg.click('.tabbar button[data-tab=rec]'); pg.wait_for_timeout(800)
        box = open_row(id9)
        lay0 = pg.evaluate("""() => { const b = document.querySelector('#recList .rsvf'), ins = [...b.querySelectorAll('.pln .pnr input')];
          return { n: ins.length, lab: b.querySelector('.pln').previousElementSibling.textContent, ph: ins.map(e => e.placeholder), aria: ins.map(e => e.getAttribute('aria-label')), max: ins.map(e => e.maxLength), tags: [...b.querySelectorAll('.pln .pnr span')].map(e => e.textContent),
            after: b.querySelector('.pln').closest('.f').previousElementSibling.querySelector('[data-k=p1]') !== null }; }""")
        check(box.count() == 1 and box.get_attribute('data-mode') == 'result' and lay0['n'] == 3 and pg.evaluate(VAL) == ['', '', ''] and lay0['lab'].startswith('1〜3着の 馬の 名前') and 'なくても OK' in lay0['lab'] and '直せるよ' in lay0['lab']
              and lay0['ph'] == ['1着の 名前', '2着の 名前', '3着の 名前'] and lay0['aria'] == ['1着の 馬の 名前', '2着の 馬の 名前', '3着の 馬の 名前'] and lay0['max'] == [18, 18, 18] and lay0['tags'] == ['1着', '2着', '3着'] and lay0['after'],
              f'結果の 欄（着順の すぐ 下）に「1〜3着の 馬の 名前」の 欄 3つ（はじめは 空・18字まで・「なくても OK…直せるよ」）（{lay0["lab"]}）')
        setp(box, 'p1', '6'); setp(box, 'p2', '2'); setp(box, 'p3', '10')
        check(pg.evaluate(VAL) == ['ミラクルアロー', 'テンゲルクイーン', 'ロイヤルステップ'], f'着順の 馬番を 入れる → その 馬番の 名前が 自動で 入る（{pg.evaluate(VAL)}）')
        setp(box, 'p2', '13')
        v13 = pg.evaluate(VAL)
        setp(box, 'p2', '2')
        check(v13 == ['ミラクルアロー', '', 'ロイヤルステップ'] and pg.evaluate(VAL)[1] == 'テンゲルクイーン', '馬番を 名前の ない 番号に かえる → その 欄は 空に・もどすと 名前も もどる')
        setp(box, 'p1', '6.1')
        vt = pg.evaluate(VAL)
        setp(box, 'p1', '6')
        check(vt[0] == 'ミラクルアロー・サンライズゴールド' and pg.evaluate(VAL)[0] == 'ミラクルアロー', f'同着（6.1）は 名前を「・」で つなぐ（{vt[0]}）')
        setp(box, 'nm3', 'なおした なまえ'); setp(box, 'p2', '5'); setp(box, 'p2', '2')
        check(pg.evaluate(VAL) == ['ミラクルアロー', 'テンゲルクイーン', 'なおした なまえ'], '手で 直した 名前は、ほかの 着順を かえても そのまま（その 着順の 馬番を かえる まで）')
        setp(box, 'nm1', '')
        pg.evaluate("(l) => { window.__ocrLines = [l]; }", RESULT)
        box.locator('[data-k=rimgfile]').set_input_files([C_JPG]); pg.wait_for_function("() => !window.__ocrLines.length", timeout=20000); pg.wait_for_timeout(1500)
        hint = box.locator('[data-k=hint]').inner_text()
        check(pg.evaluate(VAL) == ['ミラクルアロー', 'テンゲルクイーン', 'なおした なまえ'] and [box.locator(f'[data-k=p{i}]').input_value() for i in (1, 2, 3)] == ['6', '2', '10'] and '馬の 名前' in hint and '読み取った' in hint,
              f'結果の 画像を 読む → 空の 欄に 名前が 入る（記録に ある 名前が 先：ハナ では なく ミラクルアロー）・手で 直した 欄は そのまま・お知らせに「馬の 名前」（{hint[:50]}）')
        lay = pg.evaluate("""() => { const b = document.querySelector('#recList .rsvf'), c = b.getBoundingClientRect(), R = e => { const r = e.getBoundingClientRect(); return [r.left, r.right, r.top, r.bottom, r.height]; };
          const ins = [...b.querySelectorAll('.pnr input')].map(R); return { ins, box: [c.left, c.right], sw: document.documentElement.scrollWidth, fs: parseFloat(getComputedStyle(b.querySelector('.pnr input')).fontSize) }; }""")
        check(all(lay['box'][0] <= i[0] and i[1] <= lay['box'][1] + 0.5 and i[4] >= 40 for i in lay['ins']) and lay['ins'][0][3] <= lay['ins'][1][2] <= lay['ins'][2][2] and lay['sw'] <= 390 and lay['fs'] >= 16,
              f'名前の 欄は たてに 3つ・わくの 中・高さ 40px 以上・字は 16px 以上（押しても 画面が 拡大しない）・横に はみ出さない（{[round(x) for x in lay["ins"][0]]}・{lay["fs"]}px）')
        shot(pg, 'names_2_result')
        # 長い 名前・前後の 空白・改行の 字 → 保存の ときに きれいに する（18字まで）
        pg.evaluate("(v) => { const x = document.querySelector('#recList .rsvf [data-k=nm2]'); x.value = v; x.dispatchEvent(new Event('input', { bubbles: true })); }", '\u3000 ながい\t なまえ' + 'あ' * 30); pg.wait_for_timeout(200)      # 貼り付け などで 18字を こえた 形
        box.locator('[data-act=rsave]').click(); pg.wait_for_timeout(1500)
        pg.evaluate("() => { if (document.getElementById('fxOv')) TengelFx.close(true); }"); pg.wait_for_timeout(500)
        b9d = pg.evaluate(REC, 9)
        long2 = 'ながい なまえ' + 'あ' * 11
        check(b9d['rsv']['state'] == 'done' and [b9d['n1'], b9d['n2'], b9d['n3']] == [6, 2, 10] and b9d.get('pn') == ['ミラクルアロー', long2, 'なおした なまえ'] and len(long2) == 18 and b9d.get('names') == SNAMES,
              f'「結果を決める」→ 記録に 1〜3着の 名前（pn）・長い 名前は 18字まで・空白は きれいに・馬番ごとの 名前（names）は 記録の まま（結果の 画像の 名前で 上書き しない）（{b9d.get("pn")}）')
        box = pg.locator('#recList .rsvf')
        check(box.get_attribute('data-mode') == 'amount' and box.locator('[data-k=nm1]').count() == 0, '金額の 欄（つぎの 形）に 名前の 欄は ない')
        box.locator('[data-act=rsave]').click(); pg.wait_for_timeout(1000)
        b9e = pg.evaluate(REC, 9)
        box = open_row(id9)
        check(b9e.get('pn') == b9d.get('pn') and box.get_attribute('data-mode') == 'edit' and pg.evaluate(VAL) == b9d.get('pn'), '金額を 記録しても 名前は そのまま・あとから 直す 形の 欄に 保存した 名前が 出る')
        # 空に した 欄は 空の まま 覚える（つぎに 開いても 自動で 入れ直さない）・馬番を かえると 入れ直す
        setp(box, 'nm1', ''); setp(box, 'nm2', 'テンゲルクイーン')
        box.locator('[data-act=rsave]').click(); pg.wait_for_timeout(1000)
        b9f = pg.evaluate(REC, 9)
        box = open_row(id9)
        check(b9f.get('pn') == ['', 'テンゲルクイーン', 'なおした なまえ'] and pg.evaluate(VAL) == ['', 'テンゲルクイーン', 'なおした なまえ'], f'空に した 欄は 空の まま 覚える（つぎに 開いても 自動で 入れ直さない）（{b9f.get("pn")}）')
        inf0 = pg.evaluate("(id) => { const b = TengelLocal.mem.bets.get(id); return b ? [b.p1, b.p2, b.p3] : null; }", id9)
        setp(box, 'p1', '7'); v7 = pg.evaluate(VAL); setp(box, 'p1', '6')
        check(v7[0] == 'ハッピーデイズ' and pg.evaluate(VAL) == ['ミラクルアロー', 'テンゲルクイーン', 'なおした なまえ'] and inf0 == [1, 2, 3], '着順の 馬番を かえると その 馬番の 名前を 入れ直す（7番 → ハッピーデイズ・6番に もどす → ミラクルアロー）')
        box.locator('[data-act=rsave]').click(); pg.wait_for_timeout(1000)
        b9g = pg.evaluate(REC, 9)
        check(b9g.get('pn') == ['ミラクルアロー', 'テンゲルクイーン', 'なおした なまえ'], '保存 → 1〜3着の 名前が 記録に 入る')

        # 名前の ない 記録（11R）：結果の 画像の 名前が 入る → 保存で 記録の 名前（names）に 足す
        box = open_row(id11)
        check(box.get_attribute('data-mode') == 'result' and pg.evaluate(VAL) == ['', '', ''], '名前の ない 記録（11R）：名前の 欄は 空')
        setp(box, 'p1', '6'); setp(box, 'p2', '2'); setp(box, 'p3', '10')
        check(pg.evaluate(VAL) == ['', '', ''], '名前の ない 記録は 馬番を 入れても 空の まま（手で 入れられる）')
        pg.evaluate("(l) => { window.__ocrLines = [l]; }", RESULT)
        box.locator('[data-k=rimgfile]').set_input_files([C_JPG]); pg.wait_for_function("() => !window.__ocrLines.length", timeout=20000); pg.wait_for_timeout(1500)
        check(pg.evaluate(VAL) == ['ハナ', 'フタ', 'トオ'] and '馬の 名前' in box.locator('[data-k=hint]').inner_text(), f'結果の 画像に 写って いた 名前が 1〜3着の 欄に 入る（{pg.evaluate(VAL)}）')
        setp(box, 'p3', '4'); v4 = pg.evaluate(VAL); setp(box, 'p3', '10')
        check(v4[2] == 'ヨン' and pg.evaluate(VAL)[2] == 'トオ', '結果の 画像の 名前も 馬番ごと（3着を 4番に → ヨン・10番に もどす → トオ）')
        box.locator('[data-act=rsave]').click(); pg.wait_for_timeout(1500)
        pg.evaluate("() => { if (document.getElementById('fxOv')) TengelFx.close(true); }"); pg.wait_for_timeout(500)
        b11d = pg.evaluate(REC, 11)
        check(b11d['rsv']['state'] == 'done' and b11d.get('pn') == ['ハナ', 'フタ', 'トオ'] and b11d.get('names') == {'2': 'フタ', '4': 'ヨン', '6': 'ハナ', '10': 'トオ'}, f'「結果を決める」→ 1〜3着の 名前（pn）と 結果の 画像の 馬番ごとの 名前（names）が 記録に 入る（{b11d.get("names")}）')
        pg.locator('#recList .rsvf [data-act=rlater]').click(); pg.wait_for_timeout(700)

        print('■ 思い出ボード（出馬数・コース）・フィギュアの ボードに 書く 文')
        box = open_row(id9)
        box.locator('[data-act=memtog]').click(); pg.wait_for_timeout(900)
        b9m = pg.evaluate(REC, 9)
        info = pg.evaluate("(id) => TengelMem.get(id).info", id9)
        money = f'購入 {yen(b9m["stake"])}円 → 回収 {yen(b9m["payout"] or 0)}円'
        check(info == {'v': 2, 'race': '大井 9R', 'date': '2026年10月14日（水）', 'sub': '12頭・ダート 1,400m', 'lines': ['1着　6番 ミラクルアロー', '2着　2番 テンゲルクイーン', '3着　10番 なおした なまえ'], 'money': money},
              f'フィギュアの ボードに 書く 文：レース名／日付／出馬数・コース／1〜3着（馬番＋名前）／購入 → 回収。的中の 種類（kind）・買い目・結果の 行は ない（{json.dumps(info, ensure_ascii=False)}）')
        pg.locator('#recList .memtop .memrow .lmain').first.click(); pg.wait_for_selector('#fxOv.mem', timeout=10000); pg.wait_for_timeout(1500)
        rows = pg.evaluate("() => [...document.querySelectorAll('#fxOv .memx .mx')].map(e => e.querySelector('.mk').textContent + '｜' + e.querySelector('.mv').textContent.replace(/\\s+/g, ' ').trim())")
        keys = [x.split('｜')[0] for x in rows]
        check(rows[:3] == ['日付｜2026年10月14日（水）', 'レース｜大井 9R（12頭）', 'コース｜ダート 1,400m'] and keys[3] == '買い目' and '結果' in keys and keys[-1] == '金額',
              f'思い出ボード：「レース」の 行に 出馬数（12頭）・「コース」の 行（ダート 1,400m）・ほかは いままで どおり（買い目・結果・金額）（{rows[:3]}）')
        ovb = pg.evaluate("() => { const c = document.querySelector('#fxOv .memx').getBoundingClientRect(), m = [...document.querySelectorAll('#fxOv .memx .mx')].map(e => e.getBoundingClientRect()); return { in: m.every(r => r.left >= c.left - 0.5 && r.right <= c.right + 0.5), sw: document.documentElement.scrollWidth }; }")
        check(ovb['in'] and ovb['sw'] <= 390, '足した 行は カードの 中（横に はみ出さない）')
        shot(pg, 'names_3_memboard')
        pg.locator('#fxOv .close').click(force=True); pg.wait_for_timeout(500)
        # いろいろな 記録の 形（名前の 一部 だけ・名前なし・距離なし・同着・中止・馬番ごとの 名前 だけ）
        pg.evaluate("""async () => {
          const mk = (id, r, o) => Object.assign({ id, date: '2026-09-0' + r, venue: '', r, rname: 'テスト' + r, n: 14, dist: 2000, surface: '芝', types: ['馬単'], n1: 5, n2: 2, n3: 1, p1: 3, p2: 1, p3: 2, stake: '600', payout: '0', horses: [],
            rsv: { state: 'done', types: ['馬単'], bets: { '馬単': [[3, 7]] }, result: { p: [[5], [2], [1]] }, fx: 'miss', at: new Date().toISOString() }, mem: { at: new Date().toISOString(), v: 'a' } }, o);
          await TengelLocal.putBets([
            mk('nm_a', 1, { pn: ['テンゲルいち', '', 'テンゲルさん'] }),
            mk('nm_b', 2, { n: 0, dist: '', surface: 'ダ' }),
            mk('nm_c', 3, { dist: 1200, surface: 'ダ', names: { 5: 'テンゲルご', 1: 'テンゲルわん' } }),
            mk('nm_d', 4, { surface: '', rsv: { state: 'done', types: ['馬単'], bets: { '馬単': [[3, 7]] }, result: { p: [[5, 2], [], [1]] }, fx: 'miss', at: new Date().toISOString() }, n1: 5, n2: null, n3: 1, p1: 3, p2: null, p3: 2, names: { 5: 'テンゲルご', 2: 'テンゲルに' } }),
            mk('nm_e', 5, { rsv: { state: 'done', types: ['馬単'], bets: { '馬単': [[3, 7]] }, result: { p: [[], [], []], abandoned: true }, fx: 'miss', at: new Date().toISOString() }, n1: null, n2: null, n3: null, p1: null, p2: null, p3: null, pn: ['', '', ''] }),
          ]); }"""); pg.wait_for_timeout(700)
        I = {k: pg.evaluate("(id) => TengelMem.get(id).info", k) for k in ('nm_a', 'nm_b', 'nm_c', 'nm_d', 'nm_e')}
        check(I['nm_a']['lines'] == ['1着　5番 テンゲルいち', '2着　2番（1番人気）', '3着　1番 テンゲルさん'] and I['nm_a']['sub'] == '14頭・芝 2,000m' and I['nm_a']['date'] == '2026年9月1日（火）' and I['nm_a']['money'] == '購入 600円 → 回収 0円',
              f'名前が 一部 だけ：ある 着順は 馬番＋名前・ない 着順は 馬番＋人気／出馬数・芝 2,000m（{I["nm_a"]["lines"]}・{I["nm_a"]["sub"]}）')
        check(I['nm_b']['lines'] == ['1着　5番（3番人気）', '2着　2番（1番人気）', '3着　1番（2番人気）'] and I['nm_b']['sub'] == '' and 'kind' not in I['nm_b'] and 'result' not in I['nm_b'], f'名前も 出馬数も 距離も ない 記録：馬番＋人気・出馬数・コースは 書かない（{I["nm_b"]}）')
        check(I['nm_c']['lines'] == ['1着　5番 テンゲルご', '2着　2番（1番人気）', '3着　1番 テンゲルわん'] and I['nm_c']['sub'] == '14頭・ダート 1,200m', f'1〜3着の 名前を まだ 保存して いない 記録：馬番ごとの 名前から（{I["nm_c"]["lines"]}）')
        check(I['nm_d']['lines'] == ['1着　5・2番 テンゲルご・テンゲルに', '3着　1番（2番人気）'] and I['nm_d']['sub'] == '14頭・2,000m', f'同着：馬番も 名前も「・」で つなぐ・着順の ない 行は 書かない・芝／ダートが ない ときは 距離 だけ（{I["nm_d"]["lines"]}・{I["nm_d"]["sub"]}）')
        check(I['nm_e']['lines'] == ['中止（全部返還）'], f'中止の レース：「中止（全部返還）」（{I["nm_e"]["lines"]}）')
        pg.click('.tabbar button[data-tab=judge]'); pg.wait_for_timeout(300); pg.click('.tabbar button[data-tab=rec]'); pg.wait_for_timeout(800)
        pg.locator('#recList .memtop .memrow[data-mid="nm_b"] .lmain').click(); pg.wait_for_selector('#fxOv.mem', timeout=10000); pg.wait_for_timeout(1200)
        rows = pg.evaluate("() => [...document.querySelectorAll('#fxOv .memx .mx')].map(e => e.querySelector('.mk').textContent + '｜' + e.querySelector('.mv').textContent.replace(/\\s+/g, ' ').trim())")
        check(rows[1] == 'レース｜2R テスト2' and not [x for x in rows if x.startswith('コース')] and rows[2].startswith('買い目'), f'出馬数も 距離も ない 記録の 思い出ボード：（N頭）も「コース」の 行も 出さない（前と 同じ 形）（{rows[:3]}）')
        pg.locator('#fxOv .close').click(force=True); pg.wait_for_timeout(500)
        pg.locator('#recList .memtop .memrow[data-mid="nm_a"] .lmain').click(); pg.wait_for_selector('#fxOv.mem', timeout=10000); pg.wait_for_timeout(1200)
        rows = pg.evaluate("() => [...document.querySelectorAll('#fxOv .memx .mx')].map(e => e.querySelector('.mk').textContent + '｜' + e.querySelector('.mv').textContent.replace(/\\s+/g, ' ').trim())")
        check(rows[1] == 'レース｜1R テスト1（14頭）' and rows[2] == 'コース｜芝 2,000m', f'芝の レースの 思い出ボード：（14頭）・「コース｜芝 2,000m」（{rows[1:3]}）')
        pg.locator('#fxOv .close').click(force=True); pg.wait_for_timeout(500)

        print('■ 名前は ユーザーの データ：自動バックアップ・開き直し・判定画面で開く')
        pg.wait_for_timeout(2200)
        bk = {x['id']: x for x in json.loads(nat.backup or '{}').get('bets', [])}
        check(id9 in bk and bk[id9].get('names') == SNAMES and bk[id9].get('pn') == ['ミラクルアロー', 'テンゲルクイーン', 'なおした なまえ'] and bk[id11].get('pn') == ['ハナ', 'フタ', 'トオ'], '自動バックアップに 名前（names・pn）も 入る')
        open_app(); pg.click('.tabbar button[data-tab=rec]'); pg.wait_for_timeout(900)
        b9r = pg.evaluate(REC, 9)
        box = open_row(id9)
        check(b9r.get('pn') == ['ミラクルアロー', 'テンゲルクイーン', 'なおした なまえ'] and b9r.get('names') == SNAMES and pg.evaluate(VAL) == ['ミラクルアロー', 'テンゲルクイーン', 'なおした なまえ'], 'アプリを 開き直しても 名前は 記録に のこる')
        box.locator('[data-act=load]').click(); pg.wait_for_timeout(900)
        f8 = pg.evaluate(FORM)
        check(f8['r'] == '9' and f8['names'] == SNAMES and f8['nkey'] == id9 and isinstance(f8['nsig'], list) and len(f8['nsig']) == 12, '「判定画面で開く」→ 入力に 名前も もどる（予約し直しても 名前は 記録に のこる）')
        check(not errs, f'ページの エラー なし（{errs[:3]}）')
        br.close()
finally:
    srv.terminate()
print(f'\n結果：{"ぜんぶ OK" if not fails else "NG " + str(len(fails)) + "こ"}')
for x in fails: print('  ❌', x)
sys.exit(1 if fails else 0)
