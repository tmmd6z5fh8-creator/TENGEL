// ===== iPhoneアプリ版：データはこのiPhoneの中（IndexedDB）に保存する =====
// races = テンゲル基盤データ（大井）／bets = 買ったレースの記録／meta = 基盤データの情報・設定（買い目など）
// アプリを更新しても、この3つは消さない（データベースの作りを変えるときも、足すだけにする）
window.TENGEL_STANDALONE = 'pwa';
(function () {
  var DBNAME = 'tengel3', mem = { races: new Map(), bets: new Map() }, lis = { races: [], bets: [] }, idb = null, ready = null;
  var notices = [];
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
  // 基盤データをまるごと入れ替える。info.source = 'app'（アプリに入っている版）／'excel'（Excelファイル）／'paste'（貼り付け）
  function replaceRaces(rows, info) {
    info = info || {};
    var src = info.source || 'app';
    var t = idb.transaction(['races', 'meta'], 'readwrite'), s = t.objectStore('races');
    s.clear(); rows.forEach(function (r) { s.put(r); });
    var meta = { id: 'mother', source: src, file: info.file || '', ver: src + ':' + (src === 'app' ? (window.__MOTHER_VER || '') : new Date().toISOString()),
      embedded: window.__MOTHER_VER || '', at: new Date().toISOString(), n: rows.length, lastDate: lastDate(rows) };
    t.objectStore('meta').put(meta);
    return done(t).then(function () { mem.races = new Map(rows.map(function (r) { return [r.id, r]; })); notify('races'); return meta; });
  }
  function putMeta(obj) { var t = idb.transaction('meta', 'readwrite'); t.objectStore('meta').put(obj); return done(t); }
  ready = openDB().then(function (d) {
    idb = d;
    idb.onversionchange = function () { try { idb.close(); } catch (e) {} };
    return Promise.all([req(store('races', 'readonly').getAll()), req(store('bets', 'readonly').getAll()), req(store('meta', 'readonly').get('mother'))]);
  }).then(function (a) {
    a[1].forEach(function (b) { mem.bets.set(b.id, b); });
    var rows = a[0], meta = a[2], emb = window.__MOTHER || [], embVer = window.__MOTHER_VER || '';
    if (!rows.length || !meta) return replaceRaces(emb, { source: 'app' });
    rows.forEach(function (r) { mem.races.set(r.id, r); });
    if (!embVer || meta.embedded === embVer) return;
    // アプリが更新されて、アプリに入っている基盤データの版が変わったとき
    var source = meta.source || (String(meta.ver || '').indexOf('paste') === 0 ? 'paste' : 'app');
    if (source === 'app') return replaceRaces(emb, { source: 'app' });
    // まさちゃんがExcelや貼り付けで入れた基盤データのほうが新しければ、そのまま残す
    var cur = { last: meta.lastDate || lastDate(rows), n: rows.length }, nl = lastDate(emb);
    if (nl > cur.last || (nl === cur.last && emb.length > cur.n)) {
      return replaceRaces(emb, { source: 'app' }).then(function () { notices.push('アプリの更新で、基盤データも新しい版（' + emb.length + '走）になったよ'); });
    }
    meta.embedded = embVer; return putMeta(meta);
  }).catch(function (e) {
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
    function guard() { return name === 'bets' ? ready : Promise.reject({ code: 'invalid_argument', message: '基盤データは「設定」タブの「基盤データ」から入れ替えてね' }); }
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
  // アプリ版だけの機能（基盤データの入れ替え・設定・バックアップ・更新）から使う
  window.TengelLocal = {
    ready: ready, mem: mem, notices: notices,
    replaceRaces: function (rows, info) { return ready.then(function () { return replaceRaces(rows, info || { source: 'paste' }); }); },
    motherMeta: function () { return ready.then(function () { return req(store('meta', 'readonly').get('mother')); }); },
    putBets: function (list) { return ready.then(function () { var t = idb.transaction('bets', 'readwrite'), s = t.objectStore('bets'); list.forEach(function (b) { s.put(b); }); return done(t).then(function () { list.forEach(function (b) { mem.bets.set(b.id, b); }); notify('bets'); }); }); },
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
