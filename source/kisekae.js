// 着せ替え（App Store版 第4弾：アップデート指示書 9章・16.1・16.1.1・16.2.1・16.4）
//   30テーマ＝いつもの（無料）＋ポイントで解放する16枚（2,000〜7,000P）＋帯3枚（壁紙を 5・10・15枚 あつめた ミッションで）＋壁紙パック 10枚（第4.92版・買い切り）。
//     第4.147版（まさちゃん 2026/11/10 22:12「壁紙 ホワイトデー・バレンタインデー・ハロウィン・正月・クリスマス・雪・紅葉・桜・海 これら全部消して！」「七夕も消して！」）：41 → 31テーマ
//     （ポイントの 26 → 17枚・壁紙パックの 11 → 10枚・帯は 8・16・25 → 5・10・16枚）。外した 壁紙を 使って いた ときは「いつもの」に もどす（一覧に ない 名前は 使えない）。
//     第4.160版（まさちゃん 2026/11/12 14:31「壁紙のネオン消して！」）：ネオンも 外した ＝ 31 → 30テーマ（ポイントの 17 → 16枚・帯は 5・10・16 → 5・10・15枚）。同じ しくみで「いつもの」に もどして ポイントを 返す
//     解放して いた ぶんの ポイント・チケットは points_ui.js の goneBack が 返す
//   テーマは 色・字・形（CSS の変数：html[data-ks=<id>]）・判定タブの上の絵（見本と同じ 動く壁紙：#ksBnr）・的中の PUSH と 結果のボード（fx.js が TengelKisekae.fx() で読む）。
//     第4.176版（まさちゃん 2026/11/16 01:26「いつもの(デフォルト)壁紙これにして！」）：「いつもの」にも 上の絵（まさちゃんの TENGER の 絵・動かない 1まい：一覧の bnr＝ファイル名。
//     kisekae/default_wall.py・build_kisekae.py の DEFAULT_WALL）。色・字・PUSH・ボードは 前の まま。絵が 読めない（絵を 入れて いない CI など）ときは 上の絵なし（前と 同じ）
//   見本（kisekae/themes20.py・boards.py・gen_fx.py・mock/）の CSS と HTML は kisekae/build_kisekae.py が束ねる：小さい分は window.__KS、テーマごとの大きい分は ks_<id>.json（選んだときに 1回だけ読む）。
//   選んだテーマは端末に保存（localStorage＝起動の瞬間から・設定の DB にも）。解放したかどうかは ポイントの台帳（unlock-theme:<id>・TengelWallet）。
//   「視差効果を減らす」か 設定の「演出を控えめにする」なら 壁紙は止まった絵（CSS の @media と .calm）。判定タブが見えていない間は 動きを止める（.pause ※仮）。
//   第4.219版：上の絵・設定タブの 動く タイル・見本は、画面の 外か ほかの 窓（トレーニングセンター・カードバトル・的中の 演出 など）の 下に ある 間も 止める（下の seen）。
//   第4.92版：壁紙パック（買い切り 1,500円・10枚〔第4.147版で 11 → 10枚〕：kisekae/pack/）。いちばん 上の 組に 買う ボタンと 解放の 進み具合。買った あとに 読み込んだ レース 5つごとに
//   1枚ずつ 使える ように なる（TengelWallet.pack）。ポイントでは 解放 できない。帯の 壁紙の ミッションの 枚数に 数える
//   Web版（ホーム画面のアプリ）では何もしない。
(function () {
  'use strict';
  if (!window.__NATIVE || !window.__KS) return;
  const A = window.__KS;
  const $ = (s, r) => (r || document).querySelector(s);
  const TL = () => window.TengelLocal, WL = () => window.TengelWallet, FX = () => window.TengelFx;
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const yen = v => Math.round(+v || 0).toLocaleString('ja-JP'), pts = v => yen(v) + 'P';
  const KEY = 'tengel.kisekae', SETTING = 'kisekae';
  const byId = {}; A.themes.forEach(t => { byId[t.id] = t; });
  let curId = 'default', payload = null, loading = null, conf = '';
  const cache = {}, pcache = {};
  function toast(m, ms) { const t = $('#toast'); if (!t) return; t.textContent = m; t.hidden = false; clearTimeout(toast._t); toast._t = setTimeout(() => { t.hidden = true; }, ms || 2600); }
  function emit(phase) { try { document.dispatchEvent(new CustomEvent('tengel:kisekae', { detail: { phase: phase, id: curId } })); } catch (e) { /* なし */ } }

  // ---------- CSS（全テーマの変数・共通の形・@font-face） ----------
  // チケットの 箱（第4.141版：壁紙の 解放か 7,000P かを 選ぶ）
  const TK_CSS = '#setKisekae .kstk{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:10px 0 2px;border:1px dashed var(--line);border-radius:12px;padding:9px 12px;background:var(--surface-2)}'
    + '#setKisekae .kstk .kstx{flex:1 1 190px;min-width:0;font-size:13px;line-height:1.5}#setKisekae .kstk .kstx>b{display:block;font-size:14px}#setKisekae .kstk small{display:block;font-size:12px;color:var(--muted)}'
    + '#setKisekae .kstk .kstb{display:flex;gap:8px;flex:none;flex-wrap:wrap}';
  // 見本（第4.218版）：タップした 壁紙の タイルの 行の すぐ 下に、全部の 列を つかう 箱（.kspv）。並びは grid の dense で つめる（タイルの 行は 欠けない）。
  //   中は 2つの 小さな 画面（.kspvw：舞台 390×844 の まん中 390×560 を 幅に 合わせて 縮める）＝ 左 PUSH・右 結果ボード。うしろは その 壁紙の 小さな 絵
  //   右の あきは 右下の 丸い ボタンの 列（#fabCol）の 手前まで（--fabz：tc/tc_launch.js が 入れる・買い目編集の 保存の 帯と 同じ）＝「閉じる」と ボードが 列に かくれない
  const PV_CSS = '#setKisekae .ksgrid{grid-auto-flow:row dense}'
    + '#setKisekae .kspv{grid-column:1/-1;min-width:0;padding:8px max(8px,var(--fabz,0px)) 9px 8px;border:1px solid var(--line);border-radius:12px;background:var(--surface-2);animation:ksCf .18s ease-out}'
    + '#setKisekae .kspvh{display:flex;align-items:center;gap:8px;margin:0 2px 8px}'
    + '#setKisekae .kspvt{flex:1 1 auto;min-width:0;font-size:13px;line-height:1.4}#setKisekae .kspvt>b{display:block;font-size:13.5px}#setKisekae .kspvt small{display:block;font-size:11.5px;color:var(--muted)}'
    + '#setKisekae .kspvh .btn{flex:none;min-height:32px;padding:4px 12px;font-size:12.5px;line-height:1.2;border-radius:8px;cursor:pointer}'
    + '#setKisekae .kspvs{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}'
    + '#setKisekae .kspvf{margin:0;min-width:0}'
    + '#setKisekae .kspvw{position:relative;width:100%;aspect-ratio:390/560;overflow:hidden;border-radius:10px;background:#20160E;isolation:isolate}'
    + '#setKisekae .kspvw .kspvbg{position:absolute;left:0;top:0;width:100%;height:auto;aspect-ratio:390/160;object-fit:cover;display:block;pointer-events:none}'
    + '#setKisekae .kspvw .fxs{transform:translateY(var(--pvy,0px)) scale(var(--fxk,.38));pointer-events:none}'
    + '#setKisekae .kspvf figcaption{margin-top:4px;font-size:12px;font-weight:700;line-height:1.3;text-align:center;color:var(--muted)}'
    + '#setKisekae .kspvw .hit{--t0:.35s}'                 // ボードの 行は 的中の 画面（PUSH を 押して 1.15秒 あと：.fxs .hit）より 早く 出す
    + '#setKisekae .kspv.pause .kspvw *{animation-play-state:paused!important}';
  // 第4.219版：止める（.pause）ときは かざり（::before・::after）の 動きも 止める。前は 中の 要素（*）だけ で、海賊の 上の絵の 旗の 32こ・見本の PUSH の 光は
  //   ほかの タブに いる 間も アプリが 裏の 間も 動いて いた
  const STOP_CSS = '#ksBnr.pause *::before,#ksBnr.pause *::after,#setKisekae .kst .kslv.pause *::before,#setKisekae .kst .kslv.pause *::after,'
    + '#setKisekae .kspv.pause .kspvw *::before,#setKisekae .kspv.pause .kspvw *::after{animation-play-state:paused!important}';
  function css() {
    if ($('#ksCss')) return;
    const st = document.createElement('style'); st.id = 'ksCss'; st.textContent = A.css + TK_CSS + PV_CSS + STOP_CSS;
    document.head.appendChild(st);
  }

  // ---------- 解放（ポイントの台帳） ----------
  const wallet = () => (WL() && WL().on ? WL() : null);
  const unlocked = id => id === 'default' || !!(wallet() && wallet().unlocked('theme:' + id));
  // 壁紙パック（第4.92版）：買ったか・解放した 枚数（t.pack が その 数 以下なら 使える）
  const PK = A.pack || { ids: [], order: [], every: 5, name: '壁紙パック' };
  const packInfo = () => { try { const w = wallet(); if (w && w.pack) return w.pack.info(); } catch (e) { /* なし */ } return { owned: false, reads: 0, n: 0, next: null, every: PK.every, total: PK.order.length }; };
  const packHas = t => { const i = packInfo(); return !!t.pack && i.owned && t.pack <= i.n; };
  const count = () => A.paid.filter(id => unlocked(id)).length + packInfo().n;   // 解放した壁紙の枚数（ポイント＋壁紙パック。帯のミッション：8.3）
  function usable(id) { const t = byId[id]; if (!t) return false; if (t.pack) return packHas(t); if (!t.price && !t.band) return true; return unlocked(id); }

  // ---------- 適用 ----------
  function setAttr(id) { if (id === 'default') delete document.documentElement.dataset.ks; else document.documentElement.dataset.ks = id; }
  async function load(id) {
    if (id === 'default') return null;
    if (cache[id] !== undefined) return cache[id];
    let p = null;
    try { const r = await fetch('ks_' + id + '.json', { cache: 'force-cache' }); if (r.ok) p = await r.json(); } catch (e) { p = null; }
    cache[id] = p;
    return p;
  }
  function themeStyle(p) {
    let st = $('#ksTheme');
    if (!st) { st = document.createElement('style'); st.id = 'ksTheme'; document.head.appendChild(st); }
    st.textContent = p ? [(p.bnr && p.bnr.css) || '', (p.push && p.push.css) || '', (p.board && p.board.css) || ''].join('\n') : '';
  }
  function bnrBox() {
    let b = $('#ksBnr');
    if (!b) {
      const v = $('#v-judge'); if (!v) return null;
      b = document.createElement('div'); b.id = 'ksBnr'; b.hidden = true; b.setAttribute('aria-hidden', 'false');
      b.innerHTML = '<div class="ksb"></div>';
      v.insertBefore(b, v.firstChild);
    }
    return b;
  }
  function fitBnr() {
    const b = $('#ksBnr'); if (!b || b.hidden) return;
    const w = b.clientWidth || window.innerWidth; let k = w / 390;
    if (!isFinite(k) || k <= 0) k = 1; if (Math.abs(k - 1) < .01) k = 1;
    b.style.setProperty('--ksk', k.toFixed(4));
  }
  // いつもの の 上の絵（第4.176版）：動かない 1まいの 絵。読めない ときは 上の絵を かくす（下の paintBnr）
  const DEF = (() => { const t = byId.default; return t && t.bnr ? { id: 'default', bnr: { html: `<img class="bnr ksdf" src="${esc(t.bnr)}" alt="${esc(t.balt || '')}" decoding="async">`, css: '' } } : null; })();
  function paintBnr(p) {
    const b = bnrBox(); if (!b) return;
    const stage = $('.ksb', b);
    if (p && p.bnr && p.bnr.html) { stage.innerHTML = p.bnr.html; b.hidden = false; fitBnr(); } else { stage.innerHTML = ''; b.hidden = true; }
    const df = $('img.ksdf', stage);
    if (df) { const bad = () => { if (stage.contains(df)) { stage.innerHTML = ''; b.hidden = true; } }; df.addEventListener('error', bad); if (df.complete && !df.naturalWidth) bad(); }
    motion();
    if (!b.hidden) phaseSoon();
  }
  // 動きを止める：「視差効果を減らす」か「演出を控えめにする」（.calm）・判定タブが見えていない／アプリが裏・上の絵が 見えて いない（.pause：第4.219版の seen）
  function motion() {
    const b = $('#ksBnr'); if (!b) return;
    const F = FX();
    const was = b.classList.contains('pause') || b.classList.contains('calm');
    b.classList.toggle('calm', !!(F && F.calm && F.calm()));
    const v = $('#v-judge');
    const sb = !b.hidden && seen(b); SEEN.b = sb;
    b.classList.toggle('pause', !!document.hidden || !!(v && v.hidden) || (!b.hidden && !sb));
    if (was && !b.hidden && !b.classList.contains('pause') && !b.classList.contains('calm')) phaseSoon();      // また 動きだした：コマの さかい目を 合わせ直す
    watch();
  }
  // ---------- 見えて いない 間は 止める（第4.219版・まさちゃん 2026/11/25 00:00「なんか全体的にめちゃくちゃ重い！理由見つけて改善して！」）----------
  //   判定タブの 上の絵（#ksBnr）・設定タブの 動く タイル（.kslive › .kslv：いま 使って いる 壁紙と 同じ 動き まるごと）・見本（.kspv）は、
  //   多い 壁紙で 200〜300 の 動きを 毎コマ 動かす。iPhone（WebKit）は SVG の 中の 動き・steps() の コマ送り・visibility などを 画面の 合成に まかせられず、
  //   毎コマ 計算して 描き直す。前は タブが 見えて さえ いれば、下へ スクロール して 上の絵が 画面の 外の ときも、トレーニングセンター・カードバトル・
  //   思い出フィギュア・作戦会議・推し馬・的中の 演出の 窓の 下でも、設定タブの 上や 下（着せ替えの カードが 画面の 外）でも ずっと 動いて いた ＝ アプリ ぜんたいが 重い もと。
  //   → 画面の 中に ない、または 見えて いる 所が ぜんぶ ほかの 窓の 下（elementFromPoint で 9点：1点でも 見えれば 動かす）なら 止める（.pause：CSS の 止め方の まま）。
  //     見える ように なったら すぐ 動かす（上の絵は コマの さかい目も 合わせ直す：phaseSoon）。見えて いる 間の 動きは 前と 同じ。
  //   見直す とき：画面に 出入り（IntersectionObserver）・タップの あと（窓が 開く／閉じる：0.09秒・0.7秒 あと）・タブ・アプリの 表と 裏・1秒ごと（判定か 設定の タブで 壁紙が ある とき だけ）。
  //   変わった ときだけ クラスを さわる（テストが 手で つけた .pause は そのまま）
  const SEEN = { b: null, l: null, p: null };
  function seen(el, host) {
    if (!el || !el.isConnected) return false;
    const r = el.getBoundingClientRect(), W = window.innerWidth || 0, H = window.innerHeight || 0;
    const t = Math.max(r.top, 0), bt = Math.min(r.bottom, H), l = Math.max(r.left, 0), rt = Math.min(r.right, W);
    if (!(r.width > 0 && r.height > 0) || bt - t < 1 || rt - l < 1) return false;           // 画面の 外・出て いない
    const vs = window.visualViewport && window.visualViewport.scale;
    if ((vs && vs > 1.01) || typeof document.elementFromPoint !== 'function') return true;  // 2本指で 拡大 中は 点の はかり方が かわる → かくれて いるかは 見ない（動かす）
    const me = host || el;
    // 上に ある 窓が うすく なって いる とちゅう（消える・出る ときの すき通し：はじめの 画面が 消える 間・的中の 演出の 暗い 膜が 出る 間）は 見えて いる ことに する
    const thin = h => { let o = 1; for (let x = h; x && x.nodeType === 1 && x !== document.body; x = x.parentElement) { const v = parseFloat(getComputedStyle(x).opacity); if (v < 1) o *= v; if (o < 0.99) return true; } return false; };
    // 見る 点：横 3つ × 縦 3つ（見えて いる 所の 上の はし・まん中・下の はし）。上に くっつく 帯（header.top）の 下に 少し だけ 出て いる ときも 下の はしで 見つける
    for (const y of [t + Math.min(3, (bt - t) / 2), (t + bt) / 2, bt - Math.min(3, (bt - t) / 2)]) {
      for (const fx of [0.12, 0.5, 0.88]) {
        const h = document.elementFromPoint(l + (rt - l) * fx, y);
        if (!h || me.contains(h) || h.contains(me) || thin(h)) return true;                   // 1点でも 見えて いれば 動かす（中の 絵が 押せない 形でも 下の 箱が 当たる）
      }
    }
    return false;                                                                             // 見えて いる 所は ぜんぶ ほかの 窓の 下
  }
  const liveBox = () => $('#setKisekae .kst .kslive');
  function look() {
    const b = $('#ksBnr'), lw = liveBox(), pb = $('#setKisekae .kspv');
    const sb = !!b && !b.hidden && seen(b), sl = !!lw && seen(lw, lw.closest('.kst')), sp = !!pb && seen(pb);
    if (b && sb !== SEEN.b) motion();
    if ((lw && sl !== SEEN.l) || (pb && sp !== SEEN.p)) motionLive();
  }
  let lookT = 0, io = null, ioT = [];
  function observe() {
    if (typeof IntersectionObserver !== 'function') return;
    const ts = [$('#ksBnr'), liveBox(), $('#setKisekae .kspv')].filter(Boolean);
    if (ts.length === ioT.length && ts.every((e, i) => e === ioT[i])) return;
    try {
      if (!io) io = new IntersectionObserver(() => look(), { threshold: 0 });
      io.disconnect(); ts.forEach(e => io.observe(e)); ioT = ts;
    } catch (e) { io = null; ioT = []; }
  }
  function watch() {
    const vj = $('#v-judge'), vs = $('#v-set'), b = $('#ksBnr');
    const need = !document.hidden && ((!!b && !b.hidden && !!vj && !vj.hidden) || (!!vs && !vs.hidden && !!(liveBox() || $('#setKisekae .kspv'))));
    if (need && !lookT) lookT = setInterval(look, 1000);
    else if (!need && lookT) { clearInterval(lookT); lookT = 0; }
    if (need) observe();
  }
  document.addEventListener('click', () => { if (!lookT) return; setTimeout(look, 90); setTimeout(look, 700); }, true);
  // 窓の 出入り（body の すぐ 下の 要素が ふえる・へる・class／hidden／style が かわる）→ 次の コマで 見直す（＋0.35秒 あと：消える ときの うすく なる 動きの あと）。
  //   タップの ない 開き方・閉じ方も すぐ わかる（はじめの 画面が 自分で 消える・演出が 自分で 閉じる など：1秒ごとを 待たない）。見るのは body の 子 だけ（中の 動きでは よばれない）
  let lookRaf = 0;
  const lookSoon = () => { if (!lookT || lookRaf) return; lookRaf = requestAnimationFrame(() => { lookRaf = 0; look(); setTimeout(look, 350); }); };
  function kidsWatch() {
    try {
      const AT = { attributes: true, attributeFilter: ['class', 'hidden', 'style'] };
      const mo = new MutationObserver(recs => {
        recs.forEach(r => { if (r.type === 'childList') r.addedNodes.forEach(nd => { if (nd.nodeType === 1) mo.observe(nd, AT); }); });
        lookSoon();
      });
      mo.observe(document.body, { childList: true });
      Array.from(document.body.children).forEach(c => mo.observe(c, AT));
    } catch (e) { /* なし：1秒ごとと タップの あとで 見直す */ }
  }
  if (document.body) kidsWatch(); else document.addEventListener('DOMContentLoaded', kidsWatch);
  // ---------- コマ送りの 絵を なめらかに（第4.166版・まさちゃん 2026/11/13 15:21「海賊の壁紙カクカクするんだけど、他にもカクカクする物があれば見つけて！全部ヌルヌル動くようにして！」）----------
  //   壁紙の コマ送りの 絵（馬の シートを めくる）は 1コマ 1/30秒 ＝ 画面の 描きかえ（ふつう 1秒に 60回）の 2回ぶん。
  //   コマが かわる 時刻が 描きかえの 時刻と 重なると、ほんの 少しの ずれで「1回 だけ 出る コマ」と「3回 出る コマ」が まざって がたつく（コマは 30こ あっても なめらかに 見えない）。
  //   → 描きかえの 時刻を 10回 見て、コマが かわる 時刻（動きの はじまりから 1/60秒の きざみ）が 描きかえと 描きかえの ちょうど まん中に 来る ように、
  //     上の絵の 動いて いる アニメの はじまりを 少し（多くて 描きかえ 半回ぶん＝1/120秒）ずらす（Web Animations の startTime）。
  //     同じ ときに はじまって 同じ おくれの 動きは 同じ だけ ずれる ＝ たがいの そろい方は かわらない。もう まん中に 近い（2.5ミリ秒 まで）なら さわらない。
  //     止めて いる とき（.pause・.calm）と 止まって いる アニメは さわらない（止める／動かすは CSS の まま）。できない 端末・はかれない ときは なにも しない。
  //     絵を 出して すぐ（0.6秒・3秒 あと）と、また 動きだした とき、そのあとは 15秒ごとに 見直す
  let phRun = null, phT1 = 0, phT2 = 0, phIv = 0;
  function phase() {
    if (phRun) return phRun;
    // fin：この 関数の 中で もう 終わった（止めて いる・はかれない）。その ときは phRun に のこさない
    //   （のこすと、止めて いる ときに 1回 よばれた あと、動きだしても ずっと その「終わった 約束」を 返して 何も しなく なる）
    let fin = false;
    const pr = new Promise(res => {
      const done = v => { fin = true; phRun = null; res(v || null); };
      const b = $('#ksBnr'), tl = document.timeline;
      const idle = () => !b || b.hidden || b.classList.contains('pause') || b.classList.contains('calm') || document.hidden;
      if (idle() || !b.getAnimations || !tl || typeof requestAnimationFrame !== 'function') return done();
      const ts = [];
      const step = () => {
        const t = tl.currentTime;
        if (typeof t !== 'number' || idle()) return done();
        ts.push(t);
        if (ts.length < 10) return requestAnimationFrame(step);
        try {
          let sh = 0; for (let i = 1; i < ts.length; i++) if (ts[i] - ts[i - 1] < 11) sh++;
          // 描きかえの きざみ：1秒に 120回の 画面（11ミリ秒 より 短い 間かくが 9回中 3回 以上）なら 1/120秒、ほかは 1/60秒で 合わせる。
          //   1秒に 30回（省電力）でも、とちゅうで 描きかえが ぬけても、描きかえの 時刻は 1/60秒の きざみの 上に ある ので 同じ 合わせ方で よい
          //   第4.219版：前は いちばん 短い 間かく 1つで きめて いた → 重い 絵を 出した すぐ あとの 1回 だけの 短い 間かく（描きかえの おくれを とりもどす コマ）で
          //   60回の 画面を 120回と まちがえて、コマの かわる 時刻を 描きかえの 近くに おく ことが あった（見えなく なって また 見えた あとに 合わせ直す ことが ふえた ので）
          const P = sh >= 3 ? 1000 / 120 : 1000 / 60;
          let n = 0, moved = 0;
          for (const a of b.getAnimations({ subtree: true })) {
            if (a.playState !== 'running' || a.pending || typeof a.startTime !== 'number' || !a.effect) continue;
            const dl = +a.effect.getComputedTiming().delay || 0;
            const ph = (((t - a.startTime - dl) % P) + P) % P, off = ph - P / 2;
            n++;
            if (Math.abs(off) > 2.5) { a.startTime = a.startTime + off; moved++; }
          }
          done({ P: P, n: n, moved: moved });
        } catch (e) { done(); }
      };
      requestAnimationFrame(step);
    });
    if (!fin) phRun = pr;
    return pr;
  }
  function phaseSoon() {
    clearTimeout(phT1); clearTimeout(phT2);
    phT1 = setTimeout(phase, 600); phT2 = setTimeout(phase, 3000);
    if (!phIv) phIv = setInterval(phase, 15000);
  }
  async function apply(id, save) {
    if (!byId[id]) id = 'default';
    curId = id; setAttr(id); conf = ''; preArt(id);
    if (save !== false) {
      try { localStorage.setItem(KEY, id); } catch (e) { /* 覚えられなくてもOK */ }
      try { if (TL() && TL().putSetting) TL().putSetting(SETTING, { id: id }).catch(() => {}); } catch (e) { /* なし */ }
    }
    const my = loading = load(id);
    const p = await my;
    if (loading !== my || curId !== id) return;      // 途中で別のテーマにかわった
    payload = p;
    themeStyle(id === 'default' ? null : p); paintBnr(id === 'default' ? DEF : p);
    paint(); emit('apply');
  }
  // ---------- PUSHボタンの 絵（第4.148版・まさちゃん 2026/11/10 20:36「（画像は1枚だけもらって、「光る・へこむ・はじける」はコードで動かす）これがいいかも！」）----------
  //   テーマ 1つに 1まい（いつもの も）：一覧の pa＝{ f, w, h }（ファイル名・画面で 出す 大きさ：kisekae/push_art.py・build_kisekae.py）。
  //   テーマを 着せた ときに 先に 読んで おく（PUSH が 出る ときに もう 読めて いる）。読めた 絵 だけ fx.js に わたす ＝ 読めない ときは 今までの コードの PUSH
  const art = {};                                        // id → { src, w, h }（読めた）／ null（読めなかった）／ undefined（まだ）
  function preArt(id) {
    const t = byId[id], pa = t && t.pa;
    if (!pa || art[id] !== undefined || art['~' + id]) return;
    art['~' + id] = 1;                                   // 読んで いる とちゅう
    try {
      const im = new Image();
      im.onload = () => { const ok = im.naturalWidth > 0; const done = () => { art[id] = ok ? { src: pa.f, w: pa.w, h: pa.h } : null; delete art['~' + id]; }; if (ok && im.decode) im.decode().then(done, done); else done(); };
      im.onerror = () => { art[id] = null; delete art['~' + id]; };
      im.src = pa.f;
    } catch (e) { art[id] = null; delete art['~' + id]; }
  }
  // fx.js から：いまの テーマの PUSHボタンの 絵（読めて いる とき だけ）
  function pushArt(id) { const a = art[id || curId]; return a ? { src: a.src, w: a.w, h: a.h } : null; }
  // fx.js から：いまのテーマの 的中PUSH（面・押したあと・はじけるかけら）と ボードの飾り。いつもの・まだ読めていないときは null（＝いつもの形）
  function fx() {
    if (curId === 'default' || !payload) return null;
    return { tid: curId, pc: (payload.push && payload.push.pc) || '', push: payload.push || null, orn: (payload.board && payload.board.orn) || '' };
  }

  // ---------- 選ぶ画面（設定 › 着せ替え） ----------
  function card() {
    const set = $('#v-set'); if (!set || $('#setKisekae')) return;
    const c = document.createElement('div'); c.className = 'card setsec'; c.id = 'setKisekae'; c.style.marginBottom = 'var(--gap)';
    c.innerHTML = '<h2>着せ替え</h2><div class="ksbody"></div>';
    const after = $('#setMission');
    if (after && after.nextSibling) set.insertBefore(c, after.nextSibling); else if (after) set.appendChild(c); else set.insertBefore(c, set.firstChild);
    c.addEventListener('click', onClick);
    c.addEventListener('keydown', onKey);
    paint();
  }
  // 解放エフェクト（第4.60版：fx.js の TengelFx.unlock）：解放した 壁紙の タイルの 上で 金の 輪・つや・粒・「解放！」・チャイム
  function unlockFx(id) { try { const el = $(`#setKisekae .kst[data-ks="${id}"]`); if (el && window.TengelFx && window.TengelFx.unlock) window.TengelFx.unlock(el, { text: '解放！' }); } catch (e) { /* なし */ } }
  // 壁紙パックの テーマが 使える ように なるまでの レースの 数（買って いない なら -1）
  function packLeft(t) { const i = packInfo(); if (!i.owned) return -1; return Math.max(0, t.pack * (i.every || PK.every) - i.reads); }
  function lockLabel(t) {
    if (t.pack) { const k = packLeft(t); return `<span class="kslock pk">🔒 ${k < 0 ? esc(PK.name) : `あと${k}レース`}</span>`; }
    if (t.price) return `<span class="kslock">🔒 ${esc(pts(t.price))}</span>`;
    if (t.band) return `<span class="kslock">🔒 壁紙を${t.band}枚あつめると</span>`;
    return '';
  }
  // 選ぶ画面の 壁紙の 動き（第4.89版・まさちゃん「普段は壁紙は動かさないで、タップして選択しているときだけ壁紙が動くようにして！解放前、解放後どっちも！」）：
  //   タイルの 絵は ふだん 止まった 絵（牧場・ぷりけつの SVG も 止める）。タップして 選んだ タイル＝使用中（解放後）か 解放の 確認を 開いた タイル（解放前）だけ、
  //   判定タブの 上の絵と 同じ 動く 壁紙（ks_<id>.json の bnr）を 小さく 重ねて 動かす（.kslive › .kslv）。CSS は #ksBnr → #setKisekae .kslv に、@keyframes の 名前は kp を 足して、
  //   判定タブの 壁紙と ぶつからない ように（テーマどうしで 同じ 名前の @keyframes が ある）。設定タブが 見えていない 間は 止める（.pause）・控えめは .calm
  // 第4.218版：見本を 開いた タイル（pv）も 動かす（帯・壁紙パックの 待ちの タイルも タップで 動く）
  let pv = '';
  const liveId = () => conf || pv || curId;
  function liveStyle() {
    let st = $('#ksPrev');
    if (!st) { st = document.createElement('style'); st.id = 'ksPrev'; document.head.appendChild(st); }
    return st;
  }
  function rescope(id, bnr) {
    if (!pcache[id]) {
      const names = []; const re = /@keyframes (kb[\w-]+)/g; let m;
      while ((m = re.exec(bnr.css))) if (names.indexOf(m[1]) < 0) names.push(m[1]);
      names.sort((a, b) => b.length - a.length);
      let css = bnr.css.split('#ksBnr').join('#setKisekae .kslv'), html = bnr.html;
      names.forEach(n => { const rx = new RegExp('\\b' + n + '\\b', 'g'); css = css.replace(rx, 'kp' + n); html = html.replace(rx, 'kp' + n); });
      pcache[id] = { css: css, html: html };
    }
    return pcache[id];
  }
  function fitLive() {
    const w = $('#setKisekae .kst .kslive'); if (!w) return;
    const W = w.clientWidth || 118, H = w.clientHeight || 58;
    w.style.setProperty('--kss', Math.max(W / 390, H / 160).toFixed(4));
  }
  function motionLive() {
    const F = FX(), v = $('#v-set'), cm = !!(F && F.calm && F.calm()), ps = !!document.hidden || !!(v && v.hidden);
    const el = $('#setKisekae .kst .kslv'), lw = liveBox();
    const sl = !!lw && seen(lw, lw.closest('.kst')); SEEN.l = sl;      // 第4.219版：タイルが 画面の 外・ほかの 窓の 下なら 止める（上の seen）
    if (el) { el.classList.toggle('calm', cm); el.classList.toggle('pause', ps || !sl); }
    const pb = $('#setKisekae .kspv');                       // 第4.218版：見本も 同じ（控えめ＝.fxs.calm・設定タブが 見えて いない 間は 止める）
    const sp = !!pb && seen(pb); SEEN.p = sp;
    if (pb) { pb.classList.toggle('pause', ps || !sp); pb.querySelectorAll('.kspvw .fxs').forEach(s => s.classList.toggle('calm', cm)); }
    watch();
  }
  async function paintLive() {
    const id = liveId(), el = $('#setKisekae .kst .kslv'), st = liveStyle();
    if (!el || id === 'default') { st.textContent = ''; return; }
    const p = await load(id);
    if (liveId() !== id || el !== $('#setKisekae .kst .kslv')) return;     // 待つ 間に 変わった
    if (!p || !p.bnr || !p.bnr.html) { st.textContent = ''; el.innerHTML = ''; return; }
    const r = rescope(id, p.bnr);
    st.textContent = r.css; el.innerHTML = r.html; fitLive(); motionLive();
  }
  // ---------- 見本（第4.218版・まさちゃん 2026/11/24 18:55「①壁紙カスタム 壁紙を選ぶところでタップすると、pushボタンと結果ボードを表示されるようにして、見本みたいに見えるようにして！」）----------
  //   壁紙の タイルを タップすると（使う・解放の 確認・帯や 壁紙パックの 案内）、その 行の 下に その 壁紙の 的中の PUSH と 結果ボードを 小さく ならべる（.kspv）。
  //   絵は fx.js の TengelFx.sample（見本の 画面と 同じ 架空の レース・押せない）。PUSH と ボードの CSS は その テーマの ks_<id>.json の push・board（#ksPvFx：
  //   いまの テーマの #ksTheme と 同じく fx の CSS の あと ＝ 的中の 画面と 同じ 重なり。テーマごとに クラスが ちがう ので ぶつからない）。
  //   同じ タイルを もう一度 タップ・「閉じる」・ほかの タブへ 行くと 閉じる。控えめ・視差効果を減らす は 的中の 画面と 同じ 止め方（.fxs.calm）
  function pvHTML(t) {
    const nm = esc(t.name);
    return `<div class="kspv" role="group" aria-label="${nm}の見本">`
      + `<div class="kspvh"><span class="kspvt"><b>見本：${nm}</b><small>的中したときの PUSHボタンと 結果ボードだよ（架空のレース）</small></span>`
      + '<button class="btn ghost" type="button" data-ksact="pvx">閉じる</button></div><div class="kspvs">'
      + `<figure class="kspvf"><div class="kspvw" data-pvk="push" role="img" aria-label="${nm}の PUSHボタン"></div><figcaption>PUSHボタン</figcaption></figure>`
      + `<figure class="kspvf"><div class="kspvw" data-pvk="board" role="img" aria-label="${nm}の 結果ボード"></div><figcaption>結果ボード</figcaption></figure>`
      + '</div></div>';
  }
  function pvStyle() { let st = $('#ksPvFx'); if (!st) { st = document.createElement('style'); st.id = 'ksPvFx'; document.head.appendChild(st); } return st; }
  // 小さな 画面に 合わせる：幅で 縮める（--fxk）。ボードは ボードの まん中が 画面の まん中に 来る ように 上下に ずらす（--pvy：字が 読めて から もう一度）
  function fitPv() {
    document.querySelectorAll('#setKisekae .kspvw').forEach(w => {
      const st = w.querySelector('.fxs'); if (!st) return;
      const W = w.clientWidth; if (!(W > 0)) return;
      const k = W / 390; let y = 0;
      if (w.dataset.pvk === 'board') { const hb = st.querySelector('.hb'); if (hb && hb.offsetHeight) y = (422 - (hb.offsetTop + hb.offsetHeight / 2)) * k; }
      st.style.setProperty('--fxk', k.toFixed(4)); st.style.setProperty('--pvy', y.toFixed(1) + 'px');
    });
  }
  // PUSHボタンの 絵（第4.148版）が 読めるまで 待つ（読めた／読めなかった／絵の ない テーマ・長くても 2.5秒）
  function artWait(id) {
    preArt(id);
    const t0 = Date.now();
    return new Promise(res => { const tick = () => { if (art[id] !== undefined || !(byId[id] && byId[id].pa) || Date.now() - t0 > 2500) res(); else setTimeout(tick, 40); }; tick(); });
  }
  async function paintPv() {
    const id = pv, box = $('#setKisekae .kspv');
    if (!box || !id) { const st = $('#ksPvFx'); if (st) st.textContent = ''; return; }
    const r = await Promise.all([id === 'default' ? null : load(id), artWait(id)]), p = r[0];
    if (pv !== id || box !== $('#setKisekae .kspv')) return;            // 待つ 間に 変わった
    const F = FX(), t = byId[id];
    const th = p && p.push && p.push.pc ? { tid: id, pc: p.push.pc, push: p.push, orn: (p.board && p.board.orn) || '' } : null;
    if (!F || !F.sample || (id !== 'default' && !th)) { const s = $('.kspvs', box); if (s) s.innerHTML = '<p class="ptnote" style="margin:0;grid-column:1/-1">見本を 出せなかったよ</p>'; return; }
    pvStyle().textContent = th ? [(p.push && p.push.css) || '', (p.board && p.board.css) || ''].join('\n') : '';
    const s = F.sample(th, pushArt(id)), cm = s.calm ? ' calm' : '';
    const bg = t && t.thumb ? `<img class="kspvbg" src="${esc(t.thumb)}" alt="" decoding="async">` : '';
    const pw = $('[data-pvk=push]', box), bw = $('[data-pvk=board]', box);
    const col = themeBg(id);
    [pw, bw].forEach(w => { if (w && col) w.style.background = col; });
    if (pw) pw.innerHTML = bg + `<div class="fxs${cm}" inert aria-hidden="true">${s.push}</div>`;
    if (bw) bw.innerHTML = bg + `<div class="fxs${cm}" inert aria-hidden="true">${s.board}</div>`;
    fitPv(); motionLive();
    setTimeout(fitPv, 350);
    try { if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitPv); } catch (e) { /* なし */ }
  }
  // 見本が 見える ところまで 動かす：上の 帯（header.top：上に くっつく）と 下の タブ（.tabbar）の あいだに、タップした タイルの 行と 見本が
  //   ぜんぶ 入る なら はみ出した ぶん だけ（タイルが 上の 帯に かくれて いれば 下げる・見本が 下の タブに かくれて いれば 上げる）。入らない ときは 見本を ぜんぶ 見せる
  function pvScroll() {
    const p = $('#setKisekae .kspv'); if (!p) return;
    const t = p.previousElementSibling, hd = $('header.top'), tb = $('.tabbar');
    const v1 = (hd ? hd.getBoundingClientRect().bottom : 0) + 8;
    const v2 = (tb && getComputedStyle(tb).display !== 'none' ? tb.getBoundingClientRect().top : window.innerHeight) - 8;
    const pr = p.getBoundingClientRect(), a = t && t.classList.contains('kst') ? Math.min(t.getBoundingClientRect().top, pr.top) : pr.top, b = pr.bottom;
    let d = 0;
    if (b - a <= v2 - v1) { if (a < v1) d = a - v1; else if (b > v2) d = b - v2; }
    else if (b > v2) d = b - v2; else if (pr.top < v1) d = pr.top - v1;
    if (Math.abs(d) < 1) return;
    try { window.scrollBy({ top: d, behavior: 'smooth' }); } catch (e) { window.scrollBy(0, d); }
  }
  // その テーマの 画面の 地の 色（見本の うしろ：html[data-ks="<id>"] の --bg・いつもの は :root の --bg）。上に その 壁紙の 小さな 絵（判定タブの 上の 絵の かわり）
  const bgOf = {};
  function themeBg(id) {
    if (bgOf[id] !== undefined) return bgOf[id];
    let v = '';
    try {
      if (id !== 'default') { const m = A.css.match(new RegExp('html\\[data-ks="' + id + '"\\]\\{[^}]*?--bg:([^;}]+)')); v = m ? m[1].trim() : ''; }
      else {
        for (const sh of [...document.styleSheets]) {
          let rs = null; try { rs = sh.cssRules; } catch (e) { rs = null; }
          if (rs) for (const r of [...rs]) { if (!v && r.selectorText === ':root' && r.style && r.style.getPropertyValue('--bg')) v = r.style.getPropertyValue('--bg').trim(); }
          if (v) break;
        }
      }
    } catch (e) { v = ''; }
    return (bgOf[id] = /^[#\w(),.% -]+$/.test(v) ? v : '');
  }
  // 解放の 確認（第4.64版）：タップした カギの 壁紙の タイルの 中（カギの 下）に 出す。前は 一覧の 上に 1本の 帯で 出していた
  //   （2026/10/25 まさちゃん「赤のところは消して、解放されていない壁紙をタップしたら下に、解放、ボタンが出てくるようにして！」）。
  //   タイルは <div role="button">（中に 本物の ボタンを 置くため）。もう一度 タイルを タップすると 閉じる
  // トレーニングセンターの 壁紙チケット（第4.130版：お世話の 当たり 1/2400 → 第4.142版から 1/600）：1枚で 1つの テーマを 解放（ポイントは 使わない）
  const tickets = () => { try { return window.TCInfo ? window.TCInfo.tickets() : 0; } catch (e) { return 0; } };
  let actBusy = false;      // 解放の 途中（ポイント・チケット）：おわるまで 次の 解放を 受けない
  // 第4.141版（まさちゃん 11/10 15:52「壁紙チケット or 8000pにして！」→ 16:08「じゃあ7000pにして！」）：チケット 1枚は「壁紙の 解放」か「7,000P」かを 選べる。
  //   チケットが ある あいだ、着せ替えの カードの 上に 箱を 出す：壁紙に 使う ＝ カギの 壁紙を 押す（今までどおり）／ポイントに かえる ＝ ここの ボタン（2回 押して 決める）
  const TKP = () => (window.TengelPoints && window.TengelPoints.TICKET_POINTS) || 7000;
  let tkAsk = false;
  function ticketBox() {
    const n = tickets(); if (!(n > 0) || !wallet()) { tkAsk = false; return ''; }
    return `<div class="kstk" role="group" aria-label="チケット"><span class="kstx"><b>🎫 チケット ${n}枚</b><small>1枚で、<b>カギの壁紙を1つ解放</b>（壁紙を押してね）か、<b>${esc(pts(TKP()))}に変える</b>か、選べるよ</small></span>`
      + (tkAsk ? `<span class="kstb"><button class="btn primary" type="button" data-ksact="tkpt2">1枚を ${esc(pts(TKP()))}に 変える</button><button class="btn ghost" type="button" data-ksact="tkpt0">やめる</button></span>`
        : `<span class="kstb"><button class="btn" type="button" data-ksact="tkpt1">${esc(pts(TKP()))}に 変える</button></span>`) + '</div>';
  }
  // チケット 1枚 → 7,000P（獲得ポイント）。先に チケットを 1枚 使ってから 足す（足せなければ もどす）。上限を こえる ぶんは あずかりポイントへ（points_ui.js の grant）
  async function ticketToPoints() {
    const w = wallet(); if (actBusy || !w || typeof w.grant !== 'function' || !(tickets() > 0)) return false;
    actBusy = true;
    let ok = false, used = false;
    const held0 = typeof w.hold === 'function' ? w.hold().total : 0;
    try {
      try { used = !!window.TCInfo.useTicket(); } catch (x) { used = false; }
      if (used) { try { ok = await w.grant('tkp-' + Date.now().toString(36) + '-' + Math.floor(Math.random() * 1e6).toString(36), TKP(), 'チケットを ポイントに 変えた'); } catch (x) { ok = false; } }
      if (used && !ok) { try { window.TCInfo.backTicket(); } catch (x) { /* なし */ } }
    } finally { actBusy = false; }
    const held = (typeof w.hold === 'function' ? w.hold().total : 0) - held0;
    if (ok && !(held > 0)) toast(`🎫 チケット 1枚を ${pts(TKP())}に 変えたよ（合計 ${pts(w.total())}・チケット 残り ${tickets()}枚）`, 4200);      // あずかった ときは 財布の お知らせ（うち ○P は あずかったよ）が 出る
    else if (!ok) toast('チケットを ポイントに 変えられなかったよ', 3000);
    return ok;
  }
  function confBox(t, total) {
    if (t.pack) return packConf(t);
    const ok = total >= t.price;
    return `<span class="ksconf" role="group" aria-label="解放の確認"><span class="kscq">${esc(pts(t.price))}を使って解放する？<small>今 ${esc(pts(total))}</small></span>`
      + (ok ? `<button class="btn primary" type="button" data-ksact="unlock" data-id="${esc(t.id)}">解放する</button>`
        : `<span class="kscq muted">Pが足りないよ</span><button class="btn primary" type="button" data-gopt="points">ポイントを買う</button>`)
      + (tickets() > 0 ? `<button class="btn" type="button" data-ksact="ticket" data-id="${esc(t.id)}">🎫 チケットで解放（残り ${tickets()}枚）</button>` : '')
      + '<button class="btn ghost" type="button" data-ksact="cancel">やめる</button></span>';
  }
  // 壁紙パックの 買う／進み具合の 箱（組の 見出しの 下）・カギの タイルの 中の 買う 確認
  const packPrice = () => { try { const w = wallet(); if (w && w.pack) return w.pack.price(); } catch (e) { /* なし */ } return '1,500円'; };
  // 第4.114版：お得パック（壁紙パックと 結果ボードカスタムの セット 2,200円）：単品を どちらも 持って いない ときだけ 出す
  const bundleOffer = () => { try { const w = wallet(); return !!(w && w.bundle && w.bundle.offer()); } catch (e) { return false; } };
  const bundlePrice = () => { try { const w = wallet(); if (w && w.bundle) return w.bundle.price(); } catch (e) { /* なし */ } return '2,200円'; };
  function packName(no) { const id = PK.order[no - 1]; return id && byId[id] ? byId[id].name : ''; }
  function packBox() {
    const i = packInfo(), all = PK.order.length;
    if (!i.owned) {
      return '<div class="kspk"><div class="kspkt"><b>新しい壁紙 ' + all + '枚の パック</b><small>買い切り（1回 買えば ずっと）・ポイントでは 解放できないよ</small></div>'
        + `<button class="btn primary" type="button" data-ksact="pkbuy">${esc(packPrice())}で買う</button>`
        + (bundleOffer() ? `<div class="kspku"><span><b>お得パック</b><small>壁紙パックと 結果ボードカスタムの 2つが セット。別々に 買うより お得だよ</small></span><button class="btn primary" type="button" data-ksact="bundle">${esc(bundlePrice())}で買う</button></div>` : '')
        + `<p class="kspkn">買った 後に 読み込んだ レース ${PK.every}つごとに、上の 順に 1枚ずつ 使えるよ（${PK.every * all}レースで 全部）。帯の 壁紙の ミッションの 枚数にも 数えるよ。</p>`
        + '<div class="kspkr"><button class="btn ghost" type="button" data-ksact="pkrestore">購入を復元</button></div></div>';
    }
    const nx = i.next, w = Math.round(i.n / all * 100);
    return `<div class="kspk on"><div class="kspkt"><b>壁紙パック　解放 ${i.n}/${all}</b><small>${nx ? `次の「${esc(packName(nx.no))}」まで あと ${nx.left}レース（読み込み ${i.reads}レース）` : `${all}枚 全部 解放したよ！`}</small></div>`
      + `<div class="kspkb" aria-hidden="true"><i style="width:${w}%"></i></div></div>`;
  }
  function packConf(t) {
    const i = packInfo();
    if (i.owned) return '';
    return `<span class="ksconf" role="group" aria-label="壁紙パック"><span class="kscq">壁紙パックの 1枚だよ<small>${PK.order.length}枚 セット・${esc(packPrice())}（買い切り）</small></span>`
      + `<button class="btn primary" type="button" data-ksact="pkbuy">${esc(packPrice())}で買う</button>`
      + '<button class="btn ghost" type="button" data-ksact="cancel">やめる</button></span>';
  }
  // 使える ポイント（第4.139版：財布＋あずかりポイント＝上限まで。足りなければ 使う ときに あずかりから 補充される：points_ui.js の avail）
  const have = () => { const w = wallet(); return w ? (typeof w.avail === 'function' ? w.avail() : w.total()) : 0; };
  function paint() {
    const box = $('#setKisekae .ksbody'); if (!box) return;
    const cur = byId[curId] || byId.default, n = count(), total = have();
    let h = `<p class="hint" style="margin:0 0 4px">今のテーマ：<b>${esc(cur.name)}</b>。見た目だけが変わるよ。判定・記録・ポイントはそのまま。</p>`;
    h += `<p class="ptnote" style="margin:0">解放した壁紙：<b>${n}</b>/${A.paid.length + PK.order.length}枚（ポイント・壁紙パック。${[A.band.silver, A.band.golden, A.band.tengel].join('・')}枚で 帯の壁紙がミッションでもらえるよ）。解放した壁紙はずっと使えるよ（アプリを消すと消えるよ）。カギの壁紙をタップすると、その下に「解放する」が出るよ。壁紙をタップすると、的中したときのPUSHボタンと結果ボードの見本も出るよ。</p>`;
    h += ticketBox();
    const groups = [];
    A.themes.forEach(t => { let g = groups.find(x => x.name === t.group); if (!g) { g = { name: t.group, items: [] }; groups.push(g); } g.items.push(t); });
    groups.forEach(g => {
      h += `<h3 class="ksg">${esc(g.name)}<small>${g.items.length}</small></h3>` + (g.name === PK.name ? packBox() : '') + '<div class="ksgrid">';
      g.items.forEach(t => {
        const on = t.id === curId, can = usable(t.id), cf = conf === t.id && (!!t.price || (!!t.pack && !packInfo().owned)), lv = t.id === liveId() && t.id !== 'default';
        h += `<div role="button" tabindex="0" class="kst${on ? ' on' : ''}${can ? '' : ' lock'}${cf ? ' cf' : ''}${lv ? ' lv' : ''}" data-ks="${esc(t.id)}" aria-pressed="${on}" aria-expanded="${cf}" aria-label="${esc(t.name)}${on ? '（使用中）' : can ? '' : t.pack ? `（${esc(PK.name)}）` : t.price ? `（${pts(t.price)}で解放）` : `（壁紙を${t.band}枚あつめると）`}">`
          + `<img class="ksth" src="${esc(t.thumb)}" alt="" loading="lazy" decoding="async">`
          + (lv ? '<div class="kslive" aria-hidden="true"><div class="kslv"></div></div>' : '')
          + `<span class="ksn">${esc(t.name)}</span><span class="ksd">${esc(t.desc)}</span>`
          + (on ? '<span class="ksbadge">使用中</span>' : '') + (can ? '' : lockLabel(t)) + (cf ? confBox(t, total) : '') + '</div>'
          + (t.id === pv ? pvHTML(t) : '');                // 第4.218版：見本（タイルの すぐ あと・行の 下に 出る：dense）
      });
      h += '</div>';
    });
    h += '<p class="ptnote" style="margin-top:12px">馬番の枠の色は、どのテーマでも同じだよ（読み間違えないように）</p>'
      + '<div class="ksnums" aria-hidden="true">' + [1, 2, 3, 4, 5, 6, 7, 8].map(i => `<span class="num w${i}">${i}</span>`).join('') + '</div>';
    box.innerHTML = h;
    paintLive(); paintPv();
  }
  async function onClick(e) {
    const a = e.target.closest('[data-ksact]');
    if (a) {
      if (a.dataset.ksact === 'cancel') { conf = ''; pv = ''; paint(); return; }   // 第4.218版：見本も 閉じる
      if (a.dataset.ksact === 'pvx') { pv = ''; paint(); return; }                 // 第4.218版：見本の「閉じる」
      if (a.dataset.ksact === 'tkpt1') { tkAsk = true; conf = ''; paint(); return; }
      if (a.dataset.ksact === 'tkpt0') { tkAsk = false; paint(); return; }
      if (a.dataset.ksact === 'tkpt2') { a.disabled = true; await ticketToPoints(); tkAsk = false; paint(); return; }
      tkAsk = false;
      if (a.dataset.ksact === 'pkbuy' || a.dataset.ksact === 'pkrestore' || a.dataset.ksact === 'bundle') {
        const w = wallet(); if (!w || !w.pack) return;
        if (a.dataset.ksact === 'bundle') { if (w.bundle) await w.bundle.buy(a); } else if (a.dataset.ksact === 'pkbuy') await w.pack.buy(a); else await w.pack.restore(a);
        conf = ''; paint(); return;
      }
      if (a.dataset.ksact === 'ticket') {
        const id = a.dataset.id, t = byId[id]; if (!t || !wallet() || !(tickets() > 0)) return;
        // 第4.140版（抜け穴を ふさぐ）：チケットは 先に 1枚 使ってから 解放する（前は 解放の あとに 使った ので、2つの テーマを すばやく 押すと 1枚で 2つ 解放できた）。
        //   カギの ない テーマ・パックの テーマ・もう 解放した テーマには 使わない。解放できなかった ときは チケットを もどす
        if (actBusy || t.pack || !t.price || usable(id)) return;
        actBusy = true; a.disabled = true;
        let ok = false, used = false;
        try {
          try { used = !!window.TCInfo.useTicket(); } catch (x) { used = false; }
          if (used) { try { ok = await wallet().unlock('theme:' + id, 0); } catch (x) { ok = false; } }
          if (used && !ok) { try { window.TCInfo.backTicket(); } catch (x) { /* なし */ } }
        } finally { actBusy = false; }
        conf = '';
        if (ok) { toast(`🎫 チケットで「${t.name}」を解放したよ（残り ${tickets()}枚）`, 3600); emit('unlock'); await apply(id, true); unlockFx(id); }
        else { toast('チケットで 解放 できなかったよ', 3000); paint(); }
        return;
      }
      if (a.dataset.ksact === 'unlock') {
        const id = a.dataset.id, t = byId[id]; if (!t || !wallet() || actBusy) return;
        actBusy = true; a.disabled = true;
        let ok = false;
        try { ok = await wallet().unlock('theme:' + id, t.price); } catch (x) { ok = false; } finally { actBusy = false; }
        conf = '';
        if (ok) { toast(`✅ 「${t.name}」を解放したよ（残り ${pts(wallet().total())}）`, 3600); emit('unlock'); await apply(id, true); unlockFx(id); }
        else { toast(`Pが足りないよ（${pts(t.price)}いる・今 ${pts(have())}）`, 3600); paint(); }
        return;
      }
    }
    if (e.target.closest('.ksconf')) return;          // 確認の 文字の 所を 押しても 何も しない
    const b = e.target.closest('.kst'); if (!b) return;
    const id = b.dataset.ks, t = byId[id]; if (!t) return;
    // 第4.218版：タップした 壁紙の 見本（PUSH と 結果ボード）を その 行の 下に 出す。見本が 開いて いる タイルを もう一度 タップすると 閉じる
    const was = pv === id;
    if (id === curId) { pv = was ? '' : id; conf = ''; paint(); if (pv) pvScroll(); return; }   // 使用中の タイル：見本を 開く／閉じる（前は 何も しなかった）
    if (usable(id)) { pv = id; await apply(id, true); toast(`「${t.name}」に着せ替えたよ`); pvScroll(); return; }
    if (t.pack) {
      const k = packLeft(t);
      if (k >= 0) { toast(`あと ${k}レース 読み込むと「${t.name}」が使えるよ（${PK.every}レースごとに 1枚）`, 3600); pv = was ? '' : id; conf = ''; paint(); if (pv) pvScroll(); return; }
      if (conf === id) { conf = ''; pv = ''; paint(); return; }
      conf = id; pv = id; paint();
      const c = $('#setKisekae .kst.cf'); if (c) c.scrollIntoView({ block: 'nearest' });
      pvScroll();
      return;
    }
    if (t.price) {
      if (conf === id) { conf = ''; pv = ''; paint(); return; }   // もう一度 タップ → 閉じる（見本も）
      conf = id; pv = id; paint();
      const c = $('#setKisekae .kst.cf'); if (c) c.scrollIntoView({ block: 'nearest' });
      pvScroll();
      return;
    }
    if (t.band) { toast(`壁紙を${t.band}枚あつめて、ミッションで受け取ると使えるよ（今 ${count()}枚）`, 3600); pv = was ? '' : id; conf = ''; paint(); if (pv) pvScroll(); }
  }
  // タイルは <div role="button">：Enter か スペースで 押す
  function onKey(e) {
    if (e.key !== 'Enter' && e.key !== ' ') return;
    const b = e.target.closest('.kst'); if (!b || e.target !== b) return;
    e.preventDefault(); b.click();
  }

  // ---------- 起動 ----------
  css();
  let saved = 'default', lost = false;
  try { saved = localStorage.getItem(KEY) || 'default'; } catch (e) { saved = 'default'; }
  if (!byId[saved]) { saved = 'default'; lost = true; }      // 一覧に ない テーマ（第4.147版で 外した 壁紙 など）→ いつもの（下で 覚え直す）
  setAttr(saved); curId = saved;             // 色は起動の瞬間から（絵とPUSHは読めてから）
  const ready = (async () => {
    card();
    await apply(saved, false);
    try {
      if (TL() && TL().ready) {
        await TL().ready; const s = TL().getSetting ? await TL().getSetting(SETTING) : null;
        if (s && s.id && !byId[s.id]) lost = true;      // 設定の DB に 一覧に ない テーマ（外した 壁紙）が 残って いる → 下で 覚え直す
        else if (s && s.id && s.id !== curId) await apply(s.id, false);
      }
    } catch (e) { /* 設定が読めないときは localStorage のまま */ }
    try { if (wallet() && wallet().ready) await wallet().ready; } catch (e) { /* なし */ }
    if (!usable(curId)) await apply('default', true);   // 解放していないテーマが残っていたら いつものに
    else if (lost) await apply(curId, true);            // 外した 壁紙を 使って いた → いまの テーマ（ふつうは「いつもの」）を 覚え直す（端末と 設定の DB）
    paint();
  })();
  document.addEventListener('tengel:wallet', () => { paint(); if (!usable(curId)) apply('default', true); });
  document.addEventListener('tengel:tc', () => { tkAsk = false; paint(); });      // トレーニングセンターを とじた（チケットの 数が かわった かも：第4.141版）
  // 壁紙パック（第4.92版）：解放の お知らせ（読み込んだ とき：画面の 上に 小さな 絵と「着せ替える」・6.5秒）・買った／もどした・返金
  function packNote(id, many) {
    const t = byId[id]; if (!t) return;
    const old = $('#ksNote'); if (old) old.remove();
    const n = document.createElement('div'); n.id = 'ksNote'; n.setAttribute('role', 'status');
    n.innerHTML = (t.thumb ? `<img src="${esc(t.thumb)}" alt="">` : '') + `<span><b>🎉 新しい壁紙「${esc(t.name)}」</b>${many > 1 ? `壁紙パックの ${many}枚が 使えるように なったよ` : '壁紙パックの 壁紙が 使えるように なったよ'}</span>`
      + `<button type="button" class="btn primary" data-ksnote="${esc(id)}">着せ替える</button>`;
    document.body.appendChild(n);
    // 第4.168版：結果ボードの 解放の お知らせ（#bcNote：同じ 所に 出る）が 出て いる ときは その 下に（同じ レースで 両方 解放された とき、字が 重なって いた）
    try { const o = document.getElementById('bcNote'); if (o && o.offsetHeight) n.style.top = (o.offsetTop + o.offsetHeight + 8) + 'px'; } catch (e) { /* なし */ }
    n.addEventListener('click', async ev => { if (!ev.target.closest('[data-ksnote]')) return; n.remove(); await apply(id, true); toast(`「${t.name}」に着せ替えたよ`); });
    setTimeout(() => { if (n.parentNode) n.remove(); }, 6500);
  }
  document.addEventListener('tengel:wallpack', e => {
    const d = (e && e.detail) || {};
    if (d.phase === 'unlock' && d.no) {
      const id = PK.order[d.no - 1];
      paint();
      if (id && byId[id]) { packNote(id, d.many || 1); unlockFx(id); }
      return;
    }
    if (d.phase === 'owned' || d.phase === 'refund') { conf = ''; paint(); if (!usable(curId)) apply('default', true); }
  });
  document.addEventListener('tengel:tab', e => {
    if (e.detail !== 'set' && pv) {                         // 第4.218版：ほかの タブへ 行ったら 見本は 閉じる（もどった ときは 閉じた 形で 描き直す）
      pv = ''; const p = $('#setKisekae .kspv'); if (p) p.remove();
      const st = $('#ksPvFx'); if (st) st.textContent = '';
    }
    if (e.detail === 'set') { card(); paint(); try { const w = wallet(); if (w && w.pack && !packInfo().owned) w.pack.products().then(paint).catch(() => {}); } catch (x) { /* なし */ } }
    motion(); motionLive(); if (e.detail === 'judge') fitBnr();
  });
  document.addEventListener('tengel:fx', e => { if (e.detail && e.detail.phase === 'settings') { motion(); motionLive(); } });
  document.addEventListener('visibilitychange', () => { motion(); motionLive(); });
  window.addEventListener('resize', () => { fitBnr(); fitLive(); fitPv(); if (lookT) look(); });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', card);

  window.TengelKisekae = {
    on: true, ready: ready, list: () => A.themes.slice(), current: () => curId, apply: id => apply(id, true), usable: usable, unlocked: unlocked, count: count, fx: fx, pushArt: pushArt,
    loaded: () => curId === 'default' || !!payload, band: Object.assign({}, A.band), paid: A.paid.slice(), motion: motion, phase: phase, live: liveId, pv: () => pv, pack: () => Object.assign({ ids: PK.ids.slice(), order: PK.order.slice() }, packInfo())
  };
})();
