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
// 結果の画面（着順と払戻）：予約したレースの結果入力（第2弾・12.1 ※仮）
{
  const L = (ts, x0 = 0.05) => ts.map((t, i) => ({ text: t, x: x0, y: 0.05 + i * 0.035, w: 0.8, h: 0.025 }));
  // 表（見出しあり）＋払戻。4着・除外の馬・競走中止の馬は着に入れない
  const A = L(['レース結果 第9競走 はなまる特別', '着順 枠 馬番 馬名 性齢 斤量 騎手 タイム 人気', '1 3 6 ハナ 牡4 56.0 きしゅ 1:25.3 2', '2 1 2 フタ 牝3 54.0 きしゅ 1:25.5 1', '3 6 10 トオ 牡5 57.0 きしゅ 1:25.9 3',
    '4 2 4 ヨン 牡4 56.0 きしゅ 1:26.0 5', '5 11 ゴ 牡6 56.0 きしゅ 競走除外', '7 7 ナナ 牡3 55.0 きしゅ 競走中止', '払戻金', '単勝 6 240円 2人気', '複勝 6 120円', '複勝 2 180円', '複勝 10 310円',
    '枠連 1-3 1,230円', '馬連 2-6 530円', 'ワイド 2-6 220円', 'ワイド 6-10 410円', '馬単 6-2 1,120円', '3連複 2-6-10 2,340円', '三連単 6-2-10 12,340円']);
  const r = O.parseResult([A]);
  console.log('結果A', JSON.stringify(r));
  check(JSON.stringify(r.p) === JSON.stringify([[6], [2], [10]]) && JSON.stringify(r.cancel) === JSON.stringify([11]) && !r.abandoned, '結果A：1〜3着の馬番（見出しの「馬番」の列）・除外の馬・競走中止は着に入れない');
  check(r.pay['単勝']['6'] === 240 && r.pay['複勝']['2'] === 180 && r.pay['複勝']['10'] === 310 && r.pay['枠複']['1-3'] === 1230 && r.pay['馬連']['2-6'] === 530 && r.pay['ワイド']['6-10'] === 410 && r.pay['馬単']['6-2'] === 1120 && r.pay['3連複']['2-6-10'] === 2340 && r.pay['3連単']['6-2-10'] === 12340,
    '結果A：払戻（枠連→枠複・三連単→3連単・「1,230円」）' + JSON.stringify(r.pay));
  // 「1着 6」の形・2着同着・見出しなし
  const B = L(['1着 6 ハナ', '2着 2 フタ', '2着 10 トオ（同着）', '4着 4 ヨン', '取消 11 ゴ']);
  const rb = O.parseResult([B]);
  check(JSON.stringify(rb.p) === JSON.stringify([[6], [2, 10], []]) && JSON.stringify(rb.cancel) === JSON.stringify([11]), '結果B：「1着 6」の形・2着同着・取消：' + JSON.stringify(rb.p));
  // 見出しなしの表「着 馬番 馬名」（枠なし）と「着 枠 馬番 馬名」
  const C = L(['1 6 ハナ 2.4', '2 2 フタ 4.1', '3 10 トオ 6.3']);
  const D = L(['1 3 6 ハナ', '2 1 2 フタ', '3 6 10 トオ']);
  check(JSON.stringify(O.parseResult([C]).p) === JSON.stringify([[6], [2], [10]]) && JSON.stringify(O.parseResult([D]).p) === JSON.stringify([[6], [2], [10]]), '結果C・D：見出しなし（着 馬番／着 枠 馬番）');
  // 中止・何も読めない
  check(O.parseResult([L(['第9競走 レース中止（馬場不良のため）'])]).abandoned === true && O.parseResult([L(['ようこそ', 'お知らせ'])]).got.length === 0, 'レース中止・表のない画面は何も入れない');
  // 2枚：着順の画像＋払戻の画像
  const r2 = O.parseResult([B, L(['払戻金', '単勝 6 240円', '馬単 6-2 1,120円'])]);
  check(JSON.stringify(r2.p) === JSON.stringify([[6], [2, 10], []]) && r2.pay['馬単']['6-2'] === 1120 && r2.got.includes('払戻（単勝・馬単）'), '2枚をまとめる（着順＋払戻）：' + r2.got.join('・'));
}
// 第4.116版：締切済みの印（closed）：画面に 発売が 終わった 言葉が あれば その言葉・締切の 前や 予定の 表示（「オッズは締切前のものです」「締切 18:05」「締切時刻」「締切まで」）は null
{
  const withLine = t => a.concat([{ text: t, x: 0.62, y: 0.955, w: 0.3, h: 0.03 }]);
  check(O.parse([a]).closed === null && O.parse([merged(a)]).closed === null, '締切済み：A（「オッズは締切前のものです」が ある ふつうの 画面）は null');
  const yes = { '締切済': '締切済', '締切済み': '締切済み', '発売締切': '発売締切', '投票締切済み': '締切済み', '締め切りました': '締め切りました', '発売は終了しました': '発売は終了', '発売終了': '発売終了', '確定オッズ': '確定オッズ', 'オッズ確定': 'オッズ確定', '最終オッズ': '最終オッズ', '結果確定': '結果確定', '締切': '締切', '締切り': '締切り' };
  for (const [t, w] of Object.entries(yes)) check(O.parse([withLine(t)]).closed === w, `締切済み：「${t}」→ ${JSON.stringify(O.parse([withLine(t)]).closed)}`);
  for (const t of ['締切 18:03', '発売締切 18:05', '発売締切時刻 18:05', '締切予定 18:05', '締切まで あと5分', '締切間近', '締切前', '締切り前', 'オッズ']) check(O.parse([withLine(t)]).closed === null, `締切済み：「${t}」は null（締切の 前・予定）`);
  const two = O.parse([a, withLine('締切済')]);
  check(two.closed === '締切済' && two.r === 9, '締切済み：2枚の うち 1枚に あれば その言葉');
}
// 第4.170版（まさちゃん 2026/11/14「名前は読み込んだ画像から割り出せる？」）：馬の 名前（names＝{ 馬番: 名前 }）。表の 行「[人気／着順] [枠] 馬番 馬名 …」から。
//   名前の 一覧は 持たない（画面の 字 だけ）・人の 名前（騎手）は 読まない（数字より あとは 見ない）・2頭 以上 読めた とき だけ
{
  const NM = { 1: 'サンライズゴールド', 2: 'テンゲルクイーン', 3: 'ナイトレイン', 4: 'ブルーハーバー', 5: 'コスモスカイ', 6: 'ミラクルアロー', 7: 'ハッピーデイズ', 8: 'シルバーウィンド', 9: 'ドリームキャッチャー', 10: 'ロイヤルステップ', 11: 'スターダストメモリー', 12: 'ラストサムライ' };
  const sameNM = nm => !!nm && Object.keys(NM).every(k => nm[k] === NM[k]);
  for (const [name, lines] of [['A 枠つき（セルごと）', a], ['A 枠つき（行ごと）', merged(a)], ['B 人気順・取消あり（セルごと）', b], ['B 人気順・取消あり（行ごと）', merged(b)]]) {
    const r = O.parse([lines]);
    check(sameNM(r.names) && Object.keys(r.names).length === (/^B/.test(name) ? 13 : 12), name + '：馬の 名前 12頭（馬番ごと）' + (/^B/.test(name) ? '＋取消の 馬' : '') + ' ' + JSON.stringify(r.names).slice(0, 60));
    checkHorses(r, name + '（名前を 読んでも）');
  }
  check(O.parse([c]).names === null && O.parse([d]).names === null && O.parse([merged(c)]).names === null, '3連単の 人気順の 画面には 名前なし（null）');
  const two = O.parse([c, a]);
  check(sameNM(two.names) && two.s1 && two.s1.combo === '6-2-10' && two.horses.length === 12, '2枚（3連単＋単勝）：名前は 単勝の 画面から・ほかの 読み取りは そのまま');
  const L = (ts, x0 = 0.05) => ts.map((t, i) => ({ text: t, x: x0, y: 0.05 + i * 0.035, w: 0.8, h: 0.025 }));
  const tab = ts => O.nameTable(O.rows(L(ts)));
  const J = o => JSON.stringify(o);
  // 結果の 画面
  const A = L(['レース結果 第9競走 はなまる特別', '着順 枠 馬番 馬名 性齢 斤量 騎手 タイム 人気', '1 3 6 ハナ 牡4 56.0 きしゅ 1:25.3 2', '2 1 2 フタ 牝3 54.0 きしゅ 1:25.5 1', '3 6 10 トオ 牡5 57.0 きしゅ 1:25.9 3',
    '4 2 4 ヨン 牡4 56.0 きしゅ 1:26.0 5', '5 11 ゴ 牡6 56.0 きしゅ 競走除外', '7 7 ナナ 牡3 55.0 きしゅ 競走中止', '払戻金', '単勝 6 240円 2人気', '複勝 6 120円', '枠連 1-3 1,230円', '馬連 2-6 530円', '馬単 6-2 1,120円', '3連複 2-6-10 2,340円', '三連単 6-2-10 12,340円']);
  const ra = O.parseResult([A]);
  check(J(ra.names) === J({ 2: 'フタ', 4: 'ヨン', 6: 'ハナ', 7: 'ナナ', 10: 'トオ' }) && J(ra.p) === J([[6], [2], [10]]) && !ra.got.some(g => /名/.test(g)), '結果A：着順の 表の 名前（馬番ごと）。払戻の 行・1字の 名前は 入れない・着順の 読み取りは そのまま ' + J(ra.names));
  const rb = O.parseResult([L(['1着 6 ハナ', '2着 2 フタ', '2着 10 トオ（同着）', '4着 4 ヨン', '取消 11 ゴ'])]);
  check(J(rb.names) === J({ 2: 'フタ', 4: 'ヨン', 6: 'ハナ', 10: 'トオ' }) && J(rb.p) === J([[6], [2, 10], []]), '結果B：「1着 6 名前」の 形・「（同着）」は 名前に 入れない ' + J(rb.names));
  const rn = O.parseResult([L(['出馬表', '1 サンライズゴールド', '2 テンゲルクイーン'])]);
  check(rn.got.length === 0 && J(rn.names) === J({ 1: 'サンライズゴールド', 2: 'テンゲルクイーン' }), '名前 だけ 読めた 画面は「読めた もの」には 数えない（got は 空の まま）');
  const r2 = O.parseResult([L(['1着 6 ハナ', '2着 2 フタ']), L(['1 3 6 ハナ', '2 1 2 フタ', '3 6 10 トオ', '4 2 4 ヨン'])]);
  check(J(r2.names) === J({ 2: 'フタ', 4: 'ヨン', 6: 'ハナ', 10: 'トオ' }), '結果 2枚：多く 読めた 画像を もとに 名前を まとめる');
  // 人の 名前は 読まない・印は とばす
  check(J(tab(['1 1 ◎ サンライズゴールド 牡4 56.0 山田太郎 12.4', '2 2 (地) テンゲルクイーン 牝3 54.0 キシュノナ 4.1', '3 3 ナイトレイン セン5 56.0 田中 31.5'])) === J({ 1: 'サンライズゴールド', 2: 'テンゲルクイーン', 3: 'ナイトレイン' }),
    '印（◎・(地)）は とばす・性齢と 斤量の あとの 騎手（漢字・カタカナ）は 読まない');
  check(J(tab(['1 1 牡4 56.0 キシュノナ 12.4', '2 2 セン5 54.0 ノリテ 4.1', '3 3 山田太郎 56.0 31.5', '4 4 ブルーハーバー 9.8', '5 5 コスモスカイ 18.2'])) === J({ 4: 'ブルーハーバー', 5: 'コスモスカイ' }),
    '名前が 読めて いない 行：騎手（キシュノナ・ノリテ・山田太郎）や「セン」を 名前に しない');
  check(J(tab(['1 1 サンライズゴールド キシュノナ 12.4', '2 2 テンゲルクイーン ノリテ 4.1'])) === J({ 1: 'サンライズゴールド', 2: 'テンゲルクイーン' }), '名前の すぐ あとに カタカナの 騎手が 続いても、はじめの 1つ だけ');
  check(J(tab(['大井 9 R ナイター', '10月14日(水) 12頭', '9 R ナイター', '1 サンライズゴールド 12.4', '2 テンゲルクイーン 4.1'])) === J({ 1: 'サンライズゴールド', 2: 'テンゲルクイーン' }), '見出し・日付の 行（「9 R ナイター」「10月14日」）から 名前を 作らない');
  check(tab(['1 サンライズゴールド 12.4']) === null && tab(['ようこそ', 'お知らせ']) === null, '1頭 だけ・表の ない 画面は null');
  check(J(tab(['1 サンライズゴールド 12.4', '2 テンゲルクイーン 4.1', '2 ナイトレイン 4.1', '3 コスモスカイ 3.3'])) === J({ 1: 'サンライズゴールド', 3: 'コスモスカイ' }), '同じ 馬番に ちがう 名前が 読めたら その 馬番は 返さない');
  // 名前の 形：カタカナ 2〜18字・カタカナに 見える 漢字・ひらがな・横線は 直す（ほかが カタカナの とき だけ）
  const K = { 'ブルーハーバー': 'ブルーハーバー', 'サンライズゴールド牡': 'サンライズゴールド', '(地)テンゲルスター': 'テンゲルスター', '[外]ヒメノユメ': 'ヒメノユメ', 'テンゲルスター（同着）': 'テンゲルスター', 'ﾃﾝｹﾞﾙｽﾀｰ': 'テンゲルスター',
    'ミラクルア口ー': 'ミラクルアロー', 'カ力オ': 'カカオ', 'スーパ-スター': 'スーパースター', 'ハナ': 'ハナ', 'ゴ': null, 'セン': null, '山田太郎': null, 'ABC': null, '◎': null, '(地)': null, 'テン ゲル': null, 'へべぺり': null, 'アイウエオカキクケコサシスセソタチツテ': null };
  const bad = Object.keys(K).filter(t => O.kataName(t) !== K[t]);
  check(!bad.length, '名前の 形（カタカナ 2〜18字・似た 字を 直す・1字／セン／漢字の 名前／英字は 名前に しない）' + J(bad.map(t => [t, O.kataName(t)])));
}
console.log('FAILS', fails.length, fails);
process.exit(fails.length ? 1 : 0);
