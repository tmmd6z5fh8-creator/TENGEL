import json, datetime, openpyxl, zipfile, shutil, re, os, sys
from openpyxl.styles import PatternFill
os.makedirs('xt', exist_ok=True)
hist = json.load(open('hist.json', encoding='utf8'))
def mk(path, extra, text_dates=False):
    wb = openpyxl.Workbook()
    ws0 = wb.active; ws0.title = '使い方'; ws0['A1'] = 'テンゲルⅢ　大井姫フィルター【第13改訂版】'
    ws1 = wb.create_sheet('当日入力'); ws1['A1'] = '当日入力シート'; ws1['A3'] = 8; ws1['B3'] = 1200
    ws = wb.create_sheet('検証データ')
    ws['A1'] = '検証データ（大井・馬単＋3連単3着）第13改訂版'
    ws['A2'] = '黄色＝入力（A〜P）／灰色＝数式'
    hdr = ['日付','R','馬場','距離(m)','頭数','単勝1位','3連単1位','1着人気','2着人気','3着人気','3連単5位','3連単10位','馬単払戻(円)','3連単払戻(円)','備考','集計対象','比','層']
    for i, h in enumerate(hdr): ws.cell(row=3, column=i+1, value=h)
    rows = hist + extra
    for j, r in enumerate(rows):
        y, m, d = map(int, r['date'].split('-'))
        rr = 4 + j
        if text_dates: ws.cell(row=rr, column=1, value=f'{y}/{m}/{d}')
        else:
            c = ws.cell(row=rr, column=1, value=datetime.datetime(y, m, d)); c.number_format = 'm/d'
        vals = [r['r'], r['baba'], r['dist'], r['n'], r['tan1'], r['s1'], r['p1'], r['p2'], r['p3'], r.get('s5'), r.get('s10'), r.get('umatanPay'), r.get('sanrenPay'), r.get('note') or None, r['cnt']]
        for k, v in enumerate(vals):
            if v is not None: ws.cell(row=rr, column=k+2, value=v)
        ws.cell(row=rr, column=17, value=f'=ROUND(G{rr}/F{rr},1)')
        ws.cell(row=rr, column=18, value=f'=IF(C{rr}="重","A層","?")')
    for rr in range(4 + len(rows), 4 + len(rows) + 30):  # 空の灰色の行（数式だけ）
        ws.cell(row=rr, column=17, value=f'=IF(A{rr}="","",ROUND(G{rr}/F{rr},1))')
    wb.create_sheet('設定')['A1'] = '設定'
    wb.save(path)
extra = [
 {'date':'2026-10-08','r':1,'baba':'良','dist':1200,'n':12,'tan1':2.1,'s1':18.5,'p1':1,'p2':3,'p3':2,'s5':31.2,'s10':52.0,'umatanPay':560,'sanrenPay':1230,'note':'','cnt':1},
 {'date':'2026-10-08','r':2,'baba':'良','dist':1400,'n':14,'tan1':1.8,'s1':25.0,'p1':4,'p2':1,'p3':3,'s5':None,'s10':None,'umatanPay':2110,'sanrenPay':None,'note':'','cnt':1},
 {'date':'2026-10-08','r':3,'baba':'稍重','dist':1600,'n':11,'tan1':3.0,'s1':70.2,'p1':7,'p2':2,'p3':None,'s5':None,'s10':None,'umatanPay':None,'sanrenPay':None,'note':'3着は確認中','cnt':1},
 {'date':'2026-10-08','r':4,'baba':'重','dist':1200,'n':9,'tan1':1.5,'s1':9.9,'p1':2,'p2':1,'p3':5,'s5':None,'s10':None,'umatanPay':450,'sanrenPay':None,'note':'','cnt':1},
]
mk('xt/test_13.xlsx', extra)
mk('xt/test_textdates.xlsx', extra[:2], text_dates=True)
print('made xt/test_13.xlsx, xt/test_textdates.xlsx（共有文字列・ふりがな入りは mkxlsx2.py）')
