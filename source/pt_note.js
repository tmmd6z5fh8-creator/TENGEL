// ポイントの お知らせ（第4.242版・App Store版だけ：build_pwa.py が index.html に 入れる）
//   まさちゃん 2026/11/29 00:09「ポイントが2500ポイント切ったら、ポイントの項目のところにびっくりマークつけてお知らせして！ 開くと、お世話をしてポイント大量ゲットを目指そう！
//   (ルーレットや特化ゾーン、チケット扉の画像をつけて)みたいなお知らせが出るようにして！ あと、TENGERカードバトルの連続勝利でもポイントは貰えるぞ！(カードバトルで勝利して
//   ポイントをもらっている画像)が出るようにして！ 説明書と枠のデザインは同じようなデザインでいいよ！カラーとか模様！」
//   ・上の 帯の ポイントの 札（points_ui.js の #ptsPill）は、使える ポイントが 2,500P（LOW）より 少ない とき「！」が つく → 押すと この お知らせ
//     （ほかの「ポイントを買う」ボタンは 今までどおり ポイントの 窓。お知らせの 下の ボタンからも ポイントの 窓へ）
//   ・見た目は 説明書（manual/manual.css）と 同じ：濃い 青緑の 台紙・金の 罫と 枠・上の 青緑の 光と 金の 細い たての 線の 模様・金の 字・◆の 見出し
//   ・絵（アプリの 中の 絵を 使う：ふえる ファイルは ない）
//     ルーレット＝神様馬の 台紙（rt_kamisama_plate2.webp）に 盤を 描く（tc/tc_fx.js の drawFace と 同じ 描き方・止まった 盤）。数は 神様馬が 来て いる 間の いちばん 上の 当たり
//       （tc/tc_app.js の PRIZES_VISIT：10000P か 20000P）。盤の 置き方は tc_rt_geom.json（読めない ときは 同じ 数の GEO0）
//     チケット扉＝開いた 扉（tk_door_open.webp）＋ 壁紙チケット（tk_ticket.webp：扉の まん中・tc_fx.js の ticketArt と 同じ 高さ）
//     ポイント特化ゾーン＝台・玉・矢印（tc_zn_back・ball・arrow.webp：tc_zn_geom.json の 置き方 ZN）
//     カードバトルの 勝ち＝ボード（cb_board.webp）・VS の 絵（cb_logo.webp）・「あなたの 勝ち！」・連勝の ポイントの 札（cb/cb_app.js の 終わりの 窓と 同じ 字・色）
//     絵が ない（GitHub の Mac の テスト：絵は リポジトリに 入れない）ときは 絵文字と 字だけ
//   ・字は 端末の 字（テーマの しぼった 字は 使わない：この ファイルの 字は kisekae/build_fonts.py の 字に 入れなくて よい）
//   ・いちばん 下に「ポイントを 購入」の 欄（まさちゃん 2026/11/29 00:43「下の方にポイントを購入の欄も作ってほしい！」）：ポイントの 窓と 同じ パック・サブスクの 一覧と
//     買う ボタン（points_ui.js の TengelWallet.shop：値段は App Store の 表示・買う 動きも 同じ）。お知らせを 開いて いる 間は 知らせ（toast）を お知らせの 上に 出す
//   window.TengelPtNote = { open, close, isOpen, LOW }
//
// 使い方（第4.243版：同じ 見た目の 窓で 使い方を 出す）
//   まさちゃん 2026/11/29 01:11「判定の画像読み込みの横にもビックリマークつけて、タップすると、どんな画像を読み込めばいいか(画像をつけて)、買い目予約の仕方(画像をつけて)、
//     結果入力、結果記録の説明が出てくるようにして！ あと、作戦会議の画像読み込みの横にもビックリマークをつけて、タップするとどんな画像を読み込めばいいか(画像つけて)
//     どんなことができるか画像つきで説明が出てくるようにして！」
//   01:14「あと、トレーニングセンターの玉落とし抽選の横にもビックリマークをつけて、画像をつけて説明が出てくるようにして！確率とかはいらないから、何色が何に当選してるかとか！
//     激馬熱馬の当選した瞬間もちょっと紹介してほしい！ 基本的には画像付きでお願い！」
//   ・「！」＝金の 丸（.hpq）：判定の「オッズ画像から読み取る」の 横（この ファイルが 入れる）・作戦会議の「📷 画像から読み取る」の 横（tc/tc_plan.js）・
//     トレーニングセンターの お世話チャレンジ（玉を 落とす 台）の 入口の 横（tc/tc_care.js）と 台の 上の「遊び方」（tc/tc_drop.js）
//   ・判定・作戦会議の 絵＝help/img/hp_*.webp（help/help_art.py が 架空の 画面と 今の アプリで 作る。build_pwa.py が manual/ に 入れる → アプリの Resources）
//   ・お世話チャレンジの 絵＝アプリの 中の 絵（台 tc_dp_base・馬バレ tc_dp_uma1〜7・保留 tc_dp_hold1〜7・激馬熱馬 tc_gk_end2）を 台の 置き方（tc_dp.json の 数）で 重ねる。
//     絵が ない（GitHub の Mac の テスト）ときは 色の 丸と 字だけ。当たりやすさ（確率）は 書かない
//   ・窓は いちばん 上（z-index 96：トレーニングセンター〈#tcOv 90〉・作戦会議〈#planHost 90〉の 上）。✕・「閉じる」・Esc で 閉じる
//   window.TengelHelp = { open(kind, from), close, isOpen, kind }   kind＝'judge'｜'plan'｜'drop'
(function () {
  'use strict';
  const D = document, $ = (s, r) => (r || D).querySelector(s);
  const LOW = 2500;
  const yen = n => Math.round(+n || 0).toLocaleString('ja-JP');
  const SANS = '"Hiragino Sans","Hiragino Kaku Gothic ProN","Noto Sans JP","Noto Sans CJK JP",system-ui,sans-serif';
  const SERIF = '"Hiragino Mincho ProN","Noto Serif CJK JP",serif';      // 盤の 数（tc_fx.js の SERIF と 同じ）
  const RT = { a: 10000, b: 20000, crop: [0, 0, 1024, 1280] };            // 盤の 数（上・下）と 台紙（1024×1536）の 見せる 所
  const GEO0 = { c: [432.4, 922.9], r: 289, face: [['#f7e0c5', '#eaccab'], ['#e2283a', '#be1622']], edge: '#5a1e10',
    parts: { knob: { x: 822, y: 794, w: 129, h: 129 }, stick: { x: 838, y: 902, w: 75, h: 178 }, ptr: { x: 368, y: 558, w: 137, h: 141 } } };
  const ST = { line: 'rgba(255,248,230,0.55)', star: ['#f8d672', '#d4a03a'] };      // tc_fx.js の RT_STYLE.kamisama
  const ZN = { w: 1066, h: 726, back: [4, 154, 1058, 568], ball: [393, 145, 280, 247], arrow: [423, 4, 221, 116] };      // tc_zn_geom.json の parts
  const pc = (v, n) => (v / n * 100).toFixed(2) + '%';
  const at = (r, W, H) => `left:${pc(r[0], W)};top:${pc(r[1], H)};width:${pc(r[2], W)};height:${pc(r[3], H)}`;
  const X = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>';
  const CSS = '#ptNote{position:fixed;inset:0;z-index:72;display:flex;flex-direction:column;background:#0a1b22;color:#e8f0f1;font-family:' + SANS + ';font-size:15px;line-height:1.7;letter-spacing:.01em;-webkit-text-size-adjust:100%;animation:ptnIn .22s ease-out both}'
    + '@keyframes ptnIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}'
    + '#ptNote *{box-sizing:border-box}'
    + '#ptNote .pnbar{flex:none;display:flex;align-items:center;gap:10px;padding:calc(var(--sat,0px) + 8px) 14px 8px;background:rgba(10,27,34,.94);border-bottom:1px solid rgba(217,180,90,.2)}'
    + '#ptNote .pnbar .pntt{flex:1;min-width:0;font-size:14px;font-weight:700;color:#f4dc96;letter-spacing:.06em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}'
    + '#ptNote .pnx{flex:none;display:grid;place-items:center;width:38px;height:38px;border-radius:50%;border:1px solid rgba(217,180,90,.42);background:rgba(217,180,90,.08);color:#f4dc96;padding:0;font:inherit;cursor:pointer}'
    + '#ptNote .pnx svg{width:18px;height:18px}'
    + '#ptNote .pnbd{flex:1;min-height:0;overflow:auto;-webkit-overflow-scrolling:touch;overscroll-behavior:contain;position:relative;isolation:isolate}'
    + '#ptNote .pnbd::before{content:"";position:absolute;left:0;right:0;top:0;height:540px;z-index:-1;pointer-events:none;'
    + 'background:radial-gradient(60% 55% at 50% 24%,rgba(92,202,214,.14),transparent 70%),repeating-linear-gradient(90deg,rgba(217,180,90,.045) 0 1px,transparent 1px 36px);'
    + '-webkit-mask-image:linear-gradient(#000 40%,transparent);mask-image:linear-gradient(#000 40%,transparent)}'
    + '#ptNote .pnin{max-width:560px;margin:0 auto;padding:20px 16px calc(var(--sab,0px) + 30px)}'
    + '#ptNote .pney{margin:0;font-size:12.5px;letter-spacing:.16em;color:#d9b45a;font-weight:700}'
    + '#ptNote h2{margin:6px 0 10px;font-weight:900;font-size:clamp(24px,7.2vw,32px);line-height:1.32;letter-spacing:.02em}'
    + '#ptNote h2,#ptNote h3,#ptNote p,#ptNote .pntip,#ptNote figcaption{word-break:keep-all;overflow-wrap:anywhere}'
    + 'html.ptnoteon .toast{z-index:80}'
    + '#ptNote .pngold{background:linear-gradient(180deg,#fbe9b0 0%,#e2bf66 46%,#a47a2c 100%);-webkit-background-clip:text;background-clip:text;color:transparent;-webkit-text-fill-color:transparent}'
    + '#ptNote .pnlead{margin:0;color:#a6bec3;font-size:14.5px}'
    + '#ptNote .pnsec{margin:26px 0 10px;font-size:13px;letter-spacing:.14em;color:#d9b45a;font-weight:700;display:flex;align-items:center;gap:10px}'
    + '#ptNote .pnsec::after{content:"";flex:1;height:1px;background:rgba(217,180,90,.2)}'
    + '#ptNote .pnbox{border:1px solid rgba(217,180,90,.42);border-radius:16px;background:linear-gradient(160deg,#153b47,#10303a);padding:14px 14px 16px;box-shadow:0 14px 34px rgba(0,0,0,.28)}'
    + '#ptNote h3{display:flex;align-items:flex-start;gap:10px;margin:0 0 8px;font-size:17px;line-height:1.5;font-weight:800;color:#f6efd9}'
    + '#ptNote h3::before{content:"";flex:none;width:8px;height:8px;margin-top:.62em;background:#d9b45a;transform:rotate(45deg)}'
    + '#ptNote p{margin:0 0 10px;font-size:14.5px;line-height:1.7}'
    + '#ptNote p b{color:#f4dc96}'
    + '#ptNote .pnmu{color:#a6bec3;font-size:13px}'
    + '#ptNote .pnart{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:8px;margin:12px 0 0}'
    + '#ptNote .pnt{position:relative;margin:0;display:flex;flex-direction:column;border-radius:12px;border:1px solid rgba(217,180,90,.42);overflow:hidden;background:#0b222a;box-shadow:0 10px 24px rgba(0,0,0,.35)}'
    + '#ptNote .pnt .pnpic{position:relative;display:block;aspect-ratio:4/5;background:radial-gradient(80% 70% at 50% 40%,#1b4a57,#0b222a)}#ptNote .pnt.pnwide{grid-column:1/-1}#ptNote .pnt.pnwide .pnpic{aspect-ratio:2/1}'
    + '#ptNote .pnt canvas{position:absolute;inset:0;width:100%;height:100%;display:block}'
    + '#ptNote .pnt img{position:absolute;display:block;-webkit-user-drag:none;user-select:none;pointer-events:none}'
    + '#ptNote .pnt figcaption{padding:7px 6px 8px;border-top:1px solid rgba(217,180,90,.3);background:linear-gradient(180deg,#12333d,#0c252d);text-align:center;line-height:1.3}'
    + '#ptNote .pnt figcaption b{display:block;font-size:13px;color:#fff;letter-spacing:.02em}'
    + '#ptNote .pnt figcaption span{display:block;margin-top:2px;font-size:12px;font-weight:800;color:#f4dc96;font-variant-numeric:tabular-nums}'
    + '#ptNote .pnt .pnem{position:absolute;inset:0;display:none;place-items:center;font-size:42px}'
    + '#ptNote .pnt.pnnone .pnem{display:grid}#ptNote .pnt.pnnone canvas,#ptNote .pnt.pnnone img{display:none}'
    + '#ptNote .pndoor .pnd{inset:0;width:100%;height:100%;object-fit:cover}'
    + '#ptNote .pndoor .pngl{position:absolute;left:50%;top:46%;width:86%;aspect-ratio:1;transform:translate(-50%,-50%);border-radius:50%;background:radial-gradient(closest-side,rgba(255,244,205,.8),rgba(255,214,120,.28) 55%,rgba(255,214,120,0));pointer-events:none}'
    + '#ptNote .pndoor .pntk{left:50%;top:46%;width:60%;height:auto;transform:translate(-50%,-50%) rotate(-7deg);filter:drop-shadow(0 6px 8px rgba(40,20,0,.45))}'
    + '#ptNote .pnt.pnnone .pngl{display:none}'
    + '#ptNote .pnzone .pnzb{position:absolute;left:50%;top:50%;height:86%;aspect-ratio:' + ZN.w + '/' + ZN.h + ';transform:translate(-50%,-50%)}'
    + '#ptNote .pngo{display:flex;align-items:center;justify-content:center;gap:8px;width:100%;min-height:48px;margin:14px 0 0;border:0;border-radius:999px;padding:10px 16px;font:800 15.5px/1.3 ' + SANS + ';color:#1d1405;cursor:pointer;'
    + 'background:linear-gradient(180deg,#f8e3a0,#e2bf66 55%,#c39a45);box-shadow:0 6px 16px rgba(0,0,0,.35),inset 0 1px 0 rgba(255,255,255,.55)}'
    + '#ptNote .pngo:active{transform:translateY(1px);box-shadow:0 3px 8px rgba(0,0,0,.35),inset 0 1px 0 rgba(255,255,255,.55)}'
    + '#ptNote .pngh{flex:1 1 0;min-width:0;min-height:44px;border:1px solid rgba(217,180,90,.42);border-radius:999px;background:rgba(217,180,90,.08);color:#f4dc96;font:700 14px/1.3 ' + SANS + ';padding:8px 12px;cursor:pointer}'
    + '#ptNote .pngh:active{background:rgba(217,180,90,.16)}'
    + '#ptNote .pngo:focus-visible,#ptNote .pngh:focus-visible,#ptNote .pnx:focus-visible{outline:2px solid #d9b45a;outline-offset:2px}'
    + '#ptNote .pntip{margin:12px 0 0;border-radius:14px;padding:11px 13px;font-size:14px;line-height:1.7;background:rgba(217,180,90,.08);border:1px solid rgba(217,180,90,.3)}'
    + '#ptNote .pntip .pnlab{display:inline-block;margin-right:6px;font-weight:800;font-size:12.5px;letter-spacing:.06em;color:#f4dc96}'
    + '#ptNote .pntip b{color:#f4dc96}'
    + '#ptNote .pncb{position:relative;margin:12px 0 0;aspect-ratio:16/9;border-radius:12px;border:1px solid rgba(217,180,90,.42);overflow:hidden;background:radial-gradient(90% 100% at 28% 50%,#2a5a35,#0b1d10);box-shadow:0 10px 24px rgba(0,0,0,.35)}'
    + '#ptNote .pncb .pnbg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}'
    + '#ptNote .pncb .pnsh{position:absolute;inset:0;background:radial-gradient(95% 95% at 72% 50%,rgba(8,5,2,.6),rgba(8,5,2,.8))}'
    + '#ptNote .pncb .pnci{position:absolute;inset:0;display:flex;align-items:center;gap:3%;padding:4% 4% 4% 3%}'
    + '#ptNote .pncb .pnlg{position:static;flex:none;height:88%;width:auto;aspect-ratio:1;object-fit:contain;filter:drop-shadow(0 6px 12px rgba(0,0,0,.6))}'
    + '#ptNote .pncb .pnrs{flex:1;min-width:0;display:flex;flex-direction:column;align-items:center;gap:4px;text-align:center;color:#fff1cf}'
    + '#ptNote .pncb .pnhd{font-weight:900;font-size:clamp(17px,5.4vw,25px);line-height:1.15;letter-spacing:.02em;background:linear-gradient(180deg,#fff3c4 0%,#ffd76a 38%,#e2a83e 62%,#9c6410 100%);'
    + '-webkit-background-clip:text;background-clip:text;color:transparent;-webkit-text-fill-color:transparent;filter:drop-shadow(0 2px 2px rgba(0,0,0,.6))}'
    + '#ptNote .pncb .pnsc{font-weight:900;font-size:clamp(14px,4.3vw,20px);line-height:1.15;color:#ffe9a8;letter-spacing:.1em;font-variant-numeric:tabular-nums}'
    + '#ptNote .pncb .pnst{font-size:12px;font-weight:800;line-height:1.3;color:#ffe07a}'
    + '#ptNote .pncb .pnptn{display:inline-flex;align-items:center;flex-wrap:wrap;justify-content:center;gap:0 4px;max-width:100%;padding:2px 10px 3px;border-radius:14px;border:1.5px solid #8fd6ff;'
    + 'background:rgba(110,190,255,.18);font-size:11.5px;font-weight:700;line-height:1.45;color:#fff1cf;box-shadow:0 0 14px rgba(143,214,255,.35)}'
    + '#ptNote .pncb .pnptn i{font-style:normal}#ptNote .pncb .pnptn b{color:#ffe07a;font-size:13.5px;font-weight:900}'
    + '#ptNote .pncb.pnnolg .pnlg{display:none}'
    + '#ptNote .pnfoot{margin:28px 0 0;padding-top:16px;border-top:1px solid rgba(217,180,90,.2);display:grid;gap:12px}'
    + '#ptNote .pnfoot .pnrow{display:flex;gap:8px}'
    + '#ptNote .pnshop h4{margin:16px 0 0;font-size:14px;letter-spacing:.06em;color:#d9b45a}#ptNote .pnshop h4:first-of-type{margin-top:4px}'
    + '#ptNote .pnshop .ptlist{display:grid;gap:8px;margin-top:8px}'
    + '#ptNote .pnshop .ptitem{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px;align-items:center;border:1px solid rgba(217,180,90,.3);border-radius:12px;padding:10px 12px;background:rgba(6,18,23,.45)}'
    + '#ptNote .pnshop .ptitem.on{border-color:rgba(127,216,170,.6);background:rgba(127,216,170,.08)}'
    + '#ptNote .pnshop .pn{font-weight:800;font-size:14.5px;line-height:1.45;color:#f6efd9}#ptNote .pnshop .pd{font-size:12px;line-height:1.5;color:#a6bec3}'
    + '#ptNote .pnshop .row{display:flex;align-items:center;gap:8px}#ptNote .pnshop .pp{font-weight:800;font-variant-numeric:tabular-nums;color:#f4dc96;white-space:nowrap}'
    + '#ptNote .pnshop .btn{display:inline-flex;align-items:center;justify-content:center;min-height:38px;border:0;border-radius:999px;padding:8px 16px;font:800 14px/1.2 ' + SANS + ';color:#1d1405;white-space:nowrap;cursor:pointer;'
    + 'background:linear-gradient(180deg,#f8e3a0,#e2bf66 55%,#c39a45);box-shadow:0 4px 10px rgba(0,0,0,.3),inset 0 1px 0 rgba(255,255,255,.55)}'
    + '#ptNote .pnshop .btn:disabled{opacity:.45;cursor:default}#ptNote .pnshop .btn:focus-visible{outline:2px solid #d9b45a;outline-offset:2px}'
    + '#ptNote .pnshop .chip{font-size:11.5px;font-weight:700;padding:1px 8px;border-radius:999px;border:1px solid rgba(127,216,170,.6);color:#7fd8aa;white-space:nowrap}'
    + '#ptNote .pnshop .ptnote{margin:8px 0 0;font-size:12px;line-height:1.6;color:#a6bec3}'
    + '#ptNote .pnshop .pngh{display:block;width:100%;margin-top:14px;flex:none}'
    + '@media (min-width:600px){#ptNote .pnart{grid-template-columns:repeat(3,minmax(0,1fr))}#ptNote .pnt.pnwide{grid-column:auto}#ptNote .pnt.pnwide .pnpic{aspect-ratio:4/5}#ptNote .pnzone .pnzb{height:auto;width:96%}}'
    + '@media (prefers-reduced-motion:reduce){#ptNote{animation:none}}';

  const img = src => new Promise(ok => { const i = new Image(); i.onload = () => ok(i); i.onerror = () => ok(null); i.src = src; });
  let geoP = null;
  const geo = () => geoP || (geoP = fetch('tc_rt_geom.json', { cache: 'force-cache' }).then(r => (r.ok ? r.json() : null)).then(g => (g && g.kamisama && g.kamisama.c && g.kamisama.face ? g.kamisama : GEO0)).catch(() => GEO0));
  // 盤（tc_fx.js の drawFace と 同じ：止まった 盤。上が a・下が b）
  function face(g, Gm, k) {
    const [cx, cy] = Gm.c, R = Gm.r, TAU = Math.PI * 2, N = 18, edge = Gm.edge || GEO0.edge;
    const line = (x0, y0, x1, y1, c, w) => { g.strokeStyle = c; g.lineWidth = w; g.beginPath(); g.moveTo(x0, y0); g.lineTo(x1, y1); g.stroke(); };
    const poly = (p, c) => { g.fillStyle = c; g.beginPath(); p.forEach((q, i) => (i ? g.lineTo(q[0], q[1]) : g.moveTo(q[0], q[1]))); g.closePath(); g.fill(); };
    const lab = (t, x, y, s, fill, ew) => { g.font = `900 ${s}px ${SERIF}`; g.textAlign = 'center'; g.textBaseline = 'middle'; g.lineJoin = 'round'; g.lineWidth = ew; g.strokeStyle = edge; g.strokeText(t, x, y); g.fillStyle = fill; g.fillText(t, x, y); };
    g.save(); g.translate(cx, cy);
    g.save(); g.beginPath(); g.arc(0, 0, R + 2, 0, TAU); g.clip();
    for (let i = 0; i < 2; i++) {
      const a0 = -Math.PI + i * Math.PI, cols = Gm.face[i];
      for (let j = 0; j < N; j++) { const s0 = a0 + j * Math.PI / N, s1 = s0 + Math.PI / N; g.fillStyle = cols[j % 2]; g.beginPath(); g.moveTo(0, 0); g.arc(0, 0, R + 4, s0 - 0.002, s1 + 0.002); g.closePath(); g.fill(); }
      for (let j = 1; j < N; j++) { const s = a0 + j * Math.PI / N; line(0, 0, Math.cos(s) * (R + 4), Math.sin(s) * (R + 4), j % 2 ? 'rgba(255,255,255,0.18)' : 'rgba(0,0,0,0.07)', 1.4); }
    }
    line(-R - 4, 0, R + 4, 0, ST.line, 5); line(-R - 4, 2.5, R + 4, 2.5, 'rgba(0,0,0,0.12)', 2);
    const sh = g.createRadialGradient(0, 0, R * 0.25, 0, 0, R + 2);
    sh.addColorStop(0, 'rgba(255,250,235,0.07)'); sh.addColorStop(0.72, 'rgba(0,0,0,0)'); sh.addColorStop(1, 'rgba(40,15,0,0.26)');
    g.fillStyle = sh; g.fillRect(-R - 4, -R - 4, 2 * R + 8, 2 * R + 8);
    g.restore();
    for (let i = 0; i < 2; i++) {
      const phi = -Math.PI / 2 + i * Math.PI, d = R * 0.57, x = Math.cos(phi) * d, y = Math.sin(phi) * d, txt = (i ? RT.b : RT.a) + 'P';
      let fs = R * 0.37; g.font = `900 ${fs}px ${SERIF}`; const tw = g.measureText(txt).width, mw = R * 1.36; if (tw > mw) fs *= mw / tw;
      g.save(); g.shadowColor = 'rgba(0,0,0,0.35)'; g.shadowOffsetY = 5 * k; g.shadowBlur = 6 * k; lab(txt, x, y, fs, '#fff4dc', fs * 0.22); g.restore();
      lab(txt, x, y, fs, '#fff6e4', fs * 0.15);
    }
    const Ro = R * 0.27, Ri = R * 0.1;
    for (let i = 0; i < 8; i++) {
      const a = -Math.PI / 2 + i * Math.PI / 4, al = a - Math.PI / 8, ar = a + Math.PI / 8;
      const T = [Math.cos(a) * Ro, Math.sin(a) * Ro], L = [Math.cos(al) * Ri, Math.sin(al) * Ri], Q = [Math.cos(ar) * Ri, Math.sin(ar) * Ri];
      poly([[0, 0], L, T], ST.star[0]); poly([[0, 0], T, Q], ST.star[1]);
    }
    for (let i = 0; i < 8; i++) {
      const a = -Math.PI / 2 + Math.PI / 8 + i * Math.PI / 4, al = a - Math.PI / 8, ar = a + Math.PI / 8, r2 = Ro * 0.55;
      poly([[0, 0], [Math.cos(al) * Ri, Math.sin(al) * Ri], [Math.cos(a) * r2, Math.sin(a) * r2]], ST.star[1]); poly([[0, 0], [Math.cos(a) * r2, Math.sin(a) * r2], [Math.cos(ar) * Ri, Math.sin(ar) * Ri]], ST.star[0]);
    }
    g.restore();
  }
  let rtIm = null;
  async function drawRt(cv) {
    if (!rtIm) rtIm = Promise.all(['plate', 'stick', 'knob', 'ptr'].map(p => img(`rt_kamisama_${p}2.webp`))).then(a => Promise.all([geo()]).then(([Gm]) => ({ plate: a[0], stick: a[1], knob: a[2], ptr: a[3], Gm })));
    const I = await rtIm, tile = cv.closest('.pnt');
    if (!I.plate) { if (tile) tile.classList.add('pnnone'); return false; }
    const r = cv.getBoundingClientRect(); if (!r.width || !r.height) return false;
    const dpr = Math.min(3, window.devicePixelRatio || 1), W = Math.round(r.width * dpr), H = Math.round(r.height * dpr);
    if (cv.width !== W) cv.width = W; if (cv.height !== H) cv.height = H;
    const g = cv.getContext('2d'), [sx, sy, sw, shh] = RT.crop, k = Math.min(W / sw, H / shh), Gm = I.Gm, P = Gm.parts || GEO0.parts;
    g.clearRect(0, 0, W, H);
    g.save(); g.translate((W - sw * k) / 2, (H - shh * k) / 2); g.scale(k, k); g.translate(-sx, -sy);
    g.drawImage(I.plate, 0, 0, 1024, 1536);
    face(g, Gm, k);
    for (const n of ['stick', 'knob', 'ptr']) if (I[n] && P[n]) g.drawImage(I[n], P[n].x, P[n].y, P[n].w, P[n].h);
    g.restore();
    cv.dataset.ok = '1';
    return true;
  }

  let ov = null, prev = null, rsT = 0;
  const isOpen = () => !!ov;
  function cbLocked() { try { return !!(window.TengelCB && window.TengelCB.locked && window.TengelCB.locked()); } catch (e) { return false; } }
  function html() {
    const w = window.TengelWallet;
    const tk = (window.TengelPoints && window.TengelPoints.TICKET_POINTS) || 7000, toy = (w && w.toy && w.toy.cost) || 3000;
    const miss = ' onerror="this.closest(\'.pnt\').classList.add(\'pnnone\')"';
    return `<div class="pnbar"><span class="pntt">お知らせ</span><button type="button" class="pnx" data-pn="close" aria-label="閉じる">${X}</button></div>`
      + '<div class="pnbd"><div class="pnin">'
      + '<p class="pney">ポイントの お知らせ</p>'
      + '<h2 class="pngold">お世話をして ポイント大量ゲットを 目指そう！</h2>'
      + '<p class="pnlead">トレーニングセンターの お世話や、TENGERカードバトルの 連続勝利で ポイントを 増やそう！</p>'
      + '<div class="pnsec">トレーニングセンター</div><div class="pnbox">'
      + '<h3>お世話の たびに ポイントの 抽選！</h3>'
      + '<p>ごはん・おそうじ などの お世話を すると、毎回 ポイントの 抽選が あるよ。大きな 当たりは この 3つ！</p>'
      + '<div class="pnart">'
      + '<figure class="pnt pnrt"><span class="pnpic"><canvas aria-hidden="true"></canvas><span class="pnem" aria-hidden="true">🎡</span></span><figcaption><b>ルーレットチャンス</b><span>最大 20,000P</span></figcaption></figure>'
      + `<figure class="pnt pndoor"><span class="pnpic"><img class="pnd" src="tk_door_open.webp" alt=""${miss}><span class="pngl"></span><img class="pntk" src="tk_ticket.webp" alt=""${miss}><span class="pnem" aria-hidden="true">🚪</span></span><figcaption><b>チケット扉</b><span>壁紙チケット か ${yen(tk)}P</span></figcaption></figure>`
      + `<figure class="pnt pnwide pnzone"><span class="pnpic"><span class="pnzb"><img src="tc_zn_back.webp" alt="" style="${at(ZN.back, ZN.w, ZN.h)}"${miss}><img src="tc_zn_ball.webp" alt="" style="${at(ZN.ball, ZN.w, ZN.h)}"${miss}><img src="tc_zn_arrow.webp" alt="" style="${at(ZN.arrow, ZN.w, ZN.h)}"${miss}></span>`
      + '<span class="pnem" aria-hidden="true">⚡</span></span><figcaption><b>ポイント特化ゾーン</b><span>最大 25,000P</span></figcaption></figure>'
      + '</div>'
      + '<button type="button" class="pngo" data-pn="tc">🐴 トレーニングセンターを 開く</button></div>'
      + '<div class="pnsec">TENGERカードバトル</div><div class="pnbox">'
      + '<h3>TENGERカードバトルの 連続勝利でも ポイントは 貰えるぞ！</h3>'
      + '<div class="pncb" role="img" aria-label="カードバトルの 結果：あなたの 勝ち！ 3対1・コンピュータに 4連勝！ プラス 400P">'
      + '<img class="pnbg" src="cb_board.webp" alt="" onerror="this.remove()"><span class="pnsh"></span>'
      + '<span class="pnci"><img class="pnlg" src="cb_logo.webp" alt="" onerror="this.closest(\'.pncb\').classList.add(\'pnnolg\')">'
      + '<span class="pnrs"><span class="pnhd">あなたの 勝ち！</span><span class="pnsc">3 － 1</span><span class="pnst">4連勝中！</span>'
      + '<span class="pnptn"><i>🎁</i><span>コンピュータに 4連勝！</span><b>＋400P</b></span></span></span></div>'
      + '<div class="pntip"><span class="pnlab">🎁 連勝の ポイント</span>コンピュータに <b>4</b>連勝で <b>400P</b>・<b>6</b>連勝で <b>800P</b>・<b>7</b>連勝から 1勝ごとに <b>300P</b></div>'
      + (cbLocked() ? `<p class="pnmu" style="margin:10px 0 0">※TENGERカードバトルは おもちゃ（${yen(toy)}P で 解放すると 遊べるよ）</p>` : '')
      + '<button type="button" class="pngo" data-pn="cb">🃏 TENGERカードバトルを 開く</button></div>'
      + '<div class="pnsec">ポイントを 購入</div><div class="pnbox pnshop">'
      + '<h3>ポイントを 購入して すぐ 使う</h3>'
      + '<p class="pnmu" style="margin:0 0 4px">買う ときは App Store の 画面が 出るよ（値段は App Store の 表示）</p>'
      + `<h4>ポイントを 買う（パック・期限なし）</h4><div data-pn-shop="packs">${shop('packs')}</div>`
      + `<h4>サブスク（毎月 届く）</h4><div data-pn-shop="subs">${shop('subs')}</div>`
      + '<button type="button" class="pngh" data-pn="pts">ポイントの 詳細・履歴</button></div>'
      + '<div class="pnfoot"><div class="pnrow"><button type="button" class="pngh" data-pn="close">閉じる</button></div></div>'
      + '</div></div>';
  }
  // 買う 欄（points_ui.js の TengelWallet.shop）：値段（App Store）を 読んだ あと・ポイントが かわった あと（tengel:wallet）に 書き直す
  function shop(k) { const w = window.TengelWallet; try { return w && w.shop ? w.shop[k]() : ''; } catch (e) { return ''; } }
  function paintShop() {
    if (!ov) return;
    for (const k of ['packs', 'subs']) { const el = $(`[data-pn-shop="${k}"]`, ov); if (el) el.innerHTML = shop(k); }
  }
  function paintArt() {
    if (!ov) return;
    const cv = $('.pnrt canvas', ov); if (cv) drawRt(cv).catch(() => { const t = cv.closest('.pnt'); if (t) t.classList.add('pnnone'); });
  }
  function onResize() { clearTimeout(rsT); rsT = setTimeout(paintArt, 120); }
  function onKey(e) { if (e.key === 'Escape') close(); }
  function open() {
    if (ov) return;
    css();      // 第4.243版：使い方（#tgHelp）と いっしょの 形（:is(#ptNote,#tgHelp)）
    ov = D.createElement('div'); ov.id = 'ptNote'; ov.className = 'tgov'; ov.setAttribute('role', 'dialog'); ov.setAttribute('aria-modal', 'true'); ov.setAttribute('aria-label', 'ポイントの お知らせ');
    ov.innerHTML = html();
    ov.addEventListener('click', e => {
      const w0 = window.TengelWallet;
      if (e.target.closest('[data-pt]')) { if (w0 && w0.shop) w0.shop.click(e); return; }      // 買う・始める（ポイントの 窓と 同じ 動き：お知らせは 閉じない）
      const b = e.target.closest('[data-pn]'); if (!b) return;
      const k = b.dataset.pn, w = window.TengelWallet;
      close(k === 'close');
      if (k === 'tc') { if (typeof window.TCOpen === 'function') window.TCOpen(); else { const f = $('#tcFab'); if (f) f.click(); } }
      else if (k === 'cb') { if (window.TengelCB && window.TengelCB.open) window.TengelCB.open(); else { const f = $('#cbFab'); if (f) f.click(); } }
      else if (k === 'pts' && w && w.openPoints) w.openPoints();
    });
    prev = D.activeElement;
    D.documentElement.classList.add('mson', 'ptnoteon'); D.body.appendChild(ov);
    window.addEventListener('resize', onResize); D.addEventListener('keydown', onKey); D.addEventListener('tengel:wallet', paintShop);
    const w = window.TengelWallet;
    if (w && w.shop) { Promise.resolve(w.shop.load()).then(paintShop, () => { }); Promise.resolve(w.shop.status()).then(paintShop, () => { }); }
    try { $('.pnx', ov).focus({ preventScroll: true }); } catch (e) { /* なし */ }
    requestAnimationFrame(paintArt);
  }
  function close(back) {
    if (!ov) return;
    ov.remove(); ov = null; clearTimeout(rsT); D.documentElement.classList.remove('ptnoteon');
    window.removeEventListener('resize', onResize); D.removeEventListener('keydown', onKey); D.removeEventListener('tengel:wallet', paintShop);
    if (!$('.tgov')) D.documentElement.classList.remove('mson');
    if (back !== false) { const p = $('#ptsPill') || prev; try { if (p && p.focus) p.focus({ preventScroll: true }); } catch (e) { /* なし */ } }
    prev = null;
  }
  window.TengelPtNote = { open, close, isOpen, LOW };

  // ===================== 使い方（第4.243版）=====================
  // 絵の 大きさ（help/img/hp_*.webp：横・たて。help/help_art.py で 作り直したら 合わせる：test_v243.py が 見くらべる）
  const HPI = { hp_buy: [716, 1154], hp_card: [720, 1292], hp_ocr: [716, 1254], hp_odds: [720, 1108], hp_oshi: [700, 1026], hp_pay: [664, 558], hp_pform: [700, 888], hp_plan: [720, 1384], hp_rec: [720, 153], hp_res: [664, 598], hp_rsv: [720, 153], hp_stat: [720, 605], hp_tri: [720, 1108] };
  // お世話チャレンジの 台の 置き方（tc_dp.json と 同じ 数：絵 1120×1830 の 中の 場所。test_v243.py が 見くらべる）
  const DPG = { img: [1120, 1830], lcd: [559.5, 1166, 91, 118], hold: { x: [369, 506.6, 644.2, 781.9, 919.5], y: 1322.5, w: 98 }, go: [205, 1414, 914, 1559], see: [195, 1575, 925, 1712] };
  // 色ごとの 当たり（tc/tc_app.js の PRIZES・PRIZES_VISIT・RT・ZONE・GEKI と 同じ 数：test_v243.py が 見くらべる）。光の 色＝tc_drop.js の TONE
  //   k＝当たりの 種類・v＝もらえる もの・x＝下の 行（幻の馬・神様馬が 来て いる 間）
  const DC = [
    { c: 0, n: '白', k: 'ハズレ', v: '', x: '当たりは なし（馬バレが 白く 光って、うすく「ハズレ」）', rgb: '255,255,255' },
    { c: 1, n: '青', k: 'ポイント', v: '10P〜300P', rgb: '60,150,255' },
    { c: 2, n: '緑', k: 'ルーレット', v: '800P か 1,600P', rgb: '50,220,100' },
    { c: 3, n: '紫', k: 'ルーレット', v: '1,600P か 3,200P', rgb: '180,95,255' },
    { c: 4, n: '赤', k: 'ルーレット', v: '3,200P か 6,400P', rgb: '255,62,52' },
    { c: 5, n: '金', k: 'ポイント特化ゾーン', v: '1,000P〜最大 25,000P', x: '幻の馬が 来て いる 間は 幻の馬ルーレット（800P〜6,400P）', rgb: '255,196,48' },
    { c: 6, n: '虹', k: 'チケット扉', v: '壁紙チケット か 7,000P', x: '神様馬が 来て いる 間は 神様馬ルーレット（2,000P〜20,000P）', rgb: 'rb' },
    { c: 7, n: '激馬熱馬', k: '', v: '40,000P', x: 'いちばん 大きい 当たり！', rgb: 'rb' }];
  const RBG = 'conic-gradient(from 200deg,#ff4646,#ffa032,#ffe846,#50eb6e,#46aaff,#966eff,#f06ee6,#ff4646)';
  const HCSS = '#tgHelp{z-index:96}'
    + '#tgHelp .hpol{margin:4px 0 10px;padding:0;list-style:none;counter-reset:hp}'
    + '#tgHelp .hpol>li{position:relative;margin:0 0 8px;padding-left:34px;font-size:14.5px;line-height:1.65;word-break:keep-all;overflow-wrap:anywhere}'
    + '#tgHelp .hpol>li::before{counter-increment:hp;content:counter(hp);position:absolute;left:0;top:.12em;width:24px;height:24px;border-radius:50%;display:grid;place-items:center;font:800 13px/1 ' + SANS + ';color:#1d1405;background:linear-gradient(180deg,#f8e3a0,#d9b45a)}'
    + '#tgHelp .hpol>li b,#tgHelp .hpct b i{color:#f4dc96;font-style:normal}'
    + '#tgHelp .hpf{position:relative;margin:12px 0 0;display:flex;flex-direction:column;border-radius:12px;border:1px solid rgba(217,180,90,.42);overflow:hidden;background:#0b222a;box-shadow:0 10px 24px rgba(0,0,0,.35)}'
    + '#tgHelp .hpf>img{display:block;width:100%;height:auto;background:#f4f5f8;-webkit-user-drag:none;user-select:none}'
    + '#tgHelp .hpf figcaption,#tgHelp .hpcap{padding:7px 8px 8px;border-top:1px solid rgba(217,180,90,.3);background:linear-gradient(180deg,#12333d,#0c252d);text-align:center;line-height:1.35;word-break:keep-all;overflow-wrap:anywhere}'
    + '#tgHelp .hpf figcaption b,#tgHelp .hpcap b{display:block;font-size:13px;color:#fff;letter-spacing:.02em}'
    + '#tgHelp .hpf figcaption span,#tgHelp .hpcap span{display:block;margin-top:2px;font-size:12px;font-weight:700;color:#f4dc96}'
    + '#tgHelp .hpf.hpnone>img{display:none}'
    + '#tgHelp .hpg2{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:8px;margin-top:12px;align-items:start}#tgHelp .hpg2>.hpf{margin:0}'
    + '#tgHelp .hpbox2{margin-top:14px}'
    // 台（お世話チャレンジ）の 絵：台の 絵の 一部を 切り取って 見せる（.hpbi＝台の 絵 ぜんぶ の 大きさ・中の 物は 台の 絵の 中の 場所）
    + '#tgHelp .hpbd{position:relative;margin:12px auto 0;width:100%;max-width:440px;border-radius:12px 12px 0 0;overflow:hidden;background:radial-gradient(80% 70% at 50% 40%,#1b4a57,#0b222a)}'
    + '#tgHelp .hpbw{margin:12px auto 0;max-width:440px;border-radius:12px;border:1px solid rgba(217,180,90,.42);overflow:hidden;box-shadow:0 10px 24px rgba(0,0,0,.35)}#tgHelp .hpbw .hpbd{margin:0;border-radius:0}'
    + '#tgHelp .hpbi{position:absolute}'
    + '#tgHelp .hpbi img,#tgHelp .hpbi span{position:absolute;display:block;-webkit-user-drag:none;user-select:none;pointer-events:none}'
    + '#tgHelp .hpbi .hpbase{left:0;top:0;width:100%;height:100%}'
    + '#tgHelp .hpbi .hplcd{border-radius:50%;overflow:hidden;background:#2a1830}#tgHelp .hpbi .hplcd img{position:absolute;left:-1%;top:-1%;width:102%;height:102%}'
    + '#tgHelp .hpbi .hpau{border-radius:50%;mix-blend-mode:screen}#tgHelp .hpbi .hpdim{left:0;top:0;width:100%;height:100%;background:rgba(12,6,22,.5)}'
    + '#tgHelp .hpbi .hpmk{transform:translate(-50%,-50%);width:8.5%;aspect-ratio:1;border-radius:50%;display:grid;place-items:center;font:900 clamp(13px,3.9vw,19px)/1 ' + SANS + ';color:#1d1405;'
    + 'background:linear-gradient(180deg,#fbe9b0,#d9b45a);border:2px solid #fff;box-shadow:0 3px 8px rgba(0,0,0,.5)}'
    + '#tgHelp .hpbd.hpnone{background:#10303a}#tgHelp .hpbd.hpnone .hpbi{display:none}#tgHelp .hpbd .hpno{display:none}'
    + '#tgHelp .hpbd.hpnone .hpno{display:grid;position:absolute;inset:0;place-items:center;font-size:44px}'
    // 色と 当たりの 一覧
    + '#tgHelp .hpcl{display:grid;gap:8px;margin:10px 0 0}'
    + '#tgHelp .hpc{display:grid;grid-template-columns:auto auto minmax(0,1fr);align-items:center;gap:10px;padding:8px 10px;border-radius:12px;background:rgba(6,18,23,.45);border:1px solid rgba(217,180,90,.22)}'
    + '#tgHelp .hpc.hpgk{border-color:rgba(255,120,90,.55);background:linear-gradient(100deg,rgba(120,20,20,.35),rgba(120,80,10,.3))}'
    + '#tgHelp .hpu{position:relative;width:58px;height:58px;border-radius:50%;overflow:hidden;background:radial-gradient(circle at 36% 30%,rgba(255,255,255,.8),rgb(var(--c)) 56%,rgba(0,0,0,.45));box-shadow:0 0 16px rgba(var(--c),.55)}'
    + '#tgHelp .hpu.hprb{background:' + RBG + ';box-shadow:0 0 18px rgba(255,220,140,.6)}'
    + '#tgHelp .hpu.hpw{background:radial-gradient(circle,#fff 0,#f2f6ff 58%,#c7d3ee 100%);box-shadow:0 0 14px rgba(255,255,255,.55)}'
    + '#tgHelp .hpu.hpw i{position:absolute;inset:0;display:grid;place-items:center;font:800 13px/1 ' + SANS + ';color:rgba(96,112,160,.32);font-style:normal}'
    + '#tgHelp .hpu img,#tgHelp .hph img{position:absolute;left:0;top:0;width:100%;height:100%;display:block}'
    + '#tgHelp .hph{position:relative;width:36px;height:36px;clip-path:polygon(29% 0,71% 0,100% 29%,100% 71%,71% 100%,29% 100%,0 71%,0 29%);background:radial-gradient(circle at 40% 32%,rgba(255,255,255,.7),rgb(var(--c)) 60%,rgba(0,0,0,.4))}'
    + '#tgHelp .hph.hprb{background:' + RBG + '}#tgHelp .hph.hpe{background:none;clip-path:none}'
    + '#tgHelp .hpct{min-width:0;line-height:1.45}#tgHelp .hpct b{display:block;font-size:15px;color:#fff;font-weight:800}#tgHelp .hpct b small{font-size:12px;color:#a6bec3;font-weight:700;margin-left:6px}'
    + '#tgHelp .hpct span{display:block;font-size:13.5px;font-weight:700;color:#f4dc96;font-variant-numeric:tabular-nums}'
    + '#tgHelp .hpct em{display:block;margin-top:2px;font-style:normal;font-size:12.5px;color:#a6bec3}'
    // 激馬熱馬の 瞬間（プチュン → 真っ暗 → 激馬熱馬）
    + '#tgHelp .hpst{display:grid;grid-template-columns:1fr auto 1fr auto 1fr;align-items:start;gap:4px;margin:12px 0 0;text-align:center}'
    + '#tgHelp .hpst .hpar{align-self:center;margin-top:-22px;color:#d9b45a;font-size:18px;font-weight:900}'
    + '#tgHelp .hpsf{position:relative;display:block;width:100%;max-width:92px;aspect-ratio:1;margin:0 auto;border-radius:50%;overflow:hidden;border:3px solid #f2d23a;box-shadow:0 0 0 2px #8a6a10,0 6px 14px rgba(0,0,0,.45)}'
    + '#tgHelp .hpsf.hpf1{background:radial-gradient(circle,#fff 0 7%,rgba(255,240,180,.95) 12%,rgba(255,214,80,0) 46%),repeating-conic-gradient(from 4deg,#ffd23a 0 7deg,#e2283a 7deg 20deg)}'
    + '#tgHelp .hpsf.hpf2{background:radial-gradient(circle at 50% 40%,#1a1014,#030203 70%)}'
    + '#tgHelp .hpsf.hpf3{background:' + RBG + '}#tgHelp .hpsf img{position:absolute;inset:0;width:100%;height:100%}'
    + '#tgHelp .hpst b{display:block;margin-top:6px;font-size:12.5px;line-height:1.35;color:#fff;word-break:keep-all;overflow-wrap:anywhere}'
    + '#tgHelp .hpend{display:block;margin:12px auto 0;width:62%;max-width:300px;border-radius:12px;border:1px solid rgba(217,180,90,.42);overflow:hidden;box-shadow:0 10px 24px rgba(0,0,0,.35)}'
    + '#tgHelp .hpend img{display:block;width:100%;height:auto;aspect-ratio:1170/1842;background:linear-gradient(180deg,#fff3cc,#e9c46a)}'
    + '#tgHelp .hpend.hpnone img{display:none}#tgHelp .hpend.hpnone .hpcap{border-top:0}'
    + '#tgHelp .hpcap .hpbig{display:block;margin:2px 0 0;font-weight:900;font-size:clamp(22px,6.6vw,30px);line-height:1.25;letter-spacing:.02em;text-align:center;color:transparent}'
    + '@media (min-width:600px){#tgHelp .hpu{width:66px;height:66px}#tgHelp .hph{width:40px;height:40px}}';
  // 「！」の 丸（判定の 画面：テーマの 色に よらない 金の 丸・白い ふち）
  const QCSS = '.hpq{flex:none;display:inline-grid;place-items:center;width:34px;height:34px;padding:0;margin:0;border-radius:50%;border:2px solid #fff;background:linear-gradient(180deg,#ffd76a,#e2a23b);color:#3a2405;'
    + 'font:900 19px/1 ' + SANS + ';cursor:pointer;box-shadow:0 2px 7px rgba(0,0,0,.28);-webkit-tap-highlight-color:transparent;-webkit-appearance:none;appearance:none}'
    + '.hpq:active{transform:translateY(1px)}.hpq:focus-visible{outline:2px solid var(--focus,#E2A23B);outline-offset:2px}';
  const imgOk = ' onerror="var f=this.closest(\'.hpf,.hpbd,.hpend\');if(f)f.classList.add(\'hpnone\')"';
  const drop = ' onerror="this.remove()"';
  const ar = n => (HPI[n] ? `aspect-ratio:${HPI[n][0]}/${HPI[n][1]}` : '');
  // 判定・作戦会議の 絵（help/img の 絵：manual/ に 入って いる）。f＝ファイルの 名前（そのまま 書く：app_unused.py が 使って いる ファイルを 名前で さがす）
  const pic = (f, cap, sub) => { const n = f.replace(/\.webp$/, ''); return `<figure class="hpf" data-hp="${n}"><img src="manual/${f}" alt="" decoding="async" style="${ar(n)}"${imgOk}><figcaption><b>${cap}</b>${sub ? `<span>${sub}</span>` : ''}</figcaption></figure>`; };
  const ol = a => '<ol class="hpol">' + a.map(x => `<li>${x}</li>`).join('') + '</ol>';
  const tip = (lab, t) => `<div class="pntip"><span class="pnlab">${lab}</span>${t}</div>`;
  const sec = (t, inner) => `<div class="pnsec">${t}</div><div class="pnbox">${inner}</div>`;
  const yenS = n => yen(n) + 'P';
  // 台の 絵（cut＝見せる 所 [x, y, 横, たて]・台の 絵の 中の 場所）
  const bp = (r, W, H) => at(r, W || DPG.img[0], H || DPG.img[1]);
  function board(cut, inner, cap, sub, label) {
    const [x0, y0, cw, ch] = cut, [IW, IH] = DPG.img;
    return `<div class="hpbw"><div class="hpbd" role="img" aria-label="${label}" style="aspect-ratio:${cw}/${ch}"><span class="hpno" aria-hidden="true">🎯</span>`
      + `<div class="hpbi" style="left:${pc(-x0, cw)};top:${pc(-y0, ch)};width:${pc(IW, cw)};height:${pc(IH, ch)}"><img class="hpbase" src="tc_dp_base.webp" alt=""${imgOk}>${inner}</div></div>`
      + `<div class="hpcap"><b>${cap}</b>${sub ? `<span>${sub}</span>` : ''}</div></div>`;
  }
  const lcd = c => { const [cx, cy, r, R] = DPG.lcd, A = R * 2.15, col = c === 7 ? '255,150,70' : c === 6 ? '255,214,120' : DC[c].rgb;
    return '<span class="hpdim"></span>' + `<span class="hpau" style="${bp([cx - A, cy - A, 2 * A, 2 * A])};background:radial-gradient(closest-side,rgba(${col},.85),rgba(${col},.35) 55%,rgba(${col},0))"></span>`
      + `<span class="hplcd" style="${bp([cx - r, cy - r, 2 * r, 2 * r])}"><img src="tc_dp_uma${c}.webp" alt=""${drop}></span>`; };
  const hold = (slot, c) => { const H = DPG.hold, w = H.w; return `<img src="tc_dp_hold${c}.webp" alt="" style="${bp([H.x[slot] - w / 2, H.y - w / 2, w, w])}"${drop}>`; };
  const mk = (n, x, y) => `<span class="hpmk" style="left:${pc(x, DPG.img[0])};top:${pc(y, DPG.img[1])}">${n}</span>`;
  function hJudge() {
    const w = window.TengelWallet, cost = (w && w.COST && w.COST.read) || 800;
    return '<p class="pney">判定の 使い方</p>'
      + '<h2 class="pngold">画像を 読み込んで 判定 → 予約 → 記録！</h2>'
      + '<p class="pnlead">オッズの スクショを 読み込むと、判定に 使う 数字が 入るよ。そのまま 買い目を 予約して、レースの あとに 結果を 入れると 記録タブに 残るよ。</p>'
      + sec('① 読み込む 画像', '<h3>同じ レースの スクショを 1〜3枚</h3>'
        + '<p>「オッズ画像から読み取る」を 押して、この 2つの 画面を いっしょに 選んでね。</p>'
        + '<div class="hpg2">' + pic('hp_odds.webp', '単勝オッズの 画面', '馬番と 単勝が 写って いれば OK') + pic('hp_tri.webp', '3連単の 人気順', '1位〜10位まで 写そう') + '</div>'
        + tip('📷 コツ', 'レースの 見出し（<b>R・距離・馬場・頭数</b>）も 写すと そのまま 入るよ。オッズの 表は 大きく 写してね。')
        + '<div class="hpbox2"><h3>読み込むと 入力に 入るよ</h3>' + pic('hp_ocr.webp', '読めた 項目が 入力に 入る', '読めなかった 項目は 知らせが 出るので 手で 入れてね') + '</div>'
        + `<p class="pnmu" style="margin:10px 0 0">※ 読み込みは 1レース ${yenS(cost)}（同じ レースの 読み直しは 0P）。締切済みの レースは 判定は 出るけど、買い目の 予約と 結果の 記録は できないよ。</p>`)
      + sec('② 買い目予約', '<h3>判定の 下の「買い目」で 予約</h3>'
        + ol(['判定が 出たら、下の「買い目」の 欄で 券種（<b>馬単・3連単</b> など）の ボタンを 押して 行を 足す', '金額を 確かめて「<b>買い目を予約</b>」を 押す', '予約した レースは 記録タブに「<b>結果待ち</b>」で 入るよ'])
        + pic('hp_buy.webp', '券種の 行を 足して「買い目を予約」', '推奨の ゾーンの 馬が 入るよ') + pic('hp_rsv.webp', '記録タブに「結果待ち」で 入る', 'レースが 終わったら ここから 結果を 入れる'))
      + sec('③ 結果入力', '<h3>レースが 終わったら 1〜3着を 入れる</h3>'
        + ol(['記録タブで 予約した レースを 押すと 結果の 欄が 開くよ', '<b>1着・2着・3着の 馬番</b>を 入れる（「📷 結果の画像から読む」でも 入るよ）', '「<b>結果を決める</b>」を 押すと 的中を 判定するよ'])
        + pic('hp_res.webp', '1〜3着の 馬番を 入れて「結果を決める」', '取消・中止も ここで 入れられるよ'))
      + sec('④ 結果記録', '<h3>金額を 入れて 記録に 残す</h3>'
        + ol(['的中の 演出の あとに 金額の 欄が 出るよ', '券種ごとに <b>購入額 → 払戻</b> を 入れて「<b>記録する</b>」（外れは 0・あとから でも 入れられるよ）', '記録タブに 的中・回収が 残って、「<b>実測・回収</b>」タブで 回収率が 見られるよ'])
        + pic('hp_pay.webp', '購入額 → 払戻 を 入れて「記録する」', '') + pic('hp_rec.webp', '記録タブに 結果が 残る', '的中・回収が ひと目で わかるよ')
        + pic('hp_stat.webp', '「実測・回収」タブ', '的中率・回収率・収支が わかるよ'));
  }
  function hPlan() {
    return '<p class="pney">作戦会議の 使い方</p>'
      + '<h2 class="pngold">出馬表の 画像で やりたい レースを 予約！</h2>'
      + '<p class="pnlead">作戦会議では、やりたい レースを 予約して、発走の 前に 通知で 知らせて もらえるよ。画像を 読み込むと、レースの 中身が 入るよ（ポイントは 使わないよ）。</p>'
      + sec('読み込む 画像', '<h3>出馬表や オッズの 画面の スクショを 1〜3枚</h3>'
        + '<p>「レースを予約」の「📷 画像から読み取る」を 押して 選んでね。<b>開催場・R・レース名・出走頭数・距離・発走時間</b>を 読み取るよ。</p>'
        + '<div class="hpg2">' + pic('hp_card.webp', '出馬表の 画面', '日付・R・レース名・距離・発走が 写って いれば OK') + pic('hp_odds.webp', 'オッズの 画面でも OK', '見出しの 頭数・距離・発走も 読むよ') + '</div>'
        + tip('📷 コツ', '選んで いる <b>開催場と R</b> が 写る ように 撮ってね。')
        + '<div class="hpbox2"><h3>読み込むと 予約の 欄に 入るよ</h3>' + pic('hp_pform.webp', '読めた 項目が 予約の 欄に 入る', '読めなかった 項目は 知らせが 出るので 手で 入れてね') + '</div>')
      + sec('作戦会議で できること', '<h3>やりたい レースを 予約して 通知</h3>'
        + '<p>予約した レースごとに、発走の <b>20・15・10・8・5分前</b> の 通知を 選べるよ（「通知」を オン ＋ iPhone の 通知の 許可）。お知らせの 時刻が 来ると「🔔 まもなく発走」。</p>'
        + pic('hp_plan.webp', 'やりたい レースの ボード', 'その 日が すぎると 消えるよ')
        + '<div class="hpbox2"><h3>レースごとに メモ</h3><p>レースの 札に メモを 書けるよ（書いた そばから 保存・300字まで）。</p></div>'
        + '<div class="hpbox2"><h3>推し馬を 25頭まで 登録</h3><p>名前・<b>親・おじいちゃん・ひいおじいちゃん</b>（血統）と 備考を 残せるよ。日が かわっても 消えないよ。</p>'
        + pic('hp_oshi.webp', '推し馬の ボード', '「血統を見る」で 血統の 表') + '</div>'
        + tip('📋 すぐ 予約', '上の「<b>やりたいレースを予約！</b>」からも すぐ 予約の 欄が 開くよ。'));
  }
  function hDrop() {
    const w = window.TengelWallet, toy = (w && w.toy && w.toy.cost) || 3000, tk = (window.TengelPoints && window.TengelPoints.TICKET_POINTS) || 7000;
    const H = DPG.hold, L = DPG.lcd;
    const rows = DC.map(d => {
      const rb = d.rgb === 'rb', st = rb ? '' : ` style="--c:${d.rgb}"`, v = d.c === 6 ? `壁紙チケット か ${yen(tk)}P` : d.v;
      const u = d.c === 0 ? '<span class="hpu hpw" aria-hidden="true"><i>ハズレ</i></span>' : `<span class="hpu${rb ? ' hprb' : ''}"${st} aria-hidden="true"><img src="tc_dp_uma${d.c}.webp" alt=""${drop}></span>`;
      const hh = d.c === 0 ? '<span class="hph hpe" aria-hidden="true"></span>' : `<span class="hph${rb ? ' hprb' : ''}"${st} aria-hidden="true"><img src="tc_dp_hold${d.c}.webp" alt=""${drop}></span>`;
      return `<div class="hpc${d.c === 7 ? ' hpgk' : ''}" data-c="${d.c}">${u}${hh}<span class="hpct"><b>${d.n}</b><span>${[d.k, v].filter(Boolean).join('：')}</span>${d.x ? `<em>${d.x}</em>` : ''}</span></div>`;
    }).join('');
    const howTo = board([0, 560, 1120, 1270], mk('①', 262, 1486) + mk('②', 559.5, L[1] - L[3] - 30) + mk('③', 96, H.y) + mk('④', 262, 1643), 'お世話チャレンジの 台', '番号は 下の ①〜④', 'お世話チャレンジの 台：①玉を落とす ②馬バレ ③当選 ④保留結果を見る');
    const moment = board([150, 975, 820, 420], lcd(7) + hold(0, 7),'馬バレに 激馬熱馬！ 保留は 八角の 激馬熱馬', '', '激馬熱馬が 当たった 瞬間の 台');
    return '<p class="pney">お世話チャレンジ（玉落とし）の 遊び方</p>'
      + '<h2 class="pngold">玉の 光る 色で 当たりが わかる！</h2>'
      + '<p class="pnlead">お世話の あとの PUSH の 画面の 左下「お世話チャレンジ」から 遊べるよ。玉を 落として コップに 入った 瞬間、まん中の 馬バレが 当たりの 色に 光るよ。</p>'
      + sec('遊び方', '<h3>お世話トークン 1こで 玉 1こ</h3>' + howTo
        + ol(['「<b>玉を落とす</b>」を 押すと 玉が 1こ 落ちるよ（お世話トークン 1こ＝お世話 1回の 抽選）',
          '玉が コップに 入った 瞬間、当たって いれば まん中の <b>馬バレ</b> が 色つきで 光るよ（ハズレは 白く 光る）',
          '当たりは「<b>当選</b>」の ますに たまる（5つ まで・トークンが ある 間は 続けて 落とせる）',
          '「<b>保留結果を見る</b>」で、たまった 当たりを 順番に 受け取ろう！（「投入終了」で 途中でも 見られるよ）'])
        + `<p class="pnmu" style="margin:0">※ はじめは おもちゃの 解放（${yen(toy)}P）が いるよ。</p>`)
      + sec('色と 当たり', '<h3>馬バレの 色で 当たりが わかる</h3><p>光が 激しい ほど 大きい 当たり！ 当たりの 色の 保留（八角）が「当選」の ますに たまるよ。</p>'
        + `<div class="hpcl">${rows}</div>`)
      + sec('激馬熱馬の 瞬間', '<h3>玉が 入った 瞬間に プチュン！</h3>'
        + '<div class="hpst" role="img" aria-label="赤と 金の プチュン → 真っ暗 → 激馬熱馬">'
        + '<div><span class="hpsf hpf1"></span><b>赤と 金の プチュン！</b></div><span class="hpar" aria-hidden="true">▶</span>'
        + '<div><span class="hpsf hpf2"></span><b>真っ暗…</b></div><span class="hpar" aria-hidden="true">▶</span>'
        + `<div><span class="hpsf hpf3"><img src="tc_dp_uma7.webp" alt=""${drop}></span><b>激馬熱馬！</b></div></div>`
        + ol(['玉が コップに 入った 瞬間、馬バレが <b>赤と 金</b> で プチュン！ → 真っ暗に…', '虹と 同じ 音と いっしょに「<b>激馬熱馬</b>」が 出るよ', '保留は 八角の 激馬熱馬。「<b>保留結果を見る</b>」で 天国の 動画が 始まるよ'])
        + moment
        + `<figure class="hpend"><img src="tc_gk_end2.webp" alt=""${imgOk}><figcaption class="hpcap"><span class="hpbig pngold">40,000P 獲得！</span><span>天国の 動画の あとに もらえるよ</span></figcaption></figure>`);
  }
  const HELP = { judge: ['判定の 使い方', hJudge], plan: ['作戦会議の 使い方', hPlan], drop: ['お世話チャレンジの 遊び方', hDrop] };
  let hov = null, hkind = '', hprev = null;
  function hKey(e) { if (e.key === 'Escape') { e.stopPropagation(); hClose(); } }
  function css() {
    if (!$('#ptNoteCss')) { const st = D.createElement('style'); st.id = 'ptNoteCss'; st.textContent = CSS.replace(/#ptNote/g, ':is(#ptNote,#tgHelp)') + HCSS; D.head.appendChild(st); }
  }
  function hOpen(kind, from) {
    const H = HELP[kind]; if (!H) return false;
    if (hov) hClose(false);
    css();
    hov = D.createElement('div'); hov.id = 'tgHelp'; hov.className = 'tgov'; hov.dataset.kind = kind; hov.setAttribute('role', 'dialog'); hov.setAttribute('aria-modal', 'true'); hov.setAttribute('aria-label', H[0]);
    hov.innerHTML = `<div class="pnbar"><span class="pntt">${H[0]}</span><button type="button" class="pnx" data-hp="close" aria-label="閉じる">${X}</button></div>`
      + `<div class="pnbd"><div class="pnin">${H[1]()}<div class="pnfoot"><div class="pnrow"><button type="button" class="pngh" data-hp="close">閉じる</button></div></div></div></div>`;
    hov.addEventListener('click', e => { if (e.target.closest('[data-hp=close]')) hClose(); });
    hkind = kind; hprev = from || D.activeElement;
    D.documentElement.classList.add('mson'); D.body.appendChild(hov); D.addEventListener('keydown', hKey, true);
    try { $('.pnx', hov).focus({ preventScroll: true }); } catch (e) { /* なし */ }
    return true;
  }
  function hClose(back) {
    if (!hov) return;
    hov.remove(); hov = null; hkind = ''; D.removeEventListener('keydown', hKey, true);
    if (!$('.tgov')) D.documentElement.classList.remove('mson');
    if (back !== false && hprev && hprev.isConnected) { try { hprev.focus({ preventScroll: true }); } catch (e) { /* なし */ } }
    hprev = null;
  }
  window.TengelHelp = { open: hOpen, close: hClose, isOpen: () => !!hov, kind: () => hkind, DC, DPG, HPI };
  // 判定の「オッズ画像から読み取る」の 横の「！」（#ocrRow は 画像の 読み取りが 使える とき だけ 出る）
  function judgeQ() {
    if (!$('#hpqCss')) { const st = D.createElement('style'); st.id = 'hpqCss'; st.textContent = QCSS; D.head.appendChild(st); }
    const b = $('#ocrBtn'); if (!b || $('#ocrHelp')) return;
    const q = D.createElement('button'); q.type = 'button'; q.id = 'ocrHelp'; q.className = 'hpq'; q.textContent = '!'; q.title = '使い方';
    q.setAttribute('aria-label', '画像の 読み込み・買い目予約・結果入力・結果記録の 使い方');
    q.addEventListener('click', () => hOpen('judge', q));
    b.insertAdjacentElement('afterend', q);
  }
  if (D.readyState === 'loading') D.addEventListener('DOMContentLoaded', judgeQ); else judgeQ();
})();
