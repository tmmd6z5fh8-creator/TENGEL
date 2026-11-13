# たてがみの さいごの ふさの 色の 直し（第4.168版・まさちゃん 2026/11/14 01:26「二枚目の赤丸の立髪の一部が色がおかしい！直して！」＝ぶちの 馬〈2段目の 大きさ〉の たてがみの 根もとが 白い）
#   python3 test_mane_fix.py   （ios/tc_assets/ が ある とき だけ 絵の 確かめ。ない とき（CI）は コードの 確かめ だけ）
#   ・コード：アプリ（tc/tc_app.js）は 2段目の 大きさ だけ 直した 絵を 指す 名前（tc_horse_bk_<色>_s2v2）を 読む・ない ときは 前の 名前／
#     前の 絵と 前の 名前は アプリにも 軽い 版にも 入れない（assets_dir.superseded：2つ そろって いる 色 だけ）／道具（kisekae/tc/mane_fix.py）は 上書きしない
#   ・もとの 絵（マスター）：前の 11こ（色の 絵 5・名前 5・形 1）は 消して いない・1バイトも かわって いない／新しい 名前（.json）は 絵の 名前 だけ ちがう
#   ・絵：道具で 作り直した 絵と 新しい 絵は 1点も ちがわない／かわった 点は ぜんぶ さいごの ふさの 面の 中（ほかの 所は 1点も かわって いない）／
#     かわった 所の 色は その 色の 馬の たてがみの 色（ぶち：白っぽい → こい 茶）
#   ・軽い 版（アプリに 入る もの）：新しい 絵と 名前 だけ（前の ものは ない）
#   ・絵（まさちゃんの もとの 3D から 作った もの）は リポジトリに 入って いない
import hashlib, json, os, re, subprocess, sys
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
sys.path.insert(0, W); sys.path.insert(0, os.path.join(W, 'kisekae', 'tc')); sys.path.insert(0, os.path.join(W, 'kisekae'))
import assets_dir
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label)
    if not c:
        fails.append(label)


COLORS = ('brown', 'black', 'white', 'hada', 'madara')
OLD = {'tc_c_brown_s2.webp': '480e13ae2f6a2e7409220c92f4c1560b', 'tc_c_black_s2.webp': 'f83ce152a2ca019da60dc5de33f3ec4b', 'tc_c_white_s2.webp': 'f8bf96251a3481d5e44f0bbdaf9e5b84',
       'tc_c_hada_s2.webp': '8fd6e6549fbec5c3a791ecf9ec7e9d59', 'tc_c_madara_s2.webp': '7e2ca1db22d63bec22856d7a9af76663',
       'tc_horse_bk_brown_s2.json': '0f0649a3c0b720876d07015362087719', 'tc_horse_bk_black_s2.json': '18a5258c3b5d80d55b3bc3abbcf9349d', 'tc_horse_bk_white_s2.json': 'fd769b8c5ef4d3c2dbc5534daa76dc10',
       'tc_horse_bk_hada_s2.json': 'ae80523353827d3163754accd0011955', 'tc_horse_bk_madara_s2.json': '6868fb9b771fc3e0779dda38108a8b3f', 'tc_horse_bk_brown_s2.bin': '02763d016cf5cca811a694ab4198eb4c'}      # 前の もの（第4.167版まで）の md5
NEW = [f'tc_c_{c}_s2v2.webp' for c in COLORS] + [f'tc_horse_bk_{c}_s2v2.json' for c in COLORS]
GONE = [f'tc_c_{c}_s2.webp' for c in COLORS] + [f'tc_horse_bk_{c}_s2.json' for c in COLORS]            # アプリに 入れない もの（形 .bin と 法線の 絵は 今までの ものを 使う）
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()

