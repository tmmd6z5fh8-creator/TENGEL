// 馬カードバトルの「対戦の 進め役」（第4.176版）：ルール（cb_rules.js）と 画面（cb_app.js）の あいだ
//   まさちゃん 2026/11/15 21:54「・コンピュータと対戦 ・部屋を作成して、友達と対戦 これをやりたい！」
//
//   対戦の 中身（山札の 並び・2人の 手札）は「親」だけが 持つ：
//     ・コンピュータと 対戦：この 端末が 親。相手の 席に コンピュータ（cb_cpu.js）が すわる
//     ・部屋を 作った 人（ホスト）：この 端末が 親。友だち（ゲスト）には「友だちに 見せて いい こと」だけを 送る（CBRules.view・evFor）
//     ・部屋に 入った 人（ゲスト）：自分の 手を 親に 送って、見せて もらった ものを 画面に 出す だけ
//   どの 形でも 画面からは 同じ 使い方（match）：
//     match.kind（'cpu'・'host'・'guest'）・match.onUpdate＝{ ev, view } を 受ける 関数・match.onState＝つながりの できごと（'again'：相手が もう 1回・'lost'：切れた・'bye'：相手が やめた・'ver'：版が ちがう）
//     match.start()・match.act(a) → Promise<{ ok, why }>・match.again()（もう 1回）・match.idle()（画面の 動きが 終わった：コンピュータは ここから 考える）・match.leave()
//
//   つなぎ方（link）は 部品を さしかえる：{ send(文字), onText＝受けた 文字を もらう 関数, onLost＝切れた, close() }
//     ・近くの 友だち（アプリ）：CBNet.nativeRoom()（Swift の Room.swift：iPhone どうしが 直接 つながる・サーバーなし）
//     ・テスト：2つの 画面を じかに つなぐ（test_cb.py）
//   やりとり する もの（JSON の 文字・1つ 20KB まで）：
//     { t:'hello', v }（はじめに おたがいに。版が ちがえば 対戦しない）・{ t:'up', n, ev, view }（親 → ゲスト）・{ t:'act', id, a }（ゲスト → 親）・{ t:'ack', id, ok, why }（親 → ゲスト）
//     { t:'again' }（もう 1回）・{ t:'bye' }（やめる）
//   第4.179版（まさちゃん 2026/11/16 15:47「お友達と部屋を作る際に、参加ポイントと勝利者獲得ポイントを設定できるようにして！」→ 16:01「1にしよう！」＝バトルコイン・
//     16:18「お友達との部屋を作成する場合は、バトルコインで参加枚数を指定する・勝者獲得コインは、参加枚数の2倍まで」）：
//     ・部屋を 作った 人（ホスト）が 決めた「参加コイン e・勝者の 獲得コイン w」を、あいさつ（hello）で ゲストに 伝える：{ t:'hello', v, stake:{ e, w } }
//     ・ゲストは それを 見て「参加する」と 答える：{ t:'join', stake:{ e, w } }（同じ 数字を 返す）。ホストは それが 届いて から 配る（参加コインが 0 の 部屋は ゲストが すぐ 答える）
//     ・コインの 数は それぞれの 端末が 自分で 数える（画面の 係＝cb_app.js）。ここは 決まりを 伝える だけ（match.stake・onState('stake')・match.join()）
//   第4.183版（まさちゃん 2026/11/16 20:53「②お友達バトルの時は、それぞれがカスタムしている背面デザイン、カードデザインにして！」）：
//     ・あいさつ（hello）に 自分が えらんだ デザイン：{ t:'hello', v, dz:{ b：うらの 名前, f：{ カードの 種類：おもての 名前 } } }（ゲスト → ホスト・ホスト → ゲスト）
//     ・届いた 相手の デザインは match.opDz（dzOf で 形だけ たしかめる：名前は 英小文字・数字 1〜12字・種類は CBRules.KINDS。ない 名前は 画面の 係が いつもの デザインに する）
//     ・前の 版（第4.181版・第4.182版）は dz を 送らない・読まない だけ。でも 第4.183版は ルールも かわった（4 の 効果で 交換して 5 を 出したら 5 の 効果：まさちゃん 21:24）ので PROTO 6
//   第4.185版（7 の 4まい 公開で 強さ 逆転：ルールが かわった）：PROTO 7（前の 版の アプリとは 対戦しない）
//   第4.187版（7 の 4まい 公開は セットの 前〈手 x7r〉・相手の 場の カードは いつも うら・どれを セットしたか 手札の 見え方で わからない：ルールが かわった）：PROTO 8
//   第4.188版（効果タイムで 行う 順 6 → 7 → 3 → 5 → 4：手札の 効果が 先・4 は いちばん あと・ルールが かわった）：PROTO 9
//   第4.190版（6 の 効果は ターンの はじめ〈セットの 前・神様馬／幻の馬より 先：手 p6〉・効果タイムは 1つずつ〈7 → 3 → 5 → 4〉：ルールが かわった）：PROTO 10
//     ・1ターン目の はじめに 6 の 効果を 聞く ときは、配った（deal）あとの 同じ 知らせに 入れる（S.ev0 → sixt）
//   第4.197版（まさちゃん 2026/11/18 18:58「呼び寄せの決戦宝石 決戦調査とお友達バトルの設定で、決戦宝石ありにした場合のみ使用可能…お友達バトルのトークンは、1人その試合で持ち込めるのは、一つの石まで
//     お互いに何の石を所有してるか見える」）：ルールが かわった（手 gem・トークン）ので PROTO 11
//     ・部屋を 作った 人（ホスト）が「決戦宝石 あり／なし」を 決める → あいさつ（hello）で ゲストに 伝える：{ t:'hello', v, stake, dz, gm:{ on } }
//     ・まさちゃん 20:21「お友達バトルは1試合で5個使える！」：あり の 部屋は 2人とも 5つ ぜんぶ（1試合で 1つ 1回ずつ）＝ 持ち込む 宝石を えらぶ のは なくした（前の「1人 1つ」）
//     ・ゲストは 決まりを 見て「参加する」：{ t:'join', stake }。ホストは 2人に 5つずつで 配る（opt.gems＝[[5つ],[5つ]]・opt.gpub＝おたがいに 見える）。match.gm＝部屋の 決まり（画面の 係が 見せる）
//   第4.199版（まさちゃん 22:01「7トークンを1枚見せて…捨てることで、3枚引けるって効果ね！」：7トークンで 7 の 3まい 交換は 見せて 捨てる＝ルールが かわった）：PROTO 12
//   第4.202版（まさちゃん 23:42「手札から使える効果は、カードセット前に使えるようにして！」・23:55「５ターンのうち、どちらかが３ターン勝利したら、試合終了にして！」）：
//     7 の 3まい 交換・3 の 交換は セットの 前（手 x7・x3）・効果タイムは 5 → 4 だけ・決着したら その ターンで おわり（ルールが かわった）：PROTO 13
//   第4.211版（まさちゃん 2026/11/22 21:36「不正にポイントやバトルコイン、お世話トークンを手に入れる抜け穴は無いか全部細かく徹底的に確認して！」）：部屋の 相手は「本物の アプリ」とは かぎらない
//     （サーバーを 使わない ので たしかめられない：同じ つなぎ方を まねた にせものの 相手を 作れる 人が いる）→ 相手から 届いた ものは 形を たしかめて から 使う：
//     ・届いた 知らせ（up の ev・view／ack の why／ゲストの 手 act）は、数・はい いいえ・null・短い 英数字（SAFE）だけで できて いる こと（clean）。それ 以外（タグに なる 字・長い 字・深い 入れ子）が
//       1つでも あれば 使わない：ゲストは 対戦を そこで 終える（onState('bad')：勝ち負けに 数えない・参加コインは もどる）・ホストは その 手を ことわる
//     ・ゲストは、自分が カードを 3回 セットして から で ないと「対戦が 終わった」（end）を 受けとらない（MIN_SETS：どの 対戦も 3ターンは ある）。
//       前は にせものの ホストが「配った → あなたの 勝ち」を くり返し 送る だけで、勝ちの 数・お世話トークン・ミッションの 連勝を いくらでも ふやせた
//     ・ゲストは、自分が「参加する」と 答える 前・「もう 1回」を 押す 前に 配られた 対戦（deal）も 受けとらない（決まりを 見て いない のに 参加コインを 出させない）
//     ・参加コインの 上限は 画面で えらべる 数（100枚）まで（前は 届いた 数を 999枚まで 受けとって いた）
const CBNet = (() => {
  'use strict';
  const R = CBRules, PROTO = 13, MAXLEN = 20000;      // PROTO 13（第4.202版）：7 の 3まい 交換・3 は セットの 前・決着したら 試合終了。PROTO 12（第4.199版）：7トークンで 7 の 3まい 交換は 見せて 捨てる。PROTO 11（第4.197版）：決戦宝石（手 gem・トークン・あいさつの gm）。PROTO 10（第4.190版）：6 は セットの 前・効果タイムは 1つずつ。PROTO 9（第4.188版）：効果の 順 6 → 7 → 3 → 5 → 4。PROTO 8（第4.187版）：7 の 4まい 公開は セットの 前（手 x7r）・場の カードは いつも うら。PROTO 7（第4.185版）：7 の 4まい 公開で 強さ 逆転。PROTO 6（第4.183版）：4 の 効果で 交換して 5 を 出したら 5 の 効果（ルールが かわった：phase 'u5'・手 u5）＝ 前の 版の アプリとは 対戦しない。PROTO 5（第4.181版）：2人とも 4 の 効果を 使ったら ドロー（ルールが かわった）＝ 前の 版の アプリとは 対戦しない。PROTO 4（第4.179版）：あいさつに 参加コインの 決まり・「参加する」の 返事が ふえた ＝ 前の 版の アプリとは 対戦しない（「アプリの 版が ちがう」と 出る）。PROTO 3＝第4.178版（5ターン・手札 7まい・逆転勝利）・PROTO 2＝第4.177版
  // 参加コイン e（0〜STAKE_MAX）・勝者の 獲得コイン w（e 〜 e の 2倍）。数字で ない・はんいの 外は 直す（相手から 届いた ものも ここを 通す）
  const STAKE_MAX = 100;                               // 第4.211版：999 → 100（画面で えらべる いちばん 大きい 数：cb_app.js の STAKE_CHIPS）
  function stakeOf(k) {
    const e = Math.max(0, Math.min(STAKE_MAX, Math.floor(+(k && k.e) || 0)));
    const w = Math.max(e, Math.min(e * 2, Math.floor(+(k && k.w) || 0)));
    return { e: e, w: e > 0 ? w : 0 };
  }
  // 決戦宝石（第4.197版）：部屋の 決まり { on }（相手から 届いた ものも ここを 通す）
  const gmOf = o => ({ on: !!o && o.on === true });
  const say = (m, k, v) => { try { if (typeof m[k] === 'function') m[k](v); } catch (e) { /* 画面の 中の まちがいで 対戦を 止めない */ } };
  // デザイン（第4.183版）：{ b, f } の 形に そろえる（相手から 届いた もの・自分の ものも ここを 通す）
  const DZID = /^[a-z0-9]{1,12}$/;
  function dzOf(d) {
    const o = { b: '', f: {} };
    if (!d || typeof d !== 'object') return o;
    if (typeof d.b === 'string' && DZID.test(d.b)) o.b = d.b;
    const f = d.f && typeof d.f === 'object' ? d.f : {};
    R.KINDS.forEach(k => { if (Object.prototype.hasOwnProperty.call(f, k) && typeof f[k] === 'string' && DZID.test(f[k])) o.f[k] = f[k]; });
    return o;
  }

  // 第4.211版：相手から 届いた ものを たしかめる。使って よい 形に 写した もの（だめ なら BAD）
  //   数（−100万〜100万）・はい いいえ・null・短い 英数字（24字 まで）・ならび（64こ まで）・見出しも 短い 英数字（48こ まで）・入れ子は 8段 まで
  const SAFE = /^[A-Za-z0-9_-]{0,24}$/, BAD = {}, MIN_SETS = 3;
  let minSets = MIN_SETS;                              // テスト 用（短い 対戦：3ターンの 形）に だけ かえる（_t.minSets）。アプリの 中では いつも MIN_SETS
  function clean(v, d) {
    if (v === null || typeof v === 'boolean') return v;
    if (typeof v === 'number') return isFinite(v) && Math.abs(v) <= 1e6 ? v : BAD;
    if (typeof v === 'string') return SAFE.test(v) ? v : BAD;
    if (typeof v !== 'object' || d >= 8) return BAD;
    if (Array.isArray(v)) {
      if (v.length > 64) return BAD;
      const a = [];
      for (let i = 0; i < v.length; i++) { const x = clean(v[i], d + 1); if (x === BAD) return BAD; a.push(x); }
      return a;
    }
    const ks = Object.keys(v), o = {};
    if (ks.length > 48) return BAD;
    for (let i = 0; i < ks.length; i++) {
      const k = ks[i]; if (!SAFE.test(k) || k === '__proto__' || k === 'constructor' || k === 'prototype') return BAD;
      const x = clean(v[k], d + 1); if (x === BAD) return BAD;
      o[k] = x;
    }
    return o;
  }
  const isObj = x => !!x && typeof x === 'object' && !Array.isArray(x);
  // 見せて もらった 形（view）と おきた こと（ev）が、画面が 使える 形か
  const viewOk = v => isObj(v) && isObj(v.my) && isObj(v.op) && isObj(v.can) && Array.isArray(v.my.hand) && Array.isArray(v.op.hand) && Array.isArray(v.discard);
  const evOk = ev => Array.isArray(ev) && ev.every(x => isObj(x) && typeof x.e === 'string' && x.e.length > 0);

  // ---------- 親（コンピュータと 対戦・部屋の ホスト）----------
  //   seat1＝相手の 席：{ up(u)（相手に 見せる ものが できた）, idle()（画面が 落ちついた）, stop() }
  function parent(kind, rng, mkSeat, opt) {
    let S = null, seat = null, n = 0, alive = true;
    const m = { kind: kind, me: 0, onUpdate: null, onState: null, wantAgain: [false, false] };
    function push(ev) {
      n += 1;
      say(m, 'onUpdate', { n: n, ev: R.evFor(ev, 0), view: R.view(S, 0) });
      if (seat) seat.up({ n: n, ev: R.evFor(ev, 1), view: R.view(S, 1) });
    }
    function apply(i, a) {
      if (!alive || !S) return { ok: false, why: 'off' };
      const r = R.act(S, i, a, rng);
      if (r.ok) push(r.ev);
      return { ok: r.ok, why: r.why };
    }
    m.start = () => {                                   // opt＝手札を 決めて はじめる（テスト・見本 用）
      if (!alive) return;
      S = R.newGame(rng, opt); m.wantAgain = [false, false]; n = 0;
      const ev0 = S.ev0 || []; delete S.ev0;            // 第4.190版：1ターン目の はじめに おきた こと（6 の 効果を 聞く：sixt）は 配った あとに 見せる
      push([{ e: 'deal' }].concat(ev0));
    };
    m.act = a => Promise.resolve(apply(0, a));
    m.setOpt = o => { opt = o; };                     // 第4.196版：次に 配る ときの 決まり（決戦調査：戦ごとの 敵の 確定カード opt.rig）
    m.idle = () => { if (seat && seat.idle) seat.idle(); };
    m.again = () => {                                   // もう 1回：2人とも 押したら 配り直す（コンピュータは いつでも OK）
      if (!alive || !S || S.phase !== 'end') return;
      m.wantAgain[0] = true; if (seat && seat.again) seat.again();
      if (m.wantAgain[1]) m.start();
    };
    m.leave = () => { if (!alive) return; alive = false; if (seat) seat.stop(true); };
    m._ = { state: () => S, apply: apply, seatAgain: () => { m.wantAgain[1] = true; if (m.wantAgain[0]) m.start(); else say(m, 'onState', 'again'); }, end: why => { if (!alive) return; alive = false; if (seat) seat.stop(false); say(m, 'onState', why); } };
    seat = mkSeat(m);
    return m;
  }

  // コンピュータと 対戦
  function cpu(rng, think, opt) {
    rng = rng || Math.random;
    return parent('cpu', rng, m => {
      let last = null, timer = 0, stopped = false;
      const go = () => {
        timer = 0; if (stopped || !last) return;
        const a = CBCpu.decide(last, rng); if (!a) return;
        m._.apply(1, a);
      };
      return {
        up: u => { last = u.view; },
        // 画面の 動きが 終わって から 考えはじめる（めくる 動きの 間に 次の カードを 出して いた ように 見えない ため）
        idle: () => { if (stopped || timer || !last || !CBCpu.decide(last, () => 0.5)) return; timer = setTimeout(go, think ? think(last) : 700 + Math.floor(rng() * 900)); },
        again: () => { m.wantAgain[1] = true; },
        stop: () => { stopped = true; clearTimeout(timer); }
      };
    }, opt);
  }

  // 部屋の ホスト（親）：link の むこうに 友だち。stake＝{ e:参加コイン, w:勝者の 獲得コイン }（なければ 0）・dz＝自分が えらんだ デザイン（第4.183版）・
  //   gm＝決戦宝石の 決まり { on }（第4.197版：あり なら 2人とも 5つ）
  function host(link, rng, opt, stake, dz, gm) {
    rng = rng || Math.random;
    const stk = stakeOf(stake), myDz = dzOf(dz), gmv = gmOf(gm);
    const mm = parent('host', rng, m => {
      let hello = false, joined = false, closed = false, want = false;
      const send = o => { if (!closed) link.send(JSON.stringify(o)); };
      // 配るのは 友だちの あいさつ（hello：版が 同じ）と「参加する」（join：決まりを 見て 答えた）が 届いて から
      const deal = m.start; m.start = () => { want = true; if (joined) deal(); };
      link.onText = txt => {
        if (closed || typeof txt !== 'string' || txt.length > MAXLEN) return;
        let o; try { o = JSON.parse(txt); } catch (e) { return; }
        if (!o || typeof o !== 'object') return;
        if (o.t === 'hello') { if (o.v !== PROTO) { send({ t: 'hello', v: PROTO }); m._.end('ver'); return; } if (!hello) { hello = true; m.opDz = dzOf(o.dz); send({ t: 'hello', v: PROTO, stake: stk, dz: myDz, gm: gmv }); say(m, 'onState', 'ready'); } return; }
        if (!hello) return;
        if (o.t === 'join') {                           // 友だちが 決まりを 見て「参加する」：同じ 数字で ある こと（ちがえば 配らない）
          const k = stakeOf(o.stake);
          if (!joined && k.e === stk.e && k.w === stk.w) {
            joined = true;
            if (gmv.on) m.setOpt(Object.assign({}, opt || {}, { gems: [R.GEMS.slice(), R.GEMS.slice()], gpub: true }));      // 第4.197版：決戦宝石 あり ＝ 2人とも 5つ（おたがいに 見える）
            say(m, 'onState', 'joined'); if (want) deal();
          }
          return;
        }
        if (o.t === 'bye') { m._.end('bye'); return; }
        if (!joined) return;
        if (o.t === 'act') {                            // 第4.211版：手は 形を たしかめて から ルールへ（おかしな 手・ルールの 中の まちがいで 対戦を 止めない）
          const a = clean(o.a, 0); let r;
          try { r = a === BAD || !isObj(a) ? { ok: false, why: 'arg' } : m._.apply(1, a); } catch (e) { r = { ok: false, why: 'err' }; }
          send({ t: 'ack', id: typeof o.id === 'number' && isFinite(o.id) ? o.id : 0, ok: r.ok, why: r.why });
        } else if (o.t === 'again') m._.seatAgain();
      };
      link.onLost = () => { if (!closed) m._.end('lost'); };
      return {
        up: u => send({ t: 'up', n: u.n, ev: u.ev, view: u.view }),
        again: () => send({ t: 'again' }),
        stop: mine => { if (closed) return; if (mine) send({ t: 'bye' }); closed = true; setTimeout(() => { try { link.close(); } catch (e) { /* なし */ } }, mine ? 250 : 0); }
      };
    }, opt);
    mm.stake = stk; mm.opDz = null; mm.gm = gmv;
    return mm;
  }

  // 部屋の ゲスト：親（ホスト）に 手を 送って、見せて もらった ものを 受ける。dz＝自分が えらんだ デザイン（第4.183版）
  function guest(link, dz) {
    let alive = true, id = 0, hello = false, sets = 0;      // sets（第4.211版）：この 対戦で 自分が セットを 送った 数（画面で カードを 出した 数）
    let joined = false, over = false, again = false;      // 第4.211版：「参加する」と 答えた・対戦が 1つ 終わった・「もう 1回」を 押した
    const wait = new Map(), myDz = dzOf(dz);
    const m = { kind: 'guest', me: 1, onUpdate: null, onState: null, stake: null, opDz: null, gm: null };      // gm：部屋の 決戦宝石の 決まり（第4.197版）
    const send = o => { if (alive) link.send(JSON.stringify(o)); };
    const end = why => { if (!alive) return; alive = false; const fs = Array.from(wait.values()); wait.clear(); fs.forEach(f => f({ ok: false, why: 'off' })); try { link.close(); } catch (e) { /* なし */ } say(m, 'onState', why); };
    link.onText = txt => {
      if (!alive || typeof txt !== 'string' || txt.length > MAXLEN) return;
      let o; try { o = JSON.parse(txt); } catch (e) { return; }
      if (!o || typeof o !== 'object') return;
      if (o.t === 'hello') { if (o.v !== PROTO) end('ver'); else if (!hello) { hello = true; m.stake = stakeOf(o.stake); m.opDz = dzOf(o.dz); m.gm = gmOf(o.gm); say(m, 'onState', 'ready'); say(m, 'onState', 'stake'); } }      // stake：部屋の 決まり（参加コイン・勝者の 獲得コイン）が 届いた → 画面が 聞いて match.join()
      else if (o.t === 'up') {
        // 第4.211版：届いた 知らせは 形を たしかめて から 画面へ。おかしければ 対戦を 終える（'bad'：数えない）
        const ev = clean(o.ev, 0), view = clean(o.view, 0);
        if (!hello || !joined || ev === BAD || view === BAD || !evOk(ev) || !viewOk(view)) return end('bad');      // joined：「参加する」と 答える 前の 知らせは 受けとらない
        // 「配った」（deal）は、はじめの 1回 か、前の 対戦が 終わって 自分が「もう 1回」を 押した あと だけ。
        // 「対戦が 終わった」（end）は、自分が MIN_SETS 回 セットした あと だけ（配り直したら 0 から・受けとったら 0 に）
        for (let i = 0; i < ev.length; i++) {
          if (ev[i].e === 'deal') { if (over && !again) return end('bad'); over = false; again = false; sets = 0; }
          else if (ev[i].e === 'end') { if (over || sets < minSets) return end('bad'); over = true; sets = 0; }
        }
        say(m, 'onUpdate', { n: typeof o.n === 'number' && isFinite(o.n) ? o.n : 0, ev: ev, view: view });
      } else if (o.t === 'ack') { const f = wait.get(o.id); if (f) { wait.delete(o.id); f({ ok: o.ok === true, why: typeof o.why === 'string' && SAFE.test(o.why) ? o.why : '' }); } }
      else if (o.t === 'again') say(m, 'onState', 'again');
      else if (o.t === 'bye') end('bye');
    };
    link.onLost = () => end('lost');
    m.start = () => send({ t: 'hello', v: PROTO, dz: myDz });
    m.join = () => { if (hello && m.stake) { joined = true; send({ t: 'join', stake: m.stake }); } };      // 決まりを 見て「参加する」（ホストは これが 届いて から 配る）
    m.act = a => new Promise(ok => {
      if (!alive) return ok({ ok: false, why: 'off' });
      id += 1; wait.set(id, ok);
      if (a && a.t === 'set') sets += 1;               // 第4.211版：セットを 送った 数（さいごの セットの 返事〈ack〉は「終わった」の 知らせの あとに 届く ので、送った ときに 数える）
      send({ t: 'act', id: id, a: a });
    });
    m.idle = () => { };
    m.again = () => { if (over) again = true; send({ t: 'again' }); };
    m.leave = () => { if (!alive) return; send({ t: 'bye' }); alive = false; setTimeout(() => { try { link.close(); } catch (e) { /* なし */ } }, 250); };
    return m;
  }

  // ---------- 近くの 友だちと つなぐ（アプリ：Swift の Room.swift）----------
  //   nativeRoom().open('host'|'join', 部屋番号) → Promise<link>（つながったら）。onStep(名前)＝とちゅうの 様子（'wait'：さがして いる・待って いる／'found'：見つけた）
  //   やめる とき：cancel()
  function nativeRoom() {
    const N = window.TengelNative;
    let link = null, done = null, fail = null, onStep = null, live = false;
    function onNative(e) {
      const d = e.detail; if (!d || d.name !== 'room' || !live) return;
      const p = d.payload || {};
      if (p.ev === 'state') {
        if (p.state === 'connected' && done) {
          link = { send: txt => { N.call('room', { op: 'send', data: txt }).catch(() => { }); }, onText: null, onLost: null, close: () => { stop(); } };
          const ok = done; done = fail = null; ok(link);
        } else if (p.state === 'idle' && link) { const l = link; link = null; if (l.onLost) l.onLost(); }
        else if (onStep && (p.state === 'hosting' || p.state === 'searching')) onStep('wait');
        else if (onStep && p.state === 'connecting') onStep('found');
      } else if (p.ev === 'data' && link && link.onText) link.onText(String(p.data || ''));
      else if (p.ev === 'error' && fail) { const ng = fail; done = fail = null; stop(); ng(new Error(p.why || 'room')); }
    }
    function stop() { if (!live) return; live = false; document.removeEventListener('tengel:native', onNative); if (N) N.call('room', { op: 'stop' }).catch(() => { }); }
    return {
      open: (mode, room, step) => new Promise((ok, ng) => {
        if (!N || !window.__NATIVE) return ng(new Error('none'));
        onStep = step || null; done = ok; fail = ng; live = true;
        document.addEventListener('tengel:native', onNative);
        N.call('room', { op: mode === 'host' ? 'host' : 'join', room: String(room) }).then(r => { if (!r || !r.ok) { const f = fail; done = fail = null; stop(); if (f) f(new Error((r && r.why) || 'room')); } })
          .catch(e => { const f = fail; done = fail = null; stop(); if (f) f(e); });
      }),
      cancel: () => { const f = fail; done = fail = null; stop(); if (f) f(new Error('cancel')); }
    };
  }

  return { PROTO, STAKE_MAX, MIN_SETS, stakeOf, dzOf, gmOf, clean: v => { const x = clean(v, 0); return x === BAD ? undefined : x; }, cpu, host, guest, nativeRoom,
    _t: { get minSets() { return minSets; }, set minSets(n) { minSets = Math.max(0, Math.floor(+n || 0)); } } };
})();
if (typeof module !== 'undefined' && module.exports) module.exports = CBNet;
