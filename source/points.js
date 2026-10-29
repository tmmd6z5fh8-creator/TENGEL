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
    'jp.tengel.app.boardcustom': { kind: 'unlock', what: 'board', points: 0, bonus: 0, name: '結果ボードカスタム', yen: 2200 },
    // 第4.92版：壁紙パック（買い切り・非消耗型）。新しい 壁紙 11枚。買った あとに 読み込んだ レース 5つごとに 1枚ずつ 解放（ポイントでは 買えない）
    'jp.tengel.app.wallpack1': { kind: 'unlock', what: 'wallpack', points: 0, bonus: 0, name: '壁紙パック', yen: 1500 }
  };
  var PACKS = ['jp.tengel.app.points500', 'jp.tengel.app.points1000', 'jp.tengel.app.points2000', 'jp.tengel.app.points4000'];
  var SUBS = ['jp.tengel.app.sub2000', 'jp.tengel.app.sub4400', 'jp.tengel.app.sub9200'];
  var COST = { gift: 1500, read: 200, w5: 200, type: 500, slot: 15000 };
  var SUB_DAYS = 30;
  // 記録のミッション（8.2）：記録したレースの数 → もらえるP。300のあとは100レースごとに2,000P
  var MISSIONS = [[8, 500], [15, 1000], [25, 1000], [40, 1200], [60, 1200], [85, 1400], [100, 1400], [130, 1600], [160, 1600], [200, 1800], [240, 1800], [300, 2000]];
  // 壁紙のミッション（8.3・第4弾）：ポイントで解放した壁紙の枚数 → 帯の壁紙（シルバー帯 8枚・ゴールド帯 16枚・マスター帯 25枚）。受け取ると 0P の mission と unlock-theme:<帯> を足す
  var WALL_MISSIONS = [[8, 'silver', 'シルバー帯の壁紙'], [16, 'golden', 'ゴールド帯の壁紙'], [25, 'tengel', 'マスター帯の壁紙']];
  var FREE_TYPES = ['単勝', '馬単', '3連単'];
  var UNLOCK_TYPES = ['複勝', '枠複', '枠単', '馬連', 'ワイド', '3連複'];
  var ALL_TYPES = ['単勝', '複勝', '枠複', '枠単', '馬連', '馬単', 'ワイド', '3連複', '3連単'];
  var BUCKETS = ['paid_sub', 'paid_pack', 'free'];
  // 結果ボードカスタム（第4.91版・まさちゃんの 指定）：買い切り 2,200円。買った あとに 読み込んだ レースの 数で、22こを 番号の 順に 1つずつ 解放する
  //   1〜5：5レースごと・6〜10：6レースごと・11〜15：7レースごと・16〜22：8レースごと（全部で 146レース）。読み直し（0P）・5連の 予想は 数えない
  //   第4.108版：22「ボードを持つ馬」（いちばん はじめの 頃の ボード）を 出世馬の あとに 足した（8レース・146レース目）
  var BOARD = { product: 'jp.tengel.app.boardcustom', steps: [[5, 5], [5, 6], [5, 7], [7, 8]] };
  var BOARD_NEED = (function () { var out = [], n = 0; BOARD.steps.forEach(function (st) { for (var i = 0; i < st[0]; i++) { n += st[1]; out.push(n); } }); return out; })();
  // 22こ（番号の 順＝解放の 順）。when：all＝いつも・hit＝的中の とき・big＝デカ的中から 上・miss＝ハズレの とき
  var BOARD_ITEMS = [
    ['orbit', 'ボードを一周', 'ボードのまわりを、馬がぐるぐる走る', 'all'],
    ['goal', 'ゴール板', 'ボードの下の帯を走って、ゴールに駆け込む', 'all'],
    ['peek', 'ひょっこり', 'ボードの下から馬が顔を出して、まばたき', 'all'],
    ['nap', '上でお昼寝', 'ボードの上で馬が寝そべって、しっぽがゆらゆら', 'all'],
    ['hang', 'ぶら下がり', 'ボードの角に子馬がぶら下がって、足をぱたぱた', 'all'],
    ['cheer', 'ハズレの励まし', 'ハズレのとき、馬がボードにもたれて「次いこ！」', 'miss'],
    ['crowd', '観客席', 'ボードの下で、観客の馬たちが歓声と拍手', 'all'],
    ['selfie', '自撮り', '馬が自撮り棒で、ボードといっしょにパシャ', 'all'],
    ['bite', 'くわえて持つ', '馬がボードのすみをくわえて持つ', 'all'],
    ['stand', '馬がボード発表', '立った馬がボードを持つ（下は脚だけ見える）', 'all'],
    ['banner', '横断幕', '馬がボードを持って走ってくる', 'all'],
    ['stamp', '蹄のハンコ', '的中のとき、数字のない所に「的中」スタンプをドン', 'hit'],
    ['flower', 'お花が咲く', 'ボードのまわりにお花が咲く（暗いテーマは色を合わせる）', 'all'],
    ['pop', 'ぽよん', '下から出てきて、着地でぷるんと弾む', 'all'],
    ['drop', 'ドスン', '上から落ちてきて、少しつぶれて戻る', 'all'],
    ['flip', 'カードめくり', '裏向きで出てきて、くるっと表になる', 'all'],
    ['slide', 'すべり込み', '横からシュッと入って、ピタッと止まる', 'all'],
    ['float', 'ふわふわ', '出たあと、ゆっくり上下に浮く', 'all'],
    ['thump', '大きな的中', 'デカ的中から上のとき、ボードが「ドン！」と1回跳ねる', 'big'],
    ['droop', 'ハズレ', 'ハズレのとき、少しだけ傾いて、しょんぼり', 'miss'],
    ['rise', '出世馬', '連続で当たると、ボードのまわりの飾りが豪華になっていく', 'hit'],
    ['carry', 'ボードを持つ馬', '馬がうしろからボードを持って、下から出てくる', 'all']
  ].map(function (r, i) { return { no: i + 1, id: r[0], name: r[1], desc: r[2], when: r[3], need: BOARD_NEED[i] }; });

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
  function owned(events, what) {
    var es = events || [], own = false;
    es.forEach(function (e) {
      if (!e || e.kind !== 'unlock' || e.what !== what) return;
      if (e.tx && es.some(function (r) { return r && r.id === 'refund-' + e.tx; })) return;
      own = true;
    });
    return own;
  }
  function boardOwned(events) { return owned(events, 'board'); }
  // 読み込んだ レースの 数 → 解放した 数（0〜22）
  function boardUnlocked(reads) { var n = 0; BOARD_NEED.forEach(function (k) { if ((+reads || 0) >= k) n++; }); return n; }
  // つぎに 解放する もの（全部 解放ずみ なら null）：{ item, need（その 数）, left（あと いくつ）, from（ひとつ前の 数）}
  function boardNext(reads) {
    var n = boardUnlocked(reads); if (n >= BOARD_ITEMS.length) return null;
    var it = BOARD_ITEMS[n];
    return { item: it, need: it.need, left: it.need - (+reads || 0), from: n ? BOARD_NEED[n - 1] : 0 };
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
  // 出世馬の 飾りの 段（第4.91版・まさちゃんの 指定）：1回目＝クラッカーと花束・2回目＝金メダルとスポットライト・3回目＝トロフィーと金粉・
  //   4〜7回目＝黄金の どでかい冠と 金の 札束（大量）・8回目から＝幻の 馬（咆哮・ボードが 飛んで いく・暗い 雷 3秒 → ボードが もどる）→ 冠と 札束
  function riseTier(streak) { var k = +streak || 0; return k <= 0 ? 0 : k >= 8 ? 8 : k >= 4 ? 4 : k; }

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
    BOARD: BOARD, BOARD_NEED: BOARD_NEED, BOARD_ITEMS: BOARD_ITEMS, boardOwned: boardOwned, boardUnlocked: boardUnlocked, boardNext: boardNext, riseTier: riseTier, owned: owned,
    WALLPACK: WALLPACK, packOwned: packOwned, packUnlocked: packUnlocked, packNext: packNext,
    missions: missions, missionAt: missionAt, WALL_MISSIONS: WALL_MISSIONS, wallMissions: wallMissions, wallMissionEvents: wallMissionEvents, wallCount: wallCount, raceKey: raceKey, sameRace: sameRace, findPaid: findPaid, vnorm: vnorm, addDays: addDays, iso: iso };
  root.TengelPoints = API;
  if (typeof module !== 'undefined' && module.exports) module.exports = API;
})(typeof window !== 'undefined' ? window : globalThis);
