// ===== ポイント・Pカスタム（解放）・ミッション・アプリを開いた時の画面・拡大（App Store版だけ）=====
// 台帳の計算は points.js（TengelPoints）。ここは保存（アプリの中＝IndexedDB の meta 'wallet'・自動バックアップにも入る）と画面。
//  ・アプリを消すと台帳も消える（5章）。キーチェーンには「しるし」だけ：初回プレゼント（gift-first）・サブスクのPを足した取引（granted-sub）
//  ・App内課金（StoreKit 2）はアプリ（Store.swift）。台帳に書けたら finish をお願いする
//  ・読み込み（画像の読み取り）1レース 200P。同じレースの読み直しは 0P（11.4）。5連の予想（5レースまとめて）200P
//  ・ほかの画面から使う窓口：window.TengelWallet
(function () {
  'use strict';
  if (!window.__NATIVE || !window.TengelLocal || !window.TengelPoints) return;
  const P = window.TengelPoints, TL = window.TengelLocal, N = window.TengelNative;
  const $ = (s, el) => (el || document).querySelector(s);
  const $$ = (s, el) => Array.from((el || document).querySelectorAll(s));
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const yen = v => Math.round(+v || 0).toLocaleString('ja-JP');
  const pts = v => yen(v) + 'P';
  const pad = n => ('0' + n).slice(-2);
  const when = iso => { if (!iso) return ''; const d = new Date(iso); return `${d.getFullYear()}/${d.getMonth() + 1}/${d.getDate()} ${pad(d.getHours())}:${pad(d.getMinutes())}`; };
  const dayOf = iso => { if (!iso) return '—'; const d = new Date(iso); return `${d.getMonth() + 1}/${d.getDate()}`; };
  const reduced = () => matchMedia('(prefers-reduced-motion: reduce)').matches;
  function toast(m, ms) { const t = $('#toast'); if (!t) return; t.textContent = m; t.hidden = false; clearTimeout(toast._t); toast._t = setTimeout(() => { t.hidden = true; }, ms || 3000); }
  const emit = () => { try { document.dispatchEvent(new CustomEvent('tengel:wallet')); } catch (e) { /* なし */ } };

  // ---------- 台帳（アプリの中） ----------
  // meta 'wallet' = { id, v, device, events[], paid[]（200Pを使ったレース）, counted{ 日付|開催場|R: 日時 }（ミッションに数えたレース）, gift（初回プレゼントのしるしの状態） }
  let W = null, saving = Promise.resolve();
  const newId = () => Math.random().toString(36).slice(2, 10);
  const blank = () => ({ id: 'wallet', v: 1, device: newId(), events: [], paid: [], counted: {}, gift: null, at: '' });
  function normalize(w) {
    const o = Object.assign(blank(), w && typeof w === 'object' ? w : {});
    o.id = 'wallet'; o.events = Array.isArray(o.events) ? o.events.filter(Boolean) : []; o.paid = Array.isArray(o.paid) ? o.paid : []; o.counted = o.counted && typeof o.counted === 'object' ? o.counted : {};
    if (!o.device) o.device = newId();
    return o;
  }
  function save() {
    W.at = new Date().toISOString();
    const snap = JSON.parse(JSON.stringify(W));
    saving = saving.then(() => TL.putMeta(snap)).catch(() => { /* 次の保存で書く */ });
    emit(); paintAll();
    return saving;
  }
  const B = () => P.balance(W ? W.events : [], Date.now());
  const total = () => B().total;
  const device = () => (W && W.device) || 'x';

  // ---------- 初回プレゼント（キーチェーンのしるしで1回だけ） ----------
  async function marker(op, key, value) {
    try { const r = await N.marker(op, key, value); return r && r.ok ? r : { ok: false, error: r && r.error }; } catch (e) { return { ok: false, error: String(e && e.message || e), noBridge: true }; }
  }
  async function giftCheck() {
    if (P.has(W.events, 'gift-first')) {
      if (!W.gift || !W.gift.marked) { const r = await marker('set', 'gift-first', W.events.find(e => e.id === 'gift-first').at); if (r.ok) { W.gift = { marked: true }; save(); } }
      return;
    }
    const r = await marker('get', 'gift-first');
    if (r.ok && r.has) { if (!W.gift || W.gift.state !== 'already') { W.gift = { state: 'already', at: r.value || '' }; save(); } return; }   // 前に受け取っている（入れ直し・同じApple IDのほかの端末）
    const g = P.giftEvent(Date.now());
    W.events.push(g);
    const s = await marker('set', 'gift-first', g.at);
    W.gift = { marked: !!s.ok, state: 'given', note: s.ok ? '' : (s.error || '') };
    await save();
    toast('🎁 はじめまして！1,500P をプレゼントしたよ。1レースの読み込みに 200P 使うよ', 4600);
  }

  // ---------- App内課金 ----------
  let products = null, prodErr = '', subStatus = null;
  async function iap(op, p) { try { return await N.iap(op, p); } catch (e) { return { ok: false, error: String(e && e.message || e) }; } }
  async function loadProducts(force) {
    if (products && !force) return products;
    const r = await iap('products');
    if (r && r.ok && Array.isArray(r.products) && r.products.length) { products = r.products; prodErr = ''; }
    else { products = null; prodErr = (r && r.error) || 'App Storeから商品を読めなかったよ'; }
    return products;
  }
  const grantedKey = 'granted-sub';
  async function grantedSubs() { const r = await marker('get', grantedKey); if (!r.ok || !r.value) return []; try { const a = JSON.parse(r.value); return Array.isArray(a) ? a.map(String) : []; } catch (e) { return []; } }
  async function rememberSub(id) { const a = (await grantedSubs()).filter(x => x !== String(id)); a.push(String(id)); await marker('set', grantedKey, JSON.stringify(a.slice(-24))); }
  // 取引 → 台帳。返り値：足したP（0＝足していない）
  async function takeTx(tx, src) {
    if (!tx || !tx.id) return 0;
    let added = 0;
    if (tx.revoked) {
      const rf = P.refundEvent(W.events, tx, Date.now());
      if (rf) { W.events.push(rf); added = rf.amount; await save(); toast(`返金があったので ${pts(-rf.amount)} を引いたよ`, 4000); }
    } else if (!P.has(W.events, 'tx-' + tx.id)) {
      const done = tx.kind === 'sub' ? await grantedSubs() : [];
      if (tx.kind === 'sub' && done.includes(String(tx.id))) { /* 入れ直し・ほかの端末で、もうこの取引のPは足してある */ }
      else {
        const e = P.txEvent(W.events, tx, Date.now());
        if (e) {
          W.events.push(e); added = e.amount; await save();
          if (tx.kind === 'sub') await rememberSub(tx.id);
          if (src !== 'buy') toast(`✨ ${P.PRODUCTS[tx.product] ? P.PRODUCTS[tx.product].name : ''}の ${pts(e.amount)} が届いたよ`, 4000);
        }
      }
    }
    await iap('finish', { id: String(tx.id) });
    return added;
  }
  async function pullTransactions() {
    const r = await iap('unfinished');
    if (r && r.ok && Array.isArray(r.list)) for (const tx of r.list) await takeTx(tx, 'boot');
  }
  document.addEventListener('tengel:native', e => { const d = e.detail || {}; if (d.name === 'iap' && d.payload && W) takeTx(d.payload, 'update'); });
  async function buy(id, btn) {
    const Pd = P.PRODUCTS[id]; if (!Pd) return;
    if (btn) { btn.disabled = true; btn.textContent = 'App Store…'; }
    const r = await iap('buy', { id });
    if (btn) { btn.disabled = false; btn.textContent = Pd.kind === 'sub' ? 'はじめる' : '買う'; }
    if (r && r.ok && r.tx) {
      const added = await takeTx(r.tx, 'buy');
      toast(added ? `✅ ${pts(added)} が届いたよ（合計 ${pts(total())}）` : '✅ 買えたよ（このPはもう入っているよ）', 4000);
      if (Pd.kind === 'sub') refreshSubStatus();
    } else if (r && r.state === 'cancelled') { /* やめた */ }
    else if (r && r.state === 'pending') toast('承認待ちだよ。承認されたらPが届くよ（アプリを開いたときに入るよ）', 4600);
    else toast('買えなかったよ：' + ((r && (r.error || r.state)) || '不明'), 4200);
  }
  async function restore(btn) {
    if (btn) { btn.disabled = true; btn.textContent = '確かめているよ…'; }
    const r = await iap('restore');
    if (btn) { btn.disabled = false; btn.textContent = '購入を復元'; }
    if (!r || !r.ok) { toast('復元できなかったよ：' + ((r && r.error) || '不明'), 4200); return; }
    let added = 0;
    for (const tx of (r.unfinished || [])) added += await takeTx(tx, 'restore');
    for (const tx of (r.current || [])) if (tx.kind === 'sub') added += await takeTx(tx, 'restore');
    await refreshSubStatus();
    toast(added ? `✅ ${pts(added)} を足したよ` : '✅ Appleと合わせたよ（足すPはなかったよ）', 4000);
  }
  async function refreshSubStatus() { const r = await iap('status'); subStatus = r && r.ok ? r : null; paintPoints(); }

  // ---------- 使う：読み込み（200P）・読み直し 0P ----------
  const READ_WHAT = r => `読み込み ${r.date ? dayOf(r.date) : ''}${r.venue ? ' ' + r.venue : ''}${r.r ? ' ' + r.r + 'R' : ''}`.trim();
  function charge(amount, what) {
    const next = P.spend(W.events, amount, what, device(), Date.now());
    if (!next) return false;
    W.events = next; return true;
  }
  function keepPaid() { if (W.paid.length > 400) W.paid = W.paid.slice(-300); }
  // 返り値：{ ok, charged, free: 'session'|'same'|'w5'|null, pid } か { ok:false, need, have }
  async function readCharge(o) {
    await walletReady;
    const form = o.form || {}, d = o.ocr || {};
    // 読んだ画像に レース名・発走時刻が なければ、いまの入力のものを使う。ただし 別のレース（日付・開催場・R のどれかがちがう）を読んだときは引きつがない（同じレースの見分けをまちがえないため）
    const sameAsForm = (!d.r || !form.r || +d.r === +form.r) && (!d.date || !form.date || d.date === form.date) && (!d.venue || !form.venue || P.vnorm(d.venue) === P.vnorm(form.venue));
    const race = { date: d.date || form.date || '', venue: String(d.venue || form.venue || ''), r: +(d.r || form.r) || 0, rname: d.rname || (sameAsForm ? form.rname : '') || '', start: d.start || (sameAsForm ? form.start : '') || '', dist: +(d.dist || form.dist) || 0 };
    const stamp = e => { Object.assign(e, { date: e.date || race.date, venue: e.venue || race.venue, r: e.r || race.r, rname: e.rname || race.rname, start: e.start || race.start, dist: e.dist || race.dist, last: new Date().toISOString() }); };
    if (o.w5) {
      const key = 'w5:' + (o.w5.date || 'x'), hit = W.paid.find(e => e.w5 === key);
      if (hit) { stamp(hit); await save(); return { ok: true, charged: false, free: 'w5', pid: hit.pid }; }
      if (!charge(P.COST.w5, '5連の予想の読み込み ' + dayOf(o.w5.date))) return { ok: false, need: P.COST.w5, have: total() };
      const e = { pid: newId(), w5: key, at: new Date().toISOString() }; stamp(e); W.paid.push(e); keepPaid(); await save();
      return { ok: true, charged: true, free: null, pid: e.pid };
    }
    if (form.pid) {
      const cur = W.paid.find(e => e.pid === form.pid);
      if (cur && !cur.w5 && (!race.r || P.sameRace(cur, race) || !cur.r)) { stamp(cur); await save(); return { ok: true, charged: false, free: 'session', pid: cur.pid }; }
    }
    const same = P.findPaid(W.paid.filter(e => !e.w5), race);
    if (same) { stamp(same); await save(); return { ok: true, charged: false, free: 'same', pid: same.pid }; }
    if (!charge(P.COST.read, READ_WHAT(race))) return { ok: false, need: P.COST.read, have: total() };
    const e = { pid: newId(), at: new Date().toISOString() }; stamp(e); W.paid.push(e); keepPaid(); await save();
    return { ok: true, charged: true, free: null, pid: e.pid };
  }

  // ---------- ミッション：記録したレースを数える ----------
  async function countRace(b) {
    await walletReady;
    if (!b || b.kind === 'win5') return false;
    const key = P.raceKey(b); if (!key) return false;
    const paidFor = (b.pid && W.paid.some(e => e.pid === b.pid && !e.w5)) || !!P.findPaid(W.paid.filter(e => !e.w5), b);
    if (!paidFor || W.counted[key]) return false;
    W.counted[key] = new Date().toISOString();
    await save();
    const n = countedN(), claim = P.missions(n, W.events).filter(m => m.claimable);
    toast(claim.length ? `🏆 ${n}レース目の記録。受け取れるミッションがあるよ（上の「ミッション」で受け取れるよ）` : `ミッション：記録 ${n}レース目`, 3600);
    return true;
  }
  const countedN = () => W ? Object.keys(W.counted).length : 0;
  async function claim(id) {
    if (/^mission-wall-/.test(String(id))) {     // 壁紙のミッション（帯の壁紙・第4弾）
      const wm = P.wallMissions(P.wallCount(W.events), W.events).find(x => x.id === id);
      if (!wm || !wm.claimable) return;
      P.wallMissionEvents(wm, device(), Date.now()).forEach(e => { if (!P.has(W.events, e.id)) W.events.push(e); });
      await save(); paintAll();
      toast(`✅ ${wm.label}を受け取ったよ！ 設定の「着せ替え」で使えるよ`, 4000);
      unlockFx(msRowSel(id), '受け取り！');
      return;
    }
    const m = P.missions(countedN(), W.events).find(x => x.id === id);
    if (!m || !m.claimable) return;
    W.events.push(P.missionEvent(m, Date.now()));
    await save();
    toast(`🎉 ${m.label}の ${pts(m.reward)} を受け取ったよ（合計 ${pts(total())}）`, 4000);
    unlockFx(msRowSel(id), `+${pts(m.reward)}`);
  }
  // 受け取りの 効果を 出す 行：ミッションの 窓（第4.82版）が 開いて いれば その 行・そうでなければ 設定タブの カードの 行
  const msRowSel = id => ($('#msOv') ? `#msOv .msrow[data-mid="${id}"]` : `#setMission .msrow[data-mid="${id}"]`);

  // 解放エフェクト（第4.60版：fx.js の TengelFx.unlock。項目の 上で 金の 輪・つや・粒・「解放！」・チャイム）
  function unlockFx(sel, text) { try { const el = typeof sel === 'string' ? $(sel) : sel; if (el && window.TengelFx && window.TengelFx.unlock) window.TengelFx.unlock(el, { text }); } catch (e) { /* なし */ } }
  // ---------- 解放（Pカスタム） ----------
  const unlocked = key => !!(W && P.unlocked(W.events, key));
  const typeLocked = t => P.ALL_TYPES.includes(t) && !P.FREE_TYPES.includes(t) && !unlocked('type:' + t);
  const slotHasRows = n => { try { return TL.slots.rows(n).length > 0; } catch (e) { return false; } };
  const slotUnlocked = n => +n === 1 || unlocked('slot:' + n) || slotHasRows(+n);
  async function unlock(key, cost) {
    await walletReady;
    const next = P.unlock(W.events, key, cost, device(), Date.now());
    if (!next) return false;
    W.events = next; await save(); return true;
  }

  // ---------- 画面：設定タブのカード ----------
  function css() {
    if ($('#ptCss')) return;
    const st = document.createElement('style'); st.id = 'ptCss';
    st.textContent = '#setPoints .ptbal,#ptOv .ptbal{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}#setPoints .ptbig,#ptOv .ptbig{font-family:var(--font-display);font-size:34px;line-height:1.1}'
      + '#setPoints .ptbig small,#ptOv .ptbig small{font-size:16px;margin-left:2px}#setPoints .ptsub,#ptOv .ptsub{font-size:12.5px;color:var(--muted)}'
      + '.ptbk{display:grid;gap:6px;margin-top:8px}.ptbk>div{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:7px 12px;border-radius:10px;background:var(--surface-2);border:1px solid var(--line)}'
      + '.ptbk span{display:flex;flex-direction:column;font-weight:700;font-size:13.5px}.ptbk small{font-size:11px;font-weight:400;color:var(--muted)}.ptbk b{font-family:var(--font-mono);font-size:16px;white-space:nowrap}'
      + '.ptlist{display:grid;gap:8px;margin-top:10px}.ptitem{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px;align-items:center;border:1px solid var(--line);border-radius:10px;padding:10px 12px;background:var(--surface-2)}'
      + '.ptitem.on{border-color:var(--ok);background:var(--ok-bg)}.ptitem .pn{font-weight:700}.ptitem .pd{font-size:12px;color:var(--muted)}.ptitem .pp{font-family:var(--font-mono);font-weight:700;white-space:nowrap}'
      + '.pthist{margin:8px 0 0;padding:0;list-style:none;font-size:12.5px}.pthist li{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px;padding:5px 0;border-top:1px solid var(--line)}.pthist .plus{color:var(--ok);font-weight:700}.pthist .minus{color:var(--bad)}'
      + '.ptnote{font-size:12px;color:var(--muted);margin:6px 0 0}'
      + '.msrow{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px;align-items:center;padding:8px 0;border-top:1px solid var(--line)}.msrow:first-child{border-top:0}.msrow .mn{font-weight:700}.msrow .md{font-size:12px;color:var(--muted)}.msrow .bar{height:6px;border-radius:3px;background:var(--surface-2);overflow:hidden;margin-top:4px}.msrow .bar i{display:block;height:100%;background:var(--lamp)}'
      + '.tabbar button{position:relative}.tabbar button .tbdg{position:absolute;top:6px;right:calc(50% - 20px);width:9px;height:9px;border-radius:50%;background:var(--bad);box-shadow:0 0 0 2px var(--surface)}'
      + '.bettypes button.lock{opacity:.55;background:var(--surface-2)}.bettypes button.lock::after{content:"🔒";font-size:11px;margin-left:3px}'
      + '.slotchip.lock,.slotrow.lock .sr-name b::after{opacity:.9}.slotrow.lock .sr-name b::after{content:"　🔒"}'
      + '#gate{position:fixed;inset:0;z-index:70;display:flex;flex-direction:column;justify-content:flex-start;align-items:stretch;background:var(--night);color:var(--night-ink);font-family:var(--font-body);font-size:14px;line-height:1.6;letter-spacing:0;overflow:auto;-webkit-overflow-scrolling:touch;padding:calc(env(safe-area-inset-top,0px) + 28px) 20px calc(env(safe-area-inset-bottom,0px) + 24px)}'
      + '#gate .glogo{font-family:var(--font-display);font-size:40px;letter-spacing:.06em;text-align:center;margin:8px 0 2px}#gate .glogo em{font-style:normal;color:var(--lamp);font-family:var(--font-mark)}#gate .gsub{text-align:center;font-size:13px;opacity:.8;margin:0 0 18px}'
      + '#gate .gsec{background:rgba(243,240,230,.08);border:1px solid rgba(243,240,230,.18);border-radius:12px;padding:12px 14px;margin:0 0 12px;max-width:560px;width:100%;align-self:center}#gate .gsec h3{margin:0 0 6px;font-size:14.5px;color:var(--lamp)}#gate .gsec ul{margin:0;padding-left:1.2em;font-size:13.5px;line-height:1.7}#gate .gsec li{margin:2px 0}'
      + '#gate .gbtn{display:block;width:100%;max-width:560px;margin:8px auto 0;padding:14px;border-radius:12px;border:0;background:var(--lamp);color:#1C1300;font-size:17px;font-weight:700;cursor:pointer}'
      + '#gate.splash{justify-content:center;align-items:center;text-align:center}#gate.splash .gline{font-size:14px;opacity:.9;margin-top:10px}#gate.splash .gtap{font-size:12px;opacity:.6;margin-top:30px}'
      + '#gate.fade{opacity:0;transition:opacity .35s}@media (prefers-reduced-motion: reduce){#gate.fade{transition:none}}'
      + 'html.gateon{overflow:hidden}';
    document.head.appendChild(st);
  }
  function cards() {
    const set = $('#v-set'); if (!set || $('#setPoints')) return;
    css();
    const mk = (id, h2) => { const c = document.createElement('div'); c.className = 'card setsec'; c.id = id; c.innerHTML = `<h2>${h2}</h2><div class="ptbody"></div>`; return c; };
    const a = mk('setPoints', 'ポイント'), b = mk('setCustom', 'Pカスタム'), c = mk('setMission', 'ミッション');
    const first = set.firstChild;
    set.insertBefore(a, first); set.insertBefore(b, first); set.insertBefore(c, first);
    a.style.marginBottom = b.style.marginBottom = c.style.marginBottom = 'var(--gap)';
    set.addEventListener('click', onClick);
    paintAll();
  }
  const bal = () => B();
  // 所持ポイント（合計 → 内わけ：買ったP（パック）・サブスクのP・もらったP。まさちゃん「自分のポイントが、購入したポイントが何ポイントで、サブスクでもらった何ポイントかわかるようにして！」）
  function balanceHtml(b) {
    const lots = b.lots.filter(L => !L.expired && L.remain > 0).sort((x, y) => Date.parse(x.expires) - Date.parse(y.expires));
    let h = `<div class="ptbal"><span class="ptbig">${yen(b.total)}<small>P</small></span><span class="ptsub">いま使えるポイント（3つの合計）</span></div>`;
    h += `<div class="ptbk"><div><span>買ったP<small>パック・期限なし</small></span><b>${pts(b.paid_pack)}</b></div>`
      + `<div><span>サブスクのP<small>届いた日から30日</small></span><b>${pts(b.paid_sub)}</b></div>`
      + `<div><span>もらったP<small>はじめてのプレゼント・ミッション</small></span><b>${pts(b.free)}</b></div></div>`;
    if (lots.length) h += `<p class="ptnote">サブスクのP：${lots.map(L => `${yen(L.remain)}P は ${dayOf(L.expires)}まで`).join('・')}（届いた日から30日。次の月のPが届いても、期限までは使えるよ）</p>`;
    if (b.lost) h += `<p class="ptnote">期限が切れて消えたサブスクのP：${yen(b.lost)}P</p>`;
    if (W.gift && W.gift.state === 'already') h += '<p class="ptnote">はじめてのプレゼント（1,500P）は、前にこのアプリを入れたときに受け取りずみだよ。</p>';
    return h;
  }
  const price = id => { const p = (products || []).find(x => x.id === id); return p ? p.price : `${yen(P.PRODUCTS[id].yen)}円`; };
  // パック（買う）の 一覧
  function packsHtml() {
    let h = `<div class="ptlist">${P.PACKS.map(id => { const Pd = P.PRODUCTS[id]; return `<div class="ptitem"><div><div class="pn">${esc(Pd.name)}</div><div class="pd">${yen(Pd.points)}P（期限なし）</div></div><div class="row"><span class="pp">${esc(price(id))}</span><button class="btn primary" type="button" data-pt="buy" data-id="${id}">買う</button></div></div>`; }).join('')}</div>`;
    h += prodErr ? `<p class="ptnote">⚠️ ${esc(prodErr)}。値段は税込のめやす。買うときはApp Storeの表示が正しいよ</p>` : '';
    return h;
  }
  // サブスクの 一覧（加入中・次の 更新）
  function subsHtml() {
    const active = (subStatus && subStatus.active) || [];
    let h = `<div class="ptlist">${P.SUBS.map(id => { const Pd = P.PRODUCTS[id], on = active.find(x => x.product === id); return `<div class="ptitem${on ? ' on' : ''}"><div><div class="pn">${esc(Pd.name)}${on ? '　<span class="chip">加入中</span>' : ''}</div><div class="pd">毎月 ${yen(Pd.points)}P${Pd.bonus ? `（うち ${yen(Pd.bonus)}P おまけ）` : ''}・届いた日から30日 使えるよ${on && on.expires ? `・次の更新 ${dayOf(on.expires)}${on.willRenew === false ? '（更新しない）' : ''}` : ''}</div></div><div class="row"><span class="pp">月 ${esc(price(id))}</span>${on ? '' : `<button class="btn primary" type="button" data-pt="buy" data-id="${id}">はじめる</button>`}</div></div>`; }).join('')}</div>`;
    h += `<p class="ptnote">無料トライアルはないよ。プランの変更・解約は、端末の「設定」→ Apple ID → サブスクリプション。解約しても、届いたPは期限（30日）まで使えるよ。</p>`;
    h += prodErr ? `<p class="ptnote">⚠️ ${esc(prodErr)}</p>` : '';
    return h;
  }
  function paintPoints() {
    const box = $('#setPoints .ptbody'); if (!box || !W) return;
    const b = bal(), ui = paintPoints.ui || (paintPoints.ui = { show: '' });
    let h = balanceHtml(b);
    h += `<div class="row" style="margin-top:10px"><button class="btn primary" type="button" data-pt="show" data-v="buy" aria-pressed="${ui.show === 'buy'}">ポイントを買う</button><button class="btn" type="button" data-pt="show" data-v="sub" aria-pressed="${ui.show === 'sub'}">サブスク</button><button class="btn ghost" type="button" data-pt="show" data-v="hist" aria-pressed="${ui.show === 'hist'}">詳しく</button></div>`;
    h += `<p class="hint">1レースの読み込み（画像の読み取りから判定まで）に <b>200P</b> 使うよ。同じレースを読み直すときは 0P。買ったPから先に使うよ（サブスクのP → パックのP → もらったP）。</p>`;
    if (ui.show === 'buy') {
      h += packsHtml();
    } else if (ui.show === 'sub') {
      h += subsHtml();
    } else if (ui.show === 'hist') {
      const ev = W.events.slice().sort((x, y) => Date.parse(y.last || y.at) - Date.parse(x.last || x.at)).slice(0, 60);
      const lab = e => e.kind === 'purchase' ? `${(P.PRODUCTS[e.product] || {}).name || 'パック'}を買った` : e.kind === 'sub' ? `${(P.PRODUCTS[e.product] || {}).name || 'サブスク'}（${dayOf(e.expires)}まで）` : e.kind === 'gift' ? '初回プレゼント' : e.kind === 'mission' ? `ミッション：${e.what || ''}` : e.kind === 'unlock' ? `解放：${unlockName(e.what)}` : e.kind === 'refund' ? '返金' : (Array.isArray(e.what) ? e.what.slice(0, 3).join('・') + (e.what.length > 3 ? ` ほか${e.what.length - 3 + (e.more || 0)}件` : '') : e.what || '使った');
      h += `<ul class="pthist">${ev.map(e => `<li><span>${esc(dayOf(e.last || e.at))} ${esc(lab(e))}</span><span class="${+e.amount > 0 ? 'plus' : 'minus'}">${+e.amount > 0 ? '+' : ''}${yen(e.amount)}P</span></li>`).join('') || '<li><span class="muted">まだ何もないよ</span></li>'}</ul>`;
      h += `<p class="ptnote">買ったPの残り ${yen(b.paid_pack + b.paid_sub)}P・使ったP ${yen(b.used.paid_sub + b.used.paid_pack + b.used.free)}P（うち買ったPから ${yen(b.used.paid_sub + b.used.paid_pack)}P）</p>`;
      h += `<div class="row" style="margin-top:8px"><button class="btn" type="button" data-pt="restore">購入を復元</button></div><p class="ptnote">「購入を復元」は、サブスクの状態をAppleと合わせるよ。もう足したPはもう一度足さないよ。</p>`;
    }
    h += `<div class="banner warn">⚠️ <b>アプリを消すと、ポイント・解放したもの・記録はすべて消えて、もどせません。</b>ポイントはこの端末の中だけに入っているよ（ほかの端末には同期しないよ）。</div>`;
    box.innerHTML = h;
    paintPointsOv();
  }
  // ---------- ポイントの 窓（第4.84版・まさちゃん「このポイントの欄タップしたら、所持ポイントの確認と、ポイント&サブスクの購入選択画面が出てくるようにして！」）：
  //   上の帯の 所有ポイント（と「ポイントを買う」の ボタン）を 押すと 開く。所持ポイント・ポイントを 買う（パック）・サブスク を 1つの 窓に。履歴・復元は 設定タブの ポイントの「詳しく」へ ----------
  const COIN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M14.5 9.5a2.5 2.5 0 0 0-2.5-1.5c-1.7 0-2.5 1-2.5 2s.8 1.7 2.5 2 2.5 1 2.5 2-.8 2-2.5 2a2.5 2.5 0 0 1-2.5-1.5M12 6.5V8M12 16v1.5"/></svg>';
  function paintPointsOv() {
    const ov = $('#ptOv'); if (!ov || !W) return;
    const b = bal();
    $('.msn', ov).textContent = `合計 ${pts(b.total)}`;
    $('#ptBal', ov).innerHTML = balanceHtml(b) + `<p class="hint" style="margin:8px 0 0">1レースの読み込み（画像の読み取りから判定まで）に <b>200P</b> 使うよ。同じレースを読み直すときは 0P。買ったPから先に使うよ（サブスクのP → パックのP → もらったP）。</p>`;
    $('#ptBuy', ov).innerHTML = packsHtml();
    $('#ptSub', ov).innerHTML = subsHtml();
  }
  let ptPrev = null;
  function openPoints() {
    if (!W || $('#ptOv')) return;
    const ov = document.createElement('div'); ov.id = 'ptOv'; ov.className = 'tgov'; ov.setAttribute('role', 'dialog'); ov.setAttribute('aria-modal', 'true'); ov.setAttribute('aria-label', 'ポイント');
    ov.innerHTML = `<div class="msh"><h2>${COIN}ポイント</h2><span class="msn"></span><button class="btn" type="button" data-ms="close">とじる</button></div>`
      + '<div class="msb"><div class="card setsec"><h2>所持ポイント</h2><div class="ptbody" id="ptBal"></div></div>'
      + '<div class="card setsec"><h2>ポイントを買う（パック・期限なし）</h2><div class="ptbody" id="ptBuy"></div></div>'
      + '<div class="card setsec"><h2>サブスク（毎月とどく）</h2><div class="ptbody" id="ptSub"></div></div>'
      + '<div class="row" style="margin:0 0 8px"><button class="btn ghost" type="button" data-ms="hist">ポイントの履歴・購入を復元（設定タブ）</button></div>'
      + '<div class="banner warn">⚠️ <b>アプリを消すと、ポイント・解放したもの・記録はすべて消えて、もどせません。</b>ポイントはこの端末の中だけに入っているよ（ほかの端末には同期しないよ）。</div></div>';
    ov.addEventListener('click', e => { const c = e.target.closest('[data-ms]'); if (c && c.dataset.ms === 'close') { closePoints(); return; } if (c && c.dataset.ms === 'hist') { closePoints(); goSettings('points', 'hist'); return; } onClick(e); });
    ptPrev = document.activeElement;
    document.documentElement.classList.add('mson'); document.body.appendChild(ov);
    paintPointsOv();
    try { $('[data-ms=close]', ov).focus({ preventScroll: true }); } catch (e) { /* なし */ }
    loadProducts(false).then(() => paintPointsOv()).catch(() => {});
    refreshSubStatus().catch(() => {});
  }
  function closePoints() {
    const ov = $('#ptOv'); if (!ov) return;
    ov.remove(); if (!$('.tgov')) document.documentElement.classList.remove('mson');
    const b = $('#ptsPill'); if (b && b.focus) b.focus({ preventScroll: true }); else if (ptPrev && ptPrev.focus) ptPrev.focus({ preventScroll: true });
    ptPrev = null;
  }
  const TYPE_NAMES = { '複勝': '複勝', '枠複': '枠複', '枠単': '枠単', '馬連': '馬連', 'ワイド': 'ワイド', '3連複': '3連複' };
  function unlockName(key) {
    const k = String(key || ''); if (k.startsWith('type:')) return k.slice(5);
    if (k.startsWith('slot:')) { const n = +k.slice(5); try { return (TL.slots.names() || {})[n] || `マザーデータ${n}`; } catch (e) { return `マザーデータ${n}`; } }
    if (k.startsWith('theme:')) { try { const t = (window.TengelKisekae.list() || []).find(x => x.id === k.slice(6)); if (t) return `壁紙「${t.name}」`; } catch (e) { /* なし */ } return `壁紙 ${k.slice(6)}`; }
    return k;
  }
  function paintCustom() {
    const box = $('#setCustom .ptbody'); if (!box || !W) return;
    const t = total(), conf = paintCustom.conf || '';
    const btn = (key, cost) => { const ok = t >= cost; return conf === key ? `<button class="btn primary" type="button" data-pt="unlock2" data-key="${esc(key)}" data-cost="${cost}">${pts(cost)}を使って解放する（いま ${pts(t)}）</button><button class="btn ghost" type="button" data-pt="unlock0">やめる</button>` : `<button class="btn ${ok ? 'primary' : ''}" type="button" data-pt="unlock1" data-key="${esc(key)}" data-cost="${cost}">${ok ? '解放する' : 'Pが足りない'}</button>`; };
    let h = `<p class="hint" style="margin:0 0 6px"><b>Pカスタムで、自分だけのテンゲルを育てよう！</b></p><p class="hint" style="margin:0">ポイントで、使える券種とマザーデータの枠を増やせるよ。解放したものはずっと使えるよ（アプリを消すと消えるよ）。</p>`;
    h += `<h3 style="margin:12px 0 6px">券種（記録・買い目の予約で選べるもの）</h3><p class="ptnote" style="margin:0">はじめから：単勝・馬単・3連単</p><div class="ptlist">`;
    P.UNLOCK_TYPES.forEach(tp => { const key = 'type:' + tp, on = unlocked(key); h += `<div class="ptitem${on ? ' on' : ''}" data-key="${esc(key)}"><div><div class="pn">${esc(TYPE_NAMES[tp] || tp)}</div><div class="pd">${on ? '解放ずみ' : `1つ ${pts(P.COST.type)}`}</div></div><div class="row">${on ? '<span class="chip">使えるよ</span>' : btn(key, P.COST.type)}</div></div>`; });
    h += `</div><h3 style="margin:14px 0 6px">マザーデータの枠（自分のデータで参考的中率を出す）</h3><p class="ptnote" style="margin:0">1つ目はアプリに入っているデータ。2つ目・3つ目を解放すると、Excelや判定したレースで自分だけのマザーデータを作れるよ。</p><div class="ptlist">`;
    let names = {}; try { names = TL.slots.names() || {}; } catch (e) { /* なし */ }
    [2, 3].forEach(n => { const key = 'slot:' + n, on = slotUnlocked(n); h += `<div class="ptitem${on ? ' on' : ''}" data-key="${esc(key)}"><div><div class="pn">${n}つ目「${esc(names[n] || 'マザーデータ' + n)}」</div><div class="pd">${on ? '解放ずみ' : `1つ ${pts(P.COST.slot)}`}</div></div><div class="row">${on ? '<span class="chip">使えるよ</span>' : btn(key, P.COST.slot)}</div></div>`; });
    h += '</div>';
    box.innerHTML = h;
  }
  // ポイントミッション（記録の数）の 行：いちばん 上は つぎの ミッション・その 下に 受け取れる／受け取りずみ
  function missionRowsHtml() {
    const n = countedN(), ms = P.missions(n, W.events);
    const next = ms.find(m => !m.done);
    let h = `<p class="hint" style="margin:0 0 8px">200Pを使って判定して、結果を記録したレースの数でポイントがもらえるよ（同じレースは1回。Excelなどでまとめて入れた記録は数えないよ）。いま <b>${n}レース</b>${next ? `・次は ${next.n}レースで ${pts(next.reward)}` : ''}</p>`;
    h += '<div>';
    ms.slice().reverse().forEach(m => { const w = Math.min(100, Math.round(n / m.n * 100)); h += `<div class="msrow${m.claimable ? ' can' : ''}" data-mid="${esc(m.id)}"><div><div class="mn">${esc(m.label)}　<span class="muted" style="font-weight:400">${pts(m.reward)}</span></div><div class="md">${m.claimed ? '受け取りずみ' : m.done ? '受け取れるよ！' : `あと ${m.n - n}レース（${n}/${m.n}）`}</div><div class="bar"><i style="width:${w}%"></i></div></div><div>${m.claimable ? `<button class="btn primary" type="button" data-pt="claim" data-id="${m.id}">受け取る</button>` : m.claimed ? '<span class="chip">✓</span>' : ''}</div></div>`; });
    return h + '</div>';
  }
  // 壁紙のミッション（8.3・第4弾）：ポイントで解放した壁紙の枚数 → 帯の壁紙
  function wallRowsHtml() {
    const wn = P.wallCount(W.events), wms = P.wallMissions(wn, W.events);
    let h = `<p class="hint" style="margin:0 0 4px">設定の「着せ替え」でポイントを使って解放した壁紙の枚数で、帯の壁紙がもらえるよ（いつもの・帯の壁紙は数えないよ）。いま <b>${wn}枚</b></p><div>`;
    wms.forEach(m => { const w = Math.min(100, Math.round(wn / m.n * 100)); h += `<div class="msrow${m.claimable ? ' can' : ''}" data-mid="${esc(m.id)}"><div><div class="mn">壁紙を${m.n}枚あつめる　<span class="muted" style="font-weight:400">${esc(m.label)}</span></div><div class="md">${m.claimed ? '受け取りずみ' : m.done ? '受け取れるよ！' : `あと ${m.n - wn}枚（${wn}/${m.n}）`}</div><div class="bar"><i style="width:${w}%"></i></div></div><div>${m.claimable ? `<button class="btn primary" type="button" data-pt="claim" data-id="${m.id}">受け取る</button>` : m.claimed ? '<span class="chip">✓</span>' : ''}</div></div>`; });
    return h + '</div>';
  }
  function paintMission() {
    const box = $('#setMission .ptbody'); if (!box || !W) return;
    box.innerHTML = `<p class="hint" style="margin:0 0 8px">ミッションは、画面の上の<b>「ミッション」</b>からも見られるよ（受け取りもできるよ）。</p>` + missionRowsHtml()
      + '<h3 style="margin:14px 0 4px">壁紙のミッション</h3>' + wallRowsHtml();
  }
  // ---------- ミッションの 窓（第4.82版・まさちゃん「ミッションの達成状況分かりにくいから、説明書とかポイント表示とかが入ってあたりに別項目として、ミッションて欄追加して！
  //   壁紙ミッション ポイントミッション 見直し基準進捗状況」「受け取りもそこでできるようにして！」）：上の帯の「ミッション」を 押すと 開く。
  //   ポイントミッション（記録の 数）・壁紙ミッション・見直し基準の 進み具合（実測・回収タブと 同じ：chk1.js の TengelReview）。受け取るも ここで ----------
  const TROPHY = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0z"/><path d="M7 6H4a1 1 0 0 0-1 1 4 4 0 0 0 4 4M17 6h3a1 1 0 0 1 1 1 4 4 0 0 1-4 4"/></svg>';
  // 受け取れる 数の 印：メッセージ（ふきだし）の 絵＋数（まさちゃん「メッセージのマークを背景つけて、メッセージが溜まってるよ！って分かりやすくして！」）
  const BUBBLE = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M4 3h16a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H9l-5 4v-4H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z"/></svg>';
  function claimableN() { if (!W) return 0; return P.missions(countedN(), W.events).filter(m => m.claimable).length + P.wallMissions(P.wallCount(W.events), W.events).filter(m => m.claimable).length; }
  function reviewHtml() {
    try { if (window.TengelReview) return window.TengelReview() || ''; } catch (e) { /* なし */ }
    return '';
  }
  function paintMissionOv() {
    const ov = $('#msOv'); if (!ov || !W) return;
    const n = claimableN();
    $('.msn', ov).textContent = n ? `受け取れるのが ${n}つ！` : '';
    $('#msPts', ov).innerHTML = missionRowsHtml();
    $('#msWall', ov).innerHTML = wallRowsHtml();
    const rv = reviewHtml();
    $('#msRev', ov).innerHTML = rv || '<div class="card"><h2>見直し基準の進み具合</h2><p class="hint" style="margin:0">マザーデータに接続してから見られるよ（実測・回収タブと同じものだよ）。</p></div>';
  }
  let msPrev = null;
  function openMissions() {
    if (!W || $('#msOv')) return;
    const ov = document.createElement('div'); ov.id = 'msOv'; ov.className = 'tgov'; ov.setAttribute('role', 'dialog'); ov.setAttribute('aria-modal', 'true'); ov.setAttribute('aria-label', 'ミッション');
    ov.innerHTML = `<div class="msh"><h2>${TROPHY}ミッション</h2><span class="msn"></span><button class="btn" type="button" data-ms="close">とじる</button></div>`
      + '<div class="msb"><div class="card setsec"><h2>ポイントミッション</h2><div class="ptbody" id="msPts"></div></div>'
      + '<div class="card setsec"><h2>壁紙ミッション</h2><div class="ptbody" id="msWall"></div></div><div id="msRev"></div>'
      + '<p class="hint" style="margin:0 0 6px">ポイントミッションは、200Pを使って判定して記録したレースの数（Excelなどでまとめて入れた記録は数えないよ）。見直し基準は、判定して着順を入れて、マザーデータにも入れたレースで進むよ。</p></div>';
    ov.addEventListener('click', e => { const c = e.target.closest('[data-ms]'); if (c && c.dataset.ms === 'close') { closeMissions(); return; } onClick(e); });
    msPrev = document.activeElement;
    document.documentElement.classList.add('mson'); document.body.appendChild(ov);
    paintMissionOv();
    try { $('[data-ms=close]', ov).focus({ preventScroll: true }); } catch (e) { /* なし */ }
  }
  function closeMissions() {
    const ov = $('#msOv'); if (!ov) return;
    ov.remove(); if (!$('.tgov')) document.documentElement.classList.remove('mson');
    const b = $('#msBtn'); if (b && b.focus) b.focus({ preventScroll: true }); else if (msPrev && msPrev.focus) msPrev.focus({ preventScroll: true });
    msPrev = null;
  }
  document.addEventListener('keydown', e => { if (e.key !== 'Escape') return; if ($('#ptOv')) closePoints(); else if ($('#msOv')) closeMissions(); });
  // 上の帯の ならび：ロゴ → 所有ポイント → 説明書 →（テスト版の 印）→ ミッション →（段の きりかえ）→ マザーデータの 札（説明書は pwa_ui.js が あとから 入れる ことが あるので、描く たびに そろえる）
  function orderTop(top) {
    const seq = [$('.brand', top), $('#ptsPill'), $('#manBtn'), $('#testTag'), $('#msBtn'), $('.tbrk', top), $('#dbpill')].filter(Boolean);
    let prev = null;
    for (const el of seq) { if (prev && prev.nextElementSibling !== el) prev.insertAdjacentElement('afterend', el); prev = el; }
  }
  // 上の帯の「ミッション」（説明書の 下の 段・右よせ）：つぎの ミッションの 進み具合（いま／つぎ）と、受け取れる 数（水色の 数字だけ。まさちゃん「ミッションの①みたいな通知してくれてる◯は水色にして！」
  //   →「ミッション通知①の通知◯いらないかも！ 数字だけでいいや！」→「通知の数字、具ぎりが無くて分かりにくいから、メッセージのマークを背景つけて、メッセージが溜まってるよ！って分かりやすくして！」
  //   ＝四角に ふきだしの 絵と 数。色は まさちゃん「メッセージのマークの色、薄い黄緑にして！」＝うすい 黄緑 #D4F5A6）
  function missionBtn() {
    const top = $('header.top .top-in'); if (!top) return;
    let b = $('#msBtn');
    if (!b) {
      b = document.createElement('button'); b.type = 'button'; b.id = 'msBtn'; b.className = 'manbtn msbtn'; b.setAttribute('aria-label', 'ミッション（押すと開くよ）');
      b.addEventListener('click', openMissions);
      top.insertBefore(b, $('#manBtn') || $('#dbpill') || null);
    }
    if (!$('.tbrk', top)) { const k = document.createElement('i'); k.className = 'tbrk'; k.setAttribute('aria-hidden', 'true'); b.insertAdjacentElement('afterend', k); }
    orderTop(top);
    const n = W ? countedN() : 0, next = W ? P.missions(n, W.events).find(m => !m.done) : null, c = claimableN();
    b.innerHTML = `${TROPHY}ミッション${next ? `<span class="mp">${n}/${next.n}</span>` : ''}${c ? `<span class="mbd" aria-label="受け取れるミッション ${c}つ">${BUBBLE}${c}</span>` : ''}`;
    b.classList.toggle('hot', c > 0);
    b.title = c ? `受け取れるミッションが ${c}つ あるよ` : next ? `つぎのミッション：${next.n}レース記録で ${pts(next.reward)}（いま ${n}レース）` : 'ミッション';
  }
  function paintBadge() {
    const tb = $('.tabbar [data-tab=set]'); if (!tb || !W) return;
    const on = P.missions(countedN(), W.events).some(m => m.claimable) || P.wallMissions(P.wallCount(W.events), W.events).some(m => m.claimable);
    let d = tb.querySelector('.tbdg'); if (on && !d) { d = document.createElement('span'); d.className = 'tbdg'; d.setAttribute('aria-label', '受け取れるミッションがあるよ'); tb.appendChild(d); } else if (!on && d) d.remove();
  }
  function paintHint() {
    const el = $('#ocrHint'); if (!el || !W) return;
    if (!paintHint.base) paintHint.base = el.textContent;
    el.textContent = `${paintHint.base}・1レース 200P（いま ${pts(total())}）`;
  }
  function paintAll() { paintPoints(); paintCustom(); paintMission(); paintBadge(); paintHint(); topBar(); missionBtn(); dbPillLink(); paintMissionOv(); }
  async function onClick(e) {
    const b = e.target.closest('[data-pt]'); if (!b) return;
    const act = b.dataset.pt;
    if (act === 'show') { const ui = paintPoints.ui || (paintPoints.ui = {}); ui.show = ui.show === b.dataset.v ? '' : b.dataset.v; paintPoints(); if (ui.show === 'buy' || ui.show === 'sub') { await loadProducts(false); if (ui.show === 'sub') await refreshSubStatus(); paintPoints(); } return; }
    if (act === 'buy') return buy(b.dataset.id, b);
    if (act === 'restore') return restore(b);
    if (act === 'claim') return claim(b.dataset.id);
    if (act === 'unlock1') { paintCustom.conf = b.dataset.key; paintCustom(); return; }
    if (act === 'unlock0') { paintCustom.conf = ''; paintCustom(); return; }
    if (act === 'unlock2') {
      const key = b.dataset.key, cost = +b.dataset.cost; paintCustom.conf = '';
      b.disabled = true;
      const ok = await unlock(key, cost);
      if (ok) { toast(`✅ ${unlockName(key)}を解放したよ（残り ${pts(total())}）`, 3600); try { document.dispatchEvent(new CustomEvent('tengel:slots')); } catch (x) { /* なし */ } }
      else toast(`Pが足りないよ（${pts(cost)}いる・いま ${pts(total())}）`, 3600);
      paintCustom();
      if (ok) unlockFx(`#setCustom .ptitem[data-key="${key}"]`, '解放！');
    }
  }
  // 設定タブの中の場所へ（ほかの画面の「ポイントを買う」ボタンなど）
  function goSettings(sec, show) {
    const tb = $('.tabbar [data-tab=set]');
    if (tb && getComputedStyle(tb.parentNode).display !== 'none') tb.click(); else { const t2 = $('.tabs-top [data-tab=set]'); if (t2) t2.click(); }
    const id = { points: 'setPoints', custom: 'setCustom', mission: 'setMission', kisekae: 'setKisekae', mother: 'setMother' }[sec] || 'setPoints';
    if (sec === 'points') { paintPoints.ui = { show: show || 'buy' }; paintPoints(); loadProducts(false).then(paintPoints); }
    setTimeout(() => { const s = document.getElementById(id); if (s) s.scrollIntoView({ block: 'start' }); }, 60);
  }
  // data-gopt="points"（上の帯の 所有ポイント・「ポイントを買う」の ボタン）は ポイントの 窓（第4.84版）。ほかは 設定タブの その 場所へ
  document.addEventListener('click', e => { const b = e.target.closest && e.target.closest('[data-gopt]'); if (b) { e.preventDefault(); if (b.dataset.gopt === 'points') openPoints(); else goSettings(b.dataset.gopt); } });
  // 上の帯の マザーデータの 札 → 設定タブの マザーデータ（第4.84版・まさちゃん「マザーデータをタップしたら設定のマザーデータのところに飛ぶようにして！」）
  function dbPillLink() {
    const d = $('#dbpill'); if (!d || d.dataset.gopt) return;
    d.dataset.gopt = 'mother'; d.setAttribute('role', 'button'); d.tabIndex = 0; d.setAttribute('aria-label', 'マザーデータ（押すと設定のマザーデータへ）'); d.style.cursor = 'pointer';
    d.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); goSettings('mother'); } });
  }

  // ---------- 拡大（2本指）：ふだんは3倍まで。演出・アプリを開いた時の画面では1倍にもどして止める ----------
  const VP = 'width=device-width,initial-scale=1,viewport-fit=cover';
  function viewport(c) { let m = $('meta[name=viewport]'); if (!m) { m = document.createElement('meta'); m.name = 'viewport'; document.head.appendChild(m); } m.setAttribute('content', c); }
  let zoomLocked = false;
  function lockZoom(lock) {
    zoomLocked = !!lock;
    viewport(lock ? VP + ',maximum-scale=1,user-scalable=no' : VP + ',maximum-scale=3');
    N.zoom(lock ? { reset: true, lock: true } : { lock: false }).catch(() => { /* 前の版のアプリ */ });
  }
  lockZoom(false);

  // ---------- アプリを開いた時の画面（19章）：はじめては全部＋「はじめる」、2回目からは短く約2秒 ----------
  const GATE = {
    keiba: ['20歳未満の方は馬券を買えません（法律で決まっています）。', '競馬は無理のない範囲で楽しみましょう。のめり込みが心配なときは、ひとりでかかえず、お住まいの地域の相談窓口（精神保健福祉センターなど）に相談しましょう。', '馬券は公式の発売所や公式のサービスで買いましょう。'],
    app: ['テンゲルは、オッズと過去のデータからレースの目安を出すアプリです。結果やもうけを約束するものではありません。', 'テンゲルで馬券は買えません（予約はご自身のためのメモです）。買うかどうかは、ご自身で決めてください。', 'データはこの端末の中だけに入ります。アプリを消すと、記録・ポイントはすべて消えて、もどせません。'],
    fun: ['テンゲルには、判定・予約・記録・Pカスタム・ミッション・着せ替え・的中の演出など、たくさんの遊び方があります。', 'でも、いちばんの目的は、はば広いみなさんに競馬をもっと楽しんでもらうこと。どの機能を使うか、使わないかは、お客様が自由に選べます。', '予想の仕方も楽しみ方も人それぞれ。データで楽しむ人も、直感や好きな馬で楽しむ人も、みんなの競馬です。テンゲルは、その楽しみ方のひとつです。'],
    short: '馬券は20歳から・無理のない範囲で楽しもう'
  };
  const GATE_KEY = 'tengel.gateSeen';
  const gateHTML = () => `<div class="glogo">テンゲル<em>Ⅲ</em></div><p class="gsub">はじめに、3つだけ読んでね</p>`
    + `<div class="gsec"><h3>競馬の注意</h3><ul>${GATE.keiba.map(t => `<li>${esc(t)}</li>`).join('')}</ul></div>`
    + `<div class="gsec"><h3>アプリの注意</h3><ul>${GATE.app.map(t => `<li>${esc(t)}</li>`).join('')}</ul></div>`
    + `<div class="gsec"><h3>テンゲルの楽しみ方</h3><ul>${GATE.fun.map(t => `<li>${esc(t)}</li>`).join('')}</ul></div>`;
  function gateOpen() {
    css();
    let g = $('#gate');
    if (!g) { g = document.createElement('div'); g.id = 'gate'; document.body.insertBefore(g, document.body.firstChild); }
    g.hidden = false; g.setAttribute('role', 'dialog'); g.setAttribute('aria-modal', 'true'); g.setAttribute('aria-label', 'はじめに');
    document.documentElement.classList.add('gateon');
    lockZoom(true);
    let seen = false; try { seen = localStorage.getItem(GATE_KEY) === '1'; } catch (e) { seen = false; }
    if (!seen) {
      g.className = ''; g.innerHTML = gateHTML() + '<button class="gbtn" type="button" id="gateGo">はじめる</button>';
      $('#gateGo').addEventListener('click', () => { try { localStorage.setItem(GATE_KEY, '1'); } catch (e) { /* 覚えられなくてもOK */ } TL.putSetting('gate', { seen: true, at: new Date().toISOString() }).catch(() => {}); gateClose(); });
    } else {
      g.className = 'splash'; g.innerHTML = `<div class="glogo">テンゲル<em>Ⅲ</em></div><p class="gline">${esc(GATE.short)}</p><p class="gtap">タップでとばせるよ</p>`;
      const t = setTimeout(gateClose, 2000);
      g.addEventListener('click', () => { clearTimeout(t); gateClose(); }, { once: true });
    }
  }
  function gateClose() {
    const g = $('#gate'); if (!g || g.hidden) return;
    const done = () => { g.hidden = true; g.innerHTML = ''; g.className = ''; document.documentElement.classList.remove('gateon'); lockZoom(false); try { document.dispatchEvent(new CustomEvent('tengel:gate')); } catch (e) { /* なし */ } };
    if (reduced()) return done();
    g.classList.add('fade'); setTimeout(done, 380);
  }
  // 設定 →「このアプリについて」にも同じ文を出す（いつでも読めるように）
  function aboutGate() {
    const ab = $('#setAbout'); if (!ab || $('#abGate')) return;
    const d = document.createElement('details'); d.id = 'abGate';
    d.innerHTML = `<summary>はじめに（競馬の注意・アプリの注意・楽しみ方）</summary><div><h3>競馬の注意</h3><ul>${GATE.keiba.map(t => `<li>${esc(t)}</li>`).join('')}</ul><h3>アプリの注意</h3><ul>${GATE.app.map(t => `<li>${esc(t)}</li>`).join('')}</ul><h3>テンゲルの楽しみ方</h3><ul>${GATE.fun.map(t => `<li>${esc(t)}</li>`).join('')}</ul></div>`;
    const first = ab.querySelector('details'); if (first) ab.insertBefore(d, first); else ab.appendChild(d);
  }

  // ---------- 上の帯：所有ポイント（購入P・サブスクP）・説明書の 置き場（第4.59版・まさちゃんの指定 2026-10-25） ----------
  // 購入P＝パックで 買ったP＋もらったP（消えない）・サブスクP＝サブスクの P（届いた 日から 30日）※仮。押すと 設定の ポイントへ
  function topBar() {
    if (!document.getElementById('ptsCss')) {
      const st = document.createElement('style'); st.id = 'ptsCss';
      /* 上の帯の ならび（第4.83版・まさちゃん「説明書をポイントの横に配置できない？ その下にミッション、その下にマザーデータ」）：
         ロゴ・所有ポイント・説明書 ／ ミッション ／ マザーデータの 札（iPhone：3段。ミッションと 札は 右よせ・ミッションの あとで 段を かえる .tbrk）。
         iPad の たて（〜899px）は 2段：ロゴ・ポイント・説明書 … ミッション ／ 札（右よせ）。広い 画面（900px〜）は 1段：ロゴ・ポイント・説明書 … ミッション・札。
         iPhone（〜599px）の 所有ポイントは「購入／サブスク」の 字を 上・P を 下の 2行に（横に 説明書が 入る はば） */
      st.textContent = '.manbtn{order:0!important}#manBtn{margin-left:0!important}#msBtn{margin-left:auto!important}#dbpill{margin-left:0}.brand .ver:empty{display:none}.tbrk{display:none;flex-basis:100%;height:0;margin:-8px 0 0}'

        + '#ptsPill{display:inline-flex;align-items:stretch;flex:none;margin:0;border-radius:999px;border:1px solid rgba(243,240,230,.3);background:rgba(243,240,230,.08);color:var(--night-ink);font:inherit;font-size:11.5px;line-height:1.3;white-space:nowrap;cursor:pointer;padding:0;overflow:hidden}'
        + '#ptsPill .pp{display:inline-flex;align-items:baseline;gap:4px;padding:4px 9px}#ptsPill .pp+.pp{border-left:1px solid rgba(243,240,230,.25)}'
        + '#ptsPill .pl{font-size:10px;opacity:.8;letter-spacing:.04em}#ptsPill .pv{font-family:var(--font-mono);font-weight:700;font-size:12.5px}#ptsPill .pv small{font-size:10px;margin-left:1px}'
        + '#ptsPill:focus-visible{outline:2px solid var(--lamp);outline-offset:2px}'
        + '#testTag{flex:none;font-size:10.5px;font-weight:700;letter-spacing:.06em;padding:2px 7px;border-radius:6px;background:#E2A23B;color:#1B1F2A}'
        /* 上の帯の「ミッション」（第4.82版）：説明書の 左。iPhone では 3段に なる（ミッション・説明書 → マザーデータの 印）ので 段の あいだは せまく */
        + 'header.top .top-in{row-gap:8px}#msBtn{cursor:pointer;font:inherit;font-size:12.5px;font-weight:700;line-height:1.5;position:relative}'
        + '#msBtn .mp{font-family:var(--font-mono);font-size:11px;font-weight:700;opacity:.85;margin-left:1px}'
        + '#msBtn .mbd{display:inline-flex;align-items:center;gap:3px;height:18px;padding:0 6px 0 5px;border-radius:7px;background:#D4F5A6;color:#1F3A0E;font-family:var(--font-mono);font-size:12px;font-weight:700;line-height:1;margin-left:4px}'
        + '#msBtn .mbd svg{width:12px;height:12px;color:#1F3A0E}'
        + '#msBtn.hot{background:rgba(226,162,59,.34);border-color:var(--lamp)}'
        + '.tgov{position:fixed;inset:0;z-index:60;background:var(--bg);color:var(--ink);display:flex;flex-direction:column}'
        + '.tgov .msh{flex:none;display:flex;align-items:center;gap:10px;padding:calc(var(--sat,0px) + 10px) 16px 10px;background:var(--ks-hd,var(--night));color:var(--night-ink);border-bottom:var(--ks-hdB,3px solid var(--lamp))}'
        + '.tgov .msh h2{margin:0;flex:none;display:inline-flex;align-items:center;gap:7px;font-size:17px;font-weight:700;letter-spacing:.02em}.tgov .msh h2 svg{width:19px;height:19px;color:var(--lamp)}'
        + '.tgov .msh .msn{flex:1;min-width:0;font-size:12px;font-weight:700;color:var(--lamp);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}'
        + '.tgov .msh .btn{flex:none;padding:6px 12px;background:rgba(243,240,230,.1);color:var(--night-ink);border-color:rgba(243,240,230,.35)}'
        + '.tgov .msb{flex:1;min-height:0;overflow:auto;-webkit-overflow-scrolling:touch;padding:var(--gap) 16px calc(var(--sab,0px) + 28px)}.tgov .msb .card{margin:0 0 var(--gap)}#msOv #msRev .card{margin-top:0!important}'
        + '.tgov .msrow.can{background:var(--ok-bg);margin:0 -8px;padding:8px;border-radius:8px;border-top:0}'
        + 'html.mson{overflow:hidden}'
        + '#setTest{margin-bottom:var(--gap)}#setTest .row{flex-wrap:wrap}#setTest .btn{font-size:12.5px;padding:7px 10px}'
        + '@media (max-width:899px){.tbrk{display:block}#dbpill{margin-left:auto}}'
        + '@media (max-width:599px){header.top .top-in{column-gap:8px}'
        + '#ptsPill .pp{flex-direction:column;align-items:center;justify-content:center;gap:0;padding:3px 6px 2px}#ptsPill .pl{font-size:9px;line-height:11px;letter-spacing:.02em}#ptsPill .pv{font-size:12px;line-height:14px}#ptsPill .pv small{font-size:9.5px}}';
      document.head.appendChild(st);
    }
    const top = $('header.top .top-in'), brand = $('header.top .brand');
    if (!top || !brand) return;
    let pill = $('#ptsPill');
    if (!pill) {
      pill = document.createElement('button'); pill.type = 'button'; pill.id = 'ptsPill'; pill.setAttribute('data-gopt', 'points'); pill.setAttribute('aria-label', '所有ポイント（押すとポイントの窓：所持ポイント・買う・サブスク）');
      brand.insertAdjacentElement('afterend', pill);
      if (window.__TEST && !$('#testTag')) { const t = document.createElement('span'); t.id = 'testTag'; t.textContent = 'テスト版'; pill.insertAdjacentElement('afterend', t); }
    }
    const b = W ? B() : { paid_pack: 0, paid_sub: 0, free: 0 };
    const buy = b.paid_pack + b.free, sub = b.paid_sub;
    pill.innerHTML = `<span class="pp"><span class="pl">購入</span><span class="pv">${yen(buy)}<small>P</small></span></span><span class="pp"><span class="pl">サブスク</span><span class="pv">${yen(sub)}<small>P</small></span></span>`;
    pill.title = `購入P ${yen(buy)}（買ったP ${yen(b.paid_pack)}＋もらったP ${yen(b.free)}）・サブスクP ${yen(sub)}`;
  }

  // ---------- テスト版（TENGEL_TEST=1 で 作った アプリだけ・App Store には 出さない）：はじめから 10,000P・設定の いちばん上に「テスト版の道具」 ----------
  const TEST_GIFT = 10000;
  async function testGift() {
    if (!window.__TEST || !W || P.has(W.events, 'gift-test')) return;
    const need = TEST_GIFT - total(); if (need <= 0) return;   // 初回の 1,500P と 合わせて ちょうど 10,000P に（しるしが あって 1,500P が 出ない 端末では 10,000P）
    W.events.push(P.giftEvent(Date.now(), need, 'gift-test', 'テスト版のポイント'));
    await save(); paintAll();
    toast(`🧪 テスト版：はじめから ${pts(TEST_GIFT)} 入って いるよ`, 3200);
  }
  // 第4.81版（まさちゃん「ノーマルど的中のノーマルど的中ボタン入れて！ ど的中紫雷的中は、極ど的中ボタンにして！」）：ど的中は ノーマルど的中（nd：動画）と
  // 極ど的中（sd：紫電）の 2つ（くじで どちらか）。前の「ど的中」（fz：本番では もう 出ない 前の 形）は ノーマルど的中に いれかえた
  // 第4.86版（まさちゃん「あと一枚目の的中ボタン各種の、赤い×が書いてある演出消して！」）：隠れど的中・超プレミアムど的中・神様的中は アプリから 消した（ボタンも なし）
  const TEST_FX = [['hit', '的中'], ['big', 'デカ的中'], ['nd', 'ノーマルど的中'], ['sd', '極ど的中'], ['miss', 'ハズレ'], ['pc', 'プレミアムど的中'], ['sgd', '超神様的中'], ['spg', '超プレミアム神様的中']];
  // ためす 結果：14頭・3連単 11→8→2（11＝11番人気の 超大穴・8＝8番人気の 大穴・2＝2番人気）・馬単 11→8 的中・ワイド 不的中（的中は 馬単だけ・ハズレは 当たりなし）
  function testSpec(kind) {
    const tri = { t: '3連単', state: '的中', hits: [[11, 8, 2]], n: 18 }, um = { t: '馬単', state: '的中', hits: [[11, 8]], n: 9 }, wd = { t: 'ワイド', state: '不的中', hits: [], n: 6 };
    const rows = kind === 'miss' ? [Object.assign({}, tri, { state: '不的中', hits: [] }), Object.assign({}, um, { state: '不的中', hits: [] }), wd] : kind === 'hit' ? [Object.assign({}, tri, { state: '不的中', hits: [] }), um, wd] : [tri, um, wd];
    return { r: 9, n: 14, rows: rows, ranks: { 11: 11, 8: 8, 2: 2, 6: 1, 10: 3 }, force: kind };
  }
  function testCard() {
    if (!window.__TEST) return;
    const set = $('#v-set'); if (!set || $('#setTest')) return;
    const c = document.createElement('div'); c.className = 'card setsec'; c.id = 'setTest';
    c.innerHTML = '<h2>テスト版の道具</h2><p class="hint" style="margin:0 0 8px">この カードは テスト版だけ（App Store に 出す アプリには ない）。はじめから 10,000P 入って いるよ。</p>'
      + '<div class="row" style="margin-bottom:10px"><button type="button" class="btn" data-test="pts">10,000P 足す</button></div>'
      + '<p class="hint" style="margin:0 0 6px">的中ボタンを ためす（14頭・3連単 11→8→2 の 結果で 出す。くじは ひかない）</p>'
      + '<div class="row">' + TEST_FX.map(x => `<button type="button" class="btn" data-test="fx" data-kind="${x[0]}">${x[1]}</button>`).join('') + '</div>';
    set.insertBefore(c, set.firstChild);
    c.addEventListener('click', async e => {
      const b = e.target.closest('[data-test]'); if (!b) return;
      if (b.dataset.test === 'pts') { W.events.push(P.giftEvent(Date.now(), TEST_GIFT, 'gift-test-' + Date.now(), 'テスト版のポイント')); await save(); paintAll(); toast(`テスト用に ${pts(TEST_GIFT)}を 足したよ（いま ${pts(total())}）`, 2600); }
      else if (b.dataset.test === 'fx' && window.TengelFx) { try { window.TengelFx.prime(); } catch (x) { /* なし */ } window.TengelFx.show(testSpec(b.dataset.kind)); }
    });
  }

  // ---------- 起動 ----------
  let resolveReady; const walletReady = new Promise(r => { resolveReady = r; });
  async function boot() {
    gateOpen();
    cards(); testCard();
    try {
      await TL.ready;
      const doc = await TL.getMeta('wallet').catch(() => null);
      W = normalize(doc);
      if (!doc) await save();
    } catch (e) { W = normalize(null); }
    resolveReady();
    paintAll();
    try { await giftCheck(); } catch (e) { /* つぎに開いたとき */ }
    try { await testGift(); } catch (e) { /* テスト版だけ */ }
    pullTransactions().catch(() => {});
    refreshSubStatus().catch(() => {});
  }
  window.TengelWallet = {
    on: true, ready: walletReady, COST: P.COST,
    balance: () => B(), total, events: () => (W ? W.events.slice() : []), countedN,
    readCharge, countRace, unlocked, typeLocked, slotUnlocked, unlock, claim, goSettings, lockZoom, gateOpen, gateClose, openMissions, closeMissions, openPoints, closePoints,
    // 自動バックアップ（アプリの中）に入れる・戻す。書き出すバックアップ（共有シート）には入れない
    snapshot: () => (W ? JSON.parse(JSON.stringify(W)) : null),
    restore: async snap => { await walletReady; if (!snap || !Array.isArray(snap.events)) return false; const cur = W.events.length; W = normalize(snap); await save(); await giftCheck().catch(() => {}); return W.events.length !== cur; },
    // まだ何も使っていない（初回プレゼントだけ・読み込みも記録もなし）なら「空」＝自動バックアップの台帳を戻してよい
    isEmpty: () => !W || (!W.events.some(e => !/^gift-(first|test)/.test(e.id)) && !W.paid.length && !Object.keys(W.counted).length)
  };
  document.addEventListener('tengel:slots', () => { if (W) { paintCustom(); } });
  document.addEventListener('tengel:tab', e => { if (e.detail === 'set' && W) { paintAll(); aboutGate(); testCard(); } });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
  setTimeout(aboutGate, 50);
})();
