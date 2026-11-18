// 馬カードバトルの「対戦の 進め役」（cb/cb_net.js）の テスト：node test_cb_net.js
//   部屋の ホスト と ゲスト を、文字を 渡し合う だけの 線（link）で つないで 対戦する：
//     ・ゲストに 届く 文字の 中に、ホストの 手札・山札の 並び・ふせた カードの 中身が 入って いない
//     ・2人の 画面に 出る もの（view）が、同じ 対戦を それぞれの 席から 見た 形に なって いる
//     ・もう 1回・やめる・切れた・版が ちがう
//   コンピュータとの 対戦：画面の 動きが 終わって（idle）から 考える・もう 1回
//   第4.179版：部屋の 決まり（参加コイン・勝者の 獲得コイン）：ホストの あいさつに 入る → ゲストが「参加する」（join）と 答えて から 配る・数字の はんい（stakeOf）
//   第4.183版：部屋の あいさつに おたがいの デザイン（dz）・こわれた デザインは すてる・PROTO 6（ルールが かわった：4 の 効果で 交換して 5 を 出したら 5 の 効果）
//   第4.187版：PROTO 8（7 の 4まい 公開は セットの 前・場の カードは いつも うら）・部屋で 4まい 公開 → 7 を セット（ゲストには どれを 出したか わからない）
//   第4.188版：PROTO 9（効果の 順 6 → 7 → 3 → 5 → 4）・部屋で 4 は いちばん あと：ゲストの 5 の 効果で 山札から ふせた カードを、ホストの 4 で 交換
//   第4.190版：PROTO 10（6 は ターンの はじめ・効果タイムは 1つずつ）・1ターン目の はじめの 6 は 配った 知らせと いっしょ（deal,sixt）
//   第4.202版：PROTO 13（7 の 3まい 交換・3 は セットの 前・決着したら 試合終了）
//   第4.203版：相手の 手札は いつも 本当の 手札（見た カードを セットしたら 手札から 消える：ホストが 作る 見え方。ルールは 同じ ＝ PROTO 13 の まま）
//   第4.197版：PROTO 11（決戦宝石）・部屋を 作る 人が「決戦宝石 あり」→ あいさつで ゲストへ → 参加 → 2人とも 5つ（まさちゃん 20:21「お友達バトルは1試合で5個使える！」）・おたがいに 見える
global.CBRules = require('./cb/cb_rules.js'); global.CBCpu = require('./cb/cb_cpu.js');
const R = global.CBRules, C = global.CBCpu, N = require('./cb/cb_net.js');
let fails = [];
function check(c, label) { console.log((c ? '  ✅ ' : '  ❌ ') + label); if (!c) fails.push(label); }
function rngOf(seed) { let a = seed >>> 0; return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const tick = () => new Promise(r => setImmediate(r));
const sleep = ms => new Promise(r => setTimeout(r, ms));
// 2つの はしを 持つ 線：送った 文字は 次の 回に 相手へ 届く（log＝通った 文字 ぜんぶ）
function wire() {
  const log = []; let open = true;
  const mk = () => ({ onText: null, onLost: null, sent: [], closed: false });
  const a = mk(), b = mk();
  const bind = (me, you, tag) => {
    me.send = txt => { if (!open || me.closed) return; me.sent.push(txt); log.push([tag, txt]); setImmediate(() => { if (open && !you.closed && you.onText) you.onText(txt); }); };
    me.close = () => { if (me.closed) return; me.closed = true; setImmediate(() => { if (!you.closed && you.onLost) you.onLost(); }); };
  };
  bind(a, b, 'h'); bind(b, a, 'g');
  return { a, b, log, cut: () => { open = false; if (a.onLost) a.onLost(); if (b.onLost) b.onLost(); } };
}
// 席ごとの「画面」：届いた ものを 覚える だけ
function seat(m) { const s = { ups: [], states: [], view: null }; m.onUpdate = u => { s.ups.push(u); s.view = u.view; }; m.onState = x => s.states.push(x); return s; }
// 番が 来たら コンピュータと 同じ 考え方で 打つ（見えて いる こと だけ）
async function playOut(pairs, rng, guard) {
  for (let n = 0; n < (guard || 200); n++) {
    await tick(); await tick();
    let moved = false, done = true;
    for (const [m, s] of pairs) {
      if (!s.view || s.view.phase !== 'end') done = false;
      const a = s.view ? C.decide(s.view, rng) : null; if (!a) continue;
      const r = await m.act(a); await tick(); await tick();
      if (!r.ok) return 'bad:' + JSON.stringify(a) + ':' + r.why;
      moved = true;
    }
    if (done) return 'end';
    if (!moved) { await tick(); await tick(); }
  }
  return 'guard';
}

(async () => {
  console.log('■ 部屋：ホスト と ゲスト');
  {
    const w = wire(), rng = rngOf(5);
    const H = N.host(w.a, rng, { hands: [['k', '1', '2', '6', '6'], ['m', '3', '4', '5', '7']] }), G = N.guest(w.b);
    const hs = seat(H), gs = seat(G);
    H.start(); await tick();
    check(hs.ups.length === 0 && w.log.length === 0, 'ホストは 友だちの あいさつが 届く まで 配らない');
    G.start(); await tick(); await tick(); await tick();
    check(w.log[0][0] === 'g' && JSON.parse(w.log[0][1]).t === 'hello' && JSON.parse(w.log[0][1]).v === N.PROTO && N.PROTO === 13 && JSON.parse(w.log[1][1]).t === 'hello' && hs.states.join() === 'ready' && gs.states.join() === 'ready,stake'
      && JSON.stringify(JSON.parse(w.log[1][1]).stake) === '{"e":0,"w":0}' && JSON.stringify(G.stake) === '{"e":0,"w":0}' && hs.ups.length === 0,
      'はじめに おたがいに あいさつ（hello・版の 番号 11：第4.197版）・ホストの あいさつに 部屋の 決まり（参加コイン 0）→ ゲストに「決まりが 届いた」（まだ 配らない）');
    G.join(); await tick(); await tick(); await tick();
    check(JSON.parse(w.log[2][1]).t === 'join' && hs.states.join() === 'ready,joined', 'ゲストが「参加する」（join）→ ホストに 届く');
    check(hs.ups.length === 1 && gs.ups.length === 1 && hs.ups[0].ev[0].e === 'deal' && gs.ups[0].ev[0].e === 'deal' && hs.view.me === 0 && gs.view.me === 1, 'あいさつの あと 配る：2人に はじめの 形が 届く（ホスト＝席 0・ゲスト＝席 1）');
    check(hs.view.my.hand.map(c => c.k).join('') === 'k1266' && gs.view.my.hand.map(c => c.k).join('') === 'm3457' && gs.view.op.hand.every(c => c.k === null) && hs.view.op.hand.every(c => c.k === null),
      'それぞれ 自分の 手札 だけ 見える');
    check(hs.ups[0].ev.map(e => e.e).join() === 'deal,sixt' && gs.ups[0].ev.map(e => e.e).join() === 'deal,sixt' && hs.ups[0].ev[1].mine === true && gs.ups[0].ev[1].mine === false && gs.ups[0].ev[1].other === true
      && hs.view.phase === 'six' && hs.view.can.six && gs.view.can.six === null && gs.view.wait === true && !hs.view.can.set && !gs.view.can.set,
      '第4.190版：配った 知らせと いっしょに 1ターン目の はじめ：ホスト（6 が 2まい）が 6 の 効果を えらぶ 番・ゲストは 待つ（2人とも まだ セットできない）');
    const up0 = JSON.parse(w.log.find(x => x[0] === 'h' && JSON.parse(x[1]).t === 'up')[1]);
    check(!/"deck"/.test(JSON.stringify(up0)) && (JSON.stringify(up0).match(/"k":"[1-7km]"/g) || []).length === 5, 'ゲストに 送る 文字の 中の カードの 中身は ゲストの 手札の 5まい だけ（ホストの 手札・山札の 並びは 入って いない）');
    const early = await G.act({ t: 'set', u: gs.view.my.hand.find(c => c.k === '3').u }); await tick();
    const late1 = await G.act({ t: 'p6', pick: hs.view.my.hand[0].u }); await tick();
    check(early.ok === false && late1.ok === false && hs.view.phase === 'six' && !gs.view.my.set, 'ゲストは まだ セットできない・6 の 効果も 使えない（ホストが ことわる）');
    // ホストが 6 の 効果（ゲストの 手札を 1まい 見る）→ 2人とも セットへ
    const pk = gs.view.my.hand[0].u, pkK = gs.view.my.hand[0].k;
    const before = w.log.length;
    const r2 = await H.act({ t: 'p6', pick: pk }); await tick(); await tick();
    const sent = w.log.slice(before).filter(x => x[0] === 'h').map(x => JSON.parse(x[1]));
    check(r2.ok && hs.view.op.hand.find(c => c.u === pk).k === pkK && gs.view.my.hand.find(c => c.u === pk).seen === true && gs.view.op.hand.filter(c => c.k === '6').length === 2
      && sent.length === 1 && sent[0].ev.map(e => e.e).join() === 'sixd,p6' && sent[0].ev[1].k === undefined && sent[0].ev[1].pick === pk && hs.view.phase === 'set' && hs.view.can.set && gs.view.can.set,
      'ホストが 6 の 効果：ホストは 見た カードが 見える・ゲストには 見せた 6 の 2まいと「どれを 見られたか」→ 2人とも セットへ');
    // ゲストが 出す → まだ オープン しない。ホストに 届くのは「相手が 出した」だけ
    const gu = gs.view.my.hand.find(c => c.k === '3').u;
    const r1 = await G.act({ t: 'set', u: gu }); await tick(); await tick();
    check(r1.ok && hs.view.op.set && hs.view.op.set.k === null && gs.view.my.set.k === '3' && hs.ups[hs.ups.length - 1].ev[0].e === 'set' && hs.ups[hs.ups.length - 1].ev[0].me === false && hs.ups[hs.ups.length - 1].ev[0].u === undefined,
      'ゲストが 出した：ホストには「相手が 出した」だけ（どの カードかは 届かない）');
    const bad = await G.act({ t: 'set', u: gu }); await tick();
    check(bad.ok === false, 'ゲストの まちがった 手（もう 出した）は ホストが ことわる（ack ok:false）');
    const fake = await G.act({ t: 'set', u: hs.view.my.hand[0].u }); await tick();
    check(fake.ok === false && hs.view.my.hand.length === 5 && !hs.view.my.set, 'ゲストは ホストの カードを 動かせない');
    // ホストも 出す → 効果タイムは ない（第4.190版：6 は ターンの はじめ）→ オープン → 2ターン目の はじめ：まず 6・その あと 神様馬
    const r3 = await H.act({ t: 'set', u: hs.view.my.hand.find(c => c.k === 'k').u }); await tick(); await tick();
    const hu = hs.ups[hs.ups.length - 1], gu2 = gs.ups[gs.ups.length - 1];
    check(r3.ok && hu.ev.map(e => e.e).join() === 'set,open,clear,turn,sixt' && gu2.ev.map(e => e.e).join() === 'set,open,clear,turn,sixt' && hu.ev[1].res === 'win' && gu2.ev[1].res === 'lose' && hu.ev[1].my.k === 'k' && gu2.ev[1].my.k === '3' && gu2.ev[1].op.k === 'k'
      && hs.view.turn === 2 && gs.view.turn === 2 && hs.view.phase === 'six' && hs.view.can.six && !hs.view.pend && gs.view.wait === true && !hs.view.can.set && !gs.view.can.set,
      'オープン：同じ できごとが 2人に 届く（ホスト＝勝ち・ゲスト＝負け）。2ターン目の はじめ：まず ホストの 6（神様馬の 効果は その あと）');
    const r5 = await H.act({ t: 'p6', pick: null }); await tick(); await tick();
    check(r5.ok && hs.ups[hs.ups.length - 1].ev.map(e => e.e).join() === 'sixd,p6skip,pre' && gs.ups[gs.ups.length - 1].ev.map(e => e.e).join() === 'sixd,p6skip,pre'
      && hs.view.phase === 'pre' && hs.view.pend.mine === true && hs.view.pend.type === 'k' && gs.view.pend.mine === false && gs.view.wait === true && !hs.view.can.set && !gs.view.can.set,
      '6 を 使わない →（ゲストにも「使わなかった」）→ 神様馬の 効果は ホストが えらぶ・ゲストは 待つ');
    check(JSON.stringify(hs.view.discard) === '[{"k":"k","mine":true,"why":"t","turn":1},{"k":"3","mine":false,"why":"t","turn":1}]' && JSON.stringify(gs.view.discard) === '[{"k":"k","mine":false,"why":"t","turn":1},{"k":"3","mine":true,"why":"t","turn":1}]',
      '捨て札：2人に 同じ 中身が 届く（「だれの」だけ 自分から 見た 形）');
    const r4 = await H.act({ t: 'k', pick: null }); await tick(); await tick();
    check(r4.ok && hs.view.turn === 2 && gs.view.turn === 2 && hs.view.phase === 'set' && hs.view.can.set && gs.view.can.set && hs.view.my.wins === 1 && gs.view.op.wins === 1, '効果を 使わない → 2人とも 2ターン目の セットへ');
    const end = await playOut([[H, hs], [G, gs]], rng);
    check(end === 'end' && hs.view.phase === 'end' && gs.view.phase === 'end' && ((hs.view.res === 'win' && gs.view.res === 'lose') || (hs.view.res === 'lose' && gs.view.res === 'win') || (hs.view.res === 'draw' && gs.view.res === 'draw'))
      && hs.view.my.wins === gs.view.op.wins && hs.view.op.wins === gs.view.my.wins,
      `さいごまで：2人の 結果は うらおもて（ホスト ${hs.view.res} ${hs.view.my.wins}－${hs.view.op.wins}・ゲスト ${gs.view.res}）`);
    // もう 1回：2人とも 押したら 配り直す
    const n0 = hs.ups.length;
    G.again(); await tick(); await tick();
    check(hs.states.indexOf('again') >= 0 && hs.ups.length === n0, 'ゲストが「もう 1回」→ ホストに 知らせ（まだ 配らない）');
    H.again(); await tick(); await tick(); await tick();
    check(gs.states.indexOf('again') >= 0 && hs.view.phase === 'six' && gs.view.phase === 'six' && hs.view.turn === 1 && hs.ups[hs.ups.length - 1].ev.map(e => e.e).join() === 'deal,sixt' && gs.view.my.hand.length === 5 && hs.view.my.wins === 0,
      'ホストも「もう 1回」→ 配り直して 新しい 対戦');
    // やめる
    G.leave(); await sleep(320); await tick();
    check(hs.states[hs.states.length - 1] === 'bye' && w.b.closed && w.a.closed, 'ゲストが やめる → ホストに「相手が やめた」・線は とじる');
    const late = await H.act({ t: 'set', u: hs.view.my.hand[0].u });
    check(late.ok === false && late.why === 'off', 'やめた あとの 手は 通らない');
  }

  console.log('■ 部屋：逆転勝利（第4.178版：ゲストが 1 を 3まい・ホストが 幻の馬）');
  {
    const w = wire(), rng = rngOf(9);
    const H = N.host(w.a, rng, { hands: [['m', '4', '5', '6', '7'], ['1', '1', '1', '2', '3']], turns: 3 }), G = N.guest(w.b), hs = seat(H), gs = seat(G);
    H.start(); G.start(); await tick(); await tick(); await tick(); G.join(); await tick(); await tick(); await tick();
    await G.act({ t: 'set', u: gs.view.my.hand.find(c => c.k === '1').u }); await tick(); await tick();
    const n0 = w.log.length;
    await H.act({ t: 'set', u: hs.view.my.hand.find(c => c.k === 'm').u }); await tick(); await tick();
    const hu = hs.ups[hs.ups.length - 1], gu = gs.ups[gs.ups.length - 1], sent = w.log.slice(n0).filter(x => x[0] === 'h').map(x => x[1]).join('');
    check(hu.ev.map(e => e.e).join() === 'set,open' && gu.ev.map(e => e.e).join() === 'set,open' && hu.ev[1].rev === 'op' && gu.ev[1].rev === 'me' && hu.ev[1].res === 'win' && gu.ev[1].res === 'lose' && hu.ev[1].wins.join() === '0,0'
      && hs.view.phase === 'rev' && gs.view.phase === 'rev' && gs.view.pend.type === 'rev' && gs.view.pend.mine === true && hs.view.pend.mine === false && hs.view.wait === true && gs.view.wait === false && hs.view.op.hand.every(c => c.k === null),
      'オープンした 所で 止まる：ゲスト（1 が 3まい）が「逆転勝利を 使う？」・ホスト（幻の馬）は 待つ（勝ちは まだ 数えない）');
    check(!/"who"|"known"|"deck"/.test(sent) && (sent.match(/"k":"m"/g) || []).length >= 1 && !/"k":"[4567]"/.test(sent), 'ゲストに 送る 文字：場の 幻の馬は 見える・ホストの 手札（4・5・6・7）の 中身は 入って いない');
    const no = await H.act({ t: 'rev', use: true }); await tick();
    check(no.ok === false && hs.view.phase === 'rev' && hs.view.my.wins === 0, '聞かれて いない ホストが「使う」を 送っても 通らない');
    const yes = await G.act({ t: 'rev', use: true }); await tick(); await tick();
    const hu2 = hs.ups[hs.ups.length - 1], gu2 = gs.ups[gs.ups.length - 1];
    check(yes.ok && hu2.ev.map(e => e.e).join() === 'rev,fin,clear,turn' && gu2.ev.map(e => e.e).join() === 'rev,fin,clear,turn' && hu2.ev[0].me === false && gu2.ev[0].me === true && hu2.ev[0].k === '1' && hu2.ev[0].beat === 'm' && hu2.ev[0].show.length === 2 && hu2.ev[0].drop.k === '1'
      && hu2.ev[1].res === 'lose' && gu2.ev[1].res === 'win' && hu2.ev[1].rev === true && gu2.ev[1].wins.join() === '1,0' && hu2.ev[1].wins.join() === '0,1',
      'ゲストが「使う」→ 2人に 同じ できごと（見せた 2まい・捨てた 1・結果：ゲスト 勝ち／ホスト 負け）');
    check(hs.view.turn === 2 && gs.view.turn === 2 && hs.view.phase === 'set' && !hs.view.pend && gs.view.my.wins === 1 && hs.view.op.wins === 1 && hs.view.my.wins === 0 && gs.view.my.hand.length === 3
      && hs.view.op.hand.filter(c => c.k === '1').length === 1 && hs.view.op.hand.filter(c => c.k === null).length === 2 && gs.view.my.hand.filter(c => c.seen).map(c => c.k).join() === '1'
      && JSON.stringify(gs.view.discard.map(d => d.k + d.why + (d.mine ? 'me' : 'op'))) === '["11me","mtop","1tme"]',
      '2ターン目へ（幻の馬の 効果は 出ない）：ゲストの 手札 3まい・見せて のこった 1 は ホストの 画面で 表・捨て札に「1 の 効果で 捨てた 1」');
    const end = await playOut([[H, hs], [G, gs]], rng);
    check(end === 'end' && hs.view.phase === 'end' && gs.view.phase === 'end', 'その あとも さいごまで あそべる');
  }

  console.log('■ 部屋：7 の 4まい 公開（第4.187版：セットの 前・場の カードは うら）');
  {
    const w = wire(), rng = rngOf(11);
    const H = N.host(w.a, rng, { hands: [['7', '7', '7', '7', '6'], ['1', '2', '3', '4', '5']], turns: 3 }), G = N.guest(w.b), hs = seat(H), gs = seat(G);
    H.start(); G.start(); await tick(); await tick(); await tick(); G.join(); await tick(); await tick(); await tick();
    check(hs.view.can.x7r === true && gs.view.can.x7r === false && hs.view.phase === 'set', 'ホスト（7 が 4まい）は セットの 前に 4まい 公開を 使える・ゲストは 使えない');
    const no = await G.act({ t: 'x7r' }); await tick();
    const r = await H.act({ t: 'x7r' }); await tick(); await tick();
    const gu = gs.ups[gs.ups.length - 1];
    check(!no.ok && r.ok && gu.ev.map(e => e.e).join() === 'x7r' && gu.ev[0].me === false && gu.ev[0].show.length === 4 && gu.ev[0].drop.k === '7' && gs.view.rv === true && hs.view.rv === true
      && gs.view.op.hand.map(c => c.k).join(',') === '7,7,7,' && gs.view.phase === 'set' && hs.view.can.set && gs.view.can.set,
      'ホストが 使う → ゲストにも 同じ できごと（見せた 4まい・捨てた 7）・2人とも 強さ 逆転・ゲストには のこりの 7 の 3まいが 見える・セットは これから');
    const n0 = w.log.length;
    await H.act({ t: 'set', u: hs.view.my.hand.find(c => c.k === '7').u }); await tick(); await tick();
    const sent = w.log.slice(n0).filter(x => x[0] === 'h').map(x => JSON.parse(x[1])).filter(o => o.t === 'up');
    check(sent.length === 1 && gs.view.op.set && gs.view.op.set.k === null && sent[0].view.op.set.k === null && gs.view.op.hand.map(c => c.k).join(',') === '7,7,' && hs.view.my.set.k === '7',
      'ホストが 7 を セット：ゲストの 画面では 場の カードは うら・手札は 本当の 手札（見た 7 が 1まい へる：第4.203版）');
    await G.act({ t: 'set', u: gs.view.my.hand.find(c => c.k === '1').u }); await tick(); await tick();
    const op = gs.ups[gs.ups.length - 1].ev.find(e => e.e === 'open');
    check(op && op.op.k === '7' && op.my.k === '1' && op.res === 'lose' && gs.view.op.hand.map(c => c.k).join(',') === '7,7,', 'オープン：逆転ちゅうの 7 が 1 に 勝つ・その あと ゲストの 画面の 手札は ほんとうの 形（7 が 2まい）');
    const end = await playOut([[H, hs], [G, gs]], rng);
    check(end === 'end', 'その あとも さいごまで あそべる');
  }

  console.log('■ 部屋：手札の 効果は セットの 前・決着したら 試合終了（第4.202版：まさちゃん 11/18 23:42「手札から使える効果は、カードセット前に使えるようにして！」・23:55「どちらかが３ターン勝利したら、試合終了にして！」）');
  {
    const w = wire(), rng = rngOf(13);
    const H = N.host(w.a, rng, { hands: [['3', '3', '3', '1', '2'], ['1', '6', '7', '7', '2']], turns: 3 }), G = N.guest(w.b), hs = seat(H), gs = seat(G);
    H.start(); G.start(); await tick(); await tick(); await tick(); G.join(); await tick(); await tick(); await tick();
    check(hs.view.can.x3 === true && gs.view.can.x3 === false && hs.view.can.x7 === false && hs.view.phase === 'set' && !hs.view.my.set && !gs.view.my.set, 'ホスト（3 が 3まい）は セットの 前に 3 の 効果を 使える・ゲストは 使えない（まだ だれも セットして いない）');
    const no = await G.act({ t: 'x3', pick: (gs.view.op.hand[0] || {}).u }); await tick();
    const nop = await H.act({ t: 'x3' }); await tick();      // えらばない → 使えない（くじで 自動は ない）
    const pk = hs.view.can.x3p[1], r = await H.act({ t: 'x3', pick: pk }); await tick(); await tick();
    const gu = gs.ups[gs.ups.length - 1], hu = hs.ups[hs.ups.length - 1], gx = gu.ev.find(e => e.e === 'x3'), hx = hu.ev.find(e => e.e === 'x3');
    const gk = gs.view.my.hand.map(c => c.k).sort().join(''), hk = hs.view.my.hand.map(c => c.k).sort().join('');
    check(!no.ok && !nop.ok && nop.why === 'pick' && r.ok && hx && hx.take.u === pk && hs.view.can.x3p.length === 0 && gx && hx && gx.me === false && hx.me === true && gx.three.length === 3 && gx.give.k === '3' && gx.take.k === hx.take.k && '1267'.indexOf(gx.take.k) >= 0
      && gs.view.my.hand.length === 5 && hs.view.my.hand.length === 5 && gk.split('3').length === 2 && hk.split('3').length === 3 && gs.view.phase === 'set' && hs.view.can.set && gs.view.can.set && hs.view.can.x3 === false && gs.view.op.hand.filter(c => c.k === '3').length === 2,
      `ホストが うらの カードを 1まい えらんで 使う（えらばないと 使えない）→ ゲストにも 同じ できごと（見せた 3まい・わたした 3・えらんだ カード ${gx && gx.take.k}）・手札は 5まいずつ（ホスト ${hk}・ゲスト ${gk}）・ゲストには のこりの 3 が 2まい 見える・セットは これから・同じ ターンは もう 使えない`);
    const strong = v => v.my.hand.filter(c => c.k === '1' || c.k === '2').sort((a, b) => a.k < b.k ? -1 : 1)[0], weak = v => v.my.hand.filter(c => c.k === '6' || c.k === '7').sort((a, b) => a.k > b.k ? -1 : 1)[0];
    for (let t = 1; t <= 2; t++) {
      await H.act({ t: 'set', u: strong(hs.view).u }); await tick(); await tick();
      await G.act({ t: 'set', u: weak(gs.view).u }); await tick(); await tick();
    }
    const ge = gs.ups[gs.ups.length - 1].ev.find(e => e.e === 'end'), he = hs.ups[hs.ups.length - 1].ev.find(e => e.e === 'end');
    check(hs.view.phase === 'end' && gs.view.phase === 'end' && hs.view.res === 'win' && gs.view.res === 'lose' && hs.view.early === 2 && gs.view.early === 2 && ge && he && ge.early === 2 && he.early === 2 && gs.view.turn === 2 && hs.view.my.wins === 2 && gs.view.op.wins === 2,
      `2勝 0敗・のこり 1ターン → 2ターン目で 決着（2人とも できごと end に early 2・結果は うらおもて：${hs.view.res}／${gs.view.res}）`);
  }

  console.log('■ 部屋：4 は いちばん あと（第4.188版：ゲストの 5 の 効果 → 山札から ふせた カードを ホストの 4 で 交換）');
  {
    const w = wire(), rng = rngOf(12);
    const H = N.host(w.a, rng, { hands: [['4', '1', '2', '3', '6'], ['5', '6', '7', '1', '2']], deck: ['k'], turns: 3 }), G = N.guest(w.b), hs = seat(H), gs = seat(G);
    H.start(); G.start(); await tick(); await tick(); await tick(); G.join(); await tick(); await tick(); await tick();
    await G.act({ t: 'set', u: gs.view.my.hand.find(c => c.k === '5').u }); await tick(); await tick();
    await H.act({ t: 'set', u: hs.view.my.hand.find(c => c.k === '4').u }); await tick(); await tick();
    await G.act({ t: 'eff', use: { u5: gs.view.my.hand.find(c => c.k === '7').u } }); await tick(); await tick();
    const hu1 = hs.ups[hs.ups.length - 1], gu1 = gs.ups[gs.ups.length - 1];
    check(gu1.ev.map(e => e.e).join() === 'effd,u5,efft' && hu1.ev.map(e => e.e).join() === 'effd,u5,efft' && hu1.ev[2].mine === true && hu1.ev[2].st === 'u4' && gu1.ev[2].mine === false && !('st' in gu1.ev[2])
      && hs.view.can.eff && hs.view.can.eff.e4 && gs.view.can.eff === null && gs.view.wait === true,
      '第4.190版：ゲストの 5 の 効果を すぐ 行う → 次に ホストの 4（ゲストには どの 効果を 聞いて いるか 届かない）');
    await H.act({ t: 'eff', use: { u4: true } }); await tick(); await tick();
    const hu = hs.ups[hs.ups.length - 1], gu = gs.ups[gs.ups.length - 1];
    check(gu.ev.map(e => e.e).join() === 'effd,first' && hu.ev.map(e => e.e).join() === 'effd,first' && hu1.ev[1].five.k === '5' && hu1.ev[1].drop.k === '7' && gs.view.phase === 'swap' && gs.view.pend.mine === true && gs.view.my.set.blind === true && gs.view.my.set.k === null && hs.view.op.set.k === null,
      'ゲストの 5 の 効果（5 と 7 を 捨てて 山札から ふせて セット）→ ホストの 4 の 効果（いちばん あと）→ ゲストが 山札から 来た カードを 交換する 番（中身は まだ だれにも 見えない）');
    await G.act({ t: 'swap', u: gs.view.my.hand.find(c => c.k === '1').u }); await tick(); await tick();
    check(gs.view.my.hand.some(c => c.k === 'k') && gs.view.turn === 2 && gs.view.my.wins === 1, '交換：山札から 来て いた 神様馬は ゲストの 手札に 入る・出した 1 が 4 に 勝つ');
    const end = await playOut([[H, hs], [G, gs]], rng);
    check(end === 'end', 'その あとも さいごまで あそべる');
  }

  console.log('■ 部屋：たくさん あそぶ（でたらめな 手札で 300回）');
  {
    let bad = 0, leak = 0, n = 0; const res = { win: 0, lose: 0, draw: 0 };
    for (let g = 0; g < 300; g++) {
      const w = wire(), rng = rngOf(1000 + g);
      const H = N.host(w.a, rng, undefined, g % 3 ? { e: g % 7, w: g % 7 + (g % 5) } : null), G = N.guest(w.b), hs = seat(H), gs = seat(G);      // 第4.179版：参加コインの ある 部屋も まぜる
      H.start(); G.start(); await tick(); await tick(); await tick();
      if (JSON.stringify(G.stake) !== JSON.stringify(H.stake)) { bad++; continue; }
      G.join(); await tick(); await tick(); await tick();
      const end = await playOut([[H, hs], [G, gs]], rng);
      if (end !== 'end') { bad++; continue; }
      const S = H._.state();
      // ゲストへ 送った 文字に、その 時 ゲストが 知らない はずの カードの 中身が ない：送った view の 相手の 手札は 知って いる もの だけ
      for (const [tag, txt] of w.log) {
        if (tag !== 'h') continue; const o = JSON.parse(txt); if (o.t !== 'up') continue;
        if (/"deck"|"known"|"uid"/.test(txt)) leak++;
        if (o.view.op.set && o.view.op.set.k && !(o.view.op.set.up)) { /* 見た カードが 場に 出た とき だけ */ }
      }
      if (!((hs.view.res === 'win' && gs.view.res === 'lose') || (hs.view.res === 'lose' && gs.view.res === 'win') || (hs.view.res === 'draw' && gs.view.res === 'draw'))) bad++;
      if (S.phase !== 'end') bad++;
      res[hs.view.res]++; n++;
    }
    check(bad === 0 && leak === 0 && n === 300, `300回：ぜんぶ さいごまで・2人の 結果は うらおもて・山札の 並びは 送らない（ホスト 勝ち ${res.win}・負け ${res.lose}・同点 ${res.draw}）`);
  }

  console.log('■ 部屋：切れた・版が ちがう・こわれた 文字');
  {
    const w = wire(), H = N.host(w.a, rngOf(1)), G = N.guest(w.b), hs = seat(H), gs = seat(G);
    H.start(); G.start(); await tick(); await tick(); await tick();
    w.cut(); await tick();
    check(hs.states[hs.states.length - 1] === 'lost' && gs.states[gs.states.length - 1] === 'lost', '線が 切れた → 2人とも「切れた」');
    const r = await G.act({ t: 'set', u: 1 }); check(r.ok === false && r.why === 'off', '切れた あとの 手は すぐ「通らない」と 返る（待ち つづけない）');
  }
  {
    const w = wire(), H = N.host(w.a, rngOf(1)), hs = seat(H);
    H.start();
    w.b.onText = () => { };
    w.b.send(JSON.stringify({ t: 'hello', v: N.PROTO + 1 })); await tick(); await tick();
    check(hs.states.join() === 'ver' && hs.ups.length === 0 && JSON.parse(w.a.sent[0]).t === 'hello', '版が ちがう 相手：対戦しない（ホストは 自分の 版を 返して「版が ちがう」）');
  }
  {
    const w = wire(), G = N.guest(w.b), gs = seat(G);
    G.start(); w.a.onText = () => { };
    w.a.send(JSON.stringify({ t: 'hello', v: 99 })); await tick(); await tick();
    check(gs.states.join() === 'ver', 'ゲストも 版が ちがえば 対戦しない');
  }
  {
    const w = wire(), H = N.host(w.a, rngOf(1)), G = N.guest(w.b), hs = seat(H), gs = seat(G);
    H.start(); G.start(); await tick(); await tick(); await tick(); G.join(); await tick(); await tick(); await tick();
    const n0 = hs.ups.length;
    for (const junk of ['', 'x', '{', 'null', '[]', '{"t":"act"}', '{"t":"act","id":1,"a":{"t":"set","u":"zz"}}', '{"t":"up","view":{}}', 'a'.repeat(30000), '{"t":"act","id":2,"a":null}']) w.b.send(junk);
    await tick(); await tick(); await tick();
    check(hs.ups.length === n0 && hs.view.my.hand.length === 7 && H._.state().p[1].hand.length === 7 && hs.states.join() === 'ready,joined', 'こわれた 文字・長すぎる 文字・でたらめな 手が 届いても 対戦は そのまま（何も かわらない）');
    w.a.send('{bad'); w.a.send(JSON.stringify({ t: 'up' })); w.a.send(JSON.stringify({ t: 'up', n: 9, ev: 'x', view: {} })); await tick(); await tick();
    check(gs.ups.length === 1, 'ゲストも こわれた 文字は 捨てる');
  }
  {
    const w = wire(), H = N.host(w.a, rngOf(1)), hs = seat(H);
    H.start();
    w.b.onText = () => { };
    w.b.send(JSON.stringify({ t: 'act', id: 1, a: { t: 'set', u: 1 } })); await tick(); await tick();
    check(hs.ups.length === 0 && w.a.sent.length === 0, 'あいさつの 前の 手は 受けない');
  }

  console.log('■ 部屋の 決まり：参加コイン・勝者の 獲得コイン（第4.179版・まさちゃん 16:18「バトルコインで参加枚数を指定する・勝者獲得コインは、参加枚数の2倍まで」）');
  {
    const S = N.stakeOf;
    check(JSON.stringify([S(null), S({}), S({ e: 3, w: 6 }), S({ e: 3, w: 9 }), S({ e: 3, w: 1 }), S({ e: -2, w: 5 }), S({ e: 2.7, w: 4.9 }), S({ e: '4', w: '7' }), S({ e: 'x', w: 3 }), S({ e: 5000, w: 1 }), S({ e: 0, w: 9 })])
      === JSON.stringify([{ e: 0, w: 0 }, { e: 0, w: 0 }, { e: 3, w: 6 }, { e: 3, w: 6 }, { e: 3, w: 3 }, { e: 0, w: 0 }, { e: 2, w: 4 }, { e: 4, w: 7 }, { e: 0, w: 0 }, { e: N.STAKE_MAX, w: N.STAKE_MAX }, { e: 0, w: 0 }]) && N.STAKE_MAX === 999,
      '数字の はんい：参加コインは 0〜999・獲得コインは 参加コイン 〜 2倍（はみ出したら はじに よせる・数字で ない ものは 0）');
    const w = wire(), rng = rngOf(21), H = N.host(w.a, rng, { hands: [['1', '2', '3', '6', '7'], ['2', '3', '6', '7', '7']], turns: 3 }, { e: 3, w: 9 }), G = N.guest(w.b), hs = seat(H), gs = seat(G);
    H.start(); G.start(); await tick(); await tick(); await tick();
    const hello = JSON.parse(w.log.find(x => x[0] === 'h' && JSON.parse(x[1]).t === 'hello')[1]);
    check(JSON.stringify(H.stake) === '{"e":3,"w":6}' && JSON.stringify(hello.stake) === '{"e":3,"w":6}' && JSON.stringify(G.stake) === '{"e":3,"w":6}' && gs.states.join() === 'ready,stake' && hs.ups.length === 0 && gs.ups.length === 0,
      'ホストが 決めた 決まり（参加 3・勝者 9 → 2倍の 6 に なおす）が あいさつで ゲストに 届く・まだ 配らない');
    w.b.send(JSON.stringify({ t: 'join', stake: { e: 1, w: 2 } })); await tick(); await tick();
    w.b.send(JSON.stringify({ t: 'act', id: 1, a: { t: 'set', u: 1 } })); await tick(); await tick();
    check(hs.ups.length === 0 && hs.states.join() === 'ready' && !H._.state(), 'ちがう 決まりで「参加する」が 届いても 配らない・参加の 前の 手も 受けない');
    G.join(); await tick(); await tick(); await tick();
    check(hs.states.join() === 'ready,joined' && hs.ups.length === 1 && gs.ups.length === 1 && hs.view.turns === 3 && gs.view.my.hand.length === 5, '同じ 決まりで「参加する」→ 配る');
    G.join(); await tick(); await tick();
    check(hs.ups.length === 1 && hs.states.join() === 'ready,joined', '2回目の「参加する」は 何も しない（配り直さない）');
    const end = await playOut([[H, hs], [G, gs]], rng);
    check(end === 'end' && hs.view.res && gs.view.res && JSON.stringify(G.stake) === '{"e":3,"w":6}', `さいごまで あそべる（ホスト ${hs.view.res}）・決まりは 対戦の あいだ かわらない`);
    // 決まりが 0 の 部屋（前の 版と 同じ）・ゲストが 参加しないで 出る
    const w2 = wire(), H2 = N.host(w2.a, rngOf(2), undefined, { e: 0, w: 5 }), G2 = N.guest(w2.b), h2 = seat(H2), g2 = seat(G2);
    H2.start(); G2.start(); await tick(); await tick(); await tick();
    check(JSON.stringify(G2.stake) === '{"e":0,"w":0}' && h2.ups.length === 0, '参加コイン 0 の 部屋：勝者の 獲得コインも 0（ゲストが「参加する」まで 配らない）');
    G2.leave(); await sleep(300); await tick();
    check(h2.states[h2.states.length - 1] === 'bye' && h2.ups.length === 0, '「参加する」の 前に ゲストが 出た → ホストに「相手が やめた」（配って いない）');
    const w3 = wire(), G3 = N.guest(w3.b), g3 = seat(G3); w3.a.onText = () => { };
    G3.join(); await tick();
    check(w3.log.length === 0 && G3.stake === null, 'あいさつが 届く 前の「参加する」は 送らない');
  }

  console.log('■ 部屋：それぞれの デザイン（第4.183版・まさちゃん 20:53「②お友達バトルの時は、それぞれがカスタムしている背面デザイン、カードデザインにして！」）');
  {
    const w = wire(), rng = rngOf(9);
    const H = N.host(w.a, rng, null, null, { b: 'sky', f: { k: 'ka', 6: '6a' } }), G = N.guest(w.b, { b: 'star', f: { m: 'mb', 3: '3b' } });
    const hs = seat(H), gs = seat(G);
    check(H.opDz === null && G.opDz === null, 'はじめは 相手の デザインは まだ ない（opDz＝null）');
    H.start(); G.start(); await tick(); await tick(); await tick();
    const gh = JSON.parse(w.log[0][1]), hh = JSON.parse(w.log[1][1]);
    check(w.log[0][0] === 'g' && gh.t === 'hello' && gh.v === 13 && JSON.stringify(gh.dz) === '{"b":"star","f":{"3":"3b","m":"mb"}}' && hh.t === 'hello' && JSON.stringify(hh.dz) === '{"b":"sky","f":{"6":"6a","k":"ka"}}' && N.PROTO === 13,
      'あいさつ（hello）に 自分が えらんだ デザイン（dz：うら・おもて）・版の 番号 10（第4.190版：6 は ターンの はじめ・効果タイムは 1つずつ：ルールが かわった）');
    check(JSON.stringify(H.opDz) === '{"b":"star","f":{"3":"3b","m":"mb"}}' && JSON.stringify(G.opDz) === '{"b":"sky","f":{"6":"6a","k":"ka"}}' && hs.states.join() === 'ready' && gs.states.join() === 'ready,stake',
      'おたがいの デザインが 届く（match.opDz）・あいさつの 流れは 前と 同じ');
    G.join(); await tick(); await tick(); await tick();
    check(hs.ups.length === 1 && gs.ups.length === 1 && hs.ups[0].ev[0].e === 'deal' && !w.log.some(x => JSON.parse(x[1]).t === 'up' && /"dz"/.test(x[1])), '配る ところは 前と 同じ（デザインは あいさつ だけ）');
    H.leave(); await tick(); await tick();
  }
  {
    // dz を 送らない 相手（同じ 版の 番号）と つなぐ：相手の デザインは いつもの（b ''・f {}）
    const w = wire();
    const H = N.host(w.a, rngOf(3), null, null, { b: 'sky', f: { k: 'ka' } }); const hs = seat(H);
    H.start(); w.b.send(JSON.stringify({ t: 'hello', v: N.PROTO })); await tick(); await tick(); await tick();
    check(JSON.stringify(H.opDz) === '{"b":"","f":{}}' && hs.states.join() === 'ready' && JSON.parse(w.log[1][1]).t === 'hello' && JSON.parse(w.log[1][1]).dz.b === 'sky',
      'dz の ない あいさつ → 相手の デザインは いつもの（ホストは 自分の デザインを 送る）');
    const w2 = wire(), G = N.guest(w2.b, null); seat(G);
    G.start(); w2.a.send(JSON.stringify({ t: 'hello', v: N.PROTO, stake: { e: 0, w: 0 } })); await tick(); await tick(); await tick();
    check(JSON.stringify(G.opDz) === '{"b":"","f":{}}' && JSON.stringify(JSON.parse(w2.log[0][1]).dz) === '{"b":"","f":{}}', 'dz の ない ホストとも つながる・デザインを えらんで いない 人は 空の dz');
  }
  {
    const bad = N.dzOf({ b: '<img src=x>', f: { k: 'KA', m: 'ma', x: 'zz', 1: 12, 2: 'a'.repeat(13), 3: '3b', toString: 'x' } });
    check(JSON.stringify(bad) === '{"b":"","f":{"3":"3b","m":"ma"}}' && JSON.stringify(N.dzOf(null)) === '{"b":"","f":{}}' && JSON.stringify(N.dzOf('sky')) === '{"b":"","f":{}}' && JSON.stringify(N.dzOf({ b: 'ice', f: 'x' })) === '{"b":"ice","f":{}}',
      'こわれた デザインは すてる（名前は 英小文字・数字 1〜12字・カードの 種類 だけ・文字で ない ものは すてる）');
    const w = wire(), H = N.host(w.a, rngOf(4)); seat(H);
    H.start(); w.b.send(JSON.stringify({ t: 'hello', v: N.PROTO, dz: { b: '"><script>', f: { k: 'ka', '__proto__': { b: 1 } } } })); await tick(); await tick();
    check(JSON.stringify(H.opDz) === '{"b":"","f":{"k":"ka"}}' && ({}).b === undefined, 'ゲストから こわれた デザインが 届いても、形だけ のこす（あやしい 名前は すてる）');
  }

  console.log('■ コンピュータと 対戦');
  {
    const M = N.cpu(rngOf(7), () => 0), s = seat(M);
    M.start(); await tick();
    check(M.kind === 'cpu' && s.ups.length === 1 && s.view.me === 0 && s.view.op.hand.length === 7 && s.view.turns === 5 && !s.view.op.set, 'はじまった とき：コンピュータは まだ 出して いない');
    await sleep(30);
    check(!s.view.op.set, '画面の 動きが 終わる まで（idle を よぶ まで）コンピュータは 考えない');
    M.idle(); await sleep(30);
    check(!!s.view.op.set && s.view.op.set.k === null, 'idle の あと コンピュータが 出した（中身は 見えない）');
    let guard = 0;
    while (s.view.phase !== 'end' && guard++ < 60) {
      const a = C.decide(s.view, rngOf(guard)); if (a) await M.act(a);
      M.idle(); await sleep(8);
    }
    check(s.view.phase === 'end' && ['win', 'lose', 'draw'].indexOf(s.view.res) >= 0, `さいごまで あそべる（${s.view.res} ${s.view.my.wins}－${s.view.op.wins}）`);
    M.again(); await tick();
    check((s.view.phase === 'set' || s.view.phase === 'six') && s.view.turn === 1 && s.view.my.hand.length === 7 && s.view.my.wins === 0 && s.view.op.wins === 0, `もう 1回 → すぐ 配り直す（コンピュータは 待たない：${s.view.phase}）`);
    M.leave(); M.idle(); await sleep(20);
    const r = await M.act({ t: 'set', u: s.view.my.hand[0].u });
    check(r.ok === false && !s.view.op.set, 'やめた あとは コンピュータも 動かない・手も 通らない');
  }
  console.log('■ 第4.196版：決戦調査（戦ごとに 決まりを かえて 配り直す：m.setOpt → もう 1回）');
  {
    const M = N.cpu(rngOf(11), () => 0, { rig: [[], []] }), s = seat(M);
    M.start(); await tick();
    const st = () => M._.state();
    const h0 = st().p[1].hand.map(c => c.k);
    M.setOpt({ rig: [[], ['1', '1', '1']] });
    for (let i = 0; i < 400 && s.view.phase !== 'end'; i++) {
      const v = s.view, a = v.can.set ? { t: 'set', u: v.my.hand[0].u } : v.can.six ? { t: 'p6', pick: null } : v.can.eff ? { t: 'eff', use: {} } : v.pend && v.pend.mine && v.pend.type === 'k' ? { t: 'k', pick: null } : v.pend && v.pend.mine && v.pend.type === 'm' ? { t: 'm', drop: null } : v.pend && v.pend.mine && v.pend.type === 'swap' ? { t: 'swap', u: v.my.hand[0].u } : v.pend && v.pend.mine && v.pend.type === 'rev' ? { t: 'rev', use: false } : v.pend && v.pend.mine && v.pend.type === 'u5' ? { t: 'u5', drop: null } : null;
      if (a) await M.act(a);
      M.idle(); await sleep(4);
    }
    check(s.view.phase === 'end', '1戦目は さいごまで（決まりを かえても いまの 戦は そのまま）');
    M.again(); await tick();
    const h1 = st().p[1].hand.map(c => c.k);
    check(h1.filter(k => k === '1').length >= 3 && s.view.turn === 1 && s.view.my.hand.length === 7, `2戦目は 新しい 決まりで 配る（敵の 手札に 1 が 3まい 以上：${h1.join('')}・1戦目 ${h0.join('')}）`);
    M.leave();
  }
  console.log('■ 第4.197版：部屋の 決戦宝石（まさちゃん 18:58「お友達バトルの設定で、決戦宝石ありにした場合のみ使用可能 … お互いに何の石を所有してるか見える」・20:21「お友達バトルは1試合で5個使える！」）');
  {
    check(JSON.stringify(N.gmOf({ on: true })) === '{"on":true}' && JSON.stringify(N.gmOf({ on: true, g: 'z' })) === '{"on":true}' && JSON.stringify(N.gmOf(null)) === '{"on":false}' && JSON.stringify(N.gmOf({ on: 1 })) === '{"on":false}' && N.gemOf === undefined,
      '部屋の 決まりの 形を たしかめる（{ on } だけ・おかしい ものは「なし」・持ち込む 宝石は もう ない）');
    const w = wire(), H = N.host(w.a, rngOf(9), { turns: 3, hands: [['1', '2', '3', '4', '7'], ['1', '2', '3', '6', '7']] }, { e: 0, w: 0 }, null, { on: true }), G = N.guest(w.b), hs = seat(H), gs = seat(G);      // 手札 5まい（1ターン目から 使える）
    H.start(); G.start(); await tick(); await tick(); await tick();
    const hh = JSON.parse(w.log[1][1]);
    check(hh.t === 'hello' && JSON.stringify(hh.gm) === '{"on":true}' && JSON.stringify(G.gm) === '{"on":true}' && gs.states.join() === 'ready,stake' && hs.ups.length === 0,
      'ホストの あいさつに「決戦宝石 あり」→ ゲストに 届く（まだ 配らない）');
    G.join(); await tick(); await tick(); await tick();
    const jj = JSON.parse(w.log[2][1]), S = H._.state();
    check(jj.t === 'join' && jj.g === undefined && hs.ups.length === 1 && gs.ups.length === 1, 'ゲストが 決まりを 見て 参加 → 配る（宝石を えらぶ 所は ない）');
    check(S.p[0].gems.join('') === R.GEMS.join('') && S.p[1].gems.join('') === R.GEMS.join('') && S.gpub === true && hs.view.my.gem.list.length === 5 && hs.view.op.gem.list.length === 5 && gs.view.my.gem.list.length === 5 && gs.view.op.gem.list.length === 5,
      '2人とも 5つ（1試合で 1つ 1回ずつ）・おたがいの 宝石が 見える');
    const r1 = await H.act({ t: 'gem', g: '1' }); await tick(); await tick();
    const r2 = await G.act({ t: 'gem', g: '7' }); await tick(); await tick();
    check(r1.ok && r2.ok && gs.view.op.gem.used.join('') === '1' && hs.view.op.gem.used.join('') === '7' && hs.view.my.gem.can.length === 0 && gs.view.my.gem.can.length === 0,
      `2人とも 同じ ターンに 1つずつ 使える・使った 宝石は 相手にも 見える（${r1.why || ''}${r2.why || ''}）`);
    H.leave();
  }
  {
    const w = wire(), H = N.host(w.a, rngOf(9), undefined, { e: 0, w: 0 }, null, { on: false }), G = N.guest(w.b), hs = seat(H), gs = seat(G);
    H.start(); G.start(); await tick(); await tick(); await tick();
    G.join(); await tick(); await tick(); await tick();
    const S = H._.state();
    check(JSON.stringify(G.gm) === '{"on":false}' && hs.ups.length === 1 && S.p[0].gems.length === 0 && S.p[1].gems.length === 0 && hs.view.my.gem === null && gs.view.op.gem === null,
      '決戦宝石 なし の 部屋：宝石 なしで 配る');
    H.leave();
  }
  console.log('結果：', fails.length ? fails.length + '件おかしい' : 'OK');
  process.exit(fails.length ? 1 : 0);
})();
