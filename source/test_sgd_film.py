# 超神様的中の 新しい 動画と、なくした 2つの 演出（第4.162版・まさちゃん 2026/11/12 22:32「超神様的中と超プレミアム神様的中の一枚目の球体のシーン消して！
#   いきなり2枚目の爆破のシーンに入るようにして！あと、鳥居とか文字関係はこのファイルのデータを使って！」・22:34「画質は綺麗にデータが重くなりすぎないようによろしく！」・
#   22:50「これ送れてなかった！万馬券」・22:56「プレミアムど的中／超プレミアム神様的中／この二つ消して！」）
#   python3 test_sgd_film.py   （ios/fx_assets/ が ある とき だけ ファイルの 確かめ。ない とき（CI）は コードの 確かめ だけ）
#   ・動画の 道具：① は 金の 爆発 だけ（前の 48コマの さいごの 6コマ）・① 6 ＋ 白い 光 40 ＋ ② 141 ＋ ③ 198 ＝ 385コマ（12.83秒）・音は 金の 爆発から・
#     まさちゃんの 3D（6つ）が ない ときは 前の 字と 鳥居で 描ける
#   ・アプリ：プレミアムど的中（pc）・超プレミアム神様的中（spg）は 出ない（G は いつも 超神様的中・D で M で ない ものは いつも ノーマルど的中・くじは ない）・
#     押したあと／CSS／絵／音／昇格の 動画は 束に ない・決めて 出す とき（force）は ノーマルど的中／超神様的中に なる・前の 記録の 思い出ボードは そのまま
#   ・もとの ファイル（マスター）：前の 動画・さいごの 1まい・音・なくした 演出の 絵と 音と 動画は 消して いない・1バイトも かわって いない（新しい ものは 別の 名前）
#   ・新しい 動画：1170×2532・30コマ/秒・385コマ・音なし・はじめの コマから 金の 爆発（黒や 球体で ない）・0.17秒で まっ白・さいごの コマは さいごの 1まいと 同じ 絵
#   ・軽い 版（アプリに 入る もの）：新しい 3つ だけ（前の 3つと なくした 演出の ものは ない）・動画は CRF 24（さいごの 30コマは 少しずつ きれいに）
#   ・3D（まさちゃんの Meshy の GLB）と コマは リポジトリに 入って いない
import hashlib, json, os, re, shutil, subprocess, sys, tempfile
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
K = os.path.join(W, 'kisekae'); FLAT = os.path.join(K, 'flat')
sys.path.insert(0, W); sys.path.insert(0, K); sys.path.insert(0, FLAT)
import assets_dir
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label)
    if not c:
        fails.append(label)


md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
rd = lambda *p: open(os.path.join(W, *p), encoding='utf8').read()
# 前の ファイル（第4.161版まで）の md5：もとの フォルダ（ios/fx_assets）に のこす（消さない・上書きしない）
OLD = {'sgd_film.mp4': 'c7f305f92b5eb79f0cbfe8bc0aae85a0', 'sgd_last.webp': '81ce3e44481e1292fe0181c556ddfebf', 'sfx_sgd.m4a': '86f8079931f4fe00b2332a5c475f0b39',
       'spg_up.mp4': 'dc5d953f1eda66d299bbed9230033a20', 'sfx_pc.m4a': 'd15654e1d515bb1955bc73eed10bd6b3', 'sfx_zp.m4a': 'b54f9dfaa976c29ddd86ddaf58c3b6d7',
       'sfx_spg.m4a': '9428185d82e2f96b805b117bd17568b7', 'sfx_spg_up.m4a': '14cb8c0b5b0ee6117a7d43f05fa9ca9d'}
OLD_PM = (43, 'e030805b1da1f8d5363f73f048f15ac7')      # プレミアムど的中の 絵 43まい（名前の 順に つないだ もの）
NEW = ['sgd_film2.mp4', 'sgd_last2.webp', 'sfx_sgd2.m4a']

print('■ 動画の 道具')
import kami_super as SG
import kami_film as F1
check(F1.N0 == 48 and F1.CUT == 42 and F1.N == 6 and F1.T['GOLD'] == (1.333, 1.4, 1.467, 1.567) and abs(F1.CUT / F1.FPS - F1.T['GOLD'][1]) < 1e-9 and 'fi = fi + CUT' in rd('kisekae', 'flat', 'kami_film.py'),
      f'① は 金の 爆発 だけ：前の 48コマの はじめの 42コマ（1.4秒＝球体の 場面）を なくして 6コマ（0.2秒）・はじまりは 金の 爆発の 時（T の GOLD の 2つ目）（CUT {F1.CUT}・N {F1.N}）')
