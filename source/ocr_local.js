// ===== 画像の読み取り（アプリ版）：端末の中で読んだ文字（Apple の Vision）から、オッズ画面の表を組み立てる =====
// 入力：画像ごとの行の配列 [{ text, x, y, w, h }]（位置は画像の左上が原点・0〜1）
// 出力：Web版の読み取り（Claude）と同じ形 { venue, date, r, dist, surface, baba, n, horses:[{no,tan,fuku}], s1:{combo,odds}, s5, s10 }
//       ＋ names：{ 馬番: 馬の名前 }（第4.170版：表の 行に 名前が 写って いる とき だけ。読めなければ null）
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
    //   第4.233版（まさちゃん 11/27 20:20「一枚目を送ってるのに二枚目になる理由を見つけて改善して！」＝11R の 画面が 9R に なった）：
    //   画面の 上の レースの 切りかえの 並び（「9R 10R 11R 12R」：1つの 行に ちがう R が 2つ 以上）は、どれが 選ばれて いるか 字では わからない
    //   （下線や 色 だけ）ので、R と レース名には 使わない。ほかの 行（見出し「11R 2026年11月27日(金)」など）の R を 使う。ほかに なければ null（手で 入れて もらう）
    var rPat = [/第\s*(\d{1,2})\s*(?:競走|レース|R)/, /(?:^|[^\d.])(\d{1,2})\s*R(?![A-Za-z])/, /(?:^|[^\d.])(\d{1,2})\s*レース/];
    var rtext = all.map(function (s) { return tabRow(s, rPat) ? '' : s; }).join('\n');
    for (var i = 0; i < rPat.length && H.r == null; i++) {
      var re = new RegExp(rPat[i].source, 'g');
      while ((m = re.exec(rtext))) { var r = +m[1]; if (r >= 1 && r <= 12) { H.r = r; break; } }
    }
    // 開催場：R の前の短い言葉（「○○競馬場 9R」「○○ 第9競走」）。名前の一覧は持たない（画面に書いてあるものだけ）
    //   第4.233版：開催場を えらぶ 札の 下向きの 印（「○○ ⌄ 9R 10R …」：v・∨・〜 などに 読める）が 間に あっても 読む（日本語と 数字 でない 1〜2字）
    //   第4.239版（まさちゃん 11/28 15:40：出馬表の 画面〈「開催選択へ レース選択へ」の すぐ 下に「1R 2R …」〉で 開催場が「ス選択へ」に なって いた）：
    //   ① 開催の 書き方「5回京都7日」「第8回大井競馬第3日」が あれば その 開催場（いちばん たしか）
    //   ② ない ときは 前の 形（R の 前の 短い 言葉）。リンクや ボタンの 言葉（選択・一覧・開催・「〜へ」）は 開催場に しない
    if ((m = /(?:^|[^\d])\d{1,2}\s*回\s*([一-龥]{2,3}?)(?:競馬場|競馬)?\s*(?:第\s*)?\d{1,2}\s*日/.exec(text)) && STOP.indexOf(m[1]) < 0) H.venue = m[1];
    else if ((m = /([一-龥ぁ-んァ-ヶ]{2,5}?)(?:競馬場|競馬)?\s*(?:[^\s\d一-龥ぁ-んァ-ヶ]{1,2}\s*)?(?:第)?\s*\d{1,2}\s*(?:R(?![A-Za-z])|競走|レース)/.exec(text))) {
      var v = m[1].replace(/^(第|ダート|ダ|芝)/, '');
      if (v.length >= 2 && STOP.indexOf(v) < 0 && !/(オッズ|人気|単勝|複勝|馬場|曜$|回$|日$|選択|一覧|開催|へ$)/.test(v)) H.venue = v;
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
    // 頭数（「12頭」「12頭立て」「全12頭」。第4.233版：「出走頭数：12」「頭数 12」「登録頭数 12」も・まさちゃん 11/27 21:48「出馬数、レース名が抜けやすいから抜けないように改善して！」）
    if ((m = /(\d{1,2})\s*頭(?!\s*数)/.exec(text)) || (m = /頭\s*数\s*[:：]?\s*(\d{1,2})(?![\d.:])/.exec(text))) { var n = +m[1]; if (n >= 2 && n <= 18) H.n = n; }
    // 発走時刻（「発走 18:05」「18:05 発走」。なければ 9:00〜21:59 の時刻が1つだけのとき）：同じレースの読み直しの見分けに使う
    //   第4.227版（まさちゃん 11/26 17:07「レース判定で、画像を読み込んでから、まもなく締め切りレースが締め切りレースになってる！」）：
    //   ・スクショの いちばん 上の iPhone の 時計（英数字と 日付 だけの 字の 時刻：clockless）と、オッズの 時刻（「18:00現在」「更新 18:00」）は 発走に しない
    //     （画面に ほかの 時刻が ないと、スクショを とった 時刻が 発走に なって「発走 ○○ を過ぎている」で 締切済みに なる）
    //   ・「発走時刻 18:05」「発走予定 18:05」も 読む（前は「発走」の すぐ あとの 時刻 だけ）
    H.start = null;
    var tt = clockless(rs);
    if ((m = /発走\s*(?:予定\s*)?(?:時刻|時間)?\s*[:：]?\s*(\d{1,2}):(\d{2})/.exec(tt)) || (m = /(\d{1,2}):(\d{2})\s*発走/.exec(tt))) H.start = pad(m[1]) + ':' + m[2];
    else {
      var times = [], tre = /(?:^|[^\d:])(\d{1,2}):(\d{2})(?![\d:])/g;
      while ((m = tre.exec(tt))) {
        var hh = +m[1], mm = +m[2], te = m.index + m[0].length, ts = te - m[1].length - 3;
        if (/(?:現在|更新)\s*(?:時刻|時間)?\s*[:：]?\s*$/.test(tt.slice(Math.max(0, ts - 12), ts)) || /^\s*(?:現在|時点|更新)/.test(tt.slice(te, te + 6))) continue;   // オッズの 時刻
        if (hh >= 9 && hh <= 21 && mm <= 59) times.push(pad(hh) + ':' + m[2]);
      }
      if (times.length === 1) H.start = times[0];
    }
    // レース名（「第9競走 ○○特別」のように、R のあとに続く言葉。ない・読めないときは null。推測はしない）
    H.rname = null;
    if ((m = /(?:第\s*\d{1,2}\s*(?:競走|レース)|\d{1,2}\s*R(?![A-Za-z]))[^\S\n]+([^\s　]{2,20}(?:[^\S\n]+(?!ダ|芝|障|\d|発走|馬場)[^\s　]{1,12})?)/.exec(rtext))) {
      var nm = m[1].replace(/\s+/g, '');
      var bad = /^(ダート|ダ|芝|障害)?\d|^(発走|馬場|天候|単勝|複勝|馬連|馬単|ワイド|3連|オッズ|人気|出馬表|結果|締切|確定|頭|m)/.test(nm) || /(頭|m|倍|分|時|円)$/.test(nm) || BABA.indexOf(nm) >= 0 || STOP.indexOf(nm) >= 0;
      if (!bad && /[一-龥ぁ-んァ-ヶA-Za-z]/.test(nm)) H.rname = nm;
    }
    // 第4.233版：R の あとに 名前が ない（見出しの 下の 行に レース名：「11R 2026年11月27日(金)」の 下に「あいち県民の日特別 A(1 a)」）ときは、その 行から 読む（nameRow）
    if (!H.rname) H.rname = nameRow(rs, rPat);
    // 締切済みの印（第4.116版・まさちゃん「画像読み取りで締切済みレースは締切済みレースに記録される」）：画面に 発売が 終わった 言葉が あるか。
    //   読めた 言葉を そのまま 返す（判定は src.html：発走時刻を すぎて いる か・この 言葉が あるか）。
    //   「締切前」「オッズは締切前のものです」「締切 18:05」「締切時刻」「締切予定」「締切まで」「締切間近」は 締切の 前・予定の 表示なので 入れない（締切の あとに 続く 字で 見分ける）
    //   第4.227版：締切の 前の 表示（「まもなく締切」など：SOON）が あれば 言葉では 決めない（soon）・「18:03 締切」「締切順」なども 入れない（closedWord）
    var cw = closedWord(rs, all);
    H.closed = cw.word; H.soon = cw.soon;
    return H;
  }
  function pad(x) { return String(+x).padStart(2, '0'); }
  // レース名の 行（第4.233版）：R の 行の すぐ 下（3行まで）で、レース名らしい 言葉（特別・賞・杯・記念・カップ・ステークス・選抜・一般・新馬・未勝利・クラス・C1 など）の ある 行。
  //   R の すぐ 下 2行の うちは 言葉が なくても、日本語 3字 以上で ほかの 項目（発走・距離・頭数・馬場・日付・時刻・券種・ボタンの 字）で ない 行も。
  //   表の 見出し（馬番・馬名・人気とオッズ）より 下は 見ない。R が ない 画面は 上から 表の 見出しまでで、レース名らしい 言葉の ある 行 だけ
  var RN_KW = /(特別|賞|杯|盃|記念|カップ|ステークス|オープン|選抜|特選|一般|新馬|未勝利|勝クラス|クラス|ダービー|オークス|グランプリ|チャンピオン|トロフィー|スプリント|マイル|ジュベナイル|クラシック|チャレンジ|トライアル|ハンデ|重賞|[ABC][1-4]|[(（]G[1-3I]+[)）]|[(（]Jpn?[1-3I]+[)）])/;
  var RN_NG = /(混合|特指|[(（]指定|[[［]指定|定量|別定|馬齢|本賞金|コース|発走|ダート|芝\s*\d|障害|距離|\d\s*m(?![a-z])|\d\s*頭|頭数|天候|馬場|オッズ|人気|単勝|複勝|馬単|馬連|馬複|枠連|枠複|枠単|ワイド|3\s*連|三連|締\s*め?\s*切|発売|LIVE|更新|出走表|出馬表|投票|結果|払戻|TOP|入金|ポイント|メニュー|ログイン|現在|\d{1,2}:\d{2}|\d{4}\s*年|\d{1,2}\s*月\s*\d{1,2}\s*日|\d{1,2}\/\d{1,2}|お気に入り|レース一覧|予想|新聞|競馬場|競馬$|開催|ナイター$)/;
  // 第4.239版：特別で ない レースの 名前（クラス：「3歳以上 2勝クラス」「2歳 新馬」「3歳 未勝利」「3歳以上 オープン」）→ すきまを とって「3歳以上2勝クラス」。
  //   出馬表の 見出し（「12R 3歳以上 2勝クラス」）は 数字で 始まる ので 前は 名前に して いなかった（下の 行の「(混合)(特指) 定量」が 名前に なって いた）
  function className(t) {
    var m = /^([2-4])\s*歳\s*(以上)?\s*(新\s*馬|未\s*勝\s*利|[1-3]\s*勝\s*クラス|オープン)(?![一-龥ぁ-んァ-ヶ])/.exec(String(t || '').trim());
    return m ? (m[1] + '歳' + (m[2] || '') + m[3]).replace(/\s+/g, '') : null;
  }
  function nameRow(rs, pats) {
    var hdr = -1;
    for (var h = 0; h < rs.length && hdr < 0; h++) { var ht = rs[h].text; if (/馬\s*番|馬\s*名/.test(ht) || (/人気/.test(ht) && /オッズ|単勝/.test(ht))) hdr = h; }
    var lim = hdr >= 0 ? hdr : rs.length, ri = -1;
    for (var k = 0; k < lim && ri < 0; k++) { if (!tabRow(rs[k].text, pats) && pats.some(function (p) { return new RegExp(p.source).test(rs[k].text); })) ri = k; }
    var from = ri >= 0 ? ri : 0, to = ri >= 0 ? Math.min(lim, ri + 4) : lim;
    for (var j = from; j < to; j++) {
      var t = rs[j].text;
      if (j === ri) t = t.replace(/第\s*\d{1,2}\s*(?:競走|レース|R)|\d{1,2}\s*R(?![A-Za-z])/g, ' ');      // R の 行は R を とった 残り
      t = t.replace(/\s+/g, ' ').trim();
      if (ri >= 0 && j <= ri + 2 && className(t)) return className(t);      // 第4.239版：R の 行か その 下 2行の クラス
      if (!t || /^\d/.test(t) || RN_NG.test(t) || BABA.indexOf(t) >= 0 || STOP.indexOf(t) >= 0) continue;
      var jp = (t.match(/[一-龥ぁ-んァ-ヶ]/g) || []).length;
      if (jp >= 2 && RN_KW.test(t)) return t.slice(0, 30);
      if (ri >= 0 && j > ri && j <= ri + 2 && jp >= 3 && t.length <= 30) return t;
    }
    return null;
  }
  // レースの 切りかえの 並び（第4.233版）：1つの 行に ちがう レース番号（1〜12）が 2つ 以上（「9R 10R 11R 12R」「1R 締切 2R 締切済 …」）
  function tabRow(s, pats) {
    var seen = {}, k = 0, m;
    pats.forEach(function (p) { var re = new RegExp(p.source, 'g'); while ((m = re.exec(s))) { var v = +m[1]; if (v >= 1 && v <= 12 && !seen[v]) { seen[v] = 1; k++; } } });
    return k >= 2;
  }

  // ---- iPhone の 上の 時計（第4.227版）：スクショの いちばん 上（画像の 上から 4.5% まで）の、英数字と 日付 だけの 字（「17:58」「17:58 5G 87」・iPad の「17:58 11月26日(水)」）の 時刻。
  //   時刻を 読む ときは のぞく（ほかの 日本語の ある 字＝見出し「大井 9R 18:05」「発走 18:05」などは のぞかない）
  function isBar(it) { return it.yc < 0.045 && /\d{1,2}:\d{2}/.test(it.text) && /^[\x20-\x7e年月日曜火水木金土]*$/.test(it.text); }
  function clockless(rs) {
    return rs.map(function (r) { return r.items.map(function (it) { return isBar(it) ? it.text.replace(/\d{1,2}:\d{2}/g, ' ') : it.text; }).join(' '); }).join('\n');
  }

  // ---- 締切済みの 言葉（第4.116版）と 締切の 前の 表示（第4.227版） ----
  //   SOON：締切が まだ 来て いない ことが はっきり 分かる 表示。画面に 1つでも あれば、言葉では 締切済みに しない（ほかの レースの「締切」の 札や メニューの「払戻金」が いっしょに 写って いても）
  //     まもなく締切・間もなく締め切ります・まもなく発売締切・もうすぐ締切／締切まもなく・締切間近・締切直前・締切目前・締切迫る・締切が近い／締切まで あと2分／あと3分で締切・5分後に締切／締め切ります・締切となります
  //     （「締切 まもなく発走」は 締切の あと なので 入れない）。上下 2段や となりの 字に わかれて 読めた とき（「まもなく」の 下に「締切」）も つなげて 見る
  var SOON = new RegExp([
    /(?:ま|間)\s*も\s*(?:な|無)\s*く\s*(?:発売\s*|投票\s*)?締\s*め?\s*切/.source,
    /(?:もう\s*すぐ|そろそろ|いよいよ)\s*(?:発売\s*|投票\s*)?締\s*め?\s*切/.source,
    /締\s*め?\s*切\s*り?\s*(?:が\s*)?(?:(?:ま|間)\s*も\s*(?:な|無)\s*く(?!\s*(?:発走|出走|スタート))|もう\s*すぐ|迫|間\s*近|直\s*前|目\s*前|近\s*[いしづく])/.source,
    /締\s*め?\s*切\s*り?\s*(?:まで|迄)\s*(?:の\s*)?(?:あと|残り|のこり|\d)/.source,
    /(?:あと|残り|のこり)\s*\d{1,3}\s*(?:分|秒)\s*(?:ほど\s*)?(?:で|後\s*に?)\s*(?:発売\s*|投票\s*)?締\s*め?\s*切/.source,
    /\d{1,3}\s*分\s*後\s*に?\s*(?:発売\s*|投票\s*)?締\s*め?\s*切/.source,
    /締\s*め?\s*切\s*り?\s*(?:ま\s*す|[とに]\s*な\s*り\s*ま\s*す)/.source
  ].join('|'));
  //   CLOSED：発売が 終わった 言葉（第4.116版の 表）。さいごの「締切」「発売締切」だけの 言葉は、前後の 字も 見る（bare）：
  //     あとに 前・時刻・予定・まで・時刻（18:05）・順・一覧・案内 など → 入れない／前に 時刻（「18:03 締切」：発走の 時刻の あとは 入れる）・「次の」→ 入れない／
  //     すぐ 下・となりの 字が 時刻や「前」「まで」など（上下 2段の「締切／18:03」）→ 入れない
  var CLOSED = /締\s*切\s*済\s*み?|締\s*め?\s*切\s*り?\s*ました|発売\s*(?:は\s*)?終了|確定\s*オッズ|オッズ\s*確定|最終\s*オッズ|結果\s*確定|払戻金|(?:発売\s*)?締\s*め?\s*切(?!\s*り?\s*(?:前|直前|間近|が\s*近|時刻|時間|予定|まで|迄|[:：]?\s*\d|順|一覧|案内|情報|お知らせ|通知|アラーム|設定|予告))(?:\s*り)?/g;
  var BARE = /^(?:発売\s*)?締\s*め?\s*切(?:\s*り)?$/, AFTER_NG = /^\s*(?:[:：]?\s*\d{1,2}:\d{2}|前|直前|間近|時刻|時間|予定|まで|迄|順|一覧)/;
  // b が a の すぐ 下（横に 重なる）か すぐ 右（行が わかれて 読めた とき）
  function near(a, b) {
    var h = Math.max(a.h, b.h), dy = b.yc - a.yc, ov = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x);
    if (dy > 0.3 * h && dy <= 1.9 * h && ov > 0) return true;
    return Math.abs(dy) <= 0.9 * h && b.x >= a.x + a.w - 0.01 && b.x - (a.x + a.w) <= 0.06;
  }
  function closedWord(rs, all) {
    var text = all.join('\n'), items = [], off = 0;
    rs.forEach(function (r, k) {
      var o = off;
      r.items.forEach(function (it) { items.push({ it: it, s: o, e: o + it.text.length }); o += it.text.length + 1; });
      off += all[k].length + 1;
    });
    var soon = SOON.test(text);
    for (var i = 0; i < items.length && !soon; i++) {
      for (var j = 0; j < items.length && !soon; j++) {
        var A = items[i].it, B = items[j].it;
        if (i !== j && (A.text + B.text).indexOf('切') >= 0 && near(A, B) && SOON.test(A.text + B.text)) soon = true;
      }
    }
    if (soon) return { word: null, soon: true };
    var re = new RegExp(CLOSED.source, 'g'), m;
    while ((m = re.exec(text))) {
      if (BARE.test(m[0]) && !bareOK(m.index)) continue;
      if (/前\s*日/.test(text.slice(Math.max(0, m.index - 8), m.index))) continue;      // 第4.241版：「前日最終オッズ」「前日発売は締め切りました」は 前の 日の 発売（レースは まだ）
      return { word: m[0].replace(/\s+/g, ''), soon: false };
    }
    return { word: null, soon: false };

    function bareOK(p) {
      var before = text.slice(text.lastIndexOf('\n', p - 1) + 1, p), tb = /(\d{1,2}:\d{2})\s*(?:に|で|まで)?\s*$/.exec(before);
      if (tb && !/発走\s*(?:予定\s*)?(?:時刻|時間)?\s*[:：]?\s*$/.test(before.slice(0, tb.index))) return false;   // 「18:03 締切」（「発走 18:05 締切」は 入れる）
      if (/次\s*(?:の|回)?\s*$/.test(before)) return false;                                                        // 「次の締切」
      var q = p + Math.max(0, text.slice(p).search(/締/)), own = null;
      items.forEach(function (x) { if (!own && x.s <= q && q < x.e) own = x.it; });
      if (!own) return true;
      for (var n = 0; n < items.length; n++) {
        var o = items[n].it, ot; if (o === own) continue;
        if (near(own, o) && AFTER_NG.test(o.text)) return false;                                  // すぐ 下・となりが「18:03」「前」「まで」…
        if (near(o, own) && (((ot = /(\d{1,2}:\d{2})\s*(?:に|で|まで)?$/.exec(o.text)) && !/発走\s*(?:予定\s*)?(?:時刻|時間)?\s*[:：]?\s*$/.test(o.text.slice(0, ot.index))) || /次\s*(?:の|回)?$/.test(o.text))) return false;   // すぐ 上・となりが「18:03」「次の」
      }
      return true;
    }
  }

  // ---- 馬番の 列（第4.228版）----
  //   表の 行の 先頭の 整数（[人気] [枠] 馬番）の 数で いちばん 多い 数（L）の 行の、いちばん 右の 整数の 位置（cx）と 幅（cw）。3行 以上 なければ null
  //   list：[{ n：先頭の 整数の 数, x・xe：いちばん 右の 整数の 左と 右 }]
  function med(a) { a = a.slice().sort(function (p, q) { return p - q; }); return a[a.length >> 1]; }
  function numCol(list) {
    var cnt = {};
    list.forEach(function (x) { if (x.n) cnt[x.n] = (cnt[x.n] || 0) + 1; });
    var L = +Object.keys(cnt).sort(function (a, b) { return cnt[b] - cnt[a] || b - a; })[0] || 0;
    var std = list.filter(function (x) { return x.n === L; });
    if (!L || std.length < 3) return null;
    var cw = Math.max(0.008, med(std.map(function (x) { return x.xe - x.x; })));
    return { L: L, cx: med(std.map(function (x) { return (x.x + x.xe) / 2; })), cw: cw, tol: Math.max(0.6 * cw, 0.015) };
  }

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
      var i0 = i;
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
      cand.push({ no: no, vals: vals, lead: lead.length, lx: tk[i0 - 1].x, lxe: tk[i0 - 1].xe });
    });
    // 第4.228版：馬番が 読めず、前の 整数（枠・人気）を 馬番と まちがえた 行は 外す（先頭の 整数が ほかの 行より 少なく、いちばん 右の 整数が 馬番の 列まで とどいて いない）。
    //   外さないと 同じ 馬番が 2つに なって 表 ぜんぶを 使えなく なる。外した 馬は 入力で「読めなかった：単勝の○番」と 出る（gaps で 読み直しも する）。
    //   枠と 馬番が くっついて 読めた「47」は 馬番の 列まで とどいて いる ので 外さない
    var col = numCol(cand.filter(function (c) { return !c.scratched; }).map(function (c) { return { n: c.lead, x: c.lx, xe: c.lxe }; }));
    if (col) cand = cand.filter(function (c) { return c.scratched || c.lead >= col.L || c.lxe >= col.cx - col.cw / 2; });
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

  // ---- 馬の 名前（第4.170版：まさちゃん 2026/11/14「名前は読み込んだ画像から割り出せる？」）----
  //   表の 行「[人気／着順] [枠] 馬番 馬名 …」「1着 6 馬名」から 馬番ごとの 名前を 読む（オッズの 表・出馬表・結果の 表）。画面に 書いて ある 字 だけ（名前の 一覧は 持たない）。
  //   ・名前＝馬番の すぐ あとの 文字（数字が 出る 前まで）の うち、はじめの「カタカナ 2〜18字」（日本の 競走馬の 名前は カタカナ 2〜9字・外国の 馬の カナ書きは もっと 長い ことが ある）。
  //     印（◎○▲ など・（地）（外）など）は とばす。名前の 形で ない 文字が 先に あったら その 行は 名前なし。
  //   ・人の 名前（騎手・調教師）は 読まない：数字（性齢・斤量・オッズ・タイム）より あとの 文字は 見ない・性別の「セン」は 名前に しない。
  //   ・カタカナに 見える 漢字・ひらがな・横線（力→カ・口→ロ・二→ニ・一→ー など）は、ほかが カタカナの とき だけ カタカナに 直す。
  //   ・2頭 以上 読めた とき だけ 返す。同じ 馬番に ちがう 名前が 読めたら その 馬番は 返さない（どちらが 正しいか 分からない）。
  var KATA_FIX = { '力': 'カ', '口': 'ロ', '二': 'ニ', '八': 'ハ', '工': 'エ', '夕': 'タ', '卜': 'ト', '一': 'ー', '千': 'チ', '才': 'オ', 'へ': 'ヘ', 'べ': 'ベ', 'ぺ': 'ペ', 'り': 'リ', '-': 'ー', '~': 'ー' };
  var NAME_STOP = ['セン', 'ダート', 'オッズ', 'ワイド', 'レース', 'コース', 'タイム', 'ハンデ', 'ブリンカー'];
  var RE_MARK = /^(?:[◎○〇◯▲△☆★×✕✓✔・*＊]+|[\[(【]?(?:地|外|父|市|抽|混|指|特|B)[\])】]?)$/;
  function kataName(t) {
    var s = String(t || '').normalize('NFKC').replace(/^[\[(【][^\])】]{1,2}[\])】]/, '').replace(/^[\[(【「『<《]+/, '').replace(/[\[(【「『<《\])】」』>》].*$/, '').replace(/[牡牝騸]$/, '');
    if (s.length < 2 || s.length > 18) return null;
    if ((s.match(/[ァ-ヶー]/g) || []).length < Math.ceil(s.length * 0.6)) return null;
    s = s.replace(/[\s\S]/g, function (c) { return KATA_FIX[c] || c; });
    if (!/^[ァ-ヶ][ァ-ヶー]{1,17}$/.test(s) || NAME_STOP.indexOf(s) >= 0) return null;
    return s;
  }
  // 行の トークン tk の i0 番目（馬番）の あとから 名前を さがす
  function nameAfter(tk, i0) {
    var run = [];
    for (var i = i0 + 1; i < tk.length && tk[i].k === 'text'; i++) run.push(tk[i]);
    for (var s = 0; s < run.length; s++) {
      var t = run[s], best = kataName(t.t), joined = t.t, e = s;
      // 名前が 2つに 分かれて 読めた とき（字の 間の すき間）：すぐ となり（すき間が 1字ぶん より せまい）の カタカナ だけ つなぐ
      while (e + 1 < run.length) {
        var a = run[e], b = run[e + 1], cw = (a.xe - a.x) / Math.max(1, a.t.length);
        if (!(b.x - a.xe < cw * 0.9) || !/^[ァ-ヶー]+$/.test(a.t) || !/^[ァ-ヶー]/.test(b.t)) break;
        var j = kataName(joined + b.t); if (!j) break;
        joined += b.t; best = j; e++;
      }
      if (best) return best;
      if (!RE_MARK.test(t.t)) return null;
    }
    return null;
  }
  function nameTable(rs) {
    var got = {}, bad = {};
    rs.forEach(function (r) {
      var tk = r.toks, i = 0, lead = [], at;
      if (hasCombo(tk)) return;
      while (i < tk.length && tk[i].k === 'int') { lead.push(+tk[i].t); i++; }
      if (!lead.length || lead.length > 3) return;
      var no = lead[lead.length - 1]; at = i - 1;
      if (lead.length === 1 && tk[i] && /^着/.test(tk[i].t) && tk[i + 1] && tk[i + 1].k === 'int') { no = +tk[i + 1].t; at = i + 1; }   // 「1着 6 馬名」
      else if (no > 18 && lead.length === 1) { var sn = String(no); no = sn.length === 2 ? +sn[1] : +sn.slice(1); }
      if (!(no >= 1 && no <= 18)) return;
      var nm = nameAfter(tk, at);
      if (!nm) return;
      if (got[no] && got[no] !== nm) bad[no] = 1; else got[no] = nm;
    });
    Object.keys(bad).forEach(function (k) { delete got[k]; });
    return Object.keys(got).length >= 2 ? got : null;
  }
  // 画像ごとの 名前を まとめる：いちばん 多く 読めた 画像を もとに、ほかの 画像の 名前は まだ ない 馬番 だけ 足す
  function mergeNames(list) {
    var tabs = (list || []).filter(Boolean).sort(function (a, b) { return Object.keys(b).length - Object.keys(a).length; });
    if (!tabs.length) return null;
    var out = {};
    tabs.forEach(function (t) { Object.keys(t).forEach(function (k) { if (!out[k]) out[k] = t[k]; }); });
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
    return { venue: H.venue, date: H.date, r: H.r, dist: H.dist, surface: H.surface, baba: H.baba, n: H.n, start: H.start, rname: H.rname, closed: H.closed, soon: H.soon, horses: hs, tri: tri, names: nameTable(rs), lines: (lines || []).length };
  }
  // 画像（1〜3枚）をまとめる：項目ごとに最初に読めたもの。単勝の表は馬の数がいちばん多い画像、3連単は人気順の行がいちばん多い画像
  function parse(images) {
    var docs = (images || []).map(parseOne);
    var D = { venue: null, date: null, r: null, dist: null, surface: null, baba: null, n: null, start: null, rname: null, closed: null, horses: null, s1: null, s5: null, s10: null, names: null };
    ['venue', 'date', 'r', 'dist', 'surface', 'baba', 'n', 'start', 'rname', 'closed'].forEach(function (k) { docs.forEach(function (d) { if (D[k] == null && d[k] != null) D[k] = d[k]; }); });
    // 第4.227版：どれかの 画像に 締切の 前の 表示（「まもなく締切」など）が あれば、ほかの 画像の 言葉でも 締切済みに しない（同じ レースを つづけて 撮った 写真）
    D.soon = docs.some(function (d) { return d.soon; });
    if (D.soon) D.closed = null;
    var best = null; docs.forEach(function (d) { if (d.horses && (!best || d.horses.length > best.length)) best = d.horses; });
    if (best) {
      D.horses = best.map(function (h) { return { no: h.no, tan: h.tan, fuku: h.fuku || null }; });
      // 取消・除外の馬があって、表が全部写っている（残り＋取消＝画面の「○頭」）ときの出走頭数は、表に残っている馬の数
      if (best.scratched > 0 && best.length + best.scratched === D.n) D.n = best.length;
    }
    var bt = null; docs.forEach(function (d) { if (d.tri && (!bt || d.tri.count > bt.count)) bt = d.tri; });
    if (bt) { D.s1 = bt.s1; D.s5 = bt.s5; D.s10 = bt.s10; }
    if (D.n == null && D.horses && D.horses.length >= 4) D.n = D.horses.length;
    D.names = mergeNames(docs.map(function (d) { return d.names; }));
    D._docs = docs.map(function (d) { return { lines: d.lines, horses: d.horses ? d.horses.length : 0, tri: d.tri ? d.tri.count : 0 }; });
    return D;
  }
  // ---- 結果の画面（着順と払戻）：予約したレースの結果入力に使う（第2弾・12.1 ※仮：見本の画像をもらったら直す） ----
  //  読むもの：1〜3着の馬番（同着も）・取消／除外の馬番・レースの中止・券種ごとの払戻（組番 → 円）
  //  着順の表：「着順 枠 馬番 馬名 …」の行（見出しの「馬番」の位置に近い数字を馬番にする）、見出しがなければ「着順 (枠) 馬番」の数の並び、「1着 6」の形
  //  払戻の表：「単勝 6 240円」「馬単 6-2 1,120円」「3連単 6-2-10 12,340円」…（三連単・枠連 も読む）
  var PAYTYPE = { '単勝': '単勝', '複勝': '複勝', '枠連': '枠複', '枠複': '枠複', '枠単': '枠単', '馬連': '馬連', '馬単': '馬単', 'ワイド': 'ワイド', '3連複': '3連複', '三連複': '3連複', '3連単': '3連単', '三連単': '3連単' };
  var RE_MONEY = /^\d{1,3}(?:,\d{3})+$|^\d{3,7}$/;
  function payType(t) { var k = String(t).replace(/^三/, '3').replace(/\s/g, ''); return PAYTYPE[k] || null; }
  function resultOne(lines) {
    var rs = rows(lines), out = { p: [[], [], []], cancel: [], abandoned: false, pay: {}, places: 0, payRows: 0, names: null };
    out.names = nameTable(rs);   // 第4.170版：着順の 表に 写って いる 馬の 名前（馬番ごと）
    var xNo = null, xWaku = null, inPay = false;
    rs.forEach(function (r) {
      var tk = r.toks, txt = r.text;
      // レースの中止（馬の「競走中止」は別。発走取消・開催中止・レース中止）
      if (/(レース|競走|開催|発走)\s*(中止|取消|取り止め)/.test(txt) && !/\d+\s*着/.test(txt) && !/^\s*\d/.test(txt)) { if (/(開催|レース|発走)/.test(txt)) out.abandoned = true; }
      // 見出し：「馬番」の位置
      var hdr = null; tk.forEach(function (t) { if (/^馬番$/.test(t.t) || t.t === '馬' && tk[tk.indexOf(t) + 1] && tk[tk.indexOf(t) + 1].t === '番') hdr = t; });
      if (hdr && /着/.test(txt)) { xNo = (hdr.x + hdr.xe) / 2; var w = tk.find(function (t) { return /^枠(番)?$/.test(t.t); }); xWaku = w ? (w.x + w.xe) / 2 : null; return; }
      // 払戻の行：先頭が券種
      var ty = tk.length ? payType(tk[0].t) : null;
      if (!ty && tk.length > 1 && tk[0].t === '3' && /^連(単|複)$/.test(tk[1].t)) { ty = PAYTYPE['3' + tk[1].t]; tk = tk.slice(1); }
      if (ty) {
        inPay = true;
        var i = 1, nos = [];
        for (; i < tk.length; i++) { var t = tk[i], pm = /^(\d{1,2})-(\d{1,2})$/.exec(t.t); if (t.k === 'combo') { var m = RE.combo.exec(t.t); nos = [+m[1], +m[2], +m[3]]; i++; break; } if (pm) { nos = [+pm[1], +pm[2]]; i++; break; } if (t.k === 'int' && +t.t >= 1 && +t.t <= 18) { nos.push(+t.t); if (tk[i + 1] && tk[i + 1].k === 'dash') { i++; continue; } i++; break; } if (nos.length) break; }
        var yen = null;
        for (; i < tk.length; i++) { var u = tk[i].t.replace(/円$/, ''); if (RE_MONEY.test(u) && num(u) >= 100 && num(u) % 10 === 0) { yen = num(u); break; } }
        var size = { '単勝': 1, '複勝': 1, '枠複': 2, '枠単': 2, '馬連': 2, '馬単': 2, 'ワイド': 2, '3連複': 3, '3連単': 3 }[ty];
        if (nos.length === size && yen != null) { if (!out.pay[ty]) out.pay[ty] = {}; out.pay[ty][nos.join('-')] = yen; out.payRows++; }
        return;
      }
      if (inPay) return;
      // 着順の行
      var ints = []; tk.forEach(function (t, k) { if (t.k === 'int' && +t.t >= 1 && +t.t <= 18) ints.push({ v: +t.t, k: k, xc: (t.x + t.xe) / 2 }); });
      if (!ints.length) return;
      var scratched = /(取消|除外)/.test(txt) && !/競走中止/.test(txt);
      var place = null, no = null;
      if (tk[ints[0].k + 1] && /^着/.test(tk[ints[0].k + 1].t) && ints.length >= 2) { place = ints[0].v; no = ints[1].v; }   // 「1着 6」
      else if (xNo != null) {
        var cand = ints.slice(); if (ints[0].k === 0 && !scratched) { place = ints[0].v; cand = ints.slice(1); }
        if (cand.length) { var best = cand.reduce(function (a, b) { return Math.abs(b.xc - xNo) < Math.abs(a.xc - xNo) ? b : a; }); no = best.v; }
      } else if (scratched) no = ints[0].k === 0 && ints.length >= 2 ? ints[1].v : ints[0].v;
      else if (ints[0].k === 0) {
        if (ints.length >= 3 && ints[1].k === 1 && ints[2].k === 2 && ints[1].v <= 8) { place = ints[0].v; no = ints[2].v; }
        else if (ints.length >= 2 && ints[1].k === 1) { place = ints[0].v; no = ints[1].v; }
      }
      if (no == null) return;
      if (scratched) { if (out.cancel.indexOf(no) < 0) out.cancel.push(no); return; }
      if (place != null && place >= 1 && place <= 3 && out.p[place - 1].indexOf(no) < 0 && out.p.every(function (g) { return g.indexOf(no) < 0; })) { out.p[place - 1].push(no); out.places++; }
    });
    return out;
  }
  // 画像（1〜3枚）をまとめる：着順はいちばん多く読めた画像、払戻は全部合わせる
  function parseResult(images) {
    var docs = (images || []).map(resultOne), D = { p: [[], [], []], cancel: [], abandoned: false, pay: {}, got: [], names: null };
    D.names = mergeNames(docs.map(function (d) { return d.names; }));   // got（読めた ものの 一覧）には 入れない：名前 だけ 読めた 画面は「読めなかった」の まま
    var best = null; docs.forEach(function (d) { if (!best || d.places > best.places) best = d; });
    if (best && best.places) { D.p = best.p; }
    docs.forEach(function (d) { d.cancel.forEach(function (c) { if (D.cancel.indexOf(c) < 0) D.cancel.push(c); }); if (d.abandoned) D.abandoned = true; Object.keys(d.pay).forEach(function (t) { D.pay[t] = Object.assign(D.pay[t] || {}, d.pay[t]); }); });
    if (D.p[0].length) D.got.push('1着'); if (D.p[1].length) D.got.push('2着'); if (D.p[2].length) D.got.push('3着');
    if (D.cancel.length) D.got.push('取消・除外'); if (D.abandoned) D.got.push('中止');
    var pt = Object.keys(D.pay); if (pt.length) D.got.push('払戻（' + pt.join('・') + '）');
    return D;
  }
  // ---- 読めなかった 馬番の 所（第4.228版）----
  //   単勝の 表で、馬名と 単勝は 読めたのに 前の 馬番が 読めなかった 行（GitHub の Mac の 本物の Vision で、細い 数字の「11」だけ 読まれなかった）。
  //   その 行の 馬番の 所だけ 切り取って もう一度 読む（アプリの 窓口 readText の crop：pwa_shim.js の fixGaps）。
  //   使う 馬番は、読み直しで 画面から 読めた 数字 だけ（行の 順番から 決めない）。読めなければ その 馬は 入れない（入力で「読めなかった」と 知らせる）
  //   gaps(lines) → [{ crop:[x,y,w,h]（その 行の 馬番の 所）, wide:[…]（上と 下の 行の 馬番も 入れた 所・なければ null）, cx, cw, yc, h, have:[読めた 馬番], prev, next, asc }]（多くて 4つ）
  function gaps(lines) {
    var info = [];
    rows(lines).forEach(function (r) {
      var tk = r.toks, i = 0, lead = [];
      if (!tk.length || hasCombo(tk)) return;
      while (i < tk.length && tk[i].k === 'int') { lead.push(tk[i]); i++; }
      if (!tk.slice(i).some(function (t) { return t.k === 'dec'; })) return;      // 単勝（小数）の ない 行は 表の 行で ない
      if (lead.length > 3 || !nameAfter(tk, i - 1)) return;                         // 馬番（または 行の はじめ）の すぐ あとが 馬の 名前の 行 だけ
      var lt = lead[lead.length - 1];
      info.push({ n: lead.length, no: lt ? +lt.t : null, x: lt ? lt.x : null, xe: lt ? lt.xe : null, yc: r.yc, h: r.h, nameX: tk[i].x });
    });
    var col = numCol(info);
    if (!col) return [];
    var num = info.filter(function (x) { return x.n && x.no >= 1 && x.no <= 18 && Math.abs((x.x + x.xe) / 2 - col.cx) <= col.tol; });
    var cand = info.filter(function (x) { return !x.n || (x.n < col.L && x.xe < col.cx - col.cw / 2); });   // 馬番の 列に 数字が ない 行（horses で 外す 行と 同じ）
    if (num.length < 3 || !cand.length) return [];
    var cx = col.cx, cw = col.cw, have = num.map(function (n) { return n.no; });
    var byY = num.slice().sort(function (a, b) { return a.yc - b.yc; });
    var asc = byY.every(function (n, k) { return !k || n.no > byY[k - 1].no; });                  // 馬番の 順に 並んだ 表か
    var nh = med(num.map(function (n) { return n.h; })), gapsY = [];
    byY.forEach(function (n, k) { if (k && n.yc - byY[k - 1].yc > 0.5 * nh) gapsY.push(n.yc - byY[k - 1].yc); });
    var pitch = Math.max(gapsY.length ? med(gapsY) : 3 * nh, 0.01);                               // 行の 間かく（読めた 馬番の 行から）
    var top = byY[0].yc, bot = byY[byY.length - 1].yc, out = [];
    cand.forEach(function (c) {
      if (out.length >= 4 || c.yc < top - 1.6 * pitch || c.yc > bot + 1.6 * pitch) return;     // 表の 中（読めた 馬番の 行の 間・前後 1行）だけ
      if (c.nameX <= cx + cw / 2) return;                                                       // 名前が 馬番の 所に かかって いる（馬番の 列が ない）
      var prev = null, next = null;
      byY.forEach(function (n) { if (n.yc < c.yc) prev = n; else if (!next && n.yc > c.yc) next = n; });
      var m = Math.max(cw, 0.02), x0 = Math.max(0, cx - cw / 2 - m), x1 = Math.min(c.nameX - 0.002, cx + cw / 2 + m);
      var h = Math.max(c.h, nh, 0.01), y0 = Math.max(0, c.yc - 1.2 * h), y1 = Math.min(1, c.yc + 1.2 * h);
      if (x1 - x0 < 0.01) return;
      var near = function (n) { return n && Math.abs(n.yc - c.yc) <= 1.6 * pitch; };
      var w0 = near(prev) ? Math.max(0, prev.yc - 1.2 * h) : y0, w1 = near(next) ? Math.min(1, next.yc + 1.2 * h) : y1;
      out.push({ crop: [x0, y0, x1 - x0, y1 - y0], wide: w0 < y0 || w1 > y1 ? [x0, w0, x1 - x0, w1 - w0] : null, cx: cx, cw: cw, yc: c.yc, h: h,
        have: have, prev: prev ? prev.no : null, next: next ? next.no : null, asc: asc });
    });
    return out;
  }
  // 読み直しで 読めた 字（画像 全体の 位置）から、その 行の 馬番を 1つ 選ぶ。なければ null
  //   ・馬番の 列（cx）の 所・その 行の 高さ（yc）の 整数 1〜18　・もう 表に ある 馬番は 使わない（読みまちがい）
  //   ・馬番の 順の 表なら、上と 下の 行の 馬番の 間（10 と 12 の 間なら 11 だけ）
  function gapHit(g, lines) {
    var best = null;
    (lines || []).forEach(function (l) {
      var text = norm(l && l.text); if (!text) return;
      var x0 = +l.x || 0, w = +l.w || 0, h = +l.h || 0.01, yc = (+l.y || 0) + h / 2;
      var ts = tokens(text), len = Math.max(1, ts.join(' ').length), off = 0;
      ts.forEach(function (t) {
        var x = x0 + w * off / len, xe = x0 + w * (off + t.length) / len, c = (x + xe) / 2; off += t.length + 1;
        if (kind(t) !== 'int') return;
        var no = +t;
        if (!(no >= 1 && no <= 18) || g.have.indexOf(no) >= 0) return;
        if (Math.abs(c - g.cx) > Math.max(0.6 * g.cw, 0.015) || Math.abs(yc - g.yc) > 0.8 * g.h) return;
        if (g.asc && ((g.prev != null && no <= g.prev) || (g.next != null && no >= g.next))) return;
        var d = Math.abs(c - g.cx) + Math.abs(yc - g.yc);
        if (!best || d < best.d) best = { d: d, it: { text: String(no), x: x, y: yc - h / 2, w: xe - x, h: h } };
      });
    });
    return best ? best.it : null;
  }
  var API = { parse: parse, parseOne: parseOne, parseResult: parseResult, rows: rows, tokens: tokens, norm: norm, kataName: kataName, nameTable: nameTable, gaps: gaps, gapHit: gapHit, className: className };
  root.TengelOCR = API;
  if (typeof module !== 'undefined' && module.exports) module.exports = API;
})(typeof window !== 'undefined' ? window : globalThis);
