"""マザーデータ①〜③に まとめて 入れる ための Excel の ひな形（第4.123版・2026/11/04 まさちゃん「Excelの入力できるベースのデータを作成して、ダウンロードできるようにして！」）
     python3 templates/make_template.py   → templates/mother_template.xlsx（リポジトリに 入れる・App Store版の 設定 → マザーデータ①〜③の 編集 →「入力用のExcel（ひな形）を保存」で 渡す）
   形は アプリが 読む「検証データの形」（A〜P列）のまま。シート名「検証データ」・見出しは アプリの「書き出す（CSV）」と 同じ。
   ・4行目の 記入例は A列が「例 …」の 文字なので 読み込まれない（日付として 読めない 行は とばす）
   ・Q列の チェックは アプリが 読まない（A〜P列だけ 読む）
   ・開催場の 名前・アプリに 入っている データ（テンゲルデータ）の 中身は 入れない（架空の 記入例だけ）
   何回 作っても 中身は 同じ（zip の 日付は 決めた 値に そろえる）。"""
import io
import os
import re
import zipfile

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'mother_template.xlsx')
HEAD = ['日付', 'R', '馬場', '距離', '頭数', '単勝1位', '3連単1位', '1着人気', '2着人気', '3着人気', '3連単5位', '3連単10位', '馬単払戻', '3連単払戻', '備考', '集計対象']
MARK = ['★', '★', '★', '◎', '◎', '★', '★', '★', '★', '○', '○', '○', '○', '○', '○', '○']
WIDTH = [13, 6, 8, 8, 7, 9, 10, 9, 9, 9, 10, 10, 10, 11, 18, 9, 16]
EXAMPLE = ['例 2026/11/14', 9, '良', 1400, 12, 2.1, 18.5, 1, 4, 2, 42.6, 78.9, 780, 2150, '', 1]
FIRST, LAST = 5, 504          # 入れる 行（500レース分）
FONT = '游ゴシック'
NAVY, YEL, GRAY = '1B2A4A', 'FFF8D6', 'EEF0F4'
thin = Side(style='thin', color='C9CED8')
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
FMT = {0: 'yyyy/mm/dd', 1: '0', 2: '@', 3: '0', 4: '0', 5: '0.0', 6: '0.0', 7: '0', 8: '0', 9: '0', 10: '0.0', 11: '0.0', 12: '#,##0', 13: '#,##0', 14: '@', 15: '0'}
COLS = 'ABCDEFGHIJKLMNOP'


def f(size=10, bold=False, color='1F2937', italic=False):
    return Font(name=FONT, size=size, bold=bold, color=color, italic=italic)


