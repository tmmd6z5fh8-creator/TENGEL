// トレーニングセンターの 入口（App Store版だけ・index.html の 中に 入る 小さい 部分）
//   ・どの タブでも 右上（上の 帯 header.top の すぐ 下）に 丸い ボタン（絵＋下に 名前の 札「トレーニング／センター」）→ 押すと tc_bundle.js を 読んで TCApp.open()
//     （11/09 13:04 まさちゃん「右下にうかぶ丸ボタン」→ 11/10 09:45「トレーニングセンターのアイコン、一枚目の右上の赤丸の場所にして！」
//       → 11/10 09:57「トレーニングセンターのアイコンこれにして！」「アイコンの下に、トレーニングセンター、思い出フィギュア、って壁紙に合う文字で」）
//     その 下に 思い出フィギュアの ボタン（fig/fig_launch.js が ここの TengelFab.add で 入れる：同じ 列 #fabCol・上から トレーニングセンター → 思い出フィギュア）
//   ・作戦会議の 通知（tengel.plan）：src.html の syncNotify が TCPlanNotify() を いっしょに 入れる（アプリの 中から 出す お知らせ）
//   ・お世話の 合計（ミッション）・チケット（着せ替え）：バンドルを 読む 前でも TCInfo で 読める
(function () {
  'use strict';
  if (!window.__NATIVE) return;
  var TK = 'tengel.tc', PK = 'tengel.plan';
  function jget(k) { try { return JSON.parse(localStorage.getItem(k) || 'null'); } catch (e) { return null; } }
  function jset(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* なし */ } }
  var live = function () { return window.TCApp && window.TCApp.state ? window.TCApp.state : null; };
  window.TCInfo = {
    total: function () { var s = live() || jget(TK); return (s && s.total) || 0; },
    tickets: function () { var s = live() || jget(TK); return (s && s.tickets) || 0; },
    useTicket: function () {
      if (window.TCApp && window.TCApp.tickets) return window.TCApp.tickets.use();
      var s = jget(TK); if (!s || !(s.tickets > 0)) return false; s.tickets -= 1; jset(TK, s); return true;
    }
  };
  // ---------- 作戦会議の 通知（発走の 20・15・10・8・5分前：選んだ もの だけ）----------
  window.TCPlanNotify = function () {
    var P = jget(PK); if (!P || !P.on || !Array.isArray(P.races)) return [];
    var now = Date.now(), out = [];
    P.races.forEach(function (r) {
      if (!r || !/^\d{4}-\d{2}-\d{2}$/.test(r.date || '') || !/^\d{1,2}:\d{2}$/.test(r.time || '')) return;
      var d = r.date.split('-'), hm = r.time.split(':');
      var at0 = new Date(+d[0], +d[1] - 1, +d[2], +hm[0], +hm[1], 0).getTime();
      (r.notify || []).forEach(function (m) {
        var at = at0 - m * 60000; if (at <= now + 5000) return;
        out.push({ id: 'plan-' + r.id + '-' + m, at: at, title: 'まもなく発走！', body: (r.name || 'レース') + '　' + r.time + ' 発走（あと' + m + '分）', race: '' });
      });
    });
    return out;
  };
  // ---------- 右上の 丸い ボタンの 列（#fabCol）：上から トレーニングセンター（#tcFab）→ 思い出フィギュア（#figFab：fig/fig_launch.js が TengelFab.add で 入れる）----------
  //   ・ボタン＝丸い 絵（66px）＋ その 下の 名前の 札（.fabl・2行）。押せる のは 絵と 札だけ（まわりの すきまは 下の 画面に とどく）
  //   ・名前の 字（11/10 09:57 まさちゃん「壁紙に合う文字で」「文字の太さや字体は自然に馴染むように」）：
  //     字体＝いまの 壁紙（着せ替え）の 本文の 字（--font-body：どの 壁紙でも かな と「思い出」が 入って いる。見出しの 字 --font-display は しぼって あって 漢字が ない）・
  //     太さ＝下の タブの 名前と 同じ 700・札の 色＝上の 帯と 同じ（地 --night・字 --night-ink・ふちの 線 --lamp）：壁紙を かえると 帯と いっしょに かわる。
  //     字だけ（札なし）だと 下の カードの 字と 重なって 読みにくい（ためした）ので、上の 帯の 丸い 札（結果待ち・ミッション）と 同じ 見た目の 小さい 札に のせる
  //   ・名前は 2行（「トレーニング／センター」「思い出／フィギュア」）：1行だと 札が 絵より 左へ 30px ほど 出て、判定タブの データの 札（マザーデータ①）に かぶる（ためした）
  function fabCol() {
    var c = document.getElementById('fabCol'); if (c) return c;
    var st = document.createElement('style'); st.id = 'fabColCss';
    st.textContent = '#fabCol{position:fixed;right:4px;top:150px;z-index:29;display:flex;flex-direction:column;align-items:center;gap:4px;pointer-events:none}'
      + '#fabCol>button{pointer-events:none;display:flex;flex-direction:column;align-items:center;border:0;padding:0;margin:0;background:none;color:inherit;-webkit-tap-highlight-color:transparent;transition:transform .15s}'
      + '#fabCol>button:active{transform:scale(.94)}#fabCol>button:disabled{opacity:.7}'
      + '#fabCol .fabi{pointer-events:auto;cursor:pointer;display:block;width:66px;height:66px;border-radius:50%;filter:drop-shadow(0 3px 5px rgba(0,0,0,.35))}'
      + '#fabCol .fabi img{width:100%;height:100%;display:block;pointer-events:none}'
      + '#fabCol .fabt{display:flex;align-items:center;justify-content:center;width:100%;height:100%;border-radius:50%;box-sizing:border-box;border:4px solid;font:400 12px/1.15 var(--font-display,sans-serif);text-align:center}'
      + '#fabCol .fabl{pointer-events:auto;cursor:pointer;position:relative;display:block;box-sizing:border-box;min-width:64px;margin-top:-7px;padding:2px 6px 2.5px;border-radius:9px;border:1px solid var(--lamp);background:var(--night);color:var(--night-ink);'
      + 'font-family:var(--font-body);font-weight:700;font-size:9.5px;line-height:11px;letter-spacing:-.01em;text-align:center;white-space:pre;box-shadow:0 1px 3px rgba(0,0,0,.25)}'
      + '.fabsp{display:block;float:right;width:0;height:0;pointer-events:none}#w5Banner>.w5banner{padding-right:calc(14px + var(--fabbw,0px))}';
    document.head.appendChild(st);
    c = document.createElement('div'); c.id = 'fabCol'; document.body.appendChild(c);
    var place = function () {   // 上の 帯（sticky：いつも 同じ 所）の すぐ 下。帯が ない 画面は 画面の 上から
      var h = document.querySelector('header.top'), r = h ? h.getBoundingClientRect() : null;
      var b = r && r.height && getComputedStyle(h).display !== 'none' ? r.bottom : 0;
      c.style.top = b > 0 ? Math.round(b + 6) + 'px' : 'calc(env(safe-area-inset-top) + 10px)';
    };
    var both = function () { place(); dodge(); };
    both(); window.addEventListener('resize', both); setTimeout(both, 400); setTimeout(both, 1500);
    try { var hd = document.querySelector('header.top'); if (hd && window.ResizeObserver) new ResizeObserver(both).observe(hd); } catch (e) { /* なし */ }
    // 中身が かわった（カードを 書き直した・足した）・高さが かわった（壁紙の 上の絵・帯）・タブを かえた・壁紙を かえた → よけ直す
    var mn = document.querySelector('main');
    try { if (mn && window.MutationObserver) new MutationObserver(later).observe(mn, { childList: true, subtree: true }); } catch (e) { /* なし */ }
    try { if (window.ResizeObserver) { var ro = new ResizeObserver(later); ro.observe(c); if (mn) ro.observe(mn); } } catch (e) { /* なし */ }
    document.addEventListener('tengel:tab', dodge); document.addEventListener('tengel:kisekae', later);
    return c;
  }
  // ---------- ページの いちばん 上の 中身を ボタンの 列から よける ----------
  //   列は 画面に 固定（上の 帯の すぐ 下・右はし）。ページを いちばん 上まで もどした とき その 下に 来る 中身（記録タブの「6月」・設定の ポイントの 数・説明の 文の 右はし…）は、
  //   それより 下へ 動かせない ので ずっと かくれた ままに なる（下へ スクロール すると 上の 帯の 下へ 入る）。
  //   → 見えて いる タブの いちばん 上の カードの すぐ 前に、右に 寄せた すきま（.fabsp：float）を 置く。カードの 中の 字・ボタンの 行が 列を よけて ならぶ
  //     （カードの 地は そのまま 列の 下まで）。大きさ＝いちばん 上まで もどした ときに 列が かぶる 所（列の 左から 右・列の 下まで・すきま 6px）。
  //     壁紙の 上の絵（判定タブ）が ある ときは カードが 列より 下に なる ので 0（上の絵は 列の 下に そのまま）。
  //   ・単勝5連勝の レースを 判定タブで 入れて いる ときの 帯（#w5Banner：いちばん 上・右に「戻る」ボタン）は 右の 余白を 広げる（--fabbw）
  //   ・カードを 書き直すと すきまも 消える → main の 中身が かわるたびに 1コマに 1回 たしかめる（later）
  var GAP = 6, sps = {}, raf = 0;
  function later() { if (!raf) raf = requestAnimationFrame(dodge); }
  function px(el, k, v) { v = v + 'px'; if (el.style[k] !== v) el.style[k] = v; }
  function dodge() {
    if (raf) { cancelAnimationFrame(raf); raf = 0; }
    var c = document.getElementById('fabCol'); if (!c) return;
    var cr = c.getBoundingClientRect(), vs = document.querySelectorAll('main > .view'), sy = window.pageYOffset || 0, i, k;
    for (i = 0; i < vs.length; i++) {
      var v = vs[i]; if (v.hidden || !v.offsetParent) continue;
      var cards = v.querySelectorAll('.card'), card = null, sp = sps[v.id];
      for (k = 0; k < cards.length; k++) if (cards[k].offsetParent && !cards[k].closest('#ksBnr')) { card = cards[k]; break; }   // 壁紙の 上の絵の 中は 見ない
      if (!card || !cr.height || !/^(block|flow-root)$/.test(getComputedStyle(card.parentNode).display)) { if (sp && sp.parentNode) sp.parentNode.removeChild(sp); }
      else {
        if (!sp) { sp = sps[v.id] = document.createElement('i'); sp.className = 'fabsp'; sp.setAttribute('aria-hidden', 'true'); }
        var at = card, q;   // すぐ 前に かくれた カードが ならんで いたら その 前に（「.card+.card」の 上の すきまを かえない ため）
        while ((q = at.previousElementSibling) && q !== sp && !q.offsetParent && q.classList.contains('card')) at = q;
        if (at.previousSibling !== sp) card.parentNode.insertBefore(sp, at);
        var all = v.querySelectorAll('.fabsp');   // 書き直しで 写し（innerHTML の 読み書き）が できて いたら 消す（すきまは 1つ）
        for (k = 0; k < all.length; k++) if (all[k] !== sp) all[k].parentNode.removeChild(all[k]);
        var r = sp.getBoundingClientRect(), w = Math.ceil(r.right - cr.left + GAP), h = Math.ceil(cr.bottom + GAP - (r.top + sy));
        if (w <= 0 || h <= 0) w = h = 0;
        px(sp, 'width', w); px(sp, 'height', h);
      }
      var bn = document.getElementById('w5Banner');
      if (bn && v.contains(bn)) {
        var br = bn.getBoundingClientRect(), bw = !bn.hidden && br.height && cr.height && br.top + sy < cr.bottom + GAP ? Math.max(0, Math.ceil(br.right - 15 - cr.left + GAP)) : 0;
        if (bn.style.getPropertyValue('--fabbw') !== bw + 'px') bn.style.setProperty('--fabbw', bw + 'px');
      }
    }
  }
  // ボタンを 1つ 足す：o＝{ id, order（上からの 順）, name（下に 出す 名前：行ごと）, aria, img（絵）, fb（絵が ない ときの 丸：[字, 地, ふち, 字の 色]）, tap }
  function fabAdd(o) {
    var old = document.getElementById(o.id); if (old) return old;
    var b = document.createElement('button'); b.type = 'button'; b.id = o.id; b.style.order = String(o.order || 0); b.setAttribute('aria-label', o.aria || o.name.join(''));
    var i = document.createElement('span'); i.className = 'fabi';
    var im = new Image(); im.alt = '';
    im.onerror = function () {   // 絵が ない（CI など）：字の 丸
      var t = document.createElement('span'); t.className = 'fabt'; t.style.cssText = 'background:' + o.fb[1] + ';border-color:' + o.fb[2] + ';color:' + o.fb[3]; t.textContent = o.fb[0]; im.replaceWith(t);
    };
    im.src = o.img; i.appendChild(im); b.appendChild(i);
    var l = document.createElement('span'); l.className = 'fabl'; l.textContent = o.name.join('\n'); b.appendChild(l);
    b.addEventListener('click', function () { if (!b.disabled) o.tap(); });
    fabCol().appendChild(b); dodge();
    return b;
  }
  window.TengelFab = { add: fabAdd };
  var fab = null, loading = null;
  function load() {
    if (window.TCApp) return Promise.resolve();
    if (!loading) loading = new Promise(function (ok, ng) { var s = document.createElement('script'); s.src = 'tc_bundle.js'; s.onload = function () { ok(); }; s.onerror = function () { loading = null; ng(new Error('load')); }; document.head.appendChild(s); });
    return loading;
  }
  function open(opt) {
    if (fab) fab.disabled = true;
    return load().then(function () { return window.TCApp.open(opt); }).catch(function () { alert('トレーニングセンターを 読みこめなかったよ'); }).then(function () { if (fab) fab.disabled = false; });
  }
  window.TCOpen = open;
  function boot() {
    if (document.getElementById('tcFab')) return;
    fab = fabAdd({ id: 'tcFab', order: 1, name: ['トレーニング', 'センター'], aria: 'トレーニングセンター（押すと ひらくよ）', img: 'tc_icon_tc.webp', fb: ['トレセン', '#1F5A2E', '#E2B33C', '#FFF3C4'], tap: function () { open(); } });
  }
  // 通知を 押した（作戦会議）→ トレーニングセンターの 作戦会議を 開く
  document.addEventListener('tengel:native', function (e) {
    var d = e.detail || {}; if (d.name === 'notify' && d.payload && /^plan-/.test(String(d.payload.id || ''))) open({ plan: true });
  });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
