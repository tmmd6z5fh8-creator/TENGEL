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
// 壁紙のミッション（8.3・第4弾）：ポイントで解放した壁紙の枚数（帯は数えない）→ 5・10・15枚で帯の壁紙（第4.147版：壁紙を 10枚 外した ので 8・16・25 → 5・10・16。第4.160版：ネオンを 外した ので マスター帯 16 → 15）。受け取ると 0P の mission と unlock-theme:<帯>
{
  const T0 = D('2026-11-05');
  let ev = [P.giftEvent(T0)];
  for (const t of ['gold', 'news', 'ink', 'carousel']) ev = P.unlock(ev, 'theme:' + t, 0, 'd1', T0);
  check(P.wallCount(ev) === 4 && P.wallMissions(4, ev).map(m => m.claimable + '/' + m.done).join() === 'false/false,false/false,false/false' && P.wallMissions(4, ev)[0].label === 'シルバー帯の壁紙' && P.WALL_MISSIONS.map(m => m[0]).join() === '5,10,15'
    && P.WALL_MISSIONS.map(m => m[1]).join() === 'silver,golden,tengel', '4枚：まだ（5・10・15枚：第4.160版で マスター帯 16 → 15）');
  ev = P.unlock(ev, 'theme:stars', 0, 'd1', T0);
  const wm = P.wallMissions(P.wallCount(ev), ev);
  check(P.wallCount(ev) === 5 && wm[0].claimable && !wm[1].claimable && wm[0].id === 'mission-wall-silver' && wm[0].theme === 'silver' && wm.map(m => m.id).join() === 'mission-wall-silver,mission-wall-golden,mission-wall-tengel', '5枚：シルバー帯が受け取れる（id は 帯の 名前）');
  const add = P.wallMissionEvents(wm[0], 'd1', T0);
  ev = ev.concat(add);
  const b = P.balance(ev, T0);
  check(add.length === 2 && add[0].id === 'mission-wall-silver' && add[0].amount === 0 && add[1].id === 'unlock-theme:silver' && add[1].amount === 0 && P.unlocked(ev, 'theme:silver') && b.total === 1500 && b.free === 1500, '受け取ると 0P の mission と unlock-theme:silver（ポイントは変わらない）');
  check(P.wallCount(ev) === 5 && P.wallMissions(5, ev)[0].claimed && !P.wallMissions(5, ev)[0].claimable, '帯の壁紙は枚数に数えない・受け取りずみ');
  check(P.unlock(ev, 'theme:silver', 0, 'd1', T0).length === ev.length, '同じ解放は2回足さない');
  // 前の 版（8・16・25枚：id は mission-wall-8／16／25）で 受け取った 人：帯を 持って いれば 受け取りずみ・前の mission-wall-16（ゴールド帯）は 新しい 16枚（マスター帯）と まざらない
  const mk0 = (id, what, amt) => ({ id, kind: id.indexOf('unlock-') === 0 ? 'unlock' : 'mission', bucket: id.indexOf('unlock-') === 0 ? '' : 'free', amount: amt || 0, at: new Date(T0).toISOString(), what });
  const old = [P.giftEvent(T0), mk0('mission-wall-8', 'シルバー帯の壁紙'), mk0('unlock-theme:silver', 'theme:silver'), mk0('mission-wall-16', 'ゴールド帯の壁紙'), mk0('unlock-theme:golden', 'theme:golden')];
  const om = P.wallMissions(15, old), om14 = P.wallMissions(14, old);
  check(om[0].claimed && !om[0].claimable && om[1].claimed && !om[1].claimable && !om[2].claimed && om[2].claimable && om[2].theme === 'tengel' && om[2].n === 15 && !om14[2].claimable && !om14[2].done,
    '前の 版で シルバー帯・ゴールド帯を 受け取った 人：どちらも 受け取りずみ の まま・15枚で マスター帯が 受け取れる（14枚では まだ・前の mission-wall-16 と まざらない）');
  const oe = old.concat(P.wallMissionEvents(om[2], 'd1', T0));
  check(P.unlocked(oe, 'theme:tengel') && new Set(oe.map(e => e.id)).size === oe.length && P.wallMissions(16, oe).every(m => m.claimed && !m.claimable) && P.balance(oe, T0).total === 1500, 'マスター帯を 受け取っても id は かぶらない・3つとも 受け取りずみ・ポイントは 変わらない');
  // 第4.160版：前の 版（16枚）で マスター帯を 受け取った 人は 受け取りずみ の まま（帯を 持って いる）・ネオンを ふくめて 15枚 だった 人は ネオンが へって 14枚 → まだ
  const had = [P.giftEvent(T0), mk0('mission-wall-tengel', 'マスター帯の壁紙'), mk0('unlock-theme:tengel', 'theme:tengel')];
  const neo = [P.giftEvent(T0)].concat(['gold', 'news', 'ink', 'carousel', 'stars', 'sunset', 'ranch', 'silks', 'pixel', 'fireworks', 'kids', 'cute', 'night', 'marble', 'neon'].map(t => mk0('unlock-theme:' + t, 'theme:' + t)));
  check(P.wallMissions(3, had)[2].claimed && !P.wallMissions(3, had)[2].claimable && P.wallCount(neo) === 14 && !P.wallMissions(P.wallCount(neo), neo)[2].claimable
    && P.wallMissions(P.wallCount(neo.concat([mk0('unlock-theme:chalk', 'theme:chalk')])), neo)[2].claimable,
    '第4.160版：前に マスター帯を 受け取った 人は 受け取りずみ の まま・ネオンは 数えない（ネオンを 入れて 15枚 → 14枚：まだ）・もう 1枚で 15枚 → マスター帯');
}
// 第4.147版（まさちゃん 2026/11/10 22:12「壁紙 ホワイトデー・バレンタインデー・ハロウィン・正月・クリスマス・雪・紅葉・桜・海 これら全部消して！ミッションも減った分調整して！」「七夕も消して！」）：
//   外した 壁紙（GONE_THEMES）は 枚数に 数えない・解放して いた ぶんは 1回 だけ 返す（goneUnlocks：使った ポイント／チケット＝0P）
{
  const T0 = D('2026-11-10');
  const un = (t, amt) => ({ id: 'unlock-theme:' + t, kind: 'unlock', bucket: '', amount: -amt, at: new Date(T0).toISOString(), use: { paid_sub: 0, paid_pack: 0, free: amt }, what: 'theme:' + t });
  check(P.GONE_THEMES.join() === 'sakura,sea,autumn,snow,newyear,xmas,halloween,valentine,whiteday,tanabata,neon' && P.GONE_THEMES.every(t => P.GONE_NAMES[t]) && Object.keys(P.GONE_NAMES).length === 11
    && P.GONE_NAMES.sakura === '桜' && P.GONE_NAMES.whiteday === 'ホワイトデー' && P.GONE_NAMES.tanabata === '七夕' && P.GONE_NAMES.neon === 'ネオン',
    '外した 壁紙は 11枚（桜・海・紅葉・雪・お正月・クリスマス・ハロウィン・バレンタイン・ホワイトデー・七夕＋第4.160版の ネオン）・名前つき');
  // 第4.160版（まさちゃん 2026/11/12 14:31「壁紙のネオン消して！」）：ネオン（3,000P）を 解放して いた 人には 3,000P を 返す（チケットで 解放して いたら チケット＝0P）・枚数に 数えない
  {
    const evn = [P.giftEvent(T0), P.rowEvent({ id: 'mission-rec-8', reward: 20000, label: 'x' }, T0), un('neon', 3000), un('pixel', 3000)];
    const gn = P.goneUnlocks(evn, []);
    check(P.wallCount(evn) === 1 && gn.length === 1 && gn[0].theme === 'neon' && gn[0].cost === 3000 && gn[0].id === 'back-theme:neon' && gn[0].name === 'ネオン'
      && P.goneUnlocks(evn.concat([P.rowEvent({ id: 'back-theme:neon', reward: 3000, label: 'x' }, T0)]), []).length === 0 && P.goneUnlocks([P.giftEvent(T0), un('neon', 0)], [])[0].cost === 0,
      'ネオン：枚数に 数えない・使った 3,000P を 1回 だけ 返す（チケットで 解放して いたら 0P＝チケットを 返す）・ドットは そのまま');
  }
  const ev = [P.giftEvent(T0), P.rowEvent({ id: 'mission-rec-8', reward: 20000, label: 'x' }, T0), un('sakura', 1000), un('xmas', 4000), un('gold', 2000), un('halloween', 0), un('news', 2000)];
  check(P.wallCount(ev) === 2 && P.wallCount(ev, 3) === 5 && P.wallCountAll(ev, 3) === 5 && P.unlocked(ev, 'theme:sakura'), '外した 壁紙（桜・クリスマス・ハロウィン）は 枚数に 数えない（のこりの 2枚 ＋ パック 3枚 ＝ 5）・台帳の できごとは 消さない');
  const g = P.goneUnlocks(ev, []);
  check(g.length === 3 && g.map(x => x.theme + ':' + x.cost + ':' + x.id + ':' + x.name).join() === 'sakura:1000:back-theme:sakura:桜,xmas:4000:back-theme:xmas:クリスマス,halloween:0:back-theme:halloween:ハロウィン',
    '返す ぶん：桜 1,000P・クリスマス 4,000P・ハロウィン 0P（＝チケットで 解放した）。のこって いる 壁紙（ぷりけつ・競馬新聞）は 返さない');
  const ev2 = ev.concat([P.rowEvent({ id: 'back-theme:sakura', reward: 1000, label: 'x' }, T0)]);
  check(P.goneUnlocks(ev2, []).map(x => x.theme).join() === 'xmas,halloween' && P.goneUnlocks(ev2, ['back-theme:xmas']).map(x => x.theme).join() === 'halloween'
    && P.goneUnlocks(ev2.concat([P.rowEvent({ id: 'back-theme:xmas', reward: 0, label: 'x' }, T0), P.rowEvent({ id: 'back-theme:halloween', reward: 0, label: 'x' }, T0)]), []).length === 0,
    '返した もの（back-theme:<名前>）・あずかりに 入って いる ものは もう 返さない（1回 だけ）');
  check(P.goneUnlocks([], []).length === 0 && P.goneUnlocks(null).length === 0 && P.goneUnlocks([P.giftEvent(T0), un('gold', 2000)], []).length === 0
    && P.goneUnlocks([un('sakura', 1000), un('sakura', 1000)], []).length === 1, '外した 壁紙を 解放して いなければ 何も 返さない・同じ 壁紙は 1回');
  const b0 = P.balance(ev, T0).total, back = P.rowEvent({ id: 'back-theme:xmas', reward: 4000, label: 'なくなった壁紙「クリスマス」のポイントを返した' }, T0);
  const b1 = P.balance(ev.concat([back]), T0);
  check(back.kind === 'mission' && back.bucket === 'free' && back.amount === 4000 && !back.expires && b0 === 21500 - 9000 && b1.total === b0 + 4000 && b1.free === P.balance(ev, T0).free + 4000 && b1.paid_sub === 0 && b1.paid_pack === 0, '返す ポイントは 獲得ポイント（期限なし）に 入る');
  // 上限の 近く：入る ぶん だけ 入れて、のこりは あずかる（holdSplit）→ どちらも「返した」に 数える
  const sp = P.holdSplit(back, 1500);
  check(sp.event.id === 'back-theme:xmas' && sp.event.amount === 1500 && sp.event.held === 2500 && sp.hold.id === 'back-theme:xmas' && sp.hold.points === 2500 && sp.hold.kind === 'mission'
    && P.goneUnlocks(ev.concat([sp.event]), []).every(x => x.theme !== 'xmas'), '上限を こえる ぶんは あずかる（台帳に しるしが 入る ので 2回は 返さない）');
}
// 結果ボードカスタム（第4.91版）：買い切り 2,200円（非消耗型）→ 第4.114版：1,500円・買った あとに 読み込んだ レースの 数で 番号の 順に 解放
//   第4.113版（まさちゃんの 指定）：16こ（1〜15 は じゅんび中・16「ボードを持つ馬」）・6レースごと（全部で 96レース）・的中の とき／ハズレの とき の 2つを べつべつに 選ぶ
//   第4.120版（まさちゃんの 指定 2026/11/04）：15こ（1〜14 は じゅんび中・15「ボードを持つ馬」）・6レースごと（全部で 90レース）
//   第4.121版：1〜14 に まさちゃんの 絵の ボード（1〜9 的中①〜⑨・10〜14 ハズレ①〜⑤：kisekae/bcp/bcp_app.py の ITEMS）
{
  const T0 = D('2026-11-06');
  check(P.PRODUCTS['jp.tengel.app.boardcustom'] && P.PRODUCTS['jp.tengel.app.boardcustom'].kind === 'unlock' && P.PRODUCTS['jp.tengel.app.boardcustom'].yen === 1500 && P.BOARD.product === 'jp.tengel.app.boardcustom', '商品：jp.tengel.app.boardcustom（買い切り・第4.114版：1,500円）');
  check(P.BOARD_NEED.join() === '6,12,18,24,30,36,42,48,54,60,66,72,78,84,90' && P.BOARD.steps.length === 1 && P.BOARD.steps[0].join() === '15,6', '解放の 数：6レースごとに 1つ（全部で 90レース・第4.120版）');
  const C = P.BOARD_ITEMS[14];
  const PIC_IDS = ['ring', 'toast', 'race', 'snap', 'seal', 'cup', 'hoist', 'bloom', 'climb', 'rain', 'next', 'cover', 'wait', 'pen'];
  const PIC_NAMES = ['結果ボードを廻る', '馬達の祝杯', '馬レース結果ボード', '自撮り結果ボード', 'スタンプ結果ボード', 'トロフィー結果ボード', '馬が運ぶ結果ボード', '花束結果ボード', '出世馬結果ボード',
    '二人でしょんぼり', '次…！', '隠蔽作戦', 'ボード結果待ち', '書き換え参戦'];
  check(P.BOARD_ITEMS.length === 15 && P.BOARD_ITEMS.length === P.BOARD_NEED.length && P.BOARD_ITEMS.slice(0, 14).every((it, i) => it.ready && it.id === PIC_IDS[i] && it.name === PIC_NAMES[i] && it.no === i + 1 && it.need === (i + 1) * 6 && it.when === (i < 9 ? 'hit' : 'miss')),
    '15こ：1〜9 的中①〜⑨・10〜14 ハズレ①〜⑤（まさちゃんの 絵の ボード・名前も まさちゃんの もの・番号の 順に 6レースごと）');
  check(C.id === 'carry' && C.no === 15 && C.ready && C.when === 'all' && C.need === 90 && C.name === 'ボードを持つ馬' && P.BOARD_ITEMS.filter(i => i.ready).length === 15, '15「ボードを持つ馬」：的中にも ハズレにも 使える・90レース目（じゅんび中は もう ない）');
  const OLD_IDS = ['orbit', 'goal', 'peek', 'nap', 'hang', 'cheer', 'crowd', 'selfie', 'bite', 'stand', 'banner', 'stamp', 'flower', 'pop', 'drop', 'flip', 'slide', 'float', 'thump', 'droop', 'rise'];
  check(new Set(P.BOARD_ITEMS.map(i => i.id)).size === 15 && P.BOARD_ITEMS.every(it => ['all', 'hit', 'big', 'miss'].includes(it.when) && OLD_IDS.indexOf(it.id) < 0) && P.riseTier === undefined,
    'id は ぜんぶ ちがう・前の 版の 飾り（第4.113版で 消した 1〜21）の id と かぶらない・when は all／hit／big／miss・出世馬の 段（riseTier）は なくした');
  const BCX = require('fs').readFileSync(require('path').join(__dirname, 'bcx.js'), 'utf8'), BAPP = require('fs').readFileSync(require('path').join(__dirname, 'kisekae', 'bcp', 'bcp_app.py'), 'utf8');
  check(BCX.includes('B.carry = ') && P.BOARD_ITEMS.slice(0, 14).every(i => BAPP.includes(`('${i.id}', '${i.when}', `)) && BCX.includes('window.__BCP') && !/B\.(orbit|goal|peek|nap|hang|cheer|crowd|selfie|bite|stand|banner|stamp|flower|pop|drop|flip|slide|float|thump|droop|rise) = /.test(BCX) && !BCX.includes('TengelBoardPhantom'),
    '15 は bcx.js の 部品（B.carry）・1〜14 は 絵の ボード（bcp_app.py の ITEMS に 同じ id と when）・消した 1〜21 の 部品と 幻の 馬は ない');
  check(P.boardFits(C, 'hit') && P.boardFits(C, 'miss') && P.boardFits(P.BOARD_ITEMS[0], 'hit') && !P.boardFits(P.BOARD_ITEMS[0], 'miss') && P.boardFits(P.BOARD_ITEMS[9], 'miss') && !P.boardFits(P.BOARD_ITEMS[9], 'hit')
    && !P.boardFits({ ready: false, when: 'all' }, 'hit') && !P.boardFits({ ready: false, when: 'all' }, 'miss')
    && P.boardFits({ ready: true, when: 'miss' }, 'miss') && !P.boardFits({ ready: true, when: 'miss' }, 'hit') && P.boardFits({ ready: true, when: 'hit' }, 'hit') && !P.boardFits({ ready: true, when: 'hit' }, 'miss')
    && P.boardFits({ ready: true, when: 'big' }, 'hit') && !P.boardFits({ ready: true, when: 'big' }, 'miss') && P.boardSlot('miss') === 'miss' && ['hit', 'big', 'nd', 'sd', 'pc', 'sgd', 'spg', undefined].every(k => P.boardSlot(k) === 'hit'),
    '的中の 所（ハズレ いがいの 結果 ぜんぶ）・ハズレの 所に 使えるか：all＝両方・hit／big＝的中だけ（1〜9）・miss＝ハズレだけ（10〜14）・じゅんび中は どちらも だめ');
  let ev = [P.giftEvent(T0)];
  check(!P.boardOwned(ev), '買う 前は 持って いない');
  const bt = P.txEvent(ev, tx('700', 'jp.tengel.app.boardcustom', '2026-11-06'));
  ev.push(bt);
  check(bt.id === 'tx-700' && bt.kind === 'unlock' && bt.what === 'board' && bt.amount === 0 && P.boardOwned(ev), '買うと tx-700（unlock・board・0P）で 持って いる');
  check(P.txEvent(ev, tx('700', 'jp.tengel.app.boardcustom', '2026-11-06')) === null, '同じ 取引は 2回 足さない（購入を復元しても 1回）');
  const b0 = P.balance(ev, T0);
  check(b0.total === 1500 && b0.paidIn === 0, 'ポイントは 増えも 減りも しない（買い切りは ポイントでは ない）');
  check(P.boardUnlocked(0) === 0 && P.boardUnlocked(5) === 0 && P.boardUnlocked(6) === 1 && P.boardUnlocked(11) === 1 && P.boardUnlocked(12) === 2 && P.boardUnlocked(84) === 14 && P.boardUnlocked(89) === 14 && P.boardUnlocked(90) === 15 && P.boardUnlocked(96) === 15 && P.boardUnlocked(500) === 15,
    '解放の 数（6→1・12→2・84→14・90→15・その先も 15）');
  const nx = P.boardNext(29), n84 = P.boardNext(84);
  check(nx.item.id === 'seal' && nx.need === 30 && nx.left === 1 && nx.from === 24 && n84.item.id === 'carry' && n84.left === 6 && n84.from === 84 && P.boardNext(90) === null && P.boardNext(0).item.id === 'ring' && P.boardNext(0).left === 6,
    'つぎ：29レース → 5「スタンプ結果ボード」まで あと1・84レース → 15「ボードを持つ馬」まで あと6・全部 解放なら なし');
  check(P.boardNextReady(0).item.id === 'ring' && P.boardNextReady(0).left === 6 && P.boardNextReady(54).item.id === 'rain' && P.boardNextReady(89).item.id === 'carry' && P.boardNextReady(89).left === 1 && P.boardNextReady(90) === null,
    'つぎの 飾り：0レース → 1「結果ボードを廻る」まで あと6・54レース → 10「二人でしょんぼり」・89レース → ボードを持つ馬まで あと1');
  // 的中の とき・ハズレの とき（第4.113版）
  const sel = { hit: '', miss: '' };
  const g1 = P.boardOpen(sel, 0, 1);
  check(g1.map(i => i.id).join() === 'ring' && sel.hit === 'ring' && sel.miss === '', '1「結果ボードを廻る」を 解放 → まだ 選んで いない 的中の 所に つける（ハズレの 所は 的中だけの 飾りは つかない）');
  const g2 = P.boardOpen(sel, 1, 10);
  check(g2.length === 9 && g2[8].id === 'rain' && sel.hit === 'ring' && sel.miss === 'rain', '2〜10 を 解放 → 的中は そのまま・ハズレの 所に 10「二人でしょんぼり」');
  const got = P.boardOpen(sel, 14, 15);
  check(got.map(i => i.id).join() === 'carry' && sel.hit === 'ring' && sel.miss === 'rain', '15 を 解放 → もう 選んで いる 所は かえない');
  const s1 = { hit: '', miss: '' }; P.boardOpen(s1, 14, 15);
  check(s1.hit === 'carry' && s1.miss === 'carry', 'まだ 選んで いない 所が ある まま 15 を 解放 → 的中・ハズレの 両方に そのまま つける');
  const s2 = { hit: 'none', miss: '' }, s3 = { hit: 'orbit', miss: 'none' };
  P.boardOpen(s2, 0, 15); P.boardOpen(s3, 14, 15);
  check(s2.hit === 'none' && s2.miss === 'rain' && s3.hit === 'carry' && s3.miss === 'none', '「なし」に した 所は そのまま・消した 飾り（前の 版）の 所は まだ 選んで いない と 同じ');
  check(['hit', 'big', 'nd', 'sd', 'pc', 'sgd', 'spg'].every(k => P.boardActive({ hit: 'carry', miss: 'none' }, 90, k) === 'carry') && P.boardActive({ hit: 'carry', miss: 'none' }, 90, 'miss') === ''
    && P.boardActive({ hit: 'none', miss: 'carry' }, 90, 'miss') === 'carry' && P.boardActive({ hit: 'none', miss: 'carry' }, 90, 'hit') === '' && P.boardActive({ hit: 'carry', miss: 'carry' }, 89, 'hit') === ''
    && P.boardActive({ hit: 'prep3', miss: 'prep3' }, 90, 'hit') === '' && P.boardActive({ hit: 'orbit', miss: '' }, 500, 'hit') === '' && P.boardActive(null, 90, 'hit') === ''
    && ['hit', 'big', 'nd', 'sd', 'pc', 'sgd', 'spg', 'gk'].every(k => P.boardActive({ hit: 'ring', miss: 'rain' }, 90, k) === 'ring') && P.boardActive({ hit: 'ring', miss: 'rain' }, 90, 'miss') === 'rain'
    && P.boardActive({ hit: 'rain', miss: 'ring' }, 90, 'hit') === '' && P.boardActive({ hit: 'rain', miss: 'ring' }, 90, 'miss') === '' && P.boardActive({ hit: 'climb', miss: 'pen' }, 53, 'hit') === '' && P.boardActive({ hit: 'climb', miss: 'pen' }, 54, 'hit') === 'climb'
    && P.boardActive({ hit: 'climb', miss: 'pen' }, 83, 'miss') === '' && P.boardActive({ hit: 'climb', miss: 'pen' }, 84, 'miss') === 'pen',
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
  check(Pd && Pd.kind === 'unlock' && Pd.what === 'wallpack' && Pd.yen === 1500 && Pd.points === 0 && P.WALLPACK.product === 'jp.tengel.app.wallpack1' && P.WALLPACK.every === 5 && P.WALLPACK.n === 10, '商品：jp.tengel.app.wallpack1（買い切り・1,500円・5レースごと・10枚：第4.147版で 七夕を 外した）');
  check(P.PACKS.indexOf('jp.tengel.app.wallpack1') < 0 && P.SUBS.indexOf('jp.tengel.app.wallpack1') < 0, 'ポイントの パック・サブスクの 一覧には 入らない');
  let ev = [P.giftEvent(T0)];
  check(!P.packOwned(ev) && !P.boardOwned(ev), '買う 前は 持って いない');
  const pt = P.txEvent(ev, tx('800', 'jp.tengel.app.wallpack1', '2026-11-10'));
  ev.push(pt);
  check(pt.id === 'tx-800' && pt.kind === 'unlock' && pt.what === 'wallpack' && pt.amount === 0 && P.packOwned(ev) && !P.boardOwned(ev), '買うと tx-800（unlock・wallpack・0P）で 持って いる（結果ボードカスタムとは 別）');
  check(P.txEvent(ev, tx('800', 'jp.tengel.app.wallpack1', '2026-11-10')) === null, '同じ 取引は 2回 足さない');
  check(P.balance(ev, T0).total === 1500, 'ポイントは 増えも 減りも しない');
  check([0, 4, 5, 9, 10, 25, 49, 50, 54, 55, 99].map(P.packUnlocked).join() === '0,0,1,1,2,5,9,10,10,10,10', '解放の 数（5レースごとに 1枚・50で 10枚・それ以上は 10：前の 版で 55レース 読み込んで いた 人も 10枚）');
  const nx = P.packNext(7);
  check(nx.no === 2 && nx.need === 10 && nx.left === 3 && nx.from === 5 && P.packNext(0).no === 1 && P.packNext(0).left === 5 && P.packNext(49).no === 10 && P.packNext(49).left === 1 && P.packNext(50) === null && P.packNext(55) === null, 'つぎ：7レース → 2枚目まで あと3（10）・全部 解放（50レース）なら なし');
  check(P.wallCount(ev) === 0 && P.wallCount(ev, 3) === 3 && P.wallCount(ev, 0) === 0, '帯の ミッションの 枚数：パックで 解放した 枚数を 足す');
  const ev2 = ev.concat([{ id: 'unlock-theme:gold', kind: 'unlock', bucket: '', amount: -2000, at: T0, use: { paid_sub: 0, paid_pack: 0, free: 2000 }, what: 'theme:gold' }]);
  check(P.wallCount(ev2, 3) === 4 && !P.wallMissions(P.wallCount(ev2, 3), ev2)[0].claimable && P.wallCount(ev2, 4) === 5 && P.wallMissions(P.wallCount(ev2, 4), ev2)[0].claimable && !P.wallMissions(P.wallCount(ev2, 4), ev2)[1].claimable
    && P.wallMissions(P.wallCount(ev2, 9), ev2)[1].claimable && !P.wallMissions(P.wallCount(ev2, 10), ev2)[2].claimable, 'ポイントの 1枚 ＋ パックの 4枚 ＝ 5枚 → シルバー帯が 受け取れる（3枚では まだ）・＋9枚 ＝ 10枚で ゴールド帯・パックの 10枚 ぜんぶ でも マスター帯（15枚）は まだ');
  const rf = P.refundEvent(ev, { id: '800', revokedAt: D('2026-11-11') });
  ev.push(rf);
  check(rf.id === 'refund-800' && !P.packOwned(ev) && P.balance(ev, D('2026-11-11')).total === 1500, '返金 → 持って いない（ポイントは そのまま）');
}
// 第4.114版（まさちゃん 2026/11/01）：お得パック（壁紙パックと 結果ボードカスタムの セット 2,200円）・ミッション（結果ボードカスタムの 解放の 数・壁紙の 枚数）
{
  console.log('お得パック（第4.114版：買い切り 2,200円・壁紙パックと 結果ボードカスタムの 両方）・ミッション（結果ボードカスタム 3〜15こ・壁紙 3〜29枚）');
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
  check(P.BOARD_MISSIONS.map(m => m.join(':')).join() === '3:500,6:800,9:1100,12:1400,15:1600', '結果ボードカスタムの ミッション：3こ 500P・6こ 800P・9こ 1,100P・12こ 1,400P・15こ 1,600P（第4.120版：16こ → 15こ）');
  const bm = P.boardMissions(9, [P.giftEvent(T0)]);
  check(bm.length === 5 && bm.map(m => m.id).join() === 'mission-board-3,mission-board-6,mission-board-9,mission-board-12,mission-board-15' && bm.map(m => m.claimable).join() === 'true,true,true,false,false'
    && bm[0].label === '結果ボードカスタム 3こ解放' && bm[0].reward === 500 && bm[2].done && !bm[3].done && bm[4].label === '結果ボードカスタム 15こ解放', '9こ 解放：3・6・9 が 受け取れる（12・15 は まだ）');
  let evm = [P.giftEvent(T0)];
  const re = P.rowEvent(bm[0], T0); evm.push(re);
  const bal = P.balance(evm, T0), bm2 = P.boardMissions(9, evm);
  check(re.id === 'mission-board-3' && re.kind === 'mission' && re.bucket === 'free' && re.amount === 500 && re.what === '結果ボードカスタム 3こ解放' && bal.total === 2000 && bal.free === 2000 && bal.freeIn === 2000
    && bm2[0].claimed && !bm2[0].claimable && bm2[1].claimable && P.has(evm, 'mission-board-3'), '受け取ると mission-board-3（mission・free・+500P＝もらったP）・受け取りずみ（1回だけ）・6こは まだ 受け取れる');
  check(P.boardMissions(0, evm).every(m => !m.claimable) && P.boardMissions(15, evm).filter(m => m.claimable).length === 4 && P.missions(0, evm)[0].id === 'mission-rec-8' && P.wallMissions(0, evm)[0].id === 'mission-wall-silver',
    '0こ なら 受け取れない・15こ なら 残り 4つ・記録の ミッション（mission-rec-）は そのまま・帯の ミッションの id は 帯の 名前（mission-wall-silver：第4.147版）');
  // 第4.120版：前の 版で「16こ解放」を 受け取った 台帳 → 「15こ解放」は 受け取りずみ（2回 もらえない）
  const ev16 = evm.concat([{ id: 'mission-board-16', kind: 'mission', bucket: 'free', amount: 1600, at: T0, what: '結果ボードカスタム 16こ解放' }]), bm16 = P.boardMissions(15, ev16);
  check(bm16[4].n === 15 && bm16[4].claimed && !bm16[4].claimable && bm16.filter(m => m.claimable).length === 3 && P.boardMissions(15, evm)[4].claimable,
    '前の 版の「16こ解放」を 受け取った 人は「15こ解放」も 受け取りずみ・受け取って いない 人は 15こで 受け取れる');
  // ミッション：壁紙の 枚数（帯も 数える）
  //   第4.139版（まさちゃん 2026/11/10 11:58「ならミッションを40枚までにして！」）：届かない 45枚の 行を やめて 40枚まで（10こ）
  //   第4.147版（まさちゃん 2026/11/10 22:12「ミッションも減った分調整して！」）：壁紙を 10枚 外した（40 → 30枚）ので、届かない 35枚・40枚の 行を やめて 30枚まで（8こ）
  //   第4.160版（まさちゃん 2026/11/12 14:32「ミッションも減った分調整して！」）：ネオンを 外した（30 → 29枚）ので、さいごの 30枚 → 29枚（ポイントは 同じ 2,500P・行は 8こ の まま）
  check(P.WALLP_MISSIONS.map(m => m.join(':')).join() === '3:800,6:1200,9:1500,12:1800,15:2100,20:2500,25:2500,29:2500' && P.WALL_TOTAL === 29
    && P.WALLP_MISSIONS[P.WALLP_MISSIONS.length - 1][0] === P.WALL_TOTAL && P.WALLP_MISSIONS.reduce((a, m) => a + m[1], 0) === 14900,
    '壁紙の ミッション：3枚 800P・6枚 1,200P・9枚 1,500P・12枚 1,800P・15枚 2,100P・20・25・29枚 2,500P（29枚まで＝いま 解放できる 枚数・ぜんぶで 14,900P）');
  const evw = [P.giftEvent(T0)].concat(['gold', 'news', 'ink'].map(t => ({ id: 'unlock-theme:' + t, kind: 'unlock', bucket: '', amount: -500, at: T0, use: { paid_sub: 0, paid_pack: 0, free: 500 }, what: 'theme:' + t })))
    .concat(P.wallMissionEvents(P.wallMissions(5, [])[0], 'x', T0));
  check(P.wallCount(evw, 5) === 8 && P.wallCountAll(evw, 5) === 9 && P.wallCountAll(evw) === 4 && P.wallCountAll([], 0) === 0, '枚数：ポイントの 3枚 ＋ パックの 5枚 ＝ 8（帯の ミッション用）・帯の シルバーも 数えると 9（枚数の ミッション用）');
  const wm = P.wallpMissions(9, evw);
  check(wm.length === 8 && wm.map(m => m.id).slice(0, 3).join() === 'mission-wallp-3,mission-wallp-6,mission-wallp-9' && wm.filter(m => m.claimable).length === 3 && wm[0].label === '壁紙 3枚解放' && wm[2].reward === 1500
    && wm.every(m => m.reach) && wm[7].n === 29 && wm[7].id === 'mission-wallp-29' && !wm.some(m => m.n > 29), '9枚：3・6・9 が 受け取れる・行は 8こ（29枚まで・ぜんぶ 届く・30枚・35枚・40枚の 行は ない）');
  const evw2 = evw.concat([P.rowEvent(wm[2], T0)]);
  const bw = P.balance(evw2, T0);
  check(P.has(evw2, 'mission-wallp-9') && bw.free === 1500 - 1500 + 1500 && P.wallpMissions(9, evw2)[2].claimed && !P.wallpMissions(9, evw2)[2].claimable && P.wallpMissions(9, evw2)[1].claimable
    && P.wallpMissions(29, evw2).filter(m => m.claimable).length === 7 && P.wallpMissions(29, evw2).every(m => m.done) && !P.wallpMissions(28, evw2)[7].done, '受け取ると mission-wallp-9（+1,500P＝獲得ポイント）・1回だけ・29枚なら ぜんぶ 達成（残り 7つ 受け取れる・28枚では さいごは まだ）');
  // 前の 版で「35枚」「40枚」を 受け取った 人：台帳の できごと（+3,500P ずつ）は そのまま 残る（ポイントは へらない）・行には もう 出ない
  const evo = evw2.concat([{ id: 'mission-wallp-35', kind: 'mission', bucket: 'free', amount: 3500, at: T0, what: '壁紙 35枚解放' }, { id: 'mission-wallp-40', kind: 'mission', bucket: 'free', amount: 3500, at: T0, what: '壁紙 40枚解放' }]);
  check(P.balance(evo, T0).free === bw.free + 7000 && P.wallpMissions(29, evo).length === 8 && P.wallpMissions(29, evo).filter(m => m.claimable).length === 7, '前の 版で 35枚・40枚を 受け取った ぶんの ポイントは そのまま（行は 8こ の まま）');
  // 第4.160版：前の 版で「30枚解放」を 受け取った 人は「29枚解放」も 受け取りずみ（2回 もらえない）・受け取って いない 人は 29枚で 受け取れる
  const ev30 = evw2.concat([{ id: 'mission-wallp-30', kind: 'mission', bucket: 'free', amount: 2500, at: T0, what: '壁紙 30枚解放' }]);
  const w30 = P.wallpMissions(29, ev30);
  check(w30[7].n === 29 && w30[7].claimed && !w30[7].claimable && w30.filter(m => m.claimable).length === 6 && P.wallpMissions(29, evw2)[7].claimable && !P.wallpMissions(29, evw2)[7].claimed && P.balance(ev30, T0).free === bw.free + 2500,
    '前の 版の「30枚解放」を 受け取った 人は「29枚解放」も 受け取りずみ（ポイントは そのまま）・受け取って いない 人は 29枚で 受け取れる');
}
// 第4.138版：思い出フィギュアの ミッション（作った 数 1・5・8 → 5,000・5,000・10,000P）
{
  const T0 = D('2026-11-10');
  check(P.FIG_MISSIONS.map(m => m.join(':')).join() === '1:5000,5:5000,8:10000', '思い出フィギュアの ミッション：1つ 5,000P・5つ 5,000P・8つ 10,000P');
  let evf = [P.giftEvent(T0)];
  const f0 = P.figMissions(0, evf), f1 = P.figMissions(1, evf), f5 = P.figMissions(5, evf), f8 = P.figMissions(9, evf);
  check(f0.length === 3 && f0.every(m => !m.done && !m.claimable) && f0.map(m => m.id).join() === 'mission-fig-1,mission-fig-5,mission-fig-8'
    && f0.map(m => m.label).join() === '思い出フィギュアを1つ完成させる,思い出フィギュアを5つ完成させる,思い出フィギュアを8つ完成させる', '0こ：3つとも まだ（id は mission-fig-1・5・8・名前は「思い出フィギュアを○つ完成させる」）');
  check(f1.map(m => m.claimable).join() === 'true,false,false' && f5.map(m => m.claimable).join() === 'true,true,false' && f8.map(m => m.claimable).join() === 'true,true,true', '1こ → 1つめ・5こ → 2つめ まで・8こ 以上 → 3つとも 受け取れる');
  const re1 = P.rowEvent(f1[0], T0); evf.push(re1);
  const b1 = P.balance(evf, T0), g1 = P.figMissions(8, evf);
  check(re1.id === 'mission-fig-1' && re1.kind === 'mission' && re1.bucket === 'free' && re1.amount === 5000 && re1.what === '思い出フィギュアを1つ完成させる' && b1.total === 6500 && b1.free === 6500
    && g1[0].claimed && !g1[0].claimable && g1[1].claimable && g1[2].claimable, '受け取ると mission-fig-1（mission・free・+5,000P＝もらったP）・受け取りずみ（1回だけ）');
  evf.push(P.rowEvent(g1[1], T0)); evf.push(P.rowEvent(g1[2], T0));
  check(P.balance(evf, T0).total === 21500 && P.figMissions(8, evf).every(m => m.claimed && !m.claimable) && P.tcMissions(0, evf)[0].id === 'mission-tc-50' && P.boardMissions(0, evf)[0].id === 'mission-board-3',
    '3つ 受け取ると 合計 +20,000P・ほかの ミッションの id は そのまま');
}
// 第4.139版：上限 99,999P・あずかりポイント（まさちゃん 2026/11/10 11:46「ポイントの上限は、99999までにして！」・12:27「99999pに到達しながらサブスクに入っている人は、
//   ミッションのところで超えてしまっているポイントが溜まっていくようにして！で、使って減った分は、溜まってるポイントから補充できるようによろしく！」）
{
  console.log('上限 99,999P・あずかりポイント（第4.139版）');
  const T0 = D('2026-11-10'), T1 = D('2026-11-20'), T2 = D('2026-12-25');
  check(P.CAP === 99999 && P.room(0) === 99999 && P.room(1500) === 98499 && P.room(99999) === 0 && P.room(120000) === 0 && P.room(-5) === 99999, '上限は 99,999P・room＝あと 入る P（こえて いたら 0）');
  // 95,000P 持って いる 人に サブスク 9,200P が 届く → 4,999P だけ 入って 4,201P は あずかり
  let ev = [P.giftEvent(T0), { id: 'g2', kind: 'gift', bucket: 'free', amount: 93500, at: T0 }];
  check(P.balance(ev, T0).total === 95000, 'はじめ 95,000P');
  const se = P.txEvent(ev, tx('901', 'jp.tengel.app.sub9200', '2026-11-10'));
  const sp = P.holdSplit(se, P.room(P.balance(ev, T0).total));
  check(sp.event.amount === 4999 && sp.event.held === 4201 && sp.event.id === 'tx-901' && sp.event.expires === se.expires && sp.hold && sp.hold.id === 'tx-901' && sp.hold.kind === 'sub' && sp.hold.points === 4201
    && sp.hold.tx === '901' && sp.hold.product === 'jp.tengel.app.sub9200' && se.amount === 9200, 'サブスク 9,200P が 届く：4,999P は 台帳へ（held＝4,201）・4,201P は あずかり（元の できごとは かえない）');
  ev.push(sp.event); let hold = [sp.hold];
  check(P.balance(ev, T0).total === 99999 && P.balance(ev, T0).paid_sub === 4999 && P.holdTotal(hold) === 4201 && JSON.stringify(P.holdSum(hold)) === JSON.stringify({ total: 4201, paid_sub: 4201, paid_pack: 0, free: 0 }),
    '台帳は ちょうど 99,999P（サブスクポイント 4,999）・あずかり 4,201P（種類ごとの 合計）');
  check(P.txEvent(ev, tx('901', 'jp.tengel.app.sub9200', '2026-11-10')) === null, '同じ 取引は 2回 足さない（ぜんぶ あずけた ときも 台帳に 0P の できごとが 残る）');
  // いっぱいの ときは 補充できない
  let r0 = P.holdRelease(ev, hold, T0);
  check(r0.moved === 0 && r0.hold.length === 1 && r0.hold[0].points === 4201 && r0.events.length === ev.length, 'いっぱいの あいだは 補充できない（そのまま）');
  // こえない ときは 分けない
  const small = P.holdSplit(P.txEvent([], tx('902', 'jp.tengel.app.points500', '2026-11-10')), 500);
  check(small.hold === null && small.event.amount === 500 && small.event.held === undefined, 'あきに 入る ときは 分けない');
  // ぜんぶ あずける（あき 0）
  const full = P.holdSplit(P.txEvent(ev, tx('903', 'jp.tengel.app.points4000', '2026-11-10')), 0);
  check(full.event.amount === 0 && full.event.held === 4000 && full.hold.kind === 'purchase' && full.hold.points === 4000, 'あきが 0 なら ぜんぶ あずける（台帳の できごとは 0P）');
  ev.push(full.event); hold.push(full.hold);
  check(P.balance(ev, T0).total === 99999 && P.balance(ev, T0).paid_pack === 0 && P.holdSum(hold).paid_pack === 4000 && P.holdSum(hold).total === 8201, '0P の 購入の できごとは 残高に 入らない・あずかり 合計 8,201P');
  // 使う（1,000P：サブスクポイントから）→ 補充（古い 順：サブスクの あずかりから 1,000P）
  ev = P.spend(ev, 1000, '読み込み', 'dev1', T1);
  check(P.balance(ev, T1).total === 98999 && P.balance(ev, T1).paid_sub === 3999, '1,000P 使う（サブスクポイントから）→ 98,999P');
  let r1 = P.holdRelease(ev, hold, T1);
  const rel = r1.events[r1.events.length - 1];
  check(r1.moved === 1000 && r1.parts.paid_sub === 1000 && r1.parts.paid_pack === 0 && rel.id === 'rel-tx-901-1' && rel.kind === 'sub' && rel.bucket === 'paid_sub' && rel.amount === 1000 && rel.from === 'hold' && rel.tx === '901'
    && rel.product === 'jp.tengel.app.sub9200' && rel.expires === P.addDays(T1, 30) && r1.hold.length === 2 && r1.hold[0].points === 3201 && r1.hold[1].points === 4000,
    '補充：あきの 1,000P だけ・古い 順（サブスクの あずかりから）・できごと rel-tx-901-1（sub・from:hold）・期限は 補充した 日から 30日・のこり 3,201＋4,000');
  ev = r1.events; hold = r1.hold;
  check(P.balance(ev, T1).total === 99999 && P.balance(ev, T1).paid_sub === 4999 && P.holdTotal(hold) === 7201, '補充の あと：台帳 99,999P・あずかり 7,201P');
  // はじめの サブスクポイント（11/10 に 届いた ぶん）は 12/10 で 期限。補充した ぶんは 12/20 まで
  const b2 = P.balance(ev, D('2026-12-15'));
  check(b2.paid_sub === 1000 && b2.lots.filter(L => !L.expired).length === 1 && b2.lots.filter(L => !L.expired)[0].id === 'rel-tx-901-1', '12/15：はじめに 入った サブスクポイントは 期限切れ・補充した 1,000P は 残る（12/20 まで）');
  // あずかって いる あいだは 期限が 進まない：12/25（台帳の サブスクポイントは ぜんぶ 期限切れ＝95,000P）に 5,000P 使ってから 補充 → サブスクの のこり 3,201P（1/24 まで）＋ パック 4,000P
  check(P.balance(ev, T2).total === 95000 && P.balance(ev, T2).paid_sub === 0 && P.holdTotal(hold) === 7201, '12/25：台帳の サブスクポイントは 期限切れ（95,000P）・あずかりの 7,201P は そのまま');
  let ev3 = P.spend(ev, 5000, '解放', 'dev1', T2);
  const r3 = P.holdRelease(ev3, hold, T2);
  const b3 = P.balance(r3.events, T2);
  check(r3.moved === 7201 && r3.parts.paid_sub === 3201 && r3.parts.paid_pack === 4000 && b3.total === 97201 && b3.paid_sub === 3201 && b3.paid_pack === 4000 && r3.hold.length === 0
    && r3.events.some(e => e.id === 'rel-tx-901-2' && e.amount === 3201 && e.expires === P.addDays(T2, 30)) && r3.events.some(e => e.id === 'rel-tx-903-1' && e.kind === 'purchase' && e.bucket === 'paid_pack' && e.amount === 4000 && !e.expires),
    '45日 あとでも あずかりは 消えない：サブスクの のこり 3,201P（rel-tx-901-2・その 日から 30日）→ パックの あずかり 4,000P（rel-tx-903-1・期限なし）の 順に 補充（合計 97,201P・あずかり 0）');
  // あきが 足りない ときは 古い 順に 入る ぶん だけ
  const r4 = P.holdRelease(P.spend(ev, 3500, '解放', 'dev1', T1), hold, T1);
  check(r4.moved === 3500 && r4.parts.paid_sub === 3201 && r4.parts.paid_pack === 299 && r4.hold.length === 1 && r4.hold[0].id === 'tx-903' && r4.hold[0].points === 3701, 'あきが 3,500P：サブスクの あずかり 3,201P ぜんぶ ＋ パックの あずかりから 299P（のこり 3,701P）');
  // 返金：その 取引の あずかりは 消す・台帳に 入った ぶん（はじめの ぶん＋補充した ぶん）を 引く
  const rf = P.refundEvent(ev, { id: '901', revokedAt: T1 });
  check(rf && rf.amount === -(4999 + 1000) && rf.bucket === 'paid_sub' && P.holdDrop(hold, '901').length === 1 && P.holdDrop(hold, '901')[0].id === 'tx-903' && P.holdDrop(hold, '999').length === 2,
    '返金：引く のは その 取引から 入った ぶん ぜんぶ（4,999＋補充 1,000）・その 取引の あずかりは 消す（ほかの 取引の あずかりは 残る）');
  const evr = ev.concat([rf]);
  check(P.balance(evr, T1).paid_sub === 0 && P.balance(evr, T1).lots.every(L => L.remain === 0), '返金の あと：その 取引の サブスクポイントは ぜんぶ 0（補充した lot も）');
  // 前の 版の 台帳（1つの 取引に できごと 1つ）は 今までどおり
  let evo = [P.giftEvent(T0)]; evo.push(P.txEvent(evo, tx('950', 'jp.tengel.app.points1000', '2026-11-10'))); evo.push(P.txEvent(evo, tx('951', 'jp.tengel.app.sub2000', '2026-11-10')));
  const rfo = P.refundEvent(evo, { id: '950' }), rfs = P.refundEvent(evo, { id: '951' });
  check(rfo.amount === -1000 && rfo.bucket === 'paid_pack' && rfs.amount === -2000 && P.balance(evo.concat([rfo, rfs]), T0).total === 1500, '前からの 返金（パック −1,000・サブスク −2,000）は 同じ');
  // トレーニングセンターの 当たり（獲得ポイント）も あずけられる・おかしな あずかりは 捨てる
  const ge = P.holdSplit(P.rowEvent({ id: 'tc-1', reward: 300, label: 'トレーニングセンターの お世話' }, T0), 100);
  check(ge.event.amount === 100 && ge.hold.kind === 'mission' && ge.hold.points === 200 && ge.hold.what === 'トレーニングセンターの お世話' && P.holdSum([ge.hold]).free === 200, '当たり 300P・あき 100P → 100P 入って 200P あずかり（獲得ポイント）');
  const gr = P.holdRelease([P.giftEvent(T0)], [ge.hold], T0);
  check(gr.moved === 200 && gr.events[1].kind === 'mission' && gr.events[1].bucket === 'free' && gr.events[1].id === 'rel-tc-1-1' && !gr.events[1].expires && P.balance(gr.events, T0).free === 1700, '補充すると 獲得ポイントに 入る（期限なし）');
  check(P.holdNorm([null, { id: '', kind: 'sub', points: 5 }, { id: 'a', kind: 'x', points: 5 }, { id: 'b', kind: 'sub', points: 0 }, { id: 'c', kind: 'sub', points: 12.4 }]).map(h => h.id + ':' + h.points).join() === 'c:12'
    && P.holdTotal(null) === 0 && P.holdNorm('x').length === 0, 'holdNorm：id・種類・P が そろった ものだけ（P は 整数に）');
}
// ---- 台帳の ならび（第4.139版：抜け穴を ふさぐ）：書いた 順に たどる・「使った」を まとめる のは いちばん あとの 1件だけ ----
console.log('台帳の ならび（書いた 順）：使った ぶんが かならず へる（第4.139版）');
{
  const J = (h, m, day) => Date.parse(`${day || '2026-11-10'}T${String(h).padStart(2, '0')}:${String(m || 0).padStart(2, '0')}:00+09:00`);
  const tot = (e, t) => P.balance(e, t).total;
  // ① その日 1回 使った あとに パックを 買う → そのあとの 読み込みも ちゃんと へる（前は その日の のこりが 0P で 読めた）
  let e1 = [P.giftEvent(J(9), 300)];
  e1 = P.spend(e1, 200, '読み込み A', 'd', J(10, 5));
  e1.push(P.txEvent(e1, { id: '700', product: 'jp.tengel.app.points500', date: new Date(J(12)).toISOString() }, J(12)));
  check(tot(e1, J(12)) === 600, '① 300P → 1回 読む（100P）→ パック 500P を 買う ＝ 600P');
  let n1 = 0; for (let i = 0; i < 9; i++) { const x = P.spend(e1, 200, '読み込み ' + i, 'd', J(12, 10 + i)); if (!x) break; e1 = x; n1++; }
  check(n1 === 3 && tot(e1, J(13)) === 0, `① そのあと 読めるのは 3回だけ（600P ぶん）・のこり 0P（${n1}回・${tot(e1, J(13))}P）`);
  const sp1 = e1.filter(x => x.kind === 'spend');
  check(sp1.length === 2 && sp1[0].id === 'spend-d-2026-11-10' && sp1[0].amount === -200 && sp1[1].id === 'spend-d-2026-11-10-2' && sp1[1].amount === -600 && sp1[1].what.length === 3 && sp1[1].use.paid_pack === 500 && sp1[1].use.free === 100,
    '① 買う 前の「使った」（1件）には 足さない・買った あとは 新しい 1件（-2）に まとめる（3回ぶん）');
  check(e1.map(x => x.n).join() === '1,2,3,4', '① できごとに 書いた 順の 番号（プレゼント 1・使った 2・パック 3・使った 4）');
  // ② ミッションを 受け取った あと・サブスクが 届いた あとも 同じ
  let e2 = [P.giftEvent(J(9), 200)];
  e2 = P.spend(e2, 200, 'A', 'd', J(10));
  e2.push(P.rowEvent({ id: 'm-x', reward: 500, label: 'ミッション' }, J(10, 30)));
  let n2 = 0; for (let i = 0; i < 9; i++) { const x = P.spend(e2, 200, 'r' + i, 'd', J(11, i)); if (!x) break; e2 = x; n2++; }
  check(n2 === 2 && tot(e2, J(12)) === 100, `② 0P に なった あと ミッション 500P → 読めるのは 2回・のこり 100P（${n2}回・${tot(e2, J(12))}P）`);
  e2.push(P.txEvent(e2, { id: '701', product: 'jp.tengel.app.sub2000', date: new Date(J(13)).toISOString() }, J(13)));
  let n2b = 0; for (let i = 0; i < 20; i++) { const x = P.spend(e2, 200, 's' + i, 'd', J(13, 5 + i)); if (!x) break; e2 = x; n2b++; }
  check(n2b === 10 && tot(e2, J(14)) === 100 && P.balance(e2, J(14)).paid_sub === 0, `② サブスク 2,000P が 届いた あと → 読めるのは 10回・サブスクポイントは 0P（${n2b}回・${tot(e2, J(14))}P）`);
  // ③ 時計を 進めて ミッションを 受け取り、時計を もどす → その ポイントも 使えば へる（前は いくら 使っても へらなかった）
  let e3 = [P.giftEvent(J(9), 100)];
  e3.push(P.rowEvent({ id: 'm-future', reward: 500, label: 'ミッション' }, J(9, 0, '2027-11-10')));      // 1年 先の 時刻
  let n3 = 0; for (let i = 0; i < 9; i++) { const x = P.spend(e3, 200, 'f' + i, 'd', J(10, i)); if (!x) break; e3 = x; n3++; }
  check(n3 === 3 && tot(e3, J(11)) === 0 && tot(e3, J(11, 0, '2027-12-01')) === 0, `③ 100P＋先の 時刻の 500P → 読めるのは 3回・のこり 0P（${n3}回・${tot(e3, J(11))}P）`);
  // ④ 買った 時刻（Apple の 時計）が 端末の 時計より 少し 先・端末の 時計を もどして 使う
  let e4 = [P.giftEvent(J(9), 100)];
  e4.push(P.txEvent(e4, { id: '702', product: 'jp.tengel.app.points500', date: new Date(J(10, 2)).toISOString() }, J(10)));   // 端末は 10:00・取引は 10:02
  e4 = P.spend(e4, 200, 'すぐ 読む', 'd', J(10, 1));
  check(tot(e4, J(10, 1)) === 400 && P.balance(e4, J(10, 1)).paid_pack === 300, '④ 取引の 時刻が 端末より 先でも、買った あとの 読み込みは へる（600 → 400P：購入ポイントから 200P）');
  e4 = P.spend(e4, 200, '時計を もどして 読む', 'd', J(8, 0, '2026-11-01'));
  e4 = P.spend(e4, 200, 'もう 1回', 'd', J(8, 1, '2026-11-01'));
  check(tot(e4, J(10, 5)) === 0 && P.spend(e4, 200, 'x', 'd', J(8, 2, '2026-11-01')) === null, '④ 端末の 時計を もどして 使っても へる（0P）・足りなければ 使えない');
  // ⑤ 解放（unlock）も 書いた 順
  let e5 = [P.giftEvent(J(9), 100)];
  e5.push(P.rowEvent({ id: 'm-f2', reward: 500, label: 'ミッション' }, J(9, 0, '2027-11-10')));
  e5 = P.unlock(e5, 'type:複勝', 500, 'd', J(10));
  check(tot(e5, J(10)) === 100 && e5[e5.length - 1].n === 3 && P.unlock(e5, 'type:枠複', 500, 'd', J(10, 1)) === null, '⑤ 解放も 同じ（先の 時刻の 500P で 解放 → のこり 100P・番号は いちばん あと）');
  // ⑥ 前の 版の 台帳（番号なし）：番号を ふっても 残高は 前と 同じ（時刻の 順の まま）
  const old6 = [
    { id: 'gift-first', kind: 'gift', bucket: 'free', amount: 1500, at: new Date(J(9)).toISOString() },
    { id: 'tx-9', kind: 'purchase', bucket: 'paid_pack', amount: 500, at: new Date(J(12)).toISOString(), product: 'jp.tengel.app.points500', tx: '9' },
    { id: 'spend-d-2026-11-10', kind: 'spend', bucket: '', amount: -3600, at: new Date(J(10, 5)).toISOString(), use: { paid_sub: 0, paid_pack: 2400, free: 1200 }, what: ['a'], device: 'd', last: new Date(J(12, 21)).toISOString() },
    { id: 'mission-rec-8', kind: 'mission', bucket: 'free', amount: 500, at: new Date(J(11)).toISOString(), what: 'x' }
  ];
  const b6a = P.balance(old6, J(13)), cp6 = JSON.parse(JSON.stringify(old6)); P.stampAll(cp6); const b6b = P.balance(cp6, J(13));
  check(b6a.total === 1300 && b6b.total === b6a.total && b6b.paid_pack === b6a.paid_pack && b6b.free === b6a.free && cp6.map(x => x.id + ':' + x.n).join() === 'gift-first:1,tx-9:4,spend-d-2026-11-10:2,mission-rec-8:3',
    '⑥ 前の 版の 台帳は 時刻の 順に 番号（残高は 前と 同じ 1,300P）');
  let e6 = P.spend(cp6, 200, '新しい 読み込み', 'd', J(13));
  check(tot(e6, J(13)) === 1100 && e6.length === 5 && e6[4].id === 'spend-d-2026-11-10-2' && e6[4].n === 5 && e6[2].amount === -3600, '⑥ そのあとの 読み込みは 新しい 1件（前の「使った」には 足さない）・ちゃんと へる（1,100P）');
  // ⑦ 足した ばかりで 番号の ない できごと：stamp は ならんで いる 順・番号つきの あと
  const e7 = [{ id: 'a', kind: 'gift', bucket: 'free', amount: 100, at: new Date(J(9)).toISOString(), n: 5 }, { id: 'b', kind: 'mission', bucket: 'free', amount: 10, at: new Date(J(8)).toISOString() }, { id: 'c', kind: 'mission', bucket: 'free', amount: 10, at: new Date(J(7)).toISOString() }];
  P.stamp(e7);
  check(e7.map(x => x.n).join() === '5,6,7' && P.seqMax(e7) === 7 && P.seqMax([]) === 0 && P.stamp([]).length === 0, '⑦ stamp：番号の ない できごとに、ならんで いる 順に つづきの 番号（ある 番号は かえない）');
  // ⑧ その日の「使った」の 1回め から 今までに 期限が 切れた サブスクの ぶんからは 引かない（新しい 1件）
  let e8 = [P.giftEvent(J(9, 0, '2026-10-01'), 100)];
  e8.push(P.txEvent(e8, { id: '801', product: 'jp.tengel.app.sub2000', date: new Date(J(15, 0, '2026-10-11')).toISOString() }, J(15, 0, '2026-10-11')));   // 11/10 15:00 に 切れる
  e8.push(P.txEvent(e8, { id: '802', product: 'jp.tengel.app.sub2000', date: new Date(J(9, 0, '2026-11-09')).toISOString() }, J(9, 0, '2026-11-09')));
  e8 = P.spend(e8, 200, '切れる 前', 'd', J(14));
  check(P.balance(e8, J(14)).lots.map(L => L.remain).join() === '1800,2000', '⑧ 切れる 前（14:00）：期限が 近い ぶんから 引く（1,800・2,000）');
  e8 = P.spend(e8, 200, '切れた あと', 'd', J(16));
  const b8 = P.balance(e8, J(16));
  check(b8.paid_sub === 1800 && b8.lost === 1800 && b8.total === 1900 && e8.filter(x => x.kind === 'spend').length === 2, `⑧ 切れた あと（16:00）：切れた 1,800P は 消える・のこりの ぶんから 引く（サブスクポイント 1,800P・合計 1,900P）（${b8.paid_sub}・${b8.lost}・${b8.total}）`);
  // ⑨ いつもの まとめ方：間に 何も なければ 同じ 日は 1件・日が かわれば 別の 1件
  let e9 = [P.giftEvent(J(9), 1500)];
  for (let i = 0; i < 3; i++) e9 = P.spend(e9, 200, 'r' + i, 'd', J(10, i));
  e9 = P.spend(e9, 200, 'つぎの日', 'd', J(10, 0, '2026-11-11'));
  check(e9.filter(x => x.kind === 'spend').map(x => x.id + ':' + x.amount).join() === 'spend-d-2026-11-10:-600,spend-d-2026-11-11:-200' && tot(e9, J(11, 0, '2026-11-11')) === 700, '⑨ 間に 何も なければ 同じ 日は 1件（-600）・日が かわれば 別の 1件');
}
// ---- あばれテスト（第4.139版）：端末の 時計を 進めたり もどしたり しながら 足す・使う・返金・解放 → 使った ぶんは かならず ちょうど へる ----
{
  let seed = 20261110; const rnd = () => (seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648, pick = a => a[Math.floor(rnd() * a.length)];
  const BASE = Date.parse('2026-11-10T03:00:00Z'), DAYMS = 86400000;
  let bad = [], spends = 0, merged = 0;
  for (let run = 0; run < 80 && bad.length < 5; run++) {
    let fe = [], real = BASE, txn = 0;
    for (let step = 0; step < 60; step++) {
      real += Math.floor(rnd() * 6 * 3600000);
      const now = real + pick([0, 0, 0, 0, -3 * DAYMS, 400 * DAYMS, -40 * DAYMS, 120000, -120000, 20 * DAYMS]), op = rnd(), before = P.balance(fe, now).total;
      if (op < 0.12) fe.push(P.rowEvent({ id: 'fz' + run + '-' + step, reward: pick([100, 300, 500, 2000]), label: 'x' }, now));
      else if (op < 0.22) { const e = P.txEvent(fe, { id: String(++txn), product: pick(['jp.tengel.app.points500', 'jp.tengel.app.points1000', 'jp.tengel.app.sub2000', 'jp.tengel.app.sub4400']), date: new Date(real + pick([0, 90000, -3 * DAYMS])).toISOString() }, now); if (e) fe.push(e); }
      else if (op < 0.26 && txn) { const rf = P.refundEvent(fe, { id: String(1 + Math.floor(rnd() * txn)) }, now); if (rf) fe.push(rf); }
      else if (op < 0.34) { const cost = pick([0, 500, 800]), nx = P.unlock(fe, 'fk' + run + '-' + step, cost, 'd', now); if (nx) { if (P.balance(nx, now).total !== before - cost) bad.push(`解放 ${run}-${step}`); fe = nx; } }
      else {
        const amt = pick([200, 200, 200, 500]), ok = P.plan(fe, amt, now).ok, nx = P.spend(fe, amt, 'r', 'd', now);
        if (!nx) { if (ok) bad.push(`使えるのに 使えない ${run}-${step}`); continue; }
        spends++; if (nx.length === fe.length) merged++;
        if (P.balance(nx, now).total !== before - amt) bad.push(`使った ${run}-${step}：${before} − ${amt} ≠ ${P.balance(nx, now).total}`);
        fe = nx;
      }
      P.stamp(fe);
      if (new Set(fe.map(e => e.n)).size !== fe.length || new Set(fe.map(e => e.id)).size !== fe.length) bad.push(`番号か id が 重なった ${run}-${step}`);
    }
  }
  check(!bad.length && spends > 1500 && merged > 300, `あばれテスト：時計を 進める・もどす・ずらす 中で ${spends}回 使って、ぜんぶ ちょうど へった（まとめた のは ${merged}回・番号と id は 重ならない）${bad.length ? '：' + bad.join('／') : ''}`);
}
// ---- 読み直しの 見分け：読んだ 中身（第4.140版・11/10 14:22「きびしくする（人気の並びが前とぜんぜん違ったら200P。同じレースの読み直しは0Pのまま）」）----
console.log('読み直しの 見分け：読んだ 単勝の 表を くらべる（第4.140版）');
{
  const rows = a => a.map((t, i) => ({ no: i + 1, tan: String(t) }));
  const A = rows([12.4, 4.1, 31.5, 9.8, 18.2, 2.4, 7.6, 54.0, 25.9, 6.3, 14.7, 88.6]);            // 9R
  const A2 = rows([13.1, 3.8, 35.2, 10.4, 16.9, 2.6, 7.1, 61.3, 24.0, 6.8, 15.5, 97.4]);          // 同じ レース・オッズが 動いた
  const B = rows([3.3, 45.2, 5.8, 120.4, 2.2, 66.1, 15.5, 8.9, 4.7, 30.3, 99.9, 11.1]);            // 別の レース
  const fa = P.raceFp(A), fa2 = P.raceFp(A2), fb = P.raceFp(B);
  check(fa === '1:12.4,2:4.1,3:31.5,4:9.8,5:18.2,6:2.4,7:7.6,8:54,9:25.9,10:6.3,11:14.7,12:88.6' && P.raceFp(null) === '' && P.raceFp([]) === ''
    && P.raceFp([{ no: 3, tan: '5.5' }, { no: 'x', tan: 2 }, { no: 2, tan: 0 }, { no: 3, tan: 9 }, { no: 1, tan: '２.４' }, null]) === '3:5.5', '指紋＝馬番:単勝 を 馬番の 順に（読めない 行・同じ 馬番の 2つめは すてる）');
  check(P.TICKET_POINTS === 7000, 'チケット 1枚を かえられる ポイント＝7,000P（第4.141版・いちばん 高い 壁紙と 同じ）');
  // 第4.165版（まさちゃん 2026/11/13 11:46「お世話トークンは、購入できるようにする。①1個を80Pで購入 ②5個を400Pで購入 ③10個を800Pで購入 ④15個を1200Pで購入 ②25個を2000Pで購入」）
  // 第4.168版（まさちゃん 2026/11/14 01:26「お世話トークン購入金額 ・1個100P ・5個500P ・10個1000P ・15個1500P ・20個2000P ・25個2500P」）：1こ 80P → 100P・20この 組を 足した（6つ）
  check(JSON.stringify(P.TOKEN_PACKS) === '[[1,100],[5,500],[10,1000],[15,1500],[20,2000],[25,2500]]' && P.TOKEN_PACKS.every(([n, c]) => c === n * 100) && JSON.stringify(P.tokenPack(10)) === '[10,1000]' && JSON.stringify(P.tokenPack('5')) === '[5,500]'
    && JSON.stringify(P.tokenPack(20)) === '[20,2000]' && P.tokenPack(2) === null && P.tokenPack(0) === null && P.tokenPack(26) === null && P.tokenPack('x') === null && (P.tokenPack(5)[1] = 1, P.TOKEN_PACKS[1][1] === 500),
    'お世話トークンの 購入の 組（1こ 100P・5こ 500P・10こ 1,000P・15こ 1,500P・20こ 2,000P・25こ 2,500P＝どれも 1こ 100P）・表に ない 数は ない・返した 組を 書きかえても 表は かわらない');
  { const N0 = Date.UTC(2026, 10, 13, 3, 0, 0), tot = (e, t) => P.balance(e, t).total, ev0 = [P.giftEvent(N0, 1500, 'gift-t', 'テスト')];
    const a = P.unlock(ev0, 'tctok:5:b1abc-x9', 500, 'dev', N0 + 1000), b = a && P.unlock(a, 'tctok:5:b1abc-x9', 500, 'dev', N0 + 2000), c = a && P.unlock(a, 'tctok:1:b2', 100, 'dev', N0 + 3000), c2 = c && P.unlock(c, 'tctok:5:b4', 500, 'dev', N0 + 3500), d = c2 && P.unlock(c2, 'tctok:5:b3', 500, 'dev', N0 + 4000);
    check(tot(ev0, N0) === 1500 && !!a && tot(a, N0 + 1000) === 1000 && a[a.length - 1].id === 'unlock-tctok:5:b1abc-x9' && a[a.length - 1].amount === -500 && a[a.length - 1].what === 'tctok:5:b1abc-x9' && P.unlocked(a, 'tctok:5:b1abc-x9') && !P.unlocked(a, 'tctok:5:b2')
      && !!b && b.length === a.length && tot(b, N0 + 2000) === 1000 && !!c && tot(c, N0 + 3000) === 900 && !!c2 && tot(c2, N0 + 3500) === 400 && d === null,
      '台帳：お世話トークンの 購入は「unlock-tctok:<こ数>:<買い物の 番号>」で 1件ずつ（−500P）・同じ 番号は 2回 へらない・足りない ときは 買えない（のこり 400P で 500P は 買えない）'); }
  check(P.FP.min === 6 && P.FP.rho === 0.3 && P.FP.same === 0.5, 'しきい値：どちらにも ある 馬番 6頭 以上・順位の 相関 0.3 より 低い・同じ オッズ 半分 より 少ない');
  check(P.fpRho(fa, fa2) > 0.95 && P.fpShare(fa, fa2) === 0 && P.fpDiff(fa, fa2) === false, `同じ レース（オッズが 動いた だけ）：人気の 順は ほぼ 同じ → 同じ レース（相関 ${P.fpRho(fa, fa2).toFixed(2)}）`);
  check(P.fpRho(fa, fb) < 0 && P.fpShare(fa, fb) === 0 && P.fpDiff(fa, fb) === true && P.fpDiff(fb, fa) === true, `別の レース：人気の 順も オッズも ちがう → 別の レース（相関 ${P.fpRho(fa, fb).toFixed(2)}）`);
  const sh = P.raceFp(A.map((h, i) => ({ no: h.no, tan: A[(i + 5) % 12].tan })));                  // 同じ 画像・馬番との 組み合わせが ずれた
  check(P.fpRho(fa, sh) < 0.3 && P.fpShare(fa, sh) === 1 && P.fpDiff(fa, sh) === false, '同じ 画像を 読み直して 組み合わせが ずれた だけ（オッズの 数は 同じ）→ 同じ レース');
  check(P.fpDiff(P.raceFp(A.slice(0, 7)), fa2) === false && P.fpDiff(P.raceFp(A.slice(0, 7)), fb) === true, 'はじめは 7頭だけ 読めた → あとで ぜんぶ：どちらにも ある 馬番で くらべる（同じ レースは 同じ・別の レースは 別）');
  check(P.fpDiff(P.raceFp(A.slice(0, 5)), fb) === false && P.fpRho(P.raceFp(A.slice(0, 5)), fb) === null && P.fpDiff('', fb) === false && P.fpDiff(fa, '') === false && P.fpDiff(null, undefined) === false,
    'くらべられない とき（どちらにも ある 馬番が 5頭 以下・どちらかに 表が ない）は 同じ レースと 見る（前と 同じ）');
  const tie = P.raceFp(rows([5, 5, 5, 5, 5, 5, 5])), tie2 = P.raceFp(rows([2, 2, 9, 9, 4, 4, 30]));
  check(P.fpRho(tie, fb) === null && P.fpDiff(tie, fb) === false && Math.abs(P.fpRho(tie2, tie2) - 1) < 1e-9, '同じ オッズ（同じ 順位）は 平均の 順位で 数える・ぜんぶ 同じなら くらべない');
  // 相関の きょうかい：0.3 より 低く、同じ 数が 半分 より 少ない とき だけ 別
  const half = P.raceFp(B.map((h, i) => ({ no: h.no, tan: i < 6 ? A[i].tan : h.tan })));           // 半分は 前と 同じ 数
  check(P.fpShare(fa, half) === 0.5 && P.fpDiff(fa, half) === false, '同じ オッズが ちょうど 半分 → 同じ レースと 見る（半分 より 少ない とき だけ 別）');
}
console.log('結果：', fails.length ? fails.length + '件おかしい' : 'OK');
process.exit(fails.length ? 1 : 0);
