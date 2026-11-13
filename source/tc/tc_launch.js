// トレーニングセンターの 入口（App Store版だけ・index.html の 中に 入る 小さい 部分）
//   ・どの タブでも 右下（下の タブの すぐ 上）に 丸い ボタン（絵＋下に 名前の 札「トレーニング／センター」）→ 押すと tc_bundle.js を 読んで TCApp.open()
//     （11/09 13:04 まさちゃん「右下にうかぶ丸ボタン」→ 11/10 09:45「右上の赤丸の場所にして！」→ 11/10 11:32「アイコンが壁紙と重なってるから、右下に移動して！」
//       ・11/10 09:57「トレーニングセンターのアイコンこれにして！」「アイコンの下に、トレーニングセンター、思い出フィギュア、って壁紙に合う文字で」）
//     その 下に 思い出フィギュアの ボタン（fig/fig_launch.js が ここの TengelFab.add で 入れる：同じ 列 #fabCol・上から トレーニングセンター → 思い出フィギュア）
//     第4.165版（11/13 12:47「推し馬はすぐに確認できるように、トレーニングセンターと思い出フィギュアのアイコンのところの1番上に配置して！推し馬のアイコンをタップしたら、
//       推し馬の欄に飛ぶように設定して！」）：列の 1番 上に 推し馬の ボタン（#oshiFab・まさちゃんの 絵 tc_icon_oshi.webp）→ 押すと 作戦会議を 開いて「推し馬」の 欄へ（planOpen({ oshi: true })）
//   ・作戦会議の 通知（tengel.plan）：src.html の syncNotify が TCPlanNotify() を いっしょに 入れる（アプリの 中から 出す お知らせ）
//   ・作戦会議の 入口（第4.160版）：判定タブの「レース情報」の カードの 右上に 作戦会議の 札 → 押すと 判定タブの 上に 作戦会議を 開く（トレーニングセンターは 開かない）
//     第4.165版（11/13 13:55「赤枠の作戦会議のアイコンを青四角のあたりに設置して！黄丸のところに、タップすると壁紙や結果ボードカスタムのところに飛べるアイコン設置して！アイコン二枚目！」）：
//       札は カードの 右上の かどへ（上と 右へ 少し はみ出す）。
//       → 14:16「何か変だから、2枚目のアイコンにして、作戦会議のすぐ下に設置してみて！あと下にテロップ入れて！壁紙&ボード着せ替え、って！」：
//         作戦会議の 札の すぐ 下に 横長の カプセルの ボタン（#kiseBtn・まさちゃんの 絵 tc_icon_kise2.webp）・その 下に 名前の 札「壁紙&ボード着せ替え」
//       → 押すと 設定タブの「着せ替え」（壁紙）へ。その カードの 右上に「結果ボードカスタムへ↓」の 札（#kiseJump）→ すぐ 下の「結果ボードカスタム」へ
//   ・お世話の 合計（ミッション）・チケット（着せ替え）：バンドルを 読む 前でも TCInfo で 読める
//   ・推し馬の 置き場（第4.165版：TCOshi）：作戦会議の「推し馬」（tc_plan.js）が 読み書き する・バックアップ（pwa_ui.js）にも 入れる ので バンドルを 読む 前から ある
(function () {
  'use strict';
  if (!window.__NATIVE) return;
  var TK = 'tengel.tc', PK = 'tengel.plan';
  function jget(k) { try { return JSON.parse(localStorage.getItem(k) || 'null'); } catch (e) { return null; } }
  function jset(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* なし */ } }
  var live = function () { return window.TCApp && window.TCApp.state ? window.TCApp.state : null; };
  window.TCInfo = {
    total: function () { var s = live() || jget(TK); return (s && s.total) || 0; },
    tickets: function () { var s = live() || jget(TK); return (s && s.tickets) || 0; },
    useTicket: function () {
      if (window.TCApp && window.TCApp.tickets) return window.TCApp.tickets.use();
      var s = jget(TK); if (!s || !(s.tickets > 0)) return false; s.tickets -= 1; jset(TK, s); return true;
    },
    // 第4.140版：使った チケットを 1枚 もどす（着せ替えで 解放できなかった とき）
    backTicket: function () {
      if (window.TCApp && window.TCApp.tickets && window.TCApp.tickets.back) return window.TCApp.tickets.back();
      var s = jget(TK); if (!s) return false; s.tickets = (s.tickets || 0) + 1; jset(TK, s); return true;
    }
  };
  // ---------- 推し馬（第4.165版・まさちゃん 2026/11/13 11:46「作戦会議の中に、推し馬、の欄を作成して、推し馬を25頭まで登録できるようにして！
  //   できること ・名前 ・親(2頭)、おじいちゃん(4頭)、ひいおじいちゃん(8頭) ・備考欄」）----------
  //   保存：localStorage 'tengel.oshi'（{ v:1, list:[{ id, name, ped:[14こ], memo, at }] }）。この 端末の 中・日が かわっても 消えない（作戦会議の レースは その 日が すぎると 消える）。
  //     ped の ならび：父・母／父の父・父の母・母の父・母の母／父の父の父・父の父の母・父の母の父・父の母の母・母の父の父・母の父の母・母の母の父・母の母の母
  //   ・25頭まで（MAX）。名前と 血統の 名前は 1行・30字まで／備考は 300字まで（改行は のこす）。見えない 制御の 字は 消す・絵文字の 途中では 切らない
  //   ・書いたら バックアップ（アプリの 中の 自動バックアップ・書き出す バックアップ）にも 入る ように 合図（window.__tengelWrote）。戻す ときは merge（もう ある 馬は そのまま・ない 馬を 25頭まで 足す）
  var OK = 'tengel.oshi', OSHI = { MAX: 25, PED: 14, NAME: 30, MEMO: 300 };
  function oshiStr(v, max, multi) {
    var t = String(v == null ? '' : v).replace(/\r\n?/g, '\n').replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/g, '');
    if (!multi) t = t.replace(/\s+/g, ' ').replace(/^ +| +$/g, '');
    t = t.slice(0, max); if (/[\uD800-\uDBFF]$/.test(t)) t = t.slice(0, -1);
    return t;
  }
  function oshiNorm(x) {
    if (!x || typeof x !== 'object') return null;
    var name = oshiStr(x.name, OSHI.NAME), id = oshiStr(x.id, 40).replace(/[^0-9A-Za-z_-]/g, '');
    if (!name || !id) return null;
    var ped = [], src = Array.isArray(x.ped) ? x.ped : [];
    for (var i = 0; i < OSHI.PED; i++) ped.push(oshiStr(src[i], OSHI.NAME));
    return { id: id, name: name, ped: ped, memo: oshiStr(x.memo, OSHI.MEMO, true), at: oshiStr(x.at, 30) };
  }
  function oshiList(arr) {
    var out = [], seen = {};
    (Array.isArray(arr) ? arr : []).forEach(function (x) { var o = oshiNorm(x); if (o && !seen[o.id] && out.length < OSHI.MAX) { seen[o.id] = 1; out.push(o); } });
    return out;
  }
  function oshiLoad() { var d = jget(OK); return oshiList(d && d.list); }
  function oshiSave(list, quiet) {
    var out = oshiList(list); jset(OK, { v: 1, list: out });
    if (!quiet) { try { if (typeof window.__tengelWrote === 'function') window.__tengelWrote(); } catch (e) { /* なし */ } }      // 自動バックアップにも 書く（少し 待って から）
    return out;
  }
  function oshiMerge(arr) {             // バックアップから 戻す：もう ある 馬（同じ id）は そのまま・ない 馬を 足す（25頭まで）。返り値＝足した 頭数
    var cur = oshiLoad(), have = {}, add = 0;
    cur.forEach(function (o) { have[o.id] = 1; });
    oshiList(arr).forEach(function (o) { if (!have[o.id] && cur.length < OSHI.MAX) { cur.push(o); have[o.id] = 1; add++; } });
    if (add) oshiSave(cur, true);
    return add;
  }
  window.TCOshi = { MAX: OSHI.MAX, PED: OSHI.PED, NAME_MAX: OSHI.NAME, MEMO_MAX: OSHI.MEMO, load: oshiLoad, save: oshiSave, merge: oshiMerge, norm: oshiNorm, str: oshiStr };
  // ---------- 作戦会議の 通知（発走の 20・15・10・8・5分前：選んだ もの だけ）----------
  window.TCPlanNotify = function () {
    var P = jget(PK); if (!P || !P.on || !Array.isArray(P.races)) return [];
    var now = Date.now(), out = [];
    P.races.forEach(function (r) {
      if (!r || !/^\d{4}-\d{2}-\d{2}$/.test(r.date || '') || !/^\d{1,2}:\d{2}$/.test(r.time || '')) return;
      var d = r.date.split('-'), hm = r.time.split(':');
      var at0 = new Date(+d[0], +d[1] - 1, +d[2], +hm[0], +hm[1], 0).getTime();
      (r.notify || []).forEach(function (m) {
        var at = at0 - m * 60000; if (at <= now + 5000) return;
        out.push({ id: 'plan-' + r.id + '-' + m, at: at, title: 'まもなく発走！', body: (r.name || 'レース') + '　' + r.time + ' 発走（あと' + m + '分）', race: '' });
      });
    });
    return out;
  };
  // ---------- 右下の 丸い ボタンの 列（#fabCol）：上から 推し馬（#oshiFab：第4.165版）→ トレーニングセンター（#tcFab）→ 思い出フィギュア（#figFab：fig/fig_launch.js が TengelFab.add で 入れる）----------
  //   ・場所：下の タブの すぐ 上・右はし（画面に 固定）。11/10 09:45「右上の赤丸の場所にして！」で 上の 帯の すぐ 下に した（第4.138版）が、
  //     判定タブで 壁紙の 上の絵に 重なる → 11:32「アイコンが壁紙と重なってるから、右下に移動して！」で 右下へ（第4.139版）
  //   ・ボタン＝丸い 絵（66px）＋ その 下の 名前の 札（.fabl・2行）。押せる のは 絵と 札だけ（まわりの すきまは 下の 画面に とどく）
  //   ・名前の 字（11/10 09:57 まさちゃん「壁紙に合う文字で」「文字の太さや字体は自然に馴染むように」）：
  //     字体＝いまの 壁紙（着せ替え）の 本文の 字（--font-body：どの 壁紙でも かな と「思い出」が 入って いる。見出しの 字 --font-display は しぼって あって 漢字が ない）・
  //     太さ＝下の タブの 名前と 同じ 700・札の 色＝上の 帯と 同じ（地 --night・字 --night-ink・ふちの 線 --lamp）：壁紙を かえると 帯と いっしょに かわる。
  //     字だけ（札なし）だと 下の カードの 字と 重なって 読みにくい（ためした）ので、上の 帯の 丸い 札（結果待ち・ミッション）と 同じ 見た目の 小さい 札に のせる
  //   ・名前は 2行（「トレーニング／センター」「思い出／フィギュア」）：1行だと 札が 絵より 左へ 30px ほど 出る（列の はばを 絵と 同じに して 画面の 中身に かぶる 所を へらす）
  //   ・列の 下に かくれた ままに ならない ように：
  //     ページの いちばん 下の 中身＝main の 下の 余白を 列の 高さの ぶん 広げる（clear：さいごまで スクロール すると 中身が 列の 上まで 上がる）・
  //     判定タブの 下の 帯（#minibar：判定の 要点・押すと 結果へ）の ぶん、列は いつも 上に あけて おく（place：帯の 字を かくさない）。
  //       第4.168版（まさちゃん 2026/11/14 02:12「青四角の項目は、表示されるページは画面を上下にスライドしても、位置がずれずそこにいるようにして！」）：
  //       前は 帯が 出て いる あいだ だけ 上へ 上げて いた ＝ 画面を 上下に 動かして 帯が 出たり 消えたり する たびに 列が 上下に 動いて いた → どの タブでも いつも 同じ 所・
  //     買い目編集の「保存する」の 帯（.zsave.sticky：変更が ある あいだ 下に はりつく）は 右を ちぢめて 列の 手前で 終わる（--fabz）
  var MINI_B = 58, MINI_H = 40;            // 下の 帯（#minibar）：画面の 下からの 場所（src.html：bottom:calc(58px + var(--sab,0px))）・高さ（どの 壁紙でも 39.2px → 40。test_tc.py が 測る）
  function fabCol() {
    var c = document.getElementById('fabCol'); if (c) return c;
    var st = document.createElement('style'); st.id = 'fabColCss';
    st.textContent = '#fabCol{position:fixed;right:4px;bottom:calc(104px + var(--sab,0px));z-index:29;display:flex;flex-direction:column;align-items:center;gap:4px;pointer-events:none}'
      + '#fabCol>button{pointer-events:none;display:flex;flex-direction:column;align-items:center;border:0;padding:0;margin:0;background:none;color:inherit;-webkit-tap-highlight-color:transparent;transition:transform .15s}'
      + '#fabCol>button:active{transform:scale(.94)}#fabCol>button:disabled{opacity:.7}'
      + '#fabCol .fabi{pointer-events:auto;cursor:pointer;display:block;width:66px;height:66px;border-radius:50%;filter:drop-shadow(0 3px 5px rgba(0,0,0,.35))}'
      + '#fabCol .fabi img{width:100%;height:100%;display:block;pointer-events:none}'
      + '#fabCol .fabt{display:flex;align-items:center;justify-content:center;width:100%;height:100%;border-radius:50%;box-sizing:border-box;border:4px solid;font:400 12px/1.15 var(--font-display,sans-serif);text-align:center}'
      + '#fabCol .fabl{pointer-events:auto;cursor:pointer;position:relative;display:block;box-sizing:border-box;min-width:64px;margin-top:-7px;padding:2px 6px 2.5px;border-radius:9px;border:1px solid var(--lamp);background:var(--night);color:var(--night-ink);'
      + 'font-family:var(--font-body);font-weight:700;font-size:9.5px;line-height:11px;letter-spacing:-.01em;text-align:center;white-space:pre;box-shadow:0 1px 3px rgba(0,0,0,.25)}'
      + '.zsave.sticky{margin-right:var(--fabz,0px)}';
    document.head.appendChild(st);
    c = document.createElement('div'); c.id = 'fabCol'; document.body.appendChild(c);
    // 場所（第4.168版）：判定タブの 下の 帯（#minibar）が 出る 所の すぐ 上（6px）に いつも いる ＝ 帯が 出ても 消えても・どの タブでも 動かない。
    //   帯は 画面の 下から MINI_B（＋下の 安全な 余白 --sab）の 所に 高さ MINI_H で 出る（src.html の .minibar：下の タブの 高さは 壁紙で 61〜69px と かわるが、帯の 場所は かわらない）。
    //   帯が それより 上まで 来た とき（字を 大きく して いる など）だけ、その ぶん 上へ（_min：もどさない ＝ 行ったり 来たり しない）。下の タブが ない 画面（横に 広い 画面）は 画面の 下から 10px
    var place = function () {
      var tb = document.querySelector('.tabbar'), r = tb ? tb.getBoundingClientRect() : null;
      var h = r && r.height && getComputedStyle(tb).display !== 'none' ? r.height : 0;
      var mb = document.getElementById('minibar'), q = mb && !mb.hidden ? mb.getBoundingClientRect() : null;
      if (q && q.height) c._min = Math.max(c._min || 0, window.innerHeight - q.top + 6);
      c.style.bottom = h ? 'max(calc(' + (MINI_B + MINI_H + 6) + 'px + var(--sab,0px)),' + (c._min || 0).toFixed(2) + 'px)' : 'calc(10px + env(safe-area-inset-bottom))';
      clear();
    };
    place(); window.addEventListener('resize', place); setTimeout(place, 400); setTimeout(place, 1500);
    try { if (window.ResizeObserver) { var ro = new ResizeObserver(place), tb = document.querySelector('.tabbar'), mb = document.getElementById('minibar'); ro.observe(c); if (tb) ro.observe(tb); if (mb) ro.observe(mb); } } catch (e) { /* なし */ }
    try { var mb2 = document.getElementById('minibar'); if (mb2 && window.MutationObserver) new MutationObserver(place).observe(mb2, { attributes: true, attributeFilter: ['hidden', 'class', 'style'] }); } catch (e) { /* なし */ }
    return c;
  }
  // 列の 下に かくれた ままに ならない ように：main の 下の 余白（列の 高さの ぶん）・保存の 帯の 右の あき
  //   余白は 列の いまの 場所（下の 帯の すぐ 上：いつも 同じ）で 数える
  var GAP = 6;
  function clear() {
    var c = document.getElementById('fabCol'); if (!c) return;
    var r = c.getBoundingClientRect(), root = document.documentElement, mn = document.querySelector('main'), vh = window.innerHeight, vw = root.clientWidth || window.innerWidth;
    var on = r.height > 0;
    var fz = on ? Math.max(0, Math.ceil(vw - 16 - 17 - r.left + GAP)) : 0;                      // 保存の 帯（カードの 中：右はし＝画面の 右から 16＋17）を ちぢめる はば
    if (root.style.getPropertyValue('--fabz') !== fz + 'px') root.style.setProperty('--fabz', fz + 'px');
    if (mn) { var pb = on ? Math.ceil(vh - r.top + GAP + 2) + 'px' : ''; if (mn.style.paddingBottom !== pb) mn.style.paddingBottom = pb; }      // 第4.168版：列は 動かない ので、いまの 場所を そのまま 測る
  }
  // ボタンを 1つ 足す：o＝{ id, order（上からの 順）, name（下に 出す 名前：行ごと）, aria, img（絵）, fb（絵が ない ときの 丸：[字, 地, ふち, 字の 色]）, tap }
  function fabAdd(o) {
    var old = document.getElementById(o.id); if (old) return old;
    var b = document.createElement('button'); b.type = 'button'; b.id = o.id; b.style.order = String(o.order || 0); b.setAttribute('aria-label', o.aria || o.name.join(''));
    var i = document.createElement('span'); i.className = 'fabi';
    var im = new Image(); im.alt = '';
    im.onerror = function () {   // 絵が ない（CI など）：字の 丸
      var t = document.createElement('span'); t.className = 'fabt'; t.style.cssText = 'background:' + o.fb[1] + ';border-color:' + o.fb[2] + ';color:' + o.fb[3]; t.textContent = o.fb[0]; im.replaceWith(t);
    };
    im.src = o.img; i.appendChild(im); b.appendChild(i);
    var l = document.createElement('span'); l.className = 'fabl'; l.textContent = o.name.join('\n'); b.appendChild(l);
    b.addEventListener('click', function () { if (!b.disabled) o.tap(); });
    fabCol().appendChild(b); clear();
    return b;
  }
  window.TengelFab = { add: fabAdd };
  var fab = null, loading = null;
  // 第4.140版：alert() は アプリの 中で 出ない → 画面の お知らせ（下の 黒い 札）
  function note(m) { try { var t = document.getElementById('toast'); if (t) { t.textContent = m; t.hidden = false; clearTimeout(t._tc); t._tc = setTimeout(function () { t.hidden = true; }, 4200); } } catch (e) { /* なし */ } }
  function load() {
    if (window.TCApp) return Promise.resolve();
    if (!loading) loading = new Promise(function (ok, ng) { var s = document.createElement('script'); s.src = 'tc_bundle.js'; s.onload = function () { ok(); }; s.onerror = function () { loading = null; ng(new Error('load')); }; document.head.appendChild(s); });
    return loading;
  }
  function open(opt) {
    if (fab) fab.disabled = true;
    return load().then(function () { return window.TCApp.open(opt); }).catch(function () { note('トレーニングセンターを 読みこめなかったよ。もう一度 押してね'); }).then(function () { if (fab) fab.disabled = false; });
  }
  window.TCOpen = open;
  // ---------- 作戦会議の 入口：判定タブの「レース情報」の カードの 右上（第4.160版・まさちゃん 11/12 14:58「作戦会議は、1番左の項目判定のページでも開けるようにして！アイコンは右上に設置して！」）----------
  //   ・絵は トレーニングセンターの 作戦会議の 札と 同じ（tc_icon_plan.webp：500×200 の 中に 札が 468×141）。絵の 大きさ 118×47 ＝ 見える 札 110×33・押せる 所は 絵 ぜんぶ（高さ 47）
  //   ・場所（第4.165版・11/13 13:55「赤枠の作戦会議のアイコンを青四角のあたりに設置して！」）＝ カードの 右上の かど：
  //       見える 札の 上は カードの 上の ふちより 5px 上・右は カードの 右はしより 11px 外（画面の 右はしから 5px は あける ＝ 右下の 丸い ボタンの 列と 同じ ぐらい）
  //       → 見出しの 右（もと 札が いた 所）が あく（そこへ「壁紙&ボード着せ替え」の ボタン）
  //     画面の 上の 帯の 右上は「説明書」「ミッション」で いっぱい。帯の すぐ 下に うかべると 壁紙の 上の絵に 重なる（11/10 11:32「アイコンが壁紙と重なってるから」）
  //       → カードの すぐ 上の もの（壁紙の 上の絵・単勝5連勝の お知らせ）から 6px は あける（あかない ぶんは 上へ はみ出さない）
  //     壁紙で カードの かどの 丸みや 字が かわる ので、場所は 測って 決める（planPlace：壁紙を かえた とき・字が 読めた とき・画面の 大きさが かわった とき・データの 行が かわった とき）
  //   ・押すと tc_bundle.js を 読んで TCPlan.open(#planHost)。#planHost＝画面 いっぱいの 入れ物（うしろは 判定タブの まま・「とじる」で そのまま 判定タブに もどる）
  //     入れ物は いつも 置いた まま（作戦会議が 閉じて いる 間は 何も 出ない・指も とどかない：pointer-events:none）。作戦会議の 幕は 自分で 指を 受ける
  //   ・開いて いる 間、うしろの 判定タブは 動かさない（幕や 見出しを なぞっても スクロール しない・中身が 短くて スクロール しない ときも）
  //   ・第4.168版（まさちゃん 2026/11/14 02:12「青四角の項目は、表示されるページは画面を上下にスライドしても、位置がずれずそこにいるようにして！」）：
  //     札と「壁紙&ボード着せ替え」の ボタンは 画面に 止める（position:fixed）。前は カードの 中（position:absolute）＝ 画面を 上へ 動かすと カードと いっしょに 流れて 行った。
  //       場所＝ページを いちばん 上に した ときの 場所（カードの 右上の かど：今までと 同じ 見え方）。画面を 動かしても そこに いる（下の 中身は ボタンの 下を 通る）
  //       ボタンは body の 下に 置く（カードや その 親に transform・filter・backdrop-filter が つくと fixed が そこを 基準に して しまう ので、どの 壁紙でも 画面が 基準に なる 所へ）
  //       判定タブ いがいでは 出さない（#v-judge の hidden を 見張る：dockSync）。重なり（z-index 28）＝上の 帯（20）・下の 帯（25）より 上／丸い ボタンの 列（29）・下の タブ（30）・幕（45〜）より 下
  // ---------- 「壁紙&ボード着せ替え」の ボタン（第4.165版・11/13 13:55「黄丸のところに、タップすると壁紙や結果ボードカスタムのところに飛べるアイコン設置して！」
  //            → 14:16「何か変だから、2枚目のアイコンにして、作戦会議のすぐ下に設置してみて！あと下にテロップ入れて！壁紙&ボード着せ替え、って！」）----------
  //   ・絵＝横長の カプセル（tc_icon_kise2.webp：よこ÷たて 2.78）幅 100px・高さ 36px。その 下に 名前の 札「壁紙&ボード着せ替え」（右下の 丸い ボタンの 名前の 札と 同じ 見た目：
  //     いまの 壁紙の 本文の 字・太さ 700・地と 字と 線は 上の 帯と 同じ 色）。札は カプセルの 下の ふちに 3px 重ねる
  //   ・場所＝作戦会議の 札の すぐ 下（3px）・まん中を そろえる（ボタンの 幅は 作戦会議の 見える 札と 同じ 110px ＝ 右はしも 同じ）
  //   ・データの 切りかえ（#slotJudge › .slotbar：折り返す 並び）の 1行めは ボタンと 同じ 高さに 来る ので、ボタンの 手前（4px）で 折り返させる：
  //     ボタンに かかる さいしょの チップの 前に、1行めの のこりを うめる すきまの 部品（.kisesp）を はさむ ＝ その チップから 次の 行へ（2行め からは カードの 幅 いっぱい）。
  //     2行めも ボタンの 高さに かかる とき（見出しが ない など）は、データの 行 ぜんぶの 右を あける（#slotJudge の padding-right）＝ どの 壁紙・どの データの 名前でも 重ならない
  //     データの 行は アプリが 作り直す（中身を 入れかえる）ので、かわる たびに はさみ直す（自分で はさむ 間は 見張りを 止める ＝ ぐるぐる 回らない）
  //   ・押すと 設定タブへ 移って「着せ替え」（#setKisekae：壁紙を えらぶ 所）を 上の 帯の すぐ 下に 出す（その すぐ 下の カードが「結果ボードカスタム」#setBoard）
  //     「着せ替え」の カードの 右上に「結果ボードカスタムへ↓」の 小さい 札（#kiseJump）→ 押すと「結果ボードカスタム」を 上の 帯の すぐ 下に 出す（壁紙が たくさん 並んで いて 遠い ので）
  var PLAN_W = 118, PLAN_H = 47, PLAN_INK = [16 / 500, 30 / 200, 483 / 500, 170 / 200];      // 絵の 中の 札の 場所（左・上・右・下：割合）
  var PLAN_UP = 5, PLAN_OVER = 11, PLAN_EDGE = 5, PLAN_CLEAR = 6;     // 上へ はみ出す 長さ・右へ はみ出す 長さ・画面の 右はしから あける 長さ・すぐ 上の ものから あける 長さ
  var KISE_BOX = 110, KISE_W = 100, KISE_AR = 2047 / 736, KISE_H = Math.round(KISE_W / KISE_AR);      // ボタンの 幅（作戦会議の 見える 札と 同じ）・カプセルの 幅・絵の よこ÷たて（kisekae/tc/kise_asset.py が 出す 数）・高さ 36
  var KISE_UNDER = 3, KISE_LAP = 3, KISE_GAP = 4, KISE_NAME = '壁紙&ボード着せ替え';      // 作戦会議の 札の 下から あける 長さ・名前の 札が カプセルに 重なる 長さ・チップから あける 長さ
  var slotMo = null;                                                  // データの 行の 見張り（MutationObserver）
  var planHost = null, planB = null, oshiB = null, kiseB = null;      // oshiB：右下の 列の 推し馬の ボタン（第4.165版）・kiseB：「壁紙&ボード着せ替え」の ボタン（第4.165版）
  var planCard = null;                                                // 判定タブの「レース情報」の カード（札と ボタンの 場所の 基準：第4.168版）
  function planCss() {
    if (document.getElementById('planCss')) return;
    var st = document.createElement('style'); st.id = 'planCss';
    st.textContent = '#v-judge .card.planc{position:relative}'
      + '#planBtn[hidden],#kiseBtn[hidden]{display:none!important}'
      + '#planBtn{position:fixed;z-index:28;top:-200px;right:5px;width:' + PLAN_W + 'px;height:' + PLAN_H + 'px;margin:0;padding:0;border:0;background:none;color:inherit;-webkit-tap-highlight-color:transparent;cursor:pointer;transition:transform .15s}'
      + '#planBtn:active{transform:scale(.95)}#planBtn:disabled{opacity:.7}'
      + '@media (prefers-reduced-motion:reduce){#planBtn,#kiseBtn{transition:none}}'
      + '#planBtn img{display:block;width:100%;height:100%;pointer-events:none;filter:drop-shadow(0 1px 2px rgba(0,0,0,.28))}'
      + '#planBtn .plt{display:flex;align-items:center;justify-content:center;box-sizing:border-box;width:110px;height:33px;margin:7px 4px;border-radius:5px;border:3px solid #c0241c;background:#f6ead0;color:#b8201a;font:700 15px/1 "BIZ UDPGothic","Hiragino Sans",sans-serif;letter-spacing:.06em;pointer-events:none}'
      + '#kiseBtn{position:fixed;z-index:28;top:-200px;right:5px;width:' + KISE_BOX + 'px;display:flex;flex-direction:column;align-items:center;margin:0;padding:0;border:0;background:none;color:inherit;-webkit-tap-highlight-color:transparent;cursor:pointer;transition:transform .15s}'
      + '#kiseBtn:active{transform:scale(.95)}'
      + '#kiseBtn img,#kiseBtn .kft{display:block;flex:none;width:' + KISE_W + 'px;height:' + KISE_H + 'px;pointer-events:none;filter:drop-shadow(0 1px 2px rgba(0,0,0,.28))}'
      + '#kiseBtn .kft{box-sizing:border-box;border-radius:' + (KISE_H / 2) + 'px;border:3px solid #E2B33C;background:#BFE6C4}'
      + '#kiseBtn .kisel{position:relative;display:block;flex:none;box-sizing:border-box;margin-top:-' + KISE_LAP + 'px;padding:2px 6px 2.5px;border-radius:9px;border:1px solid var(--lamp);background:var(--night);color:var(--night-ink);'
      + 'font-family:var(--font-body);font-weight:700;font-size:9.5px;line-height:11px;letter-spacing:-.01em;text-align:center;white-space:nowrap;box-shadow:0 1px 3px rgba(0,0,0,.25);pointer-events:none}'
      + '#slotJudge .kisesp{display:block;height:1px;min-width:0;margin:0;padding:0;pointer-events:none}'
      + '#setKisekae.kisej{position:relative}'
      + '#kiseJump{position:absolute;top:8px;right:12px;display:inline-flex;align-items:center;height:30px;margin:0;padding:0 12px;border-radius:999px;border:1px solid var(--line);background:var(--surface-2);color:inherit;font:inherit;font-size:12px;font-weight:700;line-height:1;white-space:nowrap;-webkit-tap-highlight-color:transparent;cursor:pointer}'
      + '#kiseJump:active{opacity:.7}'
      + '#planHost{position:fixed;left:0;top:0;right:0;bottom:0;z-index:90;pointer-events:none}'
      + '#planHost>#tcPlan{pointer-events:auto;touch-action:none}'
      + '#planHost .pb{overscroll-behavior:contain}';
    document.head.appendChild(st);
  }
  // カードの すぐ 上の もの（壁紙の 上の絵・単勝5連勝の お知らせ）までの すきま。上に 何も ない ときは ページの 上の 余白
  function roomAbove(card, cr) {
    for (var e = card; e && e.id !== 'v-judge' && e !== document.body; e = e.parentNode) {
      for (var p = e.previousElementSibling; p; p = p.previousElementSibling) { var r = p.getBoundingClientRect(); if (r.height > 0 && r.width > 0) return cr.top - r.bottom; }
    }
    var mn = document.querySelector('main'); return (mn && parseFloat(getComputedStyle(mn).paddingTop)) || 0;
  }
  function px(el, k, v) { v = Math.round(v) + 'px'; if (el.style[k] !== v) el.style[k] = v; }
  // 札と「壁紙&ボード着せ替え」の ボタンの 場所（第4.168版：画面に 止める position:fixed。ページを いちばん 上に した ときの カードの 右上の かど）
  //   カードの いまの 場所（cr）＋ ページを 動かした 長さ（sy）＝ ページを いちばん 上に した ときの 場所 ＝ 画面を 動かしても かわらない
  function planPlace() {
    var b = planB, card = planCard; if (!b || !card) return;
    var cr = card.getBoundingClientRect(); if (!cr.width || !cr.height) return;                              // 判定タブが 出て いない
    var cs = getComputedStyle(card), br = parseFloat(cs.borderRightWidth) || 0;
    var vw = document.documentElement.clientWidth || window.innerWidth, sy = window.pageYOffset || document.documentElement.scrollTop || 0;
    var over = Math.max(0, Math.min(PLAN_OVER, vw - cr.right - PLAN_EDGE));                                  // 右へ はみ出す（画面の 右はしから 5px は あける）
    var up = Math.max(0, Math.min(PLAN_UP, roomAbove(card, cr) - PLAN_CLEAR));                               // 上へ はみ出す（すぐ 上の ものから 6px は あける）
    var inkT = PLAN_INK[1] * PLAN_H, inkB = PLAN_INK[3] * PLAN_H, inkR = (1 - PLAN_INK[2]) * PLAN_W;
    var top = cr.top + sy - up, rgt = vw - cr.right - over;                                                  // 見える 札の 上（ページの 上から）・右（画面の 右はしから）
    px(b, 'top', top - inkT); px(b, 'right', rgt - inkR);
    var k = kiseB; if (!k) return;
    // ---- 「壁紙&ボード着せ替え」の ボタン：作戦会議の 札の すぐ 下（右はしは 札と 同じ）----
    px(k, 'top', top + (inkB - inkT) + KISE_UNDER); px(k, 'right', rgt);
    slotFit(card, k, cr.right - br - (parseFloat(cs.paddingRight) || 0), sy);
  }
  // 判定タブが 出て いる あいだ だけ 出す（ボタンは body の 下に ある ので、タブを かえたら 自分で かくす）
  function dockSync() {
    var v = document.getElementById('v-judge'), on = !!v && !v.hidden;
    [planB, kiseB].forEach(function (e) { if (e && e.hidden !== !on) e.hidden = !on; });
    if (on) planPlace();
  }
  // データの 行を ボタンの 手前で 折り返させる（right＝カードの 中身の 右はし・sy＝ページを 動かした 長さ：ボタンは 画面に 止まって いる ので、行と 同じ 物さしに 直して くらべる）
  function slotFit(card, k, right, sy) {
    var sj = card.querySelector('#slotJudge'); if (!sj) return;
    var bar = sj.querySelector('.slotbar'), sp = bar ? bar.querySelector('.kisesp') : null;
    var items = bar ? [].slice.call(bar.children).filter(function (e) { return e !== sp && e.getBoundingClientRect().height > 0; }) : [];
    var kq = k.getBoundingClientRect(), lab = k.querySelector('.kisel'), lr = lab ? lab.getBoundingClientRect() : kq;
    var kr = { left: kq.left, top: kq.top - (sy || 0), bottom: kq.bottom - (sy || 0) };                       // ページと いっしょに 動いた と した ときの ボタンの 場所
    var limit = Math.min(kr.left, lr.left) - KISE_GAP, bottom = Math.max(kr.bottom, lr.bottom - (sy || 0));  // チップの 右はしの 限り・ボタン（名前の 札まで）の 下
    var want = -1, fill = 0, pad = '';
    if (items.length) {
      var bs = getComputedStyle(bar), gap = parseFloat(bs.columnGap) || 0, rgap = parseFloat(bs.rowGap) || 0, r0 = items[0].getBoundingClientRect();
      var c0 = (r0.top + r0.bottom) / 2, rowT = r0.top, rowB = r0.bottom;                                    // 1行めの 上と 下（同じ 行の ものは まん中の 高さが 同じ：いちばん 高い チップで 決まる）
      items.forEach(function (it) { var r = it.getBoundingClientRect(); if (Math.abs((r.top + r.bottom) / 2 - c0) < 2) { rowT = Math.min(rowT, r.top); rowB = Math.max(rowB, r.bottom); } });
      if (rowT < bottom + 2 && rowB > kr.top - 2) {                                                          // 1行めが ボタンと 同じ 高さに ある
        var x = r0.left, e = r0.left;
        for (var i = 0; i < items.length; i++) {                                                             // 1行めに 左から 並べて いって、限りを こえる さいしょの もの
          var w = items[i].getBoundingClientRect().width;
          if (i && x + w > limit + 0.01) { want = i; break; }
          e = x + w + (parseFloat(getComputedStyle(items[i]).marginRight) || 0); x = e + gap;
        }
        if (want > 0) {
          fill = Math.floor(right - (e + gap) - 1);                                                          // 1行めの のこり（1px 少なく：部品 自身が 次の 行へ 落ちない）
          if (fill < 1) want = -1;                                                                           // のこりが ない ＝ そのままでも 次の 行へ 行く
          if (rowB + rgap < bottom + 2) { want = -1; pad = Math.ceil(right - limit) + 'px'; }                // 2行めも ボタンの 高さに かかる → 行 ぜんぶの 右を あける
        }
      }
    }
    var same = sj.style.paddingRight === pad && (want < 0 ? !sp : !!sp && sp.nextElementSibling === items[want] && sp.style.flexBasis === fill + 'px');
    if (same) return;
    if (slotMo) slotMo.disconnect();                                                                         // 自分で かえる 間は 見張りを 止める
    sj.style.paddingRight = pad;
    if (want < 0) { if (sp) sp.remove(); }
    else {
      if (!sp) { sp = document.createElement('span'); sp.className = 'kisesp'; sp.setAttribute('aria-hidden', 'true'); }
      sp.style.flex = '1 0 ' + fill + 'px';
      if (sp.parentNode !== bar || sp.nextElementSibling !== items[want]) bar.insertBefore(sp, items[want]);
    }
    if (slotMo) slotMo.observe(sj, { childList: true, subtree: true, characterData: true });
  }
  // 設定タブの 欄を 上の 帯の すぐ 下に 出す（上の 帯は 3段に なると 高い ので、帯の 下の はしを 測って 合わせる）
  function secGo(id, tab) {
    if (tab) {
      var tb = document.querySelector('.tabbar [data-tab="set"]'), t2 = document.querySelector('.tabs-top [data-tab="set"]');
      if (tb && getComputedStyle(tb.parentNode).display !== 'none') tb.click(); else if (t2) t2.click(); else if (tb) tb.click();
    }
    var want = null;
    var go = function () {
      var s = document.getElementById(id); if (!s) return;
      var r = s.getBoundingClientRect(); if (!r.height) return;
      var hd = document.querySelector('header.top'), hb = hd ? hd.getBoundingClientRect().bottom : 0;
      want = Math.max(0, Math.round(window.scrollY + r.top - hb - 8)); window.scrollTo(0, want);
    };
    if (!tab) { go(); return; }
    setTimeout(function () { kiseJump(); go(); }, 60);
    setTimeout(function () { if (want == null || Math.abs(window.scrollY - want) < 3) go(); }, 450);      // 上の 欄の 高さが あとから かわった とき だけ 合わせ直す（自分で 動かして いたら さわらない）
  }
  function kiseGo() { secGo('setKisekae', true); }
  window.KiseGo = kiseGo;
  // 「着せ替え」の カードの 右上：「結果ボードカスタムへ↓」の 札（結果ボードカスタムの カードが ある とき だけ）
  function kiseJump() {
    var c = document.getElementById('setKisekae'); if (!c || document.getElementById('kiseJump') || !document.getElementById('setBoard')) return;
    planCss(); c.classList.add('kisej');
    var j = document.createElement('button'); j.type = 'button'; j.id = 'kiseJump'; j.textContent = '結果ボードカスタムへ↓';
    j.addEventListener('click', function () { secGo('setBoard', false); });
    c.appendChild(j);
  }
  // opt.oshi：開いたら「推し馬」の 欄まで 進める（右下の 推し馬の ボタンから：第4.165版）
  function planOpen(opt) {
    var bs = [planB, oshiB], lock = function (v) { bs.forEach(function (b) { if (b) b.disabled = v; }); };
    lock(true);
    return load().then(function () {
      planCss();
      if (!planHost) {
        planHost = document.createElement('div'); planHost.id = 'planHost'; document.body.appendChild(planHost);
        planHost.addEventListener('touchmove', function (e) {      // うしろの ページを 動かさない：スクロール できる 中身（.pb）の 中 だけ 指で 動かせる
          var t = e.target, pb = t && t.closest ? t.closest('.pb') : null;
          if (!pb || pb.scrollHeight <= pb.clientHeight + 1) { if (e.cancelable) e.preventDefault(); }
        }, { passive: false });
      }
      return window.TCPlan.open(planHost, opt && opt.oshi ? { oshi: true } : null);
    }).catch(function () { note('作戦会議を 読みこめなかったよ。もう一度 押してね'); }).then(function () { lock(false); });
  }
  window.TCPlanOpen = planOpen;
  function planBoot() {
    if (document.getElementById('planBtn')) return;
    var card = document.querySelector('#v-judge .card'), h = card && card.querySelector('h2'); if (!card || !h) return;
    planCss(); card.classList.add('planc');
    var b = document.createElement('button'); b.type = 'button'; b.id = 'planBtn'; b.setAttribute('aria-label', '作戦会議（押すと ひらくよ）');
    var im = new Image(); im.alt = '';
    im.onerror = function () { var t = document.createElement('span'); t.className = 'plt'; t.textContent = '作戦会議'; im.replaceWith(t); };      // 絵が ない（CI など）：字の 札
    im.src = 'tc_icon_plan.webp'; b.appendChild(im);
    b.addEventListener('click', function () { if (!b.disabled) planOpen(null); });
    planCard = card; document.body.appendChild(b); planB = b;                                                // 第4.168版：body の 下（画面に 止める）
    // 第4.165版：「壁紙&ボード着せ替え」の ボタン（作戦会議の 札の すぐ 下：カプセルの 絵 ＋ 名前の 札）→ 設定タブの「着せ替え」へ
    var k = document.createElement('button'); k.type = 'button'; k.id = 'kiseBtn'; k.setAttribute('aria-label', KISE_NAME + '（押すと 設定の 着せ替え・結果ボードカスタムを ひらくよ）');
    var km = new Image(); km.alt = '';
    km.onerror = function () { var t = document.createElement('span'); t.className = 'kft'; km.replaceWith(t); };      // 絵が ない（CI など）：色の カプセル（名前は 下の 札に ある）
    km.src = 'tc_icon_kise2.webp'; k.appendChild(km);
    var kl = document.createElement('span'); kl.className = 'kisel'; kl.textContent = KISE_NAME; k.appendChild(kl);
    k.addEventListener('click', kiseGo);
    document.body.appendChild(k); kiseB = k;
    dockSync(); window.addEventListener('resize', planPlace); setTimeout(planPlace, 400); setTimeout(planPlace, 1500);
    var vj = document.getElementById('v-judge'), ro = null;
    try { if (vj && window.MutationObserver) new MutationObserver(dockSync).observe(vj, { attributes: true, attributeFilter: ['hidden'] }); } catch (e) { /* なし */ }      // タブを かえた
    try {
      if (window.ResizeObserver) {
        ro = new ResizeObserver(planPlace); ro.observe(card); ro.observe(h);
        // カードより 上の もの（上の 帯・壁紙の 上の絵・お知らせ）の 高さが かわると カードの 場所が かわる（第4.168版：ボタンは 画面に 止まって いる ので 測り直す）
        var hd = document.querySelector('header.top'); if (hd) ro.observe(hd);
        for (var el = card; el && el !== document.body; el = el.parentNode) for (var p = el.previousElementSibling; p; p = p.previousElementSibling) if (p !== hd && !/^(SCRIPT|STYLE|LINK)$/.test(p.tagName)) ro.observe(p);
      }
    } catch (e) { /* なし */ }
    try {                                                                                                    // 判定タブの 上に あとから 入る もの（壁紙の 上の絵 #ksBnr）も 見張る
      if (vj && window.MutationObserver) new MutationObserver(function (ms) {
        ms.forEach(function (m) { [].forEach.call(m.addedNodes || [], function (n) { if (ro && n.nodeType === 1) ro.observe(n); }); });
        planPlace();
      }).observe(vj, { childList: true });
    } catch (e) { /* なし */ }
    try { var sj = card.querySelector('#slotJudge'); if (sj && window.MutationObserver) { slotMo = new MutationObserver(planPlace); slotMo.observe(sj, { childList: true, subtree: true, characterData: true }); } } catch (e) { /* なし */ }      // データの 行を 作り直した・名前や 数が かわった
    setTimeout(kiseJump, 0); setTimeout(kiseJump, 1500);
    try { if (document.fonts && document.fonts.ready) document.fonts.ready.then(planPlace); } catch (e) { /* なし */ }
    try { if (document.fonts && document.fonts.addEventListener) document.fonts.addEventListener('loadingdone', planPlace); } catch (e) { /* なし */ }      // 壁紙の 字が あとから 読めた（チップの 幅が かわる）
    try { if (window.MutationObserver) new MutationObserver(function () { planPlace(); setTimeout(planPlace, 300); setTimeout(planPlace, 1200); }).observe(document.documentElement, { attributes: true, attributeFilter: ['data-ks'] }); } catch (e) { /* なし */ }      // 壁紙を かえた
  }
  function boot() {
    if (document.getElementById('tcFab')) return;
    // 第4.165版：推し馬（列の 1番 上）→ 作戦会議の「推し馬」の 欄を すぐ 開く
    oshiB = fabAdd({ id: 'oshiFab', order: 0, name: ['推し馬'], aria: '推し馬（押すと 作戦会議の 推し馬の 欄を ひらくよ）', img: 'tc_icon_oshi.webp', fb: ['推し馬', '#BFE6C4', '#E2B33C', '#5B3412'], tap: function () { planOpen({ oshi: true }); } });
    fab = fabAdd({ id: 'tcFab', order: 1, name: ['トレーニング', 'センター'], aria: 'トレーニングセンター（押すと ひらくよ）', img: 'tc_icon_tc.webp', fb: ['トレセン', '#1F5A2E', '#E2B33C', '#FFF3C4'], tap: function () { open(); } });
    planBoot();
  }
  // 通知を 押した（作戦会議）→ トレーニングセンターの 作戦会議を 開く
  document.addEventListener('tengel:native', function (e) {
    var d = e.detail || {}; if (d.name === 'notify' && d.payload && /^plan-/.test(String(d.payload.id || ''))) open({ plan: true });
  });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
