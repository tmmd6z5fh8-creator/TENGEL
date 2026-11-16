// 馬カードバトルの 画面（App Store版）：メニュー・部屋・対戦・あそび方（第4.176版・まさちゃん 2026/11/15 21:41「TENGER馬カードバトル」）
//   ・絵は まさちゃんの もの（カード 9種・うら・プレイボード・山札・アイコン：kisekae/cb_art.py が アプリ用に した cb_*.webp）。背景は まさちゃんの 絵が 来るまで かりの 色（.cbbg）
//   ・ルールは cb_rules.js・相手（コンピュータ／部屋の 友だち）との やりとりは cb_net.js。ここは 見せる だけ：
//       画面に 出すのは「自分に 見せて いい こと」（view）だけ。おきた こと（ev）を 順に 動かして から、その あとの 形（view）を かき直す
//   ・画面の 形：縦（上から 相手の 手札 → プレイボード〈まさちゃんの 絵 ぜんぶ〉→ 自分の 手札）。ボードの 上の カードは 小さい ので、
//       めくる とき・カードを タップした ときは 大きい カード（効果の 文が 読める 大きさ）を 前に 出す
//   ・1ターンの 流れ（まさちゃん 23:12）：セット（「この カードを セットする」＝確定・もう 変えられない）→ 2人とも セットしたら 効果タイム
//       （使える 効果を 1つ ずつ「使う？」と 聞く：6 → 5 → 7 → 4 の 順。答え終わったら まとめて 送る）→ オープン。
//       神様馬・幻の馬で 勝った ときの 効果は、次の ターンの はじめに「使う？」と 聞く
//   ・捨て札（まさちゃん 23:15）：ボードの 捨て札（1番 上の カードが 見える）を タップ →「終わった ターンの 捨て札」と「効果で 捨てた カード」に 分けて 見せる
//   ・ごほうび（まさちゃん 21:4x の 答え「お世話トークン1個、5連勝で3個」）：勝つと お世話トークン 1こ・5連勝 ごとに 3こ（トレーニングセンターの TCGift：持てる 数は 25こ まで）
//       負け＝連勝は 0 に もどる・同点＝そのまま・対戦の とちゅうで「やめる」＝負け。コンピュータとの 対戦も 友だちとの 対戦も 同じ
//   ・保存：localStorage 'tengel.cb'（{ v, streak（いまの 連勝）, win, lose, draw, owe（まだ わたして いない トークン）, bgm・se・fx（設定：null＝決めて いない・true／false）}）
//   第4.178版（まさちゃん 2026/11/16 14:43「テンゲルカードバトルの追加 ①…BGMをつける。(カーボーイの時代っぽい雰囲気、ゆったりバイオリンの音と、夜の虫の音で作成して)
//     ②カードバトル５ターン勝負にする 手札7枚にして！ ③プレイボードの右下の設定ボタンを押すと、BGMオンかオフと効果エフェクトオンかオフを選べるようにして！
//     ④6.の効果は、もう見てるカードしかない場合は、発動しなくして！ ⑤フィールドの雰囲気を夜の月あかりと火のライトに照らされてるイメージにして！(デザインは変えないで、差し込んでる光りの色を変えてみて)」）：
//     ・5ターン・手札 7まい（cb_rules.js）：画面は ターンの 数・手札の 数を 見て かく（勝ちの しるし・「ターン n／5」・配る 動き）
//     ・BGM（cb_bgm.m4a：姫が 計算で 作った 曲＝kisekae/cb_bgm.py）：カードバトルを 開いて いる 間 くり返す。アプリが うしろに 行ったら 止める・もどったら つづきから
//     ・設定の 窓（ボードの 右下の 歯車・メニューの「設定」）：BGM・効果音・エフェクト（光や 動きの 演出）の オン／オフ。決めた 形は おぼえる
//     ・フィールド：ボードの 絵は 差しこむ 光の 色 だけ かえた もの（月＝青白・火＝だいだい：kisekae/cb_art.py の night）。まわりの 色も 夜に・右下の 火の あかりが ゆっくり ゆれる
//   第4.178版（まさちゃん 2026/11/16 15:33「テンゲルカードバトルに追加 1は、手札のフィールドと合わせて3枚を相手見せ、その内、手札の1を1枚捨てることで幻の馬カードと神様馬カードに勝利することができる
//     2は、手札のフィールドと合わせて3枚を相手見せ、その内、手札の2を1枚捨てることで1に勝利することができる」＋ 新しい 1・2 の 絵「3枚公開：逆転勝利」・15:41「A、オープンしてから」）：
//     ・逆転勝利：オープンして 負けた 人が 使える とき（cb_rules.js の phase 'rev'）、めくった 窓に「チャンス！」→ 聞く 窓「○ の 効果を 使う？」（使わない／使う）。
//       使う → 3まいを 見せる 窓 → 手札の 1まいが 捨て札へ →「逆転勝利！」（相手の 画面は「逆転負け…」）。勝ちの しるしは 決まって から つく
//   第4.179版：バトルコイン（まさちゃん 2026/11/16 15:47「お友達と部屋を作る際に、参加ポイントと勝利者獲得ポイントを設定できるようにして！ ※参加ポイントは、同じポイントで参加足りなけれ参加できない、
//     獲得ポイントは、参加ポイントの2倍以上は設定できない。」→ 買える ポイントを 出し合う 形の 心配（日本の 賭博の 決まり・App Store の 審査）を 伝えた → 16:01「1にしよう！」＝カードバトル専用の コイン・
//     16:10「バトルコインは買えない、CPUとの勝負で勝つと1枚貰える、5連勝すると5枚貰える」・16:18（コインの 絵）「購入できない・使用できるのは、カードバトルの着せ替え、カード背面のデザイン、カードのデザイン、のみ
//     (通常ポイントやお金では獲得できない)・お友達との部屋を作成する場合は、バトルコインで参加枚数を指定する・勝者獲得コインは、参加枚数の2倍まで…勝者獲得コインはテンゲルからのプレゼントコイン」）：
//     ・コインは この 端末の 中 だけ（localStorage 'tengel.cb' の coin）。買う しくみは ない・ポイントや お世話トークンとは かえられない・人に わたす しくみも ない
//     ・もらう：コンピュータに 勝つと 1枚・5連勝 ごとに 5枚（COIN）
//     ・部屋：作る 人が「参加コイン」と「勝者の 獲得コイン」（参加コイン 〜 2倍）を 決める → 入る 人は 決まりを 見て「参加する」（足りなければ 入れない）→ 配った とき 2人とも 参加コインを 出す
//       → 勝った 人が 獲得コインを もらう・同点は もどる・とちゅうで やめた 人は もどらない（相手は 獲得コインを もらう）・つながりが 切れた ときは もどる
//     ・コインで 解放する もの（カードバトルの 着せ替え・カード背面・カードの デザイン）→ 第4.182版の デザインカスタム（下）
//   第4.182版：デザインカスタム（まさちゃん 2026/11/16 20:00「バトルコインで購入するカード背面のデザイン送る！ ・背面カスタム1枚 バトルコイン300枚」＋ うらの 絵 7まい・
//     20:09「カードバトルデザインカスタム デザイン一枚解放、バトルコイン300枚 神様馬カードと幻の馬カード500枚」＋ おもての 絵 16まい・20:22「6.71枚づつ追加して！」＋ 6 と 7 の 絵 1まい ずつ ＝ おもて 18種）
//     ・メニューの「デザインカスタム」→「カードの おもて」「カードの うら」。バトルコインで 1つずつ 解放（おもて 300枚・神様馬／幻の馬の おもて 500枚・うら 300枚）→ 解放すると すぐ その デザインに なる
//     ・えらんだ デザインは 自分の 画面で 出る（pic・deckPic）：おもて＝その カード ぜんぶ（手札・相手の 見えた カード・めくった とき・捨て札・あそび方）／うら＝山札・相手の 手札・ふせた カード・めくる 前。
//       部屋では それぞれの iPhone が 自分で えらんだ デザインで 見て いた（第4.183版から：友だちの カードは 友だちの デザイン＝下）。いつもの デザインは はじめから 使える。デザインの 名前は 姫が つけた
//     ・コインを 使う ことは「解放」と 呼ぶ（お金で 買う ものでは ない）。解放を もどして コインを 返す しくみは ない。保存は localStorage 'tengel.cb' の backs・faces（解放した もの）・back・face（えらんだ もの）
//     ・テスト版だけ：デザインカスタムの いちばん 下に テスト版の 道具（cb_test.js：コインを ふやす・解放を もとに もどす）
//     ・ボードの カードの 種類は 絵の 名前では なく data-ck で 読む（kIn：べつの デザインの 絵の 名前でも まちがえない）
//   第4.183版（まさちゃん 2026/11/16 20:51「TENGERカードバトルミッション追加 1ヶ月に一回リセットされる CPUに連続勝利 3連勝達成30枚 5連勝達成で60枚 6連勝達成で90枚 7連勝達成で120枚
//     8連勝達成で150枚 9連勝達成で200枚 10連勝達成で300枚 お友達バトルで連続勝利 3連勝20枚 5連勝40枚 6連勝60枚 7連勝80枚 8連勝100枚 9連勝120枚 10連勝140枚」・
//     20:53「①相手の背面デザインは、CPUと戦う時は、カスタムしているデザインにして！ ②お友達バトルの時は、それぞれがカスタムしている背面デザイン、カードデザインにして！」）：
//     ・ミッション（MS）：コンピュータに 連続勝利・友だちバトルで 連続勝利。連勝が 3・5・6・7・8・9・10 に なった とき、その場で バトルコインを わたす（受け取りは いらない）
//       毎月 1日（この 端末の 時計の 月が かわった とき）に リセット（達成も 連勝も 0）。連勝は コンピュータと 友だちで 別に 数える（いつもの 連勝〈お世話トークン〉とも 別）
//       負け・とちゅうで やめる・対戦の とちゅうで アプリが 閉じられた（つぎに 開いた とき）＝ その 連勝は 0／同点 ＝ そのまま／友だちが 部屋を 出た・つながりが 切れた ＝ 数えない
//       保存：st.ms＝{ m：月（'YYYY-MM'）, cpu・fr：いまの 連勝, got：{ cpu・fr：達成した 連勝の 数 }, live：対戦 ちゅうの 種類（配った とき つけて、終わったら 消す）}
//       画面：メニューの「ミッション」（今月 ○／14 達成）→ ミッションの 画面（コンピュータ／友だちバトル の タブ）。達成した ときは さいごの 画面に「🎯 ミッション達成！」の 1行
//     ・デザイン：コンピュータとの 対戦は 相手の カード（うら・おもて）も 自分の デザイン（①）／友だちとの 対戦は、自分の カード＝自分の デザイン・友だちの カード＝友だちの デザイン（②）。
//       部屋の あいさつで おたがいの えらんだ デザインを 送る（cb_net.js の dz → match.opDz）。山札は 自分の うら。pic(k, big, side)：side＝'op' は 相手の カード
//     ・ルール（まさちゃん 21:24「4で交換したあとに5を相手がフィールドにセットした場合、五の効果を使える」）：4 の 効果で 交換して 5 を 出したら「5 の 効果を 使う？」（pend 'u5'）→
//       使う：いっしょに 捨てる 手札を えらぶ（mode 'u5'）→ 手 { t:'u5', drop } ／ 使わない：{ t:'u5', drop:null }。相手の 画面は「交換して いるよ…」の まま（cb_rules.js が かくす）
const CBApp = (() => {
  'use strict';
  const R = CBRules, SK = 'tengel.cb';
  const REWARD = { win: 1, every: 5, bonus: 3 };
  const COIN = { win: 1, every: 5, bonus: 5, max: 9999 };      // バトルコイン（第4.179版）：コンピュータに 勝つと 1枚・5連勝 ごとに 5枚・持てる 数
  const coinFor = streak => (streak > 0 && streak % COIN.every === 0 ? COIN.bonus : COIN.win);
  // ミッション（第4.183版・まさちゃん 20:51）：[連勝, バトルコイン]。毎月 1日に リセット（達成も 連勝も 0）
  const MS = { cpu: [[3, 30], [5, 60], [6, 90], [7, 120], [8, 150], [9, 200], [10, 300]], fr: [[3, 20], [5, 40], [6, 60], [7, 80], [8, 100], [9, 120], [10, 140]] };
  const MS_WHO = { cpu: 'コンピュータ', fr: '友だちバトル' }, MS_ALL = MS.cpu.length + MS.fr.length;
  const nowD = () => (typeof CBApp._now === 'function' ? CBApp._now() : new Date());      // いまの 日時（CBApp._now：テスト 用に 日づけを かえる）
  const monthKey = d => { const x = d || nowD(); return x.getFullYear() + '-' + String(x.getMonth() + 1).padStart(2, '0'); };
  const COINI = '<img class="cbci" src="cb_coin.webp" alt="">';      // 字の 中に 入れる コインの しるし
  const STAKE_CHIPS = [0, 1, 2, 3, 5, 10, 20, 30, 50, 100];      // 部屋の 参加コインで えらべる 数（持って いる 数 まで）
  const NAMES = { k: '神様馬', m: '幻の馬' };
  const nameOf = k => NAMES[k] || String(k);
  // デザインカスタム（第4.182版）：バトルコインで 解放する べつの デザイン（名前は 姫が つけた）。絵は kisekae/cb_art.py の FACES・BACKS（cb_fc_<id>_c／_s.webp・cb_bk_<id>_c／_s／_d.webp）
  const FACE_COST = 300, TOP_COST = 500, BACK_COST = 300;      // おもて 1つ 300枚・神様馬／幻の馬の おもて 500枚・うら 1つ 300枚（まさちゃん 20:00・20:09）
  const FACES = [['k', 'ka', '朱の鳥居'], ['k', 'kb', '天空の神殿'], ['m', 'ma', '三日月の幻'], ['m', 'mb', '紅い雷'], ['1', '1a', '炎の輪'], ['1', '1b', '赤銅の鎧'], ['2', '2a', '月夜の黒馬'], ['2', '2b', '銀の鎧'],
    ['3', '3a', '水晶の間'], ['3', '3b', '星の遺跡'], ['4', '4a', '雷の城'], ['4', '4b', '青の広間'], ['5', '5a', '炎の城'], ['5', '5b', '琥珀の洞窟'], ['6', '6a', '赤の書庫'], ['6', '6b', '紅玉の天文台'], ['7', '7a', '緑の森'], ['7', '7b', '天空の都']]
    .map(([k, id, name]) => ({ k: k, id: id, name: name, c: `cb_fc_${id}_c.webp`, s: `cb_fc_${id}_s.webp`, cost: k === 'k' || k === 'm' ? TOP_COST : FACE_COST }));
  const BACKS = [['sky', '天馬の光'], ['star', '星座の馬'], ['ice', '氷の結晶'], ['wa', '和の墨絵'], ['ori', '折り紙の馬'], ['crown', '王冠の紋章'], ['heart', 'ハートの2頭']]
    .map(([id, name]) => ({ k: null, id: id, name: name, c: `cb_bk_${id}_c.webp`, s: `cb_bk_${id}_s.webp`, d: `cb_bk_${id}_d.webp`, cost: BACK_COST }));
  const DZ_KINDS = ['k', 'm', '1', '2', '3', '4', '5', '6', '7'];
  // えらんだ デザイン：side＝'op' は 相手の カード。友だちとの 対戦では 友だちが えらんだ デザイン（部屋の あいさつで 届いた match.opDz・ない 名前は いつもの：第4.183版）。
  //   コンピュータとの 対戦は 相手の カードも 自分の デザイン（第4.183版 ①）
  const selOf = side => { const o = side === 'op' && match && match.kind !== 'cpu' ? match.opDz || { b: '', f: {} } : null; return o ? { back: o.b || '', face: o.f || {} } : { back: st ? st.back : '', face: st ? st.face : {} }; };
  const backNow = side => { const id = selOf(side).back; return id ? BACKS.find(b => b.id === id) || null : null; };
  const faceNow = (k, side) => { const id = selOf(side).face[k]; return id ? FACES.find(f => f.id === id && f.k === k) || null : null; };
  // カードの 絵：k＝種類（null＝うら）・big＝大きい 絵・side＝だれの カード（'my'〈なし〉／'op'）。えらんだ デザインが あれば その 絵（第4.182版・第4.183版）
  const pic = (k, big, side) => { const d = k == null ? backNow(side) : faceNow(k, side); return d ? d[big ? 'c' : 's'] : 'cb_' + (big ? 'c' : 's') + (k == null ? 'b' : k) + '.webp'; };
  const deckPic = () => { const b = backNow(); return b ? b.d : 'cb_deck.webp'; };      // 山札の 絵（自分が えらんだ うら：友だちとの 対戦でも 自分の 画面の 山札は 自分の うら）
  const power = R.power;
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  let SPEED = 1;                                       // 動きの 速さ（テストでは 小さく する）
  // 待つ 時間：ふだんは setTimeout。光の 点めつを 数える テスト（test_cb_flash.py）では 手で 進める 時計（_t.manual・_t.tick：1/60秒 ずつ 進めて 1コマ ずつ 写す）
  const clk = { manual: false, now: 0, q: [] };
  function later(fn, ms) { if (!clk.manual) return setTimeout(fn, ms); const o = { at: clk.now + Math.max(0, ms), fn: fn }; clk.q.push(o); return o; }
  function unlater(h) { if (h && typeof h === 'object') { const i = clk.q.indexOf(h); if (i >= 0) clk.q.splice(i, 1); } else clearTimeout(h); }
  function tick(ms) {
    clk.now += ms; let n = 0;
    for (;;) { const due = clk.q.filter(o => o.at <= clk.now).sort((a, b) => a.at - b.at)[0]; if (!due) break; clk.q.splice(clk.q.indexOf(due), 1); due.fn(); n++; }
    return n;
  }
  const T = ms => new Promise(ok => later(ok, Math.max(0, ms * SPEED)));
  const reduce = () => !fxOn() || !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);      // 動きを へらす：OS の「視差効果を減らす」か、ここの 設定の「エフェクト オフ」（第4.178版）

  // ---------- 保存（連勝・勝ち負けの 数）----------
  let st = null;
  const DEF = () => ({ v: 1, streak: 0, win: 0, lose: 0, draw: 0, owe: 0, bgm: null, se: null, fx: null, coin: 0, stake: null, backs: [], faces: [], back: '', face: {}, ms: null });
  let lostStake = 0;                                   // 前の 対戦が とちゅうで 終わって、もどらなかった 参加コイン（メニューで 1回 知らせる）
  let lostMs = '';                                     // 第4.183版：前の 対戦が とちゅうで 終わって 0 に もどった ミッションの 連勝の 種類（メニューで 1回 知らせる）
  function load() {
    try { const s = JSON.parse(localStorage.getItem(SK) || 'null'); st = Object.assign(DEF(), s && s.v === 1 ? s : {}); } catch (e) { st = DEF(); }
    ['streak', 'win', 'lose', 'draw', 'owe'].forEach(k => { st[k] = Math.max(0, Math.floor(+st[k] || 0)); });
    ['bgm', 'se', 'fx'].forEach(k => { st[k] = st[k] === true || st[k] === false ? st[k] : null; });      // 設定（第4.178版）：null＝まだ 決めて いない
    st.coin = Math.max(0, Math.min(COIN.max, Math.floor(+st.coin || 0)));      // バトルコイン（第4.179版）
    // ミッション（第4.183版）：月・いまの 連勝・達成した 数・対戦 ちゅうの しるし。おかしな 中身は なおす
    const m0 = st.ms && typeof st.ms === 'object' ? st.ms : {}, g0 = m0.got && typeof m0.got === 'object' ? m0.got : {};
    const gotOf = kd => (Array.isArray(g0[kd]) ? g0[kd] : []).map(x => Math.floor(+x)).filter((x, i, a) => MS[kd].some(t => t[0] === x) && a.indexOf(x) === i).sort((a, b) => a - b);
    const cnt = x => Math.max(0, Math.min(9999, Math.floor(+x || 0)));
    st.ms = { m: typeof m0.m === 'string' && /^\d{4}-\d{2}$/.test(m0.m) ? m0.m : monthKey(), cpu: cnt(m0.cpu), fr: cnt(m0.fr), got: { cpu: gotOf('cpu'), fr: gotOf('fr') }, live: m0.live === 'cpu' || m0.live === 'fr' ? m0.live : '' };
    if (st.ms.live) { if (st.ms[st.ms.live] > 0) lostMs = st.ms.live; st.ms[st.ms.live] = 0; st.ms.live = ''; save(); }      // 対戦の とちゅうで アプリが 閉じられて いた：その 連勝は 0（とちゅうで やめた のと 同じ）
    msRoll();
    // デザインカスタム（第4.182版）：解放した もの（backs・faces）・えらんだ もの（back・face）。ない 名前・解放して いない ものは すてる
    const bids = BACKS.map(b => b.id), fids = FACES.map(f => f.id);
    st.backs = Array.isArray(st.backs) ? st.backs.filter((x, i, a) => bids.indexOf(x) >= 0 && a.indexOf(x) === i) : [];
    st.faces = Array.isArray(st.faces) ? st.faces.filter((x, i, a) => fids.indexOf(x) >= 0 && a.indexOf(x) === i) : [];
    st.back = st.backs.indexOf(st.back) >= 0 ? st.back : '';
    const fc = {}, f0 = st.face && typeof st.face === 'object' ? st.face : {};
    DZ_KINDS.forEach(k => { const id = f0[k]; if (st.faces.indexOf(id) >= 0 && FACES.some(f => f.id === id && f.k === k)) fc[k] = id; });
    st.face = fc;
    // 参加コインを 出した まま 終わって いた（対戦の とちゅうで アプリが 閉じられた など）：その コインは もどらない（とちゅうで やめた のと 同じ）
    const k = st.stake; st.stake = null;
    if (k && typeof k === 'object' && Math.floor(+k.e) > 0) { lostStake = Math.floor(+k.e); save(); }
  }
  const addCoin = n => { st.coin = Math.max(0, Math.min(COIN.max, st.coin + Math.floor(+n || 0))); };
  function save() { try { localStorage.setItem(SK, JSON.stringify(st)); } catch (e) { /* なし */ } }
  // ミッション（第4.183版）：月が かわったら リセット（達成も 連勝も 0）。リセットしたら true
  function msRoll() {
    const k = monthKey(); if (st.ms.m === k) return false;
    st.ms = { m: k, cpu: 0, fr: 0, got: { cpu: [], fr: [] }, live: st.ms.live }; save(); return true;
  }
  // 勝った：その 種類の 連勝 ＋1 → 新しく 達成した ミッション [{ k, n, c }]（コインは よぶ 方で まとめて わたす）
  function msWin(kind) {
    msRoll(); const s = st.ms, out = []; s[kind] = Math.min(9999, s[kind] + 1);
    MS[kind].forEach(t => { if (s[kind] >= t[0] && s.got[kind].indexOf(t[0]) < 0) { s.got[kind].push(t[0]); out.push({ k: kind, n: t[0], c: t[1] }); } });
    return out;
  }
  const msKind = m => (m && m.kind === 'cpu' ? 'cpu' : 'fr');      // 対戦の 種類 → ミッションの 種類（コンピュータ／友だちバトル）
  const msDone = () => st.ms.got.cpu.length + st.ms.got.fr.length;
  const rewardFor = streak => (streak > 0 && streak % REWARD.every === 0 ? REWARD.bonus : REWARD.win);
  // まだ わたして いない ごほうびを わたす → { want, add, stock, max }（わたす ものが ない・読みこめない ときは null）
  async function pay() {
    if (!(st.owe > 0) || typeof window.TCGift !== 'function') return null;
    const want = st.owe; let r = null;
    try { r = await window.TCGift(want); } catch (e) { r = null; }
    if (!r) return null;                               // 読みこめなかった：つぎに 開いた とき
    st.owe = 0; save();                                // 持てる 数（25こ）を こえる ぶんは なくなる
    return { want: want, add: r.add, stock: r.stock, max: r.max };
  }
  // 対戦が 終わった：数える → ごほうび（お世話トークン）
  //   第4.179版：バトルコイン ＝ コンピュータに 勝つと 1枚・5連勝 ごとに 5枚（coin）／部屋の 参加コイン（pot）：勝ち＝勝者の 獲得コイン・同点＝参加コインが もどる・負け＝もどらない
  //   第4.183版：ミッション（ms：この 対戦で 達成した ミッション・msc：その コイン）。勝ち＝連勝 ＋1・負け＝0・同点＝そのまま
  async function settle(res) {
    let got = 0, coin = 0, pot = null, ms = []; const cpu = !!match && match.kind === 'cpu', k = st.stake, mk = msKind(match);
    st.ms.live = '';
    if (res === 'win') { st.win += 1; st.streak += 1; got = rewardFor(st.streak); st.owe += got; if (cpu) coin = coinFor(st.streak); ms = msWin(mk); }
    else if (res === 'lose') { st.lose += 1; st.streak = 0; msRoll(); st.ms[mk] = 0; }
    else { st.draw += 1; msRoll(); }
    if (k) { pot = { e: k.e, w: k.w, add: res === 'win' ? k.w : res === 'draw' ? k.e : 0 }; st.stake = null; }
    const msc = ms.reduce((a, x) => a + x.c, 0), want = coin + (pot ? pot.add : 0) + msc, c0 = st.coin; addCoin(want);
    save();
    const p = got ? await pay() : null;
    return { res: res, got: got, pay: p, streak: st.streak, coin: coin, pot: pot, coins: st.coin, full: st.coin - c0 < want, ms: ms, msc: msc, mk: mk, mst: st.ms[mk] };
  }
  // 配った：対戦 ちゅうの しるし（とちゅうで アプリが 閉じられたら、つぎに 開いた とき その 連勝を 0 に：第4.183版）
  function msLive() { if (!match) return; msRoll(); st.ms.live = msKind(match); save(); }
  // 参加コインを 出す（配った とき：2人とも 自分の 端末で）。出した 数は 対戦が 終わる まで おぼえて おく（st.stake）
  function payStake() {
    const k = match && match.stake; st.stake = null;
    if (k && k.e > 0) { st.coin = Math.max(0, st.coin - k.e); st.stake = { e: k.e, w: k.w }; }
    save();
  }

  // ---------- 音 ----------
  //   第4.178版：カードバトルの 中の 設定（ボードの 歯車）で BGM・効果音を オン／オフ できる。決めて いない 間は アプリの「効果音」の 設定と 同じ（前の 版の 動き）：
  //     ・効果音（seOn）：決めて いなければ アプリの 設定（TengelFx.get().sound）
  //     ・BGM（bgmOn）：決めて いなければ「アプリの 効果音が オン」かつ「消音スイッチ（マナーモード）に 合わせられる iOS」（navigator.audioSession が ある：16.4 から）の とき だけ 鳴らす
  //       ＝古い iOS では、設定で オンに した とき だけ（消音スイッチでも 音が 出て しまう ため）。音の 出し方は アプリの ほかの 音と 同じ きまり（ambient：消音スイッチなら 鳴らない・ほかの アプリの 音楽は 止めない＝TengelFx.prime）
  //     ・音の 出口（AudioContext）は カードバトルの 中に 1つ（アプリの 効果音が オフでも、ここの 設定で オンに すれば 鳴る）。閉じたら 休ませる
  const SE = ['deal', 'set', 'flip', 'win', 'lose', 'even', 'magic', 'tap', 'fanfare', 'over', 'join'];
  const snd = { ac: null, buf: {} };
  const AS = (() => { try { return !!(navigator.audioSession && 'type' in navigator.audioSession); } catch (e) { return false; } })();
  const appSound = () => { try { const g = window.TengelFx && window.TengelFx.get ? window.TengelFx.get() : null; return g ? g.sound !== false : true; } catch (e) { return true; } };
  const seOn = () => (st && st.se != null ? st.se : appSound());
  const bgmOn = () => (st && st.bgm != null ? st.bgm : appSound() && (AS || !!CBApp._as));
  const fxOn = () => !(st && st.fx === false);
  function actx() {
    if (!snd.ac) { const C = window.AudioContext || window.webkitAudioContext; if (C) { try { snd.ac = new C(); } catch (e) { snd.ac = null; } } }
    const c = snd.ac;
    if (c && c.state !== 'running' && c.resume) { try { const q = c.resume(); if (q && q.catch) q.catch(() => { }); } catch (e) { /* なし */ } }
    return c;
  }
  function se(name, gain) {
    if (!seOn()) return;
    const c = actx(); if (!c || SE.indexOf(name) < 0) return;
    const f = 'cb_se_' + name + '.m4a';
    if (!snd.buf[name]) snd.buf[name] = fetch(f).then(r => (r.ok ? r.arrayBuffer() : null)).then(b => (b ? new Promise(ok => { try { const q = c.decodeAudioData(b, ok, () => ok(null)); if (q && q.catch) q.catch(() => ok(null)); } catch (e) { ok(null); } }) : null)).catch(() => null);
    snd.buf[name].then(b => { if (!b || !seOn()) return; try { const s = c.createBufferSource(), g = c.createGain(); s.buffer = b; g.gain.value = gain == null ? 1 : gain; s.connect(g); g.connect(c.destination); s.start(0); } catch (e) { /* なし */ } });
  }
  // BGM（第4.178版・まさちゃん「テンゲルカードバトルにBGMをつける。(カーボーイの時代っぽい雰囲気、ゆったりバイオリンの音と、夜の虫の音で作成して)」）：
  //   第4.179版（まさちゃん 17:00「BGMにバイオリン消して、木がきしむ音、足跡を追加して！ 酒場っぽく後ろが、声とかでガヤガヤしてる感じも表現できたら入れてほしい！」）：
  //   cb_bgm.m4a＝姫が 計算で 作った 夜の 酒場の 前の 音（kisekae/cb_bgm.py：木の 床の 足音〈ブーツ＋拍車〉・木の きしみ〈床板・ゆりいす・スイングドア〉・中の グラスの チン・夜の 虫の 声。
  //   録音・よその 曲は 使って いない。第4.178版の バイオリンの 曲は 消した。話し声の ガヤガヤも 作ったが、まさちゃん 17:11「人の声ガヤガヤだけ消してみて！」で 消した）。第4.180版（まさちゃん 17:45「カードバトルのBGM、全体的に音が尖ってるから丸みをつけて！ きしむ音は、もう少し少なくていいよ！ 扉の音ももう少し短く！」）：足音の 高い 音・立ち上がりを やわらかく・きしみ 56回 → 27回・扉 約2.8秒 → 約1.2秒・虫の 声 −3dB。鳴らす 倍は 18:14「少し音小さめで」で 0.42 に（下の BGM.vol）
  //   ファイルは くり返す 1回り（BGM.len 秒）の 前と うしろに 0.5秒ずつ 同じ 音の つづきが 入って いる → まん中の 1回り だけを くり返す（つなぎ目で 音が とばない：トレーニングセンターの BGM と 同じ 形）。
  //   ・鳴らす 間：カードバトルを 開いて いる 間（メニュー・部屋・対戦・あそび方）。アプリが うしろに 行ったら 止める → もどったら つづきから（曲の 頭に もどらない）
  //   ・ほどいた 音は 大きい（約30MB）ので、カードバトルを 閉じたら 手ばなす（次に 開いた ときに ほどき直す）。ファイルが ない（絵と 音の ない ビルド）ときは 何も 鳴らさない
  const BGM = { file: 'cb_bgm.m4a', pre: 0.5, len: 34 * 3 * 60 / 76, vol: 0.42, fin: 1.4, fout: 0.45 };      // len＝約80.5秒（34 * 3 * 60 / 76：第4.178版の 曲と 同じ 長さ）：kisekae/cb_bgm.py の LOOP と 同じ。vol＝ファイルの 音を この 倍で（第4.179版：夜の 酒場の 前の 音は 曲より しずかな ので 0.32 → 0.55。第4.180版：まさちゃん 18:14「少し音小さめでカードバトルのBGMに入れて！」で 0.55 → 0.42〈−2.3dB〉：虫の 声 約−43dB・足音の 山 約−18.5dB：効果音より ひかえめ）
  const bg = { raw: null, buf: null, dec: null, cur: null, tau: 0, gone: false, want: false };
  function bgmLoad() {
    if (bg.buf || bg.gone) return Promise.resolve(bg.buf);
    if (bg.dec) return bg.dec;
    const c = actx(); if (!c || typeof fetch !== 'function') return Promise.resolve(null);
    if (!bg.raw) bg.raw = fetch(BGM.file).then(r => (r.ok ? r.arrayBuffer() : null)).catch(() => null);
    bg.dec = bg.raw.then(b => (b ? new Promise(ok => { try { const q = c.decodeAudioData(b.slice(0), ok, () => ok(null)); if (q && q.catch) q.catch(() => ok(null)); } catch (e) { ok(null); } }) : null)).then(b => {
      bg.dec = null;
      if (b && b.duration > BGM.len + BGM.pre) bg.buf = b; else if (!b) { bg.gone = true; bg.raw = null; } else bg.gone = true;
      return bg.buf;
    });
    return bg.dec;
  }
  const bgmPos = () => (bg.cur && snd.ac ? (bg.tau + Math.max(0, snd.ac.currentTime - bg.cur.t0)) % BGM.len : bg.tau);      // 曲の 中の いまの 所（秒）
  function bgmStart() {
    const c = snd.ac; if (!c || bg.cur || !bg.buf) return;
    try {
      const s = c.createBufferSource(), g = c.createGain(), n = c.currentTime;
      s.buffer = bg.buf; s.loop = true; s.loopStart = BGM.pre / 2; s.loopEnd = BGM.pre / 2 + BGM.len;
      let off = BGM.pre + bg.tau; if (off >= BGM.pre / 2 + BGM.len) off -= BGM.len;
      g.gain.setValueAtTime(0, n); g.gain.linearRampToValueAtTime(BGM.vol, n + BGM.fin);
      s.connect(g); g.connect(c.destination); s.start(0, off); bg.cur = { s: s, g: g, t0: n };
    } catch (e) { bg.cur = null; }
  }
  function bgmStop(fade) {
    if (!bg.cur || !snd.ac) return;
    const o = bg.cur, n = snd.ac.currentTime; bg.tau = bgmPos(); bg.cur = null;
    try { o.g.gain.cancelScheduledValues(n); o.g.gain.setValueAtTime(o.g.gain.value, n); o.g.gain.linearRampToValueAtTime(0, n + fade); o.s.stop(n + fade + 0.05); }
    catch (e) { try { o.s.stop(); } catch (e2) { /* もう 止まって いる */ } }
    setTimeout(() => { try { o.s.disconnect(); o.g.disconnect(); } catch (e) { /* なし */ } }, (fade + 0.3) * 1000);
  }
  // 鳴らす・止めるを、いまの ようす（設定・カードバトルが 開いて いるか・アプリが うしろか）に 合わせる
  function bgmSync() {
    const want = !!ov && ov.classList.contains('on') && !document.hidden && bgmOn();
    bg.want = want;
    if (!want) { bgmStop(BGM.fout); return; }
    if (bg.cur) return;
    if (!actx()) return;
    bgmLoad().then(b => { if (b && bg.want && !bg.cur) bgmStart(); });
  }
  // カードバトルを 閉じた：BGM を 止めて、ほどいた 音を 手ばなす・音の 出口を 休ませる（電池）
  function soundRest() {
    bgmSync();
    setTimeout(() => {
      if (ov && ov.classList.contains('on')) return;
      bg.buf = null; bg.gone = false;
      try { if (snd.ac && snd.ac.state === 'running') { const q = snd.ac.suspend(); if (q && q.catch) q.catch(() => { }); } } catch (e) { /* なし */ }
    }, (BGM.fout + 0.4) * 1000);
  }

  // ---------- 画面 ----------
  const css = `
#cbOv{position:fixed;inset:0;z-index:90;display:none;color:#f6ead2;font-family:"BIZ UDPGothic","Hiragino Sans",sans-serif;-webkit-user-select:none;user-select:none;-webkit-touch-callout:none;-webkit-tap-highlight-color:transparent;overflow:hidden;touch-action:manipulation}
#cbOv.on{display:block}
#cbOv button{font-family:inherit;-webkit-tap-highlight-color:transparent;color:inherit}
#cbOv img{-webkit-user-drag:none;user-select:none;pointer-events:none}
#cbOv .cbbg{position:absolute;inset:0;overflow:hidden;background:radial-gradient(95% 52% at 4% 4%,rgba(96,128,196,.30) 0%,rgba(52,74,132,.13) 42%,rgba(20,28,56,0) 72%),radial-gradient(120% 62% at 50% 40%,#1c1a22 0%,#100f17 52%,#06060b 100%)}
#cbOv .cbbg::after{content:"";position:absolute;inset:0;background:repeating-linear-gradient(90deg,rgba(0,0,0,0) 0 46px,rgba(0,0,0,.18) 46px 47px,rgba(190,210,255,.025) 47px 48px);opacity:.9}
#cbOv .cbfire{position:absolute;inset:0;pointer-events:none;background:radial-gradient(88% 46% at 100% 76%,rgba(255,138,44,.34) 0%,rgba(214,84,18,.15) 40%,rgba(120,40,8,0) 72%);will-change:opacity;animation:cbfire 5.6s ease-in-out infinite}
#cbOv .cbboard .cbfire{background:radial-gradient(62% 88% at 100% 82%,rgba(255,150,56,.26) 0%,rgba(226,96,24,.10) 45%,rgba(140,50,10,0) 74%);animation-duration:4.3s;animation-delay:-1.7s}
@keyframes cbfire{0%{opacity:.78}17%{opacity:.92}29%{opacity:.82}46%{opacity:1}61%{opacity:.84}78%{opacity:.95}100%{opacity:.78}}
#cbOv.nofx .cbfire{animation:none;opacity:.88}
#cbOv .cbs{position:absolute;inset:0;display:none;flex-direction:column;box-sizing:border-box;padding:var(--sat,env(safe-area-inset-top)) 0 var(--sab,env(safe-area-inset-bottom));max-width:480px;margin:0 auto}
#cbOv .cbs.on{display:flex}
#cbOv .gold{font-family:"Dela Gothic One","Hiragino Sans",sans-serif;font-weight:400;background:linear-gradient(180deg,#fff3c4 0%,#ffd76a 38%,#e2a83e 62%,#9c6410 100%);-webkit-background-clip:text;background-clip:text;color:transparent;-webkit-text-fill-color:transparent;filter:drop-shadow(0 2px 2px rgba(0,0,0,.6))}
#cbOv .cbb{display:block;box-sizing:border-box;min-height:48px;border-radius:24px;border:1.5px solid #f7d27c;background:linear-gradient(180deg,#ffe9a8,#e2a83e);color:#3a2206;font-weight:700;font-size:16px;line-height:1.25;padding:8px 18px;box-shadow:0 3px 0 #7a4c0c,0 6px 12px rgba(0,0,0,.4)}
#cbOv .cbb:active{transform:translateY(2px);box-shadow:0 1px 0 #7a4c0c,0 3px 6px rgba(0,0,0,.4)}
#cbOv .cbb.dk{background:linear-gradient(180deg,#3a2616,#22150b);color:#ffe7b0;border-color:#c9a35a;box-shadow:0 3px 0 #0d0703,0 6px 12px rgba(0,0,0,.4)}
#cbOv .cbb.sm{min-height:38px;border-radius:19px;font-size:13.5px;padding:5px 14px;box-shadow:0 2px 0 #7a4c0c,0 4px 8px rgba(0,0,0,.35)}
#cbOv .cbb.dk.sm{box-shadow:0 2px 0 #0d0703,0 4px 8px rgba(0,0,0,.35)}
#cbOv .cbb:disabled{opacity:.45}
#cbOv .cbb small{display:block;font-weight:400;font-size:11.5px;opacity:.85}

#cbOv .cbmenu{align-items:center;justify-content:center;gap:10px;padding-left:22px;padding-right:22px;text-align:center}
#cbOv .cbmenu .lg{width:min(58vw,230px);height:auto;aspect-ratio:1;filter:drop-shadow(0 8px 14px rgba(0,0,0,.55))}
#cbOv .cbmenu h1{margin:0;font-size:30px;line-height:1.15;letter-spacing:.04em}
#cbOv .cbmenu h1 small{display:block;font-size:13px;letter-spacing:.3em;margin-bottom:2px}
#cbOv .cbmenu .rec{font-size:12.5px;color:#d9c08c;line-height:1.6;margin:0 0 4px}
#cbOv .cbmenu .rec b{color:#ffe2a0}
#cbOv .cbmenu .btns{display:flex;flex-direction:column;gap:10px;width:100%;max-width:300px}
#cbOv .cbmenu .row{display:flex;gap:10px}#cbOv .cbmenu .row .cbb{flex:1 1 0;padding-left:6px;padding-right:6px}
#cbOv .cbx{position:absolute;left:12px;top:calc(var(--sat,env(safe-area-inset-top)) + 8px);z-index:2}

#cbOv .cbroom{align-items:center;justify-content:center;gap:12px;padding-left:22px;padding-right:22px;text-align:center}
#cbOv .cbroom h2{margin:0;font-size:22px}
#cbOv .cbroom p{margin:0;font-size:13.5px;line-height:1.7;color:#e6d3a6}
#cbOv .cbroom .num{font-family:"Dela Gothic One","Hiragino Sans",sans-serif;font-size:56px;letter-spacing:.14em;line-height:1.1;color:#ffe9a8;text-shadow:0 3px 0 #7a4c0c,0 6px 14px rgba(0,0,0,.6);padding-left:.14em}
#cbOv .cbroom .num.in{display:flex;justify-content:center;gap:10px;letter-spacing:0;padding-left:0}
#cbOv .cbroom .num.in span{display:block;width:52px;height:68px;line-height:68px;border-radius:12px;background:rgba(0,0,0,.35);border:1.5px solid rgba(255,226,160,.4);box-sizing:border-box}
#cbOv .cbroom .num.in span.cur{border-color:#ffd27a;box-shadow:0 0 10px rgba(255,210,90,.5)}
#cbOv .cbroom .stt{min-height:24px;font-weight:700;color:#ffe2a0;font-size:14.5px}
#cbOv .cbroom .hint{font-size:12px;color:#bfa873;line-height:1.65;max-width:320px}
#cbOv .cbkeys{display:grid;grid-template-columns:repeat(3,64px);gap:8px;justify-content:center}
#cbOv .cbkeys button{height:50px;border-radius:14px;border:1.5px solid #c9a35a;background:linear-gradient(180deg,#3a2616,#22150b);color:#ffe9a8;font-size:22px;font-weight:700}
#cbOv .cbkeys button:active{background:#5a3b1c}
#cbOv .cbkeys button[data-key=go]{font-size:17px}
#cbOv .cbkeys button[data-key=go]:not(:disabled){background:linear-gradient(180deg,#ffe9a8,#e2a83e);color:#3a2206;border-color:#f7d27c}
#cbOv .cbkeys button:disabled{opacity:.4}
#cbOv .cbspin{display:inline-block;width:18px;height:18px;border-radius:50%;border:3px solid rgba(255,226,160,.25);border-top-color:#ffd27a;animation:cbsp .9s linear infinite;vertical-align:-3px;margin-right:6px}
@keyframes cbsp{to{transform:rotate(360deg)}}

#cbOv .cbmidw{flex:1 1 auto;min-height:0;display:flex;flex-direction:column}
#cbOv .cbtop{flex:none;height:44px;display:flex;align-items:center;gap:8px;padding:0 10px}
#cbOv .cbtop .cbturn{flex:1 1 auto;text-align:center;font-family:"Dela Gothic One","Hiragino Sans",sans-serif;font-size:17px;letter-spacing:.08em;color:#ffe9a8;text-shadow:0 2px 0 rgba(0,0,0,.6)}
#cbOv .cbtop .cbturn small{font-family:"BIZ UDPGothic","Hiragino Sans",sans-serif;font-size:11px;letter-spacing:0;color:#d9c08c;margin-left:6px}
#cbOv .cbwho{display:flex;align-items:center;justify-content:center;gap:8px;height:22px;font-size:12.5px;color:#e6d3a6}
#cbOv .cbwho b{color:#ffe9a8;font-size:13px}
#cbOv .cbpips{display:inline-flex;gap:4px}
#cbOv .cbpips i{width:13px;height:13px;border-radius:50%;box-sizing:border-box;border:1.5px solid #c9a35a;background:rgba(0,0,0,.35)}
#cbOv .cbpips i.on{background:radial-gradient(circle at 35% 30%,#fff6cf,#ffd24d 45%,#b97a10);border-color:#ffe9a8;box-shadow:0 0 6px rgba(255,210,90,.75)}
#cbOv .cbopp{flex:0 1 118px;min-height:62px;display:flex;flex-direction:column;justify-content:flex-end;padding-bottom:2px}
#cbOv .cbohand{flex:1 1 auto;min-height:0;display:flex;align-items:flex-end;justify-content:center;padding:0 8px}
#cbOv .cbohand .cbc{width:var(--ow,40px);margin-left:calc(var(--ow,40px) * -.28)}
#cbOv .cbohand .cbc:first-child{margin-left:0}
#cbOv .cbc{position:relative;flex:none;display:block;aspect-ratio:2/3;border:0;padding:0;margin:0;background:none;border-radius:6.5% / 4.3%;filter:drop-shadow(0 2px 3px rgba(0,0,0,.5))}
#cbOv .cbc img{display:block;width:100%;height:100%}
#cbOv .cbc .eye{position:absolute;right:-3px;top:-5px;width:20px;height:20px;border-radius:50%;background:#1b1209;border:1.5px solid #ffd27a;box-shadow:0 1px 3px rgba(0,0,0,.6)}
#cbOv .cbc .eye::before{content:"";position:absolute;left:3px;right:3px;top:6px;height:5px;border-radius:50%;border:1.5px solid #ffd27a}
#cbOv .cbc .eye::after{content:"";position:absolute;left:7px;top:7.5px;width:3px;height:3px;border-radius:50%;background:#ffd27a}
#cbOv .cbhand .cbc .eye{right:auto;left:calc(60% - 23px)}
#cbOv .cbboard{position:relative;flex:none;width:100%;margin-top:auto;aspect-ratio:1672/941;-webkit-mask-image:linear-gradient(180deg,transparent 0,#000 7%,#000 93%,transparent 100%);mask-image:linear-gradient(180deg,transparent 0,#000 7%,#000 93%,transparent 100%)}
#cbOv .cbboard>img{position:absolute;inset:0;width:100%;height:100%;display:block}
#cbOv .cbdeck{position:absolute;left:67.2%;top:25.5%;width:9.8%;aspect-ratio:360/426}
#cbOv .cbdeck img{width:100%;height:100%;display:block;filter:drop-shadow(0 3px 4px rgba(0,0,0,.5))}
#cbOv .cbn{position:absolute;min-width:18px;height:18px;box-sizing:border-box;padding:0 4px;border-radius:9px;background:#1b1209;border:1.5px solid #ffd27a;color:#ffe9a8;font-size:10.5px;font-weight:700;line-height:15px;text-align:center}
#cbOv .cbdeck .cbn{right:-7px;top:-6px}
#cbOv .cbdis{position:absolute;left:23.5%;top:29.5%;width:15.5%;height:43%;border:0;padding:0;background:none}
#cbOv .cbdis .pl{position:absolute;left:19%;top:27%;width:62%;aspect-ratio:2/3;transform:rotate(-7deg);border-radius:6.5% / 4.3%;filter:drop-shadow(0 2px 3px rgba(0,0,0,.55))}
#cbOv .cbdis .pl img{display:block;width:100%;height:100%;border-radius:inherit}
#cbOv .cbdis .cbn{right:0;top:21%}
#cbOv .cbgear{position:absolute;left:80.6%;top:60.2%;width:13.4%;height:19.5%;border:0;padding:0;background:none;border-radius:50%}
#cbOv .cbslot{position:absolute;left:43.5%;width:12.8%;aspect-ratio:2/3}
#cbOv .cbslot.op{top:1.6%}
#cbOv .cbslot.my{top:41.4%}
#cbOv .cbslot .cbc{width:100%}
#cbOv .cbslot .tag{position:absolute;left:50%;bottom:-7px;transform:translateX(-50%);white-space:nowrap;font-size:9px;font-weight:700;line-height:13px;padding:0 5px;border-radius:7px;background:#1b1209;border:1px solid #c9a35a;color:#ffe2a0}
#cbOv .cbglow{position:absolute;left:39.6%;top:41.4%;width:20.8%;height:23%;border-radius:12% / 18%;pointer-events:none;box-shadow:0 0 0 2px rgba(255,226,130,.85),0 0 16px 4px rgba(255,210,90,.55);opacity:0;transition:opacity .3s}
#cbOv .cbglow.on{opacity:1;animation:cbgl 1.8s ease-in-out infinite alternate}
@keyframes cbgl{from{box-shadow:0 0 0 2px rgba(255,226,130,.7),0 0 10px 2px rgba(255,210,90,.35)}to{box-shadow:0 0 0 2px rgba(255,240,180,.95),0 0 18px 5px rgba(255,210,90,.6)}}
#cbOv .cbmsg{flex:none;height:44px;box-sizing:border-box;overflow:hidden;display:flex;align-items:center;justify-content:center;text-align:center;white-space:pre-line;font-size:13.5px;font-weight:700;line-height:1.35;color:#fff1cf;padding:2px 12px;text-shadow:0 1px 2px rgba(0,0,0,.7)}
#cbOv .cbme{flex:none;margin-top:auto}
#cbOv .cbhand{flex:0 1 190px;min-height:104px;display:flex;align-items:center;justify-content:center;padding:14px 6px 4px;box-sizing:border-box}
#cbOv .cbhand .cbc{width:var(--cw,70px);margin-left:var(--ov,4px);transition:transform .16s ease-out}
#cbOv .cbhand .cbc:first-child{margin-left:0}
#cbOv .cbhand .cbc.sel{transform:translateY(-12px);filter:drop-shadow(0 0 8px rgba(255,214,110,.95)) drop-shadow(0 4px 5px rgba(0,0,0,.5))}
#cbOv .cbhand .cbc.off{filter:brightness(.55) drop-shadow(0 2px 3px rgba(0,0,0,.5))}
#cbOv .cbhand .cbc.new{animation:cbin .4s ease-out both}
@keyframes cbin{from{transform:translateY(-30px) scale(.8);opacity:0}to{transform:none;opacity:1}}
#cbOv .cbact{flex:none;height:48px;overflow:hidden;display:flex;align-items:center;justify-content:center;gap:8px;flex-wrap:nowrap;padding:4px 10px 6px;box-sizing:border-box}
#cbOv .cbact .cbb{flex:0 1 auto;white-space:nowrap}

#cbOv .cbfly{position:absolute;inset:0;pointer-events:none;z-index:5}
#cbOv .cbfl{position:absolute;border-radius:6.5% / 4.3%;will-change:transform;filter:drop-shadow(0 4px 6px rgba(0,0,0,.5))}
#cbOv .cbban{position:absolute;left:0;right:0;top:38%;z-index:6;text-align:center;pointer-events:none;opacity:0;transform:scale(.8);transition:opacity .22s,transform .22s}
#cbOv .cbban.on{opacity:1;transform:none}
#cbOv .cbban .bd{padding:6px 0 8px;background:linear-gradient(90deg,rgba(0,0,0,0),rgba(10,6,3,.86) 16%,rgba(10,6,3,.86) 84%,rgba(0,0,0,0))}
#cbOv .cbban b{display:inline-block;font-size:34px;line-height:1.2;letter-spacing:.06em}
#cbOv .cbban small{display:block;font-size:13px;font-weight:700;color:#fff1cf;margin-top:2px;text-shadow:0 1px 3px #000}

#cbOv .cbmod{position:absolute;inset:0;z-index:8;display:none;flex-direction:column;align-items:center;justify-content:center;gap:10px;box-sizing:border-box;padding:calc(var(--sat,env(safe-area-inset-top)) + 10px) 16px calc(var(--sab,env(safe-area-inset-bottom)) + 12px);background:rgba(8,5,2,.8);text-align:center}
#cbOv .cbmod.on{display:flex}
#cbOv .cbmod h3{margin:0;font-size:18px;line-height:1.35}
#cbOv .cbmod p{margin:0;font-size:13.5px;line-height:1.65;color:#f0dfb6;max-width:330px}
#cbOv .cbmod .big{width:min(62vw,calc((100vh - 330px) * .6667),250px);aspect-ratio:2/3;border-radius:6.5% / 4.3%;filter:drop-shadow(0 10px 18px rgba(0,0,0,.6))}
#cbOv .cbmod .big img{width:100%;height:100%;display:block}
#cbOv .cbmod .col{display:flex;flex-direction:column;gap:9px;width:100%;max-width:310px}
#cbOv .cbmod .rowb{display:flex;gap:9px;width:100%;max-width:330px}#cbOv .cbmod .rowb .cbb{flex:1 1 0}
#cbOv .cbmod .pick{display:flex;justify-content:center;gap:8px;flex-wrap:wrap}
#cbOv .cbmod .pick .cbc{width:min(17vw,74px)}
#cbOv .cbmod .pick .cbc.knw{filter:brightness(.5)}
#cbOv .cbmod.cbdm{background:rgba(8,5,2,.95)}
#cbOv .cbmod.cbask{gap:11px;background:rgba(8,5,2,.9)}
#cbOv .cbmod.cbask h3{font-size:22px}
#cbOv .cbmod.cbask .big{width:min(52vw,calc((100vh - 410px) * .6667),220px)}
#cbOv .cbmod .askq{font-size:14px;line-height:1.6;color:#f0dfb6}
#cbOv .cbmod p,#cbOv .cbmsg,#cbOv .cbtoast,#cbOv .cbend .gift,#cbOv .cbhelp .bd{word-break:keep-all;overflow-wrap:anywhere}
#cbOv .cbmod .askq b{display:block;font-size:20px;line-height:1.4;color:#ffe9a8}
#cbOv .cbb.lg{min-height:58px;border-radius:29px;font-size:19px;padding:8px 10px}
#cbOv .cbmod .three{display:flex;justify-content:center;gap:8px}
#cbOv .cbmod .three .cbc{width:min(24vw,104px)}
#cbOv .cbdl{width:100%;max-width:340px;max-height:56vh;overflow:auto;-webkit-overflow-scrolling:touch;box-sizing:border-box;padding:2px 4px 6px}
#cbOv .cbdl h4{margin:12px 0 6px;font-size:14px;line-height:1.3;color:#ffe2a0;text-align:left;border-left:4px solid #e2a83e;padding-left:8px}
#cbOv .cbdl h4:first-child{margin-top:2px}
#cbOv .cbdl .none{font-size:12.5px;color:#bfa873;text-align:left;padding-left:12px}
#cbOv .cbdl .row{display:flex;align-items:center;gap:10px;padding:6px 8px;margin:5px 0;border-radius:12px;background:rgba(255,236,190,.06);border:1px solid rgba(255,226,160,.22)}
#cbOv .cbdl .row>b{flex:none;width:62px;font-size:12.5px;line-height:1.3;color:#ffe9a8;text-align:left}
#cbOv .cbdl .row>b small{display:block;font-size:10.5px;font-weight:400;color:#d9c08c}
#cbOv .cbdl .pr{flex:1 1 0;min-width:0;display:flex;flex-direction:column;align-items:center;gap:4px;font-size:11px;line-height:1.2;color:#e6d3a6}
#cbOv .cbdl .cs{display:flex;justify-content:center;gap:6px}
#cbOv .cbdl .cbc{width:46px}
#cbOv .cbdl .cbc img{pointer-events:none}
#cbOv .cbvs{display:flex;align-items:flex-start;justify-content:center;gap:14px;width:100%}
#cbOv .cbvs .sd{display:flex;flex-direction:column;align-items:center;gap:6px;width:min(40vw,160px);transition:transform .35s ease-out,filter .35s,opacity .35s}
#cbOv .cbvs .sd span{font-size:13px;font-weight:700;color:#ffe2a0}
#cbOv .cbvs .sd.wn{transform:scale(1.06)}
#cbOv .cbvs .sd.ls{transform:scale(.92);filter:brightness(.5)}
#cbOv .cbvs .mid{align-self:center;font-size:22px}
#cbOv .cbflip{width:100%;aspect-ratio:2/3;perspective:700px}
#cbOv .cbflip .in{position:relative;width:100%;height:100%;transform-style:preserve-3d;transition:transform .5s cubic-bezier(.3,.6,.3,1)}
#cbOv .cbflip.up .in{transform:rotateY(180deg)}
#cbOv .cbflip img{position:absolute;inset:0;width:100%;height:100%;display:block;backface-visibility:hidden;-webkit-backface-visibility:hidden;border-radius:6.5% / 4.3%;filter:drop-shadow(0 8px 12px rgba(0,0,0,.55))}
#cbOv .cbflip img.fc{transform:rotateY(180deg)}
#cbOv .cbres{min-height:52px;font-size:38px;line-height:1.15;opacity:0;transform:scale(.6);transition:opacity .25s,transform .3s cubic-bezier(.3,1.5,.5,1)}
#cbOv .cbres.on{opacity:1;transform:none}
#cbOv .cbres small{display:block;font-family:"BIZ UDPGothic","Hiragino Sans",sans-serif;font-size:13.5px;font-weight:700;color:#fff1cf;-webkit-text-fill-color:#fff1cf;letter-spacing:0;margin-top:2px}
#cbOv .cbmod.cbend{background:rgba(8,5,2,.9)}
#cbOv .cbend h3{font-size:40px;line-height:1.15}
#cbOv .cbend .sc{font-family:"Dela Gothic One","Hiragino Sans",sans-serif;font-size:26px;color:#ffe9a8;letter-spacing:.08em}
#cbOv .cbend .sc small{font-family:"BIZ UDPGothic","Hiragino Sans",sans-serif;font-size:12px;color:#d9c08c;letter-spacing:0;display:block}
#cbOv .cbend .gift{min-height:212px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;font-size:14px;line-height:1.6;color:#fff1cf}
#cbOv .cbend .gift b{color:#ffe07a;font-size:17px}
#cbOv .cbget{display:inline-flex;align-items:center;gap:14px;box-sizing:border-box;min-width:250px;padding:11px 24px 12px 18px;border-radius:22px;border:2.5px solid #ffd76a;background:linear-gradient(180deg,#5a3a12 0%,#3a240a 55%,#2a1806 100%);box-shadow:0 0 0 1.5px rgba(60,30,0,.7),0 0 22px rgba(255,210,90,.6),inset 0 1px 0 rgba(255,240,190,.35),inset 0 0 14px rgba(255,200,80,.22);animation:cbget .55s cubic-bezier(.3,1.5,.5,1) both}
#cbOv .cbget .tk{flex:none;font-style:normal;font-size:42px;line-height:1;filter:drop-shadow(0 2px 3px rgba(0,0,0,.55))}
#cbOv .cbget .tx{display:block;text-align:left}
#cbOv .cbget small{display:block;font-size:13.5px;font-weight:700;line-height:1.3;color:#ffe9b0}
#cbOv .cbend .gift .cbget .n{display:block;font-size:31px;line-height:1.15;letter-spacing:.03em}
@keyframes cbget{from{transform:scale(.5);opacity:0}to{transform:none;opacity:1}}
#cbOv .cbtoast{position:absolute;left:50%;top:calc(var(--sat,env(safe-area-inset-top)) + 54px);z-index:9;transform:translate(-50%,-8px);width:max-content;max-width:86%;box-sizing:border-box;padding:9px 16px;border-radius:16px;background:rgba(20,12,6,.94);border:1.5px solid #c9a35a;color:#fff1cf;font-size:13.5px;font-weight:700;line-height:1.5;text-align:center;white-space:pre-line;box-shadow:0 6px 16px rgba(0,0,0,.5);opacity:0;pointer-events:none;transition:opacity .2s,transform .2s}
#cbOv .cbtoast.on{opacity:1;transform:translate(-50%,0)}

#cbOv .cbhelp{padding-left:0;padding-right:0}
#cbOv .cbhelp .hd{flex:none;height:48px;display:flex;align-items:center;gap:8px;padding:0 12px}
#cbOv .cbhelp .hd b{flex:1;text-align:center;font-size:17px;color:#ffe9a8;margin-right:64px}
#cbOv .cbhelp .bd{flex:1 1 auto;min-height:0;overflow:auto;-webkit-overflow-scrolling:touch;padding:4px 18px 26px;font-size:13.5px;line-height:1.75;color:#f0dfb6}
#cbOv .cbhelp h4{margin:16px 0 6px;font-size:15px;color:#ffe2a0;border-left:4px solid #e2a83e;padding-left:8px}
#cbOv .cbhelp ul{margin:0;padding-left:1.2em}#cbOv .cbhelp li{margin:2px 0}
#cbOv .cbhelp .ord{display:flex;align-items:center;justify-content:center;gap:1px;margin:8px -6px}
#cbOv .cbhelp .ord img{flex:0 1 30px;min-width:0;width:30px;height:auto;aspect-ratio:2/3}#cbOv .cbhelp .ord i{flex:none;font-style:normal;color:#c9a35a;font-size:11px}
#cbOv .cbhelp .ef{display:flex;gap:10px;align-items:flex-start;margin:8px 0;padding:8px;border-radius:12px;background:rgba(255,236,190,.06);border:1px solid rgba(255,226,160,.22)}
#cbOv .cbhelp .ef img{flex:none;width:58px;height:87px}
#cbOv .cbhelp .ef b{display:block;color:#ffe9a8;font-size:14px}
#cbOv .cbhelp .ef strong{color:#ffe9a8}
#cbOv .cbmod.cbset{background:rgba(8,5,2,.93)}#cbOv .cbmod.cbset h3{font-size:22px}
#cbOv .cbsws{display:flex;flex-direction:column;gap:8px;width:100%;max-width:320px}
#cbOv .cbsw{display:flex;align-items:center;gap:10px;min-height:54px;box-sizing:border-box;padding:6px 8px 6px 14px;border-radius:16px;background:rgba(255,236,190,.07);border:1px solid rgba(255,226,160,.26);text-align:left}
#cbOv .cbsw>span{flex:1 1 auto;min-width:0;font-size:16px;font-weight:700;color:#ffe9a8;line-height:1.25}
#cbOv .cbsw>span small{display:block;font-size:11.5px;font-weight:400;color:#d9c08c}
#cbOv .cbseg{flex:none;display:flex;border-radius:21px;border:1.5px solid #c9a35a;overflow:hidden;background:#1b1209}
#cbOv .cbseg button{min-width:58px;height:40px;border:0;padding:0 10px;background:none;color:#bfa873;font-size:15px;font-weight:700}
#cbOv .cbseg button.on{background:linear-gradient(180deg,#ffe9a8,#e2a83e);color:#3a2206}
#cbOv .cbmenu .row.two .cbb{min-height:44px}
#cbOv .cbci{display:inline-block;width:1.35em;height:1.35em;vertical-align:-.32em;margin-right:.25em}
#cbOv .cbcoinl{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:0 2px;margin:0;font-size:13.5px;line-height:1.5;color:#f0dfb6}
#cbOv .cbcoinl b{color:#ffe07a;font-size:17px}
#cbOv .cbcoinl small{flex:0 0 100%;font-size:11.5px;color:#d9c08c}
#cbOv .cbturn small.stk{margin-left:10px;color:#ffe07a;font-size:11.5px}
#cbOv .cbstk{display:flex;flex-direction:column;gap:9px;width:100%;max-width:330px}
#cbOv .cbstk .blk{box-sizing:border-box;padding:9px 12px 11px;border-radius:16px;background:rgba(255,236,190,.07);border:1px solid rgba(255,226,160,.26);text-align:left}
#cbOv .cbstk .blk>b{display:block;font-size:15px;color:#ffe9a8}
#cbOv .cbstk .blk>small{display:block;font-size:11.5px;line-height:1.45;color:#d9c08c;margin-bottom:7px}
#cbOv .cbstk .chips{display:flex;flex-wrap:wrap;gap:6px}
#cbOv .cbstk .chips button{min-width:44px;height:40px;box-sizing:border-box;border-radius:20px;border:1.5px solid #c9a35a;background:#1b1209;color:#ffe9a8;font-size:15px;font-weight:700;padding:0 8px}
#cbOv .cbstk .chips button.on{background:linear-gradient(180deg,#ffe9a8,#e2a83e);color:#3a2206;border-color:#f7d27c}
#cbOv .cbstp{display:flex;align-items:center;justify-content:center;gap:14px}
#cbOv .cbstp button{width:48px;height:42px;border-radius:14px;border:1.5px solid #c9a35a;background:linear-gradient(180deg,#3a2616,#22150b);color:#ffe9a8;font-size:20px;font-weight:700;padding:0}
#cbOv .cbstp button:disabled{opacity:.35}
#cbOv .cbstp>b{min-width:74px;text-align:center;font-size:26px;line-height:1;color:#ffe07a}
#cbOv .cbstp>b small{font-size:13px;font-weight:400;color:#d9c08c;margin-left:2px}
#cbOv .cbstkl{margin:0;font-size:14px;color:#f0dfb6}#cbOv .cbstkl b{color:#ffe07a;font-size:16px}
#cbOv .cbmod .cbstkv{font-size:16px;line-height:1.5;color:#f0dfb6}
#cbOv .cbmod .cbstkv b{color:#ffe07a;font-size:21px}#cbOv .cbmod .cbstkv i{font-style:normal;color:#c9a35a;margin:0 8px}
#cbOv .cbmod .cbhave b{color:#ffe07a;font-size:16px}#cbOv .cbmod .cbhave strong{color:#ffb38a}
#cbOv .cbmod.cbjoin{background:rgba(8,5,2,.93)}
#cbOv .cbend .gift .cbcl b{color:#ffe07a;font-size:15.5px}
#cbOv .cbdz{padding-left:0;padding-right:0}
#cbOv .cbdz .hd{flex:none;height:48px;display:flex;align-items:center;gap:8px;padding:0 12px}
#cbOv .cbdz .hd b{flex:1;text-align:center;font-size:17px;color:#ffe9a8;margin-right:64px}
#cbOv .cbdz>.cbcoinl{flex:none;margin:0 0 6px}
#cbOv .cbdz .tabs{flex:none;display:flex;gap:4px;margin:0 14px 4px;padding:3px;border-radius:24px;border:1.5px solid #c9a35a;background:#1b1209}
#cbOv .cbdz .tabs button{flex:1 1 0;height:40px;border:0;border-radius:20px;background:none;color:#bfa873;font-size:15px;font-weight:700;padding:0 6px}
#cbOv .cbdz .tabs button.on{background:linear-gradient(180deg,#ffe9a8,#e2a83e);color:#3a2206}
#cbOv .cbdz .bd{flex:1 1 auto;min-height:0;overflow:auto;-webkit-overflow-scrolling:touch;padding:0 12px 26px}
#cbOv .cbdz h4{display:flex;align-items:baseline;gap:8px;margin:14px 2px 7px;font-size:15px;color:#ffe2a0;border-left:4px solid #e2a83e;padding-left:8px}
#cbOv .cbdz h4 small{font-size:12px;font-weight:400;color:#d9c08c}
#cbOv .cbdz h4 .cbci,#cbOv .dzt .cbci{width:1.25em;height:1.25em;vertical-align:-.3em;margin-right:.12em}
#cbOv .cbdz .tiles{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
#cbOv .cbdz .tiles.b{grid-template-columns:repeat(4,minmax(0,1fr));gap:6px}
#cbOv .dzt{display:flex;flex-direction:column;align-items:center;gap:3px;min-width:0;padding:6px 4px 7px;border-radius:12px;border:1.5px solid rgba(255,226,160,.22);background:rgba(255,236,190,.06);color:#f0dfb6}
#cbOv .dzt>img{width:100%;max-width:100px;height:auto;aspect-ratio:2/3;display:block;filter:drop-shadow(0 3px 5px rgba(0,0,0,.5))}
#cbOv .dzt span{font-size:12px;line-height:1.3;color:#ffe9a8;text-align:center;word-break:keep-all;overflow-wrap:anywhere}
#cbOv .dzt em{font-style:normal;font-size:11.5px;line-height:1.25;color:#d9c08c}
#cbOv .dzt.on{border-color:#f7d27c;background:rgba(255,214,120,.16);box-shadow:0 0 0 1px #f7d27c inset}
#cbOv .dzt.on em{color:#ffe07a;font-weight:700}
#cbOv .dzt.lk>img{filter:brightness(.6) saturate(.75) drop-shadow(0 3px 5px rgba(0,0,0,.5))}
#cbOv .cbdz .dzn{margin:12px 4px 0;font-size:12px;line-height:1.6;color:#d9c08c}
#cbOv .cbmod.cbdzm{background:rgba(8,5,2,.93)}
#cbOv .cbmod.cbdzm h3 small{display:block;font-size:12.5px;font-weight:400;color:#d9c08c;letter-spacing:.04em}
#cbOv .cbmod .big.sm{width:min(36vw,calc((100vh - 420px) * .6667),150px)}
#cbOv .cbmod .cbneed{font-size:12.5px;color:#ffb38a;text-align:center}
#cbOv .cbtst{margin:18px 2px 0;padding:10px 10px 12px;border-radius:14px;border:2px dashed #b98a4a;background:rgba(255,244,214,.08)}
#cbOv .cbtst b{display:block;color:#ffe9a8;font-size:14px}#cbOv .cbtst small{display:block;font-size:11.5px;color:#d9c08c;margin:2px 0 8px}
#cbOv .cbtst .r{display:flex;flex-wrap:wrap;gap:6px}
#cbOv .cbmenu .row.two .cbb .msn{white-space:nowrap}
#cbOv .cbms{padding-left:0;padding-right:0}
#cbOv .cbms .hd{flex:none;height:48px;display:flex;align-items:center;gap:8px;padding:0 12px}
#cbOv .cbms .hd b{flex:1;text-align:center;font-size:17px;color:#ffe9a8;margin-right:64px}
#cbOv .cbms>.cbcoinl{flex:none;margin:0 0 4px}
#cbOv .cbms .msm{flex:none;margin:0 0 6px;text-align:center;font-size:14px;font-weight:700;line-height:1.35;color:#ffe2a0}
#cbOv .cbms .msm small{display:block;font-size:11.5px;font-weight:400;color:#d9c08c}
#cbOv .cbms .tabs{flex:none;display:flex;gap:4px;margin:0 14px 4px;padding:3px;border-radius:24px;border:1.5px solid #c9a35a;background:#1b1209}
#cbOv .cbms .tabs button{flex:1 1 0;height:44px;border:0;border-radius:22px;background:none;color:#bfa873;font-size:15px;font-weight:700;line-height:1.2;padding:0 6px}
#cbOv .cbms .tabs button small{display:block;font-size:11px;font-weight:400}
#cbOv .cbms .tabs button.on{background:linear-gradient(180deg,#ffe9a8,#e2a83e);color:#3a2206}
#cbOv .cbms .bd{flex:1 1 auto;min-height:0;overflow:auto;-webkit-overflow-scrolling:touch;padding:0 14px 26px}
#cbOv .cbms h4{margin:12px 2px 6px;font-size:15px;color:#ffe2a0;border-left:4px solid #e2a83e;padding-left:8px}
#cbOv .cbms .cur{display:flex;align-items:baseline;justify-content:center;flex-wrap:wrap;gap:0 6px;margin:0 0 8px;font-size:13.5px;color:#f0dfb6}
#cbOv .cbms .cur b{font-family:"Dela Gothic One","Hiragino Sans",sans-serif;font-weight:400;font-size:30px;line-height:1.1;color:#ffe07a}
#cbOv .cbms .cur small{flex:0 0 100%;text-align:center;font-size:12px;color:#d9c08c}
#cbOv .cbms .cur .cbci{width:1.2em;height:1.2em;vertical-align:-.25em;margin-right:.1em}
#cbOv .cbms .msl{display:flex;flex-direction:column;gap:6px}
#cbOv .msr{display:grid;grid-template-columns:5.4em 1fr auto;align-items:center;gap:6px;min-height:42px;box-sizing:border-box;padding:4px 12px;border-radius:12px;border:1.5px solid rgba(255,226,160,.2);background:rgba(255,236,190,.05);color:#d9c08c;font-size:14px}
#cbOv .msr .n{font-size:16px;color:#f0dfb6}
#cbOv .msr .c{font-weight:700;color:#f0dfb6}
#cbOv .msr .c .cbci{width:1.3em;height:1.3em;vertical-align:-.3em;margin-right:.15em}
#cbOv .msr em{font-style:normal;font-size:12.5px;font-weight:700}
#cbOv .msr.done{border-color:#f7d27c;background:rgba(255,214,120,.16)}
#cbOv .msr.done .n,#cbOv .msr.done .c{color:#ffe07a}
#cbOv .msr.done em{color:#ffe07a}
#cbOv .msr.next{border-color:#c9a35a;background:rgba(255,236,190,.1)}
#cbOv .msr.next em{color:#ffd9a0}
#cbOv .cbms .note{margin:12px 2px 0;padding:0 0 0 1.2em;font-size:12px;line-height:1.65;color:#d9c08c}
#cbOv .cbend .gift .cbmsn{display:inline-flex;align-items:center;flex-wrap:wrap;justify-content:center;gap:0 5px;box-sizing:border-box;max-width:100%;padding:3px 14px 4px;border-radius:16px;border:1.5px solid #ffd76a;background:rgba(255,214,120,.15);font-size:13.5px;line-height:1.5;color:#fff1cf;animation:cbget .45s cubic-bezier(.2,1.4,.4,1) 1 both}
#cbOv .cbend .gift .cbmsn i{font-style:normal}
#cbOv .cbend .gift .cbmsn b{color:#ffe07a;font-size:15px}
#cbOv .cbend .gift .cbmsn .cbci{width:1.25em;height:1.25em;vertical-align:-.28em;margin-right:0}
@media (max-height:720px){#cbOv .cbmenu .lg{width:min(44vw,168px)}#cbOv .cbmenu{gap:8px}}
@media (prefers-reduced-motion: reduce){#cbOv .cbglow.on{animation:none}#cbOv .cbhand .cbc.new{animation:none}#cbOv .cbflip .in{transition:none}#cbOv .cbget{animation:none}#cbOv .cbend .gift .cbmsn{animation:none}#cbOv .cbfire{animation:none;opacity:.88}}
#cbOv.nofx .cbglow.on{animation:none}#cbOv.nofx .cbhand .cbc.new{animation:none}#cbOv.nofx .cbflip .in{transition:none}#cbOv.nofx .cbget{animation:none}#cbOv.nofx .cbend .gift .cbmsn{animation:none}
#cbOv.nofx .cbban,#cbOv.nofx .cbres,#cbOv.nofx .cbvs .sd,#cbOv.nofx .cbhand .cbc,#cbOv.nofx .cbtoast{transition:none}
`;
  let ov = null, built = false, scr = {}, flyEl = null, modEl = null, toastEl = null, banEl = null;
  const $ = (s, r) => (r || ov).querySelector(s);
  function build() {
    if (built) return; built = true;
    const s = document.createElement('style'); s.id = 'cbCss'; s.textContent = css; document.head.appendChild(s);
    ov = document.createElement('div'); ov.id = 'cbOv'; ov.setAttribute('role', 'dialog'); ov.setAttribute('aria-modal', 'true'); ov.setAttribute('aria-label', 'TENGERカードバトル');
    ov.innerHTML = '<div class="cbbg"><div class="cbfire"></div></div>'
      + '<section class="cbs cbmenu" data-s="menu"><button type="button" class="cbb dk sm cbx" data-cb="close">← もどる</button>'
      + '<img class="lg" src="cb_logo.webp" alt=""><h1 class="gold"><small>TENGER</small>カードバトル</h1><p class="rec"></p><p class="cbcoinl"></p>'
      + '<div class="btns"><button type="button" class="cbb" data-cb="cpu">コンピュータと 対戦</button>'
      + '<div class="row"><button type="button" class="cbb" data-cb="host">部屋を 作る<small>友だちと 対戦</small></button><button type="button" class="cbb" data-cb="join">部屋に 入る<small>友だちと 対戦</small></button></div>'
      + '<div class="row two"><button type="button" class="cbb dk" data-cb="help">あそび方</button><button type="button" class="cbb dk" data-cb="gear">設定<small>BGM・効果音</small></button></div>'
      + '<div class="row two"><button type="button" class="cbb dk" data-cb="ms">🎯ミッション<small class="msn"></small></button><button type="button" class="cbb dk" data-cb="dz">デザインカスタム<small>おもて・うらを 解放</small></button></div></div></section>'
      + '<section class="cbs cbroom" data-s="room"></section>'
      + '<section class="cbs cbgame" data-s="game">'
      + '<div class="cbtop"><button type="button" class="cbb dk sm" data-cb="quit">やめる</button><div class="cbturn"></div><button type="button" class="cbb dk sm" data-cb="help" aria-label="あそび方">？</button></div>'
      + '<div class="cbmidw"><div class="cbopp"><div class="cbohand"></div><div class="cbwho"><b></b><span class="cbpips" data-p="op"></span></div></div>'
      + '<div class="cbboard"><img src="cb_board.webp" alt=""><div class="cbfire"></div><div class="cbglow"></div>'
      + '<div class="cbdeck"><img src="cb_deck.webp" alt=""><b class="cbn"></b></div>'
      + '<button type="button" class="cbdis" data-cb="discard" aria-label="捨て札を 見る"><span class="pl"></span><b class="cbn"></b></button>'
      + '<div class="cbslot op"></div><div class="cbslot my"></div>'
      + '<button type="button" class="cbgear" data-cb="gear" aria-label="メニュー"></button></div>'
      + '<div class="cbmsg" aria-live="polite"></div>'
      + '<div class="cbme"><div class="cbwho"><b>あなた</b><span class="cbpips" data-p="my"></span></div></div>'
      + '<div class="cbhand"></div><div class="cbact"></div></div></section>'
      + '<section class="cbs cbhelp" data-s="help"></section>'
      + '<section class="cbs cbdz" data-s="dz"></section>'
      + '<section class="cbs cbms" data-s="ms"></section>'
      + '<div class="cbfly"></div><div class="cbban"></div><div class="cbmod" role="dialog" aria-modal="true"></div><div class="cbtoast" aria-live="polite"></div>';
    document.body.appendChild(ov);
    ov.querySelectorAll('.cbs').forEach(e => { scr[e.dataset.s] = e; });
    flyEl = $('.cbfly'); modEl = $('.cbmod'); toastEl = $('.cbtoast'); banEl = $('.cbban');
    ov.addEventListener('click', onClick);
    document.addEventListener('visibilitychange', () => { if (ov.classList.contains('on')) bgmSync(); });      // アプリが うしろに 行った・もどった：BGM を 止める・つづきから
    window.addEventListener('resize', () => { if (ov.classList.contains('on')) layout(); });
    if (window.ResizeObserver) new ResizeObserver(() => { if (ov.classList.contains('on')) layout(); }).observe(scr.game);
  }
  let screen = '';
  function show(name) { screen = name; Object.keys(scr).forEach(k => scr[k].classList.toggle('on', k === name)); }
  let toastT = 0;
  function toast(t, sec) {
    toastEl.textContent = t;
    // 対戦の 画面では ことばの 行（ボードの すぐ 下）に 重ねる：相手の 手札や ボードの 動きを かくさない
    const m = screen === 'game' ? $('.cbmsg') : null;
    if (m && m.getBoundingClientRect().height) { const r = m.getBoundingClientRect(), o = ov.getBoundingClientRect(); toastEl.style.top = Math.max(60, r.top - o.top - 6) + 'px'; }
    else if (screen === 'dz' || screen === 'ms') toastEl.style.top = Math.round(ov.getBoundingClientRect().height * 0.6) + 'px';      // 第4.182版：デザインカスタムでは まん中より 下（上の コインの 数と タブを かくさない）
    else toastEl.style.top = '';
    toastEl.classList.add('on');
    unlater(toastT); toastT = later(() => toastEl.classList.remove('on'), (sec || 2.4) * 1000 * Math.max(SPEED, 0.2));
  }
  async function banner(big, small, ms) {
    banEl.innerHTML = `<div class="bd"><b class="gold">${esc(big)}</b>${small ? `<small>${esc(small)}</small>` : ''}</div>`; banEl.classList.add('on');
    await T(ms || 900); banEl.classList.remove('on'); await T(180);
  }

  // ---------- メニュー ----------
  function showMenu() {
    closeMod(); show('menu'); msRoll();
    const tot = st.win + st.lose + st.draw;
    $('.rec', scr.menu).innerHTML = (tot ? `<b>${st.win}</b>勝 <b>${st.lose}</b>敗 <b>${st.draw}</b>分` + (st.streak > 0 ? `　いま <b>${st.streak}</b>連勝！` : '') + '<br>' : '')
      + `勝つと お世話トークン <b>${REWARD.win}</b>こ・<b>${REWARD.every}</b>連勝 ごとに <b>${REWARD.bonus}</b>こ`;
    $('.cbcoinl', scr.menu).innerHTML = `${COINI}<span>バトルコイン <b>${st.coin}</b>枚</span><small>コンピュータに 勝つと ${COIN.win}枚・${COIN.every}連勝 ごとに ${COIN.bonus}枚</small>`;
    $('[data-cb=ms] .msn', scr.menu).textContent = `今月 ${msDone()}／${MS_ALL} 達成`;      // 第4.183版：ミッション
    const lw = [];
    if (lostStake > 0) { lw.push(`参加コイン ${lostStake}枚は もどらなかったよ`); lostStake = 0; }
    if (lostMs) { lw.push(`ミッションの 連勝（${MS_WHO[lostMs]}）は 0 に もどったよ`); lostMs = ''; }
    if (lw.length) toast('前の 対戦が とちゅうで 終わった ので、\n' + lw.join('\n'), 3.6 + (lw.length - 1) * 1.2);
    const can = !!(window.__NATIVE && window.TengelNative);
    scr.menu.querySelectorAll('[data-cb=host],[data-cb=join]').forEach(b => { b.disabled = !can; });
    pay().then(p => { if (p && p.add > 0 && screen === 'menu') toast(`🎟 前の 対戦の ごほうび\nお世話トークン ${p.add}こを 受け取ったよ`, 3.2); });
  }

  // ---------- あそび方 ----------
  let helpBack = 'menu';
  function showHelp(from) {
    helpBack = from || 'menu'; closeMod();
    const ef = (k, t, d) => `<div class="ef"><img src="${pic(k)}" alt=""><div><b>${t}</b>${d}</div></div>`;
    scr.help.innerHTML = '<div class="hd"><button type="button" class="cbb dk sm" data-cb="helpx">← もどる</button><b>あそび方</b></div><div class="bd">'
      + `<h4>勝負の しかた</h4><ul><li>手札は <b>${R.HAND}まい</b>。<b>${R.TURNS}ターン</b>で 勝負するよ</li><li>${R.TURNS}ターン 終わって、<b>勝った 数が 多い 人の 勝ち</b>（同じ なら 同点）。先に 勝ちが 決まっても、さいごの ターンまで やるよ</li><li>出すのは 1ターンに 1まい。${R.HAND - R.TURNS}まいは 使わずに のこるよ</li></ul>`
      + '<h4>1ターンの 流れ</h4><ul><li><b>① セット</b>：手札から 1まい えらんで「この カードを セットする」。ふせて 出すよ。<b>セットしたら もう 変えられない</b></li>'
      + '<li><b>② 効果タイム</b>：2人とも セットしたら、使える 効果が ある 人に「効果を 使う？」と 聞くよ。<b>「使う」「使わない」は 自分で えらべる</b>。2人とも 決めたら、いっしょに 効果が 出る</li>'
      + '<li><b>③ オープン</b>：2まいを いっしょに めくる。<b>強い カードの 勝ち</b>（1・2 の「<b>逆転勝利</b>」は、めくった あとに 使うか えらぶよ）</li></ul>'
      + '<h4>カードの 強さ</h4><div class="ord">' + ['k', 'm'].map(k => `<img src="${pic(k)}" alt="${nameOf(k)}">`).join('<i>＝</i>') + ['1', '2', '3', '4', '5', '6', '7'].map(k => `<i>＞</i><img src="${pic(k)}" alt="${k}">`).join('') + '</div>'
      + '<ul><li><b>神様馬</b>と <b>幻の馬</b>が いちばん 強い（この 2まいが ぶつかったら 引き分け）</li><li>数字は <b>1 が いちばん 強くて、7 が いちばん 弱い</b></li><li><b>同じ 数字</b>が ぶつかったら「かぶり」＝<b>どちらも 負け</b>（4 どうしで <b>2人とも 4 の 効果を 使った</b> ときは <b>ドロー</b>）</li><li><b>逆転勝利</b>：1 が 3まい あれば 神様馬・幻の馬に、2 が 3まい あれば 1 に 勝てる（下の「カードの 効果」）</li><li>カードは ぜんぶで 30まい（1〜7 が 4まい ずつ・神様馬 1まい・幻の馬 1まい）</li></ul>'
      + '<h4>カードの 効果</h4><ul><li><b>7・6・5・4・3</b> の 効果は、2人とも セットした あとの「<b>効果タイム</b>」で、使うか えらぶよ</li><li><b>1・2</b> の 効果（逆転勝利）は、<b>オープンした あと</b>、負けた 人が 使うか えらぶよ</li><li><b>神様馬・幻の馬</b>の 効果は、勝った <b>次の ターンの はじめ</b>に、使うか えらぶよ</li><li>どの 効果も、<b>使うか 使わないかは 自分で えらべる</b>よ</li></ul>'
      + ef('7', '7：3まい そろえて 交換', '手札に 7 が 3まい あれば、3まいを 山札に もどして、新しく 3まい 引けるよ。')
      + ef('6', '6：2まい 見せて 手札を 見る', '手札に 6 が 2まい あれば、その 2まいを 相手に 見せて、相手の 手札を 1まい えらんで 見られるよ。<br>相手の 手札が <strong>もう 見た カード だけ</strong>の ときは 使えないよ（見るのは まだ 見て いない カード）。')
      + ef('5', '5：2まい 捨てて 山札から セット', '5 を セットしたら、その 5 と 手札 1まいを 捨てて、山札から 1まいを ふせて セットできるよ。何が 出るかは オープンまで わからない！<br>使えるのは、使った あとの 手札が <strong>のこりの ターンの 数より 少なく ならない とき</strong> だけ（さいごの ターンは、手札が 1まい あれば 使える）。')
      + ef('4', '4：見せて 強制交換', '4 を セットして 効果を 使うと、4 を 先に 見せる かわりに、相手は セットした カードを 手札の 別の カードと 交換しないと いけないよ。<br><strong>2人とも 4 を 出して、2人とも 効果を 使ったら</strong>、打ち消して その ターンは <strong>ドロー</strong>（引き分け）だよ。<br>交換で <strong>5 を セットしたら、5 の 効果を 使うか えらべる</strong>よ（オープンの 前）。')
      + ef('3', '3：3まい 見せて 手札を 交換', '手札に 3 が 3まい あれば、その 3まいを 相手に 見せて、その うちの 1まいと、相手の 手札から <strong>ランダムに えらんだ 1まい</strong>を 交換できるよ。')
      + ef('2', '2：3まい 見せて 逆転勝利', '2 を 出して <strong>1 に 負けた</strong> とき、手札に 2 が 2まい あれば（場の 2 と 合わせて 3まい）、その 2まいを 相手に 見せて、1まい 捨てると、<strong>勝ちに できる</strong>よ。')
      + ef('1', '1：3まい 見せて 逆転勝利', '1 を 出して <strong>神様馬・幻の馬に 負けた</strong> とき、手札に 1 が 2まい あれば（場の 1 と 合わせて 3まい）、その 2まいを 相手に 見せて、1まい 捨てると、<strong>勝ちに できる</strong>よ。<br>1・2 とも、使えるのは 捨てた あとの 手札が <strong>のこりの ターンの 数より 少なく ならない とき</strong> だけ。')
      + ef('k', '神様馬：勝ったら 手札を 見る', '神様馬で 勝ったら、次の ターンの はじめに、相手の 手札を 1まい えらんで 見られるよ（まだ 見て いない カードが ある とき）。')
      + ef('m', '幻の馬：勝ったら 手札を 交換', '幻の馬で 勝ったら、次の ターンの はじめに、手札を 2まい 捨てて、山札から 2まい 引けるよ。')
      + '<ul><li>手札の 数は「セットした あと」で 数えるよ（セットした カードは 手札に 入らない）</li><li>効果タイムで 効果が 出る 順番は <b>6 → 5 → 7 → 3 → 4</b></li><li>さいごの ターンに 神様馬・幻の馬で 勝った ときは、次の ターンが ない ので 効果は ないよ</li></ul>'
      + '<h4>見た カード・見られた カード</h4><ul><li>効果で 見た 相手の カードは、相手の 手札に ある あいだ 表で 見えるよ</li><li>相手に 見られた 自分の カードには 目の しるしが つくよ</li></ul>'
      + '<h4>捨て札</h4><ul><li>ボードの「<b>捨て札</b>」を タップすると、捨て札を 見られるよ</li><li><b>終わった ターンの 捨て札</b>（2人が 出した カード）と、<b>効果で 捨てた カード</b>に 分けて 出るよ</li></ul>'
      + `<h4>ごほうび</h4><ul><li>勝つと <b>お世話トークン ${REWARD.win}こ</b></li><li><b>${REWARD.every}連勝</b> ごとに <b>${REWARD.bonus}こ</b>（負けると 連勝は 0 に もどるよ。同点は そのまま）</li><li>お世話トークンは 25こ まで。対戦の とちゅうで やめると 負けに なるよ</li></ul>`
      + `<h4>バトルコイン</h4><ul><li><b>コンピュータに 勝つと ${COIN.win}枚</b>・<b>${COIN.every}連勝 ごとに ${COIN.bonus}枚</b> もらえるよ。<b>買う ことは できない</b>よ</li>`
      + '<li>友だちと 対戦する 部屋を 作る とき、<b>参加コイン</b>と <b>勝者の 獲得コイン</b>（参加コインの 2倍 まで）を 決められるよ</li><li>部屋に 入る 人は、同じ 数の 参加コインを 持って いないと 入れないよ</li>'
      + '<li>2人とも はじめに 参加コインを 出す。<b>勝った 人は、テンゲルから 獲得コインを プレゼントで もらえる</b>。同点は 参加コインが もどる</li><li><b>とちゅうで やめると、参加コインは もどらない</b>（つながりが 切れた ときは もどるよ）</li></ul>'
      + `<h4>デザインカスタム</h4><ul><li>メニューの「<b>デザインカスタム</b>」で、カードの <b>おもて</b>と <b>うら</b>の デザインを かえられるよ</li>`
      + `<li>新しい デザインは <b>バトルコイン</b>で 1つずつ 解放できるよ：カードの おもて <b>${FACE_COST}枚</b>（神様馬・幻の馬は <b>${TOP_COST}枚</b>）・カードの うら <b>${BACK_COST}枚</b>。いつもの デザインは はじめから 使えるよ</li>`
      + '<li>コンピュータと 対戦する ときは、コンピュータの カード（うら・おもて）も あなたが えらんだ デザインに なるよ</li><li>友だちと 対戦する ときは、<b>あなたの カードは あなたの デザイン</b>・<b>友だちの カードは 友だちが えらんだ デザイン</b>で 出るよ（山札は あなたの うら）</li></ul>'
      + `<h4>ミッション</h4><ul><li>メニューの「<b>ミッション</b>」：<b>コンピュータに 連続勝利</b>・<b>友だちバトルで 連続勝利</b>で バトルコインが もらえるよ</li>`
      + `<li>コンピュータ：${MS.cpu.map(t => `${t[0]}連勝 <b>${t[1]}枚</b>`).join('・')}</li><li>友だちバトル：${MS.fr.map(t => `${t[0]}連勝 <b>${t[1]}枚</b>`).join('・')}</li>`
      + '<li>達成した ときに、その場で もらえるよ（受け取りは いらない）。<b>毎月 1日に リセット</b>（達成も 連勝も 0 に もどる）</li>'
      + '<li>負けると その 連勝は 0 に もどるよ（とちゅうで やめた・対戦の とちゅうで アプリを 閉じた ときも 同じ）。同点は そのまま。友だちが とちゅうで 部屋を 出た・つながりが 切れた ときは 数えないよ</li><li>コンピュータと 友だちバトルの 連勝は 別に 数えるよ</li></ul>'
      + '<h4>音と エフェクト（設定）</h4><ul><li>ボードの 右下の <b>歯車</b>（メニューでは「設定」）を 押すと、<b>BGM</b>・<b>効果音</b>・<b>エフェクト</b>（光や 動きの 演出）を オン／オフ できるよ</li></ul>'
      + '<h4>友だちと 対戦（部屋）</h4><ul><li>1人が「部屋を 作る」→ 出て きた <b>部屋番号（4けた）</b>を 友だちに 教える</li><li>友だちは「部屋に 入る」で その 番号を 入れる</li><li><b>近くに いる 友だち</b>と、iPhone どうしで 直接 つながるよ（インターネットは 使わない）。2人とも Wi‑Fi か Bluetooth を オンに してね</li><li>はじめて 使う とき「ローカルネットワーク」の 確認が 出たら「許可」を 押してね</li></ul>'
      + '</div>';
    show('help');
  }

  // ---------- デザインカスタム（第4.182版）----------
  //   画面（scr.dz）：「カードの おもて」（種類ごとに いつもの ＋ べつの デザイン）・「カードの うら」（いつもの ＋ 7種）。タイルを 押す → 窓（大きい 絵・使う／解放）
  //   解放の 窓は「やめる」「解放する」。窓が 出て すぐ（DZ_GUARD）は「解放する」を 受けつけない（つづけて 2回 押した ゆびで 解放しない）
  let dzTab = 'f', dzAt = 0;
  const DZ_GUARD = 450;
  const testOn = () => !!(window.__TEST && window.CBTest);      // テスト版だけ（cb_test.js：App Store版の 中身には 入らない）
  const dzLabel = k => NAMES[k] || k + ' の カード';
  const dzFind = id => FACES.find(f => f.id === id) || BACKS.find(b => b.id === id) || null;
  const dzOwn = d => !d || (d.k ? st.faces : st.backs).indexOf(d.id) >= 0;      // d＝null：いつもの（はじめから 使える）
  const dzUsed = (kind, id) => (kind ? st.face[kind] || '' : st.back) === (id || '');
  const dzWhat = kind => (kind ? dzLabel(kind) + 'の おもて' : 'カードの うら');
  // d が kind の デザインか（id '' ＝ いつもの）。ちがえば null
  function dzGet(kind, id) {
    if (kind && DZ_KINDS.indexOf(kind) < 0) return undefined;
    if (!id) return null;
    const d = dzFind(id); return d && (d.k || null) === (kind || null) ? d : undefined;
  }
  function dzTile(kind, d) {
    const id = d ? d.id : '', used = dzUsed(kind, id), own = dzOwn(d);
    const img = d ? d.s : kind ? 'cb_s' + kind + '.webp' : 'cb_sb.webp';
    const em = used ? '使って いる' : own ? '持って いる' : `${COINI}${d.cost}枚`;
    return `<button type="button" class="dzt${used ? ' on' : ''}${own ? '' : ' lk'}" data-cb="dzi" data-id="${id}" data-ck="${kind || ''}" aria-label="${esc((d ? d.name : 'いつもの') + '・' + em.replace(/<[^>]+>/g, ''))}"><img src="${img}" alt="" draggable="false"><span>${esc(d ? d.name : 'いつもの')}</span><em>${em}</em></button>`;
  }
  function showDz(tab) {
    const same = !tab || tab === dzTab, b0 = $('.bd', scr.dz), y = same && b0 && screen === 'dz' ? b0.scrollTop : 0;
    if (tab) dzTab = tab;
    closeMod();
    const body = dzTab === 'b'
      ? `<h4>カードの うら<small>1つ ${COINI}${BACK_COST}枚</small></h4><div class="tiles b">${dzTile(null, null)}${BACKS.map(d => dzTile(null, d)).join('')}</div>`
        + '<p class="dzn">えらんだ うらは、あなたの 画面の 山札・あなたの ふせた カードに 出るよ。コンピュータの 手札も この うら。友だちと 対戦する ときは、友だちの カードは 友だちが えらんだ うらに なるよ</p>'
      : DZ_KINDS.map(k => `<h4>${esc(dzLabel(k))}<small>1つ ${COINI}${k === 'k' || k === 'm' ? TOP_COST : FACE_COST}枚</small></h4><div class="tiles">${dzTile(k, null)}${FACES.filter(f => f.k === k).map(f => dzTile(k, f)).join('')}</div>`).join('')
        + '<p class="dzn">えらんだ デザインは、あなたの カードに 出るよ（手札・めくった とき・捨て札）。コンピュータの カードも この デザイン。友だちと 対戦する ときは、友だちの カードは 友だちが えらんだ デザインに なるよ</p>';
    scr.dz.innerHTML = '<div class="hd"><button type="button" class="cbb dk sm" data-cb="dzx">← もどる</button><b>デザインカスタム</b></div>'
      + `<p class="cbcoinl">${COINI}<span>バトルコイン <b>${st.coin}</b>枚</span></p>`
      + `<div class="tabs" role="tablist"><button type="button" role="tab" data-cb="dztab" data-t="f" class="${dzTab === 'f' ? 'on' : ''}" aria-selected="${dzTab === 'f'}">カードの おもて</button>`
      + `<button type="button" role="tab" data-cb="dztab" data-t="b" class="${dzTab === 'b' ? 'on' : ''}" aria-selected="${dzTab === 'b'}">カードの うら</button></div>`
      + `<div class="bd">${body}${testOn() ? window.CBTest.html() : ''}</div>`;
    show('dz');
    const b1 = $('.bd', scr.dz); if (b1) b1.scrollTop = y;
  }
  // タイルを 押した：大きい 絵と「使う」／「バトルコイン ○枚で 解放」
  function dzItem(kind, id) {
    const d = dzGet(kind, id); if (d === undefined) return;
    const used = dzUsed(kind, id), own = dzOwn(d), big = d ? d.c : kind ? 'cb_c' + kind + '.webp' : 'cb_cb.webp';
    let btns;
    if (used) btns = '<button type="button" class="cbb" disabled>使って いるよ</button>';
    else if (own) btns = `<button type="button" class="cbb" data-cb="dzuse" data-id="${id || ''}" data-ck="${kind || ''}">この デザインを 使う</button>`;
    else if (st.coin >= d.cost) btns = `<button type="button" class="cbb" data-cb="dzopen" data-id="${d.id}" data-ck="${kind || ''}">${COINI}バトルコイン ${d.cost}枚で 解放</button>`;
    else btns = `<button type="button" class="cbb" disabled>${COINI}バトルコイン ${d.cost}枚で 解放</button><p class="cbneed">あと ${d.cost - st.coin}枚 たりないよ<br>（コンピュータに 勝つと ${COIN.win}枚・${COIN.every}連勝 ごとに ${COIN.bonus}枚）</p>`;
    modal(`<h3 class="gold">${esc(d ? d.name : 'いつもの')}<small>${esc(dzWhat(kind))}</small></h3><div class="big"><img src="${big}" alt="${esc(dzWhat(kind))}"></div>`
      + `<div class="col">${btns}<button type="button" class="cbb dk" data-cb="dzback">もどる</button></div>`, 'cbdzm');
  }
  // 解放の 窓（コインの 数 → のこり）
  function dzAsk(kind, id) {
    const d = dzGet(kind, id); if (!d || dzOwn(d) || st.coin < d.cost) return;
    dzAt = performance.now();
    modal(`<h3 class="gold">解放する？</h3><div class="big sm"><img src="${d.s}" alt=""></div><p>『${esc(d.name)}』（${esc(dzWhat(kind))}）を 解放するよ</p>`
      + `<p class="cbstkv">${COINI}<b>${st.coin}</b>枚<i>→</i>のこり <b>${st.coin - d.cost}</b>枚</p>`
      + `<div class="rowb"><button type="button" class="cbb dk" data-cb="dzback">やめる</button><button type="button" class="cbb" data-cb="dzgo" data-id="${d.id}" data-ck="${kind || ''}">解放する</button></div>`, 'cbdzm');
  }
  function dzGo(kind, id) {
    const d = dzGet(kind, id); if (!d || dzOwn(d) || st.coin < d.cost) return;
    st.coin -= d.cost; (d.k ? st.faces : st.backs).push(d.id);
    if (d.k) st.face[d.k] = d.id; else st.back = d.id;      // 解放したら すぐ その デザインに
    save(); se('magic', 0.8);
    showDz(); toast(`『${d.name}』を 解放したよ！\n${dzWhat(kind)}が この デザインに なったよ`, 3);
  }
  function dzUse(kind, id) {
    const d = dzGet(kind, id); if (d === undefined || !dzOwn(d)) return;
    if (kind) { if (d) st.face[kind] = d.id; else delete st.face[kind]; } else st.back = d ? d.id : '';
    save(); se('tap', 0.7);
    showDz(); toast(`${dzWhat(kind)}を『${d ? d.name : 'いつもの'}』に したよ`, 2.4);
  }
  // テスト版の 道具（cb_test.js）に わたす もの：App Store版では 使われない
  const dzApi = {
    add: k => { addCoin(k); save(); showDz(); toast(`🧪 バトルコイン ＋${k}枚（いま ${st.coin}枚）`, 2); },
    set: k => { st.coin = Math.max(0, Math.min(COIN.max, Math.floor(+k || 0))); save(); showDz(); toast(`🧪 バトルコイン ${st.coin}枚に したよ`, 2); },
    reset: () => { st.backs = []; st.faces = []; st.back = ''; st.face = {}; save(); showDz(); toast('🧪 解放を ぜんぶ もとに もどしたよ（いつもの デザイン）', 2.4); }
  };

  // ---------- ミッション（第4.183版）----------
  //   画面（scr.ms）：今月の ミッション・リセットの 日・タブ（コンピュータ／友だちバトル：達成した 数）・いまの 連勝・7つの ミッション（達成／あと ○勝）・決まりの 説明
  let msTab = 'cpu';
  function showMs(tab) {
    if (tab) msTab = tab === 'fr' ? 'fr' : 'cpu';
    closeMod(); msRoll();
    const d = nowD(), nx = new Date(d.getFullYear(), d.getMonth() + 1, 1), left = Math.max(1, Math.ceil((nx - d) / 86400000)), s = st.ms, kd = msTab, cur = s[kd];
    const nt = MS[kd].find(t => s.got[kd].indexOf(t[0]) < 0);      // つぎの ミッション（ぜんぶ 達成 なら なし）
    const rows = MS[kd].map(t => {
      const done = s.got[kd].indexOf(t[0]) >= 0, nxt = !!nt && nt[0] === t[0];
      return `<div class="msr${done ? ' done' : nxt ? ' next' : ''}" data-n="${t[0]}"><b class="n">${t[0]}連勝</b><span class="c">${COINI}${t[1]}枚</span><em>${done ? '✓ 達成' : nxt ? `あと ${Math.max(1, t[0] - cur)}勝` : ''}</em></div>`;
    }).join('');
    scr.ms.innerHTML = '<div class="hd"><button type="button" class="cbb dk sm" data-cb="msx">← もどる</button><b>ミッション</b></div>'
      + `<p class="cbcoinl">${COINI}<span>バトルコイン <b>${st.coin}</b>枚</span></p>`
      + `<p class="msm">${d.getMonth() + 1}月の ミッション<small>${nx.getMonth() + 1}月1日に リセット（あと ${left}日）</small></p>`
      + `<div class="tabs" role="tablist">${['cpu', 'fr'].map(k => `<button type="button" role="tab" data-cb="mstab" data-t="${k}" class="${kd === k ? 'on' : ''}" aria-selected="${kd === k}">${MS_WHO[k]}<small>${s.got[k].length}／${MS[k].length} 達成</small></button>`).join('')}</div>`
      + `<div class="bd"><h4>${kd === 'cpu' ? 'コンピュータに 連続勝利' : '友だちバトルで 連続勝利'}</h4>`
      + `<p class="cur"><span>いま</span><b>${cur}</b><span>連勝</span><small>${nt ? `つぎは ${nt[0]}連勝で ${COINI}${nt[1]}枚（あと ${Math.max(1, nt[0] - cur)}勝）` : '今月の ミッションは ぜんぶ 達成！ 🎉'}</small></p>`
      + `<div class="msl">${rows}</div>`
      + '<ul class="note"><li>達成すると、その場で バトルコインが もらえるよ（受け取りは いらない）</li>'
      + '<li>負けると 連勝は 0 に もどるよ（とちゅうで やめた・対戦の とちゅうで アプリを 閉じた ときも）。同点は そのまま</li>'
      + (kd === 'fr' ? '<li>友だちが とちゅうで 部屋を 出た・つながりが 切れた ときは 数えないよ</li>' : '')
      + '<li>コンピュータと 友だちバトルの 連勝は 別に 数えるよ</li><li><b>毎月 1日に リセット</b>（達成も 連勝も 0 に もどるよ）</li></ul>'
      + `${testOn() && window.CBTest.msHtml ? window.CBTest.msHtml() : ''}</div>`;
    show('ms');
  }
  // テスト版の 道具（cb_test.js）に わたす もの：App Store版では 使われない
  const msApi = {
    win: kd => { const g = msWin(kd), c = g.reduce((a, x) => a + x.c, 0); addCoin(c); save(); showMs(kd); toast(g.length ? `🧪 ${MS_WHO[kd]}で 1勝 → ミッション達成！\n${g.map(x => `${x.n}連勝 ＋${x.c}枚`).join('・')}（いま ${st.coin}枚）` : `🧪 ${MS_WHO[kd]}で 1勝（いま ${st.ms[kd]}連勝）`, 2.6); },
    lose: kd => { msRoll(); st.ms[kd] = 0; save(); showMs(kd); toast(`🧪 ${MS_WHO[kd]}で 負け（連勝 0）`, 2); },
    next: () => { st.ms.m = '2000-01'; msRoll(); showMs(); toast('🧪 月が かわった ことに したよ（ミッションを リセット）', 2.4); }
  };

  // ---------- 部屋（作る・入る）----------
  let room = null;                                     // { mode, code, nr（つなぐ 部品）, tm }
  function roomNumber() { let n = 0; try { const a = new Uint16Array(1); crypto.getRandomValues(a); n = a[0]; } catch (e) { n = Math.floor(Math.random() * 65536); } return String(1000 + n % 9000); }
  //   第4.179版：バトルコインを 持って いる 人が 部屋を 作る ときは、先に 参加コインと 勝者の 獲得コインを 決める（step 'stake'）。持って いなければ コインなしの 部屋を すぐ 作る（前と 同じ）。
  //   keep＝「もう一度 作る」：決めた 数の まま 作り直す
  function showRoom(mode, keep) {
    const old = keep && room && room.stake ? room.stake : null;
    closeMod(); roomStop();
    room = { mode: mode, code: mode === 'host' ? (CBApp._room || roomNumber()) : '', nr: null, tm: 0, step: '', stake: old || { e: 0, w: 0 } };
    if (mode === 'host' && !old && st.coin > 0) { room.step = 'stake'; paintRoom(); show('room'); return; }
    paintRoom(); show('room');
    if (mode === 'host') roomGo();
  }
  // 参加コイン・勝者の 獲得コインを かえる（部屋を 作る 前）：参加コインは 持って いる 数 まで・獲得コインは 参加コイン 〜 2倍（参加コインを かえたら 2倍に もどす）
  function stakeSet(kind, v) {
    const r = room; if (!r || r.mode !== 'host' || r.step !== 'stake') return;
    const k = r.stake, maxE = Math.min(st.coin, CBNet.STAKE_MAX);
    if (kind === 'e') { const e = Math.max(0, Math.min(maxE, Math.floor(+v || 0))); k.e = e; k.w = e * 2; }
    else k.w = Math.max(k.e, Math.min(k.e * 2, k.w + (v > 0 ? 1 : -1)));
    se('tap', 0.6); paintRoom();
  }
  function paintRoom() {
    const r = room, e = scr.room; if (!r) return;
    const digits = c => [0, 1, 2, 3].map(i => `<span class="${i === c.length ? 'cur' : ''}">${c.charAt(i)}</span>`).join('');
    let h = '<button type="button" class="cbb dk sm cbx" data-cb="roomx">← やめる</button>';
    if (r.mode === 'host' && r.step === 'stake') {      // 第4.179版：参加コイン・勝者の 獲得コインを 決める
      const k = r.stake, maxE = Math.min(st.coin, CBNet.STAKE_MAX), chips = STAKE_CHIPS.filter(q => q <= maxE);
      h += '<h2 class="gold">部屋を 作る</h2><p>参加コインと、勝った 人が もらう コインを 決めてね</p>'
        + `<p class="cbcoinl">${COINI}<span>持って いる バトルコイン <b>${st.coin}</b>枚</span></p>`
        + '<div class="cbstk"><div class="blk"><b>参加コイン</b><small>2人とも はじめに 出す 数。同じ 数を 持って いる 人 だけ 入れるよ</small>'
        + `<div class="chips" role="group" aria-label="参加コイン">${chips.map(q => `<button type="button" class="${q === k.e ? 'on' : ''}" data-cb="stke" data-n="${q}" aria-pressed="${q === k.e}">${q}</button>`).join('')}</div></div>`
        + '<div class="blk"><b>勝者の 獲得コイン</b><small>勝った 人への プレゼント。参加コインの 2倍 まで</small>'
        + `<div class="cbstp"><button type="button" data-cb="stkw" data-d="-1"${k.w <= k.e ? ' disabled' : ''} aria-label="1枚 へらす">−</button><b aria-live="polite">${k.w}<small>枚</small></b><button type="button" data-cb="stkw" data-d="1"${k.w >= k.e * 2 ? ' disabled' : ''} aria-label="1枚 ふやす">＋</button></div></div></div>`
        + '<p class="hint">同点の ときは 参加コインが もどるよ。<br>とちゅうで やめると、参加コインは もどらないよ</p>'
        + `<button type="button" class="cbb" data-cb="stkgo">${k.e > 0 ? `参加 ${k.e}枚・勝者 ${k.w}枚で 部屋を 作る` : 'コインなしで 部屋を 作る'}</button>`;
      e.innerHTML = h; return;
    }
    if (r.mode === 'host') {
      h += '<h2 class="gold">部屋を 作ったよ</h2><p>この 番号を 友だちに 教えてね</p>' + `<div class="num" aria-label="部屋番号 ${r.code}">${r.code}</div>`
        + (r.stake && r.stake.e > 0 ? `<p class="cbstkl">${COINI}参加コイン <b>${r.stake.e}枚</b>・勝者 <b>${r.stake.w}枚</b></p>` : '')
        + `<div class="stt">${r.step === 'found' ? '<i class="cbspin"></i>友だちが 来たよ！ つないで いるよ…' : r.step === 'fail' ? '部屋を 作れなかったよ' : '<i class="cbspin"></i>友だちを 待って いるよ…'}</div>`
        + '<p class="hint">友だちは「部屋に 入る」で この 番号を 入れるよ。<br>近くに いる 友だちと 直接 つながるよ（2人とも Wi‑Fi か Bluetooth を オンに）</p>';
      if (r.step === 'fail') h += '<button type="button" class="cbb" data-cb="roomre">もう一度 作る</button>';
    } else {
      const busy = r.step === 'wait' || r.step === 'found';
      h += '<h2 class="gold">部屋に 入る</h2><p>友だちの 部屋番号（4けた）を 入れてね</p>' + `<div class="num in" aria-label="部屋番号 ${r.code}">${digits(r.code)}</div>`
        + `<div class="stt">${r.step === 'found' ? '<i class="cbspin"></i>部屋を 見つけたよ！ つないで いるよ…' : r.step === 'wait' ? '<i class="cbspin"></i>部屋を さがして いるよ…' : r.step === 'fail' ? '部屋に 入れなかったよ' : ''}</div>`;
      if (busy) h += '<p class="hint">見つからない ときは、番号と、2人とも Wi‑Fi か Bluetooth が オンか たしかめてね</p>';
      else h += '<div class="cbkeys">' + ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'del', '0', 'go'].map(k => (k === 'del' ? '<button type="button" data-key="del" aria-label="1字 消す">⌫</button>' : k === 'go' ? `<button type="button" data-key="go" aria-label="入る"${r.code.length === 4 ? '' : ' disabled'}>入る</button>` : `<button type="button" data-key="${k}">${k}</button>`)).join('') + '</div>';
    }
    if (r.slow) h += '<p class="hint">つながらない とき：iPhone の「設定」→「テンゲル」→「ローカルネットワーク」を オンに してね</p>';
    e.innerHTML = h;
  }
  function roomStop() { if (room) { clearTimeout(room.tm); if (room.nr) { try { room.nr.cancel(); } catch (e) { /* なし */ } } } room = null; }
  function roomGo() {
    const r = room; if (!r) return;
    r.step = 'wait'; r.slow = false; paintRoom();
    clearTimeout(r.tm); r.tm = setTimeout(() => { if (room === r) { r.slow = true; paintRoom(); } }, 20000);
    const nr = (CBApp._link || CBNet.nativeRoom)(); r.nr = nr;
    nr.open(r.mode, r.code, step => { if (room !== r) return; r.step = step; paintRoom(); }).then(link => {
      if (room !== r) { try { link.close(); } catch (e) { /* なし */ } return; }
      clearTimeout(r.tm); room = null; se('join');
      const dz = { b: st.back, f: Object.assign({}, st.face) };      // 第4.183版：自分が えらんだ デザイン（部屋の あいさつで 友だちに 送る）
      startMatch(r.mode === 'host' ? CBNet.host(link, CBApp._rng || undefined, CBApp._opt || undefined, r.stake, dz) : CBNet.guest(link, dz));
    }).catch(e => {
      if (room !== r) return;
      clearTimeout(r.tm); r.step = 'fail'; r.nr = null; paintRoom();
      if (e && e.message === 'none') toast('この 端末では 部屋を 使えないよ', 3);
    });
  }
  function roomKey(k) {
    const r = room; if (!r || r.mode !== 'join' || r.step === 'wait' || r.step === 'found') return;
    if (k === 'del') r.code = r.code.slice(0, -1);
    else if (k === 'go') { if (r.code.length === 4) roomGo(); return; }
    else if (r.code.length < 4) r.code += k;
    r.step = ''; se('tap', 0.6); paintRoom();
  }

  // ---------- 対戦 ----------
  let match = null, V = null, queue = [], pumping = false, mode = { k: 'idle' }, busy = false, lock = false, ended = false, gameNo = 0;
  const WHO = () => (match && match.kind === 'cpu' ? 'コンピュータ' : 'ともだち');
  function startMatch(m) {
    match = m; V = null; queue = []; pumping = false; mode = { k: 'idle' }; busy = false; lock = false; ended = false;
    m.onUpdate = u => { queue.push(u); pump(); };
    m.onState = s => onNet(s);
    show('game'); closeMod();
    $('.cbopp .cbwho b').textContent = WHO();
    paintEmpty(); layout();
    m.start();
    if (m.kind === 'guest') say('相手を 待って いるよ…');
    else if (m.kind === 'host') say(m.stake && m.stake.e > 0 ? `${WHO()}が 参加するか えらんで いるよ…` : '相手を 待って いるよ…');      // 第4.179版：友だちが 部屋の 決まりを 見て「参加する」と 答える まで 配らない
  }
  // 部屋の 決まり（参加コイン・勝者の 獲得コイン）が 届いた（部屋に 入った 人）：コインなしの 部屋は すぐ 参加・コインの 部屋は 聞く（足りなければ 入れない）
  function joinAsk() {
    const m = match; if (!m || m.kind !== 'guest' || !m.stake) return;
    const k = m.stake;
    if (k.e <= 0) { m.join(); return; }
    const need = k.e - st.coin;
    modal(`<h3 class="gold">この 部屋の 決まり</h3><div class="cbstkv">${COINI}参加コイン <b>${k.e}枚</b><i>→</i>勝者 <b>${k.w}枚</b></div>`
      + `<p>2人とも はじめに ${k.e}枚 出すよ。勝った 人は ${k.w}枚 もらえる。<br>同点は もどる・とちゅうで やめると もどらないよ</p>`
      + `<p class="cbhave">${COINI}あなたの バトルコイン <b>${st.coin}</b>枚${need > 0 ? `<br><strong>あと ${need}枚 足りない ので、この 部屋には 入れないよ</strong>` : ''}</p>`
      + (need > 0 ? '<div class="col"><button type="button" class="cbb" data-cb="joinno">メニューへ</button></div>'
        : '<div class="rowb"><button type="button" class="cbb dk" data-cb="joinno">やめる</button><button type="button" class="cbb" data-cb="joinyes">参加する</button></div>'), 'cbjoin');
  }
  function onNet(s) {
    if (!match) return;
    if (s === 'again') { if (ended) { const e = $('.cbend .gift2'); if (e) e.textContent = WHO() + 'が「もう 1回」を 押したよ'; } return; }
    if (s === 'ready') { opPre(); return; }            // 第4.183版：友だちの デザインが 届いた → 絵を 先に 読む
    if (s === 'joined') return;
    if (s === 'stake') return joinAsk();
    const playing = !ended && !!V;
    const why = s === 'bye' ? WHO() + 'が 部屋を 出たよ' : s === 'ver' ? 'アプリの 版が ちがうので 対戦できないよ。\n2人とも 新しい 版に してね' : 'つながりが 切れたよ';
    // 参加コイン（第4.179版）：相手が とちゅうで やめた → 勝者の 獲得コインを もらう／つながりが 切れた → 参加コインが もどる
    let coinMsg = '';
    if (st.stake) {
      const k = st.stake; st.stake = null;
      if (s === 'bye') { addCoin(k.w); coinMsg = `${WHO()}が とちゅうで やめた ので、バトルコイン ${k.w}枚を もらったよ`; } else { addCoin(k.e); coinMsg = `参加コイン ${k.e}枚は もどったよ`; }
      save();
    }
    if (st.ms.live) { st.ms.live = ''; save(); }      // 第4.183版：ミッションの 連勝は 数えない（そのまま）
    match = null; queue = [];
    modal(`<h3 class="gold">${s === 'ver' ? '対戦できないよ' : '対戦は ここまで'}</h3><p>${esc(why).replace(/\n/g, '<br>')}${playing ? '<br>（この 対戦は 勝ち負けに 数えないよ）' : ''}${coinMsg ? `<br>${COINI}${esc(coinMsg)}` : ''}</p><div class="col"><button type="button" class="cbb" data-cb="menu">メニューへ</button></div>`);
  }
  function opPre() { [null, 'k', 'm', '1', '2', '3', '4', '5', '6', '7'].forEach(k => [false, true].forEach(big => { const im = new Image(); im.src = pic(k, big, 'op'); })); }
  async function pump() {
    if (pumping) return; pumping = true;
    try {
      while (queue.length && match) {
        const u = queue.shift();
        await play(u.ev, u.view);
        if (!match) break;
        V = u.view; lock = false; keepMode(); render();
      }
    } finally { pumping = false; }
    if (match && !queue.length) match.idle();
  }
  // 効果タイム：使える 効果を 1つ ずつ 聞く（6 → 5 → 7 → 3 → 4 の 順。5 の 効果で 7（3）を 捨てて 3まい なくなる ときは 7（3）を 聞かない）
  //   第4.177版（まさちゃん 2026/11/16 10:40）：3 の 効果（3 を 3まい 見せて 1まいを 交換）を 足した
  const EFFQ = ['6', '5', '7', '3', '4'];
  const EFFTXT = { 6: '6 を 2まい 見せて、相手の 手札を 1まい 見られるよ', 5: '5 と 手札 1まいを 捨てて、山札から 1まい セットできるよ', 7: '7 を 3まい 山札に もどして、新しく 3まい 引けるよ',
    3: '3 を 3まい 見せて、その 1まいと 相手の 手札の 1まい（ランダム）を 交換できるよ', 4: '4 を 見せて、相手に カードを 交換させるよ' };
  const EFFBAR = { 3: '3 を 3まい 見せて、手札を 1まい 交換できるよ' };      // 下の 行（2行ぶんの 高さ）に 出す 短い 文（ない ものは EFFTXT と 同じ）
  // 逆転勝利（第4.178版）の 文：k＝自分が 出した カード（1／2）・o＝相手の カード（神様馬・幻の馬／1）
  const toName = o => (NAMES[o] ? NAMES[o] + 'に' : o + ' に');
  const REVTXT = (k, o) => `手札の ${k} を 2まい 見せて、1まい 捨てると、${toName(o)} 勝てるよ`;
  const REVBAR = (k, o) => `手札の ${k} を 1まい 捨てて、${toName(o)} 勝てるよ`;
  function effOk(q, v, use) {
    const c = v.can.eff; if (!c) return false;
    const three = k => v.my.hand.filter(x => x.k === k && x.u !== use.u5).length >= 3;
    return q === '6' ? c.e6 : q === '5' ? c.e5 : q === '7' ? c.e7 && three('7') : q === '3' ? !!c.e3 && three('3') : c.e4;
  }
  function effNext(v, use, after) { for (let i = EFFQ.indexOf(after) + 1; i < EFFQ.length; i++) if (effOk(EFFQ[i], v, use)) return EFFQ[i]; return null; }
  // 1つ 答えた：次の 効果を 聞く。もう なければ、えらんだ ものを まとめて 送る（送ったら 決め直せない）
  function effStep() {
    const nx = effNext(V, mode.use, mode.q);
    if (nx) { mode.q = nx; mode.step = 'ask'; render(); return; }
    const use = mode.use; send({ t: 'eff', use: use });
  }
  // えらんで いる とちゅう（効果タイムの 答え・幻の馬で 捨てる 2まい）は、相手の 動きが 届いても 消さない（もう できなく なった とき だけ もどす）
  function keepMode() {
    const v = V, has = u => v.my.hand.some(c => c.u === u);
    if (mode.k === 'eff') { if (!v.can.eff) mode = { k: 'idle' }; }
    else if (mode.k === 'dropm') { if (v.pend && v.pend.mine && v.pend.type === 'm') mode.sel = mode.sel.filter(has); else mode = { k: 'idle' }; }
    else if (mode.k === 'u5') { if (!(v.pend && v.pend.mine && v.pend.type === 'u5')) mode = { k: 'idle' }; }
    else mode = { k: 'idle' };
  }
  const sortHand = h => h.slice().sort((a, b) => power(a.k) - power(b.k) || a.u - b.u);
  const cardBtn = (c, cls, extra, side) => `<button type="button" class="cbc ${cls || ''}" data-u="${c.u}" data-ck="${c.k ? esc(c.k) : ''}"${extra || ''} aria-label="${c.k ? esc(nameOf(c.k)) + ' の カード' : 'ふせた カード'}"><img src="${pic(c.k, false, side)}" alt="" draggable="false">${c.seen ? '<i class="eye" aria-hidden="true"></i>' : ''}</button>`;
  function pips(n, turns) { let h = ''; for (let i = 0; i < turns; i++) h += `<i class="${i < n ? 'on' : ''}"></i>`; return h; }
  const turnsOf = () => (V && V.turns) || R.TURNS;      // この 対戦の ターンの 数（ふだんは 5。テストでは 3 の 場面も ある）
  function deckImg() { const im = $('.cbdeck img'), f = deckPic(); if (im && im.getAttribute('src') !== f) im.setAttribute('src', f); }      // 第4.182版：山札の 絵＝えらんだ うら
  function paintEmpty() {
    $('.cbturn').innerHTML = ''; $('.cbohand').innerHTML = ''; $('.cbhand').innerHTML = ''; $('.cbact').innerHTML = ''; say('');
    deckImg(); $('.cbslot.op').innerHTML = ''; $('.cbslot.my').innerHTML = ''; $('.cbdeck .cbn').textContent = ''; $('.cbdis .cbn').textContent = '';
    ov.querySelectorAll('.cbpips').forEach(e => { e.innerHTML = pips(0, turnsOf()); });
    $('.cbglow').classList.remove('on');
  }
  function layout() {
    if (screen !== 'game') return;
    const hd = $('.cbhand'), n = Math.max(1, hd.children.length), r = hd.getBoundingClientRect();
    if (r.width > 0) {
      const W = r.width - 12, H = r.height - 30, LAP = 0.4;       // 重なりは 40% まで（左上の 数字と 絵は 見える。字は タップして 大きく 読む）。第4.178版：手札 7まい → 30% だと カードが 小さい（幅 70px）ので 40%（幅 79px・見える 所 47px）
      let w = Math.max(50, Math.min(100, Math.floor(H * 2 / 3)));
      let lap = n > 1 ? Math.max(0, (n * w - W) / (n - 1)) : 0;
      if (lap > w * LAP) { w = Math.floor(W / (n - (n - 1) * LAP)); lap = w * LAP; }
      hd.style.setProperty('--cw', w + 'px'); hd.style.setProperty('--ov', (lap > 0 ? -lap : Math.min(6, (W - n * w) / Math.max(1, n - 1))).toFixed(1) + 'px');
    }
    const oh = $('.cbohand'), q = oh.getBoundingClientRect();
    if (q.height > 0) oh.style.setProperty('--ow', Math.max(30, Math.min(58, Math.floor((q.height - 4) * 2 / 3))) + 'px');
  }
  // ことばの 行（.cbmsg）に 字を 入れる。行の 高さは 決まって いる（2行ぶん：まさちゃん 2026/11/16 10:40「説明の文字が二行になると画面が上下して、不自然」→ 何行でも まわりは 動かない）。
  //   2行に 入らない ほど 長い とき（幅の せまい 画面）は、入る まで 字を 少し 小さく する（13.5px → 10.5px まで）
  function say(t) {
    const m = $('.cbmsg'); if (!m) return;
    m.style.fontSize = ''; m.textContent = t || '';
    if (!t) return;
    let fs = 13.5;
    while (m.scrollHeight > m.clientHeight + 0.5 && fs > 10.5) { fs -= 0.5; m.style.fontSize = fs + 'px'; }
  }
  function statusText(v) {
    if (v.phase === 'end') return '';
    const w = WHO();
    if (v.pend) {
      const me = v.pend.mine;
      if (v.pend.type === 'swap') return me ? `${w}が 4 の 効果を 使ったよ！\nセットした カードと 交換する 手札を えらんでね` : `${w}が カードを 交換して いるよ…`;
      if (v.pend.type === 'u5' && me) return '交換で 5 を セットしたよ！ 5 の 効果を 使う？\n5 と 手札 1まいを 捨てて、山札から 1まい セットできるよ';      // 第4.183版
      if (v.pend.type === 'k') return me ? '神様馬で 勝った！ 効果を 使う？\n相手の 手札を 1まい 見られるよ' : `${w}が 神様馬の 効果を 使うか えらんで いるよ…`;
      if (v.pend.type === 'm') return me ? '幻の馬で 勝った！ 効果を 使う？\n手札を 2まい 捨てて、山札から 2まい 引けるよ' : `${w}が 幻の馬の 効果を 使うか えらんで いるよ…`;
      if (v.pend.type === 'rev') return me && v.my.set && v.op.set ? `逆転の チャンス！ ${v.my.set.k} の 効果を 使う？\n${REVBAR(v.my.set.k, v.op.set.k)}` : `${w}が 逆転勝利を 使うか えらんで いるよ…`;
    }
    if (v.phase === 'eff') return `${w}が 効果を 使うか えらんで いるよ…`;
    if (v.can.set) return v.op.set ? `${w}は もう セットしたよ。セットする カードを えらんでね` : 'セットする カードを えらんでね（カードを タップ）';
    return `${w}が えらんで いるよ…`;
  }
  // ボードの 捨て札：1番 上（さいごに 捨てた カード）と 数
  function paintDis(list) {
    const top = list.length ? list[list.length - 1] : null;
    $('.cbdis .pl').innerHTML = top ? `<img src="${pic(top.k, false, top.mine === false ? 'op' : 'my')}" alt="" draggable="false">` : '';      // 第4.183版：だれの カードか（友だちとの 対戦は その 人の デザイン）
    $('.cbdis .cbn').textContent = String(list.length);
    $('.cbdis').setAttribute('aria-label', `捨て札を 見る（${list.length}まい）`);
  }
  const setTag = (s, mine) => { const t = s.open ? '' : s.up ? '4 の 効果' : !mine ? '' : s.blind ? '山札から' : 'セット ずみ'; return t ? `<span class="tag">${t}</span>` : ''; };
  function render() {
    const v = V; if (!v || screen !== 'game') return;
    if (v.can.eff && mode.k !== 'eff') { const q = effNext(v, {}, null); mode = q ? { k: 'eff', use: {}, q: q, step: 'ask' } : { k: 'idle' }; }      // 効果タイム：1つ目から 聞く
    $('.cbturn').innerHTML = v.phase === 'end' ? 'けっか' : `ターン ${v.turn}<small>／${v.turns}</small>` + (st.stake ? `<small class="stk">${COINI}勝者 ${st.stake.w}枚</small>` : '');
    $('.cbpips[data-p=op]').innerHTML = pips(v.op.wins, v.turns); $('.cbpips[data-p=my]').innerHTML = pips(v.my.wins, v.turns);
    $('.cbohand').innerHTML = v.op.hand.map(c => cardBtn({ u: c.u, k: c.k }, c.k ? 'knw' : '', ' data-cb="ocard"', 'op')).join('');
    deckImg(); $('.cbdeck .cbn').textContent = String(v.deckN); paintDis(v.discard);
    const os = v.op.set, ms = v.my.set;
    $('.cbslot.op').innerHTML = os ? cardBtn({ u: os.u, k: os.k }, '', ' data-cb="oset"', 'op') + setTag(os, false) : '';
    $('.cbslot.my').innerHTML = ms ? cardBtn({ u: ms.u, k: ms.k }, '', ' data-cb="mset"') + setTag(ms, true) : '';
    $('.cbglow').classList.toggle('on', v.can.set || !!(v.pend && v.pend.mine && v.pend.type === 'swap'));
    const asking = askSync();                          // 効果を 使うか 聞く 窓（下の askSync）：出て いる 間、下の ボタンは 出さない（同じ ボタンを 2か所に 出さない）
    paintHand(); paintAct(asking);
    say(asking ? '効果を 使うか えらんでね' : (modeText() || statusText(v)));
    layout();
  }
  function modeText() {
    if (mode.k === 'eff') return mode.step === 'drop5' ? '5 と いっしょに 捨てる カードを えらんでね（カードを タップ）' : `効果タイム！ ${mode.q} の 効果を 使う？\n${EFFBAR[mode.q] || EFFTXT[mode.q]}`;
    if (mode.k === 'dropm') return `捨てる カードを 2まい えらんでね（${mode.sel.length}／2）`;
    if (mode.k === 'u5') return '5 と いっしょに 捨てる カードを えらんでね（カードを タップ）';      // 第4.183版：交換で 出した 5 の 効果
    return '';
  }
  // 手札を かく（list＝動かして いる とちゅうの 手札。なければ いまの 形の 手札）
  function paintHand(fresh, list) {
    const hd = $('.cbhand');
    hd.innerHTML = sortHand(list || V.my.hand).map(c => cardBtn(c, (mode.k === 'dropm' && mode.sel.indexOf(c.u) >= 0 ? 'sel ' : '') + (fresh && fresh.indexOf(c.u) >= 0 ? 'new' : ''), ' data-cb="card"')).join('');
  }
  function paintAct(asking) {
    const v = V, a = $('.cbact'); let h = '';
    const two = (no, yes, yesText) => `<button type="button" class="cbb dk sm" data-cb="${no}">使わない</button><button type="button" class="cbb sm" data-cb="${yes}">${yesText}</button>`;
    if (asking) h = '';
    else if (mode.k === 'eff') h = mode.step === 'drop5' ? '<button type="button" class="cbb dk sm" data-cb="effback">もどる</button>' : two('effno', 'effyes', `${mode.q} の 効果を 使う`);
    else if (mode.k === 'dropm') h = `<button type="button" class="cbb dk sm" data-cb="modex">もどる</button><button type="button" class="cbb sm" data-cb="mgo"${mode.sel.length === 2 ? '' : ' disabled'}>この 2まいを 捨てて 引く</button>`;
    else if (v.pend && v.pend.mine && v.pend.type === 'k') h = two('kskip', 'kgo', '神様馬の 効果を 使う');
    else if (v.pend && v.pend.mine && v.pend.type === 'm') h = two('mskip', 'mpick', '幻の馬の 効果を 使う');
    else if (v.pend && v.pend.mine && v.pend.type === 'rev' && v.my.set) h = two('revno', 'revyes', `${v.my.set.k} の 効果を 使う`);
    else if (mode.k === 'u5') h = '<button type="button" class="cbb dk sm" data-cb="u5back">もどる</button>';
    else if (v.pend && v.pend.mine && v.pend.type === 'u5') h = two('u5no', 'u5yes', '5 の 効果を 使う');
    a.innerHTML = h;
  }

  // ---------- 前に 出す 窓 ----------
  function modal(html, cls) { modEl.className = 'cbmod on ' + (cls || ''); modEl.innerHTML = html; }
  function closeMod() { if (modEl) { modEl.className = 'cbmod'; modEl.innerHTML = ''; } }
  const modOn = () => modEl.classList.contains('on');
  // 効果を 使うか 聞く 窓（第4.177版・まさちゃん 2026/11/16 10:40「カードの効果は使うか使わないか選べるようにして！」）：
  //   前は 画面の 下の 小さい 字と 小さい ボタン 2つ だけ だった（気づきにくい）→ 効果を 使える ときは、まん中に カードの 絵・「○ の 効果を 使う？」・大きい「使わない」「使う」を 出す。
  //   ・効果タイム（7・6・5・4・3：1つ ずつ 聞く）と、神様馬・幻の馬で 勝った 次の ターンの はじめ の どちらも 同じ 窓。第4.178版：オープンして 負けた ときの 逆転勝利（1・2）も 同じ 窓
  //   ・「手札と ボードを 見る」で 窓を 下げられる（その あとは 画面の 下の「使わない」「○ の 効果を 使う」で 答える：前と 同じ 形）
  //   ・カードや 捨て札の 窓を 見て いる とちゅうには 重ねない（その 窓を 閉じた ときに 出す）
  let peekId = '';
  // うっかり 押し 防止（第4.177版の あと：次の 版に 入る）：聞く 窓が 出て から ASK_GUARD ミリ秒は、窓の 中の 答え（使わない／使う）を 押しても 受けつけない。
  //   ・効果が 2つ つづけて 聞かれる とき（例：5 と 7）、1つ目の 答えを すばやく 2回 押すと、同じ 所に すぐ 出る 2つ目の 窓まで 同じ 答えに なって いた（2つ目を えらべない）
  //   ・カードを 大きく 見る 窓を 閉じた しゅんかん・相手が セットした しゅんかんに 窓が 出ると、指の 下に 答えの ボタンが 来る ことが ある
  //   「手札と ボードを 見る」は すぐ 押せる（何も 決まらない）。CBApp._guard＝テスト用（数字を 入れると その ミリ秒）
  const ASK_GUARD = 350;
  let askAt = 0;
  function askInfo() {
    const v = V; if (!v || ended || !match) return null;
    if (mode.k === 'eff' && mode.step === 'ask') return { id: `e${gameNo}.${v.turn}.${mode.q}`, k: mode.q, head: '効果タイム！', q: `${mode.q} の 効果を 使う？`, text: EFFTXT[mode.q], yes: 'effyes', no: 'effno' };
    if (mode.k === 'idle' && v.pend && v.pend.mine && v.pend.type === 'k') return { id: `k${gameNo}.${v.turn}`, k: 'k', head: '神様馬で 勝った！', q: '神様馬の 効果を 使う？', text: '相手の 手札を 1まい 見られるよ', yes: 'kgo', no: 'kskip' };
    if (mode.k === 'idle' && v.pend && v.pend.mine && v.pend.type === 'm') return { id: `m${gameNo}.${v.turn}`, k: 'm', head: '幻の馬で 勝った！', q: '幻の馬の 効果を 使う？', text: '手札を 2まい 捨てて、山札から 2まい 引けるよ', yes: 'mpick', no: 'mskip' };
    if (mode.k === 'idle' && v.pend && v.pend.mine && v.pend.type === 'u5') return { id: `u${gameNo}.${v.turn}`, k: '5', head: '交換で 5 を セット！', q: '5 の 効果を 使う？', text: EFFTXT[5], yes: 'u5yes', no: 'u5no' };      // 第4.183版
    if (mode.k === 'idle' && v.pend && v.pend.mine && v.pend.type === 'rev' && v.my.set && v.op.set) return { id: `r${gameNo}.${v.turn}`, k: v.my.set.k, head: '逆転の チャンス！', q: `${v.my.set.k} の 効果を 使う？`, text: REVTXT(v.my.set.k, v.op.set.k), yes: 'revyes', no: 'revno' };      // 逆転勝利（第4.178版）：オープンして 負けた とき
    return null;
  }
  const askOn = () => !!modEl && modEl.classList.contains('cbask');
  function askSync() {                                 // → 窓が 出て いる なら true
    const A = askInfo();
    if (!A || peekId === A.id || screen !== 'game') { if (askOn()) closeMod(); return false; }
    if (askOn() && modEl.dataset.ask === A.id) return true;
    if (modOn() && !askOn()) return false;
    modal(`<h3 class="gold">${esc(A.head)}</h3><div class="big"><img src="${pic(A.k, true)}" alt="${esc(nameOf(A.k))}"></div><p class="askq"><b>${esc(A.q)}</b>${esc(A.text)}</p>`
      + `<div class="rowb"><button type="button" class="cbb dk lg" data-cb="${A.no}">使わない</button><button type="button" class="cbb lg" data-cb="${A.yes}">使う</button></div>`
      + '<button type="button" class="cbb dk sm" data-cb="askpeek">手札と ボードを 見る</button>', 'cbask');
    modEl.dataset.ask = A.id; askAt = performance.now();
    return true;
  }
  // 手札の カードを タップ：大きい カード ＋ できる こと（セットは「この カードを セットする」を 押したら 確定：もう 変えられない）
  function cardModal(u) {
    const v = V, c = v.my.hand.find(x => x.u === u); if (!c) return;
    let btn = '';
    if (v.pend && v.pend.mine && v.pend.type === 'swap') btn = `<button type="button" class="cbb" data-cb="swap" data-u="${u}">この カードと 交換する</button>`;
    else if (mode.k === 'eff') { if (mode.step === 'drop5') btn = `<button type="button" class="cbb" data-cb="drop5" data-u="${u}">この カードを 捨てる<small>5 と いっしょに 捨てて、山札から 1まい セット</small></button>`; }
    else if (mode.k === 'u5') btn = `<button type="button" class="cbb" data-cb="u5drop" data-u="${u}">この カードを 捨てる<small>5 と いっしょに 捨てて、山札から 1まい セット</small></button>`;      // 第4.183版
    else if (v.can.set) btn = `<button type="button" class="cbb" data-cb="set" data-u="${u}">この カードを セットする<small>セットしたら もう 変えられないよ</small></button>`;
    modal(`<div class="big"><img src="${pic(c.k, true)}" alt="${esc(nameOf(c.k))}"></div>${c.seen ? '<p>この カードは 相手に 見られて いるよ</p>' : ''}<div class="col">${btn}<button type="button" class="cbb dk" data-cb="modx">もどる</button></div>`);
  }
  // 大きい カードを 見る（back＝'discard'：捨て札の 窓から 来た → もどる で 捨て札の 窓へ）
  function showCard(k, text, back, side) { modal(`<div class="big"><img src="${pic(k, true, side)}" alt="${esc(k ? nameOf(k) : 'ふせた カード')}"></div>${text ? `<p>${esc(text)}</p>` : ''}<div class="col"><button type="button" class="cbb dk" data-cb="${back === 'discard' ? 'discard' : 'modx'}">もどる</button></div>`); }
  // 相手の 手札から 1まい えらぶ（6・神様馬の 効果）
  function pickModal(kind) {
    const v = V;
    // 第4.178版（まさちゃん「6.の効果は、もう見てるカードしかない場合は、発動しなくして！」）：えらべるのは まだ 見て いない カード（うら）だけ。もう 見た カード（表・暗く）は 押せない
    const seen = v.op.hand.some(c => c.k);
    modal(`<h3 class="gold">${kind === 'p6' ? '6 の 効果' : '神様馬の 効果'}</h3><p>見たい カードを 1まい えらんでね${kind === 'p6' ? '<br>（手札の 6 を 2まい 相手に 見せるよ）' : ''}${seen ? '<br>もう 見た カードは えらべないよ' : ''}</p>`
      + `<div class="pick">${v.op.hand.map(c => cardBtn({ u: c.u, k: c.k }, c.k ? 'knw' : '', c.k ? ' disabled' : ` data-cb="pick" data-kind="${kind}"`, 'op')).join('')}</div>`
      + '<div class="col"><button type="button" class="cbb dk" data-cb="modx">もどる</button></div>');
  }
  // 捨て札（まさちゃん 23:15）：「終わった ターンの 捨て札」（ターン ごとに 2人の 出した カード）と「効果で 捨てた カード」（5 の 効果・幻の馬の 効果・第4.178版：1・2 の 逆転勝利）に 分けて 見せる。カードは タップで 大きく
  function discardModal() {
    const v = V; if (!v) return;
    const d = v.discard, turns = [], effs = [], w = esc(WHO());
    d.forEach(x => {
      if (x.why === 't') { (turns[x.turn] = turns[x.turn] || []).push(x); return; }
      let g = effs.find(e => e.turn === x.turn && e.why === x.why && e.mine === x.mine);
      if (!g) { g = { turn: x.turn, why: x.why, mine: x.mine, cards: [] }; effs.push(g); }
      g.cards.push(x);
    });
    const card = x => `<button type="button" class="cbc" data-cb="dcard" data-k="${esc(x.k)}" data-sd="${x.mine ? 'my' : 'op'}" aria-label="${esc(nameOf(x.k))} の カード"><img src="${pic(x.k, false, x.mine ? 'my' : 'op')}" alt="" draggable="false"></button>`;
    const pair = (name, cs) => `<div class="pr"><span>${name}</span><div class="cs">${cs.map(card).join('')}</div></div>`;
    let h = `<h3 class="gold">捨て札（${d.length}まい）</h3><div class="cbdl"><h4>終わった ターンの 捨て札</h4>`;
    if (!turns.some(Boolean)) h += '<p class="none">まだ ないよ（ターンが 終わると、出した カードが ここに 来るよ）</p>';
    turns.forEach((cs, n) => { if (cs) h += `<div class="row" data-dt="${n}"><b>ターン ${n}</b>${pair('あなた', cs.filter(x => x.mine))}${pair(w, cs.filter(x => !x.mine))}</div>`; });
    h += '<h4>効果で 捨てた カード</h4>';
    if (!effs.length) h += '<p class="none">まだ ないよ（1・2・5 の 効果・幻の馬の 効果で 捨てた カードが ここに 来るよ）</p>';
    effs.forEach(g => { h += `<div class="row" data-de="${esc(g.why)}"><b>ターン ${g.turn}${g.why === 'm' ? '<small>はじめ</small>' : ''}</b>${pair(`${g.mine ? 'あなた' : w}の ${g.why === 'm' ? '幻の馬の 効果' : esc(g.why) + ' の 効果'}`, g.cards)}</div>`; });      // why＝'5'・'m'・'1'／'2'（逆転勝利で 捨てた：第4.178版）
    h += `</div><p>山札の のこり ${v.deckN}まい</p><div class="col"><button type="button" class="cbb dk" data-cb="modx">もどる</button></div>`;
    modal(h, 'cbdm');
  }
  // 設定の 窓（第4.178版・まさちゃん「プレイボードの右下の設定ボタンを押すと、BGMオンかオフと効果エフェクトオンかオフを選べるようにして！」）：
  //   BGM・効果音・エフェクト（光や 動きの 演出：カードが とぶ・めくる・光が ゆれる）を オン／オフ。えらんだ 形は おぼえる（localStorage 'tengel.cb'）。
  //   「効果エフェクト」が 音の ことか 光や 動きの ことか 決めきれなかった ので、効果音と エフェクトの 2つを 分けて 出した（姫が 決めた 所）。
  //   対戦の 画面（ボードの 歯車）では、前から あった「対戦に もどる・あそび方・対戦を やめる」も 下に ならぶ。メニューの「設定」からも 同じ 窓
  const SETS = [['bgm', 'BGM', '音楽'], ['se', '効果音', 'カードや ボタンの 音'], ['fx', 'エフェクト', '光や 動きの 演出']];
  const setOn = k => (k === 'bgm' ? bgmOn() : k === 'se' ? seOn() : fxOn());
  function gearModal() {
    const rows = SETS.map(([k, name, note]) => { const on = setOn(k); return `<div class="cbsw" data-set="${k}"><span>${name}<small>${note}</small></span><div class="cbseg" role="group" aria-label="${name}">`
      + `<button type="button" class="${on ? 'on' : ''}" data-cb="tg" data-k="${k}" data-v="1" aria-pressed="${on}">オン</button><button type="button" class="${on ? '' : 'on'}" data-cb="tg" data-k="${k}" data-v="0" aria-pressed="${!on}">オフ</button></div></div>`; }).join('');
    const game = screen === 'game' && !!match;
    modal(`<h3 class="gold">設定</h3><div class="cbsws">${rows}</div><div class="col">`
      + (game ? '<button type="button" class="cbb" data-cb="modx">対戦に もどる</button><button type="button" class="cbb dk" data-cb="help">あそび方</button><button type="button" class="cbb dk" data-cb="quit">対戦を やめる</button>' : '<button type="button" class="cbb" data-cb="modx">もどる</button>')
      + '</div>', 'cbset');
  }
  // 設定を かえる：おぼえる → すぐ 効かせる
  function setSet(k, on) {
    if (['bgm', 'se', 'fx'].indexOf(k) < 0) return;
    st[k] = !!on; save(); applySets();
    if (k === 'se' && on) se('tap', 0.8);
    if (modEl.classList.contains('cbset')) gearModal();
  }
  function applySets() { if (ov) ov.classList.toggle('nofx', !fxOn()); bgmSync(); }
  function quitModal() {
    const mid = !ended && !!V;
    modal(`<h3 class="gold">対戦を やめる？</h3><p>${mid ? 'とちゅうで やめると 負けに なるよ（連勝は 0 に もどるよ）' + (st.stake ? `<br>${COINI}参加コイン ${st.stake.e}枚も もどらないよ` : '') : 'メニューに もどるよ'}</p><div class="rowb"><button type="button" class="cbb dk" data-cb="modx">つづける</button><button type="button" class="cbb" data-cb="quitgo">やめる</button></div>`);
  }

  // ---------- 手を 打つ ----------
  // 下の 質問（.cbmsg）と ボタン（.cbact）を かたづける：手を 打った とき・カードを 開く とき。
  //   そのままだと、結果を 見せ終わって かき直す まで 前の 質問と ボタンが のこる（測った：効果タイムで「使わない」を 押して から 5.7秒「6 の 効果を 使う？」が 出た まま
  //   ＝押せて いない ように 見える。その あいだ 押しても 何も おきない）。場所の 高さは CSS で 決まって いる ので、消しても まわりは 動かない
  function hush() { if (screen !== 'game') return; const a = $('.cbact'); if (a) a.innerHTML = ''; say(''); }
  async function send(a) {
    if (busy || !match) return false;
    busy = true; lock = true; closeMod(); hush();      // lock：この 手の 結果（おきた こと）を 見せ終わって かき直す まで、次の 手は 待つ（pump が はずす）
    let r = null;
    try { r = await match.act(a); } catch (e) { r = { ok: false, why: 'err' }; }
    busy = false;
    if (!r || !r.ok) { lock = false; if (match && V) { mode = { k: 'idle' }; render(); toast('その 手は 打てなかったよ', 2); } return false; }
    return true;
  }
  function onClick(e) {
    const key = e.target.closest('[data-key]'); if (key && !key.disabled) return roomKey(key.dataset.key);
    const b = e.target.closest('[data-cb]'); if (!b || b.disabled) return;
    const a = b.dataset.cb, u = +b.dataset.u;
    if (/^(effyes|effno|kgo|kskip|mpick|mskip|revyes|revno|u5yes|u5no)$/.test(a) && b.closest('.cbask') && performance.now() - askAt < (typeof CBApp._guard === 'number' ? CBApp._guard : ASK_GUARD)) return;      // 聞く 窓が 出て すぐ：受けつけない（上の ASK_GUARD）
    if (a === 'close') return close();
    if (a === 'cpu') { se('tap'); return startMatch(CBNet.cpu(CBApp._rng || undefined, CBApp._think || undefined, CBApp._opt || undefined)); }
    if (a === 'host' || a === 'join') { se('tap'); return showRoom(a); }
    if (a === 'dz') { se('tap'); return showDz('f'); }      // 第4.182版：デザインカスタム
    if (a === 'dzx') return showMenu();
    if (a === 'dztab') { se('tap', 0.6); return showDz(b.dataset.t === 'b' ? 'b' : 'f'); }
    if (a === 'dzi') { se('tap', 0.6); return dzItem(b.dataset.ck || null, b.dataset.id || ''); }
    if (a === 'dzback') return closeMod();
    if (a === 'dzopen') return dzAsk(b.dataset.ck || null, b.dataset.id || '');
    if (a === 'dzgo') { if (performance.now() - dzAt < (typeof CBApp._guard === 'number' ? CBApp._guard : DZ_GUARD)) return; return dzGo(b.dataset.ck || null, b.dataset.id || ''); }
    if (a === 'dzuse') return dzUse(b.dataset.ck || null, b.dataset.id || '');
    if (a === 'tst') { if (testOn()) window.CBTest.act(b.dataset.t, dzApi); return; }
    if (a === 'ms') { se('tap'); return showMs(); }      // 第4.183版：ミッション
    if (a === 'msx') return showMenu();
    if (a === 'mstab') { se('tap', 0.6); return showMs(b.dataset.t === 'fr' ? 'fr' : 'cpu'); }
    if (a === 'tstm') { if (testOn() && window.CBTest.msAct) window.CBTest.msAct(b.dataset.t, msApi); return; }
    if (a === 'help') return showHelp(screen === 'game' ? 'game' : 'menu');
    if (a === 'helpx') { show(helpBack); if (helpBack === 'game') render(); return; }
    if (a === 'roomx') { roomStop(); return showMenu(); }
    if (a === 'roomre') return showRoom('host', true);
    if (a === 'stke') return stakeSet('e', +b.dataset.n);
    if (a === 'stkw') return stakeSet('w', +b.dataset.d);
    if (a === 'stkgo') { const r = room; if (!r || r.step !== 'stake') return; se('tap'); r.step = ''; paintRoom(); return roomGo(); }
    if (a === 'joinyes') { const m = match; if (!m || m.kind !== 'guest' || !m.stake || st.coin < m.stake.e || V) return; se('tap'); closeMod(); m.join(); say('相手を 待って いるよ…'); return; }
    if (a === 'joinno') { leave(false); return showMenu(); }
    if (a === 'menu') { leave(false); return showMenu(); }
    if (a === 'modx') { closeMod(); if (match && V && screen === 'game' && !busy && !lock && askInfo()) render(); return; }      // 閉じた 所で、聞く ことが あれば 聞く 窓を 出す
    if (a === 'askpeek') { const A = askInfo(); if (A) peekId = A.id; closeMod(); if (V && screen === 'game') render(); return; }      // 聞く 窓を 下げて 手札と ボードを 見る（答えは 下の ボタンで）
    if (a === 'gear') { se('tap', 0.6); return gearModal(); }
    if (a === 'tg') return setSet(b.dataset.k, b.dataset.v === '1');
    if (a === 'quit') return quitModal();
    if (a === 'quitgo') { leave(true); return showMenu(); }
    if (a === 'again') return again();
    if (a === 'discard') { if (modEl.classList.contains('cbopen')) return; return discardModal(); }
    if (a === 'dcard') { const k = b.dataset.k; if (R.KINDS.indexOf(k) >= 0) showCard(k, '捨て札の カード', 'discard', b.dataset.sd === 'op' ? 'op' : 'my'); return; }
    if (!match || !V || busy || lock || ended || modEl.classList.contains('cbopen')) return;
    const v = V;
    if (a === 'ocard' || a === 'oset') { const c = a === 'oset' ? v.op.set : v.op.hand.find(x => x.u === u); if (c && c.k) showCard(c.k, a === 'oset' ? '相手が セットした カード' : '効果で 見た 相手の カード', '', 'op'); return; }
    if (a === 'mset') { const c = v.my.set; if (c) showCard(c.k, c.open ? 'あなたが セットした カード' : c.blind ? '山札から 来た カード（オープンまで わからない）' : c.up ? '4 の 効果で 見せた カード' : 'あなたが セットした カード（相手には 見えない・もう 変えられない）'); return; }
    if (a === 'card') {
      if (mode.k === 'dropm') { const j = mode.sel.indexOf(u); if (j >= 0) mode.sel.splice(j, 1); else if (mode.sel.length < 2) mode.sel.push(u); se('tap', 0.6); paintHand(); paintAct(); say(modeText()); layout(); return; }
      se('tap', 0.6); return cardModal(u);
    }
    if (a === 'set') { if (!v.can.set || mode.k !== 'idle') return; return send({ t: 'set', u: u }); }
    // 効果タイム：「使う」「使わない」を 1つ ずつ 答える
    if (a === 'effyes' || a === 'effno' || a === 'effback' || a === 'drop5') {
      if (mode.k !== 'eff' || !v.can.eff) return;
      se('tap', 0.6);
      if (a === 'effback') { mode.step = 'ask'; closeMod(); render(); return; }
      if (a === 'effno') { if (mode.step !== 'ask') return; return effStep(); }
      if (a === 'drop5') { if (mode.step !== 'drop5' || !v.my.hand.some(c => c.u === u)) return; mode.use.u5 = u; closeMod(); return effStep(); }
      if (mode.step !== 'ask') return;
      if (mode.q === '6') return pickModal('p6');
      if (mode.q === '5') { mode.step = 'drop5'; render(); return; }
      if (mode.q === '7') mode.use.x7 = true; else if (mode.q === '3') mode.use.x3 = true; else mode.use.u4 = true;
      return effStep();
    }
    if (a === 'modex') { mode = { k: 'idle' }; render(); return; }
    if (a === 'kgo') return pickModal('k');
    if (a === 'pick') {
      if (!v.op.hand.some(c => c.u === u && !c.k)) return;      // まだ 見て いない カード だけ
      if (b.dataset.kind === 'p6') { if (mode.k !== 'eff' || mode.q !== '6') return; mode.use.p6 = u; closeMod(); return effStep(); }
      return send({ t: 'k', pick: u });
    }
    if (a === 'kskip') return send({ t: 'k', pick: null });
    if (a === 'mskip') return send({ t: 'm', drop: null });
    if (a === 'mpick') { mode = { k: 'dropm', sel: [] }; render(); return; }
    if (a === 'mgo') { if (mode.k === 'dropm' && mode.sel.length === 2) return send({ t: 'm', drop: mode.sel.slice() }); return; }
    if (a === 'swap') return send({ t: 'swap', u: u });
    // 第4.183版：交換で 出した 5 の 効果（使う → 捨てる カードを えらぶ／使わない）
    if (a === 'u5yes') { if (!(v.pend && v.pend.mine && v.pend.type === 'u5') || mode.k !== 'idle') return; se('tap', 0.6); closeMod(); mode = { k: 'u5' }; render(); return; }
    if (a === 'u5no') { if (!(v.pend && v.pend.mine && v.pend.type === 'u5')) return; se('tap', 0.6); return send({ t: 'u5', drop: null }); }
    if (a === 'u5back') { if (mode.k === 'u5') { mode = { k: 'idle' }; render(); } return; }
    if (a === 'u5drop') { if (mode.k !== 'u5' || !v.my.hand.some(c => c.u === u)) return; closeMod(); return send({ t: 'u5', drop: u }); }
    if (a === 'revyes' || a === 'revno') { if (!(v.pend && v.pend.mine && v.pend.type === 'rev') || mode.k !== 'idle') return; se('tap', 0.6); return send({ t: 'rev', use: a === 'revyes' }); }      // 逆転勝利（第4.178版）
  }

  // ---------- 動き（おきた こと を 順に 見せる）----------
  const box = el => { const r = el.getBoundingClientRect(), o = ov.getBoundingClientRect(); return { x: r.left - o.left, y: r.top - o.top, w: r.width, h: r.height }; };
  const mid = (b, w) => ({ x: b.x + b.w / 2 - w / 2, y: b.y + b.h / 2 - w * 0.75, w: w, h: w * 1.5 });      // 箱の まん中に 置いた 幅 w の カード
  function fly(k, from, to, ms, fade, side) {      // side＝だれの カード（第4.183版：友だちとの 対戦の 相手の カードは 相手の デザイン）
    if (reduce() || !from || !to || !from.w || !to.w) return T(40);
    const im = document.createElement('img'); im.src = pic(k, false, side); im.alt = ''; im.className = 'cbfl';
    im.style.cssText = `left:${from.x}px;top:${from.y}px;width:${from.w}px;height:${from.h}px`;
    flyEl.appendChild(im);
    const dx = to.x + to.w / 2 - (from.x + from.w / 2), dy = to.y + to.h / 2 - (from.y + from.h / 2), sc = to.w / from.w, d = Math.max(1, ms * SPEED);
    return new Promise(ok => {
      let done = false; const fin = () => { if (done) return; done = true; im.remove(); ok(); };
      const go = () => { im.style.transition = `transform ${d}ms cubic-bezier(.25,.7,.25,1),opacity ${d}ms`; im.style.transform = `translate(${dx}px,${dy}px) scale(${sc})`; if (fade) im.style.opacity = '0'; };
      if (clk.manual) { void im.offsetWidth; go(); } else requestAnimationFrame(go);
      later(fin, d + 60);
    });
  }
  const slotBox = side => box($('.cbslot.' + side));
  const handBox = side => box(side === 'my' ? $('.cbhand') : $('.cbohand'));
  const deckBox = () => box($('.cbdeck'));
  const disBox = () => box($('.cbdis'));
  const cardBox = (side, u) => { const e = (side === 'my' ? $('.cbhand') : $('.cbohand')).querySelector(`[data-u="${u}"]`); return e ? box(e) : null; };
  // カードを めくって 大きく 見せる（オープン）
  //   第4.178版：逆転勝利を 使える 人が いる とき（x.rev＝'me'／'op'）は、勝ち負けを まだ 出さない（色・音・しるしは 決まって から：下の 'fin'）
  async function openShow(x) {
    const hold = x.rev === 'me' || x.rev === 'op';
    const txt = x.rev === 'me' ? ['チャンス！', `${nameOf(x.op.k)} の ほうが 強い…でも ${x.my.k} の「逆転勝利」を 使えるよ`] : x.rev === 'op' ? ['勝負は まだ！', `${WHO()}は ${x.op.k} の「逆転勝利」を 使えるよ`]
      : x.res === 'win' ? ['勝ち！', `${nameOf(x.my.k)} が ${nameOf(x.op.k)} に 勝ったよ`] : x.res === 'lose' ? ['負け…', `${nameOf(x.op.k)} の ほうが 強いよ`] : x.res === 'clash' ? ['かぶり！', `同じ カード（${nameOf(x.my.k)}）＝どちらも 負け`] : x.d4 ? ['ドロー！', 'どちらも 4 の 効果を 使った ので 引き分け'] : ['引き分け', '神様馬 と 幻の馬 は 同じ 強さ'];
    const side = (who, k) => `<div class="sd" data-sd="${who}"><span>${who === 'my' ? 'あなた' : esc(WHO())}</span><div class="cbflip"><div class="in"><img src="${pic(null, true, who)}" alt=""><img class="fc" src="${pic(k, true, who)}" alt="${esc(nameOf(k))}"></div></div></div>`;
    modal(`<h3 class="gold">ターン ${x.turn}　オープン！</h3><div class="cbvs">${side('my', x.my.k)}<b class="mid gold">VS</b>${side('op', x.op.k)}</div><div class="cbres gold" aria-live="assertive"><span></span><small></small></div>`, 'cbopen');
    await T(450); se('flip');
    modEl.querySelectorAll('.cbflip').forEach(f => f.classList.add('up'));
    await T(700);
    const res = $('.cbres', modEl); res.firstChild.textContent = txt[0]; res.lastChild.textContent = txt[1]; res.classList.add('on');
    const my = $('[data-sd=my]', modEl), op = $('[data-sd=op]', modEl);
    if (hold) se('magic');
    else if (x.res === 'win') { my.classList.add('wn'); op.classList.add('ls'); se('win'); }
    else if (x.res === 'lose') { op.classList.add('wn'); my.classList.add('ls'); se('lose'); }
    else if (x.res === 'tie') se('even');             // 引き分け（ドロー）：どちらも 暗く しない（第4.181版：負け では ない）
    else { my.classList.add('ls'); op.classList.add('ls'); se('even'); }
    $('.cbpips[data-p=op]').innerHTML = pips(x.wins[1], turnsOf()); $('.cbpips[data-p=my]').innerHTML = pips(x.wins[0], turnsOf());
    $('.cbslot.my').innerHTML = cardBtn({ u: x.my.u, k: x.my.k }, ''); $('.cbslot.op').innerHTML = cardBtn({ u: x.op.u, k: x.op.k }, '', '', 'op');
    await T(1900);
    closeMod();
  }
  // 見た カードを 大きく 見せる
  async function peekShow(title, k, note, side) {      // side＝だれの カード（相手の 手札を 見る ときは 'op'）
    modal(`<h3 class="gold">${esc(title)}</h3><div class="sd" style="width:min(46vw,190px)"><div class="cbflip"><div class="in"><img src="${pic(null, true, side)}" alt=""><img class="fc" src="${pic(k, true, side)}" alt="${esc(nameOf(k))}"></div></div></div><p>${esc(note)}</p>`, 'cbopen');
    await T(350); se('flip'); const f = $('.cbflip', modEl); if (f) f.classList.add('up');
    await T(1900); closeMod();
  }
  async function play(ev, v) {
    const P = V;                                       // 動かす 前の 形
    // まとめて 届いた できごとの とちゅうで かき直す ための 写し（自分の 手札・捨て札）
    let hand = P ? P.my.hand.slice() : [], dis = P ? P.discard.slice() : [];
    const rehand = fresh => { paintHand(fresh, hand); layout(); };
    const toDis = cs => { cs.forEach(c => dis.push({ k: c.k, mine: c.mine })); paintDis(dis); };      // cs＝[{ k, mine }]（第4.183版：だれの カードか）
    const kIn = (sd) => { const el = $('.cbslot.' + sd + ' .cbc'); return el && el.dataset.ck ? el.dataset.ck : null; };      // 第4.182版：絵の 名前では なく data-ck（べつの デザインでも 読める）
    for (const x of ev) {
      if (!match) return;
      if (x.e === 'deal') {
        ended = false; gameNo += 1; closeMod(); V = null; paintEmpty();
        payStake();                                    // 第4.179版：部屋の 参加コインを 出す（コンピュータとの 対戦・コインなしの 部屋は 何も しない）
        msLive();                                      // 第4.183版：ミッション：対戦 ちゅうの しるし
        $('.cbdeck .cbn').textContent = '30'; se('deal');
        await banner('対戦 スタート', `${WHO()}と 勝負！`, 900);
        // 配る：山札から 2人の 手札へ
        const d = deckBox(), hm = handBox('my'), ho = handBox('op'), w = Math.min(60, d.w * 1.2);
        const jobs = [];
        const nDeal = Math.max(v.my.hand.length, v.op.hand.length) || R.HAND;      // 配る 数（ふだんは 7まい ずつ）
        for (let i = 0; i < nDeal; i++) { jobs.push(T(i * 90).then(() => fly(null, mid(d, w), mid(hm, w), 320))); jobs.push(T(i * 90 + 45).then(() => fly(null, mid(d, w), mid(ho, w * 0.7), 320, false, 'op'))); }
        await Promise.all(jobs);
        V = v; mode = { k: 'idle' }; render();
        hand = v.my.hand.slice(); dis = v.discard.slice();
        $('.cbhand').querySelectorAll('.cbc').forEach((c, i) => { c.classList.add('new'); c.style.animationDelay = (i * 50 * SPEED) + 'ms'; });
        await T(380);
      } else if (x.e === 'turn') {
        await banner('ターン ' + x.n, x.n >= ((v && v.turns) || R.TURNS) ? 'さいごの 勝負！' : '', 800);
      } else if (x.e === 'pre') {                      // 前の ターンに 神様馬・幻の馬で 勝った：ターンの はじめに 効果を 使うか えらぶ
        se('magic'); await banner(nameOf(x.type) + 'の 効果', x.me ? '使うか えらんでね' : `${WHO()}が 使うか えらぶよ`, 950);
      } else if (x.e === 'set') {
        se('set');
        if (x.me) {
          const c = hand.find(q => q.u === x.u);
          await fly(c ? c.k : null, cardBox('my', x.u) || mid(handBox('my'), 60), slotBox('my'), 300);
          $('.cbslot.my').innerHTML = cardBtn({ u: x.u, k: c ? c.k : null }, '') + '<span class="tag">セット ずみ</span>';
          hand = hand.filter(q => q.u !== x.u); const h = $('.cbhand').querySelector(`[data-u="${x.u}"]`); if (h) h.remove();
        } else { const h = $('.cbohand').lastElementChild; await fly(null, h ? box(h) : mid(handBox('op'), 40), slotBox('op'), 300, false, 'op'); if (h) h.remove(); $('.cbslot.op').innerHTML = cardBtn({ u: 0, k: null }, '', '', 'op'); }
      } else if (x.e === 'efft') {                     // 2人とも セットした：効果タイム
        $('.cbglow').classList.remove('on');
        await banner('効果タイム', x.mine ? 'カードの 効果を 使うか えらんでね' : `${WHO()}が 効果を 使うか えらぶよ`, 950);
      } else if (x.e === 'effd') {
        /* 決めた こと だけ（何を 使うかは まだ 出さない）*/
      } else if (x.e === 'fizz') {
        toast(`${x.me ? '' : WHO() + 'の '}${x.k} の 効果は 使えなかったよ`, 2.2); await T(700);
      } else if (x.e === 'p6') {
        if (x.me) await peekShow('6 の 効果', x.k, `${WHO()}の 手札に ${nameOf(x.k)} が あるよ`, 'op');
        else { se('magic'); toast(`${WHO()}が 6 を 2まい 見せて、\nあなたの 手札を 1まい 見たよ`, 3.2); await T(1100); }
      } else if (x.e === 'ask5') {                     // 第4.183版：交換で 5 を セットした（自分 だけに 届く）→ 使うか 聞く 窓（render の askSync）
        se('magic', 0.7);
      } else if (x.e === 'u5') {                       // セットして いた 5 を 表に → 5 と 手札 1まいを 捨てる → 山札から ふせて セット（第4.183版：交換で 出した 5 も 同じ）
        const sd = x.me ? 'my' : 'op';
        toast(x.me ? `5 の 効果！\n5 と ${nameOf(x.drop.k)} を 捨てて、山札から 1まい セットしたよ` : `${WHO()}が 5 の 効果を 使ったよ\n5 と ${nameOf(x.drop.k)} を 捨てて、山札から 1まい`, 3);
        se('magic');
        $('.cbslot.' + sd).innerHTML = cardBtn({ u: 0, k: '5' }, '', '', sd); await T(600);
        $('.cbslot.' + sd).innerHTML = '';
        const oc = x.me ? null : $('.cbohand').querySelector(`[data-u="${x.drop.u}"]`) || $('.cbohand').lastElementChild;
        await Promise.all([fly('5', slotBox(sd), mid(disBox(), 20), 380, true, sd), fly(x.drop.k, x.me ? (cardBox('my', x.drop.u) || mid(handBox('my'), 60)) : (oc ? box(oc) : mid(handBox('op'), 40)), mid(disBox(), 20), 380, true, sd)]);
        if (x.me) { hand = hand.filter(q => q.u !== x.drop.u); rehand(); } else if (oc) oc.remove();
        toDis([{ k: '5', mine: x.me }, { k: x.drop.k, mine: x.me }]);
        se('set'); await fly(null, mid(deckBox(), 40), slotBox(sd), 340, false, sd);
        $('.cbslot.' + sd).innerHTML = cardBtn({ u: 0, k: null }, '', '', sd) + (x.me ? '<span class="tag">山札から</span>' : '');
        await T(250);
      } else if (x.e === 'x7') {
        se('magic');
        toast(x.me ? '7 の 効果！\n7 を 3まい もどして、新しく 3まい 引いたよ' : `${WHO()}が 7 の 効果を 使ったよ\n7 を 3まい もどして 3まい 引いた`, 3);
        const s7 = x.me ? 'my' : 'op', hb = handBox(s7), d = deckBox(), w = x.me ? 56 : 36;
        await Promise.all([0, 1, 2].map(i => T(i * 70).then(() => fly('7', mid(hb, w), mid(d, 36), 320, true, s7))));
        if (x.me) { let n = 0; hand = hand.filter(q => !(q.k === '7' && n++ < 3)); rehand(); }
        await Promise.all([0, 1, 2].map(i => T(i * 70).then(() => fly(null, mid(d, 36), mid(hb, w), 320, false, s7))));
        if (x.me && x.drew) { hand = hand.concat(x.drew.map(c => ({ u: c.u, k: c.k }))); rehand(x.drew.map(c => c.u)); await T(420); }
      } else if (x.e === 'x3') {                       // 第4.177版：3 を 3まい 見せて、その 1まいと 相手の 手札の 1まい（くじ）を 交換
        const hm = handBox('my'), ho = handBox('op'), tk = x.take.k;
        se('magic');
        // 見せた 3まい（2人とも 見る）
        modal(`<h3 class="gold">3 の 効果！</h3><div class="three">${[0, 1, 2].map(() => `<span class="cbc"><img src="${pic('3', false, x.me ? 'my' : 'op')}" alt="3 の カード" draggable="false"></span>`).join('')}</div><p>${x.me ? `手札の 3 を 3まい 見せたよ<br>その 1まいと、${esc(WHO())}の 手札の 1まいを 交換！` : `${esc(WHO())}が 手札の 3 を 3まい 見せたよ<br>その 1まいと、あなたの 手札の 1まいを 交換！`}</p>`, 'cbopen');
        await T(1700); closeMod();
        if (x.me) {
          await peekShow('3 の 効果：交換！', tk, `${WHO()}の 手札から ${nameOf(tk)} を もらったよ（3 を 1まい わたした）`, 'op');
          await Promise.all([fly('3', cardBox('my', x.give.u) || mid(hm, 56), mid(ho, 36), 400, false, 'op'), fly(tk, mid(ho, 36), mid(hm, 56), 400)]);
          hand = hand.filter(q => q.u !== x.give.u).map(q => (x.three.indexOf(q.u) >= 0 ? { u: q.u, k: q.k, seen: true } : q)).concat([{ u: x.take.u, k: tk, seen: true }]);
          rehand([x.take.u]);
        } else {
          toast(`${WHO()}が 3 の 効果を 使ったよ\nあなたの ${nameOf(tk)} と 3 を 交換した`, 3.4);
          await Promise.all([fly(tk, cardBox('my', x.take.u) || mid(hm, 56), mid(ho, 36), 400, false, 'op'), fly('3', mid(ho, 36), mid(hm, 56), 400)]);
          hand = hand.filter(q => q.u !== x.take.u).concat([{ u: x.give.u, k: '3' }]);
          rehand([x.give.u]);
        }
        await T(500);
      } else if (x.e === 'first') {
        se('flip');
        $('.cbslot.' + (x.me ? 'my' : 'op')).innerHTML = cardBtn({ u: 0, k: '4' }, '', '', x.me ? 'my' : 'op') + '<span class="tag">4 の 効果</span>';
        await banner('4 の 効果！', x.me ? `${WHO()}は カードを 交換するよ` : 'あなたは セットした カードを 交換してね', 1200);
      } else if (x.e === 'first2') {
        se('flip');
        $('.cbslot.my').innerHTML = cardBtn({ u: 0, k: '4' }, ''); $('.cbslot.op').innerHTML = cardBtn({ u: 0, k: '4' }, '', '', 'op');
        await banner('4 の 効果！', 'どちらも 4 の 効果 → 打ち消して ドロー', 1300);      // 第4.181版：2人とも 4 の 効果 → この ターンは ドロー
      } else if (x.e === 'swap') {
        se('set');
        const sd = x.me ? 'my' : 'op', hb = handBox(sd);
        await fly(null, slotBox(sd), mid(hb, x.me ? 56 : 36), 300, false, sd);
        const c = x.me ? hand.find(q => q.u === x.u) : null;
        await fly(c ? c.k : null, x.me ? (cardBox('my', x.u) || mid(hb, 56)) : mid(hb, 36), slotBox(sd), 300, false, sd);
        $('.cbslot.' + sd).innerHTML = cardBtn({ u: 0, k: c ? c.k : null }, '', '', sd) + (x.me ? '<span class="tag">セット ずみ</span>' : '');
        if (x.me) { const bk = v.my.hand.find(q => q.u === x.back) || (P && P.my.set && P.my.set.u === x.back ? { u: x.back, k: P.my.set.k } : null); hand = hand.filter(q => q.u !== x.u); if (bk) hand.push({ u: bk.u, k: bk.k, seen: !!bk.seen }); rehand(bk ? [bk.u] : null); }
        else toast(`${WHO()}が カードを 交換したよ`, 1.8);
      } else if (x.e === 'open') {
        hush();                                        // 「相手を 待って いるよ」などの 前の 文を 消して から 開く
        await openShow(x);
      } else if (x.e === 'k') {
        if (x.me) await peekShow('神様馬の 効果', x.k, `${WHO()}の 手札に ${nameOf(x.k)} が あるよ`, 'op');
        else { se('magic'); toast(`${WHO()}が 神様馬の 効果で、\nあなたの 手札を 1まい 見たよ`, 3.2); await T(1100); }
      } else if (x.e === 'm') {
        se('magic');
        toast(x.me ? `幻の馬の 効果！\n${x.drop.map(c => nameOf(c.k)).join(' と ')} を 捨てて、${x.n}まい 引いたよ` : `${WHO()}が 幻の馬の 効果を 使ったよ\n${x.drop.map(c => nameOf(c.k)).join(' と ')} を 捨てて、${x.n}まい 引いた`, 3.2);
        const sd = x.me ? 'my' : 'op', hb = handBox(sd), d = deckBox(), w = x.me ? 56 : 36;
        await Promise.all(x.drop.map((c, i) => T(i * 80).then(() => fly(c.k, x.me ? (cardBox('my', c.u) || mid(hb, w)) : mid(hb, w), mid(disBox(), 20), 360, true, sd))));
        if (x.me) { hand = hand.filter(q => !x.drop.some(c => c.u === q.u)); rehand(); }
        toDis(x.drop.map(c => ({ k: c.k, mine: x.me })));
        await Promise.all(Array.from({ length: x.n }, (_, i) => T(i * 80).then(() => fly(null, mid(d, 36), mid(hb, w), 320, false, sd))));
        if (x.me && x.drew) { hand = hand.concat(x.drew.map(c => ({ u: c.u, k: c.k }))); rehand(x.drew.map(c => c.u)); }
        await T(250);
      } else if (x.e === 'kskip' || x.e === 'mskip') {
        if (!x.me) { toast(`${WHO()}は 効果を 使わなかったよ`, 1.8); await T(500); }
      } else if (x.e === 'rev') {                      // 逆転勝利（第4.178版）：場の 1まいと 手札の 2まい（合わせて 3まい）を 見せて、手札の 1まいを 捨てる
        hush(); se('magic');
        modal(`<h3 class="gold">${esc(x.k)} の 効果！</h3><div class="three">${[0, 1, 2].map(() => `<span class="cbc"><img src="${pic(x.k, false, x.me ? 'my' : 'op')}" alt="${esc(x.k)} の カード" draggable="false"></span>`).join('')}</div>`
          + `<p>${x.me ? '' : esc(WHO()) + 'が '}${esc(x.k)} を 3まい（場の 1まい ＋ 手札の 2まい）見せたよ<br>手札の ${esc(x.k)} を 1まい 捨てて、${esc(toName(x.beat))} 逆転！</p>`, 'cbopen');
        await T(1700); closeMod();
        const oc = x.me ? null : $('.cbohand').querySelector(`[data-u="${x.drop.u}"]`) || $('.cbohand').lastElementChild;
        await fly(x.k, x.me ? (cardBox('my', x.drop.u) || mid(handBox('my'), 60)) : (oc ? box(oc) : mid(handBox('op'), 40)), mid(disBox(), 20), 380, true, x.me ? 'my' : 'op');
        if (x.me) { hand = hand.filter(q => q.u !== x.drop.u).map(q => (x.show.indexOf(q.u) >= 0 ? { u: q.u, k: q.k, seen: true } : q)); rehand(); } else if (oc) oc.remove();
        toDis([{ k: x.k, mine: x.me }]);
        await T(200);
      } else if (x.e === 'revskip') {
        hush();
        if (!x.me) { toast(`${WHO()}は 逆転勝利を 使わなかったよ`, 1.8); await T(500); }
      } else if (x.e === 'fin') {                      // 逆転勝利を 使うか 決まった：この ターンの 結果（勝ちの しるしは ここで つく）
        const mk = kIn('my'), ok = kIn('op'), won = x.res === 'win';
        $('.cbpips[data-p=op]').innerHTML = pips(x.wins[1], turnsOf()); $('.cbpips[data-p=my]').innerHTML = pips(x.wins[0], turnsOf());
        se(won ? 'win' : 'lose');
        await banner(x.rev ? (won ? '逆転勝利！' : '逆転負け…') : (won ? '勝ち！' : '負け…'), mk && ok ? (won ? `${nameOf(mk)} が ${nameOf(ok)} に 勝ったよ` : `${nameOf(ok)} が ${nameOf(mk)} に 勝ったよ`) : '', 1300);
      } else if (x.e === 'clear') {                    // 出した 2まいを 捨て札へ
        const ka = kIn('my'), kb = kIn('op'), d = mid(disBox(), 20), jobs = [];
        if ($('.cbslot.my .cbc')) jobs.push(fly(ka, slotBox('my'), d, 380, true));
        if ($('.cbslot.op .cbc')) jobs.push(fly(kb, slotBox('op'), d, 380, true, 'op'));
        $('.cbslot.my').innerHTML = ''; $('.cbslot.op').innerHTML = '';
        await Promise.all(jobs);
        toDis((v.me === 0 ? [{ k: ka, mine: true }, { k: kb, mine: false }] : [{ k: kb, mine: false }, { k: ka, mine: true }]).filter(c => c.k));      // 捨てる 順は 席 0 → 席 1（かき直した ときと 同じ カードが 上に なる）
      } else if (x.e === 'end') {
        V = v; render();
        await endShow(x);
      }
    }
  }
  // 対戦の 結果
  async function endShow(x) {
    ended = true;
    const head = x.res === 'win' ? 'あなたの 勝ち！' : x.res === 'lose' ? 'あなたの 負け…' : '同点！';
    se(x.res === 'win' ? 'fanfare' : x.res === 'lose' ? 'over' : 'even');
    modal(`<h3 class="gold">${head}</h3><div class="sc">${x.wins[0]} － ${x.wins[1]}<small>あなた － ${esc(WHO())}（勝った 数）</small></div><div class="gift"></div><div class="gift2" style="min-height:20px;font-size:12.5px;color:#d9c08c"></div>`
      + '<div class="col"><button type="button" class="cbb" data-cb="again">もう 1回</button><button type="button" class="cbb dk" data-cb="menu">メニューへ</button></div>', 'cbend');
    const no = gameNo, r = await settle(x.res), g = $('.cbend .gift');
    if (!g || no !== gameNo) return;
    // 第4.177版（まさちゃん 2026/11/16 10:40「お世話トークンGETした場合、最後の画面でGETしたことをもう少し分かりやすく」）：もらえた ときは 金の わくの 札「お世話トークン ＋○こ GET！」を
    //   ぽんと 出す（1回 だけ ふくらんで 止まる：点めつ しない）。前は 小さい 字の 1行 だけ だった。札の 場所は 先に あけて ある（.gift の 高さ：出ても まわりは 動かない）
    const get = (n, bonus) => `<div class="cbget" role="status" aria-label="お世話トークン ${n}こ GET"><i class="tk" aria-hidden="true">🎟</i><span class="tx"><small>${bonus ? `${REWARD.every}連勝 ボーナス！ ` : ''}お世話トークン</small><b class="n gold">＋${n}こ GET！</b></span></div>`;
    let h = '';
    if (x.res === 'win') {
      const p = r.pay, bonus = r.got > REWARD.win;
      if (p && p.add > 0) h = get(p.add, bonus) + `<div>いま ${p.stock}こ／${p.max}こ${p.add < p.want ? `（${p.max}こ まで なので ${p.add}こ だけ）` : ''}</div>`;
      else if (p) h = `<div>お世話トークンが いっぱい（${p.max}こ）なので、今回は もらえなかったよ</div>`;
      else h = get(r.got, bonus) + '<div>つぎに ここを 開いた ときに わたすね</div>';
      h += `<div><b>${r.streak}連勝中！</b>` + (r.streak % REWARD.every ? `　あと ${REWARD.every - r.streak % REWARD.every}勝で ${REWARD.bonus}こ` : '') + '</div>';
    } else if (x.res === 'lose') h = '<div>連勝は 0 に もどったよ。もう 1回 やって みよう！</div>';
    else h = `<div>${st.streak > 0 ? `同点なので 連勝（${st.streak}連勝）は そのまま` : '同点！ もう 1回 やって みよう！'}</div>`;
    // バトルコイン（第4.179版）：部屋の 参加コイン／コンピュータに 勝った ごほうび を 1行で（いまの 数も）
    //   第4.183版：ミッションを 達成した ときは、その 上に「🎯 ミッション達成！ ○連勝 🪙＋○枚」（いまの 数は 下の 行に まとめる）
    const now = `（いま ${r.coins}枚${r.full ? `：${COIN.max}枚 まで` : ''}）`;
    h += r.ms.map(m => `<div class="cbmsn" role="status" aria-label="ミッション達成 ${m.n}連勝 バトルコイン ${m.c}枚"><i aria-hidden="true">🎯</i><span>ミッション達成！</span><b>${m.n}連勝</b>${COINI}<b>＋${m.c}枚</b></div>`).join('');
    if (r.pot) h += `<div class="cbcl">${COINI}${x.res === 'win' ? `<b>バトルコイン ＋${r.pot.w}枚</b>` : x.res === 'draw' ? `同点：参加コイン ${r.pot.e}枚 もどったよ` : `参加コイン ${r.pot.e}枚は もどらないよ`}${now}</div>`;
    else if (r.coin) h += `<div class="cbcl">${COINI}<b>バトルコイン ＋${r.coin}枚</b>${now}</div>`;      // 5連勝の ときも 1行（「5連勝 ボーナス！」は 上の お世話トークンの 札に 出る）
    else if (r.ms.length) h += `<div class="cbcl">${COINI}バトルコイン${now}</div>`;      // 友だちバトル（コインなしの 部屋）で ミッション達成
    g.innerHTML = h;
    if (g.querySelector('.cbget') || g.querySelector('.cbmsn')) se('magic', 0.7);
    // 部屋の「もう 1回」：参加コインが 足りなければ できない
    const k = match && match.stake;
    if (k && k.e > 0 && st.coin < k.e) { const ab = $('.cbend [data-cb=again]'), g2 = $('.cbend .gift2'); if (ab) ab.disabled = true; if (g2) g2.textContent = `バトルコインが 足りない ので、もう 1回は できないよ`; }
  }
  function again() {
    if (!match || !ended) return;
    if (match.stake && match.stake.e > 0 && st.coin < match.stake.e) return;      // 参加コインが 足りない（第4.179版）
    const g2 = $('.cbend .gift2'), b = $('.cbend [data-cb=again]');
    if (match.kind !== 'cpu') { if (b) b.disabled = true; if (g2) g2.textContent = `${WHO()}を 待って いるよ…`; }
    match.again();
  }
  // 対戦を はなれる（count＝とちゅうで やめた → 負けに 数える）
  function leave(count) {
    const m = match; match = null; queue = [];
    if (m) { if (count && !ended && V) { st.lose += 1; st.streak = 0; msRoll(); st.ms[msKind(m)] = 0; save(); } try { m.leave(); } catch (e) { /* なし */ } }      // 第4.183版：ミッションの 連勝も 0
    if (st && st.stake) { st.stake = null; save(); }      // 第4.179版：とちゅうで やめた → 出した 参加コインは もどらない
    if (st && st.ms && st.ms.live) { st.ms.live = ''; save(); }      // 第4.183版：対戦 ちゅうの しるしを 消す
    V = null; ended = false; closeMod();
  }

  // ---------- 開く・閉じる ----------
  function open() {
    build(); load();
    ov.classList.add('on');
    try { if (window.TengelWallet && window.TengelWallet.lockZoom) window.TengelWallet.lockZoom(true); } catch (e) { /* なし */ }
    try { if (window.TengelFx && window.TengelFx.prime) window.TengelFx.prime(); } catch (e) { /* なし */ }
    ['1', '2', '3', '4', '5', '6', '7', 'k', 'm', null].forEach(k => { const im = new Image(); im.src = pic(k); });
    if (st.back) { const im = new Image(); im.src = deckPic(); }
    actx(); applySets();                               // 音の 出口を 起こす（押した 操作の 中）・設定を 効かせる（エフェクト・BGM）
    showMenu();
  }
  function close() {
    roomStop(); leave(true);
    if (ov) ov.classList.remove('on');
    soundRest();
    try { if (window.TengelWallet && window.TengelWallet.lockZoom) window.TengelWallet.lockZoom(false); } catch (e) { /* なし */ }
    try { document.dispatchEvent(new CustomEvent('tengel:cb')); } catch (e) { /* なし */ }
  }
  return {
    open, close, REWARD, rewardFor, COIN, coinFor, MS, _rng: null, _think: null, _link: null, _opt: null, _room: null, _guard: null, _as: null, _now: null,      // _rng・_think・_link・_opt・_room・_guard・_as・_now：テスト・見本 用（ふだんは 空）
    _t: {      // テスト・見本の 写真 用
      get view() { return V; }, get screen() { return screen; }, get match() { return match; }, get mode() { return mode; }, get state() { return st; }, get ended() { return ended; },
      get idle() { return !pumping && !queue.length && !busy && !lock; }, get ask() { return askOn(); }, say, get sets() { return { bgm: bgmOn(), se: seOn(), fx: fxOn(), raw: { bgm: st.bgm, se: st.se, fx: st.fx }, as: AS }; },
      get bgm() { return { on: !!bg.cur, want: bg.want, have: !!bg.buf, gone: bg.gone, pos: bgmPos(), len: BGM.len, pre: BGM.pre, vol: BGM.vol, file: BGM.file, loop: bg.cur ? [bg.cur.s.loopStart, bg.cur.s.loopEnd] : null, ctx: snd.ac ? snd.ac.state : null }; }, setSet, speed: k => { SPEED = k; }, manual: on => { clk.manual = !!on; }, tick, get now() { return clk.now; }, start: m => startMatch(m), menu: () => { leave(false); showMenu(); }, settle, pay, load, save, modOn, msKey: () => monthKey(), msRoll, ms: tab => showMs(tab), pic
    }
  };
})();
