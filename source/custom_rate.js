// 買い目カスタムの %（App Store版・第2弾：アップデート指示書 20.3）
//   いま 使って いる マザーデータの、同じ 区分（層・帯）の レースで、
//   1着の 人気が「1着側で 選んだ 馬の 人気」に 入り、2着の 人気が「2着側で 選んだ 馬の 人気」に 入った 割合（馬単）。
//   3連単は ＋3着の 人気が「3着側で 選んだ 馬の 人気」に 入った 割合。単勝5連予想は 1着の 人気が 選んだ 馬の 人気に 入った 割合。
//   判定の しくみ（engine.js）は さわらない。node でも 読める（test_custom_rate.js）
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.TengelCustomRate = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';
  var ZR = { '人気': [1, 2, 3], '中穴': [4, 5, 6], '大穴': [7, 8, 9], '超大穴': [10, 11, 12] };
  // ゾーンの 名前（「大穴／超大穴」の ように 2つ つながって いても よい）→ 人気順位の 一覧
  function zoneRanks(names) {
    var out = [];
    String(names || '').split(/[／/・,]/).forEach(function (z) { (ZR[z.trim()] || []).forEach(function (r) { if (out.indexOf(r) < 0) out.push(r); }); });
    return out;
  }
  // 馬番 → 人気順位（判定の horses：{ no, rank }）
  function ranksOf(horses, nos) {
    var out = [];
    (nos || []).forEach(function (no) { var h = (horses || []).find(function (x) { return +x.no === +no; }); if (h && h.rank && out.indexOf(h.rank) < 0) out.push(h.rank); });
    return out.sort(function (a, b) { return a - b; });
  }
  function has(list, v) { return v != null && list.indexOf(+v) >= 0; }
  // sel = { a: [人気順位], b: [人気順位], t: [人気順位] | null }
  // 返り値：{ n, hit, n3, hit3 }（n3・hit3 は 3着まで わかる レースでの 3連単）
  function rate(list, kubun, sel, excludeId) {
    var n = 0, hit = 0, n3 = 0, hit3 = 0, A = sel && sel.a || [], B = sel && sel.b || [], T = sel && sel.t;
    (list || []).forEach(function (r) {
      if (!r || !r.inStats || r.kubun !== kubun || (excludeId && r.id === excludeId)) return;
      n++;
      var ok = has(A, r.p1) && has(B, r.p2);
      if (ok) hit++;
      if (T && r.p3 != null) { n3++; if (ok && has(T, r.p3)) hit3++; }
    });
    return { n: n, hit: hit, n3: n3, hit3: hit3 };
  }
  // 単勝5連予想：1着の 人気が 選んだ 馬の 人気に 入った 割合
  function first(list, kubun, ranks, excludeId) {
    var n = 0, hit = 0;
    (list || []).forEach(function (r) {
      if (!r || !r.inStats || r.kubun !== kubun || (excludeId && r.id === excludeId)) return;
      n++; if (has(ranks || [], r.p1)) hit++;
    });
    return { n: n, hit: hit };
  }
  function pct(h, n) { return n ? (Math.round(h / n * 1000) / 10).toFixed(1) + '%' : '—'; }
  return { ZR: ZR, zoneRanks: zoneRanks, ranksOf: ranksOf, rate: rate, first: first, pct: pct, MIN_N: 5 };
});
