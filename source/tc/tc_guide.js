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
#tcg .zn{font-weight:700;color:#6a4fd0}
#tcg .note{font-size:11px;color:#8a6a48}
#tcg .hh{margin:8px 0 2px;font-weight:700;color:#6b3f1d}
`;
  // 第4.140版（11/10 14:14 まさちゃん「あと項目ごとに%を説明書に載せるようにして！」）：当たりやすさは 項目ごとに ％（となりに 小さく 分数）。
  //   第4.142版（11/10 17:20 の 指定）：ルーレットと チケットの 分数を かえた（いつも 1/125・1/245・1/399・チケット 1/600／幻の馬 1/15・1/30・1/60／神様馬 1/8・1/16・1/32）
  //   ％は 分数から 数える（pc）。分数は tc_app.js（PRIZES・PRIZES_VISIT・P_…）・tc_care.js（RULE.win・金のニンジン）と 同じ 数（test_tc.py が 見くらべる）
  const pc = (d, n) => {               // n/d → '約1.18%'（ちょうどの 数は「約」なし：10%・0.1%）
    const x = (n || 1) / d * 100, s = String(+x.toFixed(x >= 10 ? 1 : x >= 0.1 ? 2 : 3));
    return (Math.abs(+s - x) > 1e-9 ? '約' : '') + s + '%';
  };
  const R = (d, html) => `<tr data-d="${d}"><td>${pc(d)}<small>1/${d}</small></td><td>${html}</td></tr>`;
  const PT = v => `<span class="pt">${v}P</span> GET`, RT = (a, b) => `<span class="rt">ルーレット</span>（${a}P か ${b}P）`;
  // 第4.141版（11/10 15:52 まさちゃん「壁紙チケット or 8000pにして！」→ 16:08「じゃあ7000pにして！」）：チケット 1枚は 壁紙の 解放か この ポイントに かえるかを 選べる（数は points.js の TICKET_POINTS）
  const TKP = ((typeof window !== 'undefined' && window.TengelPoints && window.TengelPoints.TICKET_POINTS) || 7000).toLocaleString('ja-JP');
  const RS = { cares: 5, min: 5, limit: 30, draws: { maboroshi: 10, kamisama: 5 } };      // draws（第4.168版）：幻の馬・神様馬の 抽選の 上限（tc_app.js の VISIT_DRAWS と 同じ 数）      // 馬の リセット：お世話 5回 → 5分・幻の馬／神様馬の タイムリミット 30分（tc_app.js の RESET_CARES・RESET_MIN・VISIT_MIN と 同じ 数：test_tc.py が 見くらべる）
  // 第4.165版（まさちゃん 11/13 11:46「お世話でポイントGET 確率少し変える(ここだけ) 1/15で10P 1/25で20P 1/55で50P 1/95で100P」）：10P 1/10 → 1/15・20P 1/20 → 1/25・50P 1/50 → 1/55・100P 1/85 → 1/95（ほかは そのまま）
  // 第4.165版（11/13 12:51「ポイントの特化ゾーンを作る … 特化ゾーンも、トレーニングセンターの説明書に追加」）：ポイント特化ゾーン（tc_app.js の ZONE と 同じ 数：test_tc.py が 見くらべる）
  //   1/699 で 入る（どの 表にも 1行）・スタート 1,000P・レバー 1回ごとに 60% で ＋2,000P・12回 つづけて 上乗せで MAX 25,000P・平均 約3,993P（≒4,000P）
  const ZONE = { d: 699, start: 1000, add: 2000, rate: 0.6, max: 12 };
  const ZV = n => ZONE.start + ZONE.add * n, ZP = n => (n < ZONE.max ? Math.pow(ZONE.rate, n) * (1 - ZONE.rate) : Math.pow(ZONE.rate, ZONE.max));      // 上乗せ n回の 合計・そう なる 確率
  const ZAVG = Array.from({ length: ZONE.max + 1 }, (_, n) => ZV(n) * ZP(n)).reduce((a, b) => a + b, 0);
  const cm = v => Math.round(v).toLocaleString('ja-JP');
  const ZROW = R(ZONE.d, `<span class="zn">ポイント特化ゾーン</span>（最大${cm(ZV(ZONE.max))}P）`);      // 1行に おさまる 長さ（「1,000P〜25,000P」は 2行に なる）。くわしくは 下の 項目「ポイント特化ゾーン」
  const CARE = [15, 25, 55, 95, 99, 121, 125, 245, 399, 600, ZONE.d];      // お世話の 当たり ぜんぶ（合わせた ％を 出す）
  // 第4.165版：お世話トークンの 購入（組は points.js の TOKEN_PACKS：なければ 同じ 数）・たまる 間（tc_app.js の TOKEN_MIN と 同じ 数：test_tc.py が 見くらべる）
  const TOK = { every: 5, step: 5, max: 25 };
  const PACKS = ((typeof window !== 'undefined' && window.TengelPoints && window.TengelPoints.TOKEN_PACKS) || [[1, 100], [5, 500], [10, 1000], [15, 1500], [20, 2000], [25, 2500]]).map(x => x.slice());
  // 第4.173版：お世話チャレンジ（tc_drop.js の BALLS・tc_app.js の dropTone と 同じ：test_tc_drop.py が 見くらべる）。色の 名前・字の 色・その 色で 出る 当たり
  const DP = { name: 'お世話チャレンジ', balls: 5, tone: [['青', '#2f7fe0', '10P〜300P'], ['緑', '#2f9f4a', 'ルーレット（800P か 1600P）'], ['紫', '#8a4ad8', 'ルーレット（1600P か 3200P）'], ['赤', '#d8352c', 'ルーレット（3200P か 6400P）'],
    ['金', '#b8860b', '幻の馬のルーレット・ポイント特化ゾーン'], ['虹', '#c2456f', '神様馬のルーレット・チケット']] };
  const SEC = [
    // 第4.159版（まさちゃん 11/12 10:37）：トークンの 上限 25・お世話の あとの PUSH（押した ときに 抽選）・1個／まとめての スイッチ／12:48・14:50：10分ごとに 5つ（12:48 は 5分ごと → 14:50 に 10分ごとへ）・最大の ときに 撫でると「お世話トークンが最大だよ！」／
    //   13:27：ハートの 抽選は トークンが 20こ未満の とき だけ（20こ以上は 抽選まち → 20こを 切ったら 抽選）
    //   第4.165版（11/13 11:46「お世話トークンに5分で5個追加に変更」）：5分ごとに 5つ・購入の 項目を 足した
    ['ト', '#d9a443', 'お世話トークン', `<p>・<b>${TOK.every}分ごとに${TOK.step}つ</b>たまる（最大<b>${TOK.max}こ</b>）</p><p>・「ごはん」「おそうじ」のあとに出る<b>PUSH</b>を1回押すと1つ使う</p><p>・「撫でる」「呼ぶ」はトークンなしでできる</p><p>・ポイントで買うこともできる（下の「お世話トークンの購入」）</p>`],
    ['買', '#3f9f5a', 'お世話トークンの購入', `<p>・下の列の1番右の<b>「お世話トークン購入」</b>を押すと、ポイントで買えるよ</p>
      <table data-tab="packs">${PACKS.map(([n, c]) => `<tr data-n="${n}"><td>${n}こ</td><td><span class="pt">${c.toLocaleString('ja-JP')}P</span></td></tr>`).join('')}</table>
      <p>・持てるのは<b>最大${TOK.max}こ</b>まで（いまの数とあわせて${TOK.max}こをこえる数は、そのときは買えないよ）</p>
      <p>・「買う」→「○○Pで 買う」と2回押すと決まり</p>
      <p class="note">買ったトークンはポイントにもどせないよ。当たりの確率は下の「お世話でポイントGETチャンス」「ポイント特化ゾーン」「幻の馬・神様馬がいるあいだ」の表のとおり</p>`],
    ['押', '#d8352c', 'お世話のあとのPUSH', `<p>・ごはん・おそうじがおわると<b>PUSH</b>が出るよ。押すと<b>トークンを1つ</b>使って抽選！</p>
      <p>・当たりは押したときに出るよ（ハズレは「プフォ」の音だけ）</p>
      <p>・PUSHの横のスイッチで<b>「1個 使う」「まとめて 使う」</b>を選べる（前に選んだ方をおぼえているよ）</p>
      <p>　<b>1個 使う</b> → 1回押したらおしまい</p>
      <p>　<b>まとめて 使う</b> → トークンがあるあいだ、つづけて何回でも押せる（押した回数ぶんトークンがへる）。やめるときは「おわる」</p>
      <p class="note">トークン1つがお世話1回（馬の育ちやミッションの回数も、押した回数ぶん数えるよ）</p>`],
    // 第4.173版（まさちゃん 2026/11/14 23:34「トレーニングセンターの抽選を、今のボタンと、もう一つボール落としができるようにしたい！」）：お世話チャレンジ（玉を 落とす 台：tc_drop.js）。
    //   当たりやすさは PUSH と 同じ（下の 表）。馬バレの 色の 表は tc_app.js の dropTone と 同じ（test_tc_drop.py が 見くらべる）
    ['玉', '#e2574c', DP.name, `<p>・PUSHが出たとき、左下の<b>「お世話チャレンジ」</b>を押すと、<b>玉を落とす台</b>で抽選できるよ</p>
      <p>・<b>「玉を落とす」</b>を押すたびに<b>トークンを1つ</b>使って、玉が1こ落ちる（1回で<b>${DP.balls}こ</b>まで。トークンが${DP.balls}こないときは、あるぶんだけ）</p>
      <p>・当たりやすさは<b>PUSHとまったく同じ</b>（下の表のとおり。どのコップに入っても同じ）</p>
      <p>・玉がコップに入ったとき、当たっていれば まん中の<b>「馬バレ」</b>が光るよ。色で中身がわかる（青から虹へ、光が大きくなる）</p>
      <table data-tab="tone">${DP.tone.map(([nm, col, what]) => `<tr data-c="${nm}"><td><b style="color:${col}">${nm}</b></td><td>${what}</td></tr>`).join('')}</table>
      <p>・当たりは<b>「当選」</b>のますにたまる → 玉をぜんぶ落としたら<b>「保留結果を見る」</b>で順に受け取ろう</p>
      <p>・おわったあと、トークンが<b>${DP.balls}こ以上</b>のこっていれば<b>「続けてやる」</b>か<b>「終わり」</b>を選べるよ</p>
      <p class="note">玉1こ＝トークン1つ＝お世話1回（馬の育ちやミッションの回数も、玉の数ぶん数えるよ）</p>
      <p class="note">とちゅうでアプリを閉じても、たまった当たりはなくならないよ（次に開いたときに「保留結果を見る」から）</p>`],
    ['P', '#e0a020', 'お世話でポイントGETチャンス', `<p>ごはん・おそうじのあとの<b>PUSH</b>を押すたびに抽選！</p>
      <table data-tab="care">${R(15, PT(10))}${R(25, PT(20))}${R(55, PT(50))}${R(95, PT(100))}${R(99, PT(200))}${R(121, PT(300))}
      ${R(125, RT(800, 1600))}${R(245, RT(1600, 3200))}${R(399, RT(3200, 6400))}
      ${R(600, '<span class="tk">チケット</span>（壁紙 or ' + TKP + 'P・1〜3枚）')}${ZROW}</table>
      <p class="note" data-n="sum">ぜんぶ 合わせて ${pc(1 / CARE.reduce((a, d) => a + 1 / d, 0))}（何か 当たる）</p>
      <p class="note">ルーレットは どちらも 50%</p>
      <p class="note">チケットは 3枚 ${pc(8)}・2枚 ${pc(3)}・1枚 ${pc(24, 13)}</p>
      <p class="note">チケット1枚で、<b>カギの壁紙を1つ解放</b>するか、<b>${TKP}P</b>にかえるか、選べるよ（設定の「着せ替え」）</p>
      <p class="note">ポイント特化ゾーンは下の項目を見てね</p>`],
    ['虹', '#7a5ad8', 'ポイント特化ゾーン', `<p>・PUSHを押したとき <b>${pc(ZONE.d)}</b>（1/${ZONE.d}）で突入！（いつもの馬・幻の馬・神様馬の どのときも）</p>
      <p>・スタートは<b>${cm(ZV(0))}P</b></p>
      <p>・<b>「レバーを押し込め！」</b>→ レバーをタップするたびに<b>${Math.round(ZONE.rate * 100)}%</b>で<b>＋${cm(ZONE.add)}P 上乗せ</b>（虹色の光）</p>
      <p>・上乗せに失敗（${Math.round((1 - ZONE.rate) * 100)}%）したら そこでおしまい → それまでの合計をGET</p>
      <p>・<b>${ZONE.max}回つづけて</b>上乗せすると<b>MAX ${cm(ZV(ZONE.max))}P</b></p>
      <p data-n="zavg" data-v="${Math.round(ZAVG)}">・ゾーン1回の平均は<b>約${cm(Math.round(ZAVG / 100) * 100)}P</b></p>
      <table data-tab="zone">${Array.from({ length: ZONE.max + 1 }, (_, n) => `<tr data-n="${n}"><td>${pc(1 / ZP(n))}</td><td>上乗せ <b>${n}回</b> → <span class="pt">${cm(ZV(n))}P</span>${n === ZONE.max ? '（MAX）' : ''}</td></tr>`).join('')}</table>
      <p class="note">上乗せできる回数は、ゾーンに入ったときに決まっているよ（とちゅうでアプリを閉じても、次に開いたときに合計を受け取れるよ）</p>`],
    ['撫', '#e86a92', '撫でる → なかよしハート', `<p>・3回なでると<b>ハート＋1</b></p><p>・つづけて<b>5回</b>まで → 5回なでたら<b>7秒</b>おやすみ</p><p>・ハートは<b>1分に5こ</b>まで</p>
      <p>・ハート<b>10こ</b>で抽選（<b>${pc(66)}</b>・1/66）</p><p>　当たり → <b>ぴょん！</b> お世話トークン<b>×5</b></p><p>　ハズレ → ふぅ〜</p>
      <p>・抽選は<b>お世話トークンが20こ未満</b>のときだけ。<b>20こ以上</b>（最大の25こも）のときは、ハートが10こたまっても<b>抽選まち</b> → PUSHを押してトークンが<b>20こを切ったら</b>抽選がはじまるよ</p>
      <p class="note">トークンは最大25こまで。25このときに撫でると「お世話トークンが最大だよ！」と出るよ</p>`],
    ['呼', '#5aa7c4', '呼ぶ', `<p>・「近づいてくる」「振り向く」「甘える」のどれか（${pc(3)}ずつ・1/3）</p><p>・つづけて<b>5回</b>まで → 5回呼んだら<b>7秒</b>おやすみ</p>`],
    ['食', '#e07a3a', 'ごはん', `<p>・エサ・リンゴ・ニンジンから選ぶ</p><p>・<b>今日の好物</b>だと大よろこび</p><p>・<b>金のニンジン</b>（ニンジンの${pc(30)}・1/30）→ なかよしハート<b>＋3</b></p>`],
    // 第4.165版（11/13 12:59「ほうきと、ちりとりも自由に動かして、ゴミのところまで持っていってほうきで片付けられるようにして！」）：道具は 指で つかんで 運ぶ
    ['掃', '#6aa86a', 'おそうじ', `<p>・<b>15分ごと</b>にゴミが<b>5か所</b>に散らばる（片付けるまで次のゴミは出ない）</p><p>・うんちは2分ごとに<b>${pc(7)}</b>（1/7）で出る</p><p>・おそうじできるのは<b>ゴミかうんちがあるとき</b>だけ</p><p>・<b>ほうき</b>と<b>ちりとり</b>は、指でつかんで好きな所へ運べるよ</p><p>・ほうきでゴミを押して、ちりとりへ はき入れよう（1回でぜんぶ片付く）</p><p>・<b>金のうんち</b>（うんちの${pc(20)}・1/20）→ 運がついた！<b>高確ゾーン</b>（お世話5回）</p>`],
    ['★', '#8a62c8', '2分ごとのチャンス', `<p>・<b>高確ゾーン</b> ${pc(50)}（1/50・お世話5回のあいだ当たりやすい）</p>`],
    // 第4.144版（11/10 18:04 まさちゃん「馬のリセットは5分に切り替えよう！…」・18:19「この仕組みもトレーニングセンターの説明書に記載して！」）：馬の リセット（次の 馬の 抽選）
    ['替', '#2f8f83', '馬のリセット（次の馬の抽選）', `<p>・お世話（ごはん・おそうじ）を<b>${RS.cares}回</b>すると、リセットのタイマーがスタート</p>
      <p>・タイマーが<b>${RS.min}分</b>たつとリセット → 次の馬を抽選</p>
      <p>・<b>幻の馬</b> ${pc(245)}（1/245）・<b>神様馬</b> ${pc(399)}（1/399）がやってくる（それ以外は いつもの馬のまま）</p>
      <p class="note">お世話をしないと 馬はかわらないよ（開いているだけでは 抽選しないよ）</p>
      <p class="note">お世話のとちゅうは リセットしないよ（おわってから）</p>`],
    ['降', '#7a4ab0', '幻の馬・神様馬がいるあいだ', `<p>やってくると フィールドがかわって、お世話の当たりが かわるよ</p>
      <p data-n="draws">・抽選（お世話のあとのPUSH）は、<b>幻の馬 最大${RS.draws.maboroshi}回</b>・<b>神様馬 最大${RS.draws.kamisama}回</b>まで。つかい切ると帰るよ</p>
      <p>・帰るのは、<b>抽選をつかい切ったとき</b>・<b>お世話${RS.cares}回のあと${RS.min}分</b>（リセット）・<b>来てから${RS.limit}分</b>（タイムリミット）の いちばん早いとき</p>
      <p>・左上の「なかよし」の下に「タイムリミット・抽選の回数・切り替わりタイマー」が出るよ</p>
      <p class="hh">🌙 幻の馬</p>
      <table data-tab="maboroshi">${R(15, RT(800, 1600))}${R(30, RT(1600, 3200))}${R(60, RT(3200, 6400))}${ZROW}</table>
      <p class="hh">✨ 神様馬</p>
      <table data-tab="kamisama">${R(8, RT(2000, 4000))}${R(16, RT(5000, 10000))}${R(32, RT(10000, 20000))}${ZROW}</table>
      <p class="note">いるあいだは この表だけ（いつものポイント・チケットは出ないよ）</p>`],
    ['育', '#b07a46', '育つ・色がかわる', `<p>・お世話 <b>50・100・150・200・250回</b>で大きく育つ</p><p>・<b>300回</b>で次の色の子に（ブラウン → まだら → ブラック → ホワイト → 肌色）</p>`],
    ['時', '#4a6aa8', '時間でかわるフィールド', `<p>・朝 7:00〜15:59・夕方 16:00〜18:59・夜 19:00〜6:59</p>`],
  ];
  let root = null, inner = null, body = null, t0 = null, withDrop = false;
  // 第4.173版：「お世話チャレンジ」の 項目は 台の 絵と データが 入って いる とき だけ 出す（入口が 出ない ときに 説明だけ 出さない）
  const dropReady = () => { try { return !!(typeof window !== 'undefined' && window.TCDrop && window.TCDrop.ready()); } catch (e) { return false; } };
  function build(el) {
    if (!document.getElementById('tcg-css')) { const st = document.createElement('style'); st.id = 'tcg-css'; st.textContent = CSS; document.head.appendChild(st); }
    root = document.createElement('div'); root.id = 'tcg'; withDrop = dropReady();
    root.innerHTML = `<div class="bk"></div><div class="sh"><div class="hd"><b>トレーニングセンターの説明書</b><div class="x">✕</div></div><div class="bd"><div class="in">` +
      SEC.filter(s => withDrop || s[2] !== DP.name).map(([ic, col, tt, html]) => `<div class="sec"><h3><i style="background:${col}">${ic}</i>${tt}</h3>${html}</div>`).join('') + `</div></div></div>`;
    el.appendChild(root); inner = root.querySelector('.in'); body = root.querySelector('.bd');
    // 第4.159版（バグ直し・まさちゃん 2026/11/12 14:54「トレーニングセンターの説明書開いたらすぐ閉じるようになってて表示されないよ！」）：
    //   「？」は フィールドの キャンバスの 上の 絵 ＝ 指を はなした とき（pointerup）に 説明書を 開く。指（タッチ）では その すぐ あとに 同じ 場所へ「クリック」が とどく →
    //   もう 開いて いる 説明書の うしろの 幕（.bk：押すと 閉じる）に 当たって、開いた 瞬間に 閉じて いた（マウスでは クリックは 押した 所＝キャンバスへ とどく ので 起きない ＝ テストで 見つからなかった）。
    //   → 開いて から GUARD 秒（下から 出て くる 間）は、幕と ✕ の クリックで 閉じない
    const shut = () => { if (performance.now() - openedAt >= GUARD * 1000) close(true); };
    root.querySelector('.x').addEventListener('click', shut);
    root.querySelector('.bk').addEventListener('click', shut);
    body.style.overflowY = 'auto';
  }
  let anim = null, onClose = null, openedAt = -1e9;
  const GUARD = 0.45;                  // 開いて から この 秒 だけ、うしろの 幕と ✕ の クリックで 閉じない（開いた 指の クリックが とどく ため）
  function tween(a, b, dur, done) {           // アプリ：下から すっと 出る・下へ すっと しまう
    if (anim) cancelAnimationFrame(anim); const t0 = performance.now();
    const f = () => { const u = Math.min(1, (performance.now() - t0) / (dur * 1000)); set(a + (b - a) * u); if (u < 1) anim = requestAnimationFrame(f); else { anim = null; if (done) done(); } };
    anim = requestAnimationFrame(f);
  }
  function open(el, opt) {
    if (root && withDrop !== dropReady()) { root.remove(); root = null; }      // 台の 絵が あとから 読めた：項目を 入れて 作り直す
    if (!root) build(el); root.style.display = 'flex'; openedAt = performance.now();
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
  return { open, set, scroll, close, isOpen, GUARD, get el() { return root; } };
})();
