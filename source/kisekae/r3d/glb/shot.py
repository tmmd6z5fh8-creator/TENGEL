# shot.py — camera presets and per-frame hooks for the 神様極的中 shots on a glb.py model.
#
#   import glb, shot
#   m = glb.load('kami_uma.glb'); prims = m.flatten()
#   info = shot.analyze(prims)                       # bbox, up axis, facing direction, head/legs slices
#   cam = shot.face_cam(info, W=780, H=1688)         # ③ front face close-up
#   cam = shot.hoof_cam(info, W=780, H=1688)         # ⑥ low-angle hoof close-up
#   cam = shot.rear_cam(info, W=780, H=1688)         # ⑩ full body, facing screen-LEFT
#   fr = shot.frame(prims, cam, t=None, eyes=shot.find_eyes(prims, info), glow=6.0)   # dict: rgb, alpha, depth, emissive …
#
# frame() returns linear HDR buffers (straight alpha). Compositors (W/gk, W/gk2, W/gk3) put their own
# backgrounds behind (alpha) and effects in front / behind using depth, then tonemap.
import math
import numpy as np
import glb
from raster import Camera, Light, Scene, render, normalize, sample

UP = np.array([0, 1, 0], np.float64)


def analyze(prims, facing=None, up=UP):
    """Bounding box and a guess at where the head and the front legs are.
    facing: optional world direction the horse faces; default = horizontal vector from body centre to head centre."""
    P = np.concatenate([p.pos for p in prims]).astype(np.float64)
    lo, hi = P.min(0), P.max(0)
    size = hi - lo
    h = size[1]
    head_mask = P[:, 1] > lo[1] + 0.65 * h
    body_mask = (P[:, 1] > lo[1] + 0.25 * h) & (P[:, 1] < lo[1] + 0.65 * h)
    head_c = P[head_mask].mean(0) if head_mask.any() else (lo + hi) / 2
    body_c = P[body_mask].mean(0) if body_mask.any() else (lo + hi) / 2
    if facing is None:
        f = head_c - body_c; f[1] = 0
        if np.linalg.norm(f) < 1e-6 * max(size.max(), 1e-9):
            f = np.array([0, 0, 1.0])
        facing = f / np.linalg.norm(f)
    facing = np.array(facing, np.float64); facing /= np.linalg.norm(facing)
    right = np.cross(facing, up); right /= np.linalg.norm(right)
    head_pts = P[head_mask]
    head_lo, head_hi = (head_pts.min(0), head_pts.max(0)) if head_mask.any() else (lo, hi)
    # front legs: lowest 18%, farthest along facing
    leg_mask = P[:, 1] < lo[1] + 0.18 * h
    legs = P[leg_mask]
    along = legs @ facing
    front = legs[along > np.percentile(along, 70)] if len(legs) else legs
    hoof_c = front.mean(0) if len(front) else lo
    return dict(lo=lo, hi=hi, center=(lo + hi) / 2, size=size, diag=float(np.linalg.norm(size)), facing=facing, right=right, up=up,
                head_c=head_c, head_lo=head_lo, head_hi=head_hi, body_c=body_c, hoof_c=hoof_c, n=len(P))


def _fit_dist(extent, fov_y, aspect, margin=1.15):
    """Camera distance so that a sphere of radius extent fits vertically (or horizontally) with margin."""
    r = extent * margin
    d_v = r / math.tan(math.radians(fov_y) / 2)
    d_h = r / (math.tan(math.radians(fov_y) / 2) * aspect)
    return max(d_v, d_h)


