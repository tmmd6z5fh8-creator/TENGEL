// トレーニングセンターの 入口（App Store版だけ・index.html の 中に 入る 小さい 部分）
//   ・どの タブでも 右下（下の タブの すぐ 上）に 丸い ボタン（絵＋下に 名前の 札「トレーニング／センター」）→ 押すと tc_bundle.js を 読んで TCApp.open()
//     （11/09 13:04 まさちゃん「右下にうかぶ丸ボタン」→ 11/10 09:45「右上の赤丸の場所にして！」→ 11/10 11:32「アイコンが壁紙と重なってるから、右下に移動して！」
//       ・11/10 09:57「トレーニングセンターのアイコンこれにして！」「アイコンの下に、トレーニングセンター、思い出フィギュア、って壁紙に合う文字で」）
//     その 下に 思い出フィギュアの ボタン（fig/fig_launch.js が ここの TengelFab.add で 入れる：同じ 列 #fabCol・上から トレーニングセンター → 思い出フィギュア）
//   ・作戦会議の 通知（tengel.plan）：src.html の syncNotify が TCPlanNotify() を いっしょに 入れる（アプリの 中から 出す お知らせ）
//   ・作戦会議の 入口（第4.160版）：判定タブの「レース情報」の カードの 右上に 作戦会議の 札 → 押すと 判定タブの 上に 作戦会議を 開く（トレーニングセンターは 開かない）
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
    },
    // 第4.140版：使った チケットを 1枚 もどす（着せ替えで 解放できなかった とき）
    backTicket: function () {
      if (window.TCApp && window.TCApp.tickets && window.TCApp.tickets.back) return window.TCApp.tickets.back();
      var s = jget(TK); if (!s) return false; s.tickets = (s.tickets || 0) + 1; jset(TK, s); return true;
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
  // ---------- 右下の 丸い ボタンの 列（#fabCol）：上から トレーニングセンター（#tcFab）→ 思い出フィギュア（#figFab：fig/fig_launch.js が TengelFab.add で 入れる）----------
  //   ・場所：下の タブの すぐ 上・右はし（画面に 固定）。11/10 09:45「右上の赤丸の場所にして！」で 上の 帯の すぐ 下に した（第4.138版）が、
  //     判定タブで 壁紙の 上の絵に 重なる → 11:32「アイコンが壁紙と重なってるから、右下に移動して！」で 右下へ（第4.139版）
  //   ・ボタン＝丸い 絵（66px）＋ その 下の 名前の 札（.fabl・2行）。押せる のは 絵と 札だけ（まわりの すきまは 下の 画面に とどく）
  //   ・名前の 字（11/10 09:57 まさちゃん「壁紙に合う文字で」「文字の太さや字体は自然に馴染むように」）：
  //     字体＝いまの 壁紙（着せ替え）の 本文の 字（--font-body：どの 壁紙でも かな と「思い出」が 入って いる。見出しの 字 --font-display は しぼって あって 漢字が ない）・
  //     太さ＝下の タブの 名前と 同じ 700・札の 色＝上の 帯と 同じ（地 --night・字 --night-ink・ふちの 線 --lamp）：壁紙を かえると 帯と いっしょに かわる。
  //     字だけ（札なし）だと 下の カードの 字と 重なって 読みにくい（ためした）ので、上の 帯の 丸い 札（結果待ち・ミッション）と 同じ 見た目の 小さい 札に のせる
  //   ・名前は 2行（「トレーニング／センター」「思い出／フィギュア」）：1行だと 札が 絵より 左へ 30px ほど 出る（列の はばを 絵と 同じに して 画面の 中身に かぶる 所を へらす）
  //   ・列の 下に かくれた ままに ならない ように：
  //     ページの いちばん 下の 中身＝main の 下の 余白を 列の 高さの ぶん 広げる（clear：さいごまで スクロール すると 中身が 列の 上まで 上がる）・
  //     判定タブの 下の 帯（#minibar：判定の 要点・押すと 結果へ）が 出て いる あいだは 列を その 上へ 上げる（place：帯の 字を かくさない・帯が 消えると もどる）・
  //     買い目編集の「保存する」の 帯（.zsave.sticky：変更が ある あいだ 下に はりつく）は 右を ちぢめて 列の 手前で 終わる（--fabz）
  function fabCol() {
    var c = document.getElementById('fabCol'); if (c) return c;
    var st = document.createElement('style'); st.id = 'fabColCss';
    st.textContent = '#fabCol{position:fixed;right:4px;bottom:84px;z-index:29;display:flex;flex-direction:column;align-items:center;gap:4px;pointer-events:none;transition:bottom .18s ease}'
      + '@media (prefers-reduced-motion:reduce){#fabCol{transition:none}}'
      + '#fabCol>button{pointer-events:none;display:flex;flex-direction:column;align-items:center;border:0;padding:0;margin:0;background:none;color:inherit;-webkit-tap-highlight-color:transparent;transition:transform .15s}'
      + '#fabCol>button:active{transform:scale(.94)}#fabCol>button:disabled{opacity:.7}'
      + '#fabCol .fabi{pointer-events:auto;cursor:pointer;display:block;width:66px;height:66px;border-radius:50%;filter:drop-shadow(0 3px 5px rgba(0,0,0,.35))}'
      + '#fabCol .fabi img{width:100%;height:100%;display:block;pointer-events:none}'
      + '#fabCol .fabt{display:flex;align-items:center;justify-content:center;width:100%;height:100%;border-radius:50%;box-sizing:border-box;border:4px solid;font:400 12px/1.15 var(--font-display,sans-serif);text-align:center}'
      + '#fabCol .fabl{pointer-events:auto;cursor:pointer;position:relative;display:block;box-sizing:border-box;min-width:64px;margin-top:-7px;padding:2px 6px 2.5px;border-radius:9px;border:1px solid var(--lamp);background:var(--night);color:var(--night-ink);'
      + 'font-family:var(--font-body);font-weight:700;font-size:9.5px;line-height:11px;letter-spacing:-.01em;text-align:center;white-space:pre;box-shadow:0 1px 3px rgba(0,0,0,.25)}'
      + '.zsave.sticky{margin-right:var(--fabz,0px)}';
    document.head.appendChild(st);
    c = document.createElement('div'); c.id = 'fabCol'; document.body.appendChild(c);
    // 場所：下の タブの すぐ 上（タブが ない 画面は 画面の 下から）。判定タブの 下の 帯（#minibar）が 出て いる あいだは その 上
    var place = function () {
      var tb = document.querySelector('.tabbar'), r = tb ? tb.getBoundingClientRect() : null;
      var h = r && r.height && getComputedStyle(tb).display !== 'none' ? r.height : 0;
      var mb = document.getElementById('minibar'), q = mb && !mb.hidden ? mb.getBoundingClientRect() : null;
      var up = q && q.height ? Math.max(0, window.innerHeight - q.top - h) : 0;
      c._base = h ? h + 10 : null;                                                        // 帯が ない ときの 下からの 高さ（clear が 使う）
      c.style.bottom = 'calc(' + (h + up + (up ? 6 : 10)) + 'px + ' + (h ? '0px' : 'env(safe-area-inset-bottom)') + ')';
      clear();
    };
    place(); window.addEventListener('resize', place); setTimeout(place, 400); setTimeout(place, 1500);
    try { if (window.ResizeObserver) { var ro = new ResizeObserver(place), tb = document.querySelector('.tabbar'), mb = document.getElementById('minibar'); ro.observe(c); if (tb) ro.observe(tb); if (mb) ro.observe(mb); } } catch (e) { /* なし */ }
    try { var mb2 = document.getElementById('minibar'); if (mb2 && window.MutationObserver) new MutationObserver(place).observe(mb2, { attributes: true, attributeFilter: ['hidden', 'class', 'style'] }); } catch (e) { /* なし */ }
    return c;
  }
  // 列の 下に かくれた ままに ならない ように：main の 下の 余白（列の 高さの ぶん）・保存の 帯の 右の あき
  //   余白は 列が いつもの 場所（下の タブの すぐ 上）に ある ときの 高さで 数える（下の 帯で 上がって いる あいだも 同じ＝ページの 長さが 行ったり 来たり しない）
  var GAP = 6;
  function clear() {
    var c = document.getElementById('fabCol'); if (!c) return;
    var r = c.getBoundingClientRect(), root = document.documentElement, mn = document.querySelector('main'), vh = window.innerHeight, vw = root.clientWidth || window.innerWidth;
    var on = r.height > 0;
    var fz = on ? Math.max(0, Math.ceil(vw - 16 - 17 - r.left + GAP)) : 0;                      // 保存の 帯（カードの 中：右はし＝画面の 右から 16＋17）を ちぢめる はば
    if (root.style.getPropertyValue('--fabz') !== fz + 'px') root.style.setProperty('--fabz', fz + 'px');
    if (mn) { var pb = on ? Math.ceil((c._base != null ? c._base + r.height : vh - r.top) + GAP + 2) + 'px' : ''; if (mn.style.paddingBottom !== pb) mn.style.paddingBottom = pb; }
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
    fabCol().appendChild(b); clear();
    return b;
  }
  window.TengelFab = { add: fabAdd };
  var fab = null, loading = null;
  // 第4.140版：alert() は アプリの 中で 出ない → 画面の お知らせ（下の 黒い 札）
  function note(m) { try { var t = document.getElementById('toast'); if (t) { t.textContent = m; t.hidden = false; clearTimeout(t._tc); t._tc = setTimeout(function () { t.hidden = true; }, 4200); } } catch (e) { /* なし */ } }
  function load() {
    if (window.TCApp) return Promise.resolve();
    if (!loading) loading = new Promise(function (ok, ng) { var s = document.createElement('script'); s.src = 'tc_bundle.js'; s.onload = function () { ok(); }; s.onerror = function () { loading = null; ng(new Error('load')); }; document.head.appendChild(s); });
    return loading;
  }
  function open(opt) {
    if (fab) fab.disabled = true;
    return load().then(function () { return window.TCApp.open(opt); }).catch(function () { note('トレーニングセンターを 読みこめなかったよ。もう一度 押してね'); }).then(function () { if (fab) fab.disabled = false; });
  }
  window.TCOpen = open;
  // ---------- 作戦会議の 入口：判定タブの「レース情報」の カードの 右上（第4.160版・まさちゃん 11/12 14:58「作戦会議は、1番左の項目判定のページでも開けるようにして！アイコンは右上に設置して！」）----------
  //   ・絵は トレーニングセンターの 作戦会議の 札と 同じ（tc_icon_plan.webp：500×200 の 中に 札が 468×141）。絵の 大きさ 118×47 ＝ 見える 札 110×33・押せる 所は 絵 ぜんぶ（高さ 47）
  //   ・場所＝判定タブの いちばん 上の カード「レース情報」の 右上（見出しの まん中の 高さに 札の まん中・札の 右はしは カードの 中身の 右はし）。
  //     画面の 上の 帯の 右上は「説明書」「ミッション」で いっぱい。帯の すぐ 下に うかべると 壁紙の 上の絵に 重なる（11/10 11:32「アイコンが壁紙と重なってるから」）→ 重ならない カードの 中に 置く
  //     見出しの 字の 大きさは 壁紙で かわる ので、場所は 測って 決める（planPlace：壁紙を かえた とき・字が 読めた とき・画面の 大きさが かわった とき）
  //   ・押すと tc_bundle.js を 読んで TCPlan.open(#planHost)。#planHost＝画面 いっぱいの 入れ物（うしろは 判定タブの まま・「とじる」で そのまま 判定タブに もどる）
  //     入れ物は いつも 置いた まま（作戦会議が 閉じて いる 間は 何も 出ない・指も とどかない：pointer-events:none）。作戦会議の 幕は 自分で 指を 受ける
  //   ・開いて いる 間、うしろの 判定タブは 動かさない（幕や 見出しを なぞっても スクロール しない・中身が 短くて スクロール しない ときも）
  var PLAN_W = 118, PLAN_H = 47, PLAN_INK = [16 / 500, 30 / 200, 483 / 500, 170 / 200];      // 絵の 中の 札の 場所（左・上・右・下：割合）
  var planHost = null, planB = null;
  function planCss() {
    if (document.getElementById('planCss')) return;
    var st = document.createElement('style'); st.id = 'planCss';
    st.textContent = '#v-judge .card.planc{position:relative}'
      + '#planBtn{position:absolute;z-index:2;top:2px;right:12px;width:' + PLAN_W + 'px;height:' + PLAN_H + 'px;margin:0;padding:0;border:0;background:none;color:inherit;-webkit-tap-highlight-color:transparent;cursor:pointer;transition:transform .15s}'
      + '#planBtn:active{transform:scale(.95)}#planBtn:disabled{opacity:.7}'
      + '@media (prefers-reduced-motion:reduce){#planBtn{transition:none}}'
      + '#planBtn img{display:block;width:100%;height:100%;pointer-events:none;filter:drop-shadow(0 1px 2px rgba(0,0,0,.28))}'
      + '#planBtn .plt{display:flex;align-items:center;justify-content:center;box-sizing:border-box;width:110px;height:33px;margin:7px 4px;border-radius:5px;border:3px solid #c0241c;background:#f6ead0;color:#b8201a;font:700 15px/1 "BIZ UDPGothic","Hiragino Sans",sans-serif;letter-spacing:.06em;pointer-events:none}'
      + '#planHost{position:fixed;left:0;top:0;right:0;bottom:0;z-index:90;pointer-events:none}'
      + '#planHost>#tcPlan{pointer-events:auto;touch-action:none}'
      + '#planHost .pb{overscroll-behavior:contain}';
    document.head.appendChild(st);
  }
  // 札の 場所：見出しの まん中の 高さ・カードの 中身の 右はし。下の 行（データの 切りかえ）に かからない ように 上へ よせる（カードの 上の ふちからは 出さない）
  function planPlace() {
    var b = planB; if (!b || !b.parentNode) return;
    var card = b.parentNode, h = card.querySelector('h2'); if (!h) return;
    var cr = card.getBoundingClientRect(), hr = h.getBoundingClientRect(); if (!cr.width || !hr.height) return;      // 判定タブが 出て いない
    var cs = getComputedStyle(card), bt = parseFloat(cs.borderTopWidth) || 0, pr = parseFloat(cs.paddingRight) || 0, pt = parseFloat(cs.paddingTop) || 0;
    var inkT = PLAN_INK[1] * PLAN_H, inkB = PLAN_INK[3] * PLAN_H, inkR = (1 - PLAN_INK[2]) * PLAN_W;
    var top = hr.top + hr.height / 2 - (cr.top + bt) - PLAN_H / 2;
    var nx = h.nextElementSibling;
    while (nx && !(nx.getBoundingClientRect().height > 0)) nx = nx.nextElementSibling;                       // 見出しの 次の 見えて いる 行
    if (nx) top = Math.min(top, nx.getBoundingClientRect().top - (cr.top + bt) - 3 - inkB);                   // 札の 下が 次の 行の 3px 上まで
    top = Math.max(top, Math.min(pt, 6) - inkT);                                                             // 札の 上が カードの 上の ふちから 6px（余白が せまい ときは 余白の ぶん）より 下
    var t = Math.round(top) + 'px', r = Math.round(Math.max(0, pr - inkR)) + 'px';
    if (b.style.top !== t) b.style.top = t;
    if (b.style.right !== r) b.style.right = r;
  }
  function planOpen() {
    if (planB) planB.disabled = true;
    return load().then(function () {
      planCss();
      if (!planHost) {
        planHost = document.createElement('div'); planHost.id = 'planHost'; document.body.appendChild(planHost);
        planHost.addEventListener('touchmove', function (e) {      // うしろの ページを 動かさない：スクロール できる 中身（.pb）の 中 だけ 指で 動かせる
          var t = e.target, pb = t && t.closest ? t.closest('.pb') : null;
          if (!pb || pb.scrollHeight <= pb.clientHeight + 1) { if (e.cancelable) e.preventDefault(); }
        }, { passive: false });
      }
      return window.TCPlan.open(planHost);
    }).catch(function () { note('作戦会議を 読みこめなかったよ。もう一度 押してね'); }).then(function () { if (planB) planB.disabled = false; });
  }
  window.TCPlanOpen = planOpen;
  function planBoot() {
    if (document.getElementById('planBtn')) return;
    var card = document.querySelector('#v-judge .card'), h = card && card.querySelector('h2'); if (!card || !h) return;
    planCss(); card.classList.add('planc');
    var b = document.createElement('button'); b.type = 'button'; b.id = 'planBtn'; b.setAttribute('aria-label', '作戦会議（押すと ひらくよ）');
    var im = new Image(); im.alt = '';
    im.onerror = function () { var t = document.createElement('span'); t.className = 'plt'; t.textContent = '作戦会議'; im.replaceWith(t); };      // 絵が ない（CI など）：字の 札
    im.src = 'tc_icon_plan.webp'; b.appendChild(im);
    b.addEventListener('click', function () { if (!b.disabled) planOpen(); });
    card.appendChild(b); planB = b;
    planPlace(); window.addEventListener('resize', planPlace); setTimeout(planPlace, 400); setTimeout(planPlace, 1500);
    try { if (window.ResizeObserver) { var ro = new ResizeObserver(planPlace); ro.observe(card); ro.observe(h); } } catch (e) { /* なし */ }
    try { if (document.fonts && document.fonts.ready) document.fonts.ready.then(planPlace); } catch (e) { /* なし */ }
  }
  function boot() {
    if (document.getElementById('tcFab')) return;
    fab = fabAdd({ id: 'tcFab', order: 1, name: ['トレーニング', 'センター'], aria: 'トレーニングセンター（押すと ひらくよ）', img: 'tc_icon_tc.webp', fb: ['トレセン', '#1F5A2E', '#E2B33C', '#FFF3C4'], tap: function () { open(); } });
    planBoot();
  }
  // 通知を 押した（作戦会議）→ トレーニングセンターの 作戦会議を 開く
  document.addEventListener('tengel:native', function (e) {
    var d = e.detail || {}; if (d.name === 'notify' && d.payload && /^plan-/.test(String(d.payload.id || ''))) open({ plan: true });
  });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
