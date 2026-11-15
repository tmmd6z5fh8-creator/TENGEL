# 40000P の 3D：「4」の まん中の くぼみの 底（平らな 三角）を 頂点から じかに 測る（くりぬく 形を 決める ため）
#   python3 -I kisekae/tc/geki_cut_measure.py <GLB>      （測る だけ：何も 書かない。くりぬくのは geki_cut.py）
import sys, json, struct
import numpy as np
b = open(sys.argv[1], 'rb').read()
jl = struct.unpack('<I', b[12:16])[0]; js = json.loads(b[20:20 + jl]); binb = b[20 + jl + 8:]
bvs = js['bufferViews']; acc = js['accessors']; pr = js['meshes'][0]['primitives'][0]
def get(i, dt, nc):
    a = acc[i]; v = bvs[a['bufferView']]; off = v.get('byteOffset', 0) + a.get('byteOffset', 0)
    return np.frombuffer(binb, dt, a['count'] * nc, off).reshape(a['count'], nc).copy() if nc > 1 else np.frombuffer(binb, dt, a['count'], off).copy()
pos = get(pr['attributes']['POSITION'], '<f4', 3).astype(np.float64); idx = get(pr['indices'], '<u4', 1).reshape(-1, 3)
TF = np.array([[-0.7701, -0.0106], [-0.7430, -0.0119], [-0.7372, 0.0281]]); ZF = 0.0228
TB = np.array([[-0.7692, -0.0103], [-0.7446, -0.0126], [-0.7394, 0.0248]]); ZB = -0.0243
def sd(T, p):                          # 三角の 中なら ＋（いちばん 近い 辺までの 距離）、外なら −
    c = T.mean(0); out = np.full(len(p), 1e9)
    for k in range(3):
        a, b_ = T[k], T[(k + 1) % 3]; e = b_ - a; n = np.array([-e[1], e[0]]); n /= np.linalg.norm(n)
        if np.dot(c - a, n) < 0: n = -n
        out = np.minimum(out, (p - a) @ n)
    return out
near = (np.abs(pos[:, 0] + 0.752) < 0.05) & (np.abs(pos[:, 1] - 0.003) < 0.05)
for nm, T, Z, sg in (('前', TF, ZF, 1), ('後ろ', TB, ZB, -1)):
    m = near & (pos[:, 2] * sg > 0); p = pos[m]; d = sd(T, p[:, :2]); h = (p[:, 2] - Z) * sg     # h：底から 外がわへの 高さ
    print(nm, '近くの 頂点', int(m.sum()))
    for lo, hi in ((0.004, 9), (0.002, 0.004), (0.001, 0.002), (0.0005, 0.001), (0, 0.0005), (-0.0005, 0), (-0.001, -0.0005), (-0.002, -0.001), (-0.004, -0.002), (-0.008, -0.004)):
        q = (d >= lo) & (d < hi)
        if q.sum(): print('   ふちからの 距離 %+.4f〜%+.4f：%4d点  高さ 最小 %+.4f 中央 %+.4f 最大 %+.4f' % (lo, hi if hi < 9 else 0.02, int(q.sum()), h[q].min(), np.median(h[q]), h[q].max()))
    # 辺ごとに：高さが 0.0015 を こえる いちばん 内がわの 点（＝ 斜面の はじまり）
    c = T.mean(0)
    for k in range(3):
        a, b_ = T[k], T[(k + 1) % 3]; e = b_ - a; L = np.linalg.norm(e); n = np.array([-e[1], e[0]]) / L
        if np.dot(c - a, n) < 0: n = -n
        t = (p[:, :2] - a) @ e / L / L; dd = (p[:, :2] - a) @ n; q = (t > 0.15) & (t < 0.85) & (h > 0.0015) & (dd > -0.006)
        q2 = (t > 0.15) & (t < 0.85) & (np.abs(h) <= 0.0012) & (dd < 0.02)
        print('   辺', k, '斜面の いちばん 内がわ（ふちからの 距離）', round(float(dd[q].max()), 5) if q.sum() else None, '平らな 点の いちばん 外がわ', round(float(dd[q2].min()), 5) if q2.sum() else None)