check((SG.N1, SG.NW, SG.N2, SG.N3) == (6, 40, 141, 198) and round(SG.FILM * SG.FPS) == 385 and abs(SG.FILM - 385 / 30) < 1e-9 and abs(SG.RES - (385 / 30 + .1)) < 1e-9
      and [round(v, 4) for v in SG.OFS] == [0.0, round(46 / 30, 4), round(187 / 30, 4)] and '光の 玉が はじけ' not in SG.SGD_SR and '金色の 爆発から' in SG.SGD_SR,
      f'動画の 長さ：① 6 ＋ 白い 光 40 ＋ ② 141 ＋ ③ 198 ＝ 385コマ＝{SG.FILM:.2f}秒（前は 427コマ・14.23秒）・ボードは {SG.RES:.2f}秒・② は {SG.OFS[1]:.2f}秒から・③ は {SG.OFS[2]:.2f}秒から・読み上げの 文も 金の 爆発から')
sfx_src = rd('kisekae', 'gen_sfx.py'); mix = sfx_src.split('def sgd_mix(')[1].split('\ndef ')[0]
i_cut, i_if, i_ign, i_gold = (mix.index(x) for x in ("cut = ev.get('CUT', 0.0)", '    if not cut:\n', "ig0, igw, igf, igr, ige = (o1 + v for v in T1['IGN'])", '    mx.add(explosion(r, 1.0, 1.0), gx, .7, rv=.3)'))
check(i_cut < i_if < i_ign < i_gold and 'o1 -= cut' in mix and mix[i_if:i_gold].count('\n    mx.add(') == 0 and mix[i_if:i_gold].count('\n        mx.add(') > 20
      and "CUT=F1.CUT / FPS" in rd('kisekae', 'kami_super.py'),
      '音（gen_sfx.py の sgd_mix）：① の はじめを 切った 動画は 金の 爆発（ドガーン!!）から 鳴らす（点火・光の 滝・ドーム・雷・岩の 音は 切った 所なので 鳴らさない）・切った 秒は 絵の スクリプトから 読む')
bf = rd('kisekae', 'build_fx_films.py'); mp = rd('kisekae', 'fx_mp4.py')
check("== 385 == round(SG.FILM * SG.FPS)" in bf and "film, last = BF.FILMS['sgd_film'], BF.STILL['sgd_last']" in bf and "encode(comb, len(seq), film, SGD_CRF)" in bf and "SGD_CRF = '20'" in bf
      and 'if os.path.exists(os.path.join(out, name)) and not FORCE:' in bf and "'sgd_film.mp4'" not in bf.split('"""', 2)[2]
      and "FILM = os.path.join(FX, BF.FILMS['sgd_film'])" in mp and "FX = assets_dir.adir('fx_assets')" in mp and 'NF = int(round(K.FILM * FPS))' in mp and 'B_FROM = math.floor((K.RES - .15) * 10) / 10' in mp and 'sgd_film.mp4' not in mp.split('import math')[1],
      '動画を 作る 道具（build_fx_films.py）：385コマ・新しい 名前で 書き出す（もう ある 動画は 上書きしない）・もとは CRF 20／見本の MP4 の 道具（fx_mp4.py）も 新しい 動画と 音を 使う')
import kami_glb as KG
check(sorted(KG.FILES) == ['gate', 'logo', 'manba', 'omede', 'phrase', 'tengan'] and all(v.endswith('.glb') for v in KG.FILES.values())
      and "def draw(obj, R, Tv, W, H, focal, env" in rd('kisekae', 'flat', 'kami_glb.py') and 'for i in range(0, n, CHUNK):' in rd('kisekae', 'flat', 'kami_glb.py'),
      'まさちゃんの 3D を 描く 道具（kisekae/flat/kami_glb.py）：6つ（万馬券・天眼・4行の 文・神様的中・おめでとう御座います・鳥居）・見える 点は 分けて 色に する（メモリを おさえる）')
r = subprocess.run([sys.executable, '-c', 'import sys; sys.path[:0] = [%r, %r]\nimport kami_glb as G, kami_film2 as A, kami_film3 as B\nprint(G.have(), A.GLB, B.GLB, A.N, B.N)' % (FLAT, K)],
                   capture_output=True, text=True, env=dict(os.environ, SGD_GLB_DIR='/nonexistent'), timeout=300)
