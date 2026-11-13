// トレーニングセンターの お世話の きまり（tc/tc_care.js）を 画面なしで ためす（第4.151版・まさちゃん 2026/11/11 09:07・09:45）
//   node test_tc_care.js
//   ・撫でる：つづけて 5回まで → 5回目が おわったら 7秒 できない（さわっても・ボタンを 押しても「あと N秒」）→ 7秒で また できる・7秒 あけたら 数え直し
//   ・つづけて 撫でた とき：前の 反応を 止める（cut）・前の 回の あとの 動き（はしゃぐ）は 出ない
//   ・ハート 10こ → 抽選は 反応が おわって から・はしゃぐ は 出ない・ハズレの ときに のこった 反応は ぜんぶ 止めて ある
//   ・第4.156版（まさちゃん 2026/11/12 04:20「トレーニングセンターの馬の寝転ぶ演出は全部消して！」）：ハズレは ふぅ〜（ためいき）・夜に 撫でても あくび だけ ＝ 馬は 横に ならない（mode 'sleep'・ごろんの 音は 出ない）
//   ・呼ぶ：つづけて 5回まで → 5回目が おわったら 7秒 できない
//   ・早く 始まる：撫でる・ごはんは 歩かないで その場で 横向きに（急ぎ足 hurry）・カメラは 押した ときから 寄る・仕上げの ズームは 待たない
//     呼ぶ（近づく・甘える）は いちばん 手前まで 歩かない・着いたら 急ぎ足を もどす
//   ・おそうじ（第4.152版）：ゴミ（BR.trash）か うんちが ある とき だけ・1回で ぜんぶ・ほうきで 山を 押して ちりとりの 口へ・さわらない まま 25秒で のこりも 片付く
//     第4.165版（まさちゃん 2026/11/13 12:59「ほうきと、ちりとりも自由に動かして、ゴミのところまで持っていってほうきで片付けられるようにして！今は、触れると瞬間移動しちゃう！」）：
//       ほうきも ちりとりも つかんで 運ぶ（つかんだ 瞬間に 動かない・道具の ない 所を さわっても 飛ばない）・ちりとりは 置いた 所に いる（口 だけ 山の 方へ 向く）・ちりとりを かぶせる だけでは 片付かない
//     おそうじの あと：お花も キラッ も 出さない・くんくんの 間に ボタンを 押すと すぐ 次の お世話
//   ・第4.159版（まさちゃん 2026/11/12 10:37「①お世話の最大トークン25回にして！②お世話が終わったあとに、pushボタンが出てくるようにして…③…1個使う、か、…まとめて使う、が選べるようにして」）：
//     トークンの 上限 25・お世話の はじめには トークンを 使わない（1つ 以上 いる）・おわったら PUSH・押した 瞬間に −1 と 抽選と 結果
//     （ハズレ＝プフォの 音 だけ／10〜100P＝ピロン／200〜300P＝デデーン／ルーレット＝キュインキュイーン → 1秒 あとに 演出／チケット＝すぐ 演出）・
//     1個 使う＝1回で 消える／まとめて 使う＝トークンが ある 間 つづけて 押せる（押した 回数ぶん 減る）・おわる は 1回 押した あと・PUSH の 間は ほかの お世話は できない
//   ・第4.159版（11/12 12:48・13:27）：トークンが 25（最大）の ときに「撫でる」→ 札／ハートの 抽選は トークンが 20こ未満の とき だけ（20こ以上は 待つ → 20こを 切ったら ひとりでに 抽選）
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
  if (BR.mode === 'sleep' || BR.flop != null || BR.sl > 0) LAY++;      // 第4.156版：お世話が 馬を 横に する ことは もう ない（1コマでも あれば 数える）
}
let LAY = 0;
const run = sec => { for (let n = Math.max(1, Math.round(sec * 60)); n > 0; n--) { T += 1 / 60; stepBrain(T, 1 / 60); TCCare.pre(T, 1 / 60); } };
const until = (fn, max) => { const t0 = T; while (!fn() && T - t0 < (max || 40)) run(1 / 60); return fn(); };
const S = TCCare.S, evs = (k, from) => EV.filter(e => e.k === k && e.t >= (from == null ? -1 : from) - 1e-6);
// 第4.159版：ごはん・おそうじの あとは PUSH が 出る（押す まで ほかの お世話は できない）→ 前から ある 確かめでは 1回 押して 片付けて から 次へ
const pushLive = () => !!(S.push && S.push.hideT == null);
function clearPush() { if (pushLive()) { run(0.3); TCCare.pushPress(T); run(0.5); } }
const idle = max => { const r = until(() => S.phase === 'idle', max); clearPush(); return r; };
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
  let RND = 0.5;
  await TCCare.init({ canvas: { getContext: () => ctx }, horse: HO, brain: BR, rnd: () => RND, tod: 'morning', stageNo: 1, props: false, onEvent: e => EV.push(e) });
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
  idle(15);
  if (T < S.coolUntil) { const w = evs('wait').length; TCCare.pressPet(T); check(S.phase === 'idle' && evs('wait').length === w + 1, '7秒の 間に ボタンを 押しても 始まらない（「あと N秒」）'); }
  else check(false, `7秒の 間に 画面が もどらない（もどった 時刻 ${(T - t5).toFixed(1)}秒後）`);
  until(() => T >= S.coolUntil + 0.1, 10); check(evs('ready', t5).length === 1, '7秒 たったら 知らせる（ready）');
  TCCare.pressPet(T); check(until(() => S.phase === 'pet', 6), '7秒 たったら また 撫でられる');
  S.got = []; S.heart = S.heartShow = 0; pet(); pet(); check(S.petN === 2 && T >= S.coolUntil, '2回 撫でて やめる');      // ハートは 0 から（10こで 抽選に ならない ように）
  idle(20); run(7.5); TCCare.pressPet(T); until(() => S.phase === 'pet', 6);
  for (let i = 0; i < 4; i++) pet();
  check(S.petN === 4 && T >= S.coolUntil, `7秒 あけたら 数え直し（2回 → 休み → 4回 でも 止まらない）［petN ${S.petN}・phase ${S.phase}・あと ${(S.coolUntil - T).toFixed(1)}］`);
  pet(); check(T < S.coolUntil, 'そこから 5回目で 止まる');
  idle(20); until(() => T >= S.coolUntil + 0.2, 10);
  console.log('ハート 10こ → 抽選（ハズレ：ふぅ〜）');
  S.got = []; S.heart = S.heartShow = 9; TCCare.pressPet(T); until(() => S.phase === 'pet', 6);
  pet('back'); const tc = T, f0 = evs('frisk').length;
  check(S.busy && S.heart === 10, '10こ目の ハート → 抽選を 予約');
  until(() => evs('max', tc).length > 0, 12); const tm = T;
  check(tm - tc >= 4.6 - 0.3, `抽選は 反応（のび 4.6秒）が おわって から（${(tm - tc).toFixed(2)}秒後。前は 1.45秒後）`);
  until(() => evs('calm', tm).length > 0, 6); const tfu = T;
  check(evs('calm', tm).length === 1 && Math.abs(tfu - tm - 1.7) < 0.2 && BR.reacts.some(r => r.k === 'calm' && r.cut == null), `ハズレ → ふぅ〜（ためいき：抽選の ${(tfu - tm).toFixed(2)}秒後・立った まま）`);
  check(BR.reacts.every(r => r.cut != null || T >= r.t0 + r.dur || r.k === 'gather' || r.k === 'calm') && evs('frisk').length === f0, 'ハズレの とき：のこった 反応は 止めて ある・はしゃぐ は 出ない');
  until(() => S.phase === 'idle' && !S.busy, 30);
  check(S.phase === 'idle' && S.heart === 0 && T - tm < 6.5, `ふぅ〜の あと もとに もどる（ハートは 0 から・抽選から ${(T - tm).toFixed(1)}秒。前の ごろんは 約8秒）`);
  check(LAY === 0 && BR.mode !== 'sleep' && !['flop', 'goron', 'lie'].some(k => evs(k).length), '馬は 横に ならない（ごろん・横に なる 音の できごとは 出ない）');
  console.log('呼ぶ');
  until(() => T >= S.coolUntil + 0.2, 10);
  let rel = 0;
  for (let i = 0; i < 5; i++) { TCCare.pressCall(T, 'turn'); check(S.mode === 'call', `呼ぶ ${i + 1}回目は できる`); idle(20); rel = T; if (i < 4) run(0.2); }
  check(Math.abs(S.callCoolUntil - rel - 7) < 0.3 && S.callN === 0, `5回目が おわったら 7秒 できない（あと ${(S.callCoolUntil - T).toFixed(1)}秒）`);
  { const w = evs('wait').length; TCCare.pressCall(T, 'turn'); check(S.phase === 'idle' && S.mode == null && evs('wait').length === w + 1, '7秒の 間は 呼べない（「あと N秒」）'); }
  until(() => T >= S.callCoolUntil + 0.1, 10); TCCare.pressCall(T, 'come'); check(S.mode === 'call' && BR.hurry === 2.8, '7秒 たったら また 呼べる（近づく ときは 急ぎ足）'); idle(20);
  run(7.5); TCCare.pressCall(T, 'turn'); idle(20); check(S.callN === 1, '7秒 あけたら 数え直し');
  console.log('おそうじ（第4.152版：ゴミか うんちが ある とき だけ・ほうきで ちりとりへ）');
  const SRC = fs.readFileSync(path.join(__dirname, 'tc', 'tc_care.js'), 'utf8');
  // 第4.165版：道具は つかんで 運ぶ。指を from から to へ n コマで 動かす（stop が 真に なったら そこで 止める）→ さいごの 指の 場所
  const drag = (from, to, n, stop) => { let p = from; for (let i = 1; i <= n && !(stop && stop()); i++) { run(1 / 60); p = [from[0] + (to[0] - from[0]) * i / n, from[1] + (to[1] - from[1]) * i / n]; TCCare.input('move', p[0], p[1], T); } return p; };
  const sweepTo = Tg => {      // ほうきの 毛の 先を つかむ → 山の むこうがわ（ちりとりの 反対）へ 運ぶ → 山を 通って ちりとりの 口まで 押す → はなす
    const C = S.clean, o = Tg.o, pn = { x: C.pan.x, y: C.pan.y }, ux = o.x - pn.x, uy = o.y - pn.y, L = Math.hypot(ux, uy) || 1, far = [o.x + ux / L * 140, o.y + uy / L * 70];
    const b0 = [C.bro.x, C.bro.y]; TCCare.input('down', b0[0], b0[1], T);
    const p1 = drag(b0, far, 20), p2 = drag(p1, [pn.x, pn.y], 36, () => Tg.done);
    TCCare.input('up', p2[0], p2[1], T); run(0.05); return pn;
  };
  const movePan = (x, y) => { const C = S.clean, a = [C.pan.x, C.pan.y]; TCCare.input('down', a[0], a[1], T); const p = drag(a, [x, y], 16); TCCare.input('up', p[0], p[1], T); run(0.3); };      // ちりとりを つかんで (x, y) へ 運ぶ
  const pile = (x, y, i) => ({ x, y, sd: i, items: [{ k: i % 4, dx: 0, dy: 0, r: 0, w: 0.4, d: 0 }] });
  idle(30);
  BR.poops = []; BR.trash = []; S.trashIn = 620; let st0 = S.stock, w0 = evs('wait').length;
  TCCare.press(T, 'clean');
  check(S.phase === 'idle' && S.mode == null && S.stock === st0 && evs('wait').length === w0 + 1 && S.fx.some(f => f.k === 'tagUI' && f.txt === 'ゴミは あと 11分で 出るよ'), 'ゴミも うんちも ない → おそうじ できない（「ゴミは あと 11分で 出るよ」・トークンは 使わない）');
  BR.poops = [{ x: 600, y: 1200, img: 0, w: 0.42 }]; let tk = T;
  TCCare.press(T, 'clean'); check(S.mode === 'clean' && S.stock === st0 && BR.poops[0].sw === true && !BR.trashDone, 'うんちが ある → おそうじ できる（トークンは まだ 使わない：おわった あとの PUSH で）');
  until(() => S.phase === 'clean', 3);
  { const C = S.clean; check(S.zDur === 0.5 && S.zoom.z > 1.3 && C.tg.length === 1 && C.pan.x < 600 - 100 && Math.abs(C.pan.y - 1200) < 30, `うんち 1つ：カメラが 寄る（${S.zoom.z.toFixed(2)}倍・0.5秒）・ちりとりは うんちの 左`);
    // 第4.165版：道具の ない 所を さわっても 何も 飛ばない（前は ほうきが 指の 所へ 一瞬で 飛んで、ちりとりも 回りこんで いた）
    run(0.3); const b0 = [C.bro.x, C.bro.y], p0 = [C.pan.x, C.pan.y, C.pan.yaw], w0 = evs('wait').length;
    TCCare.input('down', 700, 840, T); drag([700, 840], [760, 900], 8); const g0 = C.grab, hint = S.fx.some(f => f.k === 'tag' && f.txt === 'ほうきか ちりとりを つかんでね'); TCCare.input('up', 760, 900, T); run(0.3);
    check(g0 == null && C.bro.x === b0[0] && C.bro.y === b0[1] && C.pan.x === p0[0] && C.pan.y === p0[1] && C.pan.yaw === p0[2] && hint && evs('wait').length === w0 + 1 && TCCare.grabAt(700, 840) === null,
      `道具の ない 所を さわる → ほうきも ちりとりも 動かない（瞬間移動 しない）・札「ほうきか ちりとりを つかんでね」（ほうき ${b0.map(Math.round)}・ちりとり ${p0.slice(0, 2).map(Math.round)}）`);
    // ほうきの 柄を つかむ → つかんだ 瞬間は 動かない → 指と 同じ だけ 動く
    TCCare.input('down', b0[0] - 8, b0[1] - 150, T); const g1 = C.grab, b1 = [C.bro.x, C.bro.y]; drag([b0[0] - 8, b0[1] - 150], [b0[0] + 42, b0[1] - 130], 6); const b2 = [C.bro.x, C.bro.y]; TCCare.input('up', b0[0] + 42, b0[1] - 130, T);
    check(g1 === 'broom' && b1[0] === b0[0] && b1[1] === b0[1] && Math.abs(b2[0] - b0[0] - 50) < 1e-6 && Math.abs(b2[1] - b0[1] - 20) < 1e-6 && C.grab == null && TCCare.grabAt(b2[0] + 300, b2[1]) === null && TCCare.grabAt(b2[0], b2[1] - 60) === 'broom' && TCCare.grabAt(b2[0], b2[1] - 0.86 * 1.35 * 200 + 10) === 'broom',
      `ほうきの 柄を つかむ → つかんだ 瞬間は 動かない・指が (＋50, ＋20) 動くと ほうきも (＋50, ＋20)（${b2.map(Math.round)}）・毛の 先から 柄の 先まで どこでも つかめる・はなれた 所は つかめない`);
    TCCare.input('down', b2[0], b2[1], T); drag(b2, b0, 6); TCCare.input('up', b0[0], b0[1], T);      // もとの 所へ もどす
    // ちりとりを つかむ → 指と 同じ だけ 動く（おくれない）・フィールドの 外へは 出ない・口は うんちの 方を 向く・かぶせても 片付かない
    TCCare.input('down', p0[0] + 20, p0[1] + 10, T); const g2 = C.grab; drag([p0[0] + 20, p0[1] + 10], [p0[0] + 20, p0[1] - 190], 8); const q1 = { x: C.pan.x, y: C.pan.y };
    drag([p0[0] + 20, p0[1] - 190], [-300, 300], 8); const q2 = { x: C.pan.x, y: C.pan.y };
    drag([-300, 300], [600 + 20, 1200 + 10], 12); const q3 = { x: C.pan.x, y: C.pan.y }; TCCare.input('up', 620, 1210, T); run(0.3);
    check(g2 === 'pan' && Math.abs(q1.x - p0[0]) < 1e-6 && Math.abs(q1.y - (p0[1] - 200)) < 1e-6 && q2.x === 90 && q2.y === 790 && Math.abs(q3.x - 600) < 1e-6 && Math.abs(q3.y - 1200) < 1e-6 && !C.tg[0].done && S.phase === 'clean' && evs('inpan', tk).length === 0,
      `ちりとりを つかんで 運ぶ：指と 同じ だけ 動く（上へ 200）・フィールドの 外へは 出ない（${q2.x}, ${q2.y}）・うんちに かぶせても 片付かない（ほうきで はく）`);
    movePan(p0[0], p0[1]); const yw = C.pan.yaw, want = Math.atan2(-(1200 - C.pan.y) * 2, 600 - C.pan.x);
    check(Math.abs(C.pan.x - p0[0]) < 1e-6 && Math.abs(C.pan.y - p0[1]) < 1e-6 && Math.abs(yw - want) < 0.05, `もとの 所へ もどす → 口は うんちの 方を 向く（向き ${yw.toFixed(2)}）`);
    sweepTo(C.tg[0]);
    check(C.tg[0].done && BR.poops.length === 0 && evs('inpan', tk).length === 1 && evs('sweep', tk).length === 1 && S.phase === 'cleanwait', 'ほうきを つかんで うんちを 押して ちりとりの 口へ → 片付く（1回 なぞる）'); }
  until(() => S.phase === 'after' || S.phase === 'idle', 12);
  check(evs('kira', tk).length === 1 && !S.fx.some(f => f.k === 'kira') && !('flowersAt' in S) && !/flowerArt\(p\[0\]/.test(SRC), 'おそうじの あと：お花も 地面の キラッ も 出さない（音の 合図 だけ）');
  check(S.phase === 'after' && BR.mode === 'walk' && BR.hurry === 2.8, 'うんちを 片付けた 所へ くんくん しに 行く（急ぎ足）');
  { const w1 = evs('wait').length; TCCare.press(T, 'feed');
    check(pushLive() && S.phase === 'after' && !S.chooser && evs('wait').length === w1 + 1 && S.fx.some(f => f.k === 'tagUI' && f.txt === '先に PUSH を 押してね'), 'おそうじが おわった → PUSH が 出て いる 間は ほかの お世話は できない（「先に PUSH を 押してね」）');
    run(0.3); const s1 = S.stock, k1 = evs('token').length; const pr = TCCare.pushPress(T);
    check(pr === true && S.stock === s1 - 1 && evs('token').length === k1 + 1 && !pushLive() && S.phase === 'after', 'PUSH を 押す → トークン −1（お世話 1回）・1個 使う なら PUSH は すぐ 消える'); }
  TCCare.press(T, 'feed'); check(S.phase === 'choose' && !!S.chooser && BR.hurry === 1, 'くんくんの 間に ごはんを 押す → すぐ えらぶ 札');
  TCCare.press(T, 'pick:apple'); const tp = T; until(() => S.phase === 'feed', 10);
  check(S.phase === 'feed' && T - tp < 3.2, `えらんで から 食べはじめる まで ${(T - tp).toFixed(2)}秒`);
  idle(30); check(S.phase === 'idle', 'ごはんの あと もとに もどる');
  console.log('ゴミ 5か所 ＋ 金のうんち');
  S.stock = S.stockShow = 6; BR.trash = [[300, 1000], [760, 980], [520, 1160], [250, 1290], [800, 1300]].map(([x, y], i) => pile(x, y, i)); BR.poops = [{ x: 430, y: 1240, img: 1, w: 0.5, gold: true }];
  S.high = 0; tk = T; TCCare.press(T, 'clean');
  check(S.mode === 'clean' && BR.trashDone === true && S.clean.tg.length === 6 && S.stock === 6, 'ゴミ 5か所と うんちを 1回で ぜんぶ：押した ときに「片付けた」しるし（次の 15分が 始まる）・トークンは まだ 使わない');
  until(() => S.phase === 'clean', 3);
  { const C = S.clean; check(S.zoom.z < 1.25, `フィールド ぜんぶが 入る（ズーム ${S.zoom.z.toFixed(2)}倍）`);
    const pan0 = [C.pan.x, C.pan.y]; let n = 0, moved = 0;
    while (C.tg.some(q => !q.done) && n < 12) { const g0 = C.got; sweepTo(C.tg.find(q => !q.done)); n++; if (Math.abs(C.pan.x - pan0[0]) > 1e-6 || Math.abs(C.pan.y - pan0[1]) > 1e-6) moved++; if (C.got === g0) break; }      // 第4.165版：ちりとりは 置いた 所の まま → 山を ほうきで そこまで 押して いく（通り道の 山も いっしょに 押される）
    check(C.tg.every(q => q.done) && C.got === 6 && n <= 6 && evs('inpan', tk).length === 6 && evs('sweep', tk).length === 6 && moved === 0, `6つ とも ほうきで 押して ちりとりへ（${n}回 なぞって ${C.got}こ）・ちりとりは ひとりでに 動かない（置いた 所の まま）`);
    check(S.phase === 'cleanwait' && C.foldT == null, 'ぜんぶ 入った → おしまいの 合図を 待つ');
    run(0.5); check(BR.trash.length === 0 && BR.poops.length === 0 && C.foldT != null, 'ゴミは 消えて、道具を たたむ'); }
  until(() => S.phase === 'after' || S.phase === 'idle', 12);
  check(evs('luck', tk).length === 1 && S.high === 5 && evs('kira', tk).length === 1, '金のうんち → 運がついた（高確ゾーン 5回）');
  idle(30); BR.trashDone = false;
  TCCare.press(T, 'clean'); check(S.phase === 'idle' && S.mode == null && S.stock === 5, 'つづけては できない（片付ける ものが ない）・前の おそうじの PUSH で トークンは 1つ 減って いる（6 → 5）');
  console.log('とちゅうで さわらない → のこりを 片付けて おしまい');
  BR.trash = [pile(300, 1000, 0), pile(700, 1200, 1)]; BR.poops = []; tk = T; TCCare.press(T, 'clean'); until(() => S.phase === 'clean', 3);
  sweepTo(S.clean.tg[1]); check(S.clean.got === 1 && S.clean.tg[1].done && !S.clean.tg[0].touched && S.phase === 'clean', '1つ（ちりとりの となりの 山）を 片付けて 手を 止める');
  run(24.5); check(S.phase === 'clean' && S.clean.got === 1, '25秒 までは 待つ');
  run(1.2); check(S.phase === 'cleanwait' && S.clean.got === 2, '25秒 さわらない → のこりも ちりとりへ（とまった まま に ならない）');
  idle(30); BR.trashDone = false;
  console.log('はしの 山・馬が かわる');
  BR.trash = [pile(70, 800, 0)]; TCCare.press(T, 'clean'); until(() => S.phase === 'clean', 3);
  { const C = S.clean, q = C.pan; check(q.x >= 90 && q.x <= 1052 - 90 && q.y >= 790 && q.y <= 1430, `はしの 山でも ちりとりは フィールドの 中（${Math.round(q.x)}, ${Math.round(q.y)}）`);
    sweepTo(C.tg[0]);      // ほうきを 外がわ（はし）へ 運んで 内へ はく（ほうきの 先は フィールドの はしで 止まる）
    check(C.tg[0].done && C.bro.x >= 40 && C.bro.y >= 770, `はしの 山も 片付く（ほうきの 先 ${Math.round(C.bro.x)}, ${Math.round(C.bro.y)}）`); }
  idle(30); BR.trashDone = false;
  BR.trash = [pile(300, 1000, 0), pile(700, 1200, 1)]; BR.poops = [{ x: 500, y: 1100, img: 0, w: 0.4 }]; TCCare.press(T, 'clean'); until(() => S.phase === 'clean', 3);
  TCCare.setHorse(HO, BR); check(S.phase === 'idle' && !S.clean && BR.trash.length === 0 && BR.poops.length === 0, 'おそうじの 途中で 馬が かわる（育つ）→ その 回の ゴミ・うんちは のこらない');
  BR.trashDone = false; S.stock = S.stockShow = 9;
  console.log('早く 始まる（歩かない）');
  until(() => T >= S.coolUntil + 0.2, 10); S.got = []; S.heart = S.heartShow = 0;
  const z0 = evs('zoomin').length;
  Object.assign(BR, { x: 560, y: 820, dir: -Math.PI / 2, mode: 'walk', tgt: [560, 700] }); const tn = T; TCCare.pressPet(T);
  check(S.phase === 'approach' && BR.mode === 'idle' && BR.hurry === 2.8 && !!S.zB && S.zB.z > 1.5 && evs('zoomin').length === z0 + 1, '奥で むこう向きに 歩いて いる → 歩くのを やめて その場で 横向きに（急ぎ足 2.8倍）・カメラは 押した ときから 寄る');
  check(until(() => S.phase === 'pet', 5) && BR.x === 560 && BR.y === 820 && Math.abs(Math.sin(BR.dir)) < 0.4 && BR.hurry === 1 && evs('zoomin').length === z0 + 1, `その場で 横向きに なって すぐ 撫でられる（${(T - tn).toFixed(2)}秒・ズームの 仕上げは 待たない）`);
  check(!!S.zB && S.zDur === 0.25, 'ズームの 仕上げ（0.25秒）は 撫でられる ように なって から');
  run(0.4); check(!S.zB && S.phase === 'pet' && S.zoom.z > 1.5, '仕上げが おわっても 撫でる まま');
  idle(20); run(0.2);
  Object.assign(BR, { x: 120, y: 1200, dir: Math.PI / 2, mode: 'idle' }); TCCare.pressPet(T);
  check(S.phase === 'approach' && BR.mode === 'walk' && BR.tgt[0] === 1.75 * 200 + 12 + 44 && BR.tgt[1] === 1200 && !!S.zB, `横向きに なると 画面から はみ出す 所（x 120）→ 入る 所（x ${BR.tgt && BR.tgt[0]}：しっぽの がわ 1.75 ＋ よゆう 44）まで だけ 歩く`);
  until(() => S.phase === 'pet', 6); check(S.phase === 'pet' && Math.cos(BR.dir) > 0.9, '左の はしの 馬は 右向き（顔を まん中へ）で 撫でる');
  idle(20); run(0.2);
  // 第4.152版（バグ直し）：行き先が 近くて 向きが ちがう → 先に その場で 行き先を 向く（回りつづけない）・走って いる 馬でも 始まる
  Object.assign(BR, { x: 800, y: 955, dir: -1.63, mode: 'run' }); const tr0 = T; TCCare.pressPet(T);
  check(S.phase === 'approach' && BR.mode === 'turn' && Math.abs(Math.abs(BR.turnTo) - Math.PI) < 0.01 && S.route.length === 1, '右の はしを 走って いる 馬を 撫でる：入る 所（左へ 少し）が 近くて 向きが ちがう → 先に その場で 行き先を 向く');
  check(until(() => S.phase === 'pet', 6) && T - tr0 < 2 && BR.x <= 1052 - (1.75 * 200 + 12) && Math.cos(BR.dir) < -0.9, `向いて から 歩いて 着く → 左向き（顔を まん中へ）で 撫でられる（${(T - tr0).toFixed(2)}秒・x ${Math.round(BR.x)}）`);
  idle(20); run(0.2);
  Object.assign(BR, { x: 526, y: 1000, dir: 0, mode: 'idle' }); TCCare.pressPet(T); S.phase = 'approach'; S.route = [[526, 1300]]; BR.mode = 'walk'; BR.tgt = null; const ts0 = T;      // 着かない まま（にせの 馬は 行き先が ないと 動かない）
  run(5.2); check(S.phase !== 'idle' && S.route.length === 0, '5秒 たっても 着かない → 歩くのを やめる（安全の ため）');
  check(until(() => S.phase === 'pet', 4) && T - ts0 < 9, `そのまま その場で 撫でられる ように なる（${(T - ts0).toFixed(1)}秒・とまった まま に ならない）`);
  idle(20); run(0.2);
  S.stock = 5; Object.assign(BR, { x: 560, y: 820, dir: Math.PI / 2, mode: 'idle' }); TCCare.press(T, 'feed'); TCCare.press(T, 'pick:apple'); const tf = T;
  check(until(() => S.phase === 'feed', 5) && BR.y === 820 && T - tf < 1.0, `ごはん：えらんで から 食べはじめる まで ${(T - tf).toFixed(2)}秒（奥に いても その場）`);
  idle(30); run(0.2);
  Object.assign(BR, { x: 300, y: 700, dir: 0, mode: 'idle' }); TCCare.pressCall(T, 'come');
  check(BR.mode === 'walk' && BR.tgt[1] === 1040 && !S.zB && S.zoom.z === 1, `呼ぶ（近づく）：いちばん 手前（1372）まで 歩かない（行き先 y ${BR.tgt[1]}）・ズームは しない`);
  idle(20);
  Object.assign(BR, { x: 526, y: 1000, dir: 0, mode: 'idle' }); run(7.5); TCCare.pressCall(T, 'amae');
  check(BR.mode === 'walk' && BR.tgt[1] === 1230, `呼ぶ（甘える）：いまの 所から 230 だけ 手前（行き先 y ${BR.tgt[1]}）`);
  idle(20);
  // 第4.168版（まさちゃん 2026/11/14 01:26「ごはんをあげたあと、おかわり？の時だけ抽選ボタンが出るのが遅すぎる。通常の時と同じ速度で表示して！」）：
  //   おかわりの目は 見つめる だけ（なでて もらうのを 待つ 場面 S.phase==='beg' は もう ない）＝ おしまいと PUSH は おかわりの目が 出ない ときと 同じ 時
  console.log('おかわりの目（見つめる だけ・PUSH は いつもと 同じ 速さ）');
  idle(30); S.stock = S.stockShow = 9; Object.assign(BR, { x: 526, y: 1100, dir: 0, mode: 'idle' }); RND = 0.99;      // 0.99：おかわりの目は 出ない
  TCCare.press(T, 'feed'); TCCare.press(T, 'pick:apple'); const tn8 = T; until(pushLive, 30); const dn = T - tn8, bn = evs('beg', tn8).length;
  check(pushLive() && bn === 0, `ふつうの ごはん：えらんで から PUSH まで ${dn.toFixed(2)}秒（おかわりの目は 出ない）`);
  idle(30); Object.assign(BR, { x: 526, y: 1100, dir: 0, mode: 'idle' }); RND = 0.2;      // 0.2：おかわりの目（1/4）が 出る・ほかの 当たりは 出ない
  TCCare.press(T, 'feed'); TCCare.press(T, 'pick:apple'); const tb8 = T; let sawBeg = false; until(() => { if (S.phase === 'beg') sawBeg = true; return pushLive(); }, 30); const db = T - tb8;
  check(evs('beg', tb8).length === 1 && !sawBeg && BR.reacts.some(r => r.k === 'beg'), 'ごはんの あと おかわりの目（1/4）：こちらを 見つめる（なでて もらうのを 待つ 場面は ない）');
  check(pushLive() && Math.abs(db - dn) < 0.05, `おかわりの目の ときも PUSH は いつもと 同じ 時に 出る（ふつう ${dn.toFixed(2)}秒・おかわり ${db.toFixed(2)}秒。前は なでる まで 6.5秒 待って いた）`);
  { const p0 = TCHorse.where(HO, 'poll'); TCCare.input('down', p0[0], p0[1], T); TCCare.input('up', p0[0], p0[1], T); run(0.2); }
  check(pushLive() && S.phase !== 'pet', 'おかわりの目の 間に 馬を さわっても 何も 始まらない（PUSH を 押す まで）');
  check(idle(10), 'PUSH を 押すと おしまい');
  RND = 0.5;
  // 第4.154版（まさちゃん 11/11 20:00「テスト版で…お世話の当選パターン全種類テストできるようにして！」）：テスト版の 道具が 使う S.test
  //   名前が あれば 次の 1回 だけ その 結果（使ったら 消える）・なければ いつもの くじ（rnd）。App Store版では S.test は いつも null
  console.log('テスト版の 道具（S.test：次の 1回 だけ 結果を 決める）');
  idle(30); RND = 0.99;      // 0.99：金のニンジン・おかわりの目・首を かしげる・ほうきを かじる・ハートの 当たりは どれも 出ない 数。呼ぶは「甘える」
  check(S.test === null, 'ふだんは S.test＝null');
  S.stock = S.stockShow = 9; Object.assign(BR, { x: 526, y: 1100, dir: 0, mode: 'idle' }); const tq0 = T;
  TCCare.press(T, 'feed'); TCCare.press(T, 'pick:carrot'); until(() => S.phase === 'feed', 10);
  check(S.feed && S.feed.gold === false, '決めて いない → ニンジンは ふつう（いつもの くじ）');
  idle(30); check(!evs('beg', tq0).length, '決めて いない → おかわりの目は 出ない');
  S.test = { gold: true, beg: true };
  TCCare.press(T, 'feed'); TCCare.press(T, 'pick:apple'); until(() => S.phase === 'feed', 10);
  check(S.feed.gold === false && S.test.gold === true, 'gold：リンゴでは 使わない（次の ニンジン まで のこる）');
  { const tq = T; check(until(() => evs('beg', tq).length > 0, 20) && !('beg' in S.test), 'beg：ごはんの あと おかわりの目（使ったら 消える）'); }
  idle(30);
  let h1 = S.heart; S.got = [];
  TCCare.press(T, 'feed'); TCCare.press(T, 'pick:carrot'); until(() => S.phase === 'feed', 10);
  check(S.feed.gold === true && !('gold' in S.test), 'gold：次の ニンジンは 金のニンジン（使ったら 消える）');
  idle(30); check(S.heart === Math.min(10, h1 + 3) && !evs('beg', T - 8).length, '金のニンジン → なかよし ＋3・おかわりの目は もう 出ない（1回 だけ）');
  TCCare.press(T, 'feed'); TCCare.press(T, 'pick:carrot'); until(() => S.phase === 'feed', 10);
  check(S.feed.gold === false, 'その 次の ニンジンは ふつう（いつもの くじに もどる）'); idle(30);
  // 呼ぶ
  run(7.5); TCCare.pressCall(T); check(S.callKind === 'amae', '決めて いない → 呼ぶは いつもの くじ（0.99 → 甘える）'); idle(20);
  for (const k of ['come', 'turn']) { run(7.5); S.test = Object.assign(S.test || {}, { call: k }); TCCare.pressCall(T); check(S.callKind === k && !('call' in S.test), `call：次の 呼ぶは「${k}」（使ったら 消える）`); idle(20); }
  // 撫でる：首を かしげる・ハートの 抽選（当たり）
  until(() => T >= S.coolUntil + 0.2, 10); S.got = []; S.heart = S.heartShow = 0;
  S.test = { rare: true }; let tt0 = T; TCCare.pressPet(T); until(() => S.phase === 'pet', 6); pet(); run(0.5);
  check(evs('tilt', tt0).length === 1 && !('rare' in S.test), 'rare：次に なでると 首を かしげる（使ったら 消える）');
  pet(); run(0.5); check(evs('tilt', tt0).length === 1, 'その 次は いつもの 反応');
  idle(30); until(() => T >= S.coolUntil + 0.2, 10);
  S.got = []; S.heart = S.heartShow = 9; S.test = { win: true }; const st1 = S.stock; tt0 = T;
  TCCare.pressPet(T); until(() => S.phase === 'pet', 6); pet();
  check(until(() => S.lot && S.lot.win === true, 12) && !('win' in S.test), 'win：ハート 10こ の 抽選は 当たり（使ったら 消える）');
  until(() => S.phase === 'idle' && !S.busy, 30);
  check(S.stock === st1 + 5 && evs('unlock', tt0).length === 1 && S.heart === 0, '当たり → ぴょん！・お世話トークン ＋5・ハートは 0 から');
  until(() => T >= S.coolUntil + 0.2, 10); S.got = []; S.heart = S.heartShow = 9; S.test = { win: false }; tt0 = T;
  TCCare.pressPet(T); until(() => S.phase === 'pet', 6); pet();
  check(until(() => S.lot && S.lot.win === false, 12), 'win＝false：ハズレ（ふぅ〜）も えらべる');
  until(() => S.phase === 'idle' && !S.busy, 30);
  // おそうじ：ほうきを かじる（馬の 顔の 近くで 2つ目を 片付けた とき）
  S.stock = S.stockShow = 9; Object.assign(BR, { x: 526, y: 1100, dir: 0, mode: 'idle' }); BR.trashDone = false;
  const two = () => { BR.poops = []; BR.trash = [pile(300, 1250, 0), pile(850, 950, 1)]; TCCare.press(T, 'clean'); until(() => S.phase === 'clean', 3); const C = S.clean; sweepTo(C.tg[0]); movePan(650, 950); sweepTo(C.tg[1]); run(0.4); };      // 第4.165版：2つ目は ちりとりを 馬の 顔の 近く（2つ目の 山の 左）へ 運んで から
  tt0 = T; two(); check(evs('nibble', tt0).length === 0, '決めて いない → ほうきは かじらない（0.99）'); idle(30); BR.trashDone = false;
  S.test = { nibble: true }; tt0 = T; two(); check(evs('nibble', tt0).length === 1 && !('nibble' in S.test), 'nibble：次の おそうじで ほうきを かじる（使ったら 消える）'); idle(30); BR.trashDone = false;
  S.test = null; RND = 0.5;
  // 第4.154版（バグ直し）：幻の馬・神様馬が 帰った あとの ルーレット・チケットで、帰った 馬の 降臨の バナーが また 出ない
  console.log('降臨の バナー（帰った あとは 出し直さない）');
  idle(30);
  const banOn = () => !!(S.ban && S.ban.hideT == null && S.ban.showT != null);
  await TCCare.special('kamisama'); run(1.0); check(banOn() && S.ban.shown && evs('banin', T - 2).length === 1, '神様馬が 来た → 降臨の バナーが 出る');
  TCCare.roulette(true); run(0.5); const r1 = banOn(); TCCare.roulette(false); run(1.0);
  check(!r1 && banOn() && S.ban.shown, 'いる 間の ルーレット：演出の 間は 消えて、おわったら また 出る（前と 同じ）');
  TCCare.special(null); run(0.6); check(!banOn(), '帰った → バナーは 消える');
  const bi = evs('banin').length; TCCare.roulette(true); run(0.5); TCCare.roulette(false); run(1.5);
  check(!banOn() && evs('banin').length === bi, '帰った あとの ルーレット・チケット：バナーは また 出ない（前は 出て、そのまま 残って いた）');
  await TCCare.special('maboroshi'); run(1.0); check(banOn() && S.ban.kind === 'maboroshi' && !S.ban.gone, 'つぎに 幻の馬が 来たら 新しい バナーが 出る');
  TCCare.special(null); run(0.6);
  // 第4.156版：夜に 撫でても ねない（あくび だけ）
  console.log('夜に 撫でる（あくび だけ・ねない）');
  until(() => S.phase === 'idle' && !S.busy, 30); until(() => T >= S.coolUntil + 0.2, 10);
  await TCCare.init({ canvas: { getContext: () => ctx }, horse: HO, brain: BR, rnd: () => RND, tod: 'night', stageNo: 5, props: false, onEvent: e => EV.push(e) });
  Object.assign(BR, { x: 526, y: 900, dir: 0, mode: 'idle', reacts: [] }); S.stock = S.stockShow = 9; S.got = []; S.heart = S.heartShow = 0; S.petN = 0; run(0.5);
  const tnt = T; TCCare.pressPet(T); check(until(() => S.phase === 'pet', 6), '夜でも 撫でられる');
  pet(); until(() => evs('yawn', tnt).length > 0, 8);
  check(evs('yawn', tnt).length === 1, '夜に 撫でた あと：あくび');
  until(() => S.phase === 'idle' && !S.busy, 30); run(8);
  check(LAY === 0 && BR.mode !== 'sleep' && !(BR.sl > 0) && !['flop', 'goron', 'lie'].some(k => evs(k).length), 'あくびの あとも ねない（横に ならない・前は 1.7秒後に 横に なって ねむった）');
  check(T - tnt < 22 && S.phase === 'idle', `夜の 撫でるは あくびで おわる（${(T - tnt).toFixed(1)}秒で もとの 画面）`);
  // ---------- 第4.159版：お世話の あとの PUSH ----------
  console.log('お世話の あとの PUSH（第4.159版）');
  idle(30); until(() => !S.busy, 10);
  let NEXT = null, LOTFREE = true; const PR = [], BK = [], PU = [];      // 次の 抽選の 結果・待って いた ハートの 抽選を 始めて よいか・わたした 当たり・スイッチ・PUSH が 出た／消えた
  await TCCare.init({ canvas: { getContext: () => ctx }, horse: HO, brain: BR, rnd: () => RND, tod: 'morning', stageNo: 5, props: false, onEvent: e => EV.push(e),
    lottery: () => (NEXT ? JSON.parse(JSON.stringify(NEXT)) : null), onPrize: z => PR.push(z), onBulk: v => BK.push(v), onPush: v => PU.push(v), bulk: false, stockMax: 25, lotFree: () => LOTFREE });
  check(TCCare.RULE.stockMax === 25 && S.bulk === false, 'きまり：お世話トークンの 上限は 25・はじめは「1個 使う」');
  const evn = (k, i) => EV.slice(i).filter(e => e.k === k).length;      // i 番目 から あとの 音の 数（音の 時刻は 小数 4けたに 丸めて ある ので、時刻では なく 番号で 数える）
  const G = TCCare.PUSHG, feed = () => { Object.assign(BR, { x: 526, y: 1100, dir: 0, mode: 'idle' }); TCCare.press(T, 'feed'); TCCare.press(T, 'pick:apple'); until(() => S.phase === 'feed', 10); until(() => S.phase === 'idle', 30); };
  S.stock = S.stockShow = 0; RND = 0.99; let w9 = evs('wait').length; TCCare.press(T, 'feed'); TCCare.press(T, 'pick:apple'); run(0.5);
  check(S.phase === 'idle' && !S.feed && evs('wait').length === w9 + 1 && !S.push, 'トークンが 0：ごはんは 始まらない（「お世話トークンが たまるまで まってね」）・PUSH も 出ない');
  S.stock = S.stockShow = 3; let k0 = evs('token').length, tp0 = T;
  TCCare.press(T, 'feed'); TCCare.press(T, 'pick:apple'); until(() => S.phase === 'feed', 10);
  check(S.stock === 3 && evs('token').length === k0 && !S.push, 'ごはんを 始めても トークンは 減らない（抽選も まだ：PUSH は 出て いない）');
  until(() => S.phase === 'idle', 30);
  check(pushLive() && S.push.n === 0 && evs('pushin', tp0).length === 1 && PU.join() === 'true' && S.stock === 3, 'ごはんが おわった → PUSH が 出る（アプリへ 知らせる・トークンは まだ 3）');
  run(0.3); const ph = S.phase;
  TCCare.pressPet(T); TCCare.pressCall(T, 'come'); TCCare.press(T, 'feed'); TCCare.press(T, 'clean');
  check(S.phase === ph && S.phase === 'idle' && !S.mode && !S.chooser && S.fx.some(f => f.txt === '先に PUSH を 押してね'), 'PUSH が 出て いる 間：撫でる・呼ぶ・ごはん・おそうじは 始まらない');
  // 指を 置いた 瞬間に 押せる（はなす まで 待たない）
  NEXT = null; let e0 = EV.length; TCCare.pointer('down', G.x, G.y, T);
  const evNow = EV.slice(e0).map(e => e.k);
  check(S.stock === 2 && evNow.includes('token') && evNow.includes('pfo') && !S.fx.some(f => f.k === 'pointpop') && PR.length === 0, `PUSH に 指を 置いた 瞬間：トークン −1・抽選 → ハズレは 音 だけ（プフォ：${evNow.join('・')}）・札は 出ない`);
  TCCare.pointer('up', G.x, G.y, T); run(0.1);
  check(S.stock === 2 && evs('token').length === k0 + 1 && !pushLive() && PU.join() === 'true,false', '指を はなしても もう 1回は 押されない・1個 使う：1回で PUSH は 消える');
  // 消えて いく 間（約0.6秒）：ごはんの ボタンの 所を さわっても 始まらない（つづけて 押した 指が、まだ 見えない ボタンを 押さない ように）→ 消えたら 押せる
  const BF = [407, 1494]; TCCare.pointer('down', BF[0], BF[1], T); TCCare.pointer('up', BF[0], BF[1], T); const g1 = !S.chooser && S.phase === 'idle';
  run(0.7); const g2 = S.push === null; TCCare.pointer('down', BF[0], BF[1], T); TCCare.pointer('up', BF[0], BF[1], T); const g3 = !!S.chooser && S.mode === 'feed';
  check(g1 && g2 && g3, `PUSH が 消えて いく 間は ごはんの 所を さわっても 始まらない → 片付いたら 押せる（${[g1, g2, g3]}）`);
  S.chooser = null; S.phase = 'idle'; S.mode = null; BR.careHold = false;      // えらぶ 札は とじる（ためした だけ）
  TCCare.pressPet(T); check(S.mode === 'pet', 'PUSH が 消えたら お世話が できる'); until(() => S.phase === 'idle' && !S.busy, 30); until(() => T >= S.coolUntil + 0.2, 10);
  // 当たり：ポイント
  for (const [v, snd, other] of [[10, 'piron', 'dedeen'], [100, 'piron', 'dedeen'], [200, 'dedeen', 'piron'], [300, 'dedeen', 'piron']]) {
    S.stock = S.stockShow = 3; PR.length = 0; feed(); run(0.3); NEXT = { k: 'pt', v }; const t1 = T, i1 = EV.length; TCCare.pushPress(T);
    check(evn(snd, i1) === 1 && evn(other, i1) === 0 && evn('pfo', i1) === 0 && evn('kyuin', i1) === 0 && evn('token', i1) === 1 && S.fx.filter(f => f.k === 'pointpop' && f.v === v && f.t0 === t1).length === 1 && PR.length === 1 && PR[0].v === v && S.stock === 2,
      `${v}P：押した 瞬間に 札（${v}P GET）と 音（${snd === 'piron' ? 'ピロン' : 'デデーン'}）・ポイントを わたす`);
    run(0.8);
  }
  // 当たり：ルーレット（キュインキュイーン → 1秒 あとに 演出）・チケット（すぐ 演出）
  S.stock = S.stockShow = 3; PR.length = 0; feed(); run(0.3); NEXT = { k: 'rt', tier: 'normal', a: 800, b: 1600, win: 1 }; let i2 = EV.length; TCCare.pushPress(T);
  check(evn('kyuin', i2) === 1 && evn('pfo', i2) + evn('piron', i2) + evn('dedeen', i2) === 0 && PR.length === 0 && S.fx.some(f => f.k === 'rtcue') && S.stock === 2, 'ルーレット当選：押した 瞬間に キュインキュイーン（ルーレットは まだ）');
  run(0.9); check(PR.length === 0, '0.9秒：まだ'); run(0.2); check(PR.length === 1 && PR[0].k === 'rt' && PR[0].win === 1, '1.0秒 あと → アプリが ルーレットを 出す');
  run(0.8);
  // 第4.165版：ポイント特化ゾーン（ルーレットと 同じ 合図：キュインキュイーン・札「特化ゾーン！」→ 1秒 あとに アプリの 演出）
  S.stock = S.stockShow = 3; PR.length = 0; feed(); run(0.3); NEXT = { k: 'zn', n: 3, v: 7000 }; i2 = EV.length; TCCare.pushPress(T);
  check(evn('kyuin', i2) === 1 && evn('pfo', i2) + evn('piron', i2) + evn('dedeen', i2) === 0 && PR.length === 0 && S.fx.some(f => f.k === 'rtcue' && f.txt === '特化ゾーン！') && S.stock === 2 && S.push.res === 'zn', 'ポイント特化ゾーン：押した 瞬間に キュインキュイーン と 札「特化ゾーン！」（演出は まだ）');
  run(0.9); check(PR.length === 0, '0.9秒：まだ'); run(0.2); check(PR.length === 1 && PR[0].k === 'zn' && PR[0].n === 3 && PR[0].v === 7000, '1.0秒 あと → アプリが 特化ゾーンを 出す（上乗せの 回数は 抽選で 決まった まま）');
  run(0.8);
  S.stock = S.stockShow = 3; PR.length = 0; feed(); run(0.3); NEXT = { k: 'tk', n: 2 }; i2 = EV.length; TCCare.pushPress(T);
  check(PR.length === 1 && PR[0].k === 'tk' && PR[0].n === 2 && evn('kyuin', i2) + evn('pfo', i2) + evn('piron', i2) + evn('dedeen', i2) === 0 && evn('token', i2) === 1, 'チケット当選：すぐ アプリの 演出（プチュン → 扉）へ');
  run(0.8);
  // まとめて 使う
  console.log('まとめて 使う');
  S.stock = S.stockShow = 6; PR.length = 0; PU.length = 0; NEXT = null; feed(); run(0.3);
  TCCare.press(T, 'pend'); check(pushLive(), 'まだ 1回も 押して いない：「おわる」は ない');
  TCCare.pointer('down', G.mn[0], G.mn[1], T); TCCare.pointer('up', G.mn[0], G.mn[1], T);
  check(S.bulk === true && BK.join() === 'true' && pushLive() && S.stock === 6, 'スイッチ「まとめて 使う」を 押す → まとめてに（アプリが おぼえる）・トークンは そのまま');
  k0 = evs('token').length; let pf0 = evs('pfo').length;
  for (let i = 0; i < 3; i++) { TCCare.pointer('down', G.x, G.y, T); TCCare.pointer('up', G.x, G.y, T); run(0.12); }      // 0.12秒ごとに つづけて 3回
  check(S.stock === 3 && evs('token').length === k0 + 3 && evs('pfo').length === pf0 + 3 && pushLive() && S.push.n === 3, 'つづけて 3回 押す：押した 回数ぶん トークンが 減る（6 → 3）・すぐ 次が 押せる・PUSH は のこる');
  NEXT = { k: 'pt', v: 50 }; TCCare.pushPress(T); run(0.1); NEXT = { k: 'pt', v: 20 }; TCCare.pushPress(T);
  check(S.fx.filter(f => f.k === 'pointpop').length === 1 && S.fx.find(f => f.k === 'pointpop').v === 20 && PR.length === 2 && S.stock === 1, 'つづけて 当たった：前の 札は 消して 新しい 札を すぐ 出す（ポイントは 2回とも わたす）');
  NEXT = null; TCCare.pushPress(T); check(S.stock === 0 && !pushLive(), 'さいごの 1つを 使った → PUSH は 消える（トークンの 分 しか 押せない）');
  const kz = evs('token').length; TCCare.pushPress(T); TCCare.pointer('down', G.x, G.y, T); TCCare.pointer('up', G.x, G.y, T);
  check(S.stock === 0 && evs('token').length === kz, 'トークンが 0：もう 押せない（マイナスに ならない）');
  run(0.8);
  // おわる・ルーレットの 間
  S.stock = S.stockShow = 8; PR.length = 0; feed(); run(0.3); NEXT = null; TCCare.pushPress(T); run(0.2);
  check(pushLive() && S.stock === 7 && S.bulk === true, 'まとめては おぼえて いる（次の お世話でも まとめて）');
  NEXT = { k: 'rt', tier: 'normal', a: 800, b: 1600, win: 0 }; TCCare.pushPress(T); const s7 = S.stock; run(0.3); NEXT = null;
  check(TCCare.pushPress(T) === false && S.stock === s7, 'ルーレット当選の キュインキュイーンの 間：PUSH は 押せない'); run(0.8);
  check(PR.length === 1 && pushLive(), 'ルーレットへ（まとめて なので PUSH は のこって いる）');
  await TCCare.special('maboroshi'); run(0.2);      // 降臨の バナーが 出て いる とき：バナーが 合図（rtReq）を 1回 読んで 消す。それでも 演出の 間（fxHold）は 押せない まま
  TCCare.roulette(true); run(0.5); check(S.ban && S.rtReq == null && S.fxHold === true && TCCare.pushPress(T) === false && S.stock === s7, 'ルーレットの 演出の 間（降臨の バナーが 出て いても）：PUSH は 押せない');
  TCCare.pointer('down', G.x, G.y, T); TCCare.pointer('up', G.x, G.y, T); check(S.stock === s7, '演出の 間は さわっても 減らない');
  TCCare.roulette(false); run(0.3); check(S.fxHold === false && TCCare.pushPress(T) === true && S.stock === s7 - 1, 'ルーレットが おわった → また 押せる'); await TCCare.special(null);
  const fo = evs('fold').length; TCCare.pointer('down', G.end[0], G.end[1], T); TCCare.pointer('up', G.end[0], G.end[1], T);
  check(!pushLive() && S.stock === s7 - 1 && evs('fold').length === fo + 1, '「おわる」→ PUSH は 消える（のこりの トークンは そのまま）'); run(0.6);
  TCCare.press(T, 'pm:1'); check(S.bulk === true, 'PUSH が 出て いない ときは スイッチは きかない');
  feed(); run(0.3); TCCare.press(T, 'pm:1'); check(S.bulk === false && BK.join() === 'true,false', 'スイッチ「1個 使う」に もどす'); TCCare.pushPress(T); check(!pushLive(), '1個 使う：1回で 消える'); run(0.6);
  // アプリを 開き直した とき（前の PUSH が まだ）・馬が かわっても PUSH は のこる
  S.stock = S.stockShow = 2; TCCare.pushShow(T + 0.1); run(0.3); check(pushLive(), '開き直した とき：前の PUSH を また 出す（pushShow）');
  TCCare.setHorse(HO, BR); check(pushLive() && S.phase === 'idle', '馬が かわって（育って）も PUSH は のこる');
  TCCare.pushPress(T); run(0.8); S.stock = 0; TCCare.pushShow(T); check(!S.push, 'トークンが 0 なら 出さない');
  // ---------- まさちゃん 2026/11/12 12:48「お世話トークンは25がMAX」「25MAXの時に撫でてても、お世話トークンが最大だよ！って表示されるようにして！」 ----------
  //   ・トークンが 25（最大）の ときに「撫でる」を 押す → 札「お世話トークンが 最大だよ！」（24こ までは 出ない）
  // ---------- 13:27「お世話トークンが25MAXの場合、なかよしハートが10個溜まっても抽選せずに、お世話トークンが20個を切ってから、お世話トークンゲットできるか抽選するようにしてほしい！」 ----------
  //   ・ハートの 抽選は トークンが 20こ未満の とき だけ。20こ以上（25こ も）で 10こ たまったら 待つ（ハートは 10の まま・もう ふえない・お知らせ）
  //   ・20こを 切ったら、何も して いない とき（PUSH・当たりの 演出・説明書などが 出て いない）に ひとりでに 抽選を 始める
  //   ・抽選の 途中で トークンが ふえて いた とき（10分ごとの ＋5）：当たりの ＋5 は 25 まで（足せる 数を 札と「＋N」の 両方に）
  console.log('トークンが 最大（25）の とき・ハートの 抽選は 20こ未満の とき だけ');
  {
  const MAXT = 'お世話トークンが 最大だよ！', LOTT = 'トークンが 20こを 切ったら 抽選だよ', AUTOT = 'なかよしハートの 抽選！';
  const tagsNow = () => S.fx.filter(f => f.k === 'tagUI' && f.txt === MAXT).length, notes = txt => S.fx.filter(f => f.k === 'note' && f.txt === txt).length;
  const settle = () => { until(() => S.phase === 'idle' && !S.busy && !S.mode, 30); run(0.8); clearPush(); until(() => T >= S.coolUntil + 0.2, 10); };
  const prep = (n, h) => {          // トークン n こ・ハート h こに して、前の 札を 片付ける
    settle(); S.petN = 0; S.got = []; S.heart = S.heartShow = h; S.drainT = null; S.test = { win: true }; S.stock = S.stockShow = n;
    S.fx = S.fx.filter(f => !['plus', 'unlock', 'tagUI', 'note', 'pointpop'].includes(f.k)); S.maxTagT = -9; S.lotNoteT = -9; S.lotIdleT = null;
  };
  const res = i0 => ({ stock: S.stock, plus: S.fx.filter(f => f.k === 'plus').map(f => f.txt).join(), sign: S.fx.filter(f => f.k === 'unlock').map(f => f.n).join(), unlock: evn('unlock', i0), stockEv: evn('stock', i0), wait: evn('wait', i0), max: evn('max', i0), heart: S.heart });
  const done = () => until(() => S.phase === 'idle' && !S.busy && !S.mode, 30);
  check(TCCare.RULE.lotStock === 20, 'きまり：ハートの 抽選は トークンが 20こ未満の とき だけ（RULE.lotStock＝20）');
  // (1) 9こ・19こ：10こ たまったら すぐ 抽選（今まで どおり）
  for (const n of [9, 19]) {
    prep(n, 9); const i0 = EV.length; TCCare.pressPet(T); const tag = tagsNow(); until(() => S.phase === 'pet', 6); pet(); const won = until(() => S.lot && S.lot.win === true, 12); done(); const w = res(i0);
    check(won && tag === 0 && w.stock === n + 5 && w.plus === '+5' && w.sign === '5' && w.unlock === 1 && w.stockEv === 1 && w.heart === 0 && w.max === 1 && notes(LOTT) === 0,
      `トークン ${n}こ で ハートが 10こ：すぐ 抽選 → 当たり ＋5（${n} → ${w.stock}）・札「お世話 5回 解放！」と「＋5」`);
  }
  // (2) 抽選の 途中で トークンが ふえて いた：当たりの ＋5 は 25 まで（出す 数と 足す 数が 同じ）・もう 25 → 足さずに「お世話トークンが 最大だよ！」の 札
  for (const [mid, plus, sign, st1] of [[23, '+2', '2', 25], [25, '', '0', 25]]) {
    prep(19, 9); const i0 = EV.length; TCCare.pressPet(T); until(() => S.phase === 'pet', 6); pet(); const won = until(() => S.lot && S.lot.win === true, 12); S.stock = S.stockShow = mid; done(); const w = res(i0);
    check(won && w.stock === st1 && w.plus === plus && w.sign === sign && w.unlock === (mid < 25 ? 1 : 0) && w.stockEv === (mid < 25 ? 1 : 0) && (mid < 25 || w.wait >= 1) && w.heart === 0,
      `抽選の 途中で トークンが ${mid}こに ふえて いた → 当たりは 25 まで（${mid} → ${w.stock}）・札と「＋N」は 同じ 数（札 ${sign}・「${plus || 'なし'}」）`);
  }
  // (3) 20こ：10こ たまっても 抽選しない（ハートは 10の まま・お知らせ 1回・「まだ だよ」の 音）→ 待っても 始まらない
  prep(20, 9); let i0 = EV.length; TCCare.pressPet(T); const tagB = tagsNow() + notes(LOTT); until(() => S.phase === 'pet', 6); pet(); run(3.5);
  const h1 = { lot: !!S.lot, busy: S.busy, heart: S.heart, show: S.heartShow, note: notes(LOTT), wait: evn('wait', i0), max: evn('max', i0), heartEv: evn('heart', i0), gather: evn('gather', i0) };
  check(tagB === 0 && !h1.lot && !h1.busy && h1.heart === 10 && h1.show === 10 && h1.note === 1 && h1.wait === 1 && h1.max === 0 && h1.heartEv === 1 && h1.gather === 0,
    `トークン 20こ で ハートが 10こ：抽選しない（ハートは 10の まま・お知らせ「${LOTT}」1回）${JSON.stringify(h1)}`);
  done(); run(6);
  check(S.phase === 'idle' && !S.mode && !S.lot && S.heart === 10 && S.stock === 20 && evn('max', i0) === 0 && S.lotIdleT == null, '待って いる 間（トークン 20こ）：6秒 たっても 抽選は 始まらない');
  // (4) 待って いる 間に また 撫でる：押した とき お知らせ・なでても ハートは ふえない（10の まま）・抽選しない・「1分に 5こまで」は 出ない
  until(() => T >= S.coolUntil + 0.2, 10); S.lotNoteT = -9; S.fx = S.fx.filter(f => f.k !== 'note'); const i1 = EV.length; TCCare.pressPet(T); const n1 = notes(LOTT);
  until(() => S.phase === 'pet', 6); S.lotNoteT = -9; pet(); run(2.5);
  check(n1 === 1 && notes(LOTT) === 2 && S.heart === 10 && evn('heart', i1) === 0 && !S.lot && !S.busy && evn('max', i1) === 0 && evn('nope', i1) === 0 && evn('rub', i1) >= 3,
    `待って いる 間に 撫でる：押した ときに お知らせ・なでても ハートは 10の まま（ふえない）・抽選しない（お知らせ ${notes(LOTT)}回）`);
  done();
  // (5) 20こを 切った（19こ）→ 何も して いなければ 約1秒で ひとりでに 抽選（お知らせ「なかよしハートの 抽選！」→ 撫でる 見え方 → ためて → ぴょん！）→ ＋5
  run(1.5); S.fx = S.fx.filter(f => !['plus', 'unlock', 'note'].includes(f.k)); const i2 = EV.length, tA = T; S.stock = S.stockShow = 19;
  const started = until(() => S.mode === 'pet', 3), dtA = T - tA, an = notes(AUTOT), rd = evn('ready', i2), wonH = until(() => S.lot && S.lot.win === true, 12); done(); const wH = res(i2);
  check(started && dtA > 0.9 && dtA < 1.3 && an === 1 && rd >= 1 && wonH && wH.stock === 24 && wH.plus === '+5' && wH.sign === '5' && wH.heart === 0 && wH.max === 1 && evn('gather', i2) === 1 && evn('rub', i2) === 0,
    `トークンが 20こを 切った（19こ）：${dtA.toFixed(2)}秒で ひとりでに 抽選が 始まる（お知らせ・なでなくて よい）→ 当たり ＋5（19 → ${wH.stock}）・ハートは 0に`);
  // (6) 25こ（最大）：押した ときに 札「お世話トークンが 最大だよ！」・10こ たまっても 抽選しない → PUSH を 6回（まとめて）押して 19こ：PUSH が 出て いる 間は 始まらない →「おわる」で 始まる
  prep(25, 9); i0 = EV.length; TCCare.pressPet(T); const tagC = tagsNow(); until(() => S.phase === 'pet', 6); pet(); run(3.5); const c1 = { lot: !!S.lot, heart: S.heart, stock: S.stock, note: notes(LOTT), plus: S.fx.filter(f => f.k === 'plus').length, unlock: S.fx.filter(f => f.k === 'unlock').length };
  check(tagC === 1 && !c1.lot && c1.heart === 10 && c1.stock === 25 && c1.note === 1 && c1.plus === 0 && c1.unlock === 0 && evn('max', i0) === 0,
    `トークン 25こ（最大）で 撫でる：押した ときに 札「${MAXT}」・ハートが 10こに なっても 抽選しない（25 の まま・当たりの 札も 出ない）${JSON.stringify(c1)}`);
  done(); NEXT = null; feed(); run(0.3); TCCare.press(T, 'pm:n');
  for (let k = 0; k < 6; k++) { TCCare.pushPress(T); run(0.15); }
  const p1 = { stock: S.stock, live: pushLive(), heart: S.heart }; run(3);
  check(p1.stock === 19 && p1.live && p1.heart === 10 && !S.lot && S.mode !== 'pet' && evn('max', i0) === 0 && pushLive(), 'PUSH を 6回 押して 19こ：PUSH が 出て いる 間は 抽選は 始まらない（つづけて 押せる）');
  TCCare.press(T, 'pend'); const tE = T, stE = until(() => S.mode === 'pet', 4), dtE = T - tE, wonE = until(() => S.lot && S.lot.win === true, 12); done(); const wE = res(i0); S.bulk = false;
  check(stE && dtE > 1.0 && dtE < 2.2 && wonE && wE.stock === 24 && wE.heart === 0 && wE.max === 1, `「おわる」→ ${dtE.toFixed(2)}秒で 抽選が 始まる → 当たり ＋5（19 → ${wE.stock}）`);
  // (7) 当たりの 演出の 間（ルーレット・チケット）・アプリが「いまは だめ」と 言う 間（馬の 入れかえ・説明書など）は 始まらない → おわったら 始まる
  prep(10, 10); TCCare.roulette(true); i0 = EV.length; run(3); const f1 = !S.lot && S.mode !== 'pet' && S.heart === 10; TCCare.roulette(false); const f2 = until(() => S.mode === 'pet', 2); until(() => !!S.lot, 6); done();
  check(f1 && f2 && S.heart === 0 && evn('max', i0) === 1, '当たりの 演出の 間（fxHold）は 始まらない → おわったら 始まる');
  prep(10, 10); LOTFREE = false; i0 = EV.length; run(3); const g1b = !S.lot && S.mode !== 'pet' && S.heart === 10; LOTFREE = true; const g2b = until(() => S.mode === 'pet', 2); until(() => !!S.lot, 6); done();
  check(g1b && g2b && S.heart === 0 && evn('max', i0) === 1, 'アプリが 止めて いる 間（lotFree＝false：馬の 入れかえ・説明書など）は 始まらない → よく なったら 始まる');
  // 開き直した／アプリに もどって きた すぐ あと（前の コマから 3秒より 長く あいた・アプリが S.wakeT を 入れた）：2.5秒は 始めない → そのあと 1秒で 始まる
  prep(10, 10); T += 20; i0 = EV.length; const tW = T; run(2.3); const k1 = !S.lot && S.mode !== 'pet' && S.wakeT > tW && S.wakeT - tW < 0.05; const k2 = until(() => S.mode === 'pet', 2.5), dtW = T - tW; until(() => !!S.lot, 6); done();
  check(k1 && k2 && dtW > 3.4 && dtW < 3.8 && S.heart === 0 && evn('max', i0) === 1, `開き直した すぐ あと：2.5秒は 始めない → ${dtW.toFixed(2)}秒で ひとりでに 抽選`);
  // (8) 待って いた 抽選が 始まる 前に「撫でる」を 押した（トークン 20こ未満）：なでなくても、撫でる 見え方に なったら すぐ 抽選
  prep(10, 10); i0 = EV.length; TCCare.pressPet(T); const q1 = S.mode === 'pet' && notes(AUTOT) === 0; const q2 = until(() => !!S.lot, 5); done();
  check(q1 && q2 && evn('rub', i0) === 0 && evn('max', i0) === 1 && S.heart === 0, '待って いた 抽選の 前に「撫でる」を 押した：なでなくても すぐ 抽選');
  // (9) ハズレ（ふぅ〜）でも 同じ：ひとりでに 始まって、トークンは ふえない・ハートは 0に
  prep(10, 10); S.test = { win: false }; i0 = EV.length; const l1 = until(() => S.lot && S.lot.win === false, 6); done();
  check(l1 && S.stock === 10 && S.heart === 0 && evn('calm', i0) === 1 && evn('unlock', i0) === 0, 'ひとりでに 始まった 抽選が ハズレ：ふぅ〜・トークンは そのまま・ハートは 0に');
  // 「撫でる」を 押した ときの 札
  settle(); S.petN = 0; S.got = []; S.heart = S.heartShow = 0; S.fx = S.fx.filter(f => f.k !== 'tagUI' && f.k !== 'note'); S.maxTagT = -9;
  S.stock = S.stockShow = 24; TCCare.pressPet(T); const mt0 = tagsNow(); idle(30);
  until(() => T >= S.coolUntil + 0.2, 10); S.stock = S.stockShow = 25; S.maxTagT = -9; TCCare.pressPet(T); const mt1 = tagsNow(); TCCare.pressPet(T); const mt2 = tagsNow(); idle(30);
  S.coolUntil = T + 5; S.maxTagT = -9; S.fx = S.fx.filter(f => f.k !== 'tagUI'); TCCare.pressPet(T); const mt3 = tagsNow(), cool = S.fx.some(f => f.k === 'tagUI' && /^あと/.test(f.txt)); S.coolUntil = -1e9;
  check(mt0 === 0 && mt1 === 1 && mt2 === 1 && mt3 === 0 && cool && notes(LOTT) === 0, `「撫でる」を 押した とき：24こ＝札は 出ない・25こ＝札が 1まい（つづけて 押しても ふえない）・7秒の 待ちの 間は「あと N秒」だけ（${[mt0, mt1, mt2, mt3]}）`);
  }
  S.stock = S.stockShow = 3;
  // 見本（説明の 動画）：PUSH を 押す 見本 だけ PUSH が 出る
  const D = TCCare.DEMOS;
  check(D.feed_b.press.some(q => q[1] === 'push') && D.clean_b.press.some(q => q[1] === 'push') && !D.feed_a.press.some(q => q[1] === 'push') && D.feed_b.pt === 100 && D.clean_b.pt === 200, '見本：ごはん（100P）・おそうじ（200P）は PUSH を 押して 当たりが 出る');
  // 第4.165版（まさちゃん 2026/11/13 12:36〜12:46「お世話トークン購入のアイコンやっぱりこっちで！お世話とかのところに上手く入れられない？」「1番右側に入れて！」「周りの大きさと合わせて！バランス調整して！」）：
  //   アプリ（onBuy を わたす）では 下の 列に 5つめ「お世話トークン購入」：お世話の 4つは 左へ・5つを 同じ 間かく・同じ 大きさ・同じ 高さ。押すと onBuy（開けない ときは 札）・PUSH の 間は 押せない
  console.log('下の 列の 5つめ：お世話トークン購入');
  { const B0 = JSON.parse(JSON.stringify(TCCare.BTN)); check(B0.pet[0] === 170 && B0.call[0] === 881 && TCCare.pointer && S.press.buy == null, 'onBuy を わたさない とき（見本）：お世話の 4つは 前の 所（170・407・644・881）・購入の ボタンは ない');
    until(() => S.phase === 'idle' && !S.busy && !S.mode, 30); run(0.8); clearPush(); run(0.8); S.fx = S.fx.filter(f => f.k !== 'tagUI');
    let BUYS = 0, BUYOK = true;
    await TCCare.init({ canvas: { getContext: () => ctx }, horse: HO, brain: BR, rnd: () => RND, tod: 'morning', stageNo: 1, props: false, onEvent: e => EV.push(e),
      lottery: () => null, onPrize: z => PR.push(z), stockMax: 25, lotFree: () => true, onBuy: () => { BUYS++; return BUYOK; } });
    const B = TCCare.BTN, Q = TCCare.BUYG, xs = [B.pet[0], B.feed[0], B.clean[0], B.call[0], Q.x], gaps = xs.slice(1).map((x, i) => x - xs[i]);
    check(JSON.stringify(xs) === '[128,327,526,725,924]' && gaps.every(g => g === 199) && xs[0] - 70 === 58 && 1052 - (Q.x + 70) === 58 && Q.y === B.pet[1] && Math.abs(Q.d - 140) <= 4 && Q.name === 'トークン購入' && TCCare.BTN_R === 70,
      `5つを 同じ 間かく（まん中から まん中 199・左右の はし 58）・同じ 高さ（${Q.y}）・絵の 幅 ${Q.d}（ほかの 丸 140 と 同じ 大きさ）・名前「トークン購入」`);
    S.stock = S.stockShow = 5; run(0.2); let e0 = EV.length;
    TCCare.pointer('down', Q.x, Q.y, T); const d0 = BUYS; TCCare.pointer('up', Q.x, Q.y, T);
    check(d0 === 0 && BUYS === 1 && S.press.buy === T && evn('button', e0) === 1 && !S.fx.some(f => f.k === 'tagUI' && /買えるよ/.test(f.txt)), '購入の ボタン：指を はなした ときに onBuy（1回）・ボタンの 音');
    TCCare.pointer('down', Q.x + 84, Q.y, T); TCCare.pointer('up', Q.x + 84, Q.y, T); TCCare.pointer('down', Q.x, Q.y, T); TCCare.pointer('up', Q.x + 200, Q.y - 300, T);
    check(BUYS === 1, '丸の 中 だけ（まわり 10px まで）・指を ずらして はなした ときは 押した ことに ならない');
    BUYOK = false; e0 = EV.length; TCCare.pointer('down', Q.x, Q.y, T); TCCare.pointer('up', Q.x, Q.y, T);
    check(BUYS === 2 && S.fx.some(f => f.k === 'tagUI' && f.txt === 'お世話が おわってから 買えるよ') && evn('wait', e0) === 1, 'アプリが 開けない とき（お世話の 途中 など：onBuy が false）→ 札「お世話が おわってから 買えるよ」');
    BUYOK = true; for (const k of ['pet', 'feed', 'clean', 'call']) { TCCare.pointer('down', B[k][0], B[k][1], T); }
    S.uiDown = null; TCCare.pushShow(T); run(0.4);
    TCCare.pointer('down', Q.x, Q.y + 60, T); TCCare.pointer('up', Q.x, Q.y + 60, T);
    check(pushLive() && BUYS === 2, 'PUSH が 出て いる 間は 列ごと かくれて、購入の ボタンも 押せない'); }
  // 第4.168版（まさちゃん 2026/11/14 01:26「ごはんを押しちゃうと戻れないから、戻るボタンを追加して！」）：えらぶ 札の「← もどる」・もう一度「ごはん」で とじる（トークンは へらない・PUSH も 出ない）
  console.log('ごはんの えらぶ 札：もどる（第4.168版）');
  { clearPush(); until(() => S.phase === 'idle' && !S.mode && !S.push, 30); run(0.6); S.stock = S.stockShow = 7; Object.assign(BR, { x: 526, y: 1100, dir: 0, mode: 'idle' });
    const B = TCCare.BTN; let e0 = EV.length; const evk = (k, from) => EV.slice(from).filter(e => e.k === k).length;
    TCCare.press(T, 'feed'); run(0.3);
    check(!!S.chooser && S.stock === 7, 'ごはんを 押す → えらぶ 札（トークンは まだ 使わない）');
    TCCare.pointer('down', 262, 1109, T); TCCare.pointer('up', 262, 1109, T); run(0.5);
    check(S.chooser === null && S.phase === 'idle' && !S.mode && S.stock === 7 && !pushLive() && evk('token', e0) === 0 && evk('fold', e0) === 1, '「← もどる」を 押す → 札が とじて もとに もどる（トークンは へらない・PUSH は 出ない・紙の 音）');
    TCCare.pointer('down', 262, 1109, T); TCCare.pointer('up', 262, 1109, T); run(0.2);
    check(S.chooser === null && S.phase === 'idle', '札が 出て いない ときに 同じ 所を さわっても 何も おきない');
    TCCare.press(T, 'feed'); run(0.3); const c1 = !!S.chooser; TCCare.pointer('down', B.feed[0], B.feed[1], T); TCCare.pointer('up', B.feed[0], B.feed[1], T); run(0.5);
    check(c1 && S.chooser === null && S.phase === 'idle' && S.stock === 7, 'もう一度「ごはん」を 押しても とじる');
    TCCare.press(T, 'feed'); run(0.3); TCCare.press(T, 'pick:apple');
    check(until(() => S.phase === 'feed', 10), 'そのあと ごはんを えらぶと いつもどおり 食べる'); idle(30); }
  // 第4.168版（まさちゃん 2026/11/14 01:26「幻の馬は、抽選最大10回まで 神様馬は、抽選最大5回まで」）：アプリが わたす drawLeft（のこりの 抽選の 回数）が 0 に なったら PUSH は 出ない・押せない
  console.log('抽選の 上限（drawLeft：第4.168版）');
  { clearPush(); until(() => S.phase === 'idle' && !S.mode && !S.push, 30); run(0.6);
    let LEFT = 2; const PR2 = [];
    await TCCare.init({ canvas: { getContext: () => ctx }, horse: HO, brain: BR, rnd: () => RND, tod: 'morning', stageNo: 1, props: false, onEvent: e => EV.push(e),
      lottery: () => null, onPrize: z => PR2.push(z), stockMax: 25, lotFree: () => true, drawLeft: () => LEFT });
    S.stock = S.stockShow = 9; S.bulk = true; Object.assign(BR, { x: 526, y: 1100, dir: 0, mode: 'idle' }); run(0.3);
    TCCare.press(T, 'feed'); run(0.3); TCCare.press(T, 'pick:apple'); until(pushLive, 30); run(0.3);
    const p1 = TCCare.pushPress(T); LEFT = 1; run(0.6); const live1 = pushLive();
    const p2 = TCCare.pushPress(T); LEFT = 0; run(0.2); const p3 = TCCare.pushPress(T); run(0.8);
    check(p1 === true && live1 && p2 === true && p3 === false && !pushLive() && S.stock === 7, `まとめて 使う：のこり 2回 → 2回 押せて、0回に なったら PUSH が 消える（3回めは 押せない・トークンは 2こ だけ へる：のこり ${S.stock}）`);
    until(() => S.phase === 'idle' && !S.mode && !S.push, 30); run(0.8); S.fx = S.fx.filter(f => f.k !== 'tagUI'); const e1 = EV.length;
    TCCare.press(T, 'feed'); run(0.3);
    check(!S.chooser && S.phase === 'idle' && S.fx.some(f => f.k === 'tagUI' && f.txt === 'この 馬の 抽選は おわったよ') && EV.slice(e1).some(e => e.k === 'wait'), 'のこり 0回：ごはんは 始まらない → 札「この 馬の 抽選は おわったよ」');
    LEFT = Infinity; run(1.4); S.fx = S.fx.filter(f => f.k !== 'tagUI'); TCCare.press(T, 'feed'); run(0.3);
    check(!!S.chooser, 'いつもの 馬（上限 なし）は 今までどおり'); TCCare.press(T, 'chback'); run(0.5); }
  // 条件の 札（幻の馬・神様馬）：2行めは「抽選 ○/○回」・神様馬（上限 5回＝リセットの 回数 以下）は 切り替わりタイマーの 行 なし
  { const R = TCCare.vinfoRows, k = R({ kind: 'kamisama', left: 1576, n: 5, need: 5, timer: 119, draws: 3, max: 5 }), m = R({ kind: 'maboroshi', left: 59, n: 5, need: 5, timer: null, draws: 10, max: 10 }), o = R({ kind: 'x', left: 100, n: 2, need: 5, timer: 30 });
    check(JSON.stringify(k.map(r => r.slice(0, 3))) === '[["タイムリミット","26:16",false],["抽選","3/5回",false]]'
      && JSON.stringify(m.map(r => r.slice(0, 3))) === '[["タイムリミット","0:59",true],["抽選","10/10回",true],["切り替わりタイマー","5回で スタート",false]]'
      && JSON.stringify(o.map(r => r.slice(0, 2))) === '[["タイムリミット","1:40"],["お世話","2/5回"],["切り替わりタイマー","0:30"]]',
      `条件の 札：神様馬＝2行（タイムリミット・抽選 3/5回）／幻の馬＝3行（抽選 10/10回は 赤）／上限の ない とき＝前と 同じ 3行（${JSON.stringify(k.map(r => r[1]))} ${JSON.stringify(m.map(r => r[1]))}）`); }
  console.log(`\n${ok} OK / ${ng} NG`); process.exit(ng ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
