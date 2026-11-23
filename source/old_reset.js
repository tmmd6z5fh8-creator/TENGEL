// 古い 台帳の リセット（第4.212版・App Store版 だけ：build_pwa.py が TARGET=app の ときに 入れる）
//   まさちゃん 2026/11/23 10:14「古い台帳は、3年おきにリセットされるようにして！注意書も入れて！そのかわり、思い出レースや思い出フィギュアは残るようによろしく！」
//     答え：消す もの＝「両方」（記録タブの 古い レース・ポイントの 履歴の 古い 行）／消し方＝「いつも直近3年分を残す」（3年 たった 分から 順に 自動で 消える。消える 30日前から 知らせる）
//   10:26「3年経ってなくても、古い台帳をリセットする、ができる項目を追加して 古い台帳をリセットする、をタップすると 3年分、2年分、1年分、全て が選べるようにして！
//     最後リセットをする前に、本当にリセットする？リセットを一度するともう消した台帳は戻せないよ！を注意書で入れて！」
//     答え「古い方から 1年分を消す」（○年分＝古い 方から ○年分）・10:30「でも3年に一回は自動リセットするのはつけてね！ やっぱり、選択は古い台帳の2年分、1年分、全て、を選べるようにして！」
//
//   ■ のこす もの（どの リセットでも 消さない）：思い出の レース（記録の mem）・思い出フィギュア（財布の figs）・ポイントの 残高・解放した もの・受け取った ミッション・
//     ミッションに 数えた レースの 数（財布の counted）・マザーデータ（races）・買い目の 設定
//   ■ 消す もの：
//     ・記録（bets：買った レース・予約・諦めた／締切済みの レース・5連の 記録）の うち、思い出で ない もの → TengelLocal.delBets（app_target.py の V212_INDEX が 足す：1回の 書きこみ）
//     ・ポイントの 履歴 → 財布の できごとを 1行に まとめる（points.js の compact・points_ui.js の TengelWallet.old：残高・解放は かわらない）
//   ■ 自動（いつも 直近 3年分を のこす）：
//     ・ポイントの 履歴：アプリを 開いた とき、3年より 前を まとめる（TengelWallet.old.auto）
//     ・記録：レースの 日付（date）で 見る。知らせて から 30日 たった ぶん だけ 消す ＝ 3年〜3年と 30日で 消える：
//       知らせ f＝{ line（この 日付より 前を 消す）, at（知らせ はじめた 時刻） } を 設定（oldreset）に おぼえる。at から 30日 たったら、line より 前の 記録を 消して、次の 知らせ
//       （line＝その 日の 3年前 ＋ 30日）を 始める。知らせた あとに 入れた・直した 記録（updatedAt が at より あと）は 次の 回（日付の 打ちまちがいを すぐ 消さない）
//       知らせて いる 数（f.n）より 増えた とき（バックアップから 戻した 古い 記録・思い出から 外した 記録）は、知らせを 始めから（そこから 30日）→ どの 記録も 知らせて から 30日は 消えない
//     ・時刻は 時計の 番人（clock_guard.js）。インターネットの 時刻で たしかめて ある とき（TengelClock.sure）だけ 動く（iPhone の 日付が まちがって いても 消さない）
//     ・記録タブの 上に 知らせ（消える 記録が ある とき だけ）・設定の カードにも 予定
//   ■ 手で（設定 →「古い台帳をリセットする」）：古い 方から 2年分・1年分・全て。いちばん 古い 月（記録と 履歴の 古い 方）から 数える。
//     さいごに「本当にリセットする？ リセットを一度すると、もう消した台帳は戻せないよ！」→「リセットする」
//   字は いまの 壁紙の 字（しぼった 字）→ ここの 画面の 言葉は その 字に 入って いる 字 だけで 書く（kisekae/build_fonts.py の body_chars に この ファイルを 足した・test_iphone_only.py が 見る）
(function () {
  'use strict';
  if (!window.__NATIVE || !window.TengelLocal) return;
  var TL = window.TengelLocal, KEY = 'oldreset', YEARS = 3, DAY = 86400000, WARN = 30 * DAY;
  var S = null, checking = null, ui = { pick: false };
  var $ = function (s, el) { return (el || document).querySelector(s); };
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function toast(m, ms) { var t = $('#toast'); if (!t) return; t.textContent = m; t.hidden = false; clearTimeout(toast._t); toast._t = setTimeout(function () { t.hidden = true; }, ms || 3600); }
  function num(n) { return Math.round(+n || 0).toLocaleString('ja-JP'); }
  function p2(n) { return (n < 10 ? '0' : '') + n; }
  function ymd(ms) { var d = new Date(ms); return d.getFullYear() + '-' + p2(d.getMonth() + 1) + '-' + p2(d.getDate()); }
  function jp(s) { var m = /^(\d{4})-(\d\d)-(\d\d)$/.exec(String(s || '')); return m ? (+m[1]) + '年' + (+m[2]) + '月' + (+m[3]) + '日' : ''; }
  function md(ms) { var d = new Date(ms); return (d.getMonth() + 1) + '月' + d.getDate() + '日'; }
  function wallet() { var w = window.TengelWallet; return w && w.on && w.old ? w : null; }
  function clock() { var c = window.TengelClock; return c && typeof c.now === 'function' ? c.now() : Date.now(); }
  function sure() { var c = window.TengelClock; return !!(c && typeof c.sure === 'function' && c.sure()); }
  function bets() { var out = []; try { TL.mem.bets.forEach(function (b) { if (b && typeof b === 'object' && b.id) out.push(b); }); } catch (e) { /* なし */ } return out; }
  function dateOf(b) { var d = String(b.date || ''); return /^\d{4}-\d\d-\d\d$/.test(d) ? d : ''; }
  function stampOf(b) { var t = Date.parse(b.updatedAt || b.createdAt || ''); return isFinite(t) ? t : 0; }
  function keeps(b) { return !!b.mem; }                                  // 思い出の レースは 消さない
  function norm(v) {
    var o = v && typeof v === 'object' ? v : {}, f = o.f && typeof o.f === 'object' && /^\d{4}-\d\d-\d\d$/.test(String(o.f.line || '')) && isFinite(+o.f.at) && +o.f.at > 0 ? { line: String(o.f.line), at: +o.f.at, n: Math.max(0, Math.round(+o.f.n || 0)) } : null;
    var l = o.last && typeof o.last === 'object' && isFinite(+o.last.at) ? { at: +o.last.at, n: Math.max(0, Math.round(+o.last.n || 0)), line: String(o.last.line || '') } : null;
    return { v: 1, f: f, last: l };
  }
  function line3(now) { var d = new Date(now); d.setFullYear(d.getFullYear() - YEARS); return ymd(d.getTime() + WARN); }      // 次の 知らせの 線：30日 あとに 3年 たって いる 日付
  // 知らせて いる 記録（f の 線より 前・思い出で ない・知らせ より 前に 入れた もの）
  function pending(st) { var f = st && st.f; if (!f) return []; return bets().filter(function (b) { var d = dateOf(b); return d && d < f.line && !keeps(b) && stampOf(b) < f.at; }); }
  function after() { try { if (typeof window.syncNotify === 'function') window.syncNotify(); } catch (e) { /* なし */ } paint(); }
  // アプリを 開いた ときの 画面（#gate：html.gateon）が 出て いる あいだは 待つ（2分 たっても 出て いたら 待たない：login_bonus.js と 同じ）
  function whenClear(fn) { var tries = 0, go = function () { if (document.documentElement.classList.contains('gateon') && tries++ < 400) { setTimeout(go, 300); return; } fn(); }; go(); }

  // ---------- 自動（いつも 直近 3年分を のこす） ----------
  // ポイントの 履歴（3年より 前を 1行に まとめる：財布の TengelWallet.old.auto）。記録の たしかめとは べつに 動く（どちらかが とちゅうでも もう 片方を とばさない）
  function histAuto() {
    var w = wallet(); if (!w) return Promise.resolve(null);
    try { return Promise.resolve(w.old.auto()).then(function (r) { paint(); return r; }, function () { return null; }); } catch (e) { return Promise.resolve(null); }
  }
  // light＝true：記録の 知らせ だけ 見る（タブを 開いた とき：ポイントの 履歴の まとめは しない）
  function autoCheck(light) {
    var a = recCheck();
    return light ? a : Promise.all([histAuto(), a]).then(function () { }, function () { });
  }
  function recCheck() {
    if (checking) return checking;
    checking = Promise.resolve(TL.ready).then(function () { return TL.getSetting(KEY); }).then(function (v) {
      var st = norm(v);
      if (!sure()) { S = st; return null; }                      // インターネットの 時刻で たしかめて ある とき だけ
      var now = clock(), changed = false, p = Promise.resolve();
      if (st.f) {
        var list = pending(st), line = st.f.line;
        if (list.length > st.f.n) { st.f = null; changed = true; }                        // 知らせた あとに 増えた（戻した 古い 記録 など）→ 知らせを 始めから
        else if (now - st.f.at >= WARN) {                        // 知らせて から 30日 たった：その 線より 前を 消す
          var ids = list.map(function (b) { return b.id; });
          st.f = null; changed = true;
          if (ids.length) p = TL.delBets(ids).then(function (n) {
            st.last = { at: now, n: n, line: line };
            if (n > 0) whenClear(function () { toast('3年たった記録 ' + num(n) + '件を消したよ（思い出のレースは残っているよ）', 5200); });      // アプリを 開いた ときの 画面が 出て いる あいだは 待つ（知らせが その うしろで 消えない ように）
          });
        }
        else if (list.length !== st.f.n) { st.f.n = list.length; changed = true; }       // 減った（消した・直した・思い出に した）
      }
      return p.then(function () {
        if (!st.f) { st.f = { line: line3(now), at: now, n: 0 }; st.f.n = pending(st).length; changed = true; }
        S = st;
        return changed ? TL.putSetting(KEY, st) : null;
      });
    }).then(function () { after(); }, function () { paint(); }).then(function () { checking = null; });
    return checking;
  }

  // テスト版 だけ（window.__TEST：build_pwa.py の TENGEL_TEST=1）：自動の リセットを 30日 待たずに ためす（知らせを 始めた 時刻を 30日 前に した ことに する → すぐ 見直す）。
  //   App Store版では 何も しない（ボタンも 出ない）。3年 より 前の 日付の 記録が あって、知らせが 出て いる とき だけ 意味が ある
  function idle() { return checking ? checking.then(idle, idle) : Promise.resolve(); }      // とちゅうの たしかめが 終わる まで 待つ
  function testSkip() {
    if (window.__TEST !== true) return Promise.resolve(false);
    return Promise.resolve(TL.ready).then(idle).then(function () { return TL.getSetting(KEY); }).then(function (v) {
      var st = norm(v); if (!st.f) return false;
      st.f.at -= WARN;
      return TL.putSetting(KEY, st).then(idle).then(function () { return recCheck(); }).then(function () { return true; });
    }).catch(function () { return false; });
  }

  // ---------- 手で：古い 方から ○年分・全て ----------
  // いちばん 古い 月（思い出で ない 記録の 日付・ポイントの 履歴の いちばん 古い 行）→ { y, m }（何も なければ null）
  function oldest() {
    var best = '';
    bets().forEach(function (b) { var d = dateOf(b); if (d && !keeps(b) && (!best || d < best)) best = d; });
    var w = wallet(), h = w ? +w.old.first() || 0 : 0;
    if (h > 0) { var hd = ymd(h); if (!best || hd < best) best = hd; }
    return best ? { y: +best.slice(0, 4), m: +best.slice(5, 7) } : null;
  }
  // えらんだ 分（years＝2・1、'all'＝全て）で 消える もの → { key, label, range, ids, recs, hist, cutMs }
  function plan(years) {
    var o = oldest(), w = wallet(), all = years === 'all', list = bets().filter(function (b) { return !keeps(b); });
    if (all) {
      var now = clock() + 1000;
      return { key: 'all', label: '全て', range: o ? o.y + '年' + o.m + '月〜今' : '', ids: list.map(function (b) { return b.id; }), recs: list.length, hist: w ? w.old.rows() : 0, cutMs: now };
    }
    var n = Math.max(1, Math.round(+years || 0));
    if (!o) return { key: String(n), label: '古い方から' + n + '年分', range: '', ids: [], recs: 0, hist: 0, cutMs: 0 };
    var cut = new Date(o.y + n, o.m - 1, 1), cutStr = ymd(cut.getTime()), end = new Date(o.y + n, o.m - 2, 1);
    var ids = list.filter(function (b) { var d = dateOf(b); return d && d < cutStr; }).map(function (b) { return b.id; });
    return { key: String(n), label: '古い方から' + n + '年分', range: o.y + '年' + o.m + '月〜' + end.getFullYear() + '年' + (end.getMonth() + 1) + '月', ids: ids, recs: ids.length, hist: w ? w.old.count(cut.getTime()) : 0, cutMs: cut.getTime() };
  }
  function run(pl) {
    var w = wallet();
    return Promise.resolve(pl.ids.length ? TL.delBets(pl.ids) : 0).then(function (n) {
      return Promise.resolve(w && pl.cutMs ? w.old.compact(pl.cutMs) : null).then(function (r) { return { recs: n, hist: r ? r.merged : 0 }; });
    }).then(function (res) { after(); return res; });
  }
  // さいごの たしかめ：「本当にリセットする？」→ リセット した ときは { recs, hist }・やめた ときは null
  function confirmRun(pl) {
    return new Promise(function (done) {
      if (!$('#oldCss')) {
        var st = document.createElement('style'); st.id = 'oldCss';
        st.textContent = '#oldOv{position:fixed;left:0;top:0;right:0;bottom:0;z-index:140;display:flex;align-items:center;justify-content:center;padding:calc(var(--sat,0px) + 16px) 16px calc(var(--sab,0px) + 16px);background:rgba(8,12,24,.6);-webkit-tap-highlight-color:transparent}'
          + '#oldOv .oldbox{width:100%;max-width:340px;box-sizing:border-box;background:var(--surface,#fff);color:var(--ink,#1b2333);border:2px solid var(--bad,#b3261e);border-radius:14px;padding:18px 16px 16px;font-family:var(--font-body);font-size:14px;line-height:1.7;box-shadow:0 10px 36px rgba(0,0,0,.4)}'
          + '#oldOv h2{margin:0 0 8px;font-size:18px;line-height:1.4}#oldOv p{margin:0 0 8px}#oldOv .oldwarn{color:var(--bad,#b3261e);font-weight:700}#oldOv .oldsm{font-size:12.5px;color:var(--muted,#667)}'
          + '#oldOv .row{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}#oldOv .row .btn{flex:1 1 auto}#oldOv .btn.danger{background:var(--bad,#b3261e);border-color:var(--bad,#b3261e);color:#fff}';
        document.head.appendChild(st);
      }
      var old = $('#oldOv'); if (old) old.remove();
      var ov = document.createElement('div'); ov.id = 'oldOv'; ov.setAttribute('role', 'alertdialog'); ov.setAttribute('aria-modal', 'true'); ov.setAttribute('aria-label', '古い台帳のリセットの確認');
      ov.innerHTML = '<div class="oldbox"><h2>本当にリセットする？</h2><p class="oldwarn">リセットを一度すると、もう消した台帳は戻せないよ！</p>'
        + '<p>消すもの：<b>' + esc(pl.label) + '</b>' + (pl.range ? '（' + esc(pl.range) + '）' : '') + '<br>レースの記録 <b>' + num(pl.recs) + '件</b>・ポイントの履歴 <b>' + num(pl.hist) + '行</b></p>'
        + '<p class="oldsm">思い出のレース・思い出フィギュア・ポイントの残高・解放したもの・マザーデータは残るよ。</p>'
        + '<div class="row"><button class="btn danger" type="button" data-old="go">リセットする</button><button class="btn" type="button" data-old="no">やめる</button></div></div>';
      var busy = false, shown = Date.now();
      function close(v) { ov.remove(); done(v); }
      ov.addEventListener('click', function (e) {
        var b = e.target.closest ? e.target.closest('[data-old]') : null;
        if (!b) { if (e.target === ov && !busy) close(null); return; }
        if (busy) return;
        if (b.getAttribute('data-old') === 'no') return close(null);
        if (Date.now() - shown < 600) return;                  // 窓が 出て すぐの 押しまちがい（2回 押し）で 消さない
        busy = true; b.disabled = true;
        run(pl).then(function (res) { close(res); }, function () { busy = false; b.disabled = false; toast('リセットできなかったよ。もう一度ためしてね', 4200); });
      });
      document.body.appendChild(ov);
      try { var nb = $('[data-old=no]', ov); if (nb) nb.focus({ preventScroll: true }); } catch (x) { /* なし */ }
    });
  }

  // ---------- 画面：設定の カード・記録タブの 知らせ ----------
  function card() {
    var c = $('#setOld'); if (c) return c;
    var set = $('#v-set'); if (!set) return null;
    c = document.createElement('div'); c.className = 'card setsec'; c.id = 'setOld'; c.style.marginTop = 'var(--gap)';
    var about = $('#setAbout'), bk = $('#setBackup');
    if (bk && bk.parentNode) bk.parentNode.insertBefore(c, bk.nextSibling); else if (about && about.parentNode) about.parentNode.insertBefore(c, about); else set.appendChild(c);
    c.addEventListener('click', onClick);
    return c;
  }
  function autoText() {
    var f = S && S.f, n = f ? pending(S).length : 0, ok = sure();
    if (!f || !n) return ok ? '今は、消える記録はないよ' : 'インターネットで時刻を確かめた後に動くよ';
    return jp(f.line) + 'より前の記録 ' + num(n) + '件が、' + md(f.at + WARN) + 'ごろに消えるよ' + (ok ? '' : '（インターネットで時刻を確かめた後に消すよ）');
  }
  function paint() {
    var c = card(), w = wallet();
    if (c) {
      var all = bets(), kept = all.filter(keeps).length, o = oldest(), rows = w ? w.old.rows() : 0, h = '';
      h += '<h2>古い台帳をリセットする</h2>';
      h += '<p class="hint">記録タブのレースの記録と、ポイントの履歴の古い分を消すよ。<b>思い出のレース・思い出フィギュア・ポイントの残高・解放したもの・マザーデータは残るよ。</b></p>';
      h += '<dl class="kvs"><dt>レースの記録</dt><dd id="soRec">' + num(all.length) + '件' + (kept ? '（うち思い出 ' + num(kept) + '件）' : '') + '</dd><dt>ポイントの履歴</dt><dd id="soHist">' + num(rows) + '行</dd>'
        + '<dt>いちばん古い月</dt><dd id="soFirst">' + (o ? o.y + '年' + o.m + '月' : 'まだないよ') + '</dd><dt>自動リセット</dt><dd id="soAuto">' + esc(autoText()) + '</dd></dl>';
      if (!ui.pick) h += '<div class="row"><button class="btn" type="button" data-so="open">古い台帳をリセットする</button></div>';
      else {
        h += '<p class="hint" style="margin:10px 0 6px"><b>どこまで消す？</b>（古い方から数えるよ）</p><div class="ptlist" id="soPick">';
        [2, 1, 'all'].forEach(function (k) {
          var pl = plan(k), none = !pl.recs && !pl.hist;
          h += '<div class="ptitem"><div><div class="pn">' + esc(pl.label) + '</div><div class="pd">' + (pl.range ? esc(pl.range) + '・' : '') + '記録 ' + num(pl.recs) + '件・履歴 ' + num(pl.hist) + '行</div></div>'
            + '<div class="row"><button class="btn' + (none ? '' : ' primary') + '" type="button" data-so="pick" data-k="' + esc(pl.key) + '"' + (none ? ' disabled' : '') + '>' + (none ? '消すものがないよ' : '選ぶ') + '</button></div></div>';
        });
        h += '</div><div class="row" style="margin-top:8px"><button class="btn ghost" type="button" data-so="close">やめる</button></div>';
      }
      h += '<div class="banner warn" style="margin-top:10px">⚠️ <b>3年たった記録と履歴は、自動でリセットされるよ。</b>消える30日前から、記録タブの上で知らせるよ。残したい記録は、先に上の「バックアップを保存」でファイルに保存してね。</div>';
      if (window.__TEST === true) h += '<div class="row" style="margin-top:8px"><button class="btn ghost" type="button" data-so="test30">テスト版：お知らせから30日たったことにする</button></div>';      // テスト版 だけ
      c.innerHTML = h;
    }
    var rec = $('#v-rec'), nb = $('#oldNote'), pend = S && S.f ? pending(S) : [];
    if (S && S.f && sure() && pend.length > S.f.n && !checking) setTimeout(function () { autoCheck(true); }, 0);      // 知らせた あとに 増えた → 知らせを 始めから
    if (rec) {
      if (!pend.length) { if (nb) nb.remove(); }
      else {
        if (!nb) { nb = document.createElement('div'); nb.id = 'oldNote'; nb.className = 'banner warn'; nb.style.marginBottom = 'var(--gap)'; rec.insertBefore(nb, rec.firstChild); }
        var left = Math.ceil((S.f.at + WARN - clock()) / DAY), when = left >= 1 ? 'あと' + left + '日（' + esc(md(S.f.at + WARN)) + 'ごろ）で' : 'もうすぐ';
        nb.innerHTML = '⚠️ <b>古い記録のお知らせ</b>：' + esc(jp(S.f.line)) + 'より前のレースの記録 <b>' + num(pend.length) + '件</b>が、' + when + '自動で消えるよ。思い出のレースは残るよ。残したいときは、設定の「バックアップ」でファイルに保存してね。';
      }
    }
  }
  function onClick(e) {
    var b = e.target.closest ? e.target.closest('[data-so]') : null; if (!b || b.disabled) return;
    var a = b.getAttribute('data-so');
    if (a === 'open') { ui.pick = true; paint(); return; }
    if (a === 'close') { ui.pick = false; paint(); return; }
    if (a === 'test30') {
      if (!sure()) { toast('インターネットで時刻を確かめた後に動くよ', 3200); return; }
      if (!(S && S.f && pending(S).length)) { toast('今は、お知らせしている記録がないよ', 3200); return; }
      testSkip(); return;
    }
    if (a === 'pick') {
      var k = b.getAttribute('data-k'), pl = plan(k === 'all' ? 'all' : +k);
      if (!pl.recs && !pl.hist) return;
      confirmRun(pl).then(function (res) {
        if (!res) return;
        ui.pick = false; paint();
        toast('古い台帳をリセットしたよ（記録 ' + num(res.recs) + '件・履歴 ' + num(res.hist) + '行）', 4600);
      });
    }
  }

  function boot() {
    var w = window.TengelWallet, c = window.TengelClock;
    Promise.resolve(TL.ready).then(function () { return w && w.ready; }).then(function () { return c && c.ready; }, function () { }).then(function () { paint(); return autoCheck(); }, function () { paint(); });
    document.addEventListener('tengel:wallet', function () { paint(); });
    document.addEventListener('tengel:clock', function (e) { if (e && e.detail && e.detail.how === 'net') autoCheck(); });      // インターネットの 時刻で たしかめた → 自動の リセットを 見る
    document.addEventListener('visibilitychange', function () { if (!document.hidden) autoCheck(); });
    document.addEventListener('click', function (e) { var t = e.target.closest ? e.target.closest('[role=tab][data-tab]') : null; if (t) setTimeout(function () { paint(); autoCheck(true); }, 80); });      // タブを 開いた とき（記録・設定）：数を 新しく・知らせを 見る
    setInterval(function () { if (!document.hidden) autoCheck(); }, 6 * 3600000);
  }
  window.TengelOld = { check: autoCheck, paint: paint, plan: plan, run: run, confirm: confirmRun, pending: function () { return pending(S).map(function (b) { return b.id; }); }, testSkip: testSkip, state: function () { return S ? JSON.parse(JSON.stringify(S)) : null; }, YEARS: YEARS, WARN: WARN };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
