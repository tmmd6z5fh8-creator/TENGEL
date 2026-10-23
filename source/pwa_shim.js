// ===== iPhoneアプリ版：データはこのiPhoneの中（IndexedDB）に保存する =====
// races = マザーデータ1つ目（大井）／bets = 買ったレースの記録／meta = マザーデータ2・3つ目、マザーデータの名前と使う番号、ひとつ前のデータ、設定（買い目・画像の読み取りなど）
// アプリを更新しても、この3つは消さない（データベースの作りを変えるときも、足すだけにする）
window.TENGEL_STANDALONE = 'pwa';
// ===== アプリ版（iPhone・iPadのアプリ。画面は tengel://localhost/ で開く）=====
// 共有シート（ファイルに保存）・コピー・アプリの中の自動バックアップは、アプリ（Swift）にお願いする
// ブラウザ（ホーム画面のWeb版）では window.__NATIVE = false で、ここは何もしない
window.__NATIVE = location.protocol === 'tengel:';
window.TengelNative = null;
if (window.__NATIVE) (function () {
  var seq = 0, pend = {};
  // アプリからの返事（アプリが window.__nativeReply(番号, 成功, 値) を呼ぶ）
  window.__nativeReply = function (id, ok, val) { var p = pend[id]; if (!p) return; delete pend[id]; if (ok) p.res(val); else p.rej(new Error(val || 'アプリでうまくいかなかったよ')); };
  function call(name, payload) {
    return new Promise(function (res, rej) {
      var h = window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.tengel;
      if (!h) { rej(new Error('アプリとつながっていないよ。アプリを開き直してね')); return; }
      var id = ++seq; pend[id] = { res: res, rej: rej };
      try { h.postMessage({ id: id, name: name, payload: payload }); } catch (e) { delete pend[id]; rej(e); }
    });
  }
  window.TengelNative = {
    call: call,
    info: window.__NATIVE_INFO || {},   // アプリの版（アプリが最初に入れる）
    // ファイルを共有シートで渡す（「ファイル」に保存・AirDrop・LINEなど）。渡したら true、閉じただけなら false
    share: function (name, text, mime) { return call('share', { name: name, text: String(text), mime: mime || 'application/octet-stream' }); },
    copy: function (text) { return call('copy', String(text)); },
    // アプリの中の自動バックアップ（記録・買い目・マザーデータ。APIキーは入れない）
    saveBackup: function (text) { return call('backup', { text: String(text) }); },
    // App Storeに出ている版（アプリがAppleに聞く）：{ found, version, url, notes, date }
    storeInfo: function () { return call('store', {}); },
    // 画像の文字を、この端末の中で読む（AppleのVision）。{ ok, lines:[{text,x,y,w,h,conf}], w, h, ms }。画像はどこにも送らない
    readText: function (b64) { return call('ocr', { data: b64 }); },
    // テスト用：時計・電波・ホームバーに重なる分の測り方
    layout: function () { return call('layout', {}); },
    loadBackup: function () { return fetch('__native/autobackup.json', { cache: 'no-store' }).then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; }); },
    // 拡大（2本指）：{ reset: 1倍にもどす, lock: 拡大を止める／もどす }（演出・アプリを開いた時の画面で使う）
    zoom: function (o) { return call('zoom', o || {}); },
    // キーチェーンの「しるし」（初回プレゼント・サブスクの取引の番号）：{ ok, value, has }。ユーザーのデータは入れない
    marker: function (op, key, value) { return call('marker', { op: op, key: key, value: value }); },
    // App内課金（StoreKit 2）：op＝products・buy・restore・unfinished・current・finish・status
    iap: function (op, p) { return call('iap', Object.assign({ op: op }, p || {})); }
  };
  // アプリからの知らせ（新しい取引など）：window.__nativeEvent(name, payload) → document の 'tengel:native'
  window.__nativeEvent = function (name, payload) { try { document.dispatchEvent(new CustomEvent('tengel:native', { detail: { name: name, payload: payload } })); } catch (e) {} };
  // コピーは、アプリがiPhoneのクリップボードに直接入れる
  try { Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText: function (t) { return call('copy', String(t)); } } }); } catch (e) {}
})();
(function () {
  var DBNAME = 'tengel3', mem = { races: new Map(), bets: new Map() }, lis = { races: [], bets: [] }, idb = null, ready = null;
  var notices = [], memOnly = '';
  var NOSAVE = window.__NATIVE ? 'いまはこの端末に保存できない状態だよ。アプリを閉じてから、開き直してね' : 'いまはiPhoneに保存できない状態だよ。アプリを上にスワイプして閉じてから、開き直してね';
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
  // 自分で入れたレース（アプリで入力＝src 'input'・ファイルから足した＝src 'file'）。アプリに入っているデータが新しくなっても消さない
  function rowKey(r) { return String(r.date) + '#' + (+r.r); }
  function userRows(rows) { return rows.filter(function (r) { return r && r.src; }); }
  // 新しいデータ＋自分で入れたレース（同じ日付・Rのレースが新しいデータにあれば、新しいデータのほうを使う）
  function keepUser(rows, cur) {
    var keys = {}, ids = {};
    rows.forEach(function (r) { keys[rowKey(r)] = 1; ids[r.id] = 1; });
    return rows.concat(userRows(cur).filter(function (r) { return !keys[rowKey(r)] && !ids[r.id]; }));
  }
  // 「データの更新」で入れた最後のデータの版（meta 'data'）
  var dataRec = null;
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
  function done(t) { return new Promise(function (res, rej) { t.oncomplete = function () { res(); wrote(t); }; t.onerror = function () { rej(t.error); }; t.onabort = function () { rej(t.error); }; }); }
  // 保存したら知らせる（アプリ版の自動バックアップが使う。Web版では何もしない）
  function wrote(t) { try { if (t.mode === 'readwrite' && typeof window.__tengelWrote === 'function') window.__tengelWrote(); } catch (e) {} }
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
  // 1つ目（大井）をまるごと入れ替える。info.source = 'app'（アプリに入っている版・データの更新）／'excel'（Excelファイル）／'paste'（貼り付け）
  // info.keepPrev = false のときは「ひとつ前」を残さない（アプリが自分で入れ直すとき）
  // info.keepUser = true のときは、自分で入れたレース（アプリで入力・ファイルから足した）を残す
  // info.dataVer＝入れるデータの版（「データの更新」で入れたとき。ふだんはアプリに入っている版）・info.home＝そのデータの開催場のしるし
  function replaceRaces(rows, info) {
    need();
    info = info || {}; rows = undup(rows);
    var src = info.source || 'app', prev = info.keepPrev === false ? null : prevOf(1);
    if (info.keepUser) rows = keepUser(rows, Array.from(slot1.values()));
    var t = idb.transaction(['races', 'meta'], 'readwrite'), s = t.objectStore('races');
    s.clear(); rows.forEach(function (r) { s.put(r); });
    var dv = src === 'app' ? (info.dataVer || window.__MOTHER_VER || '') : '';
    var meta = { id: 'mother', source: src, file: info.file || '', ver: src + ':' + (src === 'app' ? dv : new Date().toISOString()),
      embedded: window.__MOTHER_VER || '', dataVer: dv, at: new Date().toISOString(), n: rows.length, lastDate: lastDate(rows) };
    if (src === 'app' && Array.isArray(info.home) && info.home.length) meta.home = info.home.slice(0, 8);
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
  // レースを1つずつ足す・直す（同じ id は上書き）。アプリで入力したレースなど。「ひとつ前」は残さない（まるごと入れ替えたときだけ残す）
  function upsertRows(n, rows) {
    n = +n; if (n !== 1 && n !== 2 && n !== 3) return Promise.reject(new Error('マザーデータは1〜3だよ'));
    need();
    rows = (rows || []).filter(function (r) { return r && r.id && r.date && r.r; });
    if (n === 1) rows = undup(rows);
    if (!rows.length) return Promise.resolve(null);
    var now = new Date().toISOString();
    if (n === 1) {
      var all = new Map(slot1); rows.forEach(function (r) { all.set(r.id, r); });
      var list = Array.from(all.values());
      var meta = Object.assign({ id: 'mother', source: 'app', embedded: window.__MOTHER_VER || '', dataVer: window.__MOTHER_VER || '' }, mother1 || {}, { n: list.length, lastDate: lastDate(list), edited: now });
      var t = idb.transaction(['races', 'meta'], 'readwrite'), s = t.objectStore('races');
      rows.forEach(function (r) { s.put(r); }); t.objectStore('meta').put(meta);
      return done(t).then(function () {
        slot1 = all; mother1 = meta;
        if (slotsMeta.active === 1) { mem.races = slot1; notify('races'); }
        emitSlots(); return meta;
      });
    }
    var cur = slotDocs[n], map = new Map(((cur && cur.rows) || []).map(function (r) { return [r.id, r]; }));
    rows.forEach(function (r) { map.set(r.id, r); });
    var list2 = Array.from(map.values());
    var doc = Object.assign({ source: 'input', file: '', at: now }, withoutRows(cur) || {}, { id: 'slot:' + n, rows: list2, n: list2.length, lastDate: lastDate(list2), edited: now });
    return putMeta(doc).then(function () {
      slotDocs[n] = doc; slotMaps[n] = null;
      if (slotsMeta.active === n) { mem.races = slotMap(n); notify('races'); }
      emitSlots(); return doc;
    });
  }
  // レースを消す（id で）
  function removeRows(n, ids) {
    n = +n; if (n !== 1 && n !== 2 && n !== 3) return Promise.reject(new Error('マザーデータは1〜3だよ'));
    need();
    var gone = {}; (ids || []).forEach(function (id) { gone[id] = 1; });
    var now = new Date().toISOString();
    if (n === 1) {
      var keep = Array.from(slot1.values()).filter(function (r) { return !gone[r.id]; });
      if (keep.length === slot1.size) return Promise.resolve(null);
      if (!keep.length) return Promise.reject(new Error('1つ目は空にできないよ'));
      var meta = Object.assign({ id: 'mother', source: 'app' }, mother1 || {}, { n: keep.length, lastDate: lastDate(keep), edited: now });
      var t = idb.transaction(['races', 'meta'], 'readwrite'), s = t.objectStore('races');
      Object.keys(gone).forEach(function (id) { s.delete(id); }); t.objectStore('meta').put(meta);
      return done(t).then(function () {
        slot1 = new Map(keep.map(function (r) { return [r.id, r]; })); mother1 = meta;
        if (slotsMeta.active === 1) { mem.races = slot1; notify('races'); }
        emitSlots(); return meta;
      });
    }
    var cur = slotDocs[n]; if (!cur || !cur.rows) return Promise.resolve(null);
    var rest = cur.rows.filter(function (r) { return !gone[r.id]; });
    if (rest.length === cur.rows.length) return Promise.resolve(null);
    if (!rest.length) return clearSlot(n);
    var doc = Object.assign({}, withoutRows(cur), { id: 'slot:' + n, rows: rest, n: rest.length, lastDate: lastDate(rest), edited: now });
    return putMeta(doc).then(function () {
      slotDocs[n] = doc; slotMaps[n] = null;
      if (slotsMeta.active === n) { mem.races = slotMap(n); notify('races'); }
      emitSlots(); return doc;
    });
  }
  function slotRows(n) { return Array.from(slotMap(+n).values()); }
  function slotInfo() {
    return [1, 2, 3].map(function (n) {
      var rows = slotRows(n), ds = rows.map(function (r) { return r.date; }).filter(Boolean).sort();
      var usable = rows.filter(function (r) { return Number(r.cnt == null ? 1 : r.cnt) === 1 && r.p1 && r.p2; }).length;
      var m = n === 1 ? mother1 : slotDocs[n];
      var src = n === 1 ? (m ? (m.source || (String(m.ver || '').indexOf('paste') === 0 ? 'paste' : 'app')) : 'app') : (m ? m.source : '');
      return { n: n, name: slotsMeta.names[n] || DEFAULT_NAMES[n], count: rows.length, usable: usable, formed: wellFormed(rows), first: ds[0] || '', last: ds[ds.length - 1] || '',
        source: src, file: m ? (m.file || '') : '', at: m ? (m.at || '') : '', active: slotsMeta.active === n,
        inputN: rows.filter(function (r) { return r && r.src; }).length, edited: m ? (m.edited || '') : '' };
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
    dataRec = a[10] || null;
    var rows = a[0], meta = a[2], emb = window.__MOTHER || [], embVer = window.__MOTHER_VER || '';
    rows.forEach(function (r) { slot1.set(r.id, r); }); mother1 = meta || null;
    // 「データの更新」で入れたデータの開催場のしるし（アプリに入っているデータと別の開催場になったとき）
    if (meta && meta.source === 'app' && Array.isArray(meta.home) && meta.home.length && Array.isArray(window.__MOTHER_HOME)) window.__MOTHER_HOME = meta.home;
    if (slotsMeta.active !== 1 && !hasRows(slotsMeta.active)) slotsMeta.active = 1;
    mem.races = slotMap(slotsMeta.active);
    // 1つ目（大井）：初めて開いたとき・アプリに入っている大井データが新しくなったとき
    if (!rows.length || !meta) return replaceRaces(emb, { source: 'app', keepPrev: false });
    // 単勝・3連単・着順が1走も入っていない（形のちがうファイルを入れてしまった）ときは、アプリに入っている大井データに戻す
    if (!wellFormed(rows) && wellFormed(emb)) {
      return replaceRaces(emb, { source: 'app', keepPrev: false, keepUser: true }).then(function () {
        notices.push('「' + slotsMeta.names[1] + '」のデータが判定に使えない形（単勝・3連単・着順が入っていない）になっていたから、アプリに入っている大井データ（' + emb.length + '走）に戻したよ');
      });
    }
    if (!embVer || meta.embedded === embVer) return;
    var source = meta.source || (String(meta.ver || '').indexOf('paste') === 0 ? 'paste' : 'app');
    var nl = lastDate(emb), md = function (d) { return d ? (+d.slice(5, 7)) + '/' + (+d.slice(8, 10)) : ''; };
    var newer = '「' + slotsMeta.names[1] + '」のデータが新しくなったよ（' + emb.length + '走・' + md(nl) + 'まで）';
    // 自分で入れたレース（アプリで入力など）は残す
    var mine = userRows(rows).filter(function (r) { var k = rowKey(r); return !emb.some(function (e) { return rowKey(e) === k; }); }).length;
    var mineNote = mine ? '。自分で入れたレース（' + mine + '走）はそのまま残したよ' : '';
    if (source === 'app') {
      // 「データの更新」で入れたデータのほうが新しい（同じ）ときは、そのまま（アプリの更新で古いデータに戻さない）
      if (meta.dataVer && meta.dataVer >= embVer) { meta.embedded = embVer; mother1 = meta; return putMeta(meta); }
      // 中身が変わったとき（レースが増えた・直した）だけお知らせする
      var off = rows.filter(function (r) { return !r.src; });
      var same = off.length === emb.length && lastDate(off) === nl, k = dupCount(rows);
      return replaceRaces(emb, { source: 'app', keepPrev: false, keepUser: true }).then(function () { if (!same) notices.push('アプリの更新で、' + newer + (k ? '。重複していたレース（' + k + '走）は消したよ' : '') + mineNote); });
    }
    // まさちゃんがExcelや貼り付けで入れた大井データのほうが新しければ、そのまま残す
    var cur = { last: meta.lastDate || lastDate(rows), n: rows.length };
    if (nl > cur.last || (nl === cur.last && emb.length > cur.n)) {
      return replaceRaces(emb, { source: 'app', keepUser: true }).then(function () { notices.push('アプリの更新で、' + newer + mineNote + '。前に入れたデータは「ひとつ前のデータに戻す」で戻せるよ'); });
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
    el.textContent = window.__NATIVE ? 'アプリの保存場所が開けなかったよ（' + memOnly + '）。判定はできるけど、記録の保存はできないの。アプリを閉じてから、もう一度開いてね'
      : 'iPhoneの保存場所が開けなかったよ（' + memOnly + '）。判定はできるけど、記録の保存はできないの。アプリを上にスワイプして閉じてから、もう一度開いてね（プライベートブラウズのときは切ってね）';
    el.onclick = function () { el.remove(); };
    var show = function () { document.body.appendChild(el); };
    if (document.body) show(); else document.addEventListener('DOMContentLoaded', show);
  }
  ready = openDB().then(function (d) {
    idb = d;
    idb.onversionchange = function () { try { idb.close(); } catch (e) {} };
    var g = function (id) { return req(store('meta', 'readonly').get(id)); };
    return Promise.all([req(store('races', 'readonly').getAll()), req(store('bets', 'readonly').getAll()), g('mother'), g('slots'), g('slot:2'), g('slot:3'), g('prev:1'), g('prev:2'), g('prev:3'), g('set:ocr'), g('data')]);
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

  // ===== データの更新：1つ目のマザーデータ（アプリに入っているデータ）の新しい版を、ネットから読んで入れる =====
  // 読むのはデータ（レースの表）だけ。プログラムは読まない。入れても、自分で入れたレース・記録・設定はそのまま（前のデータは「ひとつ前」に残す）
  var ROW_NUM = ['r', 'dist', 'n', 'tan1', 's1', 'p1', 'p2', 'p3', 's5', 's10', 'umatanPay', 'sanrenPay', 'cnt'];
  function cleanRow(r) {
    var o = { id: String(r.id), date: String(r.date), venue: String(r.venue || ''), baba: String(r.baba || ''), surface: r.surface === '芝' ? '芝' : 'ダ', note: r.note == null ? '' : String(r.note).slice(0, 200) };
    ROW_NUM.forEach(function (k) { var v = r[k]; o[k] = v === null || v === undefined || v === '' || !isFinite(+v) ? null : +v; });
    if (o.cnt == null) o.cnt = 1;
    return o;
  }
  function remoteBad(doc) {
    if (!doc || doc.app !== 'tengel' || doc.kind !== 'mother' || typeof doc.ver !== 'string' || !/^\d{4}-\d{2}-\d{2}/.test(doc.ver)) return 'データの形がちがうよ';
    if (doc.minApp && String(window.__APP_VER || '') < String(doc.minApp)) return 'このデータは新しい版のアプリ用だよ。先にアプリを更新してね';
    var rows = doc.rows;
    if (!Array.isArray(rows) || rows.length < 20) return 'データのレースが少なすぎるよ';
    var ok = rows.filter(function (r) { return r && typeof r.id === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(String(r.date)) && +r.r >= 1 && +r.r <= 16; }).length;
    if (ok !== rows.length) return 'データの中に読めないレースがあるよ';
    if (wellFormed(rows) < rows.length / 2) return 'データが判定に使えない形だよ';
    return '';
  }
  // いま入っている、アプリのデータの版（アプリに入っている版か、データの更新で入れた版の新しいほう）
  function curDataVer() {
    var m = mother1 || {}, v = window.__MOTHER_VER || '';
    if ((m.source || 'app') === 'app' && m.dataVer && m.dataVer > v) v = m.dataVer;
    if (dataRec && dataRec.ver && dataRec.ver > v) v = dataRec.ver;
    return v;
  }
  function checkRemote() {
    var url = window.__DATA_URL || '';
    if (!url) return Promise.reject(new Error('この版では、データの更新は使えないよ'));
    return fetch(url + (url.indexOf('?') < 0 ? '?' : '&') + 't=' + Date.now(), { cache: 'no-store' })
      .catch(function () { throw new Error('通信できなかったよ。電波がいいところでもう一度試してね'); })
      .then(function (r) {
        if (r.status === 404) return null;   // 公開しているデータがない＝新しいデータはない
        if (!r.ok) throw new Error('確かめられなかったよ（' + r.status + '）。時間をおいてもう一度試してね');
        return r.json().catch(function () { throw new Error('データの形がちがうよ'); });
      })
      .then(function (doc) {
        if (doc === null) return { none: true, newer: false, cur: curDataVer() };
        var bad = remoteBad(doc); if (bad) throw new Error(bad);
        var ds = doc.rows.map(function (r) { return r.date; }).sort(), cur = curDataVer();
        var m = mother1 || {};
        return { ver: doc.ver, n: doc.rows.length, first: ds[0], last: ds[ds.length - 1], cur: cur, newer: doc.ver > cur,
          own: (m.source || 'app') !== 'app', mine: userRows(Array.from(slot1.values())).length, doc: doc };
      });
  }
  function applyRemote(doc) {
    var bad = remoteBad(doc); if (bad) return Promise.reject(new Error(bad));
    var rows = doc.rows.map(cleanRow), home = Array.isArray(doc.home) ? doc.home.map(String) : null;
    var before = userRows(Array.from(slot1.values())).length;
    return replaceRaces(rows, { source: 'app', keepUser: true, dataVer: doc.ver, home: home }).then(function (meta) {
      if (meta.home && Array.isArray(window.__MOTHER_HOME)) window.__MOTHER_HOME = meta.home;
      dataRec = { id: 'data', ver: doc.ver, at: new Date().toISOString(), n: rows.length };
      return putMeta(dataRec).catch(function () {}).then(function () {
        var kept = userRows(Array.from(slot1.values())).length;
        return { n: rows.length, kept: kept, dropped: Math.max(0, before - kept), last: lastDate(rows), ver: doc.ver };
      });
    });
  }

  function loadImage(file) {
    return new Promise(function (res, rej) {
      var u = URL.createObjectURL(file), im = new Image();
      im.onload = function () { URL.revokeObjectURL(u); res(im); };
      im.onerror = function () { URL.revokeObjectURL(u); rej({ code: 'image_rejected' }); };
      im.src = u;
    });
  }
  // 長い辺を max px（ふつう2000）までに縮めてJPEGにする（文字は読めるまま、送る量と料金をおさえる）
  function toJpeg(file, max, q) {
    return loadImage(file).then(function (im) {
      var w = im.naturalWidth || im.width, h = im.naturalHeight || im.height;
      if (!w || !h) throw { code: 'image_rejected' };
      var k = Math.min(1, (max || 2000) / Math.max(w, h)), c = document.createElement('canvas');
      c.width = Math.max(1, Math.round(w * k)); c.height = Math.max(1, Math.round(h * k));
      var g = c.getContext('2d'); g.fillStyle = '#fff'; g.fillRect(0, 0, c.width, c.height); g.drawImage(im, 0, 0, c.width, c.height);
      return c.toDataURL('image/jpeg', q || 0.9).split(',')[1];
    });
  }
  /*@web-only*/
  // ===== 画像の読み取り：オッズのスクショを Claude（Anthropic の API）で読む =====
  // APIキーはまさちゃんのもの。このiPhoneの中（meta 'set:ocr'）にだけ保存して、ほかには送らない（Anthropic に直接送るだけ）
  var OCR_MODELS = { std: 'claude-sonnet-5-5', eco: 'claude-haiku-5-5' };
  var OCR_SYSTEM = 'あなたは日本の競馬のオッズ画面のスクリーンショットを、正確に書き写す係です。画面に書かれている数字と文字だけを読み取り、指示された形のJSONだけを返します。説明文やコードブロックの印は付けません。';
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
  var sampleWeb = {
    hasKey: function () { return !!(ocrSet && ocrSet.key); },
    limits: function () { return Promise.resolve({ images: { maxCount: 3, mediaTypes: ['image/*'] } }); },
    json: function (prompt, opt) {
      var files = ((opt && opt.images) || []).slice(0, 3);
      return ready.then(function () {
        if (!ocrSet || !ocrSet.key) throw { code: 'need_key' };
        return Promise.all(files.map(function (f) { return toJpeg(f); }));
      }).then(function (imgs) {
        var content = imgs.map(function (b64) { return { type: 'image', source: { type: 'base64', media_type: 'image/jpeg', data: b64 } }; });
        content.push({ type: 'text', text: prompt });
        return apiCallWithFallback(ocrSet, { max_tokens: 3000, system: OCR_SYSTEM, messages: [{ role: 'user', content: content }] });
      }).then(pickJSON);
    }
  };
  // 設定タブ「保存して試す」用：このキーで読めるか
  function ocrTest(key, model) {
    var set = { key: String(key || '').trim(), model: model === 'eco' ? 'eco' : 'std' };
    return apiCallWithFallback(set, { max_tokens: 16, messages: [{ role: 'user', content: '「OK」とだけ返してください。' }] });
  }
  /*@/web-only*/
  // アプリ版：画像の文字はこの端末の中で読む（AppleのVision。APIキーも料金もいらない・どこにも送らない）。表の組み立ては ocr_local.js
  var sample = window.__NATIVE ? {
    local: true,
    limits: function () { return Promise.resolve({ images: { maxCount: 3, mediaTypes: ['image/*'] } }); },
    json: function (prompt, opt) {
      var files = ((opt && opt.images) || []).slice(0, 3);
      if (!window.TengelOCR) return Promise.reject({ code: 'ocr_failed', message: 'no parser' });
      return Promise.all(files.map(function (f) { return toJpeg(f, 2600, 0.92); })).then(function (imgs) {
        var one = function (i) {
          if (i >= imgs.length) return Promise.resolve([]);
          return window.TengelNative.readText(imgs[i]).then(function (r) {
            if (!r || !r.ok) throw { code: r && r.error === 'image_rejected' ? 'image_rejected' : 'ocr_failed', message: r && r.error };
            return one(i + 1).then(function (rest) { return [r.lines || []].concat(rest); });
          });
        };
        return one(0);
      }).then(function (all) {
        var d = window.TengelOCR.parse(all);
        d._lines = all.map(function (l) { return l.length; });
        return d;
      });
    }
  } : (typeof sampleWeb !== 'undefined' ? sampleWeb : null);
  // ファイルの保存（記録タブの「CSVで保存」）：アプリ版だけ。共有シートで渡す（閉じたら declined）
  var downloads = window.__NATIVE ? { save: function (o) { return window.TengelNative.share(o.filename, o.data, /\.csv$/i.test(o.filename || '') ? 'text/csv' : 'application/octet-stream').then(function (ok) { if (!ok) throw { code: 'declined' }; }); } } : null;
  window.claude = { use: function (n) { return Promise.resolve(n === 'db' ? db : n === 'user' ? { canEdit: function () { return Promise.resolve(true); } } : n === 'sample' ? sample : n === 'downloads' ? downloads : null); } };

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
      doc: function (n) { return n === 1 ? mother1 : slotDocs[n]; },
      // レースを1つずつ足す・直す・消す（アプリで入力したレースなど）
      upsert: function (n, rows) { return ready.then(function () { return upsertRows(n, rows); }); },
      remove: function (n, ids) { return ready.then(function () { return removeRows(n, ids); }); },
      key: rowKey
    },
    // データの更新（1つ目のマザーデータの新しい版をネットから読む。データだけ）
    data: {
      url: function () { return window.__DATA_URL || ''; },
      ver: curDataVer,
      check: function () { return ready.then(checkRemote); },
      apply: function (doc) { return ready.then(function () { return applyRemote(doc); }); }
    },
    // 画像の読み取り（APIキーはこのiPhoneの中だけ。バックアップにも入れない）
    ocr: {
      MODELS: typeof OCR_MODELS !== 'undefined' ? OCR_MODELS : {},
      get: function () { return ocrSet ? { key: ocrSet.key, model: ocrSet.model || 'std' } : null; },
      save: function (key, model) {
        var v = { key: String(key || '').trim(), model: model === 'eco' ? 'eco' : 'std' };
        return ready.then(function () { return putMeta({ id: 'set:ocr', value: v, at: new Date().toISOString() }); }).then(function () { ocrSet = v; return v; });
      },
      clear: function () { return ready.then(function () { need(); var t = idb.transaction('meta', 'readwrite'); t.objectStore('meta').delete('set:ocr'); return done(t); }).then(function () { ocrSet = null; }); },
      test: function (key, model) { return typeof ocrTest === 'function' ? ocrTest(key, model) : Promise.reject({ code: 'unsupported' }); }
    },
    // 設定（買い目など）。まだ無いときは undefined、初期に戻したときは null
    getSetting: function (key) { return ready.then(function () { return idb ? req(store('meta', 'readonly').get('set:' + key)) : undefined; }).then(function (o) { return o ? o.value : undefined; }); },
    putSetting: function (key, value) { return ready.then(function () { return putMeta({ id: 'set:' + key, value: value == null ? null : clone(value), at: new Date().toISOString() }); }); },
    getMeta: function (id) { return ready.then(function () { return idb ? req(store('meta', 'readonly').get(id)) : undefined; }); },
    putMeta: function (obj) { return ready.then(function () { return putMeta(obj); }); }
  };
  // アプリ版は画面がアプリの中にあるので、サービスワーカーは使わない
  if (!window.__NATIVE && 'serviceWorker' in navigator && (location.protocol === 'https:' || location.hostname === 'localhost')) {
    window.addEventListener('load', function () { navigator.serviceWorker.register('sw.js').catch(function () {}); });
  }
})();
