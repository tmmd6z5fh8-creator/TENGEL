# App Storeの製品ページ（紹介ページ）・ポイント版（CM第7弾の内容）：App Store Connect に入れる文と答え
#   python3 store/listing7.py <出力フォルダ>  → listing7.json（掲載キットのページが読む）・掲載テキスト_ポイント版.txt（そのまま貼れる文）
# ポイント・サブスクは、アプリ（Fableで作る）ができてから、この文と画面が本物と同じか確かめて出す（審査 2.3・3.1）
# 作るたびに確かめる：文字数（Appleの上限）・キーワードのバイト数・出さない言葉（app_target.FORBIDDEN）・ほかの会社の名前
import importlib.util, json, os, sys
D = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('app_target', os.path.join(os.path.dirname(D), 'app_target.py')); AT = importlib.util.module_from_spec(spec); spec.loader.exec_module(AT)
LEGAL = json.load(open(os.path.join(os.path.dirname(D), 'legal', 'legal.json'), encoding='utf-8'))
WEB = LEGAL['web']
EULA = 'https://www.apple.com/legal/internet-services/itunes/dev/stdeula/'   # Appleの標準の利用規約（自分の規約を作ったら差しかえる）

# ---- ポイントとApp内課金（まさちゃんの指定。値段は税抜で決めたもの → 表示は税込＝×1.1） ----
GIFT = 1500
USE = [('レースの判定（画像の読み取りから記録まで）', '1レース200P'), ('単勝5連勝', '5レースまとめて200P'),
       ('Pカスタム：記録できる券種をふやす', '1つ500P'), ('自分だけのマザーデータを作る', '1つ15,000P')]
PACKS = [  # 製品ID・参照名・表示名・説明・ポイント・税抜
    ('jp.tengel.app.points500', 'ポイント500', '500ポイント', 'レースの判定などに使える500P', 500, 160),
    ('jp.tengel.app.points1000', 'ポイント1000', '1,000ポイント', 'レースの判定などに使える1,000P', 1000, 320),
    ('jp.tengel.app.points2000', 'ポイント2000', '2,000ポイント', 'レースの判定などに使える2,000P', 2000, 640),
    ('jp.tengel.app.points4000', 'ポイント4000', '4,000ポイント', 'レースの判定などに使える4,000P', 4000, 1280),
]
SUBS = [  # 製品ID・参照名・表示名・説明・毎月のポイント・うちボーナス・税抜（1か月・自動更新）
    ('jp.tengel.app.sub2000', '月2000Pプラン', '月2,000Pプラン', '毎月2,000Pが届く（1か月・自動更新）', 2000, 0, 580),
    ('jp.tengel.app.sub4400', '月4400Pプラン', '月4,400Pプラン', '毎月4,400P（うちボーナス400P）が届く', 4400, 400, 1160),
    ('jp.tengel.app.sub9200', '月9200Pプラン', '月9,200Pプラン', '毎月9,200P（うちボーナス1,000P）が届く', 9200, 1000, 1740),
]
tax = lambda y: round(y * 1.1)
yen = lambda y: f'{y:,}円'

NAME = 'テンゲル｜競馬予想・オッズ判定'
SUBTITLE = 'スクショで即判定。買い目と収支を記録'
PROMO = ('【初回ダウンロードで1500Pプレゼント】オッズ・距離・馬場のスクショを入れるだけで、レースを3つの層に判定。'
         '1着→2着のゾーンと馬番、3着まで一発で。単勝5連勝や収支の記録も、このアプリひとつで。')
