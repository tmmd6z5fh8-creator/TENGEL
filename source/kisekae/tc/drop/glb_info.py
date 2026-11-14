# GLB の中身を調べる（読むだけ）
import sys, json, struct
p = sys.argv[1]
b = open(p, 'rb').read()
magic, ver, total = struct.unpack('<4sII', b[:12])
print('magic', magic, 'ver', ver, 'total', total, 'file', len(b))
off = 12
chunks = []
while off < len(b):
    ln, ty = struct.unpack('<I4s', b[off:off+8])
    chunks.append((ty, off+8, ln))
    print('chunk', ty, 'len', ln)
    off += 8 + ln
js = json.loads(b[chunks[0][1]:chunks[0][1]+chunks[0][2]])
print('keys', list(js.keys()))
print('asset', js.get('asset'))
print('scenes', js.get('scenes'))
print('nodes', len(js.get('nodes', [])))
for i, n in enumerate(js.get('nodes', [])):
    print('  node', i, {k: v for k, v in n.items()})
print('meshes', len(js.get('meshes', [])))
for i, m in enumerate(js.get('meshes', [])):
    print('  mesh', i, m.get('name'), 'prims', len(m['primitives']))
    for pr in m['primitives']:
        print('     ', pr)
print('materials')
for i, m in enumerate(js.get('materials', [])):
    print('  mat', i, json.dumps(m, ensure_ascii=False))
print('textures', js.get('textures'))
print('samplers', js.get('samplers'))
print('images')
for i, im in enumerate(js.get('images', [])):
    print('  img', i, im)
print('accessors')
for i, a in enumerate(js.get('accessors', [])):
    print('  acc', i, a)
print('bufferViews')
for i, a in enumerate(js.get('bufferViews', [])):
    print('  bv', i, a)
print('buffers', js.get('buffers'))
print('extensionsUsed', js.get('extensionsUsed'), 'required', js.get('extensionsRequired'))
print('animations', len(js.get('animations', [])), 'skins', len(js.get('skins', [])))
