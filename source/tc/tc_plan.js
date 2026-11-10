// 作戦会議（トレーニングセンターの 上の 帯の 横長の ボタン：11/09 13:04 まさちゃん）
//   ・やりたい レースを 予約：レース名・出走頭数・距離（m）・発走時間。画像から 読み取り（いまの 読み取りと 同じ しくみ・ポイントは 使わない）／手入力
//   ・予約した レースごとに 20・15・10・8・5分前の 通知を えらべる（作戦会議の「通知」を オン ＋ iPhone の 通知の 許可）
//   ・ボード：「2026年11月9日」＋ お気に入りレース一覧。その 日が すぎると 消える
//   ・メモ（第4.143版・11/10 17:49 まさちゃん「作戦会議のやりたいレースの項目に、メモが書き込めるようにして！」）：
//     レースの 札ごとに メモの 欄（そのまま 書ける・書いた そばから 保存・300字まで・行は ふえる ぶん だけ 広がる）。予約／直す の 画面にも メモの 欄。
//     その 日が すぎると レースと いっしょに 消える。通知には 出さない（ロック画面に 出る ため）
//   保存：localStorage 'tengel.plan'（{ v, on, races:[{ id, date, time, name, n, dist, venue, r, memo, notify:[分] }] }）→ 通知は tc_launch.js の TCPlanNotify と src.html の syncNotify
const TCPlan = (() => {
  const PK = 'tengel.plan', MINS = [20, 15, 10, 8, 5], MEMO_MAX = 300;
  // メモ：改行は のこす・見えない 制御の 字は 消す・300字まで（絵文字の 途中では 切らない）
  const memoClean = v => { let t = String(v == null ? '' : v).replace(/\r\n?/g, '\n').replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/g, '').slice(0, MEMO_MAX); if (/[\uD800-\uDBFF]$/.test(t)) t = t.slice(0, -1); return t; };
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const pad = n => String(n).padStart(2, '0');
  const today = () => { const d = new Date(); return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); };
  const jaDate = s => { const [y, m, d] = String(s).split('-').map(Number); return `${y}年${m}月${d}日`; };
  const WD = ['日', '月', '火', '水', '木', '金', '土'];
  const wday = s => { const [y, m, d] = String(s).split('-').map(Number); return WD[new Date(y, m - 1, d).getDay()]; };
  let P = null, root = null, edit = null, auth = '', host = null, delAsk = null;      // delAsk＝「消す」を 1回 押した レースの id（もう一度 押すと 消す）
  function load() {
    try { P = JSON.parse(localStorage.getItem(PK) || 'null'); } catch (e) { P = null; }
    if (!P || !Array.isArray(P.races)) P = { v: 1, on: false, races: [] };
    const td = today(), n0 = P.races.length;
    P.races = P.races.filter(r => r && r.date && r.date >= td);          // その 日が すぎたら 消える
    if (P.races.length !== n0) save(true);
  }
  function save(quiet) {
    try { localStorage.setItem(PK, JSON.stringify(P)); } catch (e) { /* なし */ }
    if (!quiet) resync();
  }
  function resync() { try { if (typeof window.syncNotify === 'function') window.syncNotify(); } catch (e) { /* なし */ } }
  const N = () => window.TengelNative && window.TengelNative.notify ? window.TengelNative : null;
  async function authState() { try { const n = N(); if (!n) return ''; const r = await n.notify('status'); return (r && r.auth) || ''; } catch (e) { return ''; } }
  // 第4.143版（11/10 18:05 まさちゃん「作成会議の一枚目の赤丸画面から飛び出ちゃってる！調整して！」）：予約／直す の 画面の 日付・発走時間の 欄が 右へ はみ出して いた。
  //   2つ ならびの ます（.row2）は 中身の 幅に 引っぱられて 広がる（1fr＝minmax(auto,1fr)）→ minmax(0,1fr)・ますと 欄の min-width:0・欄は max-width:100%。
  //   日付・時間の 欄は iPhone でも 中身の 幅で 広がる ことが ある ので 見た目を そろえる（appearance:none・字は 左よせ）
  const css = `
#tcPlan{--tcpf:"BIZ UDPGothic","Hiragino Sans",sans-serif;position:absolute;inset:0;z-index:60;display:flex;flex-direction:column;background:rgba(30,18,6,.55);padding-top:env(safe-area-inset-top);padding-bottom:env(safe-area-inset-bottom);font-family:"BIZ UDPGothic","Hiragino Sans",sans-serif;color:#5a3a1c;touch-action:pan-y}
#tcPlan .pp{position:relative;margin:8px auto;width:calc(100% - 16px);max-width:540px;flex:1 1 auto;min-height:0;display:flex;flex-direction:column;background:#fff8ec;border-radius:18px;box-shadow:0 8px 24px rgba(0,0,0,.4);overflow:hidden}
#tcPlan .ph{flex:none;display:flex;align-items:center;gap:8px;padding:8px 10px 8px 12px;background:linear-gradient(#f6e3bf,#efd6a8);border-bottom:2px solid #e2c48e}
#tcPlan .ph img{height:40px;max-width:60%;object-fit:contain}
#tcPlan .ph .sp{flex:1}
#tcPlan .bx{flex:none;height:36px;padding:0 14px;border-radius:18px;border:2px solid #d9b77c;background:#fff8ec;color:#7a4520;font:700 14px/1 var(--tcpf)}
#tcPlan .pb{flex:1 1 auto;min-height:0;overflow-y:auto;-webkit-overflow-scrolling:touch;padding:12px 12px 24px}
#tcPlan .board{background:#7a5232;border-radius:14px;padding:10px;box-shadow:inset 0 0 0 3px #5e3d22,inset 0 0 0 6px #9a6a40}
#tcPlan .cork{background:#e9d3a4 repeating-linear-gradient(45deg,rgba(150,110,60,.07) 0 6px,transparent 6px 12px);border-radius:8px;padding:12px 10px 14px;min-height:120px}
#tcPlan .bdt{text-align:center;font-size:22px;font-weight:700;color:#5b3412;letter-spacing:.04em;margin:2px 0 2px}
#tcPlan .bsub{text-align:center;font-size:14px;font-weight:700;color:#8a5a2a;margin:0 0 10px}
#tcPlan .dh{margin:14px 2px 6px;font-size:14px;font-weight:700;color:#5b3412;border-bottom:2px dashed rgba(91,52,18,.35);padding-bottom:3px}
#tcPlan .rc{position:relative;background:#fffdf7;border-radius:6px;padding:10px 10px 9px 12px;margin:0 0 10px;box-shadow:0 3px 0 rgba(90,55,20,.25);border-left:6px solid #e0a020}
#tcPlan .rc::before{content:"";position:absolute;top:-6px;left:50%;width:14px;height:14px;margin-left:-7px;border-radius:50%;background:radial-gradient(circle at 35% 35%,#ff9cbc,#c2456f);box-shadow:0 1px 2px rgba(0,0,0,.35)}
#tcPlan .rt{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap}
#tcPlan .tm{font-size:22px;font-weight:700;color:#c2456f;font-variant-numeric:tabular-nums}
#tcPlan .nm{font-size:16px;font-weight:700;color:#5a3a1c;word-break:break-all}
#tcPlan .mt{font-size:12.5px;color:#8a6a48;margin-top:2px}
#tcPlan .ch{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;align-items:center}
#tcPlan .ch .lb{flex:none;white-space:nowrap;font-size:12px;color:#8a6a48;margin-right:2px}
#tcPlan .nb{min-width:52px;height:30px;border-radius:15px;border:2px solid #d9b77c;background:#fff;color:#8a5a2a;font:700 12.5px/1 var(--tcpf);padding:0 8px}
#tcPlan .nb[aria-pressed="true"]{background:#e0a020;border-color:#c98a10;color:#fff}
#tcPlan .nb:disabled{opacity:.45}
#tcPlan .ra{display:flex;gap:8px;justify-content:flex-end;margin-top:8px}
#tcPlan .sb{height:30px;padding:0 12px;border-radius:15px;border:2px solid #d9b77c;background:#fff8ec;color:#7a4520;font:700 12.5px/1 var(--tcpf)}
#tcPlan .sb.del{border-color:#e7a3b4;color:#b0445f}
#tcPlan .add{display:block;width:100%;height:46px;margin:12px 0 0;border-radius:23px;border:0;background:#c2456f;color:#fff;font:700 16px/1 var(--tcpf);box-shadow:0 3px 0 #8f2f4f}
#tcPlan .empty{text-align:center;color:#8a6a48;font-size:13.5px;padding:18px 6px 8px;line-height:1.6}
#tcPlan .nt{display:flex;align-items:center;gap:10px;background:#fffdf7;border:1.5px solid #ead7b2;border-radius:12px;padding:10px 12px;margin:0 0 12px}
#tcPlan .nt .tx{flex:1;font-size:13px;line-height:1.5}
#tcPlan .nt .tx b{display:block;font-size:15px;color:#5b3412}
#tcPlan .sw{flex:none;width:58px;height:32px;border-radius:16px;border:0;background:#cdbb9a;position:relative;padding:0}
#tcPlan .sw::after{content:"";position:absolute;top:3px;left:3px;width:26px;height:26px;border-radius:50%;background:#fff;box-shadow:0 1px 2px rgba(0,0,0,.3);transition:left .15s}
#tcPlan .sw[aria-checked="true"]{background:#3f9f5a}#tcPlan .sw[aria-checked="true"]::after{left:29px}
#tcPlan .warn{font-size:12px;color:#b0445f;margin-top:4px}
#tcPlan .sb.del.ask{background:#c2456f;color:#fff;border-color:#c2456f}
#tcPlan .fm{background:#fffdf7;border:1.5px solid #ead7b2;border-radius:12px;padding:12px}
#tcPlan .fm h3{margin:0 0 8px;font-size:16px;color:#5b3412}
#tcPlan .fm label{display:block;font-size:12.5px;color:#8a6a48;margin:10px 0 4px}
#tcPlan .fm input{display:block;width:100%;min-width:0;max-width:100%;box-sizing:border-box;height:42px;margin:0;border-radius:10px;border:1.5px solid #d9b77c;background:#fff;color:#5a3a1c;font:700 16px/1 var(--tcpf);padding:0 10px;-webkit-appearance:none;appearance:none}
#tcPlan .fm .row2{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:10px}
#tcPlan .fm .row2>div{min-width:0}
#tcPlan .fm input[type=date],#tcPlan .fm input[type=time]{text-align:left;padding:0 8px}
#tcPlan .fm input::-webkit-date-and-time-value{text-align:left;margin:0}
#tcPlan .fm input::-webkit-calendar-picker-indicator{margin:0 0 0 2px;padding:0}
#tcPlan .ocr{display:flex;align-items:center;justify-content:center;gap:6px;width:100%;height:44px;border-radius:12px;border:2px dashed #c98a10;background:#fff4d6;color:#8a5a12;font:700 15px/1 var(--tcpf)}
#tcPlan .om{font-size:12.5px;color:#3f7f3a;margin-top:6px;min-height:1em}
#tcPlan .mm{display:block;width:100%;box-sizing:border-box;margin:8px 0 0;min-height:42px;border-radius:8px;border:1.5px dashed #d9b77c;background:#fff9dc;color:#5a3a1c;font:400 16px/1.45 var(--tcpf);padding:8px 10px;resize:none;overflow:hidden;-webkit-appearance:none;appearance:none}
#tcPlan .mm::placeholder,#tcPlan .fm textarea::placeholder{color:#b39a72}
#tcPlan input,#tcPlan textarea{-webkit-user-select:text;user-select:text}
#tcPlan .mm:focus{outline:0;border-style:solid;border-color:#e0a020;background:#fffdf2}
#tcPlan .fm textarea{display:block;width:100%;box-sizing:border-box;min-height:66px;border-radius:10px;border:1.5px solid #d9b77c;background:#fff;color:#5a3a1c;font:400 16px/1.45 var(--tcpf);padding:8px 10px;resize:none;overflow:hidden;-webkit-appearance:none;appearance:none}
#tcPlan .fa{display:flex;gap:10px;margin-top:14px}
#tcPlan .fa button{flex:1;height:44px;border-radius:22px;font:700 15px/1 var(--tcpf)}
#tcPlan .fa .ok{border:0;background:#c2456f;color:#fff;box-shadow:0 3px 0 #8f2f4f}
#tcPlan .fa .ng{border:2px solid #d9b77c;background:#fff8ec;color:#7a4520}
`;
  function build(el) {
    if (!document.getElementById('tcPlanCss')) { const s = document.createElement('style'); s.id = 'tcPlanCss'; s.textContent = css; document.head.appendChild(s); }
    root = document.createElement('div'); root.id = 'tcPlan'; root.setAttribute('role', 'dialog'); root.setAttribute('aria-modal', 'true'); root.setAttribute('aria-label', '作戦会議');
    root.innerHTML = `<div class="pp"><div class="ph"><img src="tc_icon_plan.webp" alt="作戦会議"><span class="sp"></span><button type="button" class="bx" data-p="close">とじる</button></div><div class="pb"></div></div><input type="file" accept="image/*" hidden data-p="file">`;
    el.appendChild(root);
    root.addEventListener('click', onClick);
    root.addEventListener('input', onInput);
    root.querySelector('[data-p=file]').addEventListener('change', onFile);
  }
  function chipRow(r) {
    return `<div class="ch"><span class="lb">通知</span>` + MINS.map(m => `<button type="button" class="nb" data-p="nt" data-id="${esc(r.id)}" data-m="${m}" aria-pressed="${(r.notify || []).includes(m)}"${P.on ? '' : ' disabled'}>${m}分前</button>`).join('') + '</div>';
  }
  // メモの 欄（札の 中）：そのまま 書ける。<textarea> は 先頭の 改行を 1つ 捨てる ので、先に 1つ 入れて おく
  const memoBox = r => `<textarea class="mm" data-p="memo" data-id="${esc(r.id)}" rows="1" maxlength="${MEMO_MAX}" placeholder="📝 メモを書く（作戦など）" aria-label="メモ" autocomplete="off" autocapitalize="off" spellcheck="false">\n${esc(r.memo || '')}</textarea>`;
  // 欄の 高さを 中身に 合わせる（行が ふえた ぶん だけ 広がる・中で スクロール しない）
  function fit(t) { if (!t) return; t.style.height = 'auto'; t.style.height = (t.scrollHeight + 3) + 'px'; }
  function fitAll() { if (root) root.querySelectorAll('textarea').forEach(fit); }
  // メモを 書いた そばから 保存（通知には かかわらない ので 通知は 入れ直さない）。予約／直す の 画面の メモは「保存」で 入る
  function onInput(e) {
    const t = e.target; if (!t || t.tagName !== 'TEXTAREA') return;
    fit(t);
    if (t.dataset.p !== 'memo' || !P) return;
    const r = P.races.find(x => x.id === t.dataset.id); if (!r) return;
    const v = memoClean(t.value); if ((r.memo || '') === v) return;
    r.memo = v; save(true);
  }
  function paint() {
    if (!root) return; const b = root.querySelector('.pb');
    if (edit) { b.innerHTML = formHtml(); fitAll(); return; }
    const td = today(), list = P.races.slice().sort((a, c) => (a.date + a.time).localeCompare(c.date + c.time));
    const off = auth === 'denied';
    let h = `<div class="nt"><div class="tx"><b>通知 ${P.on ? 'オン' : 'オフ'}</b>オンに すると、レースごとに えらんだ 時間（20・15・10・8・5分前）に お知らせするよ${off && P.on ? '<div class="warn">iPhone の 通知が オフに なってるよ。iPhone の「設定」→「通知」→「テンゲル」で 通知を 許可してね</div>' : ''}</div>`
      + `<button type="button" class="sw" role="switch" aria-checked="${!!P.on}" aria-label="通知" data-p="on"></button></div>`;
    h += `<div class="board"><div class="cork"><div class="bdt">${jaDate(td)}（${wday(td)}）</div><div class="bsub">お気に入りレース一覧</div>`;
    if (!list.length) h += '<div class="empty">まだ 予約した レースは ないよ<br>下の「＋ レースを予約」から 入れてね</div>';
    let cur = '';
    list.forEach(r => {
      if (r.date !== cur) { cur = r.date; if (r.date !== td) h += `<div class="dh">${jaDate(r.date)}（${wday(r.date)}）</div>`; }
      const meta = [r.venue ? esc(r.venue) : '', r.r ? esc(r.r) + 'R' : '', r.n ? esc(r.n) + '頭' : '', r.dist ? esc(r.dist) + 'm' : ''].filter(Boolean).join('・');
      h += `<div class="rc"><div class="rt"><span class="tm">${esc(r.time || '--:--')}</span><span class="nm">${esc(r.name || 'レース')}</span></div>${meta ? `<div class="mt">${meta}</div>` : ''}${memoBox(r)}${chipRow(r)}`
        + `<div class="ra"><button type="button" class="sb" data-p="edit" data-id="${esc(r.id)}">直す</button><button type="button" class="sb del${delAsk === r.id ? ' ask' : ''}" data-p="del" data-id="${esc(r.id)}">${delAsk === r.id ? 'ほんとに 消す？' : '消す'}</button></div></div>`;
    });
    h += `<button type="button" class="add" data-p="add">＋ レースを予約</button></div></div>`;
    b.innerHTML = h; fitAll();
  }
  function formHtml() {
    const r = edit;
    return `<div class="fm"><h3>${r._new ? 'レースを予約' : 'レースを直す'}</h3>`
      + `<button type="button" class="ocr" data-p="ocr">📷 画像から読み取る</button><div class="om" aria-live="polite">${esc(r._msg || '')}</div>`
      + `<label>レース名</label><input data-f="name" type="text" maxlength="40" value="${esc(r.name || '')}" placeholder="例）〇〇特別" autocomplete="off">`
      + `<div class="row2"><div><label>日付</label><input data-f="date" type="date" value="${esc(r.date || today())}"></div><div><label>発走時間</label><input data-f="time" type="time" value="${esc(r.time || '')}"></div></div>`
      + `<div class="row2"><div><label>出走頭数</label><input data-f="n" type="number" inputmode="numeric" min="2" max="18" value="${esc(r.n || '')}" placeholder="例）12"></div><div><label>距離（m）</label><input data-f="dist" type="number" inputmode="numeric" min="800" max="4000" step="100" value="${esc(r.dist || '')}" placeholder="例）1600"></div></div>`
      + `<label>メモ</label><textarea data-f="memo" rows="2" maxlength="${MEMO_MAX}" placeholder="例）パドックを見てから決める" aria-label="メモ" autocomplete="off" autocapitalize="off" spellcheck="false">\n${esc(r.memo || '')}</textarea>`
      + `<div class="fa"><button type="button" class="ng" data-p="cancel">やめる</button><button type="button" class="ok" data-p="save">保存</button></div></div>`;
  }
  function readForm() {
    if (!root || !edit) return; const v = k => { const i = root.querySelector(`[data-f="${k}"]`); return i ? i.value.trim() : ''; };
    edit.name = v('name'); edit.date = v('date') || today(); edit.time = v('time'); edit.n = v('n') ? Math.round(+v('n')) : ''; edit.dist = v('dist') ? Math.round(+v('dist')) : '';
    const m = root.querySelector('[data-f="memo"]'); if (m) edit.memo = memoClean(m.value);
  }
  async function onFile(e) {
    const f = e.target.files && e.target.files[0]; e.target.value = ''; if (!f || !edit) return;
    readForm(); edit._msg = '読み取り中…'; paint();
    try {
      const s = window.claude && window.claude.use ? await window.claude.use('sample') : null;
      if (!s || !s.json) throw new Error('none');
      const d = await s.json('', { images: [f] });
      const got = [];
      if (d.rname) { edit.name = d.rname; got.push('レース名'); }
      if (d.n) { edit.n = +d.n; got.push('頭数'); }
      if (d.dist) { edit.dist = +d.dist; got.push('距離'); }
      if (d.start) { edit.time = String(d.start).padStart(5, '0'); got.push('発走時間'); }
      if (d.date && /^\d{4}-\d{2}-\d{2}$/.test(d.date) && d.date >= today()) edit.date = d.date;
      if (d.venue) edit.venue = d.venue; if (d.r) edit.r = +d.r;
      edit._msg = got.length ? `読み取ったよ（${got.join('・')}）。ちがう 所は 直してね` : '読み取れなかったよ。手で 入れてね';
    } catch (er) { edit._msg = '読み取れなかったよ。手で 入れてね'; }
    paint();
  }
  async function onClick(e) {
    const a = e.target.closest('[data-p]'); if (!a) { if (delAsk) { delAsk = null; paint(); } if (e.target === root) close(); return; }
    const k = a.dataset.p;
    if (k === 'memo') { if (delAsk) { delAsk = null; const d = root.querySelector('.sb.del.ask'); if (d) { d.classList.remove('ask'); d.textContent = '消す'; } } return; }
    if (k !== 'del') delAsk = null;
    if (k === 'close') { close(); return; }
    if (k === 'on') {
      if (!P.on) {
        const n = N(); let ok = true;
        if (n) { try { const r = await n.notify('permission'); auth = (r && r.auth) || auth; ok = !!(r && (r.granted || r.auth === 'authorized' || r.auth === 'provisional')); } catch (er) { ok = false; } }
        P.on = true; save(); if (!ok) auth = 'denied';
      } else { P.on = false; save(); }
      paint(); return;
    }
    if (k === 'nt') {
      const r = P.races.find(x => x.id === a.dataset.id); if (!r) return; const m = +a.dataset.m;
      r.notify = (r.notify || []).includes(m) ? r.notify.filter(x => x !== m) : (r.notify || []).concat(m).sort((x, y) => y - x);
      save(); paint(); return;
    }
    if (k === 'add') { edit = { _new: true, id: 'p' + Date.now().toString(36), date: today(), time: '', name: '', n: '', dist: '', memo: '', notify: [] }; paint(); root.querySelector('.pb').scrollTop = 0; return; }
    if (k === 'edit') { const r = P.races.find(x => x.id === a.dataset.id); if (!r) return; edit = Object.assign({}, r); paint(); root.querySelector('.pb').scrollTop = 0; return; }
    if (k === 'del') {
      const r = P.races.find(x => x.id === a.dataset.id); if (!r) return;
      // 第4.140版（バグ直し）：アプリの 中では confirm() の 窓が 出ない（いつも「いいえ」に なる）ので、「消す」を 押しても 消せなかった
      //   → 窓は 使わない。同じ ボタンを もう一度 押すと 消す（1回めで「ほんとに 消す？」に かわる・ほかを 押すと もどる）
      if (delAsk !== r.id) { delAsk = r.id; paint(); return; }
      delAsk = null; P.races = P.races.filter(x => x.id !== r.id); save(); paint(); return;
    }
    if (k === 'cancel') { edit = null; paint(); return; }
    if (k === 'ocr') { readForm(); root.querySelector('[data-p=file]').click(); return; }
    if (k === 'save') {
      readForm(); const r = edit;
      if (!r.name && !r.time) { r._msg = 'レース名か 発走時間を 入れてね'; paint(); return; }
      if (r.date < today()) { r._msg = '今日より 前の 日は 入れられないよ'; paint(); return; }
      const out = { id: r.id, date: r.date, time: r.time, name: r.name, n: r.n || '', dist: r.dist || '', venue: r.venue || '', r: r.r || '', memo: memoClean(r.memo || '').trim(), notify: r.notify || [] };
      const i = P.races.findIndex(x => x.id === r.id); if (i >= 0) P.races[i] = out; else P.races.push(out);
      edit = null; save(); paint(); return;
    }
  }
  async function open(el) {
    host = el; load();
    if (!root) build(el); else if (root.parentNode !== el) el.appendChild(root);
    edit = null; root.style.display = 'flex'; paint();
    auth = await authState(); paint();
  }
  function close() {
    try { const f = document.activeElement; if (root && f && root.contains(f) && f.blur) f.blur(); } catch (e) { /* なし */ }      // 書いて いる 欄から ぬける（キーボードを しまう）
    if (root) root.style.display = 'none'; edit = null; delAsk = null;
  }
  function isOpen() { return !!root && root.style.display !== 'none'; }
  return { open, close, isOpen };
})();
window.TCPlan = TCPlan;