DESCRIPTION = f'''【スクショを入れるだけで、レースを判定！】
オッズ・距離・馬場のスクショを選ぶだけで、レースの「荒れやすさ」を3つの層（A層＝堅・B層＝警戒・C層＝穴）に判定。推奨の買い目ゾーン（1着→2着と3着）と馬番、過去のデータでの参考的中率まで、一画面で見られる競馬の判定アプリです。

◆初回ダウンロードで{GIFT:,}Pプレゼント
はじめてアプリを入れた方に{GIFT:,}ポイントをプレゼント。すぐに{GIFT // 200}レース分の判定を試せます。

◆できること
・画像の読み取り：出馬表（距離・馬場・出走頭数）、単勝・複勝オッズ、3連単オッズ（人気順）のスクショを選ぶと、入力欄に自動で入ります。読み取りは端末の中で行い、画像はどこにも送りません
・3つの層に判定：3連単1位と単勝1位のオッズの比や馬場などから、決まったルールで判定
・推奨ゾーンと馬番：馬単の1着→2着のゾーン（人気・中穴・大穴・超大穴）と3連単の3着、あてはまる馬番
・参考的中率：アプリに入っている過去のデータや、自分で入れたデータで、そのゾーンが実際に出た割合
・買う馬を選ぶ：番号を押して、買う馬・買わない馬を切り替え
・買い目編集：区分ごとに、1着→2着と3着を自由に変更。変えると、その場で過去のデータでの的中数を計算
・単勝5連勝：5つのレースを読み取るだけで、予算に合わせて組み立て。ゾーンは「自分で選ぶ」か「ランダム」
・収支の記録：券種ごとの購入額・回収額と、月ごと・年ごとの回収率
・マザーデータ：参考値のもとになるデータ。結果を記録したレースがそのまま入るほか、Excel・CSVからも入れられます
・説明書つき：画面の写真つきの説明書を、アプリの中でいつでも読めます

◆ポイントについて
''' + '\n'.join(f'・{a}：{b}' for a, b in USE) + '''
・Pカスタムで記録をふやせる券種：複勝・枠複・枠単・馬連・ワイド・3連複（はじめは単勝・馬単・3連単）
・購入したポイントに有効期限はありません

◆ポイントの購入（価格は税込）
''' + '\n'.join(f'・{p[4]:,}P：{yen(tax(p[5]))}' for p in PACKS) + '''

◆サブスク（1か月・自動更新・価格は税込）
''' + '\n'.join(f'・{s[2]}：月額{yen(tax(s[6]))}' + (f'（うちボーナス{s[5]:,}P）' if s[5] else '') for s in SUBS) + '''
・サブスクで届いたポイントは、届いた日から30日間使えます（次の月のポイントが届いても、期限までは残ります）
・無料トライアルはありません
・ポイントはこの端末の中だけに保存されます。アプリを削除すると、ポイント・解放したもの・記録は消え、もどせません

◆自動更新のサブスクについて
・お支払い：購入を確定したときに、Apple Accountに請求されます
・自動更新：期間の終了日の24時間以上前に自動更新をオフにしない限り、自動で更新されます。更新の料金は、終了日の前24時間以内に請求されます
・確認と解約：「設定」→ 自分の名前 →「サブスクリプション」から、いつでも確認・解約できます。アプリを削除しても解約にはなりません
・期間の途中で解約しても、終了日まではそのまま使えます

◆ご利用にあたって
・本アプリは、過去のデータから傾向を分析して表示する道具です。参考的中率などは過去の実測で、これからの的中や利益を約束するものではありません
・馬券を買うかどうか、何を買うかは、ご自身の判断でお決めください。本アプリに馬券を買う機能はありません
・馬券は20歳になってから。20歳未満の方は、法律により馬券を購入できません
・競馬は無理のない範囲で楽しみましょう。のめり込みが心配なときは、ギャンブル依存症予防回復支援センター「サポートコール」0120-683-705（24時間・通話料無料）へ
・本アプリは個人が開発した非公式のアプリで、競馬の主催者・団体とは関係ありません
・画面の写真は架空のレースの例です

◆プライバシー
記録・設定・マザーデータは、すべて端末の中に保存します。画像の読み取りも端末の中で行い、画像はどこにも送りません。お支払いはAppleが処理し、開発者がカードなどの情報を受け取ることはありません。広告・アクセス解析はありません。

◆利用規約・プライバシーポリシー
利用規約：''' + EULA + '''
プライバシーポリシー：''' + WEB + '''privacy.html

◆対応OS
iOS 16以降のiPhone（iPadOS 16以降のiPadでも、iPhoneと同じ画面で使えます）'''
KEYWORDS = '3連単,三連単,万馬券,回収率,オッズ分析,データ分析,競馬アプリ,穴狙い'
SUPPORT_URL = WEB + 'support.html'
PRIVACY_URL = WEB + 'privacy.html'
COPYRIGHT = '2026 （Apple Developerに登録した名前）'
REVIEW_NOTES = '''This app helps users analyze horse-racing odds that they enter (or read from their own screenshots) and shows suggested "zones" (popularity ranges) for exacta and trifecta tickets, based on past race statistics stored on the device.

The app does NOT offer real-money gambling: there is no betting, no purchase of betting tickets, and no link to any betting service. Users can only record their own results and spending for personal bookkeeping.

Points (in-app currency):
- New users receive 1,500 points on first launch (no purchase needed).
- Judging a race (reading the user's screenshots on the device, showing the result) uses 200 points; a 5-race pick uses 200 points.
- Points can unlock more bet types for the record (500 each), an extra data slot (15,000) and cosmetic themes (1,000-7,000).
- Points are sold as consumable in-app purchases and granted monthly by auto-renewable subscriptions (Settings > ポイント). Purchased points never expire; subscription points last 30 days from delivery. No free trial.
- Points, unlocks and records are stored only on the device (the app says before buying that deleting the app erases them); a small Keychain marker (gift received, credited subscription transactions) prevents granting the same points twice.
- On first launch the app shows a notice screen (horse-race betting is for ages 20+, play responsibly, the app does not sell betting tickets and promises no profit) that the user confirms with 「はじめる」.
- iPhone-only (UIDeviceFamily 1, portrait); on iPad it runs in iPhone compatibility mode.

Reservations and notifications:
- After a judgment the user picks horses inside the suggested zones and taps 「買い目を予約」 (reserve picks) or 「このレースを諦める」 (skip). This only stores the user's own planned picks on the device; nothing is purchased.
- If the race start time is known, the app schedules a LOCAL notification 15 minutes after the start ("結果を確認しよう！"). UNUserNotificationCenter only; no server, no remote push. Permission is asked at the first reservation; notifications can be turned off in Settings > 結果確認のお知らせ.
- The user then enters the finishing order (or reads it from a result screenshot, on the device) and the app shows hit/miss per bet type for their own record.

Result effects (visual feedback only): saving a result shows a "PUSH" button; a tap plays a short animation (CSS/SVG; two rare variants play a bundled silent MP4 we rendered ourselves) and a board listing hit/miss per bet type, never money. Nothing is won or paid. Sounds are short synthesized clips bundled in the app; they respect the silent switch and mix with other apps' audio. Flashing stays under 3 per second; effects can be turned off or reduced in Settings > 的中の演出 (also follows iOS Reduce Motion). No network is used for any effect.

Themes (Settings > 着せ替え): 41 cosmetic themes (colors, bundled OFL fonts, animated header picture, PUSH and board style): 26 unlock with points, 3 reward owning 8/16/25 themes, 11 come with the 壁紙パック. Assets are bundled (CSS/SVG/WebP); animation stops with Reduce Motion.
Non-consumables: 壁紙パック (1,500 yen, 11 themes) and 結果ボードカスタム (2,200 yen, 22 board decorations) become usable step by step as races are read; both have 「購入を復元」.

How to review (no account or sign-in needed):
1. Open the 判定 (Judge) tab and tap 「入力例を入れる」 (Load example). A full judgment for a fictional race appears.
2. 「オッズ画像から読み取る」 (Read odds from images) recognizes text in the user's screenshots on the device (Vision). No image or text leaves the device.
3. Records and settings stay on the device; the app works offline. Backup and CSV export use the iOS share sheet.
4. Settings > データの更新 downloads an updated past-race data file (JSON data only, no executable code) from our GitHub Pages site. Settings > アプリの更新 checks the App Store for a newer version (app ID only). No user data is sent.

The app is for adults (18+). Betting on horse races is legal only for people aged 20 or older in Japan; the app shows this notice.'''

