// トレーニングセンターの お世話の きまり（tc/tc_care.js）を 画面なしで ためす（第4.151版・まさちゃん 2026/11/11 09:07・09:45）
//   node test_tc_care.js
//   ・撫でる：つづけて 5回まで → 5回目が おわったら 7秒 できない（さわっても・ボタンを 押しても「あと N秒」）→ 7秒で また できる・7秒 あけたら 数え直し
//   ・つづけて 撫でた とき：前の 反応を 止める（cut）・前の 回の あとの 動き（はしゃぐ）は 出ない
//   ・ハート 10こ → 抽選は 反応が おわって から・はしゃぐ は 出ない・ごろんの ときに のこった 反応は ぜんぶ 止めて ある
//   ・呼ぶ：つづけて 5回まで → 5回目が おわったら 7秒 できない
//   ・早く 始まる：撫でる・ごはんは 歩かないで その場で 横向きに（急ぎ足 hurry）・カメラは 押した ときから 寄る・仕上げの ズームは 待たない
//     呼ぶ（近づく・甘える）は いちばん 手前まで 歩かない・着いたら 急ぎ足を もどす
//   ・おそうじ（第4.152版）：ゴミ（BR.trash）か うんちが ある とき だけ・1回で ぜんぶ・ほうきで 山を 押して ちりとりの 口へ・さわらない まま 25秒で のこりも 片付く
//     おそうじの あと：お花も キラッ も 出さない・くんくんの 間に ボタンを 押すと すぐ 次の お世話
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
  console.log('おそうじ（第4.152版：ゴミか うんちが ある とき だけ・ほうきで ちりとりへ）');
  const SRC = fs.readFileSync(path.join(__dirname, 'tc', 'tc_care.js'), 'utf8');
  const sweepTo = Tg => {      // 山の 右に 指を 置く（ちりとりは 左へ 回りこむ）→ 山を 通って ちりとりの 口まで なぞる
    const C = S.clean, o = Tg.o, from = [o.x + 140, o.y + 6]; TCCare.input('down', from[0], from[1], T);
    const pn = { x: C.pan.x, y: C.pan.y };
    for (let i = 1; i <= 30 && !Tg.done; i++) { run(1 / 60); TCCare.input('move', from[0] + (pn.x - from[0]) * i / 30, from[1] + (pn.y - from[1]) * i / 30, T); }
    TCCare.input('up', pn.x, pn.y, T); run(0.05); return pn;
  };
  const pile = (x, y, i) => ({ x, y, sd: i, items: [{ k: i % 4, dx: 0, dy: 0, r: 0, w: 0.4, d: 0 }] });
  until(() => S.phase === 'idle', 30);
  BR.poops = []; BR.trash = []; S.trashIn = 620; let st0 = S.stock, w0 = evs('wait').length;
  TCCare.press(T, 'clean');
  check(S.phase === 'idle' && S.mode == null && S.stock === st0 && evs('wait').length === w0 + 1 && S.fx.some(f => f.k === 'tagUI' && f.txt === 'ゴミは あと 11分で 出るよ'), 'ゴミも うんちも ない → おそうじ できない（「ゴミは あと 11分で 出るよ」・トークンは 使わない）');
  BR.poops = [{ x: 600, y: 1200, img: 0, w: 0.42 }]; let tk = T;
  TCCare.press(T, 'clean'); check(S.mode === 'clean' && S.stock === st0 - 1 && BR.poops[0].sw === true && !BR.trashDone, 'うんちが ある → おそうじ できる（トークン −1）');
  until(() => S.phase === 'clean', 3);
  { const C = S.clean; check(S.zDur === 0.5 && S.zoom.z > 1.3 && C.tg.length === 1 && C.pan.x < 600 - 100 && Math.abs(C.pan.y - 1200) < 30, `うんち 1つ：カメラが 寄る（${S.zoom.z.toFixed(2)}倍・0.5秒）・ちりとりは うんちの 左`);
    sweepTo(C.tg[0]);
    check(C.tg[0].done && BR.poops.length === 0 && evs('inpan', tk).length === 1 && evs('sweep', tk).length === 1 && S.phase === 'cleanwait', 'ほうきで うんちを 押して ちりとりの 口へ → 片付く（1回 なぞる）'); }
  until(() => S.phase === 'after' || S.phase === 'idle', 12);
  check(evs('kira', tk).length === 1 && !S.fx.some(f => f.k === 'kira') && !('flowersAt' in S) && !/flowerArt\(p\[0\]/.test(SRC), 'おそうじの あと：お花も 地面の キラッ も 出さない（音の 合図 だけ）');
  check(S.phase === 'after' && BR.mode === 'walk' && BR.hurry === 2.8, 'うんちを 片付けた 所へ くんくん しに 行く（急ぎ足）');
  TCCare.press(T, 'feed'); check(S.phase === 'choose' && !!S.chooser && BR.hurry === 1, 'くんくんの 間に ごはんを 押す → すぐ えらぶ 札');
  TCCare.press(T, 'pick:apple'); const tp = T; until(() => S.phase === 'feed', 10);
  check(S.phase === 'feed' && T - tp < 3.2, `えらんで から 食べはじめる まで ${(T - tp).toFixed(2)}秒`);
  until(() => S.phase === 'idle', 30); check(S.phase === 'idle', 'ごはんの あと もとに もどる');
  console.log('ゴミ 5か所 ＋ 金のうんち');
  S.stock = S.stockShow = 6; BR.trash = [[300, 1000], [760, 980], [520, 1160], [250, 1290], [800, 1300]].map(([x, y], i) => pile(x, y, i)); BR.poops = [{ x: 430, y: 1240, img: 1, w: 0.5, gold: true }];
  S.high = 0; tk = T; TCCare.press(T, 'clean');
  check(S.mode === 'clean' && BR.trashDone === true && S.clean.tg.length === 6 && S.stock === 5, 'ゴミ 5か所と うんちを 1回（トークン 1つ）で ぜんぶ：押した ときに「片付けた」しるし（次の 15分が 始まる）');
  until(() => S.phase === 'clean', 3);
  { const C = S.clean; check(S.zoom.z < 1.25, `フィールド ぜんぶが 入る（ズーム ${S.zoom.z.toFixed(2)}倍）`);
    let n = 0; while (C.tg.some(q => !q.done) && n < 12) { const g0 = C.got; sweepTo(C.tg.find(q => !q.done)); n++; if (C.got === g0) break; }      // 指に いちばん 近い 山へ ちりとりが 回りこむ → 1回 なぞる ごとに 1つ
    check(C.tg.every(q => q.done) && C.got === 6 && n === 6 && evs('inpan', tk).length === 6 && evs('sweep', tk).length === 6, `6つ とも 1回ずつ なぞって ちりとりへ（${n}回 なぞって ${C.got}こ）`);
    check(S.phase === 'cleanwait' && C.foldT == null, 'ぜんぶ 入った → おしまいの 合図を 待つ');
    run(0.5); check(BR.trash.length === 0 && BR.poops.length === 0 && C.foldT != null, 'ゴミは 消えて、道具を たたむ'); }
  until(() => S.phase === 'after' || S.phase === 'idle', 12);
  check(evs('luck', tk).length === 1 && S.high === 5 && evs('kira', tk).length === 1, '金のうんち → 運がついた（高確ゾーン 5回）');
  until(() => S.phase === 'idle', 30); BR.trashDone = false;
  TCCare.press(T, 'clean'); check(S.phase === 'idle' && S.mode == null && S.stock === 5, 'つづけては できない（片付ける ものが ない）');
  console.log('とちゅうで さわらない → のこりを 片付けて おしまい');
  BR.trash = [pile(300, 1000, 0), pile(700, 1200, 1)]; BR.poops = []; tk = T; TCCare.press(T, 'clean'); until(() => S.phase === 'clean', 3);
  sweepTo(S.clean.tg[0]); check(S.clean.got === 1 && S.phase === 'clean', '1つ 片付けて 手を 止める');
  run(24.5); check(S.phase === 'clean' && S.clean.got === 1, '25秒 までは 待つ');
  run(1.2); check(S.phase === 'cleanwait' && S.clean.got === 2, '25秒 さわらない → のこりも ちりとりへ（とまった まま に ならない）');
  until(() => S.phase === 'idle', 30); BR.trashDone = false;
  console.log('はしの 山・馬が かわる');
  BR.trash = [pile(70, 800, 0)]; TCCare.press(T, 'clean'); until(() => S.phase === 'clean', 3);
  { const C = S.clean, q = C.pan; check(q.x >= 90 && q.x <= 1052 - 90 && q.y >= 790 && q.y <= 1430, `はしの 山でも ちりとりは フィールドの 中（${Math.round(q.x)}, ${Math.round(q.y)}）`);
    TCCare.input('down', 10, 806, T); const pn = { x: C.pan.x, y: C.pan.y };      // 外がわ（はし）から 内へ はく
    for (let i = 1; i <= 40 && !C.tg[0].done; i++) { run(1 / 60); TCCare.input('move', 10 + (pn.x - 10) * i / 40, 806 + (pn.y - 806) * i / 40, T); }
    TCCare.input('up', pn.x, pn.y, T); check(C.tg[0].done, 'はしの 山も 片付く'); }
  until(() => S.phase === 'idle', 30); BR.trashDone = false;
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
  until(() => S.phase === 'idle', 20); run(0.2);
  Object.assign(BR, { x: 120, y: 1200, dir: Math.PI / 2, mode: 'idle' }); TCCare.pressPet(T);
  check(S.phase === 'approach' && BR.mode === 'walk' && BR.tgt[0] === 1.75 * 200 + 12 + 44 && BR.tgt[1] === 1200 && !!S.zB, `横向きに なると 画面から はみ出す 所（x 120）→ 入る 所（x ${BR.tgt && BR.tgt[0]}：しっぽの がわ 1.75 ＋ よゆう 44）まで だけ 歩く`);
  until(() => S.phase === 'pet', 6); check(S.phase === 'pet' && Math.cos(BR.dir) > 0.9, '左の はしの 馬は 右向き（顔を まん中へ）で 撫でる');
  until(() => S.phase === 'idle', 20); run(0.2);
  // 第4.152版（バグ直し）：行き先が 近くて 向きが ちがう → 先に その場で 行き先を 向く（回りつづけない）・走って いる 馬でも 始まる
  Object.assign(BR, { x: 800, y: 955, dir: -1.63, mode: 'run' }); const tr0 = T; TCCare.pressPet(T);
  check(S.phase === 'approach' && BR.mode === 'turn' && Math.abs(Math.abs(BR.turnTo) - Math.PI) < 0.01 && S.route.length === 1, '右の はしを 走って いる 馬を 撫でる：入る 所（左へ 少し）が 近くて 向きが ちがう → 先に その場で 行き先を 向く');
  check(until(() => S.phase === 'pet', 6) && T - tr0 < 2 && BR.x <= 1052 - (1.75 * 200 + 12) && Math.cos(BR.dir) < -0.9, `向いて から 歩いて 着く → 左向き（顔を まん中へ）で 撫でられる（${(T - tr0).toFixed(2)}秒・x ${Math.round(BR.x)}）`);
  until(() => S.phase === 'idle', 20); run(0.2);
  Object.assign(BR, { x: 526, y: 1000, dir: 0, mode: 'idle' }); TCCare.pressPet(T); S.phase = 'approach'; S.route = [[526, 1300]]; BR.mode = 'walk'; BR.tgt = null; const ts0 = T;      // 着かない まま（にせの 馬は 行き先が ないと 動かない）
  run(5.2); check(S.phase !== 'idle' && S.route.length === 0, '5秒 たっても 着かない → 歩くのを やめる（安全の ため）');
  check(until(() => S.phase === 'pet', 4) && T - ts0 < 9, `そのまま その場で 撫でられる ように なる（${(T - ts0).toFixed(1)}秒・とまった まま に ならない）`);
  until(() => S.phase === 'idle', 20); run(0.2);
  S.stock = 5; Object.assign(BR, { x: 560, y: 820, dir: Math.PI / 2, mode: 'idle' }); TCCare.press(T, 'feed'); TCCare.press(T, 'pick:apple'); const tf = T;
  check(until(() => S.phase === 'feed', 5) && BR.y === 820 && T - tf < 1.0, `ごはん：えらんで から 食べはじめる まで ${(T - tf).toFixed(2)}秒（奥に いても その場）`);
  until(() => S.phase === 'idle', 30); run(0.2);
  Object.assign(BR, { x: 300, y: 700, dir: 0, mode: 'idle' }); TCCare.pressCall(T, 'come');
  check(BR.mode === 'walk' && BR.tgt[1] === 1040 && !S.zB && S.zoom.z === 1, `呼ぶ（近づく）：いちばん 手前（1372）まで 歩かない（行き先 y ${BR.tgt[1]}）・ズームは しない`);
  until(() => S.phase === 'idle', 20);
  Object.assign(BR, { x: 526, y: 1000, dir: 0, mode: 'idle' }); run(7.5); TCCare.pressCall(T, 'amae');
  check(BR.mode === 'walk' && BR.tgt[1] === 1230, `呼ぶ（甘える）：いまの 所から 230 だけ 手前（行き先 y ${BR.tgt[1]}）`);
  until(() => S.phase === 'idle', 20);
  console.log('おかわりの目（なでない まま）');
  until(() => S.phase === 'idle', 30); S.stock = S.stockShow = 5; Object.assign(BR, { x: 526, y: 1100, dir: 0, mode: 'idle' }); RND = 0.2;      // 0.2：おかわりの目（1/4）が 出る・ほかの 当たりは 出ない
  TCCare.press(T, 'feed'); TCCare.press(T, 'pick:apple'); until(() => S.phase === 'beg', 20); const tb = T;
  check(S.phase === 'beg', 'ごはんの あと おかわりの目（1/4）');
  run(6.0); check(S.phase === 'beg', '6秒 までは なでて もらうのを 待つ');
  check(until(() => S.phase === 'idle', 6) && T - tb < 10, `なでない まま 6.5秒 → そのまま おしまい（${(T - tb).toFixed(1)}秒で もとに もどる。前は なでる まで ずっと 待って いた）`);
  RND = 0.5;
  // 第4.154版（まさちゃん 11/11 20:00「テスト版で…お世話の当選パターン全種類テストできるようにして！」）：テスト版の 道具が 使う S.test
  //   名前が あれば 次の 1回 だけ その 結果（使ったら 消える）・なければ いつもの くじ（rnd）。App Store版では S.test は いつも null
  console.log('テスト版の 道具（S.test：次の 1回 だけ 結果を 決める）');
  until(() => S.phase === 'idle', 30); RND = 0.99;      // 0.99：金のニンジン・おかわりの目・首を かしげる・ほうきを かじる・ハートの 当たりは どれも 出ない 数。呼ぶは「甘える」
  check(S.test === null, 'ふだんは S.test＝null');
  S.stock = S.stockShow = 9; Object.assign(BR, { x: 526, y: 1100, dir: 0, mode: 'idle' });
  TCCare.press(T, 'feed'); TCCare.press(T, 'pick:carrot'); until(() => S.phase === 'feed', 10);
  check(S.feed && S.feed.gold === false, '決めて いない → ニンジンは ふつう（いつもの くじ）');
  until(() => S.phase === 'idle', 30); check(!evs('beg', T - 12).length, '決めて いない → おかわりの目は 出ない');
  S.test = { gold: true, beg: true };
  TCCare.press(T, 'feed'); TCCare.press(T, 'pick:apple'); until(() => S.phase === 'feed', 10);
  check(S.feed.gold === false && S.test.gold === true, 'gold：リンゴでは 使わない（次の ニンジン まで のこる）');
  check(until(() => S.phase === 'beg', 20) && !('beg' in S.test), 'beg：ごはんの あと おかわりの目（使ったら 消える）');
  until(() => S.phase === 'idle', 30);
  let h1 = S.heart; S.got = [];
  TCCare.press(T, 'feed'); TCCare.press(T, 'pick:carrot'); until(() => S.phase === 'feed', 10);
  check(S.feed.gold === true && !('gold' in S.test), 'gold：次の ニンジンは 金のニンジン（使ったら 消える）');
  until(() => S.phase === 'idle', 30); check(S.heart === Math.min(10, h1 + 3) && !evs('beg', T - 8).length, '金のニンジン → なかよし ＋3・おかわりの目は もう 出ない（1回 だけ）');
  TCCare.press(T, 'feed'); TCCare.press(T, 'pick:carrot'); until(() => S.phase === 'feed', 10);
  check(S.feed.gold === false, 'その 次の ニンジンは ふつう（いつもの くじに もどる）'); until(() => S.phase === 'idle', 30);
  // 呼ぶ
  run(7.5); TCCare.pressCall(T); check(S.callKind === 'amae', '決めて いない → 呼ぶは いつもの くじ（0.99 → 甘える）'); until(() => S.phase === 'idle', 20);
  for (const k of ['come', 'turn']) { run(7.5); S.test = Object.assign(S.test || {}, { call: k }); TCCare.pressCall(T); check(S.callKind === k && !('call' in S.test), `call：次の 呼ぶは「${k}」（使ったら 消える）`); until(() => S.phase === 'idle', 20); }
  // 撫でる：首を かしげる・ハートの 抽選（当たり）
  until(() => T >= S.coolUntil + 0.2, 10); S.got = []; S.heart = S.heartShow = 0;
  S.test = { rare: true }; let tt0 = T; TCCare.pressPet(T); until(() => S.phase === 'pet', 6); pet(); run(0.5);
  check(evs('tilt', tt0).length === 1 && !('rare' in S.test), 'rare：次に なでると 首を かしげる（使ったら 消える）');
  pet(); run(0.5); check(evs('tilt', tt0).length === 1, 'その 次は いつもの 反応');
  until(() => S.phase === 'idle', 30); until(() => T >= S.coolUntil + 0.2, 10);
  S.got = []; S.heart = S.heartShow = 9; S.test = { win: true }; const st1 = S.stock; tt0 = T;
  TCCare.pressPet(T); until(() => S.phase === 'pet', 6); pet();
  check(until(() => S.lot && S.lot.win === true, 12) && !('win' in S.test), 'win：ハート 10こ の 抽選は 当たり（使ったら 消える）');
  until(() => S.phase === 'idle' && !S.busy, 30);
  check(S.stock === st1 + 5 && evs('unlock', tt0).length === 1 && S.heart === 0, '当たり → ぴょん！・お世話トークン ＋5・ハートは 0 から');
  until(() => T >= S.coolUntil + 0.2, 10); S.got = []; S.heart = S.heartShow = 9; S.test = { win: false }; tt0 = T;
  TCCare.pressPet(T); until(() => S.phase === 'pet', 6); pet();
  check(until(() => S.lot && S.lot.win === false, 12), 'win＝false：ハズレ（ごろん）も えらべる');
  until(() => S.phase === 'idle' && !S.busy && BR.mode !== 'sleep', 30);
  // おそうじ：ほうきを かじる（馬の 顔の 近くで 2つ目を 片付けた とき）
  S.stock = S.stockShow = 9; Object.assign(BR, { x: 526, y: 1100, dir: 0, mode: 'idle' }); BR.trashDone = false;
  const two = () => { BR.poops = []; BR.trash = [pile(300, 1250, 0), pile(850, 950, 1)]; TCCare.press(T, 'clean'); until(() => S.phase === 'clean', 3); const C = S.clean; sweepTo(C.tg[0]); sweepTo(C.tg[1]); run(0.4); };
  tt0 = T; two(); check(evs('nibble', tt0).length === 0, '決めて いない → ほうきは かじらない（0.99）'); until(() => S.phase === 'idle', 30); BR.trashDone = false;
  S.test = { nibble: true }; tt0 = T; two(); check(evs('nibble', tt0).length === 1 && !('nibble' in S.test), 'nibble：次の おそうじで ほうきを かじる（使ったら 消える）'); until(() => S.phase === 'idle', 30); BR.trashDone = false;
  S.test = null; RND = 0.5;
  // 第4.154版（バグ直し）：幻の馬・神様馬が 帰った あとの ルーレット・チケットで、帰った 馬の 降臨の バナーが また 出ない
  console.log('降臨の バナー（帰った あとは 出し直さない）');
  until(() => S.phase === 'idle', 30);
  const banOn = () => !!(S.ban && S.ban.hideT == null && S.ban.showT != null);
  await TCCare.special('kamisama'); run(1.0); check(banOn() && S.ban.shown && evs('banin', T - 2).length === 1, '神様馬が 来た → 降臨の バナーが 出る');
  TCCare.roulette(true); run(0.5); const r1 = banOn(); TCCare.roulette(false); run(1.0);
  check(!r1 && banOn() && S.ban.shown, 'いる 間の ルーレット：演出の 間は 消えて、おわったら また 出る（前と 同じ）');
  TCCare.special(null); run(0.6); check(!banOn(), '帰った → バナーは 消える');
  const bi = evs('banin').length; TCCare.roulette(true); run(0.5); TCCare.roulette(false); run(1.5);
  check(!banOn() && evs('banin').length === bi, '帰った あとの ルーレット・チケット：バナーは また 出ない（前は 出て、そのまま 残って いた）');
  await TCCare.special('maboroshi'); run(1.0); check(banOn() && S.ban.kind === 'maboroshi' && !S.ban.gone, 'つぎに 幻の馬が 来たら 新しい バナーが 出る');
  TCCare.special(null); run(0.6);
  console.log(`\n${ok} OK / ${ng} NG`); process.exit(ng ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
