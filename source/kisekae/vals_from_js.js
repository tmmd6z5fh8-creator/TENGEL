// Main.dc.html の renderVals を実際に動かして、プレビュー用の値を作る（関数は落とす）
const fs = require('fs');
const [,, file, theme, out] = process.argv;
const src = fs.readFileSync(file, 'utf8');
const js = src.match(/<script type="text\/x-dc"[^>]*>([\s\S]*?)<\/script>/)[1];
class DCLogic { constructor() { this.props = { startTheme: theme }; this.state = {}; } setState(s) { Object.assign(this.state, s); } }
const Component = new Function('DCLogic', js + '\nreturn Component;')(DCLogic);
const c = new Component();
const v = c.renderVals();
fs.writeFileSync(out, JSON.stringify(v));
console.log(out, Object.keys(v).join(','), v.rootCls, v.curName, ['g1','g2','g3','g4','g5'].map(k => v[k].length).join('/'));
