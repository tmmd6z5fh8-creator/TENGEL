// トレーニングセンターの 入口（App Store版だけ・index.html の 中に 入る 小さい 部分）
//   ・どの タブでも 右下（下の タブの 上）に 丸い ボタン（11/09 13:04 まさちゃん「右下にうかぶ丸ボタン」）→ 押すと tc_bundle.js を 読んで TCApp.open()
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
  // ---------- 右下の 丸い ボタン ----------
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
  function place() {
    if (!fab) return; var tb = document.querySelector('.tabbar'), r = tb ? tb.getBoundingClientRect() : null;
    var h = r && r.height && getComputedStyle(tb).display !== 'none' ? r.height : 0;
    fab.style.bottom = 'calc(' + (h + 10) + 'px + ' + (h ? '0px' : 'env(safe-area-inset-bottom)') + ')';
  }
  function boot() {
    if (document.getElementById('tcFab')) return;
    var st = document.createElement('style'); st.id = 'tcFabCss';
    st.textContent = '#tcFab{position:fixed;right:12px;bottom:84px;z-index:29;width:68px;height:68px;border:0;padding:0;margin:0;border-radius:50%;background:transparent;-webkit-tap-highlight-color:transparent;filter:drop-shadow(0 3px 5px rgba(0,0,0,.35));transition:transform .15s}'
      + '#tcFab:active{transform:scale(.93)}#tcFab:disabled{opacity:.7}#tcFab img{width:100%;height:100%;display:block;pointer-events:none}';
    document.head.appendChild(st);
    fab = document.createElement('button'); fab.type = 'button'; fab.id = 'tcFab'; fab.setAttribute('aria-label', 'トレーニングセンター（押すと ひらくよ）');
    fab.innerHTML = '<img src="tc_icon_tc.webp" alt="">';
    fab.addEventListener('click', function () { open(); });
    document.body.appendChild(fab); place();
    window.addEventListener('resize', place); setTimeout(place, 400); setTimeout(place, 1500);
  }
  // 通知を 押した（作戦会議）→ トレーニングセンターの 作戦会議を 開く
  document.addEventListener('tengel:native', function (e) {
    var d = e.detail || {}; if (d.name === 'notify' && d.payload && /^plan-/.test(String(d.payload.id || ''))) open({ plan: true });
  });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
