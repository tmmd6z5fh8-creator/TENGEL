// かなキーボード（App Store版だけ・第4.237版）：文字の 欄（data-kana の ついた 欄：いまは トレーニングセンターの 牧場の 名前）を 押しても
//   iOS の キーボードが 出ない とき に、アプリの 中の 50音の キーボードを 下に 出して 打てる ように する。
//   わけ：iPadOS 27 の Swift Playgrounds で 動かした アプリでは、文字の 欄を 押しても キーボードが 出ない（Apple の 不具合：Apple の 見本の アプリでも 同じ）。
//   第4.235版の iOS の 窓（UIAlertController の 1行の 欄）でも 出なかった（2026/11/28 12:32 の 写真：欄に カーソルは 入って いるのに キーボードが ない）。
//   Apple Pencil で 押した ときも キーボードが 出ない ことが ある（第4.62版の テンキー numpad.js と 同じ わけ）
// 動き（テンキーと 同じ 決まり）：
//   ・欄に 入って 0.65秒 たっても キーボードが 出ていない（アプリ（iOS）からの「キーボードが 出た」の 知らせが なく、画面の 高さも 縮まない）なら 出す。
//     キーボードが 出れば 出さない（あとから 出たら しまう）
//   ・キーボード（ハード・ソフト）で 打てている（keydown が 来た）なら しまう。アプリからの 知らせが ない ときは その あとも 出さない（知らせが あれば 知らせで 決める）
//   ・表は 4つ：あ（ひらがな）・ア（カタカナ）・A（英数）・漢（よく 使う 漢字 50）。゛ ゜ 小 は 前の 字に つける（もう 1回 押すと もどる・小 は 英字の 大文字／小文字も）
//   ・ー ・ ！ ？・空白・◀ ▶（字の 間を 動く）・⌫・クリア（ぜんぶ 消す）・完了（しまう）
//   ・TengelKana.show(欄, true)：画面の ボタンから 出す（アプリの 知らせが「キーボードが 出た」でも 出す：知らせが まちがって いる とき の 予備。しまうまで 知らせでは しまわない）
//   ・欄の 値を 入れて input の イベントを 出すので、画面の 動き（字の 数・決める）は 手で 打った ときと 同じ。押しても 欄の フォーカスは 外れない
//   ・Web版（ホーム画面の アプリ）には 入らない（build_pwa.py が App Store版だけ 入れる）
(function () {
  if (!window.__NATIVE) return;
  const $ = (s, r) => (r || document).querySelector(s);
  const SEL = 'input[data-kana],textarea[data-kana]';
  const WAIT = 650, SHRINK = 100;
  const row = s => Array.from(s).map(c => (c === '＿' ? '' : c));      // ＿ は 空きの ます
  const HIRA = ['あかさたなはまやらわ', 'いきしちにひみ＿り＿', 'うくすつぬふむゆるを', 'えけせてねへめ＿れ＿', 'おこそとのほもよろん'].map(row);
  const kata = c => (c ? String.fromCharCode(c.charCodeAt(0) + 0x60) : '');
  const TABLE = {
    h: HIRA,
    k: HIRA.map(r => r.map(kata)),
    a: ['ABCDEFGHIJ', 'KLMNOPQRST', "UVWXYZ&.-'", '1234567890', '()#@★☆♡♪+_'].map(row),
    j: ['牧場馬駒厩舎第号大地', '新天空星月日光夢王神', '金銀白黒赤青緑紅桜花', '山川海森風雷北南東西', '田野原島竜虎鷹幸福勝'].map(row)
  };
  const MODES = [['h', 'あ', 'ひらがな'], ['k', 'ア', 'カタカナ'], ['a', 'A', '英数'], ['j', '漢', 'よく 使う 漢字']];
  const HEAD = { h: 'かなキーボード（キーボードが 出ない ときに）', k: 'かなキーボード（キーボードが 出ない ときに）', a: '英数（小 で 小文字・大文字）', j: 'よく 使う 漢字' };
  // ゛ ゜ 小 の 表（ひらがな と カタカナ）：もう 1回 押すと もどる。ぱ に ゛ → ば・ば に ゜ → ぱ
  const DK = {}, HD = {}, SM = {};
  const both = s => s + Array.from(s).map(kata).join('');
  const pairs = (s, m, back) => { const a = Array.from(s); for (let i = 0; i + 1 < a.length; i += 2) { m[a[i]] = a[i + 1]; if (back) m[a[i + 1]] = a[i]; } };
  pairs(both('かがきぎくぐけげこごさざしじすずせぜそぞただちぢつづてでとどはばひびふぶへべほぼうゔ'), DK, true);
  pairs(both('ぱばぴびぷぶぺべぽぼ'), DK, false);
  pairs(both('はぱひぴふぷへぺほぽ'), HD, true);
  pairs(both('ばぱびぴぶぷべぺぼぽ'), HD, false);
  pairs(both('あぁいぃうぅえぇおぉつっやゃゆゅよょわゎ') + 'カヵケヶ', SM, true);
  let pad = null, target = null, timer = 0, hw = false, baseH = 0, baseW = 0, kbNative = null, mode = 'h', forced = false;
  const vh = () => (window.visualViewport ? window.visualViewport.height : window.innerHeight);
  function base() {   // キーボードが ない ときの 画面の 高さ（いちばん 大きかった 値。向きが 変わったら 測り直す）
    if (window.innerWidth !== baseW) { baseW = window.innerWidth; baseH = 0; }
    baseH = Math.max(baseH, vh()); return baseH;
  }
  const kbOpen = () => kbNative === true || vh() < base() - SHRINK;
  function css() {
    if ($('#kanaPadCss')) return;
    const st = document.createElement('style'); st.id = 'kanaPadCss';
    st.textContent = '#kanaPad{position:fixed;left:0;right:0;bottom:0;z-index:95;padding:6px 6px calc(8px + var(--sab,0px));background:#161F3D;color:#F3F0E6;box-shadow:0 -6px 24px rgba(0,0,0,.35);border-top:2px solid #E2A23B;font-family:var(--font-body,system-ui,sans-serif);-webkit-user-select:none;user-select:none;touch-action:manipulation}'
      + '#kanaPad[hidden]{display:none}'
      + '#kanaPad .kph{display:flex;align-items:center;justify-content:space-between;gap:8px;max-width:560px;margin:0 auto 5px;padding:0 2px;font-size:11.5px;line-height:15px;color:#C9D0E6}'
      + '#kanaPad .kph span{min-width:0;overflow:hidden;white-space:nowrap;text-overflow:ellipsis}'
      + '#kanaPad .kph b{flex:none;font-weight:700;color:#FFE6A8;white-space:nowrap}'
      + '#kanaPad .kpg{display:grid;grid-template-columns:repeat(10,minmax(0,1fr));gap:4px;max-width:560px;margin:0 auto}'
      + '#kanaPad button{appearance:none;-webkit-appearance:none;border:0;border-radius:8px;min-width:0;height:40px;padding:0;margin:0;font:500 19px/1 var(--font-body,system-ui,sans-serif);color:#162033;background:#F6F3EA;box-shadow:0 2px 0 rgba(0,0,0,.25);cursor:pointer;-webkit-tap-highlight-color:transparent;touch-action:manipulation}'
      + '#kanaPad button:active{transform:translateY(1px);box-shadow:none;background:#FFE6A8}'
      + '#kanaPad button.fn{font:700 15px/1 var(--font-body,system-ui,sans-serif);color:#F3F0E6;background:#2A3560}'
      + '#kanaPad button.fn.on{background:#E2A23B;color:#1A1405}'
      + '#kanaPad button.fn.mk{font-size:28px;font-weight:400}'
      + '#kanaPad button.s2{grid-column:span 2}'
      + '#kanaPad button.done{background:#E2A23B;color:#1A1405}'
      + '#kanaPad button.ng{animation:kpNg .25s}'
      + '@keyframes kpNg{0%,100%{transform:none}30%{transform:translateX(-3px)}70%{transform:translateX(3px)}}'
      + '#kanaPad .kpe{display:block;height:40px}'
      + 'html.kanapadon{scroll-padding-bottom:340px}';
    document.head.appendChild(st);
  }
  const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const key = (k, label, cls, aria) => `<button type="button" tabindex="-1" data-k="${esc(k)}"${cls ? ` class="${cls}"` : ''} aria-label="${esc(aria || label)}">${esc(label)}</button>`;
  function paint() {
    if (!pad) return;
    let h = MODES.map(([m, l, a]) => key('m:' + m, l, 'fn' + (m === mode ? ' on' : ''), a)).join('')
      + key('f:left', '◀', 'fn', '前へ') + key('f:right', '▶', 'fn', '次へ') + key('f:bs', '⌫', 'fn s2', '1字 消す') + key('f:clr', 'クリア', 'fn s2', 'ぜんぶ 消す');
    for (const r of TABLE[mode]) h += r.map(c => (c ? key('c:' + c, c) : '<span class="kpe"></span>')).join('');
    h += key('f:dk', '゛', 'fn mk', '濁点') + key('f:hd', '゜', 'fn mk', '半濁点') + key('f:sm', '小', 'fn', mode === 'a' ? '大文字と 小文字' : '小さい 字')
      + key('c:ー', 'ー') + key('c:・', '・') + key('c:！', '！') + key('c:？', '？') + key('c: ', '空白', 'fn', '空白') + key('f:done', '完了', 'fn s2 done');
    $('.kpg', pad).innerHTML = h;
    $('.kpt', pad).textContent = HEAD[mode];
  }
  function build() {
    css();
    pad = document.createElement('div'); pad.id = 'kanaPad'; pad.hidden = true; pad.setAttribute('role', 'group'); pad.setAttribute('aria-label', 'かなキーボード');
    pad.innerHTML = '<div class="kph"><span class="kpt"></span><b class="kpf"></b></div><div class="kpg"></div>';
    pad.addEventListener('pointerdown', e => e.preventDefault());   // 欄から フォーカスが 外れない ように（押しても blur しない）
    pad.addEventListener('mousedown', e => e.preventDefault());
    pad.addEventListener('click', onKey);
    document.body.appendChild(pad);
    paint();
  }
  function labelOf(el) {
    if (!el) return '';
    const id = el.id; if (id) { const l = document.querySelector(`label[for="${id}"]`); if (l) return l.textContent.trim(); }
    return el.getAttribute('aria-label') || el.placeholder || '';
  }
  function emit(what) { try { document.dispatchEvent(new CustomEvent('tengel:kanapad', { detail: { what: what, mode: mode } })); } catch (e) { /* なし */ } }
  function show(el, force) {
    if (!el) return;
    if (!pad) build();
    if (force) forced = true;
    target = el; const was = !pad.hidden; pad.hidden = false; document.documentElement.classList.add('kanapadon');
    const f = $('.kpf', pad); if (f) f.textContent = labelOf(el);
    try { const r = el.getBoundingClientRect(), room = vh() - pad.offsetHeight - 16; if (r.bottom > room || r.top < 0) el.scrollIntoView({ block: 'center', behavior: 'smooth' }); } catch (e) { /* なし */ }
    if (!was) emit('show');
  }
  function hide() {
    if (!pad || pad.hidden) { target = null; return; }
    pad.hidden = true; target = null; forced = false; document.documentElement.classList.remove('kanapadon');
    emit('hide');
  }
  function setMode(m) { if (!TABLE[m]) return; mode = m; paint(); emit('mode'); }
  function sel(el) {
    const v = String(el.value || ''); let s = el.selectionStart, e = el.selectionEnd;
    if (s == null) s = v.length; if (e == null) e = s;
    return { v: v, s: Math.min(s, e), e: Math.max(s, e) };
  }
  function put(el, v, at) {
    el.value = v;
    try { el.setSelectionRange(at, at); } catch (e) { /* なし */ }
    el.dispatchEvent(new Event('input', { bubbles: true }));
  }
  const hiS = c => c >= 0xD800 && c <= 0xDBFF, loS = c => c >= 0xDC00 && c <= 0xDFFF;
  const back = (v, i) => (i >= 2 && loS(v.charCodeAt(i - 1)) && hiS(v.charCodeAt(i - 2)) ? 2 : i >= 1 ? 1 : 0);      // 前の 1字の 長さ（絵文字などは 2）
  const fwd = (v, i) => (i + 1 < v.length && hiS(v.charCodeAt(i)) && loS(v.charCodeAt(i + 1)) ? 2 : i < v.length ? 1 : 0);
  function insert(ch) {
    const el = target; if (!el) return false;
    const q = sel(el), nv = q.v.slice(0, q.s) + ch + q.v.slice(q.e);
    if (el.maxLength > 0 && nv.length > el.maxLength) return false;
    put(el, nv, q.s + ch.length); return true;
  }
  function erase() {
    const el = target; if (!el) return false; const q = sel(el);
    if (q.e > q.s) { put(el, q.v.slice(0, q.s) + q.v.slice(q.e), q.s); return true; }
    const n = back(q.v, q.s); if (!n) return false;
    put(el, q.v.slice(0, q.s - n) + q.v.slice(q.s), q.s - n); return true;
  }
  function move(d) {
    const el = target; if (!el) return false; const q = sel(el);
    const p = d < 0 ? (q.e > q.s ? q.s : q.s - back(q.v, q.s)) : (q.e > q.s ? q.e : q.s + fwd(q.v, q.s));
    try { el.setSelectionRange(p, p); } catch (e) { /* なし */ }
    return true;
  }
  function modify(map, kind) {   // 前の 字（カーソルの 左）に ゛ ゜ 小 を つける・もう 1回で もどる
    const el = target; if (!el) return false; const q = sel(el);
    if (q.e < 1) return false;
    const c = q.v[q.e - 1]; let r = map[c];
    if (!r && kind === 'sm' && /[A-Za-z]/.test(c)) r = c === c.toUpperCase() ? c.toLowerCase() : c.toUpperCase();
    if (!r) return false;
    put(el, q.v.slice(0, q.e - 1) + r + q.v.slice(q.e), q.e); return true;
  }
  function done() { const t = target; if (t) t.dispatchEvent(new Event('change', { bubbles: true })); hide(); if (t && t.blur) t.blur(); }
  function onKey(e) {
    const b = e.target.closest && e.target.closest('button[data-k]'); if (!b || !target) return;
    const k = b.dataset.k, t = k.slice(0, 2), v = k.slice(2);
    let ok = true;
    if (t === 'c:') ok = insert(v);
    else if (t === 'm:') setMode(v);
    else if (v === 'bs') ok = erase();
    else if (v === 'clr') { const el = target; if (el.value) put(el, '', 0); }
    else if (v === 'left') move(-1);
    else if (v === 'right') move(1);
    else if (v === 'dk') ok = modify(DK, 'dk');
    else if (v === 'hd') ok = modify(HD, 'hd');
    else if (v === 'sm') ok = modify(SM, 'sm');
    else if (v === 'done') { done(); return; }
    if (!ok) { b.classList.remove('ng'); void b.offsetWidth; b.classList.add('ng'); }      // つけられない・入らない ときは 小さく ゆれる
  }
  document.addEventListener('focusin', e => {
    const el = e.target; if (!(el && el.matches && el.matches(SEL))) return;
    if (hw && kbNative === null) return;   // キーボードで 打てていて、アプリからの 知らせが ない（＝キーボードの 有無が 分からない）なら 出さない
    base(); clearTimeout(timer);
    if (pad && !pad.hidden) { target = el; const f = $('.kpf', pad); if (f) f.textContent = labelOf(el); return; }
    timer = setTimeout(() => { if (document.activeElement !== el || (hw && kbNative === null) || kbOpen()) return; show(el); }, WAIT);
  });
  document.addEventListener('focusout', e => {
    const el = e.target; if (!(el && el.matches && el.matches(SEL))) return;
    clearTimeout(timer);
    setTimeout(() => { const a = document.activeElement; if (!(a && a.matches && a.matches(SEL))) hide(); }, 60);
  });
  document.addEventListener('keydown', e => {   // キーボード（ハード・ソフト）で 打てている → かなキーボードは いらない
    if (!e.isTrusted || !target) return;
    if (e.key && (e.key.length === 1 || e.key === 'Backspace' || e.key === 'Enter' || e.key === 'Process')) { hw = true; hide(); }
  });
  if (window.visualViewport) window.visualViewport.addEventListener('resize', () => { base(); if (pad && !pad.hidden && !forced && kbOpen()) hide(); });
  // アプリ（iOS）からの 知らせ：キーボードが 出た（keyboardWillShow）／しまった（keyboardWillHide）。出たら しまう
  document.addEventListener('tengel:native', e => {
    const d = e.detail; if (!d || d.name !== 'keyboard' || !d.payload) return;
    kbNative = !!d.payload.open;
    if (kbNative && pad && !pad.hidden && !forced) hide();
  });
  window.TengelKana = {
    show: show, hide: hide, mode: setMode,
    state: () => ({ open: !!(pad && !pad.hidden), target: target ? (target.id || target.getAttribute('aria-label') || '') : null, mode: mode, hw: hw, kb: kbNative, forced: forced, base: base(), vh: vh() }),
    _reset: () => { hw = false; kbNative = null; }
  };
})();
