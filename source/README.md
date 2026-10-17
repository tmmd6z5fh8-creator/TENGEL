# テンゲルⅢ（大井・第13改訂版）iPhoneアプリ — ソース

公開URL：https://tmmd6z5fh8-creator.github.io/TENGEL/
（gh-pagesブランチの一番上のファイル＝公開中のアプリ。この `source/` ＝アプリを作るためのファイル）

## データの置き場所（iPhoneの中・IndexedDB「tengel3」版1）
| 入れ物 | 中身 |
|---|---|
| races | マザーデータ1つ目（大井）。アプリに入っている版（hist.json）か、設定タブでExcelから入れ替えた版 |
| bets | 買ったレースの記録（実測・回収の月ごとの収支だけに使う。マザーデータ3つで共通）。`buyZ`＝買ったゾーンの名前（例 ["人気→中穴"]）。`types`＝買った券種（単勝・複勝・馬連・馬単・ワイド・3連複・3連単）、`amt`＝券種ごとの金額 {券種:{stake,payout}}（`stake`/`payout` はその合計。`amt` がない前の記録は合計だけ）。`hp`＝選んだ馬 {ゾーン名:{a:[1着の馬番],b:[2着],t:[3着]}}（全部選んでいる側は持たない）。WIN5の記録も `kind:'win5'`（id＝日付-win5）でここに入れる（画面ではふつうの記録・収支と分けて、WIN5タブにだけ出す） |
| meta | 1つ目の情報（mother。`dataVer`＝入っているデータの版・`home`＝開催場のしるし）・マザーデータ2・3つ目（slot:2・slot:3＝{rows,…}）・名前と使う番号（slots）・ひとつ前のデータ（prev:1〜3）・買い目の設定（set:zones）・画像の読み取りのAPIキー（set:ocr）・最後のバックアップ（backup）・App Store版の「データの更新」で最後に入れた版（data） |

- マザーデータは3つ（初期の名前：大井競馬・JRA・船橋競馬。名前は変えられる）。使う1つを選ぶと、参考的中率と実測（①〜⑦）がそのデータで計算される。
- 2・3つ目は大井の検証データと同じA〜P列の形で入れる（開催場の列はないので venue は空、id は 日付-m2-R など）。アプリの更新では触らない。
- **アプリの中でレースのデータを入れる**（2026.10.13-1〜）：① 判定画面の「結果・収支の記録」で着順を入れて保存すると、「マザーデータにも入れる」で選んだマザーデータにそのレースも入る（開催場が合うマザーデータがはじめから選ばれている。馬番で入れた着順はオッズの順で人気に直す。払戻も入れられる）② 設定 → マザーデータ → 編集 →「レースを見る・直す」（月ごとの一覧・直す・消す）・「＋レースを1つ入れる」（手で入れる。入れる前に層・帯・的中を表示）③「書き出す（CSV）」（A〜P列・Excelに貼り付け）④ Excel・CSVを選ぶと「足す」（いまのレースは残す）か「入れ替える」。自分で入れた行は `src`（'input'＝アプリの中で入れた・'file'＝ファイルから足した）と `at` を持つ。id は 日付-oi-R（Web版の1つ目）／日付-m1〜m3-R（App Store版・2・3つ目）
- アプリに入っているデータが新しくなったとき（アプリの更新・App Store版の「データの更新」）は、日付＋Rが同じレースは新しいデータのほうを使い、**自分で入れたほかのレースは残す**（pwa_shim.js の keepUser）。前より古いデータには戻さない（`dataVer`）
- 入れる前に形を確かめる：単勝1位・3連単1位・1着人気・2着人気が半分以上の行に入っていないファイル（分析シート・分析表・距離／馬場フィルターなど）は入れない（理由を表示して、いまのデータはそのまま）。
- 入れ替える・空にする・アプリの版に戻すときは、前の中身を「ひとつ前」（prev:N）に残す →「ひとつ前のデータに戻す」で戻せる（もう一度押すと入れたデータに戻る）。
- 1つ目（大井）が判定に使えない形（単勝・3連単・着順が1走もない）になっていたら、アプリを開いたときにアプリに入っている大井データへ自動で戻してお知らせする。
- iPhoneの保存場所（IndexedDB）が開けないときは、1回だけやり直し、それでもだめなら保存なしで動く（アプリに入っている大井データで判定はできる。赤いお知らせを出す）。
- 買う馬の選択（判定画面）：ゾーンの番号（1着・2着・3着）を押して選ぶ・外す（最初は全部＝ゾーンで判定するのと同じ）。馬単は1着・2着、3連単は3着も、買ったゾーンの選んだ馬に入っているかで判定（馬番で入れても人気で入れても。人気はオッズの順から馬番に直す。オッズの一覧がないレースはゾーンだけ）。レース（日付・開催場・R）が変わる・画像を読むとリセット。点数は出さない（テンゲルのルール）
- 買った券種：記録カードで7つから選ぶ（いくつでも）。券種ごとに購入額→回収額。馬単・3連単はテンゲルの買ったゾーンと着順で判定（今までどおり）、単勝・複勝・馬連・ワイド・3連複はゾーンがないので回収額で判定（入っていれば的中・0なら外れ・空なら結果待ち）。どれか当たればレースは的中。収支は券種ごと（前の記録で券種を2つ以上買って金額を分けていないものは「券種を分けていない記録」にまとめる）
- 買ったゾーン：記録カードで、推奨ゾーンのうち買ったものを押して選ぶ（最初はどれも選んでいない）。的中・不的中は、選んだゾーンだけで判定（3連単はそのゾーンの3着2本）。選んでいないと「結果待ち（選んでね）」。`buyZ` がない前の記録は、前と同じく推奨ゾーン全部で判定
- WIN5タブ：JRAの指定5レースの1着を全部当てる馬券（1組100円・点数＝各レースの頭数のかけ算）。①〜⑤は判定画面で入れる（WIN5の入力中は、判定画面の入力がそのまま⑤まで入る。戻ると前の入力に戻す）か、判定画面の「WIN5に入れる ①〜⑤」
  - 1着ゾーン＝馬単ゾーンの1着側（A層→人気、B層→中穴・人気、C層・第1／第2段階→人気・中穴・大穴、C層・非該当→人気）。「推奨」として出し、自分で選ぶ（押して選ぶ）かランダム（推奨から1つずつ。「推奨以外もまぜる」で全ゾーンから）
  - 予算の中の頭数：選んだゾーンの馬を「推奨の順（第1ゾーンの1着が先）→単勝オッズの低い順」に並べ、全レース1頭から始めて「単勝オッズから出した当たる見込みの増え方÷点数の増え方」が一番大きいレースに1頭ずつ足す（点数≦予算÷100）
  - 当たる目安＝選んだゾーンの1着の割合（使っているマザーデータの実測・区分ごと）×ゾーンの中で買った馬の単勝オッズの割合（実測が5走未満なら単勝オッズだけ）
  - 買う馬は番号を押して自分で選べる（`man`。そのレースは固定・ほかのレースは残りの予算で自動・「おまかせに戻す」・ランダムにすると全部おまかせに戻る・自分で選んだ馬だけで予算をこえたら赤で案内）
  - 結果：各レースの1着の馬番 → ○×。1つでも外れたら不的中、5つとも入ったら的中。購入額が空なら点数×100円。作業中の5レース・予算などは localStorage の `tengel.win5`（入力中のレースは `tengel.w5edit`）
