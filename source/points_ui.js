// ===== ポイント・Pカスタム（解放）・ミッション・アプリを開いた時の画面・拡大（App Store版だけ）=====
// 台帳の計算は points.js（TengelPoints）。ここは保存（アプリの中＝IndexedDB の meta 'wallet'・自動バックアップにも入る）と画面。
//  ・アプリを消すと台帳も消える（5章）。キーチェーンには「しるし」だけ：初回プレゼント（gift-first）・サブスクのPを足した取引（granted-sub）
//  ・App内課金（StoreKit 2）はアプリ（Store.swift）。台帳に書けたら finish をお願いする
//  ・読み込み（画像の読み取り）1レース 200P。同じレースの読み直しは 0P（11.4）。5連の予想（5レースまとめて）200P
//  ・第4.91版：結果ボードカスタム（買い切り 2,200円・非消耗型）。買ったら 台帳に tx-<取引> の unlock（what＝board）。買った あとに 読み込んだ レースの 数（board.reads）で
//    15こを 順に 解放（points.js の BOARD：第4.113版で 16こ・6レースごと → 第4.120版で 15こ。第4.121版：1〜14 は まさちゃんの 絵の ボード・15 は「ボードを持つ馬」）。
//    第4.113版：的中の とき（board.selHit）・ハズレの とき（board.selMiss）で べつべつに 1つずつ 使う（前の 1つの board.sel は 両方へ うつす）。
//    連続的中の 数（board.streak：結果を 決めた レースごと・同じ レースは 1回）は 数えて おく（第4.113版：出世馬は 消した ので いまは どの 飾りも 使わない）
//    第4.121版：まさちゃんの 絵の ボード（1〜14）は 連続的中の 数（streak）と 続けて ハズレた 数（board.mstreak：ハズレで +1・的中で 0）で 絵が かわる
//  ・第4.92版：壁紙パック（買い切り 1,500円・非消耗型）。買ったら 台帳に tx-<取引> の unlock（what＝wallpack）。買った あとに 読み込んだ レースの 数（pack.reads）で
//    新しい 壁紙 10枚（第4.147版で 七夕を 外した：11 → 10枚）を 5レースごとに 1枚ずつ 解放（points.js の WALLPACK・並びは kisekae.js）。帯の 壁紙の ミッションの 枚数に 数える
//  ・第4.114版（まさちゃん 2026/11/01）：結果ボードカスタム 1,500円・お得パック（jp.tengel.app.bundle1・2,200円＝壁紙パックと 結果ボードカスタムの セット。持って いれば 両方を 持って いる 扱い）。
//    ミッションを 2つ 足した：結果ボードカスタムの 解放の 数（3・6・9・12・16こ → 第4.120版で 15こ）と 壁紙の 解放の 枚数（3〜45枚・帯も 数える）で ポイント（もらったP）
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
  // meta 'wallet' = { id, v, device, events[], paid[]（200Pを使ったレース）, counted{ 日付|開催場|R: 日時 }（ミッションに数えたレース）, gift（初回プレゼントのしるしの状態）,
  //                   board{ reads（買った あとに 読み込んだ レース）, selHit（的中の ときに 使う もの）・selMiss（ハズレの ときに 使う もの）（'none'＝なし・''＝まだ 選んで いない）,
  //                          streak（連続的中）, mstreak（続けて ハズレた 数：第4.121版）, res[]（連続に 数えた レース） },
  //                   pack{ reads（壁紙パックを 買った あとに 読み込んだ レース） },
  //                   figs{ items[]（思い出フィギュア：第4.134版）, slots[56]（ブースの 置き場所：id か null） },
  //                   hold[]（あずかりポイント：上限を こえて 届いた ぶん。points.js の holdSplit・holdRelease：第4.139版）,
  //                   ord（1＝できごとに 書いた 順の 番号 n を ふって ある：points.js の「台帳の ならび」：第4.139版） }
  //   paid の 1件＝{ pid, at, date, venue, r, rname, start, dist, last, ck（ミッションに 数えた レース：1回の 読み込みで 数える のは 1レースだけ：第4.139版）,
  //                  fp（読んだ 単勝の 表 '馬番:単勝,…'：読み直しが 同じ レースかを 中身で 見る）, nk（1＝別の レースと して 読んだ：レースが まだ わからない）：第4.140版 }
  let W = null, saving = Promise.resolve();
  const newId = () => Math.random().toString(36).slice(2, 10);
  const blank = () => ({ id: 'wallet', v: 1, device: newId(), events: [], paid: [], counted: {}, gift: null, at: '', board: { reads: 0, selHit: '', selMiss: '', streak: 0, mstreak: 0, res: [] }, pack: { reads: 0 }, hold: [] });
  // 思い出フィギュア（第4.134版・fig/fig_app.js）：作った フィギュア（ボードの 文は 作った ときの まま）と ブースの 置き場所（7ブース × 8 ＝ 56）
  const FIG_SLOTS = 56;
  function figNorm(f) {
    const o = f && typeof f === 'object' ? f : {};
    const items = (Array.isArray(o.items) ? o.items : []).filter(x => x && typeof x.id === 'string' && x.id && +x.n >= 1 && +x.n <= 8);
    const ids = new Set(items.map(x => x.id)), seen = new Set();
    const slots = Array.from({ length: FIG_SLOTS }, (_, i) => { const v = Array.isArray(o.slots) ? o.slots[i] : null; if (typeof v === 'string' && ids.has(v) && !seen.has(v)) { seen.add(v); return v; } return null; });
    return { items, slots };
  }
  function normalize(w) {
    const o = Object.assign(blank(), w && typeof w === 'object' ? w : {});
    o.id = 'wallet'; o.events = Array.isArray(o.events) ? o.events.filter(Boolean) : []; o.paid = Array.isArray(o.paid) ? o.paid : []; o.counted = o.counted && typeof o.counted === 'object' ? o.counted : {};
    o.board = Object.assign({ reads: 0, streak: 0, mstreak: 0, res: [] }, o.board && typeof o.board === 'object' ? o.board : {});
    // 第4.113版：的中・ハズレで べつべつに 選ぶ（selHit・selMiss）。前の 版の 1つの 選択（sel）は 的中にも ハズレにも ついて いた ので 両方へ・消した 飾りは ''（points.js の boardSel）
    const bs = P.boardSel(o.board); o.board.selHit = bs.hit; o.board.selMiss = bs.miss; delete o.board.sel;
    if (!Array.isArray(o.board.res)) o.board.res = [];
    o.board.reads = Math.max(0, Math.floor(+o.board.reads || 0)); o.board.streak = Math.max(0, Math.floor(+o.board.streak || 0));
    o.board.mstreak = Math.max(0, Math.floor(+o.board.mstreak || 0));
    o.pack = Object.assign({ reads: 0 }, o.pack && typeof o.pack === 'object' ? o.pack : {});
    o.pack.reads = Math.max(0, Math.floor(+o.pack.reads || 0));
    o.figs = figNorm(o.figs);
    o.hold = P.holdNorm(o.hold);
    // 第4.139版（抜け穴を ふさぐ）：できごとに 書いた 順の 番号（n）。前の 版の 台帳（ord が ない）は 前と 同じ 時刻の 順に ふる（残高は かわらない）。そのあとは 足した 順
    if (o.ord === 1) P.stamp(o.events); else P.stampAll(o.events);
    o.ord = 1;
    // 第4.139版：前の 版で 数えた レース（counted）に、その 読み込み（paid）の しるし ck を つける（1回の 読み込みで 数える のは 1レースだけ）
    Object.keys(o.counted).forEach(k => { if (o.paid.some(e => e && e.ck === k)) return; const pe = o.paid.find(e => e && !e.w5 && !e.ck && P.raceKey(e) === k); if (pe) pe.ck = k; });
    if (!o.device) o.device = newId();
    return o;
  }
  function save() {
    P.stamp(W.events);      // 第4.139版：足した できごとに 書いた 順の 番号（await より 前に ふる）
    W.at = new Date().toISOString();
    const snap = JSON.parse(JSON.stringify(W));
    saving = saving.then(() => TL.putMeta(snap)).catch(() => { /* 次の保存で書く */ });
    emit(); paintAll();
    return saving;
  }
  const B = () => P.balance(W ? W.events : [], Date.now());
  const total = () => B().total;
  const device = () => (W && W.device) || 'x';
  // ---------- あずかりポイント（第4.139版・まさちゃん 11/10 12:27「99999pに到達しながらサブスクに入っている人は、ミッションのところで超えてしまっているポイントが溜まっていくようにして！
  //   で、使って減った分は、溜まってるポイントから補充できるようによろしく！」）----------
  //   上限（99,999P）を こえて 届いた ぶん（サブスクの 更新・あとから 届いた 取引・トレーニングセンターの 当たり）は 台帳に 入れずに W.hold に あずかる。
  //   ・ミッションの 窓（と 設定の ミッション）の いちばん 上に「あずかりポイント」。使って あきが できたら「補充する」（上の「ミッション」の 数にも 1つ 足す）
  //   ・あずかって いる あいだは 期限は 進まない（サブスクの ぶんは 補充した 日から 30日）
  //   ・足りなくて 使えない とき（読み込み・解放・フィギュア）は、あずかりから 先に 補充してから 使う（ensure）。「使えるか」は avail＝財布＋あずかり（上限まで）で 見る
  const holdSum = () => P.holdSum(W ? W.hold : []);
  const holdN = () => holdSum().total;
  const avail = () => Math.min(P.CAP, total() + holdN());
  const holdCan = () => (W ? Math.min(holdN(), P.room(total())) : 0);          // いま 補充できる P
  function release() {                                                         // 台帳へ（保存は よぶ 側）。返り値＝入れた P
    if (!W || !W.hold.length) return 0;
    const r = P.holdRelease(W.events, W.hold, Date.now());
    if (!r.moved) return 0;
    W.events = r.events; W.hold = r.hold; return r.moved;
  }
  async function refill() {
    await walletReady;
    if (!holdN()) { toast('あずかりポイントは ないよ', 2600); return 0; }
    const n = release();
    if (!n) { toast(`いまは いっぱい（上限 ${pts(P.CAP)}）だよ。ポイントを 使うと 補充できるよ`, 3600); return 0; }
    await save();
    toast(`✅ あずかりポイントから ${pts(n)} を 補充したよ（合計 ${pts(total())}${holdN() ? `・あずかり のこり ${pts(holdN())}` : ''}）`, 4200);
    unlockFx($('#msOv') ? '#msOv .msrow[data-mid="hold"]' : '#setMission .msrow[data-mid="hold"]', `+${pts(n)}`);
    return n;
  }
  // 使う 前：財布だけでは 足りないが あずかりを 足せば 足りる → 先に 補充（保存は 使う 側が する）
  function ensure(amount) { if (W && total() < amount && holdN() > 0 && avail() >= amount) { const n = release(); if (n) toast(`あずかりポイントから ${pts(n)} を 補充したよ`, 2600); } }
  // 届いた できごと（サブスク・パック・当たり）を 台帳へ。上限を こえる ぶんは あずかる。返り値＝{ added（台帳に 入れた P）, held（あずけた P）}
  function credit(e) {
    const sp = P.holdSplit(e, P.room(total()));
    W.events.push(sp.event); if (sp.hold) W.hold.push(sp.hold);
    return { added: +sp.event.amount || 0, held: sp.hold ? sp.hold.points : 0 };
  }
  const heldNote = n => (n ? `（上限 ${pts(P.CAP)} なので、うち ${pts(n)} は あずかったよ。ミッションの 窓で 補充できるよ）` : '');

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
    const Pd = P.PRODUCTS[tx.product] || {}, isUnlock = Pd.kind === 'unlock', what = Pd.what || '';
    if (tx.revoked) {
      const rf = P.refundEvent(W.events, tx, Date.now());
      const hn = W.hold.length; W.hold = P.holdDrop(W.hold, tx.id);      // 第4.139版：その 取引の あずかりポイントも 消す
      if (rf) { W.events.push(rf); added = rf.amount; await save(); toast(isUnlock ? `返金があったので、${Pd.name}を使えなくしたよ` : `返金があったので ${pts(-rf.amount)} を引いたよ`, 4000); if (isUnlock) unlockEmit(what, 'refund'); }
      else if (W.hold.length !== hn) await save();
    } else if (!P.has(W.events, 'tx-' + tx.id)) {
      const done = tx.kind === 'sub' ? await grantedSubs() : [];
      if (tx.kind === 'sub' && done.includes(String(tx.id))) { /* 入れ直し・ほかの端末で、もうこの取引のPは足してある */ }
      else {
        const had = isUnlock && P.owned(W.events, what);
        const e = P.txEvent(W.events, tx, Date.now());
        if (e) {
          const c = credit(e); added = c.added; takeTx.held = c.held; await save();      // 第4.139版：上限を こえる ぶんは あずかる（credit）
          if (tx.kind === 'sub') await rememberSub(tx.id);
          if (e.kind === 'unlock') { if (!had) { unlockEmit(what, 'owned', { src }); if (src !== 'buy') toast((src === 'update' ? `✨ ${Pd.name}が届いたよ` : `✅ ${Pd.name}を もどしたよ`) + (unlockReads(what) ? '' : '（解放は これから 読み込む レースの 数で）'), 4600); } }
          else if (src !== 'buy') toast(`✨ ${P.PRODUCTS[tx.product] ? P.PRODUCTS[tx.product].name : ''}の ${pts(e.amount)} が届いたよ${heldNote(c.held)}`, c.held ? 6000 : 4000);
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
  // 買い切り（結果ボードカスタム）は いま 有効な もの（Apple の currentEntitlements）にも ある：入れ直し・ほかの 端末でも アプリを 開くと もどる
  async function pullEntitlements() {
    const r = await iap('current');
    if (r && r.ok && Array.isArray(r.list)) for (const tx of r.list) if (tx && tx.kind === 'unlock') await takeTx(tx, 'boot');
  }
  document.addEventListener('tengel:native', e => { const d = e.detail || {}; if (d.name === 'iap' && d.payload && W) takeTx(d.payload, 'update'); });
  // 上限（P.CAP＝99,999P）：この 商品の ポイントを 足すと こえるか（買い切りの 拡張パックは ポイントが ない ので いつでも 買える）
  const overCap = n => n > 0 && total() + n > P.CAP;
  const capMsg = (what, n) => `ポイントは ${pts(P.CAP)} まで。${what}（${pts(n)}）を 足すと こえるよ。ポイントを 使ってからに してね（いま ${pts(total())}）`;
  async function buy(id, btn) {
    const Pd = P.PRODUCTS[id]; if (!Pd) return;
    if (overCap(Pd.points)) { toast(capMsg(Pd.name, Pd.points), 5200); return; }      // 第4.139版：買う 前に 止める（払った ポイントが 入らない ことが ない ように）
    const label = btn ? btn.textContent : '';
    if (btn) { btn.disabled = true; btn.textContent = 'App Store…'; }
    const r = await iap('buy', { id });
    if (btn) { btn.disabled = false; btn.textContent = label || (Pd.kind === 'sub' ? 'はじめる' : '買う'); }
    if (r && r.ok && r.tx) {
      takeTx.held = 0;
      const added = await takeTx(r.tx, 'buy'), held = takeTx.held || 0;
      if (Pd.kind === 'unlock') toast(P.owned(W.events, Pd.what) ? (Pd.what === 'wallpack' ? `🎉 ${Pd.name}を買ったよ！ これから 読み込む レース 5つごとに 新しい 壁紙が 1枚ずつ 解放されるよ`
        : Pd.what === 'bundle' ? `🎉 ${Pd.name}を買ったよ！ 壁紙パックと 結果ボードカスタムが 使えるよ。これから 読み込む レースの 数で 1つずつ 解放されるよ`
        : `🎉 ${Pd.name}を買ったよ！ これから 読み込む レース ${P.BOARD.steps[0][1]}つで 1つめが 解放されるよ`) : '✅ 買えたよ', 4800);
      else toast(added || held ? `✅ ${pts(added + held)} が届いたよ（合計 ${pts(total())}）${heldNote(held)}` : '✅ 買えたよ（このPはもう入っているよ）', held ? 6000 : 4000);
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
    let added = 0, held = 0;      // held＝上限を こえて あずけた ぶん（第4.139版）
    const had = { board: P.boardOwned(W.events), wallpack: P.packOwned(W.events) };
    const take = async tx => { takeTx.held = 0; added += await takeTx(tx, 'restore'); held += takeTx.held || 0; };
    for (const tx of (r.unfinished || [])) await take(tx);
    for (const tx of (r.current || [])) if (tx.kind === 'sub' || tx.kind === 'unlock') await take(tx);
    await refreshSubStatus();
    const got = [['board', '結果ボードカスタム'], ['wallpack', '壁紙パック']].filter(x => !had[x[0]] && P.owned(W.events, x[0]));
    const gotTxt = got.map(x => x[1]).join('・');
    toast(added || held ? `✅ ${pts(added + held)} を足したよ${heldNote(held)}${got.length ? '・' + gotTxt + 'を もどしたよ' : ''}` : got.length ? `✅ ${gotTxt}を もどしたよ` + (got.some(x => unlockReads(x[0])) ? '' : '（解放は これから 読み込む レースの 数で）') : '✅ Appleと合わせたよ（足すものはなかったよ）', 4600);
  }
  async function refreshSubStatus() { const r = await iap('status'); subStatus = r && r.ok ? r : null; paintPoints(); }

  // ---------- 使う：読み込み（200P）・読み直し 0P ----------
  const READ_WHAT = r => `読み込み ${r.date ? dayOf(r.date) : ''}${r.venue ? ' ' + r.venue : ''}${r.r ? ' ' + r.r + 'R' : ''}`.trim();
  function charge(amount, what) {
    ensure(amount);
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
    // 第4.140版（まさちゃん 11/10 14:22「きびしくする（人気の並びが前とぜんぜん違ったら200P。同じレースの読み直しは0Pのまま）これで！」）：
    //   読み直し（0P）は、読んだ 単勝の 表（o.rows）が 前に 読んだ 表（paid の fp）と「ぜんぜん ちがう」（P.fpDiff）と 別の レース＝200P。
    //   前は 画像に 日付・R が 写って いないと 入力の 日付・R で 同じ レースと 見て いた ので、切り取った 画像なら 別の レースも 0P で 読めた。
    //   ・くらべられない とき（どちらかに 単勝の 表が ない・頭数が 少ない）は 前と 同じ（入力の 日付・R で 見る）
    //   ・別の レースと して 読んだ 読み込みには nk（レースが まだ わからない）。日付・R で さがす ときは 出さない（その 入力の 読み込みの しるし pid で だけ 見つかる）。
    //     入力の 日付・R を 直して 同じ 画像を 読み直す か、記録を 保存する（countRace）と、その レースの 読み込みに なる
    const fp = P.raceFp(o.rows);
    const judged = e => !!(e.fp && fp), bodyDiff = e => judged(e) && P.fpDiff(e.fp, fp);
    const free = async (e, how) => { stamp(e); if (fp) e.fp = fp; await save(); return { ok: true, charged: false, free: how, pid: e.pid }; };
    let diff = false;
    if (form.pid) {
      const cur = W.paid.find(e => e.pid === form.pid);
      if (cur && !cur.w5) {
        const keyOK = !race.r || P.sameRace(cur, race) || !cur.r;
        if (keyOK && !bodyDiff(cur)) return free(cur, 'session');
        // 入力の 日付・R を 直して、同じ 表を 読み直した（画像に R は 写って いない・オッズの 数が ほぼ 同じ＝同じ 画像）→ 同じ 読み込み。その 読み込みの レースを 入力に 合わせる。
        //   「ほぼ 同じ」は きびしく 見る（8割 以上 同じ 数）：人気の 順が にて いる だけ では 合わせない（次の レースを たまたま 0P に しない）
        if (!keyOK && !(+d.r) && judged(cur) && P.fpShare(cur.fp, fp) >= 0.8 && race.date && race.r) {
          Object.assign(cur, { date: race.date, venue: race.venue || cur.venue || '', r: race.r, rname: race.rname || '', start: race.start || '', dist: race.dist || cur.dist || 0 }); delete cur.nk;
          return free(cur, 'session');
        }
        if (keyOK) diff = true;
      }
    }
    const sameKey = W.paid.filter(e => e && !e.w5 && !e.nk && e.pid !== form.pid && P.sameRace(e, race)).reverse();      // 新しい 順
    const hit = sameKey.find(e => !bodyDiff(e));
    if (hit) return free(hit, 'same');
    if (sameKey.length) diff = true;
    if (!charge(P.COST.read, READ_WHAT(race))) return { ok: false, need: P.COST.read, have: total() };
    const e = { pid: newId(), at: new Date().toISOString() }; stamp(e); if (fp) e.fp = fp; if (diff) e.nk = 1; W.paid.push(e); keepPaid();
    const bu = boardRead(), pk = packRead();
    await save();
    if (bu) boardEmit('unlock', { item: bu.id, no: bu.no });
    if (pk) packEmit('unlock', { no: pk });
    return { ok: true, charged: true, free: null, pid: e.pid, diff };      // diff＝同じ 日付・R の 読み込みは あったが、中身が ぜんぜん ちがった（別の レースと して 200P）
  }

  // ---------- 結果ボードカスタム（第4.91版）----------
  function boardEmit(phase, d) { try { document.dispatchEvent(new CustomEvent('tengel:board', { detail: Object.assign({ phase }, d || {}) })); } catch (e) { /* なし */ } }
  // 買い切り（結果ボードカスタム・壁紙パック）の お知らせ・買った あとに 読み込んだ 数
  function unlockEmit(what, phase, d) { if (what === 'bundle') { packEmit(phase, d); boardEmit(phase, d); return; } if (what === 'wallpack') packEmit(phase, d); else boardEmit(phase, d); }
  function unlockReads(what) { return what === 'wallpack' ? (W.pack.reads || 0) : what === 'bundle' ? Math.max(W.pack.reads || 0, W.board.reads || 0) : (W.board.reads || 0); }

  // ---------- 壁紙パック（第4.92版）----------
  // tengel:wallpack：phase＝owned（買った・もどした）・unlock（no 枚目を 解放）・refund（返金）。kisekae.js が 選ぶ画面と お知らせを 出す
  function packEmit(phase, d) { try { document.dispatchEvent(new CustomEvent('tengel:wallpack', { detail: Object.assign({ phase }, d || {}) })); } catch (e) { /* なし */ } }
  // 買った あとの 読み込み（200P を 使った 1レース）を 数える。新しく 解放した 枚目（1〜11）を 返す（なければ 0）
  function packRead() {
    if (!W || !P.packOwned(W.events)) return 0;
    const before = P.packUnlocked(W.pack.reads);
    W.pack.reads = (+W.pack.reads || 0) + 1;
    const after = P.packUnlocked(W.pack.reads);
    return after > before ? after : 0;
  }
  function packInfo() {
    const owned = !!W && P.packOwned(W.events), reads = owned ? (W.pack.reads || 0) : 0;
    return { owned, reads, n: owned ? P.packUnlocked(reads) : 0, next: owned ? P.packNext(reads) : null, every: P.WALLPACK.every, total: P.WALLPACK.n };
  }
  const packN = () => packInfo().n;
  // 第4.113版：的中の とき（selHit）・ハズレの とき（selMiss）の 2つ。'none'＝なし・''＝まだ 選んで いない（つぎに 解放した 飾りを そのまま 使う）
  const BSLOT = { hit: 'selHit', miss: 'selMiss' };
  // n0 → n1 こ 解放した：その 間の 飾り（じゅんび中は のぞく）を、まだ 選んで いない 所に つける（points.js の boardOpen）。解放した 飾りを 返す
  function boardOpened(n0, n1) {
    const bd = W.board, sel = { hit: bd.selHit, miss: bd.selMiss }, got = P.boardOpen(sel, n0, n1);
    bd.selHit = sel.hit; bd.selMiss = sel.miss;
    return got;
  }
  // 買った あとの 読み込み（200P を 使った 1レース）を 数える。新しく 解放した 飾りを 返す（じゅんび中の 番号だけ なら null）
  function boardRead() {
    if (!W || !P.boardOwned(W.events)) return null;
    const bd = W.board, before = P.boardUnlocked(bd.reads);
    bd.reads = (+bd.reads || 0) + 1;
    const got = boardOpened(before, P.boardUnlocked(bd.reads));
    return got.length ? got[got.length - 1] : null;
  }
  function boardInfo() {
    const owned = !!W && P.boardOwned(W.events), bd = (W && W.board) || { reads: 0, selHit: '', selMiss: '', streak: 0, mstreak: 0 };
    const n = owned ? P.boardUnlocked(bd.reads) : 0, pick = id => (P.boardKnown(id) ? id : '');
    return { owned, reads: owned ? bd.reads : 0, n, next: owned ? P.boardNext(bd.reads) : null, nextReady: owned ? P.boardNextReady(bd.reads) : null,
      selHit: pick(bd.selHit), selMiss: pick(bd.selMiss), streak: bd.streak || 0, mstreak: bd.mstreak || 0, items: P.BOARD_ITEMS, need: P.BOARD_NEED };
  }
  // いま ボードに つける もの（kind＝結果の 種類：'miss'＝ハズレの 所・ほか＝的中の 所。買って いて・解放ずみで・選んで いて・その 結果に 使える もの）。なし なら ''
  function boardActive(kind) {
    const i = boardInfo();
    return i.owned ? P.boardActive({ hit: i.selHit, miss: i.selMiss }, i.reads, kind) : '';
  }
  // 選ぶ（kind：'hit'＝的中の とき・'miss'＝ハズレの とき／id：'none'＝なし）
  async function boardSelect(id, kind) {
    await walletReady;
    const i = boardInfo(), k = P.boardSlot(kind);
    if (id !== 'none') { const it = P.BOARD_ITEMS.find(x => x.id === id); if (!it || !i.owned || it.no > i.n || !P.boardFits(it, k)) return false; }
    W.board[BSLOT[k]] = id; await save(); boardEmit('select', { item: id, kind: k });
    return true;
  }
  // 連続的中：結果を 決めた レース（同じ レースは 1回）。どれか 1つの 券種が 的中なら +1・全部 ハズレなら 0。
  //   第4.121版：続けて ハズレた 数（mstreak）も 数える（ハズレで +1・的中で 0）。返り値：的中なら 連続的中の 数・ハズレなら 続けて ハズレた 数
  //   （src.html が 演出の spec.streak に 渡す → bcx.js が 絵の ボードの 段を 決める：的中①〜⑨＝連続的中・ハズレ①〜⑤＝続けて ハズレた 数）
  async function boardResult(id, hit) {
    await walletReady;
    const bd = W.board, key = String(id || '');
    if (key && bd.res.includes(key)) return hit ? bd.streak : bd.mstreak;
    bd.streak = hit ? (+bd.streak || 0) + 1 : 0;
    bd.mstreak = hit ? 0 : (+bd.mstreak || 0) + 1;
    if (key) { bd.res.push(key); if (bd.res.length > 400) bd.res = bd.res.slice(-300); }
    await save();
    return hit ? bd.streak : bd.mstreak;
  }

  // ---------- ミッション：記録したレースを数える ----------
  async function countRace(b) {
    await walletReady;
    if (!b || b.kind === 'win5') return false;
    const key = P.raceKey(b); if (!key || W.counted[key]) return false;
    // 第4.139版（抜け穴を ふさぐ）：200P の 読み込み 1回で 数える のは 1レースだけ。
    //   前は「読み込みの しるし（pid）が ついた 記録」なら 日付・R を 手で かえても 別の レースと して 数えた（1回の 読み込みで 何レースでも 数えて ミッションの ポイントを もらえた）。
    //   → その 読み込み（paid）に 数えた レース（ck）を 書く。もう 別の レースを 数えた 読み込みは 使えない
    const cand = W.paid.filter(e => e && !e.w5 && ((b.pid && e.pid === b.pid) || (!e.nk && P.sameRace(e, b))));      // nk（別の レースと して 読んだ 読み込み）は しるし（pid）で だけ
    const pe = cand.find(e => e.ck === key) || cand.find(e => !e.ck);
    if (!pe) return false;
    pe.ck = key;
    if (pe.nk) { Object.assign(pe, { date: b.date, venue: String(b.venue || ''), r: +b.r || pe.r }); delete pe.nk; }      // 第4.140版：その 読み込みの レースは 記録に 合わせる（あとの 読み直しで 見つかる ように）
    W.counted[key] = new Date().toISOString();
    await save();
    const n = countedN(), claim = P.missions(n, W.events).filter(m => m.claimable);
    toast(claim.length ? `🏆 ${n}レース目の記録。受け取れるミッションがあるよ（上の「ミッション」で受け取れるよ）` : `ミッション：記録 ${n}レース目`, 3600);
    return true;
  }
  const countedN = () => W ? Object.keys(W.counted).length : 0;
  // 第4.114版：結果ボードカスタムの 解放の 数（買って いなければ 0）・壁紙の 枚数（帯も 数える）
  const boardMissionN = () => (W && P.boardOwned(W.events) ? P.boardUnlocked(W.board.reads) : 0);
  const wallAllN = () => (W ? P.wallCountAll(W.events, packN()) : 0);
  // 第4.130版：トレーニングセンターの お世話の 合計（tc_launch.js の TCInfo：この 端末の 中・馬が リセット されても 減らない）
  const tcTotal = () => { try { return window.TCInfo ? (window.TCInfo.total() || 0) : 0; } catch (e) { return 0; } };
  // 第4.138版：作った 思い出フィギュアの 数（台帳の figs.items：しまって あっても 数える）
  const figN = () => (W && W.figs && Array.isArray(W.figs.items) ? W.figs.items.length : 0);
  const extraMissions = () => (W ? P.boardMissions(boardMissionN(), W.events).concat(P.wallpMissions(wallAllN(), W.events)).concat(P.tcMissions ? P.tcMissions(tcTotal(), W.events) : []).concat(P.figMissions ? P.figMissions(figN(), W.events) : []) : []);
  async function claim(id) {
    if (/^mission-(board|wallp|tc|fig)-/.test(String(id))) {   // 第4.114版：結果ボードカスタムの 解放の 数・壁紙の 枚数 → ポイント（第4.130版：トレーニングセンターの お世話の 合計も・第4.138版：思い出フィギュアの 数も）
      const m = extraMissions().find(x => x.id === id);
      if (!m || !m.claimable) return;
      if (overCap(m.reward)) { toast(capMsg(m.label, m.reward).replace('使ってからに してね', '使ってから 受け取ってね（ミッションは 消えないよ）'), 5200); return; }
      W.events.push(P.rowEvent(m, Date.now()));
      await save();
      toast(`🎉 ${m.label}の ${pts(m.reward)} を受け取ったよ（合計 ${pts(total())}）`, 4000);
      unlockFx(msRowSel(id), `+${pts(m.reward)}`);
      return;
    }
    if (/^mission-wall-/.test(String(id))) {     // 壁紙のミッション（帯の壁紙・第4弾）
      const wm = P.wallMissions(P.wallCount(W.events, packN()), W.events).find(x => x.id === id);
      if (!wm || !wm.claimable) return;
      P.wallMissionEvents(wm, device(), Date.now()).forEach(e => { if (!P.has(W.events, e.id)) W.events.push(e); });
      await save(); paintAll();
      toast(`✅ ${wm.label}を受け取ったよ！ 設定の「着せ替え」で使えるよ`, 4000);
      unlockFx(msRowSel(id), '受け取り！');
      return;
    }
    const m = P.missions(countedN(), W.events).find(x => x.id === id);
    if (!m || !m.claimable) return;
    if (overCap(m.reward)) { toast(capMsg(m.label, m.reward).replace('使ってからに してね', '使ってから 受け取ってね（ミッションは 消えないよ）'), 5200); return; }
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
  // 第4.123版：テンゲルデータ（1つ目）と マザーデータ①（2つ目）は はじめから。マザーデータ②・③（3・4つ目）は Pカスタムで 解放（15,000P）
  const slotUnlocked = n => +n <= 2 || unlocked('slot:' + n) || slotHasRows(+n);
  const SLOT_LABEL = n => ['', 'テンゲルデータ', 'マザーデータ①', 'マザーデータ②', 'マザーデータ③'][+n] || `マザーデータ${n}`;
  async function unlock(key, cost) {
    await walletReady;
    // 第4.139版（念のため）：券種・マザーデータの 枠の 値段は 表（points.js の COST）から。画面に 書いて ある 数字（data-cost）は 使わない
    if (/^type:/.test(key)) cost = P.COST.type; else if (/^slot:/.test(key)) cost = P.COST.slot;
    cost = Math.max(0, Math.round(+cost || 0));
    ensure(cost);
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
    // 第4.139版（まさちゃん 11/10 11:46「ポイントの詳細は ・購入ポイント ・サブスクポイント ・獲得ポイント の3つ」「ポイントの上限は、99999までにして！」）：
    //   内わけの 名前を かえた（前は 買ったP・サブスクのP・もらったP）・上限の 行を 足した
    let h = `<div class="ptbal"><span class="ptbig">${yen(b.total)}<small>P</small></span><span class="ptsub">いま使えるポイント（3つの合計）</span></div>`;
    h += `<div class="ptbk"><div><span>購入ポイント<small>パック・期限なし</small></span><b>${pts(b.paid_pack)}</b></div>`
      + `<div><span>サブスクポイント<small>届いた日から30日</small></span><b>${pts(b.paid_sub)}</b></div>`
      + `<div><span>獲得ポイント<small>はじめてのプレゼント・ミッション</small></span><b>${pts(b.free)}</b></div></div>`;
    h += `<p class="ptnote ptcap">ポイントは 合計 <b>${pts(P.CAP)}</b> まで もてるよ（${b.total >= P.CAP ? 'いま いっぱい。使うと また 入るよ' : `あと ${pts(P.room(b.total))} 入るよ`}）</p>`;
    const hd = holdN();      // 第4.139版：あずかりポイント（上限を こえて 届いた ぶん）
    if (hd) h += `<p class="ptnote pthold">あずかりポイント：<b>${pts(hd)}</b>（上限を こえて 届いた ぶん。使って へったら、画面の上の「ミッション」で 補充できるよ）</p>`;
    if (lots.length) h += `<p class="ptnote">サブスクポイント：${lots.map(L => `${yen(L.remain)}P は ${dayOf(L.expires)}まで`).join('・')}（届いた日から30日。次の月のPが届いても、期限までは使えるよ）</p>`;
    if (b.lost) h += `<p class="ptnote">期限が切れて消えたサブスクポイント：${yen(b.lost)}P</p>`;
    if (W.gift && W.gift.state === 'already') h += '<p class="ptnote">はじめてのプレゼント（1,500P）は、前にこのアプリを入れたときに受け取りずみだよ。</p>';
    return h;
  }
  const price = id => { const p = (products || []).find(x => x.id === id); return p ? p.price : `${yen(P.PRODUCTS[id].yen)}円`; };
  // パック（買う）の 一覧
  function packsHtml() {
    let h = `<div class="ptlist">${P.PACKS.map(id => { const Pd = P.PRODUCTS[id]; return `<div class="ptitem"><div><div class="pn">${esc(Pd.name)}</div><div class="pd">${yen(Pd.points)}P（期限なし）</div></div><div class="row"><span class="pp">${esc(price(id))}</span><button class="btn primary" type="button" data-pt="buy" data-id="${id}"${overCap(Pd.points) ? ' disabled title="上限をこえるので買えないよ"' : ''}>買う</button></div></div>`; }).join('')}</div>`;
    if (P.PACKS.some(id => overCap(P.PRODUCTS[id].points))) h += `<p class="ptnote">⚠️ ポイントは 合計 ${pts(P.CAP)} まで。足すと こえる パックは 買えないよ（いま ${pts(total())}・あと ${pts(P.room(total()))}）</p>`;
    h += prodErr ? `<p class="ptnote">⚠️ ${esc(prodErr)}。値段は税込のめやす。買うときはApp Storeの表示が正しいよ</p>` : '';
    return h;
  }
  // サブスクの 一覧（加入中・次の 更新）
  function subsHtml() {
    const active = (subStatus && subStatus.active) || [];
    let h = `<div class="ptlist">${P.SUBS.map(id => { const Pd = P.PRODUCTS[id], on = active.find(x => x.product === id); return `<div class="ptitem${on ? ' on' : ''}"><div><div class="pn">${esc(Pd.name)}${on ? '　<span class="chip">加入中</span>' : ''}</div><div class="pd">毎月 ${yen(Pd.points)}P${Pd.bonus ? `（うち ${yen(Pd.bonus)}P おまけ）` : ''}・届いた日から30日 使えるよ${on && on.expires ? `・次の更新 ${dayOf(on.expires)}${on.willRenew === false ? '（更新しない）' : ''}` : ''}</div></div><div class="row"><span class="pp">月 ${esc(price(id))}</span>${on ? '' : `<button class="btn primary" type="button" data-pt="buy" data-id="${id}"${overCap(Pd.points) ? ' disabled title="上限をこえるので はじめられないよ"' : ''}>はじめる</button>`}</div></div>`; }).join('')}</div>`;
    if (P.SUBS.some(id => !active.find(x => x.product === id) && overCap(P.PRODUCTS[id].points))) h += `<p class="ptnote">⚠️ ポイントは 合計 ${pts(P.CAP)} まで。足すと こえる プランは はじめられないよ（いま ${pts(total())}・あと ${pts(P.room(total()))}）。加入中の プランの ポイントは、上限でも 届くよ</p>`;
    h += `<p class="ptnote">無料トライアルはないよ。プランの変更・解約は、端末の「設定」→ Apple ID → サブスクリプション。解約しても、届いたPは期限（30日）まで使えるよ。</p>`;
    h += prodErr ? `<p class="ptnote">⚠️ ${esc(prodErr)}</p>` : '';
    return h;
  }
  function paintPoints() {
    const box = $('#setPoints .ptbody'); if (!box || !W) return;
    const b = bal(), ui = paintPoints.ui || (paintPoints.ui = { show: '' });
    let h = balanceHtml(b);
    h += `<div class="row" style="margin-top:10px"><button class="btn primary" type="button" data-pt="show" data-v="buy" aria-pressed="${ui.show === 'buy'}">ポイントを買う</button><button class="btn" type="button" data-pt="show" data-v="sub" aria-pressed="${ui.show === 'sub'}">サブスク</button><button class="btn ghost" type="button" data-pt="show" data-v="hist" aria-pressed="${ui.show === 'hist'}">詳しく</button></div>`;
    h += `<p class="hint">1レースの読み込み（画像の読み取りから判定まで）に <b>200P</b> 使うよ。同じレースを読み直すときは 0P。買ったポイントから先に使うよ（サブスクポイント → 購入ポイント → 獲得ポイント）。</p>`;
    if (ui.show === 'buy') {
      h += packsHtml();
    } else if (ui.show === 'sub') {
      h += subsHtml();
    } else if (ui.show === 'hist') {
      const ev = W.events.slice().sort((x, y) => Date.parse(y.last || y.at) - Date.parse(x.last || x.at)).slice(0, 60);
      // 第4.139版：あずかりポイントから 補充した ぶん（from:'hold'）・届いた ときに あずけた ぶん（held）も わかる ように
      const msLab = e => (/^(rel-)?back-theme:/.test(String(e.id)) ? '' : 'ミッション：') + (e.what || '');      // 第4.147版：外した 壁紙の ポイントを 返した ぶんは「ミッション：」を つけない
      const lab0 = e => e.kind === 'purchase' ? `${(P.PRODUCTS[e.product] || {}).name || 'パック'}を買った` : e.kind === 'sub' ? `${(P.PRODUCTS[e.product] || {}).name || 'サブスク'}（${dayOf(e.expires)}まで）` : msLab(e);
      const nm0 = e => e.kind === 'mission' ? msLab(e) : (P.PRODUCTS[e.product] || {}).name || (e.kind === 'sub' ? 'サブスク' : 'パック');
      const lab = e => e.from === 'hold' ? `あずかりポイントから 補充（${lab0(e)}）` : e.held ? (+e.amount > 0 ? `${lab0(e)}（ほかに ${pts(e.held)} は あずかり）` : `${nm0(e)}（${pts(e.held)} は あずかり）`) : e.kind === 'purchase' ? `${(P.PRODUCTS[e.product] || {}).name || 'パック'}を買った` : e.kind === 'sub' ? `${(P.PRODUCTS[e.product] || {}).name || 'サブスク'}（${dayOf(e.expires)}まで）` : e.kind === 'gift' ? '初回プレゼント' : e.kind === 'mission' ? msLab(e) : e.kind === 'unlock' ? (/^fig:/.test(String(e.what || '')) ? unlockName(e.what) : `解放：${unlockName(e.what)}`) : e.kind === 'refund' ? '返金' : (Array.isArray(e.what) ? e.what.slice(0, 3).join('・') + (e.what.length > 3 ? ` ほか${e.what.length - 3 + (e.more || 0)}件` : '') : e.what || '使った');
      h += `<ul class="pthist">${ev.map(e => `<li><span>${esc(dayOf(e.last || e.at))} ${esc(lab(e))}</span><span class="${+e.amount > 0 ? 'plus' : 'minus'}">${+e.amount > 0 ? '+' : ''}${yen(e.amount)}P</span></li>`).join('') || '<li><span class="muted">まだ何もないよ</span></li>'}</ul>`;
      h += `<p class="ptnote">買ったポイント（購入＋サブスク）の残り ${yen(b.paid_pack + b.paid_sub)}P・使ったP ${yen(b.used.paid_sub + b.used.paid_pack + b.used.free)}P（うち買ったポイントから ${yen(b.used.paid_sub + b.used.paid_pack)}P）</p>`;
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
    $('#ptBal', ov).innerHTML = balanceHtml(b) + `<p class="hint" style="margin:8px 0 0">1レースの読み込み（画像の読み取りから判定まで）に <b>200P</b> 使うよ。同じレースを読み直すときは 0P。買ったポイントから先に使うよ（サブスクポイント → 購入ポイント → 獲得ポイント）。</p>`;
    $('#ptBuy', ov).innerHTML = packsHtml();
    $('#ptSub', ov).innerHTML = subsHtml();
  }
  let ptPrev = null;
  function openPoints() {
    if (!W || $('#ptOv')) return;
    const ov = document.createElement('div'); ov.id = 'ptOv'; ov.className = 'tgov'; ov.setAttribute('role', 'dialog'); ov.setAttribute('aria-modal', 'true'); ov.setAttribute('aria-label', 'ポイント');
    ov.innerHTML = `<div class="msh"><h2>${COIN}ポイント</h2><span class="msn"></span><button class="btn" type="button" data-ms="close">とじる</button></div>`
      + '<div class="msb"><div class="card setsec" id="ptDetail"><h2>ポイントの詳細</h2><div class="ptbody" id="ptBal"></div></div>'
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
    if (k.startsWith('slot:')) { const n = +k.slice(5), lab = SLOT_LABEL(n); try { const nm = (TL.slots.names() || {})[n] || lab; return nm === lab ? lab : `${lab}「${nm}」`; } catch (e) { return lab; } }
    if (k.startsWith('theme:')) { try { const t = (window.TengelKisekae.list() || []).find(x => x.id === k.slice(6)); if (t) return `壁紙「${t.name}」`; } catch (e) { /* なし */ } const gn = (P.GONE_NAMES || {})[k.slice(6)]; return gn ? `壁紙「${gn}」（なくなった壁紙）` : `壁紙 ${k.slice(6)}`; }
    if (k === 'board') return '結果ボードカスタム（買い切り）';
    if (k === 'wallpack') return '壁紙パック（買い切り）';
    if (k === 'bundle') return 'お得パック（壁紙パックと 結果ボードカスタム・買い切り）';
    if (k.startsWith('fig:')) { const it = W && W.figs ? W.figs.items.find(x => x.id === k.slice(4)) : null; return `思い出フィギュアを作った${it && it.info && it.info.race ? `（${it.info.race}）` : ''}`; }
    return k;
  }
  function paintCustom() {
    const box = $('#setCustom .ptbody'); if (!box || !W) return;
    const t = avail(), conf = paintCustom.conf || '';      // 第4.139版：あずかりポイントも 数える（足りなければ 使う ときに 補充する）
    const btn = (key, cost) => { const ok = t >= cost; return conf === key ? `<button class="btn primary" type="button" data-pt="unlock2" data-key="${esc(key)}" data-cost="${cost}">${pts(cost)}を使って解放する（いま ${pts(t)}）</button><button class="btn ghost" type="button" data-pt="unlock0">やめる</button>` : `<button class="btn ${ok ? 'primary' : ''}" type="button" data-pt="unlock1" data-key="${esc(key)}" data-cost="${cost}">${ok ? '解放する' : 'Pが足りない'}</button>`; };
    let h = `<p class="hint" style="margin:0 0 6px"><b>Pカスタムで、自分だけのテンゲルを育てよう！</b></p><p class="hint" style="margin:0">ポイントで、使える券種とマザーデータの枠を増やせるよ。解放したものはずっと使えるよ（アプリを消すと消えるよ）。</p>`;
    h += `<h3 style="margin:12px 0 6px">券種（記録・買い目の予約で選べるもの）</h3><p class="ptnote" style="margin:0">はじめから：単勝・馬単・3連単</p><div class="ptlist">`;
    P.UNLOCK_TYPES.forEach(tp => { const key = 'type:' + tp, on = unlocked(key); h += `<div class="ptitem${on ? ' on' : ''}" data-key="${esc(key)}"><div><div class="pn">${esc(TYPE_NAMES[tp] || tp)}</div><div class="pd">${on ? '解放ずみ' : `1つ ${pts(P.COST.type)}`}</div></div><div class="row">${on ? '<span class="chip">使えるよ</span>' : btn(key, P.COST.type)}</div></div>`; });
    h += `</div><h3 style="margin:14px 0 6px">マザーデータの枠（自分のデータで参考的中率を出す）</h3><p class="ptnote" style="margin:0">テンゲルデータ（アプリに入っているデータ）とマザーデータ①は、はじめから使えるよ。マザーデータ②・③を解放すると、Excelや判定したレースで自分だけのマザーデータをもっと作れるよ。</p><div class="ptlist">`;
    [3, 4].forEach(n => { const key = 'slot:' + n, on = slotUnlocked(n); h += `<div class="ptitem${on ? ' on' : ''}" data-key="${esc(key)}"><div><div class="pn">${esc(unlockName(key))}</div><div class="pd">${on ? '解放ずみ' : `1つ ${pts(P.COST.slot)}`}</div></div><div class="row">${on ? '<span class="chip">使えるよ</span>' : btn(key, P.COST.slot)}</div></div>`; });
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
    const wn = P.wallCount(W.events, packN()), wms = P.wallMissions(wn, W.events);
    let h = `<p class="hint" style="margin:0 0 4px">設定の「着せ替え」でポイントを使って解放した壁紙と、壁紙パックで解放した壁紙の枚数で、帯の壁紙がもらえるよ（いつもの・帯の壁紙は数えないよ）。いま <b>${wn}枚</b></p><div>`;
    wms.forEach(m => { const w = Math.min(100, Math.round(wn / m.n * 100)); h += `<div class="msrow${m.claimable ? ' can' : ''}" data-mid="${esc(m.id)}"><div><div class="mn">壁紙を${m.n}枚あつめる　<span class="muted" style="font-weight:400">${esc(m.label)}</span></div><div class="md">${m.claimed ? '受け取りずみ' : m.done ? '受け取れるよ！' : `あと ${m.n - wn}枚（${wn}/${m.n}）`}</div><div class="bar"><i style="width:${w}%"></i></div></div><div>${m.claimable ? `<button class="btn primary" type="button" data-pt="claim" data-id="${m.id}">受け取る</button>` : m.claimed ? '<span class="chip">✓</span>' : ''}</div></div>`; });
    return h + '</div>';
  }
  // 第4.114版：ふつうの 行（受け取れる／受け取りずみ／あと いくつ）。unit＝「こ」「枚」
  function rowHtml(m, n, unit) {
    const w = Math.min(100, Math.round(n / m.n * 100));
    const md = m.claimed ? '受け取りずみ' : m.done ? '受け取れるよ！' : m.reach === false ? `いまは ${P.WALL_TOTAL}枚まで（壁紙が ふえたら 届くよ）` : `あと ${m.n - n}${unit}（${n}/${m.n}）`;
    return `<div class="msrow${m.claimable ? ' can' : ''}" data-mid="${esc(m.id)}"><div><div class="mn">${esc(m.label)}　<span class="muted" style="font-weight:400">${pts(m.reward)}</span></div><div class="md">${md}</div><div class="bar"><i style="width:${w}%"></i></div></div>`
      + `<div>${m.claimable ? `<button class="btn primary" type="button" data-pt="claim" data-id="${m.id}">受け取る</button>` : m.claimed ? '<span class="chip">✓</span>' : ''}</div></div>`;
  }
  // 結果ボードカスタムの ミッション（第4.114版・第4.120版で さいごを 15こに）：解放した 番号の 数（3・6・9・12・15こ）→ ポイント
  function boardRowsHtml() {
    const n = boardMissionN(), owned = !!W && P.boardOwned(W.events), ms = P.boardMissions(n, W ? W.events : []);
    let h = `<p class="hint" style="margin:0 0 4px">設定の「結果ボードカスタム」で 解放した 数（買った あとに 読み込んだ レースの 数で 番号の 順に 解放）で ポイントが もらえるよ。いま <b>${n}こ</b>${owned ? '' : '（結果ボードカスタムを 買うと すすむよ）'}</p><div>`;
    ms.forEach(m => { h += rowHtml(m, n, 'こ'); });
    return h + '</div>';
  }
  // 壁紙の 枚数の ミッション（第4.114版）：ポイント・壁紙パック・帯で 解放した 枚数（3〜45枚）→ ポイント
  function wallpRowsHtml() {
    const n = wallAllN(), ms = P.wallpMissions(n, W ? W.events : []);
    let h = `<p class="hint" style="margin:10px 0 4px">解放した 壁紙の 枚数（ポイント・壁紙パック・帯の 3枚。いつもの は 数えないよ）で ポイントも もらえるよ。いま <b>${n}枚</b>（いま 解放できるのは ${P.WALL_TOTAL}枚まで）</p><div>`;
    ms.forEach(m => { h += rowHtml(m, n, '枚'); });
    return h + '</div>';
  }
  // トレーニングセンターの ミッション（第4.130版）：お世話（ごはん・おそうじ）の 合計 50・100・150・200回 → ポイント
  function tcRowsHtml() {
    const n = tcTotal(), ms = W && P.tcMissions ? P.tcMissions(n, W.events) : [];
    let h = `<p class="hint" style="margin:0 0 4px">トレーニングセンターで お世話（ごはん・おそうじ）した 合計の 回数で ポイントが もらえるよ。馬の 色が かわって リセット されても 合計は 減らないよ。いま <b>${n}回</b></p><div>`;
    ms.forEach(m => { h += rowHtml(m, n, '回'); });
    return h + '</div>';
  }
  // 思い出フィギュアの ミッション（第4.138版）：作った 数 1・5・8こ → 5,000・5,000・10,000P
  function figRowsHtml() {
    const n = figN(), ms = W && P.figMissions ? P.figMissions(n, W.events) : [];
    let h = `<p class="hint" style="margin:0 0 4px">思い出のレースから 作った 思い出フィギュアの 数で ポイントが もらえるよ（しまって ある フィギュアも 数えるよ）。いま <b>${n}こ</b></p><div>`;
    ms.forEach(m => { h += rowHtml(m, n, 'こ'); });
    return h + '</div>';
  }
  function paintMission() {
    const box = $('#setMission .ptbody'); if (!box || !W) return;
    const hh = holdHtml();
    box.innerHTML = `<p class="hint" style="margin:0 0 8px">ミッションは、画面の上の<b>「ミッション」</b>からも見られるよ（受け取りもできるよ）。</p>` + (hh ? '<h3 style="margin:6px 0 4px">あずかりポイント</h3>' + hh + '<h3 style="margin:14px 0 4px">ポイントミッション</h3>' : '') + missionRowsHtml()
      + '<h3 style="margin:14px 0 4px">壁紙のミッション</h3>' + wallRowsHtml() + wallpRowsHtml()
      + '<h3 style="margin:14px 0 4px">結果ボードカスタムのミッション</h3>' + boardRowsHtml()
      + '<h3 style="margin:14px 0 4px">トレーニングセンターのミッション</h3>' + tcRowsHtml()
      + '<h3 style="margin:14px 0 4px">思い出フィギュアのミッション</h3>' + figRowsHtml();
  }
  // ---------- ミッションの 窓（第4.82版・まさちゃん「ミッションの達成状況分かりにくいから、説明書とかポイント表示とかが入ってあたりに別項目として、ミッションて欄追加して！
  //   壁紙ミッション ポイントミッション 見直し基準進捗状況」「受け取りもそこでできるようにして！」）：上の帯の「ミッション」を 押すと 開く。
  //   ポイントミッション（記録の 数）・壁紙ミッション・見直し基準の 進み具合（実測・回収タブと 同じ：chk1.js の TengelReview）。受け取るも ここで ----------
  const TROPHY = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0z"/><path d="M7 6H4a1 1 0 0 0-1 1 4 4 0 0 0 4 4M17 6h3a1 1 0 0 1 1 1 4 4 0 0 1-4 4"/></svg>';
  // 受け取れる 数の 印：メッセージ（ふきだし）の 絵＋数（まさちゃん「メッセージのマークを背景つけて、メッセージが溜まってるよ！って分かりやすくして！」）
  const BUBBLE = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M4 3h16a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H9l-5 4v-4H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z"/></svg>';
  function claimableN() { if (!W) return 0; return P.missions(countedN(), W.events).filter(m => m.claimable).length + P.wallMissions(P.wallCount(W.events, packN()), W.events).filter(m => m.claimable).length + extraMissions().filter(m => m.claimable).length + (holdCan() > 0 ? 1 : 0); }
  // あずかりポイントの 行（ミッションの 窓・設定の ミッションの いちばん 上。あずかりが ない ときは 出さない）
  function holdHtml() {
    const h = holdSum(); if (!h.total) return '';
    const can = holdCan(), parts = [['サブスクポイント', h.paid_sub], ['購入ポイント', h.paid_pack], ['獲得ポイント', h.free]].filter(x => x[1] > 0).map(x => `${x[0]} ${pts(x[1])}`).join('・');
    return `<p class="hint" style="margin:0 0 4px">上限（${pts(P.CAP)}）を こえて 届いた ポイントを あずかって いるよ。使って へった ぶんは、ここから 補充できるよ。あずかって いる あいだは 期限は 進まないよ（サブスクポイントは 補充した 日から 30日 使えるよ）。</p>`
      + `<div><div class="msrow${can ? ' can' : ''}" data-mid="hold"><div><div class="mn">あずかり中　<span class="muted" style="font-weight:400">${pts(h.total)}</span></div>`
      + `<div class="md">${esc(parts)}・${can ? `いま 補充できるのは ${pts(can)}` : `いまは いっぱい（ポイントを 使うと 補充できるよ）`}</div></div>`
      + `<div><button class="btn${can ? ' primary' : ''}" type="button" data-pt="refill"${can ? '' : ' disabled'}>補充する</button></div></div></div>`;
  }
  function reviewHtml() {
    try { if (window.TengelReview) return window.TengelReview() || ''; } catch (e) { /* なし */ }
    return '';
  }
  function paintMissionOv() {
    const ov = $('#msOv'); if (!ov || !W) return;
    const n = claimableN();
    const pg = missionProgress();
    $('.msn', ov).innerHTML = `達成 ${pg.done}/${pg.all}` + (n ? `<br>受け取れるのが ${n}つ！` : '');      // 第4.139版：上の「ミッション」の ◯/◯ と 同じ 数（達成した 数／合計）
    const hh = holdHtml(), hc = $('#msHoldCard', ov); if (hc) { hc.hidden = !hh; $('#msHold', ov).innerHTML = hh; }      // 第4.139版：あずかりポイント（ある ときだけ）
    $('#msPts', ov).innerHTML = missionRowsHtml();
    $('#msWall', ov).innerHTML = wallRowsHtml();
    $('#msWallp', ov).innerHTML = wallpRowsHtml();   // 第4.114版：壁紙の 枚数（帯の 行 #msWall とは 別の 入れ物）
    $('#msBoard', ov).innerHTML = boardRowsHtml();
    const tcb = $('#msTc', ov); if (tcb) tcb.innerHTML = tcRowsHtml();
    const fgb = $('#msFig', ov); if (fgb) fgb.innerHTML = figRowsHtml();
    const rv = reviewHtml();
    $('#msRev', ov).innerHTML = rv || '<div class="card"><h2>見直し基準の進み具合</h2><p class="hint" style="margin:0">マザーデータに接続してから見られるよ（実測・回収タブと同じものだよ）。</p></div>';
  }
  let msPrev = null;
  function openMissions() {
    if (!W || $('#msOv')) return;
    const ov = document.createElement('div'); ov.id = 'msOv'; ov.className = 'tgov'; ov.setAttribute('role', 'dialog'); ov.setAttribute('aria-modal', 'true'); ov.setAttribute('aria-label', 'ミッション');
    ov.innerHTML = `<div class="msh"><h2>${TROPHY}ミッション</h2><span class="msn"></span><button class="btn" type="button" data-ms="close">とじる</button></div>`
      + '<div class="msb"><div class="card setsec" id="msHoldCard" hidden><h2>あずかりポイント</h2><div class="ptbody" id="msHold"></div></div>'
      + '<div class="card setsec"><h2>ポイントミッション</h2><div class="ptbody" id="msPts"></div></div>'
      + '<div class="card setsec"><h2>壁紙ミッション</h2><div class="ptbody" id="msWall"></div><div class="ptbody" id="msWallp"></div></div>'
      + '<div class="card setsec"><h2>結果ボードカスタムミッション</h2><div class="ptbody" id="msBoard"></div></div>'
      + '<div class="card setsec"><h2>トレーニングセンターミッション</h2><div class="ptbody" id="msTc"></div></div>'
      + '<div class="card setsec"><h2>思い出フィギュアミッション</h2><div class="ptbody" id="msFig"></div></div><div id="msRev"></div>'
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
    // 第4.139版：1段目＝ロゴ・所有ポイント・説明書 ／（#tbrk2 で 段を かえる）2段目＝結果待ち・ミッション ／（.tbrk）3段目＝（テスト版の 印）・マザーデータの 札
    let k2 = $('#tbrk2', top); if (!k2) { k2 = document.createElement('i'); k2.id = 'tbrk2'; k2.className = 'tbrk'; k2.setAttribute('aria-hidden', 'true'); top.appendChild(k2); }
    const seq = [$('.brand', top), $('#ptsPill'), $('#manBtn'), k2, $('#rsvBtn'), $('#msBtn'), $('.tbrk:not(#tbrk2)', top), $('#testTag'), $('#dbpill')].filter(Boolean);   // 第4.122版：結果待ち（src.html）は ミッションの 左
    let prev = null;
    for (const el of seq) { if (prev && prev.nextElementSibling !== el) prev.insertAdjacentElement('afterend', el); prev = el; }
  }
  // 上の帯の「ミッション」（説明書の 下の 段・右よせ）：つぎの ミッションの 進み具合（いま／つぎ）と、受け取れる 数（水色の 数字だけ。まさちゃん「ミッションの①みたいな通知してくれてる◯は水色にして！」
  //   →「ミッション通知①の通知◯いらないかも！ 数字だけでいいや！」→「通知の数字、具ぎりが無くて分かりにくいから、メッセージのマークを背景つけて、メッセージが溜まってるよ！って分かりやすくして！」
  //   ＝四角に ふきだしの 絵と 数。色は まさちゃん「メッセージのマークの色、薄い黄緑にして！」＝うすい 黄緑 #D4F5A6）
  // 第4.139版（まさちゃん 11/10 11:59「上のミッションの◯/◯のところは合計ミッション分にして、追加がある場合は、追加していけるようにして！」）：
  //   ◯/◯＝達成した 数／ミッションの 合計（前は 記録の 数／つぎの 記録ミッションの 数）。合計は 表から 数える ので、表（points.js）に 足せば ふえる：
  //   記録（300レースまでの 12こ。そのあとは 100レースごとに つぎの 1つが ふえる）・帯の 壁紙 3・壁紙の 枚数 10・結果ボードカスタム 5・トレーニングセンター 4・思い出フィギュア 3 ＝ 37
  //   新しい 種類は extraMissions（ポイントの ミッション）に 足す
  function missionRows() {
    if (!W) return [];
    const rec = P.missions(countedN(), W.events);                                   // 達成した ところまで＋つぎの 1つ
    const rest = P.MISSIONS.slice(rec.length).map(() => ({ done: false }));         // その 先の 行（300レースまで）
    return rec.concat(rest, P.wallMissions(P.wallCount(W.events, packN()), W.events), extraMissions());
  }
  const missionProgress = () => { const r = missionRows(); return { done: r.filter(m => m.done || m.claimed).length, all: r.length }; };   // 達成＝条件を みたした（受け取る 前も 数える）
  function missionBtn() {
    const top = $('header.top .top-in'); if (!top) return;
    let b = $('#msBtn');
    if (!b) {
      b = document.createElement('button'); b.type = 'button'; b.id = 'msBtn'; b.className = 'manbtn msbtn'; b.setAttribute('aria-label', 'ミッション（押すと開くよ）');
      b.addEventListener('click', openMissions);
      top.insertBefore(b, $('#manBtn') || $('#dbpill') || null);
    }
    if (!$('.tbrk:not(#tbrk2)', top)) { const k = document.createElement('i'); k.className = 'tbrk'; k.setAttribute('aria-hidden', 'true'); b.insertAdjacentElement('afterend', k); }
    orderTop(top);
    const n = W ? countedN() : 0, next = W ? P.missions(n, W.events).find(m => !m.done) : null, c = claimableN(), pg = missionProgress();
    b.innerHTML = `${TROPHY}ミッション${pg.all ? `<span class="mp" aria-label="達成 ${pg.done}／合計 ${pg.all}">${pg.done}/${pg.all}</span>` : ''}${c ? `<span class="mbd" aria-label="受け取れるミッション ${c}つ">${BUBBLE}${c}</span>` : ''}`;
    b.classList.toggle('hot', c > 0);
    b.title = (c ? `受け取れるミッションが ${c}つ あるよ・` : '') + `達成 ${pg.done}／ぜんぶで ${pg.all}` + (next ? `（つぎの記録ミッション：${next.n}レース記録で ${pts(next.reward)}・いま ${n}レース）` : '');
  }
  function paintBadge() {
    const tb = $('.tabbar [data-tab=set]'); if (!tb || !W) return;
    const on = claimableN() > 0;
    let d = tb.querySelector('.tbdg'); if (on && !d) { d = document.createElement('span'); d.className = 'tbdg'; d.setAttribute('aria-label', '受け取れるミッションがあるよ'); tb.appendChild(d); } else if (!on && d) d.remove();
  }
  function paintHint() {
    const el = $('#ocrHint'); if (!el || !W) return;
    if (!paintHint.base) paintHint.base = el.textContent;
    el.textContent = `${paintHint.base}・1レース 200P（いま ${pts(total())}）`;
  }
  function paintAll() { paintPoints(); paintCustom(); paintMission(); paintBadge(); paintHint(); topBar(); missionBtn(); dbPillLink(); paintMissionOv(); try { paintTestBoard(); } catch (e) { /* なし */ } alignLater(); }
  async function onClick(e) {
    const b = e.target.closest('[data-pt]'); if (!b) return;
    const act = b.dataset.pt;
    if (act === 'show') { const ui = paintPoints.ui || (paintPoints.ui = {}); ui.show = ui.show === b.dataset.v ? '' : b.dataset.v; paintPoints(); if (ui.show === 'buy' || ui.show === 'sub') { await loadProducts(false); if (ui.show === 'sub') await refreshSubStatus(); paintPoints(); } return; }
    if (act === 'buy') return buy(b.dataset.id, b);
    if (act === 'restore') return restore(b);
    if (act === 'claim') return claim(b.dataset.id);
    if (act === 'refill') { b.disabled = true; return refill(); }
    if (act === 'unlock1') { paintCustom.conf = b.dataset.key; paintCustom(); return; }
    if (act === 'unlock0') { paintCustom.conf = ''; paintCustom(); return; }
    if (act === 'unlock2') {
      const key = b.dataset.key, cost = +b.dataset.cost; paintCustom.conf = '';
      b.disabled = true;
      const ok = await unlock(key, cost);
      if (ok) { toast(`✅ ${unlockName(key)}を解放したよ（残り ${pts(total())}）`, 3600); try { document.dispatchEvent(new CustomEvent('tengel:slots')); } catch (x) { /* なし */ } }
      else toast(`Pが足りないよ（${pts(cost)}いる・いま ${pts(avail())}）`, 3600);
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

  // ---------- 上の帯：所有ポイント（購入P・サブスクP・獲得P）・説明書の 置き場（第4.59版・まさちゃんの指定 2026-10-25／第4.139版で 3つに） ----------
  // 購入P＝パックで 買ったP・サブスクP＝サブスクの P（届いた 日から 30日）・獲得P＝もらったP（はじめての プレゼント・ミッション など）。押すと 設定の ポイントへ
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
        + '#msOv .msh .msn{white-space:normal;line-height:1.3}'
        + '.tgov .msh .btn{flex:none;padding:6px 12px;background:rgba(243,240,230,.1);color:var(--night-ink);border-color:rgba(243,240,230,.35)}'
        + '.tgov .msb{flex:1;min-height:0;overflow:auto;-webkit-overflow-scrolling:touch;padding:var(--gap) 16px calc(var(--sab,0px) + 28px)}.tgov .msb .card{margin:0 0 var(--gap)}#msOv #msRev .card{margin-top:0!important}'
        + '.tgov .msrow.can{background:var(--ok-bg);margin:0 -8px;padding:8px;border-radius:8px;border-top:0}'
        + 'html.mson{overflow:hidden}'
        + '#setTest{margin-bottom:var(--gap)}#setTest .row{flex-wrap:wrap}#setTest .btn{font-size:12.5px;padding:7px 10px}'
        + '@media (max-width:899px){.tbrk{display:block}#dbpill{margin-left:auto}}'
        + '#tbrk2{display:none!important}'
        + '@media (max-width:599px){header.top .top-in{column-gap:8px}'
        /* 第4.139版（まさちゃん 11/10 11:32「ポイントと説明書→の方で、画面端に合わせて！」11:37「あと結果待ちと、ポイントの項目の端できるだけ合わせて！」
           11:38「この一枚目の赤線くらいに合わせて！」＝ロゴの すぐ 右の たての 線・11:46「上のところに表示されてる時は、合計のポイントだけ」「事前に、99999まで入るように」）：
           1段目＝ロゴ・ポイントの 札（合計だけの 1行「ポイント 99,999P」）・説明書。札は ロゴの 右から 説明書（画面の 右はし）まで のびる＝数が ふえても はばは 同じ
             （flex-basis 0：中身の はばで 説明書を 次の 段へ 落とさない。上限より 多い テスト用の 数 など 入らない ときは alignTop が つめる .pc1 → .pc2＝「ポイント」の 字を かくす）。
           2段目（#tbrk2 で 段を かえる）＝結果待ちが 同じ 線から はじまって のびる・ミッションは 右はし（alignTop が --tl＝ロゴの はば＋すきま を 入れて .tl を つける）。
             はばが 足りない ときは つめる（.tc1 → .tc2 → .tc3）。それでも 入らない ときは 前と 同じ 右よせ（線より 少し 左から はじまる） */
        + '#tbrk2{display:block!important}#ptsPill{flex:1 1 0;min-width:0}'
        + '#ptsPill .pp{flex:1 1 auto;min-width:0;justify-content:center;gap:7px;padding:5px 10px 4px}#ptsPill .pl{font-size:10.5px;line-height:1.5}#ptsPill .pv{font-size:14px;line-height:1.35}#ptsPill .pv small{font-size:10.5px}'
        + '#ptsPill.pc1 .pp{gap:4px;padding:5px 5px 4px}#ptsPill.pc1 .pl{font-size:9.5px;letter-spacing:0}#ptsPill.pc1 .pv{font-size:12.5px}#ptsPill.pc1 .pv small{font-size:9.5px}#ptsPill.pc2 .pl{display:none}'
        + 'header.top .top-in #rsvBtn~#msBtn{margin-left:0!important}'
        + 'header.top .top-in.tl #rsvBtn{margin-left:var(--tl,auto)!important;flex:1 1 auto;justify-content:center}'
        + 'header.top .top-in.tc1 #rsvBtn,header.top .top-in.tc1 #msBtn{padding:4px 8px 4px 7px;gap:4px}'
        + 'header.top .top-in.tc2 #rsvBtn,header.top .top-in.tc2 #msBtn{font-size:11.5px;padding:4px 6px 4px 5px;gap:3px}header.top .top-in.tc2 #msBtn .mbd{margin-left:2px;padding:0 4px 0 3px}'
        + 'header.top .top-in.tc3 #rsvBtn,header.top .top-in.tc3 #msBtn{font-size:11px;padding:4px 5px 4px 4px;gap:2px}header.top .top-in.tc3 #rsvBtn svg,header.top .top-in.tc3 #msBtn>svg{width:13px;height:13px}'
        + 'header.top .top-in.tc3 #msBtn .mp{font-size:10px;margin-left:0}header.top .top-in.tc3 #msBtn .mbd{margin-left:1px;padding:0 3px 0 2px;gap:2px;font-size:11px}header.top .top-in.tc3 #msBtn .mbd svg{width:11px;height:11px}'
        + 'header.top .top-in.tc3 #rsvBtn .rvn{min-width:16px;height:17px;margin-left:1px;padding:0 4px;font-size:11px}header.top .top-in.tc3 #rsvBtn~#msBtn{margin-left:-2px!important}}';
      document.head.appendChild(st);
    }
    const top = $('header.top .top-in'), brand = $('header.top .brand');
    if (!top || !brand) return;
    let pill = $('#ptsPill');
    if (!pill) {
      pill = document.createElement('button'); pill.type = 'button'; pill.id = 'ptsPill'; pill.setAttribute('data-gopt', 'points'); pill.setAttribute('aria-label', '所有ポイント（合計）。押すとポイントの詳細（購入ポイント・サブスクポイント・獲得ポイント）と 買う・サブスク');
      brand.insertAdjacentElement('afterend', pill);
      if (window.__TEST && !$('#testTag')) { const t = document.createElement('span'); t.id = 'testTag'; t.textContent = 'テスト版'; pill.insertAdjacentElement('afterend', t); }
    }
    const b = W ? B() : { paid_pack: 0, paid_sub: 0, free: 0, total: 0 };
    // 第4.139版（まさちゃん 11/10 11:46「上のところに表示されてる時は、合計のポイントだけ表示するようにして！」「事前に、99999まで入るようにして作ってみて！」）：
    //   札は 合計だけ（前は 購入P＝買ったP＋もらったP と サブスクP の 2つ）。内わけ（購入ポイント・サブスクポイント・獲得ポイント）は 押すと 出る ポイントの 窓の「ポイントの詳細」
    const tot = b.total != null ? b.total : b.paid_pack + b.paid_sub + b.free;
    pill.innerHTML = `<span class="pp"><span class="pl">ポイント</span><span class="pv">${yen(tot)}<small>P</small></span></span>`;
    pill.title = `合計 ${yen(tot)}P（購入ポイント ${yen(b.paid_pack)}・サブスクポイント ${yen(b.paid_sub)}・獲得ポイント ${yen(b.free)}）・上限 ${yen(P.CAP)}P` + (W && holdN() ? `・あずかり ${yen(holdN())}P` : '');
    alignLater();
  }
  // ---------- 上の帯の 左の そろえ（第4.139版）：ポイントの 札と 結果待ちの 左はしを ロゴの すぐ 右の 線に ----------
  //   1段目は CSS だけ（札が のびる）。2段目は ロゴの はば（壁紙の 字で かわる）が いる ので ここで 数える：--tl＝ロゴの はば＋すきま。
  //   2段目の はばが 足りない ときは つめる 段を 上げる。字・数・壁紙・画面の はばが かわる たびに（ResizeObserver）数え直す
  let alignRaf = 0, alignRO = null; const alignSeen = new WeakSet();
  function alignLater() { if (!alignRaf) alignRaf = requestAnimationFrame(alignTop); }
  function alignTop() {
    if (alignRaf) { cancelAnimationFrame(alignRaf); alignRaf = 0; }
    const top = $('header.top .top-in'); if (!top) return;
    const brand = $('.brand', top), pill = $('#ptsPill'), man = $('#manBtn'), rsv = $('#rsvBtn'), ms = $('#msBtn');
    try {
      if (!alignRO && window.ResizeObserver) alignRO = new ResizeObserver(alignLater);
      if (alignRO) [top, brand, pill, man, rsv, ms].forEach(e => { if (e && !alignSeen.has(e)) { alignSeen.add(e); alignRO.observe(e); } });
    } catch (e) { /* なし */ }
    top.classList.remove('tl', 'tc1', 'tc2', 'tc3'); if (pill) pill.classList.remove('pc1', 'pc2');
    if (!brand || !pill || window.innerWidth > 599) return;
    const R = e => e.getBoundingClientRect(), F = (e, k) => parseFloat(getComputedStyle(e)[k]) || 0;
    // 1段目：札の 中身（「ポイント」＋数）が 札より 広い → つめる
    const pp = $('.pp', pill);
    if (pp) {
      const over = () => { const k = [...pp.children].filter(c => R(c).width > 0); return k.reduce((a, c) => a + R(c).width, 0) + F(pp, 'columnGap') * Math.max(0, k.length - 1) + F(pp, 'paddingLeft') + F(pp, 'paddingRight') > pill.clientWidth + 0.5; };
      if (over()) { pill.classList.add('pc1'); if (over()) pill.classList.add('pc2'); }
    }
    // 2段目：結果待ち〜ミッションの しぜんな はば（右よせの まま）が、線（ロゴの 右＋すきま）から 右はしまでに 入るか
    if (!rsv || !ms) return;
    const tr = R(top), left = tr.left + F(top, 'paddingLeft'), right = tr.right - F(top, 'paddingRight');
    const x0 = R(brand).right + F(top, 'columnGap'), span = right - x0;
    const nat = () => (Math.abs(R(ms).top - R(rsv).top) < 10 ? R(ms).right - R(rsv).left : 1e9);
    const fit = () => nat() <= span - 0.5;                                                              // 0.5px の よゆう（ぎりぎりだと ミッションが 次の 段へ 落ちる）
    let ok = fit();
    for (const c of ['tc1', 'tc2', 'tc3']) { if (ok) break; top.classList.add(c); ok = fit(); }
    if (ok) { top.style.setProperty('--tl', (x0 - left).toFixed(1) + 'px'); top.classList.add('tl'); }
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
  // 第4.162版（まさちゃん 2026/11/12 22:56「プレミアムど的中／超プレミアム神様的中／この二つ消して！」）：プレミアムど的中・超プレミアム神様的中は アプリから 消した（ボタンも なし）
  const TEST_FX = [['hit', '的中'], ['big', 'デカ的中'], ['nd', 'ノーマルど的中'], ['sd', '極ど的中'], ['miss', 'ハズレ'], ['sgd', '超神様的中'], ['gk', '神様極的中']];   // 第4.117版：神様極的中
  // ためす 結果：14頭・3連単 11→8→2（11＝11番人気の 超大穴・8＝8番人気の 大穴・2＝2番人気）・馬単 11→8 的中・ワイド 不的中（的中は 馬単だけ・ハズレは 当たりなし）
  function testSpec(kind) {
    const tri = { t: '3連単', state: '的中', hits: [[11, 8, 2]], n: 18 }, um = { t: '馬単', state: '的中', hits: [[11, 8]], n: 9 }, wd = { t: 'ワイド', state: '不的中', hits: [], n: 6 };
    const rows = kind === 'miss' ? [Object.assign({}, tri, { state: '不的中', hits: [] }), Object.assign({}, um, { state: '不的中', hits: [] }), wd] : kind === 'hit' ? [Object.assign({}, tri, { state: '不的中', hits: [] }), um, wd] : [tri, um, wd];
    return { r: 9, n: 14, rows: rows, ranks: { 11: 11, 8: 8, 2: 2, 6: 1, 10: 3 }, force: kind, streak: testStreak(kind) };
  }
  // 第4.121版：絵の ボード（1〜14）の 段を ためす 連続の 数。0＝いまの 数（的中＝連続的中・ハズレ＝続けて ハズレた 数。0 なら 1）
  //   1・2・3・4・8・16・24 を 選ぶと 的中ボタンと ハズレの どれでも その 数（ハズレは 4から 上は 4回目・出世馬は 段の 数）
  let testN = 0;
  const TEST_NS = [0, 1, 2, 3, 4, 8, 16, 24];
  function testStreak(kind) { if (testN) return testN; const b = (W && W.board) || {}; return Math.max(1, (kind === 'miss' ? b.mstreak : b.streak) || 1); }
  function testCard() {
    if (!window.__TEST) return;
    const set = $('#v-set'); if (!set || $('#setTest')) return;
    const c = document.createElement('div'); c.className = 'card setsec'; c.id = 'setTest';
    c.innerHTML = '<style>#setTest [data-test="sn"][aria-pressed="true"]{background:var(--primary);color:var(--primary-ink);border-color:var(--primary)}</style>'
      + '<h2>テスト版の道具</h2><p class="hint" style="margin:0 0 8px">この カードは テスト版だけ（App Store に 出す アプリには ない）。はじめから 10,000P 入って いるよ。</p>'
      + '<div class="row" style="margin-bottom:10px"><button type="button" class="btn" data-test="pts">10,000P 足す</button><button type="button" class="btn" data-test="pts100">上限（99,999P）まで 足す</button><button type="button" class="btn" data-test="ptcap">上限に そろえる</button><button type="button" class="btn" data-test="ptsub">サブスク 9,200P が 届いた ことに する</button></div>'
      + '<p class="hint" style="margin:0 0 6px">的中ボタンを ためす（14頭・3連単 11→8→2 の 結果で 出す。くじは ひかない）</p>'
      + '<div class="row">' + TEST_FX.map(x => `<button type="button" class="btn" data-test="fx" data-kind="${x[0]}">${x[1]}</button>`).join('') + '</div>'
      + '<p class="hint" style="margin:10px 0 6px">絵の ボードの 段（連続の 数：的中は 連勝・ハズレは 回目）：<span id="testN"></span></p>'
      + '<div class="row">' + TEST_NS.map(n => `<button type="button" class="btn" data-test="sn" data-n="${n}" aria-pressed="${n === testN}">${n ? n : 'いまの 数'}</button>`).join('') + '</div>'
      + '<p class="hint" style="margin:10px 0 6px">結果ボードカスタム（App Store の 買い物は しない）：<span id="testBoard"></span></p>'
      + '<div class="row"><button type="button" class="btn" data-test="bown">買ったことにする</button><button type="button" class="btn" data-test="bread">読み込み +' + P.BOARD.steps[0][1] + '</button><button type="button" class="btn" data-test="ball">全部 解放</button></div>'
      + '<p class="hint" style="margin:10px 0 6px">壁紙パック（App Store の 買い物は しない）：<span id="testPack"></span></p>'
      + '<div class="row"><button type="button" class="btn" data-test="pown">買ったことにする</button><button type="button" class="btn" data-test="pread">読み込み +5</button><button type="button" class="btn" data-test="pall">全部 解放</button></div>'
      + '<p class="hint" style="margin:10px 0 6px">お得パック（壁紙パックと 結果ボードカスタムの セット・App Store の 買い物は しない）：<span id="testBundle"></span></p>'
      + '<div class="row"><button type="button" class="btn" data-test="uown">買ったことにする</button></div>'
      + '<p class="hint" style="margin:10px 0 6px">トレーニングセンターの チケット（壁紙の 解放か ' + pts(P.TICKET_POINTS) + ' に かえるか 選べる）：<span id="testTk"></span></p>'
      + '<div class="row"><button type="button" class="btn" data-test="tkadd">チケットを 1枚 もらう</button></div>'
      // 第4.154版：トレーニングセンターの テスト（幻の馬・神様馬を 出す／お世話の 当たりを えらぶ）は トレーニングセンターの 中の 道具箱（tc/tc_test.js）
      //   「幻」の 字は テーマの しぼった 字に ない ので、ここは ひらがな（この 画面は テーマの 字で 出る。トレーニングセンターの 中は 別の 字）
      + '<p class="hint" id="testTcHint" style="margin:10px 0 0">トレーニングセンターの テスト（まぼろしの馬・神様馬を 出す／お世話の 当たりを ぜんぶ えらべる）：トレーニングセンターを ひらいて、上の「🧪 テスト」を 押してね</p>';
    set.insertBefore(c, set.firstChild);
    c.addEventListener('click', async e => {
      const b = e.target.closest('[data-test]'); if (!b) return;
      if (b.dataset.test === 'pts' || b.dataset.test === 'pts100') {      // 第4.139版：上限（99,999P）まで。「上限まで 足す」は いま 入る ぶん ぜんぶ
        const n = Math.min(b.dataset.test === 'pts100' ? P.CAP : TEST_GIFT, P.room(total()));
        if (n <= 0) { toast(`ポイントが いっぱい（上限 ${pts(P.CAP)}）だよ（いま ${pts(total())}）`, 2600); return; }
        W.events.push(P.giftEvent(Date.now(), n, 'gift-test-' + Date.now(), 'テスト版のポイント')); await save(); paintAll(); toast(`テスト用に ${pts(n)}を 足したよ（いま ${pts(total())}）`, 2600);
      }
      else if (b.dataset.test === 'ptcap') {      // 上限より 多く 持って いる テスト用の 端末を 上限に そろえる（こえた ぶんを 使った ことに する）
        const over = total() - P.CAP;
        if (over <= 0) { toast(`もう 上限（${pts(P.CAP)}）より 少ないよ（いま ${pts(total())}）`, 2600); return; }
        const next = P.spend(W.events, over, 'テスト版：上限に そろえる', device(), Date.now()); if (!next) return;
        W.events = next; await save(); paintAll(); toast(`テスト用に ${pts(over)}を へらして 上限（${pts(P.CAP)}）に そろえたよ`, 3000);
      }
      else if (b.dataset.test === 'ptsub') {      // 第4.139版：サブスクの 更新が 届いた ことに する（App Store の 買い物は しない）。上限を こえる ぶんは あずかりポイントへ → ミッションの 窓で 補充を ためせる
        const now = Date.now(), e = P.txEvent(W.events, { id: 'test-' + now, product: 'jp.tengel.app.sub9200', date: new Date(now).toISOString() }, now);
        if (!e) return;
        const c = credit(e); await save(); paintAll();
        toast(`🧪 サブスクの ${pts(c.added + c.held)} が 届いた ことに したよ（いま ${pts(total())}）${heldNote(c.held)}`, c.held ? 6000 : 3000);
      }
      else if (b.dataset.test === 'sn') { testN = +b.dataset.n || 0; $$('[data-test="sn"]', c).forEach(x => x.setAttribute('aria-pressed', String(+x.dataset.n === testN))); }
      else if (b.dataset.test === 'fx' && window.TengelFx) { try { window.TengelFx.prime(); } catch (x) { /* なし */ } window.TengelFx.show(testSpec(b.dataset.kind)); }
      else if (b.dataset.test === 'bown') { if (!P.boardOwned(W.events)) { const now = Date.now(); W.events.push(P.txEvent(W.events, { id: 'test-' + now, product: P.BOARD.product, date: new Date(now).toISOString() }, now)); await save(); boardEmit('owned', { src: 'test' }); toast('🧪 結果ボードカスタムを 買ったことにしたよ', 2600); } }
      else if (b.dataset.test === 'bread' || b.dataset.test === 'ball') {
        if (!P.boardOwned(W.events)) { toast('先に「買ったことにする」を 押してね', 2600); return; }
        const n0 = P.boardUnlocked(W.board.reads);
        W.board.reads = b.dataset.test === 'ball' ? P.BOARD_NEED[P.BOARD_NEED.length - 1] : W.board.reads + P.BOARD.steps[0][1];
        const got = boardOpened(n0, P.boardUnlocked(W.board.reads));
        await save(); if (got.length) boardEmit('unlock', { item: got[got.length - 1].id, no: got[got.length - 1].no, many: got.length });
      }
      else if (b.dataset.test === 'tkadd') {      // 第4.141版：チケットを ためす（当たりは まれ（第4.142版から 1/600）なので テスト版では ここから）
        try { window.TCInfo.backTicket(); } catch (x) { /* なし */ }
        try { document.dispatchEvent(new CustomEvent('tengel:tc')); } catch (x) { /* なし */ }
        paintTestBoard(); toast(`🧪 チケットを 1枚 足したよ（いま ${window.TCInfo ? window.TCInfo.tickets() : 0}枚）。設定の「着せ替え」で 使えるよ`, 4200);
      }
      else if (b.dataset.test === 'uown') { if (!P.bundleOwned(W.events)) { const now = Date.now(); W.events.push(P.txEvent(W.events, { id: 'test-bundle-' + now, product: P.BUNDLE.product, date: new Date(now).toISOString() }, now)); await save(); unlockEmit('bundle', 'owned', { src: 'test' }); toast('🧪 お得パックを 買ったことにしたよ（壁紙パックと 結果ボードカスタム）', 2600); } }
      else if (b.dataset.test === 'pown') { if (!P.packOwned(W.events)) { const now = Date.now(); W.events.push(P.txEvent(W.events, { id: 'test-pack-' + now, product: P.WALLPACK.product, date: new Date(now).toISOString() }, now)); await save(); packEmit('owned', { src: 'test' }); toast('🧪 壁紙パックを 買ったことにしたよ', 2600); } }
      else if (b.dataset.test === 'pread' || b.dataset.test === 'pall') {
        if (!P.packOwned(W.events)) { toast('先に「買ったことにする」（壁紙パック）を 押してね', 2600); return; }
        const n0 = P.packUnlocked(W.pack.reads);
        W.pack.reads = b.dataset.test === 'pall' ? P.WALLPACK.every * P.WALLPACK.n : W.pack.reads + P.WALLPACK.every;
        const n1 = P.packUnlocked(W.pack.reads);
        await save(); if (n1 > n0) packEmit('unlock', { no: n1, many: n1 - n0 });
      }
      paintTestBoard();
    });
    paintTestBoard();
  }
  function paintTestBoard() {
    const el = $('#testBoard'); if (!el || !W) return; const i = boardInfo(); const nm = id => (id === 'none' ? 'なし' : ((P.BOARD_ITEMS.find(x => x.id === id) || {}).name || 'まだ'));
    el.textContent = `${i.owned ? '買った' : 'まだ'}・読み込み ${i.reads}・解放 ${i.n}/${P.BOARD_ITEMS.length}・的中 ${nm(i.selHit)}・ハズレ ${nm(i.selMiss)}`;
    const tkEl = $('#testTk'); if (tkEl) tkEl.textContent = `いま ${window.TCInfo ? window.TCInfo.tickets() : 0}枚`;
    const en = $('#testN'); if (en) en.textContent = `いま 連続的中 ${i.streak}・続けて ハズレ ${i.mstreak}・ためす 数 ${testN ? testN : `いまの 数（的中 ${Math.max(1, i.streak)}・ハズレ ${Math.max(1, i.mstreak)}）`}`;
    const ep = $('#testPack'); if (ep) { const k = packInfo(); ep.textContent = `${k.owned ? '買った' : 'まだ'}・読み込み ${k.reads}・解放 ${k.n}/${k.total}`; }
    const eb = $('#testBundle'); if (eb) eb.textContent = P.bundleOwned(W.events) ? '買った' : 'まだ';
  }

  // ---------- 外した 壁紙を 解放して いた 人へ 返す（第4.147版・まさちゃん 2026/11/10 22:12「壁紙 …これら全部消して！」：points.js の GONE_THEMES）----------
  //   使った ポイント → 獲得ポイントで 返す（上限を こえる ぶんは あずかる）。チケットで 解放して いた もの（0P）→ チケットを 1枚 返す（tc/tc_launch.js の TCInfo.backTicket）。
  //   1つの 壁紙に 1回 だけ（台帳の back-theme:<名前>）。チケットを 返せなかった とき（TCInfo が まだ ない・トレーニングセンターの 記録が ない）は しるしを 書かない ＝ つぎに 開いた ときに もう一度。
  //   チケットは 端末（localStorage）・台帳は DB と 置き場が ちがう ので、チケットを 返したら すぐ 端末にも 覚える（GONE_TK）：台帳を 保存する 前に アプリが 閉じても、つぎに 開いた ときに 2枚目は 返さない
  //   使って いた 壁紙は kisekae.js が「いつもの」に もどす（一覧に ない 名前は 使えない）
  const GONE_TK = 'tengel.gonetk';
  const goneTkDone = () => { try { const a = JSON.parse(localStorage.getItem(GONE_TK) || '[]'); return Array.isArray(a) ? a.map(String) : []; } catch (e) { return []; } };
  async function goneBack() {
    if (!W || typeof P.goneUnlocks !== 'function') return null;
    const list = P.goneUnlocks(W.events, W.hold.map(h => String(h.id)));
    if (!list.length) return null;
    let back = 0, held = 0, tk = 0, changed = false; const names = [];
    list.forEach(g => {
      if (g.cost > 0) {
        const c = credit(P.rowEvent({ id: g.id, reward: g.cost, label: `なくなった壁紙「${g.name}」のポイントを返した` }, Date.now()));
        back += c.added + c.held; held += c.held; names.push(g.name); changed = true;
      } else {
        const done = goneTkDone();
        let ok = done.indexOf(g.theme) >= 0, fresh = false;      // ok（はじめから）＝もう チケットは 返して ある（前に 開いた とき、台帳を 保存する 前に 閉じた）→ しるし だけ 書く
        if (!ok) {
          try { ok = !!(window.TCInfo && typeof window.TCInfo.backTicket === 'function' && window.TCInfo.backTicket()); } catch (e) { ok = false; }
          if (ok) { fresh = true; try { localStorage.setItem(GONE_TK, JSON.stringify(done.concat([g.theme]))); } catch (e) { /* 覚えられなくても 台帳の しるしが ある */ } }
        }
        if (!ok) return;
        W.events.push(P.rowEvent({ id: g.id, reward: 0, label: `なくなった壁紙「${g.name}」のチケットを返した` }, Date.now()));
        changed = true;
        if (fresh) { tk += 1; names.push(g.name); }
      }
    });
    if (!changed) return null;
    await save(); paintAll();
    if (names.length) {
      const what = [back ? pts(back) : '', tk ? `チケット ${tk}枚` : ''].filter(Boolean).join(' と ');
      toast(`なくなった壁紙（${names.join('・')}）の ${what} を返したよ` + heldNote(held), 7000);
    }
    return { names: names, back: back, held: held, tickets: tk };
  }
  // tc_launch.js（TCInfo）は この ファイルの あとに 読まれる ので、ページを 読みおわって から。
  //   アプリを 開いた ときの 画面（#gate：html.gateon）が 出て いる あいだは 待つ（お知らせが その うしろで 消えない ように。2分 たっても 出て いたら 待たずに 返す）
  function goneBackSoon() {
    let tries = 0;
    const go = () => {
      if (document.documentElement.classList.contains('gateon') && tries++ < 400) { setTimeout(go, 300); return; }
      goneBack().catch(() => { /* つぎに 開いた とき */ });
    };
    const run = () => setTimeout(go, 600);
    if (document.readyState === 'complete') run(); else window.addEventListener('load', run, { once: true });
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
    goneBackSoon();                                  // 第4.147版：外した 壁紙の ポイント・チケットを 返す（1回 だけ）
    pullTransactions().then(pullEntitlements).catch(() => {});
    refreshSubStatus().catch(() => {});
  }
  window.TengelWallet = {
    on: true, ready: walletReady, COST: P.COST,
    balance: () => B(), total, events: () => (W ? W.events.slice() : []), countedN,
    readCharge, countRace, unlocked, typeLocked, slotUnlocked, unlock, claim, goSettings, lockZoom, gateOpen, gateClose, openMissions, closeMissions, openPoints, closePoints,
    // 第4.130版：トレーニングセンターの 当たり（お世話の ポイント・ルーレット）→ 獲得ポイント（無償）。id は 1回だけ
    //   第4.139版：上限（99,999P）を こえる ぶんは 消さずに あずかる（ミッションの 窓の「あずかりポイント」→ 使って あきが できたら 補充）
    grant: async (id, n, what) => {
      await walletReady; if (!W || !id || !(n > 0) || P.has(W.events, id) || W.hold.some(h => h.id === String(id))) return false;
      const c = credit(P.rowEvent({ id: String(id), reward: Math.round(n), label: String(what || 'トレーニングセンター') }, Date.now())); await save(); paintAll();
      if (c.held) toast(`上限 ${pts(P.CAP)} なので、${pts(c.added + c.held)} の うち ${pts(c.held)} は あずかったよ（ミッションの 窓で 補充できるよ）`, 5200);
      return true;
    },
    // 第4.139版：あずかりポイント（上限を こえて 届いた ぶん）。hold＝{ total, paid_sub, paid_pack, free }・avail＝財布＋あずかり（上限まで：使えるかを 見る ときは これ）・refill＝補充
    hold: () => holdSum(), avail, refill,
    goneBack,      // 第4.147版：外した 壁紙の ポイント・チケットを 返す（起動の ときに 自分で よぶ・もう 返した ものは 何も しない）
    // 結果ボードカスタム（第4.91版・bcx.js が 使う）
    board: { info: boardInfo, active: boardActive, select: boardSelect, result: boardResult, buy: btn => buy(P.BOARD.product, btn), restore: btn => restore(btn),
      price: () => price(P.BOARD.product), products: () => loadProducts(false) },
    // 壁紙パック（第4.92版・kisekae.js が 使う）
    pack: { info: packInfo, buy: btn => buy(P.WALLPACK.product, btn), restore: btn => restore(btn), price: () => price(P.WALLPACK.product), products: () => loadProducts(false) },
    // お得パック（第4.114版・bcx.js と kisekae.js が 使う）：offer＝出すか（単品を どちらも 持って いない とき）
    bundle: { owned: () => !!W && P.bundleOwned(W.events), offer: () => !!W && P.bundleOffer(W.events), buy: btn => buy(P.BUNDLE.product, btn), price: () => price(P.BUNDLE.product), products: () => loadProducts(false) },
    // 思い出フィギュア（第4.134版・fig/fig_app.js）：buy＝ポイントを 使って 作る（unlock-fig:<id>・slot を 渡せば そこに 飾る）・place＝飾る 場所（56こ）を 書く
    fig: {
      items: () => (W ? JSON.parse(JSON.stringify(W.figs.items)) : []),
      slots: () => (W ? W.figs.slots.slice() : Array(FIG_SLOTS).fill(null)),
      buy: async (item, cost, slot) => {
        await walletReady;
        if (!item || typeof item.id !== 'string' || !item.id || !(+item.n >= 1 && +item.n <= 8) || !(cost > 0)) return { ok: false, why: 'bad' };
        if (W.figs.items.some(x => x.id === item.id)) return { ok: false, why: 'dup' };
        ensure(Math.round(cost));
        const next = P.unlock(W.events, 'fig:' + item.id, Math.round(cost), device(), Date.now());
        if (!next) return { ok: false, why: 'short', need: Math.round(cost) - total() };
        W.events = next;
        const it = JSON.parse(JSON.stringify(item)); it.at = new Date().toISOString(); it.cost = Math.round(cost); W.figs.items.push(it);
        if (slot != null && slot >= 0 && slot < FIG_SLOTS && !W.figs.slots[slot]) W.figs.slots[slot] = it.id;
        await save(); return { ok: true, item: JSON.parse(JSON.stringify(it)) };
      },
      place: async slots => { await walletReady; W.figs = figNorm({ items: W.figs.items, slots }); await save(); return W.figs.slots.slice(); }
    },
    // 自動バックアップ（アプリの中）に入れる・戻す。書き出すバックアップ（共有シート）には入れない
    snapshot: () => (W ? JSON.parse(JSON.stringify(W)) : null),
    restore: async snap => { await walletReady; if (!snap || !Array.isArray(snap.events)) return false; const cur = W.events.length; W = normalize(snap); await save(); await giftCheck().catch(() => {}); await goneBack().catch(() => {}); return W.events.length !== cur; },
    // まだ何も使っていない（初回プレゼントだけ・読み込みも記録もなし）なら「空」＝自動バックアップの台帳を戻してよい
    isEmpty: () => !W || (!W.events.some(e => !/^gift-(first|test)/.test(e.id)) && !W.paid.length && !Object.keys(W.counted).length && !W.hold.length)
  };
  document.addEventListener('tengel:slots', () => { if (W) { paintCustom(); } });
  document.addEventListener('tengel:tc', () => { if (W) paintAll(); });      // 第4.130版：トレーニングセンターを 閉じた（お世話の 合計 → ミッション）
  document.addEventListener('tengel:fig', () => { if (W) paintAll(); });     // 第4.138版：思い出フィギュアを 作った・ブースを 閉じた（作った 数 → ミッション・上の 帯の ポイント）
  document.addEventListener('tengel:tab', e => { if (e.detail === 'set' && W) { paintAll(); aboutGate(); testCard(); } });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
  setTimeout(aboutGate, 50);
})();
