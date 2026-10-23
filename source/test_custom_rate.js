// 買い目カスタムの %（custom_rate.js）の テスト：node test_custom_rate.js
//   全部 選んだ 時は ゾーンの 参考的中率（engine.js の 集計）と 同じ 値に なる こと・選ぶ 馬を へらすと 値が かわる こと
const fs = require('fs');
const T = require('./engine.js');
const C = require('./custom_rate.js');
let fails = [];
function check(c, label) { console.log((c ? '  ✅ ' : '  ❌ ') + label); if (!c) fails.push(label); }
const J = x => JSON.stringify(x);
const hist = JSON.parse(fs.readFileSync('hist_280.json', 'utf8'));
const list = hist.map(r => T.derive(r));
const S = T.stats(list);

// A層 第1（人気→人気）：全部 選んだ 時 ＝ ゾーンの 値（82/151）。3着（人気・中穴）も 67/82 の 成立数と 同じ
let r = C.rate(list, 'A', { a: C.zoneRanks('人気'), b: C.zoneRanks('人気'), t: C.zoneRanks('人気・中穴') });
check(r.n === S.k.A.n && r.hit === S.k.A.hit[0] && r.hit3 === S.k.A.tri3[0], `A層 人気→人気：${r.hit}/${r.n}（ゾーンの 値 ${S.k.A.hit[0]}/${S.k.A.n}）・3連単 ${r.hit3}（成立 ${S.k.A.tri3[0]}）`);
// B層 第2（人気→大穴）：7/92
r = C.rate(list, 'B', { a: C.zoneRanks('人気'), b: C.zoneRanks('大穴'), t: null });
check(r.n === S.k.B.n && r.hit === S.k.B.hit[1] && r.n3 === 0, `B層 人気→大穴：${r.hit}/${r.n}（ゾーンの 値 ${S.k.B.hit[1]}/${S.k.B.n}）`);
// C層 第2段階 第1（人気→大穴／超大穴）：2つ つながった ゾーン
r = C.rate(list, 'C2', { a: C.zoneRanks('人気'), b: C.zoneRanks('大穴／超大穴'), t: null });
check(r.n === S.k.C2.n && r.hit === S.k.C2.hit[0], `C層 第2段階 人気→大穴／超大穴：${r.hit}/${r.n}（ゾーンの 値 ${S.k.C2.hit[0]}/${S.k.C2.n}）`);
// 1着側を 1番人気だけに しぼると へる
const r1 = C.rate(list, 'A', { a: [1], b: [1, 2, 3], t: null });
check(r1.n === S.k.A.n && r1.hit < S.k.A.hit[0] && r1.hit > 0, `A層 1着を 1番人気だけ：${r1.hit}/${r1.n}（全部 ${S.k.A.hit[0]}）`);
// 2着側を 2・3番人気に しぼる＝1番人気→1番人気は 出ないので 同じ
const r2 = C.rate(list, 'A', { a: [1], b: [2, 3], t: null });
check(r2.hit === r1.hit, '1着が 1番人気 なら 2着側から 1番人気を 外しても 同じ 値');
// 自己参照の 除外
const ex = list.find(x => x.kubun === 'A' && x.hit === 1);
const r3 = C.rate(list, 'A', { a: C.zoneRanks('人気'), b: C.zoneRanks('人気'), t: null }, ex.id);
check(r3.n === S.k.A.n - 1 && r3.hit === S.k.A.hit[0] - 1, `自己参照の 除外（${ex.id}）：${r3.hit}/${r3.n}`);
// 単勝5連予想（1着の 人気）
const f = C.first(list, 'A', [1, 2, 3]);
const z1n = list.filter(x => x.inStats && x.kubun === 'A' && x.z1 === '人気').length;
check(f.n === S.k.A.n && f.hit === z1n, `1着の 人気（A層・人気）：${f.hit}/${f.n}（z1=人気 ${z1n}）`);
// 馬番 → 人気順位
const horses = [{ no: 6, rank: 1 }, { no: 2, rank: 2 }, { no: 10, rank: 3 }, { no: 7, rank: 4 }];
check(J(C.ranksOf(horses, [10, 6, 99])) === J([1, 3]) && J(C.zoneRanks('大穴／超大穴')) === J([7, 8, 9, 10, 11, 12]) && C.pct(41, 98) === '41.8%' && C.pct(0, 0) === '—', '馬番→人気順位・ゾーン→人気順位・%の 書き方');
console.log('結果：', fails.length ? 'NG ' + fails.length : 'OK');
process.exit(fails.length ? 1 : 0);
