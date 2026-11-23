// 時計の 番人（clock_guard.js・第4.191版 → 第4.212版）の テスト：node test_clock.js
//   まさちゃん 2026/11/17 21:23「お願い！」（21:11「アプリ内のポイントとか、バトルコインとか不正に受け取ることできないようになってる？」の 抜け道 1〜3）
//   まさちゃん 2026/11/23 10:12「1.それでやって！」（日付を 先に 進めて 電源を 入れ直す 抜け穴を、オンラインの 時刻で ふさぐ）
//   ・アプリの 時計（Clock.swift：wall・mono・boot・proc・dev・net）の にせものを 使って、iPhone の 時計を 進めた・もどした・電源を 入れ直した・アプリを 開き直した・オンライン／オフライン を ためす
//   ・本当の 時刻（TengelClock.now）は、はじめて 見た とき の あとは iPhone の 時計を 使わない：同じ 起動の 中では 本当の 時刻と 同じ・
//     電源を 入れ直した あとは「前に 見た 時刻 ＋ 電源の 時間」（本当の 時刻より 先には 行かない）・インターネットの 時刻が 届いたら 本当の 時刻
//   ・でたらめに 4万回（時計を とばす・もどす・開き直す・入れ直す・つながる／切れる）で きまりが くずれない
'use strict';
const fs = require('fs'), vm = require('vm'), path = require('path');
const SRC = fs.readFileSync(path.join(__dirname, 'clock_guard.js'), 'utf8');
let n = 0, bad = 0;
function check(c, label) { n++; if (!c) bad++; console.log((c ? '  ✅ ' : '  ❌ ') + label); }
const MIN = 60000, HOUR = 3600000, DAY = 86400000, TOL = 10 * MIN, T0 = Date.UTC(2026, 10, 23, 3, 0, 0);

// にせものの 世界：real＝本当の 時刻・wall＝iPhone の 時計・mono＝電源を 入れてからの 時間・perf＝ページの 時計・online＝インターネットに つながって いる
function world(o) {
  o = o || {};
  const E = { real: T0, off: 0, mono: o.mono == null ? 5 * DAY : o.mono, perf: 1000, boot: o.boot == null ? 'B1' : o.boot, proc: 'P1', dev: o.dev || 'D1', store: o.store || {}, native: o.native !== false,
    online: !!o.online, calls: 0, netCalls: 0, netAns: null };
  E.wall = () => E.real + E.off;
  E.ls = [];
  E.hide = function () { if (E.ctx) { E.ctx.document.hidden = true; E.ls.forEach(f => f()); } };      // アプリが うしろに 回る（閉じる 前は かならず）
  E.load = function () {      // ページを 開く（clock_guard.js を 読む）
    E.hide(); E.ls = [];
    const ctx = E.ctx = {
      window: { __NATIVE: true, addEventListener: (t, f) => { if (t === 'pagehide') E.ls.push(f); } }, console,
      document: { hidden: false, addEventListener: (t, f) => { if (t === 'visibilitychange') E.ls.push(f); }, dispatchEvent() { return true; } },
      localStorage: { getItem: k => (Object.prototype.hasOwnProperty.call(E.store, k) ? E.store[k] : null), setItem: (k, v) => { E.store[k] = String(v); } },
      performance: { now: () => E.perf }, Date: { now: () => E.wall(), UTC: Date.UTC }, setInterval() { return 1; }, setTimeout() { return 1; },      // 待つ 時間（1.2秒）は 進めない：返事は すぐ 届く
      CustomEvent: function (t, x) { this.type = t; this.detail = x && x.detail; }, Promise, JSON, Math, isFinite
    };
    ctx.window.TengelNative = { call: (name, p) => {
      E.calls++;
      if (name !== 'clock' || !E.native) return Promise.resolve(true);
      const r = { wall: E.wall(), mono: E.mono, boot: E.boot, proc: E.proc, dev: E.dev };
      if (p && p.net) { E.netCalls++; r.net = E.netAns ? E.netAns(E) : E.online ? { ok: true, t: E.real, mono: E.mono, rt: 40, why: '' } : { ok: false, t: 0, mono: 0, rt: 0, why: 'net' }; }
      return Promise.resolve(r);
    } };
    vm.createContext(ctx); vm.runInContext(SRC, ctx);
    E.C = ctx.window.TengelClock; return E.C.ready;
  };
  E.pass = function (ms) { E.real += ms; E.mono += ms; E.perf += ms; };            // 本当に 時間が たつ
  E.reboot = function (down, up) { E.real += down + up; E.mono = up; E.perf = 1000; E.boot = E.boot ? 'B' + Math.random().toString(36).slice(2, 8) : ''; E.proc = 'P' + Math.random().toString(36).slice(2, 8); };
  E.reopen = function () { E.proc = 'P' + Math.random().toString(36).slice(2, 8); E.perf = 1000; return E.load(); };      // アプリを 閉じて 開き直す
  E.settle = async function () { await E.C.sync(); for (let i = 0; i < 12; i++) await Promise.resolve(); await new Promise(r => setImmediate(r)); };      // たしかめる（いる ときは インターネットの 返事も 届く まで 待つ）
  return E;
}
const near = (a, b, tol) => Math.abs(a - b) <= (tol == null ? 5 : tol);