- 着順・3連単の組番の欄：iPhoneの数字キーボードに「-」がないので、「.」が打てるキーボード（inputmode=decimal）にして、「.」や空白は打ったそばから「-」にする。区切りなし（6211）は頭数から読み（読み方が2つ以上なら区切ってと案内）、欄を離れると 6-2-11 の形に直す。
- 画像の読み取り（Web版）：判定タブの「オッズ画像から読み取る」→ スクショを長い辺2000pxのJPEGにして Anthropic の API（標準 claude-sonnet-5-5／節約 claude-haiku-5-5）へ直接送る。APIキーは設定タブで入れて set:ocr にだけ保存（バックアップには入れない）。キーがないときは写真を選ぶ前に案内する。
- **画像の読み取り（App Store版・2026.10.14-1〜）：APIキーなし・追加料金なし・端末の中で完結**（まさちゃんの指定）。スクショを長い辺2600pxのJPEGにしてアプリ（Swift の `TextReader`＝Apple の Vision の文字認識・ja/en）に渡し、読めた文字と位置（`lines`）を `ocr_local.js` がオッズ画面の表（単勝・複勝の行＝[人気][枠]馬番 馬名 単勝 複勝、3連単の人気順＝順位 組番 オッズ、レース情報＝R・距離・ダ芝・馬場・頭数・開催場・日付）に組み立てて、Web版と同じ形の JSON にする。画像も文字も外に送らない。設定タブの「画像の読み取り」はキーの欄なし（説明だけ）。説明書の「画像の読み取り（APIキー）」の項目は App Store版には出さない。**Web版だけの部分（Claude に読ませる仕組み・APIキーのカード・Claude への指示）は `/*@web-only*/ 〜 /*@/web-only*/` で囲んであり、app_target.py が App Store版からまるごと消す**（出さない言葉に Anthropic・Claude・sk-ant・APIキー も入れて、残っていたら作らない）

- アプリを更新しても、この3つは消えない。データベースの作りを変えるときは、**足すだけ**にする（消したり作り直したりしない）。
- ホーム画面のアイコンを消すと、iPhoneがこのデータも消す。アイコンを変えたいときは、先にバックアップ → 入れ直し → 戻す。

