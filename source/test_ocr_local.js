// 画像の読み取り（アプリ版・端末の中で読んだ文字から表を組み立てる ocr_local.js）のテスト
//   node test_ocr_local.js            … testdata/ocr/（testdata/ocr/make_mock.py で作った架空のオッズ画面）
// 架空のオッズ画面（枠つき・人気順・3連単の人気順・矢印）を、セルごと／行ごとにまとまった「読めた文字」として渡して、同じ答えになるか。
// 本物の文字認識（Apple の Vision）で読んだ結果は、GitHubのMac（ios/ci/selftest.js の ocr）で確かめる
const fs = require('fs'), path = require('path');
const O = require('./ocr_local.js');
const DIR = process.argv[2] || path.join(__dirname, 'testdata', 'ocr');
let fails = [];
function check(c, label) { console.log((c ? '  ✅ ' : '  ❌ ') + label); if (!c) fails.push(label); }
function load(n) { return JSON.parse(fs.readFileSync(path.join(DIR, n + '.json'), 'utf8')).lines; }
// 行ごとにまとまって読めたとき（Vision は列の間がせまいと1つの行として返す）
function merged(lines) {
  return O.rows(lines).map(r => ({ text: r.items.map(i => i.text).join(' '), x: r.items[0].x, y: r.items[0].y, w: r.items[r.items.length - 1].x + r.items[r.items.length - 1].w - r.items[0].x, h: r.h }));
}
const EXP = [[1, 12.4, '3.0-4.6'], [2, 4.1, '1.6-2.2'], [3, 31.5, '6.1-9.8'], [4, 9.8, '2.6-3.9'], [5, 18.2, '4.0-6.2'], [6, 2.4, '1.1-1.3'], [7, 7.6, '2.1-3.1'], [8, 54.0, '9.4-15.0'], [9, 25.9, '5.2-8.1'], [10, 6.3, '1.9-2.7'], [11, 14.7, '3.3-5.1'], [12, 88.6, '13.2-21.1']];
function checkHorses(d, label) {
  const hs = d.horses || [];
  const same = hs.length === 12 && EXP.every((e, i) => hs[i] && hs[i].no === e[0] && hs[i].tan === e[1] && hs[i].fuku === e[2]);
  check(same, label + '：単勝・複勝12頭 ' + JSON.stringify(hs.slice(0, 3)));
}
const a = load('a_tanfuku_waku'), b = load('b_tanfuku_ninki'), c = load('c_sanrentan'), d = load('d_sanrentan_arrow');
for (const [name, lines] of [['A 枠つき（セルごと）', a], ['A 枠つき（行ごと）', merged(a)]]) {
  const r = O.parse([lines]);
  console.log(name, JSON.stringify({ venue: r.venue, date: r.date, r: r.r, dist: r.dist, surface: r.surface, baba: r.baba, n: r.n }));
  check(r.venue === '大井' && r.r === 9 && r.dist === 1400 && r.surface === 'ダ' && r.baba === '良' && r.n === 12 && r.date === new Date().getFullYear() + '-10-14', name + '：レース情報');
  checkHorses(r, name);
  check(r.s1 === null && r.s5 === null && r.s10 === null, name + '：3連単は無し（null）');
}
for (const [name, lines] of [['B 人気順・取消あり（セルごと）', b], ['B 人気順・取消あり（行ごと）', merged(b)]]) {
  const r = O.parse([lines]);
  console.log(name, JSON.stringify({ venue: r.venue, date: r.date, r: r.r, dist: r.dist, surface: r.surface, baba: r.baba, n: r.n }));
  check(r.venue === '大井' && r.r === 9 && r.dist === 1400 && r.surface === 'ダ' && r.baba === '良' && r.date === '2026-10-14', name + '：レース情報');
  checkHorses(r, name);
  check(r.n === 12, name + '：出走頭数は取消を除いた12頭（画面の「13頭」ではなく、表に残っている馬の数）');
}
for (const [name, lines] of [['C 3連単 人気順（セルごと）', c], ['C 3連単 人気順（行ごと）', merged(c)], ['D 3連単 矢印・順位なし（セルごと）', d], ['D 3連単 矢印・順位なし（行ごと）', merged(d)]]) {
  const r = O.parse([lines]);
  console.log(name, JSON.stringify({ s1: r.s1, s5: r.s5, s10: r.s10, docs: r._docs }));
  check(r.s1 && r.s1.combo === '6-2-10' && r.s1.odds === 18.5 && r.s5 && r.s5.combo === '2-10-6' && r.s5.odds === 41.3 && r.s10 && r.s10.combo === '6-10-7' && r.s10.odds === 84.0, name + '：1位・5位・10位');
  check(r.horses === null, name + '：単勝の表は無し');
  check(r.venue === '大井' && r.r === 9, name + '：開催場とR');
}
// 2枚（単複＋3連単）をまとめる
{
  const r = O.parse([a, c]);
  check(r.horses && r.horses.length === 12 && r.s1 && r.s1.combo === '6-2-10' && r.n === 12 && r.baba === '良', '2枚をまとめる（単複＋3連単）');
  const r2 = O.parse([c, b]);
  check(r2.horses && r2.horses.length === 12 && r2.s5 && r2.s5.odds === 41.3 && r2.date === '2026-10-14', '2枚をまとめる（3連単が先でも）');
}
// 読み方のゆれ：「1.1-」「1.3」に割れる・全角・「倍」・枠と馬番がくっつく・斤量が写る
{
  const lines = [
    { text: '○○競馬場 11R ダート1200m 稍重 10頭', x: 0.05, y: 0.02, w: 0.9, h: 0.02 },
    { text: '1 1 ハナ 56.0 3.5 1.4-', x: 0.05, y: 0.10, w: 0.6, h: 0.02 }, { text: '1.8', x: 0.70, y: 0.10, w: 0.05, h: 0.02 },
    { text: '２ ２ フタ ５４．０ ２．１ １．１－１．３', x: 0.05, y: 0.14, w: 0.7, h: 0.02 },
    { text: '33 ミツ 55.0 12.8倍 3.2-5.5倍', x: 0.05, y: 0.18, w: 0.7, h: 0.02 },
    { text: '4', x: 0.05, y: 0.22, w: 0.02, h: 0.02 }, { text: '4', x: 0.09, y: 0.22, w: 0.02, h: 0.02 }, { text: 'ヨン', x: 0.14, y: 0.22, w: 0.1, h: 0.02 }, { text: '54.0', x: 0.4, y: 0.22, w: 0.06, h: 0.02 }, { text: '7.7', x: 0.55, y: 0.22, w: 0.05, h: 0.02 }, { text: '2.0', x: 0.65, y: 0.22, w: 0.05, h: 0.02 }, { text: '-', x: 0.71, y: 0.22, w: 0.01, h: 0.02 }, { text: '3.1', x: 0.74, y: 0.22, w: 0.05, h: 0.02 },
    { text: '5 5 ゴ 55.0 取消', x: 0.05, y: 0.26, w: 0.6, h: 0.02 }
  ];
  const r = O.parse([lines]);
  console.log('ゆれ', JSON.stringify(r.horses), r.venue, r.r, r.dist, r.surface, r.baba, r.n);
  check(r.r === 11 && r.dist === 1200 && r.surface === 'ダ' && r.baba === '稍重' && r.n === 10, 'ゆれ：レース情報');
  check(r.horses && r.horses.length === 4 && r.horses[0].tan === 3.5 && r.horses[0].fuku === '1.4-1.8' && r.horses[1].tan === 2.1 && r.horses[1].fuku === '1.1-1.3' && r.horses[2].no === 3 && r.horses[2].tan === 12.8 && r.horses[2].fuku === '3.2-5.5' && r.horses[3].tan === 7.7 && r.horses[3].fuku === '2.0-3.1', 'ゆれ：割れた範囲・全角・倍・くっついた枠と馬番・斤量を外す・取消を除く');
  check(r.venue === null, 'ゆれ：「○○競馬場」は開催場にしない（記号）');
}
// 単勝の表と複勝の表が別々に並ぶ画面・日付が「10/14(水)」
{
  var L = [{ text: '○○ 7R 10/14(水) 芝1600m', x: 0.05, y: 0.02, w: 0.9, h: 0.02 }, { text: '単勝', x: 0.05, y: 0.06, w: 0.1, h: 0.02 }];
  [[1, 3.5], [2, 2.1], [3, 12.8], [4, 7.7]].forEach(function (h, i) { L.push({ text: h[0] + ' ウマ' + h[0] + ' ' + h[1], x: 0.05, y: 0.10 + i * 0.04, w: 0.5, h: 0.02 }); });
  L.push({ text: '複勝', x: 0.05, y: 0.30, w: 0.1, h: 0.02 });
  [[1, '1.4-1.8'], [2, '1.1-1.3'], [3, '3.2-5.5'], [4, '2.0-3.1']].forEach(function (h, i) { L.push({ text: h[0] + ' ウマ' + h[0] + ' ' + h[1], x: 0.05, y: 0.34 + i * 0.04, w: 0.5, h: 0.02 }); });
  const r = O.parse([L]);
  console.log('別表', JSON.stringify(r.horses), r.date, r.dist, r.surface);
  check(r.horses && r.horses.length === 4 && r.horses[1].tan === 2.1 && r.horses[1].fuku === '1.1-1.3' && r.horses[3].fuku === '2.0-3.1', '単勝の表と複勝の表が別でも、同じ馬番でつなぐ');
  check(r.date === new Date().getFullYear() + '-10-14' && r.dist === 1600 && r.surface === '芝' && r.r === 7, '日付「10/14(水)」・芝1600m・7R');
}
// 何も読めない（オッズ表のない画面）
{
  const r = O.parse([[{ text: 'ようこそ', x: 0.1, y: 0.1, w: 0.3, h: 0.03 }, { text: 'お知らせ 10月14日', x: 0.1, y: 0.2, w: 0.3, h: 0.03 }]]);
  check(r.horses === null && r.s1 === null && r.r === null && r.n === null, '表のない画面：何も入れない（推測しない）');
}
// 発走時刻・レース名（同じレースの読み直しの見分けに使う。読めないときは null・推測しない）
{
  const L = (ts) => ts.map((t, i) => ({ text: t, x: 0.05, y: 0.05 + i * 0.04, w: 0.6, h: 0.03 }));
  check(O.parse([a]).start === '18:05' && O.parse([a]).rname === null && O.parse([c]).start === null, 'A：発走 18:05・レース名はなし（C：時刻なし）');
  check(O.parseOne(L(['○○競馬場 第9競走 はなまる特別', 'ダ1400m 12頭 馬場:良 発走 15:40'])).rname === 'はなまる特別', 'レース名：第9競走のあとの言葉');
  check(O.parseOne(L(['12R 東京盃 ダ1200m 発走 20:10'])).rname === '東京盃' && O.parseOne(L(['第9競走 C2 選抜 ダ1400m'])).rname === 'C2選抜', 'レース名：距離の手前まで・2語までつなぐ');
  check(O.parseOne(L(['9R 良 12頭'])).rname === null && O.parseOne(L(['9R ダ1400m 発走15:40'])).rname === null && O.parseOne(L(['9R ダ1400m 発走15:40'])).start === '15:40', '馬場・距離はレース名にしない・「発走15:40」も読む');
  check(O.parseOne(L(['10:30 12R', '13:45 3連単'])).start === null && O.parseOne(L(['3連単 締切 16:20'])).start === '16:20', '時刻が2つあると決めない・1つなら発走とみなす');
}
console.log('FAILS', fails.length, fails);
process.exit(fails.length ? 1 : 0);