(async () => {
  console.log('■ はじめて・同じ 起動の 中（オフライン・boot が 読める）');
  let E = world(); await E.load();
  check(E.C.how() === 'first' && near(E.C.now(), E.wall()) && !E.C.sure() && E.C.state().u === 1, `はじめて：iPhone の 時計から 始める（まだ たしかめて いない：${E.C.how()}）`);
  E.pass(HOUR); await E.C.sync();
  check(E.C.how() === 'ok' && near(E.C.now(), E.real), `1時間 たった：そのまま（${E.C.how()}）`);
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
  check(E.C.now() <= E.real + 5 && E.C.now() >= E.real - 2 * MIN - 5, `開いた すぐ あと（まだ たしかめる 前）も iPhone の 時計は 使わない（前に 出した 時刻から：${Math.round((E.C.now() - E.real) / 1000)}秒）`); await pre;
  check(E.C.how() === 'ahead' && near(E.C.now(), E.real, 5) && JSON.parse(E.store['tengel.clock']).hi < E.real + 5, `たしかめたら 本当の 時刻（${E.C.how()}）`);
  E.off = 9 * MIN; E.pass(MIN); await E.C.sync();
  check(E.C.how() === 'ok' && near(E.C.now(), E.real, 5), `9分 進めた（10分 までの 小さな ずれ）でも ついて 行かない（本当の 時刻：${(E.C.now() - E.real) / 1000}秒）`);
  check(E.calls >= 1 && E.netCalls >= 1, 'アプリの 時計に たずねた・インターネットの 時刻も たずねた（オフライン なので 届かない）');

  console.log('■ 電源を 入れ直した（オフライン）：日付を 進めても 先に 行かない');
  E = world(); await E.load(); E.pass(HOUR); await E.C.sync(); const tA = E.C.now();
  E.reboot(8 * HOUR, 3 * MIN); await E.load();
  check(E.C.how() === 'boot' && near(E.C.now(), tA + 3 * MIN) && E.C.now() < E.real && E.C.state().u === 1 && !E.C.sure(),
    `電源を 入れ直した（8時間 切って いた）→「前に 見た 時刻 ＋ 電源の 時間」から（切れて いた あいだは まだ 足さない：${E.C.how()}・本当より ${Math.round((E.real - E.C.now()) / HOUR)}時間 前）`);
  E.pass(30 * MIN); await E.C.sync();
  check(E.C.how() === 'ahead' && near(E.C.now(), tA + 33 * MIN), `その あとは 本当の 速さで 進む（30分 たって 30分 進む。iPhone の 時計は 8時間 先に 見える：${E.C.how()}）`);
  const tB0 = E.C.now(); E.off = DAY; E.reboot(HOUR, 2 * MIN); await E.load();
  check(E.C.how() === 'boot' && near(E.C.now(), tB0 + 2 * MIN) && E.C.now() < E.real, `日付を 1日 進めて 電源を 入れ直す → 進まない（前は ここで 1日 先どり できた：${E.C.how()}）`);
  let gain = 0; for (let i = 0; i < 20; i++) { const b = E.C.now(); E.off += DAY; E.reboot(MIN, MIN); await E.load(); gain = Math.max(gain, E.C.now() - b - MIN); }
  check(gain <= 5 && E.C.now() < E.real, `日付を 1日ずつ 進めて 20回 入れ直す → 1回も 先に 進まない（電源の 時間の ぶん だけ：よぶんに 進んだ ${gain}ms）`);
  E.off = -3 * DAY; const tC = E.C.now(); E.reboot(HOUR, 2 * MIN); await E.load();
  check(E.C.how() === 'boot' && E.C.now() >= tC + 2 * MIN - 5, `入れ直したら 時計が 3日 おくれて いた → さがらない（${E.C.how()}）`);

  console.log('■ インターネットの 時刻（オンライン）');
  E.off = 0; E.online = true; E.pass(2 * MIN); await E.settle();
  check(E.C.how() === 'net' && near(E.C.now(), E.real) && E.C.sure() && E.C.state().u === 0, `つながった → 本当の 時刻に 追いつく（${E.C.how()}）`);
  E.off = DAY; E.pass(MIN); await E.settle();
  check(E.C.how() === 'ahead' && near(E.C.now(), E.real), `たしかめた あとに 日付を 進めた → 本当の 時刻（${E.C.how()}）`);
  E.reboot(5 * HOUR, 2 * MIN); await E.load(); await E.settle();
  check(near(E.C.now(), E.real) && E.C.sure() && E.C.state().nv > T0, `日付を 進めた まま 電源を 入れ直す（オンライン）→ 本当の 時刻（切れて いた 5時間も 足す：${E.C.how()}）`);
  E = world({ online: true }); E.off = 40 * DAY; await E.load(); await E.settle();
  check(near(E.C.now(), E.real) && E.C.sure(), `はじめて 開いた ときに iPhone の 時計が 40日 先 だった（オンライン）→ 本当の 時刻（${Math.round((E.C.now() - E.real) / 1000)}秒）`);
  E = world(); E.off = 40 * DAY; await E.load();
  check(E.C.how() === 'first' && near(E.C.now(), E.wall()), 'はじめて 開いた ときに 40日 先（オフライン）→ その 時計から（まだ たしかめて いない）');
  E.online = true; E.off = 0; E.pass(2 * MIN); await E.settle();
  check(E.C.how() === 'net' && near(E.C.now(), E.real) && near(E.C.state().hi, E.real), `あとで つながった → 進んで いた 時計を 本当の 時刻へ もどす（${Math.round((E.C.now() - E.real) / 1000)}秒）`);
  { const W = world({ online: true }); await W.load(); await W.settle(); const t0 = W.C.now(); W.netAns = e => ({ ok: true, t: e.real - 5 * MIN, mono: e.mono, rt: 40 }); W.pass(8 * DAY); await W.settle();
    check(W.C.how() === 'net' && W.C.now() >= t0 + 8 * DAY - 5, `インターネットの 時刻が 5分 おくれて いた（10分 まで）→ さがらない（出した 時刻の まま）`); }
  { const W = world({ online: true }); await W.load(); await W.settle(); const c0 = W.netCalls; for (let i = 0; i < 20; i++) { W.pass(HOUR); await W.settle(); }
    const c1 = W.netCalls; W.pass(8 * DAY); await W.settle();
    check(c1 === c0 && W.netCalls === c1 + 1, `たしかめて ある あいだは たずねない（20回 たしかめて 0回）・7日 たったら もう 1回（${W.netCalls - c1}回）`); }
  { const W = world(); await W.load(); const c0 = W.netCalls; for (let i = 0; i < 30; i++) { W.pass(1000); await W.settle(); }
    const c1 = W.netCalls; for (let i = 0; i < 10; i++) { W.pass(MIN + 1000); await W.settle(); }
    check(c1 - c0 <= 1 && W.netCalls - c1 >= 2 && W.netCalls - c1 <= 10, `つながらない ときは あいだを あける（30秒で ${c1 - c0}回・その あと 10分で ${W.netCalls - c1}回）`); }
  for (const [nm, ans] of [['時刻が 2026年11月より 前', e => ({ ok: true, t: Date.UTC(2020, 0, 1), mono: e.mono, rt: 40 })], ['行って 帰る のに 9秒', e => ({ ok: true, t: e.real, mono: e.mono, rt: 9000 })],
    ['電源の 時間が 先', e => ({ ok: true, t: e.real, mono: e.mono + 5000, rt: 40 })], ['電源の 時間が 30秒 前', e => ({ ok: true, t: e.real, mono: e.mono - 30000, rt: 40 })], ['ok が ない', e => ({ t: e.real, mono: e.mono, rt: 40 })],
    ['数で ない', e => ({ ok: true, t: 'x', mono: e.mono, rt: 40 })], ['返事なし', () => null]]) {
    const W = world({ online: true }); W.netAns = ans; W.off = DAY; await W.load(); await W.settle();
    check(W.C.how() !== 'net' && !W.C.sure() && W.C.state().nv === 0 && W.C.state().u === 1 && W.netCalls >= 1, `おかしな 返事は 使わない（${nm}）`);
  }

  console.log('■ boot が 読めない（iOS が 見せて くれない）とき（オフライン）');
  E = world({ boot: '' }); await E.load(); E.pass(HOUR); await E.C.sync();
  E.off = DAY; E.pass(MIN); await E.C.sync();
  check(E.C.how() === 'ahead' && near(E.C.now(), E.real, 5), `アプリを 開いた まま 日付を 進めた（同じ アプリ）→ 本当の 時刻（${E.C.how()}）`);
  E.pass(MIN); await E.reopen();
  check(E.C.how() === 'maybe' && near(E.C.now(), E.real, 5), `アプリを 開き直した（入れ直したか わからない）→ 同じ 起動と して 進める ＝ 本当の 時刻（${E.C.how()}）`);
  E.off = 0; await E.C.sync(); const tD = E.C.now(); E.reboot(8 * HOUR, 2 * MIN); await E.load();
  check(E.C.how() === 'boot' && near(E.C.now(), tD + 2 * MIN), `電源を 入れ直した（電源の 時間が へった）→ 前に 見た 時刻 ＋ 電源の 時間（${E.C.how()}）`);
  E = world({ boot: '', mono: 2 * HOUR }); await E.load(); const tE = E.C.now(); E.off = DAY; E.reboot(10 * HOUR, 3 * HOUR); await E.reopen();
  check(E.C.how() === 'maybe' && E.C.now() <= E.real - 10 * HOUR + 5 && E.C.now() >= tE, `入れ直して 前（2時間）より 長く（3時間）入れて いた（見分けられない）→ 日付を 進めて いても 先に 行かない（${E.C.how()}）`);
  E.online = true; E.pass(2 * MIN); await E.settle();
  check(E.C.how() === 'net' && near(E.C.now(), E.real), 'つながったら 本当の 時刻');

  console.log('■ べつの 端末・おかしい おぼえ・アプリの 時計が ない');
  E = world(); await E.load(); E.off = 0; E.pass(DAY); await E.C.sync(); const st0 = JSON.parse(E.store['tengel.clock']);
  E.dev = 'D2'; E.reboot(DAY, 10 * DAY); await E.load();
  check(E.C.how() === 'first' && near(E.C.now(), E.wall()) && st0.dev === 'D1', `バックアップを べつの 端末に もどした（電源は 10日 入れっぱなし）→ はじめから（${E.C.how()}）`);
  E = world({ store: { 'tengel.clock': '{こわれた' } }); await E.load();
  check(E.C.how() === 'first', `おぼえが こわれて いる → はじめから（${E.C.how()}）`);
  E = world({ store: { 'tengel.clock': JSON.stringify({ v: 1, mono: 'x', t: 1 }) } }); await E.load();
  check(E.C.how() === 'first', `おぼえの 形が おかしい → はじめから（${E.C.how()}）`);
  E = world({ native: false }); await E.load();
  check(E.C.how() === '' && E.C.now() === E.wall() && E.C.state() === null && !E.store['tengel.clock'] && !E.C.sure(), 'アプリの 時計が ない（テストの にせもの）→ iPhone の 時計の まま・何も おぼえない');
  E.off = DAY; check(E.C.now() === E.wall(), 'アプリの 時計が ない ときは 進めても そのまま（前の 版と 同じ）');
  { const W = world(); await W.load(); W.pass(HOUR); await W.C.sync(); W.native = false; W.pass(HOUR); await W.reopen();
    check(W.C.now() === W.wall() && W.netCalls >= 1, '前に おぼえた 時刻が あって、アプリが 時計を わたさなく なった → iPhone の 時計で 進む（止まらない）'); }
  { const old = { v: 1, dev: 'D1', boot: 'B1', proc: 'P0', mono: 5 * DAY - HOUR, t: T0 - HOUR, tB: T0 - HOUR, mB: 5 * DAY - HOUR, hi: T0 - HOUR, u: 0 };      // 前の 版（第4.211版 まで）の おぼえ：nv が ない
    const W = world({ store: { 'tengel.clock': JSON.stringify(old) }, online: true }); await W.load(); await W.settle();
    check(near(W.C.now(), W.real) && W.C.sure() && W.netCalls === 1, '前の 版の おぼえ（たしかめた しるしが ない）→ 開いたら インターネットの 時刻で たしかめる（1回）'); }

  console.log('■ 小さな ずれ');
  E = world(); await E.load();
  for (let i = 0; i < 30; i++) { E.pass(MIN); E.off += 9 * MIN; await E.C.sync(); }
  check(near(E.C.now(), E.real, 5), `1分 ごとに 9分ずつ 進めた（30回・4時間半）→ 本当の 時刻の まま（${Math.round((E.C.now() - E.real) / 1000)}秒）`);
  E = world({ online: true }); await E.load(); await E.settle(); let maxd = 0;
  for (let i = 0; i < 400; i++) { E.pass(6 * HOUR); E.off += 1500; await E.settle(); maxd = Math.max(maxd, Math.abs(E.C.now() - E.real)); }
  check(maxd <= 60000, `時計の 石が 1日 6秒ずつ ずれる（100日）→ 本当の 時刻から 1分 より ずれない（いちばん ずれた ${Math.round(maxd / 1000)}秒）`);

  console.log('■ でたらめに（時計を とばす・もどす・少しずつ・アプリを 開き直す・電源を 入れ直す・つながる／切れる）');
  let rnd = 12345; const R = () => (rnd = (rnd * 1103515245 + 12345) % 2147483648) / 2147483648;
  // ① オフライン・電源を 入れ直さない（boot あり／なし・アプリの 開き直しも）：1万回 ずっと 本当の 時刻と 同じ・さがらない
  for (const boot of ['B1', '']) {
    E = world({ boot }); await E.load(); let prev = E.C.now(), ok1 = true, ok2 = true, worst = 0, hows = {};
    for (let i = 0; i < 10000; i++) {
      const r = R();
      if (r < 0.40) E.pass(Math.floor(R() * 2 * HOUR));
      else if (r < 0.55) E.off = Math.max(-300 * DAY, Math.min(300 * DAY, E.off + Math.floor((R() - 0.5) * 30 * DAY)));
      else if (r < 0.65) E.off += Math.floor((R() - 0.5) * 18 * MIN);
      else if (r < 0.70) E.off = 0;
      else if (r < 0.80) await E.reopen();
      else await E.C.sync();
      const h = E.C.how(); hows[h] = (hows[h] || 0) + 1;
      const t = E.C.now(), d = t - E.real;
      if (t < prev) ok1 = false; prev = t;
      worst = Math.max(worst, Math.abs(d)); if (Math.abs(d) > 2005) ok2 = false;      // たしかめる 前に iPhone の 時計が 2秒 より 小さく 動いた ぶん だけ は ついて 行く（とんだ か どうかの 見分け：前と 同じ）
    }
    check(ok1 && ok2 && !hows.boot && !hows.net, `オフライン・電源を 入れ直さない（boot ${boot ? 'あり' : 'なし'}・1万回）：iPhone の 時計を 300日 動かしても 本当の 時刻から 2秒 より ずれない・さがらない（いちばん ずれた ${worst}ms）`);
    console.log('     ', JSON.stringify(hows));
  }
  // ② オフライン・電源の 入れ直しも まぜる：本当の 時刻より 先に 行かない・さがらない。つながって たしかめたら 本当の 時刻
  for (const boot of ['B1', '']) {
    E = world({ boot }); await E.load(); let prev = E.C.now(), ok1 = true, ok2 = true, most = -Infinity, hows = {};
    for (let i = 0; i < 10000; i++) {
      const r = R();
      if (r < 0.40) E.pass(Math.floor(R() * 2 * HOUR));
      else if (r < 0.50) E.off += Math.floor((R() - 0.5) * 60 * DAY);
      else if (r < 0.60) E.off += Math.floor((R() - 0.5) * 18 * MIN);
      else if (r < 0.70) E.off = 0;
      else if (r < 0.72) { E.reboot(Math.floor(R() * DAY), Math.floor(R() * 3 * HOUR) + MIN); await E.load(); }
      else if (r < 0.80) await E.reopen();
      else await E.C.sync();
      const h = E.C.how(); hows[h] = (hows[h] || 0) + 1;
      const t = E.C.now();
      if (t < prev) ok1 = false; prev = t;
      most = Math.max(most, t - E.real); if (t - E.real > 2005) ok2 = false;
    }
    check(ok1 && ok2 && hows.boot > 50, `オフライン・入れ直しも まぜる（boot ${boot ? 'あり' : 'なし'}・1万回・入れ直し ${hows.boot}回）：本当の 時刻より 先に 行かない・さがらない（いちばん 先 ${most}ms）`);
    E.online = true; E.off = 0; E.pass(6 * MIN); await E.settle();
    check(E.C.how() === 'net' && near(E.C.now(), E.real, 2005) && E.C.sure(), `…その あと つながったら 本当の 時刻（おくれて いた ぶんを 追いつく）`);
    console.log('     ', JSON.stringify(hows));
  }
  // ③ つながったり 切れたり：たしかめた（sure）あいだは 本当の 時刻と 同じ・いつでも 先に 行かない・さがらない
  for (const boot of ['B1', '']) {
    E = world({ boot, online: true }); await E.load(); await E.settle(); let prev = E.C.now(), ok1 = true, ok2 = true, ok3 = true, sureN = 0, hows = {};
    for (let i = 0; i < 10000; i++) {
      const r = R();
      if (r < 0.35) E.pass(Math.floor(R() * 2 * HOUR));
      else if (r < 0.45) E.off += Math.floor((R() - 0.5) * 60 * DAY);
      else if (r < 0.55) E.off = 0;
      else if (r < 0.60) E.online = !E.online;
      else if (r < 0.63) { E.reboot(Math.floor(R() * DAY), Math.floor(R() * 3 * HOUR) + MIN); await E.load(); await E.settle(); }
      else if (r < 0.72) { await E.reopen(); await E.settle(); }
      else { E.pass(61000); await E.settle(); }
      const h = E.C.how(); hows[h] = (hows[h] || 0) + 1;
      const t = E.C.now();
      if (t < prev) ok1 = false; prev = t;
      if (t - E.real > 2005) ok2 = false;
      if (E.C.sure()) { sureN++; if (Math.abs(t - E.real) > 2005) ok3 = false; }
    }
    check(ok1 && ok2 && ok3 && sureN > 1000 && hows.net > 50, `つながったり 切れたり（boot ${boot ? 'あり' : 'なし'}・1万回）：先に 行かない・さがらない・たしかめた あいだ（${sureN}回）は 本当の 時刻と 同じ`);
    console.log('     ', JSON.stringify(hows));
  }

  console.log(`\n結果：${n - bad}/${n} OK`);
  process.exit(bad ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