## ファイル
| ファイル | 役割 |
|---|---|
| engine.js | 判定エンジン（第13改訂版）。`T.setZones()` で買い目編集を反映 |
| src.html | 画面（判定・記録・実測・回収・設定） |
| pwa_shim.js | iPhoneアプリ版の保存（IndexedDB）。アプリ更新時に基盤データをどう扱うか・壊れた大井の自動修復・画像の読み取り（Anthropic API）もここ |
| ocr_local.js | App Store版の画像の読み取り：端末の中で読んだ文字と位置から、オッズ画面の表を組み立てる（`TengelOCR.parse([lines…])`）。開催場の名前の一覧は持たない（画面に書いてあるものだけ）。テストは test_ocr_local.js（testdata/ocr/ の架空のオッズ画面＝make_mock.py で作る）と、GitHubのMacの本物の Vision（ios/ci/selftest.js の ocr） |
| pwa_ui.js | 設定タブのiPhone版だけの機能：マザーデータ（入れ替え・足す・形の確認・ひとつ前に戻す・レースの一覧と1つ入れる・CSVの読み書き）・画像の読み取り（Web版はAPIキー・App Store版は説明だけ）・アプリの更新（App Store版：App Storeの版の確認・データの更新・開いたときのお知らせ）・バックアップ（自分で入れたレースも入る） |
| build.js → build_pwa.py | アプリを組み立てる（`deploy.sh` がまとめてやる） |
| hist.json | アプリに入れておく基盤データ（大井）。まさちゃんのデータが届くたびに増える |
| mother_log.json | 基盤データの更新の記録（Excelの「突合メモ」に出る） |
| dropped.json | 重複転記などで消したレース（2026/10/11：9/2の12走＝分析シートの9/2が9/1・9/3の写し）。merge_raw は入れない・アプリはiPhoneの中の大井データに残っていたら消す・Excelや貼り付けで入れても入れない（build_pwa.py が `window.__MOTHER_DROP` に入れる。`DROP=` で無し） |
| merge_raw.py | 分析シート × 分析表（まさちゃんが打ち込む元データ）を日付＋Rで突き合わせて、hist.json に新しいレースを足す（もとのレースは書き換えない・食い違いは報告だけ）。dropped.json のレース・分析シートがほかの日の写しになっている日（同じRの距離・頭数・結果が3R分以上同じ）・同じ中身のレースがもうあるものは入れずに報告 |
| make_mother_xlsx.py | hist.json → アプリで読めるマザーデータのExcel（大井競馬_マザーデータ_アプリ用.xlsx：検証データA〜P列・使い方・突合メモ） |
| excel_to_hist.py | Excel（姫フィルター・マザーデータ）の検証データ → hist.json |
| hist_280.json | テストの土台（10/7までの280走で固定）。テストは hist.json ではなくこれを使う（数字が変わらないように） |
| test_engine.js / test_kubun.py / test_set.py / test_pwa.py / test_slots.py / test_fix.py / test_input.py / test_update.py / test_merge.py / test_buyzone.py / test_win5.py / test_types.py / test_hpick.py | テスト（買う馬の選択（test_hpick）・買った券種（test_types）・WIN5（test_win5）・買ったゾーンの判定（test_buyzone）・突合（test_merge）・データを足した版への更新（test_update）・エンジンの数字・区分ごとの判定・買い目編集・アプリ更新でデータが消えないこと・マザーデータ3つ・壊れた大井の修復／形のちがうファイル／ひとつ前に戻す／画像の読み取り（APIは偽物に差し替え）／保存場所が開けないとき） |
| manual/ | 説明書（2026.10.12-3〜）。content.html（項目ごとの中身。`<!--@id-->` で区切る）・manual.css・manual.js・build_manual.py（`build('pwa', 出力先, 版)` で manual.html と写真の manual/ を作る。build_pwa.py が呼ぶ／`artifact` でclaude.ai用）・img/（画面の写真・バナー）・meta.json/dims.json（写真の番号の位置）・tools/（写真の撮り直し：`python3 manual/tools/shots.py <作業フォルダ>` → `python3 manual/tools/conv.py <作業フォルダ>` → できた s_*.webp・meta2.json（→meta.json）・dims.json を manual/ に入れる） |
| test_dataentry.py | アプリの中でのデータ入力のテスト：記録の保存でマザーデータにも入る（馬番→人気・払戻・入れない選択）・レースの一覧／直す／消す／1つ入れる・書き出し（CSV）・CSVを「足す」・バックアップと戻す・アプリの更新で自分で入れたレースが残る・App Store版（にせもののアプリ）：App Storeの版のお知らせ・データの更新（新しい版／壊れたデータ／まだ公開していない（404））・前より古いデータに戻さない・名前の出ない画面 |
| test_manual.py | 説明書のテスト（上と設定タブの入口・もくじ→項目・アプリに戻るとタブがそのまま・電波がなくても説明書と写真が開く・アプリのページが説明書で上書きされない） |
| cm_media/ | CM（紹介動画・2026.10.12-5〜）。tengel3_cm.mp4（前置き15秒＋スロット新台CM風30秒＝45秒・1080×1920・30MB以下）と poster.jpg（表紙）。build_pwa.py が cm/ に置いて、設定タブの「テンゲルのCM」から全画面で見られる。動画は大きいのでサービスワーカーでしまわない（表紙だけしまう）。入れ替えたら ?v= が自動で変わる |
| cm/ | CMの作り方（cm2.html＝本編・pro.html＝前置き・cm2_shots.py＝アプリの画面を撮る・bgm2.py／pro_bgm.py＝音・render.py／render_pro.py＝1コマずつ撮る・assets/）。`sh cm/make.sh` で cm_media/ を作り直す。CMでは「大井」「第13改訂版」の文字は出さない（Web版の画面は cm2_shots.py の SCRUB_JS で消す・App Store版は `TARGET=app` でApp Store版の画面を撮る → shots_app/・`SHOTS=shots_app` で使う） |
| test_cm.py | CMのテスト（設定タブの説明書の下・押すと全画面・×／外側／Escで閉じる・動画はしまわない・表紙はしまう・電波がないときのお知らせ） |
| build_ios.py | iPhone・iPadアプリ（App Store用・Swift Playgrounds の App）を組み立てる：`python3 build_ios.py <出力フォルダ>` → Tengel.swiftpm と Tengel.swiftpm.zip。画面はWeb版と同じ（build_pwa.py の index.html・説明書・CMの表紙）を Resources/ に名前だけで並べる（Swift Playgrounds がフォルダを平らにするので。PNGは入れない） |
| ios/Tengel.swiftpm | アプリのSwiftの枠：Package.swift（名前「テンゲル」・jp.tengel.app・版 displayVersion/bundleVersion・iPhoneとiPad・カメラの説明）・TengelApp.swift（画面）・TengelWebView.swift（Web画面とアプリのつなぎ：共有シート・コピー・自動バックアップ・App Storeの版・画像の文字の読み取り・外のリンクはSafari。`WebHostView`＝Web画面の入れ物：時計・電波（ステータスバー）やホームバーに重なる分を測って `--top-inset`／`--bottom-inset` として渡す）・StoreCheck.swift（App Storeに出ている版を Apple の lookup で調べる。送るのはアプリのIDと国だけ）・TextReader.swift（画像の文字を端末の中で読む：Vision の VNRecognizeTextRequest・ja/en・位置つき）・AppFiles.swift（tengel://localhost/ で Resources を出す・自動バックアップのファイル・テスト用の SelfTest は Debug だけ）・Assets.xcassets（アイコンは icons/icon_master_en.png を build_ios.py が入れる） |
| ios/ci/ | GitHubのMacでの確認（run.sh・selftest.js・ios.yml）。`ios` ブランチ（Tengel.swiftpm＋ci/＋.github/workflows/ios.yml）にpushすると、Swift 5・Swift 6・Release（実機）で作って、iPhone・iPadのシミュレーターで記録の保存・開き直し・自動バックアップから戻す・画面のスクショを確かめる。結果は `ios-ci-macos-15`・`ios-ci-macos-26` ブランチ（summary.txt・report-*.json・shots/） |
| test_native.py | アプリ版の画面のテスト（にせもののアプリをつなぐ）：画像の読み取り（端末の中の文字認識のかわりに架空のオッズ画面の文字を返す → 入力欄に入る・外に通信しない・APIキーの欄がない）・「アプリの版」カード・自動バックアップ（保存のたび・APIキーは入れない）・共有シート（バックアップ・CSV）・コピー・記録0件のとき「戻す？」→ 戻す／戻さない・CMは公開中のWeb版から・Web版は今までどおり |
| legal/ | 「このアプリについて」（設定タブのいちばん下：ご利用にあたって＝参考情報・20歳・相談先／非公式のアプリ・商標の表記／プライバシーポリシー／特定商取引法に基づく表記／フォントのライセンス）と、公開するページ（legal/privacy.html・tokushoho.html・support.html）。中身は build_legal.py、販売する人の欄は legal.json（seller・email・address・phone）。**欄が空のページは公開しない**（deploy.sh が「まだなし」と出す）。確認用は `python3 legal/build_legal.py preview <フォルダ>`（空の欄を【要記入】にして全部作る） |
| ios/fonts/ | App Store版に入れるフォント（BIZ UDPGothic・Dela Gothic One・IBM Plex Mono。SIL OFL 1.1・ファイルはそのまま。入手元とライセンスは ios/fonts/README.md）。App Store版は Google Fonts に通信しない |
| manual/content_app.html | App Store版の説明書で入れ替える項目（このアプリでできること・マザーデータ・APIキー・バックアップ・困ったとき）。App Store版では「iPhoneに入れる」「データを新しくする（Web版）」は出さない（build_manual.py の mode='app'）。「アップデート」はApp Store版だけ（`WEB_SKIP`・写真 upd_* は `TARGET=app` の shots.py が、前の版のデータを入れたアプリとにせもののApp Store（1.1）で撮る）。`{{mother}}` はアプリに入れるデータの走数に置きかわる |
| manual/img_app/・meta_app.json・dims_app.json | App Store版の説明書の写真（App Store版の画面で撮ったもの＝競馬場・団体・版の名前が出ない）。撮り直し：`TARGET=app python3 manual/tools/shots.py <作業フォルダ>` → `python3 manual/tools/conv.py <作業フォルダ> app` → man_app/img の s_*.webp を img_app/ に、man_app/dims.json を dims_app.json に、man_app/raw/meta2.json を meta_app.json に |
| app_target.py | **App Store版に、特定の競馬場・団体・商標・版の名前（大井・JRA・WIN5・第13改訂版 など。`FORBIDDEN`）を1つも入れない**ための変換（2026/10/13）。build_pwa.py（TARGET=app）・build_manual.py（app）が使う。① プログラムのコメントを消す ② `INDEX`・`MANUAL_SEC` の表で置きかえる（置きかえる文字の数が合わなければ止まる＝元を直したら表も直す。`APP_TARGET_REPORT=1` で全部の食い違いを出す） ③ 出さない言葉が残っていたら作らない。アプリに入れるデータは開催場の名前を消して「しるし」（`fnv()`＝FNV-1a・JSの `T.vhash()` と同じ）だけ `window.__MOTHER_HOME` に入れる（id は 日付-m1-R）。Web版・claude.ai版はこの変換をしない |
| test_appname.py | App Store版のテスト：作ったファイルと画面（全タブ・判定の全文・説明書の全項目）に出さない言葉がない・開催場ははじめ空（空ならふつうの判定）・アプリに入っているデータの開催場はしるしで比べる（「大井」「大井競馬場」と入れてもふつうの判定、ちがう開催場は【参考判定】）・自分で入れたデータは名前で比べる・日付とRで自己参照の除外・期間「最新」・5重勝・記録の（参考）とCSV・Web版は今までどおり |
| mkxlsx.py / mkxlsx2.py / mkslotdata.py / mkrawfiles.py | テスト用のExcel・貼り付けデータを作る（mkrawfiles＝分析シート・分析表・馬場フィルターと同じ形） |

