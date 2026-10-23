// ===== 画像の読み取り（アプリ版）：端末の中で読んだ文字（Apple の Vision）から、オッズ画面の表を組み立てる =====
// 入力：画像ごとの行の配列 [{ text, x, y, w, h }]（位置は画像の左上が原点・0〜1）
// 出力：Web版の読み取り（Claude）と同じ形 { venue, date, r, dist, surface, baba, n, horses:[{no,tan,fuku}], s1:{combo,odds}, s5, s10 }
// 画面に書かれている数字と文字だけを使う。読めない項目は null（推測や計算で埋めない）。
(function (root) {
  'use strict';
  var BABA = ['不良', '稍重', '重', '良'];
  // 全角→半角、記号のそろえ（ダッシュ・波線・丸数字）
  var CIRCLED = '①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱';
  function norm(s) {
    s = String(s == null ? '' : s).normalize('NFKC');
    s = s.replace(/[①-⑱]/g, function (c) { return ' ' + (CIRCLED.indexOf(c) + 1) + ' '; });
    s = s.replace(/[‐‑‒–—―−－→⇒➡▶►＞>]/g, '-').replace(/(\d)\s*ー\s*(?=\d)/g, '$1-').replace(/[〜～~]/g, '~').replace(/[：]/g, ':').replace(/倍/g, ' ');
    return s.replace(/\s+/g, ' ').trim();
  }
  var RE = {
    int: /^\d{1,3}$/,
    dec: /^\d{1,3}(?:,\d{3})*\.\d{1,2}$/,
    range: /^(\d{1,3}(?:,\d{3})*\.\d{1,2})\s*[-~]\s*(\d{1,3}(?:,\d{3})*\.\d{1,2})$/,
    combo: /^(\d{1,2})\s*-\s*(\d{1,2})\s*-\s*(\d{1,2})$/,
    dash: /^[-~]$/
  };
  function num(t) { return parseFloat(String(t).replace(/,/g, '')); }
  // 1つの文字列をトークンに分ける（「5ホース」→「5」「ホース」、「第9競走」→「第」「9」「競走」、「1.1-」「1.3」→「1.1」「-」「1.3」）
  // 範囲（1.1-1.3）と組番（6-2-10）はそのまま1つ
  function tokens(text) {
    var s = norm(text).replace(/(\d)([^\d.,\-~\s])/g, '$1 $2').replace(/([^\d.,\-~\s])(\d)/g, '$1 $2')
      .replace(/(\d)-(?=\s|$)/g, '$1 -').replace(/(^|\s)-(?=\d)/g, '$1- ');
    return s.split(' ').map(function (t) { return t.replace(/^[.,]+|[.,]+$/g, ''); }).filter(Boolean);
  }
  function kind(t) {
    if (RE.range.test(t)) return 'range';
    if (RE.combo.test(t)) return 'combo';
    if (RE.dec.test(t)) return 'dec';
    if (RE.int.test(t)) return 'int';
    if (RE.dash.test(t)) return 'dash';
    return 'text';
  }
  // 行（同じ高さに並んでいる文字）にまとめる
  function rows(lines) {
    var items = (lines || []).filter(function (l) { return l && l.text != null && norm(l.text); }).map(function (l) {
      var h = +l.h || 0.01;
      return { text: norm(l.text), x: +l.x || 0, y: +l.y || 0, w: +l.w || 0, h: h, yc: (+l.y || 0) + h / 2 };
    }).sort(function (a, b) { return a.yc - b.yc; });
    var out = [];
    items.forEach(function (it) {
      var r = out.length ? out[out.length - 1] : null;
      if (r && Math.abs(it.yc - r.yc) <= 0.55 * Math.max(it.h, r.h)) { r.items.push(it); r.yc = (r.yc * (r.items.length - 1) + it.yc) / r.items.length; r.h = Math.max(r.h, it.h); }
      else out.push({ yc: it.yc, h: it.h, items: [it] });
    });
    out.forEach(function (r) {
      r.items.sort(function (a, b) { return a.x - b.x; });
      r.text = r.items.map(function (i) { return i.text; }).join(' ');
      r.toks = [];
      r.items.forEach(function (i) {
        var ts = tokens(i.text), joined = ts.join(' '), len = Math.max(1, joined.length), off = 0;
        ts.forEach(function (t) {
          var x = i.x + i.w * off / len, xe = i.x + i.w * (off + t.length) / len;
          r.toks.push({ t: t, k: kind(t), x: x, xe: xe }); off += t.length + 1;
        });
      });
    });
    return out;
  }

  // ---- レース情報（開催場・日付・R・距離・ダ芝・馬場・頭数） ----
  var STOP = ['ダート', 'ダ', '芝', '良', '稍重', '重', '不良', '馬場', '発走', '天候', '晴', '曇', '雨', '小雨', '雪', 'オッズ', '単勝', '複勝', '馬連', '馬単', 'ワイド', '出馬表', '結果', '人気', '締切', '確定', '本日', '今日', '明日', '昨日', '前日', '当日'];
  function header(rs, all) {
    var H = { venue: null, date: null, r: null, dist: null, surface: null, baba: null, n: null };
    var text = all.join('\n');
    var m;
    // R（レース番号）
    var rPat = [/第\s*(\d{1,2})\s*(?:競走|レース|R)/, /(?:^|[^\d.])(\d{1,2})\s*R(?![A-Za-z])/, /(?:^|[^\d.])(\d{1,2})\s*レース/];
    for (var i = 0; i < rPat.length && H.r == null; i++) {
      var re = new RegExp(rPat[i].source, 'g');
      while ((m = re.exec(text))) { var r = +m[1]; if (r >= 1 && r <= 12) { H.r = r; break; } }
    }
    // 開催場：R の前の短い言葉（「○○競馬場 9R」「○○ 第9競走」）。名前の一覧は持たない（画面に書いてあるものだけ）
    if ((m = /([一-龥ぁ-んァ-ヶ]{2,5}?)(?:競馬場|競馬)?\s*(?:第)?\s*\d{1,2}\s*(?:R(?![A-Za-z])|競走|レース)/.exec(text))) {
      var v = m[1].replace(/^(第|ダート|ダ|芝)/, '');
      if (v.length >= 2 && STOP.indexOf(v) < 0 && !/(オッズ|人気|単勝|複勝|馬場|曜$|回$|日$)/.test(v)) H.venue = v;
    }
    // 日付
    if ((m = /(20\d{2})\s*[年/.\-]\s*(\d{1,2})\s*[月/.\-]\s*(\d{1,2})/.exec(text))) H.date = m[1] + '-' + pad(m[2]) + '-' + pad(m[3]);
    else if ((m = /(\d{1,2})\s*月\s*(\d{1,2})\s*日/.exec(text)) || (m = /(?:^|[^\d/.])(\d{1,2})\/(\d{1,2})\s*[(（]?\s*[月火水木金土日]/.exec(text))) {
      var mo = +m[1], dy = +m[2];
      if (mo >= 1 && mo <= 12 && dy >= 1 && dy <= 31) {
        var now = new Date(), y = now.getFullYear(), d = new Date(y, mo - 1, dy);
        if (d - now > 60 * 86400000) y -= 1;
        H.date = y + '-' + pad(mo) + '-' + pad(dy);
      }
    }
    // 距離・ダ芝（「ダ1400m」「芝 1,600m」「1200m」）
    var dre = /(ダート|ダ|芝|障害|障)?\s*(\d{1,2},?\d{3})\s*(?:m|M|ｍ|メートル)(?![a-zA-Z])/g;
    while ((m = dre.exec(text))) {
      var dist = +m[2].replace(',', '');
      if (dist >= 800 && dist <= 4000) { H.dist = dist; if (m[1]) H.surface = /芝/.test(m[1]) ? '芝' : /ダ/.test(m[1]) ? 'ダ' : null; break; }
    }
    if (H.dist == null && (m = /(ダート|ダ|芝)\s*(\d{4})(?!\d)/.exec(text))) { var d2 = +m[2]; if (d2 >= 1000 && d2 <= 4000) { H.dist = d2; H.surface = /芝/.test(m[1]) ? '芝' : 'ダ'; } }
    if (H.surface == null && H.dist != null) { if (/ダート/.test(text)) H.surface = 'ダ'; else if (/(^|[^぀-ヿ一-龥])芝([^぀-ヿ一-龥]|$)/m.test(text)) H.surface = '芝'; }
    // 馬場（「馬場：良」「ダート 良」「(稍重)」か、単独の語）
    var bpat = [/馬場(?:状態)?\s*[:：]?\s*(不良|稍重|重|良)/, /(?:ダート|ダ|芝)\s*[:：・]?\s*(不良|稍重|重|良)(?![一-龥])/, /[（(]\s*(不良|稍重|重|良)\s*[)）]/];
    for (var j = 0; j < bpat.length && !H.baba; j++) { if ((m = bpat[j].exec(text))) H.baba = m[1]; }
    if (!H.baba) {
      rs.forEach(function (r) { if (H.baba) return; r.toks.forEach(function (t) { if (!H.baba && BABA.indexOf(t.t) >= 0) H.baba = t.t; }); });
    }
    // 頭数
    if ((m = /(\d{1,2})\s*頭/.exec(text))) { var n = +m[1]; if (n >= 2 && n <= 18) H.n = n; }
    // 発走時刻（「発走 18:05」「18:05 発走」。なければ 9:00〜21:59 の時刻が1つだけのとき）：同じレースの読み直しの見分けに使う
    H.start = null;
    if ((m = /発走\s*[:：]?\s*(\d{1,2}):(\d{2})/.exec(text)) || (m = /(\d{1,2}):(\d{2})\s*発走/.exec(text))) H.start = pad(m[1]) + ':' + m[2];
    else {
      var times = [], tre = /(?:^|[^\d:])(\d{1,2}):(\d{2})(?![\d:])/g;
      while ((m = tre.exec(text))) { var hh = +m[1], mm = +m[2]; if (hh >= 9 && hh <= 21 && mm <= 59) times.push(pad(hh) + ':' + m[2]); }
      if (times.length === 1) H.start = times[0];
    }
    // レース名（「第9競走 ○○特別」のように、R のあとに続く言葉。ない・読めないときは null。推測はしない）
    H.rname = null;
    if ((m = /(?:第\s*\d{1,2}\s*(?:競走|レース)|\d{1,2}\s*R(?![A-Za-z]))[^\S\n]+([^\s　]{2,20}(?:[^\S\n]+(?!ダ|芝|障|\d|発走|馬場)[^\s　]{1,12})?)/.exec(text))) {
      var nm = m[1].replace(/\s+/g, '');
      var bad = /^(ダート|ダ|芝|障害)?\d|^(発走|馬場|天候|単勝|複勝|馬連|馬単|ワイド|3連|オッズ|人気|出馬表|結果|締切|確定|頭|m)/.test(nm) || /(頭|m|倍|分|時|円)$/.test(nm) || BABA.indexOf(nm) >= 0 || STOP.indexOf(nm) >= 0;
      if (!bad && /[一-龥ぁ-んァ-ヶA-Za-z]/.test(nm)) H.rname = nm;
    }
    return H;
  }
  function pad(x) { return String(+x).padStart(2, '0'); }

  // ---- 単勝・複勝の表 ----
  // 行の形：[人気] [枠] 馬番 馬名… 単勝 複勝（1.1-1.3 ／ 1.1 1.3 ／ 1.1）[人気]
  function horses(rs) {
    // 見出し（単勝・複勝の位置）
    var colTan = null, colFuku = null;
    rs.forEach(function (r) {
      r.toks.forEach(function (t) {
        if (t.t === '単勝' && colTan == null) colTan = (t.x + t.xe) / 2;
        if (t.t === '複勝' && colFuku == null) colFuku = (t.x + t.xe) / 2;
      });
    });
    var cand = [], fukuOnly = {};
    rs.forEach(function (r) {
      var tk = r.toks, lead = [], i = 0;
      if (hasCombo(tk)) return;   // 3連単などの組番の行
      while (i < tk.length && tk[i].k === 'int') { lead.push(+tk[i].t); i++; }
      if (!lead.length) return;
      // 馬番は、先頭に並ぶ整数のいちばん右（[人気] [枠] 馬番 の順で出るので）。枠と馬番がくっついて読めたとき（「47」）は後ろを馬番にする
      var no = lead[lead.length - 1];
      if (no > 18 && lead.length === 1) { var sn = String(no); no = sn.length === 2 ? +sn[1] : +sn.slice(1); }
      if (no < 1 || no > 18) return;
      var vals = [], scratched = false;
      for (; i < tk.length; i++) {
        var t = tk[i];
        if (t.k === 'range') { vals.push({ k: 'range', v: t.t.replace(/\s/g, '').replace('~', '-').replace(/,/g, ''), x: t.x }); }
        else if (t.k === 'dec') { vals.push({ k: 'dec', v: num(t.t), s: t.t.replace(/,/g, ''), x: t.x }); }
        else if (t.k === 'dash' && vals.length && vals[vals.length - 1].k === 'dec' && tk[i + 1] && tk[i + 1].k === 'dec') {
          var a = vals.pop(); vals.push({ k: 'range', v: a.s + '-' + tk[i + 1].t.replace(/,/g, ''), x: a.x }); i++;
        }
        else if (/取消|除外|中止/.test(t.t)) scratched = true;
      }
      if (scratched) { cand.push({ no: no, scratched: true }); return; }
      if (!vals.length) return;
      if (vals.length === 1 && vals[0].k === 'range') { fukuOnly[no] = fukuOnly[no] || vals[0].v; return; }   // 複勝だけの行（別の表）
      cand.push({ no: no, vals: vals, lead: lead.length });
    });
    var live = cand.filter(function (c) { return !c.scratched; });
    if (live.length < 2) return null;
    // 斤量（55.0 など）が単勝の前に写っているときは外す（半数以上の行で、最初の数が 49〜63 の .0/.5）
    var wt = live.filter(function (c) { var v = c.vals[0]; return v.k === 'dec' && v.v >= 49 && v.v <= 63 && (v.v * 2) % 1 === 0 && c.vals.length >= 2; }).length;
    if (wt >= Math.ceil(live.length * 0.6)) live.forEach(function (c) { var v = c.vals[0]; if (v.k === 'dec' && v.v >= 49 && v.v <= 63 && c.vals.length >= 2) c.vals.shift(); });
    var out = [];
    live.forEach(function (c) {
      var vals = c.vals, tan = null, fuku = '';
      if (colTan != null && colFuku != null && vals.length >= 2) {
        // 見出しの位置に近いものを使う
        var near = function (x) { var best = null; vals.forEach(function (v) { var d = Math.abs(v.x - x); if (!best || d < best.d) best = { v: v, d: d }; }); return best && best.v; };
        var vt = near(colTan), vf = near(colFuku);
        if (vt && vt.k === 'dec') tan = vt.v;
        if (vf && vf !== vt) fuku = vf.k === 'range' ? vf.v : vf.s;
      }
      if (tan == null) {
        var first = vals[0];
        if (first.k === 'dec') tan = first.v;
        else if (first.k === 'range' && vals.length === 1) return;   // 単勝が読めていない
        var rest = vals.slice(1);
        if (rest.length) {
          if (rest[0].k === 'range') fuku = rest[0].v;
          else if (rest.length >= 2 && rest[0].k === 'dec' && rest[1].k === 'dec' && rest[1].v >= rest[0].v) fuku = rest[0].s + '-' + rest[1].s;
          else if (rest[0].k === 'dec') fuku = rest[0].s;
        }
      }
      if (tan == null || !(tan >= 1) || tan > 9999) return;
      if (!fuku && fukuOnly[c.no]) fuku = fukuOnly[c.no];
      out.push({ no: c.no, tan: tan, fuku: fuku });
    });
    // 同じ馬番が2つ以上あったら、その表は信用しない（別の表を読んでいる）
    var seen = {}, dup = false;
    out.forEach(function (h) { if (seen[h.no]) dup = true; seen[h.no] = 1; });
    if (dup) return null;
    out.sort(function (a, b) { return a.no - b.no; });
    if (out.length < 2) return null;
    out.scratched = cand.filter(function (c) { return c.scratched; }).length;   // 取消・除外の馬の数（出走頭数は取消を除いた数）
    return out;
  }

  function hasCombo(tk) {
    for (var i = 0; i < tk.length; i++) {
      if (tk[i].k === 'combo') return true;
      if (tk[i].k === 'int' && tk[i + 1] && tk[i + 1].k === 'dash' && tk[i + 2] && tk[i + 2].k === 'int' && tk[i + 3] && tk[i + 3].k === 'dash' && tk[i + 4] && tk[i + 4].k === 'int') return true;
    }
    return false;
  }

  // ---- 3連単の人気順（順位 組番 オッズ） ----
  function trifecta(rs) {
    var list = [];
    rs.forEach(function (r, ri) {
      var tk = r.toks, i, combo = null, rank = null, odds = null;
      for (i = 0; i < tk.length; i++) {
        var t = tk[i];
        if (t.k === 'combo') { var m = RE.combo.exec(t.t); combo = [+m[1], +m[2], +m[3]]; if (i > 0 && tk[i - 1].k === 'int') rank = +tk[i - 1].t; i++; break; }
        if (t.k === 'int' && tk[i + 1] && tk[i + 1].k === 'dash' && tk[i + 2] && tk[i + 2].k === 'int' && tk[i + 3] && tk[i + 3].k === 'dash' && tk[i + 4] && tk[i + 4].k === 'int') {
          combo = [+t.t, +tk[i + 2].t, +tk[i + 4].t]; if (i > 0 && tk[i - 1].k === 'int') rank = +tk[i - 1].t; i += 5; break;
        }
      }
      if (!combo) return;
      if (combo.some(function (x) { return x < 1 || x > 18; }) || new Set(combo).size !== 3) return;
      for (; i < tk.length; i++) { if (tk[i].k === 'dec') { odds = num(tk[i].t); break; } }
      if (odds == null || !(odds >= 1)) return;
      list.push({ rank: rank, combo: combo.join('-'), odds: odds, row: ri });
    });
    if (!list.length) return null;
    var ranked = list.filter(function (x) { return x.rank != null && x.rank >= 1 && x.rank <= 500; });
    var byRank = {};
    if (ranked.length >= 3) ranked.forEach(function (x) { if (!byRank[x.rank]) byRank[x.rank] = x; });
    else { list.slice().sort(function (a, b) { return a.odds - b.odds || a.row - b.row; }).forEach(function (x, k) { byRank[k + 1] = x; }); }
    var pick = function (k) { var x = byRank[k]; return x ? { combo: x.combo, odds: x.odds } : null; };
    return { s1: pick(1), s5: pick(5), s10: pick(10), count: list.length, ranked: ranked.length >= 3 };
  }

  function parseOne(lines) {
    var rs = rows(lines);
    var all = rs.map(function (r) { return r.text; });
    var H = header(rs, all);
    var hs = horses(rs), tri = trifecta(rs);
    return { venue: H.venue, date: H.date, r: H.r, dist: H.dist, surface: H.surface, baba: H.baba, n: H.n, start: H.start, rname: H.rname, horses: hs, tri: tri, lines: (lines || []).length };
  }
  // 画像（1〜3枚）をまとめる：項目ごとに最初に読めたもの。単勝の表は馬の数がいちばん多い画像、3連単は人気順の行がいちばん多い画像
  function parse(images) {
    var docs = (images || []).map(parseOne);
    var D = { venue: null, date: null, r: null, dist: null, surface: null, baba: null, n: null, start: null, rname: null, horses: null, s1: null, s5: null, s10: null };
    ['venue', 'date', 'r', 'dist', 'surface', 'baba', 'n', 'start', 'rname'].forEach(function (k) { docs.forEach(function (d) { if (D[k] == null && d[k] != null) D[k] = d[k]; }); });
    var best = null; docs.forEach(function (d) { if (d.horses && (!best || d.horses.length > best.length)) best = d.horses; });
    if (best) {
      D.horses = best.map(function (h) { return { no: h.no, tan: h.tan, fuku: h.fuku || null }; });
      // 取消・除外の馬があって、表が全部写っている（残り＋取消＝画面の「○頭」）ときの出走頭数は、表に残っている馬の数
      if (best.scratched > 0 && best.length + best.scratched === D.n) D.n = best.length;
    }
    var bt = null; docs.forEach(function (d) { if (d.tri && (!bt || d.tri.count > bt.count)) bt = d.tri; });
    if (bt) { D.s1 = bt.s1; D.s5 = bt.s5; D.s10 = bt.s10; }
    if (D.n == null && D.horses && D.horses.length >= 4) D.n = D.horses.length;
    D._docs = docs.map(function (d) { return { lines: d.lines, horses: d.horses ? d.horses.length : 0, tri: d.tri ? d.tri.count : 0 }; });
    return D;
  }
  var API = { parse: parse, parseOne: parseOne, rows: rows, tokens: tokens, norm: norm };
  root.TengelOCR = API;
  if (typeof module !== 'undefined' && module.exports) module.exports = API;
})(typeof window !== 'undefined' ? window : globalThis);