check(r.returncode == 0 and r.stdout.strip().split('\n')[-1] == 'False False False 141 198', f'3D が ない とき（リポジトリ だけの 所）：② と ③ は 前の 字と 鳥居で 描ける 形の まま（{(r.stdout.strip() or r.stderr.strip())[-80:]}）')
# さいごの 字を 画面の 左右の まん中に（まさちゃん 2026/11/13 00:16「超神様的中の最後のシーン、青四角の位置が少し右よりだから中央に合わせて！」）・
# ま正面に（01:10「神様的中の文字だけもう少し左が中央じゃない？まだ少し右に曲がってるように見える」）
f3 = rd('kisekae', 'flat', 'kami_film3.py'); lp = f3.split('def logo_pose(t):')[1].split('\ndef ')[0]
check('def logo_cx(yaw, pitch, roll, y, z):' in f3 and 'def logo_hull():' in f3 and "logo_obj()['prims'][:2]" in f3.split('def logo_hull():')[1].split('\ndef ')[0]
      and 'xb = logo_cx(ye, LOGO_END[1], 0.0, yf, zf) if GLB else 0.0' in lp and 'b = (ye, LOGO_END[1], 0.0, xb, yf, zf)' in lp
      and 'pose[3] = logo_cx(pose[0], pose[1], pose[2], pose[4], pose[5])' in lp,
      'さいごの 字（3D）は「神様／的中」の 見える かたまり（前の 面＋横の 面）の 左右の はしの まん中を 画面の まん中に 置く（回りきった あと ゆっくり 向きが かわる 間も 合わせ直す）')
check('GLB_END_YAW = 1.5' in f3 and 'LOGO_END = (5.0, -7.0)' in f3 and 'ye = GLB_END_YAW if GLB else LOGO_END[0]' in lp
      and 'pose[0] = GLB_END_YAW * max(0.0, 1 - s / ((N - 1) / FPS - t1))' in lp and 'if not GLB:\n        pose[0] += .9 * s' in lp,
      'さいごの 字（3D）は 回りおわり（右へ 1.5°）から ゆっくり ま正面へ もどり、さいごの コマで ちょうど 0°（右へ 曲がって 見えない）・前の 字（3D が ない とき）は 今までどおり（右へ 5° → ゆっくり 右へ）')
gg = f3.split('def glb_gate():')[1].split('\ndef ')[0]
check('yawf, pitchf, rollf, xf_, yf_, zf_ = logo_pose((N - 1) / FPS)' in gg and 'return [(pl[0] + pr[0]) / 2 - CXS]' in gg and 'ox = float(fsolve(resx, [float(ox)])[0])' in gg
      and gg.index('ox, oy, dsc = fsolve(res,') < gg.index('ox = float(fsolve(resx,') < gg.index('g = KG.bake(p, float(dsc), cx, cy, cz, float(ox), float(oy))'),
      '鳥居（3D）の 左右の 場所は さいごの コマ（字が ま正面）で 画面の まん中に 来る ように 決める（大きさと 高さは 今までどおり 回りおわりの 形で）')
