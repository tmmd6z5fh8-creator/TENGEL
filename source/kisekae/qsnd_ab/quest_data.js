// cb/cb_app.js から 決戦調査の エリアの 名前・セリフ・フィールドの 音の 鳴らし方（QSND）を 取り出して JSON に（聞きくらべの ページ用）
//   node kisekae/qsnd_ab/quest_data.js > <作業フォルダ>/quest_data.json
const fs = require('fs');
const src = fs.readFileSync(require('path').join(__dirname, '..', '..', 'cb', 'cb_app.js'), 'utf8');
const cut = (a, b) => { const i = src.indexOf(a); if (i < 0) throw new Error('ない：' + a); const j = src.indexOf(b, i); if (j < 0) throw new Error('ない：' + b); return src.slice(i + a.length, j); };
const QUEST = eval('[' + cut('const QUEST = [', '].map(([a, n, s, w, c, rig, say, en], i)') + '\n]');
const QSND = eval('[' + cut('const QSND = [', '\n  ];') + '\n]');
if (QUEST.length !== 12 || QSND.length !== 12) throw new Error('12 で ない');
const out = QUEST.map((q, i) => ({ lv: i + 1, area: q[0], say: q[6], b: Object.assign({}, QSND[i].b, QSND[i].b.le === Infinity ? { le: null } : {}), s: QSND[i].s, t: QSND[i].t }));
process.stdout.write(JSON.stringify(out, null, 1));
