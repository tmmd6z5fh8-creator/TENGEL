# テンゲルの「このアプリについて」と、公開するページ（プライバシーポリシー・特定商取引法に基づく表記・サポート）
#   about(target)  → アプリの中の「このアプリについて」に入れる中身（build_pwa.py が window.__ABOUT に入れる）
#   pages(out)     → 公開するページを out/legal/ に作る。販売する人の欄（legal.json）が空のページは作らない（返り値＝作ったページ）
#   python3 build_legal.py preview <フォルダ>  → 空の欄を【要記入】にして全部のページを作る（確認用。公開しない）
# target：'app'＝App Store版（tengel://）／'web'＝Web版（ホーム画面のアプリ）
import html, json, os, re, sys
D = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(os.path.dirname(D), 'ios', 'fonts')
CONSULT = 'https://www.cas.go.jp/jp/seisaku/gamble/'


def cfg():
    c = json.load(open(os.path.join(D, 'legal.json'), encoding='utf-8'))
    return {k: (v.strip() if isinstance(v, str) else v) for k, v in c.items() if not k.startswith('_')}


def esc(s):
    return html.escape(s or '')


def ready(c, kind):
    """そのページを公開できるか（販売する人の欄が入っているか）"""
    need = {'privacy': ('seller', 'email'), 'support': ('email',), 'tokushoho': ('seller', 'email')}[kind]
    return all(c.get(k) for k in need)


DISCLAIMER = '''<ul>
<li>テンゲルは、過去のレースのデータから傾向を分析して表示する道具です。参考的中率などは過去の実測で、これからの的中や利益を約束するものではありません。</li>
<li>馬券を買うかどうか、何を買うかは、ご自身の判断でお決めください。</li>
<li><b>馬券は20歳になってから。</b>20歳未満の方は、法律により馬券を購入できません。</li>
<li>競馬は無理のない範囲で楽しみましょう。のめり込みが心配なときは、ひとりで悩まずに相談してください。<br>
ギャンブル依存症予防回復支援センター「サポートコール」<a href="tel:0120683705">0120-683-705</a>（年中無休・24時間・通話料無料）<br>
<a href="''' + CONSULT + '''" target="_blank" rel="noopener">相談窓口の案内（内閣官房 ギャンブル等依存症対策推進本部）</a></li>
</ul>'''

NOTICES = '''<p>テンゲルは個人が開発した非公式のアプリです。日本中央競馬会（JRA）、地方競馬全国協会（NAR）、各地の競馬の主催者とは関係ありません。</p>
<ul>
<li>「JRA」「WIN5」は、日本中央競馬会の商標または登録商標です。</li>
<li>iPhone、iPad、Safariは、米国およびその他の国で登録されたApple Inc.の商標です。iPhoneの商標は、アイホン株式会社のライセンスにもとづき使用されています。</li>
<li>Excelは、米国Microsoft Corporationの米国およびその他の国における登録商標または商標です。</li>
<li>Claude、Anthropicは、Anthropic, PBCの商標です。</li>
<li>そのほか、記載されている会社名・団体名・商品名・サービス名は、各社・各団体の商標または登録商標です。</li>
</ul>'''


# App Store版（アプリの中・公開するページ）：競馬場・団体・商標（JRA・WIN5 など）の名前は出さない（アプリの中でも使っていない）。Claude・Anthropic も使わない（画像の読み取りは端末の中）
NOTICES_APP = '''<p>テンゲルは個人が開発した非公式のアプリです。競馬の主催者・団体とは関係ありません。</p>
<ul>
<li>iPhone、iPad、Safariは、米国およびその他の国で登録されたApple Inc.の商標です。iPhoneの商標は、アイホン株式会社のライセンスにもとづき使用されています。</li>
<li>Excelは、米国Microsoft Corporationの米国およびその他の国における登録商標または商標です。</li>
<li>そのほか、記載されている会社名・団体名・商品名・サービス名は、各社・各団体の商標または登録商標です。</li>
</ul>'''


def notices(target):
    return NOTICES_APP if target == 'app' else NOTICES


