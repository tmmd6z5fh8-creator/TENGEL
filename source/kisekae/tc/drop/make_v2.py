# 台の 3D の 直し：① 釘を 伸ばす ② 馬の 目を ぬり直す → 新しい GLB（元の ファイルは 書きかえない）
#   python3 -I make_v2.py <出力の GLB> [釘の 倍率=2.0]
import sys, io, os, hashlib, copy
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from common import *
import pegs as PG
import eyes as EY
from PIL import Image



def png_bytes(a):
    buf = io.BytesIO()
    Image.fromarray(a).save(buf, 'PNG', optimize=True)
    return buf.getvalue()


def build(out, k=2.0, eyes=True, pegs_on=True):
    js, binb = read_glb(ORIG)
    js = copy.deepcopy(js)
    pos, uv, nrm, idx = arrays(js, binb)
    rec = dict(source=os.path.basename(ORIG), source_sha256=hashlib.sha256(open(ORIG, 'rb').read()).hexdigest(), peg_scale=k if pegs_on else 1.0)
    # ① 釘
    P, N = pos.astype(np.float64), nrm.astype(np.float64)
    if pegs_on:
        pegs = PG.find_pegs()
        assert len(pegs) == 18, len(pegs)
        P2, N2, moved, log = PG.stretch(P, N, pegs, k)
        rec['pegs'] = log; rec['peg_vertices_moved'] = int(moved.sum())
    else:
        P2, N2, moved = P, N, np.zeros(len(P), bool)
    pos2, nrm2 = P2.astype('<f4'), N2.astype('<f4')
    pos2[~moved] = pos[~moved]; nrm2[~moved] = nrm[~moved]          # 動かさない 頂点は 1ビットも 変えない
    # ② 目
    imgs = [np.asarray(Image.open(io.BytesIO(bv_bytes(js, binb, im['bufferView']))).convert('RGB')).copy() for im in js['images']]
    new_img = [None, None, None]
    if eyes:
        outs, chg, info = EY.paint(imgs, pos, uv, idx, verbose=False)
        for i in range(3):
            new_img[i] = png_bytes(outs[i])
        rec['eyes'] = info; rec['texels_changed'] = [int(c.sum()) for c in chg]; rec['eye_rgb'] = EY.EYE_RGB.tolist()
    # 書く：バッファを 組み直す
    acc = js['accessors']; pr = js['meshes'][0]['primitives'][0]
    parts = []
    for i, v in enumerate(js['bufferViews']):
        parts.append(bytes(bv_bytes(js, binb, i)))
    parts[acc[pr['attributes']['POSITION']]['bufferView']] = pos2.tobytes()
    parts[acc[pr['attributes']['NORMAL']]['bufferView']] = nrm2.tobytes()
    for i, im in enumerate(js['images']):
        if new_img[i] is not None:
            parts[im['bufferView']] = new_img[i]; im['mimeType'] = 'image/png'
    off = 0; blob = bytearray()
    for i, v in enumerate(js['bufferViews']):
        pad = (4 - off % 4) % 4
        blob += b'\x00' * pad; off += pad
        v['byteOffset'] = off; v['byteLength'] = len(parts[i])
        blob += parts[i]; off += len(parts[i])
    js['buffers'][0]['byteLength'] = len(blob) + (4 - len(blob) % 4) % 4
    a = acc[pr['attributes']['POSITION']]
    a['min'] = [float(x) for x in pos2.min(0)]; a['max'] = [float(x) for x in pos2.max(0)]
    total = write_glb(out, js, blob)
    rec['out'] = os.path.basename(out); rec['out_bytes'] = total
    return rec


if __name__ == '__main__':
    out = sys.argv[1]
    k = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0
    rec = build(out, k)
    json.dump(rec, open(out[:-4] + '_記録.json', 'w'), indent=1, ensure_ascii=False)
    print('wrote', out, rec['out_bytes'], 'bytes; pegs moved', rec.get('peg_vertices_moved'), 'texels changed', rec.get('texels_changed'))
    for k, v in rec.get('eyes', {}).items():
        print('  ', k, v)