## アプリを直して公開する
1. source/ のファイルを直す
2. `cd source && APP_VER=2026.10.14-2 sh deploy.sh`（APP_VER は必ず前より大きく。iPhoneの「新しい版があるよ」に使う。説明書の manual.html と manual/、CMの cm/ もいっしょに置く）
3. `node test_engine.js` / `python3 test_kubun.py` / `python3 mkxlsx.py && python3 mkxlsx2.py && python3 mkslotdata.py && python3 mkrawfiles.py` / `python3 test_fix.py` / `OLD_APP=<古い版を git archive した場所> python3 test_pwa.py` / `python3 test_slots.py`（今の公開版→新しい版の更新を試す。版の文字は前より大きく）
4. gh-pagesにコミットしてpush

## iPhone・iPadアプリ（App Store用。2026.10.12〜お試し版）
- 上の帯・説明書の上のバー・下のタブは、時計・電波（ステータスバー）・ホームバーに重ならないようにしてある：CSS は `--sat`／`--sab`（`max(env(safe-area-inset-*), var(--top-inset／--bottom-inset))`）を使う。`--top-inset` などはアプリ（WebHostView）が実際の重なりを測って入れる（Swift Playgrounds のプレビューなど、安全な範囲が正しく伝わらない場所の保険。ふつうの端末では 0 で、env() のとおり）
- 画面はWeb版と同じ。アプリの中では `tengel://localhost/index.html` で開くので、`window.__NATIVE`（pwa_shim.js）が true になって、アプリ版として動く：
  - 設定タブ：「アプリの更新」（いまの版・App Storeに新しい版があれば「App Storeで更新する」。更新そのものは App Store）・「データの更新」（公開している data/mother_app.json を読んで、1つ目のマザーデータを新しくする。自分で入れたレース・記録はそのまま）・バックアップは共有シートで渡す・「自動バックアップ」の欄
  - 開いたとき（12時間に1回まで）にApp Storeの版と公開データを確かめて、新しければ上にお知らせ（「App Storeで更新」「入れる」・×で閉じる）
  - データの更新（2026.10.13-1〜）：deploy.sh が data/mother_app.json（開催場の名前なし・しるしだけ・`{app,kind,ver,n,first,last,home,rows}`）を公開する。アプリは `window.__DATA_URL` から読んで、`ver` が入っている版（MOTHER_VER）より新しければ入れる（文字の大小で比べる。**MOTHER_VER は必ず前より大きく**）。読むのはデータだけ（審査ガイドライン 2.5.2）。まだ公開していない（404）ときは「新しいデータはないよ」
  - 記録や設定を保存するたび（1.5秒まとめて）、アプリの中のファイル（Application Support/tengel-autobackup.json・アプリを開いて最初に書くときに前のを -prev に残す）にもバックアップ。APIキーは入れない
  - 開いたときに記録が0件なのに自動バックアップに記録がある（保存場所が消えた）→「前の記録が見つかったよ。戻す？」（聞いている間は自動バックアップを書かない）
  - 記録タブの書き出しに「CSVで保存」（共有シート）・コピーはアプリが直接クリップボードへ・サービスワーカーは使わない・CMの動画は公開中のWeb版から読む
