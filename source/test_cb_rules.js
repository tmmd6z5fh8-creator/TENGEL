// 馬カードバトルの ルール（cb/cb_rules.js）と コンピュータ（cb/cb_cpu.js）の テスト：node test_cb_rules.js
//   まさちゃんの ルール（2026/11/15 21:41）：3ターン・手札 5まい・30まい（1〜7 が 4まい ずつ＋神様馬＋幻の馬）・強さ・かぶりは 負け・勝った 枚数・効果 6つ
//   まさちゃんの 直し（23:12）：セットしたら 変えられない・2人とも セットしたら 効果を 使うか えらぶ（効果タイム）・神様馬／幻の馬の 効果は 勝った 次の ターンの はじめ
//   まさちゃんの 直し（23:15）：捨て札を 確認できる（終わった ターンの 捨て札・効果による 捨て札）
//   まさちゃんの 直し（第4.177版・2026/11/16 10:40）：5 は「使った あとの 手札が のこりの ターンの 数より 少なく ならない」とき 使える（3ターン目に 5 と もう 1まい でも 使える）・
//     3 に 効果（手札に 3 が 3まい → 3まいを 見せて、その 1まいと 相手の 手札の くじで えらんだ 1まいを 交換）・どの 効果も 使うか えらべる
//   まさちゃんの 直し（第4.178版・2026/11/16 14:43）：5ターン勝負・手札 7まい ／ 6 の 効果は、相手の 手札が もう 見た カード しか ない ときは 発動しない
//   まさちゃんの 追加（第4.178版・2026/11/16 15:33・15:41「A、オープンしてから」）：逆転勝利 ＝ 1 が 3まい（場 ＋ 手札 2）→ 神様馬・幻の馬に 勝てる ／ 2 が 3まい → 1 に 勝てる（手札の 1まいを 捨てる）
//   まさちゃんの 直し（第4.181版・2026/11/16 19:05「4をお互いに出して効果を発動した場合、ドローになる」）：2人とも 4 の 効果 → 打ち消して ドロー（前は かぶり＝どちらも 負け）
//   まさちゃんの 直し（第4.183版・2026/11/16 21:24「4で交換したあとに5を相手がフィールドにセットした場合、五の効果を使える」）：交換で 5 → 5 の 効果を 使うか 聞く（phase u5）
//   まさちゃんの 直し（第4.185版・2026/11/16 22:39「7は、手札に7が4枚ある場合、4枚公開し内1枚を捨てると、数字の強さ順が逆転する」・22:45「その試合は終わるまで」）：7 の 4まい 公開で 強さ 逆転（S.rv）
//   まさちゃんの 直し（第4.190版・2026/11/17 17:14「効果はそれぞれの一つ一つ終わってから効果の選択するようにして！…6は、カードをセットする前に相手のカード見れる！」）：
//     6 は ターンの はじめ（セットの 前・神様馬／幻の馬より 先：手 p6）・効果タイムは 1つずつ（7 → 3 → 5 → 4：決めたら すぐ 行う → 次の 効果）
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
// 手札と 山札の 上を 決めて はじめる（テスト用）。turns＝ターンの 数：決めなければ 3（第4.176版・第4.177版で 書いた 場面は「3ターン・手札 5まい」の まま 動かす：効果の しくみは ターンの 数に よらない）。
//   本番の 形（5ターン・手札 7まい：第4.178版）は 下の「■ 5ターン・手札 7まい」で 見る
const G = (h0, h1, deck, turns) => R.newGame(rngOf(7), { hands: [h0.split(''), h1.split('')], deck: deck ? deck.split('') : undefined, turns: turns || 3 });
const set = (S, i, k) => R.act(S, i, { t: 'set', u: U(S, i, k) }, rngOf(3));
const eff = (S, i, use, rng) => R.act(S, i, { t: 'eff', use: use || null }, rng || rngOf(3));      // 効果タイム：いまの 効果を 使うか 決める（null＝使わない。第4.190版：1つずつ）
const p6 = (S, i, pick) => R.act(S, i, { t: 'p6', pick: pick == null ? null : pick }, rngOf(3));      // 第4.190版：6 の 効果（ターンの はじめ）：pick＝見る カード・null＝使わない
const no6 = S => { if (S.phase === 'six') [0, 1].forEach(i => { if (S.p[i].six && !S.p[i].six.done) p6(S, i, null); }); return S; };      // 6 の 効果を 2人とも 使わない（6 の テストで ない 場面）
const names = r => r.ev.map(e => e.e).join();
// テスト用：プレイヤー i の 手札の k を 1まい 捨て札へ（手札の 数を へらした 形を 作る）／山札の 中の k を 1まい 手札へ
const toDis = (S, i, k) => { const P = S.p[i], j = P.hand.findIndex(c => c.k === k), c = P.hand.splice(j, 1)[0]; S.discard.push({ u: c.u, k: c.k, by: i, why: 't', turn: S.turn }); };
const fromDeck = (S, i, k) => { const j = S.deck.findIndex(c => c.k === k); S.p[i].hand.push(S.deck.splice(j, 1)[0]); };

console.log('■ カードと 配り方');
{
  const S = R.newGame(rngOf(1));
  const a = all(S), n = {}; a.forEach(c => { n[c.k] = (n[c.k] || 0) + 1; });
  check(a.length === 30 && R.NUMS.every(k => n[k] === 4) && n.k === 1 && n.m === 1 && R.KINDS.join('') === '1234567km', 'カードは 30まい：1〜7 が 4まい ずつ・神様馬 1まい・幻の馬 1まい');
  check(S.p[0].hand.length === 7 && S.p[1].hand.length === 7 && S.deck.length === 16 && S.discard.length === 0 && S.turn === 1 && S.turns === 5 && S.phase === 'set' && R.TURNS === 5 && R.HAND === 7 && R.view(S, 0).turns === 5,
    '手札は 7まい ずつ・山札 16まい・5ターン（第4.178版：まさちゃん「５ターン勝負にする 手札7枚にして！」）');
  const seen = new Set(); for (let s = 1; s <= 200; s++) seen.add(ks(R.newGame(rngOf(s)).p[0].hand)); check(seen.size > 190, `配る たびに 手札が かわる（200回で ${seen.size}通り）`);
  let km = 0, n1 = 0; for (let s = 1; s <= 3000; s++) { const h = R.newGame(rngOf(s + 999)).p[0].hand; if (h.some(c => c.k === 'k')) km++; n1 += h.filter(c => c.k === '1').length; }
  check(Math.abs(km / 3000 - 7 / 30) < 0.03 && Math.abs(n1 / 3000 - 7 * 4 / 30) < 0.06, `かたよらない：神様馬が 手札に 来る 割合 ${(km / 30).toFixed(1)}%（7/30＝23.3%）・1 の 平均 ${(n1 / 3000).toFixed(2)}まい（0.93）`);
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
  // 第4.185版：強さ 逆転ちゅう（rv）：数字 だけ 逆（7＞6＞…＞1）・神様馬 と 幻の馬は いちばん 強い まま
  let ok2 = true;
  for (const a of R.KINDS) for (const b of R.KINDS) {
    const r = c(a, b, true), na = R.NUMS.indexOf(a) >= 0, nb = R.NUMS.indexOf(b) >= 0;
    const want = a === b ? 'clash' : !na && !nb ? 'tie' : !na ? 0 : !nb ? 1 : +a > +b ? 0 : 1;
    if (r !== want) ok2 = false;
  }
  check(ok2 && P('7', true) === 1 && P('1', true) === 7 && P('k', true) === 0 && c('7', '1', true) === 0 && c('1', '2', true) === 1 && c('k', '7', true) === 0 && c('7', 'm', true) === 1 && c('6', '6', true) === 'clash',
    '第4.185版：強さ 逆転ちゅう（81通り）：数字は 7 が 1番 強くて 1 が 1番 弱い・神様馬 と 幻の馬は いちばん 強い まま・かぶり・引き分けは 同じ');
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
  const E = G('77712', '12345', '346'); const e1 = U(E, 0, '1'); set(E, 0, '1'); set(E, 1, '2');
  check(E.phase === 'eff' && R.act(E, 0, { t: 'set', u: U(E, 0, '2') }).why === 'set' && R.act(E, 1, { t: 'set', u: U(E, 1, '1') }).why === 'set' && E.p[0].set.c.u === e1, '効果タイムの あいだも セットし直せない');
}

console.log('■ 効果タイム：2人とも セットが 終わったら、効果を 使うか えらぶ（まさちゃん 23:12）・第4.190版：1つずつ（7 → 3 → 5 → 4）');
{
  const S = G('77712', '12345', '346');
  check(R.act(S, 0, { t: 'x7' }).why === 'type' && R.act(S, 0, { t: 'set5', u: 1, drop: 2 }).why === 'type' && R.act(S, 0, { t: 'eff', use: { x7: true } }).why === 'eff'
    && R.view(S, 0).can.eff === null && S.phase === 'set', 'セットの 前は 効果を 使えない（効果を えらぶのは 2人とも セットした あと だけ）');
  const r0 = set(S, 0, '1');
  check(names(r0) === 'set' && S.phase === 'set' && R.view(S, 0).can.eff === null && R.act(S, 0, { t: 'eff', use: null }).why === 'eff', '自分だけ セットした：まだ 効果は えらべない（相手の セットを 待つ）');
  const r1 = set(S, 1, '2');
  check(names(r1) === 'set,efft' && S.phase === 'eff' && S.step === 'x7' && r1.ev[1].has.join() === 'true,false' && r1.ev[1].st === 'x7' && r1.ev[1].first === true, '2人とも セットした → 効果タイム（オープンは まだ）：いまの 効果は 7（3まい 交換）');
  const v0 = R.view(S, 0), v1 = R.view(S, 1);
  check(v0.can.eff && v0.can.eff.e7 === true && v0.can.eff.st === 'x7' && v0.can.eff.n === 1 && !v0.can.eff.e6 && !v0.can.eff.e3 && !v0.can.eff.e5 && !v0.can.eff.e4 && v0.wait === false && R.legal(S, 0).join() === 'eff',
    '使える 人：いまの 効果（7）を 使うか えらぶ 番（聞くのは 1つ だけ）');
  check(v1.can.eff === null && v1.wait === true && R.legal(S, 1).length === 0 && R.act(S, 1, { t: 'eff', use: null }).why === 'eff', '使える 効果が ない 人：えらぶ ものは ない（相手を 待つ）');
  const e = [R.evFor(r1.ev, 0)[1], R.evFor(r1.ev, 1)[1]];
  check(e[0].mine === true && e[0].st === 'x7' && e[0].first === true && e[0].other === false && e[1].mine === false && !('st' in e[1]) && e[1].first === true && e[1].other === true,
    '効果タイムの 知らせ：自分に えらぶ ものが あるか・どの 効果か（第4.190版：聞かれる 人 だけ。相手が セットした カードが わからない ように）・はじめ だけ 相手が えらんで いるか');
  check(eff(S, 0, { u5: U(S, 0, '2') }).why === 'e5' && eff(S, 0, { x3: true }).why === 'e3' && eff(S, 0, { u4: true }).why === 'e4' && eff(S, 0, { x7: true, u4: true }).why === 'e4' && eff(S, 0, { p6: U(S, 1, '3') }).why === 'e6' && !S.p[0].eff.done,
    '第4.190版：いまの 効果 では ない 効果・2つ いっしょに 送る 手・6 は 受けつけない（1つずつ）');
  const r2 = eff(S, 0, null);
  check(r2.ok && names(r2) === 'effd,open,clear,turn' && r2.ev[1].res === 0 && S.turn === 2 && ks(S.p[0].hand) === '7772' && S.step === null, '「使わない」→ 次に 使える 効果が なければ そのまま オープン（1 と 2 → 1 の 勝ち）');
  // 1つずつ（第4.190版・まさちゃん 17:14）：決めたら すぐ 行う → 行った あとの 手札と 場で 次の 効果を 聞く
  const B = G('57771', '33312', '2346'); set(B, 0, '5'); set(B, 1, '2');      // 席 0：7（3まい）と 5 を セット ／ 席 1：3（3まい）
  check(B.phase === 'eff' && B.step === 'x7' && R.view(B, 0).can.eff.e7 && R.view(B, 1).can.eff === null && R.view(B, 1).wait, '7 → 3 → 5：はじめは 7（席 0）・席 1（3 が 3まい）は まだ 聞かれない（待つ）');
  const rb0 = eff(B, 0, { x7: true }, rngOf(5));
  check(rb0.ok && names(rb0) === 'effd,x7,efft' && rb0.ev[1].drew.map(c => c.k).join('') === '234' && rb0.ev[2].st === 'x3' && rb0.ev[2].first === false && rb0.ev[2].has.join() === 'false,true' && B.step === 'x3'
    && R.view(B, 1).can.eff.e3 && R.view(B, 1).can.eff.n === 2 && R.view(B, 0).can.eff === null && R.view(B, 0).wait,
    '7 を 決めたら すぐ 行う（3まい 交換）→ 次の 効果（3：席 1）を 聞く');
  const rb1 = eff(B, 1, { x3: true }, rngOf(9)), g3 = rb1.ev[1];
  check(rb1.ok && names(rb1) === 'effd,x3,efft' && rb1.ev[2].st === 'u5' && R.view(B, 0).can.eff.e5 && R.view(B, 0).my.hand.some(c => c.u === g3.give.u) && B.p[1].hand.some(c => c.u === g3.take.u) && '1234'.indexOf(g3.take.k) >= 0,
    '3 を 行う（7 で 引いた あとの 手札から くじ）→ 次の 効果（5：席 0）：もらった 3 も 手札に ある');
  const rb2 = eff(B, 0, { u5: g3.give.u });
  check(rb2.ok && names(rb2).startsWith('effd,u5,open,clear,turn') && rb2.ev[1].drop.u === g3.give.u && rb2.ev[1].drop.k === '3' && sane(B), '5 で 捨てる カードは 前の 効果の あとの 手札から（3 の 効果で もらった 3 を 捨てた）');
  // 同じ 効果を 2人とも 使える（5 と 5）：その 効果 だけ 2人とも 決めて から いっしょに 行う
  const D = G('51234', '52367', '67'); set(D, 0, '5'); set(D, 1, '5');
  check(D.step === 'u5' && R.view(D, 0).can.eff.e5 && R.view(D, 1).can.eff.e5 && !R.view(D, 0).wait && !R.view(D, 1).wait, '2人とも 5 を セット：2人とも 5 の 効果を えらぶ');
  const rd0 = eff(D, 0, { u5: U(D, 0, '4') });
  check(rd0.ok && names(rd0) === 'effd' && D.phase === 'eff' && R.view(D, 0).wait === true && R.view(D, 0).can.eff === null && R.act(D, 0, { t: 'eff', use: null }).why === 'eff' && D.p[0].set.c.k === '5',
    '1人が 決めた：効果は まだ 出ない（相手が 決める まで 待つ・決め直せない）');
  const eo = R.evFor(rd0.ev, 1)[0], vo = JSON.stringify(R.view(D, 1));
  check(JSON.stringify(eo) === '{"e":"effd","me":false}' && vo.indexOf('"drop"') < 0 && vo.indexOf('"use"') < 0, '相手には「決めた」こと だけ 伝わる（何を 使うかは わからない）');
  const rd1 = eff(D, 1, { u5: U(D, 1, '7') });
  check(rd1.ok && names(rd1) === 'effd,u5,u5,open,clear,turn' && rd1.ev[1].who === 0 && rd1.ev[1].drop.k === '4' && rd1.ev[2].who === 1 && rd1.ev[2].drop.k === '7' && sane(D), '2人とも 決めた → いっしょに 行って（席 0 → 1）から オープン');
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
  const W = G('33312', '4567k'); set(W, 0, '1'); set(W, 1, '7'); check(W.step === 'x3' && eff(W, 0, { x7: true }).why === 'e7' && W.phase === 'eff', '7 が 3まい ない 人が「7 の 効果」と 言っても 受けつけない');
  const T2 = G('17772', '12345'); set(T2, 0, '2'); set(T2, 1, '1'); eff(T2, 0, null); set(T2, 0, '1'); set(T2, 1, '2');
  check(T2.turn === 2 && T2.phase === 'eff' && R.view(T2, 0).can.eff.e7 === true && eff(T2, 0, { x7: true }).ok && T2.p[0].hand.length === 3 && sane(T2), '2ターン目（セットした あとの 手札が 7・7・7）でも 使える');
  let re = 0; for (let s = 1; s <= 400; s++) { const X = G('77712', '12345'); set(X, 0, '1'); set(X, 1, '2'); const before = new Set(X.p[0].hand.filter(c => c.k === '7').map(c => c.u)); eff(X, 0, { x7: true }, rngOf(s)); if (X.p[0].hand.some(c => before.has(c.u)) || X.p[0].hand.length !== 4) re++; }
  check(re === 0, 'もどした 7 を すぐ 引き直さない（先に 3まい 引いて から もどす：400回）');
}

