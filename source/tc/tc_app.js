// トレーニングセンター（App Store版）：馬の お世話・作戦会議（まさちゃん 2026/11/08〜11/09）
//   index.html の 中の tc_launch.js が 右上（第4.138版：上の 帯の すぐ 下）に 丸い ボタンを 出す → 押すと この ファイル（tc_bundle.js）を 読んで TCApp.open()
//   ・上の 帯：「← もどる」・作戦会議（横長の ボタン）・音
//   ・フィールド（tc_field.js：時間帯・幻の馬／神様馬）＋ 馬（tc_horse.js）＋ お世話の 紙の 絵（tc_care.js）＋ 説明書（tc_guide.js）
//   ・当たり：ポイント（台帳の もらったP）・ルーレット／チケット（tc_fx.js）
//   ・保存：localStorage 'tengel.tc'（この 端末の 中だけ）
const TCApp = (() => {
  const W = 1052, H = 1657;
  const SK = 'tengel.tc';
  const COLORS = ['brown', 'madara', 'black', 'white', 'hada'];
  const COLOR_JA = { brown: 'ブラウン', madara: 'まだら', black: 'ブラック', white: 'ホワイト', hada: '肌色' };
  // お世話トークン：5分ごとに 5つ・最大 25（第4.165版・まさちゃん 11/13 11:46「お世話トークンに5分で5個追加に変更」＝10分 → 5分。
  //   第4.159版：11/12 10:37「お世話の最大トークン25回にして！」・12:48「お世話トークンは25がMAXで、5分経つと5つずつ増えるようにね！」
  //   → 14:50「お世話トークンに関して、10分で５つトークンが追加にして！」＝5分 → 10分。その 前は 10分ごとに 1つ・最大 20）
  const TOKEN_MIN = 5, TOKEN_STEP = 5, TOKEN_MAX = 25;
  const TICK = 120;                                   // 2分ごとの チャンス（秒・開いて いる 間）：高確ゾーン・うんち（第4.144版から 幻の馬・神様馬の 抽選は しない）
  // 第4.144版（馬の リセットの きまり：11/10 18:04 まさちゃん「馬のリセットは5分に切り替えよう！…トレーニングセンターで最低5回お世話をした段階でリセットタイマーが作動して(お世話をしてる間はリセットなし)5分経ったらリセット。
  //   …トレーニングセンターを開きっぱなしでもお世話の操作をしない限りは馬は変わらないでいて！ただ、幻の馬と神様馬は…トレーニングセンターを開いてから30分経過すると切り替わる仕組みにして！」
  //   ・18:13「幻の馬と神様馬も最低5回お世話完了後はリセットタイマー作動で5分でリセットね！」）：
  //   ・馬が かわる 抽選（幻の馬 1/245・神様馬 1/399・それ 以外は いつもの 馬）は「リセット」の とき だけ。前は 2分ごとに（ひらいて いる だけで）ひいて いた
  //   ・リセット＝お世話（ごはん・おそうじ）を 5回 した あと（5回めが おわった とき）に タイマーが 動いて、5分 たったら。お世話の 途中・当たりの 演出の 途中・作戦会議や 説明書を ひらいて いる 間は 待つ
  //   ・幻の馬・神様馬は、それに 加えて 来てから 30分（タイムリミット）でも 帰る（→ いつもの 馬）。どちらか 早い 方
  //   ・時間は「もどらない 時計」（tnow）と、ひらいて いる 間に たった 秒（el）の どちらか 早い 方で 数える（時計を もどしても 止まらない）
  const RESET_CARES = 5, RESET_MIN = 5;               // 馬の リセット：お世話 5回 → タイマー 5分
  const VISIT_MIN = 30;                               // 幻の馬・神様馬の タイムリミット（来てから・分）
  // 第4.168版（まさちゃん 2026/11/14 01:26「神様馬と幻の馬の抽選について 幻の馬は、抽選最大10回まで 神様馬は、抽選最大5回まで」）：
  //   幻の馬・神様馬が いる 間の 抽選（お世話の あとの PUSH：1回 押す＝1回）は この 回数 まで。つかい切ると、その 当たりを わたし おわって から 帰る（＝馬の リセット：次の 馬の 抽選）。
  //   ・回数は 来てからの PUSH の 回数（st.rs.n：startVisit で 0 に もどる）。「まとめて 使う」でも 上限で PUSH は 消える（tc_care.js の O.drawLeft）
  //   ・お世話 5回の あと 5分（リセット）・来てから 30分（タイムリミット）は そのまま ＝ どれか 早い もので 帰る。神様馬は 上限が 5回 なので、5回めの 抽選で 帰る
  const VISIT_DRAWS = { maboroshi: 10, kamisama: 5 };
  const CAP_WAIT = 2.6;                               // 上限の 抽選の 結果（ポイントの 札は 2秒）を 見せて から 帰る（秒）
  // ゴミ（第4.152版：11/11 10:13 まさちゃん「お掃除は、15分に一回、ゴミがフィールドに散乱する仕組みにして！片付けられない限りは、新しいゴミが出ないようにして！」「ゴミは落ちる場所は5箇所、ランダムに出現するように！」）
  //   片付けて から TRASH_MIN 分 たつと、フィールドの TRASH_N か所に 散らばる（閉じて いる 間も 時間は 進む：もどらない 時計 tnow）。片付ける まで 次は 出ない
  const TRASH_MIN = 15, TRASH_N = 5, TRASH_W = [0.33, 0.38, 0.54, 0.52];      // TRASH_W：絵の 幅（リンゴの 芯・かじった ニンジン・枯れ葉・色の 葉っぱ。体の 高さ 1 の 馬＝1）
  const HIGH_N = 5, HIGH_X = 4;                       // 高確ゾーン：お世話 5回・当たりやすさ ×4 ※仮
  const P_POOP = 1 / 7, P_GOLD = 1 / 20, P_HIGH = 1 / 50, P_MAB = 1 / 245, P_KAMI = 1 / 399;
  // 第4.165版（まさちゃん 2026/11/13 12:51「トレーニングセンターの抽選に ・ポイントの特化ゾーンを作る (レバーを押し込め！で、60%で上乗せ) 1回の抽選の1/699で入る
  //   スタート1000P MAX25000P … ・ゾーン1回の平均獲得、約4000P ・MAXまでに必要な成功回数、12回連続上乗せ」）：ポイント特化ゾーン
  //   ・入るのは 抽選 1回ごとに 1/699（いつもの 馬・幻の馬・神様馬の どの 表でも。高確ゾーンの 間は ほかの 当たりと 同じ ×4）
  //   ・スタート 1,000P → レバーを 押しこむ たびに 60% で ＋2,000P 上乗せ・失敗（40%）で おわり → それまでの 合計を GET。12回 つづけて 上乗せ ＝ 1,000 ＋ 2,000×12 ＝ 25,000P（MAX）で おわり
  //   ・平均＝1,000 ＋ 2,000 ×（0.6 ＋ 0.6² ＋ … ＋ 0.6¹²）＝ 約3,993P（≒4,000P）。MAX まで 行くのは 0.6¹² ＝ 約0.22%
  //   ・何回 上乗せ できるかは 抽選の ときに 決めて 保存（lottery）：演出の 途中で アプリを 閉じても、次に 開いた ときに 合計を わたす（st.pend）
  //   ・この 分、抽選 1回の 平均は 約57.8P → 約63.5P（＋約5.7P）・何か 当たる のは 約17.0% → 約17.1%
  const ZONE = { d: 699, start: 1000, add: 2000, rate: 0.6, max: 12 };
  const zoneV = n => ZONE.start + ZONE.add * Math.max(0, Math.min(ZONE.max, Math.round(+n) || 0));      // n回 上乗せ した ときの 合計
  const zoneRoll = () => { let n = 0; while (n < ZONE.max && Math.random() < ZONE.rate) n++; return n; };
  const PRIZES = [                                    // お世話（ごはん・おそうじ）の 抽選：まれな 方から
    [1 / ZONE.d, { k: 'zn' }],
    // 第4.142版（11/10 17:20 まさちゃん「仕組みは今のままでいい！ただノーマルのルーレット抽選、幻の馬ルーレット当選と神様馬ルーレット抽選の確率だけ変えたい！」）：
    //   ルーレット 800P か 1600P 1/1000 → 1/125・1600P か 3200P 1/2000 → 1/245・3200P か 6400P 1/3600 → 1/399・チケット 1/2400 → 1/600（ポイントの 当たり 6つは そのまま）。
    //   何か 当たる のは 1回 約20.2% → 約21.6%・平均は 1回 約17.0P → 約58.6P。高確ゾーン（×4）でも 合わせて 約87%（1 を こえない：こえると まれな 当たりが 4倍に ならない）
    [1 / 600, { k: 'tk' }], [1 / 399, { k: 'rt', tier: 'kamisama' }], [1 / 245, { k: 'rt', tier: 'maboroshi' }], [1 / 125, { k: 'rt', tier: 'normal' }],
    // 第4.165版（11/13 11:46 まさちゃん「お世話でポイントGET 確率少し変える(ここだけ) 1/15で10P 1/25で20P 1/55で50P 1/95で100P」）：
    //   10P 1/10 → 1/15・20P 1/20 → 1/25・50P 1/50 → 1/55・100P 1/85 → 1/95（200P・300P・ルーレット・チケットは そのまま）。
    //   何か 当たる のは 1回 約21.6% → 約17.0%・平均は 1回 約58.6P → 約57.8P。高確ゾーン（×4）でも 合わせて 約68%（1 を こえない）
    [1 / 121, { k: 'pt', v: 300 }], [1 / 99, { k: 'pt', v: 200 }], [1 / 95, { k: 'pt', v: 100 }],
    // 第4.140版（11/10 14:14 まさちゃん「足す：10P 1/10・20P 1/20・50P 1/50 これだけ足して！」）：小さい 当たり（ほかは そのまま）。第4.165版で 1/15・1/25・1/55 に
    [1 / 55, { k: 'pt', v: 50 }], [1 / 25, { k: 'pt', v: 20 }], [1 / 15, { k: 'pt', v: 10 }]];
  const RT = { normal: [800, 1600], maboroshi: [1600, 3200], kamisama: [3200, 6400] };
  // 幻の馬・神様馬が いる 間の お世話の 抽選（11/09 14:22・14:26 まさちゃん：この表だけ・ルーレットの 絵は その馬の もの）
  //   第4.142版（同じ 17:20 の 指定）：幻の馬 1/300・1/500・1/1000 → 1/15・1/30・1/60／神様馬 1/85・1/99・1/121 → 1/8・1/16・1/32。
  //   何か 当たる のは 幻の馬 約11.7%（平均 1回 240P）・神様馬 約21.9%（平均 1回 約1,313P）。高確ゾーン（×4）でも 約46.7%・87.5%（1 を こえない）
  const PRIZES_VISIT = {
    maboroshi: [[1 / ZONE.d, { k: 'zn' }], [1 / 60, { k: 'rt', tier: 'maboroshi', v: [3200, 6400] }], [1 / 30, { k: 'rt', tier: 'maboroshi', v: [1600, 3200] }], [1 / 15, { k: 'rt', tier: 'maboroshi', v: [800, 1600] }]],
    kamisama: [[1 / ZONE.d, { k: 'zn' }], [1 / 32, { k: 'rt', tier: 'kamisama', v: [10000, 20000] }], [1 / 16, { k: 'rt', tier: 'kamisama', v: [5000, 10000] }], [1 / 8, { k: 'rt', tier: 'kamisama', v: [2000, 4000] }]] };
  const AP = p => String(p).split('/').pop();         // アプリ：Resources に 名前だけ
  window.TC_ASSET = AP;

  // ---------- 保存 ----------
  const DEF = () => ({ v: 1, color: 0, cares: 0, total: 0, stock: 5, stockAt: Date.now(), heart: 0, high: 0, tickets: 0, fav: null, poops: [], trash: [], trashAt: 0, visit: null, rs: { n: 0, at: 0, el: 0 }, snd: true, gen: 1, bulk: false, push: false, buy: null });      // bulk＝トークンを まとめて 使う（PUSH の 横の スイッチ）・push＝お世話の あとの PUSH が まだ 出て いる（第4.159版）・rs＝馬の リセット（n：前の リセットからの お世話の 回数・at：タイマーが 動いた 時刻（0＝まだ）・el：それから ひらいて いた 秒）・buy＝お世話トークンの 買い物の しるし { id, n }（第4.165版：台帳に 入れる 前に 書いて、トークンを わたしたら 消す）
  let st = null, dirty = false, saveAt = 0;
  function load() {
    try { const s = JSON.parse(localStorage.getItem(SK) || 'null'); st = Object.assign(DEF(), s && s.v === 1 ? s : {}); } catch (e) { st = DEF(); }
    const r = st.rs; st.rs = r && typeof r === 'object' ? { n: Math.max(0, Math.round(+r.n || 0)), at: Math.max(0, +r.at || 0), el: Math.max(0, +r.el || 0) } : { n: 0, at: 0, el: 0 };
    st.trash = (Array.isArray(st.trash) ? st.trash : []).filter(q => q && isFinite(q.x) && isFinite(q.y)).slice(0, 8).map(q => ({ x: Math.round(q.x), y: Math.round(q.y), sd: (+q.sd || 0) >>> 0 }));
    st.trashAt = Math.max(0, +st.trashAt || 0);
  }
  function save() { dirty = false; try { localStorage.setItem(SK, JSON.stringify(st)); } catch (e) { } }
  const touch = () => { dirty = true; };
  const TKP = () => ((window.TengelPoints && window.TengelPoints.TICKET_POINTS) || 7000).toLocaleString('ja-JP');      // チケット 1枚を かえられる ポイント（points.js）
  const note = m => { try { const t = document.getElementById('toast'); if (t) { t.textContent = m; t.hidden = false; clearTimeout(t._tc); t._tc = setTimeout(() => { t.hidden = true; }, 4200); } } catch (e) { /* なし */ } };      // アプリの 画面の お知らせ（下の 黒い 札）
  function stageOf(c) { return c < 50 ? 1 : c < 100 ? 2 : c < 150 ? 3 : c < 200 ? 4 : 5; }
  function scaleOf(c) { return c < 50 ? 0.6 : c < 100 ? 0.7 : c < 150 ? 0.8 : c < 200 ? 0.88 : c < 250 ? 0.94 : 1.0; }      // ※仮：250回で いちばん 大きく
  function tod(d) { const h = (d || new Date()).getHours(); return h >= 7 && h < 16 ? 'morning' : h >= 16 && h < 19 ? 'evening' : 'night'; }
  function today() { const d = new Date(); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); }
  // 第4.139版（抜け穴を ふさぐ）：端末の 時計を 先へ 進めて お世話トークンを ためる → 時計を もどす、を ふせぐ「もどらない 時計」。
  //   いままでに 見た いちばん 先の 時刻（st.seen）より 前には もどらない。時計を もどした あとは、本当の 時刻が そこへ 追いつくまで トークンは ふえない
  //   （前は トークンが 満タンの ときに 数えはじめの 時刻を いまの 時刻に 書きかえて いた ので、満タンに して から 時計を もどせば すぐ また ためられた）。
  //   ※ 時計を 先へ 進めた ままに する ズルは、端末の 中だけでは 見分けられない（電波で 正しい 時刻を もらう しくみが いる）
  function tnow() {
    const n = Date.now(), s0 = +st.seen || 0;
    if (n > s0) { st.seen = n; if (n > (tnow.saved || 0) + 60000) { tnow.saved = n; touch(); } }
    return Math.max(n, s0);
  }
  function accrue(now) {                              // お世話トークン（閉じて いる 間も 時間で たまる）。now＝tnow()（もどらない 時計）
    if (st.stock >= TOKEN_MAX) { st.stockAt = now; return 0; }
    const n = Math.floor((now - st.stockAt) / (TOKEN_MIN * 60000)); if (n <= 0) return 0;
    const add = Math.min(n * TOKEN_STEP, TOKEN_MAX - st.stock); st.stock += add; st.stockAt = st.stock >= TOKEN_MAX ? now : st.stockAt + n * TOKEN_MIN * 60000; touch(); return add;      // 5分（TOKEN_MIN）が n回 たった → 5つ × n（上限 まで）
  }

  // ---------- 音（WebAudio：環境音・BGM は くり返し、効果音は できごとで）----------
  const SND = (() => {
    let ac = null, master = null, bed = null, want = null, on = true;
    const cache = {};
    const AMB = { morning: 'tc_amb_morning.m4a', evening: 'tc_amb_evening.m4a', night: 'tc_amb_night.m4a', abyss: 'tc_bgm_abyss.m4a', divine: 'tc_bgm_divine2.m4a', roulette: 'tc_bgm_roulette.m4a' };
    // 第4.168版（まさちゃん 2026/11/14 01:26「ルーレットに入った時にBGMを変える。フィールドBGMは重ねない。」）：ルーレットの 間は ルーレットの BGM だけ（bgm）。
    //   ・hold＝いま フィールドの 音の かわりに 鳴らす もの：null＝なし（フィールドの 音）・''＝音なし（プチュンの あと）・名前＝その BGM。hold が ある 間は field() は おぼえる だけ（重ねない）
    //   ・ルーレットの BGM の ファイルは、くり返す 1回り（8小節）の 前と うしろに 0.5秒ずつ 同じ 音の つづきが 入って いる（kisekae/tc/snd/export_app.py）→ まん中の 1回り だけを くり返す（LOOPS）。
    //     m4a は 読む 道具に よって 頭に 短い 無音が つく ことが ある：前と うしろに つづきが ある ので、その ぶん ずれても つなぎ目は 同じ 音どうし（リズムが とばない）
    // 第4.171版（まさちゃん 2026/11/14 16:18「トレーニングセンターの神様馬出現中のBGM:もっとアップテンポで掻き立てられるようなBGM」・
    //   17:08「神様馬のBGMもう少しカッコよく！もう少し神様ぽさを混ぜて！」）：神様馬の フィールドの BGM は 新しい 曲（tc_bgm_divine2.m4a：kisekae/tc/snd/bgm_tengel.py の divine2・
    //   ホ短調・156 BPM・32小節）。ルーレットの BGM と 同じ 形の ファイル（前後に 0.5秒の つづき）→ まん中の 1回り だけを くり返す（LOOPS）。
    //   曲の 頭は「降臨」の 和音（オルガン・合唱・鐘）なので、フィールドが かわる ときは すぐ 入れる（0.15秒：ゆっくり 入れると 頭の 和音が 聞こえない）。前の 音は 2秒で 消える。
    //   新しい 曲の ファイルが ない（前の 素材の フォルダで 作った アプリ）とき だけ 前の 曲（AMB_OLD：60秒の ループ・LOOPS は 使わない）
    const AMB_OLD = { divine: 'tc_bgm_divine.m4a' };
    const LOOPS = { roulette: { pre: 0.5, len: 8 * 4 * 60 / 132 }, divine: { pre: 0.5, len: 32 * 4 * 60 / 156 } };
    let hold = null, aim = null;
    function buf(f) { if (!cache[f]) cache[f] = fetch(AP(f)).then(r => { if (!r.ok) throw new Error('no ' + f); return r.arrayBuffer(); }).then(b => new Promise((ok, ng) => { const q = ac.decodeAudioData(b, ok, ng); if (q && q.catch) q.catch(() => { }); })); return cache[f]; }
    function unlock() { try { if (!ac) { const AC = window.AudioContext || window.webkitAudioContext; if (!AC) return; ac = new AC(); master = ac.createGain(); master.gain.value = on ? 1 : 0; master.connect(ac.destination); } if (ac.state === 'suspended') ac.resume(); } catch (e) { } }
    // いま 鳴って いる 音を fout 秒で 消して、name の 音を fin 秒で 入れる（name が 空・ない ときは 何も 鳴らさない）。同じ 音が もう 鳴って いれば 何も しない
    async function swap(name, fout, fin) {
      aim = name || ''; if (!ac) return; if (bed && bed.name === aim) return;
      const old = bed; bed = null;
      if (old) { try { const n = ac.currentTime; old.g.gain.cancelScheduledValues(n); old.g.gain.setValueAtTime(old.g.gain.value, n); old.g.gain.linearRampToValueAtTime(0, n + fout); old.s.stop(n + fout + 0.1); } catch (e) { } }
      const f = AMB[aim]; if (!f) return; let b, fb = false;
      try { b = await buf(f); } catch (e) { if (!AMB_OLD[aim]) return; try { b = await buf(AMB_OLD[aim]); fb = true; } catch (e2) { return; } }
      if (aim !== (name || '') || (bed && bed.name === aim)) return;
      const s = ac.createBufferSource(); s.buffer = b; s.loop = true;
      const L = fb ? null : LOOPS[aim]; let off = 0;
      if (L && b.duration >= L.len + L.pre) { s.loopStart = L.pre / 2; s.loopEnd = L.pre / 2 + L.len; off = L.pre; }      // まん中の 1回り だけを くり返す・はじめは 1拍めから
      const g = ac.createGain(); g.gain.setValueAtTime(0, ac.currentTime); g.gain.linearRampToValueAtTime(1, ac.currentTime + fin);
      s.connect(g); g.connect(master); s.start(0, off); bed = { s, g, name: aim };
    }
    async function field(name) { want = name; if (hold != null) return; await swap(name, 2, LOOPS[name] ? 0.15 : 2); }      // フィールドの 音（2秒で 入れかえ）。ルーレットの 間（hold）は おぼえる だけ
    // ルーレットの 間の BGM：name＝BGM の 名前（すぐ 入れかえ：フィールドの 音は 0.3秒で 消す）・''＝音なし（プチュン：すぐ 消す）・null＝フィールドの 音に もどす（1.5秒で もどる）
    async function bgm(name) {
      hold = name == null ? null : String(name);
      if (hold == null) await swap(want, 0.5, 1.5); else if (hold === '') await swap('', 0.08, 0); else await swap(hold, 0.3, 0.12);
    }
    async function se(name, gain, at) {
      if (!ac || !on) return; let b; try { b = await buf(name); } catch (e) { return; }
      try { const s = ac.createBufferSource(); s.buffer = b; const g = ac.createGain(); g.gain.value = gain == null ? 1 : gain; s.connect(g); g.connect(master); s.start(ac.currentTime + Math.max(0, at || 0)); return s; } catch (e) { }
    }
    function stopAll() { if (bed) { try { bed.s.stop(); } catch (e) { } bed = null; } want = null; hold = null; aim = null; if (ac && ac.state === 'running') { try { ac.suspend(); } catch (e) { } } }
    function setOn(v) { on = !!v; if (master) master.gain.value = on ? 1 : 0; }
    function preload(list) { if (!ac) return; list.forEach(f => buf(f).catch(() => { })); }
    return { unlock, field, bgm, se, stopAll, setOn, preload, get ac() { return ac; }, get bed() { return bed ? bed.name : null; }, get hold() { return hold; }, get loop() { return bed ? [bed.s.loopStart, bed.s.loopEnd] : null; }, LOOPS };      // loop（第4.171版）＝いまの 音の くり返す 所（秒：はじめ・おわり。0・0 は ファイルの はじめから おわりまで）
  })();
  // できごと → 効果音（sfx_care.py の parts で 作った tc_se_*.m4a。大きさ・ずれは 作る ときに 入れて ある）
  const SE_VAR = { slot: e => 'slot_' + Math.max(1, Math.min(10, e.n || 1)), bite: e => 'bite_' + (e.kind === 'apple' ? 'apple' : 'carrot'), banin: e => 'banin_' + (e.kind === 'maboroshi' ? 'maboroshi' : 'kamisama') };
  const SE_SKIP = { ready2: 'ready', zoomout: 'zoomin', feedstart: null, callcool: null, unlock: 'piron', pushin: 'stock' };      // callcool（呼ぶの 7秒の 休み）は 音なし（第4.156版：ない 音の ファイルを 読みに 行かない）・unlock（ハートの 抽選の 当たり）は piron と 同じ 音（中身が 1バイトも ちがわない ファイルが 2つ あった → 1つに）
  function onCareEvent(e) {
    // 第4.159版：トークンを 使うのは お世話の あとの PUSH を 押した とき（まとめて 使う なら 押した 回数ぶん）＝トークン 1個が お世話 1回（まさちゃん「数える」）。
    //   使った トークンは その場で 保存（つづけて 押した あと すぐ 閉じても、使った 分が もどらない）
    if (e.k === 'token') { st.cares += 1; st.total = (st.total || 0) + 1; st.rs.n = (st.rs.n || 0) + 1; if (TCCare.on) st.stock = TCCare.S.stock; touch(); save(); later.push(() => growCheck()); }      // お世話の 回数（total＝ミッションの 合計：馬が リセット されても 減らない）
    let nm = SE_VAR[e.k] ? SE_VAR[e.k](e) : (e.k in SE_SKIP ? SE_SKIP[e.k] : e.k);
    if (!nm) return;
    const lag = Math.max(0, e.t - clock());
    SND.se('tc_se_' + nm + '.m4a', 1, lag);
  }

  // ---------- 画面 ----------
  let ov = null, stage = null, cvGL = null, cvOv = null, cvFx = null, field = null, gl = null, built = false;
  let HO = null, BR = null, horseKey = '', raf = 0, running = false, tBase = 0, lastT = null, lastDraw = 0, nextTick = 0, later = [], busy = false;
  let buying = false;                                 // 第4.165版：お世話トークンを 買って いる 途中（ボタンは 下の 列の 1番 右：tc_care.js が 描く）
  const clock = () => (performance.now() - tBase) / 1000 + 1.5;
  const css = `
#tcOv{position:fixed;inset:0;z-index:90;display:none;flex-direction:column;align-items:center;background:#2a1d12;padding-top:env(safe-area-inset-top);padding-bottom:env(safe-area-inset-bottom);-webkit-user-select:none;user-select:none;touch-action:none;font-family:"BIZ UDPGothic","Hiragino Sans",sans-serif}
#tcOv.on{display:flex}
#tcOv .tch{width:100%;max-width:560px;box-sizing:border-box;display:flex;align-items:center;gap:8px;padding:6px 10px;height:58px;flex:none}
#tcOv .tcbk{flex:none;height:40px;padding:0 12px;border-radius:20px;border:2px solid #d9b77c;background:#fff8ec;color:#7a4520;font:700 15px/1 "BIZ UDPGothic","Hiragino Sans",sans-serif;display:flex;align-items:center;gap:4px}
#tcOv .tcsp{flex:1 1 auto}
#tcOv .tcst .tcpl{position:absolute;right:2.47%;top:9.1%;width:25%;border:0;padding:0;margin:0;background:none;-webkit-tap-highlight-color:transparent;transition:transform .12s}
#tcOv .tcst .tcpl:active{transform:scale(.94)}
#tcOv .tcpl img{display:block;width:100%;height:auto;pointer-events:none;filter:drop-shadow(0 3px 4px rgba(0,0,0,.35))}
#tcOv .tcsd{flex:none;width:40px;height:40px;border-radius:50%;border:2px solid #d9b77c;background:#fff8ec;font-size:18px;line-height:1;padding:0}
#tcOv .tctk{flex:none;height:30px;padding:0 9px;border-radius:15px;background:#fff4d6;border:2px solid #e2c48e;color:#8a5a12;font:700 13px/26px "BIZ UDPGothic",sans-serif;white-space:nowrap}
#tcOv .tcwr{position:relative;flex:1 1 auto;min-height:0;width:100%;display:flex;align-items:center;justify-content:center;overflow:hidden}
#tcOv .tcbg{position:absolute;inset:-24px;background:#2a1d12 center/cover no-repeat;filter:blur(16px) brightness(.62) saturate(1.1);transform:scale(1.06)}
#tcOv .tcst{position:relative;flex:none;overflow:hidden;touch-action:none;box-shadow:0 0 0 1px rgba(0,0,0,.25),0 6px 24px rgba(0,0,0,.35)}
#tcOv .tcst canvas{position:absolute;left:0;top:0;width:100%;height:100%;display:block}
#tcOv .tcst .tcfx{display:none}#tcOv .tcst .tcfx.on{display:block}
#tcOv .tcmsg{white-space:pre-line;position:absolute;left:50%;top:44%;transform:translate(-50%,-50%);background:#fff8ec;border:2px solid #e2c48e;border-radius:16px;padding:14px 18px;color:#6b3f1d;font:700 16px/1.5 "BIZ UDPGothic",sans-serif;text-align:center;box-shadow:0 6px 18px rgba(0,0,0,.35);max-width:80%;z-index:30;pointer-events:none;opacity:0;transition:opacity .3s}
#tcOv .tcmsg.on{opacity:1}
#tcOv .tcld{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:#fff8ec;font:700 16px "BIZ UDPGothic",sans-serif;background:#2a1d12;z-index:40}
`;
  function build() {
    if (built) return; built = true;
    const s = document.createElement('style'); s.id = 'tcCss'; s.textContent = css; document.head.appendChild(s);
    ov = document.createElement('div'); ov.id = 'tcOv'; ov.setAttribute('role', 'dialog'); ov.setAttribute('aria-modal', 'true'); ov.setAttribute('aria-label', 'トレーニングセンター');
    ov.innerHTML = `<div class="tch"><button type="button" class="tcbk" data-tc="back" aria-label="もどる">← もどる</button>`
      + `<span class="tcsp"></span>`
      + (testOn() ? TCTest.head() : '')          // テスト版だけ：道具箱の 入口（ボタンの 絵と 字は tc_test.js）
      + `<span class="tctk" hidden></span><button type="button" class="tcsd" data-tc="snd" aria-label="音"></button></div>`
      + `<div class="tcwr"><div class="tcbg"></div><div class="tcst"><canvas class="tcgl"></canvas><canvas class="tco"></canvas><button type="button" class="tcpl" data-tc="plan" aria-label="作戦会議"><img src="${AP('tc_icon_plan.webp')}" alt="作戦会議"></button>`
      + `<canvas class="tcfx"></canvas><div class="tcmsg" aria-live="polite"></div><div class="tcld">トレーニングセンター…</div></div></div>`;
    document.body.appendChild(ov);
    stage = ov.querySelector('.tcst'); cvGL = ov.querySelector('.tcgl'); cvOv = ov.querySelector('.tco'); cvFx = ov.querySelector('.tcfx');
    ov.addEventListener('click', e => {
      const b = e.target.closest('[data-tc]'); if (!b) return; SND.unlock();
      if (b.dataset.tc === 'back') close();
      else if (b.dataset.tc === 'plan') { if (window.TCPlan) { SND.se('tc_se_button.m4a'); window.TCPlan.open(ov); } }
      else if (b.dataset.tc === 'snd') { st.snd = !st.snd; touch(); SND.setOn(st.snd); paintHead(); }
      else if (b.dataset.tc === 'test' && testOn()) { SND.se('tc_se_button.m4a'); if (TCTest.isOpen()) TCTest.close(); else TCTest.open(stage, TEST); }
    });
    const pt = (e, kind) => {
      if (busy || !TCCare.on) return; const r = stage.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width * W, y = (e.clientY - r.top) / r.height * H;
      TCCare.pointer(kind, x, y, clock());
    };
    stage.addEventListener('pointerdown', e => { SND.unlock(); if (e.target === cvOv || e.target === cvGL) { try { stage.setPointerCapture(e.pointerId); } catch (x) { } pt(e, 'down'); } });
    stage.addEventListener('pointermove', e => { if (e.buttons || e.pointerType === 'touch') pt(e, 'move'); });
    stage.addEventListener('pointerup', e => pt(e, 'up'));
    stage.addEventListener('pointercancel', e => pt(e, 'up'));
    window.addEventListener('resize', () => { if (running) layout(); });
    document.addEventListener('visibilitychange', () => { if (!ov.classList.contains('on')) return; if (document.hidden) pause(); else resume(); });
  }
  function paintHead() {
    const b = ov.querySelector('.tcsd'); b.textContent = st.snd ? '🔊' : '🔇'; b.setAttribute('aria-label', st.snd ? '音：オン（押すと けす）' : '音：オフ（押すと 出す）');
    const tk = ov.querySelector('.tctk'); tk.hidden = !(st.tickets > 0); tk.textContent = `🎫 ${st.tickets}`;
    tk.setAttribute('aria-label', `チケット ${st.tickets}枚（設定の 着せ替えで、壁紙の 解放か ${TKP()}P に かえるか 選べるよ）`);
  }
  function layout() {
    const vw = window.innerWidth, r = ov.getBoundingClientRect(), head = 58;
    const cs = getComputedStyle(ov), padT = parseFloat(cs.paddingTop) || 0, padB = parseFloat(cs.paddingBottom) || 0;
    const avail = (r.height || window.innerHeight) - padT - padB - head;
    const w = Math.max(200, Math.min(vw, avail * W / H)), h = w * H / W;
    stage.style.width = w + 'px'; stage.style.height = h + 'px';
    // 第4.150版（まさちゃん 2026/11/11 02:43「トレーニングセンターも馬の画質は高く！」）：画面の 細かさ いっぱい（3倍まで）で 描く。
    //   前は 台紙の 幅（1052px）まで ＝ iPhone（3倍・幅 1170px）では 1割、iPad（2倍・幅 1270px ほど）では 2割 ひきのばして いた（馬の ふちと 毛の もようが ぼやける）。
    //   背景の 絵は 同じ 絵を ひきのばす（前と 同じ 見え方）。GOV.q＝なめらかさを 守る ための 細かさの 倍（ふだんは 1：下の govern）
    const dpr = Math.min(window.devicePixelRatio || 1, 3) * GOV.q;
    const pw = Math.round(w * dpr), ph = Math.round(pw * H / W);
    for (const c of [cvGL, cvOv, cvFx]) if (c.width !== pw || c.height !== ph) { c.width = pw; c.height = ph; }
    if (window.TCCare && TCCare.S) TCCare.S.cs = pw / W;
    return pw / W;
  }
  function msg(txt, sec) {
    const m = ov.querySelector('.tcmsg'); m.textContent = txt; m.classList.add('on');
    clearTimeout(msg._t); msg._t = setTimeout(() => m.classList.remove('on'), (sec || 2.6) * 1000);
  }

  // ---------- 馬 ----------
  // 第4.168版（まさちゃん 2026/11/14 01:26「幻の馬と神様馬の大きさを、いつもの馬と同じ大きさに合わせる。※足の形、動き方も全て一緒にして！あくまで、外見が違うだけにして！
  //   動き方や行動についても！」）：幻の馬・神様馬が いつもの 馬と ちがうのは 見た目（形の 絵・目の 光・紙の 明るさ・フィールドの 光）だけ。
  //   ・大きさ＝いつもの 馬の いまの 大きさ（scaleOf：お世話の 回数で 育つ 6段。前は いつも 1.7倍 ＝ BIG）。育つ ときは いっしょに 大きく なる（growCheck）
  //   ・足の 形（立ち方）＝形の まま。前は 神様馬 だけ 肩幅と 足の 場所を 広げて いた（STANCE_KAMI：ひづめを 左右 0.3 へ ＝ がに股）→ やめた（ひづめは 形の まま ±0.11〜0.15：いつもの 馬と 同じ ぐらい）
  //   ・動き方・行動＝いつもの 馬と 同じ 所を 通る（tc_horse.js は 大きさが 1.3倍より 大きい 馬 だけ「どっしり 歩く」・1.4倍より 大きい 馬は「走らない」＝ もう 当たらない）。
  //     うんちも いつもの 馬と 同じ（テスト版の 道具も 幻の馬・神様馬で 使える）
  function horseSpec() {
    if (st.visit) {
      const k = scaleOf(st.cares);
      return st.visit.kind === 'kamisama'
        ? { key: 'kamisama:' + k, name: 'tc_horse_bk_kamisama2', stage: k, eyeGlow: 'gold', lift: 0.14, glowK: 0.45, glowR: 0.7, light: 'divine' }
        : { key: 'maboroshi:' + k, name: 'tc_horse_bk_maboroshi2', stage: k, eyeGlow: 'purple', light: 'abyss' };      // 名前の 2：第4.161版で 直した 形（kisekae/tc/horse_fix.py：神様馬＝マントの 先の 骨・幻の馬＝たてがみの 黒・にじみ）
    }
    const c = COLORS[st.color % COLORS.length], s = stageOf(st.cares);
    return { key: c + s + ':' + scaleOf(st.cares), name: `tc_horse_bk_${c}_s${s}${HFIX[s] || ''}`, old: HFIX[s] ? `tc_horse_bk_${c}_s${s}` : null, stage: scaleOf(st.cares) };
  }
  // 第4.168版（まさちゃん 2026/11/14 01:26「二枚目の赤丸の立髪の一部が色がおかしい！直して！」）：2段目の 大きさ（s2）は、たてがみの いちばん うしろの ふさの うしろ半分が
  //   体の 色で ぬられて いた（ぶちの 馬は そこ だけ 白く 見えた）。ふさを たてがみの 色に ぬり直した 絵（tc_c_<色>_s2v2.webp）を 指す 新しい 形の 名前（…_s2v2.json：kisekae/tc/mane_fix.py）を 読む。
  //   形（.bin）と 法線の 絵は 今までと 同じ。新しい 名前が ない とき（前の 素材 だけの 手元の ビルド）は 前の 名前（old）を 読む
  const HFIX = { 2: 'v2' };
  const hcache = {};
  async function loadHorse(sp) {
    if (hcache[sp.key]) return hcache[sp.key];
    const getMeta = n => fetch(AP(n + '.json')).then(r => { if (!r.ok) throw new Error('horse ' + r.status); return r.json(); });
    const meta = await getMeta(sp.name).catch(e => { if (!sp.old) throw e; return getMeta(sp.old); });
    const bin = TCHorse.unz(await fetch(AP(meta.bin || (sp.name + '.bin'))).then(r => r.arrayBuffer()));      // 第4.151版：番号を 詰めた 形（神様馬・幻の馬）は もとの 形に もどす
    const img = s => s ? new Promise(ok => { const im = new Image(); im.onload = () => ok(im); im.onerror = () => ok(null); im.src = AP(s); }) : Promise.resolve(null);
    const [texImg, nrmImg, p1, p2, p3, ...trashImgs] = await Promise.all([img(meta.tex), img(meta.ntex), img('tc_poop1.webp'), img('tc_poop2.webp'), img('tc_poop3.webp'), img('tc_trash1.webp'), img('tc_trash2.webp'), img('tc_trash3.webp'), img('tc_trash4.webp')]);
    const poopImgs = [p1, p2, p3];
    const h = TCHorse.create(gl, meta, bin, { base: 175, stage: sp.stage, texImg, nrmImg, eyeGlow: sp.eyeGlow || null, lift: sp.lift || 0, poopImgs: poopImgs.filter(Boolean), trashImgs, stance: sp.stance || null, glowK: sp.glowK || null, glowR: sp.glowR || null });
    hcache[sp.key] = h; return h;
  }
  async function useHorse(first, grow) {               // grow＝育って 大きさ・色が かわった だけ（来て いる 馬は 同じ：降臨の バナーは 出し直さない）
    const sp = horseSpec(); if (sp.key === horseKey && HO) return;
    const h = await loadHorse(sp);
    const nb = TCHorse.brain({ tod: tod(), force: [], stand: false }); nb.rnd = Math.random;
    if (BR) { nb.x = BR.x; nb.y = BR.y; nb.dir = BR.dir; } else { nb.x = 470 + Math.random() * 120; nb.y = 1080 + Math.random() * 90; nb.dir = Math.random() * Math.PI * 2; }
    if (sp.light) nb.light = sp.light;
    nb.poops = (st.poops || []).map(q => Object.assign({ t0: -10, h0: 1.05 }, q));
    nb.trash = BR && BR.trash && BR.trash.length ? BR.trash : (st.trash || []).map(q => trashLive(q));      // ゴミは 馬が かわっても そのまま
    HO = h; BR = nb; horseKey = sp.key;
    if (TCCare.on) TCCare.setHorse(HO, BR);
    if (!first && !grow && TCCare.on) TCCare.special(st.visit ? st.visit.kind : null);
  }
  function growCheck() {                               // 大きく 育つ・色が かわる
    const s0 = stageOf(st.cares - 1), s1 = stageOf(st.cares), k0 = scaleOf(st.cares - 1), k1 = scaleOf(st.cares);
    if (st.cares >= 300) {
      st.color = (st.color + 1) % COLORS.length; st.cares = 0; st.gen = (st.gen || 1) + 1; touch();
      msg(`🎉 お世話 300回！\n${COLOR_JA[COLORS[st.color]]}の 子が やってきたよ`, 3.6); useHorse(false, true);      // 第4.168版：幻の馬・神様馬が 来て いる 間は、その 馬の 大きさが 新しい 子の 大きさに なる
      return;
    }
    if (s1 !== s0 || k1 !== k0) { msg(`🎉 お世話 ${st.cares}回！ 大きく 育ったよ`, 3.2); useHorse(false, true); }      // 第4.168版：幻の馬・神様馬が 来て いる 間も（大きさは いつもの 馬と 同じ）
  }

  // ---------- ゴミ ----------
  function trashItems(sd) {                            // 山の 中身（種から いつも 同じ）：2〜4こ・4つの 絵を まぜる
    let a = sd >>> 0; const r = () => { a = (Math.imul(a, 1664525) + 1013904223) >>> 0; return a / 4294967296; };
    const n = 2 + Math.floor(r() * 3), items = [];
    for (let i = 0; i < n; i++) { const k = Math.floor(r() * 4) % 4, an = r() * Math.PI * 2, rad = i === 0 ? 0.06 : 0.16 + 0.2 * r(); items.push({ k, dx: Math.cos(an) * rad, dy: Math.sin(an) * rad, r: r() * Math.PI * 2, w: TRASH_W[k] * (0.86 + 0.28 * r()), d: i * 0.08 }); }
    return items;
  }
  const trashLive = (q, t0) => Object.assign({ x: q.x, y: q.y, sd: q.sd, items: trashItems(q.sd) }, t0 != null ? { t0 } : {});      // 描く 形（tc_horse.js の drawTrash）
  function trashSpots(rnd, hx, hy) {                   // 5か所：歩ける 所の 中・たがいに はなれて いる・馬の 足もと では ない
    const out = [];
    for (let k = 0; k < 400 && out.length < TRASH_N; k++) {
      const a = rnd() * Math.PI * 2, r = Math.sqrt(rnd()), x = Math.round(526 + Math.cos(a) * r * 350), y = Math.round(1110 + Math.sin(a) * r * 265);
      const far = (px, py, d) => Math.hypot(x - px, (y - py) * 2) >= d;
      if (out.every(q => far(q.x, q.y, k < 300 ? 230 : 150)) && (hx == null || far(hx, hy, 170))) out.push({ x, y, sd: Math.floor(rnd() * 4294967296) >>> 0 });
    }
    return out;
  }
  function spawnTrash(t, quiet) {                       // 散らばる（開いて いる ときは ひらひら 落ちて くる）
    st.trash = trashSpots(Math.random, BR && BR.x, BR && BR.y); touch(); save();
    if (BR) BR.trash = st.trash.map((q, i) => trashLive(q, quiet ? null : t + i * 0.16));
    if (!quiet) { SND.se('tc_se_paper.m4a', 0.7); msg('🍂 ゴミが 出たよ！\nおそうじ しよう', 2.8); }
  }
  function trashStep(gms, t) {                          // 1コマ：片付いた → 次の 時刻／時刻が 来た → 散らばる／お世話の 画面へ「あと 何秒」
    if (BR && BR.trashDone) { BR.trashDone = false; st.trash = []; st.trashAt = gms + TRASH_MIN * 60000; touch(); save(); }
    if (BR && !st.trash.length && gms >= st.trashAt && !busy && !resetting && careFree() && !panelOpen() && !(BR.trash && BR.trash.length)) spawnTrash(t, t < 4);
    if (TCCare.on) TCCare.S.trashIn = st.trash.length ? 0 : Math.max(0, st.trashAt - gms) / 1000;
  }

  // ---------- 2分ごとの チャンス・トークン・時間帯・幻の馬／神様馬 ----------
  function fieldName() { return st.visit ? (st.visit.kind === 'kamisama' ? 'divine' : 'abyss') : tod(); }
  async function syncField() {
    const f = fieldName();
    if (field.field !== f) { await field.setField(f); }
    paintBg(f); SND.field(f);
  }
  function paintBg(f) {                                 // 画面の 上下の すき間：いまの フィールドを ぼかして しく
    const bg = ov && ov.querySelector('.tcbg'); if (!bg || bg.dataset.f === f) return;
    bg.dataset.f = f; bg.style.backgroundImage = `url("${AP(`tc_field_${f}.webp`)}")`;
  }
  function chance(t) {                                  // 2分ごと：高確ゾーン・うんち（幻の馬・神様馬は 馬の リセットの とき だけ：第4.144版）
    const now = Date.now();
    if (Math.random() < P_HIGH) { const S = TCCare.S; S.high = HIGH_N; S.highBump = t; S.fx.push({ k: 'luck', t0: t, dur: 2.6 }); SND.se('tc_se_luck.m4a'); st.high = HIGH_N; touch(); }
    if (Math.random() < P_POOP && BR && (BR.poops || []).length < 3) BR.poopReq = true;          // 第4.156版：馬は もう ねない（前は ねて いる 間は しなかった）
    void now;
  }
  async function startVisit(kind) {
    st.visit = { kind, until: tnow() + VISIT_MIN * 60000, el: 0 }; st.rs = { n: 0, at: 0, el: 0 }; touch(); save();
    await useHorse(); await syncField();
    msg(kind === 'kamisama' ? '✨ 神様馬が やってきた！' : '🌙 幻の馬が やってきた！', 3.0);
  }
  async function endVisit() {
    st.visit = null; st.rs = { n: 0, at: 0, el: 0 }; touch(); save();
    await useHorse(); await syncField();
    msg('また 来てね… と 帰って いったよ', 2.6);
  }
  // ---------- 馬の リセット（第4.144版）----------
  const careFree = () => !TCCare.on || (TCCare.S.phase === 'idle' && !TCCare.S.mode && !TCCare.S.busy && !TCCare.S.chooser);      // お世話（撫でる・呼ぶも）の 動きの 途中で ない
  // 第4.159版：お世話の あとの PUSH が 出て いる 間
  //   ・careIdle（PUSH も「途中」）：テスト版の 道具箱 だけ（PUSH を 押して から 次へ）
  //   ・時間で おきる こと（馬の リセット・幻の馬／神様馬の タイムリミット・ゴミ）は PUSH が 出た ままでも 進む（careFree）。
  //     PUSH を 押さずに 置いて おくと タイムリミットが 止まる、という 抜け穴を 作らない（神様馬を 帰さずに トークンを ためて から まとめて 押す、が できて しまう）。
  //     馬を 入れかえるのは 当たりを わたし おわって から（st.pend が ない：ルーレット当選の キュインキュイーンの 間・演出の 間は 入れかえない）
  const careIdle = () => careFree() && !(TCCare.on && TCCare.S.push);
  const panelOpen = () => !!((window.TCPlan && TCPlan.isOpen && TCPlan.isOpen()) || (window.TCGuide && TCGuide.isOpen && TCGuide.isOpen()) || (window.TCTest && TCTest.isOpen && TCTest.isOpen()) || (window.TCBuy && TCBuy.isOpen && TCBuy.isOpen()));
  const rsLeft = gms => (st.rs.at ? Math.max(0, Math.min((st.rs.at + RESET_MIN * 60000 - gms) / 1000, RESET_MIN * 60 - (+st.rs.el || 0))) : null);      // タイマーの のこり（秒）・まだ 動いて いなければ null
  const visitLeft = gms => (st.visit ? Math.max(0, Math.min((st.visit.until - gms) / 1000, VISIT_MIN * 60 - (+st.visit.el || 0))) : null);              // タイムリミットの のこり（秒）
  const drawMax = () => (st.visit ? VISIT_DRAWS[st.visit.kind] || 0 : 0);                                       // いまの 馬の 抽選の 上限（いつもの 馬は 0＝上限 なし）
  const drawLeft = () => { const m = drawMax(); return m ? Math.max(0, m - (st.rs.n || 0)) : Infinity; };      // あと 何回 抽選 できるか
  let resetting = false, capT = null;
  function resetStep(gms, dt, t) {
    const rs = st.rs;
    if (rs.at) rs.el = (+rs.el || 0) + dt;
    if (!rs.at && rs.n >= RESET_CARES && careFree() && !busy) { rs.at = gms; rs.el = 0; touch(); save(); }      // 5回めの お世話が おわった → タイマーが 動く
    // 第4.168版：抽選の 上限（幻の馬 10回・神様馬 5回）を つかい切った → 結果を 見せて（CAP_WAIT 秒）・当たりを わたし おわって・PUSH が 消えて から 帰る
    const capped = drawLeft() < 1;
    if (!capped) capT = null; else if (capT == null) capT = t;
    const capGo = capped && t - capT >= CAP_WAIT && !(TCCare.on && TCCare.S.push);
    if ((capGo || (rs.at && rsLeft(gms) <= 0)) && t > 3 && careFree() && !st.pend && !busy && !panelOpen() && !resetting) { resetting = true; capT = null; doReset().catch(() => { }).finally(() => { resetting = false; }); }
  }
  let forceNext;                               // テスト 用：次の リセットの 抽選の 結果を 決めて おく（_t.force）
  function nextHorse() {                       // 次の 馬の 抽選（null＝いつもの 馬）
    if (forceNext !== undefined) { const f = forceNext; forceNext = undefined; return f; }
    const r = Math.random(); return r < P_KAMI ? 'kamisama' : r < P_KAMI + P_MAB ? 'maboroshi' : null;
  }
  async function doReset() {
    const next = nextHorse();
    st.rs = { n: 0, at: 0, el: 0 }; touch();
    if (next) await startVisit(next);            // 幻の馬・神様馬が やってくる（いま いる 馬と 同じ でも 新しく 来た ことに する：タイムリミットは はじめから）
    else if (st.visit) await endVisit();         // 幻の馬・神様馬は 帰る → いつもの 馬
    else save();                                 // いつもの 馬の まま
    return next;
  }
  function draw() {                                    // お世話の 抽選を 1回 ひく（当たり か null）
    const S = TCCare.S, hi = S.high > 0, k = hi ? HIGH_X : 1;
    if (hi) { S.high -= 1; S.highBump = clock(); st.high = S.high; touch(); }
    if (testPrize !== undefined) { const z = testPrize; testPrize = undefined; return z ? JSON.parse(JSON.stringify(z)) : null; }      // テスト版の 道具で 決めた 結果（1回 だけ）
    const r = Math.random(); let a = 0, tab = st.visit ? PRIZES_VISIT[st.visit.kind] || PRIZES : PRIZES;
    for (const [p, z] of tab) { a += p * k; if (r < a) return Object.assign({}, z, z.k === 'tk' ? { n: tkCount() } : {}); }
    return null;
  }
  function tkCount() { const r = Math.random(); return r < 1 / 8 ? 3 : r < 1 / 8 + 1 / 3 ? 2 : 1; }
  // 第4.140版（バグ直し）：当たりは お世話の はじめに 決まって、お世話の 演出が おわってから 出る。その 間に アプリを 閉じると、当たりが 消えて いた（トークンは 使った のに）。
  //   ルーレット・チケットの 演出の 途中で 閉じても 同じ。→ 決まった 当たりを すぐ 保存（st.pend）して、わたし おわったら 消す。
  //   アプリを 開き直した ときに 残って いたら、その ときに わたす（init）。同じ 当たりを 2回 わたさない：ポイントは 台帳の id（同じ id は 1回だけ）・チケットは 足すのと 消すのを 1回の 保存で
  function lottery() {                                 // tc_care.js が お世話の たびに よぶ
    const z = draw(); if (!z) return null;
    if (st.pend) give(st.pend);                                  // 前の 当たりが まだ なら 先に わたす
    z.id = 'tc-' + Date.now().toString(36) + '-' + Math.floor(Math.random() * 1e6).toString(36);
    if (TCCare.on && TCCare.S.stock !== st.stock) st.stock = TCCare.S.stock;      // 使った トークンも いっしょに 保存（当たり だけ 残って トークンが もどる ことが ない ように）
    if (z.k === 'rt') { const ab = z.v || RT[z.tier] || RT.normal; if (z.win == null) z.win = Math.random() < 0.5 ? 0 : 1; z.a = ab[0]; z.b = ab[1]; }      // ルーレットの 止まる 所も ここで 決める（50%ずつ）
    if (z.k === 'zn') { z.n = z.n == null ? zoneRoll() : Math.max(0, Math.min(ZONE.max, Math.round(+z.n) || 0)); z.v = zoneV(z.n); }      // 特化ゾーン：何回 上乗せ できるか（1回ごとに 60%）と 合計も ここで 決める
    st.pend = JSON.parse(JSON.stringify(z)); touch(); save();
    return z;
  }
  // 当たりを わたす（ポイント → 台帳・チケット → 数を 足す）。返り値＝わたした ポイント（チケットは 0）
  function give(z) {
    if (!z) return 0;
    let v = 0;
    if (z.k === 'pt') { v = +z.v || 0; grant(v, 'トレーニングセンターの お世話', z.id); }
    else if (z.k === 'rt') { const ab = z.a != null ? [z.a, z.b] : (z.v || RT[z.tier] || RT.normal); v = ab[z.win ? 1 : 0]; grant(v, 'トレーニングセンターの ルーレット', z.id); }
    else if (z.k === 'zn') { v = +z.v > 0 ? +z.v : zoneV(z.n); grant(v, 'トレーニングセンターの ポイント特化ゾーン', z.id); }
    else if (z.k === 'tk') st.tickets = (st.tickets || 0) + (z.n || 1);
    if (st.pend && (!z.id || st.pend.id === z.id)) st.pend = null;
    touch(); save();
    return v;
  }
  async function onPrize(z) {                           // 当たり（お世話の 演出が おわってから）
    if (z.k === 'pt') { give(z); return; }
    if (busy || !window.TCFX) { give(z); if (ov) paintHead(); return; }      // 演出を 出せない ときも 当たりは わたす（前は 消えて いた）
    busy = true; TCCare.roulette(true);
    try {
      if (z.k === 'rt') {
        if (z.win == null) z.win = Math.random() < 0.5 ? 0 : 1;
        const [a, b] = z.a != null ? [z.a, z.b] : (z.v || RT[z.tier] || RT.normal);
        SND.preload(z.tier === 'normal' || !z.tier ? ['sfx_big.m4a', 'tc_se_dedeen.m4a'] : ['sfx_big.m4a', 'sfx_sdp.m4a', 'tc_se_doon.m4a', 'tc_se_boom.m4a']);      // 止まった あとの 音を 回って いる 間に 読んで おく（第4.168版：ノーマルは プチュン・ドーン！！を 使わない＝高い 方は デデーン）
        // 第4.168版：ルーレットの 間は ルーレットの BGM（フィールドの 音は 消す：重ねない）。幻の馬・神様馬の 高い 方は プチュンで 音を 止める（onCut）。おわったら フィールドの 音に もどす
        // 第4.171版（まさちゃん 2026/11/14 17:48「神様馬のルーレット中のBGMはなしで！」）：神様馬の ルーレットの 間は BGM なし（フィールドの 音も ルーレットの BGM も 鳴らさない：
        //   'none'＝音の ない 名前 → いまの 音を 0.3秒で 消す だけ）。音は レバー・カチッ・止まる 音・プチュン・爆発・ドーン！！ だけ。ノーマル・幻の馬の ルーレットは いままで どおり ルーレットの BGM
        SND.bgm(z.tier === 'kamisama' ? 'none' : 'roulette');
        try { await TCFX.roulette(cvFx, { th: z.tier, a, b, win: z.win, bg: fieldName(), se: SND.se, onCut: () => SND.bgm('') }); } finally { SND.bgm(null); give(z); }      // 第4.159版：止まった あと 安い 方＝デカ的中と 同じ 音・高い 方＝プチュン → ドーン！！と テロップ「大量ポイント」（tc_fx.js）
      } else if (z.k === 'zn') {
        // 第4.165版：ポイント特化ゾーン（tc_fx.js の zone）。何回 上乗せ できるか（z.n）は もう 決まって いる → レバーを 1回ずつ 押して 見せる。おわったら（途中で 閉じても）合計を わたす
        SND.preload(['tc_se_zn_up.m4a', 'tc_se_zn_down.m4a', 'tc_se_rt_lever.m4a', 'sfx_big.m4a', 'tc_se_doon.m4a']);
        try { await TCFX.zone(cvFx, { n: z.n, start: ZONE.start, add: ZONE.add, max: ZONE.max, rate: ZONE.rate, bg: fieldName(), se: SND.se }); } finally { give(z); }
      } else if (z.k === 'tk') {
        const n = z.n || 1;
        // 第4.159版（まさちゃん 11/12「プチュンしてから今の演出」・11:56「プチュンは、極ど的中と超プレミアム神様的中で使用してたプチュンの演出入れてね！プチュンしたらすぐに扉が落ちてくる演出にして！」）：
        //   押した 瞬間に プチュン（的中の 演出と 同じ 部品）→ 真っ暗に なったら すぐ 扉が 落ちて くる（tc_fx.js の ticket の puchun）
        try { await TCFX.ticket(cvFx, { n, bg: fieldName(), se: SND.se, puchun: true }); } finally { give(z); paintHead(); }
        msg(`🎫 チケット ${n}枚 GET！\n設定の「着せ替え」で\n壁紙か ${TKP()}P を\n選べるよ`, 4.4);      // 第4.141版（11/10 15:52 まさちゃん「壁紙チケット or 8000pにして！」→ 16:08「じゃあ7000pにして！」）
      }
    } finally { busy = false; TCCare.roulette(false); }
  }
  // 第4.168版：合計ポイント（上の 帯の「ポイント」と 同じ 数：TengelWallet.total）。トレーニングセンターの 右上（作戦会議の ボタンの 下）に 出す（tc_care.js の O.points）。
  //   台帳が かわる たび（当たり・トークンの 購入・ほかの 画面での 買い物）に 読み直す（document の 'tengel:wallet'）。まだ 読めて いない ときは null（札は 出さない）
  let ptTotal = null;
  function ptSync() { try { const w = window.TengelWallet; ptTotal = w && typeof w.total === 'function' ? Math.max(0, Math.round(+w.total() || 0)) : null; } catch (e) { ptTotal = null; } return ptTotal; }
  const walletTotal = () => ptTotal;
  document.addEventListener('tengel:wallet', ptSync);
  function grant(v, what, id) {
    const w = window.TengelWallet;
    if (w && typeof w.grant === 'function' && v > 0) w.grant(id || ('tc-' + Date.now().toString(36) + '-' + Math.floor(Math.random() * 1e6).toString(36)), v, what).catch(() => { });
  }

  // ---------- お世話トークンの 購入（第4.165版・まさちゃん 2026/11/13 11:46「お世話トークンは、購入できるようにする。①1個を80Pで購入 ②5個を400Pで購入 ③10個を800Pで購入
  //   ④15個を1200Pで購入 ②25個を2000Pで購入　お世話トークン購入、のアイコンを左下のお世話などの項目の上に設置　アイコンは一枚目」
  //   → 12:33「お世話トークン呼ぶのすぐ上にして！」→ 12:36「お世話トークン購入のアイコンやっぱりこっちで！（丸い 絵）お世話とかのところに上手く入れられない？」→ 12:38「1番右側に入れて！」）----------
  //   ・下の 列（撫でる・ごはん・おそうじ・呼ぶ）の 1番 右に まさちゃんの 丸い 絵の ボタン（tc_icon_buy2.webp：kisekae/tc/buy_asset.py・リポジトリに 入れない）。
  //     描くのと 押した ことを 受けるのは tc_care.js（BUYG・O.onBuy）：ほかの ボタンと 同じ（お世話の あとの PUSH が 出て いる 間は 列ごと かくれる）→ 押すと 購入の 窓（tc_buy.js の TCBuy）。
  //     開くのは お世話の 動き・当たりの 演出・馬の 入れかえの 途中で ない とき（buyShow）。途中の ときは 札「お世話が おわってから 買えるよ」（tc_care.js の pressBuy）
  //   ・組と 値段は points.js の TOKEN_PACKS（1こ 100P：第4.168版。第4.167版までは 1こ 80P・5つの 組）。ポイントは 台帳（TengelWallet.tc.buy：買った ポイントから 先に 使う・あずかりポイントは 先に 補充）
  //   ・持てる 数は TOKEN_MAX（25こ）まで（聞いて 決めた 11:5x「25こまで」）：いまの 数 ＋ 買う 数が 25こを こえる 組は その ときは 買えない
  //   ・途中で 閉じても ずれない：台帳に 入れる 前に 買い物の しるし（st.buy＝{ id, n }）を 保存 → 台帳に 入ったら トークンを 足して しるしを 消す（1回の 保存で）。
  //     台帳に 入った あと・トークンを 足す 前に アプリが 閉じた ときは、次に 開いた ときに 台帳を 見て わたす（recoverBuy）。台帳に なければ しるし だけ 消す（ポイントは へって いない）
  //   ・買って いる 間（台帳の 保存を 待つ 間）は 時間で たまる ぶんを 待たせる（frame）：待って いる 間に ＋5 が 入って 25こを こえる ことが ない
  const PACKS = () => { const P = window.TengelPoints; return (P && P.TOKEN_PACKS ? P.TOKEN_PACKS : [[1, 100], [5, 500], [10, 1000], [15, 1500], [20, 2000], [25, 2500]]).map(x => x.slice()); };      // 第4.168版：1こ 100P・20この 組も（points.js）
  const stockNow = () => { if (TCCare.on && TCCare.S.stock !== st.stock) { st.stock = TCCare.S.stock; touch(); } return st.stock; };      // お世話で 使った ぶんを 先に 写す
  function stockSet(n, plus) {                         // トークンの 数を 決める（右上の 数も いっしょに・plus＝「＋N」を 出す）
    st.stock = n; touch();
    if (TCCare.on) { const S = TCCare.S, t = clock(); S.stock = n; S.stockShow = n; S.stockBump = t; if (plus) S.fx.push({ k: 'plus', t0: t, txt: '+' + plus }); }
  }
  const buyShow = () => !!(built && TCCare.on && HO && BR && !busy && !resetting && careIdle() && !TCCare.S.fxHold && !panelOpen());      // 購入の 窓を 開いて よい とき（お世話・PUSH・当たりの 演出・馬の 入れかえの 途中で ない）
  const BUY = {
    // いまの ようす：トークン・持てる 数・ポイント（使える 数＝財布＋あずかり）・組ごとに 買えるか（ok／full＝25こを こえる／short＝ポイントが 足りない）
    info() {
      const w = window.TengelWallet, stock = st ? stockNow() : 0, pts = w && w.avail ? w.avail() : 0;
      return { stock, max: TOKEN_MAX, room: Math.max(0, TOKEN_MAX - stock), points: pts, ready: !!(w && w.tc), busy: buying, every: TOKEN_MIN, step: TOKEN_STEP,
        packs: PACKS().map(([n, c]) => ({ n, cost: c, state: stock + n > TOKEN_MAX ? 'full' : pts < c ? 'short' : 'ok' })) };
    },
    // 買う：n＝こ数（TOKEN_PACKS に ある 数）。返り値 { ok, why（off・busy・full・short・err）, n, cost, stock }
    async buy(n) {
      const w = window.TengelWallet, pk = PACKS().find(x => x[0] === +n);
      if (!st || !w || !w.tc || !pk) return { ok: false, why: 'off' };
      if (buying) return { ok: false, why: 'busy' };
      buying = true;
      try {
        stockNow();                                    // お世話で 使った ぶんを 先に 写して から
        const got = accrue(tnow());                    // たまって いる ぶんを 入れる（この あと 買い終わる まで たまるのは 待たせる：frame）
        if (got > 0) stockSet(st.stock, got);
        const s0 = st.stock;
        if (s0 + pk[0] > TOKEN_MAX) return { ok: false, why: 'full', room: Math.max(0, TOKEN_MAX - s0) };
        const id = 'b' + Date.now().toString(36) + '-' + Math.floor(Math.random() * 1e9).toString(36);
        st.buy = { id, n: pk[0] }; touch(); save();
        let r; try { r = await w.tc.buy(id, pk[0]); } catch (e) { r = { ok: false, why: 'err' }; }
        if (!r || !r.ok) { st.buy = null; touch(); save(); return r || { ok: false, why: 'err' }; }
        const s1 = stockNow() + pk[0];
        st.buy = null; stockSet(s1, pk[0]); save();    // トークンを 足すのと しるしを 消すのは 1回の 保存で
        SND.se('tc_se_stock.m4a');
        return { ok: true, n: pk[0], cost: pk[1], stock: s1 };
      } finally { buying = false; }
    },
    guide() { if (window.TCGuide) TCGuide.open(stage, { anim: true }); },
    se: name => SND.se('tc_se_' + name + '.m4a'),
  };
  async function recoverBuy() {                        // 前に 買って すぐ 閉じた：台帳に 入って いれば トークンを わたす・入って いなければ しるし だけ 消す
    const b = st.buy; if (!b) return;
    const w = window.TengelWallet, n = Math.max(0, Math.round(+b.n || 0));
    if (!b.id || !n) { st.buy = null; touch(); save(); return; }
    if (!w || !w.tc) return;                           // 台帳が まだ 読めない → 次に 開いた とき
    try { await w.ready; } catch (e) { return; }
    if (buying || !st.buy || st.buy.id !== b.id) return;
    if (w.tc.paid(b.id)) { st.buy = null; stockSet(stockNow() + n, n); save(); later.push(() => msg(`🎟 前に 買った\nお世話トークン ${n}こを\n受け取ったよ`, 3.6)); }
    else { st.buy = null; touch(); save(); }
  }

  // ---------- テスト版の 道具（第4.154版・まさちゃん 2026/11/11 20:00「テスト版で、トレーニングセンターの幻の馬と神様馬の出現テストできるようにして！
  //   お世話の当選パターン全種類テストできるようにして！」）----------
  //   テスト版（TENGEL_TEST=1 で 作った アプリ：window.__TEST）だけ、上の 帯に「🧪 テスト」→ 紙の 道具箱（tc_test.js：テスト版の tc_bundle.js に だけ 入る）。
  //   ここは 道具箱が よぶ 入口（TEST）。App Store版では 道具箱が ない ので 何も しない（testOn が false）。
  //   ・馬：本番と 同じ 流れ（リセットの 抽選で 当たった ときの doReset → startVisit／帰る ときの endVisit）を そのまま よぶ ＝ 見え方・音・タイムリミットは 本番と 同じ
  //   ・当たり：次の お世話（ごはん・おそうじ）の 抽選の 結果を 1回 だけ 決める（testPrize → draw）。わたし方（ポイントは 台帳・ルーレット・チケットの 演出）は 本番と 同じ
  //   ・そのほか（ハートの 抽選・金のニンジン・おかわりの目・首を かしげる・ほうきを かじる・呼ぶの 3つ）：tc_care.js の S.test（次の 1回 だけ）
  function testOn() { return !!(window.__TEST && window.TCTest); }
  let testPrize;                 // undefined＝いつもの くじ・null＝はずれ・{ k, … }＝この 当たり
  let testGold = false;          // 次に 出る うんちを 金のうんちに
  const testFree = () => !!(HO && BR && !busy && !resetting && careIdle());      // お世話・当たりの 演出・馬の 入れかえの 途中で ない
  const TEST = {
    info() {
      const S = TCCare.S;
      return { visit: st.visit ? st.visit.kind : null, left: st.visit ? visitLeft(tnow()) : null, stock: S.stock, heart: S.heart, high: S.high || 0, tickets: st.tickets || 0, cares: st.cares, color: COLOR_JA[COLORS[st.color % COLORS.length]],
        prize: testPrize, gold: testGold, flags: Object.assign({}, S.test || {}), trash: (BR && BR.trash ? BR.trash.length : 0), poops: (BR && BR.poops ? BR.poops.length : 0), free: testFree(), push: !!S.push };      // push：お世話の あとの PUSH が 出て いる
    },
    // 馬を かえる：kind＝'maboroshi'・'kamisama'・null（いつもの 馬）。返り値：'ok'・'same'（もう その 馬）・'busy'（お世話の 途中）
    async visit(kind) {
      if (!testOn()) return 'off';
      kind = kind === 'maboroshi' || kind === 'kamisama' ? kind : null;
      if ((st.visit ? st.visit.kind : null) === kind) return 'same';
      if (!testFree()) return 'busy';
      resetting = true;
      try { if (kind) { forceNext = kind; await doReset(); } else await endVisit(); } finally { resetting = false; forceNext = undefined; }
      return 'ok';
    },
    // 次の お世話の 当たり：z＝undefined（くじに もどす）・null（はずれ）・{ k:'pt', v }・{ k:'rt', tier, v:[a,b]（なければ 表の 数）, win:0か1 }・{ k:'tk', n }
    //   horse＝その 当たりが 出る 馬（'normal'・'maboroshi'・'kamisama'）：ちがう 馬が いる ときは 先に 入れかえる（本番で 起きる 組み合わせ だけ ためす）
    async prize(z, horse) {
      if (!testOn()) return 'off';
      if (z === undefined) { testPrize = undefined; return 'ok'; }
      if (horse) { const r = await TEST.visit(horse === 'normal' ? null : horse); if (r === 'busy' || r === 'off') return r; }
      testPrize = z ? JSON.parse(JSON.stringify(z)) : null;
      if (TCCare.S.stock < 1) TEST.tokens();          // トークンが ない と ためせない
      return 'ok';
    },
    tokens(n) {                           // n なし＝25こ（上限）に。n あり＝ちょうど nこに（第4.159版：ハートの 抽選は 20こ未満の とき だけ → 19こに して ためす）
      if (!testOn()) return 'off';
      const S = TCCare.S; st.stock = n == null ? Math.max(st.stock, TOKEN_MAX) : Math.max(0, Math.min(TOKEN_MAX, Math.round(n))); st.stockAt = tnow(); S.stock = st.stock; S.stockBump = clock(); touch(); save(); return 'ok';
    },
    // 第4.165版：お世話トークンの 時計を min 分 進める（たまる のを ためす：5分で ＋5）。返り値：'ok'・'max'（もう 25こ）
    ahead(min) {
      if (!testOn()) return 'off';
      stockNow(); if (st.stock >= TOKEN_MAX) return 'max';
      st.stockAt = Math.min(st.stockAt, tnow()) - Math.max(1, Math.round(+min || TOKEN_MIN)) * 60000; touch(); return 'ok';      // 次の コマで たまる（frame の accrue：右上に「＋5」）
    },
    // 第4.165版：お世話（ごはん・おそうじ）を とばして、お世話の あとの PUSH を すぐ 出す（当たりを つづけて ためす）。押すと 本番と 同じ ように トークン −1・抽選
    push() {
      if (!testOn()) return 'off';
      if (!testFree()) return 'busy';
      if (TCCare.S.stock < 1) TEST.tokens();
      TCCare.pushShow(clock() + 0.25); return 'ok';
    },
    // 撫でる：ハートを 9こに して、次の 抽選（ハート 10こ）の 結果を 決める（win＝true：ぴょん！／false：ふぅ〜〈第4.155版までは ごろん〉）
    heart(win) {
      if (!testOn()) return 'off';
      const S = TCCare.S; if (S.busy || S.lot) return 'busy';
      const n = TCCare.RULE.max - 1; S.heart = S.heartShow = n; st.heart = n; S.got = []; S.coolUntil = -1e9; S.petN = 0; S.drainT = null;
      S.test = Object.assign(S.test || {}, { win: !!win }); touch(); return 'ok';
    },
    // 次の 1回 だけ：gold（金のニンジン）・beg（おかわりの目）・rare（首を かしげる）・nibble（ほうきを かじる）・call（'come'・'turn'・'amae'）
    flag(k, v) {
      if (!testOn() || ['gold', 'beg', 'rare', 'nibble', 'call'].indexOf(k) < 0) return 'off';
      const S = TCCare.S; S.test = Object.assign(S.test || {}, { [k]: v }); return 'ok';
    },
    high() {
      if (!testOn()) return 'off';
      const S = TCCare.S, t = clock(); S.high = HIGH_N; S.highBump = t; S.fx.push({ k: 'luck', t0: t, dur: 2.6 }); SND.se('tc_se_luck.m4a'); st.high = HIGH_N; touch(); return 'ok';
    },
    trash() {
      if (!testOn()) return 'off';
      if (st.trash.length || (BR && BR.trash && BR.trash.length)) return 'have';
      if (!testFree()) return 'busy';
      spawnTrash(clock(), false); return 'ok';
    },
    // うんちを させる（gold＝金のうんち）。3こ まで（第4.168版：幻の馬・神様馬も いつもの 馬と 同じ）
    poop(gold) {
      if (!testOn()) return 'off';
      if (!BR || (BR.poops || []).filter(q => !q.sw).length >= 3) return 'full';
      if (!testFree()) return 'busy';
      BR.poopReq = true; if (gold) testGold = true; return 'ok';
    },
    // 第4.156版：ねて いる 馬を 起こす（wake）は なくした（馬は もう ねない＝寝転ぶ 演出を ぜんぶ 消した）
    msg: (txt, sec) => msg(txt, sec),
  };

  // ---------- なめらかさを 守る（第4.150版・まさちゃん 2026/11/11 02:43「トレーニングセンターも今は、カクカクしてる！ヌルヌル動くことが絶対！」）----------
  //   画面の 書きかえ ごと（ふつう 60コマ／秒）に 描く（前は 30コマ／秒に おさえて いた＝歩く 馬・お世話の 動きが カクカクして 見えた）。
  //   描くのが 間に合わない 端末では、絵の 細かさを 1段ずつ 下げて（GOV_Q）なめらかさを 守る。細かさは 画面を 開き直しても そのまま（アプリを 閉じる まで）。
  //   下げても よく ならない とき（省電力モードで 画面の 書きかえが 30回／秒に おさえられて いる・ほかの 所が おそい）は 細かさの せいでは ない ので、もとに もどして もう 下げない。
  //   数え方：コマと コマの 間が 25ms より 長い＝1コマ 落ちた。120コマ ごとに 落ちた わりあいを 見る（4割 以上で 下げる）。細かさを かえた あと 45コマと、止まって いた あとの 1コマは 数えない
  const GOV_Q = [1, 0.82, 0.68], GOV_N = 120, GOV_BAD = 0.4, GOV_SAME = 0.75, GOV_WAIT = 45;
  const GOV = { q: 1, step: 0, off: false, n: 0, slow: 0, wait: GOV_WAIT, base: 0, last: 0 };
  function govSet(step, off) { GOV.step = step; GOV.q = GOV_Q[step]; GOV.off = !!off; GOV.n = GOV.slow = 0; GOV.wait = GOV_WAIT; if (ov && stage && cvGL) layout(); }
  function govern(now) {
    const d = now - GOV.last; GOV.last = now;
    if (GOV.off || !(d > 0) || d > 250) return;                    // はじめの 1コマ・止まって いた あと
    if (GOV.wait > 0) { GOV.wait--; return; }
    GOV.n++; if (d > 25) GOV.slow++;
    if (GOV.n < GOV_N) return;
    const r = GOV.slow / GOV.n; GOV.n = GOV.slow = 0;
    if (GOV.step > 0 && GOV.base > 0 && r >= GOV.base * GOV_SAME) { govSet(GOV.step - 1, true); return; }      // 下げても かわらない → 1段 もどして おわり
    GOV.base = 0;
    if (r < GOV_BAD) return;                                        // なめらか
    if (GOV.step >= GOV_Q.length - 1) { GOV.off = true; return; }   // いちばん 下の 段でも おそい → これ以上は 下げない
    GOV.base = r; govSet(GOV.step + 1, false);
  }

  // ---------- 1コマ ----------
  function frame(now) {
    raf = requestAnimationFrame(frame);
    govern(now);
    lastDraw = now;
    const t = clock(), dt = lastT == null ? 1 / 60 : Math.max(0, Math.min(0.1, t - lastT)); lastT = t;
    const ms = Date.now(), gms = tnow();
    // 第4.140版（バグ直し）：お世話で 使った トークンを 先に 写す（前は トークンが ちょうど 1つ たまる 瞬間と 重なると、使った ぶんが 消えて 1回 タダに なった）
    if (TCCare.on && TCCare.S.stock !== st.stock) { st.stock = TCCare.S.stock; touch(); }
    const got = buying ? 0 : accrue(gms);              // 第4.165版：買って いる 間は 待たせる（買い終わった 次の コマで 入る）
    if (got > 0 && TCCare.on) { const S = TCCare.S; S.stock = st.stock; S.stockShow = st.stock; S.stockBump = t; S.fx.push({ k: 'plus', t0: t, txt: '+' + got }); }      // 開いて いる 間に たまった：右上の 数が ぽんと ふえて「＋5」
    if (t >= nextTick) { nextTick = t + TICK; if (t > 3) chance(t); }
    if (!resetting) trashStep(gms, t);
    if (BR && !st.visit) BR.tod = tod();
    if (st.visit) st.visit.el = (+st.visit.el || 0) + dt;                                       // 開いて いる あいだに たった 秒（時計を もどしても 30分で 帰る）
    if (st.visit && visitLeft(gms) <= 0 && !busy && careFree() && !st.pend && !panelOpen() && !resetting) { resetting = true; endVisit().catch(() => { }).finally(() => { resetting = false; }); }      // タイムリミット → いつもの 馬
    else if (!resetting) resetStep(gms, dt, t);
    if (TCCare.on) TCCare.S.vinfo = st.visit ? { kind: st.visit.kind, left: visitLeft(gms), n: Math.min(st.rs.n || 0, RESET_CARES), need: RESET_CARES, timer: rsLeft(gms), draws: Math.min(st.rs.n || 0, drawMax() || 0), max: drawMax() } : null;      // バナーの 下の「切り替わる 条件」（tc_care.js が かく）
    if (resetting) { /* 馬を かえて いる 途中 */ }
    else if (!busy && field.field && field.field !== fieldName() && !frame._sw) { frame._sw = true; syncField().finally(() => { frame._sw = false; }); }
    while (later.length) { try { later.shift()(); } catch (e) { } }
    if (!HO || !BR) return;
    const ZV = TCCare.on ? TCCare.view() : null;
    field.render(t, ZV);
    const cvv = gl.canvas, kk = cvv.width / W, Z = ZV ? ZV.z : 1, ZX = ZV ? ZV.cx : W / 2, ZY = ZV ? ZV.cy : H / 2;
    if (TCCare.on) TCCare.pre(t, dt);
    TCHorse.step(HO, BR, t, dt, BR.rnd);
    TCHorse.draw(HO, BR, t, { W: cvv.width, H: cvv.height, k: kk * Z, ox: cvv.width / 2 - ZX * kk * Z, oy: cvv.height / 2 - ZY * kk * Z });
    if (TCCare.on) TCCare.post(t);
    // 保存する もの（トレセンの 紙の 絵が かえた 数）
    const S = TCCare.S;
    if (S.stock !== st.stock) { st.stock = S.stock; touch(); }
    if (S.heart !== st.heart) { st.heart = S.heart; touch(); }
    if ((S.high || 0) !== (st.high || 0)) { st.high = S.high || 0; touch(); }
    const ps = (BR.poops || []).filter(q => !q.sw).map(q => { if (q.gold == null) { q.gold = testGold || Math.random() < P_GOLD; testGold = false; } return { x: Math.round(q.x), y: Math.round(q.y), img: q.img || 0, w: q.w, gold: !!q.gold }; });
    if (JSON.stringify(ps) !== JSON.stringify(st.poops)) { st.poops = ps; touch(); }
    if (dirty && ms - saveAt > 2000) { saveAt = ms; save(); }
  }
  function pause() { running = false; cancelAnimationFrame(raf); SND.stopAll(); if (dirty) save(); }
  function resume() {
    if (running) return; running = true; lastT = null; lastDraw = 0; GOV.last = 0; GOV.n = GOV.slow = 0; GOV.wait = GOV_WAIT; SND.unlock(); syncField(); raf = requestAnimationFrame(frame);
  }

  // ---------- 開く・閉じる ----------
  let ready = null;
  async function init() {
    load(); build(); paintHead(); SND.setOn(st.snd);
    ov.classList.add('on'); const cs = layout();
    field = TCField.create(cvGL); if (!field) throw new Error('webgl');
    gl = field.gl; tBase = performance.now();
    if (!st.fav || st.fav.day !== today()) { st.fav = { day: today(), kind: ['esa', 'apple', 'carrot'][Math.floor(Math.random() * 3)] }; touch(); }
    if (st.visit && (tnow() > st.visit.until || (+st.visit.el || 0) >= VISIT_MIN * 60)) st.visit = null;
    if (st.pend) {      // 第4.140版：前に アプリを 閉じた ときに わたせなかった 当たりを わたす
      const z = st.pend, v = give(z);
      later.push(() => msg(z.k === 'tk' ? `🎫 前の 当たり（チケット ${z.n || 1}枚）を 受け取ったよ` : `🎁 前の 当たり（${v.toLocaleString('ja-JP')}P）を 受け取ったよ`, 3.6));
    }
    accrue(tnow());
    await Promise.all([useHorse(true), field.setField(fieldName())]); paintBg(fieldName());
    await TCCare.init({ horse: HO, brain: BR, canvas: cvOv, cs, tod: tod(), bg: st.visit ? fieldName() : '', stageNo: stageOf(st.cares),
      lottery, onPrize, onEvent: onCareEvent, banTop: 290, dropX: 726, hiX: 580, hiY: 204, points: walletTotal, onHelp: () => { if (window.TCGuide) TCGuide.open(stage, { anim: true }); },
      onBuy: () => { if (!window.TCBuy || !buyShow()) return false; TCBuy.open(stage, BUY); return true; },      // 第4.165版：下の 列の「お世話トークン購入」（tc_care.js が 描く）→ 購入の 窓
      stockMax: TOKEN_MAX, bulk: !!st.bulk, onBulk: v => { st.bulk = !!v; touch(); save(); }, onPush: on => { st.push = !!on; touch(); save(); },
      lotFree: () => !busy && !resetting && !panelOpen() && !st.pend, drawLeft });      // drawLeft（第4.168版）：幻の馬・神様馬の 抽選の のこり（上限で PUSH を 消す）      // 第4.159版：PUSH の スイッチ（1個／まとめて）と「PUSH が まだ 出て いる」を おぼえる・待って いた ハートの 抽選を 始めて よいか（当たりの 演出・馬の 入れかえ・説明書などの 途中で ない）
    const S = TCCare.S; S.heart = S.heartShow = st.heart || 0; S.stock = S.stockShow = st.stock; S.high = st.high || 0; S.fav = st.fav.kind;
    if (st.push) { if (st.stock >= 1) TCCare.pushShow(clock() + 0.9); else { st.push = false; touch(); } }      // 前に お世話を した あと PUSH を 押す 前に 閉じた → また 出す（お世話 1回には トークンを 1つは 使う）
    nextTick = clock() + TICK;
    recoverBuy().catch(() => { });                     // 第4.165版：前に 買って すぐ 閉じた ぶん（台帳に 入って いれば トークンを わたす）
    SND.preload(['tc_bgm_roulette.m4a', 'tc_se_button.m4a', 'tc_se_unfold.m4a', 'tc_se_rub.m4a', 'tc_se_heart.m4a', 'tc_se_pick.m4a', 'tc_se_chooser.m4a', 'tc_se_token.m4a', 'tc_se_pfo.m4a', 'tc_se_piron.m4a', 'tc_se_dedeen.m4a', 'tc_se_kyuin.m4a', 'sfx_sdp.m4a']);      // PUSH の 音は 先に 読む（押した 瞬間に 鳴る：チケット当選の プチュン〈的中の 演出の 音〉も）
  }
  async function open(opt) {
    SND.unlock();
    try {
      if (!ready) ready = init(); else { load(); ov.classList.add('on'); layout(); const S = TCCare.S; S.heart = S.heartShow = st.heart || 0; S.high = st.high || 0; S.wakeT = clock(); if (BR && careFree()) BR.trash = st.trash.map(q => trashLive(q)); }
      await ready;
    } catch (e) { ready = null; if (ov) ov.classList.remove('on'); note('トレーニングセンターを ひらけなかったよ（' + (e && e.message || e) + '）'); return; }      // 第4.140版：alert() は アプリの 中で 出ない → 画面の お知らせ
    const ld = ov.querySelector('.tcld'); if (ld) ld.remove();
    paintHead(); layout(); accrue(tnow()); ptSync();      // ptSync（第4.168版）：開く たびに 合計ポイントを 読み直す
    if (TCCare.on) { const S = TCCare.S; S.stock = S.stockShow = st.stock; S.ptShow = null; }
    resume();
    if (opt && opt.plan && window.TCPlan) window.TCPlan.open(ov);
    if (opt && opt.test && testOn() && !TCTest.isOpen()) TCTest.open(stage, TEST);      // 第4.165版：設定の「テスト版の道具」から 道具箱を 開いた まま 入る（テスト版 だけ）
  }
  function close() {
    if (window.TCPlan && window.TCPlan.isOpen && window.TCPlan.isOpen()) window.TCPlan.close();
    if (window.TCGuide && TCGuide.isOpen && TCGuide.isOpen()) TCGuide.close();
    if (window.TCBuy && TCBuy.isOpen && TCBuy.isOpen()) TCBuy.close();
    pause(); save(); if (ov) ov.classList.remove('on');
    try { document.dispatchEvent(new CustomEvent('tengel:tc')); } catch (e) { }      // ミッション（お世話の 合計）を かき直す
  }
  // 着せ替え（kisekae.js）から：チケットの 数・使う
  const tickets = { count: () => { if (!st) load(); return st.tickets || 0; }, use: () => { if (!st) load(); if ((st.tickets || 0) < 1) return false; st.tickets -= 1; save(); if (ov) paintHead(); return true; },
    back: () => { if (!st) load(); st.tickets = (st.tickets || 0) + 1; save(); if (ov) paintHead(); return true; } };      // back＝使った 1枚を もどす（着せ替えで 解放できなかった とき：第4.140版）
  return { open, close, tickets, get state() { return st; }, test: TEST, buy: BUY, _snd: SND, _t: { buyShow, recoverBuy, PACKS, ZONE, zoneV, zoneRoll, gov: GOV, govern, govSet, GOV_Q, lottery, draw, give, onPrize, PRIZES, PRIZES_VISIT, fieldName, startVisit, endVisit, doReset, nextHorse, drawMax, drawLeft, force: k => { forceNext = k; }, chance, rsLeft, visitLeft, RT, trash: { spawn: quiet => spawnTrash(clock(), quiet), spots: trashSpots, items: trashItems, step: trashStep, min: TRASH_MIN, n: TRASH_N }, ODDS: { trashMin: TRASH_MIN, trashN: TRASH_N, poop: P_POOP, gold: P_GOLD, high: P_HIGH, mab: P_MAB, kami: P_KAMI, highX: HIGH_X, highN: HIGH_N, tick: TICK, visitMin: VISIT_MIN, visitDraws: Object.assign({}, VISIT_DRAWS), capWait: CAP_WAIT, resetCares: RESET_CARES, resetMin: RESET_MIN, tokenMin: TOKEN_MIN, tokenStep: TOKEN_STEP, tokenMax: TOKEN_MAX, zone: Object.assign({}, ZONE) } } };      // _t：テスト 用
})();
