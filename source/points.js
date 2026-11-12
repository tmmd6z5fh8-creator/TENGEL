// ===== ポイント（App Store版）：台帳の計算だけ。画面・保存はしない（points_ui.js）。node でテストできる（test_points.js） =====
// 台帳＝1件ずつの「できごと」（4.3）。残高はできごとから毎回計算する。
//   kind：purchase（パック）・sub（サブスク）・gift（初回）・mission・spend（読み込みなど）・unlock（解放）・refund（返金）
//   bucket：paid_pack（買ったP）・paid_sub（サブスクのP・届いた日から30日）・free（もらったP）
//   使う順（4.2）：サブスクのP（期限が近い順）→ パック → 無償。足りないときは使えない（マイナスにしない）
//   n：書いた 順の 番号（第4.139版）。残高は この 順に たどる（時刻 at の 順では ない：下の「台帳の ならび」）
(function (root) {
  'use strict';
  var DAY = 86400000;
  var PRODUCTS = {
    'jp.tengel.app.points500': { kind: 'pack', points: 500, bonus: 0, name: '500ポイント', yen: 176 },
    'jp.tengel.app.points1000': { kind: 'pack', points: 1000, bonus: 0, name: '1,000ポイント', yen: 352 },
    'jp.tengel.app.points2000': { kind: 'pack', points: 2000, bonus: 0, name: '2,000ポイント', yen: 704 },
    'jp.tengel.app.points4000': { kind: 'pack', points: 4000, bonus: 0, name: '4,000ポイント', yen: 1408 },
    'jp.tengel.app.sub2000': { kind: 'sub', points: 2000, bonus: 0, name: '月2,000Pプラン', yen: 638 },
    'jp.tengel.app.sub4400': { kind: 'sub', points: 4400, bonus: 400, name: '月4,400Pプラン', yen: 1276 },
    'jp.tengel.app.sub9200': { kind: 'sub', points: 9200, bonus: 1000, name: '月9,200Pプラン', yen: 1914 },
    // 第4.91版：結果ボードカスタム（買い切り・非消耗型）。1回 買えば ずっと（機種変更・入れ直しは「購入を復元」）
    //   第4.114版（まさちゃん 2026/11/01「拡張パックの値段変える！ 壁紙1500円 結果ボードカスタム1500円 お得パック 壁紙&結果ボードカスタム 2200円」）：1,500円に
    'jp.tengel.app.boardcustom': { kind: 'unlock', what: 'board', points: 0, bonus: 0, name: '結果ボードカスタム', yen: 1500 },
    // 第4.92版：壁紙パック（買い切り・非消耗型）。新しい 壁紙 10枚（第4.147版で 七夕を 外した：11 → 10枚）。買った あとに 読み込んだ レース 5つごとに 1枚ずつ 解放（ポイントでは 買えない）
    'jp.tengel.app.wallpack1': { kind: 'unlock', what: 'wallpack', points: 0, bonus: 0, name: '壁紙パック', yen: 1500 },
    // 第4.114版：お得パック（買い切り・非消耗型）。壁紙パックと 結果ボードカスタムの セット 2,200円（単品は 1,500円ずつ＝3,000円）。持って いれば 両方を 持って いる 扱い（owned）
    'jp.tengel.app.bundle1': { kind: 'unlock', what: 'bundle', points: 0, bonus: 0, name: 'お得パック', yen: 2200 }
  };
  var BUNDLE = { product: 'jp.tengel.app.bundle1', parts: ['wallpack', 'board'] };
  var PACKS = ['jp.tengel.app.points500', 'jp.tengel.app.points1000', 'jp.tengel.app.points2000', 'jp.tengel.app.points4000'];
  var SUBS = ['jp.tengel.app.sub2000', 'jp.tengel.app.sub4400', 'jp.tengel.app.sub9200'];
  var COST = { gift: 1500, read: 200, w5: 200, type: 500, slot: 15000 };
  // 第4.139版（まさちゃん 2026/11/10 11:46「ポイントの上限は、99999までにして！」）：もてる ポイント（合計）の 上限。
  //   こえる 買い物（パック・サブスクを はじめる）は 買う 前に 止める・ミッションは 入る ように なるまで 受け取りを 待つ（points_ui.js）。
  //   上限でも 届く もの（サブスクの 更新・あとから 届いた 取引・トレーニングセンターの 当たり）の こえた ぶんは 消さずに あずかる（下の「あずかりポイント」）
  var CAP = 99999;
  // 第4.141版（まさちゃん 2026/11/10 15:52「壁紙チケット or 8000pにして！」→ 16:08「じゃあ7000pにして！」＝いちばん 高い 壁紙と 同じ 7,000P）：トレーニングセンターの チケット 1枚は、壁紙の 解放に 使うか、この ポイント（獲得ポイント）に かえるかを 選べる
  var TICKET_POINTS = 7000;
  function room(total) { return Math.max(0, CAP - Math.max(0, Math.round(+total || 0))); }
  var SUB_DAYS = 30;
  // 記録のミッション（8.2）：記録したレースの数 → もらえるP。300のあとは100レースごとに2,000P
  var MISSIONS = [[8, 500], [15, 1000], [25, 1000], [40, 1200], [60, 1200], [85, 1400], [100, 1400], [130, 1600], [160, 1600], [200, 1800], [240, 1800], [300, 2000]];
  // 壁紙のミッション（8.3・第4弾）：ポイントで解放した壁紙の枚数 → 帯の壁紙（シルバー帯 8枚・ゴールド帯 16枚・マスター帯 25枚）。受け取ると 0P の mission と unlock-theme:<帯> を足す
  //   第4.147版（まさちゃん 2026/11/10 22:12「壁紙 …これら全部消して！ミッションも減った分調整して！」）：ポイントで 解放する 壁紙が 26 → 17枚に へった ので 8・16・25 → 5・10・16枚
  //     （今までと 同じく ポイントの 壁紙 だけで マスター帯に 届く）。id は 枚数 では なく 帯の 名前（mission-wall-silver…）に した：前の mission-wall-16（ゴールド帯）と 新しい 16枚（マスター帯）が
  //     ぶつからない ように。受け取った か どうかは 帯の 壁紙を 持って いるか（unlock-theme:<帯>）で 見る ＝ 前の 版で 受け取った 人は そのまま 受け取りずみ
  //   第4.160版（まさちゃん 2026/11/12 14:31「壁紙のネオン消して！」・14:32「ミッションも減った分調整して！」）：ポイントで 解放する 壁紙が 17 → 16枚に へった ので マスター帯 16 → 15枚
  //     （シルバー帯 5枚・ゴールド帯 10枚は そのまま。今までと 同じく ポイントの 壁紙 だけで マスター帯に 届く）。id は 帯の 名前 なので 前に 受け取った 人は そのまま 受け取りずみ
  var WALL_MISSIONS = [[5, 'silver', 'シルバー帯の壁紙'], [10, 'golden', 'ゴールド帯の壁紙'], [15, 'tengel', 'マスター帯の壁紙']];
  // 第4.147版：アプリから 外した 壁紙 10枚（kisekae/build_kisekae.py の REMOVED と 同じ）。解放した 数（wallCount）に 数えない。
  //   もう 解放して いた 人には、使った ポイント（チケットで 解放して いたら チケット）を 返す（goneUnlocks → points_ui.js の goneBack：1回 だけ＝back-theme:<名前>）。七夕は 壁紙パックの 1枚（台帳に できごとは ない）
  //   第4.160版：ネオン（neon・3,000P）も 外した ＝ 11枚
  var GONE_THEMES = ['sakura', 'sea', 'autumn', 'snow', 'newyear', 'xmas', 'halloween', 'valentine', 'whiteday', 'tanabata', 'neon'];
  var GONE_NAMES = { sakura: '桜', sea: '海', autumn: '紅葉', snow: '雪', newyear: 'お正月', xmas: 'クリスマス', halloween: 'ハロウィン', valentine: 'バレンタイン', whiteday: 'ホワイトデー', tanabata: '七夕', neon: 'ネオン' };
  // 第4.114版（まさちゃん 2026/11/01）：結果ボードカスタムの 解放の 数（解放した 番号の 数＝画面の「解放 n/15」・じゅんび中も 数える）→ もらえるP
  //   第4.120版（まさちゃん 2026/11/04 02:02「結果ボードカスタムは、15個にする！ミッションも変更して！」）：さいごの 16こ → 15こ（ポイントは 同じ 1,600P）。
  //   前の 版で「16こ解放」を 受け取った 人は「15こ解放」も 受け取った ことに する（boardMissions）
  var BOARD_MISSIONS = [[3, 500], [6, 800], [9, 1100], [12, 1400], [15, 1600]];
  // 第4.114版（まさちゃん 2026/11/01）：壁紙の 解放の 枚数（ポイントで 解放＋壁紙パックで 解放＋帯の 3枚：いつもの は 数えない）→ もらえるP。
  //   いま 解放できる 壁紙は WALL_TOTAL＝29枚（ポイント 16＋壁紙パック 10＋帯 3。第4.147版〜第4.159版は 30枚）。
  //   第4.139版（まさちゃん 2026/11/10 11:58「ならミッションを40枚までにして！」）：届かない「45枚 3,500P」を やめて 40枚まで（10こ）
  //   第4.147版（壁紙を 10枚 外した：40 → 30枚）：届かなく なった「35枚 3,500P」「40枚 3,500P」を やめて 30枚まで（8こ）。3〜30枚の 8こは そのまま。前に 受け取った ぶんは 台帳に 残る
  //   第4.160版（ネオンを 外した：30 → 29枚＝ポイント 16＋壁紙パック 10＋帯 3）：さいごの「30枚 2,500P」→「29枚 2,500P」（ぜんぶ 集めた ときの ミッション・ポイントは 同じ）。
  //     前の 版で「30枚解放」を 受け取った 人は「29枚解放」も 受け取った ことに する（wallpMissions：2回 もらえない）
  var WALLP_MISSIONS = [[3, 800], [6, 1200], [9, 1500], [12, 1800], [15, 2100], [20, 2500], [25, 2500], [29, 2500]];
  var WALL_TOTAL = 29;
  var FREE_TYPES = ['単勝', '馬単', '3連単'];
  var UNLOCK_TYPES = ['複勝', '枠複', '枠単', '馬連', 'ワイド', '3連複'];
  var ALL_TYPES = ['単勝', '複勝', '枠複', '枠単', '馬連', '馬単', 'ワイド', '3連複', '3連単'];
  var BUCKETS = ['paid_sub', 'paid_pack', 'free'];
  // 結果ボードカスタム（第4.91版・まさちゃんの 指定）：買い切り 2,200円（第4.114版から 1,500円）。買った あとに 読み込んだ レースの 数で、番号の 順に 1つずつ 解放する。読み直し（0P）・5連の 予想は 数えない
  //   第4.113版（まさちゃん 2026/11/01「結果ボードカスタム、最後のボードを持つ馬以外一度全部消して！全部で16個(ボードを持つ馬を含む)にする！」）：
  //     16こ・6レースごとに 1つ（全部で 96レース）。前の 1〜21（ボードを一周〜出世馬）は 消した。1〜15 は じゅんび中（まさちゃんの デザインが とどいたら 入れる）・16 は ボードを持つ馬
  //   第4.120版（まさちゃん 2026/11/04 02:01「ハズレ⑥消して！」・02:02「結果ボードカスタムは、15個にする！ミッションも変更して！」）：
  //     15こ（的中 9・ハズレ 5・ボードを持つ馬）・6レースごと（全部で 90レース）。1〜14 は じゅんび中・15 は ボードを持つ馬
  //   第4.113版（まさちゃん 01:24「結果ボードのカスタムには2種類カスタムつけられるようにして！①的中演出 ②ハズレ演出」）：的中の とき・ハズレの とき で べつべつに 1つずつ 選ぶ
  //     （points_ui.js の board.selHit・board.selMiss。解放の 数は 1つ＝買うのも 1回）
  var BOARD = { product: 'jp.tengel.app.boardcustom', steps: [[15, 6]] };
  var BOARD_NEED = (function () { var out = [], n = 0; BOARD.steps.forEach(function (st) { for (var i = 0; i < st[0]; i++) { n += st[1]; out.push(n); } }); return out; })();
  // 15こ（番号の 順＝解放の 順）。null＝じゅんび中（設定に「じゅんび中」の タイル・選べない）。
  //   飾りを 入れる ときは、その 番号の null を [id, 名前, せつめい, when] に かえて、bcx.js に B.<id>（部品を 作る 所）を 足す（README「結果ボードカスタムに 飾りを 入れる」）
  //   when：all＝的中にも ハズレにも 使える・hit＝的中の とき だけ・big＝的中の うち デカ的中から 上 だけ・miss＝ハズレの とき だけ
  //   第4.121版（まさちゃんの デザイン 14こ・名前も まさちゃんの もの）：1〜9＝的中①〜⑨・10〜14＝ハズレ①〜⑤ の 絵の ボード（bcx.js の 絵の ボード・kisekae/bcp/bcp_app.py の ITEMS）。
  //     的中は 連続的中の 数（1〜4連勝・出世馬は 1・2・3・4・8・16・24連勝）、ハズレは 続けて ハズレた 数（1〜4回目）で 絵が かわる。
  //     id は 前の 版の 飾り（第4.113版で 消した 1〜21）と かぶらない 名前（前の 選択が つかない ように）
  var BOARD_ITEMS = [
    /* 1 */ ['ring', '結果ボードを廻る', '1〜4連勝で 絵が かわる', 'hit'],
    /* 2 */ ['toast', '馬達の祝杯', '1〜4連勝で 絵が かわる', 'hit'],
    /* 3 */ ['race', '馬レース結果ボード', '1〜4連勝で 絵が かわる', 'hit'],
    /* 4 */ ['snap', '自撮り結果ボード', '1〜4連勝で 絵が かわる', 'hit'],
    /* 5 */ ['seal', 'スタンプ結果ボード', '1〜4連勝で 絵が かわる', 'hit'],
    /* 6 */ ['cup', 'トロフィー結果ボード', '1〜4連勝で 絵が かわる', 'hit'],
    /* 7 */ ['hoist', '馬が運ぶ結果ボード', '1〜4連勝で 絵が かわる', 'hit'],
    /* 8 */ ['bloom', '花束結果ボード', '1〜4連勝で 絵が かわる', 'hit'],
    /* 9 */ ['climb', '出世馬結果ボード', '1・2・3・4・8・16・24連勝で 出世する', 'hit'],
    /* 10 */ ['rain', '二人でしょんぼり', '続けて ハズレた 数（1〜4回目）で 絵が かわる', 'miss'],
    /* 11 */ ['next', '次…！', '続けて ハズレた 数（1〜4回目）で 絵が かわる', 'miss'],
    /* 12 */ ['cover', '隠蔽作戦', '続けて ハズレた 数（1〜4回目）で 絵が かわる', 'miss'],
    /* 13 */ ['wait', 'ボード結果待ち', '続けて ハズレた 数（1〜4回目）で 絵が かわる', 'miss'],
    /* 14 */ ['pen', '書き換え参戦', '続けて ハズレた 数（1〜4回目）で 絵が かわる', 'miss'],
    /* 15 */ ['carry', 'ボードを持つ馬', '馬がうしろからボードを持っている', 'all']
  ].map(function (r, i) {
    return r ? { no: i + 1, id: r[0], name: r[1], desc: r[2], when: r[3], need: BOARD_NEED[i], ready: true }
      : { no: i + 1, id: 'prep' + (i + 1), name: 'じゅんび中', desc: 'あたらしい 飾りを じゅんび して いるよ', when: 'all', need: BOARD_NEED[i], ready: false };
  });
  // その 飾りを 的中の とき（kind＝'hit'）・ハズレの とき（'miss'）に 使えるか（じゅんび中は 使えない）
  function boardFits(it, kind) { if (!it || !it.ready) return false; return kind === 'miss' ? (it.when === 'all' || it.when === 'miss') : it.when !== 'miss'; }
  // 第4.113版：的中の とき・ハズレの とき の 2つの 選択 sel＝{ hit, miss }（'none'＝なし・''＝まだ 選んで いない＝つぎに 解放した 飾りを そのまま 使う）
  function boardSlot(kind) { return kind === 'miss' ? 'miss' : 'hit'; }
  // 選べる もの か（なし・いま ある 飾り）。前の 版の 飾り（第4.113版で 消した 1〜21）や じゅんび中は 選べない
  function boardKnown(id) { return id === 'none' || BOARD_ITEMS.some(function (x) { return x.ready && x.id === id; }); }
  // 台帳の board → sel。前の 版の 1つの 選択（board.sel）は 的中にも ハズレにも ついて いた ので 両方へ（知らない もの は ''）
  function boardSel(bd) {
    bd = bd || {};
    var old = typeof bd.sel === 'string' ? bd.sel : '', h = typeof bd.selHit === 'string' ? bd.selHit : old, m = typeof bd.selMiss === 'string' ? bd.selMiss : old;
    return { hit: boardKnown(h) ? h : '', miss: boardKnown(m) ? m : '' };
  }
  // いま ボードに つける もの（kind＝結果の 種類：'miss'＝ハズレの 所・ほか＝的中・デカ的中・ど的中…＝的中の 所）。解放ずみで その 結果に 使える ものだけ。なし なら ''
  function boardActive(sel, reads, kind) {
    var k = boardSlot(kind), id = sel ? sel[k] : '';
    if (!id || id === 'none') return '';
    var n = boardUnlocked(reads), it = BOARD_ITEMS.filter(function (x) { return x.id === id; })[0];
    return it && it.no <= n && boardFits(it, k) ? it.id : '';
  }
  // n0 → n1 こ 解放した：その 間の 飾り（じゅんび中は のぞく）を、まだ 選んで いない 所（sel の hit・miss）に つける（sel を かえる）。解放した 飾りを 返す
  function boardOpen(sel, n0, n1) {
    var got = [];
    for (var i = Math.max(0, n0); i < n1 && i < BOARD_ITEMS.length; i++) {
      var it = BOARD_ITEMS[i]; if (!it.ready) continue;
      got.push(it);
      ['hit', 'miss'].forEach(function (k) { if (!boardKnown(sel[k]) && boardFits(it, k)) sel[k] = it.id; });
    }
    return got;
  }

  function iso(d) { return (d instanceof Date ? d : new Date(d || Date.now())).toISOString(); }
  function tms(s) { var t = Date.parse(s); return isFinite(t) ? t : 0; }
  function addDays(isoStr, n) { return new Date(tms(isoStr) + n * DAY).toISOString(); }
  // ---- 台帳の ならび（第4.139版：抜け穴を ふさぐ）----
  //   balance は できごとを 1つずつ 順に たどる（使った ぶんは、その ときに ある ぶんから 引く。足りなければ 引けない）。
  //   前は 時刻（at）の 順だった → 「使った」が「届いた」より 前に ならぶと、その ぶんが 引かれなかった：
  //     ・その日 1回 使った あとに ポイントを 増やすと（パックを 買う・ミッションを 受け取る…）、その日の のこりは 使っても へらなかった
  //       （1日ぶんの「使った」を 1件に まとめて いて、時刻は 1回めの まま だった ＝ あとから 届いた ぶんより 前に ならぶ）
  //     ・端末の 時計を 進めて ミッションを 受け取り、時計を もどすと、その ポイントは 使っても へらなかった
  //   → 書いた 順の 番号 n を つけて、その 順に たどる（端末の 時計に よらない）。「使った」を まとめる のも、いちばん あとに 書いた 1件が その「使った」の とき だけ（spend）。
  //   番号の ない できごと（前の 版の 台帳）は 前と 同じ 時刻の 順（stampAll が その 順に 番号を ふる ＝ 前の 版までの 残高は かわらない）
  function byTime(a, b) { return tms(a.at) - tms(b.at) || String(a.id).localeCompare(String(b.id)); }
  function sorted(events) {
    return (events || []).filter(Boolean).slice().sort(function (a, b) {
      var x = +a.n || 0, y = +b.n || 0;
      if (x && y) return x - y || byTime(a, b);
      if (x || y) return x ? -1 : 1;                      // 番号つきが 先（番号なし＝足した ばかりで まだ 番号を ふって いない）
      return byTime(a, b);
    });
  }
  function seqMax(events) { var m = 0; (events || []).forEach(function (e) { if (e && +e.n > m) m = +e.n; }); return m; }
  // 番号の ない できごとに、ならんで いる 順（＝足した 順）に 番号を ふる。返り値は 同じ 一覧
  function stamp(events) { var m = seqMax(events); (events || []).forEach(function (e) { if (e && !(+e.n > 0)) e.n = ++m; }); return events; }
  // 前の 版の 台帳：番号の ない できごとに、時刻の 順（前の 版が たどって いた 順）で 番号を ふる
  function stampAll(events) {
    var m = seqMax(events);
    (events || []).filter(function (e) { return e && !(+e.n > 0); }).sort(byTime).forEach(function (e) { e.n = ++m; });
    return events;
  }
  function useOf(e) { var u = e && e.use || {}; return { paid_sub: +u.paid_sub || 0, paid_pack: +u.paid_pack || 0, free: +u.free || 0 }; }

  // ---- 残高 ----
  // 返り値：{ total, paid_sub, paid_pack, free, lots:[{id, product, at, expires, points, remain, expired}], lost（期限切れで消えたP）, nextExpire（いちばん近い期限）, paidIn（買ったPの合計）, freeIn, used }
  function balance(events, now) {
    var t = now ? tms(iso(now)) : Date.now();
    var lots = [], pack = 0, free = 0, used = { paid_sub: 0, paid_pack: 0, free: 0 }, paidIn = 0, freeIn = 0;
    sorted(events).forEach(function (e) {
      var amt = +e.amount || 0;
      if (e.kind === 'sub' && amt > 0) {
        lots.push({ id: e.id, tx: e.tx || '', product: e.product || '', at: e.at, expires: e.expires || addDays(e.at, SUB_DAYS), points: amt, remain: amt });
        paidIn += amt;
      } else if (e.kind === 'purchase' && amt > 0) { pack += amt; paidIn += amt; }
      else if ((e.kind === 'gift' || e.kind === 'mission') && amt > 0) { free += amt; freeIn += amt; }
      else if (e.kind === 'refund') {
        var n = Math.abs(amt);
        if (e.bucket === 'paid_sub') { lots.forEach(function (L) { if (e.tx && L.tx === e.tx) L.remain = 0; }); }      // その 取引の lot ぜんぶ（第4.139版：あずかりから 補充した lot も 同じ tx）
        else if (e.bucket === 'free') free = Math.max(0, free - n);
        else pack = Math.max(0, pack - n);
      }
      if (e.use) {
        var u = useOf(e), at = tms(e.at);
        // サブスクのP：そのときに期限が切れていない lot から、期限が近い順に引く
        var need = u.paid_sub;
        lots.filter(function (L) { return L.remain > 0 && tms(L.expires) > at; }).sort(function (a, b) { return tms(a.expires) - tms(b.expires); }).forEach(function (L) {
          if (need <= 0) return; var k = Math.min(L.remain, need); L.remain -= k; need -= k;
        });
        used.paid_sub += u.paid_sub - need;
        pack = Math.max(0, pack - u.paid_pack); used.paid_pack += u.paid_pack;
        free = Math.max(0, free - u.free); used.free += u.free;
      }
    });
    var sub = 0, lost = 0, next = null;
    lots.forEach(function (L) {
      L.expired = tms(L.expires) <= t;
      if (L.expired) lost += L.remain;
      else { sub += L.remain; if (L.remain > 0 && (!next || tms(L.expires) < tms(next))) next = L.expires; }
    });
    return { total: sub + pack + free, paid_sub: sub, paid_pack: pack, free: free, lots: lots, lost: lost, nextExpire: next, paidIn: paidIn, freeIn: freeIn, used: used };
  }

  // ---- 使う（どの枠からいくつ引くか）----
  function plan(events, amount, now) {
    amount = Math.max(0, Math.round(+amount || 0));
    var B = balance(events, now), use = { paid_sub: 0, paid_pack: 0, free: 0 }, need = amount;
    var s = Math.min(B.paid_sub, need); use.paid_sub = s; need -= s;
    var p = Math.min(B.paid_pack, need); use.paid_pack = p; need -= p;
    var f = Math.min(B.free, need); use.free = f; need -= f;
    return { ok: need === 0, use: use, short: need, total: B.total, balance: B };
  }

  // ---- できごとを作る ----
  var mk = function (id, kind, bucket, amount, at, extra) { return Object.assign({ id: id, kind: kind, bucket: bucket, amount: amount, at: at || iso() }, extra || {}); };
  // 取引（StoreKit）→ できごと。もう台帳にあれば null（同じ取引は2回足さない）
  function txEvent(events, tx, now) {
    if (!tx || !tx.id || !tx.product) return null;
    var P = PRODUCTS[tx.product]; if (!P) return null;
    var id = 'tx-' + tx.id;
    if ((events || []).some(function (e) { return e && e.id === id; })) return null;
    var at = tx.date && tms(tx.date) ? new Date(tms(tx.date)).toISOString() : iso(now);
    if (P.kind === 'sub') return mk(id, 'sub', 'paid_sub', P.points, at, { bonus: P.bonus, product: tx.product, tx: String(tx.id), otx: String(tx.originalId || ''), expires: addDays(at, SUB_DAYS) });
    if (P.kind === 'unlock') return mk(id, 'unlock', '', 0, at, { what: P.what, product: tx.product, tx: String(tx.id), otx: String(tx.originalId || ''), use: { paid_sub: 0, paid_pack: 0, free: 0 } });
    return mk(id, 'purchase', 'paid_pack', P.points, at, { product: tx.product, tx: String(tx.id), otx: String(tx.originalId || '') });
  }
  // 返金（取引に revocationDate がついた）→ できごと。元の取引が台帳になければ null
  function refundEvent(events, tx, now) {
    if (!tx || !tx.id) return null;
    var id = 'refund-' + tx.id, src = 'tx-' + tx.id;
    var es = events || [];
    if (es.some(function (e) { return e && e.id === id; })) return null;
    // 第4.139版：引く のは、その 取引から 台帳に 入った ぶん ぜんぶ（はじめに 入った ぶん＋あずかりから 補充した ぶん：どれも tx が 同じ）
    var o = null, sum = 0;
    es.forEach(function (e) { if (!e) return; if (e.id === src) o = e; if (e.tx === String(tx.id) && (e.kind === 'sub' || e.kind === 'purchase') && +e.amount > 0) sum += +e.amount; });
    if (!o) return null;
    return mk(id, 'refund', o.bucket, -Math.abs(sum || +o.amount || 0), tx.revokedAt && tms(tx.revokedAt) ? new Date(tms(tx.revokedAt)).toISOString() : iso(now), { product: o.product, tx: String(tx.id) });
  }

  // ---- あずかりポイント（第4.139版・まさちゃん 2026/11/10 12:27「99999pに到達しながらサブスクに入っている人は、ミッションのところで超えてしまっているポイントが溜まっていくようにして！
  //      で、使って減った分は、溜まってるポイントから補充できるようによろしく！」）----
  //   上限（CAP）を こえて 届いた ポイントは 台帳に 入れずに あずかる（財布の hold[]）。1件＝{ id（元の できごとの id）, kind（'sub'・'purchase'・'mission'）, product, tx, otx, what, points, at }
  //   ・あずかって いる あいだは 使えない・期限も 進まない（サブスクの ぶんは 補充した 日から SUB_DAYS 日）
  //   ・補充（holdRelease）：台帳に あきが ある ぶん だけ、古い 順に 台帳へ（できごとの id＝rel-<元の id>-<何回目>・from:'hold'）
  //   ・返金（holdDrop）：その 取引の あずかりは 消す（台帳に 入った ぶんは refundEvent が 引く）
  var HOLD_KINDS = { sub: 'paid_sub', purchase: 'paid_pack', mission: 'free' };
  function holdNorm(hold) {
    return (Array.isArray(hold) ? hold : []).filter(function (h) { return h && typeof h.id === 'string' && h.id && HOLD_KINDS[h.kind] && Math.round(+h.points || 0) > 0; })
      .map(function (h) { return Object.assign({}, h, { points: Math.round(+h.points) }); });
  }
  function holdTotal(hold) { return holdNorm(hold).reduce(function (a, h) { return a + h.points; }, 0); }
  // 種類ごとの 合計：{ total, paid_sub, paid_pack, free }
  function holdSum(hold) {
    var o = { total: 0, paid_sub: 0, paid_pack: 0, free: 0 };
    holdNorm(hold).forEach(function (h) { o[HOLD_KINDS[h.kind]] += h.points; o.total += h.points; });
    return o;
  }
  // 届いた できごと e を、台帳の あき（free＝room(合計)）で 2つに 分ける：{ event（台帳に 入れる。amount＝入る ぶん・held＝あずけた ぶん）, hold（あずかり。こえなければ null） }
  function holdSplit(e, free) {
    var amt = Math.round(+(e && e.amount) || 0), fr = Math.max(0, Math.round(+free || 0));
    if (!e || !HOLD_KINDS[e.kind] || amt <= fr) return { event: e, hold: null };
    var over = amt - fr, ev = Object.assign({}, e, { amount: fr, held: over });
    var h = { id: String(e.id), kind: e.kind, points: over, at: e.at || iso() };
    ['product', 'tx', 'otx', 'what'].forEach(function (k) { if (e[k]) h[k] = e[k]; });
    return { event: ev, hold: h };
  }
  // 補充：{ events（新しい 一覧）, hold（のこり）, moved（入れた P）, parts: { paid_sub, paid_pack, free } }。あきが なければ moved 0（そのまま）
  function holdRelease(events, hold, now) {
    var list = stamp((events || []).slice()), rest = [], moved = 0, parts = { paid_sub: 0, paid_pack: 0, free: 0 };
    var fr = room(balance(list, now).total), at = iso(now);
    holdNorm(hold).forEach(function (h) {
      var n = Math.min(h.points, fr);
      if (n > 0) {
        var pre = 'rel-' + h.id + '-', seq = list.filter(function (e) { return e && String(e.id).indexOf(pre) === 0; }).length + 1, bucket = HOLD_KINDS[h.kind];
        var extra = { from: 'hold', n: seqMax(list) + 1 };
        ['product', 'tx', 'otx', 'what'].forEach(function (k) { if (h[k]) extra[k] = h[k]; });
        if (h.kind === 'sub') extra.expires = addDays(at, SUB_DAYS);
        list.push(mk(pre + seq, h.kind, bucket, n, at, extra));
        fr -= n; moved += n; parts[bucket] += n;
      }
      if (h.points - n > 0) rest.push(Object.assign({}, h, { points: h.points - n }));
    });
    return { events: list, hold: rest, moved: moved, parts: parts };
  }
  // 返金：その 取引（tx の 番号）の あずかりを 消した 一覧
  function holdDrop(hold, txid) { return holdNorm(hold).filter(function (h) { return String(h.tx || '') !== String(txid); }); }
  function giftEvent(now, amount, id, what) { return mk(id || 'gift-first', 'gift', 'free', amount || COST.gift, iso(now), { what: what || '初回プレゼント' }); }   // amount・id・what は テスト版の P だけ
  function missionEvent(m, now) { return mk('mission-rec-' + m.n, 'mission', 'free', m.reward, iso(now), { what: m.label }); }
  // 使う：1日ごと・端末ごとに まとめる（spend-<端末>-<日付>。その日の 2件め からは 後ろに -2・-3…）。返り値は新しい一覧（足りないときは null）
  //   第4.139版：まとめる のは「いちばん あとに 書いた できごと」が 同じ 端末・同じ 日の「使った」の とき だけ。
  //     その あとに 何か 書いて いたら（届いた・解放した…）新しい 1件に する（届いた ぶんより 前に ならべない：上の「台帳の ならび」）。
  //     その 1件の 時刻（1回め）から 今までに 期限が 切れた サブスクの ぶんが ある ときも 新しい 1件（切れた ぶんからは 引かない）。
  //     さいごに たしかめる：合計が ちょうど amount へって いなければ まとめずに 新しい 1件
  function spend(events, amount, what, device, now) {
    var P = plan(events, amount, now); if (!P.ok) return null;
    var at = iso(now), day = at.slice(0, 10), dev = device || 'x', base = 'spend-' + dev + '-' + day;
    var list = stamp((events || []).slice()), top = null;
    list.forEach(function (e) { if (e && (!top || +e.n > +top.n)) top = e; });
    var cur = top && top.kind === 'spend' && String(top.id).indexOf(base) === 0 ? top : null;
    if (cur && P.balance.lots.some(function (L) { var x = tms(L.expires); return x > tms(cur.at) && x <= tms(at); })) cur = null;
    if (cur) {
      var u = useOf(cur); BUCKETS.forEach(function (b) { u[b] += P.use[b]; });
      var w = Array.isArray(cur.what) ? cur.what.slice() : (cur.what ? [cur.what] : []), more = cur.more || 0;
      if (w.length < 40) w.push(what); else more += 1;
      var next = Object.assign({}, cur, { amount: (+cur.amount || 0) - amount, use: u, what: w, last: at });
      if (more) next.more = more;
      var merged = list.map(function (e) { return e === cur ? next : e; });
      if (balance(merged, now).total === P.total - amount) return merged;
    }
    var k = list.filter(function (e) { return e && String(e.id).indexOf(base) === 0; }).length;
    list.push(mk(k ? base + '-' + (k + 1) : base, 'spend', '', -amount, at, { use: P.use, what: [what], device: dev, n: seqMax(list) + 1 }));
    return list;
  }
  // 解放：unlock-<id>（使ったPもこの1件に入れる）
  function unlock(events, key, cost, device, now) {
    var id = 'unlock-' + key;
    if ((events || []).some(function (e) { return e && e.id === id; })) return (events || []).slice();
    var P = plan(events, cost, now); if (!P.ok) return null;
    var list = stamp((events || []).slice());      // 第4.139版：書いた 順の 番号（いちばん あと）
    list.push(mk(id, 'unlock', '', -cost, iso(now), { use: P.use, what: key, device: device || 'x', n: seqMax(list) + 1 }));
    return list;
  }
  function unlocked(events, key) { var id = 'unlock-' + key; return (events || []).some(function (e) { return e && e.id === id; }); }
  function has(events, id) { return (events || []).some(function (e) { return e && e.id === id; }); }

  // ---- 結果ボードカスタム（第4.91版）----
  // 買った（取引の できごと tx-… の unlock・what＝board／wallpack）か。返金（refund-<取引>）が あれば 買って いない
  function ownedRaw(events, what) {
    var es = events || [], own = false;
    es.forEach(function (e) {
      if (!e || e.kind !== 'unlock' || e.what !== what) return;
      if (e.tx && es.some(function (r) { return r && r.id === 'refund-' + e.tx; })) return;
      own = true;
    });
    return own;
  }
  // 第4.114版：お得パック（what＝bundle）を 持って いれば、壁紙パックと 結果ボードカスタムも 持って いる 扱い（お得パックの 返金で 両方 使えなくなる・単品の 分は 残る）
  function owned(events, what) { return ownedRaw(events, what) || (BUNDLE.parts.indexOf(what) >= 0 && ownedRaw(events, 'bundle')); }
  function bundleOwned(events) { return ownedRaw(events, 'bundle'); }
  // お得パックを 出すか：単品を どちらも 持って いない ときだけ（どちらか 1つ 持って いれば 残りの 単品だけ）
  function bundleOffer(events) { return !owned(events, 'wallpack') && !owned(events, 'board'); }
  function boardOwned(events) { return owned(events, 'board'); }
  // 読み込んだ レースの 数 → 解放した 数（0〜15：じゅんび中の 番号も 数える）
  function boardUnlocked(reads) { var n = 0; BOARD_NEED.forEach(function (k) { if ((+reads || 0) >= k) n++; }); return n; }
  // つぎに 解放する 番号（じゅんび中も ふくむ・全部 解放ずみ なら null）：{ item, need（その 数）, left（あと いくつ）, from（ひとつ前の 数）}
  function boardNext(reads) {
    var n = boardUnlocked(reads); if (n >= BOARD_ITEMS.length) return null;
    var it = BOARD_ITEMS[n];
    return { item: it, need: it.need, left: it.need - (+reads || 0), from: n ? BOARD_NEED[n - 1] : 0 };
  }
  // つぎに 解放する 飾り（じゅんび中は とばす・なければ null）：{ item, need, left }
  function boardNextReady(reads) {
    var r = +reads || 0;
    for (var i = 0; i < BOARD_ITEMS.length; i++) { var it = BOARD_ITEMS[i]; if (it.ready && it.need > r) return { item: it, need: it.need, left: it.need - r }; }
    return null;
  }
  // 壁紙パック（第4.92版・まさちゃんの 指定）：買い切り 1,500円・10枚（第4.147版：七夕を 外して 11 → 10枚）。買った あとに 読み込んだ レース（200P で 読んだ 1レース・読み直しと 5連の 予想は 数えない）
  //   5つごとに 1枚ずつ 解放（50レースで 全部）。順番は 着せ替えの 一覧の 順（kisekae の pack.order）。帯の 壁紙の ミッション（5・10・15枚：第4.160版）の 枚数に 数える
  var WALLPACK = { product: 'jp.tengel.app.wallpack1', every: 5, n: 10 };
  function packOwned(events) { return owned(events, 'wallpack'); }
  function packUnlocked(reads) { return Math.min(WALLPACK.n, Math.floor((+reads || 0) / WALLPACK.every)); }
  // つぎに 解放する 1枚（全部 解放ずみ なら null）：{ no（1〜11）, need（その 読み込みの 数）, left（あと いくつ）, from（ひとつ前の 数）}
  function packNext(reads) {
    var n = packUnlocked(reads); if (n >= WALLPACK.n) return null;
    var need = (n + 1) * WALLPACK.every;
    return { no: n + 1, need: need, left: need - (+reads || 0), from: n * WALLPACK.every };
  }

  // ---- ミッション（記録の数）----
  function missionAt(i) {
    if (i < MISSIONS.length) return { n: MISSIONS[i][0], reward: MISSIONS[i][1] };
    return { n: 300 + 100 * (i - MISSIONS.length + 1), reward: 2000 };
  }
  // 返り値：いまの数に対して、受け取れるもの・受け取ったもの・つぎのもの（次の1つまで）
  function missions(count, events) {
    var out = [], i = 0;
    for (;;) {
      var m = missionAt(i), id = 'mission-rec-' + m.n, claimed = has(events, id);
      var row = { id: id, n: m.n, reward: m.reward, label: m.n + 'レース記録', done: count >= m.n, claimed: claimed, claimable: count >= m.n && !claimed };
      out.push(row);
      if (!row.done) break;
      i++;
      if (i > 400) break;
    }
    return out;
  }

  // ---- 壁紙のミッション（帯の壁紙）----
  function wallMissions(count, events) {
    return WALL_MISSIONS.map(function (m) { var id = 'mission-wall-' + m[1], claimed = has(events, id) || unlocked(events, 'theme:' + m[1]); return { id: id, n: m[0], theme: m[1], label: m[2], done: count >= m[0], claimed: claimed, claimable: count >= m[0] && !claimed }; });
  }
  function wallMissionEvents(m, device, now) {
    return [mk(m.id || ('mission-wall-' + m.theme), 'mission', 'free', 0, iso(now), { what: m.label, theme: m.theme }),
      mk('unlock-theme:' + m.theme, 'unlock', '', 0, iso(now), { use: { paid_sub: 0, paid_pack: 0, free: 0 }, what: 'theme:' + m.theme, device: device || 'x' })];
  }
  // 第4.114版：ふつうの ミッションの 行（id・n・reward）→ 受け取れる／受け取った
  function rowsOf(table, prefix, count, events, label) {
    return table.map(function (m) { var id = prefix + m[0], claimed = has(events, id); return { id: id, n: m[0], reward: m[1], label: label(m[0]), done: count >= m[0], claimed: claimed, claimable: count >= m[0] && !claimed }; });
  }
  // 結果ボードカスタムの ミッション：count＝解放した 番号の 数（買って いなければ 0）
  function boardMissions(count, events) {
    var rows = rowsOf(BOARD_MISSIONS, 'mission-board-', count, events, function (n) { return '結果ボードカスタム ' + n + 'こ解放'; });
    // 第4.120版：前の 版の「16こ解放」（mission-board-16）を 受け取った 人は「15こ解放」を 受け取った ことに（2回 もらえない）
    if (has(events, 'mission-board-16')) rows.forEach(function (r) { if (r.n === 15) { r.claimed = true; r.claimable = false; } });
    return rows;
  }
  // 壁紙の ミッション（枚数で ポイント）：count＝wallCountAll。WALL_TOTAL より 多い 行は reach＝false（いまは 届かない）
  function wallpMissions(count, events) {
    var rows = rowsOf(WALLP_MISSIONS, 'mission-wallp-', count, events, function (n) { return '壁紙 ' + n + '枚解放'; }).map(function (r) { r.reach = r.n <= WALL_TOTAL; return r; });
    // 第4.160版：前の 版の「30枚解放」（mission-wallp-30）を 受け取った 人は「29枚解放」を 受け取った ことに（2回 もらえない）
    if (has(events, 'mission-wallp-30')) rows.forEach(function (r) { if (r.n === 29) { r.claimed = true; r.claimable = false; } });
    return rows;
  }
  // 第4.130版：トレーニングセンターの ミッション（まさちゃん 2026/11/09「馬をお世話して1段階目の成長させる お世話合計50回 獲得ポイント500p … ※1回で解放したら、馬がリセットされてもミッションはリセットされない」）
  //   count＝お世話の 合計（ごはん・おそうじ。色が かわって 馬が リセット されても 減らない）。1回 受け取ったら もう 出ない
  var TC_MISSIONS = [[50, 500, 1], [100, 1000, 2], [150, 1500, 3], [200, 2000, 4]];
  function tcMissions(count, events) {
    return TC_MISSIONS.map(function (m) { var id = 'mission-tc-' + m[0], claimed = has(events, id); return { id: id, n: m[0], reward: m[1], label: '馬をお世話して' + m[2] + '段階目の成長させる', done: count >= m[0], claimed: claimed, claimable: count >= m[0] && !claimed }; });
  }
  // 第4.138版：思い出フィギュアの ミッション（まさちゃん 2026/11/10 10:50「ミッション 思い出フィギュアを１つ完成させる 5000p／5つ完成させる 5000p／8つ完成させる 10000p」）
  //   count＝作った 思い出フィギュアの 数（しまって あっても 数える）。1回 受け取ったら もう 出ない
  var FIG_MISSIONS = [[1, 5000], [5, 5000], [8, 10000]];
  function figMissions(count, events) { return rowsOf(FIG_MISSIONS, 'mission-fig-', count, events, function (n) { return '思い出フィギュアを' + n + 'つ完成させる'; }); }
  function rowEvent(m, now) { return mk(m.id, 'mission', 'free', m.reward, iso(now), { what: m.label }); }
  // 解放した 壁紙の 枚数（帯も 数える：ポイント＋壁紙パック＋帯）
  function wallCountAll(events, packN) { return wallCount(events, packN) + (events || []).filter(function (e) { return e && e.kind === 'unlock' && /^theme:(silver|golden|tengel)$/.test(String(e.what || '')); }).length; }
  // 解放した壁紙の枚数（ポイントで 解放した 壁紙 ＋ 壁紙パックで 解放した 枚数 packN。帯の壁紙は数えない）
  //   第4.147版：外した 壁紙（GONE_THEMES）は 数えない
  function goneTheme(what) { var m = /^theme:(.+)$/.exec(String(what || '')); return !!m && GONE_THEMES.indexOf(m[1]) >= 0; }
  function wallCount(events, packN) { return (events || []).filter(function (e) { return e && e.kind === 'unlock' && /^theme:/.test(String(e.what || '')) && !/^theme:(silver|golden|tengel)$/.test(String(e.what)) && !goneTheme(e.what); }).length + Math.max(0, Math.floor(+packN || 0)); }
  // 外した 壁紙を 解放して いた ぶん（まだ 返して いない もの）：[{ theme, name, cost（使った ポイント・0＝チケットで 解放した）, id（返した しるし back-theme:<名前>） }]。
  //   heldIds：あずかりポイントに 入って いる id（上限で あずかった ぶんも「返した」に 数える）
  function goneUnlocks(events, heldIds) {
    var out = [];
    (events || []).forEach(function (e) {
      if (!e || e.kind !== 'unlock' || !goneTheme(e.what)) return;
      var t = String(e.what).slice(6), id = 'back-theme:' + t;
      if (has(events, id) || (heldIds || []).indexOf(id) >= 0 || out.some(function (o) { return o.theme === t; })) return;
      out.push({ theme: t, name: GONE_NAMES[t] || t, cost: Math.max(0, Math.round(-(+e.amount || 0))), id: id });
    });
    return out;
  }

  // ---- レースの見分け方（読み直し0P・ミッションの数え方）----
  function vnorm(v) { return String(v || '').normalize('NFKC').replace(/\s/g, '').replace(/(競馬場|競馬)$/, ''); }
  // ミッション：日付＋開催場＋R（開催場が空なら空のまま）
  function raceKey(b) { if (!b || !b.date || !b.r) return ''; return String(b.date) + '|' + vnorm(b.venue) + '|' + (+b.r); }
  // 読み直し（11.4）：同じ日付で、レース名・距離・発走時刻が同じ（まさちゃんの指定）か、同じ開催場・Rなら同じレース。開催場が片方だけ空なら、空のほうは何でもOK
  function sameRace(a, b) {
    if (!a || !b || !a.date || !b.date || String(a.date) !== String(b.date)) return false;
    var na = vnorm(a.rname), nb = vnorm(b.rname);
    if (na && nb && a.start && b.start && na === nb && String(a.start) === String(b.start) && (+a.dist || 0) === (+b.dist || 0)) return true;
    if (+a.r && +b.r && +a.r === +b.r) { var va = vnorm(a.venue), vb = vnorm(b.venue); return !va || !vb || va === vb; }
    return false;
  }
  function findPaid(paid, race) { for (var i = (paid || []).length - 1; i >= 0; i--) if (sameRace(paid[i], race)) return paid[i]; return null; }

  // ---- 読み直しの 見分け：読んだ 中身も 見る（第4.140版・まさちゃん 2026/11/10 14:22「きびしくする（人気の並びが前とぜんぜん違ったら200P。同じレースの読み直しは0Pのまま）これで！」）----
  //   「同じレースの 読み直しは 0P」は、画像に 日付・R が 写って いないと 入力の 日付・R で 同じ レースと 見て いた → 切り取った 画像なら 別の レースも 0P で 読めた。
  //   → 読んだ 単勝の 表（馬番と オッズ）を 読み込みの しるし（paid の fp）に おぼえて、次に 読んだ 表と くらべる（points_ui.js の readCharge）。
  //   しきい値：どちらにも ある 馬番が 6頭 以上・順位の 相関が 0.3 より 低い・同じ オッズの 数が 半分 より 少ない。
  //   ためした 数（2万回ずつ・作った オッズ）：同じ レースを まちがえて 200P に する のは、オッズが 大きく 動いても（±50%）8頭で 約0.1%・10頭 以上で ほぼ 0・6頭で 約0.9%。
  //   別の レースが 0P で 通る のは 6頭 約28%・8頭 約24%・12頭 約16%・16頭 約13%（＝ほとんど 200P かかる ので、切り取った 画像で 読む 手は 得に ならない）
  var FP_MIN = 6, FP_RHO = 0.3, FP_SAME = 0.5;
  // 'no:tan,no:tan…' か [{no,tan}] か [[no,tan]] → [[馬番, 単勝]]（馬番の 順・同じ 馬番は 1つ・20頭まで）
  function fpList(fp) {
    var src = typeof fp === 'string' ? fp.split(',').map(function (x) { return x.split(':'); }) : Array.isArray(fp) ? fp : [], out = [], seen = {};
    src.forEach(function (h) {
      var no = Math.round(+(Array.isArray(h) ? h[0] : h && h.no)), tan = +(Array.isArray(h) ? h[1] : h && h.tan);
      if (!(no >= 1 && no <= 40) || !(tan > 0) || !isFinite(tan) || seen[no]) return;
      seen[no] = 1; out.push([no, Math.round(tan * 10) / 10]);
    });
    out.sort(function (a, b) { return a[0] - b[0]; });
    return out.slice(0, 20);
  }
  // 読んだ 単勝の 表 → おぼえる 形（'1:2.4,2:15.3…'）。表が なければ ''
  function raceFp(rows) { return fpList(rows).map(function (h) { return h[0] + ':' + h[1]; }).join(','); }
  // 順位（小さい 順・同じ 数は 同じ 順位＝平均）
  function ranksOf(v) {
    var idx = v.map(function (x, i) { return i; }).sort(function (a, b) { return v[a] - v[b]; }), r = [];
    for (var i = 0; i < idx.length;) { var j = i; while (j + 1 < idx.length && v[idx[j + 1]] === v[idx[i]]) j++; for (var k = i; k <= j; k++) r[idx[k]] = (i + j) / 2 + 1; i = j + 1; }
    return r;
  }
  // 2つの 表の 人気の 順（単勝の 低い 順）の 近さ：どちらにも ある 馬番で 数える 順位の 相関（スピアマン）。数えられない ときは null
  function fpRho(a, b) {
    var A = fpList(a), B = fpList(b), mb = {}, xa = [], xb = [];
    B.forEach(function (h) { mb[h[0]] = h[1]; });
    A.forEach(function (h) { if (mb[h[0]] != null) { xa.push(h[1]); xb.push(mb[h[0]]); } });
    if (xa.length < FP_MIN) return null;
    var ra = ranksOf(xa), rb = ranksOf(xb), n = ra.length, ma = 0, mbb = 0, sab = 0, saa = 0, sbb = 0;
    for (var i = 0; i < n; i++) { ma += ra[i]; mbb += rb[i]; }
    ma /= n; mbb /= n;
    for (var j = 0; j < n; j++) { sab += (ra[j] - ma) * (rb[j] - mbb); saa += (ra[j] - ma) * (ra[j] - ma); sbb += (rb[j] - mbb) * (rb[j] - mbb); }
    if (!(saa > 0) || !(sbb > 0)) return null;
    return sab / Math.sqrt(saa * sbb);
  }
  // b（新しく 読んだ 表）の オッズの うち、a（前の 表）にも ある 数の わりあい（0〜1）
  function fpShare(a, b) {
    var A = fpList(a), B = fpList(b), cnt = {}, hit = 0;
    A.forEach(function (h) { cnt[h[1]] = (cnt[h[1]] || 0) + 1; });
    B.forEach(function (h) { if (cnt[h[1]] > 0) { cnt[h[1]] -= 1; hit += 1; } });
    return B.length ? hit / B.length : 0;
  }
  // 「ぜんぜん ちがう」（＝別の レース）か：
  //   人気の 順が ぜんぜん ちがう（相関が FP_RHO より 低い）かつ オッズの 数も ほとんど ちがう（同じ 数が FP_SAME＝半分 より 少ない）とき だけ true。
  //   ・同じ レースは オッズが 動いても 人気の 順は ほぼ 同じ（相関が 高い）
  //   ・同じ 画像を 読み直して 馬番との 組み合わせが ずれた だけ なら、オッズの 数は ほぼ 同じ
  //   ・くらべられない とき（どちらかに 表が ない・どちらにも ある 馬番が FP_MIN 頭 より 少ない）は false ＝ 同じ レースと 見る（前と 同じ）
  function fpDiff(a, b) {
    var rho = fpRho(a, b);
    if (rho == null || rho >= FP_RHO) return false;
    return fpShare(a, b) < FP_SAME;
  }

  var API = { PRODUCTS: PRODUCTS, PACKS: PACKS, SUBS: SUBS, COST: COST, SUB_DAYS: SUB_DAYS, MISSIONS: MISSIONS, FREE_TYPES: FREE_TYPES, UNLOCK_TYPES: UNLOCK_TYPES, ALL_TYPES: ALL_TYPES,
    balance: balance, plan: plan, txEvent: txEvent, refundEvent: refundEvent, giftEvent: giftEvent, missionEvent: missionEvent, spend: spend, unlock: unlock, unlocked: unlocked, has: has,
    BOARD: BOARD, BOARD_NEED: BOARD_NEED, BOARD_ITEMS: BOARD_ITEMS, boardOwned: boardOwned, boardUnlocked: boardUnlocked, boardNext: boardNext, boardNextReady: boardNextReady, boardFits: boardFits,
    boardSlot: boardSlot, boardKnown: boardKnown, boardSel: boardSel, boardActive: boardActive, boardOpen: boardOpen, owned: owned,
    BUNDLE: BUNDLE, bundleOwned: bundleOwned, bundleOffer: bundleOffer, BOARD_MISSIONS: BOARD_MISSIONS, WALLP_MISSIONS: WALLP_MISSIONS, WALL_TOTAL: WALL_TOTAL,
    boardMissions: boardMissions, wallpMissions: wallpMissions, rowEvent: rowEvent, wallCountAll: wallCountAll, TC_MISSIONS: TC_MISSIONS, tcMissions: tcMissions, FIG_MISSIONS: FIG_MISSIONS, figMissions: figMissions, CAP: CAP, room: room, TICKET_POINTS: TICKET_POINTS,
    holdNorm: holdNorm, holdTotal: holdTotal, holdSum: holdSum, holdSplit: holdSplit, holdRelease: holdRelease, holdDrop: holdDrop,
    stamp: stamp, stampAll: stampAll, seqMax: seqMax, raceFp: raceFp, fpDiff: fpDiff, fpRho: fpRho, fpShare: fpShare, FP: { min: FP_MIN, rho: FP_RHO, same: FP_SAME },
    WALLPACK: WALLPACK, packOwned: packOwned, packUnlocked: packUnlocked, packNext: packNext,
    missions: missions, missionAt: missionAt, WALL_MISSIONS: WALL_MISSIONS, wallMissions: wallMissions, wallMissionEvents: wallMissionEvents, wallCount: wallCount, GONE_THEMES: GONE_THEMES, GONE_NAMES: GONE_NAMES, goneUnlocks: goneUnlocks, raceKey: raceKey, sameRace: sameRace, findPaid: findPaid, vnorm: vnorm, addDays: addDays, iso: iso };
  root.TengelPoints = API;
  if (typeof module !== 'undefined' && module.exports) module.exports = API;
})(typeof window !== 'undefined' ? window : globalThis);