print('■ コード')
app = open(os.path.join(W, 'tc', 'tc_app.js'), encoding='utf8').read(); tool = open(os.path.join(W, 'kisekae', 'tc', 'mane_fix.py'), encoding='utf8').read()
spec = re.search(r"function horseSpec\(\) \{.*?\n  \}", app, re.S).group(0)
check("const HFIX = { 2: 'v2' };" in app and "name: `tc_horse_bk_${c}_s${s}${HFIX[s] || ''}`" in spec and "old: HFIX[s] ? `tc_horse_bk_${c}_s${s}` : null" in spec
      and "const getMeta = n => fetch(AP(n + '.json')).then(r => { if (!r.ok) throw new Error('horse ' + r.status); return r.json(); });" in app
      and "const meta = await getMeta(sp.name).catch(e => { if (!sp.old) throw e; return getMeta(sp.old); });" in app,
      'アプリ：2段目の 大きさ（s2）だけ tc_horse_bk_<色>_s2v2.json を 読む（ほかの 大きさは 今までの 名前）・新しい 名前が ない ときは 前の 名前を 読む（馬が 出ない ことは ない）')
fa = set(GONE) | set(NEW) | {'tc_horse_bk_brown_s2.bin', 'tc_n_brown_s2.webp', 'tc_c_brown_s1.webp', 'tc_horse_bk_brown_s1.json', 'tc_c_madara_s3.webp', 'tc_horse_bk_madara_s3.json'}
s1 = assets_dir.superseded('tc_assets', fa)
s2 = assets_dir.superseded('tc_assets', fa - {'tc_c_madara_s2v2.webp'}); s3 = assets_dir.superseded('tc_assets', fa - {'tc_horse_bk_white_s2v2.json'}); s4 = assets_dir.superseded('tc_assets', fa - set(NEW))
check(s1 == set(GONE) and s2 == set(GONE) - {'tc_c_madara_s2.webp', 'tc_horse_bk_madara_s2.json'} and s3 == set(GONE) - {'tc_c_white_s2.webp', 'tc_horse_bk_white_s2.json'} and s4 == set()
      and assets_dir.superseded('fig_assets', fa) == set(),
      '前の 絵と 前の 名前（色ごとに 2つ・ぜんぶで 10こ）は アプリにも 軽い 版にも 入れない（新しい 絵と 名前が 2つ そろって いる 色 だけ。そろって いなければ 前の ものは 外さない）・形 .bin／法線の 絵／ほかの 大きさは 外さない')
check("STAGE = 2" in tool and "COLORS = ('brown', 'black', 'white', 'hada', 'madara')" in tool and "SUF = 'v2'" in tool and 'BOX = ((0.05, 1.615, -0.21), (0.34, 1.85, 0.10))' in tool
      and 'WANT = dict(islands=112, tris=679)' in tool and 'T0, R0, RH, GROW, PAD = 0.15, 48.0, 70.0, 1, 3' in tool and "with open(p, 'xb') as fh:" in tool and "'wb'" not in tool
      and "lossless=True" in tool and "assert got == WANT" in tool and "'ふさの 面の そとが かわった'" in tool and 'kisekae/lite_assets.py' in tool,
      '道具（kisekae/tc/mane_fix.py）：2段目の 大きさ・5色・さいごの ふさの 箱と 数（島 112・三角 679：形が かわったら 止まる）・ふさの 面の そとが かわったら 止まる・にごらない 形で 書く・もう ある ファイルは 上書きしない（xb）')
tracked = subprocess.run(['git', 'ls-files', 'ios/tc_assets', 'ios/lite'], cwd=W, capture_output=True, text=True).stdout.split()
check(not tracked, '絵・形（ios/tc_assets・ios/lite）は リポジトリに 入って いない')

M = assets_dir.master('tc_assets')
if not all(os.path.isfile(os.path.join(M, f)) for f in list(OLD) + NEW):
    print('（絵の 確かめは 飛ばす：ios/tc_assets/ に 2段目の 大きさの 馬の 絵が ない）')
