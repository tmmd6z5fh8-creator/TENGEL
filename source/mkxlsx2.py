# openpyxlの出力を、Excelが保存したファイルに近い形に直す：共有文字列（ふりがな rPh・リッチテキスト入り）・相対パス
import zipfile, re, html
src = 'xt/test_13.xlsx'; dst = 'xt/test_excel_like.xlsx'
zin = zipfile.ZipFile(src)
files = {i.filename: zin.read(i.filename) for i in zin.infolist()}
sst, idx = [], {}
def sid(t):
    if t not in idx: idx[t] = len(sst); sst.append(t)
    return idx[t]
for name in [n for n in files if n.startswith('xl/worksheets/sheet')]:
    s = files[name].decode('utf8')
    def rep(m):
        ref, text = m.group(1), html.unescape(m.group(2))
        return f'<c r="{ref}" t="s"><v>{sid(text)}</v></c>'
    s = re.sub(r'<c r="([A-Z]+\d+)" t="inlineStr"><is><t>(.*?)</t></is></c>', rep, s)
    files[name] = s.encode('utf8')
def si(t):
    e = html.escape(t, quote=False)
    if t == '稍重': return f'<si><t>{e}</t><rPh sb="0" eb="2"><t>ヤヤオモ</t></rPh><phoneticPr fontId="1"/></si>'
    if t == '不良': return '<si><r><t>不</t></r><r><rPr><b/></rPr><t>良</t></r><rPh sb="0" eb="2"><t>フリョウ</t></rPh></si>'
    if t == '良': return f'<si><t>{e}</t><rPh sb="0" eb="1"><t>リョウ</t></rPh></si>'
    return f'<si><t xml:space="preserve">{e}</t></si>'
files['xl/sharedStrings.xml'] = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="%d" uniqueCount="%d">' % (len(sst), len(sst)) + ''.join(si(t) for t in sst) + '</sst>').encode('utf8')
rels = files['xl/_rels/workbook.xml.rels'].decode('utf8').replace('Target="/xl/', 'Target="')
rels = rels.replace('</Relationships>', '<Relationship Id="rId99" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" Target="sharedStrings.xml"/></Relationships>')
files['xl/_rels/workbook.xml.rels'] = rels.encode('utf8')
ct = files['[Content_Types].xml'].decode('utf8').replace('</Types>', '<Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/></Types>')
files['[Content_Types].xml'] = ct.encode('utf8')
zout = zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED)
for n, d in files.items(): zout.writestr(n, d)
zout.close()
z = zipfile.ZipFile(dst); print(z.read('xl/_rels/workbook.xml.rels').decode()[:300]); print(z.read('xl/sharedStrings.xml').decode()[:500])
s3 = z.read('xl/worksheets/sheet3.xml').decode(); i = s3.find('<row r="4"'); print(s3[i:i+300])
