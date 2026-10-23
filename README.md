# テンゲル iPhone用アプリ（Swift Playgrounds の App・iPadでは互換モード）

- `Tengel.swiftpm` … アプリ本体（Swift Playgrounds・Xcodeで開ける）。中の画面（Resources/）は Web版と同じもの
- 作り方：gh-pages ブランチの `source/` で `python3 build_ios.py <出力フォルダ>`（Swiftの枠は `source/ios/Tengel.swiftpm`）
- `ci/` と `.github/workflows/ios.yml` … GitHubのMacで作ってシミュレーターで動かす確認（結果は `ios-ci-<ランナー>` ブランチ）
- 2026/10/23〜 第1弾：iPhone用だけ（Package.swift は `.phone`・縦向きだけ。Swift Playgrounds の設定を触ると戻ることがあるので `source/test_iphone_only.py` で確かめる）・ポイント（台帳は画面の中の points.js／points_ui.js・しるしは Markers.swift のキーチェーン・App内課金は Store.swift の StoreKit 2：製品は App Store Connect に jp.tengel.app.points500〜4000・sub2000／4400／9200 を作る）・開いたときの画面・2本指で拡大
- 2026/10/23〜 第3弾：的中ボタン（的中・デカ的中・ど的中・隠れど的中・ハズレ・いつものボード（お金なし）・効果音・設定の 的中エフェクト／控えめ／効果音。画面の中の fx.js。**絵と音（ネオンのマスク・効果音 m4a）はこのブランチに入れない**：手元で `source/kisekae/build_fx_assets.py` → `build_ios.py` が Resources/ に入れる。CIは絵と音なしで動くことを確かめる＝デカ・ど的中の演出を直接出してスクショ）
