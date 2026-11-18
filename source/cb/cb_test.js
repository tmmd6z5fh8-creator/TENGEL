// TENGERカードバトル：テスト版の 道具（第4.182版・まさちゃん 2026/11/16 20:00・20:09「デザインカスタム」）
//   ・テスト版（TENGEL_TEST=1 で 作った アプリ）の cb_bundle.js に だけ 入る（build_pwa.py）。App Store版の 中身には 入らない
//   ・デザインカスタムの 画面の いちばん 下に「テスト版の 道具」の 箱：
//       バトルコイン ＋300・＋1000・0枚に ／ 解放を ぜんぶ もとに もどす（いつもの デザインに）
//       第4.185版：「解放を ぜんぶ もとに もどす」は プレイボードも（いつもの ボードに）
//     ＝ 300枚・500枚 たまるまで コンピュータに 勝たなくても、解放と 使う 流れを ためせる
//   CBTest.html()・CBTest.act(t, api)　api＝cb_app.js の dzApi（add・set・reset・pk）
//   第4.189版：カードパックの「つぎの くじ」を 決める（レア・神様馬／幻の馬の レア・超レア・神様馬／幻の馬の 超レア）＝ 何回も 開けなくても、レア・超レアの 演出を ためせる
//   第4.183版：ミッションの 画面の いちばん 下にも「テスト版の 道具」：コンピュータ／友だちバトルで 1勝・負け（連勝 0）・月が かわった ことに（リセット）
//     ＝ 何回も 対戦しなくても、達成 → バトルコインを もらう 流れと 月の リセットを ためせる。CBTest.msHtml()・CBTest.msAct(t, api)　api＝cb_app.js の msApi（win・lose・next）
const CBTest = (() => {
  'use strict';
  const B = [['add300', 'バトルコイン ＋300'], ['add1000', 'バトルコイン ＋1000'], ['zero', 'バトルコインを 0枚に'], ['reset', '解放・集めた カードを 全部 元に 戻す'],
    ['pkr', '次の くじ：レア'], ['pkgr', '次の くじ：神様馬・幻の馬の レア'], ['pksr', '次の くじ：超レア'], ['pkgsr', '次の くじ：神様馬・幻の馬の 超レア']];
  function html() {
    return '<div class="cbtst"><b>🧪 テスト版の 道具</b><small>App Store版には ないよ（コインを 増やす・パックの くじを 決めて、レア・超レアの 演出を 試せる）</small><div class="r">'
      + B.map(([t, l]) => `<button type="button" class="cbb dk sm" data-cb="tst" data-t="${t}">${l}</button>`).join('') + '</div></div>';
  }
  function act(t, api) {
    if (!api) return;
    if (t === 'add300') api.add(300);
    else if (t === 'add1000') api.add(1000);
    else if (t === 'zero') api.set(0);
    else if (t === 'reset') api.reset();
    else if (/^pk(r|gr|sr|gsr)$/.test(t) && api.pk) api.pk(t.slice(2));
  }
  const M = [['mcw', 'コンピュータで 1勝'], ['mcl', 'コンピュータで 負け'], ['mfw', '友達バトルで 1勝'], ['mfl', '友達バトルで 負け'], ['mnx', '月が 変わった ことに（リセット）']];
  function msHtml() {
    return '<div class="cbtst"><b>🧪 テスト版の 道具</b><small>App Store版には ないよ（対戦 しなくても、ミッションの 達成と リセットを 試せる）</small><div class="r">'
      + M.map(([t, l]) => `<button type="button" class="cbb dk sm" data-cb="tstm" data-t="${t}">${l}</button>`).join('') + '</div></div>';
  }
  function msAct(t, api) {
    if (!api) return;
    if (t === 'mcw') api.win('cpu');
    else if (t === 'mfw') api.win('fr');
    else if (t === 'mcl') api.lose('cpu');
    else if (t === 'mfl') api.lose('fr');
    else if (t === 'mnx') api.next();
  }
  // 第4.196版：決戦調査の マップの 右上「🧪」→ テスト版の 道具：次の エリアを 討伐済みに・全部 討伐済みに・討伐を 0 に・月が 変わった ことに・戦を「1ターンで 勝てる 手札」に（切りかえ）
  //   ＝ レベル 12 まで 52勝 しなくても、強い 敵・確定カード・勝利の 演出（3段階）を 試せる。CBTest.qHtml(easy)・CBTest.qAct(t, api)　api＝cb_app.js の qApi（clr・all・zero・next・easy）
  const Q = [['qclr', '次の エリアを 討伐済みに'], ['qall', '全部 討伐済みに'], ['q0', '討伐を 0 に 戻す'], ['qnx', '月が 変わった ことに（リセット）'], ['qez', '']];
  function qHtml(easy) {
    return '<div class="cbtst"><b>🧪 テスト版の 道具</b><small>App Store版には ないよ（たくさん 勝たなくても、強い 敵・確定カード・勝利の 演出を 試せる）</small><div class="r">'
      + Q.map(([t, l]) => `<button type="button" class="cbb dk sm" data-cb="tstq" data-t="${t}">${t === 'qez' ? (easy ? '戦を いつもの 手札に 戻す' : '戦を「1ターンで 勝てる 手札」に') : l}</button>`).join('') + '</div></div>';
  }
  function qAct(t, api) {
    if (!api) return;
    if (t === 'qclr') api.clr();
    else if (t === 'qall') api.all();
    else if (t === 'q0') api.zero();
    else if (t === 'qnx') api.next();
    else if (t === 'qez') api.easy();
  }
  return { html, act, msHtml, msAct, qHtml, qAct };
})();
