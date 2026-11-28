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
    if (!$('#ptNoteCss')) { const st = D.createElement('style'); st.id = 'ptNoteCss'; st.textContent = CSS; D.head.appendChild(st); }
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
})();
