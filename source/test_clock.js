// 時計の 番人（clock_guard.js・第4.191版）の テスト：node test_clock.js
//   まさちゃん 2026/11/17 21:23「お願い！」（21:11「アプリ内のポイントとか、バトルコインとか不正に受け取ることできないようになってる？」の 抜け道 1〜3）
//   ・アプリの 時計（Clock.swift：wall・mono・boot・proc・dev）の にせものを 使って、iPhone の 時計を 進めた・もどした・電源を 入れ直した・アプリを 開き直した を ためす
//   ・本当の 時刻（TengelClock.now）が、同じ 起動の 中では iPhone の 時計を かえても 本当の 時刻から 10分 より ずれない
//   ・電源を 入れ直した あとは iPhone の 時計を 信じる（ただし 前に 見た 時刻 ＋ 電源の 時間 より 前には しない）・べつの 端末は はじめから
//   ・でたらめに 4万回（時計を とばす・もどす・少しずつ 進める・開き直す・入れ直す）で きまりが くずれない
'use strict';
const fs = require('fs'), vm = require('vm'), path = require('path');
const SRC = fs.readFileSync(path.join(__dirname, 'clock_guard.js'), 'utf8');
let n = 0, bad = 0;
function check(c, label) { n++; if (!c) bad++; console.log((c ? '  ✅ ' : '  ❌ ') + label); }
const MIN = 60000, HOUR = 3600000, DAY = 86400000, TOL = 10 * MIN, T0 = Date.UTC(2026, 10, 17, 3, 0, 0);

// にせものの 世界：real＝本当の 時刻・wall＝iPhone の 時計・mono＝電源を 入れてからの 時間・perf＝ページの 時計
function world(o) {
  o = o || {};
  const E = { real: T0, off: 0, mono: o.mono == null ? 5 * DAY : o.mono, perf: 1000, boot: o.boot == null ? 'B1' : o.boot, proc: 'P1', dev: o.dev || 'D1', store: o.store || {}, native: o.native !== false, calls: 0 };
  E.wall = () => E.real + E.off;
  E.ls = [];
  E.hide = function () { if (E.ctx) { E.ctx.document.hidden = true; E.ls.forEach(f => f()); } };      // アプリが うしろに 回る（閉じる 前は かならず）
  E.load = function () {      // ページを 開く（clock_guard.js を 読む）
    E.hide(); E.ls = [];
    const ctx = E.ctx = {
      window: { __NATIVE: true, addEventListener: (t, f) => { if (t === 'pagehide') E.ls.push(f); } }, console,
      document: { hidden: false, addEventListener: (t, f) => { if (t === 'visibilitychange') E.ls.push(f); }, dispatchEvent() { return true; } },
      localStorage: { getItem: k => (Object.prototype.hasOwnProperty.call(E.store, k) ? E.store[k] : null), setItem: (k, v) => { E.store[k] = String(v); } },
      performance: { now: () => E.perf }, Date: { now: () => E.wall() }, setInterval() { return 1; },
      CustomEvent: function (t, x) { this.type = t; this.detail = x && x.detail; }, Promise, JSON, Math, isFinite
    };
    ctx.window.TengelNative = { call: name => { E.calls++; return Promise.resolve(name === 'clock' && E.native ? { wall: E.wall(), mono: E.mono, boot: E.boot, proc: E.proc, dev: E.dev } : true); } };
    vm.createContext(ctx); vm.runInContext(SRC, ctx);
    E.C = ctx.window.TengelClock; return E.C.ready;
  };
  E.pass = function (ms) { E.real += ms; E.mono += ms; E.perf += ms; };            // 本当に 時間が たつ
  E.reboot = function (down, up) { E.real += down + up; E.mono = up; E.perf = 1000; E.boot = E.boot ? 'B' + Math.random().toString(36).slice(2, 8) : ''; E.proc = 'P' + Math.random().toString(36).slice(2, 8); };
  E.reopen = function () { E.proc = 'P' + Math.random().toString(36).slice(2, 8); E.perf = 1000; return E.load(); };      // アプリを 閉じて 開き直す
  return E;
}
const near = (a, b, tol) => Math.abs(a - b) <= (tol == null ? 5 : tol);

