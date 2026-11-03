# raster.py — software renderer for glb.py models: visibility buffer in C (libraster.so), shading in numpy.
#
#   from glb import load; from raster import Camera, Light, render, tonemap, save
#   m = load('horse.glb'); prims = m.flatten()
#   cam = Camera.look_at(eye, target, fov_y=35, W=780, H=1688)
#   out = render(prims, cam, lights=[Light.key(...)], ss=2)
#   save(tonemap(out['rgb']), 'x.png')
#
# render() returns linear HDR buffers at the output size (after supersample downsampling):
#   rgb (H,W,3) lit colour incl. emissive, alpha (H,W) coverage, depth (H,W) view distance (inf = empty),
#   normal (H,W,3) world normals, emissive (H,W,3) emissive-only (for bloom), albedo, pos (H,W,3) world pos,
#   ao (H,W), shadow (H,W) key-light visibility, mat (H,W) material id (-1 empty)
import ctypes, math, os
import numpy as np
from PIL import Image

_HERE = os.path.dirname(os.path.abspath(__file__))


def _build_lib():
    """libraster.so is not committed: build it from raster.c on first use (or when raster.c is newer)."""
    so, c = os.path.join(_HERE, 'libraster.so'), os.path.join(_HERE, 'raster.c')
    if not os.path.exists(so) or os.path.getmtime(so) < os.path.getmtime(c):
        import subprocess
        subprocess.run(['gcc', '-O3', '-shared', '-fPIC', '-o', so, c, '-lm'], check=True)
    return so


_lib = ctypes.CDLL(_build_lib())
_fp = ctypes.POINTER(ctypes.c_float)
_ip = ctypes.POINTER(ctypes.c_int32)
_lib.rasterize.argtypes = [ctypes.c_int, _fp, _fp, ctypes.c_int, _ip, _ip, _ip, ctypes.c_int, ctypes.POINTER(_fp), _ip, _ip, _fp,
                           ctypes.c_int, ctypes.c_int, _fp, _ip, _fp, ctypes.POINTER(ctypes.c_int8)]
_lib.rasterize_depth.argtypes = [ctypes.c_int, _fp, ctypes.c_int, _ip, ctypes.c_int, ctypes.c_int, _fp]


def _f32(a):
    return np.ascontiguousarray(a, np.float32)


def _i32(a):
    return np.ascontiguousarray(a, np.int32)


def normalize(v, axis=-1):
    return v / np.maximum(np.linalg.norm(v, axis=axis, keepdims=True), 1e-12)


def srgb_to_linear(c):
    c = np.asarray(c, np.float32)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4).astype(np.float32)


def linear_to_srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)


# ---------------------------------------------------------------- camera
class Camera:
    def __init__(self, view, proj, W, H, ortho=False):
        self.view, self.proj, self.W, self.H, self.ortho = view, proj, W, H, ortho
        self.inv_view = np.linalg.inv(view)
        self.eye = self.inv_view[:3, 3].copy()

    @staticmethod
    def look_at(eye, target, up=(0, 1, 0), fov_y=35.0, W=780, H=1688, near=None, far=None, ortho=False, ortho_h=None):
        eye, target, up = np.array(eye, np.float64), np.array(target, np.float64), np.array(up, np.float64)
        f = normalize(target - eye)
        s = normalize(np.cross(f, up))
        u = np.cross(s, f)
        view = np.eye(4)
        view[0, :3], view[1, :3], view[2, :3] = s, u, -f
        view[:3, 3] = -view[:3, :3] @ eye
        dist = np.linalg.norm(target - eye)
        near = near or max(dist * 0.02, 1e-3)
        far = far or dist * 20
        aspect = W / H
        if ortho:
            h = ortho_h or dist * math.tan(math.radians(fov_y) / 2) * 2
            w = h * aspect
            proj = np.array([[2 / w, 0, 0, 0], [0, 2 / h, 0, 0], [0, 0, -2 / (far - near), -(far + near) / (far - near)], [0, 0, 0, 1]])
        else:
            t = 1 / math.tan(math.radians(fov_y) / 2)
            proj = np.array([[t / aspect, 0, 0, 0], [0, t, 0, 0], [0, 0, (far + near) / (near - far), 2 * far * near / (near - far)], [0, 0, -1, 0]])
        c = Camera(view, proj, W, H, ortho)
        c.near, c.far, c.fov_y = near, far, fov_y
        return c

    def scaled(self, k):
        c = Camera(self.view, self.proj, int(round(self.W * k)), int(round(self.H * k)), self.ortho)
        c.near, c.far, c.fov_y = self.near, self.far, self.fov_y
        return c

    def view_dirs(self):
        """Per-pixel world-space ray directions (H,W,3) from the eye (perspective)."""
        ys, xs = np.mgrid[0:self.H, 0:self.W].astype(np.float32)
        ndc_x = (xs + 0.5) / self.W * 2 - 1
        ndc_y = 1 - (ys + 0.5) / self.H * 2
        t = 1 / self.proj[1, 1]
        d = np.stack([ndc_x * t * (self.W / self.H), ndc_y * t, -np.ones_like(ndc_x)], -1)
        return normalize(d @ self.inv_view[:3, :3].T)


