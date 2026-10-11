# マザーデータ2・3つ目のテスト用データ：JRA風（年をまたぐ・同じ日に同じRが何場も・18頭まで）と船橋風（貼り付け用）
import datetime, json, os, random, openpyxl
random.seed(7)
os.makedirs('xt', exist_ok=True)
def race(date, r, n):
    tan1 = round(random.uniform(1.2, 4.5), 1)
    s1 = round(tan1 * random.uniform(4, 30), 1)
    ranks = random.sample(range(1, n + 1), 3)
    if random.random() < .5: ranks[0] = random.randint(1, 3)
    if len(set(ranks)) < 3: ranks = random.sample(range(1, n + 1), 3)
    return [date, r, random.choice(['良', '良', '良', '稍重', '重', '不良']), random.choice([1200, 1400, 1600, 1800, 2000, 2400]), n, tan1, s1, ranks[0], ranks[1], ranks[2], None, None, random.choice([None, random.randint(300, 9000)]), None, None, 1]
wb = openpyxl.Workbook(); ws = wb.active; ws.title = 'JRAデータ'
ws.append(['日付', 'R', '馬場', '距離', '頭数', '単勝1位', '3連単1位', '1着人気', '2着人気', '3着人気', '3連単5位', '3連単10位', '馬単払戻', '3連単払戻', '備考', '集計対象'])
jra = []
d0 = datetime.datetime(2025, 12, 27)
for k in range(8):                       # 8開催日 × 2場 × 12R ＝ 192走（同じ日・同じRが2つずつ）
    d = d0 + datetime.timedelta(days=7 * k)
    for venue in ['東京', '京都']:
        for r in range(1, 13):
            row = race(d, r, random.randint(10, 18)); row[14] = venue
            ws.append(row); jra.append(row)
for c in ws['A'][1:]: c.number_format = 'yyyy/m/d'
wb.save('xt/jra_test.xlsx')
fun = []
for k in range(5):                       # 5日 × 12R ＝ 60走
    d = datetime.date(2026, 9, 1) + datetime.timedelta(days=k)
    for r in range(1, 13):
        row = race(d, r, random.randint(8, 14)); row[0] = d.strftime('%Y/%m/%d'); fun.append(row)
open('xt/funabashi_test.tsv', 'w', encoding='utf8').write('\n'.join('\t'.join('' if v is None else str(v) for v in row) for row in fun))
print('JRA', len(jra), 'rows; 船橋', len(fun), 'rows')
print('JRA first:', jra[0][:10]); print('JRA unique (date,R) pairs:', len({(r[0], r[1]) for r in jra}))
