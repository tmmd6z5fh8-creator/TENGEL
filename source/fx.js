// 的中ボタン（App Store版 第3弾：アップデート指示書 10章・16.2〜16.6）
//   結果を保存したあとに 1つだけ出す（強い順）：ど的中（3連単の当たりの3頭に 超大穴＝10〜12番人気）＞ デカ的中（3連単の当たり）＞ 的中（ほかの当たり）／当たりなし＝ハズレ（ボードだけ・音なし）
//   隠れど的中＝デカ的中の 2〜7回に1回（ランダム。数は端末の中だけ：記録・バックアップには入れない）→ 見た目はデカの PUSH・押すと ど的中の演出
//   流れ：PUSH（上下に動く）→ タップ → 演出 → いつものボード（券種ごとの 結果・お金は出さない：16.4）→「とじる」
//   見本（kisekae/gen_fx.py・boards.py）の CSS と HTML は kisekae/build_fx.py が window.__FX に束ねる。舞台は 390×844 を画面に合わせて縮める（16.3 ※仮）
//   音：kisekae/gen_sfx.py の音（m4a・アプリの中のファイル）を Web Audio で。「結果を保存」を押したときに準備する（iPhone は押す操作の中でないと鳴らないことがある）
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
  const HIDDEN_KEY = 'tengel.fxhidden';   // 隠れど的中の数（端末の中だけ）
  const SETTING = 'fx';
  // PUSHが出たときの音・押したときの音（隠れど的中：PUSHはデカの音・押すとど的中の音）
  const SND = { hit: ['hit_push', 'hit'], big: ['big_push', 'big'], fz: ['fz_push', 'fz'], hidden: ['big_push', 'fz'] };
  let S = { effects: true, calm: null, sound: true };
  let cur = null;

  // ---------- CSS（見本の CSS を .fxs の中だけに効かせたもの） ----------
  function css() {
    if ($('#fxCss')) return;
    const st = document.createElement('style'); st.id = 'fxCss';
    st.textContent = A.css + '\n.fxs .ov.quiet .bh,.fxs .ov.quiet .zrib,.fxs .ov.quiet .n.zx,.fxs .ov.quiet .brows li.top::after{animation:none!important}\n';
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
  function decide(spec) {
    const rows = (spec && spec.rows) || [];
    if (!rows.some(x => x.state === '的中')) return { kind: 'miss', supers: [] };
    const tri = rows.find(x => x.t === '3連単' && x.state === '的中');
    if (!tri) return { kind: 'hit', supers: [] };
    const ranks = (spec && spec.ranks) || {}, supers = [];
    (tri.hits || []).forEach(c => {
      const rs = c.map(no => (ranks[no] == null ? null : +ranks[no]));
      if (rs.some(v => v == null || !isFinite(v))) return;      // 人気がわからない馬がいる組は ど的中にしない（デカ）※仮
      c.forEach((no, i) => { if (rs[i] >= SUPER[0] && rs[i] <= SUPER[1] && !supers.some(s => s.no === +no)) supers.push({ no: +no, rank: rs[i] }); });
    });
    return { kind: supers.length ? 'fz' : 'big', supers: supers };
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

  // ---------- ボード（いつもの・お金なし） ----------
  function num(no, n, zx, isWaku) {
    const w = isWaku ? Math.min(Math.max(+no || 1, 1), 8) : (RS() ? RS().waku(+no, +n || 0) : Math.min(+no || 1, 8));
    return `<span class="n w${w}${zx ? ' zx' : ''}">${esc(no)}</span>`;
  }
  function combo(c, t, n, mark) {
    const ordered = !!(RS() && RS().ORDERED[t]) || t === '馬単' || t === '枠単' || t === '3連単', isWaku = t === '枠複' || t === '枠単';
    return `<span class="bc">${c.map(no => num(no, n, mark.indexOf(+no) >= 0, isWaku)).join(`<span class="ar">${ordered ? '→' : '-'}</span>`)}</span>`;
  }
  // 行：予約した券種ごとに 1行（9つまで）。デカ・ど的中・隠れど的中は 3連単の行をいちばん上。当たった組番は 3つまで＋「ほか○点」。当たりのない券種は組番なし・うすく
  function rowsHTML(spec, kind, supers) {
    let rows = ((spec && spec.rows) || []).slice();
    if (kind !== 'hit' && kind !== 'miss') rows.sort((a, b) => (b.t === '3連単' ? 1 : 0) - (a.t === '3連単' ? 1 : 0));
    rows = rows.slice(0, 9);
    const mark = (supers || []).map(s => s.no), n = spec && spec.n;
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
    const t = A.board.titles[kind] || '', head = t.slice(0, -1), last = t.slice(-1);
    const h = t.endsWith('！！！') ? esc(head.slice(0, -2)) + '<span class="bx3">！！</span>' : esc(head);
    return `${h}<span class="bz${last === '！' ? ' bzx' : ''}">${esc(last)}</span>`;
  }
  function boardHTML(kind, spec, supers, rows) {
    const k = kind === 'hidden' ? 'fz' : kind;
    const sub = `${esc(spec && spec.r != null ? spec.r : '')}R の券種ごとの結果`;
    let rib = '';
    if (kind === 'hidden') rib = '<div class="zrib"><b class="zt">隠れ</b><span>デカ的中が ど的中に化けた！</span></div>';
    else if (kind === 'fz' && supers && supers.length) rib = `<div class="zrib"><b class="zt">超大穴</b>${supers.map(s => num(s.no, spec && spec.n, true)).join('')}<span>${supers.map(s => esc(s.rank) + '番人気').join('・')}が3連単に！</span></div>`;
    const ks = KS(), tid = ks ? ks.tid : 'default', orn = ks ? ks.orn : A.board.orn;   // ボードはそのテーマの形（16.4）。CSS は kisekae.js が入れる
    return `<div class="rb ${k} t-${tid}"><div class="hd"><div class="bh${kind === 'miss' ? '' : ' logo'}">${titleHTML(kind)}</div><div class="bsub">${sub}</div>${rib}</div><div class="card">${orn}<ul class="brows">${rows}</ul></div></div>`;
  }

  // ---------- 音（Web Audio：先に読んで、押した瞬間を0秒にして動きとそろえる） ----------
  const SX = { raw: {}, buf: {}, ctx: null, src: null, id: 0, fetched: false, ok: 0 };
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
  // 「結果を保存」を押したとき（押す操作の中）に呼ぶ：音の準備（消音スイッチなら鳴らさない＝ambient）・ネオンの絵の先読み
  function prime() {
    try { if (navigator.audioSession && 'type' in navigator.audioSession) navigator.audioSession.type = 'ambient'; } catch (e) { /* 使えないiOS */ }
    fetchAll();
    try { Object.keys(A.assets).forEach(k => { const im = new Image(); im.src = A.assets[k]; }); } catch (e) { /* なし */ }
    if (!S.sound) return false;
    const c = actx(); if (!c) return false;
    if (!SX.ok) { SX.ok = 1; try { const s0 = c.createBufferSource(); s0.buffer = c.createBuffer(1, 1, 22050); s0.connect(c.destination); s0.start(0); } catch (e) { /* なし */ } }
    Object.keys(SX.raw).forEach(k => bufOf(c, k));
    return true;
  }
  // 音 k を、いまを0秒として from 秒の所から wait 秒後に鳴らす（読むのが0.1秒より遅れたら、遅れたぶん先から鳴らして動きとそろえる）
  function sfx(k, from, wait) {
    hush();
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
      SX.src = s;
    });
  }
  function hush() { SX.id++; if (SX.src) { try { SX.src.stop(); } catch (e) { /* もう止まっている */ } SX.src = null; } }
  document.addEventListener('visibilitychange', () => { if (document.hidden) hush(); });
  window.addEventListener('pagehide', hush);

  // ---------- 出す ----------
  // 舞台（390×844）を 画面に 入る 大きさに（縦横の 比は 変えない・1倍に 近ければ 1倍＝字が ぼけない）※仮
  function fit() { if (!cur) return; let k = Math.min(window.innerWidth / 390, window.innerHeight / 844); if (!isFinite(k) || k <= 0) k = 1; if (Math.abs(k - 1) < .03) k = 1; cur.stage.style.setProperty('--fxk', k.toFixed(4)); }
  function open(kind, spec, supers, quiet) {
    close(true); css();
    const ov = document.createElement('div'); ov.id = 'fxOv'; ov.className = 'k-' + kind + (quiet ? ' quiet' : '');
    ov.setAttribute('role', 'dialog'); ov.setAttribute('aria-modal', 'true'); ov.setAttribute('aria-label', 'レースの結果');
    const stage = document.createElement('div'); stage.className = 'fxs' + (calm() ? ' calm' : '');
    ov.appendChild(stage); document.body.appendChild(ov);
    document.documentElement.classList.add('fxon');
    cur = { kind: kind, spec: spec || {}, supers: supers || [], ov: ov, stage: stage, quiet: !!quiet, phase: '', theme: null };
    fit(); window.addEventListener('resize', fit);
    try { if (WL() && WL().lockZoom) WL().lockZoom(true); } catch (e) { /* なし */ }
    if (kind === 'miss' || quiet) reveal(); else push();
  }
  function push() {
    if (!cur) return;
    const k = cur.kind, ks = k === 'hit' ? KS() : null;
    cur.theme = ks && ks.push && ks.pc ? ks : null;      // 的中の PUSH はそのテーマの形（16.2.1）。デカ・ど的中は全テーマ共通
    cur.stage.innerHTML = cur.theme ? A.push.hit_t.split('{{PC}}').join(' ' + cur.theme.pc).replace('{{SVG}}', cur.theme.push.svg) : A.push[k === 'hidden' ? 'big' : k];
    cur.phase = 'push'; cur.ov.classList.remove('rv');
    sfx(SND[k][0]);
    emit('push');
  }
  function reveal() {
    if (!cur || cur.phase === 'reveal') return;
    const k = cur.kind, rows = rowsHTML(cur.spec, k, cur.supers);
    const th = !cur.quiet && k === 'hit' ? (cur.theme || null) : null;
    const tpl = th ? A.reveal.hit_t.split('{{PC}}').join(' ' + th.pc).replace('{{PRESSED}}', th.push.pressed).replace('{{BURST}}', th.push.burst) : A.reveal[cur.quiet ? 'miss' : (k === 'hidden' ? 'fz' : k)];
    let html = tpl.replace('{{BOARD}}', boardHTML(k, cur.spec, cur.supers, rows.html)).replace('{{N}}', String(Math.max(1, rows.n)));
    if (cur.quiet) html = html.replace('class="ov miss"', 'class="ov miss quiet"');
    cur.stage.innerHTML = html;
    cur.phase = 'reveal'; cur.ov.classList.add('rv');
    if (!cur.quiet && k !== 'miss') { if ((k === 'fz' || k === 'hidden') && calm()) sfx(SND[k][1], A.t.R, 1); else sfx(SND[k][1]); }
    emit('reveal');
  }
  function close(silent) {
    hush();
    if (!cur) return;
    const c = cur; cur = null;
    window.removeEventListener('resize', fit);
    if (c.ov.parentNode) c.ov.parentNode.removeChild(c.ov);
    document.documentElement.classList.remove('fxon');
    try { if (WL() && WL().lockZoom) WL().lockZoom(false); } catch (e) { /* なし */ }
    if (!silent) emit('close', c.kind);
  }
  // 結果を保存したあとに呼ぶ。出した種類を返す（出さないときは null）。force＝種類を決めて出す（テスト・CI用。隠れど的中の数は進めない）
  function show(spec) {
    if (!spec) return null;
    const d = decide(spec), quiet = !S.effects;
    let kind = d.kind;
    if (spec.force) kind = spec.force;
    else if (kind === 'big' && !quiet && rollHidden()) kind = 'hidden';   // 的中エフェクト オフのときは くじを ひかない ※仮
    open(kind, spec, d.supers, quiet);
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
    current: () => (cur ? { kind: cur.kind, phase: cur.phase, quiet: cur.quiet, theme: cur.theme ? cur.theme.tid : null } : null), tap: () => { if (cur && cur.phase === 'push') reveal(); }, hidden: hiddenState, sfxState: () => ({ ctx: !!SX.ctx, fetched: SX.fetched, playing: !!SX.src }), _rand: null
  };
  css();
  if (TL() && TL().ready) TL().ready.then(loadSettings).catch(loadSettings); else loadSettings();
})();
