# アプリ用の 台の 絵の カメラ（正面・少し 遠近）と 写し方（台の 座標 → 絵の 画素）
import sys, math
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from dp_env import ROOT
from common import *
import glb as GLB
import raster as RS

V2 = ROOT + '/out/Tenger_Lucky_Drop_v2.glb'
IMG_W, IMG_H = 1120, 1830            # 台の 絵の 大きさ（画素）
DIST = 4.0                           # カメラ（盤の 面 z=0 から）
EYE_Y = 0.0
TAN = 0.2519                         # tan(たての 見える 角 / 2)
FOV = 2 * math.degrees(math.atan(TAN))
F = (IMG_H / 2) / TAN                # 焦点（画素）


def camera(k=1.0):
    return RS.Camera.look_at((0.0, EYE_Y, DIST), (0.0, EYE_Y, 0.0), fov_y=FOV, W=int(round(IMG_W * k)), H=int(round(IMG_H * k)), near=2.0, far=8.0)


def proj(x, y, z, k=1.0):
    """台の 座標 → 絵の 画素（左上が 0,0）"""
    s = F * k / (DIST - np.asarray(z, float))
    return IMG_W * k / 2 + np.asarray(x, float) * s, IMG_H * k / 2 - (np.asarray(y, float) - EYE_Y) * s


def scale_at(z, k=1.0):
    return F * k / (DIST - z)


def lights(shadow=True):
    return [RS.Light((-0.45, 0.62, 1.0), (1.0, 0.985, 0.96), 2.15, shadow=shadow, shadow_res=4096, softness=2.2), RS.Light((0.65, 0.2, 0.75), (0.92, 0.96, 1.0), 0.62), RS.Light((0.0, 1.0, 0.3), (1, 1, 1), 0.42)]


AMB = ((0.64, 0.64, 0.64), (0.37, 0.37, 0.37))


def beauty(prims, k=1.0, ss=2, shadow=True):
    o = RS.render(prims, camera(k), lights(shadow), ss=ss, ambient=AMB, env_spec=(0.22, 0.22, 0.22), rim=None, ao_strength=0.75)
    return o
