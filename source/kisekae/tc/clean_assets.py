# トレーニングセンターの おそうじ（第4.152版）の 絵と 形を アプリ用に 作る：ゴミの 絵 4まい・3D の ほうき・3D の ちりとり
#   python3 kisekae/tc/clean_assets.py <作業フォルダ> [出す フォルダ（なければ <作業フォルダ>/app）]
#   作業フォルダ/src/ に まさちゃんの もと（リポジトリには 入れない）：
#     trash_apple.png・trash_carrot.png・trash_dry.png・trash_leaf.png（11/11 10:13「画像をゴミの絵として、使用して！散々に混ぜていいよ！」）
#     broom.glb・dustpan.glb（11/11 09:43「トレーニングセンターの掃除のちりとりとほうきはこの3Dのやつ使ってリアルにして！」）
#   出す もの（ios/tc_assets/ に 足す。前から ある ファイルは さわらない・消さない）：
#     tc_trash1〜4.webp（すき通りを ととのえて 余白を 切る・長い 辺 288px）
#     tc_prop_broom.json／.bin／_c.webp／_n.webp（馬・バケツと 同じ 形式 fmt2：tc_horse.js の createProp）
#     tc_prop_pan.json／.bin／_c.webp（面ごとに 1色＝折り紙の 面。法線の 絵は なし：面の 向きを 頂点に 入れる）
#   ・ほうき：fig/fig_prep.py（QEM・UV は そのまま）で 三角を へらして、毛の 先を 原点・柄を 上（+y）・毛の ひろがりを x に そろえる。長さ 1
#   ・ちりとり：絵の 島が 細かすぎて UV を 守ると へらせない（16000こ より 下に ならない）ので、UV を 守らずに へらして 面ごとに もとの 色を ぬる。
#       口（ごみを 入れる がわ）の まん中を 原点・口を +x・柄を −x・床を y＝0 に そろえる。幅 1
import json, os, subprocess, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'fig')); sys.path.insert(0, os.path.join(HERE, '..', 'r3d', 'glb'))
TRASH = ['apple', 'carrot', 'dry', 'leaf']           # 1：リンゴの 芯・2：かじった ニンジン・3：枯れ葉・4：色の 葉っぱ
TRASH_PX = 288


def trash(src, out):
    """ゴミの 絵：すき通り（中は 253 くらい・まわりに うすい 点）を ととのえる → 余白を 切る → 小さく → WebP"""
    info = []
    for i, nm in enumerate(TRASH):
        im = Image.open(os.path.join(src, f'trash_{nm}.png')).convert('RGBA'); a = np.asarray(im, np.float32)
        al = np.clip((a[..., 3] - 6) * (255 / 244), 0, 255)                 # 中を ぴったり 255 に・うすい 点（1〜6）は 消す
        ys, xs = np.nonzero(al > 8); x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        rgb = a[y0:y1, x0:x1, :3]; al = al[y0:y1, x0:x1]
        pm = np.dstack([rgb * al[..., None] / 255, al])                     # すき通りを かけて から 小さく する（ふちに 外の 色が まざらない）
        k = TRASH_PX / max(pm.shape[:2]); w, h = max(1, round(pm.shape[1] * k)), max(1, round(pm.shape[0] * k))
        ch = [np.asarray(Image.fromarray(pm[..., c]).resize((w, h), Image.LANCZOS), np.float32) for c in range(4)]
        al2 = np.clip(ch[3], 0, 255); rgb2 = np.dstack(ch[:3]) / np.maximum(al2[..., None] / 255, 1e-3)
        o = np.dstack([np.clip(rgb2, 0, 255), al2]).round().astype(np.uint8)
        p = os.path.join(out, f'tc_trash{i + 1}.webp'); Image.fromarray(o, 'RGBA').save(p, 'WEBP', quality=92, alpha_quality=100, method=6)
        info.append((os.path.basename(p), w, h, os.path.getsize(p)))
    return info


