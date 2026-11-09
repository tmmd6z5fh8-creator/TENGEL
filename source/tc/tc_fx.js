// トレーニングセンターの 当たりの 演出（App Store版）：ルーレット（ノーマル・幻の馬・神様馬の 3つの 絵）・壁紙チケット
//   h3d/roulette2.html・ticket.html と 同じ 絵と 動き（390×614 の 座標で 描いて キャンバスの 大きさに 合わせる）
//   ・うしろは いまの フィールド（下の キャンバスが そのまま 見える：少し 暗く）
//   ・「タップ」で レバーを たたく（ルーレット）・扉が 開く（チケット）：押すまで 待つ（30秒 たったら 自動）
//   ・GET の あとは タップか 3秒で とじる → Promise が とける
//   ・ちかちか しない（光は ゆっくり 1回・回る 速さは 2回／秒 未満）
const TCFX = (() => {
  const W = 390, H = 614, TAU = Math.PI * 2;
  const AP = p => (typeof window.TC_ASSET === 'function' ? window.TC_ASSET(p) : p);
  const SANS = '"Hiragino Sans", "BIZ UDPGothic", "Noto Sans CJK JP", sans-serif', SERIF = '"Hiragino Mincho ProN", "Noto Serif CJK JP", serif';
  const clamp = (x, a, b) => Math.max(a, Math.min(b, x)), sm = x => { x = clamp(x, 0, 1); return x * x * (3 - 2 * x); };
  const smoother = x => { x = clamp(x, 0, 1); return x * x * x * (x * (x * 6 - 15) + 10); };
  const backOut = x => { x = clamp(x, 0, 1); const c = 1.6; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
  const easeOut = x => 1 - Math.pow(1 - clamp(x, 0, 1), 3);
  const mod = (x, m) => ((x % m) + m) % m;
  function hash(n) { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); }
  const IMC = {};
  const img = s => IMC[s] || (IMC[s] = new Promise(ok => { const i = new Image(); i.onload = () => ok(i); i.onerror = () => ok(null); i.src = AP(s); }));
  let g = null, PX = 1;
  function poly(pts, fill) { g.beginPath(); g.moveTo(pts[0][0], pts[0][1]); for (let i = 1; i < pts.length; i++) g.lineTo(pts[i][0], pts[i][1]); g.closePath(); g.fillStyle = fill; g.fill(); }
  function line(x0, y0, x1, y1, col, lw) { g.strokeStyle = col; g.lineWidth = lw; g.beginPath(); g.moveTo(x0, y0); g.lineTo(x1, y1); g.stroke(); }
  function label(txt, x, y, size, fill, edge, ew, font) {
    g.font = `900 ${size}px ${font || SANS}`; g.textAlign = 'center'; g.textBaseline = 'middle';
    if (edge) { g.lineJoin = 'round'; g.lineWidth = ew; g.strokeStyle = edge; g.strokeText(txt, x, y); }
    g.fillStyle = fill; g.fillText(txt, x, y);
  }
  // 1コマずつ 描いて、おわったら とける（タップを 待つ）
  function play(cv, o, draw, sound) {
    return new Promise(done => {
      const q = cv.getContext('2d'); const st = { t0: performance.now(), tap: null, end: null, closeAt: null, last: 0 };
      const now = () => (performance.now() - st.t0) / 1000;
      const onTap = e => { if (e) { e.preventDefault(); e.stopPropagation(); } st.tapReq = true; };
      cv.classList.add('on'); cv.addEventListener('pointerdown', onTap);
      let raf = 0;
      const fr = () => {
        const u = now();
        if (st.tapReq) { st.tapReq = false; if (st.tap == null && u > (o.tapMin || 0.8)) st.tap = u; else if (st.end != null && u > st.end + 0.6 && st.closeAt == null) st.closeAt = u; }
        if (st.tap == null && u > 30) st.tap = u;                       // 30秒 たったら 自動
        if (st.end != null && st.closeAt == null && u > st.end + 3.0) st.closeAt = u;
        PX = cv.width / W; g = q; g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, cv.width, cv.height); g.setTransform(PX, 0, 0, PX, 0, 0);
        const fade = st.closeAt != null ? 1 - sm((u - st.closeAt) / 0.5) : 1;
        g.globalAlpha = fade; const r = draw(u, st); g.globalAlpha = 1;
        if (sound) sound(u, st, st.last);
        st.last = u;
        if (r && r.end != null && st.end == null) st.end = r.end;
        if (st.closeAt != null && u > st.closeAt + 0.52) { cv.removeEventListener('pointerdown', onTap); g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, cv.width, cv.height); cv.classList.remove('on'); done(); return; }
        raf = requestAnimationFrame(fr);
      };
      raf = requestAnimationFrame(fr);
    });
  }
  const se = (o, name, gain, lag) => { try { if (o.se) o.se(name, gain, lag); } catch (e) { /* なし */ } };
  const DIMR = { morning: 0.42, evening: 0.38, night: 0.26, abyss: 0.26, divine: 0.36 };      // うしろの フィールドを 少し 暗く

  // ================= ルーレット =================
  const RT_STYLE = {
    normal: { glow: [255, 196, 92], hglow: null, chev: ['#e0434a', '#bf2f36', '#fff1d6'], n: 1, star: ['#f6d36e', '#d9a43c'], gem: '#d8333a', tap: ['#d23b30', '#b52f27', '#f0c25a'], card: ['#22603a', '#1a4f2f', '#f0c25a', '#c8922f'], conf: ['#f3c55a', '#d8333a', '#2f7a46', '#fff1c9'], line: 'rgba(255,248,230,0.55)' },
    maboroshi: { glow: [176, 98, 245], hglow: [440, 380], chev: ['#f3ecfa', '#cdb8e2', '#9a4fc8'], n: 2, star: ['#f2f0f6', '#a9a3b8'], gem: null, tap: ['#9a33bf', '#7f2a9f', '#e6e1ee'], card: ['#8e2db2', '#74229a', '#ebe7f2', '#a9a3b8'], conf: ['#d9b3f0', '#a63cc9', '#f0edf6', '#7f2a9f'], line: 'rgba(255,250,255,0.6)' },
    kamisama: { glow: [255, 212, 118], hglow: [440, 380], chev: ['#ffd85e', '#e3a83a', '#fff4cf'], n: 2, star: ['#f8d672', '#d4a03a'], gem: null, tap: ['#cd3030', '#ad2626', '#f3c95e'], card: ['#c93030', '#a82626', '#f3c95e', '#c8922f'], conf: ['#f6d06a', '#cd3030', '#fff3cf', '#e6a93a'], line: 'rgba(255,248,230,0.55)' },
  };
  const K = H / 1536, OX = (W - 1024 * K) / 2;            // 台紙（1024×1536）を 画面に：高さに 合わせる
  let GEO = null;
  async function rtLoad(th) {
    if (!GEO) { try { GEO = await fetch(AP('tc_rt_geom.json')).then(r => r.json()); } catch (e) { GEO = null; } }
    const I = {}; await Promise.all(['plate', 'knob', 'stick', 'ptr'].map(async p => { I[p] = await img(`rt_${th}_${p}.webp`); }));
    return I;
  }
  function rtAngle(r, u) {
    const off = (hash(r.a + r.b + r.win) - 0.5) * 0.9, fin = r.win * Math.PI + off;
    if (r.S0 == null || u < r.S0) return 0;
    const p = clamp((u - r.S0) / (r.S1 - r.S0), 0, 1), e = 1 - Math.pow(1 - p, 2.5);
    const turns = 2 + mod(fin, TAU) / TAU; return fin - turns * TAU * (1 - e);
  }
  function leverK(r, u) {
    let down = 0; const HIT = r.HIT;
    if (HIT != null && u >= HIT && u < HIT + 0.09) down = sm((u - HIT) / 0.09);
    else if (HIT != null && u >= HIT + 0.09) { const v = u - HIT - 0.09; down = Math.max(-0.3, Math.exp(-v * 7) * Math.cos(v * 14)); }
    const th = 1.1 * down; return { c: Math.cos(th), s: Math.sin(th) };
  }
  function drawSprite(im, P, sx, sy, ax, ay) { if (!im) return; g.save(); g.translate(ax, ay); g.scale(sx, sy); g.drawImage(im, P.x - ax, P.y - ay, P.w, P.h); g.restore(); }
  function drawLever(r, I, Gm, u) {
    const L = leverK(r, u), [px, py] = Gm.pivot, [kx, ky] = Gm.knob;
    drawSprite(I.stick, Gm.parts.stick, 1 + 0.1 * L.s, Math.max(0.35, L.c), px, py);
    const nx = px + (kx - px) * L.c, ny = py + (ky - py) * L.c, ks = 1 + 0.16 * L.s;
    if (!I.knob) return;
    const P = Gm.parts.knob; g.save(); g.translate(nx, ny); g.scale(ks, ks); g.drawImage(I.knob, P.x - kx, P.y - ky, P.w, P.h); g.restore();
    if (r.HIT != null && u > r.HIT && u < r.HIT + 0.3) {
      const q = (u - r.HIT) / 0.3, R = Gm.knob[2] * ks; g.save(); g.globalAlpha *= 1 - q; g.lineCap = 'round';
      for (let i = 0; i < 8; i++) { const a = -Math.PI / 2 + i * Math.PI / 4, r0 = R + 18 + 22 * q; line(nx + Math.cos(a) * r0, ny + Math.sin(a) * r0, nx + Math.cos(a) * (r0 + 26), ny + Math.sin(a) * (r0 + 26), '#fff3c4', 7); }
      g.restore();
    }
  }
  function drawFace(r, Gm, ang, glowK) {
    const st = RT_STYLE[r.th], [cx, cy] = Gm.c, R = Gm.r;
    g.save(); g.translate(cx, cy);
    g.save(); g.beginPath(); g.arc(0, 0, R + 2, 0, TAU); g.clip();
    g.save(); g.rotate(ang);
    const N = 18;
    for (let i = 0; i < 2; i++) {
      const a0 = -Math.PI + i * Math.PI, cols = Gm.face[i];
      for (let j = 0; j < N; j++) { const s0 = a0 + j * Math.PI / N, s1 = s0 + Math.PI / N; g.fillStyle = cols[j % 2]; g.beginPath(); g.moveTo(0, 0); g.arc(0, 0, R + 4, s0 - 0.002, s1 + 0.002); g.closePath(); g.fill(); }
      for (let j = 1; j < N; j++) { const s = a0 + j * Math.PI / N; line(0, 0, Math.cos(s) * (R + 4), Math.sin(s) * (R + 4), j % 2 ? 'rgba(255,255,255,0.18)' : 'rgba(0,0,0,0.07)', 1.4); }
      if (i === r.win && glowK > 0) { g.save(); g.globalAlpha *= 0.32 * glowK; g.fillStyle = '#fffbe8'; g.beginPath(); g.moveTo(0, 0); g.arc(0, 0, R + 4, a0, a0 + Math.PI); g.closePath(); g.fill(); g.restore(); }
    }
    line(-R - 4, 0, R + 4, 0, st.line, 5); line(-R - 4, 2.5, R + 4, 2.5, 'rgba(0,0,0,0.12)', 2);
    g.restore();
    const sh = g.createRadialGradient(0, 0, R * 0.25, 0, 0, R + 2);
    sh.addColorStop(0, 'rgba(255,250,235,0.07)'); sh.addColorStop(0.72, 'rgba(0,0,0,0)'); sh.addColorStop(1, 'rgba(40,15,0,0.26)');
    g.fillStyle = sh; g.fillRect(-R - 4, -R - 4, 2 * R + 8, 2 * R + 8);
    g.restore();
    for (let i = 0; i < 2; i++) {                 // 数字：盤と いっしょに まわる 場所・字は いつも 上向き（大きい 数は 小さく：盤から はみ出さない）
      const phi = -Math.PI / 2 + i * Math.PI + ang, v = Math.abs(Math.sin(phi));
      const d = R * (0.57 + 0.07 * (1 - v)); let fs = R * 0.37 * (0.68 + 0.32 * v);
      const x = Math.cos(phi) * d, y = Math.sin(phi) * d, txt = (i ? r.b : r.a) + 'P';
      g.font = `900 ${fs}px ${SERIF}`; const tw = g.measureText(txt).width, mw = R * 1.36; if (tw > mw) fs *= mw / tw;
      g.save(); g.shadowColor = 'rgba(0,0,0,0.35)'; g.shadowOffsetY = 5 * K * PX; g.shadowBlur = 6 * K * PX;
      label(txt, x, y, fs, '#fff4dc', Gm.edge, fs * 0.22, SERIF); g.restore();
      label(txt, x, y, fs, '#fff6e4', Gm.edge, fs * 0.15, SERIF);
    }
    g.save(); g.rotate(ang);                       // まん中の 星
    const Ro = R * 0.27, Ri = R * 0.1;
    for (let i = 0; i < 8; i++) {
      const a = -Math.PI / 2 + i * Math.PI / 4, al = a - Math.PI / 8, ar = a + Math.PI / 8;
      const T = [Math.cos(a) * Ro, Math.sin(a) * Ro], Lp = [Math.cos(al) * Ri, Math.sin(al) * Ri], Rp = [Math.cos(ar) * Ri, Math.sin(ar) * Ri];
      poly([[0, 0], Lp, T], st.star[0]); poly([[0, 0], T, Rp], st.star[1]);
    }
    for (let i = 0; i < 8; i++) {
      const a = -Math.PI / 2 + Math.PI / 8 + i * Math.PI / 4, al = a - Math.PI / 8, ar = a + Math.PI / 8, r2 = Ro * 0.55;
      poly([[0, 0], [Math.cos(al) * Ri, Math.sin(al) * Ri], [Math.cos(a) * r2, Math.sin(a) * r2]], st.star[1]); poly([[0, 0], [Math.cos(a) * r2, Math.sin(a) * r2], [Math.cos(ar) * Ri, Math.sin(ar) * Ri]], st.star[0]);
    }
    if (st.gem) { const q = Ri * 0.85; poly([[0, -q], [q * 0.8, 0], [0, q], [-q * 0.8, 0]], st.gem); poly([[0, -q], [q * 0.8, 0], [0, 0]], 'rgba(255,255,255,0.28)'); }
    g.restore();
    g.restore();
  }
  function drawGlow(r, Gm, u) {
    const st = RT_STYLE[r.th], [cx, cy] = Gm.c, R = Gm.r * 1.22, [cr, cg, cb] = st.glow;
    const rg = g.createRadialGradient(cx, cy, R * 0.3, cx, cy, R * 1.55);
    rg.addColorStop(0, `rgba(${cr},${cg},${cb},0.42)`); rg.addColorStop(0.5, `rgba(${cr},${cg},${cb},0.2)`); rg.addColorStop(1, `rgba(${cr},${cg},${cb},0)`);
    g.fillStyle = rg; g.fillRect(cx - R * 1.6, cy - R * 1.6, R * 3.2, R * 3.2);
    g.save(); g.translate(cx, cy); g.rotate(0.04 * u);
    for (let i = 0; i < 16; i++) {
      const a = i * TAU / 16, w = 0.07, lg = g.createRadialGradient(0, 0, R * 0.8, 0, 0, R * 1.7);
      lg.addColorStop(0, `rgba(${cr},${cg},${cb},0.10)`); lg.addColorStop(1, `rgba(${cr},${cg},${cb},0)`);
      g.fillStyle = lg; g.beginPath(); g.moveTo(0, 0); g.arc(0, 0, R * 1.7, a - w, a + w); g.closePath(); g.fill();
    }
    g.restore();
    if (st.hglow) {
      const [hx, hy] = st.hglow, hr = 400, hg = g.createRadialGradient(hx, hy, 40, hx, hy, hr);
      hg.addColorStop(0, `rgba(${cr},${cg},${cb},0.38)`); hg.addColorStop(1, `rgba(${cr},${cg},${cb},0)`);
      g.fillStyle = hg; g.fillRect(hx - hr, hy - hr, hr * 2, hr * 2);
    }
  }
  function drawChev(r, Gm, u) {
    const k = sm(u / 0.5) * (r.HIT != null ? 1 - sm((u - r.HIT) / 0.2) : 1); if (k <= 0) return;
    const st = RT_STYLE[r.th], [cx, cy] = Gm.chev, bob = 7 * Math.sin((u - 0.5) * TAU * 1.0);
    g.save(); g.globalAlpha *= k;
    for (let i = 0; i < st.n; i++) {
      const y = cy + bob + (st.n === 2 ? (i - 0.5) * 36 : 0), q = st.n === 2 ? 0.95 : 1.25;
      const V = [[-32, -16], [0, 12], [32, -16], [20, -28], [0, -10], [-20, -28]].map(([x, yy]) => [cx + x * q, y + yy * q]);
      g.save(); g.shadowColor = 'rgba(0,0,0,0.3)'; g.shadowBlur = 6 * K * PX; g.shadowOffsetY = 3 * K * PX;
      g.beginPath(); V.forEach((p, j) => j ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1])); g.closePath(); g.fillStyle = st.chev[2]; g.fill(); g.restore();
      const S = [[-32, -16], [0, 12], [32, -16], [20, -28], [0, -10], [-20, -28]].map(([x, yy]) => [cx + x * q * 0.78, y + 2 + yy * q * 0.78]);
      poly([S[0], S[1], S[4], S[5]], st.chev[0]); poly([S[1], S[2], S[3], S[4]], st.chev[1]);
    }
    g.restore();
  }
  function drawTap(r, Gm, u) {
    const k = sm((u - 1.0) / 0.3) * (r.HIT != null ? 1 - sm((u - r.HIT) / 0.15) : 1); if (k <= 0) return;
    const st = RT_STYLE[r.th], cx = Math.min(Gm.chev[0], 856), cy = Gm.chev[1], y = cy - (r.th === 'normal' ? 84 : 108) + 4 * Math.sin((u - 1.0) * 2 * Math.PI * 0.9);
    g.save(); g.globalAlpha *= k; g.translate(cx, y); const s = 1 + 0.03 * Math.sin((u - 1.0) * 5); g.scale(s, s);
    const w = 250, h = 100, c = 22;
    poly([[-w / 2 + 8, -h / 2 + 12], [w / 2 + 8, -h / 2 + 12], [w / 2 + 8, h / 2 + 12], [-w / 2 + 8, h / 2 + 12]], 'rgba(0,0,0,0.25)');
    poly([[-w / 2, -h / 2], [w / 2, -h / 2], [w / 2, h / 2], [-w / 2, h / 2]], st.tap[2]);
    poly([[-w / 2 + 7, -h / 2 + 7], [w / 2 - 7, -h / 2 + 7], [w / 2 - 7, 0], [-w / 2 + 7, 0]], st.tap[0]);
    poly([[-w / 2 + 7, 0], [w / 2 - 7, 0], [w / 2 - 7, h / 2 - 7], [-w / 2 + 7, h / 2 - 7]], st.tap[1]);
    poly([[w / 2 - c - 7, -h / 2 + 7], [w / 2 - 7, -h / 2 + 7], [w / 2 - 7, -h / 2 + 7 + c]], 'rgba(255,255,255,0.3)');
    label('タップ', 0, 3, 66, '#fff6e2', '#3a160c', 15);
    g.restore();
  }
  function drawGet(r, Gm, val, k) {
    if (k <= 0) return;
    const st = RT_STYLE[r.th], [x0, y0, x1, y1] = Gm.bottom, cx = (x0 + x1) / 2, cy = (y0 + y1) / 2, w = x1 - x0, h = y1 - y0, s = backOut(k);
    g.save(); g.globalAlpha *= sm(k * 2); g.translate(cx, cy); g.scale(s, s);
    const e = 70, hh = h * 0.42;
    for (const sg of [-1, 1]) {
      const xa = sg * (w / 2 - e), xb = sg * (w / 2);
      poly([[xa, -hh + 18], [xb, -hh + 18], [xb - sg * 26, 18], [xb, hh + 18], [xa, hh + 18]], st.card[3]);
      poly([[sg * (w / 2 - e), hh], [sg * (w / 2 - e - 24), hh + 18], [sg * (w / 2 - e), hh + 18]], 'rgba(0,0,0,0.35)');
    }
    const pw = w - 2 * e + 10;
    poly([[-pw / 2 + 10, -hh + 12], [pw / 2 + 10, -hh + 12], [pw / 2 + 10, hh + 12], [-pw / 2 + 10, hh + 12]], 'rgba(0,0,0,0.25)');
    poly([[-pw / 2, -hh], [pw / 2, -hh], [pw / 2, hh], [-pw / 2, hh]], st.card[2]);
    poly([[-pw / 2 + 8, -hh + 8], [pw / 2 - 8, -hh + 8], [pw / 2 - 8, 0], [-pw / 2 + 8, 0]], st.card[0]);
    poly([[-pw / 2 + 8, 0], [pw / 2 - 8, 0], [pw / 2 - 8, hh - 8], [-pw / 2 + 8, hh - 8]], st.card[1]);
    g.font = `900 86px ${SERIF}`; const w1 = g.measureText(val + 'P').width; g.font = `900 58px ${SANS}`; const w2 = g.measureText('GET！！！').width;
    const gap = 16, tot = w1 + gap + w2, sc = Math.min(1, (pw - 50) / tot), xa = -tot / 2;
    g.scale(sc, sc);
    label(val + 'P', xa + w1 / 2, 4, 86, '#ffd65c', '#3a1a08', 15, SERIF);
    label('GET！！！', xa + w1 + gap + w2 / 2, 8, 58, '#fff6e2', '#3a1a08', 12);
    g.restore();
  }
  function confetti(cols, t, k, w, h) {
    if (k <= 0) return;
    for (let i = 0; i < 46; i++) {
      const x0 = hash(i) * (w + 76) - 40, sp = 110 + 130 * hash(i + 7), y = -60 + (t * sp + hash(i + 3) * 420) % (h + 104), sw = 36 * Math.sin(t * (1 + hash(i + 5)) + i);
      g.save(); g.globalAlpha *= 0.9 * k; g.translate(x0 + sw, y); g.rotate(t * (1 + 2 * hash(i + 9)) + i);
      poly([[0, -15], [9, 0], [0, 15], [-9, 0]], cols[i % cols.length]); poly([[0, -15], [9, 0], [0, 0]], 'rgba(255,255,255,0.25)');
      g.restore();
    }
  }
  async function roulette(cv, o) {
    const th = RT_STYLE[o.th] ? o.th : 'normal', I = await rtLoad(th);
    if (!GEO || !GEO[th]) return;
    const Gm = GEO[th], r = { th, a: o.a, b: o.b, win: o.win ? 1 : 0, HIT: null, S0: null, S1: null }, dim = DIMR[o.bg] != null ? DIMR[o.bg] : 0.4;
    let tickIdx = null;
    se(o, 'tc_se_unfold.m4a', 1, 0);
    await play(cv, o, (u, st) => {
      if (st.tap != null && r.HIT == null) { r.HIT = st.tap; r.S0 = r.HIT + 0.05; r.S1 = r.S0 + 3.5; }
      const app = sm(u / 0.45);
      g.save(); g.globalAlpha *= app; g.fillStyle = `rgba(16,10,6,${dim})`; g.fillRect(0, 0, W, H); g.restore();
      g.save(); g.globalAlpha *= app;
      const z = 1 + 0.03 * (1 - sm(u / 0.6)); g.translate(W / 2, H / 2); g.scale(z, z); g.translate(-W / 2, -H / 2);
      g.translate(OX, 0); g.scale(K, K);
      drawGlow(r, Gm, u);
      if (I.plate) g.drawImage(I.plate, 0, 0, 1024, 1536);
      const ang = rtAngle(r, u);
      drawFace(r, Gm, ang, r.S1 != null ? sm((u - r.S1 - 0.1) / 0.4) : 0);
      const P = Gm.parts.ptr; if (I.ptr) g.drawImage(I.ptr, P.x, P.y, P.w, P.h);
      drawLever(r, I, Gm, u); drawChev(r, Gm, u); drawTap(r, Gm, u);
      if (r.S1 != null && u > r.S1 + 0.4) {
        const v = u - r.S1 - 0.4; g.save(); g.setTransform(PX, 0, 0, PX, 0, 0); g.globalAlpha = app * (st.closeAt != null ? 1 - sm((u - st.closeAt) / 0.5) : 1); confetti(RT_STYLE[th].conf, v, sm(v / 0.4), W, H); g.restore();
        drawGet(r, Gm, r.win ? r.b : r.a, v / 0.45);
      }
      g.restore();
      return { end: r.S1 != null ? r.S1 + 1.2 : null };
    }, (u, st, last) => {
      if (r.HIT != null && last < r.HIT && u >= r.HIT) se(o, 'tc_se_rt_lever.m4a', 1, 0);
      if (r.S0 != null && u >= r.S0 && u <= r.S1 + 0.05) {          // カチッ：盤の ひだの さかいが 針を 通る たびに（コマの 間の 分も 時間を ずらして）
        const steps = 6, a0 = Math.max(r.S0, last);
        for (let k = 1; k <= steps; k++) {
          const uu = a0 + (u - a0) * k / steps, idx = Math.floor((rtAngle(r, uu) + Math.PI / 2) / (Math.PI / 8));
          if (tickIdx != null && idx !== tickIdx) se(o, 'tc_se_rt_tick.m4a', 0.9, Math.max(0, uu - u + 1 / 30));
          tickIdx = idx;
        }
      }
      if (r.S1 != null && last < r.S1 + 0.02 && u >= r.S1 + 0.02) se(o, 'tc_se_rt_stop.m4a', 1, 0);
      if (r.S1 != null && last < r.S1 + 0.4 && u >= r.S1 + 0.4) se(o, 'tc_se_rt_confirm.m4a', 1, 0);
    });
  }

  // ================= 壁紙チケット =================
  const IW = 1086, IH = 1448, TKK = Math.max(W / IW, H / IH), TOX = (W - IW * TKK) / 2, TOY = (H - IH * TKK) / 2;
  const FALL0 = 0.35, FALL = 0.26, LAND = FALL0 + FALL, TAPSHOW = LAND + 0.7, OPEN = 1.25, HOLD = 0.35, REVEAL = 0.95;
  const TKPOS = { 1: [[0, 0, 0, 1.0]], 2: [[-168, -0.1, 14, 0.78], [168, 0.1, 14, 0.78]], 3: [[-248, -0.2, 50, 0.66], [0, 0, 0, 0.7], [248, 0.2, 50, 0.66]] };
  function goldLight(u, k, beamW, open) {
    if (k <= 0) return;
    const cx = IW / 2, cy = 700, br = (0.86 + 0.14 * Math.sin(TAU * u / 2.4)) * k;
    g.save(); g.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 14; i++) {
      const a = i / 14 * TAU + u * 0.05, w = 0.06 + 0.04 * hash(i), L = 1300, gr = g.createRadialGradient(cx, cy, 40, cx, cy, L);
      gr.addColorStop(0, `rgba(255,220,120,${0.16 * br})`); gr.addColorStop(1, 'rgba(255,200,90,0)');
      g.fillStyle = gr; g.beginPath(); g.moveTo(cx, cy); g.arc(cx, cy, L, a - w, a + w); g.closePath(); g.fill();
    }
    const bw = beamW, gb = g.createLinearGradient(cx - bw * 2.2, 0, cx + bw * 2.2, 0);
    gb.addColorStop(0, 'rgba(255,190,80,0)'); gb.addColorStop(0.32, `rgba(255,210,110,${0.28 * br})`); gb.addColorStop(0.5, `rgba(255,250,225,${0.75 * br})`); gb.addColorStop(0.68, `rgba(255,210,110,${0.28 * br})`); gb.addColorStop(1, 'rgba(255,190,80,0)');
    g.fillStyle = gb; g.fillRect(cx - bw * 2.2, 180 - open * 300, bw * 4.4, 1100 + open * 600);
    const gc = g.createRadialGradient(cx, cy, 10, cx, cy, 420 + 600 * open);
    gc.addColorStop(0, `rgba(255,248,215,${0.55 * br})`); gc.addColorStop(0.4, `rgba(255,214,120,${0.22 * br})`); gc.addColorStop(1, 'rgba(255,190,80,0)');
    g.fillStyle = gc; g.fillRect(0, 0, IW, IH);
    for (let i = 0; i < 34; i++) {
      const sp = 40 + 60 * hash(i + 3), x = 120 + hash(i) * 846 + 30 * Math.sin(u * 0.7 + i), y = IH + 40 - ((u * sp + hash(i + 9) * IH) % (IH + 80));
      const tw = 0.55 + 0.45 * Math.sin(u * (0.8 + hash(i + 5)) + i), rr = 3 + 4 * hash(i + 7), gp = g.createRadialGradient(x, y, 0, x, y, rr * 4);
      gp.addColorStop(0, `rgba(255,240,190,${0.85 * tw * k})`); gp.addColorStop(1, 'rgba(255,200,90,0)');
      g.fillStyle = gp; g.beginPath(); g.arc(x, y, rr * 4, 0, TAU); g.fill();
    }
    g.restore();
  }
  function dust(v) {
    if (v < 0 || v > 2.2) return;
    g.save();
    for (let i = 0; i < 44; i++) {
      const s = i % 2 ? 1 : -1, base = i < 26 ? 1185 : IH - 10;
      const x0 = IW / 2 + s * (20 + hash(i) * (i < 26 ? 470 : 560)), vx = s * (90 + 280 * hash(i + 4)), up = 80 + 220 * hash(i + 8);
      const e = 1 - Math.pow(1 - Math.min(1, v / 1.8), 3.0), x = x0 + vx * e, y = base - up * e - 18 * hash(i + 6);
      const rr = (55 + 90 * hash(i + 2)) * (0.4 + 1.1 * e), a = 0.78 * Math.min(1, v / 0.06) * (1 - sm((v - 0.5) / 1.6));
      const c = i % 3 === 0 ? '168,132,88' : i % 3 === 1 ? '140,104,64' : '196,166,122';
      const gp = g.createRadialGradient(x, y, 0, x, y, rr); gp.addColorStop(0, `rgba(${c},${a})`); gp.addColorStop(0.55, `rgba(${c},${a * 0.55})`); gp.addColorStop(1, `rgba(${c},0)`);
      g.fillStyle = gp; g.beginPath(); g.arc(x, y, rr, 0, TAU); g.fill();
    }
    for (let i = 0; i < 18; i++) {
      const s = i % 2 ? 1 : -1, x = IW / 2 + s * (80 + hash(i + 30) * 420) + s * (120 + 200 * hash(i + 31)) * Math.min(1, v / 0.9), y = 1190 - (260 * hash(i + 32)) * Math.min(1, v / 0.9) + 520 * Math.pow(Math.min(1, v / 0.9), 2);
      const a = 1 - sm((v - 0.6) / 0.4); if (a <= 0) continue;
      g.save(); g.globalAlpha *= a * 0.85; g.translate(x, y); g.rotate(v * 6 + i); poly([[-7, -5], [6, -6], [8, 4], [-5, 6]], i % 2 ? '#8a6a44' : '#b08a5c'); g.restore();
    }
    g.restore();
  }
  function tkTap(u, k) {
    if (k <= 0) return;
    g.save(); g.globalAlpha *= k; g.translate(IW / 2, 1268 + 8 * Math.sin(u * TAU * 0.9)); const s = (1 + 0.03 * Math.sin(u * 5)) * (0.7 + 0.3 * backOut(k)); g.scale(s, s);
    const w = 340, h = 132, c = 28;
    poly([[-w / 2 + 9, -h / 2 + 14], [w / 2 + 9, -h / 2 + 14], [w / 2 + 9, h / 2 + 14], [-w / 2 + 9, h / 2 + 14]], 'rgba(0,0,0,0.3)');
    poly([[-w / 2, -h / 2], [w / 2, -h / 2], [w / 2, h / 2], [-w / 2, h / 2]], '#7a4a12');
    poly([[-w / 2 + 8, -h / 2 + 8], [w / 2 - 8, -h / 2 + 8], [w / 2 - 8, 0], [-w / 2 + 8, 0]], '#e9b13a');
    poly([[-w / 2 + 8, 0], [w / 2 - 8, 0], [w / 2 - 8, h / 2 - 8], [-w / 2 + 8, h / 2 - 8]], '#d1952a');
    poly([[w / 2 - c - 8, -h / 2 + 8], [w / 2 - 8, -h / 2 + 8], [w / 2 - 8, -h / 2 + 8 + c]], 'rgba(255,255,255,0.3)');
    label('タップ', 0, 4, 88, '#fff6e2', '#3a1a08', 17);
    g.restore();
  }
  let TBACK = null;
  function ticketArt(im, x, y, s, rot, sx, a) {
    if (a <= 0 || s <= 0.01 || !im) return;
    const w = 430, h = w * im.naturalHeight / im.naturalWidth;
    g.save(); g.globalAlpha *= a; g.translate(x, y); g.rotate(rot); g.scale(s * Math.abs(sx), s);
    if (sx >= 0) { g.save(); g.shadowColor = 'rgba(40,20,0,0.35)'; g.shadowBlur = 12 * TKK * s * PX; g.shadowOffsetX = 10 * TKK * s * PX; g.shadowOffsetY = 16 * TKK * s * PX; g.drawImage(im, -w / 2, -h / 2, w, h); g.restore(); }
    else {
      if (!TBACK) { TBACK = document.createElement('canvas'); TBACK.width = im.naturalWidth; TBACK.height = im.naturalHeight; const q = TBACK.getContext('2d'); q.drawImage(im, 0, 0); q.globalCompositeOperation = 'source-atop'; q.fillStyle = 'rgba(214,150,40,0.92)'; q.fillRect(0, 0, TBACK.width, TBACK.height); }
      g.drawImage(TBACK, -w / 2, -h / 2, w, h);
    }
    g.restore();
  }
  function getTag(n, v) {
    if (v <= 0) return;
    const s = backOut(v / 0.3), rot = -0.05 * Math.exp(-v * 6) * Math.cos(v * 18);
    g.save(); g.globalAlpha *= sm(v / 0.12); g.translate(IW / 2, 1110); g.rotate(rot); g.scale(s, s);
    const w = 760, h = 230, c = 46;
    poly([[-w / 2 + 14, -h / 2 + 20], [w / 2 + 14, -h / 2 + 20], [w / 2 + 14, h / 2 + 20], [-w / 2 + 14, h / 2 + 20]], 'rgba(0,0,0,0.25)');
    poly([[-w / 2, -h / 2], [w / 2 - c, -h / 2], [w / 2, -h / 2 + c], [w / 2, h / 2], [-w / 2, h / 2]], '#fff4d6');
    poly([[-w / 2, 0], [w / 2, 0], [w / 2, h / 2], [-w / 2, h / 2]], '#f7e6bf');
    poly([[w / 2 - c, -h / 2], [w / 2, -h / 2 + c], [w / 2 - c, -h / 2 + c]], '#e2c78e');
    g.strokeStyle = 'rgba(160,110,50,0.3)'; g.lineWidth = 3; g.beginPath(); g.moveTo(-w / 2, 0); g.lineTo(w / 2, 0); g.stroke();
    label(`チケット ×${n}`, 0, -40, 84, '#f3b631', '#5b3412', 16);
    label('GET！', 0, 56, 70, '#fffaf0', '#5b3412', 14);
    g.restore();
  }
  function sparkle(x, y, r, a) {
    if (a <= 0 || r <= 0) return;
    g.save(); g.globalCompositeOperation = 'lighter'; g.globalAlpha *= a; g.translate(x, y);
    const k = 0.22; poly([[0, -r], [r * k, -r * k], [r, 0], [r * k, r * k], [0, r], [-r * k, r * k], [-r, 0], [-r * k, -r * k]], 'rgba(255,240,190,0.9)');
    g.restore();
  }
  async function ticket(cv, o) {
    const [closed, open_, tk] = await Promise.all([img('tk_door_closed.webp'), img('tk_door_open.webp'), img('tk_ticket.webp')]);
    const n = Math.max(1, Math.min(3, o.n | 0)), pos = TKPOS[n], dim = (DIMR[o.bg] != null ? DIMR[o.bg] : 0.4) + 0.08;
    const T = { tap: null, get0: null };
    await play(cv, Object.assign({ tapMin: TAPSHOW }, o), (u, st) => {
      if (st.tap != null && T.tap == null) T.tap = Math.max(st.tap, TAPSHOW);
      const uo = T.tap != null ? u - T.tap : -1, get0 = T.tap != null ? T.tap + OPEN + HOLD + 0.55 : null;
      g.fillStyle = `rgba(18,10,4,${dim * sm(u / 0.45)})`; g.fillRect(0, 0, W, H);
      const p = clamp((u - FALL0) / FALL, 0, 1), q = (u - LAND) / 0.3;
      const yOff = u < LAND ? -H * (1 - p * p) : -10 * Math.sin(Math.PI * clamp(q, 0, 1)) * (1 - clamp(q, 0, 1));
      const zoom = uo > 0 ? (uo < OPEN + HOLD ? 1 + 0.08 * smoother(uo / (OPEN + HOLD)) : 1 + 0.08 * (1 - smoother((uo - OPEN - HOLD) / REVEAL))) : 1;
      const opened = uo >= OPEN + HOLD * 0.5;
      if (u >= FALL0) {
        g.save(); g.translate(W / 2, H / 2 + yOff); g.scale(zoom, zoom); g.translate(-W / 2, -H / 2);
        const im = opened ? open_ : closed; if (im) g.drawImage(im, TOX, TOY, IW * TKK, IH * TKK);
        g.save(); g.translate(TOX, TOY); g.scale(TKK, TKK);
        const lk = opened ? 0.75 + 0.25 * sm((uo - OPEN - HOLD - REVEAL * 0.3) / 0.8) : sm((u - LAND - 0.1) / 0.6);
        const ow = uo > 0 && !opened ? smoother(uo / OPEN) : 0;
        goldLight(u, lk, 34 + 520 * Math.pow(ow, 2.2), ow);
        if (u >= LAND) dust(u - LAND);
        g.restore(); g.restore();
      }
      g.save(); g.translate(TOX, TOY); g.scale(TKK, TKK);
      tkTap(u - TAPSHOW, sm((u - TAPSHOW) / 0.3) * (uo >= 0 ? 1 - sm(uo / 0.18) : 1));
      if (uo >= 0 && uo < 0.6) { g.save(); g.strokeStyle = `rgba(255,246,210,${0.8 * (1 - uo / 0.6)})`; g.lineWidth = 10; g.beginPath(); g.arc(IW / 2, 1268, 60 + 260 * easeOut(uo / 0.6), 0, TAU); g.stroke(); g.restore(); }
      g.restore();
      const wh = uo < 0 ? 0 : uo < OPEN ? Math.pow(smoother(uo / OPEN), 1.6) : uo < OPEN + HOLD ? 1 : 1 - smoother((uo - OPEN - HOLD) / REVEAL);
      if (wh > 0) { g.fillStyle = `rgba(255,251,236,${wh})`; g.fillRect(0, 0, W, H); }
      if (get0 != null) {
        const gu = u - get0;
        if (gu > -0.2) {
          g.save(); g.translate(TOX, TOY); g.scale(TKK, TKK);
          confettiTk(gu, sm(gu / 0.5));
          pos.forEach(([dx, rot, dy, sc], i) => {
            const v = gu - i * 0.28; if (v < 0) return;
            const e = easeOut(v / 0.75), x = IW / 2 + dx * e, y = 760 - 60 * e + dy * e, s = (0.15 + 0.85 * backOut(v / 0.75)) * sc, sx = Math.cos(Math.max(0, 1 - v / 0.75) * Math.PI * 2);
            ticketArt(tk, x, y + 6 * Math.sin((v - 0.75) * 2.2), s, rot * e, sx, sm(v / 0.15));
            for (let j = 0; j < 4; j++) { const w2 = v - 0.75 - j * 0.45; if (w2 > 0 && w2 < 0.9) sparkle(x + (hash(i * 7 + j) - 0.5) * 300 * sc, y + (hash(i * 3 + j + 1) - 0.5) * 170 * sc, 22 * Math.sin(Math.PI * w2 / 0.9), 0.9); }
          });
          getTag(n, gu - 0.75 - 0.28 * (pos.length - 1));
          g.restore();
        }
      }
      return { end: get0 != null ? get0 + 0.75 + 0.28 * (pos.length - 1) + 0.6 : null };
    }, (u, st, last) => {
      const cross = x => last < x && u >= x;
      if (cross(FALL0)) se(o, 'tc_se_tk_fall.m4a', 1, 0);
      if (cross(LAND)) se(o, 'tc_se_tk_land.m4a', 1, 0);
      if (cross(TAPSHOW)) se(o, 'tc_se_tk_tapshow.m4a', 1, 0);
      if (T.tap != null) {
        const tt = T.tap, get0 = tt + OPEN + HOLD + 0.55;
        if (cross(tt)) { se(o, 'tc_se_tk_tap.m4a', 1, 0); se(o, 'tc_se_tk_open.m4a', 1, 0); }
        if (cross(tt + OPEN)) se(o, 'tc_se_tk_white.m4a', 1, 0);
        if (cross(tt + OPEN + HOLD)) se(o, 'tc_se_tk_reveal.m4a', 1, 0);
        pos.forEach((_, i) => { if (cross(get0 + i * 0.28)) se(o, 'tc_se_tk_ticket.m4a', 1, 0); });
        if (cross(get0 + 0.75 + 0.28 * (pos.length - 1))) se(o, 'tc_se_tk_get.m4a', 1, 0);
      }
    });
  }
  function confettiTk(t, k) {
    if (k <= 0) return; const cols = ['#ffd65c', '#fff2bf', '#f4a39b', '#f2c24f', '#ffe9a8'];
    for (let i = 0; i < 40; i++) {
      const x0 = hash(i) * (IW + 80) - 40, sp = 90 + 110 * hash(i + 7), y = -60 + (t * sp + hash(i + 3) * 420) % (IH + 120), sw = 30 * Math.sin(t * (1 + hash(i + 5)) + i);
      g.save(); g.globalAlpha *= 0.9 * k; g.translate(x0 + sw, y); g.rotate(t * (1 + 2 * hash(i + 9)) + i);
      poly([[0, -15], [9, 0], [0, 15], [-9, 0]], cols[i % cols.length]); poly([[0, -15], [9, 0], [0, 0]], 'rgba(255,255,255,0.25)');
      g.restore();
    }
  }
  function preload(th) { rtLoad(th || 'normal'); ['tk_door_closed.webp', 'tk_door_open.webp', 'tk_ticket.webp'].forEach(img); }
  return { roulette, ticket, preload };
})();
window.TCFX = TCFX;