def build():
    wb = Workbook(); wb.properties.creator = 'テンゲル'; wb.properties.title = 'マザーデータ 入力用'
    ws = wb.active; ws.title = '検証データ'
    ws.sheet_properties.tabColor = NAVY
    # 1〜2行目：案内と 印
    ws['A1'] = 'テンゲル　マザーデータ①〜③ 入力用（1行＝1レース・黄色い行に入れてね）　★＝必ず入れる　◎＝判定に使う（入れてね）　○＝あれば（空でもOK）'
    ws['A1'].font = f(11, True, NAVY); ws.merge_cells('A1:Q1'); ws.row_dimensions[1].height = 22
    for i, m in enumerate(MARK):
        c = ws.cell(row=2, column=i + 1, value=m); c.font = f(10, True, 'B45309' if m == '★' else '475569'); c.alignment = Alignment(horizontal='center')
    # 3行目：見出し（アプリの「書き出す（CSV）」と 同じ）
    for i, h in enumerate(HEAD + ['チェック']):
        c = ws.cell(row=3, column=i + 1, value=h)
        c.font = f(10, True, 'FFFFFF'); c.fill = PatternFill('solid', fgColor=NAVY if i < 16 else '64748B')
        c.alignment = Alignment(horizontal='center', vertical='center'); c.border = BOX
    ws.row_dimensions[3].height = 20
    # 4行目：記入例（A列が 文字なので アプリは 読まない）
    for i, v in enumerate(EXAMPLE):
        c = ws.cell(row=4, column=i + 1, value=v); c.font = f(10, False, '6B7280', True); c.fill = PatternFill('solid', fgColor=GRAY); c.border = BOX
        c.alignment = Alignment(horizontal='center')
        if i and i in FMT: c.number_format = FMT[i]
    c = ws.cell(row=4, column=17, value='← 記入例（この行は読み込まれないよ）'); c.font = f(9, False, '6B7280', True)
    # 5〜504行目：入れる 行
    for r in range(FIRST, LAST + 1):
        for i in range(16):
            c = ws.cell(row=r, column=i + 1); c.fill = PatternFill('solid', fgColor=YEL); c.border = BOX; c.number_format = FMT[i]; c.font = f(10)
            c.alignment = Alignment(horizontal='left' if i == 14 else 'center')
        q = ws.cell(row=r, column=17, value=(
            f'=IF(COUNTA(A{r}:P{r})=0,"",IF(NOT(OR(ISNUMBER(A{r}),ISNUMBER(DATEVALUE(A{r})))),"日付を確認",IF(OR(NOT(ISNUMBER(B{r})),B{r}<1,B{r}>16),"Rを確認",'
            f'IF(ISNA(MATCH(C{r},{{"良","稍重","重","不良"}},0)),"馬場を確認",IF(OR(NOT(ISNUMBER(D{r})),NOT(ISNUMBER(E{r}))),"距離・頭数を確認",'
            f'IF(OR(NOT(ISNUMBER(F{r})),NOT(ISNUMBER(G{r})),F{r}<1,G{r}<F{r}),"オッズを確認",IF(OR(NOT(ISNUMBER(H{r})),NOT(ISNUMBER(I{r}))),"着順を確認","OK")))))))'))
        q.font = f(9, True, '0F766E'); q.alignment = Alignment(horizontal='center')
    for i, w in enumerate(WIDTH):
        ws.column_dimensions[(COLS + 'Q')[i]].width = w
    ws.freeze_panes = 'A5'
    ws.page_setup.orientation = 'landscape'; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0; ws.sheet_properties.pageSetUpPr.fitToPage = True   # 印刷するときは 横向き・横 1ページ
    ws.print_title_rows = '3:3'
    rng = lambda col: f'{col}{FIRST}:{col}{LAST}'

    def dv(col, **kw):
        d = DataValidation(allow_blank=True, showErrorMessage=True, showInputMessage=True, **kw); d.add(rng(col)); ws.add_data_validation(d)
    dv('A', type='date', operator='greaterThan', formula1='36526', promptTitle='日付', prompt='2026/11/14 のように入れてね', errorTitle='日付', error='2026/11/14 のように、日付で入れてね')
    dv('B', type='whole', operator='between', formula1='1', formula2='16', promptTitle='R', prompt='レース番号（1〜16）', errorTitle='R', error='1〜16 の数で入れてね')
    dv('C', type='list', formula1='"良,稍重,重,不良"', promptTitle='馬場', prompt='良・稍重・重・不良 から選んでね', errorTitle='馬場', error='良・稍重・重・不良 のどれかにしてね')
    dv('D', type='whole', operator='between', formula1='100', formula2='5000', promptTitle='距離', prompt='m（例 1400）', errorTitle='距離', error='m の数で入れてね（例 1400）')
    dv('E', type='whole', operator='between', formula1='1', formula2='18', promptTitle='頭数', prompt='出走頭数（例 12）', errorTitle='頭数', error='1〜18 の数で入れてね')
    dv('F', type='decimal', operator='between', formula1='1', formula2='999.9', promptTitle='単勝1位', prompt='いちばん低い単勝オッズ（例 2.1）', errorTitle='単勝1位', error='オッズ（例 2.1）を入れてね')
    dv('G', type='decimal', operator='between', formula1='1', formula2='99999', promptTitle='3連単1位', prompt='いちばん低い3連単オッズ（例 18.5）', errorTitle='3連単1位', error='オッズ（例 18.5）を入れてね')
    for col, nm in (('H', '1着'), ('I', '2着'), ('J', '3着')):
        dv(col, type='whole', operator='between', formula1='1', formula2='18', promptTitle=f'{nm}人気', prompt=f'{nm}の馬の単勝人気（1〜18）', errorTitle=f'{nm}人気', error='1〜18 の数で入れてね')
    dv('K', type='decimal', operator='between', formula1='1', formula2='999999', promptTitle='3連単5位', prompt='3連単の人気5位のオッズ（記録用・なくてもOK）', errorTitle='3連単5位', error='オッズを入れてね')
    dv('L', type='decimal', operator='between', formula1='1', formula2='999999', promptTitle='3連単10位', prompt='3連単の人気10位のオッズ（記録用・なくてもOK）', errorTitle='3連単10位', error='オッズを入れてね')
    dv('M', type='whole', operator='between', formula1='0', formula2='99999999', promptTitle='馬単払戻', prompt='100円あたりの払戻（例 780）。なくてもOK', errorTitle='馬単払戻', error='円の数で入れてね')
    dv('N', type='whole', operator='between', formula1='0', formula2='99999999', promptTitle='3連単払戻', prompt='100円あたりの払戻（例 2150）。なくてもOK', errorTitle='3連単払戻', error='円の数で入れてね')
    dv('P', type='list', formula1='"1,0"', promptTitle='集計対象', prompt='1＝集計に入れる（空なら1）／0＝入れない', errorTitle='集計対象', error='1 か 0 にしてね')

    # 説明の シート
    hs = wb.create_sheet('説明'); hs.sheet_properties.tabColor = 'B45309'
    hs.column_dimensions['A'].width = 6; hs.column_dimensions['B'].width = 14; hs.column_dimensions['C'].width = 10; hs.column_dimensions['D'].width = 58; hs.column_dimensions['E'].width = 14
    rows = [('t', 'テンゲル　マザーデータ①〜③の入力用Excel（ひな形）'), ('', ''),
            ('h', '入れ方'),
            ('p', '①「検証データ」のシートの黄色い行（5行目から）に、1行＝1レースで入れる'),
            ('p', '②このまま保存する（ファイルの形は .xlsx のまま。CSVで保存してもOK）'),
            ('p', '③テンゲルの 設定 → テンゲルデータ・マザーデータ → マザーデータ①〜③の「編集」→「Excel・CSVファイルを選ぶ」で、このファイルを選ぶ'),
            ('p', '④読み取った走数と期間を確かめて、「足す」（いまのレースは残す）か「入れ替える」（ファイルのとおり）を押す'),
            ('', ''), ('h', '列ごとの入れ方（★＝必ず　◎＝判定に使う　○＝あれば）'), ('c', ('列', '項目', '', '入れ方', '例'))]
    for i, (h, m) in enumerate(zip(HEAD, MARK)):
        how = ['2026/11/14 のように（Excelの日付）', 'レース番号（1〜16）', '良・稍重・重・不良 のどれか', 'm', '出走頭数', 'いちばん低い単勝オッズ', 'いちばん低い3連単オッズ',
               '1着の馬の単勝人気（馬番ではなく人気）', '2着の馬の単勝人気', '3着の馬の単勝人気（3着の判定に使う）', '3連単の人気5位のオッズ（記録用）', '3連単の人気10位のオッズ（記録用）',
               '100円あたりの払戻（回収率の計算に使う）', '100円あたりの払戻', 'メモ（自由）', '1＝集計に入れる（空なら1）／0＝入れない'][i]
        ex = ['2026/11/14', '9', '良', '1400', '12', '2.1', '18.5', '1', '4', '2', '42.6', '78.9', '780', '2150', '', '1'][i]
        rows.append(('r', (COLS[i] + '列', h, m, how, ex)))
    rows += [('', ''), ('h', '気をつけること'),
             ('p', '・シートの名前「検証データ」と、列の順番（A〜P列）は変えないでね（3行目の見出しはそのままでOK）'),
             ('p', '・4行目の記入例と、1〜3行目の案内・見出しは読み込まれないよ（消してもOK）。Q列の「チェック」も読み込まれないよ'),
             ('p', '・Q列に「OK」と出れば、その行は判定に使える形。「○○を確認」と出たら、そこを入れ直してね'),
             ('p', '・開催場の列はないよ。1つのマザーデータには、1つの開催場のレースを入れるのがおすすめ（同じ日付・Rのレースは同じレースとして比べるよ）'),
             ('p', '・同じ日付・Rのレースが、もうマザーデータに入っているときは「足す」で新しい中身に変わるよ'),
             ('p', '・テンゲルデータには入れられないよ（マザーデータ①〜③だけ）'),
             ('p', '・ファイルは、この端末の中で読むだけ。どこにも送らないよ')]
    hs.page_setup.orientation = 'portrait'; hs.page_setup.fitToWidth = 1; hs.page_setup.fitToHeight = 0; hs.sheet_properties.pageSetUpPr.fitToPage = True
    r = 1
    for kind, v in rows:
        if kind == 't':
            c = hs.cell(row=r, column=1, value=v); c.font = f(14, True, NAVY)
        elif kind == 'h':
            c = hs.cell(row=r, column=1, value=v); c.font = f(11, True, 'B45309')
        elif kind == 'p':
            c = hs.cell(row=r, column=1, value=v); c.font = f(10)
        elif kind in ('c', 'r'):
            for j, x in enumerate(v):
                c = hs.cell(row=r, column=j + 1, value=x); c.border = BOX
                c.font = f(10, kind == 'c', 'FFFFFF' if kind == 'c' else ('B45309' if x == '★' else '1F2937'))
                if kind == 'c': c.fill = PatternFill('solid', fgColor=NAVY)
                c.alignment = Alignment(horizontal='left' if j == 3 else 'center', vertical='center', wrap_text=j == 3)
        r += 1
    wb.active = 0
    bio = io.BytesIO(); wb.save(bio)
    return bio.getvalue()


