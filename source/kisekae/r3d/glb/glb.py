# glb.py — GLB / glTF 2.0 loader (numpy + PIL only).
#
#   m = load('horse.glb')            # Model
#   m.summary()                      # counts
#   prims = m.flatten(t=None)        # list of Prim with world-space pos/normal/uv (+ skinning at time t)
#
# Supported: GLB header/JSON/BIN, .gltf with embedded data URIs or external files, accessors (all
# component types, normalized, byteStride, sparse), meshes (TRIANGLES / STRIP / FAN -> triangles),
# node TRS/matrix hierarchy, materials (pbrMetallicRoughness, normal, occlusion, emissive, alphaMode,
# alphaCutoff, doubleSided, KHR_texture_transform, KHR_materials_emissive_strength), textures/samplers
# (wrapS/T), images (bufferView or data URI or file), skins (joints, inverseBindMatrices, JOINTS_0 /
# WEIGHTS_0, 4 weights), animations (translation / rotation / scale, STEP / LINEAR / CUBICSPLINE(as linear)).
import base64, json, math, os, struct, io
import numpy as np
from PIL import Image

CT = {5120: ('i1', 1), 5121: ('u1', 1), 5122: ('i2', 2), 5123: ('u2', 2), 5125: ('u4', 4), 5126: ('f4', 4)}
NC = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT2': 4, 'MAT3': 9, 'MAT4': 16}
REPEAT, CLAMP, MIRROR = 10497, 33071, 33648


class Texture:
    """Decoded image + sampler. img: float32 HxWx4 in [0,1] (sRGB as stored; convert in shading)."""
    def __init__(self, img, wrap_s=REPEAT, wrap_t=REPEAT, name=''):
        self.img = img
        self.wrap_s, self.wrap_t = wrap_s, wrap_t
        self.name = name
        self._mips = None

    @property
    def mips(self):
        if self._mips is None:
            mips = [self.img]
            cur = self.img
            while min(cur.shape[0], cur.shape[1]) > 2:
                h, w = cur.shape[0] // 2 * 2, cur.shape[1] // 2 * 2
                c = cur[:h, :w]
                cur = 0.25 * (c[0::2, 0::2] + c[1::2, 0::2] + c[0::2, 1::2] + c[1::2, 1::2])
                mips.append(cur.astype(np.float32))
            self._mips = mips
        return self._mips


class Material:
    def __init__(self, d=None, textures=None, name=''):
        d = d or {}
        self.name = name or d.get('name', '')
        pbr = d.get('pbrMetallicRoughness', {})
        self.base_color = np.array(pbr.get('baseColorFactor', [1, 1, 1, 1]), np.float32)
        self.metallic = float(pbr.get('metallicFactor', 1.0))
        self.roughness = float(pbr.get('roughnessFactor', 1.0))
        self.emissive = np.array(d.get('emissiveFactor', [0, 0, 0]), np.float32)
        ext = d.get('extensions', {})
        self.emissive *= float(ext.get('KHR_materials_emissive_strength', {}).get('emissiveStrength', 1.0))
        self.alpha_mode = d.get('alphaMode', 'OPAQUE')
        self.alpha_cutoff = float(d.get('alphaCutoff', 0.5))
        self.double_sided = bool(d.get('doubleSided', False))
        self.unlit = 'KHR_materials_unlit' in ext

        def tex(info):
            if not info or textures is None:
                return None
            t = textures[info['index']] if info['index'] < len(textures) else None
            if t is None:
                return None
            xf = info.get('extensions', {}).get('KHR_texture_transform')
            return TexRef(t, info.get('texCoord', 0), xf, info.get('scale', info.get('strength', 1.0)))
        self.base_tex = tex(pbr.get('baseColorTexture'))
        self.mr_tex = tex(pbr.get('metallicRoughnessTexture'))
        self.normal_tex = tex(d.get('normalTexture'))
        self.occl_tex = tex(d.get('occlusionTexture'))
        self.emis_tex = tex(d.get('emissiveTexture'))