def pack(out, name, V, N, UV, T, tex, ntex):
    """fmt2 の 形（pos f32×3・nrm i8×4（w＝影の なじみ：ここでは 1）・uv u16×2・bone・bone2・bw・idx u16）。区切りは 4バイトに そろえる"""
    nv, ni = len(V), T.size; assert nv < 65536 and T.max() < nv
    parts, lay = [], {}

    def add(key, arr):
        off = sum(len(p) for p in parts); pad = (-off) % 4
        if pad: parts.append(b'\0' * pad); off += pad
        b = arr.tobytes(); lay[key] = [off, len(b)]; parts.append(b)
    Nn = N / np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-9)
    add('pos', V.astype('<f4')); add('nrm', np.concatenate([np.clip(np.round(Nn * 127), -127, 127), np.full((nv, 1), 127)], 1).astype(np.int8))
    add('uv', np.clip(np.round(UV * 65535), 0, 65535).astype('<u2')); add('bone', np.zeros(nv, np.uint8)); add('bone2', np.zeros(nv, np.uint8)); add('bw', np.zeros(nv, np.uint8))
    add('idx', T.astype('<u2').ravel())
    bin_ = b''.join(parts); open(os.path.join(out, name + '.bin'), 'wb').write(bin_)
    meta = {'v': nv, 'i': int(ni), 'idx32': False, 'bones': [{'name': 'body', 'parent': -1, 'head': [0, 0, 0]}], 'layout': lay, 'tex': tex, 'fmt': 2, 'height': 1.0, 'ao': 0}
    if ntex: meta['ntex'] = ntex
    json.dump(meta, open(os.path.join(out, name + '.json'), 'w'), indent=1)
    return nv, ni // 3, len(bin_)


def smooth_normals(V, T):
    """同じ 場所の 頂点（絵の 継ぎ目で 分かれた もの）を まとめた なめらかな 法線"""
    fn = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])          # 面の 向き × 面積
    P, pid = np.unique(np.round(V.astype(np.float64), 5), axis=0, return_inverse=True); pid = pid.ravel()
    acc = np.zeros((len(P), 3)); [np.add.at(acc, pid[T[:, j]], fn) for j in range(3)]
    return acc[pid]


def cluster(V, F, cell):
    """ます目に まとめて へらす（QEM は この 形で 9000こ より 下に ならない）：ますの 中の 頂点を 1つに（置く 場所＝まわりの 面から いちばん ずれない 点）。
    うすい かべの 表と 裏が 同じ 三角に なったら 1まいに する（両面を 描く ので 見え方は 同じ）"""
    lo = V.min(0); ijk = np.floor((V - lo) / cell).astype(np.int64); key = ijk[:, 0] + ijk[:, 1] * 4096 + ijk[:, 2] * 4096 * 4096
    uq, cid = np.unique(key, return_inverse=True); cid = cid.ravel(); nc = len(uq)
    fn = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]]); ar = np.linalg.norm(fn, axis=1); n = fn / np.maximum(ar[:, None], 1e-300); d = -(n * V[F[:, 0]]).sum(1)
    A = np.zeros((nc, 3, 3)); b = np.zeros((nc, 3)); w = np.zeros(nc); mean = np.zeros((nc, 3))
    for j in range(3):
        c = cid[F[:, j]]; np.add.at(A, c, ar[:, None, None] * n[:, :, None] * n[:, None, :]); np.add.at(b, c, (ar * d)[:, None] * n)
    np.add.at(mean, cid, V); np.add.at(w, cid, 1); mean /= w[:, None]
    lam = 1e-2 * np.trace(A, axis1=1, axis2=2) / 3 + 1e-12
    X = np.linalg.solve(A + lam[:, None, None] * np.eye(3), (-b + lam[:, None] * mean)[:, :, None])[:, :, 0]
    X = np.clip(X, mean - cell, mean + cell)
    F2 = cid[F]; F2 = F2[(F2[:, 0] != F2[:, 1]) & (F2[:, 1] != F2[:, 2]) & (F2[:, 0] != F2[:, 2])]
    _, first = np.unique(np.sort(F2, 1), axis=0, return_index=True); F2 = F2[np.sort(first)]
    used = np.unique(F2); remap = -np.ones(nc, np.int64); remap[used] = np.arange(len(used))
    return X[used], remap[F2]


