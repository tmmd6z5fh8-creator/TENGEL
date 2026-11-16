// TENGERカードバトル：テスト版の 道具（第4.182版・まさちゃん 2026/11/16 20:00・20:09「デザインカスタム」）
//   ・テスト版（TENGEL_TEST=1 で 作った アプリ）の cb_bundle.js に だけ 入る（build_pwa.py）。App Store版の 中身には 入らない
//   ・デザインカスタムの 画面の いちばん 下に「テスト版の 道具」の 箱：
//       バトルコイン ＋300・＋1000・0枚に ／ 解放を ぜんぶ もとに もどす（いつもの デザインに）
//     ＝ 300枚・500枚 たまるまで コンピュータに 勝たなくても、解放と 使う 流れを ためせる
//   CBTest.html()・CBTest.act(t, api)　api＝cb_app.js の dzApi（add・set・reset）
const CBTest = (() => {
  'use strict';
  const B = [['add300', 'バトルコイン ＋300'], ['add1000', 'バトルコイン ＋1000'], ['zero', 'バトルコインを 0枚に'], ['reset', '解放を ぜんぶ もとに もどす']];
  function html() {
    return '<div class="cbtst"><b>🧪 テスト版の 道具</b><small>App Store版には ないよ（コインを ふやして、解放と 使う 流れを ためせる）</small><div class="r">'
      + B.map(([t, l]) => `<button type="button" class="cbb dk sm" data-cb="tst" data-t="${t}">${l}</button>`).join('') + '</div></div>';
  }
  function act(t, api) {
    if (!api) return;
    if (t === 'add300') api.add(300);
    else if (t === 'add1000') api.add(1000);
    else if (t === 'zero') api.set(0);
    else if (t === 'reset') api.reset();
  }
  return { html, act };
})();
