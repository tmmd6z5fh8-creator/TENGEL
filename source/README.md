# テンゲルⅢ（大井・第13改訂版）iPhoneアプリ — ソース

公開URL：https://tmmd6z5fh8-creator.github.io/TENGEL/
（gh-pagesブランチの一番上のファイル＝公開中のアプリ。この `source/` ＝アプリを作るためのファイル）

## データの置き場所（iPhoneの中・IndexedDB「tengel3」版1）
| 入れ物 | 中身 |
|---|---|
| races | マザーデータ1つ目（大井）。アプリに入っている版（hist.json）か、設定タブでExcelから入れ替えた版 |
| bets | 買ったレースの記録（実測・回収の月ごとの収支だけに使う。マザーデータ3つで共通）。`buyZ`＝買ったゾーンの名前（例 ["人気→中穴"]） |
| meta | 1つ目の情報（mother）・マザーデータ2・3つ目（slot:2・slot:3＝{rows,…}）・名前と使う番号（slots）・ひとつ前のデータ（prev:1〜3）・買い目の設定（set:zones）・画像の読み取りのAPIキー（set:ocr）・最後のバックアップ（backup） |

- マザーデータは3つ（初期の名前：大井競馬・JRA・船橋競馬。名前は変えられる）。使う1つを選ぶと、参考的中率と実測（①〜⑦）がそのデータで計算される。
- 2・3つ目は大井の検証データと同じA〜P列の形で入れる（開催場の列はないので venue は空、id は 日付-m2-R など）。アプリの更新では触らない。
- 入れる前に形を確かめる：単勝1位・3連単1位・1着人気・2着人気が半分以上の行に入っていないファイル（分析シート・分析表・距離／馬場フィルターなど）は入れない（理由を表示して、いまのデータはそのまま）。
- 入れ替える・空にする・アプリの版に戻すときは、前の中身を「ひとつ前」（prev:N）に残す →「ひとつ前のデータに戻す」で戻せる（もう一度押すと入れたデータに戻る）。
- 1つ目（大井）が判定に使えない形（単勝・3連単・着順が1走もない）になっていたら、アプリを開いたときにアプリに入っている大井データへ自動で戻してお知らせする。
- iPhoneの保存場所（IndexedDB）が開けないときは、1回だけやり直し、それでもだめなら保存なしで動く（アプリに入っている大井データで判定はできる。赤いお知らせを出す）。
- 買ったゾーン：記録カードで、推奨ゾーンのうち買ったものを押して選ぶ（最初はどれも選んでいない）。的中・不的中は、選んだゾーンだけで判定（3連単はそのゾーンの3着2本）。選んでいないと「結果待ち（選んでね）」。`buyZ` がない前の記録は、前と同じく推奨ゾーン全部で判定
- 着順・3連単の組番の欄：iPhoneの数字キーボードに「-」がないので、「.」が打てるキーボード（inputmode=decimal）にして、「.」や空白は打ったそばから「-」にする。区切りなし（6211）は頭数から読み（読み方が2つ以上なら区切ってと案内）、欄を離れると 6-2-11 の形に直す。
- 画像の読み取り：判定タブの「オッズ画像から読み取る」→ スクショを長い辺2000pxのJPEGにして Anthropic の API（標準 claude-sonnet-5-5／節約 claude-haiku-5-5）へ直接送る。APIキーは設定タブで入れて set:ocr にだけ保存（バックアップには入れない）。キーがないときは写真を選ぶ前に案内する。

- アプリを更新しても、この3つは消えない。データベースの作りを変えるときは、**足すだけ**にする（消したり作り直したりしない）。
- ホーム画面のアイコンを消すと、iPhoneがこのデータも消す。アイコンを変えたいときは、先にバックアップ → 入れ直し → 戻す。