- 作る：`python3 build_ios.py <出力フォルダ>` → Tengel.swiftpm.zip をiPadの「ファイル」に保存 → 開いて（解凍して）Swift Playgrounds で開く → ▶︎
- 確かめる：`python3 test_native.py`（画面）・`ios` ブランチにpush（GitHubのMacで作ってシミュレーターで動かす。ios/ci/）
- アプリの版を上げるときは `IOS_VERSION=1.1 IOS_BUILD=2 python3 build_ios.py <出力>`（Package.swift の displayVersion・bundleVersion を書きかえて作る。App Storeに出すたびに IOS_BUILD は前より大きく）
- 中身は `TARGET=app python3 build_pwa.py <出力>`（build_ios.py が呼ぶ）：フォントはアプリの中（ios/fonts）・説明書はApp Store版・「姫に送って」「まさちゃんの」はお客さん向けの言い方・「このアプリについて」はApp Store版（プライバシーにCM・自動バックアップ、フォントのライセンスつき）
- CMはアプリ用の版（cm_media/tengel3_cm_app.mp4。最後が「iPhone・iPadで、いつでも判定」）を公開中のWeb版から読む。アプリ用は画面もApp Store版で撮る（cm/shots_app・5重勝・マザーデータ2）。最後に非公式・iPhoneの商標（Apple・アイホン）の注意書き（Web版はJRA/WIN5の商標も）
- **App Store版には、特定の競馬場・団体・商標・版の名前を入れない**（2026/10/13・まさちゃんの指定）：開催場は使う人が入れたもの・画像から読んだものだけ（はじめは空＝使っているマザーデータの開催場として判定）・マザーデータの名前ははじめ「マザーデータ1〜3」（自由に変えられる）・WIN5→「5重勝」・版の表示（第13改訂版）なし・第13新規→「最新」・第12の帯→「旧本線の帯」。アプリに入れるデータの開催場は「しるし」（ハッシュ）で比べる。全部 app_target.py（作るたびに確かめる）・test_appname.py
- 商標・特商法まわり（2026/10/13）：アプリ名・キーワードに「JRA」「WIN5」「大井」などほかの団体の名前を入れない（App Store審査 2.3.7・5.2.1）。有料で売るときは legal.json を埋めて deploy → App Store Connect のプライバシーポリシーURL・サポートURLに legal/privacy.html・support.html

