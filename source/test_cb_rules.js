// 馬カードバトルの ルール（cb/cb_rules.js）と コンピュータ（cb/cb_cpu.js）の テスト：node test_cb_rules.js
//   まさちゃんの ルール（2026/11/15 21:41）：3ターン・手札 5まい・30まい（1〜7 が 4まい ずつ＋神様馬＋幻の馬）・強さ・かぶりは 負け・勝った 枚数・効果 6つ
//   まさちゃんの 直し（23:12）：セットしたら 変えられない・2人とも セットしたら 効果を 使うか えらぶ（効果タイム）・神様馬／幻の馬の 効果は 勝った 次の ターンの はじめ
//   まさちゃんの 直し（23:15）：捨て札を 確認できる（終わった ターンの 捨て札・効果による 捨て札）
//   まさちゃんの 直し（第4.177版・2026/11/16 10:40）：5 は「使った あとの 手札が のこりの ターンの 数より 少なく ならない」とき 使える（3ターン目に 5 と もう 1まい でも 使える）・
//     3 に 効果（手札に 3 が 3まい → 3まいを 見せて、その 1まいと 相手の 手札の くじで えらんだ 1まいを 交換）・どの 効果も 使うか えらべる
//   ＋ 見せて いい こと だけを 渡して いるか（相手の 手札・ふせた カード）・でたらめに 2万回 あそんでも カードが 30まいの まま か
const R = require('./cb/cb_rules.js'), C = require('./cb/cb_cpu.js');
let fails = [];
function check(c, label) { console.log((c ? '  ✅ ' : '  ❌ ') + label); if (!c) fails.push(label); }
// いつも 同じ 並びに なる 乱数（mulberry32）
function rngOf(seed) { let a = seed >>> 0; return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const ks = hand => hand.map(c => c.k).join('');
const U = (S, i, k, n) => S.p[i].hand.filter(c => c.k === k)[n || 0].u;      // プレイヤー i の 手札の k（n まい目）の 番号
const all = S => S.deck.concat(S.discard, S.p[0].hand, S.p[1].hand, S.p[0].set ? [S.p[0].set.c] : [], S.p[1].set ? [S.p[1].set.c] : []);
const sane = S => { const a = all(S), us = new Set(a.map(c => c.u)); const n = {}; a.forEach(c => { n[c.k] = (n[c.k] || 0) + 1; }); return a.length === 30 && us.size === 30 && R.NUMS.every(k => n[k] === 4) && n.k === 1 && n.m === 1; };
const G = (h0, h1, deck) => R.newGame(rngOf(7), { hands: [h0.split(''), h1.split('')], deck: deck ? deck.split('') : undefined });
const set = (S, i, k) => R.act(S, i, { t: 'set', u: U(S, i, k) }, rngOf(3));
const eff = (S, i, use, rng) => R.act(S, i, { t: 'eff', use: use || null }, rng || rngOf(3));      // 効果タイム：使う ものを 決める（null＝使わない）
const names = r => r.ev.map(e => e.e).join();
// テスト用：プレイヤー i の 手札の k を 1まい 捨て札へ（手札の 数を へらした 形を 作る）／山札の 中の k を 1まい 手札へ
const toDis = (S, i, k) => { const P = S.p[i], j = P.hand.findIndex(c => c.k === k), c = P.hand.splice(j, 1)[0]; S.discard.push({ u: c.u, k: c.k, by: i, why: 't', turn: S.turn }); };
const fromDeck = (S, i, k) => { const j = S.deck.findIndex(c => c.k === k); S.p[i].hand.push(S.deck.splice(j, 1)[0]); };

console.log('■ カードと 配り方');
{
  const S = R.newGame(rngOf(1));
  const a = all(S), n = {}; a.forEach(c => { n[c.k] = (n[c.k] || 0) + 1; });
  check(a.length === 30 && R.NUMS.every(k => n[k] === 4) && n.k === 1 && n.m === 1 && R.KINDS.join('') === '1234567km', 'カードは 30まい：1〜7 が 4まい ずつ・神様馬 1まい・幻の馬 1まい');
  check(S.p[0].hand.length === 5 && S.p[1].hand.length === 5 && S.deck.length === 20 && S.discard.length === 0 && S.turn === 1 && S.phase === 'set' && R.TURNS === 3 && R.HAND === 5, '手札は 5まい ずつ・山札 20まい・3ターン');
  const seen = new Set(); for (let s = 1; s <= 200; s++) seen.add(ks(R.newGame(rngOf(s)).p[0].hand)); check(seen.size > 190, `配る たびに 手札が かわる（200回で ${seen.size}通り）`);
  let km = 0, n1 = 0; for (let s = 1; s <= 3000; s++) { const h = R.newGame(rngOf(s + 999)).p[0].hand; if (h.some(c => c.k === 'k')) km++; n1 += h.filter(c => c.k === '1').length; }
  check(Math.abs(km / 3000 - 5 / 30) < 0.03 && Math.abs(n1 / 3000 - 5 * 4 / 30) < 0.06, `かたよらない：神様馬が 手札に 来る 割合 ${(km / 30).toFixed(1)}%（5/30＝16.7%）・1 の 平均 ${(n1 / 3000).toFixed(2)}まい（0.67）`);
  const T = G('1234k', '567m7', '1234567');
  check(ks(T.p[0].hand) === '1234k' && ks(T.p[1].hand) === '567m7' && T.deck.slice(-7).reverse().map(c => c.k).join('') === '1234567' && sane(T), 'テスト用：手札と 山札の 上を 決めて はじめられる（のこりは まぜる）');
}

console.log('■ 強さ');
{
  const P = R.power, c = R.compare;
  check(P('k') === 0 && P('m') === 0 && [1, 2, 3, 4, 5, 6, 7].every(n => P(String(n)) === n), '神様馬 と 幻の馬 が 1番 強い・数字は 1 が 1番 強くて 7 が 1番 弱い');
  let ok = true;
  for (const a of R.KINDS) for (const b of R.KINDS) {
    const r = c(a, b), want = a === b ? 'clash' : P(a) === P(b) ? 'tie' : P(a) < P(b) ? 0 : 1;
    if (r !== want) ok = false;
  }
  check(ok && c('1', '2') === 0 && c('7', '6') === 1 && c('k', '1') === 0 && c('1', 'm') === 1 && c('3', '3') === 'clash' && c('k', 'm') === 'tie' && c('m', 'k') === 'tie',
    'くらべ方（81通り）：強い 方の 勝ち・同じ 数字は かぶり（どちらも 負け）・神様馬 と 幻の馬 は 引き分け');
}

console.log('■ 1ターンの 流れ・3ターンで 勝負');
{
  const S = G('12367', '23456');
  const r0 = set(S, 0, '1');
  check(r0.ok && names(r0) === 'set' && S.phase === 'set' && S.p[0].hand.length === 4 && S.p[0].set && !S.p[1].set, '1人が セット：まだ オープン しない（相手を 待つ）');
  check(!set(S, 0, '2').ok && S.p[0].hand.length === 4, 'セットは 1ターンに 1まい（2まい目は 出せない）');
  const r1 = set(S, 1, '2');
  check(r1.ok && names(r1) === 'set,open,clear,turn' && r1.ev[1].res === 0 && r1.ev[1].wins.join() === '1,0' && r1.ev[1].c.map(x => x.k).join('') === '12' && S.turn === 2 && S.phase === 'set',
    '2人とも セット（使える 効果は ない）→ オープン：1 と 2 → 1 の 勝ち（1勝 0勝）→ 2ターン目へ');
  check(S.discard.map(c => c.k).join('') === '12' && !S.p[0].set && !S.p[1].set && S.p[0].hand.length === 4 && S.p[1].hand.length === 4 && S.deck.length === 20 && sane(S), '出した カードは 捨て札へ・ターンの あいだに 山札から 引かない');
  set(S, 1, '3'); const r2 = set(S, 0, '3');
  check(r2.ev[1].res === 'clash' && r2.ev[1].wins.join() === '1,0', '2ターン目：3 と 3 → かぶり＝どちらも 負け（どちらの 勝ちにも 数えない）');
  set(S, 0, '7'); const r3 = set(S, 1, '6');
  check(names(r3) === 'set,open,clear,end' && r3.ev[1].res === 1 && S.phase === 'end' && S.res === 'draw' && r3.ev[3].res === 'draw' && r3.ev[3].wins.join() === '1,1',
    '3ターン目：7 と 6 → 6 の 勝ち → 1勝 1勝 ＝ 同点で おわり');
  check(!set(S, 0, '2').ok && R.act(S, 0, { t: 'eff', use: null }).why === 'end', 'おわった あとは 何も 打てない');
  const T = G('12367', '23677'); set(T, 0, '1'); set(T, 1, '2'); set(T, 0, '2'); set(T, 1, '3');
  check(T.p[0].wins === 2 && T.phase === 'set' && T.turn === 3, '先に 2勝 しても 3ターン目を やる');
  set(T, 0, '3'); set(T, 1, '6');
  check(T.phase === 'end' && T.res === 0 && T.p[0].wins === 3 && R.view(T, 0).res === 'win' && R.view(T, 1).res === 'lose', '勝った 枚数が 多い 方の 勝ち（3勝 0勝）');
  const K = G('k2367', 'm1236'); set(K, 0, 'k'); const rk = set(K, 1, 'm');
  check(rk.ev[1].res === 'tie' && K.p[0].wins === 0 && K.p[1].wins === 0 && !K.pend && K.turn === 2 && K.phase === 'set', '神様馬 と 幻の馬 → 引き分け（どちらの 勝ちにも 数えない・効果も 出ない）');
}

console.log('■ セットしたら もう 変えられない（まさちゃん 23:12）');
{
  const S = G('12367', '23456'); const u1 = U(S, 0, '1');
  set(S, 0, '1');
  const v = R.view(S, 0);
  check(v.can.set === false && v.wait === true && v.my.set.u === u1 && v.my.set.k === '1' && R.legal(S, 0).length === 0, 'セットした あと：自分が 打てる 手は ない（相手を 待つ だけ）');
  check(R.act(S, 0, { t: 'set', u: U(S, 0, '2') }).why === 'set' && R.act(S, 0, { t: 'unset' }).why === 'type' && R.act(S, 0, { t: 'swap', u: U(S, 0, '2') }).why === 'swap' && R.act(S, 0, { t: 'eff', use: null }).why === 'eff'
    && S.p[0].set.c.u === u1 && ks(S.p[0].hand) === '2367', 'ほかの カードに 変える 手・もどす 手は ない（何を 送っても セットした カードは そのまま）');
  // 効果タイムの あいだも 自分では 変えられない（変わるのは 5 の 効果〈自分で 使う〉と 相手の 4 の 効果 だけ）
  const E = G('66123', '12345'); const e1 = U(E, 0, '1'); set(E, 0, '1'); set(E, 1, '2');
  check(E.phase === 'eff' && R.act(E, 0, { t: 'set', u: U(E, 0, '2') }).why === 'set' && R.act(E, 1, { t: 'set', u: U(E, 1, '1') }).why === 'set' && E.p[0].set.c.u === e1, '効果タイムの あいだも セットし直せない');
}

console.log('■ 効果タイム：2人とも セットが 終わったら、効果を 使うか えらぶ（まさちゃん 23:12）');
{
  const S = G('66123', '12345');
  check(R.act(S, 0, { t: 'x7' }).why === 'type' && R.act(S, 0, { t: 'p6', pick: U(S, 1, '1') }).why === 'type' && R.act(S, 0, { t: 'set5', u: 1, drop: 2 }).why === 'type' && R.act(S, 0, { t: 'eff', use: { p6: U(S, 1, '1') } }).why === 'eff'
    && R.view(S, 0).can.eff === null, 'セットの 前は 効果を 使えない（効果を えらぶのは 2人とも セットした あと だけ）');
  const r0 = set(S, 0, '1');
  check(names(r0) === 'set' && S.phase === 'set' && R.view(S, 0).can.eff === null && R.act(S, 0, { t: 'eff', use: null }).why === 'eff', '自分だけ セットした：まだ 効果は えらべない（相手の セットを 待つ）');
  const r1 = set(S, 1, '2');
  check(names(r1) === 'set,efft' && S.phase === 'eff' && r1.ev[1].has.join() === 'true,false', '2人とも セットした → 効果タイム（オープンは まだ）');
  const v0 = R.view(S, 0), v1 = R.view(S, 1);
  check(v0.can.eff && v0.can.eff.e6 === true && !v0.can.eff.e5 && !v0.can.eff.e7 && !v0.can.eff.e4 && v0.wait === false && R.legal(S, 0).join() === 'eff', '使える 効果が ある 人：使うか えらぶ 番（6 が 2まい → 6 の 効果）');
  check(v1.can.eff === null && v1.wait === true && R.legal(S, 1).length === 0 && R.act(S, 1, { t: 'eff', use: null }).why === 'eff', '使える 効果が ない 人：えらぶ ものは ない（相手を 待つ）');
  const e = [R.evFor(r1.ev, 0)[1], R.evFor(r1.ev, 1)[1]];
  check(e[0].mine === true && e[0].other === false && e[1].mine === false && e[1].other === true, '効果タイムの 知らせ：自分に えらぶ ものが あるか・相手が えらんで いるか');
  const r2 = eff(S, 0, null);
  check(r2.ok && names(r2) === 'effd,open,clear,turn' && r2.ev[2 - 1].res === 0 && S.turn === 2 && ks(S.p[0].hand) === '6623', '「使わない」を えらんだ → そのまま オープン（1 と 2 → 1 の 勝ち）');
  // 2人とも えらぶ ものが ある：1人が 決めても まだ 行わない（2人とも 決めて から いっしょに）
  const B = G('66123', '77712', '345'); set(B, 0, '1'); set(B, 1, '2');
  check(B.phase === 'eff' && R.view(B, 0).can.eff.e6 && R.view(B, 1).can.eff.e7 && !R.view(B, 0).wait && !R.view(B, 1).wait, '2人とも 使える 効果が ある（6 が 2まい ／ 7 が 3まい）');
  const tb = U(B, 1, '1'), rb0 = eff(B, 0, { p6: tb });
  check(rb0.ok && names(rb0) === 'effd' && B.phase === 'eff' && R.view(B, 0).wait === true && R.view(B, 0).can.eff === null && R.view(B, 0).op.hand.every(c => c.k === null) && R.act(B, 0, { t: 'eff', use: null }).why === 'eff',
    '1人が 決めた：効果は まだ 出ない（相手が 決める まで 待つ・決め直せない）');
  const eo = R.evFor(rb0.ev, 1)[0], vo = JSON.stringify(R.view(B, 1));
  check(JSON.stringify(eo) === '{"e":"effd","me":false}' && vo.indexOf('p6') < 0 && vo.indexOf('"use"') < 0 && R.view(B, 1).my.hand.every(c => !c.seen), '相手には「決めた」こと だけ 伝わる（何を 使うかは わからない）');
  const rb1 = eff(B, 1, { x7: true }, rngOf(5));
  check(rb1.ok && names(rb1) === 'effd,p6,x7,open,clear,turn' && rb1.ev[1].who === 0 && rb1.ev[1].k === '1' && rb1.ev[2].who === 1 && rb1.ev[2].drew.map(c => c.k).join('') === '345' && sane(B),
    '2人とも 決めた → 6 → 7 の 順に いっしょに 行って から オープン');
  // だれも 使える 効果が ない → 効果タイムは とばす
  const N = G('12367', '23456'); set(N, 0, '1'); const rn = set(N, 1, '2');
  check(names(rn) === 'set,open,clear,turn', 'だれも 使える 効果が ない ときは、効果タイムを とばして オープン');
}

console.log('■ 7：手札に 3まい そろったら 3まいを 山札に もどして 3まい 引く');
{
  const S = G('77712', '12345', '346'); set(S, 0, '1'); set(S, 1, '2');
  check(S.phase === 'eff' && R.view(S, 0).can.eff.e7 === true && R.view(S, 1).can.eff === null, '7 が 3まい ある 人 だけ 使える（セットした あとの 手札で 数える）');
  const u7 = S.p[0].hand.filter(c => c.k === '7').map(c => c.u);
  const r = eff(S, 0, { x7: true }, rngOf(5));
  check(r.ok && names(r) === 'effd,x7,open,clear,turn' && r.ev[1].drew.map(c => c.k).join('') === '346' && ks(S.p[0].hand).split('').sort().join('') === '2346' && S.deck.length === 20 && sane(S), '7 を 3まい もどして、山札の 上から 3まい（3・4・6）を 引いた（手札 4まい・山札 20まい の まま）');
  const back = S.deck.filter(c => c.k === '7'); check(back.length === 4 && !S.deck.some(c => u7.indexOf(c.u) >= 0), 'もどした 7 は 山札の 中（番号は 新しく なる＝どれが もどした 7 か 追えない）');
  const e1 = R.evFor(r.ev, 1)[1]; check(e1.e === 'x7' && e1.me === false && e1.n === 3 && e1.drew === undefined && R.evFor(r.ev, 0)[1].drew.length === 3, '相手には「3まい 交換した」こと だけ（引いた カードは 見せない）');
  const A = G('77712', '12345'); set(A, 0, '7'); const ra = set(A, 1, '2');
  check(names(ra) === 'set,open,clear,turn', '7 を セットして 手札の 7 が 2まいに なったら 使えない（効果タイムは 出ない）');
  const K = G('77712', '12345'); set(K, 0, '1'); set(K, 1, '2'); const rk = eff(K, 0, {});
  check(rk.ok && names(rk) === 'effd,open,clear,turn' && ks(K.p[0].hand) === '7772' && K.deck.length === 20, '使わなくても いい（手札は そのまま）');
  const W = G('66123', '12345'); set(W, 0, '1'); set(W, 1, '2'); check(eff(W, 0, { x7: true }).why === 'e7' && W.phase === 'eff', '7 が 3まい ない 人が「7 の 効果」と 言っても 受けつけない');
  const T2 = G('17772', '12345'); set(T2, 0, '2'); set(T2, 1, '1'); eff(T2, 0, null); set(T2, 0, '1'); set(T2, 1, '2');
  check(T2.turn === 2 && T2.phase === 'eff' && R.view(T2, 0).can.eff.e7 === true && eff(T2, 0, { x7: true }).ok && T2.p[0].hand.length === 3 && sane(T2), '2ターン目（セットした あとの 手札が 7・7・7）でも 使える');
  let re = 0; for (let s = 1; s <= 400; s++) { const X = G('77712', '12345'); set(X, 0, '1'); set(X, 1, '2'); const before = new Set(X.p[0].hand.filter(c => c.k === '7').map(c => c.u)); eff(X, 0, { x7: true }, rngOf(s)); if (X.p[0].hand.some(c => before.has(c.u)) || X.p[0].hand.length !== 4) re++; }
  check(re === 0, 'もどした 7 を すぐ 引き直さない（先に 3まい 引いて から もどす：400回）');
}

console.log('■ 6：手札の 6 を 2まい 見せると、相手の 手札を 1まい 見られる');
{
  const S = G('66123', '12345'); set(S, 0, '1'); set(S, 1, '2');
  check(R.view(S, 0).can.eff.e6 && R.view(S, 1).can.eff === null, '6 が 2まい ある 人 だけ 使える');
  const tgt = U(S, 1, '4'), six = S.p[0].hand.filter(c => c.k === '6').map(c => c.u);
  check(R.view(S, 0).op.hand.every(c => c.k === null), '見る 前：相手の 手札は ぜんぶ 見えない');
  check(eff(S, 0, { p6: 9999 }).why === 'pick' && eff(S, 0, { p6: U(S, 0, '2') }).why === 'pick' && S.phase === 'eff', '相手の 手札に ない カードは 見られない');
  const r = eff(S, 0, { p6: tgt });
  check(r.ok && names(r) === 'effd,p6,open,clear,turn' && r.ev[1].k === '4' && r.ev[1].pick === tgt && r.ev[1].six.join() === six.join(), '相手の 手札の 1まい（4）を 見た');
  const v0 = R.view(S, 0), v1 = R.view(S, 1);
  check(v0.op.hand.filter(c => c.k !== null).map(c => c.u + c.k).join() === tgt + '4' && v0.op.hand.filter(c => c.k === null).length === 3, '見た カード だけ 見える ままに なる（ほかの 3まいは 見えない）');
  check(v1.op.hand.filter(c => c.k === '6').map(c => c.u).join() === six.join() && v1.op.hand.filter(c => c.k === null).length === 2 && v1.my.hand.find(c => c.u === tgt).seen === true && v1.my.hand.filter(c => c.seen).length === 1,
    '相手には 見せた 6 の 2まいが 見える・見られた カードに しるし');
  const e1 = R.evFor(r.ev, 1)[1]; check(e1.me === false && e1.k === undefined && e1.pick === tgt && R.evFor(r.ev, 0)[1].k === '4', '見られた 人には「どの カードを 見られたか」だけ（中身は 自分の カード なので 書かない）');
  check(ks(S.p[0].hand) === '6623', '6 は 手札に のこる');
  const O = G('61234', '12367'); set(O, 0, '1'); check(names(set(O, 1, '2')) === 'set,open,clear,turn', '6 が 1まい では 使えない');
  const Q = G('66123', '12345'); set(Q, 0, '6'); check(names(set(Q, 1, '2')) === 'set,open,clear,turn', '6 を セットして 手札の 6 が 1まいに なったら 使えない');
  // 見た カードが 場に 出たら、場の カードが 何か わかる
  R.act(S, 1, { t: 'set', u: tgt });
  check(R.view(S, 0).op.set.k === '4' && R.view(S, 0).op.hand.every(c => c.k === null), '見た カードを 相手が セットした → その カードだと わかる');
  set(S, 0, '2');
  check(S.phase === 'eff' && R.view(S, 0).can.eff.e6 === true && R.view(S, 1).can.eff.e4 === true, '次の ターンも（6 が 2まい あれば）また 使える');
}

console.log('■ 5：5 と 手札 1まいを 捨てて 山札から 1まい セット（使った あとの 手札が のこりの ターンの 数より 少なく ならない とき：第4.177版）');
{
  const S = G('51237', '12346', 'k'); const u5 = U(S, 0, '5'), u7 = U(S, 0, '7');
  set(S, 0, '5'); set(S, 1, '1');
  check(S.phase === 'eff' && R.view(S, 0).can.eff.e5 === true && S.p[0].hand.length === 4, '1ターン目（5 を セットした あと 手札 4まい）は 使える');
  check(eff(S, 0, { u5: 999 }).why === 'drop' && eff(S, 0, { u5: u5 }).why === 'drop' && S.phase === 'eff', '捨てる カードが 手札に ない ときは 使えない（セットした 5 自身も 選べない）');
  const r = eff(S, 0, { u5: u7 });
  check(r.ok && names(r) === 'effd,u5,open,clear,turn,pre' && r.ev[1].five.k === '5' && r.ev[1].five.u === u5 && r.ev[1].drop.k === '7' && ks(S.p[0].hand) === '123' && S.deck.length === 19 && sane(S),
    '5 と 7 を 捨てて、山札の 上を ふせて セット（手札 3まい・山札 19まい）');
  check(r.ev[2].c[0].k === 'k' && r.ev[2].res === 0 && S.discard.map(c => c.k).join('') === '57k1' && S.pend && S.pend.type === 'k', 'オープン：山札から 来た 神様馬で 勝ち（神様馬の 効果は 次の ターンの はじめ）');
  const e1 = R.evFor(r.ev, 1)[1]; check(e1.five.k === '5' && e1.drop.k === '7' && e1.me === false, '捨てた 2まい（5 と 7）は 相手にも 見える（捨て札）');
  // 山札から 来た カードは オープンまで だれにも 見えない（相手の 4 の 効果で 止まった 所で たしかめる）
  const Z = G('51237', '41236', 'k'); set(Z, 0, '5'); set(Z, 1, '4');
  check(Z.phase === 'eff' && R.view(Z, 0).can.eff.e5 && R.view(Z, 1).can.eff.e4, '5 を セットした 人と 4 を セットした 人：2人とも えらぶ');
  eff(Z, 0, { u5: U(Z, 0, '7') }); const rz = eff(Z, 1, { u4: true });
  check(names(rz) === 'effd,u5,first' && Z.phase === 'swap' && Z.pend.who === 0 && Z.p[0].set.blind === true && Z.p[0].set.c.k === 'k', '5 → 4 の 順：山札から ふせた カードも、相手の 4 の 効果で 交換に なる');
  check(R.view(Z, 0).my.set.k === null && R.view(Z, 0).my.set.blind === true && R.view(Z, 1).op.set.k === null && JSON.stringify(R.view(Z, 0)).indexOf('"k":"k"') < 0, '山札から 来た カードは オープンまで だれにも 見えない（自分にも）');
  R.act(Z, 0, { t: 'swap', u: U(Z, 0, '1') });
  check(Z.p[0].hand.some(c => c.k === 'k') && Z.p[0].wins === 1 && Z.turn === 2, '交換：山札から 来て いた カード（神様馬）は 手札に 入る・出した 1 が 4 に 勝つ');
  // 第4.177版（まさちゃん 2026/11/16 10:40「手札がバトルターンに必要な枚数を切らない場合に発動できる」）：2ターン目・3ターン目も 使える
  const T = G('51237', '12346', 'k'); set(T, 0, '1'); set(T, 1, '2'); set(T, 0, '5'); const rt = set(T, 1, '1');
  check(names(rt) === 'set,efft' && T.turn === 2 && T.p[0].hand.length === 3 && R.view(T, 0).can.eff.e5 === true && R.view(T, 1).can.eff === null,
    '2ターン目（5 を セットした あと 手札 3まい → 使うと 2まい・のこり 1ターン）も 使える（前は 1ターン目 だけ）');
  const rt2 = eff(T, 0, { u5: U(T, 0, '7') });
  check(rt2.ok && names(rt2) === 'effd,u5,open,clear,turn,pre' && ks(T.p[0].hand) === '23' && rt2.ev[2].c[0].k === 'k' && T.turn === 3 && sane(T), '2ターン目に 使う：5 と 7 を 捨てて、山札から 来た 神様馬で 勝ち（手札 2まい で 3ターン目へ）');
  // まさちゃんの 例「最後のターンに5ともう一枚ある場合、フィールドの5と手札を一枚捨てて効果発動」
  const L = G('51237', '12346', '2'); set(L, 0, '1'); set(L, 1, '2'); set(L, 0, '2'); set(L, 1, '1'); toDis(L, 0, '3');
  check(L.turn === 3 && ks(L.p[0].hand) === '57', '（3ターン目：手札は 5 と 7 の 2まい だけ に した）');
  set(L, 0, '5'); const rl = set(L, 1, '3');
  check(names(rl) === 'set,efft' && L.p[0].hand.length === 1 && R.view(L, 0).can.eff.e5 === true, '3ターン目：5 と もう 1まい だけ でも 使える（5 を セット → 手札 1まい → 使うと 0まい・のこり 0ターン）');
  const rl2 = eff(L, 0, { u5: U(L, 0, '7') });
  check(rl2.ok && names(rl2) === 'effd,u5,open,clear,end' && L.p[0].hand.length === 0 && rl2.ev[2].c[0].k === '2' && rl2.ev[2].res === 0 && sane(L), '使う：5 と さいごの 手札（7）を 捨てて、山札の 2 で 勝負（2 が 3 に 勝ち）');
  const L0 = G('51237', '12346'); set(L0, 0, '1'); set(L0, 1, '2'); set(L0, 0, '2'); set(L0, 1, '1'); toDis(L0, 0, '3'); toDis(L0, 0, '7'); set(L0, 0, '5'); const rl0 = set(L0, 1, '3');
  check(names(rl0) === 'set,open,clear,end' && rl0.ev[1].c[0].k === '5', '3ターン目：手札が 5 だけ（セットした あと 0まい）→ いっしょに 捨てる 手札が ない ので 使えない（効果タイムは 出ない）');
  // 使った あとの 手札が のこりの ターンの 数より 少なく なる ときは 使えない
  const N1 = G('51237', '12346'); toDis(N1, 0, '1'); toDis(N1, 0, '2'); set(N1, 0, '5'); const rn1 = set(N1, 1, '1');
  check(names(rn1) === 'set,open,clear,turn' && N1.p[0].hand.length === 2, '1ターン目で 手札が 2まい（使うと 1まい・のこり 2ターン）→ 使えない');
  const N1b = G('51237', '12346'); toDis(N1b, 0, '1'); set(N1b, 0, '5'); const rn1b = set(N1b, 1, '1');
  check(names(rn1b) === 'set,efft' && N1b.p[0].hand.length === 3 && R.view(N1b, 0).can.eff.e5 === true, '1ターン目で 手札が 3まい（使うと 2まい・のこり 2ターン）→ 使える（ちょうど 足りる）');
  const N2 = G('51237', '12346'); set(N2, 0, '1'); set(N2, 1, '2'); toDis(N2, 0, '2'); toDis(N2, 0, '3'); set(N2, 0, '5'); const rn2 = set(N2, 1, '1');
  check(N2.turn === 3 && names(rn2) === 'set,open,clear,turn' && N2.p[0].hand.length === 1, '2ターン目で 手札が 1まい（使うと 0まい・のこり 1ターン）→ 使えない');
  const ND = G('51237', '12346'); set(ND, 0, '5'); ND.discard.push(...ND.deck.splice(0).map(c => ({ u: c.u, k: c.k, by: 0, why: 't', turn: 1 }))); const rnd0 = set(ND, 1, '1');
  check(names(rnd0) === 'set,open,clear,turn', '山札が ない ときは 使えない');
  const X = G('51237', '12346'); set(X, 0, '5'); set(X, 1, '1'); const rx = eff(X, 0, null);
  check(rx.ok && names(rx) === 'effd,open,clear,turn' && rx.ev[1].c[0].k === '5' && ks(X.p[0].hand) === '1237', '5 を セットして、効果を 使わなくても いい（5 の まま オープン）');
  const Y = G('12367', '12345'); set(Y, 0, '1'); set(Y, 1, '4'); check(eff(Y, 1, { u5: U(Y, 1, '1') }).why === 'e5', '5 を セットして いない 人が「5 の 効果」と 言っても 受けつけない');
  // 5 と 7 を いっしょに
  const C7 = G('57771', '12346', '2346'); set(C7, 0, '5'); set(C7, 1, '1');
  check(R.view(C7, 0).can.eff.e5 && R.view(C7, 0).can.eff.e7 && eff(C7, 0, { u5: U(C7, 0, '7'), x7: true }).why === 'e7' && C7.phase === 'eff', '5 の 効果で 7 を 捨てると 7 が 2まいに なる → 7 の 効果とは いっしょに 使えない');
  const rc = eff(C7, 0, { u5: U(C7, 0, '1'), x7: true }, rngOf(4));
  check(rc.ok && names(rc) === 'effd,u5,x7,open,clear,turn' && rc.ev[2].drew.map(c => c.k).join('') === '346' && rc.ev[3].c[0].k === '2' && ks(C7.p[0].hand).split('').sort().join('') === '346' && sane(C7), '5 の 効果（1 を 捨てる）→ 7 の 効果 の 順に 両方 使える');
  const C4 = G('57777', '12346'); set(C4, 0, '5'); set(C4, 1, '1'); const r4 = eff(C4, 0, { u5: U(C4, 0, '7'), x7: true }, rngOf(4));
  check(r4.ok && C4.p[0].hand.length === 3 && !C4.p[0].hand.some(c => c.k === '7' && c.u <= 5) && sane(C4), '7 が 4まい ある ときは、1まいを 5 の 効果で 捨てて、のこりの 3まいを 交換できる');
}

console.log('■ 3：手札に 3 が 3まい → 3まいを 見せて、その 1まいと 相手の 手札の 1まい（くじ）を 交換（第4.177版）');
{
  const mk = () => { const S = G('33312', '4567k'); set(S, 0, '1'); set(S, 1, '7'); return S; };
  const S = mk(), t3 = S.p[0].hand.filter(c => c.k === '3').map(c => c.u), h1 = S.p[1].hand.map(c => c.u);
  check(S.phase === 'eff' && JSON.stringify(R.view(S, 0).can.eff) === '{"e6":false,"e5":false,"e7":false,"e3":true,"e4":false}' && R.view(S, 1).can.eff === null && R.view(S, 1).wait === true,
    '3 が 3まい（セットした あとの 手札）→ 効果タイムで「3 の 効果」を 使える（相手は 待つ）');
  const r = eff(S, 0, { x3: true }, rngOf(5)), e = r.ev[1];
  check(r.ok && names(r) === 'effd,x3,open,clear,turn' && e.who === 0 && e.three.join() === t3.join() && e.give.k === '3' && t3.indexOf(e.give.u) >= 0 && h1.indexOf(e.take.u) >= 0 && '456k'.indexOf(e.take.k) >= 0,
    `使う：見せた 3まい・わたした 3・相手の 手札から もらった 1まい（${e.take.k}）が 出来事に 入る`);
  check(S.p[0].hand.length === 4 && S.p[1].hand.length === 4 && S.p[0].hand.filter(c => c.k === '3').length === 2 && S.p[0].hand.some(c => c.u === e.take.u) && S.p[1].hand.some(c => c.u === e.give.u) && !S.p[1].hand.some(c => c.u === e.take.u) && sane(S),
    '交換した あと：手札の 数は 2人とも そのまま（4まい）・自分は 3 が 2まい ＋ もらった カード・相手は 3 を 1まい もらう');
  const v0 = R.view(S, 0), v1 = R.view(S, 1), seen0 = v0.my.hand.filter(c => c.seen).map(c => c.u).sort().join(), want0 = t3.filter(u => u !== e.give.u).concat([e.take.u]).sort().join();
  check(seen0 === want0 && v0.my.hand.find(c => c.k === '2').seen === false, '見せた 3（手札に のこる 2まい）と もらった カードは 相手に 知られて いる（目の しるし）・見せて いない 2 は 知られて いない');
  check(v0.op.hand.filter(c => c.k != null).map(c => c.u).join() === String(e.give.u) && v0.op.hand.find(c => c.u === e.give.u).k === '3' && v1.op.hand.filter(c => c.k != null).map(c => c.u).sort().join() === want0,
    'わたした 3 は 相手の 手札の 中で 表に 見える（ほかの 相手の 手札は 見えない）・相手からは 見せた 3 と もと 自分の カードが 表に 見える');
  const e0 = R.evFor(r.ev, 0)[1], e1 = R.evFor(r.ev, 1)[1];
  check(e0.me === true && e1.me === false && [e0, e1].every(x => x.three.join() === t3.join() && x.give.u === e.give.u && x.take.u === e.take.u && x.take.k === e.take.k), '出来事は 2人とも 同じ 中身を 受け取る（見せた 3まい・交換した 2まい：どちらも 2人が 知って いる カード）');
  const got = {}; for (let sd = 1; sd <= 400; sd++) { const X = mk(), q = eff(X, 0, { x3: true }, rngOf(sd)); got[q.ev[1].take.k] = (got[q.ev[1].take.k] || 0) + 1; }
  check(Object.keys(got).sort().join('') === '456k' && Object.values(got).every(n => n > 60 && n < 140), `もらう カードは くじ（えらべない）：400回で 4まいの どれも 同じ ぐらい（${JSON.stringify(got)}）`);
  const N = mk(), rn = eff(N, 0, null);
  check(rn.ok && names(rn) === 'effd,open,clear,turn' && ks(N.p[0].hand) === '3332' && ks(N.p[1].hand) === '456k', '使わなくても いい（「使わない」→ 交換しない）');
  const A = G('33125', '4567k'); set(A, 0, '1'); const ra = set(A, 1, '7');
  check(names(ra) === 'set,open,clear,turn', '3 が 2まい では 使えない（効果タイムは 出ない）');
  const B = G('33312', '4567k'); set(B, 0, '3'); const rb = set(B, 1, '7');
  check(names(rb) === 'set,open,clear,turn', '3 を セットして 手札の 3 が 2まいに なったら 使えない（セットした あとの 手札で 数える）');
  const W = G('12456', '33312'); set(W, 0, '1'); set(W, 1, '2');
  check(W.phase === 'eff' && R.view(W, 0).can.eff === null && R.view(W, 1).can.eff.e3 === true && eff(W, 0, { x3: true }).why === 'eff' && eff(W, 1, { x3: true }, rngOf(2)).ok && W.p[1].hand.filter(c => c.k === '3').length === 2,
    '席 1 の 人も 同じ ように 使える・3 が そろって いない 人が「3 の 効果」と 言っても 受けつけない');
  // 5 と いっしょに
  const C = G('53331', '12467', '2'); set(C, 0, '5'); set(C, 1, '1');
  check(R.view(C, 0).can.eff.e5 && R.view(C, 0).can.eff.e3 && eff(C, 0, { u5: U(C, 0, '3'), x3: true }).why === 'e3' && C.phase === 'eff', '5 の 効果で 3 を 捨てると 3 が 2まいに なる → 3 の 効果とは いっしょに 使えない');
  const rc = eff(C, 0, { u5: U(C, 0, '1'), x3: true }, rngOf(4));
  check(rc.ok && names(rc) === 'effd,u5,x3,open,clear,turn' && rc.ev[1].drop.k === '1' && rc.ev[3].c[0].k === '2' && C.p[0].hand.filter(c => c.k === '3').length === 2 && C.p[0].hand.length === 3 && sane(C), '5 の 効果（1 を 捨てる）→ 3 の 効果 の 順に 両方 使える');
  const C4 = G('53333', '12467'); set(C4, 0, '5'); set(C4, 1, '1'); const r4 = eff(C4, 0, { u5: U(C4, 0, '3'), x3: true }, rngOf(4));
  check(r4.ok && names(r4).indexOf('u5,x3') > 0 && C4.p[0].hand.length === 3 && C4.p[0].hand.filter(c => c.k === '3').length === 2 && sane(C4), '3 が 4まい ある ときは、1まいを 5 の 効果で 捨てて、のこりの 3まいで 交換できる');
  // 順番：6 → 5 → 7 → 3 → 4
  const O = G('43331', '66125'); set(O, 0, '4'); set(O, 1, '5');
  eff(O, 1, { p6: U(O, 0, '1'), u5: U(O, 1, '2') }); const ro = eff(O, 0, { x3: true, u4: true }, rngOf(9));
  check(names(ro) === 'effd,p6,u5,x3,first' && O.phase === 'swap', '行う 順：6 → 5 → 3 → 4（3 の 交換の あとで 4 の 効果）');
  // 不発：相手の 手札が なくなって いた（相手が 同じ 効果タイムの 5 の 効果で さいごの 手札を 捨てた）
  const F = G('33312', '51246'); set(F, 0, '1'); set(F, 1, '1'); eff(F, 0, null); set(F, 0, '2'); set(F, 1, '2'); eff(F, 0, null); toDis(F, 1, '4'); fromDeck(F, 0, '6');
  check(F.turn === 3 && ks(F.p[0].hand) === '3336' && ks(F.p[1].hand) === '56', '（3ターン目：自分は 3・3・3・6／相手は 5・6 に した）');
  set(F, 0, '6'); set(F, 1, '5'); eff(F, 1, { u5: U(F, 1, '6') }); const rf = eff(F, 0, { x3: true });
  check(rf.ok && names(rf) === 'effd,u5,fizz,open,clear,end' && rf.ev[2].k === '3' && rf.ev[2].who === 0 && ks(F.p[0].hand) === '333' && sane(F), '相手の 手札が 先に なくなった ときは 不発（交換しない・カードは そのまま）');
}

console.log('■ 4：最初に 公開すると、相手は セットした カードを 手札の 1まいと 交換する');
{
  const S = G('41236', '15677');
  set(S, 1, '1'); const rs = set(S, 0, '4');
  check(names(rs) === 'set,efft' && S.phase === 'eff' && R.view(S, 0).can.eff.e4 === true && R.view(S, 1).can.eff === null && S.p[0].set.up === false && R.view(S, 1).op.set.k === null, '4 を セット：2人とも セットした あとで、効果を 使うか えらぶ（まだ ふせた まま）');
  const r = eff(S, 0, { u4: true });
  check(r.ok && names(r) === 'effd,first' && S.phase === 'swap' && S.pend.who === 1 && S.p[0].set.up === true && R.view(S, 1).op.set.k === '4' && R.view(S, 1).pend.mine === true && R.view(S, 0).wait === true,
    '4 の 効果を 使う：4 が 表に なって、相手が 交換する 番（オープンは まだ）');
  check(!R.act(S, 0, { t: 'swap', u: U(S, 0, '1') }).ok && !set(S, 1, '5').ok, '交換するのは 相手 だけ・ふつうの セットは もう できない');
  const u5 = U(S, 1, '5');
  const r2 = R.act(S, 1, { t: 'swap', u: u5 });
  check(r2.ok && names(r2) === 'swap,open,clear,turn' && r2.ev[1].c.map(x => x.k).join('') === '45' && r2.ev[1].res === 0 && S.p[0].wins === 1 && ks(S.p[1].hand).split('').sort().join('') === '1677',
    '相手は 1 を 手札に もどして 5 を 出した → 4 と 5 で 4 の 勝ち（もどした 1 は 手札に のこる）');
  const B = G('41236', '41567'); set(B, 0, '4'); set(B, 1, '4'); eff(B, 0, { u4: true }); const rb = eff(B, 1, { u4: true });
  check(names(rb) === 'effd,first2,open,clear,turn' && rb.ev[2].res === 'clash' && B.p[0].wins === 0 && B.p[1].wins === 0, '両方が 4 の 効果を 使った → 打ち消し（交換なし）→ 4 と 4 で どちらも 負け');
  const N = G('41236', '15677'); set(N, 0, '4'); set(N, 1, '1'); const rn = eff(N, 0, null);
  check(names(rn) === 'effd,open,clear,turn' && rn.ev[1].res === 1, '効果を 使わなければ ふつうに オープン（4 と 1 → 1 の 勝ち）');
  const F = G('66123', '12347'); set(F, 0, '1'); set(F, 1, '2'); check(eff(F, 0, { u4: true }).why === 'e4' && F.phase === 'eff', '4 を セットして いない 人が「4 の 効果」と 言っても 受けつけない');
  const W = G('41236', '45677'); set(W, 1, '4'); set(W, 0, '4'); eff(W, 1, null); eff(W, 0, { u4: true });
  check(W.phase === 'swap' && W.pend.who === 1, '相手も 4 を セットして いた（効果は 使わない）→ 相手は 交換する');
  R.act(W, 1, { t: 'swap', u: U(W, 1, '5') });
  check(W.p[0].wins === 1 && W.p[1].hand.some(c => c.k === '4'), '交換して 5 を 出した → 4 の 勝ち');
}

console.log('■ 神様馬：使って 勝ったら、次の ターンの はじめに、相手の 手札を 1まい 見られる（まさちゃん 23:12）');
{
  const S = G('k2367', '12345'); set(S, 0, 'k'); const r = set(S, 1, '1');
  check(names(r) === 'set,open,clear,turn,pre' && S.turn === 2 && S.phase === 'pre' && S.pend.type === 'k' && S.pend.who === 0 && r.ev[4].type === 'k' && r.ev[4].who === 0 && !S.p[0].set && !S.p[1].set,
    '神様馬で 勝った → 片付けて 2ターン目に 入って から、効果を 使うか 決める 番');
  check(R.view(S, 0).pend.mine && R.view(S, 0).pend.type === 'k' && R.view(S, 1).wait && !R.view(S, 0).can.set && !R.view(S, 1).can.set && set(S, 0, '2').why === 'set' && set(S, 1, '2').why === 'set' && R.legal(S, 0).join() === 'k' && R.legal(S, 1).length === 0,
    '決める までは 2人とも セットできない（ターンの スタートで えらぶ）');
  check(!R.act(S, 1, { t: 'k', pick: U(S, 0, '2') }).ok, '使えるのは 勝った 人 だけ');
  const t = U(S, 1, '3'); const r2 = R.act(S, 0, { t: 'k', pick: t });
  check(r2.ok && names(r2) === 'k' && r2.ev[0].k === '3' && R.view(S, 0).op.hand.find(c => c.u === t).k === '3' && R.view(S, 1).my.hand.find(c => c.u === t).seen && S.turn === 2 && S.phase === 'set' && !S.pend && R.view(S, 0).can.set && R.view(S, 1).can.set,
    '相手の 手札の 1まい（3）を 見た → 2ターン目の セットへ');
  const K = G('k2367', '12345'); set(K, 0, 'k'); set(K, 1, '1'); const rs = R.act(K, 0, { t: 'k', pick: null });
  check(rs.ok && names(rs) === 'kskip' && R.view(K, 0).op.hand.every(c => c.k === null) && K.phase === 'set', '使わなくても いい');
  const L = G('12k67', '23456'); set(L, 0, '1'); set(L, 1, '2'); set(L, 0, '2'); set(L, 1, '3'); set(L, 0, 'k'); const rl = set(L, 1, '6');
  check(names(rl) === 'set,open,clear,end' && L.phase === 'end' && !L.pend, '3ターン目に 勝った ときは 出ない（次の ターンが ない）');
  const M = G('k2367', 'm1234'); set(M, 0, '2'); const rm = set(M, 1, 'm');
  check(rm.ev[1].res === 1 && M.phase === 'pre' && M.pend.type === 'm' && M.pend.who === 1, '負けた 神様馬には 効果が ない（勝った 幻の馬の 効果が 次の ターンの はじめに 出る）');
  const e1 = R.evFor(r.ev, 1)[4], e0 = R.evFor(r.ev, 0)[4]; check(e0.e === 'pre' && e0.me === true && e0.type === 'k' && e1.me === false && e1.type === 'k', '知らせ：どちらが・どの 効果を えらぶか');
}

console.log('■ 幻の馬：使って 勝ったら、次の ターンの はじめに、手札を 2まい 捨てて 山札から 2まい まで 引く');
{
  const S = G('m6712', '12345', '13'); set(S, 0, 'm'); const r = set(S, 1, '1');
  check(names(r) === 'set,open,clear,turn,pre' && S.turn === 2 && S.phase === 'pre' && S.pend.type === 'm' && S.pend.who === 0, '幻の馬で 勝った → 2ターン目の はじめに、効果を 使うか 決める 番');
  const d = [U(S, 0, '6'), U(S, 0, '7')];
  check(R.act(S, 0, { t: 'm', drop: [d[0]] }).why === 'drop' && R.act(S, 0, { t: 'm', drop: [d[0], d[0]] }).why === 'drop' && R.act(S, 0, { t: 'm', drop: [d[0], 999] }).why === 'drop', '捨てるのは ちょうど 2まい（1まい・同じ カード 2回・手札に ない カードは だめ）');
  const r2 = R.act(S, 0, { t: 'm', drop: d });
  check(r2.ok && names(r2) === 'm' && r2.ev[0].drop.map(c => c.k).join('') === '67' && r2.ev[0].drew.map(c => c.k).join('') === '13' && ks(S.p[0].hand).split('').sort().join('') === '1123' && S.deck.length === 18 && S.phase === 'set' && sane(S),
    '6 と 7 を 捨てて、山札から 2まい（1・3）引いた（手札 4まい の まま）→ 2ターン目の セットへ');
  check(S.discard.map(c => c.k).join('') === 'm167', '捨て札：1ターン目に 出した 2まい → 効果で 捨てた 2まい の 順');
  const e1 = R.evFor(r2.ev, 1)[0]; check(e1.drop.map(c => c.k).join('') === '67' && e1.n === 2 && e1.drew === undefined, '相手には 捨てた カードと 引いた 数 だけ（引いた カードは 見せない）');
  const K = G('m6712', '12345'); set(K, 0, 'm'); set(K, 1, '1'); const rs = R.act(K, 0, { t: 'm', drop: null });
  check(rs.ok && rs.ev[0].e === 'mskip' && K.p[0].hand.length === 4 && K.deck.length === 20 && K.phase === 'set', '使わなくても いい');
}

console.log('■ 捨て札：終わった ターンの 捨て札・効果による 捨て札（まさちゃん 23:15）');
{
  // 1ターン目：あなた（0）が 5 の 効果（5 と 7 を 捨てる・山札から 幻の馬）・相手は 1 → 幻の馬の 勝ち → 2ターン目の はじめに 幻の馬の 効果（2 と 3 を 捨てる）
  const S = G('51237', '12346', 'm46'); set(S, 0, '5'); set(S, 1, '1'); eff(S, 0, { u5: U(S, 0, '7') });
  R.act(S, 0, { t: 'm', drop: [U(S, 0, '2'), U(S, 0, '3')] });
  set(S, 0, '1'); set(S, 1, '2');
  const d0 = R.view(S, 0).discard, d1 = R.view(S, 1).discard, f = d => d.map(x => x.k + ':' + x.why + x.turn + (x.mine ? 'm' : 'o')).join(' ');
  check(f(d0) === '5:51m 7:51m m:t1m 1:t1o 2:m2m 3:m2m 1:t2m 2:t2o', `捨て札は「何の カード・何で 捨てたか・どの ターン・だれの」を 覚える（${f(d0)}）`);
  check(f(d1) === '5:51o 7:51o m:t1o 1:t1m 2:m2o 3:m2o 1:t2o 2:t2m', '相手から 見ても 同じ 中身（「だれの」だけ 入れかわる）');
  const turnCards = d0.filter(x => x.why === 't'), effCards = d0.filter(x => x.why !== 't');
  check(turnCards.length === 4 && [1, 2].every(n => turnCards.filter(x => x.turn === n).length === 2 && turnCards.filter(x => x.turn === n && x.mine).length === 1) && effCards.map(x => x.k + x.why).join() === '55,75,2m,3m',
    '終わった ターンの 捨て札＝ターンごとに 2まい（自分 1まい・相手 1まい）／ 効果による 捨て札＝5 の 効果の 2まい と 幻の馬の 効果の 2まい');
  check(R.view(G('12367', '23456'), 0).discard.length === 0 && d0.every(x => Object.keys(x).sort().join() === 'k,mine,turn,why'), 'はじめは 0まい・渡すのは 4つの こと だけ（番号は 渡さない）');
}

console.log('■ 見せて いい こと だけを 渡す');
{
  const S = G('1236k', '567m7'); const v0 = R.view(S, 0);
  check(v0.op.hand.length === 5 && v0.op.hand.every(c => c.k === null && typeof c.u === 'number') && !/"k":"[1-7km]"/.test(JSON.stringify(v0.op)) && v0.my.hand.map(c => c.k).join('') === '1236k', '相手の 手札は 数 だけ（中身は ない）・自分の 手札は 見える');
  check(v0.deckN === 20 && !('deck' in v0) && JSON.stringify(v0).indexOf('"deck"') < 0, '山札は 数 だけ（並びは 渡さない）');
  set(S, 1, 'm');
  const w0 = R.view(S, 0);
  check(w0.op.set && w0.op.set.k === null && w0.op.set.up === false && w0.op.hand.length === 4 && w0.wait === false && R.view(S, 1).wait === true, '相手が ふせた カードは 見えない（セットした こと だけ わかる）');
  const r = set(S, 0, '1'); const e0 = R.evFor(r.ev, 0), e1 = R.evFor(r.ev, 1);
  check(e0[1].my.k === '1' && e0[1].op.k === 'm' && e0[1].res === 'lose' && e0[1].wins.join() === '0,1' && e1[1].my.k === 'm' && e1[1].op.k === '1' && e1[1].res === 'win' && e1[1].wins.join() === '1,0',
    'オープンは 2人とも 同じ カードを 見る（自分から 見た 勝ち負けに 直して 渡す）');
  const L = R.view(S, 0).last, L1 = R.view(S, 1).last; check(L.c.join('') === '1m' && L.res === 'lose' && L1.c.join('') === 'm1' && L1.res === 'win', '前の ターンの 結果も 自分から 見た 形');
  // 山札・相手の 手札の 中身が、見せる もの の どこにも 入って いない（番号 だけ）
  const T = G('1234k', '567m7'); const js = JSON.stringify(R.view(T, 0));
  check((js.match(/"k":"[1-7km]"/g) || []).length === 5, '渡す ものの 中に ある カードの 中身は 自分の 手札の 5まい だけ');
  // 効果タイム：相手が 何を 使えるか は 渡さない
  const E = G('66123', '77712'); set(E, 0, '1'); set(E, 1, '2');
  const x0 = R.view(E, 0), x1 = R.view(E, 1);
  check(JSON.stringify(x0.can.eff) === '{"e6":true,"e5":false,"e7":false,"e3":false,"e4":false}' && JSON.stringify(x1.can.eff) === '{"e6":false,"e5":false,"e7":true,"e3":false,"e4":false}' && !('eff' in x0.op) && !('eff' in x0.my), '効果タイム：自分が 使える 効果 だけ 渡す（相手が 何を 使えるかは 渡さない）');
}

console.log('■ まちがった 手は 受けつけない');
{
  const S = G('12367', '12367');
  check(R.act(S, 2, { t: 'set', u: 1 }).why === 'arg' && R.act(S, 0, null).why === 'arg' && R.act(S, 0, { t: 'zzz' }).why === 'type' && R.act(S, 0, { t: 'set', u: U(S, 1, '1') }).why === 'card'
    && R.act(S, 0, { t: 'swap', u: U(S, 0, '1') }).why === 'swap' && R.act(S, 0, { t: 'k', pick: null }).why === 'k' && R.act(S, 0, { t: 'm', drop: null }).why === 'm' && R.act(S, 0, { t: 'eff', use: { x7: true } }).why === 'eff',
    '知らない 手・相手の カード・番で ない 手は ぜんぶ 受けつけない（中身は かわらない）');
  check(ks(S.p[0].hand) === '12367' && ks(S.p[1].hand) === '12367' && S.deck.length === 20 && sane(S), '受けつけなかった あとも カードは そのまま');
}

// でたらめに えらぶ「使う 効果」：使えると 言われた もの（view.can.eff）の 中から。5 と 7（3）を いっしょに 使う ときは 7（3）を 3まい 残す
function rndUse(v, rng) {
  const c = v.can.eff, use = {}, h = v.my.hand, rc = a => a[Math.floor(rng() * a.length)];
  if (c.e6 && rng() < 0.7) use.p6 = rc(v.op.hand).u;
  if (c.e7 && rng() < 0.7) use.x7 = true;
  if (c.e3 && rng() < 0.7) use.x3 = true;
  if (c.e5 && rng() < 0.7) { const n7 = h.filter(x => x.k === '7').length, n3 = h.filter(x => x.k === '3').length, cand = h.filter(x => !(use.x7 && x.k === '7' && n7 <= 3) && !(use.x3 && x.k === '3' && n3 <= 3)); if (cand.length) use.u5 = rc(cand).u; }
  if (c.e4 && rng() < 0.7) use.u4 = true;
  return use;
}

console.log('■ でたらめに 2万回 あそぶ（どんな 手の 順でも こわれない）');
{
  const rng = rngOf(20261115); let bad = 0, n = 0, st = { efft: 0, x7: 0, p6: 0, u5: 0, x3: 0, both57: 0, both53: 0, u5t: [0, 0, 0, 0], x3t: [0, 0, 0, 0], first: 0, first2: 0, swap: 0, pre: 0, k: 0, m: 0, fizz: 0, clash: 0, tie: 0, win0: 0, win1: 0, draw: 0 };
  for (let g = 0; g < 20000; g++) {
    const S = R.newGame(rng); let guard = 0;
    while (S.phase !== 'end' && guard++ < 200) {
      const L0 = R.legal(S, 0), L1 = R.legal(S, 1);
      if (!L0.length && !L1.length) { bad++; break; }      // だれも 打てない ＝ 止まった
      const i = rng() < 0.5 ? 0 : 1, L = i === 0 ? L0 : L1; if (!L.length) continue;
      const t = L[Math.floor(rng() * L.length)], P = S.p[i], Q = S.p[1 - i]; let a;
      const rc = h => h[Math.floor(rng() * h.length)];
      if (t === 'set') a = { t: 'set', u: rc(P.hand).u };
      else if (t === 'eff') { a = { t: 'eff', use: rndUse(R.view(S, i), rng) }; if (a.use.x7 && a.use.u5 != null) st.both57++; if (a.use.x3 && a.use.u5 != null) st.both53++; }
      else if (t === 'swap') a = { t: 'swap', u: rc(P.hand).u };
      else if (t === 'k') a = { t: 'k', pick: rng() < 0.2 ? null : rc(Q.hand).u };
      else if (t === 'm') { const h = R.shuffle(P.hand.slice(), rng); a = { t: 'm', drop: rng() < 0.2 ? null : [h[0].u, h[1].u] }; }
      const before = S.p.map(X => X.set ? X.set.c.u : 0), ph = S.phase, tn = S.turn;
      const r = R.act(S, i, a, rng);
      if (!r.ok) { bad++; break; }
      r.ev.forEach(e => { if (typeof st[e.e] === 'number') st[e.e]++; if (e.e === 'u5') st.u5t[tn]++; if (e.e === 'x3') st.x3t[tn]++; if (e.e === 'open') { if (e.res === 'clash') st.clash++; if (e.res === 'tie') st.tie++; } });
      // 手札の 数：どの ターンの おわりにも、のこりの ターンで 出す 数 だけは ある（5 の 効果で 足りなく ならない）
      if (S.phase !== 'end' && S.p.some(X => X.hand.length + (X.set ? 1 : 0) < R.TURNS - S.turn + 1)) { bad++; break; }
      if (!sane(S)) { bad++; break; }
      // セットした カードが 変わるのは 5 の 効果・4 の 効果の 交換 だけ（セットの 番に 自分で 変える ことは ない）
      if (ph === 'set' && S.phase === 'set' && S.turn === tn && [0, 1].some(j => before[j] && (!S.p[j].set || S.p[j].set.c.u !== before[j]))) { bad++; break; }
      // 見せる ものに 相手の 知らない カードの 中身が 入って いない
      const v = R.view(S, 1 - i); if (v.op.hand.some(c => c.k !== null && S.p[1 - i].known.indexOf(c.u) < 0)) { bad++; break; }
      if ((S.phase === 'pre') !== (!!S.pend && (S.pend.type === 'k' || S.pend.type === 'm')) || (S.phase === 'swap') !== (!!S.pend && S.pend.type === 'swap')) { bad++; break; }
    }
    if (S.phase !== 'end' || S.turn !== 3 || S.p[0].wins + S.p[1].wins > 3 || S.discard.length < 6 || S.discard.filter(d => d.why === 't').length !== 6) bad++;
    st[S.res === 'draw' ? 'draw' : 'win' + S.res]++; n++;
  }
  check(bad === 0 && n === 20000, `2万回：ぜんぶ 3ターンで おわる・カードは いつも 30まい・打てる と 言った 手は ぜんぶ 通る・止まらない（おかしい ${bad}）`);
  check(st.efft > 5000 && st.x7 > 50 && st.p6 > 500 && st.u5 > 1000 && st.x3 > 50 && st.first > 500 && st.first2 > 20 && st.swap > 500 && st.pre > 2000 && st.k > 500 && st.m > 500 && st.clash > 2000 && st.tie > 3 && st.fizz === 0,
    `効果も ぜんぶ 出た（効果タイム ${st.efft}・7 ${st.x7}・6 ${st.p6}・5 ${st.u5}・3 ${st.x3}・5 と 7 を いっしょに ${st.both57}・5 と 3 を いっしょに ${st.both53}・4 ${st.first}・4 の 打ち消し ${st.first2}・交換 ${st.swap}・神様馬 ${st.k}・幻の馬 ${st.m}・かぶり ${st.clash}・引き分け ${st.tie}・不発 ${st.fizz}）`);
  check(st.u5t[1] > 300 && st.u5t[2] > 300 && st.u5t[3] > 300 && st.x3t[1] > 20 && st.x3t[2] > 5 && st.x3t[3] === 0,
    `5 の 効果は どの ターンでも 出た（1ターン目 ${st.u5t[1]}・2ターン目 ${st.u5t[2]}・3ターン目 ${st.u5t[3]}）・3 の 効果は 1・2ターン目（${st.x3t[1]}・${st.x3t[2]}：3ターン目は 手札が 2まい まで なので 出ない）`);
  check(Math.abs(st.win0 - st.win1) / n < 0.03, `どちらの 席も 同じ ぐらい 勝つ（${st.win0}・${st.win1}・同点 ${st.draw}）`);
}

console.log('■ コンピュータ（見えて いる こと だけで 決める）');
{
  // 自分に 見える こと（view）だけを 渡す。返した 手は かならず 通る
  const play = (seed, pol0, pol1, games) => {
    const rng = rngOf(seed); const out = { w0: 0, w1: 0, d: 0, bad: 0, t: {} };
    const tally = (i, a) => { const ks = a.t !== 'eff' ? [a.t] : ['eff'].concat(Object.keys(a.use || {}).filter(k => a.use[k] != null && a.use[k] !== false)); ks.forEach(k => { out.t[i + k] = (out.t[i + k] || 0) + 1; }); };
    for (let g = 0; g < games; g++) {
      const S = R.newGame(rng); let guard = 0;
      while (S.phase !== 'end' && guard++ < 100) {
        let moved = false;
        for (const i of (rng() < 0.5 ? [0, 1] : [1, 0])) {
          const a = (i === 0 ? pol0 : pol1)(R.view(S, i), rng); if (!a) continue;
          const r = R.act(S, i, a, rng); if (!r.ok) { out.bad++; guard = 999; break; }
          tally(i, a); moved = true;
        }
        if (!moved) { out.bad++; break; }
      }
      if (S.phase !== 'end') out.bad++;
      else if (S.res === 'draw') out.d++; else out['w' + S.res]++;
    }
    return out;
  };
  const cpu = (v, rng) => C.decide(v, rng);
  // でたらめに 出す 人（効果は 使わない・番が 来たら でたらめに）
  const rnd = (v, rng) => {
    const h = v.my.hand, rc = a => a[Math.floor(rng() * a.length)];
    if (v.pend && v.pend.mine) return v.pend.type === 'swap' ? { t: 'swap', u: rc(h).u } : v.pend.type === 'k' ? { t: 'k', pick: null } : { t: 'm', drop: null };
    if (v.can.eff) return { t: 'eff', use: null };
    return v.can.set ? { t: 'set', u: rc(h).u } : null;
  };
  // 強い 順に 出す 人
  const top = (v, rng) => {
    const h = v.my.hand.slice().sort((a, b) => R.power(a.k) - R.power(b.k));
    if (v.pend && v.pend.mine) return v.pend.type === 'swap' ? { t: 'swap', u: h[0].u } : v.pend.type === 'k' ? { t: 'k', pick: v.op.hand[0].u } : { t: 'm', drop: [h[h.length - 1].u, h[h.length - 2].u] };
    if (v.can.eff) return { t: 'eff', use: null };
    return v.can.set ? { t: 'set', u: h[0].u } : null;
  };
  const a = play(11, cpu, cpu, 4000), b = play(12, cpu, rnd, 4000), c = play(13, cpu, top, 4000);
  check(a.bad === 0 && b.bad === 0 && c.bad === 0, `コンピュータの 手は ぜんぶ 通る・かならず おわる（12,000回）`);
  check(Math.abs(a.w0 - a.w1) / 4000 < 0.04, `コンピュータ どうし：同じ ぐらい 勝つ（${a.w0}・${a.w1}・同点 ${a.d}）`);
  check(b.w0 / 4000 > 0.6 && b.w0 > b.w1 * 2.5, `でたらめに 出す 相手には よく 勝つ（${(b.w0 / 40).toFixed(1)}%・負け ${(b.w1 / 40).toFixed(1)}%・同点 ${(b.d / 40).toFixed(1)}%）`);
  check(c.w0 / 4000 > 0.3 && c.w0 / 4000 < 0.7, `強い 順に 出す 相手とは いい 勝負（勝ち ${(c.w0 / 40).toFixed(1)}%・負け ${(c.w1 / 40).toFixed(1)}%・同点 ${(c.d / 40).toFixed(1)}%）`);
  const used = Object.assign({}, a.t);
  check(['0x7', '0p6', '0u5', '0x3', '0u4', '0swap', '0k', '0m'].every(k => used[k] > 0), `コンピュータは 効果を ぜんぶ 使う（7 ${used['0x7']}・6 ${used['0p6']}・5 ${used['0u5']}・3 ${used['0x3']}・4 ${used['0u4']}・交換 ${used['0swap']}・神様馬 ${used['0k']}・幻の馬 ${used['0m']}：4,000回の 片方）`);
  // 決め方の 確かめ
  const mkv = (S, i) => R.view(S, i), kOf = (S, i, u) => (S.p[i].hand.find(c => c.u === u) || {}).k;
  const S1 = G('77712', '12345'); set(S1, 0, '1'); set(S1, 1, '2'); const a1 = C.decide(mkv(S1, 0), rngOf(1));
  check(a1.t === 'eff' && a1.use.x7 === true && a1.use.p6 == null && a1.use.u5 == null && !a1.use.u4, '効果タイム：7 が 3まい → 交換する');
  const S2 = G('66123', '12345'); set(S2, 0, '1'); set(S2, 1, '2'); const a2 = C.decide(mkv(S2, 0), rngOf(1));
  check(a2.t === 'eff' && S2.p[1].hand.some(c => c.u === a2.use.p6) && !a2.use.x7, '効果タイム：6 が 2まい → 相手の 手札を 1まい 見る');
  const S3 = G('12567', '12346'); const a3 = C.decide(mkv(S3, 0), rngOf(1));
  check(a3.t === 'set' && kOf(S3, 0, a3.u) === '5', 'セット：出す 3まい目が 5（弱い）→ 5 を セットする（5 の 効果を ねらう）');
  R.act(S3, 0, a3); set(S3, 1, '1'); const a3b = C.decide(mkv(S3, 0), rngOf(1));
  check(a3b.t === 'eff' && kOf(S3, 0, a3b.use.u5) === '7' && R.act(S3, 0, a3b).ok, '効果タイム：5 の 効果を 使って、1番 弱い 7 を 捨てる');
  // 第4.177版：5 の 効果は どの ターンでも ねらう（これから 出す 中で 1番 弱い のが 5 より 弱い か 同じ とき）・3 の 効果は ときどき 使う
  const T2 = G('15672', '12346'); set(T2, 0, '2'); set(T2, 1, '2'); const b2 = C.decide(mkv(T2, 0), rngOf(1));
  check(T2.turn === 2 && b2.t === 'set' && kOf(T2, 0, b2.u) === '5', '2ターン目：出す 2まいの 2番目が 5（1・5・6・7）→ 5 を セットする');
  R.act(T2, 0, b2); set(T2, 1, '1'); const b2e = C.decide(mkv(T2, 0), rngOf(1));
  check(T2.phase === 'eff' && b2e.t === 'eff' && kOf(T2, 0, b2e.use.u5) === '7' && R.act(T2, 0, b2e).ok && T2.p[0].hand.length === 2, '2ターン目の 効果タイム：5 の 効果を 使って 7 を 捨てる（手札 2まい → 3ターン目に 足りる）');
  const T3 = G('56712', '12346'); set(T3, 0, '1'); set(T3, 1, '1'); set(T3, 0, '2'); set(T3, 1, '2'); toDis(T3, 0, '6'); const b3 = C.decide(mkv(T3, 0), rngOf(1));
  check(T3.turn === 3 && ks(T3.p[0].hand) === '57' && b3.t === 'set' && kOf(T3, 0, b3.u) === '5', '3ターン目：手札が 5 と 7 → 5 を セットする（まさちゃんの 例の 形）');
  R.act(T3, 0, b3); set(T3, 1, '3'); const b3e = C.decide(mkv(T3, 0), rngOf(1));
  check(T3.phase === 'eff' && b3e.t === 'eff' && kOf(T3, 0, b3e.use.u5) === '7' && R.act(T3, 0, b3e).ok, '3ターン目の 効果タイム：5 と さいごの 手札（7）を 捨てて 山札から 出す');
  const T1 = G('12345', '12346'); set(T1, 0, '1'); set(T1, 1, '2'); const b1 = C.decide(mkv(T1, 0), rngOf(1));
  check(T1.turn === 2 && b1.t === 'set' && '23'.indexOf(kOf(T1, 0, b1.u)) >= 0, '強い カードが 足りて いる とき（2・3・4・5 の 2ターン目）は 5 を ねらわない');
  const X3 = G('33312', '4567k'); set(X3, 0, '1'); set(X3, 1, '7'); let u3 = 0; for (let sd = 1; sd <= 400; sd++) { const x = C.decide(mkv(X3, 0), rngOf(sd)); if (x.t === 'eff' && x.use.x3 === true) u3++; }
  check(X3.phase === 'eff' && u3 > 100 && u3 < 180, `3 が 3まい（1ターン目）：3回に 1回 ほど 使う（400回で ${u3}回）`);
  const X3b = G('33362', '4567k'); set(X3b, 0, '6'); set(X3b, 1, '7'); eff(X3b, 0, null); set(X3b, 0, '2'); set(X3b, 1, '6'); let u3b = 0; for (let sd = 1; sd <= 400; sd++) { const x = C.decide(mkv(X3b, 0), rngOf(sd)); if (x.t === 'eff' && x.use.x3 === true) u3b++; }
  check(X3b.turn === 2 && X3b.phase === 'eff' && u3b > 180 && u3b < 260, `3 が 3まい（2ターン目）：半分 ほど 使う（400回で ${u3b}回）`);
  const X35 = G('53331', '12467'); set(X35, 0, '5'); set(X35, 1, '1'); let ok35 = true, n35 = 0;
  for (let sd = 1; sd <= 300; sd++) { const x = C.decide(mkv(X35, 0), rngOf(sd)); if (x.use.x3) { n35++; if (x.use.u5 != null) ok35 = false; } else if (kOf(X35, 0, x.use.u5) !== '3') ok35 = false; const Z = JSON.parse(JSON.stringify(X35)); if (!R.act(Z, 0, x, rngOf(sd)).ok) ok35 = false; }
  check(ok35 && n35 > 60, `5 と 3 の 両方：3 の 交換を する ときは、3 も 強い 1 も 捨てない（5 の 効果は 使わない）・しない ときは 3 を 1まい 捨てて 5 の 効果（${n35}／300回 で 交換）`);
  const S4 = G('12354', '12346'); const seen = new Set(); for (let s = 1; s <= 200; s++) { const x = C.decide(mkv(S4, 0), rngOf(s)); seen.add(x.t + kOf(S4, 0, x.u)); }
  check([...seen].sort().join() === 'set1,set2,set3', `1ターン目は 強い 方から 3まいの どれか（毎回 同じ では ない：${[...seen].sort().join('・')}）・強い ときは 5 を ねらわない`);
  const S57 = G('57771', '12346'); set(S57, 0, '5'); set(S57, 1, '1'); const a57 = C.decide(mkv(S57, 0), rngOf(1));
  check(a57.t === 'eff' && a57.use.x7 === true && a57.use.u5 == null && R.act(S57, 0, a57).ok, '5 と 7 の 両方：7 の 交換を する・のこりが 強い カード（1）なら 5 の 効果は 使わない');
  const S56 = G('57776', '12346'); set(S56, 0, '5'); set(S56, 1, '1'); const a56 = C.decide(mkv(S56, 0), rngOf(1));
  check(a56.use.x7 === true && kOf(S56, 0, a56.use.u5) === '6' && R.act(S56, 0, a56).ok, '5 と 7 の 両方：のこりが 弱い カード（6）なら それを 捨てて、両方 使う');
  const S5 = G('41236', '15677'); set(S5, 0, '4'); set(S5, 1, '1'); eff(S5, 0, { u4: true });
  const a5 = C.decide(mkv(S5, 1), rngOf(1)); check(a5.t === 'swap' && kOf(S5, 1, a5.u) === '7', '交換：4 に 勝てる カードも 4 も ない → 1番 弱い 7 を 出す（強い カードを 残す）');
  const S6 = G('41236', '71234'); set(S6, 0, '4'); set(S6, 1, '7'); eff(S6, 0, { u4: true });
  const a6 = C.decide(mkv(S6, 1), rngOf(1)); check(a6.t === 'swap' && kOf(S6, 1, a6.u) === '3', '交換：4 に 勝てる カードの 中で 1番 弱い 3 を 出す（1・2 は 残す）');
  const S7 = G('41236', '74567'); set(S7, 0, '4'); set(S7, 1, '7'); eff(S7, 0, { u4: true });
  const a7 = C.decide(mkv(S7, 1), rngOf(1)); check(a7.t === 'swap' && kOf(S7, 1, a7.u) === '4', '交換：勝てる カードが なくて 4 が ある → 4 を 出す（かぶって どちらも 負け＝相手に 勝たせない）');
  const S8 = G('k2367', '12345'); set(S8, 0, 'k'); set(S8, 1, '1');
  const a8 = C.decide(mkv(S8, 0), rngOf(1)); check(S8.phase === 'pre' && a8.t === 'k' && S8.p[1].hand.some(c => c.u === a8.pick) && C.decide(mkv(S8, 1), rngOf(1)) === null, '神様馬で 勝った 次の ターンの はじめ → 相手の 手札を 見る（負けた 方は 待つ）');
  const S9 = G('m6712', '12345'); set(S9, 0, 'm'); set(S9, 1, '1');
  const a9 = C.decide(mkv(S9, 0), rngOf(1)); check(a9.t === 'm' && a9.drop.map(u => kOf(S9, 0, u)).sort().join('') === '67', '幻の馬で 勝った 次の ターンの はじめ → 弱い 方から 2まい（6・7）を 捨てて 引く');
  const S11 = G('42377', '11256'); set(S11, 0, '2'); set(S11, 1, '1'); set(S11, 0, '3'); set(S11, 1, '1'); set(S11, 0, '4'); set(S11, 1, '2');     // 3ターン目：4 を セット
  let f3 = 0; for (let s = 1; s <= 100; s++) { const x = C.decide(mkv(S11, 0), rngOf(s)); if (x.t === 'eff' && x.use.u4 === true) f3++; }
  check(S11.turn === 3 && S11.phase === 'eff' && f3 === 100, '3ターン目に 4 を セットした ときは 4 の 効果を 使う');
  const S12 = G('41236', '12357'); set(S12, 0, '4'); set(S12, 1, '1'); let f1 = 0; for (let s = 1; s <= 300; s++) { const x = C.decide(mkv(S12, 0), rngOf(s)); if (x.t !== 'eff' || x.use.u4) f1++; }
  check(S12.phase === 'eff' && f1 === 0, '1ターン目は 4 の 効果を 使わない（「使わない」と 決める）');
  const S10 = G('12367', '23456'); set(S10, 0, '1');
  check(C.decide(R.view(S10, 0), rngOf(1)) === null && C.decide(R.view(S10, 1), rngOf(1)).t === 'set' && C.decide(Object.assign(R.view(S10, 1), { phase: 'end' }), rngOf(1)) === null && C.decide(null) === null, 'セットした あと（相手を 待つ あいだ）は 何も しない・打つ ものが ない ときは null');
  const S13 = G('66123', '77712'); set(S13, 0, '1'); set(S13, 1, '2'); R.act(S13, 0, C.decide(R.view(S13, 0), rngOf(1)));
  check(S13.phase === 'eff' && C.decide(R.view(S13, 0), rngOf(1)) === null && C.decide(R.view(S13, 1), rngOf(1)).t === 'eff', '効果タイムで 決めた あとは 何も しない（相手が 決める のを 待つ）');
}
console.log('結果：', fails.length ? fails.length + '件おかしい' : 'OK');
process.exit(fails.length ? 1 : 0);