console.log('■ 6：手札の 6 を 2まい 見せると、相手の 手札を 1まい 見られる（第4.190版・まさちゃん 17:14「6は、カードをセットする前に相手のカード見れる！」＝ターンの はじめ）');
{
  const S = G('66123', '12345');
  check(S.phase === 'six' && R.view(S, 0).can.six && R.view(S, 0).can.six.n === 1 && R.view(S, 1).can.six === null && R.view(S, 1).wait === true && !R.view(S, 0).can.set && !R.view(S, 1).can.set
    && R.legal(S, 0).join() === 'p6' && R.legal(S, 1).length === 0 && S.ev0.map(e => e.e).join() === 'sixt' && S.ev0[0].has.join() === 'true,false',
    'ターンの はじめ（セットの 前）：6 が 2まい ある 人が 6 の 効果を 使うか えらぶ（相手は 待つ・2人とも まだ セットできない）');
  const ex = [R.evFor(S.ev0, 0)[0], R.evFor(S.ev0, 1)[0]];
  check(ex[0].e === 'sixt' && ex[0].mine === true && ex[0].other === false && ex[1].mine === false && ex[1].other === true, '知らせ（sixt）：自分が 聞かれて いるか・相手が えらんで いるか');
  check(set(S, 0, '1').why === 'set' && set(S, 1, '1').why === 'set' && R.act(S, 1, { t: 'p6', pick: U(S, 0, '1') }).why === 'p6' && eff(S, 0, null).why === 'eff' && R.act(S, 0, { t: 'x7r' }).why === 'x7r',
    '決める まで セットできない・6 が ない 人は 使えない・効果タイムの 手も 受けつけない');
  const tgt = U(S, 1, '4'), six = S.p[0].hand.filter(c => c.k === '6').map(c => c.u);
  check(R.view(S, 0).op.hand.every(c => c.k === null) && R.view(S, 0).op.hand.map(c => c.u).join() === S.p[1].hand.map(c => c.u).join(), '見る 前：相手の 手札は ぜんぶ 見えない（だれも セットして いない ので 見える 形は ほんとうの 手札 5まい）');
  check(p6(S, 0, 9999).why === 'pick' && p6(S, 0, U(S, 0, '2')).why === 'pick' && S.phase === 'six' && !S.p[0].six.done, '相手の 手札に ない カードは 見られない');
  const r = p6(S, 0, tgt);
  check(r.ok && names(r) === 'sixd,p6' && r.ev[1].k === '4' && r.ev[1].pick === tgt && r.ev[1].six.join() === six.join() && S.phase === 'set' && R.view(S, 0).can.set && R.view(S, 1).can.set && !S.p[0].six,
    '相手の 手札の 1まい（4）を 見た → セットへ（見てから セットする カードを えらべる）');
  const v0 = R.view(S, 0), v1 = R.view(S, 1);
  check(v0.op.hand.filter(c => c.k !== null).map(c => c.u + c.k).join() === tgt + '4' && v0.op.hand.filter(c => c.k === null).length === 4, '見た カード だけ 見える ままに なる（ほかの 4まいは 見えない）');
  check(v1.op.hand.filter(c => c.k === '6').map(c => c.u).join() === six.join() && v1.op.hand.filter(c => c.k === null).length === 3 && v1.my.hand.find(c => c.u === tgt).seen === true && v1.my.hand.filter(c => c.seen).length === 1,
    '相手には 見せた 6 の 2まいが 見える・見られた カードに しるし');
  const e1 = R.evFor(r.ev, 1)[1]; check(e1.me === false && e1.k === undefined && e1.pick === tgt && R.evFor(r.ev, 0)[1].k === '4', '見られた 人には「どの カードを 見られたか」だけ（中身は 自分の カード なので 書かない）');
  check(ks(S.p[0].hand) === '66123', '6 は 手札に のこる');
  const O = G('61234', '12367'); check(O.phase === 'set' && O.ev0.length === 0 && R.view(O, 0).can.six === null, '6 が 1まい では 使えない（ターンの はじめに 聞かれない）');
  const Q = G('66123', '12345'); p6(Q, 0, null); set(Q, 0, '6'); const rq = set(Q, 1, '2');
  check(names(rq) === 'set,open,clear,turn' && Q.phase === 'set' && Q.turn === 2, '6 を セットして 手札の 6 が 1まいに なったら、次の ターンは 聞かれない（効果タイムにも 6 は 出ない）');
  // 見た カードが 場に 出ても、場の カードは うら（第4.187版：セットは ふせて 出す・どの カードを 出したかは 手札の 見え方でも わからない）
  R.act(S, 1, { t: 'set', u: tgt });
  const w0 = R.view(S, 0);
  check(w0.op.set.k === null && w0.op.hand.length === 4 && w0.op.hand.filter(c => c.k).map(c => c.u + c.k).join() === tgt + '4' && w0.op.hand.filter(c => c.k === null).every(c => S.p[1].hand.some(h => h.u === c.u)),
    '第4.187版：見た カードを 相手が セットした → 場の カードは うら・見た 4 は 手札に ある ように 見える（うらの カードは いま 手札に ある カード）');
  set(S, 0, '1');
  check(S.phase === 'eff' && S.step === 'u4' && R.view(S, 1).can.eff.e4 === true && R.view(S, 0).can.eff === null, '（相手は 4 を セット：効果タイムは 4 だけ・6 は 出ない）');
  eff(S, 1, null);
  check(S.turn === 2 && S.phase === 'six' && R.view(S, 0).can.six && R.view(S, 0).can.six.n === 2, '次の ターンも（6 が 2まい あれば）また ターンの はじめに 使える');
  // 2人とも 6 が 2まい：2人とも 決めて から いっしょに 行う（相手が 何を 見るか 見て から 決める ことは できない）
  const D = G('66123', '66345');
  check(D.phase === 'six' && R.view(D, 0).can.six && R.view(D, 1).can.six && D.ev0[0].has.join() === 'true,true', '2人とも 6 が 2まい：2人とも 聞かれる');
  const rd0 = p6(D, 0, U(D, 1, '4'));
  check(rd0.ok && names(rd0) === 'sixd' && D.phase === 'six' && R.view(D, 0).wait === true && R.view(D, 0).can.six === null && p6(D, 0, null).why === 'p6' && R.view(D, 0).op.hand.every(c => c.k === null)
    && JSON.stringify(R.evFor(rd0.ev, 1)[0]) === '{"e":"sixd","me":false}' && JSON.stringify(R.view(D, 1)).indexOf('pick') < 0,
    '1人が 決めた：まだ 行わない（相手が 決める まで 待つ・決め直せない・相手には「決めた」こと だけ）');
  const rd1 = p6(D, 1, U(D, 0, '6'));
  check(rd1.ok && names(rd1) === 'sixd,p6,p6' && rd1.ev[1].who === 0 && rd1.ev[1].k === '4' && rd1.ev[2].who === 1 && rd1.ev[2].k === '6' && rd1.ev.every(e => e.e !== 'fizz') && D.phase === 'set',
    '2人とも 決めた → いっしょに 行う（席 0 → 1・相手の 6 を えらんでも 不発に ならない）→ セットへ');
  const D2 = G('66123', '66345'); p6(D2, 1, null); const rd2 = p6(D2, 0, null);
  check(names(rd2) === 'sixd,p6skip,p6skip' && D2.phase === 'set' && R.evFor(rd2.ev, 0)[2].me === false, '2人とも 使わない → 使わなかった ことを 知らせて（p6skip）セットへ');
  // 神様馬・幻の馬より 先（まさちゃん 17:14「神様馬カードと幻の馬カードの効果に優先順位が高いのは6の効果だよ！」）
  const K = G('k6612', '12345'); p6(K, 0, null); set(K, 0, 'k'); const rk = set(K, 1, '1');
  check(names(rk) === 'set,open,clear,turn,sixt' && K.turn === 2 && K.phase === 'six' && K.win && K.win.type === 'k' && !K.pend && R.view(K, 0).can.six && !R.view(K, 0).pend,
    '神様馬で 勝った 次の ターン：まず 6 の 効果（神様馬の 効果は その あと）');
  const rk2 = p6(K, 0, U(K, 1, '3'));
  check(rk2.ok && names(rk2) === 'sixd,p6,pre' && K.phase === 'pre' && K.pend.type === 'k' && K.pend.who === 0, '6 を 決めて 行ったら、神様馬の 効果を 聞く');
  check(R.act(K, 0, { t: 'k', pick: U(K, 1, '3') }).why === 'pick' && R.act(K, 0, { t: 'k', pick: U(K, 1, '4') }).ok && K.phase === 'set', '神様馬の 効果では、6 で 見た カード（3）は えらべない（まだ 見て いない 4 を 見る）→ セットへ');
  const M = G('m6612', '12345', '34'); p6(M, 0, null); set(M, 0, 'm'); set(M, 1, '1');
  check(M.phase === 'six' && M.win.type === 'm', '幻の馬で 勝った 次の ターンも、まず 6 の 効果');
  const rm = p6(M, 0, null);
  check(names(rm) === 'sixd,p6skip,pre' && M.phase === 'pre' && M.pend.type === 'm', '6 を 使わなくても、その あと 幻の馬の 効果を 聞く');
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
  // 山札から 来た カードは オープンまで だれにも 見えない：できごと u5 には 山札から 来た カードは 入らない（オープンで はじめて 出る）
  const e2 = R.evFor(r.ev, 0)[1], e3 = R.evFor(r.ev, 1)[1];
  check(!/"k":"k"/.test(JSON.stringify(e2)) && !/"k":"k"/.test(JSON.stringify(e3)) && Object.keys(e2).sort().join() === 'drop,e,five,me', '山札から 来た カードは オープンまで だれにも 見えない（できごと u5 に 入らない：自分にも）');
  // 第4.188版（まさちゃん 11:16「4は効果発動最後にして！」）：5 → 4 の 順（4 は いちばん あと）。山札から ふせた カードも、相手の 4 の 効果で 交換に なる
  const Z = G('51237', '41236', 'k'); set(Z, 0, '5'); set(Z, 1, '4');
  check(Z.phase === 'eff' && Z.step === 'u5' && R.view(Z, 0).can.eff.e5 && R.view(Z, 1).can.eff === null && R.view(Z, 1).wait, '5 を セットした 人と 4 を セットした 人：はじめは 5（第4.190版：1つずつ・4 は いちばん あと＝相手は 待つ）');
  const rz0 = eff(Z, 0, { u5: U(Z, 0, '7') }), rz = eff(Z, 1, { u4: true });
  check(names(rz0) === 'effd,u5,efft' && rz0.ev[2].st === 'u4' && names(rz) === 'effd,first' && Z.phase === 'swap' && Z.pend.who === 0 && Z.p[0].set.blind === true && Z.p[0].set.c.k === 'k',
    '5 → 4 の 順（4 は いちばん あと）：5 を 行って から 4 を 聞く・山札から ふせた カードも、相手の 4 の 効果で 交換に なる');
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
  // 不発（第4.190版）：同じ 効果を 2人 いっしょに 使って、山札が 1まい だけ → 席 0 が 先・席 1 は 不発（5 と 手札は そのまま）
  const Y2 = G('51234', '52367', '6'); set(Y2, 0, '5'); set(Y2, 1, '5');
  Y2.discard.push(...Y2.deck.splice(0, Y2.deck.length - 1).map(c => ({ u: c.u, k: c.k, by: 0, why: 't', turn: 1 })));      // 山札を 上の 1まい（6）だけに する
  eff(Y2, 0, { u5: U(Y2, 0, '4') }); const ry2 = eff(Y2, 1, { u5: U(Y2, 1, '7') });
  check(ry2.ok && names(ry2).startsWith('effd,u5,fizz,open') && ry2.ev[1].who === 0 && ry2.ev[2].who === 1 && ry2.ev[2].k === '5' && ry2.ev.find(e => e.e === 'open').c.map(x => x.k).join('') === '65' && Y2.p[1].hand.some(c => c.k === '7') && Y2.deck.length === 0 && sane(Y2),
    '2人とも 5 の 効果・山札が 1まい：席 0 が 山札の 6 を セット・席 1 は 不発（5 の まま・捨てる はずの 7 も 手札に のこる）');
  // 5 と 7（第4.190版：7 を 行って から、その あとの 手札で 5 を 聞く）
  const C7 = G('57771', '12346', '2346'); set(C7, 0, '5'); set(C7, 1, '1');
  check(C7.step === 'x7' && R.view(C7, 0).can.eff.e7 && !R.view(C7, 0).can.eff.e5 && eff(C7, 0, { u5: U(C7, 0, '7'), x7: true }).why === 'e5' && C7.phase === 'eff', '5 と 7：先に 7 を 聞く（5 は まだ・2つ いっしょに 送る 手は 受けつけない）');
  const rc0 = eff(C7, 0, { x7: true }, rngOf(4));
  check(rc0.ok && names(rc0) === 'effd,x7,efft' && rc0.ev[1].drew.map(c => c.k).join('') === '234' && rc0.ev[2].st === 'u5' && R.view(C7, 0).can.eff.e5 && ks(C7.p[0].hand).split('').sort().join('') === '1234', '7 を 行って（3まい 交換）から 5 を 聞く（手札は 1・2・3・4）');
  const rc = eff(C7, 0, { u5: U(C7, 0, '4') });
  check(rc.ok && names(rc).startsWith('effd,u5,open,clear,turn') && rc.ev[1].drop.k === '4' && ks(C7.p[0].hand).split('').sort().join('') === '123' && sane(C7), '5 で 7 の 効果で 引いた カード（4）を 捨てる ことも できる');
  const C4 = G('57777', '12346'); set(C4, 0, '5'); set(C4, 1, '1'); eff(C4, 0, { x7: true }, rngOf(4));
  check(C4.step === 'u5' && C4.p[0].hand.length === 4 && C4.p[0].hand.filter(c => c.k === '7').length === 1 && R.view(C4, 0).can.eff.e5 && eff(C4, 0, { u5: U(C4, 0, '7') }).ok && C4.p[0].hand.length === 3 && sane(C4),
    '7 が 4まい：3まい 交換した あと、のこった 7 を 5 の 効果で 捨てられる');
}

