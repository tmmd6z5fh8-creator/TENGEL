# テンゲル iPhone・iPadアプリ（Swift Playgrounds の App）

- `Tengel.swiftpm` … アプリ本体（Swift Playgrounds・Xcodeで開ける）。中の画面（Resources/）は Web版と同じもの
- 作り方：gh-pages ブランチの `source/` で `python3 build_ios.py <出力フォルダ>`（Swiftの枠は `source/ios/Tengel.swiftpm`）
- `ci/` と `.github/workflows/ios.yml` … GitHubのMacで作ってシミュレーターで動かす確認（結果は `ios-ci-<ランナー>` ブランチ）
