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
console.log('結果：', fails.length ? fails.length + '件おかしい' : 'OK');
process.exit(fails.length ? 1 : 0);
