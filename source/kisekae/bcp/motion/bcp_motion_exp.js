// 結果ボードカスタム（まさちゃんの 絵の ボード）の 動き：実験（2026/11/04 まさちゃん「少し動きのエフェクトをつけることは可能？ プルンと動きとか、立体感を出して少し動かすか！ まだこれは、実験ね！」）
//   絵ごと（うしろの 絵・アプリの ボード・前の 絵 を いっしょに）動かす ので、絵が ずれたり 二重に なったり しない
//   ぷるん：ボードが 出る とき（と さわった とき）に ぷるんと はずむ（大きさは 1 より 小さく しない＝画面の はしが 見えない）
//   立体：ゆっくり かたむく（3D）＋ボードの ガラスに 光が すべる（かたむきに 合わせて）＋アプリの 字が 少し 浮く
//   window.__bcpMotion = 'purun' | 'tilt' | 'both'（はじめは both）
(() => {
  const P = 1000, A = 1.1, B = 2.2, TD = 7.0;          // 立体：遠近（px）・たての かたむき・よこの かたむき（度）・1回り（秒）
  const JD = 0.30, JL = 0.9;                            // ぷるん：はじまり（ボードが 出はじめて から 秒）・長さ（秒）
  const mode = () => window.__bcpMotion || 'both';
  const css = document.createElement('style');
  css.textContent = [
    '#fxOv .hb.bcpic .bcpw{overflow:hidden}',
    '#fxOv .hb.bcpic .bcpw .bcpm,#fxOv .hb.bcpic .bcpw .bcpt{position:absolute;left:0;top:0;width:390px;height:844px}',
    '#fxOv .hb.bcpic .bcpt > img{position:absolute;left:0;top:0;width:390px;height:844px;-webkit-user-drag:none;user-select:none}',
    '#fxOv .rb.bcp .bcpgl{position:absolute;left:0;top:0;width:350px;overflow:hidden;border-radius:16px;pointer-events:none;z-index:6}',
    '#fxOv .rb.bcp .bcpgl::before{content:"";position:absolute;top:-25%;bottom:-25%;left:0;width:36%;opacity:0;'
      + 'background:linear-gradient(90deg,rgba(255,255,255,0) 0%,rgba(255,255,255,.20) 46%,rgba(255,255,255,.26) 50%,rgba(255,255,255,.20) 54%,rgba(255,255,255,0) 100%);transform:translateX(-140px) skewX(-18deg)}',
    // ぷるん（大きさは 1 より 小さく しない）
    '@keyframes bcpPurun{0%{transform:scale(1,1)}11%{transform:scale(1.045,1)}23%{transform:scale(1,1.04)}35%{transform:scale(1.026,1)}47%{transform:scale(1,1.016)}60%{transform:scale(1.008,1)}74%{transform:scale(1,1.004)}100%{transform:scale(1,1)}}',
    '@keyframes bcpPoke{0%{transform:scale(1,1)}12%{transform:scale(1.035,1)}25%{transform:scale(1,1.03)}38%{transform:scale(1.018,1)}52%{transform:scale(1,1.01)}68%{transform:scale(1.004,1)}100%{transform:scale(1,1)}}',
    '@keyframes bcpPoke2{0%{transform:scale(1,1)}12%{transform:scale(1.035,1)}25%{transform:scale(1,1.03)}38%{transform:scale(1.018,1)}52%{transform:scale(1,1.01)}68%{transform:scale(1.004,1)}100%{transform:scale(1,1)}}',
    '@media (prefers-reduced-motion:no-preference){',
    `#fxOv .hb.bcpic.bcpon:not(.bcst) .bcpm.mj{animation:bcpPurun ${JL}s ease-in-out ${JD}s both}`,
    `#fxOv .hb.bcpic:not(.bcst) .bcpm.pk1{animation:bcpPoke .8s ease-in-out both}#fxOv .hb.bcpic:not(.bcst) .bcpm.pk2{animation:bcpPoke2 .8s ease-in-out both}`,
    '}'
  ].join('\n');
  const addCss = () => { if (!css.isConnected) (document.head || document.documentElement).appendChild(css); };
  if (document.head || document.documentElement) addCss(); else document.addEventListener('DOMContentLoaded', addCss);
  // 4点 → 4点 の 射影（bcx.js と 同じ）
  function homog(src, dst) {
    const M = [], R = [];
    for (let i = 0; i < 4; i++) { const x = src[i][0], y = src[i][1], u = dst[i][0], v = dst[i][1]; M.push([x, y, 1, 0, 0, 0, -u * x, -u * y]); R.push(u); M.push([0, 0, 0, x, y, 1, -v * x, -v * y]); R.push(v); }
    for (let c = 0; c < 8; c++) {
      let p = c; for (let r = c + 1; r < 8; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r;
      if (p !== c) { const t = M[c]; M[c] = M[p]; M[p] = t; const u = R[c]; R[c] = R[p]; R[p] = u; }
      for (let r = 0; r < 8; r++) { if (r === c) continue; const k = M[r][c] / M[c][c]; if (!k) continue; for (let j = c; j < 8; j++) M[r][j] -= k * M[c][j]; R[r] -= k * R[c]; }
    }
    return R.map((v, i) => v / M[i][i]);
  }
  // かたむけた 絵が 舞台（390×844）を ぜんぶ おおう いちばん 小さい 大きさ（はしの 黒い すき間を 出さない）
  function cover(rx, ry, ox, oy) {
    const ax = rx * Math.PI / 180, ay = ry * Math.PI / 180;
    const proj = (x, y, s) => {
      let X = (x - ox) * s, Y = (y - oy) * s, Z = 0;
      const X1 = X * Math.cos(ay) + Z * Math.sin(ay), Z1 = -X * Math.sin(ay) + Z * Math.cos(ay); X = X1; Z = Z1;   // rotateY
      const Y2 = Y * Math.cos(ax) - Z * Math.sin(ax), Z2 = Y * Math.sin(ax) + Z * Math.cos(ax); Y = Y2; Z = Z2;   // rotateX
      const k = P / (P - Z); return [ox + X * k, oy + Y * k];
    };
    const inside = (pts, x, y) => { let sg = 0; for (let i = 0; i < 4; i++) { const a = pts[i], b = pts[(i + 1) % 4], c = (b[0] - a[0]) * (y - a[1]) - (b[1] - a[1]) * (x - a[0]); if (c !== 0) { if (sg && Math.sign(c) !== sg) return false; sg = Math.sign(c); } } return true; };
    const ok = s => { const q = [proj(0, 0, s), proj(390, 0, s), proj(390, 844, s), proj(0, 844, s)]; return [[0, 0], [390, 0], [390, 844], [0, 844]].every(([x, y]) => inside(q, x, y)); };
    let lo = 1, hi = 1.08; if (ok(1)) return 1;
    for (let i = 0; i < 24; i++) { const m = (lo + hi) / 2; if (ok(m)) hi = m; else lo = m; }
    return hi + 0.0015;
  }
  const done = new WeakSet();
  function setup(hb) {
    const wrap = hb.querySelector(':scope > .bcpw'); if (!wrap || done.has(wrap)) return;
    const name = hb.dataset.bcp, D = window.__BCP && window.__BCP.d[name]; if (!D) return;
    const bg = wrap.querySelector(':scope > img.bcpbg'), rb = wrap.querySelector(':scope > .rb'), fg = wrap.querySelector(':scope > img.bcpfg');
    if (!bg || !rb) return;
    done.add(wrap);
    const q = D.q, ox = (q[0][0] + q[1][0] + q[2][0] + q[3][0]) / 4, oy = (q[0][1] + q[1][1] + q[2][1] + q[3][1]) / 4;
    const m = document.createElement('div'); m.className = 'bcpm'; const t = document.createElement('div'); t.className = 'bcpt';
    m.style.transformOrigin = t.style.transformOrigin = `${ox.toFixed(2)}px ${oy.toFixed(2)}px`;
    wrap.insertBefore(m, bg); m.appendChild(t); t.appendChild(bg); t.appendChild(rb); if (fg) t.appendChild(fg);
    const md = mode();
    if (md === 'purun' || md === 'both') m.classList.add('mj');
    if (md === 'tilt' || md === 'both') {
      const gl = document.createElement('div'); gl.className = 'bcpgl'; gl.style.height = D.hp + 'px'; rb.appendChild(gl);
      t.classList.add('mt');
      const N = 64; let k1 = '', k2 = '', k3 = '';
      for (let i = 0; i <= N; i++) {
        const u = i / N, rx = A * Math.sin(4 * Math.PI * u), ry = B * Math.sin(2 * Math.PI * u), s = cover(rx, ry, ox, oy), pc = (u * 100).toFixed(3) + '%';
        k1 += `${pc}{transform:perspective(${P}px) rotateX(${rx.toFixed(3)}deg) rotateY(${ry.toFixed(3)}deg) scale(${s.toFixed(4)})}`;
        k2 += `${pc}{transform:translate(${(-0.75 * ry).toFixed(3)}px,${(0.75 * rx).toFixed(3)}px)}`;
        const gx = 175 - 63 + (ry / B) * 240, go = Math.min(1, Math.abs(ry) / B * 1.15);
        k3 += `${pc}{transform:translateX(${gx.toFixed(1)}px) skewX(-18deg);opacity:${go.toFixed(3)}}`;
      }
      const dl = md === 'both' ? JD + JL : 0.55, nm = name.replace(/[^a-z0-9_]/gi, '');
      const st = document.createElement('style');
      st.textContent = `@keyframes bcpTilt_${nm}{${k1}}@keyframes bcpTx_${nm}{${k2}}@keyframes bcpGl_${nm}{${k3}}\n@media (prefers-reduced-motion:no-preference){`
        + `#fxOv .hb.bcpic.bcpon:not(.bcst)[data-bcp="${name}"] .bcpt.mt{animation:bcpTilt_${nm} ${TD}s linear ${dl}s infinite}`
        + `#fxOv .hb.bcpic.bcpon:not(.bcst)[data-bcp="${name}"] .bcpt.mt .rb.bcp .card,#fxOv .hb.bcpic.bcpon:not(.bcst)[data-bcp="${name}"] .bcpt.mt .rb.bcp .bh,#fxOv .hb.bcpic.bcpon:not(.bcst)[data-bcp="${name}"] .bcpt.mt .rb.bcp .bsub{animation:bcpTx_${nm} ${TD}s linear ${dl}s infinite}`
        + `#fxOv .hb.bcpic.bcpon:not(.bcst)[data-bcp="${name}"] .bcpt.mt .bcpgl::before{animation:bcpGl_${nm} ${TD}s linear ${dl}s infinite}}`;
      (document.head || document.documentElement).appendChild(st);
    }
    // さわると ぷるん（実験：ボードの 上を さわった とき）
    hb.__poke = () => { const a = m.classList.contains('pk1'); m.classList.remove('mj', 'pk1', 'pk2'); void m.offsetWidth; m.classList.add(a ? 'pk2' : 'pk1'); };
  }
  const scan = () => { addCss(); document.querySelectorAll('#fxOv .hb.bcpic').forEach(setup); };
  new MutationObserver(scan).observe(document, { childList: true, subtree: true, attributes: true, attributeFilter: ['class', 'data-bcp'] });
  window.__bcpPoke = () => { const hb = document.querySelector('#fxOv .hb.bcpic'); if (hb && hb.__poke) hb.__poke(); };
})();
