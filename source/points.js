// ===== ポイント（App Store版）：台帳の計算だけ。画面・保存はしない（points_ui.js）。node でテストできる（test_points.js） =====
// 台帳＝1件ずつの「できごと」（4.3）。残高はできごとから毎回計算する。
//   kind：purchase（パック）・sub（サブスク）・gift（初回）・mission・spend（読み込みなど）・unlock（解放）・refund（返金）
//   bucket：paid_pack（買ったP）・paid_sub（サブスクのP・届いた日から30日）・free（もらったP）
//   使う順（4.2）：サブスクのP（期限が近い順）→ パック → 無償。足りないときは使えない（マイナスにしない）
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
    // 第4.92版：壁紙パック（買い切り・非消耗型）。新しい 壁紙 11枚。買った あとに 読み込んだ レース 5つごとに 1枚ずつ 解放（ポイントでは 買えない）
    'jp.tengel.app.wallpack1': { kind: 'unlock', what: 'wallpack', points: 0, bonus: 0, name: '壁紙パック', yen: 1500 },
    // 第4.114版：お得パック（買い切り・非消耗型）。壁紙パックと 結果ボードカスタムの セット 2,200円（単品は 1,500円ずつ＝3,000円）。持って いれば 両方を 持って いる 扱い（owned）
    'jp.tengel.app.bundle1': { kind: 'unlock', what: 'bundle', points: 0, bonus: 0, name: 'お得パック', yen: 2200 }
  };
  var BUNDLE = { product: 'jp.tengel.app.bundle1', parts: ['wallpack', 'board'] };
  var PACKS = ['jp.tengel.app.points500', 'jp.tengel.app.points1000', 'jp.tengel.app.points2000', 'jp.tengel.app.points4000'];
  var SUBS = ['jp.tengel.app.sub2000', 'jp.tengel.app.sub4400', 'jp.tengel.app.sub9200'];
  var COST = { gift: 1500, read: 200, w5: 200, type: 500, slot: 15000 };
  var SUB_DAYS = 30;
  // 記録のミッション（8.2）：記録したレースの数 → もらえるP。300のあとは100レースごとに2,000P
  var MISSIONS = [[8, 500], [15, 1000], [25, 1000], [40, 1200], [60, 1200], [85, 1400], [100, 1400], [130, 1600], [160, 1600], [200, 1800], [240, 1800], [300, 2000]];
  // 壁紙のミッション（8.3・第4弾）：ポイントで解放した壁紙の枚数 → 帯の壁紙（シルバー帯 8枚・ゴールド帯 16枚・マスター帯 25枚）。受け取ると 0P の mission と unlock-theme:<帯> を足す
  var WALL_MISSIONS = [[8, 'silver', 'シルバー帯の壁紙'], [16, 'golden', 'ゴールド帯の壁紙'], [25, 'tengel', 'マスター帯の壁紙']];
  // 第4.114版（まさちゃん 2026/11/01）：結果ボードカスタムの 解放の 数（解放した 番号の 数＝画面の「解放 n/16」・じゅんび中も 数える）→ もらえるP
  var BOARD_MISSIONS = [[3, 500], [6, 800], [9, 1100], [12, 1400], [16, 1600]];
  // 第4.114版（まさちゃん 2026/11/01）：壁紙の 解放の 枚数（ポイントで 解放＋壁紙パックで 解放＋帯の 3枚：いつもの は 数えない）→ もらえるP。
  //   いま 解放できる 壁紙は WALL_TOTAL＝40枚（ポイント 26＋壁紙パック 11＋帯 3）。45枚は 壁紙が ふえたら 届く（一覧には 出す）
  var WALLP_MISSIONS = [[3, 800], [6, 1200], [9, 1500], [12, 1800], [15, 2100], [20, 2500], [25, 2500], [30, 2500], [35, 3500], [40, 3500], [45, 3500]];
  var WALL_TOTAL = 40;
  var FREE_TYPES = ['単勝', '馬単', '3連単'];
  var UNLOCK_TYPES = ['複勝', '枠複', '枠単', '馬連', 'ワイド', '3連複'];
  var ALL_TYPES = ['単勝', '複勝', '枠複', '枠単', '馬連', '馬単', 'ワイド', '3連複', '3連単'];
  var BUCKETS = ['paid_sub', 'paid_pack', 'free'];
  // 結果ボードカスタム（第4.91版・まさちゃんの 指定）：買い切り 2,200円（第4.114版から 1,500円）。買った あとに 読み込んだ レースの 数で、番号の 順に 1つずつ 解放する。読み直し（0P）・5連の 予想は 数えない
  //   第4.113版（まさちゃん 2026/11/01「結果ボードカスタム、最後のボードを持つ馬以外一度全部消して！全部で16個(ボードを持つ馬を含む)にする！」）：
  //     16こ・6レースごとに 1つ（全部で 96レース）。前の 1〜21（ボードを一周〜出世馬）は 消した。1〜15 は じゅんび中（まさちゃんの デザインが とどいたら 入れる）・16 は ボードを持つ馬
  //   第4.113版（まさちゃん 01:24「結果ボードのカスタムには2種類カスタムつけられるようにして！①的中演出 ②ハズレ演出」）：的中の とき・ハズレの とき で べつべつに 1つずつ 選ぶ
  //     （points_ui.js の board.selHit・board.selMiss。解放の 数は 1つ＝買うのも 1回）
  var BOARD = { product: 'jp.tengel.app.boardcustom', steps: [[16, 6]] };
  var BOARD_NEED = (function () { var out = [], n = 0; BOARD.steps.forEach(function (st) { for (var i = 0; i < st[0]; i++) { n += st[1]; out.push(n); } }); return out; })();
  // 16こ（番号の 順＝解放の 順）。null＝じゅんび中（設定に「じゅんび中」の タイル・選べない）。
  //   飾りを 入れる ときは、その 番号の null を [id, 名前, せつめい, when] に かえて、bcx.js に B.<id>（部品を 作る 所）を 足す（README「結果ボードカスタムに 飾りを 入れる」）
  //   when：all＝的中にも ハズレにも 使える・hit＝的中の とき だけ・big＝的中の うち デカ的中から 上 だけ・miss＝ハズレの とき だけ
  var BOARD_ITEMS = [
    /* 1 */ null,
    /* 2 */ null,
    /* 3 */ null,
    /* 4 */ null,
    /* 5 */ null,
    /* 6 */ null,
    /* 7 */ null,
    /* 8 */ null,
    /* 9 */ null,
    /* 10 */ null,
    /* 11 */ null,
    /* 12 */ null,
    /* 13 */ null,
    /* 14 */ null,
    /* 15 */ null,
    /* 16 */ ['carry', 'ボードを持つ馬', '馬がうしろからボードを持って、下から出てくる', 'all']
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
  function sorted(events) { return (events || []).filter(Boolean).slice().sort(function (a, b) { return tms(a.at) - tms(b.at) || String(a.id).localeCompare(String(b.id)); }); }
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
        if (e.bucket === 'paid_sub') { var lot = null; lots.forEach(function (L) { if (!lot && e.tx && L.tx === e.tx) lot = L; }); if (lot) lot.remain = 0; }
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
    var o = null; es.forEach(function (e) { if (e && e.id === src) o = e; });
    if (!o) return null;
    return mk(id, 'refund', o.bucket, -Math.abs(+o.amount || 0), tx.revokedAt && tms(tx.revokedAt) ? new Date(tms(tx.revokedAt)).toISOString() : iso(now), { product: o.product, tx: String(tx.id) });
  }
  function giftEvent(now, amount, id, what) { return mk(id || 'gift-first', 'gift', 'free', amount || COST.gift, iso(now), { what: what || '初回プレゼント' }); }   // amount・id・what は テスト版の P だけ
  function missionEvent(m, now) { return mk('mission-rec-' + m.n, 'mission', 'free', m.reward, iso(now), { what: m.label }); }
  // 使う：1日ごと・端末ごとに1件にまとめる（spend-<端末>-<日付>）。返り値は新しい一覧（足りないときは null）
  function spend(events, amount, what, device, now) {
    var P = plan(events, amount, now); if (!P.ok) return null;
    var at = iso(now), day = at.slice(0, 10), id = 'spend-' + (device || 'x') + '-' + day;
    var list = (events || []).slice(), cur = null;
    list.forEach(function (e) { if (e && e.id === id) cur = e; });
    if (cur) {
      var u = useOf(cur); BUCKETS.forEach(function (b) { u[b] += P.use[b]; });
      var w = Array.isArray(cur.what) ? cur.what.slice() : (cur.what ? [cur.what] : []);
      if (w.length < 40) w.push(what); else cur.more = (cur.more || 0) + 1;
      var next = Object.assign({}, cur, { amount: (+cur.amount || 0) - amount, use: u, what: w, last: at });
      return list.map(function (e) { return e === cur ? next : e; });
    }
    list.push(mk(id, 'spend', '', -amount, at, { use: P.use, what: [what], device: device || 'x' }));
    return list;
  }
  // 解放：unlock-<id>（使ったPもこの1件に入れる）
  function unlock(events, key, cost, device, now) {
    var id = 'unlock-' + key;
    if ((events || []).some(function (e) { return e && e.id === id; })) return (events || []).slice();
    var P = plan(events, cost, now); if (!P.ok) return null;
    return (events || []).concat([mk(id, 'unlock', '', -cost, iso(now), { use: P.use, what: key, device: device || 'x' })]);
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
  // 読み込んだ レースの 数 → 解放した 数（0〜16：じゅんび中の 番号も 数える）
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
  // 壁紙パック（第4.92版・まさちゃんの 指定）：買い切り 1,500円・11枚。買った あとに 読み込んだ レース（200P で 読んだ 1レース・読み直しと 5連の 予想は 数えない）
  //   5つごとに 1枚ずつ 解放（55レースで 全部）。順番は 着せ替えの 一覧の 順（kisekae の pack.order）。帯の 壁紙の ミッション（8・16・25枚）の 枚数に 数える
  var WALLPACK = { product: 'jp.tengel.app.wallpack1', every: 5, n: 11 };
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
    return WALL_MISSIONS.map(function (m) { var id = 'mission-wall-' + m[0], claimed = has(events, id); return { id: id, n: m[0], theme: m[1], label: m[2], done: count >= m[0], claimed: claimed, claimable: count >= m[0] && !claimed }; });
  }
  function wallMissionEvents(m, device, now) {
    return [mk('mission-wall-' + m.n, 'mission', 'free', 0, iso(now), { what: m.label, theme: m.theme }),
      mk('unlock-theme:' + m.theme, 'unlock', '', 0, iso(now), { use: { paid_sub: 0, paid_pack: 0, free: 0 }, what: 'theme:' + m.theme, device: device || 'x' })];
  }
  // 第4.114版：ふつうの ミッションの 行（id・n・reward）→ 受け取れる／受け取った
  function rowsOf(table, prefix, count, events, label) {
    return table.map(function (m) { var id = prefix + m[0], claimed = has(events, id); return { id: id, n: m[0], reward: m[1], label: label(m[0]), done: count >= m[0], claimed: claimed, claimable: count >= m[0] && !claimed }; });
  }
  // 結果ボードカスタムの ミッション：count＝解放した 番号の 数（買って いなければ 0）
  function boardMissions(count, events) { return rowsOf(BOARD_MISSIONS, 'mission-board-', count, events, function (n) { return '結果ボードカスタム ' + n + 'こ解放'; }); }
  // 壁紙の ミッション（枚数で ポイント）：count＝wallCountAll。WALL_TOTAL より 多い 行は reach＝false（いまは 届かない）
  function wallpMissions(count, events) { return rowsOf(WALLP_MISSIONS, 'mission-wallp-', count, events, function (n) { return '壁紙 ' + n + '枚解放'; }).map(function (r) { r.reach = r.n <= WALL_TOTAL; return r; }); }
  function rowEvent(m, now) { return mk(m.id, 'mission', 'free', m.reward, iso(now), { what: m.label }); }
  // 解放した 壁紙の 枚数（帯も 数える：ポイント＋壁紙パック＋帯）
  function wallCountAll(events, packN) { return wallCount(events, packN) + (events || []).filter(function (e) { return e && e.kind === 'unlock' && /^theme:(silver|golden|tengel)$/.test(String(e.what || '')); }).length; }
  // 解放した壁紙の枚数（ポイントで 解放した 壁紙 ＋ 壁紙パックで 解放した 枚数 packN。帯の壁紙は数えない）
  function wallCount(events, packN) { return (events || []).filter(function (e) { return e && e.kind === 'unlock' && /^theme:/.test(String(e.what || '')) && !/^theme:(silver|golden|tengel)$/.test(String(e.what)); }).length + Math.max(0, Math.floor(+packN || 0)); }

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

  var API = { PRODUCTS: PRODUCTS, PACKS: PACKS, SUBS: SUBS, COST: COST, SUB_DAYS: SUB_DAYS, MISSIONS: MISSIONS, FREE_TYPES: FREE_TYPES, UNLOCK_TYPES: UNLOCK_TYPES, ALL_TYPES: ALL_TYPES,
    balance: balance, plan: plan, txEvent: txEvent, refundEvent: refundEvent, giftEvent: giftEvent, missionEvent: missionEvent, spend: spend, unlock: unlock, unlocked: unlocked, has: has,
    BOARD: BOARD, BOARD_NEED: BOARD_NEED, BOARD_ITEMS: BOARD_ITEMS, boardOwned: boardOwned, boardUnlocked: boardUnlocked, boardNext: boardNext, boardNextReady: boardNextReady, boardFits: boardFits,
    boardSlot: boardSlot, boardKnown: boardKnown, boardSel: boardSel, boardActive: boardActive, boardOpen: boardOpen, owned: owned,
    BUNDLE: BUNDLE, bundleOwned: bundleOwned, bundleOffer: bundleOffer, BOARD_MISSIONS: BOARD_MISSIONS, WALLP_MISSIONS: WALLP_MISSIONS, WALL_TOTAL: WALL_TOTAL,
    boardMissions: boardMissions, wallpMissions: wallpMissions, rowEvent: rowEvent, wallCountAll: wallCountAll,
    WALLPACK: WALLPACK, packOwned: packOwned, packUnlocked: packUnlocked, packNext: packNext,
    missions: missions, missionAt: missionAt, WALL_MISSIONS: WALL_MISSIONS, wallMissions: wallMissions, wallMissionEvents: wallMissionEvents, wallCount: wallCount, raceKey: raceKey, sameRace: sameRace, findPaid: findPaid, vnorm: vnorm, addDays: addDays, iso: iso };
  root.TengelPoints = API;
  if (typeof module !== 'undefined' && module.exports) module.exports = API;
})(typeof window !== 'undefined' ? window : globalThis);
