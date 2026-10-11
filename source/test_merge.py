# merge_raw.py（分析シート×分析表 → hist.json に新しいレースを足す）のテスト。ブラウザは使わない
#  1) ふつうの新しい日は入る  2) 分析シートがほかの日の写しになっている日は入れない（重複転記の疑い）
#  3) 同じ中身のレースがもうあるものは入れない  4) dropped.json のレースは入れない  5) もとのレースは書き換えない
import datetime, json, os, shutil, subprocess, sys, tempfile
import openpyxl
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
sys.path.insert(0, W); import merge_raw as M
subprocess.run(['python3', 'mkrawfiles.py'], check=True, stdout=subprocess.DEVNULL)   # hist_280.json と同じ中身の分析シート・分析表
tmp = tempfile.mkdtemp()
base = json.load(open('hist_280.json', encoding='utf8')); by = {(r['date'], r['r']): r for r in base}
sheet = openpyxl.load_workbook('xt/raw_bunseki_sheet.xlsx'); hyo = openpyxl.load_workbook('xt/raw_bunseki_hyo.xlsx')
ss, hs = sheet.active, hyo.active
res = lambda ps: '-'.join(f'{x}位' for x in ps if x)
def add_day(date, races):   # races: [(R, 馬場, 距離, 頭数, 単勝1位, 3連単1位, [着順])]
    line = [datetime.datetime.fromisoformat(date)] + [None] * 48
    for R, baba, dist, n, t1, s1, ps in races:
        ss.append([datetime.datetime.fromisoformat(date), R, baba, dist, n, res(ps)])
        i = 1 + (R - 1) * 4; line[i:i + 3] = [t1, s1, res(ps)]
    hs.append(line)
src = [by[('2026-10-07', R)] for R in (1, 2, 3)]
add_day('2026-10-20', [(r['r'], r['baba'], r['dist'], r['n'], r['tan1'] + 0.3, r['s1'] + 5, [r['p1'], r['p2'], r['p3']]) for r in src])   # 10/7の写し（オッズだけちがう）
add_day('2026-10-21', [(1, '良', 1400, 12, 2.4, 33.3, [2, 5, 1]), (2, '稍重', 1600, 9, 1.6, 12.2, [1, 3, 2])])                               # ふつうの日
r5 = by[('2026-10-07', 5)]
add_day('2026-10-22', [(1, r5['baba'], r5['dist'], r5['n'], r5['tan1'], r5['s1'], [r5['p1'], r5['p2'], r5['p3']]), (2, '良', 1200, 11, 3.1, 45.6, [4, 1, 7])])   # 1Rは10/7 5Rと同じ中身
a, b = os.path.join(tmp, 'sheet.xlsx'), os.path.join(tmp, 'hyo.xlsx'); sheet.save(a); hyo.save(b)
shutil.copy('hist_280.json', os.path.join(tmp, 'hist.json'))
fails = []
def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label)
    if not c: fails.append(label)
rep, new = M.main(a, b, os.path.join(tmp, 'hist.json'), os.path.join(tmp, 'out.json'))
got = {(r['date'], r['r']) for r in new}; sk = {k: w for k, w in rep['skipped']}
print('new:', sorted(got)); print('skipped(10月):', {k: w for k, w in sk.items() if k[0] >= '2026-10'})
check(got == {('2026-10-21', 1), ('2026-10-21', 2), ('2026-10-22', 2)}, 'ふつうのレースだけ入る')
check(all('重複転記の疑い' in sk.get(('2026-10-20', R), '') for R in (1, 2, 3)), '10/7の写しの日（10/20）は入れない')
check('同じ中身のレースがもうある' in sk.get(('2026-10-22', 1), ''), '同じ中身のレース（10/22 1R）は入れない')
check(rep['diffs'] == [], 'もとのデータとのちがいなし')
out = json.load(open(os.path.join(tmp, 'out.json'), encoding='utf8')); om = {r['id']: r for r in out}
check(all(om[r['id']] == r for r in base), 'もとのレースは書き換えない')
check(rep['summary'] == '10/21（1〜2R）・10/22（2R）の3走', '説明：' + rep['summary'])
# dropped.json にあるレースは入れない
json.dump([{'date': '2026-10-21', 'rs': [2], 'why': 'テスト', 'at': '2026-10-21'}], open(os.path.join(tmp, 'dropped.json'), 'w', encoding='utf8'), ensure_ascii=False)
rep2, new2 = M.main(a, b, os.path.join(tmp, 'hist.json'))
check({(r['date'], r['r']) for r in new2} == {('2026-10-21', 1), ('2026-10-22', 2)} and dict(rep2['skipped']).get(('2026-10-21', 2)) == '重複で消したレース', 'dropped.json のレースは入れない')
shutil.rmtree(tmp)
print('\nFAILS:', fails); sys.exit(1 if fails else 0)
