# 第4.236版の テスト（まさちゃん 2026/11/28 10:28「赤丸のルーレットの確率あと50ずつ増やして当たりにくくできる？ その下のチケット扉と特化ゾーンは70ずつ増やして！」
#   ・画像：トレーニングセンターの 説明書の 表（ルーレット 1/225・1/345・1/499 に 赤丸／その 下は チケット 1/700・ポイント特化ゾーン 1/799・激馬熱馬 1/299999））
#   ① 抽選の 表（tc/tc_app.js の PRIZES・ZONE）：ルーレット 1/275・1/395・1/549（＋50）・チケット 1/770（＋70）・ポイント特化ゾーン 1/869（＋70：幻の馬・神様馬の 表も 同じ ZONE.d）
#      ほか（ポイントの 当たり 6つ・激馬熱馬・幻の馬／神様馬が いる 間の ルーレット・幻の馬／神様馬が 来る 確率）は そのまま
#   ② 説明書（tc/tc_guide.js）：同じ 数（RTD・TKD・ZONE）・テスト版の 道具（tc/tc_test.js）の 字も 1/869
#   ③ 合わせた 数：何か 当たる 約16.6% → 約16.4%・平均 約50.8P → 約46.2P・高確ゾーン（×4）でも 1 を こえない（約65.7%）
#   くわしい たしかめ（ブラウザで 説明書の 表・2万回 ひく）は test_tc.py・test_tc_zone.py・test_tc_drop.py
#   python3 test_v236.py
import os, re, sys
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label, flush=True)
    if not c:
        fails.append(label)


app = open('tc/tc_app.js', encoding='utf8').read(); gd = open('tc/tc_guide.js', encoding='utf8').read(); tt = open('tc/tc_test.js', encoding='utf8').read()
nocom = lambda s: re.sub(r'(?m)^\s*//.*$', '', s)
a, g = nocom(app), nocom(gd)
pz = re.search(r'const PRIZES = \[(.*?\])\];', a, re.S).group(1)
tab = re.findall(r"\[1 / ([A-Za-z.0-9]+), \{ k: '(\w+)'(?:, (?:v: (\d+)|tier: '(\w+)'))? \}\]", pz)
zone = int(re.search(r'const ZONE = \{ d: (\d+),', a).group(1)); geki = int(re.search(r'const GEKI = \{ d: (\d+),', a).group(1))
num = lambda x: zone if x == 'ZONE.d' else geki if x == 'GEKI.d' else int(x)
rows = [(num(d), k, int(v) if v else tier) for d, k, v, tier in tab]
want = [(299999, 'gk', ''), (869, 'zn', ''), (770, 'tk', ''), (549, 'rt', 'kamisama'), (395, 'rt', 'maboroshi'), (275, 'rt', 'normal'),
        (121, 'pt', 300), (99, 'pt', 200), (95, 'pt', 100), (55, 'pt', 50), (25, 'pt', 20), (15, 'pt', 10)]
check(rows == want and zone == 869, f'① 抽選の 表：ルーレット 1/275・1/395・1/549（前 1/225・1/345・1/499 ＋50）・チケット 1/770（前 1/700 ＋70）・ポイント特化ゾーン 1/869（前 1/799 ＋70）・'
      f'ポイントの 当たり 6つと 激馬熱馬は そのまま（{[r[0] for r in rows]}）')
vis = re.search(r'const PRIZES_VISIT = \{(.*?)\n  \};', a, re.S).group(1)
check(vis.count('[1 / ZONE.d, { k: \'zn\' }]') == 2 and '[1 / 60, ' in vis and '[1 / 30, ' in vis and '[1 / 15, ' in vis and '[1 / 32, ' in vis and '[1 / 16, ' in vis and '[1 / 8, ' in vis
      and re.search(r'P_MAB = 1 / 245\b', a) and re.search(r'P_KAMI = 1 / 399\b', a),
      '① 幻の馬・神様馬が いる 間の 表：ポイント特化ゾーンは 同じ 1/869（ZONE.d）・ルーレット（1/15・1/30・1/60／1/8・1/16・1/32）と 幻の馬・神様馬が 来る 確率（1/245・1/399）は そのまま')
check('const RTD = [275, 395, 549], TKD = 770;' in g and 'const ZONE = { d: 869, start: 1000, add: 2000, rate: 0.6, max: 12 };' in g and 'const GEKI = { d: 299999, v: 40000 };' in g
      and '本番は PUSH 1回ごとに 1/869 で 入るよ。' in tt and '1/799' not in nocom(tt),
      '② 説明書（tc_guide.js）の 表も 同じ 数（ルーレット 1/275・1/395・1/549・チケット 1/770・ポイント特化ゾーン 1/869）・テスト版の 道具の 字も 1/869')
ps = [1 / d for d, _, _ in rows]; tot = sum(ps)
E_zone = sum((1000 + 2000 * n) * (0.6 ** n * 0.4 if n < 12 else 0.6 ** 12) for n in range(13))
tk = 7000 * (3 / 8 + 2 / 3 + 1 * (1 - 1 / 8 - 1 / 3))
val = {'gk': 40000, 'zn': E_zone, 'tk': tk, 'kamisama': 4800, 'maboroshi': 2400, 'normal': 1200}
avg = sum((val[k] if k in ('gk', 'zn', 'tk') else val[v] if k == 'rt' else v) / d for d, k, v in rows)
check(round(tot * 100, 1) == 16.4 and round(avg, 1) == 46.2 and tot * 4 < 1 and round(tot * 400, 1) == 65.7,
      f'③ 何か 当たる 約{tot * 100:.1f}%（前 約16.6%）・平均 約{avg:.1f}P（前 約50.8P）・高確ゾーン（×4）でも 約{tot * 400:.1f}%（1 を こえない）')
print('合計', len(fails), 'NG' if fails else 'OK')
sys.exit(1 if fails else 0)
