# App Storeに出すときの中身（App Store Connect に入れる文と答え）。ここを直して `python3 store/listing.py <出力フォルダ>` を動かす
#   → listing.json（掲載キットのページが読む）・掲載テキスト.txt（そのまま貼れる文）
# 作るたびに確かめる：文字数（Appleの上限）・キーワードのバイト数（100バイト。日本語は1文字3バイト）・
#   キーワードは3文字以上・名前やサブタイトルとかぶらない・競馬場や団体・ほかの商標の名前（app_target.FORBIDDEN）が入っていない
import importlib.util, json, os, re, sys
D = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('app_target', os.path.join(os.path.dirname(D), 'app_target.py')); AT = importlib.util.module_from_spec(spec); spec.loader.exec_module(AT)
LEGAL = json.load(open(os.path.join(os.path.dirname(D), 'legal', 'legal.json'), encoding='utf-8'))
WEB = LEGAL['web']

NAME = 'テンゲル｜競馬予想・オッズ判定'
SUBTITLE = 'スクショで即判定。買い目と収支を記録'
PROMO = ('オッズのスクショを選ぶだけで、レースを「堅い・警戒・穴」の3つの層に判定。推奨の買い目ゾーンと馬番、参考的中率まで一画面で。'
         '買い目の編集、5重勝の組み立て、収支の記録もこのアプリひとつで。')
DESCRIPTION = '''オッズのスクショを選ぶだけで、レースの「荒れやすさ」を判定。
推奨の買い目ゾーン（1着→2着と3着）と馬番、過去のデータでの参考的中率まで、一画面で見られる競馬の判定アプリです。

■ できること
・オッズ画像の読み取り：単勝・複勝・3連単の人気順のスクショを1〜3枚選ぶと、開催場・レース番号・距離・頭数・馬場・オッズが入力欄に入ります（APIキーが必要。下の「画像の読み取りについて」）
・3つの層に判定：A層（堅）・B層（警戒）・C層（穴）。3連単1位と単勝1位のオッズの比や馬場などから、決まったルールで判定します
・推奨ゾーンと馬番：馬単の1着→2着のゾーン（人気・中穴・大穴・超大穴）と3連単の3着、あてはまる馬番を表示
・参考的中率：アプリに入っている過去の290走や、自分で入れたデータで、そのゾーンが実際に出た割合
・買う馬を選ぶ：番号を押して、買う馬・買わない馬を切り替え
・買い目編集：区分ごとに、馬単の1着→2着と3着を自由に変更。変えると、その場で過去のデータでの的中数を計算
・マザーデータ：参考値のもとになるデータを3つまで。決まった形のExcelから入れられて、名前も自由に付けられます
・5重勝：5レースの1着ゾーンと買う馬を、予算の中で組み立て
・収支の記録：券種（単勝・複勝・馬連・馬単・ワイド・3連複・3連単）ごとの購入額・回収額と、月ごと・年ごとの回収率
・電波がなくても動く：判定と記録は端末の中だけで動きます。記録はアプリの中にも自動でバックアップ、ファイルにも保存できます
・説明書つき：画面の写真つきの説明書を、アプリの中でいつでも読めます

■ 使い方
1. 判定タブで「オッズ画像から読み取る」を押してスクショを選ぶ（手で入力してもOK）
2. 層・推奨ゾーン・馬番・参考的中率を見る
3. 買ったら「結果・収支の記録」に入れて保存

■ 画像の読み取りについて
画像の読み取りには、Anthropic（Claude）のAPIキーが必要です（有料・利用者ご自身で用意）。選んだスクショは、利用者のAPIキーでAnthropicのAPIに直接送られ、開発者には届きません。料金の目安は1回 約1〜4円（標準）・1円未満（節約）で、Anthropicに直接お支払いいただきます。APIキーがなくても、手で入力すれば読み取り以外の機能はすべて使えます。

■ プライバシー
記録・設定・マザーデータは、すべて端末の中に保存します。開発者が利用者の情報を受け取ることはありません。広告・アクセス解析はありません。

■ ご利用にあたって
・本アプリは、過去のデータから傾向を分析して表示する道具です。参考的中率などは過去の実測で、これからの的中や利益を約束するものではありません。
・馬券を買うかどうか、何を買うかは、ご自身の判断でお決めください。本アプリに馬券を買う機能はありません。
・馬券は20歳になってから。20歳未満の方は、法律により馬券を購入できません。
・競馬は無理のない範囲で楽しみましょう。のめり込みが心配なときは、ギャンブル依存症予防回復支援センター「サポートコール」0120-683-705（24時間・通話料無料）へ。
・本アプリは個人が開発した非公式のアプリで、競馬の主催者・団体とは関係ありません。
・画面の写真は架空のレースの例です。'''
KEYWORDS = '3連単,三連単,万馬券,回収率,オッズ分析,データ分析,競馬アプリ,穴狙い'
SUPPORT_URL = WEB + 'support.html'
PRIVACY_URL = WEB + 'privacy.html'
COPYRIGHT = '2026 （Apple Developerに登録した名前）'
REVIEW_NOTES = '''This app helps users analyze horse-racing odds that they enter (or read from their own screenshots) and shows suggested "zones" (popularity ranges) for exacta and trifecta tickets, based on past race statistics stored on the device.

The app does NOT offer real-money gambling: there is no betting, no purchase of betting tickets, and no link to any betting service. Users can only record their own results and spending for personal bookkeeping.

How to review (no account or sign-in needed):
1. Open the 判定 (Judge) tab and tap 「入力例を入れる」 (Load example). A full judgment for a fictional race appears below the form.
2. Optional feature: 「オッズ画像から読み取る」 (Read odds from images) sends the screenshots the user selects to the Anthropic API with the user's own API key (Settings > 画像の読み取り). All other features work without a key.
3. Records and settings are stored on the device and the app works offline. Backup and CSV export use the iOS share sheet.

The promotional video in Settings (テンゲルのCM) is streamed from our GitHub Pages site.
The app is intended for adults (18+). Betting on horse races is legal only for people aged 20 or older in Japan, and the app shows this notice.'''

