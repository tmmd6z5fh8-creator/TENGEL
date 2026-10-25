// テンキー（App Store版だけ・第4.62版）：数字の 欄（inputmode="numeric"／"decimal"・type="number"）を 押しても iOS の キーボードが 出ない とき
//   （Apple Pencil で 押した とき・Swift Playgrounds の 画面 など）に、アプリの 中の テンキーを 下に 出して 打てる ように する。
//   まさちゃん「結果と、単勝5連勝の項目が全て打ち込めない、改善して！」（iPad の テスト版：欄を 押しても キーボードが 出なかった）
// 動き：
//   ・数字の 欄に 入って 0.65秒 たっても キーボードが 出ていない（アプリ（iOS）からの「キーボードが 出た」の 知らせが なく、画面の 高さも 縮まない）なら テンキーを 出す。キーボードが 出れば 出さない（あとから 出たら しまう）
//   ・キーボードで 打てている（keydown が 来た）なら、テンキーは しまう。アプリからの 知らせが ない ときは その あとも 出さない（知らせが あれば 知らせで 決める）
//   ・テンキーの 7 8 9 ／ 4 5 6 ／ 1 2 3 ／ 0 と「.」「-」（同着の 6.2・取消の 4.11・組番の 6-2-10）・⌫・「次へ」（次の 数字の 欄へ）・「完了」（しまう）
//   ・欄の 値を 入れて input（と 完了・次へで change）の イベントを 出すので、画面の 動き（○×・合計・保存）は 手で 打った ときと 同じ
//   ・Web版（ホーム画面の アプリ）には 入らない（build_pwa.py が App Store版だけ 入れる）
(function () {
  if (!window.__NATIVE) return;
  const $ = (s, r) => (r || document).querySelector(s);
  const SEL = 'input[inputmode="numeric"],input[inputmode="decimal"],input[type="number"]';
  const KEYS = [['7', '8', '9', 'bs'], ['4', '5', '6', '-'], ['1', '2', '3', '.'], ['next', '0', 'done']];
  const LABEL = { bs: '⌫', next: '次へ', done: '完了' };
  const WAIT = 650, SHRINK = 100;
  let pad = null, target = null, timer = 0, hw = false, baseH = 0, baseW = 0, kbNative = null;   // kbNative：アプリ（iOS）が 知らせた「キーボードが 出ている」（null＝まだ 知らせなし）
  const vh = () => (window.visualViewport ? window.visualViewport.height : window.innerHeight);
  function base() {   // キーボードが ない ときの 画面の 高さ（いちばん 大きかった 値。向きが 変わったら 測り直す）
    if (window.innerWidth !== baseW) { baseW = window.innerWidth; baseH = 0; }
    baseH = Math.max(baseH, vh()); return baseH;
  }
  const kbOpen = () => kbNative === true || vh() < base() - SHRINK;   // キーボードが 出ている（アプリの 知らせ か、画面の 高さが 縮んでいる）
  function css() {
    if ($('#numPadCss')) return;
    const st = document.createElement('style'); st.id = 'numPadCss';
    st.textContent = '#numPad{position:fixed;left:0;right:0;bottom:0;z-index:65;padding:8px 8px calc(8px + var(--sab,0px));background:#161F3D;color:#F3F0E6;box-shadow:0 -6px 24px rgba(0,0,0,.35);border-top:2px solid #E2A23B;font-family:var(--font,system-ui,sans-serif)}'
      + '#numPad[hidden]{display:none}'
      + '#numPad .npg{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;max-width:520px;margin:0 auto}'
      + '#numPad button{appearance:none;-webkit-appearance:none;border:0;border-radius:10px;min-height:46px;font:600 22px/1 var(--font-mono,ui-monospace,monospace);color:#162033;background:#F6F3EA;box-shadow:0 2px 0 rgba(0,0,0,.25);cursor:pointer;-webkit-tap-highlight-color:transparent;touch-action:manipulation}'
      + '#numPad button:active{transform:translateY(1px);box-shadow:none}'
      + '#numPad button.fn{font:700 15px/1 var(--font,system-ui,sans-serif);color:#F3F0E6;background:#2A3560}'
      + '#numPad button.done{background:#E2A23B;color:#1A1405}'
      + '#numPad button.next{grid-column:span 2}'
      + '#numPad .nph{display:flex;align-items:center;justify-content:space-between;max-width:520px;margin:0 auto 6px;font-size:12px;color:#C9D0E6}'
      + '#numPad .nph b{font-weight:700;color:#FFE6A8}'
      + 'html.numpadon{scroll-padding-bottom:300px}';
    document.head.appendChild(st);
  }
  function build() {
    css();
    pad = document.createElement('div'); pad.id = 'numPad'; pad.hidden = true; pad.setAttribute('role', 'group'); pad.setAttribute('aria-label', 'テンキー');
    pad.innerHTML = '<div class="nph"><span>テンキー（キーボードが 出ない ときに）</span><b class="npf"></b></div><div class="npg">'
      + KEYS.map(row => row.map(k => `<button type="button" tabindex="-1" data-k="${k}" class="${k === 'bs' ? 'fn' : k === 'next' ? 'fn next' : k === 'done' ? 'fn done' : ''}" aria-label="${LABEL[k] || k}">${LABEL[k] || k}</button>`).join('')).join('') + '</div>';
    pad.addEventListener('pointerdown', e => e.preventDefault());   // 欄から フォーカスが 外れない ように（押しても blur しない）
    pad.addEventListener('mousedown', e => e.preventDefault());
    pad.addEventListener('click', onKey);
    document.body.appendChild(pad);
  }
  function labelOf(el) {
    if (!el) return '';
    const id = el.id; if (id) { const l = document.querySelector(`label[for="${id}"]`); if (l) return l.textContent.trim(); }
    return el.getAttribute('aria-label') || el.placeholder || '';
  }
  function show(el) {
    if (!pad) build();
    target = el; pad.hidden = false; document.documentElement.classList.add('numpadon');
    const f = $('.npf', pad); if (f) f.textContent = labelOf(el);
    try { const r = el.getBoundingClientRect(), room = vh() - pad.offsetHeight - 24; if (r.bottom > room || r.top < 60) el.scrollIntoView({ block: 'center', behavior: 'smooth' }); } catch (e) { /* なし */ }
    emit('show');
  }
  function hide() {
    if (!pad || pad.hidden) { target = null; return; }
    pad.hidden = true; target = null; document.documentElement.classList.remove('numpadon');
    emit('hide');
  }
  function emit(what) { try { document.dispatchEvent(new CustomEvent('tengel:numpad', { detail: { what: what, target: target ? (target.id || target.dataset.k || '') : '' } })); } catch (e) { /* なし */ } }
  function fire(type) { if (target) target.dispatchEvent(new Event(type, { bubbles: true })); }
  function insert(ch) {
    const el = target; if (!el) return;
    if (el.type === 'number') {   // type=number は 選択位置が とれないので、うしろに 足す
      if (ch === '-' || (ch === '.' && String(el.value).includes('.'))) return;
      el.value = String(el.value || '') + ch;
    } else {
      const s = el.selectionStart == null ? el.value.length : el.selectionStart, e2 = el.selectionEnd == null ? s : el.selectionEnd;
      try { el.setRangeText(ch, s, e2, 'end'); } catch (e) { el.value = String(el.value || '') + ch; }
    }
    fire('input');
  }
  function erase() {
    const el = target; if (!el) return;
    if (el.type === 'number') el.value = String(el.value || '').slice(0, -1);
    else {
      const s = el.selectionStart == null ? el.value.length : el.selectionStart, e2 = el.selectionEnd == null ? s : el.selectionEnd;
      if (e2 > s) { try { el.setRangeText('', s, e2, 'end'); } catch (e) { el.value = el.value.slice(0, s) + el.value.slice(e2); } }
      else if (s > 0) { try { el.setRangeText('', s - 1, s, 'end'); } catch (e) { el.value = el.value.slice(0, s - 1) + el.value.slice(s); } }
    }
    fire('input');
  }
  const visible = el => { const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0 && !el.disabled && !el.readOnly; };
  function next() {
    const all = Array.from(document.querySelectorAll(SEL)).filter(visible), i = all.indexOf(target), n = i >= 0 ? all[i + 1] : null;
    fire('change');
    if (!n) { done(); return; }
    clearTimeout(timer); target = n;
    try { n.focus({ preventScroll: true }); } catch (e) { n.focus(); }
    show(n);
  }
  function done() { const t = target; fire('change'); hide(); if (t && t.blur) t.blur(); }
  function onKey(e) {
    const b = e.target.closest && e.target.closest('button[data-k]'); if (!b || !target) return;
    const k = b.dataset.k;
    if (k === 'bs') erase(); else if (k === 'next') next(); else if (k === 'done') done(); else insert(k);
  }
  document.addEventListener('focusin', e => {
    const el = e.target; if (!(el && el.matches && el.matches(SEL))) return;
    if (hw && kbNative === null) return;   // キーボードで 打てていて、アプリからの 知らせが ない（＝キーボードの 有無が 分からない）なら 出さない。知らせが あるなら 知らせで 決める（指では キーボード・ペンシルでは 出ない、が 混ざっても よい）
    base(); clearTimeout(timer);
    if (pad && !pad.hidden) { target = el; const f = $('.npf', pad); if (f) f.textContent = labelOf(el); return; }   // テンキーが 出ている まま 次の 欄へ
    timer = setTimeout(() => { if (document.activeElement !== el || (hw && kbNative === null) || kbOpen()) return; show(el); }, WAIT);
  });
  document.addEventListener('focusout', e => {
    const el = e.target; if (!(el && el.matches && el.matches(SEL))) return;
    clearTimeout(timer);
    setTimeout(() => { const a = document.activeElement; if (!(a && a.matches && a.matches(SEL))) hide(); }, 60);
  });
  document.addEventListener('keydown', e => {   // キーボード（ハード・ソフト）で 打てている → テンキーは いらない（この あとは 出さない）
    if (!e.isTrusted || !target) return;
    if (e.key && (e.key.length === 1 || e.key === 'Backspace' || e.key === 'Enter')) { hw = true; hide(); }
  });
  if (window.visualViewport) window.visualViewport.addEventListener('resize', () => { base(); if (pad && !pad.hidden && kbOpen()) hide(); });   // あとから キーボードが 出たら しまう
  // アプリ（iOS）からの 知らせ：キーボードが 出た（keyboardWillShow）／しまった（keyboardWillHide）。出たら テンキーは しまう（WKWebView では 画面の 高さが 縮まない ことが ある ので、こちらが 確か）
  document.addEventListener('tengel:native', e => {
    const d = e.detail; if (!d || d.name !== 'keyboard' || !d.payload) return;
    kbNative = !!d.payload.open;
    if (kbNative && pad && !pad.hidden) hide();
  });
  window.TengelNumpad = { show: show, hide: hide, state: () => ({ open: !!(pad && !pad.hidden), target: target ? (target.id || target.dataset.k || '') : null, hw: hw, kb: kbNative, base: base(), vh: vh() }), _reset: () => { hw = false; kbNative = null; } };
})();
