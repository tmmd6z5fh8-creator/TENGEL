# 神様馬・幻の馬の 形の 直し（第4.161版・まさちゃん 2026/11/12 18:00「トレーニングセンターの神様馬、赤丸の位置から動く変なパーツが飛び出てる／
#   幻の馬は、赤丸の立髪の毛の色がブラックなっている。身体の表面の赤丸の箇所がボヤけているように見える。全て改善して！」・19:47「幻の馬、肩幅狭くして！」・20:01「赤丸の大きさにして！」）
#   python3 test_horse_fix.py   （ios/tc_assets/ が ある とき だけ 形の 確かめ。ない とき（CI）は コードの 確かめ だけ）
#   ・コード：アプリ（tc/tc_app.js）は 直した 形（tc_horse_bk_<名前>2）を 読む・描く 側（tc/tc_horse.js）の 直し（裏から 見える 面・こわれた 法線の 点・頂点の 色）は
#     印の ある 形（meta.fix・fx）だけ（ふつうの 馬・バケツなどの 物は 前と 同じ 絵）・前の 形は アプリにも 軽い 版にも 入れない（assets_dir.superseded）
#   ・もとの 形（マスター）：前の 4つは 消して いない・1バイトも かわって いない（新しい 形は 別の 名前で 足した）・道具（kisekae/tc/horse_fix.py）を もう一度 走らせても 同じ ファイル
#   ・神様馬：かわったのは 骨の 付け方 だけ（場所・絵・光は 同じ）・骨の「島」（付けまちがい）が ない・マントの 先 2まいは しっぽ／後ろ足を 動かしても 動かない（前は 動いて いた）
#   ・幻の馬：肩幅 0.78 → 0.62（頭・目は 動かない・すきまが できない・前後と 高さは 同じ）／にじむ つなぎの 膜だけに 印（紫の 紙は かえない）／裏返しの 2まいは 描く 側で 直す
#   ・軽い 版（アプリに 入る 形）：新しい 4つ だけ（前の 4つは ない）・番号を もどすと もとと 同じ
#   ・形・絵（まさちゃんの もとの 3D から 作った もの）は リポジトリに 入って いない
import hashlib, json, os, re, shutil, subprocess, sys, tempfile
W = os.path.dirname(os.path.abspath(__file__)); os.chdir(W)
sys.path.insert(0, W); sys.path.insert(0, os.path.join(W, 'kisekae', 'tc')); sys.path.insert(0, os.path.join(W, 'kisekae'))
import assets_dir
fails = []


def check(c, label):
    print(('  ✅ ' if c else '  ❌ ') + label)
    if not c:
        fails.append(label)


OLD = {'tc_horse_bk_kamisama.bin': '81e0d70fd7e36ff3d3aeb7ec5dd511ec', 'tc_horse_bk_kamisama.json': '07fcb37f39202b25a6ef03438857d47a',
       'tc_horse_bk_maboroshi.bin': 'f007c36a400cd367a5ad1069f4941119', 'tc_horse_bk_maboroshi.json': 'e2f36508e3771aa05beed547ac011cd6'}      # 前の 形（第4.160版まで）の md5
NEW = ['tc_horse_bk_kamisama2.json', 'tc_horse_bk_kamisama2.bin', 'tc_horse_bk_maboroshi2.json', 'tc_horse_bk_maboroshi2.bin']
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()

print('■ コード')
app = open(os.path.join(W, 'tc', 'tc_app.js'), encoding='utf8').read(); hs = open(os.path.join(W, 'tc', 'tc_horse.js'), encoding='utf8').read()
tool = open(os.path.join(W, 'kisekae', 'tc', 'horse_fix.py'), encoding='utf8').read()
spec = re.search(r"function horseSpec\(\) \{.*?\n  \}", app, re.S).group(0)
check("name: 'tc_horse_bk_kamisama2'" in spec and "name: 'tc_horse_bk_maboroshi2'" in spec and "tc_horse_bk_kamisama'" not in app and "tc_horse_bk_maboroshi'" not in app
      and spec.count('stance: STANCE_KAMI') == 1 and spec.count('stance:') == 1,
      'アプリは 直した 形（tc_horse_bk_kamisama2・tc_horse_bk_maboroshi2）を 読む（前の 名前は 読まない）・幻の馬の 肩幅は 形の 中で 直して ある（アプリで 動かすのは 神様馬の 立ち方 だけ）')
