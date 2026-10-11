// ===== iPhoneアプリ版：データはこのiPhoneの中（IndexedDB）に保存する =====
// races = マザーデータ1つ目（大井）／bets = 買ったレースの記録／meta = マザーデータ2・3つ目、マザーデータの名前と使う番号、設定（買い目など）
// アプリを更新しても、この3つは消さない（データベースの作りを変えるときも、足すだけにする）
window.TENGEL_STANDALONE = 'pwa';
(function () {
  var DBNAME = 'tengel3', mem = { races: new Map(), bets: new Map() }, lis = { races: [], bets: [] }, idb = null, ready = null;
  var notices = [];
  // マザーデータは3つ。1つ目＝大井（races ストア）、2・3つ目＝meta の 'slot:2' 'slot:3'
  var DEFAULT_NAMES = { 1: '大井競馬', 2: 'JRA', 3: '船橋競馬' };
  var slotsMeta = { id: 'slots', active: 1, names: { 1: DEFAULT_NAMES[1], 2: DEFAULT_NAMES[2], 3: DEFAULT_NAMES[3] } };
  var slot1 = new Map(), mother1 = null, slotDocs = { 2: null, 3: null }, slotMaps = { 2: null, 3: null };
  function req(r) { return new Promise(function (res, rej) { r.onsuccess = function () { res(r.result); }; r.onerror = function () { rej(r.error); }; }); }
  function openDB() {
    return new Promise(function (res, rej) {
      var r = indexedDB.open(DBNAME, 1);
      r.onupgradeneeded = function () { var d = r.result; ['races', 'bets', 'meta'].forEach(function (s) { if (!d.objectStoreNames.contains(s)) d.createObjectStore(s, { keyPath: 'id' }); }); };
      r.onsuccess = function () { res(r.result); }; r.onerror = function () { rej(r.error); };
      r.onblocked = function () { rej(new Error('ほかの画面でアプリが開いたままみたい。いったん全部閉じてから開き直してね')); };
    });
  }
  function store(name, mode) { return idb.transaction(name, mode).objectStore(name); }
  function done(t) { return new Promise(function (res, rej) { t.oncomplete = res; t.onerror = function () { rej(t.error); }; t.onabort = function () { rej(t.error); }; }); }
  function lastDate(rows) { var m = ''; rows.forEach(function (r) { if (r && r.date > m) m = r.date; }); return m; }
  function putMeta(obj) { var t = idb.transaction('meta', 'readwrite'); t.objectStore('meta').put(obj); return done(t); }
  function hasRows(n) { return n === 1 ? slot1.size > 0 : !!(slotDocs[n] && slotDocs[n].rows && slotDocs[n].rows.length); }
  function slotMap(n) {
    if (n === 1) return slot1;
    if (!slotMaps[n]) slotMaps[n] = new Map(((slotDocs[n] && slotDocs[n].rows) || []).map(function (r) { return [r.id, r]; }));
    return slotMaps[n];
  }
  function emitSlots() { try { document.dispatchEvent(new CustomEvent('tengel:slots')); } catch (e) {} }
  // 1つ目（大井）をまるごと入れ替える。info.source = 'app'（アプリに入っている版）／'excel'（Excelファイル）／'paste'（貼り付け）
  function replaceRaces(rows, info) {
    info = info || {};
    var src = info.source || 'app';
    var t = idb.transaction(['races', 'meta'], 'readwrite'), s = t.objectStore('races');
    s.clear(); rows.forEach(function (r) { s.put(r); });
    var meta = { id: 'mother', source: src, file: info.file || '', ver: src + ':' + (src === 'app' ? (window.__MOTHER_VER || '') : new Date().toISOString()),
      embedded: window.__MOTHER_VER || '', at: new Date().toISOString(), n: rows.length, lastDate: lastDate(rows) };
    t.objectStore('meta').put(meta);
    return done(t).then(function () {
      slot1 = new Map(rows.map(function (r) { return [r.id, r]; })); mother1 = meta;
      if (slotsMeta.active === 1) { mem.races = slot1; notify('races'); }
      emitSlots(); return meta;
    });
  }
  // 2つ目・3つ目を入れ替える（1つ目は replaceRaces）
  function replaceSlot(n, rows, info) {
    n = +n; if (n === 1) return replaceRaces(rows, info);
    if (n !== 2 && n !== 3) return Promise.reject(new Error('マザーデータは1〜3だよ'));
    info = info || {};
    var doc = { id: 'slot:' + n, rows: rows, source: info.source || 'excel', file: info.file || '', at: new Date().toISOString(), n: rows.length, lastDate: lastDate(rows) };
    return putMeta(doc).then(function () {
      slotDocs[n] = doc; slotMaps[n] = null;
      if (slotsMeta.active === n) { mem.races = slotMap(n); notify('races'); }
      emitSlots(); return doc;
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
    var t = idb.transaction('meta', 'readwrite'); t.objectStore('meta').delete('slot:' + n);
    return done(t).then(function () {
      slotDocs[n] = null; slotMaps[n] = null;
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
      return { n: n, name: slotsMeta.names[n] || DEFAULT_NAMES[n], count: rows.length, usable: usable, first: ds[0] || '', last: ds[ds.length - 1] || '',
        source: src, file: m ? (m.file || '') : '', at: m ? (m.at || '') : '', active: slotsMeta.active === n };
    });
  }
  ready = openDB().then(function (d) {
    idb = d;
    idb.onversionchange = function () { try { idb.close(); } catch (e) {} };
    var g = function (id) { return req(store('meta', 'readonly').get(id)); };
    return Promise.all([req(store('races', 'readonly').getAll()), req(store('bets', 'readonly').getAll()), g('mother'), g('slots'), g('slot:2'), g('slot:3')]);
  }).then(function (a) {
    a[1].forEach(function (b) { mem.bets.set(b.id, b); });
    if (a[3]) { slotsMeta.active = +a[3].active || 1; [1, 2, 3].forEach(function (n) { if (a[3].names && a[3].names[n]) slotsMeta.names[n] = a[3].names[n]; }); }
    slotDocs[2] = a[4] || null; slotDocs[3] = a[5] || null;
    var rows = a[0], meta = a[2], emb = window.__MOTHER || [], embVer = window.__MOTHER_VER || '';
    rows.forEach(function (r) { slot1.set(r.id, r); }); mother1 = meta || null;
    if (slotsMeta.active !== 1 && !hasRows(slotsMeta.active)) slotsMeta.active = 1;
    mem.races = slotMap(slotsMeta.active);
    // 1つ目（大井）：初めて開いたとき・アプリに入っている大井データが新しくなったとき
    if (!rows.length || !meta) return replaceRaces(emb, { source: 'app' });
    if (!embVer || meta.embedded === embVer) return;
    var source = meta.source || (String(meta.ver || '').indexOf('paste') === 0 ? 'paste' : 'app');
    if (source === 'app') return replaceRaces(emb, { source: 'app' });
    // まさちゃんがExcelや貼り付けで入れた大井データのほうが新しければ、そのまま残す
    var cur = { last: meta.lastDate || lastDate(rows), n: rows.length }, nl = lastDate(emb);
    if (nl > cur.last || (nl === cur.last && emb.length > cur.n)) {
      return replaceRaces(emb, { source: 'app' }).then(function () { notices.push('アプリの更新で、「' + slotsMeta.names[1] + '」のデータも新しい版（' + emb.length + '走）になったよ'); });
    }
    meta.embedded = embVer; mother1 = meta; return putMeta(meta);
  }).then(function () { emitSlots(); }).catch(function (e) {
    var el = document.createElement('div'); el.style.cssText = 'position:fixed;left:12px;right:12px;top:12px;z-index:99;background:#A8231B;color:#fff;padding:10px 14px;border-radius:10px;font:14px/1.5 sans-serif';
    el.textContent = 'iPhoneの保存領域が使えなかったよ（' + (e && e.message || e) + '）。プライベートブラウズを切って開き直してね';
    var show = function () { document.body.appendChild(el); };
    if (document.body) show(); else document.addEventListener('DOMContentLoaded', show);
    throw e;
  });
  try { if (navigator.storage && navigator.storage.persist) navigator.storage.persist(); } catch (e) {}

  function match(d, f) { var k = f[0], op = f[1], v = f[2]; return op === '>=' ? d[k] >= v : op === '<' ? d[k] < v : op === '==' ? d[k] === v : true; }
  function snap(name, filters) {
    var docs = []; mem[name].forEach(function (d) { if (filters.every(function (f) { return match(d, f); })) docs.push({ id: d.id, exists: true, data: function () { return d; }, metadata: { fromCache: false, hasPendingWrites: false } }); });
    return { docs: docs, size: docs.length, empty: !docs.length, docChanges: function () { return []; }, metadata: { fromCache: false, hasPendingWrites: false } };
  }
  function notify(name) { lis[name].forEach(function (x) { try { x[1](snap(name, x[0])); } catch (e) {} }); }
  function clone(o) { return JSON.parse(JSON.stringify(o)); }
  function docRef(name, id) {
    function put(doc) { var t = idb.transaction(name, 'readwrite'); t.objectStore(name).put(doc); return done(t).then(function () { mem[name].set(id, doc); notify(name); }); }
    function guard() { return name === 'bets' ? ready : Promise.reject({ code: 'invalid_argument', message: 'マザーデータは「設定」タブの「マザーデータ」から入れ替えてね' }); }
    return { id: id, path: name + '/' + id,
      get: function () { return ready.then(function () { var d = mem[name].get(id); return { id: id, exists: !!d, data: function () { return d; } }; }); },
      set: function (data) { return guard().then(function () { var d = clone(data); d.id = id; return put(d); }); },
      update: function (data) { return guard().then(function () { var old = mem[name].get(id); if (!old) throw { code: 'invalid_argument', message: 'まだない記録だよ' }; var d = Object.assign(clone(old), clone(data)); d.id = id; return put(d); }); },
      delete: function () { return guard().then(function () { var t = idb.transaction(name, 'readwrite'); t.objectStore(name).delete(id); return done(t).then(function () { mem[name].delete(id); notify(name); }); }); },
      onSnapshot: function () { return function () {}; } };
  }
  function query(name, filters) {
    return { where: function (f, op, v) { return query(name, filters.concat([[f, op, v]])); }, limit: function () { return query(name, filters); }, orderBy: function () { return query(name, filters); },
      get: function () { return ready.then(function () { return snap(name, filters); }); },
      onSnapshot: function (cb) { var e = [filters, cb]; lis[name].push(e); ready.then(function () { cb(snap(name, filters)); }); return function () { lis[name] = lis[name].filter(function (x) { return x !== e; }); }; },
      doc: function (id) { return docRef(name, id); } };
  }
  var db = { collection: function (n) { return query(n, []); }, doc: function (p) { var a = p.split('/'); return docRef(a[0], a[1]); } };
  window.claude = { use: function (n) { return Promise.resolve(n === 'db' ? db : n === 'user' ? { canEdit: function () { return Promise.resolve(true); } } : null); } };
  // アプリ版だけの機能（マザーデータ・設定・バックアップ・更新）から使う
  window.TengelLocal = {
    ready: ready, mem: mem, notices: notices,
    replaceRaces: function (rows, info) { return ready.then(function () { return replaceRaces(rows, info || { source: 'paste' }); }); },
    motherMeta: function () { return ready.then(function () { return req(store('meta', 'readonly').get('mother')); }); },
    putBets: function (list) { return ready.then(function () { var t = idb.transaction('bets', 'readwrite'), s = t.objectStore('bets'); list.forEach(function (b) { s.put(b); }); return done(t).then(function () { list.forEach(function (b) { mem.bets.set(b.id, b); }); notify('bets'); }); }); },
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
      doc: function (n) { return n === 1 ? mother1 : slotDocs[n]; }
    },
    // 設定（買い目など）。まだ無いときは undefined、初期に戻したときは null
    getSetting: function (key) { return ready.then(function () { return req(store('meta', 'readonly').get('set:' + key)); }).then(function (o) { return o ? o.value : undefined; }); },
    putSetting: function (key, value) { return ready.then(function () { return putMeta({ id: 'set:' + key, value: value == null ? null : clone(value), at: new Date().toISOString() }); }); },
    getMeta: function (id) { return ready.then(function () { return req(store('meta', 'readonly').get(id)); }); },
    putMeta: function (obj) { return ready.then(function () { return putMeta(obj); }); }
  };
  if ('serviceWorker' in navigator && (location.protocol === 'https:' || location.hostname === 'localhost')) {
    window.addEventListener('load', function () { navigator.serviceWorker.register('sw.js').catch(function () {}); });
  }
})();