def broom(src, out, work, tris=7000, cs=512, ns=512):
    """ほうき：fig_prep.py で へらす（UV は そのまま）→ 向きを そろえる → 形と 絵"""
    pre = os.path.join(work, 'broom')
    if not os.path.exists(pre + '.npz') or os.environ.get('CLEAN_REDO'):
        subprocess.run([sys.executable, os.path.join(HERE, '..', 'fig', 'fig_prep.py'), os.path.join(src, 'broom.glb'), pre, str(tris), '1024', '512', '256'], check=True, env=dict(os.environ, FIG_UVTOL='8'))
    d = np.load(pre + '.npz'); V0, T0, UVc = d['V'].astype(np.float64), d['T'], d['UVc']
    # 柄の 向き：形の いちばん 長い 向き（x–y の 中）。毛の がわ＝その 向きに 直角の ひろがりが 大きい はし
    c = V0.mean(0); u, s, vt = np.linalg.svd((V0 - c)[:, :2], full_matrices=False); ax = np.array([vt[0, 0], vt[0, 1], 0.0])
    t = (V0 - c) @ ax; side = np.array([-ax[1], ax[0], 0.0]); w = np.abs((V0 - c) @ side)
    if w[t > np.percentile(t, 80)].mean() > w[t < np.percentile(t, 20)].mean(): ax = -ax; side = -side          # 毛が + がわに あったら 逆に（柄を + に）
    R = np.stack([side, ax, np.cross(side, ax)])                              # 行＝新しい x・y・z（柄 → +y・毛の ひろがり → x・うすい 向き → z）
    V = (V0 - c) @ R.T
    # 毛の 先の ふち（ななめに 切って ある）を 水平に：下の ふちの 点（x の ますごとの いちばん 下）に 線を 合わせて、その かたむきの ぶん z の まわりに 回す → 柄は ななめに なる（はく ときの 持ち方）
    L = np.ptp(V[:, 1]); low = V[V[:, 1] < V[:, 1].min() + 0.3 * L]; xb = np.linspace(low[:, 0].min(), low[:, 0].max(), 15); ex, ey = [], []
    for i in range(14):
        q = low[(low[:, 0] >= xb[i]) & (low[:, 0] <= xb[i + 1])]
        if len(q): ex.append((xb[i] + xb[i + 1]) / 2); ey.append(q[:, 1].min())
    th = np.arctan(np.polyfit(ex[2:-2], ey[2:-2], 1)[0]); cz, sz = np.cos(-th), np.sin(-th)
    R2 = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1.0]]); R = R2 @ R; V = (V0 - c) @ R.T
    tip = V[:, 1] < V[:, 1].min() + 0.02 * L; org = np.array([(V[tip, 0].min() + V[tip, 0].max()) / 2, V[:, 1].min(), V[tip, 2].mean()])
    k = 1.0 / np.ptp(V[:, 1]); V = (V - org) * k
    # 頂点：（もとの 頂点・UV）の 組ごとに 1つ
    key = np.concatenate([T0.reshape(-1, 1).astype(np.int64), np.round(UVc.reshape(-1, 2) * 65535).astype(np.int64)], 1)
    uq, inv = np.unique(key, axis=0, return_inverse=True); inv = inv.ravel()
    Vn = V[uq[:, 0]]; UV = uq[:, 1:].astype(np.float64) / 65535; T = inv.reshape(-1, 3).astype(np.int64)
    N = smooth_normals(Vn, T)
    col = Image.open(pre + '_c.webp').convert('RGB').resize((cs, cs), Image.LANCZOS)
    nm = np.asarray(Image.open(pre + '_n.webp').convert('RGB'), np.float64) / 255 * 2 - 1
    nm = nm @ R.T; nm /= np.maximum(np.linalg.norm(nm, axis=2, keepdims=True), 1e-9)          # 法線の 絵も 同じ 向きに 回す
    nim = Image.fromarray(np.round((nm * 0.5 + 0.5) * 255).astype(np.uint8)).resize((ns, ns), Image.BILINEAR)
    col.save(os.path.join(out, 'tc_prop_broom_c.webp'), 'WEBP', quality=90, method=6); nim.save(os.path.join(out, 'tc_prop_broom_n.webp'), 'WEBP', quality=92, method=6)
    r = pack(out, 'tc_prop_broom', Vn, N, UV, T, 'tc_prop_broom_c.webp', 'tc_prop_broom_n.webp')
    top = V[V[:, 1] > 0.97]; return r + (V.min(0).round(3).tolist(), V.max(0).round(3).tolist(), '柄の 先', top.mean(0).round(3).tolist(), 'かたむき %.1f°' % np.degrees(th))