## App Storeに出す素材（2026/10/13〜）
- `sh store/make.sh <出力フォルダ>` で全部作る：プレビュー動画（iPhone 886×1920・iPad 1200×1600・29.5秒）・スクショ（iPhone 6.9インチ 1320×2868／6.3インチ 1206×2622／iPad 13インチ 2064×2752 を各6枚・透明なしPNG）・掲載の文（掲載テキスト.txt・listing.json）・掲載キットのページ（kit.html＋media/。claude.aiのアーティファクトで公開：https://claude.ai/artifact/T81oGy9zxkB2ZTUdwzAua9）
- プレビュー動画は **アプリの画面だけ** で作る（審査ガイドライン 2.3.4：プレビューはアプリそのものの画面の録画だけ。文字を重ねるのはOK）。cm/preview.html：CM（cm2.html）と同じテロップ・音楽（bgm2.wav）・タイミングで、画面いっぱいにApp Store版の画面。CMの前置き・エンブレム・スロットのリール・紙吹雪は使わない。iPadはテロップを下に出す（`window.__IPAD`）
- 画面の写真：cm/cm2_shots.py を `TARGET=app CM_PREV=1`（＋ iPhone `CM_VW=443 CM_VH=960 CM_DPR=2 CM_OUT=shots_prev`／iPad `CM_IPAD=1 CM_VW=1032 CM_VH=1376 CM_DPR=1.1627907 CM_OUT=shots_prev_ipad`）。5重勝の開催場は架空（ひがし・にし）
- スクショ：cm/store_shots.html（見出しはCMと同じ文字・金のふちの端末の中にApp Store版の画面）を cm/store_shots.py が撮る
- 掲載の文：store/listing.py（名前・サブタイトル・プロモーション用テキスト・概要・キーワード・URL・著作権・審査へのメモ・質問への答え）。作るたびに Appleの上限（キーワードは100バイト＝日本語は1文字3バイト・3文字以上）・出さない言葉（app_target.FORBIDDEN）・ほかの会社の名前を確かめる
- 素材の動画・写真はリポジトリには入れない（大きいので。make.sh でいつでも作り直せる）

## App Storeの製品ページ（紹介ページ）の素材・ポイント版（2026/10/16〜）
- `sh store/make7.sh <出力フォルダ>` で全部作る（CM第7弾の内容：初回ダウンロードで1500Pプレゼント・1レース200P・Pカスタム・マザーデータ15,000P・単勝5連予想・サブスク）
  - 画面写真：cm/store_shots7.html・store_shots7.py（iPhone 6.9インチ 1320×2868／iPad 13インチ 2064×2752 を各10枚。1枚目は「スクショを選ぶだけで即判定!!」＋1500Pのバッジ・2枚目は入れる3枚の例の画面）
  - プレビュー動画：cm/preview7.html・make_preview7.sh（29.5秒・アプリの画面だけ・テロップは下。CM第7弾の4つの場面をそのままつなぎ、音も bgm7.wav の同じところ）
  - 貼る文：store/listing7.py（App内課金：製品ID jp.tengel.app.points500〜4000・サブスク jp.tengel.app.sub2000／4400／9200・価格は税抜×1.1の税込）・掲載キット：store/kit7.py
- 画面は cm2_shots.py の `CM7=1`（ポイントの帯・ロック・購入はテスト用ブラウザの中で足して撮るイメージ・`CM_PTS_BAL` で保有ポイント）。**アプリでポイントを作ったら、本物の画面で撮り直してから出す**（審査 2.3）
- 説明文の「購入したポイントに有効期限はありません」「サブスクで届いたポイントは30日」は審査 3.1.1 に合わせた形。紹介特典は作り方と審査を確かめてから、プロモーション用テキストに入れる

## 着せ替え（仮デザイン・2026/10/17〜・まだアプリには入れていない）
- まさちゃんの指定の5テーマ＋いつもの：牧場（黄緑・芝と馬）／かわいい（ピンク・ハート・リボン・ポニー）／綺麗（レッド×ブラック・眼鏡の大人の女性・薔薇・馬）／子供向け（薄い黄色×パウダーホワイト・毛糸とフェルト・ぬいぐるみの馬・ロボット）／カッコいい（金・金ピカの馬）。アプリはFableで作る（それまでアプリのソースは変えない）
- 判定画面のいちばん上の絵（390×160）：kisekae/svg/banner_*.svg。作り直すときは `python3 kisekae/<ranch|cute|elegant|kids|gold>.py <出力フォルダ>`（art.py の部品で描く・すべてオリジナル）。子供向けの上の帯の背景は knit_tile.svg（12×10のくり返し）
- 見本の画面：kisekae/mock/（claude.ai の Design のキャンバスの中身。Judge_*.dc.html＝判定画面×6・Main.dc.html＝設定 › 着せ替え（タップで切り替わる）・Guide.dc.html＝色・文字・形・絵の表）。色はテーマごとのCSS変数（--bg・--hd・--btn など）にまとめてある
- 変えないもの：判定・記録・ポイント・馬番の枠の色（1白・2黒・3赤・4青・5黄・6緑・7橙・8桃。暗いテーマは黒の枠に細いふち）。アプリに入れるときはフォントもアプリの中へ（OFL）・選んだテーマは端末に保存
- 2026/10/17 まさちゃんの指定：綺麗は「ヴィラン」版（女性・薔薇はなし・画面いっぱいの絵＋すける黒いガラスのカード）・「黄金の炎」（炎と宝石の黄金の馬）を足して7つに
- 2026/10/17 まさちゃんの指定（2回目）：この2つは**写真を使わず、まさちゃんの画像をイメージにして一から作ったオリジナルの絵**にする（写真そのままはダメ）。ヴィランの**赤い目はやめる**（ダサい）
  - ヴィラン：赤い満月と稲妻の空・岩山の上で後ろ足で立つつやのある黒馬（目は光らない黒）・風になびくたてがみ・火の粉
  - 黄金の炎：磨いた金の馬（前足を上げる）・炎のたてがみとしっぽ・サファイアの胸当て／顔の飾り／おもがい・首のうろこ・金の炎のうず・光の粒
  - 作り方（kisekae/r3d/）：馬の形は3D（horse3d.py＝骨格と筋肉のかたまり・armor3d.py＝よろいと宝石）を、小さなレイマーチャ sdfr.c で光と映り込みまで計算して描く → 炎（fire2d.py）・毛（hair2d.py）・空や背景を2Dで重ねる
    - `gcc -O3 -march=native -ffast-math -fopenmp kisekae/r3d/sdfr.c -o kisekae/r3d/sdfr -lm`
    - `cd kisekae/r3d && python3 villain3d.py tmp/vil 1 2 && python3 villain_comp.py tmp/vil <出力>` → villain3_wall.jpg（780×1688）・villain3_thumb.jpg（780×320）
    - `python3 gold3d.py tmp/gold 1 2 && python3 gold_comp.py tmp/gold <出力>` → goldfire3_wall.jpg・goldfire3_thumb.jpg（1枚あたり1〜2分）
    - 形だけ確かめる：`python3 test_clay.py tmp/clay REAR`（粘土の色で3方向から）
  - できた絵は公開のリポジトリに入れない（作り直せる・claude.ai のキャンバスの中だけ）。前の写真から作った版（photo_*.py）は消した
