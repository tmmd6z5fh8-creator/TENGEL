// 時計の 番人（第4.191版・まさちゃん 2026/11/17 21:23「お願い！」
//   ＝ 21:11「アプリ内のポイントとか、バトルコインとか不正に受け取ることできないようになってる？」で 見つけた 抜け道 1〜3 を ふさぐ）
//   iPhone の 時計（設定で 日付を かえられる）を そのまま 信じない。アプリ（Clock.swift：お願い「clock」）が わたす、設定では かえられない 時計
//   （電源を 入れてからの 時間 mono・電源を 入れる たびに かわる 番号 boot・アプリを 開く たびに かわる 番号 proc・端末の 番号 dev）と くらべて、
//   本当の 時刻を 見つもる → TengelClock.now()（ミリ秒）。ログインボーナスの 日（login_bonus.js）・カードバトルの ミッションの 月と 調査隊切符（cb/cb_app.js）・
//   ポイントの 期限と できごとの 時刻（points_ui.js）・トレーニングセンターの お世話トークン（tc/tc_app.js）・古い 台帳の リセット（old_reset.js）が 使う
//
// 第4.212版（まさちゃん 2026/11/23 10:12「1.それでやって！」＝ 第4.211版で 残った 抜け穴「日付を 先に 進めて 電源を 入れ直す」を、オンラインの 時刻で ふさぐ）：
//   前は、電源を 入れ直した あと（mono が 0 から 始まる ので、その あいだに どれだけ たったか わからない）は iPhone の 時計を 信じて いた
//   → 日付を 先に 進めて 電源を 入れ直す たびに、ログインボーナス 1日ぶんと お世話トークン 25個を 先どり できた。
//   → iPhone の 時計は「はじめて 見た とき」 だけ 使う。あとは「設定では かえられない 時計」と「インターネットの 時刻」 だけで 進める：
//   ・同じ 起動の 中（電源を 入れ直して いない）：本当の 時刻 ＝ 基準の 時刻 ＋ その あとに 進んだ 電源の 時間（iPhone の 時計を 進めても・もどしても かわらない：'ok'／'ahead'／'back'）
//   ・電源を 入れ直した（boot が かわった・mono が へった）：「前に 見た 時刻 ＋ 電源を 入れてからの 時間」から 進める（'boot'：これより 前で ない ことは たしか）。
//     切れて いた あいだの 時間は、インターネットの 時刻で たしかめる まで 足さない（u＝1：まだ たしかめて いない）
//   ・入れ直したか わからない（boot が 読めない・アプリを 開き直した）：同じ 起動と して 進める（'maybe'：これも たしかな 下の 線）。u＝1
//   ・インターネットの 時刻（アプリの お願い「clock」に net:1 → Clock.swift が Apple の サーバーの 返事の 日付を 読む）が 届いたら、それを 基準に する（'net'）。
//     たしかめる のは：はじめて・電源を 入れ直した あと・入れ直したか わからない とき・前に たしかめて から 7日 たった とき。つながらない ときは 1分（3回 だめなら 5分）あけて また
//     （つながった 知らせ「online」が 来たら すぐ）。
//     届く まで は 上の「たしかな 下の 線」で 進む ＝ オフラインの ままだと、電源が 切れて いた あいだの ぶん だけ ログインボーナスや お世話トークンが おくれる（つながったら 追いつく）
//   ・いちど 出した いちばん 新しい 時刻（hi）より 前には もどらない（期限を もどして 使う・ミッションの 月を もどす・ログインボーナスの 日を もどす が できない）。
//     ただし インターネットの 時刻が 10分 より 前 だった とき だけ は そこへ もどす（前の 版で 進んで しまった 時計・はじめの iPhone の 時計が まちがって いた ときを 直す）
//   ・べつの 端末（バックアップを べつの 端末に もどした）：はじめから（その 端末の 時計を 信じる 'first'。u＝1）
//   ・ほかの 画面は 同期の 呼び出し（now）で 使う：さいごに たしかめた ときからの ページの 時計（performance.now）で 進める。
//     その あいだに iPhone の 時計が とんだ ときは、つぎに たしかめる まで ページの 時計で（アプリに もどって きた とき・1分 ごとに たしかめる）。
//     ページを 開いて はじめて たしかめる まで の 一瞬は、前に 出した いちばん 新しい 時刻（iPhone の 時計は 使わない）
//   ・ほうびを 決める ところ（ログインボーナス）は sync() で たしかめて から。ready ＝ はじめの たしかめ（まだ たしかめて いない ときは インターネットの 時刻を 1.2秒 まで 待つ）
//   ・おぼえる：localStorage 'tengel.clock'（{ v:1, dev, boot, proc, mono, t, tB, mB, hi, u, nv }）。どこにも 送らない
//   ・アプリが 時計を わたさない（テストの にせもの・前の 版の アプリ）ときは、iPhone の 時計の まま（Date.now）
//   App Store版 だけ（Web版には 入れない：build_pwa.py）
(function () {
  'use strict';
  if (!window.__NATIVE) return;
  var KEY = 'tengel.clock', TOL = 10 * 60000, DAY = 86400000, JUMP = 2000;
  var NET_MIN = Date.UTC(2026, 10, 1), NET_MAX = Date.UTC(2100, 0, 1), NET_EVERY = 7 * DAY, NET_WAIT = 1200;      // インターネットの 時刻：ありえる はんい・たしかめ直す 間・はじめに 待つ 時間
  var S = null, L = null, busy = null, how = '', first = null, top = 0, dead = false;      // top：この ページで 出した いちばん 新しい 時刻（さがらない）・dead：アプリが 時計を わたさない
  var netBusy = null, netAt = -1e12, netFail = 0, p0 = 0;
  function fin(x) { return typeof x === 'number' && isFinite(x); }
  function str(x) { return typeof x === 'string' ? x.slice(0, 80) : ''; }
  function good(v) { return !!v && typeof v === 'object' && v.v === 1 && fin(v.mono) && v.mono >= 0 && fin(v.t) && fin(v.tB) && fin(v.mB) && fin(v.hi); }
  function load() {
    try {
      var v = JSON.parse(localStorage.getItem(KEY) || 'null'); if (!good(v)) return null;
      return { v: 1, dev: str(v.dev), boot: str(v.boot), proc: str(v.proc), mono: v.mono, t: v.t, tB: v.tB, mB: v.mB, hi: v.hi, u: v.u ? 1 : 0, nv: fin(v.nv) && v.nv > 0 ? v.nv : 0 };
    } catch (e) { return null; }
  }
  function keep(v) { try { localStorage.setItem(KEY, JSON.stringify(v)); } catch (e) { /* おぼえられない：つぎは はじめから */ } }
  // アプリから とどいた 時計（おかしい ときは null）
  function sample(c) {
    if (!c || typeof c !== 'object' || !fin(c.wall) || !fin(c.mono) || c.mono < 0 || c.wall <= 0) return null;
    return { wall: c.wall, mono: c.mono, boot: str(c.boot), proc: str(c.proc), dev: str(c.dev) };
  }
  // インターネットの 時刻（アプリが 読んだ 返事の 日付 t・その ときの 電源の 時間 mono・行って 帰る までの 時間 rt）。おかしい ときは null
  function netOf(n, c) {
    if (!n || typeof n !== 'object' || n.ok !== true || !fin(n.t) || !fin(n.mono) || !fin(n.rt)) return null;
    if (n.rt < 0 || n.rt > 8000 || n.mono < 0 || n.mono > c.mono + 100 || c.mono - n.mono > 20000 || n.t <= NET_MIN || n.t >= NET_MAX) return null;
    return { t: n.t, mono: n.mono };
  }
  // 本当の 時刻を 見つもる（P＝前の 状態〈なければ null〉・c＝いまの 時計・net＝インターネットの 時刻〈なければ null〉）→ { s：新しい 状態, how, est, down }
  function judge(P, c, net) {
    var other = !P || (P.dev && c.dev && P.dev !== c.dev);
    if (net) {      // インターネットの 時刻：いま ＝ 返事の 時刻 ＋ その あとに 進んだ 電源の 時間。これを 基準に する
      var tn = net.t + Math.max(0, c.mono - net.mono), hi0 = other ? 0 : P.hi, down = hi0 - tn > TOL;      // down：出した 時刻より 10分 より 前 → そこへ もどす
      var tt = down ? tn : Math.max(tn, hi0);
      return { s: { v: 1, dev: c.dev || (other ? '' : P.dev), boot: c.boot, proc: c.proc, mono: c.mono, t: tt, tB: tn, mB: c.mono, hi: tt, u: 0, nv: tn }, how: 'net', est: tn, down: down };
    }
    if (other) return { s: { v: 1, dev: c.dev, boot: c.boot, proc: c.proc, mono: c.mono, t: c.wall, tB: c.wall, mB: c.mono, hi: c.wall, u: 1, nv: 0 }, how: 'first', est: c.wall, down: false };
    // 同じ 起動？ true＝同じ・false＝入れ直した・null＝わからない（boot が 読めない・アプリを 開き直した）
    var same = P.boot && c.boot ? P.boot === c.boot : (P.proc && c.proc && P.proc === c.proc) ? true : c.mono < P.mono - 1000 ? false : null;
    if (same === true && c.mono < P.mono - 1000) same = false;      // 電源を 入れてからの 時間が へった ＝ 入れ直した
    var s = { v: 1, dev: c.dev || P.dev, boot: c.boot, proc: c.proc, mono: c.mono, t: 0, tB: P.tB, mB: P.mB, hi: P.hi, u: P.u ? 1 : 0, nv: P.nv || 0 }, t, h;
    if (same === false) {
      t = P.t + c.mono;      // 入れ直したのは 前に 見た あと → いまは 少なくとも「前に 見た 時刻 ＋ 電源を 入れてからの 時間」。切れて いた あいだは まだ 足さない
      s.tB = t; s.mB = c.mono; s.u = 1; h = 'boot';
    } else {
      t = P.tB + (c.mono - P.mB);      // 同じ 起動 なら：本当の 時刻 ＝ 基準 ＋ 進んだ 電源の 時間（iPhone の 時計は 使わない）
      var d = c.wall - t;
      if (same === null) { s.u = 1; h = 'maybe'; }                                                 // 入れ直したかも（わからない）：下の 線で 進めて、インターネットの 時刻で たしかめる
      else h = Math.abs(d) <= TOL ? 'ok' : d < 0 ? 'back' : 'ahead';
      // 1日 ごとに 基準を iPhone の 時計に 合わせ直す（たしかめて ある・ずれが 1日 9秒 まで の とき だけ：時計の 石の 小さな ずれを ためない）
      if (same === true && !s.u && c.mono - P.mB >= DAY && Math.abs(d) <= Math.max(2000, (c.mono - P.mB) * 1e-4)) { s.tB = c.wall; s.mB = c.mono; t = c.wall; }
    }
    s.t = Math.max(t, P.hi); s.hi = s.t;
    return { s: s, how: h, est: t, down: false };      // est：見つもった 時刻（hi で 持ち上げる 前：ページの 時計は これで 進めて、hi の 前は 止まって 待つ）
  }
  function pnow() { try { return performance.now(); } catch (e) { return Date.now(); } }
  // いまの 本当の 時刻（同期）
  function now() {
    var w = Date.now();
    if (!S) return w;
    if (!L) return dead ? Math.max(w, S.hi) : Math.max(S.hi + Math.max(0, pnow() - p0), top);      // この ページで まだ たしかめて いない（開いた すぐ あと）：前に 出した 時刻から ページの 時計で（iPhone の 時計は 使わない）。アプリが 時計を わたさない ときは 前と 同じ
    var dp = pnow() - L.p, dw = w - L.w, t = Math.abs(dw - dp) <= JUMP ? w + L.off : L.t + Math.max(0, dp);      // iPhone の 時計が とんだ（2秒 より）：つぎに たしかめる まで ページの 時計で
    t = Math.max(t, S.hi, top); top = t;
    return t;
  }
  // 出した いちばん 新しい 時刻を おぼえる（アプリが うしろに 回った とき・たしかめる 前）：つぎに 開いた ときも それより 前に しない
  function keepTop() { if (S && top > S.hi) { S.hi = top; keep(S); } }
  // アプリの 時計（c）と、あれば インターネットの 時刻（net）で 状態を 新しく する
  function apply(c, net) {
    if (S && top > S.hi) S.hi = top;
    var j = judge(S, c, net), w = Date.now();
    S = j.s; how = j.how; keep(S);
    if (j.down) top = 0;
    L = { w: w, p: pnow(), t: j.est + Math.max(0, w - c.wall), off: j.est - c.wall };
    try { document.dispatchEvent(new CustomEvent('tengel:clock', { detail: { how: how, t: S.t, off: L.off, u: S.u } })); } catch (e) { /* なし */ }
  }
  // インターネットの 時刻で たしかめる（いる とき だけ・つながらない ときは あいだを あける）→ たしかめられたら true
  function netNeed() { return !!S && (S.u === 1 || !S.nv || S.t - S.nv > NET_EVERY); }
  function netCheck() {
    if (netBusy) return netBusy;
    var N = window.TengelNative;
    if (!N || typeof N.call !== 'function' || dead) return Promise.resolve(false);
    var p = pnow(); if (netFail && p - netAt < (netFail >= 3 ? 300000 : 60000)) return Promise.resolve(false);
    netAt = p;
    netBusy = N.call('clock', { net: 1 }).then(function (r) {
      var c = sample(r), n = c ? netOf(r.net, c) : null;
      if (!n) { netFail++; return false; }
      netFail = 0; apply(c, n); return true;
    }, function () { netFail++; return false; }).then(function (v) { netBusy = null; return v; }, function () { netBusy = null; return false; });
    return netBusy;
  }
  // アプリの 時計で たしかめる → 本当の 時刻
  function sync() {
    if (busy) return busy;
    var N = window.TengelNative;
    if (!N || typeof N.call !== 'function') { dead = true; return Promise.resolve(now()); }
    busy = N.call('clock', {}).then(function (r) {
      var c = sample(r); if (!c) { dead = true; return now(); }
      dead = false; apply(c, null);
      if (netNeed()) netCheck();
      return now();
    }, function () { dead = true; return now(); }).then(function (v) { busy = null; return v; }, function () { busy = null; return now(); });
    return busy;
  }
  function wait(ms) { return new Promise(function (ok) { setTimeout(ok, ms); }); }
  S = load(); p0 = pnow();
  first = sync().then(function (v) {      // まだ たしかめて いない（はじめて・電源を 入れ直した あと）：インターネットの 時刻を 少し 待つ（つながって いれば すぐ 届く）
    if (!S || !S.u || dead) return v;
    return Promise.race([netCheck(), wait(NET_WAIT)]).then(function () { return now(); }, function () { return now(); });
  });
  document.addEventListener('visibilitychange', function () { if (document.hidden) keepTop(); else sync(); });
  window.addEventListener('online', function () { netFail = 0; sync(); });      // つながった：あいだを あけずに インターネットの 時刻を 聞き直す（まだ たしかめて いない とき だけ：netNeed）
  window.addEventListener('pagehide', keepTop);
  setInterval(function () { if (!document.hidden) sync(); }, 60000);
  window.TengelClock = {
    now: now, sync: sync, ready: first, net: netCheck,
    how: function () { return how; },
    sure: function () { return !!S && !S.u && S.nv > 0 && !dead; },      // インターネットの 時刻で たしかめて あって、その あと 電源を 入れ直して いない（古い 台帳を 自動で 消す 前に 見る）
    state: function () { return S ? JSON.parse(JSON.stringify(S)) : null; },
    _judge: judge
  };
})();