console.log('■ 3：手札に 3 が 3まい → 3まいを 見せて、その 1まいと 相手の 手札の 1まい（くじ）を 交換（第4.177版）');
{
  const mk = () => { const S = G('33312', '4567k'); set(S, 0, '1'); set(S, 1, '7'); return S; };
  const S = mk(), t3 = S.p[0].hand.filter(c => c.k === '3').map(c => c.u), h1 = S.p[1].hand.map(c => c.u);
  check(S.phase === 'eff' && JSON.stringify(R.view(S, 0).can.eff) === '{"e6":false,"e7":false,"e3":true,"e5":false,"e4":false,"st":"x3","n":1}' && R.view(S, 1).can.eff === null && R.view(S, 1).wait === true,
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
  // 5 と いっしょに（第4.190版：3 を 行って から、その あとの 手札で 5 を 聞く）
  const C = G('53331', '12467', '2'); set(C, 0, '5'); set(C, 1, '1');
  check(C.step === 'x3' && R.view(C, 0).can.eff.e3 && !R.view(C, 0).can.eff.e5 && eff(C, 0, { u5: U(C, 0, '3'), x3: true }).why === 'e5' && C.phase === 'eff', '5 と 3：先に 3 を 聞く（5 は まだ・2つ いっしょに 送る 手は 受けつけない）');
  const rc0 = eff(C, 0, { x3: true }, rngOf(4));
  check(rc0.ok && names(rc0) === 'effd,x3,efft' && rc0.ev[2].st === 'u5' && R.view(C, 0).can.eff.e5 && C.p[0].hand.filter(c => c.k === '3').length === 2 && C.p[0].hand.length === 4, '3 を 行って（交換）から 5 を 聞く');
  const rc = eff(C, 0, { u5: U(C, 0, '3') });
  check(rc.ok && names(rc).startsWith('effd,u5,open,clear,turn') && rc.ev[1].drop.k === '3' && rc.ev[2].c[0].k === '2' && C.p[0].hand.length === 3 && sane(C), '5 で 3 を 捨てる ことも できる（3 の 効果は もう 終わって いる）');
  // 順番（第4.190版）：6（ターンの はじめ）→ セット → 3 → 5 → 4（1つずつ）
  const O = G('43331', '66125');
  check(O.phase === 'six' && R.view(O, 1).can.six && R.view(O, 0).can.six === null, '（席 1 は 6 が 2まい：ターンの はじめに 6 を 聞く）');
  const ro0 = p6(O, 1, U(O, 0, '1')); set(O, 0, '4'); const ro1 = set(O, 1, '5');
  check(names(ro0) === 'sixd,p6' && names(ro1) === 'set,efft' && O.step === 'x3' && R.view(O, 0).can.eff.e3 && R.view(O, 1).can.eff === null, '6 → セット → 効果タイムは 3 から（席 0）');
  const ro2 = eff(O, 0, { x3: true }, rngOf(9)), tx3 = ro2.ev[1];
  check(names(ro2) === 'effd,x3,efft' && O.step === 'u5' && R.view(O, 1).can.eff.e5 && O.p[1].hand.some(c => c.u === tx3.give.u), '3 を 行う → 5（席 1）：3 で もらった 3 も 手札に ある');
  const ro3 = eff(O, 1, { u5: tx3.give.u });
  check(names(ro3) === 'effd,u5,efft' && ro3.ev[1].drop.u === tx3.give.u && O.step === 'u4' && R.view(O, 0).can.eff.e4, '5 を 行う（3 で もらった 3 を 捨てる）→ 4（席 0：いちばん あと）');
  const ro4 = eff(O, 0, { u4: true });
  check(names(ro4) === 'effd,first' && O.phase === 'swap' && O.pend.who === 1 && O.p[1].set.blind === true && sane(O), '4 を 行う：相手は 5 の 効果で 山札から ふせた カードを 交換する 番');
  // 第4.190版：決めるのは 前の 効果を 行った あと ＝ 前の 効果で 手札が かわっても 不発に ならない
  const F = G('33312', '51246'); set(F, 0, '1'); set(F, 1, '1'); eff(F, 0, null); set(F, 0, '2'); set(F, 1, '2'); eff(F, 0, null); toDis(F, 1, '4'); fromDeck(F, 0, '6');
  check(F.turn === 3 && ks(F.p[0].hand) === '3336' && ks(F.p[1].hand) === '56', '（3ターン目：自分は 3・3・3・6／相手は 5・6 に した）');
  set(F, 0, '6'); set(F, 1, '5'); const rf0 = eff(F, 0, { x3: true });
  check(rf0.ok && names(rf0) === 'effd,x3,efft' && rf0.ev[1].take.k === '6' && rf0.ev[2].st === 'u5' && ks(F.p[1].hand) === '3' && R.view(F, 1).can.eff.e5, '3 の 効果（先）で 相手の さいごの 手札（6）を もらう → 相手は もらった 3 の 1まいで 5 を 聞かれる');
  const rf = eff(F, 1, { u5: U(F, 1, '3') });
  check(rf.ok && names(rf) === 'effd,u5,open,clear,end' && rf.ev[1].drop.k === '3' && F.p[1].hand.length === 0 && sane(F), '5 の 効果：もらった 3 を 捨てて 使える（前は 先に まとめて 決めて いた ので 不発に なって いた）');
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
  check(r2.ok && names(r2) === 'swap,ask5' && S.phase === 'u5' && S.pend.type === 'u5' && S.pend.who === 1 && R.view(S, 1).pend.type === 'u5' && R.view(S, 1).phase === 'u5'
    && R.view(S, 0).pend.type === 'swap' && R.view(S, 0).phase === 'swap' && R.view(S, 0).wait === true && R.evFor(r2.ev, 0).map(e => e.e).join() === 'swap' && R.evFor(r2.ev, 1).map(e => e.e).join() === 'swap,ask5'
    && R.legal(S, 1).join() === 'u5' && R.legal(S, 0).join() === '',
    '第4.183版：相手は 1 を 手札に もどして 5 を 出した → 5 の 効果を 使うか 聞く（オープンは まだ）。4 を 出した 人には「交換して いる」まま に 見える（5 だと わからない）');
  const r2b = R.act(S, 1, { t: 'u5', drop: null });
  check(r2b.ok && names(r2b) === 'u5skip,open,clear,turn' && r2b.ev[1].c.map(x => x.k).join('') === '45' && r2b.ev[1].res === 0 && S.p[0].wins === 1 && ks(S.p[1].hand).split('').sort().join('') === '1677'
    && R.evFor(r2b.ev, 0).map(e => e.e).join() === 'open,clear,turn',
    '5 の 効果を 使わない → そのまま オープン：4 と 5 で 4 の 勝ち（もどした 1 は 手札に のこる・使わなかった ことも 相手には わたさない）');
  const B = G('41236', '41567'); set(B, 0, '4'); set(B, 1, '4'); eff(B, 0, { u4: true }); const rb = eff(B, 1, { u4: true });
  const eb1 = R.evFor(rb.ev, 1)[2], vb0 = R.view(B, 0), vb1 = R.view(B, 1);
  check(names(rb) === 'effd,first2,open,clear,turn' && rb.ev[2].res === 'tie' && rb.ev[2].d4 === true && rb.ev[2].c.map(x => x.k).join('') === '44' && B.p[0].wins === 0 && B.p[1].wins === 0
    && B.last.res === 'tie' && B.last.d4 === true && vb0.last.res === 'tie' && vb0.last.d4 === true && vb1.last.res === 'tie' && vb1.last.d4 === true && eb1.res === 'tie' && eb1.d4 === true && !B.win && B.turn === 2 && B.phase === 'set',
    '両方が 4 の 効果を 使った → 打ち消し（交換なし）→ ドロー（第4.181版：どちらの 勝ちにも 数えない・2人の 画面にも「4 の 効果で ドロー」と わたる。前は 4 と 4 の かぶり＝どちらも 負け）');
  const B0 = G('41236', '41567'); set(B0, 0, '4'); set(B0, 1, '4'); eff(B0, 0, null); const rb0 = eff(B0, 1, null);
  check(names(rb0) === 'effd,open,clear,turn' && rb0.ev[1].res === 'clash' && rb0.ev[1].d4 === undefined && B0.last.d4 === false && R.view(B0, 0).last.d4 === false && B0.p[0].wins === 0 && B0.p[1].wins === 0,
    '2人とも 4 を 出して、2人とも 効果を 使わない → いままで どおり かぶり（どちらも 負け）');
  const B1 = G('41236', '41567'); set(B1, 0, '4'); set(B1, 1, '4'); eff(B1, 1, { u4: true }); eff(B1, 0, null);
  check(B1.phase === 'swap' && B1.pend.who === 0, '2人とも 4 を 出して、1人 だけ 効果を 使う → 使わなかった 人が 交換する（前と 同じ）');
  const r1 = R.act(B1, 0, { t: 'swap', u: U(B1, 0, '1') });
  check(r1.ok && r1.ev[1].res === 0 && !r1.ev[1].d4 && B1.p[0].wins === 1, '交換して 1 を 出した → 1 の 勝ち（ドローに ならない）');
  const L4 = G('41', '42', '', 1); set(L4, 0, '4'); set(L4, 1, '4'); eff(L4, 0, { u4: true }); const rl = eff(L4, 1, { u4: true });
  check(rl.ok && L4.phase === 'end' && L4.res === 'draw' && rl.ev.some(e => e.e === 'open' && e.d4 && e.res === 'tie'), 'さいごの ターンで 2人とも 4 の 効果 → ドロー（勝ち 0 対 0 → 同点）');
  const N = G('41236', '15677'); set(N, 0, '4'); set(N, 1, '1'); const rn = eff(N, 0, null);
  check(names(rn) === 'effd,open,clear,turn' && rn.ev[1].res === 1, '効果を 使わなければ ふつうに オープン（4 と 1 → 1 の 勝ち）');
  const F = G('77712', '12347', '346'); set(F, 0, '1'); set(F, 1, '2'); check(eff(F, 0, { u4: true }).why === 'e4' && F.phase === 'eff', '4 を セットして いない 人が「4 の 効果」と 言っても 受けつけない');
  const W = G('41236', '45677'); set(W, 1, '4'); set(W, 0, '4'); eff(W, 1, null); eff(W, 0, { u4: true });
  check(W.phase === 'swap' && W.pend.who === 1, '相手も 4 を セットして いた（効果は 使わない）→ 相手は 交換する');
  R.act(W, 1, { t: 'swap', u: U(W, 1, '5') }); R.act(W, 1, { t: 'u5', drop: null });
  check(W.p[0].wins === 1 && W.p[1].hand.some(c => c.k === '4'), '交換して 5 を 出した（5 の 効果は 使わない）→ 4 の 勝ち');
}

console.log('■ 4 の 効果で 交換して 5 を 出したら、5 の 効果を 使える（第4.183版・まさちゃん 21:24「4で交換したあとに5を相手がフィールドにセットした場合、五の効果を使える」）');
{
  const S = G('41236', '15677', 'k'); set(S, 1, '1'); set(S, 0, '4'); eff(S, 0, { u4: true });
  R.act(S, 1, { t: 'swap', u: U(S, 1, '5') });
  check(S.phase === 'u5' && R.act(S, 0, { t: 'u5', drop: null }).why === 'u5' && R.act(S, 1, { t: 'u5', drop: U(S, 0, '1') }).why === 'drop' && R.act(S, 1, { t: 'swap', u: U(S, 1, '6') }).why === 'swap'
    && !set(S, 1, '6').ok && R.act(S, 1, { t: 'eff', use: null }).why === 'eff' && S.phase === 'u5' && sane(S),
    'まちがった 手は 受けつけない（4 を 出した 人・相手の カード・交換の やり直し・ふつうの セット・効果タイムの 手）');
  const r = R.act(S, 1, { t: 'u5', drop: U(S, 1, '6') });
  const e0 = R.evFor(r.ev, 0), e1 = R.evFor(r.ev, 1);
  check(r.ok && names(r) === 'u5,open,clear,turn,pre' && r.ev[0].sw === true && r.ev[1].c.map(x => x.k).join('') === '4k' && r.ev[1].res === 1 && S.p[1].wins === 1 && S.p[0].wins === 0
    && S.discard.filter(d => d.why === '5').map(d => d.k).join('') === '56' && ks(S.p[1].hand).split('').sort().join('') === '177' && e0[0].e === 'u5' && e0[0].five.k === '5' && e0[0].drop.k === '6' && e1[0].e === 'u5' && sane(S),
    '5 の 効果を 使う：5 と 手札の 6 を 捨てて、山札の 上（神様馬）を ふせて セット → オープン：4 と 神様馬 → 神様馬の 勝ち（捨てた 5・6 は 2人とも 見える・次の ターンの はじめに 神様馬の 効果）');
  const N5 = G('41', '512'); set(N5, 1, '1'); set(N5, 0, '4'); eff(N5, 0, { u4: true }); const rn = R.act(N5, 1, { t: 'swap', u: U(N5, 1, '5') });
  check(rn.ok && names(rn) === 'swap,open,clear,turn' && N5.phase === 'set' && N5.p[0].wins === 1, '使った あとの 手札が のこりの ターンの 数より 少なく なる（手札 2まい・あと 2ターン）→ 聞かれない（そのまま オープン）');
  const E = G('4', '51', 'k', 1); set(E, 1, '1'); set(E, 0, '4'); eff(E, 0, { u4: true }); const re1 = R.act(E, 1, { t: 'swap', u: U(E, 1, '5') });
  const re2 = R.act(E, 1, { t: 'u5', drop: U(E, 1, '1') });
  check(names(re1) === 'swap,ask5' && re2.ok && E.phase === 'end' && E.res === 1 && E.p[1].hand.length === 0 && sane(E), 'さいごの ターン：手札が 1まい（交換で もどった カード）でも 使える → 山札の 神様馬で 勝ち（まさちゃんの 5 の 例と 同じ 考え方）');
  const D = G('41236', '15677'); set(D, 1, '1'); set(D, 0, '4'); eff(D, 0, { u4: true }); while (D.deck.length) { const c = D.deck.pop(); D.discard.push({ u: c.u, k: c.k, by: 0, why: 't', turn: 1 }); }
  const rd = R.act(D, 1, { t: 'swap', u: U(D, 1, '5') });
  check(names(rd) === 'swap,open,clear,turn' && sane(D), '山札が ない → 聞かれない');
  const X = G('41236', '15677'); set(X, 1, '1'); set(X, 0, '4'); eff(X, 0, { u4: true }); const rx = R.act(X, 1, { t: 'swap', u: U(X, 1, '6') });
  check(names(rx) === 'swap,open,clear,turn', '交換で 5 で ない カード（6）を 出した → いつも どおり オープン');
  const F = G('41236', '55677', 'k'); set(F, 1, '5'); set(F, 0, '4'); eff(F, 1, { u5: U(F, 1, '6') }); eff(F, 0, { u4: true });
  check(F.phase === 'swap' && F.p[1].set.blind === true, '効果タイムで 5 の 効果を 使った（山札から ふせた カード）あとで 4 の 効果 → 交換（4 は いちばん あと）');
  R.act(F, 1, { t: 'swap', u: U(F, 1, '5') });
  check(F.phase === 'u5' && F.p[1].hand.length === 3, '交換で もう 1まいの 5 を 出した → また 5 の 効果を 使うか 聞く（手札 3まい・あと 2ターン）');
  // コンピュータ：4 に 勝てる カードも 4 も ない とき、5 の 効果を 使えるなら 5 を 出して、5 の 効果を 使う
  const Cx = G('41236', '75677'); set(Cx, 1, '7'); set(Cx, 0, '4'); eff(Cx, 0, { u4: true });
  const ca = C.decide(R.view(Cx, 1), rngOf(1)); R.act(Cx, 1, ca);
  const cb = C.decide(R.view(Cx, 1), rngOf(1)); const rcb = R.act(Cx, 1, cb);
  check(ca.t === 'swap' && Cx.discard.some(d => d.k === '5' && d.why === '5') && cb.t === 'u5' && cb.drop != null && rcb.ok && names(rcb).startsWith('u5,open'),
    'コンピュータ：4 に 勝てる カードも 4 も ない → 5 を 出す → 5 の 効果を 使う（1番 弱い 7 を 捨てる）');
  const Cy = G('41236', '15677'); set(Cy, 1, '7'); set(Cy, 0, '4'); eff(Cy, 0, { u4: true }); const cy = C.decide(R.view(Cy, 1), rngOf(1));
  check(cy.t === 'swap' && Cy.p[1].hand.find(c => c.u === cy.u).k === '1', 'コンピュータ：4 に 勝てる カード（1）が あれば そちら（前と 同じ）');
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

console.log('■ 5ターン・手札 7まい（第4.178版・まさちゃん 2026/11/16 14:43「カードバトル５ターン勝負にする 手札7枚にして！」）');
{
  const S = G('1236745', '2367145', '', 5);
  check(S.turns === 5 && S.p[0].hand.length === 7 && S.p[1].hand.length === 7 && S.deck.length === 16 && R.view(S, 1).turns === 5 && sane(S), '手札 7まい ずつ・山札 16まい・5ターン');
  set(S, 0, '1'); set(S, 1, '2'); set(S, 0, '2'); set(S, 1, '3'); set(S, 0, '3'); const r3 = set(S, 1, '6');
  check(names(r3) === 'set,open,clear,turn' && S.p[0].wins === 3 && S.phase === 'set' && S.turn === 4 && r3.ev[3].n === 4, '先に 3勝 しても 4ターン目へ（5ターン ぜんぶ やる）');
  set(S, 0, '6'); const r4 = set(S, 1, '7');
  check(names(r4) === 'set,open,clear,turn' && S.turn === 5 && S.p[0].wins === 4 && S.p[0].hand.length === 3, '4ターン目の あと：5ターン目へ（手札は 3まい）');
  set(S, 0, '7'); const r5 = set(S, 1, '1');
  check(names(r5) === 'set,open,clear,end' && S.phase === 'end' && S.res === 0 && r5.ev[3].wins.join() === '4,1' && ks(S.p[0].hand) === '45' && ks(S.p[1].hand) === '45' && S.discard.length === 10 && sane(S),
    '5ターン目で おわり：勝った 数が 多い 方の 勝ち（4勝 1勝）・手札は 2まい ずつ のこる・捨て札 10まい');
  // 5 の 効果：手札 7まい・5ターン ＝ よぶんは 2まい → 2回 まで 使える（3回目は 手札が 足りなく なる ので 使えない）
  const F = G('5551234', '1123677', '666', 5);
  set(F, 0, '5'); const f1 = set(F, 1, '7');
  check(names(f1) === 'set,efft' && R.view(F, 0).can.eff.e5 === true && F.p[0].hand.length === 6, '1ターン目に 5 を セット（手札 6まい）：5 の 効果を 使える（使った あと 5まい ≧ のこり 4ターン）');
  const f1e = eff(F, 0, { u5: U(F, 0, '4') });
  check(f1e.ok && names(f1e) === 'effd,u5,open,clear,turn' && f1e.ev[2].c.map(x => x.k).join('') === '67' && F.p[0].hand.length === 5 && F.turn === 2, '使う（4 を 捨てる）→ 山札の 6 が 出て 7 に 勝ち・手札 5まいで 2ターン目へ');
  set(F, 0, '5'); const f2 = set(F, 1, '7');
  check(names(f2) === 'set,efft' && R.view(F, 0).can.eff.e5 === true && F.p[0].hand.length === 4, '2ターン目に 5 を セット（手札 4まい）：また 使える（使った あと 3まい ≧ のこり 3ターン）');
  eff(F, 0, { u5: U(F, 0, '3') });
  check(F.turn === 3 && F.p[0].hand.length === 3 && ks(F.p[0].hand) === '512', '2回 使った：3ターン目の 手札は 3まい（5・1・2）');
  set(F, 0, '5'); const f3 = set(F, 1, '6');
  check(names(f3) === 'set,open,clear,turn' && F.turn === 4 && F.p[0].hand.length === 2, '3ターン目に 5 を セット（手札 2まい）：もう 使えない（使うと 1まい ＜ のこり 2ターン）→ 効果タイムに ならずに オープン');
  set(F, 0, '2'); set(F, 1, '3'); set(F, 0, '1'); const f5 = set(F, 1, '2');
  check(F.phase === 'end' && names(f5) === 'set,open,clear,end' && F.p[0].hand.length === 0 && F.p[0].wins === 5 && sane(F), '5ターン目まで カードが 足りる（手札 0まいで おわり・5勝）');
  // さいごの ターン（5ターン目）に 神様馬で 勝っても 効果は 出ない・4ターン目に 勝てば 5ターン目の はじめに 出る
  const K = G('k123677', '2233677', '', 5);
  set(K, 0, '1'); set(K, 1, '2'); set(K, 0, '2'); set(K, 1, '3'); set(K, 0, '3'); set(K, 1, '6'); set(K, 0, 'k'); const k4 = set(K, 1, '7');
  check(K.turn === 5 && K.phase === 'pre' && K.pend.type === 'k' && K.pend.who === 0 && names(k4).indexOf('pre') > 0, '4ターン目に 神様馬で 勝った → 5ターン目の はじめに 効果を 聞く');
  const K5 = G('k123677', '2233677', '', 5);
  set(K5, 0, '1'); set(K5, 1, '2'); set(K5, 0, '2'); set(K5, 1, '3'); set(K5, 0, '3'); set(K5, 1, '6'); set(K5, 0, '6'); set(K5, 1, '7'); set(K5, 0, 'k'); const k5 = set(K5, 1, '7');
  check(K5.phase === 'end' && names(k5) === 'set,open,clear,end' && !K5.pend && K5.p[0].wins === 5, '5ターン目（さいご）に 神様馬で 勝った → 効果は 出ない（次の ターンが ない）');
}

console.log('■ 6：もう 見た カード しか ない ときは 発動しない（第4.178版・まさちゃん「6.の効果は、もう見てるカードしかない場合は、発動しなくして！」）・第4.190版：ターンの はじめに 聞く');
{
  // 3ターン・手札 5まいの 形で（しくみは 同じ）：6 を 2まい 持ち続けて、相手の 手札を 1まい ずつ 見て いく
  const S = G('66712', '12345');
  check(S.phase === 'six' && R.view(S, 0).can.six, '1ターン目の はじめ：相手の 手札（1〜5）は まだ 1まいも 見て いない → 6 の 効果を 使える');
  p6(S, 0, U(S, 1, '5')); set(S, 0, '7'); set(S, 1, '1');
  check(S.turn === 2 && S.phase === 'six' && R.view(S, 0).op.hand.filter(c => c.k).map(c => c.k).join('') === '5', '5 を 見た → 2ターン目の はじめ：相手の 手札（2・3・4・5）に まだ 見て いない カードが ある → また 聞かれる');
  const bad6 = p6(S, 0, U(S, 1, '5'));
  check(!bad6.ok && bad6.why === 'pick' && S.phase === 'six' && !S.p[0].six.done, 'もう 見た カード（5）を 見る 手は 受けつけない（見るのは まだ 見て いない カード だけ）');
  p6(S, 0, U(S, 1, '4')); set(S, 0, '1'); set(S, 1, '2');
  check(S.turn === 3 && S.phase === 'six' && R.view(S, 0).op.hand.filter(c => c.k).map(c => c.k).sort().join('') === '45', '4 を 見た（見た カードは 4 と 5）→ 3ターン目の はじめ：まだ 見て いない 3 が ある → 聞かれる');
  check(p6(S, 0, U(S, 1, '4')).why === 'pick' && p6(S, 0, U(S, 1, '3')).ok && S.phase === 'set' && R.view(S, 0).op.hand.every(c => c.k), 'えらべるのは まだ 見て いない 3 だけ → 相手の 手札を ぜんぶ 見た');
  // 相手の 手札が ぜんぶ もう 見た カード：6 が 2まい あっても ターンの はじめに 聞かれない
  const A = G('66712', '12345'); p6(A, 0, null); set(A, 0, '7');
  A.p[1].hand.filter(c => c.k !== '1').forEach(c => A.p[0].known.push(c.u));                     // 2・3・4・5 を ぜんぶ 見た ことに する（1 は これから セット）
  const a1 = set(A, 1, '1');
  check(names(a1) === 'set,open,clear,turn' && A.turn === 2 && A.phase === 'set' && R.view(A, 0).can.six === null, '相手の 手札を ぜんぶ 見て いる：次の ターンの はじめに 6 の 効果は 聞かれない');
  const T = G('66712', '12345'); p6(T, 0, null); set(T, 0, '7');
  T.p[1].hand.filter(c => c.k !== '1' && c.k !== '2').forEach(c => T.p[0].known.push(c.u));      // 3・4・5 を 見た ことに する（のこりは 2 と、これから セットする 1）
  const t1 = set(T, 1, '1');
  check(names(t1) === 'set,open,clear,turn,sixt' && T.phase === 'six' && !p6(T, 0, U(T, 1, '3')).ok && p6(T, 0, U(T, 1, '2')).ok, '見て いない カードが 1まい（2）だけ：使える・えらべるのは その 1まい だけ');
  // 効果タイムで「6 の 効果」と 言っても 受けつけない（第4.190版：6 は ターンの はじめ）
  const B = G('66777', '12345', '123'); p6(B, 0, null); set(B, 0, '6'); const b1 = set(B, 1, '1');
  check(names(b1) === 'set,efft' && R.view(B, 0).can.eff.e7 === true && R.view(B, 0).can.eff.e6 === false && eff(B, 0, { p6: U(B, 1, '2') }).why === 'e6' && eff(B, 0, { x7: true }).ok, '効果タイム（7）で「6 の 効果」と 言っても 受けつけない（6 は ターンの はじめ）');
  // 神様馬の 効果も 同じ 考え方（姫が 決めた 所）：相手の 手札が ぜんぶ もう 見た カードなら 聞かれない。第4.190版：6 が 先（6 で さいごの 1まいを 見たら、神様馬の 効果は 聞かれない）
  const mkK = () => { const K = G('k6672', '12345'); p6(K, 0, U(K, 1, '5')); set(K, 0, '7'); set(K, 1, '1'); p6(K, 0, U(K, 1, '4')); set(K, 0, 'k'); set(K, 1, '2'); return K; };
  const K = mkK();
  check(K.turn === 3 && K.phase === 'six' && K.win && K.win.type === 'k', '神様馬で 勝った：3ターン目の はじめは まず 6（相手の 手札 3・4・5 の うち 3 は まだ 見て いない）');
  const k2 = p6(K, 0, null);
  check(names(k2) === 'sixd,p6skip,pre' && K.phase === 'pre' && K.pend.type === 'k', '6 を 使わなければ、神様馬の 効果を 聞く（まだ 見て いない 3 が ある）');
  const kb = R.act(K, 0, { t: 'k', pick: U(K, 1, '5') });
  check(!kb.ok && kb.why === 'pick' && K.phase === 'pre' && R.act(K, 0, { t: 'k', pick: U(K, 1, '3') }).ok && K.phase === 'set', '神様馬の 効果でも、もう 見た カード（5）は えらべない・見て いない 3 は 見られる');
  const K2 = mkK(), k3 = p6(K2, 0, U(K2, 1, '3'));
  check(names(k3) === 'sixd,p6' && K2.phase === 'set' && !K2.pend && !K2.win, '6 で さいごの 見て いない カード（3）を 見たら、相手の 手札は ぜんぶ 見た → 神様馬の 効果は 聞かれない');
  const cv = mkK(); p6(cv, 0, null);
  const ck = C.decide(R.view(cv, 0), rngOf(3));
  check(ck.t === 'k' && ck.pick === U(cv, 1, '3'), 'コンピュータ：神様馬の 効果では まだ 見て いない カード（3）を 見る');
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
  // 効果タイム：相手が 何を 使えるか は 渡さない（第4.190版：いま どの 効果を 聞いて いるかも 聞かれる 人 だけ）
  const E = G('51234', '77712', '346'); set(E, 0, '5'); set(E, 1, '2');
  const x0 = R.view(E, 0), x1 = R.view(E, 1), j0 = JSON.stringify(x0);
  check(E.step === 'x7' && x0.can.eff === null && JSON.stringify(x1.can.eff) === '{"e6":false,"e7":true,"e3":false,"e5":false,"e4":false,"st":"x7","n":1}' && j0.indexOf('"st"') < 0 && !('eff' in x0.op) && !('eff' in x0.my) && x0.wait === true,
    '効果タイム：自分が 使える 効果 だけ 渡す（相手が 何を えらんで いるかは 渡さない）');
  eff(E, 1, null);
  const y0 = R.view(E, 0);
  check(E.step === 'u5' && JSON.stringify(y0.can.eff) === '{"e6":false,"e7":false,"e3":false,"e5":true,"e4":false,"st":"u5","n":2}' && R.view(E, 1).can.eff === null && JSON.stringify(R.view(E, 1)).indexOf('"st"') < 0, '次の 効果（5）も 聞かれる 人 だけ');
  const S6 = G('66123', '12345'), z1 = R.view(S6, 1);
  check(z1.can.six === null && z1.wait === true && JSON.stringify(z1.op).indexOf('six') < 0, 'ターンの はじめ：相手が 6 の 効果を えらんで いる あいだ、自分には 待つ こと だけ');
}

console.log('■ 逆転勝利：1 が 3まい（場 ＋ 手札 2まい）→ 神様馬・幻の馬に 勝てる（第4.178版・まさちゃん 15:33／15:41「A、オープンしてから」）');
{
  const S = G('11123', 'm4567'); set(S, 0, '1'); const r = set(S, 1, 'm');
  check(r.ok && names(r) === 'set,open' && S.phase === 'rev' && S.pend.type === 'rev' && S.pend.who === 0 && r.ev[1].res === 1 && r.ev[1].rev === 0 && r.ev[1].wins.join() === '0,0' && S.p[0].wins === 0 && S.p[1].wins === 0 && S.turn === 1 && S.discard.length === 0,
    '1（手札に 1 が あと 2まい）と 幻の馬 → オープンした 所で 止まる：負けた 人（1 の 方）が 使うか 決める 番（勝ち負けは まだ 数えない）');
  const v0 = R.view(S, 0), v1 = R.view(S, 1), e0 = R.evFor(r.ev, 0)[1], e1 = R.evFor(r.ev, 1)[1];
  check(v0.phase === 'rev' && v0.pend.type === 'rev' && v0.pend.mine === true && v0.wait === false && R.legal(S, 0).join() === 'rev' && v1.pend.mine === false && v1.wait === true && R.legal(S, 1).length === 0
    && v0.my.set.k === '1' && v0.op.set.k === 'm' && v1.my.set.k === 'm' && v1.op.set.k === '1' && v0.my.set.open && v0.op.set.open && !v0.can.set && !v1.can.set && v0.my.wins === 0 && v0.op.wins === 0,
    '見える もの：2まいとも 表・聞かれて いる 人は「逆転勝利を 使う？」・相手は 待つ（セットは まだ できない）');
  check(e0.rev === 'me' && e0.res === 'lose' && e0.wins.join() === '0,0' && e1.rev === 'op' && e1.res === 'win' && e1.wins.join() === '0,0' && v1.op.hand.every(c => c.k === null),
    'オープンの 知らせ：どちらが 逆転勝利を 使えるか（自分／相手）・勝ちの 数は 前の まま。相手の 手札の 中身は 渡さない');
  check(R.act(S, 1, { t: 'rev', use: true }).why === 'rev' && set(S, 0, '2').why === 'set' && set(S, 1, '4').why === 'set' && R.act(S, 0, { t: 'eff', use: null }).why === 'eff' && R.act(S, 1, { t: 'm', drop: null }).why === 'm' && S.phase === 'rev' && sane(S),
    '聞かれて いない 人の「使う」・セット・ほかの 手は 受けつけない');
  const ones = S.p[0].hand.filter(c => c.k === '1').map(c => c.u);
  const r2 = R.act(S, 0, { t: 'rev', use: true }), x = r2.ev[0], f = r2.ev[1];
  check(r2.ok && names(r2) === 'rev,fin,clear,turn' && x.who === 0 && x.k === '1' && x.beat === 'm' && x.show.length === 2 && x.show.slice().sort().join() === ones.slice().sort().join() && x.drop.k === '1' && x.drop.u === x.show[0]
    && f.res === 0 && f.rev === true && f.wins.join() === '1,0' && f.turn === 1,
    '「使う」→ 手札の 1 を 2まい 見せて（場の 1 と 合わせて 3まい）、その 1まいを 捨てる → この ターンは 1 の 勝ち（1勝 0勝）');
  check(S.p[0].wins === 1 && S.p[1].wins === 0 && S.turn === 2 && S.phase === 'set' && !S.pend && ks(S.p[0].hand) === '123' && S.p[1].hand.length === 4 && sane(S)
    && S.discard.map(d => d.k + d.why + d.by).join() === '110,1t0,mt1' && S.last.res === 0 && S.last.rev === true && R.view(S, 0).last.res === 'win' && R.view(S, 0).last.rev === true && R.view(S, 1).last.res === 'lose',
    '手札は 1・2・3（1 が 1まい へった）・捨て札＝効果で 捨てた 1 ＋ 出した 2まい・幻の馬の「勝ったら」の 効果は 出ない（負けた）→ 2ターン目の セットへ');
  const keep = S.p[0].hand.find(c => c.k === '1');
  check(S.p[1].known.indexOf(keep.u) >= 0 && S.p[1].known.length === 1 && R.view(S, 0).my.hand.filter(c => c.seen).map(c => c.k).join() === '1' && R.view(S, 1).op.hand.filter(c => c.k).map(c => c.k).join() === '1',
    '見せて 手札に のこった 1 は 相手に 知られた カード（自分の 画面では 目の しるし・相手の 画面では 表）');
  const g0 = R.evFor(r2.ev, 0), g1 = R.evFor(r2.ev, 1);
  check(g0[0].me === true && g1[0].me === false && g1[0].k === '1' && g1[0].beat === 'm' && g1[0].show.length === 2 && g1[0].drop.k === '1' && g0[1].res === 'win' && g1[1].res === 'lose' && g0[1].wins.join() === '1,0' && g1[1].wins.join() === '0,1' && g1[1].rev === true,
    '知らせ（2人とも）：見せた 2まい・捨てた 1・結果（使った 人「勝ち」・相手「負け」）');
  // 使わない
  const N = G('11123', 'm4567'); set(N, 0, '1'); set(N, 1, 'm'); const rn = R.act(N, 0, { t: 'rev', use: false });
  check(rn.ok && names(rn) === 'revskip,fin,clear,turn,pre' && rn.ev[1].res === 1 && rn.ev[1].rev === false && N.p[0].wins === 0 && N.p[1].wins === 1 && ks(N.p[0].hand) === '1123' && N.p[1].known.length === 0 && N.phase === 'pre' && N.pend.type === 'm' && N.pend.who === 1
    && N.discard.map(d => d.k + d.why).join() === '1t,mt' && N.last.rev === false && sane(N),
    '「使わない」→ そのまま 負け（手札は そのまま・何も 見せない）→ 幻の馬で 勝った 相手は 次の ターンの はじめに 効果を えらぶ（いつも どおり）');
  // 神様馬にも 勝てる
  const K = G('11145', 'k2367'); set(K, 1, 'k'); const rk = set(K, 0, '1');
  check(names(rk) === 'set,open' && K.phase === 'rev' && K.pend.who === 0 && rk.ev[1].rev === 0, '1（3まい）と 神様馬 → 聞かれる（相手が 先に セットして いても 同じ）');
  const rk2 = R.act(K, 0, { t: 'rev', use: true });
  check(names(rk2) === 'rev,fin,clear,turn' && rk2.ev[0].beat === 'k' && K.p[0].wins === 1 && K.phase === 'set' && !K.pend && ks(K.p[0].hand) === '145', '使う → 神様馬に 勝ち（神様馬の 効果は 出ない）');
  const K2 = G('11145', 'k2367'); set(K2, 0, '1'); set(K2, 1, 'k'); const rk3 = R.act(K2, 0, { t: 'rev', use: false });
  check(names(rk3) === 'revskip,fin,clear,turn,pre' && K2.pend.type === 'k' && K2.pend.who === 1 && K2.p[1].wins === 1, '使わない → 神様馬の 勝ち → 相手の 神様馬の 効果');
  // 席 1 でも 同じ
  const B = G('m4567', '11123'); set(B, 0, 'm'); const rb = set(B, 1, '1');
  check(B.phase === 'rev' && B.pend.who === 1 && rb.ev[1].res === 0 && rb.ev[1].rev === 1 && R.evFor(rb.ev, 1)[1].rev === 'me' && R.evFor(rb.ev, 0)[1].rev === 'op' && R.legal(B, 1).join() === 'rev' && R.legal(B, 0).length === 0, '席が 入れかわっても 同じ（聞かれるのは 1 を 出した 人）');
  R.act(B, 1, { t: 'rev', use: true });
  check(B.p[1].wins === 1 && B.p[0].wins === 0 && ks(B.p[1].hand) === '123' && B.discard.map(d => d.k + d.why + d.by).join() === '111,mt0,1t1' && B.phase === 'set', '使う → 席 1 の 勝ち');
}

console.log('■ 逆転勝利：2 が 3まい → 1 に 勝てる');
{
  const S = G('22234', '14567'); set(S, 0, '2'); const r = set(S, 1, '1');
  check(names(r) === 'set,open' && S.phase === 'rev' && S.pend.who === 0 && r.ev[1].res === 1 && r.ev[1].rev === 0, '2（手札に 2 が あと 2まい）と 1 → 2 を 出した 人が 聞かれる');
  const r2 = R.act(S, 0, { t: 'rev', use: true });
  check(names(r2) === 'rev,fin,clear,turn' && r2.ev[0].k === '2' && r2.ev[0].beat === '1' && r2.ev[0].drop.k === '2' && S.p[0].wins === 1 && S.p[1].wins === 0 && ks(S.p[0].hand) === '234' && S.discard.map(d => d.k + d.why + d.by).join() === '220,2t0,1t1' && S.p[1].known.length === 1 && sane(S),
    '使う → 手札の 2 を 2まい 見せて 1まい 捨てる → 2 の 勝ち（捨て札：効果で 捨てた 2 ＋ 出した 2・1）');
  const N = G('22234', '14567'); set(N, 0, '2'); set(N, 1, '1'); const rn = R.act(N, 0, { t: 'rev', use: false });
  check(names(rn) === 'revskip,fin,clear,turn' && N.p[1].wins === 1 && N.p[0].wins === 0 && ks(N.p[0].hand) === '2234', '使わない → 1 の 勝ち');
  // 1 を 3まい 持って いても、2 の 効果には やり返せない（1 の 効果は 神様馬・幻の馬に だけ）
  const C2 = G('11134', '22256'); set(C2, 0, '1'); const rc = set(C2, 1, '2');
  check(C2.phase === 'rev' && C2.pend.who === 1 && rc.ev[1].res === 0, '1（3まい）と 2（3まい）→ 聞かれるのは 2 の 方（負けて いる 人）');
  const rc2 = R.act(C2, 1, { t: 'rev', use: true });
  check(names(rc2) === 'rev,fin,clear,turn' && C2.p[1].wins === 1 && C2.p[0].wins === 0 && C2.phase === 'set' && !C2.pend && ks(C2.p[0].hand) === '1134', '2 の 効果で 逆転 → 1 の 方は やり返せない（そのまま 次の ターン）');
}

console.log('■ 逆転勝利：使えない とき（聞かれない）');
{
  const one = (h0, h1, k0, k1, turns) => { const S = G(h0, h1, '', turns); set(S, 0, k0); const r = set(S, 1, k1); return [S, r]; };
  let [S, r] = one('11234', 'm4567', '1', 'm');
  check(names(r) === 'set,open,clear,turn,pre' && r.ev[1].rev === undefined && r.ev[1].res === 1 && r.ev[1].wins.join() === '0,1' && S.pend.type === 'm', '1 が 合わせて 2まい（手札に 1まい）→ 聞かれない（ふつうに 負け）');
  [S, r] = one('11123', '24567', '1', '2');
  check(names(r) === 'set,open,clear,turn' && r.ev[1].res === 0 && r.ev[1].rev === undefined, '1（3まい）と 2 → ふつうに 勝ち（聞かれない）');
  [S, r] = one('11123', '14567', '1', '1');
  check(names(r) === 'set,open,clear,turn' && r.ev[1].res === 'clash' && S.p[0].wins === 0 && S.p[1].wins === 0, '1 と 1 → かぶり（どちらも 負け：逆転勝利は 使えない）');
  [S, r] = one('22234', 'm4567', '2', 'm');
  check(names(r) === 'set,open,clear,turn,pre' && r.ev[1].res === 1 && r.ev[1].rev === undefined, '2（3まい）と 幻の馬 → 聞かれない（2 の 効果は 1 に だけ）');
  [S, r] = one('22234', 'k4567', '2', 'k');
  check(r.ev[1].rev === undefined && S.p[1].wins === 1, '2（3まい）と 神様馬 → 聞かれない');
  [S, r] = one('33345', '24567', '3', '2');
  check(names(r) === 'set,open,clear,turn' && r.ev[1].rev === undefined, '3 が 3まい あっても 逆転勝利は ない（1 と 2 だけ）');
  [S, r] = one('11123', 'm4567', '2', 'm');
  check(r.ev[1].rev === undefined && S.p[1].wins === 1, '手札に 1 が 3まい あっても、場に 出したのが 1 で なければ 聞かれない');
  // 捨てた あとの 手札が のこりの ターンの 数より 少なく なる とき（5 と 同じ 考え方）：5ターンで 手札 5まい ＝ よぶんが ない
  [S, r] = one('11123', 'm4567', '1', 'm', 5);
  check(S.turns === 5 && names(r) === 'set,open,clear,turn,pre' && r.ev[1].rev === undefined && S.p[1].wins === 1 && S.p[0].hand.length === 4,
    '捨てると のこりの ターンに 出す カードが 足りなく なる とき（5ターン・手札 5まい：セットの あと 4まい・のこり 4ターン）→ 聞かれない');
  // さいごの ターン：手札が 1 の 2まい だけ でも 使える
  const L = no6(G('11123', '6677m')); set(L, 0, '2'); set(L, 1, '6'); set(L, 0, '3'); set(L, 1, '7'); set(L, 0, '1'); const rl = set(L, 1, 'm');      // 相手は 4・5 を 出さない（4・5 を セットすると 効果タイムに なる）
  check(L.turn === 3 && L.phase === 'rev' && ks(L.p[0].hand) === '11' && names(rl) === 'set,open', 'さいごの ターン：手札が 1 の 2まい だけ → 聞かれる');
  const rl2 = R.act(L, 0, { t: 'rev', use: true });
  check(names(rl2) === 'rev,fin,clear,end' && L.phase === 'end' && L.res === 0 && L.p[0].wins === 3 && L.p[1].wins === 0 && ks(L.p[0].hand) === '1' && rl2.ev[3].wins.join() === '3,0' && sane(L), '使う → さいごの ターンも 勝ち → 3勝 0勝で おわり');
  const L2 = no6(G('11123', '6677m')); set(L2, 0, '2'); set(L2, 1, '6'); set(L2, 0, '3'); set(L2, 1, '7'); set(L2, 0, '1'); set(L2, 1, 'm'); const rl3 = R.act(L2, 0, { t: 'rev', use: false });
  check(names(rl3) === 'revskip,fin,clear,end' && L2.res === 0 && L2.p[0].wins === 2 && L2.p[1].wins === 1 && R.act(L2, 0, { t: 'rev', use: true }).why === 'end', '使わない → 2勝 1勝で おわり（さいごの ターンなので 幻の馬の 効果は 出ない）・おわった あとは 打てない');
}

console.log('■ 逆転勝利：見せる カード・ほかの 効果との 組み合わせ');
{
  // もう 相手に 知られて いる 1 から 見せる（新しく 知られる カードを 少なく）
  const S = G('11112', 'm4567'); set(S, 0, '1'); const h = S.p[0].hand.filter(c => c.k === '1'); S.p[1].known.push(h[2].u); set(S, 1, 'm');
  const r = R.act(S, 0, { t: 'rev', use: true }), x = r.ev[0];
  check(S.p[0].hand.filter(c => c.k === '1').length === 2 && x.show[0] === h[2].u && x.drop.u === h[2].u && x.show[1] === h[0].u && S.p[1].known.join() === String(h[0].u) && R.view(S, 1).op.hand.filter(c => c.k).length === 1,
    '手札に 1 が 3まい（1まいは もう 知られて いる）→ 知られて いる 1 と もう 1まいを 見せて、知られて いる 方を 捨てる ＝ 知られた カードは 1まいの まま（のこりの 1まいは 知られない）');
  // 5 の 効果で 山札から 来た 1 でも 使える
  const F = G('51123', 'm4567', '1'); set(F, 0, '5'); set(F, 1, 'm'); const rf = eff(F, 0, { u5: U(F, 0, '2') });
  check(names(rf) === 'effd,u5,open' && F.phase === 'rev' && F.pend.who === 0 && ks(F.p[0].hand) === '113' && R.view(F, 0).my.set.k === '1', '5 の 効果で 山札から 来た カードが 1（手札に 1 が 2まい）→ オープンして 聞かれる');
  R.act(F, 0, { t: 'rev', use: true });
  check(F.p[0].wins === 1 && ks(F.p[0].hand) === '13' && F.discard.map(d => d.k + d.why).join() === '55,25,11,1t,mt' && F.turn === 2 && sane(F), '使う → 勝ち（捨て札：5 の 効果の 5・2 ／ 逆転勝利の 1 ／ 出した 1・幻の馬）');
  // 4 の 効果で 交換して 出した 1 でも 使える
  const W = G('31112', 'm4567'); set(W, 0, '3'); set(W, 1, '4'); eff(W, 1, { u4: true }); const rw = R.act(W, 0, { t: 'swap', u: U(W, 0, '1') });
  check(names(rw) === 'swap,open,clear,turn' && rw.ev[1].res === 0, '（4 の 効果で 交換して 1 を 出した：1 と 4 → ふつうに 勝ち）');
  // 逆転勝利の あと：6 の 効果（まだ 見て いない カード だけ）と 合う ＝ 見せて のこった 1 は「もう 見た カード」
  const X = no6(G('11167', '66m45')); set(X, 0, '1'); set(X, 1, 'm'); R.act(X, 0, { t: 'rev', use: true });
  const kept = X.p[0].hand.find(c => c.k === '1');
  check(X.turn === 2 && ks(X.p[0].hand) === '167' && X.p[1].known.indexOf(kept.u) >= 0, '（1 の 逆転勝利を 使った：手札 1・6・7、1 は 相手に 知られて いる）');
  check(X.phase === 'six' && X.p[1].six.can === true && p6(X, 1, kept.u).why === 'pick' && p6(X, 1, U(X, 0, '6')).ok, '相手の 6 の 効果（2ターン目の はじめ）：逆転勝利で 見せた 1 は もう 見た カード なので えらべない');
  // 部屋：見せて いい 形（相手の 手札の 中身は 渡さない）
  const V = G('11123', 'm4567'); set(V, 0, '1'); set(V, 1, 'm');
  const txt = JSON.stringify(R.view(V, 1));
  check(R.view(V, 1).op.hand.every(c => c.k === null) && !/"known"|"res":1|"who"/.test(txt) && JSON.stringify(R.view(V, 0).pend) === '{"type":"rev","mine":true}', '聞かれて いる あいだ：相手に 渡す 形に 手札の 中身・中の 数字は 入らない');
}

console.log('■ 逆転勝利：本番の 形（5ターン・手札 7まい）');
{
  const S = R.newGame(rngOf(7), { hands: [['1', '1', '1', '1', '2', '3', '4'], ['m', 'k', '2', '3', '4', '5', '6']] });
  set(S, 0, '1'); const r = set(S, 1, 'm');
  check(S.turns === 5 && S.phase === 'rev' && S.p[0].hand.length === 6 && names(r) === 'set,open', '1ターン目：1（手札に 1 が あと 3まい）と 幻の馬 → 聞かれる');
  R.act(S, 0, { t: 'rev', use: true });
  check(S.p[0].wins === 1 && S.turn === 2 && ks(S.p[0].hand) === '11234' && S.p[0].hand.length - 1 >= S.turns - S.turn, '使う → 勝ち・手札 5まい（1 が 2まい のこる）');
  set(S, 0, '1'); const r2 = set(S, 1, 'k');
  check(names(r2) === 'set,open,clear,turn,pre' && r2.ev[1].res === 1 && S.p[1].wins === 1 && S.pend.type === 'k', '2ターン目：1（手札に 1 が あと 1まい＝合わせて 2まい）と 神様馬 → もう 聞かれない（1 は 4まい：逆転勝利は 1回の 対戦で 1回 だけ）');
  R.act(S, 1, { t: 'k', pick: null });
  // よぶんの 2まいを 5 の 効果で 使い切った あとは 使えない
  const T = R.newGame(rngOf(7), { hands: [['5', '5', '2', '2', '2', '6', '7'], ['1', '1', '3', '3', '4', '4', '6']], deck: ['7', '7'] });
  set(T, 0, '5'); set(T, 1, '3'); eff(T, 0, { u5: U(T, 0, '6') }); set(T, 0, '5'); set(T, 1, '3'); eff(T, 0, { u5: U(T, 0, '7') });
  check(T.turn === 3 && ks(T.p[0].hand) === '222' && T.p[0].hand.length === T.turns - T.turn + 1, '（5 の 効果を 2回 使った：3ターン目の はじめに 手札 3まい＝のこりの ターンと 同じ 数）');
  set(T, 0, '2'); const rt = set(T, 1, '1');
  check(names(rt) === 'set,open,clear,turn' && rt.ev[1].rev === undefined && T.p[1].wins >= 1 && ks(T.p[0].hand) === '22', '2（手札に 2 が 2まい）と 1 でも、捨てると 足りなく なる → 聞かれない（負け）');
}

console.log('■ 逆転勝利：5 の 効果で 入れ替わった カードでも（第4.188版の 確かめ・まさちゃん 11/17 11:05「1と2の効果は、5の効果でカードが入れ替わった際もオープンしたあとに使用できるようになってる？」）');
{
  for (const top of ['k', 'm']) {      // 相手の 5 の 効果 → 山札の 神様馬（幻の馬）が 場に
    const S = G('11123', '54672', top); set(S, 0, '1'); set(S, 1, '5'); const r = eff(S, 1, { u5: U(S, 1, '7') }), op = r.ev.find(e => e.e === 'open');
    check(names(r) === 'effd,u5,open' && op.c[1].k === top && op.res === 1 && op.rev === 0 && S.phase === 'rev' && S.pend.who === 0 && R.view(S, 0).pend.type === 'rev',
      `相手の 5 の 効果 → 山札の ${top === 'k' ? '神様馬' : '幻の馬'}が 場に → オープン：1 は 負け …だけど 1 の 逆転勝利を 聞かれる`);
    const rr = R.act(S, 0, { t: 'rev', use: true });
    check(rr.ok && names(rr).startsWith('rev,fin') && rr.ev[0].k === '1' && rr.ev[0].beat === top && rr.ev[0].show.length === 2 && S.p[0].wins === 1 && S.p[1].wins === 0 && ks(S.p[0].hand) === '123' && S.discard.some(d => d.k === '1' && d.why === '1') && sane(S),
      `使う：場の 1 ＋ 手札の 1 を 2まい 見せて、手札の 1 を 1まい 捨てる → ${top === 'k' ? '神様馬' : '幻の馬'}に 大逆転（勝ちは 自分）`);
  }
  const T = G('22234', '54673', '1'); set(T, 0, '2'); set(T, 1, '5'); const rt = eff(T, 1, { u5: U(T, 1, '7') });
  check(T.phase === 'rev' && rt.ev.find(e => e.e === 'open').c[1].k === '1' && R.act(T, 0, { t: 'rev', use: true }).ok && T.p[0].wins === 1 && T.p[1].wins === 0, '2 は 1 に 対して 同じ（相手の 5 の 効果で 山札の 1 が 出ても、2 の 逆転勝利で 勝ち）');
  const Y = G('51123', 'k4672', '1'); set(Y, 0, '5'); set(Y, 1, 'k'); const ry = eff(Y, 0, { u5: U(Y, 0, '3') });
  check(Y.phase === 'rev' && Y.pend.who === 0 && ry.ev.find(e => e.e === 'open').c[0].k === '1' && R.act(Y, 0, { t: 'rev', use: true }).ok && Y.p[0].wins === 1, '自分の 5 の 効果で 山札から 1 が 来て、相手の 神様馬に 負けた ときも 使える');
  const W = G('11123', '46572'); set(W, 0, '3'); set(W, 1, '4'); const rw = eff(W, 1, { u4: true });
  R.act(W, 0, { t: 'swap', u: U(W, 0, '1') });
  check(names(rw) === 'effd,first' && W.last.c.join() === '1,4' && W.phase === 'set' && W.p[0].wins === 1, '（4 の 効果の 交換で 出した 1 も ふつうに 勝負：4 に 勝つ）');
}

console.log('■ 効果の 順番（第4.188版・まさちゃん 11:05・11:16「4は効果発動最後にして！」／第4.190版・17:14「効果はそれぞれの一つ一つ終わってから効果の選択するようにして！…優先順位が高いのは6の効果だよ！」）');
{
  // 席 0：6 が 2まい・3 が 3まい・4 を セット ／ 席 1：7 が 3まい・5 を セット → ターンの はじめ 6 → セット → 7 → 3 → 5 → 4（1つずつ）
  const S = G('4663337', '5777121');
  check(S.phase === 'six' && R.view(S, 0).can.six && R.view(S, 1).can.six === null, '① ターンの はじめ：6（席 0）');
  const r0 = p6(S, 0, U(S, 1, '2')); set(S, 0, '4'); const r1 = set(S, 1, '5');
  check(names(r0) === 'sixd,p6' && names(r1) === 'set,efft' && S.step === 'x7' && R.view(S, 1).can.eff.e7 && R.view(S, 0).can.eff === null, '② セット → ③ 効果タイム：7（席 1）から');
  const r2 = eff(S, 1, { x7: true });
  check(names(r2) === 'effd,x7,efft' && S.step === 'x3' && R.view(S, 0).can.eff.e3, '7 を 行う → 3（席 0）');
  const r3 = eff(S, 0, { x3: true }, rngOf(3)), x3 = r3.ev[1];
  check(names(r3) === 'effd,x3,efft' && S.step === 'u5' && R.view(S, 1).can.eff.e5 && S.p[1].hand.some(c => c.u === x3.give.u), '3 を 行う（7 で 引いた あとの 手札から くじ）→ 5（席 1）');
  const r4 = eff(S, 1, { u5: x3.give.u });
  check(names(r4) === 'effd,u5,efft' && S.step === 'u4' && R.view(S, 0).can.eff.e4, '5 を 行う（3 で もらった 3 を 捨てる）→ 4（席 0：いちばん あと）');
  const r5 = eff(S, 0, { u4: true });
  check(names(r5) === 'effd,first' && S.phase === 'swap' && S.pend.who === 1 && S.p[1].set.blind === true && sane(S), '4 を 行う：席 1 は 5 の 効果で 山札から ふせた カードを、4 の 効果で 交換する 番');
  // 4 が なければ 5 は いちばん あと
  const B = G('5663337', '4777121'); p6(B, 0, U(B, 1, '2')); set(B, 0, '5'); set(B, 1, '4');
  eff(B, 1, { x7: true }); eff(B, 0, { x3: true }, rngOf(4)); const rb5 = eff(B, 0, { u5: U(B, 0, '7') });
  check(names(rb5) === 'effd,u5,efft' && B.step === 'u4' && R.view(B, 1).can.eff.e4, '6 → 7 → 3 → 5 → 4：5 を 行って から 4（席 1）');
  const rb = eff(B, 1, null);
  check(names(rb).startsWith('effd,open') && sane(B), '4 を 使わない → オープン');
  // 神様馬・幻の馬の 効果は ターンの はじめ：セットより 前（6 が ある ときは 6 の あと：上の「■ 6」）
  const K = G('k1234', '12345'); set(K, 0, 'k'); set(K, 1, '1');
  check(K.turn === 2 && K.phase === 'pre' && !R.view(K, 0).can.set && !R.view(K, 1).can.set && R.view(K, 0).pend.type === 'k', '神様馬で 勝った 次の ターン：まず 神様馬の 効果。決める まで 2人とも セットできない');
}

console.log('■ 7 の 4まい 公開：強さ 逆転（第4.185版・まさちゃん 22:39「7は、手札に7が4枚ある場合、4枚公開し内1枚を捨てると、数字の強さ順が逆転する」・22:45「1.その試合は終わるまで」／第4.187版・11/17 09:39「手札に7が4枚ある段階で発動できる…フィールドセット必要ないからね！」＝セットの 前）');
{
  // 席 0：7 が 4まい ＋ 1。セットの 前に 4まい 公開 → 1まい 捨てる → 逆転 → 1 を セット ／ 席 1：2 を セット。この ターンの オープンから 2 が 1 に 勝つ
  const S = G('77771', '23456', '345');
  const v0 = R.view(S, 0), v1 = R.view(S, 1);
  check(S.phase === 'set' && v0.can.x7r === true && v0.can.set === true && v1.can.x7r === false && R.legal(S, 0).join() === 'set,x7r' && R.legal(S, 1).join() === 'set' && v0.rv === false,
    '第4.187版：7 が 4まい → ターンの はじめ（セットの 前）に「4まい 公開で 逆転」を 使える・セットは いらない（相手は 使えない）');
  const sev = S.p[0].hand.filter(c => c.k === '7').map(c => c.u);
  const r = R.act(S, 0, { t: 'x7r' }), x = r.ev[0];
  check(r.ok && names(r) === 'x7r' && x.who === 0 && JSON.stringify(x.show) === JSON.stringify(sev) && x.drop.k === '7' && x.drop.u === sev[0] && S.rv === true && S.phase === 'set' && !S.p[0].set && !S.p[1].set
    && ks(S.p[0].hand) === '7771' && S.discard.some(d => d.u === sev[0] && d.why === '7' && d.by === 0 && d.turn === 1) && sane(S),
    '「4まい 公開」→ 7 を 4まい 見せて 1まい 捨てる（捨て札の 理由 7）→ すぐ 強さ 逆転・セットは まだ（この あと いつもの ように セット）');
  const w1 = R.view(S, 1), w0 = R.view(S, 0), e1 = R.evFor(r.ev, 1)[0];
  check(w1.rv === true && w0.rv === true && w1.op.hand.filter(c => c.k === '7').length === 3 && w0.my.hand.filter(c => c.seen).length === 3 && e1.e === 'x7r' && e1.me === false && e1.show.length === 4 && e1.drop.k === '7'
    && w0.can.x7r === false && w0.can.set === true && R.act(S, 0, { t: 'x7r' }).why === 'x7r',
    '2人とも 逆転ちゅう（view.rv）・手札に のこった 7 の 3まいは 相手に 知られた カード・できごと x7r は 相手にも 見える・2回目は 使えない');
  set(S, 0, '1'); const ro = set(S, 1, '2'), op = ro.ev.find(e => e.e === 'open');
  check(names(ro) === 'set,open,clear,turn' && op.res === 1 && S.p[1].wins === 1, 'その ターンの オープンから 逆：1 は 2 に 負ける（強さ 逆転）・7 が 3まい のこって いても、この ターンの 効果タイムに 3まい 交換は 出ない（どちらか 1つ）');
  // 2ターン目：7 が 1番 強い 数字 ／ 3ターン目まで ずっと 逆
  check(R.view(S, 0).can.x7r === false, '2ターン目：もう 逆転ちゅう なので 4まい 公開は 出ない');
  set(S, 0, '7'); set(S, 1, '3');
  check(S.turn === 3 && S.p[0].wins === 1 && S.rv === true && S.last.res === 0, '2ターン目：7 は 3 に 勝つ（逆転は その 対戦が 終わる まで）');
  set(S, 0, '7'); set(S, 1, '6');
  check(S.phase === 'end' && S.p[0].wins === 2 && S.res === 0, '3ターン目も 逆：7 は 6 に 勝つ → 2勝 1敗');
  // のこった 7 を セットしても いい（4まい 見せて から 7 を 出す）・相手が 先に セットして いても、自分が セットする 前なら 使える
  const A = G('77771', '23456', '345'); set(A, 1, '2');
  const ra = R.act(A, 0, { t: 'x7r' }); set(A, 0, '7');
  check(ra.ok && A.rv === true && A.last.res === 0 && A.last.c.join() === '7,2', '相手が 先に セットして いても 使える・のこった 7 を セット → 逆転ちゅうの 7 は 2 に 勝つ');
  // 神様馬・幻の馬は 逆転ちゅうも いちばん 強い
  const K = G('7777k', '1123m', '345');
  R.act(K, 0, { t: 'x7r' }); set(K, 0, 'k'); set(K, 1, '1');
  check(K.rv === true && K.p[0].wins === 1 && K.turn === 2 && K.phase === 'pre', '逆転ちゅうも 神様馬は 数字に 勝つ');
  R.act(K, 0, { t: 'k', pick: null }); set(K, 0, '7'); set(K, 1, 'm');
  check(K.p[1].wins === 1 && K.last.res === 1, '逆転ちゅうも 幻の馬は 7 に 勝つ（数字 だけ 逆）');
}
{
  // 使えない とき：7 が 3まい・もう セットした・もう 逆転ちゅう・捨てると 手札が 足りなく なる・セットの とき で ない／効果タイムでは 使えない
  const A = G('77712', '23456', '345');
  check(R.view(A, 0).can.x7r === false && R.act(A, 0, { t: 'x7r' }).why === 'x7r', '7 が 3まい では 逆転は 使えない');
  const B = G('77771', '23456', '345'); set(B, 0, '1');
  check(R.view(B, 0).can.x7r === false && R.act(B, 0, { t: 'x7r' }).why === 'x7r' && B.rv === false, 'セットした あとは 使えない（使うのは セットの 前）');
  const C3 = G('77771', '23456', '345'); C3.rv = true;
  check(R.view(C3, 0).can.x7r === false && R.act(C3, 0, { t: 'x7r' }).why === 'x7r', 'もう 逆転ちゅう なら 使えない');
  const D4 = G('7777', '1234', '', 4), D3 = G('7777', '1234', '', 3);
  check(R.view(D4, 0).can.x7r === false && R.view(D3, 0).can.x7r === true, '1まい 捨てると のこりの ターンに 出す カードが 足りなく なる ときは 使えない（手札 4まい・4ターン → だめ／3ターン → 使える）');
  const E = G('77771', '23456', '345'); set(E, 0, '1'); set(E, 1, '2');
  const re = eff(E, 0, { x7r: true });
  check(E.phase === 'eff' && !('e7r' in R.view(E, 0).can.eff) && R.view(E, 0).can.eff.e7 === true && R.view(E, 0).can.x7r === false && !re.ok && re.why === 'e7r' && E.rv === false,
    '効果タイムでは もう 聞かない・使えない（7 が 4まい あっても 3まい 交換 だけ）');
  const P = G('7777k', '1234m', '345'); set(P, 0, 'k'); set(P, 1, '1'); eff(P, 0, null);      // 効果タイム（7 の 3まい 交換）は 使わない → 神様馬の 勝ち
  check(P.phase === 'pre' && R.view(P, 0).can.x7r === false && R.view(P, 1).can.x7r === false && R.act(P, 0, { t: 'x7r' }).why === 'x7r', '神様馬の 効果を 聞かれて いる あいだ（ターンの はじめ）は まだ 使えない（その あと セットの とき）');
  R.act(P, 0, { t: 'k', pick: null });
  check(P.phase === 'set' && R.view(P, 0).can.x7r === true, '（神様馬の 効果を 決めたら 使える）');
  // 次の ターンは 3まい 交換が 出る（7 が 3まい ある とき）
  const X = G('7777612', '23456', '', 3); R.act(X, 0, { t: 'x7r' }); set(X, 0, '6'); const rx = set(X, 1, '2');
  check(names(rx) === 'set,open,clear,turn' && X.p[0].r7 === 1, '4まい 公開を 使った ターンは、7 が 3まい あっても 3まい 交換は 出ない');
  set(X, 0, '1'); set(X, 1, '3');
  check(X.turn === 2 && X.phase === 'eff' && R.view(X, 0).can.eff.e7 === true, '次の ターンは 3まい 交換が 出る（7 が 3まい ある とき）');
}
{
  // 逆転勝利（1・2）は いつもの 条件：逆転ちゅうは 2 が 1 に 勝つ ので 2 の 逆転勝利は 出ない
  const S = G('77773', '22213', '3456'); R.act(S, 0, { t: 'x7r' }); set(S, 0, '3'); set(S, 1, '1');
  check(S.rv === true && S.p[0].wins === 1 && S.phase === 'set' && S.turn === 2, '逆転ちゅう：3 が 1 に 勝つ（1 の 逆転勝利は 神様馬・幻の馬に 負けた とき だけ ＝ 聞かれない）');
  set(S, 0, '7'); set(S, 1, '2');
  check(S.p[0].wins === 2 && S.phase !== 'rev', '逆転ちゅう：7 が 2 に 勝つ（逆転勝利は 出ない）');
}
{
  // コンピュータ：7 が 4まい → いつも セットの 前に 逆転・逆転ちゅうは 7 の 交換を しない・強い 7 を 出す
  const S = G('77771', '23456', '3456');
  const a = C.decide(R.view(S, 0), rngOf(1));
  check(a && a.t === 'x7r' && R.act(S, 0, a, rngOf(2)).ok && S.rv === true, 'コンピュータ：7 が 4まい → セットの 前に 4まい 公開で 逆転');
  const b = C.decide(R.view(S, 0), rngOf(3));
  check(S.rv === true && b && b.t === 'set' && S.p[0].hand.find(c => c.u === b.u).k === '7', 'コンピュータ：その あと セット。逆転ちゅうは 7 が 強い カード（のこりの ターンの 分の 強い 方から 出す）');
  const T = G('77712', '23456', '345'); T.rv = true; set(T, 0, '1'); set(T, 1, '2');
  const c3 = T.phase === 'eff' ? C.decide(R.view(T, 0), rngOf(4)) : null;
  check(T.phase === 'eff' && c3 && !c3.use.x7, 'コンピュータ：逆転ちゅうに 7 が 3まい あっても 交換しない（7 は 強い）');
}

console.log('■ セットは いつも ふせて（第4.187版・まさちゃん 09:39「4も5もフィールドセットの段階では裏面でカードをフィールドにセットだけど、合ってるかな？」）');
{
  // 席 1 が 7 を 4まい 見せた（のこりの 7 の 3まいは 席 0 が 知って いる）→ 7 を セットしても、ほかを セットしても、席 0 に 見える 形は 同じ
  const mk = () => { const S = G('12345', '777712', '', 3); R.act(S, 1, { t: 'x7r' }); return S; };      // 第4.190版：6 は ターンの はじめ なので、ここでは 6 を 持たない
  const A = mk(), B = mk(), kp = v => v.op.hand.map(c => c.k).join(',');
  const before = kp(R.view(A, 0));
  set(A, 1, '7'); set(B, 1, '1');
  const va = R.view(A, 0), vb = R.view(B, 0);
  const real = (S, v) => v.op.hand.filter(c => c.k === null).every(c => S.p[1].hand.some(h => h.u === c.u && S.p[0].known.indexOf(h.u) < 0));
  check(before === '7,7,7,,' && va.op.set.k === null && vb.op.set.k === null && kp(va) === '7,7,7,' && kp(vb) === kp(va) && va.op.hand.length === 4 && real(A, va) && real(B, vb),
    '相手が 見た カード（7）を セットしても、ほかの カードを セットしても、場の カードは うら・手札の 見え方も 同じ（7 が 3まい ＋ うら 1まい：どれを 出したか わからない）');
  check(va.op.set.up === false && R.view(A, 1).my.set.k === '7' && R.view(B, 1).my.set.k === '1', '自分の 場の カードは 自分には 何か わかる（ふせて いても）');
  const ra = set(A, 0, '3'), rb = set(B, 0, '3');
  const oa = ra.ev.find(e => e.e === 'open'), ob = rb.ev.find(e => e.e === 'open');
  check(oa.c[1].k === '7' && ob.c[1].k === '1' && kp(R.view(A, 0)).split(',').filter(k => k === '7').length === 2 && kp(R.view(B, 0)).split(',').filter(k => k === '7').length === 3,
    'オープンしたら ほんとうの 形に もどる（7 を 出した 方は 手札の 7 が 2まい）');
  // 第4.190版：6 の 効果は ターンの はじめ（だれも セットして いない）＝ 見える 手札は ほんとうの 手札・6 を 決める まで 7 の 4まい 公開も まだ
  const H = G('66345', '777712', '', 3);
  check(H.phase === 'six' && R.view(H, 0).op.hand.map(c => c.u).join() === H.p[1].hand.map(c => c.u).join() && R.view(H, 1).can.x7r === false && R.act(H, 1, { t: 'x7r' }).why === 'x7r', '6 の 効果を えらぶ ときは、相手の 手札は ほんとうの 手札（セットは まだ）・相手の 7 の 4まい 公開は その あと');
  const rh = p6(H, 0, R.view(H, 0).op.hand[5].u);
  check(rh.ok && rh.ev[1].k === '2' && H.phase === 'set' && R.view(H, 1).can.x7r === true, '6 を 決めたら セット（7 の 4まい 公開も 使える）');
  // ぜんぶ 見た 手札でも 同じ
  const mk2 = () => { const S = G('12345', '77771', '', 3); R.act(S, 1, { t: 'x7r' }); S.p[0].known.push(U(S, 1, '1')); return S; };
  const C2 = mk2(), D2 = mk2(); set(C2, 1, '1'); set(D2, 1, '7');
  check(kp(R.view(C2, 0)) === '7,7,7' && kp(R.view(D2, 0)) === '7,7,7' && R.view(C2, 0).op.set.k === null && R.view(D2, 0).op.set.k === null, '相手の 手札を ぜんぶ 知って いても、どれを セットしたかは わからない（見え方は 同じ）');
  // 4 の 効果で 見せたら 表・5 の 効果で 山札から 来た カードは だれにも うら
  const F = G('41235', '12345'); set(F, 0, '4'); set(F, 1, '5');
  check(R.view(F, 1).op.set.k === null && R.view(F, 0).op.set.k === null, '4 も 5 も ふせて セット（相手には うら）');
  eff(F, 1, null); eff(F, 0, { u4: true });      // 第4.190版：5（席 1）→ 4（席 0）の 1つずつ
  check(F.phase === 'swap' && R.view(F, 1).op.set.k === '4' && R.view(F, 1).op.set.up === true, '4 の 効果を 使ったら 4 は 表（最初に 公開）');
}

console.log('■ まちがった 手は 受けつけない');
{
  const S = G('12367', '12367');
  check(R.act(S, 2, { t: 'set', u: 1 }).why === 'arg' && R.act(S, 0, null).why === 'arg' && R.act(S, 0, { t: 'zzz' }).why === 'type' && R.act(S, 0, { t: 'set', u: U(S, 1, '1') }).why === 'card'
    && R.act(S, 0, { t: 'swap', u: U(S, 0, '1') }).why === 'swap' && R.act(S, 0, { t: 'k', pick: null }).why === 'k' && R.act(S, 0, { t: 'm', drop: null }).why === 'm' && R.act(S, 0, { t: 'eff', use: { x7: true } }).why === 'eff' && R.act(S, 0, { t: 'rev', use: true }).why === 'rev' && R.act(S, 0, { t: 'p6', pick: null }).why === 'p6',
    '知らない 手・相手の カード・番で ない 手は ぜんぶ 受けつけない（中身は かわらない）');
  check(ks(S.p[0].hand) === '12367' && ks(S.p[1].hand) === '12367' && S.deck.length === 20 && sane(S), '受けつけなかった あとも カードは そのまま');
}

// でたらめに えらぶ「使う 効果」（第4.190版：いまの 効果 1つ＝view.can.eff.st）。7 割で 使う
function rndUse(v, rng) {
  const c = v.can.eff, h = v.my.hand, rc = a => a[Math.floor(rng() * a.length)];
  if (rng() >= 0.7) return {};
  if (c.e7) return { x7: true };                     // 第4.187版：4まい 公開は セットの 前（手 x7r）
  if (c.e3) return { x3: true };
  if (c.e5) return h.length ? { u5: rc(h).u } : {};
  if (c.e4) return { u4: true };
  return {};
}
// でたらめに えらぶ 6 の 効果（第4.190版：ターンの はじめ）：まだ 見て いない カードから・3 割は 使わない
const rndSix = (v, rng) => { const un = v.op.hand.filter(x => x.k == null); return { t: 'p6', pick: rng() < 0.3 || !un.length ? null : un[Math.floor(rng() * un.length)].u }; };

console.log('■ でたらめに 2万回 あそぶ（どんな 手の 順でも こわれない）');
{
  const rng = rngOf(20261115); let bad = 0, n = 0, st = { ask5: 0, u5skip: 0, u5sw: 0, rev: 0, revskip: 0, revk: { 1: 0, 2: 0 }, revbeat: { k: 0, m: 0, 1: 0 }, fin: 0, revq: 0, efft: 0, x7: 0, p6: 0, p6skip: 0, sixt: 0, six1: 0, six6bad: 0, fz55: 0, u5: 0, x3: 0, both57: 0, both53: 0, u5t: [0, 0, 0, 0, 0, 0], x3t: [0, 0, 0, 0, 0, 0], u5n: [0, 0, 0, 0], no6: 0, no6h: 0, hid: 0, x7r: 0, fz4: 0, fz53: 0, fzx: 0, ordbad: 0, nok: 0, first: 0, first2: 0, d4: 0, d4bad: 0, swap: 0, pre: 0, k: 0, m: 0, fizz: 0, clash: 0, tie: 0, win0: 0, win1: 0, draw: 0 };
  for (let g = 0; g < 20000; g++) {
    const S = R.newGame(rng); let guard = 0;
    if (S.ev0.some(e => e.e === 'sixt') !== (S.phase === 'six')) bad++; if (S.phase === 'six') st.six1++;      // 第4.190版：1ターン目の はじめの 6
    while (S.phase !== 'end' && guard++ < 200) {
      const L0 = R.legal(S, 0), L1 = R.legal(S, 1);
      if (!L0.length && !L1.length) { bad++; break; }      // だれも 打てない ＝ 止まった
      const i = rng() < 0.5 ? 0 : 1, L = i === 0 ? L0 : L1; if (!L.length) continue;
      const t = L[Math.floor(rng() * L.length)], P = S.p[i], Q = S.p[1 - i]; let a;
      const rc = h => h[Math.floor(rng() * h.length)];
      if (t === 'set') a = { t: 'set', u: rc(P.hand).u };
      else if (t === 'x7r') { if (S.phase !== 'set' || P.set || S.rv || P.hand.filter(c => c.k === '7').length < 4) { bad++; break; } a = { t: 'x7r' }; st.x7r++; }      // 第4.187版：セットの 前
      else if (t === 'eff') a = { t: 'eff', use: rndUse(R.view(S, i), rng) };
      else if (t === 'p6') { if (S.phase !== 'six' || !P.six || !P.six.can || !Q.hand.some(c => P.known.indexOf(c.u) < 0)) { bad++; break; } a = rndSix(R.view(S, i), rng); }      // 第4.190版：ターンの はじめ
      else if (t === 'swap') a = { t: 'swap', u: rc(P.hand).u };
      else if (t === 'u5') { if (!(P.set && P.set.c.k === '5' && P.hand.length - 1 >= R.TURNS - S.turn && S.deck.length >= 1)) { bad++; break; } a = { t: 'u5', drop: rng() < 0.3 ? null : rc(P.hand).u }; }      // 第4.183版：交換で 出した 5
      else if (t === 'k') { const un = Q.hand.filter(c => P.known.indexOf(c.u) < 0); if (!un.length) { bad++; break; } a = { t: 'k', pick: rng() < 0.2 ? null : rc(un).u }; }      // 聞かれた ＝ まだ 見て いない カードが ある
      else if (t === 'm') { const h = R.shuffle(P.hand.slice(), rng); a = { t: 'm', drop: rng() < 0.2 ? null : [h[0].u, h[1].u] }; }
      else if (t === 'rev') {      // 逆転勝利を 聞かれた ＝ 負けて いる・場が 1（相手 神様馬／幻の馬）か 2（相手 1）・手札に 同じ 数字が 2まい 以上・捨てても のこりの ターンに 足りる
        const mk = P.set.c.k, ok = Q.set.c.k;
        if (!((mk === '1' && (ok === 'k' || ok === 'm')) || (mk === '2' && ok === '1')) || P.hand.filter(c => c.k === mk).length < 2 || P.hand.length - 1 < R.TURNS - S.turn) { bad++; break; }
        a = { t: 'rev', use: rng() < 0.7 };
      }
      const before = S.p.map(X => X.set ? X.set.c.u : 0), ph = S.phase, tn = S.turn, w0 = [S.p[0].wins, S.p[1].wins], hn = P.hand.length;
      const u5b = [S.p[0].u5n || 0, S.p[1].u5n || 0];
      const r = R.act(S, i, a, rng);
      if (!r.ok) { bad++; break; }
      r.ev.forEach(e => { if (e.e === 'u5') S.p[e.who].u5n = (S.p[e.who].u5n || 0) + 1; });
      // 第4.190版：不発の わけ（2人とも 5 の 効果で 山札が 足りない・それ 以外は おかしい）と 効果の 順（ターンの はじめ 6 → 神様馬／幻の馬 → セット → 7 → 3 → 5 → 4：ターンを またいで しらべる）
      r.ev.forEach(e => { if (e.e !== 'fizz') return; if (e.k === '5' && S.deck.length === 0) st.fz55++; else st.fzx++; });
      { const RK = { p6: 0, p6skip: 0, k: 1, kskip: 1, m: 1, mskip: 1, set: 2, x7r: 2, x7: 3, x3: 4, u5: 5, first: 6, first2: 6 };
        for (const e of r.ev) { if (e.e === 'turn') { S._rk = -1; continue; } if (e.e === 'open') { S._rk = 9; continue; } if (!(e.e in RK) || (e.e === 'u5' && e.sw)) continue; if (RK[e.e] < (S._rk == null ? -1 : S._rk)) { st.ordbad++; bad++; } S._rk = RK[e.e]; } }
      // 7 → 5・3 → 5（同じ 人・同じ ターン：前の 効果の あとで 5 を 決めた）
      r.ev.forEach(e => { if (e.e === 'x7') S.p[e.who]._x7 = tn; if (e.e === 'x3') S.p[e.who]._x3 = tn; if (e.e === 'u5' && !e.sw) { if (S.p[e.who]._x7 === tn) st.both57++; if (S.p[e.who]._x3 === tn) st.both53++; } });
      // 第4.190版：ターンの はじめ：6 が 2まい ＆ 相手の 手札に まだ 見て いない カード ⇔ 6 の 効果を 聞かれる（sixt）
      if (r.ev.some(e => e.e === 'turn')) { const sx = r.ev.find(e => e.e === 'sixt'); [0, 1].forEach(j => { const Pj = S.p[j], Qj = S.p[1 - j], two = Pj.hand.filter(c => c.k === '6').length >= 2, can = two && Qj.hand.some(c => Pj.known.indexOf(c.u) < 0); if (two && !can) st.no6++; if (can !== !!(sx && sx.has[j])) { st.six6bad++; bad++; } }); }
      r.ev.forEach(e => { if (typeof st[e.e] === 'number') st[e.e]++; if (e.e === 'u5') st.u5t[tn]++; if (e.e === 'x3') st.x3t[tn]++; if (e.e === 'open') { if (e.res === 'clash') st.clash++; if (e.res === 'tie') st.tie++; if (e.rev != null) st.revq++; if (e.d4) { st.d4++; if (e.res !== 'tie' || e.c[0].k !== '4' || e.c[1].k !== '4' || e.rev != null) st.d4bad++; } }
        if (e.e === 'rev') { st.revk[e.k]++; st.revbeat[e.beat]++; } if (e.e === 'u5' && e.sw) st.u5sw++; });
      // 逆転勝利：使った → 聞かれた 人の 勝ち・手札が 1まい へる ／ 使わない → 相手の 勝ち・手札は そのまま（どちらも 勝ちは 1つ だけ ふえる）
      if (t === 'rev') { const dw = [S.p[0].wins - w0[0], S.p[1].wins - w0[1]]; if (dw[i] !== (a.use ? 1 : 0) || dw[1 - i] !== (a.use ? 0 : 1) || P.hand.length !== hn - (a.use ? 1 : 0)) { bad++; break; } }
      // 手札の 数：どの ターンの おわりにも、のこりの ターンで 出す 数 だけは ある（5 の 効果で 足りなく ならない）
      if (S.phase !== 'end' && S.p.some(X => X.hand.length + (X.set ? 1 : 0) < R.TURNS - S.turn + 1)) { bad++; break; }
      if (!sane(S)) { bad++; break; }
      // セットした カードが 変わるのは 5 の 効果・4 の 効果の 交換 だけ（セットの 番に 自分で 変える ことは ない）
      if (ph === 'set' && S.phase === 'set' && S.turn === tn && [0, 1].some(j => before[j] && (!S.p[j].set || S.p[j].set.c.u !== before[j]))) { bad++; break; }
      // 見せる ものに 相手の 知らない カードの 中身が 入って いない
      const v = R.view(S, 1 - i); if (v.op.hand.some(c => c.k !== null && S.p[1 - i].known.indexOf(c.u) < 0)) { bad++; break; }
      // 第4.187版：相手の 場の カードは 4 の 効果・オープン まで うら・見える 手札の 数は ほんとうの 数・うらの カードは いま 手札に ある まだ 見て いない カード
      for (const j of [0, 1]) { const w = R.view(S, j), Qj = S.p[1 - j], Pj = S.p[j]; if (Qj.set && !Qj.set.up && !Qj.set.open) { st.hid++; if (w.op.set.k !== null) { bad++; break; } } if (w.op.hand.length !== Qj.hand.length || w.op.hand.some(c => c.k === null && !Qj.hand.some(h => h.u === c.u && Pj.known.indexOf(h.u) < 0))) { bad++; break; } }
      if ((S.phase === 'pre') !== (!!S.pend && (S.pend.type === 'k' || S.pend.type === 'm')) || (S.phase === 'swap') !== (!!S.pend && S.pend.type === 'swap') || (S.phase === 'rev') !== (!!S.pend && S.pend.type === 'rev') || (S.phase === 'u5') !== (!!S.pend && S.pend.type === 'u5')) { bad++; break; }
      if ((S.phase === 'eff') !== (S.step != null) || (S.phase === 'six') !== !!(S.p[0].six || S.p[1].six)) { bad++; break; }      // 第4.190版：効果タイムは いまの 効果（step）が ある とき だけ・6 は ターンの はじめ だけ
    }
    if (S.phase !== 'end' || S.turn !== 5 || S.p[0].wins + S.p[1].wins > 5 || S.discard.length < 10 || S.discard.filter(d => d.why === 't').length !== 10) bad++;
    S.p.forEach(X => { st.u5n[Math.min(3, X.u5n || 0)]++; });
    st[S.res === 'draw' ? 'draw' : 'win' + S.res]++; n++;
  }
  check(bad === 0 && n === 20000, `2万回：ぜんぶ 5ターンで おわる・カードは いつも 30まい・打てる と 言った 手は ぜんぶ 通る・止まらない（おかしい ${bad}）`);
  check(st.efft > 5000 && st.x7 > 50 && st.p6 > 500 && st.p6skip > 100 && st.sixt > 1000 && st.six1 > 100 && st.six6bad === 0 && st.u5 > 1000 && st.x3 > 50 && st.both57 > 0 && st.both53 > 0 && st.first > 500 && st.first2 > 20 && st.d4 === st.first2 && st.d4bad === 0 && st.swap > 500 && st.pre > 2000 && st.k > 500 && st.m > 500 && st.clash > 2000 && st.tie > 3 && st.fzx === 0 && st.ordbad === 0,
    `効果も ぜんぶ 出た（効果タイムの 効果 ${st.efft}・7 ${st.x7}・6 ${st.p6}〈ターンの はじめに 聞いた ${st.sixt}・1ターン目 ${st.six1}・使わない ${st.p6skip}〉・5 ${st.u5}・3 ${st.x3}・7 の あとで 5 ${st.both57}・3 の あとで 5 ${st.both53}・4 ${st.first}・4 の 打ち消し ${st.first2}（→ ドロー ${st.d4}）・交換 ${st.swap}・神様馬 ${st.k}・幻の馬 ${st.m}・かぶり ${st.clash}・引き分け ${st.tie}・不発 ${st.fizz}〈2人とも 5 で 山札が 足りない ${st.fz55}・ほか ${st.fzx}〉・効果の 順〈6 → 神様馬／幻の馬 → セット → 7 → 3 → 5 → 4〉が ちがう ${st.ordbad}・6 の 聞き方が ちがう ${st.six6bad}）`);
  check(st.u5t.slice(1).every(q => q > 300) && st.x3t[1] > 20 && st.x3t[2] > 5 && st.x3t[5] === 0 && st.u5n[3] === 0 && st.u5n[2] > 100,
    `5 の 効果は どの ターンでも 出た（1〜5ターン目 ${st.u5t.slice(1).join('・')}）・1人が 1回の 対戦で 使った 回数は 2回 まで（0回 ${st.u5n[0]}・1回 ${st.u5n[1]}・2回 ${st.u5n[2]}・3回 ${st.u5n[3]}：手札 7まい・5ターン＝よぶんは 2まい）・`
    + `3 の 効果は 1〜4ターン目（${st.x3t.slice(1, 5).join('・')}：5ターン目は 手札が 2まい まで なので 出ない ${st.x3t[5]}）`);
  check(st.ask5 > 50 && st.u5sw + st.u5skip === st.ask5 && st.u5sw > 20 && st.u5skip > 5, `第4.183版：4 の 効果で 交換して 5 を 出した → 5 の 効果を 聞かれた ${st.ask5}回（使った ${st.u5sw}・使わない ${st.u5skip}）`);
  check(st.no6 > 0, `6 が 2まい あっても、相手の 手札が ぜんぶ もう 見た カードの ときは 6 の 効果を 聞かれない（ターンの はじめ ${st.no6}回）`);
  check(st.hid > 10000, `第4.187版：相手が ふせて いる あいだ、場の カードは いつも うら・見える 手札は ほんとうの 数（${st.hid}回 しらべた）・7 の 4まい 公開（セットの 前）${st.x7r}回`);
  check(Math.abs(st.win0 - st.win1) / n < 0.03, `どちらの 席も 同じ ぐらい 勝つ（${st.win0}・${st.win1}・同点 ${st.draw}）`);
  check(st.revq > 10 && st.revq === st.rev + st.revskip && st.fin === st.revq && st.rev > 5 && st.revskip > 1 && st.revk[1] + st.revk[2] === st.rev && st.revbeat.k + st.revbeat.m === st.revk[1] && st.revbeat[1] === st.revk[2],
    `逆転勝利も 出た（聞かれた ${st.revq}回＝使った ${st.rev}・使わない ${st.revskip}。1 の 効果 ${st.revk[1]}回〈神様馬に ${st.revbeat.k}・幻の馬に ${st.revbeat.m}〉・2 の 効果 ${st.revk[2]}回：ふつうに 配ると めったに 出ない）`);
}

console.log('■ でたらめに あそぶ：7 が 4まい ある 手札で 5000回（第4.185版：強さ 逆転が たくさん 出る 形・第4.187版：逆転は セットの 前）');
{
  const rng = rngOf(20261185); let bad = 0, n = 0; const st = { x7r: 0, x7: 0, rvopen: 0, open: 0, fizz: 0, both: 0 };
  for (let g = 0; g < 5000; g++) {
    const S = R.newGame(rng, { hands: [['7', '7', '7', '7', rng() < 0.5 ? '1' : '5', '2', '6'], ['k', 'm', '1', '2', '3', '4', '6']] }); let guard = 0;
    while (S.phase !== 'end' && guard++ < 200) {
      const L0 = R.legal(S, 0), L1 = R.legal(S, 1);
      if (!L0.length && !L1.length) { bad++; break; }
      const i = rng() < 0.5 ? 0 : 1, L = i === 0 ? L0 : L1; if (!L.length) continue;
      const t = L[Math.floor(rng() * L.length)], P = S.p[i], Q = S.p[1 - i], rc = h => h[Math.floor(rng() * h.length)]; let a;
      if (t === 'set') a = { t: 'set', u: rc(P.hand).u };
      else if (t === 'x7r') a = { t: 'x7r' };          // 第4.187版：セットの 前
      else if (t === 'eff') a = { t: 'eff', use: rndUse(R.view(S, i), rng) };
      else if (t === 'p6') a = rndSix(R.view(S, i), rng);      // 第4.190版
      else if (t === 'swap') a = { t: 'swap', u: rc(P.hand).u };
      else if (t === 'u5') a = { t: 'u5', drop: rng() < 0.3 ? null : rc(P.hand).u };
      else if (t === 'k') a = { t: 'k', pick: rng() < 0.3 ? null : rc(Q.hand.filter(c => P.known.indexOf(c.u) < 0)).u };
      else if (t === 'm') { const h = R.shuffle(P.hand.slice(), rng); a = { t: 'm', drop: rng() < 0.3 ? null : [h[0].u, h[1].u] }; }
      else if (t === 'rev') a = { t: 'rev', use: rng() < 0.75 };
      if (t === 'x7r' && (S.phase !== 'set' || P.set)) bad++;
      const rv0 = S.rv, r = R.act(S, i, a, rng);
      if (!r.ok || !sane(S)) { bad++; break; }
      let rvNow = rv0;
      r.ev.forEach(e => {
        if (e.e === 'x7r') { st.x7r++; if (rvNow || e.show.length !== 4 || e.drop.k !== '7' || t !== 'x7r') bad++; rvNow = true; }
        if (e.e === 'x7') st.x7++;
        if (e.e === 'fizz' && !(e.k === '5' && S.deck.length === 0)) st.fizz++;      // 第4.190版：2人とも 5 の 効果で 山札が 足りない ときの 不発は 数えない
        if (e.e === 'open' && !e.d4) { st.open++; if (rvNow) st.rvopen++; if (e.res !== R.compare(e.c[0].k, e.c[1].k, rvNow)) bad++; }
      });
      if (rv0 && !S.rv) bad++;                            // 逆転は もどらない（その 対戦が 終わる まで）
      if (S.rv !== rvNow) bad++;
      if (S.phase !== 'end' && S.p.some(X => X.hand.length + (X.set ? 1 : 0) < R.TURNS - S.turn + 1)) { bad++; break; }
      const v = R.view(S, 1 - i); if (v.op.hand.some(c => c.k !== null && S.p[1 - i].known.indexOf(c.u) < 0) || v.rv !== S.rv) { bad++; break; }
    }
    if (S.phase !== 'end' || S.turn !== 5 || S.discard.filter(d => d.why === 't').length !== 10 || S.discard.filter(d => d.why === '7').length > 1) bad++;
    n++;
  }
  check(bad === 0 && n === 5000 && st.x7r > 1000 && st.rvopen > 3000 && st.fizz === 0,
    `5000回：こわれない・逆転は 1回の 対戦で 1回 まで・いちど 逆に なったら さいごまで 逆・逆転ちゅうの オープンは ぜんぶ 逆の 強さで くらべた（逆転 ${st.x7r}回・逆の オープン ${st.rvopen}／${st.open}・3まい 交換 ${st.x7}・おかしい ${bad}）`);
}

console.log('■ でたらめに あそぶ：1・2 が そろいやすい 手札で 1万回（逆転勝利が たくさん 出る 形）');
{
  const rng = rngOf(20261116); let bad = 0, n = 0; const st = { q: 0, rev: 0, skip: 0, k1: 0, k2: 0, two: 0, pre: 0 };
  for (let g = 0; g < 10000; g++) {
    // 席 0：1 が 3まい・2 が 3まい ／ 席 1：神様馬・幻の馬・1・2（のこりは でたらめ）
    const S = R.newGame(rng, { hands: [['1', '1', '1', '2', '2', '2', rng() < 0.5 ? '3' : '7'], ['k', 'm', '1', '2', '4', '5', '6']] }); let guard = 0, revs = [0, 0];
    while (S.phase !== 'end' && guard++ < 200) {
      const L0 = R.legal(S, 0), L1 = R.legal(S, 1);
      if (!L0.length && !L1.length) { bad++; break; }
      const i = rng() < 0.5 ? 0 : 1, L = i === 0 ? L0 : L1; if (!L.length) continue;
      const t = L[Math.floor(rng() * L.length)], P = S.p[i], Q = S.p[1 - i], rc = h => h[Math.floor(rng() * h.length)]; let a;
      if (t === 'set') a = { t: 'set', u: rc(P.hand).u };
      else if (t === 'x7r') a = { t: 'x7r' };
      else if (t === 'eff') a = { t: 'eff', use: rndUse(R.view(S, i), rng) };
      else if (t === 'p6') a = rndSix(R.view(S, i), rng);      // 第4.190版
      else if (t === 'swap') a = { t: 'swap', u: rc(P.hand).u };
      else if (t === 'u5') { if (!(P.set && P.set.c.k === '5' && P.hand.length - 1 >= R.TURNS - S.turn && S.deck.length >= 1)) { bad++; break; } a = { t: 'u5', drop: rng() < 0.3 ? null : rc(P.hand).u }; }      // 第4.183版：交換で 出した 5
      else if (t === 'k') a = { t: 'k', pick: rng() < 0.3 ? null : rc(Q.hand.filter(c => P.known.indexOf(c.u) < 0)).u };
      else if (t === 'm') { const h = R.shuffle(P.hand.slice(), rng); a = { t: 'm', drop: rng() < 0.3 ? null : [h[0].u, h[1].u] }; }
      else if (t === 'rev') a = { t: 'rev', use: rng() < 0.75 };
      const lose = t === 'rev' ? Q.set.c.k : null;
      const r = R.act(S, i, a, rng);
      if (!r.ok || !sane(S)) { bad++; break; }
      r.ev.forEach(e => { if (e.e === 'open' && e.rev != null) st.q++; if (e.e === 'rev') { st.rev++; st['k' + e.k]++; revs[e.who]++; } if (e.e === 'revskip') st.skip++; });
      // 逆転で 負けた 神様馬・幻の馬の 効果は 出ない ／ 使わなかった ときは（次の ターンが あって 使える なら）出る
      if (t === 'rev' && a.use && r.ev.some(e => e.e === 'pre')) { bad++; break; }
      if (t === 'rev' && !a.use && (lose === 'k' || lose === 'm') && r.ev.some(e => e.e === 'pre')) st.pre++;
      if (S.phase !== 'end' && S.p.some(X => X.hand.length + (X.set ? 1 : 0) < R.TURNS - S.turn + 1)) { bad++; break; }
      const v = R.view(S, 1 - i); if (v.op.hand.some(c => c.k !== null && S.p[1 - i].known.indexOf(c.u) < 0)) { bad++; break; }
    }
    if (S.phase !== 'end' || S.turn !== 5 || S.discard.filter(d => d.why === 't').length !== 10) bad++;
    if (revs[0] >= 2 || revs[1] >= 2) st.two++;
    n++;
  }
  check(bad === 0 && n === 10000 && st.q === st.rev + st.skip, `1万回：こわれない・聞かれた ${st.q}回 ＝ 使った ${st.rev}回 ＋ 使わない ${st.skip}回・手札は のこりの ターンに いつも 足りる（おかしい ${bad}）`);
  check(st.k1 > 300 && st.k2 > 100 && st.pre > 50, `1 の 効果 ${st.k1}回・2 の 効果 ${st.k2}回・使わなかった ときは 相手の 神様馬／幻の馬の 効果が 出る（${st.pre}回）・使った ときは 出ない`);
  check(st.two > 0, `1回の 対戦で 2回 使う ことも ある（1 で 1回・2 で 1回：${st.two}回）`);
}

console.log('■ コンピュータ（見えて いる こと だけで 決める）');
{
  // 自分に 見える こと（view）だけを 渡す。返した 手は かならず 通る
  const play = (seed, pol0, pol1, games) => {
    const rng = rngOf(seed); const out = { w0: 0, w1: 0, d: 0, bad: 0, t: {} };
    const tally = (i, a) => { const ks = a.t === 'p6' ? [a.pick != null ? 'p6' : 'p6no'] : a.t !== 'eff' ? [a.t] : ['eff'].concat(Object.keys(a.use || {}).filter(k => a.use[k] != null && a.use[k] !== false)); ks.forEach(k => { out.t[i + k] = (out.t[i + k] || 0) + 1; }); };
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
    if (v.pend && v.pend.mine) return v.pend.type === 'swap' ? { t: 'swap', u: rc(h).u } : v.pend.type === 'k' ? { t: 'k', pick: null } : v.pend.type === 'rev' ? { t: 'rev', use: false } : v.pend.type === 'u5' ? { t: 'u5', drop: null } : { t: 'm', drop: null };
    if (v.can.six) return { t: 'p6', pick: null };      // 第4.190版
    if (v.can.eff) return { t: 'eff', use: null };
    return v.can.set ? { t: 'set', u: rc(h).u } : null;
  };
  // 強い 順に 出す 人
  const top = (v, rng) => {
    const h = v.my.hand.slice().sort((a, b) => R.power(a.k) - R.power(b.k));
    if (v.pend && v.pend.mine) return v.pend.type === 'swap' ? { t: 'swap', u: h[0].u } : v.pend.type === 'k' ? { t: 'k', pick: v.op.hand.find(c => c.k == null).u } : v.pend.type === 'rev' ? { t: 'rev', use: true } : v.pend.type === 'u5' ? { t: 'u5', drop: h[h.length - 1].u } : { t: 'm', drop: [h[h.length - 1].u, h[h.length - 2].u] };
    if (v.can.six) return { t: 'p6', pick: null };      // 第4.190版
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
  const S2 = G('66123', '12345'); const a2 = C.decide(mkv(S2, 0), rngOf(1));
  check(S2.phase === 'six' && a2.t === 'p6' && S2.p[1].hand.some(c => c.u === a2.pick) && C.decide(mkv(S2, 1), rngOf(1)) === null && R.act(S2, 0, a2).ok, '第4.190版：ターンの はじめ：6 が 2まい → 相手の 手札を 1まい 見る（相手は 待つ）');
  // まさちゃん 17:19「CPUが6の効果や神様馬の効果で、ユーザーの手札を見る時に、ちゃんとランダムで手札を選択するようになってる？」：まだ 見て いない カードから ひとしく（見た カードは えらばない・中身は 見ない）
  { const H = G('66123', '12345'); H.p[0].known.push(U(H, 1, '1'), U(H, 1, '2')); const cnt = {}; let badp = 0;
    for (let sd = 1; sd <= 6000; sd++) { const x = C.decide(mkv(H, 0), rngOf(sd)), k = (H.p[1].hand.find(c => c.u === x.pick) || {}).k; if (!k || k === '1' || k === '2') badp++; cnt[k] = (cnt[k] || 0) + 1; }
    const ks3 = ['3', '4', '5'];
    check(badp === 0 && ks3.every(k => Math.abs(cnt[k] / 6000 - 1 / 3) < 0.03), `コンピュータの 6：まだ 見て いない 3まい（3・4・5）から ひとしく ランダム（6000回で ${ks3.map(k => cnt[k]).join('・')}）・見た カード（1・2）は えらばない`);
    const K9 = G('k6612', '12345'); K9.p[0].known.push(U(K9, 1, '1')); p6(K9, 0, null); set(K9, 0, 'k'); set(K9, 1, '2'); p6(K9, 0, null);      // 神様馬で 勝った 次の ターン（相手の 手札 1・3・4・5：1 は 見た）
    const ck9 = {}; let bk = 0;
    for (let sd = 1; sd <= 6000; sd++) { const x = C.decide(mkv(K9, 0), rngOf(sd)), k = (K9.p[1].hand.find(c => c.u === x.pick) || {}).k; if (x.t !== 'k' || !k || k === '1') bk++; ck9[k] = (ck9[k] || 0) + 1; }
    check(K9.phase === 'pre' && bk === 0 && ks3.every(k => Math.abs(ck9[k] / 6000 - 1 / 3) < 0.03), `コンピュータの 神様馬：まだ 見て いない 3まい（3・4・5）から ひとしく ランダム（6000回で ${ks3.map(k => ck9[k]).join('・')}）・見た カード（1）は えらばない`); }
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
  let ok35 = true, n35 = 0;      // 第4.190版：5 と 3 の 両方 → 先に 3 を 決めて 行い、その あとの 手札で 5（1番 弱い カードを 捨てる）
  for (let sd = 1; sd <= 300; sd++) {
    const Z = G('53331', '12467'); set(Z, 0, '5'); set(Z, 1, '1');
    const x = C.decide(mkv(Z, 0), rngOf(sd)); if (x.t !== 'eff' || x.use.u5 != null || !R.act(Z, 0, x, rngOf(sd)).ok) { ok35 = false; continue; } if (x.use.x3) n35++;
    const y = C.decide(mkv(Z, 0), rngOf(sd + 1)), weak = Z.p[0].hand.slice().sort((a, b) => R.power(b.k) - R.power(a.k))[0];
    if (Z.step !== 'u5' || y.t !== 'eff' || y.use.u5 == null || R.power(kOf(Z, 0, y.use.u5)) !== R.power(weak.k) || !R.act(Z, 0, y).ok) ok35 = false;
  }
  check(ok35 && n35 > 60 && n35 < 160, `5 と 3 の 両方：先に 3 だけ 決める（${n35}／300回 で 交換）→ 行った あとの 手札で 5 の 効果（1番 弱い カードを 捨てる）`);
  const S4 = G('12354', '12346'); const seen = new Set(); for (let s = 1; s <= 200; s++) { const x = C.decide(mkv(S4, 0), rngOf(s)); seen.add(x.t + kOf(S4, 0, x.u)); }
  check([...seen].sort().join() === 'set1,set2,set3', `1ターン目は 強い 方から 3まいの どれか（毎回 同じ では ない：${[...seen].sort().join('・')}）・強い ときは 5 を ねらわない`);
  const S57 = G('57771', '12346', '234'); set(S57, 0, '5'); set(S57, 1, '1'); const a57 = C.decide(mkv(S57, 0), rngOf(1));
  check(a57.t === 'eff' && a57.use.x7 === true && a57.use.u5 == null && R.act(S57, 0, a57, rngOf(2)).ok && S57.step === 'u5', '5 と 7 の 両方：先に 7 の 交換 だけ（第4.190版：1つずつ）');
  const a57b = C.decide(mkv(S57, 0), rngOf(1));
  check(a57b.t === 'eff' && kOf(S57, 0, a57b.use.u5) === '4' && R.act(S57, 0, a57b).ok, '7 で 引いた あとの 手札（1・2・3・4）で 5 の 効果：1番 弱い 4 を 捨てる');
  const S5 = G('41236', '15677'); set(S5, 0, '4'); set(S5, 1, '1'); eff(S5, 0, { u4: true });
  const a5 = C.decide(mkv(S5, 1), rngOf(1)); check(a5.t === 'swap' && kOf(S5, 1, a5.u) === '5', '交換：4 に 勝てる カードも 4 も ない → 5 の 効果を 使える ので 5 を 出す（第4.183版：交換で 出した 5 の 効果で 山札に かける）');
  const S5b = G('41', '157'); set(S5b, 0, '4'); set(S5b, 1, '1'); eff(S5b, 0, { u4: true });
  const a5b = C.decide(mkv(S5b, 1), rngOf(1)); check(a5b.t === 'swap' && kOf(S5b, 1, a5b.u) === '7', '交換：4 に 勝てる カードも 4 も ない・5 の 効果も 使えない（手札が 足りない）→ 1番 弱い 7 を 出す（強い カードを 残す）');
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
  // 逆転勝利（第4.178版）：使える ときは いつも 使う（負けた 人 だけが 聞かれる）
  const SR = G('11123', 'm4567'); set(SR, 0, '1'); set(SR, 1, 'm'); const ar = C.decide(mkv(SR, 0), rngOf(1));
  check(SR.phase === 'rev' && ar && ar.t === 'rev' && ar.use === true && C.decide(mkv(SR, 1), rngOf(1)) === null && R.act(SR, 0, ar).ok && SR.p[0].wins === 1, '逆転勝利を 使える（1 が 3まいで 幻の馬に 負けた）→ 使う（聞かれて いない 方は 待つ）');
  const SR2 = G('22234', '14567'); set(SR2, 0, '2'); set(SR2, 1, '1'); const ar2 = C.decide(mkv(SR2, 0), rngOf(5));
  check(SR2.phase === 'rev' && ar2.t === 'rev' && ar2.use === true, '2 が 3まいで 1 に 負けた → 使う');
  const S10 = G('12367', '23456'); set(S10, 0, '1');
  check(C.decide(R.view(S10, 0), rngOf(1)) === null && C.decide(R.view(S10, 1), rngOf(1)).t === 'set' && C.decide(Object.assign(R.view(S10, 1), { phase: 'end' }), rngOf(1)) === null && C.decide(null) === null, 'セットした あと（相手を 待つ あいだ）は 何も しない・打つ ものが ない ときは null');
  const S13 = G('41236', '41567'); set(S13, 0, '4'); set(S13, 1, '4'); R.act(S13, 0, C.decide(R.view(S13, 0), rngOf(1)));
  check(S13.phase === 'eff' && S13.step === 'u4' && C.decide(R.view(S13, 0), rngOf(1)) === null && C.decide(R.view(S13, 1), rngOf(1)).t === 'eff', '効果タイムで 決めた あとは 何も しない（相手が 同じ 効果を 決める のを 待つ）');
  const S14 = G('66123', '66345'); R.act(S14, 0, C.decide(R.view(S14, 0), rngOf(1)));
  check(S14.phase === 'six' && C.decide(R.view(S14, 0), rngOf(1)) === null && C.decide(R.view(S14, 1), rngOf(1)).t === 'p6', '第4.190版：ターンの はじめの 6 も 同じ（決めた あとは 待つ）');
}
console.log('■ 第4.196版：決戦調査の 確定カード（opt.rig：敵の 手札に かならず 入る カード・のこりは くじ）');
{
  const RIGS = [['1'], ['1', '1'], ['2', '2'], ['2', '2', '2'], ['1', '1', '1'], ['1', 'k']];
  let ok = 0, bad = '', firsts = {}, pos = {};
  for (const rig of RIGS) for (let s = 1; s <= 400; s++) {
    const S = R.newGame(rngOf(1000 * rig.length + s), { rig: [[], rig] }), h = S.p[1].hand.map(c => c.k), need = {};
    rig.forEach(k => { need[k] = (need[k] || 0) + 1; });
    const good = Object.keys(need).every(k => h.filter(x => x === k).length >= need[k]) && S.p[0].hand.length === R.HAND && S.p[1].hand.length === R.HAND && S.deck.length === 30 - 2 * R.HAND && sane(S) && S.uid === 30 && (S.phase === 'set' || S.phase === 'six');
    if (good) ok++; else bad = bad || JSON.stringify([rig, h]);
    const k0 = S.p[1].hand[0].k; firsts[k0] = (firsts[k0] || 0) + 1;      // 手札の 1まい目（くじで ならべる）
    const iu = S.p[1].hand.findIndex(c => c.k === rig[0]); pos[iu] = (pos[iu] || 0) + 1;
  }
  check(ok === RIGS.length * 400, `確定カードが かならず 敵の 手札に（${ok}／${RIGS.length * 400}・カードは 30まいの まま・番号 1〜30）${bad}`);
  check(Object.keys(pos).length === R.HAND, `確定カードの 手札の 場所は くじ（7か所 ぜんぶ 出る：${JSON.stringify(pos)}）`);
  // 番号（u）の 順で 確定カードが わからない（番号の いちばん 小さい カードが 確定カード とは かぎらない）
  let low = 0; for (let s = 1; s <= 400; s++) { const S = R.newGame(rngOf(5000 + s), { rig: [[], ['1']] }), a = S.p[1].hand.slice().sort((x, y) => x.u - y.u); if (a[0].k === '1') low++; }
  check(low < 200, `番号の 順でも わからない（いちばん 小さい 番号が 1 だった：${low}／400）`);
  // あなた（席 0）は いつもの くじ：400回で 1 の まい数の 平均が ふつうと 同じ くらい
  let my1 = 0, base1 = 0; for (let s = 1; s <= 400; s++) { my1 += R.newGame(rngOf(9000 + s), { rig: [[], ['1', '1', '1']] }).p[0].hand.filter(c => c.k === '1').length; base1 += R.newGame(rngOf(9000 + s)).p[0].hand.filter(c => c.k === '1').length; }
  check(my1 / 400 < 0.25 && base1 / 400 > 0.7, `敵に 1 が 3まい 入る ときは、あなたの 1 は のこりの 1まい だけ（平均 ${(my1 / 400).toFixed(2)}まい・ふつうは ${(base1 / 400).toFixed(2)}まい）`);
  let threw = false; try { R.newGame(rngOf(1), { rig: [[], ['k', 'k']] }); } catch (e) { threw = true; }
  check(threw, '1まいしか ない カード（神様馬）を 2まい 入れる ことは できない');
  // 配った あとは ふつうの 対戦（コンピュータが 1ターン 進められる）
  const S = R.newGame(rngOf(77), { rig: [[], ['1', 'k']] }); no6(S);
  const a1 = C.decide(R.view(S, 1), rngOf(2)), r1 = a1 && R.act(S, 1, a1, rngOf(3));
  check(!!(r1 && r1.ok), '確定カードの 対戦も いつもどおり 進む（コンピュータが セットできる）');
}
console.log('■ 第4.197版：決戦宝石（まさちゃん 18:58「呼び寄せの決戦宝石」・19:03「決戦宝石が使えるのは手札が6枚以下の場合ね！」：1ターンに 1つ・同じ 宝石は 1戦に 1回・トークンは その ターン だけ）');
{
  // 本物の カードは いつも 30まい（トークンは 数えない・山札には 入らない）
  const real = S => all(S).filter(c => !c.tok);
  const saneG = S => { const a = real(S), us = new Set(a.map(c => c.u)); const n = {}; a.forEach(c => { n[c.k] = (n[c.k] || 0) + 1; }); return a.length === 30 && us.size === 30 && R.NUMS.every(k => n[k] === 4) && n.k === 1 && n.m === 1 && !S.deck.some(c => c.tok); };
  const GG = (h0, h1, deck, gems, pub) => R.newGame(rngOf(7), { hands: [h0.split(''), h1.split('')], deck: deck ? deck.split('') : undefined, turns: 5, gems: gems, gpub: !!pub });
  const gem = (S, i, g) => R.act(S, i, { t: 'gem', g: g }, rngOf(3));
  const turn = (S, k0, k1) => { no6(S); set(S, 0, k0); set(S, 1, k1); while (S.phase === 'eff') [0, 1].forEach(i => { if (S.p[i].eff && !S.p[i].eff.done) eff(S, i, null); }); no6(S); };      // 1ターン（効果は 使わない）
  check(R.GEMS.join('') === 'mk137' && R.GEM_W.m === 1 && R.GEM_W.k === 1 && R.GEM_W['1'] === 2 && R.GEM_W['3'] === 2 && R.GEM_W['7'] === 3 && R.GEM_HAND === 6,
    '宝石は 5つ（幻影のアメジスト＝幻の馬・日輪の黄金石＝神様馬・双炎のルビー＝1 2頭分・双葉のエメラルド＝3 2頭分・三峰の翡翠＝7 3頭分）・手札 6まい 以下で 使える');
  { const S = R.newGame(rngOf(1)); const v = R.view(S, 0); check(v.my.gem === null && v.op.gem === null && v.can.gem.length === 0 && !gem(S, 0, 'k').ok, '宝石 なしの 対戦（決まりを 入れない ふだんの 形）：宝石は 出ない・使えない'); }
  // 決戦調査の 形：あなた（席 0）に 5つ・敵（席 1）は なし・敵には 知らせない
  {
    const S = GG('1234567', '1234566', '1234567', [R.GEMS, []]);
    let v = R.view(S, 0);
    check(v.my.gem && v.my.gem.list.join('') === 'mk137' && v.my.gem.used.length === 0 && v.can.gem.length === 0 && R.view(S, 1).my.gem === null && R.view(S, 1).op.gem === null,
      '決戦調査の 形：あなたの ケースに 5つ・敵は なし・敵には あなたの 宝石は 見えない');
    check(!gem(S, 0, 'k').ok && S.p[0].hand.length === 7, '1ターン目（手札 7まい）は 使えない（手札 6まい 以下：19:03）');
    turn(S, '7', '6');
    v = R.view(S, 0);
    check(S.turn === 2 && S.p[0].hand.length === 6 && v.can.gem.join('') === 'mk137' && R.legal(S, 0).indexOf('gem') >= 0 && R.view(S, 1).can.gem.length === 0, '2ターン目（手札 6まい）：5つ ぜんぶ 使える（敵は 使えない）');
    const r = gem(S, 0, 'k'), tk = S.p[0].hand.find(c => c.tok);
    v = R.view(S, 0);
    check(r.ok && tk && tk.k === 'k' && tk.tok === 1 && S.p[0].hand.length === 7 && v.my.hand.some(c => c.u === tk.u && c.tok === 1) && v.my.gem.used.join('') === 'k' && v.my.gem.now && v.can.gem.length === 0,
      '日輪の黄金石 → 手札に 神様馬トークン（1頭分）が 1まい・使った 宝石・この ターンは もう 使えない（1ターンに 1つ）');
    check(!gem(S, 0, '1').ok && !gem(S, 1, 'k').ok, 'この ターンに 2つ目は 使えない・敵は 使えない');
    const e1 = R.evFor(r.ev, 1), w1 = R.view(S, 1);
    check(e1.length === 0 && w1.op.hand.length === 7 && w1.op.hand.every(c => c.k === null) && R.evFor(r.ev, 0)[0].e === 'gem' && R.evFor(r.ev, 0)[0].c.k === 'k',
      '敵には 知らせない（できごとは 出ない・敵から 見ると 手札が 1まい ふえた だけ・トークンも うら）');
    set(S, 0, '2'); set(S, 1, '1'); no6(S);
    while (S.phase === 'eff') [0, 1].forEach(i => { if (S.p[i].eff && !S.p[i].eff.done) eff(S, i, null); });
    const gone = S.discard.length;
    check(S.turn === 3 && !S.p[0].hand.some(c => c.tok) && S.p[0].hand.length === 5 && saneG(S), '使わなかった トークンは ターンの おわりに 消える（手札は 本物の 5まい）');
    check(R.view(S, 0).can.gem.join('') === 'm137', '3ターン目：使った 日輪の黄金石は もう 使えない（同じ 宝石は 1戦に 1回）・ほかの 4つは 使える');
    gem(S, 0, 'm'); const tm = S.p[0].hand.find(c => c.tok);
    set(S, 0, 'm'); set(S, 1, '3');
    const last = S.discard.slice(gone).find(d => d.tok);
    check(tm && S.p[0].wins >= 1 && last && last.k === 'm' && last.tok === 1 && R.view(S, 0).discard.some(d => d.tok === 1 && d.k === 'm') && saneG(S),
      '幻影のアメジスト → 幻の馬トークンを セット → 3 に 勝つ・場の トークンは 捨て札へ（トークンの しるし つき）');
  }
  // かぶり：神様馬トークン と 神様馬
  {
    const S = GG('1234567', 'k234566', '1234567', [R.GEMS, []]);
    turn(S, '7', '6'); gem(S, 0, 'k'); set(S, 0, 'k'); set(S, 1, 'k'); no6(S);
    check(S.last.res === 'clash' && S.last.c.join('') === 'kk' && S.p[0].wins === 0 && S.p[1].wins === 1, '神様馬トークン と 神様馬が ぶつかったら かぶり（どちらも 負け：勝ちは 1ターン目の まま）');
  }
  // 1トークン（2頭分）で 逆転勝利
  {
    const S = GG('1234567', 'k234566', '1234567', [R.GEMS, []]);
    turn(S, '7', '6'); gem(S, 0, '1'); const t1 = S.p[0].hand.find(c => c.tok);
    set(S, 0, '1'); set(S, 1, 'k'); no6(S);
    check(S.phase === 'rev' && S.pend.who === 0 && t1.tok === 2, '1 を 出して 神様馬に 負けた・手札に 1トークン（1まいで 2頭分）だけ → 逆転勝利を 聞かれる（場 ＋ 2頭分 ＝ 3まい）');
    const r = R.act(S, 0, { t: 'rev', use: true }, rngOf(3)), ev = r.ev.find(e => e.e === 'rev');
    check(r.ok && ev && ev.show.length === 1 && ev.show[0] === t1.u && ev.drop.tok === 2 && S.p[0].wins === 1 && !S.p[0].hand.some(c => c.tok) && S.p[0].hand.length === 5 && saneG(S),
      '使う → 1トークンを 見せて 捨てる（1まい ぶん）→ 勝ち。本物の 手札は へらない（5まい）');
  }
  // 3トークン（2頭分）＋ 3 で 交換（わたす のは 本物の 3）
  {
    const S = GG('1324567', '1234566', '1234567', [R.GEMS, []]);
    turn(S, '7', '6'); gem(S, 0, '3'); const t3 = S.p[0].hand.find(c => c.tok), real3 = S.p[0].hand.find(c => c.k === '3' && !c.tok);
    no6(S); set(S, 0, '1'); set(S, 1, '1');
    check(S.phase === 'eff' && S.step === 'x3' && S.p[0].eff.can, '3トークン（2頭分）＋ 3 ＝ 3 が 3まい → 3 の 効果を 聞かれる');
    const r = eff(S, 0, { x3: true }), x3 = r.ev.find(e => e.e === 'x3');
    const tg = r.ev.find(e => e.e === 'tokgone' && e.who === 0);
    check(x3 && x3.give.u === real3.u && !x3.give.tok && !x3.take.tok && x3.three.indexOf(t3.u) >= 0 && !S.p[1].hand.some(c => c.u === t3.u) && S.p[1].hand.some(c => c.u === real3.u) && tg && tg.u.indexOf(t3.u) >= 0,
      '相手に わたすのは 本物の 3（トークンは 手元に のこる：ターンで 消える）・もらうのも 本物の カード');
  }
  // 7トークン（3頭分）：3まい 交換（トークンを もどして 3まい 引く）
  {
    const S = GG('1234566', '1234565', '1234567', [R.GEMS, []]);
    turn(S, '6', '5'); gem(S, 0, '7'); const t7 = S.p[0].hand.find(c => c.tok), d0 = S.deck.length, h0 = S.p[0].hand.length;
    no6(S); set(S, 0, '1'); set(S, 1, '1');
    check(S.phase === 'eff' && S.step === 'x7' && S.p[0].eff.can && t7.tok === 3, '7トークン（3頭分）1まい ＝ 7 が 3まい → 7 の 3まい 交換を 聞かれる');
    const r = eff(S, 0, { x7: true }), x7 = r.ev.find(e => e.e === 'x7');
    check(x7 && x7.tok === t7.u && x7.drew.length === 3 && !S.p[0].hand.some(c => c.u === t7.u) && S.deck.length === d0 - 3 && !S.deck.some(c => c.tok) && S.p[0].hand.length === h0 - 1 - 1 + 3 && saneG(S),
      'トークンを もどして（山札には 入らない：消える）3まい 引く ＝ 手札が 2まい ふえる（まさちゃんに 伝えた 形）');
    const o1 = R.evFor(r.ev, 1).find(e => e.e === 'x7');
    check(o1 && o1.tok === undefined && o1.drew === undefined, '決戦調査（宝石は 自分 だけ）：敵には トークンを もどした ことを 知らせない（引いた カードも）');
  }
  {      // 友だちとの 対戦：相手にも「7トークンを もどした」が わかる（引いた カードは わからない）
    const S = GG('1234566', '1234565', '1234567', [['7'], ['1']], true);
    turn(S, '6', '5'); gem(S, 0, '7'); const t7 = S.p[0].hand.find(c => c.tok);
    no6(S); set(S, 0, '1'); set(S, 1, '1');
    const r = eff(S, 0, { x7: true }), o1 = R.evFor(r.ev, 1).find(e => e.e === 'x7'), o0 = R.evFor(r.ev, 0).find(e => e.e === 'x7');
    check(o1 && o1.tok === t7.u && o1.drew === undefined && o0 && o0.tok === t7.u && o0.drew.length === 3, '友だちとの 対戦：相手にも 7トークンを もどした ことが わかる（引いた カードは 自分 だけ）');
  }
  // 7トークン（3頭分）＋ 7 ＝ 4まい 公開（強さ 逆転：捨てるのは トークン）
  {
    const S = GG('1234567', '1234566', '1234567', [R.GEMS, []]);
    turn(S, '6', '6'); gem(S, 0, '7');
    const t7 = S.p[0].hand.find(c => c.tok), r7 = S.p[0].hand.find(c => c.k === '7' && !c.tok);
    check(R.view(S, 0).can.x7r, '7トークン（3頭分）＋ 7 ＝ 7 が 4まい → セットの 前に 4まい 公開が 使える');
    const r = R.act(S, 0, { t: 'x7r' }, rngOf(3)), ev = r.ev.find(e => e.e === 'x7r');
    check(r.ok && S.rv && ev.drop.u === t7.u && ev.show.length === 2 && S.p[0].hand.some(c => c.u === r7.u) && S.p[1].known.indexOf(r7.u) >= 0 && saneG(S), '使う → 捨てるのは トークン（どうせ 消える）・本物の 7 は 手札に（相手に 知られる）・強さ 逆転');
  }
  // 5 の 効果：トークンを いっしょに 捨てる ときは 本物の 手札が へらない
  {
    const S = GG('5123467', '1234566', '1234567', [R.GEMS, []]);
    turn(S, '1', '1'); toDis(S, 0, '2'); toDis(S, 0, '3');      // 本物の 手札を ぎりぎりに（4まい：のこり 4ターン）
    gem(S, 0, '1'); const t1 = S.p[0].hand.find(c => c.tok);
    no6(S); set(S, 0, '5'); set(S, 1, '2');
    check(S.phase === 'eff' && S.step === 'u5' && S.p[0].eff.can, '本物の 手札が ぎりぎりでも、トークンを いっしょに 捨てる なら 5 の 効果を 聞かれる');
    const bad = eff(S, 0, { u5: S.p[0].hand.find(c => !c.tok).u }), good = eff(S, 0, { u5: t1.u });
    check(!bad.ok && good.ok && S.p[0].hand.filter(c => !c.tok).length === 3 && !S.p[0].hand.some(c => c.tok) && saneG(S), '本物の カードを 捨てると 足りなく なる → 受けつけない・トークンを 捨てる → 使える');
  }
  // セットの 後・ターンの はじめ（6）は 使えない
  {
    const S = GG('6612345', '1234567', '1234567', [R.GEMS, []]);
    turn(S, '5', '7'); check(S.phase === 'six' || S.phase === 'set', '2ターン目の はじめ'); if (S.phase === 'six') check(!gem(S, 0, 'k').ok, 'ターンの はじめ（6 の 効果を 決める 前）は 使えない'); no6(S);
    set(S, 0, '4'); check(!gem(S, 0, 'k').ok && R.view(S, 0).can.gem.length === 0, 'セットした あとは 使えない（セットの 前に 使う）');
  }
  // 第4.197版（まさちゃん 20:20「決戦宝石は、1試合に5個じゃなくて、1クエスト連勝継続中に合計5個しか使えない！」）：前の 戦で 使った 宝石（opt.gused）は はじめから「使った」
  {
    const S = R.newGame(rngOf(5), { hands: [['1', '2', '3', '4', '5'], ['1', '2', '3', '4', '6']], turns: 3, gems: [R.GEMS, []], gused: [['k', '1', 'x'], ['m']] });
    const v0 = R.view(S, 0);
    check(S.phase === 'set' && v0.my.gem.used.join('') === 'k1' && v0.my.gem.can.join('') === 'm37' && S.p[1].gused.length === 0 && !gem(S, 0, 'k').ok && !gem(S, 0, '1').ok,
      '決戦調査の 2戦目：前の 戦で 使った 宝石（日輪の黄金石・双炎のルビー）は はじめから「使った」＝ もう 使えない（持って いない 宝石・おかしい 名前は 数えない）');
    check(gem(S, 0, 'm').ok && R.view(S, 0).my.gem.used.join('') === 'k1m' && R.view(S, 0).my.gem.can.length === 0, 'のこりの 宝石は 使える（使った ものに たして いく）');
    const S2 = R.newGame(rngOf(5), { hands: [['1', '2', '3', '4', '5'], ['1', '2', '3', '4', '6']], turns: 3, gems: [R.GEMS, []] });
    check(R.view(S2, 0).my.gem.used.length === 0 && R.view(S2, 0).my.gem.can.join('') === R.GEMS.join(''), 'gused が ない ＝ 5つ ぜんぶ 使える（友だちとの 対戦・調査の 1戦目）');
  }
  // 持って いる 宝石だけ 使える・おたがいに 見える（例：1つずつ）
  {
    const S = GG('1234567', '1234566', '1234567', [['k'], ['1']], true);
    const v0 = R.view(S, 0), v1 = R.view(S, 1);
    check(v0.my.gem.list.join('') === 'k' && v0.op.gem.list.join('') === '1' && v1.my.gem.list.join('') === '1' && v1.op.gem.list.join('') === 'k', '持って いる 宝石だけ（1つずつ の 例）・おたがいの 宝石が 見える（gpub）');
    turn(S, '7', '6');
    check(!gem(S, 0, '1').ok && !gem(S, 1, 'k').ok, '持って いない 宝石は 使えない');
    const r = gem(S, 0, 'k'), e1 = R.evFor(r.ev, 1), w1 = R.view(S, 1), tk = S.p[0].hand.find(c => c.tok);
    check(r.ok && e1.length === 1 && e1[0].e === 'gem' && e1[0].g === 'k' && w1.op.hand.some(c => c.u === tk.u && c.k === 'k' && c.tok === 1) && w1.op.gem.used.join('') === 'k',
      '使うと 相手にも 知らせる（相手の 画面で トークンは 表に 見える・使った 宝石も 見える）');
    check(gem(S, 1, '1').ok, '相手も 同じ ターンに 自分の 宝石を 使える（1人 1ターンに 1つ）');
  }
  // でたらめに あそぶ（宝石 あり）：どんな 手の 順でも こわれない
  {
    const rng = rngOf(20261197); let bad = 0, why = ''; const st = { gem: 0, tokgone: 0, tokset: 0, revT: 0, x7T: 0, x3T: 0, x7rT: 0, u5T: 0 };
    for (let g = 0; g < 6000; g++) {
      const pub = g % 2 === 0, gems = pub ? [[R.GEMS[g % 5]], [R.GEMS[(g + 2) % 5]]] : [R.GEMS, []];
      const S = R.newGame(rng, { gems: gems, gpub: pub }); let guard = 0; const usedT = [{}, {}];
      while (S.phase !== 'end' && guard++ < 300) {
        const L0 = R.legal(S, 0), L1 = R.legal(S, 1);
        if (!L0.length && !L1.length) { bad++; why = why || 'stuck'; break; }
        const i = rng() < 0.5 ? 0 : 1, L = i === 0 ? L0 : L1; if (!L.length) continue;
        let t = L[Math.floor(rng() * L.length)]; if (L.indexOf('gem') >= 0 && rng() < 0.6) t = 'gem';
        const P = S.p[i], rc = h => h[Math.floor(rng() * h.length)]; let a;
        const v = R.view(S, i);
        if (t === 'gem') a = { t: 'gem', g: rc(v.can.gem) };
        else if (t === 'set') a = { t: 'set', u: rc(P.hand).u };
        else if (t === 'x7r') a = { t: 'x7r' };
        else if (t === 'eff') { const c = v.can.eff; a = { t: 'eff', use: rng() < 0.3 ? {} : c.e7 ? { x7: true } : c.e3 ? { x3: true } : c.e4 ? { u4: true } : c.e5 ? { u5: rc(P.hand.filter(x => R.view(S, i).my.hand.some(y => y.u === x.u))).u } : {} }; }
        else if (t === 'p6') { const un = v.op.hand.filter(x => x.k == null); a = { t: 'p6', pick: un.length && rng() < 0.8 ? rc(un).u : null }; }
        else if (t === 'swap') a = { t: 'swap', u: rc(P.hand).u };
        else if (t === 'u5') a = { t: 'u5', drop: rng() < 0.3 ? null : rc(P.hand).u };
        else if (t === 'k') { const un = v.op.hand.filter(x => x.k == null); a = { t: 'k', pick: un.length && rng() < 0.8 ? rc(un).u : null }; }
        else if (t === 'm') { const h = R.shuffle(P.hand.slice(), rng); a = { t: 'm', drop: rng() < 0.2 ? null : [h[0].u, h[1].u] }; }
        else if (t === 'rev') a = { t: 'rev', use: rng() < 0.7 };
        const tn = S.turn, hn = P.hand.length;
        let r = R.act(S, i, a, rng);
        if (!r.ok && t === 'eff') r = R.act(S, i, { t: 'eff', use: {} }, rng);      // 5 で 捨てる カード（くじ）が 足りなく なる カード だった → 使わない
        if (!r.ok && t === 'u5') r = R.act(S, i, { t: 'u5', drop: null }, rng);
        if (!r.ok) { bad++; why = why || 'ng ' + t + ' ' + r.why; break; }
        r.ev.forEach(e => {
          if (e.e === 'gem') { st.gem++; if (usedT[e.who][tn]) { bad++; why = why || 'twice'; } usedT[e.who][tn] = 1; if (hn > R.GEM_HAND) { bad++; why = why || 'hand7'; } }
          if (e.e === 'tokgone') st.tokgone++;
          if (e.e === 'open' && e.c.some(c => c.tok)) st.tokset++;
          if (e.e === 'rev' && e.drop.tok) st.revT++;
          if (e.e === 'x7' && e.tok) st.x7T++;
          if (e.e === 'x3' && e.three.length < 3) st.x3T++;      // 3トークン（2頭分）＋ 3 ＝ 2まいで 3まい ぶん
          if (e.e === 'x7r' && e.drop.tok) st.x7rT++;
          if (e.e === 'u5' && e.drop.tok) st.u5T++;
        });
        if (!saneG(S)) { bad++; why = why || 'cards'; break; }
        if (r.ev.some(e => e.e === 'turn') && S.p.some(X => X.hand.some(c => c.tok))) { bad++; why = why || 'tok left'; break; }      // ターンを またいだら トークンは ない
        if (S.phase !== 'end' && S.p.some(X => realN(X) + (X.set && !X.set.c.tok ? 1 : 0) + (X.set && X.set.c.tok ? 1 : 0) < R.TURNS - S.turn + 1)) { bad++; why = why || 'short'; break; }      // のこりの ターンに 出す カードが ある
        if (S.p.some(X => X.gused.length !== new Set(X.gused).size || X.gused.some(k => X.gems.indexOf(k) < 0))) { bad++; why = why || 'gused'; break; }
        if (!pub && t === 'gem') { const w1 = R.view(S, 1); if (w1.op.hand.some(c => c.tok) || R.evFor(r.ev, 1).length) { bad++; why = why || 'leak'; break; } }      // 決戦調査：宝石を 使った ことは 敵に 知らせない（3・7 の 効果で 見せた ときは 見える）
      }
      if (S.phase !== 'end' || S.turn !== 5) { bad++; why = why || 'end'; }
    }
    function realN(X) { return X.hand.filter(c => !c.tok).length; }
    check(bad === 0, `宝石 あり で 6000回（決戦調査の 形・友だちとの 対戦の 形）：ぜんぶ 5ターンで おわる・本物の カードは 30まい・トークンは ターンを またがない・1ターンに 1つ・手札 6まい 以下・宝石は 1回 ずつ（おかしい ${bad}${why ? '：' + why : ''}）`);
    check(st.gem > 5000 && st.tokgone > 500 && st.tokset > 500 && st.revT > 0 && st.x7T > 0 && st.x7rT > 0 && st.u5T > 0 && st.x3T > 0,
      `トークンの 効果も 出た（宝石 ${st.gem}・消えた ${st.tokgone}・場に 出した ${st.tokset}・トークンで 逆転勝利 ${st.revT}・3 の 交換 ${st.x3T}・7 の 3まい 交換 ${st.x7T}・4まい 公開 ${st.x7rT}・5 で 捨てた ${st.u5T}）`);
  }
  // コンピュータ（敵）は 宝石を 使わない・あなたの トークンが あっても いつもどおり 決める
  {
    const rng = rngOf(4197); let bad = 0;
    for (let g = 0; g < 1500; g++) {
      const S = R.newGame(rng, { gems: [R.GEMS, []] }); let guard = 0;
      while (S.phase !== 'end' && guard++ < 300) {
        const L0 = R.legal(S, 0);
        if (L0.length) { const v = R.view(S, 0); const a = v.can.gem.length && rng() < 0.7 ? { t: 'gem', g: v.can.gem[Math.floor(rng() * v.can.gem.length)] } : C.decide(v, rng); if (a && !R.act(S, 0, a, rng).ok) { bad++; break; } }
        const a1 = C.decide(R.view(S, 1), rng); if (a1) { if (a1.t === 'gem') { bad++; break; } if (!R.act(S, 1, a1, rng).ok) { bad++; break; } }
        if (!L0.length && !a1) { bad++; break; }
      }
      if (S.phase !== 'end') bad++;
    }
    check(bad === 0, `コンピュータは 宝石を 使わない・あなたが トークンを 使っても 最後まで 進む（1500回：おかしい ${bad}）`);
  }
}
console.log('結果：', fails.length ? fails.length + '件おかしい' : 'OK');
process.exit(fails.length ? 1 : 0);
