# まさちゃんの元データと同じ形のテスト用Excel：分析シート（1行1レース）・分析表（1行1日・Rごとに4列）・馬場フィルター（元データ_距離馬場）
import json, openpyxl
hist = json.load(open('hist_280.json', encoding='utf8'))   # テストの土台（10/7までの280走で固定）
def serial(d):
    import datetime
    return (datetime.date.fromisoformat(d) - datetime.date(1899, 12, 30)).days
rows = sorted(hist, key=lambda r: (r['date'], r['r']))
# 分析シート
wb = openpyxl.Workbook(); ws = wb.active; ws.title = '競馬分析表'
ws.append(['凡例：黄色いセルに入力してください（日付・R・馬場・距離・出馬数・結果）'])
ws.append(['日付', 'R', '馬場', '距離(m)', '出馬数', '結果'])
for r in rows:
    res = '-'.join(f'{x}位' for x in [r.get('p1'), r.get('p2'), r.get('p3')] if x)
    ws.append([serial(r['date']), r['r'], r['baba'], r['dist'], r['n'], res])
wb.create_sheet('使い方').append(['入力ガイド'])
wb.save('xt/raw_bunseki_sheet.xlsx')
# 分析表（1行1日、Rごとに 単勝1位・3連単1位・結果・頭数）
wb = openpyxl.Workbook(); ws = wb.active; ws.title = '競馬分析表'
ws.append(['凡例：黄色いセルに入力してください（日付・単勝1位・3連単1位・結果）'])
h1 = ['日']; h2 = ['']
for k in range(1, 13): h1 += [f'{k}R', '', '', '']; h2 += ['単勝1位', '3連単1位', '結果', '頭数' if k == 1 else '']
ws.append(h1); ws.append(h2)
ws.append(['9/2'] + ['①番', '①-②-③', '的中', ''] * 12)
days = {}
for r in rows: days.setdefault(r['date'], {})[r['r']] = r
for d, rs in days.items():
    line = [serial(d)]
    for k in range(1, 13):
        x = rs.get(k)
        line += [x['tan1'], x['s1'], '-'.join(f'{p}位' for p in [x.get('p1'), x.get('p2'), x.get('p3')] if p), None] if x else [None] * 4
    ws.append(line)
wb.save('xt/raw_bunseki_hyo.xlsx')
# 馬場フィルター（元データ_距離馬場）
wb = openpyxl.Workbook(); ws = wb.active; ws.title = 'データ処理メモ'; ws.append(['メモ'])
ws2 = wb.create_sheet('元データ_距離馬場')
ws2.append(['大井競馬　元データ']); ws2.append(['日付', 'R', '馬場', '距離(m)', '頭数', '1着人気', '2着人気', '3着人気', '1着ゾーン', '2着ゾーン', '3着ゾーン', '集計対象', '備考'])
z = lambda p: '人気' if p and p <= 3 else '中穴' if p and p <= 6 else '大穴' if p and p <= 9 else '超大穴' if p and p <= 12 else '対象外'
for r in rows: ws2.append([serial(r['date']), r['r'], r['baba'], r['dist'], r['n'], r.get('p1'), r.get('p2'), r.get('p3'), z(r.get('p1')), z(r.get('p2')), z(r.get('p3')), r.get('cnt', 1), ''])
wb.save('xt/raw_baba_filter.xlsx')
print('ok', len(rows), 'rows', len(days), 'days')