FIELDS = [  # (区分, 項目, 値, 上限, 単位, メモ)
    ('App情報', '名前', NAME, 30, 'chars', 'ホーム画面の名前は「テンゲル」のまま'),
    ('App情報', 'サブタイトル', SUBTITLE, 30, 'chars', ''),
    ('バージョン 1.0', 'プロモーション用テキスト', PROMO, 170, 'chars', '審査なしで、あとからいつでも変えられる'),
    ('バージョン 1.0', '概要', DESCRIPTION, 4000, 'chars', ''),
    ('バージョン 1.0', 'キーワード', KEYWORDS, 100, 'bytes', '名前・サブタイトルの言葉（競馬予想・オッズ判定・買い目・収支など）は入れなくても検索される'),
    ('バージョン 1.0', 'サポートURL', SUPPORT_URL, None, None, '販売者名とメールを入れて公開してから使える'),
    ('App情報', 'プライバシーポリシーURL', PRIVACY_URL, None, None, '販売者名とメールを入れて公開してから使える'),
    ('バージョン 1.0', '著作権', COPYRIGHT, None, None, '「©」は自動で付く。名前はApple Developerに登録した名前（販売者名）'),
    ('バージョン 1.0', 'App Reviewへのメモ（英語）', REVIEW_NOTES, 4000, 'bytes', '審査の人が読む。日本語の説明はページに'),
]


def nbytes(s):
    return len(s.encode('utf-8'))


