// トレーニングセンター（App Store版）：馬の お世話・作戦会議（まさちゃん 2026/11/08〜11/09）
//   index.html の 中の tc_launch.js が 右上（第4.138版：上の 帯の すぐ 下）に 丸い ボタンを 出す → 押すと この ファイル（tc_bundle.js）を 読んで TCApp.open()
//   ・上の 帯：「← もどる」・作戦会議（横長の ボタン）・音
//   ・フィールド（tc_field.js：時間帯・幻の馬／神様馬）＋ 馬（tc_horse.js）＋ お世話の 紙の 絵（tc_care.js）＋ 説明書（tc_guide.js）
//   ・当たり：ポイント（台帳の もらったP）・ルーレット／チケット（tc_fx.js）
//   ・保存：localStorage 'tengel.tc'（この 端末の 中だけ）
const TCApp = (() => {
  const W = 1052, H = 1657;
  const SK = 'tengel.tc';
  const COLORS = ['brown', 'madara', 'black', 'white', 'hada'];
  const COLOR_JA = { brown: 'ブラウン', madara: 'まだら', black: 'ブラック', white: 'ホワイト', hada: '肌色' };
  const BIG = 1.7;                                    // 幻の馬・神様馬：5段階の 馬の 1.7倍（11/09 11:38）
  const TOKEN_MIN = 10, TOKEN_MAX = 20;               // お世話トークン：10分ごとに 1つ・最大 20
  const TICK = 120;                                   // 2分ごとの チャンス（秒・開いて いる 間）：高確ゾーン・うんち（第4.144版から 幻の馬・神様馬の 抽選は しない）
  // 第4.144版（馬の リセットの きまり：11/10 18:04 まさちゃん「馬のリセットは5分に切り替えよう！…トレーニングセンターで最低5回お世話をした段階でリセットタイマーが作動して(お世話をしてる間はリセットなし)5分経ったらリセット。
  //   …トレーニングセンターを開きっぱなしでもお世話の操作をしない限りは馬は変わらないでいて！ただ、幻の馬と神様馬は…トレーニングセンターを開いてから30分経過すると切り替わる仕組みにして！」
  //   ・18:13「幻の馬と神様馬も最低5回お世話完了後はリセットタイマー作動で5分でリセットね！」）：
  //   ・馬が かわる 抽選（幻の馬 1/245・神様馬 1/399・それ 以外は いつもの 馬）は「リセット」の とき だけ。前は 2分ごとに（ひらいて いる だけで）ひいて いた
  //   ・リセット＝お世話（ごはん・おそうじ）を 5回 した あと（5回めが おわった とき）に タイマーが 動いて、5分 たったら。お世話の 途中・当たりの 演出の 途中・作戦会議や 説明書を ひらいて いる 間は 待つ
  //   ・幻の馬・神様馬は、それに 加えて 来てから 30分（タイムリミット）でも 帰る（→ いつもの 馬）。どちらか 早い 方
  //   ・時間は「もどらない 時計」（tnow）と、ひらいて いる 間に たった 秒（el）の どちらか 早い 方で 数える（時計を もどしても 止まらない）
  const RESET_CARES = 5, RESET_MIN = 5;               // 馬の リセット：お世話 5回 → タイマー 5分
  const VISIT_MIN = 30;                               // 幻の馬・神様馬の タイムリミット（来てから・分）
  const HIGH_N = 5, HIGH_X = 4;                       // 高確ゾーン：お世話 5回・当たりやすさ ×4 ※仮
  const P_POOP = 1 / 7, P_GOLD = 1 / 20, P_HIGH = 1 / 50, P_MAB = 1 / 245, P_KAMI = 1 / 399;
  const PRIZES = [                                    // お世話（ごはん・おそうじ）の 抽選：まれな 方から
    // 第4.142版（11/10 17:20 まさちゃん「仕組みは今のままでいい！ただノーマルのルーレット抽選、幻の馬ルーレット当選と神様馬ルーレット抽選の確率だけ変えたい！」）：
    //   ルーレット 800P か 1600P 1/1000 → 1/125・1600P か 3200P 1/2000 → 1/245・3200P か 6400P 1/3600 → 1/399・チケット 1/2400 → 1/600（ポイントの 当たり 6つは そのまま）。
    //   何か 当たる のは 1回 約20.2% → 約21.6%・平均は 1回 約17.0P → 約58.6P。高確ゾーン（×4）でも 合わせて 約87%（1 を こえない：こえると まれな 当たりが 4倍に ならない）
    [1 / 600, { k: 'tk' }], [1 / 399, { k: 'rt', tier: 'kamisama' }], [1 / 245, { k: 'rt', tier: 'maboroshi' }], [1 / 125, { k: 'rt', tier: 'normal' }],
    [1 / 121, { k: 'pt', v: 300 }], [1 / 99, { k: 'pt', v: 200 }], [1 / 85, { k: 'pt', v: 100 }],
    // 第4.140版（11/10 14:14 まさちゃん「足す：10P 1/10・20P 1/20・50P 1/50 これだけ足して！」）：小さい 当たり（ほかは そのまま）。
    //   何か 当たる のは 1回 約3.2% → 約20.2%（5回で 約68%・20回で 約99%）。高確ゾーン（×4）でも 合わせて 約81%（1 を こえない）
    [1 / 50, { k: 'pt', v: 50 }], [1 / 20, { k: 'pt', v: 20 }], [1 / 10, { k: 'pt', v: 10 }]];
  const RT = { normal: [800, 1600], maboroshi: [1600, 3200], kamisama: [3200, 6400] };
  // 幻の馬・神様馬が いる 間の お世話の 抽選（11/09 14:22・14:26 まさちゃん：この表だけ・ルーレットの 絵は その馬の もの）
  //   第4.142版（同じ 17:20 の 指定）：幻の馬 1/300・1/500・1/1000 → 1/15・1/30・1/60／神様馬 1/85・1/99・1/121 → 1/8・1/16・1/32。
  //   何か 当たる のは 幻の馬 約11.7%（平均 1回 240P）・神様馬 約21.9%（平均 1回 約1,313P）。高確ゾーン（×4）でも 約46.7%・87.5%（1 を こえない）
  const PRIZES_VISIT = {
    maboroshi: [[1 / 60, { k: 'rt', tier: 'maboroshi', v: [3200, 6400] }], [1 / 30, { k: 'rt', tier: 'maboroshi', v: [1600, 3200] }], [1 / 15, { k: 'rt', tier: 'maboroshi', v: [800, 1600] }]],
    kamisama: [[1 / 32, { k: 'rt', tier: 'kamisama', v: [10000, 20000] }], [1 / 16, { k: 'rt', tier: 'kamisama', v: [5000, 10000] }], [1 / 8, { k: 'rt', tier: 'kamisama', v: [2000, 4000] }]] };
  const AP = p => String(p).split('/').pop();         // アプリ：Resources に 名前だけ
  window.TC_ASSET = AP;

  // ---------- 保存 ----------
  const DEF = () => ({ v: 1, color: 0, cares: 0, total: 0, stock: 5, stockAt: Date.now(), heart: 0, high: 0, tickets: 0, fav: null, poops: [], visit: null, rs: { n: 0, at: 0, el: 0 }, snd: true, gen: 1 });      // rs＝馬の リセット（n：前の リセットからの お世話の 回数・at：タイマーが 動いた 時刻（0＝まだ）・el：それから ひらいて いた 秒）
  let st = null, dirty = false, saveAt = 0;
  function load() {
    try { const s = JSON.parse(localStorage.getItem(SK) || 'null'); st = Object.assign(DEF(), s && s.v === 1 ? s : {}); } catch (e) { st = DEF(); }
    const r = st.rs; st.rs = r && typeof r === 'object' ? { n: Math.max(0, Math.round(+r.n || 0)), at: Math.max(0, +r.at || 0), el: Math.max(0, +r.el || 0) } : { n: 0, at: 0, el: 0 };
  }
  function save() { dirty = false; try { localStorage.setItem(SK, JSON.stringify(st)); } catch (e) { } }
  const touch = () => { dirty = true; };
  const TKP = () => ((window.TengelPoints && window.TengelPoints.TICKET_POINTS) || 7000).toLocaleString('ja-JP');      // チケット 1枚を かえられる ポイント（points.js）
  const note = m => { try { const t = document.getElementById('toast'); if (t) { t.textContent = m; t.hidden = false; clearTimeout(t._tc); t._tc = setTimeout(() => { t.hidden = true; }, 4200); } } catch (e) { /* なし */ } };      // アプリの 画面の お知らせ（下の 黒い 札）
  function stageOf(c) { return c < 50 ? 1 : c < 100 ? 2 : c < 150 ? 3 : c < 200 ? 4 : 5; }
  function scaleOf(c) { return c < 50 ? 0.6 : c < 100 ? 0.7 : c < 150 ? 0.8 : c < 200 ? 0.88 : c < 250 ? 0.94 : 1.0; }      // ※仮：250回で いちばん 大きく
  function tod(d) { const h = (d || new Date()).getHours(); return h >= 7 && h < 16 ? 'morning' : h >= 16 && h < 19 ? 'evening' : 'night'; }
  function today() { const d = new Date(); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); }
  // 第4.139版（抜け穴を ふさぐ）：端末の 時計を 先へ 進めて お世話トークンを ためる → 時計を もどす、を ふせぐ「もどらない 時計」。
  //   いままでに 見た いちばん 先の 時刻（st.seen）より 前には もどらない。時計を もどした あとは、本当の 時刻が そこへ 追いつくまで トークンは ふえない
  //   （前は トークンが 満タンの ときに 数えはじめの 時刻を いまの 時刻に 書きかえて いた ので、満タンに して から 時計を もどせば すぐ また ためられた）。
  //   ※ 時計を 先へ 進めた ままに する ズルは、端末の 中だけでは 見分けられない（電波で 正しい 時刻を もらう しくみが いる）
  function tnow() {
    const n = Date.now(), s0 = +st.seen || 0;
    if (n > s0) { st.seen = n; if (n > (tnow.saved || 0) + 60000) { tnow.saved = n; touch(); } }
    return Math.max(n, s0);
  }
  function accrue(now) {                              // お世話トークン（閉じて いる 間も 時間で たまる）。now＝tnow()（もどらない 時計）
    if (st.stock >= TOKEN_MAX) { st.stockAt = now; return 0; }
    const n = Math.floor((now - st.stockAt) / (TOKEN_MIN * 60000)); if (n <= 0) return 0;
    const add = Math.min(n, TOKEN_MAX - st.stock); st.stock += add; st.stockAt = st.stock >= TOKEN_MAX ? now : st.stockAt + n * TOKEN_MIN * 60000; touch(); return add;
  }

  // ---------- 音（WebAudio：環境音・BGM は くり返し、効果音は できごとで）----------
  const SND = (() => {
    let ac = null, master = null, bed = null, want = null, on = true;
    const cache = {};
    const AMB = { morning: 'tc_amb_morning.m4a', evening: 'tc_amb_evening.m4a', night: 'tc_amb_night.m4a', abyss: 'tc_bgm_abyss.m4a', divine: 'tc_bgm_divine.m4a' };
    function buf(f) { if (!cache[f]) cache[f] = fetch(AP(f)).then(r => { if (!r.ok) throw new Error('no ' + f); return r.arrayBuffer(); }).then(b => new Promise((ok, ng) => { const q = ac.decodeAudioData(b, ok, ng); if (q && q.catch) q.catch(() => { }); })); return cache[f]; }
    function unlock() { try { if (!ac) { const AC = window.AudioContext || window.webkitAudioContext; if (!AC) return; ac = new AC(); master = ac.createGain(); master.gain.value = on ? 1 : 0; master.connect(ac.destination); } if (ac.state === 'suspended') ac.resume(); } catch (e) { } }
    async function field(name) {
      want = name; if (!ac) return; if (bed && bed.name === name) return;
      const old = bed; bed = null;
      if (old) { try { const n = ac.currentTime; old.g.gain.cancelScheduledValues(n); old.g.gain.setValueAtTime(old.g.gain.value, n); old.g.gain.linearRampToValueAtTime(0, n + 2); old.s.stop(n + 2.1); } catch (e) { } }
      const f = AMB[name]; if (!f) return; let b; try { b = await buf(f); } catch (e) { return; }
      if (want !== name || (bed && bed.name === name)) return;
      const s = ac.createBufferSource(); s.buffer = b; s.loop = true;
      const g = ac.createGain(); g.gain.setValueAtTime(0, ac.currentTime); g.gain.linearRampToValueAtTime(1, ac.currentTime + 2);
      s.connect(g); g.connect(master); s.start(); bed = { s, g, name };
    }
    async function se(name, gain, at) {
      if (!ac || !on) return; let b; try { b = await buf(name); } catch (e) { return; }
      try { const s = ac.createBufferSource(); s.buffer = b; const g = ac.createGain(); g.gain.value = gain == null ? 1 : gain; s.connect(g); g.connect(master); s.start(ac.currentTime + Math.max(0, at || 0)); return s; } catch (e) { }
    }
    function stopAll() { if (bed) { try { bed.s.stop(); } catch (e) { } bed = null; } want = null; if (ac && ac.state === 'running') { try { ac.suspend(); } catch (e) { } } }
    function setOn(v) { on = !!v; if (master) master.gain.value = on ? 1 : 0; }
    function preload(list) { if (!ac) return; list.forEach(f => buf(f).catch(() => { })); }
    return { unlock, field, se, stopAll, setOn, preload, get ac() { return ac; } };
  })();
  // できごと → 効果音（sfx_care.py の parts で 作った tc_se_*.m4a。大きさ・ずれは 作る ときに 入れて ある）
  const SE_VAR = { slot: e => 'slot_' + Math.max(1, Math.min(10, e.n || 1)), bite: e => 'bite_' + (e.kind === 'apple' ? 'apple' : 'carrot'), banin: e => 'banin_' + (e.kind === 'maboroshi' ? 'maboroshi' : 'kamisama') };
  const SE_SKIP = { ready2: 'ready', zoomout: 'zoomin', feedstart: null };
  function onCareEvent(e) {
    if (e.k === 'token') { st.cares += 1; st.total = (st.total || 0) + 1; st.rs.n = (st.rs.n || 0) + 1; touch(); later.push(() => growCheck()); }      // お世話の 回数（total＝ミッションの 合計：馬が リセット されても 減らない）
    let nm = SE_VAR[e.k] ? SE_VAR[e.k](e) : (e.k in SE_SKIP ? SE_SKIP[e.k] : e.k);
    if (!nm) return;
    const lag = Math.max(0, e.t - clock());
    SND.se('tc_se_' + nm + '.m4a', 1, lag);
  }

  // ---------- 画面 ----------
  let ov = null, stage = null, cvGL = null, cvOv = null, cvFx = null, field = null, gl = null, built = false;
  let HO = null, BR = null, horseKey = '', raf = 0, running = false, tBase = 0, lastT = null, lastDraw = 0, nextTick = 0, later = [], busy = false;
  const clock = () => (performance.now() - tBase) / 1000 + 1.5;
  const css = `
#tcOv{position:fixed;inset:0;z-index:90;display:none;flex-direction:column;align-items:center;background:#2a1d12;padding-top:env(safe-area-inset-top);padding-bottom:env(safe-area-inset-bottom);-webkit-user-select:none;user-select:none;touch-action:none;font-family:"BIZ UDPGothic","Hiragino Sans",sans-serif}
#tcOv.on{display:flex}
#tcOv .tch{width:100%;max-width:560px;box-sizing:border-box;display:flex;align-items:center;gap:8px;padding:6px 10px;height:58px;flex:none}
#tcOv .tcbk{flex:none;height:40px;padding:0 12px;border-radius:20px;border:2px solid #d9b77c;background:#fff8ec;color:#7a4520;font:700 15px/1 "BIZ UDPGothic","Hiragino Sans",sans-serif;display:flex;align-items:center;gap:4px}
#tcOv .tcsp{flex:1 1 auto}
#tcOv .tcst .tcpl{position:absolute;right:2.47%;top:9.1%;width:25%;border:0;padding:0;margin:0;background:none;-webkit-tap-highlight-color:transparent;transition:transform .12s}
#tcOv .tcst .tcpl:active{transform:scale(.94)}
#tcOv .tcpl img{display:block;width:100%;height:auto;pointer-events:none;filter:drop-shadow(0 3px 4px rgba(0,0,0,.35))}
#tcOv .tcsd{flex:none;width:40px;height:40px;border-radius:50%;border:2px solid #d9b77c;background:#fff8ec;font-size:18px;line-height:1;padding:0}
#tcOv .tctk{flex:none;height:30px;padding:0 9px;border-radius:15px;background:#fff4d6;border:2px solid #e2c48e;color:#8a5a12;font:700 13px/26px "BIZ UDPGothic",sans-serif;white-space:nowrap}
#tcOv .tcwr{position:relative;flex:1 1 auto;min-height:0;width:100%;display:flex;align-items:center;justify-content:center;overflow:hidden}
#tcOv .tcbg{position:absolute;inset:-24px;background:#2a1d12 center/cover no-repeat;filter:blur(16px) brightness(.62) saturate(1.1);transform:scale(1.06)}
#tcOv .tcst{position:relative;flex:none;overflow:hidden;touch-action:none;box-shadow:0 0 0 1px rgba(0,0,0,.25),0 6px 24px rgba(0,0,0,.35)}
#tcOv .tcst canvas{position:absolute;left:0;top:0;width:100%;height:100%;display:block}
#tcOv .tcst .tcfx{display:none}#tcOv .tcst .tcfx.on{display:block}
#tcOv .tcmsg{white-space:pre-line;position:absolute;left:50%;top:44%;transform:translate(-50%,-50%);background:#fff8ec;border:2px solid #e2c48e;border-radius:16px;padding:14px 18px;color:#6b3f1d;font:700 16px/1.5 "BIZ UDPGothic",sans-serif;text-align:center;box-shadow:0 6px 18px rgba(0,0,0,.35);max-width:80%;z-index:30;pointer-events:none;opacity:0;transition:opacity .3s}
#tcOv .tcmsg.on{opacity:1}
#tcOv .tcld{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:#fff8ec;font:700 16px "BIZ UDPGothic",sans-serif;background:#2a1d12;z-index:40}
`;
  function build() {
    if (built) return; built = true;
    const s = document.createElement('style'); s.id = 'tcCss'; s.textContent = css; document.head.appendChild(s);
    ov = document.createElement('div'); ov.id = 'tcOv'; ov.setAttribute('role', 'dialog'); ov.setAttribute('aria-modal', 'true'); ov.setAttribute('aria-label', 'トレーニングセンター');
    ov.innerHTML = `<div class="tch"><button type="button" class="tcbk" data-tc="back" aria-label="もどる">← もどる</button>`
      + `<span class="tcsp"></span>`
      + `<span class="tctk" hidden></span><button type="button" class="tcsd" data-tc="snd" aria-label="音"></button></div>`
      + `<div class="tcwr"><div class="tcbg"></div><div class="tcst"><canvas class="tcgl"></canvas><canvas class="tco"></canvas><button type="button" class="tcpl" data-tc="plan" aria-label="作戦会議"><img src="${AP('tc_icon_plan.webp')}" alt="作戦会議"></button><canvas class="tcfx"></canvas><div class="tcmsg" aria-live="polite"></div><div class="tcld">トレーニングセンター…</div></div></div>`;
    document.body.appendChild(ov);
    stage = ov.querySelector('.tcst'); cvGL = ov.querySelector('.tcgl'); cvOv = ov.querySelector('.tco'); cvFx = ov.querySelector('.tcfx');
    ov.addEventListener('click', e => {
      const b = e.target.closest('[data-tc]'); if (!b) return; SND.unlock();
      if (b.dataset.tc === 'back') close();
      else if (b.dataset.tc === 'plan') { if (window.TCPlan) { SND.se('tc_se_button.m4a'); window.TCPlan.open(ov); } }
      else if (b.dataset.tc === 'snd') { st.snd = !st.snd; touch(); SND.setOn(st.snd); paintHead(); }
    });
    const pt = (e, kind) => {
      if (busy || !TCCare.on) return; const r = stage.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width * W, y = (e.clientY - r.top) / r.height * H;
      TCCare.pointer(kind, x, y, clock());
    };
    stage.addEventListener('pointerdown', e => { SND.unlock(); if (e.target === cvOv || e.target === cvGL) { try { stage.setPointerCapture(e.pointerId); } catch (x) { } pt(e, 'down'); } });
    stage.addEventListener('pointermove', e => { if (e.buttons || e.pointerType === 'touch') pt(e, 'move'); });
    stage.addEventListener('pointerup', e => pt(e, 'up'));
    stage.addEventListener('pointercancel', e => pt(e, 'up'));
    window.addEventListener('resize', () => { if (running) layout(); });
    document.addEventListener('visibilitychange', () => { if (!ov.classList.contains('on')) return; if (document.hidden) pause(); else resume(); });
  }
  function paintHead() {
    const b = ov.querySelector('.tcsd'); b.textContent = st.snd ? '🔊' : '🔇'; b.setAttribute('aria-label', st.snd ? '音：オン（押すと けす）' : '音：オフ（押すと 出す）');
    const tk = ov.querySelector('.tctk'); tk.hidden = !(st.tickets > 0); tk.textContent = `🎫 ${st.tickets}`;
    tk.setAttribute('aria-label', `チケット ${st.tickets}枚（設定の 着せ替えで、壁紙の 解放か ${TKP()}P に かえるか 選べるよ）`);
  }
  function layout() {
    const vw = window.innerWidth, r = ov.getBoundingClientRect(), head = 58;
    const cs = getComputedStyle(ov), padT = parseFloat(cs.paddingTop) || 0, padB = parseFloat(cs.paddingBottom) || 0;
    const avail = (r.height || window.innerHeight) - padT - padB - head;
    const w = Math.max(200, Math.min(vw, avail * W / H)), h = w * H / W;
    stage.style.width = w + 'px'; stage.style.height = h + 'px';
    // 第4.150版（まさちゃん 2026/11/11 02:43「トレーニングセンターも馬の画質は高く！」）：画面の 細かさ いっぱい（3倍まで）で 描く。
    //   前は 台紙の 幅（1052px）まで ＝ iPhone（3倍・幅 1170px）では 1割、iPad（2倍・幅 1270px ほど）では 2割 ひきのばして いた（馬の ふちと 毛の もようが ぼやける）。
    //   背景の 絵は 同じ 絵を ひきのばす（前と 同じ 見え方）。GOV.q＝なめらかさを 守る ための 細かさの 倍（ふだんは 1：下の govern）
    const dpr = Math.min(window.devicePixelRatio || 1, 3) * GOV.q;
    const pw = Math.round(w * dpr), ph = Math.round(pw * H / W);
    for (const c of [cvGL, cvOv, cvFx]) if (c.width !== pw || c.height !== ph) { c.width = pw; c.height = ph; }
    if (window.TCCare && TCCare.S) TCCare.S.cs = pw / W;
    return pw / W;
  }
  function msg(txt, sec) {
    const m = ov.querySelector('.tcmsg'); m.textContent = txt; m.classList.add('on');
    clearTimeout(msg._t); msg._t = setTimeout(() => m.classList.remove('on'), (sec || 2.6) * 1000);
  }

  // ---------- 馬 ----------
  const STANCE_KAMI = { bodyW: 0.64, topOut: 0.04, hoofZ: { FL: -0.3, FR: 0.3, HL: -0.26, HR: 0.26 } };      // 神様馬：肩幅と 足の 場所（11/09 10:01〜11:24）
  function horseSpec() {
    if (st.visit) {
      return st.visit.kind === 'kamisama'
        ? { key: 'kamisama', name: 'tc_horse_bk_kamisama', stage: BIG, eyeGlow: 'gold', lift: 0.14, stance: STANCE_KAMI, glowK: 0.45, glowR: 0.7, light: 'divine' }
        : { key: 'maboroshi', name: 'tc_horse_bk_maboroshi', stage: BIG, eyeGlow: 'purple', light: 'abyss' };
    }
    const c = COLORS[st.color % COLORS.length], s = stageOf(st.cares);
    return { key: c + s + ':' + scaleOf(st.cares), name: `tc_horse_bk_${c}_s${s}`, stage: scaleOf(st.cares) };
  }
  const hcache = {};
  async function loadHorse(sp) {
    if (hcache[sp.key]) return hcache[sp.key];
    const meta = await fetch(AP(sp.name + '.json')).then(r => r.json());
    const bin = await fetch(AP(meta.bin || (sp.name + '.bin'))).then(r => r.arrayBuffer());
    const img = s => s ? new Promise(ok => { const im = new Image(); im.onload = () => ok(im); im.onerror = () => ok(null); im.src = AP(s); }) : Promise.resolve(null);
    const [texImg, nrmImg, ...poopImgs] = await Promise.all([img(meta.tex), img(meta.ntex), img('tc_poop1.webp'), img('tc_poop2.webp'), img('tc_poop3.webp')]);
    const h = TCHorse.create(gl, meta, bin, { base: 175, stage: sp.stage, texImg, nrmImg, eyeGlow: sp.eyeGlow || null, lift: sp.lift || 0, poopImgs: poopImgs.filter(Boolean), stance: sp.stance || null, glowK: sp.glowK || null, glowR: sp.glowR || null });
    hcache[sp.key] = h; return h;
  }
  async function useHorse(first) {
    const sp = horseSpec(); if (sp.key === horseKey && HO) return;
    const h = await loadHorse(sp);
    const nb = TCHorse.brain({ tod: tod(), force: [], stand: false }); nb.rnd = Math.random;
    if (BR) { nb.x = BR.x; nb.y = BR.y; nb.dir = BR.dir; } else { nb.x = 470 + Math.random() * 120; nb.y = 1080 + Math.random() * 90; nb.dir = Math.random() * Math.PI * 2; }
    if (sp.light) nb.light = sp.light;
    nb.poops = (st.poops || []).map(q => Object.assign({ t0: -10, h0: 1.05 }, q));
    HO = h; BR = nb; horseKey = sp.key;
    if (TCCare.on) TCCare.setHorse(HO, BR);
    if (!first && TCCare.on) TCCare.special(st.visit ? st.visit.kind : null);
  }
  function growCheck() {                               // 大きく 育つ・色が かわる
    const s0 = stageOf(st.cares - 1), s1 = stageOf(st.cares), k0 = scaleOf(st.cares - 1), k1 = scaleOf(st.cares);
    if (st.cares >= 300) {
      st.color = (st.color + 1) % COLORS.length; st.cares = 0; st.gen = (st.gen || 1) + 1; touch();
      msg(`🎉 お世話 300回！\n${COLOR_JA[COLORS[st.color]]}の 子が やってきたよ`, 3.6); if (!st.visit) useHorse();
      return;
    }
    if (s1 !== s0 || k1 !== k0) { msg(`🎉 お世話 ${st.cares}回！ 大きく 育ったよ`, 3.2); if (!st.visit) useHorse(); }
  }

  // ---------- 2分ごとの チャンス・トークン・時間帯・幻の馬／神様馬 ----------
  function fieldName() { return st.visit ? (st.visit.kind === 'kamisama' ? 'divine' : 'abyss') : tod(); }
  async function syncField() {
    const f = fieldName();
    if (field.field !== f) { await field.setField(f); }
    paintBg(f); SND.field(f);
  }
  function paintBg(f) {                                 // 画面の 上下の すき間：いまの フィールドを ぼかして しく
    const bg = ov && ov.querySelector('.tcbg'); if (!bg || bg.dataset.f === f) return;
    bg.dataset.f = f; bg.style.backgroundImage = `url("${AP(`tc_field_${f}.webp`)}")`;
  }
  function chance(t) {                                  // 2分ごと：高確ゾーン・うんち（幻の馬・神様馬は 馬の リセットの とき だけ：第4.144版）
    const now = Date.now();
    if (Math.random() < P_HIGH) { const S = TCCare.S; S.high = HIGH_N; S.highBump = t; S.fx.push({ k: 'luck', t0: t, dur: 2.6 }); SND.se('tc_se_luck.m4a'); st.high = HIGH_N; touch(); }
    if (Math.random() < P_POOP && BR && BR.mode !== 'sleep' && (BR.poops || []).length < 3) BR.poopReq = true;
    void now;
  }
  async function startVisit(kind) {
    st.visit = { kind, until: tnow() + VISIT_MIN * 60000, el: 0 }; st.rs = { n: 0, at: 0, el: 0 }; touch(); save();
    await useHorse(); await syncField();
    msg(kind === 'kamisama' ? '✨ 神様馬が やってきた！' : '🌙 幻の馬が やってきた！', 3.0);
  }
  async function endVisit() {
    st.visit = null; st.rs = { n: 0, at: 0, el: 0 }; touch(); save();
    await useHorse(); await syncField();
    msg('また 来てね… と 帰って いったよ', 2.6);
  }
  // ---------- 馬の リセット（第4.144版）----------
  const careIdle = () => !TCCare.on || (TCCare.S.phase === 'idle' && !TCCare.S.mode && !TCCare.S.busy && !TCCare.S.chooser);      // お世話（撫でる・呼ぶも）の 途中で ない
  const panelOpen = () => !!((window.TCPlan && TCPlan.isOpen && TCPlan.isOpen()) || (window.TCGuide && TCGuide.isOpen && TCGuide.isOpen()));
  const rsLeft = gms => (st.rs.at ? Math.max(0, Math.min((st.rs.at + RESET_MIN * 60000 - gms) / 1000, RESET_MIN * 60 - (+st.rs.el || 0))) : null);      // タイマーの のこり（秒）・まだ 動いて いなければ null
  const visitLeft = gms => (st.visit ? Math.max(0, Math.min((st.visit.until - gms) / 1000, VISIT_MIN * 60 - (+st.visit.el || 0))) : null);              // タイムリミットの のこり（秒）
  let resetting = false;
  function resetStep(gms, dt, t) {
    const rs = st.rs;
    if (rs.at) rs.el = (+rs.el || 0) + dt;
    if (!rs.at && rs.n >= RESET_CARES && careIdle() && !busy) { rs.at = gms; rs.el = 0; touch(); save(); }      // 5回めの お世話が おわった → タイマーが 動く
    if (rs.at && rsLeft(gms) <= 0 && t > 3 && careIdle() && !busy && !panelOpen() && !resetting) { resetting = true; doReset().catch(() => { }).finally(() => { resetting = false; }); }
  }
  let forceNext;                               // テスト 用：次の リセットの 抽選の 結果を 決めて おく（_t.force）
  function nextHorse() {                       // 次の 馬の 抽選（null＝いつもの 馬）
    if (forceNext !== undefined) { const f = forceNext; forceNext = undefined; return f; }
    const r = Math.random(); return r < P_KAMI ? 'kamisama' : r < P_KAMI + P_MAB ? 'maboroshi' : null;
  }
  async function doReset() {
    const next = nextHorse();
    st.rs = { n: 0, at: 0, el: 0 }; touch();
    if (next) await startVisit(next);            // 幻の馬・神様馬が やってくる（いま いる 馬と 同じ でも 新しく 来た ことに する：タイムリミットは はじめから）
    else if (st.visit) await endVisit();         // 幻の馬・神様馬は 帰る → いつもの 馬
    else save();                                 // いつもの 馬の まま
    return next;
  }
  function draw() {                                    // お世話の 抽選を 1回 ひく（当たり か null）
    const S = TCCare.S, hi = S.high > 0, k = hi ? HIGH_X : 1;
    if (hi) { S.high -= 1; S.highBump = clock(); st.high = S.high; touch(); }
    const r = Math.random(); let a = 0, tab = st.visit ? PRIZES_VISIT[st.visit.kind] || PRIZES : PRIZES;
    for (const [p, z] of tab) { a += p * k; if (r < a) return Object.assign({}, z, z.k === 'tk' ? { n: tkCount() } : {}); }
    return null;
  }
  function tkCount() { const r = Math.random(); return r < 1 / 8 ? 3 : r < 1 / 8 + 1 / 3 ? 2 : 1; }
  // 第4.140版（バグ直し）：当たりは お世話の はじめに 決まって、お世話の 演出が おわってから 出る。その 間に アプリを 閉じると、当たりが 消えて いた（トークンは 使った のに）。
  //   ルーレット・チケットの 演出の 途中で 閉じても 同じ。→ 決まった 当たりを すぐ 保存（st.pend）して、わたし おわったら 消す。
  //   アプリを 開き直した ときに 残って いたら、その ときに わたす（init）。同じ 当たりを 2回 わたさない：ポイントは 台帳の id（同じ id は 1回だけ）・チケットは 足すのと 消すのを 1回の 保存で
  function lottery() {                                 // tc_care.js が お世話の たびに よぶ
    const z = draw(); if (!z) return null;
    if (st.pend) give(st.pend);                                  // 前の 当たりが まだ なら 先に わたす
    z.id = 'tc-' + Date.now().toString(36) + '-' + Math.floor(Math.random() * 1e6).toString(36);
    if (TCCare.on && TCCare.S.stock !== st.stock) st.stock = TCCare.S.stock;      // 使った トークンも いっしょに 保存（当たり だけ 残って トークンが もどる ことが ない ように）
    if (z.k === 'rt') { const ab = z.v || RT[z.tier] || RT.normal; z.win = Math.random() < 0.5 ? 0 : 1; z.a = ab[0]; z.b = ab[1]; }      // ルーレットの 止まる 所も ここで 決める（50%ずつ）
    st.pend = JSON.parse(JSON.stringify(z)); touch(); save();
    return z;
  }
  // 当たりを わたす（ポイント → 台帳・チケット → 数を 足す）。返り値＝わたした ポイント（チケットは 0）
  function give(z) {
    if (!z) return 0;
    let v = 0;
    if (z.k === 'pt') { v = +z.v || 0; grant(v, 'トレーニングセンターの お世話', z.id); }
    else if (z.k === 'rt') { const ab = z.a != null ? [z.a, z.b] : (z.v || RT[z.tier] || RT.normal); v = ab[z.win ? 1 : 0]; grant(v, 'トレーニングセンターの ルーレット', z.id); }
    else if (z.k === 'tk') st.tickets = (st.tickets || 0) + (z.n || 1);
    if (st.pend && (!z.id || st.pend.id === z.id)) st.pend = null;
    touch(); save();
    return v;
  }
  async function onPrize(z) {                           // 当たり（お世話の 演出が おわってから）
    if (z.k === 'pt') { give(z); return; }
    if (busy || !window.TCFX) { give(z); if (ov) paintHead(); return; }      // 演出を 出せない ときも 当たりは わたす（前は 消えて いた）
    busy = true; TCCare.roulette(true);
    try {
      if (z.k === 'rt') {
        if (z.win == null) z.win = Math.random() < 0.5 ? 0 : 1;
        const [a, b] = z.a != null ? [z.a, z.b] : (z.v || RT[z.tier] || RT.normal);
        try { await TCFX.roulette(cvFx, { th: z.tier, a, b, win: z.win, bg: fieldName(), se: SND.se }); } finally { give(z); }
      } else if (z.k === 'tk') {
        const n = z.n || 1;
        try { await TCFX.ticket(cvFx, { n, bg: fieldName(), se: SND.se }); } finally { give(z); paintHead(); }
        msg(`🎫 チケット ${n}枚 GET！\n設定の「着せ替え」で\n壁紙か ${TKP()}P を\n選べるよ`, 4.4);      // 第4.141版（11/10 15:52 まさちゃん「壁紙チケット or 8000pにして！」→ 16:08「じゃあ7000pにして！」）
      }
    } finally { busy = false; TCCare.roulette(false); }
  }
  function grant(v, what, id) {
    const w = window.TengelWallet;
    if (w && typeof w.grant === 'function' && v > 0) w.grant(id || ('tc-' + Date.now().toString(36) + '-' + Math.floor(Math.random() * 1e6).toString(36)), v, what).catch(() => { });
  }

  // ---------- なめらかさを 守る（第4.150版・まさちゃん 2026/11/11 02:43「トレーニングセンターも今は、カクカクしてる！ヌルヌル動くことが絶対！」）----------
  //   画面の 書きかえ ごと（ふつう 60コマ／秒）に 描く（前は 30コマ／秒に おさえて いた＝歩く 馬・お世話の 動きが カクカクして 見えた）。
  //   描くのが 間に合わない 端末では、絵の 細かさを 1段ずつ 下げて（GOV_Q）なめらかさを 守る。細かさは 画面を 開き直しても そのまま（アプリを 閉じる まで）。
  //   下げても よく ならない とき（省電力モードで 画面の 書きかえが 30回／秒に おさえられて いる・ほかの 所が おそい）は 細かさの せいでは ない ので、もとに もどして もう 下げない。
  //   数え方：コマと コマの 間が 25ms より 長い＝1コマ 落ちた。120コマ ごとに 落ちた わりあいを 見る（4割 以上で 下げる）。細かさを かえた あと 45コマと、止まって いた あとの 1コマは 数えない
  const GOV_Q = [1, 0.82, 0.68], GOV_N = 120, GOV_BAD = 0.4, GOV_SAME = 0.75, GOV_WAIT = 45;
  const GOV = { q: 1, step: 0, off: false, n: 0, slow: 0, wait: GOV_WAIT, base: 0, last: 0 };
  function govSet(step, off) { GOV.step = step; GOV.q = GOV_Q[step]; GOV.off = !!off; GOV.n = GOV.slow = 0; GOV.wait = GOV_WAIT; if (ov && stage && cvGL) layout(); }
  function govern(now) {
    const d = now - GOV.last; GOV.last = now;
    if (GOV.off || !(d > 0) || d > 250) return;                    // はじめの 1コマ・止まって いた あと
    if (GOV.wait > 0) { GOV.wait--; return; }
    GOV.n++; if (d > 25) GOV.slow++;
    if (GOV.n < GOV_N) return;
    const r = GOV.slow / GOV.n; GOV.n = GOV.slow = 0;
    if (GOV.step > 0 && GOV.base > 0 && r >= GOV.base * GOV_SAME) { govSet(GOV.step - 1, true); return; }      // 下げても かわらない → 1段 もどして おわり
    GOV.base = 0;
    if (r < GOV_BAD) return;                                        // なめらか
    if (GOV.step >= GOV_Q.length - 1) { GOV.off = true; return; }   // いちばん 下の 段でも おそい → これ以上は 下げない
    GOV.base = r; govSet(GOV.step + 1, false);
  }

  // ---------- 1コマ ----------
  function frame(now) {
    raf = requestAnimationFrame(frame);
    govern(now);
    lastDraw = now;
    const t = clock(), dt = lastT == null ? 1 / 60 : Math.max(0, Math.min(0.1, t - lastT)); lastT = t;
    const ms = Date.now(), gms = tnow();
    // 第4.140版（バグ直し）：お世話で 使った トークンを 先に 写す（前は トークンが ちょうど 1つ たまる 瞬間と 重なると、使った ぶんが 消えて 1回 タダに なった）
    if (TCCare.on && TCCare.S.stock !== st.stock) { st.stock = TCCare.S.stock; touch(); }
    if (accrue(gms) > 0 && TCCare.on) { const S = TCCare.S; S.stock = st.stock; S.stockShow = st.stock; S.stockBump = t; }
    if (t >= nextTick) { nextTick = t + TICK; if (t > 3) chance(t); }
    if (BR && !st.visit) BR.tod = tod();
    if (st.visit) st.visit.el = (+st.visit.el || 0) + dt;                                       // 開いて いる あいだに たった 秒（時計を もどしても 30分で 帰る）
    if (st.visit && visitLeft(gms) <= 0 && !busy && careIdle() && !panelOpen() && !resetting) { resetting = true; endVisit().catch(() => { }).finally(() => { resetting = false; }); }      // タイムリミット → いつもの 馬
    else if (!resetting) resetStep(gms, dt, t);
    if (TCCare.on) TCCare.S.vinfo = st.visit ? { kind: st.visit.kind, left: visitLeft(gms), n: Math.min(st.rs.n || 0, RESET_CARES), need: RESET_CARES, timer: rsLeft(gms) } : null;      // バナーの 下の「切り替わる 条件」（tc_care.js が かく）
    if (resetting) { /* 馬を かえて いる 途中 */ }
    else if (!busy && field.field && field.field !== fieldName() && !frame._sw) { frame._sw = true; syncField().finally(() => { frame._sw = false; }); }
    while (later.length) { try { later.shift()(); } catch (e) { } }
    if (!HO || !BR) return;
    const ZV = TCCare.on ? TCCare.view() : null;
    field.render(t, ZV);
    const cvv = gl.canvas, kk = cvv.width / W, Z = ZV ? ZV.z : 1, ZX = ZV ? ZV.cx : W / 2, ZY = ZV ? ZV.cy : H / 2;
    if (TCCare.on) TCCare.pre(t, dt);
    TCHorse.step(HO, BR, t, dt, BR.rnd);
    TCHorse.draw(HO, BR, t, { W: cvv.width, H: cvv.height, k: kk * Z, ox: cvv.width / 2 - ZX * kk * Z, oy: cvv.height / 2 - ZY * kk * Z });
    if (TCCare.on) TCCare.post(t);
    // 保存する もの（トレセンの 紙の 絵が かえた 数）
    const S = TCCare.S;
    if (S.stock !== st.stock) { st.stock = S.stock; touch(); }
    if (S.heart !== st.heart) { st.heart = S.heart; touch(); }
    if ((S.high || 0) !== (st.high || 0)) { st.high = S.high || 0; touch(); }
    const ps = (BR.poops || []).map(q => { if (q.gold == null) q.gold = Math.random() < P_GOLD; return { x: Math.round(q.x), y: Math.round(q.y), img: q.img || 0, w: q.w, gold: !!q.gold }; });
    if (JSON.stringify(ps) !== JSON.stringify(st.poops)) { st.poops = ps; touch(); }
    if (dirty && ms - saveAt > 2000) { saveAt = ms; save(); }
  }
  function pause() { running = false; cancelAnimationFrame(raf); SND.stopAll(); if (dirty) save(); }
  function resume() {
    if (running) return; running = true; lastT = null; lastDraw = 0; GOV.last = 0; GOV.n = GOV.slow = 0; GOV.wait = GOV_WAIT; SND.unlock(); syncField(); raf = requestAnimationFrame(frame);
  }

  // ---------- 開く・閉じる ----------
  let ready = null;
  async function init() {
    load(); build(); paintHead(); SND.setOn(st.snd);
    ov.classList.add('on'); const cs = layout();
    field = TCField.create(cvGL); if (!field) throw new Error('webgl');
    gl = field.gl; tBase = performance.now();
    if (!st.fav || st.fav.day !== today()) { st.fav = { day: today(), kind: ['esa', 'apple', 'carrot'][Math.floor(Math.random() * 3)] }; touch(); }
    if (st.visit && (tnow() > st.visit.until || (+st.visit.el || 0) >= VISIT_MIN * 60)) st.visit = null;
    if (st.pend) {      // 第4.140版：前に アプリを 閉じた ときに わたせなかった 当たりを わたす
      const z = st.pend, v = give(z);
      later.push(() => msg(z.k === 'tk' ? `🎫 前の 当たり（チケット ${z.n || 1}枚）を 受け取ったよ` : `🎁 前の 当たり（${v.toLocaleString('ja-JP')}P）を 受け取ったよ`, 3.6));
    }
    accrue(tnow());
    await Promise.all([useHorse(true), field.setField(fieldName())]); paintBg(fieldName());
    await TCCare.init({ horse: HO, brain: BR, canvas: cvOv, cs, tod: tod(), bg: st.visit ? fieldName() : '', stageNo: stageOf(st.cares),
      lottery, onPrize, onEvent: onCareEvent, banTop: 290, dropX: 726, hiY: 284, onHelp: () => { if (window.TCGuide) TCGuide.open(stage, { anim: true }); } });
    const S = TCCare.S; S.heart = S.heartShow = st.heart || 0; S.stock = S.stockShow = st.stock; S.high = st.high || 0; S.fav = st.fav.kind;
    nextTick = clock() + TICK;
    SND.preload(['tc_se_button.m4a', 'tc_se_unfold.m4a', 'tc_se_rub.m4a', 'tc_se_heart.m4a', 'tc_se_pick.m4a', 'tc_se_chooser.m4a']);
  }
  async function open(opt) {
    SND.unlock();
    try {
      if (!ready) ready = init(); else { load(); ov.classList.add('on'); layout(); const S = TCCare.S; S.heart = S.heartShow = st.heart || 0; S.high = st.high || 0; }
      await ready;
    } catch (e) { ready = null; if (ov) ov.classList.remove('on'); note('トレーニングセンターを ひらけなかったよ（' + (e && e.message || e) + '）'); return; }      // 第4.140版：alert() は アプリの 中で 出ない → 画面の お知らせ
    const ld = ov.querySelector('.tcld'); if (ld) ld.remove();
    paintHead(); layout(); accrue(tnow());
    if (TCCare.on) { const S = TCCare.S; S.stock = S.stockShow = st.stock; }
    resume();
    if (opt && opt.plan && window.TCPlan) window.TCPlan.open(ov);
  }
  function close() {
    if (window.TCPlan && window.TCPlan.isOpen && window.TCPlan.isOpen()) window.TCPlan.close();
    if (window.TCGuide && TCGuide.isOpen && TCGuide.isOpen()) TCGuide.close();
    pause(); save(); if (ov) ov.classList.remove('on');
    try { document.dispatchEvent(new CustomEvent('tengel:tc')); } catch (e) { }      // ミッション（お世話の 合計）を かき直す
  }
  // 着せ替え（kisekae.js）から：チケットの 数・使う
  const tickets = { count: () => { if (!st) load(); return st.tickets || 0; }, use: () => { if (!st) load(); if ((st.tickets || 0) < 1) return false; st.tickets -= 1; save(); if (ov) paintHead(); return true; },
    back: () => { if (!st) load(); st.tickets = (st.tickets || 0) + 1; save(); if (ov) paintHead(); return true; } };      // back＝使った 1枚を もどす（着せ替えで 解放できなかった とき：第4.140版）
  return { open, close, tickets, get state() { return st; }, _snd: SND, _t: { gov: GOV, govern, govSet, GOV_Q, lottery, draw, give, onPrize, PRIZES, PRIZES_VISIT, fieldName, startVisit, endVisit, doReset, nextHorse, force: k => { forceNext = k; }, chance, rsLeft, visitLeft, RT, ODDS: { poop: P_POOP, gold: P_GOLD, high: P_HIGH, mab: P_MAB, kami: P_KAMI, highX: HIGH_X, highN: HIGH_N, tick: TICK, visitMin: VISIT_MIN, resetCares: RESET_CARES, resetMin: RESET_MIN, tokenMin: TOKEN_MIN, tokenMax: TOKEN_MAX } } };      // _t：テスト 用
})();
