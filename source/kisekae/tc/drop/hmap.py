# 正面から 見た 高さの 地図（正射影）を 作る：<glb> <出力 npz>
import sys
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from common import *
import glb as GLB
import raster as RS
X0, X1, Y0, Y1 = -0.60, 0.60, -1.00, 1.00
PX = 1500                                    # 1 単位 あたりの 画素


def hmap(path):
    m = GLB.load(path); prims = m.flatten()
    W, H = int(round((X1 - X0) * PX)), int(round((Y1 - Y0) * PX))
    cam = RS.Camera.look_at(((X0 + X1) / 2, (Y0 + Y1) / 2, 5.0), ((X0 + X1) / 2, (Y0 + Y1) / 2, 0.0), fov_y=28, W=W, H=H, ortho=True, ortho_h=(Y1 - Y0), near=0.5, far=20)
    o = RS.render(prims, cam, [RS.Light((0.3, 0.5, 1.0), (1, 1, 1), 2.0)], ss=1, ambient=((0.6, 0.6, 0.6), (0.3, 0.3, 0.3)), env_spec=(0.2, 0.2, 0.2), rim=((1, 1, 1), 0.0, 2.5), ao_strength=0.0)
    return o['pos'][..., 2].copy(), o['alpha'].copy(), o['albedo'].copy(), o['normal'].copy()


if __name__ == '__main__':
    z, a, alb, n = hmap(sys.argv[1])
    np.savez_compressed(sys.argv[2], z=z.astype(np.float32), a=a.astype(np.float32), alb=(alb * 255 + 0.5).clip(0, 255).astype(np.uint8), n=n.astype(np.float32))
    print(z.shape, float(z[a > 0.5].min()), float(z[a > 0.5].max()))
