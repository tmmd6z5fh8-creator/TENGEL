// トレーニングセンターの「お世話チャレンジ」（玉を 落とす 台：App Store版・第4.173版）
//   まさちゃん 2026/11/14 23:34「トレーニングセンターの抽選を、今のボタンと、もう一つボール落としができるようにしたい！ パチンコ台は俺が3Dで作ってくる！…
//     パチンコを選択すると5個玉を落とすことができる。お世話トークンが5個以上ある場合は、5回の抽選が終わったら、続けてやる、終わり、を選べるボタンがでてくる。
//     玉を落とす、のボタンがあるから押したら、台の上側に付いてる受け皿から玉が一つおちる、台のグギに当たって下にある４つのコップどれかに入る。
//     違和感なく、データに問題がない範囲で事前に玉が落ちる演出は、十何パターンか作成してランダムで使用して！…
//     確率とかは、今の抽選のままだから4つのどれかに入った時に抽選で当たっていたら中央の先バレ液晶が綺麗に光る！
//     先バレの光る色(示唆) 10P〜300Pは、青／ルーレット1/125は、緑／ルーレット1/245は、紫／ルーレット1/399は、赤／幻の馬ルーレットは、金／神様馬ルーレットとチケット扉は、虹色」
//   23:40「1個1トークン・（保留は）5マスでいいよ！・（ポイント特化ゾーンは）金色！」
//   11/15 00:40「馬バレは、コップに玉が入って、当選した瞬間に、音と一緒に、馬バレ用の所が当選の色のデザインと光が付く仕組みにして！
//     青から虹色にかけて光りは激しく大きくして！光のイメージはオーラみたいなイメージで馬バレのところを光らせて！」
//   00:48「馬バレ音 ①青:ピピィーン ②緑:ピピピィーン ③紫:ピピピピィーン ④赤:ピピピピピィーン ⑤金:ドゥゴーンとピピピピピィーン(同時)
//     ⑥虹色: キュイキュイキュイとドゥゴーンとビィボォーンとピピピピピィーン」（音は kisekae/tc/snd/sfx_drop.py）
//   01:08「サイズ合うなら馬バレアイコンの金の枠無くして、馬バレの縁に合わせた方が綺麗かもね！」（馬バレの 絵は 中の 丸 だけを 台の 黄色い 縁に はめる）
//
//   ・台＝まさちゃんの 3D（Meshy）を 正面から 描いた 絵（tc_dp_base.webp）。玉より 手前の 所（釘の 先・コップの 前の かべ）は 別の 絵（tc_dp_front.webp）を 玉の 上に 重ねる
//     ＝玉は 釘の 先の うしろを 通って、コップの 中へ 入ると 前の かべに かくれる。絵と 場所・玉の 落ち方（tc_dp.json）は kisekae/tc/drop/ の 道具が 作る（リポジトリには 入れない）
//   ・玉＝姫が 作った 3D（赤い 折り紙の 多面体：tc_dp_ball.webp＝ころがる 向きに 回した 32コマ）
//   ・落ち方＝台の 釘・コップの 形で 物理の 計算を して 先に 作った 16とおり（コップごとに 4つ）。その 中から でたらめに 1つ（同じ ものは つづけない）。どの コップに 入っても 結果は 同じ
//   ・抽選＝今の お世話の 抽選と 同じ（tc_app.js の draw）。玉 1こ＝お世話トークン 1こ＝お世話 1回。玉を 落とした 瞬間に 結果を 決めて 保存（途中で 閉じても なくならない・2回 もらえない）
//   ・玉が コップに 入った 瞬間：当たって いれば 音と いっしょに 馬バレ（まん中の 丸）が その 色の 絵に かわって オーラが 出る（青 → 虹で 大きく 激しく）→ 当たりは「当選」の ます（5つ）に たまる
//   ・玉を ぜんぶ 落とした ら「保留結果を見る」の かぎが あく → 押すと たまった 当たりを 順に わたす（ポイントは 札・ルーレット／ポイント特化ゾーン／チケットは いつもの 演出：api.show）
//   ・おわったら：お世話トークンが 5こ 以上 のこって いれば「続けてやる」「終わり」・なければ「終わり」だけ
//   ・ちかちか しない：光は 1回 ふわっと 明るく なって ゆっくり 息を する（1秒に 3回 より おそい）。「演出を控えめにする」（TengelFx.calm）の ときは 回らない・とばない
//   TCDrop.load()（絵と データを 読む：true＝そろった）・TCDrop.ready()・TCDrop.open(stage, api, opt) → Promise<{ used }>・TCDrop.close()・TCDrop.isOpen()
//     api：stock()＝のこりの トークン・left()＝あと 何回 抽選 できるか・drop()＝トークンを 1つ 使って 抽選 → { ok, z（当たり か null）, c（色 1〜6） }・
//          show(z)＝当たりを わたす（演出つき・Promise）・se(名前, 大きさ)＝音・high()＝高確ゾーンの のこり・holds()＝まだ わたして いない 当たり（開き直した とき）
const TCDrop = (() => {
  const W = 1052, H = 1657, TAU = Math.PI * 2;
  const FONT = '"BIZ UDPGothic", BIZ, "Hiragino Sans", "Noto Sans CJK JP", sans-serif';
  const AP = p => (typeof window !== 'undefined' && typeof window.TC_ASSET === 'function' ? window.TC_ASSET(p) : p);
  const clamp = (x, a, b) => Math.max(a, Math.min(b, x)), sm = x => { x = clamp(x, 0, 1); return x * x * (3 - 2 * x); };
  const lerp = (a, b, u) => a + (b - a) * u;
  const backOut = x => { x = clamp(x, 0, 1); const c = 1.7; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
  const easeOut = x => 1 - Math.pow(1 - clamp(x, 0, 1), 3);
  const hash = n => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
  const BALLS = 5;                                    // 1回り＝玉 5こ まで
  const IMG_H = 1632;                                 // 舞台（1052×1657）の 中の 台の 高さ
  // 色（1 青・2 緑・3 紫・4 赤・5 金・6 虹）ごとの 光：rgb・オーラの 大きさ（R：黄色い 縁の 何倍 まで 色が とどくか）・こさ（a）・台を 暗く する 度合い（dim）・光の すじの 数（rays）・
  //   オーラの 炎の 数（nt）と 長さ（tl：縁の 半径の 何倍）・はげしい 間（len 秒）・その あとの 落ちついた 強さ（keep）・保留が とび出す 時（hold 秒）・次の 玉を 落とせる まで（lock 秒：音が 鳴り おわる ころ）
  const TONE = [null,
    { rgb: [60, 150, 255], R: 2.0, a: 0.62, dim: 0.14, rays: 0, nt: 14, tl: 0.62, len: 1.0, keep: 0.50, hold: 0.50, lock: 0.95 },
    { rgb: [50, 220, 100], R: 2.5, a: 0.68, dim: 0.18, rays: 0, nt: 18, tl: 0.88, len: 1.15, keep: 0.50, hold: 0.55, lock: 1.05 },
    { rgb: [180, 95, 255], R: 3.1, a: 0.74, dim: 0.23, rays: 10, nt: 22, tl: 1.18, len: 1.3, keep: 0.52, hold: 0.62, lock: 1.2 },
    { rgb: [255, 62, 52], R: 3.8, a: 0.82, dim: 0.29, rays: 12, nt: 28, tl: 1.55, len: 1.5, keep: 0.54, hold: 0.72, lock: 1.35 },
    { rgb: [255, 196, 48], R: 4.7, a: 0.90, dim: 0.37, rays: 16, nt: 34, tl: 2.05, len: 2.1, keep: 0.56, hold: 1.05, lock: 2.0 },
    { rgb: [255, 255, 255], R: 6.0, a: 1.0, dim: 0.46, rays: 20, nt: 44, tl: 2.7, len: 2.5, keep: 0.60, hold: 1.35, lock: 2.4 }];
  const HUES = [[255, 70, 70], [255, 160, 50], [255, 232, 70], [80, 235, 110], [70, 170, 255], [150, 110, 255], [240, 110, 230]];      // 虹の 7色
  const NAME = [null, '青', '緑', '紫', '赤', '金', '虹'];
  const MISS_LOCK = 0.32, FLY = 0.36;                 // はずれの あと 次の 玉まで・保留が ますへ とぶ 長さ（秒）

  let D = null, IM = null, loading = null, GLOW = null;
  let cv = null, g = null, K = 1, MS = 1, MX = 0, MY = 0, cache = null, cacheKey = '';
  let S = null, API = null, stageEl = null, raf = 0, lastNow = 0, done = null, T = { speed: 1, path: null, log: [] };
  const calm = () => { try { return !!(window.TengelFx && window.TengelFx.calm && window.TengelFx.calm()); } catch (e) { return false; } };

  // ---------- 読みこみ ----------
  function img(src) {                                 // 絵を 読む（読めたら ひらいて おく：はじめて 台を 出す コマで 止まらない）
    return new Promise(ok => { const i = new Image(); i.onload = () => { const d = i.decode ? i.decode().catch(() => { }) : null; if (d && d.then) d.then(() => ok(i)); else ok(i); }; i.onerror = () => ok(null); i.src = AP(src); });
  }
  function load() {
    if (loading) return loading;
    loading = (async () => {
      let d = null;
      try { const r = await fetch(AP('tc_dp.json')); if (!r.ok) throw new Error('no data'); d = await r.json(); } catch (e) { return false; }
      if (!d || d.v !== 1 || !Array.isArray(d.paths) || !d.paths.length) return false;
      const names = ['tc_dp_base.webp', 'tc_dp_front.webp', 'tc_dp_see.webp', 'tc_dp_ball.webp'];
      for (let c = 1; c <= 6; c++) names.push('tc_dp_uma' + c + '.webp', 'tc_dp_hold' + c + '.webp');
      const ims = await Promise.all(names.map(img));
      if (ims.some(i => !i)) return false;
      IM = { base: ims[0], front: ims[1], see: ims[2], ball: ims[3], uma: [null], hold: [null] };
      for (let c = 1; c <= 6; c++) { IM.uma.push(ims[2 + 2 * c]); IM.hold.push(ims[3 + 2 * c]); }
      D = d; MS = IMG_H / d.img[1]; MX = (W - d.img[0] * MS) / 2; MY = 19;
      return true;
    })();
    loading.then(ok => { if (!ok) loading = null; });      // 読めなかった ときは 次に もう一度 ためせる
    return loading;
  }
  const ready = () => !!(D && IM);
  function glows() {                                  // 光の 絵：やわらかい 丸（粒）と 炎の 1本（根元が 太く 先へ 消える）。色ごとに 1まい
    if (GLOW) return GLOW;
    const lite = (rgb, k) => rgb.map(v => Math.round(v + (255 - v) * k));
    const mk = rgb => { const c = document.createElement('canvas'); c.width = c.height = 96; const q = c.getContext('2d'), gr = q.createRadialGradient(48, 48, 0, 48, 48, 48), l = lite(rgb, 0.7);
      gr.addColorStop(0, `rgba(${l[0]},${l[1]},${l[2]},0.95)`); gr.addColorStop(0.25, `rgba(${rgb[0]},${rgb[1]},${rgb[2]},0.75)`); gr.addColorStop(0.6, `rgba(${rgb[0]},${rgb[1]},${rgb[2]},0.22)`); gr.addColorStop(1, `rgba(${rgb[0]},${rgb[1]},${rgb[2]},0)`);
      q.fillStyle = gr; q.fillRect(0, 0, 96, 96); return c; };
    const mt = rgb => { const c = document.createElement('canvas'); c.width = 128; c.height = 64; const q = c.getContext('2d'), l = lite(rgb, 0.45);
      q.translate(0, 32); q.scale(1, 0.25); const gr = q.createRadialGradient(0, 0, 0, 0, 0, 128);
      gr.addColorStop(0, `rgba(${l[0]},${l[1]},${l[2]},0.9)`); gr.addColorStop(0.3, `rgba(${rgb[0]},${rgb[1]},${rgb[2]},0.62)`); gr.addColorStop(0.7, `rgba(${rgb[0]},${rgb[1]},${rgb[2]},0.2)`); gr.addColorStop(1, `rgba(${rgb[0]},${rgb[1]},${rgb[2]},0)`);
      q.fillStyle = gr; q.beginPath(); q.arc(0, 0, 128, 0, TAU); q.fill(); return c; };
    const gold = [255, 214, 90];
    GLOW = { tone: [null], hue: HUES.map(mk), tong: [null], thue: HUES.map(mt) };
    for (let c = 1; c <= 6; c++) { const rgb = c === 6 ? gold : TONE[c].rgb; GLOW.tone.push(mk(rgb)); GLOW.tong.push(mt(rgb)); }
    return GLOW;
  }

  // ---------- 時計・予定 ----------
  const now = () => S.t;
  const later = (dt, fn) => { S.sched.push({ t: S.t + dt, fn }); };
  const wait = dt => new Promise(ok => later(dt, ok));
  const se = (name, gain) => { T.log.push(name); if (T.log.length > 200) T.log.splice(0, 100); if (T.rec) T.rec.push([S ? +S.t.toFixed(4) : 0, name, gain == null ? 1 : gain]); try { if (API && API.se) API.se(name, gain == null ? 1 : gain); } catch (e) { /* なし */ } };

  // ---------- 流れ ----------
  function roundMax() { return Math.max(0, Math.min(BALLS, API.stock(), API.left())); }
  function newRound() {
    S.max = roundMax(); S.n = 0; S.holds = []; S.ball = null; S.old = []; S.next = S.max > 0 ? { t0: S.t } : null; S.lcd = null; S.unlockT = null; S.endT = null; S.none = null; S.sum = 0; S.tk = 0; S.roundT = S.t;
    S.phase = S.max > 0 ? 'ready' : 'end';
    if (S.phase === 'end') endChoice();
  }
  function pickPath() {                                // 落ち方を 1つ：まぜた 山から 引く（山が なくなる まで 同じ ものは 出ない・つぎの 山の はじめも 前と 同じに しない）
    if (T.path != null) { const i = T.path; T.path = null; return i % D.paths.length; }
    if (!S.deck || !S.deck.length) {
      const d = D.paths.map((_, i) => i);
      for (let i = d.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [d[i], d[j]] = [d[j], d[i]]; }
      if (d.length > 1 && d[d.length - 1] === S.lastPath) [d[0], d[d.length - 1]] = [d[d.length - 1], d[0]];
      S.deck = d;
    }
    const i = S.deck.pop(); S.lastPath = i; return i;
  }
  function pressGo() {                                 // 「玉を落とす」
    if (S.phase !== 'ready' || S.ball || S.t < S.lock || S.n >= S.max) return false;
    const r = API.drop();
    if (!r || !r.ok) { finishDrops(); return false; }
    S.n++; S.used++; S.press.go = S.t; S.next = null;
    if (S.lcd && S.lcd.off == null) S.lcd.off = S.t;                    // 前の 馬バレは 消える
    const pi = pickPath();
    S.ball = { p: D.paths[pi], pi, t0: S.t, hi: 0, inT: null, z: r.z || null, c: r.z ? (r.c || 1) : 0 };
    S.phase = 'fall'; se('dp_out');
    return true;
  }
  function ballIn(b) {                                 // 玉が コップに 入った
    b.inT = S.t; se('dp_cup', 0.9);
    S.fx.push({ k: 'cup', t0: S.t, cup: b.p.cup });
    if (b.z) later(0.12, () => reveal(b));
    else { later(0.16, () => se('dp_miss', 0.8)); S.lock = S.t + MISS_LOCK; later(MISS_LOCK, afterBall); }
  }
  function reveal(b) {                                 // 馬バレ：音と いっしょに 色の 絵と オーラ
    const c = b.c, tn = TONE[c];
    S.lcd = { c, t0: S.t, off: null };
    se('dp_uma' + c);
    const slot = S.holds.length;
    const h = { z: b.z, c, slot, t: null, fly: S.t + tn.hold, state: 'fly' };
    S.holds.push(h);
    later(tn.hold + FLY, () => { h.t = S.t; h.state = 'in'; se('dp_hold', 0.9); });
    S.lock = S.t + tn.lock; later(tn.lock, afterBall);
  }
  function afterBall() {
    if (S.phase !== 'fall') return;
    if (S.ball && S.ball.inT != null) { S.old.push(S.ball); S.ball = null; }      // コップの 中で 落ちつく までの 玉は そのまま 描く（次の 玉を 待たせない）
    if (S.n >= S.max || API.stock() < 1 || API.left() < 1) finishDrops();
    else { S.phase = 'ready'; S.next = { t0: S.t }; }
  }
  function finishDrops() {                             // 玉を 落とし おわった（やめる でも）
    S.next = null;
    if (S.lcd && S.lcd.off == null) S.lcd.off = S.t + 0.5;              // さいごの 馬バレは 少し して 消える（保留の ますと 結果が 見やすい）
    if (S.holds.length) { S.phase = 'wait'; S.unlockT = S.t; se('dp_open'); }
    else { S.phase = 'none'; S.none = S.t; later(1.5, endChoice); }
  }
  function pressSee() {                                // 「保留結果を見る」
    if (S.phase !== 'wait' || S.t < S.unlockT + 0.25) return false;
    S.phase = 'res'; S.press.see = S.t; se('button');
    runSee(S.gen).catch(() => { });
    return true;
  }
  async function runSee(gen) {                         // たまった 当たりを 順に わたす。途中で 閉じた とき（live が false）は そこで やめる（のこりは アプリが おぼえて いる）
    const live = () => !!S && S.gen === gen;
    await wait(0.35);
    for (const h of S.holds) {
      if (!live()) return;
      h.state = 'show'; h.showT = S.t; S.cur = h;
      await wait(0.4); if (!live()) return;
      const z = h.z;
      if (z.k === 'pt') {
        S.pop = { v: z.v, t0: S.t, c: h.c }; se(z.v >= 200 ? 'dedeen' : 'piron');
        try { await API.show(z); } catch (e) { /* なし */ }
        if (!live()) return;
        S.sum += +z.v || 0;
        await wait(1.25);
      } else {
        if (z.k === 'rt' || z.k === 'zn') { S.cue = { t0: S.t, txt: z.k === 'zn' ? '特化ゾーン！' : 'ルーレット！' }; se('kyuin'); await wait(1.0); if (!live()) return; }
        S.hold = true; S.holdT = S.t;                  // いつもの 演出（ルーレット・ポイント特化ゾーン・チケット）の 間は 台を かくす（フィールドの 上に いつもの 見え方で 出る）
        let v = 0; try { v = await API.show(z); } catch (e) { /* なし */ }
        if (!live()) return;
        S.hold = false; S.holdT = S.t; S.sum += +v || 0; if (z.k === 'tk') S.tk += z.n || 1;
        await wait(0.45);
      }
      if (!live()) return;
      h.state = 'done'; h.doneT = S.t; S.cur = null;
      await wait(0.3);
    }
    if (!live()) return;
    await wait(0.25); if (!live()) return;
    endChoice();
  }
  function endChoice() {                               // 「続けてやる」「終わり」
    S.phase = 'end'; S.endT = S.t; S.more = API.stock() >= BALLS && API.left() >= 1;
  }
  function pressMore() { if (S.phase !== 'end' || !S.more || S.t < S.endT + 0.35) return false; se('button'); S.press.more = S.t; newRound(); return true; }
  function pressEnd() { if (S.phase !== 'end' || S.t < S.endT + 0.35) return false; se('fold'); finish(); return true; }
  function pressQuit() {                               // 「やめる」：まだ 落として いなければ 閉じる・落とした あとなら そこで 投入 おしまい
    if (S.phase !== 'ready' || S.ball || S.t < S.lock) return false;
    se('button'); S.press.quit = S.t;
    if (S.n === 0 && !S.holds.length) finish(); else finishDrops();
    return true;
  }
  function finish(aborted) {
    const r = { used: S ? S.used : 0, aborted: !!aborted };
    stop();
    const d = done; done = null; S = null;
    if (d) d(r);
  }

  // ---------- 開く・閉じる ----------
  function open(stage, api, opt) {
    opt = opt || {};
    if (!ready() || S) return Promise.resolve({ used: 0, aborted: true });
    stageEl = stage; API = api;
    cv = stage.querySelector('canvas.tcdp');
    if (!cv) { cv = document.createElement('canvas'); cv.className = 'tcdp'; cv.setAttribute('role', 'img'); cv.setAttribute('aria-label', 'お世話チャレンジ'); stage.insertBefore(cv, stage.querySelector('canvas.tcfx')); }
    cv.style.cssText = 'position:absolute;left:0;top:0;width:100%;height:100%;display:block;touch-action:none;opacity:1';      // 重なりは DOM の 順：お世話の 絵の 上・当たりの 演出（.tcfx）の 下
    g = cv.getContext('2d'); glows();
    S = { t: 0, gen: (T.gen = (T.gen || 0) + 1), phase: 'ready', max: 0, n: 0, used: 0, holds: [], ball: null, old: [], next: null, lcd: null, lock: 0.45, fx: [], sched: [], press: {}, lastPath: -1, sum: 0, openT: 0, hold: false, cur: null, pop: null, cue: null, unlockT: null, endT: null, none: null, more: false, roundT: 0, deck: null, tk: 0, holdT: -9, op: 1 };
    T.log.length = 0;
    const pend = opt.resume && api.holds ? api.holds() : [];
    if (pend.length) {                                 // 前に 閉じた ときに 残った 当たり：すぐ「保留結果を見る」から
      S.holds = pend.slice(0, BALLS).map((z, i) => ({ z, c: z.c || 1, slot: i, t: -9, fly: -9, state: 'in' }));
      S.phase = 'wait'; S.unlockT = 0.2;
    } else newRound();
    cv.addEventListener('pointerdown', onDown);
    document.addEventListener('visibilitychange', onVis);
    lastNow = 0; raf = requestAnimationFrame(frame);
    return new Promise(ok => { done = ok; });
  }
  function stop() {
    cancelAnimationFrame(raf); raf = 0;
    if (cv) { cv.removeEventListener('pointerdown', onDown); cv.style.display = 'none'; try { g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, cv.width, cv.height); } catch (e) { /* なし */ } }
    document.removeEventListener('visibilitychange', onVis);
  }
  function close() { if (S) finish(true); }           // 外から（トレーニングセンターを 閉じた）：わたして いない 当たりは アプリが おぼえて いる
  const isOpen = () => !!S;
  function onVis() { if (!S) return; if (document.hidden) { cancelAnimationFrame(raf); raf = 0; } else if (!raf) { lastNow = 0; raf = requestAnimationFrame(frame); } }

  // ---------- 指 ----------
  const inBox = (b, x, y, pad) => x >= b[0] - pad && x <= b[2] + pad && y >= b[1] - pad && y <= b[3] + pad;
  const QUIT = { x: 122, y: 62, w: 204, h: 84 }, ENDC = { y: 960, w: 880, h: 600 }, ENDB = { y: 1146, w: 380, h: 150, gap: 36 };      // やめる・おしまいの 札（まん中・大きさ）・その 中の ボタン
  function hit(xd, yd) {                               // 舞台の 座標 → 何を 押したか
    const xi = (xd - MX) / MS, yi = (yd - MY) / MS;
    if (S.phase === 'end') {
      const cx = S.more ? [W / 2 - ENDB.w / 2 - ENDB.gap / 2, W / 2 + ENDB.w / 2 + ENDB.gap / 2] : [null, W / 2];
      if (S.more && Math.abs(xd - cx[0]) < ENDB.w / 2 && Math.abs(yd - ENDB.y) < ENDB.h / 2) return 'more';
      if (Math.abs(xd - cx[1]) < ENDB.w / 2 && Math.abs(yd - ENDB.y) < ENDB.h / 2) return 'end';
      return null;
    }
    if (S.phase === 'ready' && Math.abs(xd - (QUIT.x + 22)) < QUIT.w / 2 + 8 && Math.abs(yd - QUIT.y) < QUIT.h / 2 + 8) return 'quit';
    if (inBox(D.go.box, xi, yi, 10)) return 'go';
    if (inBox(D.see.box, xi, yi, 6)) return 'see';
    return null;
  }
  function act(what) {
    if (!S || S.hold) return false;
    if (what === 'go') return pressGo();
    if (what === 'see') return pressSee();
    if (what === 'more') return pressMore();
    if (what === 'end') return pressEnd();
    if (what === 'quit') return pressQuit();
    return false;
  }
  function onDown(e) {
    if (!S) return; e.preventDefault(); e.stopPropagation();
    const r = cv.getBoundingClientRect(); if (!r.width) return;
    const what = hit((e.clientX - r.left) / r.width * W, (e.clientY - r.top) / r.height * H);
    if (S.phase === 'res' && S.pop && !S.hold) { S.skip = S.t; }      // ポイントの 札は タップで 先へ
    if (what) act(what);
  }

  // ---------- 描く 道具 ----------
  function pf(pts, fill) { g.beginPath(); g.moveTo(pts[0][0], pts[0][1]); for (let i = 1; i < pts.length; i++) g.lineTo(pts[i][0], pts[i][1]); g.closePath(); g.fillStyle = fill; g.fill(); g.strokeStyle = fill; g.stroke(); }
  function label(txt, x, y, size, fill, edge, ew, align) {
    g.font = `700 ${size}px ${FONT}`; g.textAlign = align || 'center'; g.textBaseline = 'middle';
    if (edge) { g.lineJoin = 'round'; g.lineWidth = ew; g.strokeStyle = edge; g.strokeText(txt, x, y); }
    g.fillStyle = fill; g.fillText(txt, x, y);
  }
  function chip(cx, cy, w, h, txt, size, o) {          // 紙の 札の ボタン（o.gold：金色・o.a：こさ・o.s：大きさ・o.sub：下の 小さい 字）
    o = o || {}; const k = 22;
    g.save(); g.globalAlpha *= o.a == null ? 1 : o.a; g.translate(cx, cy); g.scale(o.s || 1, o.s || 1); g.lineWidth = 0.8;
    pf([[-w / 2 + 6, -h / 2 + 8], [w / 2 + 6, -h / 2 + 8], [w / 2 + 6, h / 2 + 8], [-w / 2 + 6, h / 2 + 8]], 'rgba(40,20,5,0.26)');
    pf([[-w / 2, -h / 2], [w / 2 - k, -h / 2], [w / 2, -h / 2 + k], [w / 2, h / 2], [-w / 2, h / 2]], o.gold ? '#f6c24a' : '#fff8ec');
    pf([[-w / 2, h * 0.08], [w / 2, h * 0.08], [w / 2, h / 2], [-w / 2, h / 2]], o.gold ? '#eaae32' : '#f8ecd4');
    pf([[w / 2 - k, -h / 2], [w / 2, -h / 2 + k], [w / 2 - k, -h / 2 + k]], o.gold ? '#c98a1c' : '#e6cf9f');
    g.strokeStyle = o.gold ? '#8a5a12' : '#d9b77c'; g.lineWidth = o.gold ? 4 : 3; g.strokeRect(-w / 2 + 3, -h / 2 + 3, w - 6, h - 6);
    label(txt, o.dx || 0, o.sub ? -size * 0.36 : 2, size, o.gold ? '#5b3412' : '#7a4520', o.gold ? '#fff3cf' : null, o.gold ? 6 : 0);
    if (o.sub) label(o.sub, 0, size * 0.62, Math.round(size * 0.52), o.gold ? '#7a4a12' : '#9a7a55');
    g.restore();
  }
  function tag(x, y, txt, size, a, sc, col) {          // 紙の 札（字だけ）
    if (a <= 0.003 || sc <= 0.01) return;
    g.save(); g.globalAlpha *= a; g.translate(x, y); g.scale(sc, sc);
    g.font = `700 ${size}px ${FONT}`; const w = g.measureText(txt).width + size * 1.0, h = size * 1.55, c = size * 0.38; g.lineWidth = 0.8;
    pf([[-w / 2 + 4, -h / 2 + 6], [w / 2 + 4, -h / 2 + 6], [w / 2 + 4, h / 2 + 6], [-w / 2 + 4, h / 2 + 6]], 'rgba(40,20,5,0.18)');
    pf([[-w / 2, -h / 2], [w / 2 - c, -h / 2], [w / 2, -h / 2 + c], [w / 2, h / 2], [-w / 2, h / 2]], '#fff8ea');
    pf([[-w / 2, 0.06 * h], [w / 2, 0.06 * h], [w / 2, h / 2], [-w / 2, h / 2]], '#f6e8cc');
    pf([[w / 2 - c, -h / 2], [w / 2, -h / 2 + c], [w / 2 - c, -h / 2 + c]], '#e3c993');
    label(txt, 0, 1, size, col || '#7a4520');
    g.restore();
  }
  function star(x, y, r, a) {                          // 4つの 先の 星（きらっ）
    if (a <= 0.01 || r <= 0.2) return;
    g.save(); g.globalAlpha *= a; g.translate(x, y); g.fillStyle = '#fff'; g.beginPath();
    for (let i = 0; i < 8; i++) { const rr = i % 2 ? r * 0.22 : r, an = i * TAU / 8; g.lineTo(Math.cos(an) * rr, Math.sin(an) * rr); }
    g.closePath(); g.fill(); g.restore();
  }
  function polyPath(p) { g.beginPath(); g.moveTo(p[0][0], p[0][1]); for (let i = 1; i < p.length; i++) g.lineTo(p[i][0], p[i][1]); g.closePath(); }

  // ---------- 玉 ----------
  function ballAt(b, u) {                              // u 秒 たった ときの 玉（絵の 画素・回る 角度）。おわって いれば null
    const p = b.p, f = u * 60, i = Math.floor(f);
    if (i >= p.n - 1) return null;
    const q = f - i, a = p.f, j = 3 * i;
    return { x: lerp(a[j], a[j + 3], q) / 10, y: lerp(a[j + 1], a[j + 4], q) / 10, r: lerp(a[j + 2], a[j + 5], q), f };
  }
  function drawBall(x, y, deg, sc, a) {
    const r = D.ball.r * sc, n = 32, fi = ((Math.round(deg / 360 * n) % n) + n) % n, cs = 96, d = r * 2 * cs / 88;
    g.save(); g.globalAlpha *= a == null ? 1 : a;
    g.fillStyle = 'rgba(30,45,40,0.22)'; g.beginPath(); g.ellipse(x + r * 0.42, y + r * 0.62, r * 0.92, r * 0.8, 0, 0, TAU); g.fill();      // 盤に 落ちる かげ（台の 絵の 光と 同じ 向き）
    g.drawImage(IM.ball, (fi % 8) * cs, Math.floor(fi / 8) * cs, cs, cs, x - d / 2, y - d / 2, d, d);
    g.restore();
  }
  function drawFront(x, y, r) {                        // 玉より 手前の 所（釘の 先・コップの 前）を 玉の まわり だけ 重ねる
    const F = D.front, x0 = Math.max(F[0], Math.floor(x - r - 3)), y0 = Math.max(F[1], Math.floor(y - r - 3)), x1 = Math.min(F[0] + F[2], Math.ceil(x + r + 3)), y1 = Math.min(F[1] + F[3], Math.ceil(y + r + 3));
    if (x1 <= x0 || y1 <= y0) return;
    g.drawImage(IM.front, x0 - F[0], y0 - F[1], x1 - x0, y1 - y0, x0, y0, x1 - x0, y1 - y0);
  }

  // ---------- 馬バレ（まん中の 丸）と オーラ ----------
  //   重ねる 順：台 → 台を 少し 暗く（auraDim）→ … → オーラ（drawAura：色の にじみ・炎・光の すじ・ひろがる 輪）→ 黄色い 縁を 描き直す（drawRim）→ 色の 絵（drawLcd）→ きらきら（drawSpark）
  //   ＝光は 馬バレの うしろから 出て、色の 絵は いつも はっきり 見える。明るい 盤の 上でも 色が 白く とばない ように、先に 色を ぬって（ふつうの 重ね）から 光を 足す
  function auraK(L) {                                  // 光の 強さ 0〜1：ふわっと 明るく → はげしい 間 → 落ちついた 強さ → 消える
    const tn = TONE[L.c], u = S.t - L.t0;
    let k = sm(u / 0.14) * (u < tn.len ? 1 : lerp(1, tn.keep, sm((u - tn.len) / 0.7)));
    if (L.off != null) k *= 1 - sm((S.t - L.off) / 0.3);
    return k;
  }
  const auraStrong = L => { const tn = TONE[L.c], u = S.t - L.t0; return u < tn.len ? 1 : 1 - sm((u - tn.len) / 0.7); };      // はげしい 間 1 → 0
  function auraDim(L) {                                // 台を 少し 暗く（光が 目立つ）：色が 上がる ほど 暗く・はげしい 間 だけ（あとは うすく）
    const tn = TONE[L.c], st = auraStrong(L), k = auraK(L) * (0.3 + 0.7 * st); if (k <= 0.004) return;
    g.fillStyle = `rgba(14,8,26,${tn.dim * k})`; g.fillRect(0, 0, D.img[0], D.img[1]);
  }
  function hueAt(x) { const i = Math.floor(x), q = sm(x - i), a = HUES[((i % 7) + 7) % 7], b = HUES[(((i + 1) % 7) + 7) % 7]; return [0, 1, 2].map(j => Math.round(lerp(a[j], b[j], q))); }      // 虹の 色を なめらかに
  function drawAura(L) {
    const c = L.c, tn = TONE[c], u = S.t - L.t0, k = auraK(L); if (k <= 0.004) return;
    const [cx, cy, , rr] = D.lcd, cm = calm(), st = auraStrong(L), G = glows();
    const br = cm ? 1 : 0.92 + 0.08 * Math.sin(TAU * 1.1 * u);                      // ゆっくり 息を する（1秒に 1回 くらい）
    const R = rr * (1 + (tn.R - 1) * (0.62 + 0.38 * st)) * (cm ? 0.9 : 1);
    const col = c === 6 ? [255, 250, 240] : tn.rgb, ka = c === 6 ? 0.45 : 1;
    g.save();
    // 色の にじみ（ふつうの 重ね：盤の 色を その 色に そめる）→ 光（足す）
    let gr = g.createRadialGradient(cx, cy, rr * 0.75, cx, cy, R);
    gr.addColorStop(0, `rgba(${col[0]},${col[1]},${col[2]},${0.78 * ka * tn.a * k * br})`); gr.addColorStop(0.4, `rgba(${col[0]},${col[1]},${col[2]},${0.4 * ka * tn.a * k * br})`); gr.addColorStop(1, `rgba(${col[0]},${col[1]},${col[2]},0)`);
    g.fillStyle = gr; g.beginPath(); g.arc(cx, cy, R, 0, TAU); g.fill();
    if (c === 6) for (let pass = 0; pass < 2; pass++) {      // 虹：7色の 光が 輪に ならんで ゆっくり 回る（いつ 見ても 虹色）
      g.globalCompositeOperation = pass ? 'lighter' : 'source-over';
      for (let i = 0; i < 7; i++) {
        const an = i * TAU / 7 + (cm ? 0 : u * 0.3), d = rr + (R - rr) * 0.36, sz = (R - rr) * 0.6 + rr * 0.55;
        g.globalAlpha = (pass ? 0.34 : 0.62) * k * br;
        g.drawImage(G.hue[i], cx + Math.cos(an) * d - sz, cy + Math.sin(an) * d - sz, sz * 2, sz * 2);
      }
      g.globalAlpha = 1;
    }
    g.globalCompositeOperation = 'lighter';
    gr = g.createRadialGradient(cx, cy, rr * 0.8, cx, cy, rr + (R - rr) * 0.7);
    gr.addColorStop(0, `rgba(${col[0]},${col[1]},${col[2]},${0.5 * ka * tn.a * k * br})`); gr.addColorStop(1, `rgba(${col[0]},${col[1]},${col[2]},0)`);
    g.fillStyle = gr; g.beginPath(); g.arc(cx, cy, R, 0, TAU); g.fill();
    // 光の すじ（紫 から：ゆっくり 回る）
    if (tn.rays && !cm) {
      const rot = u * 0.055 * TAU, len = R * 1.12;
      for (let i = 0; i < tn.rays; i++) {
        const an = rot + i * TAU / tn.rays, w = TAU / tn.rays * 0.22, rc = c === 6 ? HUES[i % 7] : tn.rgb, al = (i % 2 ? 0.22 : 0.4) * tn.a * k * (0.3 + 0.7 * st);
        const lg = g.createLinearGradient(cx + Math.cos(an) * rr, cy + Math.sin(an) * rr, cx + Math.cos(an) * len, cy + Math.sin(an) * len);
        lg.addColorStop(0, `rgba(${rc[0]},${rc[1]},${rc[2]},${al})`); lg.addColorStop(1, `rgba(${rc[0]},${rc[1]},${rc[2]},0)`);
        g.fillStyle = lg; g.beginPath(); g.moveTo(cx + Math.cos(an - w * 0.3) * rr * 0.96, cy + Math.sin(an - w * 0.3) * rr * 0.96);
        g.lineTo(cx + Math.cos(an - w) * len, cy + Math.sin(an - w) * len); g.lineTo(cx + Math.cos(an + w) * len, cy + Math.sin(an + w) * len); g.lineTo(cx + Math.cos(an + w * 0.3) * rr * 0.96, cy + Math.sin(an + w * 0.3) * rr * 0.96); g.closePath(); g.fill();
      }
    }
    // オーラの 炎：縁から 外へ のびる 光の 舌（上の 方が 長い＝立ちのぼる）。長さが 1本ずつ ゆっくり ゆれる（1秒に 1回 より おそい）
    const nt = cm ? Math.ceil(tn.nt * 0.6) : tn.nt, base = rr * tn.tl * (0.5 + 0.5 * st) * (0.55 + 0.45 * sm(u / 0.3));
    for (let pass = 0; pass < 2; pass++) {             // 1回め＝色（ふつうの 重ね）・2回め＝光（足す）
      g.globalCompositeOperation = pass ? 'lighter' : 'source-over';
      for (let i = 0; i < nt; i++) {
        const h1 = hash(i * 3.71 + c * 1.3), h2 = hash(i * 7.13 + c * 0.7), h3 = hash(i * 1.37 + c * 2.9);
        const an = i * TAU / nt + (cm ? 0 : 0.16 * Math.sin(TAU * (0.21 + 0.17 * h1) * u + TAU * h2)), up = (1 - Math.sin(an)) / 2;
        const wob = cm ? 0.75 : 0.5 + 0.5 * Math.sin(TAU * (0.5 + 0.42 * h2) * u + TAU * h3);
        const len = base * (0.5 + 0.5 * wob) * (0.62 + 0.9 * up * up) * (0.75 + 0.5 * h1) + rr * 0.35, wd = rr * (0.36 + 0.07 * c) * (0.75 + 0.5 * h3);
        g.globalAlpha = Math.min(1, (pass ? 0.42 : 0.5) * tn.a * k * (0.6 + 0.4 * wob));
        g.save(); g.translate(cx + Math.cos(an) * rr * 0.7, cy + Math.sin(an) * rr * 0.7); g.rotate(an);
        g.drawImage(c === 6 ? G.thue[(i + Math.floor(u * 0.6)) % 7] : G.tong[c], 0, -wd / 2, len, wd);
        g.restore();
      }
    }
    g.globalAlpha = 1; g.globalCompositeOperation = 'lighter';
    // のぼる 光の 粒（縁の まわりから 上へ）
    const np = cm ? 0 : 4 + c * 3;
    for (let i = 0; i < np; i++) {
      const per = 1.1 + 0.9 * hash(i * 3.1 + c), x0 = u / per + hash(i * 7.7 + c * 1.3), ph = x0 % 1, cyc = Math.floor(x0);
      const an = TAU * hash(i * 1.9 + c * 0.7 + cyc * 0.37), d0 = rr * (0.95 + 0.5 * hash(i * 5.3 + cyc)), rise = ph * rr * (0.7 + 0.28 * c) * (0.5 + 0.5 * st);
      const sz = rr * (0.16 + 0.03 * c) * (1 - 0.5 * ph), al = Math.sin(Math.PI * ph) * 0.8 * k;
      if (al <= 0.01) continue;
      g.globalAlpha = Math.min(1, al);
      g.drawImage(c === 6 ? G.hue[(i + cyc) % 7] : G.tone[c], cx + Math.cos(an) * d0 - sz, cy + Math.sin(an) * d0 * 0.9 - rise - sz, sz * 2, sz * 2);
    }
    g.globalAlpha = 1;
    // ひろがる 輪（当たった 瞬間：赤 1つ・金 1つ・虹 2つ）
    if (c >= 4 && !cm) for (let j = 0; j < (c === 6 ? 2 : 1); j++) {
      const v = (u - 0.05 - j * 0.3) / 0.8; if (v <= 0 || v >= 1) continue;
      const rc = c === 6 ? HUES[(j * 3 + 1) % 7] : tn.rgb;
      g.strokeStyle = `rgba(${rc[0]},${rc[1]},${rc[2]},${0.75 * (1 - v) * tn.a})`; g.lineWidth = rr * 0.22 * (1 - 0.6 * v);
      g.beginPath(); g.arc(cx, cy, rr * (1 + (tn.R * 1.1 - 1) * easeOut(v)), 0, TAU); g.stroke();
    }
    g.restore();
  }
  function drawRim(L) {                                // 黄色い 縁を 光の 手前に 描き直す（台の 絵の その 所）＋ 縁の きわが 色に 光る
    const k = auraK(L); if (k <= 0.004) return;
    const [cx, cy, , rr] = D.lcd, c = L.c, u = S.t - L.t0, col = c === 6 ? hueAt(u * 0.9) : TONE[c].rgb, x0 = Math.floor(cx - rr - 2), y0 = Math.floor(cy - rr - 2), w = Math.ceil(rr * 2 + 4);
    g.save(); g.globalAlpha = Math.min(1, k * 1.4); g.beginPath(); g.arc(cx, cy, rr, 0, TAU); g.clip(); g.drawImage(IM.base, x0, y0, w, w, x0, y0, w, w); g.restore();
    g.save(); g.globalCompositeOperation = 'lighter';
    const gr = g.createRadialGradient(cx, cy, rr * 0.74, cx, cy, rr * 1.2);
    gr.addColorStop(0, `rgba(${col[0]},${col[1]},${col[2]},0)`); gr.addColorStop(0.5, `rgba(${col[0]},${col[1]},${col[2]},${0.42 * k})`); gr.addColorStop(1, `rgba(${col[0]},${col[1]},${col[2]},0)`);
    g.fillStyle = gr; g.beginPath(); g.arc(cx, cy, rr * 1.2, 0, TAU); g.fill(); g.restore();
  }
  function drawSpark(L) {                              // きらきら（紫 から：いちばん 手前）
    const c = L.c, tn = TONE[c], u = S.t - L.t0, k = auraK(L); if (c < 3 || k <= 0.004) return;
    const [cx, cy, , rr] = D.lcd, cm = calm();
    g.save(); g.globalCompositeOperation = 'lighter';
    for (let i = 0; i < (cm ? 4 : 5 + (c - 3) * 6); i++) {
      const per = 1.2 + 0.8 * hash(i * 4.1 + 9), x0 = u / per + hash(i * 6.3 + 2), ph = x0 % 1, cyc = Math.floor(x0);
      const an = TAU * hash(i * 2.7 + cyc * 0.61 + c), d = rr * (1.2 + (tn.R * 0.8 - 1.2) * hash(i * 3.3 + cyc * 0.17));
      star(cx + Math.cos(an) * d, cy + Math.sin(an) * d * 0.92, rr * (0.16 + 0.05 * c) * Math.sin(Math.PI * ph), Math.sin(Math.PI * ph) * 0.9 * k);
    }
    g.restore();
  }
  function drawLcd(L) {                                // 色の 絵（丸）：ぽんと つく
    const [cx, cy, r] = D.lcd, u = S.t - L.t0, k = L.off != null ? 1 - sm((S.t - L.off) / 0.25) : 1; if (k <= 0.004) return;
    const s = calm() ? 1 : 0.86 + 0.14 * backOut(u / 0.3);
    g.save(); g.beginPath(); g.arc(cx, cy, r + 1.5, 0, TAU); g.clip();
    g.globalAlpha = k * sm(u / 0.08);
    const im = IM.uma[L.c], d = r * 2 * s * (im.width / (im.width - 4));
    g.drawImage(im, cx - d / 2, cy - d / 2, d, d);
    const fl = 1 - sm(u / 0.32);                       // つく 瞬間の 白い 光（丸の 中 だけ・1回）
    if (fl > 0.01) { g.globalAlpha = 0.7 * fl * k; g.fillStyle = '#fff'; g.fillRect(cx - r - 2, cy - r - 2, r * 2 + 4, r * 2 + 4); }
    g.restore();
  }

  // ---------- 1コマ ----------
  function sizeUp() {
    const ref = stageEl.querySelector('canvas.tco'), w = ref ? ref.width : Math.round(stageEl.clientWidth * Math.min(window.devicePixelRatio || 1, 3)), h = Math.round(w * H / W);
    if (cv.width !== w || cv.height !== h) { cv.width = w; cv.height = h; }
    K = cv.width / W;
    const key = cv.width + 'x' + cv.height;
    if (cacheKey !== key || !cache) {                  // 台の 絵（動かない）は 画面の 細かさで 1回 だけ 描いて おく
      cache = document.createElement('canvas'); cache.width = cv.width; cache.height = cv.height; cacheKey = key;
      const q = cache.getContext('2d'); q.imageSmoothingQuality = 'high';
      q.drawImage(IM.base, K * MX, K * MY, K * D.img[0] * MS, K * D.img[1] * MS);
    }
  }
  function step(dt) {
    S.t += dt;
    for (let pass = 0; pass < 4; pass++) {             // 予定（時刻が 来た もの：呼んだ 先が 足した 分も）
      const due = S.sched.filter(q => q.t <= S.t); if (!due.length) break;
      S.sched = S.sched.filter(q => q.t > S.t);
      for (const q of due.sort((a, b) => a.t - b.t)) { try { q.fn(); } catch (e) { /* なし */ } if (!S) return; }
    }
    if (S.skip != null && S.pop) {                     // ポイントの 札を タップで 先へ：のこりの 待ちを つめる
      for (const q of S.sched) q.t = Math.min(q.t, S.t + 0.12);
      S.skip = null;
    }
    const b = S.ball;
    if (b) {
      const u = S.t - b.t0, f = u * 60, p = b.p;
      while (b.hi < p.h.length && p.h[b.hi][0] <= f) {                              // 当たった 音（釘＝強さで 大きさ・コップの ふち／輪／かべ＝小さく）
        const hh = p.h[b.hi++], gain = clamp(0.22 + hh[3] / 95, 0.22, 1);
        if (hh[1] === 0) { se('dp_peg' + (1 + hh[2] % 3), gain); S.fx.push({ k: 'peg', t0: S.t, i: hh[2], a: gain }); }
        else if (b.inT == null) se('dp_peg1', gain * 0.5);
      }
      if (b.inT == null && f >= p.tin) ballIn(b);
      if (f >= p.n - 1) S.ball = null;
    }
    S.old = S.old.filter(q => (S.t - q.t0) * 60 < q.p.n - 1);
    S.fx = S.fx.filter(q => S.t - q.t0 < 0.7);
    if (S.lcd && S.lcd.off != null && S.t - S.lcd.off > 0.4) S.lcd = null;
  }
  function draw() {
    const t = S.t, cm = calm();
    const hk = S.hold ? sm((t - S.holdT) / 0.25) : 1 - sm((t - S.holdT) / 0.3), op = +(1 - hk).toFixed(3);      // いつもの 演出の 間：台を すっと 消す → おわったら もどす
    if (op !== S.op) { S.op = op; cv.style.opacity = String(op); }
    g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, cv.width, cv.height);
    const veil = sm(t / 0.3);                          // うしろ（フィールドと お世話の 札）を かくす 幕：上の 札の 所は こく
    const vg = g.createLinearGradient(0, 0, 0, cv.height);
    vg.addColorStop(0, `rgba(22,13,8,${0.96 * veil})`); vg.addColorStop(0.2, `rgba(22,13,8,${0.93 * veil})`); vg.addColorStop(0.5, `rgba(24,14,8,${0.88 * veil})`); vg.addColorStop(1, `rgba(24,14,8,${0.9 * veil})`);
    g.fillStyle = vg; g.fillRect(0, 0, cv.width, cv.height);
    // 台（はじめは 下から すっと 出る）
    const rise = cm ? 0 : (1 - easeOut(t / 0.4)) * 90 * K;
    g.globalAlpha = sm(t / 0.25); g.drawImage(cache, 0, rise); g.globalAlpha = 1;
    const TI = () => g.setTransform(K * MS, 0, 0, K * MS, K * MX, K * MY + rise), TS = () => g.setTransform(K, 0, 0, K, 0, rise);      // 台の 絵の 画素で 描く／舞台の 座標で 描く
    TI(); g.lineJoin = 'round';
    // 馬バレが ついて いる 間は 台を 少し 暗く（光が 目立つ：色が 上がる ほど）
    const L = S.lcd;
    if (L) auraDim(L);
    // ボタンの ようす
    const canGo = S.phase === 'ready' && !S.ball && t >= S.lock && S.n < S.max;
    if (!canGo) { polyPath(D.go.poly); g.fillStyle = 'rgba(60,34,40,0.36)'; g.fill(); }
    const pg = t - (S.press.go == null ? -9 : S.press.go);
    if (pg >= 0 && pg < 0.3) { polyPath(D.go.poly); g.fillStyle = `rgba(255,255,255,${0.55 * (1 - pg / 0.3)})`; g.fill(); }
    if (canGo) { const u = t - Math.max(S.lock, S.roundT + 0.45), a = sm(u / 0.25), pu = cm ? 0.6 : 0.5 + 0.5 * Math.sin(TAU * 0.8 * u); polyPath(D.go.poly); g.strokeStyle = `rgba(255,244,190,${a * (0.35 + 0.55 * pu)})`; g.lineWidth = 9; g.stroke(); }      // 押せる 合図：ふちが ゆっくり 光る（「タップ！」の 札は 当選の ますに かぶる ので 出さない）
    if (S.phase === 'wait' || S.phase === 'res') {     // かぎが あいた
      const o = D.see.open, a = sm((t - S.unlockT) / 0.2);
      g.globalAlpha = a; g.drawImage(IM.see, o[0], o[1], o[2], o[3]); g.globalAlpha = 1;
      if (S.phase === 'wait') { const pu = cm ? 0.6 : 0.5 + 0.5 * Math.sin(TAU * 0.8 * (t - S.unlockT)); polyPath(D.see.poly); g.strokeStyle = `rgba(255,236,150,${a * (0.45 + 0.5 * pu)})`; g.lineWidth = 9; g.stroke(); g.fillStyle = `rgba(255,255,255,${a * 0.1 * pu})`; g.fill(); }
      const ps = t - (S.press.see == null ? -9 : S.press.see);
      if (ps >= 0 && ps < 0.3) { polyPath(D.see.poly); g.fillStyle = `rgba(255,255,255,${0.5 * (1 - ps / 0.3)})`; g.fill(); }
    } else { polyPath(D.see.poly); g.fillStyle = 'rgba(40,60,54,0.26)'; g.fill(); }
    // 保留（当選の ます）
    for (const h of S.holds) {
      const x = D.hold.x[h.slot], y = D.hold.y, w = D.hold.w;
      if (h.state === 'fly') continue;
      let s = h.t != null && h.t > -5 ? backOut((t - h.t) / 0.32) : 1, a = 1;
      if (h.state === 'show') s *= cm ? 1.06 : 1.08 + 0.06 * Math.sin(TAU * 1.2 * (t - h.showT));
      if (h.state === 'done') { const v = sm((t - h.doneT) / 0.28); s *= 1 - 0.5 * v; a = 1 - v; }
      if (a <= 0.01) continue;
      if (h.state === 'show') { g.save(); g.globalCompositeOperation = 'lighter'; g.globalAlpha = 0.75; const G = glows(); g.drawImage(h.c === 6 ? G.hue[Math.floor(t * 3) % 7] : G.tone[h.c], x - w * 1.1, y - w * 1.1, w * 2.2, w * 2.2); g.restore(); }
      g.globalAlpha = a; g.drawImage(IM.hold[h.c], x - w * s / 2, y - w * s / 2, w * s, w * s); g.globalAlpha = 1;
    }
    // 受け皿で 待って いる 次の 玉（ぽとんと 出て くる）
    if (S.next && !S.ball && S.n < S.max) { const u = t - S.next.t0, v = backOut(u / 0.3); drawBall(D.ball.start[0], D.ball.start[1] - (1 - Math.min(1, v)) * 46, 0, 0.6 + 0.4 * Math.min(1, v), sm(u / 0.12)); }
    // 落ちて いる 玉 → 手前の 層
    for (const b of S.old.concat(S.ball ? [S.ball] : [])) {
      const q = ballAt(b, t - b.t0);
      if (q) {
        const u = t - b.t0, hop = 1 + 0.1 * Math.sin(Math.PI * clamp(u / 0.34, 0, 1));      // 出だし：受け皿の ふちを こえて 手前へ とび出す
        drawBall(q.x, q.y, q.r, hop, 1); drawFront(q.x, q.y, D.ball.r * hop + 8);
      }
    }
    // 当たった 釘の 光・コップに 入った 輪
    for (const f of S.fx) {
      const u = t - f.t0;
      if (f.k === 'peg' && u < 0.16) { const p = D.pegs[f.i]; if (p) star(p[0], p[1], 20 * (0.6 + 0.6 * f.a) * (1 - u / 0.16), 0.85 * (1 - u / 0.16)); }
      if (f.k === 'cup' && u < 0.45) { const p = D.cups[f.cup], v = u / 0.45; g.strokeStyle = `rgba(255,255,255,${0.8 * (1 - v)})`; g.lineWidth = 7 * (1 - 0.5 * v); g.beginPath(); g.ellipse(p[0], p[1] - 4, 44 + 46 * easeOut(v), 14 + 14 * easeOut(v), 0, 0, TAU); g.stroke(); }
    }
    // 「あと Nこ」（玉を落とす の 右上）
    if (S.max > 0 && (S.phase === 'ready' || S.phase === 'fall')) {
      const bx = D.go.box[2] - 26, by = D.go.box[1] + 4, left = S.max - S.n, pb = t - (S.press.go == null ? -9 : S.press.go), sc = pb >= 0 && pb < 0.3 ? 1 + 0.18 * Math.sin(Math.PI * pb / 0.3) : 1;
      g.save(); g.translate(bx, by); g.scale(sc, sc);
      g.fillStyle = 'rgba(60,30,10,0.28)'; g.beginPath(); g.arc(3, 5, 47, 0, TAU); g.fill();
      g.fillStyle = '#fff8ec'; g.beginPath(); g.arc(0, 0, 47, 0, TAU); g.fill(); g.strokeStyle = '#e0a21f'; g.lineWidth = 6; g.stroke();
      label('あと', 0, -24, 22, '#9a6a1c'); label(String(left), -8, 10, 46, left > 0 ? '#c2362b' : '#a89a88'); label('こ', 25, 16, 22, '#9a6a1c');
      g.restore();
    }
    // 馬バレ：オーラ（うしろ）→ 黄色い 縁 → 色の 絵 → きらきら。とんで いく 保留
    if (L) { drawAura(L); drawRim(L); drawLcd(L); drawSpark(L); }
    for (const h of S.holds) if (h.state === 'fly' && t >= h.fly) {
      const v = clamp((t - h.fly) / FLY, 0, 1), e = sm(v), x0 = D.lcd[0], y0 = D.lcd[1], x1 = D.hold.x[h.slot], y1 = D.hold.y;
      const x = lerp(x0, x1, e), y = lerp(y0, y1, e) - Math.sin(Math.PI * e) * 70, G = glows(), sz = 70 - 22 * e;
      g.save(); g.globalCompositeOperation = 'lighter'; g.drawImage(h.c === 6 ? G.hue[Math.floor(t * 12) % 7] : G.tone[h.c], x - sz, y - sz, sz * 2, sz * 2); g.restore();
    }
    // ---- ここから 舞台の 座標（札・字）----
    TS();
    const ia = sm((t - 0.25) / 0.3);
    // 左上：やめる
    const canQuit = S.phase === 'ready' && !S.ball && t >= S.lock, qa = S.phase === 'ready' || S.phase === 'fall' ? ia * (canQuit ? 1 : 0.4) : 0;      // 玉を 落とす 間 だけ（保留結果を見る・おしまいの 間は 出さない）
    const early = S.n > 0 || S.holds.length > 0;      // 玉を 落とした あと：「投入終了」（のこりの 玉は 落とさずに 保留結果へ）・まだ 落として いない：「やめる」（閉じる）
    if (qa > 0.01) chip(QUIT.x + 22, QUIT.y, QUIT.w, QUIT.h, early ? '投入終了' : 'やめる', early ? 36 : 34, { a: qa, dx: early ? 0 : 20 });
    if (!early) { g.save(); g.globalAlpha *= qa; g.strokeStyle = '#7a4520'; g.lineWidth = 6; g.lineCap = 'round'; g.beginPath();      // ✕（字に ない ことが ある ので 線で）
      g.moveTo(QUIT.x - 62, QUIT.y - 12); g.lineTo(QUIT.x - 38, QUIT.y + 14); g.moveTo(QUIT.x - 38, QUIT.y - 12); g.lineTo(QUIT.x - 62, QUIT.y + 14); g.stroke(); g.restore(); }
    // 右上：お世話トークン（・高確ゾーン）
    g.save(); g.globalAlpha *= ia; g.translate(W - 148, 74); g.lineWidth = 0.8;
    pf([[-125, -52], [135, -52], [135, 66], [-125, 66]], 'rgba(40,20,5,0.2)');
    pf([[-130, -58], [108, -58], [130, -36], [130, 58], [-130, 58]], '#fff8ec'); pf([[-130, 6], [130, 6], [130, 58], [-130, 58]], '#f8ecd4'); pf([[108, -58], [130, -36], [108, -36]], '#e6cf9f');
    label('お世話トークン', 0, -30, 27, '#7a4520');
    const stock = API.stock(); label('のこり', -62, 22, 28, '#9a7a55'); label(String(stock), 34, 20, 52, '#3f7f3a', '#fff8ec', 6); label('こ', 96, 24, 26, '#9a7a55');
    g.restore();
    const hi = API.high ? API.high() : 0;
    if (hi > 0) tag(W - 148, 168, `高確ゾーン あと ${hi}回`, 26, ia, 1, '#c2362b');
    // 合図
    if (S.phase === 'wait') { const u = t - S.unlockT - 0.35, k2 = sm(u / 0.25); if (k2 > 0) { const p = [MX + (D.see.box[0] + D.see.box[2]) / 2 * MS, MY + D.see.box[1] * MS - 30]; tag(p[0], p[1] + (cm ? 0 : 5 * Math.sin(TAU * 0.9 * u)), 'タップ！', 40, k2, 1, '#2f7f5f'); } }
    // 当たり なし
    if (S.phase === 'none' && S.none != null) { const u = t - S.none; tag(W / 2, 760, 'ざんねん… 当たりは なかったよ', 38, sm(u / 0.2) * (1 - sm((u - 1.2) / 0.3)), backOut(u / 0.3), '#7a4520'); }
    // ルーレット！・特化ゾーン！
    if (S.cue) { const u = t - S.cue.t0; if (u > 1.3) S.cue = null; else tag(W / 2, 700, S.cue.txt, 56, sm(u / 0.12) * (1 - sm((u - 1.0) / 0.25)), backOut(u / 0.3) * (cm ? 1 : 1 + 0.04 * Math.sin(TAU * 1.4 * u)), '#c2362b'); }
    // ポイントの 札
    if (S.pop) {
      const u = t - S.pop.t0; if (u > 1.6) S.pop = null; else {
        const a = sm(u / 0.1) * (1 - sm((u - 1.25) / 0.3)), s = backOut(u / 0.3);
        g.save(); g.globalAlpha *= a; g.translate(W / 2, 700 - (cm ? 0 : 14 * easeOut(u / 0.8))); g.scale(s, s); g.lineWidth = 0.8;
        pf([[-205, -78], [215, -78], [215, 96], [-205, 96]], 'rgba(40,20,5,0.22)');
        pf([[-210, -86], [176, -86], [210, -52], [210, 86], [-210, 86]], '#fff8ea'); pf([[-210, 10], [210, 10], [210, 86], [-210, 86]], '#f6e8cc'); pf([[176, -86], [210, -52], [176, -52]], '#e3c993');
        label(`＋${Number(S.pop.v).toLocaleString('ja-JP')}`, -22, 4, 96, '#c2362b', '#fff8ea', 8); label('P', 150, 16, 64, '#c2362b', '#fff8ea', 6);
        g.restore();
      }
    }
    // おしまいの 札：今回の 当たり・のこりの トークン・「続けてやる」「終わり」
    if (S.phase === 'end' && S.endT != null) {
      const u = t - S.endT, a = sm(u / 0.25), w = ENDC.w, h = ENDC.h, k = 36;
      g.fillStyle = `rgba(20,12,6,${0.55 * a})`; g.fillRect(0, 0, W, H);
      g.save(); g.globalAlpha *= a; g.translate(W / 2, ENDC.y); const sc = cm ? 1 : backOut(u / 0.35); g.scale(sc, sc); g.lineWidth = 0.8;
      pf([[-w / 2 + 6, -h / 2 + 10], [w / 2 + 8, -h / 2 + 10], [w / 2 + 8, h / 2 + 10], [-w / 2 + 6, h / 2 + 10]], 'rgba(40,20,5,0.3)');
      pf([[-w / 2, -h / 2], [w / 2 - k, -h / 2], [w / 2, -h / 2 + k], [w / 2, h / 2], [-w / 2, h / 2]], '#fff8ec'); pf([[w / 2 - k, -h / 2], [w / 2, -h / 2 + k], [w / 2 - k, -h / 2 + k]], '#e6cf9f');
      g.strokeStyle = '#e0a21f'; g.lineWidth = 5; g.lineJoin = 'miter'; g.beginPath(); g.moveTo(-w / 2 + 14, -h / 2 + 14); g.lineTo(w / 2 - k - 8, -h / 2 + 14); g.lineTo(w / 2 - 14, -h / 2 + k + 8); g.lineTo(w / 2 - 14, h / 2 - 14); g.lineTo(-w / 2 + 14, h / 2 - 14); g.closePath(); g.stroke(); g.lineWidth = 0.8; g.lineJoin = 'round';      // 金の わく（折った 角を よける）
      label('お世話チャレンジ', 0, -h / 2 + 70, 40, '#7a4520');
      label('今回の 当たり', 0, -h / 2 + 136, 30, '#9a7a55');
      const got = [S.sum > 0 ? `＋${Number(S.sum).toLocaleString('ja-JP')}P` : '', S.tk > 0 ? `チケット ${S.tk}枚` : ''].filter(Boolean);
      if (got.length) label(got.join('・'), 0, -h / 2 + 208, got.length > 1 ? 58 : 76, '#c2362b', '#fff8ec', 8);
      else label('なし… また チャレンジしてね', 0, -h / 2 + 204, 40, '#8a7a66');
      label(`お世話トークン のこり ${API.stock()}こ`, 0, -h / 2 + 290, 32, '#3f7f3a');
      label(S.more ? 'もう 1回（玉 5こ）できるよ' : API.left() < 1 ? 'この 馬の 抽選は ここまで' : 'トークンが 5こ たまったら また できるよ', 0, -h / 2 + 338, 26, '#9a7a55');
      g.restore();
      const pm = t - (S.press.more == null ? -9 : S.press.more);
      if (S.more) { chip(W / 2 - ENDB.w / 2 - ENDB.gap / 2, ENDB.y, ENDB.w, ENDB.h, '続けてやる', 48, { gold: true, a, s: backOut((u - 0.08) / 0.3) * (pm >= 0 && pm < 0.2 ? 0.95 : 1), sub: '玉を 5こ 落とす' }); chip(W / 2 + ENDB.w / 2 + ENDB.gap / 2, ENDB.y, ENDB.w, ENDB.h, '終わり', 48, { a, s: backOut((u - 0.14) / 0.3) }); }
      else chip(W / 2, ENDB.y, ENDB.w, ENDB.h, '終わり', 48, { a, s: backOut((u - 0.08) / 0.3) });
    }
    g.setTransform(1, 0, 0, 1, 0, 0);
  }
  function frame(tn) {
    if (!S) return;
    raf = requestAnimationFrame(frame);
    const dt = lastNow ? clamp((tn - lastNow) / 1000, 0, 0.1) : 1 / 60; lastNow = tn;
    if (T.manual) return;                              // テスト・見本 用：時計を 手で 進める（T.tick）
    sizeUp();
    step(dt * (T.speed || 1));
    if (!S) return;
    draw();
  }
  T.tick = dt => { if (!S) return false; sizeUp(); step(dt); if (S) draw(); return !!S; };      // テスト・見本 用：dt 秒 進めて 1コマ 描く

  return { load, ready, open, close, isOpen, BALLS, TONE, NAME,
    _t: T, get state() { return S; }, get data() { return D; },
    tap: what => !!act(what),                          // テスト・見本 用：'go'・'see'・'more'・'end'・'quit'（押せた ときは true）
    // テスト 用：押す 所の まん中（舞台の 座標 1052×1657）と 馬バレの 丸（まん中・黄色い 縁の 半径）
    geo: () => { if (!D) return null; const c = b => [MX + (b[0] + b[2]) / 2 * MS, MY + (b[1] + b[3]) / 2 * MS];
      return { go: c(D.go.box), see: c(D.see.box), quit: [QUIT.x + 22, QUIT.y], more: [W / 2 - ENDB.w / 2 - ENDB.gap / 2, ENDB.y], end2: [W / 2 + ENDB.w / 2 + ENDB.gap / 2, ENDB.y], end1: [W / 2, ENDB.y], lcd: [MX + D.lcd[0] * MS, MY + D.lcd[1] * MS, D.lcd[3] * MS] }; },
    info: () => (S ? { phase: S.phase, t: S.t, max: S.max, n: S.n, used: S.used, holds: S.holds.map(h => [h.c, h.state, h.z.k]), lcd: S.lcd ? S.lcd.c : 0, lcdOff: !!(S.lcd && S.lcd.off != null), ball: S.ball ? { pi: S.ball.pi, cup: S.ball.p.cup, c: S.ball.c, inT: S.ball.inT } : null, more: S.more, lock: S.lock, sum: S.sum, tk: S.tk, next: !!S.next, hold: S.hold, op: S.op } : null) };
})();
