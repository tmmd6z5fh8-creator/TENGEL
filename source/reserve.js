// 買い目の 組と 券種ごとの 判定（App Store版・第2弾：アップデート指示書 11.5・11.7・12章）
//   ・build(zones, types, n)：選んだ 馬（ゾーンの 1着側・2着側・3着側）から、券種ごとの 組を 作る（金額は 持たない）
//   ・judge(bets, result, n)：着順（同着・取消／除外・中止）で、組ごとに 的中／不的中／返還 を 出す
//   ・node でも 読める（test_reserve.js）。画面は src.html（NATIVE_APP の ときだけ 使う）
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.TengelReserve = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';
  var TYPES = ['単勝', '複勝', '枠複', '枠単', '馬連', '馬単', 'ワイド', '3連複', '3連単'];
  var ORDERED = { '馬単': true, '枠単': true, '3連単': true };
  var SIZE = { '単勝': 1, '複勝': 1, '枠複': 2, '枠単': 2, '馬連': 2, '馬単': 2, 'ワイド': 2, '3連複': 3, '3連単': 3 };
  var SEP = /[\s.．,，、。\/／\-‐－―ー−~〜・=＝]+/;

  function num(v) { var n = Number(String(v == null ? '' : v).replace(/[０-９]/g, function (c) { return String.fromCharCode(c.charCodeAt(0) - 0xFEE0); })); return isFinite(n) && n > 0 ? Math.floor(n) : null; }
  // 枠番（src.html の wakuOf と 同じ）：8頭以下は 馬番＝枠番。9頭以上は 後ろの 枠から 2頭ずつ
  function waku(no, n) {
    if (!n || n <= 8) return Math.min(no, 8);
    var base = Math.floor(n / 8), rem = n % 8, k = 0;
    for (var f = 1; f <= 8; f++) { k += f > 8 - rem ? base + 1 : base; if (no <= k) return f; }
    return 8;
  }
  function uniq(list) { var seen = {}, out = []; list.forEach(function (c) { var k = c.join('-'); if (!seen[k]) { seen[k] = 1; out.push(c); } }); return out; }
  function cmp(a, b) { for (var i = 0; i < Math.max(a.length, b.length); i++) { var d = (a[i] || 0) - (b[i] || 0); if (d) return d; } return 0; }
  function sortedSet(c) { return c.slice().sort(function (a, b) { return a - b; }); }
  function clean(list) { var out = []; (list || []).forEach(function (v) { var x = num(v); if (x != null && out.indexOf(x) < 0) out.push(x); }); return out; }

  // ---------- 組を 作る ----------
  // zones = [{ a: [1着側の 馬番], b: [2着側の 馬番], t: [3着側の 馬番] | null }]（選んだ 馬だけ・全部 選んで いる 側は ゾーンの 馬 ぜんぶ）
  function build(zones, types, n) {
    var out = {};
    (types || []).forEach(function (t) {
      if (TYPES.indexOf(t) < 0) return;
      var list = [];
      (zones || []).forEach(function (z) {
        var A = clean(z.a), B = clean(z.b), T = clean(z.t);
        if (t === '単勝' || t === '複勝') { A.forEach(function (x) { list.push([x]); }); return; }
        A.forEach(function (x) {
          B.forEach(function (y) {
            if (x === y) return;
            if (t === '馬単') list.push([x, y]);
            else if (t === '馬連' || t === 'ワイド') list.push(sortedSet([x, y]));
            else if (t === '枠単') list.push([waku(x, n), waku(y, n)]);
            else if (t === '枠複') list.push(sortedSet([waku(x, n), waku(y, n)]));
            else if (t === '3連単' || t === '3連複') T.forEach(function (w) { if (w === x || w === y) return; list.push(t === '3連単' ? [x, y, w] : sortedSet([x, y, w])); });
          });
        });
      });
      out[t] = uniq(list).sort(cmp);
    });
    return out;
  }
  function count(bets) { var c = 0; Object.keys(bets || {}).forEach(function (t) { c += (bets[t] || []).length; }); return c; }
  function label(t, c) { return ORDERED[t] ? c.join('→') : c.join('-'); }

  // ---------- 着順 ----------
  // result = { p: [[1着の 馬番…], [2着…], [3着…]], cancel: [取消・除外の 馬番], abandoned: 中止 }
  // 同着は 1つの 着に 2頭 以上。1着に 2頭 なら 次の 馬は 3着（2着の 欄に 入れても 3着に 入れても 同じ）
  function parseNos(s) { return clean(String(s == null ? '' : s).split(SEP)); }
  function groups(result) {
    var gs = [];
    ((result && result.p) || []).forEach(function (g) { var c = clean(g); if (c.length) gs.push(c); });
    return gs;
  }
  // 着順の ならび（同着の 中は どの 順でも よい）。先頭 3頭まで の ならびを 全部
  function orders(result) {
    var gs = groups(result), out = [], seen = {};
    function perms(arr) { if (arr.length <= 1) return [arr]; var r = []; arr.forEach(function (x, i) { perms(arr.slice(0, i).concat(arr.slice(i + 1))).forEach(function (p) { r.push([x].concat(p)); }); }); return r; }
    function walk(gi, acc) {
      if (acc.length >= 3 || gi >= gs.length) { var k = acc.slice(0, 3).join('-'); if (!seen[k]) { seen[k] = 1; out.push(acc.slice(0, 3)); } return; }
      perms(gs[gi]).forEach(function (p) { walk(gi + 1, acc.concat(p)); });
    }
    walk(0, []);
    return out;
  }
  // 着の 数（同着を 数えて 何頭まで わかって いるか）
  function placed(result) { var c = 0; groups(result).forEach(function (g) { c += g.length; }); return c; }
  // 複勝・ワイドの「3着まで」の 馬：着を 順に 足して、3頭（7頭以下の 複勝は 2頭）以上に なる まで
  function topSet(result, limit) { var out = []; var gs = groups(result); for (var i = 0; i < gs.length && out.length < limit; i++) out = out.concat(gs[i]); return out; }

  // ---------- 判定 ----------
  // 返り値：{ state, per: { 券種: { state, hit: [組], refund: [組], n } } }
  //   state：的中（1つでも 当たり）／不的中／返還（組が 全部 返還・中止）／結果待ち（着順が 足りない）／—（買って いない）
  function judge(bets, result, n) {
    var per = {}, states = [];
    var cancel = clean(result && result.cancel), abandoned = !!(result && result.abandoned);
    var ords = orders(result), np = placed(result);
    var fukuLimit = n && n <= 7 ? 2 : 3, fukuSet = topSet(result, fukuLimit), wideSet = topSet(result, 3);
    var pairsU = {}, pairsO = {}, triU = {}, triO = {};
    ords.forEach(function (o) {
      if (o.length >= 2) { pairsO[o[0] + '-' + o[1]] = 1; pairsU[sortedSet([o[0], o[1]]).join('-')] = 1; }
      if (o.length >= 3) { triO[o.join('-')] = 1; triU[sortedSet(o).join('-')] = 1; }
    });
    var wakuPairsU = {}, wakuPairsO = {};
    Object.keys(pairsO).forEach(function (k) { var p = k.split('-').map(Number), w = [waku(p[0], n), waku(p[1], n)]; wakuPairsO[w.join('-')] = 1; wakuPairsU[sortedSet(w).join('-')] = 1; });
    var wideIn = {}; wideSet.forEach(function (x) { wideIn[x] = 1; });
    var fukuIn = {}; fukuSet.forEach(function (x) { fukuIn[x] = 1; });
    var firstIn = {}; (groups(result)[0] || []).forEach(function (x) { firstIn[x] = 1; });
    var need = { '単勝': 1, '複勝': fukuLimit, '枠複': 2, '枠単': 2, '馬連': 2, '馬単': 2, 'ワイド': 3, '3連複': 3, '3連単': 3 };
    function hitOf(t, c) {
      if (t === '単勝') return !!firstIn[c[0]];
      if (t === '複勝') return !!fukuIn[c[0]];
      if (t === '馬単') return !!pairsO[c.join('-')];
      if (t === '馬連') return !!pairsU[sortedSet(c).join('-')];
      if (t === 'ワイド') return !!(wideIn[c[0]] && wideIn[c[1]]);
      if (t === '枠単') return !!wakuPairsO[c.join('-')];
      if (t === '枠複') return !!wakuPairsU[sortedSet(c).join('-')];
      if (t === '3連単') return !!triO[c.join('-')];
      if (t === '3連複') return !!triU[sortedSet(c).join('-')];
      return false;
    }
    // 取消の 馬が 入った 組（枠の 券種は、その 枠の 馬が 全部 取消なら 返還 ※仮：ここでは 馬番の 組で 見るので 枠は 取消の 馬が いる 枠を 返還に しない）
    function refundOf(t, c) {
      if (abandoned) return true;
      if (t === '枠複' || t === '枠単') return false;
      return c.some(function (x) { return cancel.indexOf(x) >= 0; });
    }
    Object.keys(bets || {}).forEach(function (t) {
      var list = bets[t] || [], r = { n: list.length, hit: [], refund: [], state: '—' };
      if (!list.length) { per[t] = r; return; }
      var waiting = !abandoned && np < need[t];
      list.forEach(function (c) {
        if (refundOf(t, c)) { r.refund.push(c); return; }
        if (!waiting && hitOf(t, c)) r.hit.push(c);
      });
      // 当たりが 決まって いれば（取消なしで 着順が 足りて いる）的中。着順が 足りない 時は、取消で 返還に なった 組 以外は 結果待ち
      if (r.hit.length) r.state = '的中';
      else if (r.refund.length === list.length) r.state = '返還';
      else if (waiting) r.state = '結果待ち';
      else r.state = '不的中';
      per[t] = r; states.push(r.state);
    });
    var state = states.indexOf('的中') >= 0 ? '的中' : states.indexOf('結果待ち') >= 0 ? '結果待ち' : states.length && states.every(function (s) { return s === '返還'; }) ? '返還' : states.length ? '不的中' : '—';
    return { state: state, per: per, placed: np, orders: ords };
  }

  return { TYPES: TYPES, ORDERED: ORDERED, SIZE: SIZE, waku: waku, build: build, count: count, label: label, parseNos: parseNos, orders: orders, placed: placed, judge: judge, num: num };
});
