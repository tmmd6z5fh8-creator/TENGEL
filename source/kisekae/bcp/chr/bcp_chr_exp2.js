// 結果ボードカスタム：キャラだけ 動かす（実験 v2・2026/11/05）
//   window.__BCPCHR = { <デザイン>: { bgx（キャラなしの 背景）, fgx（前の 絵から キャラを のぞいた もの・ない ときは null）,
//     layers: [{ src, box: [x, y, w, h]（舞台の pt）, o: [x, y]（動きの まん中）, amp（ぷるんの 強さ 0〜1）, deg（向きの 度）, dp, dt（遅れ 秒） }] } }
//   動きの きまり（まさちゃん 2026/11/04）：キャラ だけ・腕と 持ち物も いっしょ・ぷるん 3.2秒に 1回（つぶれ 3.8%）・3Dで 左右 4度 7秒・止まると 元の 絵と 同じ
//   「的中エフェクト」が 控えめ／オフ（.bcst）・視差効果を減らす では 動かさない
//   重ね方（11/05）：キャラは アプリの ボード（.rb）の 下（元の 絵と 同じ）。ボードの 前に 出る 所（f：前の 絵の マスク×キャラ）だけ
//     ボードの 上に 同じ 動きで もう1まい 重ねる → 板に かかる キャラも まるごと 動く（板の ところで 切れない）・止まって いる ときは 元と 同じ
(() => {
  const CH = window.__BCPCHR || {};
  const PON = [[0, 0, 0], [8, -0.010, 0.016], [14, 0.024, -0.038], [22, -0.006, 0.012], [30, 0.007, -0.007], [38, -0.002, 0.003], [46, 0, 0], [100, 0, 0]];
  const PER = 600, TP = 3.2, TT = 7.0;
  const base = document.createElement('style');
  base.textContent = [
    '#fxOv .hb.bcpic .bcpw .chrw{position:absolute;pointer-events:none}',
    '#fxOv .hb.bcpic .bcpw .chrw > .chri{position:absolute;left:0;top:0;width:100%;height:100%}',
    '#fxOv .hb.bcpic .bcpw .chrw img{position:absolute;left:0;top:0;width:100%;height:100%;-webkit-user-drag:none;user-select:none}'
  ].join('\n');
  const add = el => { if (!el.isConnected && (document.head || document.documentElement)) (document.head || document.documentElement).appendChild(el); };
  add(base);
  const f = v => (+v).toFixed(4);
  const made = {};
  function rules(name, c) {
    if (made[name]) return; made[name] = 1;
    const nm = 'chr_' + name.replace(/[^a-z0-9_]/gi, '');
    let k = '', r = '';
    c.layers.forEach((l, i) => {
      const a = l.amp == null ? 1 : l.amp, d = l.deg == null ? 4 : l.deg, ax = l.ax == null ? a : l.ax;   // ax：よこの ふくらみ（ボードを 持つ キャラは 小さく＝手が ボードから ずれない）
      k += `@keyframes ${nm}_${i}p{` + PON.map(([t, x, y]) => `${t}%{transform:scale(${f(1 + x * ax)},${f(1 + y * a)})}`).join('') + '}';
      k += `@keyframes ${nm}_${i}t{0%,100%{transform:perspective(${PER}px) rotateY(0deg)}25%{transform:perspective(${PER}px) rotateY(${d.toFixed(2)}deg)}75%{transform:perspective(${PER}px) rotateY(${(-d).toFixed(2)}deg)}}`;
      const sel = `#fxOv .hb.bcpic.bcpon:not(.bcst)[data-bcp="${name}"] .chrw.L${i}`;
      r += `${sel}{animation:${nm}_${i}t ${TT}s ease-in-out ${(l.dt == null ? 0.9 : l.dt).toFixed(2)}s infinite}`;
      r += `${sel} > .chri{animation:${nm}_${i}p ${TP}s ease-in-out ${(l.dp == null ? 0.8 : l.dp).toFixed(2)}s infinite}`;
    });
    const st = document.createElement('style');
    st.textContent = k + '\n@media (prefers-reduced-motion:no-preference){' + r + '}';
    add(st);
  }
  Object.keys(CH).forEach(n => { const c = CH[n]; [c.bgx, c.fgx, c.oc && c.oc.src, c.ot && c.ot.src].concat(c.layers.map(l => l.src), c.layers.map(l => l.f)).forEach(s => { if (s) { const im = new Image(); im.src = s; } }); });
  const done = new WeakSet();
  function setup(hb) {
    const name = hb.dataset.bcp, c = CH[name]; if (!c) return;
    const wrap = hb.querySelector(':scope > .bcpw'); if (!wrap || done.has(wrap)) return;
    const bg = wrap.querySelector(':scope > img.bcpbg'); if (!bg) return;
    done.add(wrap); rules(name, c);
    bg.src = c.bgx;
    const fg = wrap.querySelector(':scope > img.bcpfg');
    if (fg && c.fgx) fg.src = c.fgx;
    const rb = wrap.querySelector(':scope > .rb');
    const mk = (l, i, src) => {
      const w = document.createElement('div'); w.className = 'chrw L' + i;
      const ii = document.createElement('div'); ii.className = 'chri';
      // 入れものは 絵の 大きさ だけ（重ねる 層が 小さい＝iPhone でも 軽い）。動きの まん中は 入れものの 中の 位置に
      const b = l.box || [0, 0, 390, 844];
      w.style.left = b[0] + 'px'; w.style.top = b[1] + 'px'; w.style.width = b[2] + 'px'; w.style.height = b[3] + 'px';
      const o = `${(l.o[0] - b[0]).toFixed(2)}px ${(l.o[1] - b[1]).toFixed(2)}px`; w.style.transformOrigin = o; ii.style.transformOrigin = o;
      const im = document.createElement('img'); im.alt = ''; im.setAttribute('aria-hidden', 'true'); im.draggable = false; im.src = src;
      ii.appendChild(im); w.appendChild(ii); return w;
    };
    c.layers.forEach((l, i) => { const w = mk(l, i, l.src); if (rb) wrap.insertBefore(w, rb); else wrap.appendChild(w); });   // キャラ：ボードの 下
    if (c.oc) {   // キャラの 前に ある 動かない 物（ボードの ふち など）：キャラの 上・アプリの ボードの 下（動かない）
      const b = c.oc.box, im = document.createElement('img'); im.className = 'chroc'; im.alt = ''; im.setAttribute('aria-hidden', 'true'); im.draggable = false; im.src = c.oc.src;
      im.style.cssText = `position:absolute;left:${b[0]}px;top:${b[1]}px;width:${b[2]}px;height:${b[3]}px;pointer-events:none`;
      if (rb) wrap.insertBefore(im, rb); else wrap.appendChild(im);
    }
    c.layers.forEach((l, i) => { if (l.f) wrap.appendChild(mk(l, i, l.f)); });                                                // ボードの 前に 出る 所：いちばん 上
    if (c.ot) {   // 動かない 前の 絵の ボードの 前の 所（二人でしょんぼりの 残念の 青い 線）：キャラの 前の 絵（f）より 上（動かない）
      const b = c.ot.box, im = document.createElement('img'); im.className = 'chrot'; im.alt = ''; im.setAttribute('aria-hidden', 'true'); im.draggable = false; im.src = c.ot.src;
      im.style.cssText = `position:absolute;left:${b[0]}px;top:${b[1]}px;width:${b[2]}px;height:${b[3]}px;pointer-events:none`;
      wrap.appendChild(im);
    }
  }
  const scan = () => { add(base); document.querySelectorAll('#fxOv .hb.bcpic').forEach(setup); };
  new MutationObserver(scan).observe(document, { childList: true, subtree: true, attributes: true, attributeFilter: ['class', 'data-bcp'] });
})();
