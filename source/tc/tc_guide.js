// トレーニングセンターの 説明書（11/09 09:34 まさちゃん「トレーニングセンターのそれぞれの項目に対しての説明書みたいなのもトレーニングセンター内で確認ができるところを作りたい！
//   …ユーザーが一目で分かる説明書が欲しい！」）
//   右上の「？」→ 紙の 説明書（下へ スクロール）。✕ で とじる
//   TCGuide.open(el)・TCGuide.close()・TCGuide.scroll(0〜1)（見本：時間で 動かす）
const TCGuide = (() => {
  const CSS = `
#tcg{position:absolute;inset:0;z-index:20;display:flex;align-items:flex-end;justify-content:center;pointer-events:auto;font-family:"BIZ UDPGothic",BIZ,"Hiragino Sans","Noto Sans CJK JP",sans-serif}
#tcg .bk{position:absolute;inset:0;background:rgba(30,18,6,.45);opacity:0;transition:none}
#tcg .sh{position:relative;width:calc(100% - 20px);height:86%;margin-bottom:10px;background:#fff8ec;border-radius:18px 18px 14px 14px;box-shadow:0 6px 18px rgba(0,0,0,.35);overflow:hidden;transform:translateY(105%)}
#tcg .hd{display:flex;align-items:center;justify-content:space-between;padding:12px 14px 10px;background:linear-gradient(#f6e3bf,#efd6a8);border-bottom:2px solid #e2c48e}
#tcg .hd b{font-size:17px;color:#6b3f1d;letter-spacing:.04em}
#tcg .x{width:30px;height:30px;border-radius:50%;background:#fff8ec;border:2px solid #d9b77c;color:#8a5a2a;font-size:17px;line-height:26px;text-align:center}
#tcg .bd{position:absolute;top:56px;left:0;right:0;bottom:0;overflow:hidden}
#tcg .in{padding:10px 14px 40px}
#tcg .sec{background:#fffdf7;border:1.5px solid #ead7b2;border-radius:12px;padding:10px 12px 9px;margin:0 0 10px;box-shadow:0 2px 0 #f0e2c4}
#tcg h3{display:flex;align-items:center;gap:8px;margin:0 0 6px;font-size:15px;color:#6b3f1d}
#tcg h3 i{flex:none;width:24px;height:24px;border-radius:50%;font-style:normal;font-size:13px;line-height:24px;text-align:center;color:#fff;background:#d9a443}
#tcg p{margin:3px 0;font-size:12.5px;line-height:1.55;color:#5a3a1c}
#tcg p b{color:#c2456f}
#tcg table{width:100%;border-collapse:collapse;margin:4px 0 2px;font-size:12.5px;color:#5a3a1c}
#tcg td{padding:4px 6px;border-bottom:1px dashed #ead7b2}
#tcg td:first-child{width:86px;font-weight:700;color:#b06a12;text-align:center;background:#fff4dc;border-radius:6px;line-height:1.25;white-space:nowrap}
#tcg td:first-child small{display:block;font-size:10px;font-weight:400;color:#a8865a;letter-spacing:.02em}
#tcg tr:last-child td{border-bottom:0}
#tcg .pt{font-weight:700;color:#3f7f3a}
#tcg .rt{font-weight:700;color:#c2456f}
#tcg .tk{font-weight:700;color:#b07a10}
#tcg .note{font-size:11px;color:#8a6a48}
#tcg .hh{margin:8px 0 2px;font-weight:700;color:#6b3f1d}
`;
  // 第4.140版（11/10 14:14 まさちゃん「あと項目ごとに%を説明書に載せるようにして！」）：当たりやすさは 項目ごとに ％（となりに 小さく 分数）。
  //   ％は 分数から 数える（pc）。分数は tc_app.js（PRIZES・PRIZES_VISIT・P_…）・tc_care.js（RULE.win・金のニンジン）と 同じ 数（test_tc.py が 見くらべる）
  const pc = (d, n) => {               // n/d → '約1.18%'（ちょうどの 数は「約」なし：10%・0.1%）
    const x = (n || 1) / d * 100, s = String(+x.toFixed(x >= 10 ? 1 : x >= 0.1 ? 2 : 3));
    return (Math.abs(+s - x) > 1e-9 ? '約' : '') + s + '%';
  };
  const R = (d, html) => `<tr data-d="${d}"><td>${pc(d)}<small>1/${d}</small></td><td>${html}</td></tr>`;
  const PT = v => `<span class="pt">${v}P</span> GET`, RT = (a, b) => `<span class="rt">ルーレット</span>（${a}P か ${b}P）`;
  const CARE = [10, 20, 50, 85, 99, 121, 1000, 2000, 3600, 2400];      // お世話の 当たり ぜんぶ（合わせた ％を 出す）
  const SEC = [
    ['ト', '#d9a443', 'お世話トークン', `<p>・<b>10分ごとに1つ</b>たまる（最大<b>20こ</b>）</p><p>・「ごはん」「おそうじ」で1つ使う</p><p>・「撫でる」「呼ぶ」はトークンなしでできる</p>`],
    ['P', '#e0a020', 'お世話でポイントGETチャンス', `<p>ごはん・おそうじのたびに抽選！当たりはお世話のあとに出るよ</p>
      <table data-tab="care">${R(10, PT(10))}${R(20, PT(20))}${R(50, PT(50))}${R(85, PT(100))}${R(99, PT(200))}${R(121, PT(300))}
      ${R(1000, RT(800, 1600))}${R(2000, RT(1600, 3200))}${R(3600, RT(3200, 6400))}
      ${R(2400, '<span class="tk">チケット</span>（壁紙 or 結果ボード・1〜3枚）')}</table>
      <p class="note" data-n="sum">ぜんぶ 合わせて ${pc(1 / CARE.reduce((a, d) => a + 1 / d, 0))}（何か 当たる）</p>
      <p class="note">ルーレットは どちらも 50%</p>
      <p class="note">チケットは 3枚 ${pc(8)}・2枚 ${pc(3)}・1枚 ${pc(24, 13)}</p>`],
    ['撫', '#e86a92', '撫でる → なかよしハート', `<p>・3回なでると<b>ハート＋1</b></p><p>・撫でたあとは<b>7秒</b>おやすみ・ハートは<b>1分に5こ</b>まで</p>
      <p>・ハート<b>10こ</b>で抽選（<b>${pc(66)}</b>・1/66）</p><p>　当たり → <b>ぴょん！</b> お世話トークン<b>×5</b></p><p>　ハズレ → ごろん</p>`],
    ['呼', '#5aa7c4', '呼ぶ', `<p>・「近づいてくる」「振り向く」「甘える」のどれか（${pc(3)}ずつ・1/3）</p>`],
    ['食', '#e07a3a', 'ごはん', `<p>・エサ・リンゴ・ニンジンから選ぶ</p><p>・<b>今日の好物</b>だと大よろこび</p><p>・<b>金のニンジン</b>（ニンジンの${pc(30)}・1/30）→ なかよしハート<b>＋3</b></p>`],
    ['掃', '#6aa86a', 'おそうじ', `<p>・うんちは2分ごとに<b>${pc(7)}</b>（1/7）で出る</p><p>・ほうきで3回はくとピカピカ（うんちがない時は落ち葉）</p><p>・<b>金のうんち</b>（うんちの${pc(20)}・1/20）→ 運がついた！<b>高確ゾーン</b>（お世話5回）</p>`],
    ['★', '#8a62c8', '2分ごとのチャンス', `<p>・<b>高確ゾーン</b> ${pc(50)}（1/50・お世話5回のあいだ当たりやすい）</p><p>・<b>幻の馬</b> ${pc(245)}（1/245）・<b>神様馬</b> ${pc(399)}（1/399）がやってくる</p>`],
    ['降', '#7a4ab0', '幻の馬・神様馬がいるあいだ', `<p>やってくると フィールドがかわって、お世話の当たりが かわるよ（いるのは<b>10分</b>）</p>
      <p class="hh">🌙 幻の馬</p>
      <table data-tab="maboroshi">${R(300, RT(800, 1600))}${R(500, RT(1600, 3200))}${R(1000, RT(3200, 6400))}</table>
      <p class="hh">✨ 神様馬</p>
      <table data-tab="kamisama">${R(85, RT(2000, 4000))}${R(99, RT(5000, 10000))}${R(121, RT(10000, 20000))}</table>
      <p class="note">いるあいだは この表だけ（いつものポイント・チケットは出ないよ）</p>`],
    ['育', '#b07a46', '育つ・色がかわる', `<p>・お世話 <b>50・100・150・200・250回</b>で大きく育つ</p><p>・<b>300回</b>で次の色の子に（ブラウン → まだら → ブラック → ホワイト → 肌色）</p>`],
    ['時', '#4a6aa8', '時間でかわるフィールド', `<p>・朝 7:00〜15:59・夕方 16:00〜18:59・夜 19:00〜6:59</p>`],
  ];
  let root = null, inner = null, body = null, t0 = null;
  function build(el) {
    if (!document.getElementById('tcg-css')) { const st = document.createElement('style'); st.id = 'tcg-css'; st.textContent = CSS; document.head.appendChild(st); }
    root = document.createElement('div'); root.id = 'tcg';
    root.innerHTML = `<div class="bk"></div><div class="sh"><div class="hd"><b>トレーニングセンターの説明書</b><div class="x">✕</div></div><div class="bd"><div class="in">` +
      SEC.map(([ic, col, tt, html]) => `<div class="sec"><h3><i style="background:${col}">${ic}</i>${tt}</h3>${html}</div>`).join('') + `</div></div></div>`;
    el.appendChild(root); inner = root.querySelector('.in'); body = root.querySelector('.bd');
    root.querySelector('.x').addEventListener('click', () => close(true));
    root.querySelector('.bk').addEventListener('click', () => close(true));
    body.style.overflowY = 'auto';
  }
  let anim = null, onClose = null;
  function tween(a, b, dur, done) {           // アプリ：下から すっと 出る・下へ すっと しまう
    if (anim) cancelAnimationFrame(anim); const t0 = performance.now();
    const f = () => { const u = Math.min(1, (performance.now() - t0) / (dur * 1000)); set(a + (b - a) * u); if (u < 1) anim = requestAnimationFrame(f); else { anim = null; if (done) done(); } };
    anim = requestAnimationFrame(f);
  }
  function open(el, opt) {
    if (!root) build(el); root.style.display = 'flex';
    if (opt && opt.anim) { onClose = opt.onClose || null; body.scrollTop = 0; set(0.001); tween(0, 1, 0.35); } else set(1);
  }
  function set(k) {                    // 0〜1：ひらき ぐあい（下から すっと）
    if (!root) return; const e = 1 - Math.pow(1 - Math.max(0, Math.min(1, k)), 3);
    root.querySelector('.sh').style.transform = `translateY(${(1 - e) * 105}%)`; root.querySelector('.bk').style.opacity = String(e);
    root.style.display = k <= 0.001 ? 'none' : 'flex';
  }
  function scroll(f) { if (body) body.scrollTop = Math.max(0, Math.min(1, f)) * (body.scrollHeight - body.clientHeight); }
  function close(a) { if (a && root && root.style.display !== 'none') tween(1, 0, 0.3, () => { if (onClose) { const f = onClose; onClose = null; f(); } }); else set(0); }
  function isOpen() { return !!root && root.style.display !== 'none'; }
  return { open, set, scroll, close, isOpen, get el() { return root; } };
})();