# ---------------------------------------------------------------- lights
class Light:
    def __init__(self, direction, color=(1, 1, 1), intensity=1.0, shadow=False, shadow_res=2048, softness=1.5, name=''):
        self.dir = normalize(np.array(direction, np.float32))  # direction TOWARDS the light
        self.color = np.array(color, np.float32) * float(intensity)
        self.shadow, self.shadow_res, self.softness, self.name = shadow, shadow_res, softness, name

    @staticmethod
    def key(direction=(0.4, 0.8, 0.6), color=(1.0, 0.92, 0.78), intensity=3.0, shadow=True, **k):
        return Light(direction, color, intensity, shadow, name='key', **k)

    @staticmethod
    def fill(direction=(-0.7, 0.2, 0.5), color=(0.55, 0.65, 0.9), intensity=0.5, **k):
        return Light(direction, color, intensity, False, name='fill', **k)

    @staticmethod
    def rim(direction=(0.1, 0.4, -1.0), color=(1.0, 0.8, 0.45), intensity=2.5, **k):
        return Light(direction, color, intensity, False, name='rim', **k)


# ---------------------------------------------------------------- geometry prep
class Scene:
    """Concatenated primitives with per-triangle material ids."""
    def __init__(self, prims, model_matrix=None):
        pos, nrm, uv, tan, col, tri, tmat, tflag, mats = [], [], [], [], [], [], [], [], []
        off = 0
        flip = model_matrix is not None and np.linalg.det(model_matrix[:3, :3]) < 0
        matid = {}
        for p in prims:
            mid = matid.setdefault(id(p.mat), len(matid))
            if len(mats) <= mid:
                mats.append(p.mat)
            P, N = p.pos, p.nrm
            if model_matrix is not None:
                M = model_matrix
                P = P @ M[:3, :3].T + M[:3, 3]
                N = normalize(N @ np.linalg.inv(M[:3, :3]))
            pos.append(P.astype(np.float32)); nrm.append(N.astype(np.float32)); uv.append(p.uv.astype(np.float32))
            t = p.tangent if p.tangent is not None else np.zeros((len(P), 4), np.float32)
            if model_matrix is not None and p.tangent is not None:
                t = np.concatenate([normalize(t[:, :3] @ model_matrix[:3, :3].T), t[:, 3:]], 1)
            tan.append(t.astype(np.float32))
            col.append(p.color if p.color is not None else np.ones((len(P), 4), np.float32))
            idx = p.idx[:, [0, 2, 1]] if flip else p.idx
            tri.append(idx + off); off += len(P)
            tmat.append(np.full(len(idx), mid, np.int32))
            tflag.append(np.full(len(idx), 1 if p.mat.double_sided else 0, np.int32))
        self.pos, self.nrm, self.uv, self.tan, self.col = map(np.concatenate, (pos, nrm, uv, tan, col))
        self.tri, self.tmat, self.tflag = np.concatenate(tri).astype(np.int64), np.concatenate(tmat), np.concatenate(tflag)
        self.mats = mats
        self.lo, self.hi = self.pos.min(0), self.pos.max(0)

    def bbox(self):
        return self.lo, self.hi


def _project(cam, pos):
    """World -> (screen xyzw float32 (n,4): x px, y px (down), z ndc, inv_w) and clip-space z for near clipping."""
    n = len(pos)
    hp = np.concatenate([pos, np.ones((n, 1), np.float32)], 1).astype(np.float64)
    clip = hp @ (cam.proj @ cam.view).T
    return clip


