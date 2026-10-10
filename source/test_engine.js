const T = require('./engine.js');
const fs = require('fs');
const lines = fs.readFileSync('hist.csv','utf8').trim().split('\n').slice(1);
const serialToDate = s => { const d = new Date(Date.UTC(1899,11,30) + s*86400000); return d.toISOString().slice(0,10); };
const recs = lines.map(l => {
  const f = l.split(',');
  const [serial,r,baba,dist,n,tan1,s1,p1,p2,p3,cnt,hi,L,B,H] = f;
  const note = f.slice(15).join(',');
  return { id: serialToDate(+serial).replace(/-/g,'')+'-oi-'+String(r).padStart(2,'0'), date: serialToDate(+serial), venue:'大井', r:+r, baba, dist:+dist, surface:'ダ', n:+n, tan1:+tan1, s1:+s1, p1:+p1||null, p2:+p2||null, p3:p3===''?null:+p3, cnt:+cnt, note, _hi:+hi, _L:L, _B:B, _H:+H };
});
console.log('rows', recs.length, recs[0].date, recs[recs.length-1].date);
const D = recs.map(T.derive);
const bmap = {N:'非該当','1':'第1段階','2':'第2段階'};
let bad=0;
for (const d of D) {
  const errs=[];
  if (d.hi !== d._hi) errs.push(`hi ${d.hi}≠${d._hi}`);
  if (d.L !== d._L) errs.push(`L ${d.L}≠${d._L}`);
  if (d.band12 !== bmap[d._B]) errs.push(`band ${d.band12}≠${bmap[d._B]}`);
  if (d.hit12 !== d._H) errs.push(`hit12 ${d.hit12}≠${d._H}`);
  if (errs.length){bad++; console.log(d.date,d.r,errs.join(' '));}
}
console.log('row mismatches:', bad);
const S = D.filter(d=>d.inStats);
console.log('inStats', S.length);
const cnt=(arr,f)=>arr.filter(f).length;
for (const L of ['A','B','C']) console.log(L, cnt(S,d=>d.L===L), 'ana', cnt(S,d=>d.L===L&&d.ana), 'nn', cnt(S,d=>d.L===L&&d.nn));
for (const b of ['非該当','第1段階','第2段階']) console.log('band12',b,cnt(S,d=>d.band12===b));
console.log('hit12 total', cnt(S,d=>d.hit12), 'A',cnt(S,d=>d.L==='A'&&d.hit12),'B',cnt(S,d=>d.L==='B'&&d.hit12),'C',cnt(S,d=>d.L==='C'&&d.hit12));
console.log('hit13 total', cnt(S,d=>d.hit), 'A',cnt(S,d=>d.L==='A'&&d.hit),'B',cnt(S,d=>d.L==='B'&&d.hit),'C',cnt(S,d=>d.L==='C'&&d.hit));
console.log('A zones', cnt(S,d=>d.kubun==='A'&&d.hit===1), cnt(S,d=>d.kubun==='A'&&d.hit===2));
console.log('B zones', cnt(S,d=>d.kubun==='B'&&d.hit===1), cnt(S,d=>d.kubun==='B'&&d.hit===2));
console.log('tri13', cnt(S,d=>d.tri), 'A',cnt(S,d=>d.kubun==='A'&&d.tri),'B',cnt(S,d=>d.kubun==='B'&&d.tri),'C1',cnt(S,d=>d.kubun==='C1'&&d.tri),'C2',cnt(S,d=>d.kubun==='C2'&&d.tri));
console.log('kubun', ['A','B','C0','C1','C2'].map(k=>k+':'+cnt(S,d=>d.kubun===k)).join(' '));
console.log('anaHit12', cnt(S,d=>d.anaHit12), 'anaHit13', cnt(S,d=>d.anaHit13));
const St = T.stats(D);
console.log(JSON.stringify(St.k.A.t), St.k.A.n3, JSON.stringify(St.k.B.t), St.k.B.n3);
console.log('C1', JSON.stringify(St.k.C1), '\nC2', JSON.stringify(St.k.C2));
console.log('ninki', JSON.stringify(St.ninki));
console.log('early', JSON.stringify(St.early), 'c20', JSON.stringify(St.c20));
console.log('band12', JSON.stringify(St.band12));
// pair distribution
const pairs={}; for(const d of S){pairs[d.pair]=(pairs[d.pair]||0)+1;} console.log(JSON.stringify(pairs));
// B hits by period
for (const z of [1,2]) console.log('B zone',z, ['前半','後半','新規'].map(p=>cnt(S,d=>d.kubun==='B'&&d.hit===z&&d.per===p)).join('/'));
console.log('B hits', S.filter(d=>d.kubun==='B'&&d.hit).map(d=>d.date.slice(5)+' '+d.r+'R z'+d.hit+' 3rd:'+d.z3+(d.tri?'✓':'✗')).join(' | '));