else:
    import numpy as np
    from PIL import Image
    import mane_fix as MF
    print('■ もとの 絵（マスター）')
    check(all(md5(os.path.join(M, f)) == h for f, h in OLD.items()), '前の 11こ（色の 絵 5・名前 5・形 1）は 消して いない・1バイトも かわって いない')
    ok = True
    for c in COLORS:
        a = json.load(open(os.path.join(M, f'tc_horse_bk_{c}_s2.json'), encoding='utf8')); b = json.load(open(os.path.join(M, f'tc_horse_bk_{c}_s2v2.json'), encoding='utf8'))
        a2 = dict(a); a2['tex'] = f'tc_c_{c}_s2v2.webp'; a2['bin'] = a.get('bin') or f'tc_horse_bk_{c}_s2.bin'
        ok = ok and b == a2 and b['bin'] == 'tc_horse_bk_brown_s2.bin' and b['ntex'] == a['ntex'] and a['tex'] == f'tc_c_{c}_s2.webp'
    check(ok, '新しい 名前（tc_horse_bk_<色>_s2v2.json）は 絵の 名前 だけ ちがう（形は 5色とも 同じ tc_horse_bk_brown_s2.bin・法線の 絵・骨・ならびは 前と 同じ）')

    print('■ 絵')
    P = MF.plan(M); info = P['info']
    check(info['islands'] == 112 and info['tris'] == 679 and 20000 < info['body'] < info['texels'] < 30000 and int(P['mask'].sum()) < 2048 * 2048 * 0.013,
          f'さいごの ふさ：絵の 島 {info["islands"]}こ・三角 {info["tris"]}まい・絵の 上で {info["texels"]:,}点（うち 体の 色で ぬられて いた {info["body"]:,}点）＝絵 ぜんぶの {int(P["mask"].sum()) / 2048 / 2048 * 100:.1f}% だけ')
    same = True; inside = True; tone = True; rep = []
    for c in COLORS:
        old = np.asarray(Image.open(os.path.join(M, f'tc_c_{c}_s2.webp')).convert('RGB')); new = np.asarray(Image.open(os.path.join(M, f'tc_c_{c}_s2v2.webp')).convert('RGB'))
        made, mane = MF.fix_tex(old.astype(np.float64), P)
        same = same and made.shape == new.shape == (2048, 2048, 3) and bool((made == new).all())
        d = np.abs(old.astype(int) - new.astype(int)).max(2); ch = d > 0; big = d > 24
        inside = inside and int(ch.sum()) > 20000 and not (ch & ~P['mask']).any()
        after = new[big].astype(float).mean(0); before = old[big].astype(float).mean(0)
        tone = tone and int(big.sum()) > 4000 and float(np.abs(after - mane).max()) < 6 and float(np.abs(before - mane).max()) > 24
        rep.append(f'{c} {int(ch.sum()):,}点')
    check(same, '道具で 作り直した 絵と 新しい 絵（tc_c_<色>_s2v2.webp）は 5色とも 1点も ちがわない（にごらない 形）')
    check(inside, 'かわった 点は ぜんぶ さいごの ふさの 面の 中（ほかの 所は 1点も かわって いない）：' + '・'.join(rep))
    md_o = np.asarray(Image.open(os.path.join(M, 'tc_c_madara_s2.webp')).convert('RGB')).astype(int); md_n = np.asarray(Image.open(os.path.join(M, 'tc_c_madara_s2v2.webp')).convert('RGB')).astype(int)
    bigm = np.abs(md_o - md_n).max(2) > 24; vo, vn = float(md_o[bigm].max(1).mean()), float(md_n[bigm].max(1).mean())
    check(tone and vo > 150 and vn < 90, f'かわった 所の 色は その 色の 馬の たてがみの 色（ぶち：明るさ {vo:.0f} の 白・オレンジ → {vn:.0f} の こい 茶）')

    print('■ 軽い 版（アプリに 入る もの）')
    L = assets_dir.lite('tc_assets')
    if not os.path.isdir(L):
        print('（飛ばす：ios/lite/tc_assets が ない）')
    else:
        lf = set(os.listdir(L))
        ok = all(f in lf for f in NEW) and not any(f in lf for f in GONE) and 'tc_horse_bk_brown_s2.bin' in lf and 'tc_n_brown_s2.webp' in lf and not assets_dir.stale('tc_assets')
        ok = ok and all(open(os.path.join(L, f), 'rb').read() == open(os.path.join(M, f), 'rb').read() for f in NEW if f.endswith('.json'))
        ok = ok and all(Image.open(os.path.join(L, f)).size == (2048, 2048) for f in NEW if f.endswith('.webp'))
        check(ok, '新しい 絵と 名前（10こ）だけ（前の 10こは ない）・名前は もとと 同じ 中身・絵は 2048×2048 の まま・形と 法線の 絵は 今までの もの')

print('✅ ぜんぶ OK' if not fails else f'❌ {len(fails)}こ 失敗')
sys.exit(1 if fails else 0)
