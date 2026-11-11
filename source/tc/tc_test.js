// トレーニングセンター：テスト版の 道具箱（第4.154版・まさちゃん 2026/11/11 20:00「テスト版で、トレーニングセンターの幻の馬と神様馬の出現テストできるようにして！
//   お世話の当選パターン全種類テストできるようにして！」）
//   ・テスト版（TENGEL_TEST=1 で 作った アプリ）の tc_bundle.js に だけ 入る（build_pwa.py）。App Store版の 中身には 入らない
//   ・上の 帯の「🧪 テスト」→ 紙の 道具箱（下へ スクロール）。ボタンを 押すと とじて、フィールドに お知らせ → そのまま お世話を すると その 結果が 出る
//   ・馬：本番と 同じ 流れで やってくる／帰る（tc_app.js の TEST.visit）
//   ・ごはん・おそうじの 当たり：次の 1回 だけ 決める（TEST.prize）。その 当たりが 出る 馬（いつもの 馬・幻の馬・神様馬）が いない ときは 先に 入れかえる ＝ 本番で 起きる 組み合わせ だけ
//   ・そのほか：ハート 10この 抽選（ぴょん／ごろん）・金のニンジン・おかわりの目・首を かしげる・ほうきを かじる・呼ぶの 3つ・ゴミ・うんち・金のうんち・高確ゾーン・トークン
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
`;
  const P = v => Number(v).toLocaleString('ja-JP') + 'P';
  // 当たりの 表：tc_app.js の PRIZES・RT・PRIZES_VISIT と 同じ 数（test_tc_test.py が 見くらべる）
  const PTS = [10, 20, 50, 100, 200, 300];
  const RTS = { normal: [['normal', 800, 1600], ['maboroshi', 1600, 3200], ['kamisama', 3200, 6400]],
    maboroshi: [['maboroshi', 800, 1600], ['maboroshi', 1600, 3200], ['maboroshi', 3200, 6400]],
    kamisama: [['kamisama', 2000, 4000], ['kamisama', 5000, 10000], ['kamisama', 10000, 20000]] };
  const HORSE = { normal: 'いつもの 馬', maboroshi: '幻の馬', kamisama: '神様馬' };
  const CALL = { come: '近づいてくる', turn: '振り向く', amae: '甘える' };
  const FLAG = { gold: '金のニンジン', beg: 'おかわりの目', rare: '首を かしげる', nibble: 'ほうきを かじる', win: 'ハートの 抽選', call: '呼ぶ' };
  const zName = z => z === undefined ? 'くじ（本番と 同じ 確率）' : !z ? 'はずれ（当たりなし）' : z.k === 'pt' ? P(z.v) : z.k === 'tk' ? `チケット ${z.n}枚`
    : `ルーレット（${P(z.v[0])} か ${P(z.v[1])}）→ ${P(z.v[z.win ? 1 : 0])}`;
  // フィールドの お知らせ用（1行は 短く：お知らせの 札は 画面の 半分の 幅）
  const zLines = z => !z ? 'はずれ（当たりなし）' : z.k === 'pt' ? `${P(z.v)} が 当たる` : z.k === 'tk' ? `チケット ${z.n}枚` : `ルーレット\n${P(z.v[0])} か ${P(z.v[1])}\n→ ${P(z.v[z.win ? 1 : 0])}`;
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const btn = (txt, a, o, cls) => `<button type="button" class="ttb${cls ? ' ' + cls : ''}" data-a="${a}"${o ? ` data-o="${esc(JSON.stringify(o))}"` : ''}>${txt}</button>`;
  const rtRows = (h, cls) => RTS[h].map(([tier, a, b]) => `<div class="ttr"><span class="ttl w">${P(a)} か ${P(b)} →</span>`
    + [0, 1].map(w => btn(P(w ? b : a), 'prize', { h, z: { k: 'rt', tier, v: [a, b], win: w } }, cls)).join('') + '</div>').join('');
  const BODY = () => `<div class="ttn" data-now></div>`
    + `<div class="tts" data-sec="horse"><h3>① 馬を かえる（出現の テスト）</h3>`
    + `<p>本番と 同じ 流れ（リセットの 抽選で 当たった とき）で やってくるよ。来てから 30分・お世話 5回 → 5分で 帰る のも 本番と 同じ。</p>`
    + `<div class="ttr">${btn('🌙 幻の馬を 出す', 'visit', { k: 'maboroshi' }, 'v')}${btn('✨ 神様馬を 出す', 'visit', { k: 'kamisama' }, 'k')}${btn('いつもの 馬に もどす', 'visit', { k: null }, 'n')}</div></div>`
    + `<div class="tts" data-sec="prize"><h3>② 次の ごはん・おそうじの 当たり</h3>`
    + `<p>えらんだ 当たりが、次の 1回 だけ 出るよ（そのあとは いつもの くじ）。その 当たりが 出る 馬が いない ときは、先に 馬が かわるよ。お世話トークンが 0 の ときは 20こに、ねて いる 馬は 起こすよ。</p>`
    + `<div class="ttr">${btn('くじに もどす', 'prize', { z: 'lot' }, 'n')}${btn('はずれ', 'prize', { z: null }, 'n')}</div>`
    + `<div class="ttg">いつもの 馬</div>`
    + `<div class="ttr"><span class="ttl">ポイント</span>${PTS.map(v => btn(P(v), 'prize', { h: 'normal', z: { k: 'pt', v } })).join('')}</div>`
    + `<div class="ttr"><span class="ttl">ルーレット（どちらに 止まるかも えらぶ）</span></div>` + rtRows('normal')
    + `<div class="ttr"><span class="ttl">チケット</span>${[1, 2, 3].map(n => btn(n + '枚', 'prize', { h: 'normal', z: { k: 'tk', n } })).join('')}</div>`
    + `<div class="ttg">🌙 幻の馬が いる 間の ルーレット（押すと 幻の馬が 来る）</div>` + rtRows('maboroshi', 'v')
    + `<div class="ttg">✨ 神様馬が いる 間の ルーレット（押すと 神様馬が 来る）</div>` + rtRows('kamisama', 'k') + `</div>`
    + `<div class="tts" data-sec="other"><h3>③ そのほかの 当たり・めずらしい 動き</h3>`
    + `<p>どれも 次の 1回 だけ。</p>`
    + `<div class="ttg">撫でる（ハート 10この 抽選）</div>`
    + `<div class="ttr">${btn('当たり → ぴょん！（トークン +5）', 'heart', { win: true })}${btn('ハズレ → ごろん', 'heart', { win: false })}</div>`
    + `<p>ハートを 9こに するよ。1回 なでる（3回 なぞる）と 抽選が 始まるよ。</p>`
    + `<div class="ttr">${btn('首を かしげる「？」', 'flag', { k: 'rare', v: true })}</div>`
    + `<div class="ttg">ごはん</div>`
    + `<div class="ttr">${btn('金のニンジン（なかよし +3）', 'flag', { k: 'gold', v: true })}${btn('おかわりの目', 'flag', { k: 'beg', v: true })}</div>`
    + `<div class="ttg">おそうじ</div>`
    + `<div class="ttr">${btn('ゴミを 出す', 'trash')}${btn('うんちを させる', 'poop', { gold: false })}${btn('金のうんちを させる', 'poop', { gold: true })}${btn('ほうきを かじる', 'flag', { k: 'nibble', v: true })}</div>`
    + `<div class="ttg">呼ぶ</div>`
    + `<div class="ttr">${Object.keys(CALL).map(k => btn(CALL[k], 'flag', { k: 'call', v: k })).join('')}</div>`
    + `<div class="ttg">チャンス・トークン</div>`
    + `<div class="ttr">${btn('高確ゾーン（お世話 5回）', 'high')}${btn('お世話トークンを 20こに', 'tokens')}</div></div>`;

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
    root.addEventListener('click', e => { const b = e.target.closest('.ttb'); if (b && !busy) act(b.dataset.a, b.dataset.o ? JSON.parse(b.dataset.o) : {}); });
  }
  const BUSY = 'お世話が おわったら\nもう一度 押してね';
  const WOKE = '\n（ねて いる 馬を\n起こすよ）';          // 夜は 馬が ねる：ねて いる 間は お世話が 始まらない ので 起こす
  async function act(a, o) {
    busy = true;
    try {
      let m = null;
      if (a === 'visit') {
        close();
        const r = await api.visit(o.k);
        m = r === 'busy' ? BUSY : r === 'same' ? `もう ${HORSE[o.k || 'normal']}が\nいるよ` : null;      // 来た・帰った お知らせは 本番の もの（tc_app.js）
      } else if (a === 'prize') {
        close();
        if (o.z === 'lot') { await api.prize(undefined); m = '当たりは\nいつもの くじに\nもどしたよ'; }
        else {
          const before = api.info().visit, r = await api.prize(o.z, o.h), now = api.info().visit;
          m = r === 'busy' ? BUSY : (before !== now ? `${HORSE[now || 'normal']}に\nかわったよ\n` : '') + `次の ごはん・\nおそうじは\n${zLines(o.z)}` + (api.wake() ? WOKE : '');
        }
      } else if (a === 'heart') {
        close();
        const r = api.heart(o.win);
        m = r === 'busy' ? BUSY : `ハートを 9こに\nしたよ\n1回 なでると 抽選\n→ ${o.win ? 'ぴょん！' : 'ごろん'}` + (api.wake() ? WOKE : '');
      } else if (a === 'flag') {
        close(); api.flag(o.k, o.v);
        m = o.k === 'gold' ? '次の ニンジンは\n金のニンジンだよ\n（ごはんで\nニンジンを えらぶ）'
          : o.k === 'beg' ? '次の ごはんの あと\n「おかわりの目」が\n出るよ'
          : o.k === 'rare' ? '次に なでると\n首を かしげるよ'
          : o.k === 'nibble' ? '次の おそうじで\nほうきを かじるよ\n（馬の 顔の 近くで\n2つ目を 片付ける）'
          : `次の「呼ぶ」は\n「${CALL[o.v]}」だよ`;
        if (api.wake()) m += WOKE;
      } else if (a === 'trash') {
        close(); const r = api.trash();
        m = r === 'busy' ? BUSY : r === 'have' ? 'ゴミは もう\n出て いるよ' : null;      // 出た お知らせは 本番の もの
      } else if (a === 'poop') {
        close(); const r = api.poop(o.gold);
        m = r === 'busy' ? BUSY : r === 'visit' ? '幻の馬・神様馬は\nうんちを しないよ\n（いつもの 馬に\nもどしてね）' : r === 'full' ? 'うんちは 3こまで\n（先に おそうじ）'
          : (o.gold ? 'もうすぐ\n金のうんちを するよ\n（おそうじ すると\n高確ゾーン）' : 'もうすぐ\nうんちを するよ') + (api.wake() ? WOKE : '');
      } else if (a === 'high') { close(); api.high(); m = '高確ゾーン\n（お世話 5回）を\nつけたよ'; }
      else if (a === 'tokens') { close(); api.tokens(); m = 'お世話トークンを\n20こに したよ'; }
      if (m) api.msg('🧪 ' + m, 3.6);
    } catch (e) { try { api.msg('🧪 うまく\nいかなかったよ', 3.4); } catch (x) { /* なし */ } }
    finally { busy = false; }
  }
  function paintNow() {
    const el = root && root.querySelector('[data-now]'); if (!el || !api) return;
    const i = api.info(), fl = Object.keys(i.flags || {}).map(k => k === 'call' ? `呼ぶ＝${CALL[i.flags.call]}` : k === 'win' ? `ハートの 抽選＝${i.flags.win ? 'ぴょん！' : 'ごろん'}` : FLAG[k] || k);
    if (i.gold) fl.push('金のうんち');
    el.innerHTML = `いまの 馬：<b>${i.visit ? `${i.visit === 'kamisama' ? '✨ ' : '🌙 '}${HORSE[i.visit]}</b>（のこり ${Math.ceil((i.left || 0) / 60)}分）` : `${HORSE.normal}</b>（${esc(i.color)}・お世話 ${i.cares}回）`}<br>`
      + `トークン ${i.stock}・ハート ${i.heart}・高確 ${i.high}・ゴミ ${i.trash}・うんち ${i.poops}・チケット ${i.tickets}<br>`
      + `次の ごはん・おそうじ：<b>${esc(zName(i.prize))}</b>`
      + (fl.length ? `<br>次の 1回：<b>${esc(fl.join('・'))}</b>` : '');
  }
  function open(el, a) { api = a; if (!root) build(el); paintNow(); root.querySelector('.tty').scrollTop = 0; root.style.display = 'flex'; }
  function close() { if (root) root.style.display = 'none'; }
  function isOpen() { return !!root && root.style.display !== 'none'; }
  return { open, close, isOpen, head, PTS, RTS, zName, get el() { return root; } };
})();
