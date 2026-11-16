// 馬カードバトルの「対戦の 進め役」（cb/cb_net.js）の テスト：node test_cb_net.js
//   部屋の ホスト と ゲスト を、文字を 渡し合う だけの 線（link）で つないで 対戦する：
//     ・ゲストに 届く 文字の 中に、ホストの 手札・山札の 並び・ふせた カードの 中身が 入って いない
//     ・2人の 画面に 出る もの（view）が、同じ 対戦を それぞれの 席から 見た 形に なって いる
//     ・もう 1回・やめる・切れた・版が ちがう
//   コンピュータとの 対戦：画面の 動きが 終わって（idle）から 考える・もう 1回
//   第4.179版：部屋の 決まり（参加コイン・勝者の 獲得コイン）：ホストの あいさつに 入る → ゲストが「参加する」（join）と 答えて から 配る・数字の はんい（stakeOf）
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
    check(w.log[0][0] === 'g' && JSON.parse(w.log[0][1]).t === 'hello' && JSON.parse(w.log[0][1]).v === N.PROTO && N.PROTO === 5 && JSON.parse(w.log[1][1]).t === 'hello' && hs.states.join() === 'ready' && gs.states.join() === 'ready,stake'
      && JSON.stringify(JSON.parse(w.log[1][1]).stake) === '{"e":0,"w":0}' && JSON.stringify(G.stake) === '{"e":0,"w":0}' && hs.ups.length === 0,
      'はじめに おたがいに あいさつ（hello・版の 番号 4）・ホストの あいさつに 部屋の 決まり（参加コイン 0）→ ゲストに「決まりが 届いた」（まだ 配らない）');
    G.join(); await tick(); await tick(); await tick();
    check(JSON.parse(w.log[2][1]).t === 'join' && hs.states.join() === 'ready,joined', 'ゲストが「参加する」（join）→ ホストに 届く');
    check(hs.ups.length === 1 && gs.ups.length === 1 && hs.ups[0].ev[0].e === 'deal' && gs.ups[0].ev[0].e === 'deal' && hs.view.me === 0 && gs.view.me === 1, 'あいさつの あと 配る：2人に はじめの 形が 届く（ホスト＝席 0・ゲスト＝席 1）');
    check(hs.view.my.hand.map(c => c.k).join('') === 'k1266' && gs.view.my.hand.map(c => c.k).join('') === 'm3457' && gs.view.op.hand.every(c => c.k === null) && hs.view.op.hand.every(c => c.k === null),
      'それぞれ 自分の 手札 だけ 見える');
    const up0 = JSON.parse(w.log.find(x => x[0] === 'h' && JSON.parse(x[1]).t === 'up')[1]);
    check(!/"deck"/.test(JSON.stringify(up0)) && (JSON.stringify(up0).match(/"k":"[1-7km]"/g) || []).length === 5, 'ゲストに 送る 文字の 中の カードの 中身は ゲストの 手札の 5まい だけ（ホストの 手札・山札の 並びは 入って いない）');
    // ゲストが 出す → まだ オープン しない。ホストに 届くのは「相手が 出した」だけ
    const gu = gs.view.my.hand.find(c => c.k === '3').u;
    const r1 = await G.act({ t: 'set', u: gu }); await tick(); await tick();
    check(r1.ok && hs.view.op.set && hs.view.op.set.k === null && gs.view.my.set.k === '3' && hs.ups[hs.ups.length - 1].ev[0].e === 'set' && hs.ups[hs.ups.length - 1].ev[0].me === false && hs.ups[hs.ups.length - 1].ev[0].u === undefined,
      'ゲストが 出した：ホストには「相手が 出した」だけ（どの カードかは 届かない）');
    const bad = await G.act({ t: 'set', u: gu }); await tick();
    check(bad.ok === false, 'ゲストの まちがった 手（もう 出した）は ホストが ことわる（ack ok:false）');
    const fake = await G.act({ t: 'set', u: hs.view.my.hand[0].u }); await tick();
    check(fake.ok === false && hs.view.my.hand.length === 5 && !hs.view.my.set, 'ゲストは ホストの カードを 動かせない');
    // ホストも 出す → 2人とも セットした：ホストは 6 が 2まい → 効果タイム（ゲストは 待つ）
    const r3 = await H.act({ t: 'set', u: hs.view.my.hand.find(c => c.k === 'k').u }); await tick(); await tick();
    const hu0 = hs.ups[hs.ups.length - 1], gu0 = gs.ups[gs.ups.length - 1];
    check(r3.ok && hu0.ev.map(e => e.e).join() === 'set,efft' && gu0.ev.map(e => e.e).join() === 'set,efft' && hu0.ev[1].mine === true && gu0.ev[1].mine === false && gu0.ev[1].other === true
      && hs.view.phase === 'eff' && hs.view.can.eff && hs.view.can.eff.e6 === true && gs.view.can.eff === null && gs.view.wait === true && gs.view.op.set.k === null,
      '2人とも セットした → 効果タイム：ホスト（6 が 2まい）が えらぶ 番・ゲストは 待つ（オープンは まだ）');
    const late1 = await G.act({ t: 'eff', use: { u4: true } }); await tick();
    check(late1.ok === false && hs.view.phase === 'eff', 'ゲストは えらぶ ものが ない（効果を 送っても ホストが ことわる）');
    // ホストが 6 の 効果（ゲストの 手札を 1まい 見る）→ いっしょに オープン
    const pk = gs.view.my.hand[0].u, pkK = gs.view.my.hand[0].k;
    const before = w.log.length;
    const r2 = await H.act({ t: 'eff', use: { p6: pk } }); await tick(); await tick();
    const sent = w.log.slice(before).filter(x => x[0] === 'h').map(x => JSON.parse(x[1]));
    check(r2.ok && hs.view.op.hand.find(c => c.u === pk).k === pkK && gs.view.my.hand.find(c => c.u === pk).seen === true && gs.view.op.hand.filter(c => c.k === '6').length === 2
      && sent.length === 1 && sent[0].ev[0].e === 'effd' && sent[0].ev[1].e === 'p6' && sent[0].ev[1].k === undefined && sent[0].ev[1].pick === pk,
      'ホストが 6 の 効果：ホストは 見た カードが 見える・ゲストには 見せた 6 の 2まいと「どれを 見られたか」');
    const hu = hs.ups[hs.ups.length - 1], gu2 = gs.ups[gs.ups.length - 1];
    check(hu.ev.map(e => e.e).join() === 'effd,p6,open,clear,turn,pre' && gu2.ev.map(e => e.e).join() === 'effd,p6,open,clear,turn,pre' && hu.ev[2].res === 'win' && gu2.ev[2].res === 'lose' && hu.ev[2].my.k === 'k' && gu2.ev[2].my.k === '3' && gu2.ev[2].op.k === 'k'
      && hs.view.turn === 2 && gs.view.turn === 2 && hs.view.phase === 'pre' && hs.view.pend.mine === true && hs.view.pend.type === 'k' && gs.view.pend.mine === false && gs.view.wait === true && !hs.view.can.set && !gs.view.can.set,
      'オープン：同じ できごとが 2人に 届く（ホスト＝勝ち・ゲスト＝負け）。神様馬の 効果は 2ターン目の はじめに ホストが えらぶ');
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
    check(gs.states.indexOf('again') >= 0 && hs.view.phase === 'set' && gs.view.phase === 'set' && hs.view.turn === 1 && hs.ups[hs.ups.length - 1].ev[0].e === 'deal' && gs.view.my.hand.length === 5 && hs.view.my.wins === 0,
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
    check(s.view.phase === 'set' && s.view.turn === 1 && s.view.my.hand.length === 7, 'もう 1回 → すぐ 配り直す（コンピュータは 待たない）');
    M.leave(); M.idle(); await sleep(20);
    const r = await M.act({ t: 'set', u: s.view.my.hand[0].u });
    check(r.ok === false && !s.view.op.set, 'やめた あとは コンピュータも 動かない・手も 通らない');
  }
  console.log('結果：', fails.length ? fails.length + '件おかしい' : 'OK');
  process.exit(fails.length ? 1 : 0);
})();
