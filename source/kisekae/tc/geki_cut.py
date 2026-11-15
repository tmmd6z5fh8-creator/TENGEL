# 40000P の 3D：「4」の まん中の 三角（くぼみの 底）だけを くりぬく（まさちゃん 2026/11/15 14:11「4の3Dの赤線の中だけくり抜いて！」）
#   python3 -I kisekae/tc/geki_cut.py <もとの GLB> <出す GLB>      （もとの ファイルは 書きかえない・出す 先が もう あれば 止まる）
#   できた 3D（くりぬいた もの）は kisekae/tc/geki_film.py が 天国の 動画を 作る ときに 使う。まさちゃんの 3D と できた 3D は リポジトリに 入れない
#   ・前の くぼみの 底（z≈+0.0228）と 後ろの くぼみの 底（z≈−0.0243）を、三角の 線で ぴったり 切り取る（線を またぐ 面は 線で 切る）
#   ・前の 穴の ふち と 後ろの 穴の ふちを つなぐ かべ（金色）を 足す ＝ 向こうが 見える 穴
#   ・絵（色・つや・でこぼこの 3まい）と ほかの 所の 形は そのまま
import sys, os, io, json, struct
import numpy as np
SRC, OUT = sys.argv[1], sys.argv[2]
assert not os.path.exists(OUT), 'すでに ある：' + OUT
b = open(SRC, 'rb').read()
magic, ver, total = struct.unpack('<4sII', b[:12]); assert magic == b'glTF' and total == len(b)
jl = struct.unpack('<I', b[12:16])[0]; js = json.loads(b[20:20 + jl]); binb = b[20 + jl + 8:]
bvs = js['bufferViews']; acc = js['accessors']; pr = js['meshes'][0]['primitives'][0]
assert len(js['meshes']) == 1 and len(js['meshes'][0]['primitives']) == 1 and len(bvs) == 7
def get(i, dt, nc):
    a = acc[i]; v = bvs[a['bufferView']]; off = v.get('byteOffset', 0) + a.get('byteOffset', 0)
    return np.frombuffer(binb, dt, a['count'] * nc, off).reshape(a['count'], nc).copy() if nc > 1 else np.frombuffer(binb, dt, a['count'], off).copy()
iP, iU, iN, iI = pr['attributes']['POSITION'], pr['attributes']['TEXCOORD_0'], pr['attributes']['NORMAL'], pr['indices']
assert set(pr['attributes']) == {'POSITION', 'TEXCOORD_0', 'NORMAL'}
pos, uv, nrm = get(iP, '<f4', 3).astype(np.float64), get(iU, '<f4', 2).astype(np.float64), get(iN, '<f4', 3).astype(np.float64)
idx = get(iI, '<u4', 1).reshape(-1, 3).astype(np.int64)
print('もと：頂点', len(pos), '面', len(idx))
# くりぬく 三角（geki_cut_measure.py で 頂点から 確かめた 底の 三角。ふちから 0.0004 だけ 内がわ）
TF = np.array([[-0.7701, -0.0106], [-0.7430, -0.0119], [-0.7372, 0.0281]]); ZF = 0.0228
TB = np.array([[-0.7692, -0.0103], [-0.7446, -0.0126], [-0.7394, 0.0248]]); ZB = -0.0243
SHRINK = 0.0004
def inset(T, d):                       # 三角の 3辺を 内がわへ d だけ ずらす
    c = T.mean(0); L = []
    for k in range(3):
        a, b_ = T[k], T[(k + 1) % 3]; e = b_ - a; n = np.array([-e[1], e[0]]); n /= np.linalg.norm(n)
        if np.dot(c - a, n) < 0: n = -n
        L.append((a + n * d, e, n))
    out = []
    for k in range(3):                 # 角 k ＝ 辺 k-1 と 辺 k の 交わり
        (a1, e1, _), (a2, e2, _) = L[(k - 1) % 3], L[k]
        M = np.array([[e1[0], -e2[0]], [e1[1], -e2[1]]]); s = np.linalg.solve(M, a2 - a1); out.append(a1 + e1 * s[0])
    return np.array(out)
HF, HB = inset(TF, SHRINK), inset(TB, SHRINK)
def edges(H):
    c = H.mean(0); E = []
    for k in range(3):
        a, b_ = H[k], H[(k + 1) % 3]; e = b_ - a; n = np.array([-e[1], e[0]]); n /= np.linalg.norm(n)
        if np.dot(c - a, n) < 0: n = -n
        E.append((a, b_, n))
    return E
P, U, N = [p for p in pos], [u for u in uv], [n for n in nrm]      # 足して いく 頂点の 表
def mix(i, j, t):
    P.append(P[i] * (1 - t) + P[j] * t); U.append(U[i] * (1 - t) + U[j] * t)
    n = N[i] * (1 - t) + N[j] * t; N.append(n / max(np.linalg.norm(n), 1e-12)); return len(P) - 1
