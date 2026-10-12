(() => {
  document.documentElement.lang = 'ja';
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const ITEMS = window.__ITEMS, IN_APP = !!window.__IN_APP;
  const home = $('#home'), page = $('#page'), topbar = $('#topbar');
  const backBtn = $('#back'), toApp = $('#toApp'), closeApp = $('#closeApp'), emblem = $('.tb-emblem');
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* 保存できなくても動く */ } }
  };
  let cur = null, homeY = 0;

  function show(id) {
    const it = ITEMS.find(x => x.id === id);
    if (!it) {
      const wasItem = cur !== null;
      cur = null;
      page.hidden = true; home.hidden = false;
      topbar.hidden = !IN_APP; backBtn.hidden = true;
      if (toApp) toApp.hidden = !IN_APP;
      if (closeApp) closeApp.hidden = true;
      if (emblem) emblem.hidden = false;
      $('#tbTitle').textContent = IN_APP ? 'テンゲルⅢ 説明書' : '';
      document.title = 'テンゲルⅢ 説明書';
      if (wasItem) requestAnimationFrame(() => window.scrollTo(0, homeY));
      return;
    }
    if (cur === null) homeY = window.scrollY;
    home.hidden = true; topbar.hidden = false; page.hidden = false; backBtn.hidden = false;
    if (toApp) toApp.hidden = true;
    if (closeApp) closeApp.hidden = !IN_APP;
    if (emblem) emblem.hidden = IN_APP;
    for (const s of $$('section.item', page)) s.hidden = s.dataset.id !== id;
    $('#tbTitle').textContent = it.t;
    document.title = it.t + '｜テンゲルⅢ 説明書';
    cur = id;
    window.scrollTo(0, 0);
    store.set('tengel.manual.last', id);
  }
  // 説明書の中の移動は履歴を増やさない（「アプリに戻る」1回でアプリに戻れるように）
  function go(id) {
    const h = '#' + id;
    try { history.replaceState(null, '', h); } catch (e) { location.replace(h); return; }
    show(id);
  }
  function route() { show(decodeURIComponent(location.hash.replace(/^#/, ''))); }
  window.addEventListener('hashchange', route);
  backBtn.addEventListener('click', () => go('menu'));
  document.addEventListener('click', e => {
    const a = e.target.closest('a[href^="#"]'); if (!a) return;
    e.preventDefault(); go(a.getAttribute('href').slice(1));
  });

  // ---- アプリに戻る（iPhoneアプリの中だけ） ----
  const backToApp = e => {
    e.preventDefault();
    let fromApp = false;
    try { fromApp = !!document.referrer && new URL(document.referrer).origin === location.origin && !/manual\.html/.test(document.referrer); } catch (err) { fromApp = false; }
    if (fromApp && history.length > 1) history.back(); else location.href = './';
  };
  if (toApp) toApp.addEventListener('click', backToApp);
  if (closeApp) closeApp.addEventListener('click', backToApp);

  // ---- さがす ----
  const norm = s => String(s || '').normalize('NFKC').toLowerCase()
    .replace(/[ァ-ヶ]/g, c => String.fromCharCode(c.charCodeAt(0) - 0x60)).replace(/\s+/g, ' ');
  const bodyText = id => { const s = $('#s-' + id); if (!s) return ''; const c = s.cloneNode(true); for (const n of $$('.pager, .tomenu', c)) n.remove(); return c.textContent; };
  const index = ITEMS.map(it => ({ it, text: norm([it.t, it.d, it.kw, bodyText(it.id)].join(' ')) }));
  const q = $('#q'), qx = $('#qx'), qinfo = $('#qinfo'), start = $('#start');
  function search() {
    const words = norm(q.value).trim().split(' ').filter(Boolean);
    qx.hidden = !words.length;
    let n = 0;
    for (const { it, text } of index) {
      const ok = words.every(w => text.includes(w));
      const row = $('#m-' + it.id); if (row) row.hidden = !ok;
      if (ok) n++;
    }
    for (const g of $$('.group')) g.hidden = !$$('.mrow', g).some(r => !r.hidden);
    start.hidden = words.length > 0;
    qinfo.hidden = !words.length;
    qinfo.textContent = n ? `${n}件みつかったよ` : 'みつからなかったよ。ほかの言葉でさがしてね（例：WIN5、APIキー、的中）';
  }
  q.addEventListener('input', search);
  qx.addEventListener('click', () => { q.value = ''; search(); q.focus(); });

  // ---- 用語集をさがす ----
  const gq = $('#gq');
  if (gq) gq.addEventListener('input', () => {
    const w = norm(gq.value).trim();
    let n = 0;
    for (const t of $$('#terms .term')) { const ok = !w || norm(t.textContent).includes(w); t.hidden = !ok; if (ok) n++; }
    $('#gnone').hidden = n > 0;
  });

  // ---- コピー ----
  document.addEventListener('click', e => {
    const b = e.target.closest('[data-copy]'); if (!b) return;
    const el = document.getElementById(b.dataset.copy); if (!el) return;
    const txt = el.textContent.trim();
    const done = t => { const o = b.dataset.label || b.textContent; b.dataset.label = o; b.textContent = t; setTimeout(() => { b.textContent = o; }, 1600); };
    const pick = () => { const r = document.createRange(); r.selectNodeContents(el); const s = getSelection(); s.removeAllRanges(); s.addRange(r); done('長押しでコピーしてね'); };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(txt).then(() => done('コピーしたよ'), pick);
    else pick();
  });

  route();
})();
