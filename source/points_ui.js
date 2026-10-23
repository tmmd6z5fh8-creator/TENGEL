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
    const race = { date: d.date || form.date || '', venue: String(d.venue || form.venue || ''), r: +(d.r || form.r) || 0, rname: d.rname || form.rname || '', start: d.start || form.start || '', dist: +(d.dist || form.dist) || 0 };
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
    toast(claim.length ? `🏆 ${n}レース目の記録。受け取れるミッションがあるよ（設定タブ）` : `ミッション：記録 ${n}レース目`, 3600);
    return true;
  }
  const countedN = () => W ? Object.keys(W.counted).length : 0;
  async function claim(id) {
    const m = P.missions(countedN(), W.events).find(x => x.id === id);
    if (!m || !m.claimable) return;
    W.events.push(P.missionEvent(m, Date.now()));
    await save();
    toast(`🎉 ${m.label}の ${pts(m.reward)} を受け取ったよ（合計 ${pts(total())}）`, 4000);
  }

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
    st.textContent = '#setPoints .ptbal{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}#setPoints .ptbig{font-family:var(--font-display);font-size:34px;line-height:1.1}'
      + '#setPoints .ptbig small{font-size:16px;margin-left:2px}#setPoints .ptsub{font-size:12.5px;color:var(--muted)}'
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
  function paintPoints() {
    const box = $('#setPoints .ptbody'); if (!box || !W) return;
    const b = bal(), ui = paintPoints.ui || (paintPoints.ui = { show: '' });
    const lots = b.lots.filter(L => !L.expired && L.remain > 0).sort((x, y) => Date.parse(x.expires) - Date.parse(y.expires));
    const giftNote = W.gift && W.gift.state === 'already' ? '<p class="ptnote">はじめてのプレゼント（1,500P）は、前にこのアプリを入れたときに受け取りずみだよ。</p>' : '';
    let h = `<div class="ptbal"><span class="ptbig">${yen(b.total)}<small>P</small></span><span class="ptsub">買ったP ${yen(b.paid_pack + b.paid_sub)}（うちサブスク ${yen(b.paid_sub)}）・もらったP ${yen(b.free)}</span></div>`;
    if (lots.length) h += `<p class="ptnote">サブスクのP：${lots.map(L => `${yen(L.remain)}P は ${dayOf(L.expires)}まで`).join('・')}（届いた日から30日。次の月のPが届いても、期限までは使えるよ）</p>`;
    if (b.lost) h += `<p class="ptnote">期限が切れて消えたサブスクのP：${yen(b.lost)}P</p>`;
    h += giftNote;
    h += `<div class="row" style="margin-top:10px"><button class="btn primary" type="button" data-pt="show" data-v="buy" aria-pressed="${ui.show === 'buy'}">ポイントを買う</button><button class="btn" type="button" data-pt="show" data-v="sub" aria-pressed="${ui.show === 'sub'}">サブスク</button><button class="btn ghost" type="button" data-pt="show" data-v="hist" aria-pressed="${ui.show === 'hist'}">くわしく</button></div>`;
    h += `<p class="hint">1レースの読み込み（画像の読み取りから判定まで）に <b>200P</b> 使うよ。同じレースを読み直すときは 0P。買ったPから先に使うよ（サブスクのP → パックのP → もらったP）。</p>`;
    const price = id => { const p = (products || []).find(x => x.id === id); return p ? p.price : `${yen(P.PRODUCTS[id].yen)}円`; };
    if (ui.show === 'buy') {
      h += `<div class="ptlist">${P.PACKS.map(id => { const Pd = P.PRODUCTS[id]; return `<div class="ptitem"><div><div class="pn">${esc(Pd.name)}</div><div class="pd">${yen(Pd.points)}P（期限なし）</div></div><div class="row"><span class="pp">${esc(price(id))}</span><button class="btn primary" type="button" data-pt="buy" data-id="${id}">買う</button></div></div>`; }).join('')}</div>`;
      h += prodErr ? `<p class="ptnote">⚠️ ${esc(prodErr)}。値段は税込のめやす。買うときはApp Storeの表示が正しいよ</p>` : '';
    } else if (ui.show === 'sub') {
      const active = (subStatus && subStatus.active) || [];
      h += `<div class="ptlist">${P.SUBS.map(id => { const Pd = P.PRODUCTS[id], on = active.find(x => x.product === id); return `<div class="ptitem${on ? ' on' : ''}"><div><div class="pn">${esc(Pd.name)}${on ? '　<span class="chip">加入中</span>' : ''}</div><div class="pd">毎月 ${yen(Pd.points)}P${Pd.bonus ? `（うち ${yen(Pd.bonus)}P おまけ）` : ''}・届いた日から30日 使えるよ${on && on.expires ? `・次の更新 ${dayOf(on.expires)}${on.willRenew === false ? '（更新しない）' : ''}` : ''}</div></div><div class="row"><span class="pp">月 ${esc(price(id))}</span>${on ? '' : `<button class="btn primary" type="button" data-pt="buy" data-id="${id}">はじめる</button>`}</div></div>`; }).join('')}</div>`;
      h += `<p class="ptnote">無料トライアルはないよ。プランの変更・解約は、端末の「設定」→ Apple ID → サブスクリプション。解約しても、届いたPは期限（30日）まで使えるよ。</p>`;
      h += prodErr ? `<p class="ptnote">⚠️ ${esc(prodErr)}</p>` : '';
    } else if (ui.show === 'hist') {
      const ev = W.events.slice().sort((x, y) => Date.parse(y.last || y.at) - Date.parse(x.last || x.at)).slice(0, 60);
      const lab = e => e.kind === 'purchase' ? `${(P.PRODUCTS[e.product] || {}).name || 'パック'}を買った` : e.kind === 'sub' ? `${(P.PRODUCTS[e.product] || {}).name || 'サブスク'}（${dayOf(e.expires)}まで）` : e.kind === 'gift' ? '初回プレゼント' : e.kind === 'mission' ? `ミッション：${e.what || ''}` : e.kind === 'unlock' ? `解放：${unlockName(e.what)}` : e.kind === 'refund' ? '返金' : (Array.isArray(e.what) ? e.what.slice(0, 3).join('・') + (e.what.length > 3 ? ` ほか${e.what.length - 3 + (e.more || 0)}件` : '') : e.what || '使った');
      h += `<ul class="pthist">${ev.map(e => `<li><span>${esc(dayOf(e.last || e.at))} ${esc(lab(e))}</span><span class="${+e.amount > 0 ? 'plus' : 'minus'}">${+e.amount > 0 ? '+' : ''}${yen(e.amount)}P</span></li>`).join('') || '<li><span class="muted">まだ何もないよ</span></li>'}</ul>`;
      h += `<p class="ptnote">買ったPの残り ${yen(b.paid_pack + b.paid_sub)}P・使ったP ${yen(b.used.paid_sub + b.used.paid_pack + b.used.free)}P（うち買ったPから ${yen(b.used.paid_sub + b.used.paid_pack)}P）</p>`;
      h += `<div class="row" style="margin-top:8px"><button class="btn" type="button" data-pt="restore">購入を復元</button></div><p class="ptnote">「購入を復元」は、サブスクの状態をAppleと合わせるよ。もう足したPはもう一度足さないよ。</p>`;
    }
    h += `<div class="banner warn">⚠️ <b>アプリを消すと、ポイント・解放したもの・記録はすべて消えて、もどせません。</b>ポイントはこの端末の中だけに入っているよ（ほかの端末には同期しないよ）。</div>`;
    box.innerHTML = h;
  }
  const TYPE_NAMES = { '複勝': '複勝', '枠複': '枠複', '枠単': '枠単', '馬連': '馬連', 'ワイド': 'ワイド', '3連複': '3連複' };
  function unlockName(key) { const k = String(key || ''); if (k.startsWith('type:')) return k.slice(5); if (k.startsWith('slot:')) { const n = +k.slice(5); try { return (TL.slots.names() || {})[n] || `マザーデータ${n}`; } catch (e) { return `マザーデータ${n}`; } } return k; }
  function paintCustom() {
    const box = $('#setCustom .ptbody'); if (!box || !W) return;
    const t = total(), conf = paintCustom.conf || '';
    const btn = (key, cost) => { const ok = t >= cost; return conf === key ? `<button class="btn primary" type="button" data-pt="unlock2" data-key="${esc(key)}" data-cost="${cost}">${pts(cost)}を使って解放する（いま ${pts(t)}）</button><button class="btn ghost" type="button" data-pt="unlock0">やめる</button>` : `<button class="btn ${ok ? 'primary' : ''}" type="button" data-pt="unlock1" data-key="${esc(key)}" data-cost="${cost}">${ok ? '解放する' : 'Pが足りない'}</button>`; };
    let h = `<p class="hint" style="margin:0 0 6px"><b>Pカスタムで、自分だけのテンゲルを育てよう！</b></p><p class="hint" style="margin:0">ポイントで、使える券種とマザーデータの枠を増やせるよ。解放したものはずっと使えるよ（アプリを消すと消えるよ）。</p>`;
    h += `<h3 style="margin:12px 0 6px">券種（記録・買い目の予約で選べるもの）</h3><p class="ptnote" style="margin:0">はじめから：単勝・馬単・3連単</p><div class="ptlist">`;
    P.UNLOCK_TYPES.forEach(tp => { const key = 'type:' + tp, on = unlocked(key); h += `<div class="ptitem${on ? ' on' : ''}"><div><div class="pn">${esc(TYPE_NAMES[tp] || tp)}</div><div class="pd">${on ? '解放ずみ' : `1つ ${pts(P.COST.type)}`}</div></div><div class="row">${on ? '<span class="chip">使えるよ</span>' : btn(key, P.COST.type)}</div></div>`; });
    h += `</div><h3 style="margin:14px 0 6px">マザーデータの枠（自分のデータで参考的中率を出す）</h3><p class="ptnote" style="margin:0">1つ目はアプリに入っているデータ。2つ目・3つ目を解放すると、Excelや判定したレースで自分だけのマザーデータを作れるよ。</p><div class="ptlist">`;
    let names = {}; try { names = TL.slots.names() || {}; } catch (e) { /* なし */ }
    [2, 3].forEach(n => { const key = 'slot:' + n, on = slotUnlocked(n); h += `<div class="ptitem${on ? ' on' : ''}"><div><div class="pn">${n}つ目「${esc(names[n] || 'マザーデータ' + n)}」</div><div class="pd">${on ? '解放ずみ' : `1つ ${pts(P.COST.slot)}`}</div></div><div class="row">${on ? '<span class="chip">使えるよ</span>' : btn(key, P.COST.slot)}</div></div>`; });
    h += '</div>';
    box.innerHTML = h;
  }
  function paintMission() {
    const box = $('#setMission .ptbody'); if (!box || !W) return;
    const n = countedN(), ms = P.missions(n, W.events);
    const next = ms.find(m => !m.done);
    let h = `<p class="hint" style="margin:0 0 8px">200Pを使って判定して、結果を記録したレースの数でポイントがもらえるよ（同じレースは1回。Excelなどでまとめて入れた記録は数えないよ）。いま <b>${n}レース</b>${next ? `・次は ${next.n}レースで ${pts(next.reward)}` : ''}</p>`;
    h += '<div>';
    ms.slice().reverse().forEach(m => { const w = Math.min(100, Math.round(n / m.n * 100)); h += `<div class="msrow"><div><div class="mn">${esc(m.label)}　<span class="muted" style="font-weight:400">${pts(m.reward)}</span></div><div class="md">${m.claimed ? '受け取りずみ' : m.done ? '受け取れるよ！' : `あと ${m.n - n}レース（${n}/${m.n}）`}</div><div class="bar"><i style="width:${w}%"></i></div></div><div>${m.claimable ? `<button class="btn primary" type="button" data-pt="claim" data-id="${m.id}">受け取る</button>` : m.claimed ? '<span class="chip">✓</span>' : ''}</div></div>`; });
    h += '</div>';
    box.innerHTML = h;
  }
  function paintBadge() {
    const tb = $('.tabbar [data-tab=set]'); if (!tb || !W) return;
    const on = P.missions(countedN(), W.events).some(m => m.claimable);
    let d = tb.querySelector('.tbdg'); if (on && !d) { d = document.createElement('span'); d.className = 'tbdg'; d.setAttribute('aria-label', '受け取れるミッションがあるよ'); tb.appendChild(d); } else if (!on && d) d.remove();
  }
  function paintHint() {
    const el = $('#ocrHint'); if (!el || !W) return;
    if (!paintHint.base) paintHint.base = el.textContent;
    el.textContent = `${paintHint.base}・1レース 200P（いま ${pts(total())}）`;
  }
  function paintAll() { paintPoints(); paintCustom(); paintMission(); paintBadge(); paintHint(); }
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
    }
  }
  // 設定タブの中の場所へ（ほかの画面の「ポイントを買う」ボタンなど）
  function goSettings(sec) {
    const tb = $('.tabbar [data-tab=set]');
    if (tb && getComputedStyle(tb.parentNode).display !== 'none') tb.click(); else { const t2 = $('.tabs-top [data-tab=set]'); if (t2) t2.click(); }
    const id = { points: 'setPoints', custom: 'setCustom', mission: 'setMission' }[sec] || 'setPoints';
    if (sec === 'points') { paintPoints.ui = { show: 'buy' }; paintPoints(); loadProducts(false).then(paintPoints); }
    setTimeout(() => { const s = document.getElementById(id); if (s) s.scrollIntoView({ block: 'start' }); }, 60);
  }
  document.addEventListener('click', e => { const b = e.target.closest && e.target.closest('[data-gopt]'); if (b) { e.preventDefault(); goSettings(b.dataset.gopt); } });

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

  // ---------- 起動 ----------
  let resolveReady; const walletReady = new Promise(r => { resolveReady = r; });
  async function boot() {
    gateOpen();
    cards();
    try {
      await TL.ready;
      const doc = await TL.getMeta('wallet').catch(() => null);
      W = normalize(doc);
      if (!doc) await save();
    } catch (e) { W = normalize(null); }
    resolveReady();
    paintAll();
    try { await giftCheck(); } catch (e) { /* つぎに開いたとき */ }
    pullTransactions().catch(() => {});
    refreshSubStatus().catch(() => {});
  }
  window.TengelWallet = {
    on: true, ready: walletReady, COST: P.COST,
    balance: () => B(), total, events: () => (W ? W.events.slice() : []), countedN,
    readCharge, countRace, unlocked, typeLocked, slotUnlocked, unlock, claim, goSettings, lockZoom, gateOpen, gateClose,
    // 自動バックアップ（アプリの中）に入れる・戻す。書き出すバックアップ（共有シート）には入れない
    snapshot: () => (W ? JSON.parse(JSON.stringify(W)) : null),
    restore: async snap => { await walletReady; if (!snap || !Array.isArray(snap.events)) return false; const cur = W.events.length; W = normalize(snap); await save(); await giftCheck().catch(() => {}); return W.events.length !== cur; },
    // まだ何も使っていない（初回プレゼントだけ・読み込みも記録もなし）なら「空」＝自動バックアップの台帳を戻してよい
    isEmpty: () => !W || (!W.events.some(e => e.id !== 'gift-first') && !W.paid.length && !Object.keys(W.counted).length)
  };
  document.addEventListener('tengel:slots', () => { if (W) { paintCustom(); } });
  document.addEventListener('tengel:tab', e => { if (e.detail === 'set' && W) { paintAll(); aboutGate(); } });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
  setTimeout(aboutGate, 50);
})();