def split(poly, a, n):                 # 凸の 多角形（頂点番号の 並び）を 線で 2つに：内がわ（(p-a)·n ≥ 0）と 外がわ
    ins, outs = [], []; m = len(poly); d = [float(np.dot(P[i][:2] - a, n)) for i in poly]
    for i in range(m):
        p, q, dp, dq = poly[i], poly[(i + 1) % m], d[i], d[(i + 1) % m]
        if dp >= 0: ins.append(p)
        if dp <= 0: outs.append(p)
        if (dp > 0 and dq < 0) or (dp < 0 and dq > 0):
            x = mix(p, q, dp / (dp - dq)); ins.append(x); outs.append(x)
    return ins, outs
def area(poly):
    if len(poly) < 3: return 0.0
    q = np.array([P[i][:2] for i in poly]); x, y = q[:, 0], q[:, 1]; return abs(float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))) / 2
keep = np.ones(len(idx), bool); newtri = []; stat = {}
cen = pos[idx].mean(1)
for nm, H, Z, sg in (('前', HF, ZF, 1), ('後ろ', HB, ZB, -1)):
    E = edges(H); lo, hi = H.min(0) - 1e-6, H.max(0) + 1e-6
    tp = pos[idx]; bb = (tp[:, :, 0].max(1) >= lo[0]) & (tp[:, :, 0].min(1) <= hi[0]) & (tp[:, :, 1].max(1) >= lo[1]) & (tp[:, :, 1].min(1) <= hi[1]) & (cen[:, 2] * sg > 0)
    n0 = len(P); cut = whole = 0; zs = []
    for f in np.nonzero(bb)[0]:
        rest = [int(v) for v in idx[f]]; pieces = []; np0 = len(P)
        for a, b_, n in E:
            rest, outs = split(rest, a, n)
            if area(outs) > 1e-14: pieces.append(outs)
            if len(rest) < 3: break
        if area(rest) <= 1e-14:        # 三角と 重ならない 面 ＝ そのまま（足した 点は 捨てる）
            del P[np0:], U[np0:], N[np0:]; continue
        zs += [float(P[i][2]) for i in rest]
        keep[f] = False; cut += 1
        if not pieces: whole += 1
        for pl in pieces:
            for k in range(1, len(pl) - 1):
                if area([pl[0], pl[k], pl[k + 1]]) > 1e-16: newtri.append([pl[0], pl[k], pl[k + 1]])
    zs = np.array(zs)
    print(nm, '：三角に かかる 面', cut, '（まるごと 中', whole, '）足した 点', len(P) - n0, ' 穴の 中の 面の z', round(float(zs.min()), 4), '〜', round(float(zs.max()), 4))
    assert cut > 20 and np.all(np.abs(zs - Z) < 0.004), '底では ない 面が 三角の 中に ある'
    # 穴の ふちの 点（辺 ごとに、角 k から 角 k+1 へ 並べる）
    lst = []
    for a, b_, n in E:
        e = b_ - a; L2 = float(np.dot(e, e)); pts = []
        for i in range(n0, len(P)):
            d = float(np.dot(P[i][:2] - a, n)); t = float(np.dot(P[i][:2] - a, e)) / L2
            if abs(d) < 1e-9 and -1e-7 <= t <= 1 + 1e-7: pts.append((min(1.0, max(0.0, t)), i))
        pts.sort(); un = []
        for t, i in pts:
            if not un or t - un[-1][0] > 1e-7: un.append((t, i))
        assert un[0][0] < 1e-6 and un[-1][0] > 1 - 1e-6, ('角の 点が ない', nm, un[0][0], un[-1][0])
        lst.append(un)
    stat[nm] = lst; print('   ふちの 点（辺 ごと）', [len(u) for u in lst])
# かべ：前の ふち と 後ろの ふちを ジグザグに つなぐ。法線は 穴の まん中 向き。色は くぼみの 斜面の 金色
from PIL import Image
mat = js['materials'][pr['material']]; pbr = mat['pbrMetallicRoughness']
def tex_img(ti):
    v = bvs[js['images'][js['textures'][ti]['source']]['bufferView']]; return Image.open(io.BytesIO(binb[v['byteOffset']:v['byteOffset'] + v['byteLength']])).convert('RGB')
