// トレーニングセンター：お世話トークンの 購入の 窓（第4.165版・まさちゃん 2026/11/13 11:46「お世話トークンは、購入できるようにする。
//   ①1個を80Pで購入 ②5個を400Pで購入 ③10個を800Pで購入 ④15個を1200Pで購入 ②25個を2000Pで購入　お世話トークン購入、のアイコンを左下のお世話などの項目の上に設置」
//   → 12:36「お世話トークン購入のアイコンやっぱりこっちで！お世話とかのところに上手く入れられない？」・12:38「1番右側に入れて！」）
//   ・下の 列（撫でる・ごはん・おそうじ・呼ぶ）の 1番 右の「お世話トークン購入」（丸い 絵：tc_care.js が 描く）を 押すと 出る 紙の 窓。組（こ数と ポイント）は tc_app.js の BUY.info()（もとは points.js の TOKEN_PACKS）
//   ・「買う」→ その 行が「○○Pで 買う／やめる」に かわる → もう一度 押して 決まり（アプリの 中では confirm() の 窓が 出ない ので、2回 押して 決める）
//   ・買えない 組は うすく して わけを 出す：持てる 数（25こ）を こえる・ポイントが 足りない
//   ・当たりの 確率は 説明書に のって いる → 窓の 下に「説明書を 見る」（買う 前に 確かめられる ように）
//   ・ちかちか しない（光らせない）
//   TCBuy.open(el, api)・TCBuy.close()・TCBuy.isOpen()　api＝tc_app.js の BUY（info・buy・guide・se）
const TCBuy = (() => {
  const CSS = `
#tcb{position:absolute;inset:0;z-index:22;display:none;align-items:center;justify-content:center;pointer-events:auto;touch-action:auto;font-family:"BIZ UDPGothic",BIZ,"Hiragino Sans","Noto Sans CJK JP",sans-serif}
#tcb .bbk{position:absolute;inset:0;background:rgba(30,18,6,.5)}
#tcb .bsh{position:relative;width:calc(100% - 24px);max-width:420px;max-height:calc(100% - 16px);background:#fff8ec;border-radius:18px;box-shadow:0 6px 18px rgba(0,0,0,.35);overflow:hidden;display:flex;flex-direction:column}
#tcb .bhd{flex:none;display:flex;align-items:center;justify-content:space-between;gap:8px;padding:8px 12px 6px 14px;background:linear-gradient(#f6e3bf,#efd6a8);border-bottom:2px solid #e2c48e}
#tcb .bhd b{font-size:16px;color:#6b3f1d;letter-spacing:.03em}
#tcb .bx{flex:none;width:34px;height:34px;border-radius:50%;background:#fff8ec;border:2px solid #d9b77c;color:#8a5a2a;font:400 17px/1 "BIZ UDPGothic","Hiragino Sans",sans-serif;padding:0}
#tcb .bbd{flex:1 1 auto;min-height:0;overflow-y:auto;-webkit-overflow-scrolling:touch;padding:9px 12px 11px}
#tcb .bnow{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:8px;margin:0 0 6px}
#tcb .bnow div{background:#fffdf7;border:1.5px solid #ead7b2;border-radius:10px;padding:5px 6px 6px;text-align:center}
#tcb .bnow small{display:block;font-size:11px;line-height:1.4;color:#8a6a48}
#tcb .bnow b{font-size:20px;line-height:1.25;white-space:nowrap}
#tcb .bnow b i{font-style:normal;font-size:12.5px;font-weight:400;color:#9a7a55}
#tcb .bnow .tk{color:#3f7f3a}
#tcb .bnow .pt{color:#b06a12}
#tcb .bmsg{min-height:18px;margin:0 0 4px;font-size:13px;line-height:18px;font-weight:700;color:#3f7f3a;text-align:center}
#tcb .bmsg.ng{color:#b0445f}
#tcb .brow{display:flex;align-items:center;gap:8px;min-height:42px;background:#fffdf7;border:1.5px solid #ead7b2;border-radius:12px;padding:4px 7px 4px 12px;margin:0 0 5px}
#tcb .brow.cf{border-color:#3f9f5a;background:#f1faee}
#tcb .brow.off .bn,#tcb .brow.off .bc{opacity:.5}
#tcb .bn{flex:none;min-width:56px;font-size:21px;font-weight:700;color:#3f7f3a;white-space:nowrap}
#tcb .bn i{font-style:normal;font-size:13px}
#tcb .bc{flex:1 1 auto;min-width:0;font-size:15.5px;font-weight:700;color:#b06a12;white-space:nowrap}
#tcb .bb{flex:none;min-width:80px;height:40px;padding:0 12px;border-radius:20px;border:0;background:#c2456f;color:#fff;font:700 15px/1 "BIZ UDPGothic","Hiragino Sans",sans-serif;box-shadow:0 3px 0 #8f2f4f;white-space:nowrap;-webkit-tap-highlight-color:transparent}
#tcb .bb:active{transform:translateY(2px);box-shadow:0 1px 0 #8f2f4f}
#tcb .bb:disabled{opacity:.6}
#tcb .bb.go{background:#3f9f5a;box-shadow:0 3px 0 #2c7240}
#tcb .bb.go:active{box-shadow:0 1px 0 #2c7240}
#tcb .bb.no{min-width:62px;background:#fff8ec;color:#7a4520;border:2px solid #d9b77c;box-shadow:none}
#tcb .bwhy{flex:none;font-size:12px;font-weight:700;color:#b0445f;white-space:nowrap;padding-right:5px}
#tcb .bnote{margin:3px 0 0;font-size:11.5px;line-height:1.5;color:#7a5a3a}
#tcb .bnote b{color:#c2456f}
#tcb .bg{display:block;width:100%;height:36px;margin:7px 0 0;border-radius:18px;border:2px solid #d9b77c;background:#fff8ec;color:#7a4520;font:700 13px/1 "BIZ UDPGothic","Hiragino Sans",sans-serif;-webkit-tap-highlight-color:transparent}
`;
  const P = v => Number(v).toLocaleString('ja-JP') + 'P';
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const GUARD = 0.35;                  // 開いて から この 秒 だけ、うしろの 幕・✕・中の ボタンを 受けつけない（開いた 指の クリックが とどいても 閉じない・押されない）
  let root = null, api = null, conf = 0, busy = false, note = null, openedAt = -1e9, timer = 0, last = '';
  function style() { if (!document.getElementById('tcb-css')) { const st = document.createElement('style'); st.id = 'tcb-css'; st.textContent = CSS; document.head.appendChild(st); } }
  function build(el) {
    style();
    root = document.createElement('div'); root.id = 'tcb'; root.setAttribute('role', 'dialog'); root.setAttribute('aria-modal', 'true'); root.setAttribute('aria-label', 'お世話トークン購入');
    root.innerHTML = `<div class="bbk"></div><div class="bsh"><div class="bhd"><b>お世話トークン購入</b><button type="button" class="bx" aria-label="とじる">✕</button></div><div class="bbd"></div></div>`;
    el.appendChild(root);
    const shut = () => { if (!busy && performance.now() - openedAt >= GUARD * 1000) close(); };
    root.querySelector('.bx').addEventListener('click', shut);
    root.querySelector('.bbk').addEventListener('click', shut);
    for (const ev of ['pointerdown', 'pointermove', 'pointerup', 'pointercancel']) root.addEventListener(ev, e => e.stopPropagation());      // 下の フィールド（撫でる・ほうき・PUSH）へ とどけない
    // 窓は フィールドの ボタン（下の 列の 1番 右）から 指を はなした ときに 開く → その 指の クリックが、開いた ばかりの 窓の ボタン（ちょうど 下に「説明書を 見る」）に とどく ことが ある
    //   → 開いて から GUARD 秒は 中の ボタンも 受けつけない（幕・✕ と 同じ）
    root.addEventListener('click', e => { if (performance.now() - openedAt < GUARD * 1000) return; const b = e.target.closest('[data-b]'); if (b && !b.disabled) act(b.dataset.b, +b.dataset.n || 0); });
  }
  const WHY = (r, i) => r.why === 'full' ? `いまは あと ${r.room != null ? r.room : i.room}こ まで 買えるよ（持てるのは ${i.max}こ まで）`
    : r.why === 'short' ? `ポイントが 足りないよ${r.need > 0 ? `（あと ${P(r.need)}）` : ''}`
    : r.why === 'busy' ? 'ちょっと まってね' : 'うまく 買えなかったよ。もう一度 ためしてね';
  function paint() {
    if (!root || !api) return;
    const i = api.info(); last = JSON.stringify(i);
    let h = `<div class="bnow"><div><small>いまの お世話トークン</small><b class="tk" data-v="stock">${i.stock}<i> / ${i.max}こ</i></b></div><div><small>使える ポイント</small><b class="pt" data-v="points">${P(i.points)}</b></div></div>`
      + `<p class="bmsg${note && note.ng ? ' ng' : ''}" aria-live="polite">${note ? esc(note.t) : ''}</p>`;
    i.packs.forEach(pk => {
      const ok = pk.state === 'ok', head = `<span class="bn">${pk.n}<i>こ</i></span><span class="bc">${P(pk.cost)}</span>`;
      if (ok && conf === pk.n) h += `<div class="brow cf" data-n="${pk.n}" data-s="confirm">${head}<button type="button" class="bb no" data-b="no"${busy ? ' disabled' : ''}>やめる</button><button type="button" class="bb go" data-b="go" data-n="${pk.n}"${busy ? ' disabled' : ''}>${busy ? '…' : P(pk.cost) + 'で 買う'}</button></div>`;
      else if (ok) h += `<div class="brow" data-n="${pk.n}" data-s="ok">${head}<button type="button" class="bb" data-b="ask" data-n="${pk.n}"${busy ? ' disabled' : ''}>買う</button></div>`;
      else h += `<div class="brow off" data-n="${pk.n}" data-s="${pk.state}">${head}<span class="bwhy">${pk.state === 'full' ? `${i.max}こを こえる` : 'ポイントが 足りない'}</span></div>`;
    });
    h += `<p class="bnote">・持てるのは <b>${i.max}こ</b>まで。いまは あと <b>${i.room}こ</b> 買えるよ</p>`
      + `<p class="bnote">・時間でも たまるよ（<b>${i.every}分ごとに ${i.step}つ</b>）</p>`
      + `<p class="bnote">・ごはん・おそうじの あとの <b>PUSH</b> で 使うよ</p>`
      + `<p class="bnote">・買った トークンは ポイントに もどせないよ</p>`
      + `<button type="button" class="bg" data-b="guide">説明書を 見る（当たりの 確率）</button>`;
    root.querySelector('.bbd').innerHTML = h;
  }
  async function act(a, n) {
    if (busy) return;
    if (a === 'ask') { conf = n; note = null; try { api.se('button'); } catch (e) { /* なし */ } paint(); return; }
    if (a === 'no') { conf = 0; paint(); return; }
    if (a === 'guide') { close(); try { api.guide(); } catch (e) { /* なし */ } return; }
    if (a !== 'go' || conf !== n) return;
    busy = true; paint();
    let r;
    try { r = await api.buy(n); } catch (e) { r = { ok: false, why: 'err' }; }
    busy = false; conf = 0;
    note = r && r.ok ? { t: `✅ お世話トークン ${r.n}こ 買ったよ！（${P(r.cost)}）` } : { ng: true, t: WHY(r || {}, api.info()) };
    paint();
  }
  function open(el, a) {
    api = a; if (!root) build(el); else if (root.parentNode !== el) el.appendChild(root);
    conf = 0; busy = false; note = null; openedAt = performance.now(); paint();
    root.querySelector('.bbd').scrollTop = 0; root.style.display = 'flex';
    clearInterval(timer); timer = setInterval(() => { if (!isOpen()) { clearInterval(timer); return; } if (!busy && api && JSON.stringify(api.info()) !== last) paint(); }, 500);      // 開いて いる 間に トークンが たまった・ポイントが かわった → 数を 直す
  }
  function close() { clearInterval(timer); if (root) root.style.display = 'none'; conf = 0; }
  function isOpen() { return !!root && root.style.display !== 'none'; }
  return { open, close, isOpen, GUARD, get el() { return root; } };
})();
