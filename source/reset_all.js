// ぜんぶ リセット（第4.169版：まさちゃん 2026/11/14 10:32「テスト版のみに全てをリセットできる機能つけて！」）
//   テスト版（TENGEL_TEST=1）の index.html の <head> の いちばん 先頭に だけ 入る（build_pwa.py の RESET_HEAD）。App Store版・Web版には 入らない
//   ＝ App Store版には 消す しかけ そのものが ない（しるしを 置いても 何も 起きない）。
//   2段で 動く：
//   ① run()（設定の「テスト版の道具」の「ぜんぶ リセット」→「リセット する」：points_ui.js の testCard）：画面を かくして、しるし（tengel.wipe）を 置いて、ページを 開き直す
//   ② 開き直した ページの いちばん はじめ（ほかの どの コードも 保存場所を 読む 前・前の ページの コードは もう 動いて いない）に、しるしが あれば ぜんぶ 消す：
//      ・localStorage・sessionStorage を 空に（着せ替え・トレーニングセンター・ログインボーナス・推し馬・入力の とちゅう・開いた時の画面を 見た しるし など）
//      ・IndexedDB 'tengel3' を 消す（買った レースの 記録・マザーデータ 1〜4・設定・ポイントの 台帳・データの更新の 記録）。
//        pwa_shim.js の open は 消し おわる まで 待つ（同じ 名前への お願いは 順番に 動く）→ はじめて 入れた ときと 同じに 作り直される
//      ・アプリ（Swift）へ（返事は いらない ので 番号 0）：キーチェーンの しるし 2つ（gift-first＝初回の プレゼント・granted-sub＝サブスクの 取引）を 消す・
//        自動バックアップを 空に 書きかえる（開いた ときの「前の記録が見つかったよ」を 出さない）・待たせて いる お知らせを ぜんぶ 消す
//      しるしは IndexedDB を 消し おわる まで のこす（とちゅうで アプリが 閉じても、つぎに 開いた ときに もう一度 はじめから 消す）
//      消すのが 5秒 たっても 終わらない とき（ほかの つながりが のこって いる）は「アプリを いちど 閉じて、もう一度 開いてね」・消せなかった（エラー）ときは しるしを 外して 上に 知らせる
//   消せない もの：App Store の 買い物（サンドボックスの 取引は Apple が 持って いる）・通知の 許可・ひとつ 前の 自動バックアップ（アプリの 中の ファイル。画面からは 読めない）
//   確かめ：test_reset_all.py
(function () {
  var KEY = 'tengel.wipe', DB = 'tengel3';
  var did = null, going = false;

  // 上の 小さな 札（ms＝出して おく 時間・0 なら 出した まま／wide＝長い 文：幅 88% で 折り返す。短い 文は 1行＝開いた ときの 画面の ロゴに かからない 高さ）
  function note(text, ms, wide) {
    var show = function () {
      var el = document.getElementById('wipeNote') || document.createElement('div');
      el.id = 'wipeNote'; el.setAttribute('role', 'status');
      el.style.cssText = 'position:fixed;left:50%;top:calc(var(--sat,0px) + 6px);transform:translateX(-50%);z-index:2147483646;box-sizing:border-box;background:#F3F0E6;color:#16203D;border-radius:16px;padding:5px 14px;font:700 13px/1.45 "Hiragino Sans",sans-serif;box-shadow:0 4px 14px rgba(0,0,0,.35);pointer-events:none;text-align:center;'
        + (wide ? 'width:88vw;white-space:normal' : 'white-space:nowrap');
      el.textContent = text; document.body.appendChild(el);
      clearTimeout(note.t);
      if (ms) note.t = setTimeout(function () { if (el.parentNode) el.parentNode.removeChild(el); }, ms);
    };
    if (document.body) show(); else document.addEventListener('DOMContentLoaded', show);
  }

  // ② ぜんぶ 消す
  function wipe() {
    did = { at: Date.now(), db: 'pending', native: 0 };
    try { localStorage.clear(); } catch (e) {}
    try { sessionStorage.clear(); } catch (e) {}
    try { localStorage.setItem(KEY, '1'); } catch (e) {}
    var done = function (s) {
      did.db = s;
      try { localStorage.removeItem(KEY); } catch (e) {}
      if (s === 'ok') note('🧪 ぜんぶ リセットしたよ', 4200);
      else note('保存場所を 消せなかったよ。もう一度「ぜんぶ リセット」を 押してね', 9000, true);      // 消せなかった：くり返しても 同じ かも しれない ので しるしは 外す（記録は のこって いる）
    };
    try {
      var rq = indexedDB.deleteDatabase(DB);
      rq.onsuccess = function () { done('ok'); };
      rq.onerror = function () { done('error'); };
      rq.onblocked = function () { did.db = 'blocked'; };
    } catch (e) { done('error'); }
    var h = null;
    try { h = window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.tengel; } catch (e) {}
    var post = function (name, payload) { try { if (h) { h.postMessage({ id: 0, name: name, payload: payload }); did.native++; } } catch (e) {} };
    post('marker', { op: 'del', key: 'gift-first' });
    post('marker', { op: 'del', key: 'granted-sub' });
    post('backup', { text: JSON.stringify({ reset: true, bets: [] }) });
    post('notify', { op: 'sync', items: [] });
    // 保存場所を 消すのが 終わらない とき（ほかの つながりが のこって いる）：アプリを 閉じて 開き直して もらう（しるしが のこって いる ので つぎに 開いた ときに 消える）
    setTimeout(function () { if (did.db === 'pending' || did.db === 'blocked') note('リセットの とちゅうだよ。アプリを いちど 閉じて、もう一度 開いてね', 0, true); }, 5000);
  }

  var armed = false;
  try { if (sessionStorage.getItem(KEY) === '1') armed = true; } catch (e) {}
  try { if (localStorage.getItem(KEY) === '1') armed = true; } catch (e) {}
  if (armed) wipe();

  // ① しるしを 置いて 開き直す
  function run() {
    if (going) return; going = true;
    var el = document.createElement('div');
    el.id = 'wipeCover'; el.setAttribute('role', 'alert');
    el.style.cssText = 'position:fixed;inset:0;z-index:2147483647;background:#16203D;color:#F3F0E6;display:flex;align-items:center;justify-content:center;font:700 18px/1.6 "Hiragino Sans",sans-serif;letter-spacing:.04em';
    el.textContent = 'リセットして いるよ…';
    document.body.appendChild(el);
    try { sessionStorage.setItem(KEY, '1'); } catch (e) {}
    try { localStorage.setItem(KEY, '1'); } catch (e) {}
    setTimeout(function () { location.reload(); }, 400);
  }

  window.TengelReset = { run: run, did: function () { return did; } };
})();