def face_cam(info, W=780, H=1688, fov_y=28.0, yaw_deg=0.0, pitch_deg=4.0, zoom=1.0, look_shift=(0.0, 0.0)):
    """③: front view of the head. yaw_deg turns the camera around the head (0 = dead front), pitch looks slightly down."""
    hc = (info['head_lo'] + info['head_hi']) / 2
    ext = max(np.linalg.norm(info['head_hi'] - info['head_lo']) / 2, 1e-6)
    f, r, u = info['facing'], info['right'], info['up']
    yaw = math.radians(yaw_deg); pitch = math.radians(pitch_deg)
    d = (f * math.cos(yaw) + r * math.sin(yaw)) * math.cos(pitch) + u * math.sin(pitch)
    dist = _fit_dist(ext, fov_y, W / H, 1.05) / zoom
    target = hc + r * look_shift[0] * ext + u * look_shift[1] * ext
    return Camera.look_at(target + d * dist, target, u, fov_y, W, H)


def hoof_cam(info, W=780, H=1688, fov_y=30.0, side_deg=35.0, elev_deg=-12.0, zoom=1.0):
    """⑥: low camera on the front hoof, from the front-side, looking slightly up."""
    hc = info['hoof_c']
    ext = info['size'][1] * 0.12
    f, r, u = info['facing'], info['right'], info['up']
    a = math.radians(side_deg); e = math.radians(elev_deg)
    d = (f * math.cos(a) + r * math.sin(a)) * math.cos(e) + u * math.sin(e)
    dist = _fit_dist(ext, fov_y, W / H, 1.2) / zoom
    return Camera.look_at(hc + d * dist, hc, u, fov_y, W, H)


def rear_cam(info, W=780, H=1688, fov_y=32.0, face_left=True, elev_deg=6.0, zoom=1.0, toward_deg=18.0):
    """⑩: full body. The horse faces screen-left when face_left (camera on the horse's left side, slightly toward the front)."""
    c = info['center']
    ext = info['diag'] / 2
    f, r, u = info['facing'], info['right'], info['up']
    side = -r if face_left else r          # camera on the horse's left => horse's nose points to screen-left
    a = math.radians(toward_deg); e = math.radians(elev_deg)
    d = (side * math.cos(a) + f * math.sin(a)) * math.cos(e) + u * math.sin(e)
    dist = _fit_dist(ext, fov_y, W / H, 1.1) / zoom
    return Camera.look_at(c + d * dist, c, u, fov_y, W, H)


def mirror_x_matrix(info):
    """Model matrix that mirrors the horse across the plane through its centre perpendicular to 'right' (flips facing left<->right)."""
    r = info['right'][:, None]
    M = np.eye(4)
    M[:3, :3] = np.eye(3) - 2 * r @ r.T
    c = info['center']
    M[:3, 3] = c - M[:3, :3] @ c
    return M


def _cluster_eyes(Q, info):
    side = (Q - info['head_c']) @ info['right']
    out = []
    for mask in (side < 0, side >= 0):
        if mask.sum() >= 3:
            c = Q[mask].mean(0)
            rad = float(np.percentile(np.linalg.norm(Q[mask] - c, axis=1), 80))
            out.append((c, max(rad, info['size'][1] * 0.01)))
    return out


def find_eyes(prims, info, target_rgb=(1.0, 0.85, 0.2), tol=0.28, use_emissive=True, samples_per_tri=7):
    """Guess eye centres from the textures: surface points (vertices, edge midpoints, centroids of each head triangle)
    whose texture colour (emissive if the material has one, else albedo) is near target_rgb, split left/right.
    Returns list of (centre xyz, radius) — 0, 1 or 2 entries. See also find_eyes_from_frame()."""
    pts, cols = [], []
    bary = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1], [.5, .5, 0], [0, .5, .5], [.5, 0, .5], [1 / 3, 1 / 3, 1 / 3]], np.float32)[:samples_per_tri]
    for p in prims:
        m = p.mat
        tex = m.emis_tex if (use_emissive and m.emis_tex is not None) else m.base_tex
        if tex is None:
            continue
        head_v = p.pos[:, 1] > info['lo'][1] + 0.65 * info['size'][1]
        tri = p.idx[head_v[p.idx].any(1)]
        if not len(tri):
            continue
        P3 = p.pos[tri]; U3 = p.uv[tri]                       # (nt,3,3), (nt,3,2)
        Pq = np.einsum('kj,tjc->tkc', bary, P3).reshape(-1, 3)
        Uq = np.einsum('kj,tjc->tkc', bary, U3).reshape(-1, 2)
        s = sample(tex.tex, tex.uv(Uq), None)[:, :3]
        pts.append(Pq); cols.append(s)
    if not pts:
        return []
    P = np.concatenate(pts); C = np.concatenate(cols)
    d = np.linalg.norm(C - np.array(target_rgb), axis=1)
    sel = d < tol
    if sel.sum() < 3:
        return []
    return _cluster_eyes(P[sel], info)