def _clip_and_screen(cam, clip, tri, extra_tri_arrays):
    """Near-plane clipping (w > eps). Returns screen xyzw, new tri list, and index map for extra per-tri arrays."""
    eps = 1e-5
    w = clip[:, 3]
    inside = w > eps
    tin = inside[tri]
    keep = tin.all(1)
    cross = (~keep) & tin.any(1)
    new_tris, src = [tri[keep]], [np.nonzero(keep)[0]]
    added_pts = []
    base = len(clip)
    if cross.any():
        # clip the few crossing triangles against w = eps (Sutherland–Hodgman), interpolate clip coords
        ci = np.nonzero(cross)[0]
        extra_tri, extra_src = [], []
        newp = []
        for t in ci:
            vs = tri[t]
            poly = []
            for k in range(3):
                a, b = vs[k], vs[(k + 1) % 3]
                ina, inb = w[a] > eps, w[b] > eps
                if ina:
                    poly.append(('v', a))
                if ina != inb:
                    f = (eps - w[a]) / (w[b] - w[a])
                    newp.append((a, b, f))
                    poly.append(('n', base + len(newp) - 1))
            ids = [p[1] for p in poly]
            for k in range(1, len(ids) - 1):
                extra_tri.append([ids[0], ids[k], ids[k + 1]])
                extra_src.append(t)
        if extra_tri:
            new_tris.append(np.array(extra_tri, np.int64)); src.append(np.array(extra_src))
            added_pts = newp
    tri2 = np.concatenate(new_tris)
    src = np.concatenate(src)
    if added_pts:
        a = np.array([p[0] for p in added_pts]); b = np.array([p[1] for p in added_pts]); f = np.array([p[2] for p in added_pts])[:, None]
        clip = np.concatenate([clip, clip[a] + (clip[b] - clip[a]) * f])
        lerp = (a, b, f.astype(np.float32))
    else:
        lerp = None
    w = np.maximum(clip[:, 3], eps)
    invw = 1 / w
    x = (clip[:, 0] * invw * 0.5 + 0.5) * cam.W
    y = (0.5 - clip[:, 1] * invw * 0.5) * cam.H
    z = clip[:, 2] * invw
    xyzw = np.stack([x, y, z, invw], 1).astype(np.float32)
    return xyzw, tri2, src, lerp


def _lerp_attr(arr, lerp):
    if lerp is None:
        return arr
    a, b, f = lerp
    return np.concatenate([arr, arr[a] + (arr[b] - arr[a]) * f])


# ---------------------------------------------------------------- texture sampling
def _wrap(x, n, mode):
    if mode == 33071:      # clamp
        return np.clip(x, 0, n - 1)
    if mode == 33648:      # mirror
        p = np.mod(x, 2 * n)
        return np.where(p >= n, 2 * n - 1 - p, p)
    return np.mod(x, n)


def sample(tex, uv, lod=None):
    """Bilinear (trilinear if lod given) sample of a Texture at uv (n,2) -> (n,4) float."""
    mips = tex.mips if lod is not None else [tex.img]
    if lod is None:
        return _bilinear(mips[0], uv, tex)
    lod = np.clip(lod, 0, len(mips) - 1)
    l0 = np.floor(lod).astype(np.int32)
    f = (lod - l0)[:, None]
    out = np.zeros((len(uv), 4), np.float32)
    for L in np.unique(l0):
        m = l0 == L
        s0 = _bilinear(mips[L], uv[m], tex)
        if L + 1 < len(mips):
            s1 = _bilinear(mips[L + 1], uv[m], tex)
            out[m] = s0 + (s1 - s0) * f[m]
        else:
            out[m] = s0
    return out


def _bilinear(img, uv, tex):
    h, w = img.shape[:2]
    x = uv[:, 0] * w - 0.5
    y = uv[:, 1] * h - 0.5
    x0 = np.floor(x); y0 = np.floor(y)
    fx = (x - x0)[:, None].astype(np.float32); fy = (y - y0)[:, None].astype(np.float32)
    x0 = x0.astype(np.int64); y0 = y0.astype(np.int64)
    xa, xb = _wrap(x0, w, tex.wrap_s), _wrap(x0 + 1, w, tex.wrap_s)
    ya, yb = _wrap(y0, h, tex.wrap_t), _wrap(y0 + 1, h, tex.wrap_t)
    c00 = img[ya, xa]; c10 = img[ya, xb]; c01 = img[yb, xa]; c11 = img[yb, xb]
    return (c00 * (1 - fx) + c10 * fx) * (1 - fy) + (c01 * (1 - fx) + c11 * fx) * fy


