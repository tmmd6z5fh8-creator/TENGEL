// 思い出フィギュア：3D の 描画（App Store版・WebGL1）。fig_app.js が 使う（まさちゃん 2026/11/09：フィギュア 8体・3D の 棚 7色）
//   ・棚：まさちゃんの 3D の 棚に 7色の 絵を 正面から はった もの（kisekae/fig/collect_assets.py → fg_shelf.json・.bin・fg_shelf_c1〜7.webp）。光は あてず 絵の まま
//   ・フィギュア：形（16bit の 位置・UV）と 色・法線（物の 向きの まま）・金属／あらさ の 絵（fgN.json・.bin・fgN_c／n／m.webp）。
//     ブースでは 小さい 絵（fgN_cs／ns／ms.webp）・部屋（1体を 大きく 見る）では 大きい 絵
//   ・ボード：思い出の レースの 文字を キャンバスに 書いて、フィギュアの ボードの 板（fgN.json の board）の 前に はる
//   FigGL.create(canvas) → { booth(), room(), slotRects(), snapshot(), ... }（fig_app.js）
const FigGL = (() => {
  'use strict';
  const AP = p => String(p).split('/').pop();                 // アプリ：Resources に 名前だけ
  // ---------- 棚の 置き場所（棚の 体の 座標：高さ 2.15・まん中 x=0）：上の 段から 左・右 の 8こ ----------
  const FLOOR = [1.585, 1.072, 0.572, 0.062], COLX = [-0.388, 0.388];
  const SLOT_H = 0.40, SLOT_W = 0.64, SLOT_D = 0.30, SLOT_Z = 0.06, CUB_W = 0.322, CUB_H = 0.46, FRONT_Z = 0.244;
  const SLOTS = []; for (let r = 0; r < 4; r++) for (let c = 0; c < 2; c++) SLOTS.push({ x: COLX[c], y: FLOOR[r], z: SLOT_Z, ceil: FLOOR[r] + CUB_H, row: r, col: c });
  // ---------- ボードの 板の 色（フィギュアの わくの 色に 合わせる）----------
  const PAL = {
    gold: { bg: [['#f6dc8a', 0], ['#d9a83c', 0.45], ['#b8862a', 1]], dir: 'diag', ink: '#3b2408', sub: '#4a300c', kind: '#7a1d12', money: '#5a1c0c', hi: 'rgba(255,240,190,0.9)', line: 'rgba(110,70,10,0.55)' },
    amethyst: { bg: [['#b65cc8', 0], ['#7d2590', 0.5], ['#4e1060', 1]], dir: 'diag', ink: '#fff4dc', sub: '#f3dcf6', kind: '#ffd36a', money: '#ffe08a', hi: 'rgba(40,0,50,0.75)', line: 'rgba(255,215,120,0.6)' },
    duel: { bg: [['#7d2590', 0], ['#a8467a', 0.45], ['#d9a83c', 1]], dir: 'h', ink: '#fffaf0', sub: '#fff0dc', kind: '#ffe08a', money: '#fff1b0', hi: 'rgba(40,10,20,0.8)', line: 'rgba(255,225,140,0.6)' } };
  const FONT_D = '"Dela Gothic One","Hiragino Sans",sans-serif', FONT_B = '"BIZ UDPGothic","Hiragino Sans",sans-serif';

  // ---------- シェーダー：棚（絵の まま）・かげ・フィギュア（光）・ボード（平らな 金属の 板） ----------
  //   位置と UV は 16bit の まま 送って、ここで もどす（uQo＋aP×uQs）。かげ・ボード・床は 小数の まま（uQo=0・uQs=1）
  const VS = 'attribute vec3 aP;attribute vec2 aU;uniform mat4 uVP;uniform mat4 uM;uniform vec3 uQo,uQs;varying vec2 vU;varying vec3 vW;'
    + 'void main(){vec4 w=uM*vec4(uQo+aP*uQs,1.0);vW=w.xyz;vU=aU;gl_Position=uVP*w;}';
  const FS = 'precision highp float;varying vec2 vU;varying vec3 vW;'
    + 'uniform sampler2D uC,uNm,uMr;uniform float uMode,uEnvSpot;uniform vec4 uTint;uniform vec3 uEye,uLp,uLc,uLd1,uLc1,uLd2,uLc2,uEnvLo,uEnvHi,uAmbLo,uAmbHi,uMRc;uniform float uLk,uTone;'
    + 'vec3 toLin(vec3 c){return pow(c,vec3(2.2));}'
    + 'void main(){vec4 t=texture2D(uC,vU);'
    + 'if(uMode>2.5){float a=t.a*uTint.a;gl_FragColor=vec4(t.rgb*uTint.rgb*a,a);return;}'      // 3：床の あかり（光なし・すける：色は アルファを かけた 形）
    + 'if(uMode>1.5){float a=uTint.a*t.a;gl_FragColor=vec4(uTint.rgb*a,a);return;}'              // 2：かげ（まるい ぼかし）
    + 'if(uMode>0.5&&uMode<1.5){gl_FragColor=vec4(t.rgb,1.0);return;}'                          // 1：棚（絵の 色の まま）
    + 'bool bd=uMode<-0.5;if(bd&&t.a<0.5)discard;'                                          // -1：ボード（板の 前の 平らな 面）
    + 'vec3 base=toLin(t.rgb);vec3 n=bd?vec3(0.0,0.0,1.0):normalize(texture2D(uNm,vU).xyz*2.0-1.0);'
    + 'vec3 mr=bd?vec3(1.0,uMRc.y,uMRc.z*smoothstep(0.25,0.6,dot(t.rgb,vec3(0.33)))):texture2D(uMr,vU).rgb;float rough=clamp(mr.g,0.08,1.0),metal=clamp(mr.b,0.0,1.0);'
    + 'vec3 V=normalize(uEye-vW);vec3 Ls=uLp-vW;float ds=length(Ls);Ls/=ds;float att=uLk>0.0?1.0/(1.0+ds*ds*uLk):1.0;'
    + 'vec3 dif=base*(1.0-metal);vec3 F0=mix(vec3(0.04),base,metal);float sh=2.0/(rough*rough*rough*rough+0.002)-2.0;vec3 col=vec3(0.0);'
    + 'for(int i=0;i<3;i++){vec3 L=i==0?Ls:(i==1?uLd1:uLd2);vec3 C=i==0?uLc*att:(i==1?uLc1:uLc2);'
    + 'float nl=max(dot(n,L),0.0);vec3 Hh=normalize(L+V);float nh=max(dot(n,Hh),0.0);vec3 F=F0+(1.0-F0)*pow(1.0-max(dot(Hh,V),0.0),5.0);'
    + 'col+=C*(dif*nl/3.14159+F*pow(nh,sh)*(sh+8.0)/25.1327*nl);}'
    + 'vec3 R=reflect(-V,n);float up=R.y*0.5+0.5;'
    + 'vec3 env=mix(uEnvLo,uEnvHi,smoothstep(0.3,0.95,up))+vec3(1.4,1.3,1.15)*uEnvSpot*smoothstep(0.75,0.98,up)*(1.0-rough);'
    + 'vec3 Fe=F0+(1.0-F0)*pow(1.0-max(dot(n,V),0.0),5.0)*(1.0-rough);vec3 amb=mix(uAmbLo,uAmbHi,n.y*0.5+0.5);'
    + 'col+=dif*amb+Fe*env*mix(0.3,1.0,metal)*(1.0-rough*0.6);col=col/(1.0+col*uTone);'
    + 'gl_FragColor=vec4(pow(col,vec3(1.0/2.2)),1.0);}';

  // ---------- 小さな 行列 ----------
  const M4 = {
    mul(a, b) { const o = new Float32Array(16); for (let c = 0; c < 4; c++) for (let r = 0; r < 4; r++) { let s = 0; for (let k = 0; k < 4; k++) s += a[k * 4 + r] * b[c * 4 + k]; o[c * 4 + r] = s; } return o; },
    persp(fy, asp, n, f) { const t = 1 / Math.tan(fy / 2); return new Float32Array([t / asp, 0, 0, 0, 0, t, 0, 0, 0, 0, (f + n) / (n - f), -1, 0, 0, 2 * f * n / (n - f), 0]); },
    look(e, c) { const f = nrm([c[0] - e[0], c[1] - e[1], c[2] - e[2]]), s = nrm(crs(f, [0, 1, 0])), u = crs(s, f); return new Float32Array([s[0], u[0], -f[0], 0, s[1], u[1], -f[1], 0, s[2], u[2], -f[2], 0, -dot(s, e), -dot(u, e), dot(f, e), 1]); },
    st(s, x, y, z) { return new Float32Array([s, 0, 0, 0, 0, s, 0, 0, 0, 0, s, 0, x, y, z, 1]); } };
  function nrm(v) { const l = Math.hypot(v[0], v[1], v[2]) || 1; return [v[0] / l, v[1] / l, v[2] / l]; }
  function crs(a, b) { return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]; }
  function dot(a, b) { return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]; }
  function proj(VP, p) { const x = VP[0] * p[0] + VP[4] * p[1] + VP[8] * p[2] + VP[12], y = VP[1] * p[0] + VP[5] * p[1] + VP[9] * p[2] + VP[13], w = VP[3] * p[0] + VP[7] * p[1] + VP[11] * p[2] + VP[15]; return [x / w, y / w]; }

  // ---------- ボードの 絵（キャンバス）：aspect＝板の 横／縦・size＝絵の 大きさ（2の べき乗：ミップマップ）----------
  //   info＝{ kind（的中の 種類）, race, date, lines（買い目 0〜3行）, result, money }
  function boardCanvas(info, aspect, pal, size) {
    const PC = PAL[pal] || PAL.gold, S = size || 1024, Wc = 1024, Hc = Math.round(Wc / Math.max(0.5, aspect || 1.4));
    const c = document.createElement('canvas'); c.width = S; c.height = S; const g = c.getContext('2d'); g.scale(S / Wc, S / Hc);
    const r = Math.min(Wc, Hc) * 0.07; g.beginPath(); g.moveTo(r, 0); g.arcTo(Wc, 0, Wc, Hc, r); g.arcTo(Wc, Hc, 0, Hc, r); g.arcTo(0, Hc, 0, 0, r); g.arcTo(0, 0, Wc, 0, r); g.closePath(); g.clip();
    const gr = PC.dir === 'h' ? g.createLinearGradient(0, 0, Wc, 0) : g.createLinearGradient(0, 0, Wc * 0.4, Hc); PC.bg.forEach(([cc, o]) => gr.addColorStop(o, cc)); g.fillStyle = gr; g.fillRect(0, 0, Wc, Hc);
    g.strokeStyle = PC.line; g.lineWidth = Hc * 0.012; g.strokeRect(Wc * 0.035, Hc * 0.05, Wc * 0.93, Hc * 0.9);
    info = info || {};
    const rows = [];
    if (info.kind) rows.push({ t: info.kind, s: 0.085, f: FONT_D, w: 400, c: PC.kind });
    if (info.race) rows.push({ t: info.race, s: 0.11, f: FONT_D, w: 400, c: PC.ink });
    if (info.date) rows.push({ t: info.date, s: 0.06, f: FONT_B, w: 700, c: PC.sub });
    (info.lines || []).slice(0, 3).forEach((t, i) => rows.push({ t, s: 0.066, f: FONT_B, w: 700, c: PC.ink, gap: i === 0 ? 0.25 : 0 }));
    if (info.result) rows.push({ t: info.result, s: 0.056, f: FONT_B, w: 700, c: PC.sub, gap: 0.2 });
    if (info.money) rows.push({ t: info.money, s: 0.064, f: FONT_B, w: 700, c: PC.money });
    let tot = 0; rows.forEach(o => { tot += o.s * (1.32 + (o.gap || 0)); });
    const k = Math.min(1.25, 0.8 / Math.max(0.01, tot));          // 行が 多い ときは 字を 小さく・少ない ときは 少し 大きく
    let y = Hc * (0.5 - tot * k / 2);
    g.textAlign = 'center'; g.textBaseline = 'middle';
    rows.forEach(o => {
      y += Hc * o.s * k * (o.gap || 0);
      let sz = Hc * o.s * k; const fnt = s => `${o.w} ${s}px ${o.f}`; g.font = fnt(sz);
      while (g.measureText(o.t).width > Wc * 0.86 && sz > 8) { sz -= 1.5; g.font = fnt(sz); }
      const yy = y + Hc * o.s * k * 0.66;
      g.fillStyle = PC.hi; g.fillText(o.t, Wc / 2 + 2, yy + 2); g.fillStyle = o.c; g.fillText(o.t, Wc / 2, yy);
      y += Hc * o.s * k * 1.32;
    });
    return c;
  }
  function radial(stops, sz) {
    const c = document.createElement('canvas'); c.width = c.height = sz || 128; const g = c.getContext('2d'), h = c.width / 2, gr = g.createRadialGradient(h, h, 2, h, h, h - 1);
    stops.forEach(([o, col]) => gr.addColorStop(o, col)); g.fillStyle = gr; g.fillRect(0, 0, c.width, c.width); return c;
  }

  function create(canvas) {
    const gl = canvas.getContext('webgl', { antialias: true, alpha: true, premultipliedAlpha: true, preserveDrawingBuffer: false, powerPreference: 'default' });
    if (!gl) return null;
    const ext32 = gl.getExtension('OES_element_index_uint');
    let prog = null, U = {}, A = {}, lost = false;
    const cache = { mesh: {}, tex: {} };          // mesh：'fg3'・'fg_shelf'／tex：名前 → { t, n（使う 数）}
    function sh(t, s) { const o = gl.createShader(t); gl.shaderSource(o, s); gl.compileShader(o); if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(o) || 'shader'); return o; }
    function init() {
      prog = gl.createProgram(); gl.attachShader(prog, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, FS)); gl.linkProgram(prog);
      if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) throw new Error('link');
      gl.useProgram(prog); U = {}; A = { aP: gl.getAttribLocation(prog, 'aP'), aU: gl.getAttribLocation(prog, 'aU') };
      ['uVP', 'uM', 'uQo', 'uQs', 'uC', 'uNm', 'uMr', 'uMode', 'uEnvSpot', 'uTint', 'uEye', 'uLp', 'uLc', 'uLd1', 'uLc1', 'uLd2', 'uLc2', 'uEnvLo', 'uEnvHi', 'uAmbLo', 'uAmbHi', 'uMRc', 'uLk', 'uTone'].forEach(n => { U[n] = gl.getUniformLocation(prog, n); });
      gl.uniform1i(U.uC, 0); gl.uniform1i(U.uNm, 1); gl.uniform1i(U.uMr, 2);
      Q.quad = buf(new Float32Array([0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0])); Q.uv = buf(new Float32Array([0, 1, 1, 1, 1, 0, 0, 0])); Q.idx = buf(new Uint16Array([0, 1, 2, 0, 2, 3]), gl.ELEMENT_ARRAY_BUFFER);
      Q.shadow = texOf(radial([[0, 'rgba(255,255,255,1)'], [1, 'rgba(255,255,255,0)']]));
      Q.floor = texOf(radial([[0, 'rgba(255,226,180,0.55)'], [0.45, 'rgba(255,214,160,0.18)'], [1, 'rgba(255,214,160,0)']], 256));
    }
    const Q = {};
    function buf(data, target) { const b = gl.createBuffer(); gl.bindBuffer(target || gl.ARRAY_BUFFER, b); gl.bufferData(target || gl.ARRAY_BUFFER, data, gl.STATIC_DRAW); return b; }
    function texOf(src) {
      const t = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, t); gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, false);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, src);
      const pot = !(src.width & (src.width - 1)) && !(src.height & (src.height - 1));
      if (pot) { gl.generateMipmap(gl.TEXTURE_2D); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR); } else gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
      return t;
    }
    const img = src => new Promise((ok, ng) => { const im = new Image(); im.decoding = 'async'; im.onload = () => ok(im); im.onerror = () => ng(new Error('img ' + src)); im.src = AP(src); });
    // 絵（名前ごとに 1つ）：use で 数える・drop で 0 に なったら すてる
    async function tex(name) {
      let e = cache.tex[name]; if (!e) { e = cache.tex[name] = { p: img(name).then(im => { if (lost) throw new Error('lost'); e.t = texOf(im); return e.t; }), n: 0 }; e.p.catch(() => { if (cache.tex[name] === e) delete cache.tex[name]; }); }
      e.n++; return e.p;
    }
    function drop(name) { const e = cache.tex[name]; if (!e) return; e.n--; if (e.n <= 0) { if (e.t) gl.deleteTexture(e.t); delete cache.tex[name]; } }
    // 形（bin）の 番号を 詰めた 入れもの（kisekae/lite_assets.py の pack_idx：第4.151版）を もとの 形に もどす。詰めて いない bin は そのまま 返す
    //   頭 24バイト＝'TGIZ'・もとの 長さ・番号の 場所・番号の バイト数・番号の 数・詰めた 長さ → 番号より 前・番号より 後ろ・詰めた 番号（前の 番号との 差を ジグザグに して 7bit ずつ）
    function unz(ab) {
      const u = new Uint8Array(ab);
      if (u.length < 24 || u[0] !== 0x54 || u[1] !== 0x47 || u[2] !== 0x49 || u[3] !== 0x5A) return ab;
      const dv = new DataView(ab), L = dv.getUint32(4, true), io = dv.getUint32(8, true), ib = dv.getUint32(12, true), n = dv.getUint32(16, true), pl = dv.getUint32(20, true), tail = L - io - ib;
      if (tail < 0 || 24 + io + tail + pl !== u.length || ib !== n * 4 || io % 4) throw new Error('bin');
      const out = new ArrayBuffer(L), o8 = new Uint8Array(out); o8.set(u.subarray(24, 24 + io), 0); o8.set(u.subarray(24 + io, 24 + io + tail), io + ib);
      const idx = new Uint32Array(out, io, n), end = u.length; let p = 24 + io + tail, prev = 0;
      for (let i = 0; i < n; i++) {
        let v = 0, s = 0, b;
        do { if (p >= end) throw new Error('bin'); b = u[p++]; v += (b & 127) * Math.pow(2, s); s += 7; } while (b & 128);
        prev += (v % 2) ? -(v + 1) / 2 : v / 2; idx[i] = prev;
      }
      if (p !== end) throw new Error('bin');
      return out;
    }
    // 形（名前ごとに 1つ・すてない：棚 1つと フィギュア 8種）
    function mesh(name) {
      if (cache.mesh[name]) return cache.mesh[name];
      const p = (async () => {
        const meta = await fetch(AP(name + '.json')).then(r => { if (!r.ok) throw new Error('no ' + name); return r.json(); });
        const bin = unz(await fetch(AP(name + '.bin')).then(r => { if (!r.ok) throw new Error('no ' + name); return r.arrayBuffer(); }));      // 第4.151版：番号を 詰めた 形（フィギュア 8体）は もとの 形に もどす
        if (lost) throw new Error('lost');
        if (meta.idx32 && !ext32) throw new Error('idx32');
        const L = meta.layout;
        return { meta, pos: buf(new Uint16Array(bin, L.pos[0], meta.v * 3)), uv: buf(new Uint16Array(bin, L.uv[0], meta.v * 2)),
          idx: buf(meta.idx32 ? new Uint32Array(bin, L.idx[0], meta.i) : new Uint16Array(bin, L.idx[0], meta.i), gl.ELEMENT_ARRAY_BUFFER), n: meta.i, i32: !!meta.idx32 };
      })();
      cache.mesh[name] = p; p.catch(() => { if (cache.mesh[name] === p) delete cache.mesh[name]; });
      return p;
    }
    function attrQ(m) {
      gl.bindBuffer(gl.ARRAY_BUFFER, m.pos); gl.enableVertexAttribArray(A.aP); gl.vertexAttribPointer(A.aP, 3, gl.UNSIGNED_SHORT, true, 0, 0);
      gl.bindBuffer(gl.ARRAY_BUFFER, m.uv); gl.enableVertexAttribArray(A.aU); gl.vertexAttribPointer(A.aU, 2, gl.UNSIGNED_SHORT, true, 0, 0);
      gl.uniform3fv(U.uQo, m.meta.qo); gl.uniform3fv(U.uQs, m.meta.qs); gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, m.idx);
    }
    function attrF(p, u) {
      gl.bindBuffer(gl.ARRAY_BUFFER, p); gl.enableVertexAttribArray(A.aP); gl.vertexAttribPointer(A.aP, 3, gl.FLOAT, false, 0, 0);
      gl.bindBuffer(gl.ARRAY_BUFFER, u); gl.enableVertexAttribArray(A.aU); gl.vertexAttribPointer(A.aU, 2, gl.FLOAT, false, 0, 0);
      gl.uniform3f(U.uQo, 0, 0, 0); gl.uniform3f(U.uQs, 1, 1, 1);
    }
    function bindTex(c, n, m) {
      gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, c);
      gl.activeTexture(gl.TEXTURE1); gl.bindTexture(gl.TEXTURE_2D, n || c);
      gl.activeTexture(gl.TEXTURE2); gl.bindTexture(gl.TEXTURE_2D, m || c);
    }
    function drawIdx(m) { gl.drawElements(gl.TRIANGLES, m.n, m.i32 ? gl.UNSIGNED_INT : gl.UNSIGNED_SHORT, 0); }
    // 長方形（u0..u1 × v0..v1 の 平らな 板）：p0＝左下・ax／ay＝横・縦の 向きの 長さ
    function quad(p0, ax, ay) {
      const q = new Float32Array([p0[0], p0[1], p0[2], p0[0] + ax[0], p0[1] + ax[1], p0[2] + ax[2], p0[0] + ax[0] + ay[0], p0[1] + ax[1] + ay[1], p0[2] + ax[2] + ay[2], p0[0] + ay[0], p0[1] + ay[1], p0[2] + ay[2]]);
      gl.bindBuffer(gl.ARRAY_BUFFER, Q.quad); gl.bufferData(gl.ARRAY_BUFFER, q, gl.DYNAMIC_DRAW);
      attrF(Q.quad, Q.uv); gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, Q.idx); gl.drawElements(gl.TRIANGLES, 6, gl.UNSIGNED_SHORT, 0);
    }

    // ---------- フィギュア 1体（形・絵・ボードの 板）----------
    //   lod：'s'（ブース：小さい 絵）・'l'（部屋：大きい 絵）
    async function figure(n, lod) {
      const m = await mesh('fg' + n), s = lod === 'l' ? '' : 's';
      const names = [`fg${n}_c${s}.webp`, `fg${n}_n${s}.webp`, `fg${n}_m${s}.webp`];
      let ts;
      try { ts = await Promise.all(names.map(tex)); } catch (e) { names.forEach(drop); throw e; }
      const bb = m.meta.bbox, w = bb[1][0] - bb[0][0], h = bb[1][1] - bb[0][1], d = bb[1][2] - bb[0][2];
      return { n, m, tc: ts[0], tn: ts[1], tm: ts[2], names, w, h, d, board: m.meta.board, pal: m.meta.pal || 'gold', release: () => names.forEach(drop) };
    }
    // ボードの 絵（その フィギュアの 板の 縦横で 書く）
    function boardTex(F, info, size) { return texOf(boardCanvas(info, F.board ? F.board.w / F.board.h : 1.4, F.pal, size)); }
    function setLights(o) {
      gl.uniform3fv(U.uEye, o.eye); gl.uniform3fv(U.uLp, o.lp); gl.uniform3fv(U.uLc, o.lc); gl.uniform1f(U.uLk, o.lk);
      gl.uniform3fv(U.uLd1, nrm(o.ld1)); gl.uniform3fv(U.uLc1, o.lc1); gl.uniform3fv(U.uLd2, nrm(o.ld2)); gl.uniform3fv(U.uLc2, o.lc2);
      gl.uniform3fv(U.uEnvLo, o.envLo); gl.uniform3fv(U.uEnvHi, o.envHi); gl.uniform1f(U.uEnvSpot, o.envSpot || 0); gl.uniform3fv(U.uAmbLo, o.ambLo); gl.uniform3fv(U.uAmbHi, o.ambHi); gl.uniform1f(U.uTone, o.tone || 0.3);
    }
    function drawFig(F, M, boardT) {
      gl.uniform1f(U.uMode, 0); gl.uniformMatrix4fv(U.uM, false, M); attrQ(F.m); bindTex(F.tc, F.tn, F.tm); drawIdx(F.m);
      if (boardT && F.board) {
        const b = F.board, z = b.c[2] + 0.008;      // 板の 面の いちばん 前（board_find.py）より 少し 前
        gl.uniform1f(U.uMode, -1); gl.uniform3f(U.uMRc, 1, 0.38, 0.85); bindTex(boardT);
        quad([b.c[0] - b.w / 2, b.c[1] - b.h / 2, z], [b.w, 0, 0], [0, b.h, 0]);
      }
    }
    function blob(x, y, z, w, d, a) {
      gl.uniform1f(U.uMode, 2); gl.uniform4f(U.uTint, 0, 0, 0, a); gl.uniformMatrix4fv(U.uM, false, M4.st(1, 0, 0, 0)); bindTex(Q.shadow);
      quad([x - w, y, z + d], [2 * w, 0, 0], [0, 0, -2 * d]);
    }
    function begin(W, H, clear) {
      gl.viewport(0, 0, W, H); gl.clearColor(clear[0], clear[1], clear[2], clear[3]); gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
      gl.enable(gl.DEPTH_TEST); gl.depthFunc(gl.LEQUAL); gl.disable(gl.BLEND); gl.depthMask(true); gl.disable(gl.CULL_FACE); gl.useProgram(prog);
    }

    // ---------- ブース（棚 1つ・フィギュア 8こまで）----------
    //   B＝{ shelfT（棚の 絵）, figs:[{ slot（0〜7）, F, boardT }], yaw, pitch（度）}
    function boothCam(W, H, yaw, pitch) {
      const fov = 17 * Math.PI / 180, tgt = [0, 1.075, 0], asp = W / H;
      const dist = Math.max(2.26 / 2 / Math.tan(fov / 2), 1.75 / 2 / Math.tan(fov / 2) / asp) * 1.04 + 0.25;
      const a = (yaw || 0) * Math.PI / 180, e = (pitch || 0) * Math.PI / 180;
      const eye = [tgt[0] + dist * Math.sin(a) * Math.cos(e), tgt[1] + dist * Math.sin(e), tgt[2] + dist * Math.cos(a) * Math.cos(e)];
      return { eye, VP: M4.mul(M4.persp(fov, asp, Math.max(0.5, dist - 3), dist + 3), M4.look(eye, tgt)) };
    }
    async function shelfMesh() { return mesh('fg_shelf'); }
    function drawBooth(W, H, B) {
      const cam = boothCam(W, H, B.yaw, B.pitch);
      begin(W, H, [0, 0, 0, 0]);
      gl.uniformMatrix4fv(U.uVP, false, cam.VP);
      if (B.shelf && B.shelfT) { gl.uniform1f(U.uMode, 1); gl.uniformMatrix4fv(U.uM, false, M4.st(1, 0, 0, 0)); attrQ(B.shelf); bindTex(B.shelfT); drawIdx(B.shelf); }
      gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA); gl.depthMask(false);
      for (const f of B.figs) { const s = SLOTS[f.slot], k = fitK(f.F); blob(s.x, s.y + 0.004, s.z, f.F.w * k * 0.62, f.F.d * k * 0.75, 0.55); }
      gl.disable(gl.BLEND); gl.depthMask(true);
      for (const f of B.figs) {
        const s = SLOTS[f.slot], k = fitK(f.F);
        setLights({ eye: cam.eye, lp: [s.x, s.ceil - 0.02, s.z + 0.32], lc: [3.0, 2.58, 1.86], lk: 2.0, ld1: [0, 0.35, 1], lc1: [0.5, 0.47, 0.44], ld2: [0.2, 0.5, -1], lc2: [0.45, 0.36, 0.25],
          envLo: [0.10, 0.07, 0.05], envHi: [0.95, 0.78, 0.52], envSpot: 0, ambLo: [0.10, 0.07, 0.05], ambHi: [0.32, 0.26, 0.2], tone: 0.3 });
        drawFig(f.F, M4.st(k, s.x, s.y, s.z), f.boardT);
      }
      return cam;
    }
    const fitK = F => Math.min(SLOT_H / F.h, SLOT_W / F.w, SLOT_D / F.d);
    // 置き場所の 画面の 四角（CSS の px）：棚の 箱の 前の 面
    function slotRects(W, H, yaw, pitch, cssW, cssH) {
      const cam = boothCam(W, H, yaw, pitch);
      return SLOTS.map(s => {
        let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
        for (const px of [s.x - CUB_W, s.x + CUB_W]) for (const py of [s.y, s.ceil]) {
          const q = proj(cam.VP, [px, py, FRONT_Z]), sx = (q[0] * 0.5 + 0.5) * cssW, sy = (0.5 - q[1] * 0.5) * cssH;
          x0 = Math.min(x0, sx); x1 = Math.max(x1, sx); y0 = Math.min(y0, sy); y1 = Math.max(y1, sy);
        }
        return { x: x0, y: y0, w: x1 - x0, h: y1 - y0 };
      });
    }

    // ---------- 部屋（1体を 大きく・まわして 見る）----------
    //   R＝{ F, boardT, yaw, pitch（度）, zoom }
    function roomCam(W, H, F, yaw, pitch, zoom) {
      const fov = 30 * Math.PI / 180, asp = W / H, tgt = [0, F.h * 0.5, 0];
      const fit = Math.max(F.h * 0.62 / Math.tan(fov / 2), Math.max(F.w, F.d) * 0.62 / Math.tan(fov / 2) / asp);
      const dist = fit * (zoom || 1) + Math.max(F.w, F.d) * 0.25;
      const a = (yaw || 0) * Math.PI / 180, e = (pitch || 0) * Math.PI / 180;
      const eye = [tgt[0] + dist * Math.sin(a) * Math.cos(e), tgt[1] + dist * Math.sin(e), tgt[2] + dist * Math.cos(a) * Math.cos(e)];
      return { eye, tgt, dist, VP: M4.mul(M4.persp(fov, asp, 0.05, dist * 4 + 20), M4.look(eye, tgt)) };
    }
    function drawRoom(W, H, R) {
      const F = R.F, cam = roomCam(W, H, F, R.yaw, R.pitch, R.zoom);
      begin(W, H, [0, 0, 0, 0]);
      gl.uniformMatrix4fv(U.uVP, false, cam.VP);
      // 床の あかりと かげ
      gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA); gl.depthMask(false);
      const fr = Math.max(F.w, F.d) * 1.25;
      gl.uniform1f(U.uMode, 3); gl.uniform4f(U.uTint, 1, 1, 1, 1); gl.uniformMatrix4fv(U.uM, false, M4.st(1, 0, 0, 0)); bindTex(Q.floor);
      quad([-fr, -0.002, fr], [2 * fr, 0, 0], [0, 0, -2 * fr]);
      blob(0, 0.001, 0, F.w * 0.6, F.d * 0.72, 0.6);
      gl.disable(gl.BLEND); gl.depthMask(true);
      // 光：カメラから 見て 左上の 前（いつも 前から 照らす）・右の 青白い 光・うしろの ふちの 光
      const f = nrm([cam.tgt[0] - cam.eye[0], cam.tgt[1] - cam.eye[1], cam.tgt[2] - cam.eye[2]]), s = nrm(crs(f, [0, 1, 0])), u = crs(s, f);
      const dirOf = (x, y, z) => nrm([s[0] * x + u[0] * y - f[0] * z, s[1] * x + u[1] * y - f[1] * z, s[2] * x + u[2] * y - f[2] * z]);
      const key = dirOf(-0.45, 0.65, 0.62);
      setLights({ eye: cam.eye, lp: [key[0] * 1000, key[1] * 1000, key[2] * 1000], lc: [2.3, 2.1, 1.85], lk: 0, ld1: dirOf(0.7, 0.25, 0.5), lc1: [0.62, 0.66, 0.8], ld2: dirOf(0.1, 0.5, -0.85), lc2: [1.0, 0.86, 0.66],
        envLo: [0.16, 0.12, 0.09], envHi: [1.05, 0.93, 0.76], envSpot: 1, ambLo: [0.14, 0.11, 0.09], ambHi: [0.42, 0.38, 0.34], tone: 0.34 });
      drawFig(F, M4.st(1, 0, 0, 0), R.boardT);
      return cam;
    }

    // ---------- 一覧用の 写真（ブースを 見えない 所で 書いて 絵に する）----------
    let fb = null;
    function snapshot(w, h, B, out) {
      if (!fb || fb.w !== w || fb.h !== h) {
        if (fb) { gl.deleteFramebuffer(fb.f); gl.deleteTexture(fb.t); gl.deleteRenderbuffer(fb.rb); }
        const t = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, t); gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, w, h, 0, gl.RGBA, gl.UNSIGNED_BYTE, null);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
        const rb = gl.createRenderbuffer(); gl.bindRenderbuffer(gl.RENDERBUFFER, rb); gl.renderbufferStorage(gl.RENDERBUFFER, gl.DEPTH_COMPONENT16, w, h);
        const f = gl.createFramebuffer(); gl.bindFramebuffer(gl.FRAMEBUFFER, f);
        gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, t, 0); gl.framebufferRenderbuffer(gl.FRAMEBUFFER, gl.DEPTH_ATTACHMENT, gl.RENDERBUFFER, rb);
        fb = { f, t, rb, w, h, px: new Uint8Array(w * h * 4) };
      }
      gl.bindFramebuffer(gl.FRAMEBUFFER, fb.f);
      drawBooth(w, h, B);
      gl.readPixels(0, 0, w, h, gl.RGBA, gl.UNSIGNED_BYTE, fb.px);
      gl.bindFramebuffer(gl.FRAMEBUFFER, null);
      const tmp = document.createElement('canvas'); tmp.width = w; tmp.height = h; const tg = tmp.getContext('2d'), id = tg.createImageData(w, h), row = w * 4;
      for (let y = 0; y < h; y++) id.data.set(fb.px.subarray((h - 1 - y) * row, (h - y) * row), y * row);      // 上下 さかさま → もどす
      tg.putImageData(id, 0, 0);
      const g = out.getContext('2d'); g.clearRect(0, 0, out.width, out.height); g.imageSmoothingEnabled = true; g.imageSmoothingQuality = 'high'; g.drawImage(tmp, 0, 0, out.width, out.height);
      return out;
    }

    function freeTex(t) { if (t) gl.deleteTexture(t); }
    canvas.addEventListener('webglcontextlost', e => { e.preventDefault(); lost = true; }, false);
    canvas.addEventListener('webglcontextrestored', () => { lost = false; cache.mesh = {}; cache.tex = {}; fb = null; try { init(); } catch (e) { /* つぎに 開いた とき */ } if (api.onRestore) api.onRestore(); }, false);
    init();
    const api = { gl, figure, boardTex, freeTex, tex, drop, shelfMesh, drawBooth, drawRoom, slotRects, snapshot, fitK, get lost() { return lost; }, onRestore: null };
    return api;
  }
  return { create, boardCanvas, SLOTS, PAL };
})();
