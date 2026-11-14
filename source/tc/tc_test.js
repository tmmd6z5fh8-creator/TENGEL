// トレーニングセンター：テスト版の 道具箱（第4.154版・まさちゃん 2026/11/11 20:00「テスト版で、トレーニングセンターの幻の馬と神様馬の出現テストできるようにして！
//   お世話の当選パターン全種類テストできるようにして！」）
//   ・テスト版（TENGEL_TEST=1 で 作った アプリ）の tc_bundle.js に だけ 入る（build_pwa.py）。App Store版の 中身には 入らない
//   ・上の 帯の「🧪 テスト」→ 紙の 道具箱（下へ スクロール）。ボタンを 押すと とじて、フィールドに お知らせ → そのまま お世話を すると その 結果が 出る
//   ・馬：本番と 同じ 流れで やってくる／帰る（tc_app.js の TEST.visit）
//   ・ごはん・おそうじの 当たり：次の 1回 だけ 決める（TEST.prize）。その 当たりが 出る 馬（いつもの 馬・幻の馬・神様馬）が いない ときは 先に 入れかえる ＝ 本番で 起きる 組み合わせ だけ
//   ・そのほか：ハート 10この 抽選（ぴょん／ふぅ〜：第4.156版で ごろんを やめた）・金のニンジン・おかわりの目・首を かしげる・ほうきを かじる・呼ぶの 3つ・ゴミ・うんち・金のうんち・高確ゾーン・トークン
//   第4.165版（まさちゃん 2026/11/13 11:46「トレーニングセンターのルーレット抽選や幻の馬、神様馬のテストができるようにする」）：
//     ・② の いちばん 上に「えらんだら すぐ PUSH を 出す（お世話を とばす）」の スイッチ（はじめは オン・端末に おぼえる）：当たりを えらぶと ごはん・おそうじを しなくても
//       お世話の あとの PUSH が すぐ 出る → 押すと その 当たり（ルーレット・ポイント・チケット・はずれ）。オフに すると 前と 同じ（そのまま お世話を すると 出る）。「PUSH を すぐ 出す」の ボタンも
//     ・③ に お世話トークンを 0こに・トークンの 時計を 5分 進める（＋5 を ためす）。お世話トークン購入は 下の 列の 1番 右の ボタン（テスト版の ポイントで 買える）
//     ・設定の「テスト版の道具」の「トレーニングセンターの テスト道具を ひらく」からも 開ける（tc_app.js の open({ test:true })）
//     ・12:51「ポイントの特化ゾーンを作る」：② に「🌈 ポイント特化ゾーン」（上乗せの 回数を えらぶ：0・1・3・6・11・12回〈MAX〉・くじどおり）。いまの 馬の まま 出る
//   TCTest.open(el, api)・TCTest.close()・TCTest.isOpen()　api＝tc_app.js の TEST
const TCTest = (() => {
  const CSS = `
#tcOv .tctt{flex:none;height:34px;padding:0 10px;border-radius:17px;border:2px dashed #b98a4a;background:#fff4d6;color:#7a4520;font:700 13px/1 "BIZ UDPGothic","Hiragino Sans",sans-serif;white-space:nowrap}
#tct{position:absolute;inset:0;z-index:25;display:none;align-items:flex-end;justify-content:center;pointer-events:auto;touch-action:auto;font-family:"BIZ UDPGothic",BIZ,"Hiragino Sans","Noto Sans CJK JP",sans-serif}
#tct .ttk{position:absolute;inset:0;background:rgba(30,18,6,.5)}
#tct .tth{position:relative;width:calc(100% - 16px);height:90%;margin-bottom:8px;background:#fff8ec;border-radius:18px 18px 14px 14px;box-shadow:0 6px 18px rgba(0,0,0,.35);overflow:hidden;display:flex;flex-direction:column}
#tct .ttd{flex:none;display:flex;align-items:center;justify-content:space-between;padding:10px 12px 8px;background:linear-gradient(#f6e3bf,#efd6a8);border-bottom:2px dashed #b98a4a}
#tct .ttd b{font-size:16px;color:#6b3f1d;letter-spacing:.03em}
#tct .ttx{width:34px;height:34px;border-radius:50%;background:#fff8ec;border:2px solid #d9b77c;color:#8a5a2a;font:400 17px/1 "BIZ UDPGothic","Hiragino Sans",sans-serif;padding:0}
#tct .tty{flex:1 1 auto;min-height:0;overflow-y:auto;-webkit-overflow-scrolling:touch;padding:8px 10px 28px}
#tct .ttn{background:#fff;border:1.5px solid #ead7b2;border-radius:10px;padding:7px 9px;margin:0 0 8px;font-size:12px;line-height:1.55;color:#5a3a1c}
#tct .ttn b{color:#c2456f}
#tct .tts{background:#fffdf7;border:1.5px solid #ead7b2;border-radius:12px;padding:8px 9px 9px;margin:0 0 9px}
#tct h3{margin:0 0 4px;font:700 14px/1.4 "BIZ UDPGothic","Hiragino Sans",sans-serif;color:#6b3f1d}
#tct p{margin:2px 0 5px;font-size:11.5px;line-height:1.5;color:#7a5a3a}
#tct .ttg{margin:8px 0 4px;font-size:12px;font-weight:700;color:#8a5a12}
#tct .ttr{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
#tct .ttr + .ttr{margin-top:5px}
#tct .ttl{flex:none;font:400 11.5px/1.3 "BIZ UDPGothic","Hiragino Sans",sans-serif;color:#7a5a3a;white-space:nowrap}
#tct .ttl.w{min-width:132px}
#tct .ttb{min-height:36px;padding:0 10px;border-radius:10px;border:1.5px solid #d9b77c;background:#fff4dc;color:#6b3f1d;font:700 13px/1.2 "BIZ UDPGothic","Hiragino Sans",sans-serif;-webkit-tap-highlight-color:transparent}
#tct .ttb:active{background:#f3dba8}
#tct .ttb.v{border-color:#a985d6;background:#f3e9ff;color:#5b3690}
#tct .ttb.k{border-color:#d9a443;background:#fff1c4;color:#7a5208}
#tct .ttb.n{border-color:#c9c0b2;background:#f6f2ea;color:#6a5a48}
#tct .ttb.z{border-color:#8a78e0;background:#eef0ff;color:#3f3690}
#tct .ttb.sw{width:100%;text-align:left;border-style:dashed;background:#fff}
#tct .ttb.sw[aria-pressed="true"]{border-style:solid;border-color:#3f9f5a;background:#eaf7ea;color:#2c6a3a}
`;
  const P = v => Number(v).toLocaleString('ja-JP') + 'P';
  // 当たりの 表：tc_app.js の PRIZES・RT・PRIZES_VISIT と 同じ 数（test_tc_test.py が 見くらべる）
  const PTS = [10, 20, 50, 100, 200, 300];
  const RTS = { normal: [['normal', 800, 1600], ['maboroshi', 1600, 3200], ['kamisama', 3200, 6400]],
    maboroshi: [['maboroshi', 800, 1600], ['maboroshi', 1600, 3200], ['maboroshi', 3200, 6400]],
    kamisama: [['kamisama', 2000, 4000], ['kamisama', 5000, 10000], ['kamisama', 10000, 20000]] };
  // 第4.165版：ポイント特化ゾーン（tc_app.js の ZONE と 同じ 数：スタート 1,000P・1回 ＋2,000P・12回で MAX）。えらべる 上乗せの 回数
  const ZNS = [0, 1, 3, 6, 11, 12], ZV = n => 1000 + 2000 * n, ZMAX = 12;
  const znName = z => z.n == null ? '特化ゾーン（上乗せは くじどおり）' : `特化ゾーン 上乗せ ${z.n}回${z.n >= ZMAX ? '（MAX）' : ''} → ${P(ZV(z.n))}`;
  const HORSE = { normal: 'いつもの 馬', maboroshi: '幻の馬', kamisama: '神様馬' };
  // 第4.173版：お世話チャレンジの 1こめの 玉（色の 番号・名前・中身：tc_app.js の TEST.drop の 番号と 同じ）
  const DROPS = [[1, '青', '100P'], [2, '緑', 'ルーレット 800か1600'], [3, '紫', 'ルーレット 1600か3200'], [4, '赤', 'ルーレット 3200か6400'], [5, '金', '特化ゾーン'], [6, '虹', 'チケット']];
  const CALL = { come: '近づいてくる', turn: '振り向く', amae: '甘える' };
  const FLAG = { gold: '金のニンジン', beg: 'おかわりの目', rare: '首を かしげる', nibble: 'ほうきを かじる', win: 'ハートの 抽選', call: '呼ぶ' };
  const zName = z => z === undefined ? 'くじ（本番と 同じ 確率）' : !z ? 'はずれ（当たりなし）' : z.k === 'pt' ? P(z.v) : z.k === 'tk' ? `チケット ${z.n}枚` : z.k === 'zn' ? znName(z)
    : `ルーレット（${P(z.v[0])} か ${P(z.v[1])}）→ ${P(z.v[z.win ? 1 : 0])}`;
  // フィールドの お知らせ用（1行は 短く：お知らせの 札は 画面の 半分の 幅）
  const zLines = z => !z ? 'はずれ（当たりなし）' : z.k === 'pt' ? `${P(z.v)} が 当たる` : z.k === 'tk' ? `チケット ${z.n}枚` : z.k === 'zn' ? (z.n == null ? 'ポイント特化ゾーン\n（上乗せは くじどおり）' : `ポイント特化ゾーン\n上乗せ ${z.n}回${z.n >= ZMAX ? '（MAX）' : ''}\n→ ${P(ZV(z.n))}`) : `ルーレット\n${P(z.v[0])} か ${P(z.v[1])}\n→ ${P(z.v[z.win ? 1 : 0])}`;
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const btn = (txt, a, o, cls) => `<button type="button" class="ttb${cls ? ' ' + cls : ''}" data-a="${a}"${o ? ` data-o="${esc(JSON.stringify(o))}"` : ''}>${txt}</button>`;
  const rtRows = (h, cls) => RTS[h].map(([tier, a, b]) => `<div class="ttr"><span class="ttl w">${P(a)} か ${P(b)} →</span>`
    + [0, 1].map(w => btn(P(w ? b : a), 'prize', { h, z: { k: 'rt', tier, v: [a, b], win: w } }, cls)).join('') + '</div>').join('');
  // 第4.165版：えらんだら すぐ PUSH を 出す（お世話を とばす）。端末に おぼえる（はじめは オン）
  const SKIP_KEY = 'tengel.tctest.skip';
  let skip = true; try { skip = localStorage.getItem(SKIP_KEY) !== '0'; } catch (e) { skip = true; }
  const skipLabel = () => (skip ? '☑' : '☐') + ' えらんだら すぐ PUSH を 出す（ごはん・おそうじを とばす）';
  const BODY = () => `<div class="ttn" data-now></div>`
    + `<div class="tts" data-sec="horse"><h3>① 馬を かえる（出現の テスト）</h3>`
    + `<p>本番と 同じ 流れ（リセットの 抽選で 当たった とき）で やってくるよ。来てから 30分・お世話 5回 → 5分で 帰る のも 本番と 同じ。</p>`
    + `<div class="ttr">${btn('🌙 幻の馬を 出す', 'visit', { k: 'maboroshi' }, 'v')}${btn('✨ 神様馬を 出す', 'visit', { k: 'kamisama' }, 'k')}${btn('いつもの 馬に もどす', 'visit', { k: null }, 'n')}</div></div>`
    + `<div class="tts" data-sec="prize"><h3>② 次の PUSH の 当たり（ごはん・おそうじの あと）</h3>`
    + `<p>えらんだ 当たりが、次に PUSH を 押した 1回 だけ 出るよ（そのあとは いつもの くじ）。その 当たりが 出る 馬が いない ときは、先に 馬が かわるよ。お世話トークンが 0 の ときは 25こに するよ。</p>`
    + `<div class="ttr"><button type="button" class="ttb sw" data-a="skip" aria-pressed="${skip}">${skipLabel()}</button></div>`
    + `<p>オンの とき：えらぶと PUSH が すぐ 出るよ（押すと その 当たり）。オフの とき：そのまま ごはん・おそうじを すると、あとの PUSH で 出るよ。</p>`
    + `<div class="ttr">${btn('くじに もどす', 'prize', { z: 'lot' }, 'n')}${btn('はずれ', 'prize', { z: null }, 'n')}${btn('PUSH を すぐ 出す', 'push', null, 'n')}</div>`
    + `<div class="ttg">いつもの 馬</div>`
    + `<div class="ttr"><span class="ttl">ポイント</span>${PTS.map(v => btn(P(v), 'prize', { h: 'normal', z: { k: 'pt', v } })).join('')}</div>`
    + `<div class="ttr"><span class="ttl">ルーレット（どちらに 止まるかも えらぶ）</span></div>` + rtRows('normal')
    + `<div class="ttr"><span class="ttl">チケット</span>${[1, 2, 3].map(n => btn(n + '枚', 'prize', { h: 'normal', z: { k: 'tk', n } })).join('')}</div>`
    + `<div class="ttg">🌈 ポイント特化ゾーン（上乗せ できる 回数を えらぶ・いまの 馬の まま 出る）</div>`
    + `<div class="ttr">${ZNS.map(n => btn(`${n}回${n >= ZMAX ? '（MAX）' : ''} → ${P(ZV(n))}`, 'prize', { z: { k: 'zn', n } }, 'z')).join('')}${btn('くじどおり（1回ごとに 60%）', 'prize', { z: { k: 'zn' } }, 'z')}</div>`
    + `<p>本番は PUSH 1回ごとに 1/699 で 入るよ。レバーを タップ → 60% で ＋2,000P 上乗せ・失敗で おわり・12回 つづけて 上乗せで MAX 25,000P。</p>`
    + `<div class="ttg">🌙 幻の馬が いる 間の ルーレット（押すと 幻の馬が 来る）</div>` + rtRows('maboroshi', 'v')
    + `<div class="ttg">✨ 神様馬が いる 間の ルーレット（押すと 神様馬が 来る）</div>` + rtRows('kamisama', 'k') + `</div>`
    + `<div class="tts" data-sec="other"><h3>③ そのほかの 当たり・めずらしい 動き</h3>`
    + `<p>どれも 次の 1回 だけ。</p>`
    + `<div class="ttg">撫でる（ハート 10この 抽選）</div>`
    + `<div class="ttr">${btn('当たり → ぴょん！（トークン +5）', 'heart', { win: true })}${btn('ハズレ → ふぅ〜', 'heart', { win: false })}</div>`
    + `<p>ハートを 9こに するよ。1回 なでる（3回 なぞる）と 抽選が 始まるよ。お世話トークンが 20こ以上の ときは、10こ たまっても 抽選は 待ち（PUSH を 押して 20こを 切ると 始まる）。すぐ ためす ときは 下の「19こに」。</p>`
    + `<div class="ttr">${btn('首を かしげる「？」', 'flag', { k: 'rare', v: true })}</div>`
    + `<div class="ttg">ごはん</div>`
    + `<div class="ttr">${btn('金のニンジン（なかよし +3）', 'flag', { k: 'gold', v: true })}${btn('おかわりの目', 'flag', { k: 'beg', v: true })}</div>`
    + `<div class="ttg">おそうじ</div>`
    + `<div class="ttr">${btn('ゴミを 出す', 'trash')}${btn('うんちを させる', 'poop', { gold: false })}${btn('金のうんちを させる', 'poop', { gold: true })}${btn('ほうきを かじる', 'flag', { k: 'nibble', v: true })}</div>`
    + `<div class="ttg">呼ぶ</div>`
    + `<div class="ttr">${Object.keys(CALL).map(k => btn(CALL[k], 'flag', { k: 'call', v: k })).join('')}</div>`
    + `<div class="ttg">チャンス・トークン</div>`
    + `<div class="ttr">${btn('高確ゾーン（お世話 5回）', 'high')}${btn('お世話トークンを 25こに', 'tokens')}${btn('お世話トークンを 19こに', 'tokens', { n: 19 })}${btn('お世話トークンを 0こに', 'tokens', { n: 0 })}${btn('トークンの 時計を 5分 進める（＋5）', 'ahead')}</div>`
    + `<p>お世話トークンの 購入は、下の 列の 1番 右の「お世話トークン購入」から（テスト版の ポイントで 買えるよ。ポイントは 設定の「テスト版の道具」で 足せるよ）。</p></div>`
    // 第4.173版：お世話チャレンジ（玉を 落とす 台：tc_drop.js）。お世話を とばして 台を すぐ 開く・玉ごとの 馬バレの 色を えらぶ（中身は 本番の 当たり：tc_app.js の TEST.drop）
    + `<div class="tts" data-sec="drop"><h3>④ お世話チャレンジ（玉を 落とす 台）</h3>`
    + `<p>お世話を とばして 台を すぐ 開くよ。えらんだ 色の 馬バレが 玉の 順に 出る（中身は 本番の 当たり：「保留結果を見る」で 本番と 同じ ように 受け取る）。えらんで いない 玉は いつもの くじ。お世話トークンが 5こ ない ときは 25こに するよ。</p>`
    + `<div class="ttr">${btn('くじどおりで 開く', 'drop', { l: [] }, 'n')}${btn('ぜんぶ はずれ', 'drop', { l: [0, 0, 0, 0, 0] }, 'n')}</div>`
    + `<div class="ttg">1こめの 玉の 馬バレ（いつもの 馬）</div>`
    + `<div class="ttr">${DROPS.map(([c, nm, what]) => btn(`${nm}（${what}）`, 'drop', { l: [c], h: 'normal' })).join('')}</div>`
    + `<div class="ttg">5こ まとめて（いつもの 馬）</div>`
    + `<div class="ttr">${btn('青 → 緑 → 紫 → 赤 → 金', 'drop', { l: [1, 2, 3, 4, 5], h: 'normal' })}${btn('虹 → はずれ → 青 → 金 → 赤', 'drop', { l: [6, 0, 1, 5, 4], h: 'normal' })}${btn('青 5こ（10・50・100・200・300P）', 'drop', { l: [10, 50, 100, 200, 300].map(v => ({ k: 'pt', v })), h: 'normal' })}</div>`
    + `<div class="ttg">馬が いる 間の ルーレット（押すと その 馬が 来る）</div>`
    + `<div class="ttr">${btn('🌙 金（幻の馬の ルーレット）', 'drop', { l: [{ k: 'rt', tier: 'maboroshi', v: [800, 1600] }], h: 'maboroshi' }, 'v')}${btn('✨ 虹（神様馬の ルーレット）', 'drop', { l: [{ k: 'rt', tier: 'kamisama', v: [2000, 4000] }], h: 'kamisama' }, 'k')}</div>`
    + `<p>色：青＝10〜300P・緑／紫／赤＝ルーレット（800か1600／1600か3200／3200か6400）・金＝幻の馬の ルーレット と ポイント特化ゾーン・虹＝神様馬の ルーレット と チケット。</p></div>`;

  let root = null, api = null, busy = false;
  function style() { if (!document.getElementById('tct-css')) { const st = document.createElement('style'); st.id = 'tct-css'; st.textContent = CSS; document.head.appendChild(st); } }
  // 上の 帯に 入れる 入口の ボタン（tc_app.js が 画面を 作る ときに よぶ：data-tc="test" を 押すと 道具箱）
  function head() { style(); return `<button type="button" class="tctt" data-tc="test" aria-label="テスト版の道具">🧪 テスト</button>`; }
  function build(el) {
    style();
    root = document.createElement('div'); root.id = 'tct'; root.setAttribute('role', 'dialog'); root.setAttribute('aria-label', 'テスト版の道具');
    root.innerHTML = `<div class="ttk"></div><div class="tth"><div class="ttd"><b>🧪 テスト版の道具</b><button type="button" class="ttx" aria-label="とじる">✕</button></div><div class="tty">${BODY()}</div></div>`;
    el.appendChild(root);
    root.querySelector('.ttx').addEventListener('click', close);
    root.querySelector('.ttk').addEventListener('click', close);
    for (const ev of ['pointerdown', 'pointermove', 'pointerup', 'pointercancel']) root.addEventListener(ev, e => e.stopPropagation());      // 下の フィールド（撫でる・ほうき）へ とどけない
    root.addEventListener('click', e => {
      const b = e.target.closest('.ttb'); if (!b || busy) return;
      if (b.dataset.a === 'skip') { skip = !skip; try { localStorage.setItem(SKIP_KEY, skip ? '1' : '0'); } catch (x) { /* おぼえられなくても 動く */ } b.setAttribute('aria-pressed', String(skip)); b.textContent = skipLabel(); return; }      // スイッチ：道具箱は 閉じない
      act(b.dataset.a, b.dataset.o ? JSON.parse(b.dataset.o) : {});
    });
  }
  const BUSY0 = 'お世話が おわったら\nもう一度 押してね', BUSY_PUSH = '先に PUSH を 押して\nから もう一度\n押してね';      // 第4.159版：お世話の あとの PUSH が 出て いる 間も「途中」
  const busyMsg = () => { try { return api && api.info().push ? BUSY_PUSH : BUSY0; } catch (e) { return BUSY0; } };
  async function act(a, o) {
    busy = true;
    try {
      let m = null;
      if (a === 'visit') {
        close();
        const r = await api.visit(o.k);
        m = r === 'busy' ? busyMsg() : r === 'same' ? `もう ${HORSE[o.k || 'normal']}が\nいるよ` : null;      // 来た・帰った お知らせは 本番の もの（tc_app.js）
      } else if (a === 'prize') {
        close();
        if (o.z === 'lot') { await api.prize(undefined); m = '当たりは\nいつもの くじに\nもどしたよ'; }
        else {
          const before = api.info().visit, r = await api.prize(o.z, o.h), now = api.info().visit;
          // 第4.165版：スイッチが オンなら お世話を とばして PUSH を すぐ 出す（もう 出て いる ときは その PUSH で 出る）
          const pushed = r !== 'busy' && r !== 'off' && skip && (api.info().push || api.push() === 'ok');
          m = r === 'busy' ? busyMsg() : (before !== now ? `${HORSE[now || 'normal']}に\nかわったよ\n` : '') + (pushed ? `PUSH を 押すと\n${zLines(o.z)}` : `次の PUSH は\n（ごはん・おそうじの あと）\n${zLines(o.z)}`);
        }
      } else if (a === 'heart') {
        close();
        const r = api.heart(o.win);
        m = r === 'busy' ? busyMsg() : `ハートを 9こに\nしたよ\n1回 なでると 抽選\n→ ${o.win ? 'ぴょん！' : 'ふぅ〜'}` + (api.info().stock >= 20 ? '\n（いまは トークンが\n20こ以上：抽選は\n20こを 切ってから）' : '');
      } else if (a === 'flag') {
        close(); api.flag(o.k, o.v);
        m = o.k === 'gold' ? '次の ニンジンは\n金のニンジンだよ\n（ごはんで\nニンジンを えらぶ）'
          : o.k === 'beg' ? '次の ごはんの あと\n「おかわりの目」が\n出るよ'
          : o.k === 'rare' ? '次に なでると\n首を かしげるよ'
          : o.k === 'nibble' ? '次の おそうじで\nほうきを かじるよ\n（馬の 顔の 近くで\n2つ目を 片付ける）'
          : `次の「呼ぶ」は\n「${CALL[o.v]}」だよ`;
      } else if (a === 'trash') {
        close(); const r = api.trash();
        m = r === 'busy' ? busyMsg() : r === 'have' ? 'ゴミは もう\n出て いるよ' : null;      // 出た お知らせは 本番の もの
      } else if (a === 'poop') {
        close(); const r = api.poop(o.gold);
        m = r === 'busy' ? busyMsg() : r === 'full' ? 'うんちは 3こまで\n（先に おそうじ）'
          : (o.gold ? 'もうすぐ\n金のうんちを するよ\n（おそうじ すると\n高確ゾーン）' : 'もうすぐ\nうんちを するよ');
      } else if (a === 'high') { close(); api.high(); m = '高確ゾーン\n（お世話 5回）を\nつけたよ'; }
      else if (a === 'tokens') { close(); api.tokens(o.n); m = `お世話トークンを\n${o.n == null ? 25 : o.n}こに したよ`; }
      else if (a === 'push') { close(); const r = api.info().push ? 'have' : api.push(); m = r === 'busy' ? busyMsg() : r === 'have' ? 'PUSH は もう\n出て いるよ' : 'PUSH を 出したよ\n（お世話を とばした）'; }
      else if (a === 'ahead') { close(); const r = api.ahead(5); m = r === 'max' ? 'お世話トークンは\nもう 最大だよ' : 'トークンの 時計を\n5分 進めたよ\n（＋5）'; }
      else if (a === 'drop') { close(); const r = await api.drop(o.l || [], true, o.h); m = r === 'busy' ? busyMsg() : r === 'none' ? 'お世話チャレンジの\n絵が 入って いないよ' : null; }      // 第4.173版：台を すぐ 開く
      if (m) api.msg('🧪 ' + m, 3.6);
    } catch (e) { try { api.msg('🧪 うまく\nいかなかったよ', 3.4); } catch (x) { /* なし */ } }
    finally { busy = false; }
  }
  function paintNow() {
    const el = root && root.querySelector('[data-now]'); if (!el || !api) return;
    const i = api.info(), fl = Object.keys(i.flags || {}).map(k => k === 'call' ? `呼ぶ＝${CALL[i.flags.call]}` : k === 'win' ? `ハートの 抽選＝${i.flags.win ? 'ぴょん！' : 'ふぅ〜'}` : FLAG[k] || k);
    if (i.gold) fl.push('金のうんち');
    el.innerHTML = `いまの 馬：<b>${i.visit ? `${i.visit === 'kamisama' ? '✨ ' : '🌙 '}${HORSE[i.visit]}</b>（のこり ${Math.ceil((i.left || 0) / 60)}分）` : `${HORSE.normal}</b>（${esc(i.color)}・お世話 ${i.cares}回）`}<br>`
      + `トークン ${i.stock}・ハート ${i.heart}・高確 ${i.high}・ゴミ ${i.trash}・うんち ${i.poops}・チケット ${i.tickets}<br>`
      + `次の PUSH（ごはん・おそうじの あと）：<b>${esc(zName(i.prize))}</b>`
      + (fl.length ? `<br>次の 1回：<b>${esc(fl.join('・'))}</b>` : '');
  }
  function open(el, a) { api = a; if (!root) build(el); paintNow(); root.querySelector('.tty').scrollTop = 0; root.style.display = 'flex'; }
  function close() { if (root) root.style.display = 'none'; }
  function isOpen() { return !!root && root.style.display !== 'none'; }
  return { open, close, isOpen, head, PTS, RTS, ZNS, ZV, DROPS, zName, get skip() { return skip; }, get el() { return root; } };
})();