# ---------------------------------------------------------------- shading helpers
def _ggx(N, V, L, rough, F0):
    H = normalize(V + L)
    NdL = np.clip(np.sum(N * L, -1), 0, 1)
    NdV = np.clip(np.sum(N * V, -1), 1e-4, 1)
    NdH = np.clip(np.sum(N * H, -1), 0, 1)
    VdH = np.clip(np.sum(V * H, -1), 0, 1)
    a = np.maximum(rough * rough, 0.002)
    a2 = a * a
    D = a2 / (np.pi * (NdH * NdH * (a2 - 1) + 1) ** 2 + 1e-9)
    k = (rough + 1) ** 2 / 8
    G = (NdV / (NdV * (1 - k) + k)) * (NdL / (NdL * (1 - k) + k + 1e-9))
    F = F0 + (1 - F0) * ((1 - VdH) ** 5)[:, None]
    spec = (D * G / (4 * NdV * NdL + 1e-4))[:, None] * F
    return spec, NdL


def _box1d(a, r, axis):
    """Box blur of radius r along axis using cumulative sums (edge-clamped)."""
    if r < 1:
        return a
    n = a.shape[axis]
    pad = [(0, 0)] * a.ndim; pad[axis] = (r + 1, r)
    ap = np.pad(a, pad, mode='edge')
    c = np.cumsum(ap, axis=axis, dtype=np.float64)
    hi = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
    lo = np.take(c, np.arange(0, n), axis=axis)
    return ((hi - lo) / (2 * r + 1)).astype(np.float32)


def _gauss_blur(img, sigma):
    """Approximate gaussian blur (3 box passes) on (H,W[,C]) float arrays."""
    if sigma <= 0:
        return img
    r = max(1, int(round(sigma * 0.9)))
    out = np.asarray(img, np.float32)
    for _ in range(3):
        out = _box1d(_box1d(out, r, 0), r, 1)
    return out


def bloom(rgb, threshold=1.0, sigma=18, strength=0.6, levels=3):
    """Additive HDR bloom: returns rgb + glow."""
    lum = rgb.max(-1)
    hi = rgb * np.clip((lum - threshold) / max(threshold, 1e-3), 0, 4)[..., None]
    glow = np.zeros_like(rgb)
    s = sigma
    for _ in range(levels):
        glow += _gauss_blur(hi, s)
        s *= 2
    return rgb + glow * (strength / levels)


def tonemap(rgb, exposure=1.0, mode='aces'):
    x = np.asarray(rgb, np.float32) * exposure
    if mode == 'aces':
        a, b, c, d, e = 2.51, 0.03, 2.43, 0.59, 0.14
        x = np.clip((x * (a * x + b)) / (x * (c * x + d) + e), 0, 1)
    else:
        x = np.clip(x, 0, 1)
    return linear_to_srgb(x)


def save(rgb01, path, alpha=None):
    im = (np.clip(rgb01, 0, 1) * 255 + 0.5).astype(np.uint8)
    if alpha is not None:
        im = np.concatenate([im, (np.clip(alpha, 0, 1) * 255 + 0.5).astype(np.uint8)[..., None]], -1)
        Image.fromarray(im, 'RGBA').save(path)
    else:
        Image.fromarray(im, 'RGB').save(path)


# ---------------------------------------------------------------- main render
def _shadow_map(scene, xyz_world_fn, light, res):
    """Orthographic depth map from the light. Returns (depth map, light view-proj matrix, texel size)."""
    d = light.dir
    center = (scene.lo + scene.hi) / 2
    radius = np.linalg.norm(scene.hi - scene.lo) / 2 * 1.05
    up = np.array([0, 1, 0]) if abs(d[1]) < 0.95 else np.array([1, 0, 0])
    cam = Camera.look_at(center + d * radius * 3, center, up, W=res, H=res, near=radius * 1.5, far=radius * 4.6, ortho=True, ortho_h=radius * 2)
    clip = _project(cam, scene.pos)
    xyzw, tri, _, _ = _clip_and_screen(cam, clip, scene.tri, None)
    depth = np.full(res * res, np.inf, np.float32)
    _lib.rasterize_depth(len(xyzw), _f32(xyzw).ctypes.data_as(_fp), len(tri), _i32(tri).ctypes.data_as(_ip), res, res, depth.ctypes.data_as(_fp))
    return depth.reshape(res, res), cam, radius * 2 / res