def privacy(c, target, mark=False):
    blank = '【要記入】' if mark else ''
    who = esc(c.get('seller')) or blank
    mail = esc(c.get('email')) or blank
    app = target == 'app'
    s = '''<h3>1. 基本の考え方</h3>
<p>テンゲル（以下「本アプリ」）は、利用者の個人情報や使い方の情報を、開発者が集めることも、受け取ることもありません。本アプリには、広告・アクセス解析・トラッキングの仕組みは入っていません。</p>
<h3>2. 端末の中に保存する情報</h3>
<p>次の情報は、利用者の端末の中（本アプリの保存領域）にだけ保存します。開発者には送りません。</p>
<ul>
<li>買ったレースの記録・メモ、''' + ('5重勝の記録' if app else 'WIN5の記録') + '''</li>
<li>買い目の設定、マザーデータ（利用者が取り込んだExcel・CSVのデータや、自分で入れたレースのデータを含む）</li>
''' + ('' if app else '<li>画像の読み取りに使うAPIキー（利用者が入れた場合）</li>\n') + '''</ul>
''' + ('<p>記録と設定は、端末の中の自動バックアップのファイルにも保存します。これらは、端末のバックアップ（iCloudバックアップなど）に含まれることがあります。</p>\n' if app else
       '<p>これらはブラウザの保存領域に保存します。ホーム画面のアイコンやWebサイトのデータを消すと、いっしょに消えます。</p>\n') + '''<h3>3. 外部に送る情報</h3>
<ul>
''' + ('<li><b>画像の読み取り：</b>利用者が選んだスクリーンショット画像は、端末の中（iOS・iPadOS の文字認識の機能）で読み取ります。画像も読み取った文字も、外部には送りません。</li>\n' if app else
       '<li><b>画像の読み取り：</b>利用者が画像を選んで読み取りを使ったときだけ、選んだスクリーンショット画像と読み取りの指示を、利用者のAPIキーで Anthropic, PBC のAPIへ直接送ります。送った内容の扱いは、Anthropic, PBC の規約とプライバシーポリシーに従います。開発者は内容を受け取りません。</li>\n') + ('<li><b>アプリの更新の確認：</b>アプリを開いたとき（12時間に1回まで）と「新しい版があるか確認」を押したときに、App Storeに新しい版が出ているかを Apple Inc. に問い合わせます。送るのは本アプリのIDと国だけで、利用者の記録や設定は送りません。通信の仕組み上、IPアドレスなどが Apple Inc. に送られます。</li>\n'
       '<li><b>データの更新：</b>アプリを開いたとき（12時間に1回まで）と「新しいデータがあるか確認」を押したときに、開発者が GitHub Pages（GitHub, Inc.）で公開しているレースのデータを読み込みます。利用者の記録や設定は送りません。通信の仕組み上、IPアドレスなどが GitHub, Inc. に送られます。</li>\n'
       '<li><b>CM（紹介動画）：</b>見るときだけ、動画を GitHub Pages（GitHub, Inc.）から読み込みます。このとき、通信の仕組み上、IPアドレスなどが GitHub, Inc. に送られます。</li>\n'
       '<li><b>ファイルに保存・共有：</b>利用者が選んだ保存先・共有先に、バックアップやCSVのファイルを渡します。</li>\n' if app else
       '<li><b>ページの読み込み：</b>本アプリ（Web版）は GitHub Pages（GitHub, Inc.）で公開しています。開いたり更新したりするときに、通信の仕組み上、IPアドレスなどが GitHub, Inc. に送られます。</li>\n'
       '<li><b>文字（フォント）：</b>Google Fonts（Google LLC）から文字の形を読み込みます。このとき、IPアドレスなどが Google LLC に送られます。</li>\n') + '''<li><b>外部のページ：</b>リンクを押したときは、Safariなどのブラウザで開きます。</li>
</ul>
<h3>4. 第三者への提供</h3>
<p>開発者は利用者の情報を持っていないため、第三者に提供することはありません。</p>
<h3>5. 情報の削除</h3>
<p>記録は本アプリの中で削除できます。''' + ('本アプリを削除すると、端末の中の記録・設定・自動バックアップはすべて削除されます。' if app else 'APIキーは「設定 → 画像の読み取り → キーを消す」で削除できます。') + '''</p>
<h3>6. 対象年齢</h3>
<p>本アプリは20歳以上の方を対象としています（20歳未満の方は、法律により馬券を購入できません）。</p>
<h3>7. 変更</h3>
<p>このポリシーを変更するときは、本アプリまたはこのページでお知らせします。</p>
'''
    if who or mail:
        s += f'<h3>8. お問い合わせ</h3>\n<p>{who}{"<br>" if who and mail else ""}{"メール：" + mail if mail else ""}</p>\n'
    s += f'<p class="small">制定：{esc(c.get("enacted"))}</p>'
    return s