fs_ = hs.split("const FS = [")[1].split("].join('\\n');")[0]; vs_ = hs.split("const VS = [")[1].split("].join('\\n');")[0]
check("'uniform vec3 uFix;'" in fs_ and 'bool bk=!gl_FrontFacing;float fx=uFix.z*vC.a;' in fs_ and 'uFix.y*(1.0-smoothstep(-0.5,-0.2,dn))' in fs_
      and 'if(uFix.x>0.5&&bk&&n.z<0.0){n=-n;av=max(av,0.72);cv=-cv;}' in fs_ and 'mix(texture2D(uTex,vUV).rgb,vC.rgb,fx)' in fs_ and 'attribute vec4 aCol,aNrm;' in vs_ and 'varying vec4 vC;' in vs_ and 'varying vec4 vC;' in fs_
      and "else if(bk)n=-n;" in fs_,
      '描く 側（シェーダー）：裏から 見えて 法線が むこう向きの 面は 向きを 直して 光らせる（x）・焼いた 法線が 面と 逆向きの 点は なめらかな 法線（y）・印つきの 頂点は 絵の かわりに 頂点の 色（z）＝どれも uFix が 0 なら 前と 同じ 式')
check("gl.uniform3f(h.loc.uFix, fix.two ? 1 : 0, fix.nfix ? 1 : 0, h.B.fx ? 1 : 0)" in hs and 'const fix = h.meta.fix || {};' in hs and hs.count('gl.uniform3f(h.loc.uFix, 0, 0, 0)') == 2
      and "if (h.B.fx) at(h.B.fx, h.loc.aCol, 4, gl.UNSIGNED_BYTE, true); else { gl.disableVertexAttribArray(h.loc.aCol); gl.vertexAttrib4f(h.loc.aCol, 1, 1, 1, 0); }" in hs
      and 'const fxb = fmt2 && lay.fx ? new Uint8Array(bin, lay.fx[0], nv * 4) : null;' in hs and "uFix: U('uFix')" in hs and hs.count('gl.vertexAttrib4f(h.loc.aCol, 1, 1, 1, 0)') == 2 and 'gl.vertexAttrib3f(h.loc.aCol' not in hs,
      '描く 側：直しを 使うのは 印の ある 形 だけ（meta.fix・fx の 列）・ふつうの 馬（印 なし）と 物（バケツ・エサ・ほうき）と 色だけの 古い 形は いつも (0,0,0)')
fa = {f'tc_horse_bk_{h}{s}.{e}' for h in ('kamisama', 'maboroshi', 'brown_s1') for s in ('', '2') for e in ('json', 'bin')} - {'tc_horse_bk_brown_s12.json', 'tc_horse_bk_brown_s12.bin'}
s1 = assets_dir.superseded('tc_assets', fa); s2 = assets_dir.superseded('tc_assets', fa - {'tc_horse_bk_kamisama2.bin'}); s3 = assets_dir.superseded('tc_assets', {f for f in fa if '2.' not in f})
check(s1 == set(OLD) and s2 == {'tc_horse_bk_maboroshi.bin', 'tc_horse_bk_maboroshi.json'} and s3 == set() and assets_dir.superseded('fig_assets', fa) == set(),
      '前の 形（4つ）は アプリにも 軽い 版にも 入れない（新しい 形の json と bin が そろって いる 馬 だけ。そろって いなければ 前の 形は 外さない。アプリに 新しい 形が 入って いるかは test_iphone_only.py が 見る）')
check('BODY_W = 0.62' in tool and 'STRETCH = (0.56, 0.46)' in tool and 'ISLAND = 0.5' in tool and 'BW_RING = (112, 76, 43, 19, 5)' in tool and '上書きしない' in tool
      and "extra = dict(fix=dict(two=1, nfix=1" in tool and 'kisekae/lite_assets.py' in tool,
      '道具（kisekae/tc/horse_fix.py）：肩幅 0.62・引きのばしの しきい値・島の しきい値・まぜ方の 表・もう ある ファイルは 上書きしない')
