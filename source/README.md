# テンゲルⅢ（大井・第13改訂版）iPhoneアプリ — ソース

公開URL：https://tmmd6z5fh8-creator.github.io/TENGEL/
（gh-pagesブランチの一番上のファイル＝公開中のアプリ。この `source/` ＝アプリを作るためのファイル）

## データの置き場所（iPhoneの中・IndexedDB「tengel3」版1）
| 入れ物 | 中身 |
|---|---|
| races | マザーデータ1つ目（大井）。アプリに入っている版（hist.json）か、設定タブでExcelから入れ替えた版 |
| bets | 買ったレースの記録（実測・回収の月ごとの収支だけに使う。マザーデータ3つで共通） |
| meta | 1つ目の情報（mother）・マザーデータ2・3つ目（slot:2・slot:3＝{rows,…}）・名前と使う番号（slots）・買い目の設定（set:zones）・最後のバックアップ（backup） |

- マザーデータは3つ（初期の名前：大井競馬・JRA・船橋競馬。名前は変えられる）。使う1つを選ぶと、参考的中率と実測（①〜⑦）がそのデータで計算される。
- 2・3つ目は大井の検証データと同じA〜P列の形で入れる（開催場の列はないので venue は空、id は 日付-m2-R など）。アプリの更新では触らない。

- アプリを更新しても、この3つは消えない。データベースの作りを変えるときは、**足すだけ**にする（消したり作り直したりしない）。
- ホーム画面のアイコンを消すと、iPhoneがこのデータも消す。アイコンを変えたいときは、先にバックアップ → 入れ直し → 戻す。

## ファイル
| ファイル | 役割 |
|---|---|
| engine.js | 判定エンジン（第13改訂版）。`T.setZones()` で買い目編集を反映 |
| src.html | 画面（判定・記録・実測・回収・設定） |
| pwa_shim.js | iPhoneアプリ版の保存（IndexedDB）。アプリ更新時に基盤データをどう扱うかもここ |
| pwa_ui.js | 設定タブのiPhone版だけの機能：Excelから基盤データ入れ替え・アプリの更新・バックアップ |
| build.js → build_pwa.py | アプリを組み立てる（`deploy.sh` がまとめてやる） |
| hist.json | アプリに入れておく基盤データ（大井） |
| excel_to_hist.py | Excel（姫フィルター）の検証データ → hist.json |
| test_engine.js / test_kubun.py / test_set.py / test_pwa.py / test_slots.py | テスト（エンジンの数字・区分ごとの判定・買い目編集・アプリ更新でデータが消えないこと・マザーデータ3つ） |
| mkxlsx.py / mkxlsx2.py / mkslotdata.py | テスト用のExcel・貼り付けデータを作る |

## アプリを直して公開する
1. source/ のファイルを直す
2. `cd source && APP_VER=2026.10.12 sh deploy.sh`（APP_VER は必ず前より大きく。iPhoneの「新しい版があるよ」に使う）
3. `node test_engine.js` / `python3 test_kubun.py` / `python3 mkxlsx.py && python3 mkxlsx2.py && python3 mkslotdata.py` / `python3 test_pwa.py` / `python3 test_slots.py`（test_pwa・test_slots は今の公開版→新しい版の更新を試す）
4. gh-pagesにコミットしてpush

## 基盤データ（大井）をアプリに入れ直す（Excelが届いたとき）
1. `python3 excel_to_hist.py 大井競馬_姫フィルター_第13改訂版.xlsx`（hist.json を作り直す）
2. `APP_VER=… MOTHER_VER=2026-10-14 sh deploy.sh`
3. push。iPhoneでは、まさちゃんが設定タブでExcelから入れた基盤データのほうが新しいときは、そちらを残す（pwa_shim.js）
