// 思い出フィギュアの 入口（App Store版だけ・index.html の 中に 入る 小さい 部分）：第4.134版（まさちゃん 2026/11/09）
//   ・記録タブの「思い出のレース」の 欄の ボタン（src.html の memTopHTML・memBtnsHTML）が TengelFig.booth()／make({ race }) を よぶ
//   ・第4.138版（11/10 09:45 まさちゃん「思い出フィギュアの、アイコンその下の青丸のところに入れて！ 両方タップしたら、それぞれのページに飛ぶように！」
//     09:55「思い出フィギュアのアイコンタップすると、フィギュアブースに飛んで！フィギュアブースからもフィギュアを作る、ができるようにして！」）：
//     どの タブでも 右上の トレーニングセンターの ボタンの 下に 丸い ボタン（#figFab・絵 fg_icon.webp＝まさちゃんの アイコン・下に 名前「思い出フィギュア」）→ 押すと フィギュアブース
//     （ブースの 下に「＋ フィギュアを作る」：fig_app.js の footBooth）。列と ボタンの 形は tc/tc_launch.js の TengelFab.add（index.html では tc_launch.js が 先）
//   ・押した ときに fig_bundle.js（3D の 描画・ブース・部屋・作る 画面）を 読む。形と 絵は build_ios.py が Resources/ に 入れる（リポジトリには 入れない）
(function () {
  'use strict';
  if (!window.__NATIVE) return;
  var loading = null, fab = null;
  function load() {
    if (window.FigApp) return Promise.resolve();
    if (!loading) loading = new Promise(function (ok, ng) { var s = document.createElement('script'); s.src = 'fig_bundle.js'; s.onload = function () { ok(); }; s.onerror = function () { loading = null; ng(new Error('load')); }; document.head.appendChild(s); });
    return loading;
  }
  function go(fn, opt) {
    if (fab) fab.disabled = true;
    return load().then(function () { return window.FigApp[fn](opt || {}); }).catch(function () { alert('思い出フィギュアを 読みこめなかったよ'); }).then(function (r) { if (fab) fab.disabled = false; return r; });
  }
  window.TengelFig = {
    booth: function (opt) { return go('booth', opt); },
    make: function (opt) { return go('make', opt); }
  };
  // ---------- 右上の 丸い ボタン（トレーニングセンターの 下・絵＋下に 名前「思い出フィギュア」）：列と ボタンの 形は tc/tc_launch.js の TengelFab（先に 読まれる）----------
  function boot() {
    if (document.getElementById('figFab') || !window.TengelFab) return;
    fab = window.TengelFab.add({ id: 'figFab', order: 2, name: ['思い出', 'フィギュア'], aria: '思い出フィギュア（押すと フィギュアブースを ひらくよ）', img: 'fg_icon.webp', fb: ['思い出', '#1B1F4A', '#E2B33C', '#FFE6A0'], tap: function () { window.TengelFig.booth(); } });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
