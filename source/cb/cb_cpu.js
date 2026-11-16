// 馬カードバトルの コンピュータ（第4.176版）：自分に 見えて いる こと（CBRules.view）だけで 手を 決める ＝ 相手の 手札も 山札も のぞかない
//   CBCpu.decide(v, rng) → 打つ 手（CBRules.act の a）。打つ ものが ない ときは null
//   考え方（むずかしい 読みは しない・毎回 同じ 手に ならない ように 少し まぜる）：
//     ・セットする カード：強い 方から「のこりの ターンの 数」まいの 中から えらぶ（5ターンの 1ターン目＝上から 5まいの どれか・…・さいごの ターン＝1番 強い カード。
//         第4.178版：手札 7まい・5ターン ＝ 弱い 2まいは 出さずに のこる：5 の 効果・幻の馬の 効果で 捨てる カード）
//         相手の 手札で 知って いる カードと 同じ 数字は、ほかに 出せる カードが あれば さける（かぶると どちらも 負け）
//         5 の 効果が 使える ターン（第4.177版：5 を 出した あとの 手札 − 1 が のこりの ターンの 数 以上・山札が ある ＝ どの ターンでも）で、
//         これから 出す カードの 中で 1番 弱い のが 5 より 弱い か 同じ（＝どうせ 弱い カードを 出す）なら、5 を セットする（効果タイムで 5 の 効果を ねらう）
//     ・効果タイム：7 が 3まい → 交換する（7 は 1番 弱い）／ 6 が 2まい → まだ 知らない 相手の 手札を 1まい 見る ／
//         5 を セットして いる → 1番 弱い 手札を 捨てて 山札から 出す（7 の 交換・3 の 交換も する ときは、その 3まいを くずさない カードが ある とき だけ）／
//         3 が 3まい（第4.177版）→ 1ターン目は 3回に 1回・2ターン目からは 半分 ほど 使う（3 を 1まい わたして 相手の 手札を くじで 1まい もらう：手の 内を 見せる ので 毎回は 使わない）／
//         4 を セットして いる → 1ターン目は 使わない・とちゅうの ターンは 半分・さいごの ターンは 使う（相手の 手札が 少ない ほど 効く）
//     ・交換（相手の 4 の 効果）：4 に 勝てる カードの 中で 1番 弱い もの。なければ 4（かぶって どちらも 負け）。それも なければ 1番 弱い カード
//     ・神様馬の 効果（次の ターンの はじめ）：まだ 知らない カードを 見る（第4.178版：知らない カードが ない ときは 聞かれない。見るのは 知らない カード だけ）／
//         幻の馬の 効果：弱い 方から 2まい 捨てる（のこりの ターンで 出さない カード）
//     ・逆転勝利（第4.178版：1 で 神様馬・幻の馬に／2 で 1 に 負けた とき、手札に 同じ 数字が 2まい あれば 使える）：使える ときは いつも 使う
const CBCpu = (() => {
  'use strict';
  const power = k => (k === 'k' || k === 'm' ? 0 : +k);
  const byStrong = hand => hand.slice().sort((a, b) => power(a.k) - power(b.k) || a.u - b.u);      // 強い 順
  const pick = (a, rng) => a[Math.floor(rng() * a.length)];

  function decide(v, rng) {
    rng = rng || Math.random;
    if (!v || v.phase === 'end') return null;
    const hand = v.my.hand, opHand = v.op.hand;
    if (v.pend && v.pend.mine) {
      if (v.pend.type === 'swap') {
        const s = byStrong(hand), win = s.filter(c => power(c.k) < 4);
        if (win.length) return { t: 'swap', u: win[win.length - 1].u };
        const four = s.find(c => c.k === '4'); if (four) return { t: 'swap', u: four.u };
        return { t: 'swap', u: s[s.length - 1].u };
      }
      if (v.pend.type === 'k') {
        const un = opHand.filter(c => c.k == null);
        return { t: 'k', pick: un.length ? pick(un, rng).u : null };
      }
      if (v.pend.type === 'm') {
        const s = byStrong(hand);
        return { t: 'm', drop: [s[s.length - 1].u, s[s.length - 2].u] };
      }
      if (v.pend.type === 'rev') return { t: 'rev', use: true };      // 逆転勝利（第4.178版）：使える ときは いつも 使う（負けが 勝ちに なる：1まい 捨てる より 得）
      return null;
    }
    if (v.can.eff) {                                     // 効果タイム：使う ものを まとめて 決める
      const c = v.can.eff, use = {}, s = byStrong(hand), n7 = hand.filter(x => x.k === '7').length, n3 = hand.filter(x => x.k === '3').length;
      if (c.e6) { const un = opHand.filter(x => x.k == null); if (un.length) use.p6 = pick(un, rng).u; }
      if (c.e7) use.x7 = true;
      if (c.e3 && rng() < (v.turn >= 2 ? 0.55 : 0.35)) use.x3 = true;
      if (c.e5) {
        // 7 の 交換も する とき：7 は 3まい 残す（4まい ある ときは 1まい 捨てて いい）。7 で ない カードは 弱い（5・6）とき だけ 捨てる。3 の 交換も する とき：3 は 3まい 残す
        const cand = s.filter(x => !(use.x7 && x.k === '7' && n7 <= 3) && !(use.x3 && x.k === '3' && n3 <= 3)), weak = cand[cand.length - 1];
        if (weak && ((!use.x7 && !use.x3) || (use.x7 && weak.k === '7') || (use.x3 && weak.k === '3') || power(weak.k) >= 5)) use.u5 = weak.u;
      }
      if (c.e4 && (v.turn >= v.turns ? true : v.turn >= 2 ? rng() < 0.5 : false)) use.u4 = true;
      return { t: 'eff', use: use };
    }
    if (v.phase !== 'set' || !v.can.set) return null;
    const s = byStrong(hand), left = v.turns - v.turn + 1;          // のこりの ターン（この ターンも 入れて）
    const top = s.slice(0, Math.min(left, s.length));
    if (hand.length - 2 >= v.turns - v.turn && hand.length - 1 >= 1 && v.deckN >= 1) {          // 5 の 効果を ねらう（第4.177版：5 を 出して、手札を 1まい 捨てても のこりの ターンに 足りる）
      const third = top[top.length - 1], five = s.find(x => x.k === '5');
      if (five && power(third.k) >= 5) return { t: 'set', u: five.u };
    }
    const knownOp = opHand.filter(x => x.k != null).map(x => x.k);
    let cand = top.filter(x => x.k === 'k' || x.k === 'm' || knownOp.indexOf(x.k) < 0);
    if (!cand.length) cand = top;
    return { t: 'set', u: pick(cand, rng).u };
  }
  return { decide };
})();
if (typeof module !== 'undefined' && module.exports) module.exports = CBCpu;