if KG.have():
    code = ('import sys; sys.path[:0] = [%r, %r]\nimport numpy as np, kami_film3 as F\nfrom scipy.spatial import ConvexHull\nH = F.logo_hull(); out = []\n'
            'B = F.logo_obj()["prims"][2].pos.astype(np.float64); B = B[ConvexHull(B).vertices]\n'
            'for t in (3.0, 4.0, 5.0, 6.0, (F.N - 1) / F.FPS):\n'
            '    p = F.logo_pose(t); R = F.rot(p[0], p[1], p[2]); Q = H @ R.T; Qb = B @ R.T\n'
            '    px = F.FOCAL * (Q[:, 0] + p[3]) / (Q[:, 2] + p[5]) + F.CXS; pb = F.FOCAL * (Qb[:, 0] + p[3]) / (Qb[:, 2] + p[5]) + F.CXS\n'
            '    out.append((round(float(px.min() + px.max()) / 2 - F.W / 2, 2), round(float(p[0]), 3), round(float(px.min())), round(float(px.max())), round(float(pb.min() + pb.max()) / 2 - F.W / 2, 1)))\n'
            'g = F.glb_gate(); P = g["prims"][0].pos.astype(np.float64); lo, hi = P.min(0), P.max(0); gate = []\n'
            'for t in (3.0, (F.N - 1) / F.FPS):\n'
            '    p = F.logo_pose(t); R = F.rot(p[0], p[1], p[2]); Tv = np.array(p[3:])\n'
            '    e = [float(F.project(R @ np.array([x, lo[1], (lo[2] + hi[2]) / 2]) + Tv)[0]) for x in (lo[0], hi[0])]\n'
            '    gate.append([round(e[0], 1), round(e[1], 1)])\n'
            'print(repr((out, round(float(F.logo_pose(2.15)[3]), 1), gate)))') % (FLAT, K)
    r = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True, timeout=900)
    try:
        cen, x0, gate = eval(r.stdout.strip().split('\n')[-1])
    except Exception:
        cen, x0, gate = [], None, [[0, 0], [0, 0]]
    yaws = [c[1] for c in cen]
    check(r.returncode == 0 and len(cen) == 5 and all(abs(c[0]) < .5 for c in cen) and all(c[2] > 120 and c[3] < 1050 for c in cen) and x0 == 170.0,
          f'手元の 3D で：「神様／的中」の かたまりの まん中は 画面の まん中から {[c[0] for c in cen]}px・左右の はし {[(c[2], c[3]) for c in cen]}（画面 0〜1170）・'
          f'出て くる ときの はじめの 場所は 前と 同じ（{(r.stderr.strip() or "")[-120:]}）')
    gmid = [round((a_ + b_) / 2 - 585, 1) for a_, b_ in gate]
    check(len(cen) == 5 and yaws[0] == 1.5 and yaws == sorted(yaws, reverse=True) and yaws[-1] == 0.0 and all(abs(c[4]) < 8 for c in cen) and abs(cen[-1][4]) < 4
          and abs(gmid[1]) < .5 and abs(gmid[0]) < 15 and gate[1][0] > 0 and gate[1][1] < 1170,
          f'手元の 3D で：回りおわりの 向きは 右へ {yaws}°（さいごの コマで ま正面）・「おめでとう／御座います」の まん中は {[c[4] for c in cen]}px・'
          f'鳥居の 左右の はし（回りおわり・さいごの コマ）{gate}＝画面の まん中から {gmid}px（さいごの コマで まん中）')

print('■ アプリ（なくした 演出・新しい 動画の 名前）')
import build_fx as BF
check(BF.FILMS == {'sgd_film': 'sgd_film2.mp4', 'sd_film': 'sd_film3.mp4', 'nd_film': 'nd_film3.mp4', 'gk_film': 'gk_film.mp4'} and BF.STILL['sgd_last'] == 'sgd_last2.webp' and BF.SFX['sgd'] == 'sfx_sgd2.m4a'
      and sorted(BF.SFX) == ['big', 'big_push', 'fz_push', 'gk', 'hit', 'hit_push', 'nd', 'ndt', 'sd', 'sdp', 'sgd'] and sorted(BF.ART) == ['gk', 'nd', 'sd', 'sgd'] and len(BF.ASSET_FILES) == 24
      and all(f in BF.ASSET_FILES for f in NEW) and not [f for f in BF.ASSET_FILES if f in OLD or f.startswith('pm_')],
      f'アプリに 入れる ファイル（{len(BF.ASSET_FILES)}こ）：超神様は 新しい 動画・さいごの 1まい・音（{"・".join(NEW)}）・前の 3つと なくした 演出の 絵（pm_…）／音 4こ／昇格の 動画は 入れない')
B = BF.bundle()
css = B['css']
check(sorted(B['reveal']) == ['big', 'gk', 'hit', 'hit_t', 'miss', 'nd', 'sd', 'sgd'] and sorted(B['films']) == ['gk_film', 'nd_film', 'sd_film', 'sgd_film'] and 'PC' not in B['t']
      and B['t']['SG'] == {'FILM': 12.8333, 'RES': 12.9333, 'STILL_FROM': 12.8333, 'STILL_WAIT': 1.0, 'STILL_BOARD': 1.3, 'WAIT_MAX': 4.0}
      and not any(x in css for x in ('.ov.fz.pm', '.ov.fz.zp', ' .spu', '.zpdefs', 'pm_', 'fxpm', 'fxzp')) and '.fxs .ov.fz.sgd' in css and '.fxs .sgv' in css
      and 'sgd_last2.webp' in B['reveal']['sgd'] and 'sgd_last.webp' not in B['reveal']['sgd'] and B['board']['titles'].get('sgd') == '超神様的中！！！' and B['board']['titles'].get('fz') == 'ど的中！！！',
      f'演出の 束（window.__FX）：押したあとは 的中・デカ的中・ノーマルど的中・極ど的中・超神様的中・神様極的中・ハズレ だけ・プレミアム／超プレミアム／昇格の 動画の CSS は ない（CSS {len(css) / 1000:.0f}KB）・超神様の 時刻は 12.83秒・ボード 12.93秒')
