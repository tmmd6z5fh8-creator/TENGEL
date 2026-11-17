// 時計の 番人（第4.191版・まさちゃん 2026/11/17 21:23「お願い！」
//   ＝ 21:11「アプリ内のポイントとか、バトルコインとか不正に受け取ることできないようになってる？」で 見つけた 抜け道 1〜3 を ふさぐ）
//   iPhone の 時計（設定で 日付を かえられる）を そのまま 信じない。アプリ（Clock.swift：お願い「clock」）が わたす、設定では かえられない 時計
//   （電源を 入れてからの 時間 mono・電源を 入れる たびに かわる 番号 boot・アプリを 開く たびに かわる 番号 proc・端末の 番号 dev）と くらべて、
//   本当の 時刻を 見つもる → TengelClock.now()（ミリ秒）。ログインボーナスの 日（login_bonus.js）・カードバトルの ミッションの 月（cb/cb_app.js）・
//   ポイントの 期限と できごとの 時刻（points_ui.js）が 使う
//   ・同じ 起動の 中（電源を 入れ直して いない）：本当の 時刻 ＝ 基準の 時刻 ＋ その あとに 進んだ 電源の 時間。
//     iPhone の 時計が それと 10分 より ずれて いたら（日付を 先に 進めた・もどした）、本当の 時刻の 方を 使う（'ahead'／'back'）
//   ・電源を 入れ直した（boot が かわった・mono が へった）：その あいだの 時間は わからない ので、iPhone の 時計を 信じる（'boot'）。
//     ただし「前に 見た 時刻 ＋ 電源を 入れてからの 時間」より 前には しない（'boot-back'：あとで 時計が 直ったら 1回 だけ 信じる 'fix'）
//   ・boot が 読めない（iOS が 見せて くれない）ときに アプリを 閉じて 開き直した あとは「入れ直したかも」：
//     進んだ 分が「前に 見た ときの 電源を 入れてからの 時間」より 小さい ＝ 入れ直しでは ありえない → 進めた（'ahead'）。
//     それ 以外（入れ直した すぐ あと）は 信じる（'maybe'：まじめな 人を こまらせない）
//   ・いちど 出した いちばん 新しい 時刻（hi）より 前には もどらない（期限を もどして 使う・ミッションの 月を もどす・ログインボーナスの 日を もどす が できない）
//   ・べつの 端末（バックアップを べつの 端末に もどした）：はじめから（その 端末の 時計を 信じる 'first'）
//   ・小さな ずれ（10分 まで）は iPhone の 時計に 合わせる。基準は 1日 ごとに 合わせ直す（ずれが 1日 9秒 まで の とき だけ：時計の 石の 小さな ずれを ためない・
//     少しずつ 進めても 10分 より 先には 行かない）
//   ・ほかの 画面は 同期の 呼び出し（now）で 使う：さいごに たしかめた ときからの ページの 時計（performance.now）で 進める。
//     その あいだに iPhone の 時計が とんだ ときは、つぎに たしかめる まで ページの 時計で（アプリに もどって きた とき・1分 ごとに たしかめる）
//   ・ほうびを 決める ところ（ログインボーナス）は sync() で たしかめて から
//   ・おぼえる：localStorage 'tengel.clock'（{ v:1, dev, boot, proc, mono, t, tB, mB, hi, u }）。どこにも 送らない
//   ・アプリが 時計を わたさない（テストの にせもの・前の 版の アプリ）ときは、iPhone の 時計の まま（Date.now）
//   App Store版 だけ（Web版には 入れない：build_pwa.py）
(function () {
  'use strict';
  if (!window.__NATIVE) return;
  var KEY = 'tengel.clock', TOL = 10 * 60000, DAY = 86400000, JUMP = 2000;
  var S = null, L = null, busy = null, how = '', first = null, top = 0;      // top：この ページで 出した いちばん 新しい 時刻（さがらない）
  function fin(x) { return typeof x === 'number' && isFinite(x); }
  function str(x) { return typeof x === 'string' ? x.slice(0, 80) : ''; }
  function good(v) { return !!v && typeof v === 'object' && v.v === 1 && fin(v.mono) && v.mono >= 0 && fin(v.t) && fin(v.tB) && fin(v.mB) && fin(v.hi); }
  function load() {
    try {
      var v = JSON.parse(localStorage.getItem(KEY) || 'null'); if (!good(v)) return null;
      return { v: 1, dev: str(v.dev), boot: str(v.boot), proc: str(v.proc), mono: v.mono, t: v.t, tB: v.tB, mB: v.mB, hi: v.hi, u: v.u ? 1 : 0 };
    } catch (e) { return null; }
  }
  function keep(v) { try { localStorage.setItem(KEY, JSON.stringify(v)); } catch (e) { /* おぼえられない：つぎは はじめから */ } }
  // アプリから とどいた 時計（おかしい ときは null）
  function sample(c) {
    if (!c || typeof c !== 'object' || !fin(c.wall) || !fin(c.mono) || c.mono < 0 || c.wall <= 0) return null;
    return { wall: c.wall, mono: c.mono, boot: str(c.boot), proc: str(c.proc), dev: str(c.dev) };
  }
  // 本当の 時刻を 見つもる（P＝前の 状態〈なければ null〉・c＝いまの 時計）→ { s：新しい 状態, how }
  function judge(P, c) {
    if (!P || (P.dev && c.dev && P.dev !== c.dev)) return { s: { v: 1, dev: c.dev, boot: c.boot, proc: c.proc, mono: c.mono, t: c.wall, tB: c.wall, mB: c.mono, hi: c.wall, u: 0 }, how: 'first', est: c.wall };
    // 同じ 起動？ true＝同じ・false＝入れ直した・null＝わからない（boot が 読めない・アプリを 開き直した）
    var same = P.boot && c.boot ? P.boot === c.boot : (P.proc && c.proc && P.proc === c.proc) ? true : c.mono < P.mono - 1000 ? false : null;
    if (same === true && c.mono < P.mono - 1000) same = false;      // 電源を 入れてからの 時間が へった ＝ 入れ直した
    var s = { v: 1, dev: c.dev || P.dev, boot: c.boot, proc: c.proc, mono: c.mono, t: 0, tB: P.tB, mB: P.mB, hi: P.hi, u: P.u ? 1 : 0 }, t, h;
    if (same === false) {
      var lo = P.t + c.mono;      // 入れ直したのは 前に 見た あと → いまは 少なくとも「前に 見た 時刻 ＋ 電源を 入れてからの 時間」
      if (c.wall >= lo - TOL) { t = c.wall; s.u = 0; h = 'boot'; } else { t = lo; s.u = 1; h = 'boot-back'; }
      s.tB = t; s.mB = c.mono;
    } else {
      var pred = P.tB + (c.mono - P.mB), d = c.wall - pred;      // 同じ 起動 なら：本当の 時刻 ＝ 基準 ＋ 進んだ 電源の 時間
      if (Math.abs(d) <= TOL) {
        t = c.wall; s.u = 0; h = 'ok';
        if (c.mono - P.mB >= DAY && Math.abs(d) <= Math.max(2000, (c.mono - P.mB) * 1e-4)) { s.tB = c.wall; s.mB = c.mono; }      // 1日 ごとに 合わせ直す（ずれが 1日 9秒 まで の とき だけ：時計の 石の ずれ）
      } else if (d < 0) { t = pred; h = 'back'; }                                                  // 時計を もどした
      else if (P.u) { t = c.wall; s.u = 0; s.tB = c.wall; s.mB = c.mono; h = 'fix'; }              // 入れ直した すぐ あとに おくれて いた 時計が 直った（1回 だけ）
      else if (same === true || d < P.mono - 2 * TOL) { t = pred; h = 'ahead'; }                  // 時計を 先に 進めた（入れ直しでは ありえない）
      else { t = c.wall; s.tB = c.wall; s.mB = c.mono; h = 'maybe'; }                              // 入れ直したかも（わからない）：信じる
    }
    s.t = Math.max(t, P.hi); s.hi = s.t;
    return { s: s, how: h, est: t };      // est：見つもった 時刻（hi で 持ち上げる 前：ページの 時計は これで 進めて、hi の 前は 止まって 待つ）
  }
  function pnow() { try { return performance.now(); } catch (e) { return Date.now(); } }
  // いまの 本当の 時刻（同期）
  function now() {
    var w = Date.now();
    if (!S) return w;
    if (!L) return Math.max(w, S.hi);      // この ページで まだ たしかめて いない（開いた すぐ あと）：iPhone の 時計（前に 出した 時刻より 前には しない）。おぼえない（top に しない）
    var dp = pnow() - L.p, dw = w - L.w, t = Math.abs(dw - dp) <= JUMP ? w + L.off : L.t + Math.max(0, dp);      // iPhone の 時計が とんだ（2秒 より）：つぎに たしかめる まで ページの 時計で
    t = Math.max(t, S.hi, top); top = t;
    return t;
  }
  // 出した いちばん 新しい 時刻を おぼえる（アプリが うしろに 回った とき・たしかめる 前）：つぎに 開いた ときも それより 前に しない
  function keepTop() { if (S && top > S.hi) { S.hi = top; keep(S); } }
  // アプリの 時計で たしかめる → 本当の 時刻
  function sync() {
    if (busy) return busy;
    var N = window.TengelNative;
    if (!N || typeof N.call !== 'function') return Promise.resolve(now());
    busy = N.call('clock', {}).then(function (r) {
      var c = sample(r); if (!c) return now();
      if (S && top > S.hi) S.hi = top;
      var j = judge(S, c), w = Date.now();
      S = j.s; how = j.how; keep(S);
      L = { w: w, p: pnow(), t: j.est + Math.max(0, w - c.wall), off: j.est - c.wall };
      try { document.dispatchEvent(new CustomEvent('tengel:clock', { detail: { how: how, t: S.t, off: L.off } })); } catch (e) { /* なし */ }
      return now();
    }, function () { return now(); }).then(function (v) { busy = null; return v; }, function () { busy = null; return now(); });
    return busy;
  }
  S = load();
  first = sync();
  document.addEventListener('visibilitychange', function () { if (document.hidden) keepTop(); else sync(); });
  window.addEventListener('pagehide', keepTop);
  setInterval(function () { if (!document.hidden) sync(); }, 60000);
  window.TengelClock = {
    now: now, sync: sync, ready: first,
    how: function () { return how; },
    state: function () { return S ? JSON.parse(JSON.stringify(S)) : null; },
    _judge: judge
  };
})();