## ファイル
| ファイル | 役割 |
|---|---|
| engine.js | 判定エンジン（第13改訂版）。`T.setZones()` で買い目編集を反映 |
| src.html | 画面（判定・記録・実測・回収・設定） |
| pwa_shim.js | iPhoneアプリ版の保存（IndexedDB）。アプリ更新時に基盤データをどう扱うか・壊れた大井の自動修復・画像の読み取り（Anthropic API）もここ |
| pwa_ui.js | 設定タブのiPhone版だけの機能：マザーデータ（入れ替え・形の確認・ひとつ前に戻す）・画像の読み取り（APIキー）・アプリの更新・バックアップ |
| build.js → build_pwa.py | アプリを組み立てる（`deploy.sh` がまとめてやる） |
| hist.json | アプリに入れておく基盤データ（大井）。まさちゃんのデータが届くたびに増える |
| mother_log.json | 基盤データの更新の記録（Excelの「突合メモ」に出る） |
| dropped.json | 重複転記などで消したレース（2026/10/11：9/2の12走＝分析シートの9/2が9/1・9/3の写し）。merge_raw は入れない・アプリはiPhoneの中の大井データに残っていたら消す・Excelや貼り付けで入れても入れない（build_pwa.py が `window.__MOTHER_DROP` に入れる。`DROP=` で無し） |
| merge_raw.py | 分析シート × 分析表（まさちゃんが打ち込む元データ）を日付＋Rで突き合わせて、hist.json に新しいレースを足す（もとのレースは書き換えない・食い違いは報告だけ）。dropped.json のレース・分析シートがほかの日の写しになっている日（同じRの距離・頭数・結果が3R分以上同じ）・同じ中身のレースがもうあるものは入れずに報告 |
| make_mother_xlsx.py | hist.json → アプリで読めるマザーデータのExcel（大井競馬_マザーデータ_アプリ用.xlsx：検証データA〜P列・使い方・突合メモ） |
| excel_to_hist.py | Excel（姫フィルター・マザーデータ）の検証データ → hist.json |
| hist_280.json | テストの土台（10/7までの280走で固定）。テストは hist.json ではなくこれを使う（数字が変わらないように） |
| test_engine.js / test_kubun.py / test_set.py / test_pwa.py / test_slots.py / test_fix.py / test_input.py / test_update.py / test_merge.py / test_buyzone.py | テスト（買ったゾーンの判定（test_buyzone）・突合（test_merge）・データを足した版への更新（test_update）・エンジンの数字・区分ごとの判定・買い目編集・アプリ更新でデータが消えないこと・マザーデータ3つ・壊れた大井の修復／形のちがうファイル／ひとつ前に戻す／画像の読み取り（APIは偽物に差し替え）／保存場所が開けないとき） |
| mkxlsx.py / mkxlsx2.py / mkslotdata.py / mkrawfiles.py | テスト用のExcel・貼り付けデータを作る（mkrawfiles＝分析シート・分析表・馬場フィルターと同じ形） |

## アプリを直して公開する
1. source/ のファイルを直す
2. `cd source && APP_VER=2026.10.12 sh deploy.sh`（APP_VER は必ず前より大きく。iPhoneの「新しい版があるよ」に使う）
3. `node test_engine.js` / `python3 test_kubun.py` / `python3 mkxlsx.py && python3 mkxlsx2.py && python3 mkslotdata.py && python3 mkrawfiles.py` / `python3 test_fix.py` / `OLD_APP=<古い版を git archive した場所> python3 test_pwa.py` / `python3 test_slots.py`（今の公開版→新しい版の更新を試す。版の文字は前より大きく）
4. gh-pagesにコミットしてpush

## まさちゃんから分析シート・分析表が届いたとき（いつものデータ更新）
1. 届いたファイルを空のフォルダにコピーして、まず確かめる：`python3 -I merge_raw.py <分析シート> <分析表> hist.json`（新しいレース・もとのデータとの食い違い・入れなかったレースが出る）。「重複転記の疑い」「同じ中身のレース」が出たら、まさちゃんに確かめる（重複なら dropped.json に足す）
2. 良ければ足す：`python3 -I merge_raw.py <分析シート> <分析表> hist.json hist.json`（hist.json と mother_log.json が更新される）
3. Excelを作る：`python3 make_mother_xlsx.py hist.json 大井競馬_マザーデータ_アプリ用.xlsx` → xlsxスキルの recalc.py で確かめて、まさちゃんに送る
4. `APP_VER=… MOTHER_VER=<最後のレースの日付> sh deploy.sh`
5. `OLD_APP=<今の公開版> XL_OLD=<前のマザーデータExcel> XL_NEW=<新しいExcel> [XL_DUP=<重複入りのExcel>] NEW_VER=… python3 test_update.py`（ほかのテストも）→ push
6. iPhoneでは「更新する」を押すだけ。アプリの版の大井データを使っている人も、前のマザーデータExcelを入れていた人も、新しいデータに入れ替わって「データが新しくなったよ（○走・○/○まで）」と出る（Excelを入れていた人は「ひとつ前に戻す」で戻せる）

## 基盤データ（大井）をアプリに入れ直す（姫フィルターのExcelが届いたとき）
1. `python3 excel_to_hist.py 大井競馬_姫フィルター_第13改訂版.xlsx`（hist.json を作り直す）
2. `APP_VER=… MOTHER_VER=2026-10-14 sh deploy.sh`
3. push。iPhoneでは、まさちゃんが設定タブでExcelから入れた基盤データのほうが新しいときは、そちらを残す（pwa_shim.js）
