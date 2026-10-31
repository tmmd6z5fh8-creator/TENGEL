// ===== 結果ボードカスタム（App Store版・第4.91版・まさちゃんの 指定 2026-10-28／第4.113版で 16こ・的中と ハズレの 2つ）=====
//   買い切り 2,200円（App内課金の 非消耗型 jp.tengel.app.boardcustom）。買った あとに 読み込んだ レースの 数で 16こを 番号の 順に 解放（points.js の BOARD：6レースごとに 1つ）。
//   第4.113版（まさちゃん 2026/11/01 01:13「結果ボードカスタム、最後のボードを持つ馬以外一度全部消して！全部で16個(ボードを持つ馬を含む)にする！
//     15個は、デザインは仕組みはできているから準備ができたら教えて！送っていく！」）：前の 1〜21（ボードを一周〜出世馬・幻の 馬）は 消した。
//     1〜15 は じゅんび中（まさちゃんの デザインが とどいたら 入れる）・16「ボードを持つ馬」（いちばん はじめの 頃の 馬：絵は kisekae/r3d/fx/board_horse_parts.py の 部品 5まい。
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
  const BIG = { big: 1, fz: 1, nd: 1, sd: 1, pc: 1, sgd: 1, spg: 1 };
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
    // 16 ボードを持つ馬：下から ボードを かかえて 出てくる（1秒・着地で 少し はずむ）→ 頭と首・後ろ足が ぷるぷる（別々の 速さ）・しっぽを ときどき ふる・まばたき
    '.fxs .hb .bcx img{display:block;width:100%;height:100%;-webkit-user-drag:none;user-select:none}',
    '.fxs .hb.bce-carry{animation-name:bcECarry!important;animation-duration:1s!important;animation-timing-function:linear!important;transform-origin:50% 100%}',
    '@keyframes bcECarry{0%{opacity:1;transform:translateY(660px);animation-timing-function:cubic-bezier(.18,.72,.36,1)}46%{transform:translateY(-16px);animation-timing-function:ease-in}'
      + '60%{transform:translateY(0) scale(1.03,.95);animation-timing-function:ease-out}74%{transform:translateY(-5px) scale(.99,1.02);animation-timing-function:ease-in}86%{transform:translateY(0) scale(1.01,.99)}100%{opacity:1;transform:none}}',
    '.fxs .hb.bcgo .bc-hbh{animation:bcHbH 3.1s linear infinite,bcHbJ 1.4s linear 1.5s 1 none}.fxs .hb.bcgo .bc-hbl{animation:bcHbL 2.3s linear infinite -.7s,bcHbS .85s linear 1.5s 1 none}',
    '.fxs .hb.bcgo .bc-hbt{animation:bcHbT 7.9s ease-in-out infinite .6s}.fxs .hb .bc-hbe{opacity:0}.fxs .hb.bcgo .bc-hbe{animation:bcHbE 5.3s linear infinite .5s}',
    // 16：1回だけ ボードを 落としそうに なって あせる（出おわって 1.5秒後・1.4秒：ずり落ちる → 頭が びくっ・目を 見ひらく・汗・後ろ足が じたばた → 持ち直す → ふぅ）。
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
    const st = document.createElement('style'); st.id = 'bcxCss'; st.textContent = CSS_ALL + '\n' + UI_CSS; document.head.appendChild(st);
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

  // ---------- 16こ：部品を 作る ----------
  //   B.<id>(o)：o＝{ H（ボードの 高さ）, W（350）, sp（ボードの 下の すき間）, st（動かさない）, miss（ハズレ）, big（デカ的中から 上）, kind（結果の 種類）, dark（暗い ボード）,
  //     title（見出しの 字の 場所：ボードの 左上からの px）, redHd（見出しが 赤）, streak（連続的中の 数）, u（毎回 ちがう 番号：CSS の 名前に）}
  //   かえす もの：{ html（.hb に 入れる 部品）, css（その 時だけの CSS）, enter（登場の しかた：.hb に .bce-<名前>）, start（ボードが 出はじめた とき）, go（出おわった とき）,
  //     thumb（設定の 小さな 見本だけの { html, style }：動きの しるし など）}。1〜15（じゅんび中）は まだ ない
  const B = {};
  // 16 ボードを持つ馬（第4.108版・まさちゃんの 指定）：いちばん はじめの 頃の 馬。うしろから ボードを かかえて 下から 出てくる（着地で 少し はずむ）
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
  // 16：あせる 所の 部品（頭と首の 入れもの の 中：頭と いっしょに 動く）。見ひらいた 目（白目＋小さな 黒目）・汗 3つ・「！」の 形・鼻の 息（ふぅ）
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
  // 16 の 絵が ない とき：SVG の 馬（頭と首は ボードの うしろ・ひづめは 上の ふちに かける・下は 後ろ足と しっぽ）。hidden＝ふだんは かくす（絵が 読めない ときに 出す）
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
      let started = false, gone = false;
      const go = () => {
        if (gone || !hb.isConnected) return; gone = true;
        hb.classList.remove('bcin'); hb.classList.add('bcgo');
        if (r.go) r.go(hb);
      };
      const start = () => { if (started) return; started = true; hb.classList.add('bcin'); if (r.start && !st) r.start(); };
      if (st) { start(); go(); return it.id; }
      hb.addEventListener('animationstart', e => { if (e.target === hb && e.animationName !== 'fxfxH') start(); });
      hb.addEventListener('animationend', e => { if (e.target === hb && e.animationName !== 'fxfxH') { start(); go(); } });
      // 知らせが こない とき（もう おわって いる・アニメーションが ない）：ボードが 見えて いて 動いて いなければ 始める
      const poll = () => {
        if (gone || !hb.isConnected) return;
        const an = hb.getAnimations ? hb.getAnimations().filter(a => a.animationName !== 'fxfxH') : [];
        const vis = getComputedStyle(hb).visibility !== 'hidden' && +getComputedStyle(hb).opacity > .9;
        if (vis && an.every(a => a.playState === 'finished' || a.playState === 'idle')) { start(); go(); return; }
        setTimeout(poll, 300);
      };
      setTimeout(poll, 120);
      return it.id;
    } catch (e) { return null; }
  }

  // ---------- 設定 › 結果ボードカスタム（買う・進み具合・的中の とき／ハズレの とき の 2つを 選ぶ・見る） ----------
  const UI_CSS = [
    '#setBoard .bcbuy{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;align-items:center;border:1.5px solid var(--lamp,#E2A23B);border-radius:12px;padding:10px 12px;background:var(--surface-2)}',
    '#setBoard .bcbuy b{display:block;font-size:15px}#setBoard .bcbuy small{font-size:12px;color:var(--muted)}',
    '#setBoard .bcprog{border:1px solid var(--line);border-radius:12px;padding:10px 12px;background:var(--surface-2)}#setBoard .bcprog b{font-size:14px}',
    '#setBoard .bcprog .bar{height:8px;border-radius:4px;background:var(--surface);overflow:hidden;margin:6px 0 4px;border:1px solid var(--line)}#setBoard .bcprog .bar i{display:block;height:100%;background:linear-gradient(90deg,#FFC93C,#F28C1E)}',
    // 的中の とき・ハズレの とき（いま 使って いる もの・▶ 見る・なし）
    '#setBoard .bcslots{display:grid;gap:8px;margin-top:10px}',
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
    '#setBoard .bcmini .bcprep{position:absolute;left:50%;top:50%;z-index:6;transform:translate(-50%,-50%);padding:5px 12px 6px;border-radius:999px;white-space:nowrap;background:rgba(0,0,0,.5);color:#FFFFFF;font:400 15px/1.2 "Dela Gothic One","BIZ UDPGothic",sans-serif;letter-spacing:.04em}'
  ].join('\n');
  const SEEN_KEY = 'tengel.bcseen2';   // 第4.113版：もう 見た 飾りの id（,で つなぐ）。NEW の しるし（あとから 入った 飾りにも つく）
  let uiSeen = null;
  const seeK = {};                      // 「▶ 見る」：的中にも ハズレにも 使える 飾りは 押す たびに 的中 → ハズレ → 的中…
  function seenSet() { if (uiSeen) return uiSeen; let v = ''; try { v = localStorage.getItem(SEEN_KEY) || ''; } catch (e) { v = ''; } uiSeen = new Set(v.split(',').filter(Boolean)); return uiSeen; }
  function setSeen(ids) { uiSeen = new Set(ids); try { localStorage.setItem(SEEN_KEY, Array.from(uiSeen).join(',')); } catch (e) { /* なし */ } }
  const fits = (it, k) => !!(it && it.ready && B[it.id] && PT.boardFits(it, k));
  const kindOf = it => (it.when === 'miss' ? 'miss' : it.when === 'big' ? 'big' : 'hit');
  const both = it => fits(it, 'hit') && fits(it, 'miss');
  const seeLabel = it => (both(it) ? `▶ 見る（${seeK[it.id] === 'miss' ? KIND.miss : KIND.hit}）` : '▶ 見る');
  // 小さな 見本（動かさない）：ボードの かわりの 四角＋その 飾り。じゅんび中は うすい ボードに「じゅんび中」
  function fakeBoard(miss, head, tf) { return `<div class="rb bcfake${miss ? ' miss' : ''}" style="${tf || ''}"><div class="fh">${head}</div><div class="fr"></div><div class="fr"></div></div>`; }
  function thumbHtml(it) {
    if (!it.ready || !B[it.id]) return `<div class="bcmini prep" aria-hidden="true"><div class="bcmi"><div class="hb bcst">${fakeBoard(false, '')}</div></div><span class="bcprep">じゅんび中</span></div>`;
    const k = kindOf(it), miss = k === 'miss', H = 170;
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
    const price = w && w.board ? w.board.price() : '2,200円';
    const seen = seenSet(), last = PT.BOARD_NEED[PT.BOARD_NEED.length - 1], every = PT.BOARD.steps.length === 1 ? PT.BOARD.steps[0][1] : 0;
    const sel = { hit: i.selHit || '', miss: i.selMiss || '' };
    let h = '<p class="hint" style="margin:0 0 8px">結果のボード（的中・ハズレの 結果）に、馬の 飾りや 動きを つけられるよ。<b>的中のとき</b>と <b>ハズレのとき</b>で、べつべつに 1つずつ 選べるよ。<b>どの 壁紙の ボードにも 使える</b>よ。</p>';
    if (!i.owned) {
      h += `<div class="bcbuy"><div><b>結果ボードカスタム</b><small>${ITEMS.length}種・買い切り（1回 買えば ずっと）</small></div><button class="btn primary" type="button" data-bcact="buy">${esc(price)}で買う</button></div>`;
      h += `<p class="ptnote">買った あとに 読み込んだ レースの 数で、1つずつ 番号の 順に 解放されるよ（${every ? `${every}レースごと／` : ''}ぜんぶで ${last}レース）。読み直し（0P）と 5連の 予想は 数えないよ。「▶ 見る」で 買う 前にも ためせるよ。</p>`;
      h += '<div class="row" style="margin-top:6px"><button class="btn ghost" type="button" data-bcact="restore">購入を復元</button></div>';
    } else {
      const nx = i.next, nr = i.nextReady, done = !nx, pct = done ? 100 : Math.round((i.reads - nx.from) / (nx.need - nx.from) * 100);
      const nxt = done ? 'ぜんぶ 解放したよ！' : nx.item.ready ? `つぎの「${esc(nx.item.name)}」まで あと <b>${nx.left}</b>レース`
        : `つぎの 解放まで あと <b>${nx.left}</b>レース${nr ? `（「${esc(nr.item.name)}」まで あと ${nr.left}レース）` : ''}`;
      h += `<div class="bcprog"><b>解放 ${i.n}/${ITEMS.length}</b>　<span class="muted" style="font-size:12.5px">買ってから 読み込んだ レース：${i.reads}</span><div class="bar"><i style="width:${pct}%"></i></div>`
        + `<span style="font-size:12.5px">${nxt}</span></div>`;
      // 的中の とき・ハズレの とき
      h += '<div class="bcslots">' + ['hit', 'miss'].map(k => {
        const it = BY[sel[k]], has = !!(it && it.ready);
        return `<div class="bcslot" data-slot="${k}"><div class="bcsl1"><span class="bck ${k}">${KIND[k]}のとき</span><span class="bcsn${has ? '' : ' none'}">${has ? esc(it.name) : 'なし（いつもの ボード）'}</span></div>`
          + `<button class="btn ghost" type="button" data-bcact="seeslot" data-slot="${k}">▶ 見る</button>`
          + `<button class="btn ghost" type="button" data-bcact="none" data-slot="${k}"${has ? '' : ' disabled'}>なし</button></div>`;
      }).join('') + '</div>';
    }
    h += '<div class="bcgrid">';
    ITEMS.forEach(it => {
      const ok = it.ready && !!B[it.id], open = i.owned && it.no <= i.n, isNew = open && ok && !seen.has(it.id);
      const left = i.owned ? Math.max(0, it.need - i.reads) : 0;
      const useH = open && ok && sel.hit === it.id, useM = open && ok && sel.miss === it.id, on = useH || useM;
      const st = !i.owned ? '🔒 買うと 解放' : !open ? `🔒 あと ${left}レース` : !ok ? '解放ずみ・じゅんび中'
        : useH && useM ? '的中・ハズレで 使用中' : useH ? '的中で 使用中' : useM ? 'ハズレで 使用中' : '使う ときを 選んでね';
      const when = it.when === 'miss' ? '（ハズレの とき）' : it.when === 'big' ? '（デカ的中から 上）' : it.when === 'hit' ? '（的中の とき）' : '';
      let use = '';
      if (ok && open) use += ['hit', 'miss'].filter(k => fits(it, k)).map(k => { const p = sel[k] === it.id;
        return `<button class="btn ghost bcpick" type="button" data-bcact="use" data-id="${it.id}" data-slot="${k}" aria-pressed="${p}">${p ? '✓ ' : ''}${KIND[k]}</button>`; }).join('');
      if (ok) use += `<button class="btn ghost bcsee" type="button" data-bcact="see" data-id="${it.id}">${seeLabel(it)}</button>`;
      h += `<div class="bct${on ? ' on' : ''}${open ? '' : ' lock'}${ok ? '' : ' prep'}" data-bc="${it.id}" aria-label="${it.no}. ${esc(it.name)}${on ? '（使用中）' : open ? '' : '（まだ）'}">`
        + `${open ? '' : '<span class="bclk" aria-hidden="true">🔒</span>'}${thumbHtml(it)}<span class="bcn"><span class="bcno">${it.no}</span>${esc(it.name)}${isNew ? '<span class="bcnew">NEW</span>' : ''}</span>`
        + `<span class="bcd">${esc(it.desc)}${esc(when && it.desc.indexOf('とき') < 0 ? when : '')}</span>`
        + `<span class="bcs">${st}</span>${use ? `<div class="bcuse">${use}</div>` : ''}</div>`;
    });
    h += '</div>';
    h += '<p class="ptnote" style="margin-top:10px">「的中」「ハズレ」の ボタンで、その 結果の ときに 使う ものを 選ぶよ（もう一度 押すと なし）。「▶ 見る」で、ためしに 結果の ボードを 出すよ（まだ 解放して いない ものも 見られるよ）。<br>'
      + 'じゅんび中の 番号には、アプリの 更新で 新しい 飾りが 入るよ（解放ずみの 番号なら、入ったら すぐ 使えるよ）。<br>'
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
  function see(id, kind) {
    const it = BY[id], F = FX(); if (!F || !F.preview) return null;
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
      if (act === 'see') { see(a.dataset.id); const it = BY[a.dataset.id]; if (it) a.textContent = seeLabel(it); return; }
      if (!w || !w.board) return;
      if (act === 'seeslot') { const i = w.board.info(), id = (k === 'miss' ? i.selMiss : i.selHit) || 'none', it = BY[id]; see(id, k === 'miss' ? 'miss' : it ? (kindOf(it) === 'big' ? 'big' : 'hit') : 'hit'); return; }
      if (act === 'buy') { await w.board.buy(a); paint(); return; }
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
    toast('「的中」「ハズレ」の ボタンで、使う ときを 選んでね', 3000);
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
  document.addEventListener('tengel:wallet', () => { if ($('#setBoard')) paint(); });
  document.addEventListener('tengel:fx', e => { if (e.detail && e.detail.phase === 'close') stopAll(); });
  document.addEventListener('visibilitychange', () => { if (document.hidden) stopAll(); });
  window.addEventListener('pagehide', stopAll);
  document.addEventListener('tengel:tab', e => { if (e.detail === 'set') { card(); const w = WL(); if (w && w.board) w.board.products().then(paint).catch(() => {}); } });
  window.addEventListener('resize', fitThumbs);
  setTimeout(card, 60);

  window.TengelBoard = { on: true, items: () => ITEMS.slice(), decorate: decorate, snd: snd, see: see, paint: paint, _B: B, _HBX: HBX };
  css();
})();
