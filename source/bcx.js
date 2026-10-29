// ===== 結果ボードカスタム（App Store版・第4.91版・まさちゃんの 指定 2026-10-28）=====
//   買い切り 2,200円（App内課金の 非消耗型 jp.tengel.app.boardcustom）。買った あとに 読み込んだ レースの 数で 22こを 番号の 順に 解放（points.js の BOARD）。
//   第4.108版：22「ボードを持つ馬」（いちばん はじめの 頃の 馬：絵は kisekae/r3d/fx/board_horse_parts.py の 部品 5まい。ない とき（CI）は SVG の 馬）
//   使うのは 1つだけ（設定の「結果ボードカスタム」で 選ぶ）。どの 壁紙の ボードにも 重ねられる 形（ボードの 外がわ・登場の しかた・ボードの 動き）。
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
  const BIG = { big: 1, fz: 1, nd: 1, sd: 1, pc: 1, sgd: 1, spg: 1 };
  const CLOSE_TOP = 734;          // 舞台（390×844）の「とじる」の 上の はし
  const HB_TOP = 196;             // ボード（.hb）の 上の はし
  const ENTER = { pop: 1, drop: 1, flip: 1, slide: 1, banner: 1, carry: 1 };   // 登場の しかたを かえる もの（.hb の アニメーションの 名前を 入れかえる）
  let uid = 0;

  // ---------- CSS（いつも 同じ 分） ----------
  const OL = 'filter:drop-shadow(0 0 1px rgba(255,255,255,.95)) drop-shadow(0 0 .7px rgba(255,255,255,.95)) drop-shadow(0 3px 3px rgba(0,0,0,.34))';
  const CSS = [
    '.fxs .hb .bcx{position:absolute;z-index:3;pointer-events:none}.fxs .hb .bcx.bk{z-index:-1}.fxs .hb .bcx svg{display:block;width:100%;height:100%;overflow:visible}',
    `.fxs .hb .bco{${OL}}`,
    '.fxs .hb .bcx .bcf{width:100%;height:100%}',
    // 動かさない（視差効果を減らす・控えめ・静か）
    '.fxs .hb.bcst .bcx,.fxs .hb.bcst .bcx *,.fxs .hb.bcst .rb{animation:none!important;transition:none!important}',
    // まばたき・しっぽ・耳
    '.fxs .hb.bcgo .bcbl{animation:bcBlink 4.6s infinite}@keyframes bcBlink{0%,91%,100%{transform:scaleY(1)}94%{transform:scaleY(.1)}}',
    // 走る（横から 見た 馬：.run の 中の 足 .bcL1〜4・ひざ .bcK・体 .bcBd・頭 .bcH・しっぽ .bcTl）
    '.fxs .hb .run .bcL1{animation:bcGF .44s linear infinite -.03s}.fxs .hb .run .bcL2{animation:bcGF .44s linear infinite}',
    '.fxs .hb .run .bcL3{animation:bcGH .44s linear infinite -.03s}.fxs .hb .run .bcL4{animation:bcGH .44s linear infinite}',
    '.fxs .hb .run .bcL1 .bcK{animation:bcGFk .44s linear infinite -.03s}.fxs .hb .run .bcL2 .bcK{animation:bcGFk .44s linear infinite}',
    '.fxs .hb .run .bcL3 .bcK{animation:bcGHk .44s linear infinite -.03s}.fxs .hb .run .bcL4 .bcK{animation:bcGHk .44s linear infinite}',
    '.fxs .hb .run .bcBd{animation:bcGB .44s ease-in-out infinite}.fxs .hb .run .bcH{animation:bcGN .44s ease-in-out infinite}.fxs .hb .run .bcTl{animation:bcGT .44s ease-in-out infinite}',
    '@keyframes bcGF{0%{transform:rotate(-46deg)}25%{transform:rotate(-12deg)}50%{transform:rotate(26deg)}75%{transform:rotate(2deg)}100%{transform:rotate(-46deg)}}',
    '@keyframes bcGFk{0%{transform:rotate(-8deg)}25%{transform:rotate(0deg)}50%{transform:rotate(6deg)}62%{transform:rotate(70deg)}82%{transform:rotate(60deg)}100%{transform:rotate(-8deg)}}',
    '@keyframes bcGH{0%{transform:rotate(34deg)}25%{transform:rotate(10deg)}50%{transform:rotate(-30deg)}75%{transform:rotate(-6deg)}100%{transform:rotate(34deg)}}',
    '@keyframes bcGHk{0%{transform:rotate(10deg)}12%{transform:rotate(-40deg)}35%{transform:rotate(-30deg)}50%{transform:rotate(-6deg)}75%{transform:rotate(0deg)}100%{transform:rotate(10deg)}}',
    '@keyframes bcGB{0%,100%{transform:translateY(-3px) rotate(-2deg)}50%{transform:translateY(2px) rotate(2.5deg)}}',
    '@keyframes bcGN{0%,100%{transform:rotate(-4deg)}50%{transform:rotate(6deg)}}@keyframes bcGT{0%,100%{transform:rotate(-6deg)}50%{transform:rotate(8deg)}}',
    // 止まった 馬：うなずき・しっぽ
    '.fxs .hb.bcgo .idle .bcH{animation:bcNod 2.6s ease-in-out infinite}.fxs .hb.bcgo .idle .bcTl{animation:bcSwish 2.2s ease-in-out infinite}',
    '@keyframes bcNod{0%,100%{transform:rotate(0)}50%{transform:rotate(-5deg)}}@keyframes bcSwish{0%,100%{transform:rotate(-4deg)}50%{transform:rotate(9deg)}}',
    // ポン（出てくる）
    '@keyframes bcPopIn{0%{transform:scale(0);opacity:0}60%{transform:scale(1.18);opacity:1}80%{transform:scale(.94)}100%{transform:scale(1);opacity:1}}',
    '@keyframes bcFadeUp{0%{opacity:0;transform:translateY(8px)}100%{opacity:1;transform:none}}',
    '@keyframes bcFadeOut{0%{opacity:1}100%{opacity:0}}',
    // 1 ボードを一周（keyframes は ボードの 高さで 作る：dyn）
    // 2 ゴール板
    '.fxs .hb .bc-band{border-radius:7px;background:linear-gradient(#5DBB63,#3E9A48);box-shadow:inset 0 2px 0 rgba(255,255,255,.55),inset 0 -2px 0 rgba(0,0,0,.18),0 2px 4px rgba(0,0,0,.25)}',
    '.fxs .hb .bc-band::before{content:"";position:absolute;left:0;right:0;top:-5px;height:3px;border-radius:2px;background:#FFFFFF;box-shadow:0 1px 1px rgba(0,0,0,.25)}',
    '.fxs .hb.bcgo .bc-goal-run{animation:bcGoalRun 1s cubic-bezier(.25,.6,.35,1) both}@keyframes bcGoalRun{0%{transform:translateX(-330px)}100%{transform:none}}',
    '.fxs .hb:not(.bcgo):not(.bcst) .bc-goal-run{transform:translateX(-330px)}',
    '.fxs .hb .bc-goal-txt{opacity:0}.fxs .hb.bcgo .bc-goal-txt{animation:bcPopIn .5s cubic-bezier(.2,1.4,.4,1) .7s both}.fxs .hb.bcst .bc-goal-txt{opacity:1}',
    // 3 ひょっこり
    '.fxs .hb:not(.bcgo):not(.bcst) .bc-peek{transform:translateY(-64px)}',
    '.fxs .hb.bcgo .bc-peek{animation:bcPeek .7s cubic-bezier(.3,1.4,.5,1) both,bcPeekT 3.4s ease-in-out .8s infinite}',
    '@keyframes bcPeek{0%{transform:translateY(-64px)}100%{transform:none}}@keyframes bcPeekT{0%,100%{transform:rotate(0)}30%{transform:rotate(-7deg)}60%{transform:rotate(5deg)}}',
    // 4 上でお昼寝
    '.fxs .hb.bcgo .bc-nap .bcTl{animation:bcNapT 2.4s ease-in-out infinite}@keyframes bcNapT{0%,100%{transform:rotate(-4deg)}50%{transform:rotate(14deg)}}',
    '.fxs .hb.bcgo .bc-nap .bcBr{animation:bcBreath 3.2s ease-in-out infinite}@keyframes bcBreath{0%,100%{transform:scaleY(1)}50%{transform:scaleY(1.035)}}',
    '.fxs .hb .bc-z b{position:absolute;font:400 16px/1 "Dela Gothic One","BIZ UDPGothic",sans-serif;color:#FFFFFF;-webkit-text-stroke:3px var(--bcA,#5A6BC8);paint-order:stroke fill;opacity:0}',
    '.fxs .hb.bcgo .bc-z b{animation:bcZ 3s ease-out infinite}.fxs .hb.bcgo .bc-z b:nth-child(2){animation-delay:1s}.fxs .hb.bcgo .bc-z b:nth-child(3){animation-delay:2s}',
    '.fxs .hb.bcst .bc-z b{opacity:1}.fxs .hb.bcst .bc-z b:nth-child(2){transform:translate(12px,-14px) scale(1.15)}.fxs .hb.bcst .bc-z b:nth-child(3){transform:translate(24px,-30px) scale(1.3)}',
    '@keyframes bcZ{0%{opacity:0;transform:translate(0,0) scale(.7)}20%{opacity:1}80%{opacity:1}100%{opacity:0;transform:translate(26px,-34px) scale(1.35)}}',
    // 5 ぶら下がり
    '.fxs .hb.bcgo .bc-hang{animation:bcSwing 1.8s ease-in-out infinite}@keyframes bcSwing{0%,100%{transform:rotate(-4deg)}50%{transform:rotate(4deg)}}',
    '.fxs .hb.bcgo .bc-hang .bcPd1{animation:bcPedal .5s ease-in-out infinite}.fxs .hb.bcgo .bc-hang .bcPd2{animation:bcPedal .5s ease-in-out infinite -.25s}',
    '@keyframes bcPedal{0%,100%{transform:rotate(-22deg)}50%{transform:rotate(22deg)}}',
    '.fxs .hb.bcgo .bc-hang .bcTl{animation:bcSwish 1.2s ease-in-out infinite}',
    // 6 ハズレの励まし
    '.fxs .hb.bcgo .bc-cheer .bcf{animation:bcLean 2.8s ease-in-out infinite}@keyframes bcLean{0%,100%{transform:rotate(9deg)}50%{transform:rotate(12deg)}}',
    '.fxs .hb .bc-cheer .bcf{transform:rotate(10deg);transform-origin:50% 100%}',
    '.fxs .hb.bcgo .bc-cheer .bcUp{animation:bcPump 1.4s ease-in-out infinite}@keyframes bcPump{0%,100%{transform:rotate(0)}40%{transform:rotate(-16deg)}60%{transform:rotate(-12deg)}}',
    '.fxs .hb .bc-bub{opacity:0}.fxs .hb.bcgo .bc-bub{animation:bcPopIn .55s cubic-bezier(.2,1.4,.4,1) .35s both}.fxs .hb.bcst .bc-bub{opacity:1}',
    // 7 観客席
    '.fxs .hb .bc-rail{border-radius:6px;background:linear-gradient(var(--bcA,#E2A23B),color-mix(in srgb,var(--bcA,#E2A23B) 70%,#000));box-shadow:inset 0 2px 0 rgba(255,255,255,.5),0 2px 4px rgba(0,0,0,.3)}',
    '.fxs .hb.bcgo .bc-fan.clap .bcf{animation:bcHop .5s ease-in-out 5 alternate}@keyframes bcHop{0%{transform:translateY(0)}100%{transform:translateY(-6px)}}',
    '.fxs .hb.bcgo .bc-fan.clap .bcCl1{animation:bcClapL .2s ease-in-out 12 alternate}.fxs .hb.bcgo .bc-fan.clap .bcCl2{animation:bcClapR .2s ease-in-out 12 alternate}',
    '@keyframes bcClapL{0%{transform:translateX(-4px) rotate(-8deg)}100%{transform:translateX(3px) rotate(4deg)}}@keyframes bcClapR{0%{transform:translateX(4px) rotate(8deg)}100%{transform:translateX(-3px) rotate(-4deg)}}',
    '.fxs .hb.bcgo .bc-fan:nth-child(2n) .bcf{animation-delay:.12s}',
    '.fxs .hb .bc-say{opacity:0}.fxs .hb.bcgo .bc-say{animation:bcPopIn .5s cubic-bezier(.2,1.4,.4,1) both,bcFadeOut .5s ease-in 3.4s forwards}.fxs .hb.bcst .bc-say{opacity:1}',
    // 8 自撮り
    '.fxs .hb .bc-flash{opacity:0;border-radius:50%;background:radial-gradient(circle,#FFFFFF 0,rgba(255,255,255,.85) 30%,rgba(255,255,255,0) 70%)}',
    '.fxs .hb.bcgo .bc-flash{animation:bcFlash 4.6s ease-out .6s infinite}@keyframes bcFlash{0%{opacity:0;transform:scale(.4)}3%{opacity:1;transform:scale(1)}12%{opacity:0;transform:scale(1.2)}100%{opacity:0}}',
    '.fxs .hb .bc-pasha{opacity:0}.fxs .hb.bcgo .bc-pasha{animation:bcPasha 4.6s ease-out .6s infinite}.fxs .hb.bcst .bc-pasha{opacity:1}',
    '@keyframes bcPasha{0%{opacity:0;transform:scale(.6)}4%{opacity:1;transform:scale(1.15)}8%{transform:scale(1)}40%{opacity:1}50%{opacity:0}100%{opacity:0}}',
    // 9 くわえて持つ：ボードが 口の 所を 中心に 少し ゆれる
    '.fxs .hb.bcgo.bcx-bite .rb{transform-origin:46px 2px;animation:bcBite 3s ease-in-out infinite}@keyframes bcBite{0%,100%{transform:rotate(0)}50%{transform:rotate(1.3deg)}}',
    '.fxs .hb.bcgo .bc-bite{animation:bcBiteH 3s ease-in-out infinite;transform-origin:42px 70px}@keyframes bcBiteH{0%,100%{transform:rotate(0)}50%{transform:rotate(1.6deg)}}',
    // 10 馬がボード発表：ボードと 前足が いっしょに 少し 上下
    '.fxs .hb.bcgo.bcx-stand .rb,.fxs .hb.bcgo .bc-hold{animation:bcHold 2.6s ease-in-out infinite}@keyframes bcHold{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}',
    '.fxs .hb.bcgo .bc-stand-h .bcEr{animation:bcEar 3.6s ease-in-out infinite}@keyframes bcEar{0%,86%,100%{transform:rotate(0)}90%{transform:rotate(-12deg)}94%{transform:rotate(6deg)}}',
    '.fxs .hb.bcgo .bc-legs .bcTl{animation:bcSwish 1.6s ease-in-out infinite}',
    // 12 蹄のハンコ
    '.fxs .hb .bc-leg{opacity:0}.fxs .hb.bcgo .bc-leg{animation:bcStampL .9s cubic-bezier(.5,0,.5,1) .15s both}',
    '@keyframes bcStampL{0%{opacity:1;transform:translateY(-190px)}34%{opacity:1;transform:translateY(0)}52%{opacity:1;transform:translateY(-6px)}100%{opacity:0;transform:translateY(-200px)}}',
    '.fxs .hb .bc-stamp{opacity:0}.fxs .hb.bcgo .bc-stamp{animation:bcStampI .4s cubic-bezier(.2,1.2,.4,1) .45s both}.fxs .hb.bcst .bc-stamp{opacity:.95}',
    '@keyframes bcStampI{0%{opacity:0;transform:scale(1.6)}60%{opacity:.95;transform:scale(.94)}100%{opacity:.95;transform:scale(1)}}',
    // 13 お花が咲く
    '.fxs .hb .bc-fl{transform-origin:50% 100%}.fxs .hb:not(.bcgo):not(.bcst) .bc-fl{transform:scale(0)}',
    '.fxs .hb.bcgo .bc-fl{animation:bcBloom .7s cubic-bezier(.2,1.4,.4,1) var(--d,0s) both,bcSway 3.2s ease-in-out calc(var(--d,0s) + .8s) infinite}',
    '@keyframes bcBloom{0%{transform:scale(0) rotate(-20deg)}70%{transform:scale(1.12) rotate(4deg)}100%{transform:scale(1) rotate(0)}}@keyframes bcSway{0%,100%{transform:rotate(-4deg)}50%{transform:rotate(4deg)}}',
    // 14〜17 登場の しかた：.hb の アニメーションの 名前・長さ・速さだけ 入れかえる（いつ 出るかは その 演出の まま）
    '.fxs .hb.bce-pop{animation-name:bcEPop!important;animation-duration:1s!important;animation-timing-function:linear!important;transform-origin:50% 100%}',
    '@keyframes bcEPop{0%{opacity:0;transform:translateY(300px) scale(.55)}34%{opacity:1;transform:translateY(-22px) scale(1.03,.97)}48%{transform:translateY(0) scale(1.12,.86)}60%{transform:translateY(-6px) scale(.94,1.07)}72%{transform:scale(1.05,.96)}84%{transform:scale(.98,1.02)}100%{opacity:1;transform:none}}',
    '.fxs .hb.bce-drop{animation-name:bcEDrop!important;animation-duration:.95s!important;animation-timing-function:linear!important;transform-origin:50% 100%}',
    '@keyframes bcEDrop{0%{opacity:1;transform:translateY(-760px)}52%{transform:translateY(0) scale(1);animation-timing-function:ease-out}60%{transform:translateY(0) scale(1.1,.84)}72%{transform:translateY(-4px) scale(.96,1.05)}86%{transform:scale(1.02,.98)}100%{opacity:1;transform:none}}',
    '.fxs .hb.bce-flip{animation-name:bcEFlip!important;animation-duration:1s!important;animation-timing-function:linear!important}',
    '@keyframes bcEFlip{0%{opacity:0;transform:scale(.62)}10%{opacity:1;transform:scale(.8)}24%{transform:scale(.86) scaleX(.9) skewY(2deg)}45%{transform:scale(.94) scaleX(.02) skewY(5deg)}46%{transform:scale(.94) scaleX(.02) skewY(-5deg)}70%{transform:scale(1.03) scaleX(1.04) skewY(0)}85%{transform:scale(.99) scaleX(.98)}100%{opacity:1;transform:none}}',
    '.fxs .hb .bc-back{position:absolute;inset:0;z-index:4;border-radius:22px;pointer-events:none;overflow:hidden;opacity:0;',
    'background:repeating-linear-gradient(135deg,rgba(255,255,255,.14) 0 12px,rgba(255,255,255,0) 12px 24px),var(--bcA,#E2A23B);box-shadow:0 0 0 3px #FFFFFF,0 18px 38px rgba(0,0,0,.45)}',
    '.fxs .hb.bce-flip:not(.bcgo) .bc-back{opacity:1}.fxs .hb.bce-flip.bcin .bc-back{animation:bcBackOff 1s linear both}@keyframes bcBackOff{0%,45.4%{opacity:1}45.6%,100%{opacity:0}}',
    '.fxs .hb .bc-back svg{position:absolute;left:50%;top:50%;width:120px;height:120px;margin:-60px 0 0 -60px}',
    '.fxs .hb.bce-slide{animation-name:bcESlide!important;animation-duration:.78s!important;animation-timing-function:linear!important}',
    '@keyframes bcESlide{0%{opacity:0;transform:translateX(470px) skewX(-16deg)}40%{opacity:1;transform:translateX(-22px) skewX(7deg)}58%{transform:translateX(9px) skewX(-3deg)}76%{transform:translateX(-3px) skewX(1deg)}100%{opacity:1;transform:none}}',
    '.fxs .hb .bc-lines i{position:absolute;right:-30px;height:3px;border-radius:2px;background:linear-gradient(90deg,rgba(255,255,255,.95),rgba(255,255,255,0));opacity:0}',
    '.fxs .hb.bcin .bc-lines i{animation:bcLine .5s ease-out both}@keyframes bcLine{0%{opacity:0;transform:translateX(0) scaleX(.3)}20%{opacity:.95}100%{opacity:0;transform:translateX(70px) scaleX(1.4)}}',
    '.fxs .hb .bc-pita{opacity:0}.fxs .hb.bcgo .bc-pita{animation:bcPopIn .4s cubic-bezier(.2,1.4,.4,1) both,bcFadeOut .4s ease-in 1.4s forwards}',
    '.fxs .hb.bce-banner{animation-name:bcEBan!important;animation-duration:1s!important;animation-timing-function:cubic-bezier(.25,.65,.35,1)!important}',
    // 横断幕の 馬の うしろ足（走る）
    '.fxs .hb .run .bcR1{animation:bcRunL .3s ease-in-out infinite}.fxs .hb .run .bcR2{animation:bcRunL .3s ease-in-out infinite -.15s}',
    '@keyframes bcRunL{0%,100%{transform:translateY(0) rotate(0)}50%{transform:translateY(-13px) rotate(10deg)}}',
    '@keyframes bcEBan{0%{opacity:1;transform:translateX(-480px)}100%{opacity:1;transform:none}}',
    // 18 ふわふわ
    '.fxs .hb.bcgo.bcx-float .rb{animation:bcFloat 3.4s ease-in-out infinite}@keyframes bcFloat{0%,100%{transform:translateY(0) rotate(0)}30%{transform:translateY(-6px) rotate(-.5deg)}70%{transform:translateY(-2px) rotate(.5deg)}}',
    // 19 大きな的中：ドン！と 1回 はねる
    '.fxs .hb.bcgo.bcx-thump .rb{transform-origin:50% 100%;animation:bcThump .9s cubic-bezier(.3,0,.4,1) .1s both}',
    '@keyframes bcThump{0%{transform:none}30%{transform:translateY(-38px) scale(1.02)}52%{transform:translateY(0) scale(1.08,.88)}66%{transform:translateY(-5px) scale(.97,1.04)}82%{transform:scale(1.01,.99)}100%{transform:none}}',
    '.fxs .hb .bc-don{opacity:0}.fxs .hb.bcgo .bc-don{animation:bcDon .9s cubic-bezier(.2,1.3,.4,1) .55s both}.fxs .hb.bcst .bc-don{opacity:1;transform:rotate(-4deg)}',
    '@keyframes bcDon{0%{opacity:0;transform:scale(.3) rotate(-12deg)}40%{opacity:1;transform:scale(1.2) rotate(4deg)}60%{transform:scale(.96) rotate(-2deg)}100%{opacity:1;transform:scale(1) rotate(-4deg)}}',
    '.fxs .hb .bc-puff{opacity:0}.fxs .hb.bcgo .bc-puff{animation:bcPuff .7s ease-out var(--d,.55s) both}@keyframes bcPuff{0%{opacity:0;transform:translateX(0) scale(.4)}25%{opacity:.95}100%{opacity:0;transform:translateX(var(--x,20px)) scale(1.4)}}',
    // 20 ハズレ：少し かたむいて しょんぼり
    '.fxs .hb.bcx-droop .rb{transform-origin:330px 0;transition:transform .9s cubic-bezier(.3,.7,.4,1.2)}.fxs .hb.bcgo.bcx-droop .rb,.fxs .hb.bcst.bcx-droop .rb{transform:rotate(-3deg) translateY(6px)}',
    '.fxs .hb .bc-gloom{opacity:0}.fxs .hb.bcgo .bc-gloom{animation:bcFadeUp .8s ease-out .5s both}.fxs .hb.bcst .bc-gloom{opacity:1}',
    // 21 出世馬
    '.fxs .hb .bc-rib{opacity:0}.fxs .hb.bcgo .bc-rib{animation:bcPopIn .5s cubic-bezier(.2,1.4,.4,1) .25s both}.fxs .hb.bcst .bc-rib{opacity:1}',
    '.fxs .hb .bc-rib span{display:inline-block;padding:4px 14px 5px;border-radius:999px;font:400 15px/1.2 "Dela Gothic One","BIZ UDPGothic",sans-serif;color:#FFFFFF;letter-spacing:.04em;white-space:nowrap;',
    'background:var(--bcA,#E2A23B);box-shadow:0 0 0 2.5px #FFFFFF,0 3px 6px rgba(0,0,0,.3);text-shadow:0 1px 0 rgba(0,0,0,.25)}',
    '.fxs .hb .bc-rib.gold span{background:linear-gradient(180deg,#FFE27A,#F2A81E);color:#5A3A06;text-shadow:0 1px 0 rgba(255,255,255,.5)}',
    '.fxs .hb .bc-it{opacity:0}.fxs .hb.bcgo .bc-it{animation:bcPopIn .6s cubic-bezier(.2,1.4,.4,1) var(--d,0s) both}.fxs .hb.bcst .bc-it{opacity:1}',
    '.fxs .hb .bc-conf i{position:absolute;left:0;top:0;width:var(--w);height:var(--h);border-radius:2px;background:var(--c);opacity:0}',
    '.fxs .hb.bcgo .bc-conf i{animation:bcConf var(--t) cubic-bezier(.1,.7,.3,1) var(--d) both}',
    '@keyframes bcConf{0%{opacity:0;transform:translate(0,0) rotate(0)}8%{opacity:1}70%{opacity:1}100%{opacity:0;transform:translate(var(--x),var(--y)) rotate(var(--r))}}',
    '.fxs .hb .bc-beam{opacity:0;transform-origin:50% 0;background:linear-gradient(180deg,rgba(255,250,220,.55),rgba(255,240,180,.08));clip-path:polygon(44% 0,56% 0,100% 100%,0 100%);filter:blur(1.5px)}',
    '.fxs .hb.bcgo .bc-beam{animation:bcBeam 1.2s ease-out .2s both,bcBeamS 5s ease-in-out 1.4s infinite}.fxs .hb.bcst .bc-beam{opacity:.9}',
    '@keyframes bcBeam{0%{opacity:0}100%{opacity:.9}}@keyframes bcBeamS{0%,100%{transform:rotate(var(--a))}50%{transform:rotate(calc(var(--a) + 4deg))}}',
    '.fxs .hb .bc-dust i{position:absolute;left:var(--x);top:var(--y);width:var(--s);height:var(--s);opacity:0}',
    '.fxs .hb.bcgo .bc-dust i{animation:bcDust var(--t) linear var(--d) infinite}@keyframes bcDust{0%{opacity:0;transform:translateY(-16px) rotate(0)}15%{opacity:1}85%{opacity:1}100%{opacity:0;transform:translateY(46px) rotate(180deg)}}',
    '.fxs .hb.bcst .bc-dust i{opacity:.9}',
    '.fxs .hb .bc-rain i{position:absolute;left:var(--x);top:-200px;width:var(--w);opacity:0}',
    '.fxs .hb.bcgo .bc-rain i{animation:bcRain var(--t) cubic-bezier(.4,0,.8,.6) var(--d) both}@keyframes bcRain{0%{opacity:0;transform:translateY(0) rotate(var(--r0))}10%{opacity:1}85%{opacity:1}100%{opacity:0;transform:translateY(var(--y)) rotate(var(--r1))}}',
    // 22 ボードを持つ馬：下から ボードを かかえて 出てくる（1秒・着地で 少し はずむ）→ 頭と首・後ろ足が ぷるぷる（別々の 速さ）・しっぽを ときどき ふる・まばたき
    '.fxs .hb .bcx img{display:block;width:100%;height:100%;-webkit-user-drag:none;user-select:none}',
    '.fxs .hb.bce-carry{animation-name:bcECarry!important;animation-duration:1s!important;animation-timing-function:linear!important;transform-origin:50% 100%}',
    '@keyframes bcECarry{0%{opacity:1;transform:translateY(660px);animation-timing-function:cubic-bezier(.18,.72,.36,1)}46%{transform:translateY(-16px);animation-timing-function:ease-in}'
      + '60%{transform:translateY(0) scale(1.03,.95);animation-timing-function:ease-out}74%{transform:translateY(-5px) scale(.99,1.02);animation-timing-function:ease-in}86%{transform:translateY(0) scale(1.01,.99)}100%{opacity:1;transform:none}}',
    '.fxs .hb.bcgo .bc-hbh{animation:bcHbH 3.1s linear infinite,bcHbJ 1.4s linear 1.5s 1 none}.fxs .hb.bcgo .bc-hbl{animation:bcHbL 2.3s linear infinite -.7s,bcHbS .85s linear 1.5s 1 none}',
    '.fxs .hb.bcgo .bc-hbt{animation:bcHbT 7.9s ease-in-out infinite .6s}.fxs .hb .bc-hbe{opacity:0}.fxs .hb.bcgo .bc-hbe{animation:bcHbE 5.3s linear infinite .5s}',
    // 22：1回だけ ボードを 落としそうに なって あせる（出おわって 1.5秒後・1.4秒：ずり落ちる → 頭が びくっ・目を 見ひらく・汗・後ろ足が じたばた → 持ち直す → ふぅ）。
    //   まさちゃん「あと一回ボード落としそうになって焦るエフェクト追加して！」（大きく 動くのは 出てくる ときだけ の きまりの 例外：幻の 馬と 同じ）。前足は ボードと いっしょに 動く
    '.fxs .hb.bcgo.bcx-carry .rb{transform-origin:273px 0;animation:bcHbSlip 1.4s linear 1.5s 1 none}.fxs .hb.bcgo .bc-hbf{animation:bcHbSlip 1.4s linear 1.5s 1 none}',
    '.fxs .hb .bc-hbw,.fxs .hb .bc-hbx,.fxs .hb .bc-hbp,.fxs .hb .bc-hbd i{opacity:0}.fxs .hb.bcgo .bc-hbw{animation:bcHbW 1.4s linear 1.5s 1 none}',
    '.fxs .hb.bcgo .bc-hbx{animation:bcHbX .95s linear 1.55s 1 none}.fxs .hb.bcgo .bc-hbp{animation:bcHbP .8s ease-out 2.55s 1 none}',
    '.fxs .hb .bc-hbd i{position:absolute;width:7px;height:10px}.fxs .hb.bcgo .bc-hbd i{animation:bcHbD .75s cubic-bezier(.2,.7,.4,1) var(--d) 1 none}',
    hbCss(),
    // 前足（.bc-hbf）の 白い ふちと 影は 絵の 中（胸の 前と ボードの うしろへ 入る 切り口には 白い ふちを つけない ため：CSS の .bco は つけない）
    '.fxs .hb:not(.bchbv) .bc-hbsv,.fxs .hb.bchbv .bc-hbr{display:none}',
    // 21：8回目から（幻の 馬＝極ど的中の 紫の 馬：動画の 2まい bcx_ph0（暗闇に 目だけ）・bcx_ph1（顔が 見える）。ない とき（CI）は SVG の 紫の 馬）。
    //   舞台（.ov）の 上に 暗い 雷の 幕・馬・目の 光・鼻の 息・咆哮の 輪。ボードは 吹きとんで 3秒後に もどる
    '.fxs .bcph{position:absolute;inset:0;z-index:7;pointer-events:none;overflow:hidden}',
    '.fxs .bcph .phdk{position:absolute;inset:0;opacity:0;background:radial-gradient(ellipse at 50% 40%,rgba(40,18,84,.94),rgba(6,3,18,.98) 72%)}',
    '.fxs .bcph.on .phdk{animation:bcPhDk 3.75s ease-out both}@keyframes bcPhDk{0%{opacity:0}11%{opacity:1}88%{opacity:1}100%{opacity:0}}',
    '.fxs .bcph .phimg{position:absolute;inset:0;opacity:0;transform-origin:52% 36%}',
    '.fxs .bcph.on .phimg{animation:bcPhIn .45s ease-out .1s both,bcPhRoar .9s ease-out .72s both,bcPhOut .5s ease-in 3.2s forwards}',
    '@keyframes bcPhIn{0%{opacity:0}100%{opacity:1}}@keyframes bcPhOut{0%{opacity:1}100%{opacity:0;transform:scale(1.08)}}',
    '@keyframes bcPhRoar{0%{transform:none}10%{transform:translate(6px,-3px) scale(1.03)}20%{transform:translate(-6px,2px) scale(1.05)}32%{transform:translate(5px,-2px) scale(1.06)}46%{transform:translate(-4px,2px) scale(1.065)}62%{transform:translate(2px,-1px) scale(1.07)}100%{transform:scale(1.07)}}',
    '.fxs .bcph .phimg img,.fxs .bcph .phimg svg{position:absolute;left:0;top:0;width:100%;height:100%;object-fit:cover}',
    '.fxs .bcph .phimg .p1{opacity:0}.fxs .bcph.on .phimg .p1{animation:bcPhIn .45s ease-out .5s both}',
    '.fxs .bcph .pheye{position:absolute;left:52%;top:35.7%;width:150px;height:150px;margin:-75px 0 0 -75px;border-radius:50%;opacity:0;',
    'background:radial-gradient(circle,#FFFFFF 0,rgba(255,236,190,.95) 9%,rgba(255,170,70,.55) 26%,rgba(160,90,255,.25) 50%,rgba(0,0,0,0) 70%);mix-blend-mode:screen}',
    '.fxs .bcph .pheye::after{content:"";position:absolute;left:-170px;right:-170px;top:50%;height:2px;margin-top:-1px;background:linear-gradient(90deg,rgba(255,220,160,0),rgba(255,236,200,.95),rgba(255,220,160,0))}',
    '.fxs .bcph.on .pheye{animation:bcPhEye 3.3s ease-out .1s both}@keyframes bcPhEye{0%{opacity:0;transform:scale(.4)}12%{opacity:.85;transform:scale(.8)}20%{opacity:.6;transform:scale(.7)}24%{opacity:1;transform:scale(1.35)}38%{opacity:.85;transform:scale(1)}90%{opacity:.8}100%{opacity:0}}',
    '.fxs .bcph .phbr{position:absolute;left:94%;top:55%;width:90px;height:60px;margin:-30px 0 0 -10px;opacity:0;border-radius:50%;background:radial-gradient(ellipse at 30% 50%,rgba(255,255,255,.8),rgba(220,210,255,.35) 45%,rgba(255,255,255,0) 70%);filter:blur(2px)}',
    '.fxs .bcph.on .phbr{animation:bcPhBr 1.2s ease-out .78s both}@keyframes bcPhBr{0%{opacity:0;transform:translateX(-20px) scale(.4)}20%{opacity:.95}100%{opacity:0;transform:translateX(90px) scale(1.8)}}',
    '.fxs .bcph .phfl{position:absolute;inset:0;opacity:0;background:radial-gradient(ellipse at 50% 22%,rgba(225,210,255,.62),rgba(150,110,255,.22) 60%,rgba(0,0,0,0))}',
    '.fxs .bcph.on .phfl{animation:bcPhFl 3.75s linear both}@keyframes bcPhFl{0%,25%{opacity:0}26.5%{opacity:1}29.5%{opacity:0}49%{opacity:0}50.5%{opacity:.85}53.5%{opacity:0}73%{opacity:0}74.5%{opacity:1}77.5%{opacity:0}100%{opacity:0}}',
    '.fxs .bcph .phbolt{position:absolute;opacity:0;filter:drop-shadow(0 0 6px rgba(200,170,255,.95))}.fxs .bcph.on .phbolt{animation:bcPhFl 3.75s linear both}',
    '.fxs .bcph .phring{position:absolute;width:60px;height:60px;margin:-30px 0 0 -30px;border-radius:50%;border:3px solid rgba(214,196,255,.95);box-shadow:0 0 12px rgba(160,120,255,.8);opacity:0}',
    '.fxs .bcph.on .phring{animation:bcPhRing 1s ease-out both}@keyframes bcPhRing{0%{opacity:0;transform:scale(.3)}15%{opacity:.9}100%{opacity:0;transform:scale(4.6)}}',
    '.fxs .hb.bcfly{z-index:9!important}',
    // 飛んで いく ボードは すぐ うすく ぼかす（中の 字や 色の 縞が 画面を 横ぎって 点めつに ならない ように：test_bcx_flash.py）
    '.fxs .hb.bcfly .rb{animation:bcFly .75s cubic-bezier(.45,0,.8,.55) both}@keyframes bcFly{0%{transform:none;opacity:1;filter:blur(0)}12%{transform:translate(-10px,6px) rotate(-3deg);opacity:1;filter:blur(0)}30%{opacity:.3;filter:blur(7px)}100%{transform:translate(460px,-760px) rotate(38deg) scale(.55);opacity:.12;filter:blur(10px)}}',
    '.fxs .hb.bcback .rb{animation:bcBack .6s cubic-bezier(.4,0,1,1) both}@keyframes bcBack{0%{transform:translateY(-980px) rotate(8deg)}78%{transform:translateY(0) rotate(0) scale(1)}86%{transform:scale(1.08,.86)}94%{transform:scale(.97,1.03)}100%{transform:none}}',
    '.fxs .hb.bcwait .bc-it,.fxs .hb.bcwait .bc-rain,.fxs .hb.bcwait .bc-rib{visibility:hidden}',
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
  const sideVB = '0 -12 140 112', sideK = 112 / 140;          // 横から 見た 馬
  const frontVB = '-5 -8 110 110';                            // 前から 見た 頭
  const neckVB = '-5 -8 110 125';                             // 前から 見た 頭と 首
  const bodyVB = '-5 -8 115 170';                             // 前から 見た 頭と 胸と 足
  // 横から 見た 馬（cls に run＝走る・idle＝止まって うなずく）。o.flip＝左向き
  function horseSide(c, o) {
    o = o || {};
    const inner = `<g class="bcBd" style="transform-origin:70px 60px">${A.side(c, o)}</g>`;
    return o.flip ? `<g transform="translate(140 0) scale(-1 1)">${inner}</g>` : inner;
  }
  function confetti(n, seed, ox, oy, spread, up) {
    let h = '', s = seed || 1;
    const rnd = () => { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646; };
    const cols = ['#FF3B6A', '#FFD34D', '#3BC6FF', '#7CE05C', '#B56BFF', '#FF9F1A', '#FFFFFF'];
    for (let i = 0; i < n; i++) {
      const a = (up - spread / 2 + rnd() * spread) * Math.PI / 180, d = 60 + rnd() * 90;
      h += `<i style="left:${f(ox)}px;top:${f(oy)}px;--w:${f(4 + rnd() * 4)}px;--h:${f(7 + rnd() * 6)}px;--c:${cols[i % cols.length]};--x:${f(Math.cos(a) * d)}px;--y:${f(Math.sin(a) * d + 40 + rnd() * 30)}px;--r:${f(rnd() * 720 - 360)}deg;--t:${f(1.1 + rnd() * .6)}s;--d:${f(rnd() * .12)}s"></i>`;
    }
    return h;
  }

  // ---------- 22こ：部品を 作る（W＝350・H＝ボードの 高さ・sp＝ボードの 下の すき間・st＝動かさない） ----------
  const B = {};
  // 1 ボードを一周：前を 右へ（ボードの 下）→ うしろを 上へ → 上を 左へ（ボードの うしろ・上に 見える）→ うしろを 下へ
  B.orbit = o => {
    const w = 60, h = w * sideK;
    if (o.st) return { html: `<div class="bcx bco idle" style="left:6px;top:${f(o.H + 2)}px;width:${w}px;height:${f(h)}px"><svg viewBox="${sideVB}">${horseSide(PAL.chestnut, { pose: 'stand', cloth: true })}</svg></div>` };
    const n = 'bcOrb' + o.u, y1 = o.H + 2, y2 = -h + 4, xr = 350 - w / 2, xl = -w / 2;
    const k = `@keyframes ${n}{0%{transform:translate(-64px,${f(y1)}px);z-index:3}37.9%{z-index:3}38%{transform:translate(${f(xr)}px,${f(y1)}px);z-index:-1}`
      + `46.9%{transform:translate(${f(xr)}px,${f(y2)}px) scale(.92)}47%{transform:translate(${f(xr)}px,${f(y2)}px) scale(-.92,.92)}`
      + `85%{transform:translate(${f(xl)}px,${f(y2)}px) scale(-.92,.92)}99.9%{transform:translate(${f(xl - 20)}px,${f(y1)}px) scale(-1,1);z-index:-1}100%{transform:translate(-64px,${f(y1)}px);z-index:3}}`
      + `.fxs .hb.bcgo .bc-orbit{animation:${n} 6.2s linear infinite}.fxs .hb .bc-orbit{transform:translate(-64px,${f(y1)}px)}`;
    return { html: `<div class="bcx bco bc-orbit" style="left:0;top:0;width:${w}px;height:${f(h)}px"><svg class="run" viewBox="${sideVB}">${horseSide(PAL.chestnut, { pose: 'run', cloth: true })}</svg></div>`, css: k };
  };
  // 2 ゴール板：ボードの 下の 帯を 走って ゴール → 止まる
  B.goal = o => {
    const s = Math.min(1, o.sp / 92), bandY = o.H + 52 * s, w = 66 * s, h = w * sideK, post = 262;
    const top = bandY + 5 * s - (95 + 12) / 112 * h;
    let html = `<div class="bcx bc-band" style="left:6px;top:${f(bandY)}px;width:338px;height:${f(12 * s)}px"></div>`;
    html += box('bco', post - 14, bandY - 64 * s, 28, 66 * s, '-14 -64 28 66', A.goalPost(36));
    html += `<div class="bcx bco bc-goal-run${o.st ? ' idle' : ''}" style="left:270px;top:${f(top)}px;width:${f(w)}px;height:${f(h)}px"><svg class="${o.st ? '' : 'run'}" viewBox="${sideVB}">${horseSide(PAL.bay, { pose: o.st ? 'stand' : 'run', cloth: true })}</svg></div>`;
    html += `<div class="bcx bc-goal-txt" style="left:${post - 148}px;top:${f(bandY - 40 * s)}px;width:100px;height:30px;text-align:center"><span style="font:400 ${f(19 * s + 3)}px/1 'Dela Gothic One','BIZ UDPGothic',sans-serif;color:#FFFFFF;-webkit-text-stroke:4px var(--bcA,#E2A23B);paint-order:stroke fill">ゴール！</span></div>`;
    return { html, go: hb => { if (!o.st) settleAt(hb, '.bc-goal-run', 1000, 'run'); } };
  };
  // 3 ひょっこり：ボードの うしろから 下へ 顔を 出す（目は ボードの 下の ふちの すぐ 下）
  B.peek = o => {
    const w = 76, h = 76, top = o.H - 26;
    return { html: `<div class="bcx bk bco bc-peek" style="left:238px;top:${f(top)}px;width:${w}px;height:${h}px;transform-origin:50% 0">`
      + `<svg viewBox="${frontVB}">${A.front(PAL.chestnut, { expr: 'smile', blink: true })}</svg></div>` };
  };
  // 4 上でお昼寝：ボードの 上の ふちで ねそべる（左上）・Zzz
  B.nap = o => {
    const w = 124, h = w * sideK, top = -((89.5 + 12) / 112 * h) + 7;
    return { html: `<div class="bcx bco bc-nap" style="left:2px;top:${f(top)}px;width:${w}px;height:${f(h)}px"><svg viewBox="${sideVB}"><g class="bcBr" style="transform-origin:70px 90px">${A.side(PAL.palomino, { pose: 'lie', cloth: true, expr: 'sleep' })}</g></svg></div>`
      + `<div class="bcx bc-z" style="left:${f(w * .86)}px;top:${f(top + h * .12)}px;width:60px;height:60px"><b style="left:0;top:26px">Z</b><b style="left:12px;top:12px;font-size:19px">Z</b><b style="left:26px;top:-4px;font-size:22px">Z</b></div>` };
  };
  // 5 ぶら下がり：ボードの 右下の 角に 子馬
  B.hang = o => {
    const s = Math.min(1, o.sp / 104), w = 64 * s, h = 96 * s;
    return { html: `<div class="bcx bco bc-hang" style="left:${f(278 + (1 - s) * 20)}px;top:${f(o.H - 6)}px;width:${f(w)}px;height:${f(h)}px;transform-origin:50% 3px"><svg viewBox="0 0 100 150">${A.foal(PAL.foal)}</svg></div>` };
  };
  // 6 ハズレの励まし（ハズレの とき）：左下で ボードに もたれて「次いこ！」
  B.cheer = o => {
    const s = Math.min(1, o.sp / 132), w = 86 * s, h = w * 178 / 120;
    return { html: `<div class="bcx bc-cheer" style="left:${f(-14 * s)}px;top:${f(o.H - 6)}px;width:${f(w)}px;height:${f(h)}px"><div class="bcf bco"><svg viewBox="-5 -8 120 178">${A.front(PAL.chestnut, { expr: 'happy' })}${A.chest(PAL.chestnut, { arm: 'up' })}</svg></div></div>`
      + `<div class="bcx bco bc-bub" style="left:${f(84 * s + 6)}px;top:${f(o.H + 22 * s)}px;width:${f(148 * s)}px;height:${f(76 * s)}px;transform-origin:10% 90%">${A.bubble(138, 44, 'l', '次いこ！', 24)}</div>` };
  };
  // 7 観客席：ボードの 下に 5頭（的中は 拍手と 歓声・ハズレは 見守る）
  B.crowd = o => {
    const s = Math.min(1, o.sp / 96), cols = ['chestnut', 'gray', 'palomino', 'bay', 'white'];
    const says = o.miss ? ['', 'ドンマイ！', '', '次こそ！', ''] : ['わー！', '', 'すごい！', '', 'おめでとう！'];
    const ex = o.miss ? ['oh', 'sad', 'smile', 'sad', 'oh'] : ['cheer', 'happy', 'cheer', 'happy', 'cheer'];
    const w = 62 * s, h = w * 125 / 110, top = o.H + 44 * s, railY = top + h * .78;
    let html = '';
    for (let i = 0; i < 5; i++) {
      const c = PAL[cols[i]], x = 6 + i * 68 * (338 / 340) + (68 - 62) * s / 2;
      const clap = o.miss ? '' : `<g class="bcCl1" style="transform-origin:40px 108px">${A.hoof(c, 40, 92, 160, 16, 11)}</g><g class="bcCl2" style="transform-origin:60px 108px">${A.hoof(c, 60, 92, 200, 16, 11)}</g>`;
      html += `<div class="bcx bc-fan${o.miss ? '' : ' clap'}" style="left:${f(x)}px;top:${f(top)}px;width:${f(w)}px;height:${f(h)}px"><div class="bcf bco"><svg viewBox="${neckVB}">${A.front(c, { expr: ex[i], neck: true, blink: true })}${clap}</svg></div></div>`;
      if (says[i]) html += `<div class="bcx bco bc-say" style="left:${f(x + w / 2 - 50)}px;top:${f(top - 44 * s)}px;width:100px;height:${f(48 * s)}px;--d:${i * .25}s;animation-delay:${f(.2 + i * .22)}s,3.4s">${A.bubble(Math.max(70, says[i].length * 15 + 18), 30, 'r', says[i], 15)}</div>`;
    }
    html += `<div class="bcx bc-rail" style="left:0;top:${f(railY)}px;width:350px;height:${f(12 * s)}px;z-index:4"></div>`;
    return { html, go: () => { if (!o.st && !o.miss) snd('clap'); } };
  };
  // 8 自撮り：ボードの 右上で 自撮り（スマホに ボードも 入る）
  B.selfie = o => {
    const w = 124, h = w * 220 / 175, top = -(158 + 50) / 220 * h + 3, left = 300 - (50 + 60) / 175 * w;
    const px = left + (-52 + 60) / 175 * w + 8, py = top + (-38 + 50) / 220 * h + 12;
    return { html: `<div class="bcx bco bc-selfie idle" style="left:${f(left)}px;top:${f(top)}px;width:${f(w)}px;height:${f(h)}px"><svg viewBox="-60 -50 175 220">`
      + `${A.front(PAL.gray, { expr: 'wink' })}${A.chest(PAL.gray, { arm: 'stick', stick: [-34, -12] })}<g transform="translate(-52 -38) rotate(-20)">${A.phone(22, 38)}</g></svg></div>`
      + `<div class="bcx bc-flash" style="left:${f(px - 30)}px;top:${f(py - 30)}px;width:60px;height:60px"></div>`
      + `<div class="bcx bc-pasha" style="left:${f(px - 70)}px;top:${f(py - 30)}px;width:80px;height:26px;text-align:center"><span style="font:400 17px/1 'Dela Gothic One','BIZ UDPGothic',sans-serif;color:#FFFFFF;-webkit-text-stroke:3.5px var(--bcA,#E2A23B);paint-order:stroke fill">パシャ！</span></div>`,
      go: hb => { if (!o.st) shutterLoop(hb); } };
  };
  // 9 くわえて持つ：左上の すみを くわえる（頭は ボードの 前）
  B.bite = o => {
    const w = 84, h = 84, top = 2 - (85 + 8) / 110 * h;
    return { html: `<div class="bcx bco bc-bite" style="left:4px;top:${f(top)}px;width:${w}px;height:${h}px"><svg viewBox="${frontVB}">${A.front(PAL.bay, { expr: 'bite', blink: true })}</svg></div>` };
  };
  // 10 馬がボード発表：頭は ボードの 上（うしろ）・前足は ボードの 左右・下は 脚だけ
  B.stand = o => {
    const c = PAL.chestnut, w = 94, h = w * 125 / 110, top = -2 - (97 + 8) / 125 * h, hy = Math.round(o.H * .42);
    const s = Math.min(1, o.sp / 70), lh = 66 * s;
    let html = `<div class="bcx bk bco bc-stand-h" style="left:${f(175 - w / 2)}px;top:${f(top)}px;width:${w}px;height:${f(h)}px"><svg viewBox="${neckVB}">${A.front(c, { expr: 'happy', neck: true })}</svg></div>`;
    html += box('bco bc-hold', -12, hy - 9, 26, 18, '-13 -9 26 18', `<g transform="rotate(-90)">${A.hoof(c, 0, 8, 0, 6, 11)}</g>`);
    html += box('bco bc-hold', 336, hy - 9, 26, 18, '-13 -9 26 18', `<g transform="rotate(90)">${A.hoof(c, 0, 8, 0, 6, 11)}</g>`);
    // 下の 脚と しっぽ（ボードの うしろ）
    html += `<div class="bcx bk bco bc-legs" style="left:120px;top:${f(o.H - 14)}px;width:110px;height:${f(lh + 14)}px"><svg viewBox="0 -14 110 ${f(lh + 14)}" preserveAspectRatio="none">`
      + `<g class="bcTl" style="transform-origin:55px -4px"><path d="M52 -6 C44 ${f(lh * .3)} 40 ${f(lh * .6)} 44 ${f(lh * .9)} C50 ${f(lh * .7)} 56 ${f(lh * .5)} 60 -6 Z" fill="${c.n}"/></g>`
      + `<path d="M28 -14 L46 -14 L44 ${f(lh - 8)} L30 ${f(lh - 8)} Z" fill="${c.b}"/><path d="M64 -14 L82 -14 L80 ${f(lh - 8)} L66 ${f(lh - 8)} Z" fill="${c.s}"/>`
      + `${A.hoof(c, 37, lh, 0, 6, 15)}${A.hoof(c, 73, lh, 0, 6, 15)}</svg></div>`;
    return { html };
  };
  // 11 横断幕：2頭が 立って 両方の 前足を 上げ、ひづめで ボードを 持って 走って くる（登場）→ ピタッと 止まる
  B.banner = o => {
    const s = Math.min(1, o.sp / 150), w = 70 * s, k = w / 110, h = 224 * k, top = o.H - 2 - 7.5 * k;
    const one = (cx, c, flip) => `<div class="bcx bco bc-ban${o.st ? ' idle' : ''}" style="left:${f(cx - 55 * k)}px;top:${f(top)}px;width:${f(w)}px;height:${f(h)}px"><svg class="${o.st ? '' : 'run'}" viewBox="-5 -42 110 224">${A.carrier(c, { flip })}</svg></div>`;
    return { html: one(72, PAL.chestnut, false) + one(278, PAL.gray, true), go: hb => { if (!o.st) settleAt(hb, '.bc-ban', 0, 'run'); } };
  };
  // 12 蹄のハンコ（的中の とき）：見出しの 左の あいた 所
  B.stamp = o => {
    const t = o.title || { l: 108, t: 22, w: 134, h: 40 }, free = Math.max(36, t.l - 10);
    const r = Math.min(30, free / 2 - 2), cx = Math.max(r + 8, t.l / 2 + 3), cy = t.t + t.h / 2 + 4;
    const ink = o.redHd ? '#FFFFFF' : '#E0262E';
    return { html: box('bc-stamp', cx - r - 4, cy - r - 4, r * 2 + 8, r * 2 + 8, `${f(-r - 4)} ${f(-r - 4)} ${f(r * 2 + 8)} ${f(r * 2 + 8)}`, `<g transform="rotate(-14)">${A.stamp(r, ink)}</g>`, 'z-index:5')
      + box('bco bc-leg', cx - 15, cy - 124, 30, 128, '-15 -124 30 128', A.bigLeg(PAL.chestnut, 124), 'z-index:6'),
      go: () => { if (!o.st) setTimeout(() => snd('thump'), 470); } };
  };
  // 13 お花が咲く：下の ふちに 9本・上の 左右の すみに 少し。暗い テーマは アクセント色と 白・金
  B.flower = o => {
    const pal = o.dark ? ['var(--bcA,#E2A23B)', '#FFFFFF', '#FFD966', 'color-mix(in srgb,var(--bcA,#E2A23B) 55%,#FFFFFF)'] : ['#FF7FA8', '#FFD34D', '#FFFFFF', '#FF8A6B', '#B9A2FF'];
    const cc = o.dark ? ['#FFFFFF', '#FFC93C', '#B87A12', '#FFFFFF'] : ['#FFF1B8', '#FF9F1A', '#FFC93C', '#FFF1B8', '#FFF1B8'];
    let html = '', i = 0;
    const one = (x, y, hgt, r, bend) => { const k = i++ % pal.length; html += `<div class="bcx bco bc-fl" style="left:${f(x - 20)}px;top:${f(y - hgt - r - 4)}px;width:40px;height:${f(hgt + r + 8)}px;--d:${f(i * .07)}s">`
      + `<svg viewBox="-20 ${f(-hgt - r - 4)} 40 ${f(hgt + r + 8)}">${A.stem(hgt, bend)}<g transform="translate(${f(bend)} ${f(-hgt)})">${A.flower(r, pal[k], cc[k])}</g></svg></div>`; };
    const xs = [16, 52, 90, 128, 168, 210, 250, 290, 332];
    xs.forEach((x, j) => one(x, o.H + 40, 18 + (j % 3) * 6, 9 + (j % 2) * 3, (j % 2 ? 4 : -4)));
    one(10, 3, 16, 10, -4); one(36, 1, 12, 8, 3); one(342, 3, 16, 10, 4); one(318, 1, 10, 8, -3);
    return { html };
  };
  // 14 ぽよん・15 ドスン・16 カードめくり・17 すべり込み（登場の しかた）
  B.pop = o => ({ html: '', enter: 'pop', start: () => { snd('pop'); setTimeout(() => snd('boing'), 420); } });
  B.drop = o => ({ html: [[-6, -18], [356, 18]].map(([x, dx]) => `<div class="bcx bc-puff" style="left:${x - 18}px;top:${f(o.H - 16)}px;width:36px;height:24px;--x:${dx}px;--d:.5s"><svg viewBox="-18 -12 36 24">${A.puff(9)}</svg></div>`).join(''),
    enter: 'drop', start: () => setTimeout(() => snd('thump'), 480), go: () => {} });
  B.flip = o => ({ html: `<div class="bc-back" aria-hidden="true"><svg viewBox="-60 -60 120 120"><circle r="50" fill="rgba(255,255,255,.18)"/>`
    + `<path d="M-26 22 C-34 -6 -24 -38 0 -38 C24 -38 34 -6 26 22" fill="none" stroke="#FFFFFF" stroke-width="12" stroke-linecap="round"/>`
    + [[-28, 6], [-29, -14], [-18, -31], [28, 6], [29, -14], [18, -31]].map(p => `<circle cx="${p[0]}" cy="${p[1]}" r="2.6" fill="var(--bcA,#E2A23B)"/>`).join('')
    + `<text x="0" y="46" text-anchor="middle" font-family="'Dela Gothic One','BIZ UDPGothic',sans-serif" font-size="15" fill="#FFFFFF">結果発表</text></svg></div>`,
    enter: 'flip', start: () => snd('whoosh') });
  B.slide = o => {
    let lines = '';
    for (let i = 0; i < 6; i++) lines += `<i style="top:${f(o.H * (.12 + i * .15))}px;width:${60 + (i % 3) * 30}px;animation-delay:${f(.05 + i * .04)}s"></i>`;
    return { html: `<div class="bcx bc-lines" style="left:0;top:0;width:350px;height:${f(o.H)}px">${lines}</div>`
      + `<div class="bcx bc-pita" style="left:270px;top:-30px;width:90px;height:28px;text-align:center"><span style="font:400 18px/1 'Dela Gothic One','BIZ UDPGothic',sans-serif;color:#FFFFFF;-webkit-text-stroke:3.5px var(--bcA,#E2A23B);paint-order:stroke fill">ピタッ！</span></div>`,
      enter: 'slide', start: () => snd('whoosh') };
  };
  // 18 ふわふわ
  B.float = () => ({ html: '' });
  // 19 大きな的中（デカ的中から 上）：ドン！と 1回 はねる
  B.thump = o => ({ html: `<div class="bcx bc-don" style="left:236px;top:-58px;width:120px;height:50px;text-align:center"><span style="font:400 38px/1 'Dela Gothic One','BIZ UDPGothic',sans-serif;color:#FFE27A;-webkit-text-stroke:6px var(--bcA,#B0141B);paint-order:stroke fill;filter:drop-shadow(0 3px 2px rgba(0,0,0,.35))">ドン！</span></div>`
    + [[-6, -20], [356, 20]].map(([x, dx]) => `<div class="bcx bc-puff" style="left:${x - 18}px;top:${f(o.H - 16)}px;width:36px;height:24px;--x:${dx}px;--d:.55s"><svg viewBox="-18 -12 36 24">${A.puff(9)}</svg></div>`).join(''),
    go: () => { if (!o.st) setTimeout(() => snd('thump'), 560); } });
  // 20 ハズレ（ハズレの とき）：少し かたむいて しょんぼり（左上に どよーんの 線）
  B.droop = o => ({ html: box('bc-gloom', 6, -40, 54, 40, '0 0 54 40', [10, 24, 38].map((x, i) => `<path d="M${x} ${4 + i * 3} L${x} ${30 - i * 2}" stroke="#7E8CC8" stroke-width="3.4" stroke-linecap="round" opacity=".9"/>`).join('')) });
  // 21 出世馬：連続の 数で 飾りが 豪華に（1：クラッカーと 花束・2：金メダルと スポットライト・3：トロフィーと 金粉・4〜7：冠と 金の 札束・8〜：幻の 馬 → 冠と 札束）
  B.rise = o => {
    const tier = PT.riseTier(o.streak), H = o.H;
    if (!tier) return { html: '' };
    let html = '';
    const rib = (txt, gold) => `<div class="bcx bc-rib${gold ? ' gold' : ''}" style="left:0;top:${f(H + 10)}px;width:350px;text-align:center">${'<span>' + esc(txt) + '</span>'}</div>`;
    const lab = o.streak >= 2 ? `${o.streak}連続的中！` : '出世馬 スタート！';
    if (tier === 1) {
      html += box('bco bc-it', -14, H - 6, 46, 46, '-23 -23 46 46', `<g transform="translate(-2 10)">${A.cracker(-130, '#E2323A')}</g>`, '--d:.05s');
      html += box('bco bc-it', 318, H - 6, 46, 46, '-23 -23 46 46', `<g transform="translate(2 10)">${A.cracker(130, '#2F7BFF')}</g>`, '--d:.1s');
      html += `<div class="bcx bk bc-conf" style="left:0;top:0;width:0;height:0">${confetti(18, 7, 8, H, 70, -60)}${confetti(18, 11, 342, H, 70, -120)}</div>`;
      html += box('bco bc-it', 30, H + 28, 56, 64, '-28 -58 56 64', A.bouquet(), '--d:.3s');
      html += rib(lab, false);
      return { html, go: () => { if (!o.st) snd('cracker'); } };
    }
    if (tier === 2) {
      html += `<div class="bcx bk bc-beam" style="left:-120px;top:-260px;width:220px;height:${f(H + 300)}px;--a:-18deg;transform:rotate(-18deg)"></div><div class="bcx bk bc-beam" style="left:250px;top:-260px;width:220px;height:${f(H + 300)}px;--a:18deg;transform:rotate(18deg)"></div>`;
      html += box('bco bc-it', -22, -64, 54, 80, '-27 -6 54 80', A.medal(17), '--d:.2s');
      html += rib(lab, true);
      return { html, go: () => { if (!o.st) snd('chime'); } };
    }
    if (tier === 3) {
      html += box('bco bc-it', 272, H - 6, 80, 86, '-40 -80 80 86', A.trophy(80), '--d:.2s');
      let d = '';
      for (let i = 0; i < 26; i++) { const top = i % 2 === 0; d += `<i style="--x:${f(-14 + (i * 61) % 378)}px;--y:${f(top ? -150 + (i * 37) % 130 : H + 6 + (i * 29) % 120)}px;--s:${f(7 + (i % 3) * 3)}px;--t:${f(2.6 + (i % 4) * .5)}s;--d:${f((i % 6) * .4)}s"><svg viewBox="-10 -10 20 20">${A.spark(9, i % 3 ? '#FFE27A' : '#FFFFFF')}</svg></i>`; }
      html += `<div class="bcx bk bc-dust" style="left:0;top:0;width:350px;height:${f(H)}px">${d}</div>`;
      html += rib(lab, true);
      return { html, go: () => { if (!o.st) snd('chime'); } };
    }
    // 4〜：冠と 札束（たくさん）
    html += box('bco bc-it', 175 - 82, -98, 164, 100, '-82 -96 164 100', A.crown(160), '--d:.1s');
    const pile = (x, flip) => { let p = ''; [[0, 14, -6], [-16, 4, 8], [16, 4, -10], [-8, -8, 4], [10, -10, 12], [0, -20, -4]].forEach((b, j) => { p += `<g transform="translate(${flip ? -b[0] : b[0]} ${b[1]})">${A.bills(40, flip ? -b[2] : b[2])}</g>`; }); return box('bco bc-it', x - 40, H - 8, 80, 64, '-40 -34 80 64', p, '--d:.35s'); };
    html += pile(22, false) + pile(328, true);
    let rain = '';
    for (let i = 0; i < 20; i++) rain += `<i style="--x:${f(-26 + (i * 53) % 384)}px;--w:${f(34 + (i % 3) * 6)}px;--y:${f(H + 230 + (i % 4) * 30)}px;--t:${f(1.1 + (i % 5) * .12)}s;--d:${f(.15 + (i % 7) * .09)}s;--r0:${(i * 47) % 40 - 20}deg;--r1:${(i * 83) % 120 - 60}deg"><svg viewBox="-22 -12 44 24">${A.bills(40, 0)}</svg></i>`;
    html += `<div class="bcx bk bc-rain" style="left:0;top:0;width:350px;height:0">${rain}</div>`;
    html += rib(lab, true);
    return { html, phantom: tier === 8 && !o.st, go: () => { if (!o.st && tier !== 8) snd('coins'); } };
  };

  // 22 ボードを持つ馬（第4.108版・まさちゃんの 指定）：いちばん はじめの 頃の 馬。うしろから ボードを かかえて 下から 出てくる（着地で 少し はずむ）
  //   → 頭と首・後ろ足が ぷるぷる（重い ボードを 持って ふんばる：別々の 速さ）・しっぽを ときどき ふる・まばたき。前足（ボードの 上の ふちに かかる 短い 足と ひづめ）は 動かさない
  //   形は はじめの 絵（board_horse.py）と 同じ（まさちゃん 23:19・23:21「胴体の長さも2枚目の長さがベスト！」「二枚目くらいの前脚の長さが理想！」）
  //   絵 5まい（kisekae/r3d/fx/board_horse_parts.py。四角は その HBX と 同じ：頭と首・前足・目＝ボードの 左上から／後ろ足・しっぽ＝左下から の px。
  //   ボードの 高さが かわっても 上の 部品は 上の ふち・下の 部品は 下の ふちに つく）。頭と首・後ろ足・しっぽ＝ボードの うしろ（.bk）・前足＝ボードの 前
  //   絵が 読めない とき（絵なしの CI など）は SVG の 馬（.hb に .bchbv：hbVec）
  const HBX = { head: [196, -145, 128, 175], fore: [135, -48, 99, 46], hind: [242, -30, 100, 120], tail: [314, -46, 33, 90], eye: [248, -124, 26, 26], headO: [272, 9], hindO: [292, -21], tailO: [327, -64],
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
      // 前足（第4.111版）：ひづめの 下は ボードの 白い 輪の 上に のる（的中・大的中 3px／ハズレ 1.5px：ハズレは 1.5px 下げる）
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
  // 22：あせる 所の 部品（頭と首の 入れもの の 中：頭と いっしょに 動く）。見ひらいた 目（白目＋小さな 黒目）・汗 3つ・「！」の 形・鼻の 息（ふぅ）
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
  // 22 の 絵が ない とき：SVG の 馬（頭と首は ボードの うしろ・ひづめは 上の ふちに かける・下は 後ろ足と しっぽ）。hidden＝ふだんは かくす（絵が 読めない ときに 出す）
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
  // 22：ぷるぷる（頭と首 10回/秒・後ろ足 11回/秒：強い 時と 弱い 時が ある）・しっぽ（ばらばらの 間と 大きさで ふる）・まばたき の keyframes（決まった 乱数：いつも 同じ）
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
      // 22：落としそうに なる（ボードと 前足：右の 前足の 近くを 中心に 左が 大きく 下がる → じたばた → 持ち上げて 少し 上へ → もどる）
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

  // ---------- 走って きた 馬を 止める（いまの 足の 形から ふつうに 立つ 形へ なめらかに） ----------
  function settleAt(hb, sel, ms, cls) {
    const run = () => {
      if (!hb.isConnected) return;
      $$(sel, hb).forEach(el => {
        const svg = $('svg', el); if (!svg) return;
        const parts = $$('.bcL, .bcK, .bcBd, .bcH, .bcTl, .bcR1, .bcR2', svg);
        parts.forEach(p => { const t = getComputedStyle(p).transform; p.style.transform = t && t !== 'none' ? t : ''; });
        svg.classList.remove(cls);
        void svg.getBoundingClientRect();
        parts.forEach(p => { p.style.transition = 'transform .32s ease-out'; p.style.transform = 'rotate(0deg)'; });
        el.classList.add('idle');
      });
    };
    if (ms) setTimeout(run, ms); else run();
  }
  // 自撮りの シャッターの 音（4.6秒ごと）
  function shutterLoop(hb) {
    let n = 0;
    const tick = () => { if (!hb.isConnected || n++ > 12) return; snd('shutter'); setTimeout(tick, 4600); };
    setTimeout(tick, 620);
  }

  // ---------- 21：8回目からの 幻の 馬（極ど的中の 紫の 馬） ----------
  // 絵：動画（sd_film）の 2まい（暗闇に 目が 光る・顔が 見える）。ない とき（絵なしの CI など）は SVG の 紫の 馬（3Dの 馬の 形：bcx_phantom.js）
  function phantomSvg() {
    const P = window.TengelBoardPhantom; if (!P) return '';
    let wisp = '';
    const cr = P.crest || [];
    for (let i = 1; i < cr.length - 1; i++) {
      const [x, y] = cr[i], L = 90 + (i % 3) * 30;
      wisp += `<path d="M${x} ${y} C${x + 30} ${y - 10} ${x + L * .6} ${y + 20} ${x + L} ${y + 6}" fill="none" stroke-linecap="round" stroke="${i % 2 ? '#C9A8FF' : '#6E4BD8'}" stroke-width="${10 - (i % 3) * 2}" opacity=".7"/>`;
    }
    const tl = P.tail || [];
    if (tl.length) for (let k = 0; k < 5; k++) { const [x, y] = tl[0]; wisp += `<path d="M${x} ${y} C${x + 40} ${y + 60} ${x + 50 + k * 14} ${y + 150} ${x + 30 + k * 22} ${y + 230 + k * 10}" fill="none" stroke-linecap="round" stroke="${k % 2 ? '#C9A8FF' : '#6E4BD8'}" stroke-width="${12 - k}" opacity=".65"/>`; }
    return `<svg viewBox="-100 -120 1000 1240" preserveAspectRatio="xMidYMid meet" aria-hidden="true"><defs><linearGradient id="bcPhG" x1="0" y1="0" x2=".9" y2="1"><stop offset="0" stop-color="#2A1C5E"/><stop offset=".5" stop-color="#140D33"/><stop offset="1" stop-color="#07051A"/></linearGradient>`
      + `<radialGradient id="bcPhE"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".3" stop-color="#FFD58A"/><stop offset=".6" stop-color="rgba(255,150,60,.45)"/><stop offset="1" stop-color="rgba(255,150,60,0)"/></radialGradient></defs>`
      + `<g>${wisp}</g><path d="${P.all}" fill="url(#bcPhG)" fill-rule="evenodd" stroke="#B48CFF" stroke-width="3" style="filter:drop-shadow(0 0 10px rgba(170,120,255,.9))"/><path d="${P.hi}" fill="#D9C2FF" opacity=".55" fill-rule="evenodd"/>`
      + `<circle cx="${P.eye[0]}" cy="${P.eye[1]}" r="34" fill="url(#bcPhE)"/><circle cx="${P.eye[0]}" cy="${P.eye[1]}" r="6" fill="#FFFFFF"/></svg>`;
  }
  function boltSvg(seed) {
    let s = seed, x = 0, y = 0, d = 'M0 0';
    const rnd = () => { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646; };
    for (let i = 0; i < 9; i++) { x += (rnd() - .5) * 46; y += 26 + rnd() * 18; d += ` L${f(x)} ${f(y)}`; }
    return `<svg viewBox="-80 -6 160 ${f(y + 12)}" width="100%" height="100%" preserveAspectRatio="none"><path d="${d}" fill="none" stroke="rgba(170,140,255,.6)" stroke-width="12" stroke-linejoin="round"/><path d="${d}" fill="none" stroke="#FFFFFF" stroke-width="4" stroke-linejoin="round"/></svg>`;
  }
  const FXA = () => (window.__FX && window.__FX.assets) || {};
  // sched：時刻の しかけ（ふだんは setTimeout。光の 点めつの テストは 1/60秒ずつ 進める しかけを 渡す：test_bcx_flash.py）
  function phantom(stage, hb, sched) {
    const ov = $('.ov', stage) || stage; if (!ov || !hb.isConnected) return;
    hb.classList.add('bcwait');
    const as = FXA(), img0 = as.bcxph0, img1 = as.bcxph1;
    const L = document.createElement('div'); L.className = 'bcph'; L.setAttribute('aria-hidden', 'true');
    // 口の 前（動画の 絵：右の はし・上から 6割）。SVG の 馬の ときは その 口
    let mx = 372, my = 470;
    const P = window.TengelBoardPhantom;
    const vec = !img0 || !img1;
    if (vec && P) { mx = 390 * ((P.muzzle[0] + 100) / 1000); my = 844 * .5 + (P.muzzle[1] + 120 - 620) * (390 / 1000); }
    L.innerHTML = '<div class="phdk"></div>'
      + `<div class="phimg">${vec ? phantomSvg() : `<img class="p0" src="${esc(img0)}" alt=""><img class="p1" src="${esc(img1)}" alt="">`}${vec ? '' : '<div class="pheye"></div><div class="phbr"></div>'}</div>`
      + '<div class="phfl"></div>'
      + `<div class="phbolt" style="left:24px;top:40px;width:110px;height:320px">${boltSvg(5)}</div><div class="phbolt" style="left:262px;top:24px;width:116px;height:340px">${boltSvg(9)}</div>`
      + [0, .32, .64].map(d => `<i class="phring" style="left:${f(mx)}px;top:${f(my)}px;animation-delay:${f(.78 + d)}s"></i>`).join('');
    if (!vec) $$('img', L).forEach(im => { im.addEventListener('error', () => { const g = $('.phimg', L); if (g && !g.dataset.vec) { g.dataset.vec = '1'; g.innerHTML = phantomSvg(); } }); });
    ov.appendChild(L);
    const t = (fn, ms) => (sched || setTimeout)(() => { if (hb.isConnected) fn(); }, ms);
    t(() => L.classList.add('on'), 30);
    t(() => snd('rumble'), 60);
    t(() => snd('roar'), 720);
    t(() => hb.classList.add('bcfly'), 860);
    [1020, 1920, 2830].forEach(ms => t(() => snd('crack'), ms));
    t(() => { hb.classList.remove('bcfly'); hb.classList.add('bcback'); }, 3880);
    t(() => snd('thump'), 4350);
    t(() => { hb.classList.remove('bcwait'); const g = hb.classList.contains('bcgo'); hb.classList.remove('bcgo'); void hb.offsetWidth; if (g) hb.classList.add('bcgo'); snd('coins'); }, 4440);
    t(() => { hb.classList.remove('bcback'); L.remove(); }, 4560);
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
      else if (name === 'pop') tone('sine', 380, 900, .12, .22);
      else if (name === 'boing') { const o = c.createOscillator(), g = c.createGain(), l = c.createOscillator(), lg = c.createGain(); o.type = 'sine'; o.frequency.value = 260; l.frequency.value = 14; lg.gain.value = 60; l.connect(lg); lg.connect(o.frequency); env(g, t0, .01, .25, .5); o.connect(g); g.connect(out); o.start(t0); l.start(t0); o.stop(t0 + .6); l.stop(t0 + .6); keep(c, o, t0 + .6); keep(c, l, t0 + .6); }
      else if (name === 'whoosh') { const fl = noise(.45, .3, 'bandpass', 600, 1.2, 0, .12); fl.frequency.setValueAtTime(500, t0); fl.frequency.exponentialRampToValueAtTime(2600, t0 + .4); }
      else if (name === 'shutter') { noise(.03, .4, 'highpass', 2500, .7); noise(.05, .3, 'bandpass', 1800, 2, .07); }
      else if (name === 'clap') { for (let i = 0; i < 26; i++) noise(.05, .08 + Math.random() * .08, 'bandpass', 1400 + Math.random() * 900, 1.4, i * .085 + Math.random() * .04); }
      else if (name === 'cracker') { noise(.18, .5, 'lowpass', 2200, .8); tone('sine', 160, 60, .2, .3); noise(.5, .1, 'highpass', 4000, .7, .05, .02); }
      else if (name === 'chime') [1318.5, 1568, 2093, 2637].forEach((fq, i) => tone('sine', fq, fq, .7, .12, i * .08));
      else if (name === 'coins') { for (let i = 0; i < 10; i++) { const fq = 2600 + Math.random() * 1600; tone('triangle', fq, fq * 1.02, .18, .07, i * .06 + Math.random() * .03); } }
      else if (name === 'rumble') { noise(3.2, .5, 'lowpass', 140, .8, 0, .4); }
      else if (name === 'crack') { noise(.35, .55, 'highpass', 1200, .8); noise(1.2, .4, 'lowpass', 220, .8, .05, .02); }
      else if (name === 'slip') { tone('sine', 1100, 380, .24, .1); noise(.22, .07, 'bandpass', 1800, 2.2, .01, .02); }   // 22：ずり落ちる
      else if (name === 'phew') { noise(.38, .06, 'bandpass', 1100, .9, 0, .1); tone('sine', 660, 700, .14, .06, .02); tone('sine', 880, 930, .2, .05, .14); }   // 22：ふぅ
      else if (name === 'roar') {
        // 咆哮：のこぎり波の うなり（ゆれる 高さ）＋ ざらざらの 息（帯の 音）＋ ひずみ
        const o = c.createOscillator(), o2 = c.createOscillator(), vib = c.createOscillator(), vg = c.createGain(), ws = c.createWaveShaper(), g = c.createGain(), fl = c.createBiquadFilter();
        o.type = 'sawtooth'; o2.type = 'sawtooth'; o.frequency.setValueAtTime(95, t0); o.frequency.linearRampToValueAtTime(150, t0 + .35); o.frequency.linearRampToValueAtTime(118, t0 + 1.4); o.frequency.linearRampToValueAtTime(70, t0 + 2.1);
        o2.frequency.setValueAtTime(97, t0); o2.frequency.linearRampToValueAtTime(152, t0 + .35); o2.frequency.linearRampToValueAtTime(121, t0 + 1.4); o2.frequency.linearRampToValueAtTime(72, t0 + 2.1);
        vib.frequency.value = 23; vg.gain.value = 9; vib.connect(vg); vg.connect(o.frequency); vg.connect(o2.frequency);
        const k = new Float32Array(256); for (let i = 0; i < 256; i++) { const x = i / 128 - 1; k[i] = Math.tanh(x * 3.2); } ws.curve = k;
        fl.type = 'lowpass'; fl.frequency.setValueAtTime(700, t0); fl.frequency.linearRampToValueAtTime(1500, t0 + .4); fl.frequency.linearRampToValueAtTime(500, t0 + 2.1);
        g.gain.setValueAtTime(.0001, t0); g.gain.exponentialRampToValueAtTime(.32, t0 + .18); g.gain.setValueAtTime(.32, t0 + 1.3); g.gain.exponentialRampToValueAtTime(.0001, t0 + 2.2);
        o.connect(ws); o2.connect(ws); ws.connect(fl); fl.connect(g); g.connect(out);
        [o, o2, vib].forEach(x => { x.start(t0); x.stop(t0 + 2.3); keep(c, x, t0 + 2.3); });
        const br = noise(2.1, .28, 'bandpass', 900, .9, 0, .15); br.frequency.setValueAtTime(700, t0); br.frequency.linearRampToValueAtTime(1300, t0 + .4); br.frequency.linearRampToValueAtTime(600, t0 + 2);
      }
    } catch (e) { /* 音なし */ }
  }

  // ---------- ボードに つける ----------
  function lum(col) { const m = /rgba?\(([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)/.exec(col || ''); if (!m) return 1; const v = [m[1], m[2], m[3]].map(x => { x = +x / 255; return x <= .03928 ? x / 12.92 : Math.pow((x + .055) / 1.055, 2.4); }); return .2126 * v[0] + .7152 * v[1] + .0722 * v[2]; }
  function hueRed(col) { const m = /rgba?\(([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)/.exec(col || ''); if (!m) return false; const r = +m[1], g = +m[2], b = +m[3]; return r > 140 && r > g * 1.6 && r > b * 1.5; }
  function selected() { const w = WL(); try { return w && w.board ? w.board.active() : ''; } catch (e) { return ''; } }
  // stage：fx.js の 舞台（.fxs）・info：{ kind, quiet, calm, spec, item（ためす とき）, streak（ためす とき）}
  function decorate(stage, info) {
    try {
      info = info || {};
      const hb = stage && $('.hb', stage), rb = hb && $('.rb', hb);
      if (!rb || hb.dataset.bcx) return null;
      stopAll();
      const id = info.item || selected();
      const it = BY[id]; if (!it) return null;
      const kind = info.kind || 'hit', miss = kind === 'miss';
      if ((it.when === 'miss' && !miss) || (it.when === 'hit' && miss) || (it.when === 'big' && !BIG[kind])) return null;
      css();
      const st = !!(info.quiet || info.calm), H = rb.offsetHeight || 220;
      const sp = Math.max(40, CLOSE_TOP - HB_TOP - H - 10);
      const cs = getComputedStyle(rb), acc = (cs.getPropertyValue('--acc') || '').trim() || (cs.getPropertyValue('--logo') || '').trim() || '#E2A23B';
      const bg = cs.backgroundColor, hd = $('.hd', rb), hdBg = hd ? getComputedStyle(hd).backgroundColor : '';
      const dark = lum(bg) < .3;
      hb.style.setProperty('--bcA', acc);
      // 見出しの 字の 場所（ハンコ：ボードの 左上からの px。舞台の 縮みは もどす）
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
      if (it.id === 'banner' && !st) hb.classList.add('bce-banner');
      let started = false, gone = false;
      const go = () => {
        if (gone || !hb.isConnected) return; gone = true;
        hb.classList.remove('bcin'); hb.classList.add('bcgo');
        if (r.go) r.go(hb);
        if (r.phantom) setTimeout(() => phantom(stage, hb), 500);
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

  // ---------- 設定 › 結果ボードカスタム（買う・進み具合・選ぶ・見る） ----------
  const UI_CSS = [
    '#setBoard .bcbuy{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;align-items:center;border:1.5px solid var(--lamp,#E2A23B);border-radius:12px;padding:10px 12px;background:var(--surface-2)}',
    '#setBoard .bcbuy b{display:block;font-size:15px}#setBoard .bcbuy small{font-size:12px;color:var(--muted)}',
    '#setBoard .bcprog{border:1px solid var(--line);border-radius:12px;padding:10px 12px;background:var(--surface-2)}#setBoard .bcprog b{font-size:14px}',
    '#setBoard .bcprog .bar{height:8px;border-radius:4px;background:var(--surface);overflow:hidden;margin:6px 0 4px;border:1px solid var(--line)}#setBoard .bcprog .bar i{display:block;height:100%;background:linear-gradient(90deg,#FFC93C,#F28C1E)}',
    '#setBoard .bcgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px;margin-top:10px}',
    '#setBoard .bct{position:relative;display:flex;flex-direction:column;gap:3px;padding:6px 6px 8px;border:1.5px solid var(--line);border-radius:12px;background:var(--surface);cursor:pointer;text-align:left;min-width:0}',
    '#setBoard .bct.on{border-color:var(--ok,#2E9E5B);box-shadow:0 0 0 2px var(--ok,#2E9E5B) inset}',
    '#setBoard .bclk{position:absolute;right:5px;top:5px;z-index:2;width:24px;height:24px;border-radius:12px;background:rgba(0,0,0,.55);font:400 12px/24px sans-serif;text-align:center}',
    '#setBoard .bct:focus-visible{outline:2px solid var(--lamp,#E2A23B);outline-offset:2px}',
    '#setBoard .bcno{display:inline-block;min-width:20px;height:20px;margin-right:4px;padding:0 5px;border-radius:10px;background:var(--ink,#1F2433);color:var(--surface,#FFFFFF);font:700 11.5px/20px "BIZ UDPGothic",sans-serif;text-align:center;vertical-align:1px}',
    '#setBoard .bcnew{display:inline-block;margin-left:4px;padding:0 6px;border-radius:8px;background:#E2323A;color:#FFFFFF;font:700 10.5px/17px "BIZ UDPGothic",sans-serif;vertical-align:2px}',
    '#setBoard .bcn{font-weight:700;font-size:13.5px;line-height:1.3}#setBoard .bcd{font-size:11.5px;color:var(--muted);line-height:1.35}',
    '#setBoard .bcs{font-size:11.5px;font-weight:700;color:var(--muted)}#setBoard .bct.on .bcs{color:var(--ok,#2E9E5B)}',
    '#setBoard .bcsee{align-self:flex-start;margin-top:2px;padding:4px 10px;font-size:12px}',
    '#setBoard .bcmini{position:relative;width:100%;aspect-ratio:4/3;border-radius:8px;overflow:hidden;background:linear-gradient(180deg,#1E2650,#2E2A5A)}',
    '#setBoard .bcmini .bcmi{position:absolute;left:0;top:0;width:350px;height:170px;transform-origin:0 0;visibility:hidden}#setBoard .bcmini .bcmi.fit{visibility:visible}',
    '#setBoard .bcmini .hb{position:absolute;left:0;top:0;width:350px}',
    '#setBoard .bcmini .bcfake{position:relative;height:170px;border-radius:22px;padding:8px;background:#FFF8EC;box-shadow:0 0 0 2px rgba(255,255,255,.7),0 10px 20px rgba(0,0,0,.4)}',
    '#setBoard .bcmini .bcfake .fh{height:62px;border-radius:14px;background:var(--bcA,#2B3A67);display:flex;align-items:center;justify-content:center;font:400 30px/1 "Dela Gothic One","BIZ UDPGothic",sans-serif;color:#FFE27A;text-shadow:0 2px 0 rgba(0,0,0,.25)}',
    '#setBoard .bcmini .bcfake .fr{height:22px;margin:9px 6px 0;border-radius:8px;background:#E9E2D4}#setBoard .bcmini .bcfake .fr:nth-child(3){width:70%}',
    '#setBoard .bcmini .bcfake.miss .fh{color:#FFFFFF}',
    '#setBoard .bcmini .bchint{position:absolute;z-index:6;white-space:nowrap;font:400 26px/1 "Dela Gothic One","BIZ UDPGothic",sans-serif;color:#FFFFFF;-webkit-text-stroke:5px #E2A23B;paint-order:stroke fill}',
    '#setBoard .bcmini .bcarr{position:absolute;z-index:6;color:#FFFFFF;opacity:.9;font:700 40px/1 sans-serif;text-shadow:0 2px 3px rgba(0,0,0,.4)}',
    '#setBoard .bcmini .bcsl{position:absolute;z-index:6;height:5px;border-radius:3px;background:linear-gradient(90deg,rgba(255,255,255,.95),rgba(255,255,255,0))}'
  ].join('\n');
  let seeTier = 0, uiSeen = -1;
  const TIERS = [1, 2, 3, 4, 8];
  const SEEN_KEY = 'tengel.bcseen';
  function seenN() { if (uiSeen >= 0) return uiSeen; try { uiSeen = +localStorage.getItem(SEEN_KEY) || 0; } catch (e) { uiSeen = 0; } return uiSeen; }
  function setSeen(n) { uiSeen = n; try { localStorage.setItem(SEEN_KEY, String(n)); } catch (e) { /* なし */ } }
  // 小さな 見本（動かさない）：ボードの かわりの 四角＋その 飾り。動きの もの（14〜20）は 動きの しるし
  function thumbHtml(it) {
    const miss = it.when === 'miss', H = 170;
    const o = { H, W: 350, sp: 120, st: true, miss, big: it.when === 'big', kind: miss ? 'miss' : it.when === 'big' ? 'big' : 'hit', dark: false, title: { l: 112, t: 14, w: 126, h: 40 }, redHd: false, streak: it.id === 'rise' ? 4 : 0, u: 0 };
    let r = {};
    try { r = B[it.id](o) || {}; } catch (e) { r = {}; }
    let extra = '', tf = '';
    const hint = (x, y, t, st) => `<span class="bchint" style="left:${x}px;top:${y}px;${st || ''}">${t}</span>`, arr = (x, y, t) => `<span class="bcarr" style="left:${x}px;top:${y}px">${t}</span>`;
    if (it.id === 'pop') { extra = arr(118, 184, '↑') + hint(150, 190, 'ぽよん'); tf = 'transform:scale(1.06,.92);transform-origin:50% 100%;'; }
    if (it.id === 'drop') extra = arr(118, -58, '↓') + hint(150, -48, 'ドスン');
    if (it.id === 'flip') { tf = 'transform:perspective(700px) rotateY(28deg);'; extra = hint(236, -44, 'くるっ'); }
    if (it.id === 'slide') { tf = 'transform:skewX(-8deg);'; extra = hint(232, -44, 'シュッ') + [0, 1, 2].map(i => `<i class="bcsl" style="left:${362 + i * 4}px;top:${36 + i * 44}px;width:${54 - i * 10}px"></i>`).join(''); }
    if (it.id === 'float') { tf = 'transform:translateY(-8px);'; extra = hint(14, -46, 'ふわ〜', '-webkit-text-stroke-color:#5A8BE0'); }
    if (it.id === 'droop') tf = 'transform:rotate(-3deg) translateY(6px);transform-origin:330px 0;';
    const head = miss ? 'ハズレ' : it.when === 'big' ? 'デカ的中!!' : '的中！';
    return `<div class="bcmini" aria-hidden="true"><div class="bcmi"><div class="hb bcst bcx-${it.id}" style="--bcA:#2B3A67"><div class="rb bcfake${miss ? ' miss' : ''}" style="${tf}"><div class="fh">${head}</div><div class="fr"></div><div class="fr"></div></div>${r.html || ''}${extra}</div></div></div>`;
  }
  function card() {
    const set = $('#v-set'); if (!set) return;
    const after = $('#setKisekae');
    let c = $('#setBoard');
    if (!c) {
      css();
      c = document.createElement('div'); c.className = 'card setsec'; c.id = 'setBoard'; c.style.marginBottom = 'var(--gap)';
      c.innerHTML = '<h2>結果ボードカスタム</h2><div class="bcbody"></div>';
      c.addEventListener('click', onClick); c.addEventListener('keydown', onKey);
    }
    if (after && after.nextElementSibling !== c) after.insertAdjacentElement('afterend', c);
    else if (!after && !c.parentNode) set.appendChild(c);
    paint();
  }
  function paint() {
    const box = $('#setBoard .bcbody'), w = WL(); if (!box) return;
    const i = w && w.board ? w.board.info() : { owned: false, reads: 0, n: 0, next: null, sel: '', streak: 0 };
    const price = w && w.board ? w.board.price() : '2,200円';
    const seen = seenN();
    let h = '<p class="hint" style="margin:0 0 8px">結果のボード（的中・ハズレの 結果）に、馬の 飾りや 動きを つけられるよ。<b>どの 壁紙の ボードにも 使える</b>よ。使うのは 1つだけ。</p>';
    if (!i.owned) {
      h += `<div class="bcbuy"><div><b>結果ボードカスタム</b><small>${ITEMS.length}種・買い切り（1回 買えば ずっと）</small></div><button class="btn primary" type="button" data-bcact="buy">${esc(price)}で買う</button></div>`;
      h += '<p class="ptnote">買った あとに 読み込んだ レースの 数で、1つずつ 番号の 順に 解放されるよ（1〜5：5レースごと・6〜10：6レースごと・11〜15：7レースごと・16〜22：8レースごと／ぜんぶで 146レース）。読み直し（0P）と 5連の 予想は 数えないよ。「▶ 見る」で 買う 前にも ためせるよ。</p>';
      h += '<div class="row" style="margin-top:6px"><button class="btn ghost" type="button" data-bcact="restore">購入を復元</button></div>';
    } else {
      const nx = i.next, done = !nx, pct = done ? 100 : Math.round((i.reads - nx.from) / (nx.need - nx.from) * 100);
      h += `<div class="bcprog"><b>解放 ${i.n}/${ITEMS.length}</b>　<span class="muted" style="font-size:12.5px">買ってから 読み込んだ レース：${i.reads}</span><div class="bar"><i style="width:${pct}%"></i></div>`
        + `<span style="font-size:12.5px">${done ? 'ぜんぶ 解放したよ！' : `つぎの「${esc(nx.item.name)}」まで あと <b>${nx.left}</b>レース`}</span></div>`;
    }
    h += '<div class="bcgrid">';
    const none = i.owned && (!i.sel || i.sel === 'none');
    h += `<div role="button" tabindex="0" class="bct${none ? ' on' : ''}" data-bc="none" aria-pressed="${none}"><div class="bcmini" aria-hidden="true"><div class="bcmi"><div class="hb bcst"><div class="rb bcfake"><div class="fh">的中！</div><div class="fr"></div><div class="fr"></div></div></div></div></div>`
      + '<span class="bcn">なし</span><span class="bcd">いつもの ボード（飾りなし）</span>' + `<span class="bcs">${none ? '使用中' : i.owned ? 'タップで 使う' : ''}</span></div>`;
    ITEMS.forEach(it => {
      const open = i.owned && it.no <= i.n, on = open && i.sel === it.id, isNew = open && it.no > seen;
      const left = i.owned ? Math.max(0, it.need - i.reads) : 0;
      const st = on ? '使用中' : open ? 'タップで 使う' : i.owned ? `🔒 あと ${left}レース` : '🔒 買うと 解放';
      const when = it.when === 'miss' ? '（ハズレの とき）' : it.when === 'big' ? '（デカ的中から 上）' : it.when === 'hit' ? '（的中の とき）' : '';
      const see = it.id === 'rise' ? `▶ 見る（${TIERS[seeTier]}連続）` : '▶ 見る';
      h += `<div role="button" tabindex="0" class="bct${on ? ' on' : ''}${open ? '' : ' lock'}" data-bc="${it.id}" aria-pressed="${on}" aria-label="${it.no}. ${esc(it.name)}${on ? '（使用中）' : open ? '' : '（まだ）'}">`
        + `${open ? '' : '<span class="bclk" aria-hidden="true">🔒</span>'}${thumbHtml(it)}<span class="bcn"><span class="bcno">${it.no}</span>${esc(it.name)}${isNew ? '<span class="bcnew">NEW</span>' : ''}</span><span class="bcd">${esc(it.desc)}${esc(when && it.desc.indexOf('とき') < 0 ? when : '')}</span>`
        + `<span class="bcs">${st}</span><button class="btn ghost bcsee" type="button" data-bcact="see" data-id="${it.id}">${see}</button></div>`;
    });
    h += '</div>';
    h += '<p class="ptnote" style="margin-top:10px">「▶ 見る」で、ためしに 結果の ボードを 出すよ（まだ 解放して いない ものも 見られるよ）。出世馬は 押す たびに 1・2・3・4・8 連続を 見られるよ。<br>'
      + '「視差効果を減らす」か 設定の「演出を控えめにする」が オンなら、飾りは 止まった 形で 出るよ。<br>アプリを 消すと、解放の 進み具合は 0に もどるよ（買った ことは「購入を復元」で もどせるよ）。</p>';
    box.innerHTML = h;
    fitThumbs(); requestAnimationFrame(fitThumbs);
    if (i.owned && i.n > seen) { const v = $('#v-set'); if (v && !v.hidden) setTimeout(() => setSeen(i.n), 4000); }
  }
  // 見本の 枠：ボードと 飾り（見えて いる もの）が ぜんぶ 入る ように 縮めて まん中へ（はじめの 1回だけ 測る）
  const NOFIT = /bc-(beam|conf|rain|dust|lines|flash|leg|puff|back)/;
  function fitThumbs() {
    $$('#setBoard .bcmini').forEach(m => {
      const mi = $('.bcmi', m), hb = mi && $('.hb', mi), W0 = m.clientWidth, H0 = m.clientHeight; if (!hb || !W0 || !H0) return;
      if (!mi.dataset.box) {
        mi.style.transform = 'none';
        const r0 = mi.getBoundingClientRect(); let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
        const add = r => { if (!r.width || !r.height) return; x0 = Math.min(x0, r.left - r0.left); y0 = Math.min(y0, r.top - r0.top); x1 = Math.max(x1, r.right - r0.left); y1 = Math.max(y1, r.bottom - r0.top); };
        add($('.rb', hb).getBoundingClientRect());
        $$('.bcx,.bchint,.bcarr,.bcsl', hb).forEach(e => { if (NOFIT.test(e.className)) return; const cs = getComputedStyle(e); if (+cs.opacity === 0 || cs.display === 'none') return; add(e.getBoundingClientRect()); });
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
  function sample(it, kind) {
    const tri = { t: '3連単', state: '的中', hits: [[11, 8, 2]], n: 18 }, um = { t: '馬単', state: '的中', hits: [[11, 8]], n: 9 }, wd = { t: 'ワイド', state: '不的中', hits: [], n: 6 };
    const rows = kind === 'miss' ? [Object.assign({}, tri, { state: '不的中', hits: [] }), Object.assign({}, um, { state: '不的中', hits: [] }), wd] : kind === 'hit' ? [Object.assign({}, tri, { state: '不的中', hits: [] }), um, wd] : [tri, um, wd];
    return { r: 9, n: 14, rows, ranks: { 11: 11, 8: 8, 2: 2, 6: 1, 10: 3 } };
  }
  function see(id) {
    const it = BY[id], F = FX(); if (!it || !F || !F.preview) return;
    const kind = it.when === 'miss' ? 'miss' : it.when === 'big' ? 'big' : 'hit';
    let streak = 0;
    if (id === 'rise') { streak = TIERS[seeTier]; seeTier = (seeTier + 1) % TIERS.length; setTimeout(paint, 300); }
    try { F.prime(); } catch (e) { /* 音なし */ }
    F.preview(sample(it, kind), kind, { item: id, streak });
  }
  function toast(m, ms) { const t = $('#toast'); if (!t) return; t.textContent = m; t.hidden = false; clearTimeout(toast._t); toast._t = setTimeout(() => { t.hidden = true; }, ms || 3000); }
  async function onClick(e) {
    const a = e.target.closest('[data-bcact]'), w = WL();
    if (a) {
      e.stopPropagation();
      if (a.dataset.bcact === 'see') return see(a.dataset.id);
      if (!w || !w.board) return;
      if (a.dataset.bcact === 'buy') { await w.board.buy(a); paint(); return; }
      if (a.dataset.bcact === 'restore') { await w.board.restore(a); paint(); return; }
      return;
    }
    const t = e.target.closest('.bct'); if (!t || !w || !w.board) return;
    const id = t.dataset.bc, i = w.board.info();
    if (id === 'none') { if (!i.owned) { toast('先に 結果ボードカスタムを 買ってね（「▶ 見る」で ためせるよ）', 3200); return; } await w.board.select('none'); toast('結果ボードは いつもの 形に もどしたよ'); paint(); return; }
    const it = BY[id]; if (!it) return;
    if (!i.owned) { toast(`買うと、読み込んだ レースの 数で 番号の 順に 解放されるよ（「${it.name}」は ${it.need}レース）`, 3600); return; }
    if (it.no > i.n) { toast(`「${it.name}」は あと ${Math.max(0, it.need - i.reads)}レースで 解放（番号の 順に 解放されるよ）`, 3600); return; }
    if (await w.board.select(id)) { toast(`「${it.name}」を 使うよ`); paint(); }
  }
  function onKey(e) { if (e.key !== 'Enter' && e.key !== ' ') return; const b = e.target.closest('.bct'); if (!b || e.target !== b) return; e.preventDefault(); b.click(); }
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
  // 22「ボードを持つ馬」の 絵が 読めない（絵なしの CI など）→ その ボードは SVG の 馬に（error は 上へ 伝わらないので つかまえる 側で 聞く）
  document.addEventListener('error', e => { const t = e.target; if (t && t.classList && t.classList.contains('bchbi')) { const hb = t.closest('.hb'); if (hb) hb.classList.add('bchbv'); } }, true);
  document.addEventListener('tengel:wallet', () => { if ($('#setBoard')) paint(); });
  document.addEventListener('tengel:fx', e => { if (e.detail && e.detail.phase === 'close') stopAll(); });
  document.addEventListener('visibilitychange', () => { if (document.hidden) stopAll(); });
  window.addEventListener('pagehide', stopAll);
  document.addEventListener('tengel:tab', e => { if (e.detail === 'set') { card(); const w = WL(); if (w && w.board) w.board.products().then(paint).catch(() => {}); } });
  window.addEventListener('resize', fitThumbs);
  setTimeout(card, 60);

  window.TengelBoard = { on: true, items: () => ITEMS.slice(), decorate: decorate, snd: snd, see: see, paint: paint, _B: B, _phantom: phantom, _HBX: HBX };
  css();
})();