def pan(src, out, cell=0.022, name='tc_prop_pan', qem=1600):
    """ちりとり：ます目に まとめて へらす（UV は 守らない）→ 面ごとに もとの 色（いちばん 近い もとの 三角の 色）→ 面ごとに 2×2点の 絵"""
    import glb
    from scipy.spatial import cKDTree
    m = glb.load(os.path.join(src, 'dustpan.glb')); prims = m.flatten(); assert len(prims) == 1
    p = prims[0]; V0 = p.pos.astype(np.float64); F0 = np.asarray(p.idx, np.int64).reshape(-1, 3); UV0 = np.asarray(p.uv, np.float64)
    img = p.mat.base_tex.tex.img[..., :3] * np.asarray(p.mat.base_color[:3]); H, W = img.shape[:2]
    # 床の 裏（下を 向いた いちばん 下の 面）は 見えない ので 先に とる：ます目に まとめる とき、床の 表（クリーム色）と 裏（緑）が まざって まだらに ならない
    fn0 = np.cross(V0[F0[:, 1]] - V0[F0[:, 0]], V0[F0[:, 2]] - V0[F0[:, 0]]); fn0 /= np.maximum(np.linalg.norm(fn0, axis=1, keepdims=True), 1e-300)
    cy = V0[F0][:, :, 1].mean(1); ylo, yh = V0[:, 1].min(), np.ptp(V0[:, 1]); keep = ~((fn0[:, 1] < -0.3) & (cy < ylo + 0.08 * yh)); F0k = F0[keep]
    P, F2 = cluster(V0, F0k, cell)
    if qem and len(F2) > qem:                                                 # まとめた あとで QEM でも へらす（平らな 面の 三角を 大きく）
        import fig_prep
        e = np.sort(np.concatenate([F2[:, [0, 1]], F2[:, [1, 2]], F2[:, [2, 0]]]), 1); ue, cnt = np.unique(e, axis=0, return_counts=True)
        lock = np.zeros(len(P), np.uint8); lock[np.unique(ue[cnt != 2])] = 1          # ふち・重なった 所の 頂点は 動かさない（穴が あかない）
        Lq = fig_prep.lib(); P = np.ascontiguousarray(P, np.float64)
        for _ in range(6):
            n0 = len(F2); F2 = fig_prep.decimate(Lq, P, np.ascontiguousarray(F2, np.int32), lock, qem, 0.5).astype(np.int64)
            if len(F2) <= qem or len(F2) >= n0: break
    # もとの 三角の まん中の 色（UV の まん中で 絵を 読む）
    uvc = UV0[F0].mean(1); c0 = img[np.clip((uvc[:, 1] * H).astype(int), 0, H - 1), np.clip((uvc[:, 0] * W).astype(int), 0, W - 1)]
    c0 = c0[keep]; tree = cKDTree(V0[F0k].mean(1))
    A, B, C = P[F2[:, 0]], P[F2[:, 1]], P[F2[:, 2]]
    ws = [(1 / 3, 1 / 3, 1 / 3), (0.6, 0.2, 0.2), (0.2, 0.6, 0.2), (0.2, 0.2, 0.6), (0.44, 0.44, 0.12), (0.44, 0.12, 0.44), (0.12, 0.44, 0.44)]
    cols = np.stack([c0[tree.query(A * a + B * b + C * c_)[1]] for a, b, c_ in ws], 1)          # 面の 中の 7点
    colf = np.median(cols, 1)                                                 # まん中の 値（となりの 色が 少し まざっても かわらない）
    # 向き：口（+z）→ +x・柄（−z）→ −x・床を y＝0・口の はしの まん中を 原点・幅 1
    Rm = np.array([[0, 0, 1.0], [0, 1.0, 0], [-1.0, 0, 0]])                   # (x, y, z) → (z, y, −x)
    Q = P @ Rm.T; lo, hi = Q.min(0), Q.max(0)
    front = Q[:, 0] > hi[0] - 0.02 * (hi[0] - lo[0]); org = np.array([hi[0], lo[1], Q[front, 2].mean()]); k = 1.0 / (hi[2] - lo[2])
    Q = (Q - org) * k
    n = len(F2); side = int(np.ceil(np.sqrt(n))); S = 1
    while S < side * 2: S *= 2
    tex = np.zeros((S, S, 3), np.float32); UV = np.zeros((n, 2))
    for i in range(n):
        bx, by = (i % side) * 2, (i // side) * 2; tex[by:by + 2, bx:bx + 2] = colf[i]; UV[i] = ((bx + 1) / S, (by + 1) / S)          # 3つの 角とも 同じ 点（面は 1色）
    Vn = Q[F2].reshape(-1, 3); T = np.arange(n * 3).reshape(-1, 3); fn = np.cross(Vn[1::3] - Vn[0::3], Vn[2::3] - Vn[0::3]); N = np.repeat(fn, 3, 0)
    Image.fromarray(np.round(np.clip(tex, 0, 1) * 255).astype(np.uint8)).save(os.path.join(out, name + '_c.webp'), 'WEBP', lossless=True, quality=100, method=6, exact=True)
    r = pack(out, name, Vn, N, np.repeat(UV, 3, 0), T, name + '_c.webp', None)
    return r + (Q.min(0).round(3).tolist(), Q.max(0).round(3).tolist(), S)


def main():
    work = os.path.abspath(sys.argv[1]); src = os.path.join(work, 'src'); out = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.join(work, 'app')
    os.makedirs(out, exist_ok=True); os.makedirs(os.path.join(work, 'out'), exist_ok=True)
    for r in trash(src, out): print('ゴミの 絵', r)
    print('ほうき（頂点・三角・bin・箱）', broom(src, out, os.path.join(work, 'out')))
    print('ちりとり（頂点・三角・bin・箱・絵）', pan(src, out))
    tot = sum(os.path.getsize(os.path.join(out, f)) for f in os.listdir(out) if f.startswith(('tc_trash', 'tc_prop_broom', 'tc_prop_pan')))
    print('ぜんぶで %.0fKB' % (tot / 1000), sorted(f for f in os.listdir(out)))


if __name__ == '__main__':
    main()