(async () => {
  console.log('■ はじめて・同じ 起動の 中（boot が 読める）');
  let E = world(); await E.load();
  check(E.C.how() === 'first' && near(E.C.now(), E.wall()), `はじめて：iPhone の 時計を 信じる（${E.C.how()}）`);
  E.pass(HOUR); await E.C.sync();
  check(E.C.how() === 'ok' && near(E.C.now(), E.wall()), `1時間 たった：そのまま（${E.C.how()}）`);
  E.off = DAY; E.pass(MIN);
  check(near(E.C.now(), E.real, 5), `日付を 1日 進めた（まだ たしかめる 前）：ページの 時計で 本当の 時刻（${(E.C.now() - E.real) / 1000}秒）`);
  await E.C.sync();
  check(E.C.how() === 'ahead' && near(E.C.now(), E.real, 5), `日付を 1日 進めた → たしかめる：本当の 時刻（${E.C.how()}・${(E.C.now() - E.real) / 1000}秒）`);
  E.pass(10 * MIN);
  check(near(E.C.now(), E.real, 5), `その あとも 本当の 時刻で 進む（${(E.C.now() - E.real) / 1000}秒）`);
  E.off = 0; await E.C.sync();
  check(E.C.how() === 'ok' && near(E.C.now(), E.real, 5), `時計を もとに もどした → そのまま（${E.C.how()}）`);
  E.off = -DAY; E.pass(MIN); await E.C.sync();
  check(E.C.how() === 'back' && near(E.C.now(), E.real, 5), `日付を 1日 もどした → 本当の 時刻（もどらない）（${E.C.how()}）`);
  E.off = 0; await E.C.sync();
  E.off = DAY; await E.reopen();
  check(E.C.how() === 'ahead' && near(E.C.now(), E.real, 5), `アプリを 閉じて 日付を 進めて 開き直す（boot が 同じ）→ 本当の 時刻（${E.C.how()}）`);
  E.off = 3 * DAY; E.pass(2 * MIN); E.hide(); E.ls = []; const pre = E.load();
  check(E.C.now() >= E.wall() - 5, `開いた すぐ あと（まだ たしかめる 前）は iPhone の 時計（${Math.round((E.C.now() - E.real) / HOUR)}時間 先）`); await pre;
  check(E.C.how() === 'ahead' && near(E.C.now(), E.real, 5) && JSON.parse(E.store['tengel.clock']).hi < E.real + TOL, `たしかめる 前に 出した 時刻は おぼえない → たしかめたら 本当の 時刻（${E.C.how()}）`);
  E.off = 3 * DAY; E.pass(2 * MIN); await E.reopen();
  check(E.C.how() === 'ahead' && near(E.C.now(), E.real, 5), `もう 1回（3日 進めた）→ 本当の 時刻（${E.C.how()}）`);
  check(E.calls >= 1, 'アプリの 時計に たずねた');

  console.log('■ 電源を 入れ直した');
  E = world(); E.off = 0; await E.load(); E.pass(HOUR); await E.C.sync();
  E.reboot(8 * HOUR, 3 * MIN); await E.load();
  check(E.C.how() === 'boot' && near(E.C.now(), E.wall()), `電源を 入れ直した（8時間 切って いた）→ iPhone の 時計を 信じる（${E.C.how()}）`);
  const t1 = E.C.now(); E.reboot(HOUR, 2 * MIN); E.off = -3 * DAY; await E.load();
  check(E.C.how() === 'boot-back' && E.C.now() >= t1 + 2 * MIN - 5 && E.C.now() < E.real, `入れ直したら 時計が 3日 おくれて いた → 前に 見た 時刻 ＋ 電源の 時間 より 前に しない（${E.C.how()}）`);
  E.off = 0; E.pass(5 * MIN); await E.C.sync();
  check(E.C.how() === 'fix' && near(E.C.now(), E.real), `その あと 時計が 直った → 1回 だけ 信じる（${E.C.how()}）`);
  E.off = DAY; E.pass(MIN); await E.C.sync();
  check(E.C.how() === 'ahead' && near(E.C.now(), E.real, 5), `直った あとに 日付を 進めた → 本当の 時刻（${E.C.how()}）`);
  E.off = 0; await E.C.sync();
  E.reboot(HOUR, MIN); E.off = DAY; await E.load();
  check(E.C.how() === 'boot' && near(E.C.now(), E.wall()), `進めた まま 電源を 入れ直す → わからない ので 信じる（再起動を くり返す やり方は 見分けられない：${E.C.how()}）`);

  console.log('■ boot が 読めない（iOS が 見せて くれない）とき');
  E = world({ boot: '' }); await E.load(); E.pass(HOUR); await E.C.sync();
  E.off = DAY; E.pass(MIN); await E.C.sync();
  check(E.C.how() === 'ahead' && near(E.C.now(), E.real, 5), `アプリを 開いた まま 日付を 進めた（同じ アプリ）→ 本当の 時刻（${E.C.how()}）`);
  E.pass(MIN); await E.reopen();
  check(E.C.how() === 'ahead' && near(E.C.now(), E.real, 5), `アプリを 開き直した（電源は 5日 入れっぱなし）→ 進めた と わかる（${E.C.how()}）`);
  E.off = 0; await E.C.sync(); E.reboot(8 * HOUR, 2 * MIN); await E.load();
  check(E.C.how() === 'boot' && near(E.C.now(), E.wall()), `電源を 入れ直した（電源の 時間が へった）→ 信じる（${E.C.how()}）`);
  E.pass(3 * MIN); E.off = DAY; await E.reopen();
  check(E.C.how() === 'maybe' && near(E.C.now(), E.wall()), `入れ直した すぐ あと（電源の 時間 5分）に 開き直して 進めた → 見分けられない ので 信じる（${E.C.how()}）`);
  // まじめな 人：入れ直して、前より 長く 電源を 入れて いた → 信じる
  E = world({ boot: '', mono: 2 * HOUR }); await E.load(); E.reboot(10 * HOUR, 3 * HOUR); await E.reopen();
  check(E.C.how() === 'maybe' && near(E.C.now(), E.wall()), `入れ直して 前（2時間）より 長く（3時間）入れて いた → 信じる（まじめな 人を こまらせない：${E.C.how()}）`);

  console.log('■ べつの 端末・おかしい おぼえ・アプリの 時計が ない');
  E = world(); await E.load(); E.off = 0; E.pass(DAY); await E.C.sync(); const st0 = JSON.parse(E.store['tengel.clock']);
  E.dev = 'D2'; E.reboot(DAY, 10 * DAY); await E.load();
  check(E.C.how() === 'first' && near(E.C.now(), E.wall()) && st0.dev === 'D1', `バックアップを べつの 端末に もどした（電源は 10日 入れっぱなし）→ はじめから（${E.C.how()}）`);
  E = world({ store: { 'tengel.clock': '{こわれた' } }); await E.load();
  check(E.C.how() === 'first', `おぼえが こわれて いる → はじめから（${E.C.how()}）`);
  E = world({ store: { 'tengel.clock': JSON.stringify({ v: 1, mono: 'x', t: 1 }) } }); await E.load();
  check(E.C.how() === 'first', `おぼえの 形が おかしい → はじめから（${E.C.how()}）`);
  E = world({ native: false }); await E.load();
  check(E.C.how() === '' && E.C.now() === E.wall() && E.C.state() === null && !E.store['tengel.clock'], 'アプリの 時計が ない（テストの にせもの）→ iPhone の 時計の まま・何も おぼえない');
  E.off = DAY; check(E.C.now() === E.wall(), 'アプリの 時計が ない ときは 進めても そのまま（前の 版と 同じ）');

  console.log('■ 少しずつ 進める・小さな ずれ');
  E = world(); await E.load();
  for (let i = 0; i < 30; i++) { E.pass(MIN); E.off += 9 * MIN; await E.C.sync(); }
  check(E.C.now() - E.real <= TOL && E.C.now() >= E.real, `1分 ごとに 9分ずつ 進めた（30回・4時間半）→ 本当の 時刻から 10分 より 先には 行かない（${Math.round((E.C.now() - E.real) / MIN)}分）`);
  E = world(); await E.load(); let allOk = true, maxd = 0;
  for (let i = 0; i < 400; i++) { E.pass(6 * HOUR); E.off += 1500; await E.C.sync(); allOk = allOk && E.C.how() === 'ok'; maxd = Math.max(maxd, Math.abs(E.C.now() - E.wall())); }
  check(allOk && maxd <= 5, `時計の 石が 1日 6秒ずつ ずれる（100日：合わせて 10分）→ ずっと そのまま（1日 ごとに 合わせ直す：${allOk}・${maxd}ms）`);
  E = world(); await E.load(); for (let i = 0; i < 60; i++) { E.pass(DAY); E.off += 60000; await E.C.sync(); }
  check(E.C.how() === 'ahead' && E.C.now() - E.real <= TOL, `毎日 1分ずつ 進める（60日）→ 合わせ直さない（10分 より 先には 行かない：${E.C.how()}・${Math.round((E.C.now() - E.real) / 1000)}秒）`);

  console.log('■ でたらめに（時計を とばす・もどす・少しずつ・アプリを 開き直す・電源を 入れ直す）');
  let rnd = 12345; const R = () => (rnd = (rnd * 1103515245 + 12345) % 2147483648) / 2147483648;
  // ① 電源を 入れ直さない（boot あり／なし・アプリの 開き直しも）：1万回 ずっと 本当の 時刻から 10分 より ずれない・さがらない
  for (const boot of ['B1', '']) {
    E = world({ boot }); await E.load(); let prev = E.C.now(), ok1 = true, ok2 = true, worst = 0, hows = {};
    for (let i = 0; i < 10000; i++) {
      const r = R();
      if (r < 0.40) E.pass(Math.floor(R() * 2 * HOUR));
      else if (r < 0.55) E.off = Math.max(-3.5 * DAY, Math.min(3.5 * DAY, E.off + Math.floor((R() - 0.5) * 3 * DAY)));      // 電源は 5日 より 入れっぱなし → 進めた 分は それより 小さい
      else if (r < 0.65) E.off += Math.floor((R() - 0.5) * 18 * MIN);
      else if (r < 0.70) E.off = 0;
      else if (r < 0.80) await E.reopen();
      else await E.C.sync();
      const h = E.C.how(); hows[h] = (hows[h] || 0) + 1;
      const t = E.C.now(), d = t - E.real;
      if (t < prev) ok1 = false; prev = t;
      worst = Math.max(worst, Math.abs(d)); if (d > TOL + 5 || d < -TOL - 5) ok2 = false;
    }
    check(ok1 && ok2 && !hows.maybe && !hows.boot, `電源を 入れ直さない（boot ${boot ? 'あり' : 'なし'}・アプリの 開き直し ${hows.first ? '' : ''}1万回）：本当の 時刻から 10分 より ずれない・さがらない（いちばん ずれた ${Math.round(worst / 1000)}秒）`);
    console.log('     ', JSON.stringify(hows));
  }
  // ② 電源の 入れ直しも まぜる：さがらない／入れ直した あとに 時計を もとに もどして たしかめたら、また 10分 より ずれない（信じた あいだに 先に 進んだ 分 H までは そのまま）
  for (const boot of ['B1', '']) {
    E = world({ boot }); await E.load(); let prev = E.C.now(), ok1 = true, ok2 = true, lenient = false, worst = 0, hows = {}, H = 0, chk = 0;
    for (let i = 0; i < 10000; i++) {
      const r = R(); let synced = true;
      if (r < 0.40) { E.pass(Math.floor(R() * 2 * HOUR)); synced = false; }
      else if (r < 0.50) { E.off += Math.floor((R() - 0.5) * 6 * DAY); synced = false; }
      else if (r < 0.60) { E.off += Math.floor((R() - 0.5) * 18 * MIN); synced = false; }
      else if (r < 0.70) { E.off = 0; synced = false; }
      else if (r < 0.72) { E.reboot(Math.floor(R() * DAY), Math.floor(R() * 3 * HOUR) + MIN); await E.load(); }
      else if (r < 0.80) await E.reopen();
      else await E.C.sync();
      const h = E.C.how(); hows[h] = (hows[h] || 0) + 1;
      if (synced && (h === 'boot' || h === 'maybe' || h === 'fix' || h === 'first' || h === 'boot-back')) lenient = true;      // 入れ直した あとは 見分けられない（信じる・おくれた 時計なら 前に 見た 時刻 ＋ 電源の 時間）
      const t = E.C.now();
      if (t < prev) ok1 = false; prev = t;
      if (lenient) H = Math.max(H, t);
      else { chk++; const hi = Math.max(E.real + TOL, H), d = t > hi ? t - hi : t < E.real - TOL ? E.real - TOL - t : 0; worst = Math.max(worst, d); if (d > 5) ok2 = false; }
      if (lenient && synced && E.off === 0 && (h === 'ok' || h === 'boot')) lenient = false;      // 時計を もとに もどして たしかめた → また 見はる
    }
    check(ok1, `入れ直しも まぜる（boot ${boot ? 'あり' : 'なし'}・1万回）：本当の 時刻は さがらない`);
    check(ok2 && chk > 100, `入れ直しも まぜる（boot ${boot ? 'あり' : 'なし'}）：時計を もとに もどして たしかめた あとは 10分 より ずれない（たしかめた ${chk}回・はみ出した いちばん 大きい 分 ${Math.round(worst / 1000)}秒）`);
    console.log('     ', JSON.stringify(hows));
  }

  console.log(`\n結果：${n - bad}/${n} OK`);
  process.exit(bad ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
