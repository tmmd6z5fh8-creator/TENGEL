// ===== iPhoneアプリ版だけの機能（設定タブ）：マザーデータ（3つ）の切り替え・名前・入れ替え（Excelファイル・貼り付け）・アプリの更新・バックアップ =====
(function () {
  'use strict';
  const $ = (s, el) => (el || document).querySelector(s);
  const $$ = (s, el) => Array.from((el || document).querySelectorAll(s));
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const z2h = s => String(s == null ? '' : s).replace(/[０-９．／－]/g, c => String.fromCharCode(c.charCodeAt(0) - 0xFEE0));
  const pad = n => ('0' + n).slice(-2);
  const md = (d, y) => d ? (y ? d.slice(0, 4) + '/' : '') + (+d.slice(5, 7)) + '/' + (+d.slice(8, 10)) : '—';
  // 年をまたぐデータ（JRAなど）は年も出す
  const span2 = (a, b) => { const y = !!(a && b && a.slice(0, 4) !== b.slice(0, 4)); return md(a, y) + '〜' + md(b, y); };
  const APP_VER = window.__APP_VER || '';
  function toast(m, ms) { const t = $('#toast'); if (!t) return; t.textContent = m; t.hidden = false; clearTimeout(toast._t); toast._t = setTimeout(() => { t.hidden = true; }, ms || 3000); }
  function when(iso) {
    if (!iso) return '';
    const d = new Date(iso), now = new Date();
    const day = d.toDateString() === now.toDateString() ? '今日' : (d.getMonth() + 1) + '/' + d.getDate();
    return day + ' ' + pad(d.getHours()) + ':' + pad(d.getMinutes());
  }

  // ---------- 1行（Excelの検証データ A〜P列）→ 基盤データの1レース ----------
  const BABA = ['良', '稍重', '重', '不良'];
  const serialISO = (n, d1904) => new Date((d1904 ? Date.UTC(1904, 0, 1) : Date.UTC(1899, 11, 30)) + Math.round(n) * 864e5).toISOString().slice(0, 10);
  function parseDate(v, d1904) {
    if (v == null || v === '') return null;
    if (typeof v === 'number') return v > 20000 && v < 80000 ? serialISO(v, d1904) : null;
    const s = z2h(v).trim(); let m;
    if (/^\d{5}(\.\d+)?$/.test(s)) return serialISO(+s, d1904);
    if ((m = s.match(/^(\d{4})[\/\-.年](\d{1,2})[\/\-.月](\d{1,2})/))) return m[1] + '-' + pad(m[2]) + '-' + pad(m[3]);
    if ((m = s.match(/^(\d{1,2})[\/\-.月](\d{1,2})/))) return new Date().getFullYear() + '-' + pad(m[1]) + '-' + pad(m[2]);
    return null;
  }
  function num(v) {
    if (v == null || typeof v === 'boolean') return null;
    if (typeof v === 'number') return isFinite(v) ? v : null;
    const s = z2h(v).replace(/[,円\s]/g, '');
    if (s === '' || s === '-' || s === '—') return null;
    const n = Number(s); return isFinite(n) ? n : null;
  }
  // 返り値：レース（読めた）／'bad'（日付はあるのにRや馬場が読めない行）／null（見出しや空の行）
  // tag：入れるマザーデータの印（1つ目＝大井 'oi'、2・3つ目＝'m2' 'm3'。開催場の列がないので venue は空）
  const tagOf = n => +n === 1 ? { venue: '大井', key: 'oi' } : { venue: '', key: 'm' + n };
  function rowToRec(c, d1904, tag) {
    tag = tag || tagOf(1);
    const date = parseDate(c[0], d1904);
    if (!date) return null;
    const r = num(c[1]), baba = String(c[2] == null ? '' : c[2]).trim();
    if (!r || r < 1 || r > 16 || r % 1 || BABA.indexOf(baba) < 0) return 'bad';
    const cnt = num(c[15]);
    return { id: date.replace(/-/g, '') + '-' + tag.key + '-' + pad(r), date, venue: tag.venue, r, baba, dist: num(c[3]), surface: 'ダ', n: num(c[4]), tan1: num(c[5]), s1: num(c[6]),
      p1: num(c[7]), p2: num(c[8]), p3: num(c[9]), s5: num(c[10]), s10: num(c[11]), umatanPay: num(c[12]), sanrenPay: num(c[13]),
      note: c[14] == null ? '' : String(c[14]).trim(), cnt: cnt == null ? 1 : cnt };
  }
  function toRecs(rows, d1904, tag) {
    const recs = [], seen = {}; let bad = 0;
    rows.forEach(c => { const x = rowToRec(c || [], d1904, tag); if (x === 'bad') bad++; else if (x) recs.push(x); });
    // 同じ日付・Rが2回あっても、どちらも消さない（2つめ以降に印をつける）
    recs.forEach(r => { if (seen[r.id]) { seen[r.id]++; r.id = r.id + '-' + seen[r.id]; } else seen[r.id] = 1; });
    return { recs, bad };
  }
  const parsePaste = (text, tag) => { const rows = text.split(/\r?\n/).filter(l => l.trim()).map(l => l.split('\t').map(x => x.trim())); return Object.assign({ shape: shapeOf(rows) }, toRecs(rows, false, tag)); };

  // ---------- Excelファイル（.xlsx）をiPhoneの中で読む（どこにも送らない） ----------
  async function unzip(file) {
    const buf = new Uint8Array(await file.arrayBuffer()), dv = new DataView(buf.buffer, buf.byteOffset, buf.byteLength);
    let eocd = -1;
    for (let i = buf.length - 22; i >= Math.max(0, buf.length - 65557); i--) if (dv.getUint32(i, true) === 0x06054b50) { eocd = i; break; }
    if (eocd < 0) throw new Error('Excelファイル（.xlsx）じゃないみたい');
    const cnt = dv.getUint16(eocd + 10, true), ents = {}, td = new TextDecoder('utf-8');
    let p = dv.getUint32(eocd + 16, true);
    for (let k = 0; k < cnt && p + 46 <= buf.length; k++) {
      if (dv.getUint32(p, true) !== 0x02014b50) break;
      const nlen = dv.getUint16(p + 28, true), elen = dv.getUint16(p + 30, true), clen = dv.getUint16(p + 32, true);
      const name = td.decode(buf.subarray(p + 46, p + 46 + nlen));
      ents[name.toLowerCase()] = { method: dv.getUint16(p + 10, true), csize: dv.getUint32(p + 20, true), loff: dv.getUint32(p + 42, true) };
      p += 46 + nlen + elen + clen;
    }
    async function text(name) {
      const e = ents[String(name).toLowerCase()]; if (!e) return null;
      const o = e.loff, start = o + 30 + dv.getUint16(o + 26, true) + dv.getUint16(o + 28, true);
      const data = buf.subarray(start, start + e.csize);
      if (e.method === 0) return td.decode(data);
      if (e.method !== 8) throw new Error('読めない圧縮形式だよ');
      if (typeof DecompressionStream === 'undefined') throw new Error('このiPhoneではExcelファイルを直接読めないよ（iOSを新しくするか、下の「貼り付け」で入れてね）');
      const out = await new Response(new Blob([data]).stream().pipeThrough(new DecompressionStream('deflate-raw'))).arrayBuffer();
      return td.decode(out);
    }
    return { text };
  }
  function xml(s) { const d = new DOMParser().parseFromString(s, 'application/xml'); if (d.getElementsByTagName('parsererror').length) throw new Error('ファイルの中身が読めなかったよ'); return d; }
  const tags = (el, n) => Array.from(el.getElementsByTagName(n));
  function relId(el) { for (const a of Array.from(el.attributes)) if (a.localName === 'id' && /relationships/.test(a.namespaceURI || '')) return a.value; return el.getAttribute('r:id'); }
  function colIdx(ref) { const m = /^([A-Z]+)/.exec(ref || ''); if (!m) return -1; let n = 0; for (const ch of m[1]) n = n * 26 + (ch.charCodeAt(0) - 64); return n - 1; }
  const tText = el => tags(el, 't').filter(t => !(t.parentNode && t.parentNode.localName === 'rPh')).map(t => t.textContent).join('');
  async function readXlsx(file, tag) {
    const z = await unzip(file);
    const wbx = await z.text('xl/workbook.xml'); if (!wbx) throw new Error('Excelファイル（.xlsx）じゃないみたい');
    const wb = xml(wbx), pr = tags(wb, 'workbookPr')[0], d1904 = !!(pr && /^(1|true)$/i.test(pr.getAttribute('date1904') || ''));
    const rmap = {}; const relx = await z.text('xl/_rels/workbook.xml.rels');
    if (relx) tags(xml(relx), 'Relationship').forEach(r => { rmap[r.getAttribute('Id')] = r.getAttribute('Target'); });
    const sheets = tags(wb, 'sheet').map(s => { const t = rmap[relId(s)] || ''; return { name: s.getAttribute('name') || '', path: t.charAt(0) === '/' ? t.slice(1) : 'xl/' + t.replace(/^\.\//, '') }; });
    const sst = []; const sx = await z.text('xl/sharedStrings.xml');
    if (sx) tags(xml(sx), 'si').forEach(si => sst.push(tText(si)));
    async function sheetRows(path) {
      const s = await z.text(path); if (!s) return [];
      return tags(xml(s), 'row').map(row => {
        const vals = []; let seq = 0;
        for (const c of Array.from(row.children)) {
          if (c.localName !== 'c') continue;
          const ci = c.hasAttribute('r') ? colIdx(c.getAttribute('r')) : seq; seq = ci + 1;
          if (ci < 0 || ci > 15) continue;
          const t = c.getAttribute('t'), v = tags(c, 'v')[0], vt = v ? v.textContent : null;
          let val = null;
          if (t === 's') val = vt == null ? null : (sst[+vt] != null ? sst[+vt] : null);
          else if (t === 'inlineStr') { const is = tags(c, 'is')[0]; val = is ? tText(is) : null; }
          else if (t === 'str' || t === 'd') val = vt;
          else if (t === 'b') val = vt === '1';
          else if (t === 'e') val = null;
          else val = (vt == null || vt === '') ? null : Number(vt);
          vals[ci] = val;
        }
        return vals;
      });
    }
    const first = sheets.filter(s => /検証データ/.test(s.name)), rest = sheets.filter(s => !/検証データ/.test(s.name));
    let best = null, shape = '';
    for (const sh of first.concat(rest)) {
      const rows = await sheetRows(sh.path), res = toRecs(rows, d1904, tag), sp = shapeOf(rows);
      if (!shape && sp && sp !== 'kensho') shape = sp;
      if (res.recs.length && (!best || res.recs.length > best.recs.length)) best = Object.assign({ sheet: sh.name, shape: sp }, res);
      if (best && first.indexOf(sh) >= 0) break; // 検証データのシートで読めたら、それを使う
    }
    if (!best) { const e = new Error(shapeMsg(shape) || 'レースの行が見つからなかったよ。'); e.html = true; throw e; }
    return best;
  }
  // ---------- 形のちがうファイル（分析シート・分析表・フィルターの元データ）を見分ける ----------
  // 返り値：'sheet'＝分析シート／'hyo'＝分析表／'filter'＝距離・馬場フィルターの元データ／'kensho'＝検証データ／''＝わからない
  function shapeOf(rows) {
    for (const c of rows.slice(0, 15)) {
      if (!c) continue;
      const L = i => String(c[i] == null ? '' : c[i]).replace(/\s/g, '');
      if (!/^日付?$/.test(L(0))) continue;
      if (/^1R$/i.test(L(1))) return 'hyo';
      if (/結果/.test(L(5))) return 'sheet';
      if (/着人気/.test(L(5))) return 'filter';
      if (/単勝/.test(L(5)) && /3連単/.test(L(6))) return 'kensho';
    }
    for (const c of rows.slice(0, 15)) if (c && /単勝/.test(String(c[1] || '')) && /3連単/.test(String(c[2] || ''))) return 'hyo';
    return '';
  }
  const SHAPE_NAME = { sheet: '「分析シート」の形（日付・R・馬場・距離・出馬数・結果）', hyo: '「分析表」の形（1日1行で、Rごとに単勝1位・3連単1位・結果）', filter: '距離・馬場フィルターの元データの形（日付・R・馬場・距離・頭数・1〜3着人気）' };
  const SHAPE_MISS = { sheet: '単勝1位・3連単1位が入っていない', hyo: '馬場・距離・頭数が入っていない', filter: '単勝1位・3連単1位が入っていない' };
  function shapeMsg(shape, what) {
    what = what || 'このファイル';
    const head = SHAPE_NAME[shape] ? `${what}は${SHAPE_NAME[shape]}だよ。${SHAPE_MISS[shape]}から、このままマザーデータには入れられないの。` : `${what}には、単勝1位（F列）・3連単1位（G列）・1着人気（H列）・2着人気（I列）がちゃんと入っていないみたい。`;
    return esc(head) + '<br>マザーデータに入れられるのは、<b>姫フィルターのExcel（検証データのシートがあるもの）</b>だよ。分析シートと分析表に打ち込んだ新しいレースは、姫に送ってね（日付とRで合わせて入れるよ）。';
  }
  // 読み取った中身が「判定に使える形」か調べる。だめなら理由（HTML）を返す
  function badShape(res, what) {
    const recs = res.recs, n = recs.length;
    const odds = recs.filter(r => r.tan1 > 0 && r.s1 > 0).length, got = recs.filter(r => r.p1 > 0 && r.p2 > 0).length;
    const sane = recs.filter(r => r.tan1 >= 1 && r.tan1 < 1000 && r.s1 >= r.tan1).length;
    if (n && odds >= n / 2 && got >= n / 2 && sane >= n / 2) return '';
    return shapeMsg(res.shape, what);
  }
  const KEEP = '<br><b>いまのデータはそのまま</b>だよ（なにも変えていないよ）。';

  // ---------- 入れる先のマザーデータと比べる ----------
  const CMP = ['date', 'r', 'baba', 'dist', 'n', 'tan1', 's1', 'p1', 'p2', 'p3', 's5', 's10', 'umatanPay', 'sanrenPay', 'note', 'cnt'];
  const norm = v => (v === undefined || v === '') ? null : v;
  function diff(recs, n) {
    const cur = new Map(TengelLocal.slots.rows(n).map(r => [r.id, r])), nmap = new Map(recs.map(r => [r.id, r]));
    let add = 0, chg = 0, del = 0;
    nmap.forEach((r, id) => { const o = cur.get(id); if (!o) add++; else if (CMP.some(k => norm(o[k]) !== norm(r[k]))) chg++; });
    cur.forEach((o, id) => { if (!nmap.has(id)) del++; });
    return { add, chg, del };
  }
  const span = recs => { const ds = recs.map(r => r.date).sort(); return span2(ds[0], ds[ds.length - 1]); };
  const usable = recs => recs.filter(r => Number(r.cnt) === 1 && r.p1 && r.p2).length;

  // ---------- 設定タブの中身 ----------
  function build() {
    const box = $('#setExtra'); if (!box) return;
    box.innerHTML = `
<div class="card setsec" id="setMother" style="margin-top:var(--gap)">
  <h2>マザーデータ（3つ）</h2>
  <p class="hint" style="margin:0">「使う」を押したマザーデータで、判定の参考的中率と実測（①〜⑦）を計算するよ。判定タブと実測タブの上でも切り替えられるよ。買ったレースの記録と買い目の設定は、3つとも共通だよ。</p>
  <div class="slotlist" id="slotList"></div>
  <div class="slotedit" id="slotEdit"></div>
</div>
<div class="card setsec ocrset" id="setOcr">
  <h2>画像の読み取り（オッズのスクショ）</h2>
  <p class="hint" style="margin:0">判定タブの<b>「オッズ画像から読み取る」</b>で、スクショ（1〜3枚）から開催場・R・距離・馬場・頭数・単勝・複勝・3連単の人気順を読み取って、入力欄に入れるよ。読み取りはClaude（Anthropic）にしてもらうから、<b>AnthropicのAPIキー</b>を1回だけ入れてね。</p>
  <dl class="kvs"><dt>APIキー</dt><dd id="soState">まだ入っていないよ</dd><dt>料金のめやす</dt><dd>標準：1回 約1〜4円／節約：1回 1円未満<br><span class="small muted">Anthropicへの支払い。スクショの枚数で変わるよ</span></dd></dl>
  <label for="soKey" class="small muted" style="font-weight:700">APIキー（sk-ant- ではじまる文字）</label>
  <div class="namerow" style="margin-top:4px"><input id="soKey" type="password" autocomplete="off" autocapitalize="off" autocorrect="off" spellcheck="false" placeholder="sk-ant-…"><button class="btn primary" type="button" id="soSave">保存して試す</button></div>
  <div style="margin-top:10px"><span class="small muted" style="font-weight:700">読み取りのモデル</span><div class="seg" id="soModel" style="margin-top:4px"><button type="button" data-v="std" aria-pressed="true">標準（正確）</button><button type="button" data-v="eco" aria-pressed="false">節約（安い）</button></div></div>
  <div class="row" style="margin-top:10px"><button class="btn" type="button" id="soTest" hidden>いまのキーで試す</button><button class="btn danger" type="button" id="soDel" hidden>キーを消す</button></div>
  <p class="small" id="soMsg" style="margin:8px 0 0"></p>
  <details style="margin-top:10px"><summary class="small" style="cursor:pointer;font-weight:700">APIキーの作り方（5分くらい）</summary>
    <ol class="small steps">
      <li>Safariで <b>platform.claude.com</b> を開いてログイン（はじめてならアカウントを作る）</li>
      <li>Settings の <b>Billing</b> で、クレジットカードを登録してクレジット（残高）を入れる。5ドルあれば、標準でも200回以上読めるよ</li>
      <li>Settings の <b>API keys</b> →「Create key」でキーを作って、出てきた <b>sk-ant-…</b> をコピー（1回しか表示されないよ）</li>
      <li>この上の欄に貼り付けて「保存して試す」</li>
    </ol>
  </details>
  <p class="hint">キーは<b>このiPhoneの中だけ</b>に保存するよ（バックアップのファイルにも入れないよ）。スクショは読み取りのためにAnthropicへ直接送るだけだよ。キーは人に見せないでね。</p>
</div>
<div class="card setsec" id="setUpdate">
  <h2>アプリの更新</h2>
  <dl class="kvs"><dt>いまの版</dt><dd>${esc(APP_VER || '—')}（第13改訂版）</dd><dt>最後に確認</dt><dd id="suChecked">まだ</dd></dl>
  <div class="row"><button class="btn" type="button" id="suCheck">新しい版があるか確認</button><button class="btn primary" type="button" id="suApply" hidden>新しい版にする</button></div>
  <p class="small" id="suMsg" style="margin:8px 0 0"></p>
  <p class="hint">更新しても、<b>買ったレースの記録・買い目の設定・マザーデータ（3つとも）は消えないよ</b>（このiPhoneの中にそのまま残るよ）。新しい版があるときは、アプリを開いたときに上にお知らせが出るよ。</p>
  <div class="banner warn">⚠️ ホーム画面のアイコンは消さないでね。アイコンを消すと、中の記録も一緒に消えちゃうの。</div>
</div>
<div class="card setsec" id="setBackup">
  <h2>バックアップ（記録を守る）</h2>
  <p class="hint">記録はこのiPhoneの中だけに入っているよ。ときどき保存しておくと、機種変更やアイコンを消しちゃったときに戻せるよ（ファイルアプリやLINEのKeepなどに保存してね）。買い目の設定・マザーデータの名前・Excelで入れたマザーデータも一緒に保存するよ。</p>
  <dl class="kvs"><dt>記録</dt><dd id="sbCount">—</dd><dt>最後のバックアップ</dt><dd id="sbLast">まだしてないよ</dd></dl>
  <div class="row"><button class="btn primary" type="button" id="pwaBackup">バックアップを保存</button><button class="btn" type="button" id="pwaRestore">バックアップから戻す</button><input type="file" id="pwaRestoreFile" accept=".json,application/json" hidden></div>
  <p class="small" id="pwaBkInfo" style="margin:8px 0 0"></p>
</div>`;
    wireSlots(); wireOcr(); wireUpdate(); wireBackup();
  }

  // ---- 画像の読み取り（APIキー） ----
  function wireOcr() {
    const O = TengelLocal.ocr; let model = 'std';
    const mask = k => k ? k.slice(0, 10) + '…' + k.slice(-4) : '';
    function paint() {
      const s = O.get(); if (s) model = s.model;
      $('#soState').innerHTML = s ? `入っているよ（<span class="mono">${esc(mask(s.key))}</span>）` : 'まだ入っていないよ';
      $('#soTest').hidden = !s; const d = $('#soDel'); d.hidden = !s; delete d.dataset.ok; d.textContent = 'キーを消す';
      $$('#soModel button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.v === model)));
    }
    const MSG = { bad_key: 'このキーは使えないみたい。コピーし直して、もう一度貼ってね', no_credit: 'クレジット（残高）が足りないみたい。platform.claude.com の Billing で入れてね', network: '通信できなかったよ。電波がいいところでもう一度試してね', busy: 'Anthropicが混み合ってるみたい。少し待ってから試してね', rate_limited: '少し混み合ってるみたい。時間をおいてから試してね', bad_model: 'モデルが見つからなかったよ。「標準」にして試してね' };
    const msgOf = e => MSG[e && e.code] || ('うまくいかなかったよ：' + (e && (e.message || e.code) || e));
    async function tryKey(key, m, saveIt) {
      const msg = $('#soMsg'); msg.innerHTML = '<span class="spin"></span> 試しているよ…（数秒）';
      $('#soSave').disabled = true;
      try {
        await O.test(key, m);
        if (saveIt) await O.save(key, m);
        msg.textContent = saveIt ? '✅ 保存したよ。判定タブの「オッズ画像から読み取る」が使えるよ✨' : '✅ このキーで読み取れるよ✨';
        if (saveIt) $('#soKey').value = '';
      } catch (e) {
        // キーは正しそう（残高・電波・混雑）なら、保存だけはしておく
        if (saveIt && e && /^(no_credit|network|busy|rate_limited)$/.test(e.code)) { await O.save(key, m).catch(() => {}); $('#soKey').value = ''; msg.textContent = '⚠️ キーは保存したよ。でも ' + msgOf(e); }
        else msg.textContent = '❌ ' + msgOf(e);
      } finally { $('#soSave').disabled = false; paint(); }
    }
    $('#soSave').onclick = () => {
      const k = $('#soKey').value.replace(/\s/g, '');
      if (!/^sk-ant-/.test(k)) { $('#soMsg').textContent = '「sk-ant-」ではじまるキーを貼ってね'; return; }
      tryKey(k, model, true);
    };
    $('#soTest').onclick = () => { const s = O.get(); if (s) tryKey(s.key, s.model, false); };
    $('#soModel').onclick = e => {
      const b = e.target.closest('button'); if (!b) return; model = b.dataset.v;
      $$('#soModel button').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
      const s = O.get(); if (s) O.save(s.key, model).then(() => toast(model === 'eco' ? '節約モデルで読み取るよ' : '標準モデルで読み取るよ')).catch(err => toast('保存できなかったよ：' + (err && err.message || err), 3600));
    };
    $('#soDel').onclick = ev => {
      const b = ev.currentTarget; if (!b.dataset.ok) { b.dataset.ok = '1'; b.textContent = 'ほんとに消す？（もう一度押してね）'; return; }
      O.clear().then(() => { $('#soMsg').textContent = 'キーを消したよ'; paint(); }).catch(err => toast('消せなかったよ：' + (err && err.message || err), 3600));
    };
    TengelLocal.ready.then(paint).catch(() => {});
  }
  // 判定タブなどから設定タブの各カードへ飛ぶ
  function goSettings(sec) {
    const tb = document.querySelector('.tabbar [data-tab=set]');
    if (tb && getComputedStyle(tb.parentNode).display !== 'none') tb.click(); else { const t2 = document.querySelector('.tabs-top [data-tab=set]'); if (t2) t2.click(); }
    setTimeout(() => { const s = document.getElementById({ ocr: 'setOcr', backup: 'setBackup', mother: 'setMother' }[sec] || 'setMother'); if (s) s.scrollIntoView({ block: 'start' }); }, 60);
  }
  document.addEventListener('click', e => { const b = e.target.closest && e.target.closest('[data-goset]'); if (b) { e.preventDefault(); goSettings(b.dataset.goset); } });

  // ---- マザーデータ（3つ） ----
  let pending = null, editN = null;
  const L = () => TengelLocal.slots;
  const curEdit = () => editN || L().active();
  const srcText = s => s.n === 1 && s.source === 'app' ? 'アプリに入っていた大井データ' : s.source === 'excel' ? `Excel${s.file ? '「' + esc(s.file) + '」' : ''}から（${when(s.at)}）` : s.source === 'paste' ? `貼り付けで（${when(s.at)}）` : '';
  function slotRowHTML(s, en) {
    const how = s.count ? `${s.count}走（${span2(s.first, s.last)}）・集計対象 ${s.usable}走${s.formed ? '' : '<br><span class="warnline">⚠️ 判定に使えない形のデータだよ</span>'}` : 'まだ空だよ';
    const src = s.count ? srcText(s) : '';
    return `<div class="slotrow${s.active ? ' on' : ''}${en === s.n ? ' edit' : ''}" data-n="${s.n}">
      <div><div class="sr-name"><span class="sr-no">${s.n}</span><b>${esc(s.name)}</b>${s.active ? '<span class="chip cus">使用中</span>' : ''}</div>
        <div class="sr-sub">${how}${src ? '<br>' + src : ''}</div></div>
      <div class="sr-act">${!s.active && s.count ? '<button class="btn primary" type="button" data-sact="use">使う</button>' : ''}<button class="btn" type="button" data-sact="edit" aria-pressed="${en === s.n}">${en === s.n ? '編集中' : '編集'}</button></div>
    </div>`;
  }
  function paintSlots(forcePanel) {
    const box = $('#slotList'); if (!box) return;
    const en = curEdit(), list = L().info();
    box.innerHTML = list.map(s => slotRowHTML(s, en)).join('');
    const ed = $('#slotEdit');
    const busy = ed.contains(document.activeElement) && /INPUT|TEXTAREA/.test(document.activeElement.tagName);
    if (forcePanel || ed.dataset.n !== String(en)) renderEdit(en);
    else if (!busy) paintEditMeta(en);
  }
  function paintEditMeta(n) {
    const s = L().info().find(x => x.n === n); if (!s) return;
    const h = $('#seTitle'); if (h) h.textContent = `${n}つ目「${s.name}」の編集`;
    const m = $('#seMeta'); if (m) m.innerHTML = s.count ? `<dt>いまのデータ</dt><dd><b>${s.count}走</b>（${span2(s.first, s.last)}）・集計対象 ${s.usable}走${s.formed ? '' : '<br><span class="warnline">⚠️ 判定に使えない形のデータだよ（単勝・3連単・着順が入っていない）</span>'}</dd><dt>入れ方</dt><dd>${srcText(s) || '—'}</dd>` : '<dt>いまのデータ</dt><dd>まだ空だよ</dd>';
    const ud = $('#seUndo'), pv = L().prev(n);
    if (ud) { ud.hidden = !pv; if (pv) ud.textContent = `ひとつ前のデータに戻す（${pv.n}走・${span2(pv.first, pv.last)}）`; delete ud.dataset.ok; }
    const emb = window.__MOTHER || [], rv = $('#seRevert'), cl = $('#seClear');
    if (rv) { rv.hidden = !(n === 1 && s.source !== 'app' && emb.length); rv.textContent = `アプリに入っている大井データ（${emb.length}走）に戻す`; delete rv.dataset.ok; }
    if (cl) { cl.hidden = !(n !== 1 && s.count); cl.textContent = 'このマザーデータを空にする'; delete cl.dataset.ok; }
  }
  function renderEdit(n) {
    const ed = $('#slotEdit'), s = L().info().find(x => x.n === n); if (!ed || !s) return;
    pending = null; ed.dataset.n = String(n);
    ed.innerHTML = `<h3 id="seTitle"></h3>
      <label for="seName" class="small muted" style="font-weight:700">名前（16文字まで）</label>
      <div class="namerow" style="margin-top:4px"><input id="seName" maxlength="16" autocomplete="off" value="${esc(s.name)}"><button class="btn" type="button" id="seNameSave">名前を保存</button></div>
      <dl class="kvs" id="seMeta"></dl>
      <p class="hint">${n === 1 ? '大井の姫フィルター（Excel）を更新したら、ファイルを選ぶだけで入れ替えられるよ。<b>検証データ</b>シートのA〜P列（日付〜集計対象）を読むよ。' : 'このマザーデータに入れるデータを選んでね。大井の<b>検証データと同じA〜P列</b>（日付・R・馬場・距離・頭数・単勝1位・3連単1位・1着人気・2着人気・3着人気・3連単5位・3連単10位・馬単払戻・3連単払戻・備考・集計対象）の形なら入るよ。入れ直すと、まるごと新しいデータに替わるよ。'}ファイルはこのiPhoneの中で読むだけで、どこにも送らないよ。</p>
      <div class="row" style="margin-top:10px"><button class="btn primary" type="button" id="smPick">Excelファイルを選ぶ</button><input type="file" id="smFile" accept=".xlsx,.xlsm,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" hidden></div>
      <div id="smPreview"></div>
      <details style="margin-top:12px"><summary class="small" style="cursor:pointer;font-weight:700">ファイルが選べないとき：コピーして貼り付け</summary>
        <p class="hint">Excelの<b>A〜P列</b>を全部コピーして貼り付けてね。</p>
        <textarea id="smText" rows="4" placeholder="2026/10/08	1	良	1200	12	2.1	18.5	1	3	2	…"></textarea>
        <div class="row" style="margin-top:8px"><button class="btn" type="button" id="smParse">読み取る</button></div>
      </details>
      <div class="row" style="margin-top:12px"><button class="btn" type="button" id="seUndo" hidden></button><button class="btn ghost" type="button" id="seRevert" hidden></button><button class="btn danger" type="button" id="seClear" hidden></button></div>`;
    paintEditMeta(n);
    const saveName = () => {
      const v = $('#seName').value;
      L().rename(n, v).then(name => { $('#seName').value = name; toast(`名前を「${name}」にしたよ`); }).catch(e => toast('名前を保存できなかったよ：' + (e && e.message || e), 3600));
    };
    $('#seNameSave').onclick = saveName;
    $('#seName').onkeydown = e => { if (e.key === 'Enter') { e.preventDefault(); saveName(); e.target.blur(); } };
    $('#smPick').onclick = () => $('#smFile').click();
    $('#smFile').onchange = e => {
      const f = e.target.files[0]; e.target.value = ''; if (!f) return;
      const box = $('#smPreview'); box.innerHTML = '<p class="small" style="margin:8px 0 0"><span class="spin"></span> 「' + esc(f.name) + '」を読んでいるよ…</p>';
      readXlsx(f, tagOf(n)).then(res => {
        const why = badShape(res);
        if (why) { pending = null; box.innerHTML = `<div class="banner bad">❌ 「${esc(f.name)}」は入れられないよ。<br>${why}${KEEP}</div>`; return; }
        showPreview(n, res, `「${f.name}」の${res.sheet}シート`, { source: 'excel', file: f.name });
      }).catch(err => { pending = null; box.innerHTML = `<div class="banner bad">❌ 読めなかったよ：${err && err.html ? err.message : esc(err && err.message || err)}${KEEP}</div>`; });
    };
    $('#smParse').onclick = () => {
      const res = parsePaste($('#smText').value, tagOf(n)), box = $('#smPreview');
      if (!res.recs.length) { pending = null; box.innerHTML = `<div class="banner bad">読み取れる行がなかったよ。A〜P列をそのまま貼ってね${res.shape ? '<br>' + shapeMsg(res.shape, '貼り付けた内容') : ''}</div>`; return; }
      const why = badShape(res, '貼り付けた内容');
      if (why) { pending = null; box.innerHTML = `<div class="banner bad">❌ 貼り付けた内容は入れられないよ。<br>${why}${KEEP}</div>`; return; }
      showPreview(n, res, '貼り付けた内容', { source: 'paste' });
    };
    $('#seUndo').onclick = ev => {
      const b = ev.currentTarget, pv = L().prev(n); if (!pv) return;
      if (!b.dataset.ok) { b.dataset.ok = '1'; b.textContent = 'ほんとに戻す？（もう一度押してね）'; return; }
      L().undo(n).then(() => { toast(`ひとつ前のデータ（${pv.n}走）に戻したよ`); $('#smPreview').innerHTML = ''; }).catch(e => toast('戻せなかったよ：' + (e && e.message || e), 3600));
    };
    $('#seRevert').onclick = ev => {
      const b = ev.currentTarget, emb = window.__MOTHER || [];
      if (!b.dataset.ok) { b.dataset.ok = '1'; b.textContent = 'ほんとに戻す？（もう一度押してね）'; return; }
      TengelLocal.replaceRaces(emb, { source: 'app' }).then(() => { toast(`アプリに入っている大井データ（${emb.length}走）に戻したよ`); $('#smPreview').innerHTML = ''; });
    };
    $('#seClear').onclick = ev => {
      const b = ev.currentTarget, nm = L().info().find(x => x.n === n).name;
      if (!b.dataset.ok) { b.dataset.ok = '1'; b.textContent = `ほんとに「${nm}」を空にする？（もう一度押してね）`; return; }
      L().clear(n).then(() => { toast(`「${nm}」を空にしたよ`); $('#smPreview').innerHTML = ''; }).catch(e => toast('空にできなかったよ：' + (e && e.message || e), 3600));
    };
  }
  function showPreview(n, res, label, info) {
    const d = diff(res.recs, n), box = $('#smPreview'), nm = L().info().find(x => x.n === n).name, empty = !L().rows(n).length, noUse = !usable(res.recs);
    pending = { n, recs: res.recs, info };
    const same = !d.add && !d.chg && !d.del;
    box.innerHTML = `<div class="banner info">${esc(label)}から <b>${res.recs.length}走</b>（${span(res.recs)}）を読み取ったよ。集計対象 ${usable(res.recs)}走。<br>${empty ? `「${esc(nm)}」は空だから、このデータがそのまま入るよ。` : `いまの「${esc(nm)}」と比べて：新しいレース <b>${d.add}</b>走・中身が変わったレース <b>${d.chg}</b>走・なくなるレース <b>${d.del}</b>走${same ? '<br>（いまと同じ内容だよ）' : ''}`}</div>
      ${d.del && !empty ? `<div class="banner warn">いまの「${esc(nm)}」にあって、このファイルにないレースが${d.del}走あるよ。入れ替えると、そのレースは消えるよ（買ったレースの記録は消えないよ）。</div>` : ''}
      ${res.bad ? `<p class="small muted" style="margin:6px 0 0">日付はあるのにRや馬場が読めなかった行が${res.bad}行あったよ（飛ばしたよ）。</p>` : ''}
      ${noUse ? `<div class="banner warn">集計対象（P列）が全部0だから、このままだと判定の参考値や実測（①〜⑦）には使われないよ。</div>` : ''}
      <div class="row" style="margin-top:10px"><button class="btn primary" type="button" id="smApply">「${esc(nm)}」に入れる</button><button class="btn ghost" type="button" id="smCancel">やめる</button></div>
      ${L().rows(n).length ? '<p class="small muted" style="margin:6px 0 0">入れたあとでも「ひとつ前のデータに戻す」で、いまのデータに戻せるよ。</p>' : ''}`;
    $('#smCancel').onclick = () => { pending = null; box.innerHTML = ''; };
    $('#smApply').onclick = ev => {
      if (!pending) return;
      const b = ev.currentTarget, p = pending;
      if (p.n === 1 && p.recs.length < 50 && !b.dataset.ok) { b.dataset.ok = '1'; b.textContent = `ほんとに入れ替える（${p.recs.length}走だけになるよ）`; return; }
      if (noUse && !b.dataset.ok) { b.dataset.ok = '1'; b.textContent = 'それでも入れる（もう一度押してね）'; return; }
      b.disabled = true; b.textContent = '入れているよ…';
      L().replace(p.n, p.recs, p.info).then(() => {
        const act = L().active() === p.n;
        toast(`「${nm}」に${p.recs.length}走を入れたよ`, 3600);
        box.innerHTML = `<div class="banner info">✅ 「${esc(nm)}」に${p.recs.length}走を入れたよ（${when(new Date().toISOString())}）。${act ? '判定と実測（①〜⑦）は、このデータで計算しているよ。' : `<div class="row" style="margin-top:8px"><button class="btn primary" type="button" id="smUse">「${esc(nm)}」を使う</button></div>`}</div>`;
        const u = $('#smUse'); if (u) u.onclick = () => L().setActive(p.n).then(() => { toast(`マザーデータを「${nm}」にしたよ`); u.closest('.row').remove(); });
        pending = null;
      }).catch(e => { b.disabled = false; b.textContent = `「${nm}」に入れる`; box.insertAdjacentHTML('beforeend', `<div class="banner bad">❌ 入れられなかったよ：${esc(e && e.message || e)}</div>`); });
    };
  }
  function wireSlots() {
    $('#slotList').onclick = e => {
      const b = e.target.closest('[data-sact]'); if (!b) return;
      const n = +b.closest('.slotrow').dataset.n;
      if (b.dataset.sact === 'use') {
        const nm = L().info().find(x => x.n === n).name;
        L().setActive(n).then(() => toast(`マザーデータを「${nm}」にしたよ`)).catch(err => toast('切り替えられなかったよ：' + (err && err.message || err), 3600));
      } else if (b.dataset.sact === 'edit') {
        editN = n; paintSlots(true);
        const ed = $('#slotEdit'); if (ed) ed.scrollIntoView({ block: 'nearest', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
      }
    };
    TengelLocal.ready.then(() => paintSlots(true)).catch(() => {});
  }

  // ---- アプリの更新 ----
  let lastCheck = 0, newer = null;
  function setSuMsg(t) { const m = $('#suMsg'); if (m) m.textContent = t; }
  function showBar(v) {
    let bar = $('#updBar');
    if (!bar) {
      // ヘッダーの中（いつも見える所）にお知らせを出す
      bar = document.createElement('div'); bar.id = 'updBar'; bar.className = 'updbar';
      $('header.top .top-in').appendChild(bar);
    }
    const data = v.mother && window.__MOTHER_VER && v.mother !== window.__MOTHER_VER;   // アプリに入っている大井データも新しくなる版
    bar.innerHTML = `<span>✨ 新しい版（<b>${esc(v.app)}</b>）があるよ。${data ? '大井のデータも新しくなるよ。' : ''}記録はそのまま残るよ</span><button class="btn" type="button" id="updGo">更新する</button>`;
    bar.hidden = false; $('#updGo').onclick = applyUpdate;
    const ap = $('#suApply'); if (ap) ap.hidden = false;
  }
  function checkUpdate(manual) {
    if (!manual && (Date.now() - lastCheck < 10 * 60e3 || navigator.onLine === false)) return Promise.resolve();
    lastCheck = Date.now();
    if (manual) setSuMsg('確認しているよ…');
    return fetch('version.json?t=' + Date.now(), { cache: 'no-store' })
      .then(r => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .then(v => {
        const c = $('#suChecked'); if (c) c.textContent = when(new Date().toISOString());
        if (v && v.app && v.app > APP_VER) { newer = v; showBar(v); setSuMsg(`新しい版（${v.app}）があるよ。${v.mother && window.__MOTHER_VER && v.mother !== window.__MOTHER_VER ? '大井のデータも新しくなるよ。' : ''}「新しい版にする」を押してね`); }
        else { newer = null; const bar = $('#updBar'); if (bar) bar.hidden = true; if (manual) setSuMsg('いまの版が最新だよ✨'); }
      })
      .catch(() => { if (manual) setSuMsg('確認できなかったよ。電波がいいところでもう一度押してね'); });
  }
  function applyUpdate() {
    setSuMsg('新しい版にしているよ…'); toast('新しい版にしているよ…');
    const go = () => location.reload();
    if (!('serviceWorker' in navigator)) return go();
    navigator.serviceWorker.getRegistration().then(reg => {
      if (!reg) return go();
      const t = setTimeout(go, 4000);
      navigator.serviceWorker.addEventListener('controllerchange', () => { clearTimeout(t); go(); });
      reg.update().then(() => { if (!reg.installing && !reg.waiting) { clearTimeout(t); go(); } }).catch(() => { clearTimeout(t); go(); });
    }).catch(go);
  }
  function wireUpdate() {
    $('#suCheck').onclick = () => checkUpdate(true);
    $('#suApply').onclick = applyUpdate;
    if (newer) showBar(newer);
  }

  // ---- バックアップ ----
  function paintBackup() {
    const n = TengelLocal.mem.bets.size, c = $('#sbCount'); if (c) c.textContent = n + '件';
    TengelLocal.getMeta('backup').then(b => { const l = $('#sbLast'); if (l) l.textContent = b && b.at ? when(b.at) + '（' + b.n + '件）' : 'まだしてないよ'; }).catch(() => {});
  }
  function wireBackup() {
    paintBackup();
    $('#pwaBackup').onclick = async () => {
      const bets = Array.from(TengelLocal.mem.bets.values());
      const zones = await TengelLocal.getSetting('zones').catch(() => undefined);
      const meta = await TengelLocal.motherMeta().catch(() => null);
      const data = { app: 'tengel3', appVer: APP_VER, at: new Date().toISOString(), bets, settings: { zones: zones === undefined ? null : zones } };
      if (meta && meta.source !== 'app') data.mother = { meta, rows: L().rows(1) };
      data.slots = { names: L().names(), active: L().active(), data: {} };
      [2, 3].forEach(n => { const doc = L().doc(n); if (doc && doc.rows && doc.rows.length) data.slots.data[n] = doc; });
      const name = 'テンゲル記録_' + new Date().toISOString().slice(0, 10).replace(/-/g, '') + '.json';
      const file = new File([JSON.stringify(data)], name, { type: 'application/json' });
      const nSlots = Object.keys(data.slots.data).length;
      const doneMsg = how => { $('#pwaBkInfo').textContent = `記録${bets.length}件${zones ? '・買い目の設定' : ''}・マザーデータの名前${data.mother ? '・大井データ' : ''}${nSlots ? `・マザーデータ${nSlots}つ分` : ''}を${how}よ`; TengelLocal.putMeta({ id: 'backup', at: data.at, n: bets.length }).then(paintBackup); };
      if (navigator.canShare && navigator.canShare({ files: [file] })) {
        navigator.share({ files: [file], title: name }).then(() => doneMsg('保存した')).catch(() => {});
      } else {
        const a = document.createElement('a'); a.href = URL.createObjectURL(file); a.download = name; document.body.appendChild(a); a.click(); setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 2000);
        doneMsg('書き出した');
      }
    };
    $('#pwaRestore').onclick = () => $('#pwaRestoreFile').click();
    $('#pwaRestoreFile').onchange = e => {
      const f = e.target.files[0]; e.target.value = ''; if (!f) return;
      f.text().then(async t => {
        const d = JSON.parse(t), list = Array.isArray(d) ? d : d.bets;
        if (!Array.isArray(list)) throw new Error('テンゲルのバックアップじゃないみたい');
        const cur = TengelLocal.mem.bets;
        const add = list.filter(b => { if (!b || !b.id) return false; const o = cur.get(b.id); return !o || String(b.updatedAt || '') >= String(o.updatedAt || ''); });
        await TengelLocal.putBets(add);
        const msg = [`記録${add.length}件を戻したよ（同じレースは新しい方を残したよ）`];
        if (d.settings && Object.prototype.hasOwnProperty.call(d.settings, 'zones')) {
          document.dispatchEvent(new CustomEvent('tengel:zones', { detail: d.settings.zones }));
          msg.push(d.settings.zones ? '買い目の設定も戻したよ' : '買い目は初期の設定にしたよ');
        }
        const last = rs => rs.reduce((m, r) => r.date > m ? r.date : m, '');
        if (d.slots) {
          for (const n of [1, 2, 3]) if (d.slots.names && d.slots.names[n]) await L().rename(n, d.slots.names[n]);
          for (const n of [2, 3]) {
            const doc = d.slots.data && d.slots.data[n]; if (!doc || !Array.isArray(doc.rows) || !doc.rows.length) continue;
            const cur = L().rows(n), bl = last(doc.rows), cl = last(cur);
            if (!cur.length || bl > cl || (bl === cl && doc.rows.length > cur.length)) { await L().replace(n, doc.rows, { source: doc.source || 'excel', file: doc.file || '' }); msg.push(`「${L().names()[n]}」のデータ${doc.rows.length}走も戻したよ`); }
          }
        }
        if (d.mother && Array.isArray(d.mother.rows) && d.mother.rows.length) {
          const curRows = L().rows(1);
          const bl = last(d.mother.rows), cl = last(curRows);
          if (bl > cl || (bl === cl && d.mother.rows.length > curRows.length)) {
            await TengelLocal.replaceRaces(d.mother.rows, { source: (d.mother.meta && d.mother.meta.source) || 'excel', file: (d.mother.meta && d.mother.meta.file) || '' });
            msg.push(`大井データも${d.mother.rows.length}走に戻したよ`);
          }
        }
        $('#pwaBkInfo').textContent = msg.join('。');
        paintBackup();
      }).catch(err => { $('#pwaBkInfo').textContent = '戻せなかったよ：' + (err && err.message || err); });
    };
  }

  function boot() {
    build();
    // 記録タブには、バックアップの場所だけ案内する
    const rec = $('#v-rec'), list = $('#recList');
    if (rec && list) {
      const row = document.createElement('div'); row.className = 'row'; row.style.marginTop = 'var(--gap)';
      row.innerHTML = '<button class="btn ghost" type="button" data-goset="backup">💾 記録のバックアップ（設定タブ）</button>';
      rec.insertBefore(row, list);
    }
    document.addEventListener('tengel:tab', e => { if (e.detail === 'set') { TengelLocal.ready.then(() => { paintSlots(false); paintBackup(); }).catch(() => {}); } });
    document.addEventListener('tengel:slots', () => { if ($('#slotList')) TengelLocal.ready.then(() => paintSlots(false)).catch(() => {}); });
    TengelLocal.ready.then(() => { paintSlots(false); paintBackup(); (TengelLocal.notices || []).forEach(n => toast(n, 4200)); }).catch(() => {});
    setTimeout(() => checkUpdate(false), 2500);
    document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible') checkUpdate(false); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
