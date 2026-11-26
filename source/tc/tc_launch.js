// トレーニングセンターの 入口（App Store版だけ・index.html の 中に 入る 小さい 部分）
//   ・どの タブでも 右下（下の タブの すぐ 上）に 丸い ボタン（絵＋下に 名前の 札「トレーニング／センター」）→ 押すと tc_bundle.js を 読んで TCApp.open()
//     （11/09 13:04 まさちゃん「右下にうかぶ丸ボタン」→ 11/10 09:45「右上の赤丸の場所にして！」→ 11/10 11:32「アイコンが壁紙と重なってるから、右下に移動して！」
//       ・11/10 09:57「トレーニングセンターのアイコンこれにして！」「アイコンの下に、トレーニングセンター、思い出フィギュア、って壁紙に合う文字で」）
//     その 下に 思い出フィギュアの ボタン（fig/fig_launch.js が ここの TengelFab.add で 入れる：同じ 列 #fabCol・上から トレーニングセンター → 思い出フィギュア）
//     第4.176版（11/16 00:47 まさちゃん「トレーニングセンターを一番上、カードバトルを思い出フィギュアの上にして ①トレーニングセンター ②推し馬 ③カードバトル ④思い出フィギュア」）：
//       列の 順＝上から トレーニングセンター（#tcFab）→ 推し馬（#oshiFab）→ カードバトル（#cbFab：cb/cb_launch.js）→ 思い出フィギュア（#figFab：fig/fig_launch.js）
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
  //   発走の 時刻（ミリ秒・この 端末の 時刻）。日付か 時刻が ない ときは 0（第4.221版：推し馬の 丸の 🔔 と いっしょに 使う）
  function planStart(r) {
    if (!r || !/^\d{4}-\d{2}-\d{2}$/.test(r.date || '') || !/^\d{1,2}:\d{2}$/.test(r.time || '')) return 0;
    var d = r.date.split('-'), hm = r.time.split(':');
    return new Date(+d[0], +d[1] - 1, +d[2], +hm[0], +hm[1], 0).getTime();
  }
  window.TCPlanNotify = function () {
    var P = jget(PK); if (!P || !P.on || !Array.isArray(P.races)) return [];
    var now = Date.now(), out = [];
    P.races.forEach(function (r) {
      var at0 = planStart(r); if (!at0) return;
      (r.notify || []).forEach(function (m) {
        var at = at0 - m * 60000; if (at <= now + 5000) return;
        out.push({ id: 'plan-' + r.id + '-' + m, at: at, title: 'まもなく発走！', body: (r.name || 'レース') + '　' + r.time + ' 発走（あと' + m + '分）', race: '' });
      });
    });
    return out;
  };
  // ---------- 第4.230版（まさちゃん 2026/11/26 22:46「紫四角の中のアイコンを、青四角のところに配置して、赤四角のアイコンを黄四角の位置に大きさいい感じに調整して入れられない？」）----------
  //   ・丸い ボタン 4つ（トレーニングセンター・推し馬・カードバトル・思い出フィギュア）は、下の タブの すぐ 上に 横 1列（#fabCol.rw：画面の 幅を 4つで 分ける・丸の 大きさは 幅で 決める）。
  //     前は 右はしに たて 1列（中身の カードの 右に かかって いた）。判定の 帯（#minibar）・保存の 帯・お知らせは 列の 上（--fabt：src.html の CSS）。
  //     main の 下の 余白＝列の 高さ ＋ 判定の 帯（いちばん 下まで 動かすと 最後の 中身が 帯の 上まで 上がる）
  //     23:16「大きさもう少し隙間なく入るようにして！後、白の背景いらないよ！前と同じでくり抜いてる感じでいい！推し馬の文字だけ小さく見えるから周りと合わせて！」：
  //     丸は 1つ ぶんの 幅の 80%（44〜80px）・うしろの 地は なし（中身の 上に うかぶ）・名前の 札は 4つとも 同じ 大きさ（1行の 推し馬は 字を 大きく：.l1）
  //   ・作戦会議の 札と「壁紙&ボード着せ替え」の ボタンは 上の 帯の 中（帯と いっしょに 動く：.dk）。23:23「結果待ちの下に作戦会議、ミッションの下に着せ替えボードのアイコン入れて！
  //     テンゲルデータは、テンゲルⅢの文字の下に入れて！全体的に大きさなど違和感なく揃えて！」：3段目に 作戦会議（結果待ちの 下）・着せ替え（ミッションの 下）、
  //     テンゲルデータの 札は 2段目の ロゴの 下（下の dockArea・dockPut）。23:21「作戦会議と、着せ替えは、判定のところ以外、単勝5連勝、記録、実測・回収、設定のところでも表示されるようにして！」：
  //     上の 帯の 中に 置いた ときは どの タブでも 出す。置けない 画面（広い 画面の 1段の 帯 など）は 前の 場所（レース情報の カードの 右上：判定タブ だけ）
  // ---------- 右下の 丸い ボタンの 列（#fabCol）：上から トレーニングセンター（#tcFab）→ 推し馬（#oshiFab：第4.165版）→ カードバトル（#cbFab：第4.176版・cb/cb_launch.js）→ 思い出フィギュア（#figFab：fig/fig_launch.js）。
  //            あとの 2つは TengelFab.add で 入れる。順（order）は 第4.176版（まさちゃん 2026/11/16 00:47）から：前は 推し馬 → トレーニングセンター → 思い出フィギュア ----------
  //   ・場所：下の タブの すぐ 上・右はし（画面に 固定）。11/10 09:45「右上の赤丸の場所にして！」で 上の 帯の すぐ 下に した（第4.138版）が、
  //     判定タブで 壁紙の 上の絵に 重なる → 11:32「アイコンが壁紙と重なってるから、右下に移動して！」で 右下へ（第4.139版）
  //   ・ボタン＝丸い 絵（66px まで：第4.176版から 画面に 合わせて 小さく する。下の fabFit）＋ その 下の 名前の 札（.fabl・2行）。押せる のは 絵と 札だけ（まわりの すきまは 下の 画面に とどく）
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
  //       第4.176版（まさちゃん 2026/11/16 01:15「この青四角下の空間気になる。大きさ調整して空間があかないようにして！」）：たてに 1列の ときは 列を 下の タブの すぐ 上まで 下げる
  //       （帯の 上に あけて いた 40px ほどの 空間を なくす）。帯は 列の 手前で 終わる ように 右を ちぢめる（--fabm：帯が 出ても 消えても 列は 動かない・帯の 字は かくれない）・
  //     買い目編集の「保存する」の 帯（.zsave.sticky：変更が ある あいだ 下に はりつく）は 右を ちぢめて 列の 手前で 終わる（--fabz）
  var MINI_B = 58, MINI_H = 40;            // 下の 帯（#minibar）：画面の 下からの 場所（src.html：bottom:calc(58px + var(--sab,0px))）・高さ（どの 壁紙でも 39.2px → 40。test_tc.py が 測る）
  function fabCol() {
    var c = document.getElementById('fabCol'); if (c) return c;
    var st = document.createElement('style'); st.id = 'fabColCss';
    // 第4.176版：ボタンが 4つに なった（カードバトルが 入った）。前の 大きさ（丸 66px）の まま たてに 4つ ならべると 352px で、どの iPhone でも 列の 上が 判定タブの 右上の
    //   「作戦会議」「壁紙&ボード着せ替え」に 重なる（アプリの 画面の 高さ＝iPhone の 高さ − 上の 時計の 帯。下は ホームバーの ぶん あける：390×844 の iPhone で、着せ替えの ボタンの 下から 使える 高さは 約240px）。
    //   → まさちゃん 2026/11/16 00:34「丸のアイコン組を少し小さくして！ピッタリ収まるようにできない？」：**たてに 4つの まま、丸の 大きさ（--fd）を 画面に 合わせて 決める**（下の fabFit：66px から 1px ずつ 小さく して、
    //     着せ替えの ボタンの 下に おさまる いちばん 大きい 大きさ。名前の 字・札も 丸に 合わせて 小さく なる）。丸を 36px に しても たてに おさまらない 画面（iPhone SE など）だけ 2列 × 2段（.g2：
    //     順の とおりに 左の 列の 上 → 下、右の 列の 上 → 下 ＝ 左：トレーニングセンター・推し馬／右：カードバトル・思い出フィギュア）
    //   → 01:15「この青四角下の空間気になる。大きさ調整して空間があかないようにして！」：列の 下を 下の タブの すぐ 上に して（下の place）、「壁紙&ボード着せ替え」の すぐ 下 〜 下の タブの すぐ 上 を
    //     4つで ぴったり うめる（丸は その ぶん 大きく なる：390×844 の iPhone で 46px → 53〜58px）。判定の 帯（#minibar）は 列の 手前で 終わる（右の あき --fabm：下の clear が 入れる）
    st.textContent = '#fabCol{position:fixed;right:4px;bottom:calc(69px + var(--sab,0px));z-index:29;display:flex;flex-direction:column;align-items:center;gap:2px;pointer-events:none;--fd:66px}'
      + '#fabCol.g2{display:grid;grid-template-rows:auto auto;grid-auto-flow:column;justify-items:center;align-items:start}'
      // 第4.230版：横 1列（.rw）＝ 画面の 幅を ボタンの 数で 分けて、まん中に 丸と 名前の 札。広い 画面は 480px まで（まん中に よせる）。うしろの 地は なし（前と 同じ：中身の 上に うかぶ）
      //   名前の 札は 4つとも 同じ 大きさ（2行の 札の 大きさ：--lf＝名前の 字の 大きさ）。1行の 名前（推し馬）は 字を 大きく して 札の まん中に（.l1）
      //   （まさちゃん 11/26 23:16「大きさもう少し隙間なく入るようにして！後、白の背景いらないよ！前と同じでくり抜いてる感じでいい！推し馬の文字だけ小さく見えるから周りと合わせて！」）
      + '#fabCol.rw{left:0;right:0;max-width:480px;margin:0 auto;flex-direction:row;align-items:flex-start;justify-content:space-evenly;gap:0;padding:0 4px;box-sizing:border-box;--lf:clamp(8px,calc(var(--fd) * .145),11.5px)}'
      + '#fabCol.rw>button{flex:1 1 0;min-width:0}'
      + '#fabCol.rw .fabl{font-size:var(--lf);padding:calc(var(--lf) * .2) calc(var(--lf) * .5) calc(var(--lf) * .26);min-width:calc(var(--lf) * 7 + 2px);min-height:calc(var(--lf) * 2.78 + 2px);max-width:100%}'
      + '#fabCol.rw .fabl.l1{display:flex;align-items:center;justify-content:center;font-size:calc(var(--lf) * 1.25);line-height:1.1}'
      // 第4.222版：ボタンごとに 重なりの 順（z-index：下の fabZ が 入れる）。下の 段の ボタンほど 前 ＝ 丸の 右上の 札（数・🔔）は 上の ボタンの 名前の 札より 前に 出る
      + '#fabCol>button{position:relative;pointer-events:none;display:flex;flex-direction:column;align-items:center;border:0;padding:0;margin:0;background:none;color:inherit;-webkit-tap-highlight-color:transparent;transition:transform .15s}'
      + '#fabCol>button:active{transform:scale(.94)}#fabCol>button:disabled{opacity:.7}'
      + '#fabCol .fabi{pointer-events:auto;cursor:pointer;display:block;width:var(--fd);height:var(--fd);border-radius:50%;filter:drop-shadow(0 3px 5px rgba(0,0,0,.35))}'
      + '#fabCol .fabi img{width:100%;height:100%;display:block;pointer-events:none}'
      + '#fabCol .fabt{display:flex;align-items:center;justify-content:center;width:100%;height:100%;border-radius:50%;box-sizing:border-box;border:4px solid;font:400 12px/1.15 var(--font-display,sans-serif);font-size:calc(var(--fd) * .182);text-align:center}'
      + '#fabCol .fabl{pointer-events:auto;cursor:pointer;position:relative;display:block;box-sizing:border-box;min-width:calc(var(--fd) - 2px);margin-top:-8px;padding:.2em .6em .26em;border-radius:9px;border:1px solid var(--lamp);background:var(--night);color:var(--night-ink);'
      + 'font-family:var(--font-body);font-weight:700;font-size:clamp(7px,calc(var(--fd) * .144),9.5px);line-height:1.16;letter-spacing:-.01em;text-align:center;white-space:pre;box-shadow:0 1px 3px rgba(0,0,0,.25)}'
      // 第4.221版：丸の 右上の 小さい 札（fabMark）。.fabc＝数（.tk お世話トークン：金の コイン・.qt 調査隊切符：切符の 赤茶・.z 0）・.fabb＝🔔（推し馬：作戦会議の お知らせ）。
      //   丸の 中（.fabi）に 置く ＝ 押せる 所・列の 並びは かわらない（押すと 丸が 押される）。大きさは 丸に 合わせる（小さい 丸でも 字は 10.5px より 小さく しない）。
      //   右へ はみ出すのは 3px まで（列は 画面の 右はしから 4px：名前の 札が 丸より せまい とき 丸の 右はしが 列の 右はし ＝ それ より 出すと 画面の 外へ 切れる）
      + '#fabCol .fabi{position:relative}'
      + '#fabCol .fabc{position:absolute;top:calc(var(--fd) * -.05);right:max(-3px,calc(var(--fd) * -.06));z-index:1;box-sizing:border-box;display:flex;align-items:center;justify-content:center;min-width:max(18px,calc(var(--fd) * .36));height:max(18px,calc(var(--fd) * .36));'
      + 'padding:0 max(4px,calc(var(--fd) * .07));border-radius:999px;border:1.5px solid #fff;font-family:var(--font-body,sans-serif);font-weight:800;font-size:max(10.5px,calc(var(--fd) * .215));line-height:1;font-variant-numeric:tabular-nums;letter-spacing:-.02em;white-space:nowrap;'
      + 'box-shadow:0 1px 2px rgba(0,0,0,.4);pointer-events:none}'
      + '#fabCol .fabc[hidden],#fabCol .fabb[hidden]{display:none}'
      + '#fabCol .fabc.tk{background:linear-gradient(#fff0b0,#f0c04a 55%,#d99a1e);color:#5b3412;border-color:#fffbe8}'
      + '#fabCol .fabc.qt{background:linear-gradient(#c2483a,#7a2018);color:#ffe7a6;border-color:#f6d77e}'
      + '#fabCol .fabc.z{filter:grayscale(.8)}'
      + '#fabCol .fabb{position:absolute;top:calc(var(--fd) * -.07);right:max(-3px,calc(var(--fd) * -.06));z-index:1;box-sizing:border-box;display:flex;align-items:center;justify-content:center;width:max(19px,calc(var(--fd) * .4));height:max(19px,calc(var(--fd) * .4));'
      + 'border-radius:50%;border:1.5px solid #fff;background:#e0245e;font-size:max(10.5px,calc(var(--fd) * .23));line-height:1;box-shadow:0 1px 2px rgba(0,0,0,.4);pointer-events:none;transform-origin:50% 12%;animation:fabRing 2.6s ease-in-out infinite}'
      + '@keyframes fabRing{0%,64%,100%{transform:rotate(0)}68%{transform:rotate(15deg)}74%{transform:rotate(-13deg)}80%{transform:rotate(9deg)}86%{transform:rotate(-5deg)}92%{transform:rotate(2deg)}}'
      + '@media (prefers-reduced-motion:reduce){#fabCol .fabb{animation:none}}'
      + '.zsave.sticky{margin-right:var(--fabz,0px)}'
      + '#minibar{padding-right:var(--fabm,12px)}'       // 判定の 帯：右の あき（もとは 12px）を 列の 手前まで 広げる ＝ 帯（まん中に よせた 丸い 札）は 列に かからない。字が 入らない ぶんは「…」
      // ちぢめた とき（.fabn：下の clear が つける）は 少し つめる（左の あき 12 → 6px・中の すきま 10 → 6px・字 13 → 12px）：そのままだと A層・B層の 2本の ゾーン
      //   （「8R 第1 中穴→人気・第2 人気→大穴」）が 幅 390px の iPhone で 20〜29px 入らず「…」に なる（測った：30この 壁紙 ぜんぶ）→ つめると 幅 375・390・402・430px とも 入る
      + '#minibar.fabn{padding-left:6px}#minibar.fabn button{gap:6px;padding:7px 5px 7px 6px;font-size:12px}#minibar.fabn .go{padding-right:4px}';
    document.head.appendChild(st);
    c = document.createElement('div'); c.id = 'fabCol'; c.className = 'rw'; document.body.appendChild(c);      // 第4.230版：横 1列
    // 場所：列の 下は 2とおり（どちらに するかは fabFit が 決める。どちらも 帯が 出ても 消えても・どの タブでも・画面を 上下に 動かしても 動かない）
    //   ・たてに 1列（_b1：第4.176版）：下の タブの すぐ 上（FAB_B）。下の タブの 高さは 壁紙で 61〜69px と かわる ので 測る
    //   ・2列 × 2段（_b2：たての 短い 画面。第4.168版の 場所の まま）：判定タブの 下の 帯（#minibar）が 出る 所の すぐ 上（6px）。帯は 画面の 下から MINI_B（＋下の 安全な 余白 --sab）の 所に
    //     高さ MINI_H で 出る。帯が それより 上まで 来た とき（字を 大きく して いる など）だけ、その ぶん 上へ（_min：もどさない ＝ 行ったり 来たり しない）。かたまりが 広い ので 帯は ちぢめない
    //   下の タブが ない 画面（横に 広い 画面）は 画面の 下から 10px
    var place = function () {
      var tb = document.querySelector('.tabbar'), r = tb ? tb.getBoundingClientRect() : null;
      var h = r && r.height && getComputedStyle(tb).display !== 'none' ? r.height : 0;
      var mb = document.getElementById('minibar'), q = mb && !mb.hidden ? mb.getBoundingClientRect() : null;
      if (q && q.height) c._min = Math.max(c._min || 0, window.innerHeight - q.top + 6);
      var wide = 'calc(10px + env(safe-area-inset-bottom))';
      // 下の タブの 高さの うち、下の 安全な 余白（--sab：タブの 下の あき）の ぶんは CSS に まかせる ＝ アプリが あとから 余白を 知らせて も そのまま ついて いく
      var pad = h ? parseFloat(getComputedStyle(tb).paddingBottom) || 0 : 0;
      c._b1 = h ? 'calc(' + (Math.round((window.innerHeight - r.top - pad + FAB_B) * 10) / 10) + 'px + var(--sab,0px))' : wide;
      c._b2 = h ? 'max(calc(' + (MINI_B + MINI_H + 6) + 'px + var(--sab,0px)),' + (c._min || 0).toFixed(2) + 'px)' : wide;
      var b = c.classList.contains('g2') ? c._b2 : c._b1; if (c.style.bottom !== b) c.style.bottom = b;
      fitAsk();
    };
    place(); window.addEventListener('resize', place); setTimeout(place, 400); setTimeout(place, 1500);
    fitHold(2000);                                                          // はじめの 2秒：壁紙の 字が 読める まで 上の 帯の 高さが 動く → 落ち着いて から 決め直す
    try { if (window.ResizeObserver) { var ro = new ResizeObserver(place), tb = document.querySelector('.tabbar'), mb = document.getElementById('minibar'); ro.observe(c); if (tb) { try { ro.observe(tb, { box: 'border-box' }); } catch (e2) { ro.observe(tb); } } if (mb) ro.observe(mb); } } catch (e) { /* なし */ }      // 下の タブ：下の あき（余白）が かわった ときも 知る（border-box）
    try { var mb2 = document.getElementById('minibar'); if (mb2 && window.MutationObserver) new MutationObserver(place).observe(mb2, { attributes: true, attributeFilter: ['hidden', 'class', 'style'] }); } catch (e) { /* なし */ }
    return c;
  }
  // 丸の 大きさを 決める（第4.176版）：判定タブの 右上の「壁紙&ボード着せ替え」の ボタンの すぐ 下（FD_PAD）から 列の 下（下の タブの すぐ 上）まで を、4つで ぴったり うめる
  //   ＝ おさまる いちばん 大きい 丸（もとの 大きさ 66px まで・36px から。名前の 字・札も 丸に 合わせて かわる）。高さは じっさいに ならべて 測る（名前が 1行・2行の ボタンが ある ので 計算 しない）。
  //   ・着せ替えの ボタンの 下の 場所（_kb）：判定タブが 出て いる ときに 測って 覚える（ほかの タブでは ボタンは かくれて いる → 覚えた 場所を 使う ＝ どの タブでも 同じ 大きさ）。
  //     壁紙で かわる（上の 帯と 上の絵が 高い 壁紙ほど 下）ので、壁紙を かえると 丸の 大きさも 少し かわる。まだ 測って いない あいだは、いちばん 下に 来る 壁紙（星座）の 場所：
  //     画面の 幅 375px で 上から 409px・幅が 1px 広い ごとに 0.44px 下（測った 数：幅 320→384.5・375→407.5・390→414.5・402→420.5・414→425.5・430→431.5・440→435.5）
  //   ・36px でも たてに おさまらない 画面（iPhone SE で 壁紙の 上の絵が ある とき など）は 2列 × 2段（.g2：場所は 判定の 帯の 上＝_b2）で 同じ ように さがす
  //   ・壁紙を かえた すぐ あと・はじめ は 決め直さない（fitHold）：新しい 字が 読める まで 上の 帯が いっとき 高く なって、着せ替えの ボタンも 0.15秒 ほど 30px 下へ 行く
  //     （ためした：それを 拾うと 丸が いっとき 小さく なる）→ 落ち着いて から 1回 だけ 決め直す
  var FD_MAX = 66, FD_MIN = 36, FD_PAD = 4, FAB_B = 4, holdUntil = 0, holdT = 0;
  var FD_ROW = [44, 80], ROW_MAX = 480, FD_SLOT = 0.8;                   // 第4.230版：横 1列の 丸の 大きさ（いちばん 小さい・大きい・1つ ぶんの 幅に たいする 割合）・列の 幅の 上限
  function fabFit(c) {
    var n = c.children.length; if (!n) return;
    var root = document.documentElement, vw = root.clientWidth || window.innerWidth, cr = c.getBoundingClientRect();
    if (!(cr.width > 0 && cr.height > 0)) return;                          // 列が 出て いない（かくして いる）：出た ときに 決める
    if (c.classList.contains('rw')) {                                      // 第4.230版：横 1列 ＝ 1つ ぶんの 幅の 80%（44〜80px：すきまを 小さく）。下は 下の タブの すぐ 上
      var rk = ['rw', n, vw, window.innerHeight, c._b1].join(':'); if (c._fit === rk) return;
      var slot = (Math.min(vw, ROW_MAX) - 8) / n, dr = Math.max(FD_ROW[0], Math.min(FD_ROW[1], Math.floor(slot * FD_SLOT)));
      fabZ(c); if (c._b1 && c.style.bottom !== c._b1) c.style.bottom = c._b1;
      c.style.setProperty('--fd', dr + 'px'); c._fit = rk; return;
    }
    var k = kiseB, kr = k ? k.getBoundingClientRect() : null;
    if (kr && kr.height > 0 && kr.bottom > 0) c._kb = Math.round(kr.bottom * 2) / 2;
    var top = (c._kb || 409 + 0.44 * (vw - 375)) + FD_PAD;                 // 列の 上は ここより 下
    var key = [n, vw, window.innerHeight, top, c._b1, c._b2, Math.round(cr.bottom * 2) / 2].join(':'); if (c._fit === key) return;
    var set = function (d, g2) {
      c.classList.toggle('g2', !!g2); fabZ(c); var b = g2 ? c._b2 : c._b1; if (b && c.style.bottom !== b) c.style.bottom = b;
      c.style.setProperty('--fd', d + 'px'); return c.getBoundingClientRect().top;
    };
    var d;
    var done = function () { c._fit = [n, vw, window.innerHeight, top, c._b1, c._b2, Math.round(c.getBoundingClientRect().bottom * 2) / 2].join(':'); };      // 決めた あとの 列の 下も 覚える（下の 余白が かわったら 決め直す）
    for (d = FD_MAX; d >= FD_MIN; d--) if (set(d, false) >= top) return done();
    for (d = FD_MAX; d >= FD_MIN; d--) if (set(d, true) >= top) return done();
    set(FD_MIN, true); done();
  }
  // 第4.222版（まさちゃん 2026/11/25 14:39「推し馬の通知のベルがトレーニングセンターの文字の下に隠れてるから前に出てくるようにして！」）：ボタンの 重なりの 順（z-index）。
  //   画面で 下の 段の ボタンほど 前 ＝ 丸の 右上の 札（数・🔔：丸より 上へ 少し 出る）は、すぐ 上の 段の ボタンの 名前の 札より 前に 出る。
  //   前は 入れた 順（推し馬 → トレーニングセンター → …）で 重なって いて、推し馬の 🔔 が 上の トレーニングセンターの 名前の 札（2行）の 下に 2〜3px かくれて いた。
  //   段：たて 1列は 並びの 順（order）の とおり・2列 × 2段（.g2：左の 列の 上 → 下、右の 列の 上 → 下）は 並びの 順の 2で 割った あまり
  //   （2列 × 2段 では 推し馬の 🔔 が 右上の カードバトルの 名前の 札にも 少し かかる ＝ 下の 段を 前に する）
  function fabZ(c) {
    var g2 = c.classList.contains('g2');
    [].slice.call(c.children).map(function (b, k) { return [+b.style.order || 0, k, b]; }).sort(function (x, y) { return x[0] - y[0] || x[1] - y[1]; })
      .forEach(function (x, i) { var z = String((g2 ? i % 2 : i) + 1); if (x[2].style.zIndex !== z) x[2].style.zIndex = z; });
  }
  // 大きさを 決め直して ほしい（場所が かわった・着せ替えの ボタンを 置いた）：ふだんは すぐ。fitHold の あいだは おわって から 1回
  function fitAsk() {
    var c = document.getElementById('fabCol'); if (!c) return;
    clearTimeout(holdT); holdT = 0;
    var left = holdUntil - Date.now();
    if (c._fit && left > 0) { holdT = setTimeout(fitAsk, left + 40); return; }
    fabFit(c); clear();
  }
  function fitHold(ms) { holdUntil = Math.max(holdUntil, Date.now() + ms); fitAsk(); }
  // 列の 下に かくれた ままに ならない ように：main の 下の 余白（列の 高さの ぶん）・保存の 帯の 右の あき
  //   余白は 列の いまの 場所（下の 帯の すぐ 上：いつも 同じ）で 数える
  var GAP = 6;
  function clear() {
    var c = document.getElementById('fabCol'); if (!c) return;
    var r = c.getBoundingClientRect(), root = document.documentElement, mn = document.querySelector('main'), vh = window.innerHeight, vw = root.clientWidth || window.innerWidth;
    var on = r.height > 0, rw = c.classList.contains('rw');
    var fz = on && !rw ? Math.max(0, Math.ceil(vw - 16 - 17 - r.left + GAP)) : 0;                // 保存の 帯（カードの 中：右はし＝画面の 右から 16＋17）を ちぢめる はば（第4.230版：横 1列は ちぢめない）
    if (root.style.getPropertyValue('--fabz') !== fz + 'px') root.style.setProperty('--fabz', fz + 'px');
    var fm = on && !rw && !c.classList.contains('g2') ? Math.max(12, Math.ceil(vw - r.left + GAP)) : 12;      // 判定の 帯（#minibar）の 右の あき：たてに 1列の とき、列の 手前（6px）で 終わる。2列 × 2段・横 1列は もとの まま
    if (root.style.getPropertyValue('--fabm') !== fm + 'px') root.style.setProperty('--fabm', fm + 'px');
    var mbar = document.getElementById('minibar'); if (mbar && mbar.classList.contains('fabn') !== (fm > 12)) mbar.classList.toggle('fabn', fm > 12);
    // 第4.230版：--fabt＝横 1列の 上の はし（画面の 下から）＋ 6px。判定の 帯・保存の 帯・お知らせは その 上（src.html の CSS：max(いつもの 場所, --fabt)）
    var ft = on && rw ? Math.ceil(vh - r.top + 6) + 'px' : '';
    if (root.style.getPropertyValue('--fabt') !== ft) { if (ft) root.style.setProperty('--fabt', ft); else root.style.removeProperty('--fabt'); try { window.dispatchEvent(new Event('tengel:fab')); } catch (e) { /* なし */ } }
    // main の 下の 余白：列の 高さ（横 1列は ＋ 判定の 帯の 高さ：帯が 出て いても 最後の 中身が 帯の 上まで 上がる）
    if (mn) { var pb = on ? Math.ceil(vh - r.top + GAP + 2 + (rw ? MINI_H + GAP : 0)) + 'px' : ''; if (mn.style.paddingBottom !== pb) mn.style.paddingBottom = pb; }      // 第4.168版：列は 動かない ので、いまの 場所を そのまま 測る
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
    var l = document.createElement('span'); l.className = 'fabl' + (o.name.length === 1 ? ' l1' : ''); l.textContent = o.name.join('\n'); b.appendChild(l);      // 第4.230版：1行の 名前（.l1）
    b.addEventListener('click', function () { if (!b.disabled) o.tap(); });
    var c = fabCol(); c.appendChild(b); fabZ(c); c._fit = ''; fabFit(c); clear();      // ボタンが ふえた：重なりの 順・大きさを 決め直す
    return b;
  }
  // 第4.221版：丸の 右上の 小さい 札を 出す・かえる・かくす（b＝ボタン・cls＝'fabc tk' など：はじめの 名前で 1つ・text＝字。null なら かくす）。
  //   字は 読み上げない（aria-hidden：ボタンの aria-label に 入れる）
  function fabMark(b, cls, text) {
    var i = b && b.querySelector('.fabi'); if (!i) return null;
    var m = i.querySelector('.' + cls.split(' ')[0]);
    if (text == null) { if (m && !m.hidden) m.hidden = true; return m; }
    if (!m) { m = document.createElement('span'); m.setAttribute('aria-hidden', 'true'); i.appendChild(m); }
    if (m.className !== cls) m.className = cls;
    if (m.textContent !== text) m.textContent = text;
    if (m.hidden) m.hidden = false;
    return m;
  }
  window.TengelFab = { add: fabAdd, mark: fabMark, busy: function () { return !!holdT; } };      // busy：大きさを 決め直すのを 待って いる（テストが 落ち着くのを 待つ ため）
  var fab = null, loading = null;
  // 第4.140版：alert() は アプリの 中で 出ない → 画面の お知らせ（下の 黒い 札）
  function note(m) { try { var t = document.getElementById('toast'); if (t) { t.textContent = m; t.hidden = false; clearTimeout(t._tc); t._tc = setTimeout(function () { t.hidden = true; }, 4200); } } catch (e) { /* なし */ } }
  function load() {
    if (window.TCApp) return Promise.resolve();
    if (!loading) loading = new Promise(function (ok, ng) { var s = document.createElement('script'); s.src = 'tc_bundle.js'; s.onload = function () { ok(); }; s.onerror = function () { loading = null; ng(new Error('load')); }; document.head.appendChild(s); });
    return loading;
  }
  // 第4.211版（抜け穴を ふさぐ）：トレーニングセンターの 時刻は 時計の 番人（TengelClock：tc_app.js の wallNow）。アプリを 開いた すぐ あと は 番人が まだ iPhone の 時計を
  //   たしかめて いない（その 間 だけ iPhone の 時計の まま）→ たしかめ おわって から 開く・ごほうびを わたす（ふつうは 一瞬。返事が ない ときも 1.5秒で 先へ）
  function clockReady() {
    try {
      var c = window.TengelClock; if (!c || !c.ready || typeof c.ready.then !== 'function') return Promise.resolve();
      return new Promise(function (ok) { var done = false, go = function () { if (!done) { done = true; ok(); } }; c.ready.then(go, go); setTimeout(go, 1500); });
    } catch (e) { return Promise.resolve(); }
  }
  function open(opt) {
    if (fab) fab.disabled = true;
    return clockReady().then(load).then(function () { return window.TCApp.open(opt); }).catch(function () { note('トレーニングセンターを 読みこめなかったよ。もう一度 押してね'); }).then(function () { if (fab) fab.disabled = false; });
  }
  window.TCOpen = open;
  // 第4.212版：馬カードバトルの ごほうびの お世話トークン（第4.176版の window.TCGift）は なくした（まさちゃん 2026/11/23 10:19：勝った ときの お世話トークンは 廃止）
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
      // 第4.230版：上の 帯の 中（.dk：上の 帯が 基準・大きさ --dk 倍）
      + 'header.top .top-in.dk3 #dbpill,header.top .top-in.dk3 #testTag{position:absolute;margin:0;z-index:1}'
      + 'header.top .top-in.dk3 #dbpill{box-sizing:border-box;display:flex;align-items:center;justify-content:center;padding:3px 6px;white-space:normal;text-align:center;line-height:1.35;overflow-wrap:anywhere}'
      + 'header.top .top-in.dk3 .tbrk:not(#tbrk2){display:none!important}'
      + '#planBtn.dk,#kiseBtn.dk{position:absolute;right:auto;z-index:2}'
      + '#planBtn.dk{width:calc(' + PLAN_W + 'px * var(--dk,1));height:calc(' + PLAN_H + 'px * var(--dk,1))}'
      + '#planBtn.dk .plt{width:calc(110px * var(--dk,1));height:calc(33px * var(--dk,1));margin:calc(7px * var(--dk,1)) calc(4px * var(--dk,1));border-width:calc(3px * var(--dk,1));font-size:calc(15px * var(--dk,1))}'
      + '#kiseBtn.dk{width:calc(' + KISE_BOX + 'px * var(--dk,1))}'
      + '#kiseBtn.dk img,#kiseBtn.dk .kft{width:calc(' + KISE_W + 'px * var(--dk,1));height:calc(' + KISE_H + 'px * var(--dk,1))}'
      + '#kiseBtn.dk .kisel{margin-top:calc(-' + KISE_LAP + 'px * var(--dk,1));padding:calc(2px * var(--dk,1)) calc(6px * var(--dk,1)) calc(2.5px * var(--dk,1));border-radius:calc(9px * var(--dk,1));font-size:max(7.5px,calc(9.5px * var(--dk,1)));line-height:max(9px,calc(11px * var(--dk,1)))}'
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
  // ---- 第4.230版：上の 帯の 3段目（まさちゃん 11/26 23:23「結果待ちの下に作戦会議、ミッションの下に着せ替えボードのアイコン入れて！
  //   テンゲルデータは、テンゲルⅢの文字の下に入れて！全体的に大きさなど違和感なく揃えて！」）----
  //   1段目＝ロゴ・ポイント・説明書（前の まま）／2段目＝テンゲルデータの 札（ロゴの 下：ロゴと 同じ 幅）・結果待ち・ミッション／
  //   3段目＝作戦会議（結果待ちの 下：まん中を そろえる）・壁紙&ボード着せ替え（ミッションの 下）。（テスト版の 印は テンゲルデータの 札の 下）
  //   大きさ k＝ min(1, 結果待ちの 幅 ÷ 110, ミッションの 幅 ÷ 110)（見える 札・着せ替えの ボタンの 幅 110 が 上の ボタンの 幅に おさまる）。
  //   作戦会議の 見える 札の まん中の 高さ＝着せ替えの カプセルの まん中。3段目の ぶん 上の 帯の 下の 余白（.top-in の padding-bottom）を 広げる
  //   使える とき：iPhone の 幅（〜599px）・結果待ちと ミッションが ロゴの 下の 同じ 段に ならんで いる。大きさが 0.6 より 小さく なる・使えない ときは 前の 場所（レース情報の カードの 右上）
  var DOCK_W = 110, DOCK_MIN = 0.6, DOCK_GAP = 8;
  function dockArea() {
    var hd = document.querySelector('header.top'), ti = hd && hd.querySelector('.top-in'), brand = ti && ti.querySelector('.brand');
    var rsv = document.getElementById('rsvBtn'), ms = document.getElementById('msBtn');
    if (!hd || !brand || !rsv || !ms || window.innerWidth > 599) return null;
    var br = brand.getBoundingClientRect(), rr = rsv.getBoundingClientRect(), mr = ms.getBoundingClientRect();
    if (!(br.height > 0 && rr.width > 0 && mr.width > 0) || rsv.parentNode !== ti || ms.parentNode !== ti) return null;
    if (Math.abs(rr.top - mr.top) > 4 || rr.top < br.bottom - 2) return null;                         // 結果待ちと ミッションが ロゴの 下の 同じ 段に ならんで いない
    if (rr.left - DOCK_GAP - br.left < 60) return null;                                                // テンゲルデータの 札の 幅が とれない（ロゴの 大きい 壁紙で 幅の せまい 画面：結果待ちが ロゴの 右はしより 左から はじまる ときも 60px あれば 置く）
    var k = Math.min(1, rr.width / DOCK_W, mr.width / DOCK_W);
    if (!(k >= DOCK_MIN)) return null;
    return { hd: hd, ti: ti, brand: br, rsv: rr, ms: mr, k: Math.floor(k * 100) / 100 };
  }
  function dockPut(a) {
    var b = planB, k = kiseB, hd = a.hd, ti = a.ti, s = a.k;
    if (!ti.classList.contains('dk3')) ti.classList.add('dk3');
    [b, k].forEach(function (e) { if (!e) return; if (e.parentNode !== hd) hd.appendChild(e); if (!e.classList.contains('dk')) e.classList.add('dk'); if (e.style.getPropertyValue('--dk') !== String(s)) e.style.setProperty('--dk', String(s)); if (e.style.right) e.style.right = ''; });
    var hr = hd.getBoundingClientRect(), r2t = Math.min(a.rsv.top, a.ms.top), r2b = Math.max(a.rsv.bottom, a.ms.bottom), y0 = r2b + DOCK_GAP;      // 2段目の 上・下・3段目の 上
    var kh = k ? k.getBoundingClientRect().height : 0, capH = KISE_H * s;
    var inkW = (PLAN_INK[2] - PLAN_INK[0]) * PLAN_W * s, inkH = (PLAN_INK[3] - PLAN_INK[1]) * PLAN_H * s, cy = y0 + (k ? capH / 2 : inkH / 2);
    // 作戦会議：結果待ちの 下（見える 札の まん中を 結果待ちの まん中に）・壁紙&ボード着せ替え：ミッションの 下（まん中を そろえる）
    px(b, 'left', (a.rsv.left + a.rsv.right) / 2 - inkW / 2 - PLAN_INK[0] * PLAN_W * s - hr.left); px(b, 'top', cy - inkH / 2 - PLAN_INK[1] * PLAN_H * s - hr.top);
    if (k) { px(k, 'left', (a.ms.left + a.ms.right) / 2 - KISE_BOX * s / 2 - hr.left); px(k, 'top', y0 - hr.top); }
    var bottom = Math.max(y0 + kh, cy + inkH / 2);
    // テンゲルデータの 札：ロゴの 下（左は ロゴと そろえる・幅は ロゴと 同じ＝結果待ちの 手前まで）・2段目の 高さの まん中（2行に なる ときは 2段目の 上から）
    var dp = document.getElementById('dbpill'), tt = document.getElementById('testTag'), w = Math.floor(a.rsv.left - DOCK_GAP - a.brand.left);
    if (dp && dp.parentNode === ti) {
      if (dp.style.width !== w + 'px') dp.style.width = w + 'px';
      var mh = Math.round(r2b - r2t) + 'px'; if (dp.style.minHeight !== mh) dp.style.minHeight = mh;      // 結果待ち・ミッションと 同じ 高さ
      px(dp, 'left', a.brand.left - hr.left);
      var dh = dp.getBoundingClientRect().height, dt = dh <= r2b - r2t + 2 ? (r2t + r2b) / 2 - dh / 2 : r2t;
      px(dp, 'top', dt - hr.top); bottom = Math.max(bottom, dt + dh);
      if (tt && tt.parentNode === ti) {                                      // テスト版の 印：テンゲルデータの 札の 下（ロゴと 左を そろえる）
        var th = tt.getBoundingClientRect().height, t0 = Math.max(dt + dh + 6, y0);
        px(tt, 'left', a.brand.left - hr.left); px(tt, 'top', t0 - hr.top); bottom = Math.max(bottom, t0 + th);
      }
    }
    // 3段目の ぶん 下の 余白を 広げる（中身の 下＝2段目の 下：3段目の ものは 帯の 中に 重ねて 置く）
    var cs = getComputedStyle(ti), tr = ti.getBoundingClientRect(), cb = tr.bottom - (parseFloat(cs.paddingBottom) || 0), pad = (ti._pb0 == null ? (ti._pb0 = parseFloat(cs.paddingBottom) || 0) : ti._pb0);
    var pb = Math.max(pad, Math.ceil(bottom - cb + pad)) + 'px'; if (ti.style.paddingBottom !== pb) ti.style.paddingBottom = pb;
    slotReset(planCard);
    fitAsk();
  }
  function dockOff() {
    [planB, kiseB].forEach(function (e) { if (!e || !e.classList.contains('dk')) return; e.classList.remove('dk'); e.style.removeProperty('--dk'); e.style.left = ''; document.body.appendChild(e); });
    var ti = document.querySelector('header.top .top-in'); if (!ti || !ti.classList.contains('dk3')) return;
    ti.classList.remove('dk3'); ti.style.paddingBottom = '';
    ['dbpill', 'testTag'].forEach(function (id) { var e = document.getElementById(id); if (e) { e.style.left = ''; e.style.top = ''; e.style.width = ''; e.style.minHeight = ''; } });
  }
  // データの 行の すきまの 部品・右の あきを 外す（上の 帯の 中に 置いた ときは ボタンが カードに かからない）
  function slotReset(card) {
    var sj = card && card.querySelector('#slotJudge'); if (!sj) return;
    var sp = sj.querySelector('.kisesp'); if (!sp && !sj.style.paddingRight) return;
    if (slotMo) slotMo.disconnect();
    if (sp) sp.remove(); sj.style.paddingRight = '';
    if (slotMo) slotMo.observe(sj, { childList: true, subtree: true, characterData: true });
  }
  var planRaf = 0;
  function planSoon() { if (!planRaf) planRaf = requestAnimationFrame(function () { planRaf = 0; planPlace(); }); }
  function planPlace() {
    var b = planB, card = planCard; if (!b || !card) return;
    var da = dockArea(); if (da) { planVis(true); dockPut(da); return; }                                    // 第4.230版：上の 帯の 中（どの タブでも 出す）
    dockOff();
    var cr = card.getBoundingClientRect(), on = cr.width > 0 && cr.height > 0;                               // 前の 場所（カードの 右上の かど）は 判定タブ だけ
    planVis(on); if (!on) return;
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
    fitAsk();                                                                                                // 第4.176版：右下の 丸い ボタンの 大きさ（この ボタンの すぐ 下から うめる）
  }
  // 出す・かくす（ボタンは body か 上の 帯の 下に ある ので、タブを かえたら 自分で 決める）。第4.230版：上の 帯の 中は どの タブでも・カードの 右上は 判定タブ だけ
  function planVis(on) { [planB, kiseB].forEach(function (e) { if (e && e.hidden !== !on) e.hidden = !on; }); }
  function dockSync() { planPlace(); }
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
    var b = document.createElement('button'); b.type = 'button'; b.id = 'planBtn'; b.setAttribute('aria-label', '作戦会議（押すと 開くよ）');
    var im = new Image(); im.alt = '';
    im.onerror = function () { var t = document.createElement('span'); t.className = 'plt'; t.textContent = '作戦会議'; im.replaceWith(t); };      // 絵が ない（CI など）：字の 札
    im.src = 'tc_icon_plan.webp'; b.appendChild(im);
    b.addEventListener('click', function () { if (!b.disabled) planOpen(null); });
    planCard = card; document.body.appendChild(b); planB = b;                                                // 第4.168版：body の 下（画面に 止める）
    // 第4.165版：「壁紙&ボード着せ替え」の ボタン（作戦会議の 札の すぐ 下：カプセルの 絵 ＋ 名前の 札）→ 設定タブの「着せ替え」へ
    var k = document.createElement('button'); k.type = 'button'; k.id = 'kiseBtn'; k.setAttribute('aria-label', KISE_NAME + '（押すと 設定の 着せ替え・結果ボードカスタムを 開くよ）');
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
    // 第4.230版：上の 帯の 中の もの（ポイント・説明書・結果待ち・ミッション・データの 札・お知らせ）が ふえた・かわった・大きさが かわった → あいて いる 所を 測り直す
    try {
      var ti = document.querySelector('header.top .top-in');
      if (ti) {
        var ro2 = window.ResizeObserver ? new ResizeObserver(planSoon) : null, seen2 = [];
        var watch2 = function () { if (ro2) [].forEach.call(ti.children, function (e) { if (seen2.indexOf(e) < 0) { seen2.push(e); ro2.observe(e); } }); };
        watch2();
        if (window.MutationObserver) new MutationObserver(function () { watch2(); planSoon(); }).observe(ti, { childList: true, attributes: true, attributeFilter: ['class', 'style'] });
      }
    } catch (e) { /* なし */ }
    try { var sj = card.querySelector('#slotJudge'); if (sj && window.MutationObserver) { slotMo = new MutationObserver(planPlace); slotMo.observe(sj, { childList: true, subtree: true, characterData: true }); } } catch (e) { /* なし */ }      // データの 行を 作り直した・名前や 数が かわった
    setTimeout(kiseJump, 0); setTimeout(kiseJump, 1500);
    try { if (document.fonts && document.fonts.ready) document.fonts.ready.then(planPlace); } catch (e) { /* なし */ }
    try { if (document.fonts && document.fonts.addEventListener) document.fonts.addEventListener('loadingdone', planPlace); } catch (e) { /* なし */ }      // 壁紙の 字が あとから 読めた（チップの 幅が かわる）
    try { if (window.MutationObserver) new MutationObserver(function () { fitHold(1500); planPlace(); setTimeout(planPlace, 300); setTimeout(planPlace, 1200); }).observe(document.documentElement, { attributes: true, attributeFilter: ['data-ks'] }); } catch (e) { /* なし */ }      // 壁紙を かえた
  }
  // ---------- 第4.221版（まさちゃん 2026/11/25 12:07「トレーニングセンターのアイコンにお世話トークンの数が分かるように表示することって可能？」）----------
  //   トレーニングセンターの 丸の 右上に 今の お世話トークンの 数。数え方は tc_app.js の accrue と 同じ（5分ごとに 5個・25個 まで・時刻は 時計の 番人・
  //   もどらない 時計 seen より 前に しない）。まだ 開いた ことが ない ときは はじめの 5個（開いた ときから 数えはじめる）。
  //   書き直す とき：数が かわる 時刻（次の 5分：10分より 先は 10分ごとに 見直す）・閉じた（'tengel:tc'）・時計を たしかめた（'tengel:clock'）・アプリに もどった
  var TK_EVERY = 5 * 60000, TK_STEP = 5, TK_MAX = 25, TK_FIRST = 5, WAIT_MAX = 600000;
  function clockNow() { try { var c = window.TengelClock; if (c && typeof c.now === 'function') { var t = +c.now(); if (isFinite(t) && t > 0) return t; } } catch (e) { /* なし */ } return Date.now(); }
  function tokens() {
    var s = live() || jget(TK); if (!s || s.v !== 1) return { n: TK_FIRST, wait: 0 };      // 形の ちがう 保存は tc_app.js も 使わない（はじめから）
    var n = Math.max(0, Math.min(TK_MAX, Math.round(+s.stock || 0))), at = +s.stockAt;
    if (n >= TK_MAX || !isFinite(at)) return { n: n, wait: 0 };
    var t = Math.max(clockNow(), +s.seen || 0), k = Math.floor((t - at) / TK_EVERY);
    if (k > 0) n = Math.min(TK_MAX, n + k * TK_STEP);
    return { n: n, wait: n >= TK_MAX ? 0 : at + (Math.max(0, k) + 1) * TK_EVERY - t };
  }
  var tkT = 0;
  function tcPaint() {
    clearTimeout(tkT); tkT = 0; if (!fab) return;
    var r = tokens();
    fabMark(fab, 'fabc tk' + (r.n ? '' : ' z'), String(r.n));
    var a = 'トレーニングセンター（お世話トークン ' + r.n + '個・押すと 開くよ）'; if (fab.getAttribute('aria-label') !== a) fab.setAttribute('aria-label', a);
    if (r.wait > 0) tkT = setTimeout(tcPaint, Math.min(r.wait + 400, WAIT_MAX));
  }
  // ---------- 第4.221版（12:07「時間がやりたいレースの通知時間が来たら、推し馬のアイコンのところにも、通知が来てることが分かるようにして！」）----------
  //   推し馬の 丸の 右上に 🔔：作戦会議の 通知が オン（tengel.plan の on）で、予約した レースの 選んだ お知らせの 時刻（発走の ○分前）が 来て から 発走 まで。
  //   作戦会議を 開いた・閉じた 時刻（tengel.planseen：tc_plan.js）より あとに 来た お知らせ だけ ＝ 開いて 見たら 消える（次の お知らせの 時刻で また 出る）。発走を すぎたら 消える。
  //   🔔 が 出て いる ときに 押すと 作戦会議を 上（予約した レース）から 開く（ふだんは 推し馬の 欄）
  function planAlert() {
    var P = jget(PK), now = Date.now(), seen = +jget('tengel.planseen') || 0, on = false, next = 0;
    if (P && P.on && Array.isArray(P.races)) P.races.forEach(function (r) {
      var s = planStart(r); if (!s || s <= now) return;
      next = next ? Math.min(next, s) : s;                                   // 発走で 消す
      (r.notify || []).forEach(function (m) {
        var at = s - (+m) * 60000; if (!isFinite(at)) return;
        if (at <= now) { if (at > seen) on = true; } else next = Math.min(next, at);
      });
    });
    return { on: on, wait: next ? next - now : 0 };
  }
  var olT = 0;
  function oshiPaint() {
    clearTimeout(olT); olT = 0; if (!oshiB) return;
    var r = planAlert();
    fabMark(oshiB, 'fabb', r.on ? '🔔' : null);
    var a = r.on ? '推し馬（🔔 まもなく 発走の レースが あるよ。押すと 作戦会議の レースを 開くよ）' : '推し馬（押すと 作戦会議の 推し馬の 欄を 開くよ）';
    if (oshiB.getAttribute('aria-label') !== a) oshiB.setAttribute('aria-label', a);
    if (r.wait > 0) olT = setTimeout(oshiPaint, Math.min(r.wait + 400, WAIT_MAX));
  }
  function marks() { tcPaint(); oshiPaint(); }
  function boot() {
    if (document.getElementById('tcFab')) return;
    // 第4.165版：推し馬 → 作戦会議の「推し馬」の 欄を すぐ 開く。順（order）：第4.176版から トレーニングセンター 0 → 推し馬 1 → カードバトル 2 → 思い出フィギュア 3
    //   第4.221版：🔔 が 出て いる ときは 作戦会議の 上（予約した レース）から 開く
    oshiB = fabAdd({ id: 'oshiFab', order: 1, name: ['推し馬'], aria: '推し馬（押すと 作戦会議の 推し馬の 欄を 開くよ）', img: 'tc_icon_oshi.webp', fb: ['推し馬', '#BFE6C4', '#E2B33C', '#5B3412'], tap: function () { planOpen(planAlert().on ? null : { oshi: true }); } });
    fab = fabAdd({ id: 'tcFab', order: 0, name: ['トレーニング', 'センター'], aria: 'トレーニングセンター（押すと 開くよ）', img: 'tc_icon_tc.webp', fb: ['トレセン', '#1F5A2E', '#E2B33C', '#FFF3C4'], tap: function () { open(); } });
    planBoot();
    marks();
    document.addEventListener('tengel:tc', tcPaint);
    document.addEventListener('tengel:clock', tcPaint);
    document.addEventListener('tengel:plan', oshiPaint);
    document.addEventListener('visibilitychange', function () { if (!document.hidden) marks(); });
    window.addEventListener('pageshow', marks);
  }
  // 通知を 押した（作戦会議）→ トレーニングセンターの 作戦会議を 開く
  document.addEventListener('tengel:native', function (e) {
    var d = e.detail || {}; if (d.name === 'notify' && d.payload && /^plan-/.test(String(d.payload.id || ''))) open({ plan: true });
  });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
