/* ===== テンゲルⅢ 判定エンジン（第13改訂版） ===== */
const T = (() => {
  const VERSION = '第13改訂版';
  const ZN = ['人気', '中穴', '大穴', '超大穴'];
  const SYM = 'ABCDEFGHIJKL';
  const P = { // 期間の区分
    kohan: '2026-08-31', shinki: '2026-10-04', dai13: '2026-10-08'
  };

  const round1 = x => Math.round(x * 10 + 1e-7) / 10;
  const ratio = (tan1, s1) => (tan1 > 0 && s1 > 0) ? round1(s1 / tan1) : null;
  const zoneOf = rank => {
    if (!rank || rank < 1) return null;
    if (rank <= 3) return '人気';
    if (rank <= 6) return '中穴';
    if (rank <= 9) return '大穴';
    if (rank <= 12) return '超大穴';
    return '対象外';
  };
  const period = d => !d ? '' : d < P.kohan ? '前半' : d < P.shinki ? '後半' : d < P.dai13 ? '新規' : '第13新規';

  // ゾーン定義
  const Z = (a, b, label, opt = {}) => ({ a, b, label: label || (a + '→' + b.join('／')), ...opt });
  const SETS = {
    A: [Z('人気', ['人気']), Z('人気', ['中穴'])],
    B: [Z('中穴', ['人気']), Z('人気', ['大穴'])],
    C0: [Z('人気', ['人気']), Z('人気', ['中穴'])],
    C1: [Z('人気', ['大穴']), Z('中穴', ['中穴'], null, { prov: true }), Z('大穴', ['人気'])],
    C2: [Z('人気', ['大穴', '超大穴']), Z('中穴', ['大穴', '超大穴']), Z('大穴', ['人気'])]
  };
  const THIRD = {
    A: [['人気', '中穴'], ['人気', '中穴']],
    B: [['人気', '大穴'], ['人気', '大穴']],
    C0: null,
    C1: [['人気', '中穴'], ['人気', '大穴'], ['人気', '中穴']],
    C2: [['人気', '中穴'], ['人気', '超大穴'], ['人気', '中穴']]
  };
  const THIRD_PROV = { A: [false, false], B: [true, true], C0: null, C1: [false, true, false], C2: [false, true, false] };
  // 旧本線（第12の帯）は買い目編集の影響を受けない固定の定義
  const OLD = {
    '非該当': [Z('人気', ['人気']), Z('人気', ['中穴'])],
    '第1段階': [Z('人気', ['大穴']), Z('中穴', ['中穴'], null, { prov: true }), Z('大穴', ['人気'])],
    '第2段階': [Z('人気', ['大穴', '超大穴']), Z('中穴', ['大穴', '超大穴']), Z('大穴', ['人気'])]
  };
  const KUBUN_LABEL = { A: 'A層（固定）', B: 'B層（固定）', C0: 'C層・非該当', C1: 'C層・第1段階', C2: 'C層・第2段階' };

  // ===== 買い目編集（まさちゃんのカスタム） =====
  // 設定の形：{ A: [{ a:'人気', b:['人気'], t:['人気','中穴'] }, …], B: …, C0: …, C1: …, C2: … }
  // t（3着）が空＝その買い目の3着は見送り
  const KEYS = ['A', 'B', 'C0', 'C1', 'C2'];
  const MAXZ = 6;
  const DEFAULT_CFG = {};
  for (const k of KEYS) DEFAULT_CFG[k] = SETS[k].map((z, i) => ({ a: z.a, b: [...z.b], t: THIRD[k] ? [...THIRD[k][i]] : [] }));
  const DEF_SETS = {}, DEF_PROV = {};
  for (const k of KEYS) { DEF_SETS[k] = SETS[k].map(z => ({ ...z, b: [...z.b] })); DEF_PROV[k] = THIRD_PROV[k] ? [...THIRD_PROV[k]] : null; }
  const CUSTOM = { A: false, B: false, C0: false, C1: false, C2: false };
  const ordZ = arr => ZN.filter(z => (arr || []).includes(z));
  function normRow(r) {
    if (!r || !ZN.includes(r.a)) return null;
    const b = ordZ(r.b); if (!b.length) return null;
    return { a: r.a, b, t: ordZ(r.t) };
  }
  const sameRow = (x, y) => x.a === y.a && x.b.join() === y.b.join() && x.t.join() === y.t.join();
  const copyCfg = c => { const o = {}; for (const k of KEYS) o[k] = c[k].map(r => ({ a: r.a, b: [...r.b], t: [...r.t] })); return o; };
  function cleanCfg(cfg) {
    const o = {};
    for (const k of KEYS) {
      const rows = cfg && Array.isArray(cfg[k]) ? cfg[k].map(normRow).filter(Boolean).slice(0, MAXZ) : [];
      o[k] = rows.length ? rows : DEFAULT_CFG[k].map(r => ({ a: r.a, b: [...r.b], t: [...r.t] }));
    }
    return o;
  }
  function isDefaultRows(k, rows) { const d = DEFAULT_CFG[k]; return rows.length === d.length && rows.every((r, i) => sameRow(r, d[i])); }
  let CFG = copyCfg(DEFAULT_CFG);
  function setZones(cfg) {
    CFG = cleanCfg(cfg);
    for (const k of KEYS) {
      const rows = CFG[k];
      CUSTOM[k] = !isDefaultRows(k, rows);
      const zs = rows.map(r => {
        const d = DEF_SETS[k].find(z => z.a === r.a && z.b.join() === r.b.join());
        return Z(r.a, r.b, null, d && d.prov ? { prov: true } : {});
      });
      SETS[k].splice(0, SETS[k].length, ...zs);
      if (!rows.some(r => r.t.length)) { THIRD[k] = null; THIRD_PROV[k] = null; }
      else {
        THIRD[k] = rows.map(r => [...r.t]);
        THIRD_PROV[k] = rows.map(r => { const i = DEFAULT_CFG[k].findIndex(x => sameRow(x, r)); return i >= 0 && DEF_PROV[k] ? !!DEF_PROV[k][i] : false; });
      }
    }
    return CFG;
  }
  const getZones = () => copyCfg(CFG);
  const isCustom = k => k ? !!CUSTOM[k] : KEYS.some(x => CUSTOM[x]);
  // ペアの出現数（"人気|中穴" → 回数）から、あるゾーンの出現数を数える
  const zoneCount = (pairs, z) => z.b.reduce((s, b) => s + ((pairs && pairs[z.a + '|' + b]) || 0), 0);
  const LAYER_LABEL = { A: 'A層（堅）', B: 'B層（警戒）', C: 'C層（穴）' };

  function gateRaw(hi, n) {
    if (hi == null || !n) return '非該当';
    if (hi >= 10 && n >= 14) return '第2段階';
    if (hi >= 10 && n >= 9) return '第1段階';
    return '非該当';
  }
  function layerOf(baba, tan1, s1) {
    const hi = ratio(tan1, s1);
    if (baba === '重') return { L: 'A', cond: 1, hi };
    if (s1 >= 62.4) return { L: 'C', cond: 2, hi };
    if (tan1 >= 2.5 && hi >= 16) return { L: 'C', cond: 3, hi };
    if (hi >= 12) return { L: 'B', cond: 4, hi };
    return { L: 'A', cond: 5, hi };
  }
  // 第13の区分
  function classify(x) {
    const { L, cond, hi } = layerOf(x.baba, x.tan1, x.s1);
    const g = gateRaw(hi, x.n);
    let kubun, early = false, honrai = null, c0reason = null;
    if (L === 'A') kubun = 'A';
    else if (L === 'B') kubun = 'B';
    else if (x.r <= 3) { kubun = 'C0'; early = true; honrai = g; c0reason = '序盤R'; }
    else { kubun = g === '第2段階' ? 'C2' : g === '第1段階' ? 'C1' : 'C0'; if (kubun === 'C0') c0reason = 'ゲート条件未達'; }
    // 第12の帯（旧本線）
    let band12;
    if (x.r <= 3) band12 = '非該当';
    else if (L === 'A' && x.baba !== '重') band12 = '非該当';
    else band12 = g;
    const c20 = L === 'C' ? (hi >= 20 ? '比20以上' : '比20未満') : '';
    return { L, cond, hi, gate: g, kubun, early, honrai, c0reason, band12, c20 };
  }
  function zoneHit(set, z1, z2) {
    if (!z1 || !z2) return 0;
    for (let i = 0; i < set.length; i++) if (set[i].a === z1 && set[i].b.includes(z2)) return i + 1;
    return 0;
  }
  // 頭数ごとのゾーン頭数・通り数
  const zsize = (z, n) => {
    const i = ZN.indexOf(z); if (i < 0) return 0;
    return Math.max(0, Math.min(3, n - i * 3));
  };
  const combos = (zone, n) => zone.b.reduce((s, b) => {
    const sa = zsize(zone.a, n), sb = zsize(b, n);
    return s + (zone.a === b ? sa * Math.max(0, sa - 1) : sa * sb);
  }, 0);

  // レコード → 派生値
  function derive(rec) {
    const c = classify(rec);
    const z1 = zoneOf(rec.p1), z2 = zoneOf(rec.p2), z3 = zoneOf(rec.p3);
    const has12 = !!(z1 && z2);
    const set = SETS[c.kubun];
    const hit = has12 ? zoneHit(set, z1, z2) : 0;
    const third = THIRD[c.kubun];
    const has3 = has12 && !!z3;
    const t3 = (hit && third) ? (third[hit - 1] || []) : [];
    const hit3 = (hit && t3.length && has3) ? t3.includes(z3) : null;
    const tri = !!hit3;
    const oset = OLD[c.band12];
    const hit12 = has12 ? zoneHit(oset, z1, z2) : 0;
    const ana = has12 && ([z1, z2].includes('大穴') || [z1, z2].includes('超大穴'));
    const nn = z1 === '人気' && z2 === '人気';
    const anaZone = z => z.a === '大穴' || z.a === '超大穴' || z.b.includes('大穴') || z.b.includes('超大穴');
    const pay = num(rec.umatanPay);
    const inv13 = set.reduce((s, z) => s + combos(z, rec.n), 0) * 100;
    const inv12 = oset.reduce((s, z) => s + combos(z, rec.n), 0) * 100;
    const isOi = (rec.venue || '大井') === '大井';
    return {
      ...rec, ...c, z1, z2, z3, has12, has3, hit, hit3, tri, hit12,
      ana, nn, pair: has12 ? z1 + '→' + z2 : '',
      ninkiIn12: (z1 === '人気' ? 1 : 0) + (z2 === '人気' ? 1 : 0),
      anaHit13: hit ? anaZone(set[hit - 1]) : false,
      hitLabel: hit ? set[hit - 1].label : '',
      hitNoNinki: hit ? (set[hit - 1].a !== '人気' && !set[hit - 1].b.includes('人気')) : false,
      anaHit12: hit12 ? anaZone(oset[hit12 - 1]) : false,
      sup1: z1 === '超大穴',
      per: period(rec.date), isOi,
      // 集計に使うのは「集計対象＝1」で1・2着がわかるレース（どのマザーデータでも同じ。大井以外のレースは集計対象0で入れる）
      inStats: Number(rec.cnt ?? 1) === 1 && has12,
      pay, inv13, inv12,
      ret13: pay != null && hit ? pay : 0,
      ret12: pay != null && hit12 ? pay : 0
    };
  }
  function num(v) { if (v === '' || v == null) return null; const n = Number(v); return isFinite(n) ? n : null; }

  // ===== 集計 =====
  function stats(list, excludeId) {
    const rs = list.filter(r => r.inStats && r.id !== excludeId);
    const zarr = () => Array(MAXZ).fill(0), zsub = () => Array.from({ length: MAXZ }, () => ({ 人気: 0, 中穴: 0, 大穴: 0, 超大穴: 0 }));
    const S = { n: rs.length, k: {}, layer: {}, band12: {}, early: { n: 0, nn: 0, nc: 0, pairs: {} }, c20: {}, ninki: {} };
    for (const k of KEYS) S.k[k] = { n: 0, hit: zarr(), hitTot: 0, nn: 0, ana: 0, n3: 0, t: { 人気: 0, 中穴: 0, 大穴: 0, 超大穴: 0, 対象外: 0 }, hit3n: zarr(), tri3: zarr(), triTot: 0, hitIn3: 0, sub: zsub(), pairs: {} };
    for (const L of ['A', 'B', 'C']) S.layer[L] = { n: 0, ana: 0, nn: 0 };
    for (const b of ['非該当', '第1段階', '第2段階']) S.band12[b] = { n: 0, hit: zarr(), sub: zsub(), pairs: {} };
    for (const c of ['比20以上', '比20未満']) S.c20[c] = { n: 0, ana: 0, sup1: 0, nnnc: 0, hit: 0 };
    for (const i of [0, 1, 2]) S.ninki[i] = { n: 0, 人気: 0, 中穴: 0, 大穴: 0, 超大穴: 0, 対象外: 0 };
    const addPair = (o, r) => { const key = r.z1 + '|' + r.z2; o[key] = (o[key] || 0) + 1; };
    for (const r of rs) {
      const K = S.k[r.kubun];
      K.n++; addPair(K.pairs, r);
      if (r.hit) { K.hit[r.hit - 1]++; K.hitTot++; if (K.sub[r.hit - 1][r.z2] != null) K.sub[r.hit - 1][r.z2]++; }
      if (r.nn) K.nn++; if (r.ana) K.ana++;
      if (r.has3) {
        K.n3++; K.t[r.z3]++;
        if (r.hit && r.hit3 !== null) { K.hitIn3++; K.hit3n[r.hit - 1]++; if (r.tri) { K.tri3[r.hit - 1]++; K.triTot++; } }
        S.ninki[r.ninkiIn12][r.z3]++; S.ninki[r.ninkiIn12].n++;
      }
      const Ly = S.layer[r.L]; Ly.n++; if (r.ana) Ly.ana++; if (r.nn) Ly.nn++;
      const B = S.band12[r.band12]; B.n++; addPair(B.pairs, r);
      const bset = r.band12 === '非該当' ? OLD['非該当'] : OLD[r.band12];
      const bh = zoneHit(bset, r.z1, r.z2);
      if (bh) { B.hit[bh - 1]++; if (B.sub[bh - 1][r.z2] != null) B.sub[bh - 1][r.z2]++; }
      if (r.r <= 3) { S.early.n++; addPair(S.early.pairs, r); if (r.nn) S.early.nn++; if (r.pair === '人気→中穴') S.early.nc++; }
      if (r.L === 'C' && (r.kubun === 'C1' || r.kubun === 'C2')) {
        const C = S.c20[r.c20]; C.n++; if (r.ana) C.ana++; if (r.sup1) C.sup1++; if (r.pair === '人気→人気' || r.pair === '人気→中穴') C.nnnc++; if (r.hit) C.hit++;
      }
    }
    return S;
  }

  const pct = (a, b, d = 1) => b ? (a / b * 100).toFixed(d) + '%' : '—';
  function hantei(K) {
    if (!K || K.n < 5) return { mark: '・【並】', note: '※データ不足', cls: 'nami' };
    const r = K.nn / K.n;
    if (r >= 0.55) return { mark: '⚠️【薄】', note: '回収率が薄い可能性が高い', cls: 'usu' };
    if (r < 0.30) return { mark: '◎【厚】', note: '配当妙味あり', cls: 'atsu' };
    return { mark: '・【並】', note: '標準', cls: 'nami' };
  }

  // ===== 当日判定 =====
  // input: {venue,date,r,dist,surface,baba,n,horses:[{no,tan,fuku}],tan1,s1,s5,s10, s1combo}
  function judge(inp, S, opt = {}) {
    const out = { ok: false, missing: [] };
    const horses = (inp.horses || []).filter(h => h && h.no && h.tan > 0)
      .map(h => ({ no: +h.no, tan: +h.tan, fuku: fukuLow(h.fuku), fukuRaw: h.fuku || '', fukuRange: /[-〜~]/.test(String(h.fuku || '')) }))
      .sort((a, b) => a.tan - b.tan || a.no - b.no);
    horses.forEach((h, i) => { h.rank = i + 1; h.sym = i < 12 ? SYM[i] : 'M'; h.zone = zoneOf(i + 1); });
    const tan1 = horses.length ? horses[0].tan : num(inp.tan1);
    const x = { r: num(inp.r), dist: num(inp.dist), baba: inp.baba || '', n: num(inp.n), tan1, s1: num(inp.s1) };
    if (!x.r) out.missing.push('レース番号');
    if (!x.dist) out.missing.push('距離');
    if (!x.baba) out.missing.push('馬場状態');
    if (!x.n) out.missing.push('出走頭数');
    if (!x.tan1) out.missing.push('単勝1位オッズ');
    if (!x.s1) out.missing.push('3連単1位オッズ');
    if (out.missing.length) return out;
    out.ok = true;
    const venue = (inp.venue || '大井').trim() || '大井';
    const isOi = venue === '大井';
    const c = classify(x);
    const s5 = num(inp.s5), s10 = num(inp.s10);
    const hasJL = x.n >= 10;
    const chuui = s5 == null ? '確認不可' : (hasJL && s5 >= 40 ? '該当' : '非該当');
    const oldSkip = (s5 != null && s5 >= 78) || (s10 != null && s10 >= 110) ? '該当' : '非該当';
    const set = SETS[c.kubun], third = THIRD[c.kubun];
    const zoneNums = z => horses.filter(h => h.zone === z).sort(z === '大穴' || z === '超大穴' ? fukuSort : () => 0).map(h => h.no);
    const fukuUsed = z => { const hs = horses.filter(h => h.zone === z); return hs.length && hs.every(h => h.fuku != null); };
    const nums = {}; for (const z of ZN) nums[z] = zoneNums(z);
    const outside = horses.filter(h => h.rank > 12).map(h => h.no);
    function fukuSort(a, b) {
      const all = horses.filter(h => h.zone === a.zone);
      if (all.every(h => h.fuku != null)) return a.fuku - b.fuku || a.no - b.no;
      return 0;
    }
    Object.assign(out, { venue, isOi, x, c, s5, s10, chuui, oldSkip, horses, nums, outside, fukuUsed, set, third, S,
      surface: inp.surface || 'ダ', date: inp.date || '', s1combo: inp.s1combo || '', s5combo: inp.s5combo || '', s10combo: inp.s10combo || '',
      warnN: horses.length && horses.length !== x.n ? `オッズ入力${horses.length}頭／出走頭数${x.n}頭` : '' });
    out.oldSet = OLD[c.band12];
    out.combosN = set.map(z => combos(z, x.n));
    return out;
  }
  function fukuLow(v) {
    if (v == null || v === '') return null;
    const m = String(v).replace(/[０-９．]/g, ch => String.fromCharCode(ch.charCodeAt(0) - 0xFEE0)).match(/\d+(\.\d+)?/);
    return m ? Number(m[0]) : null;
  }

  return { VERSION, ZN, SETS, THIRD, THIRD_PROV, OLD, KUBUN_LABEL, LAYER_LABEL, KEYS, MAXZ, DEFAULT_CFG, setZones, getZones, cleanCfg, isCustom, isDefaultRows, zoneCount, zoneHit, round1, ratio, zoneOf, period, classify, derive, stats, judge, hantei, pct, combos, zsize, num, P };
})();
if (typeof module !== 'undefined') module.exports = T;
