// ※ 第4.172版（まさちゃん 2026/11/14 22:05「やっぱりテンゲルBGMも消して！無しでいいや！」）：この ファイルは アプリに 入れて いない（build_pwa.py）。もどす とき の ために 残して ある。
// テンゲルBGM（App Store版・第4.171版：まさちゃん 2026/11/14 16:18
//   「②テンゲルのBGMを考える ・テンゲルBGM(トレーニングセンター、思い出フィギュア、作戦会議、推し馬の画面では流れない)」）
//   判定・記録・実測・設定 などの 画面で、姫の 作った 曲（bgm_tengel9.m4a：kisekae/tc/snd/bgm_tengel.py の tengel9＝第9稿「笛 4本・鳥の 声・馬の 鳴き声と 走る 音・風の 音・笛は もっと ゆっくり」）を 小さな 音で くり返す。
//   第2稿（まさちゃん 11/14 17:49「テンゲルのBGMは、この動画の背景で流れているBGMが理想！まずは、同じやつを作ってみて！その後、アレンジしよう！」）：動画の 曲（ほかの 人の 曲）と
//     同じ ものは 作らない。ふんいき（ゆったり・あたたかい・笛と 弦と 低い 太鼓）だけを もらった 姫の 曲（ふし・和音・リズムは 新しく 作った もの）
//   第3稿（18:49「BGMもっとゆっくりで、鳥の声や笛の音入れて！」）：116 → 88 BPM・ふしは 息の 入った 笛・鳥の 声（計算で 作った 声）
//   第4稿（19:09「一回、鳥の声と笛の音だけにしてみて！もっとゆったりで！」）：笛 1本 と 鳥の 声 だけ（太鼓・弦・ベースは なし）・60 BPM・笛が 休む 間に 鳥が 鳴き交わす
//   第5稿（19:25「ここに馬の走る音と、もう少し太い音の笛を混ぜて！ゆったりね！」）：第4稿 ＋ 太い 音の 笛（低い 所で ふし・ハモリ）＋ 馬の 走る 音（ゆったりした かけ足が 通りすぎる：2回）。速さ・長さは 第4稿と 同じ
//   第6稿（19:41「もう一段階太い笛と、かなり音が低い笛も重ねて音入れて！」・19:42「馬の鳴き声と、馬が走る音追加して！」）：第5稿 ＋ もう 一段階 太い 笛 ＋ かなり 低い 笛（笛 4本）＋ 馬の 鳴き声（2回）＋ 走る 音を 足す（休みごとに 馬が 通る）
//   第7稿（19:57「この笛を、バイオリンぽくできる？」）：4本を 弓で ひく 弦の 音に（聞く 用の 見本 だけ・アプリには 入れて いない）
//   第8稿（20:12「ごめん！笛に戻して！もっとゆったりで！」・20:15「あと風の音も入れて！」）：第6稿の 笛に もどす・60 → 48 BPM（1回り 64 → 80秒）・風の 音（休みごとに ひと吹き ＋ うしろで ごく 小さく）
//   第9稿（20:27「もっと笛の音ゆっくりして！」）：48 → 36 BPM（1回り 80 → 約106.7秒）・笛の 吹き方も ゆっくり（かざりの 音なし・音の 移り変わりを なめらかに）
//   ・流さない 所：トレーニングセンター（#tcOv.on）・思い出フィギュア（#fgOv.on）・作戦会議と 推し馬（TCPlan.isOpen()）・的中の 演出の 間（html.fxon：演出の 音と 重ねない）・
//     アプリが うしろに いる 間 → 0.45秒で 消える・もどったら 1.2秒で つづきから（曲の 頭に もどらない）
//   ・設定の「BGM」で オン／オフ（localStorage 'tengel.bgm'：'1'／'0'。決めて いない ときは オン）。
//     消音スイッチ（マナーモード）なら 鳴らない・ほかの アプリの 音楽は 止めない（navigator.audioSession.type＝'ambient'：的中の 演出の 音と 同じ きまり）。
//     その きまりを アプリから 決められない 古い iOS（16.0〜16.3）では、念のため 決めて いない ときは オフ（設定で オンに すれば 鳴る）
//   ・ファイルは くり返す 1回り（16小節・36 BPM・約106.7秒）の 前と うしろに 0.5秒ずつ 同じ 音の つづきが 入って いる（kisekae/tc/snd/export_app.py）
//     → まん中の 1回り だけを くり返す（つなぎ目で リズムが とばない：トレーニングセンターの ルーレットの BGM と 同じ 形）
//   ・メモリ：ほどいた 音は 約38MB（約107.7秒・44.1kHz・ステレオ）。トレーニングセンター・思い出フィギュア（3D の 画面）に 入って 20秒 たったら 手ばなす（もどった ときに ほどき直す）。オフの 間は 持たない
//   ・音の ファイルが ない（手元に 素材の ない ビルド・GitHub の Mac）ときは 何も 鳴らさない
//   window.TengelBgm：{ get()・set(on)・state()・sync() }。設定の 札は src.html の bgmCard
(() => {
  'use strict';
  if (window.TengelBgm) return;
  const FILE = 'bgm_tengel9.m4a', KEY = 'tengel.bgm';
  const PRE = 0.5; let LEN = 16 * 4 * 60 / 36;              // ファイルの 形：前後の つづき（秒）・くり返す 1回り（秒：16小節・36 BPM＝約106.7秒）
  const FIN = 1.2, FOUT = 0.45, TICK = 200, DROP = 20000;   // 入る・消える（秒）・画面を 見に 行く 間隔・3D の 画面で 手ばなす まで（ミリ秒）
  const AS = (() => { try { return !!(navigator.audioSession && 'type' in navigator.audioSession); } catch (e) { return false; } })();
  let ac = null, cur = null, raw = null, buf = null, dec = null, tau = 0, gone = false, heavyAt = 0, asSet = false, idleAt = 0;

  function get() { let v = null; try { v = localStorage.getItem(KEY); } catch (e) { /* なし */ } return v === '1' || (v !== '0' && AS); }
  const heavy = () => !!document.querySelector('#tcOv.on, #fgOv.on');
  const plan = () => { try { return !!(window.TCPlan && typeof window.TCPlan.isOpen === 'function' && window.TCPlan.isOpen()); } catch (e) { return false; } };
  const quiet = () => document.hidden || heavy() || plan() || document.documentElement.classList.contains('fxon');
  function ctx() {
    if (!ac) { const AC = window.AudioContext || window.webkitAudioContext; if (!AC) return null; try { ac = new AC(); } catch (e) { ac = null; } }
    return ac;
  }
  // 音を 読んで ほどく（1回 だけ。ファイルが ない・こわれて いる ときは gone）
  function load() {
    if (buf || gone) return Promise.resolve(buf);
    if (dec) return dec;
    const c = ctx(); if (!c || typeof fetch !== 'function') return Promise.resolve(null);
    if (!raw) raw = fetch(FILE, { cache: 'force-cache' }).then(r => (r.ok ? r.arrayBuffer() : null)).catch(() => null);
    dec = raw.then(b => {
      if (!b) return null;
      return new Promise(ok => { try { const q = c.decodeAudioData(b.slice(0), ok, () => ok(null)); if (q && q.catch) q.catch(() => ok(null)); } catch (e) { ok(null); } });
    }).then(b => {
      dec = null;
      if (b && b.duration > 4 * PRE) { if (Math.abs(b.duration - (LEN + 2 * PRE)) > 0.25) LEN = b.duration - 2 * PRE; buf = b; }      // 長さが 決めごとと ちがう ファイル（曲を 入れかえた とき）は、前後 0.5秒を のぞいた 長さを 1回りに する
      else gone = true;
      return buf;
    });
    return dec;
  }
  const pos = () => (cur && ac ? (tau + Math.max(0, ac.currentTime - cur.t0)) % LEN : tau);      // 曲の 中の いまの 所（秒：0〜LEN）
  function start() {
    const c = ac; if (!c || cur || !buf) return;
    try {
      const s = c.createBufferSource(), g = c.createGain(), n = c.currentTime;
      s.buffer = buf; s.loop = true; s.loopStart = PRE / 2; s.loopEnd = PRE / 2 + LEN;
      let off = PRE + tau; if (off >= PRE / 2 + LEN) off -= LEN;
      g.gain.setValueAtTime(0, n); g.gain.linearRampToValueAtTime(1, n + FIN);
      s.connect(g); g.connect(c.destination); s.start(0, off); cur = { s, g, t0: n };
    } catch (e) { cur = null; }
  }
  function stop(fade) {
    if (!cur || !ac) return;
    const o = cur, n = ac.currentTime; tau = pos(); cur = null;
    try { o.g.gain.cancelScheduledValues(n); o.g.gain.setValueAtTime(o.g.gain.value, n); o.g.gain.linearRampToValueAtTime(0, n + fade); o.s.stop(n + fade + 0.05); }
    catch (e) { try { o.s.stop(); } catch (e2) { /* もう 止まって いる */ } }
    setTimeout(() => { try { o.s.disconnect(); o.g.disconnect(); } catch (e) { /* なし */ } }, (fade + 0.2) * 1000);
  }
  // 鳴らして いない 間が 1秒 つづいたら、音の 出口を 休ませる（電池）。鳴らす ときに 起こす
  function rest() {
    if (!ac || cur || ac.state !== 'running') { idleAt = 0; return; }
    if (!idleAt) idleAt = Date.now(); else if (Date.now() - idleAt > 1000) { idleAt = 0; try { const p = ac.suspend(); if (p && p.catch) p.catch(() => {}); } catch (e) { /* なし */ } }
  }
  // いまの 画面と 設定に 合わせる（0.2秒ごと・タップ・画面が もどった とき）
  function sync() {
    if (!get()) { stop(0.2); buf = null; rest(); return; }
    if (quiet()) {
      stop(document.hidden ? 0.05 : FOUT); rest();
      if (heavy()) { if (!heavyAt) heavyAt = Date.now(); else if (buf && Date.now() - heavyAt > DROP) buf = null; } else heavyAt = 0;
      return;
    }
    heavyAt = 0; idleAt = 0;
    if (gone) return;
    if (AS && !asSet) { asSet = true; try { navigator.audioSession.type = 'ambient'; } catch (e) { /* 使えない iOS */ } }      // 音の 出口を 作る 前に 決めて おく
    const c = ctx(); if (!c) return;
    if (c.state !== 'running' && c.resume) { try { const p = c.resume(); if (p && p.catch) p.catch(() => {}); } catch (e) { /* なし */ } }
    if (cur) return;
    if (!buf) { load().then(b => { if (b) sync(); }); return; }
    if (c.state === 'running') start();
  }
  function set(on) {
    try { localStorage.setItem(KEY, on ? '1' : '0'); } catch (e) { /* なし */ }
    sync();
    try { document.dispatchEvent(new CustomEvent('tengel:bgm', { detail: { on: !!on } })); } catch (e) { /* なし */ }
  }
  const state = () => ({ on: get(), quiet: quiet(), playing: !!cur, ctx: ac ? ac.state : null, loaded: !!buf, gone, pos: pos(), len: LEN, file: FILE, ambient: AS });

  setInterval(sync, TICK);
  ['pointerdown', 'touchend', 'keydown'].forEach(ev => document.addEventListener(ev, sync, { capture: true, passive: true }));
  document.addEventListener('visibilitychange', sync);
  window.addEventListener('pagehide', () => stop(0.05));
  window.TengelBgm = { get, set, state, sync };
  sync();
})();