def tokushoho(c, mark=False):
    blank = '【要記入】' if mark else ''
    req = '請求があった場合は、遅滞なく開示します。'
    rows = [
        ('販売事業者', esc(c.get('seller')) or blank),
        ('運営責任者', esc(c.get('seller')) or blank),
        ('所在地', esc(c.get('address')) or req),
        ('電話番号', esc(c.get('phone')) or req),
        ('メールアドレス', esc(c.get('email')) or blank),
        ('販売価格', 'App Storeの販売ページに表示している価格（税込）'),
        ('商品代金以外に必要な料金', 'インターネットの通信料（アプリの更新・データの更新・紹介動画を見るとき）。アプリの中に、追加で支払う機能はありません'),
        ('支払方法', 'App Storeで利用できる支払方法'),
        ('支払時期', 'App Storeで購入の手続きをしたとき（Appleの規約によります）'),
        ('引渡時期', '購入の手続きが終わったあと、すぐにダウンロードできます'),
        ('返品・キャンセル', 'デジタルコンテンツの性質上、購入後の返品・キャンセルはお受けしていません。返金については、Appleの返金の手続き（reportaproblem.apple.com）をご利用ください'),
        ('動作環境', 'iOS 16以降のiPhone、iPadOS 16以降のiPad'),
        ('表示についての注意', '本アプリの分析は過去のデータにもとづく参考情報で、的中や利益を約束するものではありません'),
    ]
    return '<table class="tk"><tbody>' + ''.join(f'<tr><th scope="row">{k}</th><td>{v}</td></tr>' for k, v in rows) + '</tbody></table>'


def fonts_html():
    """アプリに入れたフォントの著作権表示とライセンス（SIL OFL 1.1）"""
    rows = [('BIZ UDPGothic', 'OFL-BIZUDPGothic.txt'), ('Dela Gothic One', 'OFL-DelaGothicOne.txt'), ('IBM Plex Mono', 'OFL-IBMPlexMono.txt')]
    out, body = [], None
    for name, f in rows:
        t = open(os.path.join(FONTS_DIR, f), encoding='utf-8').read().strip()
        head, rest = t.split('\n', 1)
        out.append(f'<li><b>{esc(name)}</b><br><span class="small">{esc(head)}</span></li>')
        m = re.search(r'-{10,}\s*\nSIL OPEN FONT LICENSE.*', rest, re.S)
        assert m, f
        body = body or m.group(0)
    return ('<p>このアプリでは、次のフォントを SIL Open Font License, Version 1.1 にしたがって使っています（フォントのファイルは変えていません）。</p><ul>' + ''.join(out) + '</ul>'
            f'<pre class="ofl">{esc(body)}</pre>')


def about(target):
    c = cfg(); app = target == 'app'; base = c.get('web') or ''
    links = {k: (base + k + '.html' if app and base and ready(c, k) else None) for k in ('privacy', 'tokushoho', 'support')}
    return {
        'target': target, 'appName': c.get('app_name') or 'テンゲル',
        'disclaimer': DISCLAIMER, 'notices': notices(target), 'privacy': privacy(c, target),
        'tokushoho': tokushoho(c) if app and ready(c, 'tokushoho') else None,
        'fonts': fonts_html() if app else None,
        'email': c.get('email') or None, 'links': links,
    }


