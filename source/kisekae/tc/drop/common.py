# 台の 3D を 読む・描く 共通の 道具（読むだけ。元の ファイルは 書きかえない）
import sys
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from dp_env import ROOT
import sys, json, struct, io, math
import numpy as np
LIB = __import__('os').path.normpath(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', '..', 'r3d', 'glb'))
if LIB not in sys.path:
    sys.path.insert(0, LIB)

ORIG = ROOT + '/in/machine_orig.glb'


def read_glb(path):
    b = open(path, 'rb').read()
    magic, ver, total = struct.unpack('<4sII', b[:12])
    assert magic == b'glTF' and ver == 2 and total == len(b), (magic, ver, total, len(b))
    ln, ty = struct.unpack('<I4s', b[12:20]); assert ty == b'JSON'
    js = json.loads(b[20:20 + ln])
    o = 20 + ln
    ln2, ty2 = struct.unpack('<I4s', b[o:o + 8]); assert ty2 == b'BIN\x00'
    binb = b[o + 8:o + 8 + ln2]
    assert o + 8 + ln2 == len(b)
    return js, binb


def bv_bytes(js, binb, i):
    v = js['bufferViews'][i]
    return binb[v.get('byteOffset', 0):v.get('byteOffset', 0) + v['byteLength']]


def arrays(js, binb):
    """頂点・絵の 場所・面の 向き・三角（1つの かたまりの 3D だけ）"""
    pr = js['meshes'][0]['primitives'][0]
    acc = js['accessors']

    def get(i, dt, nc):
        a = acc[i]
        raw = bv_bytes(js, binb, a['bufferView'])
        off = a.get('byteOffset', 0)
        return np.frombuffer(raw, dt, a['count'] * nc, off).reshape(a['count'], nc) if nc > 1 else np.frombuffer(raw, dt, a['count'], off)
    pos = get(pr['attributes']['POSITION'], '<f4', 3)
    uv = get(pr['attributes']['TEXCOORD_0'], '<f4', 2)
    nrm = get(pr['attributes']['NORMAL'], '<f4', 3)
    idx = get(pr['indices'], '<u4', 1).reshape(-1, 3)
    return pos, uv, nrm, idx


def write_glb(path, js, binb):
    """GLB を 書く（JSON は 空白で 4の 倍数・BIN は 0 で 4の 倍数）"""
    import os
    assert not os.path.exists(path), 'すでに ある：' + path
    j = json.dumps(js, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    j += b' ' * ((4 - len(j) % 4) % 4)
    binb = bytes(binb) + b'\x00' * ((4 - len(binb) % 4) % 4)
    total = 12 + 8 + len(j) + 8 + len(binb)
    with open(path, 'wb') as f:
        f.write(struct.pack('<4sII', b'glTF', 2, total))
        f.write(struct.pack('<I4s', len(j), b'JSON')); f.write(j)
        f.write(struct.pack('<I4s', len(binb), b'BIN\x00')); f.write(binb)
    return total
