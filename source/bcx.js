// ===== 結果ボードカスタム（App Store版・第4.91版・まさちゃんの 指定 2026-10-28／第4.113版で 16こ・的中と ハズレの 2つ／第4.120版で 15こ／第4.121版で 1〜14 に まさちゃんの 絵の ボード）=====
//   買い切り 1,500円（第4.114版：2,200円 → 1,500円・まさちゃんの 指定。App内課金の 非消耗型 jp.tengel.app.boardcustom。壁紙パックと セットの お得パック jp.tengel.app.bundle1 2,200円 も ある）。買った あとに 読み込んだ レースの 数で 16こを 番号の 順に 解放（points.js の BOARD：6レースごとに 1つ）。
//   第4.113版（まさちゃん 2026/11/01 01:13「結果ボードカスタム、最後のボードを持つ馬以外一度全部消して！全部で16個(ボードを持つ馬を含む)にする！
//     15個は、デザインは仕組みはできているから準備ができたら教えて！送っていく！」）：前の 1〜21（ボードを一周〜出世馬・幻の 馬）は 消した。
//     1〜15 は じゅんび中（まさちゃんの デザインが とどいたら 入れる）・16「ボードを持つ馬」（第4.120版から 15：1〜14 は じゅんび中）（いちばん はじめの 頃の 馬：絵は kisekae/r3d/fx/board_horse_parts.py の 部品 5まい。
//     ない とき（CI）は SVG の 馬）
//   第4.113版（まさちゃん 01:24「結果ボードのカスタムには2種類カスタムつけられるようにして！①的中演出 ②ハズレ演出 これで、的中とハズレのどっちもカスタムできる。」）：
//     設定の「結果ボードカスタム」で 的中の とき（的中・デカ的中・ど的中 など ぜんぶの 的中）・ハズレの とき に べつべつに 1つずつ 選ぶ（points_ui.js の board.selHit・selMiss）
//   飾りを 入れる 手順（README「結果ボードカスタムに 飾りを 入れる」）：points.js の BOARD_ITEMS の その 番号の null を [id, 名前, せつめい, when] に かえる →
//     ここに B.<id>（o を うけとって { html, css, enter, start, go, thumb } を かえす）・その CSS（CSS の 配列）・音（snd）を 足す → テスト
//   作る ときの きまり：ボードの 数字と 見出しには 飾りを 重ねない／飾りの 馬は うすい ふち取りと 影（.bco）／リボンや 旗の 色は テーマの アクセント色（--bcA）／
//   大きく 動くのは 出てくる ときだけ（1秒で ピタッと 止める）／「とじる」は 動かさない（ボードの 外の 部品）／視差効果を減らす・演出を控えめ・的中エフェクト オフは 動かさない（.bcst）
//   fx.js が 結果の 画面（reveal）を 出した ときに TengelBoard.decorate(舞台, { kind, quiet, calm, spec }) を 呼ぶ。ボード（.rb）の 入れもの .hb の 中に 部品を 入れる
//   （.bcx.bk＝ボードの うしろ・.bcx＝ボードの 前）。ボードが 出おわった（.hb の 登場の アニメーションが おわった）ら .bcgo を つけて 動きはじめる
//   音：fx.js の Web Audio（TengelFx.audio()）で その場で 作る（ファイルは 使わない）。効果音 オフ なら 鳴らさない
(function () {
  'use strict';
  if (!window.__NATIVE) return;
  const A = window.TengelBoardArt, PT = window.TengelPoints;
  if (!A || !PT || !PT.BOARD_ITEMS) return;
  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const f = A.f, PAL = A.PAL;
  const ITEMS = PT.BOARD_ITEMS, BY = {};
  ITEMS.forEach(it => { BY[it.id] = it; });
  const WL = () => (window.TengelWallet && window.TengelWallet.on ? window.TengelWallet : null);
  const FX = () => window.TengelFx || null;
  const FXA = () => (window.__FX && window.__FX.assets) || {};
  const BIG = { big: 1, fz: 1, nd: 1, sd: 1, pc: 1, sgd: 1, spg: 1, gk: 1 };   // 第4.117版：神様極的中も
  const CLOSE_TOP = 734;          // 舞台（390×844）の「とじる」の 上の はし
  const HB_TOP = 196;             // ボード（.hb）の 上の はし
  const KIND = { hit: '的中', miss: 'ハズレ' };   // 選ぶ 所（的中の とき・ハズレの とき）
  let uid = 0;

  // ---------- CSS（いつも 同じ 分） ----------
  const OL = 'filter:drop-shadow(0 0 1px rgba(255,255,255,.95)) drop-shadow(0 0 .7px rgba(255,255,255,.95)) drop-shadow(0 3px 3px rgba(0,0,0,.34))';
  const CSS = [
    '.fxs .hb .bcx{position:absolute;z-index:3;pointer-events:none}.fxs .hb .bcx.bk{z-index:-1}.fxs .hb .bcx svg{display:block;width:100%;height:100%;overflow:visible}',
    `.fxs .hb .bco{${OL}}`,
    // 動かさない（視差効果を減らす・控えめ・静か）
    '.fxs .hb.bcst .bcx,.fxs .hb.bcst .bcx *,.fxs .hb.bcst .rb{animation:none!important;transition:none!important}',
    // まばたき（SVG の 馬の 目 .bcbl）
    '.fxs .hb.bcgo .bcbl{animation:bcBlink 4.6s infinite}@keyframes bcBlink{0%,91%,100%{transform:scaleY(1)}94%{transform:scaleY(.1)}}',
    // 15 ボードを持つ馬（第4.119版までは 16）：下から ボードを かかえて 出てくる（1秒・着地で 少し はずむ）→ 頭と首・後ろ足が ぷるぷる（別々の 速さ）・しっぽを ときどき ふる・まばたき
    '.fxs .hb .bcx img{display:block;width:100%;height:100%;-webkit-user-drag:none;user-select:none}',
    '.fxs .hb.bce-carry{animation-name:bcECarry!important;animation-duration:1s!important;animation-timing-function:linear!important;transform-origin:50% 100%}',
    '@keyframes bcECarry{0%{opacity:1;transform:translateY(660px);animation-timing-function:cubic-bezier(.18,.72,.36,1)}46%{transform:translateY(-16px);animation-timing-function:ease-in}'
      + '60%{transform:translateY(0) scale(1.03,.95);animation-timing-function:ease-out}74%{transform:translateY(-5px) scale(.99,1.02);animation-timing-function:ease-in}86%{transform:translateY(0) scale(1.01,.99)}100%{opacity:1;transform:none}}',
    '.fxs .hb.bcgo .bc-hbh{animation:bcHbH 3.1s linear infinite,bcHbJ 1.4s linear 1.5s 1 none}.fxs .hb.bcgo .bc-hbl{animation:bcHbL 2.3s linear infinite -.7s,bcHbS .85s linear 1.5s 1 none}',
    '.fxs .hb.bcgo .bc-hbt{animation:bcHbT 7.9s ease-in-out infinite .6s}.fxs .hb .bc-hbe{opacity:0}.fxs .hb.bcgo .bc-hbe{animation:bcHbE 5.3s linear infinite .5s}',
    // 15：1回だけ ボードを 落としそうに なって あせる（出おわって 1.5秒後・1.4秒：ずり落ちる → 頭が びくっ・目を 見ひらく・汗・後ろ足が じたばた → 持ち直す → ふぅ）。
    //   まさちゃん「あと一回ボード落としそうになって焦るエフェクト追加して！」（大きく 動くのは 出てくる ときだけ の きまりの 例外：まさちゃんの 指定の 1回だけの 動き）。前足は ボードと いっしょに 動く
    '.fxs .hb.bcgo.bcx-carry .rb{transform-origin:273px 0;animation:bcHbSlip 1.4s linear 1.5s 1 none}.fxs .hb.bcgo .bc-hbf{animation:bcHbSlip 1.4s linear 1.5s 1 none}',
    '.fxs .hb .bc-hbw,.fxs .hb .bc-hbx,.fxs .hb .bc-hbp,.fxs .hb .bc-hbd i{opacity:0}.fxs .hb.bcgo .bc-hbw{animation:bcHbW 1.4s linear 1.5s 1 none}',
    '.fxs .hb.bcgo .bc-hbx{animation:bcHbX .95s linear 1.55s 1 none}.fxs .hb.bcgo .bc-hbp{animation:bcHbP .8s ease-out 2.55s 1 none}',
    '.fxs .hb .bc-hbd i{position:absolute;width:7px;height:10px}.fxs .hb.bcgo .bc-hbd i{animation:bcHbD .75s cubic-bezier(.2,.7,.4,1) var(--d) 1 none}',
    hbCss(),
    // 前足（.bc-hbf）の 白い ふちと 影は 絵の 中（胸の 前と ボードの うしろへ 入る 切り口には 白い ふちを つけない ため：CSS の .bco は つけない）
    '.fxs .hb:not(.bchbv) .bc-hbsv,.fxs .hb.bchbv .bc-hbr{display:none}',
    // ためし（設定の「▶ 見る」：TengelFx.preview）は PUSH を 押して いないので、押された PUSH と はじける 絵は 出さない
    '#fxOv.pv .ov > .pressed,#fxOv.pv .ov > .clips{display:none!important}',
    // 解放の お知らせ（画面の 上）
    '#bcNote{position:fixed;left:50%;top:calc(var(--sat,0px) + 10px);z-index:80;transform:translateX(-50%);max-width:92vw;padding:9px 16px 10px;border-radius:14px;background:linear-gradient(180deg,#FFF8DC,#FFE7A3);color:#4A3206;',
    'font:700 13.5px/1.45 "BIZ UDPGothic",sans-serif;box-shadow:0 0 0 2px #FFFFFF,0 8px 22px rgba(0,0,0,.28);pointer-events:none;animation:bcNote 4.2s ease-out both;text-align:center}',
    '#bcNote b{display:block;font-family:"Dela Gothic One","BIZ UDPGothic",sans-serif;font-weight:400;font-size:15px;color:#B0141B}',
    '@keyframes bcNote{0%{opacity:0;transform:translate(-50%,-14px)}8%{opacity:1;transform:translate(-50%,0)}86%{opacity:1}100%{opacity:0;transform:translate(-50%,-8px)}}',
    '@media (prefers-reduced-motion:reduce){#bcNote{animation:bcNoteC 4.2s linear both}}@keyframes bcNoteC{0%{opacity:0}6%{opacity:1}90%{opacity:1}100%{opacity:0}}'
  ].join('\n');
  // 小さな 見本（設定の タイル .bcmini）にも 同じ 形を 使う（動かさない .bcst）
  const CSS_ALL = CSS.split('.fxs .hb').join(':is(.fxs,.bcmini) .hb');
  function css() {
    if ($('#bcxCss')) return;
    const st = document.createElement('style'); st.id = 'bcxCss'; st.textContent = CSS_ALL + '\n' + UI_CSS + '\n' + PIC_CSS; document.head.appendChild(st);
  }
  function dynCss(txt) {
    let st = $('#bcxDyn'); if (!st) { st = document.createElement('style'); st.id = 'bcxDyn'; document.head.appendChild(st); }
    st.textContent = txt || '';
  }

  // ---------- 部品 ----------
  // 箱（ボードの 左上が 0,0）に SVG を 入れる。cls：bk（うしろ）・bco（ふち取りと 影）など
  function box(cls, x, y, w, h, vb, inner, style) {
    return `<div class="bcx ${cls}" style="left:${f(x)}px;top:${f(y)}px;width:${f(w)}px;height:${f(h)}px;${style || ''}"><svg viewBox="${vb}" preserveAspectRatio="xMidYMid meet" aria-hidden="true">${inner}</svg></div>`;
  }
  const neckVB = '-5 -8 110 125';                             // 前から 見た 頭と 首（bcx_art.js の front）

  // ---------- 15こ（第4.120版）：部品を 作る ----------
  //   B.<id>(o)：o＝{ H（ボードの 高さ）, W（350）, sp（ボードの 下の すき間）, st（動かさない）, miss（ハズレ）, big（デカ的中から 上）, kind（結果の 種類）, dark（暗い ボード）,
  //     title（見出しの 字の 場所：ボードの 左上からの px）, redHd（見出しが 赤）, streak（連続的中の 数）, u（毎回 ちがう 番号：CSS の 名前に）}
  //   かえす もの：{ html（.hb に 入れる 部品）, css（その 時だけの CSS）, enter（登場の しかた：.hb に .bce-<名前>）, start（ボードが 出はじめた とき）, go（出おわった とき）,
  //     thumb（設定の 小さな 見本だけの { html, style }：動きの しるし など）}。1〜14 は 絵の ボード（第4.121版：下の「絵の ボード」。B には しるしだけ）
  const B = {};
  // 15 ボードを持つ馬（第4.120版から 15 番・第4.108版・まさちゃんの 指定）：いちばん はじめの 頃の 馬。うしろから ボードを かかえて 下から 出てくる（着地で 少し はずむ）
  //   → 頭と首・後ろ足が ぷるぷる（重い ボードを 持って ふんばる：別々の 速さ）・しっぽを ときどき ふる・まばたき。前足（ボードの 上の ふちに かかる 短い 足と ひづめ）は 動かさない
  //   形は はじめの 絵（board_horse.py）と 同じ（まさちゃん 23:19・23:21「胴体の長さも2枚目の長さがベスト！」「二枚目くらいの前脚の長さが理想！」）
  //   絵 5まい（kisekae/r3d/fx/board_horse_parts.py。四角は その HBX と 同じ：頭と首・前足・目＝ボードの 左上から／後ろ足・しっぽ＝左下から の px。
  //   ボードの 高さが かわっても 上の 部品は 上の ふち・下の 部品は 下の ふちに つく）。頭と首・後ろ足・しっぽ＝ボードの うしろ（.bk）・前足＝ボードの 前
  //   絵が 読めない とき（絵なしの CI など）は SVG の 馬（.hb に .bchbv：hbVec）
  const HBX = { head: [196, -145, 128, 175], fore: [136, -34, 107, 63], hind: [242, -30, 100, 120], tail: [314, -46, 33, 90], eye: [248, -124, 26, 26], headO: [272, 9], hindO: [292, -21], tailO: [327, -64],
    eyeC: [261, -111], muzzle: [211, -67], poll: [267, -116] };
  const HBA = { head: 'bcxhbh', fore: 'bcxhbf', hind: 'bcxhbl', tail: 'bcxhbt', eye: 'bcxhbe' };
  B.carry = o => {
    const as = FXA(), H = o.H;
    const at = (k, bot) => { const b = HBX[k]; return { x: b[0], y: bot ? H + b[1] : b[1], w: b[2], h: b[3] }; };
    const org = (k, pv, bot) => { const b = at(k, bot), q = HBX[pv]; return `${f(q[0] - b.x)}px ${f((bot ? H + q[1] : q[1]) - b.y)}px`; };
    const pos = r => `left:${f(r.x)}px;top:${f(r.y)}px;width:${f(r.w)}px;height:${f(r.h)}px`;
    const ok = Object.keys(HBA).every(k => as[HBA[k]]);
    let html = '';
    if (ok) {
      // 前足（第4.112版・09:50「蹄で持つんじゃなくて、関節で挟んでるようにして」）：関節（球節）で ボードの 上の ふちを はさむ 形＝つなぎと ひづめは ボードの 前の 面に おしつく
      //   （第4.110版と 同じ 場所。白い 輪や 見出しの 上の 帯に かかるのは つなぎと ひづめ だけ。見出しの 字とは 3px 以上 あく）
      //   10:38「ボードに脚の線が被ってるか、被ってないかのちがい」：絵は 白い 輪の いちばん 上（的中・大的中 3px）で 切って ある。ハズレは 輪が 1.5px なので 1.5px 下げて 切り目を 輪の 上に 合わせる
      const src = k => esc(as[HBA[k]]), h = at('head'), e = at('eye'), fo = at('fore');
      if (o.miss) fo.y += 1.5;
      html += `<div class="bcx bk bco bc-hbr bc-hbt" style="${pos(at('tail', 1))};transform-origin:${org('tail', 'tailO', 1)}"><img class="bchbi" src="${src('tail')}" alt=""></div>`
        + `<div class="bcx bk bco bc-hbr bc-hbl" style="${pos(at('hind', 1))};transform-origin:${org('hind', 'hindO', 1)}"><img class="bchbi" src="${src('hind')}" alt=""></div>`
        + `<div class="bcx bk bco bc-hbr bc-hbh" style="${pos(h)};transform-origin:${org('head', 'headO')}"><img class="bchbi" src="${src('head')}" alt="">`
        + `<img class="bchbi bc-hbe" src="${src('eye')}" alt="" style="position:absolute;left:${f(e.x - h.x)}px;top:${f(e.y - h.y)}px;width:${f(e.w)}px;height:${f(e.h)}px">${hbPanic(h)}</div>`
        + `<div class="bcx bc-hbr bc-hbf" style="${pos(fo)};transform-origin:${f(273 - fo.x)}px ${f(-fo.y)}px"><img class="bchbi" src="${src('fore')}" alt=""></div>`;
    }
    html += hbVec(o, ok);
    return { html, enter: 'carry', start: () => setTimeout(() => snd('thump'), 470),
      go: hb => { if (o.st) return; setTimeout(() => { if (hb.isConnected) snd('slip'); }, 1500); setTimeout(() => { if (hb.isConnected) snd('phew'); }, 2560); } };
  };
  // 15：あせる 所の 部品（頭と首の 入れもの の 中：頭と いっしょに 動く）。見ひらいた 目（白目＋小さな 黒目）・汗 3つ・「！」の 形・鼻の 息（ふぅ）
  function hbPanic(h) {
    const q = HBX, ec = q.eyeC, mz = q.muzzle, pl = q.poll, rel = (x, y) => [f(x - h.x), f(y - h.y)];
    const [ex, ey] = rel(ec[0], ec[1]), [mx, my] = rel(mz[0] - 7, mz[1] - 1), [px, py] = rel(pl[0], pl[1]);
    let s = `<div class="bc-hbw" style="position:absolute;left:${f(+ex - 11)}px;top:${f(+ey - 11)}px;width:22px;height:22px"><svg viewBox="-11 -11 22 22" aria-hidden="true"><circle r="8.8" fill="#FFFFFF" stroke="#4A2614" stroke-width="1.3"/>`
      + '<circle cx="-1.2" cy="-.4" r="3.1" fill="#1A1008"/><circle cx="-2.2" cy="-1.6" r="1.1" fill="#FFFFFF"/></svg></div>';
    const drop = '<svg viewBox="-3.5 -5.5 7 10" aria-hidden="true"><path d="M0 -5 C2.6 -1.4 3.2 .6 3.2 1.6 C3.2 3.4 1.8 4.4 0 4.4 C-1.8 4.4 -3.2 3.4 -3.2 1.6 C-3.2 .6 -2.6 -1.4 0 -5 Z" fill="#8FD8FF" stroke="#2F6FA8" stroke-width=".9"/><path d="M-1.4 .4 C-1.4 -.8 -.8 -1.8 -.2 -2.4" stroke="#FFFFFF" stroke-width=".9" fill="none" stroke-linecap="round"/></svg>';
    s += `<div class="bc-hbd" style="position:absolute;left:${px}px;top:${py}px;width:0;height:0">`
      + [[-14, -6, -12, -10, -24, 1.6], [2, -14, 6, -15, 12, 1.68], [12, -4, 15, -7, 30, 1.76]].map(([x, y, dx, dy, r, d]) => `<i style="left:${x}px;top:${y}px;--x:${dx}px;--y:${dy}px;--r:${r}deg;--d:${d}s">${drop}</i>`).join('') + '</div>';
    s += `<div class="bc-hbx" style="position:absolute;left:${f(+px + 22)}px;top:${f(+py - 30)}px;width:12px;height:24px;transform-origin:50% 100%"><svg viewBox="0 0 12 24" aria-hidden="true"><rect x="3.2" y="1" width="5.6" height="14.5" rx="2.8" fill="#FFE27A" stroke="#B0141B" stroke-width="1.4"/><circle cx="6" cy="20.4" r="2.9" fill="#FFE27A" stroke="#B0141B" stroke-width="1.4"/></svg></div>`;
    s += `<div class="bc-hbp" style="position:absolute;left:${f(+mx - 9)}px;top:${f(+my - 7)}px;width:18px;height:14px"><svg viewBox="-9 -7 18 14" aria-hidden="true">${A.puff(5.5)}</svg></div>`;
    return s;
  }
  // 15 の 絵が ない とき：SVG の 馬（頭と首は ボードの うしろ・ひづめは 上の ふちに かける・下は 後ろ足と しっぽ）。hidden＝ふだんは かくす（絵が 読めない ときに 出す）
  function hbVec(o, hidden) {
    const c = PAL.chestnut, w = 92, h = w * 125 / 110, top = -2 - (97 + 8) / 125 * h, lh = 70;
    let s = `<div class="bcx bk bco bc-hbh" style="left:${f(268 - w / 2)}px;top:${f(top)}px;width:${w}px;height:${f(h)}px;transform-origin:50% 100%"><svg viewBox="${neckVB}">${A.front(c, { expr: 'smile', neck: true, blink: true })}</svg></div>`;
    s += box('bco bc-hbf', 229, -10, 26, 22, '-13 -11 26 22', `<g transform="rotate(-6)">${A.hoof(c, 0, 9, 0, 9, 11)}</g>`, 'transform-origin:44px 10px');   // SVG の 馬の 胸の 前
    s += box('bco bc-hbf', 258, -10, 26, 22, '-13 -11 26 22', `<g transform="rotate(5)">${A.hoof(c, 0, 9, 0, 9, 11)}</g>`, 'transform-origin:15px 10px');
    s += `<div class="bcx bk bco bc-hbl" style="left:246px;top:${f(o.H - 14)}px;width:100px;height:${f(lh + 14)}px;transform-origin:50% 0"><svg viewBox="0 -14 100 ${f(lh + 14)}" preserveAspectRatio="none">`
      + `<g class="bc-hbt" style="transform-origin:84px -6px"><path d="M80 -8 C90 ${f(lh * .3)} 92 ${f(lh * .65)} 88 ${f(lh * .95)} C84 ${f(lh * .7)} 80 ${f(lh * .45)} 74 -8 Z" fill="${c.n}"/></g>`
      + `<path d="M22 -14 L40 -14 L38 ${f(lh - 8)} L24 ${f(lh - 8)} Z" fill="${c.b}"/><path d="M56 -14 L74 -14 L72 ${f(lh - 8)} L58 ${f(lh - 8)} Z" fill="${c.s}"/>`
      + `${A.hoof(c, 31, lh, 0, 6, 15)}${A.hoof(c, 65, lh, 0, 6, 15)}</svg></div>`;
    return hidden ? `<div class="bc-hbsv">${s}</div>` : s;
  }
  // 16：ぷるぷる（頭と首 10回/秒・後ろ足 11回/秒：強い 時と 弱い 時が ある）・しっぽ（ばらばらの 間と 大きさで ふる）・まばたき の keyframes（決まった 乱数：いつも 同じ）
  function hbCss() {
    let sd = 7;
    const rnd = () => { sd = (sd * 16807) % 2147483647; return (sd - 1) / 2147483646; };
    const jit = (name, dur, hz, amp, rot, env) => {
      const n = Math.round(dur * hz) * 2;
      const lv = p => { for (let i = 1; i < env.length; i++) if (p <= env[i][0]) { const p0 = env[i - 1][0], a0 = env[i - 1][1], p1 = env[i][0], a1 = env[i][1]; return a0 + (a1 - a0) * (p - p0) / (p1 - p0); } return env[env.length - 1][1]; };
      let k = '';
      for (let i = 0; i <= n; i++) {
        const p = i / n, e = i === 0 || i === n ? 0 : lv(p), sg = i % 2 ? 1 : -1;
        k += `${f(p * 100)}%{transform:translate(${f(sg * amp * e * (.55 + .45 * rnd()))}px,${f((rnd() - .5) * amp * e)}px) rotate(${f(-sg * rot * e * (.5 + .5 * rnd()))}deg)}`;
      }
      return `@keyframes ${name}{${k}}`;
    };
    return jit('bcHbH', 3.1, 10, .6, .6, [[0, 1], [.38, 1], [.46, .2], [.62, .25], [.7, .9], [.92, .9], [1, 1]])
      + jit('bcHbL', 2.3, 11, .55, .7, [[0, .3], [.2, .3], [.28, 1], [.66, 1], [.74, .25], [1, .3]])
      + '@keyframes bcHbT{0%,18%,37%,53%,66%,75%,88%,100%{transform:rotate(0)}6%{transform:rotate(9deg)}10%{transform:rotate(-5deg)}14%{transform:rotate(3deg)}'
      + '41%{transform:rotate(-11deg)}45%{transform:rotate(7deg)}49%{transform:rotate(-3deg)}69%{transform:rotate(5deg)}72%{transform:rotate(-2deg)}90.5%{transform:rotate(13deg)}93%{transform:rotate(-8deg)}96%{transform:rotate(4deg)}}'
      + '@keyframes bcHbE{0%,6%{opacity:0}6.4%,8.6%{opacity:1}9%,100%{opacity:0}}'
      // 16：落としそうに なる（ボードと 前足：右の 前足の 近くを 中心に 左が 大きく 下がる → じたばた → 持ち上げて 少し 上へ → もどる）
      + '@keyframes bcHbSlip{0%{transform:none;animation-timing-function:cubic-bezier(.55,0,1,.7)}16%{transform:translateY(9px) rotate(-2.6deg);animation-timing-function:ease-out}22%{transform:translateY(11px) rotate(-3deg)}'
      + '30%{transform:translateY(9.5px) rotate(-2.4deg)}38%{transform:translateY(10.6px) rotate(-2.9deg)}46%{transform:translateY(10px) rotate(-2.6deg);animation-timing-function:cubic-bezier(.3,0,.3,1)}'
      + '68%{transform:translateY(-3px) rotate(.6deg);animation-timing-function:ease-in-out}80%{transform:translateY(1px) rotate(-.2deg)}90%{transform:translateY(-.4px) rotate(0)}100%{transform:none}}'
      + '@keyframes bcHbJ{0%{transform:none}8%{transform:translate(2px,-4px) rotate(4deg)}12%{transform:translate(2.6px,-5px) rotate(5deg)}18%{transform:translate(1.8px,-4.2px) rotate(4.4deg)}'
      + '24%{transform:translate(2.8px,-4.8px) rotate(5deg)}30%{transform:translate(1.9px,-4.1px) rotate(4.3deg)}36%{transform:translate(2.7px,-4.9px) rotate(4.9deg)}42%{transform:translate(2px,-4.3px) rotate(4.5deg)}'
      + '56%{transform:translate(1px,-2px) rotate(2deg)}72%{transform:translate(-.6px,.8px) rotate(-1deg)}86%{transform:translate(0,.3px) rotate(-.3deg)}100%{transform:none}}'
      + jit('bcHbS', .85, 16, 1.6, 2.2, [[0, 1], [.66, 1], [1, 0]])
      + '@keyframes bcHbW{0%{opacity:0}3%{opacity:1}66%{opacity:1}72%,100%{opacity:0}}'
      + '@keyframes bcHbX{0%{opacity:0;transform:scale(.3)}12%{opacity:1;transform:scale(1.25)}22%{transform:scale(1)}70%{opacity:1}100%{opacity:0;transform:translateY(-4px)}}'
      + '@keyframes bcHbD{0%{opacity:0;transform:translate(0,0) scale(.5)}15%{opacity:1}60%{opacity:1;transform:translate(var(--x),var(--y)) rotate(var(--r)) scale(1)}100%{opacity:0;transform:translate(calc(var(--x) * 1.3),calc(var(--y) + 14px)) rotate(var(--r)) scale(.85)}}'
      + '@keyframes bcHbP{0%{opacity:0;transform:translate(0,0) scale(.4)}20%{opacity:.95}100%{opacity:0;transform:translate(-16px,5px) scale(1.35)}}';
  }

  // ---------- 1〜14 絵の ボード（第4.121版・まさちゃんの デザイン 14こ：的中①〜⑨・ハズレ①〜⑤）----------
  //   window.__BCP（kisekae/bcp/bcp_app.py）＝{ items: { id: { k（hit・miss）, st: [[連続の 数, デザイン], …] } }, d: { デザイン: { hp（ボードの 高さ）, q（板の 四すみ：舞台の pt）,
  //     fg（ボードの 前の 絵が ある）, ts（見出しの 色：''＝金・silver・copper・rainbow）, nt（見出しを 出さない：絵に 字が ある）, L（字と 行の 場所：kisekae/bcp の layout）, cl（「とじる」の 色） } } }
  //   段：的中は 連続的中の 数（spec.streak：1〜4連勝〜・出世馬は 1・2・3・4・8・16・24連勝〜）、ハズレは 続けて ハズレた 数（1〜4回目〜）。その 数から その 絵
  //   絵：bcp_<デザイン>.webp（舞台 390×844 の 3倍・ボードの うしろ）と bcp_<デザイン>_fg.webp（ボードの 前の キャラクターなど・すき通し）。読めない とき（CI）は いつもの ボード
  //     第4.145版：キャラが 動く 絵（D.mo.bgx が ある 48こ）は その 2まい（止まった 版）を アプリに 入れない。キャラなしの 背景（bgx）・キャラ・前の 絵（fgx）を 重ねて 同じ 絵に する（picParts）
  //   形：.hb（ボードの 入れもの）の 中に 舞台 ぜんぶの 入れもの .bcpw（絵 → ボード .rb → 前の 絵）。.rb は 板の 四すみに 合わせて matrix3d（ボードの 面 350×hp → 板）。
  //   字と 行は 見本（kisekae/bcp/bcp_inj.py）と 同じ 置き方・同じ 色（紺と 金）。ボードの 中の 飾り（テーマの 飾りなど）は 出さない（まさちゃん 21:49）
  //   出る 時：その 演出の ボードが 出る 時（.hb の 登場の アニメーション：時刻は そのまま・動きは 消す）に 絵ごと ふわっと（.bcpon）→ 出おわったら ほかの 絵（光・紙ふぶき・動画の コマ）を かくす（.bcpdone）
  const PIC = window.__BCP && window.__BCP.items && window.__BCP.d ? window.__BCP : null;
  if (PIC) Object.keys(PIC.items).forEach(id => { B[id] = () => ({ pic: 1 }); });
  const isPic = id => !!(PIC && PIC.items[id]);
  // 連続の 数 n → 段（[数, デザイン]）
  function picStage(id, n) { const P = PIC && PIC.items[id]; if (!P) return null; let s = P.st[0]; P.st.forEach(x => { if (n >= x[0]) s = x; }); return s; }
  // 段の 名前（「▶ 見る」：1連勝・2連勝…・いちばん 上は「4連勝〜」／ハズレは 1回目〜）
  function picStageName(id, i) { const P = PIC.items[id], s = P.st[i], last = i === P.st.length - 1; return s[0] + (P.k === 'miss' ? '回目' : '連勝') + (last ? '〜' : ''); }
  const PIC_CSS = [
    '#fxOv .ov.bcpic > .hb.bcpic{z-index:50!important;transform:none!important;filter:none!important}',
    '#fxOv .ov.bcpic > .close{z-index:52!important}',
    '#fxOv .hb.bcpic .bcpw{position:absolute;width:390px;height:844px;pointer-events:none;opacity:0}',
    '#fxOv .hb.bcpic.bcpon .bcpw{animation:bcpIn .55s cubic-bezier(.2,.8,.3,1) both}#fxOv .hb.bcpic.bcpon.bcpbig .bcpw{animation-name:bcpInB}',
    '#fxOv .hb.bcpic.bcst .bcpw{opacity:1;animation:none!important}',
    '@keyframes bcpIn{0%{opacity:0;transform:scale(1.045)}100%{opacity:1;transform:none}}',
    '@keyframes bcpInB{0%{opacity:0;transform:scale(1.07);filter:brightness(1.9)}55%{opacity:1;filter:brightness(1.25)}100%{opacity:1;transform:none;filter:none}}',
    '#fxOv .hb.bcpic .bcpw > img{position:absolute;left:0;top:0;width:390px;height:844px;-webkit-user-drag:none;user-select:none}',
    // 第4.145版：部品を 重ねる 絵は ぜんぶ 読めて から 出す（背景だけ 先に 出ると キャラが いない 絵に なる）
    '#fxOv .hb.bcpic .bcpw.bcpld > img{visibility:hidden}',
    // 第4.129版：キャラが 動く（picParts）：キャラの 入れもの（絵の 大きさ だけ）・まわりの 光と 雲（WebGL）・見えない 時計（光と 雲の 時刻）
    '#fxOv .hb.bcpic .bcpw .chrw{position:absolute;pointer-events:none}#fxOv .hb.bcpic .bcpw .chrw > .chri{position:absolute;left:0;top:0;width:100%;height:100%}',
    '#fxOv .hb.bcpic .bcpw .chrw img{position:absolute;left:0;top:0;width:100%;height:100%;-webkit-user-drag:none;user-select:none}',
    '#fxOv .hb.bcpic .bcpw .chramb{position:absolute;left:0;top:0;width:390px;height:844px;pointer-events:none}',
    '#fxOv .hb.bcpic .bcpw .chrclk{position:absolute;left:0;top:0;width:1px;height:1px;opacity:0;pointer-events:none}',
    // 出おわったら ほかの 絵を かくす（絵の うしろ：光・紙ふぶき・PUSH・動画の さいごの コマ など）
    '#fxOv .ov.bcpdone > :not(.hb):not(.close):not(.sr),#fxOv .fxs.bcpdone > video,#fxOv .fxs.bcpdone > .ov:not(.bcpic){visibility:hidden!important}',
    // ボード（見本 kisekae/bcp/bcp_inj.py と 同じ 形。テーマの ボードの 色・ふち・飾りは 消す）
    '#fxOv .rb.bcp{position:absolute!important;left:0!important;top:0!important;width:350px!important;padding:0!important;margin:0!important;background:transparent!important;box-shadow:none!important;border:0!important;'
      + 'border-radius:0!important;transform-origin:0 0!important;animation:none!important;outline:0!important;box-sizing:border-box;opacity:1!important}',
    '#fxOv .rb.bcp::before,#fxOv .rb.bcp::after,#fxOv .rb.bcp .hd::before,#fxOv .rb.bcp .hd::after,#fxOv .rb.bcp .card::before,#fxOv .rb.bcp .card::after,#fxOv .rb.bcp .orn{display:none!important}',
    '#fxOv .rb.bcp .hd{position:static!important;background:transparent!important;box-shadow:none!important;border:0!important;border-radius:0!important;padding:0!important;margin:0!important;height:0!important;min-height:0!important}',
    '#fxOv .rb.bcp .bh{position:absolute!important;white-space:nowrap;line-height:1.08;letter-spacing:1px;margin:0!important;padding:0!important;border:0!important;border-radius:0!important;box-shadow:none!important;outline:0!important;'
      + 'background:linear-gradient(180deg,#FFFCEB 0%,#FFE98A 26%,#FFCB3D 50%,#EE9F1E 74%,#C9780F 100%)!important;-webkit-background-clip:text!important;background-clip:text!important;color:transparent!important;-webkit-text-fill-color:transparent!important;'
      + '-webkit-text-stroke:.9px #7A3E00;text-shadow:none!important;filter:drop-shadow(0 1.6px 0 #5A2E00) drop-shadow(0 0 9px rgba(255,196,70,.62))}',
    '#fxOv .rb.bcp .bh .bz,#fxOv .rb.bcp .bh .bx3{color:transparent!important;-webkit-text-fill-color:transparent!important}',
    '#fxOv .rb.bcp.bcps-nt .bh{visibility:hidden!important}',
    '#fxOv .rb.bcp.bcps-silver .bh{background:linear-gradient(180deg,#FFFFFF 0%,#EEF3FB 45%,#C9D6EC 75%,#9FB2D6 100%)!important;-webkit-background-clip:text!important;background-clip:text!important;-webkit-text-stroke:.7px #3E4C70;filter:drop-shadow(0 1.2px 0 #1E2A48) drop-shadow(0 0 7px rgba(150,190,255,.55))}',
    '#fxOv .rb.bcp.bcps-copper .bh{background:linear-gradient(180deg,#FFF3E8 0%,#FFCFA8 26%,#F2914F 52%,#C55E2A 76%,#8C3C17 100%)!important;-webkit-background-clip:text!important;background-clip:text!important;-webkit-text-stroke:.9px #5A2008;filter:drop-shadow(0 1.6px 0 #3E1606) drop-shadow(0 0 9px rgba(255,140,70,.55))}',
    '#fxOv .rb.bcp.bcps-rainbow .bh{background:linear-gradient(180deg,rgba(255,255,255,.6) 0%,rgba(255,255,255,0) 46%),linear-gradient(90deg,#FF5A7A 0%,#FFB347 18%,#FFE45C 34%,#6EE07A 50%,#4CC3FF 66%,#8C7CFF 82%,#FF7AD9 100%)!important;'
      + '-webkit-background-clip:text!important;background-clip:text!important;-webkit-text-stroke:.8px #3A2A6A;filter:drop-shadow(0 1.4px 0 #221848) drop-shadow(0 0 8px rgba(255,255,255,.45))}',
    '#fxOv .rb.bcp .bh.bcp1x{letter-spacing:0}#fxOv .rb.bcp .bh.bcp1x .bzx{margin-left:-.2em}',
    '#fxOv .rb.bcp .bsub{position:absolute!important;margin:0!important;text-align:center;color:#fff!important;-webkit-text-fill-color:#fff!important;text-shadow:0 1px 2px rgba(0,0,0,.55);white-space:nowrap}',
    '#fxOv .rb.bcp .zrib{position:absolute!important;display:flex!important;width:max-content!important;max-width:none!important;margin:0!important;animation:none!important}',
    '#fxOv .rb.bcp .card{position:absolute!important;background:transparent!important;border:0!important;box-shadow:none!important;outline:0!important;border-radius:0!important;padding:0!important;margin:0!important;height:auto!important}',
    // 字は いつもの ボードの 字（テーマの 字に しない：絵の 見出しと 同じ 太い 字・見本と 同じ 形）
    '#fxOv .rb.bcp .bh,#fxOv .rb.bcp .bh *{font-family:"Dela Gothic One","BIZ UDPGothic",sans-serif!important;font-weight:400!important}',
    '#fxOv .rb.bcp .bsub,#fxOv .rb.bcp .zrib,#fxOv .rb.bcp .zrib *,#fxOv .rb.bcp .card,#fxOv .rb.bcp .card *{font-family:"BIZ UDPGothic",sans-serif!important}',
    '#fxOv .rb.bcp .brows li{min-height:0!important;padding:0 8px!important;background:rgba(40,54,100,.58)!important;border:1px solid rgba(150,172,230,.30)!important;border-radius:11px!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.06)!important;box-sizing:border-box}',
    '#fxOv .rb.bcp .bt{background:rgba(12,20,48,.88)!important;border:1px solid rgba(172,192,240,.48)!important;color:#fff!important;-webkit-text-fill-color:#fff!important;height:21px!important}',
    '#fxOv .rb.bcp .rs.miss,#fxOv .rb.bcp .rs.void,#fxOv .rb.bcp .rs.ref{background:rgba(8,14,36,.92)!important;border:1px solid rgba(160,182,232,.36)!important;color:#fff!important;-webkit-text-fill-color:#fff!important;height:21px!important}',
    '#fxOv .rb.bcp .rs.hit{background:linear-gradient(180deg,#FFEDB0,#F7C24C)!important;border:0!important;color:#fff!important;-webkit-text-fill-color:#fff!important;text-shadow:0 1px 1px rgba(128,72,0,.85),0 0 2px rgba(128,72,0,.5);height:21px!important}',
    '#fxOv .rb.bcp .ar{color:#B8C8F0!important;-webkit-text-fill-color:#B8C8F0!important}#fxOv .rb.bcp .more{color:#DDE6FF!important;-webkit-text-fill-color:#DDE6FF!important}',
    '#fxOv .rb.bcp .brows li.no{opacity:1!important}'
  ].join('\n');
  // 4点 → 4点 の 射影（ボードの 面 → 板）。h＝[a,b,c,d,e,f,g,h]（[[a,b,c],[d,e,f],[g,h,1]]）
  function homog(src, dst) {
    const A = [], R = [];
    for (let i = 0; i < 4; i++) {
      const x = src[i][0], y = src[i][1], u = dst[i][0], v = dst[i][1];
      A.push([x, y, 1, 0, 0, 0, -u * x, -u * y]); R.push(u);
      A.push([0, 0, 0, x, y, 1, -v * x, -v * y]); R.push(v);
    }
    for (let c = 0; c < 8; c++) {
      let p = c; for (let r = c + 1; r < 8; r++) if (Math.abs(A[r][c]) > Math.abs(A[p][c])) p = r;
      if (p !== c) { const t = A[c]; A[c] = A[p]; A[p] = t; const u = R[c]; R[c] = R[p]; R[p] = u; }
      for (let r = 0; r < 8; r++) { if (r === c) continue; const k = A[r][c] / A[c][c]; if (!k) continue; for (let j = c; j < 8; j++) A[r][j] -= k * A[c][j]; R[r] -= k * R[c]; }
    }
    return R.map((v, i) => v / A[i][i]);
  }
  const m3d = h => 'matrix3d(' + [h[0], h[3], 0, h[6], h[1], h[4], 0, h[7], 0, 0, 1, 0, h[2], h[5], 0, 1].map(v => +v.toFixed(8)).join(',') + ')';
  // 字と 行の 場所（kisekae/bcp/bcp_inj.py の 見本と 同じ 決め方。字の 幅を 測る ので 字が 読めて から もう一度 よぶ）
  function picLayout(rb, D) {
    const L = D.L || {}, bh = $('.bh', rb), sub = $('.bsub', rb), rib = $('.zrib', rb), card = $('.card', rb), br = $('.brows', rb);
    if (!bh || !card || !br || !L.normal) return;
    const lis = $$('.brows > li', rb), n = lis.length, px = v => (+v).toFixed(2) + 'px';
    if (/[^！]！$/.test(bh.textContent)) bh.classList.add('bcp1x');      // 「…的中！」：「！」を 字に よせる（絵の 見出しと 同じ はば）
    const M = Object.assign({}, L.normal, rib ? (L.rib || {}) : (n > 3 ? (L.many || {}) : {}));
    // 見出し：場所の まん中に・はばに おさまらない ときは 字を 小さく
    bh.style.fontSize = px(M.title_px); bh.style.top = px(M.title_top);
    const tx0 = M.text_x[0], tx1 = M.text_x[1], room = tx1 - tx0;
    let w = bh.offsetWidth;
    if (w > room) { const fs = M.title_px * room / w; bh.style.fontSize = px(fs); bh.style.top = px(M.title_top + (M.title_px - fs) * 1.08 / 2); w = bh.offsetWidth; }
    const cxp = M.title_cx != null ? M.title_cx : (tx0 + tx1) / 2, c2 = Math.min(Math.max(cxp, tx0 + w / 2), tx1 - w / 2);
    bh.style.left = px(c2 - w / 2);
    if (sub) {   // 小見出しの はば（見出しと ちがう とき：ハンコの 横 など）
      const sx0 = M.sub_x ? M.sub_x[0] : tx0, sx1 = M.sub_x ? M.sub_x[1] : tx1, sc = M.sub_cx != null ? M.sub_cx : c2, sw = 2 * Math.min(sc - sx0, sx1 - sc);
      sub.style.fontSize = px(M.sub_px); sub.style.top = px(M.sub_top); sub.style.left = px(sc - sw / 2); sub.style.width = px(sw);
    }
    let rowsTop = M.rows_top;
    if (rib) {   // 帯（ど的中〜）：見本の zoom の かわりに 縮める（WebKit でも 同じ 大きさ）
      const z = M.rib_zoom || .8;
      rib.style.transformOrigin = '0 0'; rib.style.transform = 'scale(' + z + ')';
      const rw = rib.offsetWidth * z, rh = rib.offsetHeight * z, rcx = M.rib_in === 'rows' ? (M.rows_x[0] + M.rows_x[1]) / 2 : c2;
      rib.style.left = px(rcx - rw / 2); rib.style.top = px(M.rib_top);
      if (M.rib_in === 'rows') rowsTop = M.rib_top + rh + 6;
    }
    card.style.left = px(M.rows_x[0]); card.style.width = px(M.rows_x[1] - M.rows_x[0]); card.style.top = px(rowsTop);
    br.style.gap = px(M.row_gap); lis.forEach(li => { li.style.height = px(M.row_h); });
    // 行：rows_zoom（字を 大きく）・板に おさまらない ときは 小さく（はばは そのまま）
    const avail = M.rows_bottom - rowsTop, z = M.rows_zoom || 1;
    br.style.width = (100 / z).toFixed(3) + '%';
    let h = br.scrollHeight, k = Math.min(z, avail / h);
    br.style.width = (100 / k).toFixed(3) + '%'; h = br.scrollHeight; k = Math.min(z, avail / h);
    br.style.width = (100 / k).toFixed(3) + '%';
    if (Math.abs(k - 1) > .002) { br.style.transformOrigin = '0 0'; br.style.transform = 'scale(' + k.toFixed(4) + ')'; } else br.style.transform = '';
  }
  const HELP = /^fx[a-z]*H$/;   // 待って いる 間 かくす だけの アニメーション（fxfxH・fxpmH・fxzpH）：ボードの 登場では ない
  // ボード（.hb）が 出はじめた（onStart）・出おわった（onGo）。知らせが こない とき（もう おわって いる・アニメーションが ない）は 見えて いて 動いて いなければ
  function whenBoard(hb, st, onStart, onGo) {
    let started = false, gone = false;
    const start = () => { if (started) return; started = true; onStart(); };
    const go = () => { if (gone || !hb.isConnected) return; gone = true; start(); onGo(); };
    if (st) { start(); go(); return; }
    hb.addEventListener('animationstart', e => { if (e.target === hb && !HELP.test(e.animationName)) start(); });
    hb.addEventListener('animationend', e => { if (e.target === hb && !HELP.test(e.animationName)) go(); });
    const poll = () => {
      if (gone || !hb.isConnected) return;
      const an = hb.getAnimations ? hb.getAnimations().filter(a => !HELP.test(a.animationName || '')) : [];
      const cs = getComputedStyle(hb), vis = cs.visibility !== 'hidden' && +cs.opacity > .9;
      if (vis && an.every(a => a.playState === 'finished' || a.playState === 'idle')) { go(); return; }
      setTimeout(poll, 300);
    };
    setTimeout(poll, 120);
  }
  // ---------- 絵の ボードの キャラが 動く（第4.129版・まさちゃん 2026/11/08「完成した動くカスタムボードを、アプリ内に入れてほしい！」）----------
  //   D.mo（kisekae/bcp/chr/motion.json・kisekae/bcp の README「キャラだけ 動かす」）：bgx（キャラなしの 背景）・fgx（前の 絵から キャラを のぞいた もの）・
  //     layers（キャラ：src・box（舞台の pt）・o（動きの まん中）・amp・deg・ax・dp・dt／ヒラヒラ：sw・st・fy・sf／ボードの 前に 出る 所：f）・
  //     oc（キャラの 前の 動かない 物）・ot（いちばん 上の 動かない 物）・top（キャラを ボードと 前の 絵の 上に）・amb（まわりの 光と 雲：WebGL）
  //   動き：ぷるん（3.2秒に 1回・つぶれ 3.8%）と 3Dで 向き（左右 4度・7秒）・ヒラヒラ（花：まん中の まわりで 回る＋向き）・光の すじが ゆれて 雲が うねる（トロフィー）
  //   第4.145版（まさちゃん 2026/11/10 20:04「やって！」＝止まった 版を やめて、動く 版の 部品を 重ねて 同じ 絵を 出す。アプリが 約14MB 軽く なる）：
  //     キャラなしの 背景（bgx）が ある 絵（48こ）は 止まった 版（bcp_<デザイン>.webp・_fg.webp）を 持たない。背景（bgx）と 前の 絵（fgx）を はじめから 置いて、
  //     部品が ぜんぶ 読めたら キャラを かさねて いっしょに 出す（.bcpld を 外す：止まって いる 形は 止まった 絵と 同じ＝chr_snap.py）→ 2コマ あとで 動きはじめる（.chrgo）
  //     的中エフェクト オフ・控えめ（視差効果を減らす も）は 同じ 部品を 重ねた まま 動かさない（CSS も @media prefers-reduced-motion）。部品が 読めない（CI）・8秒 たっても そろわない → いつもの ボード
  //     トロフィー（光と 雲だけ・bgx なし）と 出世馬（動かない）は 止まった 絵の まま（前と 同じ）
  const MO_PON = [[0, 0, 0], [8, -0.010, 0.016], [14, 0.024, -0.038], [22, -0.006, 0.012], [30, 0.007, -0.007], [38, -0.002, 0.003], [46, 0, 0], [100, 0, 0]];
  const MO_PER = 600, MO_TP = 3.2, MO_TT = 7;
  const moMade = {};
  function moRules(name, M) {     // デザインごとの アニメーション（1回 だけ 作る）
    if (moMade[name]) return; moMade[name] = 1;
    const nm = 'bcm_' + name.replace(/[^a-z0-9_]/gi, ''), s0 = `#fxOv .hb.bcpic.bcpon:not(.bcst) .bcpw.chrgo[data-mo="${name}"]`;
    const n4 = v => (+v).toFixed(4), n2 = v => (+v).toFixed(2), ry = d => `perspective(${MO_PER}px) rotateY(${n2(d)}deg)`;
    let k = '', r = '';
    (M.layers || []).forEach((l, i) => {
      const sel = `${s0} .chrw.L${i}`, dt = n2(l.dt == null ? .9 : l.dt), dp = n2(l.dp == null ? .8 : l.dp);
      if (l.sw != null) {        // ヒラヒラ（花）：まん中 o の まわりで ゆっくり 左右に 回る（sw 度・st 秒）＋ 少し 向きを かえる（fy 度・sf 秒）
        const sw = +l.sw, fy = l.fy == null ? 0 : +l.fy;
        k += `@keyframes ${nm}_${i}w{0%,100%{transform:rotate(0deg)}25%{transform:rotate(${n2(sw)}deg)}75%{transform:rotate(${n2(-sw)}deg)}}`;
        r += `${sel}{animation:${nm}_${i}w ${n2(l.st == null ? 3.6 : l.st)}s ease-in-out ${dt}s infinite}`;
        if (fy) {
          k += `@keyframes ${nm}_${i}y{0%,100%{transform:${ry(0)}}25%{transform:${ry(fy)}}75%{transform:${ry(-fy)}}}`;
          r += `${sel} > .chri{animation:${nm}_${i}y ${n2(l.sf == null ? 2.6 : l.sf)}s ease-in-out ${dp}s infinite}`;
        }
        return;
      }
      const a = l.amp == null ? 1 : +l.amp, d = l.deg == null ? 4 : +l.deg, ax = l.ax == null ? a : +l.ax;   // ax：よこの ふくらみ（ボードを 持つ キャラは 小さく）
      k += `@keyframes ${nm}_${i}p{` + MO_PON.map(([t, x, y]) => `${t}%{transform:scale(${n4(1 + x * ax)},${n4(1 + y * a)})}`).join('') + '}';
      k += `@keyframes ${nm}_${i}t{0%,100%{transform:${ry(0)}}25%{transform:${ry(d)}}75%{transform:${ry(-d)}}}`;
      r += `${sel}{animation:${nm}_${i}t ${MO_TT}s ease-in-out ${dt}s infinite}${sel} > .chri{animation:${nm}_${i}p ${MO_TP}s ease-in-out ${dp}s infinite}`;
    });
    if (M.amb) {
      k += `@keyframes ${nm}_clk{from{transform:translateX(0)}to{transform:translateX(1px)}}`;
      r += `${s0} .chrclk{animation:${nm}_clk 3600s linear 0s 1 both}`;
    }
    const st = document.createElement('style'); st.className = 'bcmCss'; st.textContent = k + '\n@media (prefers-reduced-motion:no-preference){' + r + '}';
    document.head.appendChild(st);
  }
  // その デザインの 背景・前の 絵（第4.145版）：キャラなしの 背景（mo.bgx）が ある デザインは 止まった 絵を 使わない（アプリに 入って いない：kisekae/bcp/bcp_app.py の pics と 同じ きまり）
  const picBg = (name, D) => (D.mo && D.mo.bgx) || `bcp_${name}.webp`;
  const picFg = (name, D) => (D.fg ? ((D.mo && D.mo.bgx && D.mo.fgx) || `bcp_${name}_fg.webp`) : null);
  // 絵を 出す のに いる もの ぜんぶ（背景・前の 絵・キャラ・動かない 物。まわりの 光と 雲 amb は のぞく：あとから かさねる）
  function picSrcs(name, D) {
    const M = D.mo || {}, L = M.layers || [];
    return [picBg(name, D), picFg(name, D), M.oc && M.oc.src, M.ot && M.ot.src].concat(L.map(l => l.src), L.map(l => l.f)).filter((s, i, a) => s && a.indexOf(s) === i);
  }
  // 絵を 読む（読めたら 先に 開く：decode。開くのを 待つのは 1.5秒 まで＝それでも 出す ときに 開く）
  function picLoad(s) {
    return new Promise((ok, ng) => {
      const im = new Image(); let fin = false;
      const done = () => { if (!fin) { fin = true; ok(im); } };
      im.onload = () => {
        let p = null; try { p = im.decode ? im.decode() : null; } catch (e) { p = null; }
        if (p && p.then) { p.then(done, done); setTimeout(done, 1500); } else done();
      };
      im.onerror = () => ng(new Error(s));
      im.src = s;
    });
  }
  // 部品（キャラ・動かない 物）を 読んで かさねる。move＝動かす（オフ・控えめ では かさねた まま 止めて おく）。
  //   かさねたら onShow（部品を 重ねる 絵は ここで はじめて 絵が 出る）。読めない・かさねられない → onFail
  function picParts(hb, wrap, rb, bg, name, D, move, onShow, onFail) {
    const M = D.mo, L = M.layers || [];
    Promise.all(picSrcs(name, D).map(picLoad)).then(() => {
      if (!wrap.isConnected || !hb.classList.contains('bcpic')) return;
      try {
        if (move) { moRules(name, M); wrap.dataset.mo = name; }
        const pic = (cls, src) => { const im = document.createElement('img'); im.className = cls; im.alt = ''; im.setAttribute('aria-hidden', 'true'); im.draggable = false; im.decoding = 'sync'; im.src = src; return im; };   // sync＝ほかの 部品と 同じ コマで 出す
        const still = (cls, o) => { const im = pic(cls, o.src), b = o.box; im.style.cssText = `position:absolute;left:${b[0]}px;top:${b[1]}px;width:${b[2]}px;height:${b[3]}px;pointer-events:none`; return im; };
        const mk = (l, i, src) => {   // 入れものは 絵の 大きさ だけ（重ねる 層が 小さい＝iPhone でも 軽い）。動きの まん中は 入れものの 中の 位置
          const w = document.createElement('div'), ii = document.createElement('div'), b = l.box;
          w.className = 'chrw L' + i; ii.className = 'chri';
          w.style.cssText = `left:${b[0]}px;top:${b[1]}px;width:${b[2]}px;height:${b[3]}px`;
          const o = `${f(l.o[0] - b[0])}px ${f(l.o[1] - b[1])}px`; w.style.transformOrigin = o; ii.style.transformOrigin = o;
          ii.appendChild(pic('', src)); w.appendChild(ii); return w;
        };
        // キャラ（ボードの 下・top は ボードと 前の 絵の 上）→ キャラの 前の 動かない 物（ボードの 下）→ ボードの 前に 出る 所 → いちばん 上の 動かない 物
        L.forEach((l, i) => { const w = mk(l, i, l.src); if (M.top) wrap.appendChild(w); else wrap.insertBefore(w, rb); });
        if (M.oc) wrap.insertBefore(still('chroc', M.oc), rb);
        L.forEach((l, i) => { if (l.f) wrap.appendChild(mk(l, i, l.f)); });
        if (M.ot) wrap.appendChild(still('chrot', M.ot));
      } catch (e) { onFail(e); return; }
      onShow();
      if (!move) return;
      if (M.amb) ambStart(wrap, rb, bg.getAttribute('src'), M.amb);
      // かさなって から 2コマ あとに 動きはじめる
      requestAnimationFrame(() => requestAnimationFrame(() => { if (wrap.isConnected) wrap.classList.add('chrgo'); }));
    }, onFail);
  }
  // まわりの 光と 雲（トロフィー：kisekae/bcp/chr/amb_stage.py の m1・m2・m3・f）：舞台の 絵の 上（アプリの ボードの 下）に WebGL の 絵を かさねる。
  //   光の すじは もとの まわりで ゆっくり ゆれて 明るさが 角度で 流れる・雲は 外へ むかう 波で うねる。トロフィー・紙ふぶきの 所は 動かない（かさねない）。
  //   時刻は 見えない 時計（.chrclk の CSS アニメーション）の currentTime（動きを 止める 設定では 時計が 動かない＝かさねない＝止まった 絵）。出はじめは ramp 秒で 0 から
  const AMB_VS = 'attribute vec2 p;void main(){gl_Position=vec4(p,0.0,1.0);}';
  const AMB_FS = ['precision highp float;', 'uniform sampler2D uO,uF,uM1,uM2,uM3;', 'uniform vec2 uC,uS;uniform float uT,uA;uniform vec4 uR,uK,uQ;',
    'const vec2 SZ=vec2(1170.0,2532.0);const float TAU=6.2831853;',
    'void main(){',
    '  vec2 px=vec2(gl_FragCoord.x,uC.y-gl_FragCoord.y)*(SZ.x/uC.x);vec2 uv=px/SZ;',
    '  vec3 m2=texture2D(uM2,uv).rgb;float w=m2.b;',
    '  if(w<0.002){gl_FragColor=vec4(0.0);return;}',
    '  vec3 m1=texture2D(uM1,uv).rgb;vec3 m3=texture2D(uM3,uv).rgb;',
    '  float rw=m2.r*uA,cw=m1.b*uA;',
    '  float th=uR.x*sin(TAU*uT/uR.y);vec2 r=px-uS;float cs=cos(th),sn=sin(th);',
    '  vec2 d=(vec2(cs*r.x-sn*r.y,sn*r.x+cs*r.y)-r)*rw;',
    '  vec2 dir=m1.rg*2.0-1.0;vec2 pp=vec2(-dir.y,dir.x);float rr=length(px-uQ.yz);',
    '  d+=cw*(uK.x*dir*sin(TAU*(uT/uK.z-rr/uQ.x)+TAU*m2.g)+uK.y*pp*sin(TAU*uT/uK.w+TAU*m3.b));',
    '  vec2 q=(px+d)/SZ;vec3 col=texture2D(uO,q).rgb;',
    '  float fs=texture2D(uM3,q).r*(1.0-m3.r);col=mix(col,texture2D(uF,q).rgb,fs);',
    '  float ang=atan(px.x-uS.x,px.y-uS.y);float fr=smoothstep(90.0,320.0,length(r));',
    '  col*=1.0+rw*fr*uR.z*sin(TAU*uT/uR.w-uQ.w*ang);',
    '  gl_FragColor=vec4(col*w,w);',
    '}'].join('\n');
  function ambStart(wrap, rb, bgSrc, A) {
    const u = A.u || {};
    const cv = document.createElement('canvas'); cv.className = 'chramb';
    const dpr = Math.min(3, window.devicePixelRatio || 1); cv.width = Math.round(390 * dpr); cv.height = Math.round(844 * dpr);
    wrap.insertBefore(cv, rb);
    const clk = document.createElement('i'); clk.className = 'chrclk'; wrap.appendChild(clk);
    let gl = null, U = {}, ready = false, dead = false, drawn = false, last = -1;
    const kill = () => { dead = true; if (cv.parentNode) cv.parentNode.removeChild(cv); };
    const init = () => {
      try { gl = cv.getContext('webgl', { alpha: true, premultipliedAlpha: true, antialias: false, depth: false, stencil: false }); } catch (e) { gl = null; }
      if (!gl) { kill(); return; }
      cv.addEventListener('webglcontextlost', e => { e.preventDefault(); kill(); });
      const sh = (ty, src) => { const o = gl.createShader(ty); gl.shaderSource(o, src); gl.compileShader(o); if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw new Error('shader'); return o; };
      let pg;
      try {
        pg = gl.createProgram(); gl.attachShader(pg, sh(gl.VERTEX_SHADER, AMB_VS)); gl.attachShader(pg, sh(gl.FRAGMENT_SHADER, AMB_FS)); gl.linkProgram(pg);
        if (!gl.getProgramParameter(pg, gl.LINK_STATUS)) throw new Error('link');
      } catch (e) { kill(); return; }
      gl.useProgram(pg);
      gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer()); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
      const loc = gl.getAttribLocation(pg, 'p'); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
      ['uO', 'uF', 'uM1', 'uM2', 'uM3', 'uC', 'uS', 'uT', 'uA', 'uR', 'uK', 'uQ'].forEach(n => { U[n] = gl.getUniformLocation(pg, n); });
      ['uO', 'uF', 'uM1', 'uM2', 'uM3'].forEach((n, i) => gl.uniform1i(U[n], i));
      const srcs = [bgSrc, A.f, A.m1, A.m2, A.m3]; let left = srcs.length;
      srcs.forEach((s, i) => {
        const im = new Image();
        im.onload = () => {
          if (dead) return;
          gl.activeTexture(gl.TEXTURE0 + i); gl.bindTexture(gl.TEXTURE_2D, gl.createTexture());
          gl.pixelStorei(gl.UNPACK_COLORSPACE_CONVERSION_WEBGL, i === 0 ? gl.BROWSER_DEFAULT_WEBGL : gl.NONE);   // 向きと 強さの 絵は 色の 変換を しない
          gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, im);
          [[gl.TEXTURE_MIN_FILTER, gl.LINEAR], [gl.TEXTURE_MAG_FILTER, gl.LINEAR], [gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE], [gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE]].forEach(([k, v]) => gl.texParameteri(gl.TEXTURE_2D, k, v));
          if (--left === 0) ready = true;
        };
        im.onerror = kill;
        im.src = s;
      });
      gl.uniform2f(U.uC, cv.width, cv.height);
      const S = u.src || [585, 40], C = u.c || [585, 1350];
      gl.uniform2f(U.uS, S[0], S[1]);
      gl.uniform4f(U.uR, (u.deg == null ? 1.1 : u.deg) * Math.PI / 180, u.pr || 8, u.sh == null ? .1 : u.sh, u.ps || 7);
      gl.uniform4f(U.uK, u.a1 == null ? 10 : u.a1, u.a2 == null ? 5 : u.a2, u.p1 || 6, u.p2 || 8.5);
      gl.uniform4f(U.uQ, u.wl || 420, C[0], C[1], u.bands || 6);
    };
    const clear = () => { if (gl && drawn) { gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT); } drawn = false; last = -1; };
    const tick = () => {
      if (!wrap.isConnected) { if (gl) { const x = gl.getExtension('WEBGL_lose_context'); if (x) x.loseContext(); } return; }
      requestAnimationFrame(tick);
      if (dead) return;
      const an = clk.getAnimations ? clk.getAnimations()[0] : null;
      if (!an) { clear(); return; }       // 動かさない（オフ・控えめ・視差効果を減らす）
      if (!gl) init();
      if (dead || !ready) return;
      const t = (an.currentTime || 0) / 1000;
      if (t === last || (t > last && last >= 0 && t - last < 1 / 31)) return;   // 30コマ／秒 まで（ゆっくりした 動き なので 十分）
      last = t;
      const rp = u.ramp || 1.5, x = Math.min(1, Math.max(0, t / rp));
      gl.uniform1f(U.uT, t); gl.uniform1f(U.uA, x * x * (3 - 2 * x));
      gl.viewport(0, 0, cv.width, cv.height); gl.drawArrays(gl.TRIANGLES, 0, 3); drawn = true;
    };
    requestAnimationFrame(tick);
  }
  function picDecorate(stage, hb, rb, it, info, kind) {
    const raw = info.streak != null ? info.streak : (info.spec && info.spec.streak != null ? info.spec.streak : 0);
    const sg = picStage(it.id, Math.max(1, Math.floor(+raw || 0))), name = sg && sg[1], D = name && PIC.d[name];
    if (!D) return null;
    css();
    const ov = hb.parentNode, st = !!(info.quiet || info.calm), orig = rb.cloneNode(true);
    const L0 = hb.offsetLeft, T0 = hb.offsetTop, q = D.q;
    const wrap = document.createElement('div'); wrap.className = 'bcpw';
    wrap.style.left = -L0 + 'px'; wrap.style.top = -T0 + 'px';
    wrap.style.transformOrigin = `${f((q[0][0] + q[1][0] + q[2][0] + q[3][0]) / 4)}px ${f((q[0][1] + q[1][1] + q[2][1] + q[3][1]) / 4)}px`;   // 板の まん中から
    const img = (cls, src) => { const im = document.createElement('img'); im.className = cls; im.alt = ''; im.setAttribute('aria-hidden', 'true'); im.draggable = false; im.decoding = 'sync'; im.src = src; return im; };   // sync＝背景・キャラ・前の 絵を 同じ コマで 出す
    // 第4.145版：parts＝止まった 版を 持たない 絵（キャラなしの 背景 bgx と 前の 絵 fgx を 置いて、部品が そろって から いっしょに 出す：.bcpld の 間は 見せない）
    const M = D.mo || null, parts = !!(M && M.bgx), fgSrc = picFg(name, D);
    const bg = img('bcpbg', picBg(name, D)), fg = fgSrc ? img('bcpfg', fgSrc) : null;
    if (parts) wrap.classList.add('bcpld');
    hb.insertBefore(wrap, rb); wrap.appendChild(bg); wrap.appendChild(rb); if (fg) wrap.appendChild(fg);
    hb.dataset.bcx = it.id; hb.dataset.bcp = name;
    hb.classList.add('bcpic', 'bcx-' + it.id); if (st) hb.classList.add('bcst'); if (BIG[kind]) hb.classList.add('bcpbig');
    if (ov && ov.classList) ov.classList.add('bcpic');
    rb.classList.add('bcp'); if (D.ts) rb.classList.add('bcps-' + D.ts); if (D.nt) rb.classList.add('bcps-nt');
    rb.style.setProperty('height', D.hp + 'px', 'important');
    rb.style.setProperty('transform', m3d(homog([[0, 0], [350, 0], [350, D.hp], [0, D.hp]], q)), 'important');
    const cl = D.cl;
    dynCss(cl ? `#fxOv .ov.bcpic > .close{border-color:${cl[0]}!important;background:${cl[1]}!important;box-shadow:${cl[2]}!important;${cl[3] || ''}}` : '');
    const lay = () => { try { if (rb.isConnected) picLayout(rb, D); } catch (e) { /* なし */ } };
    lay();
    try { if (document.fonts && document.fonts.ready) document.fonts.ready.then(lay); } catch (e) { /* なし */ }
    try { if (bg.decode) bg.decode().catch(() => {}); } catch (e) { /* なし */ }
    // 絵が 読めない（CI など）→ いつもの ボードに もどす
    let undone = false;
    const undo = () => {
      if (undone || !wrap.isConnected) return; undone = true;
      wrap.replaceWith(orig);
      hb.classList.remove('bcpic', 'bcst', 'bcpbig', 'bcpon'); if (ov && ov.classList) ov.classList.remove('bcpic', 'bcpdone'); stage.classList.remove('bcpdone');
      dynCss(''); delete hb.dataset.bcp;
    };
    bg.addEventListener('error', undo);
    if (fg) fg.addEventListener('error', () => { if (parts) undo(); else if (fg.parentNode) fg.parentNode.removeChild(fg); });   // 部品を 重ねる 絵は 1まい でも 欠けたら いつもの ボード
    // 出る 時：ボードの 登場が 始まったら 絵ごと 出す・出おわって（絵の ふわっと も おわって・部品を 重ねる 絵は 絵が 出て）から ほかの 絵を かくす
    let wDone = st, hDone = false, pDone = !parts;
    const done = () => { if (undone || !wDone || !hDone || !pDone || !hb.isConnected) return; if (ov && ov.classList) ov.classList.add('bcpdone'); stage.classList.add('bcpdone'); };
    // 第4.129版：キャラが 動く（D.mo）・オフと 控えめ では 動かさない。第4.145版：部品を 重ねる 絵は オフと 控えめ でも 部品で 出す（かさねた まま 止めて おく）。
    //   トロフィー（光と 雲だけ）は 止まった 絵が 読めて から（読めない とき＝CI は いつもの ボード）
    if (M && (parts || !st)) {
      const show = () => { wrap.classList.remove('bcpld'); pDone = true; done(); };
      const go = () => { if (!undone && wrap.isConnected) picParts(hb, wrap, rb, bg, name, D, !st, show, parts ? undo : () => { /* 光と 雲が 読めない → 止まった 絵の まま */ }); };
      if (parts || (bg.complete && bg.naturalWidth)) go(); else bg.addEventListener('load', go, { once: true });
      if (parts) setTimeout(() => { if (!pDone) undo(); }, 8000);   // 8秒 たっても 部品が そろわない → いつもの ボード（字だけ 出た まま に しない）
    }
    const wEnd = () => { if (wDone) return; wDone = true; done(); };
    wrap.addEventListener('animationend', e => { if (e.target === wrap) wEnd(); });
    whenBoard(hb, false, () => { lay(); hb.classList.add('bcpon'); if (!st) setTimeout(wEnd, 1500); }, () => { hDone = true; done(); });   // 1.5秒：知らせが こない とき
    return it.id;
  }
  // つぎの 結果で 出す 絵（的中＝連続的中＋1・ハズレ＝続けて ハズレた 数＋1）を 先に 読む（fx.js の prime：「結果を保存」を 押した とき）
  //   第4.145版：部品を 重ねる 絵は 部品 ぜんぶ（picSrcs：背景・前の 絵・キャラ・動かない 物）。持つ のは つぎの 的中と ハズレの ぶん だけ（前の ぶんは はなす）
  let warm = [];
  function prime() {
    try {
      const w = WL(); if (!PIC || !w || !w.board) return;
      const i = w.board.info(), keep = [];
      [['hit', i.streak], ['miss', i.mstreak]].forEach(([k, s]) => {
        const id = w.board.active(k); if (!isPic(id)) return;
        const sg = picStage(id, (+s || 0) + 1), D = sg && PIC.d[sg[1]]; if (!D) return;
        picSrcs(sg[1], D).forEach(src => {
          if (keep.some(x => x.s === src)) return;
          const old = warm.find(x => x.s === src);
          if (old) { keep.push(old); return; }
          const im = new Image(); im.src = src; keep.push({ s: src, im });
        });
      });
      warm = keep;
    } catch (e) { /* なし */ }
  }

  // ---------- 音（その場で 作る） ----------
  function ctx() { try { const F = FX(); return F && F.audio ? F.audio() : null; } catch (e) { return null; } }
  function noiseBuf(c, sec) { const n = Math.floor(c.sampleRate * sec), b = c.createBuffer(1, n, c.sampleRate), d = b.getChannelData(0); let l = 0; for (let i = 0; i < n; i++) { const w = Math.random() * 2 - 1; l = (l + .02 * w) / 1.02; d[i] = w * .6 + l * 3.2; } return b; }
  function env(g, t0, a, peak, dec, end) { g.gain.setValueAtTime(.0001, t0); g.gain.exponentialRampToValueAtTime(peak, t0 + a); g.gain.exponentialRampToValueAtTime(.0001, t0 + (end || a + dec)); }
  // 鳴って いる 音（結果の 画面を とじた・アプリを 閉じた・つぎの 結果が 出た ときに 止める）
  let live = [];
  function keep(c, n, end) { live = live.filter(x => x.end > c.currentTime); live.push({ n, end }); }
  function stopAll() { const l = live; live = []; l.forEach(x => { try { x.n.stop(); } catch (e) { /* もう 止まって いる */ } }); }
  function snd(name) {
    const c = ctx(); if (!c) return;
    try {
      const t0 = c.currentTime + .01, out = c.createGain(); out.gain.value = 1; out.connect(c.destination);
      const tone = (type, f0, f1, dur, vol, at) => { const o = c.createOscillator(), g = c.createGain(); o.type = type; o.frequency.setValueAtTime(f0, t0 + (at || 0)); o.frequency.exponentialRampToValueAtTime(f1, t0 + (at || 0) + dur); env(g, t0 + (at || 0), .008, vol, dur); o.connect(g); g.connect(out); o.start(t0 + (at || 0)); o.stop(t0 + (at || 0) + dur + .05); keep(c, o, t0 + (at || 0) + dur + .05); };
      const noise = (dur, vol, ftype, fq, q, at, a) => { const s = c.createBufferSource(), fl = c.createBiquadFilter(), g = c.createGain(); s.buffer = noiseBuf(c, dur + .05); fl.type = ftype; fl.frequency.value = fq; fl.Q.value = q || 1; env(g, t0 + (at || 0), a || .005, vol, dur); s.connect(fl); fl.connect(g); g.connect(out); s.start(t0 + (at || 0)); s.stop(t0 + (at || 0) + dur + .05); keep(c, s, t0 + (at || 0) + dur + .05); return fl; };
      if (name === 'thump') { tone('sine', 120, 38, .32, .55); noise(.12, .25, 'lowpass', 900, .7); }
      else if (name === 'slip') { tone('sine', 1100, 380, .24, .1); noise(.22, .07, 'bandpass', 1800, 2.2, .01, .02); }   // 16：ずり落ちる
      else if (name === 'phew') { noise(.38, .06, 'bandpass', 1100, .9, 0, .1); tone('sine', 660, 700, .14, .06, .02); tone('sine', 880, 930, .2, .05, .14); }   // 16：ふぅ
    } catch (e) { /* 音なし */ }
  }

  // ---------- ボードに つける ----------
  function lum(col) { const m = /rgba?\(([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)/.exec(col || ''); if (!m) return 1; const v = [m[1], m[2], m[3]].map(x => { x = +x / 255; return x <= .03928 ? x / 12.92 : Math.pow((x + .055) / 1.055, 2.4); }); return .2126 * v[0] + .7152 * v[1] + .0722 * v[2]; }
  function hueRed(col) { const m = /rgba?\(([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)/.exec(col || ''); if (!m) return false; const r = +m[1], g = +m[2], b = +m[3]; return r > 140 && r > g * 1.6 && r > b * 1.5; }
  // いま 選んで いる もの（第4.113版：ハズレの 結果は ハズレの 所・ほかは ぜんぶ 的中の 所）
  function selected(kind) { const w = WL(); try { return w && w.board ? w.board.active(kind === 'miss' ? 'miss' : 'hit') : ''; } catch (e) { return ''; } }
  // stage：fx.js の 舞台（.fxs）・info：{ kind, quiet, calm, spec, item（ためす とき：'none'＝なし）, streak（ためす とき）}
  function decorate(stage, info) {
    try {
      info = info || {};
      const hb = stage && $('.hb', stage), rb = hb && $('.rb', hb);
      if (!rb || hb.dataset.bcx) return null;
      stopAll();
      const kind = info.kind || 'hit', miss = kind === 'miss';
      const id = info.item || selected(kind);
      const it = BY[id]; if (!it || !it.ready || !B[it.id]) return null;
      if ((it.when === 'miss' && !miss) || (it.when === 'hit' && miss) || (it.when === 'big' && !BIG[kind])) return null;
      if (isPic(it.id)) return picDecorate(stage, hb, rb, it, info, kind);   // 第4.121版：まさちゃんの 絵の ボード
      css();
      const st = !!(info.quiet || info.calm), H = rb.offsetHeight || 220;
      const sp = Math.max(40, CLOSE_TOP - HB_TOP - H - 10);
      const cs = getComputedStyle(rb), acc = (cs.getPropertyValue('--acc') || '').trim() || (cs.getPropertyValue('--logo') || '').trim() || '#E2A23B';
      const bg = cs.backgroundColor, hd = $('.hd', rb), hdBg = hd ? getComputedStyle(hd).backgroundColor : '';
      const dark = lum(bg) < .3;
      hb.style.setProperty('--bcA', acc);
      // 見出しの 字の 場所（ボードの 左上からの px。舞台の 縮みは もどす）
      let title = null; const bh = $('.bh', rb);
      if (bh) { const k = rb.getBoundingClientRect().width / (rb.offsetWidth || 350) || 1, r0 = rb.getBoundingClientRect(), r1 = bh.getBoundingClientRect(); title = { l: (r1.left - r0.left) / k, t: (r1.top - r0.top) / k, w: r1.width / k, h: r1.height / k }; }
      const streak = info.streak != null ? +info.streak : (info.spec && info.spec.streak != null ? +info.spec.streak : 0);
      const o = { H, W: 350, sp, st, miss, big: !!BIG[kind], kind, dark, title, redHd: hueRed(hdBg), streak, u: ++uid };
      const r = B[it.id](o) || {};
      hb.dataset.bcx = it.id;
      hb.classList.add('bcx-' + it.id);
      if (dark) hb.classList.add('bcdk');
      if (st) hb.classList.add('bcst');
      if (r.html) hb.insertAdjacentHTML('beforeend', r.html);
      dynCss(r.css || '');
      if (r.enter && !st) hb.classList.add('bce-' + r.enter);
      // 第4.121版：ボードが 出る 時の 知らせは whenBoard（待つ 間 かくす だけの fxpmH・fxzpH も ボードの 登場と まちがえない）
      whenBoard(hb, st, () => { hb.classList.add('bcin'); if (r.start && !st) r.start(); }, () => { hb.classList.remove('bcin'); hb.classList.add('bcgo'); if (r.go) r.go(hb); });
      return it.id;
    } catch (e) { return null; }
  }

  // ---------- 設定 › 結果ボードカスタム（買う・進み具合・的中の とき／ハズレの とき の 2つを 選ぶ・見る） ----------
  const UI_CSS = [
    '#setBoard .bcbuy{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;align-items:center;border:1.5px solid var(--lamp,#E2A23B);border-radius:12px;padding:10px 12px;background:var(--surface-2)}',
    '#setBoard .bcbuy b{display:block;font-size:15px}#setBoard .bcbuy small{font-size:12px;color:var(--muted)}',
    // 第4.114版：お得パック（壁紙パックと 結果ボードカスタムの セット）の 行：単品を どちらも 持って いない ときだけ
    '#setBoard .bcbun{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;align-items:center;margin-top:8px;border:1.5px dashed var(--lamp,#E2A23B);border-radius:12px;padding:9px 12px;background:var(--surface)}',
    '#setBoard .bcbun b{display:block;font-size:14px}#setBoard .bcbun small{font-size:11.5px;color:var(--muted);line-height:1.35}',
    '#setBoard .bcprog{border:1px solid var(--line);border-radius:12px;padding:10px 12px;background:var(--surface-2)}#setBoard .bcprog b{font-size:14px}',
    '#setBoard .bcprog .bar{height:8px;border-radius:4px;background:var(--surface);overflow:hidden;margin:6px 0 4px;border:1px solid var(--line)}#setBoard .bcprog .bar i{display:block;height:100%;background:linear-gradient(90deg,#FFC93C,#F28C1E)}',
    // 的中の とき・ハズレの とき（いま 使って いる もの・▶ 見る・なし）
    '#setBoard .bcslots{display:grid;gap:8px;margin-top:10px}',
    // 第4.125版：的中ボード・ハズレボードの かたまり（見出し＝いま つけて いる もの・▶ 見る・つけない）
    '#setBoard .bcsec{margin-top:14px;padding-top:12px;border-top:2px dashed var(--line)}#setBoard .bcsec .bcgrid{margin-top:8px}',
    '#setBoard .bcsech{display:flex;align-items:center;gap:8px;flex-wrap:wrap}#setBoard .bcsech .bcsc{font-size:12.5px;color:var(--muted)}#setBoard .bcsec .bck{font-size:13px;line-height:24px;padding:0 11px}',
    '#setBoard .bcslot{display:grid;grid-template-columns:minmax(0,1fr) auto auto;gap:8px;align-items:center;border:1.5px solid var(--line);border-radius:12px;padding:8px 10px;background:var(--surface)}',
    '#setBoard .bcsl1{display:flex;flex-direction:column;align-items:flex-start;gap:3px;min-width:0}',
    '#setBoard .bck{display:inline-block;padding:0 9px;border-radius:999px;font:700 12px/22px "BIZ UDPGothic",sans-serif;color:#FFFFFF;white-space:nowrap;background:#E2323A}#setBoard .bck.miss{background:#4A63B8}',
    '#setBoard .bcsn{font-weight:700;font-size:13.5px;line-height:1.3;max-width:100%;overflow-wrap:anywhere}#setBoard .bcsn.none{color:var(--muted);font-weight:400;font-size:12.5px}',
    '#setBoard .bcslot .btn{padding:4px 10px;font-size:12px}',
    '#setBoard .bcgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px;margin-top:10px}',
    '#setBoard .bct{position:relative;display:flex;flex-direction:column;gap:3px;padding:6px 6px 8px;border:1.5px solid var(--line);border-radius:12px;background:var(--surface);text-align:left;min-width:0}',
    '#setBoard .bct.on{border-color:var(--ok,#2E9E5B);box-shadow:0 0 0 2px var(--ok,#2E9E5B) inset}',
    '#setBoard .bct.prep{background:var(--surface-2)}#setBoard .bct.prep .bcn,#setBoard .bct.prep .bcd{color:var(--muted)}',
    '#setBoard .bclk{position:absolute;right:5px;top:5px;z-index:2;width:24px;height:24px;border-radius:12px;background:rgba(0,0,0,.55);font:400 12px/24px sans-serif;text-align:center}',
    '#setBoard .bcno{display:inline-block;min-width:20px;height:20px;margin-right:4px;padding:0 5px;border-radius:10px;background:var(--ink,#1F2433);color:var(--surface,#FFFFFF);font:700 11.5px/20px "BIZ UDPGothic",sans-serif;text-align:center;vertical-align:1px}',
    '#setBoard .bcnew{display:inline-block;margin-left:4px;padding:0 6px;border-radius:8px;background:#E2323A;color:#FFFFFF;font:700 10.5px/17px "BIZ UDPGothic",sans-serif;vertical-align:2px}',
    '#setBoard .bcn{font-weight:700;font-size:13.5px;line-height:1.3}#setBoard .bcd{font-size:11.5px;color:var(--muted);line-height:1.35}',
    '#setBoard .bcs{font-size:11.5px;font-weight:700;color:var(--muted)}#setBoard .bct.on .bcs{color:var(--ok,#2E9E5B)}',
    // 使う 所の ボタン（的中・ハズレ：押すと その 所に 使う・もう一度 押すと なし）と「▶ 見る」
    '#setBoard .bcuse{display:flex;flex-wrap:wrap;gap:6px;margin-top:2px}#setBoard .bcuse .btn{padding:4px 10px;font-size:12px}',
    '#setBoard .bcpick[aria-pressed=true]{background:var(--ok,#2E9E5B);border-color:var(--ok,#2E9E5B);color:#FFFFFF}',
    '#setBoard .bcsee{align-self:flex-start;padding:4px 10px;font-size:12px}',
    '#setBoard .bcmini{position:relative;width:100%;aspect-ratio:4/3;border-radius:8px;overflow:hidden;background:linear-gradient(180deg,#1E2650,#2E2A5A)}',
    '#setBoard .bcmini .bcmi{position:absolute;left:0;top:0;width:350px;height:170px;transform-origin:0 0;visibility:hidden}#setBoard .bcmini .bcmi.fit{visibility:visible}',
    '#setBoard .bcmini .hb{position:absolute;left:0;top:0;width:350px}',
    '#setBoard .bcmini .bcfake{position:relative;height:170px;border-radius:22px;padding:8px;background:#FFF8EC;box-shadow:0 0 0 2px rgba(255,255,255,.7),0 10px 20px rgba(0,0,0,.4)}',
    '#setBoard .bcmini .bcfake .fh{height:62px;border-radius:14px;background:var(--bcA,#2B3A67);display:flex;align-items:center;justify-content:center;font:400 30px/1 "Dela Gothic One","BIZ UDPGothic",sans-serif;color:#FFE27A;text-shadow:0 2px 0 rgba(0,0,0,.25)}',
    '#setBoard .bcmini .bcfake .fr{height:22px;margin:9px 6px 0;border-radius:8px;background:#E9E2D4}#setBoard .bcmini .bcfake .fr:nth-child(3){width:70%}',
    '#setBoard .bcmini .bcfake.miss .fh{color:#FFFFFF}',
    // じゅんび中の 見本：うすい ボードの 上に「じゅんび中」
    '#setBoard .bcmini.prep .bcmi{opacity:.32}',
    '#setBoard .bcmini .bcprep{position:absolute;left:50%;top:50%;z-index:6;transform:translate(-50%,-50%);padding:5px 12px 6px;border-radius:999px;white-space:nowrap;background:rgba(0,0,0,.5);color:#FFFFFF;font:400 15px/1.2 "Dela Gothic One","BIZ UDPGothic",sans-serif;letter-spacing:.04em}',
    // 第4.121版：絵の ボードの 見本（bcp_t_<id>.webp：いちばん はじめの 段の 結果の 画面・たて 3:4）。読めない とき（CI）は 名前だけ
    '#setBoard .bcmini.pic{aspect-ratio:3/4}#setBoard .bcmini.pic .bcpth{position:absolute;left:0;top:0;width:100%;height:100%;object-fit:cover;display:block;-webkit-user-drag:none}',
    '#setBoard .bcmini.pic .bcpno{display:none;position:absolute;inset:0;align-items:center;justify-content:center;padding:10px;text-align:center;color:#FFE9A8;font:400 15px/1.35 "Dela Gothic One","BIZ UDPGothic",sans-serif}',
    '#setBoard .bcmini.pic.bad .bcpth{display:none}#setBoard .bcmini.pic.bad .bcpno{display:flex}'
  ].join('\n');
  const SEEN_KEY = 'tengel.bcseen2';   // 第4.113版：もう 見た 飾りの id（,で つなぐ）。NEW の しるし（あとから 入った 飾りにも つく）
  let uiSeen = null;
  const seeK = {};                      // 「▶ 見る」：的中にも ハズレにも 使える 飾りは 押す たびに 的中 → ハズレ → 的中…
  function seenSet() { if (uiSeen) return uiSeen; let v = ''; try { v = localStorage.getItem(SEEN_KEY) || ''; } catch (e) { v = ''; } uiSeen = new Set(v.split(',').filter(Boolean)); return uiSeen; }
  function setSeen(ids) { uiSeen = new Set(ids); try { localStorage.setItem(SEEN_KEY, Array.from(uiSeen).join(',')); } catch (e) { /* なし */ } }
  const fits = (it, k) => !!(it && it.ready && B[it.id] && PT.boardFits(it, k));
  const kindOf = it => (it.when === 'miss' ? 'miss' : it.when === 'big' ? 'big' : 'hit');
  const both = it => fits(it, 'hit') && fits(it, 'miss');
  const seeS = {};                      // 第4.121版：絵の ボードの「▶ 見る」は 押す たびに つぎの 段（1連勝 → 2連勝 → … → 1連勝）
  const seeLabel = (it, k) => (isPic(it.id) ? `▶ 見る（${picStageName(it.id, seeS[it.id] || 0)}）` : both(it) && !k ? `▶ 見る（${seeK[it.id] === 'miss' ? KIND.miss : KIND.hit}）` : '▶ 見る');   // k＝的中ボード／ハズレボードの 一覧（第4.125版）
  // 小さな 見本（動かさない）：ボードの かわりの 四角＋その 飾り。じゅんび中は うすい ボードに「じゅんび中」
  function fakeBoard(miss, head, tf) { return `<div class="rb bcfake${miss ? ' miss' : ''}" style="${tf || ''}"><div class="fh">${head}</div><div class="fr"></div><div class="fr"></div></div>`; }
  function thumbHtml(it, sk) {   // sk：的中ボード／ハズレボードの 一覧（第4.125版：どちらにも 出る 飾りは その 結果の 見本）
    if (it.ready && isPic(it.id)) return `<div class="bcmini pic" aria-hidden="true"><img class="bcpth" src="${esc(String(PIC.thumb || '').replace('{}', it.id))}" alt="" decoding="async" draggable="false"><div class="bcpno">${esc(it.name)}</div></div>`;
    if (!it.ready || !B[it.id]) return `<div class="bcmini prep" aria-hidden="true"><div class="bcmi"><div class="hb bcst">${fakeBoard(false, '')}</div></div><span class="bcprep">じゅんび中</span></div>`;
    const k = sk && it.when === 'all' ? sk : kindOf(it), miss = k === 'miss', H = 170;
    const o = { H, W: 350, sp: 120, st: true, miss, big: k === 'big', kind: k, dark: false, title: { l: 112, t: 14, w: 126, h: 40 }, redHd: false, streak: 0, u: 0 };
    let r = {};
    try { r = B[it.id](o) || {}; } catch (e) { r = {}; }
    const th = r.thumb || {};
    const head = miss ? 'ハズレ' : k === 'big' ? 'デカ的中!!' : '的中！';
    return `<div class="bcmini" aria-hidden="true"><div class="bcmi"><div class="hb bcst bcx-${it.id}" style="--bcA:#2B3A67">${fakeBoard(miss, head, th.style)}${r.html || ''}${th.html || ''}</div></div></div>`;
  }
  function card() {
    const set = $('#v-set'); if (!set) return;
    const after = $('#setKisekae');
    let c = $('#setBoard');
    if (!c) {
      css();
      c = document.createElement('div'); c.className = 'card setsec'; c.id = 'setBoard'; c.style.marginBottom = 'var(--gap)';
      c.innerHTML = '<h2>結果ボードカスタム</h2><div class="bcbody"></div>';
      c.addEventListener('click', onClick);
    }
    if (after && after.nextElementSibling !== c) after.insertAdjacentElement('afterend', c);
    else if (!after && !c.parentNode) set.appendChild(c);
    paint();
  }
  function paint() {
    const box = $('#setBoard .bcbody'), w = WL(); if (!box) return;
    const i = w && w.board ? w.board.info() : { owned: false, reads: 0, n: 0, next: null, nextReady: null, selHit: '', selMiss: '', streak: 0 };
    const price = w && w.board ? w.board.price() : '1,500円';
    const bundle = w && w.bundle && w.bundle.offer() ? { price: w.bundle.price() } : null;   // 第4.114版：お得パック（単品を どちらも 持って いない とき）
    const seen = seenSet(), last = PT.BOARD_NEED[PT.BOARD_NEED.length - 1], every = PT.BOARD.steps.length === 1 ? PT.BOARD.steps[0][1] : 0;
    const sel = { hit: i.selHit || '', miss: i.selMiss || '' };
    let h = '<p class="hint" style="margin:0 0 8px">結果のボードを、絵の ボードや 馬の 飾りに かえられるよ。<b>的中ボード</b>と <b>ハズレボード</b>から、それぞれ <b>1つずつ</b> つけられるよ（<b>つけない</b>＝いつもの ボード）。<b>どの 壁紙でも 使える</b>よ。</p>';
    if (!i.owned) {
      h += `<div class="bcbuy"><div><b>結果ボードカスタム</b><small>${ITEMS.length}種・買い切り（1回 買えば ずっと）</small></div><button class="btn primary" type="button" data-bcact="buy">${esc(price)}で買う</button></div>`;
      h += `<p class="ptnote">買った あとに 読み込んだ レースの 数で、1つずつ 番号の 順に 解放されるよ（${every ? `${every}レースごと／` : ''}ぜんぶで ${last}レース）。読み直し（0P）と 5連の 予想は 数えないよ。「▶ 見る」で 買う 前にも ためせるよ。</p>`;
      if (bundle) h += `<div class="bcbun"><div><b>お得パック</b><small>壁紙パック（新しい 壁紙 11枚）と 結果ボードカスタムの 2つが セット。べつべつに 買うより お得だよ</small></div><button class="btn primary" type="button" data-bcact="bundle">${esc(bundle.price)}で買う</button></div>`;
      h += '<div class="row" style="margin-top:6px"><button class="btn ghost" type="button" data-bcact="restore">購入を復元</button></div>';
    } else {
      const nx = i.next, nr = i.nextReady, done = !nx, pct = done ? 100 : Math.round((i.reads - nx.from) / (nx.need - nx.from) * 100);
      const nxt = done ? 'ぜんぶ 解放したよ！' : nx.item.ready ? `つぎの「${esc(nx.item.name)}」まで あと <b>${nx.left}</b>レース`
        : `つぎの 解放まで あと <b>${nx.left}</b>レース${nr ? `（「${esc(nr.item.name)}」まで あと ${nr.left}レース）` : ''}`;
      h += `<div class="bcprog"><b>解放 ${i.n}/${ITEMS.length}</b>　<span class="muted" style="font-size:12.5px">買ってから 読み込んだ レース：${i.reads}</span><div class="bar"><i style="width:${pct}%"></i></div>`
        + `<span style="font-size:12.5px">${nxt}</span></div>`;
    }
    // 第4.125版：一覧を「的中ボード」「ハズレボード」の 2つに 分ける（まさちゃん 2026/11/04「結果ボードカスタムは2種類 的中とハズレ それぞれ一つずつ取り付けられる機能追加して！ どちらかをつけないことも可能にして！」）。
    //   それぞれ 1つ「つける」か「つけない」（いつもの ボード）。15「ボードを持つ馬」は どちらにも 出る。解放は 今までどおり 番号の 順（1〜15）
    const SEC = { hit: '的中ボード', miss: 'ハズレボード' };
    const inSec = (it, k) => (k === 'miss' ? it.when === 'miss' || it.when === 'all' : it.when !== 'miss');
    ['hit', 'miss'].forEach(k => {
      const list = ITEMS.filter(it => inSec(it, k)), cur = BY[sel[k]], has = !!(i.owned && cur && cur.ready && inSec(cur, k));
      h += `<section class="bcsec" data-sec="${k}" aria-label="${SEC[k]}">`;
      h += i.owned
        ? `<div class="bcslot" data-slot="${k}"><div class="bcsl1"><span class="bck ${k}">${SEC[k]}（${list.length}種）</span><span class="bcsn${has ? '' : ' none'}">${has ? esc(cur.name) : 'なし（いつもの ボード）'}</span></div>`
          + `<button class="btn ghost" type="button" data-bcact="seeslot" data-slot="${k}">▶ 見る</button>`
          + `<button class="btn ghost" type="button" data-bcact="none" data-slot="${k}"${has ? '' : ' disabled'}>つけない</button></div>`
        : `<div class="bcsech"><span class="bck ${k}">${SEC[k]}（${list.length}種）</span><span class="bcsc">${KIND[k]}の ときの 結果の ボード</span></div>`;
      h += '<div class="bcgrid">';
      list.forEach(it => {
        const ok = it.ready && !!B[it.id], open = i.owned && it.no <= i.n, isNew = open && ok && !seen.has(it.id);
        const left = i.owned ? Math.max(0, it.need - i.reads) : 0, on = open && ok && sel[k] === it.id;
        const st = !i.owned ? '🔒 買うと 解放' : !open ? `🔒 あと ${left}レース` : !ok ? '解放ずみ・じゅんび中' : on ? `${KIND[k]}で つけている` : 'つけられるよ';
        let use = '';
        if (ok && open) use += `<button class="btn ghost bcpick" type="button" data-bcact="use" data-id="${it.id}" data-slot="${k}" aria-pressed="${on}">${on ? '✓ つけている' : 'つける'}</button>`;
        if (ok) use += `<button class="btn ghost bcsee" type="button" data-bcact="see" data-id="${it.id}"${both(it) && !isPic(it.id) ? ` data-kind="${k}"` : ''}>${seeLabel(it, k)}</button>`;
        h += `<div class="bct${on ? ' on' : ''}${open ? '' : ' lock'}${ok ? '' : ' prep'}" data-bc="${it.id}" data-sec="${k}" role="group" aria-label="${it.no}. ${esc(it.name)}${on ? '（つけている）' : open ? '' : '（まだ）'}">`
          + `${open ? '' : '<span class="bclk" aria-hidden="true">🔒</span>'}${thumbHtml(it, k)}<span class="bcn"><span class="bcno">${it.no}</span>${esc(it.name)}${isNew ? '<span class="bcnew">NEW</span>' : ''}</span>`
          + `<span class="bcd">${esc(it.desc)}</span>`
          + `<span class="bcs">${st}</span>${use ? `<div class="bcuse">${use}</div>` : ''}</div>`;
      });
      h += '</div></section>';
    });
    h += '<p class="ptnote" style="margin-top:10px">「的中ボード」「ハズレボード」の 中で「つける」を 押すと、その 結果の ときに 使うよ（それぞれ 1つ。もう一度 押すか「つけない」で いつもの ボード）。「▶ 見る」で、ためしに 結果の ボードを 出すよ（まだ 解放して いない ものも 見られるよ）。<br>'
      + '絵の ボードは、的中は 続けて 当てた 数（連勝）・ハズレは 続けて ハズレた 数で 絵が かわるよ（「▶ 見る」は 押す たびに つぎの 絵）。<br>'
      + (ITEMS.some(x => !x.ready) ? 'じゅんび中の 番号には、アプリの 更新で 新しい 飾りが 入るよ（解放ずみの 番号なら、入ったら すぐ 使えるよ）。<br>' : '')
      + '「視差効果を減らす」か 設定の「演出を控えめにする」が オンなら、飾りは 止まった 形で 出るよ。<br>アプリを 消すと、解放の 進み具合は 0に もどるよ（買った ことは「購入を復元」で もどせるよ）。</p>';
    box.innerHTML = h;
    fitThumbs(); requestAnimationFrame(fitThumbs);
    const opened = ITEMS.filter(it => i.owned && it.no <= i.n && it.ready && B[it.id]).map(it => it.id);
    if (opened.some(id => !seen.has(id))) { const v = $('#v-set'); if (v && !v.hidden) setTimeout(() => setSeen(Array.from(seen).concat(opened)), 4000); }
  }
  // 見本の 枠：ボードと 飾り（見えて いる もの）が ぜんぶ 入る ように 縮めて まん中へ（はじめの 1回だけ 測る）。.bcnf の 部品（光・紙ふぶき など）は 測らない
  const NOFIT = /(^|\s)bcnf(\s|$)/;
  function fitThumbs() {
    $$('#setBoard .bcmini').forEach(m => {
      const mi = $('.bcmi', m), hb = mi && $('.hb', mi), W0 = m.clientWidth, H0 = m.clientHeight; if (!hb || !W0 || !H0) return;
      if (!mi.dataset.box) {
        mi.style.transform = 'none';
        const r0 = mi.getBoundingClientRect(); let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
        const add = r => { if (!r.width || !r.height) return; x0 = Math.min(x0, r.left - r0.left); y0 = Math.min(y0, r.top - r0.top); x1 = Math.max(x1, r.right - r0.left); y1 = Math.max(y1, r.bottom - r0.top); };
        add($('.rb', hb).getBoundingClientRect());
        $$('.bcx', hb).forEach(e => { if (NOFIT.test(e.className)) return; const cs = getComputedStyle(e); if (+cs.opacity === 0 || cs.display === 'none') return; add(e.getBoundingClientRect()); });
        if (x1 <= x0) return;
        mi.dataset.box = [x0, y0, x1, y1].map(v => v.toFixed(1)).join(',');
      }
      const [x0, y0, x1, y1] = mi.dataset.box.split(',').map(Number), pad = 12;
      const k = Math.min(W0 / (x1 - x0 + pad * 2), H0 / (y1 - y0 + pad * 2));
      const tx = (W0 - (x1 - x0) * k) / 2 - x0 * k, ty = (H0 - (y1 - y0) * k) / 2 - y0 * k;
      mi.style.transform = `translate(${tx.toFixed(1)}px,${ty.toFixed(1)}px) scale(${k.toFixed(4)})`;
      mi.classList.add('fit');
    });
  }
  function sample(kind) {
    const tri = { t: '3連単', state: '的中', hits: [[11, 8, 2]], n: 18 }, um = { t: '馬単', state: '的中', hits: [[11, 8]], n: 9 }, wd = { t: 'ワイド', state: '不的中', hits: [], n: 6 };
    const rows = kind === 'miss' ? [Object.assign({}, tri, { state: '不的中', hits: [] }), Object.assign({}, um, { state: '不的中', hits: [] }), wd] : kind === 'hit' ? [Object.assign({}, tri, { state: '不的中', hits: [] }), um, wd] : [tri, um, wd];
    return { r: 9, n: 14, rows, ranks: { 11: 11, 8: 8, 2: 2, 6: 1, 10: 3 } };
  }
  // ためしに 出す（PUSH なしで すぐ 結果の 画面）。kind を 決めない とき：その 飾りの 結果（的中にも ハズレにも 使える ものは 押す たびに 的中 → ハズレ）
  function see(id, kind, n) {
    const it = BY[id], F = FX(); if (!F || !F.preview) return null;
    if (it && it.ready && isPic(id)) {   // 絵の ボード：kind なし＝押す たびに つぎの 段・kind あり（使う 所の「▶ 見る」）＝連続の 数 n（つぎの 結果と 同じ 段）
      const P = PIC.items[id], k = P.k === 'miss' ? 'miss' : 'hit';
      let m = n;
      if (!kind) { const i = seeS[id] || 0; m = P.st[i][0]; seeS[id] = (i + 1) % P.st.length; }
      try { F.prime(); } catch (e) { /* 音なし */ }
      F.preview(sample(k), k, { item: id, streak: Math.max(1, +m || 1) });
      return k;
    }
    let k = kind;
    if (!k) {
      if (!it || !it.ready || !B[it.id]) return null;
      k = kindOf(it);
      if (both(it)) { k = seeK[id] === 'miss' ? 'miss' : 'hit'; seeK[id] = k === 'miss' ? 'hit' : 'miss'; }
    }
    try { F.prime(); } catch (e) { /* 音なし */ }
    F.preview(sample(k), k, { item: it && it.ready ? id : 'none' });
    return k;
  }
  function toast(m, ms) { const t = $('#toast'); if (!t) return; t.textContent = m; t.hidden = false; clearTimeout(toast._t); toast._t = setTimeout(() => { t.hidden = true; }, ms || 3000); }
  async function onClick(e) {
    const a = e.target.closest('[data-bcact]'), w = WL();
    if (a) {
      e.stopPropagation();
      const act = a.dataset.bcact, k = a.dataset.slot === 'miss' ? 'miss' : 'hit';
      if (act === 'see') { see(a.dataset.id, a.dataset.kind || undefined); const it = BY[a.dataset.id]; if (it) a.textContent = seeLabel(it, a.closest('.bct') ? a.closest('.bct').dataset.sec : ''); return; }
      if (!w || !w.board) return;
      if (act === 'seeslot') { const i = w.board.info(), id = (k === 'miss' ? i.selMiss : i.selHit) || 'none', it = BY[id]; see(id, k === 'miss' ? 'miss' : it ? (kindOf(it) === 'big' ? 'big' : 'hit') : 'hit', (k === 'miss' ? i.mstreak : i.streak) + 1); return; }
      if (act === 'buy') { await w.board.buy(a); paint(); return; }
      if (act === 'bundle') { if (w.bundle) await w.bundle.buy(a); paint(); return; }
      if (act === 'restore') { await w.board.restore(a); paint(); return; }
      if (act === 'none') { if (await w.board.select('none', k)) { toast(`${KIND[k]}の ときは いつもの ボードに もどしたよ`); paint(); } return; }
      if (act === 'use') {
        const it = BY[a.dataset.id], i = w.board.info(); if (!it) return;
        const cur = k === 'miss' ? i.selMiss : i.selHit, off = cur === it.id;
        if (await w.board.select(off ? 'none' : it.id, k)) { toast(off ? `${KIND[k]}の ときは いつもの ボードに もどしたよ` : `${KIND[k]}の ときに「${it.name}」を 使うよ`); paint(); }
        return;
      }
      return;
    }
    // タイル（ボタンの 外）：まだ 使えない ときの 案内
    const t = e.target.closest('.bct'); if (!t) return;
    const it = BY[t.dataset.bc]; if (!it) return;
    const i = w && w.board ? w.board.info() : { owned: false, reads: 0, n: 0 };
    if (!it.ready || !B[it.id]) { toast(`${it.no}番は じゅんび中だよ（アプリの 更新で 新しい 飾りが 入るよ）`, 3600); return; }
    if (!i.owned) { toast(`買うと、読み込んだ レースの 数で 番号の 順に 解放されるよ（「${it.name}」は ${it.need}レース）`, 3600); return; }
    if (it.no > i.n) { toast(`「${it.name}」は あと ${Math.max(0, it.need - i.reads)}レースで 解放（番号の 順に 解放されるよ）`, 3600); return; }
    toast(`「つける」を 押すと、${t.dataset.sec === 'miss' ? 'ハズレ' : '的中'}の ときに 使うよ`, 3000);
  }
  // 解放の お知らせ（読み込みの あと：画面の 上に 4秒）・設定の タイルの 解放エフェクト
  function note(html) {
    css();
    const old = $('#bcNote'); if (old) old.remove();
    const n = document.createElement('div'); n.id = 'bcNote'; n.setAttribute('role', 'status'); n.innerHTML = html; document.body.appendChild(n);
    setTimeout(() => { if (n.parentNode) n.remove(); }, 4300);
  }
  document.addEventListener('tengel:board', e => {
    const d = e.detail || {};
    paint();
    if (d.phase === 'unlock' && BY[d.item]) {
      const it = BY[d.item];
      note(`<b>🎉 結果ボードカスタム「${esc(it.name)}」が 解放！</b>${d.many > 1 ? `${d.many}こ 解放したよ。` : ''}設定の「結果ボードカスタム」で 使えるよ`);
      const tile = $(`#setBoard .bct[data-bc="${it.id}"]`), v = $('#v-set');
      if (tile && v && !v.hidden && FX() && FX().unlock) FX().unlock(tile, { text: '解放！' });
    }
  });
  // 16「ボードを持つ馬」の 絵が 読めない（絵なしの CI など）→ その ボードは SVG の 馬に（error は 上へ 伝わらないので つかまえる 側で 聞く）
  document.addEventListener('error', e => { const t = e.target; if (t && t.classList && t.classList.contains('bchbi')) { const hb = t.closest('.hb'); if (hb) hb.classList.add('bchbv'); } }, true);
  // 第4.121版：絵の ボードの 見本が 読めない（絵なしの CI）→ 名前だけ
  document.addEventListener('error', e => { const t = e.target; if (t && t.classList && t.classList.contains('bcpth')) { const m = t.closest('.bcmini'); if (m) m.classList.add('bad'); } }, true);
  document.addEventListener('tengel:wallet', () => { if ($('#setBoard')) paint(); });
  document.addEventListener('tengel:fx', e => { if (e.detail && e.detail.phase === 'close') stopAll(); });
  document.addEventListener('visibilitychange', () => { if (document.hidden) stopAll(); });
  window.addEventListener('pagehide', stopAll);
  document.addEventListener('tengel:tab', e => { if (e.detail === 'set') { card(); const w = WL(); if (w && w.board) w.board.products().then(paint).catch(() => {}); } });
  window.addEventListener('resize', fitThumbs);
  setTimeout(card, 60);

  window.TengelBoard = { on: true, items: () => ITEMS.slice(), decorate: decorate, snd: snd, see: see, paint: paint, prime: prime, pic: id => (isPic(id) ? JSON.parse(JSON.stringify(PIC.items[id])) : null), stage: (id, n) => picStage(id, n), _B: B, _HBX: HBX,
    _picSrcs: name => (PIC && PIC.d[name] ? picSrcs(name, PIC.d[name]) : []), _warm: () => warm.map(x => x.s) };   // 第4.145版：テスト用（その デザインで 読む 絵・先に 読んだ 絵）
  css();
})();