def find_eyes_from_frame(fr, info, use='emissive', threshold=0.5, target_rgb=(1.0, 0.85, 0.2), tol=0.3):
    """Guess eye centres from a rendered front frame (shot.frame output): pixels whose emissive (use='emissive', max channel >
    threshold) or albedo (use='albedo', colour within tol of target_rgb) matches, using the frame's world positions."""
    if use == 'emissive':
        sel = fr['emissive'].max(-1) > threshold
    else:
        sel = np.linalg.norm(fr['albedo'] - np.array(target_rgb), axis=-1) < tol
    sel &= fr['alpha'] > 0.5
    if sel.sum() < 6:
        return []
    Q = fr['pos'][sel]
    return _cluster_eyes(Q, info)


def eye_glow(eyes, color=(1.0, 0.8, 0.3), strength=6.0, falloff=1.6):
    """extra_emissive hook: gold glow around eye centres (world-space spheres, soft edge)."""
    col = np.array(color, np.float32) * strength

    def fn(P, N, V):
        e = np.zeros((len(P), 3), np.float32)
        for c, r in eyes:
            d = np.linalg.norm(P - c, axis=1) / (r * falloff)
            w = np.clip(1 - d * d, 0, 1) ** 1.5
            e += w[:, None] * col[None, :]
        return e
    return fn


GOLD_LIGHTS = [Light.key((0.35, 0.85, 0.55), (1.0, 0.88, 0.62), 3.2, True, shadow_res=2048, softness=1.5),
               Light.fill((-0.8, 0.15, 0.45), (0.45, 0.5, 0.75), 0.35),
               Light.rim((0.15, 0.45, -1.0), (1.0, 0.78, 0.4), 2.8)]
GOLD_AMBIENT = ((0.6, 0.47, 0.25), (0.1, 0.07, 0.05))


def frame(prims, cam, t=None, model=None, lights=None, eyes=None, glow=6.0, ss=2, model_matrix=None, scene=None, **kw):
    """Render one frame. t: animation time (needs model=glb.Model to re-flatten); eyes: from find_eyes() or [(xyz, r), …].
    Returns the render() dict (rgb linear HDR straight alpha, alpha, depth, emissive, normal, pos, …)."""
    if t is not None and model is not None:
        prims = model.flatten(t=t)
        scene = None
    extra = eye_glow(eyes, strength=glow) if eyes else None
    return render(prims, cam, lights or GOLD_LIGHTS, ss=ss, model_matrix=model_matrix, ambient=GOLD_AMBIENT, extra_emissive=extra, scene=scene, **kw)


def orbit_cam(info, deg, W=390, H=844, fov_y=35.0, elev_deg=8.0, zoom=1.0):
    """Turntable camera around the whole model (deg = 0 is in front of the horse)."""
    c = info['center']; ext = info['diag'] / 2
    f, r, u = info['facing'], info['right'], info['up']
    a = math.radians(deg); e = math.radians(elev_deg)
    d = (f * math.cos(a) + r * math.sin(a)) * math.cos(e) + u * math.sin(e)
    dist = _fit_dist(ext, fov_y, W / H, 1.1) / zoom
    return Camera.look_at(c + d * dist, c, u, fov_y, W, H)
