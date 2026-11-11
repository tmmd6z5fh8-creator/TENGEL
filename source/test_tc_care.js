// トレーニングセンターの お世話の きまり（tc/tc_care.js）を 画面なしで ためす（第4.151版・まさちゃん 2026/11/11 09:07・09:45）
//   node test_tc_care.js
//   ・撫でる：つづけて 5回まで → 5回目が おわったら 7秒 できない（さわっても・ボタンを 押しても「あと N秒」）→ 7秒で また できる・7秒 あけたら 数え直し
//   ・つづけて 撫でた とき：前の 反応を 止める（cut）・前の 回の あとの 動き（はしゃぐ）は 出ない
//   ・ハート 10こ → 抽選は 反応が おわって から・はしゃぐ は 出ない・ごろんの ときに のこった 反応は ぜんぶ 止めて ある
//   ・呼ぶ：つづけて 5回まで → 5回目が おわったら 7秒 できない
//   ・早く 始まる：撫でる・ごはんは 歩かないで その場で 横向きに（急ぎ足 hurry）・カメラは 押した ときから 寄る・仕上げの ズームは 待たない
//     呼ぶ（近づく・甘える）は いちばん 手前まで 歩かない・着いたら 急ぎ足を もどす
//   ・おそうじの あと：お花も キラッ も 出さない・くんくんの 間に ボタンを 押すと すぐ 次の お世話
// 馬（TCHorse）と 馬の 動き（step）は にせもの：場所と 向き だけ
const fs = require('fs'), path = require('path');
const ctx = new Proxy({}, { get: (t, k) => k === 'canvas' ? { width: 1052, height: 1657, parentNode: null } : (k in t ? t[k] : () => ({ addColorStop() { } })), set: (t, k, v) => { t[k] = v; return true; } });
global.window = {}; global.document = { createElement: () => ({ getContext: () => ctx, width: 0, height: 0 }), fonts: { load: async () => { } } };
global.Image = class { decode() { return Promise.resolve(); } set src(v) { } get naturalWidth() { return 0; } };
const MARK = { nose: [0.9, -0.95], eye: [0.75, -1.1], poll: [0.6, -1.25], neck: [0.4, -1.1], withers: [0.2, -1.0], back: [-0.1, -0.98], rump: [-0.5, -0.95] };
const BR = { x: 526, y: 900, dir: 0, mode: 'idle', until: 0, want: { graze: 0, look: [0, 0] }, reacts: [], sl: 0, rise: 0, stand: false, poops: [] }, HO = {};
global.TCHorse = {
  where: (h, n) => { const m = MARK[n]; if (!m) return null; const f = Math.cos(BR.dir) >= 0 ? 1 : -1; return [BR.x + m[0] * 200 * f, BR.y + m[1] * 200]; },
  scaleAt: () => 200, extent: () => [BR.x - 200, BR.y - 300, BR.x + 200, BR.y], pose: () => ({}), wherePose: (h, m, n) => global.TCHorse.where(h, n), anchorPose: () => [0, 0, 0], project: () => [0, 0], unz: b => b, M: {}, draw() { },
  react: (st, k, dur, t, o) => { st.reacts = (st.reacts || []).filter(r => t - r.t0 < r.dur); st.reacts.push(Object.assign({ k, t0: t, dur }, o || {})); },
};
const TCCare = new Function(fs.readFileSync(path.join(__dirname, 'tc', 'tc_care.js'), 'utf8') + '; return TCCare;')();
let T = 100, ok = 0, ng = 0; const EV = [];
const check = (c, msg) => { if (c) { ok++; console.log('  ✅', msg); } else { ng++; console.log('  ❌', msg); } };
function stepBrain(t, dt) {
  if (BR.mode === 'walk' && BR.tgt) {
    const dx = BR.tgt[0] - BR.x, dy = BR.tgt[1] - BR.y, d = Math.hypot(dx, dy), v = 190 * (BR.hurry > 1 ? BR.hurry : 1) * dt;
    if (d <= Math.max(v, 28)) { BR.mode = 'idle'; BR.until = t + 5; } else { BR.x += dx / d * v; BR.y += dy / d * v; BR.dir = Math.atan2(dy / 0.5, dx); }
  } else if (BR.mode === 'turn') { BR.dir = BR.turnTo; BR.mode = 'idle'; }
  else if (BR.mode === 'sleep') {
    if (BR.sl < 1) BR.sl = Math.min(1, BR.sl + dt / (BR.lieDur || 4.6));
    else if (t >= BR.until - 1.7) { BR.rise = Math.min(1, (BR.rise || 0) + dt / 1.7); if (BR.rise >= 1) { BR.mode = 'idle'; BR.sl = 0; BR.rise = 0; BR.flop = null; } }
  }
}
const run = sec => { for (let n = Math.max(1, Math.round(sec * 60)); n > 0; n--) { T += 1 / 60; stepBrain(T, 1 / 60); TCCare.pre(T, 1 / 60); } };
const until = (fn, max) => { const t0 = T; while (!fn() && T - t0 < (max || 40)) run(1 / 60); return fn(); };
const S = TCCare.S, evs = (k, from) => EV.filter(e => e.k === k && e.t >= (from == null ? -1 : from) - 1e-6);
function pet(zone) {          // 3回 なでる ＝ 撫でる 1回
  const A = zone === 'back' ? 'back' : 'poll', B = zone === 'back' ? 'rump' : 'withers';
  for (let k = 0; k < 3; k++) {
    const a = TCHorse.where(HO, A), b = TCHorse.where(HO, B);
    TCCare.input('down', a[0], a[1], T);
    for (let i = 1; i <= 8; i++) { run(1 / 60); TCCare.input('move', a[0] + (b[0] - a[0]) * i / 8, a[1] + (b[1] - a[1]) * i / 8, T); }
    TCCare.input('up', b[0], b[1], T); run(0.04);
  }
}
(async () => {
  await TCCare.init({ canvas: { getContext: () => ctx }, horse: HO, brain: BR, rnd: () => 0.5, tod: 'morning', stageNo: 1, props: false, onEvent: e => EV.push(e) });
  S.stock = S.stockShow = 9; run(0.5);
  console.log('撫でる');
  let t0 = T; TCCare.pressPet(T);      // 馬は 奥（y 900）で 右向き（横向き）
  check(S.phase === 'zoomin' && S.zDur === 0.5 && BR.mode === 'idle' && BR.y === 900 && BR.x === 526, '撫でる を 押す：横向きで 立って いる → 歩かないで すぐ ズーム（0.5秒・奥に いても その場）');
  check(until(() => S.phase === 'pet', 5) && T - t0 < 0.6, `押して から 撫でられる まで ${(T - t0).toFixed(2)}秒`);
  const h0 = S.heart;
  for (let i = 0; i < 4; i++) { pet(); if (i === 0) run(0.3); }
  check(S.heart === h0 + 4 && T >= S.coolUntil && S.petN === 4 && !evs('wait').length, 'つづけて 4回：まだ 止まらない（ハート ＋4）');
  check(BR.reacts.filter(r => r.cut != null).length >= 3 && BR.reacts.filter(r => r.cut == null && T < r.t0 + r.dur).length <= 1 && evs('frisk').length === 0, 'つづけて 撫でた：前の 反応は 止める・前の 回の「はしゃぐ」は 出ない');
  pet(); const t5 = T;
  check(S.heart === h0 + 5 && Math.abs(S.coolUntil - t5 - 7) < 0.4 && S.petN === 0, `5回目 → 7秒 できない（あと ${(S.coolUntil - T).toFixed(1)}秒）`);
  run(0.3); const sesBefore = S.ses; { const a = TCHorse.where(HO, 'poll'); TCCare.input('down', a[0], a[1], T); TCCare.input('up', a[0], a[1], T); }
  check(S.ses === sesBefore && evs('wait', t5).length === 1 && S.heart === h0 + 5, '7秒の 間に さわっても 撫でられない（「あと N秒」）');
  until(() => S.phase === 'idle', 15);
  if (T < S.coolUntil) { const w = evs('wait').length; TCCare.pressPet(T); check(S.phase === 'idle' && evs('wait').length === w + 1, '7秒の 間に ボタンを 押しても 始まらない（「あと N秒」）'); }
  else check(false, `7秒の 間に 画面が もどらない（もどった 時刻 ${(T - t5).toFixed(1)}秒後）`);
  until(() => T >= S.coolUntil + 0.1, 10); check(evs('ready', t5).length === 1, '7秒 たったら 知らせる（ready）');
  TCCare.pressPet(T); check(until(() => S.phase === 'pet', 6), '7秒 たったら また 撫でられる');
  S.got = []; S.heart = S.heartShow = 0; pet(); pet(); check(S.petN === 2 && T >= S.coolUntil, '2回 撫でて やめる');      // ハートは 0 から（10こで 抽選に ならない ように）
  until(() => S.phase === 'idle', 20); run(7.5); TCCare.pressPet(T); until(() => S.phase === 'pet', 6);
  for (let i = 0; i < 4; i++) pet();
  check(S.petN === 4 && T >= S.coolUntil, `7秒 あけたら 数え直し（2回 → 休み → 4回 でも 止まらない）［petN ${S.petN}・phase ${S.phase}・あと ${(S.coolUntil - T).toFixed(1)}］`);
  pet(); check(T < S.coolUntil, 'そこから 5回目で 止まる');
  until(() => S.phase === 'idle', 20); until(() => T >= S.coolUntil + 0.2, 10);
  console.log('ハート 10こ → 抽選（ごろん）');
  S.got = []; S.heart = S.heartShow = 9; TCCare.pressPet(T); until(() => S.phase === 'pet', 6);
  pet('back'); const tc = T, f0 = evs('frisk').length;
  check(S.busy && S.heart === 10, '10こ目の ハート → 抽選を 予約');
  until(() => evs('max', tc).length > 0, 12); const tm = T;
  check(tm - tc >= 4.6 - 0.3, `抽選は 反応（のび 4.6秒）が おわって から（${(tm - tc).toFixed(2)}秒後。前は 1.45秒後）`);
  until(() => BR.mode === 'sleep', 6);
  check(BR.mode === 'sleep' && BR.flop != null && BR.reacts.every(r => r.cut != null || T >= r.t0 + r.dur || r.k === 'gather') && evs('frisk').length === f0, 'ごろんの とき：のこった 反応は 止めて ある・はしゃぐ は 出ない');
  until(() => S.phase === 'idle' && !S.busy && BR.mode !== 'sleep', 30); check(S.phase === 'idle' && S.heart === 0, 'ごろんの あと もとに もどる（ハートは 0 から）');
  console.log('呼ぶ');
  until(() => T >= S.coolUntil + 0.2, 10);
  let rel = 0;
  for (let i = 0; i < 5; i++) { TCCare.pressCall(T, 'turn'); check(S.mode === 'call', `呼ぶ ${i + 1}回目は できる`); until(() => S.phase === 'idle', 20); rel = T; if (i < 4) run(0.2); }
  check(Math.abs(S.callCoolUntil - rel - 7) < 0.3 && S.callN === 0, `5回目が おわったら 7秒 できない（あと ${(S.callCoolUntil - T).toFixed(1)}秒）`);
  { const w = evs('wait').length; TCCare.pressCall(T, 'turn'); check(S.phase === 'idle' && S.mode == null && evs('wait').length === w + 1, '7秒の 間は 呼べない（「あと N秒」）'); }
  until(() => T >= S.callCoolUntil + 0.1, 10); TCCare.pressCall(T, 'come'); check(S.mode === 'call' && BR.hurry === 2.8, '7秒 たったら また 呼べる（近づく ときは 急ぎ足）'); until(() => S.phase === 'idle', 20);
  run(7.5); TCCare.pressCall(T, 'turn'); until(() => S.phase === 'idle', 20); check(S.callN === 1, '7秒 あけたら 数え直し');
  console.log('おそうじ');
  BR.poops = [{ x: 600, y: 1200, img: 0, w: 0.42 }]; const st0 = S.stock, tk = T;
  TCCare.press(T, 'clean'); check(S.phase === 'zoomin' && S.zDur === 0.5 && S.stock === st0 - 1, 'おそうじ：ズーム 0.5秒');
  until(() => S.phase === 'clean', 3);
  for (let k = 0; k < 3; k++) { const C = S.clean; TCCare.input('down', C.x + 60, C.y, T); for (let i = 1; i <= 6; i++) { run(1 / 60); TCCare.input('move', C.x + 60 - i * 12, C.y, T); } TCCare.input('up', C.x - 12, C.y, T); run(0.1); }
  until(() => S.phase === 'after' || S.phase === 'idle', 12);
  check(evs('kira', tk).length === 1 && !S.fx.some(f => f.k === 'kira') && !('flowersAt' in S) && !/flowerArt\(p\[0\]/.test(fs.readFileSync(path.join(__dirname, 'tc', 'tc_care.js'), 'utf8')), 'おそうじの あと：お花も 地面の キラッ も 出さない（音の 合図 だけ）');
  check(S.phase === 'after' && BR.mode === 'walk' && BR.hurry === 2.8, 'きれいに なった 所へ くんくん しに 行く（急ぎ足）');
  TCCare.press(T, 'feed'); check(S.phase === 'choose' && !!S.chooser && BR.hurry === 1, 'くんくんの 間に ごはんを 押す → すぐ えらぶ 札');
  TCCare.press(T, 'pick:apple'); const tp = T; until(() => S.phase === 'feed', 10);
  check(S.phase === 'feed' && T - tp < 3.2, `えらんで から 食べはじめる まで ${(T - tp).toFixed(2)}秒`);
  until(() => S.phase === 'idle', 30); check(S.phase === 'idle', 'ごはんの あと もとに もどる');
  console.log('早く 始まる（歩かない）');
  until(() => T >= S.coolUntil + 0.2, 10); S.got = []; S.heart = S.heartShow = 0;
  const z0 = evs('zoomin').length;
  Object.assign(BR, { x: 560, y: 820, dir: -Math.PI / 2, mode: 'walk', tgt: [560, 700] }); const tn = T; TCCare.pressPet(T);
  check(S.phase === 'approach' && BR.mode === 'idle' && BR.hurry === 2.8 && !!S.zB && S.zB.z > 1.5 && evs('zoomin').length === z0 + 1, '奥で むこう向きに 歩いて いる → 歩くのを やめて その場で 横向きに（急ぎ足 2.8倍）・カメラは 押した ときから 寄る');
  check(until(() => S.phase === 'pet', 5) && BR.x === 560 && BR.y === 820 && Math.abs(Math.sin(BR.dir)) < 0.4 && BR.hurry === 1 && evs('zoomin').length === z0 + 1, `その場で 横向きに なって すぐ 撫でられる（${(T - tn).toFixed(2)}秒・ズームの 仕上げは 待たない）`);
  check(!!S.zB && S.zDur === 0.25, 'ズームの 仕上げ（0.25秒）は 撫でられる ように なって から');
  run(0.4); check(!S.zB && S.phase === 'pet' && S.zoom.z > 1.5, '仕上げが おわっても 撫でる まま');
  until(() => S.phase === 'idle', 20); run(0.2);
  Object.assign(BR, { x: 120, y: 1200, dir: Math.PI / 2, mode: 'idle' }); TCCare.pressPet(T);
  check(S.phase === 'approach' && BR.mode === 'walk' && BR.tgt[0] === 1.8 * 200 + 12 && BR.tgt[1] === 1200 && !!S.zB, `横向きに なると 画面から はみ出す 所（x 120）→ 入る 所（x ${BR.tgt && BR.tgt[0]}）まで だけ 歩く`);
  until(() => S.phase === 'pet', 6); until(() => S.phase === 'idle', 20); run(0.2);
  S.stock = 5; Object.assign(BR, { x: 560, y: 820, dir: Math.PI / 2, mode: 'idle' }); TCCare.press(T, 'feed'); TCCare.press(T, 'pick:apple'); const tf = T;
  check(until(() => S.phase === 'feed', 5) && BR.y === 820 && T - tf < 1.0, `ごはん：えらんで から 食べはじめる まで ${(T - tf).toFixed(2)}秒（奥に いても その場）`);
  until(() => S.phase === 'idle', 30); run(0.2);
  Object.assign(BR, { x: 300, y: 700, dir: 0, mode: 'idle' }); TCCare.pressCall(T, 'come');
  check(BR.mode === 'walk' && BR.tgt[1] === 1040 && !S.zB && S.zoom.z === 1, `呼ぶ（近づく）：いちばん 手前（1372）まで 歩かない（行き先 y ${BR.tgt[1]}）・ズームは しない`);
  until(() => S.phase === 'idle', 20);
  Object.assign(BR, { x: 526, y: 1000, dir: 0, mode: 'idle' }); run(7.5); TCCare.pressCall(T, 'amae');
  check(BR.mode === 'walk' && BR.tgt[1] === 1230, `呼ぶ（甘える）：いまの 所から 230 だけ 手前（行き先 y ${BR.tgt[1]}）`);
  until(() => S.phase === 'idle', 20);
  console.log(`\n${ok} OK / ${ng} NG`); process.exit(ng ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