tracked = subprocess.run(['git', 'ls-files', 'ios/tc_assets', 'ios/lite'], cwd=W, capture_output=True, text=True).stdout.split()
check(tracked == [], '形・絵（ios/tc_assets・ios/lite）は リポジトリに 入って いない')

M = assets_dir.master('tc_assets')
if not all(os.path.isfile(os.path.join(M, f)) for f in list(OLD) + NEW + ['tc_c_maboroshi.webp']):
    print('（形の 確かめは 飛ばす：ios/tc_assets/ に 神様馬・幻の馬の 形が ない）')
else:
    import numpy as np
    from PIL import Image
    import horse_fix as HF
    print('■ もとの 形（マスター）')
    check(all(md5(os.path.join(M, f)) == h for f, h in OLD.items()), '前の 形 4つ（神様馬・幻の馬の json と bin）は 消して いない・1バイトも かわって いない')
    tmp = tempfile.mkdtemp(prefix='hfix_')
    try:
        quiet = lambda *a, **k: None
        rk, ik = HF.kamisama(tmp, log=quiet); rm, im_ = HF.maboroshi(tmp, log=quiet)
        same = all(open(os.path.join(tmp, f), 'rb').read() == open(os.path.join(M, f), 'rb').read() for f in NEW)
        check(same and all(r[2] == '作った' for r in rk + rm), f'道具を もう一度 走らせると 同じ ファイルが できる（{len(NEW)}つ とも 1バイトも ちがわない）')
        ck = [r[2] for r in HF.kamisama(M, check=True, log=quiet)[0] + HF.maboroshi(M, check=True, log=quiet)[0]]
        check(ck == ['そのまま（同じ 中身）'] * 4, '道具は もう ある ファイルを 上書きしない（同じ 中身か たしかめる だけ）')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print('■ 神様馬：マントの 先の 骨')
    k0, k2 = HF.load('kamisama'), HF.load('kamisama2'); names = k0['names']; bi = {n: i for i, n in enumerate(names)}
    eq = {k: bool(np.array_equal(k0[k], k2[k])) for k in ('pos', 'nrm', 'uv', 'idx', 'cv', 'bone', 'bone2', 'bw')}
    chg = k0['bone'] != k2['bone']
    check(all(eq[k] for k in ('pos', 'nrm', 'uv', 'idx', 'cv')) and not eq['bone'] and k2['fx'] is None and 'fix' not in k2['meta'] and k2['meta'].get('skinfix2', {}).get('verts') == int(chg.sum()) == 983
          and k2['meta']['v'] == k0['meta']['v'] and k2['meta']['i'] == k0['meta']['i'] and k2['meta']['layout'] == k0['meta']['layout'] and k2['meta']['bones'] == k0['meta']['bones'],
          f'かわったのは 骨の 付け方 だけ（場所・法線・かげ・絵の 場所・三角・折り目は 1バイトも 同じ・頂点 {int(chg.sum())} の 骨を 付け直した・光り方の 印は なし＝神様馬の 見た目は 前と 同じ）')

    def islands(d):
        g, ng, A = HF.graph(d); lab = HF.welded(g, ng, d['bone']); k, reg = HF.regions(A, lab); cnt = np.bincount(reg, minlength=k); rl = np.zeros(k, np.int64); rl[reg] = lab
        out = []
        for b in range(len(names)):
            cs = sorted((int(cnt[q]) for q in range(k) if rl[q] == b), reverse=True); out += [(names[b], c) for c in cs[1:]]
        return out
    i0, i2 = islands(k0), islands(k2)
    check(sorted(i0) == sorted([('HR_u', 207), ('HR_u', 8), ('tail2', 166), ('tail2', 13), ('tail2', 4), ('body', 85), ('body', 20), ('body', 8), ('body', 4)]) and i2 == [],
          f'骨の「島」（同じ 骨の 頂点の かたまりの うち いちばん 大きい もの 以外）：前は {len(i0)}こ（後ろ足の 骨に 207・しっぽの 先の 骨に 166 など）→ 0こ')
    t2 = chg & (k0['bone'] == bi['tail2']); hr = chg & (k0['bone'] == bi['HR_u']); bd = chg & (k0['bone'] == bi['body'])
    check(int(t2.sum()) == 329 and int(hr.sum()) == 440 and (k2['bone'][t2] == bi['body']).all() and (k2['bone'][hr] == bi['body']).all() and set(names[b] for b in np.unique(k2['bone'][bd])) == {'tail', 'FL_u'}
          and ((k2['bw'] > 0) == (k2['bone2'] != k2['bone'])).all() and int(k2['bw'].max()) <= 127,
          'マントの うしろの 先 2まい（しっぽの 先の 骨に 329頂点・右の 後ろ足の 骨に 440頂点）は 体の 骨に・しっぽの つけ根／前足の 中の 体の 骨の 島は まわりの 骨に')
    P = k0['pos'].astype(np.float64)

    def swing(d, bone, ang):
        """骨 bone だけを 回る 中心の まわりに（横の 軸で）ang 回した ときの 頂点の 動き（アプリと 同じ まぜ方：bone と bone2 を bw で）"""
        h = np.array(d['meta']['bones'][bi[bone]]['head']); c, s = np.cos(ang), np.sin(ang); R = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
        q = (P - h) @ R.T + h; w = d['bw'].astype(np.float64) / 255.0
        p1 = np.where((d['bone'] == bi[bone])[:, None], q, P); p2 = np.where((d['bone2'] == bi[bone])[:, None], q, P)
        return np.linalg.norm(p1 * (1 - w[:, None]) + p2 * w[:, None] - P, axis=1)
    a_t, b_t = swing(k0, 'tail2', 0.6)[t2], swing(k2, 'tail2', 0.6)[t2]; a_h, b_h = swing(k0, 'HR_u', 0.5)[hr], swing(k2, 'HR_u', 0.5)[hr]
    near = (~chg) & ((k0['bone2'] != k2['bone2']) | (k0['bw'] != k2['bw'])); a_n, b_n = swing(k0, 'tail2', 0.6)[near], swing(k2, 'tail2', 0.6)[near]
    check(a_t.mean() > 0.1 and a_t.max() > 0.18 and b_t.max() < 0.002 and a_h.mean() > 0.05 and a_h.max() > 0.12 and b_h.max() < 0.005 and b_n.mean() < a_n.mean() * 0.2,
          f'しっぽの 先を ふる：マントの 先（左）は 前は 平均 {a_t.mean():.3f}（体の 高さ 2.15 に 対して・いちばん 大きい 所 {a_t.max():.3f}）動いて 飛び出して いた → {b_t.max():.4f}／'
          f'右の 後ろ足を ふる：マントの 先（右）は 前は 平均 {a_h.mean():.3f}（{a_h.max():.3f}）→ {b_h.max():.4f}／まわりの 体も つられて 動かない（{a_n.mean():.4f} → {b_n.mean():.4f}）')

    print('■ 幻の馬：肩幅・にじむ 膜・裏返しの 面')
    m0, m2 = HF.load('maboroshi'), HF.load('maboroshi2'); nv0 = len(m0['pos']); mi = {n: i for i, n in enumerate(m0['names'])}
    tex = np.array(Image.open(os.path.join(M, m0['meta']['tex'])).convert('RGB')); idx0, idx2 = m0['idx'], m2['idx']
    fixm = m2['meta'].get('fix') or {}; slim = m2['meta'].get('slim') or {}
    check(fixm.get('two') == 1 and fixm.get('nfix') == 1 and 'fx' in m2['meta']['layout'] and m2['fx'] is not None and m2['meta']['i'] == m0['meta']['i'] and len(m2['pos']) == m2['meta']['v'] >= nv0
          and m2['meta']['tex'] == m0['meta']['tex'] and m2['meta']['ntex'] == m0['meta']['ntex'] and m2['meta']['eyes'] == m0['meta']['eyes'] and 'bin' not in m2['meta'],
          f'印：裏から 見える 面を 直す・こわれた 法線の 点を 直す・頂点の 色の 列（fx）あり／絵 2まい（色・法線）は 前と 同じ ファイル（作り直して いない＝画質は 落ちない）・頂点 {nv0} → {len(m2["pos"])}・三角は 同じ 数')
    p0, p2 = m0['pos'].astype(np.float64)[idx0], m2['pos'].astype(np.float64)[idx2]
    same_tri = np.array_equal(p0[..., :2], p2[..., :2]) and np.array_equal(m0['uv'][idx0], m2['uv'][idx2]) and all(np.array_equal(m0[k][idx0], m2[k][idx2]) for k in ('bone', 'bone2', 'bw')) and np.array_equal(m0['nrm'][idx0][..., 3], m2['nrm'][idx2][..., 3])
    w0, w2 = HF.body_width(m0), HF.body_width(m2); kk = w2 / w0
    hd = np.isin(m0['bone'], [mi['head'], mi['jaw']]); dz = m2['pos'][:nv0, 2].astype(np.float64) - m0['pos'][:, 2].astype(np.float64)
    g0 = HF.weld(m0['pos']); zs = np.zeros(int(g0.max()) + 1); zmin = np.full(len(zs), 1e9); zmax = np.full(len(zs), -1e9); np.minimum.at(zmin, g0, m2['pos'][:nv0, 2]); np.maximum.at(zmax, g0, m2['pos'][:nv0, 2])
    hoof = lambda d, L: float(d['pos'][(d['bone'] == mi[L + '_f']) & (d['pos'][:, 1] < d['pos'][d['bone'] == mi[L + '_f'], 1].min() + 0.04), 2].mean())
    hz = {L: (hoof(m0, L), hoof(m2, L)) for L in HF.LEGS}; bh = {L: (m0['meta']['bones'][mi[L + '_u']]['head'][2], m2['meta']['bones'][mi[L + '_u']]['head'][2]) for L in HF.LEGS}
    inward = bool((np.sign(dz[np.abs(dz) > 0.001]) == -np.sign(m0['pos'][:, 2][np.abs(dz) > 0.001])).all())      # 動いた 頂点は どれも まん中の 面の 方へ
    check(same_tri and abs(w0 - 0.779) < 0.003 and abs(w2 - 0.62) < 0.003 and slim.get('w') == [round(w0, 4), round(w2, 4)] and float(np.abs(dz[hd]).max()) < 0.002 and float((zmax - zmin).max()) < 1e-6 and inward
          and all(abs(hz[L][1] / hz[L][0] - kk) < 0.02 and abs(bh[L][1] / bh[L][0] - kk) < 0.03 for L in HF.LEGS) and float(np.abs(dz).max()) < 0.09,
          f'肩幅 {w0:.3f} → {w2:.3f}（×{kk:.3f}：赤丸の 見本の 大きさ）：横（まん中の 面へ）だけ 寄せた（前後・高さ・絵の 場所・骨・かげは 同じ）・頭と 目は 動かない・同じ 場所の 頂点は 同じ だけ 動く（すきまが できない）・'
          f'ひづめと 足の つけ根も 同じ 割合で 内がわへ（前足の ひづめ {hz["FL"][0]:.3f} → {hz["FL"][1]:.3f}）')
    fx = m2['fx']; a2 = fx[idx2, 3]; core = (a2 == 255).all(1); any_ = (a2 > 0).any(1)
    uv = m0['uv'].astype(np.float64) / 65535.0; BW = np.array([[.6, .2, .2], [.2, .6, .2], [.2, .2, .6], [.4, .4, .2], [.2, .4, .4], [.4, .2, .4]]); U = (uv[idx0][:, None, :, :] * BW[None, :, :, None]).sum(2)
    C = HF.tex_at(tex, U[..., 0].reshape(-1), U[..., 1].reshape(-1)).reshape(len(idx0), len(BW), 3); pur = HF.is_purple(C).mean(1) >= 0.5
    den, dmin, a3 = HF.tri_density(m0, tex.shape[1], tex.shape[0]); q = dmin / np.median(den); cy = m0['pos'][idx0][..., 1].mean(1)
    paper = fx[0, :3]; keep = a2 == 0
    webs = core & (q <= 0.462)                                                     # いちばん 引きのばされた 三角（道具の 数え方と ほぼ 同じ）。core＝3つの 頂点とも 強さ いっぱい（間に はさまれた 三角も 入る）
    check(fixm.get('webs') == 394 and abs(int(webs.sum()) - 394) <= 6 and 394 <= int(core.sum()) < 600 and not pur[any_].any() and float(cy[webs].min()) > HF.WEB_Y - 0.05 and (fx[:, :3] == paper).all() and 40 <= int(paper.max()) <= 70
          and np.array_equal(idx2[pur], idx0[pur]) and np.array_equal(m2['nrm'][idx2][keep], m0['nrm'][idx0][keep]) and np.array_equal(m2['cv'][idx2][keep], m0['cv'][idx0][keep])
          and 0.2 < float(a3[webs].sum()) < 0.5 and int(any_.sum()) < 2500 and len(m2['pos']) - nv0 < 40,
          f'にじむ つなぎの 膜（絵が 2倍より 大きく 引きのばされた 三角・たてがみの 生えぎわと しっぽの つけ根）{int(webs.sum())}こ（体の 表面の {a3[webs].sum() / a3.sum():.1%}）だけ 絵の かわりに 黒い 紙の 色 {paper.tolist()} と '
          f'となりの 体の 面の 向きで 描く・まわり 1列（合わせて {int(any_.sum())}こ）で なめらかに 絵へ もどる・紫の 紙（たてがみ・しっぽ）は 1つも かえない・印の ない 頂点の 法線と 折り目は 前と 同じ')
    g2, ng2, A2 = HF.graph(m0); import scipy.sparse.csgraph as cg
    kc, lab = cg.connected_components(A2, directed=False); tl = lab[g2[idx0[:, 0]]]; T = m0['pos'].astype(np.float64)[idx0]; sv = (np.cross(T[:, 0], T[:, 1]) * T[:, 2]).sum(1) / 6
    vol = sorted((round(float(sv[tl == c].sum()), 4), int((tl == c).sum())) for c in range(kc)); T2 = m2['pos'].astype(np.float64)[idx2]; sv2 = (np.cross(T2[:, 0], T2[:, 1]) * T2[:, 2]).sum(1) / 6
    check(kc == 3 and vol[0][0] < 0 and vol[1][0] < 0 and vol[2][0] > 0.5 and {vol[0][1], vol[1][1]} == {2088, 2526} and all(float(sv2[tl == c].sum()) < 0 for c in range(kc) if (tl == c).sum() < 3000),
          f'たてがみの 中の 2まい（三角 2088・2526）は 面の 向きが 裏返し（体積が 負：{vol[0][0]}・{vol[1][0]}）＝ 形は そのまま（絵を 作り直さない）で、描く 側が 裏から 見える 面の 向きを 直して 光らせる')

    print('■ 軽い 版（アプリに 入る 形）')
    L = assets_dir.lite('tc_assets')
    if not os.path.isdir(L):
        print('（飛ばす：ios/lite/tc_assets が ない）')
    else:
        import lite_assets as LA
        lf = set(os.listdir(L)); man = assets_dir.manifest('tc_assets') or {'files': {}}
        check(all(f in lf for f in NEW) and not any(f in lf for f in OLD) and not assets_dir.stale('tc_assets')
              and all(LA.unpack_idx(open(os.path.join(L, f), 'rb').read()) == open(os.path.join(M, f), 'rb').read() and open(os.path.join(L, f), 'rb').read(4) == b'TGIZ' for f in NEW if f.endswith('.bin'))
              and all(open(os.path.join(L, f), 'rb').read() == open(os.path.join(M, f), 'rb').read() for f in NEW if f.endswith('.json')) and all(man['files'].get(f, {}).get('how') == ('idxz' if f.endswith('.bin') else 'copy') for f in NEW),
              f'新しい 形 4つ だけ（前の 4つは ない）・番号を もどすと もとと 1バイトも ちがわない（幻の馬の 形 {os.path.getsize(os.path.join(L, "tc_horse_bk_maboroshi2.bin")) / 1e6:.2f}MB・神様馬 {os.path.getsize(os.path.join(L, "tc_horse_bk_kamisama2.bin")) / 1e6:.2f}MB）')

print('✅ ぜんぶ OK' if not fails else f'❌ {len(fails)}こ 失敗')
sys.exit(1 if fails else 0)