- 2026/10/17 まさちゃんの指定（3回目）：**とりあえず4つだけ**（牧場・かわいい・子供向け・カッコいい）＋いつもの（元の見た目に戻す用）。綺麗（ヴィラン）と黄金の炎はいったん外した（キャンバス・mock から消した）。r3d/ の作り方は残してあるので、いつでも戻せる。elegant.py・banner_elegant.svg（最初の綺麗）も今は使っていない
- 判定画面の並び（全テーマ共通）：上の帯 → テーマの絵 → **レース情報（マザーデータの切り替え・オッズ画像から読み取る。いつもと同じボタンで、色と形だけテーマに合わせる）** → 判定の結果（下へスクロール）。最初の見本は絵がレース情報の場所に入っていて、レース情報が抜けていたので直した
- 2026/10/17 まさちゃん「姫に任せる！後20個着せ替え作ってみて！」→ **新しく20テーマ**（いつもの＋定番4＋20＝25）
  - 季節・行事7：桜／海／夕焼け／紅葉／雪／午年（お正月）／花火　競馬4：ナイター／競馬新聞／勝負服／開運（蹄鉄）　和・アート4：将棋（桂馬）／水墨画／大理石／チェス　レトロ・ポップ5：ネオン／ドット絵／黒板／メリーゴーランド／星座（ペガサス）
  - 絵（780×320）：kisekae/r3d/banners/<名前>.py。3Dの馬（horse3d.py の STAND・REAR・PRANCE・GALLOP）を sdfr で描き、style2d.py でアニメ塗り・輪郭・たてがみ・騎手などの2Dにする（すべて一から描いたオリジナル）。`cd kisekae/r3d && python3 banners/sakura.py <出力>.webp`。できた絵はリポジトリに入れない（キャンバスの中だけ）
  - 色・文字・形・飾り：kisekae/themes20.py（テーマごとのCSS変数・背景のもよう・帯の飾り・カードのすみの小さな飾り・メモの文）
  - 見本を作る：`python3 kisekae/gen_screens.py kisekae/blobs20.json`（Judge_*.dc.html ×20。文字と背景のコントラストも調べて、4.5未満は LOW と出る）→ `python3 kisekae/gen_main.py kisekae/blobs20.json 1960 2460`（Main.dc.html＝25テーマを5つの組に分けた選ぶ画面・Guide20.dc.html＝新しい20個のメモ）。元の5テーマのCSSは mock/base/main_v17.dc.html から取る。blobs20.json はキャンバスに上げた絵のid
  - 選ぶ画面の動きの確認：`node kisekae/vals_from_js.js kisekae/mock/Main.dc.html <テーマid> <出力>.json`（Main の renderVals をそのまま動かした値）
  - フォントはすべて Google Fonts の無料のもの（OFL）。アプリに入れるときはアプリの中へ。暗いテーマ（花火・ナイター・ネオン・黒板・星座）は黒の枠に細いふち
- 2026/10/17 まさちゃん「壁紙の馬の絵が雑すぎるから直してほしい！合計19枚分訂正して！」→ テーマごとに、まさちゃんが送る参考の絵の **感じ（ぺたっとした色＋太い線）** で、馬だけを描き直す。**壁紙の色と模様はそのまま・馬の色と飾りは壁紙に合わせる・参考の絵はそのまま使わない（形は一から）**
  - 道具：kisekae/flat/flat_horse.py（点をなめらかにつなぐ・足の形・「線を先に太く→色を上に」で外がわだけ線・SVGを透明なPNGに）
  - 1枚目 メリーゴーランド：kisekae/flat/carousel_horse.py（木馬。前足を上げた形・丸い波のたてがみと鞍の布・パステルの足首・金のひづめ・金の頭のベルトと胸の飾り）→ `python3 kisekae/flat/carousel_banner.py <出力>.webp`（背景・屋根・電球・ぼけた光・床・金の柱は前の carousel.py と同じ。線の色はテーマの文字色 #4A2A4E）
  - 2枚目 星座・ペガサス（まさちゃん「2枚目を星座のように羽つけて！」＝走る馬の感じ＋羽）：`python3 kisekae/flat/pegasus_banner.py <出力>.webp`（sdfr がいる）。走る馬の形は3Dの馬（体・首・頭・足）、たてがみ・しっぽ・羽は一から作った形。うすく光る形＋なめらかな外の線＋線の上の小さい星＋星座の線と明るい星。夜空・天の川・星・三日月は前の constellation.py と同じ