FIELDS = [  # (区分, 項目, 値, 上限, 単位, メモ)
    ('App情報', '名前', NAME, 30, 'chars', 'ホーム画面の名前は「テンゲル」のまま'),
    ('App情報', 'サブタイトル', SUBTITLE, 30, 'chars', ''),
    ('バージョン 1.0', 'プロモーション用テキスト', PROMO, 170, 'chars', '審査なしで、あとからいつでも変えられる（キャンペーンはここに書く）'),
    ('バージョン 1.0', '概要', DESCRIPTION, 4000, 'chars', 'ポイントの値段・サブスクの説明・利用規約とプライバシーのリンクはサブスクがあるアプリに必要（審査 3.1.2）'),
    ('バージョン 1.0', 'キーワード', KEYWORDS, 100, 'bytes', '名前・サブタイトルの言葉は入れなくても検索される'),
    ('バージョン 1.0', 'サポートURL', SUPPORT_URL, None, None, '販売者名とメールを入れて公開してから使える'),
    ('App情報', 'プライバシーポリシーURL', PRIVACY_URL, None, None, 'ポイント・サブスクのことを書き足してから使う'),
    ('バージョン 1.0', '著作権', COPYRIGHT, None, None, '「©」は自動で付く。名前はApple Developerに登録した名前（販売者名）'),
    ('バージョン 1.0', 'App Reviewへのメモ（英語）', REVIEW_NOTES, 4000, 'bytes', 'ポイントの仕組みをアプリで作ったあと、本物と同じか確かめる'),
]
# 紹介特典（アプリで作ったら、プロモーション用テキストに入れる候補。審査 3.1.1 に合うかを先に確かめる）
LATER = {'紹介特典（プロモーション用テキストの候補）': '【ユーザー紹介特典】サブスク入会＆紹介で1,600P、紹介で入会すると1,000Pプレゼント！'}


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
    OTHERS = ['netkeiba', 'ネットケイバ', 'JRA-VAN', 'SPAT4', 'オッズパーク', '楽天', 'ウマニティ', 'うまい馬券', 'TARGET', '競馬ブック', 'iPhone', 'iPad', 'Apple', 'Anthropic', 'Claude']
    for k, v in (('名前', NAME), ('サブタイトル', SUBTITLE), ('キーワード', KEYWORDS), ('プロモーション用テキスト', PROMO)):
        w = [x for x in OTHERS if x.lower() in v.lower()]
        if w:
            bad.append(f'{k}：ほかの会社・サービスの名前 {w}')
    kws = KEYWORDS.split(',')
    if len(set(kws)) != len(kws) or any(' ' in x for x in kws):
        bad.append('キーワード：重複か空白')
    for pid, ref, disp, desc, *_ in PACKS + [s[:4] + (0,) for s in SUBS]:
        if len(disp) > 30 or len(desc) > 45:
            bad.append(f'App内課金 {pid}：表示名{len(disp)}/30・説明{len(desc)}/45')
        w = [x for x in AT.FORBIDDEN if x in disp + desc]
        if w:
            bad.append(f'App内課金 {pid}：出さない言葉 {w}')
    if bad:
        raise SystemExit('掲載の文がAppleの決まりに合っていないよ：\n' + '\n'.join(bad))
    return {k: (nbytes(v) if unit == 'bytes' else len(v), lim, unit) for sec, k, v, lim, unit, _ in FIELDS}


