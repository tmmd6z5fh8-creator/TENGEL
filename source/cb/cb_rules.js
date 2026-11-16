// 馬カードバトルの ルール（第4.176版・まさちゃん 2026/11/15 21:41「TENGER馬カードバトル」）：画面とは 別の、計算 だけの 部品（node でも 動く：test_cb_rules.js）
//
//   まさちゃんの ルール（21:41 の 文）：
//     ・3ターンで 勝負・手札は 5まい ずつ・カードは 1〜7（同じ 数字が 4まい）＋ 神様馬 1まい ＋ 幻の馬 1まい ＝ 30まい
//     ・強さ：神様馬 と 幻の馬 が 1番・数字は 1 が 1番 強くて 7 が 1番 弱い
//     ・オープンした とき 同じ カード なら、かぶった プレイヤーは その ターン 無条件で 負け
//     ・勝った 枚数が 多い 方の 勝ち・同じ なら 同点
//     ・効果：7＝手札に 3まい そろったら 3まいを 山札に もどして 3まい 引く ／ 6＝手札の 6 を 2まい 見せると 相手の 手札を 1まい 見られる ／
//             5＝セットした あと 手札が 4まい 以上なら、その 5 と 手札 1まいを 捨てて 山札から ランダムに 1まい セット ／
//             4＝最初に 公開すると 相手は セットした カードを 手札の 1まいと 交換する ／ 神様馬＝勝ったら 相手の 手札を 1まい 見る ／
//             幻の馬＝勝ったら 手札を 2まい 捨てて 山札から 2まい まで 引く
//   まさちゃんの 直し（23:12）：
//     ・「このカードをセットする」を 選ぶと、もう カードの 変更は できない
//     ・セットが お互いに 完了したら、カードの 効果を 使うか 選択できる（＝「効果タイム」）
//     ・神様馬と 幻の馬の ように 勝利したら 出てくる 効果は、勝利した 次の ターンの スタートで 使うか 選べる
//   まさちゃんの 直し（23:15）：捨て札は タップすると 確認できる（終わった ターンの 捨て札・効果による 捨て札）→ 捨て札は「だれの・どの ターンの・何で 捨てたか」を 覚える
//   まさちゃんの 直し（第4.177版・2026/11/16 10:40）：
//     ・5 の ルール変更「手札がバトルターンに必要な枚数を切らない場合に発動できる（例:最後のターンに5ともう一枚ある場合、フィールドの5と手札を一枚捨てて効果発動）」
//       ＋ 10:54 の 新しい 5 の 絵「5を表向きにセットした後、その5と手札1枚を捨て、山札からランダムに1枚をフィールドにセットできる。※発動後の手札が、残りターン数より少なくならない場合のみ発動可能。」
//       → 使える 条件：5 を セットして いる・手札が 1まい 以上・山札が 1まい 以上・（手札 − 1）≧ のこりの ターンの 数（＝3 − いまの ターン）。前は「手札が 4まい 以上」＝1ターン目 だけ だった
//     ・3 に 効果追加「手札に3が3枚ある場合、その3枚を相手に見せることで、一枚と、相手の手札からランダムに選んだ一枚を交換できる」（絵：「3枚公開：手札交換」）
//     ・「カードの効果は使うか使わないか選べるようにして！」→ どの 効果も 使うか えらべる（3 の 効果も 効果タイムで 聞く）
//   まさちゃんの 直し（第4.178版・2026/11/16 14:43）：
//     ・「カードバトル５ターン勝負にする 手札7枚にして！」→ TURNS 3 → 5・HAND 5 → 7（山札は 20 → 16まい）
//     ・「6.の効果は、もう見てるカードしかない場合は、発動しなくして！」→ 6 の 効果は、相手の 手札に まだ 見て いない カードが 1まい 以上 ある とき だけ 使える（聞かれない）。
//       見る カードも まだ 見て いない カード だけ（もう 見た カードを えらぶ 手は 受けつけない）
//   まさちゃんの 追加（第4.178版・2026/11/16 15:33「テンゲルカードバトルに追加」と 新しい 1・2 の 絵「3枚公開：逆転勝利」）：
//     ・「1は、手札のフィールドと合わせて3枚を相手見せ、その内、手札の1を1枚捨てることで幻の馬カードと神様馬カードに勝利することができる」
//     ・「2は、手札のフィールドと合わせて3枚を相手見せ、その内、手札の2を1枚捨てることで1に勝利することができる」
//     ・使う とき（姫が 聞いた：A＝オープンした あと／B＝効果タイム）→ まさちゃん 15:41「A、オープンしてから」
//       ＝オープンして 負けた 人が、場に 出した 1（相手＝神様馬・幻の馬）か 2（相手＝1）と 同じ 数字を 手札に 2まい 以上 持って いたら「使う？」と 聞く（phase 'rev'）。
//         使う → 手札の 2まいを 相手に 見せて（場の 1まいと 合わせて 3まい）、その 1まいを 捨てる → その ターンは 勝ち
//   まさちゃんの 直し（第4.181版・2026/11/16 19:05）：
//     ・「4をお互いに出して効果を発動した場合、ドローになる」→ 2人とも 4 を セットして 2人とも 4 の 効果を 使ったら、打ち消し（交換なし）→ その ターンは ドロー
//       （引き分け＝'tie'：どちらの 勝ちにも 数えない。open の ev と S.last に d4）。前は 4 と 4 の かぶり（どちらも 負け）。
//       2人とも 使わない ときは いまも かぶり・1人 だけ 使う ときは 相手が 交換（前と 同じ）
//     ・「お互いにカードの効果は、カードを伏せてセットしてから、効果を使うか使わないか申告して、オープンする」→ 姫が 聞いた
//       （効果が ない 人にも 毎ターン 聞く？・神様馬／幻の馬も 伏せて から？）→「いまの流れのままでOK」＝ 流れは 下の まま
//
//   1ターンの 流れ：
//     （はじめ：前の ターンに 神様馬／幻の馬で 勝った 人が 効果を 使うか 決める＝phase 'pre'）
//     → セット（2人とも 1まい ずつ ふせる。出したら 確定＝phase 'set'）
//     → 効果タイム（使える 効果が ある 人が 使うか 決める。2人とも 決めて から いっしょに 行う＝phase 'eff'。だれも 使える 効果が なければ とばす）
//     → （4 の 効果が 出たら 相手が 交換＝phase 'swap'。2人とも 4 の 効果なら 打ち消して ドロー：第4.181版）→ オープン
//     → （負けた 人が 1・2 の「逆転勝利」を 使える なら、使うか 決める＝phase 'rev'。勝ち負けを 数えるのは 決めた あと）→ 捨て札へ → 次の ターン
//
//   姫が 決めた 所（ルールの 文に ない 所。README と 報告に 書く）：
//     ・神様馬 と 幻の馬 が ぶつかったら 引き分け（どちらの 勝ちにも 数えない）。同じ 数字が ぶつかったら どちらも 負け（どちらの 勝ちにも 数えない）
//     ・5ターン ぜんぶ やる（先に 3勝 しても さいごの ターンまで やる：第4.176版の「3ターン ぜんぶ やる」と 同じ 考え方）。ターンの あいだに 山札から 引かない（引くのは 効果 だけ）
//     ・効果タイムで えらぶのは 7・6・5・4・3 の 5つ とも（手札の 効果の 7・6・3 も ここ。手札は「セットした あと」の 手札で 数える）
//     ・効果タイムは 2人とも 決めて から いっしょに 行う（相手が 何を 使うか 見て から 決める ことは できない）。行う 順は 6 → 5 → 7 → 3 → 4（同じ 効果は 2人 いっしょ）
//     ・3（第4.177版）：見せた 3 の うち 相手に わたす 1まいは どれでも 同じ（ぜんぶ 3）なので はじめの 1まい。相手の 手札からは くじで 1まい（えらべない）。
//         見せた 3まいは 相手に「知られた カード」に なる（手札に のこる 2まい）。わたした 3 は 自分が 知って いる（相手の 手札の 中で 表に 見える）。もらった カードは 相手が 知って いる（目の しるし）。
//         5 の 効果で 3 を 捨てて 3まい なくなる ときは いっしょに 使えない。3 は 4まい しか ない ので、2人が 同時に 使う ことは ない
//     ・7：先に 3まい 引いて から 7 を 山札に もどして まぜる（もどした 7 を すぐ 引き直さない ＝ かならず「新しく 3まい」）
//     ・6：見る カードは 決める ときに えらぶ。見せた 6 の 2まいは 相手に「知られた カード」に なる
//         第4.178版：神様馬の 効果（勝った 次の ターンの はじめに 相手の 手札を 1まい 見る）も 同じ 考え方に した ＝ 相手の 手札が ぜんぶ もう 見た カードなら 聞かれない（見る ものが ない）
//     ・5：手札の 数は「5 を セットした あと」で 数える。「残りターン数」は いまの ターンの あとに のこる ターンの 数（5ターンの とき：1ターン目 4・…・5ターン目 0）。
//         ＝ 使った あとの 手札（手札 − 1）が、のこりの ターンで 出す 数より 少なく ならない とき だけ 使える（さいごの ターンは 手札が 1まい あれば 使える：まさちゃんの 例）。
//         手札 7まい・5ターン ＝ よぶんは 2まい → 5 の 効果は ふつう 1回の 対戦で 2回 まで（ほかの 効果で 手札が ふえて いなければ）。
//         山札から 来た カードは オープンまで だれにも 見えない（自分にも）。捨てた 5 と 手札は 捨て札で 2人とも 見える（＝5 は 表に なる）
//     ・4：両方が 4 の 効果を 使ったら 打ち消し（交換なし）→ 第4.181版から その ターンは ドロー（前は 4 と 4 で どちらも 負け）。交換で もどった カードは 手札に 入る
//     ・神様馬・幻の馬の 効果は 使わなくても いい。さいごの ターンに 勝った ときは 出ない（次の ターンが ない）。幻の馬は ちょうど 2まい 捨てて 引ける だけ（2まい まで）引く
//     ・「見た カード」は その カードが 相手の 手札に ある あいだ 覚えて いる（そのカードが 場に 出たら、場の カードが 何か わかる）
//     ・逆転勝利（1・2：第4.178版）：
//         場の カードは オープンで もう 見えて いる ので、「3まい 見せる」＝手札の 同じ 数字 2まいを 見せる。見せる 2まいは、もう 相手に 知られて いる カードから（新しく 知られる カードを 少なく）。
//         捨てるのは その うちの 1まい（どれも 同じ 数字）。手札に のこる 1まいは 相手に「知られた カード」に なる
//         5 と 同じ 考え方で、捨てた あとの 手札が のこりの ターンの 数より 少なく なる ときは 使えない（聞かれない）：あとの ターンに 出す カードが なくなる ため
//         逆転で 負けに なった 神様馬・幻の馬の「勝ったら」の 効果は 出ない（勝って いない）。使わなければ そのまま 負け（相手の 神様馬・幻の馬の 効果は いつも どおり）
//         2 の 効果で 負けに なった 1 は やり返せない（1 の 効果は 神様馬・幻の馬に だけ）＝ 1ターンに 逆転勝利を 使えるのは 1人 だけ
//         山札から 来た カード（5 の 効果）・交換で 出した カード（4 の 効果）が 1・2 でも 同じ（オープンした ときの 場の カードで 決める）
//
//   部品：
//     CBRules.newGame(rng, opt) → S（対戦の 中身 ぜんぶ：ホスト だけが 持つ）   opt.hands＝[[手札],[手札]]・opt.deck＝[上から …]・opt.turns＝ターンの 数（どれも テスト用：ふだんは 7まい・5ターン）
//     CBRules.act(S, i, a)      → { ok, why, ev }：プレイヤー i（0／1）の 手 a を S に 入れる（ev＝おきた こと）
//        a＝{ t:'set', u } ／ { t:'eff', use:{ p6:見る カード, u5:捨てる カード, x7:true, x3:true, u4:true }（使う もの だけ。使わない＝null か {}）} ／ { t:'swap', u } ／
//           { t:'k', pick:u|null } ／ { t:'m', drop:[u,u]|null } ／ { t:'rev', use:true|false }（逆転勝利）
//     CBRules.view(S, i)        → プレイヤー i に 見せて いい こと だけ（相手の 手札・ふせた カードは 見えない）
//     CBRules.evFor(ev, i)      → おきた こと の うち、プレイヤー i に 見せて いい 形
const CBRules = (() => {
  'use strict';
  const NUMS = ['1', '2', '3', '4', '5', '6', '7'], KINDS = NUMS.concat(['k', 'm']);
  const TURNS = 5, HAND = 7, COPIES = 4;      // 第4.178版：5ターン・手札 7まい（前は 3ターン・5まい）
  const power = k => (k === 'k' || k === 'm' ? 0 : +k);          // 小さい ほど 強い（神様馬・幻の馬＝0）
  // 2まいを くらべる：0＝a の 勝ち・1＝b の 勝ち・'clash'＝同じ カード（どちらも 負け）・'tie'＝神様馬 と 幻の馬（引き分け）
  function compare(a, b) {
    if (a === b) return 'clash';
    const pa = power(a), pb = power(b);
    return pa === pb ? 'tie' : pa < pb ? 0 : 1;
  }
  function shuffle(a, rng) {
    for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(rng() * (i + 1)), t = a[i]; a[i] = a[j]; a[j] = t; }
    return a;
  }
  const fullSet = () => { const a = []; NUMS.forEach(k => { for (let i = 0; i < COPIES; i++) a.push(k); }); a.push('k', 'm'); return a; };
  const mkP = () => ({ hand: [], set: null, wins: 0, known: [], eff: null });
  const count = (hand, k) => hand.reduce((n, c) => n + (c.k === k ? 1 : 0), 0);
  const idx = (hand, u) => hand.findIndex(c => c.u === u);

  function newGame(rng, opt) {
    rng = rng || Math.random; opt = opt || {};
    const tn = Math.floor(+opt.turns);
    const S = { v: 3, turn: 1, turns: tn >= 1 && tn <= 9 ? tn : TURNS, phase: 'set', uid: 0, deck: [], discard: [], p: [mkP(), mkP()], pend: null, win: null, last: null, res: null };
    let rest = fullSet();
    const take = k => { const j = rest.indexOf(k); if (j < 0) throw new Error('card ' + k); rest.splice(j, 1); return k; };
    if (opt.hands) {
      const hs = opt.hands.map(h => h.map(take));
      let dk;
      if (opt.deck) { dk = opt.deck.map(take); shuffle(rest, rng); dk = dk.concat(rest); } else dk = shuffle(rest, rng);
      // 山札は 配列の 後ろが 上（pop で 引く）：dk は「上から」の 順
      for (let i = 0; i < 2; i++) S.p[i].hand = hs[i].map(k => ({ u: ++S.uid, k }));
      S.deck = dk.slice().reverse().map(k => ({ u: ++S.uid, k }));
    } else {
      S.deck = shuffle(rest, rng).map(k => ({ u: ++S.uid, k }));
      for (let n = 0; n < HAND; n++) for (let i = 0; i < 2; i++) S.p[i].hand.push(S.deck.pop());      // 1まい ずつ 交互に 配る
    }
    return S;
  }

  const forget = (S, u) => { S.p.forEach(P => { const j = P.known.indexOf(u); if (j >= 0) P.known.splice(j, 1); }); };
  const learn = (P, u) => { if (P.known.indexOf(u) < 0) P.known.push(u); };
  // 捨て札へ：だれの（by）・何で 捨てたか（why：'t'＝ターンに 出した カード・'5'＝5 の 効果・'m'＝幻の馬の 効果・'1'／'2'＝逆転勝利で 捨てた 1／2）・どの ターンか を 覚える
  const toss = (S, c, by, why) => { forget(S, c.u); S.discard.push({ u: c.u, k: c.k, by: by, why: why, turn: S.turn }); };

  // 相手（Q）の 手札の 中で、P が まだ 見て いない カード（第4.178版：6・神様馬の 効果で 見られる カード）
  const unseen = (P, Q) => Q.hand.filter(c => P.known.indexOf(c.u) < 0);
  // 効果タイムで 使える 効果（2人とも セットした あとの 手札と 場で 数える）
  function canEff(S, i) {
    const P = S.p[i], Q = S.p[1 - i], sk = P.set ? P.set.c.k : null;
    return {
      e6: count(P.hand, '6') >= 2 && unseen(P, Q).length >= 1,                                                  // 第4.178版：もう 見た カード しか ない ときは 使えない
      e5: sk === '5' && P.hand.length >= 1 && P.hand.length - 1 >= S.turns - S.turn && S.deck.length >= 1,      // 第4.177版：使った あとの 手札が のこりの ターンの 数より 少なく ならない
      e7: count(P.hand, '7') >= 3 && S.deck.length >= 3,
      e3: count(P.hand, '3') >= 3 && Q.hand.length >= 1,                                                        // 第4.177版：3 が 3まい → 見せて 交換
      e4: sk === '4' && Q.hand.length >= 1
    };
  }
  const any = c => c.e6 || c.e5 || c.e7 || c.e3 || c.e4;
  // 逆転勝利（第4.178版）を 使える 人の 席（いなければ null）。r＝オープンして ふつうに くらべた 結果（0／1＝勝った 席）
  //   負けた 人の 場の カードが 1（相手＝神様馬・幻の馬）か 2（相手＝1）・手札に 同じ 数字が 2まい 以上（場と 合わせて 3まい）・1まい 捨てても のこりの ターンに 足りる
  function revWho(S, r) {
    if (r !== 0 && r !== 1) return null;
    const i = 1 - r, P = S.p[i], mk = P.set.c.k, wk = S.p[r].set.c.k;
    const hit = (mk === '1' && (wk === 'k' || wk === 'm')) || (mk === '2' && wk === '1');
    return hit && count(P.hand, mk) >= 2 && P.hand.length - 1 >= S.turns - S.turn ? i : null;
  }
  const NOUSE = () => ({ p6: null, u5: null, x7: false, x3: false, u4: false });

  function act(S, i, a, rng) {
    rng = rng || Math.random;
    const ev = [], bad = why => ({ ok: false, why: why, ev: [] });
    if (!S || (i !== 0 && i !== 1) || !a || typeof a !== 'object') return bad('arg');
    if (S.phase === 'end') return bad('end');
    const P = S.p[i], Q = S.p[1 - i];
    if (a.t === 'set') {                                 // ふせて セット（出したら 確定：もう 変えられない）
      if (S.phase !== 'set' || P.set) return bad('set');
      const j = idx(P.hand, a.u); if (j < 0) return bad('card');
      const c = P.hand.splice(j, 1)[0];
      P.set = { c: c, up: false, blind: false, open: false };
      ev.push({ e: 'set', who: i, u: c.u });
      if (S.p[0].set && S.p[1].set) afterSet(S, ev);
      return { ok: true, ev: ev };
    }
    if (a.t === 'eff') {                                 // 効果タイム：使う 効果を 決める（まとめて 1回。相手には「決めた」こと だけ 伝わる）
      if (S.phase !== 'eff' || !P.eff || P.eff.done) return bad('eff');
      const can = P.eff.can, w = a.use && typeof a.use === 'object' ? a.use : {}, use = NOUSE();
      if (w.p6 != null) { if (!can.e6) return bad('e6'); if (idx(Q.hand, w.p6) < 0 || P.known.indexOf(w.p6) >= 0) return bad('pick'); use.p6 = w.p6; }      // 見るのは まだ 見て いない カード だけ
      if (w.u5 != null) { if (!can.e5) return bad('e5'); if (idx(P.hand, w.u5) < 0) return bad('drop'); use.u5 = w.u5; }
      if (w.x7) {                                        // 5 の 効果で 7 を 捨てる なら、のこりの 7 が 3まい いる
        if (!can.e7 || count(P.hand.filter(c => c.u !== use.u5), '7') < 3) return bad('e7');
        use.x7 = true;
      }
      if (w.x3) {                                        // 5 の 効果で 3 を 捨てる なら、のこりの 3 が 3まい いる
        if (!can.e3 || count(P.hand.filter(c => c.u !== use.u5), '3') < 3) return bad('e3');
        use.x3 = true;
      }
      if (w.u4) { if (!can.e4) return bad('e4'); use.u4 = true; }
      P.eff.use = use; P.eff.done = true;
      ev.push({ e: 'effd', who: i });
      if (S.p[0].eff.done && S.p[1].eff.done) resolve(S, ev, rng);
      return { ok: true, ev: ev };
    }
    if (a.t === 'swap') {                                // 相手の 4 の 効果：セットした カードを 手札の 1まいと 交換
      if (S.phase !== 'swap' || !S.pend || S.pend.who !== i) return bad('swap');
      const j = idx(P.hand, a.u); if (j < 0) return bad('card');
      const old = P.set.c, c = P.hand.splice(j, 1)[0];
      P.hand.push(old);
      P.set = { c: c, up: false, blind: false, open: false };
      S.pend = null;
      ev.push({ e: 'swap', who: i, u: c.u, back: old.u });
      open(S, ev);
      return { ok: true, ev: ev };
    }
    if (a.t === 'k') {                                   // 前の ターンに 神様馬で 勝った：相手の 手札を 1まい 見る（null＝使わない）
      if (S.phase !== 'pre' || !S.pend || S.pend.type !== 'k' || S.pend.who !== i) return bad('k');
      if (a.pick == null) ev.push({ e: 'kskip', who: i });
      else {
        const j = idx(Q.hand, a.pick); if (j < 0 || P.known.indexOf(a.pick) >= 0) return bad('pick');      // 見るのは まだ 見て いない カード だけ（第4.178版）
        learn(P, Q.hand[j].u);
        ev.push({ e: 'k', who: i, pick: Q.hand[j].u, k: Q.hand[j].k });
      }
      S.pend = null; S.phase = 'set';
      return { ok: true, ev: ev };
    }
    if (a.t === 'm') {                                   // 前の ターンに 幻の馬で 勝った：手札を 2まい 捨てて、2まい まで 引く（null＝使わない）
      if (S.phase !== 'pre' || !S.pend || S.pend.type !== 'm' || S.pend.who !== i) return bad('m');
      if (a.drop == null) ev.push({ e: 'mskip', who: i });
      else {
        if (!Array.isArray(a.drop) || a.drop.length !== 2 || a.drop[0] === a.drop[1]) return bad('drop');
        const j0 = idx(P.hand, a.drop[0]), j1 = idx(P.hand, a.drop[1]); if (j0 < 0 || j1 < 0) return bad('drop');
        const out = [P.hand[j0], P.hand[j1]];
        P.hand = P.hand.filter(c => out.indexOf(c) < 0);
        out.forEach(c => toss(S, c, i, 'm'));
        const drew = []; while (drew.length < 2 && S.deck.length) drew.push(S.deck.pop());
        drew.forEach(c => P.hand.push(c));
        ev.push({ e: 'm', who: i, drop: out.map(c => ({ u: c.u, k: c.k })), drew: drew.map(c => ({ u: c.u, k: c.k })) });
      }
      S.pend = null; S.phase = 'set';
      return { ok: true, ev: ev };
    }
    if (a.t === 'rev') {                                 // 逆転勝利（1・2 の 効果）：オープンして 負けた 人が 使うか 決める（use:true＝使う）
      if (S.phase !== 'rev' || !S.pend || S.pend.type !== 'rev' || S.pend.who !== i) return bad('rev');
      let r = S.pend.res;
      if (a.use) {
        const k = P.set.c.k, kn = c => (Q.known.indexOf(c.u) >= 0 ? 1 : 0);
        const same = P.hand.filter(c => c.k === k).sort((x, y) => kn(y) - kn(x) || x.u - y.u);      // もう 知られて いる カードを 先に 見せる
        if (same.length < 2) return bad('rev');
        const drop = same[0], keep = same[1];
        P.hand.splice(P.hand.indexOf(drop), 1); toss(S, drop, i, k);
        learn(Q, keep.u);                                // 見せて 手札に のこった 1まいは 相手が 知って いる
        r = i;
        ev.push({ e: 'rev', who: i, k: k, show: [drop.u, keep.u], drop: { u: drop.u, k: drop.k }, beat: Q.set.c.k });
      } else ev.push({ e: 'revskip', who: i });
      S.pend = null;
      score(S, r, !!a.use);
      ev.push({ e: 'fin', turn: S.turn, res: r, wins: [S.p[0].wins, S.p[1].wins], rev: !!a.use });
      endTurn(S, ev);
      return { ok: true, ev: ev };
    }
    return bad('type');
  }

  // 2人とも セットした：使える 効果が ある 人が いれば 効果タイム・いなければ そのまま オープン
  function afterSet(S, ev) {
    const c0 = canEff(S, 0), c1 = canEff(S, 1);
    if (!any(c0) && !any(c1)) { open(S, ev); return; }
    S.phase = 'eff';
    S.p[0].eff = { can: c0, done: !any(c0), use: null };
    S.p[1].eff = { can: c1, done: !any(c1), use: null };
    ev.push({ e: 'efft', has: [any(c0), any(c1)] });
  }
  // 2人とも 決めた：6 → 5 → 7 → 3 → 4 の 順に 行う（その とき もう できなく なって いたら 不発：fizz）
  function resolve(S, ev, rng) {
    const U = S.p.map(P => (P.eff && P.eff.use) || NOUSE());
    [0, 1].forEach(i => {                                // 6：2まい 見せて、相手の 手札を 1まい 見る
      const P = S.p[i], Q = S.p[1 - i]; if (U[i].p6 == null) return;
      const j = idx(Q.hand, U[i].p6), six = P.hand.filter(c => c.k === '6').slice(0, 2);
      if (j < 0 || six.length < 2) { ev.push({ e: 'fizz', who: i, k: '6' }); return; }      // えらんだ カードが 同じ 効果タイムの 中で 先に 見えた（相手が 6 の 効果で 見せた 6）ときも、そのまま 行う（不発に しない）
      six.forEach(c => learn(Q, c.u));
      learn(P, Q.hand[j].u);
      ev.push({ e: 'p6', who: i, six: six.map(c => c.u), pick: Q.hand[j].u, k: Q.hand[j].k });
    });
    [0, 1].forEach(i => {                                // 5：セットした 5 と 手札 1まいを 捨てて、山札の 上を ふせて セット
      const P = S.p[i]; if (U[i].u5 == null) return;
      const d = idx(P.hand, U[i].u5);
      if (d < 0 || !P.set || P.set.c.k !== '5' || S.deck.length < 1) { ev.push({ e: 'fizz', who: i, k: '5' }); return; }
      const five = P.set.c, drop = P.hand.splice(d, 1)[0];
      toss(S, five, i, '5'); toss(S, drop, i, '5');
      P.set = { c: S.deck.pop(), up: false, blind: true, open: false };
      ev.push({ e: 'u5', who: i, five: { u: five.u, k: five.k }, drop: { u: drop.u, k: drop.k } });
    });
    [0, 1].forEach(i => {                                // 7：3まい 引いて、7 を 3まい 山札に もどす
      const P = S.p[i]; if (!U[i].x7) return;
      const back = P.hand.filter(c => c.k === '7').slice(0, 3);
      if (back.length < 3 || S.deck.length < 3) { ev.push({ e: 'fizz', who: i, k: '7' }); return; }
      P.hand = P.hand.filter(c => back.indexOf(c) < 0);
      const drew = [S.deck.pop(), S.deck.pop(), S.deck.pop()];
      drew.forEach(c => P.hand.push(c));
      back.forEach(c => { forget(S, c.u); S.deck.push({ u: ++S.uid, k: c.k }); });      // もどした カードは 新しい 番号（どれが もどした 7 か 追えない ように）
      shuffle(S.deck, rng);
      ev.push({ e: 'x7', who: i, n: 3, drew: drew.map(c => ({ u: c.u, k: c.k })) });
    });
    [0, 1].forEach(i => {                                // 3（第4.177版）：3 を 3まい 見せて、その 1まいと 相手の 手札の 1まい（くじ）を 交換
      const P = S.p[i], Q = S.p[1 - i]; if (!U[i].x3) return;
      const three = P.hand.filter(c => c.k === '3').slice(0, 3);
      if (three.length < 3 || Q.hand.length < 1) { ev.push({ e: 'fizz', who: i, k: '3' }); return; }
      const give = three[0], take = Q.hand[Math.floor(rng() * Q.hand.length)];
      P.hand.splice(P.hand.indexOf(give), 1); Q.hand.splice(Q.hand.indexOf(take), 1);
      P.hand.push(take); Q.hand.push(give);
      forget(S, give.u); forget(S, take.u);              // 持ち主が かわった：前の「知って いる」は 消して から 入れ直す
      three.slice(1).forEach(c => learn(Q, c.u));        // 見せた 3（手札に のこる 2まい）は 相手が 知って いる
      learn(P, give.u);                                  // わたした 3 は 自分が 知って いる（相手の 手札の 中）
      learn(Q, take.u);                                  // もらった カードは 相手が 知って いる（もとは 相手の カード）
      ev.push({ e: 'x3', who: i, three: three.map(c => c.u), give: { u: give.u, k: give.k }, take: { u: take.u, k: take.k } });
    });
    S.p.forEach(P => { P.eff = null; });
    const A = S.p[0], B = S.p[1], f0 = U[0].u4 && A.set.c.k === '4', f1 = U[1].u4 && B.set.c.k === '4';      // 4：先に 見せて、相手に 交換させる
    if (f0 && f1) { A.set.up = B.set.up = true; ev.push({ e: 'first2' }); open(S, ev, true); return; }      // 両方：打ち消し → ドロー（第4.181版：まさちゃん 19:05「4をお互いに出して効果を発動した場合、ドローになる」）
    if (f0 || f1) {
      const w = f0 ? 0 : 1, F = S.p[w], O = S.p[1 - w];
      F.set.up = true;
      ev.push({ e: 'first', who: w });
      if (O.hand.length >= 1) { S.phase = 'swap'; S.pend = { type: 'swap', who: 1 - w }; return; }
    }
    open(S, ev);
  }
  // d4＝2人とも 4 の 効果を 使った（第4.181版：くらべずに ドロー＝'tie'。逆転勝利も 出ない）
  function open(S, ev, d4) {
    const c0 = S.p[0].set.c, c1 = S.p[1].set.c, r = d4 ? 'tie' : compare(c0.k, c1.k), cs = [{ u: c0.u, k: c0.k }, { u: c1.u, k: c1.k }];
    S.p.forEach(P => { P.set.up = true; P.set.blind = false; P.set.open = true; P.eff = null; });
    const rv = revWho(S, r);
    if (rv != null) {                                    // 逆転勝利（第4.178版）：負けた 人が 使うか 決める まで、勝ち負けは 数えない（wins は 前の まま・rev＝聞かれる 席）
      S.phase = 'rev'; S.pend = { type: 'rev', who: rv, res: r };
      ev.push({ e: 'open', turn: S.turn, c: cs, res: r, wins: [S.p[0].wins, S.p[1].wins], rev: rv });
      return;
    }
    score(S, r, false, d4);
    ev.push(Object.assign({ e: 'open', turn: S.turn, c: cs, res: r, wins: [S.p[0].wins, S.p[1].wins] }, d4 ? { d4: true } : {}));
    endTurn(S, ev);
  }
  // この ターンの 勝ち負けを 数える（r＝0／1＝勝った 席・'clash'・'tie'。rev＝逆転勝利で 決まった・d4＝2人とも 4 の 効果で ドロー：第4.181版）
  function score(S, r, rev, d4) {
    const c0 = S.p[0].set.c, c1 = S.p[1].set.c;
    if (r === 0 || r === 1) S.p[r].wins += 1;
    S.last = { turn: S.turn, c: [c0.k, c1.k], res: r, rev: !!rev, d4: !!d4 };
    // 神様馬・幻の馬で 勝った：次の ターンの はじめに 効果を 使うか 決める（さいごの ターンは 次が ない ので 出ない。逆転で 負けた ときは 勝って いない ので 出ない）
    S.win = null;
    if ((r === 0 || r === 1) && S.turn < S.turns) { const wk = r === 0 ? c0.k : c1.k; if (wk === 'k' || wk === 'm') S.win = { type: wk, who: r }; }
  }
  function endTurn(S, ev) {
    S.p.forEach((P, i) => { if (P.set) { toss(S, P.set.c, i, 't'); P.set = null; } P.eff = null; });
    S.pend = null;
    ev.push({ e: 'clear' });
    if (S.turn >= S.turns) {
      const a = S.p[0].wins, b = S.p[1].wins;
      S.phase = 'end'; S.res = a > b ? 0 : b > a ? 1 : 'draw';
      ev.push({ e: 'end', wins: [a, b], res: S.res });
      return;
    }
    S.turn += 1; S.phase = 'set';
    ev.push({ e: 'turn', n: S.turn });
    const w = S.win; S.win = null;
    if (w) {
      const Wn = S.p[w.who], Ls = S.p[1 - w.who];
      if ((w.type === 'k' && unseen(Wn, Ls).length >= 1) || (w.type === 'm' && Wn.hand.length >= 2 && S.deck.length >= 1)) {      // 神様馬：まだ 見て いない カードが ある とき だけ（第4.178版）
        S.phase = 'pre'; S.pend = { type: w.type, who: w.who };
        ev.push({ e: 'pre', who: w.who, type: w.type });
      }
    }
  }

  // プレイヤー i に 見せて いい こと
  function view(S, i) {
    const P = S.p[i], Q = S.p[1 - i];
    const setOf = (X, mine) => {
      if (!X.set) return null;
      const c = X.set.c, o = { u: c.u, k: null, up: X.set.up, blind: X.set.blind, open: !!X.set.open };
      if (mine) o.k = X.set.blind ? null : c.k;
      else if (X.set.up || (!X.set.blind && P.known.indexOf(c.u) >= 0)) o.k = c.k;
      return o;
    };
    const ce = S.phase === 'eff' && P.eff && !P.eff.done ? P.eff.can : null;
    return {
      v: 3, me: i, turn: S.turn, turns: S.turns, phase: S.phase, deckN: S.deck.length,
      discard: S.discard.map(d => ({ k: d.k, mine: d.by === i, why: d.why, turn: d.turn })),
      my: { hand: P.hand.map(c => ({ u: c.u, k: c.k, seen: Q.known.indexOf(c.u) >= 0 })), set: setOf(P, true), wins: P.wins },
      op: { hand: Q.hand.map(c => ({ u: c.u, k: P.known.indexOf(c.u) >= 0 ? c.k : null })), set: setOf(Q, false), wins: Q.wins },
      can: { set: S.phase === 'set' && !P.set, eff: ce ? { e6: ce.e6, e5: ce.e5, e7: ce.e7, e3: ce.e3, e4: ce.e4 } : null },
      pend: S.pend ? { type: S.pend.type, mine: S.pend.who === i } : null,
      wait: (S.phase === 'set' && !!P.set && !Q.set) || (S.phase === 'eff' && !!P.eff && P.eff.done && !!Q.eff && !Q.eff.done) || (!!S.pend && S.pend.who !== i),
      last: S.last ? { turn: S.last.turn, c: i === 0 ? S.last.c.slice() : [S.last.c[1], S.last.c[0]], res: S.last.res === 0 || S.last.res === 1 ? (S.last.res === i ? 'win' : 'lose') : S.last.res, rev: !!S.last.rev, d4: !!S.last.d4 } : null,
      res: S.phase === 'end' ? (S.res === 'draw' ? 'draw' : S.res === i ? 'win' : 'lose') : null
    };
  }

  // おきた こと を プレイヤー i に 見せて いい 形に（who は「自分か」に する：me）
  function evFor(ev, i) {
    return ev.map(x => {
      const o = { e: x.e };
      if (x.who != null) o.me = x.who === i;
      if (x.e === 'x7') { o.n = x.n; if (x.who === i) o.drew = x.drew; }
      else if (x.e === 'set' || x.e === 'swap') { if (x.who === i) { o.u = x.u; if (x.back != null) o.back = x.back; } }
      else if (x.e === 'efft') { o.mine = x.has[i]; o.other = x.has[1 - i]; }
      else if (x.e === 'p6') { o.six = x.six; o.pick = x.pick; if (x.who === i) o.k = x.k; }
      else if (x.e === 'u5') { o.five = x.five; o.drop = x.drop; }
      else if (x.e === 'x3') { o.three = x.three; o.give = x.give; o.take = x.take; }      // 見せた 3まい・わたした 3・もらった カード：2人とも 知って いる（もらった カードは もとの 持ち主も 知って いる）
      else if (x.e === 'fizz') o.k = x.k;
      else if (x.e === 'open') { o.turn = x.turn; o.my = x.c[i]; o.op = x.c[1 - i]; o.res = x.res === 0 || x.res === 1 ? (x.res === i ? 'win' : 'lose') : x.res; o.wins = [x.wins[i], x.wins[1 - i]]; if (x.rev != null) o.rev = x.rev === i ? 'me' : 'op'; if (x.d4) o.d4 = true; }      // rev＝逆転勝利を 使えるのは 自分か 相手か（ある とき：勝ち負けは まだ 決まって いない）
      else if (x.e === 'rev') { o.k = x.k; o.show = x.show; o.drop = x.drop; o.beat = x.beat; }      // 逆転勝利：見せた 2まい・捨てた 1まいは 2人とも 見える
      else if (x.e === 'fin') { o.turn = x.turn; o.res = x.res === i ? 'win' : 'lose'; o.wins = [x.wins[i], x.wins[1 - i]]; o.rev = !!x.rev; }
      else if (x.e === 'pre') o.type = x.type;
      else if (x.e === 'k') { o.pick = x.pick; if (x.who === i) o.k = x.k; }
      else if (x.e === 'm') { o.drop = x.drop; o.n = x.drew.length; if (x.who === i) o.drew = x.drew; }
      else if (x.e === 'turn') o.n = x.n;
      else if (x.e === 'end') { o.wins = [x.wins[i], x.wins[1 - i]]; o.res = x.res === 'draw' ? 'draw' : x.res === i ? 'win' : 'lose'; }
      return o;
    });
  }

  // いま プレイヤー i が 打てる 手の 種類（テスト・コンピュータ用）
  function legal(S, i) {
    const v = view(S, i), out = [];
    if (v.can.set) out.push('set');
    if (v.can.eff) out.push('eff');
    if (v.pend && v.pend.mine) out.push(v.pend.type);
    return out;
  }

  return { NUMS, KINDS, TURNS, HAND, COPIES, power, compare, shuffle, newGame, act, view, evFor, legal };
})();
if (typeof module !== 'undefined' && module.exports) module.exports = CBRules;
