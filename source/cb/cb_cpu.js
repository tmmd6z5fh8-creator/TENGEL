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
//         第4.183版：4 も なくて 5 の 効果を 使える（手札 − 1 が のこりの ターンの 数 以上・山札が ある）なら 5（交換で 出した 5 の 効果で 山札から 出す）。
//         交換で 出した 5 の 効果は いつも 使う（4 には 5 で 勝てない：山札の カードに かける）。捨てるのは 1番 弱い 手札
//     ・神様馬の 効果（次の ターンの はじめ）：まだ 知らない カードを 見る（第4.178版：知らない カードが ない ときは 聞かれない。見るのは 知らない カード だけ）／
//         幻の馬の 効果：弱い 方から 2まい 捨てる（のこりの ターンで 出さない カード）
//     ・逆転勝利（第4.178版：1 で 神様馬・幻の馬に／2 で 1 に 負けた とき、手札に 同じ 数字が 2まい あれば 使える）：使える ときは いつも 使う
//     ・第4.185版：7 が 4まい → いつも 4まい 見せて 逆転（7 が 1番 強く なる）。強さ 逆転ちゅう（v.rv）は 強さを 逆で 見る（出す カード・交換・捨てる カード）・7 の 3まい 交換は しない（7 は 強い）
//       第4.187版：4まい 公開は セットの 前（v.can.x7r → { t:'x7r' }。その あと いつもの ように セット：逆転した 強さで えらぶ）
//     ・第4.190版：6 の 効果は ターンの はじめ（v.can.six → { t:'p6', pick }：まだ 見て いない 手札から ランダムに 1まい）。
//       効果タイムは 1つずつ 聞かれる（v.can.eff に いまの 効果 1つ）→ その 効果 だけ 決める（7・3 の あとの 手札で 5 を 考える）
//     ・相手の 手札を 見る（6・神様馬）ときは、まだ 見て いない カード（うら）の 中から ひとしく ランダムに えらぶ（カードの 中身は 見えて いない：のぞかない）
//     ・第4.197版：決戦宝石は 使わない（決戦調査の 敵は 宝石 なし：まさちゃんの 答え）。手札に トークンが ある とき（テストで 席 0 を まかせた とき）は 5 の 効果で トークンを 捨てる
//     ・第4.202版（まさちゃん 23:42「手札から使える効果は、カードセット前に使えるようにして！」）：7 の 3まい 交換・3 の 交換は セットの 前（v.can.x7 → { t:'x7' }・v.can.x3 → { t:'x3' }）。
//       考え方は 前と 同じ：7 が 3まい → 交換する（逆転ちゅうは しない）／3 が 3まい → 1ターン目は 3回に 1回・2ターン目からは 半分 ほど。使った あとの 手札で セットする カードを えらぶ。
//       効果タイムは 5 → 4 だけ。3 で もらう カードは 相手の 手札の うらの カード（v.can.x3p）から ランダムに 1まい（00:38「CPUが勝手に選ぶ形にならないようにして！」：使う 人が えらぶ 決まり）
const CBCpu = (() => {
  'use strict';
  const power = (k, rv) => (k === 'k' || k === 'm' ? 0 : rv ? 8 - +k : +k);      // 小さい ほど 強い（rv＝強さ 逆転ちゅう：第4.185版）
  const byStrong = (hand, rv) => hand.slice().sort((a, b) => power(a.k, rv) - power(b.k, rv) || a.u - b.u);      // 強い 順
  const pick = (a, rng) => a[Math.floor(rng() * a.length)];

  function decide(v, rng) {
    rng = rng || Math.random;
    if (!v || v.phase === 'end') return null;
    const hand = v.my.hand, opHand = v.op.hand, rv = !!v.rv, P = k => power(k, rv), byS = h => byStrong(h, rv);
    if (v.pend && v.pend.mine) {
      if (v.pend.type === 'swap') {
        const s = byS(hand), win = s.filter(c => P(c.k) < P('4'));
        if (win.length) return { t: 'swap', u: win[win.length - 1].u };
        const four = s.find(c => c.k === '4'); if (four) return { t: 'swap', u: four.u };
        const five = s.find(c => c.k === '5'); if (five && hand.length - 1 >= v.turns - v.turn && v.deckN >= 1) return { t: 'swap', u: five.u };      // 第4.183版
        return { t: 'swap', u: s[s.length - 1].u };
      }
      if (v.pend.type === 'u5') { const s = byS(hand), tk = hand.find(c => c.tok); return { t: 'u5', drop: tk ? tk.u : s.length ? s[s.length - 1].u : null }; }      // 第4.183版：交換で 出した 5 の 効果（第4.197版：トークンが あれば それを 捨てる）
      if (v.pend.type === 'k') {
        const un = opHand.filter(c => c.k == null);
        return { t: 'k', pick: un.length ? pick(un, rng).u : null };
      }
      if (v.pend.type === 'm') {
        const s = byS(hand);
        return { t: 'm', drop: [s[s.length - 1].u, s[s.length - 2].u] };
      }
      if (v.pend.type === 'rev') return { t: 'rev', use: true };      // 逆転勝利（第4.178版）：使える ときは いつも 使う（負けが 勝ちに なる：1まい 捨てる より 得）
      return null;
    }
    if (v.can.six) {                                     // 第4.190版：6 の 効果（ターンの はじめ）：まだ 見て いない 手札から ランダムに 1まい 見る
      const un = opHand.filter(x => x.k == null);
      return { t: 'p6', pick: un.length ? pick(un, rng).u : null };
    }
    if (v.can.eff) {                                     // 効果タイム（第4.190版：1つずつ）：いまの 効果 だけ 決める（第4.202版：5 → 4 だけ。7 の 3まい・3 は セットの 前）
      const c = v.can.eff, s = byS(hand);
      if (c.e5) { const weak = hand.find(x => x.tok) || s[s.length - 1]; return { t: 'eff', use: weak ? { u5: weak.u } : {} }; }      // 1番 弱い 手札を 捨てて 山札から 出す（7・3 は もう 終わって いる。第4.197版：トークンが あれば それ：ターンで 消える）
      if (c.e4) return { t: 'eff', use: (v.turn >= v.turns ? true : v.turn >= 2 ? rng() < 0.5 : false) ? { u4: true } : {} };
      return { t: 'eff', use: {} };
    }
    if (v.phase !== 'set' || !v.can.set) return null;
    if (v.can.x7r) return { t: 'x7r' };                 // 第4.187版：7 が 4まい → セットの 前に 4まい 見せて 逆転（7 が 1番 強く なる）→ その あと セット
    if (v.can.x7 && !rv) return { t: 'x7' };            // 第4.202版：7 が 3まい → セットの 前に 交換（逆転ちゅうの 7 は 強い ので 交換しない）
    if (v.can.x3 && v.can.x3p.length && rng() < (v.turn >= 2 ? 0.55 : 0.35)) return { t: 'x3', pick: pick(v.can.x3p, rng) };      // 第4.202版：3 が 3まい → セットの 前（手の 内を 見せる ので 毎回は 使わない）・もらう カードは 相手の うらの カードから ランダムに 1まい（中身は 見ない）
    const s = byS(hand), left = v.turns - v.turn + 1;          // のこりの ターン（この ターンも 入れて）
    const top = s.slice(0, Math.min(left, s.length));
    if (hand.length - 2 >= v.turns - v.turn && hand.length - 1 >= 1 && v.deckN >= 1) {          // 5 の 効果を ねらう（第4.177版：5 を 出して、手札を 1まい 捨てても のこりの ターンに 足りる）
      const third = top[top.length - 1], five = s.find(x => x.k === '5');
      if (five && P(third.k) >= P('5')) return { t: 'set', u: five.u };
    }
    const knownOp = opHand.filter(x => x.k != null).map(x => x.k);
    let cand = top.filter(x => x.k === 'k' || x.k === 'm' || knownOp.indexOf(x.k) < 0);
    if (!cand.length) cand = top;
    return { t: 'set', u: pick(cand, rng).u };
  }
  return { decide };
})();
if (typeof module !== 'undefined' && module.exports) module.exports = CBCpu;