def check():
    bad = []
    for sec, k, v, lim, unit, _ in FIELDS:
        n = nbytes(v) if unit == 'bytes' else len(v)
        if lim and n > lim:
            bad.append(f'{k}：{n}{unit} > {lim}')
        w = [x for x in AT.FORBIDDEN if x in v]
        if w:
            bad.append(f'{k}：出さない言葉 {w}')
    # ほかの会社・サービスの名前（キーワード・名前・サブタイトルには入れない）
    OTHERS = ['netkeiba', 'ネットケイバ', 'JRA-VAN', 'SPAT4', 'オッズパーク', '楽天', 'ウマニティ', 'うまい馬券', 'TARGET', '競馬ブック', 'iPhone', 'iPad', 'Apple', 'Anthropic', 'Claude']
    for k, v in (('名前', NAME), ('サブタイトル', SUBTITLE), ('キーワード', KEYWORDS)):
        w = [x for x in OTHERS if x.lower() in v.lower()]
        if w:
            bad.append(f'{k}：ほかの会社・サービスの名前 {w}')
    kws = KEYWORDS.split(',')
    if any(len(x) < 3 for x in kws):
        bad.append(f'キーワード：3文字未満 {[x for x in kws if len(x) < 3]}')
    if len(set(kws)) != len(kws) or any(' ' in x for x in kws):
        bad.append('キーワード：重複か空白')
    dup = [x for x in kws if x in NAME or x in SUBTITLE]
    if dup:
        bad.append(f'キーワード：名前・サブタイトルとかぶっている {dup}')
    if bad:
        raise SystemExit('掲載の文がAppleの決まりに合っていないよ：\n' + '\n'.join(bad))
    return {k: (nbytes(v) if unit == 'bytes' else len(v), lim, unit) for sec, k, v, lim, unit, _ in FIELDS}


ANSWERS = {
    'カテゴリ': ['プライマリ：スポーツ', 'セカンダリ：ユーティリティ'],
    '年齢制限指定': [
        'アプリ内の機能（保護者による制限・年齢確認・無制限のWebアクセス・ユーザー生成コンテンツ・メッセージ・広告・ソーシャルメディア）：すべて「いいえ」（外のページはSafariで開くだけ）',
        '内容（暴力・性的な内容・言葉・恐怖・医療・アルコールやたばこ など）：すべて「なし」',
        'シミュレートされたギャンブル：「なし」（アプリの中で賭けはしない）',
        'ギャンブル（実際のお金）：「いいえ」／コンテスト：「なし」／ルートボックス：「いいえ」',
        '年齢カテゴリと上書き：「より高い年齢区分に上書き」→ 18+（日本では馬券は20歳から）',
    ],
    'Appのプライバシー': [
        'データを収集していますか？：「はい」',
        'データの種類：ユーザコンテンツ › 写真またはビデオ（画像の読み取りで選んだスクショがAnthropicのAPIに送られて、Anthropicで一定期間保存されるため）',
        '使用目的：Appの機能／ユーザに関連付け：はい（利用者のAPIキー＝利用者のAnthropicのアカウントで送るため）／トラッキング：いいえ',
        'ほかのデータの種類：すべて「収集しない」（記録・設定は端末の中だけ。開発者には届かない）',
    ],
    '輸出コンプライアンス（暗号化）': [
        'ビルドを出すときに聞かれる「アプリで使用している暗号化アルゴリズムの種類」：「上記のアルゴリズムのいずれでもない」（None of the algorithms mentioned above）',
        '理由：通信はiOSの標準の仕組み（HTTPS）だけで、アプリが自分で暗号化をしていないため',
    ],
    'コンテンツ配信権': [
        '「第三者のコンテンツを含む、表示する、またはアクセスしますか？」：アプリに入っている290走のデータ（オッズ・着順）の元をまさちゃんが確かめてから答える',
    ],
    'App Reviewに関する情報': [
        'サインインが必要：チェックを外す（アカウントなし）',
        '連絡先：まさちゃんの名前・電話番号・メール（審査の人だけが見る）',
        'メモ：下の英語の文をそのまま貼る',
    ],
    '価格および配信状況': [
        '配信する国と地域：日本だけ（説明も画面も日本語・日本の競馬のため）',
        '価格：まさちゃんが決める（無料／有料の買い切り）。有料にするときは「契約／税金／口座情報」で有料Appの契約・口座・税の登録が先に必要',
    ],
    'バージョンのリリース': ['「このバージョンを手動でリリースする」がおすすめ（合格したあと、確かめてから出せる）'],
}
REVIEW_NOTES_JA = ('（日本語の意味）オッズを入れて（または自分のスクショから読み取って）、端末の中の過去のデータをもとに、馬単・3連単の買い目のゾーンを表示するアプリです。'
                   '実際のお金の賭けはできません（馬券の購入・賭け・賭けのサービスへのリンクはなし）。利用者は自分の結果と収支を記録するだけです。'
                   '確かめ方：判定タブの「入力例を入れる」で架空のレースの判定が出ます（アカウント不要）。画像の読み取りだけは利用者自身のAnthropicのAPIキーが必要で、ほかは全部キーなしで動きます。'
                   '記録は端末の中・電波がなくても動く・バックアップとCSVは共有シート。設定のCMはGitHub Pagesから再生。18歳以上向け（日本では馬券は20歳から・アプリにも表示）。')