fx = rd('fx.js'); code = '\n'.join(l for l in fx.split('\n') if not l.lstrip().startswith('//'))
tbl = lambda name: re.search(r'const %s = (\{.*?\});' % name, code, re.S).group(1)
check("const kind = tier === 'g' ? 'sgd' : tier === 'd' ? 'sd' : tier === 'b' ? 'big' : 'hit';" in code and 'lottery' not in code and 'LOT' not in re.findall(r'\b[A-Z]{3}\b', code)
      and "function shown(kind, quiet) { return kind === 'pc' || kind === 'nd' ? 'sd' : kind === 'spg' ? 'sgd' : !quiet && (kind === 'fz' || kind === 'gd') ? 'sd' : kind; }" in code
      and "else if (d.tier === 'g' && d.multi && +spec.godN >= 2) kind = 'gk';\n    open(kind, spec, d.supers, d.bigs, quiet, null, d.trig);" in code,
      'どれが 出るか（fx.js）：G（神様）は M でも 超神様的中・D は M で なくても いつも 極ど的中（第4.165版：ノーマルど的中は なし・くじも ない）・神様極的中の 条件は そのまま・決めて 出す とき（force・ためし）の pc・nd は sd・spg は sgd')
check(all(not re.search(r'\b(pc|spg)\b', tbl(n)) for n in ('SND', 'NEED', 'FZ_PUSH', 'PZ', 'RBW', 'PLABEL')) and not any(x in code for x in ('spgGo', 'spgUp', 'spgFilm', 'spzOv', 'spg_up', 'A.art.pm', 'A.t.PC', 'UP_AT')) and not re.search(r'\b(cur|c)\.(u|sp)\b', code)
      and "pc: 'fz'" in tbl('BOARD_OF') and "spg: 'fz'" in tbl('BOARD_OF') and "pc: 'fz'" in tbl('TITLE_OF') and "spg: 'sgd'" in tbl('TITLE_OF') and "pc: 'turf'" in tbl('MEM_FRAME') and "spg: 'toriicute'" in tbl('MEM_FRAME')
      and "if (kind === 'sgd' || kind === 'spg' || kind === 'gk') {" in code,
      'fx.js：プレミアムど的中・超プレミアム神様的中の 音／PUSH／動画の 流れは ない・前に 記録した 思い出ボード（種類 pc・spg）の ボードの 形・見出し・帯・わくは のこす（そのまま 開ける）')
pu = rd('points_ui.js'); src = rd('src.html'); man = rd('manual', 'content_app.html')
tfx = re.search(r'const TEST_FX = (\[\[.*?\]\]);', pu).group(1)
check(re.findall(r"\['(\w+)', '([^']+)'\]", tfx) == [('hit', '的中'), ('big', 'デカ的中'), ('sd', '極ど的中'), ('miss', 'ハズレ'), ('sgd', '超神様的中'), ('gk', '神様極的中')]
      and "pc: 'ど的中（プレミアム）'" in src and "spg: '超プレミアム神様的中'" in src and "const memNeedsChoice = b => memKindOf(b) === 'nd' || memKindOf(b) === 'pc';" in src
      and '長いものは15秒くらい' in man and '30秒くらい' not in man,
      'テスト版の 道具の ボタンは 6こ（ノーマルど的中・プレミアムど的中・超プレミアム神様的中は なし）・前の 記録の 札（ど的中・ど的中（プレミアム）・超プレミアム神様的中）は そのまま 読める・説明書の「長いものは」は 15秒くらい')
