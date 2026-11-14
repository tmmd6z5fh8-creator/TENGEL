# 台の 3D を アプリ用の 絵に 描く（帯に 分けて 2倍で 描いて → 半分に：ふちが なめらか）
#   python3 -I drop_render.py <GLB> <出力の npz> [y0 y1（台の 座標：この 高さの 帯だけ）]
import sys, time
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from cam import *

K = 2            # 描く 倍率（あとで 半分に）
SS = 2           # その 上の 細かさ
BAND = 366       # 帯の 高さ（K倍の 画素）


def crop_cam(cam, x0, y0, w, h):
    W, H = cam.W, cam.H
    a, b = x0 / W * 2 - 1, (x0 + w) / W * 2 - 1
    c, d = 1 - (y0 + h) / H * 2, 1 - y0 / H * 2
    sx, cx = (b - a) / 2, (a + b) / 2; sy, cy = (d - c) / 2, (c + d) / 2
    M = np.array([[1 / sx, 0, 0, -cx / sx], [0, 1 / sy, 0, -cy / sy], [0, 0, 1, 0], [0, 0, 0, 1]])
    c2 = RS.Camera(cam.view, M @ cam.proj, w, h, cam.ortho); c2.near, c2.far, c2.fov_y = cam.near, cam.far, cam.fov_y
    return c2


def render_full(prims, rows=None, verbose=True):
    """→ dict（K倍の 大きさ）：a（明かり あり）・b（まわりの 光 だけ）・alpha・pos・normal・albedo。rows＝(r0, r1)：K倍の 画素の 行の はんい"""
    full = camera(K)
    W, H = full.W, full.H
    r0, r1 = rows or (0, H)
    out = {k: np.zeros((r1 - r0, W, 3), np.float32) for k in ('a', 'b', 'pos', 'normal', 'albedo')}
    out['alpha'] = np.zeros((r1 - r0, W), np.float32)
    L = lights(True); Z = [RS.Light((0, 0, 1), (0, 0, 0), 0.0)]
    sc = RS.Scene(prims)
    y = r0
    while y < r1:
        h = min(BAND, r1 - y)
        cam = crop_cam(full, 0, y, W, h)
        t0 = time.time()
        oa = RS.render(prims, cam, L, ss=SS, ambient=AMB, env_spec=(0.22, 0.22, 0.22), rim=None, ao_strength=0.0, scene=sc)
        ob = RS.render(prims, cam, Z, ss=SS, ambient=AMB, env_spec=(0.22, 0.22, 0.22), rim=None, ao_strength=0.0, scene=sc)
        s = slice(y - r0, y - r0 + h)
        out['a'][s] = oa['rgb']; out['b'][s] = ob['rgb']; out['alpha'][s] = oa['alpha']; out['pos'][s] = oa['pos']; out['normal'][s] = oa['normal']; out['albedo'][s] = oa['albedo']
        if verbose:
            print(f'band {y}-{y + h} {time.time() - t0:.1f}s', flush=True)
        y += h
    return out


def half(a, alpha=None):
    """2×2 の 平均（alpha が あれば 色は 重みつき）"""
    H, W = a.shape[:2]
    if alpha is None:
        return a.reshape(H // 2, 2, W // 2, 2, *a.shape[2:]).mean((1, 3))
    w = alpha[..., None] if a.ndim == 3 else alpha
    s = (a * w).reshape(H // 2, 2, W // 2, 2, *a.shape[2:]).sum((1, 3))
    n = w.reshape(H // 2, 2, W // 2, 2, *w.shape[2:]).sum((1, 3))
    return s / np.maximum(n, 1e-6)


def finish(o, rows=None):
    """K倍の バッファ → 仕上げの 大きさ（半分）：まわりの 光の 影（AO）を かけて 色に する"""
    A2 = o['alpha']
    al = half(A2)
    a, b = half(o['a'], A2), half(o['b'], A2)
    pos, nrm, alb = half(o['pos'], A2), half(o['normal'], A2), half(o['albedo'], A2)
    return dict(a=a, b=b, alpha=al, pos=pos, normal=nrm, albedo=alb)


def ao_map(pos, nrm, alpha):
    """仕上げの 大きさの まわりの 光の 影（全体の カメラ：左右 対称）"""
    cam = camera(1)
    eye = cam.eye.astype(np.float32); R = cam.inv_view[:3, :3].astype(np.float32)
    Pv = (pos - eye[None, None, :]) @ R
    zv = np.where(alpha > 0.02, -Pv[..., 2], np.inf).astype(np.float32)
    n = nrm / np.maximum(np.linalg.norm(nrm, axis=-1, keepdims=True), 1e-6)
    Nv = (n @ R).astype(np.float32)
    return RS._ssao(zv, Nv, cam, 2.24 * 0.03)


def color(f, ao, strength=0.75):
    k = (1 - strength * (1 - ao))[..., None]
    lin = f['b'] * k + (f['a'] - f['b'])
    return RS.tonemap(lin, 1.0)


if __name__ == '__main__':
    path, outp = sys.argv[1], sys.argv[2]
    m = GLB.load(path); prims = m.flatten()
    t0 = time.time()
    o = render_full(prims)
    f = finish(o)
    ao = ao_map(f['pos'], f['normal'], f['alpha'])
    rgb = color(f, ao)
    np.savez_compressed(outp, rgb=(np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8), alpha=(np.clip(f['alpha'], 0, 1) * 255 + 0.5).astype(np.uint8), z=f['pos'][..., 2].astype(np.float32),
                        albedo=(np.clip(f['albedo'], 0, 1) * 255 + 0.5).astype(np.uint8), ao=ao.astype(np.float32), a=f['a'].astype(np.float16), b=f['b'].astype(np.float16), nz=f['normal'][..., 2].astype(np.float16))
    # 見る 用・あとの 道具（paths.py）用の PNG（npz の rgb＋alpha と 同じ 中身）：<出力>.png
    from PIL import Image
    d = np.load(outp)
    Image.fromarray(np.dstack([d['rgb'], d['alpha']]), 'RGBA').save(__import__('os').path.splitext(outp)[0] + '.png')
    print('done', round(time.time() - t0, 1), 's', rgb.shape)