MEDIA = {
    'preview_iphone': {'file': 'tengel_preview_iphone_886x1920.mp4', 'size': '886×1920', 'where': 'iPhone 6.9インチ ディスプレイの「Appプレビュー」（いちばん左＝最初に出る）', 'poster': '6.8秒（「即判定!!」のところ）'},
    'preview_ipad': {'file': 'tengel_preview_ipad_1200x1600.mp4', 'size': '1200×1600', 'where': 'iPad 13インチ ディスプレイの「Appプレビュー」', 'poster': '6.8秒'},
    'shots_iphone69': {'dir': 'iphone_6.9', 'size': '1320×2868', 'where': 'iPhone 6.9インチ ディスプレイのスクリーンショット（01〜06の順）'},
    'shots_iphone63': {'dir': 'iphone_6.3', 'size': '1206×2622', 'where': 'iPhone 6.3インチ ディスプレイのスクリーンショット（入れておくと安心）'},
    'shots_ipad13': {'dir': 'ipad_13', 'size': '2064×2752', 'where': 'iPad 13インチ ディスプレイのスクリーンショット（01〜06の順）'},
}


def main(out):
    counts = check()
    os.makedirs(out, exist_ok=True)
    data = {'fields': [{'sec': s, 'key': k, 'value': v, 'limit': lim, 'unit': u, 'note': n, 'count': counts[k][0]} for s, k, v, lim, u, n in FIELDS],
            'answers': ANSWERS, 'review_ja': REVIEW_NOTES_JA, 'media': MEDIA}
    json.dump(data, open(os.path.join(out, 'listing.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    lines = ['テンゲル　App Store Connect に入れる文（そのまま貼れる）', '']
    for s, k, v, lim, u, n in FIELDS:
        c = counts[k][0]
        lines += [f'■ {k}（{s}）' + (f'　{c}/{lim}{"バイト" if u == "bytes" else "文字"}' if lim else ''), v, '']
    lines += ['■ App Reviewへのメモの意味（日本語）', REVIEW_NOTES_JA, '']
    for k, vs in ANSWERS.items():
        lines += [f'■ {k}'] + ['・' + x for x in vs] + ['']
    lines += ['■ 画像と動画（ファイル名・大きさ・入れる場所）']
    for m in MEDIA.values():
        lines.append(f'・{m.get("file") or m.get("dir") + "/01〜06.png"}（{m["size"]}）→ {m["where"]}' + (f'。ポスターフレーム：{m["poster"]}' if m.get('poster') else ''))
    open(os.path.join(out, '掲載テキスト.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    for k, (c, lim, u) in counts.items():
        print(f'{k}: {c}' + (f'/{lim} {u}' if lim else ''))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(D, 'out'))