class TexRef:
    def __init__(self, tex, texcoord=0, transform=None, scale=1.0):
        self.tex, self.texcoord, self.scale = tex, texcoord, float(scale)
        self.offset = np.array((transform or {}).get('offset', [0, 0]), np.float32)
        self.rot = float((transform or {}).get('rotation', 0.0))
        self.tscale = np.array((transform or {}).get('scale', [1, 1]), np.float32)
        self.has_xf = transform is not None

    def uv(self, uv):
        if not self.has_xf:
            return uv
        c, s = math.cos(self.rot), math.sin(self.rot)
        u = uv[..., 0] * self.tscale[0]; v = uv[..., 1] * self.tscale[1]
        return np.stack([c * u + s * v + self.offset[0], -s * u + c * v + self.offset[1]], -1)


class Prim:
    """One drawable: world-space triangles with per-vertex attributes."""
    def __init__(self, pos, nrm, uv, idx, mat, name='', uv1=None, tangent=None, color=None):
        self.pos, self.nrm, self.uv, self.idx, self.mat, self.name = pos, nrm, uv, idx, mat, name
        self.uv1, self.tangent, self.color = uv1, tangent, color

    @property
    def ntri(self):
        return len(self.idx)


class Model:
    def __init__(self, gltf, buffers, path=''):
        self.g, self.buffers, self.path = gltf, buffers, path
        self.images = [self._image(i) for i in range(len(gltf.get('images', [])))]
        self.textures = []
        for t in gltf.get('textures', []):
            src = t.get('source', t.get('extensions', {}).get('KHR_texture_basisu', {}).get('source'))
            samp = gltf.get('samplers', [])[t['sampler']] if 'sampler' in t else {}
            img = self.images[src] if src is not None and src < len(self.images) else None
            self.textures.append(Texture(img, samp.get('wrapS', REPEAT), samp.get('wrapT', REPEAT), t.get('name', '')) if img is not None else None)
        self.materials = [Material(m, self.textures) for m in gltf.get('materials', [])]
        self.default_material = Material({}, self.textures, 'default')
        self.nodes = gltf.get('nodes', [])
        self.scene = gltf.get('scenes', [{}])[gltf.get('scene', 0)] if gltf.get('scenes') else {'nodes': list(range(len(self.nodes)))}
        self.parent = [-1] * len(self.nodes)
        for i, n in enumerate(self.nodes):
            for c in n.get('children', []):
                self.parent[c] = i
        self.animations = gltf.get('animations', [])
        self._mesh_cache = {}

    # ---------- raw access
    def accessor(self, i):
        a = self.g['accessors'][i]
        n, ncomp = a['count'], NC[a['type']]
        dt, sz = CT[a['componentType']]
        if 'bufferView' in a:
            bv = self.g['bufferViews'][a['bufferView']]
            buf = self.buffers[bv['buffer']]
            off = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
            stride = bv.get('byteStride', 0)
            elem = ncomp * sz
            if stride and stride != elem:
                raw = np.frombuffer(buf, np.uint8, count=stride * (n - 1) + elem, offset=off)
                idx = (np.arange(n)[:, None] * stride + np.arange(elem)[None, :])
                arr = raw[idx].copy().view(dt).reshape(n, ncomp)
            else:
                arr = np.frombuffer(buf, dt, count=n * ncomp, offset=off).reshape(n, ncomp)
        else:
            arr = np.zeros((n, ncomp), dt)
        arr = np.array(arr)
        if 'sparse' in a:
            sp = a['sparse']
            iv = self.g['bufferViews'][sp['indices']['bufferView']]
            idt, _ = CT[sp['indices']['componentType']]
            ind = np.frombuffer(self.buffers[iv['buffer']], idt, count=sp['count'], offset=iv.get('byteOffset', 0) + sp['indices'].get('byteOffset', 0))
            vv = self.g['bufferViews'][sp['values']['bufferView']]
            val = np.frombuffer(self.buffers[vv['buffer']], dt, count=sp['count'] * ncomp, offset=vv.get('byteOffset', 0) + sp['values'].get('byteOffset', 0)).reshape(-1, ncomp)
            arr[ind] = val
        if a.get('normalized') and dt != 'f4':
            mx = {'i1': 127., 'u1': 255., 'i2': 32767., 'u2': 65535., 'u4': 4294967295.}[dt]
            arr = np.maximum(arr.astype(np.float32) / mx, -1.0)
        if ncomp == 1:
            arr = arr[:, 0]
        return arr

    def _image(self, i):
        im = self.g['images'][i]
        try:
            if 'bufferView' in im:
                bv = self.g['bufferViews'][im['bufferView']]
                data = bytes(self.buffers[bv['buffer']][bv.get('byteOffset', 0): bv.get('byteOffset', 0) + bv['byteLength']])
            elif im.get('uri', '').startswith('data:'):
                data = base64.b64decode(im['uri'].split(',', 1)[1])
            else:
                with open(os.path.join(os.path.dirname(self.path), im['uri']), 'rb') as f:
                    data = f.read()
            pil = Image.open(io.BytesIO(data)).convert('RGBA')
            return np.asarray(pil, np.float32) / 255.0
        except Exception as e:  # keep going without the texture
            print('image', i, 'failed:', e)
            return None

    # ---------- node transforms
    @staticmethod
    def _trs(n, over=None):
        over = over or {}
        if 'matrix' in n and not over:
            return np.array(n['matrix'], np.float64).reshape(4, 4).T
        t = np.array(over.get('translation', n.get('translation', [0, 0, 0])), np.float64)
        q = np.array(over.get('rotation', n.get('rotation', [0, 0, 0, 1])), np.float64)
        s = np.array(over.get('scale', n.get('scale', [1, 1, 1])), np.float64)
        x, y, z, w = q / max(np.linalg.norm(q), 1e-12)
        R = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                      [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                      [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
        M = np.eye(4)
        M[:3, :3] = R * s[None, :]
        M[:3, 3] = t
        return M

    def world_matrices(self, t=None, anim=0):
        over = self.animate(t, anim) if t is not None and self.animations else {}
        local = [self._trs(n, over.get(i)) for i, n in enumerate(self.nodes)]
        world = [None] * len(self.nodes)

        def get(i):
            if world[i] is None:
                p = self.parent[i]
                world[i] = local[i] if p < 0 else get(p) @ local[i]
            return world[i]
        for i in range(len(self.nodes)):
            get(i)
        return world

    # ---------- animation
    def anim_duration(self, anim=0):
        if not self.animations:
            return 0.0
        return max(float(self.accessor(self.g['animations'][anim]['samplers'][ch['sampler']]['input']).max())
                   for ch in self.animations[anim]['channels'])

    def animate(self, t, anim=0):
        a = self.animations[anim]
        over = {}
        for ch in a['channels']:
            tgt = ch['target']
            if 'node' not in tgt or tgt['path'] not in ('translation', 'rotation', 'scale'):
                continue
            s = a['samplers'][ch['sampler']]
            times = self.accessor(s['input']).astype(np.float64)
            vals = self.accessor(s['output']).astype(np.float64)
            interp = s.get('interpolation', 'LINEAR')
            if interp == 'CUBICSPLINE':
                vals = vals.reshape(len(times), 3, -1)[:, 1]
            tt = float(np.clip(t, times[0], times[-1]))
            k = int(np.searchsorted(times, tt, side='right') - 1)
            k = max(0, min(k, len(times) - 1))
            if interp == 'STEP' or k >= len(times) - 1 or times[k + 1] <= times[k]:
                v = vals[k]
            else:
                f = (tt - times[k]) / (times[k + 1] - times[k])
                v0, v1 = vals[k], vals[k + 1]
                if tgt['path'] == 'rotation':
                    d = float(np.dot(v0, v1))
                    if d < 0:
                        v1, d = -v1, -d
                    if d > 0.9995:
                        v = v0 + f * (v1 - v0)
                    else:
                        th = math.acos(d)
                        v = (math.sin((1 - f) * th) * v0 + math.sin(f * th) * v1) / math.sin(th)
                    v = v / np.linalg.norm(v)
                else:
                    v = v0 + f * (v1 - v0)
            over.setdefault(tgt['node'], {})[tgt['path']] = v
        return over

    # ---------- geometry
    def _mesh_prims(self, mi):
        if mi in self._mesh_cache:
            return self._mesh_cache[mi]
        out = []
        mesh = self.g['meshes'][mi]
        for p in mesh['primitives']:
            mode = p.get('mode', 4)
            if mode not in (4, 5, 6):
                continue
            at = p['attributes']
            pos = self.accessor(at['POSITION']).astype(np.float32)
            n = len(pos)
            idx = self.accessor(p['indices']).astype(np.int64) if 'indices' in p else np.arange(n, dtype=np.int64)
            if mode == 4:
                tri = idx[: len(idx) // 3 * 3].reshape(-1, 3)
            elif mode == 5:
                tri = np.stack([idx[:-2], idx[1:-1], idx[2:]], 1)
                tri[1::2] = tri[1::2][:, [1, 0, 2]]
            else:
                tri = np.stack([np.full(len(idx) - 2, idx[0]), idx[1:-1], idx[2:]], 1)
            nrm = self.accessor(at['NORMAL']).astype(np.float32) if 'NORMAL' in at else None
            uv = self.accessor(at['TEXCOORD_0']).astype(np.float32) if 'TEXCOORD_0' in at else np.zeros((n, 2), np.float32)
            uv1 = self.accessor(at['TEXCOORD_1']).astype(np.float32) if 'TEXCOORD_1' in at else None
            tan = self.accessor(at['TANGENT']).astype(np.float32) if 'TANGENT' in at else None
            col = self.accessor(at['COLOR_0']).astype(np.float32) if 'COLOR_0' in at else None
            if col is not None and col.shape[1] == 3:
                col = np.concatenate([col, np.ones((n, 1), np.float32)], 1)
            joints = self.accessor(at['JOINTS_0']).astype(np.int64) if 'JOINTS_0' in at else None
            weights = self.accessor(at['WEIGHTS_0']).astype(np.float32) if 'WEIGHTS_0' in at else None
            mat = self.materials[p['material']] if 'material' in p and p['material'] < len(self.materials) else self.default_material
            out.append(dict(pos=pos, nrm=nrm, uv=uv, uv1=uv1, tan=tan, col=col, tri=tri, mat=mat, joints=joints, weights=weights, name=mesh.get('name', f'mesh{mi}')))
        self._mesh_cache[mi] = out
        return out

    def flatten(self, t=None, anim=0, compute_normals=True):
        """World-space primitives; t = animation time (seconds) or None for the rest pose."""
        world = self.world_matrices(t, anim)
        prims = []
        for ni, n in enumerate(self.nodes):
            if 'mesh' not in n:
                continue
            skin = self.g['skins'][n['skin']] if 'skin' in n and 'skins' in self.g else None
            if skin is not None:
                joints = skin['joints']
                ibm = self.accessor(skin['inverseBindMatrices']).reshape(-1, 4, 4).transpose(0, 2, 1) if 'inverseBindMatrices' in skin else np.tile(np.eye(4), (len(joints), 1, 1))
                J = np.stack([world[j] @ ibm[k] for k, j in enumerate(joints)])  # (nj,4,4)
            for pr in self._mesh_prims(n['mesh']):
                pos, nrm = pr['pos'], pr['nrm']
                if skin is not None and pr['joints'] is not None:
                    w = pr['weights']
                    w = w / np.maximum(w.sum(1, keepdims=True), 1e-8)
                    M = np.einsum('vk,vkij->vij', w, J[pr['joints']])  # (n,4,4)
                    pos = np.einsum('vij,vj->vi', M[:, :3, :3], pos) + M[:, :3, 3]
                    if nrm is not None:
                        nrm = np.einsum('vij,vj->vi', np.linalg.inv(M[:, :3, :3]).transpose(0, 2, 1), nrm)
                else:
                    W = world[ni]
                    pos = pos @ W[:3, :3].T + W[:3, 3]
                    if nrm is not None:
                        nrm = nrm @ np.linalg.inv(W[:3, :3])
                pos = pos.astype(np.float32)
                tri = pr['tri']
                if nrm is None and compute_normals:
                    nrm = vertex_normals(pos, tri)
                if nrm is not None:
                    nrm = (nrm / np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-9)).astype(np.float32)
                tan = pr['tan']
                if tan is None and pr['mat'].normal_tex is not None:
                    tan = vertex_tangents(pos, nrm, pr['uv'], tri)
                prims.append(Prim(pos, nrm, pr['uv'], tri, pr['mat'], f"{n.get('name', 'node%d' % ni)}/{pr['name']}", pr['uv1'], tan, pr['col']))
        return prims

    def bbox(self, prims=None):
        prims = prims or self.flatten()
        lo = np.min([p.pos.min(0) for p in prims], 0)
        hi = np.max([p.pos.max(0) for p in prims], 0)
        return lo, hi

    def summary(self):
        prims = self.flatten()
        print(f"nodes {len(self.nodes)}  meshes {len(self.g.get('meshes', []))}  prims {len(prims)}  tris {sum(p.ntri for p in prims):,}  verts {sum(len(p.pos) for p in prims):,}")
        print(f"materials {len(self.materials)}  textures {len(self.textures)}  images {len(self.images)}  skins {len(self.g.get('skins', []))}  animations {len(self.animations)}"
              + (f" (dur {self.anim_duration():.2f}s)" if self.animations else ''))
        for m in self.materials:
            print(f"  mat {m.name!r}: base {np.round(m.base_color, 2).tolist()} tex={'yes' if m.base_tex else 'no'} mr={'yes' if m.mr_tex else 'no'} nrm={'yes' if m.normal_tex else 'no'} emis={'yes' if m.emis_tex else 'no'} {np.round(m.emissive, 2).tolist()} alpha={m.alpha_mode} ds={m.double_sided}")
        lo, hi = self.bbox(prims)
        print('bbox', np.round(lo, 3).tolist(), np.round(hi, 3).tolist(), 'size', np.round(hi - lo, 3).tolist())
        return prims


def vertex_normals(pos, tri):
    fn = np.cross(pos[tri[:, 1]] - pos[tri[:, 0]], pos[tri[:, 2]] - pos[tri[:, 0]])
    n = np.zeros_like(pos)
    for k in range(3):
        np.add.at(n, tri[:, k], fn)
    return n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)


def vertex_tangents(pos, nrm, uv, tri):
    e1, e2 = pos[tri[:, 1]] - pos[tri[:, 0]], pos[tri[:, 2]] - pos[tri[:, 0]]
    d1, d2 = uv[tri[:, 1]] - uv[tri[:, 0]], uv[tri[:, 2]] - uv[tri[:, 0]]
    det = d1[:, 0] * d2[:, 1] - d2[:, 0] * d1[:, 1]
    r = np.where(np.abs(det) > 1e-12, 1.0 / np.where(np.abs(det) > 1e-12, det, 1), 0.0)
    ft = (e1 * d2[:, 1:2] - e2 * d1[:, 1:2]) * r[:, None]
    fb = (e2 * d1[:, 0:1] - e1 * d2[:, 0:1]) * r[:, None]
    t = np.zeros_like(pos); b = np.zeros_like(pos)
    for k in range(3):
        np.add.at(t, tri[:, k], ft); np.add.at(b, tri[:, k], fb)
    t = t - nrm * np.sum(nrm * t, 1, keepdims=True)
    t /= np.maximum(np.linalg.norm(t, axis=1, keepdims=True), 1e-12)
    w = np.where(np.sum(np.cross(nrm, t) * b, 1) < 0, -1.0, 1.0)
    return np.concatenate([t, w[:, None]], 1).astype(np.float32)


def load(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data[:4] == b'glTF':
        magic, ver, length = struct.unpack_from('<III', data, 0)
        off = 12
        gltf, buffers = None, []
        while off < length:
            clen, ctype = struct.unpack_from('<II', data, off)
            chunk = data[off + 8: off + 8 + clen]
            if ctype == 0x4E4F534A:
                gltf = json.loads(chunk.decode('utf-8'))
            elif ctype == 0x004E4942:
                buffers.append(np.frombuffer(chunk, np.uint8))
            off += 8 + clen
    else:
        gltf = json.loads(data.decode('utf-8'))
        buffers = []
        for b in gltf.get('buffers', []):
            uri = b.get('uri', '')
            if uri.startswith('data:'):
                buffers.append(np.frombuffer(base64.b64decode(uri.split(',', 1)[1]), np.uint8))
            else:
                with open(os.path.join(os.path.dirname(path), uri), 'rb') as f:
                    buffers.append(np.frombuffer(f.read(), np.uint8))
    return Model(gltf, buffers, path)


if __name__ == '__main__':
    import sys
    load(sys.argv[1]).summary()
