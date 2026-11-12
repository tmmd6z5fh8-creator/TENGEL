// トレーニングセンターの 当たりの 演出（App Store版）：ルーレット（ノーマル・幻の馬・神様馬の 3つの 絵）・壁紙チケット
//   h3d/roulette2.html・ticket.html と 同じ 絵と 動き（390×614 の 座標で 描いて キャンバスの 大きさに 合わせる）
//   ・うしろは いまの フィールド（下の キャンバスが そのまま 見える：少し 暗く）
//   ・「タップ」で レバーを たたく（ルーレット）・扉が 開く（チケット）：押すまで 待つ（30秒 たったら 自動）
//   ・GET の あとは タップか 3秒で とじる → Promise が とける
//   ・ちかちか しない（光は ゆっくり 1回・回る 速さは 2回／秒 未満）。プチュン（下）は 的中の 演出と 同じ 部品：明るく なって 暗く なるのは 1回 だけ
//   ・第4.159版（まさちゃん 2026/11/12 10:37・11:56「プチュンは、極ど的中と超プレミアム神様的中で使用してたプチュンの演出入れてね！プチュンしたらすぐに扉が落ちてくる演出にして！」）：
//     プチュン＝極ど的中の 押した 瞬間と 同じ 部品（白く 光る → 青い 画面 → 青白い 横一本の 線 → 点に ちぢんで 真っ暗。的中の 演出の 束 window.__FX の 中の <div class="pc">）を 舞台に 重ねる（pcOpen）。
//     チケット：PUSH を 押した 瞬間に プチュン → 真っ暗に なったら すぐ 扉が 落ちて くる（ticket の o.puchun）／
//     ルーレット：止まった あと「安い 方＝デカ的中と 同じ 音」「高い 方＝プチュン → 真っ暗に なったら すぐ ポイント」。音は 的中の 演出の もの（sfx_big.m4a・sfx_sdp.m4a：アプリの 同じ フォルダ）を 小さめに
//   ・第4.159版（まさちゃん 11/12 13:27「ルーレット高い方が当たった時に、プチュンしてまたルーレットの画面に戻ると変だから、光輝きながら獲得ポイントを表示するようにして！一枚目がテロップの画像！」
//     ・13:30「ドーン！！みたいな音と一緒にテロップ出して！」）：高い 方は プチュンの あと ルーレットに もどらない ＝ 暗い 舞台に 金の 光と テロップ「大量ポイント」（下の drawBig）・音は ドーン！！（tc_se_doon.m4a）
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

  // ================= プチュン（第4.159版）=================
  //   極ど的中（紫電）の 押した 瞬間の プチュンと 同じ 部品を そのまま 使う（まさちゃん 11/12 11:56）：kisekae/gen_fx.py の FZ_HTML ＝ <div class="pc">…（白く 光る 0〜0.2秒 → 水色の 帯 → 0.3秒 青い 画面と 白い 光・細い 電気
  //   → 0.45秒 青白い 横一本の 線 → 0.62秒 線が 点に ちぢむ → 0.8秒 真っ暗・光の 粒は 1.02秒 まで）。HTML は 的中の 演出の 束（window.__FX.reveal.sd）から とり出す・CSS は fx.js が 入れた もの（.fxs の 中 だけに 効く）。
  //   ・舞台（.tcst）の 上に 黒い 幕（.tcpc）を 重ねて、その 中に .fxs（390×844 を 舞台の 幅に 合わせて 拡大・まん中 合わせ ＝ 横一本の 線は 舞台の まん中）＞ .ov.fz ＞ .pc。上下の はみ出した 分は 切れる
  //   ・under＝true：演出の キャンバス（.tcfx）の 下に 置く（チケット：真っ暗の 上に 扉が 落ちて くる）／false：上に 置く（ルーレット：盤を かくす）
  //   ・「演出を控えめにする」・iPhone の「視差効果を減らす」（TengelFx.calm）：光る 部品は 出さない（黒い 幕 だけ・音も なし：的中の 演出と 同じ）。束が ない（見本の ページ）ときも 黒い 幕 だけ
  //   ・的中の 演出の 作りの まま：明るい 色の 帯どうしは 明るさを そろえて ある ＝ 明るく なって 暗く なるのは 1回 だけ（1秒に 3回の 点めつに ならない）
  const PCH = { dark: 0.82, len: 1.02, calm: 0.4 };      // 真っ暗に なる 時（線が 点に ちぢみ おわる 0.80秒の すぐ あと）・部品が 動く 長さ・控えめの ときの 黒い 幕の 長さ（秒）
  let PCN;                             // 部品の HTML（1回 だけ とり出す。ない ときは null）
  function pcHtml() {
    if (PCN !== undefined) return PCN;
    PCN = null;
    try { const A = window.__FX, h = A && A.reveal && A.reveal.sd, e = h && new DOMParser().parseFromString(h, 'text/html').querySelector('.pc'); if (e) PCN = e.outerHTML; } catch (er) { /* なし */ }
    return PCN;
  }
  const pcCalm = () => { try { return !!(window.TengelFx && window.TengelFx.calm && window.TengelFx.calm()); } catch (er) { return false; } };
  function pcOpen(cv, under) {         // 幕を 出す → { el, t0, calm, dark（真っ暗に なる までの 秒） }
    const st = cv.parentNode, calm = pcCalm(), h = calm ? null : pcHtml(), el = document.createElement('div');
    el.className = 'tcpc'; el.setAttribute('aria-hidden', 'true');
    el.style.cssText = 'position:absolute;left:0;top:0;width:100%;height:100%;overflow:hidden;background:#000;pointer-events:none';
    if (h) el.innerHTML = `<div class="fxs" style="--fxk:${((st.clientWidth || W) / W).toFixed(4)}"><div class="ov fz">${h}</div></div>`;
    st.insertBefore(el, under ? cv : cv.nextSibling);
    return { el, t0: performance.now(), calm: !h, dark: h ? PCH.dark : PCH.calm };
  }
  function pcClose(pc, fade) {         // 幕を 消す（fade 秒で うすく して から 外す・0 なら すぐ）
    if (!pc || !pc.el || pc.gone) return; pc.gone = true; const el = pc.el;
    if (!(fade > 0)) { el.remove(); return; }
    el.style.transition = `opacity ${fade}s linear`; el.style.opacity = '0'; setTimeout(() => el.remove(), fade * 1000 + 80);
  }
  const until = ms => new Promise(ok => { const f = () => (performance.now() >= ms ? ok() : requestAnimationFrame(f)); f(); });
  // プチュン だけ（ためす 用・ほかから 使う 用）：真っ暗に なったら とける。幕は keep 秒 のこして から 消える
  async function puchun(cv, o) {
    o = o || {}; const pc = pcOpen(cv, !!o.under); if (!pc.calm) se(o, 'sfx_sdp.m4a', PCH_GAIN, 0);
    await until(pc.t0 + pc.dark * 1000); setTimeout(() => pcClose(pc, 0.2), Math.max(0, (o.keep || 0) * 1000));
    return pc;
  }
  const PCH_GAIN = 0.85, BIG_GAIN = 0.5;      // 的中の 演出の 音は トレーニングセンターの 音より ずっと 大きい（プチュン −7dB・デカ的中 −2dB）→ ルーレットの 確定の 音（−7dB）に 合わせて 小さく

  // ================= ルーレット =================
  const RT_STYLE = {
    normal: { glow: [255, 196, 92], hglow: null, chev: ['#e0434a', '#bf2f36', '#fff1d6'], n: 1, star: ['#f6d36e', '#d9a43c'], gem: '#d8333a', tap: ['#d23b30', '#b52f27', '#f0c25a'], card: ['#22603a', '#1a4f2f', '#f0c25a', '#c8922f'], conf: ['#f3c55a', '#d8333a', '#2f7a46', '#fff1c9'], line: 'rgba(255,248,230,0.55)' },
    maboroshi: { glow: [176, 98, 245], hglow: [440, 380], eye: [651.4, 286, 190, 120, 255], chev: ['#f3ecfa', '#cdb8e2', '#9a4fc8'], n: 2, star: ['#f2f0f6', '#a9a3b8'], gem: null, tap: ['#9a33bf', '#7f2a9f', '#e6e1ee'], card: ['#8e2db2', '#74229a', '#ebe7f2', '#a9a3b8'], conf: ['#d9b3f0', '#a63cc9', '#f0edf6', '#7f2a9f'], line: 'rgba(255,250,255,0.6)' },
    kamisama: { glow: [255, 212, 118], hglow: [440, 380], eye: [641, 271.9, 255, 206, 96], chev: ['#ffd85e', '#e3a83a', '#fff4cf'], n: 2, star: ['#f8d672', '#d4a03a'], gem: null, tap: ['#cd3030', '#ad2626', '#f3c95e'], card: ['#c93030', '#a82626', '#f3c95e', '#c8922f'], conf: ['#f6d06a', '#cd3030', '#fff3cf', '#e6a93a'], line: 'rgba(255,248,230,0.55)' },
  };
  const K = H / 1536, OX = (W - 1024 * K) / 2;            // 台紙（1024×1536）を 画面に：高さに 合わせる
  let GEO = null;
  async function rtLoad(th) {
    if (!GEO) { try { GEO = await fetch(AP('tc_rt_geom.json')).then(r => r.json()); } catch (e) { GEO = null; } }
    // 第4.158版（まさちゃん 2026/11/12 08:59「画像がなんかまだらに色がついてるから綺麗にできる？」）：紙の もようの まだらを けした 絵（rt_<絵>_<部品>2.webp：kisekae/tc/rt_clean.py）
    //   新しい 絵が ない とき だけ 前の 絵（rt_<絵>_<部品>.webp）＝絵が 出ない ままに ならない
    const I = {}; await Promise.all(['plate', 'knob', 'stick', 'ptr'].map(async p => { I[p] = await img(`rt_${th}_${p}2.webp`) || await img(`rt_${th}_${p}.webp`); }));
    return I;
  }
  // 第4.158版（まさちゃん 08:59「このルーレットの神様馬、目が怖いから金色に光らせて！」・09:00「幻の馬のルーレットは、目を紫に光らせて！」）：
  //   目は 絵の 中で 光の 玉に して ある（rt_clean.py）。ここでは その 光が ゆっくり 息を する（2.4秒で 1回・小さな 光：ちかちか しない）
  function drawEye(r, u) {
    const e = RT_STYLE[r.th].eye; if (!e) return;
    const [ex, ey, cr, cg, cb] = e, k = 0.5 + 0.5 * Math.sin(TAU * u / 2.4 - 1.2), R = 38 + 10 * k;
    g.save(); g.globalCompositeOperation = 'lighter';
    const rg = g.createRadialGradient(ex, ey, 0, ex, ey, R);
    rg.addColorStop(0, `rgba(${cr},${cg},${cb},${0.3 + 0.3 * k})`); rg.addColorStop(0.4, `rgba(${cr},${cg},${cb},${0.12 + 0.14 * k})`); rg.addColorStop(1, `rgba(${cr},${cg},${cb},0)`);
    g.fillStyle = rg; g.fillRect(ex - R, ey - R, R * 2, R * 2);
    g.globalAlpha *= 0.35 + 0.45 * k; g.lineCap = 'round';
    for (const [dx, dy] of [[36 + 18 * k, 0], [0, 22 + 12 * k]]) {      // 十字の きらめき（のびちぢみ）
      const lg = g.createLinearGradient(ex - dx, ey - dy, ex + dx, ey + dy);
      lg.addColorStop(0, 'rgba(255,252,240,0)'); lg.addColorStop(0.5, 'rgba(255,252,240,0.9)'); lg.addColorStop(1, 'rgba(255,252,240,0)');
      g.strokeStyle = lg; g.lineWidth = 1.7; g.beginPath(); g.moveTo(ex - dx, ey - dy); g.lineTo(ex + dx, ey + dy); g.stroke();
    }
    g.restore();
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
  // ================= 大量ポイント（ルーレットの 高い 方・第4.159版）=================
  //   プチュンで 真っ暗に なったら、ルーレットには もどらないで、暗い 舞台に 金の 光（ゆっくり 回る 光の すじ・うしろの 光・紙ふぶき・きらめき）と いっしょに
  //   まさちゃんの テロップ「大量ポイント」（tc_telop_big.webp：kisekae/tc/telop_asset.py）が ドーン！！と 手前から 飛びこんで くる → 板の 中に ポイント → 下に「GET!!」
  //   ・光は ゆっくり：光の すじ 18本が 1秒に 0.14ラジアン（1周 45秒・同じ 所を すじが 通るのは 2.5秒に 1回）・うしろの 光は 2.6秒で 1回 息を する・
  //     テロップを なでる 光は 3.2秒に 1回（0.9秒 かけて 通る）・きらめきは 1.6〜2.5秒で 1回 ＝ちかちか しない。
  //     プチュン（明るく なって 暗く なる 1回）の あと 明るく なるのは この 1回 だけ（0.4秒 かけて）
  //   ・「演出を控えめにする」・iPhone の「視差効果を減らす」（calm）：飛びこまない（ふわっと 出る）・光は 回らない／息を しない・紙ふぶきと なでる 光と 光の 輪は なし
  //   ・絵が ない（手元に 素材が ない ビルド・見本）とき：コードで 描いた かんたんな 札（bigCard）
  //   TELOP：w＝画面での 幅（390 の 座標）・ar＝絵の たて÷よこ・panel＝板の 中で 字を 書いて よい 所（左・上・右・下：絵の 幅・高さに 対する 割合。telop_asset.py が 測る）・
  //     slam＝着く 時・z0＝はじめの 大きさ（倍）・fade＝テロップが はっきり する までの 長さ・rise＝うしろの 光が 明るく なる 長さ・num＝ポイントが 出る 時・get＝「GET!!」が 出る 時・hold＝とじられる ように なる まで（秒：ドーン！！から）・
  //     spin＝光の すじが 回る 速さ（ラジアン／秒）・sweep＝なでる 光［はじめ・くり返し・通る 長さ（秒）］
  //     fade と rise：テロップは 大きい うちは うすく（画面 いっぱいの 明るい 板が 一度 出て から 小さく なると、画面 ぜんぶの 明るさが 上がって 下がる ＝ 点めつに 近い）。
  //       着く ころに はっきり して、うしろの 光も いっしょに 上がる ＝ 画面 ぜんぶの 明るさは 上がる だけ（test_tc.py が 1/30秒ごとに 測る：下がるのは 0.02 まで）
  const TELOP = { src: 'tc_telop_big.webp', w: 372, ar: 742 / 1110, cx: W / 2, cy: 278, panel: [0.1532, 0.4555, 0.8405, 0.7925], slam: 0.24, z0: 1.9, fade: 0.24, rise: 0.4, num: 0.3, get: 0.55, hold: 1.2, spin: 0.14, sweep: [1.6, 3.2, 0.9] };
  const BIGCONF = ['#ffd65c', '#f6b73c', '#fff4cf', '#e8452e', '#ffe9a8'];
  const comma = n => String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  let TSH = null;                       // テロップを なでる 光の 下書き（絵の 形の 中 だけ 光らせる）
  function bigCard(w, h) {
    const [x0, y0, x1, y1] = TELOP.panel, l = -w / 2 + x0 * w - 8, r = -w / 2 + x1 * w + 8, t = -h / 2 + y0 * h - 7, b = -h / 2 + y1 * h + 7;
    poly([[l - 8, t - 8], [r + 8, t - 8], [r + 8, b + 8], [l - 8, b + 8]], '#c8262b'); poly([[l - 3, t - 3], [r + 3, t - 3], [r + 3, b + 3], [l - 3, b + 3]], '#f3c33d'); poly([[l, t], [r, t], [r, b], [l, b]], '#fbe5c1');
    label('大量ポイント', 0, -h / 2 + h * 0.25, 52, '#ffd65c', '#a81818', 12);
  }
  function drawBig(im, v, val, calm) {
    const T = TELOP, cx = T.cx, cy = T.cy, w = T.w, h = w * T.ar, L = sm(v / (calm ? 0.8 : T.rise)), rot = 0.3 + (calm ? 0 : v * T.spin);
    // 暗い 舞台（ルーレットは 見せない）と うしろの 赤い 光
    g.save(); g.fillStyle = '#060302'; g.fillRect(0, 0, W, H);
    const bg = g.createRadialGradient(cx, cy, 20, cx, cy, 470);
    bg.addColorStop(0, `rgba(255,190,60,${0.95 * L})`); bg.addColorStop(0.3, `rgba(224,82,20,${0.85 * L})`); bg.addColorStop(0.62, `rgba(126,16,10,${0.7 * L})`); bg.addColorStop(1, `rgba(36,4,4,${0.5 * L})`);
    g.fillStyle = bg; g.fillRect(0, 0, W, H);
    // 金の 光の すじ（ゆっくり 回る：太い 18本と、反対へ 回る 細い 9本）
    g.globalCompositeOperation = 'lighter';
    for (const [n, half, dir, al, len] of [[18, 0.085, 1, 0.42, 560], [9, 0.035, -0.7, 0.34, 620]]) {
      const gr = g.createRadialGradient(cx, cy, 30, cx, cy, len);
      gr.addColorStop(0, `rgba(255,232,140,${al * L})`); gr.addColorStop(0.5, `rgba(255,200,90,${al * 0.55 * L})`); gr.addColorStop(1, 'rgba(255,170,60,0)');
      g.fillStyle = gr; g.beginPath();
      for (let i = 0; i < n; i++) { const a = i / n * TAU + rot * dir; g.moveTo(cx, cy); g.arc(cx, cy, len, a - half, a + half); g.closePath(); }
      g.fill();
    }
    // うしろの 光（ゆっくり 息を する）
    const br = calm ? 1 : 0.92 + 0.08 * Math.sin(TAU * v / 2.6), gl = g.createRadialGradient(cx, cy, 10, cx, cy, 250);
    gl.addColorStop(0, `rgba(255,248,214,${0.7 * L * br})`); gl.addColorStop(0.5, `rgba(255,214,120,${0.34 * L * br})`); gl.addColorStop(1, 'rgba(255,180,70,0)');
    g.save(); g.translate(cx, cy); g.scale(1.3, 0.82); g.translate(-cx, -cy); g.fillStyle = gl; g.fillRect(-W, -H, 3 * W, 3 * H); g.restore();      // 横に 長い 光（テロップの 形に 合わせる）
    g.restore();
    if (!calm) confetti(BIGCONF, Math.max(0, v - 0.2), sm((v - 0.2) / 0.5), W, H);      // 紙ふぶき（金・赤・白）
    // テロップ：手前から 飛びこんで（1.9倍 → 1倍）着いたら 少し はずむ
    const sl = T.slam; let s;
    if (calm) s = 1.04 - 0.04 * sm(v / 0.5);
    else if (v < sl) { const q = v / sl; s = T.z0 - (T.z0 - 1) * q * q; }
    else { const q = clamp((v - sl) / 0.32, 0, 1); s = 1 - 0.06 * Math.sin(Math.PI * q) * (1 - q); }
    if (!calm) { const q = (v - sl) / 0.55; if (q > 0 && q < 1) {      // 着いた ときの 光の 輪（1回）
      g.save(); g.globalCompositeOperation = 'lighter'; g.strokeStyle = `rgba(255,236,170,${0.45 * (1 - q)})`; g.lineWidth = 7 - 5 * q;
      g.beginPath(); g.ellipse(cx, cy, 150 + 230 * easeOut(q), 100 + 150 * easeOut(q), 0, 0, TAU); g.stroke(); g.restore(); } }
    g.save(); g.globalAlpha *= calm ? sm(v / 0.5) : sm(v / T.fade); g.translate(cx, cy); g.scale(s, s);
    if (im) {
      const sw = calm || v < T.sweep[0] ? -1 : mod(v - T.sweep[0], T.sweep[1]) / T.sweep[2];      // なでる 光（0〜1 の 間 だけ：ななめの 白い 帯が 左から 右へ。はじめは 1.6秒 から ＝ 出て くる 動きと 重ねない）
      if (sw >= 0 && sw < 1) {
        const pw = Math.max(1, Math.round(w * PX)), ph = Math.max(1, Math.round(h * PX));
        if (!TSH) TSH = document.createElement('canvas');
        if (TSH.width !== pw || TSH.height !== ph) { TSH.width = pw; TSH.height = ph; }
        const q = TSH.getContext('2d'); q.globalCompositeOperation = 'source-over'; q.clearRect(0, 0, pw, ph); q.drawImage(im, 0, 0, pw, ph);
        q.globalCompositeOperation = 'source-atop';
        const x = (-0.3 + 1.6 * sw) * pw, bw = 0.15 * pw, gs = q.createLinearGradient(x - bw, 0, x + bw, 0);
        gs.addColorStop(0, 'rgba(255,255,255,0)'); gs.addColorStop(0.5, 'rgba(255,255,236,0.5)'); gs.addColorStop(1, 'rgba(255,255,255,0)');
        q.save(); q.transform(1, 0, -0.35, 1, 0.35 * ph / 2, 0); q.fillStyle = gs; q.fillRect(x - bw, -ph, 2 * bw, 3 * ph); q.restore();
        g.drawImage(TSH, -w / 2, -h / 2, w, h);
      } else g.drawImage(im, -w / 2, -h / 2, w, h);
    } else bigCard(w, h);
    // ポイント（板の 中）
    const nv = v - T.num;
    if (nv > 0) {
      const [px0, py0, px1, py1] = T.panel, bx = -w / 2 + (px0 + px1) / 2 * w, by = -h / 2 + (py0 + py1) / 2 * h, bw = (px1 - px0) * w, bh = (py1 - py0) * h;
      // 字の ある 所（数字の 上から「,」の しっぽの 下 まで）の まん中を 板の まん中に（字の 形から 測る ＝ フォントが かわっても ずれない）。しっぽと ふちが 板から 出ない 大きさに する
      const txt = comma(val), S1 = 64, S2 = 46, gap = 4, EW = 13;
      g.textAlign = 'left'; g.textBaseline = 'alphabetic';
      g.font = `900 ${S1}px ${SERIF}`; const m1 = g.measureText(txt), w1 = m1.width, asc = m1.actualBoundingBoxAscent > 0 ? m1.actualBoundingBoxAscent : S1 * 0.74, dsc = Math.max(0, m1.actualBoundingBoxDescent || 0);
      g.font = `900 ${S2}px ${SERIF}`; const w2 = g.measureText('P').width;
      const tot = w1 + gap + w2, sc = Math.min(bw * 0.92 / (tot + EW), bh * 0.94 / (asc + dsc + EW)) * (calm ? 1 : 0.6 + 0.4 * backOut(nv / 0.28)), yb = (asc - dsc) / 2;
      g.save(); g.globalAlpha *= sm(nv / 0.12); g.translate(bx, by); g.scale(sc, sc); g.lineJoin = 'round'; g.strokeStyle = '#4a1a06';
      const gf = g.createLinearGradient(0, yb - asc, 0, yb); gf.addColorStop(0, '#fff3a6'); gf.addColorStop(0.5, '#ffd034'); gf.addColorStop(1, '#f08c12');
      for (const [t, x, size, ew] of [[txt, -tot / 2, S1, EW], ['P', -tot / 2 + w1 + gap, S2, 11]]) { g.font = `900 ${size}px ${SERIF}`; g.lineWidth = ew; g.strokeText(t, x, yb); g.fillStyle = gf; g.fillText(t, x, yb); }
      g.restore();
    }
    g.restore();
    // きらめき（テロップの まわり：ゆっくり 光る）
    for (let i = 0; i < 12; i++) {
      const ang = i / 12 * TAU + 0.4 * hash(i + 2), x = cx + Math.cos(ang) * w * (0.5 + 0.1 * hash(i + 5)), y = cy + Math.sin(ang) * h * (0.6 + 0.16 * hash(i + 8));
      const q = calm ? 0.5 : 0.5 + 0.5 * Math.sin(TAU * (v / (1.6 + 0.9 * hash(i + 11)) + hash(i + 3)));
      sparkle(x, y, (7 + 9 * hash(i + 13)) * (0.35 + 0.65 * q), 0.9 * L * (0.3 + 0.7 * q));
    }
    // 「GET!!」（テロップの 下）
    const gv = v - T.get;
    if (gv > 0) {
      g.save(); g.globalAlpha *= sm(gv / 0.12); g.translate(cx, cy + h / 2 + 44); const k = calm ? 1 : backOut(gv / 0.3); g.scale(k, k);
      const gf = g.createLinearGradient(0, -24, 0, 24); gf.addColorStop(0, '#fffbe6'); gf.addColorStop(0.55, '#ffe27a'); gf.addColorStop(1, '#f5a623');
      label('GET!!', 0, 0, 58, gf, '#3a1206', 13); g.restore();
    }
  }

  // ためす 用：大量ポイントの 場面の 1コマ（ドーン！！から v 秒め）を 描く。時計を 使わない ＝ 決めた 秒の 絵が いつも 同じ（光の 点めつを 1/30秒ごとに 測る：test_tc.py）。noImg＝絵が ない ときの 札で 描く
  async function bigFrame(cv, v, val, calm, noImg) {
    const im = noImg ? null : await img(TELOP.src);
    PX = cv.width / W; g = cv.getContext('2d'); g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.globalCompositeOperation = 'source-over'; g.clearRect(0, 0, cv.width, cv.height); g.setTransform(PX, 0, 0, PX, 0, 0);
    drawBig(im, v, val, !!calm); g.setTransform(1, 0, 0, 1, 0, 0);
    return !!im;
  }

  async function roulette(cv, o) {
    const th = RT_STYLE[o.th] ? o.th : 'normal', I = await rtLoad(th);
    if (!GEO || !GEO[th]) return;
    const Gm = GEO[th], r = { th, a: o.a, b: o.b, win: o.win ? 1 : 0, HIT: null, S0: null, S1: null }, dim = DIMR[o.bg] != null ? DIMR[o.bg] : 0.4;
    // 第4.159版：止まった あと ポイントを 出す 時（RV）。安い 方＝すぐ（止まって 0.4秒）・デカ的中と 同じ 音／高い 方＝止まって 0.25秒 あとに プチュン（盤の 上に 幕）→ 真っ暗に なったら すぐ ポイント
    //   高い 方（まさちゃん 11/12 13:27・13:30）：真っ暗に なったら ルーレットには もどらない → 大量ポイントの 場面（drawBig）・音は ドーン！！
    //   RV は プチュンの 幕を 出した コマから PD 秒（コマが おくれても、幕の 中の 動きと ずれない：線が 点に ちぢんだ あとに 出る）
    const val = r.win ? r.b : r.a, high = val >= Math.max(r.a, r.b), calm = pcCalm(), P0 = 0.25, PD = calm || !pcHtml() ? PCH.calm : PCH.dark;
    const telop = high ? await img(TELOP.src) : null;
    let pc = null, RV = null;
    let tickIdx = null;
    se(o, 'tc_se_unfold.m4a', 1, 0);
    await play(cv, o, (u, st) => {
      if (st.tap != null && r.HIT == null) { r.HIT = st.tap; r.S0 = r.HIT + 0.05; r.S1 = r.S0 + 3.5; if (!high) RV = r.S1 + 0.4; }
      if (high && RV != null && u >= RV) {                    // 高い 方：プチュンの あとは 大量ポイントの 場面 だけ（ルーレットは 描かない）。幕は 0.2秒で 明ける（下も 真っ暗から 始まる）
        if (pc) { pcClose(pc, 0.2); pc = null; }
        drawBig(telop, u - RV, val, calm);
        return { end: RV + TELOP.hold };
      }
      const app = sm(u / 0.45);
      g.save(); g.globalAlpha *= app; g.fillStyle = `rgba(16,10,6,${dim})`; g.fillRect(0, 0, W, H); g.restore();
      g.save(); g.globalAlpha *= app;
      const z = 1 + 0.03 * (1 - sm(u / 0.6)); g.translate(W / 2, H / 2); g.scale(z, z); g.translate(-W / 2, -H / 2);
      g.translate(OX, 0); g.scale(K, K);
      drawGlow(r, Gm, u);
      if (I.plate) { g.drawImage(I.plate, 0, 0, 1024, 1536); drawEye(r, u); }
      const ang = rtAngle(r, u);
      drawFace(r, Gm, ang, r.S1 != null ? sm((u - r.S1 - 0.1) / 0.4) : 0);
      const P = Gm.parts.ptr; if (I.ptr) g.drawImage(I.ptr, P.x, P.y, P.w, P.h);
      drawLever(r, I, Gm, u); drawChev(r, Gm, u); drawTap(r, Gm, u);
      if (RV != null && u > RV) {                             // 安い 方：盤の 上に 紙ふぶきと「○P GET！！！」
        const v = u - RV; g.save(); g.setTransform(PX, 0, 0, PX, 0, 0); g.globalAlpha = app * (st.closeAt != null ? 1 - sm((u - st.closeAt) / 0.5) : 1); confetti(RT_STYLE[th].conf, v, sm(v / 0.4), W, H); g.restore();
        drawGet(r, Gm, val, v / 0.45);
      }
      g.restore();
      if (high && r.S1 != null && RV == null && u >= r.S1 + P0) { pc = pcOpen(cv, false); RV = u + PD; }      // 高い 方：プチュン（盤の 上に 幕）→ PD 秒で 真っ暗 → 上の 大量ポイントの 場面へ
      return { end: RV != null ? RV + (high ? TELOP.hold : 0.8) : null };
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
      if (high && r.S1 != null && last < r.S1 + P0 && u >= r.S1 + P0 && !calm) se(o, 'sfx_sdp.m4a', PCH_GAIN, 0);    // 高い 方：プチュン（控えめの ときは 音も なし：的中の 演出と 同じ）
      if (RV != null && last < RV && u >= RV) se(o, high ? 'tc_se_doon.m4a' : 'sfx_big.m4a', high ? 1 : BIG_GAIN, 0);      // ポイントが 出る：高い 方＝ドーン！！（テロップと いっしょ）・安い 方＝デカ的中と 同じ 音
    });
    pcClose(pc, 0);
  }

  // ================= 壁紙チケット =================
  const IW = 1086, IH = 1448, TKK = Math.max(W / IW, H / IH), TOX = (W - IW * TKK) / 2, TOY = (H - IH * TKK) / 2;
  const FALL0 = 0.35, FALL = 0.26, OPEN = 1.25, HOLD = 0.35, REVEAL = 0.95;      // 扉が 落ちはじめる（プチュンの あとは 0.03）・落ちる 長さ・開く・白い 光・チケットが 出る（秒）。着く＝落ちはじめ＋FALL・「タップ」＝着いて 0.7秒
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
    // 第4.159版（まさちゃん 11/12 11:56「プチュンしたらすぐに扉が落ちてくる演出にして！」）：o.puchun＝よんだ 瞬間（PUSH を 押した 瞬間）に プチュン（幕は この キャンバスの 下・絵を 読むのを 待たない）
    //   → 真っ暗に なったら すぐ 扉が 落ちて くる（いつもの はじめの 間 0.35秒は なし・うしろは 真っ暗の まま）。
    //   幕は、扉が 着いて はずみ おわったら 外す（扉の 絵が 舞台 ぜんぶを かくして いる ので 見た目は かわらない）
    let pc = null;
    if (o.puchun) { pc = pcOpen(cv, true); if (!pc.calm) se(o, 'sfx_sdp.m4a', PCH_GAIN, 0); }
    const [closed, open_, tk] = await Promise.all([img('tk_door_closed.webp'), img('tk_door_open.webp'), img('tk_ticket.webp')]);
    const n = Math.max(1, Math.min(3, o.n | 0)), pos = TKPOS[n], dim = (DIMR[o.bg] != null ? DIMR[o.bg] : 0.4) + 0.08;
    const T = { tap: null, get0: null };
    if (pc) await until(pc.t0 + pc.dark * 1000);
    const F0 = pc ? 0.03 : FALL0, LD = F0 + FALL, TS = LD + 0.7;      // 扉が 落ちはじめる・着く・「タップ」が 出る（秒）
    try {
    await play(cv, Object.assign({ tapMin: TS }, o), (u, st) => {
      if (pc && u > LD + 0.34) { pcClose(pc, 0); pc = null; }
      if (st.tap != null && T.tap == null) T.tap = Math.max(st.tap, TS);
      const uo = T.tap != null ? u - T.tap : -1, get0 = T.tap != null ? T.tap + OPEN + HOLD + 0.55 : null;
      g.fillStyle = `rgba(18,10,4,${dim * sm(u / 0.45)})`; g.fillRect(0, 0, W, H);
      const p = clamp((u - F0) / FALL, 0, 1), q = (u - LD) / 0.3;
      const yOff = u < LD ? -H * (1 - p * p) : -10 * Math.sin(Math.PI * clamp(q, 0, 1)) * (1 - clamp(q, 0, 1));
      const zoom = uo > 0 ? (uo < OPEN + HOLD ? 1 + 0.08 * smoother(uo / (OPEN + HOLD)) : 1 + 0.08 * (1 - smoother((uo - OPEN - HOLD) / REVEAL))) : 1;
      const opened = uo >= OPEN + HOLD * 0.5;
      if (u >= F0) {
        g.save(); g.translate(W / 2, H / 2 + yOff); g.scale(zoom, zoom); g.translate(-W / 2, -H / 2);
        const im = opened ? open_ : closed; if (im) g.drawImage(im, TOX, TOY, IW * TKK, IH * TKK);
        g.save(); g.translate(TOX, TOY); g.scale(TKK, TKK);
        const lk = opened ? 0.75 + 0.25 * sm((uo - OPEN - HOLD - REVEAL * 0.3) / 0.8) : sm((u - LD - 0.1) / 0.6);
        const ow = uo > 0 && !opened ? smoother(uo / OPEN) : 0;
        goldLight(u, lk, 34 + 520 * Math.pow(ow, 2.2), ow);
        if (u >= LD) dust(u - LD);
        g.restore(); g.restore();
      }
      g.save(); g.translate(TOX, TOY); g.scale(TKK, TKK);
      tkTap(u - TS, sm((u - TS) / 0.3) * (uo >= 0 ? 1 - sm(uo / 0.18) : 1));
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
      if (cross(F0)) se(o, 'tc_se_tk_fall.m4a', 1, 0);
      if (cross(LD)) se(o, 'tc_se_tk_land.m4a', 1, 0);
      if (cross(TS)) se(o, 'tc_se_tk_tapshow.m4a', 1, 0);
      if (T.tap != null) {
        const tt = T.tap, get0 = tt + OPEN + HOLD + 0.55;
        if (cross(tt)) { se(o, 'tc_se_tk_tap.m4a', 1, 0); se(o, 'tc_se_tk_open.m4a', 1, 0); }
        if (cross(tt + OPEN)) se(o, 'tc_se_tk_white.m4a', 1, 0);
        if (cross(tt + OPEN + HOLD)) se(o, 'tc_se_tk_reveal.m4a', 1, 0);
        pos.forEach((_, i) => { if (cross(get0 + i * 0.28)) se(o, 'tc_se_tk_ticket.m4a', 1, 0); });
        if (cross(get0 + 0.75 + 0.28 * (pos.length - 1))) se(o, 'tc_se_tk_get.m4a', 1, 0);
      }
    });
    } finally { pcClose(pc, 0); }
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
  function preload(th) { rtLoad(th || 'normal'); ['tk_door_closed.webp', 'tk_door_open.webp', 'tk_ticket.webp', TELOP.src].forEach(img); }
  return { roulette, ticket, puchun, preload, PCH, TELOP, bigFrame };
})();
window.TCFX = TCFX;
