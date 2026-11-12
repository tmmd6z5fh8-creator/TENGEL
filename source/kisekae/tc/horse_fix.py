#!/usr/bin/env python3
"""トレーニングセンターの 神様馬・幻の馬の 形（3D）の 直し（第4.161版・まさちゃん 2026/11/12 18:00
   「神様馬、赤丸の位置から動く変なパーツが飛び出てる／幻の馬は、赤丸の立髪の毛の色がブラックなっている。身体の表面の赤丸の箇所がボヤけているように見える。全て改善して！」）

   もとの 形（ios/tc_assets/tc_horse_bk_<名前>.json＋.bin・色の 絵 tc_c_<名前>.webp）は **読む だけ**。直した 形は 名前の おわりに 2 を つけて 新しく 作る
   （tc_horse_bk_<名前>2.json＋.bin：前の 形は 上書きしない・消さない → アプリに 入れるのは 新しい 方 だけ＝assets_dir.superseded）。

   神様馬（kamisama）：骨の 付けまちがい。マントの うしろの 先（左右 2まい）が しっぽの 先の 骨（tail2）と 右の 後ろ足の 骨（HR_u）に 付いて いて、
     しっぽ・足と いっしょに 動いて 腰から 飛び出して いた。骨ごとの「島」（同じ 骨の 頂点の かたまりの うち、いちばん 大きい もの 以外）を
     となりの 骨に 付け直す（マントの 先 → 体）。となりの 骨との まぜ方（bone2・bw）は 直した 所の まわり だけ 作り直す（ほかは 1バイトも かえない）。
   幻の馬（maboroshi）：体を 横に 広げた ときに 引きのばされた 三角（たてがみの 生えぎわ・しっぽの つけ根の「つなぎの 膜」）は 絵（テクスチャ）が 足りなくて
     にじんで 見えた。その 三角 だけ「絵を 使わないで、まわりの 紙の 色と なめらかな 面の 向きで 描く」印（頂点ごとの fx：色 3＋強さ 1）を つける。
     たてがみの 裏返しの 2まい（面の 向きが 逆で 黒く 見えた）と 法線の 絵の こわれた 点は、描く 側（tc/tc_horse.js：meta.fix の 形 だけ）が 直す。
     肩幅（19:47「幻の馬、肩幅狭くして！」・20:01「赤丸の大きさにして！」）：体・首の つけ根・足を まん中へ 寄せる（横幅 0.78 → 0.62）。
     頭と 目は そのまま・足は 細く しない（足ごと 内がわへ）。場所 だけ かえる（骨の 付け先・絵の 場所は そのまま）→ ふちが がたがたに ならない。

   使い方：python3 kisekae/tc/horse_fix.py kamisama|maboroshi [出す フォルダ（なければ ios/tc_assets）] [--check]
     同じ 入力からは いつも 同じ ファイルが できる。出す 先に もう ある ときは 中身が 同じか たしかめる だけ（ちがえば 止まる：上書きしない）。--check は 作らないで くらべる だけ
     作った あと：python3 kisekae/lite_assets.py（アプリに 入れる 軽い 版を 作り直す）
"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
import assets_dir

LEGS = ('FL', 'FR', 'HL', 'HR')
STREAMS = (('pos', '<f4', 3), ('nrm', 'i1', 4), ('uv', '<u2', 2), ('bone', 'u1', 1), ('bone2', 'u1', 1), ('bw', 'u1', 1), ('idx', None, 0), ('cv', 'u1', 1), ('fx', 'u1', 4))      # bin の 中の 並び（idx は 三角の 番号）
BW_RING = (112, 76, 43, 19, 5)      # 骨の 境目からの 輪の 数（0〜4）ごとの まぜる 強さ（0〜127 ≒ 0〜0.5）：もとの データの まん中の 値（輪 0：112・1：76・2：43・3：19・4：5）
ISLAND = 0.5                        # 同じ 骨の いちばん 大きい かたまりの この 割合より 小さい かたまり ＝ 島（付けまちがい）


# ---------- 読む・書く ----------
def load(name, root=None):
    root = root or assets_dir.master('tc_assets')
    m = json.load(open(os.path.join(root, f'tc_horse_bk_{name}.json'), encoding='utf8'))
    raw = open(os.path.join(root, m.get('bin') or f'tc_horse_bk_{name}.bin'), 'rb').read()
    assert raw[:4] != b'TGIZ', 'もとの 形（ios/tc_assets）を 読む こと（軽い 版では ない）'
    L = m['layout']; nv = m['v']
    f = lambda k, dt, n: np.frombuffer(raw, dtype=dt, count=n, offset=L[k][0]).copy()
    d = dict(name=name, meta=m, pos=f('pos', '<f4', nv * 3).reshape(nv, 3), nrm=f('nrm', 'i1', nv * 4).reshape(nv, 4), uv=f('uv', '<u2', nv * 2).reshape(nv, 2),
             bone=f('bone', 'u1', nv), bone2=f('bone2', 'u1', nv), bw=f('bw', 'u1', nv), idx=f('idx', '<u4' if m.get('idx32') else '<u2', m['i']).reshape(-1, 3).astype(np.int64), cv=f('cv', 'u1', nv))
    d['fx'] = f('fx', 'u1', nv * 4).reshape(nv, 4) if 'fx' in L else None
    d['names'] = [b['name'] for b in m['bones']]
    assert m.get('fmt') == 2 and m.get('idx32'), '神様馬・幻の馬の 形（fmt 2・番号 32bit）用'
    return d


def pack(d, extra):
    """直した 形 → (json の 文字, bin の 中身)。並びと 4バイトの そろえ方は もとと 同じ"""
    nv = len(d['pos']); parts = []; lay = {}; off = 0
    for key, dt, n in STREAMS:
        if key == 'idx':
            a = np.ascontiguousarray(d['idx'].reshape(-1), '<u4')
        elif d.get(key) is None:
            continue
        else:
            a = np.ascontiguousarray(d[key].reshape(-1), dt); assert a.size == nv * n, (key, a.size, nv, n)
        b = a.tobytes(); pad = (-off) % 4
        if pad:
            parts.append(b'\0' * pad); off += pad
        lay[key] = [off, len(b)]; parts.append(b); off += len(b)
    meta = dict(d['meta']); meta.pop('bin', None)
    meta.update(v=nv, i=int(d['idx'].size), layout=lay); meta.update(extra)
    return json.dumps(meta), b''.join(parts)


def emit(d, name2, extra, out, check=False):
    js, raw = pack(d, extra); res = []
    for f, data in ((f'tc_horse_bk_{name2}.json', js.encode('utf8')), (f'tc_horse_bk_{name2}.bin', raw)):
        p = os.path.join(out, f)
        if os.path.isfile(p):
            same = open(p, 'rb').read() == data
            assert same, f'{p}：もう ある ファイルと 中身が ちがう（上書きしない）。作り直す ときは 別の フォルダへ 出して たしかめる'
            res.append((f, len(data), 'そのまま（同じ 中身）'))
        elif check:
            res.append((f, len(data), 'まだ ない'))
        else:
            tmp = p + '.tmp'; open(tmp, 'wb').write(data); os.replace(tmp, p); res.append((f, len(data), '作った'))
    return res


# ---------- 形の つながり ----------
def weld(pos, eps=1e-5):
    """同じ 場所の 頂点を 1つに（絵の 切れ目で 分かれた 頂点を つなぐ）→ 頂点ごとの 組の 番号"""
    q = np.round(pos.astype(np.float64) / eps).astype(np.int64)
    _, inv = np.unique(q, axis=0, return_inverse=True)
    return inv.reshape(-1)


def graph(d):
    """→ (頂点 → 溶接した 頂点の 番号, 溶接した 頂点の 数, となりの 表（CSR：indptr・indices）)"""
    import scipy.sparse as sp
    g = weld(d['pos']); ng = int(g.max()) + 1; a = g[d['idx']]
    e = np.concatenate([a[:, [0, 1]], a[:, [1, 2]], a[:, [2, 0]]]); e = e[e[:, 0] != e[:, 1]]
    A = sp.coo_matrix((np.ones(len(e), np.int8), (e[:, 0], e[:, 1])), shape=(ng, ng)).tocsr(); A = ((A + A.T) > 0).astype(np.int8).tocsr(); A.sort_indices()
    return g, ng, A


def welded(g, ng, per_vertex):
    """頂点ごとの 値 → 溶接した 頂点ごと（同じ 場所の 頂点は 同じ 値の はず）"""
    out = np.zeros(ng, np.int64); out[g] = per_vertex
    assert (out[g] == per_vertex).all(), '同じ 場所の 頂点で 値が ちがう'
    return out


def regions(A, lab):
    """同じ 骨の 頂点が つながった かたまり → (数, 溶接した 頂点ごとの かたまりの 番号)"""
    import scipy.sparse as sp, scipy.sparse.csgraph as cg
    ng = A.shape[0]; src = np.repeat(np.arange(ng), np.diff(A.indptr)); keep = lab[src] == lab[A.indices]
    G = sp.coo_matrix((np.ones(int(keep.sum()), np.int8), (src[keep], A.indices[keep])), shape=(ng, ng))
    return cg.connected_components(G, directed=False)


def spread(A, start, maxr, through=None):
    """start（溶接した 頂点の 印）から 何輪か → 輪の 数（とどかない 所は 99）。through が あれば その 印の 頂点 だけ 通る"""
    ng = A.shape[0]; r = np.full(ng, 99, np.int64); r[start] = 0; cur = start.copy()
    for k in range(1, maxr + 1):
        nx = (A @ cur.astype(np.int8)) > 0; nx &= r == 99
        if through is not None:
            nx &= through
        if not nx.any():
            break
        r[nx] = k; cur = nx
    return r


def boundary_rings(A, lab, maxr):
    """溶接した 頂点ごと：いちばん 近い「別の 骨」までの 輪の 数（0＝となりが 別の 骨・同じ 骨の 中を たどる・とどかなければ 99）と その 骨"""
    ng = A.shape[0]; ci = A.indices; cp = A.indptr; src = np.repeat(np.arange(ng), np.diff(cp)); diff = lab[src] != lab[ci]
    r = np.full(ng, 99, np.int64); other = np.full(ng, -1, np.int64)
    b0 = np.unique(src[diff]); r[b0] = 0
    for v in b0:
        nb = lab[ci[cp[v]:cp[v + 1]]]; nb = nb[nb != lab[v]]; other[v] = np.bincount(nb).argmax()      # となりで いちばん 多い 別の 骨（同じ 数なら 番号の 小さい 方）
    front = b0
    for k in range(1, maxr + 1):
        nxt = []
        for v in front:
            for u in ci[cp[v]:cp[v + 1]]:
                if r[u] == 99 and lab[u] == lab[v]:
                    r[u] = k; other[u] = other[v]; nxt.append(u)
        front = np.array(nxt, np.int64)
        if not len(front):
            break
    return r, other


# ---------- 神様馬：骨の 付け直し ----------
def fix_islands(d, log=print):
    """骨ごとの 島（付けまちがい）を となりの 骨に 付け直す → (直した d, 記録)"""
    names = d['names']; g, ng, A = graph(d); ci = A.indices; cp = A.indptr; src = np.repeat(np.arange(ng), np.diff(cp))
    lab0 = welded(g, ng, d['bone']); lab = lab0.copy(); moved = []
    gp = np.zeros((ng, 3)); gp[g] = d['pos']
    for _pass in range(20):
        k, reg = regions(A, lab); cnt = np.bincount(reg, minlength=k)
        rl = np.zeros(k, np.int64); rl[reg] = lab                          # かたまりごとの 骨
        main = {}
        for r_ in range(k):
            if rl[r_] not in main or cnt[r_] > cnt[main[rl[r_]]]:
                main[int(rl[r_])] = r_
        isl = [r_ for r_ in range(k) if r_ != main[int(rl[r_])] and cnt[r_] < ISLAND * cnt[main[int(rl[r_])]]]
        if not isl:
            break
        for r_ in sorted(isl, key=lambda q: (-cnt[q], q)):                 # 大きい 島から（同じ 大きさなら 番号 順：いつも 同じ 結果）
            vs = np.nonzero(reg == r_)[0]
            if (lab[vs] != rl[r_]).any():
                continue                                                   # この 回で もう 付け直した
            inn = np.zeros(ng, bool); inn[vs] = True; e = inn[src] & ~inn[ci]; nb = np.bincount(lab[ci[e]], minlength=len(names))
            to = int(nb.argmax()); assert nb[to] > 0 and to != rl[r_]
            moved.append(dict(frm=names[int(rl[r_])], to=names[to], n=int(len(vs)), center=[round(float(v), 3) for v in gp[vs].mean(0)], lo=[round(float(v), 3) for v in gp[vs].min(0)], hi=[round(float(v), 3) for v in gp[vs].max(0)]))
            lab[vs] = to
    else:
        raise AssertionError('島が なくならない')
    ch = lab != lab0
    # まぜ方（bone2・bw）を 作り直す 頂点：付け直した 頂点 ＋ その 島と まぜて いた まわりの 頂点（島の もとの 骨と まぜて いて、その 骨の 本体より 島の 方が 近い）
    b2 = welded(g, ng, d['bone2']); bw = welded(g, ng, d['bw'])
    redo = ch.copy()
    for L in np.unique(lab0[ch]):
        near = spread(A, ch & (lab0 == L), 8); far = spread(A, (lab == L), 8)        # 島から の 輪・その 骨の 本体（付け直した あと）から の 輪
        redo |= (~ch) & (bw > 0) & (b2 == L) & (near < 99) & (near < far)
    r, other = boundary_rings(A, lab, len(BW_RING) - 1)
    nb2 = b2.copy(); nbw = bw.copy()
    hit = redo & (r < len(BW_RING)); nb2[hit] = other[hit]; nbw[hit] = np.array(BW_RING)[r[hit]]
    miss = redo & ~hit; nb2[miss] = lab[miss]; nbw[miss] = 0
    out = dict(d); out['bone'] = lab[g].astype(np.uint8); out['bone2'] = nb2[g].astype(np.uint8); out['bw'] = nbw[g].astype(np.uint8)
    assert ((out['bw'] > 0) == (out['bone2'] != out['bone'])).all()
    # たしかめ：島が のこって いない・付け直して いない 頂点の 骨は そのまま
    k, reg = regions(A, lab); cnt = np.bincount(reg, minlength=k); rl = np.zeros(k, np.int64); rl[reg] = lab
    for b in range(len(names)):
        cs = sorted((int(cnt[q]) for q in range(k) if rl[q] == b), reverse=True)
        assert len(cs) <= 1 or cs[1] >= ISLAND * cs[0], (names[b], cs[:4])
    info = dict(moved=moved, verts=int(ch[g].sum()), welded=int(ch.sum()), blend=int((redo & ~ch)[g].sum()),
                bone_changed=int((out['bone'] != d['bone']).sum()), bone2_changed=int((out['bone2'] != d['bone2']).sum()), bw_changed=int((out['bw'] != d['bw']).sum()))
    for m_ in moved:
        log('  島 %-5s → %-5s  頂点 %4d（溶接）  まん中 %s' % (m_['frm'], m_['to'], m_['n'], m_['center']))
    log('  付け直した 頂点 %d（溶接 %d）・まぜ方を 作り直した まわりの 頂点 %d・bone2 %d・bw %d' % (info['verts'], info['welded'], info['blend'], info['bone2_changed'], info['bw_changed']))
    return out, info


def kamisama(out, check=False, log=print):
    d = load('kamisama'); log('神様馬：頂点 %d・三角 %d' % (len(d['pos']), len(d['idx'])))
    fixed, info = fix_islands(d, log)
    for k in ('pos', 'nrm', 'uv', 'idx', 'cv'):
        assert np.array_equal(fixed[k], d[k]), k                           # 形・絵の 場所・光は 1バイトも かえない
    extra = dict(skinfix2=dict(v='4.161', islands=len(info['moved']), verts=info['verts'], note='11/12 18:00 マントの 先が しっぽ・後ろ足の 骨に 付いて いた → 体に 付け直し'))
    return emit(fixed, 'kamisama2', extra, out, check), info


# ---------- 幻の馬：にじむ 三角（つなぎの 膜）を きれいに ----------
STRETCH = (0.56, 0.46)          # いちばん 引きのばされた 向きの 絵の 細かさ（テクセル／長さ）÷ 全体の まん中の 値：0.56 より 細かければ そのまま・0.46 より 粗ければ 絵を 使わない（間は なめらかに）
                                #   つなぎの 膜は 2倍より 大きく のびて いる（0.45 より 小さい）・体を 広げた だけの 面（背中・おしり）は 1.5倍 くらい（0.6〜0.7）＝ かえない
WEB_Y = 1.25                    # たてがみの 生えぎわ・しっぽの つけ根（体の 上の 方）だけ 直す（足の つけ根・ひざは さわらない：黒い 紙で にじみが 見えない）
WEB_BONES = ('body', 'neck', 'tail', 'tail2')
WEB_AREA = 0.003                # つなぎの 膜＝引きのばされた 三角が 辺で つながった かたまりの うち、紫の 紙（たてがみ・しっぽ）の 頂点から 2輪 より 近くて、面積が これ 以上の もの
WEB_NEAR = 2                    #   （肩の 横・背中の 折り目に そった 細い 三角の 列は 紫の 紙から 遠い・小さい ＝ かえない）


def tri_density(d, tw, th):
    """三角ごと：絵の 細かさ（テクセル／体の 長さ 1：面積から）・いちばん 引きのばされた 向きの 細かさ（絵 → 形の のび方の 大きい 方から）・面積"""
    P = d['pos'].astype(np.float64); idx = d['idx']; uv = d['uv'].astype(np.float64) / 65535.0
    T3 = P[idx]; a3 = 0.5 * np.linalg.norm(np.cross(T3[:, 1] - T3[:, 0], T3[:, 2] - T3[:, 0]), axis=1)
    T2 = uv[idx] * [tw, th]; E2 = np.stack([T2[:, 1] - T2[:, 0], T2[:, 2] - T2[:, 0]], 2); E3 = np.stack([T3[:, 1] - T3[:, 0], T3[:, 2] - T3[:, 0]], 2)
    det = E2[:, 0, 0] * E2[:, 1, 1] - E2[:, 0, 1] * E2[:, 1, 0]; a2 = 0.5 * np.abs(det)
    den = np.sqrt(a2 / np.maximum(a3, 1e-12))
    ok = np.abs(det) > 1e-9; dd = np.where(ok, det, 1.0)
    inv = np.stack([np.stack([E2[:, 1, 1] / dd, -E2[:, 0, 1] / dd], 1), np.stack([-E2[:, 1, 0] / dd, E2[:, 0, 0] / dd], 1)], 1)      # E2 の 逆
    J = E3 @ inv                                                                   # 形の 長さ／テクセル（3×2）
    G = np.einsum('nij,nik->njk', J, J); tr = G[:, 0, 0] + G[:, 1, 1]; dt = G[:, 0, 0] * G[:, 1, 1] - G[:, 0, 1] ** 2
    s1 = np.sqrt(np.maximum(tr / 2 + np.sqrt(np.maximum(tr * tr / 4 - dt, 0)), 1e-30))                                             # いちばん のびた 向きの 長さ／テクセル
    dmin = np.where(ok, 1.0 / s1, 0.0)
    return den, dmin, a3


def tex_at(tex, u, v):
    """絵の 色（まわり 4点を なめらかに まぜる）：u, v は 0〜1"""
    th, tw = tex.shape[:2]; x = u * tw - 0.5; y = v * th - 0.5; x0 = np.floor(x).astype(np.int64); y0 = np.floor(y).astype(np.int64); fx = (x - x0)[:, None]; fy = (y - y0)[:, None]
    g = lambda yy, xx: tex[np.clip(yy, 0, th - 1), np.clip(xx, 0, tw - 1)].astype(np.float64)
    return (g(y0, x0) * (1 - fx) + g(y0, x0 + 1) * fx) * (1 - fy) + (g(y0 + 1, x0) * (1 - fx) + g(y0 + 1, x0 + 1) * fx) * fy


def is_purple(c):
    return (c[..., 2] - c[..., 1] > 50) & (c[..., 0] - c[..., 1] > 25)


def ramp(x, hi, lo):
    """hi より 上＝0・lo より 下＝1（間は なめらかに）"""
    u = np.clip((hi - x) / (hi - lo), 0, 1); return u * u * (3 - 2 * u)


def clean_webs(d, tex, log=print, shape=None):
    """引きのばされた 三角（絵が 足りなくて にじむ：たてがみの 生えぎわ・しっぽの つけ根の つなぎの 膜）に
       「絵を 使わないで、まわりの 紙の 色と なめらかな 法線で 描く」印（fx：色 3＋強さ 1）を つける → (直した d, 記録)
       強さは 頂点ごと（その 頂点を 使う 黒い 紙の 三角の うち いちばん 引きのばされた もの）＝ 膜の 三角は ぜんぶ 同じ 描き方に なり、まわりの 三角 1列で なめらかに 絵へ もどる。
       紫の 紙（たてがみ・しっぽ）の 三角は かえない：同じ 頂点を 紫の 三角も 使う ときは、黒い 紙の 三角 用に 頂点の 写しを 作る。
       shape：出す 形（肩幅を 細く した あとの 形）。どの 三角が 膜かは d（体を 広げた ままの もとの 形：引きのばしが はっきり 出る）で 決めて、場所と 面の 向きは shape の もの を 使う
       （細く した あとの 形で 決めると、引きのばしが へって 膜の 一部を 見のがす：絵の にじみは 形を 細く しても のこる）"""
    geo = d if shape is None else shape; assert np.array_equal(geo['idx'], d['idx']) and len(geo['pos']) == len(d['pos'])
    names = d['names']; idx = d['idx']; nv = len(d['pos']); th, tw = tex.shape[:2]; uv = d['uv'].astype(np.float64) / 65535.0
    den, dmin, a3 = tri_density(d, tw, th); med = float(np.median(den))
    cen = d['pos'].astype(np.float64)[idx].mean(1); okb = np.isin(d['bone'], [names.index(n) for n in WEB_BONES])
    reg = (cen[:, 1] > WEB_Y) & okb[idx].all(1)
    # 三角ごとの 色（中の 6点）と 紫（たてがみ・しっぽ）か 黒（体）か
    BW = np.array([[.6, .2, .2], [.2, .6, .2], [.2, .2, .6], [.4, .4, .2], [.2, .4, .4], [.4, .2, .4]])
    U = (uv[idx][:, None, :, :] * BW[None, :, :, None]).sum(2)                    # (三角, 6, 2)
    C = tex_at(tex, U[..., 0].reshape(-1), U[..., 1].reshape(-1)).reshape(len(idx), len(BW), 3)
    pur = is_purple(C).mean(1) >= 0.5
    g, ng, A0 = graph(d); gi = g[idx]
    ft = ramp(dmin / med, *STRETCH) * (reg & ~pur)                                # 三角ごとの 強さ（0〜1）：紫の 三角・直す 場所の 外は 0
    pv = np.zeros(ng, bool); pv[gi[pur].reshape(-1)] = True; near = spread(A0, pv, WEB_NEAR)      # 紫の 紙の 頂点から の 輪の 数
    cand = np.nonzero(ft > 0)[0]; par = {int(t): int(t) for t in cand}; edge = {}
    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]; x = par[x]
        return x
    for t in cand:                                                                # 辺で つながった かたまり
        a_, b_, c_ = (int(v) for v in gi[t])
        for u_, v_ in ((a_, b_), (b_, c_), (c_, a_)):
            key = (u_, v_) if u_ < v_ else (v_, u_)
            if key in edge:
                ra, rb = find(edge[key]), find(int(t))
                if ra != rb:
                    par[max(ra, rb)] = min(ra, rb)
            else:
                edge[key] = int(t)
    root = np.array([find(int(t)) for t in cand], np.int64); webs = 0
    for r_ in np.unique(root):
        ts_ = cand[root == r_]
        if near[gi[ts_]].min() <= WEB_NEAR and a3[ts_].sum() >= WEB_AREA:
            webs += 1
        else:
            ft[ts_] = 0
    wv = np.zeros(ng); np.maximum.at(wv, gi.reshape(-1), np.repeat(ft, 3))        # 溶接した 頂点ごとの 強さ
    dark = ~pur                                                                    # 黒い 紙の 三角（強さの ある 頂点を 使う ものは 印つきの 頂点で 描く）
    core = ft >= 0.999; soft = dark & (wv[gi].max(1) > 0)
    # 紙の 色：体の 上の 方の「引きのばされて いない 黒い 紙の 三角」の 色の まん中の 値 1つ（黒い 紙は どこも ほぼ 同じ 色：明るさ 48〜62）。
    #   頂点ごとに 近くの 絵から とる やり方は、膜の ふちの 絵に のこる 白い にじみを ひろって 明るい ふちどりが 出た ので やめた
    clean = dark & (ft <= 0.001)
    paper = np.clip(np.round(np.median(C[clean & reg].reshape(-1, 3), axis=0)), 0, 255).astype(np.uint8)
    # 面の 向き（なめらかな 法線）：膜は もとの 形に ない 面（たてがみの ふちと 広げた 体を つなぐ）なので、自分の 向きで 光らせると ギザギザの 帯に 見える。
    #   → となりの 体の 面（引きのばされて いない 黒い 紙の 三角）の 向きを 膜の 中へ つたえて、体の 面の つづきに 見える ように する
    import scipy.sparse as sp
    P64 = geo['pos'].astype(np.float64); T = P64[idx]; fnv = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])     # 面の 向き × 面積の 2倍（出す 形で）
    body_n = np.zeros((ng, 3)); np.add.at(body_n, gi[clean].reshape(-1), np.repeat(fnv[clean], 3, axis=0))
    need = wv > 0; nodes = np.nonzero(need)[0]; pos_of = np.full(ng, -1, np.int64); pos_of[nodes] = np.arange(len(nodes)); n = len(nodes)
    nn_ = body_n[nodes]; ln = np.linalg.norm(nn_, axis=1); fixed = ln > 1e-12; nn_[fixed] /= ln[fixed, None]
    a = pos_of[gi[soft]]; e = np.concatenate([a[:, [0, 1]], a[:, [1, 2]], a[:, [2, 0]]]); e = e[(e[:, 0] >= 0) & (e[:, 1] >= 0) & (e[:, 0] != e[:, 1])]
    Aw = sp.coo_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), shape=(n, n)).tocsr(); Aw = ((Aw + Aw.T) > 0).astype(np.float64).tocsr()
    for _ in range(400):                                                          # 体の 面に さわらない 頂点（たてがみの ふち・膜の 中）：となりの 平均を くり返す
        nx = Aw @ nn_; ln = np.linalg.norm(nx, axis=1); okn = ln > 1e-12; nx[okn] /= ln[okn, None]; nn_ = np.where(fixed[:, None] | ~okn[:, None], nn_, nx)
    have = np.linalg.norm(nn_, axis=1) > 0.5                                      # どこからも とどかない 頂点は もとの 向きの まま
    def new_nrm(v, w):                                                            # 頂点 v（強さ w）の 新しい なめらかな 法線（int8×3）
        i = pos_of[g[v]]; old = d['nrm'][v, :3].astype(np.float64) / 127.0
        if i < 0 or not have[i]:
            return d['nrm'][v, :3]
        m_ = old * (1 - w) + nn_[i] * w; l_ = np.linalg.norm(m_)
        return d['nrm'][v, :3] if l_ < 1e-6 else np.clip(np.round(m_ / l_ * 127), -127, 127).astype(np.int8)
    # 頂点：紫の 三角も 使う 頂点は 写しを 作る（黒い 紙の 三角 用）・そうで なければ そのまま 印を つける
    used_p = np.zeros(nv, bool); used_p[idx[pur].reshape(-1)] = True
    fxs = np.zeros((nv, 4), np.uint8); fxs[:, :3] = paper; nidx = idx.copy(); rows = []; copy_of = {}      # 色は どの 頂点も 紙の 色（強さ 0 の 頂点も：三角の 中で 色を まぜる とき、白が まざって 明るい ふちどりに ならない ように）
    cvn = d['cv'].astype(np.float64).copy(); nrn = d['nrm'].copy()
    for t in np.nonzero(soft)[0]:
        for c in range(3):
            v = int(idx[t, c]); w = wv[g[v]]
            if w <= 0:
                continue
            if used_p[v]:
                if v not in copy_of:
                    copy_of[v] = nv + len(rows); rows.append(v)
                nidx[t, c] = copy_of[v]
            else:
                fxs[v, 3] = int(round(w * 255)); cvn[v] = 128 + (cvn[v] - 128) * (1 - w); nrn[v, :3] = new_nrm(v, w)
    rows = np.array(rows, np.int64)
    out = {k: (geo[k].copy() if isinstance(geo[k], np.ndarray) else geo[k]) for k in geo}
    for k in ('pos', 'uv', 'bone', 'bone2', 'bw'):
        out[k] = np.concatenate([geo[k], geo[k][rows]])
    nrx = d['nrm'][rows].copy()
    for j_, v in enumerate(rows):
        nrx[j_, :3] = new_nrm(int(v), wv[g[v]])
    out['nrm'] = np.concatenate([nrn, nrx])
    cvx = d['cv'][rows].astype(np.float64); wr = wv[g[rows]]
    out['cv'] = np.clip(np.round(np.concatenate([cvn, 128 + (cvx - 128) * (1 - wr)])), 0, 255).astype(np.uint8)
    fxr = np.zeros((len(rows), 4), np.uint8); fxr[:, :3] = paper; fxr[:, 3] = np.round(wr * 255).astype(np.uint8)
    out['idx'] = nidx; out['fx'] = np.concatenate([fxs, fxr])
    # たしかめ：場所・骨は どの 三角も そのまま／紫の 三角は 1つも かわらない（印 なしの 頂点 だけ）／いちばん 引きのばされた 三角は 3つの 頂点とも 強さ いっぱい
    assert np.array_equal(out['pos'][nidx], geo['pos'][idx]) and np.array_equal(out['bone'][nidx], d['bone'][idx]) and np.array_equal(out['uv'][nidx], d['uv'][idx])
    assert np.array_equal(out['nrm'][nidx][..., 3], d['nrm'][idx][..., 3])                                    # かげ（AO）は そのまま
    keep = out['fx'][nidx, 3] == 0; assert np.array_equal(out['nrm'][nidx][keep], d['nrm'][idx][keep]) and np.array_equal(out['cv'][nidx][keep], d['cv'][idx][keep])      # 印 なしの 頂点は 1つも かわらない
    assert np.array_equal(nidx[pur], idx[pur]) and (out['fx'][nidx[pur].reshape(-1), 3] == 0).all() and (out['fx'][:, :3] == paper).all()
    assert (out['fx'][nidx[core].reshape(-1), 3] == 255).all() and (out['fx'][nidx[~soft].reshape(-1), 3] == 0).all()
    info = dict(webs=int(webs), core=int(core.sum()), soft=int(soft.sum()), area=round(float(a3[core].sum()), 4), added=int(len(rows)), flagged=int((out['fx'][:, 3] > 0).sum()),
                median=round(med, 1), paper=[int(v) for v in paper])
    log('  つなぎの 膜 %d か所・にじむ 三角 %d（面積 %.3f）・まわりも 入れて 印つきの 頂点を 使う 三角 %d・印つきの 頂点 %d（うち 足した 写し %d）・黒い 紙の 色 %s' % (
        info['webs'], info['core'], info['area'], info['soft'], info['flagged'], info['added'], info['paper']))
    return out, info


# ---------- 幻の馬：肩幅を 細く ----------
BODY_W = 0.62                   # 肩幅（体の 前から 3/4 の 所の 横幅：tc_horse.js の morphStance の bodyW と 同じ はかり方）：前は 0.78 → 0.62
                                #   まさちゃん 2026/11/12 20:01「赤丸の大きさにして！」（4とおりの 見本の 上から 2段目＝0.62 に 赤丸）
NECK_T = (0.05, 0.6)            # 首：つけ根から 頭への 向きに そって、つけ根（0.05）までは 体と 同じ だけ 細く・0.6 から 先（頭）は そのまま（間は なめらかに）
LEG_BLEND = 0.4                 # 足：つけ根は 体と 同じ ように 寄せて、これだけ 下からは 足ごと 内がわへ 平行に 寄せる（足は 細く しない・ひづめの 間も 同じ 割合で せまく）


def smooth(u):
    u = np.clip(u, 0, 1); return u * u * (3 - 2 * u)


def body_width(d):
    """肩幅：体の 骨の 頂点の、前から 3/4 の 所（前後 0.05）の 横幅（morphStance と 同じ）"""
    P = d['pos'].astype(np.float64); body = d['bone'] == d['names'].index('body'); x0, x1 = P[body, 0].min(), P[body, 0].max(); xs = x0 + (x1 - x0) * 0.75
    m = body & (np.abs(P[:, 0] - xs) < 0.05)
    return float(P[m, 2].max() - P[m, 2].min())


def narrow_body(d, log=print):
    """肩幅を 細く（まさちゃん 2026/11/12 19:47「幻の馬、肩幅狭くして！」・20:01「赤丸の大きさにして！」）→ (直した d, 記録)
       体の まん中の 面（z＝0）へ 向かって 横（z）だけ ちぢめる：体・しっぽ・たてがみは 同じ 割合、首は つけ根から 頭へ 向かって だんだん もとの まま、頭は そのまま。
       足 4本は つけ根が 体と いっしょに 動いて、下は 足ごと 内がわへ 寄る。骨の 回る 中心（bones の head）も いっしょに 動かす。
       アプリの morphStance（骨ごとに 動かす）で 同じ 幅に すると、骨の 境目で 動きが そろわず 胸の ふちが ギザギザに なる → ここでは 場所だけで 決まる なめらかな 動かし方に した"""
    names = d['names']; bi = {n: i for i, n in enumerate(names)}; P = d['pos'].astype(np.float64); bn = d['bone']; B = d['meta']['bones']
    w0 = body_width(d); k = BODY_W / w0; assert 0.6 < k < 1.0, (w0, k)
    nh = np.array(B[bi['neck']]['head'][:2]); hh = np.array(B[bi['head']]['head'][:2]); nL = float(np.linalg.norm(hh - nh)); ax = (hh - nh) / nL
    legs = {L: [bi[L + s_] for s_ in ('_u', '_k', '_f')] for L in LEGS}; hoof = {}; top = {}
    for L in LEGS:
        m = bn == bi[L + '_f']; my = P[m, 1].min(); hoof[L] = float(P[m & (P[:, 1] < my + 0.04), 2].mean()); top[L] = float(B[bi[L + '_u']]['head'][1])
    def field(x, y, z, b):
        """点（x, y, z・骨 b）の 横（z）の うごき"""
        x = np.asarray(x, np.float64); y = np.asarray(y, np.float64); z = np.asarray(z, np.float64); b = np.asarray(b)
        t = ((x - nh[0]) * ax[0] + (y - nh[1]) * ax[1]) / nL                       # 首の つけ根から 頭への 向きに そった 場所（0＝つけ根・1＝頭の 骨）
        dz = z * (k - 1) * (1 - smooth((t - NECK_T[0]) / (NECK_T[1] - NECK_T[0])))
        for L in LEGS:
            m = np.isin(b, legs[L]); e = smooth((top[L] - y[m]) / LEG_BLEND); dz[m] = (1 - e) * dz[m] + e * hoof[L] * (k - 1)
        return dz
    dz = field(P[:, 0], P[:, 1], P[:, 2], bn)
    # 同じ 場所の 頂点（骨の 境目・絵の 切れ目）は 同じ だけ 動かす（すきまを 作らない）
    g = weld(d['pos']); ng = int(g.max()) + 1; sm = np.zeros(ng); ct = np.zeros(ng); np.add.at(sm, g, dz); np.add.at(ct, g, 1)
    gap = np.zeros(ng); np.maximum.at(gap, g, np.abs(dz - (sm / ct)[g])); dz = (sm / ct)[g]
    out = dict(d); out['pos'] = d['pos'].copy(); out['pos'][:, 2] = (P[:, 2] + dz).astype(np.float32)
    meta = json.loads(json.dumps(d['meta'])); hb = np.array([b_['head'] for b_ in meta['bones']], np.float64)
    hd = field(hb[:, 0], hb[:, 1], hb[:, 2], np.arange(len(names)))
    for i, b_ in enumerate(meta['bones']):
        b_['head'] = [b_['head'][0], b_['head'][1], round(float(b_['head'][2] + hd[i]), 6)]
    out['meta'] = meta
    w1 = body_width(out); head = np.isin(bn, [bi['head'], bi['jaw']]); ey = np.array([e_['p'] for e_ in meta.get('eyes', [])], np.float64).reshape(-1, 3)
    eye_dz = float(np.abs(field(ey[:, 0], ey[:, 1], ey[:, 2], np.full(len(ey), bi['head']))).max()) if len(ey) else 0.0
    assert abs(w1 - BODY_W) < 0.004 and float(np.abs(dz[head]).max()) < 0.002 and eye_dz == 0.0, (w1, float(np.abs(dz[head]).max()), eye_dz)      # 頭は 動かない（首との つなぎ目が ほんの 少し だけ）・目の 場所は そのまま
    assert np.array_equal(out['pos'][:, :2], d['pos'][:, :2])                                                          # 前後・高さは かえない
    info = dict(before=round(w0, 4), after=round(w1, 4), k=round(k, 4), moved=int((np.abs(dz) > 1e-6).sum()), max=round(float(np.abs(dz).max()), 4), gap=round(float(gap.max()), 5),
                hoof={L: [round(hoof[L], 4), round(hoof[L] * k, 4)] for L in LEGS})
    log('  肩幅 %.3f → %.3f（×%.3f）・動かした 頂点 %d（いちばん 大きい 動き %.3f）・ひづめの 場所（横）%s' % (w0, w1, k, info['moved'], info['max'], info['hoof']))
    return out, info


def maboroshi(out, check=False, log=print):
    from PIL import Image
    d = load('maboroshi'); log('幻の馬：頂点 %d・三角 %d' % (len(d['pos']), len(d['idx'])))
    tex = np.array(Image.open(os.path.join(assets_dir.master('tc_assets'), d['meta']['tex'])).convert('RGB'))
    slim, inf_s = narrow_body(d, log)
    fixed, info = clean_webs(d, tex, log, shape=slim); info['shoulder'] = inf_s
    extra = dict(fix=dict(two=1, nfix=1, v='4.161', webs=info['core'], note='11/12 18:00 たてがみの 裏返しの 面・法線の 絵の こわれた 点・にじむ つなぎの 膜'),
                 slim=dict(v='4.161', w=[inf_s['before'], inf_s['after']], note='11/12 19:47 肩幅を 細く（20:01 赤丸の 大きさ）'))
    return emit(fixed, 'maboroshi2', extra, out, check), info


def main(argv):
    args = [a for a in argv if not a.startswith('--')]; check = '--check' in argv
    assert args and args[0] in ('kamisama', 'maboroshi'), __doc__
    out = args[1] if len(args) > 1 else assets_dir.master('tc_assets'); os.makedirs(out, exist_ok=True)
    res, info = (kamisama if args[0] == 'kamisama' else maboroshi)(out, check)
    for f, n, how in res:
        print('%s  %d バイト  %s' % (f, n, how))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
