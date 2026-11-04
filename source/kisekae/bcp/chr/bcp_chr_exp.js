// 結果ボードカスタム：キャラだけ 動かす（実験・2026/11/04 まさちゃん「やるならキャラクターだけ！」）
//   絵を「キャラなしの 背景」と「キャラごとの すき通しの 絵」に 分けて（kisekae/bcp/chr）、キャラの 絵だけ 動かす。ボード・光・紙ふぶきは 動かない
//   止まって いる ときは 元の 絵と 同じ（キャラの まわりの 光の ふちも キャラと いっしょ）
//   window.__BCPCHR = { <デザイン>: { bgx: 背景, layers: [{ src, kind, o: [x, y]（動きの まん中・舞台の pt） }] } }
//   kind：horse（ぷるん と 息を する・ゆっくり 3Dで 首を ふる）・stamp（ときどき「ポン」と おす・ぷるん と もどる）
//   22:53 まさちゃん「もう少し動き弱くしてみて！」→ 大きさを 半分くらいに（息 1.2%・首ふり 4度・ポン 6%・かたむき 3.5度）
(() => {
  const CH = window.__BCPCHR || {};
  const css = document.createElement('style');
  css.textContent = [
    '#fxOv .hb.bcpic .bcpw .chrw{position:absolute;left:0;top:0;width:390px;height:844px;pointer-events:none}',
    '#fxOv .hb.bcpic .bcpw .chrw > .chri{position:absolute;left:0;top:0;width:390px;height:844px}',
    '#fxOv .hb.bcpic .bcpw .chrw img{position:absolute;left:0;top:0;width:390px;height:844px;-webkit-user-drag:none;user-select:none}',
    // 馬：息（ぷるん）2.6秒・首ふり（3D）7秒
    '@keyframes chrBreath{0%{transform:scale(1,1)}9%{transform:scale(1.012,.985)}20%{transform:scale(.993,1.018)}32%{transform:scale(1.006,.994)}44%{transform:scale(.998,1.004)}56%,100%{transform:scale(1,1)}}',
    '@keyframes chrTurn{0%,100%{transform:perspective(600px) rotateY(0deg)}25%{transform:perspective(600px) rotateY(4deg)}75%{transform:perspective(600px) rotateY(-4deg)}}',
    // ハンコ：ためて（のびる）→「ポン」（つぶれる）→ ぷるん と もどる（3.2秒に 1回）・ゆっくり 3Dで かたむく
    '@keyframes chrPon{0%{transform:scale(1,1)}8%{transform:scale(.985,1.025)}14%{transform:scale(1.035,.94)}22%{transform:scale(.991,1.02)}30%{transform:scale(1.011,.989)}38%{transform:scale(.997,1.005)}46%,100%{transform:scale(1,1)}}',
    '@keyframes chrTilt{0%,100%{transform:perspective(600px) rotateY(0deg)}25%{transform:perspective(600px) rotateY(-3.5deg)}75%{transform:perspective(600px) rotateY(3.5deg)}}',
    '@media (prefers-reduced-motion:no-preference){',
    '#fxOv .hb.bcpic.bcpon:not(.bcst) .chrw.horse{animation:chrTurn 7s ease-in-out .9s infinite}',
    '#fxOv .hb.bcpic.bcpon:not(.bcst) .chrw.horse > .chri{animation:chrBreath 2.6s ease-in-out .6s infinite}',
    '#fxOv .hb.bcpic.bcpon:not(.bcst) .chrw.stamp{animation:chrTilt 8s ease-in-out 1.4s infinite}',
    '#fxOv .hb.bcpic.bcpon:not(.bcst) .chrw.stamp > .chri{animation:chrPon 3.2s ease-in-out 1.0s infinite}',
    '}'
  ].join('\n');
  const addCss = () => { if (!css.isConnected && (document.head || document.documentElement)) (document.head || document.documentElement).appendChild(css); };
  addCss();
  Object.keys(CH).forEach(n => { const c = CH[n]; [c.bgx].concat(c.layers.map(l => l.src)).forEach(s => { const im = new Image(); im.src = s; }); });
  const done = new WeakSet();
  function setup(hb) {
    const name = hb.dataset.bcp, c = CH[name]; if (!c) return;
    const wrap = hb.querySelector(':scope > .bcpw'); if (!wrap || done.has(wrap)) return;
    const bg = wrap.querySelector('img.bcpbg'); if (!bg) return;
    done.add(wrap);
    bg.src = c.bgx;
    c.layers.forEach(l => {
      const w = document.createElement('div'); w.className = 'chrw ' + l.kind;
      const i = document.createElement('div'); i.className = 'chri';
      const o = `${l.o[0].toFixed(2)}px ${l.o[1].toFixed(2)}px`; w.style.transformOrigin = o; i.style.transformOrigin = o;
      const im = document.createElement('img'); im.alt = ''; im.setAttribute('aria-hidden', 'true'); im.draggable = false; im.src = l.src;
      i.appendChild(im); w.appendChild(i); wrap.appendChild(w);
    });
  }
  const scan = () => { addCss(); document.querySelectorAll('#fxOv .hb.bcpic').forEach(setup); };
  new MutationObserver(scan).observe(document, { childList: true, subtree: true, attributes: true, attributeFilter: ['class', 'data-bcp'] });
})();
