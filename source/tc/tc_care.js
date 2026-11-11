// トレーニングセンターの お世話（撫でる・食事・掃除）の 演出：馬の 上に 重ねる 紙の 絵（2D キャンバス）
//   11/09 08:29 まさちゃん「お世話のアイディア全部組み込んで！」
//   ・絵は ぜんぶ 計算で 描く 折り紙ふう（紙の 手・ハート・札・きらきら）。下の ボタンの 絵は かり（まさちゃんの アイコン 待ち）
//   ・撫でる：指で なぞると 紙の 手が ついてくる。3回 なでると 撫でる 1回 → なかよしハート +1
//       体の 場所で 反応が かわる：頭 → すりすり・首 → しっぽ ふりふり・背中 → ぐーっと のび・鼻 → ぷしゅっ
//       時間帯：朝 → 手を 出すと 元気に うなずく・夕方 → ゆったり よりかかる・夜 → あくびを して ねむる
//       育ち：小さい ころ（1〜2段目）→ はしゃぐ（とばない）・大きく なると → 手の 方へ 顔を よせる
//       たまに（1/20）：首を かしげる
//   ・なかよしハート（11/09 08:37 まさちゃん）：ハートは 1分に 5こまで（6回目からは ハートなし ※仮）
//       第4.151版（11/11 09:07 まさちゃん「撫でるは、連続で5回までにして！7秒間は5回撫でたら撫でられないように！」「呼ぶ、も連続で5回まで！5回超えたら7秒間はできない」）：
//         撫でる・呼ぶは つづけて 5回まで（RULE.streak）→ 5回目が おわったら 7秒（RULE.cool）できない（ボタンに 残りの 秒）。7秒 あけたら 数え直し。前は 撫でる たびに 7秒
//         つづけて 撫でた ときは 前の 反応を すっと 止めて 新しい 反応に かえる（重ねない）・前の 回の あとの 動き（はしゃぐ・あくび・ねむる）は とり消す（petGen）
//         「ボタンを押してから行われるまでが遅すぎる」→ 撫でる・ごはんは 歩いて 来ない：その場で 横向きに なる（急ぎ足 HURRY 倍）・カメラは 押した ときから 寄る・仕上げの ズームは 待たない
//           （comeNear：押して から 撫でられる まで 約0.8秒。前は いちばん 手前まで 歩いて 来て 7〜15秒）。奥に いる ぶん 大きく 寄る（zCap）。
//           呼ぶ（近づく・甘える）は いちばん 手前まで 歩かない（approach：いまの 所から STEP_Y だけ 手前）・ごはんと おそうじの 出だしの 待ちも 短く
//         09:45「トレーニングセンターの掃除した後の花消して！掃除した後のエフェクトは特にいらない！」→ おそうじの あとの お花と 地面の キラッ は 出さない（「きれい！」の 札 だけ）。
//           おそうじの あと 馬が くんくん しに 行く 間も、ボタンを 押せば すぐ 次の お世話が 始まる（cancelAfter）
//         「連続で撫ですぎると、馬がバグる。撫でたあとのごろんをすると、馬が宙に少し浮き、地面と空中をいったりきたりする」→
//           もと：10こ目の ハートの 反応（のび 4.6秒・小さい 馬の はしゃぐ）が ごろん（横に なる）と 重なって、横に なった まま 体が はずんで いた。
//           抽選は 反応が おわって から・はしゃぐ／あくび などは 抽選の ときは 出さない・横に なる 間は お世話の 反応を 止める（tc_horse.js）
//       10こで 1/66 の 抽選 → 当たり：ぴょん ＋ お世話 5回 解放／ハズレ：ごろん（どちらも 少し しゃがんで ためてから）
//       ※ぴょんは 当たりの 合図 なので、ほかの 場面では とばない（小さい 子の はしゃぎも とばない）
//   ・お世話の ストック：10分で +1・最高 20（解放の +5 も 20 まで ※仮）
//   ・ちかちか しない（光らせない・ふくらむ ものは ゆっくり）
//   TCCare.init(o)・TCCare.pre(t, dt)（馬を 動かす 前）・TCCare.post(t)（馬を 描いた あと）・TCCare.input(kind, x, y, t)（フィールドの 絵の px）
//   見本：preview3d.html?care=pet_a など（決まった 指の 動きを 時間で 流す・音の きっかけは window.__events()）
//   ・撫でる の 流れ（11/09 09:23 まさちゃん → 第4.151版で 早く）：ボタンを 押す → 馬が その場で 横向きに なる（前は 画面の いちばん 手前まで 歩いて 来た）
//       → 画面が ふわっと ズーム（ゲージ・ボタンは ズーム しない）→ 撫でる → 反応が 終わったら ゆっくり もとに もどる
//   ・呼ぶ（11/09 09:27 まさちゃん）：近づいて くる／振り向く／甘える を ランダム（1/3 ずつ：09:35 まさちゃん「それでいいよ！」）
//   ・ごはん（お世話トークン 1つ）：エサ・リンゴ・ニンジンから えらぶ（今日の 好物は 日ごとに かわる）
//       エサ → その場で バケツから もぐもぐ（3回で からっぽ）→ ぺろっ／リンゴ・ニンジン → 手から 3口（シャクッ）
//       好物 → 大よろこび・金のニンジン（ニンジンの 1/30）→ なかよし +3・ときどき おかわりの目（なでると まんぞく）
//   ・おそうじ（お世話トークン 1つ）：うんちを ほうきで 3回 はいて ちりとりへ →「きれい！」の 札（第4.151版：地面の キラッ と 花は なし）→ 馬が くんくん
//       うんちが ない 時は 落ち葉など（季節：春 花びら・夏 わら・秋 もみじ・冬 雪）・金のうんち（うんちの 1/20）→「運がついた！」高確ゾーン（お世話 5回）
//       ときどき 馬が ほうきを かじろうと する
//   ・お世話（ごはん・おそうじ）の 演出が おわったら、当たって いれば「ピロン」と ポイント
const TCCare = (() => {
  const TAU = Math.PI * 2, W = 1052, H = 1657;
  const clamp = (x, a, b) => Math.max(a, Math.min(b, x)), sm = x => { x = clamp(x, 0, 1); return x * x * (3 - 2 * x); };
  const lerp = (a, b, u) => a + (b - a) * u, mixP = (a, b, u) => [lerp(a[0], b[0], u), lerp(a[1], b[1], u)];
  const backOut = x => { x = clamp(x, 0, 1); const c = 1.7; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
  const easeOut = x => 1 - Math.pow(1 - clamp(x, 0, 1), 3), easeIO = x => { x = clamp(x, 0, 1); return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
  const hash = n => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
  const angDiff = (a, b) => { let d = (b - a) % TAU; if (d > Math.PI) d -= TAU; if (d < -Math.PI) d += TAU; return d; };
  const FONT = '"BIZ UDPGothic", BIZ, "Hiragino Sans", "Noto Sans CJK JP", sans-serif';
  const AP = p => (typeof window !== 'undefined' && typeof window.TC_ASSET === 'function') ? window.TC_ASSET(p) : p;      // 絵の 場所（アプリは 名前だけ）
  const RULE = { strokes: 3, strokeLen: 34, cool: 7, streak: 5, perMin: 5, max: 10, win: 1 / 66, unlock: 5, stockMax: 20, stockEvery: 600 };
  const HURRY = 2.8, ZOOM_IN = 0.5, ZOOM_OUT = 0.6, NEAR_Y = 1040, STEP_Y = 230, ZOOM_MIN = 2.2, ZOOM_MAX = 2.7;
  //   第4.151版：急ぎ足（歩く・向きを かえる 速さの 倍）・ズームの 秒（前は 0.95）・呼ぶで 来る 所（いちばん 手前まで 歩かない：いまの 所から STEP_Y だけ 手前・NEAR_Y より 奥なら NEAR_Y まで）
  //   ズームの 上限：いちばん 手前まで 来た とき（2.2倍）と 同じ 大きさに 見える 倍率（奥に 立って いる ぶん 大きく 寄る・2.7倍まで）

  let g = null, HO = null, BR = null, O = {}, rnd = Math.random, apple = null, carrot = null, carrotG = null, bucket = null, BANNER = null, PROPS = null;
  const FRONT = { x: 526, y: 1372 };          // 画面の いちばん 手前（撫でる・呼ぶで 来る 所）
  function front() {                          // 大きな 馬（幻の馬・神様馬：5段階の 1.7倍）は 横向きで 画面に 収まる 所まで 下がる（11/09 11:38 まさちゃん「他の馬と同じ動きにして！」）
    let y = FRONT.y; while (y > 960 && TCHorse.scaleAt(HO, y) * 1.8 > 0.47 * W) y -= 8; return { x: FRONT.x, y, big: y < FRONT.y };      // 大きな 馬は まん中（頭も しっぽも 画面に 入る）
  }
  const BTN = { pet: [170, 1494], feed: [407, 1494], clean: [644, 1494], call: [881, 1494] }, BTN_R = 70, HELP = [678, 97];      // HELP：説明書の「？」
  const S = { on: false, heart: 0, heartShow: 0, stock: 3, stockShow: 3, got: [], coolUntil: -1e9, coolFrom: -1e9, ses: null, hand: null, fx: [], ev: [], sched: [],
    greeted: false, busy: false, lot: null, holdUntil: -1, drainT: null, demo: null, t0: null, finger: null, readyT: null, stockBump: null,
    petN: 0, petLast: -1e9, petGen: 0, callN: 0, callLast: -1e9, callCoolUntil: -1e9, callCoolFrom: -1e9,
    phase: 'idle', mode: null, route: null, zoom: { z: 1, cx: W / 2, cy: H / 2 }, zA: null, zB: null, zT0: 0, zDur: 1, marks: {}, press: { pet: -9, call: -9, feed: -9, clean: -9 }, petIdle: 0, callKind: null,
    chooser: null, feed: null, clean: null, fav: 'apple', high: 0, highBump: null, popVal: null, stockDrop: null };
  const POOP = [];          // うんちの 絵（おそうじで ほうきで 動かす とき）

  // ---------- 紙の 絵 ----------
  function tone(hex, k) {
    const n = parseInt(hex.slice(1), 16); let r = n >> 16, gg = (n >> 8) & 255, b = n & 255;
    if (k >= 1) { const u = k - 1; r += (255 - r) * u; gg += (255 - gg) * u; b += (255 - b) * u; } else { r *= k; gg *= k; b *= k; }
    return `rgb(${r | 0},${gg | 0},${b | 0})`;
  }
  function pf(pts, fill) {            // 面（となりの 面との すきまが 見えない ように 同じ 色で ふちも ぬる）
    g.beginPath(); g.moveTo(pts[0][0], pts[0][1]); for (let i = 1; i < pts.length; i++) g.lineTo(pts[i][0], pts[i][1]); g.closePath();
    g.fillStyle = fill; g.fill(); g.strokeStyle = fill; g.stroke();
  }
  function polyP(q, x, y, r, n, rot) { q.beginPath(); for (let i = 0; i < n; i++) { const an = rot + i * TAU / n; if (i) q.lineTo(x + Math.cos(an) * r, y + Math.sin(an) * r); else q.moveTo(x + Math.cos(an) * r, y + Math.sin(an) * r); } q.closePath(); }      // 角ばった 丸（折り紙の かじった あと）
  function line(a, b, col) { g.strokeStyle = col; g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(b[0], b[1]); g.stroke(); }
  function label(txt, x, y, size, fill, edge, ew, align) {
    g.font = `700 ${size}px ${FONT}`; g.textAlign = align || 'center'; g.textBaseline = 'middle';
    if (edge) { g.lineJoin = 'round'; g.lineWidth = ew; g.strokeStyle = edge; g.strokeText(txt, x, y); }
    g.fillStyle = fill; g.fillText(txt, x, y);
  }
  // 折り紙の ハート（左は 光が 当たって 明るく・右は かげ）
  const HP = [[0, 0.95], [-0.98, -0.02], [-1.0, -0.42], [-0.72, -0.82], [-0.3, -0.86], [0, -0.5], [0.3, -0.86], [0.72, -0.82], [1.0, -0.42], [0.98, -0.02]];
  function heart(x, y, r, rot, a, col) {
    if (a <= 0.003 || r <= 0.3) return;
    col = col || '#ff7aa6';
    g.save(); g.globalAlpha *= a; g.translate(x, y); g.rotate(rot || 0); g.scale(r, r); g.lineWidth = 0.9 / r; g.lineJoin = 'round';
    const [B, L1, L2, L3, L4, C, R4, R3, R2, R1] = HP;
    pf([B, L1, C], tone(col, 1.05)); pf([L1, L2, L3, C], tone(col, 1.15)); pf([L3, L4, C], tone(col, 1.3));
    pf([B, C, R1], tone(col, 0.84)); pf([C, R3, R2, R1], tone(col, 0.93)); pf([C, R4, R3], tone(col, 1.05));
    g.lineWidth = 1.2 / r; line(B, C, 'rgba(120,40,70,0.22)'); line(L1, C, 'rgba(120,40,70,0.1)'); line(R1, C, 'rgba(120,40,70,0.12)'); line(L3, C, 'rgba(255,255,255,0.25)'); line(R3, C, 'rgba(120,40,70,0.1)');
    g.restore();
  }
  function heartSlot(x, y, r) {        // ハートの 入る 所（うすい 紙の くぼみ）
    g.save(); g.translate(x, y); g.scale(r, r); g.lineWidth = 2 / r;
    g.beginPath(); HP.forEach((p, i) => i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1])); g.closePath();
    g.fillStyle = '#f6e2e6'; g.fill(); g.strokeStyle = '#e8c1cc'; g.stroke(); g.restore();
  }
  // 紙の 星（4つの 角）
  function star(x, y, r, rot, a, col) {
    if (a <= 0.003 || r <= 0.3) return; col = col || '#f5d06a';
    g.save(); g.globalAlpha *= a; g.translate(x, y); g.rotate(rot || 0); g.lineWidth = 0.8;
    const k = 0.3;
    pf([[0, -r], [r * k, -r * k], [r, 0], [r * k, r * k], [0, r], [-r * k, r * k], [-r, 0], [-r * k, -r * k]], tone(col, 1.18));
    pf([[0, -r], [r * k, -r * k], [r, 0], [0, 0]], col); pf([[0, r], [-r * k, r * k], [-r, 0], [0, 0]], col);
    g.restore();
  }
  // 紙の 手（右手の こう・中指の 先が さわる 所：x,y）。s：大きさ・press：0 浮く〜1 さわる・open：0〜1 ひらく
  const HAND = (() => {
    const F = [[-0.335, 0.15, 0.215], [-0.105, 0.0, 0.225], [0.125, 0.08, 0.215], [0.34, 0.3, 0.19]], base = 0.76;
    const fingers = F.map(([cx, tip, w]) => ({
      L: [[cx - w / 2, base], [cx - w / 2, tip + w * 0.45], [cx - w * 0.2, tip], [cx, tip], [cx, base]],
      R: [[cx, base], [cx, tip], [cx + w * 0.2, tip], [cx + w / 2, tip + w * 0.45], [cx + w / 2, base]],
      k: [[cx - w / 2, tip + (base - tip) * 0.5], [cx + w / 2, tip + (base - tip) * 0.5]] }));
    const T = [[-0.47, 1.12], [-0.73, 0.82], [-0.8, 0.55], [-0.69, 0.46], [-0.56, 0.62], [-0.46, 0.8]];
    return { fingers, thumb: [[T[0], T[1], T[2], T[3]], [T[0], T[3], T[4], T[5]]],
      palm: [[[-0.47, 0.72], [0.47, 0.72], [0.0, 1.08]], [[0.47, 0.72], [0.5, 1.2], [0.28, 1.5], [0.0, 1.08]], [[-0.47, 0.72], [0.0, 1.08], [-0.27, 1.5], [-0.49, 1.18]], [[0.0, 1.08], [0.28, 1.5], [-0.27, 1.5]]],
      cuff: [[[-0.31, 1.45], [0.31, 1.45], [0.34, 1.62], [-0.34, 1.62]], [[-0.34, 1.62], [0.34, 1.62], [0.36, 1.82], [-0.36, 1.82]]] };
  })();
  let HAND_PATH = null, HAND_BB = null;
  function handPath() {                // 手の 形（1つの 形に まとめる）
    if (!HAND_PATH) {
      HAND_PATH = new Path2D(); let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
      for (const p of [...HAND.thumb, ...HAND.palm, ...HAND.cuff, ...HAND.fingers.flatMap(f => [f.L, f.R])]) {
        HAND_PATH.moveTo(p[0][0], p[0][1]); for (let i = 1; i < p.length; i++) HAND_PATH.lineTo(p[i][0], p[i][1]); HAND_PATH.closePath();
        for (const q of p) { x0 = Math.min(x0, q[0]); y0 = Math.min(y0, q[1]); x1 = Math.max(x1, q[0]); y1 = Math.max(y1, q[1]); }
      }
      HAND_BB = [x0, y0, x1, y1];
    }
    return HAND_PATH;
  }
  const HAND_SH = {};
  function handShadow(lv) {            // 手の かげ（ぼかした 絵を 5だんかい 先に 作って おく：ctx.filter は 使わない＝前の コマの 手が 消えずに のこる 不具合の 元・iPhone でも 重く ない）
    if (HAND_SH[lv]) return HAND_SH[lv];
    const path = handPath(), [x0, y0, x1, y1] = HAND_BB, S0 = 64, bl = (1.5 + 3.5 * lv / 4) * S0 / 62, pad = Math.ceil(bl * 3) + 2;
    const c = document.createElement('canvas'); c.width = Math.ceil((x1 - x0) * S0) + pad * 2; c.height = Math.ceil((y1 - y0) * S0) + pad * 2;
    const q = c.getContext('2d'), off = c.width + 60;
    q.shadowColor = '#2b1a0e'; q.shadowBlur = bl * 2; q.shadowOffsetX = off;      // 形は 絵の 外（左）に かいて、かげ だけを 絵の 中へ
    q.setTransform(S0, 0, 0, S0, pad - x0 * S0 - off, pad - y0 * S0); q.fillStyle = '#2b1a0e'; q.fill(path, 'nonzero');
    return (HAND_SH[lv] = { c, S0, ox: pad - x0 * S0, oy: pad - y0 * S0 });
  }
  function hand(x, y, s, rot, press, a, open) {
    if (a <= 0.003 || open <= 0.003) return;
    const lift = 1 - press, P = '#fdf1dd';
    const sh = handShadow(Math.round(clamp(lift, 0, 1) * 4));
    g.save(); g.globalAlpha *= a * (0.2 + 0.08 * press);
    g.translate(x + (4 + 12 * lift) * s / 46, y + (6 + 16 * lift) * s / 46); g.rotate(rot); g.scale(s * open / sh.S0, s / sh.S0); g.drawImage(sh.c, -sh.ox, -sh.oy);
    g.restore();
    g.save(); g.globalAlpha *= a; g.translate(x, y - 5 * lift * s / 46); g.rotate(rot); const sc = s * (1 + 0.05 * lift); g.scale(sc * open, sc); g.lineWidth = 0.9 / sc; g.lineJoin = 'round';
    const [c0, c1] = HAND.cuff; pf(c0, '#9fd0f0'); pf(c1, '#7db9e2'); g.lineWidth = 1.2 / sc; line([-0.34, 1.62], [0.34, 1.62], 'rgba(40,80,120,0.25)'); g.lineWidth = 0.9 / sc;
    const [p0, p1, p2, p3] = HAND.palm; pf(p0, tone(P, 1.04)); pf(p2, tone(P, 0.97)); pf(p1, tone(P, 0.88)); pf(p3, tone(P, 0.92));
    pf(HAND.thumb[0], tone(P, 1.02)); pf(HAND.thumb[1], tone(P, 0.9));
    for (const f of HAND.fingers) { pf(f.L, tone(P, 1.03)); pf(f.R, tone(P, 0.9)); }
    g.lineWidth = 1.3 / sc;
    for (const f of HAND.fingers) line(f.k[0], f.k[1], 'rgba(150,100,60,0.22)');
    line([-0.47, 0.72], [0.47, 0.72], 'rgba(150,100,60,0.18)'); line([0, 1.08], [-0.47, 0.72], 'rgba(150,100,60,0.12)'); line([0, 1.08], [0.47, 0.72], 'rgba(150,100,60,0.16)');
    g.restore();
  }
  function paperSquare(x, y, r, rot, a) {       // たたんだ 紙（手が ひらく 前・とじた 後）
    if (a <= 0.003 || r <= 0.3) return;
    g.save(); g.globalAlpha *= a; g.translate(x, y); g.rotate(rot); g.lineWidth = 0.8;
    pf([[0, -r], [r, 0], [0, r], [-r, 0]], '#fbeeda'); pf([[0, -r], [r, 0], [0, r]], '#ecd9bb'); pf([[-r, 0], [0, -r], [0, 0]], '#fff6e8');
    g.restore();
  }
  // 小さな 紙の 札（音の ことば：すりすり など）
  function tag(x, y, txt, size, a, sc, rot, col) {
    if (a <= 0.003 || sc <= 0.01) return;
    g.save(); g.globalAlpha *= a; g.translate(x, y); g.rotate(rot || 0); g.scale(sc, sc);
    g.font = `700 ${size}px ${FONT}`; const w = g.measureText(txt).width + size * 1.0, h = size * 1.55, c = size * 0.38; g.lineWidth = 0.8;
    pf([[-w / 2 + 4, -h / 2 + 6], [w / 2 + 4, -h / 2 + 6], [w / 2 + 4, h / 2 + 6], [-w / 2 + 4, h / 2 + 6]], 'rgba(40,20,5,0.18)');
    pf([[-w / 2, -h / 2], [w / 2 - c, -h / 2], [w / 2, -h / 2 + c], [w / 2, h / 2], [-w / 2, h / 2]], '#fff8ea');
    pf([[-w / 2, 0.06 * h], [w / 2, 0.06 * h], [w / 2, h / 2], [-w / 2, h / 2]], '#f6e8cc');
    pf([[w / 2 - c, -h / 2], [w / 2, -h / 2 + c], [w / 2 - c, -h / 2 + c]], '#e3c993');
    label(txt, 0, 1, size, col || '#7a4520');
    g.restore();
  }
  // 紙の 板（上の なかよしゲージ・ストック）
  function panel(x, y, w, h, c) {
    g.save(); g.lineWidth = 0.8;
    pf([[x + 5, y + 7], [x + w + 5, y + 7], [x + w + 5, y + h + 7], [x + 5, y + h + 7]], 'rgba(40,20,5,0.2)');
    pf([[x, y], [x + w - c, y], [x + w, y + c], [x + w, y + h], [x, y + h]], '#fff8ec');
    pf([[x, y + h * 0.55], [x + w, y + h * 0.55], [x + w, y + h], [x, y + h]], '#f8ecd4');
    pf([[x + w - c, y], [x + w, y + c], [x + w - c, y + c]], '#e6cf9f');
    g.restore();
  }

  // ---------- ズーム（撫でる 間だけ・ゲージと ボタンは ズーム しない）----------
  const toS = p => [(p[0] - S.zoom.cx) * S.zoom.z + W / 2, (p[1] - S.zoom.cy) * S.zoom.z + H / 2];       // フィールドの px → 画面（ズーム後）
  const toW = q => [(q[0] - W / 2) / S.zoom.z + S.zoom.cx, (q[1] - H / 2) / S.zoom.z + S.zoom.cy];
  function setZoom(t, to, dur) { S.zA = Object.assign({}, S.zoom); S.zB = to; S.zT0 = t; S.zDur = dur; }
  const zCap = y => clamp(ZOOM_MIN * TCHorse.scaleAt(HO, FRONT.y) / TCHorse.scaleAt(HO, y), ZOOM_MIN, ZOOM_MAX);      // その 所での ズームの 上限
  function zoomFor() {                 // 馬が 画面の 8割の 幅に なる ズーム（まん中は 体の まん中）
    const e = TCHorse.extent(HO); if (!e) return { z: 1, cx: W / 2, cy: H / 2 };
    const z = clamp(Math.min(0.8 * W / (e[2] - e[0]), 0.56 * H / (e[3] - e[1])), 1, zCap(BR.y));
    const hw = W / (2 * z), hh = H / (2 * z);
    return { z, cx: clamp((e[0] + e[2]) / 2, hw, W - hw), cy: clamp((e[1] + e[3]) / 2 + 0.01 * H / z, hh, H - hh) };
  }

  // ---------- 体の 場所 ----------
  const P = n => TCHorse.where(HO, n);
  const CHAIN = [['nose', 'nose'], ['eye', 'head'], ['poll', 'head'], ['neck', 'neck'], ['withers', 'neck'], ['back', 'back'], ['rump', 'back']];
  function zoneAt(x, y) {              // さわった 所（フィールドの px）→ 体の 場所（はなれて いれば null）
    const pts = CHAIN.map(([n, z]) => [P(n), z]).filter(q => q[0]);
    if (pts.length < 2) return null;
    const R = 0.46 * TCHorse.scaleAt(HO, BR.y); let best = null;
    for (let i = 0; i < pts.length - 1; i++) {
      const a = pts[i][0], b = pts[i + 1][0], dx = b[0] - a[0], dy = b[1] - a[1], L2 = dx * dx + dy * dy || 1;
      const u = clamp(((x - a[0]) * dx + (y - a[1]) * dy) / L2, 0, 1), d = Math.hypot(x - a[0] - dx * u, y - a[1] - dy * u);
      if (d < R && (!best || d < best.d)) best = { d, zone: u < 0.5 ? pts[i][1] : pts[i + 1][1] };
    }
    return best;
  }
  function sideToward(x, y) {          // 首を どちらに ふると 人（画面の こちら側）の 方を 向くか：＋1／−1
    //   首を ＋に ふると 鼻は 体の −z へ。体の ＋z が こちらを 向いて いれば −1。正面・後ろ 向きの ときは 指の 左右で きめる
    const L = HO.last, n = P('nose'); if (!L || !n) return 1;
    const zz = L.R3[8], zx = L.R3[6];
    if (Math.abs(zz) > 0.25) return zz > 0 ? -1 : 1;
    return ((x - n[0]) * -zx) >= 0 ? 1 : -1;
  }
  const react = (k, dur, t, o) => TCHorse.react(BR, k, dur, t, o);
  const ev = (t, k, o) => { const e = Object.assign({ t: +t.toFixed(4), k }, o || {}); if (S.demo || !O.onEvent) S.ev.push(e); if (O.onEvent) { try { O.onEvent(e); } catch (er) { } } };
  const at = (t, fn) => S.sched.push({ t, fn });
  const fx = o => S.fx.push(o);
  const SLOT = i => [26 + 134 + i * 44, 34 + 86];          // ゲージの ハートの 場所
  const mark = (k, t) => { if (S.marks[k] == null) S.marks[k] = t - S.t0; };
  const tagW = (p, txt, t, o) => { if (p) fx(Object.assign({ k: 'tag', t0: t, w: p.slice(), txt, size: 36, dur: 1.5, rot: (hash(t) - 0.5) * 0.16 }, o || {})); };      // 体の 所に 札（ズームに ついて 動く）

  // ---------- 手前へ 来る（撫でる・呼ぶ）----------
  function zoomGuess(x, y) {            // 横向きで (x, y) に 立った ときの ズーム（着く 前から カメラを 寄せる：体の 幅 2.75・高さ 1.8 × 体の 高さ）
    const sc = TCHorse.scaleAt(HO, y), z = clamp(Math.min(0.8 * W / (2.75 * sc), 0.56 * H / (1.8 * sc)), 1, zCap(y)), hw = W / (2 * z), hh = H / (2 * z);
    return { z, cx: clamp(x, hw, W - hw), cy: clamp(y - 0.83 * sc + 0.01 * H / z, hh, H - hh) };
  }
  function approach(t) {               // 呼ぶ（近づく・甘える）：近くへ 急ぎ足で 来て、着いたら その場で 横向きに なる（顔と 体が よく 見える）
    //   第4.151版（まさちゃん「ボタンを押してから行われるまでが遅すぎる」）：いちばん 手前まで 歩かない（いまの 所から STEP_Y だけ 手前。NEAR_Y より 奥なら NEAR_Y まで）。大きな 馬（幻の馬・神様馬の 歩く 形）は 前と 同じ 所へ
    const fr = front(), ex = fr.big ? fr.x : lerp(fr.x, clamp(BR.x, fr.x - 170, fr.x + 170), 0.45), ey = fr.big ? fr.y : clamp(BR.y + STEP_Y, NEAR_Y, fr.y);
    S.route = [[ex, ey]]; S.turnAfter = true; S.phase = 'approach'; nextLeg(t);
  }
  function comeNear(t) {                // 撫でる・ごはん：歩かないで その場で 横向きに なる（カメラは 押した ときから 寄る）＝どこに いても すぐ 始まる（第4.151版）
    //   少し 歩く のは、横向きに なると 体が 画面から はみ出す 所に いる とき・大きな 馬（幻の馬・神様馬の 歩く 形）が まん中に いない とき だけ
    const fr = front(), side = Math.abs(Math.sin(BR.dir)) < 0.4, half = 1.8 * TCHorse.scaleAt(HO, BR.y) + 12;
    let tx = BR.x, ty = BR.y;
    if (fr.big) { if (Math.abs(BR.x - fr.x) > 50) tx = fr.x; if (BR.y > fr.y + 36) ty = fr.y; }
    else if (half < W / 2) tx = clamp(BR.x, half, W - half);
    const here = Math.abs(tx - BR.x) < 20 && ty === BR.y;
    if (here && side) { if (BR.mode === 'walk' || BR.mode === 'run') { BR.mode = 'idle'; BR.until = t + 30; } arrived(t); return; }
    S.turnAfter = true; S.phase = 'approach'; BR.want.graze = 0; BR.want.look = [0, 0];
    if (here) { S.route = []; BR.hurry = HURRY; BR.mode = 'idle'; BR.until = t + 30; }      // その場で 横向きに（つぎの コマで 回りはじめる）
    else { S.route = [[tx, ty]]; nextLeg(t); }
    setZoom(t, zoomGuess(tx, ty), 0.8); ev(t, 'zoomin');
  }
  function nextLeg(t) { const p = S.route.shift(); Object.assign(BR, { tgt: p, mode: 'walk', until: t + 30, forcedWalk: true, hurry: HURRY }); BR.want.graze = 0; BR.want.look = [0, 0]; }
  function arrived(t) {
    mark('A', t); BR.hurry = 1;
    if (S.mode === 'pet' || S.mode === 'feed') {
      const zf = zoomFor();
      if (S.mode === 'feed') { const n = P('nose'); if (n) { const hw = W / (2 * zf.z); zf.cx = clamp(lerp(zf.cx, n[0], 0.3), hw, W - hw); } }      // ごはんは 顔（口もと）が よく 見える ように 少し 顔の 方へ
      if (S.zoom.z > 1.05 || S.zB) {      // 向きを かえる 間に もう 寄せて ある：仕上げ（0.25秒）は 待たないで すぐ 始める
        setZoom(t, zf, 0.25);
        if (S.mode === 'feed') feedStart(t); else { S.phase = 'pet'; S.petIdle = t; mark('R', t); ev(t, 'ready2'); }
      } else { S.phase = 'zoomin'; setZoom(t, zf, ZOOM_IN); ev(t, 'zoomin'); }
    }
    else callArrive(t);
  }
  function endCare(t) {                 // 撫でる・呼ぶ おしまい：ズームを もどして 馬を 自由に
    if (S.zoom.z > 1.001 || S.zB) { S.phase = 'zoomout'; setZoom(t, { z: 1, cx: W / 2, cy: H / 2 }, ZOOM_OUT); ev(t, 'zoomout'); }
    else release(t);
  }
  function release(t) {
    const m = S.mode; S.phase = 'idle'; S.mode = null; mark('Z', t); BR.careHold = false; BR.want.look = [0, 0]; BR.until = t + 2.5; BR.forcedWalk = false; BR.hurry = 1; S.grazeOK = false;
    if (m === 'call') { S.callLast = t; if (S.callN >= RULE.streak) { S.callN = 0; S.callCoolUntil = t + RULE.cool; S.callCoolFrom = t; ev(t, 'callcool'); } }      // 呼ぶ：5回目が おわったら 7秒 できない
    if ((m === 'feed' || m === 'clean') && S.popVal) {
      const pz = typeof S.popVal === 'object' ? S.popVal : { k: 'pt', v: S.popVal }; S.popVal = null;
      if (pz.k === 'pt') at(t + 0.15, tt => { fx({ k: 'pointpop', t0: tt, v: pz.v, dur: 2.0 }); ev(tt, 'piron'); if (O.onPrize) O.onPrize(pz); });
      else if (O.onPrize) at(t + 0.4, tt => O.onPrize(pz));          // ルーレット・チケット：アプリが 演出を 出す
    }      // 当たって いれば ピロン（お世話の 演出が おわってから）
    if (m === 'clean' && S.clean && S.clean.sniff && !BR.stand) {          // きれいに なった 所へ 行って くんくん
      const c = S.clean; S.clean = null; BR.careHold = true; S.mode = 'after'; S.phase = 'after'; S.holdUntil = Infinity; S.afterT = t;
      const d = Math.atan2((c.y - BR.y) / 0.5, c.x - BR.x), sc = TCHorse.scaleAt(HO, c.y);
      Object.assign(BR, { tgt: [c.x - Math.cos(d) * 1.05 * sc, c.y - Math.sin(d) * 0.5 * 1.05 * sc], mode: 'walk', until: t + 30, forcedWalk: true, hurry: HURRY });
      S.afterSniff = true;
    } else if (m === 'clean') { S.clean = null; mark('Z2', t); }
    if (m === 'feed') S.feed = null;
  }

  // ---------- ごはん ----------
  const FOOD = { esa: 'エサ', apple: 'リンゴ', carrot: 'ニンジン' };
  function useToken(t, k) {
    if (S.stock < 1) { fx({ k: 'tagUI', t0: t, x: BTN[k][0], y: BTN[k][1] - 150, txt: 'お世話トークンが たまるまで まってね', size: 30, dur: 1.8 }); ev(t, 'wait'); return false; }
    S.stock -= 1; S.stockDrop = t; ev(t, 'token'); return true;
  }
  function careLottery() {               // お世話の 抽選（見本：ポイントだけ。アプリ：O.lottery() → { k: 'pt', v } ・{ k: 'rt', tier }・{ k: 'tk', n }）
    if (O.lottery) return O.lottery();
    if (S.demo && S.demo.pt !== undefined) return S.demo.pt;
    const r = rnd(); let a = 0;
    for (const [p, v] of [[1 / 85, 100], [1 / 99, 200], [1 / 121, 300]]) { a += p; if (r < a) return v; }
    return null;
  }
  function pressFeed(t) {
    cancelAfter(t);
    S.press.feed = t; ev(t, 'button');
    if (S.busy || S.phase !== 'idle' || BR.sl > 0.001) return;
    S.chooser = { t0: t, pick: null, pickT: null }; S.phase = 'choose'; S.mode = 'feed'; BR.careHold = true; S.holdUntil = Infinity; ev(t, 'chooser');
  }
  function pick(t, kind) {
    if (!S.chooser || S.chooser.pick) return;
    S.chooser.pick = kind; S.chooser.pickT = t; ev(t, 'pick');
    at(t + 0.25, tt => {
      S.chooser = null;
      if (!useToken(tt, 'feed')) { S.phase = 'idle'; S.mode = null; BR.careHold = false; return; }
      const gold = kind === 'carrot' && (S.demo && S.demo.gold != null ? S.demo.gold : rnd() < 1 / 30);
      S.feed = { kind, gold, fav: kind === S.fav, bites: 0, t0: tt }; S.popVal = careLottery();
      if (BR.stand) { BR.reacts = []; mark('A', tt); feedStart(tt); return; }          // 幻の馬・神様馬：正面の まま
      comeNear(tt);
    });
  }
  function feedStart(t) {
    const F = S.feed; S.phase = 'feed'; mark('F', t); ev(t, 'feedstart');
    BR.want.look = [0, 0]; BR.reacts = (BR.reacts || []).filter(r => r.k !== 'look');      // 顔は まっすぐ（11/09 13:44 まさちゃん「顔がバケツから避けちゃってるからバケツに真っ直ぐにして！」）
    const s = TCHorse.scaleAt(HO, BR.y), n = P('nose');
    if (F.kind === 'esa') {             // バケツ：草を 食べる 時に 鼻が 来る 所の 下の 地面（いまの 場所・向きで 体の 形を 先に 計算）
      const tmp = Object.assign({}, BR, { graze: 1, look: [0, 0], lookS: [0, 0], reacts: [{ k: 'deep', t0: t - 2, dur: 4.4 }] }), mats = TCHorse.pose(HO, tmp, t);
      const gq = TCHorse.wherePose(HO, mats, 'nose', true) || [BR.x, BR.y], nq = TCHorse.wherePose(HO, mats, 'nose'), pq = TCHorse.wherePose(HO, mats, 'poll');
      // 鼻先だけ バケツに 入る（11/09 13:35 まさちゃん「顔がバケツに埋まりすぎてるから顔が少し入るくらいにして！」）：
      //   バケツの まん中は 鼻の 下・ふちの 高さは 鼻と 目の あいだの 下から 3わり（台の 足の 長さで 合わせる）
      const eq = TCHorse.wherePose(HO, mats, 'eye'), bx = nq ? (pq ? nq[0] * 0.86 + pq[0] * 0.14 : nq[0]) : gq[0];
      const by = gq[1] + 4, rimW = nq && eq ? nq[1] - 0.3 * (nq[1] - eq[1]) : by - 0.78 * s;
      const lh = clamp((by - rimW) / s - 0.48, 0.04, 0.9);          // 台の 足（体の 高さ 1 に 対して）：ふち ＝ 足 ＋ 台 0.06 ＋ バケツ 0.42
      F.bucket = { x: bx, y: by, lh, level: 3, t0: t, hideT: null }; ev(t, 'unfold'); at(t + 0.25, tt => ev(tt, 'bucket'));
      const ds = [t + 1.2, t + 2.2, t + 3.2];          // エサが 減る 時刻（もぐもぐ）
      if (PROPS && PROPS.bucket) {                      // まさちゃんの 3D の バケツ・エサ：エサが 減るたびに 顔が バケツの 中へ（11/09 14:02・14:13）
        const tmp1 = Object.assign({}, tmp, { reacts: [{ k: 'deep', t0: t - 2, dur: 4.4, ds: [t - 10] }] }), mats1 = TCHorse.pose(HO, tmp1, t);
        F.b3 = place3(TCHorse.anchorPose(HO, mats, 'nose'), TCHorse.anchorPose(HO, mats, 'eye'), TCHorse.anchorPose(HO, mats, 'poll'), TCHorse.anchorPose(HO, mats1, 'nose'), ds);
      }
      at(t + 0.3, tt => { S.grazeOK = true; BR.want.graze = 1; react('deep', F.b3 ? 4.8 : 4.4, tt, F.b3 ? { ds } : null); });
      for (let k = 0; k < 3; k++) at(t + 1.2 + k * 1.0, tt => { F.bucket.level = 2 - k; ev(tt, 'munch', { n: k }); const b = F.bucket, rw = F.b3 ? TCHorse.project(HO, [F.b3.cx, F.b3.R, F.b3.cz]) : null; fx({ k: 'crumbs', t0: tt, w: rw || [b.x, b.y - (b.lh + 0.48) * s], col: ['#e8c46a', '#d9a94a', '#f2dc94'] }); });
      at(t + 4.4, tt => { BR.want.graze = 0; S.grazeOK = false; });
      at(t + 4.9, tt => { react('lick', 1.3, tt, { side: sideToward(BR.x, BR.y + 200) }); ev(tt, 'lick'); tagW(P('nose'), 'ぺろっ', tt + 0.2, { off: [0, -90], size: 34 }); });
      at(t + 6.1, tt => { F.bucket.hideT = tt; ev(tt, 'fold'); });
      at(t + 6.7, tt => feedAfter(tt));
    } else {                            // リンゴ・ニンジン：手から 3口
      F.handT = t; F.itemW = itemPos(); ev(t, 'unfold');
      if (F.gold) at(t + 0.3, tt => { fx({ k: 'glint', t0: tt, dur: 3.2 }); ev(tt, 'gold'); tagW(P('nose'), '金のニンジン！', tt + 0.1, { off: [0, -150], size: 36, dur: 1.8, col: '#b07a10' }); });
      for (let k = 0; k < 3; k++) at(t + (F.gold ? 1.2 : 0.7) + k * 1.0, tt => {
        F.bites = k + 1; react('eat', 0.95, tt, { side: sideToward(BR.x, BR.y + 200) }); ev(tt, 'bite', { n: k, kind: F.kind });
        const q = F.itemW; fx({ k: 'crumbs', t0: tt, w: q, col: F.kind === 'apple' ? ['#f4efe0', '#d9343c', '#f7e9c8'] : F.gold ? ['#ffd65c', '#fff1b0', '#e9b13a'] : ['#f08a2a', '#ffb25c', '#f6c38a'] });
        if (k === 0) tagW(P('nose'), 'シャクッ', tt + 0.05, { off: [-20, -100], size: 34, dur: 1.0 });
      });
      at(t + (F.gold ? 3.9 : 3.4), tt => { F.handHide = tt; ev(tt, 'fold'); });
      at(t + (F.gold ? 4.3 : 3.8), tt => feedAfter(tt));
    }
  }
  function feedAfter(t) {                // 食べた あと：好物・金のニンジン・おかわりの目
    const F = S.feed; let end = t + 0.4;
    if (F.fav) { at(t + 0.1, tt => { react('happy', 2.6, tt); react('nod', 1.4, tt + 0.3); ev(tt, 'yummy'); tagW(P('poll'), 'だいすき！', tt + 0.1, { off: [30, -100], size: 40, dur: 2.0 });
      for (let k = 0; k < 5; k++) at(tt + 0.2 + k * 0.3, t2 => { const p = P('poll'); if (p) fx({ k: 'mini', t0: t2, w: [p[0] + (hash(t2 * 3) - 0.5) * 120, p[1] - 10], r: 22, dx: (hash(t2 * 7) - 0.5) * 70 }); ev(t2, 'heartpop'); }); }); end = t + 2.8; }
    if (F.gold) {                       // なかよし +3
      for (let k = 0; k < 3; k++) at(t + 0.3 + k * 0.3, tt => {
        const q = toS(F.itemW || itemPos()), i = Math.min(S.heart, RULE.max - 1); fx({ k: 'fly', t0: tt, x: q[0], y: q[1], i, dur: 0.8 }); ev(tt, 'heart'); S.heart = Math.min(RULE.max, S.heart + 1);
        at(tt + 0.8, t2 => { S.heartShow = Math.max(S.heartShow, i + 1); ev(t2, 'slot', { n: i + 1 }); fx({ k: 'pop', t0: t2, x: SLOT(i)[0], y: SLOT(i)[1] }); });
      });
      at(t + 0.3, tt => tagW(P('poll'), 'なかよし +3', tt, { off: [30, -110], size: 38, dur: 1.8, col: '#c2456f' }));
      end = Math.max(end, t + 2.2);
    }
    const beg = S.demo && S.demo.beg != null ? S.demo.beg : rnd() < 1 / 4;
    if (beg) {                          // おかわりの目：こちらを じっと 見る → なでると まんぞく
      at(end, tt => { S.phase = 'beg'; mark('B', tt); const side = sideToward(BR.x, BR.y + 200); react('beg', 6, tt, { side }); BR.want.look = [side * 0.6, 0.2]; ev(tt, 'beg');
        tagW(P('poll'), 'おかわり…？', tt + 0.2, { off: [30, -100], size: 34, dur: 2.4 }); S.begT = tt; });
      S.holdUntil = Infinity; S.phase = 'feedwait';
    } else { S.phase = 'feedwait'; S.holdUntil = end; at(end, tt => { S.phase = 'feeddone'; }); }
  }
  function begPet(t) {                   // おかわりの目の あとで なでた
    S.phase = 'feeddone'; BR.reacts = (BR.reacts || []).filter(r => r.k !== 'beg'); BR.want.look = [0, 0];
    react('nod', 1.4, t + 0.1); ev(t, 'rub'); fx({ k: 'mini', t0: t + 0.1, w: (P('poll') || [BR.x, BR.y]).slice(), r: 22, dx: 20 });
    tagW(P('poll'), 'まんぞく', t + 0.3, { off: [30, -100], size: 34, dur: 1.6 }); S.holdUntil = t + 1.9;
  }
  function itemPos() {                   // 手で 持つ リンゴ・ニンジンの 場所（口もと）
    const n = P('nose') || [BR.x, BR.y - 200], s = TCHorse.scaleAt(HO, BR.y);
    return [n[0] + Math.cos(BR.dir) * 0.02 * s, n[1] + 0.07 * s];
  }

  // ---------- おそうじ ----------
  function season() { const m = (O.month || new Date().getMonth() + 1); return m >= 3 && m <= 5 ? 'spring' : m >= 6 && m <= 8 ? 'summer' : m >= 9 && m <= 11 ? 'autumn' : 'winter'; }
  function pressClean(t) {
    cancelAfter(t);
    S.press.clean = t; ev(t, 'button');
    if (S.busy || S.phase !== 'idle') return;
    if (!useToken(t, 'clean')) return;
    S.mode = 'clean'; BR.careHold = true; S.holdUntil = Infinity; S.popVal = careLottery();
    const ps = BR.poops || []; let tg = null;
    if (ps.length) { const q = ps.reduce((a, b) => (b.y > a.y ? b : a)); BR.poops = ps.filter(x => x !== q); tg = { type: 'poop', x: q.x, y: q.y, img: q.img || 0, w: q.w || 0.42, gold: !!q.gold }; }
    else {                              // うんちが ない：落ち葉など（季節）
      const cx = BR.stand ? W / 2 : clamp(FRONT.x + (BR.x < FRONT.x ? 170 : -170), 260, 792), cy = BR.stand ? H * 0.82 : FRONT.y - 20, ss = season();
      tg = { type: 'leaves', x: cx, y: cy, ss, leaves: Array.from({ length: 11 }, (_, i) => ({ dx: (hash(i * 3.1) - 0.5) * 230, dy: (hash(i * 5.7) - 0.5) * 90, r: hash(i * 7.3) * TAU, s: 0.8 + 0.4 * hash(i * 2.9), c: i % 3 })) };
    }
    S.clean = { t0: t, x: tg.x, y: tg.y, tg, swipes: 0, prog: 0, sniff: tg.type === 'poop' };
    S.clean.pan = { x: tg.x - 120, y: tg.y + 6 };
    const z = BR.stand ? 1 : 1.7, hw = W / (2 * z), hh = H / (2 * z);
    if (z > 1) { S.phase = 'zoomin'; setZoom(t, { z, cx: clamp(tg.x - 20, hw, W - hw), cy: clamp(tg.y - 90, hh, H - hh) }, ZOOM_IN); ev(t, 'zoomin'); }
    else cleanStart(t);
    if (!BR.stand) { const side = sideToward(tg.x, tg.y); BR.want.look = [side * 0.6, -0.1]; }
  }
  function cleanStart(t) {
    const C = S.clean; S.phase = 'clean'; mark('C', t); C.toolT = t; ev(t, 'unfold'); at(t + 0.2, tt => ev(tt, 'unfold'));
    if (C.tg.gold) at(t + 0.2, tt => { tagW([C.x, C.y], '金のうんち！', tt, { off: [0, -120], size: 36, dur: 1.8, col: '#b07a10' }); ev(tt, 'gold'); });
  }
  function sweep(t) {                    // 1回 はいた
    const C = S.clean; C.swipes++; ev(t, 'sweep', { n: C.swipes });
    fx({ k: 'dust', t0: t, w: [lerp(C.x, C.pan.x + 30, C.swipes / 3), C.y] });
    const nose = P('nose'), br = S.finger;
    if (!C.nibbled && !BR.stand && nose && br && Math.hypot(nose[0] - br[0], nose[1] - br[1]) < 300 && (S.demo && S.demo.nibble != null ? S.demo.nibble : rnd() < 1 / 4) && C.swipes === 2) {
      C.nibbled = true; at(t + 0.1, tt => { react('nibble', 1.6, tt, { side: sideToward(br[0], br[1]) }); ev(tt, 'nibble'); tagW(P('nose'), 'もぐっ？', tt + 0.3, { off: [0, -100], size: 34, dur: 1.3 }); });
    }
    if (C.swipes >= 3) {
      at(t + 0.35, tt => { C.inPan = true; ev(tt, 'inpan'); });
      at(t + 0.8, tt => { C.foldT = tt; ev(tt, 'fold'); });
      at(t + 1.1, tt => { ev(tt, 'kira'); tagW([C.x, C.y], 'きれい！', tt, { off: [0, -130], size: 38, dur: 1.6 }); });      // 第4.151版：地面の キラッ と お花は 出さない（札 だけ）
      if (C.tg.gold) at(t + 2.2, tt => { S.high = 5; S.highBump = tt; fx({ k: 'luck', t0: tt, dur: 2.6 }); ev(tt, 'luck'); });
      S.holdUntil = t + (C.tg.gold ? 5.0 : 2.7); S.phase = 'cleanwait'; at(S.holdUntil - 0.01, tt => { if (S.phase === 'cleanwait') S.phase = 'cleandone'; });
    }
  }

  // ---------- ボタン ----------
  function cancelAfter(t) {              // おそうじの あとの くんくん（歩いて 行く・かぐ）の 間に ボタンを 押した：やめて すぐ 次の お世話へ（第4.151版）
    if (S.phase !== 'after') return;
    S.afterSniff = false; S.mode = null; S.phase = 'idle'; BR.careHold = false; BR.forcedWalk = false; BR.hurry = 1; S.holdUntil = -1; mark('Z2', t);
    for (const r of (BR.reacts || [])) if ((r.k === 'sniff' || r.k === 'swish') && r.cut == null) r.cut = Math.max(t, r.t0);
    if (BR.mode === 'walk') { BR.mode = 'idle'; BR.until = t + 2; }
  }
  function pressPet(t) {
    cancelAfter(t);
    S.press.pet = t; ev(t, 'button');
    if (S.busy || S.phase !== 'idle') return;
    if (t < S.coolUntil) { fx({ k: 'tagUI', t0: t, x: BTN.pet[0] + 40, y: BTN.pet[1] - 150, txt: `あと ${Math.ceil(S.coolUntil - t)}秒`, size: 36, dur: 1.4 }); ev(t, 'wait'); return; }
    S.mode = 'pet'; BR.careHold = true; S.holdUntil = Infinity;
    if (BR.mode === 'sleep' || BR.sl > 0.001) { S.mode = null; BR.careHold = false; return; }      // 寝て いる 間は 来ない（かり）
    if (BR.stand) { BR.reacts = []; S.phase = 'pet'; S.petIdle = t; mark('A', t); mark('R', t); ev(t, 'ready2'); return; }      // 幻の馬・神様馬：正面の まま その場で 撫でる（11/09 09:40 まさちゃん）
    comeNear(t);
  }
  function pressCall(t, kind) {
    cancelAfter(t);
    S.press.call = t; ev(t, 'button');
    if (S.busy || S.phase !== 'idle' || BR.sl > 0.001) return;
    if (t < S.callCoolUntil) { fx({ k: 'tagUI', t0: t, x: BTN.call[0] - 40, y: BTN.call[1] - 150, txt: `あと ${Math.ceil(S.callCoolUntil - t)}秒`, size: 36, dur: 1.4 }); ev(t, 'wait'); return; }
    if (t - S.callLast > RULE.cool) S.callN = 0;          // 7秒 あけたら 数え直し
    S.callN++;
    kind = kind || ['come', 'turn', 'amae'][Math.floor(rnd() * 3) % 3];
    S.mode = 'call'; S.callKind = kind; BR.careHold = true; S.holdUntil = Infinity; ev(t, 'call', { kind });
    fx({ k: 'notes', t0: t });
    if (BR.stand) { BR.reacts = []; callArrive(t + 0.1); return; }       // 幻の馬・神様馬：正面の まま（歩かない）
    if (kind === 'turn') {             // 振り向く：その場で 体を こちらへ 向けて（ななめ 前）から 顔を こちらへ
      if (BR.mode === 'walk') BR.mode = 'idle';
      const want = Math.cos(BR.dir) >= 0 ? 0.6 : Math.PI - 0.6;
      if (Math.abs(angDiff(BR.dir, want)) > 0.25) { S.route = []; S.turnAfter = true; S.turnTarget = want; S.phase = 'approach'; BR.hurry = HURRY; }
      else callArrive(t + 0.1);
    } else approach(t);
  }
  function callArrive(t) {
    S.phase = 'callact'; BR.mode = 'idle'; BR.until = Math.max(BR.until, t + 6);
    const side = sideToward(BR.x, BR.y + 200);
    if (BR.stand) {                    // 幻の馬・神様馬：正面の まま（近づく → 首を 下げて 顔を よせる・振り向く → よそ見から こちらへ・甘える → すりすり）
      if (S.callKind === 'come') { at(t, tt => { react('nod', 1.8, tt); react('happy', 2.2, tt); ev(tt, 'nod'); tagW(P('poll'), 'ぶるるっ', tt + 0.2, { off: [60, -60] }); }); S.holdUntil = t + 2.6; }
      else if (S.callKind === 'turn') { at(t, tt => { BR.want.look = [0.75, 0.05]; }); at(t + 0.9, tt => { BR.want.look = [0, 0.28]; ev(tt, 'turn'); tagW(P('poll'), '！', tt + 0.4, { off: [60, -60], size: 44 }); }); S.holdUntil = t + 3.6; }
      else { at(t, tt => { react('nuzzle', 3.4, tt, { side: 1 }); react('happy', 3.4, tt); ev(tt, 'amae'); tagW(P('poll'), 'すりすり', tt + 0.4, { off: [70, -60], dur: 2.0 }); });
        for (let k = 0; k < 4; k++) at(t + 0.5 + k * 0.62, tt => { const p = P('poll'); if (p) fx({ k: 'mini', t0: tt, w: [p[0] + (hash(tt * 3) - 0.5) * 90, p[1] - 10], r: 22, dx: (hash(tt * 7) - 0.5) * 60 }); ev(tt, 'heartpop'); });
        S.holdUntil = t + 4.0; }
      return;
    }
    if (S.callKind === 'come') {       // 近づいて くる：着いたら ぶるるっと うなずく
      at(t + 0.05, tt => { react('nod', 1.6, tt); react('swish', 2.0, tt + 0.3); ev(tt, 'nod'); tagW(P('poll'), 'ぶるるっ', tt + 0.2, { off: [30, -90] }); BR.want.look = [side * 0.5, 0.15]; });
      S.holdUntil = t + 2.6;
    } else if (S.callKind === 'turn') {  // 振り向く：首を こちらへ ぐっと 向けて 見つめる
      at(t, tt => { BR.want.look = [side * 1.0, 0.32]; ev(tt, 'turn'); });
      at(t + 0.7, tt => { tagW(P('poll'), '！', tt, { off: [20, -96], size: 44 }); react('swish', 1.8, tt); });
      S.holdUntil = t + 3.4;
    } else {                           // 甘える：近くで 頭を すりすり・ハートが ぽわっ
      at(t + 0.05, tt => { react('nuzzle', 3.4, tt, { side }); react('happy', 3.4, tt); BR.want.look = [side * 0.55, 0.05]; ev(tt, 'amae'); tagW(P('poll'), 'すりすり', tt + 0.4, { off: [30, -96], dur: 2.0 }); });
      for (let k = 0; k < 4; k++) at(t + 0.5 + k * 0.62, tt => { const p = P('poll'); if (p) fx({ k: 'mini', t0: tt, w: [p[0] + (hash(tt * 3) - 0.5) * 60, p[1] - 20], r: 22, dx: (hash(tt * 7) - 0.5) * 60 }); ev(tt, 'heartpop'); });
      S.holdUntil = t + 4.0;
    }
  }

  // ---------- 撫でる ----------
  function startSession(t, x, y, z) {
    S.ses = { t0: t, n: 0, dist: 0, zone: z.zone, down: false, last: [x, y], upT: null };
    S.hand = { t0: t, hideT: null };
    ev(t, 'unfold');
    if (O.tod === 'morning' && !S.greeted) { S.greeted = true; at(t + 0.35, tt => { react('nod', 1.5, tt); ev(tt, 'nod'); }); }      // 朝：元気に うなずく
  }
  function stroke(t, x, y) {
    S.ses.n++; S.petIdle = t; ev(t, 'rub', { n: S.ses.n });
    fx({ k: 'mini', t0: t, w: [x + (hash(t * 7) - 0.5) * 24, y - 14], r: 19, dx: (hash(t * 3) - 0.5) * 40 });
    if (S.ses.n >= RULE.strokes) complete(t, x, y);
  }
  function cutReacts(t) {               // つづけて 撫でた：前の 反応を すっと 止める（tc_horse.js の pose が 0.25秒で 弱める）
    for (const r of (BR.reacts || [])) if (r.cut == null && r.k !== 'look' && r.k !== 'deep' && t < r.t0 + r.dur) r.cut = Math.max(t, r.t0);
  }
  function complete(t, x, y) {
    const z = S.ses.zone, side = sideToward(x, y), slow = O.tod === 'evening' ? 1.35 : 1;
    const ZR = { head: ['nuzzle', 2.6, 'すりすり'], neck: ['swish', 2.4, 'ふりふり'], back: ['stretch', 4.6, 'ぐーっ'], nose: ['sneeze', 1.5, 'ぷしゅっ'] };
    let [rk, rd, rt] = ZR[z] || ZR.neck;
    const rare = S.demo && S.demo.rare != null ? S.demo.rare : rnd() < 1 / 20;
    if (rare) { rk = 'tilt'; rd = 1.9; rt = '？'; }
    rd *= slow;
    const gen = ++S.petGen, live = fn => tt => { if (S.petGen === gen) fn(tt); };      // 次に 撫でたら、この 回の あとの 動きは とり消す
    cutReacts(t);
    S.got = S.got.filter(q => t - q < 60);
    const getHeart = S.got.length < RULE.perMin, willLot = getHeart && S.heart + 1 >= RULE.max;      // この 回で ハートが 10こ → 抽選（ぴょん／ごろん）
    at(t + 0.25, live(tt => {
      react(rk, rd, tt, { side }); ev(tt, rk);
      const hp = rk === 'sneeze' ? P('nose') : rk === 'swish' ? P('rump') : rk === 'stretch' ? P('withers') : P('poll');
      tagW(hp || [x, y], rt, tt, { off: rk === 'swish' ? [-40, -60] : [26, -96], dur: 1.5 * slow });
      if (rk === 'sneeze' && hp) fx({ k: 'bits', t0: tt + 0.62, w: hp.slice() });
    }));
    let end = t + 0.25 + rd;
    if (!willLot) {                      // 抽選の ときは あとの 動き（ゆったり・はしゃぐ・あくび → ねむる）を 出さない：ごろん／ぴょんと 重ならない
      if (O.tod === 'evening') { at(end - 0.6, live(tt => { react('calm', 3.6, tt, { side }); ev(tt, 'calm'); tagW(P('poll'), 'ふぅ〜', tt + 0.4, { off: [36, -90], size: 34, dur: 2.0, rot: 0.06 }); })); end += 3.0; }
      if (O.stageNo <= 2) { at(end - 0.3, live(tt => { react('frisk', 2.2, tt, { side }); ev(tt, 'frisk'); tagW(P('poll'), 'るんっ', tt + 0.2, { off: [30, -96], dur: 1.4, rot: -0.08 }); })); end += 1.9; }
      if (O.tod === 'night') {
        at(end - 0.4, live(tt => { react('yawn', 2.0, tt); ev(tt, 'yawn'); tagW(P('poll'), 'ふわぁ…', tt + 0.3, { off: [36, -96], size: 34, dur: 1.8, rot: 0.05 }); }));
        at(end + 1.7, live(tt => { Object.assign(BR, { mode: 'sleep', until: tt + 600, sleepT: tt, sl: 0, rise: 0, doze: 0, lieDoneT: 0, lieDur: null, flop: null }); ev(tt, 'lie'); }));
        end += 3.6;
      }
    }
    // なかよしハート（1分に 5こまで）
    if (!getHeart) { at(t + 0.5, tt => { fx({ k: 'note', t0: tt, txt: 'ハートは 1分に 5こまで', dur: 2.6 }); ev(tt, 'nope'); }); }
    else {
      S.got.push(t); const i = Math.min(S.heart, RULE.max - 1), q = toS([x, y - 24]);
      fx({ k: 'fly', t0: t + 0.15, x: q[0], y: q[1], i, dur: 0.8 }); ev(t + 0.15, 'heart');
      S.heart = Math.min(RULE.max, S.heart + 1);
      at(t + 0.95, tt => { S.heartShow = Math.max(S.heartShow, i + 1); ev(tt, 'slot', { n: i + 1 }); fx({ k: 'pop', t0: tt, x: SLOT(i)[0], y: SLOT(i)[1] }); });
      if (S.heart >= RULE.max) { S.busy = true; at(Math.max(t + 1.45, end - 0.15), lottery); }      // 抽選は 反応が おわって から（前は 1.45秒後＝のび などの 途中で ためる・横に なる が 重なった）
    }
    // つづけて 5回まで → 7秒 できない（7秒 あけたら 数え直し）
    if (t - S.petLast > RULE.cool) S.petN = 0;
    S.petN++; S.petLast = t;
    if (S.petN >= RULE.streak) { S.petN = 0; S.coolUntil = t + RULE.cool; S.coolFrom = t; S.readyT = S.coolUntil; }
    S.hand.hideT = t + 0.55; at(t + 0.55, tt => ev(tt, 'fold'));
    S.holdUntil = end + 0.5; S.ses.done = true;
  }
  // なかよしハート 10こ：1/66 の 抽選（当たり：ぴょん ＋ お世話 5回 解放／ハズレ：ごろん）
  function lottery(t) {
    const win = S.demo && S.demo.win != null ? S.demo.win : rnd() < RULE.win;
    S.lot = { t0: t, win }; ev(t, 'max'); S.holdUntil = Infinity; S.petGen++; cutReacts(t);
    at(t + 0.9, tt => { react('gather', 1.0, tt); ev(tt, 'gather'); });
    if (win) {
      at(t + 1.7, tt => { react('hop', 2.4, tt); for (let k = 0; k < 2; k++) ev(tt + 0.1 + 1.12 * k, 'frisk', { n: k }); fx({ k: 'burst', t0: tt + 0.35, w: (P('withers') || [BR.x, BR.y - 200]).slice() }); });      // ぴょん → 足を バタバタ（11/09 14:36）
      at(t + 4.1, tt => { fx({ k: 'unlock', t0: tt, dur: 2.6 }); ev(tt, 'unlock'); });
      // 第4.140版（バグ直し）：当たりの ＋5 は 20こを こえても 足す（前は 20こで 切って いた ので、16こ 以上 持って いると「＋5」と 出るのに 5つ ふえなかった・20こ なら 1つも ふえなかった）。10分ごとに たまる のは 20こ まで（tc_app.js の accrue）
      at(t + 4.6, tt => { S.stockBump = tt; S.stock = S.stock + RULE.unlock; fx({ k: 'plus', t0: tt, txt: '+' + RULE.unlock }); ev(tt, 'stock'); });
      at(t + 2.6, tt => { S.drainT = tt; });
      at(t + 6.6, tt => { S.busy = false; S.lot = null; S.holdUntil = tt + 0.3; });
    } else {
      at(t + 1.7, tt => { Object.assign(BR, { mode: 'sleep', until: tt + 2.4 + 2.1 + 1.7, sleepT: tt, sl: 0, rise: 0, doze: 0, lieDoneT: 0, lieDur: 2.4, flop: tt }); ev(tt, 'flop'); });
      at(t + 3.9, tt => { tagW(P('withers') || [BR.x, BR.y], 'ごろん', tt, { off: [20, -110], size: 40, dur: 2.0, rot: -0.06 }); ev(tt, 'goron'); });
      at(t + 3.3, tt => { S.drainT = tt; });
      at(t + 8.1, tt => { S.busy = false; S.lot = null; S.holdUntil = tt + 0.2; });
    }
  }
  // さわる（x,y：フィールドの px）
  function input(kind, x, y, t) {
    if (S.phase === 'beg' && kind === 'down' && zoneAt(x, y)) { begPet(t); S.finger = [x, y]; S.begHand = t; return; }
    if (S.mode === 'clean' && S.phase === 'clean') {         // ほうきで はく（ほうきを うんち・落ち葉の 上で ちりとりの 方へ なぞる）
      const C = S.clean; S.finger = [x, y];
      if (kind === 'down') { C.down = true; C.last = [x, y]; C.dist = 0; }
      else if (kind === 'move' && C.down) { const dx = x - C.last[0], dy = y - C.last[1]; C.last = [x, y]; const toward = (C.pan.x - C.x) >= 0 ? dx : -dx; if (toward > 0) C.dist += toward * S.zoom.z; if (C.dist >= 70 && !C.counted) { C.counted = true; sweep(t); } }
      else if (kind === 'up') { C.down = false; C.counted = false; C.dist = 0; }
      return;
    }
    if (kind === 'down') {
      if (S.ses && !S.ses.done) { S.ses.down = true; S.ses.last = [x, y]; S.ses.dist = 0; S.ses.counted = false; S.ses.sdir = null; S.finger = [x, y]; return; }
      if (S.phase !== 'pet' || S.busy) return;
      if (t < S.coolUntil) {              // 5回 撫でた あとの 7秒
        if (zoneAt(x, y) && t - (S.coolTagT || -9) > 1.2) { S.coolTagT = t; fx({ k: 'tagUI', t0: t, x: BTN.pet[0] + 40, y: BTN.pet[1] - 150, txt: `あと ${Math.ceil(S.coolUntil - t)}秒`, size: 36, dur: 1.4 }); ev(t, 'wait'); }
        return;
      }
      const z = zoneAt(x, y); if (!z) return;
      startSession(t, x, y, z); S.ses.down = true; S.finger = [x, y]; S.petIdle = t;
    } else if (kind === 'move') {
      S.finger = [x, y]; const s = S.ses; if (!s || s.done || !s.down) return;
      const dx = x - s.last[0], dy = y - s.last[1], d = Math.hypot(dx, dy); s.last = [x, y]; if (d < 0.01) return;
      // 1回の なでる：押して なぞった 長さ（画面の 長さ）が strokeLen を こえたら 1回（指を はなすか 向きを 反対に するまで 次は 数えない）
      if (s.sdir && (dx * s.sdir[0] + dy * s.sdir[1]) / d < -0.3) { s.dist = 0; s.counted = false; }
      s.sdir = [dx / d, dy / d];
      const z = zoneAt(x, y); if (z) { s.dist += d * S.zoom.z; s.zone = z.zone; }
      if (s.dist >= RULE.strokeLen && !s.counted) { s.counted = true; stroke(t, x, y); }
    } else if (kind === 'up') { if (S.ses) { S.ses.down = false; S.ses.upT = t; S.ses.dist = 0; S.ses.counted = false; S.ses.sdir = null; } }
  }

  // ---------- 見本（決まった 指の 動き）----------
  //   体の 場所は 目印から（馬が 動いても その 場所を なでる）。指の 時間は「撫でられる ように なった 時（R）」から
  const SPOT = {
    neckA: () => mixP(P('poll'), P('withers'), 0.3), neckB: () => mixP(P('poll'), P('withers'), 0.74),
    headA: () => mixP(P('poll'), P('eye'), 0.1), headB: () => mixP(P('eye'), P('nose'), 0.45),
    backA: () => mixP(P('withers'), P('rump'), 0.12), backB: () => mixP(P('withers'), P('rump'), 0.66),
    noseA: () => mixP(P('eye'), P('nose'), 0.3), noseB: () => mixP(P('eye'), P('nose'), 1.0),
    awayR: () => { const n = P('nose'), b = P('withers'); return toW(n && b && n[0] > b[0] ? [W * 0.2, H * 0.8] : [W * 0.8, H * 0.8]); },     // 顔と 反対の 下から 手が 来る
    brA: () => { const C = S.clean; if (!C) return null; const p = cleanTgPos(), d = C.x >= C.pan.x ? 1 : -1; return [p[0] + 150 * d, p[1] + 4]; },      // ほうき：うんちの 外がわ → ちりとりの 方へ
    brB: () => { const C = S.clean; if (!C) return null; const p = cleanTgPos(), d = C.x >= C.pan.x ? 1 : -1; return [p[0] + 14 * d, p[1] + 4]; },
  };
  // [開始, 終わり, から, まで, 押して いるか]（時間は R から）
  function strokes(u0, A, B, n, ds, dr) {
    ds = ds || 0.6; dr = dr || 0.34; const out = []; let u = u0;
    for (let i = 0; i < n; i++) { out.push([u, u + ds, A, B, true]); u += ds; if (i < n - 1) { out.push([u, u + dr, B, A, false]); u += dr; } }
    return out;
  }
  const PET3 = (A, B, ds, dr, u0) => { u0 = u0 || 0.25; const st = strokes(u0 + 0.7, A, B, 3, ds || 0.58, dr || 0.33), e = st[st.length - 1][1]; return [[u0, u0 + 0.7, 'awayR', A, false], ...st, [e + 0.1, e + 1.0, B, 'awayR', false]]; };
  const DEMOS = {
    // ① 撫でる の 流れ・④ 朝（ボタン → 手前へ → ズーム → 撫でる → もどる → 7秒）
    pet_a: { press: [[1.0, 'pet'], ['Z+1.4', 'pet']], cap: [[0.2, 'A+0.3', '「撫でる」を押すと 手前に 来るよ'], ['A+0.3', 'R+3.0', '近くで ズーム → 指で なぞってね'], ['R+3.0', 'Z-0.2', '3回 なでると なかよしハート +1'], ['Z-0.2', 'Z+4.4', 'つづけて 5回まで → 5回 なでたら 7秒 おやすみ']],
      path: [[0.25, 0.95, 'awayR', 'neckA', false], [0.95, 2.3, 'neckA', 'neckA', true], ...strokes(2.3, 'neckA', 'neckB', 3, 0.6, 0.34), [4.3, 5.3, 'neckB', 'awayR', false]], greeted: false, end: 'Z+4.6' },
    // ② 体の 場所（はじめから 手前・ズーム）
    pet_b: { front: 1, heart: 1, got: [-20], greeted: true, cap: [[0.2, 'R+5.6', '頭を なでると → すりすり']], path: PET3('headA', 'headB', 0.55, 0.32), end: 'R+5.8' },
    pet_d: { front: 1, heart: 2, got: [-25, -14], greeted: true, cap: [[0.2, 'R+8.0', '背中を なでると → ぐーっと のび']], path: PET3('backA', 'backB', 0.6, 0.34), end: 'R+8.2' },
    pet_e: { front: 1, heart: 3, got: [-30, -20, -10], greeted: true, cap: [[0.2, 'R+5.0', '鼻を なでると → ぷしゅっ']], path: PET3('noseA', 'noseB', 0.5, 0.3), end: 'R+5.2' },
    // ハートは 1分に 5こまで
    pet_f: { front: 1, heart: 5, got: [-50, -41, -30, -19, -8], greeted: true, cap: [[0.2, 'R+6.0', 'ハートは 1分に 5こまで']], path: PET3('neckA', 'neckB'), end: 'R+6.2' },
    // なかよしハート 10こ → 抽選
    pet_g: { front: 1, heart: 9, got: [], greeted: true, win: false, cap: [[0.2, 'R+3.4', 'ハートが 10こに なると…'], ['R+3.4', 'R+13.0', '抽選（1/66）→ ハズレは ごろん']], path: PET3('neckA', 'neckB'), end: 'R+13.2' },
    pet_h: { front: 1, heart: 9, got: [], greeted: true, win: true, cap: [[0.2, 'R+3.4', 'ハートが 10こに なると…'], ['R+3.4', 'R+11.2', '当たり → ぴょん！ お世話 5回 解放']], path: PET3('neckA', 'neckB'), end: 'R+11.4' },
    // ④ 時間帯・⑤ 育ち・たまに
    pet_i: { front: 1, heart: 2, got: [-30, -15], greeted: true, cap: [[0.2, 'R+9.6', '夕方は ゆったり よりかかる']], path: PET3('neckA', 'neckB', 0.7, 0.4), end: 'R+9.8' },
    pet_j: { front: 1, heart: 3, got: [-30, -15], greeted: true, cap: [[0.2, 'R+13.0', '夜は あくびを して ねむる']], path: PET3('neckA', 'neckB', 0.7, 0.4), end: 'R+13.2' },
    pet_k: { front: 1, heart: 2, got: [-30, -15], greeted: true, cap: [[0.2, 'R+7.2', '小さい ころは はしゃぐ']], path: PET3('neckA', 'neckB', 0.5, 0.3), end: 'R+7.4' },
    pet_l: { front: 1, heart: 2, got: [-30, -15], greeted: true, rare: true, cap: [[0.2, 'R+5.4', 'たまに（1/20）首を かしげる']], path: PET3('headA', 'headB', 0.55, 0.32), end: 'R+5.6' },
    // 呼ぶ
    call_a: { press: [[0.9, 'call', 'come']], cap: [[0.2, 'Z+0.4', '呼ぶ：近づいて くる']], end: 'Z+0.6' },
    call_b: { press: [[0.9, 'call', 'turn']], cap: [[0.2, 'Z+0.4', '呼ぶ：振り向く']], end: 'Z+0.6' },
    call_c: { press: [[0.9, 'call', 'amae']], cap: [[0.2, 'Z+0.4', '呼ぶ：甘える']], end: 'Z+0.6' },
    // ごはん（エサ・リンゴ・ニンジン）
    feed_a: { press: [[0.8, 'feed'], [2.3, 'pick', 'esa']], pt: null, beg: false, cap: [[0.2, 2.7, 'ごはん：エサ・リンゴ・ニンジンから えらぶ'], [2.7, 'Z-0.2', 'エサ → バケツから もぐもぐ（3回で からっぽ）']], end: 'Z+0.6' },
    feed_b: { press: [[0.6, 'feed'], [1.9, 'pick', 'apple']], pt: 100, beg: false, cap: [[0.2, 'F+0.2', 'リンゴ・ニンジン → 手から 3口'], ['F+0.2', 'F+3.8', 'シャクッ・シャクッ・シャクッ'], ['F+3.8', 'Z+0.1', '今日の 好物だと 大よろこび'], ['Z+0.1', 'Z+2.4', '当たり → ピロン']], end: 'Z+2.5' },
    feed_c: { heart: 2, got: [], press: [[0.6, 'feed'], [1.9, 'pick', 'carrot']], gold: true, pt: null, beg: true, pathBase: 'B', path: [[0.7, 1.3, 'awayR', 'headA', false], [1.3, 1.45, 'headA', 'headA', true], [1.45, 2.2, 'headA', 'awayR', false]],
      cap: [[0.2, 'F+0.4', 'ニンジンは 1/30で 金のニンジン'], ['F+0.4', 'B-0.2', '金のニンジン → なかよし +3'], ['B-0.2', 'Z+0.2', 'おかわりの目 → なでると まんぞく']], end: 'Z+0.6' },
    feed_d: { press: [[0.6, 'feed'], [1.9, 'pick', 'carrot']], gold: false, pt: null, beg: false, cap: [[0.2, 'F+0.2', 'ニンジン → 手から 3口'], ['F+0.2', 'Z+0.2', '先から シャクッ・シャクッ・シャクッ']], end: 'Z+0.6' },
    ban_k: { rt: [6.4, 6.7], cap: [], end: 10.6 },          // 神様馬の フィールド：降臨の バナー → 当選で ルーレット → 消える → もどる
    ban_m: { rt: [6.4, 6.7], cap: [], end: 10.6 },
    // おそうじ
    clean_a: { poop: [770, 1240, 0], nibble: true, pt: null, press: [[0.8, 'clean']], pathBase: 'C', path: [[0.15, 0.6, 'brA', 'brA', false], ...strokes(0.6, 'brA', 'brB', 3, 0.5, 0.36)],
      cap: [[0.2, 'C+0.5', 'おそうじ：うんちを ほうきで はく'], ['C+0.5', 'C+3.5', '3回 はくと ちりとりへ（ときどき かじられる）'], ['C+3.5', 'Z2+0.2', 'きれいに なると くんくん しに 来る']], end: 'Z2+0.4' },
    clean_b: { pt: 200, month: 11, press: [[0.8, 'clean']], pathBase: 'C', path: [[0.15, 0.6, 'brA', 'brA', false], ...strokes(0.6, 'brA', 'brB', 3, 0.5, 0.36)],
      cap: [[0.2, 'C+3.8', 'うんちが ない 時は 落ち葉（季節で かわる）'], ['C+3.8', 'Z+0.1', 'きれい！'], ['Z+0.1', 'Z+2.4', '当たり → ピロン']], end: 'Z+2.5' },
    guide: { press: [[0.8, 'help']], guideEnd: 15.8, cap: [], end: 16.8 },
    clean_c: { poop: [700, 1250, 2, true], pt: null, press: [[0.8, 'clean']], pathBase: 'C', path: [[0.15, 0.6, 'brA', 'brA', false], ...strokes(0.6, 'brA', 'brB', 3, 0.5, 0.36)],
      cap: [[0.2, 'C+3.4', '金のうんち（うんちの 1/20）'], ['C+3.4', 'Z2+0.2', '運がついた！ 高確ゾーン（お世話 5回）']], end: 'Z2+0.4' },
  };
  function tu(v) {                     // 見本の 時間：数（はじめから）か 'R+1.2'（撫でられる ように なって から）・'A'（着いた）・'Z'（もとに もどった）
    if (typeof v === 'number') return v;
    const m = /^([A-Z][0-9]?)([+-][\d.]+)?$/.exec(v); const b = S.marks[m[1]]; return b == null ? Infinity : b + Number(m[2] || 0);
  }
  function demoFinger(u) {             // → { p, down }（その 時の 指：フィールドの px）
    const D = S.demo, R = S.marks[D.pathBase || 'R']; if (R == null || !D.path) return null; const v = u - R; let cur = null;
    for (const sg of D.path) if (v >= sg[0]) cur = sg;
    if (!cur) return null;
    const [u0, u1, A, B, down] = cur, k = clamp((v - u0) / (u1 - u0), 0, 1);
    if (v > u1 + 0.5) return null;                                       // 道の おわりから 少し たったら 指は もう 動かさない
    if (A === B) { if (cur.hold == null) cur.hold = SPOT[A](); return cur.hold ? { p: cur.hold.slice(), down: down && v < u1 } : null; }      // じっと さわる（指は 動かさない）
    const a = SPOT[A](), b = SPOT[B](); if (!a || !b) return null;
    const e = down ? easeIO(k) : easeOut(k), p = mixP(a, b, e);
    if (!down && k > 0 && k < 1) p[1] -= 22 / S.zoom.z * Math.sin(Math.PI * k);      // 指を 浮かせて もどる
    return { p, down: down && v < u1 };
  }

  // ---------- ごはん・おそうじの 絵（折り紙ふう・画面の px で 描く）----------
  // ---------- 3D の バケツ・エサ（まさちゃんの 3D：11/09 14:13「これエサとバケツの3Dモデル！これでやって！」）----------
  //   馬の 体の 座標（x 前・y 上・z 横・地面 0）に 置いて 馬と いっしょに 描く（tc_horse.js の st.props）→ 顔が 手前の ふちに かくれて、奥の かべの 前に 見える
  //   ・口（ふちの 上）の 高さ＝食べはじめの 鼻 と 目の 間（下から B3.rimK）：鼻先が 少し 入る（13:35 まさちゃん）
  //   ・エサ（金の 山）は もぐもぐの たびに 鼻と いっしょに 下がって ひらたく なる → 顔が だんだん バケツの 中へ（14:02 まさちゃん）
  const B3 = { yaw: 0.31, rimK: 0.25, feedR: 0.88, feedH: 0.62, inner: [[1.0, 0.43], [1.2, 0.46], [1.4, 0.5], [1.6, 0.53], [1.8, 0.55], [2.0, 0.52], [2.15, 0.48]] };      // バケツの 内がわの 半径（物の 単位：高さ 2.15）
  function innerR(yp) { const T = B3.inner; if (yp <= T[0][0]) return T[0][1]; for (let i = 1; i < T.length; i++) if (yp <= T[i][0]) { const [y0, r0] = T[i - 1], [y1, r1] = T[i]; return lerp(r0, r1, (yp - y0) / (y1 - y0)); } return T[T.length - 1][1]; }
  function place3(n0, e0, p0, n1, ds) {
    if (!n0 || !e0 || !p0 || !n1) return null;
    const R = n0[1] + B3.rimK * (e0[1] - n0[1]);
    return { cx: n0[0] * 0.86 + p0[0] * 0.14, cz: n0[2] * 0.86 + p0[2] * 0.14, R, sB: R / 2.15, top0: n0[1] + 0.012, top1: n1[1] + 0.012, ds };
  }
  function props3(t) {
    const F = S.feed, b = F && F.bucket, q = F && F.b3; if (!b || !q || !PROPS) return null;
    const op = b.hideT != null ? 1 - sm((t - b.hideT) / 0.45) : backOut((t - b.t0) / 0.45); if (op <= 0.01) return null;
    const M = TCHorse.M, ox = 0.86 + 0.14 * clamp(op, 0, 1.2), oy = Math.max(0.02, op);
    const mB = M.mul(M.tr(q.cx, 0, q.cz), M.mul(M.ry(B3.yaw), M.sc(q.sB * ox, q.sB * oy, q.sB * ox)));
    const out = [{ P: PROPS.bucket, m: mB, sh: [q.cx, q.cz, 0.8 * q.sB * ox, 0.8 * clamp(op, 0, 1)] }];
    if (PROPS.feed) {
      const d = q.ds.reduce((a, s) => a + sm((t - s) / 0.45), 0) / q.ds.length;          // 0〜1：エサが 減った わりあい（馬の 首と 同じ 時刻）
      const top = lerp(q.top0, q.top1, d) * oy, rf0 = B3.feedR * innerR(1.75) * q.sB;      // エサの 山の 半径（バケツの 上の 方の 内がわに 合わせる）
      const hf = B3.feedH * rf0 * (1 - 0.6 * d) * oy, base = top - hf, rf = Math.min(rf0, B3.feedR * innerR(base / q.sB) * q.sB) * ox;
      out.push({ P: PROPS.feed, m: M.mul(M.tr(q.cx, base, q.cz), M.mul(M.ry(0.7), M.sc(rf / 2.65, hf / 2.15, rf / 2.65))) });
    }
    return out;
  }
  async function loadProps() {          // tc_items/tc_prop_*.json＋bin＋絵（まさちゃんの 3D から 作った もの：リポジトリに 入れない）
    if (!HO || !HO.gl || typeof TCHorse === 'undefined' || !TCHorse.createProp) return null;
    const one = async nm => {
      const meta = await fetch(AP(`tc_items/${nm}.json`)).then(r => { if (!r.ok) throw new Error(nm); return r.json(); });
      const bin = TCHorse.unz(await fetch(AP(`tc_items/${meta.bin || nm + '.bin'}`)).then(r => { if (!r.ok) throw new Error(nm); return r.arrayBuffer(); }));
      const im = f => f ? new Promise(ok => { const i = new Image(); i.onload = () => ok(i); i.onerror = () => ok(null); i.src = AP(`tc_items/${f}`); }) : Promise.resolve(null);
      const [texImg, nrmImg] = await Promise.all([im(meta.tex), im(meta.ntex)]);
      return TCHorse.createProp(HO.gl, meta, bin, { texImg, nrmImg });
    };
    try { const [b3, f3] = await Promise.all([one('tc_prop_bucket'), one('tc_prop_feed').catch(() => null)]); return { bucket: b3, feed: f3 }; } catch (e) { return null; }
  }
  function bucketArt(x, y, k, level, op, legH) {      // x,y：足もと（画面）・k：px／体の 高さ 1・level：0〜3・op：0〜1 ひらく・legH：台の 足の 長さ（体の 高さ 1 に 対して・ふつう 0.3）
    if (op <= 0.01) return;
    g.save(); g.translate(x, y); g.scale(1, op); g.lineWidth = 0.8;
    const sw = 0.5 * k, lh = (legH != null ? legH : 0.3) * k, bh = 0.42 * k, tw = 0.5 * k, bw = 0.38 * k;
    g.fillStyle = 'rgba(40,20,5,0.22)'; g.beginPath(); g.ellipse(0, 0, sw * 0.62, sw * 0.16, 0, 0, TAU); g.fill();
    for (const sx of [-1, 1]) { pf([[sx * sw * 0.36 - 4, -lh], [sx * sw * 0.36 + 4, -lh], [sx * sw * 0.42 + 4, 0], [sx * sw * 0.42 - 4, 0]], sx < 0 ? '#9c6a3c' : '#7e5330'); }      // 台の 足
    pf([[-sw / 2, -lh - 0.06 * k], [sw / 2, -lh - 0.06 * k], [sw / 2, -lh], [-sw / 2, -lh]], '#b98552'); pf([[-sw / 2, -lh], [sw / 2, -lh], [sw / 2, -lh + 6], [-sw / 2, -lh + 6]], '#8e6238');      // 台
    const y0 = -lh - 0.06 * k, y1 = y0 - bh;
    pf([[-bw / 2, y0], [0, y0], [0, y1], [-tw / 2, y1]], '#d49a5c'); pf([[0, y0], [bw / 2, y0], [tw / 2, y1], [0, y1]], '#b9793f');      // バケツ（左は 光・右は かげ）
    for (const f of [0.2, 0.75]) { const yy = lerp(y0, y1, f), hw = lerp(bw, tw, f) / 2; pf([[-hw - 1, yy - 4], [hw + 1, yy - 4], [hw + 1, yy + 4], [-hw - 1, yy + 4]], '#8d8f96'); pf([[0, yy - 4], [hw + 1, yy - 4], [hw + 1, yy + 4], [0, yy + 4]], '#6f7178'); }
    g.lineWidth = 1.2; for (let q = -2; q <= 2; q++) line([q * bw / 6, y0], [q * tw / 6, y1], 'rgba(90,50,20,0.25)');
    g.fillStyle = '#7a4a22'; g.beginPath(); g.ellipse(0, y1, tw / 2, tw * 0.16, 0, 0, TAU); g.fill();       // 口
    if (level > 0) {                                   // エサ（えん麦：小さな 金色の 紙）
      const hh = [0, 0.05, 0.1, 0.16][level] * k;
      g.fillStyle = '#e2b858'; g.beginPath(); g.ellipse(0, y1 - hh * 0.3, tw * 0.44, tw * 0.13, 0, 0, TAU); g.fill();
      pf([[-tw * 0.4, y1], [-tw * 0.15, y1 - hh], [tw * 0.12, y1 - hh * 0.8], [tw * 0.4, y1]], '#f0cf73'); pf([[tw * 0.12, y1 - hh * 0.8], [tw * 0.4, y1], [0, y1 + 2]], '#d6aa4a');
      for (let i = 0; i < 9; i++) { const gx = (hash(i * 3.3) - 0.5) * tw * 0.7, gy = y1 - hh * (0.2 + 0.6 * hash(i * 7.7)); pf([[gx - 4, gy], [gx, gy - 3], [gx + 4, gy], [gx, gy + 3]], i % 2 ? '#fff0b8' : '#c99a3c'); }
    }
    g.restore();
  }
  const APPLE_C = typeof document !== 'undefined' ? document.createElement('canvas') : null;
  function appleArt(x, y, r, bites, a, flip) {         // まさちゃんの りんごの 絵に かじった あと（右から・flip で 左から：かじった ふちは 白っぽい 実の 色）
    if (!apple || !apple.naturalWidth || a <= 0.01) return;
    const w = r * 2, h = w * apple.naturalHeight / apple.naturalWidth, c = APPLE_C; c.width = Math.ceil(w) + 4; c.height = Math.ceil(h) + 4; const q = c.getContext('2d');
    q.clearRect(0, 0, c.width, c.height); q.drawImage(apple, 2, 2, w, h);
    const nb = Math.min(3, bites | 0);
    if (nb > 0) {
      const B = [[1.0, 0.45, 0.13], [0.98, 0.66, 0.15], [0.86, 0.56, 0.19]];          // 体の 右の ふち（体は 横 0.03〜0.95・縦 0.22〜0.97）
      q.globalCompositeOperation = 'source-atop'; q.fillStyle = '#fff2d6';
      for (let i = 0; i < nb; i++) { const [bx, by, br] = B[i]; polyP(q, 2 + w * bx, 2 + h * by, w * (br + 0.035), 11, i * 0.8); q.fill(); }
      q.globalCompositeOperation = 'destination-out'; q.fillStyle = '#000';
      for (let i = 0; i < nb; i++) { const [bx, by, br] = B[i]; polyP(q, 2 + w * bx, 2 + h * by, w * br, 11, i * 0.8); q.fill(); }
      q.globalCompositeOperation = 'source-over';
    }
    g.save(); g.globalAlpha *= a; g.translate(x, y); if (flip) g.scale(-1, 1); g.drawImage(c, -w / 2 - 2, -h / 2 - 2); g.restore();
  }
  // ニンジン（まさちゃんの 絵・金は その絵を 金色に した 絵）：先から かじる（かじった ふちは 明るい 実の 色・歯の あとの 角ばった 丸）
  const CAR = { tip: [8.8, 498.9], u: [0.6852, -0.7283], len: 411.5, wp: [3.6, 26.2, 48.1, 68.6, 84.9, 102.6, 120.2, 133.7, 141.6, 129.4, 31.9] };     // 絵の 中の 先・向き（先 → 根もと）・体の 長さ・はば（先から 0〜1）
  const carW = f => { const i = clamp(f, 0, 0.9999) * 10, k = Math.floor(i); return lerp(CAR.wp[k], CAR.wp[k + 1], i - k); };
  const CAR_C = {};
  function carrotCanvas(bites, gold) {
    const im = gold ? carrotG : carrot; if (!im || !im.naturalWidth) return null;
    const nb = Math.min(3, bites | 0), key = (gold ? 'g' : 'n') + nb; if (CAR_C[key]) return CAR_C[key];
    const c = document.createElement('canvas'); c.width = im.naturalWidth; c.height = im.naturalHeight; const q = c.getContext('2d'); q.drawImage(im, 0, 0);
    if (nb > 0) {
      const [ux, uy] = CAR.u, nx = -uy, ny = ux, dc = CAR.len * 0.27 * nb, w = carW(dc / CAR.len), rim = 9;
      const cut = (o, grow) => {           // 先の 方を けす 形：半分の 平面 ＋ 歯の あとの 丸 3つ
        const bx = CAR.tip[0] + ux * (dc + o), by = CAR.tip[1] + uy * (dc + o);
        q.beginPath(); q.moveTo(bx + nx * 500, by + ny * 500); q.lineTo(bx + nx * 500 - ux * 1200, by + ny * 500 - uy * 1200); q.lineTo(bx - nx * 500 - ux * 1200, by - ny * 500 - uy * 1200); q.lineTo(bx - nx * 500, by - ny * 500); q.closePath(); q.fill();
        for (let j = -1; j <= 1; j++) { polyP(q, bx + nx * j * w * 0.32 + ux * w * 0.02, by + ny * j * w * 0.32 + uy * w * 0.02, w * 0.24 + grow, 9, j * 0.7 + nb); q.fill(); }
      };
      q.globalCompositeOperation = 'source-atop'; q.fillStyle = gold ? '#fff0ad' : '#ffc684'; cut(rim, rim * 0.6);
      q.globalCompositeOperation = 'destination-out'; q.fillStyle = '#000'; cut(0, 0);
      q.globalCompositeOperation = 'source-over';
    }
    return (CAR_C[key] = c);
  }
  function carrotHeld(qx, qy, side, L, bites, gold, a) {   // 先（かじった 所）を 口もと（qx,qy）に・根もとは 手の 方（side：馬の 向き）・L：体の 長さ（画面）
    const c = carrotCanvas(bites, gold); if (!c || a <= 0.01) return;
    const nb = Math.min(3, bites | 0), dc = CAR.len * 0.27 * nb, px = CAR.tip[0] + CAR.u[0] * dc, py = CAR.tip[1] + CAR.u[1] * dc;
    const s = L / CAR.len, th = Math.atan2(-0.27, 0.96) - Math.atan2(CAR.u[1], CAR.u[0]);
    g.save(); g.globalAlpha *= a; g.translate(qx, qy); g.scale(side, 1); g.rotate(th); g.scale(s, s); g.drawImage(c, -px, -py); g.restore();
  }
  function broomArt(x, y, k, rot, a) {                 // ほうき（はく 所＝毛の 先が x,y）
    if (a <= 0.01) return;
    g.save(); g.globalAlpha *= a; g.translate(x, y); g.rotate(rot); g.lineWidth = 0.8;
    const bw = 0.34 * k, bh = 0.26 * k, hl = 0.95 * k;
    g.fillStyle = 'rgba(40,20,5,0.18)'; g.beginPath(); g.ellipse(4, 4, bw * 0.6, 7, 0, 0, TAU); g.fill();
    pf([[-4, -bh - hl], [4, -bh - hl], [5, -bh], [-5, -bh]], '#b07a46'); pf([[0, -bh - hl], [4, -bh - hl], [5, -bh], [0, -bh]], '#8c5c32');       // 柄
    pf([[-bw * 0.32, -bh], [bw * 0.32, -bh], [bw / 2, 0], [-bw / 2, 0]], '#f2cd62'); pf([[0, -bh], [bw * 0.32, -bh], [bw / 2, 0], [0, 0]], '#d9ad43');      // 毛
    pf([[-bw * 0.34, -bh - 6], [bw * 0.34, -bh - 6], [bw * 0.33, -bh + 6], [-bw * 0.33, -bh + 6]], '#d9534f');       // しばり
    g.lineWidth = 1.6; for (let q = -3; q <= 3; q++) line([q * bw * 0.08, -bh + 8], [q * bw * 0.14, -2], 'rgba(120,80,20,0.35)');
    g.restore();
  }
  function panArt(x, y, k, dirX, a, fold) {            // ちりとり（口が dirX の 向き）・fold：0〜1 たたむ
    if (a <= 0.01 || fold >= 0.999) return;
    g.save(); g.globalAlpha *= a; g.translate(x, y); g.scale(dirX * (1 - fold), 1 - 0.3 * fold); g.lineWidth = 0.8;
    const w = 0.42 * k, d = 0.18 * k, hw = 0.2 * k;
    g.fillStyle = 'rgba(40,20,5,0.2)'; g.beginPath(); g.ellipse(0, 4, w * 0.62, 9, 0, 0, TAU); g.fill();
    pf([[-w * 0.1, -hw * 0.5], [w * 0.5, -d * 0.4], [w * 0.5, d * 0.4], [-w * 0.1, hw * 0.5]], '#7ec3d9');     // 底
    pf([[-w * 0.5, -hw], [-w * 0.1, -hw * 0.5], [-w * 0.1, hw * 0.5], [-w * 0.5, hw * 0.2]], '#5aa7c4');     // うしろの かべ
    pf([[-w * 0.5, -hw], [-w * 0.1, -hw * 0.5], [w * 0.5, -d * 0.4], [w * 0.36, -d * 0.62]], '#9bd3e6');
    pf([[-w * 0.5, -hw * 0.3], [-w * 0.95, -hw * 0.75], [-w * 0.95, -hw * 0.55], [-w * 0.5, -hw * 0.1]], '#3f86a6');     // 柄
    g.restore();
  }
  function leafArt(x, y, sz, rot, ss, c, a) {
    if (a <= 0.01) return;
    g.save(); g.globalAlpha *= a; g.translate(x, y); g.rotate(rot); g.lineWidth = 0.6;
    if (ss === 'autumn') {                             // もみじ
      const col = ['#e2552d', '#f08a2a', '#c9402a'][c], R = sz, P5 = [];
      for (let i = 0; i < 10; i++) { const an = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? R * 0.42 : R; P5.push([Math.cos(an) * rr, Math.sin(an) * rr * 0.62]); }
      pf(P5, col); pf([[0, 0], ...P5.slice(0, 6)], tone(col, 1.12)); line([0, 0], [0, R * 0.7], 'rgba(90,30,10,0.4)');
    } else if (ss === 'spring') { const col = ['#ffc0d4', '#ffd7e2', '#f7a8c2'][c]; g.scale(1, 0.62); pf([[0, -sz], [sz * 0.7, -sz * 0.2], [sz * 0.3, sz * 0.7], [0, sz * 0.45], [-sz * 0.3, sz * 0.7], [-sz * 0.7, -sz * 0.2]], col); pf([[0, -sz], [sz * 0.7, -sz * 0.2], [0, sz * 0.45]], tone(col, 1.08)); }
    else if (ss === 'summer') { const col = ['#e8c96a', '#d9b452', '#f2dc8c'][c]; pf([[-sz, -2], [sz, -4], [sz, 1], [-sz, 3]], col); }
    else { g.fillStyle = ['#ffffff', '#f2f6fb', '#e8eef6'][c]; g.beginPath(); g.ellipse(0, 0, sz * 0.8, sz * 0.45, 0, 0, TAU); g.fill(); }
    g.restore();
  }
  function flowerArt(x, y, sz, c, a) {                 // 小さな 紙の 花
    if (a <= 0.01 || sz <= 0.5) return;
    const col = ['#ff9cbc', '#ffd65c', '#ffffff', '#c9a8ff'][c % 4];
    g.save(); g.globalAlpha *= a; g.translate(x, y); g.lineWidth = 0.6;
    pf([[0, 0], [-3, sz * 1.6], [3, sz * 1.6]], '#5fae5a');
    for (let i = 0; i < 5; i++) { const an = -Math.PI / 2 + i * TAU / 5; g.save(); g.rotate(an); pf([[0, 0], [sz * 0.5, -sz * 0.35], [sz, 0], [sz * 0.5, sz * 0.35]], i % 2 ? col : tone(col, 0.92)); g.restore(); }
    g.fillStyle = '#ffcf4a'; g.beginPath(); g.arc(0, 0, sz * 0.28, 0, TAU); g.fill();
    g.restore();
  }
  function poopArt(q, x, y, w, gold, a) {             // うんちの 絵（金は 金色に）
    const im = POOP[q % Math.max(1, POOP.length)]; if (!im || !im.naturalWidth || a <= 0.01) return;
    const h = w * im.naturalHeight / im.naturalWidth;
    g.save(); g.globalAlpha *= a; g.fillStyle = 'rgba(40,20,5,0.2)'; g.beginPath(); g.ellipse(x, y, w * 0.4, w * 0.12, 0, 0, TAU); g.fill();
    if (gold) {
      const c = APPLE_C; c.width = Math.ceil(w) + 2; c.height = Math.ceil(h) + 2; const q2 = c.getContext('2d'); q2.clearRect(0, 0, c.width, c.height); q2.drawImage(im, 1, 1, w, h);
      q2.globalCompositeOperation = 'source-atop'; q2.fillStyle = 'rgba(255,200,60,0.62)'; q2.fillRect(0, 0, c.width, c.height); q2.globalCompositeOperation = 'source-over';
      g.drawImage(c, x - w / 2 - 1, y - h * 0.9 - 1);
    } else g.drawImage(im, x - w / 2, y - h * 0.9, w, h);
    g.restore();
  }
  function cleanTgPos() { const C = S.clean; return [lerp(C.x, C.pan.x + 34, C.progS || 0), C.y]; }
  function drawCare(t) {
    const z = S.zoom.z;
    // 金のうんち（地面に ある 間も きらきら）
    for (const q of (BR.poops || [])) if (q.gold) { const p = toS([q.x, q.y]); for (let i = 0; i < 3; i++) { const v = ((t * 0.6 + i / 3) % 1); star(p[0] + (hash(i * 3) - 0.5) * 60 * z, p[1] - 30 * z - 40 * z * v, 9 * z * Math.sin(Math.PI * v), v * 2, 0.9); } }
    // ごはん
    const F = S.feed;
    if (F && F.bucket) { const b = F.bucket, p = toS([b.x, b.y]), k = TCHorse.scaleAt(HO, b.y) * z, op = b.hideT != null ? 1 - sm((t - b.hideT) / 0.45) : backOut((t - b.t0) / 0.45);
      paperSquare(p[0], p[1] - 0.3 * k, 30 * z * (b.hideT != null ? sm((t - b.hideT - 0.3) / 0.2) * (1 - sm((t - b.hideT - 0.5) / 0.2)) : (1 - sm((t - b.t0 - 0.25) / 0.2))), t, 1);
      if (!F.b3) bucketArt(p[0], p[1], k, b.level, Math.max(0, op), b.lh); }
    if (F && F.handT != null && F.itemW) {
      const q = toS(F.itemW), k = TCHorse.scaleAt(HO, BR.y) * z, uo = (t - F.handT) / 0.5, uc = F.handHide != null ? (t - F.handHide) / 0.5 : -1;
      const open = uc >= 0 ? 1 - sm(uc / 0.6) : backOut((uo - 0.3) / 0.6), a = uc >= 0 ? 1 - sm((uc - 0.4) / 0.4) : 1;
      const n = P('nose'), w2 = P('withers'), side = n && w2 && n[0] > w2[0] ? 1 : -1;
      if (F.kind === 'apple') {         // リンゴ：口もとの 少し 前（かじった あとは 口の 方）
        const ax = q[0] + side * 0.14 * k; hand(ax + side * 0.04 * k, q[1] + 0.16 * k, 62, side * 0.3, 1, a, Math.max(0, open)); appleArt(ax, q[1], 0.2 * k, F.bites, a * sm(uo / 0.6), side > 0);
      } else {                         // ニンジン：先は いつも 口もと（かじると 手で 押しこむ・11:01 まさちゃん「もっと先端を口もとに出るようにして！」）・葉の 方を 手で 持つ
        const L = 0.7 * k, len = L * (1 - 0.27 * Math.min(3, F.bites)), dx = side * 0.96, dy = -0.27, T = [q[0] + dx * len, q[1] + dy * len];
        const Hp = mixP(T, q, 0.3); hand(Hp[0], Hp[1] + 0.13 * k, 62, side * 0.25, 1, a, Math.max(0, open));
        carrotHeld(q[0], q[1], side, L, F.bites, F.gold, a * sm(uo / 0.6));
      }
    }
    // おそうじ
    const C = S.clean;
    if (C) {
      const tgt = (C.swipes || 0) / 3; C.progS = (C.progS || 0) + (tgt - (C.progS || 0)) * 0.18;
      const k = TCHorse.scaleAt(HO, C.y) * z, dirX = C.x >= C.pan.x ? 1 : -1, tp = toS(cleanTgPos()), pp = toS([C.pan.x, C.pan.y]);
      const ft = C.foldT != null ? sm((t - C.foldT) / 0.5) : 0, op = C.toolT != null ? backOut((t - C.toolT) / 0.45) : 0;
      if (C.toolT != null) { paperSquare(pp[0], pp[1] - 20 * z, 26 * z * (1 - sm((t - C.toolT - 0.2) / 0.2)), t, 1); panArt(pp[0], pp[1], k, dirX, Math.max(0, Math.min(1, op)), ft); }
      if (C.tg.type === 'poop' && !(C.inPan && ft > 0.2)) { const w = C.tg.w * TCHorse.scaleAt(HO, C.y) * z * (C.inPan ? 0.7 : 1); poopArt(C.tg.img, tp[0], tp[1] - (C.inPan ? 8 * z : 0), w, C.tg.gold, 1 - ft);
        if (C.tg.gold) for (let i = 0; i < 3; i++) { const v = ((t * 0.6 + i / 3) % 1); star(tp[0] + (hash(i * 3) - 0.5) * 60 * z, tp[1] - 30 * z - 40 * z * v, 9 * z * Math.sin(Math.PI * v), v * 2, 0.9); } }
      if (C.tg.type === 'leaves') for (const L of C.tg.leaves) { const sp = toS([C.x + L.dx, C.y + L.dy]), e = C.progS || 0, x = lerp(sp[0], pp[0] + 30 * z + L.dx * 0.1 * z, e), y = lerp(sp[1], pp[1] - 6 * z + L.dy * 0.08 * z, e); leafArt(x, y, 22 * L.s * z, L.r + e * 2, C.tg.ss, L.c, 1 - ft); }
      if (C.toolT != null && C.foldT == null) { const f = S.finger ? toS(S.finger) : toS([C.x + 150, C.y]); broomArt(f[0], f[1], k, dirX * 0.45 + 0.05 * Math.sin(t * 3), Math.max(0, Math.min(1, op))); }
      else if (C.foldT != null) { const f = S.finger ? toS(S.finger) : toS([C.x + 150, C.y]); broomArt(f[0], f[1], k, dirX * 0.45, 1 - ft); }
    }
  }
  // ピロン（お世話の あとの 当たり：pointpop.html と 同じ 紙の 札・コイン）
  function coinArt(x, y, r) {
    const fc = ['#f6d47e', '#eec86a', '#e2b654', '#d8aa49', '#d3a344', '#dbad4e', '#e8bf5f', '#f2cc72'];
    for (let i = 0; i < 8; i++) { const a0 = -Math.PI / 2 - Math.PI / 8 + i * Math.PI / 4, a1 = a0 + Math.PI / 4; pf([[x, y], [x + Math.cos(a0) * r, y + Math.sin(a0) * r], [x + Math.cos(a1) * r, y + Math.sin(a1) * r]], fc[i]); }
    g.strokeStyle = 'rgba(140,90,30,0.5)'; g.lineWidth = 3; g.beginPath();
    for (let i = 0; i <= 8; i++) { const a = -Math.PI / 2 - Math.PI / 8 + i * Math.PI / 4, px = x + Math.cos(a) * r * 0.74, py = y + Math.sin(a) * r * 0.74; i ? g.lineTo(px, py) : g.moveTo(px, py); }
    g.stroke(); label('P', x, y + 2, r * 1.05, '#fff6dc', '#8a5a1c', 7);
  }
  function pointPop(val, u) {
    const D = 2.0; if (u < 0 || u > D) return;
    const PX = W / 2, PY = 720, a = 1 - sm((u - D + 0.35) / 0.35), rise = 43 * (1 - Math.pow(1 - clamp(u / 1.6, 0, 1), 2)), F = 2.7;
    const n = val >= 300 ? 10 : val >= 200 ? 8 : 6, cols = ['#f2c24f', '#f4a39b', '#a6d58f', '#9cc6ec', '#f6dc8c'];
    for (let i = 0; i < n; i++) { const v = u - 0.04; if (v < 0 || v > 0.85) continue; const th = i * TAU / n + 0.35 + 0.3 * hash(i + val), sp = (120 + 60 * hash(i * 3 + val)) * F;
      const x = PX + Math.cos(th) * (40 * F + sp * v) * 1.25, y = PY - rise + Math.sin(th) * (24 * F + sp * v * 0.7) + 160 * F * v * v;
      g.save(); g.globalAlpha *= a * (1 - sm((v - 0.5) / 0.35)); g.translate(x, y); g.rotate(v * 7 + i); g.scale(F, F); pf([[-6, -4], [6, -4], [0, 6]], cols[i % cols.length]); pf([[0, -4], [6, -4], [0, 6]], 'rgba(0,0,0,0.14)'); g.restore(); }
    const s = backOut(u / 0.3), rot = -0.07 * Math.exp(-u * 6) * Math.cos(u * 18);
    g.save(); g.globalAlpha *= a * sm(u / 0.12); g.translate(PX, PY + 8 * F * (1 - sm(u / 0.3)) - rise); g.rotate(rot); g.scale(s * F, s * F); g.lineWidth = 0.4;
    const w = 182, h = 66, c = 15;
    pf([[-w / 2 + 5, -h / 2 + 7], [w / 2 + 5, -h / 2 + 7], [w / 2 + 5, h / 2 + 7], [-w / 2 + 5, h / 2 + 7]], 'rgba(0,0,0,0.22)');
    pf([[-w / 2, -h / 2], [w / 2 - c, -h / 2], [w / 2, -h / 2 + c], [w / 2, h / 2], [-w / 2, h / 2]], '#fff4d6');
    pf([[-w / 2, 0], [w / 2, 0], [w / 2, h / 2], [-w / 2, h / 2]], '#f7e6bf'); pf([[w / 2 - c, -h / 2], [w / 2, -h / 2 + c], [w / 2 - c, -h / 2 + c]], '#e2c78e');
    g.scale(1 / F, 1 / F); coinArt((-w / 2 + 34) * F, 0, 20 * F);
    label(val + 'P', 22 * F, -10 * F, 30 * F, '#f3b631', '#5b3412', 7 * F); label('GET！', 22 * F, 18 * F, 18 * F, '#fffaf0', '#5b3412', 5 * F);
    g.restore();
  }
  // ごはんの えらぶ 札（エサ・リンゴ・ニンジン：今日の 好物に ハート）
  function drawChooser(t) {
    const C = S.chooser; if (!C) return;
    const items = [['esa', 'エサ'], ['apple', 'リンゴ'], ['carrot', 'ニンジン']];
    items.forEach(([kd, txt], i) => {
      const v = (t - C.t0 - i * 0.07) / 0.35; if (v <= 0) return;
      const picked = C.pick === kd, gone = C.pick && !picked, pv = C.pickT != null ? (t - C.pickT) / 0.45 : 0;
      const x = 270 + i * 256, y = 1262, s = backOut(v) * (picked ? 1 + 0.12 * Math.sin(Math.PI * clamp(pv, 0, 1)) : 1) * (gone ? 1 - sm(pv) : 1), a = gone ? 1 - sm(pv) : picked ? 1 - sm((pv - 0.7) / 0.3) : 1;
      if (s <= 0.01 || a <= 0.01) return;
      g.save(); g.globalAlpha *= a; g.translate(x, y); g.scale(s, s);
      panel(-108, -120, 216, 230, 22);
      if (picked) { g.strokeStyle = '#f2b63c'; g.lineWidth = 7; g.strokeRect(-104, -116, 208, 222); }
      if (kd === 'esa') { if (bucket && bucket.naturalWidth) g.drawImage(bucket, -64, -72, 128, 128 * bucket.naturalHeight / bucket.naturalWidth); else bucketArt(0, 52, 230, 3, 1); } else if (kd === 'apple') appleArt(0, -10, 56, 0, 1); else if (carrot && carrot.naturalWidth) g.drawImage(carrot, -58, -76, 116, 116 * carrot.naturalHeight / carrot.naturalWidth);
      label(txt, 0, 84, 34, '#7a4520');
      if (kd === S.fav) { heart(80, -96, 22, 0.1, 1); label('好物', 60, -60, 24, '#c2456f', '#fff8ec', 6); }
      g.restore();
    });
    const v = (t - C.t0) / 0.3; if (v > 0 && !C.pick) { g.save(); g.globalAlpha *= sm(v); g.font = `700 34px ${FONT}`; const w = g.measureText('どれを あげる？').width + 50; g.fillStyle = 'rgba(40,24,10,0.6)'; g.beginPath(); g.roundRect(W / 2 - w / 2, 1080, w, 58, 29); g.fill(); label('どれを あげる？', W / 2, 1110, 34, '#fff8ea'); g.restore(); }
  }

  // ---------- 1コマ ----------
  function pre(t, dt) {
    if (S.t0 == null) S.t0 = t;
    const u = t - S.t0;
    if (S.demo && S.demo.rt) { const R = S.demo.rt; if (u >= R[0] && !R.a) { R.a = 1; S.rtReq = true; } if (u >= R[1] && !R.b) { R.b = 1; S.rtReq = false; } }
    bannerStep(t);
    // ズーム
    if (S.zB) {
      const k = easeIO((t - S.zT0) / S.zDur); S.zoom = { z: lerp(S.zA.z, S.zB.z, k), cx: lerp(S.zA.cx, S.zB.cx, k), cy: lerp(S.zA.cy, S.zB.cy, k) };
      if (k >= 1) { S.zB = null;
        if (S.phase === 'zoomin') { if (S.mode === 'feed') feedStart(t); else if (S.mode === 'clean') cleanStart(t); else { S.phase = 'pet'; S.petIdle = t; mark('R', t); ev(t, 'ready2'); } }
        else if (S.phase === 'zoomout') release(t); }
    }
    // 見本：ボタン・指
    if (S.demo) {
      for (const pr of (S.demo.press || [])) if (!pr.done && u >= tu(pr[0])) { pr.done = true; if (pr[1] === 'help') { S.press.help = t; S.guide = { t0: t }; ev(t, 'button'); ev(t + 0.1, 'paper'); } else if (pr[1] === 'pet') pressPet(t); else if (pr[1] === 'feed') pressFeed(t); else if (pr[1] === 'pick') pick(t, pr[2]); else if (pr[1] === 'clean') pressClean(t); else pressCall(t, pr[2]); }
      const f = demoFinger(u), was = S.fdown || false;
      if (f) {
        if (f.down && !was) input('down', f.p[0], f.p[1], t); else if (f.down) input('move', f.p[0], f.p[1], t); else if (was) input('up', f.p[0], f.p[1], t);
        else S.finger = f.p;
        S.fdown = f.down;
      }
      if (S.demo.end && u >= tu(S.demo.end)) S.demoDone = true;
      if (S.guide && typeof TCGuide !== 'undefined') {          // 説明書：下から すっと 出て → ゆっくり 下へ → とじる
        const D = S.demo, gu = t - S.guide.t0, end = (D.guideEnd || 16) - 0.6;
        if (!TCGuide.el) TCGuide.open(g.canvas.parentNode);
        TCGuide.set(gu < end ? sm(gu / 0.45) : 1 - sm((gu - end) / 0.4)); TCGuide.scroll(sm((gu - 1.6) / (end - 3.2)));
        if (gu >= end + 0.4 && !S.guide.closed) { S.guide.closed = true; ev(t, 'paper'); }
      }
    }
    S.sched.sort((a, b) => a.t - b.t);
    while (S.sched.length && S.sched[0].t <= t) S.sched.shift().fn(t);
    if (BR.careHold && !S.grazeOK) BR.want.graze = 0;          // お世話の 間は 草を 食べない（ごはんの 時だけ）
    // 手前へ 歩いて いる：着いたら 次の 道・ぜんぶ 着いたら ズーム（撫でる）か 呼ぶの 動き
    if (S.phase === 'approach' && BR.mode === 'walk' && S.route && S.route.length && BR.tgt && Math.hypot(BR.x - BR.tgt[0], (BR.y - BR.tgt[1]) / 0.5) < 80) nextLeg(t);      // 止まらずに 次の 道へ
    if (S.phase === 'approach' && BR.mode === 'idle') {
      if (S.route && S.route.length) nextLeg(t);
      else if (S.turnAfter) {           // 横向きに なる（右に 進んで 来たら 右向き・少しだけ こちらへ）
        S.turnAfter = false; const want = S.turnTarget != null ? S.turnTarget : Math.cos(BR.dir) >= 0 ? 0.12 : Math.PI - 0.12; S.turnTarget = null;
        Object.assign(BR, { mode: 'turn', turnTo: want, until: t + 30 });
      } else arrived(t);
    }
    // 撫でて いる 間は 手の 方（人の 方）を 見る
    if (S.ses && !S.ses.done && S.finger) {
      const side = sideToward(S.finger[0], S.finger[1]), zone = S.ses.zone, mag = zone === 'head' || zone === 'nose' ? 0.35 : 0.85;
      BR.want.look = [side * mag, zone === 'back' ? 0.05 : 0.12];
    }
    if (S.ses && S.ses.done && S.hand && S.hand.hideT != null && t > S.hand.hideT + 0.7) { S.ses = null; S.hand = null; }
    if (S.ses && !S.ses.done && !S.ses.down && S.ses.upT != null && t - S.ses.upT > 2.2) { S.hand.hideT = t; ev(t, 'fold'); S.ses.done = true; S.holdUntil = t + 0.8; }      // とちゅうで やめた
    // おしまい：撫でる（反応が 終わった・6秒 さわらない）・呼ぶ（動きが 終わった）
    if (!S.busy && t > S.holdUntil && (S.phase === 'pet' && !S.ses || S.phase === 'callact' || S.phase === 'feeddone' || S.phase === 'cleandone')) { S.holdUntil = Infinity; endCare(t); }
    if (S.afterSniff && BR.mode === 'idle') { S.afterSniff = false; BR.hurry = 1; react('sniff', 2.2, t, { side: 0 }); react('swish', 2.2, t + 1.2); ev(t, 'sniff'); tagW(P('nose'), 'くんくん', t + 0.3, { off: [0, -100], size: 32, dur: 1.4 }); S.holdUntil = t + 2.6; }
    if (S.mode === 'after' && !S.afterSniff && t > S.holdUntil) { S.mode = null; S.phase = 'idle'; BR.careHold = false; BR.until = t + 2; mark('Z2', t); }
    if (S.phase === 'pet' && !S.ses && !S.busy && S.holdUntil === Infinity && t - S.petIdle > 6) endCare(t);
    if (S.readyT != null && t >= S.readyT) { ev(S.readyT, 'ready'); S.readyT = null; S.readyPop = t; }
    if (S.drainT != null && t > S.drainT + RULE.max * 0.07 + 0.2) { S.heart = 0; S.heartShow = 0; S.drainT = null; }
    S.stockShow += clamp(S.stock - S.stockShow, -dt * 6, dt * 6);
    const pp = props3(t); if (pp) BR.props = pp; else if (BR.props) BR.props = null;      // 3D の バケツ・エサ（馬と いっしょに 描く）
  }
  function post(t) {
    const cs = S.cs || O.cs || 1; g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, g.canvas.width, g.canvas.height); g.setTransform(cs, 0, 0, cs, 0, 0);      // S.cs：アプリ（画面の 大きさが かわった とき）
    g.lineJoin = 'round'; g.lineCap = 'round';
    drawBanner(t);
    drawCare(t);
    drawUI(t);
    drawVInfo(t);
    drawChooser(t);
    // 手（画面の 上で いつも 同じ 大きさ）
    if (S.hand) {
      const hs = S.hand, f = toS(S.finger || [W / 2, H / 2]);
      const uo = (t - hs.t0) / 0.5, uc = hs.hideT != null ? (t - hs.hideT) / 0.5 : -1;
      let open = uc >= 0 ? 1 - sm(uc / 0.6) : backOut((uo - 0.38) / 0.62), sq = uc >= 0 ? sm((uc - 0.35) / 0.25) * (1 - sm((uc - 0.7) / 0.3)) : (1 - sm((uo - 0.45) / 0.3)) * backOut(uo / 0.4);
      if (uo < 0.38) open = 0;
      const press = S.ses && S.ses.down && !S.ses.done ? 1 : 0;
      hs.press = (hs.press == null ? 0 : hs.press) + (press - (hs.press || 0)) * 0.3;
      const n = P('nose'), b = P('withers'), rot = (n && b && n[0] > b[0] ? 0.5 : -0.5) + 0.06 * Math.sin(t * 1.3);      // 顔と 反対の 下から 手が 来る（顔に かからない）
      paperSquare(f[0] + 20 * Math.sign(-rot), f[1] + 32, 34 * sq, 0.8 * (1 - sq) + t * 0.5, Math.min(1, sq * 2));
      hand(f[0], f[1], 62 * (O.handK || 1), rot, hs.press, 1, Math.max(0, open));
    }
    if (S.begHand != null && t - S.begHand < 1.1) { const f = toS(S.finger || [W / 2, H / 2]), u2 = (t - S.begHand) / 1.1; hand(f[0], f[1], 62, -0.4, u2 < 0.5 ? 1 : 0, 1 - sm((u2 - 0.75) / 0.25), backOut(u2 / 0.25)); }
    drawFx(t);
    drawCaption(t);
  }
  // ---------- 降臨の バナー（11/09 12:34 まさちゃん「神様馬フィールドの時に上にバナーとして出して！当選して、ルーレットになったら消して！」）----------
  //   フィールドの 間 ずっと 上に（ゲージ・お世話の 札の すぐ 下）。来た とき：上から ふわっと 落ちて ぽよん ＋ ゆっくり きらきら
  //   ルーレットに なったら 上へ すっと 消える（ルーレットの 絵にも 降臨の 帯が ある ので 2つ 出さない）→ ルーレットが おわったら また 出る
  async function special(kind) {        // kind：'kamisama'・'maboroshi'・null（ふつうの フィールドに もどる）
    if (!kind) { if (S.ban) S.ban.hideT = S.lastT || 0; return; }
    BANNER = new Image(); BANNER.src = AP(`tc_items/tc_banner_${kind}.webp`); try { await BANNER.decode(); } catch (e) { }
    S.ban = { kind, showT: null, hideT: null, shown: false };
  }
  function roulette(on) { S.rtReq = !!on; }      // アプリ：ルーレットが 始まる・おわる
  function setHorse(horse, brain) { HO = horse; BR = brain; S.phase = 'idle'; S.mode = null; S.ses = null; S.hand = null; S.feed = null; S.clean = null; S.chooser = null; S.zoom = { z: 1, cx: W / 2, cy: H / 2 }; S.zB = null; }
  // アプリ：画面を 押した（フィールドの px・ズーム前の 画面の 座標）。ボタン・えらぶ 札・説明書の「？」は ここ、馬（なでる・ほうき）は input へ
  function uiHit(x, y) {
    if (S.chooser && !S.chooser.pick) { const items = ['esa', 'apple', 'carrot']; for (let i = 0; i < 3; i++) { const cx = 270 + i * 256; if (Math.abs(x - cx) < 110 && y > 1262 - 122 && y < 1262 + 112) return 'pick:' + items[i]; } }
    if (Math.hypot(x - HELP[0], y - HELP[1]) < 48) return 'help';
    for (const k of ['pet', 'feed', 'clean', 'call']) if (Math.hypot(x - BTN[k][0], y - BTN[k][1]) < BTN_R + 10) return k;
    return null;
  }
  function press(t, what) {
    if (what === 'pet') pressPet(t); else if (what === 'feed') pressFeed(t); else if (what === 'clean') pressClean(t); else if (what === 'call') pressCall(t);
    else if (what === 'help') { S.press.help = t; ev(t, 'button'); ev(t + 0.05, 'paper'); if (O.onHelp) O.onHelp(); }
    else if (what && what.startsWith('pick:')) pick(t, what.slice(5));
  }
  function pointer(kind, x, y, t) {        // アプリの 指（画面の 座標）
    if (kind === 'down') { const h = uiHit(x, y); S.uiDown = h; if (h) return; }
    if (kind === 'up' && S.uiDown) { const h = uiHit(x, y); if (h === S.uiDown) press(t, h); S.uiDown = null; return; }
    if (S.uiDown) return;
    const w = toW([x, y]); input(kind, w[0], w[1], t);
  }
  function bannerStep(t) {
    const B = S.ban; if (!B) return;
    if (B.showT == null && B.hideT == null) B.showT = t + 0.6;
    if (S.rtReq != null) {
      if (S.rtReq && !S.rtOn) { S.rtOn = true; if (B.hideT == null) { B.hideT = t; ev(t, 'banout'); } }
      else if (!S.rtReq && S.rtOn) { S.rtOn = false; B.showT = t + 0.3; B.hideT = null; B.shown = false; }
      S.rtReq = null;
    }
    if (!B.shown && B.hideT == null && B.showT != null && t >= B.showT) { B.shown = true; ev(t, 'banin', { kind: B.kind }); }
  }
  const BAN_W = 860; let BAN_TOP = 172;      // アプリ：作戦会議の ボタン（右上の お世話の 下：11/09 14:41 まさちゃん）の 下に（O.banTop）
  function bannerVisible() { const B = S.ban; return !!(B && B.hideT == null && B.showT != null); }
  function drawBanner(t) {
    const B = S.ban, im = BANNER; if (!B || !im || !im.naturalWidth || B.showT == null) return;
    const w = BAN_W, h = w * im.naturalHeight / im.naturalWidth, cx = W / 2, cy = BAN_TOP + h / 2, ui = t - B.showT;
    let k, a, dy;
    if (B.hideT != null) { const v = (t - B.hideT) / 0.38; if (v >= 1) return; k = 1 - 0.12 * sm(v); a = 1 - sm(v); dy = -70 * v * v; }
    else { if (ui < 0) return; const v = ui / 0.62; k = 0.72 + 0.28 * backOut(v); a = sm(v / 0.35); dy = -90 * (1 - easeOut(v)); }
    const bob = 4 * Math.sin(TAU * ui / 3.4), sway = 0.007 * Math.sin(TAU * ui / 4.6);
    g.save(); g.globalAlpha *= a; g.translate(cx, cy + dy + bob); g.rotate(sway); g.scale(k, k); g.drawImage(im, -w / 2, -h / 2, w, h); g.restore();
    if (B.hideT == null && ui > 0.25 && ui < 2.4) {                 // 来た ときの きらきら（ゆっくり 1回ずつ・ちかちか しない）
      const col = B.kind === 'kamisama' ? '#fff2bf' : '#f6dcff';
      for (let i = 0; i < 7; i++) { const v = (ui - 0.25 - i * 0.16) / 1.0; if (v > 0 && v < 1) star(cx + (hash(i * 7.3 + 1) - 0.5) * w * 0.92, BAN_TOP + h * (0.1 + 0.8 * hash(i * 3.1 + 2)) + bob, 22 * Math.sin(Math.PI * v), v * 1.4, 0.95, col); }
    }
  }
  // ---------- 切り替わる 条件の 札（第4.144版・11/10 18:04 まさちゃん「幻の馬と神様馬は、上のバナーの下に切り替わる条件を表示して！
  //   ・タイムリミット ・お世話の回数 お世話5回完了後の切り替わりタイマー」）----------
  //   S.vinfo＝{ left：タイムリミットの のこり（秒）, n：お世話の 回数, need：5, timer：切り替わりタイマーの のこり（秒）・まだ 動いて いなければ null }（アプリが 毎コマ 入れる）
  //   場所：はじめは バナーの 下（640×180）→ 18:31「馬と被らないようにもっと上にして！あと、テロップもう少し大きさ小さくして…大きいと背景も分かりにくい！」で 小さく（字 26・29px）
  //   → 18:44「リセット条件バナーの下から左上のハートのトークンの下に表示するようにして！」で、左上の なかよしの 板（26〜626・34〜160）の すぐ 下・左そろえ（420×125）。
  //   バナーと いっしょに 出て いっしょに 消える（ルーレットの 間は 消える）。数字は 1秒ごとに かわる だけ（点めつ しない・ゆれない）。のこり 1分は 赤
  const mmss = v => { const n = Math.max(0, Math.ceil(v)); return Math.floor(n / 60) + ':' + String(n % 60).padStart(2, '0'); };
  const VI = { x: 26, y: 172, w: 420, row: 37, pad: 7, lab: 26, val: 29, small: 22 };
  function vinfoRows(V) {
    return [['タイムリミット', mmss(V.left), V.left <= 60, VI.val],
      ['お世話', `${V.n}/${V.need}回`, false, VI.val],
      ['切り替わりタイマー', V.timer == null ? `${V.need}回で スタート` : mmss(V.timer), V.timer != null && V.timer <= 60, V.timer == null ? VI.small : VI.val]];
  }
  function vinfoRect() { return { x: VI.x, y: VI.y, w: VI.w, h: 3 * VI.row + 2 * VI.pad }; }
  function drawVInfo(t) {
    const B = S.ban, V = S.vinfo; if (!B || !V || B.showT == null) return;
    const ui = t - B.showT; let a;
    if (B.hideT != null) { const v = (t - B.hideT) / 0.3; if (v >= 1) return; a = 1 - sm(v); } else { if (ui < 0.5) return; a = sm((ui - 0.5) / 0.35); }
    const { x, y, w, h } = vinfoRect();
    g.save(); g.globalAlpha *= a; panel(x, y, w, h, 16);
    vinfoRows(V).forEach(([lb, val, hot, size], i) => {
      const cy = y + VI.pad + VI.row * (i + 0.5) + 2;
      label(lb, x + 22, cy, VI.lab, '#7a4520', null, 0, 'left'); label(val, x + w - 22, cy, size, hot ? '#d0342c' : '#c2456f', null, 0, 'right');
      if (i < 2) { g.save(); g.strokeStyle = 'rgba(122,69,32,0.28)'; g.lineWidth = 2; g.setLineDash([7, 7]); g.beginPath(); g.moveTo(x + 18, y + VI.pad + VI.row * (i + 1)); g.lineTo(x + w - 18, y + VI.pad + VI.row * (i + 1)); g.stroke(); g.restore(); }
    });
    g.restore();
  }
  function drawCaption(t) {
    if (!S.demo || !S.demo.cap) return; const u = t - S.t0;
    for (const [a0, b0, txt] of S.demo.cap) {
      const a = tu(a0), b = tu(b0); if (a === Infinity) continue;
      const k = sm((u - a) / 0.25) * (b === Infinity ? 1 : 1 - sm((u - b + 0.25) / 0.25)); if (k <= 0) continue;
      g.save(); g.globalAlpha *= k; g.font = `700 40px ${FONT}`; const w = g.measureText(txt).width + 64;
      const cy0 = bannerVisible() ? BAN_TOP + 262 : 186;      // 降臨の バナーが ある ときは その 下
      g.fillStyle = 'rgba(40,24,10,0.6)'; g.beginPath(); g.roundRect(W / 2 - w / 2, cy0, w, 74, 37); g.fill();
      label(txt, W / 2, cy0 + 38, 40, '#fff8ea'); g.restore();
    }
  }
  function drawUI(t) {
    // なかよしゲージ（左上）
    const gx = 26, gy = 34, gw = 600, gh = 126;
    panel(gx, gy, gw, gh, 24);
    const pulse = S.lot ? 1 + 0.06 * Math.sin(TAU * 0.9 * (t - S.lot.t0)) * (1 - sm((t - S.lot.t0 - 2.2) / 0.6)) : 1;
    heart(gx + 62, gy + gh / 2 + 4, 36 * pulse, -0.06, 1);
    label('なかよし', gx + 128, gy + 36, 32, '#7a4520', null, 0, 'left');
    label(`${S.heartShow}/10`, gx + gw - 30, gy + 36, 32, '#c2456f', null, 0, 'right');
    const dr = S.drainT != null ? t - S.drainT : -1;
    for (let i = 0; i < RULE.max; i++) {
      const [x, y] = SLOT(i); heartSlot(x, y, 17);
      if (i < S.heartShow) {
        let a = 1, r = 17;
        if (dr >= 0) { const q = (dr - (RULE.max - 1 - i) * 0.07) / 0.25; a = 1 - sm(q); r = 17 * (1 + 0.3 * Math.sin(Math.PI * clamp(q, 0, 1))); }
        if (S.lot && dr < 0) r = 17 * (1 + 0.1 * Math.sin(TAU * 0.9 * (t - S.lot.t0) - i * 0.5));
        heart(x, y, r, 0, a);
      }
    }
    // お世話の ストック（右上）
    const sx = W - 26 - 296, sy = 44, sw = 296, shh = 106; panel(sx, sy, sw, shh, 20);
    const bu = S.stockBump != null ? (t - S.stockBump) / 0.5 : 2, bs = bu < 1 ? 1 + 0.12 * Math.sin(Math.PI * bu) : 1;
    label('お世話', sx + 24, sy + 36, 28, '#7a4520', null, 0, 'left');
    g.save(); g.translate(sx + sw - 118, sy + 70); g.scale(bs, bs); label(String(Math.round(S.stockShow)), 0, 0, 50, '#3f7f3a', '#fff8ec', 6); g.restore();
    label('/20', sx + sw - 54, sy + 76, 28, '#9a7a55');
    // 「−1」と 高確ゾーンの 札は お世話の 板の すぐ 下。アプリでは そこに 作戦会議の ボタン（板の すぐ 下：11/10 10:48 まさちゃん）が 上に のる ので
    //   「−1」は ボタンの 左（O.dropX）・高確ゾーンの 札は ボタンの 下（O.hiY）へ
    if (S.stockDrop != null) { const v = (t - S.stockDrop) / 1.2; if (v < 1) label('−1', O.dropX || sx + sw - 60, sy + shh + 26 + 30 * easeOut(v), 40, '#b0445f', '#fff8ec', 7); }
    if (S.high > 0) {                  // 高確ゾーン（のこり お世話 ○回）
      const hb = S.highBump != null ? (t - S.highBump) / 0.5 : 2, hs = hb < 1 ? 1 + 0.15 * Math.sin(Math.PI * hb) : 1;
      g.save(); g.translate(sx + sw / 2, O.hiY || sy + shh + 44); g.scale(hs, hs); panel(-130, -30, 260, 60, 14); label(`高確ゾーン あと${S.high}回`, 0, 2, 28, '#c2456f'); g.restore();
    }
    // 説明書の「？」（ゲージと お世話の あいだ）
    { const [hx, hy] = HELP, pq = S.press.help != null ? (t - S.press.help) / 0.35 : 9, ps = pq < 1 ? 1 - 0.1 * Math.sin(Math.PI * pq) : 1;
      g.save(); g.translate(hx, hy); g.scale(ps, ps); g.fillStyle = 'rgba(40,20,5,0.22)'; g.beginPath(); g.arc(3, 5, 40, 0, TAU); g.fill();
      g.fillStyle = '#fff8ec'; g.beginPath(); g.arc(0, 0, 40, 0, TAU); g.fill(); g.strokeStyle = '#e5cfa8'; g.lineWidth = 3; g.beginPath(); g.arc(0, 0, 38.5, 0, TAU); g.stroke();
      label('？', 0, 2, 44, '#8a5a2a'); g.restore(); }
    // 下の ボタン（絵は かり）
    const items = [['pet', '撫でる'], ['feed', 'ごはん'], ['clean', 'おそうじ'], ['call', '呼ぶ']];
    items.forEach(([k, txt]) => {
      const [x, y] = BTN[k], r = BTN_R, pq = S.press[k] != null ? (t - S.press[k]) / 0.35 : 9, ps = pq < 1 ? 1 - 0.1 * Math.sin(Math.PI * pq) : 1;
      g.save(); g.translate(x, y); g.scale(ps, ps); g.translate(-x, -y);
      g.fillStyle = 'rgba(40,20,5,0.22)'; g.beginPath(); g.arc(x + 4, y + 7, r, 0, TAU); g.fill();
      g.fillStyle = '#fff8ec'; g.beginPath(); g.arc(x, y, r, 0, TAU); g.fill(); g.fillStyle = '#f6e8cf'; g.beginPath(); g.arc(x, y, r, 0.15 * Math.PI, 0.85 * Math.PI); g.fill();
      g.strokeStyle = '#e5cfa8'; g.lineWidth = 3; g.beginPath(); g.arc(x, y, r - 1.5, 0, TAU); g.stroke();
      if (k === 'pet') { handPath(); const [hx0, hy0, hx1, hy1] = HAND_BB, s_ = 34, r_ = -0.5, cx_ = (hx0 + hx1) / 2 * s_, cy_ = (hy0 + hy1) / 2 * s_;      // 手の 形の まん中を ボタンの まん中に（11/09 13:21 まさちゃん「撫でるの手を真ん中にして！」）
        hand(x - (Math.cos(r_) * cx_ - Math.sin(r_) * cy_), y - 4 - (Math.sin(r_) * cx_ + Math.cos(r_) * cy_), s_, r_, 1, 1, 1); }
      else if (k === 'feed') { const im_ = bucket && bucket.naturalWidth ? bucket : apple; if (im_ && im_.naturalWidth) { const w_ = 96, h_ = w_ * im_.naturalHeight / im_.naturalWidth; g.drawImage(im_, x - w_ / 2, y - 4 - h_ / 2, w_, h_); } }      // まさちゃんの バケツの 絵（11/09 13:21）
      else if (k === 'clean') { g.save(); g.translate(x, y); g.rotate(0.5); g.lineWidth = 0.8; pf([[-5, -50], [5, -50], [5, 8], [-5, 8]], '#c98d55'); pf([[-24, 8], [24, 8], [32, 42], [-32, 42]], '#f0c75e'); pf([[0, 8], [24, 8], [32, 42], [0, 42]], '#d9ad43'); g.lineWidth = 2; for (let q = -2; q <= 2; q++) line([q * 9, 14], [q * 12, 40], 'rgba(120,80,20,0.35)'); g.restore(); }
      else { g.save(); g.translate(x, y - 4); g.lineWidth = 0.8; pf([[-34, -26], [34, -26], [34, 18], [-6, 18], [-20, 34], [-18, 18], [-34, 18]], '#9fd0f0'); pf([[0, -26], [34, -26], [34, 18], [0, 18]], '#86c0e6'); label('♪', 0, -4, 40, '#ffffff'); g.restore(); }
      if (pq < 1.6) { const q = clamp(pq / 1.6, 0, 1); g.strokeStyle = `rgba(255,248,236,${0.75 * (1 - q)})`; g.lineWidth = 6; g.beginPath(); g.arc(x, y, r + 6 + 30 * easeOut(q), 0, TAU); g.stroke(); }
      g.restore();
      label(txt, x, y + r + 34, 30, '#fff8ea', 'rgba(60,35,15,0.85)', 7);
      // 撫でた あとの 7秒（輪っかが 減って いく）
      if (k === 'pet' && t < S.coolUntil) {
        const rem = (S.coolUntil - t) / RULE.cool;
        g.save(); g.fillStyle = 'rgba(60,40,25,0.45)'; g.beginPath(); g.moveTo(x, y); g.arc(x, y, r, -Math.PI / 2, -Math.PI / 2 + TAU * rem); g.closePath(); g.fill();
        g.strokeStyle = '#ff9cbc'; g.lineWidth = 8; g.beginPath(); g.arc(x, y, r + 8, -Math.PI / 2, -Math.PI / 2 + TAU * rem); g.stroke(); g.restore();
        label(String(Math.ceil(S.coolUntil - t)), x, y + 2, 54, '#ffffff', 'rgba(60,35,15,0.9)', 8);
      }
      if (k === 'call' && t < S.callCoolUntil) {
        const rem = (S.callCoolUntil - t) / RULE.cool;
        g.save(); g.fillStyle = 'rgba(60,40,25,0.45)'; g.beginPath(); g.moveTo(x, y); g.arc(x, y, r, -Math.PI / 2, -Math.PI / 2 + TAU * rem); g.closePath(); g.fill();
        g.strokeStyle = '#8fd0ff'; g.lineWidth = 8; g.beginPath(); g.arc(x, y, r + 8, -Math.PI / 2, -Math.PI / 2 + TAU * rem); g.stroke(); g.restore();
        label(String(Math.ceil(S.callCoolUntil - t)), x, y + 2, 54, '#ffffff', 'rgba(60,35,15,0.9)', 8);
      }
      if (k === 'pet' && S.readyPop != null) { const q = (t - S.readyPop) / 0.6; if (q < 1) { g.save(); g.strokeStyle = `rgba(255,156,188,${0.7 * (1 - q)})`; g.lineWidth = 6; g.beginPath(); g.arc(x, y, r + 8 + 26 * easeOut(q), 0, TAU); g.stroke(); g.restore(); } }
    });
  }
  function drawFx(t) {
    S.fx = S.fx.filter(f => t - f.t0 < (f.dur || 3) + 1.5);
    const z = S.zoom.z;
    for (const f of S.fx) {
      const u = t - f.t0; if (u < 0) continue;
      if (f.k === 'mini') {            // なでた 所の 小さな ハート（体の 所から 画面の 上へ うかぶ）
        const d = 1.0; if (u > d) continue; const k = u / d, q = toS(f.w), s = Math.sqrt(z);
        heart(q[0] + f.dx * s * easeOut(k), q[1] - 70 * s * easeOut(k), f.r * s * backOut(k / 0.3), 0.12 * Math.sin(u * 6), 1 - sm((k - 0.6) / 0.4));
      } else if (f.k === 'fly') {       // なかよしハート：ぽんっと 出て ゲージへ とんで いく
        const d = f.dur, [tx, ty] = SLOT(f.i), k = u / d; if (k > 1) continue;
        const c = [lerp(f.x, tx, 0.5) + 120, Math.min(f.y, ty) - 160], e = easeIO(clamp((k - 0.25) / 0.75, 0, 1));
        const p = [(1 - e) * (1 - e) * f.x + 2 * (1 - e) * e * c[0] + e * e * tx, (1 - e) * (1 - e) * (f.y - 30) + 2 * (1 - e) * e * c[1] + e * e * ty];
        const r = k < 0.25 ? 34 * backOut(k / 0.25) : lerp(34, 17, e);
        heart(p[0], p[1], r, 0.2 * Math.sin(u * 9) * (1 - e), 1);
      } else if (f.k === 'pop') {      // ゲージに 入った：紙の つぶ
        const d = 0.6; if (u > d) continue;
        for (let i = 0; i < 6; i++) { const a = i * TAU / 6 + 0.3, rr = 18 + 30 * easeOut(u / d); star(f.x + Math.cos(a) * rr, f.y + Math.sin(a) * rr, 7 * (1 - u / d), u * 3, 1 - sm((u / d - 0.5) / 0.5), i % 2 ? '#ffb3cb' : '#f5d06a'); }
      } else if (f.k === 'tag') {      // 体の 所の 札（ズームに ついて 動く・大きさは 少しだけ ズームに 合わせる）
        const d = f.dur; if (u > d) continue; const q = toS(f.w), s = Math.sqrt(z), o = f.off || [0, -100], sz = f.size * Math.min(1.25, s);
        g.font = `700 ${sz}px ${FONT}`; const hw = (g.measureText(f.txt).width + sz * 1.0) / 2 + 14;      // 画面の はしで 切れない ように
        tag(clamp(q[0] + o[0] * s, hw, W - hw), Math.max(290, q[1] + o[1] * s - 26 * easeOut(u / d)), f.txt, sz, 1 - sm((u - d + 0.35) / 0.35), backOut(u / 0.28), f.rot, f.col);
      } else if (f.k === 'tagUI') {
        const d = f.dur; if (u > d) continue;
        tag(f.x, f.y - 26 * easeOut(u / d), f.txt, f.size, 1 - sm((u - d + 0.35) / 0.35), backOut(u / 0.28), 0);
      } else if (f.k === 'note') {     // ゲージの 下の お知らせ
        const d = f.dur; if (u > d) continue;
        tag(26 + 300, 34 + 126 + 56, f.txt, 32, 1 - sm((u - d + 0.4) / 0.4), backOut(u / 0.28), 0, '#b0445f');
      } else if (f.k === 'bits') {     // ぷしゅっ：鼻から 紙の 小さな つぶ
        const d = 0.9; if (u > d) continue;
        const L = HO.last, zx = L ? L.V[0] * L.view.W : 1, zy = L ? -L.V[1] * L.view.H : 0, n = Math.hypot(zx, zy) || 1, fxv = zx / n, fyv = zy / n, q = toS(f.w), s = Math.sqrt(z);
        for (let i = 0; i < 7; i++) {
          const a = (hash(i * 5.1) - 0.5) * 1.3, vx = fxv * Math.cos(a) - fyv * Math.sin(a), vy = fxv * Math.sin(a) + fyv * Math.cos(a), sp = (70 + 70 * hash(i * 2.3)) * s;
          const x = q[0] + vx * sp * easeOut(u / d), y = q[1] + vy * sp * easeOut(u / d) + 30 * s * (u / d) * (u / d);
          g.save(); g.globalAlpha *= 1 - sm((u / d - 0.4) / 0.6); g.translate(x, y); g.rotate(u * 6 + i); g.scale(s, s); g.lineWidth = 0.6; pf([[-7, -5], [7, -5], [0, 7]], i % 2 ? '#ffffff' : '#f3e9d8'); g.restore();
        }
      } else if (f.k === 'burst') {    // ぴょん：ハートと 星が ふわっと 広がる
        const d = 1.9; if (u > d) continue; const p = toS(f.w), s = Math.sqrt(z);
        for (let i = 0; i < 12; i++) {
          const a = -Math.PI / 2 + (i - 5.5) * 0.24 + (hash(i) - 0.5) * 0.2, sp = (260 + 120 * hash(i * 3.3)) * s, k = easeOut(u / d);
          const x = p[0] + Math.cos(a) * sp * k, y = p[1] - 40 + Math.sin(a) * sp * k + 120 * (u / d) * (u / d), al = 1 - sm((u / d - 0.55) / 0.45);
          if (i % 3 === 2) star(x, y, 14 * s * backOut(u / 0.3), u * 2 + i, al); else heart(x, y, (i % 2 ? 18 : 24) * s * backOut(u / 0.3), 0.3 * Math.sin(u * 5 + i), al);
        }
      } else if (f.k === 'notes') {    // 呼ぶ：ボタンから 音符が ふわっと 馬の 方へ
        const d = 1.6; if (u > d) continue; const [bx, by] = BTN.call, tg = toS([BR.x, BR.y - 200]);
        for (let i = 0; i < 3; i++) {
          const v = clamp((u - i * 0.18) / (d - 0.4), 0, 1); if (v <= 0) continue; const e = easeOut(v);
          const x = lerp(bx, tg[0], e * 0.55) + 26 * Math.sin(v * 7 + i * 2), y = lerp(by - 70, tg[1], e * 0.55) - 30 * i;
          g.save(); g.globalAlpha *= 1 - sm((v - 0.6) / 0.4); label(i === 1 ? '♫' : '♪', x, y, 54 - i * 6, '#ffffff', 'rgba(60,110,160,0.85)', 7); g.restore();
        }
      } else if (f.k === 'unlock') {   // お世話 5回 解放！（ピロンと 同じ 紙の 札）
        const d = f.dur; if (u > d) continue; unlockTag(u, d);
      } else if (f.k === 'crumbs') {   // かけら（エサ・リンゴ・ニンジン）
        const d = 0.8; if (u > d) continue; const q = toS(f.w), s2 = Math.sqrt(z);
        for (let i = 0; i < 8; i++) { const an = -Math.PI / 2 + (hash(i * 2.3 + f.t0) - 0.5) * 2.6, sp = (60 + 70 * hash(i * 4.1)) * s2, x = q[0] + Math.cos(an) * sp * easeOut(u / d), y = q[1] + Math.sin(an) * sp * easeOut(u / d) + 90 * s2 * (u / d) * (u / d);
          g.save(); g.globalAlpha *= 1 - sm((u / d - 0.5) / 0.5); g.translate(x, y); g.rotate(u * 8 + i); g.scale(s2, s2); g.lineWidth = 0.6; pf([[-5, -4], [5, -4], [0, 5]], f.col[i % f.col.length]); g.restore(); }
      } else if (f.k === 'dust') {     // さっ（はいた ときの ほこり）
        const d = 0.7; if (u > d) continue; const q = toS(f.w), s2 = z;
        for (let i = 0; i < 6; i++) { const x = q[0] - (20 + 60 * hash(i * 1.9)) * s2 * easeOut(u / d), y = q[1] - (6 + 30 * hash(i * 3.7)) * s2 * easeOut(u / d), r = (10 + 10 * hash(i)) * s2 * (0.6 + 0.6 * u / d);
          g.save(); g.globalAlpha *= 0.35 * (1 - u / d); g.fillStyle = '#e8d2a8'; g.beginPath(); g.arc(x, y, r, 0, TAU); g.fill(); g.restore(); }
      } else if (f.k === 'kira') {     // キラッ（きれいに なった：ゆっくり 1回）
        const d = 1.0; if (u > d) continue; const q = toS(f.w);
        for (let i = 0; i < 4; i++) { const v = (u - i * 0.12) / 0.7; if (v <= 0 || v >= 1) continue; star(q[0] + (hash(i * 5.1) - 0.5) * 140 * z, q[1] - (10 + 50 * hash(i * 2.2)) * z, 18 * z * Math.sin(Math.PI * v), v, 0.95, '#fff2bf'); }
      } else if (f.k === 'glint') {    // 金のニンジンの きらきら
        const d = f.dur; if (u > d || !S.feed || !S.feed.itemW) continue; const q = toS(S.feed.itemW);
        for (let i = 0; i < 4; i++) { const v = ((u * 0.8 + i / 4) % 1); star(q[0] + (hash(i * 3.3) - 0.5) * 120 * z, q[1] + (hash(i * 7.1) - 0.5) * 120 * z, 12 * z * Math.sin(Math.PI * v), v * 2, 0.9 * (1 - sm((u - d + 0.4) / 0.4))); }
      } else if (f.k === 'luck') {     // 運がついた！ 高確ゾーン（お世話 5回）
        const d = f.dur; if (u > d) continue; const a = 1 - sm((u - d + 0.4) / 0.4), s2 = backOut(u / 0.3);
        g.save(); g.globalAlpha *= a; g.translate(W / 2, 640); g.scale(s2, s2);
        panel(-300, -110, 600, 220, 40); label('運がついた！', 0, -36, 70, '#f3b631', '#5b3412', 14); label('高確ゾーン（お世話 5回）', 0, 52, 40, '#c2456f', '#fff8ec', 8);
        g.restore();
        for (let i = 0; i < 6; i++) { const v = (u - i * 0.15) / 0.8; if (v > 0 && v < 1) star(W / 2 + (hash(i * 9.1) - 0.5) * 640, 640 + (hash(i * 4.4) - 0.5) * 260, 22 * Math.sin(Math.PI * v), v, a); }
      } else if (f.k === 'pointpop') {
        pointPop(f.v, u);
      } else if (f.k === 'plus') {
        const d = 1.6; if (u > d) continue;
        label(f.txt, W - 26 - 296 + 150, 44 + 140 + 30 - 40 * easeOut(u / d), 44, '#3f7f3a', '#fff8ec', 7);
      }
    }
  }
  function unlockTag(u, d) {
    const PX = W / 2, PY = 640, a = 1 - sm((u - d + 0.35) / 0.35), rise = 40 * (1 - Math.pow(1 - clamp(u / 1.6, 0, 1), 2));
    const s = backOut(u / 0.3), rot = -0.07 * Math.exp(-u * 6) * Math.cos(u * 18);
    for (const [sx, sy, d0] of [[-250, -80, 0.12], [262, 70, 0.24], [-180, 96, 0.36]]) { const v = (u - d0) / 0.6; if (v > 0 && v < 1) star(PX + sx, PY - rise + sy, 24 * Math.sin(Math.PI * v), v * 1.2, a); }
    g.save(); g.globalAlpha *= a * sm(u / 0.12); g.translate(PX, PY + 20 * (1 - sm(u / 0.3)) - rise); g.rotate(rot); g.scale(s, s);
    const w = 560, h = 190, c = 40; g.lineWidth = 0.8;
    pf([[-w / 2 + 12, -h / 2 + 18], [w / 2 + 12, -h / 2 + 18], [w / 2 + 12, h / 2 + 18], [-w / 2 + 12, h / 2 + 18]], 'rgba(0,0,0,0.22)');
    pf([[-w / 2, -h / 2], [w / 2 - c, -h / 2], [w / 2, -h / 2 + c], [w / 2, h / 2], [-w / 2, h / 2]], '#fff4d6');
    pf([[-w / 2, 0], [w / 2, 0], [w / 2, h / 2], [-w / 2, h / 2]], '#f7e6bf');
    pf([[w / 2 - c, -h / 2], [w / 2, -h / 2 + c], [w / 2 - c, -h / 2 + c]], '#e2c78e');
    g.lineWidth = 2.5; line([-w / 2, 0], [w / 2, 0], 'rgba(160,110,50,0.3)');
    heart(-w / 2 + 96, 4, 58, -0.08, 1);
    label('お世話 5回', 54, -30, 72, '#3f8f3a', '#5b3412', 14);
    label('解放！', 54, 48, 56, '#fffaf0', '#5b3412', 12);
    g.restore();
  }

  async function init(o) {
    O = Object.assign({ cs: 1, tod: 'morning', stageNo: 5 }, o); HO = o.horse; BR = o.brain; rnd = o.rnd || Math.random;
    if (O.banTop) BAN_TOP = O.banTop;
    g = o.canvas.getContext('2d'); S.on = true;
    apple = new Image(); apple.src = AP('tc_items/tc_item_apple.webp'); try { await apple.decode(); } catch (e) { }
    bucket = new Image(); bucket.src = AP('tc_items/tc_item_bucket.webp'); try { await bucket.decode(); } catch (e) { }      // まさちゃんの エサの バケツの 絵（11/09 13:21：ごはんの ボタン）
    if (o.props !== false) PROPS = await loadProps();      // まさちゃんの 3D の バケツ・エサ（11/09 14:13）：なければ 紙の 絵の バケツ
    carrot = new Image(); carrot.src = AP('tc_items/tc_item_carrot.webp'); carrotG = new Image(); carrotG.src = AP('tc_items/tc_item_carrot_gold.webp');      // まさちゃんの ニンジンの 絵・それを 金に した 絵（11/09 11:27・11:28）
    try { await Promise.all([carrot.decode(), carrotG.decode()]); } catch (e) { }
    const bk = O.bg === 'divine' ? 'kamisama' : O.bg === 'abyss' ? 'maboroshi' : null;      // 神様馬・幻の馬の フィールド → 上に 降臨の バナー
    if (bk) await special(bk);
    for (const f of ['tc_poop1.webp', 'tc_poop2.webp', 'tc_poop3.webp']) { const im = new Image(); im.src = AP(f); try { await im.decode(); POOP.push(im); } catch (e) { } }
    try { await document.fonts.load(`700 40px ${FONT}`); } catch (e) { }
    if (o.demo && DEMOS[o.demo]) {
      const D = DEMOS[o.demo]; S.demo = D;
      S.heart = S.heartShow = D.heart || 0; S.got = (D.got || []).map(q => q + 1.5); S.greeted = !!D.greeted; S.stock = S.stockShow = D.stock != null ? D.stock : 3;
      if (D.month) O.month = D.month;
      if (D.poop) { const [px, py, im, gold] = D.poop; BR.poops = [{ x: px, y: py, img: im, t0: -10, h0: 1.05, w: [0.3, 0.5, 0.42][im] * (HO.opt.stage || 1), gold: !!gold }]; }
      if (D.front) {                   // はじめから 手前で ズーム して 撫でられる
        const cw = o.canvas.width, ch = o.canvas.height, k = cw / W; TCHorse.draw(HO, BR, 0, { W: cw, H: ch, k, ox: 0, oy: 0 });
        S.zoom = zoomFor(); S.mode = 'pet'; S.phase = 'pet'; BR.careHold = true; S.holdUntil = Infinity; S.marks.R = 0.35; S.marks.A = 0;
      }
    } else if (o.demo === 'free') {         // さわって ためす（ボタンも 押せる）
      const el = o.canvas; el.style.touchAction = 'none';
      const pos = e => { const r = el.getBoundingClientRect(); return [(e.clientX - r.left) * W / r.width, (e.clientY - r.top) * H / r.height]; };
      const hitBtn = q => Object.keys(BTN).find(k => Math.hypot(q[0] - BTN[k][0], q[1] - BTN[k][1]) < BTN_R + 10);
      el.addEventListener('pointerdown', e => { const q = pos(e), b = hitBtn(q); if (b === 'pet') return pressPet(S.lastT || 0); if (b === 'call') return pressCall(S.lastT || 0); const p = toW(q); el.setPointerCapture(e.pointerId); input('down', p[0], p[1], S.lastT || 0); });
      el.addEventListener('pointermove', e => { const p = toW(pos(e)); input('move', p[0], p[1], S.lastT || 0); });
      el.addEventListener('pointerup', e => { const p = toW(pos(e)); input('up', p[0], p[1], S.lastT || 0); });
    }
    window.__events = () => S.ev;
    window.__careDone = () => !!S.demoDone;
  }
  return { init, pre: (t, dt) => { S.lastT = t; pre(t, dt); }, post, input, pointer, press, pressPet, pressCall, get _hb() { return [HO, BR]; }, special, roulette, setHorse, view: () => S.zoom, get on() { return S.on; }, S, DEMOS, RULE, vinfoRows, vinfoBox: () => { const im = BANNER; if (!S.ban || !S.vinfo || !im || !im.naturalWidth || !bannerVisible()) return null; return Object.assign(vinfoRect(), { banTop: BAN_TOP, banH: BAN_W * im.naturalHeight / im.naturalWidth, banW: BAN_W, gauge: [26, 34, 600, 126] }); } };
})();