base = np.asarray(tex_img(pbr['baseColorTexture']['index']), np.float64); th, tw = base.shape[:2]
mrt = np.asarray(tex_img(pbr['metallicRoughnessTexture']['index']), np.float64)
def at(img, u): return img[np.clip((u[:, 1] % 1 * th).astype(int), 0, th - 1), np.clip((u[:, 0] % 1 * tw).astype(int), 0, tw - 1)]
# 「4」の 外がわの 金の わく（いちばん 手前の 面）の ふつうの 色・つやの 点を 1つ えらぶ（かべは その 色 1色）
ring = np.nonzero((np.abs(pos[:, 0] + 0.752) < 0.12) & (pos[:, 2] > 0.045))[0]; cb, cm = at(base, uv[ring]), at(mrt, uv[ring])
g = (cb[:, 0] > 120) & (cb[:, 1] > 90) & (cb[:, 2] < 80); ring, cb, cm = ring[g], cb[g], cm[g]
feat = np.concatenate([cb, cm[:, 1:]], 1); med = np.median(feat, 0); pick = ring[int(np.argmin(((feat - med) ** 2).sum(1)))]; guv = uv[pick]
print('かべの 色：金の わくの 点', len(ring), '中央（色 RGB・あらさ・金属）', med.round(0), 'えらんだ 点', np.concatenate([at(base, guv[None])[0], at(mrt, guv[None])[0][1:]]).round(0), 'UV', guv.round(4))
nw0 = len(P); wall = []
EF = edges(HF)
for k in range(3):
    F, B = stat['前'][k], stat['後ろ'][k]; nin = np.array([EF[k][2][0], EF[k][2][1], 0.0])
    def wv(i): P.append(P[i].copy()); U.append(guv.copy()); N.append(nin.copy()); return len(P) - 1
    fi = [wv(i) for _, i in F]; bi = [wv(i) for _, i in B]; i = j = 0
    while i < len(F) - 1 or j < len(B) - 1:
        if i < len(F) - 1 and (j == len(B) - 1 or F[i + 1][0] <= B[j + 1][0]): t3 = [fi[i], fi[i + 1], bi[j]]; i += 1
        else: t3 = [fi[i], bi[j + 1], bi[j]]; j += 1
        g = np.cross(P[t3[1]] - P[t3[0]], P[t3[2]] - P[t3[0]])
        if np.dot(g, nin) < 0: t3 = [t3[0], t3[2], t3[1]]
        wall.append(t3)
print('かべ：頂点', len(P) - nw0, '面', len(wall))
pos2, uv2, nrm2 = np.array(P, '<f4'), np.array(U, '<f4'), np.array(N, '<f4')
idx2 = np.concatenate([idx[keep], np.array(newtri, np.int64), np.array(wall, np.int64)]).astype('<u4')
used = np.zeros(len(pos2), bool); used[idx2.ravel()] = True                      # 使わなく なった 頂点を はずす
remap = np.cumsum(used) - 1; pos2, uv2, nrm2 = pos2[used], uv2[used], nrm2[used]; idx2 = remap[idx2].astype('<u4')
print('あたらしい 3D：頂点', len(pos2), '面', len(idx2), '（もとから 消した 面', int((~keep).sum()), '・切って 残した 面', len(newtri), '・かべ', len(wall), '）')
vI, vP, vU, vN = acc[iI]['bufferView'], acc[iP]['bufferView'], acc[iU]['bufferView'], acc[iN]['bufferView']
data = {vI: idx2.tobytes(), vP: pos2.tobytes(), vU: uv2.tobytes(), vN: nrm2.tobytes()}
blob = b''
for i in range(len(bvs)):
    d = data.get(i); d = d if d is not None else bytes(binb[bvs[i]['byteOffset']:bvs[i]['byteOffset'] + bvs[i]['byteLength']])
    blob += b'\x00' * ((4 - len(blob) % 4) % 4); bvs[i]['byteOffset'] = len(blob); bvs[i]['byteLength'] = len(d); blob += d
for i in (iI, iP, iU, iN): acc[i]['byteOffset'] = 0
acc[iI]['count'] = int(idx2.size); acc[iP]['count'] = acc[iU]['count'] = acc[iN]['count'] = int(len(pos2))
for i, a in ((iP, pos2), (iU, uv2), (iN, nrm2)):
    if 'min' in acc[i]: acc[i]['min'] = [float(x) for x in a.min(0)]; acc[i]['max'] = [float(x) for x in a.max(0)]
if 'min' in acc[iI]: acc[iI]['min'] = [int(idx2.min())]; acc[iI]['max'] = [int(idx2.max())]
js['buffers'][0]['byteLength'] = len(blob)
j = json.dumps(js, separators=(',', ':')).encode(); j += b' ' * ((4 - len(j) % 4) % 4); blob += b'\x00' * ((4 - len(blob) % 4) % 4)
tot = 12 + 8 + len(j) + 8 + len(blob)
with open(OUT, 'wb') as f:
    f.write(struct.pack('<4sII', b'glTF', 2, tot)); f.write(struct.pack('<I4s', len(j), b'JSON')); f.write(j); f.write(struct.pack('<I4s', len(blob), b'BIN\x00')); f.write(blob)
print('書いた', OUT, tot, 'B')