PAGE_CSS = '''*{box-sizing:border-box}html{-webkit-text-size-adjust:100%;background:#ECEEF3}body{margin:0;background:#ECEEF3;color:#141A2E;font:15px/1.75 "Hiragino Sans","Hiragino Kaku Gothic ProN","Yu Gothic UI",Meiryo,sans-serif}
header{background:#16203D;color:#F3F0E6;border-bottom:3px solid #E2A23B;padding:18px 16px}header .in,main{max-width:760px;margin:0 auto}
header p{margin:0;font-size:12.5px;opacity:.8;letter-spacing:.06em}header h1{margin:4px 0 0;font-size:21px;line-height:1.4}
main{padding:20px 16px 48px}section{background:#fff;border:1px solid #D7DBE4;border-radius:12px;padding:16px 18px;margin:0 0 16px}
h2{font-size:17px;margin:0 0 10px}h3{font-size:15px;margin:18px 0 6px}h3:first-child{margin-top:0}p{margin:0 0 10px}ul{margin:0 0 10px;padding-left:1.3em}li{margin:3px 0}
a{color:#1B4FA8}.small{font-size:12.5px;color:#5A6175}
table.tk{width:100%;border-collapse:collapse;font-size:14px}table.tk th,table.tk td{border-top:1px solid #E3E6EE;padding:9px 8px;text-align:left;vertical-align:top}
table.tk th{width:32%;color:#3A4159;font-weight:700}
@media (max-width:560px){table.tk th,table.tk td{display:block;width:auto}table.tk th{padding-bottom:0}table.tk td{border-top:0;padding-top:2px}}
nav.links{display:flex;flex-wrap:wrap;gap:8px 16px;font-size:14px}footer{max-width:760px;margin:0 auto;padding:0 16px 32px;font-size:12px;color:#5A6175}
@media (prefers-color-scheme:dark){html,body{background:#0C1121;color:#ECEEF5}header{background:#090E1C}section{background:#141B31;border-color:#2A3457}table.tk th,table.tk td{border-color:#2A3457}table.tk th{color:#C9CEDD}a{color:#8CB8F0}.small,footer{color:#9BA3BB}}'''


def page(title, body, c):
    nav = '<nav class="links"><a href="support.html">サポート</a><a href="privacy.html">プライバシーポリシー</a><a href="tokushoho.html">特定商取引法に基づく表記</a></nav>'
    return f'''<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}｜{esc(c.get("app_name") or "テンゲル")}</title><meta name="robots" content="noindex">
<style>{PAGE_CSS}</style></head><body>
<header><div class="in"><p>{esc(c.get("app_name") or "テンゲル")}（iPhone・iPadアプリ）</p><h1>{esc(title)}</h1></div></header>
<main>{body}<section>{nav}</section></main>
<footer>© {esc(c.get("seller") or "テンゲル")}</footer>
</body></html>
'''


def pages(out, mark=False):
    """公開するページを out/legal/ に作る（mark=True は確認用：空の欄を【要記入】にして全部作る）"""
    c = cfg(); made = []
    d = os.path.join(out, 'legal'); os.makedirs(d, exist_ok=True)
    if mark or ready(c, 'privacy'):
        open(os.path.join(d, 'privacy.html'), 'w', encoding='utf-8').write(page('プライバシーポリシー', f'<section>{privacy(c, "app", mark)}</section>', c)); made.append('privacy.html')
    if mark or ready(c, 'tokushoho'):
        open(os.path.join(d, 'tokushoho.html'), 'w', encoding='utf-8').write(page('特定商取引法に基づく表記', f'<section>{tokushoho(c, mark)}</section>', c)); made.append('tokushoho.html')
    if mark or ready(c, 'support'):
        mail = esc(c.get('email')) or ('【要記入】' if mark else '')
        body = (f'<section><h2>テンゲルについて</h2><p>テンゲルは、競馬のオッズから「荒れやすさ」を判定して、買い目のゾーンを提案し、結果と収支を記録できるアプリです。記録はすべて端末の中に保存されます。</p></section>'
                f'<section><h2>お問い合わせ</h2><p>ご質問・不具合のご連絡は、メールでお願いします。<br>メール：{mail}</p><p class="small">返信まで数日いただくことがあります。不具合のときは、アプリの版（設定 → このアプリについて）と、画面のスクリーンショットを添えていただけると助かります。</p></section>'
                f'<section><h2>ご利用にあたって</h2>{DISCLAIMER}</section><section><h2>非公式のアプリです・商標について</h2>{NOTICES_APP}</section>')
        open(os.path.join(d, 'support.html'), 'w', encoding='utf-8').write(page('サポート', body, c)); made.append('support.html')
    if not made:
        os.rmdir(d)
    return made


if __name__ == '__main__':
    if len(sys.argv) >= 3 and sys.argv[1] == 'preview':
        print('preview', pages(sys.argv[2], mark=True))
    else:
        print(json.dumps({k: (v[:60] + '…' if isinstance(v, str) and len(v) > 60 else v) for k, v in about(sys.argv[1] if len(sys.argv) > 1 else 'app').items()}, ensure_ascii=False, indent=1))
