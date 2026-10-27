// 着せ替え（App Store版 第4弾：アップデート指示書 9章・16.1・16.1.1・16.2.1・16.4）
//   30テーマ＝いつもの（無料）＋ポイントで解放する26枚（1,000〜7,000P）＋帯3枚（壁紙を 8・16・25枚 あつめた ミッションで）。
//   テーマは 色・字・形（CSS の変数：html[data-ks=<id>]）・判定タブの上の絵（見本と同じ 動く壁紙：#ksBnr）・的中の PUSH と 結果のボード（fx.js が TengelKisekae.fx() で読む）。
//   見本（kisekae/themes20.py・boards.py・gen_fx.py・mock/）の CSS と HTML は kisekae/build_kisekae.py が束ねる：小さい分は window.__KS、テーマごとの大きい分は ks_<id>.json（選んだときに 1回だけ読む）。
//   選んだテーマは端末に保存（localStorage＝起動の瞬間から・設定の DB にも）。解放したかどうかは ポイントの台帳（unlock-theme:<id>・TengelWallet）。
//   「視差効果を減らす」か 設定の「演出を控えめにする」なら 壁紙は止まった絵（CSS の @media と .calm）。判定タブが見えていない間は 動きを止める（.pause ※仮）。
//   Web版（ホーム画面のアプリ）では何もしない。
(function () {
  'use strict';
  if (!window.__NATIVE || !window.__KS) return;
  const A = window.__KS;
  const $ = (s, r) => (r || document).querySelector(s);
  const TL = () => window.TengelLocal, WL = () => window.TengelWallet, FX = () => window.TengelFx;
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const yen = v => Math.round(+v || 0).toLocaleString('ja-JP'), pts = v => yen(v) + 'P';
  const KEY = 'tengel.kisekae', SETTING = 'kisekae';
  const byId = {}; A.themes.forEach(t => { byId[t.id] = t; });
  let curId = 'default', payload = null, loading = null, conf = '';
  const cache = {}, pcache = {};
  function toast(m, ms) { const t = $('#toast'); if (!t) return; t.textContent = m; t.hidden = false; clearTimeout(toast._t); toast._t = setTimeout(() => { t.hidden = true; }, ms || 2600); }
  function emit(phase) { try { document.dispatchEvent(new CustomEvent('tengel:kisekae', { detail: { phase: phase, id: curId } })); } catch (e) { /* なし */ } }

  // ---------- CSS（全テーマの変数・共通の形・@font-face） ----------
  function css() {
    if ($('#ksCss')) return;
    const st = document.createElement('style'); st.id = 'ksCss'; st.textContent = A.css;
    document.head.appendChild(st);
  }

  // ---------- 解放（ポイントの台帳） ----------
  const wallet = () => (WL() && WL().on ? WL() : null);
  const unlocked = id => id === 'default' || !!(wallet() && wallet().unlocked('theme:' + id));
  const count = () => A.paid.filter(id => unlocked(id)).length;          // ポイントで解放した壁紙の枚数（帯のミッション：8.3）
  function usable(id) { const t = byId[id]; if (!t) return false; if (!t.price && !t.band) return true; return unlocked(id); }

  // ---------- 適用 ----------
  function setAttr(id) { if (id === 'default') delete document.documentElement.dataset.ks; else document.documentElement.dataset.ks = id; }
  async function load(id) {
    if (id === 'default') return null;
    if (cache[id] !== undefined) return cache[id];
    let p = null;
    try { const r = await fetch('ks_' + id + '.json', { cache: 'force-cache' }); if (r.ok) p = await r.json(); } catch (e) { p = null; }
    cache[id] = p;
    return p;
  }
  function themeStyle(p) {
    let st = $('#ksTheme');
    if (!st) { st = document.createElement('style'); st.id = 'ksTheme'; document.head.appendChild(st); }
    st.textContent = p ? [(p.bnr && p.bnr.css) || '', (p.push && p.push.css) || '', (p.board && p.board.css) || ''].join('\n') : '';
  }
  function bnrBox() {
    let b = $('#ksBnr');
    if (!b) {
      const v = $('#v-judge'); if (!v) return null;
      b = document.createElement('div'); b.id = 'ksBnr'; b.hidden = true; b.setAttribute('aria-hidden', 'false');
      b.innerHTML = '<div class="ksb"></div>';
      v.insertBefore(b, v.firstChild);
    }
    return b;
  }
  function fitBnr() {
    const b = $('#ksBnr'); if (!b || b.hidden) return;
    const w = b.clientWidth || window.innerWidth; let k = w / 390;
    if (!isFinite(k) || k <= 0) k = 1; if (Math.abs(k - 1) < .01) k = 1;
    b.style.setProperty('--ksk', k.toFixed(4));
  }
  function paintBnr(p) {
    const b = bnrBox(); if (!b) return;
    const stage = $('.ksb', b);
    if (p && p.bnr && p.bnr.html) { stage.innerHTML = p.bnr.html; b.hidden = false; fitBnr(); } else { stage.innerHTML = ''; b.hidden = true; }
    motion();
  }
  // 動きを止める：「視差効果を減らす」か「演出を控えめにする」（.calm）・判定タブが見えていない／アプリが裏（.pause）※仮
  function motion() {
    const b = $('#ksBnr'); if (!b) return;
    const F = FX();
    b.classList.toggle('calm', !!(F && F.calm && F.calm()));
    const v = $('#v-judge');
    b.classList.toggle('pause', !!document.hidden || !!(v && v.hidden));
  }
  async function apply(id, save) {
    if (!byId[id]) id = 'default';
    curId = id; setAttr(id); conf = '';
    if (save !== false) {
      try { localStorage.setItem(KEY, id); } catch (e) { /* 覚えられなくてもOK */ }
      try { if (TL() && TL().putSetting) TL().putSetting(SETTING, { id: id }).catch(() => {}); } catch (e) { /* なし */ }
    }
    const my = loading = load(id);
    const p = await my;
    if (loading !== my || curId !== id) return;      // 途中で別のテーマにかわった
    payload = p;
    themeStyle(id === 'default' ? null : p); paintBnr(id === 'default' ? null : p);
    paint(); emit('apply');
  }
  // fx.js から：いまのテーマの 的中PUSH（面・押したあと・はじけるかけら）と ボードの飾り。いつもの・まだ読めていないときは null（＝いつもの形）
  function fx() {
    if (curId === 'default' || !payload) return null;
    return { tid: curId, pc: (payload.push && payload.push.pc) || '', push: payload.push || null, orn: (payload.board && payload.board.orn) || '' };
  }

  // ---------- 選ぶ画面（設定 › 着せ替え） ----------
  function card() {
    const set = $('#v-set'); if (!set || $('#setKisekae')) return;
    const c = document.createElement('div'); c.className = 'card setsec'; c.id = 'setKisekae'; c.style.marginBottom = 'var(--gap)';
    c.innerHTML = '<h2>着せ替え</h2><div class="ksbody"></div>';
    const after = $('#setMission');
    if (after && after.nextSibling) set.insertBefore(c, after.nextSibling); else if (after) set.appendChild(c); else set.insertBefore(c, set.firstChild);
    c.addEventListener('click', onClick);
    c.addEventListener('keydown', onKey);
    paint();
  }
  // 解放エフェクト（第4.60版：fx.js の TengelFx.unlock）：解放した 壁紙の タイルの 上で 金の 輪・つや・粒・「解放！」・チャイム
  function unlockFx(id) { try { const el = $(`#setKisekae .kst[data-ks="${id}"]`); if (el && window.TengelFx && window.TengelFx.unlock) window.TengelFx.unlock(el, { text: '解放！' }); } catch (e) { /* なし */ } }
  function lockLabel(t) {
    if (t.price) return `<span class="kslock">🔒 ${esc(pts(t.price))}</span>`;
    if (t.band) return `<span class="kslock">🔒 壁紙を${t.band}枚あつめると</span>`;
    return '';
  }
  // 選ぶ画面の 壁紙の 動き（第4.89版・まさちゃん「普段は壁紙は動かさないで、タップして選択しているときだけ壁紙が動くようにして！解放前、解放後どっちも！」）：
  //   タイルの 絵は ふだん 止まった 絵（牧場・ぷりけつの SVG も 止める）。タップして 選んだ タイル＝使用中（解放後）か 解放の 確認を 開いた タイル（解放前）だけ、
  //   判定タブの 上の絵と 同じ 動く 壁紙（ks_<id>.json の bnr）を 小さく 重ねて 動かす（.kslive › .kslv）。CSS は #ksBnr → #setKisekae .kslv に、@keyframes の 名前は kp を 足して、
  //   判定タブの 壁紙と ぶつからない ように（テーマどうしで 同じ 名前の @keyframes が ある）。設定タブが 見えていない 間は 止める（.pause）・控えめは .calm
  const liveId = () => conf || curId;
  function liveStyle() {
    let st = $('#ksPrev');
    if (!st) { st = document.createElement('style'); st.id = 'ksPrev'; document.head.appendChild(st); }
    return st;
  }
  function rescope(id, bnr) {
    if (!pcache[id]) {
      const names = []; const re = /@keyframes (kb[\w-]+)/g; let m;
      while ((m = re.exec(bnr.css))) if (names.indexOf(m[1]) < 0) names.push(m[1]);
      names.sort((a, b) => b.length - a.length);
      let css = bnr.css.split('#ksBnr').join('#setKisekae .kslv'), html = bnr.html;
      names.forEach(n => { const rx = new RegExp('\\b' + n + '\\b', 'g'); css = css.replace(rx, 'kp' + n); html = html.replace(rx, 'kp' + n); });
      pcache[id] = { css: css, html: html };
    }
    return pcache[id];
  }
  function fitLive() {
    const w = $('#setKisekae .kst .kslive'); if (!w) return;
    const W = w.clientWidth || 118, H = w.clientHeight || 58;
    w.style.setProperty('--kss', Math.max(W / 390, H / 160).toFixed(4));
  }
  function motionLive() {
    const el = $('#setKisekae .kst .kslv'); if (!el) return;
    const F = FX(), v = $('#v-set');
    el.classList.toggle('calm', !!(F && F.calm && F.calm()));
    el.classList.toggle('pause', !!document.hidden || !!(v && v.hidden));
  }
  async function paintLive() {
    const id = liveId(), el = $('#setKisekae .kst .kslv'), st = liveStyle();
    if (!el || id === 'default') { st.textContent = ''; return; }
    const p = await load(id);
    if (liveId() !== id || el !== $('#setKisekae .kst .kslv')) return;     // 待つ 間に 変わった
    if (!p || !p.bnr || !p.bnr.html) { st.textContent = ''; el.innerHTML = ''; return; }
    const r = rescope(id, p.bnr);
    st.textContent = r.css; el.innerHTML = r.html; fitLive(); motionLive();
  }
  // 解放の 確認（第4.64版）：タップした カギの 壁紙の タイルの 中（カギの 下）に 出す。前は 一覧の 上に 1本の 帯で 出していた
  //   （2026/10/25 まさちゃん「赤のところは消して、解放されていない壁紙をタップしたら下に、解放、ボタンが出てくるようにして！」）。
  //   タイルは <div role="button">（中に 本物の ボタンを 置くため）。もう一度 タイルを タップすると 閉じる
  function confBox(t, total) {
    const ok = total >= t.price;
    return `<span class="ksconf" role="group" aria-label="解放の確認"><span class="kscq">${esc(pts(t.price))}を使って解放する？<small>いま ${esc(pts(total))}</small></span>`
      + (ok ? `<button class="btn primary" type="button" data-ksact="unlock" data-id="${esc(t.id)}">解放する</button>`
        : `<span class="kscq muted">Pが足りないよ</span><button class="btn primary" type="button" data-gopt="points">ポイントを買う</button>`)
      + '<button class="btn ghost" type="button" data-ksact="cancel">やめる</button></span>';
  }
  function paint() {
    const box = $('#setKisekae .ksbody'); if (!box) return;
    const cur = byId[curId] || byId.default, n = count(), total = wallet() ? wallet().total() : 0;
    let h = `<p class="hint" style="margin:0 0 4px">いまのテーマ：<b>${esc(cur.name)}</b>。見た目だけが変わるよ。判定・記録・ポイントはそのまま。</p>`;
    h += `<p class="ptnote" style="margin:0">ポイントで解放した壁紙：<b>${n}</b>/${A.paid.length}枚（8・16・25枚で 帯の壁紙がミッションでもらえるよ）。解放した壁紙はずっと使えるよ（アプリを消すと消えるよ）。カギの壁紙をタップすると、その下に「解放する」が出るよ。</p>`;
    const groups = [];
    A.themes.forEach(t => { let g = groups.find(x => x.name === t.group); if (!g) { g = { name: t.group, items: [] }; groups.push(g); } g.items.push(t); });
    groups.forEach(g => {
      h += `<h3 class="ksg">${esc(g.name)}<small>${g.items.length}</small></h3><div class="ksgrid">`;
      g.items.forEach(t => {
        const on = t.id === curId, can = usable(t.id), cf = conf === t.id && !!t.price, lv = t.id === liveId() && t.id !== 'default';
        h += `<div role="button" tabindex="0" class="kst${on ? ' on' : ''}${can ? '' : ' lock'}${cf ? ' cf' : ''}${lv ? ' lv' : ''}" data-ks="${esc(t.id)}" aria-pressed="${on}" aria-expanded="${cf}" aria-label="${esc(t.name)}${on ? '（使用中）' : can ? '' : t.price ? `（${pts(t.price)}で解放）` : `（壁紙を${t.band}枚あつめると）`}">`
          + `<img class="ksth" src="${esc(t.thumb)}" alt="" loading="lazy" decoding="async">`
          + (lv ? '<div class="kslive" aria-hidden="true"><div class="kslv"></div></div>' : '')
          + `<span class="ksn">${esc(t.name)}</span><span class="ksd">${esc(t.desc)}</span>`
          + (on ? '<span class="ksbadge">使用中</span>' : '') + (can ? '' : lockLabel(t)) + (cf ? confBox(t, total) : '') + '</div>';
      });
      h += '</div>';
    });
    h += '<p class="ptnote" style="margin-top:12px">馬番の枠の色は、どのテーマでも同じだよ（読み間違えないように）</p>'
      + '<div class="ksnums" aria-hidden="true">' + [1, 2, 3, 4, 5, 6, 7, 8].map(i => `<span class="num w${i}">${i}</span>`).join('') + '</div>';
    box.innerHTML = h;
    paintLive();
  }
  async function onClick(e) {
    const a = e.target.closest('[data-ksact]');
    if (a) {
      if (a.dataset.ksact === 'cancel') { conf = ''; paint(); return; }
      if (a.dataset.ksact === 'unlock') {
        const id = a.dataset.id, t = byId[id]; if (!t || !wallet()) return;
        a.disabled = true;
        let ok = false;
        try { ok = await wallet().unlock('theme:' + id, t.price); } catch (x) { ok = false; }
        conf = '';
        if (ok) { toast(`✅ 「${t.name}」を解放したよ（残り ${pts(wallet().total())}）`, 3600); emit('unlock'); await apply(id, true); unlockFx(id); }
        else { toast(`Pが足りないよ（${pts(t.price)}いる・いま ${pts(wallet().total())}）`, 3600); paint(); }
        return;
      }
    }
    if (e.target.closest('.ksconf')) return;          // 確認の 文字の 所を 押しても 何も しない
    const b = e.target.closest('.kst'); if (!b) return;
    const id = b.dataset.ks, t = byId[id]; if (!t) return;
    if (id === curId) return;
    if (usable(id)) { await apply(id, true); toast(`「${t.name}」に着せ替えたよ`); return; }
    if (t.price) {
      if (conf === id) { conf = ''; paint(); return; }   // もう一度 タップ → 閉じる
      conf = id; paint();
      const c = $('#setKisekae .kst.cf'); if (c) c.scrollIntoView({ block: 'nearest' });
      return;
    }
    if (t.band) { toast(`壁紙を${t.band}枚あつめて、ミッションで受け取ると使えるよ（いま ${count()}枚）`, 3600); }
  }
  // タイルは <div role="button">：Enter か スペースで 押す
  function onKey(e) {
    if (e.key !== 'Enter' && e.key !== ' ') return;
    const b = e.target.closest('.kst'); if (!b || e.target !== b) return;
    e.preventDefault(); b.click();
  }

  // ---------- 起動 ----------
  css();
  let saved = 'default';
  try { saved = localStorage.getItem(KEY) || 'default'; } catch (e) { saved = 'default'; }
  if (!byId[saved]) saved = 'default';
  setAttr(saved); curId = saved;             // 色は起動の瞬間から（絵とPUSHは読めてから）
  const ready = (async () => {
    card();
    await apply(saved, false);
    try {
      if (TL() && TL().ready) { await TL().ready; const s = TL().getSetting ? await TL().getSetting(SETTING) : null; if (s && s.id && byId[s.id] && s.id !== curId) await apply(s.id, false); }
    } catch (e) { /* 設定が読めないときは localStorage のまま */ }
    try { if (wallet() && wallet().ready) await wallet().ready; } catch (e) { /* なし */ }
    if (!usable(curId)) await apply('default', true);   // 解放していないテーマが残っていたら いつものに
    paint();
  })();
  document.addEventListener('tengel:wallet', () => { paint(); if (!usable(curId)) apply('default', true); });
  document.addEventListener('tengel:tab', e => { if (e.detail === 'set') { card(); paint(); } motion(); motionLive(); if (e.detail === 'judge') fitBnr(); });
  document.addEventListener('tengel:fx', e => { if (e.detail && e.detail.phase === 'settings') { motion(); motionLive(); } });
  document.addEventListener('visibilitychange', () => { motion(); motionLive(); });
  window.addEventListener('resize', () => { fitBnr(); fitLive(); });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', card);

  window.TengelKisekae = {
    on: true, ready: ready, list: () => A.themes.slice(), current: () => curId, apply: id => apply(id, true), usable: usable, unlocked: unlocked, count: count, fx: fx,
    loaded: () => curId === 'default' || !!payload, band: Object.assign({}, A.band), paid: A.paid.slice(), motion: motion, live: liveId
  };
})();
