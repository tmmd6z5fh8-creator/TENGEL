// 思い出フィギュア（App Store版）：ブース・一覧・部屋・作る 画面（まさちゃん 2026/11/09）
//   「思い出レースをフィギュアにする」：思い出の レースを 選ぶ → 8種の デザインを 選ぶ → 3D で 見て → ポイントで 作る（ボードに その レースを 書く）
//   「フィギュアブース」：7つの ブース（棚の 色 7種）× 8こ ＝ 56こ まで 飾れる。飾る 場所は 選べる・長押しで 場所を かえる・押すと 3D の 部屋で 見る
//   「一覧」：7つの ブースを いっぺんに 見る
//   値段（まさちゃん 11/09 20:34）：通常 22,000P・幻の馬 30,000P・神様馬 32,000P・幻の馬＆神様馬 36,000P
//   保存：台帳（TengelWallet.fig：作った フィギュアと 飾る 場所）＝ この 端末の 中・自動バックアップにも 入る
const FigApp = (() => {
  'use strict';
  const PAGES = 7, PER = 8, MAX = PAGES * PER;
  const NAMES = ['', 'ロイヤルポニー', 'ゴールデンスカラー', 'フローラルゴールド', 'ロイヤルゴールデン', 'ロイヤルフォーチュン', '神様馬', '幻の馬', '幻の馬＆神様馬'];
  const KIND = ['', 'normal', 'normal', 'normal', 'normal', 'normal', 'kami', 'mab', 'both'];
  const PRICE = { normal: 22000, mab: 30000, kami: 32000, both: 36000 };
  const KIND_JA = { normal: '', mab: '幻の馬', kami: '神様馬', both: '幻の馬＆神様馬' };
  const PK = 'tengel.figpage';
  const WL = () => window.TengelWallet, MEM = () => window.TengelMem;
  const nf = n => Math.round(+n || 0).toLocaleString('ja-JP');
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const circ = n => '①②③④⑤⑥⑦⑧'.charAt(n - 1) || String(n);
  const priceOf = n => PRICE[KIND[n]] || PRICE.normal;
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));

  // ---------- データ（台帳の コピー）----------
  let items = [], slots = Array(MAX).fill(null);
  function sync() { const w = WL(); if (w && w.fig) { items = w.fig.items(); slots = w.fig.slots(); } }
  const itemOf = id => items.find(x => x.id === id) || null;
  const slotOf = id => slots.indexOf(id);
  const onPage = p => { const out = []; for (let i = 0; i < PER; i++) { const it = itemOf(slots[p * PER + i]); if (it) out.push({ slot: i, it }); } return out; };
  const stored = () => items.filter(x => slotOf(x.id) < 0);
  async function saveSlots(next) { const w = WL(); if (!w || !w.fig) return; slots = await w.fig.place(next); sync(); }

  // ---------- 画面 ----------
  const css = `
#fgOv{position:fixed;inset:0;z-index:90;display:none;flex-direction:column;background:radial-gradient(130% 75% at 50% 32%,#2c1d12 0%,#140d08 58%,#070403 100%);color:#f6ead2;padding-top:env(safe-area-inset-top);padding-bottom:env(safe-area-inset-bottom);font-family:"BIZ UDPGothic","Hiragino Sans",sans-serif;-webkit-user-select:none;user-select:none;-webkit-touch-callout:none;-webkit-tap-highlight-color:transparent}
#fgOv.on{display:flex}
#fgOv button{font-family:inherit;-webkit-tap-highlight-color:transparent}
#fgOv .fgh{flex:none;height:56px;width:100%;max-width:640px;margin:0 auto;box-sizing:border-box;display:flex;align-items:center;gap:8px;padding:6px 10px}
#fgOv .fgbtn{flex:none;height:38px;min-width:64px;padding:0 12px;border-radius:19px;border:1.5px solid #c9a35a;background:#fff8ec;color:#5c3714;font-weight:700;font-size:14px;line-height:1}
#fgOv .fgbtn:active{transform:scale(.96)}
#fgOv .fgbtn[hidden]{display:inline-block!important;visibility:hidden}
#fgOv .fgt{flex:1 1 auto;min-width:0;text-align:center;line-height:1.25}
#fgOv .fgt b{display:block;font-size:16px;color:#ffe2a0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;letter-spacing:.04em}
#fgOv .fgt span{display:block;font-size:12px;color:#cdb68c;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#fgOv .fgwr{position:relative;flex:1 1 auto;min-height:0;width:100%;max-width:640px;margin:0 auto;overflow:hidden}
#fgOv .fgst{position:absolute;inset:0;touch-action:none;will-change:transform}
#fgOv .fgst canvas{position:absolute;left:0;top:0;width:100%;height:100%;display:block}
#fgOv .fgst.room{background:radial-gradient(90% 60% at 50% 42%,rgba(255,214,150,.16),rgba(0,0,0,0) 70%)}
#fgOv .fgsl{position:absolute;inset:0;pointer-events:none}
#fgOv .fgs{position:absolute;pointer-events:none;border:0;padding:0;margin:0;background:transparent;border-radius:8px;display:flex;align-items:center;justify-content:center}
#fgOv .fgs:focus-visible{outline:2px solid #ffd27a}
#fgOv .fgs .pl{width:30px;height:30px;border-radius:50%;border:1.5px solid rgba(255,236,200,.45);color:rgba(255,236,200,.6);font-size:20px;line-height:26px;text-align:center;box-sizing:border-box}
#fgOv .fgs.has .pl{display:none}
#fgOv.pick .fgs.empty{background:rgba(255,210,120,.10);box-shadow:inset 0 0 0 2px rgba(255,214,130,.65)}
#fgOv.pick .fgs.empty .pl{border-color:#ffd27a;color:#ffd27a;background:rgba(40,24,8,.5)}
#fgOv .fgs.sel{box-shadow:inset 0 0 0 3px #ffd27a,0 0 18px rgba(255,200,90,.55);animation:fgpl 1.1s ease-in-out infinite alternate}
@keyframes fgpl{from{box-shadow:inset 0 0 0 3px #ffd27a,0 0 10px rgba(255,200,90,.35)}to{box-shadow:inset 0 0 0 3px #fff0c0,0 0 22px rgba(255,200,90,.7)}}
#fgOv .fgld{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;color:#f0dcb4;font-size:14px;pointer-events:none}
#fgOv .fgld[hidden]{display:none}
#fgOv .fgld i{width:26px;height:26px;border-radius:50%;border:3px solid rgba(255,226,160,.25);border-top-color:#ffd27a;animation:fgsp .9s linear infinite}
@keyframes fgsp{to{transform:rotate(360deg)}}
#fgOv .fgpn{position:absolute;inset:0;overflow:auto;-webkit-overflow-scrolling:touch;padding:6px 14px 18px;box-sizing:border-box;background:inherit}
#fgOv .fgpn[hidden]{display:none}
#fgOv .fgf{flex:none;width:100%;max-width:640px;margin:0 auto;box-sizing:border-box;padding:6px 12px 10px}
#fgOv .fgpg{display:flex;align-items:center;justify-content:center;gap:12px;height:34px}
#fgOv .fgpg button{width:40px;height:32px;border-radius:16px;border:1px solid rgba(255,226,160,.4);background:rgba(255,248,236,.08);color:#ffe2a0;font-size:20px;line-height:1}
#fgOv .fgpg button:disabled{opacity:.3}
#fgOv .fgdots{display:flex;gap:7px}#fgOv .fgdots i{width:7px;height:7px;border-radius:50%;background:rgba(255,236,200,.28)}#fgOv .fgdots i.on{background:#ffd27a;box-shadow:0 0 6px rgba(255,210,120,.8)}
#fgOv .fgrow{display:flex;gap:8px;margin-top:6px}
#fgOv .fgrow button{flex:1 1 0;min-height:44px;border-radius:14px;border:1.5px solid #c9a35a;background:#fff8ec;color:#5c3714;font-weight:700;font-size:14.5px;padding:6px 8px;line-height:1.25}
#fgOv .fgrow button.pri{background:linear-gradient(180deg,#ffe39a,#e2a83e);border-color:#f7d27c;color:#3a2206}
#fgOv .fgrow button.dk{background:rgba(255,248,236,.08);color:#f6ead2;border-color:rgba(255,226,160,.45)}
#fgOv .fgrow button:disabled{opacity:.45}
#fgOv .fgpick{text-align:center;font-weight:700;color:#ffe2a0;font-size:14.5px;margin-top:2px}#fgOv .fgpick small{display:block;font-weight:400;color:#cdb68c;font-size:12px}
#fgOv .fginfo{text-align:center;line-height:1.45;padding:2px 4px}
#fgOv .fginfo .k{display:inline-block;font-size:11.5px;font-weight:700;color:#3a2206;background:linear-gradient(180deg,#ffe39a,#e2a83e);border-radius:9px;padding:1px 9px;margin-bottom:3px}
#fgOv .fginfo b{display:block;font-size:15px;color:#fff1cf;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#fgOv .fginfo small{display:block;font-size:12px;color:#cdb68c}
#fgOv .fghint{text-align:center;font-size:11.5px;color:#a8946f;margin-top:4px}
#fgOv .fgmsg{position:absolute;left:50%;top:42%;transform:translate(-50%,-50%);z-index:5;background:#fff8ec;border:2px solid #e2c48e;border-radius:16px;padding:14px 18px;color:#5c3714;font-weight:700;font-size:15.5px;line-height:1.5;text-align:center;box-shadow:0 8px 24px rgba(0,0,0,.45);max-width:82%;white-space:pre-line;pointer-events:none;opacity:0;transition:opacity .25s}
#fgOv .fgmsg.on{opacity:1}
#fgOv .fgsh{position:absolute;left:0;right:0;bottom:0;z-index:4;max-height:72%;display:flex;flex-direction:column;background:#1d140d;border-top:1.5px solid #c9a35a;border-radius:18px 18px 0 0;box-shadow:0 -10px 30px rgba(0,0,0,.5);padding:12px 14px calc(12px + env(safe-area-inset-bottom));box-sizing:border-box;transform:translateY(105%);transition:transform .22s ease-out}
#fgOv .fgsh.on{transform:none}
#fgOv .fgsh h3{margin:0 0 8px;font-size:15px;color:#ffe2a0;display:flex;align-items:center;gap:8px}#fgOv .fgsh h3 span{flex:1}
#fgOv .fgsh h3 button{height:32px;padding:0 12px;border-radius:16px;border:1px solid rgba(255,226,160,.5);background:transparent;color:#f6ead2;font-weight:700}
#fgOv .fgsl2{overflow:auto;-webkit-overflow-scrolling:touch;display:grid;gap:8px}
#fgOv .fgsr{display:flex;align-items:center;gap:10px;width:100%;text-align:left;border:1px solid rgba(255,226,160,.3);background:rgba(255,248,236,.06);border-radius:12px;padding:8px 10px;color:#f6ead2}
#fgOv .fgsr img{width:56px;height:56px;object-fit:contain;flex:none;filter:drop-shadow(0 2px 3px rgba(0,0,0,.5))}
#fgOv .fgsr span{min-width:0;flex:1}#fgOv .fgsr b{display:block;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}#fgOv .fgsr small{display:block;font-size:12px;color:#cdb68c;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#fgOv .fgsr em{font-style:normal;flex:none;font-size:12.5px;font-weight:700;color:#3a2206;background:linear-gradient(180deg,#ffe39a,#e2a83e);border-radius:12px;padding:5px 10px}
#fgOv .fgempty{text-align:center;color:#cdb68c;font-size:13.5px;line-height:1.7;padding:18px 6px}
#fgOv .fgov{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px 10px;padding-top:4px}
#fgOv .fgoc{border:0;background:none;padding:0;color:#f6ead2;display:flex;flex-direction:column;align-items:center;gap:3px}
#fgOv .fgoc canvas{width:100%;aspect-ratio:300/388;height:auto;display:block;border-radius:4px;background:radial-gradient(circle at 50% 40%,rgba(255,220,160,.08),rgba(0,0,0,0) 70%)}
#fgOv .fgoc.cur canvas{box-shadow:0 0 0 2px #ffd27a}
#fgOv .fgoc b{font-size:12.5px}#fgOv .fgoc small{font-size:11px;color:#cdb68c}
#fgOv .fgos{border:1.5px solid rgba(255,226,160,.45);border-radius:14px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;padding:10px 4px;text-align:center;align-self:stretch}
#fgOv .fgos span{font-size:12px;color:#cdb68c}#fgOv .fgos b{font-family:"Dela Gothic One","Hiragino Sans",sans-serif;font-weight:400;font-size:24px;color:#ffe2a0}#fgOv .fgos small{font-size:11.5px;color:#cdb68c}
#fgOv .fgmk h3{font-size:14.5px;color:#ffe2a0;margin:6px 0 8px}
#fgOv .fgmk .lead{font-size:12.5px;color:#cdb68c;margin:0 0 10px;line-height:1.6}
#fgOv .fgrace{display:block;width:100%;text-align:left;border:1px solid rgba(255,226,160,.32);background:rgba(255,248,236,.06);border-radius:12px;padding:9px 12px;margin:0 0 8px;color:#f6ead2}
#fgOv .fgrace .k{font-size:11.5px;font-weight:700;color:#3a2206;background:linear-gradient(180deg,#ffe39a,#e2a83e);border-radius:9px;padding:1px 8px;margin-right:6px}
#fgOv .fgrace b{display:block;font-size:14.5px;margin-top:3px}#fgOv .fgrace small{display:block;font-size:12px;color:#cdb68c;margin-top:1px}
#fgOv .fgsel{border:1px solid rgba(255,226,160,.4);border-radius:12px;padding:8px 12px;margin:0 0 10px;background:rgba(255,248,236,.05);font-size:12.5px;color:#cdb68c;line-height:1.5}#fgOv .fgsel b{color:#fff1cf;font-size:14px}
#fgOv .fgdg{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
#fgOv .fgd{border:1px solid rgba(255,226,160,.35);background:radial-gradient(circle at 50% 38%,rgba(255,220,160,.16),rgba(255,248,236,.03) 70%);border-radius:14px;padding:8px 6px 9px;color:#f6ead2;display:flex;flex-direction:column;align-items:center;gap:3px}
#fgOv .fgd img{height:118px;max-width:100%;object-fit:contain;filter:drop-shadow(0 4px 6px rgba(0,0,0,.55))}
#fgOv .fgd b{font-size:13px;white-space:nowrap}#fgOv .fgd .pr{font-family:"Dela Gothic One","Hiragino Sans",sans-serif;font-size:15px;color:#ffe2a0}
#fgOv .fgd .kd{font-size:10.5px;font-weight:700;border-radius:8px;padding:1px 7px;color:#fff}
#fgOv .fgd .kd.mab{background:#7d2590}#fgOv .fgd .kd.kami{background:#b8862a}#fgOv .fgd .kd.both{background:linear-gradient(90deg,#7d2590,#b8862a)}
#fgOv .fgbuy{text-align:center;font-size:13px;color:#cdb68c;line-height:1.5}#fgOv .fgbuy b{color:#ffe2a0;font-size:15px}#fgOv .fgbuy .ng{color:#ff9d8a;font-weight:700}
@media (prefers-reduced-motion: reduce){#fgOv .fgs.sel{animation:none}#fgOv .fgsh{transition:none}}
`;
  let ov = null, stg = null, cv = null, slEl = null, pn = null, ft = null, ldEl = null, sh = null, R = null, built = false;
  function build() {
    if (built) return; built = true;
    const s = document.createElement('style'); s.id = 'fgCss'; s.textContent = css; document.head.appendChild(s);
    ov = document.createElement('div'); ov.id = 'fgOv'; ov.setAttribute('role', 'dialog'); ov.setAttribute('aria-modal', 'true'); ov.setAttribute('aria-label', '思い出フィギュア');
    ov.innerHTML = '<div class="fgh"><button type="button" class="fgbtn" data-fg="back">← もどる</button><div class="fgt"><b></b><span></span></div><button type="button" class="fgbtn" data-fg="over">一覧</button></div>'
      + '<div class="fgwr"><div class="fgst"><canvas></canvas><div class="fgsl"></div><div class="fgld" hidden><i></i><span>よみこみ中…</span></div></div><div class="fgpn" hidden></div></div>'
      + '<div class="fgf"></div><div class="fgsh" aria-hidden="true"></div><div class="fgmsg" aria-live="polite"></div>';
    document.body.appendChild(ov);
    stg = ov.querySelector('.fgst'); cv = stg.querySelector('canvas'); slEl = ov.querySelector('.fgsl'); pn = ov.querySelector('.fgpn'); ft = ov.querySelector('.fgf'); ldEl = ov.querySelector('.fgld'); sh = ov.querySelector('.fgsh');
    let h = ''; for (let i = 0; i < PER; i++) h += `<button type="button" class="fgs empty" data-slot="${i}" tabindex="0"><span class="pl" aria-hidden="true">＋</span></button>`;
    slEl.innerHTML = h;
    slEl.addEventListener('click', e => { const b = e.target.closest('.fgs'); if (b) tapSlot(+b.dataset.slot); });
    ov.addEventListener('click', onClick);
    stg.addEventListener('pointerdown', onDown); stg.addEventListener('pointermove', onMove); stg.addEventListener('pointerup', onUp); stg.addEventListener('pointercancel', onUp);
    stg.addEventListener('contextmenu', e => e.preventDefault());
    if (window.ResizeObserver) new ResizeObserver(() => { if (ov.classList.contains('on')) { layout(); need(); } }).observe(stg);
    window.addEventListener('resize', () => { if (ov.classList.contains('on')) { layout(); need(); } });
    document.addEventListener('visibilitychange', () => { if (!document.hidden && ov.classList.contains('on')) need(); });
  }
  function layout() {
    const r = stg.getBoundingClientRect(); if (!r.width || !r.height) return false;
    const dpr = Math.min(window.devicePixelRatio || 1, 2), w = Math.round(r.width * dpr), h = Math.round(r.height * dpr);
    if (cv.width !== w || cv.height !== h) { cv.width = w; cv.height = h; }
    return true;
  }
  function head(title, sub, back, right) {
    ov.querySelector('.fgt b').textContent = title; ov.querySelector('.fgt span').textContent = sub || '';
    const bk = ov.querySelector('[data-fg=back]'); bk.textContent = back || '← もどる';
    const rb = ov.querySelector('[data-fg=over]'); rb.hidden = !right; if (right) rb.textContent = right;
  }
  function msg(t, sec) {
    const m = ov.querySelector('.fgmsg'); m.textContent = t; m.classList.add('on');
    clearTimeout(msg._t); msg._t = setTimeout(() => m.classList.remove('on'), (sec || 2.6) * 1000);
  }
  let ldT = 0;
  function loading(on) { clearTimeout(ldT); if (on) ldT = setTimeout(() => { ldEl.hidden = false; }, 160); else ldEl.hidden = true; }

  // ---------- 3D の 準備 ----------
  let fontsP = null;
  function fonts() {
    if (!fontsP) fontsP = Promise.race([Promise.all([document.fonts ? document.fonts.load('400 48px "Dela Gothic One"', '的中') : null, document.fonts ? document.fonts.load('700 48px "BIZ UDPGothic"', '購入') : null]).catch(() => { }), new Promise(ok => setTimeout(ok, 1500))]);
    return fontsP;
  }
  function gl() {
    if (R) return R;
    R = FigGL.create(cv); if (!R) throw new Error('webgl');
    R.onRestore = () => { fcache = {}; bcache.clear(); scene = null; snaps = []; if (room) { room.F = null; room.boardT = null; } reload(); };
    return R;
  }
  let fcache = {};                                     // ブース用の フィギュア（デザインごと：小さい 絵）
  const figB = n => (fcache[n] = fcache[n] || R.figure(n, 's').catch(e => { delete fcache[n]; throw e; }));
  const bcache = new Map();                            // ボードの 絵（ブース用・フィギュアごと）
  function boardB(it, F) { let t = bcache.get(it.id); if (!t) { t = R.boardTex(F, it.info, 512); bcache.set(it.id, t); } return t; }
  function boardsKeep(ids) { for (const [id, t] of bcache) if (!ids.has(id)) { R.freeTex(t); bcache.delete(id); } }

  // ---------- 描く ----------
  let mode = '', page = 0, scene = null, pageTok = 0, raf = 0;
  const view = { yaw: 0, pitch: 0 };
  let hold = false;                                    // 見本の 動画を 写す とき：ブースの かたむきを もどさない（_t.hold）
  let room = null;                                     // { it（作った もの）か prev（作る 前）, F, boardT, yaw, pitch, zoom, vy, intro }
  let rects = [];
  function need() { if (!raf && ov && ov.classList.contains('on')) raf = requestAnimationFrame(frame); }
  function frame(now) {
    raf = 0; if (!R || R.lost || !cv.width) return;
    let more = false;
    if (mode === 'booth' && scene) {
      if (!drag && !hold) { view.yaw *= 0.78; view.pitch *= 0.78; if (Math.abs(view.yaw) < 0.04 && Math.abs(view.pitch) < 0.04) { view.yaw = 0; view.pitch = 0; } else more = true; }
      R.drawBooth(cv.width, cv.height, { shelf: scene.shelf, shelfT: scene.shelfT, figs: scene.figs, yaw: view.yaw, pitch: view.pitch });
      paintSlots();
    } else if ((mode === 'room' || (mode === 'make' && mk.step === 'prev')) && room && room.F) {
      if (room.intro) { const k = clamp((now - room.intro.t0) / 1300, 0, 1), e = 1 - Math.pow(1 - k, 3); room.yaw = room.intro.y0 * (1 - e); if (k < 1) more = true; else room.intro = null; }
      else if (!drag && Math.abs(room.vy) > 0.02) { room.yaw += room.vy; room.vy *= 0.93; more = true; }
      R.drawRoom(cv.width, cv.height, room);
    } else { const g = R.gl; g.viewport(0, 0, cv.width, cv.height); g.clearColor(0, 0, 0, 0); g.clear(g.COLOR_BUFFER_BIT | g.DEPTH_BUFFER_BIT); }
    if (more) need();
  }

  // ---------- ブース ----------
  async function loadPage(p) {
    const tok = ++pageTok; loading(true);
    try {
      await fonts(); const shelf = await R.shelfMesh();
      const name = `fg_shelf_c${p + 1}.webp`, shelfT = await R.tex(name);
      const list = onPage(p); let Fs;
      try { Fs = await Promise.all(list.map(x => figB(x.it.n))); } catch (e) { R.drop(name); throw e; }
      if (tok !== pageTok) { R.drop(name); return false; }
      const old = scene;
      scene = { p, shelf, shelfName: name, shelfT, figs: list.map((x, k) => ({ slot: x.slot, it: x.it, F: Fs[k], boardT: boardB(x.it, Fs[k]) })) };
      if (old) R.drop(old.shelfName);
      boardsKeep(new Set(list.map(x => x.it.id)));
      return true;
    } finally { if (tok === pageTok) loading(false); }
  }
  function paintSlots() {
    const r = stg.getBoundingClientRect(); rects = R.slotRects(cv.width, cv.height, view.yaw, view.pitch, r.width, r.height);
    const bs = slEl.children, sel = pick ? pick.id : '';
    for (let i = 0; i < PER; i++) {
      const b = bs[i], q = rects[i], id = slots[page * PER + i], it = itemOf(id);
      b.style.left = q.x + 'px'; b.style.top = q.y + 'px'; b.style.width = q.w + 'px'; b.style.height = q.h + 'px';
      b.classList.toggle('has', !!it); b.classList.toggle('empty', !it); b.classList.toggle('sel', !!it && it.id === sel);
      const lab = `${['上', '2段目', '3段目', '下'][i >> 1]}の ${i & 1 ? '右' : '左'}：` + (it ? `${NAMES[it.n]}（${it.info && it.info.race || ''}）` : pick ? 'ここに 飾る' : '空き（押すと 飾る フィギュアを 選ぶ）');
      if (b.getAttribute('aria-label') !== lab) b.setAttribute('aria-label', lab);
    }
  }
  function slotAt(x, y) { for (let i = 0; i < rects.length; i++) { const q = rects[i]; if (x >= q.x && x <= q.x + q.w && y >= q.y && y <= q.y + q.h) return i; } return -1; }
  function footBooth() {
    const st = stored().length;
    let h = `<div class="fgpg"><button type="button" data-fg="prev" aria-label="前の ブース"${page <= 0 ? ' disabled' : ''}>‹</button><div class="fgdots" aria-hidden="true">${Array.from({ length: PAGES }, (_, i) => `<i class="${i === page ? 'on' : ''}"></i>`).join('')}</div><button type="button" data-fg="next" aria-label="次の ブース"${page >= PAGES - 1 ? ' disabled' : ''}>›</button></div>`;
    if (pick) {
      const it = itemOf(pick.id);
      h += `<div class="fgpick">${pick.from >= 0 ? '動かす 場所を 選んでね' : '飾る 場所を 選んでね'}<small>${esc(it ? `${NAMES[it.n]}・${it.info && it.info.race || ''}` : '')}　ほかの ブースは ‹ › で</small></div>`
        + `<div class="fgrow">${pick.from >= 0 ? '<button type="button" class="dk" data-fg="unplace">しまう</button>' : ''}<button type="button" class="dk" data-fg="pickx">${pick.fresh ? 'あとで（しまっておく）' : 'やめる'}</button></div>`;
    } else {
      h += `<div class="fgrow"><button type="button" class="dk" data-fg="store">しまってある（${st}）</button><button type="button" class="pri" data-fg="make">＋ フィギュアを作る</button></div>`;
    }
    ft.innerHTML = h;
    ov.classList.toggle('pick', !!pick);
  }
  async function showBooth(p, dir) {
    closeSheet(); exitRoom();
    mode = 'booth'; ov.classList.remove('roomm'); pn.hidden = true; pn.innerHTML = ''; slEl.hidden = false; stg.classList.remove('room');
    if (p != null) page = clamp(p, 0, PAGES - 1);
    try { localStorage.setItem(PK, String(page)); } catch (e) { /* なし */ }
    head('思い出フィギュアブース', `ブース ${page + 1} / ${PAGES}`, '← もどる', '一覧');
    footBooth(); layout();
    if (dir) await slide(dir, () => loadPage(page)); else { try { await loadPage(page); } catch (e) { fail(e); } }
    need();
  }
  // ページを 横に すべらせて かえる（CSS で 今の 絵を 外へ → 新しい ページを 書いて 反対から 入れる）
  async function slide(dir, load) {
    const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (!reduce) { stg.style.transition = 'transform .16s ease-in,opacity .16s'; stg.style.transform = `translateX(${-dir * 36}%)`; stg.style.opacity = '0'; await wait(160); }
    try { await load(); } catch (e) { fail(e); }
    if (!reduce) { stg.style.transition = 'none'; stg.style.transform = `translateX(${dir * 36}%)`; need(); await wait(30); stg.style.transition = 'transform .2s ease-out,opacity .2s'; stg.style.transform = 'none'; stg.style.opacity = '1'; await wait(200); stg.style.transition = ''; }
    else { stg.style.transform = ''; stg.style.opacity = ''; }
  }
  const wait = ms => new Promise(ok => setTimeout(ok, ms));
  function fail(e) { loading(false); console.warn('fig', e); msg('フィギュアの 絵を 読みこめなかったよ', 3.2); }
  function goPage(d) { const np = clamp(page + d, 0, PAGES - 1); if (np === page) return; page = np; head('思い出フィギュアブース', `ブース ${page + 1} / ${PAGES}`, '← もどる', '一覧'); footBooth(); slide(d, () => loadPage(page)).then(need); try { localStorage.setItem(PK, String(page)); } catch (e) { /* なし */ } }

  // 置き場所を 押した
  let pick = null;                                     // { id, from（いまの 場所・-1＝しまって いた）, fresh（作った ばかり）}
  async function tapSlot(i) {
    if (mode !== 'booth' || i < 0) return;
    const g = page * PER + i, id = slots[g];
    if (pick) {
      if (id === pick.id) { pick = null; footBooth(); need(); return; }
      const next = slots.slice(), from = pick.from >= 0 ? pick.from : slotOf(pick.id);
      if (from >= 0) next[from] = id || null; next[g] = pick.id;
      const moved = id && from < 0 ? itemOf(id) : null;
      pick = null; await saveSlots(next); await reloadScene(); footBooth(); need();
      msg(moved ? `飾ったよ！\n（${NAMES[moved.n]}は しまったよ）` : '飾ったよ！', 2.0);
      return;
    }
    if (id) { const it = itemOf(id); if (it) openRoom(it); return; }
    openSheet(g);
  }
  async function reloadScene() { try { await loadPage(page); } catch (e) { fail(e); } }
  function startPick(id, fresh) { pick = { id, from: slotOf(id), fresh: !!fresh }; footBooth(); need(); }

  // しまってある フィギュア（下から 出る 欄）：target＝押した 空きの 場所（そこに 飾る）
  let sheetTarget = -1;
  function openSheet(target) {
    sheetTarget = target == null ? -1 : target;
    const list = stored().slice().reverse();
    let h = `<h3><span>${sheetTarget >= 0 ? 'ここに 飾る フィギュアを 選んでね' : 'しまってある フィギュア'}</span><button type="button" data-fg="shx">とじる</button></h3><div class="fgsl2">`;
    if (!list.length) {
      h += `<div class="fgempty">しまってある フィギュアは ないよ。${hasRaces() ? '<br>思い出のレースから 新しく 作れるよ' : '<br>記録タブで「思い出のレースに記録する」と、フィギュアに できるよ'}</div>`;
      if (hasRaces()) h += '<div class="fgrow"><button type="button" class="pri" data-fg="make">＋ フィギュアを作る</button></div>';
    } else list.forEach(it => { h += `<button type="button" class="fgsr" data-fg="sitem" data-id="${esc(it.id)}"><img src="fg${it.n}_t.webp" alt=""><span><b>${esc(it.info && it.info.race || '')}</b><small>${esc(circ(it.n) + ' ' + NAMES[it.n])}・${esc(it.info && it.info.date || '')}</small></span><em>${sheetTarget >= 0 ? '飾る' : '見る'}</em></button>`; });
    sh.innerHTML = h + '</div>'; sh.setAttribute('aria-hidden', 'false');
    requestAnimationFrame(() => sh.classList.add('on'));
  }
  function closeSheet() { if (!sh) return; sh.classList.remove('on'); sh.setAttribute('aria-hidden', 'true'); sheetTarget = -1; }
  const hasRaces = () => { try { return !!(MEM() && MEM().list().length); } catch (e) { return false; } };

  // ---------- 一覧（7つの ブースを いっぺんに）----------
  let snaps = [];
  const sigOf = p => slots.slice(p * PER, p * PER + PER).map(x => x || '').join(',');
  async function showOver() {
    closeSheet(); exitRoom(); pick = null; ov.classList.remove('pick');
    mode = 'over'; slEl.hidden = true;
    const placed = slots.filter(Boolean).length;
    head('ブース一覧', `飾っている フィギュア ${placed} / ${MAX}`, '← ブースへ', '');
    ft.innerHTML = '';
    let h = '<div class="fgov">';
    for (let p = 0; p < PAGES; p++) h += `<button type="button" class="fgoc${p === page ? ' cur' : ''}" data-fg="ovp" data-p="${p}" aria-label="ブース ${p + 1}（${onPage(p).length}こ）"><canvas width="300" height="388"></canvas><b>ブース ${p + 1}</b><small>${onPage(p).length} / ${PER}</small></button>`;
    h += `<div class="fgos"><span>飾っている<br>フィギュア</span><b>${placed} / ${MAX}</b><small>しまってある ${stored().length}</small></div></div>`;
    pn.innerHTML = h; pn.hidden = false; pn.scrollTop = 0;
    for (let p = 0; p < PAGES; p++) {
      if (mode !== 'over') return;
      const c = pn.querySelector(`[data-p="${p}"] canvas`), sig = sigOf(p);
      if (!c) return;
      if (!(snaps[p] && snaps[p].sig === sig)) {
        try { snaps[p] = { sig, c: await snapPage(p) }; } catch (e) { fail(e); return; }
      }
      if (mode !== 'over') return;
      const g = c.getContext('2d'); g.clearRect(0, 0, c.width, c.height); g.drawImage(snaps[p].c, 0, 0);
    }
  }
  async function snapPage(p) {
    await fonts(); const shelf = await R.shelfMesh(), name = `fg_shelf_c${p + 1}.webp`, shelfT = await R.tex(name);
    try {
      const list = onPage(p), Fs = await Promise.all(list.map(x => figB(x.it.n)));
      const bts = list.map((x, k) => R.boardTex(Fs[k], x.it.info, 256));
      const out = document.createElement('canvas'); out.width = 300; out.height = 388;
      R.snapshot(600, 776, { shelf, shelfT, figs: list.map((x, k) => ({ slot: x.slot, F: Fs[k], boardT: bts[k] })), yaw: 0, pitch: 0 }, out);
      bts.forEach(t => R.freeTex(t));
      return out;
    } finally { R.drop(name); }
  }

  // ---------- 部屋（1体を 3D で 見る）----------
  async function openRoom(it) {
    closeSheet(); pick = null; ov.classList.remove('pick');
    mode = 'room'; pn.hidden = true; slEl.hidden = true; stg.classList.add('room');
    head(`${circ(it.n)} ${NAMES[it.n]}`, it.info && it.info.race || '', '← ブースへ', '');
    footRoom(it); layout();
    await enterRoom(it.n, it.info, { it });
  }
  function footRoom(it) {
    const at = it.at ? new Date(it.at) : null, made = at ? `${at.getFullYear()}/${at.getMonth() + 1}/${at.getDate()}` : '';
    const placed = slotOf(it.id) >= 0;
    ft.innerHTML = `<div class="fginfo">${it.info && it.info.kind ? `<span class="k">${esc(it.info.kind)}</span>` : ''}<b>${esc(it.info && it.info.race || '')}</b><small>${esc(it.info && it.info.date || '')}${made ? `　・　作った日 ${made}` : ''}</small></div>`
      + `<div class="fgrow">${placed ? '<button type="button" class="dk" data-fg="move">場所をかえる</button><button type="button" class="dk" data-fg="unplace">しまう</button>' : '<button type="button" class="pri" data-fg="place">ブースに飾る</button>'}</div>`
      + '<div class="fghint">指で まわせるよ・2本指で 大きく</div>';
  }
  async function enterRoom(n, info, extra) {
    exitRoom();
    const tok = ++roomTok; loading(true);
    try {
      await fonts(); const F = await R.figure(n, 'l');
      if (tok !== roomTok) { F.release(); return; }
      room = Object.assign({ F, boardT: R.boardTex(F, info, 1024), yaw: 0, pitch: 8, zoom: 1, vy: 0, intro: { t0: performance.now(), y0: -28 } }, extra || {});
    } catch (e) { fail(e); } finally { if (tok === roomTok) loading(false); }
    need();
  }
  let roomTok = 0;
  function exitRoom() { roomTok++; if (room) { if (room.F) room.F.release(); if (room.boardT) R.freeTex(room.boardT); room = null; } }

  // ---------- 作る（レース → デザイン → 3D で 見て 作る）----------
  const mk = { step: 'race', race: null, n: 0, conf: false, back: 'close', fixed: false };
  function showMake(step) {
    closeSheet(); pick = null; ov.classList.remove('pick');
    mode = 'make'; mk.step = step; mk.conf = false; slEl.hidden = true;
    if (step === 'race') {
      exitRoom(); stg.classList.remove('room');
      head('フィギュアを作る', '1. 思い出のレースを 選ぶ', mk.back === 'booth' ? '← ブースへ' : '← もどる', '');
      const list = (MEM() && MEM().list()) || [];
      let h = '<div class="fgmk"><p class="lead">思い出のレースを、ボードに 書いた フィギュアに できるよ。デザインは 8種類。作った フィギュアは フィギュアブースに 飾れるよ。</p>';
      if (!list.length) h += '<div class="fgempty">思い出のレースが まだ ないよ。<br>記録タブで 結果を 決めた レースを 開いて「思い出のレースに記録する」を 押してね。</div>';
      list.forEach(r => { h += `<button type="button" class="fgrace" data-fg="race" data-id="${esc(r.id)}">${r.kind ? `<span class="k">${esc(r.kind)}</span>` : ''}<b>${esc(r.day)}　${esc(r.race)}</b><small>${esc(r.result)}</small></button>`; });
      pn.innerHTML = h + '</div>'; pn.hidden = false; pn.scrollTop = 0; ft.innerHTML = '';
    } else if (step === 'design') {
      exitRoom(); stg.classList.remove('room');
      const r = mk.race;
      head('フィギュアを作る', '2. デザインを 選ぶ', '← もどる', '');
      let h = `<div class="fgmk"><div class="fgsel">${r.kind ? `${esc(r.kind)}　` : ''}<b>${esc(r.day)}　${esc(r.race)}</b><br>${esc(r.result)}</div><div class="fgdg">`;
      for (let n = 1; n <= 8; n++) {
        const k = KIND[n];
        h += `<button type="button" class="fgd" data-fg="design" data-n="${n}" aria-label="${circ(n)} ${NAMES[n]}　${nf(priceOf(n))}ポイント"><img src="fg${n}_t.webp" alt=""><b>${circ(n)} ${esc(NAMES[n])}</b>${KIND_JA[k] ? `<span class="kd ${k}">${esc(KIND_JA[k])}</span>` : ''}<span class="pr">${nf(priceOf(n))}P</span></button>`;
      }
      pn.innerHTML = h + '</div></div>'; pn.hidden = false; pn.scrollTop = 0; ft.innerHTML = '';
    } else if (step === 'prev') {
      pn.hidden = true; stg.classList.add('room');
      head(`${circ(mk.n)} ${NAMES[mk.n]}`, '3. 3D で 見て 作る', '← デザイン', '');
      footBuy(); layout();
      enterRoom(mk.n, mk.race.info, { prev: true });
    }
    need();
  }
  function footBuy() {
    const w = WL(), have = w ? w.total() : 0, cost = priceOf(mk.n), ok = have >= cost;
    ft.innerHTML = `<div class="fgbuy"><b>${nf(cost)}P</b>　いま ${nf(have)}P${ok ? '' : `<br><span class="ng">あと ${nf(cost - have)}P 足りないよ</span>`}</div>`
      + `<div class="fgrow">${mk.conf ? `<button type="button" class="dk" data-fg="buyx">やめる</button><button type="button" class="pri" data-fg="buy2">${nf(cost)}Pを使って作る</button>` : `<button type="button" class="pri" data-fg="buy1"${ok ? '' : ' disabled'}>このデザインで作る</button>`}</div>`
      + '<div class="fghint">指で まわせるよ・2本指で 大きく</div>';
  }
  let buying = false;
  async function buy() {
    if (buying) return; buying = true;
    try {
      const w = WL(); if (!w || !w.fig || !mk.race) return;
      const n = mk.n, it = { id: 'f' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6), n, bet: mk.race.id, info: mk.race.info };
      const r = await w.fig.buy(it, priceOf(n));
      if (!r.ok) { mk.conf = false; footBuy(); msg(r.why === 'short' ? `ポイントが 足りないよ\n（あと ${nf(r.need)}P）` : 'フィギュアを 作れなかったよ', 3); return; }
      sync(); snaps = [];
      const free = slots.indexOf(null);
      if (free < 0) { msg('🎉 思い出フィギュアが できたよ！\nブースが いっぱいなので しまっておくね', 3.6); await showBooth(page); return; }
      pick = { id: r.item.id, from: -1, fresh: true };
      await showBooth(Math.floor(free / PER));
      msg('🎉 思い出フィギュアが できたよ！\n飾る 場所を 選んでね', 3.2);
      try { document.dispatchEvent(new CustomEvent('tengel:fig')); } catch (e) { /* なし */ }
    } finally { buying = false; }
  }

  // ---------- ボタン ----------
  async function onClick(e) {
    const b = e.target.closest('[data-fg]'); if (!b || b.disabled) return;
    const a = b.dataset.fg;
    if (a === 'back') return back();
    if (a === 'over') return showOver();
    if (a === 'prev') return goPage(-1);
    if (a === 'next') return goPage(1);
    if (a === 'ovp') return showBooth(+b.dataset.p);
    if (a === 'store') return openSheet(-1);
    if (a === 'shx') return closeSheet();
    if (a === 'make') { mk.back = 'booth'; mk.fixed = false; return showMake('race'); }
    if (a === 'sitem') {
      const it = itemOf(b.dataset.id); if (!it) return;
      if (sheetTarget >= 0) { const next = slots.slice(), g = sheetTarget; next[g] = it.id; closeSheet(); await saveSlots(next); await reloadScene(); footBooth(); need(); msg('飾ったよ！', 1.8); }
      else openRoom(it);
      return;
    }
    if (a === 'pickx') { pick = null; footBooth(); need(); return; }
    if (a === 'move' && room && room.it) { const it = room.it; const g = slotOf(it.id); await showBooth(g >= 0 ? Math.floor(g / PER) : page); startPick(it.id, false); return; }
    if (a === 'place' && room && room.it) { const it = room.it, free = slots.indexOf(null); if (free < 0) { msg('ブースが いっぱいだよ。\nほかの フィギュアを しまってから 飾ってね', 3.2); return; } await showBooth(Math.floor(free / PER)); startPick(it.id, false); return; }
    if (a === 'unplace') {
      const id = room && room.it ? room.it.id : pick ? pick.id : ''; if (!id) return;
      const next = slots.slice(), g = slotOf(id); if (g >= 0) next[g] = null;
      pick = null; await saveSlots(next); snaps = [];
      if (mode === 'room') { footRoom(itemOf(id) || room.it); msg('しまったよ（「しまってある」から また 飾れるよ）', 3); }
      else { await reloadScene(); footBooth(); need(); msg('しまったよ', 1.8); }
      return;
    }
    if (a === 'race') { const r = MEM() && MEM().get(b.dataset.id); if (!r) return; mk.race = r; return showMake('design'); }
    if (a === 'design') { mk.n = +b.dataset.n; return showMake('prev'); }
    if (a === 'buy1') { mk.conf = true; footBuy(); return; }
    if (a === 'buyx') { mk.conf = false; footBuy(); return; }
    if (a === 'buy2') return buy();
  }
  function back() {
    if (sh && sh.classList.contains('on')) return closeSheet();
    if (mode === 'booth') { if (pick) { pick = null; footBooth(); need(); return; } return close(); }
    if (mode === 'over' || mode === 'room') return showBooth(page);
    if (mode === 'make') {
      if (mk.step === 'prev') return showMake('design');
      if (mk.step === 'design') return mk.fixed ? (mk.back === 'booth' ? showBooth(page) : close()) : showMake('race');
      return mk.back === 'booth' ? showBooth(page) : close();
    }
    close();
  }

  // ---------- 指の 動き ----------
  let drag = null, lp = 0;
  const ptrs = new Map();
  function rel(e) { const r = stg.getBoundingClientRect(); return { x: e.clientX - r.left, y: e.clientY - r.top }; }
  function onDown(e) {
    if (!(mode === 'booth' || mode === 'room' || (mode === 'make' && mk.step === 'prev'))) return;
    try { stg.setPointerCapture(e.pointerId); } catch (x) { /* なし */ }
    const p = rel(e); ptrs.set(e.pointerId, p);
    if (ptrs.size === 1) {
      drag = { x0: p.x, y0: p.y, x: p.x, y: p.y, t0: performance.now(), moved: false, yaw0: room ? room.yaw : 0, pitch0: room ? room.pitch : 0, lastX: p.x, lastT: performance.now() };
      if (room) { room.vy = 0; room.intro = null; }
      if (mode === 'booth' && !pick) {
        const i = slotAt(p.x, p.y), id = i >= 0 ? slots[page * PER + i] : null;
        clearTimeout(lp); if (id) lp = setTimeout(() => { if (drag && !drag.moved) { drag.lp = true; startPick(id, false); msg('動かす 場所を 選んでね', 1.8); } }, 520);
      }
    } else if (ptrs.size === 2 && room) {
      clearTimeout(lp); const [a, b] = [...ptrs.values()]; drag = Object.assign(drag || {}, { pinch: Math.hypot(a.x - b.x, a.y - b.y), zoom0: room.zoom, moved: true });
    }
  }
  function onMove(e) {
    if (!drag || !ptrs.has(e.pointerId)) return;
    const p = rel(e); ptrs.set(e.pointerId, p);
    if (ptrs.size >= 2 && room && drag.pinch) { const [a, b] = [...ptrs.values()], d = Math.hypot(a.x - b.x, a.y - b.y); room.zoom = clamp(drag.zoom0 * drag.pinch / Math.max(20, d), 0.42, 1.6); need(); return; }
    const dx = p.x - drag.x0, dy = p.y - drag.y0;
    if (!drag.moved && Math.hypot(dx, dy) > 8) { drag.moved = true; clearTimeout(lp); }
    if (!drag.moved) return;
    if (mode === 'booth') { view.yaw = clamp(dx * 0.055, -12, 12); view.pitch = clamp(dy * 0.04, -6, 9); }
    else if (room) {
      const now = performance.now(); room.yaw = drag.yaw0 - dx * 0.45; room.pitch = clamp(drag.pitch0 + dy * 0.3, -10, 45);
      if (now - drag.lastT > 0) { room.vy = -(p.x - drag.lastX) * 0.45 * Math.min(1, 16 / (now - drag.lastT)); drag.lastX = p.x; drag.lastT = now; }
    }
    need();
  }
  function onUp(e) {
    if (!ptrs.has(e.pointerId)) return;
    ptrs.delete(e.pointerId); clearTimeout(lp);
    if (!drag) return;
    if (ptrs.size > 0) { if (ptrs.size === 1 && room) { const q = [...ptrs.values()][0]; drag.x0 = q.x; drag.y0 = q.y; drag.yaw0 = room.yaw; drag.pitch0 = room.pitch; drag.pinch = 0; drag.lastX = q.x; } return; }
    const d = drag; drag = null;
    if (e.type === 'pointercancel') { need(); return; }
    const p = rel(e), mx = p.x - d.x0, my = p.y - d.y0, dt = performance.now() - d.t0;
    if (mode === 'booth') {
      if (d.lp) { need(); return; }
      if (!d.moved) { tapSlot(slotAt(p.x, p.y)); return; }
      if (Math.abs(mx) > 60 && Math.abs(mx) > Math.abs(my) * 1.3) goPage(mx < 0 ? 1 : -1);
      else if (Math.abs(mx) > 30 && dt < 260 && Math.abs(mx) > Math.abs(my) * 1.3) goPage(mx < 0 ? 1 : -1);
      need(); return;
    }
    if (room) {
      if (!d.moved) { const t = performance.now(); if (t - (onUp.lastTap || 0) < 320) { room.yaw = 0; room.pitch = 8; room.zoom = 1; room.vy = 0; onUp.lastTap = 0; } else onUp.lastTap = t; }
      if (performance.now() - d.lastT > 80) room.vy = 0;
      need();
    }
  }

  // ---------- 開く・閉じる ----------
  async function init() {
    build(); sync();
    ov.classList.add('on'); layout();
    gl();
  }
  let ready = null;
  async function start() {
    if (!ready) ready = init().catch(e => { ready = null; throw e; });
    await ready; sync(); ov.classList.add('on'); layout();
    try { if (window.TengelWallet && window.TengelWallet.lockZoom) window.TengelWallet.lockZoom(true); } catch (e) { /* なし */ }
  }
  async function booth(opt) {
    try { await start(); } catch (e) { return openFail(e); }
    let p = 0; try { p = +(localStorage.getItem(PK) || 0) || 0; } catch (e) { /* なし */ }
    pick = null;
    if (opt && opt.id) { const g = slotOf(opt.id); if (g >= 0) p = Math.floor(g / PER); }
    await showBooth(p);
  }
  async function make(opt) {
    try { await start(); } catch (e) { return openFail(e); }
    mk.back = 'close'; mk.fixed = false; mk.race = null;
    if (opt && opt.race) { const r = MEM() && MEM().get(opt.race); if (r) { mk.race = r; mk.fixed = true; return showMake('design'); } }
    showMake('race');
  }
  function openFail(e) { if (ov) ov.classList.remove('on'); alert('思い出フィギュアを ひらけなかったよ（' + (e && e.message || e) + '）'); }
  function reload() { if (mode === 'booth') showBooth(page); else if (mode === 'over') showOver(); else if (mode === 'room' && room && room.it) openRoom(room.it); else if (mode === 'make') showMake(mk.step); }
  function close() {
    closeSheet(); exitRoom(); pick = null; mode = '';
    if (ov) ov.classList.remove('on', 'pick');
    try { if (window.TengelWallet && window.TengelWallet.lockZoom) window.TengelWallet.lockZoom(false); } catch (e) { /* なし */ }
    try { document.dispatchEvent(new CustomEvent('tengel:fig')); } catch (e) { /* なし */ }
  }
  return { booth, make, close, NAMES, KIND, PRICE, _t: { get mode() { return mode; }, get page() { return page; }, get slots() { return slots.slice(); }, get items() { return items.slice(); }, tapSlot, goPage, showOver, get mk() { return mk; }, get room() { return room; }, need,
    get view() { return view; }, hold: v => { hold = !!v; }, draw: () => { if (raf) { cancelAnimationFrame(raf); raf = 0; } frame(performance.now()); } } };      // _t：テスト・見本の 動画 用
})();