S = assets_dir.superseded
allf = set(OLD) | set(NEW) | {'pm_bg.webp', 'pm_fin_sh.webp', 'sd_film.mp4', 'sfx_sd.m4a', 'gk_last.webp', 'bcx_hb_eye.webp'}
check(S('fx_assets', allf) == set(OLD) | {'pm_bg.webp', 'pm_fin_sh.webp'} and S('fx_assets', allf - {'sfx_sgd2.m4a'}) == (set(OLD) - {'sgd_film.mp4', 'sgd_last.webp', 'sfx_sgd.m4a'}) | {'pm_bg.webp', 'pm_fin_sh.webp'}
      and S('fx_assets', {'sd_film.mp4', 'sfx_sd.m4a', 'sgd_film.mp4'}) == set(),
      'アプリに 入れない もの（assets_dir.superseded）：なくした 演出の 絵・音・昇格の 動画は いつも／前の 超神様の 動画・さいごの 1まい・音は 新しい 3つが そろって いる とき だけ（そろう までは 前の ものを 使う）')
st = rd('ios', 'ci', 'selftest.js'); rn = rd('ios', 'ci', 'run.sh')
check('fx-pc' not in st and 'fx-pc' not in rn and "force: 'pc'" not in st and 'F.lottery(' not in st and "for (var fk of ['pc', 'spg'])" in st and 'fx-fz-result fx-sgd-still fx-sd' in rn,
      'CI（シミュレーター）：プレミアムど的中の 写真と 確かめは なくした・決めて 出すと ノーマルど的中／超神様的中に なる ことを 見る')