def _shadow_lookup(depth_map, cam, pos, nrm, light, texel, softness):
    res = depth_map.shape[0]
    bias = texel * 1.5
    p = pos + nrm * bias * 2 + light.dir * bias
    clip = _project(cam, p.astype(np.float32))
    x = (clip[:, 0] * 0.5 + 0.5) * res; y = (0.5 - clip[:, 1] * 0.5) * res; z = clip[:, 2]
    vis = np.zeros(len(pos), np.float32)
    taps = 0
    r = softness
    for dx in (-r, 0, r):
        for dy in (-r, 0, r):
            xi = np.clip((x + dx).astype(np.int64), 0, res - 1); yi = np.clip((y + dy).astype(np.int64), 0, res - 1)
            vis += (z <= depth_map[yi, xi] + 1e-4).astype(np.float32)
            taps += 1
    vis /= taps
    return vis


def _ssao(depth_view, normal_view, cam, radius, samples=16, seed=1):
    """Hemisphere SSAO on view-space depth (positive distance) and view-space normals. Returns ao in [0,1]."""
    H, W = depth_view.shape
    valid = np.isfinite(depth_view)
    if not valid.any():
        return np.ones((H, W), np.float32)
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    t = 1 / cam.proj[1, 1]
    ndc_x = (xs + 0.5) / W * 2 - 1; ndc_y = 1 - (ys + 0.5) / H * 2
    dz = np.where(valid, depth_view, 1.0)
    P = np.stack([ndc_x * t * (W / H) * dz, ndc_y * t * dz, -dz], -1)   # view-space positions
    rng = np.random.default_rng(seed)
    occ = np.zeros((H, W), np.float32)
    cnt = 0
    fx = cam.proj[0, 0]; fy = cam.proj[1, 1]
    R = rng.normal(size=(H, W, 3)).astype(np.float32); R /= np.linalg.norm(R, axis=-1, keepdims=True)   # per-pixel reflection vector
    for i in range(samples):
        v = rng.normal(size=3); v /= np.linalg.norm(v)
        v = (v * (0.25 + 0.75 * (i + 1) / samples) * radius).astype(np.float32)
        vp = v[None, None, :] - 2 * np.sum(R * v, -1, keepdims=True) * R          # householder reflection -> per-pixel random direction
        vp = np.where(np.sum(normal_view * vp, -1, keepdims=True) < 0, -vp, vp)
        s = P + vp + normal_view * radius * 0.05
        sz = -s[..., 2]
        sx = ((s[..., 0] * fx / np.maximum(sz, 1e-6)) * 0.5 + 0.5) * W
        sy = (0.5 - (s[..., 1] * fy / np.maximum(sz, 1e-6)) * 0.5) * H
        xi = np.clip(sx.astype(np.int64), 0, W - 1); yi = np.clip(sy.astype(np.int64), 0, H - 1)
        scene_z = depth_view[yi, xi]
        diff = sz - scene_z
        occluded = (diff > radius * 0.03) & np.isfinite(scene_z)
        rangecheck = np.clip(radius / np.maximum(np.abs(diff), 1e-6), 0, 1)
        occ += occluded * rangecheck
        cnt += 1
    ao = 1 - occ / cnt
    ao = np.where(valid, ao, 1.0)
    ao = _gauss_blur(ao, 3.0)
    return np.clip(ao, 0, 1).astype(np.float32)


