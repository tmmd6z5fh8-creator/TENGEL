// 的中ボタン（App Store版 第3弾：アップデート指示書 10章・16.2〜16.6）
//   結果を保存したあとに 1つだけ出す（強い順）：神様的中（3連単の当たりの3頭に 超大穴＝10〜12番人気と、ほかに 大穴以上＝7〜12番人気）＞ ど的中（3連単の当たりの3頭に 超大穴）＞ デカ的中（3連単の当たり）＞ 的中（ほかの当たり）／当たりなし＝ハズレ（ボードだけ・音なし）
//   隠れど的中＝デカ的中の 2〜7回に1回（ランダム。数は端末の中だけ：記録・バックアップには入れない）→ 見た目はデカの PUSH・押すと ど的中の演出
//   第5弾（16.3 の 特別な 演出・くじは ※仮）：ど的中の 6回に1回は プレミアムど的中（pc）・その 8回に1回は 超プレミアムど的中（zp）／
//     神様的中の 8回に1回は 超神様的中（sgd：1コマずつ 描いた 動画）・その 4回に1回は 超プレミアム神様的中（spg：超プレミアムの ふり → き！で 昇格の 動画 → 超神様の 動画）
//     どれも PUSH は ど的中と 同じ・どの 着せ替えでも 出る・隠れど的中では 出ない・的中エフェクト オフでは くじを ひかない
//   流れ：PUSH（上下に動く）→ タップ → 演出 → いつものボード（券種ごとの 結果・お金は出さない：16.4）→「とじる」
//   見本（kisekae/gen_fx.py・boards.py・premium_cute.py・super_premium.py・kami.py・kami_super.py）の CSS と HTML は kisekae/build_fx.py が window.__FX に束ねる。
//   舞台は 390×844 を画面に合わせて縮める（16.3 ※仮）
//   音：kisekae/gen_sfx.py の音（m4a・アプリの中のファイル）を Web Audio で。「結果を保存」を押したときに準備する（iPhone は押す操作の中でないと鳴らないことがある）
//   動画（超神様的中・超プレミアム神様的中）：アプリの中の mp4 を <video> で。押した 瞬間（タップの 中）に 再生 → 動きだした 時（playing）を 0秒に して 音と ボードの 時計を そろえる。
//     4秒 たっても 動かない・読めない・視差効果を減らす／控えめ → さいごの 1まい → 1.3秒 ボード（※仮）
//   設定：的中エフェクト（オフ＝PUSH・演出・音なしでボードだけ静かに）・演出を控えめにする（iPhone の視差効果を減らすと同じ形。はじめはその設定に合わせる）・効果音（はじめはオン ※仮）
//   ほかの画面から：window.TengelFx（decide・show・close・prime・get・set…）。Web版（ホーム画面のアプリ）では何もしない
(function () {
  'use strict';
  if (!window.__NATIVE || !window.__FX) return;
  const A = window.__FX;
  const $ = (s, r) => (r || document).querySelector(s);
  const TL = () => window.TengelLocal, WL = () => window.TengelWallet, RS = () => window.TengelReserve;
  // 着せ替え（第4弾・kisekae.js）：いまのテーマの 的中PUSH（面・押したあと・はじけるかけら）と ボードの飾り。いつもの・読めていないときは null（いつもの形）
  const KS = () => { try { const k = window.TengelKisekae; return k && k.on && k.fx ? k.fx() : null; } catch (e) { return null; } };
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const SUPER = [10, 12];                 // 超大穴＝単勝人気 10〜12番人気（判定の J・K・L）。13番人気より下は入れない
  const BIG = [7, 9];                     // 大穴＝7〜9番人気（神様的中：超大穴と いっしょに 3連単に）
  const HIDDEN_KEY = 'tengel.fxhidden';   // 隠れど的中の数（端末の中だけ）
  const SETTING = 'fx';
  // PUSHが出たときの音・押したときの音（隠れど的中：PUSHはデカの音・押すとど的中の音。プレミアム・神様 など：PUSHは ど的中の音・押すと その音。超プレミアム神様は 超プレミアムの音 → 昇格 → 超神様＋声）
  const SND = { hit: ['hit_push', 'hit'], big: ['big_push', 'big'], fz: ['fz_push', 'fz'], hidden: ['big_push', 'fz'], pc: ['fz_push', 'pc'], zp: ['fz_push', 'zp'], gd: ['fz_push', 'gd'], sgd: ['fz_push', 'sgd'], spg: ['fz_push', 'zp'] };
  const FZ_PUSH = { fz: 1, pc: 1, zp: 1, gd: 1, sgd: 1, spg: 1 };     // PUSH が ど的中の 虹色の 超デカ PUSH の もの
  const BOARD_OF = { hidden: 'fz', pc: 'fz', zp: 'fz', gd: 'fz', sgd: 'fz', spg: 'fz' };   // ボードの 形（ど的中の 形）
  const TITLE_OF = { pc: 'fz', zp: 'fz', spg: 'sgd' };                                      // ボードの 見出し（A.board.titles の キー）
  const LOT = { pc: 1 / 6, zp: 1 / 8, sgd: 1 / 8, spg: 1 / 4 };                             // くじ（※仮）：ど的中 → プレミアム → 超プレミアム／神様 → 超神様 → 超プレミアム神様
  let S = { effects: true, calm: null, sound: true };
  let cur = null;

  // ---------- CSS（見本の CSS を .fxs の中だけに効かせたもの） ----------
  function css() {
    if ($('#fxCss')) return;
    const st = document.createElement('style'); st.id = 'fxCss';
    st.textContent = A.css + '\n.fxs .ov.quiet .bh,.fxs .ov.quiet .zrib,.fxs .ov.quiet .n.zx,.fxs .ov.quiet .brows li.top::after{animation:none!important}\n'
      + '#fxVh{position:fixed;left:-9999px;top:0;width:1px;height:1px;overflow:hidden;opacity:0;pointer-events:none}\n';
    document.head.appendChild(st);
  }
  const reduced = () => !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  const calm = () => !!S.calm || reduced();   // iPhone の「視差効果を減らす」が オンなら いつも 控えめ（CSS の @media も 効く）。設定は それに 足す 形
  const rand = () => (typeof window.TengelFx === 'object' && typeof window.TengelFx._rand === 'function' ? window.TengelFx._rand() : Math.random());
  function emit(phase, kind) { try { document.dispatchEvent(new CustomEvent('tengel:fx', { detail: { phase: phase, kind: kind || (cur && cur.kind) || null } })); } catch (e) { /* なし */ } }

  // ---------- 設定 ----------
  async function loadSettings() {
    try { const v = TL() && TL().getSetting ? await TL().getSetting(SETTING) : undefined; if (v && typeof v === 'object') S = Object.assign({}, S, v); } catch (e) { /* はじめの値のまま */ }
    emit('settings');
  }
  function set(patch) {
    S = Object.assign({}, S, patch || {});
    try { if (TL() && TL().putSetting) TL().putSetting(SETTING, S).catch(() => {}); } catch (e) { /* 覚えられなくてもOK */ }
    if (cur) cur.stage.classList.toggle('calm', calm());
    emit('settings');
    return Object.assign({}, S);
  }

  // ---------- どれが出るか（10章） ----------
  // spec = { r, n（頭数）, rows: [{ t（券種）, state（的中／不的中／返還）, hits: [[馬番…]…], n（点数） }…]（予約した順）, ranks: { 馬番: 人気順位 } }
  // → { kind: miss／hit／big／fz／gd, supers: [{ no, rank }…]（超大穴）, bigs: [{ no, rank }…]（大穴：神様のとき） }
  function decide(spec) {
    const rows = (spec && spec.rows) || [];
    if (!rows.some(x => x.state === '的中')) return { kind: 'miss', supers: [], bigs: [] };
    const tri = rows.find(x => x.t === '3連単' && x.state === '的中');
    if (!tri) return { kind: 'hit', supers: [], bigs: [] };
    const ranks = (spec && spec.ranks) || {}, supers = [], bigs = [];
    let god = false;
    const add = (arr, no, rank) => { if (!arr.some(s => s.no === +no)) arr.push({ no: +no, rank: rank }); };
    (tri.hits || []).forEach(c => {
      const rs = c.map(no => (ranks[no] == null ? null : +ranks[no]));
      if (rs.some(v => v == null || !isFinite(v))) return;      // 人気がわからない馬がいる組は ど的中・神様にしない（デカ）※仮
      const sp = [], bg = [];
      c.forEach((no, i) => { if (rs[i] >= SUPER[0] && rs[i] <= SUPER[1]) sp.push([no, rs[i]]); else if (rs[i] >= BIG[0] && rs[i] <= BIG[1]) bg.push([no, rs[i]]); });
      if (!sp.length) return;
      sp.forEach(x => add(supers, x[0], x[1]));
      if (sp.length >= 2 || bg.length) { god = true; bg.forEach(x => add(bigs, x[0], x[1])); }   // 神様：超大穴と、ほかに 大穴以上（超大穴が 2頭でも）※仮
    });
    return { kind: god ? 'gd' : supers.length ? 'fz' : 'big', supers: supers, bigs: god ? bigs : [] };
  }
  // 隠れど的中の数（※仮）：デカ的中が出るたびに数えて、2〜7回目（ランダム）の1回を隠れど的中に。出たら次の回数をまた 2〜7 から決める。本物のど的中は数えない
  const nextHidden = () => 2 + Math.floor(rand() * 6);
  function hiddenState() {
    try { const o = JSON.parse(localStorage.getItem(HIDDEN_KEY) || 'null'); if (o && o.n >= 2 && o.n <= 7 && o.c >= 0) return { c: +o.c, n: +o.n }; } catch (e) { /* なし */ }
    return { c: 0, n: nextHidden() };
  }
  function rollHidden() {
    const h = hiddenState(); h.c += 1;
    let hid = false;
    if (h.c >= h.n) { hid = true; h.c = 0; h.n = nextHidden(); }
    try { localStorage.setItem(HIDDEN_KEY, JSON.stringify(h)); } catch (e) { /* 覚えられなくてもOK */ }
    return hid;
  }
  // 特別な 演出の くじ（※仮・数えかたは しない）：ど的中 → 6分の1 で プレミアム → その 8分の1 で 超プレミアム／神様 → 8分の1 で 超神様 → その 4分の1 で 超プレミアム神様
  function lottery(kind) {
    if (kind === 'fz') return rand() < LOT.pc ? (rand() < LOT.zp ? 'zp' : 'pc') : 'fz';
    if (kind === 'gd') return rand() < LOT.sgd ? (rand() < LOT.spg ? 'spg' : 'sgd') : 'gd';
    return kind;
  }

  // ---------- ボード（いつもの・お金なし） ----------
  function num(no, n, zx, isWaku) {
    const w = isWaku ? Math.min(Math.max(+no || 1, 1), 8) : (RS() ? RS().waku(+no, +n || 0) : Math.min(+no || 1, 8));
    return `<span class="n w${w}${zx ? ' zx' : ''}">${esc(no)}</span>`;
  }
  function combo(c, t, n, mark) {
    const ordered = !!(RS() && RS().ORDERED[t]) || t === '馬単' || t === '枠単' || t === '3連単', isWaku = t === '枠複' || t === '枠単';
    return `<span class="bc">${c.map(no => num(no, n, mark.indexOf(+no) >= 0, isWaku)).join(`<span class="ar">${ordered ? '→' : '-'}</span>`)}</span>`;
  }
  // 行：予約した券種ごとに 1行（9つまで）。デカ・ど的中・隠れど的中・特別な 演出は 3連単の行をいちばん上。当たった組番は 3つまで＋「ほか○点」。当たりのない券種は組番なし・うすく
  function rowsHTML(spec, kind, supers, bigs) {
    let rows = ((spec && spec.rows) || []).slice();
    if (kind !== 'hit' && kind !== 'miss') rows.sort((a, b) => (b.t === '3連単' ? 1 : 0) - (a.t === '3連単' ? 1 : 0));
    rows = rows.slice(0, 9);
    const mark = (supers || []).map(s => s.no).concat((bigs || []).map(s => s.no)), n = spec && spec.n;
    const html = rows.map((x, i) => {
      const hit = x.state === '的中', ref = x.state === '返還', hits = x.hits || [];
      const cls = [hit && x.t === '3連単' && kind !== 'hit' ? 'top' : '', hit ? '' : 'no'].filter(Boolean).join(' ');
      const rs = hit ? '<span class="rs hit">的中</span>' : ref ? '<span class="rs ref">返還</span>' : '<span class="rs miss">不的中</span>';
      const cs = hit ? hits.slice(0, 3).map(c => combo(c, x.t, n, x.t === '3連単' ? mark : [])).join('') + (hits.length > 3 ? `<span class="more">ほか${hits.length - 3}点</span>` : '') : '';
      return `<li${cls ? ` class="${cls}"` : ''} style="--i:${i}"><span class="bt">${esc(x.t)}</span>${rs}${cs}</li>`;
    }).join('');
    return { html: html, n: rows.length };
  }
  // 見出し：全角の「！」が3つ続くところは字の間をつめる（.bx3）・最後の字は .bz（全角の「！」なら .bzx：右のあきをつめて まん中に）
  function titleHTML(kind) {
    const t = A.board.titles[TITLE_OF[kind] || kind] || '', head = t.slice(0, -1), last = t.slice(-1);
    const h = t.endsWith('！！！') ? esc(head.slice(0, -2)) + '<span class="bx3">！！</span>' : esc(head);
    return `${h}<span class="bz${last === '！' ? ' bzx' : ''}">${esc(last)}</span>`;
  }
  // 帯：ど的中・プレミアム・超プレミアム＝超大穴の 馬番と 人気／神様・超神様・超プレミアム神様＝超大穴と 大穴の 馬番（※仮）／隠れ＝デカ的中が ど的中に化けた
  function ribbonHTML(kind, spec, supers, bigs) {
    const n = spec && spec.n;
    if (kind === 'hidden') return '<div class="zrib"><b class="zt">隠れ</b><span>デカ的中が ど的中に化けた！</span></div>';
    if (!supers || !supers.length) return '';
    if (kind === 'gd' || kind === 'sgd' || kind === 'spg') {
      const bg = bigs && bigs.length ? `<b class="zt">大穴</b>${bigs.map(s => num(s.no, n, true)).join('')}` : '';
      return `<div class="zrib"><b class="zt">超大穴</b>${supers.map(s => num(s.no, n, true)).join('')}${bg}<span>が3連単に！</span></div>`;
    }
    return `<div class="zrib"><b class="zt">超大穴</b>${supers.map(s => num(s.no, n, true)).join('')}<span>${supers.map(s => esc(s.rank) + '番人気').join('・')}が3連単に！</span></div>`;
  }
  function boardHTML(kind, spec, supers, bigs, rows) {
    const k = BOARD_OF[kind] || kind;
    const sub = `${esc(spec && spec.r != null ? spec.r : '')}R の券種ごとの結果`;
    const rib = ribbonHTML(kind, spec, supers, bigs);
    const ks = KS(), tid = ks ? ks.tid : 'default', orn = ks ? ks.orn : A.board.orn;   // ボードはそのテーマの形（16.4）。CSS は kisekae.js が入れる
    return `<div class="rb ${k} t-${tid}"><div class="hd"><div class="bh${kind === 'miss' ? '' : ' logo'}">${titleHTML(kind)}</div><div class="bsub">${sub}</div>${rib}</div><div class="card">${orn}<ul class="brows">${rows}</ul></div></div>`;
  }

  // ---------- 音（Web Audio：先に読んで、押した瞬間を0秒にして動きとそろえる） ----------
  const SX = { raw: {}, buf: {}, ctx: null, src: null, more: [], id: 0, fetched: false, ok: 0 };
  function fetchAll() {
    if (SX.fetched || typeof fetch !== 'function') return;
    SX.fetched = true;
    Object.keys(A.sfx).forEach(k => { SX.raw[k] = fetch(A.sfx[k], { cache: 'force-cache' }).then(r => (r.ok ? r.arrayBuffer() : null)).catch(() => null); });
  }
  function decode(c, b) { return new Promise(ok => { try { const q = c.decodeAudioData(b, ok, () => ok(null)); if (q && q.catch) q.catch(() => ok(null)); } catch (e) { ok(null); } }); }
  function actx() {
    if (!SX.ctx) { const AC = window.AudioContext || window.webkitAudioContext; if (AC) { try { SX.ctx = new AC(); } catch (e) { SX.ctx = null; } } }
    if (SX.ctx && SX.ctx.state !== 'running' && SX.ctx.resume) { try { const p = SX.ctx.resume(); if (p && p.catch) p.catch(() => {}); } catch (e) { /* なし */ } }
    return SX.ctx;
  }
  function bufOf(c, k) { if (!SX.buf[k] && SX.raw[k]) SX.buf[k] = SX.raw[k].then(b => (b ? decode(c, b.slice(0)) : null)); return SX.buf[k] || Promise.resolve(null); }
  // 「結果を保存」を押したとき（押す操作の中）に呼ぶ：音の準備（消音スイッチなら鳴らさない＝ambient）・ネオンの絵の先読み・動画の 先読み
  function prime() {
    try { if (navigator.audioSession && 'type' in navigator.audioSession) navigator.audioSession.type = 'ambient'; } catch (e) { /* 使えないiOS */ }
    fetchAll();
    try { Object.keys(A.assets).forEach(k => { const im = new Image(); im.src = A.assets[k]; }); } catch (e) { /* なし */ }
    try { Object.keys(A.films || {}).forEach(video); } catch (e) { /* なし */ }
    if (!S.sound) return false;
    const c = actx(); if (!c) return false;
    if (!SX.ok) { SX.ok = 1; try { const s0 = c.createBufferSource(); s0.buffer = c.createBuffer(1, 1, 22050); s0.connect(c.destination); s0.start(0); } catch (e) { /* なし */ } }
    Object.keys(SX.raw).forEach(k => bufOf(c, k));
    return true;
  }
  // 音 k を、いまを0秒として from 秒の所から wait 秒後に鳴らす（読むのが0.1秒より遅れたら、遅れたぶん先から鳴らして動きとそろえる）。layer＝前の音を止めずに重ねる（超プレミアム神様の 超神様の音）
  function sfx(k, from, wait, layer) {
    if (!layer) hush();
    if (!S.sound) return;
    fetchAll();
    const c = actx(); if (!c || !SX.raw[k]) return;
    const id = SX.id, t0 = Date.now(); from = from || 0; wait = wait || 0;
    bufOf(c, k).then(buf => {
      if (id !== SX.id || !buf) return;
      const el = (Date.now() - t0) / 1000, late = Math.max(0, el - wait), off = from + (late > .1 ? late : 0);
      if (off >= buf.duration) return;
      const s = c.createBufferSource(); s.buffer = buf; s.connect(c.destination);
      s.start(c.currentTime + Math.max(0, wait - el), off);
      if (layer) SX.more.push(s); else SX.src = s;
    });
  }
  function hush() {
    SX.id++;
    if (SX.src) { try { SX.src.stop(); } catch (e) { /* もう止まっている */ } SX.src = null; }
    SX.more.forEach(s => { try { s.stop(); } catch (e) { /* もう止まっている */ } }); SX.more = [];
  }
  document.addEventListener('visibilitychange', () => { if (document.hidden) { hush(); vidHidden(); } else vidBack(); });
  window.addEventListener('pagehide', hush);

  // ---------- 動画（超神様的中・超プレミアム神様的中：アプリの中の mp4・押す前から読んでおく） ----------
  const VID = {};
  function holder() { let h = $('#fxVh'); if (!h) { h = document.createElement('div'); h.id = 'fxVh'; h.setAttribute('aria-hidden', 'true'); document.body.appendChild(h); } return h; }
  function video(name) {
    if (!A.films || !A.films[name]) return null;
    let v = VID[name];
    if (!v) {
      v = document.createElement('video'); VID[name] = v;
      v.muted = true; v.defaultMuted = true; v.playsInline = true; v.preload = 'auto'; v.loop = false;
      v.setAttribute('muted', ''); v.setAttribute('playsinline', ''); v.setAttribute('webkit-playsinline', ''); v.setAttribute('aria-hidden', 'true'); v.setAttribute('data-film', name);
      v.addEventListener('playing', () => onPlaying(name, v));
      v.addEventListener('ended', () => onEnded(name));
      v.addEventListener('error', () => onError(name));
      holder().appendChild(v);
    }
    if (v.dataset.src !== A.films[name]) { v.dataset.src = A.films[name]; v.src = A.films[name]; try { v.load(); } catch (e) { /* なし */ } }   // ファイル名が かわった（テスト）とき も 読み直す
    return v;
  }
  function park(v) { if (!v) return; try { v.pause(); } catch (e) { /* なし */ } try { v.currentTime = 0; } catch (e) { /* なし */ } v.className = ''; if (v.parentNode !== holder()) holder().appendChild(v); }
  function tryPlay(v, bad) { let p = null; try { p = v.play(); } catch (e) { bad(); return; } if (p && p.catch) p.catch(() => bad()); }
  function wake(v) { try { v.currentTime = 0; } catch (e) { /* なし */ } try { const p = v.play(); if (p && p.catch) p.catch(() => {}); v.pause(); } catch (e) { /* なし */ } }   // タップの 中で 一度 動かして 止めて おく（iPhone で あとから 再生できる ように）
  function later(fn, ms) { const t = setTimeout(() => { if (cur && cur.timers) cur.timers = cur.timers.filter(x => x !== t); fn(); }, ms); if (cur) cur.timers.push(t); return t; }
  function clearTimers() { if (!cur) return; cur.timers.forEach(clearTimeout); cur.timers = []; }
  const sgdOv = () => (cur ? $('.ov.sgd', cur.stage) : null), spzOv = () => (cur ? $('.ov.spz', cur.stage) : null);
  // 超神様的中：押した 瞬間に 動画を 再生。動きだした 時（playing）を 0秒に して 音と ボード（go）。4秒 たっても 動かない・視差効果を減らす／控えめ → さいごの 1まい（still）
  function sgdGo() {
    const v = video('sgd_film'); cur.v = v; cur.on = 0;
    if (!v || v.error || calm()) { sgdStill(); return; }     // 動画が ない・読めなかった（error）・控えめ → さいごの 1まい
    cur.stage.appendChild(v); v.className = 'sgv';
    try { v.currentTime = 0; } catch (e) { /* なし */ }
    tryPlay(v, sgdStill);
    later(() => { if (cur && !cur.on) sgdStill(); }, A.t.SG.WAIT_MAX * 1000);
  }
  function sgdStill() {
    if (!cur || cur.on === 2) return;
    clearTimers(); cur.on = 2;
    [cur.u, cur.v].forEach(x => { if (x) { try { x.pause(); } catch (e) { /* なし */ } x.classList.remove('on'); } });
    const z = spzOv(); if (z) z.classList.add('stop', 'gone');      // 超プレミアム神様：ふりの 画面も 消す
    const ov = sgdOv(); if (ov) ov.classList.add('still');
    sfx(cur.kind === 'spg' ? 'spg' : 'sgd', A.t.SG.STILL_FROM, A.t.SG.STILL_WAIT);
    emit('still');
  }
  // 超プレミアム神様的中：超プレミアムの ①〜③（音は 超プレミアム）→ 6.0秒（き！）で 止めて 昇格の 動画（sp：1＝き！で 止まった・2＝昇格の 動画・3＝超神様の 動画へ）→ 超神様の 動画（声つきの 音を 昇格の 音に 重ねる）
  function spgGo() {
    const u = video('spg_up'), v = video('sgd_film'); cur.u = u; cur.v = v; cur.on = 0; cur.sp = 0;
    if (!u || !v || u.error || v.error || calm()) { sgdStill(); return; }     // どちらかの 動画が ない・読めなかった・控えめ → ふりも 出さず さいごの 1まい ※仮
    cur.stage.appendChild(u); u.className = 'spu'; cur.stage.appendChild(v); v.className = 'sgv';
    wake(u); wake(v);
    sfx('zp');
    later(spgUp, A.t.SG.UP_AT * 1000);
  }
  function spgUp() {
    if (!cur || cur.kind !== 'spg' || cur.sp || cur.on) return;
    cur.sp = 1; hush();
    const z = spzOv(); if (z) z.classList.add('stop');
    const u = cur.u; try { u.currentTime = 0; } catch (e) { /* なし */ }
    tryPlay(u, sgdStill);
    later(() => { if (cur && cur.sp === 1) sgdStill(); }, A.t.SG.WAIT_MAX * 1000);
  }
  function spgFilm() {
    if (!cur || cur.kind !== 'spg' || cur.sp !== 2 || cur.on) return;
    cur.sp = 3; clearTimers();
    const v = cur.v; try { v.currentTime = 0; } catch (e) { /* なし */ }
    tryPlay(v, sgdStill);
    later(() => { if (cur && !cur.on) sgdStill(); }, A.t.SG.WAIT_MAX * 1000);
  }
  function onPlaying(name, v) {
    if (!cur || cur.phase !== 'reveal' || cur.on) return;
    if (cur.kind === 'sgd' && name === 'sgd_film') {
      cur.on = 1; clearTimers();
      sfx('sgd', v.currentTime || 0);
      v.classList.add('on'); const ov = sgdOv(); if (ov) ov.classList.add('go');
      emit('film');
    } else if (cur.kind === 'spg' && name === 'spg_up' && cur.sp === 1) {
      cur.sp = 2; clearTimers();
      sfx('spg_up', v.currentTime || 0);
      const z = spzOv(); if (z) z.classList.add('gone');
      v.classList.add('on');
      const rest = Math.max(0, (isFinite(v.duration) && v.duration ? v.duration : A.t.SG.UP) - (v.currentTime || 0));
      later(spgFilm, (rest + .5) * 1000);   // おわりの 知らせが こない 時の ため
      emit('up');
    } else if (cur.kind === 'spg' && name === 'sgd_film' && cur.sp === 3) {
      cur.on = 1; clearTimers();
      sfx('spg', v.currentTime || 0, 0, true);
      if (cur.u) cur.u.classList.remove('on');
      v.classList.add('on'); const ov = sgdOv(); if (ov) ov.classList.add('go');
      emit('film');
    }
  }
  function onEnded(name) { if (cur && cur.kind === 'spg' && name === 'spg_up' && cur.sp === 2) spgFilm(); }
  function onError(name) { if (cur && cur.phase === 'reveal' && !cur.on && (cur.kind === 'sgd' || cur.kind === 'spg')) sgdStill(); }   // 読めなかったら（どちらの 動画でも）さいごの 1まい ※仮
  function vidHidden() { if (!cur || !(cur.kind === 'sgd' || cur.kind === 'spg')) return; if (cur.on === 1) { [cur.u, cur.v].forEach(x => { if (x) { try { x.pause(); } catch (e) { /* なし */ } } }); } }
  function vidBack() { if (!cur || cur.on !== 1 || !cur.v) return; try { const p = cur.v.play(); if (p && p.catch) p.catch(() => {}); } catch (e) { /* なし */ } }

  // ---------- 出す ----------
  // 舞台（390×844）を 画面に 入る 大きさに（縦横の 比は 変えない・1倍に 近ければ 1倍＝字が ぼけない）※仮
  function fit() { if (!cur) return; let k = Math.min(window.innerWidth / 390, window.innerHeight / 844); if (!isFinite(k) || k <= 0) k = 1; if (Math.abs(k - 1) < .03) k = 1; cur.stage.style.setProperty('--fxk', k.toFixed(4)); }
  // 出る 前に 絵を 読んで おく（プレミアム 38まい・神様 24まい・超神様の さいごの 1まい・動画）
  function preload(kind) {
    const names = kind === 'pc' ? A.art.pm : kind === 'gd' ? A.art.gd : (kind === 'sgd' || kind === 'spg') ? A.art.sgd : [];
    try { names.forEach(f => { const im = new Image(); im.src = f; }); } catch (e) { /* なし */ }
    if (kind === 'sgd' || kind === 'spg') { video('sgd_film'); if (kind === 'spg') video('spg_up'); }
  }
  function open(kind, spec, supers, bigs, quiet) {
    close(true); css();
    const ov = document.createElement('div'); ov.id = 'fxOv'; ov.className = 'k-' + kind + (quiet ? ' quiet' : '');
    ov.setAttribute('role', 'dialog'); ov.setAttribute('aria-modal', 'true'); ov.setAttribute('aria-label', 'レースの結果');
    const stage = document.createElement('div'); stage.className = 'fxs' + (calm() ? ' calm' : '');
    ov.appendChild(stage); document.body.appendChild(ov);
    document.documentElement.classList.add('fxon');
    cur = { kind: kind, spec: spec || {}, supers: supers || [], bigs: bigs || [], ov: ov, stage: stage, quiet: !!quiet, phase: '', theme: null, timers: [], on: 0, sp: 0, u: null, v: null };
    fit(); window.addEventListener('resize', fit);
    try { if (WL() && WL().lockZoom) WL().lockZoom(true); } catch (e) { /* なし */ }
    if (!quiet) preload(kind);
    if (kind === 'miss' || quiet) reveal(); else push();
  }
  function push() {
    if (!cur) return;
    const k = cur.kind, ks = k === 'hit' ? KS() : null;
    cur.theme = ks && ks.push && ks.pc ? ks : null;      // 的中の PUSH はそのテーマの形（16.2.1）。デカ・ど的中・特別な 演出は全テーマ共通
    cur.stage.innerHTML = cur.theme ? A.push.hit_t.split('{{PC}}').join(' ' + cur.theme.pc).replace('{{SVG}}', cur.theme.push.svg) : A.push[FZ_PUSH[k] ? 'fz' : (k === 'hidden' ? 'big' : k)];
    cur.phase = 'push'; cur.ov.classList.remove('rv');
    sfx(SND[k][0]);
    emit('push');
  }
  function reveal() {
    if (!cur || cur.phase === 'reveal') return;
    const k = cur.kind, rows = rowsHTML(cur.spec, k, cur.supers, cur.bigs);
    const th = !cur.quiet && k === 'hit' ? (cur.theme || null) : null;
    const tpl = th ? A.reveal.hit_t.split('{{PC}}').join(' ' + th.pc).replace('{{PRESSED}}', th.push.pressed).replace('{{BURST}}', th.push.burst) : A.reveal[cur.quiet ? 'miss' : (k === 'hidden' ? 'fz' : k)];
    let html = tpl.replace('{{BOARD}}', boardHTML(k, cur.spec, cur.supers, cur.bigs, rows.html)).replace('{{N}}', String(Math.max(1, rows.n)));
    if (cur.quiet) html = html.replace('class="ov miss"', 'class="ov miss quiet"');
    cur.stage.innerHTML = html;
    cur.phase = 'reveal'; cur.ov.classList.add('rv');
    if (!cur.quiet && k !== 'miss') {
      if (k === 'sgd') sgdGo();
      else if (k === 'spg') spgGo();
      else if ((k === 'fz' || k === 'hidden') && calm()) sfx(SND[k][1], A.t.R, 1);           // 控えめ：1秒後に 結果の 所から
      else if ((k === 'pc' || k === 'zp') && calm()) sfx(SND[k][1], A.t.PC, 1);             // 控えめ：1秒後に ボードの 所から ※仮
      else if (k === 'gd' && calm()) sfx(SND[k][1], A.t.GD, 1);
      else sfx(SND[k][1]);
    }
    emit('reveal');
  }
  function close(silent) {
    hush();
    if (!cur) return;
    const c = cur; cur = null;
    c.timers.forEach(clearTimeout);
    park(c.u); park(c.v);
    window.removeEventListener('resize', fit);
    if (c.ov.parentNode) c.ov.parentNode.removeChild(c.ov);
    document.documentElement.classList.remove('fxon');
    try { if (WL() && WL().lockZoom) WL().lockZoom(false); } catch (e) { /* なし */ }
    if (!silent) emit('close', c.kind);
  }
  // 結果を保存したあとに呼ぶ。出した種類を返す（出さないときは null）。force＝種類を決めて出す（テスト・CI用。隠れど的中の数は進めない・くじも ひかない）
  function show(spec) {
    if (!spec) return null;
    const d = decide(spec), quiet = !S.effects;
    let kind = d.kind;
    if (spec.force) kind = spec.force;
    else if (!quiet) {   // 的中エフェクト オフのときは くじを ひかない ※仮
      if (kind === 'big' && rollHidden()) kind = 'hidden';
      else kind = lottery(kind);
    }
    open(kind, spec, d.supers, d.bigs, quiet);
    return kind;
  }
  document.addEventListener('click', e => {
    if (!cur) return;
    const b = e.target.closest ? e.target.closest('[data-fx]') : null;
    if (!b || !cur.ov.contains(b)) return;
    e.preventDefault();
    if (b.dataset.fx === 'tap') reveal(); else if (b.dataset.fx === 'close') close();
  });

  window.TengelFx = {
    on: true, T: A.t, decide: decide, show: show, close: close, prime: prime, get: () => Object.assign({}, S), set: set, calm: calm, reduced: reduced,
    current: () => (cur ? { kind: cur.kind, phase: cur.phase, quiet: cur.quiet, theme: cur.theme ? cur.theme.tid : null, film: cur.on, sp: cur.sp } : null),
    tap: () => { if (cur && cur.phase === 'push') reveal(); }, hidden: hiddenState, lottery: lottery, sfxState: () => ({ ctx: !!SX.ctx, fetched: SX.fetched, playing: !!SX.src, more: SX.more.length }),
    video: video, _rand: null
  };
  css();
  if (TL() && TL().ready) TL().ready.then(loadSettings).catch(loadSettings); else loadSettings();
})();
