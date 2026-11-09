// 思い出フィギュアの 入口（App Store版だけ・index.html の 中に 入る 小さい 部分）：第4.134版（まさちゃん 2026/11/09）
//   ・記録タブの「思い出のレース」の 欄の ボタン（src.html の memTopHTML・memBtnsHTML）が TengelFig.booth()／make({ race }) を よぶ
//   ・押した ときに fig_bundle.js（3D の 描画・ブース・部屋・作る 画面）を 読む。形と 絵は build_ios.py が Resources/ に 入れる（リポジトリには 入れない）
(function () {
  'use strict';
  if (!window.__NATIVE) return;
  var loading = null;
  function load() {
    if (window.FigApp) return Promise.resolve();
    if (!loading) loading = new Promise(function (ok, ng) { var s = document.createElement('script'); s.src = 'fig_bundle.js'; s.onload = function () { ok(); }; s.onerror = function () { loading = null; ng(new Error('load')); }; document.head.appendChild(s); });
    return loading;
  }
  function go(fn, opt) {
    return load().then(function () { return window.FigApp[fn](opt || {}); }).catch(function () { alert('思い出フィギュアを 読みこめなかったよ'); });
  }
  window.TengelFig = {
    booth: function (opt) { return go('booth', opt); },
    make: function (opt) { return go('make', opt); }
  };
})();
