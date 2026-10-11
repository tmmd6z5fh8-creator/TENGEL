// ===== iPhoneアプリ版：データはこのiPhoneの中（IndexedDB）に保存する =====
// races = マザーデータ1つ目（大井）／bets = 買ったレースの記録／meta = マザーデータ2・3つ目、マザーデータの名前と使う番号、ひとつ前のデータ、設定（買い目・画像の読み取りなど）
// アプリを更新しても、この3つは消さない（データベースの作りを変えるときも、足すだけにする）
window.TENGEL_STANDALONE = 'pwa';
(function () {
  var DBNAME = 'tengel3', mem = { races: new Map(), bets: new Map() }, lis = { races: [], bets: [] }, idb = null, ready = null;
  var notices = [], memOnly = '';
  var NOSAVE = 'いまはiPhoneに保存できない状態だよ。アプリを上にスワイプして閉じてから、開き直してね';
  // マザーデータは3つ。1つ目＝大井（races ストア）、2・3つ目＝meta の 'slot:2' 'slot:3'
  var DEFAULT_NAMES = { 1: '大井競馬', 2: 'JRA', 3: '船橋競馬' };
  var slotsMeta = { id: 'slots', active: 1, names: { 1: DEFAULT_NAMES[1], 2: DEFAULT_NAMES[2], 3: DEFAULT_NAMES[3] } };
  var slot1 = new Map(), mother1 = null, slotDocs = { 2: null, 3: null }, slotMaps = { 2: null, 3: null };
  // ひとつ前のデータ（入れ替える前の中身）。meta の 'prev:1' 'prev:2' 'prev:3'
  var prevDocs = { 1: null, 2: null, 3: null };
  // 画像の読み取りの設定（meta 'set:ocr' = { key, model }）
  var ocrSet = null;
  // 重複転記などで消したレース（アプリに入っている大井データから外したもの）。1つ目（大井）には、Excelや貼り付けで入れても入れない
  var DROP = {}; (window.__MOTHER_DROP || []).forEach(function (id) { DROP[id] = 1; });
  function undup(rows) { return rows.filter(function (r) { return !(r && DROP[r.id]); }); }
  function dupCount(rows) { var k = 0; rows.forEach(function (r) { if (r && DROP[r.id]) k++; }); return k; }
  function req(r) { return new Promise(function (res, rej) { r.onsuccess = function () { res(r.result); }; r.onerror = function () { rej(r.error); }; }); }
  function openOnce() {
    return new Promise(function (res, rej) {
      var r = indexedDB.open(DBNAME, 1);
      r.onupgradeneeded = function () { var d = r.result; ['races', 'bets', 'meta'].forEach(function (s) { if (!d.objectStoreNames.contains(s)) d.createObjectStore(s, { keyPath: 'id' }); }); };
      r.onsuccess = function () { res(r.result); }; r.onerror = function () { rej(r.error); };
      r.onblocked = function () { rej(new Error('ほかの画面でアプリが開いたままみたい。いったん全部閉じてから開き直してね')); };
    });
  }
  // iPhoneで保存場所がたまに開けないことがあるので、少し待ってもう一度だけ試す
  function openDB() { return openOnce().catch(function () { return new Promise(function (r) { setTimeout(r, 700); }).then(openOnce); }); }
  function need() { if (!idb) throw new Error(NOSAVE); }
  function store(name, mode) { need(); return idb.transaction(name, mode).objectStore(name); }
  function done(t) { return new Promise(function (res, rej) { t.oncomplete = res; t.onerror = function () { rej(t.error); }; t.onabort = function () { rej(t.error); }; }); }
  function lastDate(rows) { var m = ''; rows.forEach(function (r) { if (r && r.date > m) m = r.date; }); return m; }
  // 判定に使える形のレース（単勝1位・3連単1位・1着人気・2着人気が入っている）
  function wellFormed(rows) { var k = 0; rows.forEach(function (r) { if (r && r.tan1 > 0 && r.s1 > 0 && r.p1 > 0 && r.p2 > 0) k++; }); return k; }
  function putMeta(obj) { need(); var t = idb.transaction('meta', 'readwrite'); t.objectStore('meta').put(obj); return done(t); }
  function hasRows(n) { return n === 1 ? slot1.size > 0 : !!(slotDocs[n] && slotDocs[n].rows && slotDocs[n].rows.length); }
  function slotMap(n) {
    if (n === 1) return slot1;
    if (!slotMaps[n]) slotMaps[n] = new Map(((slotDocs[n] && slotDocs[n].rows) || []).map(function (r) { return [r.id, r]; }));
    return slotMaps[n];
  }
  function emitSlots() { try { document.dispatchEvent(new CustomEvent('tengel:slots')); } catch (e) {} }
  function withoutRows(o) { if (!o) return null; var c = {}; Object.keys(o).forEach(function (k) { if (k !== 'rows') c[k] = o[k]; }); return c; }
  // いまの中身を「ひとつ前」として残す（判定に使える形のときだけ）
  function prevOf(n) {
    var rows = slotRows(n); if (!rows.length || !wellFormed(rows)) return null;
    return { id: 'prev:' + n, rows: rows, meta: withoutRows(n === 1 ? mother1 : slotDocs[n]), at: new Date().toISOString(), n: rows.length, lastDate: lastDate(rows) };
  }
  // 1つ目（大井）をまるごと入れ替える。info.source = 'app'（アプリに入っている版）／'excel'（Excelファイル）／'paste'（貼り付け）
  // info.keepPrev = false のときは「ひとつ前」を残さない（アプリが自分で入れ直すとき）
  function replaceRaces(rows, info) {
    need();
    info = info || {}; rows = undup(rows);
    var src = info.source || 'app', prev = info.keepPrev === false ? null : prevOf(1);
    var t = idb.transaction(['races', 'meta'], 'readwrite'), s = t.objectStore('races');
    s.clear(); rows.forEach(function (r) { s.put(r); });
    var meta = { id: 'mother', source: src, file: info.file || '', ver: src + ':' + (src === 'app' ? (window.__MOTHER_VER || '') : new Date().toISOString()),
      embedded: window.__MOTHER_VER || '', at: new Date().toISOString(), n: rows.length, lastDate: lastDate(rows) };
    t.objectStore('meta').put(meta);
    if (prev) t.objectStore('meta').put(prev);
    return done(t).then(function () {
      slot1 = new Map(rows.map(function (r) { return [r.id, r]; })); mother1 = meta;
      if (prev) prevDocs[1] = prev;
      if (slotsMeta.active === 1) { mem.races = slot1; notify('races'); }
      emitSlots(); return meta;
    });
  }
  // 2つ目・3つ目を入れ替える（1つ目は replaceRaces）
  function replaceSlot(n, rows, info) {
    n = +n; if (n === 1) return replaceRaces(rows, info);
    if (n !== 2 && n !== 3) return Promise.reject(new Error('マザーデータは1〜3だよ'));
    need();
    info = info || {};
    var doc = { id: 'slot:' + n, rows: rows, source: info.source || 'excel', file: info.file || '', at: new Date().toISOString(), n: rows.length, lastDate: lastDate(rows) };
    var prev = info.keepPrev === false ? null : prevOf(n);
    var t = idb.transaction('meta', 'readwrite'), ms = t.objectStore('meta'); ms.put(doc); if (prev) ms.put(prev);
    return done(t).then(function () {
      slotDocs[n] = doc; slotMaps[n] = null; if (prev) prevDocs[n] = prev;
      if (slotsMeta.active === n) { mem.races = slotMap(n); notify('races'); }
      emitSlots(); return doc;
    });
  }
  // ひとつ前のデータに戻す（いまの中身は、こんどは「ひとつ前」になる）
  function undoSlot(n) {
    n = +n; var p = prevDocs[n];
    if (!p || !p.rows || !p.rows.length) return Promise.reject(new Error('ひとつ前のデータがないよ'));
    need();
    var cur = prevOf(n), rows = p.rows;
    if (n === 1) {
      rows = undup(rows);
      var meta = Object.assign({ source: 'excel' }, p.meta || {}, { id: 'mother', embedded: window.__MOTHER_VER || '', n: rows.length, lastDate: lastDate(rows) });
      var t = idb.transaction(['races', 'meta'], 'readwrite'), s = t.objectStore('races'), ms = t.objectStore('meta');
      s.clear(); rows.forEach(function (r) { s.put(r); }); ms.put(meta); if (cur) ms.put(cur); else ms.delete('prev:1');
      return done(t).then(function () {
        slot1 = new Map(rows.map(function (r) { return [r.id, r]; })); mother1 = meta; prevDocs[1] = cur;
        if (slotsMeta.active === 1) { mem.races = slot1; notify('races'); }
        emitSlots();
      });
    }
    var doc = Object.assign({ source: 'excel' }, p.meta || {}, { id: 'slot:' + n, rows: rows, n: rows.length, lastDate: lastDate(rows) });
    var t2 = idb.transaction('meta', 'readwrite'), m2 = t2.objectStore('meta'); m2.put(doc); if (cur) m2.put(cur); else m2.delete('prev:' + n);
    return done(t2).then(function () {
      slotDocs[n] = doc; slotMaps[n] = null; prevDocs[n] = cur;
      if (slotsMeta.active === n) { mem.races = slotMap(n); notify('races'); }
      emitSlots();
    });
  }
  function setActive(n) {
    n = +n;
    if (n !== 1 && n !== 2 && n !== 3) return Promise.reject(new Error('マザーデータは1〜3だよ'));
    if (!hasRows(n)) return Promise.reject(new Error('そのマザーデータはまだ空だよ'));
    slotsMeta.active = n;
    return putMeta(slotsMeta).then(function () { mem.races = slotMap(n); notify('races'); emitSlots(); });
  }
  function clearSlot(n) {
    n = +n; if (n !== 2 && n !== 3) return Promise.reject(new Error('1つ目（大井）は空にできないよ'));
    need();
    var prev = prevOf(n), t = idb.transaction('meta', 'readwrite'), ms = t.objectStore('meta'); ms.delete('slot:' + n); if (prev) ms.put(prev);
    return done(t).then(function () {
      slotDocs[n] = null; slotMaps[n] = null; if (prev) prevDocs[n] = prev;
      if (slotsMeta.active === n) return setActive(1);
      emitSlots();
    });
  }
  function renameSlot(n, name) {
    n = +n; if (n !== 1 && n !== 2 && n !== 3) return Promise.reject(new Error('マザーデータは1〜3だよ'));
    name = String(name == null ? '' : name).replace(/\s+/g, ' ').trim().slice(0, 16) || DEFAULT_NAMES[n];
    slotsMeta.names[n] = name;
    return putMeta(slotsMeta).then(function () { emitSlots(); return name; });
  }
  function slotRows(n) { return Array.from(slotMap(+n).values()); }
  function slotInfo() {
    return [1, 2, 3].map(function (n) {
      var rows = slotRows(n), ds = rows.map(function (r) { return r.date; }).filter(Boolean).sort();
      var usable = rows.filter(function (r) { return Number(r.cnt == null ? 1 : r.cnt) === 1 && r.p1 && r.p2; }).length;
      var m = n === 1 ? mother1 : slotDocs[n];
      var src = n === 1 ? (m ? (m.source || (String(m.ver || '').indexOf('paste') === 0 ? 'paste' : 'app')) : 'app') : (m ? m.source : '');
      return { n: n, name: slotsMeta.names[n] || DEFAULT_NAMES[n], count: rows.length, usable: usable, formed: wellFormed(rows), first: ds[0] || '', last: ds[ds.length - 1] || '',
        source: src, file: m ? (m.file || '') : '', at: m ? (m.at || '') : '', active: slotsMeta.active === n };
    });
  }
  function prevInfo(n) {
    var p = prevDocs[+n]; if (!p || !p.rows || !p.rows.length) return null;
    var rows = +n === 1 ? undup(p.rows) : p.rows;   // 戻すときに重複は入らないので、その数で見せる
    var ds = rows.map(function (r) { return r.date; }).filter(Boolean).sort(), m = p.meta || {};
    return { n: rows.length, first: ds[0] || '', last: ds[ds.length - 1] || '', at: p.at || '', source: m.source || '', file: m.file || '' };
  }
  function boot(a) {
    a[1].forEach(function (b) { mem.bets.set(b.id, b); });
    if (a[3]) { slotsMeta.active = +a[3].active || 1; [1, 2, 3].forEach(function (n) { if (a[3].names && a[3].names[n]) slotsMeta.names[n] = a[3].names[n]; }); }
    slotDocs[2] = a[4] || null; slotDocs[3] = a[5] || null;
    prevDocs[1] = a[6] || null; prevDocs[2] = a[7] || null; prevDocs[3] = a[8] || null;
    ocrSet = a[9] && a[9].value && a[9].value.key ? a[9].value : null;
    var rows = a[0], meta = a[2], emb = window.__MOTHER || [], embVer = window.__MOTHER_VER || '';
    rows.forEach(function (r) { slot1.set(r.id, r); }); mother1 = meta || null;
    if (slotsMeta.active !== 1 && !hasRows(slotsMeta.active)) slotsMeta.active = 1;
    mem.races = slotMap(slotsMeta.active);
    // 1つ目（大井）：初めて開いたとき・アプリに入っている大井データが新しくなったとき
    if (!rows.length || !meta) return replaceRaces(emb, { source: 'app', keepPrev: false });
    // 単勝・3連単・着順が1走も入っていない（形のちがうファイルを入れてしまった）ときは、アプリに入っている大井データに戻す
    if (!wellFormed(rows) && wellFormed(emb)) {
      return replaceRaces(emb, { source: 'app', keepPrev: false }).then(function () {
        notices.push('「' + slotsMeta.names[1] + '」のデータが判定に使えない形（単勝・3連単・着順が入っていない）になっていたから、アプリに入っている大井データ（' + emb.length + '走）に戻したよ');
      });
    }
    if (!embVer || meta.embedded === embVer) return;
    var source = meta.source || (String(meta.ver || '').indexOf('paste') === 0 ? 'paste' : 'app');
    var nl = lastDate(emb), md = function (d) { return d ? (+d.slice(5, 7)) + '/' + (+d.slice(8, 10)) : ''; };
    var newer = '「' + slotsMeta.names[1] + '」のデータが新しくなったよ（' + emb.length + '走・' + md(nl) + 'まで）';
    if (source === 'app') {
      // 中身が変わったとき（レースが増えた・直した）だけお知らせする
      var same = rows.length === emb.length && lastDate(rows) === nl, k = dupCount(rows);
      return replaceRaces(emb, { source: 'app', keepPrev: false }).then(function () { if (!same) notices.push('アプリの更新で、' + newer + (k ? '。重複していたレース（' + k + '走）は消したよ' : '')); });
    }
    // まさちゃんがExcelや貼り付けで入れた大井データのほうが新しければ、そのまま残す
    var cur = { last: meta.lastDate || lastDate(rows), n: rows.length };
    if (nl > cur.last || (nl === cur.last && emb.length > cur.n)) {
      return replaceRaces(emb, { source: 'app' }).then(function () { notices.push('アプリの更新で、' + newer + '。前に入れたデータは「ひとつ前のデータに戻す」で戻せるよ'); });
    }
    meta.embedded = embVer; mother1 = meta; return putMeta(meta);
  }
  // 前の版で入った重複レース（9/2など）が1つ目に残っていたら消す（Excelや貼り付けで入れたデータでも。入れた日時やファイル名はそのまま）
  function dropDups() {
    var all = Array.from(slot1.values()), k = dupCount(all);
    if (!k || !idb) return;
    var rest = undup(all), t = idb.transaction(['races', 'meta'], 'readwrite'), s = t.objectStore('races');
    all.forEach(function (r) { if (DROP[r.id]) s.delete(r.id); });
    var meta = Object.assign({ id: 'mother', source: 'app' }, mother1 || {}, { n: rest.length, lastDate: lastDate(rest) });
    t.objectStore('meta').put(meta);
    return done(t).then(function () {
      slot1 = new Map(rest.map(function (r) { return [r.id, r]; })); mother1 = meta;
      if (slotsMeta.active === 1) { mem.races = slot1; notify('races'); }
      notices.push('「' + slotsMeta.names[1] + '」から、重複していたレース（' + k + '走）を消したよ（' + rest.length + '走に）');
    });
  }
  // 保存場所が開けないときも、アプリに入っている大井データで判定はできるようにする（記録の保存はできない）
  function memoryMode(e) {
    try { if (idb) idb.close(); } catch (x) {}
    idb = null; memOnly = String(e && e.message || e || '');
    var emb = window.__MOTHER || [];
    if (!wellFormed(Array.from(slot1.values()))) { slot1 = new Map(emb.map(function (r) { return [r.id, r]; })); mother1 = null; }
    else slot1 = new Map(undup(Array.from(slot1.values())).map(function (r) { return [r.id, r]; }));
    if (!mother1) mother1 = { id: 'mother', source: 'app', n: slot1.size };
    slotsMeta.active = 1; mem.races = slot1;
    var el = document.createElement('div'); el.id = 'memOnlyBar';
    el.style.cssText = 'position:fixed;left:12px;right:12px;top:calc(env(safe-area-inset-top,0px) + 12px);z-index:99;background:#A8231B;color:#fff;padding:10px 14px;border-radius:10px;font:14px/1.5 sans-serif';
    el.textContent = 'iPhoneの保存場所が開けなかったよ（' + memOnly + '）。判定はできるけど、記録の保存はできないの。アプリを上にスワイプして閉じてから、もう一度開いてね（プライベートブラウズのときは切ってね）';
    el.onclick = function () { el.remove(); };
    var show = function () { document.body.appendChild(el); };
    if (document.body) show(); else document.addEventListener('DOMContentLoaded', show);
  }
  ready = openDB().then(function (d) {
    idb = d;
    idb.onversionchange = function () { try { idb.close(); } catch (e) {} };
    var g = function (id) { return req(store('meta', 'readonly').get(id)); };
    return Promise.all([req(store('races', 'readonly').getAll()), req(store('bets', 'readonly').getAll()), g('mother'), g('slots'), g('slot:2'), g('slot:3'), g('prev:1'), g('prev:2'), g('prev:3'), g('set:ocr')]);
  }).then(function (a) { return Promise.resolve(boot(a)).then(function () { return Promise.resolve().then(dropDups).catch(function () {}); }); }).catch(memoryMode).then(function () { emitSlots(); });
  try { if (navigator.storage && navigator.storage.persist) navigator.storage.persist(); } catch (e) {}

  function match(d, f) { var k = f[0], op = f[1], v = f[2]; return op === '>=' ? d[k] >= v : op === '<' ? d[k] < v : op === '==' ? d[k] === v : true; }
  function snap(name, filters) {
    var docs = []; mem[name].forEach(function (d) { if (filters.every(function (f) { return match(d, f); })) docs.push({ id: d.id, exists: true, data: function () { return d; }, metadata: { fromCache: false, hasPendingWrites: false } }); });
    return { docs: docs, size: docs.length, empty: !docs.length, docChanges: function () { return []; }, metadata: { fromCache: false, hasPendingWrites: false } };
  }
  function notify(name) { lis[name].forEach(function (x) { try { x[1](snap(name, x[0])); } catch (e) {} }); }
  function clone(o) { return JSON.parse(JSON.stringify(o)); }
  function docRef(name, id) {
    function put(doc) { need(); var t = idb.transaction(name, 'readwrite'); t.objectStore(name).put(doc); return done(t).then(function () { mem[name].set(id, doc); notify(name); }); }
    function guard() { return name === 'bets' ? ready : Promise.reject({ code: 'invalid_argument', message: 'マザーデータは「設定」タブの「マザーデータ」から入れ替えてね' }); }
    return { id: id, path: name + '/' + id,
      get: function () { return ready.then(function () { var d = mem[name].get(id); return { id: id, exists: !!d, data: function () { return d; } }; }); },
      set: function (data) { return guard().then(function () { var d = clone(data); d.id = id; return put(d); }); },
      update: function (data) { return guard().then(function () { var old = mem[name].get(id); if (!old) throw { code: 'invalid_argument', message: 'まだない記録だよ' }; var d = Object.assign(clone(old), clone(data)); d.id = id; return put(d); }); },
      delete: function () { return guard().then(function () { need(); var t = idb.transaction(name, 'readwrite'); t.objectStore(name).delete(id); return done(t).then(function () { mem[name].delete(id); notify(name); }); }); },
      onSnapshot: function () { return function () {}; } };
  }
  function query(name, filters) {
    return { where: function (f, op, v) { return query(name, filters.concat([[f, op, v]])); }, limit: function () { return query(name, filters); }, orderBy: function () { return query(name, filters); },
      get: function () { return ready.then(function () { return snap(name, filters); }); },
      onSnapshot: function (cb) { var e = [filters, cb]; lis[name].push(e); ready.then(function () { cb(snap(name, filters)); }); return function () { lis[name] = lis[name].filter(function (x) { return x !== e; }); }; },
      doc: function (id) { return docRef(name, id); } };
  }
  var db = { collection: function (n) { return query(n, []); }, doc: function (p) { var a = p.split('/'); return docRef(a[0], a[1]); } };

  // ===== 画像の読み取り：オッズのスクショを Claude（Anthropic の API）で読む =====
  // APIキーはまさちゃんのもの。このiPhoneの中（meta 'set:ocr'）にだけ保存して、ほかには送らない（Anthropic に直接送るだけ）
  var OCR_MODELS = { std: 'claude-sonnet-5-5', eco: 'claude-haiku-5-5' };
  var OCR_SYSTEM = 'あなたは日本の競馬のオッズ画面のスクリーンショットを、正確に書き写す係です。画面に書かれている数字と文字だけを読み取り、指示された形のJSONだけを返します。説明文やコードブロックの印は付けません。';
  function loadImage(file) {
    return new Promise(function (res, rej) {
      var u = URL.createObjectURL(file), im = new Image();
      im.onload = function () { URL.revokeObjectURL(u); res(im); };
      im.onerror = function () { URL.revokeObjectURL(u); rej({ code: 'image_rejected' }); };
      im.src = u;
    });
  }
  // 長い辺を2000pxまでに縮めてJPEGにする（文字は読めるまま、送る量と料金をおさえる）
  function toJpeg(file) {
    return loadImage(file).then(function (im) {
      var w = im.naturalWidth || im.width, h = im.naturalHeight || im.height;
      if (!w || !h) throw { code: 'image_rejected' };
      var k = Math.min(1, 2000 / Math.max(w, h)), c = document.createElement('canvas');
      c.width = Math.max(1, Math.round(w * k)); c.height = Math.max(1, Math.round(h * k));
      var g = c.getContext('2d'); g.fillStyle = '#fff'; g.fillRect(0, 0, c.width, c.height); g.drawImage(im, 0, 0, c.width, c.height);
      return c.toDataURL('image/jpeg', 0.9).split(',')[1];
    });
  }
  function apiCall(set, body, model) {
    body.model = model || OCR_MODELS[set.model] || OCR_MODELS.std;
    var ctl = typeof AbortController !== 'undefined' ? new AbortController() : null, tm = ctl ? setTimeout(function () { ctl.abort(); }, 120000) : null;
    return fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST', signal: ctl ? ctl.signal : undefined,
      headers: { 'x-api-key': set.key, 'anthropic-version': '2023-06-01', 'content-type': 'application/json', 'anthropic-dangerous-direct-browser-access': 'true' },
      body: JSON.stringify(body)
    }).catch(function () { throw { code: 'network' }; }).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (d) {
        if (tm) clearTimeout(tm);
        if (r.ok) {
          if (d.stop_reason === 'refusal') throw { code: 'refused' };
          return (d.content || []).filter(function (c) { return c && c.type === 'text'; }).map(function (c) { return c.text; }).join('');
        }
        var et = (d && d.error && d.error.type) || '', em = (d && d.error && d.error.message) || '';
        if (/credit balance|billing/i.test(em)) throw { code: 'no_credit', message: em };
        if (r.status === 401 || r.status === 403 || et === 'authentication_error' || et === 'permission_error') throw { code: 'bad_key', message: em };
        if (r.status === 404 || et === 'not_found_error') throw { code: 'bad_model', message: em };
        if (r.status === 429 || et === 'rate_limit_error') throw { code: 'rate_limited', message: em };
        if (r.status === 413 || /image/i.test(em)) throw { code: 'image_rejected', message: em };
        if (r.status >= 500 || et === 'overloaded_error' || et === 'api_error') throw { code: 'busy', message: em };
        throw { code: 'api_error', message: em || ('HTTP ' + r.status) };
      });
    }, function (e) { if (tm) clearTimeout(tm); throw e; });
  }
  // 決めたモデルが見つからないときは、標準のモデルでもう一度だけ試す
  function apiCallWithFallback(set, body) {
    return apiCall(set, JSON.parse(JSON.stringify(body))).catch(function (e) {
      if (e && e.code === 'bad_model' && set.model !== 'std') return apiCall(set, body, OCR_MODELS.std);
      throw e;
    });
  }
  function pickJSON(text) {
    var s = String(text || ''), a = s.indexOf('{'), b = s.lastIndexOf('}');
    if (a < 0 || b <= a) throw { code: 'invalid_json' };
    try { return JSON.parse(s.slice(a, b + 1)); } catch (e) { throw { code: 'invalid_json' }; }
  }
  var sample = {
    hasKey: function () { return !!(ocrSet && ocrSet.key); },
    limits: function () { return Promise.resolve({ images: { maxCount: 3, mediaTypes: ['image/*'] } }); },
    json: function (prompt, opt) {
      var files = ((opt && opt.images) || []).slice(0, 3);
      return ready.then(function () {
        if (!ocrSet || !ocrSet.key) throw { code: 'need_key' };
        return Promise.all(files.map(toJpeg));
      }).then(function (imgs) {
        var content = imgs.map(function (b64) { return { type: 'image', source: { type: 'base64', media_type: 'image/jpeg', data: b64 } }; });
        content.push({ type: 'text', text: prompt });
        return apiCallWithFallback(ocrSet, { max_tokens: 3000, system: OCR_SYSTEM, messages: [{ role: 'user', content: content }] });
      }).then(pickJSON);
    }
  };
  window.claude = { use: function (n) { return Promise.resolve(n === 'db' ? db : n === 'user' ? { canEdit: function () { return Promise.resolve(true); } } : n === 'sample' ? sample : null); } };

  // アプリ版だけの機能（マザーデータ・設定・バックアップ・更新・画像の読み取り）から使う
  window.TengelLocal = {
    ready: ready, mem: mem, notices: notices,
    memOnly: function () { return memOnly; },
    replaceRaces: function (rows, info) { return ready.then(function () { return replaceRaces(rows, info || { source: 'paste' }); }); },
    motherMeta: function () { return ready.then(function () { return idb ? req(store('meta', 'readonly').get('mother')) : mother1; }); },
    putBets: function (list) { return ready.then(function () { need(); var t = idb.transaction('bets', 'readwrite'), s = t.objectStore('bets'); list.forEach(function (b) { s.put(b); }); return done(t).then(function () { list.forEach(function (b) { mem.bets.set(b.id, b); }); notify('bets'); }); }); },
    // マザーデータ（3つ）
    slots: {
      DEFAULT_NAMES: DEFAULT_NAMES,
      info: slotInfo,
      rows: slotRows,
      names: function () { return clone(slotsMeta.names); },
      active: function () { return slotsMeta.active; },
      setActive: function (n) { return ready.then(function () { return setActive(n); }); },
      rename: function (n, name) { return ready.then(function () { return renameSlot(n, name); }); },
      replace: function (n, rows, info) { return ready.then(function () { return replaceSlot(n, rows, info); }); },
      clear: function (n) { return ready.then(function () { return clearSlot(n); }); },
      prev: prevInfo,
      undo: function (n) { return ready.then(function () { return undoSlot(n); }); },
      formed: wellFormed,
      doc: function (n) { return n === 1 ? mother1 : slotDocs[n]; }
    },
    // 画像の読み取り（APIキーはこのiPhoneの中だけ。バックアップにも入れない）
    ocr: {
      MODELS: OCR_MODELS,
      get: function () { return ocrSet ? { key: ocrSet.key, model: ocrSet.model || 'std' } : null; },
      save: function (key, model) {
        var v = { key: String(key || '').trim(), model: model === 'eco' ? 'eco' : 'std' };
        return ready.then(function () { return putMeta({ id: 'set:ocr', value: v, at: new Date().toISOString() }); }).then(function () { ocrSet = v; return v; });
      },
      clear: function () { return ready.then(function () { need(); var t = idb.transaction('meta', 'readwrite'); t.objectStore('meta').delete('set:ocr'); return done(t); }).then(function () { ocrSet = null; }); },
      test: function (key, model) {
        var set = { key: String(key || '').trim(), model: model === 'eco' ? 'eco' : 'std' };
        return apiCallWithFallback(set, { max_tokens: 16, messages: [{ role: 'user', content: '「OK」とだけ返してください。' }] });
      }
    },
    // 設定（買い目など）。まだ無いときは undefined、初期に戻したときは null
    getSetting: function (key) { return ready.then(function () { return idb ? req(store('meta', 'readonly').get('set:' + key)) : undefined; }).then(function (o) { return o ? o.value : undefined; }); },
    putSetting: function (key, value) { return ready.then(function () { return putMeta({ id: 'set:' + key, value: value == null ? null : clone(value), at: new Date().toISOString() }); }); },
    getMeta: function (id) { return ready.then(function () { return idb ? req(store('meta', 'readonly').get(id)) : undefined; }); },
    putMeta: function (obj) { return ready.then(function () { return putMeta(obj); }); }
  };
  if ('serviceWorker' in navigator && (location.protocol === 'https:' || location.hostname === 'localhost')) {
    window.addEventListener('load', function () { navigator.serviceWorker.register('sw.js').catch(function () {}); });
  }
})();
