// 結果ボードカスタム：キャラだけ 動かす（実験 v2・2026/11/05）
//   window.__BCPCHR = { <デザイン>: { bgx（キャラなしの 背景）, fgx（前の 絵から キャラを のぞいた もの・ない ときは null）,
//     layers: [{ src, box: [x, y, w, h]（舞台の pt）, o: [x, y]（動きの まん中）, amp（ぷるんの 強さ 0〜1）, deg（向きの 度）, dp, dt（遅れ 秒） }] } }
//   動きの きまり（まさちゃん 2026/11/04）：キャラ だけ・腕と 持ち物も いっしょ・ぷるん 3.2秒に 1回（つぶれ 3.8%）・3Dで 左右 4度 7秒・止まると 元の 絵と 同じ
//   「的中エフェクト」が 控えめ／オフ（.bcst）・視差効果を減らす では 動かさない
//   重ね方（11/05）：キャラは アプリの ボード（.rb）の 下（元の 絵と 同じ）。ボードの 前に 出る 所（f：前の 絵の マスク×キャラ）だけ
//     ボードの 上に 同じ 動きで もう1まい 重ねる → 板に かかる キャラも まるごと 動く（板の ところで 切れない）・止まって いる ときは 元と 同じ
//   まわりの 光と 雲（amb：まさちゃん 11/05 21:46「周り光や雲が動くようにして！」・amb_stage.py）：舞台の 絵の 上（アプリの ボードの 下）に WebGL の 絵を かさねる。
//     光の すじは もとの まわりで ゆっくり ゆれて 明るさが 角度で 流れる・雲は ゆっくり うねる（トロフィー・ボード・紙ふぶきは 動かない）。
//     時刻は 見えない 時計の CSS アニメーション（.chrclk）の currentTime（動きを 止める 設定では 時計が 動かない＝かさねない＝元の 絵）
(() => {
  const CH = window.__BCPCHR || {};
  const PON = [[0, 0, 0], [8, -0.010, 0.016], [14, 0.024, -0.038], [22, -0.006, 0.012], [30, 0.007, -0.007], [38, -0.002, 0.003], [46, 0, 0], [100, 0, 0]];
  const PER = 600, TP = 3.2, TT = 7.0;
  const base = document.createElement('style');
  base.textContent = [
    '#fxOv .hb.bcpic .bcpw .chrw{position:absolute;pointer-events:none}',
    '#fxOv .hb.bcpic .bcpw .chrw > .chri{position:absolute;left:0;top:0;width:100%;height:100%}',
    '#fxOv .hb.bcpic .bcpw .chrw img{position:absolute;left:0;top:0;width:100%;height:100%;-webkit-user-drag:none;user-select:none}',
    '#fxOv .hb.bcpic .bcpw .chramb{position:absolute;left:0;top:0;width:390px;height:844px;pointer-events:none}',
    '#fxOv .hb.bcpic .bcpw .chrclk{position:absolute;left:0;top:0;width:1px;height:1px;opacity:0;pointer-events:none}'
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
      if (l.sw != null) {
        // ヒラヒラ（花・リボン：まさちゃん 11/05 20:26「花がヒラヒラ動く演出できる？そんなに激しくなく！」）：
        //   まん中 o の まわりで ゆっくり 左右に 回る（sw 度・st 秒）＋ 少し 向きを かえる（たての じく fy 度・sf 秒）。0% は 元の 絵と 同じ
        const sw = +l.sw, fy = l.fy == null ? 0 : +l.fy, st = l.st == null ? 3.6 : +l.st, sf = l.sf == null ? 2.6 : +l.sf;
        k += `@keyframes ${nm}_${i}w{0%,100%{transform:rotate(0deg)}25%{transform:rotate(${sw.toFixed(2)}deg)}75%{transform:rotate(${(-sw).toFixed(2)}deg)}}`;
        k += `@keyframes ${nm}_${i}y{0%,100%{transform:perspective(${PER}px) rotateY(0deg)}25%{transform:perspective(${PER}px) rotateY(${fy.toFixed(2)}deg)}75%{transform:perspective(${PER}px) rotateY(${(-fy).toFixed(2)}deg)}}`;
        const sel = `#fxOv .hb.bcpic.bcpon:not(.bcst)[data-bcp="${name}"] .chrw.L${i}`;
        r += `${sel}{animation:${nm}_${i}w ${st.toFixed(2)}s ease-in-out ${(l.dt == null ? 0.9 : l.dt).toFixed(2)}s infinite}`;
        if (fy) r += `${sel} > .chri{animation:${nm}_${i}y ${sf.toFixed(2)}s ease-in-out ${(l.dp == null ? 0.8 : l.dp).toFixed(2)}s infinite}`;
        return;
      }
      const a = l.amp == null ? 1 : l.amp, d = l.deg == null ? 4 : l.deg, ax = l.ax == null ? a : l.ax;   // ax：よこの ふくらみ（ボードを 持つ キャラは 小さく＝手が ボードから ずれない）
      k += `@keyframes ${nm}_${i}p{` + PON.map(([t, x, y]) => `${t}%{transform:scale(${f(1 + x * ax)},${f(1 + y * a)})}`).join('') + '}';
      k += `@keyframes ${nm}_${i}t{0%,100%{transform:perspective(${PER}px) rotateY(0deg)}25%{transform:perspective(${PER}px) rotateY(${d.toFixed(2)}deg)}75%{transform:perspective(${PER}px) rotateY(${(-d).toFixed(2)}deg)}}`;
      const sel = `#fxOv .hb.bcpic.bcpon:not(.bcst)[data-bcp="${name}"] .chrw.L${i}`;
      r += `${sel}{animation:${nm}_${i}t ${TT}s ease-in-out ${(l.dt == null ? 0.9 : l.dt).toFixed(2)}s infinite}`;
      r += `${sel} > .chri{animation:${nm}_${i}p ${TP}s ease-in-out ${(l.dp == null ? 0.8 : l.dp).toFixed(2)}s infinite}`;
    });
    if (c.amb) {
      k += `@keyframes ${nm}_clk{from{transform:translateX(0)}to{transform:translateX(1px)}}`;
      r += `#fxOv .hb.bcpic.bcpon:not(.bcst)[data-bcp="${name}"] .chrclk{animation:${nm}_clk 3600s linear 0s 1 both}`;
    }
    const st = document.createElement('style');
    st.textContent = k + '\n@media (prefers-reduced-motion:no-preference){' + r + '}';
    add(st);
  }
  Object.keys(CH).forEach(n => { const c = CH[n]; [c.bgx, c.fgx, c.oc && c.oc.src, c.ot && c.ot.src, c.amb && c.amb.f, c.amb && c.amb.m1, c.amb && c.amb.m2, c.amb && c.amb.m3].concat(c.layers.map(l => l.src), c.layers.map(l => l.f)).forEach(s => { if (s) { const im = new Image(); im.src = s; } }); });
  // ---- まわりの 光と 雲（WebGL）----
  const AVS = 'attribute vec2 p;void main(){gl_Position=vec4(p,0.0,1.0);}';
  const AFS = [
    'precision highp float;',
    'uniform sampler2D uO,uF,uM1,uM2,uM3;',
    'uniform vec2 uC,uS;uniform float uT,uA;uniform vec4 uR,uK,uQ;',
    'const vec2 SZ=vec2(1170.0,2532.0);const float TAU=6.2831853;',
    'void main(){',
    '  vec2 px=vec2(gl_FragCoord.x,uC.y-gl_FragCoord.y)*(SZ.x/uC.x);vec2 uv=px/SZ;',
    '  vec3 m2=texture2D(uM2,uv).rgb;float w=m2.b;',
    '  if(w<0.002){gl_FragColor=vec4(0.0);return;}',
    '  vec3 m1=texture2D(uM1,uv).rgb;vec3 m3=texture2D(uM3,uv).rgb;',
    '  float rw=m2.r*uA,cw=m1.b*uA;',
    // 光の すじ：もと uS の まわりで 回す（uR.x rad・uR.y 秒）
    '  float th=uR.x*sin(TAU*uT/uR.y);vec2 r=px-uS;float cs=cos(th),sn=sin(th);',
    '  vec2 d=(vec2(cs*r.x-sn*r.y,sn*r.x+cs*r.y)-r)*rw;',
    // 雲：向き dir に 外へ 流れる 波（uK.x px・uK.z 秒・波長 uQ.x）＋横の ゆれ（uK.y px・uK.w 秒）
    '  vec2 dir=m1.rg*2.0-1.0;vec2 pp=vec2(-dir.y,dir.x);float rr=length(px-uQ.yz);',
    '  d+=cw*(uK.x*dir*sin(TAU*(uT/uK.z-rr/uQ.x)+TAU*m2.g)+uK.y*pp*sin(TAU*uT/uK.w+TAU*m3.b));',
    '  vec2 q=(px+d)/SZ;vec3 col=texture2D(uO,q).rgb;',
    // 取った 所が 動かない 所（トロフィー・紙ふぶき）なら うめた 色
    '  float fs=texture2D(uM3,q).r*(1.0-m3.r);col=mix(col,texture2D(uF,q).rgb,fs);',
    // 光の すじの 明るさ：角度で ゆっくり 流れる（uR.z・uR.w 秒・すじの 数 uQ.w）
    '  float ang=atan(px.x-uS.x,px.y-uS.y);float fr=smoothstep(90.0,320.0,length(r));',   // 光の もとの 近くは 流さない（すじが 1点に あつまる）
    '  col*=1.0+rw*fr*uR.z*sin(TAU*uT/uR.w-uQ.w*ang);',
    '  gl_FragColor=vec4(col*w,w);',
    '}'].join('\n');
  function ambSetup(wrap, rb, c) {
    const A = c.amb, u = A.u || {};
    const cv = document.createElement('canvas'); cv.className = 'chramb';
    const dpr = Math.min(3, window.devicePixelRatio || 1); cv.width = Math.round(390 * dpr); cv.height = Math.round(844 * dpr);
    if (rb) wrap.insertBefore(cv, rb); else wrap.appendChild(cv);
    const clk = document.createElement('i'); clk.className = 'chrclk'; wrap.appendChild(clk);
    let gl = null, pg = null, U = {}, ready = false, dead = false, drawn = false, lastT = -1;
    const init = () => {
      try { gl = cv.getContext('webgl', { alpha: true, premultipliedAlpha: true, antialias: false, depth: false, stencil: false, preserveDrawingBuffer: false }); } catch (e) { gl = null; }
      if (!gl) { dead = true; cv.remove(); return; }
      cv.addEventListener('webglcontextlost', e => { e.preventDefault(); dead = true; cv.style.display = 'none'; });
      const sh = (ty, src) => { const o = gl.createShader(ty); gl.shaderSource(o, src); gl.compileShader(o); if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(o)); return o; };
      try {
        pg = gl.createProgram(); gl.attachShader(pg, sh(gl.VERTEX_SHADER, AVS)); gl.attachShader(pg, sh(gl.FRAGMENT_SHADER, AFS)); gl.linkProgram(pg);
        if (!gl.getProgramParameter(pg, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(pg));
      } catch (e) { console.warn('[bcp amb]', e && e.message); dead = true; cv.remove(); return; }
      gl.useProgram(pg);
      const b = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, b); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
      const loc = gl.getAttribLocation(pg, 'p'); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
      ['uO', 'uF', 'uM1', 'uM2', 'uM3', 'uC', 'uS', 'uT', 'uA', 'uR', 'uK', 'uQ'].forEach(n => { U[n] = gl.getUniformLocation(pg, n); });
      ['uO', 'uF', 'uM1', 'uM2', 'uM3'].forEach((n, i) => gl.uniform1i(U[n], i));
      const srcs = [c.bgx, A.f, A.m1, A.m2, A.m3]; let left = srcs.length;
      srcs.forEach((s, i) => {
        const im = new Image();
        im.onload = () => {
          if (dead) return;
          gl.activeTexture(gl.TEXTURE0 + i); gl.bindTexture(gl.TEXTURE_2D, gl.createTexture());
          gl.pixelStorei(gl.UNPACK_COLORSPACE_CONVERSION_WEBGL, i === 0 ? gl.BROWSER_DEFAULT_WEBGL : gl.NONE);
          gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, im);
          [[gl.TEXTURE_MIN_FILTER, gl.LINEAR], [gl.TEXTURE_MAG_FILTER, gl.LINEAR], [gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE], [gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE]].forEach(([k, v]) => gl.texParameteri(gl.TEXTURE_2D, k, v));
          if (--left === 0) ready = true;
        };
        im.onerror = () => { dead = true; cv.remove(); };
        im.src = s;
      });
      gl.uniform2f(U.uC, cv.width, cv.height);
      const S = u.src || [585, 40]; gl.uniform2f(U.uS, S[0], S[1]);
      gl.uniform4f(U.uR, (u.deg == null ? 1.1 : u.deg) * Math.PI / 180, u.pr || 8, u.sh == null ? 0.1 : u.sh, u.ps || 7);
      gl.uniform4f(U.uK, u.a1 == null ? 10 : u.a1, u.a2 == null ? 5 : u.a2, u.p1 || 6, u.p2 || 8.5);
      const C = u.c || [585, 1350]; gl.uniform4f(U.uQ, u.wl || 420, C[0], C[1], u.bands || 6);
    };
    const clear = () => { if (gl && drawn) { gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT); } drawn = false; lastT = -1; };
    const tick = () => {
      if (!wrap.isConnected) { if (gl) { const x = gl.getExtension('WEBGL_lose_context'); if (x) x.loseContext(); } return; }
      requestAnimationFrame(tick);
      if (dead) return;
      const an = clk.getAnimations ? clk.getAnimations()[0] : null;
      if (!an) { clear(); return; }
      if (!gl) init();
      if (dead || !ready) return;
      const t = (an.currentTime || 0) / 1000;
      if (t === lastT) return;
      lastT = t;
      const rp = u.ramp || 1.5, x = Math.min(1, Math.max(0, t / rp)), amp = x * x * (3 - 2 * x);   // 出はじめは 0 から なめらかに
      gl.uniform1f(U.uT, t); gl.uniform1f(U.uA, amp);
      gl.viewport(0, 0, cv.width, cv.height); gl.drawArrays(gl.TRIANGLES, 0, 3); drawn = true;
    };
    requestAnimationFrame(tick);
  }
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
    // キャラ：ボードの 下（top：いつも ボードの 前に ある キャラ＝花束の 花 は アプリの ボードと 前の 絵の 上＝前の 絵との さかいで 切れない）
    c.layers.forEach((l, i) => { const w = mk(l, i, l.src); if (rb && !c.top) wrap.insertBefore(w, rb); else wrap.appendChild(w); });
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
    if (c.amb) ambSetup(wrap, rb, c);   // まわりの 光と 雲：舞台の 絵の すぐ 上・アプリの ボードの 下
  }
  const scan = () => { add(base); document.querySelectorAll('#fxOv .hb.bcpic').forEach(setup); };
  new MutationObserver(scan).observe(document, { childList: true, subtree: true, attributes: true, attributeFilter: ['class', 'data-bcp'] });
})();