def fixed_zip(data):
    """zip の 中の 日付を 決めた 値に（何回 作っても 同じ バイト）"""
    zin = zipfile.ZipFile(io.BytesIO(data)); out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zo:
        for it in zin.infolist():
            zi = zipfile.ZipInfo(it.filename, date_time=(2026, 11, 4, 0, 0, 0)); zi.compress_type = zipfile.ZIP_DEFLATED; zi.external_attr = 0o600 << 16
            body = zin.read(it.filename)
            if it.filename == 'docProps/core.xml':   # 作った 日時（openpyxl は いまの 時刻を 入れる）も 決めた 値に
                body = re.sub(rb'(<dcterms:(?:created|modified)[^>]*>)[^<]*(</dcterms:(?:created|modified)>)', rb'\g<1>2026-11-04T00:00:00Z\g<2>', body)
            zo.writestr(zi, body)
    return out.getvalue()


if __name__ == '__main__':
    import sys
    data = build()
    if len(sys.argv) > 1 and sys.argv[1] == '--raw':   # LibreOffice で 計算した あとの ファイルを 使う ときの 下書き
        open(OUT, 'wb').write(data)
    else:
        open(OUT, 'wb').write(fixed_zip(data))
    print(OUT, len(open(OUT, 'rb').read()), 'bytes')
