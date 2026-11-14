# 直した GLB を 元と くらべて 確かめる：<新しい GLB>
import sys, io
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from common import *
from PIL import Image
new = sys.argv[1]
ok = True


def chk(name, cond, extra=''):
    global ok
    ok &= bool(cond)
    print(('OK  ' if cond else 'NG  ') + name + (' … ' + str(extra) if extra != '' else ''))


b = open(new, 'rb').read()
magic, ver, total = struct.unpack('<4sII', b[:12])
chk('GLB の 頭（glTF・2・長さ）', magic == b'glTF' and ver == 2 and total == len(b), (ver, total, len(b)))
ln, ty = struct.unpack('<I4s', b[12:20])
chk('JSON の かたまり（4の 倍数）', ty == b'JSON' and ln % 4 == 0, ln)
ln2, ty2 = struct.unpack('<I4s', b[20 + ln:28 + ln])
chk('BIN の かたまり（4の 倍数・ファイルの 終わりまで）', ty2 == b'BIN\x00' and ln2 % 4 == 0 and 28 + ln + ln2 == len(b), ln2)
js0, bin0 = read_glb(ORIG)
js1, bin1 = read_glb(new)
chk('バッファの 長さ', js1['buffers'][0]['byteLength'] == len(bin1), (js1['buffers'][0]['byteLength'], len(bin1)))
end = 0; good = True
for v in js1['bufferViews']:
    good &= v['byteOffset'] % 4 == 0 and v['byteOffset'] >= end and v['byteOffset'] + v['byteLength'] <= len(bin1)
    end = v['byteOffset'] + v['byteLength']
chk('bufferView：4の 倍数・重ならない・はみ出さない', good)
p0, u0, n0, i0 = arrays(js0, bin0)
p1, u1, n1, i1 = arrays(js1, bin1)
chk('三角・絵の 場所（UV）は 1ビットも 変わらない', i0.tobytes() == i1.tobytes() and u0.tobytes() == u1.tobytes(), (i1.shape, u1.shape))
mv = (p0 != p1).any(1)
chk('動いた 頂点は 釘 だけ（x・y は そのまま・z は 前へ）', mv.sum() > 10000 and (p0[mv, :2] == p1[mv, :2]).all() and (p1[mv, 2] > p0[mv, 2]).all(), int(mv.sum()))
bx = (np.abs(p0[mv, 0]) < 0.42) & (p0[mv, 1] > -0.15) & (p0[mv, 1] < 0.30)
chk('動いた 頂点は ぜんぶ 盤の 中', bx.all(), (float(p0[mv, 0].min()), float(p0[mv, 0].max()), float(p0[mv, 1].min()), float(p0[mv, 1].max())))
dz = p1[mv, 2] - p0[mv, 2]
print('    前へ 出た 分：最大', float(dz.max()), '釘の 先（z）：元', float(p0[mv, 2].max()), '→ 新', float(p1[mv, 2].max()), ' コップの 前（z の 最大）', float(p1[:, 2].max()))
nm = (n0 != n1).any(1)
chk('面の 向きが 変わった 頂点＝動いた 頂点の 中 だけ', (nm & ~mv).sum() == 0, (int(nm.sum()), int((nm & ~mv).sum())))
ln_ = np.linalg.norm(n1.astype(np.float64), axis=1)
chk('面の 向きの 長さ＝1', np.abs(ln_ - 1).max() < 1e-4, float(np.abs(ln_ - 1).max()))
a = js1['accessors'][js1['meshes'][0]['primitives'][0]['attributes']['POSITION']]
chk('POSITION の min・max', np.allclose(a['min'], p1.min(0)) and np.allclose(a['max'], p1.max(0)), (a['min'], a['max']))
# 三角が 裏返って いない（動いた 頂点を ふくむ 三角）
tm = mv[i1].any(1)
t = i1[tm]


def fn(p):
    q = p.astype(np.float64)
    return np.cross(q[t[:, 1]] - q[t[:, 0]], q[t[:, 2]] - q[t[:, 0]])


f0, f1 = fn(p0), fn(p1)
flip = (f0 * f1).sum(1) <= 0
a0, a1 = np.linalg.norm(f0, axis=1), np.linalg.norm(f1, axis=1)
chk('裏返った 三角・つぶれた 三角は ない', flip.sum() == 0 and (a1[a0 > 1e-12] > 0).all(), (int(tm.sum()), int(flip.sum())))
# 頂点の 向きと 新しい 面の 向きの ずれ（動いた 頂点）
fz = f1 / np.maximum(np.linalg.norm(f1, axis=1, keepdims=True), 1e-20)
dots = []
for k in range(3):
    dots.append((fz * n1[t[:, k]].astype(np.float64)).sum(1))
dots = np.concatenate(dots)
dots0 = []
fz0 = f0 / np.maximum(np.linalg.norm(f0, axis=1, keepdims=True), 1e-20)
for k in range(3):
    dots0.append((fz0 * n0[t[:, k]].astype(np.float64)).sum(1))
dots0 = np.concatenate(dots0)
print('    頂点の 向き・面の 向きの 合い方（1＝ぴったり）：元 中央', round(float(np.median(dots0)), 4), 'p5', round(float(np.percentile(dots0, 5)), 4), ' → 新 中央', round(float(np.median(dots)), 4), 'p5', round(float(np.percentile(dots, 5)), 4))
chk('面の 向きは 形に 合っている（元と 同じ くらい）', np.percentile(dots, 5) > np.percentile(dots0, 5) - 0.08)
# 絵
for k, im in enumerate(js1['images']):
    raw1 = bv_bytes(js1, bin1, im['bufferView']); raw0 = bv_bytes(js0, bin0, js0['images'][k]['bufferView'])
    A0 = np.asarray(Image.open(io.BytesIO(raw0)).convert('RGB')); pic = Image.open(io.BytesIO(raw1)); A1 = np.asarray(pic.convert('RGB'))
    df = (A0 != A1).any(2)
    ys, xs = np.nonzero(df)
    chk(f'絵 {k}：{im["mimeType"]}・{pic.size}・変わった 点 {int(df.sum())}（ぜんぶ 目の あたり）', im['mimeType'] == 'image/png' and raw1[:8] == b'\x89PNG\r\n\x1a\n' and pic.size == (2048, 2048) and pic.mode == 'RGB' and 3000 < df.sum() < 9000 and xs.min() > 330 and xs.max() < 740 and ys.min() > 250 and ys.max() < 1650, (int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max()), len(raw1)))
print('まとめ：', 'ぜんぶ OK' if ok else 'NG あり')
sys.exit(0 if ok else 1)
