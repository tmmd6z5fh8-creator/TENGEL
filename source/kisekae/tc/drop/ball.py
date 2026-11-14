# 玉（折り紙ふうの 多面体・赤い 紙）：盤の 上を ころがる 向き（画面に 垂直な 軸）で 回した コマを ならべた 絵
#   python3 -I ball.py <出力の PNG>   → 8×4 コマ（1コマ 96×96・玉の 半径 44）・明かりは 台と 同じ
import sys, math
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from cam import *
from PIL import Image

N_FR, CELL, RAD = 32, 96, 44
COLS, ROWS = 8, 4
BASE = np.array([236, 74, 86], np.float64) / 255          # 屋根・ボタンと 同じ 赤


def icosphere(level=1):
    t = (1 + 5 ** 0.5) / 2
    V = np.array([[-1, t, 0], [1, t, 0], [-1, -t, 0], [1, -t, 0], [0, -1, t], [0, 1, t], [0, -1, -t], [0, 1, -t], [t, 0, -1], [t, 0, 1], [-t, 0, -1], [-t, 0, 1]], float)
    V /= np.linalg.norm(V, axis=1, keepdims=True)
    F = [[0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11], [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8], [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9], [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1]]
    V = [v for v in V]
    for _ in range(level):
        cache = {}; F2 = []

        def mid(a, b):
            k = (min(a, b), max(a, b))
            if k not in cache:
                m = V[a] + V[b]; V.append(m / np.linalg.norm(m)); cache[k] = len(V) - 1
            return cache[k]
        for a, b, c in F:
            ab, bc, ca = mid(a, b), mid(b, c), mid(c, a)
            F2 += [[a, ab, ca], [b, bc, ab], [c, ca, bc], [ab, bc, ca]]
        F = F2
    return np.array(V), np.array(F)


def rot(ax, deg):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    x, y, z = ax
    return np.array([[c + x * x * (1 - c), x * y * (1 - c) - z * s, x * z * (1 - c) + y * s], [y * x * (1 - c) + z * s, c + y * y * (1 - c), y * z * (1 - c) - x * s], [z * x * (1 - c) - y * s, z * y * (1 - c) + x * s, c + z * z * (1 - c)]])


def make():
    V, F = icosphere(1)
    V = V @ rot((0.3, 0.8, 0.52) / np.linalg.norm((0.3, 0.8, 0.52)), 37.0).T          # かたよらない 向きに
    rng = np.random.default_rng(5)
    P = V[F].reshape(-1, 3)
    fn = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]]); fn /= np.linalg.norm(fn, axis=1, keepdims=True)
    N = np.repeat(fn, 3, 0)
    tint = 1 + rng.uniform(-0.10, 0.10, len(F))
    light = rng.random(len(F)) < 0.16                                              # ところどころ 明るい 面（紙の 折り目）
    lin = RS.srgb_to_linear(np.clip(BASE[None, :] * tint[:, None] + np.where(light, 0.10, 0.0)[:, None], 0, 1))
    col = np.concatenate([np.repeat(lin, 3, 0), np.ones((len(P), 1))], 1).astype(np.float32)
    mat = GLB.Material({'pbrMetallicRoughness': {'baseColorFactor': [1, 1, 1, 1], 'metallicFactor': 0.0, 'roughnessFactor': 0.5}, 'doubleSided': False})
    idx = np.arange(len(P)).reshape(-1, 3)
    return P, N, idx, col, mat


def sheet():
    P, N, idx, col, mat = make()
    S = 4                                       # 4倍で 描いて もどす
    out = np.zeros((ROWS * CELL, COLS * CELL, 4), np.float32)
    half = CELL / 2 / RAD                       # コマの 半分（玉の 半径＝1）
    cam = RS.Camera.look_at((0, 0, 80.0), (0, 0, 0), fov_y=2 * math.degrees(math.atan(half / 80.0)), W=CELL * S // 2, H=CELL * S // 2, near=40.0, far=120.0)      # ほぼ 平行（描く 道具の 平行カメラは 光の 向きが 逆に なる ので 使わない）
    L = [RS.Light((-0.45, 0.62, 1.0), (1.0, 0.985, 0.96), 2.5), RS.Light((0.65, 0.2, 0.75), (0.92, 0.96, 1.0), 0.5), RS.Light((0.0, 1.0, 0.3), (1, 1, 1), 0.45)]      # 台と 同じ 向き（玉は 少し くっきり）
    for i in range(N_FR):
        M = rot((0, 0, 1), 360.0 * i / N_FR)
        p = GLB.Prim((P @ M.T).astype(np.float32), (N @ M.T).astype(np.float32), np.zeros((len(P), 2), np.float32), idx, mat, color=col)
        o = RS.render([p], cam, L, ss=2, ambient=((0.52, 0.50, 0.50), (0.25, 0.22, 0.22)), env_spec=(0.05, 0.05, 0.05), rim=None, ao_strength=0.0)
        rgb = RS.tonemap(o['rgb'], 1.0); a = o['alpha']
        # 下の ほうを 少し 暗く（盤に 近い がわ：台の 絵の かげと 合わせる）
        yy = np.linspace(-1, 1, rgb.shape[0])[:, None, None]
        rgb = rgb * (1 - 0.16 * np.clip(yy, 0, 1))
        h, w = a.shape
        im = Image.fromarray((np.dstack([np.clip(rgb, 0, 1), a]) * 255 + 0.5).astype(np.uint8), 'RGBA')
        r = np.asarray(im.resize((CELL, CELL), Image.LANCZOS)).astype(np.float32) / 255
        cy, cx = i // COLS, i % COLS
        out[cy * CELL:(cy + 1) * CELL, cx * CELL:(cx + 1) * CELL] = r
    return (np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)


if __name__ == '__main__':
    a = sheet()
    Image.fromarray(a, 'RGBA').save(sys.argv[1])
    al = a[:CELL, :CELL, 3]
    ys, xs = np.nonzero(al > 128)
    print('sheet', a.shape, 'frame0 bbox', xs.min(), xs.max(), ys.min(), ys.max())
