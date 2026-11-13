// ログインボーナス（第4.168版・まさちゃん 2026/11/14 01:26「毎日ログインボーナスを作る！１週間単位
//   ・１日目、200P ・２日目、300P ・３日目、400P ・４日目、500P ・５日目、600P ・６日目、1000P ・７日目、1300P」）
//   ・その 日（端末の 日付）に はじめて アプリを 開いた とき、1回 だけ もらえる。アプリを 開いた まま 日付が かわった ときも（もどって きた とき・1分ごとに 見る）
//   ・7日で ひとまわり：もらう たびに 1日目 → 2日目 → … → 7日目 → また 1日目（1週間で 合わせて 4,300P）。
//     開かない 日が あっても つづきから（1日目に もどさない ※仮：「毎日」「1週間単位」と だけ 聞いた ので、休んでも 損を しない 方に した）
//   ・ポイントは 獲得ポイント（無償）：TengelWallet.grant('login-<年-月-日>', P, …)＝同じ 日付の id は 1回 だけ（財布が 二重に 入れない）。
//     上限（99,999P）を こえる ぶんは 財布が あずかる（ミッションの 窓で 補充）
//   ・何日目まで もらったか：localStorage 'tengel.login'（{ v:1, n: もらった 回数, last: さいごに もらった 日付 }）。なくなった とき（入れ直し・バックアップから もどした）は
//     財布の 台帳の login-… の 数と いちばん 新しい 日付から 作り直す
//   ・端末の 時計を もどしても もらえない（さいごに もらった 日付より あとの 日 だけ）
//   ・もらった とき：まん中に 小さな 窓（7日ぶんの 札・今日の 札に しるし・「OK」か 外を 押すと とじる）。アプリを 開いた ときの 画面（#gate）が 消えて から 出す
//   ・字は いまの 壁紙の 字（--font-body・--font-display：しぼった 字）→ ここの 画面の 言葉は その 字に 入って いる 字 だけで 書く（test_login.py が 確かめる）
//   ・テスト版（TENGEL_TEST=1）だけ：窓の 下に「つぎの 日を ためす」（日付を 1日 先に 進めた ことに して つぎの ボーナスを もらう：7日ぶんを すぐ 見られる）
//   App Store版 だけ（Web版には 入れない：build_pwa.py）
(function () {
  'use strict';
  if (!window.__NATIVE) return;
  var KEY = 'tengel.login', BONUS = [200, 300, 400, 500, 600, 1000, 1300], DAYS = BONUS.length, NAME = 'ログインボーナス';
  var busy = false, shown = null;
  function jget() { try { var v = JSON.parse(localStorage.getItem(KEY) || 'null'); return v && typeof v === 'object' ? v : null; } catch (e) { return null; } }
  function jset(v) { try { localStorage.setItem(KEY, JSON.stringify(v)); } catch (e) { /* なし */ } }
  function p2(n) { return (n < 10 ? '0' : '') + n; }
  function ymd(ms) { var d = new Date(ms); return d.getFullYear() + '-' + p2(d.getMonth() + 1) + '-' + p2(d.getDate()); }
  function comma(n) { return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
  function wallet() { return window.TengelWallet && window.TengelWallet.on ? window.TengelWallet : null; }
  // 財布の 台帳から（login-<年-月-日> の 数・いちばん 新しい 日付）
  function fromWallet() {
    var n = 0, last = '';
    try {
      (wallet().events() || []).forEach(function (e) { var m = /^login-(\d{4}-\d\d-\d\d)$/.exec(String((e && e.id) || '')); if (m) { n++; if (m[1] > last) last = m[1]; } });
    } catch (e) { /* なし */ }
    return { v: 1, n: n, last: last };
  }
  function state() {
    var s = jget(), w = fromWallet();
    if (!s || !(s.n >= 0)) s = { v: 1, n: w.n, last: w.last, off: 0 };
    if (w.last > String(s.last || '')) { s.last = w.last; s.n = Math.max(+s.n || 0, w.n); }      // 台帳の 方が 新しい（ほかの 端末の バックアップを もどした など）
    s.n = Math.max(0, Math.round(+s.n || 0)); s.last = String(s.last || ''); s.off = testOn() ? Math.max(0, Math.round(+s.off || 0)) : 0;
    return s;
  }
  function testOn() { return !!window.__TEST; }
  var today = function (s) { return ymd(Date.now() + (s.off || 0) * 86400000); };
  // その 日の ぶんを もらう（もう もらって いれば 何も しない）→ もらった 日（0〜6）か −1
  function check() {
    var w = wallet(); if (!w || busy) return Promise.resolve(-1);
    busy = true;
    return Promise.resolve(w.ready).then(function () {
      var s = state(), t = today(s);
      if (s.last && t <= s.last) return -1;                                  // 今日は もう もらった／時計が もどって いる
      var day = s.n % DAYS;
      return w.grant('login-' + t, BONUS[day], NAME + '（' + (day + 1) + '日目）').then(function (ok) {
        if (!ok) { var f = fromWallet(); if (f.last >= t) { s.last = f.last; s.n = Math.max(s.n, f.n); jset(s); } return -1; }      // 財布には もう 入って いた
        s.n += 1; s.last = t; jset(s);
        return day;
      });
    }).catch(function () { return -1; }).then(function (day) { busy = false; if (day >= 0) whenClear(function () { popup(day); }); return day; });
  }
  // アプリを 開いた ときの 画面（#gate：html.gateon）が 出て いる あいだは 待つ（2分 たっても 出て いたら 待たない）
  function whenClear(fn) {
    var tries = 0, go = function () { if (document.documentElement.classList.contains('gateon') && tries++ < 400) { setTimeout(go, 300); return; } fn(); };
    go();
  }
  function css() {
    if (document.getElementById('lgCss')) return;
    var st = document.createElement('style'); st.id = 'lgCss';
    st.textContent = '#lgOv{position:fixed;left:0;top:0;right:0;bottom:0;z-index:60;display:flex;align-items:center;justify-content:center;padding:calc(var(--sat,0px) + 16px) 16px calc(var(--sab,0px) + 16px);background:rgba(8,12,24,.56);-webkit-tap-highlight-color:transparent;animation:lgIn .18s ease-out both}'
      + '#lgOv .lgc{box-sizing:border-box;width:100%;max-width:348px;max-height:100%;overflow:auto;padding:18px 14px 14px;border-radius:18px;background:var(--surface,#fff);color:var(--ink,#1a2233);border:2px solid var(--lamp,#E2B33C);box-shadow:0 14px 40px rgba(0,0,0,.4);font-family:var(--font-body,sans-serif);text-align:center;animation:lgPop .26s cubic-bezier(.2,1.3,.4,1) both}'
      + '#lgOv .lgh{margin:0;font-family:var(--font-display,sans-serif);font-weight:400;font-size:22px;line-height:1.2;letter-spacing:.04em;color:var(--primary,#1E40AF)}'
      + '#lgOv .lgs{margin:8px 0 12px;font-size:14px;line-height:1.5}'
      + '#lgOv .lgs b{font-weight:700}#lgOv .lgs .lgp{display:inline-block;margin:0 2px;padding:1px 9px 2px;border-radius:999px;background:var(--night,#16203D);color:var(--lamp,#FFD45C);font-family:var(--font-mono,monospace);font-size:16px;font-weight:700;letter-spacing:.02em}'
      + '#lgOv .lgd{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px}'
      + '#lgOv .lgd li{position:relative;box-sizing:border-box;min-width:0;padding:7px 2px 6px;border-radius:11px;border:1px solid var(--line,#d5d9e2);background:var(--surface-2,#f4f6fa);line-height:1.2}'
      + '#lgOv .lgd li:nth-child(7){grid-column:span 2}'
      + '#lgOv .lgd .d{display:block;font-size:11px;font-weight:700;color:var(--muted,#667)}'
      + '#lgOv .lgd .p{display:block;margin-top:3px;font-family:var(--font-mono,monospace);font-size:14.5px;font-weight:700;letter-spacing:-.01em}'
      + '#lgOv .lgd li.got{border-color:var(--ok,#2E8B57);background:var(--ok-bg,#E6F5EC)}'
      + '#lgOv .lgd li.got .p{opacity:.62}'
      + '#lgOv .lgd li.now{border:2px solid var(--lamp,#E2B33C);padding:6px 1px 5px;background:var(--night,#16203D);color:var(--night-ink,#F3F0E6);box-shadow:0 0 0 3px rgba(226,179,60,.25);animation:lgNow .42s cubic-bezier(.2,1.5,.4,1) .2s both}'
      + '#lgOv .lgd li.now .d{color:var(--lamp,#FFD45C)}'
      + '#lgOv .lgd .ck{position:absolute;right:-4px;top:-5px;width:17px;height:17px;border-radius:50%;background:var(--ok,#2E8B57);box-shadow:0 0 0 2px var(--surface,#fff)}'
      + '#lgOv .lgd .ck::after{content:"";position:absolute;left:5.4px;top:2.6px;width:4px;height:8px;border:solid var(--surface,#fff);border-width:0 2.2px 2.2px 0;transform:rotate(45deg)}'
      + '#lgOv .lgd li.now .ck{background:var(--lamp,#E2B33C)}#lgOv .lgd li.now .ck::after{border-color:#1C1300}'
      + '#lgOv .lgn{margin:11px 0 0;font-size:11.5px;line-height:1.55;color:var(--muted,#667)}'
      + '#lgOv .lgb{display:block;width:100%;margin:12px 0 0;padding:12px;border-radius:12px;border:0;background:var(--primary,#1E40AF);color:var(--primary-ink,#fff);font-family:inherit;font-size:16px;font-weight:700;letter-spacing:.06em;cursor:pointer}'
      + '#lgOv .lgb:active{opacity:.8}'
      + '#lgOv .lgt{display:block;width:100%;margin:8px 0 0;padding:8px;border-radius:10px;border:1px dashed var(--line,#c9ced8);background:none;color:var(--muted,#667);font-family:inherit;font-size:12px;font-weight:700;cursor:pointer}'
      + '@keyframes lgIn{from{opacity:0}to{opacity:1}}@keyframes lgPop{from{opacity:0;transform:scale(.92)}to{opacity:1;transform:scale(1)}}@keyframes lgNow{from{transform:scale(1.22)}to{transform:scale(1)}}'
      + '@media (prefers-reduced-motion:reduce){#lgOv,#lgOv .lgc,#lgOv .lgd li.now{animation:none}}';
    document.head.appendChild(st);
  }
  function close() { var o = document.getElementById('lgOv'); if (o) o.remove(); shown = null; }
  // 窓：day＝今日 もらった 日（0〜6）
  function popup(day) {
    css(); close();
    var o = document.createElement('div'); o.id = 'lgOv'; o.setAttribute('role', 'dialog'); o.setAttribute('aria-modal', 'true'); o.setAttribute('aria-label', NAME);
    var li = '';
    for (var i = 0; i < DAYS; i++) {
      var cls = i < day ? 'got' : i === day ? 'now' : '';
      li += '<li' + (cls ? ' class="' + cls + '"' : '') + '><span class="d">' + (i + 1) + '日目</span><span class="p">' + comma(BONUS[i]) + 'P</span>' + (i <= day ? '<i class="ck" aria-hidden="true"></i>' : '') + '</li>';
    }
    o.innerHTML = '<div class="lgc"><h2 class="lgh">' + NAME + '</h2>'
      + '<p class="lgs"><b>' + (day + 1) + '日目</b> の ボーナス<span class="lgp">+' + comma(BONUS[day]) + 'P</span>を もらったよ</p>'
      + '<ol class="lgd">' + li + '</ol>'
      + '<p class="lgn">毎日、さいしょに ひらいた ときに 1回 もらえるよ。<br>7日目の つぎは、また 1日目から。</p>'
      + '<button type="button" class="lgb" data-lg="ok">OK</button>'
      + (testOn() ? '<button type="button" class="lgt" data-lg="next">テスト版：つぎの 日を ためす</button>' : '')
      + '</div>';
    o.addEventListener('click', function (e) {
      var b = e.target.closest ? e.target.closest('[data-lg]') : null;
      if (b && b.getAttribute('data-lg') === 'next') { e.preventDefault(); testNext(); return; }
      if (b || e.target === o) { e.preventDefault(); close(); }
    });
    document.body.appendChild(o); shown = day;
    try { document.dispatchEvent(new CustomEvent('tengel:login', { detail: { day: day, points: BONUS[day] } })); } catch (e) { /* なし */ }
  }
  // テスト版 だけ：日付を 1日 先に 進めた ことに して、つぎの 日の ぶんを もらう
  function testNext() {
    if (!testOn() || busy) return Promise.resolve(-1);
    var s = state(), t = ymd(Date.now() + s.off * 86400000);
    while (ymd(Date.now() + s.off * 86400000) <= (s.last > t ? s.last : t) && s.off < 4000) s.off += 1;
    jset(s);
    return check();
  }
  // 自動で 動かす ブラウザ（テストの 道具：navigator.webdriver）の 中では、自分からは 出さない（ほかの テストの 画面を 窓で ふさがない）。
  //   ログインボーナスの テスト（test_login.py）は window.__LOGIN_AUTO を 立てて、アプリと 同じ 動き（開いた とき・もどって きた とき）を ためす
  var auto = !(navigator.webdriver && !window.__LOGIN_AUTO);
  var boot = function () { whenClear(function () { setTimeout(check, 700); }); };
  if (auto) {
    if (document.readyState === 'complete') boot(); else window.addEventListener('load', boot, { once: true });
    document.addEventListener('visibilitychange', function () { if (!document.hidden) check(); });
    setInterval(function () { if (!document.hidden) check(); }, 60000);
  }
  window.TengelLogin = { BONUS: BONUS.slice(), check: check, state: state, close: close, shown: function () { return shown; }, next: testNext };
})();
