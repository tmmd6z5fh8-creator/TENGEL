# フィギュアの 写真（すける 背景・元の GLB の まま）：python3 kisekae/fig/thumb.py <in.glb> <out.png> [大きさ 640] [見下ろし 度 6]
import os, sys, math
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'r3d', 'glb'))
import glb
from raster import Camera, render, tonemap
from PIL import Image
src, out = sys.argv[1], sys.argv[2]; R = int(sys.argv[3]) if len(sys.argv) > 3 else 640; EL = float(sys.argv[4]) if len(sys.argv) > 4 else 6
m = glb.load(src); prims = m.flatten()
lo, hi = m.bbox(); lo = np.array(lo); hi = np.array(hi); c = (lo + hi) / 2; ext = hi - lo
e = math.radians(EL); dist = max(ext[0], ext[1]) * 4.2
eye = c + dist * np.array([0, math.sin(e), math.cos(e)])
cam = Camera.look_at(eye, c, fov_y=15, W=R, H=R)
fr = render(prims, cam, ss=2, want=('rgb', 'alpha'))
rgb = np.clip(tonemap(fr['rgb'], 1.0), 0, 1); a = np.clip(fr['alpha'], 0, 1)
img = np.dstack([rgb, a]); im = Image.fromarray((img * 255 + 0.5).astype(np.uint8), 'RGBA')
bb = im.getbbox(); im = im.crop(bb); im.save(out); print(out, im.size)
