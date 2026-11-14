# 台を いろいろな 向きから 描く（読むだけ）
#   python3 -I view.py <glb> <出力の 接頭辞> <名前=az,el,dist係数,tx,ty,tz,fov,W,H> …
import sys, math, time
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from common import *
import glb as GLB
import raster as RS
from PIL import Image

LIGHTS = [RS.Light((0.35, 0.55, 1.0), (1.0, 0.98, 0.95), 2.1, shadow=False), RS.Light((-0.6, 0.3, 0.7), (0.9, 0.95, 1.0), 0.7), RS.Light((0.0, 1.0, 0.25), (1, 1, 1), 0.5)]
AMB = ((0.62, 0.62, 0.62), (0.34, 0.34, 0.34))


def shot(prims, az, el, dist, tgt, fov, W, H, ss=2, bg=(0.93, 0.93, 0.95), want_raw=False):
    a, e = math.radians(az), math.radians(el)
    eye = np.array(tgt, np.float64) + dist * np.array([math.sin(a) * math.cos(e), math.sin(e), math.cos(a) * math.cos(e)])
    cam = RS.Camera.look_at(eye, tgt, fov_y=fov, W=W, H=H)
    o = RS.render(prims, cam, LIGHTS, ss=ss, ambient=AMB, env_spec=(0.25, 0.25, 0.25), rim=((1, 1, 1), 0.0, 2.5), ao_strength=0.7)
    rgb = RS.tonemap(o['rgb'], 1.0)
    A = o['alpha'][..., None]
    img = rgb * A + np.array(bg, np.float32) * (1 - A)
    if want_raw:
        return img, o, cam
    return img


if __name__ == '__main__':
    path, pre = sys.argv[1], sys.argv[2]
    t0 = time.time()
    m = GLB.load(path)
    prims = m.flatten()
    print('load', round(time.time() - t0, 1), 's', [p.ntri for p in prims])
    for spec in sys.argv[3:]:
        name, v = spec.split('=')
        az, el, dist, tx, ty, tz, fov, W, H = [float(x) for x in v.split(',')]
        t1 = time.time()
        img = shot(prims, az, el, dist, (tx, ty, tz), fov, int(W), int(H))
        Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)).save(f'{pre}{name}.png')
        print(name, round(time.time() - t1, 1), 's')
