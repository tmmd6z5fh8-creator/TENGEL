const fs=require('fs');
const eng=fs.readFileSync('engine.js','utf8');
let src=fs.readFileSync('src.html','utf8');
src=src.replace('/*ENGINE*/', ()=>eng);
fs.writeFileSync('tengel3.html', src);
// syntax check each inline script
const scripts=[...src.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
scripts.forEach((s,i)=>fs.writeFileSync(`chk${i}.js`, s));
console.log('size', src.length, 'scripts', scripts.length);