def render(prims, cam, lights=None, ss=2, model_matrix=None, ambient=((0.55, 0.45, 0.28), (0.12, 0.09, 0.07)), cull=False,
           env_spec=(0.9, 0.75, 0.45), ao_strength=1.0, ao_radius=None, rim=((1.0, 0.85, 0.5), 0.6, 2.5),
           emissive_boost=1.0, extra_emissive=None, scene=None, want=('rgb', 'alpha', 'depth', 'normal', 'emissive', 'pos', 'albedo', 'ao', 'shadow', 'mat'),
           verbose=False):
    """Render prims with camera cam. lights: list of Light (default key+fill+rim).
    ambient = (sky colour, ground colour) hemisphere; env_spec = colour of a fake specular environment.
    extra_emissive(pos, nrm, V) -> (n,3) emissive to add (e.g. eye glow). cull=True honours single-sided materials.
    Returns dict of buffers at cam.W x cam.H (rendered at ss× and box-downsampled)."""
    import time
    t0 = time.time()
    lights = lights or [Light.key(), Light.fill(), Light.rim()]
    sc = scene or Scene(prims, model_matrix)
    hc = cam.scaled(ss)
    tflag_all = sc.tflag if cull else np.ones_like(sc.tflag)      # cull=False: draw both sides (safe for imported meshes)
    W, H = hc.W, hc.H
    # project + clip
    clip = _project(hc, sc.pos)
    xyzw, tri, src, lerp = _clip_and_screen(hc, clip, sc.tri, None)
    tmat = sc.tmat[src]; tflag = tflag_all[src]
    uvs = _lerp_attr(sc.uv, lerp)
    # alpha-cutout textures
    nmat = len(sc.mats)
    atex_ptrs = (_fp * nmat)()
    aw = np.zeros(nmat, np.int32); ah = np.zeros(nmat, np.int32); acut = np.zeros(nmat, np.float32)
    keep_alive = []
    for i, m in enumerate(sc.mats):
        if m.alpha_mode in ('MASK', 'BLEND') and m.base_tex is not None:
            a = np.ascontiguousarray(m.base_tex.tex.img[..., 3] * m.base_color[3], np.float32)
            keep_alive.append(a)
            atex_ptrs[i] = a.ctypes.data_as(_fp); ah[i], aw[i] = a.shape; acut[i] = m.alpha_cutoff if m.alpha_mode == 'MASK' else 0.5
        else:
            atex_ptrs[i] = ctypes.cast(None, _fp)
    depth = np.full(W * H, np.inf, np.float32); tid = np.full(W * H, -1, np.int32)
    bary = np.zeros(W * H * 2, np.float32); facing = np.zeros(W * H, np.int8)
    _lib.rasterize(len(xyzw), _f32(xyzw).ctypes.data_as(_fp), _f32(uvs).ctypes.data_as(_fp), len(tri), _i32(tri).ctypes.data_as(_ip),
                   _i32(tflag).ctypes.data_as(_ip), _i32(tmat).ctypes.data_as(_ip), nmat, atex_ptrs, aw.ctypes.data_as(_ip), ah.ctypes.data_as(_ip), acut.ctypes.data_as(_fp),
                   W, H, depth.ctypes.data_as(_fp), tid.ctypes.data_as(_ip), bary.ctypes.data_as(_fp), facing.ctypes.data_as(ctypes.POINTER(ctypes.c_int8)))
    t1 = time.time()
    cov = tid >= 0
    pix = np.nonzero(cov)[0]
    n = len(pix)
    if verbose:
        print(f'raster {t1 - t0:.2f}s  covered {n:,}/{W * H:,}')
    out = {}
    rgb = np.zeros((W * H, 3), np.float32); emis = np.zeros((W * H, 3), np.float32); alb = np.zeros((W * H, 3), np.float32)
    nrm_out = np.zeros((W * H, 3), np.float32); pos_out = np.zeros((W * H, 3), np.float32)
    ao_out = np.ones(W * H, np.float32); sh_out = np.ones(W * H, np.float32); mat_out = np.full(W * H, -1, np.int32)
    if n:
        t = tid[pix]
        b1 = bary[pix * 2]; b2 = bary[pix * 2 + 1]; b0 = 1 - b1 - b2
        vi = tri[t]                                    # (n,3) vertex ids (may include clipped verts)
        pos_all = _lerp_attr(sc.pos, lerp); nrm_all = _lerp_attr(sc.nrm, lerp); tan_all = _lerp_attr(sc.tan, lerp); col_all = _lerp_attr(sc.col, lerp)

        def interp(arr):
            return arr[vi[:, 0]] * b0[:, None] + arr[vi[:, 1]] * b1[:, None] + arr[vi[:, 2]] * b2[:, None]
        P = interp(pos_all); N = normalize(interp(nrm_all)); UV = interp(uvs); T = interp(tan_all); C = interp(col_all)
        eye32 = hc.eye.astype(np.float32)
        V = normalize(eye32[None, :] - P) if not hc.ortho else np.tile(-hc.inv_view[:3, 2].astype(np.float32), (n, 1))
        # orient normals toward the viewer where the surface is seen from behind (double-sided / inverted normals)
        fc = np.where(np.sum(N * V, -1) < 0, -1.0, 1.0).astype(np.float32)
        N = N * fc[:, None]
        Ng = N.copy()                                  # geometric normal (before normal mapping) for SSAO
        mid = tmat[t]
        # per-triangle LOD: texel/pixel ratio
        xy = xyzw[:, :2]
        sa = 0.5 * np.abs((xy[vi[:, 1], 0] - xy[vi[:, 0], 0]) * (xy[vi[:, 2], 1] - xy[vi[:, 0], 1]) - (xy[vi[:, 2], 0] - xy[vi[:, 0], 0]) * (xy[vi[:, 1], 1] - xy[vi[:, 0], 1]))
        ua = 0.5 * np.abs((uvs[vi[:, 1], 0] - uvs[vi[:, 0], 0]) * (uvs[vi[:, 2], 1] - uvs[vi[:, 0], 1]) - (uvs[vi[:, 2], 0] - uvs[vi[:, 0], 0]) * (uvs[vi[:, 1], 1] - uvs[vi[:, 0], 1]))
        base = np.zeros((n, 4), np.float32); mr = np.zeros((n, 2), np.float32); em = np.zeros((n, 3), np.float32); occ = np.ones(n, np.float32)
        Nn = N.copy()
        for i, m in enumerate(sc.mats):
            sel = np.nonzero(mid == i)[0]
            if not len(sel):
                continue
            uv = UV[sel]
            bc = np.tile(m.base_color, (len(sel), 1))
            if m.base_tex is not None:
                tx = m.base_tex.tex
                th, tw = tx.img.shape[:2]
                lod = 0.5 * np.log2(np.maximum(ua[sel] * tw * th, 1e-12) / np.maximum(sa[sel], 1e-6))
                s = sample(tx, m.base_tex.uv(uv), lod)
                bc = bc * np.concatenate([srgb_to_linear(s[:, :3]), s[:, 3:4]], 1)
            bc[:, :3] *= C[sel, :3]
            base[sel] = bc
            m_r = np.tile([m.metallic, m.roughness], (len(sel), 1)).astype(np.float32)
            if m.mr_tex is not None:
                tx = m.mr_tex.tex; th, tw = tx.img.shape[:2]
                lod = 0.5 * np.log2(np.maximum(ua[sel] * tw * th, 1e-12) / np.maximum(sa[sel], 1e-6))
                s = sample(tx, m.mr_tex.uv(uv), lod)
                m_r = m_r * np.stack([s[:, 2], s[:, 1]], 1)
            mr[sel] = m_r
            e = np.tile(m.emissive, (len(sel), 1)).astype(np.float32)
            if m.emis_tex is not None:
                tx = m.emis_tex.tex; th, tw = tx.img.shape[:2]
                lod = 0.5 * np.log2(np.maximum(ua[sel] * tw * th, 1e-12) / np.maximum(sa[sel], 1e-6))
                s = sample(tx, m.emis_tex.uv(uv), lod)
                e = e * srgb_to_linear(s[:, :3])
            em[sel] = e
            if m.occl_tex is not None:
                tx = m.occl_tex.tex
                s = sample(tx, m.occl_tex.uv(uv), None)
                occ[sel] = 1 - m.occl_tex.scale * (1 - s[:, 0])
            if m.normal_tex is not None and np.any(np.abs(T[sel, :3]).sum(1) > 0):
                tx = m.normal_tex.tex; th, tw = tx.img.shape[:2]
                lod = 0.5 * np.log2(np.maximum(ua[sel] * tw * th, 1e-12) / np.maximum(sa[sel], 1e-6))
                s = sample(tx, m.normal_tex.uv(uv), lod)
                tn = s[:, :3] * 2 - 1
                tn[:, :2] *= m.normal_tex.scale
                tn = normalize(tn)
                Ns = N[sel]; Ts = T[sel, :3] * fc[sel][:, None]; Ts = normalize(Ts - Ns * np.sum(Ns * Ts, 1, keepdims=True))
                Bs = np.cross(Ns, Ts) * T[sel, 3:4]
                Nn[sel] = normalize(Ts * tn[:, 0:1] + Bs * tn[:, 1:2] + Ns * tn[:, 2:3])
        N = Nn
        albedo = base[:, :3]; metal = np.clip(mr[:, 0], 0, 1); rough = np.clip(mr[:, 1], 0.03, 1)
        F0 = 0.04 * (1 - metal)[:, None] + albedo * metal[:, None]
        diff_col = albedo * (1 - metal)[:, None]
        # shadows (key light)
        shadow = np.ones(n, np.float32)
        for L in lights:
            if L.shadow:
                dm, lcam, texel = _shadow_map(sc, None, L, L.shadow_res)
                shadow = _shadow_lookup(dm, lcam, P, N, L, texel, L.softness)
                break
        # SSAO at half of the supersampled res
        ao = np.ones(n, np.float32)
        if ao_strength > 0:
            k = 2
            dv = depth[pix]
            # view-space depth: reconstruct from world pos
            Pv = (P - eye32[None, :]) @ hc.inv_view[:3, :3].astype(np.float32)
            zview = -Pv[:, 2]
            Dfull = np.full(W * H, np.inf, np.float32); Dfull[pix] = zview
            Nv = Ng @ hc.inv_view[:3, :3].astype(np.float32)
            Nfull = np.zeros((W * H, 3), np.float32); Nfull[pix] = Nv
            Dh = Dfull.reshape(H, W)[::k, ::k]; Nh = Nfull.reshape(H, W, 3)[::k, ::k]
            r = ao_radius or np.linalg.norm(sc.hi - sc.lo) * 0.03
            aoh = _ssao(Dh, Nh, hc, r)
            aof = np.repeat(np.repeat(aoh, k, 0), k, 1)[:H, :W].reshape(-1)
            ao = 1 - ao_strength * (1 - aof[pix])
        ao = ao * occ
        # lighting
        col = np.zeros((n, 3), np.float32)
        sky, ground = np.array(ambient[0], np.float32), np.array(ambient[1], np.float32)
        hemi = ((0.5 + 0.5 * N[:, 1:2]) * sky + (0.5 - 0.5 * N[:, 1:2]) * ground).astype(np.float32)
        col += diff_col * hemi * ao[:, None]
        NdV = np.clip(np.sum(N * V, -1), 0, 1)
        Fr = F0 + (1 - F0) * ((1 - NdV) ** 5)[:, None]
        env = np.array(env_spec, np.float32)
        col += Fr * env * ((1 - rough * 0.85)[:, None]) * ao[:, None] * 0.6   # fake env reflection
        for L in lights:
            spec, NdL = _ggx(N, V, L.dir[None, :].astype(np.float32), rough, F0)
            vis = shadow if L.shadow else 1.0
            col += (diff_col / np.pi + spec) * (NdL * vis)[:, None] * L.color[None, :]
        if rim is not None:
            rc, rp, rs = np.array(rim[0], np.float32), rim[1], rim[2]
            f = (1 - NdV) ** rs
            col += rc * (f * rp)[:, None] * (0.3 + 0.7 * ao)[:, None]
        e_total = em * emissive_boost
        if extra_emissive is not None:
            e_total = e_total + extra_emissive(P, N, V)
        col += e_total
        rgb[pix] = col; emis[pix] = e_total; alb[pix] = albedo; nrm_out[pix] = N; pos_out[pix] = P; ao_out[pix] = ao; sh_out[pix] = shadow; mat_out[pix] = mid
    t2 = time.time()
    if verbose:
        print(f'shade {t2 - t1:.2f}s')
    # downsample
    def ds(a):
        a = a.reshape(H, W, -1)
        return a.reshape(H // ss, ss, W // ss, ss, a.shape[-1]).mean((1, 3))
    alpha = cov.astype(np.float32)
    A = ds(alpha)[..., 0]
    out['alpha'] = A
    safe = np.maximum(A, 1e-6)[..., None]
    out['rgb'] = ds(rgb) / safe * (A[..., None] > 0)        # premultiplied -> straight
    out['emissive'] = ds(emis) / safe * (A[..., None] > 0)
    out['albedo'] = ds(alb) / safe * (A[..., None] > 0)
    out['normal'] = normalize(ds(nrm_out))
    out['pos'] = ds(pos_out) / safe
    out['ao'] = ds(ao_out)[..., 0]
    out['shadow'] = ds(sh_out)[..., 0]
    dview = np.where(cov, np.linalg.norm(pos_out - hc.eye.astype(np.float32)[None, :], axis=1), np.inf).astype(np.float32).reshape(H, W)
    dmin = dview.reshape(H // ss, ss, W // ss, ss).min((1, 3))
    out['depth'] = dmin
    out['mat'] = mat_out.reshape(H, W)[::ss, ::ss]
    out['time'] = dict(raster=t1 - t0, shade=t2 - t1, total=time.time() - t0)
    return out


def composite_over(rgb, alpha, bg):
    """Straight-alpha composite rgb over bg (both linear)."""
    a = alpha[..., None]
    return rgb * a + bg * (1 - a)


def turntable(prims, center, radius_dist, n=8, fov=35, W=390, H=844, elev_deg=8, lights=None, ss=1, **kw):
    """Render n views around +Y. Returns list of (rgb_srgb, alpha)."""
    outs = []
    for i in range(n):
        a = 2 * math.pi * i / n
        eye = center + np.array([math.sin(a), math.tan(math.radians(elev_deg)), math.cos(a)]) * radius_dist
        cam = Camera.look_at(eye, center, fov_y=fov, W=W, H=H)
        o = render(prims, cam, lights, ss=ss, **kw)
        outs.append((tonemap(bloom(o['rgb'], 1.2, 10, 0.5, 2)), o['alpha']))
    return outs