M = assets_dir.master('fx_assets')
if os.path.isdir(M) and all(os.path.exists(os.path.join(M, f)) for f in OLD):
    print('■ もとの ファイル（マスター）')
    bad = [f for f, h in OLD.items() if md5(os.path.join(M, f)) != h]
    pm = sorted(f for f in os.listdir(M) if re.fullmatch(r'pm_.+\.webp', f)); h = hashlib.md5()
    for f in pm:
        h.update(open(os.path.join(M, f), 'rb').read())
    check(not bad and (len(pm), h.hexdigest()) == OLD_PM, f'前の 動画・さいごの 1まい・音／なくした 演出の 絵 {len(pm)}まい・音 4こ・昇格の 動画は もとの フォルダに ある・1バイトも かわって いない（{bad}）')
    if all(os.path.exists(os.path.join(M, f)) for f in NEW) and shutil.which('ffprobe') and shutil.which('ffmpeg'):
        import cv2, numpy as np

        def probe(p):
            j = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', p], capture_output=True, text=True, check=True).stdout)
            return j

        def frame(p, n, out):
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', p, '-vf', f'select=eq(n\\,{n})', '-vsync', '0', '-frames:v', '1', out], check=True)
            return cv2.imread(out)
        tmp = tempfile.mkdtemp()
        try:
            film = os.path.join(M, 'sgd_film2.mp4'); j = probe(film); v = [s for s in j['streams'] if s['codec_type'] == 'video'][0]
            head = open(film, 'rb').read(1 << 20)
            check(len(j['streams']) == 1 and (v['codec_name'], v['profile'], v['width'], v['height'], v['pix_fmt'], v['r_frame_rate'], v['nb_frames']) == ('h264', 'High', 1170, 2532, 'yuv420p', '30/1', '385')
                  and abs(float(v['duration']) - 385 / 30) < 1e-3 and 0 <= head.find(b'moov') < head.find(b'mdat'),
                  f'新しい 動画（もと）：1170×2532・30コマ/秒・385コマ（{float(v["duration"]):.2f}秒）・H.264・音なし・はじめから 読める 形（{os.path.getsize(film) / 1e6:.2f}MB）')
            f0, f2, f5, fl = (frame(film, n, os.path.join(tmp, f'f{n}.png')) for n in (0, 2, 5, 384))
            c0 = f0[900:1500, 300:870].astype(float).mean((0, 1))      # まん中（金の 爆発）：BGR
            still = cv2.imread(os.path.join(M, 'sgd_last2.webp'))
            mse = float(((fl.astype(float) - still.astype(float)) ** 2).mean()); psnr = 99.0 if mse == 0 else 10 * np.log10(255 ** 2 / mse)
            check(f0.mean() > 90 and c0[2] > 200 and c0[2] > c0[0] + 40 and f2.mean() > f0.mean() + 15 and f5.mean() > 240 and still.shape[:2] == (2532, 1170) and psnr > 34,
                  f'はじめの コマから 金の 爆発（黒や 球体の 場面で ない：明るさ {f0.mean():.0f}・まん中は 金色）→ 0.07秒 {f2.mean():.0f} → 0.17秒で まっ白（{f5.mean():.0f}）・さいごの コマは さいごの 1まい（sgd_last2.webp）と 同じ 絵（PSNR {psnr:.1f}dB）')
            snd = os.path.join(M, 'sfx_sgd2.m4a'); a = probe(snd); dur = float(a['format']['duration'])
            pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', snd, '-ac', '1', '-ar', '8000', '-f', 's16le', '-'], capture_output=True, check=True).stdout
            x = np.frombuffer(pcm, np.int16).astype(float) / 32768
            rms = lambda t0, t1: float(np.sqrt((x[int(t0 * 8000):int(t1 * 8000)] ** 2).mean() + 1e-12))
            check(abs(dur - (SG.T0B + 2.0)) < .15 and rms(0, .3) > .08 and rms(0, .3) > rms(SG.OFS[1] - .6, SG.OFS[1] - .3) * 1.5,
                  f'新しい 音：{dur:.2f}秒（ボードの 買い目の 2秒 あと まで）・はじめの 0.3秒から 爆発の 音（大きさ {rms(0, .3):.2f}：白い 光の 間 {rms(SG.OFS[1] - .6, SG.OFS[1] - .3):.2f} より 大きい）')
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        L = assets_dir.lite('fx_assets')
        if os.path.isdir(L):
            print('■ 軽い 版（アプリに 入る もの）')
            lf = set(os.listdir(L)); mf = assets_dir.manifest('fx_assets') or {'files': {}}
            lv = [s for s in probe(os.path.join(L, 'sgd_film2.mp4'))['streams'] if s['codec_type'] == 'video'][0] if 'sgd_film2.mp4' in lf else {}
            e = mf['files'].get('sgd_film2.mp4', {})
            check(all(f in lf for f in NEW) and not [f for f in lf if f in OLD or f.startswith('pm_')] and not assets_dir.stale('fx_assets') and all(f in lf for f in BF.ASSET_FILES)
                  and e.get('how') == 'film' and e.get('p') == 'crf24-slow-tail30:23/20:22/10:21' and (lv.get('nb_frames'), lv.get('width'), lv.get('height')) == ('385', 1170, 2532)
                  and md5(os.path.join(L, 'sgd_last2.webp')) == md5(os.path.join(M, 'sgd_last2.webp')) and md5(os.path.join(L, 'sfx_sgd2.m4a')) == md5(os.path.join(M, 'sfx_sgd2.m4a')),
                  f'新しい 3つ だけ（前の 3つと なくした 演出の ものは ない）・アプリに 入れる {len(BF.ASSET_FILES)}こ ぜんぶ ある・動画は CRF 24（さいごの 30コマは 23 → 22 → 21）で 385コマ'
                  f'（{os.path.getsize(os.path.join(L, "sgd_film2.mp4")) / 1e6:.2f}MB：前の 動画は 10.88MB・14.23秒）・さいごの 1まいと 音は もとの まま')
    else:
        print('  ⚠️ 新しい 動画・さいごの 1まい・音が まだ ない（python3 kisekae/build_fx_films.py）か ffmpeg が ない')
else:
    print('  ⚠️ ios/fx_assets/ が ない（CI）→ ファイルの 確かめは しない')

print('■ リポジトリ')
root = os.path.dirname(W)
tracked = subprocess.run(['git', 'ls-files'], cwd=root, capture_output=True, text=True).stdout.split('\n')
ign = lambda p: subprocess.run(['git', 'check-ignore', '-q', p], cwd=root).returncode == 0
check(not [f for f in tracked if f.lower().endswith('.glb')] and not [f for f in tracked if re.search(r'(sgd_film|sgd_last|sfx_sgd)\d*\.(mp4|webp|m4a|webm)$|/fx_assets/|sgd162', f)]
      and ign('source/ios/fx_assets/sgd_film2.mp4') and ign('source/ios/lite/fx_assets/sgd_film2.mp4') and not ign('source/kisekae/flat/kami_glb.py') and os.path.isfile(os.path.join(FLAT, 'kami_glb.py')),
      'まさちゃんの 3D（GLB）・動画・さいごの 1まい・音・コマは リポジトリに 入って いない（道具 kisekae/flat/kami_glb.py だけ 入る）')

print('✅ ぜんぶ OK' if not fails else f'❌ {len(fails)}こ 失敗')
sys.exit(1 if fails else 0)