- 2026/10/17 まさちゃん「記録時に的中した場合に表示される的中ボタン、デカ的中ボタンのベースを作成して！」→ **的中ボタン・デカ的中ボタン（ベース）**。アプリはまだ変えていない（Fableで入れる）
  - 的中（3連単以外が当たり）：記録する → PUSH（上下に動く）→ タップ → 壁紙の馬がボードを持って下から出てくる（ボードに当たった買い目と払戻の合計）
  - デカ的中（3連単が当たり。ほかの券種もいっしょに当たっていてもデカ）：大きいPUSH（虹の輪）→ タップ → 白く光る → 虹の光に包まれる → 光の中から馬がボードを持って出てくる（3連単の行は虹色の枠）
  - 見本：kisekae/mock/Fx_Hit.dc.html・Fx_Big.dc.html（タップで動く）・Fx_Memo.dc.html（出るとき・流れと時間・重ねる順・ボードに書くもの・テーマごとに変えるところ・容量）。動きは全部CSS（動画なし）。iPhoneの「視差効果を減らす」がオンなら、上下の動き・回転・広がる光・紙ふぶきを止めて、馬とボードはふわっと出す
  - 2026/10/17 まさちゃんの指定：**PUSHボタンは横長の長方形（角は丸い）**（的中200×100・角26px／デカ280×140・角36px。丸 → 角の丸い四角 → 横長）。デカの虹の輪もボタンと同じ形で、形は動かず色だけが回る（.halo の中で大きい円すいグラデーションを回して、輪の形に切り抜く）
  - ボードは当たりの数で下にのびる（7行まで「とじる」にかからない）。買い目の行は0.15秒おき（行に --i）、合計と「とじる」は最後の行のあと（.ov に --n＝行の数）
  - 指示書（Fable用）の16.2に同じ中身（プロジェクトの「テンゲル_AppStore版_アップデート指示書」第1.1版）
  - ボードを持つ馬：`cd kisekae/r3d && python3 fx/board_horse.py <出力> hb_ranch` → hb_ranch_back.png（馬ぜんぶ）・hb_ranch_front.png（ボードにかぶさる前足の先だけ）・hb_ranch.json（ボードの四角とひづめの位置）。アプリでは「うしろの馬 → ボード（HTMLの文字）→ 前足の先」の順に重ねるので、ひづめがボードのふちにかかって見える。前足を外へ開く形は horse3d.py の fore_spread（1.0なら前と同じ形）。ポーズを並べて選ぶ：fx/hold_test.py
  - 見本を作る：`python3 kisekae/gen_fx.py kisekae/fx_blobs.json <hb_ranch.json>`（牧場の色と上の絵は mock/Judge_Ranch.dc.html から取る。fx_blobs.json はキャンバスに上げた絵のid）
  - できた絵はリポジトリに入れない（キャンバスの中だけ）。いまの馬は見本（牧場の栗毛）。壁紙の絵を描き直したら、テーマごとに作り直す（色はCSS変数 --pushA〜--rimD・--bFrame・--bFace・--bInk・--hitRed・--ray）

## まさちゃんから分析シート・分析表が届いたとき（いつものデータ更新）
1. 届いたファイルを空のフォルダにコピーして、まず確かめる：`python3 -I merge_raw.py <分析シート> <分析表> hist.json`（新しいレース・もとのデータとの食い違い・入れなかったレースが出る）。「重複転記の疑い」「同じ中身のレース」が出たら、まさちゃんに確かめる（重複なら dropped.json に足す）
2. 良ければ足す：`python3 -I merge_raw.py <分析シート> <分析表> hist.json hist.json`（hist.json と mother_log.json が更新される）
3. Excelを作る：`python3 make_mother_xlsx.py hist.json 大井競馬_マザーデータ_アプリ用.xlsx` → xlsxスキルの recalc.py で確かめて、まさちゃんに送る
4. `APP_VER=… MOTHER_VER=<最後のレースの日付> sh deploy.sh`
5. `OLD_APP=<今の公開版> XL_OLD=<前のマザーデータExcel> XL_NEW=<新しいExcel> [XL_DUP=<重複入りのExcel>] NEW_VER=… python3 test_update.py`（ほかのテストも）→ push
6. iPhoneでは「更新する」を押すだけ。アプリの版の大井データを使っている人も、前のマザーデータExcelを入れていた人も、新しいデータに入れ替わって「データが新しくなったよ（○走・○/○まで）」と出る（Excelを入れていた人は「ひとつ前に戻す」で戻せる。アプリの中で自分で入れたレースは残る）
7. App Store版は、deploy.sh が置いた data/mother_app.json を「データの更新」で読む（アプリの更新はいらない。開いたときに「新しいデータがあるよ」と出る）

## 基盤データ（大井）をアプリに入れ直す（姫フィルターのExcelが届いたとき）
1. `python3 excel_to_hist.py 大井競馬_姫フィルター_第13改訂版.xlsx`（hist.json を作り直す）
2. `APP_VER=… MOTHER_VER=2026-10-14 sh deploy.sh`
3. push。iPhoneでは、まさちゃんが設定タブでExcelから入れた基盤データのほうが新しいときは、そちらを残す（pwa_shim.js）
