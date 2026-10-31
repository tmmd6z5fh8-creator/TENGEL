// ポイントの台帳（points.js）のテスト：node test_points.js
//   残高（買ったP・サブスクのP・もらったP）・使う順（サブスク→パック→無償）・サブスクの期限（30日）・同じ取引を2回足さない・返金・
//   使ったPは1日1件にまとめる・解放・ミッション（8〜300・以降100ごと）・読み直しの見分け方（同じレース）
const P = require('./points.js');
let fails = [];
function check(c, label) { console.log((c ? '  ✅ ' : '  ❌ ') + label); if (!c) fails.push(label); }
const D = (s) => new Date(s + 'T03:00:00Z').toISOString();
const tx = (id, product, date) => ({ id, originalId: 'o' + id, product, date: D(date) });

// 初回プレゼント
let ev = [P.giftEvent(D('2026-11-01'))];
let B = P.balance(ev, D('2026-11-01'));
check(B.total === 1500 && B.free === 1500 && B.paid_pack === 0 && B.paid_sub === 0, '初回プレゼント 1,500P は無償の枠');
// パックを買う → 同じ取引は2回足さない
ev.push(P.txEvent(ev, tx('100', 'jp.tengel.app.points1000', '2026-11-02')));
check(P.txEvent(ev, tx('100', 'jp.tengel.app.points1000', '2026-11-02')) === null, '同じ取引（tx-100）は2回足さない');
B = P.balance(ev, D('2026-11-02'));
check(B.total === 2500 && B.paid_pack === 1000, 'パック 1,000P は買ったPの枠');
// サブスク（4,400P・うち400Pおまけ）→ 期限は届いた日＋30日
const sub = P.txEvent(ev, tx('200', 'jp.tengel.app.sub4400', '2026-11-03')); ev.push(sub);
check(sub.kind === 'sub' && sub.amount === 4400 && sub.bonus === 400 && sub.expires === P.addDays(D('2026-11-03'), 30), 'サブスク 4,400P（うち400P）・期限は30日後');
B = P.balance(ev, D('2026-11-03'));
check(B.total === 6900 && B.paid_sub === 4400 && B.paidIn === 5400 && B.freeIn === 1500, '合計 6,900P（買ったP 5,400・もらったP 1,500）');
// 使う順：サブスク → パック → 無償
let pl = P.plan(ev, 200, D('2026-11-04'));
check(pl.ok && pl.use.paid_sub === 200 && pl.use.paid_pack === 0 && pl.use.free === 0, '200P はサブスクのPから');
ev = P.spend(ev, 200, '読み込み 10/10 8R', 'dev1', '2026-11-04T05:00:00.000Z');
let ev2 = P.spend(ev, 200, '読み込み 10/10 9R', 'dev1', D('2026-11-04'));
const spends = ev2.filter(e => e.kind === 'spend');
check(spends.length === 1 && spends[0].amount === -400 && spends[0].use.paid_sub === 400 && spends[0].what.length === 2 && spends[0].id === 'spend-dev1-2026-11-04', '同じ日の使ったPは1件にまとめる（-400P・2つ）');
ev = ev2;
pl = P.plan(ev, 5000, D('2026-11-05'));
check(pl.ok && pl.use.paid_sub === 4000 && pl.use.paid_pack === 1000 && pl.use.free === 0, '5,000P はサブスクの残り4,000 → パック1,000');
check(!P.plan(ev, 7000, D('2026-11-05')).ok && P.plan(ev, 7000, D('2026-11-05')).short === 500, '7,000P は500P足りない（マイナスにしない）');
check(P.spend(ev, 7000, 'x', 'dev1', D('2026-11-05')) === null, '足りないときは使えない');
// 期限：30日たつとサブスクの残りは消える（パック・無償は残る）
B = P.balance(ev, D('2026-12-04'));
check(B.paid_sub === 0 && B.lost === 4000 && B.paid_pack === 1000 && B.free === 1500 && B.total === 2500, '30日後：サブスクの残り4,000Pは消える・パックと無償は残る');
check(P.balance(ev, D('2026-12-02')).paid_sub === 4000 && P.balance(ev, D('2026-12-02')).nextExpire === sub.expires, '期限の前なら残っている・いちばん近い期限');
// 繰り越し：次の月のPが届いても、前の月の残りは期限（30日）まで使える。期限が切れた lot からは引かない
let ev3 = ev.concat([P.txEvent(ev, tx('201', 'jp.tengel.app.sub4400', '2026-12-01'))]);
B = P.balance(ev3, D('2026-12-02'));
check(B.paid_sub === 8400, '12/2：前の月の残り4,000＋新しい4,400＝8,400P（繰り越し）');
pl = P.plan(ev3, 500, D('2026-12-02'));
ev3 = P.spend(ev3, 500, 'x', 'dev1', D('2026-12-02'));
B = P.balance(ev3, D('2026-12-05'));
check(B.paid_sub === 4400 && B.lost === 3500, '12/2 に500P使う → 期限の近い前の月から引く → 12/5 には前の月の残り3,500Pが消え、新しい4,400Pは残る');
// 12/5 に使ったPは、新しい lot から（期限の切れた lot からは引かない）
let ev4 = P.spend(ev3, 400, 'y', 'dev1', D('2026-12-05'));
check(P.balance(ev4, D('2026-12-05')).paid_sub === 4000, '期限が切れたあとに使ったPは新しいPから引く（4,000P残る）');
// 返金
const rf = P.refundEvent(ev4, { id: '100', revokedAt: D('2026-12-06') }, D('2026-12-06'));
check(rf && rf.kind === 'refund' && rf.bucket === 'paid_pack' && rf.amount === -1000, '返金：パックの1,000Pを引く');
B = P.balance(ev4.concat([rf]), D('2026-12-06'));
check(B.paid_pack === 0 && P.refundEvent(ev4.concat([rf]), { id: '100' }) === null && P.refundEvent(ev4, { id: '999' }) === null, '返金で買ったPは0（0より下にしない）・同じ返金は2回しない・知らない取引は何もしない');
// 解放
let ev5 = P.unlock(ev4, 'type:複勝', P.COST.type, 'dev1', D('2026-12-07'));
check(ev5 && P.unlocked(ev5, 'type:複勝') && !P.unlocked(ev5, 'type:馬連') && P.balance(ev5, D('2026-12-07')).total === P.balance(ev4, D('2026-12-07')).total - 500, '券種の解放（500P）・解放したものは unlocked');
check(P.unlock(ev5, 'type:複勝', 500, 'dev1', D('2026-12-07')).length === ev5.length, '同じものは2回解放しない（Pも引かない）');
check(P.unlock(ev5, 'slot:2', P.COST.slot, 'dev1', D('2026-12-07')) === null, 'マザーデータの解放（15,000P）は足りないので null');
// ミッション
let ms = P.missions(7, []);
check(ms.length === 1 && ms[0].n === 8 && !ms[0].done && !ms[0].claimable, '7レース：8レースのミッションがまだ');
ms = P.missions(16, []);
check(ms.length === 3 && ms[0].claimable && ms[1].claimable && ms[2].n === 25 && !ms[2].done, '16レース：8と15は受け取れる・次は25');
const claimed = [P.missionEvent(ms[0], D('2026-12-08'))];
ms = P.missions(16, claimed);
check(ms[0].claimed && !ms[0].claimable && ms[1].claimable && claimed[0].id === 'mission-rec-8' && claimed[0].amount === 500 && claimed[0].bucket === 'free', '受け取ったら claimed・報酬は無償の枠');
ms = P.missions(305, []);
check(ms.map(m => m.n).join(',') === '8,15,25,40,60,85,100,130,160,200,240,300,400' && ms[11].reward === 2000 && ms[12].reward === 2000 && !ms[12].done, '300のあとは100ごと（400）・2,000P');
check(P.missionAt(13).n === 500 && P.missionAt(13).reward === 2000, '500レースも2,000P');
// レースの見分け方
check(P.raceKey({ date: '2026-10-10', venue: '○○競馬場', r: 8 }) === '2026-10-10|○○|8' && P.raceKey({ date: '2026-10-10', venue: '', r: '8' }) === '2026-10-10||8', 'ミッションの鍵：日付＋開催場（競馬場をとる）＋R');
const a = { date: '2026-10-10', venue: '', r: 8, rname: 'テスト特別', start: '15:40', dist: 1400 };
check(P.sameRace(a, { date: '2026-10-10', venue: 'どこか', r: 8 }), '同じ日付・同じR（開催場が片方だけ空）→ 同じレース');
check(P.sameRace(a, { date: '2026-10-10', rname: 'テスト 特別', start: '15:40', dist: '1400' }), 'レース名・距離・発走時刻が同じ → 同じレース（Rがなくても）');
check(!P.sameRace(a, { date: '2026-10-11', venue: '', r: 8 }) && !P.sameRace(a, { date: '2026-10-10', venue: '', r: 9 }) && !P.sameRace({ date: '2026-10-10', venue: 'あ', r: 8 }, { date: '2026-10-10', venue: 'い', r: 8 }), '別の日・別のR・別の開催場 → 別のレース');
check(P.findPaid([{ date: '2026-10-10', venue: '', r: 7, pid: 'p1' }, { date: '2026-10-10', venue: '', r: 8, pid: 'p2' }], { date: '2026-10-10', venue: '', r: 8 }).pid === 'p2' && P.findPaid([], a) === null, '払ったレースの一覧から見つける');
// 壁紙のミッション（8.3・第4弾）：ポイントで解放した壁紙の枚数（帯は数えない）→ 8・16・25枚で帯の壁紙。受け取ると 0P の mission と unlock-theme:<帯>
{
  const T0 = D('2026-11-05');
  let ev = [P.giftEvent(T0)];
  for (const t of ['sakura', 'sea', 'autumn', 'snow', 'newyear', 'news', 'ink']) ev = P.unlock(ev, 'theme:' + t, 0, 'd1', T0);
  check(P.wallCount(ev) === 7 && P.wallMissions(7, ev).map(m => m.claimable + '/' + m.done).join() === 'false/false,false/false,false/false' && P.wallMissions(7, ev)[0].label === 'シルバー帯の壁紙' && P.WALL_MISSIONS.map(m => m[0]).join() === '8,16,25', '7枚：まだ（8・16・25枚）');
  ev = P.unlock(ev, 'theme:stars', 0, 'd1', T0);
  const wm = P.wallMissions(P.wallCount(ev), ev);
  check(P.wallCount(ev) === 8 && wm[0].claimable && !wm[1].claimable && wm[0].id === 'mission-wall-8' && wm[0].theme === 'silver', '8枚：シルバー帯が受け取れる');
  const add = P.wallMissionEvents(wm[0], 'd1', T0);
  ev = ev.concat(add);
  const b = P.balance(ev, T0);
  check(add.length === 2 && add[0].id === 'mission-wall-8' && add[0].amount === 0 && add[1].id === 'unlock-theme:silver' && add[1].amount === 0 && P.unlocked(ev, 'theme:silver') && b.total === 1500 && b.free === 1500, '受け取ると 0P の mission と unlock-theme:silver（ポイントは変わらない）');
  check(P.wallCount(ev) === 8 && P.wallMissions(8, ev)[0].claimed && !P.wallMissions(8, ev)[0].claimable, '帯の壁紙は枚数に数えない・受け取りずみ');
  check(P.unlock(ev, 'theme:silver', 0, 'd1', T0).length === ev.length, '同じ解放は2回足さない');
}
// 結果ボードカスタム（第4.91版）：買い切り 2,200円（非消耗型）→ 第4.114版：1,500円・買った あとに 読み込んだ レースの 数で 番号の 順に 解放
//   第4.113版（まさちゃんの 指定）：16こ（1〜15 は じゅんび中・16「ボードを持つ馬」）・6レースごと（全部で 96レース）・的中の とき／ハズレの とき の 2つを べつべつに 選ぶ
{
  const T0 = D('2026-11-06');
  check(P.PRODUCTS['jp.tengel.app.boardcustom'] && P.PRODUCTS['jp.tengel.app.boardcustom'].kind === 'unlock' && P.PRODUCTS['jp.tengel.app.boardcustom'].yen === 1500 && P.BOARD.product === 'jp.tengel.app.boardcustom', '商品：jp.tengel.app.boardcustom（買い切り・第4.114版：1,500円）');
  check(P.BOARD_NEED.join() === '6,12,18,24,30,36,42,48,54,60,66,72,78,84,90,96' && P.BOARD.steps.length === 1 && P.BOARD.steps[0].join() === '16,6', '解放の 数：6レースごとに 1つ（全部で 96レース・第4.113版）');
  const C = P.BOARD_ITEMS[15];
  check(P.BOARD_ITEMS.length === 16 && P.BOARD_ITEMS.length === P.BOARD_NEED.length && P.BOARD_ITEMS.slice(0, 15).every((it, i) => !it.ready && it.name === 'じゅんび中' && it.no === i + 1 && it.id === 'prep' + (i + 1) && it.need === (i + 1) * 6),
    '16こ：1〜15 は じゅんび中（デザインが とどくまで 選べない・番号の 順に 6レースごと）');
  check(C.id === 'carry' && C.no === 16 && C.ready && C.when === 'all' && C.need === 96 && C.name === 'ボードを持つ馬' && P.BOARD_ITEMS.filter(i => i.ready).length === 1, '16「ボードを持つ馬」：的中にも ハズレにも 使える・96レース目（いま 飾りが あるのは これだけ）');
  check(new Set(P.BOARD_ITEMS.map(i => i.id)).size === 16 && P.BOARD_ITEMS.every(it => ['all', 'hit', 'big', 'miss'].includes(it.when)) && P.riseTier === undefined, 'id は ぜんぶ ちがう・when は all／hit／big／miss・出世馬の 段（riseTier）は なくした');
  const BCX = require('fs').readFileSync(require('path').join(__dirname, 'bcx.js'), 'utf8');
  check(P.BOARD_ITEMS.filter(i => i.ready).every(i => BCX.includes(`B.${i.id} = `)) && !/B\.(orbit|goal|peek|nap|hang|cheer|crowd|selfie|bite|stand|banner|stamp|flower|pop|drop|flip|slide|float|thump|droop|rise) = /.test(BCX) && !BCX.includes('TengelBoardPhantom'),
    '飾りが ある 番号は bcx.js に 部品を 作る 所（B.<id>）が ある・消した 1〜21 の 部品と 幻の 馬は ない');
  check(P.boardFits(C, 'hit') && P.boardFits(C, 'miss') && !P.boardFits(P.BOARD_ITEMS[0], 'hit') && !P.boardFits(P.BOARD_ITEMS[0], 'miss')
    && P.boardFits({ ready: true, when: 'miss' }, 'miss') && !P.boardFits({ ready: true, when: 'miss' }, 'hit') && P.boardFits({ ready: true, when: 'hit' }, 'hit') && !P.boardFits({ ready: true, when: 'hit' }, 'miss')
    && P.boardFits({ ready: true, when: 'big' }, 'hit') && !P.boardFits({ ready: true, when: 'big' }, 'miss') && P.boardSlot('miss') === 'miss' && ['hit', 'big', 'nd', 'sd', 'pc', 'sgd', 'spg', undefined].every(k => P.boardSlot(k) === 'hit'),
    '的中の 所（ハズレ いがいの 結果 ぜんぶ）・ハズレの 所に 使えるか：all＝両方・hit／big＝的中だけ・miss＝ハズレだけ・じゅんび中は どちらも だめ');
  let ev = [P.giftEvent(T0)];
  check(!P.boardOwned(ev), '買う 前は 持って いない');
  const bt = P.txEvent(ev, tx('700', 'jp.tengel.app.boardcustom', '2026-11-06'));
  ev.push(bt);
  check(bt.id === 'tx-700' && bt.kind === 'unlock' && bt.what === 'board' && bt.amount === 0 && P.boardOwned(ev), '買うと tx-700（unlock・board・0P）で 持って いる');
  check(P.txEvent(ev, tx('700', 'jp.tengel.app.boardcustom', '2026-11-06')) === null, '同じ 取引は 2回 足さない（購入を復元しても 1回）');
  const b0 = P.balance(ev, T0);
  check(b0.total === 1500 && b0.paidIn === 0, 'ポイントは 増えも 減りも しない（買い切りは ポイントでは ない）');
  check(P.boardUnlocked(0) === 0 && P.boardUnlocked(5) === 0 && P.boardUnlocked(6) === 1 && P.boardUnlocked(11) === 1 && P.boardUnlocked(12) === 2 && P.boardUnlocked(90) === 15 && P.boardUnlocked(95) === 15 && P.boardUnlocked(96) === 16 && P.boardUnlocked(500) === 16,
    '解放の 数（6→1・12→2・90→15・96→16）');
  const nx = P.boardNext(29), n90 = P.boardNext(90);
  check(nx.item.id === 'prep5' && nx.need === 30 && nx.left === 1 && nx.from === 24 && n90.item.id === 'carry' && n90.left === 6 && n90.from === 90 && P.boardNext(96) === null && P.boardNext(0).item.id === 'prep1' && P.boardNext(0).left === 6,
    'つぎ：29レース → 5（じゅんび中）まで あと1・90レース → 16「ボードを持つ馬」まで あと6・全部 解放なら なし');
  check(P.boardNextReady(0).item.id === 'carry' && P.boardNextReady(0).left === 96 && P.boardNextReady(95).left === 1 && P.boardNextReady(96) === null, 'つぎの 飾り（じゅんび中を とばす）：0レース → ボードを持つ馬まで あと96');
  // 的中の とき・ハズレの とき（第4.113版）
  const sel = { hit: '', miss: '' };
  check(P.boardOpen(sel, 0, 15).length === 0 && sel.hit === '' && sel.miss === '', 'じゅんび中（1〜15）を 解放しても 選ぶ ものは かわらない（お知らせも なし）');
  const got = P.boardOpen(sel, 15, 16);
  check(got.map(i => i.id).join() === 'carry' && sel.hit === 'carry' && sel.miss === 'carry', '16 を 解放 → まだ 選んで いない 的中・ハズレの 両方に そのまま つける');
  const s2 = { hit: 'none', miss: '' }, s3 = { hit: 'orbit', miss: 'none' };
  P.boardOpen(s2, 0, 16); P.boardOpen(s3, 15, 16);
  check(s2.hit === 'none' && s2.miss === 'carry' && s3.hit === 'carry' && s3.miss === 'none', '「なし」に した 所は そのまま・消した 飾り（前の 版）の 所は まだ 選んで いない と 同じ');
  check(['hit', 'big', 'nd', 'sd', 'pc', 'sgd', 'spg'].every(k => P.boardActive({ hit: 'carry', miss: 'none' }, 96, k) === 'carry') && P.boardActive({ hit: 'carry', miss: 'none' }, 96, 'miss') === ''
    && P.boardActive({ hit: 'none', miss: 'carry' }, 96, 'miss') === 'carry' && P.boardActive({ hit: 'none', miss: 'carry' }, 96, 'hit') === '' && P.boardActive({ hit: 'carry', miss: 'carry' }, 95, 'hit') === ''
    && P.boardActive({ hit: 'prep3', miss: 'prep3' }, 96, 'hit') === '' && P.boardActive({ hit: 'orbit', miss: '' }, 500, 'hit') === '' && P.boardActive(null, 96, 'hit') === '',
    'ボードに つける もの：的中の 所は 的中・デカ的中・ど的中 など・ハズレの 所は ハズレだけ（べつべつ）・解放 前・じゅんび中・消した 飾りは つけない');
  check(JSON.stringify(P.boardSel({ reads: 150, sel: 'carry' })) === '{"hit":"carry","miss":"carry"}' && JSON.stringify(P.boardSel({ sel: 'none' })) === '{"hit":"none","miss":"none"}' && JSON.stringify(P.boardSel({ sel: 'orbit' })) === '{"hit":"","miss":""}'
    && JSON.stringify(P.boardSel({ selHit: 'carry', selMiss: 'none', sel: 'orbit' })) === '{"hit":"carry","miss":"none"}' && JSON.stringify(P.boardSel(null)) === '{"hit":"","miss":""}' && P.boardKnown('none') && P.boardKnown('carry') && !P.boardKnown('prep1') && !P.boardKnown(''),
    '前の 版の 台帳：1つの 選択（sel）→ 的中・ハズレの 両方へ（その とき 両方に ついて いた）・消した 飾りは まだ 選んで いない に・新しい 台帳は そのまま');
  const rf = P.refundEvent(ev, { id: '700', revokedAt: D('2026-11-07') });
  ev.push(rf);
  check(rf.id === 'refund-700' && rf.amount === 0 && !P.boardOwned(ev) && P.balance(ev, D('2026-11-07')).total === 1500, '返金 → 持って いない（ポイントは そのまま）');
  check(P.wallCount(ev) === 0 && !P.unlocked(ev, 'board'), '壁紙の 枚数・ポイントの 解放には 数えない');
}
{
  console.log('壁紙パック（第4.92版：買い切り 1,500円・11枚・読み込み 5レースごとに 1枚・帯の ミッションに 数える）');
  const D = s => new Date(s + 'T12:00:00+09:00').toISOString();
  const T0 = D('2026-11-10');
  const tx = (id, product, date) => ({ id, originalId: 'o' + id, product, date: D(date) });
  const Pd = P.PRODUCTS['jp.tengel.app.wallpack1'];
  check(Pd && Pd.kind === 'unlock' && Pd.what === 'wallpack' && Pd.yen === 1500 && Pd.points === 0 && P.WALLPACK.product === 'jp.tengel.app.wallpack1' && P.WALLPACK.every === 5 && P.WALLPACK.n === 11, '商品：jp.tengel.app.wallpack1（買い切り・1,500円・5レースごと・11枚）');
  check(P.PACKS.indexOf('jp.tengel.app.wallpack1') < 0 && P.SUBS.indexOf('jp.tengel.app.wallpack1') < 0, 'ポイントの パック・サブスクの 一覧には 入らない');
  let ev = [P.giftEvent(T0)];
  check(!P.packOwned(ev) && !P.boardOwned(ev), '買う 前は 持って いない');
  const pt = P.txEvent(ev, tx('800', 'jp.tengel.app.wallpack1', '2026-11-10'));
  ev.push(pt);
  check(pt.id === 'tx-800' && pt.kind === 'unlock' && pt.what === 'wallpack' && pt.amount === 0 && P.packOwned(ev) && !P.boardOwned(ev), '買うと tx-800（unlock・wallpack・0P）で 持って いる（結果ボードカスタムとは 別）');
  check(P.txEvent(ev, tx('800', 'jp.tengel.app.wallpack1', '2026-11-10')) === null, '同じ 取引は 2回 足さない');
  check(P.balance(ev, T0).total === 1500, 'ポイントは 増えも 減りも しない');
  check([0, 4, 5, 9, 10, 25, 49, 50, 54, 55, 99].map(P.packUnlocked).join() === '0,0,1,1,2,5,9,10,10,11,11', '解放の 数（5レースごとに 1枚・55で 11枚・それ以上は 11）');
  const nx = P.packNext(7);
  check(nx.no === 2 && nx.need === 10 && nx.left === 3 && nx.from === 5 && P.packNext(0).no === 1 && P.packNext(0).left === 5 && P.packNext(55) === null, 'つぎ：7レース → 2枚目まで あと3（10）・全部 解放なら なし');
  check(P.wallCount(ev) === 0 && P.wallCount(ev, 3) === 3 && P.wallCount(ev, 0) === 0, '帯の ミッションの 枚数：パックで 解放した 枚数を 足す');
  const ev2 = ev.concat([{ id: 'unlock-theme:sakura', kind: 'unlock', bucket: '', amount: -1000, at: T0, use: { paid_sub: 0, paid_pack: 0, free: 1000 }, what: 'theme:sakura' }]);
  check(P.wallCount(ev2, 7) === 8 && P.wallMissions(P.wallCount(ev2, 7), ev2)[0].claimable, 'ポイントの 1枚 ＋ パックの 7枚 ＝ 8枚 → シルバー帯が 受け取れる');
  const rf = P.refundEvent(ev, { id: '800', revokedAt: D('2026-11-11') });
  ev.push(rf);
  check(rf.id === 'refund-800' && !P.packOwned(ev) && P.balance(ev, D('2026-11-11')).total === 1500, '返金 → 持って いない（ポイントは そのまま）');
}
// 第4.114版（まさちゃん 2026/11/01）：お得パック（壁紙パックと 結果ボードカスタムの セット 2,200円）・ミッション（結果ボードカスタムの 解放の 数・壁紙の 枚数）
{
  console.log('お得パック（第4.114版：買い切り 2,200円・壁紙パックと 結果ボードカスタムの 両方）・ミッション（結果ボードカスタム 3〜16こ・壁紙 3〜45枚）');
  const D = s => new Date(s + 'T12:00:00+09:00').toISOString();
  const T0 = D('2026-11-12');
  const tx = (id, product, date) => ({ id, originalId: 'o' + id, product, date: D(date) });
  const Pd = P.PRODUCTS['jp.tengel.app.bundle1'];
  check(Pd && Pd.kind === 'unlock' && Pd.what === 'bundle' && Pd.yen === 2200 && Pd.points === 0 && Pd.name === 'お得パック' && P.BUNDLE.product === 'jp.tengel.app.bundle1' && P.BUNDLE.parts.join() === 'wallpack,board',
    '商品：jp.tengel.app.bundle1（買い切り・2,200円・what＝bundle・壁紙パックと 結果ボードカスタム）');
  check(P.PRODUCTS['jp.tengel.app.wallpack1'].yen === 1500 && P.PRODUCTS['jp.tengel.app.boardcustom'].yen === 1500 && P.PACKS.indexOf('jp.tengel.app.bundle1') < 0 && P.SUBS.indexOf('jp.tengel.app.bundle1') < 0,
    '単品は 1,500円ずつ（合わせて 3,000円 → お得パックは 2,200円）・ポイントの パック・サブスクの 一覧には 入らない');
  let ev = [P.giftEvent(T0)];
  check(!P.bundleOwned(ev) && !P.packOwned(ev) && !P.boardOwned(ev) && P.bundleOffer(ev), '買う 前：どれも 持って いない → お得パックを 出す');
  const bt = P.txEvent(ev, tx('900', 'jp.tengel.app.bundle1', '2026-11-12'));
  ev.push(bt);
  check(bt.id === 'tx-900' && bt.kind === 'unlock' && bt.what === 'bundle' && bt.amount === 0 && P.bundleOwned(ev) && P.packOwned(ev) && P.boardOwned(ev) && P.owned(ev, 'wallpack') && P.owned(ev, 'board') && !P.bundleOffer(ev),
    '買うと tx-900（unlock・bundle・0P）で 壁紙パックも 結果ボードカスタムも 持って いる（お得パックは もう 出さない）');
  check(P.txEvent(ev, tx('900', 'jp.tengel.app.bundle1', '2026-11-12')) === null && P.balance(ev, T0).total === 1500, '同じ 取引は 2回 足さない・ポイントは 増えも 減りも しない');
  const rf = P.refundEvent(ev, { id: '900', revokedAt: D('2026-11-13') });
  ev.push(rf);
  check(rf.id === 'refund-900' && rf.amount === 0 && !P.bundleOwned(ev) && !P.packOwned(ev) && !P.boardOwned(ev) && P.bundleOffer(ev), 'お得パックの 返金 → 2つとも 使えなくなる（お得パックを また 出す）');
  // 単品を 1つ 持って いれば お得パックは 出さない（残りの 単品だけ）・単品の 分は お得パックの 返金でも 残る
  const ev2 = [P.giftEvent(T0), P.txEvent([], tx('800', 'jp.tengel.app.wallpack1', '2026-11-12'))];
  check(P.packOwned(ev2) && !P.boardOwned(ev2) && !P.bundleOffer(ev2), '壁紙パックだけ 持って いる → お得パックは 出さない（結果ボードカスタムの 単品だけ）');
  const ev3 = ev2.concat([P.txEvent(ev2, tx('901', 'jp.tengel.app.bundle1', '2026-11-12'))]);
  const ev4 = ev3.concat([P.refundEvent(ev3, { id: '901', revokedAt: D('2026-11-13') })]);
  check(P.boardOwned(ev3) && P.packOwned(ev4) && !P.boardOwned(ev4) && !P.bundleOwned(ev4), 'お得パックを 返金しても、べつに 買った 壁紙パックは 残る');
  // ミッション：結果ボードカスタムの 解放の 数
  check(P.BOARD_MISSIONS.map(m => m.join(':')).join() === '3:500,6:800,9:1100,12:1400,16:1600', '結果ボードカスタムの ミッション：3こ 500P・6こ 800P・9こ 1,100P・12こ 1,400P・16こ 1,600P');
  const bm = P.boardMissions(9, [P.giftEvent(T0)]);
  check(bm.length === 5 && bm.map(m => m.id).join() === 'mission-board-3,mission-board-6,mission-board-9,mission-board-12,mission-board-16' && bm.map(m => m.claimable).join() === 'true,true,true,false,false'
    && bm[0].label === '結果ボードカスタム 3こ解放' && bm[0].reward === 500 && bm[2].done && !bm[3].done, '9こ 解放：3・6・9 が 受け取れる（12・16 は まだ）');
  let evm = [P.giftEvent(T0)];
  const re = P.rowEvent(bm[0], T0); evm.push(re);
  const bal = P.balance(evm, T0), bm2 = P.boardMissions(9, evm);
  check(re.id === 'mission-board-3' && re.kind === 'mission' && re.bucket === 'free' && re.amount === 500 && re.what === '結果ボードカスタム 3こ解放' && bal.total === 2000 && bal.free === 2000 && bal.freeIn === 2000
    && bm2[0].claimed && !bm2[0].claimable && bm2[1].claimable && P.has(evm, 'mission-board-3'), '受け取ると mission-board-3（mission・free・+500P＝もらったP）・受け取りずみ（1回だけ）・6こは まだ 受け取れる');
  check(P.boardMissions(0, evm).every(m => !m.claimable) && P.boardMissions(16, evm).filter(m => m.claimable).length === 4 && P.missions(0, evm)[0].id === 'mission-rec-8' && P.wallMissions(0, evm)[0].id === 'mission-wall-8',
    '0こ なら 受け取れない・16こ なら 残り 4つ・記録の ミッション（mission-rec-）と 帯の ミッション（mission-wall-）の id は そのまま');
  // ミッション：壁紙の 枚数（帯も 数える）
  check(P.WALLP_MISSIONS.map(m => m.join(':')).join() === '3:800,6:1200,9:1500,12:1800,15:2100,20:2500,25:2500,30:2500,35:3500,40:3500,45:3500' && P.WALL_TOTAL === 40,
    '壁紙の ミッション：3枚 800P・6枚 1,200P・9枚 1,500P・12枚 1,800P・15枚 2,100P・20・25・30枚 2,500P・35・40・45枚 3,500P（いま 解放できるのは 40枚）');
  const evw = [P.giftEvent(T0)].concat(['sakura', 'sea', 'snow'].map(t => ({ id: 'unlock-theme:' + t, kind: 'unlock', bucket: '', amount: -1000, at: T0, use: { paid_sub: 0, paid_pack: 0, free: 1000 }, what: 'theme:' + t })))
    .concat(P.wallMissionEvents(P.wallMissions(8, [])[0], 'x', T0));
  check(P.wallCount(evw, 5) === 8 && P.wallCountAll(evw, 5) === 9 && P.wallCountAll(evw) === 4 && P.wallCountAll([], 0) === 0, '枚数：ポイントの 3枚 ＋ パックの 5枚 ＝ 8（帯の ミッション用）・帯の シルバーも 数えると 9（枚数の ミッション用）');
  const wm = P.wallpMissions(9, evw);
  check(wm.length === 11 && wm.map(m => m.id).slice(0, 3).join() === 'mission-wallp-3,mission-wallp-6,mission-wallp-9' && wm.filter(m => m.claimable).length === 3 && wm[0].label === '壁紙 3枚解放' && wm[2].reward === 1500
    && wm.slice(0, 10).every(m => m.reach) && wm[10].n === 45 && wm[10].reach === false && !wm[10].claimable, '9枚：3・6・9 が 受け取れる・45枚の 行は reach＝false（いまは 40枚まで）');
  const evw2 = evw.concat([P.rowEvent(wm[2], T0)]);
  const bw = P.balance(evw2, T0);
  check(P.has(evw2, 'mission-wallp-9') && bw.free === 1500 - 3000 + 1500 && P.wallpMissions(9, evw2)[2].claimed && !P.wallpMissions(9, evw2)[2].claimable && P.wallpMissions(9, evw2)[1].claimable
    && P.wallpMissions(40, evw2).filter(m => m.claimable).length === 9 && P.wallpMissions(45, evw2)[10].reach === false, '受け取ると mission-wallp-9（+1,500P＝もらったP）・1回だけ・40枚なら 残り 9つ');
}
console.log('結果：', fails.length ? fails.length + '件おかしい' : 'OK');
process.exit(fails.length ? 1 : 0);