IAP = {
    'consumable': [{'id': p[0], 'ref': p[1], 'name': p[2], 'desc': p[3], 'points': p[4], 'ex': p[5], 'inc': tax(p[5])} for p in PACKS],
    'subs_group': 'テンゲル ポイントのサブスク',
    'subs': [{'id': s[0], 'ref': s[1], 'name': s[2], 'desc': s[3], 'points': s[4], 'bonus': s[5], 'ex': s[6], 'inc': tax(s[6]), 'level': 3 - i} for i, s in enumerate(SUBS)],
    'use': USE, 'gift': GIFT,
}
ANSWERS = {
    'カテゴリ': ['プライマリ：スポーツ', 'セカンダリ：ユーティリティ'],
    '年齢制限指定': [
        'アプリ内の機能（保護者による制限・年齢確認・無制限のWebアクセス・ユーザー生成コンテンツ・メッセージ・広告・ソーシャルメディア）：すべて「いいえ」',
        '内容（暴力・性的な内容・言葉・恐怖・医療・アルコールやたばこ など）：すべて「なし」',
        'シミュレートされたギャンブル：「なし」（アプリの中で賭けはしない）／ギャンブル（実際のお金）：「いいえ」',
        '年齢カテゴリ：「より高い年齢区分に上書き」→ 18+（日本では馬券は20歳から）',
    ],
    'Appのプライバシー': [
        'データを収集していますか？：「いいえ」（記録・設定・画像は端末の中だけ。購入はAppleが処理して、開発者は受け取らない）',
        '紹介特典などでサーバーを使うときは「収集している」に変わる（ID・購入など）。そのときはプライバシーポリシーも直す',
    ],
    'App内課金（App Store Connect の「App内課金」）': [f'{p[1]}：製品ID {p[0]}・消耗型・表示名「{p[2]}」・説明「{p[3]}」・価格 {yen(tax(p[5]))}（税抜{yen(p[5])}）' for p in PACKS],
    'サブスクリプション（グループ「テンゲル ポイントのサブスク」）': [f'{s[1]}：製品ID {s[0]}・1か月・表示名「{s[2]}」・説明「{s[3]}」・価格 月額{yen(tax(s[6]))}（税抜{yen(s[6])}）・レベル{3 - i}' for i, s in enumerate(SUBS)],
    '価格および配信状況': ['配信する国と地域：日本だけ（EUで配信すると住所・電話が製品ページに出る）', 'アプリ本体：無料（ポイントとサブスクで収益）。有料Appの契約・口座・税の登録が先に必要'],
    '先に決めること': [
        'App Storeで選べる価格に「176円」などがあるか（なければ近い価格に合わせて、説明文と画面写真も直す）',
        'ポイントの期限：審査3.1.1で「買ったポイントは期限切れにできない」。説明文は「購入したポイントは期限なし・サブスクで届いたポイントは30日」にしてある',
        '紹介特典：作り方（サーバー／Appleのオファーコード）と審査3.1.1に合うかを確かめてから、プロモーション用テキストに入れる',
        '結果確認のお知らせ：ローカル通知だけ（プッシュ通知の権限・サーバーは使わない）。App Store Connect の「App のプライバシー」はデータ収集なしのまま',
        '的中ボタン（第3弾）：演出は CSS と SVG・音はアプリの中の m4a（通信なし・お金は出さない・1秒に3回までの点めつ・設定でオフと控えめ）。審査へのメモに書いてある',
    ],
}
MEDIA = {
    'preview_iphone': {'file': 'tengel_preview7_iphone_886x1920.mp4', 'size': '886×1920', 'where': 'iPhone 6.9インチの「Appプレビュー」（いちばん左＝最初に出る）。ポスターフレーム：9.6秒（「ゾーンまで判定!!」）'},
    'preview_ipad': {'file': 'tengel_preview7_ipad_1200x1600.mp4', 'size': '1200×1600', 'where': 'iPad 13インチの「Appプレビュー」。ポスターフレーム：9.6秒'},
    'shots_iphone69': {'dir': 'iphone_6.9', 'size': '1320×2868', 'where': 'iPhone 6.9インチのスクリーンショット（01〜10の順）'},
    'shots_ipad13': {'dir': 'ipad_13', 'size': '2064×2752', 'where': 'iPad 13インチのスクリーンショット（01〜10の順）'},
}


def main(out):
    counts = check()
    os.makedirs(out, exist_ok=True)
    data = {'fields': [{'sec': s, 'key': k, 'value': v, 'limit': lim, 'unit': u, 'note': n, 'count': counts[k][0]} for s, k, v, lim, u, n in FIELDS],
            'answers': ANSWERS, 'iap': IAP, 'later': LATER, 'media': MEDIA}
    json.dump(data, open(os.path.join(out, 'listing7.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    lines = ['テンゲル（ポイント版）　App Store Connect に入れる文（そのまま貼れる）', '']
    for s, k, v, lim, u, n in FIELDS:
        c = counts[k][0]
        lines += [f'■ {k}（{s}）' + (f'　{c}/{lim}{"バイト" if u == "bytes" else "文字"}' if lim else ''), v, '']
    for k, vs in ANSWERS.items():
        lines += [f'■ {k}'] + ['・' + x for x in vs] + ['']
    for k, v in LATER.items():
        lines += [f'■ {k}', v, '']
    open(os.path.join(out, '掲載テキスト_ポイント版.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    for k, (c, lim, u) in counts.items():
        print(f'{k}: {c}' + (f'/{lim} {u}' if lim else ''))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(D, 'out7'))
